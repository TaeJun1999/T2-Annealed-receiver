"""rank_probe_2026-10-11/srp_corr.py -- route pool SRP: |<h_a, h_b>| / (|h_a| |h_b|) between snapshots a given number of steps apart
on the same row (same heading) and between the same x on rows 2j apart.  Channel statistics only."""
import os
import numpy as np
H = np.load(os.path.expanduser("~/data/sionna_rt/srp_Nr8/H.npy"), mmap_mode="r")
NX, NY = 600, 576
X = np.asarray(H).reshape(NY, NX, -1)
X = np.where((np.arange(NY) % 2 == 0)[:, None, None], X, X[:, ::-1])       # every row in +x order
n = np.linalg.norm(X, axis=2)
c = lambda a, b, na, nb: (np.abs((a.conj() * b).sum(-1)) / (na * nb)).ravel()
print("same row, lag [steps of 1.5 cm]: median |corr| (p10, p90)")
for k in (1, 2, 3, 4, 6, 8, 12, 20, 40):
    q = c(X[:, :-k], X[:, k:], n[:, :-k], n[:, k:]); print(f"  {k:3d} ({1.5 * k:5.1f} cm): {np.median(q):.3f} ({np.percentile(q, 10):.2f}, {np.percentile(q, 90):.2f})")
print("same x, rows apart: median |corr|")
for k in (1, 2, 4, 8, 20):
    q = c(X[:-k], X[k:], n[:-k], n[k:]); print(f"  {k:3d} ({1.5 * k:5.1f} cm{', opposite headings' if k % 2 else ''}): {np.median(q):.3f}")
