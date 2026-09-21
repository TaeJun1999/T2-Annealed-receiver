"""conf/code/selftest_V2.py -- the mandatory self-check for Stage C variant V2 (10_SPEC_stageC §3b).

V2 parameterises the score as the gradient of a scalar energy, s = -grad_x E_theta(x, sigma), so that
    d s / d x = -Hess E                        is SYMMETRIC BY CONSTRUCTION,
which is the property the measured collapse mechanism says the learned denoiser was missing
(results/diag/jacobian-psd_D2.npz: 255/256 indefinite site covariances vs 0/256 for the exact GMM).

Three checks, all asserted, all on CPU:
  1. SYMMETRY   through the REAL consumer path -- score.jac_batch on score.tweedie_real, exactly the call
                gates GD and conf/code/jacobian_psd.py make -- with ||J - J^T||_F / ||J||_F <= 1e-5.
                Run on a RANDOMISED net (at zero-init the Jacobian is the identity and the test would be
                vacuous), and run on the plain-DiT V0 model too, which must FAIL the same bound: that is
                what makes the check informative rather than tautological.
                Also asserted: real symmetry implies the complex Wirtinger J is HERMITIAN (the receiver
                symmetrises nu*J before inverting it), which is an algebraic consequence, not a hope.
  2. SHAPES     score_real / denoise_real with leading shapes () and (b,), value-identical across the two,
                and the Tweedie/native-head identity GA is built on.
  3. OVERFIT    a few hundred Adam steps on a tiny real D2 subset, through the SAME ScoreModel.loss the
                frozen recipe uses.  A broken double-backward path shows up here in seconds instead of
                after GPU hours.

Run:  OMP_NUM_THREADS=2 CUDA_VISIBLE_DEVICES= ~/miniforge3/envs/torch/bin/python code/selftest_V2.py
"""
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import torch

import common as C
import score
import sigma as SG

NR, NT = 8, 4
DIM = 2 * NR * NT
SYM_TOL = 1e-5                      # the V2 bound; a Hessian gives ~1e-16 in float64, so this is generous
# The frozen Stage C recipe (10_SPEC_stageC §4 / A4), copied verbatim from code/run_d2_sx.py::HP.
# head='energy' is the ONLY difference -- that is what V2 is.
HP_V0 = dict(arch="dit", param="vp", domain="angle", lr=0.002238046051591068, ema=0.999,
             batch=256, emb=256, width=64, depth=6, heads=8, patch=1)
HP_V2 = dict(HP_V0, head="energy")


def _randomise(m, sd=0.1, seed=7):
    """Move every parameter off its (partly zero) init, so the Jacobian is not trivially the identity."""
    g = torch.Generator().manual_seed(seed)
    with torch.no_grad():
        for p in m.parameters():
            p.add_(torch.randn(p.shape, generator=g, dtype=torch.float64).to(p.dtype) * sd)
    return m


def _build(hp, dtype=torch.float64, randomise=True):
    m = score.make_model("V2SELFTEST", hp, NR, NT).to(dtype=dtype).eval()
    m.refresh_M()                                  # exact orthogonal M at THIS dtype (01_RULES §9.3/§9.5)
    if randomise:
        _randomise(m)
    for p in m.parameters():
        p.requires_grad_(False)                    # as score.load_model leaves it for the receiver
    return m


def check_symmetry(n=8, k=6):
    """CHECK 1.  Relative asymmetry of the real Jacobian that D-14 consumes, at one frozen D2 grid point."""
    nu_grid, sig_grid = SG.load("D2")
    nu, sg = float(nu_grid[k]), float(sig_grid[k])
    rng = np.random.default_rng(20260921)
    X = torch.as_tensor(rng.standard_normal((n, DIM)) / math.sqrt(2), dtype=torch.float64)
    S = torch.full((n,), sg, dtype=torch.float64)
    out = {}
    print(f"[1] symmetry at D2 grid k={k}: sigma={sg:.4e} nu={nu:.4e}, n={n} random inputs, float64")
    for tag, hp in (("V2 energy head", HP_V2), ("V0 vector head (control)", HP_V0)):
        m = _build(hp)
        Jr = score.jac_batch(lambda v, u: score.tweedie_real(m, v, u), X, S)     # THE consumer call
        asym = (Jr - Jr.transpose(-1, -2)).norm(dim=(-2, -1)) / Jr.norm(dim=(-2, -1))
        Jc = score.wirtinger(Jr)
        herm = ((Jc - Jc.conj().transpose(-1, -2)).abs().amax((-2, -1))
                / Jc.abs().amax((-2, -1)).clamp_min(1e-300))
        # the native x0 head is the other path the receiver never takes but the gates do
        Jn = score.jac_batch(lambda v, u: m.denoise_real(v, u), X, S)
        asym_n = (Jn - Jn.transpose(-1, -2)).norm(dim=(-2, -1)) / Jn.norm(dim=(-2, -1))
        out[tag] = (float(asym.max()), float(herm.max()), float(asym_n.max()))
        print(f"    {tag:<26} ||J-J^T||/||J||  max {float(asym.max()):.3e}  median "
              f"{float(asym.median()):.3e} | herm(Wirtinger) max {float(herm.max()):.3e} | "
              f"native x0 head max {float(asym_n.max()):.3e}")
    a2, h2, an2 = out["V2 energy head"]
    a0 = out["V0 vector head (control)"][0]
    assert a2 <= SYM_TOL, f"V2 Tweedie Jacobian is NOT symmetric: {a2:.3e} > {SYM_TOL:.0e}"
    assert an2 <= SYM_TOL, f"V2 native-head Jacobian is NOT symmetric: {an2:.3e} > {SYM_TOL:.0e}"
    assert h2 <= 1e-10, f"V2 Wirtinger J is not Hermitian: {h2:.3e} (real symmetry should force this)"
    assert a0 > SYM_TOL, f"the control is symmetric too ({a0:.3e}) -- check 1 proves nothing as written"
    print(f"    OK: V2 {a2:.3e} <= {SYM_TOL:.0e} < {a0:.3e} = V0 control")
    return out


def check_shapes():
    """CHECK 2.  Leading shapes () and (b,) -- a past bug here came from a module assuming a batch axis."""
    m = _build(HP_V2)
    rng = np.random.default_rng(11)
    Xb = torch.as_tensor(rng.standard_normal((5, DIM)) / math.sqrt(2), dtype=torch.float64)
    Sb = torch.as_tensor(np.exp(rng.uniform(math.log(0.05), math.log(0.8), 5)), dtype=torch.float64)
    print("[2] shape robustness: lead (), (b,), (b1,b2) on score_real / denoise_real / tweedie_real")
    sb, db, tb = m.score_real(Xb, Sb), m.denoise_real(Xb, Sb), score.tweedie_real(m, Xb, Sb)
    assert sb.shape == db.shape == tb.shape == Xb.shape, (sb.shape, db.shape, tb.shape)
    worst_s = worst_d = 0.0
    for i in range(len(Xb)):                                     # lead = () -- the receiver's own call
        x, s = Xb[i], Sb[i]
        assert m.score_real(x, s).shape == (DIM,) and m.denoise_real(x, s).shape == (DIM,)
        worst_s = max(worst_s, float((m.score_real(x, s) - sb[i]).abs().max()))
        worst_d = max(worst_d, float((m.denoise_real(x, s) - db[i]).abs().max()))
    X2 = Xb[:4].reshape(2, 2, DIM); S2 = Sb[:4].reshape(2, 2)    # lead = (b1, b2)
    assert m.score_real(X2, S2).shape == X2.shape
    assert float((m.score_real(X2, S2).reshape(4, DIM) - sb[:4]).abs().max()) < 1e-12
    # GA's identity: x + sigma^2 * score_real == the native x0 head (exact for 'vp', V2 must not break it)
    ga = float(((tb - db).norm(dim=-1) / db.norm(dim=-1)).max())
    print(f"    unbatched vs batched: score {worst_s:.3e}  denoise {worst_d:.3e} | "
          f"GA identity |tweedie - native|/|native| max {ga:.3e}")
    assert worst_s < 1e-12 and worst_d < 1e-12, (worst_s, worst_d)
    assert ga < 1e-10, ga
    print("    OK")
    return dict(worst_score=worst_s, worst_denoise=worst_d, GA=ga)


def check_overfit(ntrain=1024, steps=300, batch=64, seed=3):
    """CHECK 3.  The loss must fall on a tiny real D2 subset, through the SAME ScoreModel.loss the frozen
    recipe optimises.  Catches a severed gradient path before any GPU time is spent."""
    torch.set_default_dtype(torch.float32)
    Xtr, _, split_hash, pw = score.training_split("D2", "S2", NR, NT, ntrain)
    smin, smax, _, _ = score._sigma_range("D2")
    tr = torch.as_tensor(score.np_pack(Xtr), dtype=torch.float32)
    m = score.make_model("V2SELFTEST", HP_V2, NR, NT).float()
    m.refresh_M()
    opt = torch.optim.Adam(m.parameters(), lr=HP_V2["lr"])
    g = torch.Generator().manual_seed(seed)
    print(f"[3] overfit sanity: n={len(tr)} real D2/S2 samples (split {split_hash}, power {pw:.4f}), "
          f"{steps} Adam steps, batch {batch}, lr {HP_V2['lr']:.4e}")
    def draw():
        b = tr[torch.randint(len(tr), (batch,), generator=g)]
        s = torch.exp(torch.rand(batch, generator=g) * (math.log(smax) - math.log(smin)) + math.log(smin))
        return b, s, torch.randn(batch, DIM, generator=g)

    # THE BASELINE IS THE UNTRAINED MODEL, measured before any optimiser step.  The energy head is
    # zero-initialised, so eps_hat == 0 and this loss is E||eps||^2 = 1 analytically -- the value a model
    # that learns nothing keeps.  (An earlier version of this check averaged the FIRST 20 Adam steps
    # instead; at lr 2.2e-3 the loss is already down to ~0.855 by then, so that "baseline" was itself a
    # partly-trained model and the 10% bar measured the wrong interval.  The bar is unchanged.)
    with torch.no_grad():
        base = float(m.loss(*draw()))
    hist, t0 = [], time.time()
    for it in range(steps):
        loss = m.loss(*draw())
        opt.zero_grad(set_to_none=True); loss.backward(); opt.step()
        hist.append(float(loss.detach()))
    first = float(np.mean(hist[:20])); last = float(np.mean(hist[-20:]))
    print(f"    untrained (zero-init, eps_hat=0) {base:.5f}  ->  last-20 mean {last:.5f}   "
          f"({100 * (1 - last / base):.1f}% below the identity denoiser; first-20 mean {first:.5f}; "
          f"{time.time() - t0:.1f} s on CPU)")
    assert last < 0.9 * base, (base, first, last)
    assert np.isfinite(hist).all(), "non-finite loss -- the double-backward path is broken"
    print("    OK")
    return dict(base=base, first=first, last=last)


if __name__ == "__main__":
    os.environ["CUDA_VISIBLE_DEVICES"] = ""      # CPU only: the GPUs are Exclusive_Process
    torch.set_num_threads(int(os.environ.get("OMP_NUM_THREADS", "2")))
    torch.manual_seed(0)              # model init is otherwise entropy-seeded: fix it (01_RULES: seeds)
    torch.set_default_dtype(torch.float64)
    print(f"selftest_V2  torch {torch.__version__}  hp = {HP_V2}")
    s = check_symmetry()
    h = check_shapes()
    o = check_overfit()
    print("\nselftest_V2 OK -- V2 Jacobian symmetry "
          f"{s['V2 energy head'][0]:.3e} (tol {SYM_TOL:.0e}), control {s['V0 vector head (control)'][0]:.3e}; "
          f"GA {h['GA']:.3e}; overfit {o['base']:.4f} -> {o['last']:.4f}")
    print("NOTE: symmetry is not positive-semidefiniteness.  Whether the site is a valid covariance is "
          "measured AFTER training by code/jacobian_psd.py --ckpt ckpt/d2sx_V2_N160000_a1.pt.")
