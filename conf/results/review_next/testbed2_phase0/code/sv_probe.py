# Critic supplement: clustered extended Saleh-Valenzuela narrowband model (El Ayach et al. TWC 2014; Alkhateeb et al. JSTSP 2014)
# through the SAME headroom/secondary code as tb2/rt/ana.py (pilot query, K1, MC-LO with phases redrawn, EM-GMM GPU port).
import sys, time, json, argparse, numpy as np, torch
sys.path.insert(0, "/home/HTJ/t2/conf/code"); sys.path.insert(0, "/home/HTJ/t2/Demo")
from emt import fit_gmm_em_t
ap = argparse.ArgumentParser(); ap.add_argument("--src", default="d2"); ap.add_argument("--Nr", type=int, default=8); ap.add_argument("--Nt", type=int, default=4)
ap.add_argument("--ntr", type=int, default=40000); ap.add_argument("--nte", type=int, default=2000); ap.add_argument("--R", type=int, default=400)
ap.add_argument("--Ks", default="16,64,256"); ap.add_argument("--label", default=None); ap.add_argument("--nval", type=int, default=4000)
ap.add_argument("--ncl", default="8"); ap.add_argument("--nray", type=int, default=10); ap.add_argument("--spread", type=float, default=7.5)
ap.add_argument("--cpow", default="equal"); ap.add_argument("--bs_sector", type=float, default=60.); ap.add_argument("--seed", type=int, default=1)
A = ap.parse_args(); Nr, Nt = A.Nr, A.Nt; N = Nr * Nt; R = A.R; dev = "cuda"
vec = lambda H: H.transpose(0, 2, 1).reshape(len(H), -1)
out = dict(label=A.label or A.src, Nr=Nr, Nt=Nt, ntr=A.ntr, nte=A.nte, R=R, args=vars(A))
er = lambda C: (lambda l: float(l.sum() ** 2 / (l ** 2).sum()))(np.linalg.eigvalsh(C))
steer = lambda s, M: np.exp(1j * np.pi * s[..., None] * np.arange(M))
def sv_draw(rng, n):
    """per sample: Ncl clusters, cluster-mean AoA ~ U(+-bs_sector) (BS 120-deg sector), cluster-mean AoD ~ U[-pi,pi) (UE yaw-only uniform),
    Nray rays/cluster with Laplacian offsets (std = spread deg) on both sides, ray gains CN(0, g_c/Nray); per-sample sum|a|^2 = 1."""
    lo, hi = [int(x) for x in (A.ncl.split("-") * 2)[:2]]; P = hi * A.nray
    L = rng.integers(lo, hi + 1, n); cm = np.arange(hi)[None] < L[:, None]
    mA = np.deg2rad(A.bs_sector) * rng.uniform(-1, 1, (n, hi)); mD = rng.uniform(-np.pi, np.pi, (n, hi))
    b = np.deg2rad(A.spread) / np.sqrt(2); th = mA[..., None] + rng.laplace(0, b, (n, hi, A.nray)); ph = mD[..., None] + rng.laplace(0, b, (n, hi, A.nray))
    g = np.ones((n, hi)) if A.cpow == "equal" else np.exp(-np.arange(1, hi + 1) / 2.0)[None].repeat(n, 0)   # 'exp': D2's tau=2 profile
    g = g * cm; g = g / g.sum(1, keepdims=True)
    a = np.sqrt(g[..., None] / A.nray) * (rng.standard_normal((n, hi, A.nray)) + 1j * rng.standard_normal((n, hi, A.nray))) / np.sqrt(2)
    a = a.reshape(n, P); a = a / np.sqrt((np.abs(a) ** 2).sum(1, keepdims=True))
    return a, np.sin(th).reshape(n, P), np.sin(ph).reshape(n, P), L
def Vof(sr, st): return (steer(st, Nt)[..., :, None] * steer(sr, Nr)[..., None, :]).reshape(*sr.shape, N)   # kron(a_t, a_r) = column-major vec
rng = np.random.default_rng(A.seed); t0 = time.time()
if A.src == "d2":
    import d2
    g = d2.D2Gen("S2", Nr, Nt); Xtr = g.sample_vecs(rng, A.ntr); Hc = []; pw = []; Ce = []
    for b in range(A.nte):
        Hs, (th, ph, p) = g.sample_angles(rng, R + 1); Hc.append(vec(Hs)); pw.append(p)
        V = Vof(np.sin(th), -np.sin(ph)); Ce.append((V.T * p) @ V.conj())
    Hc = np.stack(Hc); Ce = np.stack(Ce)   # D2: H = sum alpha a_r(unnorm) conj(a_t(unnorm))^T
    out.update(clusters_mean=float(np.mean([len(p) for p in pw])), paths_eff=float(np.mean([1 / (p ** 2).sum() for p in pw])))
else:
    X = np.empty((A.ntr, N), complex)
    for i0 in range(0, A.ntr, 5000):
        a, sr, st, _ = sv_draw(rng, min(5000, A.ntr - i0)); X[i0:i0 + len(a)] = np.einsum("nl,nlk->nk", a, Vof(sr, st))
    gen_s = (time.time() - t0) / A.ntr; Xtr = X
    a, sr, st, L = sv_draw(rng, A.nte); V = Vof(sr, st); h0 = np.einsum("nl,nlk->nk", a, V)
    Hc = np.empty((A.nte, R + 1, N), complex); Hc[:, 0] = h0
    for b0 in range(0, A.nte, 100):
        bb = slice(b0, b0 + 100); ph_ = np.exp(2j * np.pi * rng.random((len(a[bb]), R, a.shape[1])))
        Hc[bb, 1:] = np.einsum("brl,blk->brk", np.abs(a[bb])[:, None] * ph_, V[bb])
    p = np.abs(a) ** 2; Ce = np.einsum("bl,bli,blj->bij", p, V, V.conj())
    pc = p.reshape(A.nte, -1, A.nray).sum(2)
    out.update(clusters_mean=float(L.mean()), rays_per_sample=float((p > 0).sum(1).mean()), paths_eff=float((1 / (p ** 2).sum(1)).mean()),
               clusters_eff=float((1 / (pc ** 2).sum(1)).mean()), gen_ms_per_sample=1e3 * gen_s, gen_min_for_182920=gen_s * 182920 / 60)
s = np.sqrt(N / (np.abs(Xtr) ** 2).sum(1).mean()); Xtr = Xtr * s; Hc = Hc * s; h = Hc[:, 0]; Ce = Ce * s ** 2
Chat = Xtr.T @ Xtr.conj() / len(Xtr); Hm = Xtr.reshape(-1, Nt, Nr).transpose(0, 2, 1)
out.update(erank_C=er(Chat))
lam = np.linalg.eigvalsh(Ce)[:, ::-1]; out["cond_erank"] = float(np.mean(lam.sum(1) ** 2 / (lam ** 2).sum(1)))
out["P_rank90_ge3"] = float(np.mean((np.cumsum(lam, 1) / lam.sum(1, keepdims=True) < 0.9).sum(1) + 1 >= 3))
Fr = np.fft.fft(np.eye(Nr)) / np.sqrt(Nr); Ft = np.fft.fft(np.eye(Nt)) / np.sqrt(Nt)
E = np.sort(np.abs(np.einsum("ri,bij,jt->brt", Fr.conj().T, Hm, Ft)).reshape(len(Hm), -1) ** 2, 1)[:, ::-1]; E = E / E.sum(1, keepdims=True)
out.update(top4=float(E[:, :4].sum(1).mean()), top8=float(E[:, :8].sum(1).mean()))
sv_ = np.linalg.svd(Hm[:20000], compute_uv=False) ** 2
for snr in (-3, 3): out[f"outage_{snr:+d}dB"] = float(np.mean(np.log2(1 + sv_ / 10 ** (-snr / 10)).sum(1) < 4))
def nnd(Q, T):
    Qt, Tt = torch.as_tensor(Q, device=dev), torch.as_tensor(T, device=dev); d = []
    for i in range(0, len(Qt), 500): d.append(torch.cdist(torch.view_as_real(Qt[i:i + 500]).flatten(1), torch.view_as_real(Tt).flatten(1)).min(1).values)
    return (torch.cat(d) / torch.linalg.norm(Qt, dim=1)).cpu().numpy()
d = nnd(h, Xtr); out.update(leak_iid_med=float(np.median(d)), leak_iid_lt01=float(np.mean(d < 0.1)))
print(json.dumps(out), flush=True)
Cc = np.einsum("bri,brj->bij", Hc[:, 1:], Hc[:, 1:].conj()) / R
reg = lambda C: C + 1e-3 * np.eye(N) * (np.trace(C, axis1=1, axis2=2).real / N)[:, None, None]
Cc, Ce = reg(Cc), reg(Ce)
gm = {}; Ks = [int(k) for k in A.Ks.split(",")]; nf = A.ntr - A.nval
for K in Ks:
    t1 = time.time(); r = fit_gmm_em_t(Xtr[:nf], K, np.random.default_rng(K), n_iter=200, Xval=Xtr[nf:], patience=40)
    gm[K] = (r["covs"], r["pi"]); out[f"fit_K{K}"] = dict(sec=round(time.time() - t1, 1), it_best=r["it_best"], n_iter=r["n_iter"], reseed=r["n_reseed"], ll_val=r["ll_val"])
    print(f"  GMM K={K} fit {time.time()-t1:.0f}s it_best {r['it_best']} n_iter {r['n_iter']} reseed {r['n_reseed']}", flush=True)
tt = lambda x: torch.as_tensor(x, device=dev); rng = np.random.default_rng(99); I = np.eye(N)
for snr in (-3, 3):
    nu = 10 ** (-snr / 10) / Nt
    q = h + np.sqrt(nu / 2) * (rng.standard_normal(h.shape) + 1j * rng.standard_normal(h.shape))
    est = {"K1": q @ np.linalg.solve(Chat + nu * I, Chat).T, "LO": np.einsum("bij,bj->bi", Cc @ np.linalg.inv(Cc + nu * I), q),
           "LOx": np.einsum("bij,bj->bi", Ce @ np.linalg.inv(Ce + nu * I), q)}
    for K, (C, w) in gm.items():
        Ct = tt(C); At = Ct + nu * tt(I); Ai = torch.linalg.inv(At); ld = torch.linalg.slogdet(At)[1]; qt = tt(q)
        ll = -torch.einsum("bi,kij,bj->bk", qt.conj(), Ai, qt).real - ld[None] + torch.log(tt(w))[None]
        gam = torch.softmax(ll, 1).to(qt.dtype)
        est[f"GMM{K}"] = torch.einsum("bk,kbi->bi", gam, torch.einsum("kij,bj->kbi", Ct @ Ai, qt)).cpu().numpy()
    nm = {k: float((np.abs(v - h) ** 2).sum() / (np.abs(h) ** 2).sum()) for k, v in est.items()}
    clo = {K: (nm["K1"] - nm[f"GMM{K}"]) / (nm["K1"] - nm["LO"]) for K in gm}
    # bootstrap 95% CI of closed fraction at K=64 (test-sample resampling)
    e = {k: (np.abs(v - h) ** 2).sum(1) for k, v in est.items()}; hh = (np.abs(h) ** 2).sum(1); rb = np.random.default_rng(3); bs = []
    for _ in range(500):
        ix = rb.integers(0, len(h), len(h)); f = lambda k: e[k][ix].sum() / hh[ix].sum(); bs.append((f("K1") - f("GMM64")) / (f("K1") - f("LO")))
    out[f"all_{snr:+d}dB"] = dict(nmse=nm, closed=clo, ci64=list(np.percentile(bs, [2.5, 97.5])), gap_abs=nm["K1"] - nm["LO"], gap_db=10 * np.log10(nm["K1"] / nm["LO"]))
    print(f"{out['label']:12s} {snr:+d}dB NMSE " + " ".join(f"{k} {v:.4f}" for k, v in nm.items()) + " | closed " + " ".join(f"K{K} {c:.2f}" for K, c in clo.items())
          + f" [K64 CI {bs and np.percentile(bs,2.5):.2f},{np.percentile(bs,97.5):.2f}] | gap {nm['K1']-nm['LO']:.4f} ({10*np.log10(nm['K1']/nm['LO']):.1f} dB)", flush=True)
json.dump(out, open(f"res_{out['label']}.json", "w"), indent=1, default=float)
