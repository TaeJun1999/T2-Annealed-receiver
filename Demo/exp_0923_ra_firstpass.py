"""exp_0923 — Q-27 / R-A: does annealed posterior sampling with the ISOTROPIC score recover the exact-EP moments that the one-shot interface (D-13 + D-14) loses?
First pass only (pilots, no decoder), GMM testbed of exp_0920/0922 (16 directional components, ensemble covariance = I, exact score), 4x4.

Cases (SNR 6/12/18 dB each):  Tp4 / Tp3 / Tp2 = DFT pilots (G = g Pi, kappa = Tp/Nt);   aniso = 2 DFT pilots at full power + 2 at -10 dB (full-rank, anisotropic G:
  exercises the 'weak-coordinate' path of the sampler that later turbo passes will need).
Methods, all on the SAME (H, W) per trial (paired):
  exact        exact mixture posterior, moment-matched Gaussian (= what exactEP_pf uses)             -> KL = 0 by definition
  D13+D14      one-shot isotropic interface + matrix site (v1 default; identical to exp_0922 column)
  LMMSE(I)     ensemble-covariance Gaussian
  PS-M{8,32,128}   R-A moments from a PERFECT sampler of pi'_{nu_L} (GMM closed form)               -> Monte-Carlo floor at M chains; also checks w' == exact P(k|y)
  RA-M{M}-L{L}-K{K}   R-A with the annealed predictor-corrector sampler (t2_ra_sampler.ra_sample), delta = 0.3, nu_1 = 10, K_fin = 2K
  ...-J1       same chains, Tweedie covariance from ONE chain only (cost of one Jacobian = D-14 cost)
Per-trial metrics (raw npz): se = ||m - h||^2, hn = ||h||^2, wt = P-hat(k_true), pm = [argmax P-hat = k_true], kl = KL(N_exact || N_method) / N  [nats per complex dim],
  ce = ||Cov - Cov_ex||_F / ||Cov_ex||_F, clip = [site Lambda = Cov^-1 - G needed eigenvalue clipping at 1e-6], nfe = score evaluations per chain.
Header per cell: chi = nu_q tr(G)/N  (>= 1, = 1 iff G ∝ I  [exact, Jensen]) — anisotropy index of the interface.
Reproducible for any --jobs/--chunk: data rng = default_rng([SEED, case, snr, trial]), sampler rng = default_rng([SEED, case, snr, trial, method]).
usage: python exp_0923_ra_firstpass.py [--n 1000] [--jobs all] [--chunk 25] [--cases Tp4,Tp3,Tp2,aniso] [--snr 6,12,18]      seed 20260923"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"): os.environ.setdefault(_v, "1")
import sys, time, argparse, warnings, multiprocessing as mp, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from scipy.special import logsumexp
from t2_route_a import GMMPrior, steer_corr, dft_pilots
from t2_ra_sampler import GMMBatch, ra_sample, gmm_exact_zsample, rb_moments, site_from_moments
Nr = Nt = 4; N = Nr * Nt; SEED = 20260923; RHO_C = 0.7; LAM = 1e-6; I_N = np.eye(N)
RAW = os.path.join(HERE, "exp_0923_raw")
CASES = {"Tp4": 0, "Tp3": 1, "Tp2": 2, "aniso": 3}
RA_CFG = [(32, 12, 2), (32, 24, 4), (32, 48, 8), (8, 24, 4), (128, 24, 4)]                  # (M chains, L levels, K corrector steps)
METHODS = ["exact", "D13+D14", "LMMSE(I)", "PS-M8", "PS-M32", "PS-M128"] + [f"RA-M{M}-L{L}-K{K}" for M, L, K in RA_CFG] + ["RA-M32-L24-K4-J1", "PS-M32-J1"]
KEYS = ("se", "wt", "pm", "kl", "ce", "clip", "nfe")
_G = {}


def setup():
    if not _G:
        psis = 2 * np.pi * (np.arange(4) + 0.5) / 4
        prior = GMMPrior(Nr, Nt, [np.kron(steer_corr(Nt, RHO_C, pt).T, steer_corr(Nr, RHO_C, pr)) for pt in psis for pr in psis])
        _G.update(prior=prior, gb=GMMBatch(prior), Cinv=[np.linalg.inv(C) for C in prior.covs])
    return _G["prior"], _G["gb"], _G["Cinv"]


def pilots(case):
    F = dft_pilots(Nt, Nt)
    return {"Tp4": F, "Tp3": F[:, :3], "Tp2": F[:, :2], "aniso": np.concatenate([F[:, :2], np.sqrt(0.1) * F[:, 2:]], 1)}[case]


def exact_moments(prior, Cinv, G, b):
    S = [np.linalg.inv(Ci + G) for Ci in Cinv]; mk = [Sk @ b for Sk in S]
    lw = np.array([np.log(p) - np.linalg.slogdet(I_N + C @ G)[1] + (b.conj() @ m).real for p, C, m in zip(prior.pi, prior.covs, mk)])
    w = np.exp(lw - logsumexp(lw)); m = sum(wk * x for wk, x in zip(w, mk))
    Cov = sum(wk * (Sk + np.outer(x, x.conj())) for wk, Sk, x in zip(w, S, mk)) - np.outer(m, m.conj())
    return w, m, 0.5 * (Cov + Cov.conj().T)


def kl_gauss(m0, S0, m1, S1):
    """KL( CN(m0,S0) || CN(m1,S1) ) / N, complex Gaussians."""
    S1i = np.linalg.inv(S1); d = m1 - m0
    return (np.trace(S1i @ S0).real - N + (d.conj() @ S1i @ d).real + np.linalg.slogdet(S1)[1] - np.linalg.slogdet(S0)[1]) / N


def run_chunk(task):
    case, snr, t0, cnt = task; prior, gb, Cinv = setup(); cid = CASES[case]
    sigma2 = 10 ** (-snr / 10); Xp = pilots(case); Tp = Xp.shape[1]
    G = np.kron(Xp.conj() @ Xp.T, np.eye(Nr)) / sigma2
    SigL = np.linalg.inv(I_N / prior.cbar + G); aL = np.trace(SigL).real / (N * prior.cbar); nu_q = aL / (1 - aL) * prior.cbar
    out = {k: np.full((cnt, len(METHODS)), np.nan) for k in KEYS}; hn = np.empty(cnt); wchk = 0.0
    for j in range(cnt):
        tr = t0 + j; rng = np.random.default_rng([SEED, cid, snr, tr])
        H = prior.sample(rng); k = prior.last_k; h = H.reshape(-1, order="F"); hn[j] = np.sum(np.abs(h) ** 2)
        W = np.sqrt(sigma2 / 2) * (rng.standard_normal((Nr, Tp)) + 1j * rng.standard_normal((Nr, Tp)))
        Yp = H @ Xp + W; b = sum(np.kron(Xp[:, t].conj(), Yp[:, t]) for t in range(Tp)) / sigma2
        w_ex, m_ex, C_ex = exact_moments(prior, Cinv, G, b); nC = np.linalg.norm(C_ex)

        def put(name, m, Cov, wk, nfe=0):
            i = METHODS.index(name); out["se"][j, i] = np.sum(np.abs(m - h) ** 2); out["nfe"][j, i] = nfe
            if wk is not None: out["wt"][j, i] = wk[k]; out["pm"][j, i] = float(np.argmax(wk) == k)
            if Cov is not None:
                out["kl"][j, i] = kl_gauss(m_ex, C_ex, m, Cov); out["ce"][j, i] = np.linalg.norm(Cov - C_ex) / nC
                out["clip"][j, i] = float(site_from_moments(m, Cov, G, b, LAM)[2])

        put("exact", m_ex, C_ex, w_ex)
        q = (SigL @ b) / (1 - aL); w_iso, _, _ = prior._post(q, nu_q); h13, J = prior.denoise_full(q, nu_q)          # D-13 + D-14, as in exp_0922
        SigH = nu_q * J; SigH = 0.5 * (SigH + SigH.conj().T); SHi = np.linalg.inv(SigH)
        lam, U = np.linalg.eigh(SHi - I_N / nu_q); P = (U * np.maximum(lam, LAM)) @ U.conj().T + G; Pi = np.linalg.inv(P)
        put("D13+D14", Pi @ (SHi @ h13 - q / nu_q + b), 0.5 * (Pi + Pi.conj().T), w_iso); out["clip"][j, METHODS.index("D13+D14")] = float(lam.min() < LAM)
        put("LMMSE(I)", SigL @ b, SigL, None)
        for mi, name in enumerate(METHODS):
            if name.endswith("-J1") or not name[:2] in ("PS", "RA"): continue
            r2 = np.random.default_rng([SEED, cid, snr, tr, mi])
            if name.startswith("PS"):
                M = int(name[4:]); Z, nuL, wp = gmm_exact_zsample(prior, G, b, M, r2); nfe = 0; wchk = max(wchk, np.abs(wp - w_ex).max())
            else:
                M, L, K = (int(x[1:]) for x in name.split("-")[1:]); Z, nuL, nfe = ra_sample(gb.denoise, G, b, M, L, K, r2, cbar=prior.cbar)
            put(name, *rb_moments(gb, Z, nuL), nfe=nfe)
            if name + "-J1" in METHODS: put(name + "-J1", *rb_moments(gb, Z, nuL, jac="one"), nfe=nfe)
    return case, snr, t0, out, hn, wchk, float(nu_q * np.trace(G).real / N), float(nu_q)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--n", type=int, default=1000); ap.add_argument("--jobs", type=int, default=os.cpu_count())
    ap.add_argument("--chunk", type=int, default=25); ap.add_argument("--cases", default="Tp4,Tp3,Tp2,aniso"); ap.add_argument("--snr", default="6,12,18")
    warnings.simplefilter("ignore", RuntimeWarning)                                        # all-NaN columns (methods without P(k) / Cov)
    a = ap.parse_args(); cases = a.cases.split(","); snrs = [int(s) for s in a.snr.split(",")]; os.makedirs(RAW, exist_ok=True); t_start = time.time()
    tasks = [(c, s, t0, min(a.chunk, a.n - t0)) for t0 in range(0, a.n, a.chunk) for c in cases for s in snrs]
    if a.jobs > 1:
        with mp.Pool(a.jobs) as pool: res = pool.map(run_chunk, tasks, chunksize=1)
    else:
        res = [run_chunk(t) for t in tasks]
    print(f"exp_0923 R-A first pass, GMM rho_c={RHO_C}, 4x4, n={a.n}, seed {SEED}, delta=0.3, nu_1=10, K_fin=2K  ({time.time() - t_start:.0f} s)")
    for c in cases:
        for s in snrs:
            rs = sorted([r for r in res if r[0] == c and r[1] == s], key=lambda r: r[2])
            o = {k: np.concatenate([r[3][k] for r in rs]) for k in KEYS}; hn = np.concatenate([r[4] for r in rs]); wchk = max(r[5] for r in rs)
            np.savez_compressed(os.path.join(RAW, f"{c}_snr{s}.npz"), methods=np.array(METHODS), hn=hn, **o)
            print(f"\n[{c}  SNR {s} dB]  chi = {rs[0][6]:.2f}   nu_q(one-shot) = {rs[0][7]:.4f}   max|w'(perfect sampler) - w_exact| = {wchk:.1e}")
            print(f"  {'method':<18} {'NFE/ch':>6} {'NMSE':>7} {'vs exact':>8} {'w_true':>7} {'P_map':>6} {'KL/N':>8} {'KL med':>8} {'covErr':>7} {'clip%':>6}")
            e0 = o["se"][:, 0].sum() / hn.sum()
            for i, name in enumerate(METHODS):
                e = o["se"][:, i].sum() / hn.sum(); f = lambda x: f"{x:.3f}" if np.isfinite(x) else "-"
                print(f"  {name:<18} {np.nanmean(o['nfe'][:, i]):6.0f} {e:7.4f} {100 * (e / e0 - 1):+7.1f}% {f(np.nanmean(o['wt'][:, i])):>7} {f(np.nanmean(o['pm'][:, i])):>6}"
                      f" {np.nanmean(o['kl'][:, i]):8.4f} {np.nanmedian(o['kl'][:, i]):8.4f} {np.nanmean(o['ce'][:, i]):7.3f} {100 * np.nanmean(o['clip'][:, i]):6.1f}")
    print("\nread: (1) Tp4: RA/PS rows == D13+D14 == exact up to mixture-projection (lossless, NFE 0).  (2) PS-M* = Monte-Carlo floor of R-A at M chains (NMSE ~ exact (1 + c/M)).")
    print("      (3) RA rows -> PS row of the same M as L,K grow = sampler bias.  (4) decision: smallest (M, L, K) whose KL/N and NMSE gap are << those of D13+D14.  (5) -J1: is one Jacobian enough?")


if __name__ == "__main__":
    main()
