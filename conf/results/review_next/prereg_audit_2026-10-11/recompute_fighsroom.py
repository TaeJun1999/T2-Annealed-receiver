#!/usr/bin/env python
"""recompute_fighsroom.py -- independent RECORD AUDIT of NEXT_EXPERIMENTS_FIGHSROOM16e4.md §6 (Fable 5.1 subagent, read-only).
Run from /home/HTJ/t2/conf:
  CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=3 MKL_NUM_THREADS=3 ~/miniforge3/envs/torch/bin/python -B \
      results/review_next/prereg_audit_2026-10-11/recompute_fighsroom.py > results/review_next/prereg_audit_2026-10-11/recompute_fighsroom.out
Everything is re-derived from primary sources with numpy only (no analysis.load_raw, no s6_fighsroom_gen.py, no hisnr_report;
the count tables / figure records / registration are compared AGAINST, never read as input).  Single process, writes only stdout.
Sections: A rows / registration  B new raws (3 x 2048)  C original raws (3 x 448)  D controls  E count tables + §6.2  F §6.3 predictions
G figure records (merge, rising, y rule)  H run log / runner logs / manifests / mtimes / git  I §6.4, EXPERIMENTS row, DECISIONS.
"""
import glob, hashlib, json, os, re, subprocess, sys
from datetime import datetime
from zoneinfo import ZoneInfo

import numpy as np
from scipy.stats import fisher_exact

os.chdir("/home/HTJ/t2/conf")
RV = "results/review_next"; REG = f"{RV}/NEXT_EXPERIMENTS_FIGHSROOM16e4.md"; REC = "../conference/figures/records"
CDT, KST = ZoneInfo("America/Chicago"), ZoneInfo("Asia/Seoul")
SN = (6.0, 9.0, 12.0, 15.0); ALL = (-3.0, 0.0, 3.0) + SN; N2 = 20480; N1 = 2560
KEYS_RAW = ("blk_err", "ber", "nmse", "tauL_gmean", "alphaD", "tauL_clip_frac", "alphaD_clip")   # common.KEYS_RAW (copied)
REPLAY_KEYS = ("blk_err", "ber", "tauL_gmean", "alphaD")
PAT = re.compile(r"^D2_(C\d)_([A-Za-z0-9]+?)_Nr(\d+)_T(\d+)_Tp(\d+)_(dft|eig)_snr(-?\d+)_skip(\d+)_n(\d+)\.npz$")
ORDER = ["M-ours-dscore-C-V1", "ALD-pilot", "M-ours-bstar", "R2-ours-G", "R1-turbo", "R3-bigamp", "R0-pilot@1", "SBL-loop", "SBL-pilot",
         "OMP-pilot", "R5-genie"]
SRC = {a: ("FHSRBB16e4", "SRBB16e4") for a in ORDER}
SRC.update({"ALD-pilot": ("FHALDSRB", "ALDSRB"), "SBL-loop": ("FHSPSRB", "SPSRB"), "SBL-pilot": ("FHSPSRB", "SPSRB"), "OMP-pilot": ("FHSPSRB", "SPSRB")})
BARS = ("M-ours-dscore-C-V1", "M-ours-bstar", "R2-ours-G", "R5-genie")

CHECKS = []
def chk(name, ok, detail=""):
    CHECKS.append((name, bool(ok)))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" -- {detail}" if detail else ""))
    return bool(ok)
def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
def wilson(k, n, z=1.959963984540054):
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h
def fisher_p(hi, lo):      # hi = (k, n) at the higher SNR, lo at the lower; one-sided 'greater' as fighs_merge.merge
    return fisher_exact([[hi[0], hi[1] - hi[0]], [lo[0], lo[1] - lo[0]]], alternative="greater").pvalue
def rising(seq):           # indices i with BLER(i) > BLER(i-1), exact in integers
    return [i for i in range(1, len(seq)) if seq[i][0] * seq[i - 1][1] > seq[i - 1][0] * seq[i][1]]
def cdt(ts): return datetime.fromtimestamp(ts, CDT)
def sh(c): return subprocess.run(c, shell=True, capture_output=True, text=True).stdout.strip()
def arm_name(a): return "R0-pilot@1" if a == "R0-pilot@1" else a

print(f"# recompute_fighsroom.py  started {datetime.now(CDT):%Y-%m-%d %H:%M:%S %Z} (= {datetime.now(KST):%H:%M KST})  HEAD {sh('git rev-parse --short HEAD')}")

# ====================================================================== A. rows / registration
F = "TAG CELL PR BF CK SHA ROLE BS KK LL REF ORIG PICK FL ARMS".split()
rows_txt = re.search(r"^ROWS='(.*?)'$", open("code/run_fighsroom16e4.sh").read(), re.S | re.M)[1].split("\n")
ROWS = [dict(zip(F, l.split("|"))) for l in rows_txt]; TAGS = [r["TAG"] for r in ROWS]
chk("A1 ROWS: 3 rows FHSRBB16e4 / FHSPSRB / FHALDSRB, 15 fields", TAGS == ["FHSRBB16e4", "FHSPSRB", "FHALDSRB"] and all(len(l.split("|")) == 15 for l in rows_txt))
reg = open(REG, encoding="utf-8").read().split("\n")
i6 = next(i for i, l in enumerate(reg) if l.startswith("## 6. "))
S6 = reg[i6:]
chk("A2 registration: the diff 193776a1..ed265304 touches only the '## 6.' block (first changed line = the §6 header; nothing before it)",
    (lambda d: d and all(re.match(r"^@@ -(\d+)", h) and int(re.match(r"^@@ -(\d+)", h)[1]) >= i6 - 2 for h in re.findall(r"^@@.*$", d, re.M)))(sh(f"git diff 193776a1 ed265304 -- {REG}")),
    sh(f"git diff 193776a1 ed265304 -- {REG} | grep '^@@'"))
chk("A3 lines 1..§6 header of the working-tree registration == committed 193776a1 (frozen §1/§3/§5)",
    sh(f"git show 193776a1:./{REG}").split("\n")[:i6] == reg[:i6])
chk("A4 on disk: ckpt sha ed437f21af15c305, pick sha 4c6da315c701b9d4, ALD test estimate a3d249188f9c061a, test pilots 97a2d08640fef383, tune e0adb06cce792093",
    sha("ckpt/d2sx_SRB_N160000_a1_best.pt")[:16] == "ed437f21af15c305" and sha("results/sparse/pick_SRB_C2.json")[:16] == "4c6da315c701b9d4" and
    sha("results/ald/ald_PILSRB.npz")[:16] == "a3d249188f9c061a" and sha("results/ald/pilots_PILSRB_test.npz")[:16] == "97a2d08640fef383" and
    sha("results/ald/tune_PILSRB.json")[:16] == "e0adb06cce792093")
ALD_HS_SHA = sha("results/ald/ald_PILSRB_hisnr.npz")[:16]
chk("A5 new-trial ALD estimate ald_PILSRB_hisnr.npz sha256[:16] = a7b2c943b3968846 (§6.4), prov git 193776a1, skip 10000, hhat (4, 20480, 32), snrs 6/9/12/15",
    (lambda z: ALD_HS_SHA == "a7b2c943b3968846" and json.loads(str(z["prov"]))["git"] == "193776a1" and int(z["skip"]) == 10000 and z["hhat"].shape == (4, N2, 32)
     and z["snrs"].tolist() == list(SN) and json.loads(str(z["tune"]))["c"] == 0.01 and json.loads(str(z["tune"]))["beta"] == 0.005)(np.load("results/ald/ald_PILSRB_hisnr.npz")),
    ALD_HS_SHA)

# ====================================================================== B. new raws
PICK = json.load(open("results/sparse/pick_SRB_C2.json"))
def scan(path, want_meta=True):
    b = os.path.basename(path); m = PAT.match(b)
    o = {"file": b, "mtime": os.stat(path).st_mtime, "name": (m[1], m[2], float(m[7]), int(m[8]), int(m[9])) if m else None, "arms": {}, "meta": {}, "err": None, "keys": None}
    try:
        with np.load(path) as z:
            fs = set(z.files); o["keys"] = fs
            o["git"] = str(z["run|git"]) if "run|git" in fs else None
            o["run"] = (float(z["run|snr"]), int(z["run|skip"]), int(z["run|n"]), int(z["run|iters"]), int(z["run|seed"]))
            for k in ("ntrain", "bstar", "ll_val|gmm1024", "stagec_ckpt_id", "sparse", "rotation", "ald_file", "kron_K"):
                if f"meta|{k}" in fs:
                    v = z[f"meta|{k}"]; o["meta"][k] = str(v.item() if v.ndim == 0 else v)
            arms = sorted({k.split("|")[0] for k in fs if "|" in k and not k.startswith(("meta|", "run|"))})
            for a in arms:
                if f"{a}|blk_err" not in fs: continue
                be = np.asarray(z[f"{a}|blk_err"], float); last, first = be[:, -1], be[:, 0]; nf = ~np.isfinite(last)
                o["arms"][a] = (int(np.where(nf, 1.0, last).sum()), int(np.where(np.isfinite(first), first, 1.0).sum()), be.shape, int(nf.sum()),
                                int(z[f"{a}|failed"].sum()) if f"{a}|failed" in fs else 0, f"{a}|failed" in fs)
    except Exception as e:
        o["err"] = repr(e)
    return o
print("\n# B. scanning the 3 new raws (single process) ...")
BY = {t: [scan(p) for p in sorted(glob.glob(f"raw_{t}/D2_*.npz"))] for t in TAGS}
chk("B0 every new chunk readable", not [o for t in TAGS for o in BY[t] if o["err"]])
PLAN = {(s, 10000 + 40 * k, 40) for s in SN for k in range(512)}
COUNTS, COUNTS1, MT = {}, {}, {}
bad_plan, bad_git, bad_meta, bad_shape, bad_raised = [], [], [], [], []
for r in ROWS:
    t = r["TAG"]; L = BY[t]
    plan = [(o["name"][2], o["name"][3], o["name"][4]) for o in L]
    if len(L) != 2048 or set(plan) != PLAN or len(set(plan)) != 2048 or any(o["run"][:3] != p for o, p in zip(L, plan)): bad_plan.append(t)
    if {o["name"][0] for o in L} != {"C2"} or {o["name"][1] for o in L} != {"SRB"}: bad_plan.append((t, "cell/prior"))
    if {o["git"] for o in L} != {"193776a1"} or {o["run"][3] for o in L} != {16} or {o["run"][4] for o in L} != {20260926}: bad_git.append((t, {o["git"] for o in L}))
    for o in L:
        mt = o["meta"]
        if mt.get("ntrain") != "160000.0" or mt.get("bstar") != "gmm1024" or mt.get("ll_val|gmm1024") != "97.00871495382869": bad_meta.append((t, o["file"], "ntrain/bstar/ll", mt)); break
        cid = mt.get("stagec_ckpt_id")
        if r["CK"] == "-":
            if cid is not None: bad_meta.append((t, o["file"], "SP row has stagec_ckpt_id")); break
        elif cid != "sha256[:16]=ed437f21af15c305 epoch=1660 best_epoch=1660 role=best 8x4": bad_meta.append((t, o["file"], "ckpt id", cid)); break
        if r["PICK"] != "-":
            e = PICK["per_snr"][str(int(o["name"][2]))]
            if json.loads(mt.get("sparse", "null")) != dict(rho_sbl=PICK["rho_sbl"], rho_omp=PICK["rho_omp"], n_em=e["n_em"], L=e["L"]): bad_meta.append((t, o["file"], "sparse", mt.get("sparse"))); break
        elif "sparse" in mt: bad_meta.append((t, o["file"], "unexpected meta|sparse")); break
        if "rotation" in mt: bad_meta.append((t, o["file"], "unexpected meta|rotation")); break
        if "--ald-file" in r["FL"]:
            if mt.get("ald_file") != f"/home/HTJ/t2/conf/results/ald/ald_PILSRB_hisnr.npz sha256[:16]={ALD_HS_SHA}": bad_meta.append((t, o["file"], "ald_file", mt.get("ald_file"))); break
        elif "ald_file" in mt: bad_meta.append((t, o["file"], "unexpected meta|ald_file")); break
    arms = set(r["ARMS"].split())
    if any(set(o["arms"]) != arms for o in L): bad_shape.append((t, "arm set", sorted({a for o in L for a in o["arms"]})))
    if any(v[2] != (40, 16) for o in L for v in o["arms"].values()): bad_shape.append((t, "shape"))
    if any(v[3] or v[4] or v[5] for o in L for v in o["arms"].values()): bad_raised.append(t)
    c = {a: {s: 0 for s in SN} for a in arms}; c1 = {s: 0 for s in SN}
    for o in L:
        for a, v in o["arms"].items():
            c[a][o["name"][2]] += v[0]
            if a == "R0-pilot": c1[o["name"][2]] += v[1]
    COUNTS[t] = c; COUNTS1[t] = c1 if "R0-pilot" in arms else None
    MT[t] = (min(o["mtime"] for o in L), max(o["mtime"] for o in L))
chk("B1 trial plan: 3 tags x 2048 chunks = 4 SNR x skip 10000..30440 step 40 (each once), n 40; run|snr/skip/n = file name; cell C2 prior SRB", not bad_plan, str(bad_plan))
chk("B2 run|git == '193776a1' (no +dirty), run|iters 16, run|seed 20260926 in every chunk", not bad_git, str(bad_git))
chk("B3 meta: ntrain 160000 / bstar gmm1024 / ll_val|gmm1024 97.00871495382869 / stagec_ckpt_id (sha ed437f21af15c305, role best; absent in SP) / meta|sparse == pick (SP only) / no rotation / meta|ald_file == path + sha (ALD only)",
    not bad_meta, str(bad_meta[:3]))
chk("B4 arm set of every chunk = the row's; blk_err shape (40, 16)", not bad_shape, str(bad_shape[:3]))
chk("B5 raised trials 0: no |failed| key, no non-finite blk_err@16 in any chunk of the 3 raws", not bad_raised, str(bad_raised))
# genie replay across the three raws (all KEYS_RAW + guardH)
bad = []; ncmp = 0
for t in ("FHSPSRB", "FHALDSRB"):
    for o in BY[t]:
        with np.load(f"raw_{t}/{o['file']}") as z, np.load(f"raw_FHSRBB16e4/{o['file']}") as y:
            for q in KEYS_RAW + ("guardH",):
                k = f"R5-genie|{q}"; ncmp += 1
                if k not in z.files or k not in y.files or z[k].shape != y[k].shape or not np.array_equal(z[k], y[k], equal_nan=True): bad.append((t, o["file"], k))
chk(f"B6 R5-genie bit-identical across the three FH raws: FHSPSRB / FHALDSRB vs FHSRBB16e4, every chunk x KEYS_RAW 7 + guardH ({ncmp} arrays)", not bad, str(bad[:3]))
print("   genie failures per SNR: " + " · ".join(f"{t} {[COUNTS[t]['R5-genie'][s] for s in SN]}" for t in TAGS))

# ====================================================================== C. original raws
print("\n# C. scanning the 3 original raws ...")
OB = {o: [scan(p) for p in sorted(glob.glob(f"raw_{o}/D2_*.npz"))] for o in ("SRBB16e4", "SPSRB", "ALDSRB")}
OC, OC1 = {}, {}
bad = []
for o, L in OB.items():
    if [x for x in L if x["err"]]: bad.append((o, "unreadable"))
    plan = {}
    for x in L: plan.setdefault(x["name"][2], []).append((x["name"][3], x["name"][4]))
    if len(L) != 448 or set(plan) != set(ALL) or any(sorted(v) != [(40 * k, 40) for k in range(64)] for v in plan.values()): bad.append((o, len(L)))
    if {x["git"] for x in L} != ({"9ad4caa0"} if o == "SRBB16e4" else {"7d524638"}): bad.append((o, "git", {x["git"] for x in L}))
    c, c1 = {}, {s: [0, 0] for s in ALL}
    for x in L:
        for a, v in x["arms"].items():
            d = c.setdefault(a, {}).setdefault(x["name"][2], [0, 0, 0]); d[0] += v[0]; d[1] += v[2][0]; d[2] += v[3]
            if a == "R0-pilot": c1[x["name"][2]][0] += v[1]; c1[x["name"][2]][1] += v[2][0]
    OC[o] = {a: {s: (v[0], v[1]) for s, v in d.items()} for a, d in c.items()}; OC1[o] = {s: tuple(v) for s, v in c1.items()}
    if any(v[1] != N1 for d in c.values() for v in d.values()): bad.append((o, "n != 2560"))
    if any(v[2] for d in c.values() for v in d.values()): bad.append((o, "non-finite"))
chk("C1 original raws SRBB16e4 (git 9ad4caa0) / SPSRB / ALDSRB (7d524638): 448 chunks = 7 SNR x skip 0..2520 step 40, n 2560, no non-finite", not bad, str(bad))
def ocount(a, o, s): return OC1[o][s][0] if a == "R0-pilot@1" else OC[o][a][s][0]
def ncount(a, t, s): return COUNTS1[t][s] if a == "R0-pilot@1" else COUNTS[t][a][s]
MERGED = {a: [(ocount(a, SRC[a][1], s), N1) for s in ALL[:3]] + [(ncount(a, SRC[a][0], s), N2) for s in SN] for a in ORDER}
ORIG7 = {a: [(ocount(a, SRC[a][1], s), N1) for s in ALL] for a in ORDER}

# ====================================================================== D. controls
print("\n# D. controls")
bad = []; tot = 0
for r in ROWS:
    c = r["TAG"].replace("FH", "FHC", 1); arms = r["ARMS"].split(); fs = sorted(glob.glob(f"raw_{c}/D2_*.npz")); n = 0; b = []
    names = sorted(os.path.basename(f) for f in fs)
    if names != sorted(f"D2_C2_SRB_Nr8_T16_Tp4_dft_snr{int(s)}_skip0_n40.npz" for s in SN): b.append(("names", names))
    for f in fs:
        with np.load(f) as z, np.load(f"raw_{r['ORIG']}/{os.path.basename(f)}") as y:
            if str(z["run|git"]) != "193776a1": b.append((f, "git", str(z["run|git"])))
            for a in arms:
                for q in KEYS_RAW:
                    k = f"{a}|{q}"; n += 1
                    if k not in z.files or k not in y.files or z[k].shape != y[k].shape or not np.array_equal(z[k], y[k], equal_nan=True): b.append((os.path.basename(f), k))
    tot += n
    txt = open(f"{RV}/{c}_control.txt").read()
    m = re.search(r"(\d+) chunk files \(expected (\d+)\).*?(\d+) \(chunk, arm, key\) comparisons, (\d+) differ", txt)
    if len(fs) != 4 or b or not m or (int(m[1]), int(m[2]), int(m[3]), int(m[4])) != (4, 4, n, 0) or txt.rstrip().split("\n")[-1] != "CONTROL: OK": bad.append((c, len(fs), n, b[:2], m and m.groups()))
    print(f"   {c}: {len(fs)} chunks, {n} (chunk, arm, key) comparisons, {len(b)} differ (file says {m and m.groups()})")
chk("D1 receiver controls: raw_FHC* (4 chunks, trials 0..39, run|git 193776a1) vs the original raws, every arm x KEYS_RAW bit-identical (NaN = NaN); counts = *_control.txt (196 / 112 / 56); CONTROL: OK",
    not bad and tot == 196 + 112 + 56, str(bad[:3]))
A, Bn = np.load("results/ald/ald_FHCALDSRB.npz"), np.load("results/ald/ald_PILSRB.npz")
same = all(A[k].shape == Bn[k].shape and np.array_equal(A[k], Bn[k]) for k in ("hhat", "b", "v"))
txt = open(f"{RV}/FHCALDSRB_aldcontrol.txt").read()
chk("D2 ALD estimator control: ald_FHCALDSRB.npz hhat (7, 2560, 32) / b / v bit-identical to ald_PILSRB.npz; file says max|diff| 0, CONTROL-ALD: OK",
    same and A["hhat"].shape == (7, 2560, 32) and "max|diff| 0," in txt and txt.rstrip().endswith("CONTROL-ALD: OK"))
chk("D3 FHC copies of the frozen ALD records = the originals (tune json, dev / test pilots sha)",
    all(sha(f"results/ald/{x}_FHCALDSRB{y}") == sha(f"results/ald/{x}_PILSRB{y}") for x, y in (("tune", ".json"), ("pilots", "_dev.npz"), ("pilots", "_test.npz"))))

# ====================================================================== E. count tables + §6.2
print("\n# E. count tables / §6.2")
TAB = {}; bad, bad_w, nrow, heads = [], [], 0, []
for r in ROWS:
    t = r["TAG"]; tb = {}
    for l in open(f"{RV}/fighs_{t}.txt"):
        if l.startswith("#"): heads.append(l.strip()); continue
        m = re.match(r"SNR ([+-]\d+)\s+(\S+)\s+(\d+) / (\d+)\s+BLER (\S+)\s+95% \[(\S+), (\S+)\]\s*$", l)
        if not m: continue
        s, a, f, n = float(m[1]), m[2], int(m[3]), int(m[4]); tb[(s, a)] = (f, n, m[5], m[6], m[7]); nrow += 1
        want = COUNTS1[t][s] if a == "R0-pilot@1" else COUNTS[t].get(a, {}).get(s)
        if want is None or (f, n) != (want, N2): bad.append((t, s, a, (f, n), want))
        lo, hi = wilson(f, n)
        if (f"{f / n:.2e}", f"{lo:.2e}", f"{hi:.2e}") != (m[5], m[6], m[7]): bad_w.append((t, s, a, m[5:8], f"{f / n:.2e} {lo:.2e} {hi:.2e}"))
    TAB[t] = tb
    if len(tb) != 4 * (len(r["ARMS"].split()) + ("R0-pilot" in r["ARMS"])): bad.append((t, "rows", len(tb)))
chk(f"E1 count tables: every (SNR, arm) failures / n = own recount ({nrow} rows incl. R0-pilot@1 = iteration 1); 32 + 16 + 8 rows", not bad and nrow == 56, str(bad[:4]))
chk(f"E2 count tables: BLER / Wilson strings (%.2e, z 1.959964) re-formatted from own Wilson ({nrow} rows)", not bad_w, str(bad_w[:3]))
chk("E3 count-table headers = §6.1 '집계표 머리말' lines (3) and say load_raw warnings 0", [f"- `{h}`" for h in heads] == [l for l in S6 if l.startswith("- `# run_fighsroom16e4")] and all(h.endswith("load_raw warnings 0") for h in heads))
# §6.2 table
bad = []; n62 = 0
for l in S6:
    m = re.match(r"^\| (\S+) \| raw_(FH\w+) \| (.*) \| (\d+) / (\d+) / (\d+) / (\d+) \|$", l)
    if not m or m[1] not in ORDER: continue
    a, t = m[1], m[2]; cells = m[3].split(" | ")
    if t != SRC[a][0]: bad.append((a, "source", t))
    for i, s in enumerate(SN):
        q = re.match(r"^(\d+) \((\S+), \[(\S+), (\S+)\]\)$", cells[i]); n62 += 1
        k = ncount(a, t, s); lo, hi = wilson(k, N2)
        if not q or (int(q[1]), q[2], q[3], q[4]) != (k, f"{k / N2:.2e}", f"{lo:.2e}", f"{hi:.2e}"): bad.append((a, s, cells[i], k))
    if [int(m[i]) for i in range(4, 8)] != [ocount(a, SRC[a][1], s) for s in SN]: bad.append((a, "orig", m.groups()[3:], [ocount(a, SRC[a][1], s) for s in SN]))
chk(f"E4 §6.2 table: 11 curves x 4 SNR k / BLER / Wilson from the new raws ({n62} cells) + source raw + '원 raw k / 2560' column from the original raws", not bad and n62 == 44, str(bad[:4]))
g = {t: [COUNTS[t]["R5-genie"][s] for s in SN] for t in TAGS}
chk("E5 §6.2 genie line: 'FHSRBB16e4 [17, 5, 1, 1] · FHSPSRB [17, 5, 1, 1] · FHALDSRB [17, 5, 1, 1] → 동일'",
    any(l.startswith("Perfect CSI (R5-genie) 의 실패 수는 세 raw 에서 같다: " + " · ".join(f"{t} {v}" for t, v in g.items()) + " → 동일.") for l in S6) and len({tuple(v) for v in g.values()}) == 1 and g["FHSRBB16e4"] == [17, 5, 1, 1])
zero = [f"{a} {s:+.0f} dB" for a in ORDER for s in SN if ncount(a, SRC[a][0], s) == 0]
chk("E6 §6.2 '0 실패 점 (n = 20480): 없음' = recount", not zero and "0 실패 점 (n = 20480): 없음." in S6, str(zero))
# rising cells of the merged curves (all 7 SNRs), one-sided Fisher p, %.2g
mine = {}
for a in ORDER:
    seq = MERGED[a]
    up = [f"{ALL[i - 1]:+.0f}->{ALL[i]:+.0f} dB p={fisher_p(seq[i], seq[i - 1]):.2g}" for i in rising(seq)]
    mine[a] = (f"    {a:<20}@16  " + " ".join(f"{k}/{n}" for k, n in seq[3:]) + f"   (raw_{SRC[a][0]})" + (f"   rising: {'; '.join(up)}" if up else ""))
rec = open(f"{REC}/paper_f21srbhs.txt", encoding="utf-8").read().split("\n")
blk = [l for l in rec if re.match(r"^    \S+\s+@16  ", l)]
chk("G1 figure record paper_f21srbhs.txt merge block: 11 lines, k/n at +6..+15 = new raws, source tag, 'rising' cells + one-sided Fisher p (%.2g) over the 7 merged points — byte-identical to own",
    blk == [mine[a] for a in ORDER], f"diff {[(x, y) for x, y in zip(blk, [mine[a] for a in ORDER]) if x != y][:2]}")
ris = [l.strip() for l in blk if "rising:" in l]
chk("E7 §6.2 'rising' lines (3) = the figure record's rising lines = own (V1 +12->+15 p=0.5; ALD-pilot +12->+15 p=0.24; R3 +9->+12 p=3.7e-06)",
    [l[3:-1] for l in S6 if l.startswith("- `") and "rising:" in l] == ris == [mine[a].strip() for a in ORDER if "rising:" in mine[a]] and len(ris) == 3 and
    any("오르는 칸" in l and ": 3 줄." in l for l in S6), str(ris))
print("   own rising cells: " + " | ".join(l.split("rising: ")[1] for l in ris))
print("   all rising cells of the 11 merged curves (incl. +3->+6): " + str({a: [f"{ALL[i-1]:+.0f}->{ALL[i]:+.0f}" for i in rising(MERGED[a])] for a in ORDER if rising(MERGED[a])}))

# ====================================================================== F. §6.3 predictions
print("\n# F. §6.3 predictions (scored by me against §3 wording)")
V = [ncount("M-ours-dscore-C-V1", "FHSRBB16e4", s) for s in SN]; B = [ncount("M-ours-bstar", "FHSRBB16e4", s) for s in SN]
p2 = {a: [fisher_p(MERGED[a][i], MERGED[a][i - 1]) for i in rising(MERGED[a])] for a in ("M-ours-dscore-C-V1", "M-ours-bstar", "R5-genie")}
LOG = [l for l in open("logs/run_fighsroom16e4.log", encoding="utf-8", errors="replace").read().split("\n") if l.startswith("[fighs ")]
done = [l for l in LOG if "FIGHS_DONE" in l]
sc = {1: V[0] > V[1], 2: all(p >= 0.05 for v in p2.values() for p in v), 3: V[0] <= B[0] and V[1] <= B[1], 4: V[3] <= 5, 5: len(done) == 1 and done[0].endswith("FIGHS_DONE ok=3 fail=0")}
got = {int(m[1]): m[2] for l in S6 for m in [re.match(r"^(\d)\. .*→ \*\*(적중|빗나감)\*\*", l)] if m}
chk("F1 §6.3: five predictions all '적중' and my own scoring agrees (1: 45 > 10; 2: rising-cell p's of V1/b*/genie all >= 0.05 incl. the +3->+6 cell; 3: 45<=90, 10<=23; 4: 4 <= 5; 5: ok=3 fail=0)",
    got == {i: "적중" for i in range(1, 6)} and all(sc.values()), f"V {V}, b* {B}, p2 {p2}, got {got}")
chk("F2 §6.3 item 2 quotes p 0.5 for V1 and 없음 for b* / genie; items 1/3/4 quote (45 대 10), (45 대 90, 10 대 23), (4)",
    any("M-ours-dscore-C-V1 [0.5], M-ours-bstar 없음, R5-genie 없음" in l for l in S6) and any("(45 대 10)" in l for l in S6) and any("(45 대 90, 10 대 23)" in l for l in S6) and
    any(l.startswith("4. ") and "(4)." in l for l in S6) and [f"{p:.2g}" for p in p2["M-ours-dscore-C-V1"]] == ["0.5"] and not p2["M-ours-bstar"] and not p2["R5-genie"])

# ====================================================================== G. figure records
print("\n# G. figure records")
cnt = {}
for l in rec[rec.index("Counts:") + 1:]:
    f = l.split()
    if not f: break
    if f[0] in ORDER: cnt[f[0]] = ([tuple(int(x) for x in v.split("/")) for v in f[1:8]], f[8])
chk("G2 paper_f21srbhs.txt 'Counts:' block = merged (−3/0/+3 original n 2560, +6..+15 new n 20480) for the 11 curves; source = original raw",
    all(cnt[a][0] == MERGED[a] and cnt[a][1] == f"raw_{SRC[a][1]}" for a in ORDER) and len(cnt) == 11)
rec0 = open(f"{REC}/paper_f21srb.txt", encoding="utf-8").read().split("\n"); cnt0 = {}
for l in rec0[rec0.index("Counts:") + 1:]:
    f = l.split()
    if not f: break
    if f[0] in ORDER: cnt0[f[0]] = [tuple(int(x) for x in v.split("/")) for v in f[1:8]]
chk("G3 paper_f21srb.txt (original figure record, n 2560 at 7 SNRs) 'Counts:' = own recount of the original raws (11 x 7)", all(cnt0[a] == ORIG7[a] for a in ORDER) and len(cnt0) == 11)
zero0 = [(a, s) for a in ORDER for s, (k, n) in zip(ALL, ORIG7[a]) if k == 0]
chk("G4 original record: 6 zero-failure points (V1 +12/+15, ALD +15, genie +9/+12/+15); merged record has no zero-failure line and no point with k = 0",
    zero0 == [("M-ours-dscore-C-V1", 12.0), ("M-ours-dscore-C-V1", 15.0), ("ALD-pilot", 15.0), ("R5-genie", 9.0), ("R5-genie", 12.0), ("R5-genie", 15.0)] and
    not any(l.startswith("Zero-failure points") for l in rec) and not [a for a in ORDER for k, n in MERGED[a] if k == 0])
below = [a for a in ORDER if a not in ("M-ours-dscore-C-V1", "R5-genie") and any(k <= kv for (k, _), (kv, _) in zip(MERGED[a], MERGED["M-ours-dscore-C-V1"]))]
chk("G5 merged record 'at or below the proposed curve: none' = own (no drawn baseline point <= V1's at any of the 7 merged points)",
    not below and any(l.endswith("pairB_SPSRB.txt: none.") for l in rec), str(below))
# y-range rule (paper_f21dmc.py ROOM branch): (2e-4, 1.2) iff no zero point and min over (Wilson lower for BARS arms else k/n) of k>0 points > 2e-4; else (3e-5, 1.2)
pos = {(a, s): (wilson(k, n)[0] if a in BARS else k / n) for a in ORDER for s, (k, n) in zip(ALL, MERGED[a]) if k > 0}
lowpts = sorted((a, s, f"{v:.3g}") for (a, s), v in pos.items() if v <= 2e-4)
ylim = "(3e-05, 1.2)" if min(pos.values()) <= 2e-4 else "(0.0002, 1.2)"
chk("G6 y-range rule on the drawn (merged) values -> (3e-05, 1.2) as the record / §6.4 say; the values at or below 2e-4 are listed below",
    ylim == "(3e-05, 1.2)" and any("y log (3e-05, 1.2)" in l for l in rec) and any("y 축 (3e-05, 1.2)" in l for l in S6), str(lowpts))
print("   drawn values (Wilson lower bar end for V1/b*/R2/genie, else k/n) at or below 2e-4: " + "; ".join(f"{a} {s:+.0f} dB {v}" for a, s, v in lowpts))
print("   point estimates k/n below 2e-4 (any arm): " + "; ".join(f"{a} {s:+.0f} dB {k}/{n}={k/n:.3g}" for a in ORDER for s, (k, n) in zip(ALL, MERGED[a]) if 0 < k / n < 2e-4))
# the §6.4 reason sentence
chk("G7 §6.4 names Perfect CSI +12/+15 dB (1/20480 = 4.9e-05) as the reason for the second range: true but not the only sub-2e-4 drawn value (see G6 list; INFO)",
    any("Perfect CSI 의 +12 · +15 dB 점(1 / 20480 = 4.9e-05)이 2e-4 아래" in l for l in S6))
chk("G8 figure files F21srbhs_col.{pdf,png} + record mtime after FIGHS_DONE (18:31 CDT) and before the §6 record time 18:32 CDT; F21srb_col untouched since f183160d-era (06:43 KST)",
    all(cdt(os.stat(f"../conference/figures/{f}").st_mtime) > datetime(2026, 10, 11, 18, 31, tzinfo=CDT) for f in ("F21srbhs_col.pdf", "F21srbhs_col.png", "records/paper_f21srbhs.txt")) and
    cdt(os.stat("../conference/figures/F21srb_col.pdf").st_mtime) < datetime(2026, 10, 11, 17, 1, tzinfo=CDT),
    " ".join(f"{f} {cdt(os.stat('../conference/figures/' + f).st_mtime):%H:%M:%S}" for f in ("F21srbhs_col.pdf", "F21srbhs_col.png", "records/paper_f21srbhs.txt", "F21srb_col.pdf", "records/paper_f21srb.txt")))

# ====================================================================== H. run log, runner logs, manifests, mtimes, git
print("\n# H. logs / timeline")
def tsl(l):
    m = re.match(r"\[fighs (\d\d)-(\d\d) (\d\d):(\d\d) CDT\]", l)
    return datetime(2026, int(m[1]), int(m[2]), int(m[3]), int(m[4]), tzinfo=CDT) if m else None
starts = [l for l in LOG if "start (git" in l]
chk("H1 run log: ONE start line '[fighs 10-11 17:01 CDT] start (git 193776a1) rows: all resume=0 skip0 10000 n 20480 SNR 6 9 12 15'; no resume line",
    starts == ["[fighs 10-11 17:01 CDT] start (git 193776a1) rows: all resume=0 skip0 10000 n 20480 SNR 6 9 12 15"] and not any("resume:" in l for l in LOG))
chk("H2 phase C line '[fighs 10-11 17:03 CDT] phase C done: 3 receiver control(s) OK, 1 ALD estimator control(s) OK'; FIGHS_DONE ok=3 fail=0 at 10-11 18:31 CDT = last line; no ABORT/SKIP/INVALID/FAILED/rc!=0",
    "[fighs 10-11 17:03 CDT] phase C done: 3 receiver control(s) OK, 1 ALD estimator control(s) OK" in LOG and LOG[-1] == "[fighs 10-11 18:31 CDT] FIGHS_DONE ok=3 fail=0" and
    not any(re.search(r"ABORT|INVALID|SKIP|FAILED|rc=[1-9]", l) for l in LOG))
RUN = {m[1]: tsl(l) for l in LOG for m in [re.match(r"\[fighs [^\]]+\] (FH\w+) run:", l)] if m}
ACC = {m[1]: (tsl(l), int(m[2]), m[3].strip()) for l in LOG for m in [re.match(r"\[fighs [^\]]+\] (FH\w+) acceptance rc=(\d+) \((.*)\)", l)] if m}
chk("H3 run / acceptance lines: FHSRBB16e4 17:03 / 17:42, FHSPSRB 17:42 / 18:24, FHALDSRB 18:28 / 18:31, rc 0, 'ACCEPT: OK -- <tag> ACCEPT (f): OK'",
    [(t, f"{RUN[t]:%H:%M}", f"{ACC[t][0]:%H:%M}", ACC[t][1], ACC[t][2]) for t in TAGS] ==
    [("FHSRBB16e4", "17:03", "17:42", 0, "ACCEPT: OK -- FHSRBB16e4 ACCEPT (f): OK"), ("FHSPSRB", "17:42", "18:24", 0, "ACCEPT: OK -- FHSPSRB ACCEPT (f): OK"), ("FHALDSRB", "18:28", "18:31", 0, "ACCEPT: OK -- FHALDSRB ACCEPT (f): OK")])
chk("H4 ALD lines: estimator control on GPU 1 at 17:01; new-trial regen+estimate on GPU 1 at 18:25 'rotation none'; '[ald regen] PILSRB hisnr: 4 SNR x 20480 trials (skip 10000)'",
    "[fighs 10-11 17:01 CDT] FHALDSRB ALD estimator control: ald.py estimate --tag FHCALDSRB --set test on GPU 1 (copies of the frozen records of PILSRB)" in LOG and
    "[fighs 10-11 18:25 CDT] FHALDSRB ALD PILSRB: regen (CPU) + estimate (GPU 1) on trials 10000.., rotation none (tune record results/ald/tune_PILSRB.json)" in LOG and
    any(l.startswith("[ald regen] PILSRB hisnr: 4 SNR x 20480 trials (skip 10000) rotation=None doppler=None") for l in open("logs/run_fighsroom16e4.log", encoding="utf-8").read().split("\n")))
# runner logs + §6.1 table
bad = []; rows61 = {}
for l in S6:
    m = re.match(r"^\| (FH\w+) \| 10-11 (\d\d:\d\d) \| (\S+) 분 · (\d+) 작업 · (\d+) 워커 \| (\d+) / (\d+) \| 10-11 (\d\d:\d\d) \| (.*?) \| (\w+) · (\w+) \| (.*?) \|$", l)
    if m: rows61[m[1]] = m.groups()
for t in TAGS:
    rl = open(f"logs/run_D2_{t}.log", encoding="utf-8", errors="replace").read().split("\n")
    hd = [l for l in rl if l.startswith("# run_fighs")]
    mins = re.findall(r"\[run\] finished in ([\d.]+) min", "\n".join(rl)); tasks = re.findall(r"-> (\d+) tasks on (\d+) workers", "\n".join(rl))
    nd, ne = sum(bool(re.match(r"\d+/\d+ done ", l)) for l in rl), sum(bool(re.match(r"\d+/\d+ exists", l)) for l in rl)
    af = open(f"{RV}/{t}_accept.txt").read(); v = "; ".join(x.strip() for x in af.split("\n") if x.startswith("ACCEPT"))
    man = json.load(open(f"{RV}/run_manifest_{t}.json"))
    ctl = open(f"{RV}/{t.replace('FH', 'FHC', 1)}_control.txt").read().strip().split("\n")[-1]
    if t == "FHALDSRB": ctl += " · " + open(f"{RV}/FHCALDSRB_aldcontrol.txt").read().strip().split("\n")[-1]
    want = (t, f"{RUN[t]:%H:%M}", mins[0], tasks[0][0], tasks[0][1], str(nd), str(ne), f"{ACC[t][0]:%H:%M}", f"rc={ACC[t][1]}; {v}", man["git_commit"], man["config_hash"], ctl)
    if rows61.get(t) != want: bad.append((t, rows61.get(t), want))
    if hd != [f"# run_fighsroom16e4 git 193776a1 2026-10-11 {RUN[t]:%H:%M} CDT resume=0"] or len(mins) != 1 or nd != 2048 or ne != 0 or tasks != [("2048", "192")]: bad.append((t, "runner log", hd, mins, nd, ne, tasks))
    if man["n_raw_files"] != 2048 or sorted(man["arms"]) != sorted(ROWS[TAGS.index(t)]["ARMS"].split()) or man["git_commit"] != "193776a1" or man["config_hash"] != "cef74db071b50187": bad.append((t, "manifest", man["n_raw_files"], man["arms"]))
    w = datetime.strptime(man["written"], "%Y-%m-%d %H:%M:%S KST").replace(tzinfo=KST)
    if not (RUN[t] <= w <= ACC[t][0] + __import__("datetime").timedelta(minutes=1)): bad.append((t, "manifest written outside run..acceptance", man["written"]))
    if not (RUN[t] <= cdt(MT[t][0]) and cdt(MT[t][1]) <= ACC[t][0] + __import__("datetime").timedelta(minutes=1)): bad.append((t, "chunk mtimes outside run..acceptance", cdt(MT[t][0]), cdt(MT[t][1])))
    if f"run|git ['193776a1']" not in af or not re.search(r"raised trials per arm \(= failures, report only\) 0\n", af): bad.append((t, "accept file", af))
chk("H5 §6.1 per-row table (3 rows: start, runner minutes / tasks / workers, done / exists, acceptance time, verdicts, manifest git · config_hash, control verdicts) = logs + files; runner logs one header, 2048 done, 0 exists; manifests 2048 files / arms / git / hash, written inside run..acceptance; chunk mtimes inside run..acceptance",
    not bad, str(bad[:2]))
print("   chunk mtime windows (CDT): " + " · ".join(f"{t} {cdt(MT[t][0]):%H:%M:%S}–{cdt(MT[t][1]):%H:%M:%S}" for t in TAGS))
print("   manifests written: " + " · ".join(json.load(open(f"{RV}/run_manifest_{t}.json"))["written"] for t in TAGS))
fl = [l for l in S6 if l.startswith("- `(f) raw_")]
chk("H6 §6.1 '(f)' lines (3) = the accept files' (f) lines verbatim",
    fl == [f"- `{x.strip()}`" for t in TAGS for x in open(f"{RV}/{t}_accept.txt").read().split("\n") if x.strip().startswith("(f)")] and len(fl) == 3)
gl = sh("git log --format='%h %ci' 193776a1^..ed265304").split("\n")
t193 = datetime.strptime(sh("git log -1 --format=%ci 193776a1"), "%Y-%m-%d %H:%M:%S %z"); ted = datetime.strptime(sh("git log -1 --format=%ci ed265304"), "%Y-%m-%d %H:%M:%S %z")
chk("H7 git: no commit between 193776a1 (17:01:06 CDT, before the 17:01 start line's minute end and before the first chunk) and ed265304 (18:33:26 CDT, after FIGHS_DONE 18:31)",
    len(gl) == 2 and t193.astimezone(CDT) < cdt(MT["FHSRBB16e4"][0]) and ted.astimezone(CDT) > datetime(2026, 10, 11, 18, 31, tzinfo=CDT) and
    t193.astimezone(CDT) < datetime(2026, 10, 11, 17, 2, tzinfo=CDT), f"{t193.astimezone(CDT)} .. {ted.astimezone(CDT)}; {gl}")
chk("H8 §6 header '기록 2026-10-11 18:32 CDT' = registration file mtime (08:32 KST); s6_fighsroom_gen.py same minute; ROOM16e4 record mtime 17:03 CDT; audit_ROOM16e4.md mtime 17:01 CDT (§6.4 '17:01 CDT 까지')",
    f"{cdt(os.stat(REG).st_mtime):%H:%M}" == "18:32" and f"{cdt(os.stat(f'{RV}/prereg_audit_2026-10-11/s6_fighsroom_gen.py').st_mtime):%H:%M}" == "18:32" and
    f"{cdt(os.stat(f'{RV}/NEXT_EXPERIMENTS_ROOM16e4.md').st_mtime):%H:%M}" == "17:03" and f"{cdt(os.stat(f'{RV}/prereg_audit_2026-10-11/audit_ROOM16e4.md').st_mtime):%H:%M}" == "17:01")
pre = [p for p in ("raw_FHSRBB16e4", "raw_FHSPSRB", "raw_FHALDSRB", "results/ald/ald_PILSRB_hisnr.npz", "results/ald/pilots_PILSRB_hisnr.npz") if cdt(os.stat(p).st_mtime) < datetime(2026, 10, 11, 17, 1, tzinfo=CDT)]
chk("H9 §5 '실행 시작 전 상태: raw_FH* · ald_PILSRB_hisnr.npz 없음': every such path has an mtime after the 17:01 CDT start (dirs and files)", not pre, str(pre))
chk("H10 paper_f21dmc.py mtime 17:17 CDT (during the run, uncommitted then; committed in ed265304 = HSREG edit as §6.4 says); fighs_merge.py unchanged since 10-06 (19:22 CDT)",
    f"{cdt(os.stat('../conference/figures/paper_f21dmc.py').st_mtime):%m-%d %H:%M}" == "10-11 17:17" and f"{cdt(os.stat('../conference/figures/fighs_merge.py').st_mtime):%m-%d %H:%M}" == "10-06 19:22",
    f"{cdt(os.stat('../conference/figures/paper_f21dmc.py').st_mtime)} {cdt(os.stat('../conference/figures/fighs_merge.py').st_mtime)}")

# ====================================================================== I. §6.4 / EXPERIMENTS row / DECISIONS
print("\n# I. §6.4, EXPERIMENTS, DECISIONS")
chk("I1 §6.4 'ald_PILSRB_hisnr.npz sha256[:16] a7b2c943b3968846 (git 밖)' = disk; file untracked", any("a7b2c943b3968846 (git 밖)" in l for l in S6) and ALD_HS_SHA == "a7b2c943b3968846" and not sh("git ls-files results/ald/ald_PILSRB_hisnr.npz"))
exp = [l for l in open("../docs/EXPERIMENTS.md", encoding="utf-8").read().split("\n") if "run_fighsroom16e4.sh" in l]
E = exp[0] if exp else ""
want_counts = "V1 45 / 10 / 3 / 4, ALD-pilot 81 / 25 / 7 / 11, b\\* 90 / 23 / 11 / 6, R2 438 / 135 / 37 / 19, R1 917 / 287 / 87 / 34, BiG-AMP 2861 / 2507 / 2813 / 2481, R0@1 2630 / 978 / 376 / 173, SBL-loop 261 / 73 / 17 / 13, SBL-pilot 306 / 85 / 23 / 13, OMP-pilot 607 / 217 / 63 / 53, genie 17 / 5 / 1 / 1 (세 raw 동일)"
NM = {"V1": "M-ours-dscore-C-V1", "ALD-pilot": "ALD-pilot", "b\\*": "M-ours-bstar", "R2": "R2-ours-G", "R1": "R1-turbo", "BiG-AMP": "R3-bigamp", "R0@1": "R0-pilot@1", "SBL-loop": "SBL-loop", "SBL-pilot": "SBL-pilot", "OMP-pilot": "OMP-pilot", "genie": "R5-genie"}
own = ", ".join(f"{k} " + " / ".join(str(ncount(a, SRC[a][0], s)) for s in SN) for k, a in NM.items()) + " (세 raw 동일)"
chk("I2 EXPERIMENTS.md FIGHSROOM16e4 row: the 11 x 4 failure counts = own recount", len(exp) == 1 and want_counts in E and want_counts == own, f"own: {own}")
chk("I3 EXPERIMENTS.md FIGHSROOM16e4 row: times 07:01 ~ 08:31 KST (17:01 ~ 18:31 CDT), 193776a1, FIGHS_DONE ok=3 fail=0, controls 3 + 1, ACCEPT x3, 0 zero-failure points, rising cells (0.5 / 0.24 / 3.7e-06), runner 39.0 · 41.6 · 1.5, ALD GPU 1 17:01 · 18:25, y (3e-05, 1.2), 5 predictions hit",
    all(x in E for x in ("2026-10-12 07:01 ~ 08:31 KST (텍사스 10-11 17:01 ~ 18:31 CDT; 한 번 시작, 재개 없음)", "실행 커밋 193776a1", "`FIGHS_DONE ok=3 fail=0`", "수신기 3 · ALD 추정기 1 OK; ACCEPT OK ×3", "0 실패 점 없음",
                        "V1 +12→+15 dB p 0.5, ALD-pilot +12→+15 dB p 0.24, BiG-AMP +9→+12 dB p 3.7e-06", "runner 39.0 · 41.6 · 1.5 분", "GPU 1 (17:01 · 18:25 CDT", "y (3e-05, 1.2)", "§3 예측 5 개 모두 적중", "| 193776a1 |")))
dec = [l for l in open("DECISIONS.md", encoding="utf-8").read().split("\n") if "FIGHSROOM16e4" in l and "08:33 KST" in l]
chk("I4 DECISIONS.md 08:33 KST line: FIGHSROOM16e4 17:01 ~ 18:31 CDT @193776a1, ok=3 fail=0, V1 45 / 10 / 3 / 4, b* 90 / 23 / 11 / 6, genie 17 / 5 / 1 / 1, 0 실패 점 없음, 예측 5 개 적중; ROOM16e4 audit MUST 0 · SHOULD 2 · NIT 8, 1,048 값",
    len(dec) == 1 and all(x in dec[0] for x in ("FIGHSROOM16e4: 10-11 17:01 ~ 18:31 CDT @193776a1, FIGHS_DONE ok=3 fail=0", "45 / 10 / 3 / 4, b* 90 / 23 / 11 / 6, genie 17 / 5 / 1 / 1 — 0 실패 점 없음", "예측 5 개 적중", "MUST 0 · SHOULD 2 · NIT 8", "1,048 값")))
# SRB baselines row: counts at -3 / +3 and the high-SNR V1 counts from the original raws
exp2 = [l for l in open("../docs/EXPERIMENTS.md", encoding="utf-8").read().split("\n") if "run_srb_base.sh" in l]
own2 = ", ".join(f"{k} {ocount(a, SRC[a][1], -3.0)} / {ocount(a, SRC[a][1], 3.0)}" for k, a in NM.items())
chk("I5 EXPERIMENTS.md SRB-baselines row: '실패 수 / 2560 (−3 / +3 dB)' 11 arms + '고SNR V1 3 / 4 / 0 / 0' = own recount of the original raws",
    len(exp2) == 1 and f"실패 수 / 2560 (−3 / +3 dB): {own2}." in exp2[0] and "V1 +6 / +9 / +12 / +15 dB = 3 / 4 / 0 / 0 건" in exp2[0] and [ocount("M-ours-dscore-C-V1", "SRBB16e4", s) for s in SN] == [3, 4, 0, 0], own2)
exp3 = [l for l in open("../docs/EXPERIMENTS.md", encoding="utf-8").read().split("\n") if "run_prior_eval.sh SRB SRBB16e4" in l]
bl = lambda a, s: f"{ocount(a, 'SRBB16e4', s) / N1:.3f}"
chk("I6 EXPERIMENTS.md SRB-main row: BLER@16 −3 / 0 / +3 dB genie / V1 / b* / R2 (3 dp) = own recount",
    len(exp3) == 1 and f"BLER@16 −3 / 0 / +3 dB: genie {bl('R5-genie', -3.0)} / {bl('R5-genie', 0.0)} / {bl('R5-genie', 3.0)}, V1 {bl('M-ours-dscore-C-V1', -3.0)} / {bl('M-ours-dscore-C-V1', 0.0)} / {bl('M-ours-dscore-C-V1', 3.0)}, b\\* {bl('M-ours-bstar', -3.0)} / {bl('M-ours-bstar', 0.0)} / {bl('M-ours-bstar', 3.0)}, R2 {bl('R2-ours-G', -3.0)} / {bl('R2-ours-G', 0.0)} / {bl('R2-ours-G', 3.0)}" in exp3[0],
    f"genie {[bl('R5-genie', s) for s in ALL[:3]]} V1 {[bl('M-ours-dscore-C-V1', s) for s in ALL[:3]]} b* {[bl('M-ours-bstar', s) for s in ALL[:3]]} R2 {[bl('R2-ours-G', s) for s in ALL[:3]]}")
# §1 cost estimate vs actual (info)
print(f"   INFO §1 cost estimate 65 / 50 / 10 min vs runner 39.0 / 41.6 / 1.5 min (+ ALD regen/estimate 18:25 -> 18:28); §6 does not compare them")
# pilot type named in the five new EXPERIMENTS rows vs the raw file names
EXP = open("../docs/EXPERIMENTS.md", encoding="utf-8").read().split("\n")
new5 = [l for l in EXP if any(x in l for x in ("run_srp_eval.sh", "run_srp_base.sh", "run_srb_eval.sh", "run_srb_base.sh", "run_fighsroom16e4.sh"))]
pil = {t: sorted({PAT.match(os.path.basename(p))[6] for p in glob.glob(f"raw_{t}/D2_*.npz")}) for t in ("SRPB16e4", "SRBB16e4", "FHSRBB16e4")}
bad = [(l[:60], "eig 파일럿" in l) for l in new5 if "eig 파일럿" in l]
chk(f"I7 EXPERIMENTS.md new rows: none says 'eig 파일럿' while the SRP / SRB raws are '_dft_' pilots (raw names {pil}; PATH16e4 §5 / ROOM16e4 §5 '파일럿 DFT')",
    not bad and all(v == ["dft"] for v in pil.values()), f"rows saying 'eig 파일럿': {[b[0] for b in bad]}")

# ====================================================================== J. ROOM16e4 additions (§6.8–6.10, [감사 …]) and the GB′ files
print("\n# J. ROOM16e4 additions")
room = open(f"{RV}/NEXT_EXPERIMENTS_ROOM16e4.md", encoding="utf-8").read()
ll = {K: float(np.load(f"results/gmm_fits_D2_SRBB16e4/fit_SRB_Nr8_fullK{K}_n160000.npz", allow_pickle=True)["ll_val"]) for K in (16, 32, 64, 128, 256, 512, 1024)}
gains = [ll[2 * K] - ll[K] for K in (16, 32, 64, 128, 256, 512)]
s1 = re.search(r"full 계열의 배증당 증가 ([^)]*) nat", room)
chk("J1 [감사 S1] 'full 계열의 배증당 증가 +10.1 · +11.0 · +10.1 · +7.8 nat' = the full-family ll_val gains per doubling from the fit files (last four)",
    s1 and s1[1] == " · ".join(f"{g:+.1f}" for g in gains[-4:]), f"record '{s1 and s1[1]}' vs fit files {[f'{g:+.1f}' for g in gains]} (16→32→64→128→256→512→1024)")
z = np.load("results/d2_gbprime_SRB_N160000_a1.npz"); r = z["nmse_model"] / z["nmse_gmm"]
zp = np.load("results/d2_gbprime_SRP_N160000_a1.npz"); rp = zp["nmse_model"] / zp["nmse_gmm"]
post = open("logs/tb2_post_SRB.log", encoding="utf-8").read()
chk("J2 §6.9 GB′: median 0.6472 / min 0.5949 / max 5.1046; 18 of 20 ratios < 1; σ 0.720 → 1.017 (0.2301 vs 0.2263); σ 0.855 → 5.105 (1.514 vs 0.297); SRP 20/20 < 1 max 0.913; log line; 16:33 → 16:40 CDT rc 0 on GPU 1; npz mtime 16:40:45 CDT > fit 14:49:46",
    (f"{np.median(r):.4f}", f"{r.min():.4f}", f"{r.max():.4f}", int((r < 1).sum())) == ("0.6472", "0.5949", "5.1046", 18) and f"{z['sigma'][18]:.3f} {r[18]:.3f} {z['nmse_model'][18]:.4f} {z['nmse_gmm'][18]:.4f}" == "0.720 1.017 0.2301 0.2263"
    and f"{z['sigma'][19]:.3f} {r[19]:.3f} {z['nmse_model'][19]:.3f} {z['nmse_gmm'][19]:.3f}" == "0.855 5.105 1.514 0.297" and int((rp < 1).sum()) == 20 and f"{rp.max():.3f}" == "0.913"
    and "[d2sx] GMM b* = gmm1024 (full K=1024) @N=160000 | diff/gmm min 0.5949 max 5.1046 median 0.6472 | equal_budget=True" in open("logs/gbprime_SRBB16e4.log").read()
    and "[post SRB 10-11 16:33 CDT] GB' resume on GPU 1" in post and "[post SRB 10-11 16:40 CDT] GB' rc=0" in post
    and f"{cdt(os.stat('results/d2_gbprime_SRB_N160000_a1.npz').st_mtime):%m-%d %H:%M:%S}" == "10-11 16:40:45" and f"{cdt(os.stat('results/gmm_fits_D2_SRBB16e4/fit_SRB_Nr8_fullK1024_n160000.npz').st_mtime):%H:%M:%S}" == "14:49:46"
    and all(x in room for x in ("median **0.6472** (min 0.5949 · **max 5.1046**", "σ 0.720 에서 1.017 (모델 NMSE 0.2301 대 GMM 0.2263)", "σ 0.855 (격자 끝)에서 5.105 (모델 1.514 대 GMM 0.297)", "(SRP 는 20 개 모두 < 1, max 0.913.)", "mtime 10-11 16:40:45 CDT > full 1024 적합 파일 mtime 14:49:46 CDT")),
    f"median {np.median(r):.4f} min {r.min():.4f} max {r.max():.4f} n<1 {int((r < 1).sum())}")
others = {"SRP": "gbprime_SRPB16e4.log", "SRT": "gbprime_SRTB16e4.log", "DMC": "gbprime_DMCB16e4.log", "U28": "gbprime_U28B16e4.log"}
med = {k: float(re.search(r"median ([\d.]+)", open(f"logs/{v}").read())[1]) for k, v in others.items()}
chk("J3 §6.9 neighbours: SRP 0.5836 · Sionna RT 도시 0.543 · DeepMIMO 도시 0.715 · UMi28 0.920 = the other GB′ logs' medians (3–4 dp); D3 0.559 = NEXT_EXPERIMENTS_D3B16e4.md",
    f"{med['SRP']:.4f}" == "0.5836" and abs(med['SRT'] - 0.543) < 0.00051 and abs(med['DMC'] - 0.715) < 0.00051 and abs(med['U28'] - 0.920) < 0.00051 and "GB′ median 0.559" in open(f"{RV}/NEXT_EXPERIMENTS_D3B16e4.md", encoding="utf-8").read()
    and "SRP 0.5836 · D3 0.559 · Sionna RT 도시 0.543 · DeepMIMO 도시 0.715 · UMi28 0.920" in room, str(med))
chk("J4 §3 item 8 reads 'GB′ median ≤ 0.90.' and §6.9 scores it 적중 (0.6472); §6.6 item 8 still says 채점 보류 (append-only, pointer in §6.9)",
    "8. GB′ median ≤ 0.90." in room and "**예측 8** (GB′ median ≤ 0.90) → **적중** (0.6472)" in room and "8. GB′ median ≤ 0.90 → **채점 보류**" in room)
hf = open(f"{RV}/SRBB16e4_highsnr_fail.txt", encoding="utf-8").read()
def sect(s): return hf.split(f"\n{s} dB  n=2560")[1].split("\n\n")[0]
tr = {s: re.findall(r"trial\s+(\d+): share ([\d.]+).*?also fail: (.*)$", sect(s), re.M) for s in ("+6", "+9")}
it = {s: re.search(r"by iteration \(1, 2, 4, 8, 16\): \[([\d, ]+)\]", sect(s))[1] for s in ("+6", "+9", "+12", "+15")}
med = {s: re.search(r"share median ([\d.]+)", sect(s))[1] for s in ("+6", "+9")}
chk("J5 §6.10 post hoc: V1 +6 dB trials 818 · 1737 · 2421 (share 0.914 · 0.938 · 0.933), +9 dB 177 · 1000 · 1528 · 2346 (0.917 · 0.816 · 0.930 · 0.922), +12/+15 0 failures, share medians ≈ 0.82, every failing trial also fails >= 2 of {b*, R2, V4, genie}, failures by iteration 77→15→4→3→3 and 33→6→5→4→4",
    [t[0] for t in tr["+6"]] == ["818", "1737", "2421"] and [t[1] for t in tr["+6"]] == ["0.914", "0.938", "0.933"] and [t[0] for t in tr["+9"]] == ["177", "1000", "1528", "2346"] and
    [t[1] for t in tr["+9"]] == ["0.917", "0.816", "0.930", "0.922"] and all(len([a for a in t[2].split(", ") if a in ("bstar", "R2-ours-G", "V4", "R5-genie")]) >= 2 for s in tr for t in tr[s]) and
    it["+6"] == "77, 15, 4, 3, 3" and it["+9"] == "33, 6, 5, 4, 4" and it["+12"].startswith("10, 2, 0, 0, 0") and it["+15"].startswith("6, 0, 0, 0, 0") and
    all(f"{float(med[s]):.2f}" == "0.82" for s in med) and "failures@16: V1 0  bstar 1" in sect("+12") and "failures@16: V1 0  bstar 1" in sect("+15") and
    all(x in room for x in ("+6 dB 3 건(시행 818 · 1737 · 2421) · +9 dB 4 건(177 · 1000 · 1528 · 2346) · +12 · +15 dB 0 건 / 2560", "0.914 · 0.938 · 0.933 / 0.917 · 0.816 · 0.930 · 0.922 (전체 시행의 중앙값 0.82)", "+6 dB 77 → 15 → 4 → 3 → 3, +9 dB 33 → 6 → 5 → 4 → 4")),
    f"{tr} {it} {med}")
chk("J6 §6.10 'highsnr_fail_SRB.py ... 주 실행의 raw 만 읽는다' and '커밋 1404d315': the script loads only raw_<TAG> (SRBB16e4); both files tracked since 1404d315; txt mtime 16:38 CDT < 1404d315 (16:44:51 CDT)",
    "raw_{TAG}" in open(f"{RV}/prereg_audit_2026-10-11/highsnr_fail_SRB.py").read() and open(f"{RV}/prereg_audit_2026-10-11/highsnr_fail_SRB.py").read().count("load_raw(") == 1 and
    sh(f"git log --format=%h --diff-filter=A -- {RV}/SRBB16e4_highsnr_fail.txt") == "1404d315" and sh(f"git log --format=%h --diff-filter=A -- {RV}/prereg_audit_2026-10-11/highsnr_fail_SRB.py") == "1404d315" and
    f"{cdt(os.stat(f'{RV}/SRBB16e4_highsnr_fail.txt').st_mtime):%H:%M}" == "16:38")
aud = open(f"{RV}/prereg_audit_2026-10-11/audit_ROOM16e4.md", encoding="utf-8").read()
chk("J7 [감사 N1] / [감사 N2] / [감사 N4] / §6.8 figures = audit_ROOM16e4.md (245 placeholders π 6.24e-6 sum 0.0015, 779 live, 99.85 %, full 512: 82, kron 2048: 586; last CI [0.128, 0.223]; SRP GB′ 14:07 → 15:52; 1,048 = 328 + 466 + 194 + 60; −48.6 → 100.43, it_best 180, 3.4 nat, 161 nat; MUST 0 · SHOULD 2 · NIT 8; [−0.299, −0.176])",
    all(x in room for x in ("245 개는 다시 뿌려진 자리채움 성분(π 각 6.24e-6, 합 0.0015)이고 질량의 99.85 % 는 779 성분", "full 512: 82 개, kron 2048: 586 개", "[0.128, 0.223] (`recovery_SRBB16e4last.txt`)", "14:07 → 15:52 CDT 에 돌았다", "1,048 값(328 + 466 + 194 + 60)", "−48.6 → 100.43, it_best 180", "3.4 nat", "+161 nat", "MUST 0 · SHOULD 2 · NIT 8", "[−0.299, −0.176]"))
    and all(x in aud for x in ("245 of the 1024 components", "π_k = 6.24e-6 each, total π mass 0.0015", "779 components carrying 99.85 %", "full 512: 82 of 512", "kron 2048: 586 of 2048", "[0.128, 0.223]", "14:07 → 15:52 CDT", "328 values checked, 0 differ", "466 values checked, 1 DIFF", "194 values checked, 6 DIFFs", "60 values checked, 0 differ", "−48.6 → 42.8 → 98.8 @10 → 100.43 @181, it_best 180", "train−val gap 3.4 nat", "161 nat", "[−0.299, −0.176]")))
chk("J8 §6.8 '불일치로 찍힌 7 줄' = the audit's 0 + 1 + 6 + 0 DIFF lines; 'eval_accept × 4' = four rerun_room_accept_*.txt files",
    "불일치로 찍힌 7 줄" in room and len(glob.glob(f"{RV}/prereg_audit_2026-10-11/rerun_room_accept_*.txt")) == 4)

print(f"\n# SUMMARY: {sum(ok for _, ok in CHECKS)} PASS / {sum(not ok for _, ok in CHECKS)} FAIL of {len(CHECKS)} checks  ({datetime.now(CDT):%Y-%m-%d %H:%M:%S %Z})")
for n, ok in CHECKS:
    if not ok: print("   FAIL:", n)
