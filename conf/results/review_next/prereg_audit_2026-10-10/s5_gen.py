"""§5 material of NEXT_EXPERIMENTS_DMC16e4 read from the files (no hand transcription): grid table, mtimes, sigma grid."""
import glob, os, sys, time
import numpy as np
os.chdir("/home/HTJ/t2/conf"); sys.path.insert(0, "code")
D = "results/gmm_fits_D2_DMCB16e4"
cdt = lambda t: time.strftime("%m-%d %H:%M:%S", time.gmtime(t - 5 * 3600)) + " CDT"
g = lambda z, k: (z[k].item() if k in z.files and z[k].ndim == 0 else None)
rows = {}
for f in sorted(glob.glob(f"{D}/fit_DMC_Nr8_*_n160000*.npz")):
    z = np.load(f, allow_pickle=True); b = os.path.basename(f)
    fam = "full" if "_fullK" in b else "kron"; K = int(b.split("K")[1].split("_")[0]); cand = b.split("n160000")[1].replace(".npz", "")
    rows[(fam, K, cand)] = dict(ll=float(z["ll_val"]), n_iter=g(z, "n_iter"), it_best=g(z, "it_best"), rs=g(z, "n_reseed"), restart=g(z, "restart"),
                               kappa=g(z, "kappa"), mtime=os.path.getmtime(f), batched=("kron_batched" in z.files and float(np.atleast_1d(z["kron_batched"])[0]) == 1.0))
for fam in ("full", "kron"):
    out = []
    for (f_, K, cand), r in sorted(rows.items()):
        if f_ != fam or cand: continue
        cap = " **상한 500 정지**" if r["n_iter"] == 500 else ""
        s = f"{K} {r['ll']:.3f} (r{r['restart']}, {r['n_iter']}/{r['it_best']}{cap}, 재시드 {r['rs']:,}, κ={r['kappa']})"
        if K >= 1024:
            cs = [f"r{c[-1]} {rows[(fam, K, c)]['ll']:.3f} {rows[(fam, K, c)]['n_iter']}/{rows[(fam, K, c)]['it_best']} rs {rows[(fam, K, c)]['rs']:,}" for c in (".k0r0", ".k0r1", ".k0r2")]
            s = f"**{K} {r['ll']!r}** (r{r['restart']}, {r['n_iter']}/{r['it_best']}, rs {r['rs']:,}; 후보 " + ", ".join(cs) + ")"
        out.append(s)
    print(f"[{fam}] ({'일괄' if fam == 'kron' else '정확'} 경로: batched flags {sorted({r['batched'] for (f_, K, c), r in rows.items() if f_ == fam})})\n  " + " / ".join(out))
print("merged mtimes:", {K: cdt(rows[("kron", K, "")]["mtime"]) for K in (1024, 2048, 4096)})
print("candidate mtimes 4096:", [cdt(rows[("kron", 4096, c)]["mtime"]) for c in (".k0r0", ".k0r1", ".k0r2")])
print("n files:", len(rows), "| max iter over all:", max(r["n_iter"] for r in rows.values()))
z = np.load("results/sigma_grid_D2_DMC.npz"); print("sigma grid keys:", z.files)
for k in z.files:
    v = np.asarray(z[k]); 
    if v.ndim == 1 and v.size >= 2 and v.dtype.kind == "f": print(" ", k, v.size, repr(float(v.min())), repr(float(v.max())))
for f in sorted(glob.glob("results/d2_gbprime_DMC*")):
    print("GB' file:", f, cdt(os.path.getmtime(f)))
