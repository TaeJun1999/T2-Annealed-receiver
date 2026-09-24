"""conf/code/em_batched_check_nr.py -- Nr-general version of em_batched_check.py / em_batched_check2.py for the C6 (Nr=16)
equal-budget point at N' = 1.6e5 (user decision 2026-09-24 17:45 CDT 무렵: "C6(Nr=16) 1.6e5 동일예산").

Is gmm_em_gpu's opt-in BATCHED kron M-step numerically the same EM as the exact per-component loop at Nr=16?
Two cases, both with Xval=None so the FINAL-iterate parameters are compared (em_batched_check2's lesson), seed tuple of
runner.cmd_fit restart 0:
  (a) the real C6 data at N'=160000, kron K=512, 6 iterations;
  (b) RESEED-ACTIVE: the real C6 data at N=10000, kron K=512, 15 iterations -- at 1e4 this configuration reseeded
      1010-1674 times per restart (gmm_fits_D2_NR16), so the starved-component branch of the batched path is exercised
      (the Nr=8 checks never were: 0 reseeds).  Case (b) counts only if the exact path reseeds at least once.
PASS criterion (fixed here, before the run; the same thresholds as em_batched_check): per case max |ll_t(batched) -
ll_t(exact)| <= 1e-6 nat/sample, max relative Frobenius difference of the final covariances <= 1e-6, max |pi difference|
<= 1e-9, the same number of reseeds; and case (b) has >= 1 reseed.  Then times the batched path at N'=160000, kron
K=1024 and 2048 (3 iterations each).  Output: results/nr16b_batched_check.txt.  GPU (one), no BLER.
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

NR, NT, PRIOR = 16, 4, "S2"
OUT = os.path.join(C.CONF, "results", "nr16b_batched_check.txt")


def run(X, K, batched, n_iter, r=0):
    rng = np.random.default_rng([C.SEED, C.TBID["D2"], 9, C.PID[PRIOR], NR, FAM["kron"], K, 0, r])
    torch.cuda.synchronize(); t = time.time()
    f = fit_gmm_em_gpu(X, K, rng, n_iter=n_iter, kappa=0.0, struct="kron", dims=(NR, NT), Xval=None, batched=batched)
    torch.cuda.synchronize()
    f["sec"] = time.time() - t
    return f


def compare(label, X, K, n_iter, need_reseed):
    ex, ba = run(X, K, False, n_iter), run(X, K, True, n_iter)
    dll = float(np.max(np.abs(ba["ll"] - ex["ll"]))) if len(ba["ll"]) == len(ex["ll"]) else np.inf
    dcov = float(np.max(np.linalg.norm(ba["covs"] - ex["covs"], axis=(1, 2)) / np.linalg.norm(ex["covs"], axis=(1, 2))))
    dpi = float(np.max(np.abs(ba["pi"] - ex["pi"])))
    good = dll <= 1e-6 and dcov <= 1e-6 and dpi <= 1e-9 and ba["n_reseed"] == ex["n_reseed"]
    if need_reseed:
        good &= ex["n_reseed"] >= 1
    return good, (f"{label}: exact {ex['sec']:.0f} s ({ex['sec'] / ex['n_iter']:.1f} s/iter), batched {ba['sec']:.0f} s "
                  f"({ba['sec'] / ba['n_iter']:.2f} s/iter, x{ex['sec'] / ba['sec']:.1f}); n_iter {ex['n_iter']}/{ba['n_iter']}, "
                  f"max|dll_t| {dll:.2e}, max rel dcov {dcov:.2e}, max|dpi| {dpi:.2e}, reseeds {ex['n_reseed']}/{ba['n_reseed']}"
                  f"{' (>= 1 required)' if need_reseed else ''} -> {'PASS' if good else 'FAIL'}")


def main():
    L = [C.header("D2", extra=["content     : C6 (Nr=16) equal-budget N'=1.6e5 -- batched vs exact kron M-step, final iterate, "
                               "real data; (a) N'=160000 K=512 6 it, (b) reseed-active N=10000 K=512 15 it"])]
    X16, _, _ = _sets(PRIOR, NR, NT, 160000)[1]
    X1, _, _ = _sets(PRIOR, NR, NT, 10000)[1]
    ok = True
    for lab, X, n_it, need in (("(a) N'=160000 K=512", X16, 6, False), ("(b) N=10000 K=512 reseed-active", X1, 15, True)):
        g, line = compare(lab, X, 512, n_it, need)
        ok &= g; L.append(line); print(line, flush=True)
    for K in (1024, 2048):
        t = run(X16, K, True, 3)
        L.append(f"timing N'=160000 kron K={K} batched: {t['sec']:.0f} s for {t['n_iter']} iterations "
                 f"({t['sec'] / t['n_iter']:.1f} s/iter), reseeds {t['n_reseed']}")
        print(L[-1], flush=True)
    L.append(f"VERDICT: {'PASS' if ok else 'FAIL'} (criterion in the module docstring)")
    txt = "\n".join(L) + "\n"
    with open(OUT, "w") as fh:
        fh.write(txt)
    print(txt, flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
