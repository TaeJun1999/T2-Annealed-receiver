#!/usr/bin/env python3
"""
exp_0917_onsager_small_N.py  (T2, Q-05: Onsager term for the channel denoiser at small N)

Gaussian channel prior with closed-form score, complex per-entry convention (D-01):
  h ~ CN(0, C), C = R_r (x) R_t, [R]_{ij} = rho^{|i-j|};  q = h + sqrt(nu) xi, xi ~ CN(0, I)
  s_c(q) = grad_{q*} log p(q) = -(C + nu I)^{-1} q ;  eta(q) = q + nu s_c(q) = C (C + nu I)^{-1} q
  exact alpha = (1/N) tr( C (C + nu I)^{-1} )          (Wirtinger d eta / d q, normalized trace)
Estimators compared (mean and std over draws):
  F1  SC-VAMP Fisher trick, single sample:  1 - (nu/N) ||s_c(q)||^2            [arXiv:2601.07095 eq.(47)-(48), B=1, complex form]
  FB  same with a mini-batch of B independent q's (only possible offline, not inside one receiver run)
  HK  Hutchinson with K complex probes on eta:  (1/(N K)) sum_k Re{ zeta_k^H (eta(q+e zeta_k)-eta(q))/e }
  EX  exact trace via 2N directional derivatives (deterministic; cost 2N denoiser calls or one Jacobian trace)
Also reports the induced relative error of the extrinsic variance v_ext = alpha/(1-alpha) nu.
"""
import numpy as np
rng = np.random.default_rng(20260917)

def kron_corr(Nr, Nt, rho):
    R = lambda n: rho ** np.abs(np.subtract.outer(np.arange(n), np.arange(n)))
    return np.kron(R(Nr), R(Nt)).astype(complex)

def run(Nr, Nt, rho, nu_list, draws=2000):
    N = Nr * Nt; C = kron_corr(Nr, Nt, rho)
    L = np.linalg.cholesky(C)
    print(f"\nN_r x N_t = {Nr}x{Nt} (N={N}), rho={rho}, {draws} draws")
    print(f"{'nu':>6} {'alpha':>7} | {'F1 mean':>8} {'F1 std':>7} | {'FB=8 std':>8} | {'H1 std':>7} {'H4 std':>7} {'H16 std':>8} | {'v_ext rel.err: F1':>18} {'H4':>7} {'H16':>7}")
    for nu in nu_list:
        G = C @ np.linalg.inv(C + nu * np.eye(N))          # eta(q) = G q
        Sinv = np.linalg.inv(C + nu * np.eye(N))
        alpha = np.trace(G).real / N
        F1 = np.zeros(draws); FB = np.zeros(draws // 8); H = {1: np.zeros(draws), 4: np.zeros(draws), 16: np.zeros(draws)}
        for d in range(draws):
            h = L @ (rng.standard_normal(N) + 1j * rng.standard_normal(N)) / np.sqrt(2)
            q = h + np.sqrt(nu / 2) * (rng.standard_normal(N) + 1j * rng.standard_normal(N))
            s = -Sinv @ q
            F1[d] = 1 - nu / N * np.vdot(s, s).real
            for K in H:
                Z = (rng.standard_normal((N, K)) + 1j * rng.standard_normal((N, K))) / np.sqrt(2)   # CN(0,1) probes
                H[K][d] = np.mean(np.real(np.sum(np.conj(Z) * (G @ Z), axis=0))) / N              # linear eta: exact directional derivative
        FB = F1.reshape(-1, 8).mean(1)
        rel = lambda a_hat: np.std(a_hat / (1 - a_hat) * nu) / (alpha / (1 - alpha) * nu)
        print(f"{nu:6.3f} {alpha:7.4f} | {F1.mean():8.4f} {F1.std():7.4f} | {FB.std():8.4f} | {H[1].std():7.4f} {H[4].std():7.4f} {H[16].std():8.4f} | "
              f"{rel(F1):18.3f} {rel(H[4]):7.3f} {rel(H[16]):7.3f}")
    print("EX: exact trace needs 2N real directional derivatives (2N =", 2 * N, ") or one autodiff Jacobian trace; std = 0.")

if __name__ == "__main__":
    NUS = [0.01, 0.1, 0.3, 1.0]
    run(8, 4, 0.7, NUS)
    run(8, 8, 0.7, NUS, draws=1000)
    run(32, 32, 0.7, [0.1, 1.0], draws=200)
