"""§5 material of a pool-prior registration (DMC16e4 / SRT16e4) read from the files (no hand transcription): grid table, mtimes,
sigma grid, checkpoints.  Usage (cwd anywhere): python s5_gen.py <PRIOR> <TAG>      -- run only AFTER the freeze commit (it prints ll_val)."""
import glob, os, sys, time
import numpy as np
os.chdir("/home/HTJ/t2/conf"); sys.path.insert(0, "code")
PR, TAG = sys.argv[1], sys.argv[2]
D = f"results/gmm_fits_D2_{TAG}"
cdt = lambda t: time.strftime("%m-%d %H:%M:%S", time.gmtime(t - 5 * 3600)) + " CDT"
g = lambda z, k: (z[k].item() if k in z.files and z[k].ndim == 0 else None)
rows = {}
for f in sorted(glob.glob(f"{D}/fit_{PR}_Nr8_*_n160000*.npz")):
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
z = np.load(f"results/sigma_grid_D2_{PR}.npz"); print("sigma grid keys:", z.files)
for k in z.files:
    v = np.asarray(z[k]); 
    if v.ndim == 1 and v.size >= 2 and v.dtype.kind == "f": print(" ", k, v.size, repr(float(v.min())), repr(float(v.max())))
for f in sorted(glob.glob(f"results/d2_gbprime_{PR}*")):
    print("GB' file:", f, cdt(os.path.getmtime(f)))
import hashlib, torch
STEMS = sys.argv[3:] or [f"d2sx_{PR}_N160000_a1"]                 # optional: checkpoint stems (e.g. the fallback attempts)
for role, f in [(r + " " + s, f"ckpt/{s}{x}.pt") for s in STEMS for r, x in (("best", "_best"), ("last", ""))]:
    if os.path.exists(f):
        c = torch.load(f, map_location="cpu", weights_only=False)
        print(role, f, "sha256[:16]", hashlib.sha256(open(f, "rb").read()).hexdigest()[:16], "mtime", cdt(os.path.getmtime(f)),
              {k: c.get(k) for k in ("epoch", "best_epoch", "best_val", "val_loss", "stopped_by", "role", "prior", "sigma_tag", "rung", "attempt", "grad_clip", "split_hash") if k in c})
for f in (f"logs/tb2_train_state_{PR}.txt", f"logs/tb2_post_{PR}.sel"):
    print(f, "->", open(f).read().strip() if os.path.exists(f) else "(missing)")
for f in (f"results/sparse/pick_{PR}_C2.json", f"results/sparse/tune_{PR}_C2.json", f"results/ald/tune_PIL{PR}.json", f"results/ald/tune_PIL{PR}_curves.npz"):
    print(f, "sha256[:16]", hashlib.sha256(open(f, "rb").read()).hexdigest()[:16], "mtime", cdt(os.path.getmtime(f))) if os.path.exists(f) else print(f, "(missing)")
