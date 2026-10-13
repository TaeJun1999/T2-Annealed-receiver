"""recompute_dmi_emcont.py -- RECORD AUDIT of NEXT_EXPERIMENTS_ROOM16e4.md 5-DMI: HOW FAR from an EM fixed point is the evaluated
b* (fit_DMI_Nr8_fullK1024_n160000.npz)?  The registered EM run ended at iteration 71 on a negative train-ll step (the tolerance
break of gmm_em_gpu.py:142 also fires on a decrease), while its last increments were ~0.0017 nat / iteration (15 x the tolerance)
and the validation likelihood was best at the last validation point (it 70).  This script CONTINUES plain EM on the CPU from the
stored snapshot (pi, covs = the it-70 state) and reports the train / validation / test log-likelihood per iteration:
  * same data: runner._sets("DMI", 8, 4, 160000) = train stream 7 (n 160000), validation stream 8 (n 5000), test stream 10 (n 5000);
  * same likelihood code: gmm_em_gpu._loglik_t (device cpu, complex128);
  * same M-step for the full family: S_k = sum_i g_ik x_i x_i^H / n_k, cov_k = (S_k + S_k^H)/2 + 1e-4 cbar I, kappa = 0;
  * NO reseeding (a starved component, n_k < 32, keeps its covariance and gets n_k = max(n_k, 1) -- the registered loop would
    replace it by a fresh random seed, which is what makes its train ll non-monotone).
It is a diagnostic of the stored model only: nothing is written but this script's stdout; no fit file, raw or record is touched;
no GPU.  It does NOT produce a replacement b* and no BLER.

usage (cwd = ~/t2/conf):  CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 taskset -c 0-15 \
    ~/miniforge3/envs/torch/bin/python -B results/review_next/prereg_audit_2026-10-11/recompute_dmi_emcont.py [max_iter=25] [max_minutes=22]
"""
import os
import sys
import time

CONF = "/home/HTJ/t2/conf"
sys.path.insert(0, os.path.join(CONF, "code"))
import numpy as np  # noqa: E402
import torch  # noqa: E402

import common as C  # noqa: E402,F401
import runner  # noqa: E402
from gmm_em_gpu import _loglik_t  # noqa: E402

FLOOR, NMIN = 1e-4, 32


def main():
    max_iter = int(sys.argv[1]) if len(sys.argv) > 1 else 25
    max_min = float(sys.argv[2]) if len(sys.argv) > 2 else 22.0
    runner._init("DMIB16e4")
    torch.set_num_threads(int(os.environ.get("OMP_NUM_THREADS", "8")))
    t00 = time.time()
    gen, (X, Xv, Xt) = runner._sets("DMI", 8, 4, 160000)
    z = np.load(os.path.join(CONF, "results/gmm_fits_D2_DMIB16e4/fit_DMI_Nr8_fullK1024_n160000.npz"), allow_pickle=True)
    n, N = X.shape; K = len(z["pi"])
    Xt_ = torch.as_tensor(np.asarray(X, np.complex128)); Xv_ = torch.as_tensor(np.asarray(Xv, np.complex128)); Xs_ = torch.as_tensor(np.asarray(Xt, np.complex128))
    covs = torch.as_tensor(z["covs"].copy()); pi = z["pi"].copy()
    Chat = torch.as_tensor(z["Chat"]); cbar = torch.trace(Chat).real.item() / N
    I = torch.eye(N, dtype=torch.complex128)
    print(f"# recompute_dmi_emcont.py -- plain EM continuation of the stored b* (full K = {K}); n = {n}, N = {N}, threads {torch.get_num_threads()}; data loaded in {time.time() - t00:.0f} s", flush=True)
    print(f"# stored: it_best {int(z['it_best'])}, ll_train {float(z['ll_train']):.6f}, ll_val {float(z['ll_val']):.6f}, ll_test {float(z['ll_test']):.6f}; Chat equals X^T X^* / n: "
          f"{bool(torch.allclose(Chat, Xt_.mT @ Xt_.conj() / n, atol=1e-12))}", flush=True)
    print("#  it   ll_train      ll_val       ll_test     d_train     d_val(vs stored)  starved(n_k<32)  sec", flush=True)
    logpi = torch.as_tensor(np.log(pi))
    hist = []
    for it in range(max_iter + 1):
        t0 = time.time()
        lw = _loglik_t(Xt_, logpi, covs, N)
        lse = torch.logsumexp(lw, 1)
        ll_tr = float(lse.mean())
        ll_v = float(torch.logsumexp(_loglik_t(Xv_, logpi, covs, N), 1).mean())
        ll_te = float(torch.logsumexp(_loglik_t(Xs_, logpi, covs, N), 1).mean())
        gam = lw.sub_(lse[:, None]).exp_()
        nk = gam.sum(0).numpy().copy()
        starved = nk < NMIN
        hist.append((it, ll_tr, ll_v, ll_te))
        print(f"  {it:3d}  {ll_tr:.6f}  {ll_v:.6f}  {ll_te:.6f}  {ll_tr - hist[max(it - 1, 0)][1]:+.2e}  {ll_v - float(z['ll_val']):+.6f}        {int(starved.sum()):4d}          {time.time() - t0:.0f}", flush=True)
        if it == 0:
            print(f"#   check at it 0: |ll_train - stored| = {abs(ll_tr - float(z['ll_train'])):.2e}, |ll_val - stored| = {abs(ll_v - float(z['ll_val'])):.2e}, |ll_test - stored| = {abs(ll_te - float(z['ll_test'])):.2e}", flush=True)
        if it == max_iter or (time.time() - t00) / 60 > max_min:
            break
        # M-step (full family, kappa 0), all K at once through the weighted scatter matrices
        Sre = torch.zeros((K, N * N), dtype=torch.float64); Sim = torch.zeros_like(Sre)
        for a in range(0, n, 16384):
            x = Xt_[a:a + 16384]
            XX = (x[:, :, None] * x.conj()[:, None, :]).reshape(x.shape[0], N * N)
            gT = gam[a:a + 16384].mT
            Sre += gT @ XX.real
            Sim += gT @ XX.imag
        S = torch.complex(Sre, Sim).reshape(K, N, N) / torch.as_tensor(np.maximum(nk, 1.0))[:, None, None]
        new = 0.5 * (S + S.mH) + FLOOR * cbar * I
        ok = torch.as_tensor(~starved)
        covs[ok] = new[ok]
        nk2 = np.where(starved, np.maximum(nk, 1.0), nk)
        logpi = torch.as_tensor(np.log(nk2 / nk2.sum()))
        del lw, gam, Sre, Sim, S, new
    h = np.array(hist)
    print(f"\n# SUMMARY after {int(h[-1, 0])} further EM iterations: ll_train {h[0, 1]:.4f} -> {h[-1, 1]:.4f} ({h[-1, 1] - h[0, 1]:+.4f}); ll_val {h[0, 2]:.4f} -> {h[-1, 2]:.4f} ({h[-1, 2] - h[0, 2]:+.4f}), "
          f"max ll_val {h[:, 2].max():.4f} at it +{int(h[np.argmax(h[:, 2]), 0])} ({h[:, 2].max() - h[0, 2]:+.4f}); ll_test {h[0, 3]:.4f} -> {h[-1, 3]:.4f} ({h[-1, 3] - h[0, 3]:+.4f}); "
          f"last train step {h[-1, 1] - h[-2, 1]:+.2e} (tolerance 1e-6 |ll| = {1e-6 * abs(h[-1, 1]):.2e}); wall {(time.time() - t00) / 60:.1f} min")
    print("# for scale: the validation-likelihood gain of the registered grid step full 512 -> full 1024 is +6.192 nat; the three kappa-0 restarts of full 1024 differ by 0.139 nat")


if __name__ == "__main__":
    main()
