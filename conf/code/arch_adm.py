"""conf/code/arch_adm.py -- ADM-style U-Net backbone for the L4 architecture rung (04_SPEC §4).

WHAT THIS ADDS OVER score.py::_UNet (the plain U-Net already in the ladder)
  score.py::_UNet is a plain noise-conditional U-Net: GroupNorm + an ADDITIVE embedding term inside the
  residual block, no attention, no zero-initialised residual branch.  This file implements the three things
  Dhariwal & Nichol, "Diffusion Models Beat GANs on Image Synthesis" (NeurIPS 2021) actually contribute
  over that baseline, and nothing else, so that L4 vs L4-ADM is an architecture ablation with a named axis:

  1. adaGN / scale-shift normalisation.  The conditioning embedding does NOT enter as  h <- h + emb(t).
     It is regressed into a PAIR (scale, shift) per channel and applied as
         h <- GroupNorm(h) * (1 + scale) + shift
     (class _AdaResBlk, the `s, b = self.emb(t).chunk(2, -1)` line).  This is ADM §3 "adaptive group
     normalisation"; it is the single change ADM's own ablation credits with the largest FID gain.

  2. Self-attention at the coarse scale(s).  A block of multi-head self-attention over the array positions
     is inserted at every scale whose resolution (Nr_s * Nt_s POSITIONS) is <= `attn_at`.  With the default
     attn_at = 8:
         8x4 cell:  32 positions (no attn) -> 4x2 = 8 positions (ATTN) -> 2x1 = 2 positions (ATTN)
         4x4 cell:  16 positions (no attn) -> 2x2 = 4 positions (ATTN) -> 1x1 = 1 position  (ATTN)
     so the encoder/decoder second scale and the bottleneck get it.  8 tokens of width 4*width is a
     rounding error in FLOPs here, which is the whole reason attention is affordable on this problem:
     convolution on a 4-wide aperture can only ever mix neighbours, while the Kronecker structure of this
     prior is a GLOBAL correlation across the aperture.  Attention at 1 position (4x4 bottleneck) is
     mathematically a per-position linear map -- it is kept only so the two array sizes run identical code;
     it is reported as "degenerate" rather than as a working attention site.

  3. Residual blocks with a ZERO-INITIALISED second convolution (ADM's `zero_module(conv_out)`).  Every
     _AdaResBlk starts as the exact identity, so a deeper stack costs nothing at init and the network is
     the identity denoiser at step 0 -- the same reason score.py zero-inits its output projection.
     [deliberately skipped] BigGAN-style up/down sampling INSIDE the residual block.  At this size the whole
     network contains 1-2 down-samplings of a 4-wide axis; moving the resample into the residual branch
     changes only which of two 3x3 convolutions carries the stride, adds parameters, and cannot pay for
     itself on 9000 training samples.  Down/up stay as a strided conv / nearest-upsample + conv, i.e.
     IDENTICAL to score.py::_UNet, so items 1-3 above are the only difference between the two U-Nets.

SIZING FOR THIS PROBLEM (not image diffusion)
  x is 2*Nr*Nt reals -- 64 for the 8x4 headline cell, 32 for 4x4 -- and the data budget is FIXED at
  9000 train / 1000 val (04_SPEC §2).  So: no extra scales, no wide attention head count, no pretraining.
  n_down = min(2, floor(log2(min(Nr, Nt)))), the SAME rule score.py::_UNet uses, so the two are comparable:
      8x4 -> 4x2 -> 2x1        4x4 -> 2x2 -> 1x1
  Prefer the narrow configurations at this data budget.  Measured against score.py::_UNet at depth 4
  (8x4; the 4x4 counts are identical because n_down = 2 either way and conv weights do not see extent):
      width 32:  _UNet 1,058,914   ADMUNet 1,267,746      (+19.7%: adaGN doubles the emb Linear, +2 attn)
      width 48:  _UNet 2,366,354   ADMUNet 2,834,738
      width 64:  _UNet 4,192,450   ADMUNet 5,023,810
  score.py's ATTEMPT_HP already drops L4u attempt 2 to width 32 for exactly this reason (9000 samples);
  an ADM rung should start no wider than that.

LAYOUT (copied verbatim from score.py::_Conv.forward -- get this wrong and every gate number is wrong)
  h = vec(H) is COLUMN-MAJOR, h[i + Nr*j] = H[i,j], so the real vector reshapes as (2, Nt, Nr) in C order
  and is then transposed to (2, Nr, Nt).  forward() accepts ARBITRARY leading dims (the D-14 Jacobian code
  vmaps over a batch axis); the leading dims are flattened into the conv batch axis and restored on exit,
  because nn.Conv2d takes exactly one batch dim.

  padding_mode follows _Conv / _UNet: 'circular' in the ANGLE domain (DFT bins wrap), 'zeros' in pixel --
  EXCEPT on a feature map with a spatial extent of 1, where torch requires pad < dim and circular padding
  is impossible; those scales fall back to 'zeros' (2x1 and 1x1 bottlenecks).
"""
import math
import os
import sys

import torch
import torch.nn as nn
import torch.nn.functional as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from score import _TimeEmb, _gn                      # noqa: E402  (same Fourier embedding as the whole ladder)


class _Attn(nn.Module):
    """Multi-head self-attention over the Nr*Nt array positions, ADM's QKV attention block.
    Pre-norm GroupNorm, a 1x1 QKV projection, and a ZERO-INITIALISED output projection so the block starts
    as the identity.  `heads` is reduced until it divides the channel count."""

    def __init__(self, c, heads):
        super().__init__()
        while c % heads:
            heads -= 1
        self.heads = heads
        self.norm = _gn(c)
        self.qkv = nn.Conv1d(c, 3 * c, 1)
        self.proj = nn.Conv1d(c, c, 1)
        nn.init.zeros_(self.proj.weight)
        nn.init.zeros_(self.proj.bias)

    def forward(self, x):
        b, c, H, W = x.shape
        n, d = H * W, c // self.heads
        q, k, v = self.qkv(self.norm(x).reshape(b, c, n)).reshape(b, 3, self.heads, d, n).unbind(1)
        # written out rather than F.scaled_dot_product_attention: SDPA has no torch.func batching rule, so
        # it makes the vmap'd Jacobian of gate GD fall back to a loop.  n <= 8 tokens -- this costs nothing.
        w = torch.softmax(torch.einsum("bhdi,bhdj->bhij", q, k) / math.sqrt(d), dim=-1)
        a = torch.einsum("bhij,bhdj->bhdi", w, v).reshape(b, c, n)
        return x + self.proj(a).reshape(b, c, H, W)


class _AdaResBlk(nn.Module):
    """ADM residual block: GroupNorm -> SiLU -> conv, then adaGN scale-shift from the conditioning
    embedding, then SiLU -> ZERO-INIT conv.  The scale-shift is the point (item 1 of the module docstring):
        h = norm(h) * (1 + scale) + shift,   (scale, shift) = Linear(emb).chunk(2)
    NOT  h = h + Linear(emb), which is what score.py::_ResBlk does."""

    def __init__(self, cin, cout, tdim, pm):
        super().__init__()
        self.n1, self.c1 = _gn(cin), nn.Conv2d(cin, cout, 3, padding=1, padding_mode=pm)
        self.emb = nn.Linear(tdim, 2 * cout)                       # -> (scale, shift)
        self.n2, self.c2 = _gn(cout), nn.Conv2d(cout, cout, 3, padding=1, padding_mode=pm)
        self.skip = nn.Conv2d(cin, cout, 1) if cin != cout else nn.Identity()
        nn.init.zeros_(self.c2.weight)                             # ADM zero_module: block starts as identity
        nn.init.zeros_(self.c2.bias)

    def forward(self, x, t):
        h = self.c1(F.silu(self.n1(x)))
        s, b = self.emb(t).reshape(*t.shape[:-1], -1, 1, 1).chunk(2, dim=-3)
        h = self.n2(h) * (1.0 + s) + b                             # <-- adaGN
        return self.c2(F.silu(h)) + self.skip(x)


class ADMUNet(nn.Module):
    """ADM-style U-Net over the (Nr, Nt) array grid.  Drop-in for score.py's backbones: same constructor
    shape as _UNet plus (heads, attn_at), same forward(x, logsig) contract, same column-major layout,
    zero output at init.

        __init__(Nr, Nt, width, depth, emb, circular=False, heads=4, attn_at=8)
        forward(x, logsig)      x (..., 2*Nr*Nt) -> (..., 2*Nr*Nt);  logsig shape == x.shape[:-1]

    `attn_at` is a POSITION count: a scale of shape (h, w) gets self-attention iff h*w <= attn_at.
    self.attn_scales lists the scales that actually got it (for the report / the LADDER.md line)."""

    def __init__(self, Nr, Nt, width, depth, emb, circular=False, heads=4, attn_at=8):
        super().__init__()
        self.Nr, self.Nt = Nr, Nt
        self.temb = _TimeEmb(emb)
        tdim = 4 * width
        self.tproj = nn.Sequential(nn.Linear(self.temb.dim, tdim), nn.SiLU(), nn.Linear(tdim, tdim))

        n_down = min(2, int(math.log2(min(Nr, Nt))))               # same rule as score.py::_UNet
        chs = [width * (2 ** min(i, 2)) for i in range(n_down + 1)]
        shapes = [(Nr >> i, Nt >> i) for i in range(n_down + 1)]
        per = max(1, depth // max(n_down + 1, 1))                  # residual blocks per scale
        # circular padding needs pad < dim; a spatial extent of 1 (2x1, 1x1) cannot wrap.
        pmode = ["circular" if (circular and min(s) >= 2) else "zeros" for s in shapes]
        self.attn_scales = [f"{h}x{w}" for (h, w) in shapes if h * w <= attn_at]
        use_attn = [h * w <= attn_at for (h, w) in shapes]

        self.inp = nn.Conv2d(2, chs[0], 3, padding=1, padding_mode=pmode[0])
        self.enc, self.enc_attn, self.down = nn.ModuleList(), nn.ModuleList(), nn.ModuleList()
        for i in range(n_down):
            self.enc.append(nn.ModuleList(_AdaResBlk(chs[i], chs[i], tdim, pmode[i]) for _ in range(per)))
            self.enc_attn.append(_Attn(chs[i], heads) if use_attn[i] else nn.Identity())
            self.down.append(nn.Conv2d(chs[i], chs[i + 1], 3, stride=2, padding=1, padding_mode=pmode[i]))
        self.mid1 = _AdaResBlk(chs[-1], chs[-1], tdim, pmode[-1])
        self.mid_attn = _Attn(chs[-1], heads) if use_attn[-1] else nn.Identity()
        self.mid2 = nn.ModuleList(_AdaResBlk(chs[-1], chs[-1], tdim, pmode[-1]) for _ in range(max(1, per - 1)))
        self.upc, self.dec, self.dec_attn = nn.ModuleList(), nn.ModuleList(), nn.ModuleList()
        for i in reversed(range(n_down)):
            self.upc.append(nn.Conv2d(chs[i + 1], chs[i], 3, padding=1, padding_mode=pmode[i]))
            self.dec.append(nn.ModuleList([_AdaResBlk(2 * chs[i], chs[i], tdim, pmode[i])]
                                          + [_AdaResBlk(chs[i], chs[i], tdim, pmode[i]) for _ in range(per - 1)]))
            self.dec_attn.append(_Attn(chs[i], heads) if use_attn[i] else nn.Identity())
        self.outn = _gn(chs[0])
        self.out = nn.Conv2d(chs[0], 2, 3, padding=1, padding_mode=pmode[0])
        nn.init.zeros_(self.out.weight)                            # required: identity denoiser at init
        nn.init.zeros_(self.out.bias)

    def forward(self, x, logsig):
        lead = x.shape[:-1]
        n = 1
        for d in lead:
            n *= d
        # column-major vec: h[i + Nr*j] = H[i,j]  ->  reshape (Nt, Nr) in C order, then transpose.
        y = x.reshape(*lead, 2, self.Nt, self.Nr).transpose(-1, -2).reshape(n, 2, self.Nr, self.Nt)
        t = self.tproj(self.temb(logsig)).reshape(n, -1)
        h = self.inp(y)
        skips = []
        for blks, at, dn in zip(self.enc, self.enc_attn, self.down):
            for b in blks:
                h = b(h, t)
            h = at(h)
            skips.append(h)
            h = dn(h)
        h = self.mid_attn(self.mid1(h, t))
        for b in self.mid2:
            h = b(h, t)
        for uc, blks, at in zip(self.upc, self.dec, self.dec_attn):
            h = uc(F.interpolate(h, scale_factor=2, mode="nearest"))
            h = torch.cat([h, skips.pop()], dim=-3)
            for b in blks:
                h = b(h, t)
            h = at(h)
        o = self.out(F.silu(self.outn(h)))
        return o.reshape(*lead, 2, self.Nr, self.Nt).transpose(-1, -2).reshape(*lead, 2 * self.Nr * self.Nt)


# ----------------------------------------------------------------------------- self-test
def _selftest(Nr, Nt, width=32, depth=4, emb=128, B=32, K=3, steps=200, seed=0):
    torch.manual_seed(seed)
    dim = 2 * Nr * Nt
    m = ADMUNet(Nr, Nt, width, depth, emb)
    npar = sum(p.numel() for p in m.parameters())
    print(f"  {Nr}x{Nt} width={width} depth={depth}: {npar} params | "
          f"attention at {m.attn_scales} (of {[f'{Nr>>i}x{Nt>>i}' for i in range(len(m.enc) + 1)]})")
    m.eval()

    # 1. shape, for lead = (B,) and lead = (B, K)
    for lead in [(B,), (B, K)]:
        x, ls = torch.randn(*lead, dim), torch.randn(*lead)
        y = m(x, ls)
        assert y.shape == x.shape, (y.shape, x.shape)
        # 2. zero-init
        assert torch.equal(y, torch.zeros_like(y)), f"not zero at init, max |y| = {y.abs().max()}"
        # 3. determinism
        assert torch.equal(m(x, ls), y)

    # 3b. determinism once the weights are NOT all-zero-output (the check above is vacuous at init)
    with torch.no_grad():
        m.out.weight.normal_(0, 0.02)
    x, ls = torch.randn(B, dim), torch.randn(B)
    assert torch.equal(m(x, ls), m(x, ls)), "non-deterministic in eval mode"

    # 4. trainability: fixed synthetic denoising task, 200 Adam steps, loss must drop >= 30%
    torch.manual_seed(seed + 1)
    m = ADMUNet(Nr, Nt, width, depth, emb)
    A = torch.randn(dim, dim) / math.sqrt(dim)
    x0 = torch.randn(256, dim) @ A.T                       # correlated "channels"
    sig = torch.exp(torch.rand(256) * 2.0 - 2.0)
    eps = torch.randn(256, dim)
    xt = x0 + sig.unsqueeze(-1) * eps
    opt = torch.optim.Adam(m.parameters(), lr=2e-3)
    m.train()
    losses = []
    for _ in range(steps):
        loss = ((m(xt, torch.log(sig)) - eps) ** 2).mean()
        opt.zero_grad(set_to_none=True); loss.backward(); opt.step()
        losses.append(float(loss.detach()))
    l0, l1 = sum(losses[:5]) / 5, sum(losses[-5:]) / 5
    print(f"       trainability: loss {l0:.4f} -> {l1:.4f}  ({100 * (1 - l1 / l0):.1f}% reduction)")
    assert l1 <= 0.7 * l0, f"loss only fell {100 * (1 - l1 / l0):.1f}%, need >= 30%"
    return npar


if __name__ == "__main__":
    # The self-test is CPU-only by design (tiny tensors).  Hide the GPUs so it cannot fail with
    # "CUDA-capable device(s) is/are busy" when the machine's GPUs are in Exclusive_Process use.
    os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
    print("ADMUNet self-test")
    for Nr, Nt in ((8, 4), (4, 4)):
        for w in (32, 48, 64):
            _selftest(Nr, Nt, width=w)
    print("all assertions passed")
