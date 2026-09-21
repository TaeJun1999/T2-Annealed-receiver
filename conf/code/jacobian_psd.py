"""H1 diagnostic: is the learned denoiser's Jacobian a valid covariance, and does RouteAClip._matrix_site
turn the answer into a divergence?

For a TRUE posterior-mean denoiser under real Gaussian noise of std sigma,
    Jr = d m_real / d x  =  Cov_real(h | q) / sigma^2   -> SYMMETRIC and PSD.
The receiver does not consume Jr; it consumes the complex Wirtinger J = dm/dq and forms
    SigH = nu J  (Hermitian-symmetrised),  Lam = SigH^-1 - I/nu,  eta = SigH^-1 hH - q/nu
in RouteAClip._matrix_site (Demo/t2_gmm.py:114).  So we report BOTH, plus the exact site arithmetic.
Nothing here is tuned or retrained: a fixed checkpoint is measured on the frozen D2 sigma grid.
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, torch
import common as C, score, arms as A, sigma as SG

NR, NT = 8, 4
N = NR * NT


def jac_stats(model, Xq, sg, nu, chunk=32, project=None):
    """-> dict of per-sample arrays for the real Jacobian Jr and the complex Wirtinger J.

    project: optional callable applied to each Hermitian part Hc BEFORE the eigen/site statistics --
    score.project_psd for the Stage C V1 (F1) measurement.  None (default) = the original diagnostic."""
    R = dict(asym_r=[], lmin_r=[], lmax_r=[], herm_c=[], lmin_c=[], lmax_c=[], cond_c=[],
             shift=[], eta_ratio=[], nclip=[])
    I = np.eye(N)
    for i in range(0, len(Xq), chunk):
        x = Xq[i:i + chunk]
        s = torch.full((len(x),), float(sg), dtype=x.dtype, device=x.device)
        Jr = score.jac_batch(lambda v, u: score.tweedie_real(model, v, u), x, s)      # (b,2N,2N)
        with torch.no_grad():
            m = score.tweedie_real(model, x, s)
        Sr = 0.5 * (Jr + Jr.transpose(-1, -2))
        R["asym_r"].append(((Jr - Jr.transpose(-1, -2)).norm(dim=(-2, -1))
                            / Jr.norm(dim=(-2, -1)).clamp_min(1e-300)).numpy())
        er = torch.linalg.eigvalsh(Sr)
        R["lmin_r"].append(er[:, 0].numpy()); R["lmax_r"].append(er[:, -1].numpy())
        Jc = score.wirtinger(Jr).numpy()                                              # (b,N,N) complex
        Hc = 0.5 * (Jc + Jc.conj().transpose(0, 2, 1))                                # what ScorePrior returns
        if project is not None:                                                       # (F1): what ScorePrior
            Hc = np.stack([project(h) for h in Hc])                                   # returns with psd_project=True
        R["herm_c"].append(np.abs(Jc - Jc.conj().transpose(0, 2, 1)).max((1, 2))
                           / np.maximum(np.abs(Jc).max((1, 2)), 1e-300))
        ec = np.linalg.eigvalsh(Hc)
        R["lmin_c"].append(ec[:, 0]); R["lmax_c"].append(ec[:, -1])
        R["cond_c"].append(np.abs(ec).max(1) / np.maximum(np.abs(ec).min(1), 1e-300))
        # --- the receiver's own arithmetic, RouteAClip._matrix_site verbatim (G omitted: it cancels
        #     out of the clip test, and mu below is the DENOISER-STAGE belief mean the code compares to hH)
        q = score.np_unpack(x.numpy()); hH = score.np_unpack(m.numpy())
        for b in range(len(x)):
            SigH = nu * Hc[b]
            try:
                Si = np.linalg.inv(SigH)
            except np.linalg.LinAlgError:
                R["shift"].append(np.inf); R["eta_ratio"].append(np.inf); R["nclip"].append(1.0); continue
            Lam = 0.5 * (Si - I / nu + (Si - I / nu).conj().T)
            w, V = np.linalg.eigh(Lam)
            eta = Si @ hH[b] - q[b] / nu
            R["eta_ratio"].append(float(np.linalg.norm(eta) / max(np.linalg.norm(q[b] / nu), 1e-300)))
            if w.min() < C.LAM_MIN:
                R["nclip"].append(1.0)
                Lc = (V * np.maximum(w, C.LAM_MIN)) @ V.conj().T
                mu = np.linalg.solve(Lc + I / nu, eta + q[b] / nu)
                R["shift"].append(float(np.sum(np.abs(mu - hH[b]) ** 2)
                                        / max(np.sum(np.abs(hH[b]) ** 2), 1e-300)))
            else:
                R["nclip"].append(0.0); R["shift"].append(0.0)
    return {k: np.concatenate([np.atleast_1d(np.asarray(v)) for v in val]) if k in
            ("asym_r", "lmin_r", "lmax_r", "herm_c", "lmin_c", "lmax_c", "cond_c")
            else np.asarray(val) for k, val in R.items()}


def main(a):
    torch.set_default_dtype(torch.float64)
    torch.set_num_threads(a.threads)
    gen = C.make_gen("D2", a.prior, NR, NT)
    nu_grid, sig_grid = SG.load("D2")
    H = gen.sample_vecs(C.train_rng("D2", a.prior, NR, 10), a.n)          # held-out stream 10
    rng = np.random.default_rng(score.SEED_GATE)
    E = (rng.standard_normal((a.n, N)) + 1j * rng.standard_normal((a.n, N))) / np.sqrt(2)

    fits, llv, bstar, kron_K = A.gmm_selection("D2", a.prior, NR, C.N_TRAIN)
    fam, K = ("kron", kron_K) if bstar == "kron" else ("full", int(bstar[3:]))
    gmm = C.GMMPriorB(NR, NT, fits[(fam, K)]["covs"], fits[(fam, K)]["pi"])
    models = {"diffusion": score._as_model(a.ckpt, NR, NT, "cpu")[0],
              f"GMM-exact(b*={bstar},K={K})": score.ExactGMMTorch(gmm)}

    print(f"# H1: Jacobian validity as a covariance.  ckpt = {a.ckpt}   n = {a.n} held-out D2 samples/point")
    print(f"# Jr = real Jacobian of tweedie_real (what score.jac_batch returns); J = wirtinger(Jr) (what")
    print(f"# ScorePrior hands RouteAClip._matrix_site, after Hermitian symmetrisation).")
    print(f"# TRUE posterior-mean denoiser => Jr symmetric PSD, and nu*Herm(J) = Cov(h|q) >= 0.")
    out = {}
    for tag, m in models.items():
        print(f"\n=== {tag} ===")
        print(f"{'k':>3}{'sigma':>11}{'nu':>11} | {'asym(Jr)':>10}{'lmin(Jr)':>11}{'lmax(Jr)':>10}"
              f"{'f<0':>7} | {'herm(J)':>9}{'lmin(J)':>11}{'lmax(J)':>9}{'f<0':>7}{'f>1':>7}"
              f" | {'clipfrac':>9}{'shift_med':>11}{'shift_max':>11}")
        rows = []
        for k, (nu, sg) in enumerate(zip(nu_grid, sig_grid)):
            Q = torch.as_tensor(score.np_pack(H + np.sqrt(nu) * E), dtype=torch.float64)
            r = jac_stats(m, Q, sg, float(nu))
            rows.append(dict(k=k, nu=float(nu), sigma=float(sg),
                             asym_r=float(r["asym_r"].mean()), lmin_r=float(r["lmin_r"].min()),
                             lmax_r=float(r["lmax_r"].max()), frac_lmin_r_neg=float((r["lmin_r"] < 0).mean()),
                             herm_c=float(r["herm_c"].mean()), lmin_c=float(r["lmin_c"].min()),
                             lmax_c=float(r["lmax_c"].max()), frac_lmin_c_neg=float((r["lmin_c"] < 0).mean()),
                             frac_lmax_c_gt1=float((r["lmax_c"] > 1).mean()),
                             clip_frac=float(r["nclip"].mean()), shift_med=float(np.median(r["shift"])),
                             shift_max=float(np.max(r["shift"])),
                             eta_ratio_med=float(np.median(r["eta_ratio"])),
                             cond_c_med=float(np.median(r["cond_c"]))))
            q = rows[-1]
            print(f"{k:>3}{sg:>11.4e}{nu:>11.4e} | {q['asym_r']:>10.3e}{q['lmin_r']:>11.3e}"
                  f"{q['lmax_r']:>10.3f}{q['frac_lmin_r_neg']:>7.3f} | {q['herm_c']:>9.2e}"
                  f"{q['lmin_c']:>11.3e}{q['lmax_c']:>9.3f}{q['frac_lmin_c_neg']:>7.3f}"
                  f"{q['frac_lmax_c_gt1']:>7.3f} | {q['clip_frac']:>9.3f}{q['shift_med']:>11.3e}"
                  f"{q['shift_max']:>11.3e}", flush=True)
        out[tag] = rows
    np.savez_compressed(a.out, names=list(out), sigma=sig_grid, nu=nu_grid,
                        **{f"{t}|{f}": np.array([r[f] for r in rows])
                           for t, rows in out.items() for f in rows[0]})
    print(f"\n# saved -> {a.out}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--ckpt", default=os.path.join(C.CONF, "ckpt", "d2sx_N10000_a1.pt"))
    p.add_argument("--prior", default="S2")
    p.add_argument("--n", type=int, default=128)
    p.add_argument("--threads", type=int, default=4)
    p.add_argument("--out", default=os.path.join(C.CONF, "results", "diag", "jacobian-psd_D2.npz"))
    main(p.parse_args())
