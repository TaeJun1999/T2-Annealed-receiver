"""conf/code/arch_dit.py -- DiT (Peebles & Xie 2023) backbone for the score ladder (04_SPEC §4, L4-class
architecture ablation).  ONE class, DiT, with the same call signature as score.py::_Conv / _UNet:

    net = DiT(Nr, Nt, width, depth, emb, circular=False, patch=1, heads=4)
    eps_hat = net(x, logsig)         # x (..., 2*Nr*Nt) -> same shape

so it drops straight into score.py::make_model's `net` slot and is wrapped by ScoreModel exactly like the
MLP / conv / U-Net rungs.  Nothing about the parameterisation (ve/vp/rf), the domain (pixel/angle) or the
training regime lives here -- this file is only the backbone.

WHY A *SMALL* DiT IS THE RIGHT TRANSPLANT HERE, AND WHAT WAS DROPPED
  The object is a MIMO channel prior, not an image: H is (Nr x Nt) with Nr in {4,8}, Nt = 4, i.e. 32 or 16
  spatial positions and 2 real channels, with 9000 training samples TOTAL (04_SPEC §2, fixed budget).
  Consequences, all of them deliberate:
    * patch=1.  A ViT patchifies to cut an image's token count; here the whole array is already only
      Nr*Nt <= 32 tokens, so the default is one token per antenna pair and no information is pooled away.
      patch=2 (8 tokens for 8x4, 4 for 4x4) is supported and asserted to divide the grid, as a cheaper
      variant, not as the default.
    * NO patch-embedding pretraining, no class labels, no CFG, no multi-resolution: DiT-XL's scaling story
      does not transfer to 9000 samples.  What DOES transfer is adaLN-Zero -- the per-block scale/shift/GATE
      regressed from the conditioning embedding with the gate zero-initialised, so the network starts as the
      identity map and the data budget is spent on deviations from it instead of on learning to be harmless.
      That is DiT's actual contribution over a plain ViT and it is implemented in full below.
    * width/depth are the ladder's retry axes (04_SPEC §4); the sensible range here is width 64-192,
      depth 4-6, i.e. 0.2M-2M parameters, not 100M+.

POSITIONAL EMBEDDING: LEARNED (nn.Parameter table over the Nr*Nt grid), not fixed 2D sin-cos.
  A 2D sin-cos embedding encodes "distance in the grid" and pays off when the signal is approximately
  translation-invariant, which an image is and an antenna array is NOT: position (0,0) is a specific
  physical element pair, the Rx axis (Nr up to 8, ULA aperture) and the Tx axis (Nt = 4) are not
  interchangeable, and in the ANGLE domain a token is a specific (DFT bin r, DFT bin t) pair whose statistics
  depend on the absolute bin, not on bin differences.  With at most 32 positions a free table costs
  32*width parameters (2048 at width 64) -- cheaper than justifying an inductive bias the geometry does not
  have.  It is zero-initialised so that the model starts from "no positional information" and buys position
  dependence only where the data pays for it.

`circular` is accepted for signature compatibility with _Conv/_UNet and is RECORDED, not silently reused:
  self-attention is global and permutation-free, so there is no padding mode to switch -- a DFT-bin wrap
  imposes no constraint on an all-to-all token mixer, and the learned position table can represent wrap-around
  structure by itself.  The flag is kept in the module (and in its repr) so a checkpoint's configuration is
  still fully described.

LAYOUT.  h = vec(H) is COLUMN-MAJOR, h[i + Nr*j] = H[i,j]; the reshape/transpose pair below is copied
verbatim from score.py::_Conv.forward so that every rung sees the same tensor in the same place.
Arbitrary leading dims are supported (the Jacobian code vmaps over a batch axis): the leading dims are
flattened to one batch axis for the attention and restored on the way out.

ZERO-INIT.  The final linear (and the final adaLN modulation) are zero-initialised, so at init the module
outputs EXACTLY 0 -- the identity denoiser -- as _Conv/_UNet do.
"""
import math
import os

import torch
import torch.nn as nn

# module-level (not from-import) so that this file is safe to import from score.py itself: _TimeEmb is
# looked up when a DiT is CONSTRUCTED, not while either module is still executing.
import score


def _modulate(x, shift, scale):
    """adaLN: x * (1 + scale) + shift, with (B, 1, W) conditioning broadcast over tokens."""
    return x * (1.0 + scale.unsqueeze(-2)) + shift.unsqueeze(-2)


class _Attn(nn.Module):
    """Multi-head self-attention over the Nr*Nt tokens.  No mask, no dropout (determinism is a gate
    requirement and there is no overfitting regulariser here beyond the small width)."""

    def __init__(self, width, heads):
        super().__init__()
        assert width % heads == 0, f"width {width} must be divisible by heads {heads}"
        self.h, self.dh = heads, width // heads
        self.qkv = nn.Linear(width, 3 * width)
        self.proj = nn.Linear(width, width)

    def forward(self, x):                                   # (B, T, W)
        B, T, W = x.shape
        q, k, v = self.qkv(x).reshape(B, T, 3, self.h, self.dh).permute(2, 0, 3, 1, 4)
        # explicit softmax attention rather than F.scaled_dot_product_attention: T <= 32, so the fused
        # kernel buys nothing, and it has no vmap batching rule (the gates take Jacobians through
        # torch.func.vmap in float64, where the fused path falls back with a warning anyway).
        a = torch.softmax(q @ k.transpose(-2, -1) / math.sqrt(self.dh), dim=-1)
        o = a @ v                                           # (B, h, T, dh)
        return self.proj(o.transpose(1, 2).reshape(B, T, W))


class _Block(nn.Module):
    """Pre-norm DiT block with adaLN-Zero.  One linear regresses all six modulation vectors
    (shift/scale/gate for attention and for the MLP) from the conditioning vector; it is zero-initialised,
    so at init scale = shift = 0 AND gate = 0 and the block is exactly the identity."""

    def __init__(self, width, heads, mlp_ratio=4):
        super().__init__()
        self.n1 = nn.LayerNorm(width, elementwise_affine=False, eps=1e-6)
        self.attn = _Attn(width, heads)
        self.n2 = nn.LayerNorm(width, elementwise_affine=False, eps=1e-6)
        self.mlp = nn.Sequential(nn.Linear(width, mlp_ratio * width), nn.GELU(approximate="tanh"),
                                 nn.Linear(mlp_ratio * width, width))
        self.ada = nn.Sequential(nn.SiLU(), nn.Linear(width, 6 * width))
        nn.init.zeros_(self.ada[-1].weight)
        nn.init.zeros_(self.ada[-1].bias)

    def forward(self, x, c):                                # x (B, T, W), c (B, W)
        sh1, sc1, g1, sh2, sc2, g2 = self.ada(c).chunk(6, dim=-1)
        x = x + g1.unsqueeze(-2) * self.attn(_modulate(self.n1(x), sh1, sc1))
        return x + g2.unsqueeze(-2) * self.mlp(_modulate(self.n2(x), sh2, sc2))


class DiT(nn.Module):
    """Diffusion Transformer over the (Nr, Nt) antenna grid, conditioned on log(sigma_t)."""

    def __init__(self, Nr, Nt, width, depth, emb, circular=False, patch=1, heads=4):
        super().__init__()
        assert Nr % patch == 0 and Nt % patch == 0, f"patch {patch} does not divide the {Nr}x{Nt} grid"
        assert width % heads == 0, f"width {width} must be divisible by heads {heads}"
        self.Nr, self.Nt, self.patch, self.heads, self.circular = Nr, Nt, patch, heads, circular
        self.gr, self.gt = Nr // patch, Nt // patch
        self.T = self.gr * self.gt                          # tokens
        self.cdim = 2 * patch * patch                       # reals per token
        self.temb = score._TimeEmb(emb)
        self.cond = nn.Sequential(nn.Linear(self.temb.dim, width), nn.SiLU(), nn.Linear(width, width))
        self.inp = nn.Linear(self.cdim, width)
        self.pos = nn.Parameter(torch.zeros(self.T, width))  # LEARNED, zero-init (see module docstring)
        self.blocks = nn.ModuleList(_Block(width, heads) for _ in range(depth))
        self.fn = nn.LayerNorm(width, elementwise_affine=False, eps=1e-6)
        self.fada = nn.Sequential(nn.SiLU(), nn.Linear(width, 2 * width))
        self.out = nn.Linear(width, self.cdim)
        for m in (self.fada[-1], self.out):                 # zero-init: the net outputs exactly 0 at init
            nn.init.zeros_(m.weight)
            nn.init.zeros_(m.bias)

    def extra_repr(self):
        return (f"Nr={self.Nr}, Nt={self.Nt}, patch={self.patch}, tokens={self.T}, heads={self.heads}, "
                f"circular={self.circular} (recorded; attention has no padding mode)")

    def _tokens(self, y):
        """(B, 2, Nr, Nt) -> (B, T, 2*p*p), patches in row-major (gr, gt) order."""
        p, B = self.patch, y.shape[0]
        y = y.reshape(B, 2, self.gr, p, self.gt, p).permute(0, 2, 4, 1, 3, 5)
        return y.reshape(B, self.T, self.cdim)

    def _grid(self, o):
        """inverse of _tokens."""
        p, B = self.patch, o.shape[0]
        o = o.reshape(B, self.gr, self.gt, 2, p, p).permute(0, 3, 1, 4, 2, 5)
        return o.reshape(B, 2, self.Nr, self.Nt)

    def forward(self, x, logsig):
        lead = x.shape[:-1]
        # column-major vec: h[i + Nr*j] = H[i,j] -> reshape (Nt, Nr) in C order, then transpose. (== _Conv)
        y = x.reshape(-1, 2, self.Nt, self.Nr).transpose(-1, -2)          # (B, 2, Nr, Nt)
        c = self.cond(self.temb(logsig.reshape(-1)))                      # (B, W)
        h = self.inp(self._tokens(y)) + self.pos
        for b in self.blocks:
            h = b(h, c)
        sh, sc = self.fada(c).chunk(2, dim=-1)
        o = self._grid(self.out(_modulate(self.fn(h), sh, sc)))           # (B, 2, Nr, Nt)
        return o.transpose(-1, -2).reshape(*lead, 2 * self.Nr * self.Nt)


# ----------------------------------------------------------------------------- self-test
def _selftest():
    torch.manual_seed(0)
    for Nr, Nt in ((8, 4), (4, 4)):
        dim = 2 * Nr * Nt
        for patch in (1, 2):
            net = DiT(Nr, Nt, 64, 4, 128, patch=patch).eval()
            print(f"  ({Nr}x{Nt}) patch={patch}: tokens={net.T} chan/token={net.cdim} "
                  f"params={sum(p.numel() for p in net.parameters())}")
            for lead in ((5,), (3, 4)):
                x = torch.randn(*lead, dim)
                ls = torch.randn(*lead)
                o = net(x, ls)
                assert o.shape == x.shape, (o.shape, x.shape)                       # 1. shape
                assert torch.count_nonzero(o) == 0, float(o.abs().max())            # 2. zero-init
                assert torch.equal(o, net(x, ls))                                   # 3. determinism
            # layout round-trip: tokenise/de-tokenise is the identity on the raw vector
            y = torch.randn(7, 2, Nr, Nt)
            assert torch.equal(net._grid(net._tokens(y)), y)
        for w in (64, 128, 192):
            net = DiT(Nr, Nt, w, 4, 128)
            print(f"  ({Nr}x{Nt}) width={w:3d} depth=4 heads=4 patch=1: "
                  f"params={sum(p.numel() for p in net.parameters())}")

        # 4. trainability: 200 full-batch Adam steps on a FIXED synthetic denoising task (predict eps from
        #    x0 + s*eps, x0 drawn through a random correlation A so there is structure to learn).  The
        #    threshold is 30%; this is a smoke test that gradients flow through adaLN-Zero, not a benchmark.
        g = torch.Generator().manual_seed(1)
        A = torch.randn(dim, dim, generator=g) / math.sqrt(dim)
        x0 = torch.randn(512, dim, generator=g) @ A.T
        x0 = x0 / x0.pow(2).mean().sqrt()
        eps = torch.randn(512, dim, generator=g)
        s = torch.full((512,), 1.0)
        xt, ls = x0 + s.unsqueeze(-1) * eps, torch.log(s)
        net = DiT(Nr, Nt, 64, 4, 128)
        opt = torch.optim.Adam(net.parameters(), lr=2e-3)
        l0 = None
        for i in range(200):
            loss = (net(xt, ls) - eps).pow(2).mean()
            opt.zero_grad(set_to_none=True); loss.backward(); opt.step()
            l0 = float(loss.detach()) if l0 is None else l0
        with torch.no_grad():
            l1 = float((net(xt, ls) - eps).pow(2).mean())
        print(f"  ({Nr}x{Nt}) train: loss {l0:.4f} -> {l1:.4f}  ({100 * (1 - l1 / l0):.1f}% reduction)")
        assert l1 <= 0.7 * l0, (l0, l1)
    print("arch_dit selftest OK")


if __name__ == "__main__":
    # The self-test is CPU-only by design (64 real dims); hiding CUDA keeps it runnable while the shared
    # GPUs are in Exclusive_Process use by a training run.  torch's CUDA init is lazy, so this takes effect.
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    _selftest()
