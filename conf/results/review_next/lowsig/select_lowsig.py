"""select_lowsig.py -- SELECTION_RULE.md (committed 1f4c5c4c before the n = 320 results): the primary low-sigma variant.
Reads screen_<cell>_<mod>_<skip0>_320_snr<snr>.npz (V1, b*, V1-clamp = A, V1-gmmfb = B) and screenC_<...>.npz (C) for the 12 points
(UMi28, D2) x (qpsk, 16qam) x (+15, +18, +21 dB); failures = iteration-16 blk_err != 0 (raise = failure).  Checks every file holds
n = 320 trials.  A missing C file -> C is not a candidate (rule 5) and the output says why.
    cd ~/t2/conf && python results/review_next/lowsig/select_lowsig.py [d]
With 'd' (SELECTION_RULE.md addendum, Fable M1): C = the checkpoints re-trained on the development-trial grids (screenCd_*), and the M4
check: at the expected L2 decision-point SNRs not among the 12 points (screen_* / screenCd_* there), per run (cell x modulation) the
PRIMARY's failure sum <= V1's + 2 sqrt(V1's) -- a violation is printed and goes to the user before the freeze (not a judgement)."""
import math, os, sys
import numpy as np

CSET = sys.argv[1] if len(sys.argv) > 1 else ""

D = os.path.dirname(os.path.abspath(__file__))
PTS = [(c, m, s) for c in ("U28", "D2") for m in ("qpsk", "16qam") for s in (15, 18, 21)]
SK = {"16qam": 5120, "qpsk": 6000}
F = lambda be: int((np.asarray(be)[:, 15] != 0).sum())
rows, M, M15, missC = [], {k: 0 for k in ("V1", "b*", "A", "B", "C")}, {k: 0 for k in ("V1", "A", "B", "C")}, []
for c, m, s in PTS:
    z = np.load(os.path.join(D, f"screen_{c}_{m}_{SK[m]}_320_snr{s}.npz"))
    f = {"V1": F(z[f"{s}|V1|blk_err"]), "b*": F(z[f"{s}|b*|blk_err"]), "A": F(z[f"{s}|V1-clamp|blk_err"]), "B": F(z[f"{s}|V1-gmmfb|blk_err"])}
    assert all(len(z[f"{s}|{a}|blk_err"]) == 320 for a in ("V1", "b*", "V1-clamp", "V1-gmmfb"))
    pc = os.path.join(D, f"screenC{CSET}_{c}_{m}_{SK[m]}_320_snr{s}.npz")
    if os.path.exists(pc):
        zc = np.load(pc); assert len(zc["blk_err"]) == 320; f["C"] = F(zc["blk_err"])
    else:
        missC.append(f"{c} {m} {s:+d}")
    for k, v in f.items():
        M[k] += v
        if s == 15 and k in M15:
            M15[k] += v
    rows.append(f"{c:3s} {m:5s} {s:+3d} dB  " + "  ".join(f"{k} {v:3d}" for k, v in f.items()))
cand = ["A", "B"] + ([] if missC else ["C"])
lim = M15["V1"] + 2 * math.sqrt(M15["V1"])
ok = [k for k in cand if M15[k] <= lim]
best = min(ok, key=lambda k: (M[k], "ABC".index(k))) if ok else None
print("# select_lowsig: failures @16 / 320 per point (development trials; SELECTION_RULE.md)")
print("\n".join(rows))
print(f"M (12 points / 3840 blocks): " + "  ".join(f"{k} {v}" for k, v in M.items() if k in cand or k in ("V1", "b*")))
print(f"no-harm at +15 dB: V1 {M15['V1']}, limit {lim:.2f}; " + "  ".join(f"{k} {M15[k]} {'pass' if k in ok else 'FAIL'}" for k in cand))
if missC:
    print(f"C not a candidate: missing evaluation at {missC} (rule 5)")
print(f"PRIMARY = {best}")
if CSET:
    M4 = {("U28", "qpsk"): (3, 6, 9), ("D2", "qpsk"): (-3, 0, 3), ("U28", "16qam"): (12,), ("D2", "16qam"): (9, 12)}
    print("M4 (decision-point SNRs not among the 12 points; failures @16 / 320 summed per run):")
    for (c, m), ss in M4.items():
        tot = {k: 0 for k in ("V1", "b*", "A", "B", "C")}
        for s in ss:
            z = np.load(os.path.join(D, f"screen_{c}_{m}_{SK[m]}_320_snr{s:g}.npz"))
            for k, a in (("V1", "V1"), ("b*", "b*"), ("A", "V1-clamp"), ("B", "V1-gmmfb")):
                tot[k] += F(z[f"{float(s):g}|{a}|blk_err"])
            zc = np.load(os.path.join(D, f"screenC{CSET}_{c}_{m}_{SK[m]}_320_snr{float(s):g}.npz")); tot["C"] += F(zc["blk_err"])
        lim4 = tot["V1"] + 2 * math.sqrt(tot["V1"])
        print(f"  {c:3s} {m:5s} SNR {ss}: " + "  ".join(f"{k} {v}" for k, v in tot.items())
              + f"   PRIMARY {best} {tot[best] if best else '-'} vs limit {lim4:.2f} -> " + ("ok" if best and tot[best] <= lim4 else "VIOLATION (to the user)"))
