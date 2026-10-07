#!/usr/bin/env python
"""recompute_fighs.py -- independent RECORD AUDIT of NEXT_EXPERIMENTS_FIGHS16e4.md §6.1 (Fable 5.1 subagent, read-only).
Run from /home/HTJ/t2/conf:  CUDA_VISIBLE_DEVICES= ~/miniforge3/envs/torch/bin/python results/review_next/prereg_audit_2026-10-07/recompute_fighs.py
Everything is re-derived from primary sources: the raw npz chunks are opened directly (numpy only; no analysis.load_raw, no
hisnr_report, no s6_gen.py, the count tables are compared AGAINST, never read as input), Wilson is re-implemented, Fisher via
scipy.stats.fisher_exact (as the registration prescribes).  Writes nothing except stdout.  Up to 32 worker processes.
Sections: A rows / registration  B new raws (24 x 2048 chunks)  C original raws (26 x 448)  D controls (FHC vs ORIG, ZZ vs FHC,
ALD)  E count tables + §6.1 tables  F predictions / cells.tsv / §0.4 / Fisher  G run log, runner logs, interruption, manifests,
before/, mtimes, git  H figure records  I environment / wording numbers.  Each check prints PASS/FAIL; a summary ends the output.
"""
import glob, hashlib, json, os, re, subprocess, sys
from datetime import datetime, timedelta
from multiprocessing import get_context
from zoneinfo import ZoneInfo

import numpy as np
from scipy.stats import fisher_exact

os.chdir("/home/HTJ/t2/conf")
RV = "results/review_next"; REG = f"{RV}/NEXT_EXPERIMENTS_FIGHS16e4.md"; D = "logs/fighs_interrupt_20261006CDT"
AUD = f"{RV}/prereg_audit_2026-10-07"
CDT, KST = ZoneInfo("America/Chicago"), ZoneInfo("Asia/Seoul")
SN = (6.0, 9.0, 12.0, 15.0); N2 = 20480; N1 = 2560
KEYS_RAW = ("blk_err", "ber", "nmse", "tauL_gmean", "alphaD", "tauL_clip_frac", "alphaD_clip")   # common.KEYS_RAW (copied, not imported)
REPLAY_KEYS = ("blk_err", "ber", "tauL_gmean", "alphaD")
PAT = re.compile(r"^D2_(C\d)_([A-Za-z0-9]+?)_Nr(\d+)_T(\d+)_Tp(\d+)_(dft|eig)_snr(-?\d+)_skip(\d+)_n(\d+)\.npz$")
WANT_META = ("ntrain", "bstar", "kron_K", "ll_val|kron", "ll_val|gmm256", "stagec_ckpt_id", "sparse", "rotation", "ald_file", "em_sec_note")

CHECKS = []
def chk(name, ok, detail=""):
    CHECKS.append((name, bool(ok)))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" -- {detail}" if detail else ""))
    return bool(ok)
def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
def wilson(k, n, z=1.959963984540054):            # own implementation of the Wilson score interval (= hisnr_report.wilson formula)
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h
def fisher_p(hi, lo):                               # §1: table [[f_hi, n_hi - f_hi], [f_lo, n_lo - f_lo]], alternative='greater'
    return fisher_exact([[hi[0], hi[1] - hi[0]], [lo[0], lo[1] - lo[0]]], alternative="greater")[1]
def cdt(ts): return datetime.fromtimestamp(ts, CDT)
def ts_cdt(s, fmt="%Y-%m-%d %H:%M"): return datetime.strptime(s, fmt).replace(tzinfo=CDT)
def sh(c): return subprocess.run(c, shell=True, capture_output=True, text=True).stdout.strip()

print(f"# recompute_fighs.py  started {datetime.now(CDT):%Y-%m-%d %H:%M:%S %Z} (= {datetime.now(KST):%H:%M KST})  HEAD {sh('git rev-parse --short HEAD')}")

# ====================================================================== A. the 24 registered rows (script ROWS vs §1a)
F = "TAG CELL PR BF CK SHA ROLE BS KK LL REF ORIG PICK FL ARMS".split()
rows_txt = re.search(r"^ROWS='(.*?)'$", open("code/run_fighs16e4.sh").read(), re.S | re.M)[1].split("\n")
ROWS = [dict(zip(F, l.split("|"))) for l in rows_txt]
TAGS = [r["TAG"] for r in ROWS]
chk("A1 ROWS: 24 rows, 15 fields each", len(ROWS) == 24 and all(len(l.split("|")) == 15 for l in rows_txt))
reg = open(REG, encoding="utf-8").read().split("\n")
i61 = next(i for i, l in enumerate(reg) if l.startswith("### 6.1"))
S61 = reg[i61:]
# §1a rows: | # | TAG | dataset | arm | flags | ckpt | b* · ll | REF | ORIG |
reg1a = {}
for l in reg[:i61]:
    m = re.match(r"^\| (\d+) \| (FH\w+) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \|$", l)
    if m: reg1a[m[2]] = m
chk("A2 §1a lists the same 24 tags in the same order", [t for t in reg1a] == TAGS)
bad = []
for r in ROWS:
    m = reg1a[r["TAG"]]; flags, ck, ref, orig = m[5], m[6], m[8], m[9]
    want_ref = "—" if r["REF"] == "-" else (f"raw_{r['REF']}" if not r["REF"].startswith("FH") else r["REF"])
    want_orig = " + ".join(f"raw_{o}" for o in r["ORIG"].split(","))
    if ref.strip() != want_ref or orig.strip() != want_orig: bad.append((r["TAG"], ref, orig))
    if r["PICK"] != "-" and r["PICK"].split(":")[1] not in flags: bad.append((r["TAG"], "pick sha"))
    if r["CK"] != "-" and r["SHA"] not in ck and r["SHA"][:4] + "…" not in ck and "〃" not in ck: bad.append((r["TAG"], "ckpt sha"))   # §1a abbreviates '4443…' on row 16
    for fl in ("--rotation 15", "--rotation 30", "--pilot-arms", "--ald-file"):
        if (fl in r["FL"]) != (fl in flags): bad.append((r["TAG"], fl))
chk("A3 §1a REF / ORIG / pick sha / ckpt sha / flags agree with ROWS", not bad, str(bad[:5]))
# registered values present on disk
bad = [(r["TAG"], "ckpt") for r in ROWS if r["CK"] != "-" and sha(r["CK"])[:16] != r["SHA"]]
bad += [(r["TAG"], "pick") for r in ROWS if r["PICK"] != "-" and sha(r["PICK"].split(":")[0])[:16] != r["PICK"].split(":")[1]]
chk("A4 checkpoint / pick sha256[:16] on disk = ROWS (6 ckpt, 6 picks)", not bad, str(bad))
ALD_REG = {"XAROTaB16e4k": ("4d053e3e69cea6ce", "844d55939b7bb55a", "64939076f196f810", "6dd071bcd697d5d2"),
           "XAROTbB16e4k": ("1ea34f2fb53df32c", "e6c68c6af0f7b72a", "2032a1c8ea447159", "46da6a9477252a72")}
bad = [t for t, (s, pt, pd, tn) in ALD_REG.items() if (sha(f"results/ald/ald_{t}.npz")[:16], sha(f"results/ald/pilots_{t}_test.npz")[:16],
       sha(f"results/ald/pilots_{t}_dev.npz")[:16], sha(f"results/ald/tune_{t}.json")[:16]) != (s, pt, pd, tn)]
chk("A5 original ALD test estimate / test+dev pilots / tune record sha256[:16] = §1/§5", not bad, str(bad))

# ====================================================================== B. new raws: 24 x 2048 chunks (workers)
def scan_new(args):
    tag, path, ref = args
    b = os.path.basename(path); m = PAT.match(b)
    o = {"tag": tag, "file": b, "mtime": os.stat(path).st_mtime, "name": (m[1], m[2], float(m[7]), int(m[8]), int(m[9])) if m else None,
         "arms": {}, "meta": {}, "replay": None, "err": None}
    try:
        with np.load(path) as z:
            fs = set(z.files)
            o["git"] = str(z["run|git"]) if "run|git" in fs else None
            o["run"] = (float(z["run|snr"]), int(z["run|skip"]), int(z["run|n"]), int(z["run|iters"]), int(z["run|seed"]))
            for k in WANT_META:
                if f"meta|{k}" in fs:
                    v = z[f"meta|{k}"]; o["meta"][k] = str(v.item() if v.ndim == 0 else v)
            arms = sorted({k.split("|")[0] for k in fs if "|" in k and not k.startswith(("meta|", "run|"))})
            for a in arms:
                if f"{a}|blk_err" not in fs: continue
                be = np.asarray(z[f"{a}|blk_err"], float)
                last, first = be[:, -1], be[:, 0]
                nf = ~np.isfinite(last)
                o["arms"][a] = (int(np.where(nf, 1.0, last).sum()), int(np.where(np.isfinite(first), first, 1.0).sum()), be.shape,
                                int(nf.sum()), int(z[f"{a}|failed"].sum()) if f"{a}|failed" in fs else 0, f"{a}|failed" in fs)
            if ref:
                rp = os.path.join(ref, b)
                if not os.path.exists(rp): o["replay"] = ["missing ref chunk"]
                else:
                    with np.load(rp) as y:
                        o["replay"] = [k for k in REPLAY_KEYS if f"R5-genie|{k}" not in fs or f"R5-genie|{k}" not in y.files or
                                       z[f"R5-genie|{k}"].shape != y[f"R5-genie|{k}"].shape or
                                       not np.array_equal(z[f"R5-genie|{k}"], y[f"R5-genie|{k}"], equal_nan=True)]
    except Exception as e:
        o["err"] = repr(e)
    return o

jobs = []
for r in ROWS:
    ref = None if r["REF"] == "-" else f"raw_{r['REF']}"
    jobs += [(r["TAG"], p, ref) for p in sorted(glob.glob(f"raw_{r['TAG']}/D2_*.npz"))]
print(f"\n# B. scanning {len(jobs)} new-raw chunks with 32 workers ...")
with get_context("fork").Pool(32) as pool:
    NEW = list(pool.imap_unordered(scan_new, jobs, chunksize=64))
BY = {t: [] for t in TAGS}
for o in NEW: BY[o["tag"]].append(o)
chk("B0 every chunk readable (no exceptions)", not [o for o in NEW if o["err"]], str([(o["tag"], o["file"], o["err"]) for o in NEW if o["err"]][:3]))
PLAN = {(s, 10000 + 40 * k, 40) for s in SN for k in range(512)}
COUNTS = {}            # tag -> {arm: {snr: f16}}, plus R0-pilot@1
COUNTS1 = {}
NFAILED = {}           # tag -> {arm: sum of |failed|}
MT = {}                # tag -> (min, max) mtime
bad_plan, bad_git, bad_meta, bad_replay, bad_shape, bad_cellprior = [], [], [], [], [], []
PICKS = {r["TAG"]: json.load(open(r["PICK"].split(":")[0])) for r in ROWS if r["PICK"] != "-"}
for r in ROWS:
    t = r["TAG"]; L = BY[t]
    plan = {(o["name"][2], o["name"][3], o["name"][4]) for o in L}
    if len(L) != 2048 or plan != PLAN or any(o["run"][:3] != (o["name"][2], o["name"][3], o["name"][4]) for o in L): bad_plan.append(t)
    if {o["name"][0] for o in L} != {r["CELL"]} or {o["name"][1] for o in L} != {r["PR"]}: bad_cellprior.append(t)
    if {o["git"] for o in L} != {"331f6e57"} or {o["run"][3] for o in L} != {16} or {o["run"][4] for o in L} != {20260926}: bad_git.append(t)
    # meta promised by (a)+(f)
    llkey = "ll_val|kron" if r["BS"] == "kron" else "ll_val|gmm256"
    for o in L:
        mt = o["meta"]
        if mt.get("ntrain") != "160000.0" or mt.get("bstar") != r["BS"] or (r["KK"] != "-" and mt.get("kron_K") != r["KK"]) \
                or mt.get(llkey) != r["LL"]:
            bad_meta.append((t, o["file"], "ntrain/bstar/kron/ll", mt.get("ntrain"), mt.get("bstar"), mt.get("kron_K"), mt.get(llkey))); break
        cid = mt.get("stagec_ckpt_id")
        if r["CK"] == "-":
            if cid is not None: bad_meta.append((t, o["file"], "SP row has stagec_ckpt_id")); break
        elif cid is None or f"sha256[:16]={r['SHA']}" not in cid or f"role={r['ROLE']}" not in cid:
            bad_meta.append((t, o["file"], "ckpt id", cid)); break
        if t in PICKS:
            pk = PICKS[t]; e = pk["per_snr"][str(int(o["name"][2]))]
            if json.loads(mt.get("sparse", "null")) != dict(rho_sbl=pk["rho_sbl"], rho_omp=pk["rho_omp"], n_em=e["n_em"], L=e["L"]):
                bad_meta.append((t, o["file"], "sparse", mt.get("sparse"))); break
        rot = re.search(r"--rotation (\d+)", r["FL"])
        if rot and not (mt.get("rotation") or "").startswith(f"deg={float(rot[1])!r}:"): bad_meta.append((t, o["file"], "rotation", mt.get("rotation"))); break
        if not rot and "rotation" in mt: bad_meta.append((t, o["file"], "unexpected rotation")); break
        ald = re.search(r"--ald-file (\S+)", r["FL"])
        if ald and mt.get("ald_file") != f"{ald[1]} sha256[:16]={sha(ald[1])[:16]}": bad_meta.append((t, o["file"], "ald_file", mt.get("ald_file"))); break
    # arms, shapes, counts
    arms = set(r["ARMS"].split())
    if any(set(o["arms"]) != arms for o in L): bad_shape.append((t, "arm set", sorted({a for o in L for a in o["arms"]})))
    if any(v[2] != (40, 16) for o in L for v in o["arms"].values()): bad_shape.append((t, "shape"))
    c = {a: {s: 0 for s in SN} for a in arms}; c1 = {s: 0 for s in SN}; nf = {a: 0 for a in arms}
    for o in L:
        for a, v in o["arms"].items():
            c[a][o["name"][2]] += v[0]; nf[a] += v[4]
            if a == "R0-pilot": c1[o["name"][2]] += v[1]
    COUNTS[t] = c; COUNTS1[t] = c1 if "R0-pilot" in arms else None; NFAILED[t] = nf
    MT[t] = (min(o["mtime"] for o in L), max(o["mtime"] for o in L))
    if r["REF"] != "-":
        rb = [(o["file"], o["replay"]) for o in L if o["replay"]]
        if rb: bad_replay.append((t, len(rb), rb[:2]))
chk("B1 trial plan: 24 tags x 2048 chunks = 4 SNR x skip 10000..30440 step 40, n 40; run|snr/skip/n = file name", not bad_plan, str(bad_plan))
chk("B2 cell / prior of every chunk name = the row's", not bad_cellprior, str(bad_cellprior))
chk("B3 run|git = 331f6e57 (no +dirty), run|iters 16, run|seed 20260926 in every chunk of every tag", not bad_git, str(bad_git))
chk("B4 meta ntrain / bstar / kron_K / ll_val / ckpt sha+role (SP rows: no ckpt id) / sparse = pick / rotation / ald_file+sha", not bad_meta, str(bad_meta[:3]))
chk("B5 arm set of every chunk = the row's arms; blk_err shape (40, 16)", not bad_shape, str(bad_shape[:3]))
chk("B6 non-finite blk_err@16 count = 0 and <arm>|failed sums = 0 in all 24 tags (raised trials 0)",
    all(v == 0 for t in TAGS for v in NFAILED[t].values()) and all(v[3] == 0 for o in NEW for v in o["arms"].values()), str({t: NFAILED[t] for t in TAGS if any(NFAILED[t].values())}))
chk("B7 genie replay vs REF (HSB16e4k / HSNR16 / same-dataset first row): blk_err, ber, tauL_gmean, alphaD bit-identical in every chunk of the 18 REF rows",
    not bad_replay, str(bad_replay[:3]))
print(f"   replay rows checked: {sum(1 for r in ROWS if r['REF'] != '-')} (= {sum(len(BY[r['TAG']]) for r in ROWS if r['REF'] != '-')} chunks x 4 keys)")
# informational: rotation genie differs from the static HISNR genie (it must)
def genie_vec(tag):
    v = {}
    for o in BY[tag]: v[(o["name"][2], o["name"][3])] = o["arms"]["R5-genie"][0]
    return v
print(f"   info: FHROTaB16e4k genie failures per SNR {[sum(v for (s, _), v in genie_vec('FHROTaB16e4k').items() if s == q) for q in SN]} vs HSB16e4k 66/36/16/13 (different channel: expected to differ)")

# ====================================================================== C. original raws (26 x 448 chunks)
ORIGS = sorted({o for r in ROWS for o in r["ORIG"].split(",")})
def scan_orig(args):
    raw, path = args
    b = os.path.basename(path); m = PAT.match(b)
    o = {"raw": raw, "file": b, "name": (m[1], m[2], float(m[7]), int(m[8]), int(m[9])), "arms": {}, "err": None, "git": None}
    try:
        with np.load(path) as z:
            fs = set(z.files); o["git"] = str(z["run|git"]) if "run|git" in fs else None
            for a in sorted({k.split("|")[0] for k in fs if "|" in k and not k.startswith(("meta|", "run|"))}):
                if f"{a}|blk_err" in fs:
                    be = np.asarray(z[f"{a}|blk_err"], float); last = be[:, -1]
                    o["arms"][a] = (int(np.where(np.isfinite(last), last, 1.0).sum()), be.shape[0], int((~np.isfinite(last)).sum()))
    except Exception as e:
        o["err"] = repr(e)
    return o
jobs = [(o, p) for o in ORIGS for p in sorted(glob.glob(f"raw_{o}/D2_*.npz"))]
print(f"\n# C. scanning {len(jobs)} original-raw chunks ({len(ORIGS)} raws) ...")
with get_context("fork").Pool(32) as pool:
    OR = list(pool.imap_unordered(scan_orig, jobs, chunksize=32))
OBY = {o: [] for o in ORIGS}
for o in OR: OBY[o["raw"]].append(o)
chk("C0 original chunks readable", not [o for o in OR if o["err"]])
OC = {}          # orig raw -> {arm: {snr: (f, n)}}
bad = []
for o in ORIGS:
    L = OBY[o]
    plan = {}
    for x in L: plan.setdefault(x["name"][2], []).append((x["name"][3], x["name"][4]))
    cont = all(sorted(v) == [(40 * k, 40) for k in range(64)] for v in plan.values()) and set(plan) == {-3.0, 0.0, 3.0, 6.0, 9.0, 12.0, 15.0}
    if len(L) != 448 or not cont: bad.append((o, len(L), sorted(plan)))
    c = {}
    for x in L:
        for a, (f, n, nf) in x["arms"].items():
            d = c.setdefault(a, {}).setdefault(x["name"][2], [0, 0, 0]); d[0] += f; d[1] += n; d[2] += nf
    OC[o] = {a: {s: (v[0], v[1]) for s, v in d.items()} for a, d in c.items()}
    if any(v[1] != N1 for d in c.values() for v in d.values()): bad.append((o, "n != 2560"))
    nfin = sum(v[2] for d in c.values() for v in d.values())
    if nfin: print(f"   note: raw_{o} has {nfin} non-finite blk_err@16 blocks (counted as failures)")
chk("C1 26 original raws: 448 chunks each = 7 SNR x skip 0..2520 step 40 (no hole / overlap), n = 2560 per point", not bad, str(bad[:3]))
print(f"   original raws' run|git: " + ", ".join(f"{o}:{sorted({x['git'] for x in OBY[o]})}" for o in ORIGS))

# the 76 redrawn curves (§0.1 / §3): group, tag, arm, orig raw
GROUPS = [("D2 C2 (Sparse specular 8×4)", TAGS[0:3]), ("D3 (S2c) C2", TAGS[3:6]), ("SV8e C2", TAGS[6:9]), ("UMi28 C2", TAGS[9:12]),
          ("MIX3 C2", TAGS[12:15]), ("D2 C2 회전 15°", TAGS[15:18]), ("D2 C2 회전 30°", TAGS[18:21]), ("D2 C6 (Sparse specular 16×4)", TAGS[21:24])]
GOF = {t: g for g, ts in GROUPS for t in ts}
CURVES = []
for r in ROWS:
    for a in r["ARMS"].split():
        if a == "R5-genie" and r["REF"] != "-": continue
        src = next((o for o in r["ORIG"].split(",") if a in OC[o] and all(s in OC[o][a] for s in (3.0,) + SN)), None)
        assert src, (r["TAG"], a)
        CURVES.append((GOF[r["TAG"]], r["TAG"], a, src))
chk("C2 redrawn curves = 76 (D2 C2 6, D3/SV8e/UMi28/MIX3 12 each, rotation 8 each, D2 C6 6)", len(CURVES) == 76 and
    [sum(1 for c in CURVES if c[0] == g) for g, _ in GROUPS] == [6, 12, 12, 12, 12, 8, 8, 6], str([sum(1 for c in CURVES if c[0] == g) for g, _ in GROUPS]))

# ====================================================================== D. controls
def cmp_arms(new, refs, arms, nan_equal=True):
    fs = sorted(glob.glob(new + "/D2_*.npz")); n = 0; bad = []; other = set()
    for f in fs:
        b = os.path.basename(f)
        ys = [np.load(os.path.join(r, b)) for r in refs if os.path.exists(os.path.join(r, b))]
        with np.load(f) as z:
            for a in arms:
                y = next((y for y in ys if f"{a}|blk_err" in y.files), None)
                if y is None: bad.append((b, a, "no ref")); continue
                for q in KEYS_RAW:
                    k = f"{a}|{q}"; n += 1
                    if k not in z.files or k not in y.files or z[k].shape != y[k].shape or not np.array_equal(z[k], y[k], equal_nan=True):
                        bad.append((b, k))
            if len(refs) == 1 and ys:
                y = ys[0]
                for k in sorted(set(z.files) | set(y.files)):
                    try:
                        same = k in z.files and k in y.files and z[k].shape == y[k].shape and (
                            np.array_equal(z[k], y[k], equal_nan=True) if z[k].dtype.kind in "fc" else np.array_equal(z[k], y[k]))
                    except Exception:
                        same = False
                    if not same: other.add(k)
        for y in ys: y.close()
    return len(fs), n, bad, other
print("\n# D. controls")
ctl_mine, ctl_file = {}, {}
bad = []
for r in ROWS:
    c = r["TAG"].replace("FH", "FHC", 1); arms = r["ARMS"].split()
    nf, n, b, _ = cmp_arms(f"raw_{c}", [f"raw_{o}" for o in r["ORIG"].split(",")], arms)
    ctl_mine[c] = (nf, n, len(b))
    txt = open(f"{RV}/{c}_control.txt").read()
    m = re.search(r"(\d+) chunk files \(expected (\d+)\).*?(\d+) \(chunk, arm, key\) comparisons, (\d+) differ", txt)
    ctl_file[c] = (int(m[1]), int(m[3]), int(m[4])) if m else None
    if nf != 4 or b or ctl_file[c] != (nf, n, 0) or not txt.rstrip().endswith("CONTROL: OK"): bad.append((c, ctl_mine[c], ctl_file[c], b[:2]))
chk("D1 24 receiver controls: raw_FHC* vs ORIG, every arm x KEYS_RAW bit-identical (NaN = NaN), 4 chunks each; counts = *_control.txt; verdict OK",
    not bad, str(bad[:3]))
print(f"   total (chunk, arm, key) comparisons FHC vs ORIG: {sum(v[1] for v in ctl_mine.values())}, differ {sum(v[2] for v in ctl_mine.values())}")
# ZZ (new container) vs FHC (old container)
bad = []; tot = 0; oth = set(); okf = 0
for r in ROWS:
    c = r["TAG"].replace("FH", "FHC", 1); zt = "ZZ" + r["TAG"][2:]
    nf, n, b, other = cmp_arms(f"raw_{zt}", [f"raw_{c}"], r["ARMS"].split()); tot += n; oth |= other
    txt = open(f"{D}/envchk/cmp_{zt}.txt").read()
    m = re.search(r"(\d+) \(chunk, arm, key\) comparisons, (\d+) differ", txt)
    okf += "ENVCHK: OK" in txt.split("\n")
    if nf != 4 or b or not m or (int(m[1]), int(m[2])) != (n, 0): bad.append((zt, nf, n, b[:2], m and m.groups()))
chk("D2 environment check: 24 raw_ZZ* vs raw_FHC*, arms x KEYS_RAW identical; cmp_ZZ*.txt counts agree; ENVCHK: OK x 24", not bad and okf == 24, str(bad[:3]))
chk("D3 §6.1 '비교 2632, 다름 0; 다른 키 [meta|em_sec_note]' = recomputed", tot == 2632 and sorted(oth) == ["meta|em_sec_note"], f"{tot}, other keys {sorted(oth)}")
# ALD estimator controls
bad = []
for t in ("a", "b"):
    A = np.load(f"results/ald/ald_FHCXAROT{t}B16e4k.npz"); B = np.load(f"results/ald/ald_XAROT{t}B16e4k.npz")
    same = all(A[k].shape == B[k].shape and np.array_equal(A[k], B[k]) for k in ("hhat", "b", "v"))
    mx = max(float(np.max(np.abs(A[k] - B[k]))) for k in ("hhat", "b", "v"))
    txt = open(f"{RV}/FHCXAROT{t}B16e4k_aldcontrol.txt").read()
    if not same or A["hhat"].shape != (7, 2560, 32) or mx != 0 or "CONTROL-ALD: OK" not in txt: bad.append((t, same, A["hhat"].shape, mx))
    print(f"   ALD control {t}: hhat {A['hhat'].shape} b {B['b'].shape} v {B['v'].shape}, identical {same}, max|diff| {mx}; keys {sorted(A.files)}")
chk("D4 2 ALD estimator controls: hhat (7, 2560, 32), b, v bit-identical to the original test estimates; file says CONTROL-ALD: OK", not bad, str(bad))

# ====================================================================== E. count tables (fighs_<TAG>.txt) and the §6.1 tables
print("\n# E. count tables")
TAB = {}
bad, bad_w, nrow, nw, heads = [], [], 0, 0, set()
for r in ROWS:
    t = r["TAG"]; tb = {}
    for l in open(f"{RV}/fighs_{t}.txt"):
        if l.startswith("# run_fighs16e4"):
            heads.add(re.search(r"load_raw warnings (\d+)", l)[1]); continue
        m = re.match(r"SNR ([+-]\d+)\s+(\S+)\s+(\d+) / (\d+)\s+BLER (\S+)\s+95% \[(\S+), (\S+)\]\s*$", l)
        if not m: continue
        s, a, f, n = float(m[1]), m[2], int(m[3]), int(m[4]); tb[(s, a)] = (f, n, m[5], m[6], m[7]); nrow += 1
        want = COUNTS1[t][s] if a == "R0-pilot@1" else COUNTS[t].get(a, {}).get(s)
        if want is None or (f, n) != (want, N2): bad.append((t, s, a, (f, n), want))
        lo, hi = wilson(f, n); nw += 1
        if (f"{f / n:.2e}", f"{lo:.2e}", f"{hi:.2e}") != (m[5], m[6], m[7]): bad_w.append((t, s, a, m[5:8], f"{f / n:.2e} {lo:.2e} {hi:.2e}"))
    TAB[t] = tb
    want_rows = 4 * (len(r["ARMS"].split()) + ("R0-pilot" in r["ARMS"]))
    if len(tb) != want_rows: bad.append((t, "rows", len(tb), want_rows))
chk(f"E1 24 count tables: every (SNR, arm) failures / n = raw recount ({nrow} rows incl. R0-pilot@1 = iteration 1); row count = 4 x (arms + alias)", not bad, str(bad[:4]))
chk(f"E2 count tables: BLER and 95% Wilson strings re-formatted from own Wilson ({nw} cells)", not bad_w, str(bad_w[:3]))
chk("E3 count-table headers: load_raw warnings 0 in all 24", heads == {"0"}, str(heads))
# §6.1 report tables
bad = []; n61 = 0; genie_lines = []
for l in S61:
    m = re.match(r"^\| (\S+) \((FH\w+)\) \| (\d+) · (\S+) \| (\d+) · (\S+) \| (\d+) · (\S+) \| (\d+) · (\S+) \|$", l)
    if m:
        a, t = m[1], m[2]
        for i, s in enumerate(SN):
            f, b = int(m[3 + 2 * i]), m[4 + 2 * i]; n61 += 1
            want = COUNTS1[t][s] if a == "R0-pilot@1" else COUNTS[t][a][s]
            if f != want or b != f"{want / N2:.2e}": bad.append((t, a, s, f, b, want))
        continue
    m = re.match(r"^\| R5-genie \((.*?): 같은 수\) \| (\d+) · (\S+) \| (\d+) · (\S+) \| (\d+) · (\S+) \| (\d+) · (\S+) \|$", l)
    if m:
        tags = [x.strip() for x in m[1].split(",")]; genie_lines.append(tags)
        vals = {tuple(COUNTS[t]["R5-genie"][s] for s in SN) for t in tags}
        if len(vals) != 1: bad.append(("genie not same", tags, vals))
        for i, s in enumerate(SN):
            f, b = int(m[2 + 2 * i]), m[3 + 2 * i]; n61 += 1; want = COUNTS[tags[0]]["R5-genie"][s]
            if f != want or b != f"{want / N2:.2e}": bad.append((tags, s, f, b, want))
chk(f"E4 §6.1 report tables: every 'failures · BLER' cell = raw recount ({n61} cells) and the 8 '같은 수' genie lines are truly equal across their tags",
    not bad and len(genie_lines) == 8 and sum(len(g) for g in genie_lines) == 24, str(bad[:4]))
exp_cells = sum(4 * (len(r["ARMS"].split()) + ("R0-pilot" in r["ARMS"])) for r in ROWS) - 4 * 16   # genie rows merged: 24 -> 8 lines
chk("E5 §6.1 report tables cover every (arm, SNR) of the 24 count tables (genie merged per group)", n61 == exp_cells, f"{n61} vs {exp_cells}")

# ====================================================================== F. originals, cells.tsv, §0.4, predictions, Fisher
print("\n# F. predictions")
cells = []           # (group, tag, arm, orig, snr, f1, lo, hi, f2, p, inside)
for g, t, a, src in CURVES:
    for s in SN:
        f1, n1 = OC[src][a][s]; lo, hi = wilson(f1, n1); f2 = COUNTS[t][a][s]; p = f2 / N2
        cells.append((g, t, a, src, s, f1, n1, lo, hi, f2, p, lo <= p <= hi))
inside = sum(c[-1] for c in cells)
chk("F1 prediction 1: 281/304 cells inside the original 95% Wilson interval (closed), 0.9243 >= 0.90",
    len(cells) == 304 and inside == 281, f"{inside}/{len(cells)} = {inside / len(cells):.4f}")
# cells.tsv
tsv = [l.rstrip("\n").split("\t") for l in open(f"{AUD}/fighs_cells.tsv")][1:]
bad = []
for row, c in zip(tsv, cells):
    g, t, a, src, s, f1, n1, lo, hi, f2, p, ins = c
    want = [g, t, a, src, f"{s:.6e}", str(f1), str(n1), f"{lo:.6e}", f"{hi:.6e}", str(f2), str(N2), f"{p:.6e}", str(ins)]
    if row != want: bad.append((row, want))
chk("F2 fighs_cells.tsv: 304 rows = (group, tag, arm, orig raw, SNR, orig fail/n, Wilson lo/hi, new fail/n, BLER, inside) recomputed", len(tsv) == 304 and not bad, str(bad[:2]))
# per-group table in §6.1
bad = []
for l in S61:
    m = re.match(r"^\| (.+?) \| (\d+) \| (\d+) \| (\d+) \|$", l)
    if m and m[1] in GOF.values():
        cc = [c for c in cells if c[0] == m[1]]
        if (int(m[2]), int(m[3]), int(m[4])) != (len({(c[1], c[2]) for c in cc}), len(cc), sum(c[-1] for c in cc)): bad.append((m[1], m.groups()))
chk("F3 §6.1 prediction-1 group table (curves, cells, inside) x 8", not bad, str(bad))
# outside list
out61 = []
for l in S61:
    m = re.match(r"^- (.+?) · (\S+) · ([+-]\d+) dB · (\d+) · \[(\S+), (\S+)\] · (\d+) · (\S+)$", l)
    if m: out61.append((m[1], m[2], float(m[3]), int(m[4]), m[5], m[6], int(m[7]), m[8]))
mine = [(c[0], c[2], c[4], c[5], f"{c[7]:.2e}", f"{c[8]:.2e}", c[9], f"{c[10]:.2e}") for c in cells if not c[-1]]
chk("F4 §6.1 list of the 23 outside cells = recomputed (order, counts, intervals, BLER)", out61 == mine and len(mine) == 23, f"{len(out61)} listed, {len(mine)} recomputed; diff {[x for x in out61 if x not in mine][:2]}")
# §0.4 original counts
NM = {"R0-pilot": "R0-pilot", "R1": "R1-turbo", "R2": "R2-ours-G", "R3": "R3-bigamp", "b\\*": "M-ours-bstar", "V1": "M-ours-dscore-C-V1",
      "genie": "R5-genie", "SBL-loop": "SBL-loop", "SBL-pilot": "SBL-pilot", "OMP-pilot": "OMP-pilot", "V1-pilot": "V1-pilot",
      "bstar-pilot": "bstar-pilot", "ALD-pilot": "ALD-pilot"}
G04 = {"D2 C2 (새 arm 만)": GROUPS[0][0], "D2 C6 (새 arm 만)": GROUPS[7][0], "D3": GROUPS[1][0], "SV8e": GROUPS[2][0], "UMi28": GROUPS[3][0],
       "MIX3": GROUPS[4][0], "회전 15°": GROUPS[5][0], "회전 30°": GROUPS[6][0]}
reg04, up04 = {}, set()
for l in reg[:i61]:
    m = re.match(r"^\| ([^|]+?) \| (.*\d+/\d+/\d+/\d+.*) \|\s*$", l)
    if m and m[1].strip() in G04:
        for it in m[2].split(";"):
            q = re.match(r"\s*(\S+) (\d+)/(\d+)/(\d+)/(\d+)( ↑)?", it)
            if q:
                reg04[(G04[m[1].strip()], NM[q[1]])] = tuple(int(q[i]) for i in range(2, 6))
                if q[6]: up04.add((G04[m[1].strip()], NM[q[1]]))
def rising(seq): return [i for i in range(1, len(seq)) if seq[i][0] * seq[i - 1][1] > seq[i - 1][0] * seq[i][1]]   # BLER(i) > BLER(i-1), exact
oc4 = {(g, a): tuple(OC[src][a][s][0] for s in SN) for g, t, a, src in CURVES}
bad = [(k, v, reg04.get(k)) for k, v in oc4.items() if reg04.get(k) != v]
chk("F5 §0.4 original failure counts (+6/+9/+12/+15, n = 2560) = raw recount for all 76 curves", len(reg04) == 76 and not bad, str(bad[:3]))
old_all = {(g, a) for g, t, a, src in CURVES if rising([OC[src][a][s] for s in SN])}
chk("F6 §0.4 ↑ marks = curves with a rising cell in the original counts (15/76)", old_all == up04 and len(up04) == 15, f"{len(old_all)} vs {len(up04)}; diff {sorted(old_all ^ up04)}")
old_up = sorted((g, a) for g, a in old_all if a != "R3-bigamp")
new_up = [(g, a) for g, t, a, src in CURVES if a != "R3-bigamp" and rising([(COUNTS[t][a][s], N2) for s in SN])]
want_old = [("D2 C2 (Sparse specular 8×4)", "SBL-loop"), ("D2 C2 (Sparse specular 8×4)", "SBL-pilot"), ("D2 C2 (Sparse specular 8×4)", "bstar-pilot"),
            ("D3 (S2c) C2", "R5-genie"), ("SV8e C2", "R1-turbo"), ("D2 C2 회전 15°", "R5-genie"), ("D2 C2 회전 30°", "R5-genie"),
            ("D2 C6 (Sparse specular 16×4)", "V1-pilot"), ("D2 C6 (Sparse specular 16×4)", "SBL-loop")]
chk("F7 prediction 2: original 9/70 (the 9 curves listed in §6.1), new 0/70; R3 excluded = 70 curves",
    sorted(old_up) == sorted(want_old) and new_up == [] and sum(1 for c in CURVES if c[2] != "R3-bigamp") == 70, f"old {old_up}, new {new_up}")
# rising-cell table (+3 original -> +6..+15 new), Fisher p
mine = []
for g, t, a, src in CURVES:
    seq = [(3.0, OC[src][a][3.0])] + [(s, (COUNTS[t][a][s], N2)) for s in SN]
    for i in rising([x[1] for x in seq]):
        (s0, lo), (s1, hi) = seq[i - 1], seq[i]
        mine.append((g, a, f"{s0:+.0f} → {s1:+.0f} dB", f"{lo[0]} / {lo[1]}", f"{hi[0]} / {hi[1]}", f"{fisher_p(hi, lo):.2g}",
                     "—  (기록만)" if s0 == 3.0 else ("R3 제외" if a == "R3-bigamp" else "예")))
tab61 = []
for l in S61:
    m = re.match(r"^\| (.+?) \| (\S+) \| ([+-]\d+ → [+-]\d+ dB) \| (\d+ / \d+) \| (\d+ / \d+) \| (\S+) \| (.+?) \|$", l)
    if m and m[1] in GOF.values(): tab61.append(tuple(m.groups()))
chk("F8 §6.1 rising-cell table (8 rows: cells, counts, one-sided Fisher p, label) = recomputed from raw", tab61 == mine and len(mine) == 8,
    f"{len(tab61)} rows vs {len(mine)}; diff {[x for x in tab61 if x not in mine][:2]} / {[x for x in mine if x not in tab61][:2]}")
# prediction 3
p3 = []
for g, tags in GROUPS[1:7]:
    t = tags[0]; pr = [(COUNTS[t]["M-ours-dscore-C-V1"][s], COUNTS[t]["M-ours-bstar"][s]) for s in SN]
    p3.append((g, t, pr, sum(v <= b for v, b in pr)))
tab61 = []
for l in S61:
    m = re.match(r"^\| (.+?) \((FH\w+)\) \| (\d+) : (\d+) \| (\d+) : (\d+) \| (\d+) : (\d+) \| (\d+) : (\d+) \| (\d)/4 \|$", l)
    if m: tab61.append((m[1], m[2], [(int(m[3 + 2 * i]), int(m[4 + 2 * i])) for i in range(4)], int(m[11])))
chk("F9 prediction 3 table (6 datasets x 4 SNR V1 : b*) = raw; total 23/24 (SV8e +12 dB 1 > 0 is the one miss)",
    tab61 == p3 and sum(x[3] for x in p3) == 23 and [x[3] for x in p3] == [4, 3, 4, 4, 4, 4], str(p3))

# ====================================================================== G. run log, runner logs, interruption, manifests, before/, mtimes, git
print("\n# G. logs / narrative")
LOG = open("logs/run_fighs16e4.log", encoding="utf-8").read().split("\n")
def tsl(l):
    m = re.match(r"\[fighs (\d\d)-(\d\d) (\d\d):(\d\d) CDT\]", l)
    return datetime(2026, int(m[1]), int(m[2]), int(m[3]), int(m[4]), tzinfo=CDT) if m else None
starts = [i for i, l in enumerate(LOG) if "start (git" in l]
chk("G1 run log: exactly 2 'start (git 331f6e57)' lines (resume=0 at 10-06 19:30, resume=1 at 10-06 21:15 CDT)", len(starts) == 2 and
    LOG[starts[0]] == "[fighs 10-06 19:30 CDT] start (git 331f6e57) rows: all resume=0 skip0 10000 n 20480 SNR 6 9 12 15" and
    LOG[starts[1]] == "[fighs 10-06 21:15 CDT] start (git 331f6e57) rows: all resume=1 skip0 10000 n 20480 SNR 6 9 12 15")
seg1, seg2 = LOG[starts[0]:starts[1]], LOG[starts[1]:]
chk("G2 segment 1: phase C done 19:38 '24 receiver control(s) OK, 2 ALD estimator control(s) OK'; last timed line = FHD3B16e4 run 20:37; no FIGHS_DONE; no ABORT/INVALID/SKIP/FAILED/rc!=0",
    any(l == "[fighs 10-06 19:38 CDT] phase C done: 24 receiver control(s) OK, 2 ALD estimator control(s) OK" for l in seg1) and
    [l for l in seg1 if tsl(l)][-1].startswith("[fighs 10-06 20:37 CDT] FHD3B16e4 run:") and not any("FIGHS_DONE" in l for l in seg1) and
    not any(re.search(r"ABORT|INVALID|SKIP|FAILED|rc=[1-9]", l) for l in seg1))
chk("G3 segment 2: phase C done 21:16 (same counts); FIGHS_DONE ok=24 fail=0 at 10-07 16:12; no ABORT/INVALID/SKIP/FAILED/rc!=0; resume scan line '0 unreadable'",
    any(l == "[fighs 10-06 21:16 CDT] phase C done: 24 receiver control(s) OK, 2 ALD estimator control(s) OK" for l in seg2) and
    seg2[-2] == "[fighs 10-07 16:12 CDT] FIGHS_DONE ok=24 fail=0" and not any(re.search(r"ABORT|INVALID|SKIP|FAILED|rc=[1-9]", l) for l in seg2) and
    LOG[starts[1] - 1] == "[fighs] resume: 0 unreadable chunk file(s) moved aside" and sum("[fighs] resume:" in l for l in LOG) == 1)
RUN, ACC = {}, {}
for l in seg2:
    m = re.match(r"\[fighs [^\]]+\] (FH\w+) run:", l)
    if m: RUN[m[1]] = tsl(l)
    m = re.match(r"\[fighs [^\]]+\] (FH\w+) acceptance rc=(\d+) \((.*)\)", l)
    if m: ACC[m[1]] = (tsl(l), int(m[2]), m[3].strip())
RUN1 = {m[1]: tsl(l) for l in seg1 for m in [re.match(r"\[fighs [^\]]+\] (FH\w+) run:", l)] if m}
ACC1 = {m[1]: tsl(l) for l in seg1 for m in [re.match(r"\[fighs [^\]]+\] (FH\w+) acceptance rc=0", l)] if m}
chk("G4 segment 1 ran rows 1-3 to acceptance (rc=0) and started row 4; segment 2 ran/accepted all 24 (rc=0) in registered order",
    list(RUN1) == TAGS[:4] and list(ACC1) == TAGS[:3] and list(RUN) == TAGS and list(ACC) == TAGS and all(v[1] == 0 for v in ACC.values()))
# runner logs
def segs(tag):
    out = []
    for l in open(f"logs/run_D2_{tag}.log", encoding="utf-8", errors="replace"):
        m = re.match(r"# run_fighs16e4 git (\w+) (\S+ \S+) CDT resume=(\d)", l)
        if m: out.append([m[2], int(m[3]), 0, 0, None, m[1]]); continue
        if not out: continue
        if re.match(r"\d+/\d+ done ", l): out[-1][2] += 1
        elif re.match(r"\d+/\d+ exists", l): out[-1][3] += 1
        m = re.search(r"\[run\] finished in ([\d.]+) min", l)
        if m: out[-1][4] = float(m[1])
    return out
SEG = {t: segs(t) for t in TAGS}
EST = {m[1]: m[2].strip() for l in reg[:i61] for m in [re.match(r"^\| \d+ \| (FH\w+) \|.*\| ([^|]+) \| [^|]*\|\s*$", l)] if m}
bad = []
rows61 = {}
for l in S61:
    m = re.match(r"^\| (\d+) \| (FH\w+) \| (.*?) \| (.*?) \| (.*?) \| (\d+) \| (.*?) \|$", l)
    if m: rows61[m[2]] = m
for i, r in enumerate(ROWS):
    t = r["TAG"]; sg = SEG[t]
    s = "; ".join(f"{d} · r{rs} · {nd} · {ne} · {'미완' if fm is None else fm}" for d, rs, nd, ne, fm, g in sg)
    a = ACC[t]; acc = open(f"{RV}/{t}_accept.txt").read()
    v = " / ".join(x.strip() for x in acc.split("\n") if x.startswith("ACCEPT"))
    rz = re.search(r"raised trials per arm \(= failures, report only\) (.*)", acc)[1].strip()
    want = (str(i + 1), t, s, f"{a[0]:%m-%d %H:%M} rc={a[1]}", v, rz, EST[t])
    got = rows61[t].groups()
    if got != want: bad.append((t, got, want))
    # consistency of the runner log with the run log and the raw
    if {g for *_, g in sg} != {"331f6e57"} or sg[-1][2] + sg[-1][3] != 2048 or sum(x[2] for x in sg) != 2048: bad.append((t, "runner log chunks", sg))
    if ts_cdt(sg[-1][0]) != RUN[t].replace(second=0): bad.append((t, "resume header time != run log", sg[-1][0], RUN[t]))
    if v != f"ACCEPT: OK -- {t} / ACCEPT (f): OK" or rz != "0" or "run|git ['331f6e57']" not in acc: bad.append((t, "accept file", v, rz))
    if a[2] != f"ACCEPT: OK -- {t} ACCEPT (f): OK": bad.append((t, "log acceptance text", a[2]))
chk("G5 §6.1 per-row table (24 rows: runner segments / done / exists / minutes, acceptance time+rc, accept-file verdicts, raised 0, §1b estimate) = logs + files",
    not bad, str(bad[:2]))
mins = {t: [fm for *_, fm, g in SEG[t] if fm is not None and fm >= 0.5] for t in TAGS}
tot = sum(x for v in mins.values() for x in v)
chk("G6 runner minutes: sum of 'finished in' (segments >= 0.5 min) = 1166.4", abs(tot - 1166.4) < 0.05, f"{tot:.1f}")
num = lambda x: int(re.search(r"\d+", x)[0])
gm = {g: (sum(x for t in ts for x in mins[t]), sum(num(EST[t]) for t in ts)) for g, ts in GROUPS}
want_gm = {"D2 C2 (Sparse specular 8×4)": (56.1, 57), "D3 (S2c) C2": (129.2, 146), "SV8e C2": (69.8, 78), "UMi28 C2": (297.5, 248), "MIX3 C2": (302.7, 250),
           "D2 C2 회전 15°": (45.8, 51), "D2 C2 회전 30°": (46.0, 51), "D2 C6 (Sparse specular 16×4)": (219.3, 255)}
chk("G7 §6.1 group runner minutes and 'estimate' column = sums of per-row minutes / per-row §1b integers",
    all(abs(gm[g][0] - want_gm[g][0]) < 0.05 and gm[g][1] == want_gm[g][1] for g in gm), str({g: (round(v[0], 1), v[1]) for g, v in gm.items()}))
print("   note: the registration's own §1b group table reads 58 / 145 / 78 / 247 / 250 / 51 / 51 / 256 (its per-row values were rounded differently); §6.1's column is the per-row sum")
t0, t1, tdone = tsl(LOG[starts[0]]), tsl(LOG[starts[1]]), tsl(seg2[-2])
chk("G8 durations: resume -> FIGHS_DONE 18.95 h, first start -> FIGHS_DONE 20.70 h", abs((tdone - t1).total_seconds() / 3600 - 18.95) < 0.01 and
    abs((tdone - t0).total_seconds() / 3600 - 20.70) < 0.01, f"{(tdone - t1).total_seconds() / 3600:.2f} / {(tdone - t0).total_seconds() / 3600:.2f}")
# control files (§6.1 table) and manifests
bad = []
ctab = {}
for l in S61:
    m = re.match(r"^\| (FHC\w+) \((control|aldcontrol)\) \| (.*) \| (CONTROL[^|]*) \|$", l)
    if m: ctab[(m[1], m[2])] = (m[3], m[4])
for r in ROWS:
    c = r["TAG"].replace("FH", "FHC", 1)
    for suf in ("control", "aldcontrol"):
        p = f"{RV}/{c}_{suf}.txt"
        if not os.path.exists(p):
            if (c, suf) in ctab: bad.append((c, suf, "listed but no file"))
            continue
        ls = [x for x in open(p).read().split("\n") if x.strip()]
        if ctab.get((c, suf)) != (ls[0][:230].replace("|", "\\|"), ls[-1]): bad.append((c, suf, ctab.get((c, suf)), ls[0][:60]))
chk("G9 §6.1 control table = first / last line of the 24 control + 2 aldcontrol files (26 rows)", not bad and len(ctab) == 26, str(bad[:2]))
bad = []
mtab = {}
for l in S61:
    m = re.match(r"^\| (FH\w+) \| (\w+) \| (\d+) \| (\w+) \| `(.*?)` → `(.*?)` \| (.*?) · (.*?) \| (\d+)\.\.(\d+) \| (.*?) \| (\w+) · (.*?) \|$", l)
    if m: mtab[m[1]] = m.groups()[1:]
for r in ROWS:
    t = r["TAG"]; mf = json.load(open(f"{RV}/run_manifest_{t}.json")); ck = mf.get("stagec_checkpoint") or {}; tr = mf["trial_stream"]
    lk = f"results/gmm_fits_D2_{t}"
    want = (mf["git_commit"], str(mf["n_raw_files"]), mf["config_hash"], os.path.basename(lk), os.readlink(lk), ck.get("sha256_16", "—"),
            str(mf.get("stagec_ckpt_id", "—")).replace("|", "\\|"), str(tr["skip_min"]), str(tr["skip_max_end"]), ", ".join(mf["arms"]), mf["versions"]["host"], mf["written"])
    if mtab.get(t) != want: bad.append((t, mtab.get(t), want))
    if mf["git_commit"] != "331f6e57" or mf["n_raw_files"] != 2048 or os.readlink(lk) != f"gmm_fits_D2_{r['BF']}" or sorted(mf["arms"]) != sorted(r["ARMS"].split()):
        bad.append((t, "manifest content"))
    if r["CK"] != "-" and ck.get("sha256_16") != r["SHA"]: bad.append((t, "manifest ckpt sha"))
    # written (KST) vs acceptance time (CDT): manifest is written just before eval_accept
    w = datetime.strptime(mf["written"], "%Y-%m-%d %H:%M:%S KST").replace(tzinfo=KST)
    if not (timedelta(0) <= ACC[t][0] + timedelta(minutes=1) - w <= timedelta(minutes=3)): bad.append((t, "written vs acceptance", mf["written"], ACC[t][0]))
chk("G10 §6.1 manifest table (24 rows) = run_manifest_<TAG>.json + fits links; git 331f6e57, 2048 files, arms, ckpt sha, link -> registered fits; written (KST) <= acceptance (CDT) within 3 min",
    not bad and len(mtab) == 24, str(bad[:2]))
# before/ vs now
bs = sorted(os.listdir(f"{D}/before")); same, diff = 0, []
for f in bs:
    if f in ("run_fighs16e4.log", "fighs_tmux.out"): continue
    cur = f"results/ald/{f}" if f.startswith("ald_") else f"{RV}/{f}"
    (same := same + 1) if sha(f"{D}/before/{f}") == sha(cur) else diff.append(f)
b256 = {l.split()[1]: l.split()[0] for l in open(f"{D}/before.sha256")}
chk("G11 before/: 39 files (= before.sha256 entries, recover.log 'backup: 39'); excluding the 2 appended logs: 34 identical now, 3 manifests differ",
    len(bs) == 39 and all(b256[f] == sha(f"{D}/before/{f}") for f in bs) and same == 34 and diff == ["run_manifest_FHB16e4k.json", "run_manifest_FHPILB16e4k.json", "run_manifest_FHSPB16e4k.json"],
    f"{len(bs)} files, same {same}, diff {diff}")
bad = []
for f in diff:
    a, b = json.load(open(f"{D}/before/{f}")), json.load(open(f"{RV}/{f}"))
    ks = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
    if ks != ["versions", "written"] or a["versions"]["host"] != "0695aede856d" or b["versions"]["host"] != "262d04c812cc" or \
            {k: v for k, v in a["versions"].items() if k != "host"} != {k: v for k, v in b["versions"].items() if k != "host"}: bad.append((f, ks))
    line = next((l for l in S61 if l.strip().startswith(f"- `{f}`")), "")
    if f'written: "{a["written"]}" → "{b["written"]}"' not in line or '"host": "0695aede856d"' not in line: bad.append((f, "§6.1 line", line[:80]))
chk("G12 the 3 differing manifests differ only in versions.host (0695aede856d -> 262d04c812cc) and written; §6.1 quotes both values", not bad, str(bad))
chk("G13 ALD control estimates: sha256[:16] before = now (be03f8de6de67c10 / 6534bb27258fa42b) and mtimes 10-07 11:15:40 / 11:16:15 KST (resume recomputed them)",
    sha(f"{D}/before/ald_FHCXAROTaB16e4k.npz")[:16] == sha("results/ald/ald_FHCXAROTaB16e4k.npz")[:16] == "be03f8de6de67c10" and
    sha(f"{D}/before/ald_FHCXAROTbB16e4k.npz")[:16] == sha("results/ald/ald_FHCXAROTbB16e4k.npz")[:16] == "6534bb27258fa42b" and
    f"{datetime.fromtimestamp(os.path.getmtime('results/ald/ald_FHCXAROTaB16e4k.npz'), KST):%m-%d %H:%M:%S}" == "10-07 11:15:40" and
    f"{datetime.fromtimestamp(os.path.getmtime('results/ald/ald_FHCXAROTbB16e4k.npz'), KST):%m-%d %H:%M:%S}" == "10-07 11:16:15")
hs = {}
for t in ("a", "b"):
    f = f"results/ald/ald_XAROT{t}B16e4k_hisnr.npz"; z = np.load(f); pv = json.loads(str(z["prov"]))
    hs[t] = (sha(f)[:16], f"{datetime.fromtimestamp(os.path.getmtime(f), KST):%m-%d %H:%M:%S}", pv["git"], int(z["skip"]) if "skip" in z.files else None, int(z["hhat"].shape[1]), z["hhat"].shape, sorted(z.files))
chk("G14 new-trial ALD estimates: sha d962c0b6cf7e47a6 / bc23a889d2521ec0, mtimes 10-08 01:36:09 / 02:28:07 KST, prov git 331f6e57 (and skip 10000, n 20480)",
    hs["a"][:3] == ("d962c0b6cf7e47a6", "10-08 01:36:09", "331f6e57") and hs["b"][:3] == ("bc23a889d2521ec0", "10-08 02:28:07", "331f6e57") and
    all(v[3] == 10000 and v[4] == 20480 for v in hs.values()), str(hs))
# recover.log / figs_pushed / paper branch
rl = open(f"{D}/recover.log").read().split("\n")
chk("G15 recover.log: start 21:08:00 (host 262d04c812cc, driver 580.178.04, git 331f6e57), backup 39, envchk done 21:15:03 '24/24', resume call, exit rc=0 16:12:53; §6.1 quotes it verbatim",
    all(l in S61 or ("    " + l) in S61 for l in rl if l.strip()) and "host 262d04c812cc, driver 580.178.04" in rl[0] and "24/24 rows" in rl[3] and "rc=0" in rl[5])
fp = [l.rstrip() for l in open(f"{D}/figs_pushed.txt") if not l.startswith("#")]
chk("G16 figs_pushed.txt (7 lines) quoted verbatim in §6.1", all(("    " + l) in S61 for l in fp) and len(fp) == 7)
bad = []
for l in fp:
    fig, when, commit, note = [x.strip() for x in l.split("|")]
    cd = sh(f"cd /home/HTJ/t2 && TZ=America/Chicago git log -1 --format=%cd --date=format-local:'%Y-%m-%d %H:%M CDT' {commit}")
    br = sh(f"cd /home/HTJ/t2 && git branch --contains {commit} --format='%(refname:short)'").split()
    if cd != when or "paper" not in br or "main" in br: bad.append((fig, commit, cd, br))
chk("G17 the 6 paper-branch commits in figs_pushed.txt exist, their commit times = the listed times, on branch paper and not on main", not bad, str(bad))
# mtimes of the new-raw chunks vs the interruption / resume
cut = datetime(2026, 10, 6, 20, 38, 41, tzinfo=CDT); res = datetime(2026, 10, 6, 21, 15, tzinfo=CDT)
bad = []
for i, r in enumerate(ROWS):
    t = r["TAG"]; lo, hi = cdt(MT[t][0]), cdt(MT[t][1])
    if i < 3 and not (RUN1[t] - timedelta(minutes=1) <= lo and hi <= ACC1[t] + timedelta(minutes=1) and hi < cut): bad.append((t, lo, hi))
    if i >= 3 and not (RUN[t] - timedelta(minutes=1) <= lo and hi <= ACC[t][0] + timedelta(minutes=1) and lo > res): bad.append((t, lo, hi))
gap = [(o["tag"], cdt(o["mtime"])) for o in NEW if cut - timedelta(minutes=2) < cdt(o["mtime"]) < res + timedelta(minutes=4)]
chk("G18 chunk mtimes: rows 1-3 written 19:38-20:37 CDT (before the container re-creation 20:38:41), rows 4-24 after 21:19 CDT within their own run..acceptance window; nothing written to raw_FH* between the last pre-interruption chunk and the resume",
    not bad and not gap, f"{bad[:2]} gap {gap[:3]}")
print("   per-tag chunk mtime windows (CDT): " + "; ".join(f"{t} {cdt(MT[t][0]):%m-%d %H:%M}..{cdt(MT[t][1]):%H:%M}" for t in TAGS))
fc = [os.path.getmtime(p) for p in glob.glob("raw_FHC*/D2_*.npz")]; zz = [os.path.getmtime(p) for p in glob.glob("raw_ZZ*/D2_*.npz")]
chk("G19 control raws raw_FHC* (96 chunks) written 19:30-19:38 CDT in the old container only (no chunk written at the resume); raw_ZZ* (96) written 21:08-21:15 CDT",
    len(fc) == 96 and cdt(min(fc)) >= t0 and cdt(max(fc)) <= datetime(2026, 10, 6, 19, 38, 59, tzinfo=CDT) and len(zz) == 96 and
    cdt(min(zz)) >= datetime(2026, 10, 6, 21, 8, tzinfo=CDT) and cdt(max(zz)) <= datetime(2026, 10, 6, 21, 15, 3, tzinfo=CDT),
    f"FHC {cdt(min(fc)):%H:%M:%S}..{cdt(max(fc)):%H:%M:%S}, ZZ {cdt(min(zz)):%H:%M:%S}..{cdt(max(zz)):%H:%M:%S}")
bad = []
for r in ROWS:
    c = r["TAG"].replace("FH", "FHC", 1); sg = segs(c) if os.path.exists(f"logs/run_D2_{c}.log") else []
    hdr = [l for l in open(f"logs/run_D2_{c}.log") if l.startswith("# run_fighs16e4")]
    if len(hdr) != 2 or "resume=0" not in hdr[0] or "resume=1" not in hdr[1]: bad.append((c, hdr))
    txt = open(f"logs/run_D2_{c}.log").read()
    if txt.count(" done ") != 4 or txt.count(" exists") != 4: bad.append((c, txt.count(" done "), txt.count(" exists")))
chk("G20 24 control runner logs: 2 headers (control resume=0 at 19:31, resume=1 at 21:16), 4 done + 4 exists (resume skipped the chunks)", not bad, str(bad[:2]))
chk("G21 FHD3B16e4 first segment: header 20:37 CDT, 0 done, 0 exists, no 'finished in'; second segment 21:19 CDT 2048 done, 72.5 min",
    SEG["FHD3B16e4"][0][:5] == ["2026-10-06 20:37", 0, 0, 0, None] and SEG["FHD3B16e4"][1][:5] == ["2026-10-06 21:19", 1, 2048, 0, 72.5])
# git: frozen part unchanged, HEAD, cleanliness
old = subprocess.run("cd /home/HTJ/t2 && git show 331f6e57:conf/results/review_next/NEXT_EXPERIMENTS_FIGHS16e4.md", shell=True, capture_output=True, text=True).stdout.split("\n")
chk("G22 registration: lines 1..204 (through '## 6. 결과 (이 절은 추가만 한다)') byte-identical to commit 331f6e57; §6.1 is pure addition",
    len(old) == 205 and old[-2] == "## 6. 결과 (이 절은 추가만 한다)" and reg[:204] == old[:204] and len(reg) > 204, f"frozen {len(old) - 1} lines, now {len(reg) - 1}")
chk("G23 HEAD = 331f6e57 (commit 2026-10-06 19:30 CDT), 0 commits after it, conf/code + Demo clean, DECISIONS.md clean",
    sh("git rev-parse --short HEAD") == "331f6e57" and sh("cd /home/HTJ/t2 && git log --oneline 331f6e57..HEAD") == "" and
    sh("cd /home/HTJ/t2 && git status --porcelain conf/code Demo") == "" and sh("git status --porcelain DECISIONS.md") == "",
    sh("cd /home/HTJ/t2 && TZ=America/Chicago git log -1 --format=%cd --date=format-local:'%Y-%m-%d %H:%M CDT' 331f6e57"))
pngs = ["F16_headline_budget", "F17_codim_C6", "F20_channel_models", "F21_all_baselines", "F22_pilot_only", "F24_nonstationary_D2C2", "F25_nonstationary_all",
        "F26_drift_spatial", "F31_sparse_baselines"]
dif = [p for p in pngs if subprocess.run(f"cd /home/HTJ/t2 && git diff --quiet paper -- conference/figures/{p}.png", shell=True).returncode != 0]
chk("G24 the 9 PNGs on the paper branch = the regenerated working-tree PNGs (git diff --quiet paper)", not dif, str(dif))
print("   tracked files modified vs 331f6e57 (git status ' M', non-log): " + sh("cd /home/HTJ/t2 && git status --porcelain | grep '^ M' | grep -v 'conf/logs/' | cut -c4- | tr '\\n' ' '"))
print("   untracked figure code / records: " + sh("cd /home/HTJ/t2 && git status --porcelain conference/ | grep '^??' | cut -c4- | tr '\\n' ' '"))

# ====================================================================== H. figure records
print("\n# H. figure records")
def parse_table(path):
    out, s = {}, None
    for l in open(path):
        h = re.match(r"SNR ([+-]\d+) dB, n = \d+:", l); m = re.match(r"(?:SNR ([+-]\d+))?\s+(\S+)\s+(\d+) / (\d+)\s+BLER", l)
        if h: s = float(h[1])
        elif m: s = float(m[1]) if m[1] else s; out[(s, m[2])] = (int(m[3]), int(m[4]))
    return out
HTAB = {"HSB16e4k": parse_table(f"{RV}/hisnr_HSB16e4k.txt"), "HSNR16": parse_table(f"{RV}/hisnr_HSNR16.txt")}
ORIG_OF = {("HSB16e4k", a): "B16e4k" for a in ("R1-turbo", "R2-ours-G", "R3-bigamp", "M-ours-bstar", "M-ours-dscore-C-V1", "R5-genie")}
ORIG_OF.update({("HSNR16", a): "NR16B16e4" for a in ("R1-turbo", "R2-ours-G", "R3-bigamp", "M-ours-bstar", "M-ours-dscore-C-V1", "R5-genie")})
for g, t, a, src in CURVES: ORIG_OF[(t, a)] = src
for r in ROWS:                                          # genie copies of dependent rows: same original as the group's first row genie
    if r["REF"].startswith("FH"): ORIG_OF[(r["TAG"], "R5-genie")] = ORIG_OF[(r["REF"], "R5-genie")]
bad, nk, nr, rl61 = [], 0, 0, []
for l in S61:
    m = re.match(r"^    - (R\S+ @16 .*)$", l)
    if m: rl61.append(re.sub(r"\s+", " ", m[1]))
recs = {}
for nn in (16, 17, 20, 21, 22, 24, 31):
    p = f"/home/HTJ/t2/conference/figures/records/paper_f{nn}.txt"; L = open(p, encoding="utf-8").read().split("\n")
    recs[nn] = L
    if any(x in "\n".join(L) for x in ("FALLBACK", "WARNING", "n = 2560 over the whole range")): bad.append((nn, "fallback/warning/n2560 text"))
    if sum(l.startswith("FIGHS16e4 merge (REPORT-ONLY") for l in L) != 1: bad.append((nn, "merge block count"))
    for l in L:
        m = re.match(r"^    (\S+)\s+@16\s+(\d+)/(\d+) (\d+)/(\d+) (\d+)/(\d+) (\d+)/(\d+)\s+\((raw_(\w+))\)(?:\s+rising: (.*))?$", l)
        if not m: continue
        a, tag = m[1], m[11]; kn = [(int(m[2 + 2 * i]), int(m[3 + 2 * i])) for i in range(4)]; nk += 4
        tab = HTAB[tag] if tag in HTAB else {k: (v[0], v[1]) for k, v in TAB[tag].items()}
        if any(tab.get((s, a)) != kn[i] for i, s in enumerate(SN)) or any(n != N2 for _, n in kn): bad.append((nn, a, tag, kn, [tab.get((s, a)) for s in SN]))
        if tag not in HTAB and any(COUNTS[tag][a][s] != kn[i][0] for i, s in enumerate(SN)): bad.append((nn, a, tag, "raw"))
        o = ORIG_OF[(tag, a)]
        seq = [OC[o][a][s] for s in (-3.0, 0.0, 3.0)] + kn; xs = [-3, 0, 3, 6, 9, 12, 15]
        up = [f"{xs[i - 1]:+.0f}->{xs[i]:+.0f} dB p={fisher_p(seq[i], seq[i - 1]):.2g}" for i in rising(seq)]
        got = m[12] or ""
        if got != "; ".join(up): bad.append((nn, a, tag, "rising", got, up))
        if got:
            nr += 1; line = re.sub(r"\s+", " ", l.strip())
            if line not in rl61: bad.append((nn, "rising line not quoted in §6.1", line[:60]))
chk(f"H1 7 figure records: every merged k/n ({nk}) = count table (fighs_/hisnr_) and (FH tags) = raw; rising cells + one-sided Fisher p recomputed over the whole drawn curve; no FALLBACK / WARNING / 'n = 2560 over the whole range'",
    not bad, str(bad[:3]))
hdrs_ok = []
for nn in recs:
    p = f"/home/HTJ/t2/conference/figures/records/paper_f{nn}.txt"
    mt_s = datetime.fromtimestamp(os.path.getmtime(p), KST).strftime("%m-%d %H:%M:%S")
    nlines = len(recs[nn]) - (1 if recs[nn][-1] == "" else 0)
    hdrs_ok.append(f"`paper_f{nn}.txt` ({mt_s} KST, {nlines} 줄)" in "\n".join(S61))
chk(f"H2 §6.1 quotes exactly the records' rising lines ({nr} lines) and the records' line counts / mtimes",
    len(rl61) == nr == 10 and all(hdrs_ok), f"{len(rl61)} vs {nr} (f21 7 + f22 1 + f24 2); headers {hdrs_ok}")

# ====================================================================== I. environment / wording numbers
print("\n# I. environment")
env = dict(host=sh("hostname"), pid1=sh("TZ=America/Chicago ps -o lstart= -p 1"), up=sh("uptime -p"),
           drv=sh("nvidia-smi --query-gpu=driver_version --format=csv,noheader | sort -u"), ldd=sh("ldd --version | head -1"),
           apt=sh("grep ^Start-Date /var/log/apt/history.log | tail -1"))
print("   now: " + json.dumps(env, ensure_ascii=False))
chk("I1 §6.1 '환경': hostname 262d04c812cc, PID 1 start '화 10월  6 20:38:41 2026' (CDT), driver 580.178.04, glibc 2.39-0ubuntu8.7, apt last Start-Date 2026-07-07 13:42:56 = read now",
    env["host"] == "262d04c812cc" and env["pid1"] == "화 10월  6 20:38:41 2026" and env["drv"] == "580.178.04" and "2.39-0ubuntu8.7" in env["ldd"] and "2026-07-07  13:42:56" in env["apt"]
    and all(x in "\n".join(S61) for x in ("`262d04c812cc`", "`화 10월  6 20:38:41 2026`", "`580.178.04`", "GLIBC 2.39-0ubuntu8.7", "2026-07-07  13:42:56")))
chk("I2 the container re-creation (PID 1 start 20:38:41 CDT) falls between the last pre-interruption log line (20:37) and recover start (21:08:00)",
    datetime(2026, 10, 6, 20, 37, tzinfo=CDT) <= datetime(2026, 10, 6, 20, 38, 41, tzinfo=CDT) <= datetime(2026, 10, 6, 21, 8, tzinfo=CDT))
old_claude = sh("cd /home/HTJ/t2 && git show 331f6e57:CLAUDE.md")
chk("I3 driver value before the interruption: committed CLAUDE.md (331f6e57) says 580.173.02; working-tree CLAUDE.md now says 580.178.04 (uncommitted edit after the record)",
    "580.173.02" in old_claude and "580.178.04" in open("/home/HTJ/t2/CLAUDE.md").read(), f"CLAUDE.md mtime {datetime.fromtimestamp(os.path.getmtime('/home/HTJ/t2/CLAUDE.md'), CDT):%m-%d %H:%M CDT}")
print("   note: recover.sh header says 'old container 9000babdde68' (= the committed CLAUDE.md id); the manifests written before the interruption say host 0695aede856d")
print("   no log under conf/ records the driver version before 10-06 21:08 CDT: " + (sh("grep -rl '580\\.173' logs results 2>/dev/null | grep -v 'fighs_interrupt\\|FIGHS16e4\\|prereg_audit_2026-10-07' | tr '\\n' ' '") or "(none)"))
hdr = next(l for l in S61 if l.startswith("### 6.1"))
chk("I4 §6.1 header time 16:23 CDT (= 06:23 KST) is after the s6 generator outputs' mtimes (06:22 KST) and after FIGHS_DONE",
    "2026-10-07 16:23 CDT (= 10-08 06:23 KST)" in hdr and datetime.fromtimestamp(os.path.getmtime(f"{AUD}/s6_draft_raw.md"), KST) < datetime(2026, 10, 8, 6, 23, tzinfo=KST))
draft = open(f"{AUD}/s6_draft_raw.md", encoding="utf-8").read().split("\n")
body = [l for l in S61[1:] if not l.startswith("**편차·주의")]
i_dev = next(i for i, l in enumerate(S61) if l.startswith("**편차·주의"))
d0 = next(i for i, l in enumerate(draft) if l.startswith("**실행·수용**"))
chk("I5 §6.1 body (between the header and '편차·주의') = s6_draft_raw.md output (after its HTML comment) line for line",
    [l.rstrip() for l in S61[2:i_dev] if l.strip()] == [l.rstrip() for l in draft[d0:] if l.strip()],
    f"{sum(1 for l in S61[2:i_dev] if l.strip())} vs {sum(1 for l in draft[d0:] if l.strip())} non-empty lines")

# ====================================================================== summary
nf = [n for n, ok in CHECKS if not ok]
print(f"\n# SUMMARY: {len(CHECKS)} checks, {len(nf)} FAIL" + (": " + "; ".join(nf) if nf else ""))
print(f"# finished {datetime.now(CDT):%Y-%m-%d %H:%M:%S %Z}")
