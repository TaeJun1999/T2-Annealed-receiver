"""conf/code/em_batched_check.py -- NEXT_EXPERIMENTS_B32e4 speed-up check 2 (user 2026-09-24: "좀 더 가속 … 자원을 몰아줘도").

Is gmm_em_gpu's opt-in BATCHED kron M-step (scatter matrices, all K at once; algebraically exact) numerically the same
EM as the exact per-component loop?  On the REAL B32e4 data
(N' = 3.2e5, the fit_gpu training / validation sets) with the seed tuple of kron K=1024 restart 0, run the exact path and
the batched path for the same number of iterations from the same initial state and compare.
PASS criterion (fixed here, before the run, the same as em_sparse_check): max |ll_t(batched) - ll_t(exact)| over the iterations
<= 1e-6 nat/sample, |ll_val(batched) - ll_val(exact)| <= 1e-6, max relative Frobenius difference of the final covariances
<= 1e-6, max |pi difference| <= 1e-9, and the same number of reseeds.  Then times the batched path at K=4096 (5 iterations).
Output: results/b32e4_batched_check.txt.  GPU (one), no BLER.
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

N_ITER, NTRAIN, NR, NT, PRIOR = 8, 320000, 8, 4, "S2"
OUT = os.path.join(C.CONF, "results", "b32e4_batched_check.txt")


def run(X, Xv, K, batched, n_iter, r=0):
    rng = np.random.default_rng([C.SEED, C.TBID["D2"], 9, C.PID[PRIOR], NR, FAM["kron"], K, 0, r])
    torch.cuda.synchronize(); t = time.time()
    f = fit_gmm_em_gpu(X, K, rng, n_iter=n_iter, kappa=0.0, struct="kron", dims=(NR, NT), Xval=Xv, batched=batched)
    torch.cuda.synchronize()
    f["sec"] = time.time() - t
    return f


def main():
    L = [C.header("D2", extra=["content     : NEXT_EXPERIMENTS_B32e4 speed-up 2 -- batched kron M-step vs exact EM on the "
                               f"real N'={NTRAIN} data, kron K=1024 restart-0 seed, {N_ITER} iterations"])]
    _, (X, Xv, Xt) = _sets(PRIOR, NR, NT, NTRAIN)
    ex = run(X, Xv, 1024, False, N_ITER)
    L.append(f"exact        : {ex['sec']:.0f} s ({ex['sec'] / ex['n_iter']:.1f} s/iter), n_iter {ex['n_iter']}, "
             f"reseeds {ex['n_reseed']}, ll_val {ex['ll_val']:.9f}")
    ok = True
    for tol in ("batched",):
        sp = run(X, Xv, 1024, True, N_ITER)
        dll = float(np.max(np.abs(sp["ll"] - ex["ll"]))) if len(sp["ll"]) == len(ex["ll"]) else np.inf
        dval = abs(sp["ll_val"] - ex["ll_val"])
        dcov = float(np.max(np.linalg.norm(sp["covs"] - ex["covs"], axis=(1, 2)) / np.linalg.norm(ex["covs"], axis=(1, 2))))
        dpi = float(np.max(np.abs(sp["pi"] - ex["pi"])))
        good = dll <= 1e-6 and dval <= 1e-6 and dcov <= 1e-6 and dpi <= 1e-9 and sp["n_reseed"] == ex["n_reseed"]
        ok &= good
        L.append(f"batched     : {sp['sec']:.0f} s ({sp['sec'] / sp['n_iter']:.1f} s/iter, x{ex['sec'] / sp['sec']:.1f}), "
                 f"max|dll_t| {dll:.2e}, |dll_val| {dval:.2e}, max rel dcov {dcov:.2e}, max|dpi| {dpi:.2e}, "
                 f"reseeds {sp['n_reseed']} -> {'PASS' if good else 'FAIL'}")
    t4 = run(X, Xv, 4096, True, 5)
    L.append(f"timing K=4096 batched: {t4['sec']:.0f} s for {t4['n_iter']} iterations ({t4['sec'] / t4['n_iter']:.1f} s/iter)")
    L.append(f"VERDICT: {'PASS' if ok else 'FAIL'} (criterion in the module docstring)")
    txt = "\n".join(L) + "\n"
    with open(OUT, "w") as fh:
        fh.write(txt)
    print(txt, flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
