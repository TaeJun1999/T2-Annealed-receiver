"""conf/code/bigamp.py -- R3 baseline: BiG-AMP (Parker-Schniter-Cevher, arXiv:1310.2632v3, Table III) + BCJR turbo.

ONLY the equations transcribed into conf/02_SPEC_baselines.md §1.2 are implemented here; nothing is
reconstructed from memory (conf/01_RULES.md §2).  Mapping of the paper's notation onto ours:
    Z = A X   ->   P = H X,     A -> H,  M -> Nr,  N -> Nt,  L -> T,  nu^w -> sigma2.

                        *** ERRATUM IN THE SOURCE -- do not "fix" this back ***
The paper's damping equation (95) prints   nu^s <- beta ((nu^z/nu^p - 1)/nu^p) + ...   which has the
OPPOSITE SIGN of Table III (R7).  (R7) is the correct one: in AWGN
    nu^z = nu^p sigma2/(nu^p + sigma2) < nu^p   =>   (1 - nu^z/nu^p)/nu^p = 1/(nu^p + sigma2) > 0,
which is exactly the paper's own closed form (72).  Following (95) gives nu^s < 0 and diverges.
=> we use the sign of (R7).  Test B6 locks this.  See conf/09_PRIOR_ART_NOTE.md §2.

Structural limitation (02_SPEC §1.3, 09_PRIOR_ART_NOTE §2): Table III admits only an ELEMENT-WISE
SEPARABLE channel prior, so the Kronecker-correlated prior of our testbed cannot be supplied.  R3 runs
with i.i.d. CN(0, 1/Nr).  This is BiG-AMP's limitation, not a handicap we imposed; it is printed in the
result header.

The whole core is written with trailing (Nr, Nt) / (Nt, T) / (Nr, T) axes and plain `@`, so an arbitrary
number of leading batch axes broadcasts (01_RULES §9.2 rank 3).  No GPU port is done on speculation.
"""
import numpy as np

from common import (BETA, EPS_CLIP, N_ITER, T_IN, VAR_FLOOR, KEYS_LOG, bit_llrs_from_pmf,
                    code_to_grid, grid_to_code, qpsk_posterior)

NU_CAP = 1e12                    # variance cap implied by flooring the reciprocals' denominators


def _T(A):
    return np.swapaxes(A, -1, -2)


def _H(A):
    return np.conj(np.swapaxes(A, -1, -2))


# ----------------------------------------------------------------------------- AWGN output channel, eqs (71)-(72)
def awgn_out(y, phat, nu_p, sigma2):
    """(R5)-(R8) specialised to  y = z + CN(0, sigma2)  [exact, paper eqs (71)-(72)].
    Returns (nu_z, zhat, nu_s, shat).  nu_s here carries the sign of (R7), not of the misprinted (95)."""
    d = nu_p + sigma2
    nu_z = nu_p * sigma2 / d
    zhat = (sigma2 * phat + nu_p * y) / d
    nu_s = 1.0 / d                                          # (R7) == eq (72); see the note below
    shat = (y - phat) / d                                   # (R8) == eq (72)
    return nu_z, zhat, nu_s, shat
    # (R7) reads nu^s = (1 - nu^z/nu^p)/nu^p.  That is ALGEBRAICALLY the same as 1/(nu^p + sigma2), but in
    # float64 it cancels: the relative error is ~eps*(1 + sigma2/nu^p), i.e. 1e-9 at sigma2/nu^p = 1e7.
    # 02_SPEC_baselines.md §1.2 instructs to implement (R5)-(R8) "directly with this closed form", so we do.
    # Test B6 verifies the identity (in extended precision) and, above all, the SIGN against the misprinted eq (95).


class BiGAMPState:
    """(H_hat, nu_h, X_hat, nu_x, s_hat) plus the damping memory of (93)-(98)."""

    __slots__ = ("Hh", "nuh", "Xh", "nux", "sh", "nubp", "nup", "nus", "Xbar", "Hbar", "pbar_prev",
                 "t", "diverged", "stop_hits")

    def __init__(self, Hh, nuh, Xh, nux):
        self.Hh, self.nuh, self.Xh, self.nux = Hh, nuh, Xh, nux
        self.sh = np.zeros(( Hh.shape[-2], Xh.shape[-1]), complex)      # s_hat(0) = 0
        self.nubp = self.nup = self.nus = None
        self.Xbar, self.Hbar = Xh.copy(), Hh.copy()
        self.pbar_prev = None
        self.t = 0
        self.diverged = False
        self.stop_hits = 0


def bigamp_iter(st, Y, sigma2, beta, tau_h, x_prior, tol_stop=1e-8):
    """One iteration of Table III (R1)-(R16) with the damping of §IV-A applied to
    (nubar^p, nu^p, nu^s, s_hat, x_hat, h_hat) -- exactly the list of conf/02_SPEC_baselines.md §1.2.
    The damped means x_bar, h_bar feed (R9)-(R12) ONLY; (R1)-(R2) use the undamped x_hat, h_hat.
    beta = 1 reduces to undamped Table III bit-for-bit (test B1).

    x_prior(rhat, nu_r) -> (x_hat_new, nu_x_new) is the separable symbol prior (R13)(R14).
    tau_h is the i.i.d. channel prior variance, (R15)(R16) = Wiener shrinkage.
    """
    Hh, nuh, Xh, nux = st.Hh, st.nuh, st.Xh, st.nux

    ah2 = np.abs(Hh) ** 2
    ax2 = np.abs(Xh) ** 2
    nubp = ah2 @ nux + nuh @ ax2                                               # (R1)
    pbar = Hh @ Xh                                                             # (R2)
    if st.nubp is not None:
        nubp = beta * nubp + (1 - beta) * st.nubp                              # (93)
    nup = nubp + nuh @ nux                                                     # (R3)
    if st.nup is not None:
        nup = beta * nup + (1 - beta) * st.nup
    nup = np.maximum(nup, VAR_FLOOR)
    phat = pbar - st.sh * nubp                                                 # (R4)

    nu_z, zhat, nus, sh = awgn_out(Y, phat, nup, sigma2)                       # (R5)-(R8), AWGN closed form
    if st.nus is not None:
        nus = beta * nus + (1 - beta) * st.nus                                 # (95) with the sign of (R7)
        sh = beta * sh + (1 - beta) * st.sh                                    # (96)

    Xbar = beta * Xh + (1 - beta) * st.Xbar                                    # (97)
    Hbar = beta * Hh + (1 - beta) * st.Hbar                                    # (98)
    abh2 = np.abs(Hbar) ** 2
    abx2 = np.abs(Xbar) ** 2

    nu_r = 1.0 / np.maximum(_T(abh2) @ nus, VAR_FLOOR)                         # (R9)
    rhat = Xbar * (1.0 - nu_r * (_T(nuh) @ nus)) + nu_r * (_H(Hbar) @ sh)      # (R10)
    nu_q = 1.0 / np.maximum(nus @ _T(abx2), VAR_FLOOR)                         # (R11)
    qhat = Hbar * (1.0 - nu_q * (nus @ _T(nux))) + nu_q * (sh @ _H(Xbar))      # (R12)
    nu_r = np.minimum(nu_r, NU_CAP)
    nu_q = np.minimum(nu_q, NU_CAP)

    Xh_new, nux_new = x_prior(rhat, nu_r)                                      # (R13)(R14)
    nuh_new = tau_h * nu_q / (tau_h + nu_q)                                    # (R15)  i.i.d. CN(0, tau_h)
    Hh_new = (tau_h / (tau_h + nu_q)) * qhat                                   # (R16)

    fields = (nubp, nup, nus, sh, Xh_new, nux_new, Hh_new, nuh_new, rhat, nu_r)
    if not all(np.all(np.isfinite(f)) for f in fields):
        st.diverged = True                                                     # 01_RULES §4: classify, never silently zero
        return st, None

    if st.pbar_prev is not None:                                               # (R17), logged only (all arms run N_ITER)
        num = np.sum(np.abs(pbar - st.pbar_prev) ** 2)
        if num <= tol_stop * max(np.sum(np.abs(pbar) ** 2), 1e-300):
            st.stop_hits += 1
    st.pbar_prev = pbar

    st.nubp, st.nup, st.nus, st.sh = nubp, nup, nus, sh
    st.Xbar, st.Hbar = Xbar, Hbar
    st.Xh, st.nux, st.Hh, st.nuh = Xh_new, np.maximum(nux_new, 0.0), Hh_new, np.maximum(nuh_new, VAR_FLOOR)
    st.t += 1
    return st, (rhat, nu_r)


# ----------------------------------------------------------------------------- pilot-based initialisation (I2)
def pilot_lmmse_init(Y, Xp, sigma2, tau_h, Nr, Nt):
    """Row-wise LMMSE from the pilot block under R3's OWN i.i.d. prior CN(0, tau_h)
    (using the correlated prior here would contradict the arm's stated prior).
    y_m = Xp^T h_m + CN(0, sigma2 I),  h_m = H[m,:]^T."""
    Tp = Xp.shape[1]
    Prec = np.eye(Nt) / tau_h + (Xp.conj() @ Xp.T) / sigma2
    Sig = np.linalg.inv(Prec)
    Hh = (Sig @ (Xp.conj() @ Y[:, :Tp].T) / sigma2).T                          # (Nr, Nt)
    nuh = np.broadcast_to(np.maximum(np.diag(Sig).real, VAR_FLOOR), (Nr, Nt)).copy()
    return Hh, nuh


# ----------------------------------------------------------------------------- R3 arm
class R3BiGAMP:
    """BiG-AMP + BCJR turbo receiver.  Interface identical to t2_route_a.RouteA (test C1):
    .run(Y, H, u, perm, n_iter) -> dict of per-iteration arrays with the keys of RouteA.run."""

    tag = "R3-bigamp"

    def __init__(self, Nr, Nt, T, Tp, sigma2, code, Xp, beta=BETA, t_in=T_IN, tau_h=None):
        self.Nr, self.Nt, self.T, self.Tp, self.Td = Nr, Nt, T, Tp, T - Tp
        self.sigma2, self.code, self.beta, self.t_in = sigma2, code, beta, t_in
        self.tau_h = (1.0 / Nr) if tau_h is None else tau_h                    # 02_SPEC §1.3 / 01_RULES §4
        self.Xp = np.asarray(Xp, complex)
        assert self.Xp.shape == (Nt, Tp)
        assert code.Ns == Nt * self.Td
        self.prior = None                                                      # no channel prior object: i.i.d. by construction
        self.cfg_dump = dict(arm="R3-bigamp", class_="R3BiGAMP", beta=beta, t_in=t_in, tau_h=self.tau_h,
                             channel_prior="iid CN(0,1/Nr) -- Table III admits only element-wise separable priors",
                             symbol_prior="separable QPSK from the decoder extrinsic bit marginals",
                             out_channel="AWGN closed form, eqs (71)-(72)", damping="nubar_p, nu_p, nu_s, s_hat, x_hat, h_hat",
                             erratum="eq (95) sign NOT followed; (R7) sign used", stop_rule="(R17) logged only",
                             var_floor=VAR_FLOOR, nu_cap=NU_CAP, iters="outer x t_in")

    def transmit(self, u, perm, H, rng):
        x = self.code.encode(u)
        grid = np.empty(self.Nt * self.Td, complex)
        grid[perm] = x
        X = np.hstack([self.Xp, grid.reshape(self.Td, self.Nt).T])
        W = np.sqrt(self.sigma2 / 2) * (rng.standard_normal((self.Nr, self.T)) + 1j * rng.standard_normal((self.Nr, self.T)))
        return X, H @ X + W

    def run(self, Y, H, u, perm, n_iter=N_ITER):
        Nr, Nt, Tp, Td = self.Nr, self.Nt, self.Tp, self.Td
        s2, code, st_tr = self.sigma2, self.code, self.code.st
        h_norm2 = float(np.sum(np.abs(H) ** 2))
        Ns = code.Ns

        Hh, nuh = pilot_lmmse_init(Y, self.Xp, s2, self.tau_h, Nr, Nt)
        Xh = np.hstack([self.Xp, np.zeros((Nt, Td), complex)])
        nux = np.hstack([np.zeros((Nt, Tp)), np.ones((Nt, Td))])
        st = BiGAMPState(Hh, nuh, Xh, nux)

        La = np.zeros((Ns, 2))                                                 # decoder extrinsic bit LLRs, code order
        log = {k: [] for k in KEYS_LOG}
        last = (np.zeros((Nt, Td), complex), np.ones((Nt, Td)))
        n_div = 0

        def x_prior(rhat, nu_r):
            xg, vg = qpsk_posterior(grid_to_code(rhat[:, Tp:], perm), grid_to_code(nu_r[:, Tp:], perm), La)
            return (np.hstack([self.Xp, code_to_grid(xg, perm, Nt, Td)]),
                    np.hstack([np.zeros((Nt, Tp)), code_to_grid(vg, perm, Nt, Td)]))

        for t in range(n_iter):
            for _ in range(self.t_in):
                if st.diverged:
                    n_div += 1
                    break
                st, out = bigamp_iter(st, Y, s2, self.beta, self.tau_h, x_prior)
                if out is not None:
                    last = (out[0][:, Tp:], out[1][:, Tp:])
            r_code = grid_to_code(last[0], perm)
            tau_code = np.maximum(grid_to_code(last[1], perm), VAR_FLOOR)
            # AMP's r_hat is already the cavity (extrinsic) observation: the decoder gets NO a-priori here,
            # and returns its own extrinsic pmf -> no double counting of the code constraint.
            P, Lu, Pe = st_tr.bcjr(r_code, tau_code, code.K, return_info=True, return_ext=True)
            La = bit_llrs_from_pmf(Pe)
            xbar = P @ code.st.CONST
            v = (P @ (np.abs(code.st.CONST) ** 2)).real - np.abs(xbar) ** 2
            uhat = (Lu.reshape(-1) < 0).astype(int)

            log["nmse"].append(float(np.sum(np.abs(st.Hh - H) ** 2) / h_norm2))
            log["ber"].append(float(np.mean(uhat != u)))
            log["blk_err"].append(int(np.any(uhat != u)))
            log["tauL_mean"].append(float(np.mean(tau_code)))
            log["tauL_gmean"].append(float(np.exp(np.mean(np.log(tau_code)))))
            log["alphaD"].append(float(np.mean(np.clip(v / tau_code, EPS_CLIP, 1 - EPS_CLIP))))
            log["nu_q"].append(np.nan)
            log["alphaH"].append(np.nan)
            log["nuE"].append(float(np.mean(st.nuh)))
            log["hE_norm"].append(float(np.linalg.norm(st.Hh)))
            log["tauL_clip_frac"].append(float(np.mean(grid_to_code(last[1], perm) <= VAR_FLOOR)))
            log["alphaD_clip"].append(0.0)

        out = {k: np.array(v) for k, v in log.items()}
        out["diverged"] = np.full(n_iter, float(st.diverged))
        out["stop_hits"] = np.full(n_iter, float(st.stop_hits))
        return out


# ----------------------------------------------------------------------------- real-valued reference core (test B4)
def bigamp_iter_real(Hh, nuh, Xh, nux, sh, Y, sigma2, tau_h, tau_x, beta=1.0,
                     mem=None):
    """Literal REAL transcription of Table III with Gaussian priors on both factors, no damping.
    Used only by test B4: feeding the complex core purely real data must reproduce this bit for bit."""
    m = mem if mem is not None else {}
    nubp = (Hh ** 2) @ nux + nuh @ (Xh ** 2)
    pbar = Hh @ Xh
    if "nubp" in m:
        nubp = beta * nubp + (1 - beta) * m["nubp"]
    nup = nubp + nuh @ nux
    if "nup" in m:
        nup = beta * nup + (1 - beta) * m["nup"]
    nup = np.maximum(nup, 1e-12)
    phat = pbar - sh * nubp
    d = nup + sigma2
    nus = 1.0 / d
    sh_new = (Y - phat) / d
    if "nus" in m:
        nus = beta * nus + (1 - beta) * m["nus"]
        sh_new = beta * sh_new + (1 - beta) * sh
    Xb = beta * Xh + (1 - beta) * m.get("Xbar", Xh)
    Hb = beta * Hh + (1 - beta) * m.get("Hbar", Hh)
    nu_r = np.minimum(1.0 / np.maximum((Hb.T ** 2) @ nus, 1e-12), 1e12)
    rhat = Xb * (1.0 - nu_r * (nuh.T @ nus)) + nu_r * (Hb.T @ sh_new)
    nu_q = np.minimum(1.0 / np.maximum(nus @ (Xb ** 2).T, 1e-12), 1e12)
    qhat = Hb * (1.0 - nu_q * (nus @ nux.T)) + nu_q * (sh_new @ Xb.T)
    Xn = (tau_x / (tau_x + nu_r)) * rhat
    nxn = tau_x * nu_r / (tau_x + nu_r)
    Hn = (tau_h / (tau_h + nu_q)) * qhat
    nhn = np.maximum(tau_h * nu_q / (tau_h + nu_q), 1e-12)
    m.update(nubp=nubp, nup=nup, nus=nus, Xbar=Xb, Hbar=Hb)
    return Hn, nhn, Xn, np.maximum(nxn, 0.0), sh_new, rhat, nu_r, m


# ----------------------------------------------------------------------------- undamped reference core (test B1)
def bigamp_iter_plain(Hh, nuh, Xh, nux, sh, Y, sigma2, tau_h, x_prior, drop_onsager=False):
    """Independent, literal transcription of Table III (R1)-(R16) with NO damping and no state object.
    Test B1 asserts that bigamp_iter(beta=1) reproduces this trajectory to <= 1e-14.
    drop_onsager=True zeroes the s_hat(t-1) term of (R4) -- test B5 asserts this CHANGES the result."""
    nubp = (np.abs(Hh) ** 2) @ nux + nuh @ (np.abs(Xh) ** 2)                   # (R1)
    pbar = Hh @ Xh                                                             # (R2)
    nup = nubp + nuh @ nux                                                     # (R3)
    phat = pbar - (0.0 if drop_onsager else sh * nubp)                         # (R4)
    nu_z, zhat, nus, sh_new = awgn_out(Y, phat, nup, sigma2)                   # (R5)-(R8), eqs (71)-(72)
    nu_r = 1.0 / ((np.abs(Hh) ** 2).T @ nus)                                   # (R9)
    rhat = Xh * (1.0 - nu_r * (nuh.T @ nus)) + nu_r * (Hh.conj().T @ sh_new)   # (R10)
    nu_q = 1.0 / (nus @ (np.abs(Xh) ** 2).T)                                   # (R11)
    qhat = Hh * (1.0 - nu_q * (nus @ nux.T)) + nu_q * (sh_new @ Xh.conj().T)   # (R12)
    Xn, nxn = x_prior(rhat, nu_r)                                              # (R13)(R14)
    nhn = tau_h * nu_q / (tau_h + nu_q)                                        # (R15)
    Hn = (tau_h / (tau_h + nu_q)) * qhat                                       # (R16)
    return Hn, nhn, Xn, nxn, sh_new, rhat, nu_r
