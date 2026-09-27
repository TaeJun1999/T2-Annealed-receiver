"""conf/code/pair_ald.py -- table B for the ALD pilot-only arms (NEXT_EXPERIMENTS_ALD16e4 §1) against the loop arms (base raw)
and the one-shot pilot-only arms (PIL raw), all on the SAME trials (streams fixed by testbed, prior, Nr, T, Tp, SNR).

Integrity (any failure -> exit 1 BEFORE any label): the same point set in the three raw sets = the cell's SNR grid, no
load_raw warning, R5-genie identical in the ALD raw and the base raw (4 keys), no raised trial in the ALD arms (a raise is
how ALDSitePrior reports a pilot-site mismatch, i.e. a mis-aligned estimate), the ALD arms' channel estimate fixed over
the iterations (nmse[:, t] == nmse[:, 0]) and equal to the precomputed estimate's error (nmse @1 vs results/ald/ files).
    python code/pair_ald.py --base raw_B16e4k --pil raw_PILB16e4k --ald raw_ALDB16e4k --est PILB16e4k --cell C2 --prior S2
"""
import argparse
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import numpy as np
from analysis import load_raw, decision_points, paired, gain, sign_p, MIN_DISC
from pair_cross import same, failed

PAIRS = (("ALDv-pilot", "M-ours-dscore-C-V1", "A1: ALD pilot-only (error-aware) -> loop V1"),
         ("ALD-pilot", "M-ours-dscore-C-V1", "A2: ALD pilot-only (plug-in, as published) -> loop V1"),
         ("ALDv-pilot", "V1-pilot", "report: ALD sample -> one-shot posterior mean, both pilot-only, same weights"),
         ("ALDv-pilot", "M-ours-bstar", "report: ALD pilot-only -> loop b*"),
         ("bstar-pilot", "ALDv-pilot", "report: pilot-only b* -> ALD pilot-only"),
         ("ALD-pilot", "ALDv-pilot", "report: plug-in -> error-aware"))
SHOW = ("R0-pilot", "bstar-pilot", "ALD-pilot", "ALDv-pilot", "V1-pilot", "M-ours-bstar", "M-ours-dscore-C-V1", "R5-genie")
ALD = ("ALD-pilot", "ALDv-pilot")


def main():
    ap = argparse.ArgumentParser()
    for k in ("--base", "--pil", "--ald", "--est", "--cell", "--prior"):
        ap.add_argument(k, required=True)
    a = ap.parse_args()
    raws = {k: load_raw("D2", root=os.path.join(C.CONF, getattr(a, k))) for k in ("base", "pil", "ald")}
    b, p, m = (raws[k][0] for k in ("base", "pil", "ald"))
    sel = lambda d: sorted((k for k in d if k[:2] == (a.cell, a.prior)), key=lambda k: k[2])
    keys = sel(m)
    grid = [float(s) for s in C.CELLS[a.cell]["snrs"]]
    head = subprocess.run(["git", "-C", C.CONF, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    bad = [f"point set {[k[2] for k in sel(d)]} != grid {grid}" for d in (b, p, m) if [k[2] for k in sel(d)] != grid]
    bad += [f"load_raw warning: {w.strip()}" for k in raws for w in raws[k][2]]
    est = np.load(os.path.join(C.CONF, "results", "ald", f"ald_{a.est}.npz"))
    pil = np.load(os.path.join(C.CONF, "results", "ald", f"pilots_{a.est}_test.npz"))
    for i, k in enumerate(keys if not bad else []):
        for q in ("blk_err", "ber", "tauL_gmean", "alphaD"):
            if not same(b[k]["R5-genie"][q], m[k]["R5-genie"][q]):
                bad.append(f"{k[2]:+.0f} dB R5-genie|{q} differs")
        j = int(np.flatnonzero(np.isclose(est["snrs"], k[2]))[0])
        H, hh = pil["H"][j], est["hhat"][j]
        ref = np.sum(np.abs(hh - H) ** 2, -1) / np.sum(np.abs(H) ** 2, -1)
        for arm in ALD:
            nm = np.asarray(m[k][arm]["nmse"])
            if failed(m[k], arm).any():
                bad.append(f"{k[2]:+.0f} dB {arm}: {int(failed(m[k], arm).sum())} raised trials (estimate mis-aligned)")
            elif not same(nm, np.repeat(nm[:, :1], nm.shape[1], axis=1)) or not np.allclose(nm[:, 0], ref, rtol=1e-9, atol=0):
                bad.append(f"{k[2]:+.0f} dB {arm}: channel estimate not the precomputed ALD estimate")
    n = len(m[keys[0]]["R5-genie"]["blk_err"]) if keys else 0
    print(f"# pair_ald {a.ald} x {a.pil} x {a.base}, cell {a.cell}, prior {a.prior}, n={n} per SNR, git {head}; "
          f"integrity (point sets, genie identical, no raised ALD trial, estimate = precomputed ALD, fixed): "
          + ("OK" if not bad else "FAILED: " + "; ".join(bad[:10])))
    if bad:
        sys.exit(1)                                     # an invalid dataset gets no label (registration §1)
    data = {k: {**b[k], **{arm: p[k][arm] for arm in ("V1-pilot", "bstar-pilot")}, **{arm: m[k][arm] for arm in ALD}}
            for k in keys}
    snrs = [k[2] for k in keys]
    for x, y, name in PAIRS:                            # same rule as analysis.table_B / pair_cross
        cand = decision_points(data, a.cell, a.prior, snrs, x)            # anchor = the first member
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
    print("BLER@16 failures / n per SNR " + " ".join(f"{s:+.0f}" for s in snrs) + " dB:")
    for arm in SHOW:
        print(f"    {arm:<20}" + " ".join(f"{int(np.nan_to_num(np.asarray(data[k][arm]['blk_err'])[:, -1], nan=1).sum()):5d}"
                                         for k in keys))
    print("report-only, median NMSE@16 of the channel estimate per SNR " + " ".join(f"{s:+.0f}" for s in snrs) + " dB:")
    for arm in SHOW[:-1]:
        print(f"    {arm:<20}" + " ".join(f"{np.nanmedian(np.asarray(data[k][arm]['nmse'])[:, -1]):.2e}" for k in keys))


if __name__ == "__main__":
    main()
