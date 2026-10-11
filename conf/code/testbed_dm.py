"""conf/code/testbed_dm.py -- verification of the DeepMIMO prior DMC (code/dmimo.py) -> results/testbed_DMC.txt.

Probe = the phase-0 6-city block-split screen (results/review_next/testbed2_phase0/json/res_city_0_newyork_28+...+
city_4_phoenix_28_8_block_centroid.json: same scenarios, same BS / UE conventions, its own yaw draws and its own split).
Checks (tolerances fixed here before the first run; no receiver / BLER anywhere):
  TDMa normalisation: mean ||H||_F^2 / (Nr Nt) on the VALIDATION stream (8), n = N_VAL, within 4 MC s.e. of 1 (P_RAW was
       calibrated on the train stream 7, so this is an out-of-sample check on other pairs of the same tiles);
  TDMb per-entry power E|H_ab|^2: reported;
  TDMc pool identity vs the probe: number of pairs equal, the 18 BS yaws equal to 0.1 deg, LoS fraction of all pairs within 1e-6;
  TDMd pilot-stage K=1 Gaussian (LMMSE with the sample covariance of 40000 train draws) NMSE at -3 dB, nu = sigma^2 / Nt, on
       the validation draw: within 0.02 of the probe's headroom['-3dB/all'].nmse.K1 (same estimator, different draws / split);
  TDMe T2b pilot decision (erank Rt vs 0.9 Nt), ensemble effective rank, beamspace top-4 energy (report);
  TDMf block split: the three pools are disjoint and no 20 m tile has pairs on both the test side and the fit / validation side;
  TDMg split shift (report): LoS fraction, -3 dB outage P(MI < 4 bit) and K=1 NMSE on the fit / validation side vs the TEST side
       (stream 10) -- the test tiles are other places, so these need not agree; the receiver is evaluated on the test side;
  TDMh leakage (report): share of 2000 test draws whose nearest of the N' = 160000 training channels is within a normalised
       squared distance 0.1 (probe: 0.411 against its whole train pool);
  TDMi generation cost.
"""
import json, os, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import common as C
import d2
import dmimo

PRIOR, NR, NT, N_VAL = (sys.argv[1] if len(sys.argv) > 1 else "DMC"), 8, 4, 20000      # python testbed_dm.py [DMC | SRT]
OUT = os.path.join(C.CONF, "results", f"testbed_{PRIOR}.txt")
PROBE = os.path.join(C.CONF, "results", "review_next", "testbed2_phase0", "json",
                     "res_city_0_newyork_28+city_6_miami_28+city_1_losangeles_28+city_2_chicago_28+city_3_houston_28+"
                     "city_4_phoenix_28_8_block_centroid.json")


def k1_nmse(Chat, h, snr_db=-3):
    nu = 10 ** (-snr_db / 10) / NT
    rng = np.random.default_rng(99)
    q = h + np.sqrt(nu / 2) * (rng.standard_normal(h.shape) + 1j * rng.standard_normal(h.shape))
    est = q @ np.linalg.solve(Chat + nu * np.eye(NR * NT), Chat).T
    return float(np.sum(np.abs(est - h) ** 2) / np.sum(np.abs(h) ** 2))


def outage(H, snr_db=-3):
    sv = np.linalg.svd(H, compute_uv=False) ** 2
    return float(np.mean(np.log2(1 + sv * 10 ** (snr_db / 10)).sum(1) < 4))


def main():
    t_start = time.time()
    g = C.make_gen("D2", PRIOR, NR, NT)
    m = np.load(os.path.join(dmimo.pool_dir(PRIOR, NR), "meta.npz"))
    pr = json.load(open(PROBE)) if PRIOR == "DMC" else None      # SRT / SRB / DMI: no phase-0 probe of this configuration -> report only
    nanp = {"n_pairs": float("nan"), "los_frac": float("nan"), "erank_ens": float("nan"), "beam_top4": float("nan"), "outage_m3dB": float("nan"),
            "leak_chan_frac_lt0.1": float("nan")}
    L = [f"# date        : {time.strftime('%Y-%m-%d %H:%M:%S KST')}",
         f"# git commit  : {subprocess.run(['git', '-C', C.CONF, 'rev-parse', '--short=8', 'HEAD'], capture_output=True, text=True).stdout.strip()}",
         f"# content     : testbed_dm.py -- {'DeepMIMO v4' if PRIOR in ('DMC', 'DMI') else 'Sionna RT 2.1'} {PRIOR} (code/dmimo.py, pool by code/{dict(DMC='dmimo_build.py', SRT='srt_build.py', SRB='srb_build.py', DMI='dmi_build.py')[PRIOR]}), Nr={NR} x Nt={NT}; streams from common.train_rng('D2','{PRIOR}',...)",
         f"# pool        : sha H.npy / split.npy = {dmimo.POOL_SHA[(PRIOR, NR)]}; pairs {len(m['los'])} = fit {len(g.idx['fit'])} + val {len(g.idx['val'])} + test {len(g.idx['test'])}",
         f"# calibration : P_RAW={dmimo.P_RAW[(PRIOR, NR, NT)]!r}  TRAIN_SHA={dmimo.TRAIN_SHA[(PRIOR, NR, NT)]}  (n={dmimo.N_CAL}, train stream 7)", ""]
    ok = True
    t0 = time.time()
    H = g._draw(C.train_rng("D2", PRIOR, NR, 8), N_VAL)
    t_val = time.time() - t0
    p = np.sum(np.abs(H) ** 2, (1, 2)) / (NR * NT)
    se = p.std() / np.sqrt(len(p))
    a = abs(p.mean() - 1) <= 4 * se
    ok &= a
    L.append(f"TDMa normalisation (val stream 8, n={N_VAL}): mean ||H||^2/(Nr Nt) = {p.mean():.5f} (s.e. {se:.5f}; 4 s.e. band) "
             f"-> {'PASS' if a else 'FAIL'};  per-block power CV {p.std() / p.mean():.3f}")
    E = np.mean(np.abs(H) ** 2, 0)
    L.append(f"TDMb per-entry E|H_ab|^2: min {E.min():.4f} max {E.max():.4f} (report only)")
    los = m["los"] == 1
    if pr is None and PRIOR == "SRB":                            # room pool: identity from srb_build's constants
        import srb_build
        c = len(los) == srb_build.TARGET and list(m["scenes"]) == [srb_build.SCENE]
        ok &= c
        L.append(f"TDMc pool identity: pairs {len(los)} (== TARGET {srb_build.TARGET}), scene {srb_build.SCENE}, ONE BS at {[round(float(x), 3) for x in m['bs']]}, "
                 f"LoS fraction {los.mean():.6f}, mean paths {m['npath'].mean():.2f} -> {'PASS' if c else 'FAIL'}")
        pr = nanp
    elif pr is None and PRIOR == "DMI":                          # indoor pool: identity from dmi_build's constants
        import dmi_build
        c = (len(los) == dmi_build.N_GRID * dmi_build.NYAW and list(m["scenarios"]) == [dmi_build.SCEN]
             and bool(np.allclose(m["tx"], dmi_build.TX_POS, atol=0.01)) and len(set(m["posi"].tolist())) == dmi_build.N_GRID)
        ok &= c
        L.append(f"TDMc pool identity: pairs {len(los)} (== {dmi_build.N_GRID} grid positions x {dmi_build.NYAW} yaws), scenario {dmi_build.SCEN} dataset "
                 f"{dmi_build.DS}, ONE BS at {[round(float(x), 2) for x in m['tx']]}, LoS fraction {los.mean():.6f}, mean paths {m['npath'].mean():.2f} -> {'PASS' if c else 'FAIL'}")
        pr = nanp
    elif pr is None:                                             # SRT: pool identity from the builder's constants
        import srt_build
        cnt = np.bincount(m["scen"], minlength=len(srt_build.SCENES))
        c = bool((cnt == srt_build.TARGET).all()) and list(m["scenes"]) == list(srt_build.SCENES)
        ok &= c
        L.append(f"TDMc pool identity: pairs per scene {dict(zip(srt_build.SCENES, cnt.tolist()))} (== TARGET {srt_build.TARGET}), sites per scene "
                 f"{[int(len(set(m['site'][m['scen'] == i].tolist()))) for i in range(len(cnt))]}, LoS fraction {los.mean():.6f}, mean paths "
                 f"{m['npath'].mean():.2f} -> {'PASS' if c else 'FAIL'}")
        pr = nanp
    else:
        yaws = sorted(set(np.round(m["bsyaw"], 1).tolist()))
        c = (len(los) == pr["n_pairs"] and len(yaws) == len(pr["bsrot_deg"]) and np.allclose(yaws, pr["bsrot_deg"], atol=0.1001)
             and abs(los.mean() - pr["los_frac"]) < 1e-6)
        ok &= c
        L.append(f"TDMc pool vs probe: pairs {len(los)} vs {pr['n_pairs']}; {len(yaws)} BS yaws max |diff| "
                 f"{np.max(np.abs(np.array(yaws) - np.array(pr['bsrot_deg']))) if len(yaws) == len(pr['bsrot_deg']) else float('nan'):.2f} deg; "
                 f"LoS fraction {los.mean():.6f} vs {pr['los_frac']:.6f} -> {'PASS' if c else 'FAIL'}")
    Xtr = g.sample_vecs(C.train_rng("D2", PRIOR, NR, 7), dmimo.N_CAL)
    Chat = Xtr[:40000].T @ Xtr[:40000].conj() / 40000
    h = H.transpose(0, 2, 1).reshape(N_VAL, NR * NT)
    nm = k1_nmse(Chat, h)
    if "headroom" in pr:
        kp = pr["headroom"]["-3dB/all"]["nmse"]["K1"]
        dd = abs(nm - kp) <= 0.02
        ok &= dd
        L.append(f"TDMd pilot-stage K=1 Gaussian NMSE @ -3 dB (nu = sigma^2/Nt, val draw): {nm:.4f} vs probe {kp:.4f} (|diff| <= 0.02) "
                 f"-> {'PASS' if dd else 'FAIL'}")
    else:
        L.append(f"TDMd pilot-stage K=1 Gaussian NMSE @ -3 dB (nu = sigma^2/Nt, val draw): {nm:.4f} (report only: no probe of this configuration; "
                 f"phase-0 single-scene depth-2 'rs' rows: see report_rt.md)")
    Rt, Rr, inf = dmimo.ensemble_sides_dm(PRIOR, NR, NT)
    pil, _ = C.make_pilots("D2", PRIOR, NT, 4, NR)
    F = np.fft.fft(np.fft.fft(H, axis=1, norm="ortho"), axis=2, norm="ortho")
    en = np.sort((np.abs(F) ** 2).reshape(N_VAL, -1), 1)[:, ::-1]
    t4 = en[:, :4].sum(1) / en.sum(1)
    L.append(f"TDMe erank(Rt) = {d2._erank(np.linalg.eigvalsh(Rt)):.3f} / {NT} (T2b threshold {d2.T2B_ERANK_FRAC * NT:.1f}) -> "
             f"pilots '{pil}' for Tp<=Nt;  erank(C_ens) = {d2._erank(np.linalg.eigvalsh(Chat)):.2f} / {NR * NT} (probe "
             f"{pr['erank_ens']:.2f});  beamspace top-4 energy median {np.median(t4):.3f} mean {t4.mean():.3f} (probe mean {pr['beam_top4']:.3f})")
    fit, val, test = (set(g.idx[k].tolist()) for k in ("fit", "val", "test"))
    key = m["key"]
    f_ = (not (fit & val or fit & test or val & test) and len(fit | val | test) == len(los)
          and not set(key[g.idx["test"]].tolist()) & set(key[np.concatenate([g.idx["fit"], g.idx["val"]])].tolist()))
    ok &= f_
    L.append(f"TDMf block split: pools disjoint and exhaustive, no tile on both sides ({len(set(key.tolist()))} tiles, "
             f"{len(set(key[g.idx['test']].tolist()))} test; test share {len(test) / len(los):.4f}) -> {'PASS' if f_ else 'FAIL'}")
    Ht = g._draw(C.train_rng("D2", PRIOR, NR, 10), N_VAL)
    ht = Ht.transpose(0, 2, 1).reshape(N_VAL, NR * NT)
    tr_side = np.concatenate([g.idx["fit"], g.idx["val"]])
    L.append(f"TDMg split shift (report): LoS fraction fit+val side {los[tr_side].mean():.4f} / test side {los[g.idx['test']].mean():.4f}; "
             f"outage P(MI<4 bit) @ -3 dB val {outage(H):.4f} / test {outage(Ht):.4f} (probe {pr['outage_m3dB']:.4f}); "
             f"K=1 NMSE @ -3 dB val {nm:.4f} / test {k1_nmse(Chat, ht):.4f};  mean ||H||^2/(Nr Nt) test {np.mean(np.abs(Ht) ** 2):.4f}")
    a2 = (np.abs(ht[:2000]) ** 2).sum(1)
    best = np.full(2000, np.inf)
    for i in range(0, len(Xtr), 20000):
        B = Xtr[i:i + 20000]
        best = np.minimum(best, (a2[:, None] + (np.abs(B) ** 2).sum(1)[None] - 2 * (ht[:2000] @ B.conj().T).real).min(1))
    dn = np.maximum(best, 0) / a2
    L.append(f"TDMh leakage (report): nearest training channel of 2000 test draws (N' = {dmimo.N_CAL}): median normalised squared "
             f"distance {np.median(dn):.4f}, share < 0.1 = {np.mean(dn < 0.1):.3f} (probe {pr['leak_chan_frac_lt0.1']:.3f} vs its whole train pool)")
    rng = C.trial_rng("D2", PRIOR, NR, 16, 4, -3)
    t0 = time.time(); [g.sample(rng) for _ in range(200)]; t1 = (time.time() - t0) / 200
    t0 = time.time(); g.sample_vecs(C.train_rng("D2", PRIOR, NR, 7), dmimo.N_CAL); t2 = time.time() - t0
    L.append(f"TDMi cost: sample() {1e3 * t1:.2f} ms/call, sample_vecs {dmimo.N_CAL} in {t2:.1f} s, val draw {N_VAL} in {t_val:.1f} s")
    L += ["", f"ALL {'PASS' if ok else 'FAIL'} ({time.time() - t_start:.0f} s CPU)"]
    open(OUT, "w").write("\n".join(L) + "\n")
    print("\n".join(L))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
