"""conf/code/sv.py -- the SECOND testbed "SV": clustered (extended) Saleh-Valenzuela narrowband channel, prior id 'SV8e'.

User decision 2026-09-26 00:06 CDT (conf/DECISIONS.md): second testbed = SV8e, El Ayach et al., IEEE TWC 2014 parameters
with the arrays / directions mapped onto our cell conventions.  Selection was by channel statistics only
(conf/results/review_next/testbed2_phase0/selection.md; the probe generator is .../testbed2_phase0/code/sv_probe.py).
It runs through the D2 pipeline as a prior VARIANT of testbed D2 (TBID 2), exactly like D3 = prior 'S2c': its own PID (6),
so every SV8e stream is a NEW stream, and 'SV8e' is in every output name (rung D2SXSV8e<N>, ckpt d2sx_SV8e_*, fits
fit_SV8e_Nr*_*, sigma grid sigma_grid_D2_SV8e).  common.make_gen / make_pilots dispatch here for prior in C.SV_PRIORS;
the D2 code path (d2.py) is untouched (conf/code/selftest_sv.py checks every existing path bit for bit).

Channel model [every choice stated; values = selection.md "생성 설정"]
    H = SCALE * sum_{c=1..8} sum_{r=1..10} alpha_cr a_r(theta_cr) a_t(phi_cr)^H          (Nr x Nt, uplink: UE Nt=4 -> BS Nr)
    a_N(x)[n] = exp(j pi n sin x) / sqrt(N), n = 0..N-1  half-wavelength ULA, UNIT NORM, single V-pol, omni elements  (= d2.py)
    SCALE = sqrt(Nr Nt)                                                                                         (= d2.py)
    cluster-mean AoA  theta_c ~ U[-60 deg, 60 deg]   (BS 120-degree sector, the D2 S2 sector)
    cluster-mean AoD  phi_c   ~ U[-180 deg, 180 deg) (UE yaw uniform in [-pi, pi), pitch = roll = slant = 0; the omni
                                                      element makes the yaw a pure AoD shift)
    ray angles        theta_cr = theta_c + e, phi_cr = phi_c + e',  e, e' iid Laplace(0, b), b = 7.5 deg / sqrt(2)
                      (standard deviation 7.5 deg on BOTH sides; angles are not wrapped -- only sin() enters)
    ray gains         g_cr ~ CN(0, 1/80) iid (equal cluster powers 1/8, 10 rays each), then PER-BLOCK normalised:
                      alpha = g / ||g||, so sum_cr |alpha_cr|^2 = 1 in every block (pathloss / shadowing removed; this
                      deviates from El Ayach, who keeps the CN draw -- recorded in selection.md "주의점")
    no LOS component; narrowband block fading (one H per block); every block has all 80 rays (nothing to discard).
    h = vec(H) COLUMN-MAJOR, h[i + Nr j] = H[i, j]; complex128.
Normalisation [exact]: the ray phases are uniform and independent of the angles, so the cross terms vanish in
expectation and E||H||_F^2 = SCALE^2 sum |alpha|^2 ||a_r||^2 ||a_t||^2 = Nr Nt, E|H_ab|^2 = 1 for every entry.
(The probe used UN-normalised steering with a_t^T and rescaled by the measured training power; with unit-norm steering and
SCALE that rescale is 1 analytically.  a_t^H vs the probe's a_t^T is phi -> -phi, which leaves U[-pi, pi) + Laplace
invariant in distribution -- the same model; testbed_sv.py checks the construction identity and the probe statistics.)

Conditional law [exact]: GIVEN all 80 ray angles, h = V alpha with V = [SCALE conj(a_t,l) kron a_r,l]_l fixed and
alpha = g/||g|| UNIFORM on the unit sphere of C^80.  Before the normalisation (alpha = g) h would be complex Gaussian;
after it h is elliptically contoured (a Gaussian divided by an independent chi scalar), covariance V V^H / 80, and its
fourth-moment ratio is E|h|^4/(E|h|^2)^2 = 2 P/(P+1) = 160/81 = 1.9753 for P = 80 rays at every angle set (complex
Gaussian: 2; D2 S2: 2 - sum p_l^2 = 1.61..1.75).  Near-Gaussian given the angles, not exactly Gaussian (testbed_sv.py TSVd).
Ensemble second moment [exact]: C_ens = kron(Rt^T, Rr), Rt/Rr Toeplitz with lags r(k) = E[exp(j pi k sin x)]:
    transmit side: phi mod 2 pi is UNIFORM (uniform circle + any offset), so r_t(k) = J_0(pi k) (== D2 prior U2's Rt);
    receive side : theta = U[-pi/3, pi/3] + Laplace, density f = (F_L(t - lo) - F_L(t - hi))/(hi - lo) in closed form,
                   r_r(k) = int f(t) exp(j pi k sin t) dt by adaptive quadrature (real: f is symmetric).
The pilot decision is the D2 T2b rule on Rt (d2.T2B_ERANK_FRAC): DFT pilots unless erank(Rt) < 0.9 Nt.  MEASURED at Nt = 4:
erank(Rt) = 3.3229 = 0.831 Nt < 0.9 Nt -> EIGEN-ALIGNED pilots for Tp <= Nt (as D2 prior U2, whose Rt is identical): the
full-circle AoD makes sin(phi) arcsine-distributed (endfire-heavy), so the transmit side is NOT near-white.  Tp > Nt (C7/C8)
keeps make_pilots' DFT-row branch.  (testbed_sv.py TSVb/TSVc; flagged for the user: selection.md had assumed DFT.)
Model constants live here as module constants, as in d2.py (the conf pipeline has no YAML layer; the testbed is FROZEN
by the user decision -- change nothing here without a new decision and a new prior id).
"""
import numpy as np
from scipy.integrate import quad
from scipy.special import j0

import d2

PRIORS = ("SV8e",)                        # == common.SV_PRIORS
N_CL, N_RAY = 8, 10                       # clusters x rays per cluster (El Ayach TWC 2014)
P_RAYS = N_CL * N_RAY
SPREAD = np.deg2rad(7.5)                  # Laplacian ray-offset STANDARD DEVIATION, both sides
LAP_B = SPREAD / np.sqrt(2.0)             # Laplace scale: std = sqrt(2) b
AOA = (-np.pi / 3, np.pi / 3)             # cluster-mean AoA ~ U[-60, 60] deg (BS 120-degree sector, = D2 S2)
AOD = (-np.pi, np.pi)                     # cluster-mean AoD ~ U[-180, 180) deg (UE yaw uniform)
CHUNK = 8192                              # blocks per _channels step (memory only; the output does not depend on it)


def _lap_cdf(x):
    return np.where(x < 0, 0.5 * np.exp(np.minimum(x, 0) / LAP_B), 1.0 - 0.5 * np.exp(-np.maximum(x, 0) / LAP_B))


def aoa_density(t):
    """Density of theta_cr = U[lo, hi] + Laplace(0, LAP_B)  [exact convolution]."""
    lo, hi = AOA
    return (_lap_cdf(t - lo) - _lap_cdf(t - hi)) / (hi - lo)


def _lag_rx(k):
    lo, hi, w = AOA[0], AOA[1], 40 * LAP_B    # tails beyond 40 b carry < e^-40 of the mass
    z = np.pi * k
    re = quad(lambda t: aoa_density(t) * np.cos(z * np.sin(t)), lo - w, hi + w, points=[lo, hi], limit=400,
              epsabs=1e-13, epsrel=1e-13)[0]
    im = quad(lambda t: aoa_density(t) * np.sin(z * np.sin(t)), lo - w, hi + w, points=[lo, hi], limit=400,
              epsabs=1e-13, epsrel=1e-13)[0]
    return re + 1j * im


def _toeplitz(r):
    r = np.asarray(r)
    assert np.max(np.abs(np.imag(r))) < 1e-10, "symmetric angle law must give a real lag sequence"
    k = np.arange(len(r))
    return np.real(r)[np.abs(k[:, None] - k[None, :])].astype(float)


_SIDES = {}


def ensemble_sides_sv(prior, Nr, Nt):
    """(Rt, Rr, informative) for C_ens = kron(Rt^T, Rr), tr = Nt / Nr -- same contract as d2.ensemble_sides_d2."""
    assert prior in PRIORS, prior
    key = (prior, Nr, Nt)
    if key not in _SIDES:
        Rt = _toeplitz(j0(np.pi * np.arange(Nt)))
        Rr = _toeplitz([_lag_rx(k) for k in range(Nr)])
        _SIDES[key] = (Rt, Rr, bool(d2._erank(np.linalg.eigvalsh(Rt)) < d2.T2B_ERANK_FRAC * Nt))
    return _SIDES[key]


class SVGen:
    rot = 0.0                             # NEXT_EXPERIMENTS_ROT16e4: receive-array rotation (rad) added to every ray AoA
    """SV8e generator with the D2Gen slots the pipeline uses: .sample(rng), .sample_vecs(rng, n), .prior (None: no
    closed-form density or exact score, like D2), .name ("D2": it runs under testbed D2), .kind, .Nr/.Nt/.N."""

    name = "D2"
    prior = None

    def __init__(self, prior, Nr, Nt):
        assert prior in PRIORS, f"SV priors are {PRIORS}, got {prior!r}"
        self.kind = prior
        self.Nr, self.Nt, self.N = Nr, Nt, Nr * Nt
        self.scale = np.sqrt(Nr * Nt)

    @staticmethod
    def _gains(rng, n):
        g = (rng.standard_normal((n, P_RAYS)) + 1j * rng.standard_normal((n, P_RAYS))) / np.sqrt(2.0 * P_RAYS)
        return g / np.sqrt(np.sum(g.real ** 2 + g.imag ** 2, 1, keepdims=True))     # per-block sum |alpha|^2 = 1

    def _draw(self, rng, n):
        """One block per row: ray angles theta, phi (n, 80) (cluster c = columns 10c..10c+9) and gains alpha (n, 80)."""
        mA = AOA[0] + (AOA[1] - AOA[0]) * rng.random((n, N_CL))
        mD = AOD[0] + (AOD[1] - AOD[0]) * rng.random((n, N_CL))
        th = np.repeat(mA, N_RAY, 1) + rng.laplace(0.0, LAP_B, (n, P_RAYS)) + self.rot    # (+ ROT16e4 drift)
        ph = np.repeat(mD, N_RAY, 1) + rng.laplace(0.0, LAP_B, (n, P_RAYS))
        return th, ph, self._gains(rng, n)

    def _channels(self, th, ph, alpha):
        """(n, 80) ray angles + gains -> (n, Nr, Nt) complex128, computed CHUNK blocks at a time."""
        n = len(alpha)
        out = np.empty((n, self.Nr, self.Nt), complex)
        for i in range(0, n, CHUNK):
            s = slice(i, i + CHUNK)
            ar = np.exp(1j * np.pi * np.sin(th[s])[..., None] * np.arange(self.Nr)) / np.sqrt(self.Nr)
            at = np.exp(1j * np.pi * np.sin(ph[s])[..., None] * np.arange(self.Nt)) / np.sqrt(self.Nt)
            out[s] = self.scale * np.einsum("nl,nli,nlj->nij", alpha[s], ar, at.conj(), optimize=True)
        return out

    def sample(self, rng):
        return self._channels(*self._draw(rng, 1))[0]

    def sample_paths(self, rng):
        """(H, P): H EXACTLY as sample() and the per-ray matrices P (80, Nr, Nt) (NEXT_EXPERIMENTS_DOP16e4)."""
        th, ph, al = self._draw(rng, 1)
        ar = np.exp(1j * np.pi * np.sin(th)[..., None] * np.arange(self.Nr)) / np.sqrt(self.Nr)
        at = np.exp(1j * np.pi * np.sin(ph)[..., None] * np.arange(self.Nt)) / np.sqrt(self.Nt)
        P = self.scale * np.einsum("nl,nli,nlj->nlij", al, ar, at.conj())[0]
        return self._channels(th, ph, al)[0], P

    def sample_vecs(self, rng, n):
        """(n, Nr*Nt) complex128, row i = vec(H_i) column-major (== H.reshape(-1, order='F'))."""
        return self._channels(*self._draw(rng, n)).transpose(0, 2, 1).reshape(n, self.N)

    def sample_angles(self, rng, n, angles=None):
        """n draws with ALL 80 ray angles held FIXED, only the gains alpha = g/||g|| redrawn (the conditional law above).
        Returns (H (n, Nr, Nt), angles = (theta (80,), phi (80,))); pass `angles` back to keep the same set."""
        if angles is None:
            th, ph, _ = self._draw(rng, 1)
            angles = (th[0], ph[0])
        th, ph = angles
        return self._channels(np.broadcast_to(th, (n, P_RAYS)), np.broadcast_to(ph, (n, P_RAYS)),
                              self._gains(rng, n)), angles


if __name__ == "__main__":
    g = SVGen("SV8e", 8, 4)
    X = g.sample_vecs(np.random.default_rng(0), 5)
    Hs = g._channels(*g._draw(np.random.default_rng(0), 5))
    assert np.array_equal(X, np.array([H.reshape(-1, order="F") for H in Hs])), "vec is not column-major"
    assert np.array_equal(g.sample(np.random.default_rng(7)).reshape(-1, order="F"),
                          g.sample_vecs(np.random.default_rng(7), 1)[0])
    th, ph, al = g._draw(np.random.default_rng(1), 3 * CHUNK + 5)              # chunking does not change the output
    Hc = g._channels(th, ph, al)
    assert np.array_equal(Hc[-5:], g._channels(th[-5:], ph[-5:], al[-5:])), "block output depends on the chunking"
    assert np.allclose(np.sum(np.abs(al) ** 2, 1), 1.0, rtol=0, atol=1e-12)
    # receive-side quadrature vs Monte Carlo of the same angle law; transmit side = J_0 (uniform circle)
    Rt, Rr, inf = ensemble_sides_sv("SV8e", 8, 4)
    t = np.random.default_rng(2)
    x = AOA[0] + (AOA[1] - AOA[0]) * t.random(2_000_000) + t.laplace(0, LAP_B, 2_000_000)
    mc = np.array([np.mean(np.cos(np.pi * k * np.sin(x))) for k in range(8)])
    assert np.max(np.abs(mc - Rr[0])) < 5e-3, np.max(np.abs(mc - Rr[0]))
    lag_q = np.array([quad(lambda u: np.cos(np.pi * k * np.sin(u)), -np.pi, np.pi)[0] / (2 * np.pi) for k in range(4)])
    assert np.max(np.abs(lag_q - Rt[0])) < 1e-10
    print(f"sv selfcheck OK | Rt lags {np.round(Rt[0], 5)} | Rr lags {np.round(Rr[0], 5)} (MC max err "
          f"{np.max(np.abs(mc - Rr[0])):.1e}) | informative(Rt) = {inf}")
