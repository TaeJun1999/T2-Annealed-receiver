"""(review_next P0-1 / P0-4) Regression checks for checkpoint integrity and hp inheritance.  CPU only, ~1 min.

    ~/miniforge3/envs/torch/bin/python conf/code/selftest_ckpt.py

P0-1  a tiny D2 score net trained until patience fires (so best_epoch < last epoch by construction):
  1. <ckpt>_best.pt exists, role='best', epoch == best_epoch; <ckpt> is role='last' at the final epoch
  2. re-measured val loss of _best.pt == recorded best_val, of <ckpt> == last hist val  (so the best file
     holds the best epoch's EMA, not an alias of the live EMA that later updates moved)
  3. resuming the finished checkpoint trains nothing and leaves BOTH files byte-identical
  4. interrupted at an earlier epoch and resumed == uninterrupted (same last and best EMA tensors),
     both after the best epoch [4] and before it [4b] (the resumed segment writes _best.pt itself)
stop rules: sign-safe divergence predicate (negative VAE loss), resume restores the divergence counter.
P0-4  resolve_hp inherits hp from the argmin-gate-score ATTEMPT, not from the last existing attempt.
"""
import hashlib
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
import score

torch.set_num_threads(4)
HP = dict(arch="dit", param="vp", domain="angle", lr=1e-2, ema=0.9, batch=64, emb=32, width=16, depth=1,
          heads=2, patch=1)
KW = dict(testbed="D2", prior="S2", Nr=8, Nt=4, device="cpu", hp=HP, ntrain=600, max_epochs=80,
          patience=3, min_epochs=0, verbose=False)
NTRAIN = KW["ntrain"]


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def load(p):
    return torch.load(p, map_location="cpu", weights_only=False)


def same_ema(a, b):
    return all(torch.equal(a["ema"][k], b["ema"][k]) for k in a["ema"])


def run(d, name, **over):
    # score.train draws the INITIAL weights from torch's global RNG (make_model is not seeded), so two
    # fresh runs in one process start from different nets.  Pin it here; a resume ignores it (weights load).
    torch.manual_seed(0)
    ck = os.path.join(d, f"{name}.pt")
    return score.train("SELFTESTCK", 1, ckpt=ck, log_path=os.path.join(d, f"{name}.log"), **dict(KW, **over)), ck


def test_p01(d):
    res, ck = run(d, "A")
    bk = score.best_ckpt_path(ck)
    assert res["stopped_by"] == "patience", f"tune HP: expected a patience stop, got {res['stopped_by']}"
    last, best = load(ck), load(bk)
    assert res["best_ckpt"] == bk and best["role"] == "best" and last["role"] == "last"
    assert best["epoch"] == best["best_epoch"] == res["best_epoch"] < last["epoch"] == res["epochs"]
    assert last["stopped_by"] == "patience" and not same_ema(last, best)
    print(f"[1] ok: best @{best['epoch']} / last @{last['epoch']}, files distinct")

    vb, vl = score.val_loss_of(bk, NTRAIN), score.val_loss_of(ck, NTRAIN)
    rb, rl = best["best_val"], last["hist"][-1][2]
    assert abs(vb - rb) <= 1e-5 * abs(rb), (vb, rb)
    assert abs(vl - rl) <= 1e-5 * abs(rl), (vl, rl)
    assert vb < vl
    print(f"[2] ok: reload val best {vb:.6e} (rec {rb:.6e}), last {vl:.6e} (rec {rl:.6e})")

    h = (sha(ck), sha(bk))
    res2, _ = run(d, "A")
    assert res2["epochs"] == res["epochs"] and (sha(ck), sha(bk)) == h, "resume of a finished ckpt mutated it"
    print(f"[3] ok: resume of finished ckpt trained 0 epochs, both files byte-identical")

    k = max(1, res["epochs"] - 2)
    run(d, "B", max_epochs=k)
    resb, ckb = run(d, "B")
    assert resb["epochs"] == res["epochs"], (resb["epochs"], res["epochs"])
    assert same_ema(load(ckb), last) and same_ema(load(score.best_ckpt_path(ckb)), best)
    print(f"[4] ok: stop at {k} + resume == uninterrupted (last and best EMA identical)")

    # [4b] interrupted BEFORE the best epoch: the resumed segment itself must write _best.pt (in [4] the best
    # epoch always falls before k, so that path was never exercised -- P0 review finding)
    k = max(1, res["best_epoch"] - 1)
    run(d, "Cb", max_epochs=k)
    resc, ckc = run(d, "Cb")
    bc = load(score.best_ckpt_path(ckc))
    assert resc["epochs"] == res["epochs"] and bc["epoch"] == best["epoch"] > k, (bc["epoch"], k)
    assert same_ema(load(ckc), last) and same_ema(bc, best)
    print(f"[4b] ok: stop at {k} (< best @{best['epoch']}) + resume rewrites _best.pt == uninterrupted")


def test_stop_rules():
    """_bad_epoch / _trailing_bad / _already_stopped on synthetic histories (no training)."""
    M, E = score.DIVERGE_TRAIN_MULT, score.DIVERGE_TRAIN_EPOCHS
    assert score._bad_epoch(3.01, 1.0) and not score._bad_epoch(2.99, 1.0) and score._bad_epoch(float("nan"), 1.0)
    # negative loss (VAE L6): improving or flat epochs are NOT bad; only a blow-up of (M-1)|best| is
    assert not score._bad_epoch(-0.10, -0.09) and not score._bad_epoch(-0.05, -0.09)
    assert score._bad_epoch(0.1 + 1e-9, -0.05) and not score._bad_epoch(0.05, -0.05)
    l6 = [(i, 0.0, -0.09 + 1e-4 * (i - 293) ** 2 * (i > 293)) for i in range(1, 314)]
    assert score._already_stopped(313, -0.09, 293, l6, 20, 200, 3000) == "patience"
    h = [(1, 0, 1.0)] + [(i, 0, 5.0) for i in range(2, 2 + E - 1)]            # E-1 bad epochs at the tail
    assert score._trailing_bad(h, 1.0) == E - 1 and score._already_stopped(E, 1.0, 1, h, 99, 0, 99) is None
    assert score._already_stopped(E + 1, 1.0, 1, h + [(E + 1, 0, float("nan"))], 99, 0, 99) == "diverged"
    print(f"[stop] ok: sign-safe divergence predicate, trailing-bad count (resume restores ndiv={E - 1})")


def test_p04(d):
    """L3 inherits 'param' from the rung with the best gate score.  L1 a2 wins; a3 exists and is worse."""
    old = (score.ckpt_path, score.gates_D1, score.gate_score)
    scores = {("L1", 1): 0.5, ("L1", 2): 0.1, ("L1", 3): 0.9, ("L2", 1): 0.3}
    try:
        score.ckpt_path = lambda r, a, t, dd=None: os.path.join(d, f"{r}_a{a}_{t}.pt")
        for (r, a), s in scores.items():
            torch.save(dict(hp=dict(param=f"P_{r}_a{a}", domain="angle", arch="mlp"), s=s),
                       score.ckpt_path(r, a, "D1"))
        score.gates_D1 = lambda p, *x, **y: load(p)["s"]
        score.gate_score = lambda g: g
        hp, sel = score.resolve_hp("L3", 1, "D1", 8, 4)
    finally:
        score.ckpt_path, score.gates_D1, score.gate_score = old
    assert sel["base"] == "L1" and sel["base_attempt"] == 2, sel
    assert hp["param"] == "P_L1_a2", hp["param"]
    print(f"[P0-4] ok: base L1 attempt {sel['base_attempt']} (score {sel['base_score']}), param {hp['param']}")


def test_chunk_plan():
    """runner --skip0: the development set is exactly 16 chunks (2560+40k, 40); the test set is unchanged."""
    import common as C, runner as R
    dev = R.chunk_plan(C.DEV_SKIP0, 640, 40)
    assert dev == [(C.DEV_SKIP0 + 40 * k, 40) for k in range(16)], dev[:3]
    assert R.chunk_plan(0, 2560, 40) == [(40 * k, 40) for k in range(64)]
    assert R.chunk_plan(0, 100, 40) == [(0, 40), (40, 40), (80, 20)]
    print(f"[chunk] ok: dev set = 16 x ({C.DEV_SKIP0}+40k, 40); test set unchanged")


if __name__ == "__main__":
    test_chunk_plan()
    test_stop_rules()
    with tempfile.TemporaryDirectory() as d:
        test_p04(d)
    with tempfile.TemporaryDirectory() as d:
        test_p01(d)
    print("selftest_ckpt: ALL OK")
