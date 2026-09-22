"""conf/code/sigma.py -- A4 / B3: MEASURE the sigma_t grid (conf/04_SPEC_diffusion.md §3).

"score model 이 어느 노이즈 수준에서 좋아야 하는지는 수신기가 실제로 질의하는 범위가 정한다."
So we run the receiver that actually queries Module H -- the one-shot D-13(belief) + D-14(matrix site)
interface, i.e. EXACTLY the interface of M-ours-score / M-ours-dscore -- with Module H set to the Gaussian
sample-covariance prior (= M-ours-G), and collect the empirical distribution of the cavity noise level
nu_q that the denoiser receives, pooled over iterations, SNRs and cells.

Conventions.  nu_q is the per-COMPLEX-entry cavity variance: q = h + e, e ~ CN(0, nu_q I).
The score network lives in the real 2-channel domain, where the per-REAL-dimension noise std is
    sigma_t = sqrt(nu_q / 2).
Both are written to sigma_grid.txt; training and the gates use sigma_t.
"""
import os
import numpy as np

import common as C
import arms as A

N_MEAS = 64                 # 04_SPEC §3: "a small n (e.g. 64)"
N_GRID = 20                 # "log-equispaced grid, 20 points recommended"
PCT = (1.0, 99.0)           # "covering the 1-99 percentile of that distribution"


def measure_point(task):
    testbed, prior, cell, snr, n = task
    c = C.CELLS[cell]
    Nr, Nt, T, Tp = c["Nr"], c["Nt"], c["T"], c["Tp"]
    sigma2 = 10 ** (-snr / 10)
    code = C.QAMCode(C.GENS, C.NU, C.M_QAM, Nt * (T - Tp))
    pil, Xp = C.make_pilots(testbed, prior, Nt, Tp, Nr)
    gen = C.make_gen(testbed, prior, Nr, Nt)
    fits = A.load_fits(testbed, prior, Nr)
    Cs = C.GaussianPrior(Nr, Nt, fits[("full", 32)]["Chat"])
    rx = A.route_a(Nr, Nt, T, Tp, sigma2, Cs, code, Xp, "score", clip="eta")     # == M-ours-G in the score interface
    rng = C.trial_rng(testbed, prior, Nr, T, Tp, snr)
    vals = []
    for _ in range(n):
        H = gen.sample(rng)
        u = rng.integers(0, 2, code.K)
        perm = rng.permutation(code.Ns)
        X, Y = rx.transmit(u, perm, H, rng)
        o = rx.run(Y, H, u, perm, C.N_ITER)
        vals.append(o["nu_q"])
    v = np.asarray(vals, float)
    return (cell, snr), v


def measure(testbed, cells, prior=None, n=N_MEAS, jobs=None):
    import multiprocessing as mp
    prior = prior or C.PRIOR_OF[testbed]
    tasks = [(testbed, prior, cell, float(s), n) for cell in cells for s in C.CELLS[cell]["snrs"]]
    with mp.Pool(min(jobs or os.cpu_count(), len(tasks))) as pool:
        res = dict(pool.map(measure_point, tasks))
    return res, prior


def build_grid(res, n_grid=N_GRID, pct=PCT):
    allv = np.concatenate([v.reshape(-1) for v in res.values()])
    fin = allv[np.isfinite(allv) & (allv > 0)]
    lo, hi = np.percentile(fin, pct)
    nu = np.exp(np.linspace(np.log(lo), np.log(hi), n_grid))
    return nu, fin, lo, hi


def write(testbed, res, prior, out=None, tag=""):
    """tag != "" routes BOTH the .txt and the .npz to tagged paths, so a smoke run can never overwrite the
    FROZEN A4 grid that every GA-GD gate and every score arm reads (04_SPEC §3)."""
    sfx = f"_{tag}" if tag else ""
    out = out or os.path.join(C.CONF, "results",
                              f"sigma_grid{sfx}.txt" if testbed == "D1" else f"sigma_grid_{testbed}{sfx}.txt")
    nu, fin, lo, hi = build_grid(res)
    sig = np.sqrt(nu / 2.0)
    cells = sorted({k[0] for k in res})
    with open(out, "w") as f:
        f.write(C.header(testbed, extra=[
            f"content     : conf/04_SPEC_diffusion.md §3 -- the sigma_t grid MEASURED from the receiver's own queries",
            f"measured by : the D-13(belief)+D-14(matrix site) one-shot interface with Module H = Gaussian sample",
            f"              covariance (= M-ours-G); this is the interface M-ours-score / M-ours-dscore use.",
            f"prior       : {prior}   cells: {cells}   n = {len(next(iter(res.values())))} trials/point  x  "
            f"{C.N_ITER} iterations  x  {len(res)} points  =  {fin.size} samples",
            "convention  : nu_q = per-complex-entry cavity variance (q = h + CN(0, nu_q I));  "
            "sigma_t = sqrt(nu_q/2) = per-real-dimension std",
        ]) + "\n\n")
        f.write("empirical distribution of nu_q (pooled over iterations, SNRs, cells)\n")
        qs = [0.1, 1, 5, 10, 25, 50, 75, 90, 95, 99, 99.9]
        f.write("  percentile " + " ".join(f"{q:>9}" for q in qs) + "\n")
        f.write("  nu_q       " + " ".join(f"{x:9.3e}" for x in np.percentile(fin, qs)) + "\n")
        f.write("  sigma_t    " + " ".join(f"{x:9.3e}" for x in np.sqrt(np.percentile(fin, qs) / 2)) + "\n")
        f.write(f"  min {fin.min():.4e}  max {fin.max():.4e}  non-finite/non-positive dropped: "
                f"{int(np.sum(~(np.isfinite(np.concatenate([v.reshape(-1) for v in res.values()])) )))}\n\n")
        f.write("per cell x SNR: median nu_q per iteration (iterations 1, 2, 4, 8, 16)\n")
        for (cell, snr) in sorted(res, key=lambda k: (k[0], k[1])):
            v = res[(cell, snr)]
            m = np.nanmedian(v, axis=0)
            f.write(f"  {cell} {snr:>5.1f} dB  " + " ".join(f"it{i+1:<2}={m[i]:9.3e}" for i in (0, 1, 3, 7, 15)) + "\n")
        f.write(f"\nCHOSEN GRID  ({len(nu)} log-equispaced points covering the {PCT[0]}-{PCT[1]} percentile "
                f"[{lo:.4e}, {hi:.4e}] of nu_q)\n")
        f.write("  k    nu_q          sigma_t\n")
        for i, (a, b) in enumerate(zip(nu, sig)):
            f.write(f"  {i:<4} {a:.6e}  {b:.6e}\n")
        f.write("\nThis grid is FROZEN from here on (04_SPEC §3).  Training, the GA-GD gates and GB' all use it.\n")
    np.savez(os.path.join(C.CONF, "results", f"sigma_grid_{testbed}{sfx}.npz"),
             nu=nu, sigma=sig, lo=lo, hi=hi, samples=fin[:200000])
    return nu, sig, out


def load(testbed, tag=""):
    """tag="" is the FROZEN grid every Stage A/B number was taken with (04_SPEC §3) and is never
    overwritten.  tag="NR16" etc. loads a grid measured for a DIFFERENT array, which is a different
    ruler and must never be mixed with the frozen one in the same table (10_SPEC_stageC §7)."""
    sfx = f"_{tag}" if tag else ""
    z = np.load(os.path.join(C.CONF, "results", f"sigma_grid_{testbed}{sfx}.npz"))
    return z["nu"], z["sigma"]
