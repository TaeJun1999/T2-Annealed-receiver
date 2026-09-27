"""conf/code/pair_cross.py -- table B across two raw sets of the SAME trials (NEXT_EXPERIMENTS_PILOT16e4 §1).

A pilot-only tag holds only V1-pilot / bstar-pilot / R5-genie; the loop arms live in the base tag's raw.  Trial streams are
fixed by (testbed, prior, Nr, T, Tp, SNR), so the two raw sets are paired trial by trial.  The script merges them per point
(arm names are distinct) and reuses analysis.decision_points / paired / gain unchanged, after checking (integrity; any
failure -> exit 1 BEFORE any label is computed):
  - the same (cell, prior) point set in both raw sets, the cell's full SNR grid, no load_raw warning,
  - R5-genie identical in both raw sets at every trial and iteration (same trials),
  - V1-pilot @1 == M-ours-dscore-C-V1 @1 and bstar-pilot @1 == M-ours-bstar @1 (the pilot-only arms' first iteration is
    the loop arms' first iteration; PilotSitePrior), over the trials where neither arm raised ("<arm>|failed"),
  - the pilot-only arms' channel estimate is fixed: nmse[:, t] == nmse[:, 0] for every iteration t (non-raised trials).
A raised trial stays a block error (analysis.load_raw: NaN -> 1.0) and is counted in the header.
    python code/pair_cross.py --base raw_B16e4k --pilot raw_PILB16e4k --cell C2 --prior S2
"""
import argparse
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import numpy as np
from analysis import load_raw, decision_points, paired, gain, sign_p, MIN_DISC

PAIRS = (("V1-pilot", "M-ours-dscore-C-V1", "P1: pilot-only V1 -> loop V1"),
         ("bstar-pilot", "V1-pilot", "P2: pilot-only b* -> pilot-only V1"),
         ("bstar-pilot", "M-ours-bstar", "report: pilot-only b* -> loop b*"),
         ("V1-pilot", "M-ours-bstar", "report: pilot-only V1 -> loop b*"))
SAME1 = (("V1-pilot", "M-ours-dscore-C-V1"), ("bstar-pilot", "M-ours-bstar"))
SHOW = ("R0-pilot", "M-ours-bstar", "bstar-pilot", "M-ours-dscore-C-V1", "V1-pilot", "R5-genie")


def same(x, y):
    return np.array_equal(np.nan_to_num(np.asarray(x), nan=1e300), np.nan_to_num(np.asarray(y), nan=1e300))


def failed(d, arm):
    return np.asarray(d[arm].get("failed", np.zeros(len(d[arm]["blk_err"])))) > 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True); ap.add_argument("--pilot", required=True)
    ap.add_argument("--cell", required=True); ap.add_argument("--prior", required=True)
    a = ap.parse_args()
    b, _, wb = load_raw("D2", root=os.path.join(C.CONF, a.base))
    p, _, wp = load_raw("D2", root=os.path.join(C.CONF, a.pilot))
    sel = lambda d: sorted((k for k in d if k[:2] == (a.cell, a.prior)), key=lambda k: k[2])
    keys = sel(p)
    head = subprocess.run(["git", "-C", C.CONF, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    bad = []
    if [k[2] for k in keys] != [k[2] for k in sel(b)] or [k[2] for k in keys] != [float(s) for s in C.CELLS[a.cell]["snrs"]]:
        bad.append(f"point set {[k[2] for k in keys]} != base {[k[2] for k in sel(b)]} / grid {list(C.CELLS[a.cell]['snrs'])}")
    bad += [f"load_raw warning: {w.strip()}" for w in wb + wp]
    nfail = {}
    for k in keys if not bad else []:
        for q in ("blk_err", "ber", "tauL_gmean", "alphaD"):
            if not same(b[k]["R5-genie"][q], p[k]["R5-genie"][q]):
                bad.append(f"{k[2]:+.0f} dB R5-genie|{q} differs")
        for new, ref in SAME1:
            ok = ~(failed(p[k], new) | failed(b[k], ref))
            nfail[new] = nfail.get(new, 0) + int(failed(p[k], new).sum())
            for q in ("blk_err", "ber", "nmse"):
                if not same(np.asarray(p[k][new][q])[ok, 0], np.asarray(b[k][ref][q])[ok, 0]):
                    bad.append(f"{k[2]:+.0f} dB {new} @1 {q} != {ref} @1")
            nm = np.asarray(p[k][new]["nmse"])[~failed(p[k], new)]
            if not same(nm, np.repeat(nm[:, :1], nm.shape[1], axis=1)):
                bad.append(f"{k[2]:+.0f} dB {new} nmse varies over iterations (channel estimate not fixed)")
    n = len(p[keys[0]]["R5-genie"]["blk_err"]) if keys else 0
    print(f"# pair_cross {a.pilot} x {a.base}, cell {a.cell}, prior {a.prior}, n={n} per SNR, git {head}; raised trials "
          f"{nfail}; integrity (point set, genie identical, pilot-only @1 == loop @1, fixed channel estimate): "
          + ("OK" if not bad else "FAILED: " + "; ".join(bad[:10])))
    if bad:
        sys.exit(1)                                     # an invalid dataset gets no label (registration §1)
    data = {k: {**b[k], **{arm: p[k][arm] for arm in ("V1-pilot", "bstar-pilot")}} for k in keys}
    snrs = [k[2] for k in keys]
    for x, y, name in PAIRS:
        cand = decision_points(data, a.cell, a.prior, snrs, x)            # anchor = the baseline (first) member
        res = [paired(data[(a.cell, a.prior, s)], x, y) for s in cand]
        A, Bn = sum(r[0] for r in res), sum(r[1] for r in res)
        powered = len(cand) == 3 and sum(1 for r in res if r[0] + r[1] >= MIN_DISC) >= 2
        wy = sum(1 for r in res if r[0] > r[1] and r[2] < 0.05); wx = sum(1 for r in res if r[1] > r[0] and r[2] < 0.05)
        lab = ("(iv) UNDECIDED" if not powered else "(i) second arm fewer" if wy >= 2 else "(ii) first arm fewer" if wx >= 2
               else "(iii) no direction")
        print(f"{name}: {x} -> {y}  [anchor {x}]  decision SNRs {[f'{s:+.0f}' for s in cand]}")
        print("    sign test @16: " + "  ".join(f"{s:+.0f} dB {r[0]}:{r[1]} p={r[2]:.2g}" for s, r in zip(cand, res))
              + f"   pooled {A}:{Bn} p={sign_p(A, Bn):.2g}")
        print(f"    POWERED={powered}  second arm fewer at {wy}/{len(cand)}, first arm fewer at {wx}/{len(cand)}  -> {lab}")
        print(f"    SNR@0.1 gap ({x} minus {y}): {gain(data, a.cell, a.prior, snrs, x, y)['text']}")
    k3 = [k for k in keys if k[2] == -3.0]
    if k3:
        row = "  ".join(f"{arm} {np.nan_to_num(np.asarray(data[k3[0]][arm]['blk_err'])[:, -1], nan=1).mean():.3f}"
                        for arm in SHOW)
        print(f"-3 dB BLER@16: {row}")
    print("report-only, median NMSE@16 of the channel estimate per SNR " + " ".join(f"{s:+.0f}" for s in snrs) + " dB:")
    for arm in SHOW[:-1]:
        print(f"    {arm:<20}" + " ".join(f"{np.nanmedian(np.asarray(data[k][arm]['nmse'])[:, -1]):.2e}" for k in keys))


if __name__ == "__main__":
    main()
