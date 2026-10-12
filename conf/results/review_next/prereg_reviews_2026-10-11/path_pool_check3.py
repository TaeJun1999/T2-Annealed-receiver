"""review_PATH16e4 part 3: reproduce testbed_dm.py's TDMh exactly (stream-10 draws, 2000) and split it by test stratum."""
import os, sys, numpy as np
sys.path.insert(0, "/home/HTJ/t2/conf/code")
import common as C, dmimo
g = dmimo.DMGen("SRP", 8, 4); meta = np.load(os.path.join(dmimo.pool_dir("SRP", 8), "meta.npz")); row = meta["row"]
Xtr = g.sample_vecs(C.train_rng("D2", "SRP", 8, 7), dmimo.N_CAL)
r10 = C.train_rng("D2", "SRP", 8, 10)
# replay _draw to keep the indices
ix = g.idx["test"]; i10 = ix[r10.integers(0, len(ix), 20000)]
ht = (np.asarray(g.H[i10], dtype=complex) / g.s).transpose(0, 2, 1).reshape(20000, 32)[:2000]; i10 = i10[:2000]
a2 = (np.abs(ht) ** 2).sum(1); best = np.full(2000, np.inf)
for i in range(0, len(Xtr), 20000):
    B = Xtr[i:i + 20000]
    best = np.minimum(best, (a2[:, None] + (np.abs(B) ** 2).sum(1)[None] - 2 * (ht @ B.conj().T).real).min(1))
dn = np.maximum(best, 0) / a2
print(f"TDMh reproduced: median {np.median(dn):.4f}, share < 0.1 = {np.mean(dn < 0.1):.3f}   (testbed_SRP.txt: 0.1833 / 0.073)")
r = row[i10] - 489
for k, lab in enumerate(("first 29 rows", "middle 29", "last 29")):
    m = r // 29 == k; print(f"  stratum {lab:<14} n={m.sum():4d}: median {np.median(dn[m]):.4f}, share < 0.1 = {np.mean(dn[m] < 0.1):.3f}")
lo = a2 < np.percentile(a2, 20); print(f"  lowest-power 20% of the test draws: share < 0.1 = {np.mean(dn[lo] < 0.1):.3f}; others {np.mean(dn[~lo] < 0.1):.3f}")
