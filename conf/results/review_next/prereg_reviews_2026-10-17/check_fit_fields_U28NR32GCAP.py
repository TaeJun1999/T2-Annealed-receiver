"""Read-only check of §0 claims of NEXT_EXPERIMENTS_U28NR32GCAP.md against the existing fit files (t2_wtS)."""
import numpy as np, glob, os, hashlib
D = "/home/HTJ/t2_wtS/conf/results/gmm_fits_D2_U28NR32B16e4"
f = np.load(f"{D}/fit_UMi28_Nr32_kronK4096_n160000.npz")
print("keys:", sorted(f.files))
ll = f["ll"]; print("n_iter", int(f["n_iter"]), "len(ll)", len(ll), "it_best", int(f["it_best"]), "restart", int(f["restart"]), "kappa", int(f["kappa"]))
print("ll_val", repr(float(f["ll_val"])), "ll_train", repr(float(f["ll_train"])), "ll[it_best]", repr(float(ll[int(f['it_best'])])), "gap", float(f["ll_train"]) - float(f["ll_val"]))
print("ll[29], ll[30]:", repr(float(ll[29])), repr(float(ll[30])), "diff", repr(float(ll[30] - ll[29])), "tol*|ll|", 1e-6 * abs(float(ll[30])))
print("legacy tol fires at it 30?", (ll[30] - ll[29]) < 1e-6 * abs(ll[30]), " gcap would fire?", 0 <= (ll[30] - ll[29]) < 1e-6 * abs(ll[30]))
print("any earlier it>=20 with dll < tol*|ll|?", [(i, float(ll[i]-ll[i-1])) for i in range(20, len(ll)) if ll[i]-ll[i-1] < 1e-6*abs(ll[i])])
print("ll trajectory:", np.round(ll, 4).tolist())
print("n_reseed", int(f["n_reseed"]), "kron_batched", f["kron_batched"], "cand", f["cand"].tolist(), "cand_ll_val", [repr(float(x)) for x in f["cand_ll_val"]])
print("sparse_tol", f["sparse_tol"], "sec", float(f["sec"]), "sec_best", float(f["sec_best"]))
print("--- candidates")
for r in range(3):
    c = np.load(f"{D}/fit_UMi28_Nr32_kronK4096_n160000.k0r{r}.npz")
    lc = c["ll"]
    print(f" r{r}: n_iter {int(c['n_iter'])} it_best {int(c['it_best'])} ll_val {float(c['ll_val'])!r} reseeds {int(c['n_reseed'])} last dll {float(lc[-1]-lc[-2]):+.3e} (decrease: {bool(lc[-1] < lc[-2])}) kron_batched {c['kron_batched']} sha {hashlib.sha256(open(f'{D}/fit_UMi28_Nr32_kronK4096_n160000.k0r{r}.npz','rb').read()).hexdigest()[:16]}")
print("--- grid ll_val")
for fam in ("full", "kron"):
    row = []
    for p in sorted(glob.glob(f"{D}/fit_UMi28_Nr32_{fam}K*_n160000.npz")):
        if ".k0r" in p: continue
        K = int(os.path.basename(p).split("K")[1].split("_")[0]); z = np.load(p)
        row.append((K, round(float(z["ll_val"]), 2), int(z["n_iter"]), int(z["it_best"]), float(z["sec"])))
    print(fam, sorted(row))
z = np.load(f"{D}/fit_UMi28_Nr32_fullK32_n160000.npz"); print("full32 ll_val", repr(float(z["ll_val"])), "keys has Chat", "Chat" in z.files)
tot = sum(float(np.load(p)["sec"]) for p in glob.glob(f"{D}/fit_UMi28_Nr32_*_n160000.npz") if ".k0r" not in p)
print("sum sec over merged files (em_sec as fit_cost_meta computes it):", tot)
