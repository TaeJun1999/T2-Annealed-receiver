"""audit U28NR32GCAP -- read the scalar / small fields of the fit files directly (numpy only; covs never loaded)."""
import numpy as np, hashlib, os, glob
G = "/home/HTJ/t2/conf/results/gmm_fits_D2_U28NR32GCAP"
S = "/home/HTJ/t2_wtS/conf/results/gmm_fits_D2_U28NR32B16e4"
files = {
 "A": f"{S}/fit_UMi28_Nr32_kronK4096_n160000.npz",
 "B": f"{G}/fit_UMi28_Nr32_kronK4096_n160000.cont50.npz",
 "Cr0": f"{G}/fit_UMi28_Nr32_kronK8192_n160000.k0r0.npz",
 "Cr1": f"{G}/fit_UMi28_Nr32_kronK8192_n160000.k0r1.npz",
 "Cr2": f"{G}/fit_UMi28_Nr32_kronK8192_n160000.k0r2.npz",
 "Cm": f"{G}/fit_UMi28_Nr32_kronK8192_n160000.npz",
 "full32": f"{S}/fit_UMi28_Nr32_fullK32_n160000.npz",
}
for name, f in files.items():
    z = np.load(f, allow_pickle=True)
    print(f"\n## {name}  {f}")
    for k in z.files:
        info = z.format if False else None
        # shape without loading: use zipfile sizes
    for k in sorted(z.files):
        try:
            if k in ("covs", "cov", "mu", "means", "Tk", "L"):
                # peek shape cheaply via header
                import zipfile
                with zipfile.ZipFile(f) as zf:
                    with zf.open(k + ".npy") as fh:
                        ver = np.lib.format.read_magic(fh)
                        shp, fo, dt = np.lib.format._read_array_header(fh, ver)
                print(f"  {k}: shape {shp} dtype {dt} (not loaded)")
                continue
            v = z[k]
            if v.ndim == 0:
                print(f"  {k}: {v.item()!r}")
            elif v.size <= 40:
                print(f"  {k}: {v.tolist()!r}")
            else:
                print(f"  {k}: shape {v.shape} dtype {v.dtype}  first {v.ravel()[:3].tolist()} last {v.ravel()[-3:].tolist()}")
        except Exception as e:
            print(f"  {k}: ERR {type(e).__name__} {e}")
# grid ll_val and em_sec over the merged files of the old folder
print("\n## old grid (merged files only)")
tot = 0.0
for f in sorted(glob.glob(f"{S}/fit_UMi28_Nr32_*_n160000.npz")):
    if ".k0r" in f: continue
    z = np.load(f, allow_pickle=True)
    sec = float(z["sec"]) if "sec" in z.files else float("nan")
    tot += sec
    print(f"  {os.path.basename(f)}: ll_val {float(z['ll_val'])!r}  sec {sec}")
print(f"  sum sec over merged files = {tot}")
