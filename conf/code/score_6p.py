"""(10_SPEC_stageC §6p) Score the low-SNR extension against its pre-registered predictions.

Reads raw_B1e4lo (C2 and C5 at -9/-7/-6/-5 dB, equal budget N=1e4, n=2560) plus the existing -3..+15 dB
points (raw_B1e4 for C2, raw_B1e4x for C5) and prints, per cell and SNR: BLER@16 of the arms, the
GMM/V1 BLER ratio, the F3 guard rate of V1, and the pre-registered predictions scored one by one.
Report-only; the pre-registered analysis tables (tables_D2_B1e4lo.txt) remain the file of record for
the sign tests.  A block on which an arm raised is a block error (analysis.py:172-175).
"""
import glob
import os
import re
import sys
import collections

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import common as C  # noqa: E402

RAW = {("C2", "lo"): "raw_B1e4lo", ("C5", "lo"): "raw_B1e4lo", ("C2", "hi"): "raw_B1e4", ("C5", "hi"): "raw_B1e4x"}
ARMS = ["R1-turbo", "M-ours-bstar", "M-ours-dscore-C-V1", "M-ours-dscore-C-V4", "M-ours-dscore-C-V0", "R5-genie"]
DIV = 10.0
GRID_TOP = 2 * 0.8451555 ** 2


def nu_q(Tp, snr_db, Nt=4, cb=1.0):
    s2 = 10 ** (-snr_db / 10.0)
    aL = (1 - Tp / Nt) + (Tp / Nt) / (1 + Nt * cb / s2)
    return cb * aL / (1 - aL)


def load(cell):
    acc = collections.defaultdict(lambda: collections.defaultdict(list))
    grd = collections.defaultdict(lambda: collections.defaultdict(list))
    cnt = collections.defaultdict(int)
    for part in ("lo", "hi"):
        for f in glob.glob(os.path.join(C.CONF, RAW[(cell, part)], f"D2_{cell}_*.npz")):
            snr = int(re.search(r"snr(-?\d+)", f).group(1))
            d = np.load(f, allow_pickle=True)
            for k in d.files:
                if k.endswith("|blk_err"):
                    v = d[k][:, 15]
                    acc[k.split("|")[0]][snr].append(np.where(np.isfinite(v), v, 1.0))
                if k.endswith("|nmse"):
                    v = d[k][:, 15]
                    grd[k.split("|")[0]][snr].append(~np.isfinite(v) | (v > DIV))
            cnt[snr] += len(d[ARMS[0] + "|blk_err"]) if ARMS[0] + "|blk_err" in d.files else 0
    return acc, grd, cnt


def main():
    out = []
    w = out.append
    w("# (10_SPEC_stageC §6p) low-SNR extension, equal budget N=1e4, scored against the pre-registration")
    w("# raw: raw_B1e4lo (-9/-7/-6/-5 dB) + raw_B1e4 (C2) / raw_B1e4x (C5) for -3..+15 dB.  n per point printed;")
    w("# a point with n < 2560 is INCOMPLETE and is marked.  Raised blocks count as block errors.")
    w("")
    ratio_ref = {}
    guardV1 = {}
    for cell, Tp in (("C2", 4), ("C5", 3)):
        acc, grd, cnt = load(cell)
        snrs = sorted(cnt)
        w(f"===== {cell} (Tp={Tp}) =====")
        w(f"{'SNR':>5} {'n':>5} {'nu_q':>7} {'grid':>5} | " + " ".join(f"{a[:12]:>12}" for a in ARMS) + " | GMM/V1  V1 guard")
        for s in snrs:
            b = {a: float(np.concatenate(acc[a][s]).mean()) if s in acc[a] else float("nan") for a in ARMS}
            g = float(np.concatenate(grd["M-ours-dscore-C-V1"][s]).mean()) if s in grd["M-ours-dscore-C-V1"] else float("nan")
            r = b["M-ours-bstar"] / b["M-ours-dscore-C-V1"] if b["M-ours-dscore-C-V1"] > 0 else float("inf")
            nq = nu_q(Tp, s)
            flag = "" if cnt[s] >= 2560 else "  <-- INCOMPLETE"
            w(f"{s:>+5d} {cnt[s]:>5d} {nq:>7.3f} {'OUT' if nq > GRID_TOP else 'in':>5} | "
              + " ".join(f"{b[a]:>12.4f}" for a in ARMS) + f" | {r:>6.2f}  {g:>7.3f}{flag}")
            ratio_ref[(cell, s)] = r
            guardV1[(cell, s)] = g
        w("")
    w("===== predictions (§6p, committed 279512b before the run) =====")
    R = ratio_ref
    g = guardV1
    def fmt(x): return "n/a" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.2f}"
    p1 = [R.get(("C2", s)) for s in (-6, -7)]
    w(f"1. C2 GMM/V1 ratio at -6 / -7 dB EXCEEDS the -3 dB ratio ({fmt(R.get(('C2', -3)))}): "
      f"-6 dB {fmt(p1[0])}, -7 dB {fmt(p1[1])} -> "
      + ("TRUE" if all(x is not None and x > R.get(("C2", -3), np.inf) for x in p1) else
         ("PARTLY" if any(x is not None and x > R.get(("C2", -3), np.inf) for x in p1) else "FALSE")))
    w(f"2. C2 -9 dB: V1 collapses (guard > 0.5 and V1 worse than GMM): guard {fmt(g.get(('C2', -9)))}, "
      f"ratio {fmt(R.get(('C2', -9)))} -> "
      + ("TRUE" if (g.get(("C2", -9), 0) > 0.5 and R.get(("C2", -9), 9) < 1) else "FALSE"))
    w(f"3. C5 alive at -5 dB, degrades from -6 dB: ratio -5 {fmt(R.get(('C5', -5)))}, -6 {fmt(R.get(('C5', -6)))}, "
      f"-7 {fmt(R.get(('C5', -7)))}, -9 {fmt(R.get(('C5', -9)))}; V1 guard -5 {fmt(g.get(('C5', -5)))}, "
      f"-6 {fmt(g.get(('C5', -6)))}, -7 {fmt(g.get(('C5', -7)))}")
    w("4. collapse SNRs differ between cells and follow the closed form (C2 -7.57 / C5 -5.17 dB, +-1 dB):")
    for cell in ("C2", "C5"):
        ss = sorted(s for (c, s) in g if c == cell)
        first = next((s for s in ss if g[(cell, s)] > 0.5), None)
        w(f"   {cell}: lowest SNR with V1 guard <= 0.5 = "
          f"{next((s for s in ss if g[(cell, s)] <= 0.5), None)}; first collapse (guard > 0.5) at {first}")
    w("")
    w("Score against the wording in 10_SPEC_stageC.md §6p; where a point is INCOMPLETE the score is provisional.")
    txt = "\n".join(out) + "\n"
    with open(os.path.join(C.CONF, "results", "lowsnr_6p_score.txt"), "w") as fh:
        fh.write(txt)
    print(txt)


if __name__ == "__main__":
    main()
