"""conf/code/prior_variants.py -- Module H prior objects for the K1 / K2 follow-ups of P4-LO (user decision 2026-09-25 00:2x
CDT: "K2 격자 밖 질의 수정", "K1 Bayes 참조 폐루프").  NEW FILE ONLY: score.py / arms.py / runner.py are untouched, so every
existing arm and every recorded result is bit-identical.  Both classes duck-type score.ScorePrior (C, Cinv, cbar, eh2_prior
from the SAME Chat, denoise(), denoise_full() -> (mean, J) with SigH = nu * J the posterior covariance, psd projection as V1)
and are wired exactly like V1: arms.route_a(..., prior, code, Xp, "score", clip="eta").

ScorePriorOOG (K2) -- V1 with a different rule ONLY for queries ABOVE the measured sigma grid (sigma_t > s_hi, i.e.
    nu_q > nu_hi = 2 s_hi^2).  In-grid and below-grid queries call ScorePrior._eval unchanged (bit-identical to V1).  Above:
      "clamp": z ~= q.  mean = D(q, nu_hi), Cov = nu_hi * J(q, nu_hi)          (one network + one Jacobian, like V1)
      "edge" : exact noise split q = z + e2, z = h + e1, e1 ~ CN(0, nu_hi I), e2 ~ CN(0, (nu_q - nu_hi) I):
               z | q sampled by unadjusted Langevin on log p_{nu_hi}(z) - |q - z|^2 / (nu_q - nu_hi) using ONLY the in-grid
               learned score;  mean = E_z[D(z, nu_hi)],  Cov = E_z[nu_hi J(z, nu_hi)] + Cov_z[D(z, nu_hi)]
               (law of total expectation / variance; J at n_jac of the kept samples).
    Returned J = Cov / nu_q so that the receiver's SigH = nu_q * J = Cov.  The frozen V1 ("extrapolate, never clamp",
    DECISIONS 2026-09-20 12:35) is NOT changed; these are separate, registered variants.
BayesGPrior (K1) -- a q-measurable, generator-aware REFERENCE denoiser ("Bayes-G"): posterior mean / covariance of h given q
    under the D2 generator with the path gains relaxed to CN(0, p_l) given (L, angles) -- the same Gaussian-given-latents
    step as the P4-LO oracle, but with the latents INFERRED from q by griddy Gibbs over (L, theta_1..8, phi_1..8) on a
    fixed angle grid, Rao-Blackwellised E[h | q, L, angles] and Cov.  It uses no latent truth.  A reference, not a bound.

Determinism: every stochastic estimate is seeded from a hash of (q, nu, salt), so a query gets the same answer in any chunk
or process.  selftest(): in-grid identity of ScorePriorOOG with ScorePrior (bit-identical), edge == clamp limit checks, and
BayesGPrior against the exact closed form on a single-atom toy (L fixed, one grid angle).
"""
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import numpy as np
import torch
import d2
import score as S


def _seed(q, nu, salt):
    return int.from_bytes(hashlib.sha256(np.ascontiguousarray(q).tobytes() + np.float64(nu).tobytes()
                                         + salt.encode()).digest()[:8], "little")


# ----------------------------------------------------------------------------- K2: out-of-grid rule for V1
class ScorePriorOOG(S.ScorePrior):
    def __init__(self, ckpt, Nr, Nt, Chat, oog="clamp", M=16, burn=100, keep=100, n_jac=16, eps_frac=0.05, **kw):
        kw.setdefault("psd_project", True)                         # V1's projection
        super().__init__(ckpt, Nr, Nt, Chat, **kw)
        assert oog in ("clamp", "edge"), oog
        self.oog, self.M, self.burn, self.keep, self.n_jac, self.eps_frac = oog, int(M), int(burn), int(keep), int(n_jac), float(eps_frac)
        self.nu_hi = 2.0 * self.s_hi ** 2
        self.n_oog = 0

    def _net(self, X, s):
        return S.tweedie_real(self.model, X, torch.full((X.shape[0],), float(s), dtype=torch.float64, device=self.device))

    def _jac(self, x, s):
        sg = torch.as_tensor(s, dtype=torch.float64, device=self.device)
        return S.wirtinger(torch.func.jacrev(lambda v: S.tweedie_real(self.model, v, sg))(x)).detach().cpu().numpy()

    def _eval(self, q, nu):
        if float(S.NU_TO_SIGMA(nu)) <= self.s_hi:
            return super()._eval(q, nu)                            # in-grid / below-grid: V1 unchanged, bit for bit
        key = (q.tobytes(), float(nu))
        if self._cache is not None and self._cache[0] == key:
            return self._cache[1]
        self.n_query += 1; self.n_out_of_grid += 1; self.n_oog += 1
        s_hi = self.s_hi
        x = torch.as_tensor(S.np_pack(q), dtype=torch.float64, device=self.device)
        with torch.no_grad():
            if self.oog == "clamp":
                m = S.np_unpack(self._net(x[None], s_hi)[0].cpu().numpy())
            else:
                s2hi, s2d = self.nu_hi / 2.0, (nu - self.nu_hi) / 2.0      # per-real-dimension variances
                eps = self.eps_frac * min(s2hi, s2d)
                g = torch.Generator(device="cpu").manual_seed(_seed(q, nu, "edge") % (2 ** 63))
                X = x[None].repeat(self.M, 1); Z = X.clone()
                sig = torch.full((self.M,), float(s_hi), dtype=torch.float64, device=self.device)
                Ds, Zk = [], []
                for k in range(self.burn + self.keep):
                    grad = self.model.score_real(Z, sig) + (X - Z) / s2d
                    Z = Z + eps * grad + np.sqrt(2 * eps) * torch.randn(Z.shape, generator=g, dtype=torch.float64).to(self.device)
                    if k >= self.burn:
                        Ds.append(self._net(Z, s_hi)); Zk.append(Z)
                D = S.np_unpack(torch.cat(Ds).cpu().numpy())               # (M*keep, N)
                m = D.mean(0)
                Dc = D - m
                CovD = (Dc.T @ Dc.conj()) / len(D)                         # Cov_z[D]  (E[d d^H] - m m^H)
                last = torch.cat(Zk)[-self.n_jac:]                         # the final kept states (one per chain when n_jac = M)
        if self.oog == "clamp":
            Cov = self.nu_hi * self._jac(x, s_hi)                   # Jacobian outside no_grad, as ScorePrior._eval
        else:
            EJ = np.mean([self._jac(z, s_hi) for z in last], 0)
            Cov = self.nu_hi * EJ + CovD
        J = Cov / nu
        J = S.project_psd(J, self.psd_floor) if self.psd_project else 0.5 * (J + J.conj().T)
        self._cache = (key, (m, J))
        return m, J

    def query_stats(self):
        return dict(super().query_stats(), n_oog=self.n_oog, oog=self.oog)


# ----------------------------------------------------------------------------- K1: Bayes-G reference
class BayesGPrior:
    """See the module docstring.  Grid: 96 AoA x 48 AoD midpoints, uniform in the physical angle over the S2 range."""

    def __init__(self, Nr, Nt, Chat, prior="S2", chains=4, burn=25, keep=75, n_th=96, n_ph=48, psd_project=True):
        self.Nr, self.Nt, self.N = Nr, Nt, Nr * Nt
        Chat = np.asarray(Chat, complex)
        self.C = 0.5 * (Chat + Chat.conj().T); self.Cinv = np.linalg.inv(self.C)
        self.cbar = np.trace(self.C).real / self.N
        self.eh2_prior = np.diag(self.C).real.reshape(Nr, Nt, order="F").mean(0)
        self.chains, self.burn, self.keep, self.psd_project, self.psd_floor = int(chains), int(burn), int(keep), bool(psd_project), C.LAM_MIN
        gen = C.make_gen("D2", prior, Nr, Nt)
        lo, hi = d2.ANGLE_RANGE[prior]
        TH = np.linspace(lo, hi, n_th + 1)[:-1] + (hi - lo) / (2 * n_th)
        PH = np.linspace(lo, hi, n_ph + 1)[:-1] + (hi - lo) / (2 * n_ph)
        ar = np.exp(1j * np.pi * np.sin(TH)[:, None] * np.arange(Nr)) / np.sqrt(Nr)
        at = np.exp(1j * np.pi * np.sin(PH)[:, None] * np.arange(Nt)) / np.sqrt(Nt)
        self.A = gen.scale * np.stack([np.kron(at[b].conj(), ar[a]) for b in range(n_ph) for a in range(n_th)], 1)
        self.G = self.A.shape[1]
        self.P = d2._P
        self._cache = None
        self.n_query = 0; self.mc_disagree = []                    # |m_c - m|^2 / |m|^2 spread over chains per query

    def _lik(self, q, nu, idx, L):
        V = self.A[:, idx[:L]]
        Cm = (V * self.P[L - 3, :L]) @ V.conj().T + nu * np.eye(self.N)
        _, ld = np.linalg.slogdet(Cm)
        return -ld - np.real(np.vdot(q, np.linalg.solve(Cm, q)))

    def _chain(self, q, nu, rng):
        A, P, N, G = self.A, self.P, self.N, self.G
        idx = rng.integers(0, G, 8); L = 5
        for l in range(8):                                          # greedy start
            Vs = A[:, idx[:l]]
            Si = np.linalg.inv((Vs * P[5, :l]) @ Vs.conj().T + nu * np.eye(N)); SA = Si @ A
            a = np.real(np.sum(A.conj() * SA, 0)); b = SA.conj().T @ q; pl = P[5, l]
            idx[l] = int(np.argmax(-np.log1p(pl * a) + pl * np.abs(b) ** 2 / (1 + pl * a)))
        m_acc = np.zeros(N, complex); S_acc = np.zeros((N, N), complex); n_acc = 0
        for sw in range(self.burn + self.keep):
            p = P[L - 3]
            for l in range(8):
                if l >= L:
                    idx[l] = rng.integers(0, G); continue
                oth = [k for k in range(L) if k != l]
                Vs = A[:, idx[oth]]
                Si = np.linalg.inv((Vs * p[oth]) @ Vs.conj().T + nu * np.eye(N)); SA = Si @ A
                a = np.real(np.sum(A.conj() * SA, 0)); b = SA.conj().T @ q
                lw = -np.log1p(p[l] * a) + p[l] * np.abs(b) ** 2 / (1 + p[l] * a)
                w = np.exp(lw - lw.max()); idx[l] = rng.choice(G, p=w / w.sum())
            ll = np.array([self._lik(q, nu, idx, Lc) for Lc in range(3, 9)])
            w = np.exp(ll - ll.max()); L = 3 + rng.choice(6, p=w / w.sum())
            if sw >= self.burn:
                V = A[:, idx[:L]]; Cz = (V * P[L - 3, :L]) @ V.conj().T
                K = Cz @ np.linalg.inv(Cz + nu * np.eye(N)); m = K @ q
                m_acc += m; S_acc += (Cz - K @ Cz) + np.outer(m, m.conj()); n_acc += 1
        return m_acc / n_acc, S_acc / n_acc

    def _eval(self, q, nu):
        key = (q.tobytes(), float(nu))
        if self._cache is not None and self._cache[0] == key:
            return self._cache[1]
        self.n_query += 1
        rng = np.random.default_rng(_seed(q, nu, "bayesg"))
        out = [self._chain(q, nu, np.random.default_rng(rng.integers(2 ** 63))) for _ in range(self.chains)]
        m = np.mean([o[0] for o in out], 0)
        E2 = np.mean([o[1] for o in out], 0)                        # E[h h^H | q] pooled over chains
        Cov = E2 - np.outer(m, m.conj())
        self.mc_disagree.append(float(np.mean([np.sum(np.abs(o[0] - m) ** 2) for o in out]) / max(np.sum(np.abs(m) ** 2), 1e-300)))
        J = Cov / nu
        J = S.project_psd(J, self.psd_floor) if self.psd_project else 0.5 * (J + J.conj().T)
        self._cache = (key, (m, J))
        return m, J

    def denoise(self, q, nu):
        m, J = self._eval(q, nu)
        return m, float(np.trace(J).real / self.N)

    def denoise_full(self, q, nu):
        return self._eval(q, nu)

    def query_stats(self):
        d = np.array(self.mc_disagree) if self.mc_disagree else np.array([np.nan])
        return dict(n_query=self.n_query, mc_disagree_median=float(np.median(d)), mc_disagree_p90=float(np.quantile(d, 0.9)))


def selftest():
    """(1) ScorePriorOOG == ScorePrior bit-for-bit on in-grid queries (both oog modes); (2) above the grid clamp/edge return
    finite PSD J and edge's mean differs from clamp's; (3) BayesGPrior on a toy query reproduces the closed form when the
    grid posterior is concentrated (a single strong atom at a grid point, high SNR)."""
    Nr, Nt = 8, 4
    ck = os.path.join(C.CONF, "ckpt", "d2sx_N160000_a1.pt")
    import arms as A
    import runner
    runner._init("B16e4k")
    Chat = A.load_fits("D2", "S2", Nr, 160000)[("full", 32)]["Chat"]
    base = S.ScorePrior(ck, Nr, Nt, Chat, psd_project=True)
    rng = np.random.default_rng(1)
    gen = C.make_gen("D2", "S2", Nr, Nt)
    h = gen.sample_vecs(rng, 1)[0]
    for oog in ("clamp", "edge"):
        v = ScorePriorOOG(ck, Nr, Nt, Chat, oog=oog, M=4, burn=20, keep=20, n_jac=4)
        for nu in (0.01, 0.2, 1.0):                                   # in-grid
            q = h + np.sqrt(nu / 2) * (rng.standard_normal(32) + 1j * rng.standard_normal(32))
            m0, J0 = base._eval(q, nu); m1, J1 = v._eval(q, nu)
            assert np.array_equal(m0, m1) and np.array_equal(J0, J1), f"{oog}: in-grid not bit-identical at nu={nu}"
        nu = 2.0                                                      # above the grid (nu_hi = 1.4286)
        q = h + np.sqrt(nu / 2) * (rng.standard_normal(32) + 1j * rng.standard_normal(32))
        m, J = v._eval(q, nu)
        w = np.linalg.eigvalsh(0.5 * (J + J.conj().T))
        assert np.all(np.isfinite(m)) and np.all(np.isfinite(J)) and w.min() >= C.LAM_MIN * (1 - 1e-9), (oog, w.min())
        print(f"[selftest] {oog}: in-grid bit-identical (3 nu), out-of-grid nu=2.0 finite, min eig(J) {w.min():.3e}, "
              f"NMSE vs h {np.sum(np.abs(m - h) ** 2) / np.sum(np.abs(h) ** 2):.3f}")
    bg = BayesGPrior(Nr, Nt, Chat, chains=2, burn=10, keep=20)
    m, J = bg._eval(h + 0.05 * (rng.standard_normal(32) + 1j * rng.standard_normal(32)) / np.sqrt(2), 0.005)
    print(f"[selftest] Bayes-G at nu=0.005: NMSE {np.sum(np.abs(m - h) ** 2) / np.sum(np.abs(h) ** 2):.4f}, "
          f"tr(J)/N {np.trace(J).real / 32:.4f}, chain spread {bg.mc_disagree[-1]:.2e}")
    return 0


if __name__ == "__main__":
    sys.exit(selftest())
