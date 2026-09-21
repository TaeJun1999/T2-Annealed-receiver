"""verify_gpu_port.py -- INDEPENDENT verification of code/gmm_em_gpu.py.

Written by a second engineer to check the port, not by its author.  Three things, none of which
reuses code/gmm_gpu_equiv.py's own comparison:

  dtypes  <npz...>          runtime dtype evidence: every array in a saved fit, and an aten-level
                            TorchDispatchMode trace of EVERY tensor the port materialises (both
                            structs).  A float32/complex64 anywhere shows up here.
  equiv   <Nr> <fam> <K> <kappa> <restart> <ntrain> <device>
                            one real task tuple driven exactly as runner.fit_task drives it, EM from
                            gmm_em_gpu on <device>, written to <out>; compare with `diff`.
  ref     <Nr> <fam> <K> <kappa> <restart> <ntrain>
                            the same tuple through the READ-ONLY Demo/t2_gmm.fit_gmm_em.
  diff    <a.npz> <b.npz>   path identity (exact) + numeric agreement, computed here.

Read-only w.r.t. Demo/, results/ and the running CPU fit.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C                                    # FIRST: pins OMP/OPENBLAS/MKL to 1
import numpy as np
from runner import _sets, FAM


def _task_rng(Nr, fam, K, kappa, restart):
    return np.random.default_rng([C.SEED, C.TBID["D2"], 9, C.PID[C.PRIOR_OF["D2"]], Nr,
                                  FAM[fam], K, kappa, restart])


def _save(out, f, sec, tag):
    np.savez_compressed(out, pi=f["pi"], covs=f["covs"], Chat=f["Chat"], ll=f["ll"],
                        ll_val_traj=f["ll_val_traj"], it_best=f["it_best"], n_iter=f["n_iter"],
                        n_reseed=f["n_reseed"], ll_train=f["ll_train"], ll_val=f["ll_val"],
                        ll_test=f["ll_test"], sec=sec, who=tag)
    print(f"[{tag}] iters {f['n_iter']} best@{f['it_best']} reseeds {f['n_reseed']} "
          f"ll_train {f['ll_train']:.6f} ll_val {f['ll_val']:.6f} ll_test {f['ll_test']:.6f} "
          f"({sec:.1f} s) -> {out}", flush=True)


def _run(Nr, fam, K, kappa, restart, ntrain, out, tag, device=None):
    prior, Nt = C.PRIOR_OF["D2"], C.NT
    gen, (X, Xv, Xt) = _sets(prior, Nr, Nt, ntrain)
    rng = _task_rng(Nr, fam, K, kappa, restart)
    kw = dict(n_iter=500, kappa=float(kappa), struct=fam, dims=(Nr, Nt), Xval=Xv)
    t0 = time.time()
    if device is None:
        from t2_gmm import fit_gmm_em
        f = fit_gmm_em(X, K, rng, **kw)
    else:
        from gmm_em_gpu import fit_gmm_em_gpu
        f = fit_gmm_em_gpu(X, K, rng, device=device, **kw)
    sec = time.time() - t0
    f["ll_test"] = float(C.GMMPriorB(Nr, Nt, f["covs"], f["pi"]).log_pdf(Xt).mean())
    f["ll_train"] = float(f["ll"][f["it_best"]])
    _save(out, f, sec, tag)


def diff(pa, pb):
    a, b = np.load(pa, allow_pickle=True), np.load(pb, allow_pickle=True)
    print(f"A {pa}\nB {pb}")
    ok = True
    for k in ("n_iter", "it_best", "n_reseed"):
        x, y = int(a[k]), int(b[k])
        same = x == y
        ok &= same
        print(f"  {k:<10} {x:>8} {y:>8}   {'MATCH' if same else '*** DIFFER ***'}")
    for k in ("ll_train", "ll_val", "ll_test"):
        x, y = float(a[k]), float(b[k])
        print(f"  {k:<10} {x:>22.15f} {y:>22.15f}   rel {abs(x - y) / abs(x):.3e}")
    for k in ("pi", "covs", "Chat"):
        u, v = np.asarray(a[k]), np.asarray(b[k])
        if u.shape != v.shape:
            print(f"  {k:<10} SHAPE {u.shape} vs {v.shape}  *** DIFFER ***"); ok = False; continue
        d = np.abs(u - v)
        print(f"  {k:<10} max|dA|/max|A| = {d.max() / np.abs(u).max():.3e}   "
              f"max elementwise rel = {(d / np.maximum(np.abs(u), 1e-300)).max():.3e}   "
              f"dtype {u.dtype}/{v.dtype}")
    la, lb = np.asarray(a["ll"]), np.asarray(b["ll"])
    n = min(len(la), len(lb))
    r = np.abs(la[:n] - lb[:n]) / np.abs(la[:n])
    print(f"  ll traj    len {len(la)}/{len(lb)}   max rel over prefix {r.max():.3e} at it {int(r.argmax())}")
    print(f"  ll traj    it0 rel {r[0]:.3e}   it{n-1} rel {r[-1]:.3e}   max {r.max():.3e}  "
          f"(no amplification if max stays at round-off scale)")
    va, vb = np.asarray(a["ll_val_traj"]), np.asarray(b["ll_val_traj"])
    print(f"  val traj   shape {va.shape}/{vb.shape}   its equal: {np.array_equal(va[:,0], vb[:,0])}   "
          f"max rel {np.abs((va[:,1]-vb[:,1])/va[:,1]).max():.3e}")
    print(f"  sec        {float(a['sec']):.1f} / {float(b['sec']):.1f}  -> {float(a['sec'])/max(float(b['sec']),1e-9):.1f}x")
    print("  PATH IDENTITY:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def dtypes(paths):
    for p in paths:
        z = np.load(p, allow_pickle=True)
        print(p)
        for k in sorted(z.files):
            print(f"   {k:<14} {str(np.asarray(z[k]).dtype):<12} {np.asarray(z[k]).shape}")
    import torch
    from torch.utils._python_dispatch import TorchDispatchMode
    from torch.utils._pytree import tree_flatten
    from gmm_em_gpu import fit_gmm_em_gpu

    class Spy(TorchDispatchMode):
        def __init__(self):
            self.seen = {}
        def __torch_dispatch__(self, func, types, args=(), kwargs=None):
            out = func(*args, **(kwargs or {}))
            for t in tree_flatten((args, kwargs, out))[0]:
                if isinstance(t, torch.Tensor):
                    key = str(t.dtype)
                    self.seen[key] = self.seen.get(key, 0) + 1
            return out

    rs = np.random.default_rng(0)
    Nr, Nt = 4, 2; N = Nr * Nt; n = 1500
    C0 = [a @ a.conj().T + np.eye(N) for a in
          (rs.standard_normal((N, 2)) + 1j * rs.standard_normal((N, 2)) for _ in range(3))]
    ks = rs.integers(3, size=n)
    X = np.stack([np.linalg.cholesky(C0[k]) @ (rs.standard_normal(N) + 1j * rs.standard_normal(N)) / np.sqrt(2)
                  for k in ks])
    for struct in ("full", "kron"):
        spy = Spy()
        with spy:
            fit_gmm_em_gpu(X, 4, np.random.default_rng(7), n_iter=40, kappa=8.0, struct=struct,
                           dims=(Nr, Nt), Xval=X[:300], device="cpu")
        print(f"\naten-level tensor dtypes seen, struct={struct} (device=cpu; dtypes are device-independent):")
        for k, v in sorted(spy.seen.items(), key=lambda x: -x[1]):
            print(f"   {k:<24} {v:>8} tensor occurrences")
        bad = [k for k in spy.seen if k in ("torch.float32", "torch.complex64", "torch.float16",
                                            "torch.bfloat16", "torch.complex32")]
        print("   REDUCED PRECISION FOUND:", bad if bad else "none")


def reseed():
    """The one branch NOTHING covers: the kron starved-component re-seed (nk < 4).  No kron run in the
    172 completed CPU tasks of logs/fit_D2_n16e4.log has n_reseed > 0, and the real K<=512 fits have
    nk ~ n/K >> 4, so neither the CPU log nor the author's 6 configs exercise it.  Force it with K
    large relative to n and check the port takes the identical path (it also sets Tk[k] = I and
    installs a FULL, non-Kronecker seed_cov, which is the part most likely to be ported wrong)."""
    from t2_gmm import fit_gmm_em
    from gmm_em_gpu import fit_gmm_em_gpu
    rs = np.random.default_rng(3)
    Nr, Nt = 4, 2; N = Nr * Nt
    for n, K in ((400, 64), (900, 96)):
        C0 = [a @ a.conj().T + 0.2 * np.eye(N) for a in
              (rs.standard_normal((N, 2)) + 1j * rs.standard_normal((N, 2)) for _ in range(5))]
        ks = rs.integers(5, size=n)
        X = np.stack([np.linalg.cholesky(C0[k]) @ (rs.standard_normal(N) + 1j * rs.standard_normal(N)) / np.sqrt(2)
                      for k in ks])
        Xv = X[:200]
        for fam in ("kron", "full"):
            kw = dict(n_iter=120, kappa=0.0, struct=fam, dims=(Nr, Nt), Xval=Xv)
            a = fit_gmm_em(X, K, np.random.default_rng(11), **kw)
            b = fit_gmm_em_gpu(X, K, np.random.default_rng(11), device="cpu", **kw)
            dv = abs(a["ll_val"] - b["ll_val"]) / abs(a["ll_val"])
            dp = np.abs(a["pi"] - b["pi"]).max() / np.abs(a["pi"]).max()
            dc = np.abs(a["covs"] - b["covs"]).max() / np.abs(a["covs"]).max()
            same = (a["n_iter"] == b["n_iter"] and a["it_best"] == b["it_best"]
                    and a["n_reseed"] == b["n_reseed"])
            print(f"  n={n:<4} K={K:<3} {fam:<4}  n_iter {a['n_iter']}/{b['n_iter']}  "
                  f"it_best {a['it_best']}/{b['it_best']}  RESEEDS {a['n_reseed']}/{b['n_reseed']}  "
                  f"d_ll_val {dv:.2e}  d_pi {dp:.2e}  d_cov {dc:.2e}   "
                  f"{'PATH MATCH' if same else '*** PATH DIFFER ***'}")
            assert same and dv < 1e-12 and dp < 1e-10 and dc < 1e-10, (dv, dp, dc)
            assert a["n_reseed"] > 0, f"{fam}: re-seed branch NOT exercised -- test is vacuous"
    print("  kron + full re-seed branches: identical path, params within tolerance")


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "reseed":
        reseed()
    elif c == "dtypes":
        dtypes(sys.argv[2:])
    elif c == "diff":
        sys.exit(diff(sys.argv[2], sys.argv[3]))
    elif c == "ref":
        _, _, Nr, fam, K, kap, r, nt, out = sys.argv
        _run(int(Nr), fam, int(K), int(kap), int(r), int(nt), out, "cpu-numpy", None)
    elif c == "equiv":
        _, _, Nr, fam, K, kap, r, nt, dev, out = sys.argv
        _run(int(Nr), fam, int(K), int(kap), int(r), int(nt), out, f"port-{dev}", dev)
    else:
        sys.exit(__doc__)
