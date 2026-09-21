"""Why is the learned Jacobian indefinite on D2 but not on D1?  Measure the SPECTRUM, not just lmin.

HYPOTHESIS (stated before measuring).  J = dm/dq = Cov(h|q)/sigma^2 for a true posterior-mean denoiser.
D2's support is a union of 3L-dimensional manifolds (L ~ U{3..8}) inside R^(2*Nr*Nt) = R^64, i.e.
9..24 dimensions with 40..55 co-dimensions.  Along a co-dimension the conditional variance is ~0, so the
TRUE J has 40..55 eigenvalues sitting AT the PSD boundary.  Any finite-network error therefore flips
roughly half of them negative, which is why f(lmin<0) = 1 at every budget.  D1's prior is a
1024-component grid GMM with FULL support in R^64, so its true J has no near-zero eigenvalue
(measured lmin = +0.94) and the same estimation error cannot change a sign.

PREDICTION.  n_neg on D2 should be of order (co-dimension)/2 ~ 20-27 and roughly budget-independent;
on D1 it should be 0.  The EXACT prior (GMM, closed form) is measured alongside as the control.
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, torch
import common as C, score, arms as A, sigma as SG

NR, NT = 8, 4
N = NR * NT


def spectra(model, Xq, sg, chunk=16):
    """-> (n_samples, 2N) real-symmetric eigenvalues of sym(Jr), ascending."""
    out = []
    for i in range(0, len(Xq), chunk):
        x = Xq[i:i + chunk]
        s = torch.full((len(x),), float(sg), dtype=x.dtype, device=x.device)
        Jr = score.jac_batch(lambda v, u: score.tweedie_real(model, v, u), x, s)
        Js = 0.5 * (Jr + Jr.transpose(-1, -2))
        out.append(torch.linalg.eigvalsh(Js.double()).cpu().numpy())
    return np.concatenate(out, 0)


def main(a):
    torch.set_num_threads(a.threads)
    TB = a.testbed
    prior = a.prior or C.PRIOR_OF[TB]
    gen = C.make_gen(TB, prior, NR, NT)
    nu_grid, sig_grid = SG.load(TB)
    H = gen.sample_vecs(C.train_rng(TB, prior, NR, 10), a.n)          # held-out stream 10
    models = {"diffusion": score._as_model(a.ckpt, NR, NT, "cpu")[0]}

    # THE reference matters.  On D1 the TRUE prior is available in closed form -- it is the grid
    # mixture the testbed is DEFINED by (common.D1Gen.prior = t2_gmm.angle_grid_prior(...), 32x32 =
    # 1024 components).  An earlier version of this script used arms.gmm_selection() here, which
    # returns an EM FIT on N_TRAIN samples, and the output was labelled "EXACT"; the 2026-09-21 18:20
    # audit caught that and the claim resting on it was retracted.  Now BOTH are reported on D1, so a
    # reader can see the learned model against ground truth AND against the fitted mixture.
    if TB == "D1":
        models["TRUE-prior(grid GMM, 1024 comp)"] = score.ExactGMMTorch(gen.prior)
    fits, llv, bstar, kron_K = A.gmm_selection(TB, prior, NR, C.N_TRAIN)
    fam, K = ("kron", kron_K) if bstar == "kron" else ("full", int(bstar[3:]))
    gmm = C.GMMPriorB(NR, NT, fits[(fam, K)]["covs"], fits[(fam, K)]["pi"])
    models[f"FITTED-GMM(b*={bstar},K={K},N={C.N_TRAIN})"] = score.ExactGMMTorch(gmm)

    print(C.header(TB, extra=[
        f"content     : eigenvalue SPECTRUM of sym(Jr), not just its minimum.  ckpt = {a.ckpt}",
        f"n           : {a.n} held-out samples per grid point, 2N = {2 * N} eigenvalues each",
        "hypothesis  : D2's support is a union of 3L-dim manifolds (L~U{3..8}) in R^64, so the TRUE J",
        "              has 40..55 eigenvalues AT the PSD boundary; estimation error flips ~half of them.",
        "              D1's grid-GMM prior has full support, so its true J has no near-zero eigenvalue.",
    ]))
    print()
    for name, m in models.items():
        print(f"=== {name} ===")
        print(f"{'k':>3} {'sigma':>11} | {'n_neg mean':>10} {'n_neg med':>9} {'n_neg p90':>9} | "
              f"{'n<0.01':>7} {'n<0.1':>7} | {'lmin':>10} {'l[0.25]':>9} {'lmed':>8} {'lmax':>8}")
        for k in a.ks:
            ev = spectra(m, torch.as_tensor(np.concatenate([H.real, H.imag], -1), dtype=torch.float64),
                         float(sig_grid[k]))
            nneg = (ev < 0).sum(1)
            print(f"{k:>3} {sig_grid[k]:>11.4e} | {nneg.mean():>10.2f} {np.median(nneg):>9.1f} "
                  f"{np.percentile(nneg, 90):>9.1f} | {(ev < 0.01).sum(1).mean():>7.2f} "
                  f"{(ev < 0.1).sum(1).mean():>7.2f} | {ev.min():>10.3e} "
                  f"{np.percentile(ev, 25):>9.3e} {np.median(ev):>8.3e} {ev.max():>8.3e}")
        print()
    print(f"co-dimension of the D2 support: 2*Nr*Nt - 3L = {2*N} - {{9..24}} = {{{2*N-24}..{2*N-9}}}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--ckpt", required=True)
    p.add_argument("--testbed", default="D2", choices=["D1", "D2"])
    p.add_argument("--prior", default=None)
    p.add_argument("--n", type=int, default=48)
    p.add_argument("--ks", type=int, nargs="+", default=[0, 6, 12, 18])
    p.add_argument("--threads", type=int, default=2)
    main(p.parse_args())
