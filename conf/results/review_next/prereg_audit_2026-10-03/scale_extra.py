"""Extra checks for the SCALE16e4 §6.1 audit: §5 stop-reason counts quoted in G_d (tol / patience / cap over the 24 fits files
per new cell: 15 merged + 9 kron candidates), and the run_manifest config_hash definition (why tags of different datasets share a hash)."""
import glob, os, re, numpy as np
CONF = "/home/HTJ/t2_wtS/conf"
for T, prior, nr in (("NR32B16e4", "S2", 32), ("U28NR16B16e4", "UMi28", 16), ("U28NR32B16e4", "UMi28", 32)):
    d = os.path.join(CONF, f"results/gmm_fits_D2_{T}")
    fs = sorted(glob.glob(os.path.join(d, f"fit_{prior}_Nr{nr}_*K*_n160000.npz")) + glob.glob(os.path.join(d, f"fit_{prior}_Nr{nr}_*K*_n160000.k0r?.npz")))
    cnt = {"tol": 0, "patience": 0, "cap": 0}; pat = []
    for f in fs:
        with np.load(f, allow_pickle=True) as z:
            n, ib = int(z["n_iter"]), int(z["it_best"])
            r = "cap" if n == 500 else "patience" if n - 1 - ib >= 40 else "tol"
            cnt[r] += 1
            if r != "tol":
                pat.append((os.path.basename(f)[len(f"fit_{prior}_Nr{nr}_"):], n, ib))
    print(f"{T}: files {len(fs)} merged {sum('.k0r' not in f for f in fs)} candidates {sum('.k0r' in f for f in fs)} -> {cnt} non-tol {pat}")
src = open(os.path.join(CONF, "code/run_manifest.py")).read()
i = src.find("config_hash")
print("\nrun_manifest.py config_hash context:")
for m in re.finditer(r"config_hash", src):
    s = src.rfind("\n", 0, m.start()); e = src.find("\n", m.end())
    print("   ", src[s + 1:e].strip()[:200])
