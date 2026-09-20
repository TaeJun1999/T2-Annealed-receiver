"""conf/code/arch_uvit.py -- U-ViT backbone (Bao et al., "All are Worth Words: A ViT Backbone for
Diffusion Models") as a drop-in `net` for score.py::ScoreModel, i.e. one more architecture for the
L4 rung of 04_SPEC_diffusion.md §4 under the SAME frozen gates GA-GD.

WHY THIS IS A DIFFERENT ARM FROM DiT (the thing that justifies spending a rung on it)
  Two design choices distinguish U-ViT from DiT, and both are implemented here literally:
  1. LONG SKIP CONNECTIONS between shallow and deep blocks.  The blocks are split
     encoder / middle / decoder; decoder block i consumes concat(h, encoder_skip) followed by a linear
     back down to `width`.  This is the U-Net-in-a-transformer part and it is the paper's headline
     ablation (removing it is what hurts most).  `self.use_long_skips` exists ONLY so a test can turn
     them off and show the output moves -- it is not a configuration knob.
  2. The conditioning is a TOKEN, not adaLN.  log(sigma_t) is embedded once and PREPENDED as an extra
     token, so it is mixed into the sequence by attention.  DiT instead modulates every LayerNorm with
     adaLN-zero.  Keeping the U-ViT choice is what makes this arm genuinely different from the DiT file
     rather than a re-skin of it.

WHY THE PARAMETER-EFFICIENT VARIANT (04_SPEC §2: N_train = 9000, and that budget is FIXED)
  The input is 2*Nr*Nt = 64 reals for the 8x4 headline cell (32 for 4x4).  With patch = 1 that is
  Nr*Nt = 32 spatial tokens + 1 time token -- already a full-length sequence, so there is nothing to gain
  from patching up (patch > 1 is supported but only shortens an already short sequence) and nothing to
  gain from multi-scale: a ViT has one scale by construction, which is precisely why it survives a
  4-wide transmit axis where a deep U-Net cannot down-sample.  Depth and width are kept small
  (width 64, depth 5 => ~0.3M parameters) because 9000 samples is the whole data budget; a
  web-scale-pretrained ViT configuration does not transfer to this problem and is not offered.

CONVENTIONS COPIED VERBATIM FROM score.py::_Conv (do not "simplify" these two lines)
  h = vec(H) is COLUMN-MAJOR, h[i + Nr*j] = H[i,j], so the real 2-channel grid is recovered as
      x.reshape(..., 2, Nt, Nr).transpose(-1, -2)   ->  (..., 2, Nr, Nt)
  and written back with the mirrored transpose+reshape.  Any other order silently permutes the array
  geometry and every gate number downstream is wrong.
  padding_mode of the output conv follows _Conv: 'circular' in the ANGLE domain (DFT bins wrap),
  'zeros' in the pixel domain (a ULA aperture does not wrap).

Final-layer zero-init: the 3x3 output conv (U-ViT adds it to suppress patch artefacts) has zero weight
AND zero bias, so the network outputs exactly 0 at init and ScoreModel starts at the identity denoiser
-- the same contract _Conv / _UNet obey.

forward(x, logsig) accepts ARBITRARY leading dims (jac_batch vmaps over the sample axis, which removes
the batch dim entirely -> lead = ()).  Everything is flattened to one batch axis internally.
"""
import math

import torch
import torch.nn as nn


def _time_emb(emb):
    """score.py::_TimeEmb, imported lazily: score.py may import this module, and a deferred import is the
    cheapest way to stay cycle-proof whichever order the orchestrator wires them in."""
    from score import _TimeEmb
    return _TimeEmb(emb)


class _Attn(nn.Module):
    """Plain multi-head self-attention.  Written out as explicit softmax(QK^T/sqrt(d))V instead of
    nn.MultiheadAttention / scaled_dot_product_attention because this runs under
    torch.func.vmap(jacrev(...)) in the GD gate path: the fused SDPA kernels have no CPU batching rule
    and fall back (slowly and noisily), while plain matmul+softmax is transform-native."""

    def __init__(self, width, heads):
        super().__init__()
        assert width % heads == 0, f"width {width} not divisible by heads {heads}"
        self.h = heads
        self.qkv = nn.Linear(width, 3 * width)
        self.proj = nn.Linear(width, width)

    def forward(self, z):                                   # z: (B, T, W)
        B, T, W = z.shape
        q, k, v = self.qkv(z).reshape(B, T, 3, self.h, W // self.h).permute(2, 0, 3, 1, 4)
        a = torch.softmax(q @ k.transpose(-1, -2) / math.sqrt(q.shape[-1]), -1) @ v   # (B, h, T, W/h)
        return self.proj(a.transpose(1, 2).reshape(B, T, W))


class _Blk(nn.Module):
    """Pre-norm transformer block, MLP ratio 4 (U-ViT Table 1)."""

    def __init__(self, width, heads):
        super().__init__()
        self.n1, self.attn = nn.LayerNorm(width), _Attn(width, heads)
        self.n2 = nn.LayerNorm(width)
        self.mlp = nn.Sequential(nn.Linear(width, 4 * width), nn.GELU(), nn.Linear(4 * width, width))

    def forward(self, z):
        z = z + self.attn(self.n1(z))
        return z + self.mlp(self.n2(z))


class UViT(nn.Module):
    """U-ViT over the (Nr, Nt) array grid, 2 real channels.

    depth is rounded UP to an odd number so that there is a genuine middle block:
        n = depth // 2 encoder blocks | 1 bottleneck block | n decoder blocks,
    decoder block i receiving concat(h, skip from encoder block n-1-i) -> Linear(2W, W) -> block.
    """

    def __init__(self, Nr, Nt, width, depth, emb, circular=False, patch=1, heads=4):
        super().__init__()
        assert Nr % patch == 0 and Nt % patch == 0, f"patch {patch} does not divide the {Nr}x{Nt} grid"
        self.Nr, self.Nt, self.p = Nr, Nt, patch
        self.Gr, self.Gt = Nr // patch, Nt // patch
        self.depth = depth if depth % 2 else depth + 1      # round UP to odd -> a middle block exists
        n = self.depth // 2
        pm = "circular" if circular else "zeros"

        self.temb = _time_emb(emb)
        self.cond = nn.Sequential(nn.Linear(self.temb.dim, width), nn.SiLU(), nn.Linear(width, width))
        self.patch_embed = nn.Conv2d(2, width, patch, stride=patch)
        self.pos = nn.Parameter(torch.zeros(1, 1 + self.Gr * self.Gt, width))   # learned, incl. time token
        nn.init.trunc_normal_(self.pos, std=0.02)

        self.enc = nn.ModuleList(_Blk(width, heads) for _ in range(n))
        self.mid = _Blk(width, heads)
        self.dec = nn.ModuleList(_Blk(width, heads) for _ in range(n))
        self.skip_proj = nn.ModuleList(nn.Linear(2 * width, width) for _ in range(n))
        self.use_long_skips = True                          # test hook (see module docstring), not a knob

        self.norm = nn.LayerNorm(width)
        self.head = nn.Linear(width, 2 * patch * patch)
        self.out = nn.Conv2d(2, 2, 3, padding=1, padding_mode=pm)
        nn.init.zeros_(self.out.weight); nn.init.zeros_(self.out.bias)          # exact 0 at init

    def forward(self, x, logsig):
        lead = x.shape[:-1]
        # column-major vec: h[i + Nr*j] = H[i,j]  ->  reshape (Nt, Nr) in C order, then transpose.  [_Conv]
        y = x.reshape(-1, 2, self.Nt, self.Nr).transpose(-1, -2)                # (B, 2, Nr, Nt)
        t = self.cond(self.temb(logsig)).reshape(y.shape[0], 1, -1)             # the conditioning TOKEN
        z = self.patch_embed(y).flatten(2).transpose(1, 2)                      # (B, Gr*Gt, W), row-major
        z = torch.cat([t, z], 1) + self.pos

        skips = []
        for b in self.enc:
            z = b(z)
            skips.append(z)

        z = self.mid(z)
        for b, pr in zip(self.dec, self.skip_proj):
            s = skips.pop()
            z = pr(torch.cat([z, s if self.use_long_skips else torch.zeros_like(s)], -1))
            z = b(z)

        h = self.head(self.norm(z[:, 1:]))                                      # drop the time token
        h = h.reshape(-1, self.Gr, self.Gt, 2, self.p, self.p).permute(0, 3, 1, 4, 2, 5)
        h = self.out(h.reshape(-1, 2, self.Nr, self.Nt))
        return h.transpose(-1, -2).reshape(*lead, 2 * self.Nr * self.Nt)


# ----------------------------------------------------------------------------- self-test
def _selftest():
    torch.manual_seed(0)
    ok = True
    for Nr, Nt in ((8, 4), (4, 4)):
        dim = 2 * Nr * Nt
        for width, depth, patch in ((64, 5, 1), (32, 5, 1), (64, 4, 2)):
            m = UViT(Nr, Nt, width, depth, 128, circular=(patch == 1), patch=patch).eval()
            tag = f"{Nr}x{Nt} w{width} d{depth}(->{m.depth}) p{patch}"
            print(f"[{tag}] params = {sum(p.numel() for p in m.parameters()):,}")

            # 1. shape, for lead = (B,) and lead = (B, K)   2. exact zero at init   3. determinism
            for lead in ((7,), (3, 5), ()):
                x, ls = torch.randn(lead + (dim,)), torch.randn(lead)
                o = m(x, ls)
                assert o.shape == x.shape, f"{tag} lead {lead}: {tuple(o.shape)} != {tuple(x.shape)}"
                assert torch.equal(o, torch.zeros_like(o)), f"{tag} lead {lead}: not zero at init"
                assert torch.equal(o, m(x, ls)), f"{tag} lead {lead}: not deterministic"

            # vmap(jacrev) is how the GD gate calls this net (score.py::jac_batch) -- fail here, not there.
            J = torch.func.vmap(torch.func.jacrev(m))(torch.randn(3, dim), torch.randn(3))
            assert J.shape == (3, dim, dim), f"{tag}: jac_batch shape {tuple(J.shape)}"

            # 4. trainability: 200 Adam steps on a fixed synthetic denoising task
            g = torch.Generator().manual_seed(1)
            A = torch.randn(dim, 6, generator=g) / math.sqrt(6)
            x0 = (torch.randn(256, 6, generator=g) @ A.T)
            eps = torch.randn(256, dim, generator=g)
            u = torch.rand(256, generator=g)
            sig = torch.exp(math.log(0.05) + u * (math.log(2.0) - math.log(0.05)))
            xt, ls = x0 + sig[:, None] * eps, torch.log(sig)
            m.train()
            opt = torch.optim.Adam(m.parameters(), lr=1e-3)
            l0 = None
            for _ in range(200):
                loss = ((m(xt, ls) - eps) ** 2).mean()
                l0 = loss.item() if l0 is None else l0
                opt.zero_grad(); loss.backward(); opt.step()
            l1 = ((m(xt, ls) - eps) ** 2).mean().item()
            drop = 1.0 - l1 / l0
            good = drop >= 0.30
            ok &= good
            print(f"[{tag}] loss {l0:.4f} -> {l1:.4f}  ({100 * drop:.1f}% down)  {'PASS' if good else 'FAIL'}")

            # long skips actually wired: ablating them must move a TRAINED model's output
            m.eval()
            with torch.no_grad():
                a = m(xt[:4], ls[:4])
                m.use_long_skips = False
                b = m(xt[:4], ls[:4])
                m.use_long_skips = True
            d = ((a - b).norm() / a.norm()).item()
            wired = d > 1e-3
            ok &= wired
            print(f"[{tag}] long-skip ablation: rel change {d:.4f}  {'WIRED' if wired else 'NOT WIRED'}")
    print("SELFTEST", "PASS" if ok else "FAIL")
    return ok


if __name__ == "__main__":
    raise SystemExit(0 if _selftest() else 1)
