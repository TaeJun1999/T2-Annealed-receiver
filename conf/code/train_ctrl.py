"""(review_next NEXT_EXPERIMENTS §2.5, H0) Control retrain of the headline D2 score prior under a NEW tag.

Same recipe, same rung label (-> same training seed), same split and N_train as ckpt/d2sx_N160000_a1.pt, but
run with the P0-fixed score.train, so <ckpt>_best.pt (best-epoch weights) is stored next to the last-epoch file.
Not a re-run of the pre-registered checkpoint: it writes only under conf/ckpt_review_next/ and
conf/logs/review_next/, and ckpt/d2sx_N160000_a1.pt and every result made from it stay untouched.
Bit-identity with the legacy checkpoint is NOT expected (GPU nondeterminism).  One training per process.

    CUDA_VISIBLE_DEVICES=<free> ~/miniforge3/envs/torch/bin/python conf/code/train_ctrl.py --ntrain 160000 --attempt 1
"""
import argparse
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import torch
import common as C
import score

HP = dict(arch="dit", param="vp", domain="angle", lr=0.002238046051591068, ema=0.999,
          batch=256, emb=256, width=64, depth=6, heads=8, patch=1)       # = run_d2_sx.HP (frozen, 04_SPEC §6)
NR, NT, PRIOR = 8, 4, "S2"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ntrain", type=int, default=160000)
    ap.add_argument("--attempt", type=int, default=1)
    a = ap.parse_args()
    tag = f"ctrl_N{a.ntrain}_a{a.attempt}"
    ckd, lgd = os.path.join(C.CONF, "ckpt_review_next"), os.path.join(C.CONF, "logs", "review_next")
    os.makedirs(ckd, exist_ok=True); os.makedirs(lgd, exist_ok=True)
    ck, lg = os.path.join(ckd, f"{tag}.pt"), os.path.join(lgd, f"train_{tag}.log")
    rung = f"D2SX{a.ntrain}"                              # SAME label as run_d2_sx.py -> same training seed
    # initial weights come from torch's global RNG (make_model is unseeded, CHANGELOG N1): record the seed and
    # the init hash by drawing the same model on a copy of the RNG state, then restoring it for score.train.
    s0 = torch.get_rng_state()
    m0 = score.make_model(rung, HP, NR, NT)
    h0 = hashlib.sha256(b"".join(v.detach().cpu().numpy().tobytes() for _, v in sorted(m0.state_dict().items())))
    torch.set_rng_state(s0)
    print(f"[ctrl] {tag}: rung {rung} (seed as legacy d2sx), torch.initial_seed={torch.initial_seed()} "
          f"init sha256[:16]={h0.hexdigest()[:16]}  -> {ck}", flush=True)
    res = score.train(rung, a.attempt, "D2", PRIOR, NR, NT, device="cuda", hp=HP, resume=True,
                      ntrain=a.ntrain, max_epochs=3000, patience=20, min_epochs=200, log_path=lg, ckpt=ck,
                      verbose=False)
    print(f"[ctrl] done: {res['epochs']} ep, stopped_by={res['stopped_by']}, best val {res['val_loss']:.6e} "
          f"@{res['best_epoch']}, best_ckpt={res['best_ckpt']}, {res['wall_sec']:.0f}s", flush=True)
    if res["best_ckpt"]:
        b, l = score.ckpt_identity(res["best_ckpt"]), score.ckpt_identity(ck)
        ok = b["epoch"] == l["best_epoch"]
        print(f"[ctrl] best file epoch {b['epoch']} == last file best_epoch {l['best_epoch']}: {ok}  "
              f"(best sha {b['sha256_16']}, last sha {l['sha256_16']})", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
