# Faithful torch (complex128, GPU) port of Demo/t2_gmm.fit_gmm_em, struct='full', kappa=0 -- same seeding/reseed/early-stop logic, same numpy rng calls.
import numpy as np, torch
def _loglik(X, logpi, covs, chunk=32):
    n, N = X.shape; L = torch.linalg.cholesky(covs); Linv = torch.linalg.solve_triangular(L, torch.eye(N, dtype=X.dtype, device=X.device).expand_as(L), upper=False)
    logdet = 2 * torch.log(torch.diagonal(L, dim1=1, dim2=2).real).sum(1); lw = torch.empty(n, len(covs), dtype=torch.float64, device=X.device)
    for k0 in range(0, len(covs), chunk):
        Z = torch.einsum("ni,kji->knj", X, Linv[k0:k0 + chunk])                  # rows L_k^-1 x_i
        lw[:, k0:k0 + chunk] = -(Z.real ** 2 + Z.imag ** 2).sum(2).T
    return lw + logpi[None] - logdet[None] - N * np.log(np.pi)
def fit_gmm_em_t(X, K, rng, n_iter=500, tol=1e-6, floor=1e-4, Xval=None, val_every=10, patience=40, dev="cuda", chunk=32):
    n, N = X.shape; Xn = X; X = torch.as_tensor(X, dtype=torch.complex128, device=dev)
    Xv = None if Xval is None else torch.as_tensor(Xval, dtype=torch.complex128, device=dev)
    Chat = X.T @ X.conj() / n; cbar = torch.trace(Chat).real.item() / N; I = torch.eye(N, dtype=X.dtype, device=dev)
    def seed_cov(i):
        s = X[i]; return 0.5 * Chat + 0.5 * (N * cbar / torch.vdot(s, s).real) * torch.outer(s, s.conj())
    covs = torch.stack([seed_cov(int(i)) for i in rng.choice(n, K, replace=False)]); logpi = torch.full((K,), -np.log(K), dtype=torch.float64, device=dev)
    ll = []; n_reseed = 0; best = dict(ll_val=-np.inf, it=0, pi=logpi.exp(), covs=covs.clone()); llv = []
    for it in range(n_iter):
        lw = _loglik(X, logpi, covs, chunk); lse = torch.logsumexp(lw, 1); ll.append(float(lse.mean()))
        if Xv is not None and it % val_every == 0:
            v = float(torch.logsumexp(_loglik(Xv, logpi, covs, chunk), 1).mean()); llv.append((it, v))
            if v > best["ll_val"]: best = dict(ll_val=v, it=it, pi=logpi.exp(), covs=covs.clone())
            elif it - best["it"] >= patience: break
        if it >= 20 and ll[-1] - ll[-2] < tol * abs(ll[-1]): break
        gam = torch.exp(lw - lse[:, None]); nk = gam.sum(0)
        new = torch.empty_like(covs)
        for k0 in range(0, K, chunk):
            G = gam[:, k0:k0 + chunk].T.to(X.dtype)                                   # (c, n)
            S = torch.einsum("kn,ni,nj->kij", G, X, X.conj()) / nk[k0:k0 + chunk, None, None]
            new[k0:k0 + chunk] = 0.5 * (S + S.conj().transpose(1, 2)) + floor * cbar * I
        starved = (nk < N).cpu().numpy(); nk = nk.clone()
        for k in np.flatnonzero(starved):                                             # same order & rng calls as the numpy loop
            new[k] = seed_cov(int(rng.integers(n))); nk[k] = max(float(nk[k]), 1.0); n_reseed += 1
        covs = new; logpi = torch.log(nk / nk.sum())
    out = dict(pi=logpi.exp(), covs=covs, n_iter=len(ll), n_reseed=n_reseed, it_best=len(ll) - 1)
    if Xv is not None: out.update(pi=best["pi"], covs=best["covs"], it_best=best["it"], ll_val=best["ll_val"])
    return {k: (v.cpu().numpy() if torch.is_tensor(v) else v) for k, v in out.items()}
if __name__ == "__main__":   # check: port == numpy reference on a small D2 problem
    import sys, time; sys.path.insert(0, "/home/HTJ/t2/conf/code"); sys.path.insert(0, "/home/HTJ/t2/Demo")
    import d2; from t2_gmm import fit_gmm_em
    X = d2.D2Gen("S2", 8, 4).sample_vecs(np.random.default_rng(1), 6000)
    t0 = time.time(); r0 = fit_gmm_em(X[:5000], 16, np.random.default_rng(16), n_iter=60, Xval=X[5000:], patience=40); t1 = time.time()
    r1 = fit_gmm_em_t(X[:5000], 16, np.random.default_rng(16), n_iter=60, Xval=X[5000:], patience=40); t2 = time.time()
    d = np.abs(r0["covs"] - r1["covs"]).max() / np.abs(r0["covs"]).max(); print(f"cpu {t1-t0:.1f}s gpu {t2-t1:.1f}s it_best {r0['it_best']} {r1['it_best']} reseed {r0['n_reseed']} {r1['n_reseed']} rel maxdiff covs {d:.2e} pi {np.abs(r0['pi']-r1['pi']).max():.2e}")
    assert d < 1e-6 and r0["it_best"] == r1["it_best"]
