"""t2_ra_sampler — R-A (Q-27): moments of  pi(h) ∝ p(h) exp(-h^H G h + 2 Re b^H h)  from an ISOTROPIC-noise denoiser only.

Notation (D-01): complex per-entry variances; D(z,nu) = E[h | z = h + e], e ~ CN(0, nu I); score  d/dz^* log p_nu(z) = (D(z,nu) - z) / nu;
2nd-order Tweedie  Cov[h | z] = nu J(z,nu).

[exact] noise splitting.  G = V diag(g) V^H, ups_i = (V^H b)_i / g_i  ("LS observation" of zeta_i = (V^H h)_i with noise variance 1/g_i).
  For nu <= 1/g_max write the observation noise as  w = e + w',  e ~ CN(0, nu I),  Cov[w'_i] = r_i = 1/g_i - nu >= 0,  z = h + e.  Then h -> z -> y is Markov and
      pi(h) = ∫ pi'(z) p(h | z, nu) dz,    pi'(z) ∝ p_nu(z) * prod_i CN(ups_i; zeta^z_i, r_i)          (r_i = 0: zeta^z_i = ups_i clamped; g_i = 0: no factor)
      E[h|y] = E_{pi'}[ D(z,nu) ],   Cov[h|y] = E_{pi'}[ nu J(z,nu) ] + Cov_{pi'}[ D(z,nu) ],   P(k|y) = E_{pi'}[ w_k(z,nu) ]   (Rao-Blackwell).
  The score of pi' needs the isotropic score only. With nu_L = 1/g_max:  G = g I  ->  z = ups deterministic  ->  R-A == D-13 + D-14 one-shot (lossless case).
[heuristic bridge, exact final target] coarse levels nu_l > 1/g_i use a VIRTUAL noisier observation ups_i + xi_i^(l), xi^(l) ~ CN(0, nu_l - 1/g_i) (forward-noised
  path of the clamped coordinate, per chain), i.e. replacement-type conditioning in the eigenbasis of G; predictor = VE ancestral step with the prior score,
  corrector = per-coordinate preconditioned unadjusted Langevin on the exact level-l conditional. Only the LAST level has to be right.
Prior art: SVD-decoupled annealed Langevin with annealing noise taken from the measurement noise = SNIPS (arXiv:2105.14951) [V: abstract]; annealed Langevin
  channel estimation = arXiv:2204.07122 Alg. 1 (point estimate, tuned noise factor beta; not calibrated moments). Ours: stop at nu_L = 1/g_max + Rao-Blackwellised
  Tweedie moments as the EP prior site of the turbo receiver; D-13 + D-14 as the single-point special case."""
import numpy as np
from scipy.special import logsumexp


def _cn(rng, shape):
    return (rng.standard_normal(shape) + 1j * rng.standard_normal(shape)) / np.sqrt(2)


class GMMBatch:
    """Batched (over chains) isotropic-noise denoiser of a t2_route_a.GMMPrior: two GEMMs per call."""

    def __init__(self, prior):
        self.K, self.N = prior.K, prior.N; self.lam = prior.lam; self.logpi = np.log(prior.pi); self.U = prior.U
        self.UH = prior.U.conj().transpose(0, 2, 1).reshape(self.K * self.N, self.N)        # row (k,i) = conj(U_k[:, i])
        self.Uc = prior.U.transpose(1, 0, 2).reshape(self.N, self.K * self.N)               # column (k,j) = U_k[:, j]

    def _post(self, Z, nu):
        Zp = (Z @ self.UH.T).reshape(-1, self.K, self.N)                                    # U_k^H z
        lw = self.logpi - np.sum(np.abs(Zp) ** 2 / (self.lam + nu), 2) - np.sum(np.log(self.lam + nu), 1)
        w = np.exp(lw - logsumexp(lw, 1, keepdims=True)); gain = self.lam / (self.lam + nu)
        return w, gain, Zp

    def denoise(self, Z, nu):
        w, gain, Zp = self._post(Z, nu)
        return ((w[:, :, None] * gain * Zp).reshape(len(Z), -1)) @ self.Uc.T

    def moments(self, Z, nu):
        """w (M,K), D (M,N), Wbar = mean_i nu J(z_i, nu) (N,N)."""
        w, gain, Zp = self._post(Z, nu); M = len(Z)
        mk = np.einsum("kij,mkj->mki", self.U, gain * Zp); D = np.einsum("mk,mki->mi", w, mk)
        Sk = nu * np.einsum("kij,kj,klj->kil", self.U, gain, self.U.conj())
        X = (np.sqrt(w)[:, :, None] * mk).reshape(M * self.K, self.N)
        Wbar = np.einsum("k,kil->il", w.mean(0), Sk) + (X.T @ X.conj() - D.T @ D.conj()) / M
        return w, D, 0.5 * (Wbar + Wbar.conj().T)


def _split(G, b, tol=1e-10):
    g, V = np.linalg.eigh(0.5 * (G + G.conj().T)); g = np.maximum(g, 0.0); obs = g > tol * g.max()
    ups = np.zeros(len(g), complex); ups[obs] = (V.conj().T @ b)[obs] / g[obs]
    return g, V, obs, ups


def ra_sample(denoise, G, b, M, L, K, rng, delta=0.3, nu1=10.0, K_fin=None, cbar=1.0):
    """M chains -> Z (M,N) approximately ~ pi'_{nu_L}, nu_L = 1/g_max.  NFE per chain = (L-1)(K+1) + K_fin.  denoise(Z, nu) -> (M,N)."""
    g, V, obs, ups = _split(G, b); N = len(g); nuL = 1.0 / g.max(); K_fin = 2 * K if K_fin is None else K_fin
    nus = np.geomspace(max(nu1, nuL), nuL, L) if nu1 > nuL and L > 1 else np.array([nuL])
    L = len(nus); ginv = np.where(obs, 1.0 / np.where(obs, g, 1.0), np.inf)
    tau = lambda nu: np.where(obs, np.maximum(nu, ginv), 0.0)                               # virtual observation-noise variance at level nu
    xi = np.zeros((L, M, N), complex)
    for l in range(L - 2, -1, -1):                                                          # forward-noised observation path, built from the last level upwards
        xi[l] = xi[l + 1] + np.sqrt(np.maximum(tau(nus[l]) - tau(nus[l + 1]), 0.0)) * _cn(rng, (M, N))
    nfe = 0

    def sets(nu):
        cl = obs & (g * nu >= 1.0 - 1e-9); r = np.where(obs & ~cl, ginv - nu, np.inf)       # clamped / weak (r finite) / null (r = inf)
        return cl, r

    cl, r = sets(nus[0])
    Zt = np.sqrt(np.minimum(r, cbar + nus[0])) * _cn(rng, (M, N)) + np.where(np.isfinite(r), ups, 0.0)
    Zt[:, cl] = ups[cl] + xi[0][:, cl]
    for l in range(L):
        nu = nus[l]; cl, r = sets(nu); free = ~cl
        eps = np.where(free, delta / (1.0 / nu + 1.0 / r), 0.0)                             # per-coordinate preconditioned step (r = inf -> delta nu)
        for _ in range(K_fin if l == L - 1 else K):
            if not free.any(): break
            Z = Zt @ V.T; S = ((denoise(Z, nu) - Z) / nu) @ V.conj(); nfe += 1              # prior score in eigen-coordinates
            grad = S - np.where(np.isfinite(r), (Zt - ups) / r, 0.0)
            Zt = Zt + eps * grad + np.sqrt(2 * eps) * _cn(rng, (M, N))
            Zt[:, cl] = ups[cl] + xi[l][:, cl]
        if l < L - 1:                                                                       # predictor: VE ancestral step nu_l -> nu_{l+1} (prior score), then re-clamp
            nn = nus[l + 1]
            if free.any():
                Z = Zt @ V.T; S = ((denoise(Z, nu) - Z) / nu) @ V.conj(); nfe += 1
                Zt = np.where(free, Zt + (nu - nn) * S + np.sqrt(nn * (nu - nn) / nu) * _cn(rng, (M, N)), Zt)
            Zt[:, cl] = ups[cl] + xi[l + 1][:, cl]                                          # coordinates that turn weak at l+1 start from ups (xi = 0 there)
    return Zt @ V.T, nuL, nfe


def gmm_exact_zsample(prior, G, b, M, rng):
    """GMM only: EXACT draws z ~ pi'_{nu_L} (reference 'perfect sampler'); also returns the mixture weights w'_k (must equal the exact P(k|y))."""
    g, V, obs, ups = _split(G, b); N = len(g); nuL = 1.0 / g.max()
    cl = obs & (g * nuL >= 1.0 - 1e-9); f = ~cl; wk = obs & f
    rho = np.zeros(N); rho[wk] = 1.0 / (1.0 / g[wk] - nuL); rho = rho[f]                   # likelihood precision on the free coordinates (0 on null ones)
    lw = np.empty(prior.K); means = []; chols = []
    for k, C in enumerate(prior.covs):
        A = V.conj().T @ (C + nuL * np.eye(N)) @ V; Acc = A[np.ix_(cl, cl)]; uc = ups[cl]
        lw[k] = np.log(prior.pi[k]) - np.linalg.slogdet(Acc)[1] - np.real(np.vdot(uc, np.linalg.solve(Acc, uc)))
        if f.any():
            Afc = A[np.ix_(f, cl)]; mu = Afc @ np.linalg.solve(Acc, uc); Af = A[np.ix_(f, f)] - Afc @ np.linalg.solve(Acc, Afc.conj().T)
            Af = 0.5 * (Af + Af.conj().T); Afi = np.linalg.inv(Af); P = Afi + np.diag(rho); Sig = np.linalg.inv(P); Sig = 0.5 * (Sig + Sig.conj().T)
            if wk.any():                                                                    # evidence of the weak coordinates: CN(ups_w; mu_w, [Af]_ww + diag r_w)
                iw = wk[f]; Cw = Af[np.ix_(iw, iw)] + np.diag(1.0 / rho[iw]); dw = ups[f][iw] - mu[iw]
                lw[k] += -np.linalg.slogdet(Cw)[1] - np.real(np.vdot(dw, np.linalg.solve(Cw, dw)))
            means.append(Sig @ (Afi @ mu + rho * ups[f])); chols.append(np.linalg.cholesky(Sig))
    w = np.exp(lw - logsumexp(lw)); Zt = np.tile(ups * cl, (M, 1)).astype(complex)
    if f.any():
        ks = rng.choice(prior.K, size=M, p=w); E = _cn(rng, (M, int(f.sum())))
        Zt[:, f] = np.array([means[k] + chols[k] @ e for k, e in zip(ks, E)])
    return Zt @ V.T, nuL, w


def rb_moments(gmmb, Z, nu, jac="all"):
    """Rao-Blackwellised posterior moments from chain states Z ~ pi'_nu.  jac='all': Wbar = mean_i nu J_i;  'one': nu J of chain 0 only (one Jacobian = D-14 cost)."""
    w, D, Wbar = gmmb.moments(Z, nu); M = len(Z); m = D.mean(0)
    if jac == "one":
        Wbar = gmmb.moments(Z[:1], nu)[2]
    Dc = D - m; B = (Dc.T @ Dc.conj()) / max(M - 1, 1)
    return m, 0.5 * ((Wbar + B) + (Wbar + B).conj().T), w.mean(0)


def site_from_moments(m, Cov, G, b, lam_min=1e-6):
    """EP prior site  Lambda = Cov^-1 - G,  eta = Cov^-1 m - b  (same convention as GMMPrior.ep_site); returns (Lambda, eta, clipped?)."""
    Ci = np.linalg.inv(Cov); Lam = Ci - G; Lam = 0.5 * (Lam + Lam.conj().T); ev, U = np.linalg.eigh(Lam); clipped = bool(ev.min() < lam_min)
    if clipped:
        Lam = (U * np.maximum(ev, lam_min)) @ U.conj().T
    return Lam, Ci @ m - b, clipped


# ============================================================================= R-A v2 (exp_0924): fresh-noise posterior diffusion + exact handover
# exp_0923 verdict: the v1 bridge (replacement-type clamping to a forward-noised observation path) is biased and converges slowly in (L, K).
# v2 bridge [approx; exact for a Gaussian prior at any step size]: z^l = h + n_l, n_l ~ CN(0, nu_l I) FRESH noise, y independent of n_l given h. Ancestral step
#     z^{l+1} | z^l, y  ~  CN( a z^l + (1-a) m_+ ,  nu_{l+1} (1-a) I + (1-a)^2 S_+ ),   a = nu_{l+1}/nu_l,   (m_+, S_+) ~= moments of p(h | z^l, y)
#   'X'  exact mixture p(h | z^l, y) (GMM only; isolates the discretisation error)
#   'J'  p(h | z^l) ~= CN(D, nu J) (2nd-order Tweedie) times the exact Gaussian likelihood:  S_+ = (I + Sig G)^-1 Sig,  m_+ = (I + Sig G)^-1 (D + Sig b),  Sig = nu J
#        = the D-14 operation at every step; same approximation family as moment-matching posterior sampling (arXiv:2405.13712 Sec. 4.2 [V: excerpt])
#   'S'  Sig = nu c_J I,  c_J = cbar / (cbar + nu)  (no Jacobian; exact for an isotropic Gaussian prior of variance cbar)
# Handover [exact for clamped / null coordinates]: at nu_L = 1/g_max the null-space coordinates of the fresh-noise sample have exactly the pi'_{nu_L} marginal
#   (e_u is not part of the observation noise), clamped coordinates are set to ups; weak coordinates are repaired by K_fin exact-target corrector steps.
def gmm_post_cov(gmmb, Z, nu):
    """per-chain D (M,N) and Cov[h | z_i] = nu J(z_i, nu) (M,N,N)."""
    w, gain, Zp = gmmb._post(Z, nu); mk = np.einsum("kij,mkj->mki", gmmb.U, gain * Zp); D = np.einsum("mk,mki->mi", w, mk)
    Sk = nu * np.einsum("kij,kj,klj->kil", gmmb.U, gain, gmmb.U.conj())
    Cov = np.einsum("mk,kil->mil", w, Sk) + np.einsum("mk,mki,mkl->mil", w, mk, mk.conj()) - D[:, :, None] * D.conj()[:, None, :]
    return D, 0.5 * (Cov + Cov.conj().transpose(0, 2, 1))


class PostDenoiser:
    """(m_+, S_+)(Z, nu) for the three bridges; G, b fixed per call site. kind in {'X','J','S'}."""

    def __init__(self, kind, prior, gmmb, G, b, cache=None):
        self.kind, self.prior, self.gb, self.G, self.b = kind, prior, gmmb, G, b; self.N = len(b); self.cache = {} if cache is None else cache; self.n_jac = 0

    def __call__(self, Z, nu):
        N = self.N; I = np.eye(N); M = len(Z)
        if self.kind == "X":
            key = ("X", float(nu))
            if key not in self.cache:                                                       # depends on (G, nu) only -> shared by all trials of a cell
                if not hasattr(self.prior, "covinv"): self.prior.covinv = [np.linalg.inv(C) for C in self.prior.covs]
                Sk = np.array([np.linalg.inv(Ci + self.G + I / nu) for Ci in self.prior.covinv])
                ld = np.array([-np.linalg.slogdet(I + C @ (self.G + I / nu))[1] for C in self.prior.covs])
                self.cache[key] = (Sk, ld)
            Sk, ld = self.cache[key]; beta = self.b[None, :] + Z / nu
            mk = np.einsum("kij,mj->mki", Sk, beta); lw = np.log(self.prior.pi) + ld + np.einsum("mj,mkj->mk", beta.conj(), mk).real
            w = np.exp(lw - logsumexp(lw, 1, keepdims=True)); m = np.einsum("mk,mki->mi", w, mk)
            S = np.einsum("mk,kil->mil", w, Sk) + np.einsum("mk,mki,mkl->mil", w, mk, mk.conj()) - m[:, :, None] * m.conj()[:, None, :]
            return m, 0.5 * (S + S.conj().transpose(0, 2, 1))
        if self.kind == "J":
            D, Sig = gmm_post_cov(self.gb, Z, nu); self.n_jac += 1
            A = np.linalg.inv(I[None] + Sig @ self.G[None]); S = A @ Sig
            m = np.einsum("mij,mj->mi", A, D + np.einsum("mij,j->mi", Sig, self.b))
            return m, 0.5 * (S + S.conj().transpose(0, 2, 1))
        D = self.gb.denoise(Z, nu); s = nu * self.prior.cbar / (self.prior.cbar + nu)       # 'S'
        S = np.linalg.inv(I / s + self.G); S = 0.5 * (S + S.conj().T)
        return (D / s + self.b[None, :]) @ S.T, S


def _corrector(denoise, Zt, V, ups, nu, cl, r, K, delta, rng):
    """K per-coordinate preconditioned ULA steps on the exact level-nu noise-split target (clamped coordinates held at their current values)."""
    free = ~cl; eps = np.where(free, delta / (1.0 / nu + 1.0 / r), 0.0); hold = Zt[:, cl].copy(); M, N = Zt.shape
    for _ in range(K):
        if not free.any(): break
        Z = Zt @ V.T; S = ((denoise(Z, nu) - Z) / nu) @ V.conj()
        Zt = Zt + eps * (S - np.where(np.isfinite(r), (Zt - ups) / r, 0.0)) + np.sqrt(2 * eps) * _cn(rng, (M, N))
        Zt[:, cl] = hold
    return Zt


def ra2_sample(postden, denoise, G, b, M, L, rng, nu1=10.0, K_fin=0, delta=0.3, cbar=1.0):
    """v2: L-level ancestral posterior diffusion nu_1 -> nu_L = 1/g_max with postden(Z, nu) -> (m_+, S_+), exact handover, K_fin corrector steps.
    Returns Z (M,N) ~ pi'_{nu_L} (approx), nu_L, number of denoiser calls per chain."""
    g, V, obs, ups = _split(G, b); N = len(g); nuL = 1.0 / g.max(); I = np.eye(N)
    nus = np.geomspace(max(nu1, 2 * nuL), nuL, max(L, 2)); nfe = 0
    S0 = np.linalg.inv(I / cbar + G); S0 = 0.5 * (S0 + S0.conj().T); m0 = S0 @ b                                   # start: ensemble-covariance Gaussian posterior, noised to nu_1
    Z = m0[None, :] + _cn(rng, (M, N)) @ np.linalg.cholesky(S0).T + np.sqrt(nus[0]) * _cn(rng, (M, N))
    for l in range(len(nus) - 1):
        nu, nn = nus[l], nus[l + 1]; a = nn / nu; mp, Sp = postden(Z, nu); nfe += 1
        Cst = nn * (1 - a) * I + (1 - a) ** 2 * Sp                                                                 # (N,N) or (M,N,N)
        Lc = np.linalg.cholesky(Cst); E = _cn(rng, (M, N))
        Z = a * Z + (1 - a) * mp + (np.einsum("mij,mj->mi", Lc, E) if Lc.ndim == 3 else E @ Lc.T)
    cl = obs & (g * nuL >= 1.0 - 1e-9); ginv = np.where(obs, 1.0 / np.where(obs, g, 1.0), np.inf); r = np.where(obs & ~cl, ginv - nuL, np.inf)
    Zt = Z @ V.conj(); Zt[:, cl] = ups[cl]                                                                         # handover to the noise-split target
    if K_fin > 0 and (~cl).any():
        Zt = _corrector(denoise, Zt, V, ups, nuL, cl, r, K_fin, delta, rng); nfe += K_fin
    return Zt @ V.T, nuL, nfe


def corrector_from(denoise, Z, G, b, K, rng, delta=0.3):
    """diagnostic: K exact-target corrector steps at nu_L starting from given states Z (e.g. perfect-sampler draws)."""
    g, V, obs, ups = _split(G, b); nuL = 1.0 / g.max(); cl = obs & (g * nuL >= 1.0 - 1e-9)
    ginv = np.where(obs, 1.0 / np.where(obs, g, 1.0), np.inf); r = np.where(obs & ~cl, ginv - nuL, np.inf)
    return _corrector(denoise, Z @ V.conj(), V, ups, nuL, cl, r, K, delta, rng) @ V.T
