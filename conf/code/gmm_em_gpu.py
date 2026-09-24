"""gmm_em_gpu.py -- float64 CUDA port of Demo/t2_gmm.py :: fit_gmm_em.

Demo/t2_gmm.py is READ-ONLY (01_RULES).  This file reproduces fit_gmm_em line for line on the GPU:
same signature, same returned dict, same numpy Generator consumed in the same draw order
(rng.choice once at init, then one rng.integers(n) per re-seed, in k order inside it order), so the
same seed gives the same initialisation and -- as long as no re-seed decision flips -- the same path.

Everything numeric is complex128 / float64.  A float32 port would NOT reproduce the CPU fit.

Deliberate structural choices (all of them keep the CPU expression, they only move it to the device):
  * the E-step is chunked over k purely to bound the (chunk, n, N) temporary; the per-k expression
    X @ Linv[k].T is unchanged.
  * nk is pulled to the host once per iteration so the starved-component branch and the scalar
    divisions use exactly the same float64 scalars numpy would use (and so the re-seed RNG draws
    happen in the same order without 512 device syncs).
Not reproduced bit-for-bit: GEMM / reduction order.  cuBLAS sums differently from OpenBLAS, so
agreement is to float64 round-off accumulated over the EM path, not to the last bit.  See the
equivalence test in code/gmm_gpu_equiv.py.
"""
import numpy as np
import torch


def _host(t):
    """Tensor -> a numpy array that OWNS its memory.  t.cpu() is a no-op when t is already on the CPU,
    so t.cpu().numpy() would return a VIEW that keeps tracking later in-place writes to t -- the
    best-validation snapshot would then silently become the final-iteration parameters.  On CUDA .cpu()
    always copies, which is why that defect is invisible on the GPU; numpy's covs.copy() in
    t2_gmm.fit_gmm_em always copies, so a copy here is what reproduces it on every device."""
    return np.array(t.detach().cpu())


def _loglik_t(X, logpi, covs, N, budget=1.5e9):
    """(n,K) torch: log pi_k + log CN(x_i; 0, C_k).  Mirrors t2_gmm._loglik."""
    n = X.shape[0]; K = covs.shape[0]
    L = torch.linalg.cholesky(covs)
    Linv = torch.linalg.inv(L)
    logdet = 2 * torch.log(torch.diagonal(L, dim1=1, dim2=2).real).sum(1)
    lw = torch.empty((n, K), dtype=torch.float64, device=X.device)
    chunk = max(1, int(budget // (n * N * 16)))
    for a in range(0, K, chunk):
        b = min(a + chunk, K)
        Z = torch.matmul(X, Linv[a:b].mT)                      # rows L_k^-1 x_i, batched over k
        lw[:, a:b] = -(Z.real ** 2 + Z.imag ** 2).sum(-1).mT
    return lw + logpi - logdet - N * np.log(np.pi)


def _kron_mstep_batched(Xt, gam, nk, covs, Tk, Nr, Nt, floor, cbar, eyeNr, eyeNt, chunk=16384):
    """All-K kron M-step through the weighted scatter matrices (see fit_gmm_em_gpu, batched=True).  Updates covs and
    Tk in place for the components with nk >= 4 (the rest are reseeded by the caller)."""
    n, N = Xt.shape
    K = gam.shape[1]
    Sre = torch.zeros((K, N * N), dtype=torch.float64, device=Xt.device)
    Sim = torch.zeros_like(Sre)
    for a in range(0, n, chunk):                                  # S_k = sum_i gam_ik x_i x_i^H, chunked over samples
        x = Xt[a:a + chunk]
        XX = (x[:, :, None] * x.conj()[:, None, :]).reshape(x.shape[0], N * N)
        gT = gam[a:a + chunk].mT
        Sre += gT @ XX.real
        Sim += gT @ XX.imag
    S4 = torch.complex(Sre, Sim).reshape(K, Nt, Nr, Nt, Nr)       # S4[k,c,a,d,b] = S_k[a + Nr c, b + Nr d]
    ok = torch.as_tensor(nk >= 4, device=Xt.device)
    nkt = torch.as_tensor(np.maximum(nk, 1.0), device=Xt.device)  # starved rows are discarded below
    T = Tk.clone()
    for _ in range(3):
        W = torch.linalg.inv(T).mT                                # T^-T
        R = torch.einsum("kcd,kcadb->kab", W, S4) / (nkt * Nt)[:, None, None]
        R = 0.5 * (R + R.mH) + floor * cbar * eyeNr
        Tt = torch.einsum("kab,kdbca->kcd", torch.linalg.inv(R), S4) / (nkt * Nr)[:, None, None]
        T = Tt.mT; T = 0.5 * (T + T.mH)
        c = torch.diagonal(T, dim1=1, dim2=2).real.sum(1) / Nt
        T = T / c[:, None, None] + floor * eyeNt; R = R * c[:, None, None]
    new = torch.einsum("kij,kab->kiajb", T, R).reshape(K, Nt * Nr, Nt * Nr)   # kron(T_k, R_k)
    covs[ok] = new[ok]
    Tk[ok] = T[ok]


def fit_gmm_em_gpu(X, K, rng, n_iter=500, tol=1e-6, floor=1e-4, kappa=0.0, struct="full", dims=None,
                   Xval=None, val_every=10, patience=40, log=None, device="cuda", sparse_tol=None, batched=False):
    """Drop-in for t2_gmm.fit_gmm_em.  X (n,N) complex128 numpy (or torch) zero-mean samples.

    sparse_tol (opt-in, NEXT_EXPERIMENTS_B32e4 speed-up, default None = the exact path, unchanged): in the kron
    M-step, component k's flip-flop sweeps run only over the samples with responsibility gam[i, k] > sparse_tol
    instead of all n.  nk (the normaliser), the E-step, reseeding, the stopping rules and the RNG draws are
    untouched; the only change is that terms with gam < sparse_tol are left out of the weighted sums.  The largest
    dropped responsibility mass (sum of the skipped gam / nk, over components and iterations) is returned as
    out["sparse_max_dropped"] so the approximation is on record for every fit.

    batched (opt-in, kron only, default False = the exact per-component loop): the SAME M-step computed through the
    per-component weighted scatter S_k = sum_i gam_ik x_i x_i^H (one chunked matmul for all k), after which the three
    flip-flop sweeps run for all K components at once on S_k:  R_k = sum_cd W_k[c,d] S_k[(a,c),(b,d)] / (nk Nt),
    W_k = T_k^-T, and T_k^T = sum_ab Rinv_k[a,b] S_k[(b,d),(a,c)] / (nk Nr) -- algebraically identical to the loop
    (only the order of summation differs).  Starved components are reseeded afterwards in k order with the same RNG
    draws, so the random stream is unchanged."""
    dev = torch.device(device)
    Xt = torch.as_tensor(np.asarray(X, np.complex128), device=dev)
    n, N = Xt.shape
    Chat = Xt.mT @ Xt.conj() / n
    cbar = torch.trace(Chat).real.item() / N
    I = torch.eye(N, dtype=torch.complex128, device=dev)
    if struct == "kron":
        Nr, Nt = dims; assert Nr * Nt == N
        Hs = Xt.reshape(n, Nt, Nr).permute(0, 2, 1).contiguous()          # H_i (Nr x Nt), column-major vec
        H2 = Hs.permute(0, 2, 1).reshape(n * Nt, Nr).contiguous()
        H3 = Hs.reshape(n * Nr, Nt).contiguous()
        H2c = H2.conj().contiguous(); H3ch = H3.conj().mT.contiguous()
        eyeNr = torch.eye(Nr, dtype=torch.complex128, device=dev)
        eyeNt = torch.eye(Nt, dtype=torch.complex128, device=dev)

    def seed_cov(i):
        s = Xt[i]
        return 0.5 * Chat + 0.5 * (N * cbar / torch.vdot(s, s).real.item()) * torch.outer(s, s.conj())

    covs = torch.stack([seed_cov(int(i)) for i in rng.choice(n, K, replace=False)])
    logpi_np = np.full(K, -np.log(K))
    logpi = torch.as_tensor(logpi_np, device=dev)
    ll = []; n_reseed = 0
    Tk = torch.eye(Nt, dtype=torch.complex128, device=dev).expand(K, Nt, Nt).clone() if struct == "kron" else None
    max_dropped = 0.0
    best = dict(ll_val=-np.inf, it=0, pi=np.exp(logpi_np), covs=_host(covs))
    llv = []
    Xv = torch.as_tensor(np.asarray(Xval, np.complex128), device=dev) if Xval is not None else None

    for it in range(n_iter):
        lw = _loglik_t(Xt, logpi, covs, N)
        lse = torch.logsumexp(lw, 1)
        ll.append(float(lse.mean()))
        if Xv is not None and it % val_every == 0:
            v = float(torch.logsumexp(_loglik_t(Xv, logpi, covs, N), 1).mean())
            llv.append((it, v))
            if v > best["ll_val"]:
                best = dict(ll_val=v, it=it, pi=np.exp(logpi_np), covs=_host(covs))
            elif it - best["it"] >= patience:
                break
        if log is not None and it % 25 == 0:
            log(f"    it {it:>3} ll/sample = {ll[-1]:.4f}" + (f"  val {llv[-1][1]:.4f}" if llv else ""))
        if it >= 20 and ll[-1] - ll[-2] < tol * abs(ll[-1]):
            break
        gam = torch.exp(lw - lse[:, None])
        nk_t = gam.sum(0)
        nk = _host(nk_t)                                         # host copy: same float64 scalars as numpy uses
        if batched and struct == "kron":
            _kron_mstep_batched(Xt, gam, nk, covs, Tk, Nr, Nt, floor, cbar, eyeNr, eyeNt)
            for k in range(K):                                   # reseed starved components in k order (same RNG)
                if nk[k] < 4:
                    covs[k] = seed_cov(int(rng.integers(n))); nk[k] = max(nk[k], 1.0); n_reseed += 1
                    Tk[k] = eyeNt
            logpi_np = np.log(nk / nk.sum())
            logpi = torch.as_tensor(logpi_np, device=dev)
            continue
        for k in range(K):
            if nk[k] < (N if struct == "full" else 4):           # starved component -> re-seed
                covs[k] = seed_cov(int(rng.integers(n))); nk[k] = max(nk[k], 1.0); n_reseed += 1
                if struct == "kron":
                    Tk[k] = eyeNt
                continue
            g = gam[:, k]
            if struct == "full":
                Xw = Xt * torch.sqrt(g)[:, None]
                S = Xw.mT @ Xw.conj() / nk[k]
                S = (nk[k] * S + kappa * Chat) / (nk[k] + kappa)
                covs[k] = 0.5 * (S + S.mH) + floor * cbar * I
            else:
                T = Tk[k]
                if sparse_tol is None:                                            # exact path (default)
                    Hk, gk, H2ck, H3chk, m = Hs, g, H2c, H3ch, n
                else:                                                             # opt-in: active samples only
                    sel = torch.nonzero(g > sparse_tol).flatten()
                    Hk, gk, m = Hs[sel], g[sel], int(sel.numel())
                    H2ck = Hk.permute(0, 2, 1).reshape(m * Nt, Nr).conj()
                    H3chk = Hk.reshape(m * Nr, Nt).conj().mT
                    max_dropped = max(max_dropped, float((nk_t[k] - gk.sum()) / nk_t[k]))
                for _ in range(3):
                    A = (Hk @ torch.linalg.inv(T).mT) * gk[:, None, None]         # g_i H_i T^-T
                    R = A.permute(0, 2, 1).reshape(m * Nt, Nr).mT @ H2ck / (nk[k] * Nt)
                    R = 0.5 * (R + R.mH) + floor * cbar * eyeNr
                    B = (torch.linalg.inv(R) @ Hk) * gk[:, None, None]            # g_i R^-1 H_i
                    Tt = H3chk @ B.reshape(m * Nr, Nt) / (nk[k] * Nr)
                    T = Tt.mT; T = 0.5 * (T + T.mH)
                    c = torch.trace(T).real / Nt
                    T = T / c + floor * eyeNt; R = R * c
                Tk[k] = T; covs[k] = torch.kron(T.contiguous(), R.contiguous())
        logpi_np = np.log(nk / nk.sum())
        logpi = torch.as_tensor(logpi_np, device=dev)

    out = dict(pi=np.exp(logpi_np), covs=_host(covs), ll=np.array(ll), n_iter=len(ll),
               n_reseed=n_reseed, Chat=_host(Chat), it_best=len(ll) - 1, ll_val=np.nan,
               sparse_tol=(np.nan if sparse_tol is None else float(sparse_tol)), sparse_max_dropped=max_dropped)
    if Xval is not None:
        out.update(pi=best["pi"], covs=best["covs"], it_best=best["it"], ll_val=best["ll_val"],
                   ll_val_traj=np.array(llv))
    return out


def _demo():
    """Self-check: tiny problem, GPU vs the READ-ONLY CPU fit_gmm_em, same seed.  Both structs."""
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Demo"))
    from t2_gmm import fit_gmm_em
    rs = np.random.default_rng(0)
    Nr, Nt = 4, 2; N = Nr * Nt; n = 3000
    C0 = [a @ a.conj().T + np.eye(N) for a in
          (rs.standard_normal((N, 2)) + 1j * rs.standard_normal((N, 2)) for _ in range(3))]
    ks = rs.integers(3, size=n)
    X = np.stack([np.linalg.cholesky(C0[k]) @ (rs.standard_normal(N) + 1j * rs.standard_normal(N)) / np.sqrt(2)
                  for k in ks])
    Xv = X[:500]
    for struct in ("full", "kron"):
        a = fit_gmm_em(X, 4, np.random.default_rng(7), n_iter=60, kappa=8.0, struct=struct,
                       dims=(Nr, Nt), Xval=Xv)
        b = fit_gmm_em_gpu(X, 4, np.random.default_rng(7), n_iter=60, kappa=8.0, struct=struct,
                           dims=(Nr, Nt), Xval=Xv)
        dv = abs(a["ll_val"] - b["ll_val"]) / abs(a["ll_val"])
        dp = np.abs(a["pi"] - b["pi"]).max() / np.abs(a["pi"]).max()
        dc = np.abs(a["covs"] - b["covs"]).max() / np.abs(a["covs"]).max()
        print(f"{struct}: n_iter {a['n_iter']}/{b['n_iter']}  it_best {a['it_best']}/{b['it_best']}  "
              f"reseed {a['n_reseed']}/{b['n_reseed']}  d_ll_val {dv:.3e}  d_pi {dp:.3e}  d_cov {dc:.3e}")
        assert a["n_iter"] == b["n_iter"] and a["it_best"] == b["it_best"] and a["n_reseed"] == b["n_reseed"]
        assert dv < 1e-10 and dp < 1e-8 and dc < 1e-8, (dv, dp, dc)
    print("gmm_em_gpu self-check OK")


if __name__ == "__main__":
    _demo()
