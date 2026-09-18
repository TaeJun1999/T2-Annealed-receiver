"""exp_0921 runner — QPSK route (a), Gaussian Kronecker prior, Nt = 4, T = 28, (133,171)_8 nu = 6 terminated, 16 iterations logged
(the iteration-8 result is index 7 of the same trajectory: RouteA.run is deterministic and iteration t does not depend on n_iter).

  python exp_0921_run.py predict                  closed-form first-pass (pilot-only LMMSE) NMSE and interference-limited SIR per config  (< 1 s)
  python exp_0921_run.py time  [--Nr 8]           seconds per RouteA.run for every variant (3 trials)                                   (~10 s)
  python exp_0921_run.py A     [--n 320]          set A: D-15 baseline table, rho = 0.7, 4x4;  Tp=4: 0,3,6,9 dB;  Tp=2: 6,9,12,15 dB
  python exp_0921_run.py C     [--n 320]          set C: GMM testbed (exp_0920 prior, exact score), Q-25(b): is D-13 / D-14 still needed once D-15 is on?
                                                  Tp=4: 3,6,9 dB;  Tp=2: 9,12,15 dB;  --rho = per-component correlation (default 0.7), DFT pilots
  python exp_0921_run.py B     [--n 160]          set B: Q-20 regime scan, Tp x rho x pilot{dft,eig} x SNR;  options --Nr 8 --rho .. --tp .. --snr ..
  common options: --jobs J (default: all cores), --chunk 40

Reproducibility: trials of a point come from ONE rng stream seeded SEED + 100 + int(snr) (SEED = 20260921); a task = (point, skip, chunk) regenerates
the skipped trials, so chunks concatenate into one sequence and every variant at a point sees the same (H, u, perm, Y). Points that differ only in the
pilot type share (H, u, perm, W). Finished chunks are skipped on re-run (raise --n later to extend a point). Raw logs: exp_0921_raw/*.npz.
Requires the exp_0921 version of t2_route_a.py (kwargs Xp, beta_fb) and t2_trellis.py (vectorised bcjr) in the same directory."""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"): os.environ.setdefault(_v, "1")   # one BLAS thread per worker
import sys, time, argparse, inspect, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from t2_route_a import KronGaussianPrior, GaussianPrior, GMMPrior, steer_corr, QAMCode, RouteA, exp_corr, dft_pilots
assert "beta_fb" in inspect.signature(RouteA.__init__).parameters, "t2_route_a.py is not the exp_0921 version (needs Xp / beta_fb kwargs)"
GENS, NU, SEED, T, NT, N_ITER = ("133", "171"), 6, 20260921, 28, 4, 16
RAW = os.path.join(HERE, "exp_0921_raw")
KEYS = ("blk_err", "ber", "nmse", "tauL_gmean", "alphaD")

# In the Gaussian testbed the v1 bundle (D-13 belief scalarisation + D-14 matrix site) == mode 'colored' exactly (T6), so 'colored' stands for v1.
_fb = dict(feedback="posterior")
SETS = {
  "A": {
    "col_ext_b1":         dict(mode="colored"),
    "col_ext_b0.7":       dict(mode="colored", beta=0.7),
    "col_post_b1":        dict(mode="colored", **_fb),                                   # D-15
    "col_post_b0.7":      dict(mode="colored", beta=0.7, **_fb),                         # D-15 + D-12  (candidate default)
    "col_post_b0.7_fbd":  dict(mode="colored", beta=0.7, beta_fb=0.7, **_fb),            # ... with the a-posteriori feedback path damped too
    "col_postnoloo_b0.7": dict(mode="colored", beta=0.7, loo=False, **_fb),              # LOO ablation under damping
    "v0_ext_b1":          dict(mode="scalar"),
    "v0_post_b1":         dict(mode="scalar", **_fb),
    "v0_ext_b0.7":        dict(mode="scalar", beta=0.7),
    "v0_post_b0.7":       dict(mode="scalar", beta=0.7, **_fb),
    "bel_ext_b0.7":       dict(mode="scalar", scal="belief", beta=0.7),                  # D-13 only (isotropic H-site)
    "bel_post_b0.7":      dict(mode="scalar", scal="belief", beta=0.7, **_fb),
    "pilot_b1":           dict(mode="pilot_only"),
    "pilot_b0.7":         dict(mode="pilot_only", beta=0.7),
    "genie_b1":           dict(mode="genie"),
  },
  "C": {   # GMM prior, all with beta = 0.7, n_inner = 1, 16 iterations. *_ext: extrinsic feedback to L_H, *_pf: a-posteriori feedback (D-15)
    "v0_ext":      dict(mode="scalar", beta=0.7),
    "v0_pf":       dict(mode="scalar", beta=0.7, **_fb),
    "D13_ext":     dict(mode="scalar", scal="belief", beta=0.7),
    "D13_pf":      dict(mode="scalar", scal="belief", beta=0.7, **_fb),
    "D14_pf":      dict(mode="scalar", hsite="matrix", lam_min=1e-6, beta=0.7, **_fb),
    "D13+14_ext":  dict(mode="scalar", scal="belief", hsite="matrix", lam_min=1e-6, beta=0.7),
    "D13+14_pf":   dict(mode="scalar", scal="belief", hsite="matrix", lam_min=1e-6, beta=0.7, **_fb),      # v1 candidate
    "exactEP_ext": dict(mode="colored", exact_prior=True, lam_min=1e-6, beta=0.7),
    "exactEP_pf":  dict(mode="colored", exact_prior=True, lam_min=1e-6, beta=0.7, **_fb),                  # reference: exact mixture EP site
    "lmmseC_pf":   dict(mode="colored", beta=0.7, **_fb),                                                  # second-moment method (ensemble C_hat = I)
    "pilot_gmm":   dict(mode="pilot_only", exact_prior=True, lam_min=1e-6, beta=0.7),
    "pilot_C":     dict(mode="pilot_only", beta=0.7),
    "genie":       dict(mode="genie"),
  },                # + "oracle_pf": colored + posterior with the TRUE component's Gaussian prior (added in run_task)
  "B": {
    "col_ext_b0.7":       dict(mode="colored", beta=0.7),
    "col_post_b0.7":      dict(mode="colored", beta=0.7, **_fb),
    "pilot_b1":           dict(mode="pilot_only"),
    "pilot_b0.7":         dict(mode="pilot_only", beta=0.7),
    "genie_b1":           dict(mode="genie"),
  },
}


def make_pilots(kind, Tp, rho):
    """'dft': first Tp DFT columns (unit-modulus entries). 'eig': sqrt(Nt) * top-Tp eigenvectors of R_t (same per-column energy Nt; unequal
    per-antenna power -> ablation). For C = kron(R_t^T, R_r) and site precision kron(conj(x) x^T, I) the matched direction is x = u_k(R_t)."""
    if kind == "dft": return dft_pilots(NT, Tp)
    w, U = np.linalg.eigh(exp_corr(NT, rho)); U = U[:, ::-1]
    U = U * np.sign(U[np.argmax(np.abs(U), 0), np.arange(NT)])          # fix the eigenvector sign (platform independent)
    return np.sqrt(NT) * U[:, :Tp].astype(complex)


def make_prior(sname, Nr, rho):
    if sname != "C": return KronGaussianPrior(Nr, NT, rho)
    psis = 2 * np.pi * (np.arange(4) + 0.5) / 4               # exp_0920 prior: 16 equiprobable directional components, ensemble covariance = I
    return GMMPrior(Nr, NT, [np.kron(steer_corr(NT, rho, pt).T, steer_corr(Nr, rho, pr)) for pt in psis for pr in psis])


def fname(sname, Nr, rho, Tp, pil, snr, skip, n):
    return os.path.join(RAW, f"{sname}_Nr{Nr}_rho{rho}_Tp{Tp}_{pil}_snr{int(snr)}_skip{skip}_n{n}.npz")


def run_task(task):
    sname, Nr, rho, Tp, pil, snr, skip, n = task
    out = fname(*task)
    if os.path.exists(out): return f"exists  {os.path.basename(out)}"
    t0 = time.time()
    prior = make_prior(sname, Nr, rho); code = QAMCode(GENS, NU, 2, NT * (T - Tp)); sigma2 = 10 ** (-snr / 10)
    Xp = make_pilots(pil, Tp, rho)
    oracle = [RouteA(Nr, NT, T, Tp, sigma2, GaussianPrior(Nr, NT, C), code, Xp=Xp, mode="colored", beta=0.7, **_fb) for C in prior.covs] if sname == "C" else None
    rxs = {k: RouteA(Nr, NT, T, Tp, sigma2, prior, code, Xp=Xp, **c) for k, c in SETS[sname].items()}
    first = next(iter(rxs.values())); logs = {k: [] for k in rxs}; comp = []
    if oracle: logs["oracle_pf"] = []
    rng = np.random.default_rng(SEED + 100 + int(snr))
    for tr in range(skip + n):
        H = prior.sample(rng); u = rng.integers(0, 2, code.K); perm = rng.permutation(code.Ns)
        X, Y = first.transmit(u, perm, H, rng)
        if tr < skip: continue
        for k, rx in rxs.items(): logs[k].append(rx.run(Y, H, u, perm, N_ITER))
        if oracle: comp.append(prior.last_k); logs["oracle_pf"].append(oracle[prior.last_k].run(Y, H, u, perm, N_ITER))
    flat = {f"{k}|{key}": np.array([l[key] for l in L]) for k, L in logs.items() for key in KEYS}
    if oracle: flat["comp"] = np.array(comp)
    np.savez_compressed(out, **flat)
    bl = " ".join(f"{k}={np.mean([l['blk_err'][-1] for l in L]):.2f}" for k, L in logs.items() if k in ("col_post_b0.7", "pilot_b0.7", "genie_b1", "v0_pf", "D13+14_pf", "pilot_gmm", "genie"))
    return f"done    {os.path.basename(out)}  ({time.time() - t0:.0f} s)  BLER16: {bl}"


def tasks_for(points, n, chunk):
    return [p + (s, min(chunk, n - s)) for p in points for s in range(0, n, chunk)]


def grid_A():
    return [("A", 4, 0.7, Tp, "dft", float(s)) for Tp, snrs in ((4, (0, 3, 6, 9)), (2, (6, 9, 12, 15))) for s in snrs]


def grid_C(rho):
    return [("C", 4, rho, Tp, "dft", float(s)) for Tp, snrs in ((4, (3, 6, 9)), (2, (9, 12, 15))) for s in snrs]


def grid_B(Nr, rhos, tps, snrs):
    pts = []
    for rho in rhos:
        ss = snrs if snrs else (range(0, 19, 3) if rho <= 0.75 else range(6, 25, 3))
        for Tp in tps:
            for pil in (("dft",) if Tp == NT else ("dft", "eig")):       # Tp = Nt: sqrt(Nt) U is a scaled unitary like DFT -> same LMMSE error, skip
                pts += [("B", Nr, rho, Tp, pil, float(s)) for s in ss]
    return pts


def predict():
    """[exact, Gaussian prior] First pass of EVERY receiver = pilot-only LMMSE (data sites are zero at x_bar = 0, form A).
    Sigma = (C^-1 + kron(conj(Xp) Xp^T, I)/sigma2)^-1, NMSE = tr Sigma / tr C.   sigma2 -> 0:  Sigma -> kron(S^T, R_r),
    S = R_t - R_t Xp (Xp^H R_t Xp)^-1 Xp^H R_t,  NMSE_inf = tr S / Nt  (independent of R_r, Nr);  'eig' pilots: NMSE_inf = sum_{k>Tp} lambda_k / Nt
    = minimum over all Tp-dim pilot subspaces (Ky Fan).  First-pass L_X noise (r = 0, tau = 1 -> M = I):  R_n = sigma2 I + tr(S) R_r
    -> interference-limited  SIR_inf = (1 - NMSE_inf) / NMSE_inf  (all streams together), independent of SNR  => F5."""
    print("closed-form first pass (pilot-only LMMSE), Nt = 4.  NMSE = tr Sigma / tr C  (ratio of expectations, not the per-trial ratio logged by RouteA)")
    print(f"{'rho':>4} {'Tp':>3} {'pil':>4} | {'eig(R_t)':>26} | {'NMSE_inf':>8} {'SIR_inf[dB]':>11} | " + " ".join(f"NMSE@{s:>2}dB" for s in (6, 12, 18)))
    for rho in (0.5, 0.7, 0.9):
        Rt = exp_corr(NT, rho); lam = np.linalg.eigvalsh(Rt)[::-1]
        for Tp in (2, 3, 4):
            for pil in (("dft",) if Tp == NT else ("dft", "eig")):
                Xp = make_pilots(pil, Tp, rho)
                S = Rt - Rt @ Xp @ np.linalg.inv(Xp.conj().T @ Rt @ Xp) @ Xp.conj().T @ Rt
                inf = max(np.trace(S).real / NT, 0.0)
                pr = KronGaussianPrior(4, NT, rho); fin = []               # finite SNR: exact 4x4 Kronecker prior (R_r = R_exp(rho))
                for s in (6, 12, 18):
                    Sig = np.linalg.inv(pr.Cinv + np.kron(Xp.conj() @ Xp.T, np.eye(4)) * 10 ** (s / 10))
                    fin.append(np.trace(Sig).real / np.trace(pr.C).real)
                sir = "inf" if inf < 1e-12 else f"{10 * np.log10((1 - inf) / inf):.1f}"
                print(f"{rho:>4} {Tp:>3} {pil:>4} | {' '.join(f'{x:6.3f}' for x in lam)} | {inf:8.4f} {sir:>11} | " + " ".join(f"{x:9.4f}" for x in fin))
    print("finite-SNR columns: Nr = 4, R_r = R_exp(rho). NMSE_inf does not depend on R_r or Nr.")


def timing(Nr):
    Tp, snr = 2, 12.0
    code = QAMCode(GENS, NU, 2, NT * (T - Tp)); rng = np.random.default_rng(1)
    for sname in ("A", "B", "C"):
        prior = make_prior(sname, Nr, 0.7); tot = 0.0
        for k, c in SETS[sname].items():
            rx = RouteA(Nr, NT, T, Tp, 10 ** (-snr / 10), prior, code, **c); t0 = time.time()
            for _ in range(3):
                H = prior.sample(rng); u = rng.integers(0, 2, code.K); perm = rng.permutation(code.Ns); X, Y = rx.transmit(u, perm, H, rng)
                rx.run(Y, H, u, perm, N_ITER)
            dt = (time.time() - t0) / 3; tot += dt; print(f"  [{sname}] {k:<20} {dt:.3f} s/run ({N_ITER} it, {Nr}x{NT})")
        print(f"  [{sname}] total {tot:.2f} s/trial")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["predict", "time", "A", "B", "C"])
    ap.add_argument("--n", type=int, default=None); ap.add_argument("--jobs", type=int, default=os.cpu_count()); ap.add_argument("--chunk", type=int, default=40)
    ap.add_argument("--Nr", type=int, default=4); ap.add_argument("--rho", type=float, nargs="+", default=None)
    ap.add_argument("--tp", type=int, nargs="+", default=[4, 3, 2]); ap.add_argument("--snr", type=float, nargs="+", default=None)
    a = ap.parse_args()
    if a.cmd == "predict": predict(); sys.exit()
    if a.cmd == "time": timing(a.Nr); sys.exit()
    os.makedirs(RAW, exist_ok=True)
    n = a.n or (160 if a.cmd == "B" else 320)
    pts = grid_A() if a.cmd == "A" else grid_C((a.rho or [0.7])[0]) if a.cmd == "C" else grid_B(a.Nr, a.rho or [0.7, 0.9], a.tp, a.snr)
    tasks = tasks_for(pts, n, a.chunk)
    tasks.sort(key=lambda t: t[6])                                       # all points get their first chunk early -> usable partial results
    print(f"[{a.cmd}] {len(pts)} points x n={n} -> {len(tasks)} tasks on {a.jobs} workers", flush=True); t0 = time.time()
    if a.jobs <= 1:
        for i, t in enumerate(tasks): print(f"{i + 1}/{len(tasks)} {run_task(t)}", flush=True)
    else:
        import multiprocessing as mp
        with mp.Pool(a.jobs) as pool:
            for i, msg in enumerate(pool.imap_unordered(run_task, tasks)): print(f"{i + 1}/{len(tasks)} {msg}", flush=True)
    print(f"[{a.cmd}] finished in {(time.time() - t0) / 60:.1f} min -> now run: python exp_0921_analysis.py {a.cmd}")