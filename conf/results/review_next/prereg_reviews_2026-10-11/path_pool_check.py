"""review_PATH16e4: recompute the SRP pool facts from the files (CPU, read-only). Output -> path_pool_check.out"""
import hashlib, os, sys, time
import numpy as np
sys.path.insert(0, "/home/HTJ/t2/conf/code")
import common as C, dmimo, srp_build as B

d = os.path.expanduser("~/data/sionna_rt/srp_Nr8")
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]
print("sha H/split:", sha(f"{d}/H.npy"), sha(f"{d}/split.npy"), "POOL_SHA:", dmimo.POOL_SHA[("SRP", 8)])
for f in ("H.npy", "split.npy", "meta.npz"):
    print(f, time.strftime("%m-%d %H:%M:%S KST", time.localtime(os.path.getmtime(f"{d}/{f}"))))
H = np.load(f"{d}/H.npy"); sp = np.load(f"{d}/split.npy"); m = np.load(f"{d}/meta.npz")
n = len(H); print("n", n, H.shape, H.dtype, "counts fit/val/test", [(sp == k).sum() for k in range(3)])
pos, yaw, t, row = m["pos"], m["yaw"], m["t"], m["row"]
# route geometry recomputed independently
NX, NY, S = 600, 576, 0.015
r = np.repeat(np.arange(NY), NX); c = np.tile(np.arange(NX), NY); c = np.where(r % 2 == 0, c, NX - 1 - c)
xy = S * np.stack([c - (NX - 1) / 2, r - (NY - 1) / 2], 1)       # centre (0,0): bbox [-5,5]^2
print("pos == recomputed lattice:", np.abs(pos - xy).max(), "| t == arange:", np.array_equal(t, np.arange(n)), "| row == r:", np.array_equal(row, r))
print("x range", pos[:, 0].min(), pos[:, 0].max(), "y range", pos[:, 1].min(), pos[:, 1].max())
print("yaw values:", np.unique(yaw), "| yaw == (row odd)*pi:", np.array_equal(yaw, np.where(r % 2 == 0, 0.0, np.pi)))
print("unique positions:", len(np.unique(np.round(pos / S * 2).astype(np.int64), axis=0)))
st = np.linalg.norm(np.diff(pos, axis=0), axis=1)
print("consecutive step: min %.4f max %.4f; steps != 0.015 (row turns): %d (expected %d)" % (st.min(), st.max(), (np.abs(st - S) > 1e-9).sum(), NY - 1))
turn = np.where(np.abs(st - S) > 1e-9)[0]
print("row turns at t =", turn[:3], "... all at (k*600-1):", np.array_equal(turn, np.arange(1, NY) * NX - 1), "turn step =", np.unique(st[turn].round(6)))
print("x at a turn (should be the room edge +-4.4925):", pos[turn[:4], 0], pos[turn[:4] + 1, 0])
# split by time
it = np.where(sp == 2)[0]; iv = np.where(sp == 1)[0]; ifit = np.where(sp == 0)[0]
print("test: t min", it.min(), "max", it.max(), "contiguous end:", np.array_equal(it, np.arange(n - 52200, n)), "rows", row[it].min(), "-", row[it].max(), "y min %.4f" % pos[it, 1].min())
print("test rows == 87:", len(np.unique(row[it])), "| smallest #rows with >=15%:", int(np.ceil(0.15 * NY)), "| 86 rows =", 86 * 600, "< 0.15 n =", 0.15 * n)
print("val: rows", row[iv].min(), "-", row[iv].max(), "| val in time order? spread over", len(np.unique(row[iv])), "rows; fit rows", len(np.unique(row[ifit])))
# validation draw reproducible from the documented rng
rng = np.random.default_rng([C.SEED, C.TBID["D2"], 12, C.PID["SRP"], 1]); tr = np.where(row < NY - 87)[0]
v = np.zeros(len(tr), bool); v[rng.permutation(len(tr))[:20000]] = True
print("val draw reproduced:", np.array_equal(tr[v], iv), "| fit reproduced:", np.array_equal(tr[~v], ifit))
print("PID SRP", C.PID["SRP"], "| DM_PRIORS", C.DM_PRIORS, "| dmimo.PRIORS", dmimo.PRIORS)
# normalisation: per-pair path power sum = 1 -> ||H||_F^2 ~ Nr*Nt-ish (not exactly); ensemble P_RAW
p = (np.abs(H) ** 2).sum((1, 2)) / 32
print("||H||^2/(NrNt) per pair: mean %.5f median %.4f min %.4f max %.4f" % (p.mean(), np.median(p), p.min(), p.max()))
# stream 7 training set: distinct? subset of fit pool?
g = dmimo.DMGen("D2", "SRP", 8, 4) if hasattr(dmimo, "DMGen") else None
print("DMGen idx sizes:", {k: len(v) for k, v in g.idx.items()} if g is not None else None)
# banner strings
b = C.banner("D2", "SRP")
for s in ("SITE-SPECIFIC RAY-TRACED TESTBED (prior SRP)", "ONE UE MOVING along a lawn-mower route", "CLAIM TESTBED -- sparse specular"):
    print(repr(s), "in banner:", s in b)
# nearest-row leakage picture: rows adjacent to the boundary
print("train rows present near boundary (486..488):", [int((row[ifit] == k).sum()) for k in (486, 487, 488)], "| test rows 489..491:", [int((row[it] == k).sum()) for k in (489, 490, 491)])
# sample row-to-row channel correlation (how different are neighbouring snapshots?)
Hf = H.reshape(n, -1); nrm = np.linalg.norm(Hf, axis=1)
corr1 = np.abs((Hf[:-1] * Hf[1:].conj()).sum(1)) / (nrm[:-1] * nrm[1:])
same_row = r[:-1] == r[1:]
print("|corr| consecutive snapshots (same row): median %.3f, p10 %.3f, p90 %.3f" % tuple(np.percentile(corr1[same_row], [50, 10, 90])))
# same column, adjacent row (1.5 cm across, yaw flipped)
j = np.arange(NX); i0 = 488 * NX + j; i1 = 489 * NX + (NX - 1 - j)   # row 488 (+x) col j  vs row 489 (-x) same x
c2 = np.abs((Hf[i0] * Hf[i1].conj()).sum(1)) / (nrm[i0] * nrm[i1])
print("|corr| row 488 vs row 489 at the same x (yaw differs by pi): median %.3f" % np.median(c2), "| pos diff", np.abs(pos[i0, 0] - pos[i1, 0]).max())
