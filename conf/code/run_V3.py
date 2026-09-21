"""conf/code/run_V3.py -- Stage C variant V3 (10_SPEC_stageC §3b):
the FROZEN N'=1.6e5 recipe plus the Jacobian-symmetry regulariser

    loss = DSM  +  lambda * E_v || (J - J^T) v ||^2,     J = d tweedie_real / dx,     lambda = 1.0 FIXED.

lambda is NOT a knob: §3b registers the single value 1.0 and tuning it would violate A2.  If training
diverges at lambda = 1.0 that is the result and it is reported as such.

Everything else is V0 byte for byte: dit / vp / angle, w64 d6 heads8 patch1 emb256,
lr 2.238046051591068e-3, ema 0.999, batch 256, ntrain 160000, D2 / S2 / 8x4, float32 on GPU,
patience 20 on the PURE DSM val loss, never before 200 epochs, max 3000.

The rung label is deliberately V0's ("D2SX160000", attempt 1), because score.train derives its training
seed from (rung, attempt): V3 therefore sees the SAME (x0, sigma, eps) stream as V0 in the same order,
and the Hutchinson probe comes from a separate generator.  The only difference between the two runs is
the extra loss term.  The checkpoint and the log are separate files, so nothing of V0's is touched.

Usage (GPU 2 only -- Compute Mode is Exclusive_Process):
  CUDA_VISIBLE_DEVICES=2 OMP_NUM_THREADS=2 ~/miniforge3/envs/torch/bin/python conf/code/run_V3.py --tag C
"""
import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import score

HP = dict(arch="dit", param="vp", domain="angle", lr=0.002238046051591068, ema=0.999,
          batch=256, emb=256, width=64, depth=6, heads=8, patch=1)     # V0's, copied verbatim (A4)
NR, NT, PRIOR, NTRAIN = 8, 4, "S2", 160000
RUNG, ATTEMPT = "D2SX160000", 1                                        # V0's seed -> same data stream
LAM = 1.0                                                              # §3b: FIXED, never tuned

ap = argparse.ArgumentParser()
ap.add_argument("--tag", default="C", help="routes the ladder log: LADDER_<tag>.md")
ap.add_argument("--ntrain", type=int, default=NTRAIN)
ap.add_argument("--attempt", type=int, default=1)
ap.add_argument("--device", default="cuda")
a = ap.parse_args()

# NOTE: the rung/attempt handed to score.train stay at V0's (RUNG, ATTEMPT) so the DATA STREAM is
# identical to V0's -- that is what makes V3 a controlled one-factor change.  The CHECKPOINT path
# must still carry the fallback attempt number (§3d), otherwise attempt 2 would resume from the
# diverged attempt-1 state instead of starting clean.
ck = os.path.join(C.CONF, "ckpt", f"d2sx_V3_N{a.ntrain}_a{a.attempt}.pt")
lg = os.path.join(C.CONF, "logs", f"train_V3_D2_N{a.ntrain}_a{a.attempt}.log")
ladder = os.path.join(C.CONF, f"LADDER_{a.tag}.md" if a.tag else "LADDER.md")

with open(lg, "a", buffering=1) as f:
    f.write(f"\n# ##### Stage C V3 (10_SPEC_stageC §3b): V0's recipe + lambda={LAM} * E||(J-J^T)v||^2.\n"
            f"# ##### rung label '{RUNG}' a{ATTEMPT} is V0's ON PURPOSE (same training seed -> same\n"
            f"# ##### (x0,sigma,eps) stream); the ONLY difference from V0 is the extra loss term.\n"
            f"# ##### CUDA_VISIBLE_DEVICES={os.environ.get('CUDA_VISIBLE_DEVICES', '<unset>')}"
            f"  started {time.strftime('%Y-%m-%d %H:%M:%S %Z')}\n")

print(f"[V3] ntrain={a.ntrain} lambda={LAM} ckpt={ck} log={lg} ladder={ladder}", flush=True)

# 10_SPEC_stageC §3d fallback ladder, keyed on the attempt number.  attempt 1 = frozen recipe;
# 2 = + global grad-norm clip 1.0;  3 = + clip 1.0 and lr/3.  The numbers live in score.py and
# are NOT searched here.  Applying them is automatic so no one can pick a rung by hand.
_i = min(max(a.attempt, 1), 3) - 1
GRAD_CLIP = score.GRAD_CLIP_LADDER[_i]
HP["lr"] = HP["lr"] / score.LR_DIV_LADDER[_i]
print(f"[fallback §3d] attempt={a.attempt} grad_clip={GRAD_CLIP} lr={HP['lr']:.6e}", flush=True)

res = score.train(RUNG, ATTEMPT, "D2", PRIOR, NR, NT, device=a.device, hp=HP, resume=True,
                  ntrain=a.ntrain, max_epochs=3000, patience=20, min_epochs=200, log_path=lg,
                  ckpt=ck, verbose=True, jac_reg=LAM, grad_clip=GRAD_CLIP)
print(f"[V3] trained {res['epochs']} ep, val {res['val_loss']:.6e}, {res['wall_sec']:.0f}s -> {ck}",
      flush=True)

# §3d: a run the DIVERGE_TRAIN criterion stopped must say so in the ladder.  It is a COMPLETED
# attempt (it consumes a slot), so it is neither ABORTED nor a plain UNGATED result.
res["verdict"] = ("ABORTED" if res.get("aborted") else
                  "DIVERGED" if res.get("stopped_by") == "diverged" else "UNGATED")
res["config"] = (f"V3 lambda={LAM} | dit vp/angle w64 d6 h8 p1 emb256 lr{HP['lr']} ema{HP['ema']} "
                 f"({res['params']} par)")
res["note"] = (f"Stage C V3 (§3b): V0 recipe + lambda={LAM} * E_v||(J-J^T)v||^2, J = d tweedie_real/dx, "
               f"1 Rademacher probe/sample, lambda FIXED (never tuned). "
               f"{res['epochs']} ep (stop: {res['stopped_by']}), {res['wall_sec']:.0f} s, "
               f"{res['sec_per_epoch']:.2f} s/ep, ntrain={a.ntrain}, device {res['device']}, ckpt {ck}, "
               f"split {res['split_hash']}. D2 has no true score: UNGATED here, gates are D1-only "
               f"(04_SPEC §5). Estimator + no-op-when-off verified by code/selftest_V3.py.")
print(f"[V3] {ladder} += {score.ladder_append(res, path=ladder).rstrip()}", flush=True)
