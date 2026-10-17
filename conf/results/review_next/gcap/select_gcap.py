"""select_gcap.py -- NEXT_EXPERIMENTS_U28NR32GCAP §1.2: final b* = argmax validation ll over {A, B, C} (strict >), B a
distinct candidate only when its best state > 0.  Reads the three fit files only (no raw, no BLER, no ll_test used).
    python select_gcap.py > select_U28NR32GCAP.out"""
import hashlib
import os
import numpy as np

A = "/home/HTJ/t2_wtS/conf/results/gmm_fits_D2_U28NR32B16e4/fit_UMi28_Nr32_kronK4096_n160000.npz"
D = "/home/HTJ/t2/conf/results/gmm_fits_D2_U28NR32GCAP/"
B, C = D + "fit_UMi28_Nr32_kronK4096_n160000.cont50.npz", D + "fit_UMi28_Nr32_kronK8192_n160000.npz"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
g = lambda z, k: (z[k].item() if z[k].shape == () else z[k]) if k in z.files else None

cand = {}
za = np.load(A)
cand["A"] = float(za["ll_val"])
print(f"A  {A}\n   ll_val {cand['A']!r}  it_best {int(za['it_best'])}  n_iter {int(za['n_iter'])}")
if os.path.exists(B):
    zb = np.load(B)
    print(f"B  {B}\n   ll_val {float(zb['ll_val'])!r}  best state {int(zb['it_best'])}  stop {g(zb, 'stop')}  "
          f"status {g(zb, 'status')}  steps {int(zb['steps_done'])}/{int(zb['steps_requested'])}")
    print("   validation trajectory (state, ll_val): " + ", ".join(f"({int(i)}, {v!r})" for i, v in zb["ll_val_traj"]))
    if int(zb["it_best"]) > 0:
        cand["B"] = float(zb["ll_val"])
    else:
        print("   best state = 0 = A itself -> not a distinct candidate (§1.2)")
else:
    print(f"B  missing ({B}) -> not a candidate (recorded as a failed process, §1.5)")
if os.path.exists(C):
    zc = np.load(C)
    print(f"C  {C}\n   ll_val {float(zc['ll_val'])!r}  restart {int(zc['restart'])}  it_best {int(zc['it_best'])}  "
          f"n_iter {int(zc['n_iter'])}  stop {g(zc, 'stop')}")
    print(f"   candidates (kappa, restart) {zc['cand'].tolist()}  ll_val {[repr(float(v)) for v in zc['cand_ll_val']]}  "
          f"stop {g(zc, 'cand_stop').tolist() if g(zc, 'cand_stop') is not None else None}")
    for r in range(3):
        f = D + f"fit_UMi28_Nr32_kronK8192_n160000.k0r{r}.npz"
        z = np.load(f)
        print(f"   r{r}: n_iter {int(z['n_iter'])} it_best {int(z['it_best'])} reseeds {int(z['n_reseed'])} stop {g(z, 'stop')} "
              f"sec {float(z['sec']):.0f}  val traj " + ", ".join(f"({int(i)}, {v:.4f})" for i, v in z["ll_val_traj"]))
    cand["C"] = float(zc["ll_val"])
else:
    print(f"C  missing ({C}) -> not a candidate (§1.5)")
best = max(cand, key=cand.get)
path = {"A": A, "B": B, "C": C}[best]
print(f"\nFINAL {best}  ll_val {cand[best]!r}  path {path}  sha256 {sha(path)}")
print("candidates " + "  ".join(f"{k} {v!r}" for k, v in sorted(cand.items())))
