"""fit_gpu.py -- run the D2 GMM re-fit for ONE (Nr, fam, K) configuration on ONE GPU, with exactly the
protocol of runner.cmd_fit: same kappa grid, same restarts, same iteration cap, same validation-based
early stopping, same selection rule (validation log-likelihood ONLY), same fields in the same
arms.fit_path() file.  The EM itself is code/gmm_em_gpu.py (float64 port of the READ-ONLY
Demo/t2_gmm.py :: fit_gmm_em).

  CUDA_VISIBLE_DEVICES=k python code/fit_gpu.py <Nr> <fam> <K> [ntrain]

Never overwrites an existing fit file (the CPU run owns those).  Writes atomically.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import numpy as np
import arms as A
from runner import _sets, ref_task, FAM, KAPPAS, N_VAL, RESTARTS, FIT_ITERS, d_fits_d2
from gmm_em_gpu import fit_gmm_em_gpu


def main(Nr, fam, K, ntrain):
    prior, Nt = C.PRIOR_OF["D2"], C.NT
    out = A.fit_path("D2", prior, Nr, fam, K, ntrain)
    if os.path.exists(out):
        print(f"[gpu-fit] {out} exists -- CPU run owns it, skipping", flush=True)
        return 0
    os.makedirs(d_fits_d2(), exist_ok=True)
    gen, (X, Xv, Xt) = _sets(prior, Nr, Nt, ntrain)
    ref = ref_task((prior, Nr, Nt, ntrain))[1]
    kaps = KAPPAS if fam == "full" else (0,)
    rs = {}
    t0 = time.time()
    for kap in kaps:
        for r in range(RESTARTS):
            rng = np.random.default_rng([C.SEED, C.TBID["D2"], 9, C.PID[prior], Nr, FAM[fam], K, kap, r])
            t = time.time()
            f = fit_gmm_em_gpu(X, K, rng, n_iter=FIT_ITERS, kappa=float(kap), struct=fam,
                               dims=(Nr, Nt), Xval=Xv)
            f["ll_test"] = float(C.GMMPriorB(Nr, Nt, f["covs"], f["pi"]).log_pdf(Xt).mean())
            f["ll_train"] = float(f["ll"][f["it_best"]])
            f["sec"] = time.time() - t
            rs[(kap, r)] = f
            print(f"  ('{prior}', {Nr}, {Nt}, '{fam}', {K}, {kap}, {r}): iters {f['n_iter']} "
                  f"best@{f['it_best']} reseeds {f['n_reseed']} ll_train {f['ll_train']:.3f} "
                  f"ll_val {f['ll_val']:.3f} ({f['sec']:.0f} s)", flush=True)
    kb = max(rs, key=lambda k: rs[k]["ll_val"])          # selection: validation log-likelihood ONLY
    f, cand = rs[kb], sorted(rs)
    tmp = out + f".tmp{os.getpid()}.npz"
    np.savez_compressed(tmp, pi=f["pi"], covs=f["covs"], Chat=f["Chat"], ll=f["ll"],
                        kappa=kb[0], restart=kb[1], it_best=f["it_best"], n_iter=f["n_iter"],
                        n_reseed=f["n_reseed"], ll_train=f["ll_train"], ll_val=f["ll_val"],
                        ll_test=f["ll_test"], gauss_val=ref["gauss_val"], gauss_test=ref["gauss_test"],
                        sec=sum(rs[c]["sec"] for c in cand), sec_best=f["sec"],
                        cand=np.array(cand), cand_ll_val=np.array([rs[c]["ll_val"] for c in cand]),
                        cand_ll_test=np.array([rs[c]["ll_test"] for c in cand]),
                        ntrain=ntrain, n_val=N_VAL)
    if os.path.exists(out):                              # CPU won the race while we were fitting
        os.remove(tmp); print(f"[gpu-fit] {out} appeared meanwhile -- kept the CPU file", flush=True)
        return 0
    os.replace(tmp, out)
    print(f"[gpu-fit] {prior} Nr={Nr} {fam:<4} K={K:<3}: kappa {kb[0]:>3} restart {kb[1]} "
          f"best@{f['it_best']:<3} train-val gap {f['ll_train'] - f['ll_val']:6.3f}  "
          f"ll_test - ll_test(Gaussian) = {f['ll_test'] - ref['gauss_test']:6.3f} nat  "
          f"pi_min {f['pi'].min():.4f}  ({(time.time() - t0) / 60:.1f} min GPU over {len(cand)} EM runs) "
          f"-> {out}", flush=True)
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    sys.exit(main(int(a[0]), a[1], int(a[2]), int(a[3]) if len(a) > 3 else 160000))
