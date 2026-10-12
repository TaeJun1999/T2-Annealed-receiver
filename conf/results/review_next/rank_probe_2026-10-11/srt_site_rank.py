"""rank_probe_2026-10-11/srt_site_rank.py <part_*.npz> [min_pairs] -- per BS site of a scan: pairs, LoS share, rank-1 share (largest
singular value's energy share >= 0.95), share of links below 0.80, mean effective rank; the distribution and the lowest sites."""
import sys

import numpy as np

z = np.load(sys.argv[1]); MINP = int(sys.argv[2]) if len(sys.argv) > 2 else 400
H, site, los = z["H"], z["site"], z["los"].astype(bool)
q = np.linalg.svd(H, compute_uv=False) ** 2; q /= q.sum(1, keepdims=True); sh = q[:, 0]
er = np.exp(-(q * np.log(np.maximum(q, 1e-300))).sum(1))
ids = np.unique(site); n = np.array([(site == j).sum() for j in ids]); keep = n >= MINP
st = lambda j: ((sh[site == j] >= 0.95).mean(), (sh[site == j] < 0.80).mean(), er[site == j].mean(), los[site == j].mean())
S = np.array([st(j) for j in ids])
r1 = S[keep, 0]
print(f"{sys.argv[1]}: {len(H)} pairs, {len(ids)} sites, {keep.sum()} with >= {MINP} pairs; all pairs: rank-1 {(sh >= 0.95).mean():.3f}, LoS {los.mean():.3f}, erank {er.mean():.2f}")
print("  per-site rank-1 share: min / 5% / 25% / median / 75% / max = " + " / ".join(f"{x:.2f}" for x in np.percentile(r1, [0, 5, 25, 50, 75, 100]))
      + f";  sites below 0.5: {(r1 < 0.5).sum()}, below 0.3: {(r1 < 0.3).sum()}, below 0.2: {(r1 < 0.2).sum()}, below 0.1: {(r1 < 0.1).sum()}")
print("  lowest 12 sites (site: pairs, rank-1, share<0.80, erank, LoS, BS xy, boresight deg):")
for k in np.argsort(np.where(keep, S[:, 0], 9))[:12]:
    j = ids[k]
    print(f"    {j:5d}: {n[k]:5d}  {S[k, 0]:.3f}  {S[k, 1]:.3f}  {S[k, 2]:.2f}  {S[k, 3]:.2f}  ({z['sxy'][j][0]:8.1f}, {z['sxy'][j][1]:8.1f})  {np.degrees(z['sbore'][j]):+7.1f}")
