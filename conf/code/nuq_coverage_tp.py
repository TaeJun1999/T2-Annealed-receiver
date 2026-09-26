"""conf/code/nuq_coverage_tp.py -- where do the Module-H queries of the Tp >= Nt cells fall relative to the headline sigma grid?

User decision 2026-09-25 CDT (Tp >= Nt Pareto cells C7 Tp=6, C8 Tp=8).  Measurement only, no BLER is read or written.

Receiver: the Gaussian sample-covariance prior of the B16e4k fits (results/gmm_fits_D2_B16e4k, full K=32 'Chat', N=1.6e5
-- what runner.build_point hands R2-ours-G at --ntrain 160000 --tag B16e4k), run through the SCORE interface
(route_a(..., "score", clip="eta") = sigma.py's measuring receiver).  R2-ours-G itself (mode 'colored') never calls a
denoiser and logs nu_q = NaN (t2_route_a.RouteA.run, else-branch); for a Gaussian prior the score interface is the SAME
trajectory (matrix site = C^{-1}, eta = 0: Demo unit test T6).  That identity is re-checked here on every trial: R2-ours-G
runs on the same (H, Y) and the max |NMSE_t difference| over all trials and iterations is printed.

Trials 6400..6463 of each point's own stream (common.trial_rng; never the test set 0..2559 or a registered range).
Grid: the headline checkpoint ckpt/d2sx_N160000_a1.pt reads the sigma grid named by its own 'sigma_tag' (score.ScorePrior:
s_lo = min, s_hi = max of results/sigma_grid_D2[_tag].npz); a query nu_q is below / inside / above when
sigma_t = sqrt(nu_q/2) is < s_lo / in [s_lo, s_hi] / > s_hi (ScorePrior's out-of-grid rule).

  python nuq_coverage_tp.py        -> results/review_next/nuq_coverage_tp.txt (+ .npz), CPU, one worker per point
"""
import multiprocessing as mp
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C                      # FIRST: sets OMP/OPENBLAS/MKL_NUM_THREADS=1 before numpy loads the BLAS
import numpy as np
import arms as A
import sigma as SG

CELLS, SKIP, N = ("C2", "C7", "C8"), 6400, 64
FITS = os.path.join(C.CONF, "results", "gmm_fits_D2_B16e4k")
NTRAIN = 160000
CKPT = os.path.join(C.CONF, "ckpt", "d2sx_N160000_a1.pt")
OUT = os.path.join(C.CONF, "results", "review_next", "nuq_coverage_tp.txt")


def point(task):
    cell, snr = task
    A.D2_FITS = FITS
    c = C.CELLS[cell]
    Nr, Nt, T, Tp = c["Nr"], c["Nt"], c["T"], c["Tp"]
    code = C.QAMCode(C.GENS, C.NU, C.M_QAM, Nt * (T - Tp))
    pil, Xp = C.make_pilots("D2", "S2", Nt, Tp, Nr)
    gen = C.make_gen("D2", "S2", Nr, Nt)
    Cs = C.GaussianPrior(Nr, Nt, A.load_fits("D2", "S2", Nr, NTRAIN)[("full", 32)]["Chat"])
    a = (Nr, Nt, T, Tp, 10 ** (-snr / 10))
    rx = A.route_a(*a, Cs, code, Xp, "score", clip="eta")          # sigma.py's receiver
    r2 = A.route_a(*a, Cs, code, Xp, "gaussian")                   # R2-ours-G, identity check only
    rng = C.trial_rng("D2", "S2", Nr, T, Tp, snr)
    nu, dmax = [], 0.0
    for tr in range(SKIP + N):
        H = gen.sample(rng)
        u = rng.integers(0, 2, code.K)
        perm = rng.permutation(code.Ns)
        _, Y = rx.transmit(u, perm, H, rng)
        if tr < SKIP:
            continue
        o, o2 = rx.run(Y, H, u, perm, C.N_ITER), r2.run(Y, H, u, perm, C.N_ITER)
        nu.append(o["nu_q"])
        dmax = max(dmax, float(np.max(np.abs(np.asarray(o["nmse"]) - np.asarray(o2["nmse"])))))
    return (cell, snr), (np.array(nu, float), dmax, pil, Xp.shape)


def main():
    import torch
    st = torch.load(CKPT, map_location="cpu", weights_only=False)
    stag = st.get("sigma_tag", "")
    nu_g, sg_g = SG.load("D2", stag)
    s_lo, s_hi = float(sg_g.min()), float(sg_g.max())
    tasks = [(c, float(s)) for c in CELLS for s in C.CELLS[c]["snrs"]]
    t0 = time.time()
    with mp.Pool(len(tasks)) as pool:
        res = dict(pool.map(point, tasks))
    L = [C.header("D2", extra=[
        "content     : nu_q coverage of the Tp >= Nt cells vs the headline sigma grid (measurement, no BLER)",
        f"receiver    : Gaussian Chat of {os.path.relpath(FITS, C.CONF)} (full K=32, N={NTRAIN}) through the score "
        "interface (= sigma.py's receiver; R2-ours-G's trajectory, checked per trial below)",
        f"trials      : {SKIP}..{SKIP + N - 1} of each point's common.trial_rng stream (D2/S2), {C.N_ITER} outer iterations",
        f"grid        : {os.path.relpath(CKPT, C.CONF)} sigma_tag={stag!r} -> results/sigma_grid_D2{'_' + stag if stag else ''}"
        f".npz: s_lo = {s_lo:.6e}, s_hi = {s_hi:.6e} (nu = 2 sigma^2: [{2 * s_lo ** 2:.4e}, {2 * s_hi ** 2:.4e}])",
        "fractions   : below = sigma_t < s_lo, inside = s_lo <= sigma_t <= s_hi, above = sigma_t > s_hi (ScorePrior rule)",
    ]), ""]
    agg, dall = {}, 0.0
    for c in CELLS:
        cc = C.CELLS[c]
        L.append(f"=== {c}  ({cc['Nr']}x{cc['Nt']}, T={cc['T']}, Tp={cc['Tp']}, K={cc['Nt'] * (cc['T'] - cc['Tp']) - 6}, "
                 f"pilots {res[(c, float(cc['snrs'][0]))][2]} {res[(c, float(cc['snrs'][0]))][3]})")
        L.append(f"  {'SNR':>5} {'n_q':>6} {'below':>7} {'inside':>7} {'above':>7}   {'median sigma_t per iteration 1,2,4,8,16':<52}"
                 f"  below% per iteration 1..16")
        for s in cc["snrs"]:
            v, d, _, _ = res[(c, float(s))]
            dall = max(dall, d)
            sg = np.sqrt(v / 2.0)
            fin = np.isfinite(sg)
            b, h = (sg < s_lo) & fin, (sg > s_hi) & fin
            agg.setdefault(c, []).append(sg[fin])
            m = np.nanmedian(sg, 0)
            L.append(f"  {s:>+5.0f} {int(fin.sum()):>6} {b.sum() / fin.sum():>7.3f} {1 - (b.sum() + h.sum()) / fin.sum():>7.3f} "
                     f"{h.sum() / fin.sum():>7.3f}   " + " ".join(f"{m[i]:9.3e}" for i in (0, 1, 3, 7, 15))
                     + "   " + " ".join(f"{100 * x:3.0f}" for x in b.mean(0)))
        a = np.concatenate(agg[c])
        L.append(f"  {'all':>5} {a.size:>6} {np.mean(a < s_lo):>7.3f} {np.mean((a >= s_lo) & (a <= s_hi)):>7.3f} "
                 f"{np.mean(a > s_hi):>7.3f}   pooled over the 7 SNRs x {N} trials x {C.N_ITER} iterations; "
                 f"min sigma_t {a.min():.4e} ({a.min() / s_lo:.3f} x s_lo)")
        L.append("")
    L.append(f"identity check: max |NMSE_t(score-interface Gaussian) - NMSE_t(R2-ours-G)| over every trial, iteration, "
             f"point = {dall:.3e}")
    L.append(f"wall {time.time() - t0:.0f} s on {len(tasks)} workers")
    txt = "\n".join(L) + "\n"
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        f.write(txt)
    np.savez_compressed(OUT[:-4] + ".npz", s_lo=s_lo, s_hi=s_hi, sigma_tag=stag, skip=SKIP, n=N,
                        **{f"{c}|{s:+.0f}|nu_q": res[(c, s)][0] for c, s in res})
    print(txt, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
