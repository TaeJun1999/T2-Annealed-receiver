"""golden helper: numpy default (method='linear') percentile values for the hand-computed summary cases."""
import warnings
import numpy as np
P = lambda x, p: float(np.percentile(np.asarray(x, float), p)) if len(x) else float("nan")
def summ(name, x):
    x = np.asarray(x, float)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        med = float(np.median(x)) if len(x) else float("nan")
    print(f"{name}: n={len(x)} median={med!r} p25={P(x,25)!r} p75={P(x,75)!r} IQR width={P(x,75)-P(x,25)!r} p90={P(x,90)!r}")
# S1 pooled per-call (ms), 8 values
summ("S1 per-call", [3, 1, 4, 1, 5, 9, 2, 6])
# S2 score arm per-call = denoise_i + _matrix_site_i (4 calls of one block)
d = np.array([2.0, 3.0, 2.5, 4.0]); m = np.array([0.5, 0.4, 0.6, 0.5])
pc = d + m; print("S2 per-call d+m =", pc.tolist(), " block H sum =", float(pc.sum()))
summ("S2 per-call", pc)
# S3 pooling across blocks: block1 [1,2,9], block2 [3,4,5]
summ("S3 pooled", [1, 2, 9, 3, 4, 5]); print("S3 median of block medians =", float(np.median([np.median([1, 2, 9]), np.median([3, 4, 5])])))
summ("S3 H per block", [12, 12]); summ("S3 rx.run per block", [40, 30])
r = np.array([12, 12]) / np.array([40, 30]); print("S3 share: median of per-block ratios", float(np.median(r)), " sum ratio", 24 / 70, " ratio of medians", 12 / 35)
# S4 H share definitions disagree
H = np.array([0.20, 0.60, 0.30]); R = np.array([1.00, 1.20, 0.90])
print("S4 per-block ratios", (H / R).tolist())
print("S4 median of ratios", float(np.median(H / R)), " ratio of sums", float(H.sum() / R.sum()), " ratio of medians", float(np.median(H) / np.median(R)))
summ("S4 rx.run", R)
# S5 single value, S6 empty
summ("S5 single", [7.0]); summ("S6 empty", [])
# S7 one failed block excluded: blocks 1 and 3 complete (16 calls each), block 2 raised after 5 calls
print("S7 calls/blk over completed blocks:", float(np.median([16, 16])))
