"""conf/code/selftest_V3.py -- the three mandatory checks for V3 (10_SPEC_stageC §3b):
the Jacobian-symmetry regulariser  loss += lambda * E_v||(J - J^T) v||^2,  lambda = 1.0 FIXED.

J is the REAL Jacobian of the DENOISER, J = d tweedie_real / dx (see score.jac_asym_hutch's docstring for
why the denoiser and not the score: they differ by I + a factor sigma^2, and the denoiser is what
ScorePrior.denoise_full differentiates, what RouteAClip._matrix_site inverts, and what
code/jacobian_psd.py reports asym(Jr) for).

  1. ESTIMATOR.  The Hutchinson average of ||(J - J^T)v||^2 over Rademacher probes converges to the exact
     ||J - J^T||_F^2 formed from the full Jacobian via score.jac_batch.  Asserted against the Monte-Carlo
     standard error, not against a hand-picked tolerance.
  2. IT WORKS.  Two training runs from the SAME seed and the SAME data stream, jac_reg=0 vs jac_reg=1,
     on a tiny model and a tiny subset: the relative asymmetry ||J-J^T||_F / ||J||_F -- the quantity
     jacobian_psd.py calls asym(Jr) -- must go DOWN, on the frozen D2 sigma grid.
  3. OPT-IN IS FREE.  train(..., jac_reg=0.0) on the patched score.py is BIT-IDENTICAL to train(...) on
     the pre-patch score.py (git 5e2e77a), same seed: same epoch lines, same weights.  Plus a one-step
     run showing that with jac_reg=1.0 the reported DSM train loss of the FIRST step is unchanged
     (the probe comes from a separate generator, so the data stream does not move).

CPU only, OMP_NUM_THREADS=2 (the box is shared; a 180-worker GMM fit owns the cores).
Run:  OMP_NUM_THREADS=2 ~/miniforge3/envs/torch/bin/python conf/code/selftest_V3.py
"""
import os

os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ["CUDA_VISIBLE_DEVICES"] = ""          # never touch a GPU from the self-test

import re
import subprocess
import sys
import importlib.util

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import torch

import common as C
import score
import sigma as SG

torch.set_num_threads(int(os.environ["OMP_NUM_THREADS"]))

NR, NT, PRIOR = 4, 4, "S2"                       # 4x4 -> 2N = 32 real dims: jac_batch is cheap on CPU
DIM = 2 * NR * NT
# The FROZEN Stage C recipe, shrunk in width/depth ONLY so the self-test runs on two CPU threads.
# arch/param/domain/heads/patch/ema/batch are the real ones; nothing here feeds a training decision.
HP = dict(arch="dit", param="vp", domain="angle", width=16, depth=2, emb=32, heads=2, patch=1,
          lr=2.238046051591068e-3, ema=0.999, batch=256)
RUNG, NTRAIN = "V3SELFTEST", 2048
CK = os.path.join(C.CONF, "ckpt", "selftest_V3_{}.pt")
LG = os.path.join(C.CONF, "logs", "selftest_V3_{}.log")
REF_COMMIT = "5e2e77a"                           # the last commit of score.py BEFORE the V3 patch

FAIL = []


def check(name, ok, msg):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}: {msg}", flush=True)
    if not ok:
        FAIL.append(name)


def fresh(tag):
    for p in (CK.format(tag), LG.format(tag)):
        if os.path.exists(p):
            os.remove(p)
    return CK.format(tag), LG.format(tag)


def jac(model, X, sg):
    """(b, 2N, 2N) real Jacobian of the denoiser at noise level sg -- exactly jacobian_psd.py's Jr."""
    S = torch.full((len(X),), float(sg), dtype=X.dtype)
    return score.jac_batch(lambda v, u: score.tweedie_real(model, v, u), X, S)


def asym(Jr):
    """(mean relative ||J-J^T||_F/||J||_F, mean absolute ||J-J^T||_F^2) -- the reg's own target."""
    A = Jr - Jr.transpose(-1, -2)
    return (float((A.norm(dim=(-2, -1)) / Jr.norm(dim=(-2, -1))).mean()),
            float((A.norm(dim=(-2, -1)) ** 2).mean()))


# ============================================================ 1. the estimator is the right quantity
def test_estimator():
    print("\n1. Hutchinson estimator vs the exact ||J - J^T||_F^2 from score.jac_batch")
    torch.set_default_dtype(torch.float64)
    torch.manual_seed(7)
    m = score.make_model(RUNG, HP, NR, NT).double().eval()
    with torch.no_grad():                        # the zero-init net has J = I exactly: perturb it first
        for p in m.parameters():
            p.add_(0.3 * torch.randn_like(p))
    for p in m.parameters():
        p.requires_grad_(False)

    nb, M = 8, 2000
    g = torch.Generator().manual_seed(11)
    X = torch.randn(nb, DIM, generator=g, dtype=torch.float64)
    for sg in (0.05, 0.3, 0.8):
        S = torch.full((nb,), sg, dtype=torch.float64)
        Jr = jac(m, X, sg)
        exact = float(((Jr - Jr.transpose(-1, -2)).norm(dim=(-2, -1)) ** 2).mean())
        est = np.empty(M)
        for i in range(M):
            v = (2.0 * torch.randint(0, 2, (nb, DIM), generator=g, dtype=torch.float64) - 1.0)
            est[i] = float(score.jac_asym_hutch(m, X, S, v).detach())
        mc, se = est.mean(), est.std(ddof=1) / np.sqrt(M)
        z = abs(mc - exact) / max(se, 1e-300)
        check(f"sigma={sg}", z < 4.0,
              f"exact {exact:.6e} | MC {mc:.6e} +- {se:.2e} ({M} probes) | "
              f"rel {abs(mc / exact - 1):.3%} | z = {z:.2f} (< 4)")
    torch.set_default_dtype(torch.float32)


# ============================================================ 2/3. training runs
def run(tag, jac_reg, epochs, batch=None, module=None, seed=0):
    ck, lg = fresh(tag)
    hp = dict(HP, **({"batch": batch} if batch else {}))
    torch.manual_seed(seed)                      # train() does not seed the model init; pin it here
    mod = module or score
    kw = dict(device="cpu", hp=hp, resume=False, max_epochs=epochs, patience=10 ** 6, min_epochs=1,
              log_path=lg, ckpt=ck, verbose=False, ntrain=NTRAIN)
    if jac_reg:
        kw["jac_reg"] = jac_reg
    res = mod.train(RUNG, 1, "D2", PRIOR, NR, NT, **kw)
    return res, ck, lg, [l for l in open(lg) if l.startswith("epoch")]


def nums(lines):
    """epoch lines with the wall-clock column removed -- the ONE field two runs may legitimately differ
    in.  Everything else (train, val, best, epoch numbering) must match to the last printed digit."""
    return [re.sub(r"\|\s*[0-9.]+ s\s*\|", "|", l) for l in lines]


def load_ref():
    """The pre-patch score.py, straight out of git, imported beside the patched one."""
    src = subprocess.run(["git", "-C", C.CONF, "show", f"{REF_COMMIT}:conf/code/score.py"],
                         capture_output=True, text=True, check=True).stdout
    p = os.path.join(C.CONF, "ckpt", "_selftest_V3_score_ref.py")
    open(p, "w").write(src)
    spec = importlib.util.spec_from_file_location("score_ref", p)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["score_ref"] = mod
    spec.loader.exec_module(mod)
    return mod, p


def test_identity():
    print(f"\n3. jac_reg=0.0 is bit-identical to pre-patch score.py (git {REF_COMMIT})")
    ref, refpath = load_ref()
    assert not hasattr(ref, "jac_asym_hutch"), "the reference copy is not pre-patch"
    try:
        r_new, ck_new, _, ln_new = run("id_new", 0.0, 3)
        r_ref, ck_ref, _, ln_ref = run("id_ref", 0.0, 3, module=ref)
        ok = nums(ln_new) == nums(ln_ref)
        check("epoch lines", ok,
              f"{len(ln_new)} lines identical apart from the wall-clock column | "
              f"first: {nums(ln_new)[0].strip()}"
              if ok else f"new {ln_new[0].strip()!r} vs ref {ln_ref[0].strip()!r}")
        a = torch.load(ck_new, map_location="cpu", weights_only=False)
        b = torch.load(ck_ref, map_location="cpu", weights_only=False)
        same = all(torch.equal(a["model"][k], b["model"][k]) for k in a["model"]) and \
            all(torch.equal(a["ema"][k], b["ema"][k]) for k in a["ema"])
        check("weights", same, f"{len(a['model'])} model + {len(a['ema'])} EMA tensors bitwise equal"
              if same else "weights DIFFER")
        check("val loss", r_new["val_loss"] == r_ref["val_loss"],
              f"{r_new['val_loss']!r} == {r_ref['val_loss']!r}")

        # first-step DSM loss with the regulariser ON: batch = ntrain -> one step per epoch, so the
        # 'train' column of epoch 1 IS the first step's loss.
        _, _, _, l0 = run("step0", 0.0, 3, batch=NTRAIN)
        _, _, _, l1 = run("step1", 1.0, 3, batch=NTRAIN)
        d0, d1 = l0[0].split("|")[1].strip(), l1[0].split("|")[1].strip()
        regs = [float(l.split("asym_reg")[1]) for l in l1]
        check("first-step DSM loss", d0 == d1,
              f"jac_reg=0 -> {d0} | jac_reg=1 -> {d1} (batch = ntrain, so epoch 1 IS step 1; the probe "
              f"comes from a separate generator, so the data stream does not move)")
        check("exact on a symmetric Jacobian", regs[0] == 0.0,
              f"step 1 starts at the DiT's zero-init, where the net outputs exactly 0 => m(x) = x, "
              f"J = I, J - J^T = 0: estimator returns {regs[0]:.1e} (exactly 0, not 'small')")
        check("regulariser is live", regs[-1] > 0,
              f"asym_reg by step: {', '.join(f'{r:.4e}' for r in regs)} -- > 0 once the first DSM "
              f"update has moved the net off its zero-init")
    finally:
        os.remove(refpath)


def test_reduces():
    print("\n2. jac_reg=1.0 lowers the relative asymmetry (same seed, same data stream)")
    ep = int(os.environ.get("V3_SELFTEST_EPOCHS", 60))
    r0, ck0, _, _ = run("reg0", 0.0, ep)
    r1, ck1, _, _ = run("reg1", 1.0, ep)
    print(f"   {ep} epochs x {NTRAIN // HP['batch']} steps | DSM val: jac_reg=0 {r0['val_loss']:.6e}, "
          f"jac_reg=1 {r1['val_loss']:.6e} | {r0['sec_per_epoch']:.2f} vs {r1['sec_per_epoch']:.2f} s/epoch")
    torch.set_default_dtype(torch.float64)
    m0 = score.load_model(ck0, NR, NT)[0]
    m1 = score.load_model(ck1, NR, NT)[0]
    gen = C.make_gen("D2", PRIOR, NR, NT)
    H = gen.sample_vecs(C.train_rng("D2", PRIOR, NR, 10), 32)            # held-out stream 10
    rng = np.random.default_rng(score.SEED_GATE)
    E = (rng.standard_normal((32, NR * NT)) + 1j * rng.standard_normal((32, NR * NT))) / np.sqrt(2)
    nu_grid, sig_grid = SG.load("D2")
    print(f"   {'k':>3}{'sigma':>10} | {'asym_rel(0)':>12}{'asym_rel(1)':>12}{'ratio':>8} | "
          f"{'asymF2(0)':>11}{'asymF2(1)':>11}")
    rel0, rel1, ab0, ab1 = [], [], [], []
    for k in (0, 6, 12, 19):
        nu, sg = float(nu_grid[k]), float(sig_grid[k])
        X = torch.as_tensor(score.np_pack(H + np.sqrt(nu) * E), dtype=torch.float64)
        a0, b0 = asym(jac(m0, X, sg))
        a1, b1 = asym(jac(m1, X, sg))
        rel0.append(a0); rel1.append(a1); ab0.append(b0); ab1.append(b1)
        print(f"   {k:>3}{sg:>10.4e} | {a0:>12.4e}{a1:>12.4e}{a1 / a0:>8.3f} | {b0:>11.4e}{b1:>11.4e}")
    torch.set_default_dtype(torch.float32)
    check("relative asymmetry", float(np.mean(rel1)) < float(np.mean(rel0)),
          f"grid mean {np.mean(rel0):.4e} -> {np.mean(rel1):.4e} "
          f"({100 * (1 - np.mean(rel1) / np.mean(rel0)):+.1f}%)")
    check("absolute ||J-J^T||_F^2", float(np.mean(ab1)) < float(np.mean(ab0)),
          f"grid mean {np.mean(ab0):.4e} -> {np.mean(ab1):.4e} "
          f"({100 * (1 - np.mean(ab1) / np.mean(ab0)):+.1f}%)")


if __name__ == "__main__":
    print(f"selftest_V3 | torch {torch.__version__} | {os.environ['OMP_NUM_THREADS']} threads | "
          f"{NR}x{NT} | hp {HP}")
    only = sys.argv[1:]                       # e.g. `selftest_V3.py 3` to re-run only check 3
    for n, t in (("1", test_estimator), ("2", test_reduces), ("3", test_identity)):
        if not only or n in only:
            t()
    for t in ("id_new", "id_ref", "step0", "step1", "reg0", "reg1"):
        if os.path.exists(CK.format(t)):
            os.remove(CK.format(t))
    print(f"\nselftest_V3: {'OK -- all checks passed' if not FAIL else 'FAILED: ' + ', '.join(FAIL)}")
    sys.exit(1 if FAIL else 0)
