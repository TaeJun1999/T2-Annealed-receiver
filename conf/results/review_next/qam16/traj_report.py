"""traj_report.py -- E5QAM16 §6.4 (post hoc, report only; NOT a registered analysis, no label): per SNR, the per-iteration
failures (iteration 1 / 2 / 4 / 8 / 16), the raised-block count (the `<arm>|failed` key) and the median channel-estimate NMSE
(iteration 1 / 16) of the five E5 arms in one 16-QAM test raw.  Reads the raw only.
    cd ~/t2/conf && python results/review_next/qam16/traj_report.py U28QAM16|D2QAM16"""
import glob, sys, collections as C
import numpy as np

T = sys.argv[1]
by = C.defaultdict(list)
for f in sorted(glob.glob(f"raw_{T}/*.npz")):
    z = np.load(f); by[float(z["run|snr"])].append(z)
print(f"# traj_report {T}: {sum(len(v) for v in by.values())} chunks, n per SNR {[sum(len(z['R5-genie|blk_err']) for z in by[s]) for s in sorted(by)]}")
for s in sorted(by):
    zs = by[s]
    for a in ("M-ours-dscore-C-V1", "M-ours-bstar", "R2-ours-G", "R5-genie", "V1-pilot"):
        be = np.concatenate([z[f"{a}|blk_err"] for z in zs]); nm = np.concatenate([z[f"{a}|nmse"] for z in zs])
        fa = sum(int(z[f"{a}|failed"].sum()) for z in zs if f"{a}|failed" in z.files)
        f = lambda i: int((~(be[:, i] == 0)).sum())          # failures (non-finite = failure, 01_RULES §4)
        print(f"{s:+5.0f} dB {a:<20} failures @1 {f(0):4d} @2 {f(1):4d} @4 {f(3):4d} @8 {f(7):4d} @16 {f(15):4d} / {len(be)}  raised {fa}  "
              f"median NMSE @1 {np.nanmedian(nm[:, 0]):.2e} @16 {np.nanmedian(nm[:, 15]):.2e}")
