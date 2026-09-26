# GMM-headroom + channel-statistics screen: D2-S2 (calibration) vs DeepMIMO v4 scenarios.  Adapted from verify/gmm_headroom.py:
# same query model (q = h + CN(0, nu I), nu = sigma^2/Nt, Tp = Nt orthogonal pilots), same K1 / EM-GMM (fit_gmm_em, GPU port
# gmm_t.fit_gmm_em_t, exact-match checked) / latent-oracle estimators, same 36000-train + 4000-val stream, same 1e-3 LO loading.
# LO covariance: exact closed form sum_l p_l v_l v_l^H (latents = angles + powers, phases uniform); the script's Monte-Carlo LO
# (R=400 phase redraws) is ALSO computed on the first 500 test samples as a cross-check.
# usage: python run.py CASE NR SPLIT [BSROT]   CASE in {d2, boston5g_28, city_0_newyork_28+city_6_miami_28, ...}
#        SPLIT in {iid, block}; BSROT in {centroid (registered), default}
import sys, time, json, numpy as np, torch
sys.path.insert(0, "/home/HTJ/t2/conf/code"); sys.path.insert(0, "/tmp/claude-1005/-home-HTJ-t2/47f1f727-1d40-4c8f-a798-01f8d9d886c3/scratchpad/tb2/deepmimo")
import d2, dmimo
from gmm_t import fit_gmm_em_t, gmm_cme

CASE, NR, SPLIT = sys.argv[1], int(sys.argv[2]), sys.argv[3]; BSROT = sys.argv[4] if len(sys.argv) > 4 else "centroid"
NT, NTR, NTE, NMC, R, KS, TILE = 4, 40000, 2000, 500, 400, (16, 64, 256), 20.0
N = NR * NT; dev = "cuda"; rng = np.random.default_rng(0); T0 = time.time(); res = dict(case=CASE, Nr=NR, split=SPLIT, bsrot=BSROT)
er = lambda C: float((lambda l: l.sum() ** 2 / (l ** 2).sum())(np.linalg.eigvalsh(C)))

# ------------------------------------------------------------------ build: Xtr (NTR,N), hte (NTE,N), Cte (NTE,N,N), Hmc (NMC,R,N), pool
if CASE == "d2":
    g = d2.D2Gen("S2", NR, NT); r1 = np.random.default_rng(1)
    t0 = time.time(); Xtr = g.sample_vecs(r1, NTR); res["gen_s_per_1e5"] = (time.time() - t0) / NTR * 1e5
    hte, Cte, Hmc, effp = [], [], [], []
    for b in range(NTE):
        Hs, (th, ph, p) = g.sample_angles(r1, R + 1 if b < NMC else 1)
        v = g.scale * np.einsum("lj,li->lji", np.exp(-1j * np.pi * np.sin(ph)[:, None] * np.arange(NT)) / np.sqrt(NT),
                                np.exp(1j * np.pi * np.sin(th)[:, None] * np.arange(NR)) / np.sqrt(NR)).reshape(len(p), N)
        vs = Hs.transpose(0, 2, 1).reshape(len(Hs), N); hte.append(vs[0]); Cte.append(np.einsum("l,li,lj->ij", p, v, v.conj()))
        if b < NMC: Hmc.append(vs[1:])
        effp.append(1 / (p ** 2).sum())
    hte, Cte, Hmc = np.array(hte), np.array(Cte), np.array(Hmc)
    strata = {"all": np.ones(NTE, bool)}; los = np.zeros(NTE, bool); npath = None
    pool = g.sample_vecs(np.random.default_rng(2), 160000)                                   # i.i.d. continuous -> leakage reference
    pool_cov = None; res.update(los_frac=0.0, eff_paths_mean=float(np.mean(effp)), eff_paths_median=float(np.median(effp)), paths_median=5.5)
else:
    D = {}
    for si, s in enumerate(CASE.split("+")):
        Di = dmimo.load_paths(s); Di["scen"] = np.full(len(Di["los"]), si)
        for k, v in Di.items(): D[k] = v if k not in D else (np.concatenate([D[k], v]) if D[k].ndim == v.ndim == 1 or D[k].shape[1:] == v.shape[1:]
                                                               else np.concatenate([np.pad(D[k], ((0, 0), (0, max(0, v.shape[1] - D[k].shape[1]))), constant_values=np.nan if k in dmimo.FIELDS else 0),
                                                                                    np.pad(v, ((0, 0), (0, max(0, D[k].shape[1] - v.shape[1]))), constant_values=np.nan if k in dmimo.FIELDS else 0)]))
    n = len(D["los"]); D["plin"] = np.nan_to_num(D["plin"])
    # BS yaw: registered rule = boresight (+x local) toward the centroid of that BS's valid users; 'default' = DeepMIMO [0,0,0]
    D["bsrot"] = np.zeros(n); bkey = np.round(D["bspos"], 1) + 1e4 * D["scen"][:, None]
    for u in np.unique(bkey, axis=0):
        m = (bkey == u).all(1); d = D["pos"][m].mean(0) - D["bspos"][m][0]
        if BSROT == "centroid": D["bsrot"][m] = np.degrees(np.arctan2(d[1], d[0]))
    lm = D["los"] == 1; j = np.nanargmax(D["plin"], 1)                                        # azimuth convention check on LOS users
    dd = D["pos"][lm] - D["bspos"][lm]; az = np.degrees(np.arctan2(dd[:, 1], dd[:, 0]))
    res["los_az_check_deg"] = float(np.median(np.abs((D["aod_az"][lm, j[lm]] - az + 180) % 360 - 180)))
    res["bsrot_deg"] = sorted(set(np.round(D["bsrot"], 1).tolist()))
    yaw = rng.uniform(-180, 180, n)                                                          # registered: yaw-only random UE orientation
    # split
    if SPLIT == "iid":
        perm = rng.permutation(n); te = perm[:NTE]; trpool = perm[NTE:]
    else:
        tile = np.floor(D["pos"][:, :2] / TILE).astype(np.int64); key = tile[:, 0] * 100003 + tile[:, 1] + 10 ** 12 * D["scen"]
        uk, inv = np.unique(key, return_inverse=True); order = rng.permutation(len(uk)); cnt = np.bincount(inv)
        tsel = order[: np.searchsorted(np.cumsum(cnt[order]), 0.15 * n) + 1]; istest = np.isin(inv, tsel)
        te = rng.choice(np.where(istest)[0], NTE, replace=False); trpool = np.where(~istest)[0]
        res["block_test_share"] = float(istest.mean())
    tr = rng.choice(trpool, NTR, replace=False)
    t0 = time.time(); Xtr = dmimo.channels(D, tr, NR, NT, yaw[tr]); res["gen_s_per_1e5"] = (time.time() - t0) / NTR * 1e5
    hte = dmimo.channels(D, te, NR, NT, yaw[te]); Cte = dmimo.lo_cov(D, te, NR, NT, yaw[te])
    Hmc = np.stack([dmimo.channels(D, te[:NMC], NR, NT, yaw[te[:NMC]], phases=False, rng=rng) for _ in range(R)], 1)
    los = D["los"][te] == 1; strata = {"all": np.ones(NTE, bool), "LOS": los, "NLOS": ~los}
    pool = dmimo.channels(D, trpool, NR, NT, yaw[trpool])
    pool0 = dmimo.channels(D, trpool, NR, NT, np.zeros(len(trpool))); hte0 = dmimo.channels(D, te, NR, NT, np.zeros(NTE))   # fixed-yaw diagnostic
    ep = 1 / (D["plin"] ** 2).sum(1)
    res.update(n_pairs=int(n), n_trpool=int(len(trpool)), los_frac=float((D["los"] == 1).mean()), paths_median=float(np.median(D["npath"])),
               paths_mean=float(D["npath"].mean()), eff_paths_mean=float(ep.mean()), eff_paths_median=float(np.median(ep)),
               paths_within20dB_median=float(np.median((D["plin"] > 0.01 * D["plin"].max(1, keepdims=True)).sum(1))))
print(f"[{CASE} {NR}x{NT} {SPLIT} {BSROT}] built in {time.time()-T0:.0f}s", flush=True)

# ------------------------------------------------------------------ normalisation from the train stream
s = np.sqrt(N / (np.abs(Xtr) ** 2).sum(1).mean()); Xtr, hte, Cte, Hmc, pool = Xtr * s, hte * s, Cte * s * s, Hmc * s, pool * s
Chat = Xtr.T @ Xtr.conj() / len(Xtr); res["erank_ens"] = er(Chat)

# ------------------------------------------------------------------ headroom
def lo_est(C, q, nu):
    C = C + 1e-3 * np.eye(N) * (np.trace(C, axis1=1, axis2=2).real / N)[:, None, None]
    return np.einsum("bij,bj->bi", C @ np.linalg.inv(C + nu * np.eye(N)), q)

gm = {}
for K in KS:
    t0 = time.time(); r = fit_gmm_em_t(Xtr[:36000], K, np.random.default_rng(K), n_iter=200, Xval=Xtr[36000:], patience=40, dev=dev)
    gm[K] = (r["covs"], r["pi"]); print(f"  GMM K={K} fit {time.time()-t0:.0f}s it_best {r['it_best']} reseed {r['n_reseed']}", flush=True)
Cmc = np.einsum("bri,brj->bij", Hmc, Hmc.conj()) / R
rngn = np.random.default_rng(99); res["headroom"] = {}; bt = np.random.default_rng(7)
for snr in (-3, 3):
    nu = 10 ** (-snr / 10) / NT
    q = hte + np.sqrt(nu / 2) * (rngn.standard_normal(hte.shape) + 1j * rngn.standard_normal(hte.shape))
    est = {"K1": q @ np.linalg.solve(Chat + nu * np.eye(N), Chat).T, "LO": lo_est(Cte, q, nu)}
    for K, (C, w) in gm.items(): est[f"GMM{K}"] = gmm_cme(q, C, w, nu)
    e = {k: (np.abs(v - hte) ** 2).sum(1) for k, v in est.items()}; e0 = (np.abs(hte) ** 2).sum(1)
    e_mc = (np.abs(lo_est(Cmc, q[:NMC], nu) - hte[:NMC]) ** 2).sum(1)
    for sn, m in strata.items():
        if m.sum() < 20: continue
        nm = {k: v[m].sum() / e0[m].sum() for k, v in e.items()}
        row = dict(n=int(m.sum()), nmse=nm, lo_gap=nm["K1"] - nm["LO"], closed={}, ci={})
        B = [bt.integers(0, m.sum(), m.sum()) for _ in range(1000)]; idx = np.where(m)[0]
        for K in KS:
            row["closed"][K] = (nm["K1"] - nm[f"GMM{K}"]) / (nm["K1"] - nm["LO"])
            bs = [(e["K1"][idx[b]].sum() - e[f"GMM{K}"][idx[b]].sum()) / (e["K1"][idx[b]].sum() - e["LO"][idx[b]].sum()) for b in B]
            row["ci"][K] = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
        if sn == "all":                                                                      # MC-LO cross-check (script's LO) on first NMC
            k1, lm_, lc = e["K1"][:NMC].sum(), e["LO"][:NMC].sum(), e_mc.sum()
            row["closed64_first500_exactLO"] = (k1 - e["GMM64"][:NMC].sum()) / (k1 - lm_); row["closed64_first500_mcLO"] = (k1 - e["GMM64"][:NMC].sum()) / (k1 - lc)
        res["headroom"][f"{snr:+d}dB/{sn}"] = row
        print(f"  {snr:+d}dB {sn:4s} n={m.sum():4d} NMSE K1 {nm['K1']:.4f} " + " ".join(f"G{K} {nm[f'GMM{K}']:.4f}" for K in KS) +
              f" LO {nm['LO']:.4f} | gap {row['lo_gap']:.4f} closed " + " ".join(f"K{K} {row['closed'][K]:.2f}[{row['ci'][K][0]:.2f},{row['ci'][K][1]:.2f}]" for K in KS) +
              (f" | K64 first500 exactLO {row['closed64_first500_exactLO']:.2f} mcLO {row['closed64_first500_mcLO']:.2f}" if sn == "all" else ""), flush=True)

# ------------------------------------------------------------------ secondary: beamspace sparsity, outage, leakage
Fr = np.fft.fft(np.eye(NR)) / np.sqrt(NR); Ft = np.fft.fft(np.eye(NT)) / np.sqrt(NT)
H = pool[:20000].reshape(-1, NT, NR).transpose(0, 2, 1); Bm = np.abs(Fr @ H @ Ft.conj().T) ** 2
Bs = np.sort(Bm.reshape(len(Bm), -1), 1)[:, ::-1] / Bm.reshape(len(Bm), -1).sum(1, keepdims=True)
res["beam_top4"], res["beam_top8"] = float(Bs[:, :4].sum(1).mean()), float(Bs[:, :8].sum(1).mean())
sv = np.linalg.svd(H, compute_uv=False) ** 2
res["outage_m3dB"] = float(np.mean(np.log2(1 + sv / 10 ** 0.3).sum(1) < 4)); res["outage_p3dB"] = float(np.mean(np.log2(1 + sv / 10 ** -0.3).sum(1) < 4))

def nn(te_, tr_):
    a = torch.as_tensor(te_, dtype=torch.complex64, device=dev); b = torch.as_tensor(tr_, dtype=torch.complex64, device=dev)
    na, nb, best = (a.abs() ** 2).sum(1), (b.abs() ** 2).sum(1), torch.full((len(a),), float("inf"), device=dev)
    for i in range(0, len(b), 20000):
        d = na[:, None] + nb[None, i:i + 20000] - 2 * (a @ b[i:i + 20000].conj().T).real; best = torch.minimum(best, d.min(1).values)
    return (best.clamp_min(0) / na).cpu().numpy()
dnn = nn(hte, pool); res["leak_chan_median"], res["leak_chan_frac_lt0.1"] = float(np.median(dnn)), float(np.mean(dnn < 0.1))
if CASE != "d2":
    d0 = nn(hte0, pool0); res["leak_chan_fixedyaw_median"], res["leak_chan_fixedyaw_frac_lt0.1"] = float(np.median(d0)), float(np.mean(d0 < 0.1))
    ctr = trpool[rng.choice(len(trpool), min(len(trpool), 60000), replace=False)]            # latent (LO-covariance) NN, 60k subsample of pool
    Cp = dmimo.lo_cov(D, ctr, NR, NT, yaw[ctr]).reshape(len(ctr), -1) * s * s
    dl = nn(Cte.reshape(NTE, -1), Cp); res["leak_latent_median_sq"], res["leak_latent_frac_lt0.1"] = float(np.median(dl)), float(np.mean(dl < 0.1))
res["gen_extrapolated_s_182920"] = res["gen_s_per_1e5"] * 1.8292
res["wall_s"] = time.time() - T0
print(json.dumps({k: v for k, v in res.items() if k != "headroom"}, indent=None, default=float), flush=True)
json.dump(res, open(f"/tmp/claude-1005/-home-HTJ-t2/47f1f727-1d40-4c8f-a798-01f8d9d886c3/scratchpad/tb2/deepmimo/res_{CASE}_{NR}_{SPLIT}_{BSROT}.json", "w"), default=float, indent=1)
