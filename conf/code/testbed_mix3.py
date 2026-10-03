"""conf/code/testbed_mix3.py [MIX3|UMi28] [--nr {8,16,32}] -- verification of a 38.901 prior (code/mix3.py) -> results/testbed_<prior>.txt
(Nr 8, default, unchanged) or results/testbed_<prior>_Nr<nr>.txt (Nr 16 / 32).
UMi28 (added 2026-09-26, the main 38.901 experiment): same checks and tolerances against its own phase-0 probe UMi28_mix_8_seed1.json
(same law: UMi 28 GHz, LoS by the model); its scenario share is 1 by construction.
--nr 16 / 32 (added 2026-09-30 10:50 CDT for NEXT_EXPERIMENTS_SCALE16e4 ④, before the first Nr 16/32 run; only (UMi28, 16|32, 4) is
calibrated in mix3.py): the SAME checks with the SAME tolerances as NEXT_EXPERIMENTS_38901 §0 -- TMXa |mean - 1| <= 4 MC s.e. (val
stream 8 of that Nr, n = N_VAL = 20000), TMXc LoS within 4 binomial s.e. / shares within 4 s.e. of 1/NS, TMXd |NMSE - probe| <= 0.02
-- against the phase-0 probe of the same Nr (UMi28_mix_16_seed1.json: LoS 0.400, K1 NMSE @ -3 dB 0.3246; UMi28_mix_32_seed1.json:
LoS 0.400, K1 0.3222; ntr 40000 / nte 1000 like the Nr 8 probe).  TMXa PASS at Nr 16 and 32 is the freeze precondition of stage 2.

Checks (tolerances fixed here before the first run; no receiver / BLER anywhere):
  TMXa normalisation: mean ||H||_F^2 / (Nr Nt) on the VALIDATION stream (8), n = N_VAL, within 4 MC s.e. of 1 (the constant
       P_RAW was calibrated on the train stream 7, so this is an out-of-sample check);
  TMXb per-entry power E|H_ab|^2: reported (the ensemble is not required to be entry-wise flat: BS downtilt / sectors);
  TMXc LoS fraction and scenario mix vs the phase-0 probe (phy_results/MIX3_8_seed1.json: LoS 0.273 over 1000 test blocks):
       LoS fraction within 4 binomial s.e. of the pooled probe value, scenario shares within 4 s.e. of 1/3;
  TMXd pilot-stage K=1 Gaussian (LMMSE with the sample covariance of 40000 train draws) NMSE at -3 dB, nu = sigma^2 / Nt:
       within 0.02 of the probe's 0.3150 (headroom.all@-3dB.nmse.K1; same estimator, different draws);
  TMXe T2b pilot decision (erank Rt vs 0.9 Nt) and ensemble effective rank; beamspace top-4 energy (report);
  TMXf generation cost: sample() per call, sample_vecs per 4096.
"""
import argparse, hashlib, json, os, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import common as C
import d2
import mix3

_ap = argparse.ArgumentParser()
_ap.add_argument("prior", nargs="?", default="MIX3", choices=mix3.PRIORS)
_ap.add_argument("--nr", type=int, choices=(8, 16, 32), default=8)
_a = _ap.parse_args()
NR, NT, N_VAL = _a.nr, 4, 20000
PRIOR = _a.prior
OUT = os.path.join(C.CONF, "results", f"testbed_{PRIOR}{'' if NR == 8 else f'_Nr{NR}'}.txt")
PROBE = os.path.join(C.CONF, "results", "review_next", "testbed2_phase0", "phy_results",
                     {"MIX3": f"MIX3_{NR}_seed1.json", "UMi28": f"UMi28_mix_{NR}_seed1.json"}[PRIOR])
NS = mix3.NSCEN[PRIOR]


def main():
    t_start = time.time()
    g = C.make_gen("D2", PRIOR, NR, NT)
    L = [f"# date        : {time.strftime('%Y-%m-%d %H:%M:%S KST')}",
         f"# git commit  : {subprocess.run(['git', '-C', C.CONF, 'rev-parse', '--short=8', 'HEAD'], capture_output=True, text=True).stdout.strip()}",
         f"# content     : testbed_mix3.py -- 3GPP TR 38.901 {PRIOR} (code/mix3.py), Nr={NR} x Nt={NT}; streams from common.train_rng('D2','{PRIOR}',...)",
         f"# calibration : P_RAW={mix3.P_RAW[(PRIOR, NR, NT)]!r}  TRAIN_SHA={mix3.TRAIN_SHA.get((PRIOR, NR, NT))}  (n={mix3.N_CAL}, train stream 7)", ""]
    ok = True
    aux = []
    t0 = time.time()
    H = g._draw(C.train_rng("D2", PRIOR, NR, 8), N_VAL, aux)
    t_val = time.time() - t0
    p = np.sum(np.abs(H) ** 2, (1, 2)) / (NR * NT)
    se = p.std() / np.sqrt(len(p))
    a = abs(p.mean() - 1) <= 4 * se
    ok &= a
    L.append(f"TMXa normalisation (val stream 8, n={N_VAL}): mean ||H||^2/(Nr Nt) = {p.mean():.5f} (s.e. {se:.5f}; 4 s.e. band) "
             f"-> {'PASS' if a else 'FAIL'};  per-block power CV {p.std() / p.mean():.3f}")
    E = np.mean(np.abs(H) ** 2, 0)
    L.append(f"TMXb per-entry E|H_ab|^2: min {E.min():.4f} max {E.max():.4f} (report only)")
    codes = np.empty(N_VAL, int); los = np.empty(N_VAL, bool)
    for c, ix, l in aux:
        codes[ix] = c; los[ix] = l
    pr = json.load(open(PROBE)) if os.path.exists(PROBE) else None
    lf = los.mean(); lp = pr["los_frac"] if pr else np.nan
    se_l = np.sqrt(lp * (1 - lp) / 1000 + lf * (1 - lf) / N_VAL)
    shares = np.bincount(codes, minlength=NS) / N_VAL
    b = abs(lf - lp) <= 4 * se_l and np.all(np.abs(shares - 1 / NS) <= 4 * np.sqrt((1 / NS) * (1 - 1 / NS) / N_VAL + 1e-300))
    ok &= b
    per = ", ".join(f"{mix3.SCEN[c][0]}@{mix3.SCEN[c][1] / 1e9:g}GHz share {shares[c]:.3f} LoS {los[codes == c].mean():.3f}" for c in range(NS))
    L.append(f"TMXc LoS fraction {lf:.4f} vs probe {lp:.3f} (4 s.e. = {4 * se_l:.3f}); {per} -> {'PASS' if b else 'FAIL'}")
    Xtr = g.sample_vecs(C.train_rng("D2", PRIOR, NR, 7), 40000)
    Chat = Xtr.T @ Xtr.conj() / len(Xtr)
    s2 = 10 ** (3 / 10); nu = s2 / NT
    h = H.transpose(0, 2, 1).reshape(N_VAL, NR * NT)
    rng = np.random.default_rng(99)
    q = h + np.sqrt(nu / 2) * (rng.standard_normal(h.shape) + 1j * rng.standard_normal(h.shape))
    est = q @ np.linalg.solve(Chat + nu * np.eye(NR * NT), Chat).T
    nm = np.sum(np.abs(est - h) ** 2) / np.sum(np.abs(h) ** 2)
    kp = pr["headroom"]["all@-3dB"]["nmse"]["K1"] if pr else np.nan
    c_ = abs(nm - kp) <= 0.02
    ok &= c_
    L.append(f"TMXd pilot-stage K=1 Gaussian NMSE @ -3 dB (nu = sigma^2/Nt): {nm:.4f} vs probe {kp:.4f} (|diff| <= 0.02) -> {'PASS' if c_ else 'FAIL'}")
    Rt, Rr, inf = mix3.ensemble_sides_mix3(PRIOR, NR, NT)
    ev = np.linalg.eigvalsh(Chat)
    pil, _ = C.make_pilots("D2", PRIOR, NT, 4, NR)
    F = np.fft.fft(np.fft.fft(H, axis=1, norm="ortho"), axis=2, norm="ortho")
    en = np.sort((np.abs(F) ** 2).reshape(N_VAL, -1), 1)[:, ::-1]
    top4 = np.median(en[:, :4].sum(1) / en.sum(1))
    L.append(f"TMXe erank(Rt) = {d2._erank(np.linalg.eigvalsh(Rt)):.3f} / {NT} (T2b threshold {d2.T2B_ERANK_FRAC * NT:.1f}) -> "
             f"pilots '{pil}' for Tp<=Nt;  erank(C_ens) = {d2._erank(ev):.2f} / {NR * NT};  beamspace top-4 energy median {top4:.3f}")
    rng = np.random.default_rng(7)
    t0 = time.time(); [g.sample(rng) for _ in range(20)]; t1 = (time.time() - t0) / 20
    t0 = time.time(); g.sample_vecs(np.random.default_rng(8), 4096); t2 = time.time() - t0
    L.append(f"TMXf cost: sample() {1e3 * t1:.1f} ms/call (after warm-up), sample_vecs 4096 in {t2:.1f} s, val draw {N_VAL} in {t_val:.1f} s")
    L += ["", f"ALL {'PASS' if ok else 'FAIL'} ({time.time() - t_start:.0f} s CPU)"]
    open(OUT, "w").write("\n".join(L) + "\n")
    print("\n".join(L))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
