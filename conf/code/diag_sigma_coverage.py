"""H2 diagnostic -- does the RouteA loop query Module H OUTSIDE the trained/gated sigma range?

Runs the D2 / cell C2 receiver for a handful of trials at several SNRs and records, per outer
iteration, the cavity variance nu_q that Module H is actually asked for (log['nu_q'] is EXACTLY the
nu passed to prior.denoise / _matrix_site -- see t2_route_a.RouteA.run, scal='belief' branch), the
resulting NMSE, and alpha^H.  The denoise methods are ALSO wrapped in this driver to cross-check
that the logged nu_q is the queried one.  Nothing under Demo/ is modified.

Arms (all 16 outer iterations, identical loop, identical channel/noise realisations):
  M-ours-dscore   : the fixed checkpoint, score interface (belief scalarisation + matrix site)
  M-ours-bstar    : GMM b*, exact mixture-EP site  -- the real control arm
  ctrl-bstar-sIF  : the SAME GMM object through the SCORE interface (one-shot Tweedie + matrix site)
  ctrl-G-sIF      : Gaussian sample-cov through the score interface == the arm that MEASURED the grid
"""
import os, sys, time

os.environ.setdefault("OMP_NUM_THREADS", "4")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import common as C
import arms as A
import sigma as SG

CKPT = os.path.join(C.CONF, "ckpt", "d2sx_N10000_a1.pt")
OUT = os.path.join(C.CONF, "results", "diag")
ARMS = ("M-ours-dscore", "M-ours-bstar", "ctrl-bstar-sIF", "ctrl-G-sIF")
KEYS = ("nu_q", "nmse", "alphaH", "nuE", "blk_err", "ber")


def wrap(prior, rec):
    """Instance-level log of every (method, nu) Module H is queried with.  Observation only."""
    for name in ("denoise", "denoise_full"):
        f = getattr(prior, name)
        setattr(prior, name, lambda q, nu, f=f, name=name: (rec.append((name, float(nu))), f(q, nu))[1])


def build(cell, snr, prior="S2", testbed="D2"):
    import score as S
    c = C.CELLS[cell]
    Nr, Nt, T, Tp = c["Nr"], c["Nt"], c["T"], c["Tp"]
    sigma2 = 10 ** (-snr / 10)
    code = C.QAMCode(C.GENS, C.NU, C.M_QAM, Nt * (T - Tp))
    pil, Xp = C.make_pilots(testbed, prior, Nt, Tp, Nr)
    gen = C.make_gen(testbed, prior, Nr, Nt)
    fits = A.load_fits(testbed, prior, Nr)
    Chat = fits[("full", 32)]["Chat"]
    hp, _, _, bstar, _ = A.module_h_priors(testbed, prior, Nr, Nt)
    gm = hp[bstar]
    sp = S.ScorePrior(CKPT, Nr, Nt, Chat, device="cpu")
    Cs = C.GaussianPrior(Nr, Nt, Chat)
    a = (Nr, Nt, T, Tp, sigma2)
    rx = {
        "M-ours-dscore":  A.route_a(*a, sp, code, Xp, "score", clip="eta"),
        "M-ours-bstar":   A.route_a(*a, gm.view("eta"), code, Xp, "gmm_site"),
        "ctrl-bstar-sIF": A.route_a(*a, gm, code, Xp, "score", clip="eta"),
        "ctrl-G-sIF":     A.route_a(*a, Cs, code, Xp, "score", clip="eta"),
    }
    rec = {k: [] for k in rx}
    for k in ("M-ours-dscore", "ctrl-bstar-sIF", "ctrl-G-sIF"):
        wrap(rx[k].prior, rec[k])
    return rx, rec, gen, code, pil, bstar, sp


def run(cell, snrs, n, testbed="D2", prior="S2"):
    res = {}
    for snr in snrs:
        t0 = time.time()
        rx, rec, gen, code, pil, bstar, sp = build(cell, snr, prior, testbed)
        c = C.CELLS[cell]
        rng = C.trial_rng(testbed, prior, c["Nr"], c["T"], c["Tp"], snr)
        first = rx["M-ours-bstar"]
        logs = {k: {q: [] for q in KEYS} for k in rx}
        qnu = {k: [] for k in rx}
        for tr in range(n):
            H = gen.sample(rng)
            u = rng.integers(0, 2, code.K)
            perm = rng.permutation(code.Ns)
            X, Y = first.transmit(u, perm, H, rng)
            for k, r in rx.items():
                del rec[k][:]
                o = r.run(Y, H, u, perm, C.N_ITER)
                for q in KEYS:
                    logs[k][q].append(o[q])
                qnu[k].append([v for _, v in rec[k]])
        res[snr] = {k: {q: np.asarray(v, float) for q, v in d.items()} for k, d in logs.items()}
        for k in rx:
            res[snr][k]["queried_nu"] = np.asarray(qnu[k], float) if qnu[k] and qnu[k][0] else np.zeros((n, 0))
        print(f"[diag] snr {snr:+.0f} dB  n={n}  {time.time() - t0:.0f} s  pil={pil}  b*={bstar}  "
              f"dscore qstats={sp.query_stats()}", flush=True)
    return res, pil, bstar, sp


def first_true(mask):
    """1-based index of the first True along axis 1, or 0 when never."""
    any_ = mask.any(1)
    return np.where(any_, mask.argmax(1) + 1, 0)


def report(res, s_lo, s_hi, pil, bstar, cell, n, path):
    lines = [C.header("D2", extra=[
        "content     : H2 diagnostic -- the sigma_t the RouteA loop ACTUALLY queries Module H with,",
        "              per outer iteration, vs the FROZEN trained/gated grid range.  DIAGNOSTIC ONLY;",
        "              nothing here selects, tunes or replaces any pre-registered number.",
        f"checkpoint  : {CKPT}  (fixed, not retrained)",
        f"cell        : {cell} (8x4 T=16 Tp=4) prior S2  pilots={pil}  b*={bstar}  n={n} trials/point",
        f"trained/gated sigma_t range = [{s_lo:.6e}, {s_hi:.6e}]  (score._sigma_range -> sigma.load('D2'),",
        "              the frozen measured grid; train() draws sigma log-uniform on exactly this interval)",
        "convention  : nu_q per complex entry, sigma_t = sqrt(nu_q/2) per real dimension",
    ]), ""]
    for snr in sorted(res):
        lines.append(f"===== SNR {snr:+.0f} dB " + "=" * 70)
        for arm in ARMS:
            d = res[snr][arm]
            nu, nm = d["nu_q"], d["nmse"]
            lines.append(f"  --- {arm}")
            if not np.isfinite(nu).any():
                lines.append("      nu_q is NaN at every iteration: this arm never queries a DENOISER "
                             "(mode='colored', exact mixture-EP site).  NMSE trajectory only.")
            else:
                sg = np.sqrt(nu / 2.0)
                out = (sg < s_lo) | (sg > s_hi)
                fin = np.isfinite(sg)
                lines.append(f"      sigma_t queried : median {np.nanmedian(sg):.4e}  "
                             f"[{np.nanmin(sg):.4e}, {np.nanmax(sg):.4e}]")
                lines.append(f"      out of range    : {int((out & fin).sum())}/{int(fin.sum())} "
                             f"= {100.0 * (out & fin).sum() / max(fin.sum(), 1):.1f}%   "
                             f"(below {int(((sg < s_lo) & fin).sum())}, above {int(((sg > s_hi) & fin).sum())})")
                fo, fn = first_true(out & fin), first_true(nm > 1.0)
                both = (fo > 0) & (fn > 0)
                lines.append(f"      first it out of range : {np.array2string(fo, max_line_width=200)}  (0 = never)")
                lines.append(f"      first it NMSE > 1     : {np.array2string(fn, max_line_width=200)}  (0 = never)")
                if both.any():
                    lines.append(f"      ORDER on the {int(both.sum())} trials with both: "
                                 f"NMSE>1 strictly first {int((fn[both] < fo[both]).sum())}, "
                                 f"same iteration {int((fn[both] == fo[both]).sum())}, "
                                 f"out-of-range first {int((fo[both] < fn[both]).sum())}")
                lines.append("      it :  " + " ".join(f"{i + 1:>9}" for i in range(C.N_ITER)))
                lines.append("      sig:  " + " ".join(f"{x:9.3e}" for x in np.nanmedian(sg, 0)))
                lines.append("      oor%: " + " ".join(f"{100.0 * m:9.1f}" for m in (out & fin).mean(0)))
            lines.append("      nmse: " + " ".join(f"{x:9.3e}" for x in np.nanmedian(nm, 0)))
            lines.append(f"      BLER@1/@2/@16 = {np.nanmean(d['blk_err'][:, 0]):.3f} "
                         f"{np.nanmean(d['blk_err'][:, 1]):.3f} {np.nanmean(d['blk_err'][:, -1]):.3f}")
        lines.append("")
    txt = "\n".join(lines) + "\n"
    with open(path, "w") as f:
        f.write(txt)
    return txt


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", default="C2")
    ap.add_argument("--snr", type=float, nargs="+", default=[0, 3, 6, 15])
    ap.add_argument("--n", type=int, default=8)
    a = ap.parse_args()
    nu_g, sg_g = SG.load("D2")
    s_lo, s_hi = float(sg_g.min()), float(sg_g.max())
    res, pil, bstar, sp = run(a.cell, a.snr, a.n)
    os.makedirs(OUT, exist_ok=True)
    tag = f"sigma-coverage_D2_{a.cell}_n{a.n}"
    flat = {f"{snr:+.0f}dB|{arm}|{q}": v for snr, d in res.items() for arm, dd in d.items() for q, v in dd.items()}
    flat.update({"grid|sigma": sg_g, "grid|nu": nu_g, "grid|s_lo": s_lo, "grid|s_hi": s_hi,
                 "meta|ckpt": CKPT, "meta|cell": a.cell, "meta|n": a.n, "meta|pilots": pil, "meta|bstar": bstar})
    np.savez_compressed(os.path.join(OUT, tag + ".npz"), **flat)
    print(report(res, s_lo, s_hi, pil, bstar, a.cell, a.n, os.path.join(OUT, tag + ".txt")))
    print(f"[diag] -> {os.path.join(OUT, tag)}.txt / .npz", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
