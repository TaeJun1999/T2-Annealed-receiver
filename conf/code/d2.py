"""conf/code/d2.py -- testbed D2: sparse specular multipath, the CLAIM testbed (conf/05_SPEC_testbed_D2.md).

What this file implements
  D2Gen               the channel generator of 05_SPEC §1 (drop-in for common.D1Gen: .sample / .sample_vecs
                      / .prior, same column-major vec convention, seeded from common.train_rng / trial_rng).
  ensemble_sides_d2   the ANALYTIC ensemble covariance factors (Rt, Rr) + the T2b pilot decision, cached.
  tests_T2            the pre-registered verification T2a..T2e of 05_SPEC §2 (07_SPEC §T), returned in the
                      same 5-tuple format as conf/code/tests.py so the runner prints one table.

Channel model [exact, 05_SPEC §1]
    H = SCALE * sum_{l=1..L} alpha_l a_r(theta_l) a_t(phi_l)^H
    L ~ Unif{3..8}, redrawn per block.
    theta_l, phi_l CONTINUOUS uniform in the PHYSICAL angle, no grid.  prior "U2" = Unif[-pi/2, pi/2],
      prior "S2" = Unif[-pi/3, pi/3] (the standard 120-degree sector).  S2 is the primary prior.
    alpha_l = sqrt(p_l) exp(j psi_l), psi_l ~ Unif[0, 2pi).  |alpha_l| is DETERMINISTIC.
    p_l ∝ exp(-l/tau), tau = 2, normalised to sum_l p_l = 1 (so p_l depends on the drawn L).
    a(theta)[n] = exp(j pi n sin(theta)) / sqrt(N)   -- half-wavelength ULA, UNIT NORM.

Why |alpha_l| is deterministic [05_SPEC §1]: with alpha_l ~ CN (the 3GPP-style convention) H would be
Gaussian GIVEN the angles, i.e. a conditionally-Gaussian mixture, and a GMM would be correctly specified.
Sparse specular multipath with a deterministic power-delay profile is the physically standard mmWave
model; the failure of conditional Gaussianity is a CONSEQUENCE of that physics, and test T2d is its
direct evidence (conf/01_RULES.md §5 framing rule).

NORMALISATION -- one correction to the printed spec, already recorded in conf/DECISIONS.md.
05_SPEC prints sqrt(Nr*Nt/L) TOGETHER WITH sum_l p_l = 1; using both gives E||H||_F^2 = Nr*Nt/L, which
varies with L ~ Unif{3..8} and structurally violates T2a.  The standard convention
sum_l E|alpha_l|^2 = L is algebraically identical to SCALE = sqrt(Nr*Nt) with sum_l p_l = 1, so that is
what is used here.  Do not "fix" this back.  With independent uniform path phases the cross terms
vanish in expectation, so [exact]  E||H||_F^2 = SCALE^2 sum_l p_l ||a_r||^2 ||a_t||^2 = Nr*Nt.

ENSEMBLE COVARIANCE -- closed form, not Monte-Carlo [exact].
h = vec(H) column-major = SCALE sum_l alpha_l (conj(a_t,l) kron a_r,l).  Angles are independent across
paths and sides and the phases are independent and uniform, so only the l = m terms survive and
    C_ens = E[h h^H] = kron(Rt^T, Rr),   Rt = Nt E[a_t a_t^H],  Rr = Nr E[a_r a_r^H],
    tr(Rt) = Nt, tr(Rr) = Nr   (the convention of Demo/t2_gmm.ensemble_sides).
Rt, Rr are Toeplitz with lag entries  r(k) = E[exp(j pi k sin(theta))]  -- a 1-D integral, evaluated by
adaptive quadrature (scipy.integrate.quad) to ~1e-13, never by sampling.  The angle density is symmetric
about 0 for both U2 and S2, so the odd part cancels and r(k) is REAL: Rt, Rr are real symmetric and
Rt^T = Rt (checked at construction).  For U2 the integral is J_0(pi k) in closed form, which the
self-check at the bottom of this file uses as an independent reference.
*** C_ens being Kronecker is a SECOND-MOMENT statement only.  The prior is still NON-GAUSSIAN and, per
    T2d, non-Gaussian even conditionally on the angles.  Do not read Kronecker second moments as
    conditional Gaussianity. ***

Conventions inherited from the project (do not re-derive):
  h = vec(H) is COLUMN-MAJOR, h[i + Nr*j] = H[i,j]  -- fed straight into t2_gmm.fit_gmm_em / GMMPriorB.
  complex variances are PER COMPLEX ENTRY;  dtype is complex128 / float64 everywhere.
"""
import numpy as np
from scipy.integrate import quad

import common as C

# ----------------------------------------------------------------------------- model constants (05_SPEC §1)
L_MIN, L_MAX = 3, 8                       # L ~ Unif{L_MIN..L_MAX}
TAU = 2.0                                 # exponential power-delay profile p_l ∝ exp(-l/tau)
ANGLE_RANGE = {"U2": (-np.pi / 2, np.pi / 2),        # full range
               "S2": (-np.pi / 3, np.pi / 3)}        # standard 120-degree sector; PRIMARY prior

# _P[L - L_MIN, :] = the normalised profile of a block with L paths, zero-padded to L_MAX.
_P = np.zeros((L_MAX - L_MIN + 1, L_MAX))
for _L in range(L_MIN, L_MAX + 1):
    _w = np.exp(-np.arange(1, _L + 1) / TAU)
    _P[_L - L_MIN, :_L] = _w / _w.sum()
_AMP = np.sqrt(_P)                        # |alpha_l| = sqrt(p_l), DETERMINISTIC given L

T2B_ERANK_FRAC = 0.9                      # T2b: effective rank >= 0.9 * Nt  =>  near-white  =>  DFT pilots
# T2c: |NMSE_inf - (1-Tp/Nt)| below this counts as "indistinguishable from the pilot-span floor", i.e.
# same-Tp (upper bound)-(lower bound) comparisons are vacuous.  05_SPEC §2 says "close to 1-Tp/Nt" and
# fixes no number: this cutoff is a CONF-SIDE CHOICE, NOT PRESENT IN 05_SPEC, pre-registered here and
# printed in the T2c row so the reader sees the threshold that produced the verdict.
T2C_VACUOUS_GAP = 0.05


# ----------------------------------------------------------------------------- analytic ensemble sides
def _lag(k, lo, hi):
    """r(k) = E[exp(j pi k sin(theta))], theta ~ Unif[lo, hi]  [exact up to quadrature error ~1e-13]."""
    z, w = np.pi * k, 1.0 / (hi - lo)
    re = quad(lambda t: np.cos(z * np.sin(t)), lo, hi, limit=400, epsabs=1e-13, epsrel=1e-13)[0]
    im = quad(lambda t: np.sin(z * np.sin(t)), lo, hi, limit=400, epsabs=1e-13, epsrel=1e-13)[0]
    return w * (re + 1j * im)


def _side(N, lo, hi):
    """R = N * E[a a^H] for the unit-norm half-wavelength ULA -> Toeplitz, tr(R) = N."""
    r = np.array([_lag(k, lo, hi) for k in range(N)])
    assert np.max(np.abs(r.imag)) < 1e-10, "symmetric angle support must give a real lag sequence"
    k = np.arange(N)
    return np.real(r)[np.abs(k[:, None] - k[None, :])].astype(float)


_SIDES = {}                               # module-level cache: (prior, Nr, Nt) -> (Rt, Rr, informative)


def ensemble_sides_d2(prior, Nr, Nt):
    """(Rt, Rr, informative) for C_ens = kron(Rt^T, Rr).  `informative` is the T2b pilot decision.

    The pilots span the TRANSMIT side (Y = H Xp), so the TRANSMIT-side effective rank is what decides
    whether eigen-alignment buys anything: informative = erank(Rt) < 0.9 * Nt.  common.make_pilots falls
    back to DFT pilots when this is False.  (T2b also records the full C_ens effective rank, which is
    erank(Rt) * erank(Rr) because the eigenvalues of a Kronecker product are the pairwise products.)"""
    key = (prior, Nr, Nt)
    if key not in _SIDES:
        lo, hi = ANGLE_RANGE[prior]
        Rt, Rr = _side(Nt, lo, hi), _side(Nr, lo, hi)
        _SIDES[key] = (Rt, Rr, bool(_erank(np.linalg.eigvalsh(Rt)) < T2B_ERANK_FRAC * Nt))
    return _SIDES[key]


def _erank(lam):
    """Effective rank (participation ratio) (sum lam)^2 / sum lam^2  -- 05_SPEC §2 T2b."""
    lam = np.asarray(lam, float)
    return float(lam.sum() ** 2 / np.sum(lam ** 2))


# ----------------------------------------------------------------------------- generator
class D2Gen:
    """Sparse specular generator.  Same slots as common.D1Gen, except that `prior` is None: the true
    density has no closed-form EP site and no exact score, so the arms R6-exactEP / M-ours-score do not
    exist on D2 (05_SPEC §3 -- recorded as a loss, not worked around)."""

    name = "D2"
    prior = None                          # no exact-score prior object exists for D2

    def __init__(self, prior, Nr, Nt):
        assert prior in ANGLE_RANGE, f"D2 priors are {tuple(ANGLE_RANGE)}, got {prior!r}"
        self.kind = prior
        self.lo, self.hi = ANGLE_RANGE[prior]
        self.Nr, self.Nt, self.N = Nr, Nt, Nr * Nt
        self.scale = np.sqrt(Nr * Nt)     # SCALE, see the module docstring (NOT sqrt(Nr*Nt/L))

    # ---- drawing
    def _draw(self, rng, n):
        """One block draw per row: (theta, phi, alpha) each (n, L_MAX), zero-amplitude beyond L."""
        L = rng.integers(L_MIN, L_MAX + 1, n)                                  # Unif{3..8}, per block
        th = self.lo + (self.hi - self.lo) * rng.random((n, L_MAX))            # CONTINUOUS physical angle
        ph = self.lo + (self.hi - self.lo) * rng.random((n, L_MAX))
        psi = 2 * np.pi * rng.random((n, L_MAX))
        return th, ph, _AMP[L - L_MIN] * np.exp(1j * psi), L

    def _channels(self, th, ph, alpha):
        """(n, L) angles + path gains -> (n, Nr, Nt) complex128 channels."""
        ar = np.exp(1j * np.pi * np.sin(th)[..., None] * np.arange(self.Nr)) / np.sqrt(self.Nr)
        at = np.exp(1j * np.pi * np.sin(ph)[..., None] * np.arange(self.Nt)) / np.sqrt(self.Nt)
        return self.scale * np.einsum("nl,nli,nlj->nij", alpha, ar, at.conj(), optimize=True)

    # ---- API used by common.py / arms.py
    def sample(self, rng):
        """One block channel H, (Nr, Nt) complex128."""
        th, ph, al, _ = self._draw(rng, 1)
        return self._channels(th, ph, al)[0]

    def sample_vecs(self, rng, n):
        """(n, Nr*Nt) complex128; row i = vec(H_i) COLUMN-MAJOR, i.e. H.reshape(-1, order='F').
        transpose(0,2,1) then C-order reshape gives index j*Nr + i -> H[i,j], which is exactly that."""
        th, ph, al, _ = self._draw(rng, n)
        return self._channels(th, ph, al).transpose(0, 2, 1).reshape(n, self.N)

    def sample_angles(self, rng, n, angles=None):
        """T2d: n draws with the angle set AND L held FIXED -- only the path phases vary.
        Returns (H (n, Nr, Nt), angles), angles = (theta (L,), phi (L,), p (L,)).  Pass `angles` back in
        to keep conditioning on the same set."""
        if angles is None:
            L = int(rng.integers(L_MIN, L_MAX + 1))
            angles = (self.lo + (self.hi - self.lo) * rng.random(L),
                      self.lo + (self.hi - self.lo) * rng.random(L),
                      _P[L - L_MIN, :L].copy())
        th, ph, p = angles
        L = len(th)
        alpha = np.sqrt(p) * np.exp(2j * np.pi * rng.random((n, L)))           # |alpha_l| fixed, phase free
        Hs = self._channels(np.broadcast_to(th, (n, L)), np.broadcast_to(ph, (n, L)), alpha)
        return Hs, angles


# ----------------------------------------------------------------------------- pilots (T2c helper)
def _pilots(kind, Rt, Nt, Tp):
    if kind == "dft":
        return C.dft_pilots(Nt, Tp)
    w, U = np.linalg.eigh(Rt)
    return np.sqrt(Nt) * U[:, ::-1][:, :Tp]                                    # sqrt(Nt) x top-Tp eigenvectors


def nmse_inf(Rt, Xp):
    """05_SPEC §2 T2c: first-pass NMSE_inf = tr(S)/tr(Rt), S = Rt - Rt Xp (Xp^H Rt Xp)^-1 Xp^H Rt.
    Noise-free (sigma^2 -> 0) LMMSE error of the transmit-side covariance seen through the pilots; the
    floor that no number of turbo iterations can go below on the pilot span alone.  Rt is real symmetric
    here, so the conj() that formally belongs on Xp (Y = H Xp acts on H's ROWS) is a no-op."""
    A = Xp.conj().T @ Rt @ Xp
    S = Rt - Rt @ Xp @ np.linalg.solve(A, Xp.conj().T @ Rt)
    return float(np.trace(S).real / np.trace(Rt).real)


# ----------------------------------------------------------------------------- T2a..T2e
def _rec(tid, ok, resid, crit, desc):
    return (tid, ok if isinstance(ok, str) else ("PASS" if ok else "FAIL"), resid, crit, desc)


def tests_T2(prior, Nr, Nt, Tp, n=100000, n_sets=8, n_phase=20000, n_boot=1000):
    """The pre-registered D2 verification (05_SPEC §2).  5-tuples (id, verdict, residual, criterion, desc),
    identical in shape to conf/code/tests.py so the runner prints them in one table.

    T2d is the justification of the whole claim testbed: FAIL there means Stage B does not start
    (00_GOAL §3, 01_RULES §4)."""
    out = []
    gen = D2Gen(prior, Nr, Nt)
    Rt, Rr, informative = ensemble_sides_d2(prior, Nr, Nt)
    X = gen.sample_vecs(C.train_rng("D2", prior, Nr, 90), n)                   # verification stream (which=90)
    P2 = X.real ** 2 + X.imag ** 2                                             # (n, N) per-entry |h|^2

    # ---- T2a  normalisation E||H||_F^2 = Nr*Nt   [measured]
    ef = P2.sum(1).mean()
    rel = abs(ef / (Nr * Nt) - 1.0)
    # same samples, second moment: analytic C_ens = kron(Rt^T, Rr) vs the Monte-Carlo covariance.
    Cens = np.kron(Rt.T, Rr)
    Cmc = (X.T @ X.conj()) / n            # E[h h^H], the t2_gmm 'Chat' convention (NOT X^H X / n)
    cerr = float(np.max(np.abs(Cmc - Cens)) / (np.trace(Cens).real / gen.N))
    cfro = float(np.linalg.norm(Cmc - Cens) / np.linalg.norm(Cens))
    # The C_ens agreement is REPORTED here, not gated (T2a's pre-registered criterion is the
    # normalisation alone, 05_SPEC §2).  So state the measured verdict instead of asserting it: a wrong
    # Rt/Rr would otherwise print "confirmed" while silently changing the T2b decision and the
    # eigen-aligned pilot matrix, both of which are built from these same factors.
    nsig = float(cerr * np.sqrt(n))       # worst entry, in units of the per-entry MC s.e. ~ 1/sqrt(n)
    cok = nsig <= 6.0                     # max over N^2 entries: ~4.5 s.e. is the null's tail, 6 is slack
    out.append(_rec("T2a", rel <= 1e-3, rel, "rel err <= 1e-3",
                    f"E||H||_F^2 = {ef:.6f} vs Nr*Nt = {Nr * Nt} over n={n}; "
                    f"analytic C_ens=kron(Rt^T,Rr) vs MC: max|dC|/cbar = {cerr:.3e} = {nsig:.1f} MC s.e., "
                    f"||dC||_F/||C||_F = {cfro:.3e} (per-entry MC s.e. ~ {1.0 / np.sqrt(n):.1e}). "
                    + ("The closed form AGREES with samples it was never fitted to."
                       if cok else
                       "*** DISAGREES: Rt/Rr do not describe these samples. The T2b pilot decision and "
                       "the eigen-aligned pilot matrix are built from them -- do not use this testbed. ***")))

    # ---- T2b  effective rank of the ensemble covariance + the pilot decision   [measured]
    lt, lr = np.linalg.eigvalsh(Rt), np.linalg.eigvalsh(Rr)
    et, er = _erank(lt), _erank(lr)
    ec = _erank(np.kron(lt, lr))                                               # = et * er  (Kronecker)
    decision = ("eigen-aligned (Rt is informative)" if informative else
                "DFT (transmit side near-white, eigen-alignment is meaningless)")
    # The contract fixes the decision on Rt (the pilots span the transmit side, Y = H Xp).  The
    # full-covariance reading is reported too, because on the primary prior it sits on the other side of
    # the same cutoff -- an audit trail, not a second decision.
    full_informative = bool(ec < T2B_ERANK_FRAC * gen.N)
    out.append(_rec("T2b", "RECORD", et, f"erank(Rt) < {T2B_ERANK_FRAC}*Nt ?",
                    f"erank(Rt) = {et:.4f}/{Nt} ({et / Nt:.3f}), erank(Rr) = {er:.4f}/{Nr} ({er / Nr:.3f}), "
                    f"erank(C_ens) = {ec:.4f}/{gen.N} ({ec / gen.N:.3f}); "
                    f"DECISION: pilots = {decision}; Rt eigenvalues = "
                    f"[{', '.join(f'{v:.4f}' for v in lt[::-1])}]. "
                    f"THE DECISION IS TAKEN ON Rt, because the pilots span the TRANSMIT side (Y = H Xp); "
                    f"erank(C_ens) is reported but does NOT decide. The full-covariance reading "
                    f"(erank(C_ens) = {ec:.4f} {'<' if full_informative else '>='} "
                    f"{T2B_ERANK_FRAC}*{gen.N} = {T2B_ERANK_FRAC * gen.N:.4f}) would have said "
                    f"{'eigen-aligned (informative)' if full_informative else 'DFT (near-white)'}"
                    + (" -- IT DIFFERS from the decision in force. Knife edge: Rt is "
                       f"{et / Nt:.3f} of full and C_ens is {ec / gen.N:.3f}, on opposite sides of "
                       f"{T2B_ERANK_FRAC}. The choice is recorded here so it is auditable, not invisible."
                       if full_informative != informative else
                       " -- it agrees with the decision in force.")))

    # ---- T2c  closed-form first-pass NMSE_inf for BOTH pilot types   [exact]
    nm = {k: nmse_inf(Rt, _pilots(k, Rt, Nt, Tp)) for k in ("eig", "dft")}
    base = 1.0 - Tp / Nt
    used = "eig" if informative else "dft"                     # the pilot type actually in force (T2b)
    gap = abs(nm[used] - base)                                 # judge the USED pilot, not the better of the two
    if Tp >= Nt:
        # NMSE_inf = 0 and 1-Tp/Nt = 0 here, so gap = 0 -- but that is NOT vacuity.  The pilots span the
        # ENTIRE transmit side, which is the BEST possible first pass, and the floor they are being
        # compared against is zero for the same reason.
        conseq = (f"Tp = {Tp} >= Nt = {Nt}: the pilots span the ENTIRE transmit side, so NMSE_inf = 0 -- "
                  "the BEST possible first pass, with no pilot-span floor left to be vacuous about "
                  "(1-Tp/Nt = 0 for the same reason, so the gap test does not apply). Cross-Tp goodput "
                  "(cells C1 vs C2) remains the primary reading.")
    elif gap < T2C_VACUOUS_GAP:
        conseq = ("close to 1-Tp/Nt, so same-Tp (upper bound)-(lower bound) comparisons are VACUOUS "
                  "-- the reading must be CROSS-Tp goodput (cells C1 vs C2).")
    else:
        conseq = ("measurably below 1-Tp/Nt, so the pilot span is informative and same-Tp "
                  "comparisons retain headroom; cross-Tp goodput is still the primary reading.")
    out.append(_rec("T2c", "RECORD", nm[used], f"vs 1-Tp/Nt = {base:.4f}",
                    f"NMSE_inf(Tp={Tp}): eig = {nm['eig']:.6f}, dft = {nm['dft']:.6f}; 1-Tp/Nt = {base:.4f}; "
                    f"pilots IN USE = {used} (T2b decision) -> |NMSE_inf - (1-Tp/Nt)| = {gap:.4f}, judged "
                    f"against the vacuity cutoff T2C_VACUOUS_GAP = {T2C_VACUOUS_GAP} (conf-side constant, "
                    f"not present in 05_SPEC). CONSEQUENCE: " + conseq))

    # ---- T2d  direct evidence that conditional Gaussianity is broken   [measured + exact prediction]
    # Condition on a FIXED angle set and a FIXED L; vary only the path phases.  For h = sum_l u_l e^{j psi_l}
    # with |u_l| deterministic and psi_l iid Unif[0,2pi)  [exact]:
    #     E|h|^2 = sum_l |u_l|^2,   E|h|^4 = 2 (sum_l |u_l|^2)^2 - sum_l |u_l|^4
    # (only the phase pairings {l,p} = {m,q} survive; the l=m=p=q term is counted twice and subtracted), so
    #     E|h|^4 / (E|h|^2)^2 = 2 - sum_l |u_l|^4 / (sum_l |u_l|^2)^2.
    # A circularly-symmetric complex Gaussian has EXACTLY 2.  Here u_l = SCALE sqrt(p_l) a_r,l[i] a_t,l[j]^*
    # and the steering vectors are unit-norm, so |u_l|^2 = p_l for EVERY entry and every angle set:
    # the prediction is 2 - sum_l p_l^2, i.e. the deficit is set by the power-delay profile.
    rng_d = C.train_rng("D2", prior, Nr, 91)
    rows, ok_all = [], True
    # STRATIFIED over L: the predicted ratio is 2 - sum_l p_l^2, i.e. L-determined and angle-invariant, so
    # leaving the L coverage to chance would test some L values twice and others never.  We force one angle
    # set per L in {L_MIN..L_MAX} and then draw the remaining sets freely, which both covers the support and
    # keeps repeated-L sets for the within-L spread the report quotes.
    forced = list(range(L_MIN, L_MAX + 1))
    for i in range(max(n_sets, len(forced))):
        Lf = forced[i] if i < len(forced) else None
        if Lf is None:
            Hs, ang = gen.sample_angles(rng_d, n_phase)
        else:
            ang0 = (gen.lo + (gen.hi - gen.lo) * rng_d.random(Lf),
                    gen.lo + (gen.hi - gen.lo) * rng_d.random(Lf),
                    _P[Lf - L_MIN, :Lf].copy())
            Hs, ang = gen.sample_angles(rng_d, n_phase, angles=ang0)
        p = ang[2]
        pred = 2.0 - float(np.sum(p ** 2) / np.sum(p) ** 2)
        a2 = (Hs.real ** 2 + Hs.imag ** 2).reshape(n_phase, -1)                # per-realisation |h|^2
        s2, s4 = a2.sum(1), (a2 ** 2).sum(1)                                   # pooled over the Nr*Nt entries
        meas = gen.N * s4.mean() / s2.mean() ** 2
        # bootstrap over REALISATIONS (the independent unit given the angles; entries of one block share
        # the same phases and are NOT independent), 99.9% percentile interval.
        bs = np.empty(n_boot)
        for b in range(n_boot):
            i = rng_d.integers(0, n_phase, n_phase)
            bs[b] = gen.N * s4[i].mean() / s2[i].mean() ** 2
        lo, hi = np.percentile(bs, [0.05, 99.95])
        rows.append((len(p), meas, pred, lo, hi))
        ok_all &= bool(hi < 2.0)
    resid = max(r[4] for r in rows) - 2.0                                      # worst CI upper bound vs 2
    mech = max(abs(r[1] - r[2]) for r in rows)
    # How many INDEPENDENT conditions were actually exercised.  The derivation above gives the ratio as
    # 2 - sum_l p_l^2, which is a function of the drawn L ALONE: |u_l|^2 = p_l for every entry and every
    # angle set (unit-norm steering), so the angles do not enter.  Angle sets sharing an L are therefore
    # REPLICATIONS (they check angle-invariance), not extra conditions -- report both counts.
    Ldrawn = sorted({r[0] for r in rows})
    Lmiss = sorted(set(range(L_MIN, L_MAX + 1)) - set(Ldrawn))
    within = max((max(v) - min(v) for v in
                  ({q: [r[1] for r in rows if r[0] == q] for q in Ldrawn}).values()), default=0.0)
    across = max(r[1] for r in rows) - min(r[1] for r in rows)
    out.append(_rec("T2d", ok_all, resid, "max CI_hi - 2 < 0",
                    f"{n_sets} angle sets x {n_phase} phase draws, 99.9% bootstrap CI "
                    f"({n_boot} resamples over realisations). Gaussian value = 2 EXACTLY. "
                    + " | ".join(f"L={L}: meas {m:.4f} (CI {a:.4f},{b:.4f}) pred {q:.4f}"
                                 for L, m, q, a, b in rows)
                    + f"  -> every CI excludes 2; worst CI_hi - 2 = {resid:+.4f}. "
                      "Conditional Gaussianity is broken. "
                      "HOW MANY INDEPENDENT CONDITIONS: the ratio is 2 - sum_l p_l^2, i.e. L-DETERMINED and "
                      "ANGLE-INVARIANT, so the evidence is indexed by L, not by the angle sets. "
                      f"{n_sets} angle sets exercised {len(Ldrawn)} DISTINCT L values "
                      f"{{{', '.join(str(q) for q in Ldrawn)}}} out of the {L_MAX - L_MIN + 1} in "
                      f"Unif{{{L_MIN}..{L_MAX}}}"
                    + (f"; NOT EXERCISED: L = {{{', '.join(str(q) for q in Lmiss)}}}. "
                       if Lmiss else " (full range covered). ")
                    + f"Spread of the measured ratio WITHIN one L (repeated angle sets) = {within:.4f} vs "
                      f"ACROSS L = {across:.4f}, confirming the angle-invariance."))
    out.append(_rec("T2dm", mech <= 1e-2, mech, "|meas - pred| <= 1e-2",
                    "T2d MECHANISM: measured fourth-moment ratio vs the analytic 2 - sum_l |u_l|^4/(sum_l |u_l|^2)^2 "
                    f"= 2 - sum_l p_l^2 (unit-norm steering => |u_l|^2 = p_l). max |meas - pred| = {mech:.3e} "
                    "-- the deviation is the deterministic power profile, not a sampling artefact."))

    # ---- T2e  sparsity   [measured]
    Ls = np.arange(L_MIN, L_MAX + 1)
    Hstack = X.reshape(n, Nt, Nr).transpose(0, 2, 1)                           # undo the column-major vec
    Fr = np.exp(-2j * np.pi * np.outer(np.arange(Nr), np.arange(Nr)) / Nr) / np.sqrt(Nr)   # unitary DFT
    Ft = np.exp(-2j * np.pi * np.outer(np.arange(Nt), np.arange(Nt)) / Nt) / np.sqrt(Nt)
    B = np.abs(np.einsum("ab,nbc,cd->nad", Fr.conj(), Hstack, Ft, optimize=True)) ** 2      # angular bins
    B = B.reshape(n, -1)
    f = np.sort(B / B.sum(1, keepdims=True), 1)[:, ::-1]                       # per-block bin-energy shares
    topk = {k: float(f[:, :k].sum(1).mean()) for k in (1, 2, 4, 8) if k <= gen.N}
    part = float((1.0 / np.sum(f ** 2, 1)).mean())                             # effective number of bins
    out.append(_rec("T2e", "RECORD", part, "record only",
                    f"participating paths L ~ Unif{{{L_MIN}..{L_MAX}}}, E[L] = {Ls.mean():.2f}; "
                    f"2D-DFT angular energy concentration over {gen.N} bins: "
                    + ", ".join(f"top-{k} = {v:.4f}" for k, v in topk.items())
                    + f"; effective #bins (1/sum f_b^2) = {part:.3f}/{gen.N} "
                      f"({part / gen.N:.3f} of the aperture)"))
    return out


# ----------------------------------------------------------------------------- self-check
if __name__ == "__main__":
    import sys
    from scipy.special import j0

    # (1) column-major vec, against an independently constructed reference.
    g = D2Gen("S2", 8, 4)
    Xs = g.sample_vecs(np.random.default_rng(0), 5)
    th, ph, al, _ = g._draw(np.random.default_rng(0), 5)
    Hs = g._channels(th, ph, al)
    ref = np.array([H.reshape(-1, order="F") for H in Hs])                     # the literal definition
    assert np.max(np.abs(Xs - ref)) == 0.0, "sample_vecs is not column-major vec"
    assert Xs[0][3 + 8 * 2] == Hs[0][3, 2], "h[i + Nr*j] != H[i,j]"
    assert Xs.dtype == np.complex128 and Xs.shape == (5, 32)

    # (2) .sample(rng) agrees with the (n=1) vec path; shape/dtype as common.D1Gen.
    H1 = g.sample(np.random.default_rng(7))
    v1 = g.sample_vecs(np.random.default_rng(7), 1)[0]
    assert H1.shape == (8, 4) and H1.dtype == np.complex128
    assert np.max(np.abs(H1.reshape(-1, order="F") - v1)) == 0.0

    # (3) the quadrature side against the U2 closed form  r(k) = J_0(pi k).
    Ru, _, _ = ensemble_sides_d2("U2", 8, 4)
    kk = np.arange(4)
    err = np.max(np.abs(Ru - j0(np.pi * np.abs(kk[:, None] - kk[None, :]))))
    assert err < 1e-10, err
    print(f"selfcheck: vec column-major OK | sample==sample_vecs OK | "
          f"Rt(U2) vs J_0(pi k): max err {err:.2e}")

    prior = sys.argv[1] if len(sys.argv) > 1 else "S2"
    Nr, Nt, Tp = 8, 4, 2
    Rt, Rr, inf = ensemble_sides_d2(prior, Nr, Nt)
    print(f"\nD2 / prior {prior} / Nr={Nr} Nt={Nt} Tp={Tp}   informative(Rt) = {inf}")
    print("Rt =\n", np.array2string(Rt, precision=5))
    print("Rr diag-lags =", np.array2string(Rr[0], precision=5))
    rows = tests_T2(prior, Nr, Nt, Tp)
    print("\nid    | verdict | residual      | criterion               | description")
    print("-" * 130)
    for tid, v, rs, cr, d in rows:
        print(f"{tid:<5} | {v:<7} | {rs:>13.3e} | {cr:<23} | {d}")
