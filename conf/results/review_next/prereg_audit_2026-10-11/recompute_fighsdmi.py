#!/usr/bin/env python
"""recompute_fighsdmi.py -- independent RECORD AUDIT (Fable 5.1 subagent, read-only) of NEXT_EXPERIMENTS_FIGHSDMI16e4.md §6 (6.1-6.4)
and of what commit 42fd4e03 wrote about that run elsewhere (docs/EXPERIMENTS.md last row, docs/RESULTS.md §25.6 bullet,
conference/figures/README.md rows, conf/DECISIONS.md last two lines, WORK_QUEUE.md, records/paper_f21dmihs.txt).

Run from anywhere (the script chdirs to ~/t2/conf):
  CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 taskset -c 0-15 ~/miniforge3/envs/torch/bin/python -B \
      results/review_next/prereg_audit_2026-10-11/recompute_fighsdmi.py > results/review_next/prereg_audit_2026-10-11/recompute_fighsdmi.out

Own numpy reader (chunk()) over the raw npz files; analysis.load_raw / hisnr_report / s6_fighsroom_gen.py / fighs_merge are NOT imported.
Count tables, figure records and the registration are compared AGAINST, never used as input.  Expected values (EXP62 etc.) were
retyped by the auditor from §6 of the record, so every number is checked three ways: record text == retyped == own recount.
Writes stdout only.  Process pool of 12 single-thread workers (<= 16 threads in total).
Sections: A inputs / registration  B new raws (3 x 2048)  C original raws (3 x 448)  D controls  E count tables + §6.2  F §6.3
G figure records  H logs / manifests / timeline / git  I §6.4  J other documents of 42fd4e03.
"""
import glob, hashlib, json, os, re, subprocess, sys
from datetime import datetime, timedelta
from multiprocessing import Pool
from zoneinfo import ZoneInfo

import numpy as np
from scipy.stats import fisher_exact

os.chdir("/home/HTJ/t2/conf")
RV = "results/review_next"; AUD = f"{RV}/prereg_audit_2026-10-11"; REG = f"{RV}/NEXT_EXPERIMENTS_FIGHSDMI16e4.md"
FIGD = "../conference/figures"; REC = f"{FIGD}/records"
RUNC, S6C = "e5caaccb", "42fd4e03"
CDT, KST = ZoneInfo("America/Chicago"), ZoneInfo("Asia/Seoul")
HS = (6, 9, 12, 15); ALL = (-3, 0, 3) + HS; N2, N1 = 20480, 2560
KEYS = ("blk_err", "ber", "nmse", "tauL_gmean", "alphaD", "tauL_clip_frac", "alphaD_clip")     # = common.KEYS_RAW (checked in A0)
NAME = re.compile(r"^D2_C2_DMI_Nr8_T16_Tp4_dft_snr(-?\d+)_skip(\d+)_n(\d+)\.npz$")
TAGS = ("FHDMIB16e4", "FHSPDMI", "FHALDDMI"); ORIGS = ("DMIB16e4", "SPDMI", "ALDDMI")
ARMS = {"FHDMIB16e4": "R0-pilot R1-turbo R2-ours-G R3-bigamp M-ours-bstar M-ours-dscore-C-V1 R5-genie".split(),
        "FHSPDMI": "SBL-loop SBL-pilot OMP-pilot R5-genie".split(), "FHALDDMI": "ALD-pilot R5-genie".split()}
V1, BST, GE = "M-ours-dscore-C-V1", "M-ours-bstar", "R5-genie"
# ---- retyped from §6.2 of the record (legend order): arm -> (source tag, k at +6/+9/+12/+15 of 20480, original k of 2560)
EXP62 = {V1: ("FHDMIB16e4", [21, 2, 0, 0], [4, 0, 0, 0]),
         "ALD-pilot": ("FHALDDMI", [58, 8, 1, 0], [4, 1, 1, 0]),
         BST: ("FHDMIB16e4", [27, 8, 2, 0], [7, 0, 0, 0]),
         "R2-ours-G": ("FHDMIB16e4", [308, 54, 6, 2], [31, 12, 0, 0]),
         "R1-turbo": ("FHDMIB16e4", [767, 153, 20, 6], [90, 23, 4, 0]),
         "R3-bigamp": ("FHDMIB16e4", [4194, 3448, 4530, 4940], [554, 437, 573, 603]),
         "R0-pilot@1": ("FHDMIB16e4", [2390, 634, 145, 39], [302, 81, 23, 3]),
         "SBL-loop": ("FHSPDMI", [192, 20, 4, 1], [16, 5, 0, 0]),
         "SBL-pilot": ("FHSPDMI", [244, 41, 7, 1], [20, 3, 1, 0]),
         "OMP-pilot": ("FHSPDMI", [601, 114, 26, 12], [80, 24, 3, 0]),
         GE: ("FHDMIB16e4", [7, 1, 0, 0], [0, 0, 0, 0])}
ORDER = list(EXP62)
OSRC = {a: {"FHDMIB16e4": "DMIB16e4", "FHSPDMI": "SPDMI", "FHALDDMI": "ALDDMI"}[EXP62[a][0]] for a in ORDER}
LABEL = {V1: "Proposed (diffusion prior)", "ALD-pilot": "Annealed Langevin (plug-in)", BST: "GMM prior", "R2-ours-G": "Gaussian prior",
         "R1-turbo": "Turbo LMMSE receiver", "R3-bigamp": "BiG-AMP", "R0-pilot@1": "Pilot-only LMMSE", "SBL-loop": "SBL (in loop)",
         "SBL-pilot": "SBL (pilot-only)", "OMP-pilot": "OMP (pilot-only)", GE: "Perfect CSI"}
BARS = (V1, BST, "R2-ours-G", GE)                      # paper_f16deep.BARS (checked in G0)
CKID = "sha256[:16]=dc784649f1e9b890 epoch=1142 best_epoch=1142 role=best 8x4"
LLV = "112.04253042212595"
ALDF = "/home/HTJ/t2/conf/results/ald/ald_PILDMI_hisnr.npz"

RES = []; NVAL = [0]; NARR = [0]
def chk(name, ok, detail="", n=1):
    RES.append((name, bool(ok))); NVAL[0] += n
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f"\n        -- {detail}" if detail else ""), flush=True)
    return bool(ok)
def sha16(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]
def sh(c):
    return subprocess.run(c, shell=True, capture_output=True, text=True).stdout.rstrip("\n")
def rd(p):
    return open(p, encoding="utf-8", errors="replace").read()
def wil(k, n, z=1.959963984540054):
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h
def fmt(k, n):
    lo, hi = wil(k, n); return f"{k / n:.2e}", f"{lo:.2e}", f"{hi:.2e}"
def fis(hi, lo):                                       # one-sided: BLER at the higher SNR (hi) greater than at the lower (lo)
    return fisher_exact([[hi[0], hi[1] - hi[0]], [lo[0], lo[1] - lo[0]]], alternative="greater").pvalue
def cdt(ts):
    return datetime.fromtimestamp(ts, CDT)


def chunk(path):
    """own reader of ONE raw chunk: file-name fields, run|*, selected meta|*, and per arm the blk_err matrix reduced to
    (failures@last, failures@first, shape, n non-finite cells, has '|failed' key, sum of '|failed') + the failing-row index list."""
    b = os.path.basename(path); m = NAME.match(b)
    o = {"file": b, "mtime": os.stat(path).st_mtime, "nm": (int(m[1]), int(m[2]), int(m[3])) if m else None}
    with np.load(path) as z:
        F = set(z.files)
        o["git"] = str(z["run|git"]); o["run"] = (float(z["run|snr"]), int(z["run|skip"]), int(z["run|n"]), int(z["run|iters"]), int(z["run|seed"]))
        o["meta"] = {k[5:]: str(z[k]) for k in F if k in ("meta|bstar", "meta|kron_K", "meta|ntrain", "meta|ll_val|gmm1024", "meta|ll_val|kron",
                                                         "meta|stagec_ckpt_id", "meta|sparse", "meta|rotation", "meta|ald_file", "meta|ald_tune")}
        o["arms"] = {}
        for a in sorted({k.split("|")[0] for k in F if k.endswith("|blk_err")}):
            e = np.asarray(z[a + "|blk_err"], dtype=float)
            bad = ~np.isfinite(e)
            last = np.where(bad[:, -1], 1.0, e[:, -1]); first = np.where(bad[:, 0], 1.0, e[:, 0])
            o["arms"][a] = (int(last.sum()), int(first.sum()), e.shape, int(bad.sum()), (a + "|failed") in F,
                            int(z[a + "|failed"].sum()) if (a + "|failed") in F else 0, np.flatnonzero(last > 0).tolist(),
                            bool(np.isin(e[~bad], (0.0, 1.0)).all()))
        o["nkeys"] = len(F)
    return o


def cmp_files(args):
    """bit comparison (NaN == NaN) of the keys `keys` between the same-named chunk of two raw dirs -> (n compared, [differing])"""
    da, db, f, keys = args
    bad = []
    with np.load(os.path.join(da, f)) as x, np.load(os.path.join(db, f)) as y:
        for k in keys:
            if k not in x.files or k not in y.files or x[k].shape != y[k].shape or x[k].dtype != y[k].dtype or not np.array_equal(x[k], y[k], equal_nan=True):
                bad.append((f, k))
    return len(keys), bad


def main():
    print(f"# recompute_fighsdmi.py  {datetime.now(CDT):%Y-%m-%d %H:%M:%S %Z} (= {datetime.now(KST):%H:%M KST})  HEAD {sh('git rev-parse --short HEAD')}  affinity {len(os.sched_getaffinity(0))} cpus")
    pool = Pool(12)

    # ================================================================== A. inputs / registration
    print("\n# A. inputs / registration")
    cm = re.search(r"^KEYS_RAW = \((.*?)\)", rd("code/common.py"), re.M)
    chk("A0 common.KEYS_RAW (read as text) = the 7 keys this script compares; common.HISNR_SKIP0 = 10000; PID['DMI'] = 14",
        cm and tuple(re.findall(r'"(\w+)"', cm[1])) == KEYS and re.search(r"^HISNR_SKIP0 = 10000\b", rd("code/common.py"), re.M) and re.search(r'"DMI": 14,', rd("code/common.py")), n=3)
    script = rd("code/run_fighsdmi16e4.sh")
    rows = [l.split("|") for l in re.search(r"^ROWS='(.*?)'$", script, re.S | re.M)[1].split("\n")]
    want_rows = [["FHDMIB16e4", "C2", "DMI", "DMIB16e4", "ckpt/d2sx_DMI_N160000_a1_best.pt", "dc784649f1e9b890", "best", "gmm1024", "-", LLV, "-", "DMIB16e4", "-", "", " ".join(ARMS["FHDMIB16e4"])],
                 ["FHSPDMI", "C2", "DMI", "DMIB16e4", "-", "-", "-", "gmm1024", "-", LLV, "FHDMIB16e4", "SPDMI", "results/sparse/pick_DMI_C2.json:8f72c113efb91b0b", "", " ".join(ARMS["FHSPDMI"])],
                 ["FHALDDMI", "C2", "DMI", "DMIB16e4", "ckpt/d2sx_DMI_N160000_a1_best.pt", "dc784649f1e9b890", "best", "gmm1024", "-", LLV, "FHDMIB16e4", "ALDDMI", "-", "--ald-file " + ALDF, " ".join(ARMS["FHALDDMI"])]]
    chk("A1 ROWS of code/run_fighsdmi16e4.sh = §1 of the registration (3 rows x 15 fields: tags, prior DMI, fits DMIB16e4, ckpt + sha dc784649f1e9b890 + role best, b* gmm1024, kron K '-', ll_val 112.04253042212595, REF, ORIG, pick:sha, --ald-file, arms in order)",
        rows == want_rows, str([(a, b) for r, w in zip(rows, want_rows) for a, b in zip(r, w) if a != b]), n=45)
    reg = rd(REG).split("\n"); old = sh(f"git show {RUNC}:conf/{REG}").split("\n")
    i6 = next(i for i, l in enumerate(reg) if l.startswith("## 6. ")); S6 = reg[i6:]
    numstat = sh(f"git diff --numstat {RUNC} {S6C} -- {REG}").split()
    hunks = re.findall(r"^@@ .*? @@", sh(f"git diff {RUNC} {S6C} -- {REG}"), re.M)
    chk("A2 registration: git diff e5caaccb 42fd4e03 = +71 -0 in ONE hunk; the 45 lines of e5caaccb are the first 45 lines of the working-tree file byte for byte (머리말 / §1 / §3 / §5 frozen); working tree == 42fd4e03; '## 6.' at line 49",
        numstat[:2] == ["71", "0"] and len(hunks) == 1 and reg[:len(old)] == old and len(old) == 45 and not sh(f"git diff {S6C} -- {REG}") and i6 + 1 == 49,
        f"numstat {numstat[:2]}, hunks {hunks}, old lines {len(old)}, §6 header line {i6 + 1}", n=4)
    disk = {"code/run_fighsdmi16e4.sh": "b32cfd92db26e8e3", "ckpt/d2sx_DMI_N160000_a1_best.pt": "dc784649f1e9b890", "results/sparse/pick_DMI_C2.json": "8f72c113efb91b0b",
            "results/ald/ald_PILDMI.npz": "b0145dac7b7076aa", "results/ald/pilots_PILDMI_test.npz": "1e8cc99169b3f18c", "results/ald/tune_PILDMI.json": "1e7824c1bae10376"}
    got = {p: sha16(p) for p in disk}
    chk("A3 on disk sha256[:16] = §1 / §5: script b32cfd92db26e8e3, ckpt dc784649f1e9b890, pick 8f72c113efb91b0b, ALD test estimate b0145dac7b7076aa, test pilots 1e8cc99169b3f18c, tune 1e7824c1bae10376; conf/code + Demo have NO diff e5caaccb..HEAD and no uncommitted change",
        got == disk and not sh(f"git diff --stat {RUNC} HEAD -- code ../Demo") and not sh("git status --porcelain code ../Demo"), str({p: v for p, v in got.items() if disk[p] != v}), n=8)
    ALDSHA = sha16(ALDF); z = np.load(ALDF); prov = json.loads(str(z["prov"])); tn = json.loads(str(z["tune"])); TUNE = json.load(open("results/ald/tune_PILDMI.json"))
    chk("A4 new-trial ALD estimate ald_PILDMI_hisnr.npz: sha256[:16] 01d221fb66ceada3 (§6.4), untracked ('git 밖'), prov.git e5caaccb, prov.ckpt_sha dc784649f1e9b890, prov.ald_py_sha = sha of code/ald.py now, skip 10000, snrs 6/9/12/15, hhat (4, 20480, 32), embedded tune == tune_PILDMI.json (whole dict)",
        ALDSHA == "01d221fb66ceada3" and not sh(f"git ls-files {ALDF}") and prov["git"] == RUNC and prov["ckpt_sha"] == "dc784649f1e9b890" and prov["ald_py_sha"] == sha16("code/ald.py")
        and int(z["skip"]) == 10000 and z["snrs"].tolist() == [6.0, 9.0, 12.0, 15.0] and z["hhat"].shape == (4, N2, 32) and tn == TUNE,
        f"sha {ALDSHA}, prov {prov}, tune c {tn.get('c')} beta {tn.get('beta')}, dev_skip {TUNE.get('dev_skip')} n_dev {TUNE.get('n_dev')}", n=9)
    pz = np.load("results/ald/pilots_PILDMI_hisnr.npz")
    chk("A5 pilots_PILDMI_hisnr.npz (regen output): skip 10000, n 20480, snrs 6/9/12/15, prior DMI cell C2 fits_tag DMIB16e4; its pilot observations b == the 'b' stored in the estimate file (same trials)",
        int(pz["skip"]) == 10000 and int(pz["n"]) == N2 and pz["snrs"].tolist() == [6.0, 9.0, 12.0, 15.0] and (str(pz["prior"]), str(pz["cell"]), str(pz["fits_tag"])) == ("DMI", "C2", "DMIB16e4") and np.array_equal(pz["b"], z["b"]), n=6)

    # ================================================================== B. new raws
    print("\n# B. new raws (own reader, 3 x 2048 chunks)")
    FILES = {t: sorted(glob.glob(f"raw_{t}/*")) for t in TAGS}
    BY = {t: pool.map(chunk, [f for f in FILES[t] if f.endswith(".npz")], chunksize=16) for t in TAGS}
    chk("B0 each raw dir holds exactly 2048 entries, all D2_C2_DMI_Nr8_T16_Tp4_dft_snr<S>_skip<K>_n40.npz, all readable",
        all(len(FILES[t]) == 2048 == len(BY[t]) and all(o["nm"] for o in BY[t]) for t in TAGS), str({t: len(FILES[t]) for t in TAGS}), n=3)
    PLAN = {(s, 10000 + 40 * k, 40) for s in HS for k in range(512)}
    PICK = json.load(open("results/sparse/pick_DMI_C2.json"))
    CNT, CNT1, FAILROWS, MT = {}, {}, {}, {}
    bp, bg, bm, bs_, br = [], [], [], [], []
    for t in TAGS:
        L = BY[t]
        if {o["nm"] for o in L} != PLAN or len({o["nm"] for o in L}) != 2048 or any((int(o["run"][0]), o["run"][1], o["run"][2]) != o["nm"] or o["run"][0] != int(o["run"][0]) for o in L): bp.append(t)
        if {o["git"] for o in L} != {RUNC} or {o["run"][3] for o in L} != {16} or {o["run"][4] for o in L} != {20260926}: bg.append((t, sorted({o["git"] for o in L})))
        for o in L:
            mt = o["meta"]; why = None
            if (mt.get("ntrain"), mt.get("bstar"), mt.get("ll_val|gmm1024")) != ("160000.0", "gmm1024", LLV): why = "ntrain/bstar/ll_val"
            elif t == "FHSPDMI" and "stagec_ckpt_id" in mt: why = "SP row has stagec_ckpt_id"
            elif t != "FHSPDMI" and mt.get("stagec_ckpt_id") != CKID: why = "ckpt id"
            elif t == "FHSPDMI" and json.loads(mt.get("sparse", "null")) != dict(rho_sbl=PICK["rho_sbl"], rho_omp=PICK["rho_omp"], n_em=PICK["per_snr"][str(o["nm"][0])]["n_em"], L=PICK["per_snr"][str(o["nm"][0])]["L"]): why = "sparse != pick"
            elif t != "FHSPDMI" and "sparse" in mt: why = "unexpected sparse"
            elif "rotation" in mt: why = "unexpected rotation"
            elif t == "FHALDDMI" and (mt.get("ald_file") != f"{ALDF} sha256[:16]={ALDSHA}" or json.loads(mt.get("ald_tune", "null")) != TUNE): why = "ald_file / ald_tune"
            elif t != "FHALDDMI" and ("ald_file" in mt or "ald_tune" in mt): why = "unexpected ald_file"
            if why: bm.append((t, o["file"], why, mt)); break
        if any(sorted(o["arms"]) != sorted(ARMS[t]) for o in L): bs_.append((t, "arm set"))
        if any(v[2] != (40, 16) for o in L for v in o["arms"].values()): bs_.append((t, "shape"))
        if any(not v[7] for o in L for v in o["arms"].values()): bs_.append((t, "blk_err not in {0,1}"))
        if any(v[3] or v[4] or v[5] for o in L for v in o["arms"].values()): br.append(t)
        c = {a: {s: 0 for s in HS} for a in ARMS[t]}; c1 = {s: 0 for s in HS}; fr = {a: {s: [] for s in HS} for a in ARMS[t]}
        for o in L:
            s, sk, _ = o["nm"]
            for a, v in o["arms"].items():
                c[a][s] += v[0]; fr[a][s] += [sk + i for i in v[6]]
                if a == "R0-pilot": c1[s] += v[1]
        CNT[t] = c; CNT1[t] = c1; FAILROWS[t] = fr; MT[t] = (min(o["mtime"] for o in L), max(o["mtime"] for o in L))
    chk("B1 trial plan: per raw 2048 chunks = {+6,+9,+12,+15} x skip 10000..30440 step 40 x n 40, each exactly once (= trials 10000..30479 once per SNR, n = 20480); run|snr/skip/n == file name", not bp, str(bp), n=3 * 2048)
    chk("B2 run|git == 'e5caaccb' in every chunk (one value per raw; no '+dirty'); run|iters 16; run|seed 20260926", not bg, str(bg), n=3 * 2048)
    chk("B3 meta in every chunk: ntrain 160000 / bstar gmm1024 / ll_val|gmm1024 112.04253042212595; stagec_ckpt_id sha dc784649f1e9b890 epoch 1142 role best (rows 1, 3; absent in SP); meta|sparse == pick_DMI_C2.json per SNR (SP only); no meta|rotation; meta|ald_file == abs path + sha 01d221fb66ceada3 and meta|ald_tune == tune_PILDMI.json (ALD row only)",
        not bm, str(bm[:2]), n=3 * 2048)
    print(f"   (info) meta|kron_K values: {sorted({o['meta'].get('kron_K') for t in TAGS for o in BY[t]})}, meta|ll_val|kron: {sorted({o['meta'].get('ll_val|kron') for t in TAGS for o in BY[t]})} (best kron candidate, not selected: b* is the full-K gmm1024)")
    chk("B4 arm set of every chunk = the row's ARMS; blk_err shape (40, 16); every finite blk_err entry is 0 or 1", not bs_, str(bs_))
    chk("B5 raised blocks 0: no '<arm>|failed' key, no non-finite blk_err entry (any iteration) in any of the 6144 chunks", not br, str(br))
    jobs = [(f"raw_{t}", "raw_FHDMIB16e4", o["file"], tuple(f"{GE}|{q}" for q in KEYS + ("guardH",))) for t in ("FHSPDMI", "FHALDDMI") for o in BY[t]]
    r = pool.map(cmp_files, jobs, chunksize=32); nb = sum(x[0] for x in r); bad = [b for x in r for b in x[1]]; NARR[0] += nb
    chk(f"B6 R5-genie bit-identical across the three new raws: FHSPDMI and FHALDDMI vs FHDMIB16e4, every chunk x (KEYS_RAW 7 + guardH) = {nb} arrays, NaN == NaN, dtype and shape equal",
        not bad and nb == 2 * 2048 * 8, str(bad[:3]), n=0)
    g = {t: [CNT[t][GE][s] for s in HS] for t in TAGS}
    print("   genie failures per SNR: " + " · ".join(f"{t} {v}" for t, v in g.items()))
    print("   failing stream trials (own; trial = chunk skip + row): " + "; ".join(f"{a} {s:+d} dB {FAILROWS[t][a][s]}" for t, a, s in (("FHDMIB16e4", V1, 9), ("FHDMIB16e4", GE, 6), ("FHDMIB16e4", GE, 9), ("FHDMIB16e4", BST, 12), ("FHALDDMI", "ALD-pilot", 12))))

    def newk(a, s):
        t = EXP62[a][0]; return CNT1[t][s] if a == "R0-pilot@1" else CNT[t][a][s]

    # ================================================================== C. original raws
    print("\n# C. original raws (3 x 448 chunks)")
    OB = {o: pool.map(chunk, sorted(glob.glob(f"raw_{o}/D2_*.npz")), chunksize=16) for o in ORIGS}
    OC, OC1 = {}, {}; bad = []
    for o, L in OB.items():
        if {x["nm"] for x in L} != {(s, 40 * k, 40) for s in ALL for k in range(64)} or len(L) != 448 or len(os.listdir(f"raw_{o}")) != 448: bad.append((o, "plan", len(L)))
        if any(v[3] or v[4] for x in L for v in x["arms"].values()): bad.append((o, "raised / non-finite"))
        c, c1 = {}, {s: 0 for s in ALL}
        for x in L:
            for a, v in x["arms"].items():
                c.setdefault(a, {s: 0 for s in ALL})[x["nm"][0]] += v[0]
                if a == "R0-pilot": c1[x["nm"][0]] += v[1]
        OC[o], OC1[o] = c, c1
        print(f"   raw_{o}: {len(L)} chunks, run|git {sorted({x['git'] for x in L})}, arms {len(c)}, max skip {max(x['nm'][1] for x in L)}")
    chk("C1 original raws DMIB16e4 / SPDMI / ALDDMI: 448 chunks = 7 SNR x skip 0..2520 step 40 (n = 2560 per SNR), nothing else in the dirs, no raised / non-finite block; run|git one value each (4131a3b0 / 29cf411d / 29cf411d)",
        not bad and [sorted({x["git"] for x in OB[o]}) for o in ORIGS] == [["4131a3b0"], ["29cf411d"], ["29cf411d"]], str(bad), n=3 * 448)
    def origk(a, s):
        o = OSRC[a]; return OC1[o][s] if a == "R0-pilot@1" else OC[o][a][s]
    ORIG7 = {a: [(origk(a, s), N1) for s in ALL] for a in ORDER}
    MERGED = {a: ORIG7[a][:3] + [(newk(a, s), N2) for s in HS] for a in ORDER}
    used = {d: max(int(NAME.match(os.path.basename(f))[2]) for f in glob.glob(f"{d}/D2_*.npz")) for d in ("raw_DMIB16e4", "raw_DMIB16e4last", "raw_PILDMI", "raw_ALDDMI", "raw_SPDMI")}
    chk("C2 (frozen 머리말, context) the five earlier DMI raws end at skip 2520; raw_DMI/ is empty; tune_PILDMI.json dev_skip 2560 n_dev 512 -> trials 10000..30479 unused before this run (by file name / record)",
        set(used.values()) == {2520} and os.path.isdir("raw_DMI") and not os.listdir("raw_DMI") and (TUNE.get("dev_skip"), TUNE.get("n_dev")) == (2560, 512), str(used), n=7)

    # ================================================================== D. controls
    print("\n# D. controls (phase C)")
    bad = []; tot = 0; per = {}
    for t, o in zip(TAGS, ORIGS):
        c = t.replace("FH", "FHC", 1); fs = sorted(os.listdir(f"raw_{c}"))
        if fs != sorted(f"D2_C2_DMI_Nr8_T16_Tp4_dft_snr{s}_skip0_n40.npz" for s in HS): bad.append((c, "names", fs))
        r = pool.map(cmp_files, [(f"raw_{c}", f"raw_{o}", f, tuple(f"{a}|{q}" for a in ARMS[t] for q in KEYS)) for f in fs]); n = sum(x[0] for x in r); d = [b for x in r for b in x[1]]
        gits = sorted({str(np.load(f"raw_{c}/{f}")["run|git"]) for f in fs})
        txt = rd(f"{RV}/{c}_control.txt"); m = re.search(r"control raw_(\w+) vs \['raw_(\w+)'\]: (\d+) chunk files \(expected (\d+)\), arms (\[.*?\]), (\d+) \(chunk, arm, key\) comparisons, (\d+) differ", txt)
        if d or gits != [RUNC] or not m or (m[1], m[2], int(m[3]), int(m[4]), eval(m[5]), int(m[6]), int(m[7])) != (c, o, 4, 4, ARMS[t], n, 0) or txt.rstrip().split("\n")[-1] != "CONTROL: OK": bad.append((c, n, d[:2], gits, m and m.groups()))
        tot += n; per[c] = n
    NARR[0] += tot
    chk("D1 receiver controls raw_FHC{DMIB16e4,SPDMI,ALDDMI} (4 chunks each = trials 0..39 at +6/+9/+12/+15 dB; run|git e5caaccb) vs the ORIGINAL raws: every arm x KEYS_RAW bit-identical (NaN == NaN); 196 / 112 / 56 comparisons, 0 differ = the *_control.txt lines; last line 'CONTROL: OK'",
        not bad and per == {"FHCDMIB16e4": 196, "FHCSPDMI": 112, "FHCALDDMI": 56}, str(bad) + str(per), n=12)
    A, B = np.load("results/ald/ald_FHCALDDMI.npz"), np.load("results/ald/ald_PILDMI.npz")
    txt = rd(f"{RV}/FHCALDDMI_aldcontrol.txt"); NARR[0] += 3
    chk("D2 ALD estimator control: ald_FHCALDDMI.npz hhat (7, 2560, 32) / b / v bit-identical to ald_PILDMI.npz (also nmse, snrs, skip, tune); prov.git e5caaccb; file: 'max|diff| 0, differing none' + 'CONTROL-ALD: OK'",
        all(A[k].shape == B[k].shape and np.array_equal(A[k], B[k]) for k in ("hhat", "b", "v", "nmse", "snrs", "skip")) and str(A["tune"]) == str(B["tune"]) and A["hhat"].shape == (7, N1, 32)
        and json.loads(str(A["prov"]))["git"] == RUNC and "hhat (7, 2560, 32), keys hhat b v, max|diff| 0, differing none" in txt and txt.rstrip().split("\n")[-1] == "CONTROL-ALD: OK", n=8)
    chk("D3 FHC copies of the frozen ALD records = the originals (tune json, dev pilots, test pilots: same sha256)",
        all(hashlib.sha256(open(f"results/ald/{x}_FHCALDDMI{y}", "rb").read()).digest() == hashlib.sha256(open(f"results/ald/{x}_PILDMI{y}", "rb").read()).digest() for x, y in (("tune", ".json"), ("pilots", "_dev.npz"), ("pilots", "_test.npz"))), n=3)
    ctl_log = {c: rd(f"logs/run_D2_{c}.log") for c in ("FHCDMIB16e4", "FHCSPDMI", "FHCALDDMI")}
    chk("D4 control runner logs: one header each '# run_fighsdmi16e4 git e5caaccb 2026-10-12 18:44 CDT control resume=0', '4 tasks on 4 workers', 4 'done' lines, no Traceback",
        all(len(re.findall(r"^# run_fighsdmi16e4 git e5caaccb 2026-10-12 18:44 CDT control resume=0$", v, re.M)) == 1 and len(re.findall(r"^# run_", v, re.M)) == 1 and "-> 4 tasks on 4 workers" in v and len(re.findall(r"^\d/4 done ", v, re.M)) == 4 and "Traceback" not in v for v in ctl_log.values()), n=12)

    # ================================================================== E. count tables + §6.2
    print("\n# E. count tables / §6.2")
    bad, badw, nrow, heads = [], [], 0, []
    for t in TAGS:
        tb = {}
        for l in rd(f"{RV}/fighs_{t}.txt").split("\n"):
            if l.startswith("#"): heads.append(l); continue
            m = re.match(r"^SNR ([+-]\d+)  (\S+)\s+(\d+) / (\d+)  BLER (\S+)  95% \[(\S+), (\S+)\]$", l)
            if not m:
                if l.strip(): bad.append((t, "unparsed", l))
                continue
            s, a, k, n = int(m[1]), m[2], int(m[3]), int(m[4]); nrow += 1; tb[s, a] = k
            want = CNT1[t][s] if a == "R0-pilot@1" else CNT[t].get(a, {}).get(s)
            if (k, n) != (want, N2): bad.append((t, s, a, k, n, want))
            if (m[5], m[6], m[7]) != fmt(k, n): badw.append((t, s, a, m.groups()[4:], fmt(k, n)))
        if len(tb) != 4 * (len(ARMS[t]) + ("R0-pilot" in ARMS[t])): bad.append((t, "rows", len(tb)))
    chk(f"E1 count tables fighs_FH*.txt: every (SNR, arm) failures / n == own recount ({nrow} rows = 32 + 16 + 8, incl. R0-pilot@1 = after the first iteration); no other line", not bad and nrow == 56, str(bad[:4]), n=2 * nrow)
    chk(f"E2 count tables: BLER / Wilson strings == own Wilson (z 1.959964, %.2e) for all {nrow} rows", not badw, str(badw[:3]), n=3 * nrow)
    wh = [f"# run_fighsdmi16e4 git {RUNC} raw_{t} C2: failures@16 / n, BLER, 95% Wilson -- REPORT-ONLY (FIGHSDMI16e4 §1); load_raw warnings 0" for t in TAGS]
    chk("E3 count-table headers (3) = expected and = the §6.1 '집계표 머리말' bullets verbatim", heads == wh and [l for l in S6 if l.startswith("- `# run_fighsdmi16e4")] == [f"- `{h}`" for h in wh], n=6)
    bad = []; ncell = 0; rows62 = []
    for l in S6:
        m = re.match(r"^\| (\S+) \| raw_(\w+) \| (.*) \| (\d+) / (\d+) / (\d+) / (\d+) \|$", l)
        if not m or m[1] not in EXP62: continue
        a = m[1]; rows62.append(a); cells = m[3].split(" | ")
        if m[2] != EXP62[a][0]: bad.append((a, "source", m[2]))
        for i, s in enumerate(HS):
            q = re.match(r"^(\d+) \((\S+), \[(\S+), (\S+)\]\)$", cells[i]); ncell += 1; k = newk(a, s)
            if not q or int(q[1]) != k or k != EXP62[a][1][i] or (q[2], q[3], q[4]) != fmt(k, N2): bad.append((a, s, cells[i], k, EXP62[a][1][i], fmt(k, N2)))
        ok_ = [origk(a, s) for s in HS]
        if [int(m[i]) for i in range(4, 8)] != ok_ or ok_ != EXP62[a][2]: bad.append((a, "orig column", m.groups()[3:], ok_))
    chk(f"E4 §6.2 table: 11 rows in legend order; source raw; {ncell} cells k == own recount == retyped, BLER / Wilson strings == own; '원 raw k / 2560' column == own recount of the original raws == retyped",
        not bad and ncell == 44 and rows62 == ORDER, str(bad[:4]), n=44 * 4 + 11 + 44)
    chk("E5 §6.2 genie line 'FHDMIB16e4 [7, 1, 0, 0] · FHSPDMI [7, 1, 0, 0] · FHALDDMI [7, 1, 0, 0] → 동일.' == own (and B6: the arrays are bit-identical)",
        "Perfect CSI (R5-genie) 의 실패 수는 세 raw 에서 같다: FHDMIB16e4 [7, 1, 0, 0] · FHSPDMI [7, 1, 0, 0] · FHALDDMI [7, 1, 0, 0] → 동일." in S6 and all(v == [7, 1, 0, 0] for v in g.values()), n=12)
    zero = [f"{a} {s:+d} dB" for a in ORDER for s in HS if newk(a, s) == 0]
    chk("E6 §6.2 zero-failure sentence (6 points: V1 +12, V1 +15, ALD-pilot +15, b* +15, genie +12, genie +15) == own recount",
        "0 실패 점 (n = 20480): M-ours-dscore-C-V1 +12 dB, M-ours-dscore-C-V1 +15 dB, ALD-pilot +15 dB, M-ours-bstar +15 dB, R5-genie +12 dB, R5-genie +15 dB." in S6
        and zero == ["M-ours-dscore-C-V1 +12 dB", "M-ours-dscore-C-V1 +15 dB", "ALD-pilot +15 dB", "M-ours-bstar +15 dB", "R5-genie +12 dB", "R5-genie +15 dB"], str(zero), n=6)
    def rise(seq):
        return [i for i in range(1, len(seq)) if seq[i][0] * seq[i - 1][1] > seq[i - 1][0] * seq[i][1]]
    mine = {}
    for a in ORDER:
        up = [f"{ALL[i - 1]:+d}->{ALL[i]:+d} dB p={fis(MERGED[a][i], MERGED[a][i - 1]):.2g}" for i in rise(MERGED[a])]
        mine[a] = f"    {a:<20}@16  " + " ".join(f"{k}/{n}" for k, n in MERGED[a][3:]) + f"   (raw_{EXP62[a][0]})" + (f"   rising: {'; '.join(up)}" if up else "")
    rec = rd(f"{REC}/paper_f21dmihs.txt").split("\n")
    blk = [l for l in rec if re.match(r"^    \S+\s+@16  ", l)]
    chk("G1 figure record paper_f21dmihs.txt merge block (11 lines: k/n at +6..+15, source tag, rising cells + one-sided Fisher p %.2g over the 7 merged points) == own, byte for byte",
        blk == [mine[a] for a in ORDER], str([(x, y) for x, y in zip(blk, [mine[a] for a in ORDER]) if x != y][:2]), n=11 * 5)
    ris = [l.strip() for l in blk if "rising:" in l]
    p1, p2 = fis(MERGED["R3-bigamp"][5], MERGED["R3-bigamp"][4]), fis(MERGED["R3-bigamp"][6], MERGED["R3-bigamp"][5])
    chk("E7 §6.2 rising line: '1 줄' and the quoted line == the record's == own: R3-bigamp +9->+12 dB p=7.4e-42; +12->+15 dB p=8.2e-07 (own Fisher: scipy one-sided 'greater'); no other rising cell on any of the 11 merged curves (incl. +3->+6)",
        [l[3:-1] for l in S6 if l.startswith("- `") and "rising:" in l] == ris == [mine[a].strip() for a in ORDER if "rising:" in mine[a]] and len(ris) == 1 and ris[0].endswith("rising: +9->+12 dB p=7.4e-42; +12->+15 dB p=8.2e-07")
        and any("의 '오르는 칸' (SNR 이 오를 때 BLER 이 오르는 칸, 한쪽 Fisher p; 보고만): 1 줄." in l for l in S6) and {a for a in ORDER if rise(MERGED[a])} == {"R3-bigamp"},
        f"own p {p1:.4g}, {p2:.4g}; rising cells {({a: [(ALL[i - 1], ALL[i]) for i in rise(MERGED[a])] for a in ORDER if rise(MERGED[a])})}", n=5)
    ties = {a: [f"{ALL[i - 1]:+d}->{ALL[i]:+d}" for i in range(1, 7) if MERGED[a][i][0] * MERGED[a][i - 1][1] == MERGED[a][i - 1][0] * MERGED[a][i][1]] for a in ORDER}
    print("   ties (equal BLER in adjacent cells; not 'rising'): " + str({a: v for a, v in ties.items() if v}))
    print("   +3 -> +6 dB cells (n 2560 -> n 20480), own BLER: " + "; ".join(f"{a} {MERGED[a][2][0] / N1:.2e}->{MERGED[a][3][0] / N2:.2e}" for a in (V1, BST, GE)))

    # ================================================================== F. §6.3
    print("\n# F. §6.3 predictions, scored by the auditor against the frozen §3 wording")
    V = [newk(V1, s) for s in HS]; Bk = [newk(BST, s) for s in HS]
    p2r = {a: [fis(MERGED[a][i], MERGED[a][i - 1]) for i in rise(MERGED[a])] for a in (V1, BST, GE)}
    LOGALL = rd("logs/run_fighsdmi16e4.log").split("\n"); LOG = [l for l in LOGALL if l.startswith("[fighs ")]
    starts = [l for l in LOG if "] start (git" in l]; done = [l for l in LOG if "FIGHS_DONE" in l]
    own = {"1": V[0] >= V[1] >= V[2] >= V[3], "2": all(p >= 0.05 for v in p2r.values() for p in v), "3": V[0] <= Bk[0] and V[1] <= Bk[1], "4a": V[1] >= 1, "4b": V[3] <= 5,
           "5": len(done) == 1 and done[0].endswith("FIGHS_DONE ok=3 fail=0") and len(starts) == 1 and not any("resume" in l and "resume=0" not in l for l in LOGALL)}
    got = {m[1]: m[2] for l in S6 for m in [re.match(r"^(\d[ab]?)\. .*→ \*\*(적중|빗나감)\*\*", l)] if m}
    chk("F1 §6.3 scores: 1, 2, 3, 4a, 4b, 5 all '적중' == own scoring (1: 21 >= 2 >= 0 >= 0; 2: no rising cell at all on V1 / b* / genie, +3->+6 included; 3: 21 <= 27 and 2 <= 8; 4a: 2 >= 1; 4b: 0 <= 5; 5: one start line, no resume, ok=3 fail=0)",
        got == {k: "적중" for k in own} and all(own.values()), f"V1 {V}, b* {Bk}, rising p {p2r}, record {got}, own {own}", n=6)
    want63 = ["1. V1 의 실패 수가 +6 ≥ +9 ≥ +12 ≥ +15 dB 로 줄기만 한다 → **적중** (21 / 2 / 0 / 0).",
              "2. V1 · b\\* · Perfect CSI 에 Fisher p < 0.05 인 오르는 칸 없음 → **적중** (오르는 칸의 p: M-ours-dscore-C-V1 없음, M-ours-bstar 없음, R5-genie 없음).",
              "3. +6 · +9 dB 에서 실패 수 V1 ≤ b\\* → **적중** (21 대 27, 2 대 8).", "4a. V1 의 +9 dB 실패 수 ≥ 1 / 20480 → **적중** (2).", "4b. V1 의 +15 dB 실패 수 ≤ 5 / 20480 → **적중** (0).",
              "5. `FIGHS_DONE ok=3 fail=0`, 재개 없이 한 번에(시작 줄 1 개) → **적중** (ok=3 fail=0; 시작 줄 1 개)."]
    i63 = S6.index("### 6.3 §3 예측 채점"); i64 = next(i for i, l in enumerate(S6) if l.startswith("### 6.4 "))
    chk("F2 §6.3 text = the six lines retyped by the auditor, with the quoted numbers == own (21 / 2 / 0 / 0; 21 대 27, 2 대 8; 2; 0; ok=3 fail=0; 시작 줄 1 개); nothing else in §6.3",
        [l for l in S6[i63 + 1:i64] if l] == want63 and V == [21, 2, 0, 0] and Bk == [27, 8, 2, 0], str([l for l in S6[i63 + 1:i64] if l and l not in want63]), n=12)
    s3 = "\n".join(reg[next(i for i, l in enumerate(reg) if l.startswith("## 3. ")):next(i for i, l in enumerate(reg) if l.startswith("## 5. "))])
    need = ["실패 수는 +6 ≥ +9 ≥ +12 ≥ +15 dB 로 줄기만 한다. 채점: 실패 수 비교(세 부등식이 모두 성립해야 적중).", "V1 · b\\* · Perfect CSI 의 곡선에 Fisher p < 0.05 인 \"오르는 칸\" 이 없다(+3 → +6 dB 칸 포함; 세 곡선 모두 성립해야 적중).",
            "+6 dB 와 +9 dB 에서 실패 수 V1 ≤ b\\* (점추정; 두 점 모두 성립해야 적중).", "**4a.** V1 의 +9 dB 실패 수 ≥ 1 / 20480 (곡선이 +9 dB 까지 이어진다). **4b.** V1 의 +15 dB 실패 수 ≤ 5 / 20480.",
            "세 행 모두 대조·수용 통과(`FIGHS_DONE ok=3 fail=0`), 재개 없이 한 번에(시작 줄 1 개)."]
    chk("F3 frozen §3 holds exactly the five numbered predictions (4 = 4a + 4b) the §6.3 lines paraphrase, with the scoring clauses; the §3 memo ('예측이 아니다 — 채점하지 않는다') is not scored in §6.3",
        all(x in s3 for x in need) and "**메모(예측이 아니다 — 채점하지 않는다)**" in s3 and len(re.findall(r"^\d\. ", s3, re.M)) == 5 and len(got) == 6, str([x for x in need if x not in s3]), n=6)

    # ================================================================== G. figure records
    print("\n# G. figure records")
    dsrc = rd(f"{FIGD}/paper_f16deep.py"); csrc = rd(f"{FIGD}/paper_f16col.py"); fsrc = rd(f"{FIGD}/paper_f21dmc.py")
    chk("G0 figure code constants (read as text): paper_f16deep BARS = (V1, BS, 'R2-ours-G', GE); paper_f16col YLO, YLO_RULE = 2e-4, 3e-5; paper_f21dmc ROOM rule '(Q.YLO, 1.2) if not zero and min(pos) > Q.YLO else (Q.YLO_RULE, 1.2)'; HSREG has DMI: FIGHSDMI16e4; paper_f21dmc.py + fighs_merge.py unchanged ecaaf967..HEAD",
        'BARS = (V1, BS, "R2-ours-G", GE)' in dsrc and "YLO, YLO_RULE = 2e-4, 3e-5" in csrc and "YLIM, YTICKS = ((Q.YLO, 1.2) if not zero and min(pos) > Q.YLO else (Q.YLO_RULE, 1.2)), None" in fsrc
        and '"DMI": "FIGHSDMI16e4"' in fsrc and not sh(f"git diff ecaaf967 HEAD -- {FIGD}/paper_f21dmc.py {FIGD}/fighs_merge.py {FIGD}/paper_f16deep.py {FIGD}/paper_f16col.py"), n=5)
    def cblock(lines):
        c = {}
        for l in lines[lines.index("Counts:") + 1:]:
            f = l.split()
            if not f: break
            c[f[0]] = ([tuple(int(x) for x in v.split("/")) for v in f[1:8]], f[8])
        return c
    cnt = cblock(rec)
    chk("G2 paper_f21dmihs.txt 'Counts:' block == own merged counts (11 curves x 7 SNR: -3/0/+3 from the original raws n 2560, +6..+15 from the new raws n 20480), in legend order, source column = the original raw",
        list(cnt) == ORDER and all(cnt[a][0] == MERGED[a] and cnt[a][1] == f"raw_{OSRC[a]}" for a in ORDER), n=77 + 11)
    rec0 = rd(f"{REC}/paper_f21dmi.txt").split("\n"); cnt0 = cblock(rec0)
    chk("G3 paper_f21dmi.txt (n = 2560 figure record) 'Counts:' block == own recount of the original raws (11 x 7)", list(cnt0) == ORDER and all(cnt0[a][0] == ORIG7[a] for a in ORDER), n=77)
    zl = [l for l in rec if l.startswith("Zero-failure points")]
    zown = "Zero-failure points (the curve breaks there; Perfect CSI: fighs_merge.zero_arrows): " + "; ".join(f"{LABEL[a]} {s:+d} dB" for a in ORDER for s, (k, n) in zip(ALL, MERGED[a]) if k == 0) + "."
    zq = "Zero-failure points (the curve breaks there; Perfect CSI: fighs_merge.zero_arrows): Proposed (diffusion prior) +12 dB; Proposed (diffusion prior) +15 dB; Annealed Langevin (plug-in) +15 dB; GMM prior +15 dB; Perfect CSI +12 dB; Perfect CSI +15 dB."
    fig_b = next(l for l in S6 if l.startswith("- **그림** "))
    chk("G4 zero-failure line: record == own == the retyped line; §6.4 quotes it verbatim inside backticks ('기록 원문')", zl == [zown] and zown == zq and f"기록 원문: `{zq}`" in fig_b, zl[0] if zl else "none", n=8)
    bel = [(a, s, k, kv) for a in ORDER if a not in (V1, GE) for s, (k, _), (kv, _) in zip(ALL, MERGED[a], MERGED[V1]) if k <= kv]
    bq = ("Drawn baseline curves (Perfect CSI excluded) at or below the proposed curve (point estimates; failures vs the proposed curve's) -- reported only, nothing is tested here; the registered "
          "paired tests are in conf/results/review_next/pairB_SPDMI.txt: Annealed Langevin (plug-in) at +15 dB (0 vs 0); GMM prior at +15 dB (0 vs 0).")
    ab_b = next(l for l in S6 if l.startswith("- **'at or below the proposed curve' 줄**"))
    chk("G5 'at or below the proposed curve' line: own = exactly two baseline points (ALD-pilot +15 dB 0 vs 0, b* +15 dB 0 vs 0); record line == retyped; §6.4 quotes it verbatim ('보강 그림 기록 원문')",
        bel == [("ALD-pilot", 15, 0, 0), (BST, 15, 0, 0)] and bq in rec and f"보강 그림 기록 원문): `{bq}`" in ab_b, str(bel), n=6)
    bel0 = [(a, s, k, kv) for a in ORDER if a not in (V1, GE) for s, (k, _), (kv, _) in zip(ALL, ORIG7[a], ORIG7[V1]) if k <= kv]
    l0 = next(l for l in rec0 if l.startswith("Drawn baseline curves"))
    n0 = len(re.findall(r"dB \(\d+ vs \d+\)", l0))
    zero0 = [(a, s) for a in ORDER for s, (k, _) in zip(ALL, ORIG7[a]) if k == 0]
    chk("G6 n = 2560 record paper_f21dmi.txt: its 'at or below' line lists 12 points == own recount of the original raws (12; only ALD-pilot +6 dB '4 vs 4' is not 0 vs 0) -> §6.4 '같은 줄은 12 점이었다(ROOM16e4 §7.4)'; own zero-failure points of the n = 2560 figure 18 of 77 (머리말)",
        n0 == 12 == len(bel0) and [b for b in bel0 if (b[2], b[3]) != (0, 0)] == [("ALD-pilot", 6, 4, 4)] and len(zero0) == 18 and "같은 줄은 12 점이었다(ROOM16e4 §7.4)." in ab_b
        and l0.split("pairB_SPDMI.txt: ")[1] in rd(f"{RV}/NEXT_EXPERIMENTS_ROOM16e4.md"), f"record {n0}, own {len(bel0)}: {bel0}", n=14)
    zeroany = any(k == 0 for a in ORDER for k, _ in MERGED[a])
    drawn = {(a, s): (wil(k, n)[0] if a in BARS else k / n) for a in ORDER for s, (k, n) in zip(ALL, MERGED[a]) if k > 0}
    ylim = (2e-4, 1.2) if (not zeroany and min(drawn.values()) > 2e-4) else (3e-5, 1.2)
    pts = {(a, s): k / n for a in ORDER for s, (k, n) in zip(ALL, MERGED[a]) if k > 0}
    chk("G7 y range by the ROOM rule on the drawn (merged) values -> (3e-05, 1.2) [zero-failure points exist]; record Layout line 'y log (3e-05, 1.2)'; §6.4 'y 축 (3e-05, 1.2) (기록의 Layout 줄)'; every drawn point estimate inside the range (min 1/20480 = 4.88e-05)",
        ylim == (3e-5, 1.2) and any(l.startswith("Layout:") and "y log (3e-05, 1.2), ticks None" in l for l in rec) and "y 축 (3e-05, 1.2) (기록의 Layout 줄)" in fig_b and 3e-5 <= min(pts.values()) and max(pts.values()) <= 1.2,
        f"min drawn point {min(pts.values()):.3g} at {min(pts, key=pts.get)}", n=4)
    clip = [(LABEL[a], s, f"{wil(k, n)[0]:.2e}") for a in BARS for s, (k, n) in zip(ALL, MERGED[a]) if k > 0 and wil(k, n)[0] < 3e-5]
    chk("G8 §6.4 clipped bars: among the four bar curves exactly four lower Wilson ends lie below 3e-05 -- Proposed +9 dB (2.68e-05), GMM prior +12 dB (2.68e-05), Gaussian prior +15 dB (2.68e-05), Perfect CSI +9 dB (8.62e-06); Wilson upper bound of 0 / 20480 = 1.88e-04",
        clip == [("Proposed (diffusion prior)", 9, "2.68e-05"), ("GMM prior", 12, "2.68e-05"), ("Gaussian prior", 15, "2.68e-05"), ("Perfect CSI", 9, "8.62e-06")] and f"{wil(0, N2)[1]:.2e}" == "1.88e-04"
        and "Proposed +9 dB (2.68e-05), GMM prior +12 dB (2.68e-05), Gaussian prior +15 dB (2.68e-05), Perfect CSI +9 dB (8.62e-06)" in fig_b and "(0 / 20480, Wilson 상한 1.88e-04)" in fig_b, str(clip), n=10)
    print(f"   Perfect CSI zero-failure arrows at +12 / +15 dB (fighs_merge.zero_arrows): cap {1.96 ** 2 / (N2 + 1.96 ** 2):.3e}, tip {1.96 ** 2 / (N2 + 1.96 ** 2) / 1.7:.3e} (inside the axis)")
    print(f"   upper Wilson ends above 1.2: {[(a, s) for a in BARS for s, (k, n) in zip(ALL, MERGED[a]) if k > 0 and wil(k, n)[1] > 1.2]}")
    chk("G9 record wording: 'REPORT-ONLY, NEXT_EXPERIMENTS_FIGHSDMI16e4 §1' merge header; second paragraph names FIGHSDMI16e4 §1; 'Asserts passed: counts before the merge (n = 2560, the registered judgement) = pairB_SPDMI.txt'; labels line 'all (i)'; 'Raised blocks ...: none.'; arm -> figure-name map == LABEL",
        sum("NEXT_EXPERIMENTS_FIGHSDMI16e4 §1" in l for l in rec) == 2 and any(l.startswith("FIGHSDMI16e4 merge (REPORT-ONLY, NEXT_EXPERIMENTS_FIGHSDMI16e4 §1): -3/0/+3 dB = the original test trials 0..2559 (n = 2560, the registered judgement); +6/+9/+12/+15 dB = new trials 10000..30479 (n = 20480 per SNR; one point = one raw, never pooled).") for l in rec)
        and any(l.startswith("Asserts passed: counts before the merge (n = 2560, the registered judgement) = pairB_SPDMI.txt") for l in rec) and "Registered table-B labels against the proposed prior (pairB_SPDMI.txt) of the 9 drawn baselines: all (i)." in rec
        and "Raised blocks (analysis.load_raw NOTE lines; kept and counted as failures) in the raws read: none." in rec and "Curves (internal arm -> figure name): " + "; ".join(f"{a} -> {LABEL[a]}" for a in ORDER) + "." in rec, n=6 + 11)

    # ================================================================== H. logs / timeline / git
    print("\n# H. logs / manifests / timeline / git")
    def ts(l):
        m = re.match(r"\[fighs (\d\d)-(\d\d) (\d\d):(\d\d) CDT\]", l); return datetime(2026, int(m[1]), int(m[2]), int(m[3]), int(m[4]), tzinfo=CDT)
    chk("H1 run log: ONE start line '[fighs 10-12 18:43 CDT] start (git e5caaccb) rows: all resume=0 skip0 10000 n 20480 SNR 6 9 12 15' (first line); no 'resume:' line",
        starts == ["[fighs 10-12 18:43 CDT] start (git e5caaccb) rows: all resume=0 skip0 10000 n 20480 SNR 6 9 12 15"] and LOG[0] == starts[0] and not any("resume:" in l for l in LOGALL), n=3)
    nb_ = [l for l in LOGALL if re.search(r"ABORT|SKIP|INVALID|FAILED|failed|Traceback|Error|rc=[1-9]|not made", l)]
    s61 = ("`bash code/run_fighsdmi16e4.sh` **한 번**, tmux `fighsdmi`, 10-12 18:43 CDT 시작(git e5caaccb = 실행 커밋; 시작 줄 하나, 재개 없음). 단계 C (관측된 시험 청크 0 의 대조) 10-12 18:45 CDT: 3 receiver control(s) OK, 1 ALD estimator control(s) OK. "
           "`FIGHS_DONE ok=3 fail=0` 10-12 21:32 CDT. ABORT · SKIP · INVALID 줄: 0 개.")
    chk("H2 §6.1 first paragraph (retyped) is in §6 and == the log: phase C done 10-12 18:45 CDT '3 receiver control(s) OK, 1 ALD estimator control(s) OK'; last line '[fighs 10-12 21:32 CDT] FIGHS_DONE ok=3 fail=0'; 0 lines with ABORT / SKIP / INVALID / FAILED / failed / Traceback / Error / rc!=0 / 'not made' in the whole log",
        s61 in S6 and "[fighs 10-12 18:45 CDT] phase C done: 3 receiver control(s) OK, 1 ALD estimator control(s) OK" in LOG and LOG[-1] == "[fighs 10-12 21:32 CDT] FIGHS_DONE ok=3 fail=0" and not nb_ and len(done) == 1, str(nb_), n=7)
    RUN = {m[1]: (ts(l), m[2]) for l in LOG for m in [re.match(r"\[fighs [^\]]+\] (FH\w+) run: (.*)$", l)] if m}
    ACC = {m[1]: (ts(l), int(m[2]), m[3]) for l in LOG for m in [re.match(r"\[fighs [^\]]+\] (FH\w+) acceptance rc=(\d+) \((.*)\)$", l)] if m}
    wr = {"FHDMIB16e4": "--testbed D2 --prior DMI --cell C2 --chunk 40 --ntrain 160000 --stagec-ckpt /home/HTJ/t2/conf/ckpt/d2sx_DMI_N160000_a1_best.pt  --snr 6 9 12 15 --n 20480 --skip0 10000 --arm " + " ".join(ARMS["FHDMIB16e4"]),
          "FHSPDMI": "--testbed D2 --prior DMI --cell C2 --chunk 40 --ntrain 160000 --sparse-file results/sparse/pick_DMI_C2.json  --snr 6 9 12 15 --n 20480 --skip0 10000 --arm " + " ".join(ARMS["FHSPDMI"]),
          "FHALDDMI": f"--testbed D2 --prior DMI --cell C2 --chunk 40 --ntrain 160000 --stagec-ckpt /home/HTJ/t2/conf/ckpt/d2sx_DMI_N160000_a1_best.pt --ald-file {ALDF} --snr 6 9 12 15 --n 20480 --skip0 10000 --arm " + " ".join(ARMS["FHALDDMI"])}
    chk("H3 run / acceptance lines: FHDMIB16e4 18:49 / 20:05, FHSPDMI 20:05 / 21:28, FHALDDMI 21:29 / 21:32 (CDT, 10-12), rc 0 x 3, 'ACCEPT: OK -- <tag> ACCEPT (f): OK'; the three 'run:' lines carry exactly the §1 runner flags",
        list(RUN) == list(TAGS) == list(ACC) and [(f"{RUN[t][0]:%m-%d %H:%M}", f"{ACC[t][0]:%m-%d %H:%M}", ACC[t][1], ACC[t][2]) for t in TAGS] ==
        [("10-12 18:49", "10-12 20:05", 0, "ACCEPT: OK -- FHDMIB16e4 ACCEPT (f): OK "), ("10-12 20:05", "10-12 21:28", 0, "ACCEPT: OK -- FHSPDMI ACCEPT (f): OK "), ("10-12 21:29", "10-12 21:32", 0, "ACCEPT: OK -- FHALDDMI ACCEPT (f): OK ")]
        and all(RUN[t][1] == wr[t] for t in TAGS), str([(t, RUN[t][1]) for t in TAGS if RUN[t][1] != wr[t]]), n=15)
    chk("H4 ALD lines (§6.4): estimator control on GPU 0 at 18:43; EARLY regen + estimate '[fighs 10-12 18:45 CDT] FHALDDMI ALD PILDMI: regen (CPU) + estimate (GPU 0) on trials 10000.., rotation none' right after 'phase C done' and before the first run line; '[ald regen] PILDMI hisnr: 4 SNR x 20480 trials (skip 10000)'; phase R '[fighs 10-12 21:29 CDT] FHALDDMI ALD PILDMI: reusing … (prov git e5caaccb)'; only ONE regen/estimate in the log",
        "[fighs 10-12 18:43 CDT] FHALDDMI ALD estimator control: ald.py estimate --tag FHCALDDMI --set test on GPU 0 (copies of the frozen records of PILDMI)" in LOG
        and LOG.index("[fighs 10-12 18:45 CDT] FHALDDMI ALD PILDMI: regen (CPU) + estimate (GPU 0) on trials 10000.., rotation none (tune record results/ald/tune_PILDMI.json)") == LOG.index("[fighs 10-12 18:45 CDT] phase C done: 3 receiver control(s) OK, 1 ALD estimator control(s) OK") + 1
        and f"[fighs 10-12 21:29 CDT] FHALDDMI ALD PILDMI: reusing {ALDF} (prov git e5caaccb)" in LOG and sum("regen (CPU) + estimate" in l for l in LOG) == 1
        and sum(l.startswith("[ald regen] PILDMI hisnr: 4 SNR x 20480 trials (skip 10000) rotation=None doppler=None") for l in LOGALL) == 1 and sum(l.startswith("[ald estimate] PILDMI hisnr -> ") for l in LOGALL) == 1, n=6)
    aldm = cdt(os.stat(ALDF).st_mtime)
    chk("H4b ald_PILDMI_hisnr.npz mtime (18:49 CDT) lies after 'phase C done' (18:45) and not after the first row's run line (18:49) + 1 min, i.e. it was made by the EARLY call and never rewritten in phase R (21:29)",
        ts("[fighs 10-12 18:45 CDT]") <= aldm <= RUN["FHDMIB16e4"][0] + timedelta(minutes=1), f"{aldm:%m-%d %H:%M:%S %Z}", n=1)
    bad = []; rows61 = {}; RMIN = {}
    for l in S6:
        m = re.match(r"^\| (FH\w+) \| (10-12 \d\d:\d\d) \| (\S+) 분 · (\d+) 작업 · (\d+) 워커 \| (\d+) / (\d+) \| (10-12 \d\d:\d\d) \| (.*?) \| (\w+) · (\w+) \| (.*?) \|$", l)
        if m: rows61[m[1]] = m.groups()[1:]
    for t in TAGS:
        rl = rd(f"logs/run_D2_{t}.log"); L = rl.split("\n")
        hd = [l for l in L if l.startswith("# run_")]; mins = re.findall(r"^\[run\] finished in ([\d.]+) min", rl, re.M); tasks = re.findall(r"-> (\d+) tasks on (\d+) workers", rl)
        dn = [m[1] for l in L for m in [re.match(r"^\d+/2048 done\s+(\S+\.npz)", l)] if m]; ne = sum(bool(re.match(r"^\d+/\d+ exists", l)) for l in L)
        af = rd(f"{RV}/{t}_accept.txt"); man = json.load(open(f"{RV}/run_manifest_{t}.json"))
        ctl = rd(f"{RV}/{t.replace('FH', 'FHC', 1)}_control.txt").strip().split("\n")[-1] + (" · " + rd(f"{RV}/FHCALDDMI_aldcontrol.txt").strip().split("\n")[-1] if t == "FHALDDMI" else "")
        RMIN[t] = mins[0] if mins else None
        want = (f"{RUN[t][0]:%m-%d %H:%M}", RMIN[t], "2048", "192", str(len(dn)), str(ne), f"{ACC[t][0]:%m-%d %H:%M}", f"rc={ACC[t][1]}; ACCEPT: OK -- {t}; ACCEPT (f): OK", man["git_commit"], man["config_hash"], ctl)
        if rows61.get(t) != want: bad.append((t, "§6.1 row", rows61.get(t), want))
        if hd != [f"# run_fighsdmi16e4 git {RUNC} 2026-{RUN[t][0]:%m-%d %H:%M} CDT resume=0"] or len(mins) != 1 or tasks != [("2048", "192")] or sorted(dn) != sorted(o["file"] for o in BY[t]) or len(dn) != 2048 or ne or "Traceback" in rl:
            bad.append((t, "runner log", hd, mins, tasks, len(dn), ne))
        if (man["git_commit"], man["config_hash"], man["n_raw_files"], sorted(man["arms"]), man["trial_stream"]["skip_min"], man["trial_stream"]["skip_max_end"], sorted(man["points"].values()), len(man["points"]), man["gmm"]["bstar"]) != \
           (RUNC, "66bd25e9fa596040", 2048, sorted(ARMS[t]), 10000, 30480, [N2] * 4, 4, "gmm1024"): bad.append((t, "manifest"))
        w = datetime.strptime(man["written"], "%Y-%m-%d %H:%M:%S KST").replace(tzinfo=KST)
        if not (RUN[t][0] <= w <= ACC[t][0] + timedelta(minutes=1)): bad.append((t, "manifest written", man["written"]))
        if not (RUN[t][0] <= cdt(MT[t][0]) and cdt(MT[t][1]) <= ACC[t][0] + timedelta(minutes=1)): bad.append((t, "chunk mtimes", cdt(MT[t][0]), cdt(MT[t][1])))
        if af.split("\n")[0] != f"ACCEPT: OK -- {t}" or af.rstrip().split("\n")[-1] != "ACCEPT (f): OK" or f"2048 chunk files, run|git ['{RUNC}']" not in af or "raised trials per arm (= failures, report only) 0\n" not in af: bad.append((t, "accept file"))
        rr = rd(f"{AUD}/rerun_fighsdmi_accept_{t}.txt")
        if rr != f"ACCEPT: OK -- {t}\n": bad.append((t, "auditor's eval_accept re-run", rr))
    chk("H5 §6.1 row table (3 rows x 11 fields: start, runner minutes 75.3 / 82.3 / 2.6, 2048 tasks, 192 workers, done 2048 / exists 0, acceptance time, verdict, manifest git e5caaccb · config_hash 66bd25e9fa596040, control verdicts) == logs + files; runner logs: one header each (resume=0), one 'finished', 2048 'done' lines naming exactly the 2048 chunk files, 0 'exists', no Traceback; manifests (2048 files, arms, trial_stream 10000..30480, 4 points x 20480, bstar gmm1024) written inside run..acceptance; chunk mtimes inside run..acceptance; accept files; the auditor's eval_accept re-runs (rerun_fighsdmi_accept_*.txt) == 'ACCEPT: OK -- <tag>'",
        not bad and len(rows61) == 3 and [RMIN[t] for t in TAGS] == ["75.3", "82.3", "2.6"], str(bad[:3]), n=3 * 11 + 3 * 12)
    print("   chunk mtime windows (CDT): " + " · ".join(f"{t} {cdt(MT[t][0]):%H:%M:%S}–{cdt(MT[t][1]):%H:%M:%S}" for t in TAGS))
    fl = [l for l in S6 if l.startswith("- `(f) raw_")]
    chk("H6 §6.1 '(f)' bullets (3) == the accept files' (f) lines verbatim", fl == [f"- `{x.strip()}`" for t in TAGS for x in rd(f"{RV}/{t}_accept.txt").split("\n") if x.strip().startswith("(f)")] and len(fl) == 3, n=3)
    gl = sh(f"git log --format='%h %cI' {RUNC}^..{S6C}").split("\n")
    trun = datetime.fromisoformat(gl[-1].split()[1]); ts6 = datetime.fromisoformat(gl[0].split()[1])
    rfl = [l for l in sh("git reflog --date=iso-strict -40").split("\n") if "HEAD@{2026-10-13T" in l]
    inwin = [l for l in rfl for m in [re.search(r"HEAD@\{(\S+?)\}", l)] if trun < datetime.fromisoformat(m[1]) < ts6]
    logm = cdt(os.stat("logs/run_fighsdmi16e4.log").st_mtime)
    chk("H7 git: e5caaccb committed 10-12 18:43:50 CDT (same minute as the start line; the first artefact of the run, the tune copy for the ALD control, is later), 42fd4e03 committed 10-12 21:39:25 CDT, after FIGHS_DONE (log mtime 21:32:33); `git log e5caaccb^..42fd4e03` = exactly these two; reflog has no HEAD movement strictly between them; e5caaccb is the last commit touching the registration before 42fd4e03",
        len(gl) == 2 and gl[0].startswith(S6C) and gl[1].startswith(RUNC) and f"{trun.astimezone(CDT):%m-%d %H:%M:%S}" == "10-12 18:43:50" and f"{ts6.astimezone(CDT):%m-%d %H:%M:%S}" == "10-12 21:39:25"
        and trun.timestamp() <= os.stat("results/ald/tune_FHCALDDMI.json").st_mtime and ts6 > logm and not inwin and sh(f"git log --format=%h -2 {S6C} -- {REG}").split("\n") == [S6C, RUNC],
        f"{gl}; first artefact {cdt(os.stat('results/ald/tune_FHCALDDMI.json').st_mtime):%H:%M:%S}; log mtime {logm:%H:%M:%S}; reflog entries inside: {inwin}", n=6)
    T0, T1 = trun.astimezone(CDT), datetime(2026, 10, 12, 21, 32, 59, tzinfo=CDT)
    paths = [f"raw_{t}" for t in TAGS] + [f"raw_{t.replace('FH', 'FHC', 1)}" for t in TAGS] + [ALDF, "results/ald/pilots_PILDMI_hisnr.npz", "results/ald/ald_FHCALDDMI.npz", "results/ald/tune_FHCALDDMI.json", "results/ald/pilots_FHCALDDMI_dev.npz",
             "results/ald/pilots_FHCALDDMI_test.npz", f"{RV}/FHCDMIB16e4_control.txt", f"{RV}/FHCSPDMI_control.txt", f"{RV}/FHCALDDMI_control.txt", f"{RV}/FHCALDDMI_aldcontrol.txt"] + [f"{RV}/{x}" for t in TAGS for x in (f"fighs_{t}.txt", f"{t}_accept.txt", f"run_manifest_{t}.json")]
    def first_m(p):
        return min([os.stat(os.path.join(p, f)).st_mtime for f in os.listdir(p)] + [os.stat(p).st_mtime]) if os.path.isdir(p) else os.stat(p).st_mtime
    def last_m(p):
        return max([os.stat(os.path.join(p, f)).st_mtime for f in os.listdir(p)]) if os.path.isdir(p) else os.stat(p).st_mtime
    pre = [p for p in paths if not (T0 <= cdt(first_m(p)) and cdt(last_m(p)) <= T1)]
    chk("H8 §5 '실행 시작 전 상태: … 없음' and no later rewrite: every run artefact (6 raw dirs with all their files, the hisnr estimate + pilots, the FHC ALD copies, 4 control files, 3 count tables, 3 accept files, 3 manifests) has all mtimes inside [run commit 18:43:50, FIGHS_DONE 21:32] CDT",
        not pre, str(pre), n=len(paths))
    touched = [p for p in sh("git ls-files code ../Demo DECISIONS.md").split("\n") if p and T0 < cdt(os.stat(p).st_mtime) <= T1]
    untr = [p for p in sh("git ls-files --others --exclude-standard code ../Demo").split("\n") if p]
    chk("H9 §6.4 '작업 트리에서 conf/code · Demo · DECISIONS.md · 이 문서를 건드리지 않았다': no tracked file under conf/code / Demo and not DECISIONS.md has an mtime inside the run window; no untracked file under conf/code / Demo now; DECISIONS.md and the registration were last written after FIGHS_DONE (21:39 / 21:37 CDT)",
        not touched and not untr and cdt(os.stat("DECISIONS.md").st_mtime) > T1 and cdt(os.stat(REG).st_mtime) > T1,
        f"touched {touched}; untracked {untr}; DECISIONS mtime {cdt(os.stat('DECISIONS.md').st_mtime):%H:%M:%S}, registration mtime {cdt(os.stat(REG).st_mtime):%H:%M:%S}", n=4)
    figm = {f: cdt(os.stat(f"{FIGD}/{f}").st_mtime) for f in ("F21dmihs_col.pdf", "F21dmihs_col.png", "records/paper_f21dmihs.txt", "F21dmi_col.pdf", "F21dmi_col.png", "records/paper_f21dmi.txt")}
    chk("H10 §6 header '기록 2026-10-12 21:37 CDT' = registration mtime minute; figure F21dmihs_col.{pdf,png} + its record written 21:33 CDT = after FIGHS_DONE and before the §6 record; the registered figure F21dmi_col + its record untouched since before the run commit ('그대로 둔다'), and not part of commit 42fd4e03",
        S6[0].startswith("## 6. 결과 (기록 2026-10-12 21:37 CDT, Opus 5.5") and f"{cdt(os.stat(REG).st_mtime):%m-%d %H:%M}" == "10-12 21:37" and all(logm < figm[f] < cdt(os.stat(REG).st_mtime) for f in list(figm)[:3])
        and all(figm[f] < T0 for f in list(figm)[3:]) and not sh(f"git diff --stat {RUNC} {S6C} -- {FIGD}/F21dmi_col.pdf {FIGD}/F21dmi_col.png {REC}/paper_f21dmi.txt"), " ".join(f"{f} {v:%H:%M:%S}" for f, v in figm.items()), n=8)

    # ================================================================== I. §6.4 remaining statements
    print("\n# I. §6.4")
    head = "\n".join(reg[:i6])
    chk("I1 §6.4 ALD bullet: 'sha256[:16] 01d221fb66ceada3 (git 밖)', '(운영 로그 10-12 18:45 CDT 줄, GPU 0)', '(10-12 21:29 CDT 줄 \"reusing … (prov git e5caaccb)\")' present (facts: A4, H4)",
        any("`results/ald/ald_PILDMI_hisnr.npz` sha256[:16] 01d221fb66ceada3 (git 밖). 단계 C 직후 `# EARLY` 줄이 만들었고(운영 로그 10-12 18:45 CDT 줄, GPU 0), 단계 R 이 그대로 썼다(10-12 21:29 CDT 줄 \"reusing … (prov git e5caaccb)\")." in l for l in S6), n=4)
    chk("I2 §6.4 cost bullet == §1 estimates + runner logs + log times: 'base ≈ 65 분 · SP ≈ 60 분 · ALD ≈ 5 분, 합 ≈ 2.5 시간' vs §1 'FHDMIB16e4 ≈ 65 분 … FHSPDMI ≈ 60 분 … FHALDDMI ≈ 5 분 … 합 ≈ 2.5 시간'; '실측 runner 75.3 · 82.3 · 2.6 분, 전체 10-12 18:43 → 10-12 21:32 CDT (CPU 96 스레드, runner 는 192 워커)'",
        any("§1 의 비용 추정(base ≈ 65 분 · SP ≈ 60 분 · ALD ≈ 5 분, 합 ≈ 2.5 시간) 대비 실측 runner 75.3 · 82.3 · 2.6 분, 전체 10-12 18:43 → 10-12 21:32 CDT (CPU 96 스레드, runner 는 192 워커)." in l for l in S6)
        and all(x in head for x in ("FHDMIB16e4 ≈ 65 분", "FHSPDMI ≈ 60 분", "FHALDDMI ≈ 5 분", "합 ≈ 2.5 시간")), n=9)
    print(f"   (info) §1 estimate arithmetic: 39.0 x 46.6 / 28.3 = {39.0 * 46.6 / 28.3:.1f} min; 41.6 x 14.9 / 10.4 = {41.6 * 14.9 / 10.4:.1f} min; sum of runner minutes {75.3 + 82.3 + 2.6:.1f}; wall 18:43 -> 21:32 = 169 min")
    aud_dmi = rd(f"{AUD}/audit_ROOM16e4_DMI.md"); room = rd(f"{RV}/NEXT_EXPERIMENTS_ROOM16e4.md")
    chk("I3 §6.4 audit bullet: 'MUST 0 · SHOULD 3 · NIT 9; ROOM16e4 §7.8' == §7.8 of ROOM16e4 and the audit report's headings; S1 content (72 iterations, negative training-likelihood step, +0.016 nat in 30 iterations) == the audit report; the 머리말's n = 2560 quotes (V1 4/0/0/0, b* 7/0/0/0, genie 0/0/0/0) == own recount of the original raws ('그대로다')",
        "**MUST 0 · SHOULD 3 · NIT 9 — 반영(수치·라벨 불변; 기록 2026-10-12 19:13 CDT, Opus 5.5)**" in room and "(검증 우도는 30 반복에 +0.016 nat)" in aud_dmi and "EM 72 반복" in aud_dmi
        and [origk(a, s) for a in (V1, BST, GE) for s in HS] == [4, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0] and "V1 +6 / +9 / +12 / +15 dB = 4 / 0 / 0 / 0, b\\* 7 / 0 / 0 / 0, genie 0 / 0 / 0 / 0" in head
        and any("감사(MUST 0 · SHOULD 3 · NIT 9; ROOM16e4 §7.8)는 §7 의 수치·라벨을 고치지 않았다" in l and "(72 반복; 30 반복을 이어 돌리면 ll_val +0.016 nat)" in l for l in S6),
        f"audit headings: SHOULD {len(re.findall(r'^(?:###? ?|\*\*)S-?\d', aud_dmi, re.M))}, NIT {len(re.findall(r'^(?:- )?\*\*N-?\d', aud_dmi, re.M))}", n=8)
    path6 = rd(f"{RV}/NEXT_EXPERIMENTS_FIGHSPATH16e4.md")
    chk("I4 §6.4 quote of FIGHSPATH16e4 §6.4 '`FIGHS_DONE` 뒤에 처음 열었다' exists there; first count table fighs_FHDMIB16e4.txt was written 20:05 CDT (so it could be opened before FIGHS_DONE 21:32)",
        "결과 파일은 `FIGHS_DONE` 뒤에 처음 열었다" in path6 and f"{cdt(os.stat(f'{RV}/fighs_FHDMIB16e4.txt').st_mtime):%H:%M}" == "20:05", n=2)
    conc = {p: cdt(os.stat(p).st_mtime) for p in (f"{AUD}/audit_ROOM16e4_DMI.md", f"{AUD}/gmm_stop_survey.py", f"{AUD}/gmm_stop_survey.out", f"{AUD}/recompute_dmi_emcont.out", f"{AUD}/s6_fighsroom_gen.py", f"{RV}/NEXT_EXPERIMENTS_ROOM16e4.md",
                                             "../docs/EXPERIMENTS.md", "../docs/RESULTS.md", f"{FIGD}/README.md", f"{RV}/WORK_QUEUE.md")}
    print("   (info) mtimes of the concurrent work §6.4 names (CDT): " + "; ".join(f"{os.path.basename(p)} {v:%m-%d %H:%M:%S}" for p, v in conc.items()))
    modified = sorted(l.split("\t")[1] for l in sh(f"git diff --name-status {RUNC} {S6C}").split("\n") if l.startswith("M"))
    print(f"   (info) tracked files MODIFIED (not added) by 42fd4e03: {modified}")
    voc = {w: [i6 + 1 + i for i, l in enumerate(S6) if w in l] for w in ("라벨", "유의", "우수", "입증", "시사", "결론", "일반화", "동치", "판정", "검정", "이긴", "우위", "개선", "낫다", "better", "significant", "outperform")}
    print("   wording: vocabulary hits in §6 (line numbers): " + str({w: v for w, v in voc.items() if v}))
    print("   §6 lines naming M-ours-bstar / b\\* / GMM: " + str([i6 + 1 + i for i, l in enumerate(S6) if re.search(r"M-ours-bstar|b\\\*|GMM", l)]) + "; lines carrying a GMM caveat word (캐비엇): " + str([i6 + 1 + i for i, l in enumerate(S6) if "캐비엇" in l]))

    # ================================================================== J. other documents of 42fd4e03
    print("\n# J. other documents")
    NM = {"V1": V1, "ALD-pilot": "ALD-pilot", "b\\*": BST, "R2": "R2-ours-G", "R1": "R1-turbo", "BiG-AMP": "R3-bigamp", "R0@1": "R0-pilot@1", "SBL-loop": "SBL-loop", "SBL-pilot": "SBL-pilot", "OMP-pilot": "OMP-pilot", "genie": GE}
    own11 = ", ".join(f"{k} " + " / ".join(str(newk(a, s)) for s in HS) for k, a in NM.items())
    zdoc = "0 실패 점 (n 20480): V1 +12 · +15 dB, ALD-pilot +15 dB, b\\* +15 dB, genie +12 · +15 dB (제안 곡선은 +9 dB 에서 끝남)"
    EXP = rd("../docs/EXPERIMENTS.md").split("\n"); erow = [l for l in EXP if "run_fighsdmi16e4.sh" in l]; E = erow[0] if erow else ""
    chk("J1 docs/EXPERIMENTS.md: one row names run_fighsdmi16e4.sh and it is the last non-empty line; the 11 x 4 failure counts == own recount; zero-failure list == own; same number of column separators as the previous row",
        len(erow) == 1 and [l for l in EXP if l.strip()][-1] == E and f"**실패 수 / 20480 (+6 / +9 / +12 / +15 dB)**: {own11}." in E and zdoc in E and E.replace("\\|", "").count("|") == [l for l in EXP if l.strip()][-2].replace("\\|", "").count("|"),
        f"own: {own11}; separators {E.count('|')} vs {[l for l in EXP if l.strip()][-2].count('|')}", n=44 + 6 + 2)
    e3 = ("| 2026-10-13 08:43 ~ 11:32 KST (텍사스 10-12 18:43 ~ 21:32 CDT; 한 번 시작, 재개 없음) |", "`taskset -c 24-47,120-143,72-95,168-191 bash conf/code/run_fighsdmi16e4.sh` (NEXT_EXPERIMENTS_FIGHSDMI16e4 v2 = 실행 커밋 e5caaccb; **보고 전용** — 새 검정·라벨 없음)",
          "`runner.py run --testbed D2 --prior DMI --cell C2 --chunk 40 --ntrain 160000 --snr 6 9 12 15 --n 20480 --skip0 10000`", "(b\\* full 1024)", "ROOM16e4 5-DMI 그대로",
          "| 20260926, **새 시행 10000..30479** (n 20480 / SNR; 테스트 풀 60,700 쌍 복원 추출 — 새 추첨이지 새 채널이 아님), C2 4 SNR, PID 14 | e5caaccb | ALD 대조·추정만 GPU 0; 수신기 CPU (192 워커를 96 스레드에) |",
          "`FIGHS_DONE ok=3 fail=0`; ACCEPT OK ×3.", "오르는 칸 (한쪽 Fisher p; 보고만) 1 줄: BiG-AMP +9→+12 dB p 7.4e-42, +12→+15 dB p 8.2e-07.", "runner 75.3 · 82.3 · 2.6 분. §3 예측: 1 적중, 2 적중, 3 적중, 4a 적중, 4b 적중, 5 적중 |",
          "판정·라벨은 원 raw (n 2560) 그대로이고 다시 판정하지 않는다.", "(y (3e-05, 1.2))", "Fable 사전 검토 MUST 1 · SHOULD 5 · NIT 8 반영", "**사용자의 별도 지시 없음 — 세션의 해석**", "첫 행의 집계표는 `FIGHS_DONE` 전에 열어 봤다 (§6.4).")
    rv = rd(f"{RV}/prereg_reviews_2026-10-11/review_FIGHSDMI16e4.md")
    chk("J2 EXPERIMENTS row: KST / CDT times (start line 18:43, FIGHS_DONE 21:32; KST = CDT + 14 h), command, run commit, flags, b* full 1024, seed / trials / pool 60,700 (머리말) / PID 14, commit column, GPU 0, FIGHS_DONE, rising cell + both p, runner minutes, six scores, 'not re-judged', y range, review counts MUST 1 · SHOULD 5 · NIT 8 (= review file headings), 'no separate user instruction', 'first count table opened before FIGHS_DONE'",
        all(x in E for x in e3) and (len(re.findall(r"^### M-\d", rv, re.M)), len(re.findall(r"^### S-\d", rv, re.M))) == (1, 5) and "MUST 1 · SHOULD 5 · NIT 8" in rv and "테스트 풀(60,700 쌍)" in head
        and f"{(ts(starts[0]).astimezone(KST)):%Y-%m-%d %H:%M}" == "2026-10-13 08:43" and f"{(ts(done[0]).astimezone(KST)):%H:%M}" == "11:32", str([x for x in e3 if x not in E]), n=len(e3) + 6)
    RESL = rd("../docs/RESULTS.md").split("\n"); rb = [l for l in RESL if l.startswith("- **그림 보강 (보고 전용; 새 검정·라벨 없음; 추가 2026-10-12 21:39 CDT, Opus 5.5)**")]
    R = rb[0] if rb else ""
    chk("J3 docs/RESULTS.md §25.6 bullet '그림 보강 (보고 전용 …)': cites the EXPERIMENTS row by its KST head `2026-10-13 08:43 ~ 11:32 KST` (exists) and FIGHSDMI16e4 §6; '새 시행 10000..30479, n 20480 / SNR, `FIGHS_DONE ok=3 fail=0`'; the 11 x 4 counts == own recount == the EXPERIMENTS row's string; zero-failure list; figure + record names; 'no separate user instruction'; inside §25.6",
        len(rb) == 1 and "EXPERIMENTS.md 행 `2026-10-13 08:43 ~ 11:32 KST`, 결과 절 `NEXT_EXPERIMENTS_FIGHSDMI16e4.md` §6: 새 시행 10000..30479, n 20480 / SNR, `FIGHS_DONE ok=3 fail=0`." in R and f"실패 수 / 20480 (+6 / +9 / +12 / +15 dB): {own11}." in R and zdoc + "." in R
        and "그림 `F21dmihs_col`, 기록 `records/paper_f21dmihs.txt`. 사용자의 별도 지시 없이 시작한 보강이다 (세션의 해석)." in R and E.startswith("| 2026-10-13 08:43 ~ 11:32 KST")
        and max(i for i, l in enumerate(RESL) if l.startswith("### 25.")) == next(i for i, l in enumerate(RESL) if l.startswith("### 25.6 ")) < RESL.index(R), n=44 + 10)
    r2560 = [l for l in RESL if l.startswith("- 고SNR (n 2560): V1 +6 / +9 / +12 / +15 dB = 4 / 0 / 0 / 0 건")]
    chk("J3b RESULTS §25.6 neighbouring line (edited in 42fd4e03): '고SNR (n 2560): V1 … = 4 / 0 / 0 / 0 건 … +9 dB 부터 0 실패로 끊긴다. 새 시행 n = 20480 보강은 바로 아래 줄.' and the bullet is the next line",
        len(r2560) == 1 and r2560[0].endswith("새 시행 n = 20480 보강은 바로 아래 줄.") and RESL.index(R) == RESL.index(r2560[0]) + 1, n=3)
    RM = rd(f"{FIGD}/README.md").split("\n")
    r1 = [l for l in RM if l.startswith("| F21dmihs_col |")]; r2 = [l for l in RM if l.startswith("| 실패 수 +6 / +9 / +12 / +15 dB (새 시행 n = 20480; 보고 전용): Proposed · GMM · Perfect CSI |")]
    r0 = [l for l in RM if l.startswith("| F21dmi_col |")]
    chk("J4 conference/figures/README.md: row F21dmihs_col ('−3/0/+3 dB n = 2560 …, +6…+15 dB 는 새 시행 n = 20480 (보고 전용; … §6), y 3×10⁻⁵–1.2 | … (+6 / +9 dB 21 / 2 건) +12 · +15 dB 는 0 / 20480 … 0 실패 점 여섯: Proposed +12 · +15 dB, Annealed Langevin +15 dB, GMM prior +15 dB, Perfect CSI +12 · +15 dB (Perfect CSI 만 화살표). 판정·라벨은 n = 2560 그대로') and the numeric row '21 / 2 / 0 / 0 · 27 / 8 / 2 / 0 · 7 / 1 / 0 / 0 (FIGHSDMI16e4 §6.2)' == own; row F21dmi_col still says '0 실패 점 18 개' and points to the row below",
        len(r1) == 1 and "같은 풀. −3/0/+3 dB n = 2560 (등록된 판정의 시행), **+6…+15 dB 는 새 시행 n = 20480** (보고 전용; `NEXT_EXPERIMENTS_FIGHSDMI16e4.md` §6), y 3×10⁻⁵–1.2 |" in r1[0]
        and "제안 곡선은 +9 dB 까지 이어지고 (+6 / +9 dB 21 / 2 건) +12 · +15 dB 는 0 / 20480 이라 끊긴다. 0 실패 점 여섯: Proposed +12 · +15 dB, Annealed Langevin +15 dB, GMM prior +15 dB, Perfect CSI +12 · +15 dB (Perfect CSI 만 화살표). 판정·라벨은 n = 2560 그대로 |" in r1[0]
        and len(r2) == 1 and r2[0].endswith("| " + " · ".join(" / ".join(str(newk(a, s)) for s in HS) for a in (V1, BST, GE)) + " (FIGHSDMI16e4 §6.2) |") and len(r0) == 1 and "(0 실패 점 18 개) — 보강 그림은 아래 행 |" in r0[0] and RM.index(r1[0]) == RM.index(r0[0]) + 1
        and len(zero) == 6, n=12 + 12 + 3)
    DEC = [l for l in rd("DECISIONS.md").split("\n") if l.strip()]
    d1, d2 = DEC[-2], DEC[-1]
    dq = ("`[2026-10-13 11:39 KST] FIGHSDMI16e4 종료 · §6 전사 (Opus 5.5; 텍사스 10-12 21:39 CDT) | run_fighsdmi16e4.sh (실행 커밋 e5caaccb, CPU 96 스레드) 10-12 18:43 ~ 21:32 CDT, FIGHS_DONE ok=3 fail=0 (한 번 시작, 재개 없음); ACCEPT OK ×3. 실패 수 / 20480 (+6/+9/+12/+15 dB): "
          + own11 + ". " + zdoc + ". 그림 F21dmihs_col; §3 예측 6 개 적중. 보고 전용 — 판정·라벨은 원 raw (n 2560) 그대로. 첫 행의 집계표를 FIGHS_DONE 전에 열어 사용자에게 보고했다 (§6.4 공개).")
    chk("J5 conf/DECISIONS.md last line (FIGHSDMI16e4 종료 · §6 전사): stamp 11:39 KST = 21:39 CDT (= DECISIONS.md mtime minute; KST − 14 h), run commit, times, ok=3 fail=0, 11 x 4 counts == own, zero-failure list, six predictions, report-only, the §6.4 disclosure; both new lines were added by 42fd4e03 (numstat +4 -0)",
        d2.startswith(dq) and f"{cdt(os.stat('DECISIONS.md').st_mtime):%m-%d %H:%M}" == "10-12 21:39" and sh(f"git diff --numstat {RUNC} {S6C} -- DECISIONS.md").split()[:2] == ["4", "0"], d2[:len(dq)] if not d2.startswith(dq) else "", n=44 + 12)
    sv = [l for l in rd(f"{AUD}/gmm_stop_survey.out").split("\n")[1:] if l.strip()]
    neg = [l.split()[0] for l in sv if l.rstrip().endswith("NEGATIVE last step")]; nonneg = [l.split()[0] for l in sv if l.rstrip().endswith("non-negative last step")]
    dmi_l = next(l for l in sv if l.startswith("gmm_fits_D2_DMIB16e4 "))
    d613 = [l for l in DEC if l.startswith("`[2026-10-13 06:13 KST] ROOM16e4")]
    f512 = float(np.load("results/gmm_fits_D2_DMIB16e4/fit_DMI_Nr8_fullK512_n160000.npz", allow_pickle=True)["ll_val"]); f1024 = np.load("results/gmm_fits_D2_DMIB16e4/fit_DMI_Nr8_fullK1024_n160000.npz", allow_pickle=True)
    ll = np.asarray(f1024["ll"], float).ravel()
    chk("J6 conf/DECISIONS.md second-to-last line (ROOM16e4 — DMI §7 audit + correction): 'MUST 0 · SHOULD 3 · NIT 9; 1,219 값 재계산 불일치 0; 여섯 청크 재생' == audit_ROOM16e4_DMI.md; the 06:13 KST line it corrects exists and says '(정상 수렴; …'; '72 반복', '음수 스텝 (-1.545e-03 nat)', 'it_best 70' == the b* fit file (own read: len(ll) 72, ll[-1] − ll[-2], it_best); '+0.016 nat'; survey '57 개 가운데 34 개 … 23 개' == gmm_stop_survey.out (headline B16e4k / SRB / SRT / SV non-negative)",
        d1.startswith("`[2026-10-13 11:39 KST] ROOM16e4 — DMI §7 기록 감사 반영 + 정정 (Opus 5.5; 텍사스 10-12 21:39 CDT) | Fable 서브에이전트 감사 (prereg_audit_2026-10-11/audit_ROOM16e4_DMI.md): MUST 0 · SHOULD 3 · NIT 9; 1,219 값 재계산 불일치 0; 여섯 청크 재생 비트 동일")
        and "합계 **1,219 값 자동 대조, 최종 불일치 줄 0**" in aud_dmi and "여섯 청크 모두 `run|git` 한 키만 빼고 비트 동일" in aud_dmi and len(d613) == 1 and "최종 b* = full 1024, ll_val 112.04253042212595 (정상 수렴;" in d613[0]
        and "EM 은 72 반복에서 학습 우도의 음수 스텝 (-1.545e-03 nat) 으로 멈췄다" in d1 and len(ll) == 72 and f"{ll[-1] - ll[-2]:.3e}" == "-1.545e-03" and int(f1024["it_best"]) == 70 and "선택은 it_best 70 의 검증 최고 상태" in d1
        and "30 반복을 이어 돌린 감사 진단에서 ll_val +0.016 nat" in d1 and "fits 폴더 57 개 가운데 34 개의 선택 적합이 음수 마지막 스텝으로 끝났고 23 개는 아니다 (헤드라인 D2 B16e4k · SRB · SRT · SV 는 아님)" in d1
        and (len(sv), len(neg), len(nonneg)) == (57, 34, 23) and {"gmm_fits_D2_B16e4k", "gmm_fits_D2_SRBB16e4", "gmm_fits_D2_SRTB16e4", "gmm_fits_D2_SVB16e4"} <= set(nonneg) and "WORK_QUEUE 사용자 결정 대기 7" in d1,
        f"survey rows {len(sv)} neg {len(neg)} nonneg {len(nonneg)}; DMI line: {dmi_l.strip()}; fit: len(ll) {len(ll)}, last step {ll[-1] - ll[-2]:.3e}, it_best {int(f1024['it_best'])}", n=16)
    WQ = rd(f"{RV}/WORK_QUEUE.md").split("\n")
    wq_done = WQ.index("## 완료 (최근)"); wq_pend = WQ.index("## 사용자 결정 대기")
    w1 = ("- **FIGHSDMI16e4** (2026-10-12 21:39 CDT 기록): 실행 커밋 e5caaccb → 10-12 18:43–21:32 CDT `FIGHS_DONE ok=3 fail=0` (CPU 96 스레드, 재개 없음) → §6: 실패 수 / 20480 (+6/+9/+12/+15 dB) V1 21 / 2 / 0 / 0, b\\* 27 / 8 / 2 / 0, genie 7 / 1 / 0 / 0; "
          "그림 `F21dmihs_col` (V1 은 +9 dB 에서 끝남); 예측 6 개 적중; 사용자의 별도 지시 없이 시작 (세션의 해석 — §5 · §6.4). 기록 감사 (Fable) 는 §6.5 에.")
    chk("J7 WORK_QUEUE.md: header line '갱신 2026-10-12 21:39 CDT … (FIGHSDMI16e4, n = 20480; 10-12 18:43–21:32 CDT `FIGHS_DONE ok=3 fail=0`) …'; the FIGHSDMI16e4 entry is the first line under '## 완료 (최근)' with times, commit, V1 / b* / genie counts == own; it is no longer in the in-progress table",
        WQ[2].startswith("갱신 2026-10-12 21:39 CDT (Opus 5.5). **지금: DeepMIMO 실내 풀 (prior DMI) — 주 실행·baseline·기록 감사 (MUST 0)·그림 보강 (FIGHSDMI16e4, n = 20480; 10-12 18:43–21:32 CDT `FIGHS_DONE ok=3 fail=0`) 까지 끝, §6 전사·그림 `F21dmihs_col` 커밋.")
        and WQ[wq_done + 1] == w1 and [newk(a, s) for a in (V1, BST, GE) for s in HS] == [21, 2, 0, 0, 27, 8, 2, 0, 7, 1, 0, 0] and not any(l.startswith("| **FIGHSDMI16e4**") or l.startswith("| **ROOM16e4 — DMI**") for l in WQ), n=20)
    w2 = WQ[wq_done + 2]
    w2q = ("5-DMI = 실행 커밋 4131a3b0 → 주 실행 10-12 16:15–17:54 CDT (ACCEPT OK) 표 B `b* → V1` **(i)** 263:179 (2/3 점), SNR@0.1 격차 +0.23 dB, b\\* = full 1024 (붕괴 없음; EM 은 음수 스텝에서 멈춤 — §7.8); baseline @29cf411d 17:56–18:15 CDT 16 개 전부 (i)",
           "§7 전사 cde35a4e; Fable 기록 감사 MUST 0 · SHOULD 3 · NIT 9 (1,219 값 불일치 0, 여섯 청크 재생 비트 동일) 반영 §7.8; RESULTS §25.6 · figures/README.")
    chk("J8 WORK_QUEUE.md 'ROOM16e4 — DMI' entry under 완료: numbers identical to the entry it replaces in the in-progress table of e5caaccb (4131a3b0, 16:15–17:54, 263:179, 2/3, +0.23 dB, 29cf411d 17:56–18:15, 16 baselines) + cde35a4e (the §7 commit) + the audit summary (= ROOM16e4 §7.8)",
        w2.startswith("- **ROOM16e4 — DMI** (2026-10-12 21:39 CDT 기록): ") and all(x in w2 for x in w2q) and "주 실행 10-12 16:15–17:54 CDT (ACCEPT OK) 표 B `b* → V1` **(i)** 263:179 (2/3 점), SNR@0.1 격차 +0.23 dB" in sh(f"git show {RUNC}:conf/{RV}/WORK_QUEUE.md")
        and sh("git log -1 --format=%s cde35a4e").startswith("conf: ROOM16e4 §7 결과 전사"), n=12)
    p7 = next(l for l in WQ[wq_pend:] if l.startswith("7. ")); p8 = next(l for l in WQ[wq_pend:] if l.startswith("8. "))
    emsrc = rd("code/gmm_em_gpu.py"); emstop = re.findall(r"^.*it >= (\d+) and .*tol.*$", emsrc, re.M)
    chk("J9 WORK_QUEUE pending item 7 (GMM EM stop): '57 개 가운데 34 개' == survey; list 'DMI · DeepMIMO 도시 · D3 · UMi28 · MIX3 · NR16' all NEGATIVE and 'B16e4k · SRB · SRT · SV' all non-negative in the survey; '+0.016 nat (격자 한 칸 +6.192 nat 의 0.3 %)': own ll_val(full 1024) − ll_val(full 512) = +6.192, 0.016 / 6.192 = 0.26 %; '20 반복 뒤' == the stop line of code/gmm_em_gpu.py",
        "fits 폴더 57 개 가운데 34 개의 선택 적합이 그렇게 끝났다 (DMI · DeepMIMO 도시 · D3 · UMi28 · MIX3 · NR16 등; 헤드라인 D2 B16e4k · SRB · SRT · SV 는 아님" in p7
        and {"gmm_fits_D2_DMIB16e4", "gmm_fits_D2_DMCB16e4", "gmm_fits_D2_D3B16e4", "gmm_fits_D2_U28B16e4", "gmm_fits_D2_MXB16e4", "gmm_fits_D2_NR16B16e4"} <= set(neg)
        and "30 반복 연장 시 ll_val +0.016 nat (격자 한 칸 +6.192 nat 의 0.3 %)" in p7 and f"{float(f1024['ll_val']) - f512:+.3f}" == "+6.192" and f"{100 * 0.016 / (float(f1024['ll_val']) - f512):.1f}" == "0.3"
        and "20 반복 뒤 학습 우도가 처음 줄어든 스텝에서도 멈춘다" in p7 and bool(emstop) and "20" in emstop,
        f"ll_val 1024 − 512 = {float(f1024['ll_val']) - f512:+.4f}; ratio {100 * 0.016 / (float(f1024['ll_val']) - f512):.2f} %; stop line(s): {[l.strip()[:120] for l in re.findall(r'^.*it >= 20 and .*$', emsrc, re.M)]}", n=10)
    chk("J10 WORK_QUEUE pending item 8: 'n = 20480 에서 V1 · Perfect CSI 는 +12 dB 부터, b\\* · ALD 는 +15 dB 에서 0 실패' == own recount (V1 and genie: 0 at +12 and +15, > 0 at +9; b* and ALD-pilot: 0 at +15, > 0 at +12); says a further run 'must be registered separately' (FIGHSX16e4 frame; FIGHSDMI16e4 §3 memo) and 'decision pending'; the user quote is the same string as in DECISIONS",
        "n = 20480 에서 V1 · Perfect CSI 는 +12 dB 부터, b\\* · ALD 는 +15 dB 에서 0 실패." in p8 and all(newk(a, 12) == 0 == newk(a, 15) and newk(a, 9) > 0 for a in (V1, GE)) and all(newk(a, 15) == 0 and newk(a, 12) > 0 for a in (BST, "ALD-pilot"))
        and "추가 시행은 따로 등록해야 하는 실행 (FIGHSX16e4 의 틀; FIGHSDMI16e4 §3 메모)" in p8 and "결정 대기" in p8 and '"좀 더 시행을 늘려서 15dB까지 다 그리면 좋긴 하겠는데"' in p8 and '"좀 더 시행을 늘려서 15dB까지 다 그리면 좋긴 하겠는데"' in d2, n=8)
    for nm, txt in (("EXPERIMENTS row", E), ("RESULTS bullet", R), ("README F21dmihs row", r1[0] if r1 else ""), ("README numeric row", r2[0] if r2 else ""), ("DECISIONS last line", d2), ("WORK_QUEUE done entry", WQ[wq_done + 1]), ("WORK_QUEUE item 8", p8)):
        print(f"   wording [{nm}]: " + str({w: txt.count(w) for w in ("유의", "우수", "입증", "시사", "결론", "이긴", "우위", "개선", "낫다", "검정", "판정", "라벨", "보고 전용") if w in txt}))

    pool.close()
    print(f"\n# SUMMARY: {sum(ok for _, ok in RES)} PASS / {sum(not ok for _, ok in RES)} FAIL of {len(RES)} check groups; ≈ {NVAL[0]} scalar / string values, {NARR[0]} array comparisons  ({datetime.now(CDT):%Y-%m-%d %H:%M:%S %Z})")
    for n, ok in RES:
        if not ok: print("   FAIL:", n[:160])


if __name__ == "__main__":
    main()
