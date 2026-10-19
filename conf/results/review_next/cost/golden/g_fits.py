"""golden helper: re-derive the b* rule (validation log-likelihood; kron family = its own best K first) for several
fits-folder compositions, reading only 'll_val' and the npy header of 'covs' (no full array load).
Rule as specified in conf/code/arms.py gmm_selection (written independently here, not imported)."""
import os, re, sys, zipfile
import numpy as np

D2_KS = (16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192)
PAT = re.compile(r"^fit_(?P<prior>[^_]+)_Nr(?P<Nr>\d+)_(?P<fam>full|kron)K(?P<K>\d+)_n(?P<n>\d+)\.npz$")

def covs_shape(p):
    with zipfile.ZipFile(os.path.realpath(p)) as z:
        with z.open("covs.npy") as f:
            v = np.lib.format.read_magic(f)
            shape, fortran, dtype = (np.lib.format.read_array_header_1_0 if v == (1, 0) else np.lib.format.read_array_header_2_0)(f)
    return shape, str(dtype)

def info(paths, prior, Nr, ntrain):
    fits = {}
    for p in paths:
        m = PAT.match(os.path.basename(p))
        if not m or m["prior"] != prior or int(m["Nr"]) != Nr or int(m["n"]) != ntrain or int(m["K"]) not in D2_KS:
            continue
        with np.load(os.path.realpath(p)) as z:
            fits[(m["fam"], int(m["K"]))] = dict(ll_val=float(z["ll_val"]), path=p)
    return fits

def select(fits):
    Ks = sorted(K for fam, K in fits if fam == "full")
    llv = {f"gmm{K}": fits[("full", K)]["ll_val"] for K in Ks}
    kron = [(K, fits[("kron", K)]["ll_val"]) for fam, K in fits if fam == "kron"]
    kron_K = max(kron, key=lambda t: t[1])[0] if kron else None
    if kron_K is not None:
        llv["kron"] = fits[("kron", kron_K)]["ll_val"]
    bstar = max(llv, key=llv.get)
    K_arm = (kron_K if bstar == "kron" else int(bstar[3:]))
    return llv, bstar, kron_K, K_arm

def show(name, paths, prior, Nr, ntrain=160000, shapes=True):
    fits = info(paths, prior, Nr, ntrain)
    print(f"== {name}: {len(fits)} usable fit(s): " + ", ".join(f"{f}K{K}" for f, K in sorted(fits)))
    for k in sorted(fits):
        print(f"   {k[0]:>4}K{k[1]:<5} ll_val = {fits[k]['ll_val']!r}")
    has_full32 = ("full", 32) in fits
    llv, bstar, kron_K, K_arm = select(fits)
    print(f"   -> b* = {bstar!r}, kron_K = {kron_K}, K of M-ours-bstar = {K_arm}, full32 present (Chat for build_baseline_arms) = {has_full32}")
    if shapes:
        key = ("kron", kron_K) if bstar == "kron" else ("full", K_arm)
        print(f"   covs header of the b* file: {covs_shape(fits[key]['path'])}")

B = "/home/HTJ/t2/conf/results/gmm_fits_D2_B16e4k"
W = "/home/HTJ/t2_wtS/conf/results/gmm_fits_D2_U28NR32B16e4"
G = "/home/HTJ/t2/conf/results/gmm_fits_D2_U28NR32GCAP"
d2two = [f"{B}/fit_S2_Nr8_fullK32_n160000.npz", f"{B}/fit_S2_Nr8_kronK1024_n160000.npz"]
u4096 = [f"{W}/fit_UMi28_Nr32_fullK32_n160000.npz", f"{W}/fit_UMi28_Nr32_kronK4096_n160000.npz"]
u8192 = [f"{W}/fit_UMi28_Nr32_fullK32_n160000.npz", f"{G}/fit_UMi28_Nr32_kronK8192_n160000.npz"]
show("D2 two files (full32 + kron1024)", d2two, "S2", 8)
show("D2 whole B16e4k folder (Nr8 files)", [os.path.join(B, f) for f in os.listdir(B)], "S2", 8, shapes=False)
show("UMi32 K4096 two files (full32 + kron4096)", u4096, "UMi28", 32)
show("UMi32 GCAP two files (full32 + kron8192)", u8192, "UMi28", 32)
show("UMi32 whole U28NR32B16e4 folder", [os.path.join(W, f) for f in os.listdir(W)], "UMi28", 32, shapes=False)
show("EDGE: original GCAP folder alone", [os.path.join(G, f) for f in os.listdir(G)], "UMi28", 32, shapes=False)
show("EDGE: full32 + kron4096 + kron8192 in ONE folder", u4096 + u8192[1:], "UMi28", 32, shapes=False)
for p in d2two + u4096 + u8192[1:]:
    print("covs header", os.path.basename(p), covs_shape(p))
