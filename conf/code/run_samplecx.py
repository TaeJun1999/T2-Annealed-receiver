"""Sample-complexity curve for the learned score (REPORT ONLY -- 04_SPEC §6 category).

The arm comparison stays at the equal N_train = 1e4 budget that 01_RULES §5 mandates.  This measures a
different quantity: HOW MUCH DATA the pre-registered quality bar GC <= 0.15 actually needs.  Without it the
negative result is "we tried 959 configurations and failed"; with it, it is "GB and GD are met at 1e4 and
GC needs N samples", which is a number a follow-up can act on.
Architecture is the best-D1-gate-score configuration, not re-searched.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, common as C, score

HP = dict(arch="dit", param="vp", domain="angle", lr=0.002238046051591068, ema=0.999,
          batch=256, emb=256, width=64, depth=6, heads=8, patch=1)
N = int(sys.argv[1]); NR, NT = 8, 4
# 10_SPEC §3d ladder (NEXT_EXPERIMENTS_B32e4 §1): optional 2nd argument = fallback 2 (grad clip 1.0) or 3 (+ lr/3);
# same rung/attempt (data stream), checkpoint suffix _fb<k>.  No 2nd argument = the frozen recipe, unchanged.
FB = int(sys.argv[2]) if len(sys.argv) > 2 else 1
assert FB in (1, 2, 3), FB
GRAD_CLIP = score.GRAD_CLIP_LADDER[FB - 1]
HP["lr"] = HP["lr"] / score.LR_DIV_LADDER[FB - 1]
sfx = f"_fb{FB}" if FB > 1 else ""
ck = os.path.join(C.CONF, "ckpt", f"sx_N{N}_D1{sfx}.pt")
lg = os.path.join(C.CONF, "logs", f"train_sx_N{N}_D1{sfx}.log")
print(f"[sx] N_train={N} (arm budget is 1e4; this is a report-only measurement)", flush=True)
res = score.train(f"SX{N}", 1, "D1", "S", NR, NT, device="cuda", hp=HP, resume=True, ntrain=N,
                  max_epochs=3000, patience=20, min_epochs=200, log_path=lg, ckpt=ck, verbose=False,
                  **({"grad_clip": GRAD_CLIP} if FB > 1 else {}))
G = score.gates_D1(ck, NR, NT, prior="S", n_eval=512, device="cuda", n_jac=64, stream=10)
print(f"[sx] N={N:>7} epochs={res['epochs']:>4} val={res['val_loss']:.4e} "
      f"GB={float(G['GB']):.5f} GC={float(G['GC']):.5f} GD={float(G['GD']):.5f} "
      f"gate_score={score.gate_score(G):.4f} passed={G['passed']}", flush=True)
with open(os.path.join(C.CONF, "results", "samplecx.csv"), "a") as f:
    if f.tell() == 0:
        f.write("N_train,epochs,val_loss,GA,GB,GC,GD,GD_trace,gate_score,passed\n")
    f.write(f"{N},{res['epochs']},{res['val_loss']:.6e},{float(G['GA']):.6e},{float(G['GB']):.6e},"
            f"{float(G['GC']):.6e},{float(G['GD']):.6e},{float(G['GD_trace']):.6e},"
            f"{score.gate_score(G):.6f},{G['passed']}\n")
