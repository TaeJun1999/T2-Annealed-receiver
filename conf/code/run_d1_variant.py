"""Stage C: train a variant (V2 energy head / V3 Jacobian regulariser) on D1 at the Stage C budget.

WHY D1.  The pre-registered gates GA-GD need the exact score, which exists in closed form only on D1
(04_SPEC §5).  A variant therefore cannot be promoted to an arm until it has a D1 checkpoint to gate.
The D2 models trained on GPUs 1 and 2 are the ones the receiver will use; these are their gate twins.

Nothing here is re-searched: the recipe is the frozen Stage C one (10_SPEC_stageC §4 A4), and the only
difference between the two variants is the single change each of them IS.
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C, score

BASE = dict(arch="dit", param="vp", domain="angle", lr=0.002238046051591068, ema=0.999,
            batch=256, emb=256, width=64, depth=6, heads=8, patch=1)
NR, NT = 8, 4

ap = argparse.ArgumentParser()
ap.add_argument("--variant", choices=["V2", "V3"], required=True)
ap.add_argument("--ntrain", type=int, default=160000)
ap.add_argument("--attempt", type=int, default=1)
ap.add_argument("--device", default="cuda")
ap.add_argument("--max-epochs", type=int, default=3000)
ap.add_argument("--tag", default="C")
# §6e DIAGNOSTIC SWEEP ONLY.  Default None = use the §3b fixed value.  When given, this is the
# lambda sweep that asks "is there a lambda at which the penalty HELPS", because the prior-art
# survey found Chao et al. (ICML 2023) making the same penalty work and we have no explanation.
# §6e states in advance that NO lambda from this sweep becomes an arm, gate-passing or not.
ap.add_argument("--jac-reg", type=float, default=None,
                help="§6e sweep only; omit to use the §3b fixed value")
a = ap.parse_args()

HP = dict(BASE)
jac_reg = 0.0
if a.variant == "V2":
    HP["head"] = "energy"
else:
    jac_reg = 1.0                      # FIXED by 10_SPEC_stageC §3b -- never tuned, never swept
if a.jac_reg is not None:              # §6e diagnostic sweep; see the flag's help and §6e
    jac_reg = a.jac_reg

prior = C.PRIOR_OF["D1"]
sfx = "" if a.jac_reg is None else f"_lam{a.jac_reg:g}"
ck = os.path.join(C.CONF, "ckpt", f"sx_{a.variant}_N{a.ntrain}_D1_a{a.attempt}{sfx}.pt")
lg = os.path.join(C.CONF, "logs", f"train_{a.variant}_D1_N{a.ntrain}_a{a.attempt}{sfx}.log")
print(f"[{a.variant}/D1] ntrain={a.ntrain} attempt={a.attempt} prior={prior} device={a.device} "
      f"CUDA_VISIBLE_DEVICES={os.environ.get('CUDA_VISIBLE_DEVICES','<unset>')}", flush=True)
print(f"[{a.variant}/D1] hp={HP} jac_reg={jac_reg}\n[{a.variant}/D1] ckpt {ck}", flush=True)


# 10_SPEC_stageC §3d fallback ladder, keyed on the attempt number.  attempt 1 = frozen recipe;
# 2 = + global grad-norm clip 1.0;  3 = + clip 1.0 and lr/3.  The numbers live in score.py and
# are NOT searched here.  Applying them is automatic so no one can pick a rung by hand.
_i = min(max(a.attempt, 1), 3) - 1
GRAD_CLIP = score.GRAD_CLIP_LADDER[_i]
HP["lr"] = HP["lr"] / score.LR_DIV_LADDER[_i]
print(f"[fallback §3d] attempt={a.attempt} grad_clip={GRAD_CLIP} lr={HP['lr']:.6e}", flush=True)

res = score.train(f"D1{a.variant}{a.ntrain}", a.attempt, "D1", prior, NR, NT, device=a.device, hp=HP,
                  resume=True, ntrain=a.ntrain, max_epochs=a.max_epochs, patience=20, min_epochs=200,
                  log_path=lg, ckpt=ck, verbose=True, jac_reg=jac_reg, grad_clip=GRAD_CLIP)
print(f"[{a.variant}/D1] {res['epochs']} ep, best val {res['val_loss']:.6e}, {res['wall_sec']:.0f} s, "
      f"stopped_by={res['stopped_by']}, aborted={res['aborted']}", flush=True)

# §3d: a run the DIVERGE_TRAIN criterion stopped must say so in the ladder.  It is a COMPLETED
# attempt (it consumes a slot), so it is neither ABORTED nor a plain UNGATED result.
res["verdict"] = ("ABORTED" if res.get("aborted") else
                  "DIVERGED" if res.get("stopped_by") == "diverged" else "UNGATED")
res["note"] = ((("" if a.jac_reg is None else
                 f"§6e LAMBDA SWEEP lambda={a.jac_reg:g} -- DIAGNOSTIC, NOT AN ARM (§6e forbids "
                 f"promoting any lambda from this sweep, gate-passing or not).  ") )
               + f"Stage C {a.variant} on D1 (gate twin): N_train={a.ntrain}, ckpt {ck}, "
               f"split {res['split_hash']}  || UNGATED here; run `runner.py gate --testbed D1 "
               f"--ckpt {ck} --tag {a.tag}` to obtain GA-GD.")
try:
    print("[ladder]", score.ladder_append(res, path=os.path.join(C.CONF, f"LADDER_{a.tag}.md")).rstrip(), flush=True)
except Exception as ex:
    print(f"[{a.variant}/D1] WARNING ladder_append: {type(ex).__name__}: {ex}", flush=True)
