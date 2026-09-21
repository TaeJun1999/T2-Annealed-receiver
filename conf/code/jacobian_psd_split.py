"""Isolate WHICH Jacobian invalidity drives the site blow-up, at the sigma the receiver actually operates at
on C2 (median nu_q = 1.837e-2 at 6 dB -> grid point k=6, nu=1.6932e-2).  Splits the shift induced by
RouteAClip._matrix_site's clip by whether SigH = nu*Herm(J) is indefinite (lmin<0) or merely has lmax>1."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, torch
import common as C, score, arms as A, sigma as SG

NR, NT = 8, 4; N = NR * NT; K = 6
torch.set_default_dtype(torch.float64); torch.set_num_threads(4)
gen = C.make_gen("D2", "S2", NR, NT)
nu_grid, sig_grid = SG.load("D2"); nu, sg = float(nu_grid[K]), float(sig_grid[K])
n = 256
H = gen.sample_vecs(C.train_rng("D2", "S2", NR, 10), n)
rng = np.random.default_rng(score.SEED_GATE)
E = (rng.standard_normal((n, N)) + 1j * rng.standard_normal((n, N))) / np.sqrt(2)
Q = H + np.sqrt(nu) * E
fits, _, bstar, kK = A.gmm_selection("D2", "S2", NR, C.N_TRAIN)
fam, KK = ("kron", kK) if bstar == "kron" else ("full", int(bstar[3:]))
gmm = C.GMMPriorB(NR, NT, fits[(fam, KK)]["covs"], fits[(fam, KK)]["pi"])
models = {"diffusion": score._as_model(os.path.join(C.CONF, "ckpt", "d2sx_N10000_a1.pt"), NR, NT, "cpu")[0],
          f"GMM-exact({bstar},K={KK})": score.ExactGMMTorch(gmm)}
I = np.eye(N)
print(f"# grid point k={K}: sigma={sg:.4e}, nu={nu:.4e}  (C2 @ 6 dB median nu_q = 1.837e-2)  n={n}")
print(f"# shift = ||mu - hH||^2 / ||hH||^2, mu = (Lam_clipped + I/nu)^-1 (eta + q/nu)  -- t2_gmm.py:120 verbatim")
print(f"{'model':<24}{'group':<22}{'n':>5}{'shift_med':>12}{'shift_p90':>12}{'shift_max':>12}"
      f"{'||eta||/||q/nu||':>19}{'cond(SigH)':>12}")
for tag, m in models.items():
    X = torch.as_tensor(score.np_pack(Q), dtype=torch.float64)
    s = torch.full((n,), sg, dtype=X.dtype)
    Jr = score.jac_batch(lambda v, u: score.tweedie_real(m, v, u), X, s)
    with torch.no_grad():
        hHt = score.tweedie_real(m, X, s)
    Jc = score.wirtinger(Jr).numpy(); Hc = 0.5 * (Jc + Jc.conj().transpose(0, 2, 1))
    hH = score.np_unpack(hHt.numpy())
    ec = np.linalg.eigvalsh(Hc)
    sh = np.empty(n); er = np.empty(n); cd = np.empty(n)
    for b in range(n):
        S = nu * Hc[b]; Si = np.linalg.inv(S)
        Lam = 0.5 * (Si - I / nu + (Si - I / nu).conj().T)
        w, V = np.linalg.eigh(Lam); eta = Si @ hH[b] - Q[b] / nu
        er[b] = np.linalg.norm(eta) / np.linalg.norm(Q[b] / nu)
        e = np.linalg.eigvalsh(S); cd[b] = abs(e).max() / max(abs(e).min(), 1e-300)
        if w.min() < C.LAM_MIN:
            Lc = (V * np.maximum(w, C.LAM_MIN)) @ V.conj().T
            mu = np.linalg.solve(Lc + I / nu, eta + Q[b] / nu)
            sh[b] = np.sum(np.abs(mu - hH[b]) ** 2) / np.sum(np.abs(hH[b]) ** 2)
        else:
            sh[b] = 0.0
    neg = ec[:, 0] < 0; big = (~neg) & (ec[:, -1] > 1); ok = (~neg) & (~big)
    for name, msk in (("SigH indefinite", neg), ("PD but lmax(J)>1", big), ("PD and lmax(J)<=1", ok)):
        if msk.sum() == 0:
            print(f"{tag:<24}{name:<22}{0:>5}{'-':>12}{'-':>12}{'-':>12}{'-':>19}{'-':>12}"); continue
        print(f"{tag:<24}{name:<22}{int(msk.sum()):>5}{np.median(sh[msk]):>12.3e}"
              f"{np.percentile(sh[msk],90):>12.3e}{sh[msk].max():>12.3e}{np.median(er[msk]):>19.3e}"
              f"{np.median(cd[msk]):>12.3e}")
