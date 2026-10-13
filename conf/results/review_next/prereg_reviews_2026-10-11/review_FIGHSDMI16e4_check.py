"""Read-only CPU dry checks for the pre-run review of NEXT_EXPERIMENTS_FIGHSDMI16e4 (draft v1).  Writes nothing.
Run: cd ~/t2/conf && CUDA_VISIBLE_DEVICES= taskset -c 48-63 ~/miniforge3/envs/torch/bin/python -B <this file>"""
import glob
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, "code")
import numpy as np

import common as C

sha = lambda f: hashlib.sha256(open(f, "rb").read()).hexdigest()[:16]
LL = 112.04253042212595
ok = []


def chk(name, cond, detail=""):
    ok.append(bool(cond))
    print(f"[{'OK' if cond else 'FAIL'}] {name} {detail}")


# ---- 1. b*: the fit file and the runner's own selection in the fits dir the FH tags will link to
f = "results/gmm_fits_D2_DMIB16e4/fit_DMI_Nr8_fullK1024_n160000.npz"
v = repr(float(np.load(f)["ll_val"]))
chk("ll_val repr", v == "112.04253042212595", v)
import arms as A
A.D2_FITS = os.path.join(C.CONF, "results", "gmm_fits_D2_DMIB16e4")
fits, llv, bstar, kron_K = A.gmm_selection("D2", "DMI", 8, 160000)
chk("gmm_selection", bstar == "gmm1024" and llv["gmm1024"] == LL, f"b*={bstar} ll={llv[bstar]!r} kron_K={kron_K} "
    f"kron ll={llv.get('kron')!r}; loaded {sorted(fits)}")
print("   llv:", {k: round(x, 3) for k, x in sorted(llv.items(), key=lambda t: -t[1])})

# ---- 2. constants
chk("HISNR_SKIP0 / DEV_SKIP0 / PID", (C.HISNR_SKIP0, C.DEV_SKIP0, C.PID["DMI"]) == (10000, 2560, 14),
    f"{C.HISNR_SKIP0} {C.DEV_SKIP0} {C.PID['DMI']}")
chk("C2 snrs", [float(s) for s in C.CELLS["C2"]["snrs"]] == [-3, 0, 3, 6, 9, 12, 15], str(C.CELLS["C2"]))

# ---- 3. ALD records
t = json.load(open("results/ald/tune_PILDMI.json"))
print("   tune:", {k: t[k] for k in ("tag", "ckpt", "ckpt_sha", "git", "c", "beta", "n_dev", "dev_skip", "rotation", "train_prior",
                                     "doppler", "stop", "seed") if k in t})
chk("tune ckpt == $CK and sha", t["ckpt"] == "ckpt/d2sx_DMI_N160000_a1_best.pt" and t["ckpt_sha"] == "dc784649f1e9b890")
chk("tune stop/v keys for 6..15", all(str(float(s)) in t["stop"] and str(float(s)) in t["v"] for s in (6, 9, 12, 15)))
chk("tune dev", (t["dev_skip"], t["n_dev"]) == (2560, 512))
zd = np.load("results/ald/pilots_PILDMI_dev.npz"); zt = np.load("results/ald/pilots_PILDMI_test.npz"); za = np.load("results/ald/ald_PILDMI.npz")
g = lambda z: {k: (str(z[k]) if z[k].dtype.kind in "US" else float(z[k])) for k in ("rotation", "doppler", "train_prior", "prior",
                                                                                     "fits_tag", "skip", "n") if k in z.files}
print("   pilots dev :", g(zd), "b", zd["b"].shape); print("   pilots test:", g(zt), "b", zt["b"].shape)
print("   ald test   :", g(za), "hhat", za["hhat"].shape, "ckpt_sha", str(za["ckpt_sha"]), "prov", json.loads(str(za["prov"])))
chk("dev pilots guard == what regen --set hisnr will write (rotation -1, doppler -1, train_prior DMI)",
    (float(zd["rotation"]), float(zd["doppler"]), str(zd["train_prior"])) == (-1.0, -1.0, "DMI"))
chk("ald test ckpt_sha", str(za["ckpt_sha"]) == "dc784649f1e9b890")

# ---- 4. pick
pk = json.load(open("results/sparse/pick_DMI_C2.json"))
chk("pick per_snr has 6 9 12 15 + rho", all(str(s) in pk["per_snr"] for s in (6, 9, 12, 15)) and "rho_sbl" in pk and "rho_omp" in pk,
    f"rho_sbl {pk.get('rho_sbl')} rho_omp {pk.get('rho_omp')} per_snr {pk['per_snr']}")

# ---- 5. original raws: the control references (chunk skip0 n40 at +6..+15), meta, max skip
ROWS = {"DMIB16e4": "R0-pilot R1-turbo R2-ours-G R3-bigamp M-ours-bstar M-ours-dscore-C-V1 R5-genie".split(),
        "SPDMI": "SBL-loop SBL-pilot OMP-pilot R5-genie".split(), "ALDDMI": "ALD-pilot R5-genie".split()}
for tag, arms in ROWS.items():
    for s in (6, 9, 12, 15):
        fs = glob.glob(f"raw_{tag}/D2_*_snr{s}_skip0_n40.npz")
        if len(fs) != 1:
            chk(f"raw_{tag} +{s} chunk0", False, str(fs)); continue
        with np.load(fs[0]) as z:
            miss = [f"{a}|{q}" for a in arms for q in C.KEYS_RAW if f"{a}|{q}" not in z.files]
            gg = lambda k: str(z[k].item() if z[k].shape == () else z[k]) if k in z.files else "(absent)"
            meta = dict(bstar=gg("meta|bstar"), kron_K=gg("meta|kron_K"), ll=gg("meta|ll_val|gmm1024"), ntrain=gg("meta|ntrain"),
                        ck=gg("meta|stagec_ckpt_id")[:90], git=gg("run|git"), iters=gg("run|iters"), em=gg("meta|em_sec")[:12])
            cond = (not miss and meta["bstar"] == "gmm1024" and abs(float(meta["ll"]) - LL) <= 1e-9 and int(float(meta["ntrain"])) == 160000
                    and meta["kron_K"] != "(absent)" and meta["em"] != "(absent)")
            if tag == "SPDMI":
                e = pk["per_snr"][str(s)]
                cond = cond and meta["ck"] == "(absent)" and json.loads(gg("meta|sparse")) == dict(
                    rho_sbl=pk["rho_sbl"], rho_omp=pk["rho_omp"], n_em=e["n_em"], L=e["L"])
            else:
                cond = cond and "sha256[:16]=dc784649f1e9b890" in gg("meta|stagec_ckpt_id") and "role=best" in gg("meta|stagec_ckpt_id")
            if tag == "ALDDMI":
                cond = cond and gg("meta|ald_file") == "/home/HTJ/t2/conf/results/ald/ald_PILDMI.npz sha256[:16]=b0145dac7b7076aa"
                meta["ald_file"] = gg("meta|ald_file")
            chk(f"raw_{tag} +{s} dB chunk0 ({os.path.basename(fs[0])})", cond, f"missing {miss[:3]} meta {meta}" if s == 6 or not cond else "")
            if s == 6:
                print("     arms in file:", sorted({k.split('|')[0] for k in z.files if k.endswith('|blk_err')}))
PAT = re.compile(r"_snr(-?\d+)_skip(\d+)_n(\d+)\.npz$")
for tag in ("DMIB16e4", "DMIB16e4last", "PILDMI", "ALDDMI", "SPDMI"):
    m = [PAT.search(x) for x in glob.glob(f"raw_{tag}/D2_*.npz")]
    chk(f"raw_{tag} max skip", max(int(x[2]) for x in m) == 2520 and {int(x[3]) for x in m} == {40},
        f"{len(m)} files, max skip {max(int(x[2]) for x in m)}, snrs {sorted({int(x[1]) for x in m})}")
chk("raw_DMI empty", os.path.isdir("raw_DMI") and not os.listdir("raw_DMI"))
others = [d for d in glob.glob("raw_*") if "DMI" in d]
print("   every raw_*DMI* dir:", sorted(others))

# ---- 6. test pool size and trial stream -> test pool
import dmimo
gen = C.make_gen("D2", "DMI", 8, 4)
rng = C.trial_rng("D2", "DMI", 8, 16, 4, 6)
chk("trial stream -> test pool; pool size", dmimo._which(rng, "DMI", 8) == "test" and len(gen.idx["test"]) == 60700,
    f"which={dmimo._which(rng, 'DMI', 8)} test={len(gen.idx['test'])} fit={len(gen.idx['fit'])} val={len(gen.idx['val'])}")
n = 20480
print(f"   expected distinct pairs among {n} draws from 60700: {60700 * (1 - (1 - 1 / 60700) ** n):.0f}; "
      f"expected draws that repeat a pair of trials 0..2559 of the same SNR: {n * (1 - (1 - 1 / 60700) ** 2560):.0f}")

# ---- 7. is an ALD estimate 'the same FILE whenever made'?  arrays yes (control), bytes no (zip member timestamps)
for new, ref in (("results/ald/ald_FHCALDSRP.npz", "results/ald/ald_PILSRP.npz"), ("results/ald/ald_FHCALDSRB.npz", "results/ald/ald_PILSRB.npz")):
    if os.path.exists(new) and os.path.exists(ref):
        a, b = np.load(new), np.load(ref)
        same = all(np.array_equal(a[k], b[k]) for k in ("hhat", "b", "v"))
        import zipfile
        ta = zipfile.ZipFile(new).infolist()[0].date_time; tb = zipfile.ZipFile(ref).infolist()[0].date_time
        print(f"   {new} vs {ref}: arrays hhat/b/v identical {same}; file sha {sha(new)} vs {sha(ref)}; zip member time {ta} vs {tb}; "
              f"prov git {json.loads(str(a['prov']))['git']} vs {json.loads(str(b['prov']))['git']}")

# ---- 8. the reuse branch of ald_new on an existing hisnr estimate (exactly the script's one-liner)
for E in ("results/ald/ald_PILSRP_hisnr.npz", "results/ald/ald_PILSRB_hisnr.npz"):
    if os.path.exists(E):
        print(f"   reuse-branch one-liner on {E}: prov git = {json.loads(str(np.load(E)['prov']))['git']!r}; skip {int(np.load(E)['skip'])}; "
              f"hhat {np.load(E)['hhat'].shape}; snrs {np.load(E)['snrs']}")
print(f"\n{sum(ok)} / {len(ok)} checks OK")
