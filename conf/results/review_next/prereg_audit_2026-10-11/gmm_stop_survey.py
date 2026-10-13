"""prereg_audit_2026-10-11/gmm_stop_survey.py -- POST-HOC, READ-ONLY survey (author, after the record audit of ROOM16e4 §7 found, S1,
that the DMI b* fit ended on a NEGATIVE step of the training log-likelihood): how did EM end for the highest-validation-likelihood
fit of every fits directory?  gmm_em_gpu.py stops when `it >= 20 and ll[-1] - ll[-2] < tol * |ll[-1]|` (true for a decrease too),
or by validation patience; the returned model is the best-validation state (it_best).  Nothing is re-fitted, no BLER, no label.
Run (cwd ~/t2/conf): CUDA_VISIBLE_DEVICES= python -B results/review_next/prereg_audit_2026-10-11/gmm_stop_survey.py > .../gmm_stop_survey.out
"""
import glob, os
import numpy as np

print(f"{'fits dir (real dirs only)':<28}{'highest-ll_val file':<44}{'ll_val':>10} {'n_ll':>5} {'it_best':>7} {'last step':>11} {'neg steps':>9}  end")
for d in sorted(glob.glob("results/gmm_fits_D2_*")):
    if os.path.islink(d):
        continue
    best = None
    for f in sorted(glob.glob(d + "/fit_*.npz")):
        z = np.load(f, allow_pickle=True)
        if "ll_val" not in z.files or "ll" not in z.files:
            continue
        ll, lv = np.asarray(z["ll"], float).ravel(), float(z["ll_val"])
        if len(ll) > 1 and (best is None or lv > best[0]):
            best = (lv, os.path.basename(f), len(ll), int(z["it_best"]) if "it_best" in z.files else -1, float(ll[-1] - ll[-2]), int((np.diff(ll) < 0).sum()))
    if best:
        lv, f, n, ib, st, ng = best
        print(f"{os.path.basename(d):<28}{f:<44}{lv:>10.3f} {n:>5d} {ib:>7d} {st:>11.3e} {ng:>9d}  {'NEGATIVE last step' if st < 0 else 'non-negative last step'}")
