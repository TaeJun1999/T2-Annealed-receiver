# Second-testbed scan, CHANNEL STATISTICS ONLY: "GMM headroom closed" (K1 Gaussian -> EM-GMM -> latent oracle LO)
# + secondary stats, for 38.901 PHY configs vs D2 (calibration). Adapted from scratchpad/verify/gmm_headroom.py.
# Conventions: uplink narrowband block fading (sum over paths at t=0), BS ULA Nr (lambda/2), UE ULA Nt=4, single V pol,
# omni patterns, UE orientation = yaw ~ U[-pi,pi), pitch = roll = 0; BS = gen_single_sector_topology default (sector-centred
# yaw, scenario downtilt); pathloss & shadowing off; outdoor UEs only; ensemble norm E||H||^2 = Nr*Nt from TRAIN; h = vec col-major.
import sys, os, copy, time, json, argparse, numpy as np, torch
sys.path.insert(0, "/home/HTJ/t2/conf/code"); sys.path.insert(0, "/home/HTJ/t2/Demo")
DEV = "cuda:0"; C128 = torch.complex128
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
vec = lambda H: H.transpose(0, 2, 1).reshape(len(H), -1)
NT = 4
LSPO = False


# ---------------------------------------------------------------- GPU port of Demo/t2_gmm.fit_gmm_em (struct='full', kappa=0)
def _loglik_t(X, logpi, covs, kc=32):
    n, N = X.shape; L = torch.linalg.cholesky(covs); Linv = torch.linalg.inv(L)
    logdet = 2 * torch.log(torch.diagonal(L, dim1=1, dim2=2).real).sum(1)
    lw = torch.empty(n, len(covs), dtype=torch.float64, device=X.device)
    for s in range(0, len(covs), kc):
        Z = X[None] @ Linv[s:s + kc].transpose(-1, -2)
        lw[:, s:s + kc] = -(Z.real ** 2 + Z.imag ** 2).sum(-1).T
    return lw + logpi - logdet - N * np.log(np.pi)


def fit_gmm_em_t(X, K, rng, n_iter=200, tol=1e-6, floor=1e-4, Xval=None, val_every=10, patience=40, kc=32):
    X = torch.as_tensor(X, dtype=C128, device=DEV); Xv = None if Xval is None else torch.as_tensor(Xval, dtype=C128, device=DEV)
    n, N = X.shape; Chat = X.T @ X.conj() / n; cbar = Chat.diagonal().real.sum() / N; I = torch.eye(N, dtype=C128, device=DEV)
    def seed_cov(i):
        s = X[i]; return 0.5 * Chat + 0.5 * (N * cbar / (s.conj() @ s).real) * torch.outer(s, s.conj())
    covs = torch.stack([seed_cov(int(i)) for i in rng.choice(n, K, replace=False)])
    logpi = torch.full((K,), -np.log(K), dtype=torch.float64, device=DEV)
    best = dict(ll_val=-np.inf, it=0, pi=logpi.exp(), covs=covs.clone()); ll = []; n_reseed = 0
    for it in range(n_iter):
        lw = _loglik_t(X, logpi, covs); lse = torch.logsumexp(lw, 1); ll.append(lse.mean().item())
        if Xv is not None and it % val_every == 0:
            v = torch.logsumexp(_loglik_t(Xv, logpi, covs), 1).mean().item()
            if v > best["ll_val"]: best = dict(ll_val=v, it=it, pi=logpi.exp(), covs=covs.clone())
            elif it - best["it"] >= patience: break
        if it >= 20 and ll[-1] - ll[-2] < tol * abs(ll[-1]): break
        gam = torch.exp(lw - lse[:, None]); nk = gam.sum(0); new = torch.empty_like(covs)
        for s in range(0, K, kc):
            g = gam[:, s:s + kc].T.to(C128)
            S = (X[None] * g[:, :, None]).transpose(-1, -2) @ X.conj() / nk[s:s + kc, None, None]
            new[s:s + kc] = 0.5 * (S + S.conj().transpose(-1, -2)) + floor * cbar * I
        for k in torch.nonzero(nk < N).flatten().tolist():                       # starved -> re-seed (same order as the CPU code)
            new[k] = seed_cov(int(rng.integers(n))); nk[k] = max(nk[k].item(), 1.0); n_reseed += 1
        covs = new; logpi = torch.log(nk / nk.sum())
    out = dict(pi=logpi.exp(), covs=covs, n_iter=len(ll), n_reseed=n_reseed, it_best=len(ll) - 1)
    if Xv is not None: out.update(pi=best["pi"], covs=best["covs"], it_best=best["it"], ll_val=best["ll_val"])
    return out


# ---------------------------------------------------------------- generators
def gen_d2(Nr, ntr, nte, R, seed):
    import d2
    g = d2.D2Gen("S2", Nr, NT); rng = np.random.default_rng(seed)
    t0 = time.time(); Xtr = g.sample_vecs(rng, ntr); dt = time.time() - t0
    Hc, L = [], []
    for b in range(nte):
        Hs, ang = g.sample_angles(rng, R + 1); Hc.append(vec(Hs)); L.append(len(ang[0]))
    return dict(Xtr=Xtr, Hc=np.stack(Hc), strata={"all": np.ones(nte, bool)}, ms_per_sample=1e3 * dt / ntr,
                paths=float(np.mean(L)), los_frac=None, pos_tr=None, pos_te=None)


def _sionna():
    import sionna.phy
    from sionna.phy.channel.tr38901 import UMi, UMa, RMa, PanelArray, CDL
    from sionna.phy.channel import gen_single_sector_topology
    return sionna.phy, UMi, UMa, RMa, PanelArray, CDL, gen_single_sector_topology


def sys_model(scen, fc, Nr, B, los, mkw=None):
    sp, UMi, UMa, RMa, PanelArray, _, gsst = _sionna()
    mk = lambda n: PanelArray(num_rows_per_panel=1, num_cols_per_panel=n, polarization="single", polarization_type="V",
                              antenna_pattern="omni", carrier_frequency=fc, device=DEV)
    kw = dict(carrier_frequency=fc, ut_array=mk(NT), bs_array=mk(Nr), direction="uplink",
              enable_pathloss=False, enable_shadow_fading=False, device=DEV)
    if scen != "rma": kw["o2i_model"] = "low"
    kw.update(mkw or {})                                                          # e.g. 38.901 §7.6.4 blockage model A
    m = dict(umi=UMi, uma=UMa, rma=RMa)[scen](**kw)
    tp = list(gsst(B, 1, scen, indoor_probability=0.0, device=DEV))
    o = torch.zeros_like(tp[2]); o[..., 0] = (torch.rand(o[..., 0].shape, device=DEV) * 2 - 1) * torch.pi; tp[2] = o
    extra = dict(in_car=torch.zeros_like(tp[5])) if scen == "rma" else {}
    m.set_topology(*tp, los=los, **extra)
    return m, tp


def draw(m, B, Nr):
    return m(1, 1.0)[0][..., 0].sum(-1).reshape(B, Nr, NT).cpu().numpy().astype(np.complex128)


def gen_3gpp_part(scen, fc, los, Nr, ntr, nte, R, mkw=None, chunk=4000):
    Xtr, pos_tr, t_gen = [], [], 0.0
    for s in range(0, ntr, chunk):
        b = min(chunk, ntr - s); torch.cuda.synchronize(); t0 = time.time()
        m, tp = sys_model(scen, fc, Nr, b, los, mkw); H = draw(m, b, Nr); torch.cuda.synchronize(); t_gen += time.time() - t0
        Xtr.append(vec(H)); pos_tr.append(tp[0][:, 0, :2].cpu().numpy())
    m, tp = sys_model(scen, fc, Nr, nte, los, mkw); orig = m._ray_sampler; box = {}
    Hl = np.stack([vec(draw(m, nte, Nr)) for _ in range(R)], 1) if LSPO else None     # LSP-oracle: topology+LSPs fixed, rays redrawn
    def cap(lsp):
        r = orig(lsp); box["r"] = copy.deepcopy(r); return r
    object.__setattr__(m, "_ray_sampler", cap); m(1, 1.0)
    object.__setattr__(m, "_ray_sampler", lambda lsp: copy.deepcopy(box["r"]))
    los_te = m._scenario.los.reshape(nte).cpu().numpy()
    ncl = (box["r"].powers.reshape(nte, -1) > 0).sum(1).float().mean().item()
    Hc = np.stack([vec(draw(m, nte, Nr)) for _ in range(R + 1)], 1)
    return dict(Xtr=np.concatenate(Xtr), Hc=Hc, Hl=Hl, los=los_te, ncl=ncl, t_gen=t_gen,
                pos_tr=np.concatenate(pos_tr), pos_te=tp[0][:, 0, :2].cpu().numpy())


def gen_3gpp(parts, Nr, ntr, nte, R, seed):
    sp = _sionna()[0]; sp.config.seed = seed; torch.manual_seed(seed)
    k = len(parts); ntrs = [ntr // k + (i < ntr % k) for i in range(k)]; ntes = [nte // k + (i < nte % k) for i in range(k)]
    P = [gen_3gpp_part(*p[:3], Nr, a, b, R, *p[3:]) for p, a, b in zip(parts, ntrs, ntes)]
    perm = np.random.default_rng(seed).permutation(ntr)                        # shuffle BEFORE the 36000/4000 train/val cut
    los = np.concatenate([p["los"] for p in P]); tag = np.concatenate([np.full(b, i) for i, b in enumerate(ntes)])
    strata = {"all": np.ones(nte, bool)}
    if 0 < los.mean() < 1: strata.update(LOS=los, NLOS=~los)
    if k > 1: strata.update({f"part{i}": tag == i for i in range(k)})
    return dict(Xtr=np.concatenate([p["Xtr"] for p in P])[perm], Hc=np.concatenate([p["Hc"] for p in P]), strata=strata,
                Hl=np.concatenate([p["Hl"] for p in P]) if LSPO else None,
                ms_per_sample=1e3 * sum(p["t_gen"] for p in P) / ntr, los_frac=float(los.mean()),
                paths=float(np.average([p["ncl"] for p in P], weights=ntes)),
                pos_tr=np.concatenate([p["pos_tr"] for p in P])[perm], pos_te=np.concatenate([p["pos_te"] for p in P]))


def gen_cdl(model, Nr, ntr, nte, R, seed, fc=28e9):
    sp, _, _, _, PanelArray, CDL, _ = _sionna(); sp.config.seed = seed
    mk = lambda n: PanelArray(num_rows_per_panel=1, num_cols_per_panel=n, polarization="single", polarization_type="V",
                              antenna_pattern="omni", carrier_frequency=fc, device=DEV)
    c = CDL(model, 100e-9, fc, ut_array=mk(NT), bs_array=mk(Nr), direction="uplink", device=DEV)
    d = lambda B: c(B, 1, 1.0)[0][..., 0].sum(-1).reshape(B, Nr, NT).cpu().numpy().astype(np.complex128)
    torch.cuda.synchronize(); t0 = time.time(); Xtr = np.concatenate([vec(d(4000)) for _ in range(ntr // 4000)]); dt = time.time() - t0
    Hc = np.concatenate([vec(d(4010)) for _ in range(nte * (R + 1) // 4010)]).reshape(nte, R + 1, -1)          # CDL: geometry fixed; LO = i.i.d. draws (coupling+phases free)
    return dict(Xtr=Xtr, Hc=Hc, strata={"all": np.ones(nte, bool)}, ms_per_sample=1e3 * dt / ntr, los_frac=None,
                paths=None, pos_tr=None, pos_te=None)


# ---------------------------------------------------------------- metrics
er = lambda lam: float(lam.sum() ** 2 / (lam ** 2).sum())


def secondary(Xtr, h, Nr, pos_tr, pos_te):
    N = Nr * NT; out = {}
    X = torch.as_tensor(Xtr, dtype=C128, device=DEV); Q = torch.as_tensor(h, dtype=C128, device=DEV)
    out["erank_ens"] = er(np.linalg.eigvalsh(Xtr.T @ Xtr.conj() / len(Xtr)))
    H = Xtr[:20000].reshape(-1, NT, Nr).transpose(0, 2, 1)
    Fr = np.fft.fft(np.eye(Nr)) / np.sqrt(Nr); Ft = np.fft.fft(np.eye(NT)) / np.sqrt(NT)
    E = np.abs(Fr.conj().T @ H @ Ft) ** 2; E = np.sort(E.reshape(len(H), -1), 1)[:, ::-1]; E /= E.sum(1, keepdims=True)
    out["beam_top4"], out["beam_top8"] = float(E[:, :4].sum(1).mean()), float(E[:, :8].sum(1).mean())
    s = np.linalg.svd(H, compute_uv=False) ** 2
    mi = np.log2(1 + s / 10 ** (3 / 10)).sum(1)                                   # -3 dB: sigma^2 = 10^(0.3)
    out["outage_m3dB"] = float(np.mean(mi < 4)); out["MI_m3dB_med"] = float(np.median(mi))
    def nn(Qs, Xs):
        xx = (Xs.abs() ** 2).sum(1); qq = (Qs.abs() ** 2).sum(1); d, dp = [], []
        for i in range(0, len(Qs), 250):
            G = Qs[i:i + 250].conj() @ Xs.T
            d.append(((qq[i:i + 250, None] + xx[None] - 2 * G.real).clamp_min(0).min(1).values / qq[i:i + 250]).sqrt())
            dp.append(((qq[i:i + 250, None] + xx[None] - 2 * G.abs()).clamp_min(0).min(1).values / qq[i:i + 250]).sqrt())
        d, dp = torch.cat(d).cpu().numpy(), torch.cat(dp).cpu().numpy()
        return dict(med=float(np.median(d)), frac_lt01=float(np.mean(d < 0.1)), med_phase=float(np.median(dp)), frac_lt01_phase=float(np.mean(dp < 0.1)))
    out["leak_iid"] = nn(Q, X)
    if pos_tr is not None:                                                        # spatial-block split: azimuth halves of the sector
        az_tr, az_te = np.arctan2(pos_tr[:, 1], pos_tr[:, 0]), np.arctan2(pos_te[:, 1], pos_te[:, 0]); cut = np.median(az_tr)
        mt, me = torch.as_tensor(az_tr < cut, device=DEV), az_te >= cut
        out["leak_block"] = nn(Q[torch.as_tensor(me, device=DEV)], X[mt])
    return out


def headroom(Xtr, Hc, strata, Ks, R, ntrain=36000, Hl=None):
    N = Xtr.shape[1]; I = torch.eye(N, dtype=C128, device=DEV)
    Hc_t = torch.as_tensor(Hc, dtype=C128, device=DEV); h = Hc_t[:, 0]
    Cc = torch.einsum("bri,brj->bij", Hc_t[:, 1:], Hc_t[:, 1:].conj()) / R           # LO 2nd moment from the OTHER draws
    cond_er = float(np.mean([er(l) for l in torch.linalg.eigvalsh(Cc).clamp_min(0).cpu().numpy()]))
    Cc = Cc + 1e-3 * I * (Cc.diagonal(dim1=1, dim2=2).real.sum(1) / N)[:, None, None]
    X = torch.as_tensor(Xtr, dtype=C128, device=DEV); Chat = X.T @ X.conj() / len(X)
    if Hl is not None:
        Hl_t = torch.as_tensor(Hl, dtype=C128, device=DEV); Cl = torch.einsum("bri,brj->bij", Hl_t, Hl_t.conj()) / Hl_t.shape[1]
        Cl = Cl + 1e-3 * I * (Cl.diagonal(dim1=1, dim2=2).real.sum(1) / N)[:, None, None]
    gm, fitinfo = {}, {}
    for K in Ks:
        t0 = time.time(); r = fit_gmm_em_t(Xtr[:ntrain], K, np.random.default_rng(K), n_iter=200, Xval=Xtr[ntrain:], patience=40)
        gm[K] = (r["covs"], r["pi"]); fitinfo[K] = dict(sec=round(time.time() - t0, 1), n_iter=r["n_iter"], it_best=r["it_best"], n_reseed=r["n_reseed"])
        print(f"  GMM K={K} fit {fitinfo[K]}", flush=True)
    rng = np.random.default_rng(99); res = {}
    for snr in (-3, 3):
        nu = 10 ** (-snr / 10) / NT                                                    # sigma^2/Tp, Tp = Nt orthogonal pilots
        z = rng.standard_normal(h.shape) + 1j * rng.standard_normal(h.shape)
        q = h + np.sqrt(nu / 2) * torch.as_tensor(z, dtype=C128, device=DEV)
        est = {"K1": q @ torch.linalg.solve(Chat + nu * I, Chat).T,
               "LO": torch.einsum("bij,bj->bi", Cc @ torch.linalg.inv(Cc + nu * I), q)}
        if Hl is not None: est["LSPO"] = torch.einsum("bij,bj->bi", Cl @ torch.linalg.inv(Cl + nu * I), q)
        for K, (C, w) in gm.items():
            A = C + nu * I; Ai = torch.linalg.inv(A); ld = torch.linalg.slogdet(A)[1]
            qa = torch.einsum("bi,kij->kbj", q.conj(), Ai)
            ll = -(qa * q[None]).sum(-1).real.T - ld[None] + torch.log(w)[None]
            gam = torch.softmax(ll, 1).to(C128)
            est[f"GMM{K}"] = torch.einsum("bk,kbi->bi", gam, torch.einsum("kij,bj->kbi", C @ Ai, q))
        for sname, msk in strata.items():
            mt = torch.as_tensor(msk, device=DEV)
            nm = {k: ((v[mt] - h[mt]).abs() ** 2).sum().item() / (h[mt].abs() ** 2).sum().item() for k, v in est.items()}
            gap = nm["K1"] - nm["LO"]
            res[f"{sname}@{snr:+d}dB"] = dict(n=int(msk.sum()), nmse=nm, gap_K1_LO=gap, closed={K: (nm["K1"] - nm[f"GMM{K}"]) / gap for K in gm})
            if "LSPO" in nm: res[f"{sname}@{snr:+d}dB"]["closed_LSPO"] = (nm["K1"] - nm["LSPO"]) / gap
            print(f"  {sname:6s} n={msk.sum():4d} {snr:+d}dB NMSE " + " ".join(f"{k} {v:.4f}" for k, v in nm.items()) +
                  f" | gap {gap:.4f} closed " + " ".join(f"K{K}:{(nm['K1']-nm[f'GMM{K}'])/gap:.2f}" for K in gm), flush=True)
    return res, fitinfo, cond_er


BLK = dict(enable_blockage=True, blockage_model="A", blockage_self_blocking="landscape", blockage_num_non_self_blockers=4)
CFG = {  # name: (kind, Nr, spec)
    "D2_8": ("d2", 8, None), "D2_16": ("d2", 16, None),
    "UMi28_mix_8": ("3gpp", 8, [("umi", 28e9, None)]),
    "UMi100_los_8": ("3gpp", 8, [("umi", 100e9, True)]),
    "UMi100_mix_8": ("3gpp", 8, [("umi", 100e9, None)]),
    "UMa28_los_8": ("3gpp", 8, [("uma", 28e9, True)]),
    "RMa_los_8": ("3gpp", 8, [("rma", 3.5e9, True)]),
    "RMa_mix_8": ("3gpp", 8, [("rma", 3.5e9, None)]),
    "MIX3_8": ("3gpp", 8, [("umi", 28e9, None), ("uma", 28e9, None), ("rma", 3.5e9, None)]),
    "CDLC_8": ("cdl", 8, "C"),
    "UMi28_mix_16": ("3gpp", 16, [("umi", 28e9, None)]),
    "RMa_los_16": ("3gpp", 16, [("rma", 3.5e9, True)]),
    "UMi100_los_16": ("3gpp", 16, [("umi", 100e9, True)]),
    "MIX3_16": ("3gpp", 16, [("umi", 28e9, None), ("uma", 28e9, None), ("rma", 3.5e9, None)]),
    "UMi28_mix_blkA_8": ("3gpp", 8, [("umi", 28e9, None, BLK)]), "UMi28_los_blkA_8": ("3gpp", 8, [("umi", 28e9, True, BLK)]),
    "UMi100_mix_blkA_8": ("3gpp", 8, [("umi", 100e9, None, BLK)]), "UMi28_mix_blkA_16": ("3gpp", 16, [("umi", 28e9, None, BLK)]),
    "D2_32": ("d2", 32, None), "UMi28_mix_32": ("3gpp", 32, [("umi", 28e9, None)]),
    "UMi100_los_32": ("3gpp", 32, [("umi", 100e9, True)]), "RMa_los_32": ("3gpp", 32, [("rma", 3.5e9, True)]),
}

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cfgs", nargs="+"); ap.add_argument("--ntr", type=int, default=40000)
    ap.add_argument("--nte", type=int, default=1000); ap.add_argument("--R", type=int, default=400)
    ap.add_argument("--K", type=int, nargs="+", default=[16, 64, 256]); ap.add_argument("--seed", type=int, default=1); ap.add_argument("--lspo", action="store_true")
    a = ap.parse_args(); os.makedirs(OUT, exist_ok=True); LSPO = a.lspo
    for name in a.cfgs:
        kind, Nr, spec = CFG[name]; t0 = time.time(); print(f"=== {name}", flush=True)
        D = (gen_d2(Nr, a.ntr, a.nte, a.R, a.seed) if kind == "d2" else gen_cdl(spec, Nr, a.ntr, a.nte, a.R, a.seed) if kind == "cdl"
             else gen_3gpp(spec, Nr, a.ntr, a.nte, a.R, a.seed))
        s = np.sqrt(Nr * NT / (np.abs(D["Xtr"]) ** 2).sum(1).mean()); Xtr, Hc = D["Xtr"] * s, D["Hc"] * s
        tg = time.time() - t0; print(f"  gen {tg:.0f}s, train {D['ms_per_sample']:.3f} ms/sample", flush=True)
        res, fitinfo, cond_er = headroom(Xtr, Hc, D["strata"], a.K, a.R, Hl=None if D.get("Hl") is None else D["Hl"] * s)
        sec = secondary(Xtr, Hc[:, 0], Nr, D["pos_tr"], D["pos_te"])
        rec = dict(cfg=name, kind=kind, Nr=Nr, Nt=NT, spec=str(spec), ntr=a.ntr, nte=a.nte, R=a.R, seed=a.seed, los_frac=D["los_frac"],
                   paths_or_clusters=D["paths"], cond_erank_LO=cond_er, ms_per_sample=D["ms_per_sample"],
                   gen_min_for_182920=D["ms_per_sample"] * 182920 / 6e4, fit=fitinfo, headroom=res, **sec, wall_s=round(time.time() - t0))
        print(json.dumps({k: v for k, v in rec.items() if k != "headroom"}), flush=True)
        json.dump(rec, open(os.path.join(OUT, f"{name}_seed{a.seed}{'_lspo' if LSPO else ''}.json"), "w"), indent=1, default=float)
