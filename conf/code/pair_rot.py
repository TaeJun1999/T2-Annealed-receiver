"""conf/code/pair_rot.py -- table B for a receive-array ROTATION (distribution drift) tag (NEXT_EXPERIMENTS_ROT16e4 §1) against the static base raw.

The rotation tag ran V1, b*, R2-ours-G and R5-genie on the SAME trial stream as the base raw (bits, interleaver, noise and every
random channel draw unchanged; every AoA + rot -- generator .rot), with the priors trained at 0 deg.
Its arms are renamed V1-rot / bstar-rot / R2-rot / genie-rot and merged with the static arms; analysis.decision_points /
paired / gain are reused.  Trial identity is established by the 0-deg control (run_rot16e4.sh: every arm bit-identical to
the base raw through the same code path); here: the same point set = the cell's grid, no load_raw warning, meta|rotation of
every chunk = the expected angle, one clean code version, fits/ckpt fingerprint, trial counts, rotation applied.  Any failure -> exit 1 BEFORE any label.
    python code/pair_rot.py --base raw_B16e4k --rot raw_ROTaB16e4k --deg 15 --cell C2 --prior S2
"""
import argparse
import glob
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import numpy as np
from analysis import load_raw, decision_points, paired, gain, sign_p, MIN_DISC

REN = {"M-ours-dscore-C-V1": "V1-rot", "M-ours-bstar": "bstar-rot", "R2-ours-G": "R2-rot", "R5-genie": "genie-rot"}
PAIRS = (("bstar-rot", "V1-rot", "DP: b* -> V1, both under the same receive-array rotation"),
         ("V1-rot", "M-ours-dscore-C-V1", "report: V1 rotated -> V1 static"),
         ("bstar-rot", "M-ours-bstar", "report: b* rotated -> b* static"),
         ("M-ours-bstar", "V1-rot", "report: static b* -> V1 rotated"),
         ("R2-rot", "V1-rot", "report: Gaussian R2 -> V1, both rotated"),
         ("genie-rot", "R5-genie", "report: genie (knows the rotated H) rotated -> static genie"))
SHOW = ("R2-rot", "bstar-rot", "V1-rot", "genie-rot", "R2-ours-G", "M-ours-bstar", "M-ours-dscore-C-V1", "R5-genie")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True); ap.add_argument("--rot", required=True)
    ap.add_argument("--deg", type=float, required=True)
    ap.add_argument("--cell", required=True); ap.add_argument("--prior", required=True)
    a = ap.parse_args()
    b, bm, wb = load_raw("D2", root=os.path.join(C.CONF, a.base))
    m, mm, wm = load_raw("D2", root=os.path.join(C.CONF, a.rot))
    sel = lambda d: sorted((k for k in d if k[:2] == (a.cell, a.prior)), key=lambda k: k[2])
    keys = sel(m)
    grid = [float(s) for s in C.CELLS[a.cell]["snrs"]]
    head = subprocess.run(["git", "-C", C.CONF, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    bad = [f"point set {[k[2] for k in sel(d)]} != grid {grid}" for d in (b, m) if [k[2] for k in sel(d)] != grid]
    bad += [f"load_raw warning: {w.strip()}" for w in wb + wm]
    gits = set()
    for f in glob.glob(os.path.join(C.CONF, a.rot, f"D2_{a.cell}_*.npz")):
        with np.load(f) as z:
            md = str(z["meta|rotation"]) if "meta|rotation" in z.files else ""
            gits.add(str(z["run|git"]) if "run|git" in z.files else "(none)")
        if not md.startswith(f"deg={a.deg!r}:"):
            bad.append(f"{os.path.basename(f)}: meta|rotation {md[:40]!r} != deg={a.deg!r}")
            break
    if len(gits) != 1 or any(g.endswith("+dirty") or g == "(none)" for g in gits):
        bad.append(f"code version across chunks: {sorted(gits)} (one clean commit expected)")
    mt, bt = mm.get((a.cell, a.prior), {}), bm.get((a.cell, a.prior), {})
    fk = ["em_sec", "stagec_ckpt_id"] + sorted(k for k in bt if k.startswith("ll_val|"))
    if bt.get("stagec_ckpt_id") is None:
        fk.remove("stagec_ckpt_id")                     # raw_B16e4k predates the id key (P0-1)
    if any(str(mt.get(k)) != str(bt.get(k)) for k in fk):
        bad.append("fits/ckpt fingerprint differs from the base: " + "; ".join(k for k in fk if str(mt.get(k)) != str(bt.get(k))))
    for k in keys if not bad else []:
        if not all(len(d[k][arm]["blk_err"]) == 2560 for d, arms in ((b, REN), (m, REN)) for arm in arms):
            bad.append(f"{k[2]:+.0f} dB: trial count != 2560")
        elif a.deg != 0 and np.array_equal(np.nan_to_num(b[k]["R5-genie"]["tauL_gmean"]), np.nan_to_num(m[k]["R5-genie"]["tauL_gmean"])):
            bad.append(f"{k[2]:+.0f} dB: genie identical to the static genie (rotation not applied)")
    n = len(m[keys[0]]["R5-genie"]["blk_err"]) if keys else 0
    raised = {REN[arm]: int(sum(np.asarray(m[k][arm].get("failed", np.zeros(1))).sum() for k in keys)) for arm in REN} if not bad else {}
    print(f"# pair_rot {a.rot} x {a.base}, deg={a.deg}, cell {a.cell}, prior {a.prior}, n={n} per SNR, git {head}; raised {raised}; "
          f"integrity (point sets, meta angle, one clean code version, fits/ckpt fingerprint, trial counts, rotation applied): " + ("OK" if not bad else "FAILED: " + "; ".join(bad[:10])))
    if bad:
        sys.exit(1)                                     # an invalid tag gets no label (registration §1)
    data = {k: {**b[k], **{REN[arm]: m[k][arm] for arm in REN}} for k in keys}
    snrs = [k[2] for k in keys]
    for x, y, name in PAIRS:                            # same rule as analysis.table_B
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
    g1, g0 = (gain(data, a.cell, a.prior, snrs, x, y)["est"] for x, y in (("bstar-rot", "V1-rot"), ("M-ours-bstar", "M-ours-dscore-C-V1")))
    print(f"report-only, gap retention = gap(bstar-rot - V1-rot) / gap(b* - V1, static) = "
          + (f"{g1:+.2f} / {g0:+.2f} = {g1 / g0:.2f}" if np.isfinite(g1) and np.isfinite(g0) and g0 else "n/a"))
    print("BLER@16 failures / n per SNR " + " ".join(f"{s:+.0f}" for s in snrs) + " dB:")
    for arm in SHOW:
        print(f"    {arm:<20}" + " ".join(f"{int(np.nan_to_num(np.asarray(data[k][arm]['blk_err'])[:, -1], nan=1).sum()):5d}"
                                         for k in keys))


if __name__ == "__main__":
    main()
