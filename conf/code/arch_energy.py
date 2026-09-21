"""conf/code/arch_energy.py -- Stage C variant V2 (10_SPEC_stageC.md §3b): the score as the gradient of a
SCALAR energy, so that the denoiser Jacobian is a Hessian and therefore SYMMETRIC BY CONSTRUCTION.

WHY.  For a true posterior-mean denoiser under real Gaussian noise of std sigma,
    Jr = d m_real / dx = Cov_real(h|q) / sigma^2                      -> symmetric, and PSD.
A network whose eps-head is an arbitrary R^2N -> R^2N map carries no such guarantee.  Measured on D2
(results/diag/jacobian-psd_D2.npz): 255/256 indefinite site covariances for the trained prior against
0/256 for the exact GMM, and RouteAClip._matrix_site then floors Lam while eta still comes from the
UNCLIPPED SigH, so the belief mean lands 6-8 orders of magnitude off and the receiver diverges.

WHAT CHANGES.  Only the OUTPUT HEAD.  The trunk stays the frozen Stage C recipe (dit / vp / angle,
width 64, depth 6, heads 8, patch 1, emb 256) and its per-token Linear(width -> 2*patch^2) is replaced
by a per-token Linear(width -> 1) SUMMED over tokens into one scalar Phi(x, log sigma).  forward()
returns grad_x Phi, so every consumer downstream is untouched and, with sa = sqrt(abar),
sb = sqrt(1-abar) of ScoreModel._vp and M the orthogonal angle-domain transform,

    eps_hat(u) = grad_u Phi(u)                                        gradient field
    raw(x)     = M^T (grad Phi)(M x) = grad_x [ Phi(M x) ]            M orthogonal -> still a gradient field
    score_real = -(sa/sb) eps_hat(sa x) = -grad_x E,   E = (1/sb) Phi(sa x)
                 [reviewer 2026-09-21: the potential is Phi/sb, NOT (sa/sb)Phi -- grad_x Phi(sa M x)
                  = sa * raw(sa x) already carries one factor sa.  Verified by central FD on the live
                  checkpoint: ||score_real + grad E||/||score_real|| = 3.4e-09 for (1/sb)Phi versus
                  1.9e-02 = 1 - sa for (sa/sb)Phi.  COMMENT ONLY -- no code formed E, so nothing that
                  was run or measured is affected, and the Hessian line below was already correct.]
    d score_real / dx = -(sa^2/sb) Hess Phi                           SYMMETRIC to machine precision
    d tweedie_real/dx = I + sigma^2 * (that)                          SYMMETRIC

THE OBJECTIVE IS UNCHANGED.  ScoreModel.loss('vp') still fits ||eps_hat - eps||^2, the same denoising
score-matching loss the frozen recipe uses.  This is a restriction to the correct function class, not a
new objective: the true eps-head IS a gradient field, eps* = -sigma * grad_x log p_sigma(x).

SYMMETRY IS NOT PSD.  V2 forces J = J^T; it does not force J >= 0.  Whether the remaining negative
eigenvalues still break the site is a MEASUREMENT (conf/code/jacobian_psd.py), and 10_SPEC_stageC.md
§3b pre-commits to reporting it either way.

WHY torch.func.grad AND NOT torch.autograd.grad.  The four consumers compose differently:
  score.jac_batch        vmap(jacrev(.))            -- gates GD, jacobian_psd.py
  ScorePrior._eval       jacrev(.)                  -- the receiver, one sample, lead shape ()
  score._gate_batch      under torch.no_grad()      -- denoise_real / tweedie_real
  score.train            backward() into the params -- needs the gradient itself to be differentiable
torch.autograd.grad has no batching rule under vmap and needs requires_grad on the input; torch.func.grad
survives all four.  _selftest() below exercises every one of them.
"""
import math
import os

import torch
import torch.nn as nn

import arch_dit


class EnergyDiT(arch_dit.DiT):
    """The frozen DiT trunk with a SCALAR head.  forward(x, logsig) = grad_x energy(x, logsig)."""

    def __init__(self, Nr, Nt, width, depth, emb, circular=False, patch=1, heads=4):
        super().__init__(Nr, Nt, width, depth, emb, circular=circular, patch=patch, heads=heads)
        del self.out                                    # the vector head V2 replaces
        self.ehead = nn.Linear(width, 1)                # per-token scalar; Phi = sum over tokens
        nn.init.zeros_(self.ehead.weight)               # Phi == 0 at init => eps_hat == 0, exactly as
        nn.init.zeros_(self.ehead.bias)                 # DiT's zero-init vector head (identity denoiser)

    def extra_repr(self):
        return super().extra_repr() + ", head=energy (forward returns grad_x E)"

    def energy(self, x, logsig):
        """(..., 2N) -> (...).  The body is arch_dit.DiT.forward verbatim up to its head, so the trunk is
        the frozen one; only the final Linear and the token sum differ."""
        lead = x.shape[:-1]
        # column-major vec: h[i + Nr*j] = H[i,j] -> reshape (Nt, Nr) in C order, then transpose. (== DiT)
        y = x.reshape(-1, 2, self.Nt, self.Nr).transpose(-1, -2)          # (B, 2, Nr, Nt)
        c = self.cond(self.temb(logsig.reshape(-1)))                      # (B, W)
        h = self.inp(self._tokens(y)) + self.pos
        for b in self.blocks:
            h = b(h, c)
        sh, sc = self.fada(c).chunk(2, dim=-1)
        e = self.ehead(arch_dit._modulate(self.fn(h), sh, sc))            # (B, T, 1)
        return e.sum((-2, -1)).reshape(lead)

    def forward(self, x, logsig):
        # Sum over the batch before differentiating: sample i's energy depends only on x_i (attention is
        # within a sample), so d/dx sum_i E_i is exactly the stack of the per-sample gradients.  Under
        # vmap/jacrev the leading dim is absent and the sum is over a single scalar.
        return torch.func.grad(lambda v: self.energy(v, logsig).sum())(x)


# ----------------------------------------------------------------------------- self-test
def _selftest():
    torch.manual_seed(0)
    Nr, Nt = 8, 4
    dim = 2 * Nr * Nt
    net = EnergyDiT(Nr, Nt, 64, 6, 256, circular=True, patch=1, heads=8)
    print(f"  EnergyDiT({Nr}x{Nt}) params={sum(p.numel() for p in net.parameters())}")

    # 1. zero-init: Phi == 0, hence eps_hat == 0 -- the identity denoiser, as arch_dit.DiT
    x, ls = torch.randn(5, dim), torch.randn(5)
    assert float(net.energy(x, ls).detach().abs().max()) == 0.0
    assert float(net(x, ls).detach().abs().max()) == 0.0

    with torch.no_grad():                                # give the head weights so the rest is non-vacuous
        net.ehead.weight.normal_(0.0, 0.3)
        net.ehead.bias.normal_(0.0, 0.3)
        for b in net.blocks:                             # adaLN-Zero starts at the identity block
            b.ada[-1].weight.normal_(0.0, 0.05)
            b.ada[-1].bias.normal_(0.0, 0.05)

    # 2. forward IS the gradient of energy (central finite differences)
    torch.set_default_dtype(torch.float64)
    netd = net.double()
    x0, l0 = torch.randn(dim, dtype=torch.float64), torch.tensor(-0.5, dtype=torch.float64)
    g = netd(x0, l0)
    h = 1e-5
    fd = torch.empty(dim, dtype=torch.float64)
    for i in range(dim):
        d = torch.zeros(dim, dtype=torch.float64); d[i] = h
        fd[i] = (netd.energy(x0 + d, l0) - netd.energy(x0 - d, l0)) / (2 * h)
    rel = float((g - fd).norm() / fd.norm())
    print(f"  grad vs central FD: rel {rel:.3e}")
    assert rel < 1e-6, rel

    # 3. the Jacobian of the head is a Hessian -> symmetric (this is the whole point of V2)
    J = torch.func.jacrev(lambda v: netd(v, l0))(x0)
    asym = float((J - J.T).norm() / J.norm())
    print(f"  ||J - J^T||_F / ||J||_F = {asym:.3e}")
    assert asym < 1e-10, asym

    # 4. shapes: lead (), (b,), (b1,b2) -- and vmap(jacrev(.)), which score.jac_batch uses
    for lead in ((), (3,), (2, 3)):
        xx = torch.randn(lead + (dim,), dtype=torch.float64)
        ll = torch.randn(lead, dtype=torch.float64)
        assert netd(xx, ll).shape == xx.shape, (lead, netd(xx, ll).shape)
    Xb, Sb = torch.randn(4, dim, dtype=torch.float64), torch.randn(4, dtype=torch.float64)
    Jb = torch.func.vmap(torch.func.jacrev(lambda v, u: netd(v, u)))(Xb, Sb)
    assert Jb.shape == (4, dim, dim)
    assert float((Jb - Jb.transpose(-1, -2)).norm() / Jb.norm()) < 1e-10

    # 5. under torch.no_grad() (score._gate_batch evaluates the denoiser there) -- same value, no error
    ref = netd(Xb, Sb).detach()
    with torch.no_grad():
        off = netd(Xb, Sb)
    assert off.shape == Xb.shape and torch.equal(off, ref)

    # 6. trainable: the loss must fall through the double-backward path.  Same synthetic denoising task
    #    arch_dit._selftest uses, same 30% bar.
    torch.set_default_dtype(torch.float32)
    g = torch.Generator().manual_seed(1)
    A = torch.randn(dim, dim, generator=g) / math.sqrt(dim)
    x0 = torch.randn(512, dim, generator=g) @ A.T
    x0 = x0 / x0.pow(2).mean().sqrt()
    eps = torch.randn(512, dim, generator=g)
    s = torch.exp(torch.rand(512, generator=g) * (math.log(3.0) - math.log(0.1)) + math.log(0.1))
    xt, ls = x0 + s.unsqueeze(-1) * eps, torch.log(s)
    net = EnergyDiT(Nr, Nt, 64, 4, 128, patch=1, heads=4)
    opt = torch.optim.Adam(net.parameters(), lr=2e-3)
    l0 = None
    for _ in range(200):
        loss = (net(xt, ls) - eps).pow(2).mean()
        opt.zero_grad(set_to_none=True); loss.backward(); opt.step()
        l0 = float(loss.detach()) if l0 is None else l0
    with torch.no_grad():
        l1 = float((net(xt, ls) - eps).pow(2).mean())
    print(f"  train: loss {l0:.4f} -> {l1:.4f}  ({100 * (1 - l1 / l0):.1f}% reduction)")
    assert l1 <= 0.7 * l0, (l0, l1)
    print("arch_energy selftest OK")


if __name__ == "__main__":
    os.environ["CUDA_VISIBLE_DEVICES"] = ""        # CPU-only by design; the GPUs are Exclusive_Process
    _selftest()
