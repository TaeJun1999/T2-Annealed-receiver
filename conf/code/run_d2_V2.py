"""conf/code/run_d2_V2.py -- Stage C variant V2 (10_SPEC_stageC §3b): train the ENERGY-parameterised
score prior on D2 at the Stage C budget.

s(x,sigma) = -grad_x E_theta(x,sigma), so the denoiser Jacobian is a Hessian and symmetric by
construction (code/arch_energy.py).  Everything that is not the output parameterisation is the frozen
Stage C recipe, copied verbatim from code/run_d2_sx.py::HP -- no re-search of anything (A4).

WHY NOT `runner.py train`.  cmd_train resolves its hyper-parameters from the ladder table
(score.hp_for asserts rung in score.RUNGS) and never forwards --ntrain to score.train, so it cannot
express "frozen D1-optimal recipe, N'=160000, energy head".  10_SPEC_stageC allows the driver route and
code/run_d2_sx.py is the precedent; this file is the same shape, minus the GB'/GMM comparison, which is
a separate reporting step that needs the equal-budget GMM fit to exist first.

OUTPUTS (all Stage C names -- nothing here touches LADDER.md, tables_D1/D2.txt or gate_D1.txt):
  ckpt/d2sx_V2_N<ntrain>_a<attempt>.pt     per-epoch checkpoint, resumable
  logs/train_V2_D2_N<ntrain>.log           the per-epoch log score.train writes
  LADDER_C.md                              one appended row when training stops (verdict UNGATED)

AFTER TRAINING, the two things that decide V2 (do NOT tune against either -- A2):
  code/jacobian_psd.py --ckpt ckpt/d2sx_V2_N160000_a1.pt --out results/diag/jacobian-psd_V2_D2.npz
  runner.py gate --testbed D1 --tag C      (the gate is measurable on D1 only -- 04_SPEC §5)
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import score

# Frozen Stage C recipe + the ONE change V2 is: head='energy'.
HP = dict(arch="dit", param="vp", domain="angle", lr=0.002238046051591068, ema=0.999,
          batch=256, emb=256, width=64, depth=6, heads=8, patch=1, head="energy")
NR, NT, PRIOR = 8, 4, "S2"

ap = argparse.ArgumentParser()
ap.add_argument("--ntrain", type=int, default=160000)
ap.add_argument("--attempt", type=int, default=1)
ap.add_argument("--device", default="cuda")
ap.add_argument("--max-epochs", type=int, default=3000)
ap.add_argument("--tag", default="C", help="Stage C ladder file: LADDER_<tag>.md")
a = ap.parse_args()

tag = f"V2_N{a.ntrain}_a{a.attempt}"
ck = os.path.join(C.CONF, "ckpt", f"d2sx_{tag}.pt")
lg = os.path.join(C.CONF, "logs", f"train_V2_D2_N{a.ntrain}_a{a.attempt}.log")
print(f"[V2] ntrain={a.ntrain} attempt={a.attempt} device={a.device} "
      f"CUDA_VISIBLE_DEVICES={os.environ.get('CUDA_VISIBLE_DEVICES', '<unset>')}", flush=True)
print(f"[V2] hp = {HP}", flush=True)
print(f"[V2] ckpt {ck}\n[V2] log  {lg}", flush=True)


# 10_SPEC_stageC §3d fallback ladder, keyed on the attempt number.  attempt 1 = frozen recipe;
# 2 = + global grad-norm clip 1.0;  3 = + clip 1.0 and lr/3.  The numbers live in score.py and
# are NOT searched here.  Applying them is automatic so no one can pick a rung by hand.
_i = min(max(a.attempt, 1), 3) - 1
GRAD_CLIP = score.GRAD_CLIP_LADDER[_i]
HP["lr"] = HP["lr"] / score.LR_DIV_LADDER[_i]
print(f"[fallback §3d] attempt={a.attempt} grad_clip={GRAD_CLIP} lr={HP['lr']:.6e}", flush=True)

res = score.train(f"D2V2{a.ntrain}", a.attempt, "D2", PRIOR, NR, NT, device=a.device, hp=HP, resume=True,
                  ntrain=a.ntrain, max_epochs=a.max_epochs, patience=20, min_epochs=200,
                  log_path=lg, ckpt=ck, verbose=True, grad_clip=GRAD_CLIP)
print(f"[V2] trained {res['epochs']} ep, best val {res['val_loss']:.6e}, {res['wall_sec']:.0f} s "
      f"({res['sec_per_epoch']:.2f} s/ep), stopped_by={res['stopped_by']}, aborted={res['aborted']}",
      flush=True)

res["verdict"] = "ABORTED" if res.get("aborted") else "UNGATED"
res["note"] = (f"Stage C V2 (energy head, s = -grad_x E): {res['epochs']} ep (stop: {res['stopped_by']}), "
               f"{res['wall_sec']:.0f} s, {res['sec_per_epoch']:.2f} s/ep, device {res['device']}, "
               f"N_train={a.ntrain}, ckpt {ck}, split {res['split_hash']}  || UNGATED: GA-GD are measured "
               f"by runner.py gate on D1; the site-validity check is code/jacobian_psd.py.")
try:
    row = score.ladder_append(res, path=os.path.join(C.CONF, f"LADDER_{a.tag}.md"))
    print(f"[V2] LADDER_{a.tag}.md += {row.rstrip()}", flush=True)
except Exception as ex:                       # a bookkeeping failure must never lose the checkpoint
    print(f"[V2] WARNING: ladder_append failed: {type(ex).__name__}: {ex}", flush=True)
