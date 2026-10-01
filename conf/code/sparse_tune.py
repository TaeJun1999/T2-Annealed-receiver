"""conf/code/sparse_tune.py -- development tuning of the sparse baselines (NEXT_EXPERIMENTS_SPARSE16e4 §1): pilot-only channel-
estimate NMSE of SBL (arms.SparsePrior, rho x n_em) and OMP (arms.OMPSitePrior, rho x L) on channels drawn from a DEDICATED
stream (default_rng([20260930, TBID, PID, Nr, SNR]) -- never the test trials 0..2559 nor the development trials of any registered
tag), with the receiver's own pilot site (G, b) = sum over pilot columns of (x x^H)^* kron I / sigma2, x^* kron y / sigma2
(RouteA._sites with Tau = 0 on pilots).  The estimate is the pilot-only posterior mean hpost = (Lam + G)^-1 (eta + b), i.e. what
RouteA mode='pilot_only' freezes.  BLER is NOT computed here.  Rule (v2, SPARSE16e4 §1 / §5): per_snr_pick below -- per family rho
minimising the SNR-mean (dB) of the per-SNR best NMSE, then at that rho the per-SNR n_em (SBL) / L (OMP, L <= N); ties -> smaller.
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

RHOS, NEMS, LS = (1, 2, 4, 8, 16), (1, 2, 3, 5, 10, 25, 50), (1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64)
# v2b (SPARSE16e4 review + edge rule): MacKay SBL, per-SNR n_em / L.  v2a (results/sparse/v2a) picked rho 8 (upper edge) and n_em 5
# (lower edge) -> each edge axis extended one step (rho 16; n_em 1, 2, 3; n_em 100 / 200 were never picked and are dropped).
# L <= N is structural (L = N is least squares on N atoms), so L = N is not an edge; L = 64 added for C6 (N = 64).


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


def per_snr_pick(res, cell, N, rhos=None):
    """SPARSE16e4 §1 rule (v2): per family choose rho minimising the SNR-mean (dB) of the per-SNR best NMSE over the second
    parameter (n_em for SBL, L for OMP; L > N is not allowed); ties -> smaller rho.  Then at that rho, per SNR, the second
    parameter with the lowest NMSE (ties -> smaller).  A per-SNR choice at the largest grid value is flagged (edge)."""
    snrs = [str(x) for x in cell["snrs"]]; out = {}; RH = tuple(sorted(rhos or RHOS))
    for fam, grid, key in (("sbl", NEMS, "n_em"), ("omp", [L for L in LS if L <= N], "L")):
        best = lambda r, s: min(grid, key=lambda g: (res[fam][f"{r},{g}"][s], g))
        score = {r: np.mean([res[fam][f"{r},{best(r, s)}"][s] for s in snrs]) for r in RH}
        r = min(RH, key=lambda r: (score[r], r)); out[f"rho_{fam}"] = r; out[f"score_{fam}_db"] = float(score[r])
        for s in snrs:
            g = best(r, s); e = out.setdefault("per_snr", {}).setdefault(s, {})
            e[key] = g; e[f"nmse_{fam}_db"] = float(res[fam][f"{r},{g}"][s])
            e[f"edge_{fam}"] = (g == max(grid) and not (fam == "omp" and g == N)) or (fam == "sbl" and g == min(grid))
        out[f"edge_rho_{fam}"] = r == max(RH)
    out["rhos"] = list(RH)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prior", required=True); ap.add_argument("--cell", required=True)
    ap.add_argument("--n", type=int, default=256); ap.add_argument("--out", default=None)
    ap.add_argument("--rhos", type=int, nargs="*", default=None, help="evaluate only these rho (the final edge extension: 32); then --merge-with the earlier tune JSON so the pick is made over the union")
    ap.add_argument("--merge-with", default=None, help="earlier tune JSON whose nmse_db is merged before picking")
    a = ap.parse_args()
    cell = C.CELLS[a.cell]; Nr, Nt, Tp = cell["Nr"], cell["Nt"], cell["Tp"]
    gen = C.make_gen("D2", a.prior, Nr, Nt); _, Xp = C.make_pilots("D2", a.prior, Nt, Tp, Nr)
    base = C.GaussianPrior(Nr, Nt, np.eye(Nr * Nt))          # only cbar / N are read by the sparse priors (unit-power channels)
    rhos = tuple(a.rhos) if a.rhos else RHOS
    res = {"sbl": {}, "omp": {}}; t0 = time.time()
    for snr in cell["snrs"]:
        rng = np.random.default_rng([20260930, C.TBID["D2"], C.PID[a.prior], Nr, int(snr) + 100])
        Hs = gen.sample_vecs(rng, a.n); sigma2 = 10 ** (-snr / 10)
        S = [sites(h.reshape(Nr, Nt, order="F"), Xp, sigma2, rng) for h in Hs]
        e = lambda pr: 10 * np.log10(np.mean([np.sum(np.abs(post(pr, G, b) - h) ** 2) for (G, b), h in zip(S, Hs)])
                                     / np.mean(np.sum(np.abs(Hs) ** 2, 1)))
        for rho in rhos:
            sp = A.SparsePrior(base, Nr, Nt, rho, max(NEMS)); err = {ne: [] for ne in NEMS}
            for (G, bb), h in zip(S, Hs):                    # one MacKay run per sample, read at every n_em in NEMS
                for ne, g in sp.gamma_path(G, bb, set(NEMS)).items():
                    Lam, eta = sp.site_from_gamma(g, G.shape[0])
                    err[ne].append(np.sum(np.abs(np.linalg.solve(Lam + G, eta + bb) - h) ** 2))
            for ne in NEMS:
                res["sbl"].setdefault(f"{rho},{ne}", {})[str(snr)] = float(10 * np.log10(np.mean(err[ne]) / np.mean(np.sum(np.abs(Hs) ** 2, 1))))
            for L in [L for L in LS if L <= Nr * Nt]:
                res["omp"].setdefault(f"{rho},{L}", {})[str(snr)] = e(A.OMPSitePrior(base, Nr, Nt, rho, L))
        print(f"[sparse_tune] {a.prior} {a.cell} {snr:+d} dB done ({time.time() - t0:.0f} s)", flush=True)
    allr = set(rhos)
    if a.merge_with:                               # union with the earlier grid (same stream, same n, same second-parameter grids)
        old = json.load(open(a.merge_with)); assert old["n"] == a.n and old["prior"] == a.prior and old["cell"] == a.cell
        for fam in ("sbl", "omp"):
            for k, v in old["nmse_db"][fam].items():
                res[fam].setdefault(k, v)
        allr |= set(old["grid"]["rho"])
    pick = per_snr_pick(res, cell, Nr * Nt, rhos=allr)
    pfile = os.path.join(C.CONF, "results", "sparse", f"pick_{a.prior}_{a.cell}.json")
    os.makedirs(os.path.dirname(pfile), exist_ok=True); json.dump(pick, open(pfile, "w"), indent=1)
    out = dict(prior=a.prior, cell=a.cell, n=a.n, seed="default_rng([20260930, TBID, PID, Nr, snr+100])", grid=dict(rho=sorted(allr),
               n_em=NEMS, L=LS), nmse_db=res, pick=pick, wall_sec=time.time() - t0)
    path = a.out or os.path.join(C.CONF, "results", "sparse", f"tune_{a.prior}_{a.cell}.json")
    os.makedirs(os.path.dirname(path), exist_ok=True); json.dump(out, open(path, "w"), indent=1)
    print(f"[sparse_tune] pick {pick} -> {path}")


if __name__ == "__main__":
    main()
