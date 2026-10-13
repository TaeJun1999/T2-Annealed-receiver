"""recompute_fighsdmi_gmmstop.py -- RECORD AUDIT (read-only) of WORK_QUEUE.md pending item 7 / DECISIONS.md 2026-10-13 11:39 KST
(ROOM16e4 -- DMI line): "fits 폴더 57 개 가운데 34 개의 선택 적합이 음수 마지막 스텝으로 끝났고 23 개는 아니다".
Own recount (not gmm_stop_survey.py): per REAL directory results/gmm_fits_D2_* the fit file with the highest ll_val, the sign of the
last training-likelihood step, and -- what the survey does not print -- how many DISTINCT fits these are (several folders hold the
same fit under another name; identity = the (ll trajectory, ll_val) content, hashed).
Run (cwd ~/t2/conf): CUDA_VISIBLE_DEVICES= python -B .../recompute_fighsdmi_gmmstop.py > .../recompute_fighsdmi_gmmstop.out
"""
import glob, hashlib, os
import numpy as np

os.chdir("/home/HTJ/t2/conf")
rows = []
for d in sorted(glob.glob("results/gmm_fits_D2_*")):
    if os.path.islink(d) or not os.path.isdir(d):
        continue
    best = None
    for f in sorted(glob.glob(d + "/fit_*.npz")):
        with np.load(f, allow_pickle=True) as z:
            if "ll_val" not in z.files or "ll" not in z.files:
                continue
            ll = np.asarray(z["ll"], float).ravel(); lv = float(z["ll_val"])
            if len(ll) > 1 and (best is None or lv > best[0]):
                best = (lv, os.path.basename(f), len(ll), float(ll[-1] - ll[-2]), int((np.diff(ll) < 0).sum()),
                        hashlib.sha256(ll.tobytes() + np.float64(lv).tobytes()).hexdigest()[:12])
    if best:
        rows.append((os.path.basename(d),) + best)
neg = [r for r in rows if r[4] < 0]; non = [r for r in rows if r[4] >= 0]
print(f"real fits folders with a usable fit: {len(rows)}; highest-ll_val fit ends on a NEGATIVE last step: {len(neg)}; non-negative: {len(non)}")
print(f"DISTINCT fits (by ll trajectory + ll_val): {len({r[6] for r in rows})} = negative {len({r[6] for r in neg})} + non-negative {len({r[6] for r in non})}")
print(f"negative-ending fits with MORE than one negative step anywhere (not 'the first decrease'): {sorted({(r[2], r[5]) for r in neg if r[5] > 1})}")
by = {}
for r in neg:
    by.setdefault(r[6], []).append(r[0])
print("negative-ending distinct fits and the folders holding each:")
for h, ds in sorted(by.items(), key=lambda kv: -len(kv[1])):
    r = next(x for x in neg if x[6] == h)
    print(f"  {r[2]:<46} ll_val {r[1]:>9.3f}  n_ll {r[3]:>4}  last step {r[4]:+.3e}  folders {len(ds)}: {' '.join(x.replace('gmm_fits_D2_', '') for x in ds)}")
old = [l.split() for l in open("results/review_next/prereg_audit_2026-10-11/gmm_stop_survey.out").read().split("\n")[1:] if l.strip()]
same = [(o[0], o[1], o[-3] if o[-1] == "step" else None) for o in old] == [(r[0], r[2], "NEGATIVE" if r[4] < 0 else "non-negative") for r in rows]
print(f"own table == gmm_stop_survey.out (folder, file, sign of last step) for all {len(old)} rows: {same}")
