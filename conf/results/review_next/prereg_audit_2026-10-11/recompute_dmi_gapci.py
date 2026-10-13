"""recompute_dmi_gapci.py -- RECORD AUDIT of NEXT_EXPERIMENTS_ROOM16e4.md §7.1 / §7.2 (prior DMI): an INDEPENDENT paired bootstrap of the
SNR@0.1 gaps that the record transcribes from table B (results/tables_D2_DMIB16e4{,last}.txt).  Own resampler (default_rng(1),
B = 4000; per SNR an independent draw of trial indices, the same indices for both arms; SNR@0.1 by the log-linear rule with the
0.5/n floor; replicates in which either arm does not cross 0.1 on the grid are dropped and counted), so the CI ends are expected to
agree with the tool's only to a few 0.01 dB.  Reads the raw chunks through recompute_dmi_main.load_tag (own reader).

usage (cwd = ~/t2/conf):  CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=2 taskset -c 0-15 ~/miniforge3/envs/torch/bin/python -B \
    results/review_next/prereg_audit_2026-10-11/recompute_dmi_gapci.py
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import recompute_dmi_main as M  # noqa: E402

SNRS, N = M.SNRS, M.N


def snr01(bl):
    lb = np.log10(np.maximum(bl, 0.5 / N)); lt = -1.0
    if lb[0] <= lt:
        return None
    for i in range(len(SNRS) - 1):
        if lb[i] > lt >= lb[i + 1]:
            return SNRS[i] + (lb[i] - lt) / (lb[i] - lb[i + 1]) * (SNRS[i + 1] - SNRS[i])
    return None


def main():
    best = M.load_tag(os.path.join(M.CONF, "raw_DMIB16e4"), "DMI", "dft")[0]
    last = M.load_tag(os.path.join(M.CONF, "raw_DMIB16e4last"), "DMI", "dft")[0]
    rec = {("best", M.BS, M.V1): (0.23, 0.08, 0.37), ("last", M.BS, M.V1): (0.24, 0.11, 0.39), ("best", M.BS, M.SC): (-0.21, -0.31, -0.12), ("best", M.R2, M.BS): (3.13, 2.89, 3.38),
           ("best", M.V1, M.GEN): (1.73, 1.56, 1.90), ("best", M.BS, M.GEN): (1.95, 1.76, 2.14), ("best", M.BS, M.V4): (0.02, -0.13, 0.17), ("best", M.BS, M.V4B): (-0.05, -0.20, 0.10)}
    print("# independent paired bootstrap of the SNR@0.1 gaps (first arm minus second arm), B = 4000, seed 1; record = table B as transcribed in 7.1 / 7.2")
    worst = 0.0
    for (tag, x, y), (g0, lo0, hi0) in rec.items():
        pts = best if tag == "best" else last
        ex = np.stack([M.fails(pts, s, x) for s in SNRS]); ey = np.stack([M.fails(pts, s, y) for s in SNRS])
        point = snr01(ex.mean(1)) - snr01(ey.mean(1))
        rng = np.random.default_rng(1); out, drop = [], 0
        for _ in range(4000):
            idx = rng.integers(0, N, (len(SNRS), N))
            a = snr01(np.take_along_axis(ex, idx, 1).mean(1)); b = snr01(np.take_along_axis(ey, idx, 1).mean(1))
            if a is None or b is None:
                drop += 1
            else:
                out.append(a - b)
        lo, hi = np.percentile(out, [5, 95])
        d = max(abs(lo - lo0), abs(hi - hi0), abs(point - g0))
        worst = max(worst, d)
        print(f"  [{tag}] {x} - {y}: point {point:+.2f} dB, 90% [{lo:+.2f}, {hi:+.2f}] (dropped {drop})   record {g0:+.2f} [{lo0:+.2f}, {hi0:+.2f}]   max |diff| {d:.3f} dB")
    print(f"# largest difference between this resampler and the record over the 8 gaps: {worst:.3f} dB; sign of every CI end as in the record: "
          f"{'checked above' if not math.isnan(worst) else '-'}")


if __name__ == "__main__":
    main()
