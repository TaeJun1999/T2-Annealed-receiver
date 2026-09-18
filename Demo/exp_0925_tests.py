"""exp_0925 unit tests for t2_gmm.py (code verification only — no receiver simulation).   usage: python exp_0925_tests.py        (~1 min, single core)
T1 batched tilted moments == loop reference with the parent's formulas (<= 1e-10); site == parent's ep_site at the BELIEF level.
   (The raw site Lambda = Cov^-1 - G is ill-conditioned: round-off 1e-12 in the evidences is amplified by |Cov^-1|^2 ~ 1e5 -> compare beliefs, not sites.)
   T1b clip='mean' keeps the belief mean at the exact tilted mean m;  clip='eta' (legacy) does not (shift reported)
T2 denoise_full / denoise == parent;  log_pdf == parent's log_pdf_noisy(nu=0)
T3 EM: monotone log-likelihood (floor=0), identity sum_k pi_k C_k = sample covariance, recovery of a known small mixture (validation KL gap);
   T3k Kronecker M-step: K=1 flip-flop is the matrix-normal MLE (train LL(fit) >= LL(true kron) — fails if a transpose is wrong), error -> 0 with n, monotone for K=3;
   T3s kappa -> inf gives C_k = Chat;  validation early stopping returns the best-validation iterate
T4 prior definitions: U ensemble covariance = I, Kronecker form of the ensemble covariance, spectra of S and P, component index convention
T5 sample_vecs: second moments (Monte Carlo, loose)
T6 RouteAClip(clip='eta') reproduces RouteA bit-for-bit on one trial (D-14 site path), and one n=1 smoke run of clip='mean' (numbers discarded)"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"): os.environ.setdefault(_v, "1")
import sys, time, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from scipy.special import logsumexp
from t2_route_a import GMMPrior, steer_corr, RouteA, QAMCode
from t2_gmm import GMMPriorB, RouteAClip, fit_gmm_em, angle_grid_prior, ensemble_sides, angle_grids, _cn
np.set_printoptions(precision=3, suppress=True, linewidth=170)
ok_all = True


def check(name, err, tol):
    global ok_all; ok = err <= tol; ok_all &= ok
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}: {err:.2e} (tol {tol:.0e})")


def covs_0920(Nr, Nt, rho=0.7):
    psis = 2 * np.pi * (np.arange(4) + 0.5) / 4
    return [np.kron(steer_corr(Nt, rho, pt).T, steer_corr(Nr, rho, pr)) for pt in psis for pr in psis]


def rand_Gb(rng, Nr, Nt, Tcols, sigma2):
    """L_H-type (G, b): sum over Tcols columns of d kron(conj(x) x^T, I), d kron(conj(x), y) — rank-deficient when Tcols < Nt."""
    N = Nr * Nt; G = np.zeros((N, N), complex); b = np.zeros(N, complex)
    for _ in range(Tcols):
        x = _cn(rng, Nt) * np.sqrt(2); y = _cn(rng, Nr); d = 1 / sigma2
        G += d * np.kron(np.outer(x.conj(), x), np.eye(Nr)); b += d * np.kron(x.conj(), y)
    return G, b


rng = np.random.default_rng(925)
print("T1/T2 — batched vs parent (exp_0920 16-component prior)")
for Nr, Nt in ((4, 4), (8, 4)):
    cv = covs_0920(Nr, Nt); pa = GMMPrior(Nr, Nt, cv); pb = GMMPriorB(Nr, Nt, cv); pm = pb.view("mean"); e_mom = e_bel = e_mp = e_den = e_lp = 0.0; shifts = []
    for Tcols, s2 in ((2, 0.1), (2, 0.01), (6, 0.05), (14, 0.5)):
        G, b = rand_Gb(rng, Nr, Nt, Tcols, s2); I = np.eye(pa.N)
        Sig = [np.linalg.inv(np.linalg.inv(C) + G) for C in pa.covs]; mu = [S @ b for S in Sig]                       # loop reference, parent's formulas
        lw = np.array([np.log(pa.pi[k]) - np.linalg.slogdet(I + pa.covs[k] @ G)[1] + np.real(np.vdot(b, mu[k])) for k in range(pa.K)]); w0 = np.exp(lw - logsumexp(lw))
        m0 = sum(wk * mk for wk, mk in zip(w0, mu)); C0 = sum(wk * (Sk + np.outer(mk, mk.conj())) for wk, Sk, mk in zip(w0, Sig, mu)) - np.outer(m0, m0.conj())
        w1, m1, C1 = pb.tilted_moments(G, b); e_mom = max(e_mom, np.abs(w0 - w1).max(), np.abs(m0 - m1).max(), np.abs(C0 - C1).max())
        for lam_min in (0.0, 1e-6):
            La, ea = pa.ep_site(G, b, lam_min); Lb, eb = pb.ep_site(G, b, lam_min); Lm, em = pm.ep_site(G, b, lam_min)
            ha, hb, hm = (np.linalg.solve(L + G, e + b) for L, e in ((La, ea), (Lb, eb), (Lm, em)))
            e_bel = max(e_bel, np.abs(ha - hb).max(), np.abs(np.linalg.inv(La + G) - np.linalg.inv(Lb + G)).max())
            e_mp = max(e_mp, np.abs(hm - m1).max(), np.abs(Lm - Lb).max() / max(1.0, np.abs(Lb).max())); shifts.append(np.sum(np.abs(hb - m1) ** 2) / np.sum(np.abs(m1) ** 2))
    check(f"{Nr}x{Nt} tilted moments (w, m, Cov) vs loop reference", e_mom, 1e-10); check(f"{Nr}x{Nt} ep_site vs parent, belief level (mean, Sigma)", e_bel, 1e-7)
    check(f"{Nr}x{Nt} clip='mean': belief mean == m, same Lambda", e_mp, 1e-8)
    print(f"      legacy clip='eta': |mu - m|^2/|m|^2 over the 8 (G,b,lam_min) cases = {np.array(shifts)}   counters n_clip/n_site = {pb.n_clip}/{pb.n_site}")
    for nu in (1.2, 0.3, 0.01):
        q = pa.sample(rng).reshape(-1, order="F") + np.sqrt(nu) * _cn(rng, pa.N)
        ma, Ja = pa.denoise_full(q, nu); mb, Jb = pb.denoise_full(q, nu); e_den = max(e_den, np.abs(ma - mb).max(), np.abs(Ja - Jb).max())
        m1, a1 = pb.denoise(q, nu); e_den = max(e_den, np.abs(m1 - mb).max(), abs(a1 - np.trace(Jb).real / pb.N))
        e_lp = max(e_lp, abs(pa.log_pdf_noisy(q, 0.0) - pb.log_pdf(q[None])[0]))
    check(f"{Nr}x{Nt} denoise_full / denoise", e_den, 1e-12); check(f"{Nr}x{Nt} log_pdf", e_lp, 1e-10)

print("T3 — EM")
Nr = Nt = 2; cv = [np.kron(steer_corr(Nt, 0.9, a).T, steer_corr(Nr, 0.9, c)) for a, c in ((0.3, 2.0), (2.5, -1.0), (-2.0, 0.5))]
true = GMMPriorB(Nr, Nt, cv, weights=[0.5, 0.3, 0.2]); X, _ = true.sample_vecs(np.random.default_rng(1), 20000); Xv, _ = true.sample_vecs(np.random.default_rng(2), 5000)
f0 = fit_gmm_em(X, 3, np.random.default_rng(3), n_iter=200, tol=0.0, floor=0.0)
check("monotone log-likelihood, floor=0 (largest decrease)", max(0.0, float(-np.diff(f0["ll"]).min())), 1e-9)
check("sum_k pi_k C_k == sample covariance, floor=0", np.abs(np.einsum("k,kij->ij", f0["pi"], f0["covs"]) - f0["Chat"]).max(), 1e-12)
best = max((fit_gmm_em(X, 3, np.random.default_rng([3, r]), n_iter=300) for r in range(4)), key=lambda f: GMMPriorB(Nr, Nt, f["covs"], f["pi"]).log_pdf(Xv).mean())
fit = GMMPriorB(Nr, Nt, best["covs"], best["pi"]); kl = float(true.log_pdf(Xv).mean() - fit.log_pdf(Xv).mean())
print(f"    recovery: weights true {np.sort(true.pi)[::-1]} fit {np.sort(fit.pi)[::-1]}  iterations {best['n_iter']}  reseeds {best['n_reseed']}")
check("validation KL gap  E_true[log p_true - log p_fit]  (n_val = 5000; pass = small)", abs(kl), 5e-3)

print("T3k/T3s — Kronecker M-step, shrinkage, early stopping")
Nr, Nt = 3, 2; T0 = steer_corr(Nt, 0.8, 0.7).T; R0 = steer_corr(Nr, 0.6, -1.1); one = GMMPriorB(Nr, Nt, np.kron(T0, R0)[None]); Xk, _ = one.sample_vecs(np.random.default_rng(11), 40000)
fk = fit_gmm_em(Xk, 1, np.random.default_rng(12), n_iter=30, tol=0.0, floor=0.0, struct="kron", dims=(Nr, Nt))
check("K=1 kron: |C_fit - kron(T0, R0)|max (n = 40000; pass = O(1/sqrt n))", np.abs(fk["covs"][0] - np.kron(T0, R0)).max(), 0.03)
check("K=1 kron: train LL(true) - LL(fit) <= 0 (MLE property)", max(0.0, float(one.log_pdf(Xk).mean() - fk["ll"][-1])), 1e-9)
ff = fit_gmm_em(Xk, 1, np.random.default_rng(12), n_iter=25, tol=0.0, floor=0.0)
check("K=1: LL(full) >= LL(kron) >= LL(true)  (nested models)", max(0.0, float(fk["ll"][-1] - ff["ll"][-1])), 1e-9)
cvk = [np.kron(steer_corr(Nt, 0.9, a).T, steer_corr(Nr, 0.9, c)) for a, c in ((0.3, 2.0), (2.5, -1.0), (-2.0, 0.5))]; tk = GMMPriorB(Nr, Nt, cvk); X3, _ = tk.sample_vecs(np.random.default_rng(13), 20000)
f3 = fit_gmm_em(X3, 3, np.random.default_rng(14), n_iter=150, tol=0.0, floor=0.0, struct="kron", dims=(Nr, Nt))
check("K=3 kron: monotone log-likelihood (largest decrease)", max(0.0, float(-np.diff(f3["ll"]).min())), 1e-9)
X3v, _ = tk.sample_vecs(np.random.default_rng(15), 5000); check("K=3 kron: validation KL gap", abs(float(tk.log_pdf(X3v).mean() - GMMPriorB(Nr, Nt, f3["covs"], f3["pi"]).log_pdf(X3v).mean())), 5e-3)
fs = fit_gmm_em(X3, 3, np.random.default_rng(14), n_iter=30, floor=0.0, kappa=1e12); check("kappa -> inf: every C_k == Chat", max(np.abs(C - fs["Chat"]).max() for C in fs["covs"]), 1e-6)
Xs, _ = tk.sample_vecs(np.random.default_rng(16), 120); fe = fit_gmm_em(Xs, 8, np.random.default_rng(17), n_iter=200, tol=0.0, Xval=X3v, val_every=5, patience=20)     # tiny n -> over-fits
tr = fe["ll_val_traj"]; check("early stopping returns the best-validation iterate", abs(fe["ll_val"] - tr[:, 1].max()) + abs(fe["it_best"] - tr[np.argmax(tr[:, 1]), 0]), 0.0)
check("... and its parameters reproduce that validation LL", abs(float(GMMPriorB(Nr, Nt, fe["covs"], fe["pi"]).log_pdf(X3v).mean()) - fe["ll_val"]), 1e-9)
print(f"      (over-fit demo: best val at it {fe['it_best']} of {fe['n_iter']}, val LL {fe['ll_val']:.3f} vs last {tr[-1, 1]:.3f})")

print("T4 — prior definitions (Kg = 32)")
for Nr, Nt in ((4, 4), (8, 4)):
    for kind in ("U", "S", "P"):
        t0 = time.time(); pr = angle_grid_prior(kind, Nr, Nt); Rt, Rr = ensemble_sides(kind, Nr, Nt); dt = time.time() - t0
        check(f"{kind} {Nr}x{Nt}: prior.C == kron(R_t,ens^T, R_r,ens)   [K={pr.K}, build {dt:.1f} s]", np.abs(pr.C - np.kron(Rt.T, Rr)).max(), 1e-12)
        if kind == "U": check(f"U {Nr}x{Nt}: ensemble covariance == I", np.abs(pr.C - np.eye(pr.N)).max(), 1e-12)
        print(f"      eig R_t,ens = {np.linalg.eigvalsh(Rt)[::-1]}   eig R_r,ens = {np.linalg.eigvalsh(Rr)[::-1]}   min eig C_k = {pr.lam.min():.4f}")
    pt, prr = angle_grids("S", 32); pr = angle_grid_prior("S", Nr, Nt); k = 5 * 32 + 17
    check(f"S {Nr}x{Nt}: component index k = a_t*Kg + a_r", np.abs(pr.covs[k] - np.kron(steer_corr(Nt, 0.7, pt[5]).T, steer_corr(Nr, 0.7, prr[17]))).max(), 1e-13)

print("T5 — sample_vecs second moments (Monte Carlo, n = 40000; loose)")
pr = angle_grid_prior("S", 4, 4); X, ks = pr.sample_vecs(np.random.default_rng(5), 40000)
check("|sample cov - prior.C|max", np.abs(X.T @ X.conj() / len(X) - pr.C).max(), 0.05)
H = pr.sample(np.random.default_rng(6)); check("parent .sample still works (shape, last_k)", float(H.shape != (4, 4) or pr.last_k is None), 0)

print("T6 — RouteAClip vs RouteA (one trial, 4x4, T=28, Tp=2, 12 dB, exp_0920 prior, D13+14_pf path; smoke only)")
Nr = Nt = 4; T, Tp = 28, 2; pr = GMMPriorB(Nr, Nt, covs_0920(Nr, Nt)); code = QAMCode(("133", "171"), 6, 2, Nt * (T - Tp)); r6 = np.random.default_rng(6)
kw = dict(mode="scalar", scal="belief", hsite="matrix", lam_min=1e-6, beta=0.7, feedback="posterior")
rx0 = RouteA(Nr, Nt, T, Tp, 10 ** -1.2, pr, code, **kw); rx1 = RouteAClip(Nr, Nt, T, Tp, 10 ** -1.2, pr, code, clip="eta", **kw); rx2 = RouteAClip(Nr, Nt, T, Tp, 10 ** -1.2, pr, code, clip="mean", **kw)
H = pr.sample(r6); u = r6.integers(0, 2, code.K); perm = r6.permutation(code.Ns); X, Y = rx0.transmit(u, perm, H, r6)
l0, l1, l2 = (rx.run(Y, H, u, perm, 8) for rx in (rx0, rx1, rx2))
check("clip='eta' logs identical to RouteA (max |diff| over nmse, ber, nu_q, tauL)", max(float(np.nanmax(np.abs(l0[k] - l1[k]))) for k in ("nmse", "ber", "nu_q", "tauL_gmean")), 0.0)
print(f"      clips (eta arm) {rx1.n_clip}/{rx1.n_site}, (mean arm) {rx2.n_clip}/{rx2.n_site};  clip='mean' run finite: {bool(np.all(np.isfinite(l2['nmse'])))}")
print("ALL PASS" if ok_all else "SOME TESTS FAILED")
