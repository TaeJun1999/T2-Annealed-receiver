"""conf/code/sparse_tune.py -- development tuning of the sparse baselines (NEXT_EXPERIMENTS_SPARSE16e4 §1): pilot-only channel-
estimate NMSE of SBL (arms.SparsePrior, rho x n_em) and OMP (arms.OMPSitePrior, rho x L) on channels drawn from a DEDICATED
stream (default_rng([20260930, TBID, PID, Nr, SNR]) -- never the test trials 0..2559 nor the development trials of any registered
tag), with the receiver's own pilot site (G, b) = sum over pilot columns of (x x^H)^* kron I / sigma2, x^* kron y / sigma2
(RouteA._sites with Tau = 0 on pilots).  The estimate is the pilot-only posterior mean hpost = (Lam + G)^-1 (eta + b), i.e. what
RouteA mode='pilot_only' freezes.  BLER is NOT computed here.  Rule (fixed before running, §1): per dataset pick the (rho, n_em)
and (rho, L) with the lowest NMSE averaged in dB over the cell's SNR grid; ties -> smaller rho, then smaller n_em / L.
    python code/sparse_tune.py --prior S2 --cell C2 [--n 256] [--out results/sparse/tune_<prior>_<cell>.json]
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import common as C
import arms as A

RHOS, NEMS, LS = (1, 2, 4, 8), (10, 25, 50, 100, 200), (1, 2, 3, 4, 6, 8, 12, 16, 24)   # extended once after the stage smoke hit rho 4 / n_em 100


def sites(H, Xp, sigma2, rng):
    Nr, Tp = H.shape[0], Xp.shape[1]
    W = np.sqrt(sigma2 / 2) * (rng.standard_normal((Nr, Tp)) + 1j * rng.standard_normal((Nr, Tp)))
    Y = H @ Xp + W; I = np.eye(Nr)
    G = sum(np.kron(np.outer(Xp[:, n].conj(), Xp[:, n]), I) for n in range(Tp)) / sigma2
    b = sum(np.kron(Xp[:, n].conj(), Y[:, n]) for n in range(Tp)) / sigma2
    return G, b


def post(prior, G, b):
    Lam, eta = prior.ep_site(G, b, 0.0)
    return np.linalg.solve(Lam + G, eta + b)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prior", required=True); ap.add_argument("--cell", required=True)
    ap.add_argument("--n", type=int, default=256); ap.add_argument("--out", default=None)
    a = ap.parse_args()
    cell = C.CELLS[a.cell]; Nr, Nt, Tp = cell["Nr"], cell["Nt"], cell["Tp"]
    gen = C.make_gen("D2", a.prior, Nr, Nt); _, Xp = C.make_pilots("D2", a.prior, Nt, Tp, Nr)
    base = C.GaussianPrior(Nr, Nt, np.eye(Nr * Nt))          # only cbar / N are read by the sparse priors (unit-power channels)
    res = {"sbl": {}, "omp": {}}; t0 = time.time()
    for snr in cell["snrs"]:
        rng = np.random.default_rng([20260930, C.TBID["D2"], C.PID[a.prior], Nr, int(snr) + 100])
        Hs = gen.sample_vecs(rng, a.n); sigma2 = 10 ** (-snr / 10)
        S = [sites(h.reshape(Nr, Nt, order="F"), Xp, sigma2, rng) for h in Hs]
        e = lambda pr: 10 * np.log10(np.mean([np.sum(np.abs(post(pr, G, b) - h) ** 2) for (G, b), h in zip(S, Hs)])
                                     / np.mean(np.sum(np.abs(Hs) ** 2, 1)))
        for rho in RHOS:
            for ne in NEMS:
                res["sbl"].setdefault(f"{rho},{ne}", {})[str(snr)] = e(A.SparsePrior(base, Nr, Nt, rho, ne))
            for L in LS:
                res["omp"].setdefault(f"{rho},{L}", {})[str(snr)] = e(A.OMPSitePrior(base, Nr, Nt, rho, L))
        print(f"[sparse_tune] {a.prior} {a.cell} {snr:+d} dB done ({time.time() - t0:.0f} s)", flush=True)
    pick = {}
    for fam in ("sbl", "omp"):
        key = lambda k: (np.mean(list(res[fam][k].values())), *map(int, k.split(",")))
        best = min(res[fam], key=key); vals = list(map(int, best.split(",")))
        grid2 = NEMS if fam == "sbl" else LS
        pick[fam] = dict(zip(("rho", "n_em" if fam == "sbl" else "L"), vals), nmse_db_mean=float(key(best)[0]),
                         grid_edge=[n for n, v, g in (("rho", vals[0], RHOS), ("n_em" if fam == "sbl" else "L", vals[1], grid2)) if v == max(g)])
    out = dict(prior=a.prior, cell=a.cell, n=a.n, seed="default_rng([20260930, TBID, PID, Nr, snr+100])", grid=dict(rho=RHOS,
               n_em=NEMS, L=LS), nmse_db=res, pick=pick, wall_sec=time.time() - t0)
    path = a.out or os.path.join(C.CONF, "results", "sparse", f"tune_{a.prior}_{a.cell}.json")
    os.makedirs(os.path.dirname(path), exist_ok=True); json.dump(out, open(path, "w"), indent=1)
    print(f"[sparse_tune] pick {pick} -> {path}")


if __name__ == "__main__":
    main()
