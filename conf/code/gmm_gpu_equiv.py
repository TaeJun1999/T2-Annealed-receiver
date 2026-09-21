"""gmm_gpu_equiv.py -- run ONE (prior,Nr,Nt,fam,K,kappa,restart) EM task on cpu or gpu, exactly as
runner.fit_task drives it, and dump the full result so CPU and GPU fits can be compared parameter
by parameter.  Read-only w.r.t. Demo/ and results/.

  python code/gmm_gpu_equiv.py run  <dev> <Nr> <fam> <K> <kappa> <restart> <ntrain> <out.npz>
  python code/gmm_gpu_equiv.py cmp  <a.npz> <b.npz>
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C                                    # FIRST: pins OMP/OPENBLAS/MKL threads to 1
import numpy as np
from runner import _sets, FAM, N_VAL


def run(dev, Nr, fam, K, kappa, restart, ntrain, out):
    prior, Nt, iters = C.PRIOR_OF["D2"], C.NT, 500
    t_data = time.time()
    gen, (X, Xv, Xt) = _sets(prior, Nr, Nt, ntrain)
    t_data = time.time() - t_data
    rng = np.random.default_rng([C.SEED, C.TBID["D2"], 9, C.PID[prior], Nr, FAM[fam], K, kappa, restart])
    t0 = time.time()
    if dev == "cpu":
        from t2_gmm import fit_gmm_em
        f = fit_gmm_em(X, K, rng, n_iter=iters, kappa=float(kappa), struct=fam, dims=(Nr, Nt), Xval=Xv)
    else:
        from gmm_em_gpu import fit_gmm_em_gpu
        f = fit_gmm_em_gpu(X, K, rng, n_iter=iters, kappa=float(kappa), struct=fam, dims=(Nr, Nt), Xval=Xv)
    sec = time.time() - t0
    f["ll_test"] = float(C.GMMPriorB(Nr, Nt, f["covs"], f["pi"]).log_pdf(Xt).mean())
    f["ll_train"] = float(f["ll"][f["it_best"]])
    f["sec"] = sec
    np.savez_compressed(out, pi=f["pi"], covs=f["covs"], Chat=f["Chat"], ll=f["ll"],
                        ll_val_traj=f["ll_val_traj"], it_best=f["it_best"], n_iter=f["n_iter"],
                        n_reseed=f["n_reseed"], ll_train=f["ll_train"], ll_val=f["ll_val"],
                        ll_test=f["ll_test"], sec=sec, sec_data=t_data,
                        task=np.array([prior, Nr, Nt, fam, K, kappa, restart, ntrain], object))
    print(f"[{dev}] Nr={Nr} {fam} K={K} kappa={kappa} r={restart}: iters {f['n_iter']} "
          f"best@{f['it_best']} reseeds {f['n_reseed']} ll_train {f['ll_train']:.3f} "
          f"ll_val {f['ll_val']:.3f} ll_test {f['ll_test']:.3f} ({sec:.0f} s, data {t_data:.0f} s)",
          flush=True)


def _rel(a, b):
    d = np.abs(a - b); s = np.abs(a)
    return float(d.max() / max(s.max(), 1e-300)), float((d / np.maximum(s, 1e-300)).max())


def cmp(pa, pb):
    a, b = np.load(pa, allow_pickle=True), np.load(pb, allow_pickle=True)
    print(f"A {pa}\nB {pb}")
    for k in ("n_iter", "it_best", "n_reseed"):
        print(f"  {k:<10} {int(a[k]):>6} {int(b[k]):>6}   {'MATCH' if int(a[k]) == int(b[k]) else 'DIFFER'}")
    for k in ("ll_train", "ll_val", "ll_test"):
        x, y = float(a[k]), float(b[k])
        print(f"  {k:<10} {x:>20.12f} {y:>20.12f}   rel {abs(x - y) / max(abs(x), 1e-300):.3e}")
    for k in ("pi", "covs", "Chat"):
        m, e = _rel(a[k], b[k])
        print(f"  {k:<10} max|dA| / max|A| = {m:.3e}    max elementwise rel = {e:.3e}")
    na, nb = len(a["ll"]), len(b["ll"])
    n = min(na, nb)
    d = np.abs(a["ll"][:n] - b["ll"][:n]) / np.abs(a["ll"][:n])
    print(f"  ll traj    len {na}/{nb}  max rel over common prefix {d.max():.3e}  (at it {int(d.argmax())})")
    print(f"  sec        {float(a['sec']):.1f} / {float(b['sec']):.1f}  -> speedup "
          f"{float(a['sec']) / max(float(b['sec']), 1e-9):.1f}x")


if __name__ == "__main__":
    if sys.argv[1] == "run":
        _, _, dev, Nr, fam, K, kap, r, nt, out = sys.argv
        run(dev, int(Nr), fam, int(K), int(kap), int(r), int(nt), out)
    else:
        cmp(sys.argv[2], sys.argv[3])
