"""exp_0922 — Q-27: what does the one-shot ISOTROPIC denoiser interface (D-13 + D-14) lose against the exact mixture posterior?
First pass only (pilots, no decoder): GMM testbed of exp_0920 (16 directional components, ensemble covariance = I), 4x4, DFT pilots.

Closed form to be checked [exact; projector model G = g Pi, rank(Pi) = kappa N, isotropic prior-site (hE, nuE)]:
    alpha_L = (1 - kappa) + kappa / (1 + g nuE),   nu_q = ((1 - kappa) / kappa) nuE + 1 / (kappa g),   q = hE + Pi (y - hE) / kappa  (g -> inf)
  -> for kappa < 1 (Tp < Nt) the denoiser input noise nu_q does NOT vanish with SNR (floor ((1-kappa)/kappa) nuE; = 1 for Tp = 2, nuE = 1),
     and the unobserved directions are fed the receiver's own previous estimate (q = hE there) as if it were an observation.
     For Tp = Nt with DFT pilots G = (Nt / sigma2) I, kappa = 1: nu_q = sigma2 / Nt, the interface is lossless.

Per (Tp, SNR) the script prints, over n trials:
  nu_q   : measured mean (design-note formula, first pass) vs the closed form above; cross-check against RouteA's own log on the first trials
  P_map  : P(argmax_k w_k = true component)  and  E[w_true]  for  exact  w_k(G, b)  vs  isotropic  w_k(q, nu_q)
  NMSE   : sum ||h_hat - h||^2 / sum ||h||^2  for  (a) exact mixture posterior mean, (b) one-shot denoiser mean h_post(q, nu_q) [D-13],
           (c) mean after the D-14 matrix site  P^-1 (eta_E + b), (d) LMMSE with the ensemble covariance (= I), (e) oracle component LMMSE
usage: python exp_0922_interface.py [n=2000]        (seconds; seed 20260922)"""
import sys, os, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from scipy.special import logsumexp
from t2_route_a import GMMPrior, steer_corr, dft_pilots, QAMCode, RouteA
Nr = Nt = 4; N = Nr * Nt; SEED = 20260922; RHO_C = 0.7; LAM = 1e-6
n = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
psis = 2 * np.pi * (np.arange(4) + 0.5) / 4
prior = GMMPrior(Nr, Nt, [np.kron(steer_corr(Nt, RHO_C, pt).T, steer_corr(Nr, RHO_C, pr)) for pt in psis for pr in psis])
Cinv = [np.linalg.inv(C) for C in prior.covs]; I_N = np.eye(N)


def exact_post(G, b):
    """exact tilted mixture: w_k ∝ pi_k det(I + C_k G)^-1 exp(b^H S_k b), S_k = (C_k^-1 + G)^-1, m_k = S_k b."""
    S = [np.linalg.inv(Ci + G) for Ci in Cinv]; m = [Sk @ b for Sk in S]
    lw = np.array([np.log(p) - np.linalg.slogdet(I_N + C @ G)[1] + (b.conj() @ mk).real for p, C, mk in zip(prior.pi, prior.covs, m)])
    w = np.exp(lw - logsumexp(lw)); return w, sum(wk * mk for wk, mk in zip(w, m)), m


print(f"exp_0922 Q-27 interface loss, first pass, GMM rho_c={RHO_C}, 4x4, DFT pilots, n={n}, seed {SEED}")
print(f"{'Tp':>3} {'SNR':>4} | {'nu_q meas':>9} {'closed':>7} {'RouteA':>7} | {'Pmap ex':>7} {'Pmap iso':>8} {'w_true ex':>9} {'w_true iso':>10} |"
      f" {'NMSE exact':>10} {'D13 1shot':>9} {'D13+D14':>8} {'LMMSE(I)':>8} {'oracle':>7}")
for Tp in (4, 3, 2):
    Xp = dft_pilots(Nt, Tp); kappa = Tp / Nt
    for snr in (6, 12, 18):
        sigma2 = 10 ** (-snr / 10); rng = np.random.default_rng(SEED + 100 * Tp + snr)
        G = np.kron(Xp.conj() @ Xp.T, np.eye(Nr)) / sigma2; g = Nt / sigma2
        SigL = np.linalg.inv(I_N / prior.cbar + G); aL = np.trace(SigL).real / (N * prior.cbar); nu_q = aL / (1 - aL) * prior.cbar
        closed = (1 - kappa) / kappa * prior.cbar + 1 / (kappa * g) if kappa < 1 else 1 / g
        code = QAMCode(("133", "171"), 6, 2, Nt * (28 - Tp)); rx = RouteA(Nr, Nt, 28, Tp, sigma2, prior, code, mode="scalar", scal="belief", hsite="matrix", lam_min=LAM)
        acc = dict(pe=0, pi=0, we=0.0, wi=0.0, e=np.zeros(5), hn=0.0); nu_rx = []
        for tr in range(n):
            H = prior.sample(rng); k = prior.last_k; h = H.reshape(-1, order="F")
            W = np.sqrt(sigma2 / 2) * (rng.standard_normal((Nr, Tp)) + 1j * rng.standard_normal((Nr, Tp)))
            Yp = H @ Xp + W; b = sum(np.kron(Xp[:, t].conj(), Yp[:, t]) for t in range(Tp)) / sigma2
            w_ex, m_ex, m_k = exact_post(G, b)
            q = (SigL @ b) / (1 - aL)                                                     # hE = 0 at the first pass
            w_iso, _, _ = prior._post(q, nu_q); h13, J = prior.denoise_full(q, nu_q)
            SigH = nu_q * J; SigH = 0.5 * (SigH + SigH.conj().T); SHi = np.linalg.inv(SigH)
            lam, U = np.linalg.eigh(SHi - I_N / nu_q); Lam = (U * np.maximum(lam, LAM)) @ U.conj().T
            h14 = np.linalg.solve(Lam + G, SHi @ h13 - q / nu_q + b)
            hI = np.linalg.solve(I_N / prior.cbar + G, b)
            acc["pe"] += int(np.argmax(w_ex) == k); acc["pi"] += int(np.argmax(w_iso) == k); acc["we"] += w_ex[k]; acc["wi"] += w_iso[k]
            acc["e"] += [np.sum(np.abs(x - h) ** 2) for x in (m_ex, h13, h14, hI, m_k[k])]; acc["hn"] += np.sum(np.abs(h) ** 2)
            if tr < 3:                                                                   # cross-check with the receiver's own first-pass nu_q
                u = rng.integers(0, 2, code.K); perm = rng.permutation(code.Ns); X, Y = rx.transmit(u, perm, H, rng); nu_rx.append(rx.run(Y, H, u, perm, 1)["nu_q"][0])
        e = acc["e"] / acc["hn"]
        print(f"{Tp:>3} {snr:>4} | {nu_q:9.4f} {closed:7.4f} {np.mean(nu_rx):7.4f} | {acc['pe'] / n:7.3f} {acc['pi'] / n:8.3f} {acc['we'] / n:9.3f} {acc['wi'] / n:10.3f} |"
              f" {e[0]:10.4f} {e[1]:9.4f} {e[2]:8.4f} {e[3]:8.4f} {e[4]:7.4f}", flush=True)
print("read: Tp=4 -> all columns should coincide (lossless interface). Tp<4 -> 'closed' floor ~ (1-kappa)/kappa, Pmap iso << Pmap ex, NMSE D13+D14 > exact.")
