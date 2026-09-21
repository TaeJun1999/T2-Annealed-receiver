"""H5 provenance: did results/hyvarinen_D2_n1e4.npz come from ckpt/d2sx_N10000_a1.pt (and a2)?
Reproduce selected sigma rows with the IDENTICAL H/E/grid and compare to the stored npz."""
import os, sys, json, hashlib, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, torch
import common as C, score, arms as A, hyvarinen as HY

NR, NT = 8, 4
n   = int(sys.argv[1]) if len(sys.argv) > 1 else 2048
ks  = [int(x) for x in (sys.argv[2].split(",") if len(sys.argv) > 2 else ["0","6","12","19"])]
torch.set_default_dtype(torch.float64)

ref = np.load("results/hyvarinen_D2_n1e4.npz", allow_pickle=True)
names, sm, se = list(ref["names"]), ref["sm"], ref["se"]
print("# stored names:", names)

gen = C.make_gen("D2", "S2", NR, NT)
nu_grid, sig_grid = __import__("sigma").load("D2")
H = gen.sample_vecs(C.train_rng("D2", "S2", NR, 10), n)
rng = np.random.default_rng(score.SEED_GATE)
E = (rng.standard_normal((n, NR*NT)) + 1j*rng.standard_normal((n, NR*NT))) / np.sqrt(2)

fits, llv, bstar, kron_K = A.gmm_selection("D2", "S2", NR, 10000)
fam, K = ("kron", kron_K) if bstar == "kron" else ("full", int(bstar[3:]))
gmm = C.GMMPriorB(NR, NT, fits[(fam, K)]["covs"], fits[(fam, K)]["pi"])

cands = {f"GMM b*={bstar} K={K} @N=10000": ("(exact GMM)", score.ExactGMMTorch(gmm)),
         "diff N=1e4 a1": ("ckpt/d2sx_N10000_a1.pt", None),
         "diff N=1e4 a2": ("ckpt/d2sx_N10000_a2.pt", None),
         "ALT B3":        ("ckpt/B3_dscore_D2.pt",   None),
         "ALT N2500":     ("ckpt/d2sx_N2500_a1.pt",  None)}
only = sys.argv[3].split("|") if len(sys.argv) > 3 else list(cands)
cands = {t: v for t, v in cands.items() if t in only}
models = {}
for t, (p, m) in cands.items():
    models[t] = (p, m if m is not None else score._as_model(p, NR, NT, "cpu")[0],
                 "" if m is not None else hashlib.sha256(open(p,'rb').read()).hexdigest()[:16])

out = {"n": n, "ks": ks, "sigma": [float(sig_grid[k]) for k in ks], "rows": {}}
print(f"\n# n={n}  (stored run used n_eval=2048)")
print(f"{'model':<28}{'ckpt':<26}{'k':>3} {'sigma':>10} {'SM recomputed':>18} {'SM stored':>18} {'rel dev':>11}")
for t, (p, m, sh) in models.items():
    ridx = names.index(t) if t in names else None
    out["rows"][t] = {"ckpt": p, "sha256_16": sh, "sm": [], "stored": [], "rel_dev": []}
    for k in ks:
        t0 = time.time()
        Q = torch.as_tensor(score.np_pack(H + np.sqrt(nu_grid[k])*E), dtype=torch.float64)
        tr, q = HY.sm_terms(m, Q, sig_grid[k])
        v = float((tr+q).mean())
        st = float(sm[ridx, k]) if ridx is not None else float("nan")
        rd = abs(v/st - 1) if ridx is not None else float("nan")
        out["rows"][t]["sm"].append(v); out["rows"][t]["stored"].append(st); out["rows"][t]["rel_dev"].append(rd)
        print(f"{t:<28}{p:<26}{k:>3} {sig_grid[k]:>10.4e} {v:>18.4f} {st:>18.4f} {rd:>11.3e}"
              f"   [{time.time()-t0:.0f}s]", flush=True)
json.dump(out, open(os.environ.get("OUTJ","results/diag/checkpoint-provenance_hyvarinen.json"),"w"), indent=1)
print("-> results/diag/checkpoint-provenance_hyvarinen.json")
