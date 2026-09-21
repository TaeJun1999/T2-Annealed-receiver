"""Independent re-derivation of the 'learned Jacobian is not PSD' claim.
Differences from the published check (code/jacobian_psd*.py): a DIFFERENT held-out channel stream
(seed 11, not 10), a DIFFERENT noise seed, and score.ExactGMMTorch as the GMM reference (the published
run used t2_gmm.GMMPriorB -- their caveat (3) was that the two were never cross-checked).
Read-only: frozen checkpoint, no training, no tuning."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, torch
import common as C, score, arms as A, sigma as SG

NR, NT = 8, 4; N = NR * NT
torch.set_default_dtype(torch.float64); torch.set_num_threads(2)
n = 96
gen = C.make_gen("D2", "S2", NR, NT)
nu_grid, sig_grid = SG.load("D2")
H = gen.sample_vecs(C.train_rng("D2", "S2", NR, 11), n)          # stream 11: NOT the published one
rng = np.random.default_rng(20260921)                             # independent noise seed
fits, _, bstar, kK = A.gmm_selection("D2", "S2", NR, C.N_TRAIN)
fam, KK = ("kron", kK) if bstar == "kron" else ("full", int(bstar[3:]))
gmm = C.GMMPriorB(NR, NT, fits[(fam, KK)]["covs"], fits[(fam, KK)]["pi"])
models = {"diffusion": score._as_model(os.path.join(C.CONF, "ckpt", "d2sx_N10000_a1.pt"), NR, NT, "cpu")[0],
          f"ExactGMMTorch({bstar},K={KK})": score.ExactGMMTorch(gmm)}
I = np.eye(N)
rows = {}
print(f"# INDEPENDENT PSD re-check. n={n} held-out q per nu, stream 11, noise seed 20260921, b*={bstar} K={KK}")
print(f"# nu picked from the FROZEN measured D2 grid nearest the median nu_q the C2 receiver actually visits")
print(f"{'model':<26}{'nu':>10}{'sigma':>10}{'in-grid':>8}{'med lmin(J)':>13}{'worst lmin':>12}"
      f"{'med lmax(J)':>13}{'frac lmin<0':>12}{'frac lmax>1':>12}{'med #eig<0':>11}{'med|eta|/|q/nu|':>17}{'med shift':>11}")
for nu_target in (2.50e-1, 8.04e-2, 3.00e-2, 1.95e-2):
    k = int(np.argmin(np.abs(nu_grid - nu_target))); nu, sg = float(nu_grid[k]), float(sig_grid[k])
    Q = H + np.sqrt(nu) * (rng.standard_normal((n, N)) + 1j * rng.standard_normal((n, N))) / np.sqrt(2)
    X = torch.as_tensor(score.np_pack(Q), dtype=torch.float64); s = torch.full((n,), sg, dtype=X.dtype)
    for tag, m in models.items():
        Jr = score.jac_batch(lambda v, u: score.tweedie_real(m, v, u), X, s)
        with torch.no_grad():
            hH = score.np_unpack(score.tweedie_real(m, X, s).numpy())
        Jc = score.wirtinger(Jr).numpy(); Hc = 0.5 * (Jc + Jc.conj().transpose(0, 2, 1))
        asym = float(np.median(np.abs(Jc - Jc.conj().transpose(0, 2, 1)).max((1, 2))
                               / np.maximum(np.abs(Jc).max((1, 2)), 1e-300)))
        ec = np.linalg.eigvalsh(Hc)
        sh = np.zeros(n); er = np.zeros(n)
        for b in range(n):
            S = nu * Hc[b]; Si = np.linalg.inv(S)
            Lam = 0.5 * (Si - I / nu + (Si - I / nu).conj().T)
            w, V = np.linalg.eigh(Lam); eta = Si @ hH[b] - Q[b] / nu
            er[b] = np.linalg.norm(eta) / np.linalg.norm(Q[b] / nu)
            if w.min() < C.LAM_MIN:
                Lc = (V * np.maximum(w, C.LAM_MIN)) @ V.conj().T
                mu = np.linalg.solve(Lc + I / nu, eta + Q[b] / nu)
                sh[b] = np.sum(np.abs(mu - hH[b]) ** 2) / np.sum(np.abs(hH[b]) ** 2)
        print(f"{tag:<26}{nu:>10.3e}{sg:>10.3e}{'yes':>8}{np.median(ec[:,0]):>13.3e}{ec[:,0].min():>12.3e}"
              f"{np.median(ec[:,-1]):>13.4f}{np.mean(ec[:,0]<0):>12.3f}{np.mean(ec[:,-1]>1):>12.3f}"
              f"{np.median((ec<0).sum(1)):>11.1f}{np.median(er):>17.3e}{np.median(sh):>11.3e}")
        rows[f"{tag}|nu{nu:.4e}"] = np.array([nu, sg, np.median(ec[:,0]), ec[:,0].min(), np.median(ec[:,-1]),
                                              np.mean(ec[:,0]<0), np.mean(ec[:,-1]>1), np.median((ec<0).sum(1)),
                                              np.median(er), np.median(sh), asym])
    print("    -> median relative non-Hermitian residual of the RAW J: diffusion %.4f, gmm %.2e"
          % (rows["diffusion|nu%.4e" % nu][10], rows["ExactGMMTorch(%s,K=%d)|nu%.4e" % (bstar, KK, nu)][10]))
np.savez_compressed(os.path.join(C.CONF, "results", "diag", "h4-jswap_psd_independent.npz"), **rows,
                    cols=np.array("nu,sigma,med_lmin,worst_lmin,med_lmax,frac_lmin_neg,frac_lmax_gt1,med_neig,med_eta_ratio,med_shift,med_asym"))
print("# saved results/diag/h4-jswap_psd_independent.npz")
