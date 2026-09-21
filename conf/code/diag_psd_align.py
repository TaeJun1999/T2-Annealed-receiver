"""conf/code/diag_psd_align.py -- independent re-derivation of the Jacobian-validity statistics with a
DIFFERENT sample stream, plus the measurement that decides WHICH property of the bad Jacobian drives the
D-14 site blow-up:  the SIGN of the eigenvalues (indefiniteness) or their MAGNITUDE near zero
(near-singular SigH), and how the small-eigenvalue directions line up with the denoiser output hH.

eta = SigH^-1 hH - q/nu  blows up only along directions where 1/eig(SigH) is huge AND hH has energy.
  align_k = |<v_k, hH>|^2 / ||hH||^2  for the eigenvector of the k-th smallest |eig| of Herm(J).
Site-level (no receiver) so it is cheap; the receiver-level counterfactual is diag_psd_cf.py.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, torch
import common as C, score, arms as A, sigma as SG

NR, NT = 8, 4; N = NR * NT
torch.set_default_dtype(torch.float64); torch.set_num_threads(2)
K = int(os.environ.get("KGRID", 6)); n = int(os.environ.get("NSAMP", 128))
SEED = 987654321                                  # NOT score.SEED_GATE: an independent stream

gen = C.make_gen("D2", "S2", NR, NT)
nu_grid, sig_grid = SG.load("D2"); nu, sg = float(nu_grid[K]), float(sig_grid[K])
H = gen.sample_vecs(np.random.default_rng([SEED, 1]), n)          # held out from training and from their run
rng = np.random.default_rng([SEED, 2])
E = (rng.standard_normal((n, N)) + 1j * rng.standard_normal((n, N))) / np.sqrt(2)
Q = H + np.sqrt(nu) * E

fits, _, bstar, kK = A.gmm_selection("D2", "S2", NR, C.N_TRAIN)
fam, KK = ("kron", kK) if bstar == "kron" else ("full", int(bstar[3:]))
gmm = C.GMMPriorB(NR, NT, fits[(fam, KK)]["covs"], fits[(fam, KK)]["pi"])
models = {"diffusion": score._as_model(os.path.join(C.CONF, "ckpt", "d2sx_N10000_a1.pt"), NR, NT, "cpu")[0],
          f"GMM-exact({bstar},K={KK})": score.ExactGMMTorch(gmm)}
I = np.eye(N)

def interventions(w):
    """spectra of Herm(J) after each do()-intervention used by diag_psd_cf.py"""
    out = {"as-is": w}
    out["psd1e-2"] = np.clip(w, 1e-2, 1.0)                                   # sign AND magnitude repaired
    out["abs1e-2"] = np.sign(w) * np.clip(np.abs(w), 1e-2, 1.0)              # magnitude repaired, sign KEPT
    ix = np.argsort(np.abs(w))[:4]
    f = w.copy(); f[ix] = -np.abs(f[ix]); out["flip4"] = f                   # sign broken, magnitude kept
    t = w.copy(); t[ix] = 1e-4;           out["tiny4"] = t                   # magnitude broken, sign kept (PD)
    return out

print(f"# independent stream seed={SEED} (NOT the claimant's SEED_GATE), n={n}, grid k={K}: "
      f"sigma={sg:.4e}  nu={nu:.4e}")
print(f"# align_k = |<v_k,hH>|^2/||hH||^2, v_k = eigvec of the k-th smallest |eig| of Herm(J)\n")
hdr = (f"{'model':<22}{'frac lmin<0':>12}{'med lmin':>11}{'med |lmin|':>11}{'med align_0':>12}"
       f"{'med align_0..3':>15}{'med cond':>11}")
print(hdr)
store = {}
for tag, m in models.items():
    X = torch.as_tensor(score.np_pack(Q), dtype=torch.float64)
    s = torch.full((n,), sg, dtype=X.dtype)
    Jr = score.jac_batch(lambda v, u: score.tweedie_real(m, v, u), X, s)
    with torch.no_grad():
        hH = score.np_unpack(score.tweedie_real(m, X, s).numpy())
    Jc = score.wirtinger(Jr).numpy(); Hc = 0.5 * (Jc + Jc.conj().transpose(0, 2, 1))
    lmin = np.empty(n); amin = np.empty(n); a0 = np.empty(n); a03 = np.empty(n); cd = np.empty(n)
    sh = {k: np.empty(n) for k in ("as-is", "psd1e-2", "abs1e-2", "flip4", "tiny4")}
    er = {k: np.empty(n) for k in sh}
    for b in range(n):
        w, V = np.linalg.eigh(Hc[b])
        lmin[b] = w[0]; amin[b] = np.abs(w).min(); cd[b] = np.abs(w).max() / max(np.abs(w).min(), 1e-300)
        o = np.argsort(np.abs(w)); nh2 = max(np.sum(np.abs(hH[b]) ** 2), 1e-300)
        pr = np.abs(V.conj().T @ hH[b]) ** 2 / nh2
        a0[b] = pr[o[0]]; a03[b] = pr[o[:4]].sum()
        for k, wk in interventions(w).items():
            S = nu * (V * wk) @ V.conj().T
            Si = np.linalg.inv(S)
            Lam = 0.5 * (Si - I / nu + (Si - I / nu).conj().T)
            ww, VV = np.linalg.eigh(Lam); eta = Si @ hH[b] - Q[b] / nu
            er[k][b] = np.linalg.norm(eta) / np.linalg.norm(Q[b] / nu)
            if ww.min() < C.LAM_MIN:
                Lc = (VV * np.maximum(ww, C.LAM_MIN)) @ VV.conj().T
                mu = np.linalg.solve(Lc + I / nu, eta + Q[b] / nu)
                sh[k][b] = np.sum(np.abs(mu - hH[b]) ** 2) / nh2
            else:
                sh[k][b] = 0.0
    store[tag] = (sh, er)
    print(f"{tag:<22}{np.mean(lmin<0):12.3f}{np.median(lmin):11.3e}{np.median(amin):11.3e}"
          f"{np.median(a0):12.3e}{np.median(a03):15.3e}{np.median(cd):11.3e}")

print(f"\n# site-level belief-mean shift ||mu-hH||^2/||hH||^2 under each do()-intervention on Herm(J)")
print(f"{'model':<22}{'intervention':<12}{'shift med':>12}{'shift p90':>12}{'shift max':>12}{'||eta||/||q/nu|| med':>22}")
for tag, (sh, er) in store.items():
    for k in ("as-is", "psd1e-2", "abs1e-2", "flip4", "tiny4"):
        print(f"{tag:<22}{k:<12}{np.median(sh[k]):12.3e}{np.percentile(sh[k],90):12.3e}"
              f"{sh[k].max():12.3e}{np.median(er[k]):22.3e}")
