"""conf/code/em_sparse_check.py -- NEXT_EXPERIMENTS_B32e4 speed-up check (user decision 2026-09-24: "EM 구현 가속").

Is gmm_em_gpu's opt-in sparse kron M-step (sparse_tol) numerically the same EM as the exact path?  On the REAL B32e4 data
(N' = 3.2e5, the fit_gpu training / validation sets) with the seed tuple of kron K=1024 restart 0, run the exact path and
the sparse path (tol 1e-12 and 1e-14) for the same number of iterations from the same initial state and compare.
PASS criterion (fixed here, before the run): for both tolerances, max |ll_t(sparse) - ll_t(exact)| over the iterations
<= 1e-6 nat/sample, |ll_val(sparse) - ll_val(exact)| <= 1e-6, max relative Frobenius difference of the final covariances
<= 1e-6, max |pi difference| <= 1e-9, and the same number of reseeds.  Then times the sparse path at K=4096 (3 iterations).
Output: results/b32e4_sparse_check.txt.  GPU (one), no BLER.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import numpy as np
import torch
from runner import _sets, FAM
from gmm_em_gpu import fit_gmm_em_gpu

N_ITER, NTRAIN, NR, NT, PRIOR = 12, 320000, 8, 4, "S2"
OUT = os.path.join(C.CONF, "results", "b32e4_sparse_check.txt")


def run(X, Xv, K, tol, n_iter, r=0):
    rng = np.random.default_rng([C.SEED, C.TBID["D2"], 9, C.PID[PRIOR], NR, FAM["kron"], K, 0, r])
    torch.cuda.synchronize(); t = time.time()
    f = fit_gmm_em_gpu(X, K, rng, n_iter=n_iter, kappa=0.0, struct="kron", dims=(NR, NT), Xval=Xv, sparse_tol=tol)
    torch.cuda.synchronize()
    f["sec"] = time.time() - t
    return f


def main():
    L = [C.header("D2", extra=["content     : NEXT_EXPERIMENTS_B32e4 speed-up -- sparse kron M-step vs exact EM on the "
                               f"real N'={NTRAIN} data, kron K=1024 restart-0 seed, {N_ITER} iterations"])]
    _, (X, Xv, Xt) = _sets(PRIOR, NR, NT, NTRAIN)
    ex = run(X, Xv, 1024, None, N_ITER)
    L.append(f"exact        : {ex['sec']:.0f} s ({ex['sec'] / ex['n_iter']:.1f} s/iter), n_iter {ex['n_iter']}, "
             f"reseeds {ex['n_reseed']}, ll_val {ex['ll_val']:.9f}")
    ok = True
    for tol in (1e-12, 1e-14):
        sp = run(X, Xv, 1024, tol, N_ITER)
        dll = float(np.max(np.abs(sp["ll"] - ex["ll"]))) if len(sp["ll"]) == len(ex["ll"]) else np.inf
        dval = abs(sp["ll_val"] - ex["ll_val"])
        dcov = float(np.max(np.linalg.norm(sp["covs"] - ex["covs"], axis=(1, 2)) / np.linalg.norm(ex["covs"], axis=(1, 2))))
        dpi = float(np.max(np.abs(sp["pi"] - ex["pi"])))
        good = dll <= 1e-6 and dval <= 1e-6 and dcov <= 1e-6 and dpi <= 1e-9 and sp["n_reseed"] == ex["n_reseed"]
        ok &= good
        L.append(f"sparse {tol:.0e}: {sp['sec']:.0f} s ({sp['sec'] / sp['n_iter']:.1f} s/iter, x{ex['sec'] / sp['sec']:.1f}), "
                 f"max|dll_t| {dll:.2e}, |dll_val| {dval:.2e}, max rel dcov {dcov:.2e}, max|dpi| {dpi:.2e}, "
                 f"reseeds {sp['n_reseed']}, max dropped mass {sp['sparse_max_dropped']:.2e} -> {'PASS' if good else 'FAIL'}")
    t4 = run(X, Xv, 4096, 1e-12, 3)
    L.append(f"timing K=4096 sparse 1e-12: {t4['sec']:.0f} s for {t4['n_iter']} iterations "
             f"({t4['sec'] / t4['n_iter']:.1f} s/iter), max dropped mass {t4['sparse_max_dropped']:.2e}")
    L.append(f"VERDICT: {'PASS' if ok else 'FAIL'} (criterion in the module docstring)")
    txt = "\n".join(L) + "\n"
    with open(OUT, "w") as fh:
        fh.write(txt)
    print(txt, flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
