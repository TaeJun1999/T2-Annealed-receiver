"""conf/code/hisnr_report.py -- NEXT_EXPERIMENTS_HISNR16e4 report (REPORT-ONLY; no registered label): per SNR the failures / n
and 95% Wilson interval of every arm at iteration 16, and the paired V1-vs-b* discordant counts with the exact two-sided sign
test (analysis.paired / sign_p -- shown, not judged).  A raised block counts as a failure (01_RULES §4).
    python code/hisnr_report.py --raw raw_HSB16e4k --cell C2 --prior S2
"""
import argparse
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import common as C
from analysis import load_raw, paired, sign_p


def wilson(k, n, z=1.959963984540054):
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True); ap.add_argument("--cell", required=True); ap.add_argument("--prior", required=True)
    a = ap.parse_args()
    d, _, warns = load_raw("D2", root=os.path.join(C.CONF, a.raw))
    keys = sorted((k for k in d if k[:2] == (a.cell, a.prior)), key=lambda k: k[2])
    want = ("M-ours-dscore-C-V1", "M-ours-bstar", "R2-ours-G", "R1-turbo", "R3-bigamp", "R5-genie")
    arms = [x for x in want if x in d[keys[0]]]
    if warns or len(arms) != len(want) or not keys:
        print(f"# hisnr_report {a.raw}: load_raw warnings {warns} / missing arms {set(want) - set(arms)} -> no report"); sys.exit(1)
    print(f"# hisnr_report {a.raw} {a.cell} {a.prior}; load_raw warnings: {len(warns)}; REPORT-ONLY (HISNR16e4 §1)")
    for k in keys:
        n = len(np.asarray(d[k][arms[0]]["blk_err"]))
        print(f"SNR {k[2]:+.0f} dB, n = {n}:")
        for x in arms:
            e = np.asarray(d[k][x]["blk_err"], float)[:, -1]; e = np.where(np.isfinite(e), e, 1.0); f = int(e.sum())
            lo, hi = wilson(f, n); print(f"    {x:<20} {f:6d} / {n}  BLER {f / n:.2e}  95% [{lo:.2e}, {hi:.2e}]")
        a_, b_ = paired(d[k], "M-ours-bstar", "M-ours-dscore-C-V1")[:2]
        print(f"    paired b* only : V1 only = {a_}:{b_}, exact two-sided sign p = {sign_p(a_, b_):.2g} (report)")


if __name__ == "__main__":
    main()
