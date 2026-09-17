"""exp_0920 — learning-free NON-Gaussian testbed: Gaussian-mixture channel prior with an exact (closed-form) score, denoiser and Jacobian.
Prior: 16 equiprobable components, C_k = kron(R_t(psi_a)^T, R_r(psi_b)), R(psi) = D(psi) R_exp(0.9) D(psi)^H, psi in 2*pi*(k+1/2)/4, k=0..3
  -> every realisation is strongly directional (per-side eigenvalues 3.53/0.31/0.10/0.06) while the ENSEMBLE covariance is exactly C_hat = I.
Purpose: separate D-11 (dataset second moment folded in at the start) from the score-native rules D-13 (belief scalarisation) and D-14 (matrix H-site),
  in the regime where second moments carry no information. QPSK, 4x4, T=28, (133,171)_8, 8 iterations, seed 20260920 + 100 + SNR.
usage: python exp_0920_gmm.py <Tp> <snr_db> <n_trials> <skip>"""
import os, sys, time, numpy as np
os.makedirs("./exp_0919_raw", exist_ok=True); os.makedirs("./exp_0920_raw", exist_ok=True)
sys.path.insert(0, ".")
from t2_route_a import GMMPrior, GaussianPrior, steer_corr, QAMCode, RouteA
GENS, NU, SEED = ("133", "171"), 6, 20260920
Nr = Nt = 4; T = 28; LAM = 1e-6
RHO_C = float(sys.argv[5]) if len(sys.argv) > 5 else 0.7     # per-component exponential correlation (0.9: near rank-1, 4-stream multiplexing fails even with genie CSI)
def make_prior():
    psis = 2 * np.pi * (np.arange(4) + 0.5) / 4
    return GMMPrior(Nr, Nt, [np.kron(steer_corr(Nt, RHO_C, pt).T, steer_corr(Nr, RHO_C, pr)) for pt in psis for pr in psis])
MODES = {
    "v0":          dict(mode="scalar"),
    "D11":         dict(mode="scalar", init_colored=1),
    "D13":         dict(mode="scalar", scal="belief"),
    "D13x3":       dict(mode="scalar", scal="belief", n_inner=3),
    "D14":         dict(mode="scalar", hsite="matrix", lam_min=LAM),
    "D13+14":      dict(mode="scalar", scal="belief", hsite="matrix", lam_min=LAM),
    "D13x3+14":    dict(mode="scalar", scal="belief", n_inner=3, hsite="matrix", lam_min=LAM),
    "D13x3+14_pf": dict(mode="scalar", scal="belief", n_inner=3, hsite="matrix", lam_min=LAM, feedback="posterior"),
    "exactEP":     dict(mode="colored", exact_prior=True, lam_min=LAM),
    "exactEP_pf":  dict(mode="colored", exact_prior=True, lam_min=LAM, feedback="posterior"),
    "lmmseC":      dict(mode="colored"),
    "lmmseC_pf":   dict(mode="colored", feedback="posterior"),
    "pilot_gmm":   dict(mode="pilot_only", exact_prior=True, lam_min=LAM),
    "pilot_C":     dict(mode="pilot_only"),
    "genie":       dict(mode="genie"),
}
if __name__ == "__main__":
    Tp, snr, n_trials, skip = int(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    prior = make_prior(); code = QAMCode(GENS, NU, 2, Nt * (T - Tp)); sigma2 = 10 ** (-snr / 10)
    rxs = {n: RouteA(Nr, Nt, T, Tp, sigma2, prior, code, **c) for n, c in MODES.items()}
    oracle_priors = [GaussianPrior(Nr, Nt, C) for C in prior.covs]
    logs = {n: [] for n in list(MODES) + ["oracle", "oracle_pf"]}; comp = []
    rng = np.random.default_rng(SEED + 100 + int(snr)); t0 = time.time()
    for tr in range(skip + n_trials):
        H = prior.sample(rng); k = prior.last_k; u = rng.integers(0, 2, code.K); perm = rng.permutation(code.Ns)
        X, Y = rxs["v0"].transmit(u, perm, H, rng)
        if tr < skip: continue
        comp.append(k)
        for n, rx in rxs.items(): logs[n].append(rx.run(Y, H, u, perm, 8))
        logs["oracle"].append(RouteA(Nr, Nt, T, Tp, sigma2, oracle_priors[k], code, mode="colored").run(Y, H, u, perm, 8))
        logs["oracle_pf"].append(RouteA(Nr, Nt, T, Tp, sigma2, oracle_priors[k], code, mode="colored", feedback="posterior").run(Y, H, u, perm, 8))
    flat = {f"{n}|{key}": np.array([l[key] for l in L]) for n, L in logs.items() for key in ("blk_err", "nmse", "ber", "nu_q", "tauL_gmean")}
    flat["comp"] = np.array(comp)
    np.savez_compressed(f"./exp_0920_raw/gmm_rho{RHO_C}_Tp{Tp}_snr{int(snr)}_skip{skip}_n{n_trials}.npz", **flat)
    print(f"[gmm rho_c={RHO_C}] Tp={Tp} SNR={snr:.0f} dB trials {skip}..{skip + n_trials - 1} ({time.time() - t0:.0f} s) BLER(last): " +
          " ".join(f"{n}={np.mean([l['blk_err'][-1] for l in L]):.3f}" for n, L in logs.items()), flush=True)
