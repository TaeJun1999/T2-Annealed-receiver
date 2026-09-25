"""conf/code/recovery_ci.py -- genie-gap recovery R = (b* - V1) / (b* - genie) from failure counts @16, with a PAIRED
bootstrap 90% CI (NEXT_EXPERIMENTS_C6B16e4 §1 "회수율 대역": trial indices resampled with replacement, the three arms
resampled TOGETHER, B = 2000, numpy.random.default_rng(20260926), percentiles 5 / 95).  Report-only; R is not a registered
judgement statistic anywhere.  Per decision SNR and on the pooled failure counts of the listed SNRs.

    python conf/code/recovery_ci.py --raw raw_NR16B16e4 --cell C6 --snrs -3 0 3
    python conf/code/recovery_ci.py --raw raw_B32e4 --cell C2 --snrs -3 0 3         (the C2 budgets, same computation)
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import numpy as np
from analysis import load_raw

ARMS = ("M-ours-bstar", "M-ours-dscore-C-V1", "R5-genie")


def fails(data, cell, snr, arm, it=-1):
    key = [k for k in data if k[0] == cell and k[2] == snr][0]
    v = np.asarray(data[key][arm]["blk_err"])[:, it]
    return np.where(np.isfinite(v), v, 1.0)                     # a raised block is a failure (01_RULES §4)


def rec(b, v, g):
    d = b.sum() - g.sum()
    return (b.sum() - v.sum()) / d if d > 0 else np.nan


def boot(cols, B, seed):
    rng = np.random.default_rng(seed)
    n = len(cols[0][0])
    out = np.empty(B)
    for i in range(B):
        idx = rng.integers(0, n, n)
        bs = sum(b[idx].sum() for b, _, _ in cols); vs = sum(v[idx].sum() for _, v, _ in cols)
        gs = sum(g[idx].sum() for _, _, g in cols)
        out[i] = (bs - vs) / (bs - gs) if bs - gs > 0 else np.nan
    ok = np.isfinite(out)
    return np.percentile(out[ok], [5, 95]) if ok.sum() else (np.nan, np.nan), int((~ok).sum())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--cell", required=True)
    ap.add_argument("--snrs", type=float, nargs="+", required=True)
    ap.add_argument("--B", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=20260926)
    a = ap.parse_args()
    data, _, _ = load_raw("D2", root=os.path.join(C.CONF, a.raw))
    print(f"# recovery R = (b* - V1)/(b* - genie) @16, {a.raw} {a.cell}, paired bootstrap B={a.B} seed={a.seed}, 90% CI")
    cols = []
    for s in a.snrs:
        b, v, g = (fails(data, a.cell, s, arm) for arm in ARMS)
        cols.append((b, v, g))
        (lo, hi), nn = boot([(b, v, g)], a.B, a.seed)
        print(f"  {s:+.0f} dB  b* {int(b.sum())}  V1 {int(v.sum())}  genie {int(g.sum())}  n={len(b)}  "
              f"R = {rec(b, v, g):.3f}  [90% {lo:.3f}, {hi:.3f}]" + (f"  ({nn} replicates undefined)" if nn else ""))
    (lo, hi), nn = boot(cols, a.B, a.seed)
    B_, V_, G_ = (sum(c[i].sum() for c in cols) for i in range(3))
    print(f"  pooled {len(cols)} SNRs  b* {int(B_)}  V1 {int(V_)}  genie {int(G_)}  R = {(B_ - V_) / (B_ - G_):.3f}  "
          f"[90% {lo:.3f}, {hi:.3f}]" + (f"  ({nn} replicates undefined)" if nn else ""))


if __name__ == "__main__":
    main()
