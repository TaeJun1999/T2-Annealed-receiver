#!/usr/bin/env python
"""recompute_fighspath.py -- independent RECORD AUDIT of NEXT_EXPERIMENTS_FIGHSPATH16e4.md §6 (Fable 5.1 subagent, read-only) and of
the other record lines added in commit aefbfc12 (EXPERIMENTS rows, DECISIONS line, FIGHSROOM16e4 §6.4 in-place notes / §6.5 / §6.6,
ROOM16e4 [정정], audit_ROOM16e4.md erratum).  Adapted from recompute_fighsroom.py (same folder); every expected value is retyped from
the SRP record.  Run from /home/HTJ/t2/conf:
  CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=3 MKL_NUM_THREADS=3 ~/miniforge3/envs/torch/bin/python -B \
      results/review_next/prereg_audit_2026-10-11/recompute_fighspath.py > results/review_next/prereg_audit_2026-10-11/recompute_fighspath.out
Own numpy reader only (no analysis.load_raw, no s6_fighsroom_gen.py, no hisnr_report); count tables / figure records / registration
are compared AGAINST, never read as input.  Single process, writes only stdout.  Nothing under raw_FX* / *FX* is opened.
Sections: A rows / registration  B new raws (3 x 2048)  C original raws (3 x 448)  D controls  E count tables + §6.2  F §6.3
G figure record  H logs / manifests / mtimes / git  I §6.4, EXPERIMENTS row, DECISIONS  J other lines of aefbfc12.
"""
import glob, hashlib, json, os, re, subprocess
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import numpy as np
from scipy.stats import fisher_exact

os.chdir("/home/HTJ/t2/conf")
RV = "results/review_next"; AUD = f"{RV}/prereg_audit_2026-10-11"; REG = f"{RV}/NEXT_EXPERIMENTS_FIGHSPATH16e4.md"; REC = "../conference/figures/records"
RUNC, S6C = "c48ee796", "aefbfc12"
CDT, KST = ZoneInfo("America/Chicago"), ZoneInfo("Asia/Seoul")
SN = (6.0, 9.0, 12.0, 15.0); ALL = (-3.0, 0.0, 3.0) + SN; N2 = 20480; N1 = 2560
KEYS_RAW = ("blk_err", "ber", "nmse", "tauL_gmean", "alphaD", "tauL_clip_frac", "alphaD_clip")   # common.KEYS_RAW (copied)
PAT = re.compile(r"^D2_(C\d)_([A-Za-z0-9]+?)_Nr(\d+)_T(\d+)_Tp(\d+)_(dft|eig)_snr(-?\d+)_skip(\d+)_n(\d+)\.npz$")
ORDER = ["M-ours-dscore-C-V1", "ALD-pilot", "M-ours-bstar", "R2-ours-G", "R1-turbo", "R3-bigamp", "R0-pilot@1", "SBL-loop", "SBL-pilot",
         "OMP-pilot", "R5-genie"]
LABEL = {"M-ours-dscore-C-V1": "Proposed (diffusion prior)", "ALD-pilot": "Annealed Langevin (plug-in)", "M-ours-bstar": "GMM prior",
         "R2-ours-G": "Gaussian prior", "R1-turbo": "Turbo LMMSE receiver", "R3-bigamp": "BiG-AMP", "R0-pilot@1": "Pilot-only LMMSE",
         "SBL-loop": "SBL (in loop)", "SBL-pilot": "SBL (pilot-only)", "OMP-pilot": "OMP (pilot-only)", "R5-genie": "Perfect CSI"}
SRC = {a: ("FHSRPB16e4", "SRPB16e4") for a in ORDER}
SRC.update({"ALD-pilot": ("FHALDSRP", "ALDSRP"), "SBL-loop": ("FHSPSRP", "SPSRP"), "SBL-pilot": ("FHSPSRP", "SPSRP"), "OMP-pilot": ("FHSPSRP", "SPSRP")})
BARS = ("M-ours-dscore-C-V1", "M-ours-bstar", "R2-ours-G", "R5-genie")
CKID = "sha256[:16]=ac4699c78b3e2d80 epoch=694 best_epoch=694 role=best 8x4"
LLV = "244.1932863626755"

CHECKS = []; NVAL = [0]
def chk(name, ok, detail="", n=1):
    CHECKS.append((name, bool(ok))); NVAL[0] += n
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" -- {detail}" if detail else ""))
    return bool(ok)
def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
def wilson(k, n, z=1.959963984540054):
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h
def fisher_p(hi, lo):      # hi = (k, n) at the higher SNR, lo at the lower; one-sided 'greater'
    return fisher_exact([[hi[0], hi[1] - hi[0]], [lo[0], lo[1] - lo[0]]], alternative="greater").pvalue
def rising(seq):           # indices i with BLER(i) > BLER(i-1), exact in integers
    return [i for i in range(1, len(seq)) if seq[i][0] * seq[i - 1][1] > seq[i - 1][0] * seq[i][1]]
def cdt(ts): return datetime.fromtimestamp(ts, CDT)
def sh(c): return subprocess.run(c, shell=True, capture_output=True, text=True).stdout.strip()
def rd(p): return open(p, encoding="utf-8", errors="replace").read()

print(f"# recompute_fighspath.py  started {datetime.now(CDT):%Y-%m-%d %H:%M:%S %Z} (= {datetime.now(KST):%H:%M KST})  HEAD {sh('git rev-parse --short HEAD')}")

# ====================================================================== A. rows / registration
F = "TAG CELL PR BF CK SHA ROLE BS KK LL REF ORIG PICK FL ARMS".split()
script = rd("code/run_fighspath16e4.sh")
rows_txt = re.search(r"^ROWS='(.*?)'$", script, re.S | re.M)[1].split("\n")
ROWS = [dict(zip(F, l.split("|"))) for l in rows_txt]; TAGS = [r["TAG"] for r in ROWS]
chk("A1 ROWS: 3 rows FHSRPB16e4 / FHSPSRP / FHALDSRP, 15 fields; prior SRP, fits SRPB16e4, kron|4096|244.1932863626755 in all three; ckpt sha ac4699c78b3e2d80 role best (rows 1, 3), '-' (row 2); pick results/sparse/pick_SRP_C2.json:6ae22a15de019833; ORIG SRPB16e4 / SPSRP / ALDSRP; REF - / FHSRPB16e4 / FHSRPB16e4",
    TAGS == ["FHSRPB16e4", "FHSPSRP", "FHALDSRP"] and all(len(l.split("|")) == 15 for l in rows_txt) and all((r["PR"], r["BF"], r["BS"], r["KK"], r["LL"], r["CELL"]) == ("SRP", "SRPB16e4", "kron", "4096", LLV, "C2") for r in ROWS)
    and [(r["CK"], r["SHA"], r["ROLE"]) for r in ROWS] == [("ckpt/d2sx_SRP_N160000_a1_best.pt", "ac4699c78b3e2d80", "best"), ("-", "-", "-"), ("ckpt/d2sx_SRP_N160000_a1_best.pt", "ac4699c78b3e2d80", "best")]
    and [r["PICK"] for r in ROWS] == ["-", "results/sparse/pick_SRP_C2.json:6ae22a15de019833", "-"] and [r["ORIG"] for r in ROWS] == ["SRPB16e4", "SPSRP", "ALDSRP"] and [r["REF"] for r in ROWS] == ["-", "FHSRPB16e4", "FHSRPB16e4"]
    and ROWS[2]["FL"] == "--ald-file /home/HTJ/t2/conf/results/ald/ald_PILSRP_hisnr.npz", n=20)
reg = rd(REG).split("\n")
i6 = next(i for i, l in enumerate(reg) if l.startswith("## 6. "))
S6 = reg[i6:]
hunks = re.findall(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", sh(f"git diff {RUNC} {S6C} -- {REG}"), re.M)
old = sh(f"git show {RUNC}:./{REG}").split("\n")
j6 = next(i for i, l in enumerate(old) if l.startswith("## 6. "))
chk(f"A2 registration: git diff {RUNC} {S6C} = ONE hunk that starts in the 3 context lines above the '## 6.' header (old line {j6 + 1}); old §6 = header + placeholder only",
    len(hunks) == 1 and int(hunks[0][0]) >= j6 + 1 - 3 and old[j6:] in ([old[j6], "", "(실행 뒤 채운다.)"], [old[j6], "", "(실행 뒤 채운다.)", ""]),
    f"hunks {hunks}; old tail {old[j6:]}")
chk(f"A3 lines 1..§6 header-1 of the working-tree registration == committed {RUNC} (frozen 머리말 / §1 / §3 / §5); working tree == {S6C} (git diff empty)",
    old[:j6] == reg[:i6] and not sh(f"git diff {S6C} -- {REG}"), f"§6 header at line {i6 + 1}")
chk("A4 on disk: ckpt sha ac4699c78b3e2d80, pick sha 6ae22a15de019833, ALD test estimate ebb14a8952f0ae17, test pilots 8bfc83a43f790bbf, tune 858087f53952bcbf (§1); script sha e51214bd1b49a16d (§5) and unchanged since the run commit",
    sha("ckpt/d2sx_SRP_N160000_a1_best.pt")[:16] == "ac4699c78b3e2d80" and sha("results/sparse/pick_SRP_C2.json")[:16] == "6ae22a15de019833" and
    sha("results/ald/ald_PILSRP.npz")[:16] == "ebb14a8952f0ae17" and sha("results/ald/pilots_PILSRP_test.npz")[:16] == "8bfc83a43f790bbf" and
    sha("results/ald/tune_PILSRP.json")[:16] == "858087f53952bcbf" and sha("code/run_fighspath16e4.sh")[:16] == "e51214bd1b49a16d" and not sh(f"git diff {RUNC} HEAD -- code/run_fighspath16e4.sh"), n=6)
ALD_HS_SHA = sha("results/ald/ald_PILSRP_hisnr.npz")[:16]
TUNE = json.load(open("results/ald/tune_PILSRP.json"))
def _a5(z):
    tn = json.loads(str(z["tune"]))
    print(f"   ald_PILSRP_hisnr.npz: sha {ALD_HS_SHA}, prov.git {json.loads(str(z['prov']))['git']}, skip {int(z['skip'])}, hhat {z['hhat'].shape}, snrs {z['snrs'].tolist()}, tune c {tn.get('c')} beta {tn.get('beta')} (tune_PILSRP.json c {TUNE.get('c')} beta {TUNE.get('beta')}, dev_skip {TUNE.get('dev_skip')}, n_dev {TUNE.get('n_dev')})")
    return (ALD_HS_SHA == "3a13dfb7191bd3ed" and json.loads(str(z["prov"]))["git"] == RUNC and int(z["skip"]) == 10000 and z["hhat"].shape == (4, N2, 32)
            and z["snrs"].tolist() == list(SN) and tn.get("c") == TUNE.get("c") and tn.get("beta") == TUNE.get("beta"))
chk("A5 new-trial ALD estimate ald_PILSRP_hisnr.npz sha256[:16] = 3a13dfb7191bd3ed (§6.4), prov git c48ee796, skip 10000, hhat (4, 20480, 32), snrs 6/9/12/15, tune (c, beta) = tune_PILSRP.json",
    _a5(np.load("results/ald/ald_PILSRP_hisnr.npz")), ALD_HS_SHA, n=7)

# ====================================================================== B. new raws
PICK = json.load(open("results/sparse/pick_SRP_C2.json"))
MKEYS = ("ntrain", "bstar", "kron_K", "ll_val|kron", "stagec_ckpt_id", "sparse", "rotation", "ald_file")
def scan(path):
    b = os.path.basename(path); m = PAT.match(b)
    o = {"file": b, "mtime": os.stat(path).st_mtime, "name": (m[1], m[2], float(m[7]), int(m[8]), int(m[9]), m[6]) if m else None, "arms": {}, "meta": {}, "err": None}
    try:
        with np.load(path) as z:
            fs = set(z.files)
            o["git"] = str(z["run|git"]) if "run|git" in fs else None
            o["run"] = (float(z["run|snr"]), int(z["run|skip"]), int(z["run|n"]), int(z["run|iters"]), int(z["run|seed"]))
            for k in MKEYS:
                if f"meta|{k}" in fs:
                    v = z[f"meta|{k}"]; o["meta"][k] = str(v.item() if v.ndim == 0 else v)
            arms = sorted({k.split("|")[0] for k in fs if "|" in k and not k.startswith(("meta|", "run|"))})
            for a in arms:
                if f"{a}|blk_err" not in fs: continue
                be = np.asarray(z[f"{a}|blk_err"], float); last, first = be[:, -1], be[:, 0]; nf = ~np.isfinite(last)
                o["arms"][a] = (int(np.where(nf, 1.0, last).sum()), int(np.where(np.isfinite(first), first, 1.0).sum()), be.shape, int(nf.sum()),
                                int(z[f"{a}|failed"].sum()) if f"{a}|failed" in fs else 0, f"{a}|failed" in fs, int((~np.isfinite(be)).sum()))
    except Exception as e:
        o["err"] = repr(e)
    return o
print("\n# B. scanning the 3 new raws (single process) ...")
BY = {t: [scan(p) for p in sorted(glob.glob(f"raw_{t}/D2_*.npz"))] for t in TAGS}
chk("B0 every new chunk readable; each raw dir holds only D2_*.npz chunk files (2048)", not [o for t in TAGS for o in BY[t] if o["err"]] and all(len(os.listdir(f"raw_{t}")) == 2048 == len(BY[t]) for t in TAGS),
    str({t: len(os.listdir(f"raw_{t}")) for t in TAGS}), n=3)
PLAN = {(s, 10000 + 40 * k, 40) for s in SN for k in range(512)}
COUNTS, COUNTS1, MT = {}, {}, {}
bad_plan, bad_git, bad_meta, bad_shape, bad_raised = [], [], [], [], []
for r in ROWS:
    t = r["TAG"]; L = BY[t]
    plan = [(o["name"][2], o["name"][3], o["name"][4]) for o in L]
    if len(L) != 2048 or set(plan) != PLAN or len(set(plan)) != 2048 or any(o["run"][:3] != p for o, p in zip(L, plan)): bad_plan.append(t)
    if {o["name"][0] for o in L} != {"C2"} or {o["name"][1] for o in L} != {"SRP"} or {o["name"][5] for o in L} != {"dft"}: bad_plan.append((t, "cell/prior/pilot"))
    if {o["git"] for o in L} != {RUNC} or {o["run"][3] for o in L} != {16} or {o["run"][4] for o in L} != {20260926}: bad_git.append((t, {o["git"] for o in L}))
    for o in L:
        mt = o["meta"]
        if mt.get("ntrain") != "160000.0" or mt.get("bstar") != "kron" or mt.get("kron_K") != "4096" or mt.get("ll_val|kron") != LLV: bad_meta.append((t, o["file"], "ntrain/bstar/kron_K/ll", mt)); break
        cid = mt.get("stagec_ckpt_id")
        if r["CK"] == "-":
            if cid is not None: bad_meta.append((t, o["file"], "SP row has stagec_ckpt_id")); break
        elif cid != CKID: bad_meta.append((t, o["file"], "ckpt id", cid)); break
        if r["PICK"] != "-":
            e = PICK["per_snr"][str(int(o["name"][2]))]
            if json.loads(mt.get("sparse", "null")) != dict(rho_sbl=PICK["rho_sbl"], rho_omp=PICK["rho_omp"], n_em=e["n_em"], L=e["L"]): bad_meta.append((t, o["file"], "sparse", mt.get("sparse"))); break
        elif "sparse" in mt: bad_meta.append((t, o["file"], "unexpected meta|sparse")); break
        if "rotation" in mt: bad_meta.append((t, o["file"], "unexpected meta|rotation")); break
        if "--ald-file" in r["FL"]:
            if mt.get("ald_file") != f"/home/HTJ/t2/conf/results/ald/ald_PILSRP_hisnr.npz sha256[:16]={ALD_HS_SHA}": bad_meta.append((t, o["file"], "ald_file", mt.get("ald_file"))); break
        elif "ald_file" in mt: bad_meta.append((t, o["file"], "unexpected meta|ald_file")); break
    arms = set(r["ARMS"].split())
    if any(set(o["arms"]) != arms for o in L): bad_shape.append((t, "arm set", sorted({a for o in L for a in o["arms"]})))
    if any(v[2] != (40, 16) for o in L for v in o["arms"].values()): bad_shape.append((t, "shape"))
    if any(v[3] or v[4] or v[5] or v[6] for o in L for v in o["arms"].values()): bad_raised.append(t)
    c = {a: {s: 0 for s in SN} for a in arms}; c1 = {s: 0 for s in SN}
    for o in L:
        for a, v in o["arms"].items():
            c[a][o["name"][2]] += v[0]
            if a == "R0-pilot": c1[o["name"][2]] += v[1]
    COUNTS[t] = c; COUNTS1[t] = c1 if "R0-pilot" in arms else None
    MT[t] = (min(o["mtime"] for o in L), max(o["mtime"] for o in L))
chk("B1 trial plan: 3 tags x 2048 chunks = 4 SNR x skip 10000..30440 step 40 (each once = trials 10000..30479), n 40; run|snr/skip/n = file name; cell C2 prior SRP, '_dft_' names", not bad_plan, str(bad_plan), n=3 * 2048)
chk("B2 run|git == 'c48ee796' (no +dirty), run|iters 16, run|seed 20260926 in every chunk", not bad_git, str(bad_git), n=3 * 2048)
chk("B3 meta: ntrain 160000 / bstar kron / kron_K 4096 / ll_val|kron 244.1932863626755 / stagec_ckpt_id (sha ac4699c78b3e2d80 epoch 694 role best; absent in SP) / meta|sparse == pick per SNR (SP only) / no rotation / meta|ald_file == path + sha (ALD only), every chunk",
    not bad_meta, str(bad_meta[:3]), n=3 * 2048)
chk("B4 arm set of every chunk = the row's; blk_err shape (40, 16)", not bad_shape, str(bad_shape[:3]))
chk("B5 raised trials 0: no |failed| key, no non-finite blk_err (any iteration) in any chunk of the 3 raws", not bad_raised, str(bad_raised))
bad = []; ncmp = 0
for t in ("FHSPSRP", "FHALDSRP"):
    for o in BY[t]:
        with np.load(f"raw_{t}/{o['file']}") as z, np.load(f"raw_FHSRPB16e4/{o['file']}") as y:
            for q in KEYS_RAW + ("guardH",):
                k = f"R5-genie|{q}"; ncmp += 1
                if k not in z.files or k not in y.files or z[k].shape != y[k].shape or not np.array_equal(z[k], y[k], equal_nan=True): bad.append((t, o["file"], k))
NARR = ncmp
chk(f"B6 R5-genie bit-identical across the three FH raws: FHSPSRP / FHALDSRP vs FHSRPB16e4, every chunk x KEYS_RAW 7 + guardH ({ncmp} arrays)", not bad, str(bad[:3]), n=0)
print("   genie failures per SNR: " + " · ".join(f"{t} {[COUNTS[t]['R5-genie'][s] for s in SN]}" for t in TAGS))

# ====================================================================== C. original raws
print("\n# C. scanning the 3 original raws ...")
OB = {o: [scan(p) for p in sorted(glob.glob(f"raw_{o}/D2_*.npz"))] for o in ("SRPB16e4", "SPSRP", "ALDSRP")}
OC, OC1 = {}, {}
bad = []
for o, L in OB.items():
    if [x for x in L if x["err"]]: bad.append((o, "unreadable"))
    plan = {}
    for x in L: plan.setdefault(x["name"][2], []).append((x["name"][3], x["name"][4]))
    if len(L) != 448 or set(plan) != set(ALL) or any(sorted(v) != [(40 * k, 40) for k in range(64)] for v in plan.values()): bad.append((o, len(L)))
    c, c1 = {}, {s: [0, 0] for s in ALL}
    for x in L:
        for a, v in x["arms"].items():
            d = c.setdefault(a, {}).setdefault(x["name"][2], [0, 0, 0]); d[0] += v[0]; d[1] += v[2][0]; d[2] += v[3]
            if a == "R0-pilot": c1[x["name"][2]][0] += v[1]; c1[x["name"][2]][1] += v[2][0]
    OC[o] = {a: {s: (v[0], v[1]) for s, v in d.items()} for a, d in c.items()}; OC1[o] = {s: tuple(v) for s, v in c1.items()}
    if any(v[1] != N1 for d in c.values() for v in d.values()): bad.append((o, "n != 2560"))
    if any(v[2] for d in c.values() for v in d.values()): bad.append((o, "non-finite"))
    print(f"   raw_{o}: {len(L)} chunks, run|git {sorted({x['git'] for x in L})}, max skip {max(x['name'][3] for x in L)}")
chk("C1 original raws SRPB16e4 / SPSRP / ALDSRP: 448 chunks = 7 SNR x skip 0..2520 step 40 (max skip 2520, as the 머리말 says), n 2560, no non-finite; run|git one value per raw (SRPB16e4 99039ef5)",
    not bad and all(len({x["git"] for x in L}) == 1 for L in OB.values()) and {x["git"] for x in OB["SRPB16e4"]} == {"99039ef5"}, str(bad), n=3 * 448)
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
    if names != sorted(f"D2_C2_SRP_Nr8_T16_Tp4_dft_snr{int(s)}_skip0_n40.npz" for s in SN): b.append(("names", names))
    for f in fs:
        with np.load(f) as z, np.load(f"raw_{r['ORIG']}/{os.path.basename(f)}") as y:
            if str(z["run|git"]) != RUNC: b.append((f, "git", str(z["run|git"])))
            for a in arms:
                for q in KEYS_RAW:
                    k = f"{a}|{q}"; n += 1
                    if k not in z.files or k not in y.files or z[k].shape != y[k].shape or not np.array_equal(z[k], y[k], equal_nan=True): b.append((os.path.basename(f), k))
    tot += n
    txt = rd(f"{RV}/{c}_control.txt")
    m = re.search(r"(\d+) chunk files \(expected (\d+)\).*?(\d+) \(chunk, arm, key\) comparisons, (\d+) differ", txt)
    if len(fs) != 4 or b or not m or (int(m[1]), int(m[2]), int(m[3]), int(m[4])) != (4, 4, n, 0) or txt.rstrip().split("\n")[-1] != "CONTROL: OK": bad.append((c, len(fs), n, b[:2], m and m.groups()))
    print(f"   {c}: {len(fs)} chunks, {n} (chunk, arm, key) comparisons, {len(b)} differ (file says {m and m.groups()})")
chk("D1 receiver controls: raw_FHC* (4 chunks, trials 0..39 at +6..+15 dB, run|git c48ee796) vs the original raws, every arm x KEYS_RAW bit-identical (NaN = NaN); counts = *_control.txt (196 / 112 / 56); CONTROL: OK",
    not bad and tot == 196 + 112 + 56, str(bad[:3]), n=6)
NARR += tot
A, Bn = np.load("results/ald/ald_FHCALDSRP.npz"), np.load("results/ald/ald_PILSRP.npz")
same = all(A[k].shape == Bn[k].shape and np.array_equal(A[k], Bn[k]) for k in ("hhat", "b", "v"))
txt = rd(f"{RV}/FHCALDSRP_aldcontrol.txt")
chk("D2 ALD estimator control: ald_FHCALDSRP.npz hhat (7, 2560, 32) / b / v bit-identical to ald_PILSRP.npz; file says max|diff| 0, CONTROL-ALD: OK",
    same and A["hhat"].shape == (7, 2560, 32) and "max|diff| 0," in txt and txt.rstrip().endswith("CONTROL-ALD: OK"), n=3)
NARR += 3
chk("D3 FHC copies of the frozen ALD records = the originals (tune json, dev / test pilots sha)",
    all(sha(f"results/ald/{x}_FHCALDSRP{y}") == sha(f"results/ald/{x}_PILSRP{y}") for x, y in (("tune", ".json"), ("pilots", "_dev.npz"), ("pilots", "_test.npz"))), n=3)

# ====================================================================== E. count tables + §6.2
print("\n# E. count tables / §6.2")
TAB = {}; bad, bad_w, nrow, heads = [], [], 0, []
for r in ROWS:
    t = r["TAG"]; tb = {}
    for l in open(f"{RV}/fighs_{t}.txt", encoding="utf-8"):
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
chk(f"E1 count tables: every (SNR, arm) failures / n = own recount ({nrow} rows incl. R0-pilot@1 = iteration 1); 32 + 16 + 8 rows", not bad and nrow == 56, str(bad[:4]), n=2 * nrow)
chk(f"E2 count tables: BLER / Wilson strings (%.2e, z 1.959964) re-formatted from own Wilson ({nrow} rows)", not bad_w, str(bad_w[:3]), n=3 * nrow)
chk("E3 count-table headers = §6.1 '집계표 머리말' lines (3), name run_fighspath16e4 git c48ee796 / FIGHSPATH16e4 §1, and say load_raw warnings 0",
    [f"- `{h}`" for h in heads] == [l for l in S6 if l.startswith("- `# run_fighspath16e4")] and len(heads) == 3 and
    heads == [f"# run_fighspath16e4 git {RUNC} raw_{t} C2: failures@16 / n, BLER, 95% Wilson -- REPORT-ONLY (FIGHSPATH16e4 §1); load_raw warnings 0" for t in TAGS], n=3)
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
rows62 = [m[1] for l in S6 for m in [re.match(r"^\| (\S+) \| raw_FH", l)] if m]
chk(f"E4 §6.2 table: 11 curves (legend order) x 4 SNR k / BLER / Wilson from the new raws ({n62} cells) + source raw + '원 raw k / 2560' column from the original raws",
    not bad and n62 == 44 and rows62 == ORDER, str(bad[:4]), n=4 * 44 + 11 + 44)
g = {t: [COUNTS[t]["R5-genie"][s] for s in SN] for t in TAGS}
chk("E5 §6.2 genie line: 'FHSRPB16e4 [14, 1, 1, 0] · FHSPSRP [14, 1, 1, 0] · FHALDSRP [14, 1, 1, 0] → 동일'",
    any(l.startswith("Perfect CSI (R5-genie) 의 실패 수는 세 raw 에서 같다: " + " · ".join(f"{t} {v}" for t, v in g.items()) + " → 동일.") for l in S6) and len({tuple(v) for v in g.values()}) == 1 and g["FHSRPB16e4"] == [14, 1, 1, 0], n=12)
zero = [f"{a} {s:+.0f} dB" for a in ORDER for s in SN if ncount(a, SRC[a][0], s) == 0]
chk("E6 §6.2 '0 실패 점 (n = 20480): M-ours-dscore-C-V1 +12 dB, M-ours-dscore-C-V1 +15 dB, R5-genie +15 dB.' = recount",
    zero == ["M-ours-dscore-C-V1 +12 dB", "M-ours-dscore-C-V1 +15 dB", "R5-genie +15 dB"] and f"0 실패 점 (n = 20480): {', '.join(zero)}." in S6, str(zero), n=3)
mine = {}
for a in ORDER:
    seq = MERGED[a]
    up = [f"{ALL[i - 1]:+.0f}->{ALL[i]:+.0f} dB p={fisher_p(seq[i], seq[i - 1]):.2g}" for i in rising(seq)]
    mine[a] = (f"    {a:<20}@16  " + " ".join(f"{k}/{n}" for k, n in seq[3:]) + f"   (raw_{SRC[a][0]})" + (f"   rising: {'; '.join(up)}" if up else ""))
rec = rd(f"{REC}/paper_f21srphs.txt").split("\n")
blk = [l for l in rec if re.match(r"^    \S+\s+@16  ", l)]
chk("G1 figure record paper_f21srphs.txt merge block: 11 lines, k/n at +6..+15 = new raws, source tag, 'rising' cells + one-sided Fisher p (%.2g) over the 7 merged points — byte-identical to own",
    blk == [mine[a] for a in ORDER], f"diff {[(x, y) for x, y in zip(blk, [mine[a] for a in ORDER]) if x != y][:2]}", n=11 * 5)
ris = [l.strip() for l in blk if "rising:" in l]
chk("E7 §6.2 'rising' line (1) = the figure record's rising line = own (R3-bigamp +9->+12 dB p=9e-06); '1 줄'",
    [l[3:-1] for l in S6 if l.startswith("- `") and "rising:" in l] == ris == [mine[a].strip() for a in ORDER if "rising:" in mine[a]] and len(ris) == 1 and
    any("오르는 칸" in l and ": 1 줄." in l for l in S6) and ris[0].endswith("rising: +9->+12 dB p=9e-06"), str(ris), n=3)
allr = {a: [(f"{ALL[i-1]:+.0f}->{ALL[i]:+.0f}", f"{fisher_p(MERGED[a][i], MERGED[a][i-1]):.3g}") for i in rising(MERGED[a])] for a in ORDER if rising(MERGED[a])}
print("   all rising cells of the 11 merged curves (incl. +3->+6): " + str(allr))
print("   ties (equal BLER in adjacent cells, not 'rising'): " + str({a: [f"{ALL[i-1]:+.0f}->{ALL[i]:+.0f}" for i in range(1, 7) if MERGED[a][i][0] * MERGED[a][i-1][1] == MERGED[a][i-1][0] * MERGED[a][i][1]] for a in ORDER
                                                                      if any(MERGED[a][i][0] * MERGED[a][i-1][1] == MERGED[a][i-1][0] * MERGED[a][i][1] for i in range(1, 7))}))

# ====================================================================== F. §6.3 predictions
print("\n# F. §6.3 predictions (scored by me against the frozen §3 wording)")
V = [ncount("M-ours-dscore-C-V1", "FHSRPB16e4", s) for s in SN]; B = [ncount("M-ours-bstar", "FHSRPB16e4", s) for s in SN]
p2 = {a: [fisher_p(MERGED[a][i], MERGED[a][i - 1]) for i in rising(MERGED[a])] for a in ("M-ours-dscore-C-V1", "M-ours-bstar", "R5-genie")}
LOGALL = rd("logs/run_fighspath16e4.log").split("\n")
LOG = [l for l in LOGALL if l.startswith("[fighs ")]
done = [l for l in LOG if "FIGHS_DONE" in l]
sc = {"1": V[0] >= V[1] >= V[2] >= V[3], "2": all(p >= 0.05 for v in p2.values() for p in v), "3": V[0] <= B[0] and V[1] <= B[1], "4a": V[1] >= 1, "4b": V[3] <= 5,
      "5": len(done) == 1 and done[0].endswith("FIGHS_DONE ok=3 fail=0")}
got = {m[1]: m[2] for l in S6 for m in [re.match(r"^(\d[ab]?)\. .*→ \*\*(적중|빗나감)\*\*", l)] if m}
chk("F1 §6.3: six predictions (1, 2, 3, 4a, 4b, 5) all '적중' and my own scoring agrees (1: 45 >= 7 >= 0 >= 0; 2: no rising cell on V1 / b* / genie incl. +3->+6; 3: 45<=202, 7<=33; 4a: 7 >= 1; 4b: 0 <= 5; 5: ok=3 fail=0)",
    got == {i: "적중" for i in ("1", "2", "3", "4a", "4b", "5")} and all(sc.values()), f"V {V}, b* {B}, p2 {p2}, got {got}, own {sc}", n=6)
chk("F2 §6.3 quoted numbers: 1 (45 / 7 / 0 / 0); 2 'M-ours-dscore-C-V1 없음, M-ours-bstar 없음, R5-genie 없음'; 3 (45 대 202, 7 대 33); 4a (7); 4b (0); 5 (ok=3 fail=0)",
    any(l.startswith("1. ") and "(45 / 7 / 0 / 0)." in l for l in S6) and any("M-ours-dscore-C-V1 없음, M-ours-bstar 없음, R5-genie 없음" in l for l in S6) and any("(45 대 202, 7 대 33)" in l for l in S6) and
    any(l.startswith("4a. ") and l.endswith("(7).") for l in S6) and any(l.startswith("4b. ") and l.endswith("(0).") for l in S6) and any(l.startswith("5. ") and l.endswith("(ok=3 fail=0).") for l in S6)
    and V == [45, 7, 0, 0] and B == [202, 33, 3, 1] and not any(p2.values()), n=10)
s3 = "\n".join(reg[next(i for i, l in enumerate(reg) if l.startswith("## 3. ")):next(i for i, l in enumerate(reg) if l.startswith("## 5. "))])
chk("F3 the §6.3 paraphrases keep the §3 wording's content (1 '+6 ≥ +9 ≥ +12 ≥ +15 dB 로 줄기만'; 2 'Fisher p < 0.05 인 \"오르는 칸\" 이 없다(+3 → +6 dB 칸 포함)'; 3 '+6 dB 와 +9 dB 에서 실패 수 V1 ≤ b\\*'; 4a '≥ 1 / 20480'; 4b '≤ 5 / 20480'; 5 FIGHS_DONE ok=3 fail=0)",
    all(x in s3 for x in ("+6 ≥ +9 ≥ +12 ≥ +15 dB 로 줄기만 한다", "Fisher p < 0.05 인 \"오르는 칸\" 이 없다(+3 → +6 dB 칸 포함)", "+6 dB 와 +9 dB 에서 실패 수 V1 ≤ b\\*", "V1 의 +9 dB 실패 수 ≥ 1 / 20480", "V1 의 +15 dB 실패 수 ≤ 5 / 20480", "`FIGHS_DONE ok=3 fail=0`")))

# ====================================================================== G. figure records
print("\n# G. figure records")
def cblock(lines):
    c = {}
    for l in lines[lines.index("Counts:") + 1:]:
        f = l.split()
        if not f: break
        if f[0] in ORDER: c[f[0]] = ([tuple(int(x) for x in v.split("/")) for v in f[1:8]], f[8])
    return c
cnt = cblock(rec)
chk("G2 paper_f21srphs.txt 'Counts:' block = merged (−3/0/+3 original n 2560, +6..+15 new n 20480) for the 11 curves; source = original raw",
    all(cnt[a][0] == MERGED[a] and cnt[a][1] == f"raw_{SRC[a][1]}" for a in ORDER) and len(cnt) == 11, n=77 + 11)
rec0 = rd(f"{REC}/paper_f21srp.txt").split("\n"); cnt0 = cblock(rec0)
chk("G3 paper_f21srp.txt (original figure record, n 2560 at 7 SNRs) 'Counts:' = own recount of the original raws (11 x 7)", all(cnt0[a][0] == ORIG7[a] for a in ORDER) and len(cnt0) == 11, n=77)
zl = [l for l in rec if l.startswith("Zero-failure points")]
zown = "; ".join(f"{LABEL[a]} {s:+.0f} dB" for a in ORDER for s, (k, n) in zip(ALL, MERGED[a]) if k == 0)
chk("G4 merged record zero-failure line = own: 'Proposed (diffusion prior) +12 dB; Proposed (diffusion prior) +15 dB; Perfect CSI +15 dB.'; §6.4 quotes the same three; record's arm -> figure-name map = LABEL",
    len(zl) == 1 and zl[0] == "Zero-failure points (the curve breaks there; Perfect CSI: fighs_merge.zero_arrows): " + zown + "." and
    zown == "Proposed (diffusion prior) +12 dB; Proposed (diffusion prior) +15 dB; Perfect CSI +15 dB" and any(zown + "." in l for l in S6 if l.startswith("- **그림**")) and
    any(l == "Curves (internal arm -> figure name): " + "; ".join(f"{a} -> {LABEL[a]}" for a in ORDER) + "." for l in rec), zown, n=3 + 11)
zero0 = [f"{a} {s:+.0f}" for a in ORDER for s, (k, n) in zip(ALL, ORIG7[a]) if k == 0]
print(f"   original (n = 2560) zero-failure points, own: {zero0}")
z0l = [l for l in rec0 if l.startswith("Zero-failure points")]
z0own = "; ".join(f"{LABEL[a]} {s:+.0f} dB" for a in ORDER for s, (k, n) in zip(ALL, ORIG7[a]) if k == 0)
chk("G4b original record paper_f21srp.txt zero-failure line = own recount of the original raws", len(z0l) == 1 and z0l[0].endswith(": " + z0own + "."), z0l[0][-200:] if z0l else "no line", n=len(zero0))
below = [(a, ALL[i]) for a in ORDER if a not in ("M-ours-dscore-C-V1", "R5-genie") for i, ((k, _), (kv, _)) in enumerate(zip(MERGED[a], MERGED["M-ours-dscore-C-V1"])) if k <= kv]
chk("G5 merged record 'at or below the proposed curve: none' = own (no drawn baseline point <= V1's count at any of the 7 merged points; same n per SNR on both curves)",
    not below and any(l.endswith("pairB_SPSRP.txt: none.") for l in rec), str(below), n=63)
pos = {(a, s): (wilson(k, n)[0] if a in BARS else k / n) for a in ORDER for s, (k, n) in zip(ALL, MERGED[a]) if k > 0}
haszero = any(k == 0 for a in ORDER for k, n in MERGED[a])
ylim = "(0.0002, 1.2)" if (not haszero and min(pos.values()) > 2e-4) else "(3e-05, 1.2)"
pts = {(a, s): k / n for a in ORDER for s, (k, n) in zip(ALL, MERGED[a]) if k > 0}
chk("G6 y-range rule (paper_f21dmc.py ROOM branch) on the drawn (merged) values -> (3e-05, 1.2) [a zero-failure point exists]; record 'y log (3e-05, 1.2)' and §6.4 'y 축 (3e-05, 1.2)'; every drawn point k/n within (3e-05, 1.2)",
    ylim == "(3e-05, 1.2)" and any("y log (3e-05, 1.2)" in l for l in rec) and any("y 축 (3e-05, 1.2)" in l for l in S6) and min(pts.values()) >= 3e-5 and max(pts.values()) <= 1.2,
    f"zero point {haszero}; min drawn point {min(pts.values()):.3g}; drawn values (Wilson lower for bar curves) <= 2e-4: {sorted((a, s, f'{v:.3g}') for (a, s), v in pos.items() if v <= 2e-4)}", n=3)
print("   point estimates k/n at or below 2e-4 (any arm): " + "; ".join(f"{a} {s:+.0f} dB {k}/{n}={k/n:.3g}" for a in ORDER for s, (k, n) in zip(ALL, MERGED[a]) if 0 < k / n <= 2e-4))
print(f"   Perfect CSI zero-failure arrow at +15 dB: cap {1.96 ** 2 / (N2 + 1.96 ** 2):.3g}, tip {1.96 ** 2 / (N2 + 1.96 ** 2) / 1.7:.3g}")
FIGT = {f: cdt(os.stat(f"../conference/figures/{f}").st_mtime) for f in ("F21srphs_col.pdf", "F21srphs_col.png", "records/paper_f21srphs.txt", "F21srp_col.pdf", "records/paper_f21srp.txt", "F21srbhs_col.pdf", "records/paper_f21srbhs.txt", "paper_f21dmc.py", "fighs_merge.py")}
chk("G8 figure files F21srphs_col.{pdf,png} + record mtime after FIGHS_DONE (20:36 CDT, log mtime 20:36:54) and not after the registration mtime; F21srp_col + its record untouched since 10-11 16:43 / 15:22 CDT",
    all(cdt(os.stat("logs/run_fighspath16e4.log").st_mtime) < FIGT[f] <= cdt(os.stat(REG).st_mtime) for f in ("F21srphs_col.pdf", "F21srphs_col.png", "records/paper_f21srphs.txt")) and
    f"{FIGT['F21srp_col.pdf']:%m-%d %H:%M}" == "10-11 16:43" and f"{FIGT['records/paper_f21srp.txt']:%m-%d %H:%M}" == "10-11 15:22",
    " ".join(f"{f} {t:%H:%M:%S}" for f, t in FIGT.items()), n=5)
chk("G9 figure record wording: REPORT-ONLY, names NEXT_EXPERIMENTS_FIGHSPATH16e4 §1 (twice), 'counts before the merge (n = 2560, the registered judgement)' (the FIGHSROOM N2 fix), no GMM seed-initialisation caveat in the record (INFO -> finding)",
    sum("NEXT_EXPERIMENTS_FIGHSPATH16e4 §1" in l for l in rec) == 2 and any("FIGHSPATH16e4 merge (REPORT-ONLY" in l for l in rec) and any("Asserts passed: counts before the merge (n = 2560, the registered judgement) = pairB_SPSRP.txt" in l for l in rec),
    f"caveat words in record: {[w for w in ('seed', 'initiali', 'collapsed', 'it_best') if any(w in l for l in rec)]}")

# ====================================================================== H. run log, runner logs, manifests, mtimes, git
print("\n# H. logs / timeline")
def tsl(l):
    m = re.match(r"\[fighs (\d\d)-(\d\d) (\d\d):(\d\d) CDT\]", l)
    return datetime(2026, int(m[1]), int(m[2]), int(m[3]), int(m[4]), tzinfo=CDT) if m else None
starts = [l for l in LOG if "start (git" in l]
chk("H1 run log: ONE start line '[fighs 10-11 18:34 CDT] start (git c48ee796) rows: all resume=0 skip0 10000 n 20480 SNR 6 9 12 15'; no resume line",
    starts == ["[fighs 10-11 18:34 CDT] start (git c48ee796) rows: all resume=0 skip0 10000 n 20480 SNR 6 9 12 15"] and not any("resume:" in l for l in LOGALL), n=3)
nbad = [l for l in LOG if re.search(r"ABORT|INVALID|SKIP|FAILED|failed|rc=[1-9]", l)]
chk("H2 phase C line '[fighs 10-11 18:38 CDT] phase C done: 3 receiver control(s) OK, 1 ALD estimator control(s) OK'; FIGHS_DONE ok=3 fail=0 at 10-11 20:36 CDT = last line; ABORT/SKIP/INVALID/FAILED/rc!=0 lines 0 (§6.1 '0 개')",
    "[fighs 10-11 18:38 CDT] phase C done: 3 receiver control(s) OK, 1 ALD estimator control(s) OK" in LOG and LOG[-1] == "[fighs 10-11 20:36 CDT] FIGHS_DONE ok=3 fail=0" and not nbad and
    any("단계 C (관측된 시험 청크 0 의 대조) 10-11 18:38 CDT: 3 receiver control(s) OK, 1 ALD estimator control(s) OK. `FIGHS_DONE ok=3 fail=0` 10-11 20:36 CDT. ABORT · SKIP · INVALID 줄: 0 개." in l for l in S6) and
    any(l.startswith("`bash code/run_fighspath16e4.sh` **한 번**, tmux `fighspath`, 10-11 18:34 CDT 시작(git c48ee796 = 실행 커밋; 시작 줄 하나, 재개 없음).") for l in S6), str(nbad), n=6)
RUN = {m[1]: tsl(l) for l in LOG for m in [re.match(r"\[fighs [^\]]+\] (FH\w+) run:", l)] if m}
ACC = {m[1]: (tsl(l), int(m[2]), m[3].strip()) for l in LOG for m in [re.match(r"\[fighs [^\]]+\] (FH\w+) acceptance rc=(\d+) \((.*)\)", l)] if m}
chk("H3 run / acceptance lines: FHSRPB16e4 18:38 / 19:52, FHSPSRP 19:52 / 20:30, FHALDSRP 20:34 / 20:36, rc 0, 'ACCEPT: OK -- <tag> ACCEPT (f): OK'",
    [(t, f"{RUN[t]:%H:%M}", f"{ACC[t][0]:%H:%M}", ACC[t][1], ACC[t][2]) for t in TAGS] ==
    [("FHSRPB16e4", "18:38", "19:52", 0, "ACCEPT: OK -- FHSRPB16e4 ACCEPT (f): OK"), ("FHSPSRP", "19:52", "20:30", 0, "ACCEPT: OK -- FHSPSRP ACCEPT (f): OK"), ("FHALDSRP", "20:34", "20:36", 0, "ACCEPT: OK -- FHALDSRP ACCEPT (f): OK")], n=12)
chk("H4 ALD lines: estimator control on GPU 1 at 18:34; new-trial regen + estimate on GPU 1 at 20:30 'rotation none'; '[ald regen] PILSRP hisnr: 4 SNR x 20480 trials (skip 10000)'",
    "[fighs 10-11 18:34 CDT] FHALDSRP ALD estimator control: ald.py estimate --tag FHCALDSRP --set test on GPU 1 (copies of the frozen records of PILSRP)" in LOG and
    "[fighs 10-11 20:30 CDT] FHALDSRP ALD PILSRP: regen (CPU) + estimate (GPU 1) on trials 10000.., rotation none (tune record results/ald/tune_PILSRP.json)" in LOG and
    any(l.startswith("[ald regen] PILSRP hisnr: 4 SNR x 20480 trials (skip 10000) rotation=None doppler=None") for l in LOGALL), n=3)
runl = [l for l in LOG if " run: " in l]
want_run = {"FHSRPB16e4": "--testbed D2 --prior SRP --cell C2 --chunk 40 --ntrain 160000 --stagec-ckpt /home/HTJ/t2/conf/ckpt/d2sx_SRP_N160000_a1_best.pt  --snr 6 9 12 15 --n 20480 --skip0 10000 --arm R0-pilot R1-turbo R2-ours-G R3-bigamp M-ours-bstar M-ours-dscore-C-V1 R5-genie",
            "FHSPSRP": "--testbed D2 --prior SRP --cell C2 --chunk 40 --ntrain 160000 --sparse-file results/sparse/pick_SRP_C2.json  --snr 6 9 12 15 --n 20480 --skip0 10000 --arm SBL-loop SBL-pilot OMP-pilot R5-genie",
            "FHALDSRP": "--testbed D2 --prior SRP --cell C2 --chunk 40 --ntrain 160000 --stagec-ckpt /home/HTJ/t2/conf/ckpt/d2sx_SRP_N160000_a1_best.pt --ald-file /home/HTJ/t2/conf/results/ald/ald_PILSRP_hisnr.npz --snr 6 9 12 15 --n 20480 --skip0 10000 --arm ALD-pilot R5-genie"}
chk("H4b the three 'run:' lines carry exactly the §1 runner flags (prior SRP, C2, chunk 40, ntrain 160000, ckpt / pick / ald-file, SNR 6 9 12 15, n 20480, skip0 10000, the row's arms)",
    [l.split(" run: ")[1] for l in runl] == [want_run[t] for t in TAGS], n=3)
bad = []; rows61 = {}
for l in S6:
    m = re.match(r"^\| (FH\w+) \| 10-11 (\d\d:\d\d) \| (\S+) 분 · (\d+) 작업 · (\d+) 워커 \| (\d+) / (\d+) \| 10-11 (\d\d:\d\d) \| (.*?) \| (\w+) · (\w+) \| (.*?) \|$", l)
    if m: rows61[m[1]] = m.groups()
RMIN = {}
for t in TAGS:
    rl = rd(f"logs/run_D2_{t}.log").split("\n")
    hd = [l for l in rl if l.startswith("# run_fighs")]
    mins = re.findall(r"\[run\] finished in ([\d.]+) min", "\n".join(rl)); tasks = re.findall(r"-> (\d+) tasks on (\d+) workers", "\n".join(rl))
    nd, ne = sum(bool(re.match(r"\d+/\d+ done ", l)) for l in rl), sum(bool(re.match(r"\d+/\d+ exists", l)) for l in rl)
    dn = {m[1] for l in rl for m in [re.match(r"\d+/\d+ done\s+(\S+\.npz)", l)] if m}
    af = rd(f"{RV}/{t}_accept.txt"); v = "; ".join(x.strip() for x in af.split("\n") if x.startswith("ACCEPT"))
    man = json.load(open(f"{RV}/run_manifest_{t}.json"))
    ctl = rd(f"{RV}/{t.replace('FH', 'FHC', 1)}_control.txt").strip().split("\n")[-1]
    if t == "FHALDSRP": ctl += " · " + rd(f"{RV}/FHCALDSRP_aldcontrol.txt").strip().split("\n")[-1]
    RMIN[t] = mins[0] if mins else None
    want = (t, f"{RUN[t]:%H:%M}", mins[0], tasks[0][0], tasks[0][1], str(nd), str(ne), f"{ACC[t][0]:%H:%M}", f"rc={ACC[t][1]}; {v}", man["git_commit"], man["config_hash"], ctl)
    if rows61.get(t) != want: bad.append((t, rows61.get(t), want))
    if hd != [f"# run_fighspath16e4 git {RUNC} 2026-10-11 {RUN[t]:%H:%M} CDT resume=0"] or len(mins) != 1 or nd != 2048 or ne != 0 or tasks != [("2048", "192")] or dn != {o["file"] for o in BY[t]}: bad.append((t, "runner log", hd, mins, nd, ne, tasks, len(dn)))
    if re.search(r"Traceback|Error", "\n".join(rl)): bad.append((t, "Traceback/Error in runner log"))
    if man["n_raw_files"] != 2048 or sorted(man["arms"]) != sorted(ROWS[TAGS.index(t)]["ARMS"].split()) or man["git_commit"] != RUNC or man["config_hash"] != "c28b71e6ef34d918": bad.append((t, "manifest", man["n_raw_files"], man["arms"]))
    if man["trial_stream"].get("skip_min") != 10000 or man["trial_stream"].get("skip_max_end") != 30480 or set(man["points"].values()) != {N2} or len(man["points"]) != 4: bad.append((t, "manifest trial_stream/points", man["trial_stream"], man["points"]))
    w = datetime.strptime(man["written"], "%Y-%m-%d %H:%M:%S KST").replace(tzinfo=KST)
    if not (RUN[t] <= w <= ACC[t][0] + timedelta(minutes=1)): bad.append((t, "manifest written outside run..acceptance", man["written"]))
    if not (RUN[t] <= cdt(MT[t][0]) and cdt(MT[t][1]) <= ACC[t][0] + timedelta(minutes=1)): bad.append((t, "chunk mtimes outside run..acceptance", cdt(MT[t][0]), cdt(MT[t][1])))
    if f"run|git ['{RUNC}']" not in af or not re.search(r"raised trials per arm \(= failures, report only\) 0\n", af): bad.append((t, "accept file", af))
chk("H5 §6.1 per-row table (3 rows: start, runner minutes 74.3 / 36.9 / 1.6, 2048 tasks, 192 workers, done 2048 / exists 0, acceptance time, verdicts, manifest git c48ee796 · config_hash c28b71e6ef34d918, control verdicts) = logs + files; runner logs: one header each, one 'finished', 2048 'done' lines naming exactly the 2048 chunk files, 0 'exists', no Traceback; manifests 2048 files / arms / trial_stream 10000..30480 / 4 points x 20480, written inside run..acceptance; chunk mtimes inside run..acceptance",
    not bad and len(rows61) == 3 and [RMIN[t] for t in TAGS] == ["74.3", "36.9", "1.6"], str(bad[:2]), n=3 * 12 + 3 * 8)
print("   chunk mtime windows (CDT): " + " · ".join(f"{t} {cdt(MT[t][0]):%H:%M:%S}–{cdt(MT[t][1]):%H:%M:%S}" for t in TAGS))
print("   manifests written: " + " · ".join(json.load(open(f"{RV}/run_manifest_{t}.json"))["written"] for t in TAGS))
fl = [l for l in S6 if l.startswith("- `(f) raw_")]
chk("H6 §6.1 '(f)' lines (3) = the accept files' (f) lines verbatim",
    fl == [f"- `{x.strip()}`" for t in TAGS for x in rd(f"{RV}/{t}_accept.txt").split("\n") if x.strip().startswith("(f)")] and len(fl) == 3, n=3)
gl = sh(f"git log --format='%h %ci' {RUNC}^..{S6C}").split("\n")
trun = datetime.strptime(sh(f"git log -1 --format=%ci {RUNC}"), "%Y-%m-%d %H:%M:%S %z"); ts6 = datetime.strptime(sh(f"git log -1 --format=%ci {S6C}"), "%Y-%m-%d %H:%M:%S %z")
ctlcopy = cdt(os.stat("results/ald/tune_FHCALDSRP.json").st_mtime)
chk("H7 git: no commit between c48ee796 (18:34:19 CDT; not after the first file the run wrote, same minute as the start line) and aefbfc12 (20:38:36 CDT, after FIGHS_DONE 20:36); c48ee796 is the last commit touching the registration before aefbfc12",
    len(gl) == 2 and trun.astimezone(CDT) <= ctlcopy + timedelta(seconds=1) and trun.astimezone(CDT) < cdt(MT["FHSRPB16e4"][0]) and ts6.astimezone(CDT) > cdt(os.stat("logs/run_fighspath16e4.log").st_mtime) and
    f"{trun.astimezone(CDT):%H:%M}" == "18:34" and sh(f"git log --format=%h -2 {S6C} -- {REG}").split("\n") == [S6C, RUNC],
    f"{trun.astimezone(CDT)} .. {ts6.astimezone(CDT)}; first run artefact (tune copy for the ALD control) {ctlcopy:%H:%M:%S}; {gl}", n=4)
chk("H8 §6 header '기록 2026-10-11 20:37 CDT' = registration file mtime minute; §6.1 names the generator s6_fighsroom_gen.py (committed in aefbfc12 with the SRP mode)",
    f"{cdt(os.stat(REG).st_mtime):%m-%d %H:%M}" == "10-11 20:37" and S6[0].startswith("## 6. 결과 (기록 2026-10-11 20:37 CDT, Opus 5.5") and not sh(f"git diff {S6C} -- {AUD}/s6_fighsroom_gen.py"),
    f"registration mtime {cdt(os.stat(REG).st_mtime):%H:%M:%S}; generator mtime {cdt(os.stat(f'{AUD}/s6_fighsroom_gen.py').st_mtime):%H:%M:%S}", n=2)
T0 = datetime(2026, 10, 11, 18, 34, 19, tzinfo=CDT)
paths = [f"raw_{t}" for t in TAGS] + [f"raw_{t.replace('FH', 'FHC', 1)}" for t in TAGS] + ["results/ald/ald_PILSRP_hisnr.npz", "results/ald/pilots_PILSRP_hisnr.npz", "results/ald/ald_FHCALDSRP.npz", "results/ald/tune_FHCALDSRP.json",
         f"{RV}/FHCSRPB16e4_control.txt", f"{RV}/FHCSPSRP_control.txt", f"{RV}/FHCALDSRP_control.txt", f"{RV}/FHCALDSRP_aldcontrol.txt"]
def first_m(p): return min([os.stat(os.path.join(p, f)).st_mtime for f in os.listdir(p)] + [os.stat(p).st_mtime]) if os.path.isdir(p) else os.stat(p).st_mtime
pre = [p for p in paths if cdt(first_m(p)) < T0]
chk("H9 §5 '실행 시작 전 상태: raw_FH*SRP* · ald_PILSRP_hisnr.npz · FHC*SRP 대조 파일 없음': every such path (and every file in the raw dirs) has an mtime at or after the run commit 18:34:19 CDT", not pre, str(pre), n=len(paths))
chk("H10 paper_f21dmc.py and fighs_merge.py mtime 10-11 19:54 CDT: after the run commit c48ee796 (so uncommitted when the figure was made 20:37:41), before the figure; both committed in aefbfc12 and unchanged since",
    f"{FIGT['paper_f21dmc.py']:%m-%d %H:%M}" == "10-11 19:54" == f"{FIGT['fighs_merge.py']:%m-%d %H:%M}" and FIGT["paper_f21dmc.py"] < FIGT["F21srphs_col.pdf"] and
    not sh(f"git diff {S6C} -- ../conference/figures/paper_f21dmc.py ../conference/figures/fighs_merge.py") and
    sh(f"git diff --stat {RUNC} {S6C} -- ../conference/figures/paper_f21dmc.py ../conference/figures/fighs_merge.py").count("|") == 2, f"{FIGT['paper_f21dmc.py']} {FIGT['fighs_merge.py']}", n=4)
SR = [l for l in rd("logs/seeds_SRB_train.log").split("\n") if l]; SP_ = [l for l in rd("logs/seeds_SRP_train.log").split("\n") if l]
chk("H11 seed-training logs vs §6.4 / DECISIONS: SRP seeds on GPU 0 from 14:20 CDT, a2 stopped 16:47, a3 stopped 19:20, SEEDS_TRAIN_DONE 19:20; SRB a2 on GPU 0 and a3 on GPU 2 start 19:26 CDT (git c48ee796)",
    SR == ["[seeds 10-11 19:26 CDT] SRB a2 start (git c48ee796) GPU 0 pin 20,116", "[seeds 10-11 19:26 CDT] SRB a3 start (git c48ee796) GPU 2 pin 22,118"] and
    SP_[0] == "[seeds 10-11 14:20 CDT] start (git 99039ef5) GPU 0 pin 20,116" and SP_[1].startswith("[seeds 10-11 16:47 CDT] SRP a2 ") and SP_[2].startswith("[seeds 10-11 19:20 CDT] SRP a3 ") and SP_[3] == "[seeds 10-11 19:20 CDT] SEEDS_TRAIN_DONE", n=6)

# ====================================================================== I. §6.4 / EXPERIMENTS row / DECISIONS
print("\n# I. §6.4, EXPERIMENTS, DECISIONS")
chk("I1 §6.4 'ald_PILSRP_hisnr.npz sha256[:16] 3a13dfb7191bd3ed (git 밖)' = disk; file untracked", any("3a13dfb7191bd3ed (git 밖)" in l for l in S6) and ALD_HS_SHA == "3a13dfb7191bd3ed" and not sh("git ls-files results/ald/ald_PILSRP_hisnr.npz"), n=2)
chk("I1b §6.4 cost line: '§1 의 비용 추정(base ≈ 90 분 · SP ≈ 50 분 · ALD ≈ 10 분, 합 ≈ 2.5 시간) 대비 실측 runner 74.3 · 36.9 · 1.6 분, 전체 10-11 18:34 → 10-11 20:36 CDT' = §1 estimates + runner logs + log times",
    any("§1 의 비용 추정(base ≈ 90 분 · SP ≈ 50 분 · ALD ≈ 10 분, 합 ≈ 2.5 시간) 대비 실측 runner 74.3 · 36.9 · 1.6 분, 전체 10-11 18:34 → 10-11 20:36 CDT." in l for l in S6) and
    all(x in "\n".join(reg[:i6]) for x in ("FHSRPB16e4 ≈ 90 분", "FHSPSRP ≈ 50 분", "FHALDSRP ≈ 10 분", "합 ≈ 2.5 시간")), n=7)
chk("I1c §6.4 concurrent-work times checkable from files: audit_FIGHSROOM16e4.md (18:56 CDT), review_FIGHSX16e4.md (19:52 CDT), FHSRBB16e4_highsnr_fail.txt (18:53 CDT) all inside the run window 18:34..20:36 CDT",
    all(T0 < cdt(os.stat(p).st_mtime) < datetime(2026, 10, 11, 20, 37, tzinfo=CDT) for p in (f"{AUD}/audit_FIGHSROOM16e4.md", f"{RV}/prereg_reviews_2026-10-11/review_FIGHSX16e4.md", f"{RV}/FHSRBB16e4_highsnr_fail.txt")),
    " ".join(f"{os.path.basename(p)} {cdt(os.stat(p).st_mtime):%H:%M:%S}" for p in (f"{AUD}/audit_FIGHSROOM16e4.md", f"{RV}/prereg_reviews_2026-10-11/review_FIGHSX16e4.md", f"{RV}/prereg_reviews_2026-10-11/review_FIGHSX16e4_gpu_smoke.py", f"{RV}/FHSRBB16e4_highsnr_fail.txt")), n=3)
EXP = rd("../docs/EXPERIMENTS.md").split("\n")
exp = [l for l in EXP if "run_fighspath16e4.sh" in l]
E = exp[0] if exp else ""
NM = {"V1": "M-ours-dscore-C-V1", "ALD-pilot": "ALD-pilot", "b\\*": "M-ours-bstar", "R2": "R2-ours-G", "R1": "R1-turbo", "BiG-AMP": "R3-bigamp", "R0@1": "R0-pilot@1", "SBL-loop": "SBL-loop", "SBL-pilot": "SBL-pilot", "OMP-pilot": "OMP-pilot", "genie": "R5-genie"}
own = ", ".join(f"{k} " + " / ".join(str(ncount(a, SRC[a][0], s)) for s in SN) for k, a in NM.items())
chk("I2 EXPERIMENTS.md FIGHSPATH16e4 row (last line, 75): the 11 x 4 failure counts = own recount", len(exp) == 1 and EXP.index(E) == 74 and (not EXP[75:] or not any(EXP[75:])) and f"**실패 수 / 20480 (+6 / +9 / +12 / +15 dB)**: {own}." in E, f"own: {own}", n=44)
i3 = ("| 2026-10-12 08:34 ~ 10:36 KST (텍사스 10-11 18:34 ~ 20:36 CDT; 한 번 시작, 재개 없음) |", "NEXT_EXPERIMENTS_FIGHSPATH16e4 v2 = 실행 커밋 c48ee796", "`FIGHS_DONE ok=3 fail=0`; ACCEPT OK ×3", "| c48ee796 |",
      "오르는 칸 (한쪽 Fisher p; 보고만) 1 줄 (그림 기록)", "runner 74.3 · 36.9 · 1.6 분", "ALD 대조·추정만 GPU 1; 수신기 CPU 192", "(y (3e-05, 1.2))", "§3 예측: 1 적중, 2 적중, 3 적중, 4a 적중, 4b 적중, 5 적중",
      "--snr 6 9 12 15 --n 20480 --skip0 10000", "20260926, **새 시행 10000..30479** (n 20480 / SNR; 테스트 풀 52,200 스냅숏 복원 추출 — 새 추첨이지 새 채널이 아님), C2 4 SNR, PID 15",
      "**GMM b\\* 는 PATH16e4 의 씨앗 초기화 그대로**", "판정·라벨은 원 raw (n 2560) 그대로이고 다시 판정하지 않는다", "Fable 사전 검토 MUST 1 · SHOULD 5 · NIT 5 반영", "(b\\* kron 4096)", "**보고 전용** — 새 검정·라벨 없음")
chk("I3 EXPERIMENTS.md FIGHSPATH16e4 row: times, run commit, FIGHS_DONE, ACCEPT x3, commit column, rising '1 줄', runner minutes, GPU 1, y range, 6 predictions, flags, seed / trials / pool / PID, GMM caveat, 'not re-judged', review counts",
    all(x in E for x in i3), str([x for x in i3 if x not in E]), n=len(i3))
pid = re.search(r"[\"']SRP[\"']\s*:\s*(\d+)", rd("code/common.py"))
rv = rd(f"{RV}/prereg_reviews_2026-10-11/review_FIGHSPATH16e4.md")
chk("I3b PID of prior SRP in code/common.py = 15; review_FIGHSPATH16e4.md counts MUST 1 · SHOULD 5 · NIT 5 (headings M-/S-/N-)",
    pid and pid[1] == "15" and (len(re.findall(r"^### M-\d", rv, re.M)), len(re.findall(r"^### S-\d", rv, re.M)), len(re.findall(r"^- N-\d", rv, re.M))) == (1, 5, 5),
    f"PID {pid and pid[1]}; review items {(len(re.findall(r'^### M-', rv, re.M)), len(re.findall(r'^### S-', rv, re.M)), len(re.findall(r'^- N-', rv, re.M)))}", n=4)
DEC = rd("DECISIONS.md").split("\n")
dec = [l for l in DEC if "FIGHSPATH16e4 실행 끝" in l and "10:38 KST" in l]
d4 = ("`[2026-10-12 10:38 KST] FIGHSPATH16e4 실행 끝 + FIGHSROOM16e4 기록 감사 + 빈 GPU 에 SRB 시드 학습 (Opus 5.5; 텍사스 10-11 20:38 CDT)", "10-11 18:34 ~ 20:36 CDT @c48ee796, FIGHS_DONE ok=3 fail=0",
      "V1 45 / 7 / 0 / 0, b* 202 / 33 / 3 / 1, genie 14 / 1 / 1 / 0", "곡선이 +9 dB 에서 끝남", "예측 6 개 적중", "GMM b* 는 씨앗 초기화 그대로", "§6 의 수치·채점 오류 0 (약 1,050 값 + 배열 비교 33,135 건), MUST 1 · SHOULD 2 · NIT 4 반영",
      "SRB 의 시드 a2 · a3 학습을 GPU 0 · 2 에서 시작 (19:26 CDT", "SRP 시드 a2 · a3 는 19:20 CDT 에 끝남", "FHSRBB16e4_highsnr_fail.txt (FIGHSROOM16e4 §6.6)")
chk("I4 DECISIONS.md 10:38 KST line (added in aefbfc12): FIGHSPATH16e4 18:34 ~ 20:36 CDT @c48ee796, ok=3 fail=0, V1 45 / 7 / 0 / 0, b* 202 / 33 / 3 / 1, genie 14 / 1 / 1 / 0, 6 predictions; FIGHSROOM audit summary; SRB seeds 19:26 GPU 0 · 2; SRP seeds 19:20",
    len(dec) == 1 and all(x in dec[0] for x in d4) and [f"{ncount(a, 'FHSRPB16e4', s)}" for a in ("M-ours-dscore-C-V1", "M-ours-bstar", "R5-genie") for s in SN] == "45 7 0 0 202 33 3 1 14 1 1 0".split()
    and sh(f"git log -S'FIGHSPATH16e4 실행 끝' --format=%h -- DECISIONS.md").split("\n")[-1] == S6C, str([x for x in d4 if x not in (dec[0] if dec else "")]), n=len(d4) + 12)

# ====================================================================== J. other lines of aefbfc12
print("\n# J. other record lines added in aefbfc12")
pil = {t: sorted({PAT.match(os.path.basename(p))[6] for p in glob.glob(f"raw_{t}/D2_*.npz")}) for t in ("SRPB16e4", "SRBB16e4", "FHSRPB16e4", "FHSRBB16e4")}
path16, room16 = rd(f"{RV}/NEXT_EXPERIMENTS_PATH16e4.md"), rd(f"{RV}/NEXT_EXPERIMENTS_ROOM16e4.md")
chk("J1 EXPERIMENTS.md rows 70 / 72 (lines 70, 72): 'DFT 파일럿 (T2b 규칙: erank(Rt) 3.756 ≥ 3.6)' / '… 3.991 ≥ 3.6' = PATH16e4 §0 (3.756/4 ≥ 3.6 → DFT) + §5 / ROOM16e4 §0 (3.991/4) + §5 = '_dft_' raw names; no 'eig 파일럿' left on rows 70..75",
    "`conf/code/srp_build.py`), DFT 파일럿 (T2b 규칙: erank(Rt) 3.756 ≥ 3.6);" in EXP[69] and "`conf/code/srb_build.py`), DFT 파일럿 (T2b 규칙: erank(Rt) 3.991 ≥ 3.6)" in EXP[71] and
    "erank(Rt) 3.756/4 ≥ 3.6 → **DFT 파일럿**" in path16 and "파일럿 DFT (erank Rt 3.756)" in path16 and "erank(Rt) 3.991/4 ≥ 3.6 → **DFT 파일럿**" in room16 and "파일럿 DFT (erank Rt 3.991)" in room16 and
    all(v == ["dft"] for v in pil.values()) and not any("eig 파일럿" in l for l in EXP[69:]), f"raw pilot tokens {pil}", n=8)
d7072 = sh(f"git diff {RUNC} {S6C} --word-diff=porcelain -- ../docs/EXPERIMENTS.md")
wd = [l for l in d7072.split("\n") if re.match(r"^[+-][^+-]", l)]
print("   EXPERIMENTS.md word diff c48ee796..aefbfc12 (changed words only, new last row cut): " + " | ".join(l[:90] for l in wd))
ll = {K: float(np.load(f"results/gmm_fits_D2_SRBB16e4/fit_SRB_Nr8_fullK{K}_n160000.npz", allow_pickle=True)["ll_val"]) for K in (16, 32, 64, 128, 256, 512, 1024)}
gains = [ll[2 * K] - ll[K] for K in (16, 32, 64, 128, 256, 512)]
gstr = " · ".join(f"{g:+.1f}" for g in gains); lstr = " / ".join(f"{ll[K]:.3f}" for K in (16, 32, 64, 128, 256, 512, 1024))
m5 = re.search(r"\[정정 2026-10-11 18:58 CDT — FIGHSROOM16e4 기록 감사 S1: 이 수열은 틀렸다\. §5 격자의 ll_val ([\d./ ]+) 로 계산한 배증당 증가는 ([^n]+) nat \(16 → 32 → … → 1024\) 이다", room16)
chk("J2 ROOM16e4 '[정정 … 감사 S1 …]': ll_val 30.445 / 41.698 / 55.912 / 68.085 / 79.119 / 89.214 / 97.009 and gains +11.3 · +14.2 · +12.2 · +11.0 · +10.1 · +7.8 nat = the fit files' ll_val (own differences); the wrong sequence is kept in place before the bracket (append-only); the §5 grid text holds the same seven values",
    m5 and m5[1] == lstr and m5[2] == gstr and gstr == "+11.3 · +14.2 · +12.2 · +11.0 · +10.1 · +7.8" and "+10.1 · +11.0 · +10.1 · +7.8 nat **[정정" in room16 and f"{gains[-1]:.3f}" == "7.795",
    f"own ll_val {lstr}; gains {gstr}; last {gains[-1]:.3f}", n=14)
aud_room = rd(f"{AUD}/audit_ROOM16e4.md")
chk("J3 audit_ROOM16e4.md erratum (appended; 4 added lines, nothing removed): same ll_val list and gains; 'found by audit_FIGHSROOM16e4.md S1'; '+7.795 nat'",
    f"From the §5 grid (ll_val {lstr}) they are " + gstr.replace(" · ", ", ") + " nat (16 → 32 → … → 1024)." in aud_room and "## Erratum (added 2026-10-11 18:58 CDT by the main session, Opus 5.5; found by `audit_FIGHSROOM16e4.md` S1)" in aud_room
    and sh(f"git diff --numstat {RUNC} {S6C} -- {AUD}/audit_ROOM16e4.md").split()[:2] == ["4", "0"], sh(f"git diff --numstat {RUNC} {S6C} -- {AUD}/audit_ROOM16e4.md"), n=15)
chk("J3b the 18:58 CDT time typed in the ROOM16e4 [정정], the audit erratum and FIGHSROOM16e4 §6.5 / §6.6 = mtime of those three files (18:58:40 CDT)",
    all(f"{cdt(os.stat(p).st_mtime):%m-%d %H:%M}" == "10-11 18:58" for p in (f"{RV}/NEXT_EXPERIMENTS_ROOM16e4.md", f"{RV}/NEXT_EXPERIMENTS_FIGHSROOM16e4.md", f"{AUD}/audit_ROOM16e4.md")), n=3)
# ---- FIGHSROOM16e4 §6.5 vs the audit report
fr = rd(f"{RV}/NEXT_EXPERIMENTS_FIGHSROOM16e4.md"); af_ = rd(f"{AUD}/audit_FIGHSROOM16e4.md")
s65 = fr.split("### 6.5 ")[1].split("### 6.6 ")[0]; s66 = fr.split("### 6.6 ")[1]
j4 = [("보고서 파일 mtime 2026-10-11 18:56 CDT", f"{cdt(os.stat(f'{AUD}/audit_FIGHSROOM16e4.md').st_mtime):%Y-%m-%d %H:%M}" == "2026-10-11 18:56"),
      ("감사 대상 = 커밋 ed265304", "Audited version: commit **ed265304**" in af_),
      ("약 1,050 값 + 배열 비교 33,135 건(검사 묶음 58 개 중 56 통과", "≈ 1,050 scalar or string values and 33,135 array comparisons re-derived; 58 check groups, 56 PASS, 2 FAIL" in af_),
      ("**MUST 1 · SHOULD 2 · NIT 4", "MUST 1 · SHOULD 2 · NIT 4." in af_ and len(re.findall(r"^\*\*M\d", af_, re.M)) == 1 and len(re.findall(r"^\*\*S\d", af_, re.M)) == 2 and len(re.findall(r"^- \*\*N\d", af_, re.M)) == 4),
      ("오르는 칸 3 개의 p (0.5 / 0.24 / 3.7e-06)", "(0.5, 0.24, 3.7e-06" in af_),
      ("집계표 56 행", "All 56 count-table rows" in af_), ("6.2 의 44 칸", "the 44 cells of the §6.2 table" in af_), ("새 raw 3 × 2048 청크·원 raw 3 × 448", "3 × 2048 chunks" in af_ and "(3 × 448)" in af_),
      ("`eval_accept` 세 행 재실행 → 모두 `ACCEPT: OK`", "→ `ACCEPT: OK` × 3, rc 0" in af_),
      ("기록 2 개·PDF/PNG 4 개가 **바이트 동일**", "stdout **byte-identical** to the committed `records/paper_f21srb.txt` and `records/paper_f21srbhs.txt`; `F21srb_col.{pdf,png}` and `F21srbhs_col.{pdf,png}` **byte-identical**" in af_),
      ("T2b 규칙 erank(Rt) 3.756 · 3.991 ≥ 3.6", "erank(Rt) 3.756 ≥ 3.6" in af_ and "erank(Rt) 3.991 ≥ 3.6" in af_),
      ("(+11.3 · +14.2 · +12.2 · +11.0 · +10.1 · +7.8 nat)", "+11.3 · +14.2 · +12.2 · +11.0 · +10.1 · +7.8 nat" in af_),
      ("비용 추정 65 / 50 / 10 분 대비 실측 runner 39.0 / 41.6 / 1.5 분 + 새 시행의 ALD 재생성·추정 약 3 분, 전체 17:01 → 18:31 CDT", "runner 39.0 / 41.6 / 1.5 min, plus the new-trial ALD regen (11 s) + estimate 18:25 → 18:28 CDT, wall 17:01 → 18:31 CDT" in af_),
      ("`SKIP0` 모드가 추가됐다(10-11 18:51 CDT", "mtime 10-11 18:51:31 CDT" in af_)]
chk("J4 FIGHSROOM16e4 §6.5 reports audit_FIGHSROOM16e4.md faithfully (14 quoted facts: mtime, audited commit, value / array / check-group counts, MUST/SHOULD/NIT counts, p's, table sizes, re-runs, byte-identity, M1 / S1 / N1 content, SKIP0 note)",
    all(q in s65 and ok for q, ok in j4), str([q for q, ok in j4 if not (q in s65 and ok)]), n=len(j4))
nv = [x for x in ("N4", "GPU 0", "[감사 S2]", "§0") if x in af_.split("## Not verified")[1].split("## Note")[0]]
print(f"   audit 'Not verified' section has {len(re.findall(r'^- ', af_.split('## Not verified')[1].split('## Note')[0], re.M))} bullets (keywords {nv}); §6.5 lists: '그 진술들, GPU 0 의 시드 학습, 풀 통계(§0)의 원 재계산'")
print(f"   ed265304 added to DECISIONS.md: {len([l for l in sh('git diff 193776a1 ed265304 -- DECISIONS.md').split(chr(10)) if l.startswith('+`[')])} line(s) (§6.5 says 'DECISIONS.md 두 줄' among the things 'in the same commit')")
print(f"   git diff --numstat 193776a1 ed265304 -- paper_f21dmc.py: {sh('git diff --numstat 193776a1 ed265304 -- ../conference/figures/paper_f21dmc.py')} (§6.4 [감사 N3] says '7 줄')")
# ---- FIGHSROOM16e4 §6.4 [감사 S2] six values, from the SRB FH raws (own reader)
print("   scanning raw_FHSRBB16e4 for §6.4 [감사 S2] and §6.6 ...")
ARB = ("M-ours-dscore-C-V1", "M-ours-bstar", "R2-ours-G", "R5-genie")
RB = {s: {a: [] for a in ARB} for s in SN}; rbgit = set()
for p in sorted(glob.glob("raw_FHSRBB16e4/D2_*.npz"), key=lambda p: (float(PAT.match(os.path.basename(p))[7]), int(PAT.match(os.path.basename(p))[8]))):
    m = PAT.match(os.path.basename(p))
    with np.load(p) as z:
        rbgit.add(str(z["run|git"]))
        for a in ARB: RB[float(m[7])][a].append(np.asarray(z[f"{a}|blk_err"], float))
RB = {s: {a: np.concatenate(v) for a, v in d.items()} for s, d in RB.items()}
kb = {a: [int(RB[s][a][:, -1].sum()) for s in SN] for a in ARB}
s2 = (f"Perfect CSI +12 · +15 dB (1 / 20480 = {1 / N2:.1e}; Wilson 하한 {wilson(1, N2)[0]:.1e})", f"{3 / N2:.1e} · {4 / N2:.1e}", f"{wilson(3, N2)[0]:.1e} · {wilson(4, N2)[0]:.1e}", f"({wilson(kb['M-ours-bstar'][3], N2)[0]:.1e} · {wilson(kb['R5-genie'][1], N2)[0]:.1e})")
chk("J5 FIGHSROOM16e4 §6.4 [감사 S2] six sub-2e-4 values from raw_FHSRBB16e4 (own): genie +12/+15 1/20480 = 4.9e-05, Wilson lower 8.6e-06; Proposed +12/+15 = 3 · 4 / 20480 = '1.5e-04 · 1.9e-04', lower 5.0e-05 · 7.6e-05; b* +15 and genie +9 lower 1.3e-04 · 1.0e-04",
    kb["M-ours-dscore-C-V1"] == [45, 10, 3, 4] and kb["R5-genie"] == [17, 5, 1, 1] and kb["M-ours-bstar"] == [90, 23, 11, 6] and
    "Perfect CSI +12 · +15 dB (1 / 20480 = 4.9e-05; Wilson 하한 8.6e-06), Proposed +12 · +15 dB (3 · 4 / 20480 = 1.5e-04 · 1.9e-04; 하한 5.0e-05 · 7.6e-05), GMM b\\* +15 dB 와 Perfect CSI +9 dB 의 Wilson 하한 (1.3e-04 · 1.0e-04)" in fr
    and s2[0] in fr and s2[1] in fr and s2[2] in fr and s2[3] in fr,
    f"own strings (%.1e): {s2}; 4/20480 = {4 / N2:.4e}", n=8)
# ---- §6.6 against FHSRBB16e4_highsnr_fail.txt and against the raw
hf = rd(f"{RV}/FHSRBB16e4_highsnr_fail.txt")
def sect(s): return hf.split(f"\n{s} dB  n=20480")[1].split("\n\n")[0]
tr = {s: re.findall(r"trial\s+(\d+): share ([\d.]+).*?also fail: (.*?)  channel (\w+) \(drawn (\d+)x", sect(s), re.M) for s in ("+6", "+9", "+12", "+15")}
it = {s: re.search(r"by iteration \(1, 2, 4, 8, 16\): \[([\d, ]+)\]", sect(s))[1] for s in ("+6", "+9", "+12", "+15")}
med = {s: re.search(r"share median ([\d.]+)", sect(s))[1] for s in ("+6", "+9", "+12", "+15")}
dist = {s: int(re.search(r"distinct channels among the 20480 trials (\d+)", sect(s))[1]) for s in ("+6", "+9", "+12", "+15")}
alg = [("alignment (genie, first 20 trials) OK" in sect(s)) for s in ("+6", "+9", "+12", "+15")]
ownidx = {s: np.where(RB[s]["M-ours-dscore-C-V1"][:, -1] > 0)[0].tolist() for s in SN}
ownit = {s: [int(RB[s]["M-ours-dscore-C-V1"][:, i - 1].sum()) for i in (1, 2, 4, 8, 16)] for s in SN}
ownalso = {s: [[n_ for a, n_ in (("M-ours-bstar", "bstar"), ("R5-genie", "R5-genie"), ("R2-ours-G", "R2-ours-G")) if RB[s][a][t, -1] > 0] for t in ownidx[s]] for s in SN}
k12, k15 = tr["+12"], tr["+15"]
chk("J6 §6.6 vs FHSRBB16e4_highsnr_fail.txt AND vs raw_FHSRBB16e4 (own reader, chunks in skip order): V1 failing blocks +12 dB at raw index 1853 · 15558 · 19518, +15 dB 3420 · 4014 · 9512 · 12742; shares 0.854 · 0.936 · 0.980 / 0.988 · 0.991 · 0.846 · 0.821; medians 0.82; seven distinct channel fingerprints; every one also fails on b* or R2 (one also genie); iteration series 76 → 6 → 3 → 3 → 3 and 41 → 9 → 4 → 4 → 4; alignment OK x 4; distinct channels ≈ 1.7e4",
    [int(t[0]) for t in k12] == [1853, 15558, 19518] == ownidx[12.0] and [int(t[0]) for t in k15] == [3420, 4014, 9512, 12742] == ownidx[15.0] and
    [t[1] for t in k12] == ["0.854", "0.936", "0.980"] and [t[1] for t in k15] == ["0.988", "0.991", "0.846", "0.821"] and all(f"{float(v):.2f}" == "0.82" for v in med.values()) and
    len({t[3] for t in k12 + k15}) == 7 and all(("bstar" in t[2].split(", ")) or ("R2-ours-G" in t[2].split(", ")) for t in k12 + k15) and sum("R5-genie" in t[2].split(", ") for t in k12 + k15) == 1 and
    [t[2].split(", ") for t in k12] == ownalso[12.0] and [t[2].split(", ") for t in k15] == ownalso[15.0] and
    it["+12"] == "76, 6, 3, 3, 3" == ", ".join(map(str, ownit[12.0])) and it["+15"] == "41, 9, 4, 4, 4" == ", ".join(map(str, ownit[15.0])) and all(alg) and all(16500 <= v <= 17499 for v in dist.values()) and
    all(x in s66 for x in ("+12 dB 시행 1853 · 15558 · 19518, +15 dB 시행 3420 · 4014 · 9512 · 12742", "0.854 · 0.936 · 0.980 / 0.988 · 0.991 · 0.846 · 0.821 (전체 시행의 중앙값 0.82)", "+12 dB 76 → 6 → 3 → 3 → 3, +15 dB 41 → 9 → 4 → 4 → 4", "서로 다른 풀 채널 약 1.7 만 개", "한 건은 genie 도", "서로 다른 채널 일곱 개", "genie 재생 정렬 검사 네 SNR 모두 OK")),
    f"own idx {ownidx[12.0]} {ownidx[15.0]}; own it {ownit[12.0]} {ownit[15.0]}; file medians {med}; distinct {dist}; raw_FHSRBB16e4 run|git {sorted(rbgit)}", n=7 + 7 + 7 + 10 + 4 + 4 + 4)
print(f"   §6.6 'trial' numbers are 0-based positions in the n = 20480 raw (script prints np.where index); stream trial = 10000 + index: +12 dB {[10000 + i for i in ownidx[12.0]]}, +15 dB {[10000 + i for i in ownidx[15.0]]}")
print(f"   own recount of the file's other header numbers: V1 failures by iteration +6 {ownit[6.0]} (file [{it['+6']}]), +9 {ownit[9.0]} (file [{it['+9']}]); V1 idx count +6 {len(ownidx[6.0])} (file {len(tr['+6'])}), +9 {len(ownidx[9.0])} (file {len(tr['+9'])})")
fp_all = {s: [t[3] for t in tr[s]] for s in tr}
print(f"   channel fingerprints of the seven: {[t[3] for t in k12 + k15]}; of these also failing at another SNR in the file: {sorted({f for f in [t[3] for t in k12 + k15] if sum(f in fp_all[s] for s in fp_all) > 1})}")
chk("J7 FHSRBB16e4_highsnr_fail.txt added in aefbfc12 (mtime 18:53 CDT); the committed SRBB16e4_highsnr_fail.txt is unchanged 1404d315..aefbfc12; highsnr_fail_SRB.py diff 1404d315..aefbfc12 = +18 −7 (default-mode equivalence judged by reading the diff, see report)",
    sh(f"git log --format=%h --diff-filter=A -- {RV}/FHSRBB16e4_highsnr_fail.txt") == S6C and not sh(f"git diff 1404d315 {S6C} -- {RV}/SRBB16e4_highsnr_fail.txt") and
    sh(f"git diff --numstat 1404d315 {S6C} -- {AUD}/highsnr_fail_SRB.py").split()[:2] == ["18", "7"] and f"{cdt(os.stat(f'{RV}/FHSRBB16e4_highsnr_fail.txt').st_mtime):%H:%M}" == "18:53", sh(f"git diff --numstat 1404d315 {S6C} -- {AUD}/highsnr_fail_SRB.py"), n=4)
chk("J8 paper_f21srbhs.txt changed in aefbfc12 by one line only (the 'Asserts passed: counts before the merge …' wording, FIGHSROOM N2); F21srbhs_col.{pdf,png} not in the commit (unchanged since ed265304)",
    sh(f"git diff --numstat {RUNC} {S6C} -- ../conference/figures/records/paper_f21srbhs.txt").split()[:2] == ["1", "1"] and not sh(f"git diff --stat ed265304 {S6C} -- ../conference/figures/F21srbhs_col.pdf ../conference/figures/F21srbhs_col.png"), n=3)

# ---- wording of §6
voc = {w: [i6 + 1 + i for i, l in enumerate(S6) if w in l] for w in ("라벨", "유의", "우수", "입증", "시사", "결론", "일반화", "동치", "판정", "검정", "이긴", "우위", "개선", "낫다", "better", "significant")}
print("\n# wording: vocabulary hits in §6 (line numbers): " + str({w: v for w, v in voc.items() if v}))
print("   §6 lines mentioning the GMM caveat (씨앗 초기화): " + str([i6 + 1 + i for i, l in enumerate(S6) if "씨앗 초기화" in l]) + "; lines naming M-ours-bstar / b\\* / GMM: " + str([i6 + 1 + i for i, l in enumerate(S6) if re.search(r"M-ours-bstar|b\\\*|GMM", l)]))

print(f"\n# SUMMARY: {sum(ok for _, ok in CHECKS)} PASS / {sum(not ok for _, ok in CHECKS)} FAIL of {len(CHECKS)} checks; ≈ {NVAL[0]} scalar / string values, {NARR} array comparisons  ({datetime.now(CDT):%Y-%m-%d %H:%M:%S %Z})")
for n, ok in CHECKS:
    if not ok: print("   FAIL:", n)
