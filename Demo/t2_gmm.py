"""t2_gmm.py — exp_0925 (D-18 Module H-GMM, D-19 kill test). t2_route_a.py is NOT modified (regression tests t0/t6 depend on it).

  GMMPriorB        drop-in subclass of t2_route_a.GMMPrior with batched linear algebra (K up to ~1e3 components, N = Nr*Nt <= 32):
                   ep_site (exact mixture-EP prior site), denoise_full (isotropic-noise denoiser + full Jacobian), log_pdf, sample_vecs.
                   Same formulas as the parent (unit test T1/T2: <= 1e-12 against the parent's loop versions).
  fit_gmm_em       EM for  p(h) = sum_k pi_k CN(h; 0, C_k)  (zero-mean circular complex components, full covariances).
                   Prior art of "fit a GMM to channel samples, then closed-form CME": Koller-Fesl-Turan-Utschick, IEEE TSP 2022 (arXiv:2112.12499) [V: abstract].
  angle_grid_prior "true" priors of exp_0925: a DENSE Kg x Kg grid mixture over (psi_t, psi_r) that DEFINES the continuous-angle prior
                   (C = kron(R_t(psi_t)^T, R_r(psi_r)), R(psi) = steer_corr(n, rho_c, psi)); not representable by a K <= 64 mixture.

Notation (D-01): complex per-entry variances, h = vec(H) column-major, E[h h^H] = C.
EM [exact]:  E-step  gamma_ik ∝ pi_k CN(h_i; 0, C_k);   M-step  pi_k = n_k / n,  C_k = (1/n_k) sum_i gamma_ik h_i h_i^H  (+ floor * cbar * I),  n_k = sum_i gamma_ik.
  Identity [exact, floor = 0]: after every M-step  sum_k pi_k C_k = (1/n) sum_i h_i h_i^H  = the sample covariance  -> the second-moment method 'lmmseC' sees
  exactly the ensemble covariance of the fitted mixture.
  Initialisation: zero-mean components make k-means on h meaningless (h and e^{j phi} h are equivalent) -> 'seed' init:  C_k^(0) = Chat/2 + (N cbar / |h_s|^2) h_s h_s^H / 2
  for K random training samples h_s (the first E-step then clusters by alignment with the seeds); several restarts, selected by VALIDATION log-likelihood."""
import numpy as np
from scipy.special import logsumexp
from t2_route_a import GMMPrior, RouteA, steer_corr


def _cn(rng, shape):
    return (rng.standard_normal(shape) + 1j * rng.standard_normal(shape)) / np.sqrt(2)


class GMMPriorB(GMMPrior):
    def __init__(self, Nr, Nt, covs, weights=None):
        self.Nr, self.Nt, self.N = Nr, Nt, Nr * Nt
        covs = np.asarray(covs, complex); covs = 0.5 * (covs + covs.conj().transpose(0, 2, 1))
        self.K = len(covs); self.pi = np.full(self.K, 1.0 / self.K) if weights is None else np.asarray(weights, float) / np.sum(weights)
        self.covs = covs                                                                 # (K,N,N); iterates like the parent's list
        lam, U = np.linalg.eigh(covs)
        assert lam.min() > 0, "singular component covariance (use a covariance floor in the fit)"
        self.lam, self.U = lam, U                                                        # (K,N), (K,N,N)
        self.C = np.einsum("k,kij->ij", self.pi, covs); self.C = 0.5 * (self.C + self.C.conj().T); self.Cinv = np.linalg.inv(self.C)
        self.cbar = np.trace(self.C).real / self.N
        self.eh2_prior = np.diag(self.C).real.reshape(Nr, Nt, order="F").mean(0)
        self.last_k = None
        self.covinv = np.linalg.inv(covs); self.covinv = 0.5 * (self.covinv + self.covinv.conj().transpose(0, 2, 1))
        self.logdetC = np.sum(np.log(lam), 1); self.logpi = np.log(self.pi)
        self.clip = "eta"; self.reset_stats()

    # ---- exact mixture-EP prior site (batched version of GMMPrior.ep_site; same formulas)
    def tilted_moments(self, G, b):
        """pi(h) ∝ p(h) exp(-h^H G h + 2 Re b^H h) = sum_k w_k CN(mu_k, Sig_k):  Sig_k = (C_k^-1 + G)^-1, mu_k = Sig_k b,
        log w_k = log pi_k - log det(I + C_k G) + b^H Sig_k b,   log det(I + C_k G) = log det C_k + log det(C_k^-1 + G).   -> (w, m, Cov) of pi."""
        A = self.covinv + G
        Sig = np.linalg.inv(A); mu = Sig @ b                                             # (K,N,N), (K,N)
        lw = self.logpi - (self.logdetC + np.linalg.slogdet(A)[1]) + np.real(mu @ b.conj())
        w = np.exp(lw - logsumexp(lw)); m = w @ mu
        Cov = np.einsum("k,kij->ij", w, Sig) + (mu.T * w) @ mu.conj() - np.outer(m, m.conj())
        return w, m, 0.5 * (Cov + Cov.conj().T)

    def ep_site(self, G, b, lam_min=0.0):
        """Moment-matched Gaussian (m, Cov) -> prior site  Lambda = Cov^-1 - G,  eta = Cov^-1 m - b;  eigenvalues of Lambda clipped at lam_min.
        self.clip = 'eta'  (legacy = parent): eta is kept when Lambda is clipped -> belief mean (Lam_c + G)^-1 Cov^-1 m  != m.
        self.clip = 'mean' (exp_0925 diagnostic): eta = (Lam_c + G) m - b -> belief mean = m  [exact: KL(CN(m,Cov) || CN(mu, P^-1)) is minimised at mu = m for fixed P].
        Counters (reset by .reset_stats()): n_site, n_clip, shift = sum over clipped calls of |mu_legacy - m|^2 / |m|^2 (what 'eta' costs / 'mean' avoids)."""
        w, m, Cov = self.tilted_moments(G, b); self.last_w = w
        Ci = np.linalg.inv(Cov); Lam = Ci - G; Lam = 0.5 * (Lam + Lam.conj().T); eta = Ci @ m - b
        ev, V = np.linalg.eigh(Lam); self.n_site += 1
        if ev.min() < lam_min:
            Lam = (V * np.maximum(ev, lam_min)) @ V.conj().T; self.n_clip += 1
            mu = np.linalg.solve(Lam + G, eta + b); self.shift += float(np.sum(np.abs(mu - m) ** 2) / max(np.sum(np.abs(m) ** 2), 1e-300))
            if self.clip == "mean": eta = (Lam + G) @ m - b
        return Lam, eta

    def reset_stats(self):
        self.n_site = 0; self.n_clip = 0; self.shift = 0.0

    def view(self, clip="eta"):
        """Shallow copy sharing all arrays, with its own clip rule and counters (one view per receiver arm)."""
        import copy
        v = copy.copy(self); v.clip = clip; v.reset_stats(); return v

    # ---- isotropic-noise denoiser with full Jacobian (one GEMM instead of the parent's (K,N,N) einsum)
    def denoise_full(self, q, nu):
        w, g, mk = self._post(q, nu); m = w @ mk
        X = (self.U * np.sqrt(w[:, None] * nu * g)[:, None, :]).transpose(1, 0, 2).reshape(self.N, -1)     # sum_k w_k U_k diag(nu g_k) U_k^H = X X^H
        Cov = X @ X.conj().T + (mk.T * w) @ mk.conj() - np.outer(m, m.conj())
        return m, Cov / nu

    # ---- utilities
    def sample_vecs(self, rng, n):
        """n iid channel vectors (n,N) and their component indices (n,) — for training / validation sets (NOT the trial stream; trials use .sample)."""
        ks = rng.choice(self.K, size=n, p=self.pi); Z = _cn(rng, (n, self.N)); X = np.empty((n, self.N), complex)
        for k in np.unique(ks):
            i = ks == k; X[i] = (Z[i] * np.sqrt(self.lam[k])) @ self.U[k].T
        return X, ks

    def log_pdf(self, X):
        """log p(h_i) of the clean prior for the rows of X -> (n,)."""
        lw = np.empty((len(X), self.K))
        for k in range(self.K):
            Z = X @ self.U[k].conj()                                                     # rows U_k^H h
            lw[:, k] = -np.sum((Z.real ** 2 + Z.imag ** 2) / self.lam[k], 1)
        return logsumexp(lw + self.logpi - self.logdetC - self.N * np.log(np.pi), 1)


# ----------------------------------------------------------------------------- receiver variant: clip rule of the Jacobian (D-14) site + clip statistics
class RouteAClip(RouteA):
    """RouteA with the D-14 matrix site re-implemented to (i) count clips and (ii) offer the mean-preserving clip. clip='eta' reproduces RouteA._matrix_site exactly
    (unit test T6: identical logs). Site from the denoiser stage: belief_H = CN(hH, nu J) against the isotropic cavity CN(q, nu I):
        Lambda = (nu J)^-1 - I/nu,   eta = (nu J)^-1 hH - q/nu;     clip='mean':  eta = (Lambda_c + I/nu) hH - q/nu   (denoiser-stage belief mean stays hH)."""

    def __init__(self, *a, clip="eta", **kw):
        super().__init__(*a, **kw); assert clip in ("eta", "mean"); self.clip = clip; self.reset_stats()

    def reset_stats(self):
        self.n_site = 0; self.n_clip = 0; self.shift = 0.0

    def _matrix_site(self, q, nu_q, G):
        hH, J = self.prior.denoise_full(q, nu_q)
        SigH = nu_q * J; SigH = 0.5 * (SigH + SigH.conj().T)
        SigHinv = np.linalg.inv(SigH)
        Lam = SigHinv - self.I_N / nu_q; Lam = 0.5 * (Lam + Lam.conj().T)
        w, V = np.linalg.eigh(Lam); eta = SigHinv @ hH - q / nu_q; self.n_site += 1
        if w.min() < self.lam_min:
            Lam = (V * np.maximum(w, self.lam_min)) @ V.conj().T; self.n_clip += 1
            mu = np.linalg.solve(Lam + self.I_N / nu_q, eta + q / nu_q); self.shift += float(np.sum(np.abs(mu - hH) ** 2) / max(np.sum(np.abs(hH) ** 2), 1e-300))
            if self.clip == "mean": eta = (Lam + self.I_N / nu_q) @ hH - q / nu_q
        return Lam + G, eta


# ----------------------------------------------------------------------------- EM fit
def _loglik(X, logpi, covs):
    """(n,K) matrix of log pi_k + log CN(x_i; 0, C_k)."""
    n, N = X.shape; K = len(covs); L = np.linalg.cholesky(covs); Linv = np.linalg.inv(L)
    logdet = 2 * np.sum(np.log(np.real(np.diagonal(L, axis1=1, axis2=2))), 1); lw = np.empty((n, K))
    for k in range(K):
        Z = X @ Linv[k].T                                                                # rows L_k^-1 x_i
        lw[:, k] = -np.sum(Z.real ** 2 + Z.imag ** 2, 1)
    return lw + logpi - logdet - N * np.log(np.pi)


def fit_gmm_em(X, K, rng, n_iter=500, tol=1e-6, floor=1e-4, kappa=0.0, struct="full", dims=None, Xval=None, val_every=10, patience=40, log=None):
    """EM for  p(h) = sum_k pi_k CN(h; 0, C_k).  X (n,N) zero-mean complex samples.
    struct='full': C_k = (n_k S_k + kappa Chat) / (n_k + kappa) + floor cbar I,  S_k = (1/n_k) sum_i gamma_ik h_i h_i^H   (kappa = 0: plain ML EM; kappa > 0: MAP-EM
                   shrinkage towards the sample covariance Chat with pseudo-count kappa — regulariser against the over-fit of N x N covariances from n_k ~ n/K samples).
    struct='kron': C_k = kron(T_k, R_k), dims = (Nr, Nt), T_k (Nt x Nt, = R_t^T in the notation of t2_route_a), R_k (Nr x Nr); M-step = 3 flip-flop sweeps of the
                   weighted matrix-normal ML equations  R = sum_i g_i H_i T^-T H_i^H / (n_k Nt),  T^T = sum_i g_i H_i^H R^-1 H_i / (n_k Nr)  (generalised EM: every sweep
                   increases the expected complete-data log-likelihood), normalised to tr T = Nt.  Structured-covariance GMM channel estimators: arXiv:2205.03634 [V: title only].
    Xval given: validation log-likelihood every val_every iterations, the BEST-validation parameters are returned (early stopping, patience in iterations).
    Stops when the per-sample train log-likelihood gain < tol * |ll| (after >= 20 iterations), on patience, or at n_iter."""
    n, N = X.shape; Chat = X.T @ X.conj() / n; cbar = np.trace(Chat).real / N; I = np.eye(N)
    if struct == "kron":
        Nr, Nt = dims; assert Nr * Nt == N
        Hs = X.reshape(n, Nt, Nr).transpose(0, 2, 1)                                     # H_i (Nr x Nt), column-major vec
        H2 = Hs.transpose(0, 2, 1).reshape(n * Nt, Nr); H3 = Hs.reshape(n * Nr, Nt)

    def seed_cov(i):
        s = X[i]; return 0.5 * Chat + 0.5 * (N * cbar / np.vdot(s, s).real) * np.outer(s, s.conj())

    covs = np.array([seed_cov(i) for i in rng.choice(n, K, replace=False)]); logpi = np.full(K, -np.log(K)); ll = []; n_reseed = 0
    Tk = np.array([np.eye(Nt, dtype=complex)] * K) if struct == "kron" else None
    best = dict(ll_val=-np.inf, it=0, pi=np.exp(logpi), covs=covs.copy()); llv = []
    for it in range(n_iter):
        lw = _loglik(X, logpi, covs); lse = logsumexp(lw, 1); ll.append(float(lse.mean()))
        if Xval is not None and it % val_every == 0:
            v = float(logsumexp(_loglik(Xval, logpi, covs), 1).mean()); llv.append((it, v))
            if v > best["ll_val"]: best = dict(ll_val=v, it=it, pi=np.exp(logpi), covs=covs.copy())
            elif it - best["it"] >= patience: break
        if log is not None and it % 25 == 0: log(f"    it {it:>3} ll/sample = {ll[-1]:.4f}" + (f"  val {llv[-1][1]:.4f}" if llv else ""))
        if it >= 20 and ll[-1] - ll[-2] < tol * abs(ll[-1]): break
        gam = np.exp(lw - lse[:, None]); nk = gam.sum(0)
        for k in range(K):
            if nk[k] < (N if struct == "full" else 4):                                   # starved component -> re-seed (breaks monotonicity once; counted)
                covs[k] = seed_cov(int(rng.integers(n))); nk[k] = max(nk[k], 1.0); n_reseed += 1
                if struct == "kron": Tk[k] = np.eye(Nt)
                continue
            g = gam[:, k]
            if struct == "full":
                Xw = X * np.sqrt(g)[:, None]; S = Xw.T @ Xw.conj() / nk[k]
                S = (nk[k] * S + kappa * Chat) / (nk[k] + kappa); covs[k] = 0.5 * (S + S.conj().T) + floor * cbar * I
            else:
                T = Tk[k]
                for _ in range(3):
                    A = (Hs @ np.linalg.inv(T).T) * g[:, None, None]                     # g_i H_i T^-T
                    R = A.transpose(0, 2, 1).reshape(n * Nt, Nr).T @ H2.conj() / (nk[k] * Nt); R = 0.5 * (R + R.conj().T) + floor * cbar * np.eye(Nr)
                    B = (np.linalg.inv(R) @ Hs) * g[:, None, None]                       # g_i R^-1 H_i
                    Tt = H3.conj().T @ B.reshape(n * Nr, Nt) / (nk[k] * Nr); T = Tt.T; T = 0.5 * (T + T.conj().T)
                    c = np.trace(T).real / Nt; T = T / c + floor * np.eye(Nt); R = R * c
                Tk[k] = T; covs[k] = np.kron(T, R)
        logpi = np.log(nk / nk.sum())
    out = dict(pi=np.exp(logpi), covs=covs, ll=np.array(ll), n_iter=len(ll), n_reseed=n_reseed, Chat=Chat, it_best=len(ll) - 1, ll_val=np.nan)
    if Xval is not None: out.update(pi=best["pi"], covs=best["covs"], it_best=best["it"], ll_val=best["ll_val"], ll_val_traj=np.array(llv))
    return out


# ----------------------------------------------------------------------------- "true" priors of exp_0925
PRIOR_DOC = {
    "U": "psi_t, psi_r ~ U[0, 2pi)  (grid midpoints)  -> ensemble covariance = I exactly (second moments carry NO information)",
    "S": "psi_t, psi_r ~ U[-pi/3, pi/3]  (D-19 literal: +-60 deg in the ELECTRICAL angle = +-19.5 deg physical for a lambda/2 ULA) -> informative ensemble covariance on both sides",
    "P": "psi_t ~ U[0, 2pi),  psi_r = pi sin(theta), theta ~ U[-60 deg, 60 deg]  (lambda/2 ULA, standard 120-deg sector at the receiver) -> ensemble covariance nearly white",
}


def angle_grids(kind, Kg):
    a = (np.arange(Kg) + 0.5) / Kg
    full = 2 * np.pi * a; sect = -np.pi / 3 + (2 * np.pi / 3) * a; phys = np.pi * np.sin(np.deg2rad(-60 + 120 * a))
    return {"U": (full, full), "S": (sect, sect), "P": (full, phys)}[kind]                # (psi_t grid, psi_r grid)


def ensemble_sides(kind, Nr, Nt, rho_c=0.7, Kg=32):
    """(R_t,ens, R_r,ens): the ensemble covariance of the grid prior is kron(R_t,ens^T, R_r,ens) [exact: independent uniform grid indices]."""
    pt, pr = angle_grids(kind, Kg)
    return sum(steer_corr(Nt, rho_c, p) for p in pt) / Kg, sum(steer_corr(Nr, rho_c, p) for p in pr) / Kg


def angle_grid_prior(kind, Nr, Nt, rho_c=0.7, Kg=32):
    pt, pr = angle_grids(kind, Kg)
    Rt = [steer_corr(Nt, rho_c, p).T for p in pt]; Rr = [steer_corr(Nr, rho_c, p) for p in pr]
    return GMMPriorB(Nr, Nt, np.array([np.kron(A, B) for A in Rt for B in Rr]))           # component index k = a_t * Kg + a_r
