"""B3 -- D2 score training + GB' (04_SPEC §6).

The architecture is NOT re-searched on D2 (04_SPEC §6 forbids it).  It is copied verbatim from the
configuration with the best D1 gate score on the REPORTED held-out stream (HPO trial 386).  That
configuration did NOT pass the D1 gates, so the resulting model is REPORT-ONLY: it produces GB' and it
never becomes an arm in any BLER table (conf/DECISIONS.md 2026-09-20 13:30).
"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C, score, arms as A

HP = dict(arch="dit", param="vp", domain="angle", lr=0.002238046051591068, ema=0.999,
          batch=256, emb=256, width=64, depth=6, heads=8, patch=1)
NR, NT, PRIOR = 8, 4, "S2"

ck = os.path.join(C.CONF, "ckpt", "B3_dscore_D2.pt")
lg = os.path.join(C.CONF, "logs", "train_B3_D2.log")
print(f"[B3] D1-best config (gate_score 1.494 on stream 10, NOT gate-passing) -> D2\n     {HP}", flush=True)
res = score.train("B3", 1, "D2", PRIOR, NR, NT, device="cuda", hp=HP, resume=True,
                  max_epochs=3000, patience=20, min_epochs=200, log_path=lg, ckpt=ck, verbose=True)
print(f"[B3] trained: {res['epochs']} ep, val {res['val_loss']:.6e}, {res['wall_sec']:.0f}s", flush=True)

fits, llv, bstar, kron_K = A.gmm_selection("D2", PRIOR, NR)
fam, K = ("kron", kron_K) if bstar == "kron" else ("full", int(bstar[3:]))
gp = C.GMMPriorB(NR, NT, fits[(fam, K)]["covs"], fits[(fam, K)]["pi"])
print(f"[B3] GMM b* = {bstar} ({fam} K={K}, ll_val {llv[bstar]:.3f})", flush=True)
G = score.gb_prime(ck, gp, "D2", NR, NT, prior=PRIOR, device="cuda")
out = os.path.join(C.CONF, "results", "gate_D2.txt")
with open(out, "w") as f:
    f.write(C.header("D2", extra=[
        "content     : GB' (04_SPEC §6) -- held-out denoising NMSE of the GMM prior vs the diffusion prior",
        "              on the SAME frozen D2 sigma grid.  REPORT ONLY: never used to select anything.",
        "*** The diffusion model here did NOT pass the D1 gates (best GC 0.2241 vs 0.15 over 959 trials).",
        "    It is NOT an arm in any BLER table; M-ours-dscore stays BLOCKED on both testbeds. ***",
        f"architecture: copied verbatim from the best-D1-gate-score configuration, NOT re-searched (04_SPEC §6)",
        f"              {HP}",
        f"GMM b*      : {bstar} ({fam} K={K}), selected by validation log-likelihood only",
    ]) + "\n\n" + C.D2_WARNING + "\n\n")
    f.write(f"{'k':>3} {'sigma':>11} {'nu':>11} {'nmse_gmm':>12} {'nmse_diff':>12} {'diff/gmm':>10}\n")
    for r in G.get("per_sigma", G.get("rows", [])):
        g, d = r.get("nmse_gmm"), r.get("nmse_model", r.get("nmse_diff"))
        f.write(f"{int(r['k']):>3} {r['sigma']:>11.4e} {r['nu']:>11.4e} {g:>12.5e} {d:>12.5e} {d/g:>10.4f}\n")
    f.write(f"\nsummary: {dict((k, v) for k, v in G.items() if not isinstance(v, (list, dict)))}\n")
print(f"[B3] -> {out}", flush=True)
