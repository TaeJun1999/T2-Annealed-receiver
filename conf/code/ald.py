"""conf/code/ald.py -- Arvinte & Tamir (IEEE TWC 2023) posterior-sampling channel estimation with annealed Langevin
dynamics (ALD), run with OUR learned prior (the V1 score network, same weights) on the SAME trials as the receiver
(NEXT_EXPERIMENTS_ALD16e4).  The receiver is CPU/complex128 by rule; ALD is a PILOT-ONLY estimator, so its estimate is
precomputed here (GPU allowed for this step only) and the receiver arm reads it (arms.ALDSitePrior).

Algorithm (the authors' CODE utcsilab/score-based-channels test_score.py -- its noise term and annealed denominator differ
from the typeset Alg. 1), real-stacked coordinates x = [Re h,
Im h] (the network's own convention: noise of real std sigma per component, complex nu = 2 sigma^2):
    x ~ CN(0, I) (real N(0, 1/2));  for i = 1..L (sigma_i geometric from the network's TRAINED range smax -> smin):
        alpha_i = alpha_step * (sigma_i / sigma_L)^2;  M = 3 times:
        x <- x + alpha_i * ( s_theta(x, sigma_i) + pack( A^H (y - A h) / (sigma_n^2/2 + sigma_i^2) ) ) + sqrt(2 alpha_i beta) z
    output: the iterate at the early-stopping step (tuned per SNR on validation NMSE, as the authors do).
A^H (y - A h) = sigma_n^2 (b - G h) with the receiver's own pilot site (G, b) (RouteA._sites, pilot columns), so the
estimator sees exactly the pilots the receiver sees.  z is real N(0, 1); the authors use complex randn (variance 1/2 per
real component), so their beta = 0.01 equals beta = 0.005 here -- both are in BETA_GRID.  GPU, float32 (the authors'
precision; this GPU's FP64 rate is ~1/64), deterministic algorithms ON, TF32 OFF (DECISIONS: the receiver-CPU rule's
exception covers this precompute only).

    regen    : (CPU, GPUs hidden) regenerate trials with the runner's stream -> results/ald/pilots_<TAG>_<set>.npz
               (b, H per trial, G, sigma2 per SNR; set = dev (trials DEV_SKIP0..+n) or test (0..2559))
    tune     : (GPU) grid alpha_step = c * smin^2 (c in C_GRID) x beta in BETA_GRID on dev NMSE; stop step per SNR
    estimate : (GPU) frozen hyper-parameters on the test pilots -> results/ald/ald_<TAG>.npz (hhat, b, v per SNR)
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")      # required by deterministic cuBLAS (_det)

C_GRID = (1e-3, 3e-3, 1e-2, 3e-2, 1e-1, 3e-1)   # alpha_step = c * sigma_L^2, half-decade steps (review_ALD16e4 #6)
BETA_GRID = (0.001, 0.005, 0.01, 0.1, 1.0)      # 0.005 = the authors' default 0.01 in this noise convention
EDGE_EXT = 2                                    # a grid-edge optimum extends that axis by one step (x sqrt(10) or x 10), <= 2 times
BETA0, TIE_DB = 0.005, 0.1                      # keep the authors' default beta unless the dev optimum beats it by > 0.1 dB
L_LEVELS, M_STEPS = 200, 3              # M = 3 as in the paper; L levels span the trained sigma range
SEED = 20260927
OUT = os.path.join(C.CONF, "results", "ald")


def _regen_one(args):
    """One SNR: the runner's trial loop (runner.run_task) up to the pilot site; nothing else consumes the stream."""
    testbed, prior, cell, snr, skip, n, fits_tag, rotation = args
    import arms as A
    A.D2_FITS = os.path.join(C.CONF, "results", f"gmm_fits_D2_{fits_tag}")
    c = C.CELLS[cell]
    Nr, Nt, T, Tp = c["Nr"], c["Nt"], c["T"], c["Tp"]
    sigma2 = 10 ** (-snr / 10)
    code = C.QAMCode(C.GENS, C.NU, C.M_QAM, Nt * (T - Tp))
    _, Xp = C.make_pilots(testbed, prior, Nt, Tp, Nr)
    gen = C.make_gen(testbed, prior, Nr, Nt)
    if rotation is not None:                        # ROTMIX16e4: the same receive-array rotation as runner.py --rotation
        assert hasattr(gen, "rot"), f"{prior}: generator has no .rot"
        gen.rot = float(np.deg2rad(rotation))       # radians, added to every AoA of the block; the stream is unchanged
    arms, _, _, _ = A.build_baseline_arms(testbed, prior, Nr, Nt, T, Tp, sigma2, code, Xp, ntrain=160000)
    first = arms["R5-genie"]
    Td = T - Tp
    Xbar = np.hstack([Xp, np.zeros((Nt, Td))]); Tau = np.hstack([np.zeros((Nt, Tp)), np.ones((Nt, Td))])
    rng = C.trial_rng(testbed, prior, Nr, T, Tp, snr)
    bs, Hs, G = [], [], None
    for tr in range(skip + n):
        H = gen.sample(rng)
        u = rng.integers(0, 2, code.K)
        perm = rng.permutation(code.Ns)
        X, Y = first.transmit(u, perm, H, rng)
        if tr < skip:
            continue
        _, Asite, Bsite = first._sites(Y, Xbar, Tau, first.prior.eh2_prior.copy())
        G = Asite[:Tp].sum(0)
        bs.append(Bsite[:Tp].sum(0)); Hs.append(H.reshape(-1, order="F"))
    return snr, np.array(bs), np.array(Hs), G, sigma2


def cmd_regen(a):
    import multiprocessing as mp
    snrs = [float(s) for s in C.CELLS[a.cell]["snrs"]]
    skip, n = (C.DEV_SKIP0, a.n_dev) if a.set == "dev" else (0, 2560)
    jobs = [(a.testbed, a.prior, a.cell, s, skip, n, a.fits_tag, a.rotation) for s in snrs]
    t0 = time.time()
    with mp.Pool(len(jobs)) as pool:
        res = pool.map(_regen_one, jobs)
    res.sort(key=lambda r: r[0])
    os.makedirs(OUT, exist_ok=True)
    out = os.path.join(OUT, f"pilots_{a.tag}_{a.set}.npz")
    np.savez(out, snrs=np.array(snrs), skip=skip, n=n, b=np.stack([r[1] for r in res]), H=np.stack([r[2] for r in res]),
             G=np.stack([r[3] for r in res]), sigma2=np.array([r[4] for r in res]), testbed=a.testbed, prior=a.prior,
             cell=a.cell, fits_tag=a.fits_tag, rotation=-1.0 if a.rotation is None else float(a.rotation))
    print(f"[ald regen] {a.tag} {a.set}: {len(snrs)} SNR x {n} trials (skip {skip}) rotation={a.rotation} -> {out}  "
          f"{time.time() - t0:.0f} s")


def ald_run(model, b, G, sigma2, smin, smax, c, beta, H=None, gen=None, keep=None):
    """Batched ALD for ONE SNR.  b (B,N) complex, G (N,N) complex.  Returns the trajectory NMSE (if H given, mean over
    trials per step) and the iterates at the steps in `keep` (dict step -> (B,N) complex)."""
    import torch
    dev = next(model.parameters()).device
    dt, ct = torch.float32, torch.complex64              # the authors' precision; this GPU's FP64 rate is ~1/64
    B, N = b.shape
    bt = torch.as_tensor(b, dtype=ct, device=dev)
    Gt = torch.as_tensor(G, dtype=ct, device=dev)
    sig = torch.exp(torch.linspace(math.log(smax), math.log(smin), L_LEVELS, dtype=dt, device=dev))
    a_step = c * smin ** 2
    x = torch.randn(B, 2 * N, dtype=dt, device=dev, generator=gen) * math.sqrt(0.5)
    Ht = torch.as_tensor(H, dtype=ct, device=dev) if H is not None else None
    hn = (Ht.abs() ** 2).sum(-1) if H is not None else None
    curve, kept, step = [], {}, 0
    for i in range(L_LEVELS):
        s = sig[i]
        alpha = a_step * (s / smin) ** 2
        sv = s.expand(B)
        for _ in range(M_STEPS):
            h = torch.complex(x[:, :N], x[:, N:])
            g = (bt - h @ Gt.T) * (sigma2 / (sigma2 / 2 + s ** 2))            # A^H(y - A h)/(sigma_n^2/2 + s^2)
            with torch.no_grad():
                sc = model.score_real(x, sv)
            x = x + alpha * (sc + torch.cat([g.real, g.imag], -1)) \
                + torch.sqrt(2 * alpha * beta) * torch.randn(B, 2 * N, dtype=dt, device=dev, generator=gen)
            step += 1
            if H is not None:
                e = ((torch.complex(x[:, :N], x[:, N:]) - Ht).abs() ** 2).sum(-1) / hn
                curve.append(float(e.mean()))
            if keep is not None and step in keep:
                kept[step] = torch.complex(x[:, :N], x[:, N:]).cpu().numpy().astype(complex)
    return np.array(curve), kept


def _det():
    import torch
    torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False


def _prov(ckpt):
    """Provenance stored in every tune/estimate record: checkpoint sha, this file's sha, device, precision."""
    import hashlib, subprocess, torch
    sha = lambda f: hashlib.sha256(open(f, "rb").read()).hexdigest()[:16]
    git = subprocess.run(["git", "-C", C.CONF, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    return dict(ckpt_sha=sha(os.path.join(C.CONF, ckpt)), ald_py_sha=sha(os.path.abspath(__file__)), git=git,
                device=torch.cuda.get_device_name(0), precision="float32/complex64, deterministic, TF32 off")


def _model(ckpt, device):
    import score as S
    m, st = S.load_model(ckpt, device=device, dtype=__import__("torch").float32)
    m.eval()
    _, sg = S.SG.load(st["testbed"], st.get("sigma_tag", "") or "")
    return m, float(sg.min()), float(sg.max()), st


def cmd_tune(a):
    import torch
    _det()
    m, smin, smax, _ = _model(a.ckpt, "cuda")
    z = np.load(os.path.join(OUT, f"pilots_{a.tag}_dev.npz"))
    snrs = z["snrs"]
    res = {}
    t0 = time.time()

    def run(c, beta):
        if (c, beta) in res:
            return
        curves = []
        for k, s in enumerate(snrs):
            gen = torch.Generator(device="cuda").manual_seed(SEED + 17 * k)
            cv, _ = ald_run(m, z["b"][k], z["G"][k], float(z["sigma2"][k]), smin, smax, c, beta, H=z["H"][k], gen=gen)
            curves.append(cv)
        curves = np.array(curves)                                   # (nSNR, steps)
        score = float(np.mean(10 * np.log10(np.nanmin(np.where(np.isfinite(curves), curves, np.inf), 1))))
        res[(c, beta)] = (score if np.isfinite(score) else np.inf, curves)
        print(f"[ald tune] {a.tag} c={c:g} beta={beta:g}: mean over SNR of best dev NMSE {score:+.2f} dB  "
              f"({time.time() - t0:.0f} s)", flush=True)

    cg, bg = list(C_GRID), list(BETA_GRID)
    for c in cg:
        for beta in bg:
            run(c, beta)
    ext = []
    for _ in range(EDGE_EXT):                                       # grid-edge rule: extend the edge axis once more
        (cb, bb) = min(res, key=lambda k: res[k][0])
        new = []
        if cb == cg[0]:
            cg.insert(0, cg[0] / math.sqrt(10)); new.append(("c", cg[0]))
        if cb == cg[-1]:
            cg.append(cg[-1] * math.sqrt(10)); new.append(("c", cg[-1]))
        if bb == bg[0]:
            bg.insert(0, bg[0] / 10); new.append(("beta", bg[0]))
        if bb == bg[-1]:
            bg.append(bg[-1] * 10); new.append(("beta", bg[-1]))
        if not new:
            break
        ext += new
        for c in cg:
            for beta in bg:
                run(c, beta)
    (cb, bb), (best, curves) = min(res.items(), key=lambda kv: kv[1][0])
    c0 = min((c for (c, b) in res if b == BETA0), key=lambda c: res[(c, BETA0)][0])
    rule = f"dev optimum c={cb:g}, beta={bb:g} ({best:+.3f} dB)"
    if res[(c0, BETA0)][0] - best <= TIE_DB:            # beta rule (review_ALD16e4 #2): the authors' default wins ties
        rule += f"; authors' default beta={BETA0:g} kept with its best c={c0:g} ({res[(c0, BETA0)][0]:+.3f} dB, within {TIE_DB} dB)"
        cb, bb, best, curves = c0, BETA0, res[(c0, BETA0)][0], res[(c0, BETA0)][1]
    edge = [n for n, v, g in (("c", cb, cg), ("beta", bb, bg)) if v in (g[0], g[-1])]
    stop = [int(np.nanargmin(np.where(np.isfinite(cv), cv, np.inf))) + 1 for cv in curves]
    v = []                                                          # v per SNR for the error-aware arm (dev MSE / entry)
    for k, s in enumerate(snrs):
        gen = torch.Generator(device="cuda").manual_seed(SEED + 17 * k)
        _, kept = ald_run(m, z["b"][k], z["G"][k], float(z["sigma2"][k]), smin, smax, cb, bb, gen=gen, keep={stop[k]})
        v.append(float(np.mean(np.abs(kept[stop[k]] - z["H"][k]) ** 2)))
    rec = dict(tag=a.tag, ckpt=a.ckpt, smin=smin, smax=smax, L=L_LEVELS, M=M_STEPS, c=cb, alpha_step=cb * smin ** 2,
               beta=bb, stop=dict(zip([float(s) for s in snrs], stop)), v=dict(zip([float(s) for s in snrs], v)),
               dev_nmse_db=dict(zip([float(s) for s in snrs], [float(10 * np.log10(np.nanmin(cv))) for cv in curves])),
               grid={f"c={c:g},beta={b:g}": r[0] for (c, b), r in res.items()}, extended=[f"{n}={x:g}" for n, x in ext],
               optimum_at_edge_after_extension=edge, selection_rule=rule, n_dev=int(z["n"]), dev_skip=int(z["skip"]), seed=SEED,
               **_prov(a.ckpt))
    json.dump(rec, open(os.path.join(OUT, f"tune_{a.tag}.json"), "w"), indent=1)
    np.savez(os.path.join(OUT, f"tune_{a.tag}_curves.npz"), **{f"c{c:g}_b{b:g}": r[1] for (c, b), r in res.items()})
    print(json.dumps({k: rec[k] for k in ("c", "beta", "selection_rule", "optimum_at_edge_after_extension", "stop", "dev_nmse_db")}))


def cmd_estimate(a):
    import torch
    _det()
    rec = json.load(open(os.path.join(OUT, f"tune_{a.tag}.json")))
    m, smin, smax, _ = _model(a.ckpt, "cuda")
    prov = _prov(a.ckpt)
    assert (smin, smax) == (rec["smin"], rec["smax"]) and a.ckpt == rec["ckpt"] and prov["ckpt_sha"] == rec["ckpt_sha"]
    z = np.load(os.path.join(OUT, f"pilots_{a.tag}_{a.set}.npz"))
    hh, nm = [], []
    for k, s in enumerate(z["snrs"]):
        gen = torch.Generator(device="cuda").manual_seed(SEED + 1000 + 17 * k)
        st = rec["stop"][str(float(s))]
        _, kept = ald_run(m, z["b"][k], z["G"][k], float(z["sigma2"][k]), smin, smax, rec["c"], rec["beta"], gen=gen,
                          keep={int(st)})
        h = kept[int(st)]
        if k == 0:                                      # determinism check (01_RULES §9.3 (4)): the same seed twice
            gen = torch.Generator(device="cuda").manual_seed(SEED + 1000)
            _, again = ald_run(m, z["b"][k], z["G"][k], float(z["sigma2"][k]), smin, smax, rec["c"], rec["beta"], gen=gen,
                               keep={int(st)})
            assert np.array_equal(again[int(st)], h), "ALD estimate not bit-reproducible with the same seed"
        hh.append(h)
        nm.append(float(np.mean(np.sum(np.abs(h - z["H"][k]) ** 2, -1) / np.sum(np.abs(z["H"][k]) ** 2, -1))))
    v = np.array([rec["v"][str(float(s))] for s in z["snrs"]])
    out = os.path.join(OUT, f"ald_{a.tag}" + ("" if a.set == "test" else f"_{a.set}") + ".npz")
    np.savez(out, snrs=z["snrs"], skip=int(z["skip"]), b=z["b"], hhat=np.stack(hh), v=v, nmse=np.array(nm), tune=json.dumps(rec),
             prov=json.dumps(prov), ckpt_sha=prov["ckpt_sha"])
    print(f"[ald estimate] {a.tag} {a.set} -> {out} (NMSE stored, not printed)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("regen", "tune", "estimate"))
    ap.add_argument("--tag", required=True); ap.add_argument("--testbed", default="D2")
    ap.add_argument("--prior", default="S2"); ap.add_argument("--cell", default="C2")
    ap.add_argument("--fits-tag"); ap.add_argument("--set", choices=("dev", "test"), default="dev")
    ap.add_argument("--n-dev", type=int, default=512); ap.add_argument("--ckpt")
    ap.add_argument("--rotation", type=float, default=None,
                    help="regen: receive-array rotation in DEGREES of the TEST channels (NEXT_EXPERIMENTS_ROTMIX16e4; the "
                         "same meaning as runner.py --rotation; 0 = the rotation code path with no rotation).  Stored in the npz.")
    a = ap.parse_args()
    {"regen": cmd_regen, "tune": cmd_tune, "estimate": cmd_estimate}[a.cmd](a)


if __name__ == "__main__":
    main()
