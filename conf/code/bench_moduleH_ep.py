"""(review_next P0-2) Module H cost on the REAL receiver call paths, headline B16e4k configuration.

bench_moduleH.py (A8, complexity_moduleH.txt) timed prior.denoise_full(q, nu) for BOTH priors.  The headline
GMM arm M-ours-bstar never calls that: once per outer iteration it calls GMMPriorB.ep_site(G, b, lam_min)
(mixture EP site from the colored likelihood, Demo/t2_route_a.py 'colored' branch).  The score arms call
prior.denoise(q, nu) (this is where ScorePrior evaluates m and the jacrev Jacobian, V1 also PSD-projects)
and then RouteAClip._matrix_site(q, nu, G) (a cache hit on (q, nu) plus the site construction).  So:

    Module H (GMM b*)   = ep_site
    Module H (score)    = denoise + _matrix_site          (non-overlapping; denoise_full inside is a cache hit)

Both are timed INSIDE real rx.run calls on the runner's own trial stream (common.trial_rng), so the inputs
are the receiver's actual (G, b) / (q, nu) trajectories, not synthetic isotropic queries.  Full-block
rx.run time is recorded too.  Arms are INTERLEAVED per trial with a rotating order, so load drift hits all
arms alike; the load average before/after is written down.  float64, ONE thread (the receiver runs one
thread per worker process).  CPU, because the receiver is CPU complex128 for every arm (01_RULES §9.3).

The old file is left untouched as the historical record; this writes new files under results/review_next/.
Report-only: selects nothing, changes no arm, not a BLER measurement.

    ~/miniforge3/envs/torch/bin/python conf/code/bench_moduleH_ep.py [--trials 24] [--snr -3 6]
"""
import argparse
import os
import platform
import sys
import time

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ["CUDA_VISIBLE_DEVICES"] = ""
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import common as C
import runner as R
import score as S

TAG, TESTBED, PRIOR, CELL, NTRAIN = "B16e4k", "D2", "S2", "C2", 160000
CKPT = os.path.join(C.CONF, "ckpt", "d2sx_N160000_a1.pt")
ARMS = ("M-ours-bstar", "M-ours-dscore-C-V1", "M-ours-dscore-C-V0")
OUTD = os.path.join(C.CONF, "results", "review_next")


class Tap:
    """Wrap a bound method on ONE object; accumulate per-trial call times (perf_counter, seconds)."""

    def __init__(self, obj, name):
        self.obj, self.name, self.f = obj, name, getattr(obj, name)
        self.calls = []
        setattr(obj, name, self)

    def __call__(self, *a, **k):
        t0 = time.perf_counter()
        r = self.f(*a, **k)
        self.calls.append(time.perf_counter() - t0)
        return r


def q(x, p):
    return float(np.percentile(x, p)) if len(x) else float("nan")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=24)
    ap.add_argument("--snr", type=float, nargs="+", default=[-3.0, 6.0])
    ap.add_argument("--iters", type=int, default=C.N_ITER)
    a = ap.parse_args()
    import torch
    torch.set_num_threads(1)
    R._init(TAG)
    cid = S.ckpt_identity(CKPT)
    load0 = os.getloadavg()
    rows, raw = [], {}
    for snr in a.snr:
        P = R.build_point(TESTBED, CELL, PRIOR, snr, NTRAIN, stagec_ckpt=CKPT)
        meta, code, gen = P["meta"], P["code"], P["gen"]
        assert meta.get("bstar") == "kron" and int(meta.get("kron_K")) == 1024, (meta.get("bstar"), meta.get("kron_K"))
        arms = {k: P["arms"][k] for k in ARMS}
        taps = {}
        for k, rx in arms.items():
            if k == "M-ours-bstar":
                assert rx.exact_prior and rx.mode == "colored", "headline GMM arm must take the ep_site path"
                taps[k] = dict(mh=[Tap(rx.prior, "ep_site")])
            else:
                taps[k] = dict(mh=[Tap(rx.prior, "denoise"), Tap(rx, "_matrix_site")])
        first = P["arms"]["R5-genie"]
        rng = C.trial_rng(TESTBED, PRIOR, P["Nr"], P["T"], P["Tp"], snr)
        per = {k: dict(block=[], mh_trial=[], mh_call=[], n_call=[]) for k in ARMS}
        nfail = {k: 0 for k in ARMS}
        for tr in range(a.trials + 1):                  # trial 0 = warm-up (imports, BLAS init), not reported
            H = gen.sample(rng)
            u = rng.integers(0, 2, code.K)
            perm = rng.permutation(code.Ns)
            X, Y = first.transmit(u, perm, H, rng)
            order = ARMS[tr % len(ARMS):] + ARMS[:tr % len(ARMS)]
            for k in order:
                for t in taps[k]["mh"]:
                    t.calls.clear()
                t0 = time.perf_counter()
                try:
                    arms[k].run(Y, H, u, perm, a.iters)
                except Exception as e:                  # a failed block is counted, never silently timed
                    nfail[k] += 1
                    print(f"[bench] {snr:+.0f} dB trial {tr} {k}: rx.run raised {e!r}", flush=True)
                    continue
                dt = time.perf_counter() - t0
                if tr == 0:
                    continue
                mh = taps[k]["mh"]
                assert len({len(t.calls) for t in mh}) == 1, [len(t.calls) for t in mh]
                per_call = np.sum([np.array(t.calls) for t in mh], axis=0)   # denoise_i + _matrix_site_i
                per[k]["block"].append(dt)
                per[k]["mh_trial"].append(float(per_call.sum()))
                per[k]["mh_call"].extend(per_call.tolist())
                per[k]["n_call"].append(len(per_call))
        for k in ARMS:
            d = {m: np.array(v) for m, v in per[k].items()}
            raw[f"{snr:+.0f}dB|{k}"] = d
            rows.append((snr, k, d, nfail[k]))
    load1 = os.getloadavg()

    lines = []
    w = lines.append
    w("# (review_next P0-2) Module H cost on the REAL receiver call paths -- headline B16e4k configuration")
    w(f"# date        : {time.strftime('%Y-%m-%d %H:%M:%S')} KST   git {os.popen('git -C ' + C.CONF + ' rev-parse --short HEAD').read().strip()}")
    w(f"# host        : {platform.node()} {os.cpu_count()} cores, CPU float64, ONE thread (OMP/MKL/OPENBLAS=1, torch threads 1)")
    w(f"# libs        : python {platform.python_version()}  numpy {np.__version__}  torch {torch.__version__}")
    w(f"# load avg    : before {load0[0]:.1f}/{load0[1]:.1f}/{load0[2]:.1f}  after {load1[0]:.1f}/{load1[1]:.1f}/{load1[2]:.1f}  (1/5/15 min)")
    w(f"# config      : testbed {TESTBED} prior {PRIOR} cell {CELL} ({C.CELLS[CELL]}), N_train={NTRAIN}, fits {R.d_fits_d2()}")
    w(f"# GMM arm     : M-ours-bstar = kron K=1024 (b* by validation log-likelihood), Module H = GMMPriorB.ep_site(G, b, lam_min)")
    w(f"# score arms  : {os.path.basename(CKPT)}  {cid}; Module H = ScorePrior.denoise (m + jacrev J [+PSD for V1]) + RouteAClip._matrix_site")
    w(f"# trials      : {a.trials} per SNR (+1 warm-up dropped), runner trial stream common.trial_rng, arms interleaved with rotating order")
    w(f"# iterations  : {a.iters} outer (n_inner=1, one Module H call per iteration)")
    w("")
    w(f"{'SNR':>5} {'arm':<22} | {'MH/call med':>11} {'IQR':>17} {'p90':>8} | {'calls/blk':>9} | {'MH/blk med':>10} | "
      f"{'block med':>9} {'IQR':>17} | {'MH share':>8} | fail")
    for snr, k, d, nf in rows:
        mc, bl = d["mh_call"] * 1e3, d["block"] * 1e3
        w(f"{snr:>+5.0f} {k:<22} | {np.median(mc):>9.3f}ms [{q(mc, 25):>6.2f},{q(mc, 75):>7.2f}] {q(mc, 90):>8.2f} | "
          f"{np.median(d['n_call']):>9.1f} | {np.median(d['mh_trial']) * 1e3:>8.1f}ms | "
          f"{np.median(bl):>7.0f}ms [{q(bl, 25):>6.0f},{q(bl, 75):>7.0f}] | {np.median(d['mh_trial'] / d['block']):>8.1%} | {nf}")
    w("")
    w("RATIOS (median, learned / GMM b*)")
    for snr in a.snr:
        g = raw[f"{snr:+.0f}dB|M-ours-bstar"]
        for k in ARMS[1:]:
            s = raw[f"{snr:+.0f}dB|{k}"]
            w(f"  {snr:+.0f} dB  {k:<22}: Module H per call {np.median(s['mh_call']) / np.median(g['mh_call']):.2f}x   "
              f"full block {np.median(s['block']) / np.median(g['block']):.2f}x")
    w("")
    w("WHAT THIS DOES AND DOES NOT SAY")
    w("  - Inference cost only; training / EM fitting cost is separate (TABLE A 'fit' column, meta|em_sec / fit_sec).")
    w("  - ONE implementation on ONE machine: numpy/BLAS for the GMM site, torch.func.jacrev for the network.")
    w("  - Module H per call and per block are measured on real receiver inputs; the full block includes the shared")
    w("    L_X / detector / BCJR work, identical code for every arm but data-dependent in time.")
    w("  - Supersedes complexity_moduleH.txt (A8) as the arm-to-arm cost statement: A8 timed denoise_full for the GMM,")
    w("    which M-ours-bstar never calls, at K=512 with the N=1e4 checkpoint.  A8 is kept unmodified as the record.")
    os.makedirs(OUTD, exist_ok=True)
    out = os.path.join(OUTD, "complexity_moduleH_ep.txt")
    with open(out, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    np.savez_compressed(os.path.join(OUTD, "complexity_moduleH_ep.npz"),
                        **{f"{key}|{m}": v for key, d in raw.items() for m, v in d.items()})
    print("\n".join(lines))
    print(f"\n-> {out}")


if __name__ == "__main__":
    main()
