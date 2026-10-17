"""test_gcap_em.py -- checks of the U28NR32GCAP opt-ins in code/gmm_em_gpu.py (init, stop_rule, kron_tk).

  CUDA_VISIBLE_DEVICES=k python test_gcap_em.py <old_gmm_em_gpu.py>   (old = `git show <commit>:conf/code/gmm_em_gpu.py`)

T1  default path (no init, stop_rule legacy) is BIT-identical to the old module: full, kron, kron batched.
T2  continuation = the straight run: gcap fit with n_iter 2m+1 vs (n_iter m+1 -> out["final"] -> init, the SAME rng
    object, n_iter m+1): train ll of states m..2m and the last state bit-identical (Tk handed over exactly).
T3  kron_tk(final covs) recovers final Tk (reseeded components -> I) to round-off, and a continuation started from
    kron_tk instead of the exact Tk tracks the straight run to round-off.
T4  init does not consume the rng (the reseed stream starts where the caller left it)."""
import importlib.util, os, sys
sys.path.insert(0, os.path.expanduser("~/t2/conf/code"))
import numpy as np
import gmm_em_gpu as new

spec = importlib.util.spec_from_file_location("gmm_old", sys.argv[1]); old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)

rs = np.random.default_rng(0)
Nr, Nt = 4, 2; N = Nr * Nt; n = 3000
C0 = [a @ a.conj().T + np.eye(N) for a in (rs.standard_normal((N, 2)) + 1j * rs.standard_normal((N, 2)) for _ in range(3))]
ks = rs.integers(3, size=n)
X = np.stack([np.linalg.cholesky(C0[k]) @ (rs.standard_normal(N) + 1j * rs.standard_normal(N)) / np.sqrt(2) for k in ks])
Xv = X[:500]
K = 24                                   # large enough that components starve and get reseeded (exercises Tk = I)

for struct, batched in (("full", False), ("kron", False), ("kron", True)):
    kw = dict(n_iter=60, kappa=8.0, struct=struct, dims=(Nr, Nt), Xval=Xv, batched=batched)
    a = old.fit_gmm_em_gpu(X, K, np.random.default_rng(7), **kw)
    b = new.fit_gmm_em_gpu(X, K, np.random.default_rng(7), **kw)
    same = all(np.array_equal(a[k], b[k], equal_nan=True) for k in a) and set(b) - set(a) <= {"stop", "stop_rule"}
    print(f"T1 {struct}{' batched' if batched else ''}: n_iter {b['n_iter']} reseeds {b['n_reseed']} stop {b['stop']} "
          f"bit-identical {same}")
    assert same

m = 10
K = 300                                  # T2-T4: about 10 samples per component, so kron components starve and reseed
for batched in (False, True):
    kw = dict(kappa=0.0, struct="kron", dims=(Nr, Nt), Xval=Xv, batched=batched, stop_rule="gcap", tol=None, patience=None)
    s = new.fit_gmm_em_gpu(X, K, np.random.default_rng(11), n_iter=2 * m + 1, **kw)
    r = np.random.default_rng(11)
    h = new.fit_gmm_em_gpu(X, K, r, n_iter=m + 1, **kw)
    c = new.fit_gmm_em_gpu(X, K, r, n_iter=m + 1, init=h["final"], **kw)
    dll2 = np.abs(s["ll"][m:] - c["ll"]).max()           # init takes pi, so log(exp(logpi)) costs round-off only
    dcv2 = np.abs(s["final"]["covs"] - c["final"]["covs"]).max() / np.abs(s["final"]["covs"]).max()
    ok2 = (dll2 < 1e-9 and dcv2 < 1e-9 and s["n_reseed"] == h["n_reseed"] + c["n_reseed"] > 0
           and s["stop"] == c["stop"] == "budget" and len(s["ll"]) == 2 * m + 1 and len(c["ll"]) == m + 1)
    print(f"T2 batched={batched}: straight {len(s['ll'])} states, reseeds {s['n_reseed']} = {h['n_reseed']} + "
          f"{c['n_reseed']}; max |d ll| {dll2:.2e}, max rel |d cov| {dcv2:.2e}; ok {ok2}; val traj straight {np.round(s['ll_val_traj'][:, 1], 6).tolist()} "
          f"cont {np.round(c['ll_val_traj'][:, 1], 6).tolist()}")
    assert ok2
    Tr = new.kron_tk(h["final"]["covs"], Nr, Nt)
    dT = np.abs(Tr - h["final"]["Tk"]).max()
    n_eye = int(sum(np.array_equal(t, np.eye(Nt)) for t in h["final"]["Tk"]))
    r2 = np.random.default_rng(11); new.fit_gmm_em_gpu(X, K, r2, n_iter=m + 1, **kw)
    c2 = new.fit_gmm_em_gpu(X, K, r2, n_iter=m + 1, init=dict(pi=h["final"]["pi"], covs=h["final"]["covs"]), **kw)
    dl = np.abs(c2["ll"] - c["ll"]).max()
    print(f"T3 batched={batched}: max |kron_tk - Tk| {dT:.2e} (Tk = I in {n_eye} components); "
          f"continuation from kron_tk: max |d ll| {dl:.2e}")
    assert dT < 1e-10 and dl < 1e-8

r = np.random.default_rng(5); r.integers(10); st = r.bit_generator.state
new.fit_gmm_em_gpu(X, K, r, n_iter=1, init=h["final"], struct="kron", dims=(Nr, Nt), stop_rule="gcap")
print(f"T4 init consumes no rng draw on a 1-state run: {r.bit_generator.state == st}")
assert r.bit_generator.state == st
print("test_gcap_em OK")
