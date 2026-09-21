"""conf/code/common.py — shared setup for the conference run (conf/06_SPEC_runner.md §2, §3).

Demo/ is READ-ONLY here: t2_route_a.py / t2_trellis.py / t2_gmm.py are imported, never modified
(conf/01_RULES.md §2; test C3 hashes them before and after).

Testbeds
  D1  grid-GMM prior  = t2_gmm.angle_grid_prior(kind, Nr, Nt, RHO_C, KG)  -- the exp_0925 "true" prior.
      CIRCULAR: the true prior IS a 32x32-component grid mixture, so the GMM arm is correctly specified
      and the exact score exists in closed form. Used as the INSTRUMENT (quality gates), never for a claim.
  D2  sparse specular multipath (conf/code/d2.py) -- the claim testbed.

Seeds (conf/01_RULES.md §4: keep the existing convention, change only the experiment number).
  SEED = 20260926.  Trials of one point come from ONE stream
      default_rng([SEED, TBID[testbed], PID[prior], Nr, T, Tp, int(snr) + 100])
  so a task = (point, skip, chunk) regenerates the skipped trials and every arm at a point sees the
  same (H, u, perm, Y) -> paired within a cell (conf/01_RULES.md §5, test C4).
  Training set of a testbed: see arms.py (D1 inherits exp_0925's [20260925, 7, prior_id, Nr]).
"""
import os, sys, hashlib, subprocess, time

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")                                    # one BLAS thread per worker

import numpy as np

CONF = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))    # .../t2/conf
REPO = os.path.dirname(CONF)
DEMO = os.path.join(REPO, "Demo")
ARCHIVE = os.path.join(DEMO, "archive")
for _p in (DEMO, os.path.join(CONF, "code")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from t2_trellis import qam_constellation                              # noqa: E402
from t2_route_a import QAMCode, dft_pilots, GaussianPrior, RouteA     # noqa: E402
from t2_gmm import angle_grid_prior, ensemble_sides, GMMPriorB, RouteAClip   # noqa: E402

# ----------------------------------------------------------------------------- fixed configuration (06_SPEC_runner.md §2)
GENS, NU = ("133", "171"), 6                  # rate-1/2 convolutional, terminated, BCJR
M_QAM = 2                                     # QPSK
NT = 4                                        # transmit antennas (all cells)
N_ITER = 16                                   # outer iterations, ALL arms
RHO_C, KG = 0.7, 32                           # D1 grid prior: per-component correlation, grid size
N_TRAIN = 10000                               # channel dataset for GMM fit AND diffusion training (identical samples)
SEED = 20260926
BETA = 0.7                                    # damping, v1 configuration
T_IN = 5                                      # BiG-AMP inner iterations (01_RULES §4 fallback)
LAM_MIN = 1e-6                                # EP site eigenvalue floor
EPS_CLIP = 1e-6                               # alpha clip range [eps, 1-eps]  (02_SPEC §2.2(a))
VAR_FLOOR = 1e-12                             # variance floor  (01_RULES §4 fallback)

CELLS = {                                     # 06_SPEC_runner.md §3, priority order
    "C1": dict(Nr=8, Nt=4, T=16, Tp=2, snrs=(-3, 0, 3, 6, 9, 12, 15)),   # headline
    "C2": dict(Nr=8, Nt=4, T=16, Tp=4, snrs=(-3, 0, 3, 6, 9, 12, 15)),   # cross-Tp goodput
    "C3": dict(Nr=4, Nt=4, T=28, Tp=2, snrs=(9, 12, 15)),                # sanity
    "C4": dict(Nr=4, Nt=4, T=28, Tp=4, snrs=(3, 6, 9)),                  # sanity
    # C5 fills the pilot-budget REGIME curve between C1 (Tp=2, first pass uninformative -> no prior can
    # work, diagnosed by T2c) and C2 (Tp=4, prior works).  Same array/block as C1/C2 so Tp is the ONLY
    # axis that moves.  Added after T2c's pre-registered diagnosis fired, not after seeing a BLER.
    "C5": dict(Nr=8, Nt=4, T=16, Tp=3, snrs=(-3, 0, 3, 6, 9, 12, 15)),
}
# SNR grids are exp_0925_run.CELLS verbatim: H/H4 (8x4, T=16) -> -3..15 dB, R (4x4, T=28, Tp=2) -> 9/12/15.
# C4 (4x4, Tp=4) has no exp_0925 counterpart -> 01_RULES §4 fallback "Tp=4 -> 0,3,6,9 dB" shifted onto the
# 4x4 grid actually used by exp_0921 A (Tp=4: 0,3,6,9) intersected with exp_0925 R -> 3/6/9 (see DECISIONS).

PID = {"U": 0, "S": 1, "P": 2, "U2": 3, "S2": 4}       # prior id inside the seed
TBID = {"D1": 1, "D2": 2}
PRIOR_OF = {"D1": "S", "D2": "S2"}                     # primary prior per testbed (06_SPEC §2)

KEYS_RAW = ("blk_err", "ber", "nmse", "tauL_gmean", "alphaD", "tauL_clip_frac", "alphaD_clip")
KEYS_LOG = ("nmse", "tauL_mean", "tauL_gmean", "nu_q", "alphaH", "nuE", "hE_norm",
            "alphaD", "ber", "blk_err", "tauL_clip_frac", "alphaD_clip")     # == RouteA.run keys (test C1)

CONST_QPSK, CBITS_QPSK = qam_constellation(M_QAM)


# ----------------------------------------------------------------------------- QPSK bit <-> symbol helpers
def bit_llrs_from_pmf(P, floor=1e-300):
    """(Ns, 4) symbol pmf -> (Ns, 2) bit LLRs  L = log P(b=0)/P(b=1).  Bit 0 = real axis, bit 1 = imaginary axis
    (t2_trellis.qam_constellation(2): x = (s0 + j s1)/sqrt(2), s = 1 - 2b)."""
    P0 = P @ (CBITS_QPSK == 0)
    return np.log(np.maximum(P0, floor)) - np.log(np.maximum(1.0 - P0, floor))


def qpsk_prior(La):
    """(Ns, 2) a-priori bit LLRs -> separable QPSK prior moments (x_bar, v) of  x = (s0 + j s1)/sqrt(2).
    02_SPEC_baselines.md §0:  E[x] = (b0_bar + j b1_bar)/sqrt(2),  Var(x) = [(1-b0_bar^2) + (1-b1_bar^2)]/2."""
    b = np.tanh(0.5 * La)
    return (b[:, 0] + 1j * b[:, 1]) / np.sqrt(2.0), 0.5 * ((1 - b[:, 0] ** 2) + (1 - b[:, 1] ** 2))


def qpsk_posterior(r, nu, La):
    """(R13)(R14) for the separable QPSK prior under r = x + CN(0, nu):  the real and imaginary bits separate.
    LLR update  L_post,0 = La_0 + 2*sqrt(2)*Re(r)/nu   [exact: |r - (+-1/sqrt2 + ...)|^2 expansion, nu per complex entry]."""
    s = 2.0 * np.sqrt(2.0) / np.maximum(nu, VAR_FLOOR)
    t0 = np.tanh(0.5 * (La[..., 0] + s * r.real))
    t1 = np.tanh(0.5 * (La[..., 1] + s * r.imag))
    return (t0 + 1j * t1) / np.sqrt(2.0), 0.5 * ((1 - t0 ** 2) + (1 - t1 ** 2))


# ----------------------------------------------------------------------------- interleaver <-> grid maps
def grid_to_code(A, perm):
    """(Nt, Td) antenna/time grid -> (Ns,) code order.  Same map as t2_route_a.RouteA.run."""
    return A.T.reshape(-1)[perm]


def code_to_grid(v, perm, Nt, Td):
    """(Ns,) code order -> (Nt, Td) grid.  Inverse of grid_to_code."""
    g = np.empty(Nt * Td, dtype=v.dtype)
    g[perm] = v
    return g.reshape(Td, Nt).T


# ----------------------------------------------------------------------------- pilots
def make_pilots(testbed, prior, Nt, Tp, Nr):
    """DFT unless the transmit-side ENSEMBLE covariance is informative; then sqrt(Nt) x top-Tp eigenvectors of
    R_t,ens (the exp_0921/exp_0925 'eig' rule).  Same matrix for every arm inside a cell (06_SPEC §2).
    D2 defers to the measured effective rank (test T2b) through d2.ensemble_sides_d2."""
    if testbed == "D1":
        if prior != "S":
            return "dft", dft_pilots(Nt, Tp)
        Rt, _ = ensemble_sides(prior, Nr, Nt, RHO_C, KG)
    else:
        from d2 import ensemble_sides_d2
        Rt, _, informative = ensemble_sides_d2(prior, Nr, Nt)
        if not informative:
            return "dft", dft_pilots(Nt, Tp)
    w, U = np.linalg.eigh(Rt)
    U = U[:, ::-1]
    U = U * np.exp(-1j * np.angle(U[np.argmax(np.abs(U), 0), np.arange(Nt)]))    # platform-independent phase
    return "eig", np.sqrt(Nt) * U[:, :Tp]


# ----------------------------------------------------------------------------- testbed generators
class D1Gen:
    """D1 = the exp_0925 grid-GMM prior.  .sample(rng) and .prior are the SAME object, so the exact score exists."""
    name = "D1"

    def __init__(self, prior, Nr, Nt):
        self.prior = angle_grid_prior(prior, Nr, Nt, RHO_C, KG)
        self.Nr, self.Nt, self.N = Nr, Nt, Nr * Nt
        self.kind = prior

    def sample(self, rng):
        return self.prior.sample(rng)

    def sample_vecs(self, rng, n):
        return self.prior.sample_vecs(rng, n)[0]


def make_gen(testbed, prior, Nr, Nt):
    if testbed == "D1":
        return D1Gen(prior, Nr, Nt)
    from d2 import D2Gen
    return D2Gen(prior, Nr, Nt)


def trial_rng(testbed, prior, Nr, T, Tp, snr):
    return np.random.default_rng([SEED, TBID[testbed], PID[prior], Nr, T, Tp, int(snr) + 100])


def train_rng(testbed, prior, Nr, which):
    """which: 7 = training set, 8 = GMM validation set, 10 = held-out test set (reporting / gates).
    D1 reuses exp_0925's streams verbatim so the GMM fits in Demo/exp_0925_fits/ stay valid (test M1)."""
    if testbed == "D1":
        return np.random.default_rng([20260925, which, PID[prior], Nr])
    return np.random.default_rng([SEED, TBID[testbed], which, PID[prior], Nr])


# ----------------------------------------------------------------------------- reproducibility header
def file_sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


DEMO_LOCKED = ("t2_route_a.py", "t2_trellis.py", "t2_gmm.py")


def demo_hashes():
    return {f: file_sha(os.path.join(DEMO, f)) for f in DEMO_LOCKED}


def git_commit():
    try:
        return subprocess.run(["git", "-C", REPO, "rev-parse", "--short", "HEAD"],
                              capture_output=True, text=True, timeout=20).stdout.strip() or "?"
    except Exception:
        return "?"


def header(testbed, extra=()):
    import scipy
    try:
        import torch
        tv = f"torch {torch.__version__} (cuda_available={torch.cuda.is_available()})"
    except Exception:
        tv = "torch n/a"
    lines = [
        f"date        : {time.strftime('%Y-%m-%d %H:%M:%S %Z')}",
        f"git commit  : {git_commit()}",
        f"versions    : python {sys.version.split()[0]}  numpy {np.__version__}  scipy {scipy.__version__}  {tv}",
        f"device      : CPU ({os.cpu_count()} cores) | dtype: complex128 / float64 | deterministic: yes (fixed seeds, no GPU in the receiver)",
        f"testbed     : {testbed}",
        f"seed rule   : default_rng([{SEED}, TBID[testbed], PID[prior], Nr, T, Tp, int(snr)+100])  (trials of a point = ONE stream)",
        f"code        : rate-1/2 conv ({GENS[0]},{GENS[1]})_8 nu={NU} terminated, QPSK, outer iterations = {N_ITER} for EVERY arm",
        "Demo/ hashes: " + "  ".join(f"{k}={v}" for k, v in demo_hashes().items()),
    ]
    lines += list(extra)
    return "\n".join("# " + l for l in lines)


D1_WARNING = (
    "# " + "!" * 100 + "\n"
    "# CIRCULAR TESTBED -- true prior is defined as a grid GMM; the GMM arm is correctly specified.\n"
    "# No claim about learned priors can be made from this table.\n"
    "# " + "!" * 100
)

D2_WARNING = (
    "# " + "=" * 100 + "\n"
    "# CLAIM TESTBED -- sparse specular; conditional Gaussianity broken (see T2d). Upper bound = genie only.\n"
    "# " + "=" * 100
)

ARM_NOTES = {
    "R3-bigamp": "BiG-AMP prior: i.i.d. CN(0,1/Nr) -- correlated prior not supported by Table III (structural limitation)",
    "R4-scvamp": "channel estimation = classical APP-LMMSE (no LOO); only the Onsager extrinsic interface follows arXiv:2604.19061",
    "R4-llr":    "same, Module B mode='llr' (the paper's 'LLR Turbo' ablation)",
    "M-ours-score": ("ORACLE arm -- exact score of the TRUE prior, NOT a learned diffusion prior. "
                     "No claim of 'learned channel prior gain' can be made from this arm."),
}
