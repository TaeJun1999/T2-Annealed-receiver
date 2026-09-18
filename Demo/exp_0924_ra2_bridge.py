"""exp_0924 — Q-29: why did the v1 R-A sampler miss the exp_0923 criterion, and does the v2 bridge (posterior diffusion + exact handover) fix it?
Same GMM testbed, same first-pass data as exp_0923 (data rng = default_rng([20260923, case, snr, trial]) -> every row is PAIRED with exp_0923 rows).
Cases Tp3 / Tp2 / aniso x SNR 6/12/18 (Tp4 is trivially exact for every sampler: all coordinates clamped). M = 32 chains unless stated.

Diagnostic ladder (each rung isolates one error source):
  exact, D13+D14, PS-M32                as exp_0923 (PS = perfect sampler of pi'_{nu_L} = Monte-Carlo floor)
  RA-M32-L24-K4                         v1, same sampler seed as exp_0923 -> must REPRODUCE the exp_0923 row (regression)
  PSinit-K16 / PSinit-K128              perfect-sampler draws + K exact-target corrector steps at nu_L   -> is the final-level ULA corrector itself biased?
  RA2X-L{6,12,24}                       v2 bridge with the EXACT mixture posterior denoiser E[h|z,y], Cov   -> pure discretisation error of the ancestral chain
  RA2J-L{6,12,24}                       v2, moment-matched (Tweedie mean + Jacobian, = D-14 at every step) -> cost of the Gaussian guidance approximation
  RA2S-L{12,24}                         v2, scalar Jacobian surrogate (no Jacobian)                        -> is a Jacobian needed in the bridge?
  RA2J-L12-K8                           v2-J + 8 exact-target corrector steps after the handover
  RA2J-L12-M128                         v2-J, 128 chains
Columns: NFE = denoiser calls per chain, nJ = Jacobians per chain (bridge only; the final Rao-Blackwell step uses all-chain J here, exp_0923 showed one J suffices),
  NMSE (+% vs exact), w_true, P_map, KL/N mean/median/99%, KLc/N = same KL after the EP-site round trip (Lambda clipped at 1e-6; what the receiver would see), covErr, clip%.
usage: python exp_0924_ra2_bridge.py [--n 1000] [--jobs all] [--chunk 25] [--cases Tp3,Tp2,aniso] [--snr 6,12,18]"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"): os.environ.setdefault(_v, "1")
import sys, time, argparse, warnings, multiprocessing as mp, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from scipy.special import logsumexp
from t2_route_a import GMMPrior, steer_corr, dft_pilots
import t2_ra_sampler as ra
assert hasattr(ra, "ra2_sample"), "t2_ra_sampler.py is not the exp_0924 version (needs ra2_sample / PostDenoiser / corrector_from)"
Nr = Nt = 4; N = Nr * Nt; SEED = 20260923; RHO_C = 0.7; LAM = 1e-6; I_N = np.eye(N)
RAW = os.path.join(HERE, "exp_0924_raw"); CASES = {"Tp4": 0, "Tp3": 1, "Tp2": 2, "aniso": 3}
# name -> sampler-seed id (RA-M32-L24-K4 keeps its exp_0923 id 7, PS-M32 its id 4)
METHODS = {"exact": 0, "D13+D14": 1, "PS-M32": 4, "RA-M32-L24-K4": 7, "PSinit-K16": 101, "PSinit-K128": 102,
           "RA2X-L6": 110, "RA2X-L12": 111, "RA2X-L24": 112, "RA2J-L6": 120, "RA2J-L12": 121, "RA2J-L24": 122, "RA2S-L12": 131, "RA2S-L24": 132,
           "RA2J-L12-K8": 141, "RA2J-L12-M128": 142}
NAMES = list(METHODS); KEYS = ("se", "wt", "pm", "kl", "klc", "ce", "clip", "nfe", "njac")
_G = {}


def setup():
    if not _G:
        psis = 2 * np.pi * (np.arange(4) + 0.5) / 4
        prior = GMMPrior(Nr, Nt, [np.kron(steer_corr(Nt, RHO_C, pt).T, steer_corr(Nr, RHO_C, pr)) for pt in psis for pr in psis])
        _G.update(prior=prior, gb=ra.GMMBatch(prior), Cinv=[np.linalg.inv(C) for C in prior.covs], xcache={})
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
    S1i = np.linalg.inv(S1); d = m1 - m0
    return (np.trace(S1i @ S0).real - N + (d.conj() @ S1i @ d).real + np.linalg.slogdet(S1)[1] - np.linalg.slogdet(S0)[1]) / N


def run_chunk(task):
    case, snr, t0, cnt = task; prior, gb, Cinv = setup(); cid = CASES[case]; xc = _G["xcache"].setdefault((case, snr), {})
    sigma2 = 10 ** (-snr / 10); Xp = pilots(case); Tp = Xp.shape[1]
    G = np.kron(Xp.conj() @ Xp.T, np.eye(Nr)) / sigma2
    SigL = np.linalg.inv(I_N / prior.cbar + G); aL = np.trace(SigL).real / (N * prior.cbar); nu_q = aL / (1 - aL) * prior.cbar
    out = {k: np.full((cnt, len(NAMES)), np.nan) for k in KEYS}; hn = np.empty(cnt)
    for j in range(cnt):
        tr = t0 + j; rng = np.random.default_rng([SEED, cid, snr, tr])
        H = prior.sample(rng); k = prior.last_k; h = H.reshape(-1, order="F"); hn[j] = np.sum(np.abs(h) ** 2)
        W = np.sqrt(sigma2 / 2) * (rng.standard_normal((Nr, Tp)) + 1j * rng.standard_normal((Nr, Tp)))
        Yp = H @ Xp + W; b = sum(np.kron(Xp[:, t].conj(), Yp[:, t]) for t in range(Tp)) / sigma2
        w_ex, m_ex, C_ex = exact_moments(prior, Cinv, G, b); nC = np.linalg.norm(C_ex)

        def put(name, m, Cov, wk, nfe=0, njac=0):
            i = NAMES.index(name); out["se"][j, i] = np.sum(np.abs(m - h) ** 2); out["nfe"][j, i] = nfe; out["njac"][j, i] = njac
            out["wt"][j, i] = wk[k]; out["pm"][j, i] = float(np.argmax(wk) == k)
            out["kl"][j, i] = kl_gauss(m_ex, C_ex, m, Cov); out["ce"][j, i] = np.linalg.norm(Cov - C_ex) / nC
            Lam, eta, clipped = ra.site_from_moments(m, Cov, G, b, LAM); Sc = np.linalg.inv(Lam + G); Sc = 0.5 * (Sc + Sc.conj().T)
            out["clip"][j, i] = float(clipped); out["klc"][j, i] = kl_gauss(m_ex, C_ex, Sc @ (eta + b), Sc)

        put("exact", m_ex, C_ex, w_ex)
        q = (SigL @ b) / (1 - aL); w_iso, _, _ = prior._post(q, nu_q); h13, J = prior.denoise_full(q, nu_q)
        SigH = nu_q * J; SigH = 0.5 * (SigH + SigH.conj().T); SHi = np.linalg.inv(SigH)
        lam, U = np.linalg.eigh(SHi - I_N / nu_q); Pi = np.linalg.inv((U * np.maximum(lam, LAM)) @ U.conj().T + G)
        i = NAMES.index("D13+D14"); m14 = Pi @ (SHi @ h13 - q / nu_q + b); P14 = 0.5 * (Pi + Pi.conj().T)
        out["se"][j, i] = np.sum(np.abs(m14 - h) ** 2); out["wt"][j, i] = w_iso[k]; out["pm"][j, i] = float(np.argmax(w_iso) == k); out["nfe"][j, i] = 1; out["njac"][j, i] = 1
        out["kl"][j, i] = out["klc"][j, i] = kl_gauss(m_ex, C_ex, m14, P14); out["ce"][j, i] = np.linalg.norm(P14 - C_ex) / nC; out["clip"][j, i] = float(lam.min() < LAM)
        for name, sid in METHODS.items():
            if sid < 2: continue
            r2 = np.random.default_rng([SEED, cid, snr, tr, sid]); nfe = njac = 0; p = name.split("-")
            if name == "PS-M32":
                Z, nuL, _ = ra.gmm_exact_zsample(prior, G, b, 32, r2)
            elif name == "RA-M32-L24-K4":
                Z, nuL, nfe = ra.ra_sample(gb.denoise, G, b, 32, 24, 4, r2, cbar=prior.cbar)
            elif p[0] == "PSinit":
                Z, nuL, _ = ra.gmm_exact_zsample(prior, G, b, 32, r2); K = int(p[1][1:]); Z = ra.corrector_from(gb.denoise, Z, G, b, K, r2); nfe = K
            else:
                kind = p[0][3]; L = int(p[1][1:]); M = 32; Kf = 0
                for t in p[2:]:
                    if t[0] == "K": Kf = int(t[1:])
                    if t[0] == "M": M = int(t[1:])
                pd = ra.PostDenoiser(kind, prior, gb, G, b, cache=xc); Z, nuL, nfe = ra.ra2_sample(pd, gb.denoise, G, b, M, L, r2, K_fin=Kf, cbar=prior.cbar); njac = pd.n_jac
            put(name, *ra.rb_moments(gb, Z, nuL), nfe=nfe, njac=njac)
    return case, snr, t0, out, hn, float(nu_q * np.trace(G).real / N)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--n", type=int, default=1000); ap.add_argument("--jobs", type=int, default=os.cpu_count())
    ap.add_argument("--chunk", type=int, default=25); ap.add_argument("--cases", default="Tp3,Tp2,aniso"); ap.add_argument("--snr", default="6,12,18")
    warnings.simplefilter("ignore", RuntimeWarning)
    a = ap.parse_args(); cases = a.cases.split(","); snrs = [int(s) for s in a.snr.split(",")]; os.makedirs(RAW, exist_ok=True); t_start = time.time()
    tasks = [(c, s, t0, min(a.chunk, a.n - t0)) for t0 in range(0, a.n, a.chunk) for c in cases for s in snrs]
    if a.jobs > 1:
        with mp.Pool(a.jobs) as pool: res = pool.map(run_chunk, tasks, chunksize=1)
    else:
        res = [run_chunk(t) for t in tasks]
    print(f"exp_0924 R-A v2 bridge ladder, GMM rho_c={RHO_C}, 4x4, first pass, n={a.n}, data seed {SEED} (paired with exp_0923), M=32, nu_1=10  ({time.time() - t_start:.0f} s)")
    for c in cases:
        for s in snrs:
            rs = sorted([r for r in res if r[0] == c and r[1] == s], key=lambda r: r[2])
            o = {k: np.concatenate([r[3][k] for r in rs]) for k in KEYS}; hn = np.concatenate([r[4] for r in rs])
            np.savez_compressed(os.path.join(RAW, f"{c}_snr{s}.npz"), methods=np.array(NAMES), hn=hn, **o)
            reg = ""; f23 = os.path.join(HERE, "exp_0923_raw", f"{c}_snr{s}.npz")
            if os.path.exists(f23):                                                         # regression against the exp_0923 raw log (same trials, same sampler seed)
                d = np.load(f23); m23 = list(d["methods"]); nn = min(len(hn), len(d["hn"]))
                reg = "   v1 regression max|se - se(exp_0923)| = " + f"{np.abs(o['se'][:nn, NAMES.index('RA-M32-L24-K4')] - d['se'][:nn, m23.index('RA-M32-L24-K4')]).max():.1e}"
            print(f"\n[{c}  SNR {s} dB]  chi = {rs[0][5]:.2f}{reg}")
            print(f"  {'method':<16} {'NFE':>4} {'nJ':>3} {'NMSE':>7} {'vs exact':>8} {'w_true':>7} {'P_map':>6} {'KL/N':>7} {'KL med':>7} {'KL 99%':>7} {'KLc/N':>7} {'covErr':>7} {'clip%':>6}")
            e0 = o["se"][:, 0].sum() / hn.sum()
            for i, name in enumerate(NAMES):
                e = o["se"][:, i].sum() / hn.sum()
                print(f"  {name:<16} {np.nanmean(o['nfe'][:, i]):4.0f} {np.nanmean(o['njac'][:, i]):3.0f} {e:7.4f} {100 * (e / e0 - 1):+7.1f}% {np.nanmean(o['wt'][:, i]):7.3f} {np.nanmean(o['pm'][:, i]):6.3f}"
                      f" {np.nanmean(o['kl'][:, i]):7.4f} {np.nanmedian(o['kl'][:, i]):7.4f} {np.nanquantile(o['kl'][:, i], .99):7.3f} {np.nanmean(o['klc'][:, i]):7.4f} {np.nanmean(o['ce'][:, i]):7.3f} {100 * np.nanmean(o['clip'][:, i]):6.1f}")
    print("\nread: PSinit ~ PS -> final-level corrector is unbiased.  RA2X -> PS as L grows = discretisation only;  RA2J - RA2X = Gaussian-guidance loss;  RA2S - RA2J = value of the Jacobian in the bridge.")


if __name__ == "__main__":
    main()
