# conf/code/pilot_position_check.py -- is the receiver invariant to the order of the T columns (pilot position)?
# Block fading (one H per block): permuting data / pilot columns (compensated in perm / Xp) must leave every arm's
# trajectory unchanged up to floating-point summation order.  Read-only; output -> results/review_next/pilot_position_check.txt
import sys, numpy as np
sys.path.insert(0, "/home/HTJ/t2/conf/code")
import common as C
from arms import route_a
from bigamp import R3BiGAMP
from scvamp import R4SCVAMP
from d2 import D2Gen, ensemble_sides_d2

Nr, Nt, T, Tp, snr = 8, 4, 16, 4, 0          # cell C2 geometry
Td, sigma2 = T - Tp, 10 ** (-snr / 10)
code = C.QAMCode(C.GENS, C.NU, C.M_QAM, Nt * Td)
_, Xp = C.make_pilots("D2", "S2", Nt, Tp, Nr)
Rt, Rr, _ = ensemble_sides_d2("S2", Nr, Nt)
Cs = C.GaussianPrior(Nr, Nt, np.kron(Rt.T, Rr))   # analytic ensemble cov (no fits needed)
gen = D2Gen("S2", Nr, Nt)
rng = np.random.default_rng(12345)
sp = np.random.default_rng(7)

def arms(Xp_):
    return {"RouteA-G": route_a(Nr, Nt, T, Tp, sigma2, Cs, code, Xp_, "gaussian"),
            "R3-bigamp": R3BiGAMP(Nr, Nt, T, Tp, sigma2, code, Xp_, beta=C.BETA, t_in=C.T_IN),
            "R4-scvamp": R4SCVAMP(Nr, Nt, T, Tp, sigma2, Cs, code, Xp_, mode="onsager")}

A0 = arms(Xp)
worst = {k: 0.0 for k in A0}; blk_same = {k: 0 for k in A0}; ntr = 30
gdiff = 0.0
for tr in range(ntr):
    H = gen.sample(rng); u = rng.integers(0, 2, code.K); perm = rng.permutation(code.Ns)
    X, Y = A0["RouteA-G"].transmit(u, perm, H, rng)
    # (a) data-column permutation sd and pilot-column permutation sp_, compensated in perm / Xp
    sd = sp.permutation(Td); spp = sp.permutation(Tp)
    Y2 = np.empty_like(Y); Y2[:, :Tp] = Y[:, spp]; Y2[:, Tp + sd] = Y[:, Tp:]
    perm2 = sd[perm // Nt] * Nt + perm % Nt
    A1 = arms(Xp[:, spp])
    for k in A0:
        o0 = A0[k].run(Y, H, u, perm, C.N_ITER); o1 = A1[k].run(Y2, H, u, perm2, C.N_ITER)
        worst[k] = max(worst[k], float(np.nanmax(np.abs(o0["nmse"] - o1["nmse"]))))
        blk_same[k] += int(np.array_equal(o0["blk_err"], o1["blk_err"]))
    # (b) SPREAD layout, pilots at t = 0,4,8,12 in natural time order: channel-side sums without any reordering
    P = np.arange(0, T, T // Tp); D = np.setdiff1d(np.arange(T), P); pos = np.r_[P, D]
    Ys = np.empty_like(Y); Ys[:, pos] = Y
    rx = A0["RouteA-G"]
    Xbar = np.hstack([Xp, X[:, Tp:]]); Tau = np.hstack([np.zeros((Nt, Tp)), 0.3 * np.ones((Nt, Td))])
    Xs = np.empty_like(Xbar); Xs[:, pos] = Xbar; Ts = np.empty_like(Tau); Ts[:, pos] = Tau
    _, Af, Bf = rx._sites(Y, Xbar, Tau, Cs.eh2_prior); _, As, Bs = rx._sites(Ys, Xs, Ts, Cs.eh2_prior)
    gdiff = max(gdiff, np.abs(Af.sum(0) - As.sum(0)).max() / np.abs(Af.sum(0)).max(),
                np.abs(Bf.sum(0) - Bs.sum(0)).max() / np.abs(Bf.sum(0)).max(),
                float(np.abs(As[pos] - Af).max()))
for k in A0:
    print(f"{k:10s}: max|nmse diff| over {ntr} trials x {C.N_ITER} iters = {worst[k]:.2e}; blk_err trajectories identical in {blk_same[k]}/{ntr}")
print(f"spread layout (pilots at {P.tolist()}): channel-side G,b relative diff vs front = {gdiff:.2e}")
