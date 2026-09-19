"""conf/code/scvamp.py -- R4 baseline: 3-module SC-VAMP-type receiver.

*** R4 IS NOT THE ALGORITHM OF arXiv:2604.19061. ***
It is that paper's *interface* adapted to our setting.  The paper has a KNOWN i.i.d. real channel, a
nonlinearity f, an LDPC/BP denoiser and BPSK; we have an UNKNOWN correlated channel, f = id, a
convolutional/BCJR denoiser and QPSK (conf/02_SPEC_baselines.md §2.1, conf/09_PRIOR_ART_NOTE.md §1).
Everything below comes from the equations transcribed into 02_SPEC §2.2; nothing from memory.

What is taken from the paper (02_SPEC §2.2):
  (a) universal extrinsic rule            alpha = v_post/v_in,  r_out = (x_post - alpha r_in)/(1-alpha),
                                          v_out = alpha/(1-alpha) v_in,  alpha clipped to [eps, 1-eps]
  (b) Module A with f = id                returns (y, sigma2) unchanged every iteration -> 3 modules
                                          collapse EXACTLY to 2 (test S1)
  (c) Module C = SISO-LMMSE               Sigma^C = (I/v_x + Hh^H Hh/sigma2)^-1,
                                          alpha^C_x = (1/Nt) sum_n sigma2/(sigma2 + v_x lambda_n)  (test S2)
  (d) Module B = BCJR denoiser            mode 'onsager' (variance-ratio extrinsic) / 'llr' (classical
                                          L_ext = L_app - L_in) -- the paper's "LLR Turbo" ablation switch

What we add because the paper has no channel estimator (02_SPEC §2.3): the MOST CLASSICAL one --
pilot + A-POSTERIORI soft-symbol LMMSE, NO LOO, NO damping, with the same Gaussian sample-covariance
prior and the same pilot matrix as R2-ours-G.  That way R2 -> R4 isolates exactly one thing: whether our
D-15+LOO gain is obtainable from the variance-ratio Onsager interface alone.

[approximation, paper §III-C3]  the variance ratio alpha^B equals the theoretical Onsager correction only
for an EXACT MMSE denoiser; for an approximate decoder it is a surrogate.
"""
import numpy as np

from common import (BETA, EPS_CLIP, N_ITER, VAR_FLOOR, KEYS_LOG, CONST_QPSK, CBITS_QPSK,
                    bit_llrs_from_pmf, code_to_grid, grid_to_code)


# ----------------------------------------------------------------------------- (a) universal extrinsic rule
class Extrinsic:
    """r_out = (x_post - alpha r_in)/(1 - alpha),  v_out = alpha/(1-alpha) v_in,  alpha = v_post/v_in.
    alpha is clipped to [eps, 1-eps] (paper-specified); every clip is counted (test S5)."""

    def __init__(self, eps=EPS_CLIP):
        self.eps = eps
        self.n_call = 0
        self.n_clip = 0

    def __call__(self, r_in, v_in, x_post, v_post):
        a = v_post / max(v_in, VAR_FLOOR)
        ac = float(np.clip(a, self.eps, 1 - self.eps))
        self.n_call += 1
        self.n_clip += int(ac != a)
        return (x_post - ac * r_in) / (1 - ac), ac / (1 - ac) * v_in, ac


# ----------------------------------------------------------------------------- (b) Module A, f = id
def module_A(y, sigma2):
    """[paper-explicit] with f = id Module A is the identity: it returns the observation and its noise
    variance unchanged at every iteration.  Kept as a function so test S1 can assert the constancy."""
    return y, sigma2


# ----------------------------------------------------------------------------- (c) Module C = SISO-LMMSE
def module_C(Hh, Yd, r_x, v_x, sigma2):
    """Sigma^C = (I/v_x + Hh^H Hh/sigma2)^-1 ;  x_post_l = Sigma^C (r_x_l/v_x + Hh^H y_l/sigma2)
    v_post = tr(Sigma^C)/Nt ;  alpha^C_x = v_post/v_x = (1/Nt) sum_n sigma2/(sigma2 + v_x lambda_n).
    The eigendecomposition of Hh^H Hh is computed once per iteration and reused for both forms."""
    Nt = Hh.shape[1]
    Gm = Hh.conj().T @ Hh
    lam, V = np.linalg.eigh(0.5 * (Gm + Gm.conj().T))
    lam = np.maximum(lam.real, 0.0)
    dinv = 1.0 / (1.0 / max(v_x, VAR_FLOOR) + lam / sigma2)
    Sig = (V * dinv) @ V.conj().T
    Xp = Sig @ (r_x / max(v_x, VAR_FLOOR) + (Hh.conj().T @ Yd) / sigma2)
    v_post = float(np.trace(Sig).real / Nt)
    alpha_cf = float(np.mean(sigma2 / (sigma2 + v_x * lam)))                   # closed form, test S2
    return Xp, v_post, alpha_cf, lam


# ----------------------------------------------------------------------------- QPSK channel bit LLRs (for mode 'llr')
def qpsk_channel_llr(r, v):
    """Exact per-bit channel LLR of an uncoded QPSK symbol observed as r = x + CN(0, v):
    L_0 = 2 sqrt(2) Re(r)/v,  L_1 = 2 sqrt(2) Im(r)/v.  Test S6 checks this against
    t2_trellis.demap_bit_llrs (independent brute-force marginalisation over the constellation)."""
    s = 2.0 * np.sqrt(2.0) / np.maximum(v, VAR_FLOOR)
    return np.stack([s * r.real, s * r.imag], axis=-1)


def soft_qpsk_from_llr(L):
    t = np.tanh(0.5 * L)
    return (t[..., 0] + 1j * t[..., 1]) / np.sqrt(2.0), 0.5 * ((1 - t[..., 0] ** 2) + (1 - t[..., 1] ** 2))


# ----------------------------------------------------------------------------- classical APP-LMMSE channel estimator
def lmmse_channel(Y, Xbar, Tau, Cinv, eh2, sigma2, Nr, Nt):
    """Form-'A' linearised LMMSE for h = vec(H) (column-major), IDENTICAL algebra to t2_route_a.RouteA._sites
    + the 'colored' belief, but with NO leave-one-out cavity and NO damping (that is exactly the point of R4).
      d_n = 1/(sigma2 + sum_j Tau_jn E|h_ij|^2),  A_n = d_n kron(conj(x_n) x_n^T, I),  b_n = d_n kron(conj(x_n), y_n)
      P = C^-1 + sum_n A_n,  h_post = P^-1 sum_n b_n."""
    N = Nr * Nt
    I_Nr = np.eye(Nr)
    d = 1.0 / (sigma2 + Tau.T @ eh2)
    G = np.zeros((N, N), complex)
    b = np.zeros(N, complex)
    for n in range(Y.shape[1]):
        x = Xbar[:, n]
        G += d[n] * np.kron(np.outer(x.conj(), x), I_Nr)
        b += d[n] * np.kron(x.conj(), Y[:, n])
    Sig = np.linalg.inv(Cinv + G)
    hp = Sig @ b
    eh2_new = (np.abs(hp) ** 2 + np.diag(Sig).real).reshape(Nr, Nt, order="F").mean(0)
    return hp.reshape(Nr, Nt, order="F"), Sig, eh2_new


# ----------------------------------------------------------------------------- R4 arm
class R4SCVAMP:
    """3-module SC-VAMP-type receiver.  mode 'onsager' -> R4-scvamp, mode 'llr' -> R4-llr.
    .run(Y, H, u, perm, n_iter) -> the RouteA.run key set (test C1)."""

    def __init__(self, Nr, Nt, T, Tp, sigma2, prior, code, Xp, mode="onsager", eps=EPS_CLIP,
                 gauss_code=False, genie_H=None):
        assert mode in ("onsager", "llr")
        self.Nr, self.Nt, self.T, self.Tp, self.Td = Nr, Nt, T, Tp, T - Tp
        self.sigma2, self.prior, self.code, self.mode = sigma2, prior, code, mode
        self.Xp = np.asarray(Xp, complex)
        assert self.Xp.shape == (Nt, Tp)
        self.eps = eps
        self.gauss_code = gauss_code                 # test S3: replace p_X by CN(0,1)
        self.genie_H = genie_H                       # test S3: skip channel estimation
        self.tag = "R4-scvamp" if mode == "onsager" else "R4-llr"
        self.cfg_dump = dict(arm=self.tag, class_="R4SCVAMP", mode=mode, eps=eps,
                             prior="Gaussian sample covariance of the training set (same as R2-ours-G)",
                             module_A="identity (f = id): returns (y, sigma2) unchanged",
                             module_C="SISO-LMMSE, scalar v_x, eigendecomposition reused",
                             module_B="BCJR; 'onsager' = variance-ratio extrinsic, 'llr' = L_app - L_in",
                             channel_est="classical APP-LMMSE, NO LOO, NO damping (02_SPEC §2.3)",
                             gauss_code=bool(gauss_code), genie_H=(genie_H is not None))

    def transmit(self, u, perm, H, rng):
        x = self.code.encode(u)
        grid = np.empty(self.Nt * self.Td, complex)
        grid[perm] = x
        X = np.hstack([self.Xp, grid.reshape(self.Td, self.Nt).T])
        W = np.sqrt(self.sigma2 / 2) * (rng.standard_normal((self.Nr, self.T)) + 1j * rng.standard_normal((self.Nr, self.T)))
        return X, H @ X + W

    def _decode(self, r_code, tau, r_in_c, v_in, ext_op):
        """Module B.  Returns (x_out_code, v_out, alpha_B, xbar, v_app, uhat)."""
        if self.gauss_code:                                                     # test S3: p_X = CN(0,1)
            xp = r_code / (1.0 + v_in)
            vp = v_in / (1.0 + v_in)
            r_out, v_out, a = ext_op(r_in_c, v_in, xp, vp)
            return r_out, v_out, a, xp, np.full(len(r_code), vp), None
        P, Lu, Pe = self.code.st.bcjr(r_code, np.full(len(r_code), tau), self.code.K,
                                      return_info=True, return_ext=True)
        xbar = P @ CONST_QPSK
        v_app = np.maximum((P @ (np.abs(CONST_QPSK) ** 2)).real - np.abs(xbar) ** 2, 0.0)
        uhat = (Lu.reshape(-1) < 0).astype(int)
        if self.mode == "onsager":
            r_out, v_out, a = ext_op(r_in_c, v_in, xbar, float(np.mean(v_app)))
        else:                                                                   # classical  L_ext = L_app - L_in
            L_app = bit_llrs_from_pmf(P)
            L_in = qpsk_channel_llr(r_code, v_in)
            xe, ve = soft_qpsk_from_llr(L_app - L_in)
            r_out, v_out, a = xe, float(np.mean(ve)), float(np.mean(ve)) / max(v_in, VAR_FLOOR)
        return r_out, v_out, a, xbar, v_app, uhat

    def run(self, Y, H, u, perm, n_iter=N_ITER):
        Nr, Nt, Tp, Td = self.Nr, self.Nt, self.Tp, self.Td
        s2 = self.sigma2
        Yd = Y[:, Tp:]
        h_norm2 = float(np.sum(np.abs(H) ** 2))
        ext_C, ext_B = Extrinsic(self.eps), Extrinsic(self.eps)
        yA, s2A = module_A(Y, s2)                                               # Module A, f = id (constant)

        Cinv = self.prior.Cinv
        eh2 = self.prior.eh2_prior.copy()
        if self.genie_H is not None:
            Hh, Sig = self.genie_H, np.zeros((Nr * Nt, Nr * Nt), complex)
        else:
            Xb0 = np.hstack([self.Xp, np.zeros((Nt, Td))])
            Tau0 = np.hstack([np.zeros((Nt, Tp)), np.ones((Nt, Td))])
            Hh, Sig, eh2 = lmmse_channel(yA, Xb0, Tau0, Cinv, eh2, s2A, Nr, Nt)

        r_x = np.zeros((Nt, Td), complex)
        v_x = 1.0
        log = {k: [] for k in KEYS_LOG}
        alphaCs, alphaBs = [], []

        for t in range(n_iter):
            Xc, v_post, alpha_cf, lam = module_C(Hh, Yd, r_x, v_x, s2A)         # Module C
            r_B, v_B, aC = ext_C(r_x, v_x, Xc, v_post)
            alphaCs.append(aC)
            r_code = grid_to_code(r_B, perm)
            r_in_c = r_code
            x_out, v_x_new, aB, xbar, v_app, uhat = self._decode(r_code, max(v_B, VAR_FLOOR), r_in_c, v_B, ext_B)
            alphaBs.append(aB)
            r_x = code_to_grid(x_out, perm, Nt, Td)
            v_x = max(float(v_x_new), VAR_FLOOR)

            xg = code_to_grid(xbar, perm, Nt, Td)
            vg = code_to_grid(v_app, perm, Nt, Td)
            if self.genie_H is None:                                            # classical APP-LMMSE, no LOO, no damping
                Xb = np.hstack([self.Xp, xg])
                Tau = np.hstack([np.zeros((Nt, Tp)), vg])
                Hh, Sig, eh2 = lmmse_channel(yA, Xb, Tau, Cinv, eh2, s2A, Nr, Nt)

            log["nmse"].append(float(np.sum(np.abs(Hh - H) ** 2) / h_norm2))
            log["ber"].append(np.nan if uhat is None else float(np.mean(uhat != u)))
            log["blk_err"].append(0 if uhat is None else int(np.any(uhat != u)))
            log["tauL_mean"].append(float(v_B))
            log["tauL_gmean"].append(float(v_B))
            log["alphaD"].append(float(aB))
            log["nu_q"].append(np.nan)
            log["alphaH"].append(np.nan)
            log["nuE"].append(float(v_x))
            log["hE_norm"].append(float(np.linalg.norm(Hh)))
            log["tauL_clip_frac"].append(ext_C.n_clip / max(ext_C.n_call, 1))
            log["alphaD_clip"].append(ext_B.n_clip / max(ext_B.n_call, 1))

        out = {k: np.array(v) for k, v in log.items()}
        out["alphaC"] = np.array(alphaCs)
        out["diverged"] = np.full(n_iter, float(not np.all(np.isfinite(out["nmse"]))))
        out["stop_hits"] = np.zeros(n_iter)
        self.clip_calls = (ext_C.n_call, ext_C.n_clip, ext_B.n_call, ext_B.n_clip)
        return out
