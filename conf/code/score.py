"""conf/code/score.py -- A5 / B3: the score-model ladder L1..L6, its training regime and the
pre-registered quality gates GA-GD (conf/04_SPEC_diffusion.md, whole document).

What is in here
  RUNGS / DEFAULT_HP / ATTEMPT_HP   the ladder of 04_SPEC §4 and the <= 3 retries per rung (§4 "칸마다의 재시도").
  make_model(rung, hp, Nr, Nt)      one torch.nn.Module per rung; every one exposes the SAME three methods
                                    score_real / denoise_real / loss, so the trainer, the gates and the
                                    receiver adapter are written once.
  train(...)                        the training regime of 04_SPEC §2: identical N_train=1e4 samples as the
                                    GMM fit, fixed 9:1 split, MEASURED sigma grid, deterministic validation
                                    loss, patience 20 / min 200 epochs, per-epoch checkpoint + log.
  ScorePrior                        duck-types t2_route_a.GMMPrior so arms.route_a(..., "score") can use a
                                    trained network as Module H through the SAME D-13 + D-14 interface as
                                    the oracle arm M-ours-score (04_SPEC §1).
  gates_D1 / gb_prime               §5 gates (D1 only, exact score available) and the §6 report-only GB'.
  load_prior                        the runner-side factory of M-ours-dscore: the GATE-PASSING checkpoint
                                    wrapped as a ScorePrior, or None (reason in score.last_reason).
  ladder_append                     the append-only attempt log of §4.
  selftest_M5 / selftest_gates      the two mandatory self-tests (see __main__).

HOW TO READ GA AND GD (both decided before any checkpoint was gated -- conf/DECISIONS.md 2026-09-20 12:35)
  GA is identically zero BY CONSTRUCTION for this model family: every parameterisation reduces
  x + sigma^2 * score_real to the native x0 head, so GA guards an INCONSISTENCY between the score path
  and the x0 path only -- it cannot catch an error shared by both, and a PASS therefore rests on GB/GC/GD.
  GD is the relative Frobenius error of the FULL Wirtinger matrix J (04_SPEC §5 "the Jacobian/divergence
  estimate that D-14 uses"; RouteAClip._matrix_site consumes SigH = nu*J, not its trace).  The old scalar
  quantity, the relative error of tr(J)/N, is KEPT and REPORTED as GD_trace but is NOT the gate.

THE CONVENTIONS (fixed by the project; implemented here, not re-derived)
  h = vec(H) COLUMN-MAJOR, h[i + Nr*j] = H[i,j].                                            [exact]
  The receiver hands Module H  q = h + e,  e ~ CN(0, nu I_N),  nu = PER-COMPLEX-ENTRY variance.
  The network lives in the real 2-channel domain  x = [Re(h), Im(h)] in R^{2N}, where each real
  dimension carries nu/2, hence
        sigma_t = sqrt(nu / 2)                          <- NU_TO_SIGMA; the whole file hangs on this line.
  Real Tweedie:      E[x|x_q]_real = x_q + sigma_t^2 * grad_{x_q} log p(x_q).                [exact]
  Complex Wirtinger: E[h|q]        = q   + nu * d/dq* log p(q),  d/dq* = (d/dRe + j d/dIm)/2. [exact]
  The two agree because  s_real = 2 * [Re(s_c), Im(s_c)]  and  sigma_t^2 * 2 = nu.  This is the
  convention test T4 of Demo/archive/exp_0915_bcjr_score_check.py verifies to 1e-10; selftest_M5
  re-verifies the channel-side version of it against GMMPriorB to 1e-8.                      [measured]
  Wirtinger Jacobian consumed by the D-14 matrix site, from the 2N x 2N REAL Jacobian of the real
  denoiser map (blocks A = dm_r/dq_r, B = dm_r/dq_i, Cc = dm_i/dq_r, D = dm_i/dq_i):
        J = 0.5 * [ (A + D) + 1j * (Cc - B) ]                                                [exact]
  For an exact MMSE denoiser J = Cov[h|q]/nu (2nd-order Tweedie) = what GMMPriorB.denoise_full returns.
  Receiver dtype is complex128 / float64 (01_RULES §9.3); training is float32 on GPU (§9.5).
"""
import hashlib
import zlib
import math
import os
import re
import time

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

import common as C
import arms as A
import sigma as SG

# ----------------------------------------------------------------------------- noise-level conventions
def NU_TO_SIGMA(nu):
    """per-complex-entry cavity variance -> per-real-dimension noise std."""
    return np.sqrt(np.asarray(nu, float) / 2.0)


def SIGMA_TO_NU(sigma):
    return 2.0 * np.asarray(sigma, float) ** 2


def SIGMA_TO_NU_T(sigma):
    """The same map for a torch tensor (np.asarray would detach it from the autograd graph)."""
    return 2.0 * sigma ** 2


SEED_SPLIT, SEED_VAL, SEED_TRAIN, SEED_GATE, SEED_VAE = 20260926, 20260927, 20260928, 20260929, 20260930
VAL_FRAC = 0.1                      # 04_SPEC §2: 9:1, the SAME split for every rung and attempt
CKPT_DIR = os.path.join(C.CONF, "ckpt")
LOG_DIR = os.path.join(C.CONF, "logs")
LADDER = os.path.join(C.CONF, "LADDER.md")
GATE_TOL = dict(GA=1e-6, GB=0.05, GC=0.15, GD=0.20)          # 04_SPEC §5, frozen before any BLER is seen
# GD_trace deliberately has NO entry here: it is reported, never gated (conf/DECISIONS.md 2026-09-20 12:35).

# Attached to EVERY place GA is reported, so that "GA 1e-17 PASS" is never read as evidence that the
# score -> x0 conversion was validated on the trained model.  See the GA computation site in gates_D1().
GA_NOTE = ("GA is identically zero by construction for this model family; it guards score-path vs x0-path "
           "inconsistency only, and PASS therefore rests on GB/GC/GD.")

RUNGS = ("L1", "L2", "L3", "L4", "L4u", "L5", "L6",
         "L7", "L8", "L9", "L10")   # L4u/L7..L10 = user-directed extensions (DECISIONS)


# ----------------------------------------------------------------------------- hyper-parameters (04_SPEC §4)
# param : 've' = VE/DSM eps-prediction, 'vp' = VP/DDPM eps-prediction, 'rf' = rectified flow, 'vae'.
# domain: 'pixel' = H as it is, 'angle' = unitary 2D DFT across the (Nr, Nt) array axes.
# 'auto' is resolved by resolve_hp() from the GATE SCORE of the earlier rungs -- never from BLER (01_RULES §5).
DEFAULT_HP = {
    "L1": dict(arch="mlp",  param="ve", domain="pixel", width=256, depth=4, emb=128, lr=2e-4, ema=0.999, batch=256),
    "L2": dict(arch="mlp",  param="vp", domain="pixel", width=256, depth=4, emb=128, lr=2e-4, ema=0.999, batch=256),
    "L3": dict(arch="mlp",  param="auto", domain="angle", base="auto", width=256, depth=4, emb=128, lr=2e-4, ema=0.999, batch=256),
    "L4": dict(arch="conv", param="auto", domain="auto", base="auto", width=64, depth=4, emb=128, lr=2e-4, ema=0.999, batch=256),
    # L5 = flow matching on "the configuration that won at L3/L4" (04_SPEC §4), so BOTH the architecture and
    # the domain are inherited from the gate-score winner; 'rf' is the one axis L5 is there to vary.
    "L5": dict(arch="auto", param="rf", domain="auto", base="auto", width=256, depth=4, emb=128, lr=2e-4, ema=0.999, batch=256),
    # L4u: 04_SPEC §4 names TWO architectures for L4, "2D conv / 소형 U-Net".  L4 ran the flat conv stack;
    # L4u runs the U-Net.  param/domain are PINNED to L4's resolved values (vp / pixel) rather than 'auto',
    # so the ONLY difference from L4 is the architecture and the comparison is a clean one-axis ablation.
    "L4u": dict(arch="unet", param="vp", domain="pixel", width=64, depth=4, emb=128, lr=2e-4, ema=0.999,
                batch=256),
    "L6": dict(arch="vae",  param="vae", domain="pixel", width=256, depth=3, emb=0, latent=16, n_mix=512,
               lr=1e-3, ema=0.999, batch=256),
    # ---- extension rungs (user-directed, conf/DECISIONS.md 2026-09-20 14:15).  Gates are UNCHANGED.
    # Each pins param/domain to L4's resolved values so exactly ONE axis differs from L4 a1.
    "L7": dict(arch="conv", param="edm", domain="pixel", width=64, depth=4, emb=128, lr=2e-4, ema=0.999,
               batch=256),                                    # EDM preconditioning, L4's architecture
    "L8": dict(arch="dit",  param="vp",  domain="pixel", width=128, depth=4, emb=128, lr=2e-4, ema=0.999,
               batch=256, patch=1, heads=4),                  # DiT, adaLN-Zero
    "L9": dict(arch="uvit", param="vp",  domain="pixel", width=128, depth=5, emb=128, lr=2e-4, ema=0.999,
               batch=256, patch=1, heads=4),                  # U-ViT, long skips (depth ODD on purpose)
    "L10": dict(arch="adm", param="vp",  domain="pixel", width=64, depth=4, emb=128, lr=2e-4, ema=0.999,
                batch=256, heads=4, attn_at=8),               # ADM, adaGN + coarse-scale attention
}
# The <= 3 attempts per rung.  ONLY lr / width / depth / EMA may move (04_SPEC §4); the axis the rung is
# supposed to test (parameterisation, domain, architecture) is never touched by a retry.
ATTEMPT_HP = {
    ("L1", 2): dict(lr=1e-3, ema=0.9995),   ("L1", 3): dict(width=512, depth=6, lr=3e-4),
    ("L2", 2): dict(lr=1e-3, ema=0.9995),   ("L2", 3): dict(width=512, depth=6, lr=3e-4),
    ("L3", 2): dict(lr=1e-3, ema=0.9995),   ("L3", 3): dict(width=512, depth=6, lr=3e-4),
    ("L4", 2): dict(lr=1e-3, ema=0.9995),   ("L4", 3): dict(width=96, depth=6, lr=3e-4),
    # L4u a2 goes DOWN in width, not just in lr: at the same `width` the U-Net carries ~13x the parameters
    # of L4's flat stack (4.19M vs 310k) because of the channel doubling per scale, and 9000 training
    # samples is the budget.  a3 mirrors L4 a3 so the two architectures are compared on the same schedule.
    ("L4u", 2): dict(width=32, lr=1e-3, ema=0.9995),
    ("L4u", 3): dict(width=96, depth=6, lr=3e-4),
    ("L5", 2): dict(lr=1e-3, ema=0.9995),   ("L5", 3): dict(width=512, depth=6, lr=3e-4),
    ("L6", 2): dict(lr=3e-4, ema=0.9995),   ("L6", 3): dict(width=512, depth=4, lr=1e-3),
    ("L7", 2): dict(lr=1e-3, ema=0.9995),   ("L7", 3): dict(width=96, depth=6, lr=3e-4),
    ("L8", 2): dict(lr=1e-3, ema=0.9995),   ("L8", 3): dict(width=64, depth=6, lr=3e-4),
    ("L9", 2): dict(lr=1e-3, ema=0.9995),   ("L9", 3): dict(width=64, depth=7, lr=3e-4),
    ("L10", 2): dict(lr=1e-3, ema=0.9995),  ("L10", 3): dict(width=32, depth=6, lr=3e-4),
}
MAX_ATTEMPTS = 3


def _rung_ix(rung):
    """Stable integer for a rung label.  Ladder rungs keep their positional index (so their seeds are
    unchanged); anything else -- e.g. a hyper-parameter search passing its own label -- gets a stable
    hash instead of a ValueError."""
    return RUNGS.index(rung) if rung in RUNGS else 1000 + zlib.crc32(rung.encode()) % 1000


def hp_for(rung, attempt):
    """DEFAULT_HP overridden by the retry recipe.  Attempt 1 = the default configuration."""
    assert rung in RUNGS and 1 <= attempt <= MAX_ATTEMPTS, f"{rung} attempt {attempt}"
    return dict(DEFAULT_HP[rung], **ATTEMPT_HP.get((rung, attempt), {}))


# ----------------------------------------------------------------------------- real <-> complex packing
def _unpack(x):
    """(..., 2N) real -> (..., N) complex.  x = [Re(h), Im(h)]."""
    n = x.shape[-1] // 2
    return torch.complex(x[..., :n], x[..., n:])


def _pack(z):
    return torch.cat([z.real, z.imag], -1)


def np_pack(z):
    return np.concatenate([z.real, z.imag], -1)


def np_unpack(x):
    n = x.shape[-1] // 2
    return x[..., :n] + 1j * x[..., n:]


# ----------------------------------------------------------------------------- backbones
class _TimeEmb(nn.Module):
    """Fourier embedding of log(sigma_t) (04_SPEC §4, L1).  log-sigma because the grid is log-equispaced."""

    def __init__(self, dim, n_freq=None):
        super().__init__()
        k = dim // 2 if n_freq is None else n_freq
        self.register_buffer("w", torch.exp(torch.linspace(math.log(0.5), math.log(50.0), k)))
        self.dim = 2 * k

    def forward(self, logsig):
        a = logsig.unsqueeze(-1) * self.w
        return torch.cat([torch.sin(a), torch.cos(a)], -1)


class _MLP(nn.Module):
    """Noise-conditional residual MLP.  Input/output = the 2N reals of the working domain."""

    def __init__(self, dim, width, depth, emb):
        super().__init__()
        self.temb = _TimeEmb(emb)
        self.cond = nn.Sequential(nn.Linear(self.temb.dim, width), nn.SiLU(), nn.Linear(width, width))
        self.inp = nn.Linear(dim, width)
        self.blocks = nn.ModuleList(
            nn.Sequential(nn.SiLU(), nn.Linear(width, width), nn.SiLU(), nn.Linear(width, width))
            for _ in range(depth))
        self.out = nn.Linear(width, dim)
        nn.init.zeros_(self.out.weight); nn.init.zeros_(self.out.bias)   # start at eps_hat = 0 (a finite loss at t=0)

    def forward(self, x, logsig):
        h = self.inp(x) + self.cond(self.temb(logsig))
        for b in self.blocks:
            h = h + b(h)
        return self.out(h)


class _Conv(nn.Module):
    """2D conv stack over the (Nr, Nt) array grid, 2 channels (04_SPEC §4, L4).  Nt = 4 and Nr <= 8, so a
    U-Net would down-sample a 4-wide axis to nothing: depth is spent on channels, not on scales.
    padding_mode: 'circular' in the ANGLE domain (DFT bins wrap) and 'zeros' in the pixel domain
    (a ULA aperture does not wrap)."""

    def __init__(self, Nr, Nt, width, depth, emb, circular):
        super().__init__()
        self.Nr, self.Nt = Nr, Nt
        pm = "circular" if circular else "zeros"
        self.temb = _TimeEmb(emb)
        self.cond = nn.Sequential(nn.Linear(self.temb.dim, width), nn.SiLU(), nn.Linear(width, width))
        self.inp = nn.Conv2d(2, width, 3, padding=1, padding_mode=pm)
        self.blocks = nn.ModuleList(
            nn.Sequential(nn.SiLU(), nn.Conv2d(width, width, 3, padding=1, padding_mode=pm),
                          nn.SiLU(), nn.Conv2d(width, width, 3, padding=1, padding_mode=pm))
            for _ in range(depth))
        self.out = nn.Conv2d(width, 2, 3, padding=1, padding_mode=pm)
        nn.init.zeros_(self.out.weight); nn.init.zeros_(self.out.bias)

    def forward(self, x, logsig):
        lead = x.shape[:-1]
        # column-major vec: h[i + Nr*j] = H[i,j]  ->  reshape (Nt, Nr) in C order, then transpose.
        y = x.reshape(*lead, 2, self.Nt, self.Nr).transpose(-1, -2)
        h = self.inp(y) + self.cond(self.temb(logsig)).reshape(*lead, -1, 1, 1)
        for b in self.blocks:
            h = h + b(h)
        return self.out(h).transpose(-1, -2).reshape(*lead, 2 * self.Nr * self.Nt)


def _gn(c):
    """GroupNorm with the largest group count that divides c (<= 8)."""
    g = 8
    while c % g:
        g //= 2
    return nn.GroupNorm(g, c)


class _ResBlk(nn.Module):
    """Pre-norm residual block with the log-sigma embedding injected between the two convolutions."""

    def __init__(self, cin, cout, tdim, pm):
        super().__init__()
        self.n1, self.c1 = _gn(cin), nn.Conv2d(cin, cout, 3, padding=1, padding_mode=pm)
        self.emb = nn.Linear(tdim, cout)
        self.n2, self.c2 = _gn(cout), nn.Conv2d(cout, cout, 3, padding=1, padding_mode=pm)
        self.skip = nn.Conv2d(cin, cout, 1) if cin != cout else nn.Identity()

    def forward(self, x, t):
        h = self.c1(F.silu(self.n1(x)))
        h = h + self.emb(t).reshape(*t.shape[:-1], -1, 1, 1)
        h = self.c2(F.silu(self.n2(h)))
        return h + self.skip(x)


class _UNet(nn.Module):
    """Small 2D U-Net over the (Nr, Nt) array grid -- the SECOND architecture 04_SPEC §4 names for L4
    ("2D conv / 소형 U-Net").  The flat stack _Conv implements the first; this implements the second, so the
    two can be compared under the same frozen gates with the architecture as the only difference.

    The objection _Conv's docstring raises is real -- Nt = 4, so a deep U-Net would shrink the transmit axis
    to nothing -- and it is handled by CHOOSING the number of scales from the grid rather than fixing it:
        n_down = min(2, floor(log2(min(Nr, Nt))))
    which gives 8x4 -> 4x2 -> 2x1 for the headline cell and 4x4 -> 2x2 -> 1x1 for the 4x4 cells.  Two
    down-samplings is what a 4-wide axis supports; the bottleneck still carries a full feature vector per
    position.  Skip connections concatenate the encoder map at each scale, which is the part a flat stack
    cannot emulate: it lets the fine scale keep array-element detail while the coarse scale carries the
    aperture-wide correlation that the Kronecker structure of this prior actually lives in.

    padding_mode follows _Conv: 'circular' in the ANGLE domain (DFT bins wrap), 'zeros' in pixel."""

    def __init__(self, Nr, Nt, width, depth, emb, circular):
        super().__init__()
        self.Nr, self.Nt = Nr, Nt
        pm = "circular" if circular else "zeros"
        self.temb = _TimeEmb(emb)
        tdim = 4 * width
        self.tproj = nn.Sequential(nn.Linear(self.temb.dim, tdim), nn.SiLU(), nn.Linear(tdim, tdim))
        n_down = min(2, int(math.log2(min(Nr, Nt))))
        chs = [width * (2 ** min(i, 2)) for i in range(n_down + 1)]
        per = max(1, depth // max(n_down + 1, 1))               # residual blocks per scale
        self.inp = nn.Conv2d(2, chs[0], 3, padding=1, padding_mode=pm)
        self.enc, self.down = nn.ModuleList(), nn.ModuleList()
        for i in range(n_down):
            self.enc.append(nn.ModuleList(_ResBlk(chs[i], chs[i], tdim, pm) for _ in range(per)))
            self.down.append(nn.Conv2d(chs[i], chs[i + 1], 3, stride=2, padding=1, padding_mode=pm))
        self.mid = nn.ModuleList(_ResBlk(chs[-1], chs[-1], tdim, pm) for _ in range(max(2, per)))
        self.up, self.dec = nn.ModuleList(), nn.ModuleList()
        for i in reversed(range(n_down)):
            self.up.append(nn.ConvTranspose2d(chs[i + 1], chs[i], 2, stride=2))
            self.dec.append(nn.ModuleList([_ResBlk(2 * chs[i], chs[i], tdim, pm)]
                                          + [_ResBlk(chs[i], chs[i], tdim, pm) for _ in range(per - 1)]))
        self.outn = _gn(chs[0])
        self.out = nn.Conv2d(chs[0], 2, 3, padding=1, padding_mode=pm)
        nn.init.zeros_(self.out.weight)
        nn.init.zeros_(self.out.bias)

    def forward(self, x, logsig):
        lead = x.shape[:-1]
        # identical layout to _Conv: column-major vec h[i + Nr*j] = H[i,j]
        y = x.reshape(*lead, 2, self.Nt, self.Nr).transpose(-1, -2)
        # FLATTEN every leading dim into ONE batch axis before the normalised blocks.  _Conv can skip this
        # because Conv2d accepts an unbatched (C, H, W); GroupNorm CANNOT -- with a 3-D input it reads dim 0
        # as the batch and dim 1 as the channels.  The gate's Jacobian path calls the model with lead = ()
        # (torch.func.jacrev on a single sample), so without this the whole gate stage dies.
        y = y.reshape(-1, 2, self.Nr, self.Nt)
        t = self.tproj(self.temb(logsig)).reshape(y.shape[0], -1)
        h = self.inp(y)
        skips = []
        for blks, dn in zip(self.enc, self.down):
            for b in blks:
                h = b(h, t)
            skips.append(h)
            h = dn(h)
        for b in self.mid:
            h = b(h, t)
        for u, blks in zip(self.up, self.dec):
            h = u(h)
            h = torch.cat([h, skips.pop()], dim=-3)
            for b in blks:
                h = b(h, t)
        h = self.out(F.silu(self.outn(h)))
        h = h.reshape(*lead, 2, self.Nr, self.Nt)
        return h.transpose(-1, -2).reshape(*lead, 2 * self.Nr * self.Nt)


def dft_domain_matrix(Nr, Nt):
    """Real 2N x 2N orthogonal embedding of the unitary spatial 2D DFT  H_a = F_r^H H F_t, i.e.
    h_a = W h with W = kron(F_t^T, F_r^H) (column-major vec).  W is unitary (Kronecker of unitaries), so its
    real embedding M = [[Re W, -Im W], [Im W, Re W]] is ORTHOGONAL.  That is the whole legitimacy of L3:
    an orthogonal map sends N(0, sigma^2 I) to N(0, sigma^2 I), so the DSM problem at level sigma is the
    same problem in both domains, the noise target transforms as a vector (eps_a = M eps), and therefore
        s_pixel = M^T s_angle = F^H s_angle        [exact, no approximation, no Jacobian correction]."""
    F = lambda n: np.exp(-2j * np.pi * np.outer(np.arange(n), np.arange(n)) / n) / np.sqrt(n)
    W = np.kron(F(Nt).T, F(Nr).conj().T)
    return np.block([[W.real, -W.imag], [W.imag, W.real]])


# ----------------------------------------------------------------------------- the ladder models
class ScoreModel(nn.Module):
    """Rungs L1-L5.  ONE class, four parameterisations -- because 04_SPEC §1 fixes the receiver interface and
    lets only the score model change.  Every parameterisation implements TWO SEPARATE code paths:

      score_real(x, sigma)   the VE score of the pixel-domain real vector, grad_x log p_sigma(x)
      denoise_real(x, sigma) the model's OWN NATIVE denoiser (x0-head), NOT routed through the score

    and gate GA measures the distance between  x + sigma^2 * score_real  and  denoise_real.  For 've' the two
    expressions are identical by construction (GA = 0 exactly); for 'vp' and 'rf' they are two different
    formulas that agree only if the VE<->VP / flow<->score conversions are right, which is what GA is for."""

    def __init__(self, net, param, Nr, Nt, M=None):
        super().__init__()
        assert param in ("ve", "vp", "rf", "edm")
        self.net, self.param, self.Nr, self.Nt, self.N = net, param, Nr, Nt, Nr * Nt
        # M is a CONSTANT, not a parameter: non-persistent (never in the state_dict) and carried at the
        # module's current dtype -- float32 while training, float64 in the receiver (01_RULES §9.5 / §9.3).
        self.register_buffer("M", torch.zeros(0) if M is None else
                             torch.as_tensor(M, dtype=torch.get_default_dtype()), persistent=False)

    def refresh_M(self):
        """Recompute the exact orthogonal transform at the module's CURRENT dtype, so that a float32 training
        run and a float64 inference run each get an exactly orthogonal M rather than an up-cast of the other."""
        if self.M.numel():
            self.M.copy_(torch.as_tensor(dft_domain_matrix(self.Nr, self.Nt), dtype=self.M.dtype))
        return self

    # -- working-domain wrapper: x_work = M x_pixel, and any vector-valued output comes back as M^T y_work.
    def raw(self, x, logsig):
        if self.M.numel() == 0:
            return self.net(x, logsig)
        return self.net(x @ self.M.T, logsig) @ self.M

    # -- VE <-> VP conversion, written out because L2 is the rung that tests it (04_SPEC §4).
    #    abar = 1/(1+sigma^2);  q_vp = sqrt(abar) q_ve  (then sqrt(1-abar) = sigma sqrt(abar) matches the VP noise);
    #    score_vp(u) = -eps_hat/sqrt(1-abar);  score_ve(q) = sqrt(abar) * score_vp(sqrt(abar) q).
    def _vp(self, x, sigma):
        abar = 1.0 / (1.0 + sigma ** 2)
        sa = torch.sqrt(abar)
        return abar, sa, torch.sqrt(1.0 - abar), self.raw(sa.unsqueeze(-1) * x, torch.log(sigma))

    def _rf(self, x, sigma):
        t = sigma / (1.0 + sigma)                       # z = (1-t) h + t eps  <=>  q = h + sigma eps, z = (1-t) q
        z = (1.0 - t).unsqueeze(-1) * x
        return t, z, self.raw(z, torch.log(sigma))

    def _edm(self):
        import param_edm
        return param_edm, getattr(self, "sigma_data", param_edm.SIGMA_DATA_DEFAULT)

    def score_real(self, x, sigma):
        if self.param == "edm":
            P, sd = self._edm()
            return P.edm_score(self.raw, x, sigma, sd)
        if self.param == "ve":
            eps = self.raw(x, torch.log(sigma))
            return -eps / sigma.unsqueeze(-1)                                     # s = -eps_hat/sigma
        if self.param == "vp":
            abar, sa, sb, eps = self._vp(x, sigma)
            return (sa / sb).unsqueeze(-1) * (-eps)                               # sqrt(abar) * (-eps/sqrt(1-abar))
        t, z, v = self._rf(x, sigma)
        # Gaussian probability path z = a h + b eps with a = 1-t, b = t, a+b = 1.  v = E[eps - h|z] and
        # s_z = -(z - a E[h|z])/b^2 give E[h|z] = z - b v and s_z = -(a v + z)/(b(a+b)) = -((1-t)v + z)/t;
        # pulling back through z = (1-t) q (p_ve(q) = (1-t)^{2N} p_z((1-t)q)) gives the VE score below.
        return -((1.0 - t) ** 2 / t).unsqueeze(-1) * (v + x)

    def denoise_real(self, x, sigma):
        """The NATIVE denoiser head -- deliberately NOT  x + sigma^2 * score_real  (gate GA compares them)."""
        if self.param == "edm":
            P, sd = self._edm()
            return P.edm_denoise(self.raw, x, sigma, sd)
        if self.param == "ve":
            return x - sigma.unsqueeze(-1) * self.raw(x, torch.log(sigma))        # VE x0-head
        if self.param == "vp":
            abar, sa, sb, eps = self._vp(x, sigma)
            return ((sa.unsqueeze(-1) * x) - sb.unsqueeze(-1) * eps) / sa.unsqueeze(-1)   # VP x0-head
        t, z, v = self._rf(x, sigma)
        return z - t.unsqueeze(-1) * v                                            # flow x-prediction

    def loss(self, x0, sigma, eps):
        """04_SPEC §4.  L1: E|| sigma s_theta + eps ||^2 = E||eps_hat - eps||^2 in the eps-parameterisation."""
        s = sigma.unsqueeze(-1)
        if self.param == "edm":
            P, sd = self._edm()
            return P.edm_loss(self.raw, x0, sigma, eps, sd)
        if self.param == "ve":
            return ((self.raw(x0 + s * eps, torch.log(sigma)) - eps) ** 2).mean()
        if self.param == "vp":
            abar = 1.0 / (1.0 + sigma ** 2)
            u = torch.sqrt(abar).unsqueeze(-1) * x0 + torch.sqrt(1.0 - abar).unsqueeze(-1) * eps
            return ((self.raw(u, torch.log(sigma)) - eps) ** 2).mean()
        t = (sigma / (1.0 + sigma)).unsqueeze(-1)
        return ((self.raw((1.0 - t) * x0 + t * eps, torch.log(sigma)) - (eps - x0)) ** 2).mean()


class VAEModel(nn.Module):
    """Rung L6 (04_SPEC §4, lowest priority): a VAE prior, i.e. NOT a diffusion model -- it answers the
    reviewer question "would a GMM/VAE not do?".  p(h) = int N(x; dec(z), s_x^2 I) N(z; 0, I) dz with a single
    shared scalar observation variance, which keeps the component covariance isotropic and therefore the
    complex prior circularly symmetric (a per-dimension variance would break Re/Im symmetry).
    For the receiver the latent integral is frozen ONCE into an n_mix-component Gaussian mixture on a fixed
    seeded set of latents (freeze()); the denoiser and score of that mixture are closed form.
      [approximation] the frozen mixture is a Monte-Carlo approximation of the latent integral (n_mix = 512);
      it is the ONLY approximation in the file and it is the price of using a VAE as Module H."""

    def __init__(self, dim, width, depth, latent, n_mix):
        super().__init__()
        self.dim, self.latent, self.n_mix = dim, latent, n_mix
        mk = lambda i, o: nn.Sequential(*sum(([nn.Linear(i if k == 0 else width, width), nn.SiLU()]
                                              for k in range(depth)), []), nn.Linear(width, o))
        self.enc, self.dec = mk(dim, 2 * latent), mk(latent, dim)
        self.log_sx = nn.Parameter(torch.tensor(-1.0))
        g = torch.Generator().manual_seed(SEED_VAE)
        self.register_buffer("z_fix", torch.randn(n_mix, latent, generator=g))   # frozen latents (in the ckpt)
        self.register_buffer("mu_fix", torch.zeros(n_mix, dim))
        self.param = "vae"

    def freeze(self):
        with torch.no_grad():
            self.mu_fix.copy_(self.dec(self.z_fix.to(self.mu_fix.dtype)))
        return self

    def _mix(self, x, sigma):
        v = torch.exp(2 * self.log_sx) + sigma.unsqueeze(-1) ** 2                # per-component noisy variance
        d = x.unsqueeze(-2) - self.mu_fix                                        # (..., n_mix, dim)
        w = torch.softmax(-0.5 * (d ** 2).sum(-1) / v, -1)
        return v, d, w

    def score_real(self, x, sigma):
        v, d, w = self._mix(x, sigma)
        return -(w.unsqueeze(-1) * d).sum(-2) / v

    def denoise_real(self, x, sigma):
        """Native path: per-component Wiener shrinkage towards mu_m, then the mixture average."""
        v, d, w = self._mix(x, sigma)
        s2 = (sigma ** 2).unsqueeze(-1)
        return (w.unsqueeze(-1) * (x.unsqueeze(-2) - (s2 / v).unsqueeze(-1) * d)).sum(-2)

    def loss(self, x0, sigma, eps):
        """Negative ELBO per real dimension.  sigma is unused (the VAE is not noise-conditional); eps is reused
        as the reparameterisation noise so that the VALIDATION loss is deterministic like every other rung."""
        h = self.enc(x0)
        mu, lv = h[..., :self.latent], h[..., self.latent:].clamp(-8, 8)
        z = mu + torch.exp(0.5 * lv) * eps[..., :self.latent]
        rec = ((x0 - self.dec(z)) ** 2).sum(-1) / (2 * torch.exp(2 * self.log_sx)) + self.dim * self.log_sx
        kl = 0.5 * (mu ** 2 + lv.exp() - 1.0 - lv).sum(-1)
        return ((rec + kl) / self.dim).mean()


class ExactGMMTorch(nn.Module):
    """The EXACT mixture denoiser/score of a t2_gmm.GMMPriorB, re-expressed in torch on the real 2N map.
    It exists for the two mandatory self-tests only:
      (a) selftest_M5 pushes it through the SAME autodiff/Wirtinger machinery as a trained net and compares
          (m, J, alpha) with GMMPriorB.denoise_full / .denoise  -> catches every factor-2, conjugation and
          real/complex packing error in this file;
      (b) selftest_gates feeds it to gates_D1 as if it were the model -> GA..GD must come out ~ 0, which is
          the proof that the gate code is not vacuous.
    Both paths are written from DIFFERENT closed forms:  denoise = sum_k w_k C_k(C_k+nu)^-1 q,
    score = -sum_k w_k (C_k+nu)^-1 q  (equal by Tweedie, but not the same expression)."""

    def __init__(self, prior, dtype=torch.float64):
        super().__init__()
        cd = torch.complex128 if dtype == torch.float64 else torch.complex64
        self.N, self.param = prior.N, "exact"
        self.register_buffer("lam", torch.as_tensor(np.asarray(prior.lam), dtype=dtype))
        self.register_buffer("U", torch.as_tensor(np.asarray(prior.U), dtype=cd))
        self.register_buffer("logpi", torch.as_tensor(np.log(prior.pi), dtype=dtype))

    def _post(self, q, nu):
        z = torch.einsum("kji,...j->...ki", self.U.conj(), q)                     # U_k^H q
        d = self.lam + nu.unsqueeze(-1).unsqueeze(-1)
        lw = self.logpi - (z.real ** 2 + z.imag ** 2).div(d).sum(-1) - torch.log(d).sum(-1)
        return torch.softmax(lw, -1), z, d

    def score_real(self, x, sigma):
        q = _unpack(x)
        w, z, d = self._post(q, SIGMA_TO_NU_T(sigma))
        sk = torch.einsum("kij,...kj->...ki", self.U, (1.0 / d).to(z.dtype) * z)  # (C_k + nu I)^-1 q
        return 2.0 * _pack(-torch.einsum("...k,...ki->...i", w.to(sk.dtype), sk))  # s_real = 2 * [Re, Im] of s_c

    def denoise_real(self, x, sigma):
        q = _unpack(x)
        w, z, d = self._post(q, SIGMA_TO_NU_T(sigma))
        mk = torch.einsum("kij,...kj->...ki", self.U, (self.lam / d).to(z.dtype) * z)   # C_k(C_k+nu)^-1 q
        return _pack(torch.einsum("...k,...ki->...i", w.to(mk.dtype), mk))


def make_model(rung, hp, Nr, Nt):
    """rung + (resolved) hyper-parameters -> torch.nn.Module.  Pure: 'auto' fields must already be resolved
    by resolve_hp(), so a checkpoint can always rebuild its own model from the hp it stored."""
    dim = 2 * Nr * Nt
    assert hp.get("param") in ("ve", "vp", "rf", "edm", "vae"), f"unresolved hp['param'] = {hp.get('param')!r}"
    assert hp.get("arch") in ("mlp", "conv", "unet", "dit", "uvit", "adm", "vae"), \
        f"unresolved hp['arch'] = {hp.get('arch')!r}"
    if hp["arch"] == "vae":
        return VAEModel(dim, hp["width"], hp["depth"], hp["latent"], hp["n_mix"])
    ang = hp["domain"] == "angle"
    if hp["arch"] == "conv":
        net = _Conv(Nr, Nt, hp["width"], hp["depth"], hp["emb"], circular=ang)
    elif hp["arch"] == "unet":
        net = _UNet(Nr, Nt, hp["width"], hp["depth"], hp["emb"], circular=ang)
    elif hp["arch"] in ("dit", "uvit", "adm"):
        # lazy import: arch_*.py do `import score` at module level, so a top-level from-import here
        # would be circular (noted by the arch_dit reviewer).
        if hp["arch"] == "dit":
            # hp['head'] == 'energy' is Stage C variant V2 (10_SPEC_stageC §3b): the SAME DiT trunk with its
            # vector output head replaced by a scalar energy and forward() returning grad_x E, so that every
            # Jacobian downstream is a Hessian and SYMMETRIC by construction.  Absent -- which it is in every
            # existing hp dict and every existing checkpoint -- nothing changes: the plain DiT branch runs.
            if hp.get("head") == "energy":
                import arch_energy
                net = arch_energy.EnergyDiT(Nr, Nt, hp["width"], hp["depth"], hp["emb"], circular=ang,
                                            patch=hp.get("patch", 1), heads=hp.get("heads", 4))
            else:
                import arch_dit
                net = arch_dit.DiT(Nr, Nt, hp["width"], hp["depth"], hp["emb"], circular=ang,
                                   patch=hp.get("patch", 1), heads=hp.get("heads", 4))
        elif hp["arch"] == "uvit":
            import arch_uvit
            net = arch_uvit.UViT(Nr, Nt, hp["width"], hp["depth"], hp["emb"], circular=ang,
                                 patch=hp.get("patch", 1), heads=hp.get("heads", 4))
        else:
            import arch_adm
            net = arch_adm.ADMUNet(Nr, Nt, hp["width"], hp["depth"], hp["emb"], circular=ang,
                                   heads=hp.get("heads", 4), attn_at=hp.get("attn_at", 8))
    else:
        net = _MLP(dim, hp["width"], hp["depth"], hp["emb"])
    return ScoreModel(net, hp["param"], Nr, Nt, M=dft_domain_matrix(Nr, Nt) if ang else None)


def n_params(model):
    return sum(p.numel() for p in model.parameters())


# ----------------------------------------------------------------------------- Wirtinger machinery
def tweedie_real(model, x, sigma):
    """x + sigma_t^2 * s(x, sigma_t).  Equivalent to the complex  q + nu * d/dq* log p  because
    sigma_t^2 = nu/2 and s_real = 2 * [Re(s_c), Im(s_c)]."""
    return x + (sigma ** 2).unsqueeze(-1) * model.score_real(x, sigma)


def wirtinger(Jr):
    """(..., 2N, 2N) real Jacobian of the real denoiser map -> (..., N, N) complex J = dm/dq (q* held fixed)."""
    n = Jr.shape[-1] // 2
    a, b = Jr[..., :n, :n], Jr[..., :n, n:]
    c, d = Jr[..., n:, :n], Jr[..., n:, n:]
    return 0.5 * torch.complex(a + d, c - b)


def project_psd(J, lam_min=C.LAM_MIN):
    """(F1) Project a complex Wirtinger Jacobian onto the constraint set the TRUE posterior-mean denoiser
    is guaranteed to satisfy, and onto nothing else.  Under real Gaussian noise of std sigma,
    J = dm/dq = Cov(h|q)/nu, so J is Hermitian and PSD -- necessarily.  A network's Jacobian is not.

    Hermitian part, then the eigenvalues of that Hermitian part floored at lam_min (= common.LAM_MIN,
    the constant RouteAClip already floors Lambda with; no new constant is introduced).
    lmax is NOT touched: the exact GMM denoiser genuinely has lmax(J) > 1 on a large fraction of D2 test
    points, so clamping the top of the spectrum would impose a bias the true prior does not have.
    When no eigenvalue is below the floor the Hermitian part is returned untouched -- so on a denoiser
    whose Jacobian is already Hermitian PSD (the exact GMM) this is the identity to machine precision,
    not merely to eigendecomposition round-off (selftest_M6, step 1)."""
    H = 0.5 * (J + J.conj().T)
    w, V = np.linalg.eigh(H)
    if w.min() >= lam_min:
        return H
    return (V * np.maximum(w, lam_min)) @ V.conj().T


def jac_batch(f, X, S):
    """Batched real Jacobian of f(x, sigma) over the leading sample axis (reverse mode; 2N VJPs per sample,
    vectorised).  2N = 64 for the 8x4 cell, so this is a single small batched backward."""
    return torch.func.vmap(torch.func.jacrev(f, argnums=0))(X, S)


def jac_asym_hutch(model, x, sigma, v):
    """V3 (10_SPEC_stageC §3b): Hutchinson estimate of  R = E_v || (J - J^T) v ||^2  for
    J = d tweedie_real / dx, the REAL Jacobian of the DENOISER.

    WHICH JACOBIAN, AND WHY THE DENOISER AND NOT THE SCORE.  m = x + sigma^2 s, so J = I + sigma^2 J_s and
    J - J^T = sigma^2 (J_s - J_s^T): the two differ by the identity (which is symmetric and drops out) and
    by the factor sigma^2, i.e. penalising the denoiser is the SAME constraint with a sigma^4 weight.  The
    denoiser is the object the receiver actually differentiates -- ScorePrior.denoise_full returns
    wirtinger(d tweedie_real/dx) and RouteAClip._matrix_site inverts nu times its Hermitian part -- and it
    is the matrix code/jacobian_psd.py reports asym(Jr) for.  So the regularised quantity, the diagnosed
    quantity and the consumed quantity are the same object.

    Jv is a jvp (the double-backward trick: JTu = J^T u is linear in u, so d(v.JTu)/du = J v) and J^T v is
    the vjp that same call already produced -- TWO backward passes, the full Jacobian is never formed.
    E_v||(J-J^T)v||^2 = ||J-J^T||_F^2 for v with unit isotropic covariance (Rademacher here, lower variance
    than Gaussian at the same cost); selftest_V3.py checks that against score.jac_batch."""
    x = x.detach().requires_grad_(True)
    m = tweedie_real(model, x, sigma)
    u = v.detach().clone().requires_grad_(True)
    JTv = torch.autograd.grad(m, x, grad_outputs=u, create_graph=True)[0]       # J^T u, evaluated at u = v
    Jv = torch.autograd.grad(JTv, u, grad_outputs=v, create_graph=True)[0]      # d(v . J^T u)/du = J v
    return ((Jv - JTv) ** 2).sum(-1).mean()


# ----------------------------------------------------------------------------- training data (04_SPEC §2)
def training_split(testbed, prior, Nr, Nt, ntrain=C.N_TRAIN):
    """THE identical N_train = 1e4 channel samples the GMM fit received (arms.training_set), split 9:1 with a
    FIXED seed -- the same split for every rung and every attempt (tests D1t, D2t).
    Normalisation E||H||_F^2 = Nr*Nt is ASSERTED, never silently applied (04_SPEC §2)."""
    X = A.training_set(testbed, prior, Nr, Nt, ntrain)
    N = Nr * Nt
    p = float(np.mean(np.sum(np.abs(X) ** 2, 1))) / N
    assert abs(p - 1.0) < 0.05, f"E||H||_F^2 / (Nr Nt) = {p:.4f} != 1 -- fix the generator, do not rescale here"
    perm = np.random.default_rng(SEED_SPLIT).permutation(len(X))
    nv = int(round(VAL_FRAC * len(X)))
    h = hashlib.sha256(X.tobytes()); h.update(perm.tobytes()); h.update(f"{nv}".encode())
    return X[perm[nv:]], X[perm[:nv]], h.hexdigest()[:16], p


def _sigma_range(testbed):
    nu, sig = SG.load(testbed)                 # MEASURED grid (04_SPEC §3); never invent one
    return float(sig.min()), float(sig.max()), nu, sig


# ----------------------------------------------------------------------------- training (04_SPEC §2)
class _EMA:
    def __init__(self, model, decay):
        self.decay = decay
        self.shadow = {k: v.detach().clone().float() for k, v in model.state_dict().items()}

    def update(self, model):
        for k, v in model.state_dict().items():
            s = self.shadow[k]
            s.mul_(self.decay).add_(v.detach().float(), alpha=1 - self.decay) if s.is_floating_point() else s.copy_(v)

    def copy_to(self, model):
        model.load_state_dict({k: self.shadow[k].to(v.dtype) for k, v in model.state_dict().items()})


def ckpt_path(rung, attempt, testbed, d=None):
    return os.path.join(d or CKPT_DIR, f"{rung}_a{attempt}_{testbed}.pt")


def resolve_hp(rung, attempt, testbed, Nr, Nt, prior=None, device="cpu", n_eval=128, n_jac=16):
    """Fill the 'auto' fields of L3/L4/L5.  04_SPEC §4: L3 takes the backbone of whichever of L1/L2 has the
    better GATE SCORE (not BLER -- 01_RULES §5), L4 keeps the domain L3 chose, and L5 -- "flow matching on
    the configuration that won at L3/L4" -- inherits that winner's ARCHITECTURE as well as its domain, so
    that a conv winner at L4 is actually the thing L5 re-tests ('rf' is the one axis L5 varies).
    On D2 nothing is re-searched: the D1 checkpoint's resolved configuration is copied verbatim (04_SPEC §6)."""
    hp = hp_for(rung, attempt)
    if not any(v == "auto" for v in hp.values()):
        return hp, {}
    if testbed != "D1":                                                    # §6: reuse the D1 configuration
        for a in range(1, MAX_ATTEMPTS + 1):
            p = ckpt_path(rung, a, "D1")
            if os.path.exists(p):
                d1 = torch.load(p, map_location="cpu", weights_only=False)["hp"]
                return dict(hp, **{k: d1[k] for k in ("param", "domain", "arch", "base") if k in d1}), {"from": p}
        raise FileNotFoundError(f"{rung} on {testbed} needs the D1 configuration (04_SPEC §6); no D1 ckpt found")
    cand = {"L3": ("L1", "L2"), "L4": ("L1", "L2", "L3"), "L5": ("L3", "L4", "L1", "L2")}[rung]
    sc = {}
    for r in cand:
        for a in range(1, MAX_ATTEMPTS + 1):
            p = ckpt_path(r, a, testbed)
            if os.path.exists(p):
                try:
                    g = gates_D1(p, Nr, Nt, prior=prior or C.PRIOR_OF[testbed], n_eval=n_eval,
                                 device=device, n_jac=n_jac)
                    sc[r] = min(sc.get(r, np.inf), gate_score(g))
                except Exception as e:                                     # a broken ckpt must not stop the ladder
                    sc[f"{r}!"] = repr(e)
    ok = {k: v for k, v in sc.items() if isinstance(v, float)}
    base = min(ok, key=ok.get) if ok else "L1"
    bhp = None
    for a in range(1, MAX_ATTEMPTS + 1):
        if os.path.exists(ckpt_path(base, a, testbed)):
            bhp = torch.load(ckpt_path(base, a, testbed), map_location="cpu", weights_only=False)["hp"]
    out = dict(hp, base=base)
    for f in ("param", "domain", "arch"):              # 'arch' matters for L5: 04_SPEC §4 says L5 is the
        if out.get(f) == "auto":                       # WINNING configuration, and L4's winner may be conv
            out[f] = (bhp or DEFAULT_HP[base])[f]
    return out, dict(gate_scores=sc, base=base, note="chosen BY GATE SCORE (04_SPEC §4), never by BLER")


# 10_SPEC_stageC §3d -- frozen training-divergence criterion and fallback ladder.
# Registered BEFORE any fallback attempt was run; the trigger is numerical (the validation
# loss series), never a gate value and never a BLER.  Never tuned.
DIVERGE_TRAIN_MULT, DIVERGE_TRAIN_EPOCHS = 3.0, 5
GRAD_CLIP_LADDER = (0.0, 1.0, 1.0)          # attempt 1, 2, 3;  attempt 3 also uses lr/3
LR_DIV_LADDER    = (1.0, 1.0, 3.0)          # divisor applied to the frozen lr


def train(rung, attempt, testbed, prior, Nr, Nt, device="cuda", hp=None, resume=True,
          max_epochs=3000, patience=20, min_epochs=200, log_path=None, ckpt=None, verbose=True,
          ntrain=C.N_TRAIN, jac_reg=0.0, grad_clip=0.0):
    """One ladder attempt, exactly under the regime of 04_SPEC §2 / 01_RULES §5.

    Stopping: validation loss with no improvement for `patience` epochs, but never before `min_epochs`.
    A run that ends any other way is aborted=True: it must be logged to LADDER.md as ABORTED and does NOT
    count as one of the three attempts of the rung.
    Checkpoints every epoch (epoch / model / EMA / optimizer / best_val / RNG state) and resumes from them.

    jac_reg (V3, 10_SPEC_stageC §3b) is OPT-IN and defaults to 0.0, in which case NOTHING below changes:
    the loss object handed to backward() is the same object, no extra number is drawn from the training
    generator `g`, and the log line is byte-identical.  When it is > 0 the loss becomes
    DSM + jac_reg * jac_asym_hutch(...), the probe v is drawn from a SEPARATE generator `gj` so that the
    (x0, sigma, eps) stream stays bit-identical to the jac_reg=0 run of the same rung/attempt, and the
    EARLY-STOPPING criterion is left alone: val_loss() is the pure DSM validation loss, as in V0."""
    t_start = time.time()
    dev = torch.device(device if (device != "cuda" or torch.cuda.is_available()) else "cpu")
    base_hp = hp
    os.makedirs(CKPT_DIR, exist_ok=True); os.makedirs(LOG_DIR, exist_ok=True)
    cpath = ckpt or ckpt_path(rung, attempt, testbed)
    lpath = log_path or os.path.join(LOG_DIR, f"train_{rung}_a{attempt}_{testbed}.log")
    # A resume CONTINUES the run the checkpoint saved, so the CHECKPOINT's hp wins -- never a freshly
    # re-resolved one.  resolve_hp can move between the first call and the resume (more L1/L2 checkpoints
    # exist by then), and for an MLP a different param/domain leaves the state_dict keys and shapes
    # unchanged: the weights would load silently and the net would then be optimised under a different
    # loss than the one it was trained with, while the saved hp still claimed the old configuration.
    st = torch.load(cpath, map_location=dev, weights_only=False) if (resume and os.path.exists(cpath)) else None
    if hp is not None:
        sel = {}
    elif st is not None:
        hp, sel = st["hp"], {"resumed": cpath, "note": "hp taken from the checkpoint, not re-resolved"}
    else:
        hp, sel = resolve_hp(rung, attempt, testbed, Nr, Nt, prior,
                             device="cuda" if dev.type == "cuda" else "cpu")

    # ntrain defaults to the 1e4 budget every ladder arm gets (01_RULES §5).  It is a parameter ONLY so the
    # report-only sample-complexity curve can vary it; no arm is ever built at a different budget.
    Xtr, Xva, split_hash, pw = training_split(testbed, prior, Nr, Nt, ntrain)
    smin, smax, nu_grid, sig_grid = _sigma_range(testbed)
    dim = 2 * Nr * Nt
    tr = torch.as_tensor(np_pack(Xtr), dtype=torch.float32, device=dev)
    va = torch.as_tensor(np_pack(Xva), dtype=torch.float32, device=dev)

    # deterministic validation draws: ONE fixed (sigma, eps) set, reused every epoch, or early stopping is noise.
    vg = torch.Generator().manual_seed(SEED_VAL)
    v_sig = torch.exp(torch.rand(len(va), generator=vg) * (math.log(smax) - math.log(smin)) + math.log(smin))
    v_eps = torch.randn(len(va), dim, generator=vg)
    v_sig, v_eps = v_sig.to(dev), v_eps.to(dev)

    model = make_model(rung, hp, Nr, Nt).to(dev)
    opt = torch.optim.Adam(model.parameters(), lr=hp["lr"])
    ema = _EMA(model, hp["ema"])
    # _rung_ix: RUNGS.index for a ladder rung, so every existing rung keeps its EXACT seed; a stable hash
    # for anything else, so a search driver can pass its own rung label without colliding or crashing.
    g = torch.Generator(device="cpu").manual_seed(SEED_TRAIN + _rung_ix(rung) * 17 + attempt)
    # separate stream for the Hutchinson probes: the data order of a jac_reg run must match jac_reg=0.
    gj = (torch.Generator(device="cpu").manual_seed(SEED_TRAIN + _rung_ix(rung) * 17 + attempt + 7919)
          if jac_reg else None)
    ep0, best, best_ep, hist = 0, np.inf, -1, []
    if st is not None:
        model.load_state_dict(st["model"]); opt.load_state_dict(st["opt"])
        ema.shadow = {k: v.to(dev) for k, v in st["ema"].items()}
        g.set_state(st["rng"].cpu() if torch.is_tensor(st["rng"]) else st["rng"])
        if gj is not None and st.get("rng_jac") is not None:
            gj.set_state(st["rng_jac"].cpu() if torch.is_tensor(st["rng_jac"]) else st["rng_jac"])
        ep0, best, best_ep, hist = st["epoch"], st["best_val"], st["best_epoch"], st["hist"]

    lg = open(lpath, "a", buffering=1)
    lg.write(f"\n# ===== {time.strftime('%Y-%m-%d %H:%M:%S %Z')}  {rung} attempt {attempt}  testbed {testbed} "
             f"prior {prior}  Nr={Nr} Nt={Nt}\n")
    lg.write(f"# DEVICE      : {dev} | cuda_available={torch.cuda.is_available()}"
             + (f" | {torch.cuda.get_device_name(dev)}" if dev.type == "cuda" else f" | {os.cpu_count()} cores")
             + f" | torch {torch.__version__} | train dtype float32 (01_RULES §9.5)\n")
    lg.write(f"# data        : n_train={len(tr)} n_val={len(va)} split_hash={split_hash} "
             f"E||H||_F^2/(NrNt)={pw:.6f} (04_SPEC §2)\n")
    lg.write(f"# sigma grid  : MEASURED, {len(sig_grid)} points, log-uniform draw over [{smin:.4e}, {smax:.4e}]\n")
    lg.write(f"# hp          : {hp}  params={n_params(model)}" + (f"  base-selection {sel}" if sel else "") + "\n")
    lg.write(f"# stopping    : patience {patience} on val loss, never before {min_epochs} epochs, "
             f"max {max_epochs} (01_RULES §5)\n")
    if jac_reg:
        lg.write(f"# jac_reg     : V3, loss += {jac_reg} * E_v||(J-J^T)v||^2, J = d tweedie_real/dx, "
                 f"1 Rademacher probe/sample, lambda FIXED (10_SPEC_stageC §3b, never tuned). "
                 f"val loss / early stopping unchanged (pure DSM).\n")
    dname = (f"{dev}:{torch.cuda.current_device()} {torch.cuda.get_device_name(dev)}" if dev.type == "cuda"
             else f"{dev} ({os.cpu_count()} cores)")
    if verbose:
        print(f"[train] {rung} a{attempt} {testbed}/{prior} {Nr}x{Nt} | {dname} | {n_params(model)} params | "
              f"resume from epoch {ep0} | log {lpath}", flush=True)

    def val_loss():
        ema.copy_to(vm)
        vm.eval()
        with torch.no_grad():
            return float(vm.loss(va, v_sig, v_eps))

    vm = make_model(rung, hp, Nr, Nt).to(dev)
    stopped, aborted, ep, ndiv = "max_epochs", False, ep0, 0
    try:
        for ep in range(ep0 + 1, max_epochs + 1):
            te = time.time()
            model.train()
            idx = torch.randperm(len(tr), generator=g).to(dev)
            tot = nb = rtot = gsum = gmax = 0.0
            nstep = 0
            for i in range(0, len(tr), hp["batch"]):
                b = tr[idx[i:i + hp["batch"]]]
                s = torch.exp(torch.rand(len(b), generator=g) * (math.log(smax) - math.log(smin))
                              + math.log(smin)).to(dev)
                e = torch.randn(len(b), dim, generator=g).to(dev)
                dsm = model.loss(b, s, e)
                loss = dsm
                if jac_reg:
                    v = (2.0 * torch.randint(0, 2, (len(b), dim), generator=gj,
                                             dtype=torch.float32) - 1.0).to(dev)
                    r = jac_asym_hutch(model, b + s.unsqueeze(-1) * e, s, v)
                    loss = dsm + jac_reg * r
                    rtot += float(r.detach()) * len(b)
                opt.zero_grad(set_to_none=True); loss.backward()
                if grad_clip:          # 10_SPEC_stageC §3d fallback.  OFF (0.0) by default, so a V0 run
                    gn = float(torch.nn.utils.clip_grad_norm_(   # is bit-identical to before this change.
                        model.parameters(), grad_clip))
                    gsum += gn; gmax = gn if gn > gmax else gmax
                opt.step(); ema.update(model)
                tot += float(dsm.detach()) * len(b); nb += len(b); nstep += 1
            trl, vl, dt = tot / nb, val_loss(), time.time() - te
            hist.append((ep, trl, vl))
            imp = vl < best - 1e-12
            if imp:
                best, best_ep = vl, ep
            lg.write(f"epoch {ep:>4} | train {trl:.6e} | val {vl:.6e} | {dt:7.3f} s | "
                     f"best {best:.6e} @{best_ep}{' *' if imp else ''}"
                     + (f" | asym_reg {rtot / nb:.6e}" if jac_reg else "")
                     + (f" | gnorm mean {gsum / max(nstep, 1):.3e} max {gmax:.3e}" if grad_clip else "")
                     + "\n")
            torch.save(dict(epoch=ep, model=model.state_dict(), ema=ema.shadow, opt=opt.state_dict(),
                            best_val=best, best_epoch=best_ep, rng=g.get_state(), hist=hist, hp=hp,
                            rung=rung, attempt=attempt, testbed=testbed, prior=prior, Nr=Nr, Nt=Nt,
                            split_hash=split_hash, wall_sec=time.time() - t_start,
                            jac_reg=jac_reg, grad_clip=grad_clip,
                            rng_jac=(gj.get_state() if gj is not None else None),
                            device=dname), cpath)
            # 10_SPEC_stageC §3d DIVERGE_TRAIN: val above 3x best for 5 consecutive epochs.  This
            # OVERRIDES min_epochs on purpose -- carrying a blown-up run to epoch 200 buys no
            # information.  A DIVERGED run is a COMPLETED attempt (it consumes a slot), not ABORTED.
            # NaN must COUNT as divergence.  `nan > x` is False, so the naive comparison silently
            # disables the guard exactly when it is most needed (audit 2026-09-21 18:20: V2 D2 a2 ran
            # 105 NaN epochs undetected).  math.isnan first, then the ratio test.
            bad = (vl != vl) or (vl > DIVERGE_TRAIN_MULT * best)
            ndiv = ndiv + 1 if bad else 0
            if ndiv >= DIVERGE_TRAIN_EPOCHS:
                stopped = "diverged"
                break
            if ep >= min_epochs and ep - best_ep >= patience:
                stopped = "patience"
                break
    except KeyboardInterrupt:
        stopped, aborted = "interrupted", True
    if stopped == "max_epochs" and ep < min_epochs:
        aborted = True                                    # 01_RULES §5: not an attempt, does not use up the rung
    wall = time.time() - t_start
    lg.write(f"# done        : {ep} epochs, stopped_by={stopped}, aborted={aborted}, best val {best:.6e} "
             f"@ epoch {best_ep}, wall {wall:.1f} s, {wall / max(ep - ep0, 1):.3f} s/epoch\n")
    lg.close()
    if verbose:
        print(f"[train] {rung} a{attempt}: {ep} epochs, stopped_by={stopped}, aborted={aborted}, "
              f"best val {best:.6e} @ {best_ep}, {wall:.1f} s ({wall / max(ep - ep0, 1):.3f} s/epoch)", flush=True)
    return dict(rung=rung, attempt=attempt, ckpt=cpath, epochs=ep, val_loss=best,
                train_loss=(hist[-1][1] if hist else float("nan")), wall_sec=wall, device=dname,
                sec_per_epoch=wall / max(ep - ep0, 1), stopped_by=stopped, n_train=len(tr), n_val=len(va),
                split_hash=split_hash, hp=hp, aborted=aborted, params=n_params(model), log=lpath,
                selection=sel, given_hp=base_hp is not None, jac_reg=jac_reg)


# ----------------------------------------------------------------------------- receiver adapter (04_SPEC §1)
def load_model(ckpt, Nr=None, Nt=None, device="cpu", dtype=torch.float64):
    """Rebuild a model from a checkpoint and load its EMA weights (the weights the gates and the receiver use)."""
    st = torch.load(ckpt, map_location="cpu", weights_only=False) if isinstance(ckpt, str) else ckpt
    m = make_model(st["rung"], st["hp"], Nr or st["Nr"], Nt or st["Nt"])
    m.load_state_dict({k: st["ema"][k].to(v.dtype) for k, v in m.state_dict().items()})
    m = m.to(dtype=dtype, device=device).eval()
    for p in m.parameters():
        p.requires_grad_(False)
    if isinstance(m, VAEModel):
        m.freeze()
    if isinstance(m, ScoreModel):
        m.refresh_M()
    return m, st


class ScorePrior:
    """Module H backed by a trained score model -- duck-types t2_route_a.GMMPrior so that
    arms.route_a(..., moduleH='score', clip='eta') builds M-ours-dscore through EXACTLY the interface
    (one-shot Tweedie + D-13 belief + D-14 matrix site) that the oracle arm M-ours-score uses (04_SPEC §1).

    C / Cinv / cbar / eh2_prior come from Chat -- the SAME sample covariance the GMM arms get -- because the
    receiver uses them only for the second-moment bookkeeping (initial nuE, E|h_ij|^2), which must not differ
    between arms.  The network is float64 here: inference precision is identical for every arm (01_RULES §9.3).

    n_query / n_out_of_grid count how often the receiver asked for a nu outside the MEASURED grid; the grid
    covers the 1-99 percentile of the queries by construction, so a few percent is expected.  We do NOT clamp:
    clamping would silently return the denoiser of a different noise level."""

    def __init__(self, ckpt, Nr, Nt, Chat, device="cpu", psd_project=False):
        self.psd_project = bool(psd_project)       # (F1) / Stage C V1 -- OFF by default: V0 is unchanged
        if device == "cpu":
            torch.set_num_threads(1)               # one worker process = one thread (common.py sets the BLAS env)
        self.model, self.st = load_model(ckpt, Nr, Nt, device=device)
        self.rung, self.attempt = self.st["rung"], self.st["attempt"]
        self.ckpt = ckpt if isinstance(ckpt, str) else self.st.get("ckpt", "<dict>")
        self.Nr, self.Nt, self.N, self.device = Nr, Nt, Nr * Nt, device
        Chat = np.asarray(Chat, complex)
        self.C = 0.5 * (Chat + Chat.conj().T)
        self.Cinv = np.linalg.inv(self.C)
        self.cbar = np.trace(self.C).real / self.N
        self.eh2_prior = np.diag(self.C).real.reshape(Nr, Nt, order="F").mean(0)
        try:
            _, sg = SG.load(self.st["testbed"])
            self.s_lo, self.s_hi = float(sg.min()), float(sg.max())
        except Exception:
            self.s_lo, self.s_hi = 0.0, np.inf
        self.n_query = self.n_out_of_grid = 0
        self.herm_res = 0.0                       # max |nu J - (nu J)^H| / |nu J| seen (diagnostic, not a clip)
        self._cache = None

    def _eval(self, q, nu):
        """(m, J) for the ONE-SHOT TWEEDIE denoiser m = q + nu * s_hat(q, nu) and its Wirtinger Jacobian.
        RouteA (scal='belief', hsite='matrix') calls denoise() and then _matrix_site() with the same (q, nu),
        so the result is cached: one network+Jacobian evaluation per receiver iteration, not two."""
        key = (q.tobytes(), float(nu))
        if self._cache is not None and self._cache[0] == key:
            return self._cache[1]
        self.n_query += 1
        s = float(NU_TO_SIGMA(nu))
        self.n_out_of_grid += int(s < self.s_lo or s > self.s_hi)
        x = torch.as_tensor(np_pack(q), dtype=torch.float64, device=self.device)
        sg = torch.as_tensor(s, dtype=torch.float64, device=self.device)
        f = lambda v: tweedie_real(self.model, v, sg)
        Jr = torch.func.jacrev(f)(x)
        m = np_unpack(f(x).detach().cpu().numpy())
        J = wirtinger(Jr).detach().cpu().numpy()
        SigH = nu * J
        self.herm_res = max(self.herm_res, float(np.max(np.abs(SigH - SigH.conj().T))
                                                 / max(np.max(np.abs(SigH)), 1e-300)))
        # nu*J must be Hermitian for RouteAClip._matrix_site; the receiver symmetrises anyway, so the
        # Hermitian part changes nothing there and leaves alpha = tr(J).real/N untouched.
        # psd_project=True additionally floors the eigenvalues (F1); it is a DIFFERENT arm, never the default.
        J = project_psd(J) if self.psd_project else 0.5 * (J + J.conj().T)
        self._cache = (key, (m, J))
        return m, J

    def denoise(self, q, nu):
        m, J = self._eval(q, nu)
        return m, float(np.trace(J).real / self.N)

    def denoise_full(self, q, nu):
        return self._eval(q, nu)

    def query_stats(self):
        """Out-of-grid reporting for the raw npz and the result header (conf/DECISIONS.md 2026-09-20 12:35:
        extrapolate, never clamp).  frac_out_of_grid is the share of denoiser queries whose sigma_t fell
        outside the FROZEN measured grid [s_lo, s_hi]; a few percent is expected by construction (the grid
        covers the 1-99 percentile), and iteration 1 is always above it.  herm_res is the largest relative
        non-Hermitian residual of nu*J seen before symmetrisation (a diagnostic, not a clip)."""
        return dict(n_query=self.n_query, n_out_of_grid=self.n_out_of_grid,
                    frac_out_of_grid=self.n_out_of_grid / max(self.n_query, 1),
                    herm_res=self.herm_res, s_lo=self.s_lo, s_hi=self.s_hi)


last_reason = ""      # why the last load_prior() returned None -- or which checkpoint it returned and why


def _passing_attempts(testbed):
    """The (rung, attempt) pairs RECORDED AS PASSING, read from conf/results/gate_<testbed>.txt and from the
    ladder state conf/LADDER.md.  A row counts only when one of its pipe-separated fields is exactly 'PASS',
    so a FAIL row, an ABORTED row, the format line 'PASS/FAIL' or a prose mention can never be mistaken for
    one: the parser fails CLOSED.  Ordered by 04_SPEC §4, where the ladder stops at the first rung to pass."""
    out = []
    for p in (os.path.join(C.CONF, "results", f"gate_{testbed}.txt"), LADDER):
        if not os.path.exists(p):
            continue
        with open(p) as f:
            for line in f:
                fld = [c.strip().strip("`") for c in line.split("|")]
                if "PASS" not in fld or len(fld) < 2:
                    continue
                m, n = re.search(r"\b(L[1-6])\b", fld[0]), re.search(r"\ba?([1-3])\b", fld[1])
                if m and n:
                    out.append((m.group(1), int(n.group(1))))
    return sorted(set(out), key=lambda t: (_rung_ix(t[0]), t[1]))


def load_prior(testbed, prior, Nr, Nt, rung=None, attempt=None, ckpt=None, device="cpu", psd_project=False,
               ntrain=None):
    """Module H for M-ours-dscore: the gate-passing checkpoint wrapped as a ScorePrior.
    ckpt given -> use it.  Otherwise pick the checkpoint recorded as PASSING in
    conf/results/gate_<testbed>.txt / the ladder state, or (rung, attempt) if given.
    Chat is the sample covariance of the SAME training set the GMM arms got:
    arms.load_fits(testbed, prior, Nr)[("full", 32)]["Chat"].
    Returns None (never raises) when no gate-passing checkpoint exists, so the runner can mark
    the arm absent rather than crash.

    It NEVER silently returns an un-gated checkpoint: without an explicit `ckpt` the chosen (rung, attempt)
    must carry a recorded PASS, and a (rung, attempt) without one returns None.  THE REASON IS IN THE
    MODULE-LEVEL STRING `score.last_reason`, which the caller reads after the call -- on None it says why,
    and on success it names the checkpoint and whether the gate record or the caller chose it (an explicit
    `ckpt` is an operator override and is reported as NOT gate-verified by this function)."""
    global last_reason
    try:
        ok = _passing_attempts(testbed)
        if ckpt is None:
            cand = [t for t in ok if (rung is None or t[0] == rung) and (attempt is None or t[1] == attempt)]
            if not cand:
                last_reason = (f"no gate-passing checkpoint for {testbed}"
                               + (f" at {rung or '*'} a{attempt or '*'}" if (rung or attempt) else "")
                               + f"; recorded PASS rows: {ok or 'none'} (searched conf/results/"
                                 f"gate_{testbed}.txt and {os.path.basename(LADDER)})")
                return None
            rung, attempt = cand[0]
            ckpt = ckpt_path(rung, attempt, testbed)
            if not os.path.exists(ckpt):
                last_reason = f"{rung} a{attempt} is recorded PASS for {testbed} but the file {ckpt} is missing"
                return None
            why = f"{rung} a{attempt} recorded PASS -> {ckpt}"
        else:
            why = (f"explicit ckpt {ckpt} -- caller override, NOT verified against the gate record here "
                   f"(recorded PASS rows: {ok or 'none'})")
        # ntrain=None keeps arms.load_fits' own default (N_TRAIN) -- byte-identical to the previous call.
        # Stage C passes the run's --ntrain so that Chat comes from the SAME channel set the GMM arms were
        # fitted on (10_SPEC A3, equal budget); with N'=1.6e5 fits the default would find no file at all.
        Chat = A.load_fits(testbed, prior, Nr, *( () if ntrain is None else (ntrain,) ))[("full", 32)]["Chat"]
        sp = ScorePrior(ckpt, Nr, Nt, Chat, device=device, psd_project=psd_project)
        last_reason = why
        return sp
    except Exception as ex:
        last_reason = f"{type(ex).__name__}: {ex}"
        return None


# ----------------------------------------------------------------------------- gates GA-GD (04_SPEC §5)
def _as_model(ckpt, Nr, Nt, device):
    if hasattr(ckpt, "score_real"):
        return ckpt, {"rung": getattr(ckpt, "param", "?"), "attempt": 0, "hp": {}}
    m, st = load_model(ckpt, Nr, Nt, device=device)
    return m, st


def _model_device(m):
    """Where the model actually lives.  ExactGMMTorch has buffers but no parameters, so check both: every
    tensor the gates build must be created there or the first matmul raises (device='cuda' path)."""
    for t in list(m.parameters()) + list(m.buffers()):
        return t.device
    return torch.device("cpu")


def _gate_batch(model, X, sig, n_jac, chunk=64):
    """Model-side quantities at one grid point.  The two denoiser paths are evaluated on ALL n_eval samples
    (cheap, no derivatives); the Wirtinger Jacobian -- and therefore alpha = tr(J)/N, which GD compares -- only
    on the first n_jac of them, because GD is an EXPECTATION and a Jacobian costs 2N backward passes."""
    nat, tw = [], []
    for i in range(0, len(X), chunk):
        x = X[i:i + chunk]
        s = torch.full((len(x),), sig, dtype=x.dtype, device=x.device)
        with torch.no_grad():
            nat.append(model.denoise_real(x, s))
            tw.append(tweedie_real(model, x, s))
    J, nj = [], min(n_jac, len(X))
    for i in range(0, nj, chunk):
        x = X[i:min(i + chunk, nj)]
        s = torch.full((len(x),), sig, dtype=x.dtype, device=x.device)
        J.append(wirtinger(jac_batch(lambda v, u: tweedie_real(model, v, u), x, s)))
    J = torch.cat(J) if J else torch.zeros(0, X.shape[-1] // 2, X.shape[-1] // 2,
                                            dtype=torch.complex128, device=X.device)
    return torch.cat(nat), torch.cat(tw), torch.diagonal(J, dim1=-2, dim2=-1).sum(-1).real / max(J.shape[-1], 1), J


def gates_D1(ckpt, Nr, Nt, prior="S", n_eval=512, device="cpu", n_jac=64, verbose=False, stream=10):
    """The four pre-registered quality gates of 04_SPEC §5, on HELD-OUT D1 samples (common.train_rng stream 10)
    and on the FROZEN measured sigma grid.  D1 is the instrument: its true prior IS a GMMPriorB, so the exact
    score, denoiser and Jacobian are closed form.

      GA <= 1e-6   Tweedie self-consistency: || (q + nu s_hat) - native_denoise || / || native_denoise ||
                   (two separate code paths -- see ScoreModel).  GA_NOTE applies: this quantity is
                   identically zero by construction here and PASS rests on GB/GC/GD.
      GB <= +5%    denoising NMSE excess over the exact score, AT EVERY grid point
      GC <= 0.15   E||s_hat - s_star||_2 / E||s_star||_2
      GD <= 0.20   relative FROBENIUS error of the FULL Wirtinger matrix J that D-14 consumes
                   (RouteAClip._matrix_site inverts SigH = nu*J, so the matrix -- not its trace -- is
                   "the Jacobian/divergence estimate that D-14 uses" of 04_SPEC §5; the stricter of the
                   two readings, per 01_RULES §1).  Measured on the first n_jac samples: it is an
                   expectation and one Jacobian costs 2N backward passes.
      GD_trace     the OLD scalar quantity, the relative error of tr(J)/N.  REPORTED, NOT GATED
                   (no GATE_TOL entry) -- conf/DECISIONS.md 2026-09-20 12:35.
    PASS = GA, GB, GC, GD.  The per-point numbers are returned in `per_sigma`, not just the verdict."""
    model, st = _as_model(ckpt, Nr, Nt, device)
    mdev = _model_device(model)
    gen = C.make_gen("D1", prior, Nr, Nt)
    P = gen.prior                                            # GMMPriorB: exact score / denoiser / Jacobian
    N = Nr * Nt
    _, _, nu_grid, sig_grid = _sigma_range("D1")
    # stream 10 = the held-out draw the REPORTED gate uses.  An HPO search must pass a different stream
    # (11) and the winner is then re-gated on 10, so hundreds of trials cannot overfit the reported number.
    rng = C.train_rng("D1", prior, Nr, stream)                # held-out stream (never trained on)
    H = gen.sample_vecs(rng, n_eval)
    nrng = np.random.default_rng(SEED_GATE)                  # same (h, eps) for EVERY rung -> paired comparison
    E = (nrng.standard_normal((n_eval, N)) + 1j * nrng.standard_normal((n_eval, N))) / np.sqrt(2)
    Ht = torch.as_tensor(np_pack(H), dtype=torch.float64)
    rows = []
    for k, (nu, sg) in enumerate(zip(nu_grid, sig_grid)):
        Q = H + np.sqrt(nu) * E
        m_star = np.empty_like(Q); a_star = np.empty(n_eval)
        for i in range(n_eval):                              # authoritative exact side: the numpy GMMPriorB
            m_star[i], a_star[i] = P.denoise(Q[i], nu)
        s_star = (m_star - Q) / nu                           # Tweedie -> exact Wirtinger score
        Xq = torch.as_tensor(np_pack(Q), dtype=torch.float64, device=mdev)
        nat, tw, alpha, J = _gate_batch(model, Xq, float(sg), n_jac)
        m_hat = np_unpack(tw.cpu().numpy()); m_nat = np_unpack(nat.cpu().numpy())
        s_hat = (m_hat - Q) / nu
        # GA.  KNOWN AND VERIFIED: this is identically zero by construction for every parameterisation of
        # ScoreModel, because x + sigma^2 * score_real collapses onto the native x0 head:
        #   ve:  x + s^2 * (-eps/s)                     = x - s*eps                      = native
        #   vp:  sqrt(abar)/sqrt(1-abar) = 1/sigma, so the score reduces to -eps/sigma    = native
        #   rf:  (1-t)^2/t = 1/(sigma(1+sigma)), so x + s^2*score = x(1-t) - t*v          = native
        # GA therefore guards an INCONSISTENCY between the score path and the x0 path; it cannot catch an
        # error shared by both, and a PASS rests on GB/GC/GD (GA_NOTE, conf/DECISIONS.md 2026-09-20 12:35).
        # The computation and the 1e-6 tolerance are 04_SPEC §5 verbatim and are NOT changed.
        ga = float(np.max(np.linalg.norm(m_hat - m_nat, axis=1)
                          / np.maximum(np.linalg.norm(m_nat, axis=1), 1e-300)))
        e_hat = float(np.mean(np.sum(np.abs(m_hat - H) ** 2, 1)))
        e_star = float(np.mean(np.sum(np.abs(m_star - H) ** 2, 1)))
        p_h = float(np.mean(np.sum(np.abs(H) ** 2, 1)))
        gb = e_hat / e_star - 1.0
        gc = float(np.sum(np.linalg.norm(s_hat - s_star, axis=1)) / np.sum(np.linalg.norm(s_star, axis=1)))
        nj = min(n_jac, n_eval)
        ah = alpha.cpu().numpy()
        # GD_trace: the OLD scalar quantity, kept and REPORTED, but not the gate any more.
        gd_tr = float(np.mean(np.abs(ah - a_star[:nj])) / np.mean(np.abs(a_star[:nj]))) if nj else float("nan")
        jf = herm = float("nan")
        if nj:                                               # THE GATE (GD): the FULL matrix D-14 consumes
            num = den = 0.0; hm = 0.0
            for i in range(nj):
                _, Js = P.denoise_full(Q[i], nu)
                Ji = J[i].cpu().numpy()
                num += np.linalg.norm(Ji - Js); den += np.linalg.norm(Js)
                hm = max(hm, float(np.max(np.abs(Ji - Ji.conj().T)) / max(np.max(np.abs(Ji)), 1e-300)))
            jf, herm = num / max(den, 1e-300), hm
        rows.append(dict(k=k, nu=float(nu), sigma=float(sg), GA=ga, GB=gb, GC=gc, GD=jf, GD_trace=gd_tr,
                         nmse_hat=e_hat / p_h, nmse_star=e_star / p_h, alpha_hat=float(ah.mean()),
                         alpha_star=float(a_star[:nj].mean()) if nj else float("nan"),
                         J_rel_fro=jf, herm_res=herm, n_jac=nj))
        if verbose:
            print(f"  k={k:2d} sigma={sg:.4e} nu={nu:.4e} | GA {ga:.2e} | GB {gb:+.4%} | GC {gc:.4f} | "
                  f"GD {jf:.4f} | GD_trace {gd_tr:.4f} | NMSE {e_hat / p_h:.4e} vs {e_star / p_h:.4e}")
    # np.max, NOT the builtin: builtin max() silently keeps 0.9 out of [0.9, nan], which would drop a
    # diverged grid point from the aggregate (01_RULES §4/§5).  np.max propagates the NaN and nan <= tol
    # is False, so a non-finite grid point FAILS the gate.
    G = {g: float(np.max([r[g] for r in rows])) for g in ("GA", "GB", "GC", "GD", "GD_trace")}
    G.update(per_sigma=rows, passed=all(G[g] <= GATE_TOL[g] for g in GATE_TOL), tol=dict(GATE_TOL),
             rung=st.get("rung"), attempt=st.get("attempt"), ckpt=(ckpt if isinstance(ckpt, str) else "<model>"),
             n_eval=n_eval, n_jac=n_jac, Nr=Nr, Nt=Nt, prior=prior, hp=st.get("hp", {}), ga_note=GA_NOTE)
    if verbose:
        print(f"  WORST | GA {G['GA']:.2e} | GB {G['GB']:+.4%} | GC {G['GC']:.4f} | GD {G['GD']:.4f} "
              f"(tol {GATE_TOL['GD']}) | GD_trace {G['GD_trace']:.4f} (reported, not gated) | "
              f"gate_score {gate_score(G):.3f} | passed={G['passed']}")
        print(f"  NOTE  | {GA_NOTE}")
    return G


def gate_score(G):
    """Scalar summary used ONLY to order rungs (04_SPEC §4 "게이트 점수"): the worst gate in units of its own
    tolerance.  < 1 means every gate passes.  It never sees a BLER.
    It scores exactly the four GATE_TOL entries, so its GD term is the FULL-matrix relative Frobenius error;
    GD_trace has no tolerance and is deliberately NOT part of the score (it is reported alongside it, see the
    'WORST' line of gates_D1(verbose=True) and the LADDER note).  GA contributes but is structurally zero --
    see GA_NOTE."""
    return float(np.max([G[g] / GATE_TOL[g] for g in GATE_TOL]))


def gb_prime(ckpt, gmm_prior, testbed, Nr, Nt, prior=None, n_eval=512, device="cpu", true_prior=None):
    """GB' (04_SPEC §6) -- the pre-registered REPORT-ONLY comparison for the claim testbed D2, where no exact
    score exists: denoising NMSE of the GMM prior and of the diffusion prior on held-out samples over the SAME
    sigma grid.  It is never used to select anything (§6: "선택에 쓰지 않는다. 보고에만 쓴다")."""
    prior = prior or C.PRIOR_OF[testbed]
    gen = C.make_gen(testbed, prior, Nr, Nt)
    N = Nr * Nt
    _, _, nu_grid, sig_grid = _sigma_range(testbed)
    H = gen.sample_vecs(C.train_rng(testbed, prior, Nr, 10), n_eval)
    nrng = np.random.default_rng(SEED_GATE)
    E = (nrng.standard_normal((n_eval, N)) + 1j * nrng.standard_normal((n_eval, N))) / np.sqrt(2)
    model = None if ckpt is None else _as_model(ckpt, Nr, Nt, device)[0]
    mdev = None if model is None else _model_device(model)
    rows = []
    for k, (nu, sg) in enumerate(zip(nu_grid, sig_grid)):
        Q = H + np.sqrt(nu) * E
        p_h = float(np.mean(np.sum(np.abs(H) ** 2, 1)))
        r = dict(k=k, nu=float(nu), sigma=float(sg), nmse_gmm=float(np.mean(
            [np.sum(np.abs(gmm_prior.denoise(Q[i], nu)[0] - H[i]) ** 2) for i in range(n_eval)])) / p_h)
        if true_prior is not None:
            r["nmse_exact"] = float(np.mean(
                [np.sum(np.abs(true_prior.denoise(Q[i], nu)[0] - H[i]) ** 2) for i in range(n_eval)])) / p_h
        if model is not None:
            X = torch.as_tensor(np_pack(Q), dtype=torch.float64, device=mdev)
            with torch.no_grad():
                m = np_unpack(tweedie_real(model, X, torch.full((len(X),), float(sg), dtype=X.dtype,
                                                                device=mdev)).cpu().numpy())
            r["nmse_model"] = float(np.mean(np.sum(np.abs(m - H) ** 2, 1))) / p_h
            r["excess"] = r["nmse_model"] / r["nmse_gmm"] - 1.0
        rows.append(r)
    return dict(per_sigma=rows, testbed=testbed, prior=prior, n_eval=n_eval, Nr=Nr, Nt=Nt,
                worst_excess=(max((r["excess"] for r in rows), default=float("nan")) if model is not None
                              else float("nan")),
                note="GB' is REPORT-ONLY (04_SPEC §6); arm selection was fixed by the D1 gates")


# ----------------------------------------------------------------------------- ladder log (04_SPEC §4)
def _fmt(v, f="{:.3e}"):
    return "-" if v is None or (isinstance(v, float) and not np.isfinite(v)) else f.format(v)


def ladder_append(row, path=None):
    """Append ONE line to conf/LADDER.md in its documented format
       [시각] 칸 | 시도# | 구성 요약 | train/val loss | GA | GB | GC | GD | PASS/FAIL | 비고
    `row` is meant to be  {**train(...)-result, **gates_D1(...)-result, 'verdict': ...}.
    APPEND-ONLY: every attempt, including the failed and the ABORTED ones, stays (01_RULES §5)."""
    p = path or LADDER
    hp = row.get("hp", {})
    cfg = row.get("config") or (f"{hp.get('arch','?')} {hp.get('param','?')}/{hp.get('domain','?')} "
                                f"w{hp.get('width','?')} d{hp.get('depth','?')} lr{hp.get('lr','?')} "
                                f"ema{hp.get('ema','?')}" + (f" base={hp['base']}" if hp.get("base") else "")
                                + (f" ({row['params']} par)" if row.get("params") else ""))
    verdict = row.get("verdict") or ("ABORTED" if row.get("aborted") else
                                     ("PASS" if row.get("passed") else "FAIL"))
    note = row.get("note", "")
    if not note:
        note = (f"{row.get('epochs','?')} ep (stop: {row.get('stopped_by','?')}), "
                f"{row.get('wall_sec',float('nan')):.0f} s, {row.get('sec_per_epoch',float('nan')):.2f} s/ep, "
                f"device {row.get('device','?')}, ckpt {row.get('ckpt','?')}")
        if row.get("ckpt") and isinstance(row["ckpt"], str) and os.path.exists(row["ckpt"]):
            note += f" ({os.path.getsize(row['ckpt']) / 1e6:.1f} MB)"
        note += f", split {row.get('split_hash','?')}"
        if row.get("aborted"):
            note += "  -- ABORTED: does NOT count as an attempt (01_RULES §5)"
    if row.get("GD") is not None or row.get("GA") is not None:
        # The pre-registered column count of 04_SPEC §4 is kept; the redefinition and the reported-only
        # GD_trace go into the 비고 field, together with GA_NOTE.
        note += (f"  || GD = full Wirtinger matrix rel. Frobenius error (redefined before any checkpoint was "
                 f"gated, conf/DECISIONS.md 2026-09-20 12:35); GD_trace {_fmt(row.get('GD_trace'), '{:.4f}')} "
                 f"= the old tr(J)/N error, reported not gated. {GA_NOTE}")
    line = (f"[{time.strftime('%Y-%m-%d %H:%M %Z')}] {row.get('rung','?')} | a{row.get('attempt','?')} | {cfg} | "
            f"train {_fmt(row.get('train_loss'))} / val {_fmt(row.get('val_loss'))} | "
            f"GA {_fmt(row.get('GA'))} | GB {_fmt(row.get('GB'), '{:+.2%}')} | GC {_fmt(row.get('GC'), '{:.4f}')} | "
            f"GD {_fmt(row.get('GD'), '{:.4f}')} | {verdict} | {note}\n")
    with open(p, "a") as f:
        f.write(line)
    return line


# ----------------------------------------------------------------------------- MANDATORY self-tests
def selftest_M5(cells=((4, 4), (8, 4)), nus=(2.17e-3, 0.05, 1.25), n=3, tol=1e-8, prior="S"):
    """SELF-TEST 1 (mandatory).  Push the EXACT GMM denoiser of the D1 true prior through the SAME
    autodiff/Wirtinger machinery a trained network goes through, and require it to reproduce
    GMMPriorB.denoise_full (m, J) and GMMPriorB.denoise (alpha) to <= 1e-8.
    This single test catches every factor-of-2, conjugation and real/complex packing error in the file."""
    print(f"[selftest_M5] exact GMMPriorB -> torch -> Wirtinger machinery   (tol {tol:.0e})")
    worst = dict(m=0.0, J=0.0, alpha=0.0, GA=0.0)
    for (Nr, Nt) in cells:
        P = C.make_gen("D1", prior, Nr, Nt).prior
        E = ExactGMMTorch(P)
        rng = np.random.default_rng(1234)
        for nu in nus:
            sg = torch.tensor(float(NU_TO_SIGMA(nu)), dtype=torch.float64)
            em = eJ = ea = ega = 0.0
            for _ in range(n):
                h = P.sample(rng).reshape(-1, order="F")
                q = h + np.sqrt(nu / 2) * (rng.standard_normal(P.N) + 1j * rng.standard_normal(P.N))
                m_np, J_np = P.denoise_full(q, nu)
                _, a_np = P.denoise(q, nu)
                x = torch.as_tensor(np_pack(q), dtype=torch.float64)
                Jr = torch.func.jacrev(lambda v: tweedie_real(E, v, sg))(x)      # RAW, un-symmetrised
                J_t = wirtinger(Jr).numpy()
                m_t = np_unpack(tweedie_real(E, x, sg).numpy())
                m_n = np_unpack(E.denoise_real(x, sg).numpy())
                em = max(em, np.abs(m_t - m_np).max()); eJ = max(eJ, np.abs(J_t - J_np).max())
                ea = max(ea, abs(float(np.trace(J_t).real) / P.N - a_np))
                ega = max(ega, np.abs(m_t - m_n).max())
            print(f"   {Nr}x{Nt} nu={nu:9.3e} sigma_t={float(sg):8.5f} | "
                  f"max|m-m_np| {em:8.2e} | max|J-J_np| {eJ:8.2e} | |alpha-alpha_np| {ea:8.2e} | "
                  f"|tweedie-native| {ega:8.2e}")
            for k, v in zip(("m", "J", "alpha", "GA"), (em, eJ, ea, ega)):
                worst[k] = max(worst[k], v)
    ok = all(v <= tol for v in worst.values())
    print(f"[selftest_M5] worst: m {worst['m']:.2e}  J {worst['J']:.2e}  alpha {worst['alpha']:.2e}  "
          f"tweedie-vs-native {worst['GA']:.2e}   -> {'PASS' if ok else 'FAIL'}")
    return ok, worst


def selftest_gates(Nr=8, Nt=4, prior="S", n_eval=32, n_jac=2):
    """SELF-TEST 2 (mandatory).  Feed the EXACT score in as if it were the model.  The exact side of the gate
    is computed from the numpy GMMPriorB and the model side from the independent torch expression, so
    GA..GD ~ 0 proves BOTH that the gate plumbing is not vacuous and that the two implementations agree."""
    print(f"[selftest_gates] exact score as the 'model'  ({Nr}x{Nt}, n_eval={n_eval}, n_jac={n_jac})")
    P = C.make_gen("D1", prior, Nr, Nt).prior
    G = gates_D1(ExactGMMTorch(P), Nr, Nt, prior=prior, n_eval=n_eval, n_jac=n_jac)
    r = G["per_sigma"]
    print(f"   GA {G['GA']:.2e}  GB {G['GB']:+.3e}  GC {G['GC']:.3e}  GD {G['GD']:.3e} (full J)  "
          f"GD_trace {G['GD_trace']:.3e} (reported)  max J_rel_fro {max(x['J_rel_fro'] for x in r):.2e}  "
          f"passed={G['passed']}")
    print(f"   note: {GA_NOTE}")
    ok = (G["passed"] and G["GA"] < 1e-10 and abs(G["GB"]) < 1e-8 and G["GC"] < 1e-8
          and G["GD"] < 1e-8 and G["GD_trace"] < 1e-8)
    print(f"[selftest_gates] -> {'PASS' if ok else 'FAIL'}  (gates must read ~0 for the exact score)")
    return ok, G


def selftest_rungs(Nr=8, Nt=4, sig=0.1):
    """Smoke: every rung builds, runs its loss, its score, its native denoiser and its Jacobian, and its
    Tweedie/native paths agree (GA) -- the same check the gate makes, on random weights."""
    print("[selftest_rungs] rung | params | loss | GA (tweedie vs native) | tr(J)/N | Jacobian shape")
    dim, out = 2 * Nr * Nt, []
    x = torch.randn(4, dim, dtype=torch.float64)
    s = torch.full((4,), sig, dtype=torch.float64)
    e = torch.randn(4, dim, dtype=torch.float64)
    for r in RUNGS:
        hp = dict(hp_for(r, 1))
        for f in ("param", "domain", "arch"):               # stand in for resolve_hp (no trained L1/L2 needed)
            if hp.get(f) == "auto":
                hp[f] = {"param": "ve", "domain": "angle" if r == "L3" else "pixel", "arch": "mlp"}[f]
        hp["base"] = hp.get("base") if hp.get("base") != "auto" else "L1"
        m = make_model(r, hp, Nr, Nt).double().eval()
        for p in m.parameters():
            p.requires_grad_(False)
        if isinstance(m, VAEModel):
            m.freeze()
        if isinstance(m, ScoreModel):
            m.refresh_M()
        with torch.no_grad():
            L = float(m.loss(x, s, e)); nat = m.denoise_real(x, s); tw = tweedie_real(m, x, s)
        J = wirtinger(jac_batch(lambda v, u: tweedie_real(m, v, u), x, s))
        ga = float((tw - nat).norm(dim=-1).max() / nat.norm(dim=-1).max())
        tr = float(torch.diagonal(J, dim1=-2, dim2=-1).sum(-1).real.mean() / (Nr * Nt))
        print(f"   {r} {hp['arch']:>4}/{hp['param']:<3}/{hp['domain']:<5} | {n_params(m):>8} | {L:10.4e} | "
              f"{ga:9.2e} | {tr:+.4f} | {tuple(J.shape)}")
        out.append(ga)
    ok = max(out) <= 1e-9
    print(f"[selftest_rungs] worst Tweedie-vs-native over the six rungs: {max(out):.2e} -> "
          f"{'PASS' if ok else 'FAIL'}")
    return ok, out


if __name__ == "__main__":
    torch.manual_seed(0)
    a, _ = selftest_M5()
    b, _ = selftest_rungs()
    c, _ = selftest_gates()
    print(f"\nSELFTEST M5 {'PASS' if a else 'FAIL'} | RUNGS {'PASS' if b else 'FAIL'} | "
          f"GATES {'PASS' if c else 'FAIL'}")
    raise SystemExit(0 if (a and b and c) else 1)
