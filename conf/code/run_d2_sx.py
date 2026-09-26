"""D2 diffusion prior: multi-seed verification of GB' and the budget curve.

  --ntrain N       training samples for the DIFFUSION model
  --attempt K      changes the training seed (score.train derives its seed from the attempt index)
  --gmm-ntrain M   which GMM fit to compare against.  For an EQUAL-BUDGET comparison pass M == N.
                   When the two differ the row is written with equal_budget=False and must be read as a
                   diffusion-only measurement, never as a prior-vs-prior comparison.

  --prior S2c      D3 (user decision 2026-09-25 CDT): the D2 prior variant with alpha_l ~ CN(0, p_l) (d2.py).  Default S2 =
                   every name, seed and path exactly as before.  For S2c EVERY output carries the prior, so a D3 file can
                   never collide with a D2 one: rung D2SXS2c<N> (-> its own training seed, score._rung_ix), checkpoint
                   ckpt/d2sx_S2c_N<N>_a<k>[_fb<j>].pt, log logs/train_d2sx_S2c_..., results/d2_gbprime_S2c_....npz and
                   results/d2_gbprime_S2c.csv; the sigma grid is the one measured for S2c (results/sigma_grid_D2_S2c.npz,
                   `runner.py sigma --testbed D2 --prior S2c --cell C1 C2 --tag S2c`), recorded in the checkpoint.
  --prior SV8e     the second testbed SV (user decision 2026-09-26 00:06 CDT; code/sv.py), same scheme with SV8e in every
                   name: rung D2SXSV8e<N>, ckpt/d2sx_SV8e_N<N>_a<k>[_fb<j>].pt, logs/train_d2sx_SV8e_..., results/
                   d2_gbprime_SV8e[_...].{csv,npz}, sigma grid results/sigma_grid_D2_SV8e.npz (`runner.py sigma --testbed D2
                   --prior SV8e --cell C1 C2 --tag SV8e`).
  --no-gbprime    train (or resume) only, skip the GB' step -- the D3 queue (run_d3.sh) computes GB' once the GMM grid is
                   complete, so GB' can never be taken against a partial grid.

Architecture is the best-D1-gate-score configuration, copied verbatim and never re-searched (04_SPEC §6).
Everything here is REPORT-ONLY: the pre-registered arm comparison stays at N = 1e4.
"""
import argparse, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, common as C, score, arms as A

HP = dict(arch="dit", param="vp", domain="angle", lr=0.002238046051591068, ema=0.999,
          batch=256, emb=256, width=64, depth=6, heads=8, patch=1)
NR, NT, PRIOR = 8, 4, "S2"
CSV = os.path.join(C.CONF, "results", "d2_gbprime.csv")

ap = argparse.ArgumentParser()
ap.add_argument("--ntrain", type=int, default=10000)
ap.add_argument("--attempt", type=int, default=1)
ap.add_argument("--gmm-ntrain", type=int, default=None)
ap.add_argument("--n-eval", type=int, default=4096)
ap.add_argument("--tag", default=None, help="GMM fits dir tag (runner._init: results/gmm_fits_D2_<tag>); default = the "
                                           "untagged dir, as before (NEXT_EXPERIMENTS_B32e4: equal-budget GB' needs it)")
ap.add_argument("--prior", default="S2", choices=("S2", "S2c", "SV8e"),
                help="S2 = D2 (default, unchanged); S2c = D3; SV8e = second testbed SV (sv.py)")
ap.add_argument("--no-gbprime", action="store_true", help="train/resume only; no GB' (default: GB' as before)")
ap.add_argument("--fallback", type=int, default=1, choices=(1, 2, 3),
                help="10_SPEC §3d ladder after a DIVERGED/aborted run: 2 = grad-norm clip 1.0, 3 = + lr/3 (score.*_LADDER; "
                     "same data stream, checkpoint suffix _fb<k>).  1 = the frozen recipe (default, unchanged)")
a = ap.parse_args()
if a.tag:
    import runner
    runner._init(a.tag)                        # A.D2_FITS -> results/gmm_fits_D2_<tag>
gmm_n = a.gmm_ntrain or a.ntrain
PRIOR = a.prior
PT = "" if PRIOR == "S2" else PRIOR                      # "" keeps every S2 name / rung / grid exactly as before
if PT:
    CSV = os.path.join(C.CONF, "results", f"d2_gbprime_{PT}.csv")

tag = (f"{PT}_" if PT else "") + f"N{a.ntrain}_a{a.attempt}" + (f"_fb{a.fallback}" if a.fallback > 1 else "")
GRAD_CLIP = score.GRAD_CLIP_LADDER[a.fallback - 1]
HP["lr"] = HP["lr"] / score.LR_DIV_LADDER[a.fallback - 1]
ck = os.path.join(C.CONF, "ckpt", f"d2sx_{tag}.pt")
lg = os.path.join(C.CONF, "logs", f"train_d2sx_{tag}.log")
print(f"[d2sx] ntrain={a.ntrain} attempt={a.attempt} gmm_ntrain={gmm_n} n_eval={a.n_eval}"
      + (f" prior={PRIOR} ckpt={ck} sigma_tag={PT}" if PT else ""), flush=True)
res = score.train(f"D2SX{PT}{a.ntrain}", a.attempt, "D2", PRIOR, NR, NT, device="cuda", hp=HP, resume=True,
                  ntrain=a.ntrain, max_epochs=3000, patience=20, min_epochs=200, log_path=lg, ckpt=ck,
                  verbose=False, **({"grad_clip": GRAD_CLIP} if a.fallback > 1 else {}),
                  **({"sigma_tag": PT} if PT else {}))
print(f"[d2sx] trained {res['epochs']} ep, val {res['val_loss']:.5e}, {res['wall_sec']:.0f}s", flush=True)
if PT or a.no_gbprime:
    print(f"[d2sx] stopped_by={res.get('stopped_by')} aborted={res.get('aborted')} best_epoch={res.get('best_epoch')}",
          flush=True)
if a.no_gbprime:
    sys.exit(0)

fits, llv, bstar, kron_K = A.gmm_selection("D2", PRIOR, NR, gmm_n)
fam, K = ("kron", kron_K) if bstar == "kron" else ("full", int(bstar[3:]))
gp = C.GMMPriorB(NR, NT, fits[(fam, K)]["covs"], fits[(fam, K)]["pi"])
G = score.gb_prime(ck, gp, "D2", NR, NT, prior=PRIOR, n_eval=a.n_eval, device="cuda")
rows = G["per_sigma"]
rat = np.array([r["nmse_model"] / r["nmse_gmm"] for r in rows])
print(f"[d2sx] GMM b* = {bstar} ({fam} K={K}) @N={gmm_n} | diff/gmm min {rat.min():.4f} "
      f"max {rat.max():.4f} median {np.median(rat):.4f} | equal_budget={a.ntrain == gmm_n}", flush=True)
new = not os.path.exists(CSV)
with open(CSV, "a") as f:
    if new:
        f.write("ntrain,attempt,gmm_ntrain,equal_budget,epochs,val_loss,gmm_bstar,gmm_K,n_eval,"
                "ratio_min,ratio_max,ratio_median,worst_excess\n")
    f.write(f"{a.ntrain},{a.attempt},{gmm_n},{a.ntrain == gmm_n},{res['epochs']},{res['val_loss']:.6e},"
            f"{bstar},{K},{a.n_eval},{rat.min():.6f},{rat.max():.6f},{np.median(rat):.6f},"
            f"{float(G['worst_excess']):.6f}\n")
np.savez_compressed(os.path.join(C.CONF, "results", f"d2_gbprime_{tag}.npz"),
                    nu=[r["nu"] for r in rows], sigma=[r["sigma"] for r in rows],
                    nmse_gmm=[r["nmse_gmm"] for r in rows], nmse_model=[r["nmse_model"] for r in rows])
