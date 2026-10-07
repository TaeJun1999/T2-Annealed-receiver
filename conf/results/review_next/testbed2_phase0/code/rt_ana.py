# GMM-headroom + secondary channel statistics for one config (RT npz or D2). Pilot query / estimators / LO exactly as verify/gmm_headroom.py.
import sys, time, json, argparse, numpy as np, torch
sys.path.insert(0, "/home/HTJ/t2/conf/code"); sys.path.insert(0, "/home/HTJ/t2/Demo")
from emt import fit_gmm_em_t
ap = argparse.ArgumentParser(); ap.add_argument("--src", default="d2"); ap.add_argument("--Nr", type=int, default=8); ap.add_argument("--Nt", type=int, default=4)
ap.add_argument("--ntr", type=int, default=40000); ap.add_argument("--nte", type=int, default=2000); ap.add_argument("--R", type=int, default=400)
ap.add_argument("--Ks", default="16,64,256"); ap.add_argument("--label", default=None); ap.add_argument("--block", type=float, default=10.); ap.add_argument("--nlos", action="store_true"); ap.add_argument("--merge", type=float, default=0.005); ap.add_argument("--nval", type=int, default=4000); ap.add_argument("--n_iter", type=int, default=200)
A = ap.parse_args(); Nr, Nt = A.Nr, A.Nt; N = Nr * Nt; R = A.R; dev = "cuda"
vec = lambda H: H.transpose(0, 2, 1).reshape(len(H), -1)            # column-major
out = dict(label=A.label or A.src, Nr=Nr, Nt=Nt, ntr=A.ntr, nte=A.nte, R=R)
er = lambda C: (lambda l: float(l.sum() ** 2 / (l ** 2).sum()))(np.linalg.eigvalsh(C))
if A.src == "d2":
    import d2
    g = d2.D2Gen("S2", Nr, Nt); rng = np.random.default_rng(1)
    Xtr = g.sample_vecs(rng, A.ntr); Hc = []; Pte = []
    for b in range(A.nte):
        Hs, ang = g.sample_angles(rng, R + 1); Hc.append(vec(Hs)); Pte.append(ang[2])
    Hc = np.stack(Hc); los_te = np.zeros(A.nte, bool)
    pw = [p / p.sum() for p in Pte]; out.update(los_frac=0.0, paths_mean=float(np.mean([len(p) for p in pw])),
        paths_eff=float(np.mean([1 / (p ** 2).sum() for p in pw])), paths_20dB=float(np.mean([(p > p.max() / 100).sum() for p in pw])))
    Vexact = None
else:
    G = dict(np.load(A.src))
    if A.nlos:   # NLOS-only population (drop every block with a LOS path)
        m = ~G["los"]; G = {k: (v[m] if (hasattr(v, "shape") and v.ndim and len(v) == len(m)) else v) for k, v in G.items()}
        G["sec_per_valid"] = G["sec_per_valid"] / m.mean(); G["valid_frac"] = G["valid_frac"] * m.mean()
    a = G["a"]; n_all = len(a); need = A.ntr + A.nte; assert n_all >= need, (n_all, need)
    ry = np.random.default_rng(7); yaw = ry.uniform(-np.pi, np.pi, n_all)                     # UE yaw ~ U[-pi, pi), UE ULA horizontal (no tilt/slant)
    bore = G["bores"][G["site"]]; ub = np.stack([-np.sin(bore), np.cos(bore), 0 * bore], 1)  # BS ULA horizontal, perpendicular to site boresight
    uu = np.stack([np.cos(yaw), np.sin(yaw), 0 * yaw], 1)
    dvec = lambda th, ph: np.stack([np.sin(th) * np.cos(ph), np.sin(th) * np.sin(ph), np.cos(th)], -1)
    sr = np.einsum("nlk,nk->nl", dvec(G["thb"], G["phb"]), ub); st = np.einsum("nlk,nk->nl", dvec(G["thu"], G["phu"]), uu)
    p = np.abs(a) ** 2; a = a / np.sqrt(p.sum(1, keepdims=True)); p = p / p.sum(1, keepdims=True)      # pathloss/shadowing removed per sample
    V = np.exp(1j * np.pi * st[..., None] * np.arange(Nt))[..., :, None] * np.exp(1j * np.pi * sr[..., None] * np.arange(Nr))[..., None, :]
    V = V.reshape(n_all, a.shape[1], N)                                                      # v_l = kron(a_t, a_r): column-major vec of a_r a_t^T
    X = np.einsum("nl,nlk->nk", a, V); Xtr = X[:A.ntr]; te = np.arange(A.ntr, need)
    rng = np.random.default_rng(1); Hc = np.empty((A.nte, R + 1, N), complex); Hc[:, 0] = X[te]
    for b0 in range(0, A.nte, 250):
        bb = te[b0:b0 + 250]; ph = np.exp(2j * np.pi * rng.random((len(bb), R, a.shape[1])))
        Hc[b0:b0 + 250, 1:] = np.einsum("brl,blk->brk", np.abs(a[bb])[:, None] * ph, V[bb])
    los_te = G["los"][te]; Vexact = (V[te], p[te])
    # LOm: paths whose steering coordinates coincide within `merge` on BOTH sides (e.g. LOS + ground bounce) are unresolvable by the arrays;
    # merge them COHERENTLY (true relative phase kept) into one latent path, then treat merged paths as phase-free (sensitivity variant of LO).
    Cm = np.zeros((A.nte, N, N), complex); nm_paths = []
    for i, b in enumerate(te):
        cl = []
        for l in np.flatnonzero(p[b] > 0):
            for c in cl:
                if abs(sr[b, l] - sr[b, c[0]]) < A.merge and abs(st[b, l] - st[b, c[0]]) < A.merge: c[1] += a[b, l]; break
            else: cl.append([l, a[b, l]])
        Vm = V[b, [c[0] for c in cl]]; pm = np.array([abs(c[1]) ** 2 for c in cl]); nm_paths.append(len(cl))
        Cm[i] = (Vm.T * pm) @ Vm.conj()
    out["merged_paths_mean"] = float(np.mean(nm_paths))
    nz = p > 0; out.update(los_frac=float(G["los"].mean()), paths_mean=float(nz.sum(1).mean()), paths_eff=float((1 / (p ** 2).sum(1)).mean()),
        paths_20dB=float((p > p.max(1, keepdims=True) / 100).sum(1).mean()), n_sites=int(len(G["bores"])),
        gen_ms_per_valid=float(1e3 * G["sec_per_valid"]), valid_frac=float(G["valid_frac"]),
        gen_h_for_183920=float(G["sec_per_valid"] * 183920 / 3600))
s = np.sqrt(N / (np.abs(Xtr) ** 2).sum(1).mean()); Xtr = Xtr * s; Hc = Hc * s; h = Hc[:, 0]
# ---------------- secondary statistics
Chat = Xtr.T @ Xtr.conj() / len(Xtr); Hm = Xtr.reshape(-1, Nt, Nr).transpose(0, 2, 1)
Rt = np.einsum("bij,bik->jk", Hm.conj(), Hm) / len(Hm) / Nr; Rr = np.einsum("bij,bkj->ik", Hm, Hm.conj()) / len(Hm) / Nt
out.update(erank_C=er(Chat), erank_Rr=er(Rr), erank_Rt=er(Rt))
Fr = np.fft.fft(np.eye(Nr)) / np.sqrt(Nr); Ft = np.fft.fft(np.eye(Nt)) / np.sqrt(Nt)
E = np.sort(np.abs(np.einsum("ri,bij,jt->brt", Fr.conj().T, Hm, Ft)).reshape(len(Hm), -1) ** 2, 1)[:, ::-1]; E = E / E.sum(1, keepdims=True)
out.update(top4=float(E[:, :4].sum(1).mean()), top8=float(E[:, :8].sum(1).mean()))
sv = np.linalg.svd(Hm[:20000], compute_uv=False) ** 2
for snr in (-3, 3): out[f"outage_{snr:+d}dB"] = float(np.mean(np.log2(1 + sv / 10 ** (-snr / 10)).sum(1) < 4))
def nnd(Q, T):   # normalised NN distance min_j ||q_i - t_j|| / ||q_i||
    Qt, Tt = torch.as_tensor(Q, device=dev), torch.as_tensor(T, device=dev); d = []
    for i in range(0, len(Qt), 500):
        d.append(torch.cdist(torch.view_as_real(Qt[i:i + 500]).flatten(1), torch.view_as_real(Tt).flatten(1)).min(1).values)
    return (torch.cat(d) / torch.linalg.norm(Qt, dim=1)).cpu().numpy()
d = nnd(h, Xtr); out.update(leak_iid_med=float(np.median(d)), leak_iid_lt01=float(np.mean(d < 0.1)))
if A.src != "d2":
    pos = G["pos"]; out["pos_nn_iid_med_m"] = float(np.median(torch.cdist(torch.as_tensor(pos[te], device=dev), torch.as_tensor(pos[:A.ntr], device=dev)).min(1).values.cpu().numpy()))
    blk = np.c_[np.floor(pos[:, :2] / A.block).astype(np.int64), G["site"]]; ub, inv = np.unique(blk, axis=0, return_inverse=True)
    tb = (np.random.default_rng(5).random(len(ub)) < 0.2)[inv.ravel()]; Xs = X * s        # random 20% of the 10 m x 10 m blocks held out
    iq, it_ = np.flatnonzero(tb)[:A.nte], np.flatnonzero(~tb)[:A.ntr]; db = nnd(Xs[iq], Xs[it_])
    out.update(leak_block_med=float(np.median(db)), leak_block_lt01=float(np.mean(db < 0.1)), block_test_los=float(G["los"][iq].mean()), iid_test_los=float(los_te.mean()),
               pos_nn_block_med_m=float(np.median(torch.cdist(torch.as_tensor(pos[iq], device=dev), torch.as_tensor(pos[it_], device=dev)).min(1).values.cpu().numpy())))
print(json.dumps(out), flush=True)
# ---------------- headroom (identical to verify/gmm_headroom.py run(), GPU EM port, extra K and exact-LO check)
Cc = np.einsum("bri,brj->bij", Hc[:, 1:], Hc[:, 1:].conj()) / R
Cc += 1e-3 * np.eye(N) * (np.trace(Cc, axis1=1, axis2=2).real / N)[:, None, None]
if Vexact is not None:
    Ve, pe = Vexact; Ce = np.einsum("bl,bli,blj->bij", pe, Ve, Ve.conj()) * s ** 2
    Ce += 1e-3 * np.eye(N) * (np.trace(Ce, axis1=1, axis2=2).real / N)[:, None, None]
    Cm = Cm * s ** 2; Cm += 1e-3 * np.eye(N) * (np.trace(Cm, axis1=1, axis2=2).real / N)[:, None, None]
gm = {}; Ks = [int(k) for k in A.Ks.split(",")]; ntr_fit = A.ntr - A.nval
for K in Ks:
    t0 = time.time(); r = fit_gmm_em_t(Xtr[:ntr_fit], K, np.random.default_rng(K), n_iter=A.n_iter, Xval=Xtr[ntr_fit:], patience=40)
    gm[K] = (r["covs"], r["pi"]); out[f"fit_K{K}"] = dict(sec=round(time.time() - t0, 1), it_best=r["it_best"], n_iter=r["n_iter"], reseed=r["n_reseed"], ll_val=r["ll_val"])
    print(f"  GMM K={K} fit {time.time()-t0:.0f}s it_best {r['it_best']} n_iter {r['n_iter']} reseed {r['n_reseed']}", flush=True)
tt = lambda x: torch.as_tensor(x, device=dev)
rng = np.random.default_rng(99); I = np.eye(N)
for snr in (-3, 3):
    nu = 10 ** (-snr / 10) / Nt                                                  # sigma^2 / Tp, Tp = Nt orthogonal pilots
    q = h + np.sqrt(nu / 2) * (rng.standard_normal(h.shape) + 1j * rng.standard_normal(h.shape))
    est = {"K1": q @ np.linalg.solve(Chat + nu * I, Chat).T}
    est["LO"] = np.einsum("bij,bj->bi", Cc @ np.linalg.inv(Cc + nu * I), q)
    if Vexact is not None: est["LOx"] = np.einsum("bij,bj->bi", Ce @ np.linalg.inv(Ce + nu * I), q)
    if Vexact is not None: est["LOm"] = np.einsum("bij,bj->bi", Cm @ np.linalg.inv(Cm + nu * I), q)
    for K, (C, w) in gm.items():
        Ct = tt(C); At = Ct + nu * tt(I); Ai = torch.linalg.inv(At); ld = torch.linalg.slogdet(At)[1]; qt = tt(q)
        ll = -torch.einsum("bi,kij,bj->bk", qt.conj(), Ai, qt).real - ld[None] + torch.log(tt(w))[None]
        gam = torch.softmax(ll, 1).to(qt.dtype)
        est[f"GMM{K}"] = torch.einsum("bk,kbi->bi", gam, torch.einsum("kij,bj->kbi", Ct @ Ai, qt)).cpu().numpy()
    strata = {"all": np.ones(len(h), bool)}
    if los_te.any(): strata.update(LOS=los_te, NLOS=~los_te)
    for sname, msk in strata.items():
        nm = {k: float((np.abs(v[msk] - h[msk]) ** 2).sum() / (np.abs(h[msk]) ** 2).sum()) for k, v in est.items()}
        clo = {K: (nm["K1"] - nm[f"GMM{K}"]) / (nm["K1"] - nm["LO"]) for K in gm}
        clm = {K: (nm["K1"] - nm[f"GMM{K}"]) / (nm["K1"] - nm["LOm"]) for K in gm} if "LOm" in nm else {}
        out[f"{sname}_{snr:+d}dB"] = dict(n=int(msk.sum()), nmse=nm, closed=clo, closed_vs_LOm=clm, gap_abs=nm["K1"] - nm["LO"], gap_db=10 * np.log10(nm["K1"] / nm["LO"]))
        print(f"{out['label']:14s} {sname:4s} n={msk.sum():4d} {snr:+d}dB NMSE " + " ".join(f"{k} {v:.4f}" for k, v in nm.items()) +
              " | closed " + " ".join(f"K{K} {c:.2f}" for K, c in clo.items()) + (" | vs LOm " + " ".join(f"K{K} {c:.2f}" for K, c in clm.items()) if clm else "") + f" | gap K1-LO {nm['K1']-nm['LO']:.4f} ({10*np.log10(nm['K1']/nm['LO']):.1f} dB)", flush=True)
json.dump(out, open(f"res_{out['label']}.json", "w"), indent=1, default=float)
