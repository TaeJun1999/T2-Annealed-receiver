"""conf/code/em_batched_check2.py -- strengthening of em_batched_check.py (its 8-iteration run only evaluated ll_val at
iteration 0, so its covariance / pi comparison was between two copies of the initial state -- vacuous).  Here Xval=None,
so fit_gmm_em_gpu returns the FINAL-iteration parameters: exact vs batched kron M-step on the real N'=3.2e5 data, K=1024,
restart-0 seed, 4 iterations.  PASS (same thresholds): max |dll_t| <= 1e-6, max rel Frobenius dcov <= 1e-6, max |dpi| <= 1e-9,
same reseeds.  Output: results/b32e4_batched_check2.txt."""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import numpy as np
import torch
from runner import _sets, FAM
from gmm_em_gpu import fit_gmm_em_gpu

X, _, _ = _sets("S2", 8, 4, 320000)[1]
res = {}
for b in (False, True):
    rng = np.random.default_rng([C.SEED, C.TBID["D2"], 9, C.PID["S2"], 8, FAM["kron"], 1024, 0, 0])
    t = time.time()
    res[b] = fit_gmm_em_gpu(X, 1024, rng, n_iter=4, kappa=0.0, struct="kron", dims=(8, 4), Xval=None, batched=b)
    torch.cuda.synchronize(); res[b]["sec"] = time.time() - t
ex, ba = res[False], res[True]
dll = float(np.max(np.abs(ba["ll"] - ex["ll"])))
dcov = float(np.max(np.linalg.norm(ba["covs"] - ex["covs"], axis=(1, 2)) / np.linalg.norm(ex["covs"], axis=(1, 2))))
dpi = float(np.max(np.abs(ba["pi"] - ex["pi"])))
ok = dll <= 1e-6 and dcov <= 1e-6 and dpi <= 1e-9 and ba["n_reseed"] == ex["n_reseed"]
txt = (C.header("D2", extra=["content     : em_batched_check2 -- FINAL-iterate exact vs batched kron M-step, N'=3.2e5, K=1024, 4 iterations"])
       + f"\nexact {ex['sec']:.0f} s, batched {ba['sec']:.0f} s; max|dll_t| {dll:.2e}, max rel dcov {dcov:.2e}, max|dpi| {dpi:.2e}, "
       f"reseeds {ex['n_reseed']}/{ba['n_reseed']} -> {'PASS' if ok else 'FAIL'}\n")
open(os.path.join(C.CONF, "results", "b32e4_batched_check2.txt"), "w").write(txt)
print(txt, flush=True)
sys.exit(0 if ok else 1)
