"""srt_pool_check.py -- adversarial review of NEXT_EXPERIMENTS_SRT16e4 v1: recompute §0 pool statistics from the pool files only
(CPU, read-only; no BLER, no ray tracer).  Output: srt_pool_check.out next to this file."""
import hashlib
import os
import sys
import time

import numpy as np

sys.path.insert(0, "/home/HTJ/t2/conf/code")
import common as C          # noqa: E402
import dmimo                # noqa: E402

t0 = time.time()
d = os.path.expanduser("~/data/sionna_rt/srt_Nr8")
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]
print("sha H.npy", sha(f"{d}/H.npy"), "split.npy", sha(f"{d}/split.npy"), "pinned", dmimo.POOL_SHA[("SRT", 8)])
for s in ("munich", "etoile", "florence"):
    print(f"part_{s}.npz sha", sha(f"{d}/part_{s}.npz"))
H = np.load(f"{d}/H.npy", mmap_mode="r"); split = np.load(f"{d}/split.npy"); M = np.load(f"{d}/meta.npz")
n = len(H); print("pairs", n, "shape", H.shape, H.dtype)
cnt = np.bincount(split, minlength=3); print("fit / val / test", cnt.tolist(), "test share %.4f" % (cnt[2] / n))
key, scen, site, los, npath, pos = M["key"], M["scen"], M["site"], M["los"], M["npath"], M["pos"]
tiles = np.unique(key); ttest = np.unique(key[split == 2]); tother = np.unique(key[split != 2])
print("tiles", len(tiles), "test tiles", len(ttest), "overlap tiles", len(set(ttest) & set(tother)))
# tile key collision check: (scene, floor(x/20), floor(y/20)) -> key must be injective
tile = np.floor(pos / 20.0).astype(np.int64)
trip = {(int(a), int(b), int(c)) for a, b, c in zip(scen, tile[:, 0], tile[:, 1])}
print("distinct (scene, tx, ty)", len(trip), "== distinct keys", len(tiles))
for i, s in enumerate(("munich", "etoile", "florence")):
    m = scen == i
    print(f"{s}: pairs {m.sum()}, sites with pairs {len(np.unique(site[m]))}, max site id {site[m].max()}, LoS {los[m].mean():.4f}, "
          f"mean paths {npath[m].mean():.3f}, per-site pairs max {np.bincount(site[m]).max()}, test share {np.mean(split[m] == 2):.4f}")
print("LoS all %.4f  train-side (fit+val) %.4f  test-side %.4f" % (los.mean(), los[split != 2].mean(), los[split == 2].mean()))
print("mean paths all %.3f" % npath.mean())
# per-pair power of the raw pool (should be ~1 up to multipath interference) and P_RAW over train stream 7
Hf = np.asarray(H[:]).astype(np.complex64)
pw = (np.abs(Hf) ** 2).sum((1, 2)) / 32
print("raw ||H||^2/(NrNt): mean %.6f  median %.6f  CV %.3f  min %.4f  max %.4f" % (pw.mean(), np.median(pw), pw.std() / pw.mean(), pw.min(), pw.max()))
g = dmimo.DMGen("SRT", 8, 4, raw=True)
Xtr = g._draw(C.train_rng("D2", "SRT", 8, 7), 160000)
p = float(np.mean(np.sum(np.abs(Xtr) ** 2, (1, 2)))) / 32
print("P_RAW recomputed %r  frozen %r  diff %.2e" % (p, dmimo.P_RAW[("SRT", 8, 4)], p - dmimo.P_RAW[("SRT", 8, 4)]))
Xn = Xtr / np.sqrt(p)
sh = hashlib.sha256(np.ascontiguousarray(Xn.transpose(0, 2, 1).reshape(len(Xn), 32)).tobytes()).hexdigest()[:16]
print("TRAIN_SHA recomputed", sh, "frozen", dmimo.TRAIN_SHA[("SRT", 8, 4)])
# which pairs does stream 7 pick?  all from the fit pool, distinct?
rng = C.train_rng("D2", "SRT", 8, 7); ix = g.idx["fit"]; i7 = ix[rng.permutation(len(ix))[:160000]]
print("stream 7: distinct", len(np.unique(i7)) == 160000, "all fit", np.all(split[i7] == 0))
# TDMa: validation stream 8, n = 20000, normalised
gn = dmimo.DMGen("SRT", 8, 4)
Xv = gn._draw(C.train_rng("D2", "SRT", 8, 8), 20000)
pv = (np.abs(Xv) ** 2).sum((1, 2)) / 32
print("TDMa val stream 8 n=20000: mean %.5f  s.e. %.5f  block power CV %.3f" % (pv.mean(), pv.std() / np.sqrt(len(pv)), pv.std() / pv.mean()))
Xt = gn._draw(C.train_rng("D2", "SRT", 8, 10), 20000)
print("test stream 10 n=20000: mean ||H||^2/(NrNt) %.4f" % ((np.abs(Xt) ** 2).sum((1, 2)) / 32).mean())
# rank share s1^2 / sum s^2 over the whole fit pool and test pool
def share(A):
    s = np.linalg.svd(A, compute_uv=False) ** 2
    return s[:, 0] / s.sum(1)
for name, m in (("fit pool", split == 0), ("test pool", split == 2), ("val pool", split == 1)):
    sh_ = share(Hf[m].astype(np.complex128))
    print(f"rank share {name}: >=0.95 {np.mean(sh_ >= 0.95):.3f}  0.80-0.95 {np.mean((sh_ >= 0.8) & (sh_ < 0.95)):.3f}  "
          f"<0.80 {np.mean(sh_ < 0.8):.3f}  (0.60-0.80 {np.mean((sh_ >= 0.6) & (sh_ < 0.8)):.3f}, <0.60 {np.mean(sh_ < 0.6):.3f})  median {np.median(sh_):.4f}")
# TDMh leakage: 2000 test samples (stream 10) vs the N' = 160000 training set (stream 7), normalised squared distance
h = gn._draw(C.train_rng("D2", "SRT", 8, 10), 2000).transpose(0, 2, 1).reshape(2000, 32)
X = Xn.transpose(0, 2, 1).reshape(len(Xn), 32)
a2 = (np.abs(h) ** 2).sum(1); best = np.full(len(h), np.inf)
for i in range(0, len(X), 20000):
    B = X[i:i + 20000]
    best = np.minimum(best, (a2[:, None] + (np.abs(B) ** 2).sum(1)[None] - 2 * (h @ B.conj().T).real).min(1))
dd = np.maximum(best, 0) / a2
print("TDMh (stream 10 first 2000 vs stream 7): d median %.4f  share < 0.1 %.3f" % (np.median(dd), np.mean(dd < 0.1)))
# expected duplicate pairs within one SNR's 2560 test trials
print("expected duplicates among 2560 draws from %d: %.1f" % (cnt[2], 2560 ** 2 / (2 * cnt[2])))
print("done %.0f s" % (time.time() - t0))
