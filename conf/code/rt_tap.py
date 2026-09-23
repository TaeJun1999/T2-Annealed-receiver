"""conf/code/rt_tap.py -- review_next P3 (NEXT_EXPERIMENTS_P3 §1, §5): the state residual r_t of a RouteA receiver,

    r_t = ||h_post^t - h_post^{t-1}|| / ||h_post^t||      (t = 2..n_iter; r_1 = NaN, there is no h_post^0)

r_t = +inf when it is non-finite or ||h_post^t|| = 0 (§1 "비정상 값").  h_post^t is the receiver's own channel posterior
mean of iteration t, rebuilt from INSTANCE-LEVEL hooks (Demo/ untouched, same idea as diag_p1_cavity.Tap):
  rx._sites            -> b = sum_n B_n                      (the receiver computes b = B.sum(0) the same way)
  rx._matrix_site      -> (P, eta)          score arms  (mode 'scalar', hsite 'matrix': V1 and its P3 variants)
  rx.prior.ep_site     -> (Lam + G, eta)    mixture-EP arms (mode 'colored', exact_prior: b* and its P3 variants)
  h_post^t = inv(P) @ (eta + b)             = RouteA.run's `Sigma = np.linalg.inv(P); hpost = Sigma @ (site_vec + b)`
Each wrapper returns what the original returned, untouched, so the trajectory is unchanged; rx.run is wrapped to add
log["r_t"] (n_iter,).  Any other wiring raises Unsupported (it has no such hook point / no h_post) -- never a silent NaN.
The prior hook needs a per-arm prior object (arms.py gives every b* arm its own .view("eta")); a prior that is already
hooked is refused.

    ~/miniforge3/envs/torch/bin/python conf/code/rt_tap.py        # selftest (development trials, CPU)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C                                  # first: one BLAS thread per process (env set before numpy)
import numpy as np


class Unsupported(ValueError):
    pass


class RtTap:
    def __init__(self, rx):
        self.rx, self.h, self._b = rx, [], None
        if getattr(rx, "mode", None) == "scalar" and rx.hsite == "matrix":
            self._hook(rx, "_matrix_site", self._msite)
        elif getattr(rx, "mode", None) == "colored" and rx.exact_prior:
            if "ep_site" in vars(rx.prior):
                raise Unsupported("prior.ep_site is already hooked (a prior object shared by two arms?)")
            self._hook(rx.prior, "ep_site", self._ep)
        else:
            raise Unsupported(f"{type(rx).__name__} mode={getattr(rx, 'mode', '?')}: no r_t hook for this wiring")
        self._hook(rx, "_sites", self._sites)
        self._hook(rx, "run", self._run)

    @staticmethod
    def _hook(obj, name, wrap):
        f = getattr(obj, name)
        setattr(obj, name, lambda *a: wrap(f, *a))

    def off(self):                  # instance attributes removed -> the class methods are back (selftest only)
        for obj in (self.rx, self.rx.prior):
            for name in ("_matrix_site", "_sites", "run", "ep_site"):
                vars(obj).pop(name, None)

    def _sites(self, f, *a):
        d, A, B = f(*a)
        self._b = B.sum(0)
        return d, A, B

    def _msite(self, f, q, nu, G):
        P, eta = f(q, nu, G)
        self.h.append(np.linalg.inv(P) @ (eta + self._b))
        return P, eta

    def _ep(self, f, G, b, lam_min=0.0):
        Lam, eta = f(G, b, lam_min)
        self.h.append(np.linalg.inv(Lam + G) @ (eta + b))
        return Lam, eta

    def _run(self, f, Y, H, u, perm, n_iter):
        self.h = []
        log = f(Y, H, u, perm, n_iter)
        assert len(self.h) == n_iter, f"r_t tap saw {len(self.h)} channel updates in {n_iter} iterations"
        log["r_t"] = residuals(self.h)
        return log


def residuals(h):
    """[h^1 .. h^n] -> r (n,), r[0] = NaN; +inf where non-finite or ||h^t|| = 0 (NEXT_EXPERIMENTS_P3 §1)."""
    r = np.full(len(h), np.nan)
    with np.errstate(all="ignore"):
        for t in range(1, len(h)):
            nt = np.linalg.norm(h[t])
            v = np.linalg.norm(h[t] - h[t - 1]) / nt if nt > 0 else np.inf
            r[t] = v if np.isfinite(v) else np.inf
    return r


def selftest(n_trials=2, skip=None, iters=32):
    """On development trials (never the P3 judging set): (1) hooked run == unhooked run, every log key bit-identical;
    (2) h_post rebuilt by the tap reproduces the receiver's logged NMSE; (3) the first 16 iterations of a 32-iteration
    run are bit-identical to a 16-iteration run (the offline-rule equivalence, §2); (4) residuals() edge cases."""
    import runner as R
    nan, inf = np.nan, np.inf
    r = residuals([np.ones(2), np.ones(2) * 2, np.zeros(2), np.array([nan, 1.0]), np.ones(2)])
    assert np.isnan(r[0]) and r[1] == 0.5 and r[2] == inf and r[3] == inf and r[4] == inf, r
    skip = C.DEV_SKIP0 if skip is None else skip
    R._init("B16e4k")
    P = R.build_point("D2", "C2", "S2", -3.0, 160000, stagec_ckpt=f"{C.CONF}/ckpt/d2sx_N160000_a1.pt", p3_arms=True)
    names = ("M-ours-dscore-C-V1", "M-ours-bstar", "V1-b05", "bstar-b05", "V1-fb05", "bstar-fb05")
    arms = {k: P["arms"][k] for k in names}
    for k in ("R5-genie", "M-ours-bstar-scalar"):
        try:
            RtTap(P["arms"][k]); raise AssertionError(f"{k} should be Unsupported")
        except Unsupported:
            pass
    taps = {k: RtTap(rx) for k, rx in arms.items()}
    rng = C.trial_rng("D2", "S2", P["Nr"], P["T"], P["Tp"], -3.0)
    worst = 0.0
    for tr in range(skip + n_trials):
        H = P["gen"].sample(rng)
        u = rng.integers(0, 2, P["code"].K)
        perm = rng.permutation(P["code"].Ns)
        X, Y = P["arms"]["R5-genie"].transmit(u, perm, H, rng)
        if tr < skip:
            continue
        h = H.reshape(-1, order="F")
        for k, rx in arms.items():
            lg = rx.run(Y, H, u, perm, iters)
            hp = np.array(taps[k].h)
            nm = np.sum(np.abs(hp - h) ** 2, 1) / np.sum(np.abs(h) ** 2)
            worst = max(worst, float(np.max(np.abs(nm - lg["nmse"]) / lg["nmse"])))
            taps[k].off()
            l0 = rx.run(Y, H, u, perm, iters)
            l16 = rx.run(Y, H, u, perm, 16)
            taps[k] = RtTap(rx)
            assert set(l0) | {"r_t"} == set(lg), k
            for q in l0:
                assert np.array_equal(l0[q], lg[q], equal_nan=True), f"{k}: hooked run differs in {q}"
                assert np.array_equal(l16[q], l0[q][:16], equal_nan=True), f"{k}: 16-iteration run != first 16 of 32 in {q}"
            print(f"  trial {tr} {k:<20} r_16 {lg['r_t'][15]:.3e}  r_32 {lg['r_t'][31]:.3e}", flush=True)
    assert worst <= 1e-12, f"tap h_post does not reproduce the logged NMSE: rel {worst:.2e}"
    print(f"[rt_tap selftest] OK: {n_trials} dev trials x {len(arms)} arms, hooked == unhooked (all keys, bit), "
          f"iterations 1..16 of {iters} == 16-iteration run (bit), max rel |NMSE(h_tap) - logged| = {worst:.1e}")


if __name__ == "__main__":
    os.environ["CUDA_VISIBLE_DEVICES"] = ""          # the receiver path is CPU complex128
    selftest()
