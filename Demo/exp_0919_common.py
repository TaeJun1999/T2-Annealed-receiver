"""exp_0919 common harness (QPSK route (a), Gaussian Kronecker prior). Seed base 20260919.
Trials are generated exactly as in exp_0918 (H, u, perm, then transmit noise, all from one rng per (Tp, SNR) point),
so every receiver variant at a point sees the same (H, u, perm, Y)."""
import sys, json, numpy as np
sys.path.insert(0, ".")
from t2_route_a import KronGaussianPrior, BPSKCode, QAMCode, RouteA
GENS, NU, SEED = ("133", "171"), 6, 20260919

def make_code(mod, Ns):
    return BPSKCode(GENS, NU, Ns) if mod == "bpsk" else QAMCode(GENS, NU, {"qpsk": 2, "16qam": 4}[mod], Ns)

def run_trials(Tp, snr_db, modes, n_trials, n_iter, seed, Nr=4, Nt=4, T=28, rho=0.7, mod="qpsk", skip=0):
    """modes: {name: RouteA kwargs}. skip: number of leading trials to generate but not run (for chunked execution)."""
    prior = KronGaussianPrior(Nr, Nt, rho); code = make_code(mod, Nt * (T - Tp)); sigma2 = 10 ** (-snr_db / 10)
    rxs = {n: RouteA(Nr, Nt, T, Tp, sigma2, prior, code, **c) for n, c in modes.items()}
    logs = {n: [] for n in modes}; rng = np.random.default_rng(seed)
    first = rxs[next(iter(modes))]
    for tr in range(n_trials):
        H = prior.sample(rng); u = rng.integers(0, 2, code.K); perm = rng.permutation(code.Ns)
        X, Y = first.transmit(u, perm, H, rng)
        if tr < skip: continue
        for n, rx in rxs.items(): logs[n].append(rx.run(Y, H, u, perm, n_iter))
    return {n: {k: np.array([l[k] for l in L]) for k in L[0]} for n, L in logs.items()}

def fmt(v, f="{:.3g}"): return " ".join(f.format(x) for x in v)

def m1_report(a):
    """Measurement convention M-1: BLER trajectory, NMSE median, decode-success-conditional NMSE (last iter), rescued/lost blocks (t=2 -> last)."""
    be = a["blk_err"]; nm = a["nmse"]; ok = be[:, -1] == 0
    return dict(bler=be.mean(0), nmse_med=np.median(nm, 0), nmse_ok=(np.median(nm[ok, -1]) if ok.any() else np.nan), n_ok=int(ok.sum()),
                rescued=int(np.sum((be[:, 1] == 1) & (be[:, -1] == 0))), lost=int(np.sum((be[:, 1] == 0) & (be[:, -1] == 1))))
