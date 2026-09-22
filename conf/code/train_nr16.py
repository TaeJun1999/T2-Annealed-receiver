"""(10_SPEC_stageC §7) Train the D2 score prior on the Nr=16 array of cell C6.

This is run_d2_sx.py with exactly two differences, both forced by the array and neither a search:
  NR = 16                  the net's input dimension follows as 2*Nr*Nt = 128 (score.make_model)
  sigma_tag = "NR16"       the sigma grid is the one MEASURED on this array; the frozen D2 grid was
                           measured on Nr=8 and is a different ruler (04_SPEC §3, 10_SPEC §7)

The hyper-parameters are the frozen best-D1-gate configuration, copied verbatim and NOT re-searched
(04_SPEC §6, 01_RULES A2).  If this recipe fails to converge at 2x the input dimension, the §3d
fallback ladder applies and a failure is reported as a failure.

GATE STATUS: there is no D1 sibling for an Nr=16 array, so this checkpoint is UNGATED.  §7 registers
that in advance: the C6 numbers are a geometry-axis measurement, never an arm verdict.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import common as C
import score
import arms as A

HP = dict(arch="dit", param="vp", domain="angle", lr=0.002238046051591068, ema=0.999,
          batch=256, emb=256, width=64, depth=6, heads=8, patch=1)
NR, NT, PRIOR, STAG = 16, 4, "S2", "NR16"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ntrain", type=int, default=10000)
    ap.add_argument("--attempt", type=int, default=1)
    ap.add_argument("--n-eval", type=int, default=4096)
    a = ap.parse_args()
    tag = f"NR16_N{a.ntrain}_a{a.attempt}"
    ck = os.path.join(C.CONF, "ckpt", f"d2sx_{tag}.pt")
    lg = os.path.join(C.CONF, "logs", f"train_d2sx_{tag}.log")
    nu, sg = __import__("sigma").load("D2", STAG)
    print(f"[nr16] ntrain={a.ntrain} attempt={a.attempt} Nr={NR} dim={2*NR*NT} "
          f"sigma grid '{STAG}' [{sg.min():.4e}, {sg.max():.4e}] ({len(sg)} pts)", flush=True)
    res = score.train(f"D2SXNR16{a.ntrain}", a.attempt, "D2", PRIOR, NR, NT, device="cuda", hp=HP,
                      resume=True, ntrain=a.ntrain, max_epochs=3000, patience=20, min_epochs=200,
                      log_path=lg, ckpt=ck, verbose=False, sigma_tag=STAG)
    print(f"[nr16] trained {res['epochs']} ep, val {res['val_loss']:.5e}, {res['wall_sec']:.0f}s, "
          f"stopped_by={res.get('stopped_by')}", flush=True)

    # GB' against the equal-budget GMM b* on THIS array -- report-only, same quantity as run_d2_sx.py.
    # The Nr=16 fits live in the NR16-tagged directory (fit_gpu.py -> runner._init("NR16")); arms.D2_FITS
    # defaults to the untagged Nr=8 one, where this used to die with FileNotFoundError (review_next S7-a).
    A.D2_FITS = os.path.join(C.CONF, "results", "gmm_fits_D2_NR16")
    fits, llv, bstar, kron_K = A.gmm_selection("D2", PRIOR, NR, a.ntrain)
    fam, K = ("kron", kron_K) if bstar == "kron" else ("full", int(bstar[3:]))
    gp = C.GMMPriorB(NR, NT, fits[(fam, K)]["covs"], fits[(fam, K)]["pi"])
    G = score.gb_prime(ck, gp, "D2", NR, NT, prior=PRIOR, n_eval=a.n_eval, device="cuda",
                       sigma_tag=STAG, gmm_device="cuda")      # GMM posterior mean batched on GPU, CPU-checked
    rat = np.array([r["nmse_model"] / r["nmse_gmm"] for r in G["per_sigma"]])
    chk = max(r.get("gmm_gpu_check_rel", 0.0) for r in G["per_sigma"])
    print(f"[nr16] GMM on GPU, max rel diff vs CPU loop on the checked samples {chk:.2e} (limit 1e-10)", flush=True)
    print(f"[nr16] GMM b* = {bstar} ({fam} K={K}) @N={a.ntrain} | diff/gmm min {rat.min():.4f} "
          f"max {rat.max():.4f} median {np.median(rat):.4f} | equal_budget=True", flush=True)
    np.savez_compressed(os.path.join(C.CONF, "results", f"d2_gbprime_{tag}.npz"),
                        nu=[r["nu"] for r in G["per_sigma"]], sigma=[r["sigma"] for r in G["per_sigma"]],
                        nmse_gmm=[r["nmse_gmm"] for r in G["per_sigma"]],
                        nmse_model=[r["nmse_model"] for r in G["per_sigma"]])
    return 0


if __name__ == "__main__":
    sys.exit(main())
