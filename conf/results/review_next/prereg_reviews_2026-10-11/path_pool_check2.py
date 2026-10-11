"""review_PATH16e4 part 2: route turns, generator identity, banner strings, neighbour correlation, boundary leakage by stratum."""
import os, sys, numpy as np
sys.path.insert(0, "/home/HTJ/t2/conf/code")
import common as C, dmimo, arms
d = os.path.expanduser("~/data/sionna_rt/srp_Nr8")
H = np.load(f"{d}/H.npy"); sp = np.load(f"{d}/split.npy"); m = np.load(f"{d}/meta.npz"); pos, row = m["pos"], m["row"]
n = len(H); NX, NY, S = 600, 576, 0.015
st = np.diff(pos, axis=0)
turn = np.where(np.abs(st[:, 1]) > 1e-9)[0]
print("all 345599 consecutive steps = 1.5 cm:", np.allclose(np.linalg.norm(st, axis=1), S), "| row turns (dy != 0):", len(turn), "at t = k*600-1:", np.array_equal(turn, np.arange(1, NY) * NX - 1),
      "| dx at turns = 0:", np.allclose(st[turn, 0], 0), "| x at turns:", np.unique(pos[turn, 0].round(4)))
g = dmimo.DMGen("SRP", 8, 4)
print("DMGen idx sizes:", {k: len(v) for k, v in g.idx.items()}, "| test idx == split 2:", np.array_equal(g.idx["test"], np.where(sp == 2)[0]), "| fit idx == split 0:", np.array_equal(g.idx["fit"], np.where(sp == 0)[0]))
# trial stream -> test pool, i.i.d. with replacement; training set stream 7 -> distinct subset of fit pool
r = C.trial_rng("D2", "SRP", 8, 16, 4, -3); print("trial stream -> pool:", dmimo._which(r, "SRP", 8))
r7 = C.train_rng("D2", "SRP", 8, 7); ix = g.idx["fit"]; i7 = ix[r7.permutation(len(ix))[:160000]]
print("stream 7: 160000 distinct:", len(np.unique(i7)) == 160000, "| all in fit pool:", np.isin(i7, ix).all(), "| rows covered:", len(np.unique(row[i7])), "of 489 | max row", row[i7].max())
# replay: the trial's pool index is NOT returned by DMGen.sample; a strata script must replay rng.integers in run_task's order
b = C.banner("D2", "SRP")
for s in ("SITE-SPECIFIC RAY-TRACED TESTBED (prior SRP)", "ONE UE MOVING along a lawn-mower route", "CLAIM TESTBED -- sparse specular", "FIVE", "ONE fixed BS"):
    print(repr(s), "in banner:", s in b)
Hf = H.reshape(n, -1); nrm = np.linalg.norm(Hf, axis=1)
corr1 = np.abs((Hf[:-1] * Hf[1:].conj()).sum(1)) / (nrm[:-1] * nrm[1:]); same = row[:-1] == row[1:]
print("|<h_t, h_t+1>| / norms, same row (1.5 cm along): median %.3f p10 %.3f p90 %.3f" % tuple(np.percentile(corr1[same], [50, 10, 90])))
j = np.arange(NX); i0 = 488 * NX + j; i1 = 489 * NX + (NX - 1 - j)
c2 = np.abs((Hf[i0] * Hf[i1].conj()).sum(1)) / (nrm[i0] * nrm[i1])
print("row 488 (last train) vs row 489 (first test) at the same x (1.5 cm across, yaw flipped): median %.3f p90 %.3f; x diff max %.1e" % (np.median(c2), np.percentile(c2, 90), np.abs(pos[i0, 0] - pos[i1, 0]).max()))
# the same with the UE array order reversed (yaw pi == reversed ULA up to a common phase for a horizontal ULA): compare H[:, ::-1]
Hr = H[i1][:, :, ::-1].reshape(len(i1), -1); c3 = np.abs((Hf[i0] * Hr.conj()).sum(1)) / (nrm[i0] * nrm[i1])
print("same, after reversing the UE elements of row 489: median %.3f p90 %.3f" % (np.median(c3), np.percentile(c3, 90)))
# leakage (testbed_dm's TDMh definition: nearest training channel, normalised squared distance) by test stratum of 29 rows
T = arms.training_set("D2", "SRP", 8, 4)          # (160000, 32) normalised vecs, column-major
Tn = (np.abs(T) ** 2).sum(1)
def leak(idx, rng):
    sel = rng.choice(idx, 600, replace=False)
    X = (H[sel] / g.s).transpose(0, 2, 1).reshape(len(sel), -1)
    G = X @ T.conj().T
    d2 = (np.abs(X) ** 2).sum(1)[:, None] + Tn[None, :] - 2 * G.real
    dm = d2.min(1) / (np.abs(X) ** 2).sum(1)
    return np.median(dm), (dm < 0.1).mean()
rng = np.random.default_rng(0); it = np.where(sp == 2)[0]
for name, lo, hi in (("first 29 rows (489-517, next to training)", 489, 517), ("middle 29 (518-546)", 518, 546), ("last 29 (547-575)", 547, 575)):
    med, fr = leak(it[(row[it] >= lo) & (row[it] <= hi)], rng); print(f"TDMh-style leakage, test stratum {name}: median {med:.4f}, share < 0.1 = {fr:.3f}")
med, fr = leak(it, rng); print(f"TDMh-style leakage, whole test pool (600 draws): median {med:.4f}, share < 0.1 = {fr:.3f}  (testbed_SRP.txt: 0.1833 / 0.073 on 2000 draws)")
# how far is the nearest training snapshot in SPACE for a test draw? (rows 489.. vs train rows <= 488)
print("done")
