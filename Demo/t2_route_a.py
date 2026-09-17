"""
t2_route_a.py — Route (a) v0: EP/VAMP-type 3-module annealed turbo receiver (numpy reference, exp_0918).

Model (D-01): Y = H X + W, H in C^{Nr x Nt}, X = [X_p X_d] in C^{Nt x T}, W ~ CN(0, sigma2 I) per complex entry.
Channel prior (exp_0918, no learning): vec(H) ~ CN(0, C), C = kron(R_t^T, R_r), exponential correlation rho
  -> Module H has a closed-form denoiser  h_post = C (C + nu I)^{-1} q  and exact Onsager  alpha^H = tr(C (C+nu I)^{-1})/N  (D-09).

All channel-side algebra is on h = vec(H) (column-major, h[i + Nr*j] = H[i,j]) with explicit N x N matrices, N = Nr*Nt <= 32.
Likelihood site of column n after soft-symbol linearization (form 'A' = marginalization / LMMSE, cf. BiG-AMP (R11)):
  y_n ~ CN(H r_n, d_n^{-1} I),  d_n = 1/(sigma2 + sum_j tau_jn E|h_ij|^2)
  precision  A_n = d_n kron(conj(r_n) r_n^T, I_Nr),   linear term  b_n = d_n kron(conj(r_n), y_n)  (= vec(d_n y_n r_n^H))
Form 'B' (route_a_design_v0 hybrid / T1-EM style) adds  d_n kron(diag(tau_n), I_Nr)  to A_n  — ablation only (D-10).

Modules (route_a_design_v0 §3):
  L_H : G = sum_n A_n, b = sum_n b_n ; extrinsic to H:  C_q = (G + I/nu_max)^{-1}, Q = C_q b, nu_q = tr(C_q)/N   [guard G-1]
  H   : Gaussian closed form + exact trace Onsager, extrinsic (2)-(3) of SC-VAMP
  L_X : LOO cavity P^{\n} = P - A_n (T1 §3.2, exact), EP-LMMSE with R_n = sigma2 I + sum_{jj'} M_jj' Sigma^{[j,j']}
        (M = r r^H + diag(tau)), extrinsic (24)-(25)
  D   : BPSK bit-level BCJR (Lemma 1 / Cor. 1.1, L_c = 4/tau on Re r) or symbol-level BCJR (Lemma 2, QPSK/16-QAM);
        Onsager alpha^D = mean(v/tau^L) (or per-symbol, Q-04'), extrinsic (2)-(3)
Reference receivers: mode='colored' (Gaussian prior folded exactly into L_H; Q-07 upper reference),
  'pilot_only' (pilot LMMSE with the true colored prior, then L_X<->D turbo with fixed channel belief), 'genie' (known H).
"""
import numpy as np
from scipy.special import logsumexp
from t2_trellis import make_trellis, encode, SymbolTrellis, soft_symbols


# ----------------------------------------------------------------------------- channel prior (Gaussian, Kronecker)
def exp_corr(n, rho):
    i = np.arange(n)
    return rho ** np.abs(i[:, None] - i[None, :]).astype(float)


def sqrtm_psd(A):
    w, V = np.linalg.eigh(A)
    return (V * np.sqrt(np.maximum(w, 0.0))) @ V.conj().T


class KronGaussianPrior:
    """vec(H) = S z, z ~ CN(0, I), S = kron(R_t^{1/2 T}, R_r^{1/2});  C = S S^H = kron(R_t^T, R_r)."""

    def __init__(self, Nr, Nt, rho):
        self.Nr, self.Nt, self.N = Nr, Nt, Nr * Nt
        self.S = np.kron(sqrtm_psd(exp_corr(Nt, rho)).T, sqrtm_psd(exp_corr(Nr, rho)))
        self.C = self.S @ self.S.conj().T
        self.Cinv = np.linalg.inv(self.C)
        self.cbar = np.trace(self.C).real / self.N
        self.eh2_prior = np.diag(self.C).real.reshape(Nr, Nt, order="F").mean(0)   # E|h_ij|^2 averaged over rows i

    def sample(self, rng):
        z = (rng.standard_normal(self.N) + 1j * rng.standard_normal(self.N)) / np.sqrt(2)
        return (self.S @ z).reshape(self.Nr, self.Nt, order="F")

    def denoise(self, q, nu):
        """Module H (closed form): posterior mean of h given q = h + e, e ~ CN(0, nu I), and exact alpha = tr(dh/dq)/N."""
        Kmat = self.C @ np.linalg.inv(self.C + nu * np.eye(self.N))
        return Kmat @ q, np.trace(Kmat).real / self.N

    def denoise_full(self, q, nu):
        """As denoise(), but returns the full Wirtinger Jacobian J = dh_post/dq (N x N). Second-order Tweedie: Cov[h | q] = nu * J
        (exact for an MMSE denoiser; the channel-side analogue of Lemma 2(c')). alpha = tr(J)/N."""
        Kmat = self.C @ np.linalg.inv(self.C + nu * np.eye(self.N))
        return Kmat @ q, Kmat


class GaussianPrior(KronGaussianPrior):
    """vec(H) ~ CN(0, C) with an arbitrary covariance C (same interface as KronGaussianPrior)."""

    def __init__(self, Nr, Nt, C):
        self.Nr, self.Nt, self.N = Nr, Nt, Nr * Nt
        self.C = 0.5 * (C + C.conj().T); self.S = sqrtm_psd(self.C)
        self.Cinv = np.linalg.inv(self.C)
        self.cbar = np.trace(self.C).real / self.N
        self.eh2_prior = np.diag(self.C).real.reshape(Nr, Nt, order="F").mean(0)


def steer_corr(n, rho, psi):
    """Narrow angular cluster around electrical angle psi: R = D(psi) R_exp(rho) D(psi)^H, D = diag(exp(j psi m))."""
    d = np.exp(1j * psi * np.arange(n))
    return (d[:, None] * exp_corr(n, rho)) * d.conj()[None, :]


class GMMPrior:
    """Gaussian-mixture channel prior  p(h) = sum_k pi_k CN(h; 0, C_k)  (exp_0920: learning-free NON-Gaussian testbed with an exact score).
    Isotropic-noise denoiser, q = h + e, e ~ CN(0, nu I)  (closed form):
        w_k(q) ∝ pi_k CN(q; 0, C_k + nu I),  m_k = K_k q,  K_k = C_k (C_k + nu I)^{-1},  S_k = nu K_k
        E[h|q] = sum_k w_k m_k,   Cov[h|q] = sum_k w_k (S_k + m_k m_k^H) - m m^H,   J = dE[h|q]/dq (Wirtinger) = Cov[h|q] / nu   (2nd-order Tweedie)
    .C / .Cinv / .cbar / .eh2_prior are those of the ENSEMBLE covariance C_hat = sum_k pi_k C_k (what a second-moment method such as D-11 sees)."""

    def __init__(self, Nr, Nt, covs, weights=None):
        self.Nr, self.Nt, self.N = Nr, Nt, Nr * Nt
        self.K = len(covs); self.pi = np.full(self.K, 1.0 / self.K) if weights is None else np.asarray(weights, float)
        self.covs = [0.5 * (C + C.conj().T) for C in covs]
        ev = [np.linalg.eigh(C) for C in self.covs]
        self.lam = np.array([np.maximum(e[0], 0.0) for e in ev]); self.U = np.array([e[1] for e in ev])      # (K,N), (K,N,N)
        self.C = sum(p * C for p, C in zip(self.pi, self.covs)); self.Cinv = np.linalg.inv(self.C)
        self.cbar = np.trace(self.C).real / self.N
        self.eh2_prior = np.diag(self.C).real.reshape(Nr, Nt, order="F").mean(0)
        self.last_k = None

    def sample(self, rng):
        k = int(rng.choice(self.K, p=self.pi)); self.last_k = k
        z = (rng.standard_normal(self.N) + 1j * rng.standard_normal(self.N)) / np.sqrt(2)
        return ((self.U[k] * np.sqrt(self.lam[k])) @ z).reshape(self.Nr, self.Nt, order="F")

    def _post(self, q, nu):
        z = np.einsum("kji,j->ki", self.U.conj(), q)                                   # U_k^H q
        lw = np.log(self.pi) - np.sum(np.abs(z) ** 2 / (self.lam + nu), 1) - np.sum(np.log(self.lam + nu), 1)
        w = np.exp(lw - logsumexp(lw))
        g = self.lam / (self.lam + nu)                                                 # (K,N) per-component Wiener gains
        mk = np.einsum("kij,kj->ki", self.U, g * z)                                    # (K,N) component means K_k q
        return w, g, mk

    def denoise(self, q, nu):
        w, g, mk = self._post(q, nu); m = w @ mk
        tr_cov = np.sum(w * (nu * g.sum(1) + np.sum(np.abs(mk) ** 2, 1))) - np.sum(np.abs(m) ** 2)
        return m, float(tr_cov / (self.N * nu))

    def denoise_full(self, q, nu):
        w, g, mk = self._post(q, nu); m = w @ mk
        Sk = nu * np.einsum("kij,kj,klj->kil", self.U, g, self.U.conj())               # (K,N,N) component posterior covariances
        Cov = np.einsum("k,kil->il", w, Sk) + np.einsum("k,ki,kl->il", w, mk, mk.conj()) - np.outer(m, m.conj())
        return m, Cov / nu

    def ep_site(self, G, b, lam_min=0.0):
        """Exact posterior of h under the mixture prior and the Gaussian likelihood exp(-h^H G h + 2 Re b^H h) (a mixture again), moment-matched
        to a Gaussian (m, Cov), returned as the EP prior site  Lambda = Cov^{-1} - G,  eta = Cov^{-1} m - b  (eigenvalues of Lambda clipped at lam_min).
        Component evidence: log w_k = log pi_k - log det(I + C_k G) + b^H (C_k^{-1} + G)^{-1} b."""
        if not hasattr(self, "covinv"):
            self.covinv = [np.linalg.inv(C) for C in self.covs]
        I = np.eye(self.N); lw = np.empty(self.K); mus = []; Sigs = []
        for k in range(self.K):
            Sig = np.linalg.inv(self.covinv[k] + G); mu = Sig @ b
            lw[k] = np.log(self.pi[k]) - np.linalg.slogdet(I + self.covs[k] @ G)[1] + np.real(np.vdot(b, mu))
            mus.append(mu); Sigs.append(Sig)
        w = np.exp(lw - logsumexp(lw)); mus = np.array(mus); m = w @ mus
        Cov = sum(wk * (Sk + np.outer(mk, mk.conj())) for wk, Sk, mk in zip(w, Sigs, mus)) - np.outer(m, m.conj())
        Cov = 0.5 * (Cov + Cov.conj().T); Ci = np.linalg.inv(Cov)
        Lam = Ci - G; Lam = 0.5 * (Lam + Lam.conj().T); eta = Ci @ m - b
        ev, V = np.linalg.eigh(Lam)
        if ev.min() < lam_min:
            Lam = (V * np.maximum(ev, lam_min)) @ V.conj().T
        return Lam, eta

    def log_pdf_noisy(self, q, nu):
        """log p_nu(q) of the noisy marginal (for finite-difference Tweedie checks)."""
        z = np.einsum("kji,j->ki", self.U.conj(), q)
        return logsumexp(np.log(self.pi) - np.sum(np.abs(z) ** 2 / (self.lam + nu), 1) - np.sum(np.log(np.pi * (self.lam + nu)), 1))


# ----------------------------------------------------------------------------- fast bit-level BCJR (binary feed-forward trellis)
class BitTrellis:
    """Vectorised exact Log-MAP for the rate-1/n_c feed-forward trellis of t2_trellis.make_trellis
    (state = last nu inputs, msb = most recent, so every state has exactly two predecessors sharing the same input)."""

    def __init__(self, gens_oct, nu):
        self.nxt, self.out = make_trellis(gens_oct, nu)
        self.nu, self.nc = nu, self.out.shape[2]
        S = 1 << nu
        s2 = np.arange(S)
        base = 2 * (s2 & (S // 2 - 1))
        self.pS = np.stack([base, base + 1], 1)          # predecessor states of s2
        self.pU = s2 >> (nu - 1)                          # the (common) input on those branches
        assert np.all(self.nxt[self.pS[:, 0], self.pU] == s2) and np.all(self.nxt[self.pS[:, 1], self.pU] == s2)
        self.xs = 1 - 2 * self.out                        # (S,2,nc) coded symbols in {+1,-1}
        self.m0 = [self.out[:, :, i] == 0 for i in range(self.nc)]

    def bcjr(self, Lch, K):
        """Lch: (K+nu, nc) coded-bit channel LLRs (L = log P(c=0)/P(c=1)). Exact log-sum-exp.
        Returns coded-bit APP LLRs (K+nu, nc) and info-bit APP LLRs (K,)."""
        S = 1 << self.nu
        Ksec = Lch.shape[0]
        gamma = 0.5 * np.einsum("sui,ki->ksu", self.xs, Lch)
        gamma[K:, :, 1] = -np.inf                                                     # forced zero tail
        alpha = np.full((Ksec + 1, S), -np.inf); alpha[0, 0] = 0.0
        with np.errstate(invalid="ignore"):
            for k in range(Ksec):
                cand = alpha[k][:, None] + gamma[k]
                alpha[k + 1] = np.logaddexp(cand[self.pS[:, 0], self.pU], cand[self.pS[:, 1], self.pU])
            beta = np.full((Ksec + 1, S), -np.inf); beta[Ksec, 0] = 0.0
            for k in range(Ksec - 1, -1, -1):
                g = gamma[k]
                beta[k] = np.logaddexp(g[:, 0] + beta[k + 1][self.nxt[:, 0]], g[:, 1] + beta[k + 1][self.nxt[:, 1]])
        Lapp = np.zeros((Ksec, self.nc)); Lu = np.zeros(K)
        for k in range(Ksec):
            bp = alpha[k][:, None] + gamma[k] + beta[k + 1][self.nxt]
            for i in range(self.nc):
                Lapp[k, i] = logsumexp(np.where(self.m0[i], bp, -np.inf)) - logsumexp(np.where(self.m0[i], -np.inf, bp))
            if k < K:
                Lu[k] = logsumexp(bp[:, 0]) - logsumexp(bp[:, 1])
        return Lapp, Lu


# ----------------------------------------------------------------------------- code wrappers (Module D)
class BPSKCode:
    """Terminated convolutional code + BPSK (real +-1 embedded in C). Ns = number of coded bits = symbols."""

    def __init__(self, gens_oct, nu, Ns):
        self.tr = BitTrellis(gens_oct, nu); self.nu, self.nc = nu, self.tr.nc
        assert Ns % self.nc == 0
        self.K, self.Ns, self.m = Ns // self.nc - nu, Ns, 1

    def encode(self, u):
        return (1 - 2 * encode(u, self.tr.nxt, self.tr.out, self.nu)).astype(complex)

    def decode(self, r, tau, ext=False):
        """r, tau: (Ns,) complex pseudo-observations and per-symbol variances. Returns (x_bar, v, Lu). Exact (Lemma 1, Cor. 1.1).
        ext=True additionally returns the moments of the exact extrinsic pmf (L_ext = L_app - L_ch): (r_ext, tau_ext)."""
        Lch = (4.0 * r.real / tau).reshape(-1, self.nc)                                 # L_c = 4/tau on Re{r}
        Lapp, Lu = self.tr.bcjr(Lch, self.K)
        xbar = np.tanh(Lapp / 2).reshape(-1)
        if not ext:
            return xbar.astype(complex), 1.0 - xbar ** 2, Lu                            # v = E|x - xbar|^2 (x real)
        xe = np.tanh((Lapp - Lch) / 2).reshape(-1)
        return xbar.astype(complex), 1.0 - xbar ** 2, Lu, xe.astype(complex), 1.0 - xe ** 2


class QAMCode:
    """Terminated convolutional code + 2^m-QAM on consecutive m coded bits (Lemma 2, symbol-level super-section trellis)."""

    def __init__(self, gens_oct, nu, m, Ns):
        self.st = SymbolTrellis(gens_oct, nu, m)
        self.K = Ns * self.st.q - nu
        assert self.st.n_symbols(self.K) == Ns
        self.Ns, self.m = Ns, m

    def encode(self, u):
        return self.st.encode_symbols(u)[1]

    def decode(self, r, tau, ext=False):
        if not ext:
            P, Lu = self.st.bcjr(r, tau, self.K, return_info=True)
            xbar, v = soft_symbols(P, self.st.CONST)
            return xbar, v, Lu.reshape(-1)
        P, Lu, Pe = self.st.bcjr(r, tau, self.K, return_info=True, return_ext=True)
        xbar, v = soft_symbols(P, self.st.CONST); xe, ve = soft_symbols(Pe, self.st.CONST)
        return xbar, v, Lu.reshape(-1), xe, np.maximum(ve, 0.0)


# ----------------------------------------------------------------------------- receiver
def dft_pilots(Nt, Tp):
    F = np.exp(-2j * np.pi * np.outer(np.arange(Nt), np.arange(Nt)) / Nt)             # unit-modulus columns, E_s = 1
    return F[:, :Tp]


class RouteA:
    def __init__(self, Nr, Nt, T, Tp, sigma2, prior, code, mode="scalar", lh_form="A", alphaD="mean",
                 feedback="extrinsic", loo=True, beta=1.0, eps=1e-6, nu_max=1e4, p_min=1e-8, init_colored=0,
                 scal="site", n_inner=1, nu_sw=None, hsite="scalar", lam_min=0.0, dec_ext="moment", tauD_min=1e-8, exact_prior=False, Xp=None, beta_fb=None):
        assert mode in ("scalar", "colored", "pilot_only", "genie") and lh_form in ("A", "B") and scal in ("site", "belief")
        assert hsite in ("scalar", "matrix")
        self.Nr, self.Nt, self.T, self.Tp, self.Td = Nr, Nt, T, Tp, T - Tp
        self.N, self.sigma2, self.prior, self.code = Nr * Nt, sigma2, prior, code
        assert code.Ns == Nt * self.Td
        self.mode, self.lh_form, self.alphaD, self.feedback, self.loo = mode, lh_form, alphaD, feedback, loo
        self.beta, self.eps, self.nu_max, self.p_min = beta, eps, nu_max, p_min
        self.init_colored = init_colored                                             # scalar mode: first k iterations use the exact colored prior (exp_0918b F1 test)
        # exp_0919: how the L_H -> H message is made isotropic (scalar mode only).
        #   'site'   (v0): exact matrix extrinsic C_q = G^{-1} (guard G-1), then nu_q = tr(C_q)/N  [scalarise the SITE]
        #   'belief' : EP projection of the L_H belief N(h_L, Sigma_L), Sigma_L = (I/nuE + G)^{-1}, onto isotropic Gaussians
        #              (eta = tr(Sigma_L)/N), then the scalar extrinsic of SC-VAMP (2)-(3) with alpha_L = eta/nuE  [scalarise the BELIEF;
        #              this is the LMMSE stage of VAMP]. n_inner > 1 repeats L_H <-> H before going to L_X (inner VAMP iterations).
        self.scal, self.n_inner = scal, n_inner
        # exp_0919: form of the H -> L_H/L_X site. 'scalar' (v0): SC-VAMP (2)-(3) with alpha^H = tr(J)/N  -> CN(hE, nuE I).
        #   'matrix': full-covariance EP site from the full denoiser Jacobian J (same 2N JVPs as the exact trace of D-09):
        #             Sigma_H = nu_q J,  Lambda_E = Sigma_H^{-1} - I/nu_q,  eta_E = Sigma_H^{-1} h_H - q/nu_q  (eigenvalues of Lambda_E clipped at lam_min).
        #             Gaussian prior: Lambda_E = C^{-1}, eta_E = 0 for ANY (q, nu_q)  ->  identical to mode 'colored' (unit test T6).
        self.hsite, self.lam_min = hsite, lam_min
        # exp_0919b (Q-04): Module D extrinsic. 'moment' = project-then-divide (EP / SC-VAMP (2)-(3): Gaussian division of the projected posterior);
        #   'pmf' = divide-then-project (classical turbo): exact extrinsic symbol pmf P(x_n | r_{\n}) from the BCJR, then its mean/variance
        #   (per-symbol tau^D in [0, E_s]; no alpha^D, no clip).
        assert dec_ext in ("moment", "pmf")
        self.dec_ext, self.tauD_min = dec_ext, tauD_min
        # exp_0920: modes 'colored' / 'pilot_only' use the Gaussian CN(0, prior.C) (for a mixture prior: the ENSEMBLE covariance) unless
        # exact_prior=True and the prior offers ep_site(G, b): then the prior site is the exact-tilted-moment EP site under the anisotropic cavity.
        self.exact_prior = exact_prior and hasattr(prior, "ep_site")
        self.nu_sw = nu_sw                                                           # Q-19 threshold rule: colored iteration while site-form nu_q > nu_sw
        # exp_0921: Xp = pilot override (Nt x Tp; default DFT columns). beta_fb = damping of the a-posteriori soft symbols (xbar, v) fed to L_H
        #   when feedback='posterior' (None = undamped = session-3 behaviour; D-12's beta only acts on the extrinsic pair (rD, tauD)).
        self.Xp = dft_pilots(Nt, Tp) if Xp is None else np.asarray(Xp, complex)
        assert self.Xp.shape == (Nt, Tp)
        self.beta_fb = beta_fb
        self.I_N, self.I_Nr = np.eye(self.N), np.eye(Nr)

    # --- transmitter
    def transmit(self, u, perm, H, rng):
        x = self.code.encode(u)
        grid = np.empty(self.Nt * self.Td, complex); grid[perm] = x                   # symbol interleaver
        Xd = grid.reshape(self.Td, self.Nt).T                                          # Xd[j, n] = grid[n*Nt + j]
        X = np.hstack([self.Xp, Xd])
        W = np.sqrt(self.sigma2 / 2) * (rng.standard_normal((self.Nr, self.T)) + 1j * rng.standard_normal((self.Nr, self.T)))
        return X, H @ X + W

    # --- L_H likelihood sites (vec form)
    def _sites(self, Y, Xbar, Tau, eh2):
        d = 1.0 / (self.sigma2 + Tau.T @ eh2)                                          # (T,)
        A = np.empty((self.T, self.N, self.N), complex); B = np.empty((self.T, self.N), complex)
        for n in range(self.T):
            x = Xbar[:, n]
            An = np.kron(np.outer(x.conj(), x), self.I_Nr)
            if self.lh_form == "B":
                An = An + np.kron(np.diag(Tau[:, n]), self.I_Nr)
            A[n] = d[n] * An
            B[n] = d[n] * np.kron(x.conj(), Y[:, n])
        return d, A, B

    # --- full-covariance H -> L site from the denoiser Jacobian (exp_0919)
    def _matrix_site(self, q, nu_q, G):
        hH, J = self.prior.denoise_full(q, nu_q)
        SigH = nu_q * J; SigH = 0.5 * (SigH + SigH.conj().T)
        SigHinv = np.linalg.inv(SigH)
        Lam = SigHinv - self.I_N / nu_q; Lam = 0.5 * (Lam + Lam.conj().T)
        w, V = np.linalg.eigh(Lam)
        if w.min() < self.lam_min:                                                     # non-log-concave priors only; no-op for a Gaussian prior
            Lam = (V * np.maximum(w, self.lam_min)) @ V.conj().T
        eta = SigHinv @ hH - q / nu_q
        return Lam + G, eta

    # --- one full run
    def run(self, Y, H, u, perm, n_iter):
        Nr, Nt, Tp, Td, N = self.Nr, self.Nt, self.Tp, self.Td, self.N
        h_true = H.reshape(-1, order="F"); h_norm2 = np.sum(np.abs(h_true) ** 2)
        rD = np.zeros((Nt, Td), complex); tauD = np.ones((Nt, Td))                    # non-informative decoder site
        xbar_grid, v_grid = rD.copy(), tauD.copy()
        hE = np.zeros(N, complex); nuE = self.prior.cbar                               # = Module H at nu_q -> inf
        eh2 = self.prior.eh2_prior.copy()
        log = {k: [] for k in ("nmse", "tauL_mean", "tauL_gmean", "nu_q", "alphaH", "nuE", "hE_norm",
                               "alphaD", "ber", "blk_err", "tauL_clip_frac", "alphaD_clip")}
        P = Sigma = hpost = None; site_vec = np.zeros(N, complex); A = B = None; b = np.zeros(N, complex)
        if self.mode == "pilot_only":                                                  # fixed channel belief from pilots + true prior
            Xbar = np.hstack([self.Xp, np.zeros((Nt, Td))]); Tau = np.hstack([np.zeros((Nt, Tp)), np.ones((Nt, Td))])
            d, A, B = self._sites(Y, Xbar, Tau, eh2)
            G = A[:Tp].sum(0); b = B[:Tp].sum(0)
            if self.exact_prior:
                Lam, eta = self.prior.ep_site(G, b, self.lam_min); P = Lam + G; Sigma = np.linalg.inv(P); hpost = Sigma @ (eta + b)
            else:
                P = self.prior.Cinv + G; Sigma = np.linalg.inv(P); hpost = Sigma @ b
        for t in range(n_iter):
            # ---------------- L_H + H (channel side)
            if self.mode in ("scalar", "colored"):
                Xd_soft, Td_soft = (rD, tauD) if self.feedback == "extrinsic" else (xbar_grid, v_grid)
                Xbar = np.hstack([self.Xp, Xd_soft]); Tau = np.hstack([np.zeros((Nt, Tp)), Td_soft])
                d, A, B = self._sites(Y, Xbar, Tau, eh2)
                G = A.sum(0); b = B.sum(0)
                use_scalar = self.mode == "scalar" and t >= self.init_colored
                if use_scalar and (self.scal == "site" or self.nu_sw is not None):
                    Cq = np.linalg.inv(G + self.I_N / self.nu_max)                     # guard G-1 (singular G early on)
                    q = Cq @ b; nu_q = np.trace(Cq).real / N
                    if self.nu_sw is not None and nu_q > self.nu_sw:                   # Q-19 threshold rule
                        use_scalar = False
                if use_scalar and self.scal == "site":
                    hH, alphaH = self.prior.denoise(q, nu_q)
                    alphaH = float(np.clip(alphaH, self.eps, 1 - self.eps))
                    hE = (hH - alphaH * q) / (1 - alphaH); nuE = alphaH / (1 - alphaH) * nu_q   # SC-VAMP (2)-(3)
                    P = self.I_N / nuE + G; site_vec = hE / nuE
                    if self.hsite == "matrix":
                        P, site_vec = self._matrix_site(q, nu_q, G)
                    log["nu_q"].append(nu_q); log["alphaH"].append(alphaH)
                elif use_scalar:                                                       # scal == 'belief'
                    for _ in range(self.n_inner):
                        SigL = np.linalg.inv(self.I_N / nuE + G); hL = SigL @ (hE / nuE + b)
                        aL = float(np.clip(np.trace(SigL).real / N / nuE, self.eps, 1 - self.eps))
                        nu_q = aL / (1 - aL) * nuE; q = (hL - aL * hE) / (1 - aL)       # SC-VAMP (2)-(3), L_H side
                        hH, alphaH = self.prior.denoise(q, nu_q)
                        alphaH = float(np.clip(alphaH, self.eps, 1 - self.eps))
                        hE = (hH - alphaH * q) / (1 - alphaH); nuE = alphaH / (1 - alphaH) * nu_q   # SC-VAMP (2)-(3), H side
                    P = self.I_N / nuE + G; site_vec = hE / nuE
                    if self.hsite == "matrix":                                         # isotropic site only feeds the denoiser input; L_X sees the matrix site
                        P, site_vec = self._matrix_site(q, nu_q, G)
                    log["nu_q"].append(nu_q); log["alphaH"].append(alphaH)
                else:
                    if self.exact_prior:
                        Lam, site_vec = self.prior.ep_site(G, b, self.lam_min); P = Lam + G
                    else:
                        P = self.prior.Cinv + G; site_vec = np.zeros(N, complex)
                    log["nu_q"].append(np.nan); log["alphaH"].append(np.nan)
                Sigma = np.linalg.inv(P); hpost = Sigma @ (site_vec + b)
                eh2 = (np.abs(hpost) ** 2 + np.diag(Sigma).real).reshape(Nr, Nt, order="F").mean(0)   # for next linearization (I-2)
            else:
                log["nu_q"].append(np.nan); log["alphaH"].append(np.nan)
            log["nuE"].append(nuE); log["hE_norm"].append(float(np.linalg.norm(hE)))
            log["nmse"].append(np.nan if hpost is None else float(np.sum(np.abs(hpost - h_true) ** 2) / h_norm2))
            # ---------------- L_X (symbol side, per data column)
            rL = np.empty((Nt, Td), complex); tauL = np.empty((Nt, Td)); nclip = 0
            for n in range(Td):
                c = Tp + n; y = Y[:, c]; r = rD[:, n]; tau = tauD[:, n]
                if self.mode == "genie":
                    Hc, R = H, self.sigma2 * self.I_Nr
                else:
                    if self.mode in ("scalar", "colored") and self.loo:
                        Sc = np.linalg.inv(P - A[c]); hc = Sc @ (site_vec + b - B[c])     # LOO cavity (T1 §3.2)
                    else:
                        Sc, hc = Sigma, hpost
                    Hc = hc.reshape(Nr, Nt, order="F")
                    M = np.outer(r, r.conj()) + np.diag(tau)                            # E[x x^H] under the symbol belief
                    Sc4 = Sc.reshape(Nt, Nr, Nt, Nr)
                    R = self.sigma2 * self.I_Nr + np.einsum("jk,jikl->il", M, Sc4)
                    R = 0.5 * (R + R.conj().T)
                Tm = np.diag(tau)
                Sy = Hc @ Tm @ Hc.conj().T + R
                Kg = Tm @ Hc.conj().T @ np.linalg.inv(Sy)
                xhat = r + Kg @ (y - Hc @ r)
                sp = np.diag(Tm - Kg @ Hc @ Tm).real                                    # posterior variances
                pL = 1.0 / sp - 1.0 / tau                                               # extrinsic precision (>= 0 for LMMSE)
                nclip += int(np.sum(pL < self.p_min)); pL = np.maximum(pL, self.p_min)
                tauL[:, n] = 1.0 / pL
                rL[:, n] = (xhat / sp - r / tau) / pL
            log["tauL_clip_frac"].append(nclip / (Nt * Td))
            # ---------------- D (decoder, exact)
            r_code = rL.T.reshape(-1)[perm]; tau_code = tauL.T.reshape(-1)[perm]
            if self.dec_ext == "pmf":
                xbar, v, Lu, rD_c, tauD_c = self.code.decode(r_code, tau_code, ext=True)
                tauD_c = np.maximum(tauD_c, self.tauD_min)
                a = np.clip(np.mean(v / tau_code), self.eps, 1 - self.eps); log["alphaD_clip"].append(0.0)   # alpha^D logged only
            else:
                xbar, v, Lu = self.code.decode(r_code, tau_code)
                ratio = v / tau_code
                a = np.mean(ratio) if self.alphaD == "mean" else ratio
                a_cl = np.clip(a, self.eps, 1 - self.eps)
                log["alphaD_clip"].append(float(np.mean(a_cl != a)))
                a = a_cl
                rD_c = (xbar - a * r_code) / (1 - a); tauD_c = a / (1 - a) * tau_code       # SC-VAMP (2)-(3)
            gr = np.empty(Nt * Td, complex); gt = np.empty(Nt * Td); gx = np.empty(Nt * Td, complex); gv = np.empty(Nt * Td)
            gr[perm] = rD_c; gt[perm] = tauD_c; gx[perm] = xbar; gv[perm] = v
            rD_new = gr.reshape(Td, Nt).T; tauD_new = gt.reshape(Td, Nt).T
            rD = self.beta * rD_new + (1 - self.beta) * rD; tauD = self.beta * tauD_new + (1 - self.beta) * tauD
            xb_new = gx.reshape(Td, Nt).T; v_new = gv.reshape(Td, Nt).T
            if self.beta_fb is None: xbar_grid, v_grid = xb_new, v_new
            else: xbar_grid = self.beta_fb * xb_new + (1 - self.beta_fb) * xbar_grid; v_grid = self.beta_fb * v_new + (1 - self.beta_fb) * v_grid
            uhat = (Lu < 0).astype(int)
            log["alphaD"].append(float(np.mean(a)))
            log["tauL_mean"].append(float(np.mean(tau_code))); log["tauL_gmean"].append(float(np.exp(np.mean(np.log(tau_code)))))
            log["ber"].append(float(np.mean(uhat != u))); log["blk_err"].append(int(np.any(uhat != u)))
        return {k: np.array(v) for k, v in log.items()}
