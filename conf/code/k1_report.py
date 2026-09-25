"""conf/code/k1_report.py -- NEXT_EXPERIMENTS_K1K2 §1.2 report: BR-S (raw_review_next_K1) against V1 / b* / R5-genie
(re-run in raw_review_next_K1 and checked bit-identical against raw_review_next_P3ref) and LO-S-d0.001 (raw_review_next_LO,
32-iteration run, index 15 = @16) at the SAME trials.  Fail-closed: nothing is printed for a point whose acceptance fails.
Writes results/review_next/<save> (overwrites).  Report-only.
    python conf/code/k1_report.py [--points C2:-3:3200:1280 C5:-3:3200:640] [--save K1_report.txt]
"""
import argparse
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import numpy as np
from analysis import sign_p

PAT = re.compile(r"_snr(-?\d+)_skip(\d+)_n(\d+)\.npz$")
SRC = {"M-ours-bstar": "raw_review_next_K1", "M-ours-dscore-C-V1": "raw_review_next_K1",
       "R5-genie": "raw_review_next_K1", "LO-S-d0.001": "raw_review_next_LO", "BR-S": "raw_review_next_K1"}
CHUNK = 20


def fails(rawdir, cell, snr, arm, it=15):
    out = {}
    for f in glob.glob(os.path.join(C.CONF, rawdir, f"D2_{cell}_*_snr{snr:g}_skip*_n*.npz")):
        s = int(PAT.search(f).group(2)); d = np.load(f, allow_pickle=True)
        if f"{arm}|blk_err" not in d.files:
            continue
        v = d[f"{arm}|blk_err"][:, it]
        for i in range(len(v)):
            out[s + i] = 1.0 if not np.isfinite(v[i]) else float(v[i])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--points", nargs="+", default=["C2:-3:3200:1280", "C5:-3:3200:640"])
    ap.add_argument("--save", default=None)
    a = ap.parse_args()
    L = ["# K1 (NEXT_EXPERIMENTS_K1K2 §1.2): BR-S vs V1 / b* / LO-S / genie at the same trials, @16, house sign test"]
    import diag_prior_swap as D
    for pt in a.points:
        cell, snr, skip0, n = pt.split(":"); snr, skip0, n = float(snr), int(skip0), int(n)
        ok, prob, ms = D.accept("raw_review_next_K1", cell, snr, skip0, n, CHUNK)
        # construction identity of the arms shared with P3ref (V1, b*, genie): every KEYS_RAW field bit-identical @1..16
        X, R = D.load("raw_review_next_K1", cell, snr), D.load("raw_review_next_P3ref", cell, snr)
        shared = sorted(set(X) & set(R)); worst = {}
        for t in shared:
            for k in X[t]:
                if k in R[t] and k.split("|")[1] in C.KEYS_RAW:
                    x, y = np.asarray(X[t][k], float), np.asarray(R[t][k], float)[: len(np.asarray(X[t][k]))]
                    worst[k.split("|")[0]] = max(worst.get(k.split("|")[0], 0.0), float(np.max(np.abs(np.nan_to_num(x, nan=1e300) - np.nan_to_num(y, nan=1e300)))))
        ident = len(shared) == n and {"M-ours-bstar", "M-ours-dscore-C-V1", "R5-genie"} <= set(worst) and all(v == 0.0 for v in worst.values())
        F = {arm: fails(src, cell, snr, arm) for arm, src in SRC.items()}
        tr = [t for t in range(skip0, skip0 + n) if all(t in F[arm] for arm in F)]
        L.append(f"\n== {cell} {snr:g} dB trials {skip0}..{skip0 + n - 1} ==\n"
                 f"   acceptance: chunks/meta {'PASS' if ok else 'FAIL: ' + '; '.join(prob)}; V1/b*/genie vs P3ref shared {len(shared)}/{n}, "
                 f"max |diff| {worst} -> {'PASS' if ident else 'FAIL'}; LO-S shared {len(tr)}/{n}; arms {ms[0]} meta {ms[1]}")
        if not (ok and ident and len(tr) == n):
            L.append("   ** nothing below is read **")
            continue
        be = {arm: np.array([F[arm][t] for t in tr]) for arm in F}
        g, r = be["M-ours-bstar"].sum(), be["R5-genie"].sum()
        for arm in ("M-ours-bstar", "M-ours-dscore-C-V1", "BR-S", "LO-S-d0.001", "R5-genie"):
            L.append(f"   {arm:<20} {int(be[arm].sum()):>5} ({be[arm].mean():.4f})   gap position {(g - be[arm].sum()) / (g - r):+.3f}")
        for x, y, lab in (("M-ours-dscore-C-V1", "BR-S", "R1'"), ("BR-S", "LO-S-d0.001", "R2'"), ("BR-S", "R5-genie", "report"),
                          ("M-ours-bstar", "BR-S", "report")):
            p, q = int(np.sum((be[x] == 1) & (be[y] == 0))), int(np.sum((be[x] == 0) & (be[y] == 1)))
            L.append(f"   {lab:<7} {x:>20} -> {y:<14} {p:>4}:{q:<4} p={sign_p(p, q):.2g}" + ("  UNDECIDED (n_d < 6)" if p + q < 6 else ""))
        md, ex, gd = [], 0, 0
        for f in glob.glob(os.path.join(C.CONF, "raw_review_next_K1", f"D2_{cell}_*_snr{snr:g}_skip*_n*.npz")):
            d = np.load(f, allow_pickle=True)
            md += list(d["BR-S|mc_disagree"]); ex += int(d["BR-S|failed"].sum()); gd += int(np.nansum(d["BR-S|guardH"]))
        L.append(f"   BR-S exceptions {ex}, F3 guard {gd}; chain spread (median over queries per block): median "
                 f"{np.nanmedian(md):.2e}, p90 {np.nanquantile(md, .9):.2e}")
    txt = "\n".join(L)
    print(txt)
    if a.save:
        open(os.path.join(C.CONF, "results", "review_next", a.save), "w").write(txt + "\n")


if __name__ == "__main__":
    main()
