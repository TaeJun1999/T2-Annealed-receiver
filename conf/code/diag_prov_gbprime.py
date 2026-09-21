"""H5 provenance: which checkpoint produced results/gate_D2.txt?  Recompute GB' (n_eval=512, D2/S2 8x4)
for every candidate D2 checkpoint on the identical frozen sigma grid and compare to the recorded table."""
import os, sys, json, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, torch
import common as C, score, arms as A

NR, NT, NEV = 8, 4, 512
torch.set_default_dtype(torch.float64)

fits, llv, bstar, kron_K = A.gmm_selection("D2", "S2", NR, 10000)
fam, K = ("kron", kron_K) if bstar == "kron" else ("full", int(bstar[3:]))
gmm = C.GMMPriorB(NR, NT, fits[(fam, K)]["covs"], fits[(fam, K)]["pi"])
print(f"# gmm b*={bstar} K={K}  ll_val={llv[bstar]:.9f}", flush=True)

# recorded gate_D2.txt table
rec = []
for ln in open("results/gate_D2.txt"):
    p = ln.split()
    if len(p) == 6 and p[0].isdigit():
        rec.append([float(x) for x in p[1:]])
rec = np.array(rec)

gen = C.make_gen("D2", "S2", NR, NT)
_, _, nu_grid, sig_grid = score._sigma_range("D2")
H = gen.sample_vecs(C.train_rng("D2", "S2", NR, 10), NEV)
nrng = np.random.default_rng(score.SEED_GATE)
E = (nrng.standard_normal((NEV, NR*NT)) + 1j*nrng.standard_normal((NEV, NR*NT))) / np.sqrt(2)
p_h = float(np.mean(np.sum(np.abs(H)**2, 1)))

# GMM column once
nmse_gmm = np.array([float(np.mean([np.sum(np.abs(gmm.denoise(H[i]+np.sqrt(nu)*E[i], nu)[0]-H[i])**2)
                                    for i in range(NEV)]))/p_h for nu in nu_grid])
print("# nmse_gmm recomputed vs recorded: max rel dev = "
      f"{np.max(np.abs(nmse_gmm/rec[:,2]-1)):.3e}", flush=True)

cands = ["ckpt/B3_dscore_D2.pt", "ckpt/d2sx_N10000_a1.pt", "ckpt/d2sx_N10000_a2.pt",
         "ckpt/d2sx_N10000_a3.pt", "ckpt/d2sx_N2500_a1.pt", "ckpt/d2sx_N40000_a1.pt",
         "ckpt/d2sx_N160000_a1.pt"]
out = {"n_eval": NEV, "gmm_bstar": bstar, "gmm_K": int(K), "ll_val": float(llv[bstar]),
       "nmse_gmm_recomputed": nmse_gmm.tolist(), "nmse_gmm_recorded": rec[:,2].tolist(),
       "nmse_diff_recorded_gate_D2": rec[:,3].tolist(), "sigma": sig_grid.tolist(), "candidates": {}}
for ck in cands:
    m = score._as_model(ck, NR, NT, "cpu")[0]
    col = []
    for nu, sg in zip(nu_grid, sig_grid):
        Q = H + np.sqrt(nu)*E
        X = torch.as_tensor(score.np_pack(Q), dtype=torch.float64)
        with torch.no_grad():
            mm = score.np_unpack(score.tweedie_real(m, X, torch.full((len(X),), float(sg),
                                                                     dtype=X.dtype)).numpy())
        col.append(float(np.mean(np.sum(np.abs(mm-H)**2, 1)))/p_h)
    col = np.array(col)
    reldev = np.abs(col/rec[:,3]-1)
    sha = hashlib.sha256(open(ck,'rb').read()).hexdigest()
    out["candidates"][ck] = {"sha256": sha, "nmse_diff": col.tolist(),
                             "max_rel_dev_vs_gate_D2": float(reldev.max()),
                             "worst_excess": float((col/nmse_gmm - 1).max()),
                             "ratio_min": float((col/nmse_gmm).min()),
                             "ratio_max": float((col/nmse_gmm).max())}
    print(f"{ck:<30} sha={sha[:16]}  max|rel dev vs gate_D2| = {reldev.max():.3e}"
          f"   worst_excess={float((col/nmse_gmm-1).max()):+.6f}"
          f"   ratio {float((col/nmse_gmm).min()):.4f}->{float((col/nmse_gmm).max()):.4f}", flush=True)
json.dump(out, open("results/diag/checkpoint-provenance_gbprime.json","w"), indent=1)
print("-> results/diag/checkpoint-provenance_gbprime.json")
