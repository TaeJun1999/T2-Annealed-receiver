"""(review_next, groundwork for a future P3 pre-registration) Loop dynamics of the JCED receiver on the DEVELOPMENT set.

Descriptive only -- decides nothing.  Reads the per-iteration channel beliefs h_post^t that diag_p1_cavity.py stored for
V1, V0, M-ours-bstar-scalar and M-ours-bstar (dev trials 2560..3199, n=640 per point) and asks what the loop is DOING on
the blocks it fails: settled at a fixed point, alternating in a 2-cycle, or still moving.  This is the diagnostic the
record lacked when it called the tail "a bad fixed point" (REVIEW_AUDIT R-10.2).  It also lists which RECEIVER-OBSERVABLE
per-block signals separate final failures (AUC, report-only) -- the candidates a restart/damping trigger could use.

State residual  r_t  = ||h^t - h^{t-1}|| / ||h^t||        (t = 2..16)
2-cycle residual c_t = ||h^t - h^{t-2}|| / ||h^t||        (t = 3..16)
End-state class over iterations 13..16 (thresholds fixed here, before looking at the numbers):
  settled   : max r_13..16 < 1e-3
  2-cycle   : max c_15..16 < 1e-3  and  min r_15..16 > 1e-2
  slow      : max r_13..16 < 1e-2  (and not settled)
  moving    : everything else
Failure = blk_err at iteration 16 (the reported BLER).  Observable signals only (no h_true, no bits): r_16, alphaD@16,
tauL_gmean@16, nuE@16, and for the scalar-cavity arms nu_q@16 and alphaH@16, clip for V0/V1.

    ~/miniforge3/envs/torch/bin/python conf/code/diag_p3_loop.py
"""
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from scipy.stats import mannwhitneyu
import common as C

ARMS = ("M-ours-dscore-C-V1", "M-ours-dscore-C-V0", "M-ours-bstar-scalar", "M-ours-bstar")
D = os.path.join(C.CONF, "results", "review_next")
EPS = 1e-300


def auc(x, y):
    """P(signal on a failed block > signal on a decoded block); 0.5 = no separation.  NaN-safe."""
    ok = np.isfinite(x)
    x, y = x[ok], y[ok]
    n1, n0 = int(y.sum()), int((1 - y).sum())
    if n1 == 0 or n0 == 0:
        return float("nan"), n1
    return float(mannwhitneyu(x[y == 1], x[y == 0]).statistic / (n1 * n0)), n1


def main():
    out = [C.header("D2", extra=["content     : review_next P3 groundwork -- loop dynamics on the DEVELOPMENT set "
                                 "(descriptive, decides nothing); source = diag_p1_cavity merged npz"])]
    w = out.append
    for f in sorted(glob.glob(os.path.join(D, "p1_cavity_D2_*.npz"))):
        z = np.load(f)
        w(f"\n=== {z['meta|point']}  (n = {len(z['trial'])}, trials {int(z['trial'].min())}..{int(z['trial'].max())})")
        w(f"{'arm':<22} {'fail':>5} | {'settled':>15} {'2-cycle':>15} {'slow':>15} {'moving':>15} | "
          f"{'lost 8->16':>10} {'rescued':>8} | AUC(fail) of observable signals @16")
        for a in ARMS:
            if f"{a}|hpost" not in z.files:
                continue
            h = z[f"{a}|hpost"]                                            # (n, 16, N)
            y = np.asarray(z[f"{a}|fail"], dtype=float)
            nrm = np.maximum(np.linalg.norm(h, axis=2), EPS)
            r = np.full(h.shape[:2], np.nan); r[:, 1:] = np.linalg.norm(h[:, 1:] - h[:, :-1], axis=2) / nrm[:, 1:]
            c = np.full(h.shape[:2], np.nan); c[:, 2:] = np.linalg.norm(h[:, 2:] - h[:, :-2], axis=2) / nrm[:, 2:]
            rmax = np.nanmax(r[:, 12:16], axis=1)
            settled = rmax < 1e-3
            cyc = (~settled) & (np.nanmax(c[:, 14:16], axis=1) < 1e-3) & (np.nanmin(r[:, 14:16], axis=1) > 1e-2)
            slow = (~settled) & (~cyc) & (rmax < 1e-2)
            moving = ~(settled | cyc | slow)
            be = z[f"{a}|log_blk_err"]
            lost = int(((be[:, 7] == 0) & (be[:, 15] == 1)).sum()); resc = int(((be[:, 7] == 1) & (be[:, 15] == 0)).sum())
            cells = []
            for m in (settled, cyc, slow, moving):
                k = int(m.sum()); kf = int((m & (y == 1)).sum())
                cells.append(f"{k:>4} (f {kf:>3})")
            sig = {"r16": r[:, 15], "alphaD": z[f"{a}|log_alphaD"][:, 15], "tauL": z[f"{a}|log_tauL_gmean"][:, 15],
                   "nuE": z[f"{a}|log_nuE"][:, 15]}
            if f"{a}|nu_q" in z.files:
                sig["nu_q"] = z[f"{a}|nu_q"][:, 15]; sig["alphaH"] = z[f"{a}|alphaH"][:, 15]
            if f"{a}|clip" in z.files and a.startswith("M-ours-dscore"):
                sig["clip"] = z[f"{a}|clip"][:, 15].astype(float)
            aucs = "  ".join(f"{k} {auc(v.astype(float), y)[0]:.2f}" for k, v in sig.items())
            w(f"{a:<22} {int(y.sum()):>5} | " + " ".join(f"{x:>15}" for x in cells) + f" | {lost:>10} {resc:>8} | {aucs}")
        # the headline question in one line per arm: where do the FAILURES sit?
    w("\nclasses: settled = max r_13..16 < 1e-3; 2-cycle = max c_15..16 < 1e-3 and min r_15..16 > 1e-2; slow = max r < 1e-2;")
    w("         moving = rest.  '(f k)' = failures in that class.  lost 8->16 = decoded at iteration 8, failed at 16; rescued = opposite.")
    w("AUC: P(signal larger on a failed block); 0.5 = no separation, <0.5 = smaller on failures.  Receiver-observable signals only.")
    w("Descriptive groundwork for a P3 pre-registration; dev trials used here must NOT be reused to judge a P3 rule (use skip >= 3200).")
    txt = "\n".join(out) + "\n"
    with open(os.path.join(D, "p3_loop_groundwork.txt"), "w") as fh:
        fh.write(txt)
    print(txt)


if __name__ == "__main__":
    main()
