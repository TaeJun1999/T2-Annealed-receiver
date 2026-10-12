#!/usr/bin/env python
"""recompute_fighsx.py -- independent RECORD AUDIT of NEXT_EXPERIMENTS_FIGHSX16e4.md §6 (Fable 5.1 subagent, read-only) and of the
other record lines added in commit 4c536f1b (EXPERIMENTS last row, three DECISIONS lines, the bracketed corrections in
NEXT_EXPERIMENTS_FIGHSROOM16e4.md / NEXT_EXPERIMENTS_FIGHSPATH16e4.md).  Adapted from recompute_fighspath.py (same folder); every
expected value is retyped from THIS record.  Run from /home/HTJ/t2/conf:
  CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 ~/miniforge3/envs/torch/bin/python -B \
      results/review_next/prereg_audit_2026-10-11/recompute_fighsx.py > results/review_next/prereg_audit_2026-10-11/recompute_fighsx.out
Own numpy reader only (no analysis.load_raw, no s6_fighsx_gen.py, no fx_overlap_check.py, no hisnr_report); count tables / figure
records / registration are compared AGAINST, never read as input.  8 worker processes (one thread each), writes only stdout.
Sections: A rows / registration  B new raws (6 x 4096)  C FH raws (6 x 2048) + original raws (6 x 448)  D controls
P8 the first 20480 trials vs raw_FH*  E count tables ('# split' included) + §6.2a/b  F §6.3  G figure records (hsx, hsx12)
H logs / manifests / mtimes / git  I §6.4, EXPERIMENTS row, DECISIONS  J corrections in the two earlier registrations.
"""
import glob, hashlib, json, os, re, subprocess, sys
from datetime import datetime, timedelta
from multiprocessing import Pool
from zoneinfo import ZoneInfo

import numpy as np
from scipy.stats import fisher_exact

os.chdir("/home/HTJ/t2/conf")
RV = "results/review_next"; AUD = f"{RV}/prereg_audit_2026-10-11"; REG = f"{RV}/NEXT_EXPERIMENTS_FIGHSX16e4.md"; REC = "../conference/figures/records"
FIGD = "../conference/figures"
RUNC, S6C = "037c6610", "4c536f1b"
CDT, KST = ZoneInfo("America/Chicago"), ZoneInfo("Asia/Seoul")
HX = (12.0, 15.0); HS4 = (6.0, 9.0, 12.0, 15.0); ALL = (-3.0, 0.0, 3.0) + HS4; N4 = 81920; N2 = 20480; N1 = 2560; NU = N4 - N2
KEYS_RAW = ("blk_err", "ber", "nmse", "tauL_gmean", "alphaD", "tauL_clip_frac", "alphaD_clip")   # common.KEYS_RAW (copied)
PAT = re.compile(r"^D2_(C\d)_([A-Za-z0-9]+?)_Nr(\d+)_T(\d+)_Tp(\d+)_(dft|eig)_snr(-?\d+)_skip(\d+)_n(\d+)\.npz$")
ORDER = ["M-ours-dscore-C-V1", "ALD-pilot", "M-ours-bstar", "R2-ours-G", "R1-turbo", "R3-bigamp", "R0-pilot@1", "SBL-loop", "SBL-pilot",
         "OMP-pilot", "R5-genie"]
LABEL = {"M-ours-dscore-C-V1": "Proposed (diffusion prior)", "ALD-pilot": "Annealed Langevin (plug-in)", "M-ours-bstar": "GMM prior",
         "R2-ours-G": "Gaussian prior", "R1-turbo": "Turbo LMMSE receiver", "R3-bigamp": "BiG-AMP", "R0-pilot@1": "Pilot-only LMMSE",
         "SBL-loop": "SBL (in loop)", "SBL-pilot": "SBL (pilot-only)", "OMP-pilot": "OMP (pilot-only)", "R5-genie": "Perfect CSI"}
BARS = ("M-ours-dscore-C-V1", "M-ours-bstar", "R2-ours-G", "R5-genie")
V, B, GE = "M-ours-dscore-C-V1", "M-ours-bstar", "R5-genie"
PRS = ("SRB", "SRP")
def srcs(p, a): return {"ALD-pilot": f"ALD{p}", "SBL-loop": f"SP{p}", "SBL-pilot": f"SP{p}", "OMP-pilot": f"SP{p}"}.get(a, f"{p}B16e4")   # original tag of a curve
# frozen meta, retyped from the registration §1 / the task brief
FROZ = {"SRB": dict(ck="ckpt/d2sx_SRB_N160000_a1_best.pt", sha="ed437f21af15c305", bstar="gmm1024", llkey="ll_val|gmm1024", ll="97.00871495382869",
                    pick="results/sparse/pick_SRB_C2.json", picksha="4c6da315c701b9d4", tune="e0adb06cce792093", aldtest="a3d249188f9c061a",
                    piltest="97a2d08640fef383", hs4sha="dcdce65b032899b1", pid=13),
        "SRP": dict(ck="ckpt/d2sx_SRP_N160000_a1_best.pt", sha="ac4699c78b3e2d80", bstar="kron", llkey="ll_val|kron", ll="244.1932863626755",
                    pick="results/sparse/pick_SRP_C2.json", picksha="6ae22a15de019833", tune="858087f53952bcbf", aldtest="ebb14a8952f0ae17",
                    piltest="8bfc83a43f790bbf", hs4sha="2608bcf1c02fe80c", pid=15)}
# §6.2a / §6.2b retyped from the record: arm -> (k12, k15, unseen12, unseen15, seen12, seen15, FH12, FH15)
EXP = {"SRB": {"M-ours-dscore-C-V1": (12, 11, 9, 7, 3, 4, 3, 4), "ALD-pilot": (40, 31, 31, 17, 9, 14, 7, 11), "M-ours-bstar": (32, 15, 21, 9, 11, 6, 11, 6),
               "R2-ours-G": (144, 65, 107, 46, 37, 19, 37, 19), "R1-turbo": (319, 127, 232, 93, 87, 34, 87, 34),
               "R3-bigamp": (11377, 10284, 8564, 7803, 2813, 2481, 2813, 2481), "R0-pilot@1": (1558, 676, 1182, 503, 376, 173, 376, 173),
               "SBL-loop": (90, 43, 73, 30, 17, 13, 17, 13), "SBL-pilot": (103, 43, 80, 30, 23, 13, 23, 13), "OMP-pilot": (304, 178, 241, 125, 63, 53, 63, 53),
               "R5-genie": (5, 4, 4, 3, 1, 1, 1, 1)},
       "SRP": {"M-ours-dscore-C-V1": (4, 1, 4, 1, 0, 0, 0, 0), "ALD-pilot": (11, 4, 6, 2, 5, 2, 3, 2), "M-ours-bstar": (14, 6, 11, 5, 3, 1, 3, 1),
               "R2-ours-G": (16, 6, 12, 5, 4, 1, 4, 1), "R1-turbo": (44, 11, 33, 7, 11, 4, 11, 4),
               "R3-bigamp": (11333, 10874, 8452, 8192, 2881, 2682, 2881, 2682), "R0-pilot@1": (656, 196, 487, 141, 169, 55, 169, 55),
               "SBL-loop": (14, 8, 6, 6, 8, 2, 8, 2), "SBL-pilot": (20, 8, 9, 6, 11, 2, 11, 2), "OMP-pilot": (124, 38, 94, 29, 30, 9, 30, 9),
               "R5-genie": (1, 0, 0, 0, 1, 0, 1, 0)}}

CHECKS = []; NVAL = [0]
def chk(name, ok, detail="", n=1):
    CHECKS.append((name, bool(ok))); NVAL[0] += n
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" -- {detail}" if detail else ""), flush=True)
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
def same(x, y):            # bit identity (bytes) first; NaN == NaN value identity as the fallback level
    if x.shape != y.shape: return 0
    if x.dtype == y.dtype and x.tobytes() == y.tobytes(): return 2
    return 1 if np.array_equal(x, y, equal_nan=True) else 0

MKEYS = ("ntrain", "bstar", "kron_K", "ll_val|gmm1024", "ll_val|kron", "stagec_ckpt_id", "sparse", "rotation", "ald_file")
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
            for a in sorted({k.split("|")[0] for k in fs if "|" in k and not k.startswith(("meta|", "run|"))}):
                if f"{a}|blk_err" not in fs: continue
                be = np.asarray(z[f"{a}|blk_err"], float); nf = ~np.isfinite(be)
                o["arms"][a] = (np.where(nf[:, -1], 1.0, be[:, -1]).astype(np.int8), np.where(nf[:, 0], 1.0, be[:, 0]).astype(np.int8) if a == "R0-pilot" else None,
                                be.shape, int(nf.sum()), int(z[f"{a}|failed"].sum()) if f"{a}|failed" in fs else 0, f"{a}|failed" in fs)
    except Exception as e:
        o["err"] = repr(e)
    return o
def pair(args):            # compare the arm arrays of two chunk files -> per-arm (n, n not value-identical, n not byte-identical), keys differing
    fa, fb, only = args
    out = {"file": os.path.basename(fa), "twin": os.path.exists(fb), "arms": {}, "bad": [], "keyset": None, "runbad": []}
    if not out["twin"]: return out
    with np.load(fa) as a, np.load(fb) as b:
        ka = {k for k in a.files if not k.startswith(("meta|", "run|")) and (only is None or k.split("|")[0] in only)}
        kb = {k for k in b.files if not k.startswith(("meta|", "run|")) and (only is None or k.split("|")[0] in only)}
        out["keyset"] = ka == kb
        for k in sorted(ka):
            arm, q = k.split("|", 1); lev = same(a[k], b[k]) if k in kb else 0
            c = out["arms"].setdefault(arm, [0, 0, 0]); c[0] += 1; c[1] += lev == 0; c[2] += lev < 2
            if lev == 0: out["bad"].append((arm, q))
        for k in ("run|skip", "run|snr", "run|n", "run|seed", "run|iters"):
            if str(a[k]) != str(b[k]): out["runbad"].append(k)
    return out


if __name__ == "__main__":
    POOL = Pool(8)
    print(f"# recompute_fighsx.py  started {datetime.now(CDT):%Y-%m-%d %H:%M:%S %Z} (= {datetime.now(KST):%H:%M KST})  HEAD {sh('git rev-parse --short HEAD')}")

    # ====================================================================== A. rows / registration
    F = "TAG CELL PR BF CK SHA ROLE BS KK LL REF ORIG PICK FL ARMS".split()
    script = rd("code/run_fighsx16e4.sh")
    rows_txt = re.search(r"^ROWS='(.*?)'$", script, re.S | re.M)[1].split("\n")
    ROWS = [dict(zip(F, l.split("|"))) for l in rows_txt]; TAGS = [r["TAG"] for r in ROWS]; ROW = {r["TAG"]: r for r in ROWS}
    want_tags = [f"FX{x}" for p in PRS for x in (f"{p}B16e4", f"SP{p}", f"ALD{p}")]
    okA = TAGS == want_tags and all(len(l.split("|")) == 15 for l in rows_txt)
    for p in PRS:
        fz = FROZ[p]; b_, s_, a_ = (ROW[f"FX{p}B16e4"], ROW[f"FXSP{p}"], ROW[f"FXALD{p}"])
        okA &= all((r["PR"], r["BF"], r["CELL"], r["LL"]) == (p, f"{p}B16e4", "C2", fz["ll"]) for r in (b_, s_, a_))
        okA &= all((r["BS"], r["KK"]) == (("gmm1024", "-") if p == "SRB" else ("kron", "4096")) for r in (b_, s_, a_))
        okA &= [(r["CK"], r["SHA"], r["ROLE"]) for r in (b_, s_, a_)] == [(fz["ck"], fz["sha"], "best"), ("-", "-", "-"), (fz["ck"], fz["sha"], "best")]
        okA &= [r["PICK"] for r in (b_, s_, a_)] == ["-", f"{fz['pick']}:{fz['picksha']}", "-"] and [r["ORIG"] for r in (b_, s_, a_)] == [f"{p}B16e4", f"SP{p}", f"ALD{p}"]
        okA &= [r["REF"] for r in (b_, s_, a_)] == ["-", f"FX{p}B16e4", f"FX{p}B16e4"] and a_["FL"] == f"--ald-file /home/HTJ/t2/conf/results/ald/ald_PIL{p}_hisnr4.npz" and b_["FL"] == s_["FL"] == ""
        okA &= b_["ARMS"] == "R0-pilot R1-turbo R2-ours-G R3-bigamp M-ours-bstar M-ours-dscore-C-V1 R5-genie" and s_["ARMS"] == "SBL-loop SBL-pilot OMP-pilot R5-genie" and a_["ARMS"] == "ALD-pilot R5-genie"
    chk("A1 ROWS of run_fighsx16e4.sh: 6 rows FX{SRBB16e4,SPSRB,ALDSRB,SRPB16e4,SPSRP,ALDSRP} in this order, 15 fields; SRB gmm1024 | - | 97.00871495382869, ckpt sha ed437f21af15c305 role best, pick pick_SRB_C2.json:4c6da315c701b9d4; SRP kron | 4096 | 244.1932863626755, ckpt sha ac4699c78b3e2d80, pick pick_SRP_C2.json:6ae22a15de019833; REF = the prior's FX base row; ALD flag = the absolute ald_PIL{SRB,SRP}_hisnr4.npz; SNRS=\"12 15\", N=81920, SK=10000",
        okA and 'SK=10000; N=81920; SNRS="12 15"' in script, n=6 * 12)
    reg = rd(REG).split("\n")
    i6 = next(i for i, l in enumerate(reg) if l.startswith("## 6. "))
    S6 = reg[i6:]
    dtxt = sh(f"git diff {RUNC} {S6C} -- {REG}")
    hunks = re.findall(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", dtxt, re.M)
    old = sh(f"git show {RUNC}:./{REG}").split("\n")
    j6 = next(i for i, l in enumerate(old) if l.startswith("## 6. "))
    removed = [l[1:] for l in dtxt.split("\n") if l.startswith("-") and not l.startswith("---")]
    chk(f"A2 registration: git diff {RUNC} {S6C} = ONE hunk, starting in the 3 context lines above the old '## 6.' header (old line {j6 + 1}); the only removed lines are the §6 header + placeholder",
        len(hunks) == 1 and int(hunks[0][0]) >= j6 + 1 - 3 and removed == ["## 6. 결과", "", "(실행 뒤 채운다.)"] and old[j6:] in (["## 6. 결과", "", "(실행 뒤 채운다.)"], ["## 6. 결과", "", "(실행 뒤 채운다.)", ""]),
        f"hunks {hunks}; removed {removed}; old tail {old[j6:]}", n=3)
    chk(f"A3 lines 1..§6 header-1 of the working-tree registration == committed {RUNC} (frozen 머리말 / §1 / §3 / §5); working tree == {S6C} (git diff empty); {RUNC} is the last commit touching the registration before {S6C}",
        old[:j6] == reg[:i6] and not sh(f"git diff {S6C} -- {REG}") and sh(f"git log --format=%h -2 {S6C} -- {REG}").split("\n") == [S6C, RUNC], f"§6 header at line {i6 + 1}; {i6} frozen lines", n=3)
    okA4 = sha("code/run_fighsx16e4.sh")[:16] == "44fc2e671a63f4be" and sha("code/ald.py")[:16] == "f81f3c0f65bed35e" and not sh(f"git diff {RUNC} HEAD -- code ../Demo") and not sh("git status --porcelain code ../Demo")
    for p in PRS:
        fz = FROZ[p]
        okA4 &= (sha(fz["ck"])[:16] == fz["sha"] and sha(fz["pick"])[:16] == fz["picksha"] and sha(f"results/ald/tune_PIL{p}.json")[:16] == fz["tune"] and
                 sha(f"results/ald/ald_PIL{p}.npz")[:16] == fz["aldtest"] and sha(f"results/ald/pilots_PIL{p}_test.npz")[:16] == fz["piltest"])
    chk("A4 on disk: ckpt sha ed437f21af15c305 / ac4699c78b3e2d80, pick sha 4c6da315c701b9d4 / 6ae22a15de019833, tune e0adb06cce792093 / 858087f53952bcbf, ALD test estimates a3d249188f9c061a / ebb14a8952f0ae17, test pilots 97a2d08640fef383 / 8bfc83a43f790bbf (§1, script `case`); script sha 44fc2e671a63f4be and ald.py f81f3c0f65bed35e (§5); conf/code and Demo: no diff since the run commit, git status clean",
        okA4, n=14)
    ald_diff = sh(f"git diff aefbfc12 {RUNC} -- code/ald.py")
    plus = [l[1:].strip() for l in ald_diff.split("\n") if l.startswith("+") and not l.startswith("+++")]
    minus = [l[1:].strip() for l in ald_diff.split("\n") if l.startswith("-") and not l.startswith("---")]
    chk("A5 git diff aefbfc12 037c6610 -- code/ald.py = the hisnr4 set only (4 lines replaced by 5: docstring 1 -> 2, the regen SNR list, the regen (skip, n) table, the --set choices); every added line names hisnr4; cmd_estimate untouched",
        len(minus) == 4 and len(plus) == 5 and sum("hisnr4" in l for l in plus) == 4 and plus[0].startswith("(b, H per trial") and
        '"hisnr4": [12.0, 15.0]' in plus[2] and '"hisnr4": (C.HISNR_SKIP0, 81920)' in plus[3] and 'choices=("dev", "test", "hisnr", "hisnr4")' in plus[4] and "cmd_estimate" not in ald_diff.split("@@")[-1],
        f"+{len(plus)} -{len(minus)}; hunk heads {re.findall(r'@@ [^@]+ @@ (.*)', ald_diff)}", n=5)
    aldsrc = rd("code/ald.py")
    est = aldsrc.split("def cmd_estimate(a):")[1].split("\ndef ")[0]
    chk("A6 머리말 '시행' statement verified in code/ald.py: cmd_estimate seeds each SNR by its INDEX in the pilots file (`for k, s in enumerate(z[\"snrs\"])`: manual_seed(SEED + 1000 + 17 * k)) and ald_run draws torch.randn(B, 2 * N, generator=gen) for the whole batch -> +12 / +15 dB are k = 2 / 3 with B = 20480 in the hisnr file, k = 0 / 1 with B = 81920 in hisnr4",
        'for k, s in enumerate(z["snrs"]):' in est and "manual_seed(SEED + 1000 + 17 * k)" in est and "torch.randn(B, 2 * N, dtype=dt, device=dev, generator=gen)" in aldsrc and "SEED = 20260927" in aldsrc, n=3)
    HS4Z = {}
    okA7 = True; det = []
    for p in PRS:
        z = np.load(f"results/ald/ald_PIL{p}_hisnr4.npz"); y = np.load(f"results/ald/ald_PIL{p}_hisnr.npz")
        pv = json.loads(str(z["prov"])); tn = json.loads(str(z["tune"])); T = json.load(open(f"results/ald/tune_PIL{p}.json"))
        s4 = sha(f"results/ald/ald_PIL{p}_hisnr4.npz")[:16]; HS4Z[p] = s4
        bsame = [bool(np.array_equal(z["b"][i][:N2], y["b"][2 + i])) for i in (0, 1)]; hsame = [bool(np.array_equal(z["hhat"][i][:N2], y["hhat"][2 + i])) for i in (0, 1)]
        hrow = [int((z["hhat"][i][:N2] != y["hhat"][2 + i]).any(axis=1).sum()) for i in (0, 1)]
        det.append(f"{p}: sha {s4}, prov.git {pv['git']}, ald_py_sha {pv.get('ald_py_sha')}, skip {int(z['skip'])}, hhat {z['hhat'].shape}, snrs {z['snrs'].tolist()}, c {tn.get('c')} beta {tn.get('beta')}; "
                   f"first 20480 rows vs hisnr file at +12/+15: pilots b identical {bsame}, hhat identical {hsame} (rows with a different estimate {hrow} of 20480)")
        okA7 &= (s4 == FROZ[p]["hs4sha"] and pv["git"] == RUNC and int(z["skip"]) == 10000 and z["hhat"].shape == (2, N4, 32) and z["snrs"].tolist() == list(HX) and tn == T
                 and y["snrs"].tolist() == list(HS4) and all(bsame) and not any(hsame) and not sh(f"git ls-files results/ald/ald_PIL{p}_hisnr4.npz"))
    chk("A7 new-trial ALD estimates ald_PIL{SRB,SRP}_hisnr4.npz: sha256[:16] dcdce65b032899b1 / 2608bcf1c02fe80c (§6.4; untracked), prov git 037c6610, skip 10000, hhat (2, 81920, 32), snrs 12 / 15, tune == the frozen tune record; on the first 20480 rows the pilot observations b are bit-identical to the hisnr file's +12 / +15 dB rows (same trials) while hhat differs (a new posterior sample)",
        okA7, " | ".join(det), n=18)
    print(f"   ald.py sha256[:16] at {RUNC}: {hashlib.sha256(subprocess.run(f'git show {RUNC}:./code/ald.py', shell=True, capture_output=True).stdout).hexdigest()[:16]} (prov.ald_py_sha above is the file's own convention)")

    # ====================================================================== B. new raws
    print("\n# B. scanning the 6 new raws (8 processes) ...", flush=True)
    BY = {t: POOL.map(scan, sorted(glob.glob(f"raw_{t}/D2_*.npz")), chunksize=64) for t in TAGS}
    chk("B0 every new chunk readable; each raw dir holds only D2_*.npz chunk files (4096 each)", not [o for t in TAGS for o in BY[t] if o["err"]] and all(len(os.listdir(f"raw_{t}")) == 4096 == len(BY[t]) for t in TAGS),
        str({t: len(os.listdir(f"raw_{t}")) for t in TAGS}), n=6)
    PLAN = {(s, 10000 + 40 * k, 40) for s in HX for k in range(2048)}
    PICK = {p: json.load(open(FROZ[p]["pick"])) for p in PRS}
    VEC, VEC1, MT, CKIDS = {}, {}, {}, {}
    bad_plan, bad_git, bad_meta, bad_shape, bad_raised = [], [], [], [], []
    for r in ROWS:
        t = r["TAG"]; L = BY[t]; p = r["PR"]; fz = FROZ[p]
        plan = [(o["name"][2], o["name"][3], o["name"][4]) for o in L]
        if len(L) != 4096 or set(plan) != PLAN or len(set(plan)) != 4096 or any(o["run"][:3] != q for o, q in zip(L, plan)): bad_plan.append(t)
        if {o["name"][0] for o in L} != {"C2"} or {o["name"][1] for o in L} != {p} or {o["name"][5] for o in L} != {"dft"}: bad_plan.append((t, "cell/prior/pilot"))
        if {o["git"] for o in L} != {RUNC} or {o["run"][3] for o in L} != {16} or {o["run"][4] for o in L} != {20260926}: bad_git.append((t, {o["git"] for o in L}))
        aldf = f"/home/HTJ/t2/conf/results/ald/ald_PIL{p}_hisnr4.npz sha256[:16]={HS4Z[p]}"
        CKIDS[t] = sorted({o["meta"].get("stagec_ckpt_id") for o in L}, key=str)
        for o in L:
            mt = o["meta"]
            if mt.get("ntrain") != "160000.0" or mt.get("bstar") != fz["bstar"] or mt.get(fz["llkey"]) != fz["ll"] or (p == "SRP" and mt.get("kron_K") != "4096"): bad_meta.append((t, o["file"], "ntrain/bstar/ll/kron_K", mt)); break
            cid = mt.get("stagec_ckpt_id")
            if r["CK"] == "-":
                if cid is not None: bad_meta.append((t, o["file"], "SP row has stagec_ckpt_id")); break
            elif not (cid and cid.startswith(f"sha256[:16]={fz['sha']} ") and " role=best " in cid): bad_meta.append((t, o["file"], "ckpt id", cid)); break
            if r["PICK"] != "-":
                e = PICK[p]["per_snr"][str(int(o["name"][2]))]
                if json.loads(mt.get("sparse", "null")) != dict(rho_sbl=PICK[p]["rho_sbl"], rho_omp=PICK[p]["rho_omp"], n_em=e["n_em"], L=e["L"]): bad_meta.append((t, o["file"], "sparse", mt.get("sparse"))); break
            elif "sparse" in mt: bad_meta.append((t, o["file"], "unexpected meta|sparse")); break
            if "rotation" in mt: bad_meta.append((t, o["file"], "unexpected meta|rotation")); break
            if "--ald-file" in r["FL"]:
                if mt.get("ald_file") != aldf: bad_meta.append((t, o["file"], "ald_file", mt.get("ald_file"))); break
            elif "ald_file" in mt: bad_meta.append((t, o["file"], "unexpected meta|ald_file")); break
        arms = set(r["ARMS"].split())
        if any(set(o["arms"]) != arms for o in L): bad_shape.append((t, "arm set", sorted({a for o in L for a in o["arms"]})))
        if any(v[2] != (40, 16) for o in L for v in o["arms"].values()): bad_shape.append((t, "shape"))
        if any(v[3] or v[4] or v[5] for o in L for v in o["arms"].values()): bad_raised.append((t, {a: sum(o["arms"][a][3] + o["arms"][a][4] for o in L) for a in arms}))
        Ls = sorted(L, key=lambda o: (o["name"][2], o["name"][3]))                      # SNR, then skip = trial order
        VEC[t] = {a: {s: np.concatenate([o["arms"][a][0] for o in Ls if o["name"][2] == s]) for s in HX} for a in arms}
        VEC1[t] = {s: np.concatenate([o["arms"]["R0-pilot"][1] for o in Ls if o["name"][2] == s]) for s in HX} if "R0-pilot" in arms else None
        MT[t] = (min(o["mtime"] for o in L), max(o["mtime"] for o in L))
    chk("B1 trial plan: 6 tags x 4096 chunks = 2 SNR (+12, +15) x skip 10000..91880 step 40 (each once = trials 10000..91919), n 40; run|snr/skip/n = file name; cell C2, prior = the row's, '_dft_' names", not bad_plan, str(bad_plan), n=6 * 4096)
    chk("B2 run|git == '037c6610' (no +dirty), run|iters 16, run|seed 20260926 in every chunk of the six raws (incl. raw_FXALDSRP, written in the 04:5x CDT resume)", not bad_git, str(bad_git), n=6 * 4096)
    chk("B3 meta, every chunk: ntrain 160000; SRB bstar gmm1024 / ll_val|gmm1024 97.00871495382869, SRP bstar kron / kron_K 4096 / ll_val|kron 244.1932863626755; stagec_ckpt_id sha ed437f21af15c305 (SRB) / ac4699c78b3e2d80 (SRP) role best in the checkpoint rows, absent in SP rows; meta|sparse == pick per SNR (SP only); no rotation; meta|ald_file == absolute path + sha (ALD only)",
        not bad_meta, str(bad_meta[:3]), n=6 * 4096)
    print("   stagec_ckpt_id values: " + "; ".join(f"{t} {CKIDS[t]}" for t in TAGS))
    chk("B4 arm set of every chunk = the row's; blk_err shape (40, 16)", not bad_shape, str(bad_shape[:3]))
    chk("B5 raised trials 0 (registration §1 N-7: ALD-pilot included): no |failed key, no non-finite blk_err at any iteration in any chunk of the six raws", not bad_raised, str(bad_raised))
    def K4(t, a, s): return int((VEC1[t][s] if a == "R0-pilot@1" else VEC[t][a][s]).sum())
    def KS(t, a, s): return int((VEC1[t][s] if a == "R0-pilot@1" else VEC[t][a][s])[:N2].sum())          # trials 10000..30479
    def KU(t, a, s): return int((VEC1[t][s] if a == "R0-pilot@1" else VEC[t][a][s])[N2:].sum())          # trials 30480..91919
    chk("B5b every per-SNR vector holds 81920 trials (2048 chunks x 40, in skip order)", all(len(v) == N4 for t in TAGS for d in VEC[t].values() for v in d.values()))
    jobs = [(f"raw_FX{x}/{o['file']}", f"raw_FX{p}B16e4/{o['file']}", ("R5-genie",)) for p in PRS for x in (f"SP{p}", f"ALD{p}") for o in BY[f"FX{x}"]]
    res = POOL.map(pair, jobs, chunksize=64)
    ng = sum(r["arms"].get("R5-genie", [0])[0] for r in res); nb = sum(r["arms"].get("R5-genie", [0, 0])[1] for r in res); nbyte = sum(r["arms"].get("R5-genie", [0, 0, 0])[2] for r in res)
    NARR = ng
    chk(f"B6 R5-genie identical across the three FX raws of each prior: FXSP* / FXALD* vs the FX base raw, every chunk x (KEYS_RAW 7 + guardH) -- {ng} arrays, {nb} differ in value, {nbyte} differ in bytes",
        ng == 4 * 4096 * 8 and nb == 0 and all(r["twin"] and r["keyset"] for r in res), n=0)
    print("   genie failures per SNR (+12, +15): " + " · ".join(f"{t} {[K4(t, GE, s) for s in HX]}" for t in TAGS))
    print("   chunk mtime windows (CDT): " + " · ".join(f"{t} {cdt(MT[t][0]):%m-%d %H:%M:%S}–{cdt(MT[t][1]):%m-%d %H:%M:%S}" for t in TAGS))

    # ====================================================================== C. FH raws (n = 20480) and original raws (n = 2560)
    print("\n# C. scanning the 6 FH raws and the 6 original raws ...", flush=True)
    FHT = [t.replace("FX", "FH", 1) for t in TAGS]; OT = [t[2:] for t in TAGS]
    FB = {t: POOL.map(scan, sorted(glob.glob(f"raw_{t}/D2_*.npz")), chunksize=64) for t in FHT}
    OB = {t: POOL.map(scan, sorted(glob.glob(f"raw_{t}/D2_*.npz")), chunksize=64) for t in OT}
    FC, OC = {}, {}
    bad = []
    for t, L in FB.items():
        plan = {}
        for x in L: plan.setdefault(x["name"][2], []).append((x["name"][3], x["name"][4]))
        if [x for x in L if x["err"]] or len(L) != 2048 or set(plan) != set(HS4) or any(sorted(v) != [(10000 + 40 * k, 40) for k in range(512)] for v in plan.values()): bad.append((t, len(L)))
        if any(v[3] or v[4] or v[5] for x in L for v in x["arms"].values()): bad.append((t, "raised / non-finite"))
        c = {}
        for x in L:
            for a, v in x["arms"].items():
                c.setdefault(a, {}).setdefault(x["name"][2], [0, 0]); c[a][x["name"][2]][0] += int(v[0].sum()); c[a][x["name"][2]][1] += len(v[0])
                if a == "R0-pilot": c.setdefault("R0-pilot@1", {}).setdefault(x["name"][2], [0, 0]); c["R0-pilot@1"][x["name"][2]][0] += int(v[1].sum()); c["R0-pilot@1"][x["name"][2]][1] += len(v[1])
        FC[t] = c
        if any(v[1] != N2 for d in c.values() for v in d.values()): bad.append((t, "n != 20480"))
    print("   FH raws: " + "; ".join(f"raw_{t} {len(L)} chunks git {sorted({x['git'] for x in L})} max skip {max(x['name'][3] for x in L)}" for t, L in FB.items()))
    chk("C1 n = 20480 raws raw_FH{SRBB16e4,SPSRB,ALDSRB,SRPB16e4,SPSRP,ALDSRP}: 2048 chunks = 4 SNR x skip 10000..30440 step 40, n 20480, no raised / non-finite block; run|git 193776a1 (SRB) / c48ee796 (SRP)",
        not bad and all({x["git"] for x in FB[f"FH{x_}"]} == {g} for p, g in (("SRB", "193776a1"), ("SRP", "c48ee796")) for x_ in (f"{p}B16e4", f"SP{p}", f"ALD{p}")), str(bad), n=6 * 2048)
    bad = []
    for t, L in OB.items():
        plan = {}
        for x in L: plan.setdefault(x["name"][2], []).append((x["name"][3], x["name"][4]))
        if [x for x in L if x["err"]] or len(L) != 448 or set(plan) != set(ALL) or any(sorted(v) != [(40 * k, 40) for k in range(64)] for v in plan.values()): bad.append((t, len(L)))
        if any(v[3] for x in L for v in x["arms"].values()): bad.append((t, "non-finite"))
        c = {}
        for x in L:
            for a, v in x["arms"].items():
                c.setdefault(a, {}).setdefault(x["name"][2], [0, 0]); c[a][x["name"][2]][0] += int(v[0].sum()); c[a][x["name"][2]][1] += len(v[0])
                if a == "R0-pilot": c.setdefault("R0-pilot@1", {}).setdefault(x["name"][2], [0, 0]); c["R0-pilot@1"][x["name"][2]][0] += int(v[1].sum()); c["R0-pilot@1"][x["name"][2]][1] += len(v[1])
        OC[t] = c
        if any(v[1] != N1 for d in c.values() for v in d.values()): bad.append((t, "n != 2560"))
    print("   original raws: " + "; ".join(f"raw_{t} {len(L)} chunks git {sorted({x['git'] for x in L})} max skip {max(x['name'][3] for x in L)}" for t, L in OB.items()))
    chk("C2 original raws (test trials 0..2559): 6 x 448 chunks = 7 SNR x skip 0..2520 step 40, n 2560, no non-finite", not bad, str(bad), n=6 * 448)
    def MERGED(p, a):      # the 7 drawn points of the hsx figure: (k, n)
        o = srcs(p, a)
        return [tuple(OC[o][a][s]) for s in ALL[:3]] + [tuple(FC[f"FH{o}"][a][s]) for s in HS4[:2]] + [(K4(f"FX{o}", a, s), N4) for s in HX]
    def MERGED_HS(p, a):   # the 7 points of the earlier hs figure (n = 20480 at +6..+15)
        o = srcs(p, a)
        return [tuple(OC[o][a][s]) for s in ALL[:3]] + [tuple(FC[f"FH{o}"][a][s]) for s in HS4]
    other = sorted({os.path.basename(d) for d in glob.glob("raw_*") for f in [next(iter(glob.glob(f"{d}/D2_C2_SR[BP]_*.npz")), None)] if f} - {f"raw_{t}" for t in TAGS})
    mx = {d: max(int(PAT.match(os.path.basename(f))[8]) for f in glob.glob(f"{d}/D2_C2_SR[BP]_*.npz")) for d in other}
    chk("C3 머리말 '시행 30480..91919 는 SRB · SRP 에서 한 번도 쓰인 적이 없다': by file name, no raw dir other than the six raw_FX* holds an SRB / SRP chunk with skip > 30440",
        all(v <= 30440 for v in mx.values()), f"{len(other)} other raw dirs with SRB / SRP chunks; max skip {max(mx.values())}; dirs with skip >= 10000: {sorted(d for d, v in mx.items() if v >= 10000)}", n=len(other))

    # ====================================================================== D. controls
    print("\n# D. controls", flush=True)
    bad = []; tot = 0; ctl_txt_ok = True
    for r in ROWS:
        c = r["TAG"].replace("FX", "FXC", 1); arms = r["ARMS"].split(); fs = sorted(glob.glob(f"raw_{c}/D2_*.npz")); n = 0; b = []
        names = sorted(os.path.basename(f) for f in fs)
        if names != sorted(f"D2_C2_{r['PR']}_Nr8_T16_Tp4_dft_snr{int(s)}_skip0_n40.npz" for s in HX): b.append(("names", names))
        for f in fs:
            with np.load(f) as z, np.load(f"raw_{r['ORIG']}/{os.path.basename(f)}") as y:
                if str(z["run|git"]) != RUNC: b.append((f, "git", str(z["run|git"])))
                for a in arms:
                    for q in KEYS_RAW:
                        k = f"{a}|{q}"; n += 1
                        if k not in z.files or k not in y.files or not same(z[k], y[k]): b.append((os.path.basename(f), k))
        tot += n
        txt = rd(f"{RV}/{c}_control.txt")
        own = f"control raw_{c} vs ['raw_{r['ORIG']}']: {len(fs)} chunk files (expected 2), arms {arms}, {n} (chunk, arm, key) comparisons, {len(b)} differ\n\nCONTROL: OK\n"
        ctl_txt_ok &= txt == own
        if len(fs) != 2 or b or txt != own: bad.append((c, len(fs), n, b[:2], txt[:120]))
        print(f"   {c}: {len(fs)} chunks (mtime {' '.join(f'{cdt(os.stat(f).st_mtime):%m-%d %H:%M:%S}' for f in fs)}), {n} (chunk, arm, key) comparisons, {len(b)} differ; control file byte-identical to the text my comparison yields: {txt == own}; file mtime {cdt(os.stat(f'{RV}/{c}_control.txt').st_mtime):%m-%d %H:%M:%S}")
    chk("D1 receiver controls: raw_FXC* (2 chunks each = trials 0..39 at +12 / +15 dB, run|git 037c6610) vs the original raws, every arm x KEYS_RAW identical; the six *_control.txt files are byte-identical to the text my own comparison yields (98 / 56 / 28 comparisons per prior, 0 differ, CONTROL: OK) -- so the three control files REWRITTEN by the resumes hold what the first pass must have written",
        not bad and tot == 2 * (98 + 56 + 28) and ctl_txt_ok, str(bad[:3]), n=12)
    NARR += tot
    okD2 = True
    for p in PRS:
        A_, B_ = np.load(f"results/ald/ald_FXCALD{p}.npz"), np.load(f"results/ald/ald_PIL{p}.npz")
        s_ = all(same(A_[k], B_[k]) for k in ("hhat", "b", "v"))
        txt = rd(f"{RV}/FXCALD{p}_aldcontrol.txt")
        own = f"ALD estimator control results/ald/ald_FXCALD{p}.npz vs results/ald/ald_PIL{p}.npz: hhat (7, 2560, 32), keys hhat b v, max|diff| 0, differing none\nCONTROL-ALD: OK\n"
        okD2 &= s_ and A_["hhat"].shape == (7, 2560, 32) and txt == own
        okD2 &= all(sha(f"results/ald/{x}_FXCALD{p}{y}") == sha(f"results/ald/{x}_PIL{p}{y}") for x, y in (("tune", ".json"), ("pilots", "_dev.npz"), ("pilots", "_test.npz")))
        print(f"   ald_FXCALD{p}.npz mtime {cdt(os.stat(f'results/ald/ald_FXCALD{p}.npz').st_mtime):%m-%d %H:%M:%S}, prov git {json.loads(str(A_['prov']))['git']}; aldcontrol file mtime {cdt(os.stat(f'{RV}/FXCALD{p}_aldcontrol.txt').st_mtime):%m-%d %H:%M:%S}")
    chk("D2 ALD estimator controls: ald_FXCALD{SRB,SRP}.npz hhat (7, 2560, 32) / b / v identical to ald_PIL{SRB,SRP}.npz; *_aldcontrol.txt byte-identical to the expected text (max|diff| 0, CONTROL-ALD: OK); FXC copies of the tune json / dev / test pilots = the originals (sha)",
        okD2, n=12)
    NARR += 6

    # ====================================================================== P8. the first 20480 trials vs raw_FH* (own check; fx_overlap_check.py not used)
    print("\n# P8. prediction 8: chunks skip 10000..30440 at +12 / +15 dB of raw_FX<tag> vs the same-named chunk of raw_FH<tag>", flush=True)
    P8 = {}; okP8 = True; p8lines = []
    for t in TAGS:
        h = t.replace("FX", "FH", 1)
        fl = [o["file"] for o in BY[t] if 10000 <= o["name"][3] <= 30440]
        res = POOL.map(pair, [(f"raw_{t}/{f}", f"raw_{h}/{f}", None) for f in fl], chunksize=32)
        arms = sorted({a for r in res for a in r["arms"]} - {"ALD-pilot"})
        n = sum(r["arms"][a][0] for r in res for a in arms if a in r["arms"]); nd = sum(r["arms"][a][1] for r in res for a in arms if a in r["arms"]); nby = sum(r["arms"][a][2] for r in res for a in arms if a in r["arms"])
        an = sum(r["arms"].get("ALD-pilot", [0, 0, 0])[0] for r in res); ad = sum(r["arms"].get("ALD-pilot", [0, 0, 0])[1] for r in res)
        akeys = {}
        for r in res:
            for arm, q in r["bad"]:
                if arm == "ALD-pilot": akeys[q] = akeys.get(q, 0) + 1
        nrun = 5 * len(res); rb = sum(len(r["runbad"]) for r in res)
        ok = len(fl) == 1024 and all(r["twin"] and r["keyset"] for r in res) and nd == 0 and rb == 0
        okP8 &= ok; P8[t] = (len(fl), arms, n, nd, nby, an, ad, akeys, nrun)
        NARR += n + an
        line = f"   raw_{t} vs raw_{h}: {len(fl)} chunk files (twin exists and same arm-array key set in all: {all(r['twin'] and r['keyset'] for r in res)}), arms {arms}: {n} arrays compared, {nd} differ in value (NaN == NaN), {nby} differ in bytes; run|skip/snr/n/seed/iters {nrun} scalars, {rb} differ"
        if an:
            p = ROW[t]["PR"]
            fxk = [KS(t, "ALD-pilot", s) for s in HX]; fhk = [FC[h]["ALD-pilot"][s][0] for s in HX]
            both = {s: int((VEC[t]["ALD-pilot"][s][:N2].astype(bool) & np.concatenate([o["arms"]["ALD-pilot"][0] for o in sorted(FB[h], key=lambda o: o["name"][3]) if o["name"][2] == s]).astype(bool)).sum()) for s in HX}
            line += f"\n      ALD-pilot (not required): {ad} of {an} arrays differ, by key {dict(sorted(akeys.items()))}; failures on trials 10000..30479 at +12 / +15 dB: raw_{t} {fxk}, raw_{h} {fhk}; blocks failing in BOTH {list(both.values())}"
            P8[t] += (fxk, fhk)
        print(line); p8lines.append(line)
    chk("P8 prediction 8 (own check): in all six raws the 1024 chunks with skip 10000..30440 have a same-named twin in raw_FH<tag> with the same arm-array key set, and EVERY array of every arm except ALD-pilot is identical (61 / 32 / 8 arrays per chunk = 62464 / 32768 / 8192 per raw), run|skip/snr/n/seed/iters equal -> 'bit-identical (ALD-pilot excluded)' holds",
        okP8 and [P8[t][2] for t in TAGS] == [62464, 32768, 8192] * 2 and all(P8[t][4] == 0 for t in TAGS), str({t: P8[t][2:5] for t in TAGS}), n=6)
    ov = rd(f"{RV}/FX_overlap_check.txt").strip().split("\n")
    chk("P8b the author's FX_overlap_check.txt (quoted in §6.3 item 8) vs own: 1024 files per raw; its 'array comparisons' 67584 / 37888 / 13312 = my arm arrays + 5 run|* scalars per chunk (5120); ALD-pilot '3214 of 9216' (SRB) and '3229 of 9216' (SRP) arrays differ = own; §6.3 quotes the file verbatim (7 lines)",
        all(f"{P8[t][2] + P8[t][8]} array comparisons, 0 differ" in l and "1024 chunk files" in l for t, l in zip(TAGS, ov[:6])) and
        f"{P8['FXALDSRB'][6]} of {P8['FXALDSRB'][5]} arrays differ" == "3214 of 9216 arrays differ" and "3214 of 9216 arrays differ" in ov[2] and
        f"{P8['FXALDSRP'][6]} of {P8['FXALDSRP'][5]} arrays differ" == "3229 of 9216 arrays differ" and "3229 of 9216 arrays differ" in ov[5] and ov[6] == "OVERLAP: OK" and
        [l for l in S6 if l.startswith("   - `")] == [f"   - `{l}`" for l in ov], f"own ALD-pilot: SRB {P8['FXALDSRB'][6]} of {P8['FXALDSRB'][5]}, SRP {P8['FXALDSRP'][6]} of {P8['FXALDSRP'][5]}", n=6 + 4 + 7)

    # ====================================================================== E. count tables + §6.2
    print("\n# E. count tables ('# split' lines included) / §6.2a / §6.2b", flush=True)
    okE1 = True; nrow = 0; heads = {}
    for r in ROWS:
        t = r["TAG"]; arms = sorted(set(r["ARMS"].split()) | ({"R0-pilot@1"} if "R0-pilot" in r["ARMS"] else set()))
        out = [f"# run_fighsx16e4 git {RUNC} raw_{t} C2: failures@16 / n, BLER, 95% Wilson -- REPORT-ONLY (FIGHSX16e4 §1); load_raw warnings 0", ""]
        heads[t] = out[0]
        for s in HX:
            for a in arms:
                f = K4(t, a, s); lo, hi = wilson(f, N4); nrow += 1
                out.append(f"SNR {s:+.0f}  {a:<20} {f:6d} / {N4}  BLER {f / N4:.2e}  95% [{lo:.2e}, {hi:.2e}]")
                g = KS(t, a, s); lo, hi = wilson(f - g, NU)
                out.append(f"# split SNR {s:+.0f}  {a:<20} trials 10000..30479 (seen, raw_FH*): {g} of 20480;  trials 30480..91919 (unseen): {f - g} of {NU}  BLER {(f - g) / NU:.2e}  95% [{lo:.2e}, {hi:.2e}]")
        mine = "\n".join(out) + "\n"; theirs = rd(f"{RV}/fighs_{t}.txt")
        if mine != theirs:
            okE1 = False
            print(f"   DIFF fighs_{t}.txt: " + str([(x, y) for x, y in zip(mine.split("\n"), theirs.split("\n")) if x != y][:3]))
        print(f"   fighs_{t}.txt: {len(out) - 2} lines regenerated from the raw by own code, byte-identical to the file: {mine == theirs} (file mtime {cdt(os.stat(f'{RV}/fighs_{t}.txt').st_mtime):%m-%d %H:%M:%S})")
    chk(f"E1 the six count tables fighs_FX*.txt regenerated from the raws by own code (header, {nrow} count rows incl. R0-pilot@1 = iteration 1, {nrow} '# split' rows: seen k of 20480 / unseen k of 61440 / unseen BLER / unseen Wilson) are BYTE-IDENTICAL to the committed files -- incl. fighs_FXSRPB16e4.txt, rewritten by the 04:4x resume (its content is what the unchanged raw yields)",
        okE1 and nrow == 2 * (8 + 4 + 2) * 2, n=nrow * (2 + 3 + 2 + 3))
    chk("E2 count-table headers = the six '집계표 머리말' lines of §6 (three before 6.2a, three before 6.2b), name run_fighsx16e4 git 037c6610 / FIGHSX16e4 §1 and say load_raw warnings 0",
        [l for l in S6 if l.startswith("집계표 머리말: `")] == [f"집계표 머리말: `{heads[t]}`" for t in TAGS], n=6)
    # "seen" == fighs_FH*.txt count for every arm but ALD-pilot (registration §1, N-7) -- FH tables parsed here as the thing compared against; own FH recount as the reference
    FHTAB = {}
    for h in FHT:
        tb = {}
        for l in open(f"{RV}/fighs_{h}.txt", encoding="utf-8"):
            m = re.match(r"SNR ([+-]\d+)\s+(\S+)\s+(\d+) / (\d+)\s+BLER (\S+)\s+95% \[(\S+), (\S+)\]\s*$", l)
            if m: tb[(float(m[1]), m[2])] = (int(m[3]), int(m[4]))
        FHTAB[h] = tb
    bad = []; nseen = 0; aldseen = {}
    for r in ROWS:
        t = r["TAG"]; h = t.replace("FX", "FH", 1)
        if any(FHTAB[h].get((s, a)) != tuple(FC[h][a][s]) for a in FC[h] for s in HS4): bad.append((h, "fighs_FH table != own FH recount"))
        for a in sorted(set(r["ARMS"].split()) | ({"R0-pilot@1"} if "R0-pilot" in r["ARMS"] else set())):
            for s in HX:
                g = KS(t, a, s); fh = FHTAB[h][(s, a)][0]; nseen += 1
                if a == "ALD-pilot": aldseen[(t, s)] = (g, fh)
                elif g != fh: bad.append((t, a, s, g, fh))
    chk(f"E3 '# split' seen == fighs_FH*.txt (N-7): for every arm x SNR of the six raws except ALD-pilot the failures on trials 10000..30479 recomputed from raw_FX* equal the fighs_FH<tag>.txt count (and the fighs_FH tables equal my own recount of raw_FH*, 4 SNRs); {nseen} arm x SNR cells incl. R0-pilot and R0-pilot@1",
        not bad and nseen == 2 * 2 * (8 + 4 + 2), str(bad[:4]) + f"; ALD-pilot seen (new sample) vs fighs_FH: {aldseen}", n=nseen + sum(len(v) for v in FHTAB.values()))
    for p, sec in (("SRB", "6.2a"), ("SRP", "6.2b")):
        bad = []; n62 = 0; rows62 = []
        i0 = next(i for i, l in enumerate(S6) if l.startswith(f"### {sec} {p} ")); i1 = next((i for i, l in enumerate(S6) if i > i0 and l.startswith("### ")), len(S6))
        blk = S6[i0:i1]
        for l in blk:
            m = re.match(r"^\| (\S+) \| raw_(FX\w+) \| (.*) \|$", l)
            if not m or m[1] not in ORDER: continue
            a, t = m[1], m[2]; cells = m[3].split(" | "); rows62.append(a)
            if t != f"FX{srcs(p, a)}" or len(cells) != 2: bad.append((a, "source", t))
            for i, s in enumerate(HX):
                q = re.match(r"^(\d+) \((\S+), \[(\S+), (\S+)\]\) · (\d+) \((\S+)\) · (\d+) \[(\d+)\]$", cells[i]); n62 += 1
                k = K4(t, a, s); lo, hi = wilson(k, N4); u = KU(t, a, s); g = KS(t, a, s); fh = FC[t.replace("FX", "FH", 1)][a][s][0]
                want = (str(k), f"{k / N4:.2e}", f"{lo:.2e}", f"{hi:.2e}", str(u), f"{u / NU:.2e}", str(g), str(fh))
                if not q or q.groups() != want: bad.append((a, s, cells[i], want))
                e = EXP[p][a]
                if (k, u, g, fh) != (e[i], e[2 + i], e[4 + i], e[6 + i]): bad.append((a, s, "typed expectation", (k, u, g, fh), e))
        chk(f"E4 §{sec} table ({p}): 11 curves in legend order x 2 SNR; each cell k / 81920, BLER, Wilson, unseen k / 61440 + BLER, seen k / 20480, [raw_FH k] = own recount from raw_FX* / raw_FH* ({n62} cells x 8 values), source raw, and = the values I retyped from the record",
            not bad and n62 == 22 and rows62 == ORDER, str(bad[:4]), n=22 * 8 + 11)
        g = {f"FX{x}": [K4(f"FX{x}", GE, s) for s in HX] for x in (f"{p}B16e4", f"SP{p}", f"ALD{p}")}
        gl = "Perfect CSI (R5-genie) 의 실패 수는 세 raw 에서 같다: " + " · ".join(f"{t} {v}" for t, v in g.items()) + " → 동일."
        chk(f"E5 §{sec} genie line: '{' · '.join(f'{t} {v}' for t, v in g.items())} → 동일' = own recount; the sentence about the seen counts (assert; ALD-pilot may differ) present",
            any(l.startswith(gl) and "\"본 시행\" 의 수는 ALD-pilot 을 뺀 모든 arm 에서 n = 20480 raw 의 수와 같다(assert); ALD-pilot 은 새 사후 표본이라 다를 수 있다(등록 머리말 '시행')." in l for l in blk)
            and len({tuple(v) for v in g.values()}) == 1 and list(g.values())[0] == ([5, 4] if p == "SRB" else [1, 0]), n=7)
        zero = [f"{a} {s:+.0f} dB" for a in ORDER for s in HX if K4(f"FX{srcs(p, a)}", a, s) == 0]
        zl = f"0 실패 점 (n = 81920): {', '.join(zero) if zero else '없음'}."
        chk(f"E6 §{sec} zero-failure line = own: '{zl}'", zl in blk and zero == ([] if p == "SRB" else ["R5-genie +15 dB"]), str(zero), n=22)

    # ====================================================================== G. figure records (hsx, hsx12; hs for reference)
    print("\n# G. figure records", flush=True)
    def cblock(lines):
        c = {}
        for l in lines[lines.index("Counts:") + 1:]:
            f = l.split()
            if not f: break
            if f[0] in ORDER: c[f[0]] = ([tuple(int(x) for x in v.split("/")) for v in f[1:8]], f[8])
        return c
    def yrule(p, drawn):   # FIGHSX16e4 §1 three tiers on the DRAWN points (drawn = number of SNR points drawn)
        M_ = {a: MERGED(p, a)[:drawn] for a in ORDER}
        zero = any(k == 0 for a in ORDER for k, n in M_[a])
        pos = {(a, ALL[i]): (wilson(k, n)[0] if a in BARS else k / n) for a in ORDER for i, (k, n) in enumerate(M_[a]) if k > 0}
        pts = {(a, ALL[i]): k / n for a in ORDER for i, (k, n) in enumerate(M_[a]) if k > 0}
        tips = {(GE, ALL[i]): 1.96 ** 2 / (n + 1.96 ** 2) / 1.7 for i, (k, n) in enumerate(M_[GE]) if k == 0}
        if not zero and min(pos.values()) > 2e-4: return (0.0002, 1.2), zero, pos, pts, tips
        low = {**{k: v for k, v in pts.items() if v < 3e-5}, **{(a, s, "arrow tip"): v for (a, s), v in tips.items() if v < 3e-5}}
        return ((7.5e-06, 1.2) if low else (3e-05, 1.2)), zero, pos, pts, {**tips, "force": low}
    RECS = {}; MINE = {}
    for p in PRS:
        pl = p.lower()
        for mode, drawn in (("hsx", 7), ("hsx12", 6)):
            rec = rd(f"{REC}/paper_f21{pl}{mode}.txt").split("\n"); RECS[p, mode] = rec
            cnt = cblock(rec)
            chk(f"G1 paper_f21{pl}{mode}.txt 'Counts:' block = own merged counts for the 11 curves (-3/0/+3 dB original raws n 2560; +6/+9 dB raw_FH* n 20480; +12/+15 dB raw_FX* n 81920 -- the +15 dB entry present in hsx12 too); source suffix = the original raw",
                len(cnt) == 11 and all(cnt[a][0] == MERGED(p, a) and cnt[a][1] == f"raw_{srcs(p, a)}" for a in ORDER), n=77 + 11)
            mine = {}
            for a in ORDER:
                seq = MERGED(p, a); o = srcs(p, a)
                up = [f"{ALL[i - 1]:+.0f}->{ALL[i]:+.0f} dB p={fisher_p(seq[i], seq[i - 1]):.2g}" for i in rising(seq)]
                mine[a] = (f"    {a:<20}@16  " + " ".join(f"{k}/{n}" for k, n in seq[3:]) + f"   (+6..+15 dB: raw_FH{o}; then +12/+15 dB: raw_FX{o})" + (f"   rising: {'; '.join(up)}" if up else ""))
            MINE[p] = mine
            blk = [l for l in rec if re.match(r"^    \S+\s+@16  ", l)]
            chk(f"G2 paper_f21{pl}{mode}.txt merge block: 11 lines (k/n at +6..+15 dB, both source tags, 'rising' cells with one-sided Fisher p %.2g over the 7 merged points) byte-identical to own",
                blk == [mine[a] for a in ORDER], f"diff {[(x, y) for x, y in zip(blk, [mine[a] for a in ORDER]) if x != y][:2]}", n=11 * 5)
            (ylim, zero, pos, pts, tips) = yrule(p, drawn)
            yl = re.search(r"y log (\([^)]*\))", "\n".join(rec))[1]
            force = tips.pop("force", {})
            want_y = {"SRB": "(3e-05, 1.2)", "SRP": "(7.5e-06, 1.2)"}[p]
            lowbars = sorted((a, s, f"{v:.3g}") for (a, s), v in pos.items() if a in BARS and v < ylim[0])
            chk(f"G3 y-range rule of §1 (three tiers, own implementation on the DRAWN merged values) for F21{pl}{mode}_col -> {ylim}; record says 'y log {yl}'; registered value {want_y}; every drawn point k/n inside the range",
                str(ylim) == yl == want_y and min(pts.values()) >= ylim[0] and max(pts.values()) <= 1.2,
                f"zero-failure point drawn: {zero}; drawn values (Wilson lower end for the 4 bar curves, k/n else) <= 2e-4: {len([v for v in pos.values() if v <= 2e-4])} {sorted((LABEL[a], f'{s_:+.0f}', f'{v:.3g}') for (a, s_), v in pos.items() if v <= 2e-4)}; min drawn k/n {min(pts.values()):.3g}; "
                f"values below 3e-5 that force the third tier: {[(k, f'{v:.3g}') for k, v in force.items()] or 'none'}; lower Wilson bar ends below the axis floor (clipped): {lowbars or 'none'}", n=4)
            zown = "; ".join(f"{LABEL[a]} {s:+.0f} dB" for a in ORDER for s, (k, n) in zip(ALL[:drawn], MERGED(p, a)[:drawn]) if k == 0)
            zl = [l for l in rec if l.startswith("Zero-failure points")]
            chk(f"G4 paper_f21{pl}{mode}.txt zero-failure line = own over the drawn points ('{zown or 'no line'}')",
                (zl == ["Zero-failure points (the curve breaks there; Perfect CSI: fighs_merge.zero_arrows): " + zown + "."]) if zown else not zl, str(zl), n=drawn * 11)
            below = [(a, ALL[i]) for a in ORDER if a not in (V, GE) for i, ((k, _), (kv, _)) in enumerate(zip(MERGED(p, a)[:drawn], MERGED(p, V)[:drawn])) if k <= kv]
            chk(f"G5 paper_f21{pl}{mode}.txt 'at or below the proposed curve: none' = own (no drawn baseline count <= V1's at any drawn point); 'all (i)' labels line present; raised blocks none",
                not below and any(l.endswith(f"pairB_SP{p}.txt: none.") for l in rec) and any("drawn baselines: all (i)." in l for l in rec) and any(l.endswith("in the raws read: none.") for l in rec), str(below), n=9 * drawn)
            w = "\n".join(rec)
            chk(f"G6 paper_f21{pl}{mode}.txt wording: REPORT-ONLY, both registrations named, 'n = 81920 (new trials 10000..91919) at +12/+15 dB', the not-independent sentence ('first 20480 trials are the same trials as the n = 20480 raw's -- Annealed Langevin: the same trials with a new posterior sample; the unseen trials 30480..91919 alone are the '# split' lines'), 'counts before the merge (n = 2560, the registered judgement)'",
                "REPORT-ONLY" in w and f"NEXT_EXPERIMENTS_{'FIGHSROOM16e4' if p == 'SRB' else 'FIGHSPATH16e4'} §1 and NEXT_EXPERIMENTS_FIGHSX16e4 §1" in w and "n = 81920 (new trials 10000..91919) at +12/+15 dB" in w and
                "20480 trials are the same trials as the n = 20480 raw's -- Annealed Langevin: the same trials with a new posterior sample; the unseen trials 30480..91919 alone are the '# split' lines of results/review_next/fighs_FX<tag>.txt; one point = one raw, never pooled)" in w
                and f"Asserts passed: counts before the merge (n = 2560, the registered judgement) = pairB_SP{p}.txt" in w, n=5)
            if mode == "hsx12":
                dr = [l for l in rec if l.startswith("DRAWN RANGE")]
                chk(f"G7 paper_f21{pl}hsx12.txt states the drawn range: 'DRAWN RANGE: -3 .. +12 dB only (paper variant, user decision 2026-10-12 CDT -- conf/DECISIONS.md).  The +15 dB point of every curve was measured (n = 81920; ...) and is NOT drawn here; the full-range figure is F21{pl}hsx_col.'; x range (-4, 13.0); the +15 dB counts are in its Counts block and merge block (G1 / G2)",
                    len(dr) == 1 and dr[0].startswith("DRAWN RANGE: -3 .. +12 dB only (paper variant, user decision 2026-10-12 CDT -- conf/DECISIONS.md).  The +15 dB point of every curve was measured (n = 81920; last entry of each row of the Counts block and of the merge block below) and is NOT drawn here; the full-range figure is "
                                                       f"F21{pl}hsx_col.  The lines 'at or below the proposed curve' and 'Zero-failure points' below refer to the drawn points.") and "x range (-4, 13.0)" in w
                    and all(cnt[a][0][6] == (K4(f"FX{srcs(p, a)}", a, 15.0), N4) for a in ORDER), f"caveat words in the hsx12 record -- 'after' / 'seen' / 'chosen': {[x for x in ('after seeing', 'chosen after', 'seed', 'initiali') if x in w]}", n=4 + 11)
            else:
                chk(f"G7 paper_f21{pl}hsx.txt: x range (-4, 16); no DRAWN RANGE line", "x range (-4, 16)" in w and "DRAWN RANGE" not in w)
        # the earlier records must be untouched by this commit
        chk(f"G8 earlier records unchanged by {S6C}: paper_f21{pl}.txt and paper_f21{pl}hs.txt have no diff {RUNC}..{S6C}; their Counts blocks = own recount (original 7 x n 2560; hs: +6..+15 dB n 20480)",
            not sh(f"git diff {RUNC} {S6C} -- {REC}/paper_f21{pl}.txt {REC}/paper_f21{pl}hs.txt {FIGD}/F21{pl}_col.pdf {FIGD}/F21{pl}_col.png {FIGD}/F21{pl}hs_col.pdf {FIGD}/F21{pl}hs_col.png") and
            all(cblock(rd(f"{REC}/paper_f21{pl}hs.txt").split("\n"))[a][0] == MERGED_HS(p, a) for a in ORDER) and
            all(cblock(rd(f"{REC}/paper_f21{pl}.txt").split("\n"))[a][0] == [tuple(OC[srcs(p, a)][a][s]) for s in ALL] for a in ORDER), n=154)
        ris = [l.strip() for l in RECS[p, "hsx"] if "rising:" in l]
        i0 = next(i for i, l in enumerate(S6) if l.startswith(f"### {'6.2a' if p == 'SRB' else '6.2b'} ")); i1 = next((i for i, l in enumerate(S6) if i > i0 and l.startswith("### ")), len(S6))
        blk = S6[i0:i1]
        wantp = {"SRB": "p=2.7e-10", "SRP": "p=2.7e-06"}[p]
        chk(f"E7 §6.2 ({p}) 'rising' line (1 줄) = the hsx record's rising line = own: R3-bigamp +9->+12 dB {wantp} (n = 20480 vs n = 81920); 'y 축 {want_y}' in the same sentence; no other rising cell on any of the 11 merged curves",
            [l[3:-1] for l in blk if l.startswith("- `") and "rising:" in l] == ris == [MINE[p][a].strip() for a in ORDER if "rising:" in MINE[p][a]] and len(ris) == 1 and ris[0].endswith(f"rising: +9->+12 dB {wantp}") and
            any(f"의 '오르는 칸' (한쪽 Fisher p; 보고만): 1 줄. y 축 {want_y}." in l for l in blk), str(ris), n=4)
        allr = {a: [(f"{ALL[i-1]:+.0f}->{ALL[i]:+.0f}", f"{fisher_p(MERGED(p, a)[i], MERGED(p, a)[i-1]):.3g}") for i in rising(MERGED(p, a))] for a in ORDER if rising(MERGED(p, a))}
        ties = {a: [f"{ALL[i-1]:+.0f}->{ALL[i]:+.0f}" for i in range(1, 7) if MERGED(p, a)[i][0] * MERGED(p, a)[i-1][1] == MERGED(p, a)[i-1][0] * MERGED(p, a)[i][1]] for a in ORDER}
        print(f"   {p}: all rising cells of the 11 merged curves: {allr}; ties (equal BLER, not 'rising'): { {a: v for a, v in ties.items() if v} }")
        print(f"   {p}: the +12 -> +15 dB cell restricted to the unseen trials (30480..91919), k12 -> k15: " + ", ".join(f"{a} {KU(f'FX{srcs(p, a)}', a, 12.0)}->{KU(f'FX{srcs(p, a)}', a, 15.0)}" for a in ORDER))

    # ====================================================================== F. §6.3 predictions
    print("\n# F. §6.3 predictions (scored by me against the frozen §3 wording)", flush=True)
    LOGALL = rd("logs/run_fighsx16e4.log").split("\n")
    LOG = [l for l in LOGALL if l.startswith("[fighs ")]
    done = [l for l in LOG if "FIGHS_DONE" in l]; starts = [l for l in LOG if "start (git" in l]
    kv = {p: [K4(f"FX{p}B16e4", V, s) for s in HX] for p in PRS}; kb = {p: [K4(f"FX{p}B16e4", B, s) for s in HX] for p in PRS}
    uv = {p: [KU(f"FX{p}B16e4", V, s) for s in HX] for p in PRS}; ub = {p: [KU(f"FX{p}B16e4", B, s) for s in HX] for p in PRS}
    p2 = {a: [fisher_p(MERGED("SRB", a)[i], MERGED("SRB", a)[i - 1]) for i in rising(MERGED("SRB", a)) if i >= 5] for a in (V, B, GE)}
    lo3, hi3 = wilson(3, N2); lo4, hi4 = wilson(4, N2)
    r4a = [k for k in range(0, 200) if lo3 <= k / N4 <= hi3]; r4b = [k for k in range(0, 200) if lo4 <= k / N4 <= hi4]
    sc = {"1": kv["SRB"][1] <= kv["SRB"][0], "2": all(x >= 0.05 for v in p2.values() for x in v), "3a": kv["SRB"][0] <= kb["SRB"][0], "3b": kv["SRB"][1] <= kb["SRB"][1],
          "4a": 5 <= kv["SRB"][0] <= 35, "4b": 7 <= kv["SRB"][1] <= 41, "5": kv["SRP"][1] <= kv["SRP"][0], "6a": kv["SRP"][0] <= kb["SRP"][0], "6b": kv["SRP"][1] <= kb["SRP"][1],
          "7": len(done) == 1 and done[0].endswith("FIGHS_DONE ok=6 fail=0"), "8": okP8}
    got = {m[1]: m[2] for l in S6 for m in [re.match(r"^(\d[ab]?)\. .*?→ \*\*(적중|빗나감)\*\*", l)] if m}
    want = {k: ("적중" if v else "빗나감") for k, v in sc.items()}
    chk("F1 §6.3: 11 scored items (1, 2, 3a, 3b, 4a, 4b, 5, 6a, 6b, 7, 8); the record's verdicts = my own scoring from the raws / logs: ten hits and one miss (7)",
        got == want and list(got) == ["1", "2", "3a", "3b", "4a", "4b", "5", "6a", "6b", "7", "8"] and sum(v == "적중" for v in got.values()) == 10 and got["7"] == "빗나감",
        f"V1 SRB {kv['SRB']} (unseen {uv['SRB']}), b* SRB {kb['SRB']} (unseen {ub['SRB']}); V1 SRP {kv['SRP']} (unseen {uv['SRP']}), b* SRP {kb['SRP']} (unseen {ub['SRP']}); rising p on V1 / b* / genie (+9..+15) {p2}; FIGHS_DONE lines {[l[-12:] for l in done]}; got {got}", n=11)
    chk("F2 §6.3 quoted numbers: 1 (12 → 11; 보지 않은 시행 9 → 7); 2 '없음' x3; 3a (12 대 32; 9 대 21); 3b (11 대 15; 7 대 9); 4a (12); 4b (11); 5 (4 → 1; 4 → 1); 6a (4 대 14; 4 대 11); 6b (1 대 6; 1 대 5); 7 'ok=5 fail=1; 시작 줄 3 개; … 6 / 6'",
        all(any(l.startswith(a) and b in l for l in S6) for a, b in (("1. ", "(12 → 11; 보지 않은 시행 9 → 7)."), ("2. ", "M-ours-dscore-C-V1 없음, M-ours-bstar 없음, R5-genie 없음"), ("3a. ", "(12 대 32; 보지 않은 시행 9 대 21)."),
            ("3b. ", "(11 대 15; 보지 않은 시행 7 대 9)."), ("4a. ", "(12)."), ("4b. ", "(11)."), ("5. ", "(4 → 1; 보지 않은 시행 4 → 1)."), ("6a. ", "(4 대 14; 보지 않은 시행 4 대 11)."), ("6b. ", "(1 대 6; 보지 않은 시행 1 대 5)."),
            ("7. ", "(첫 실행의 종료 줄 ok=5 fail=1; 시작 줄 3 개; 재개까지 마친 뒤 수용 파일이 `ACCEPT: OK` 인 행 6 / 6")))
        and kv == {"SRB": [12, 11], "SRP": [4, 1]} and kb == {"SRB": [32, 15], "SRP": [14, 6]} and uv == {"SRB": [9, 7], "SRP": [4, 1]} and ub == {"SRB": [21, 9], "SRP": [11, 5]} and not any(p2.values()), n=24)
    s3 = "\n".join(reg[next(i for i, l in enumerate(reg) if l.startswith("## 3. ")):next(i for i, l in enumerate(reg) if l.startswith("## 5. "))])
    chk("F3 prediction 4's frozen ranges are what the Wilson intervals of 3 / 20480 and 4 / 20480 give: k / 81920 inside [4.98e-05, 4.31e-04] <=> k in 5..35; inside [7.60e-05, 5.02e-04] <=> k in 7..41; the §6.3 paraphrases keep the §3 content",
        (r4a[0], r4a[-1], r4b[0], r4b[-1]) == (5, 35, 7, 41) and (f"{lo3:.2e}", f"{hi3:.2e}", f"{lo4:.2e}", f"{hi4:.2e}") == ("4.98e-05", "4.31e-04", "7.60e-05", "5.02e-04") and
        all(x in s3 for x in ("Proposed (V1) 의 실패 수 +15 dB ≤ +12 dB", "Fisher p < 0.05 인 \"오르는 칸\" 이 없다(+9 → +12 → +15 dB 칸", "+12 dB 에서 5..35, +15 dB 에서 7..41", "`FIGHS_DONE ok=6 fail=0`", "ALD-pilot 을 뺀 모든 arm × `common.KEYS_RAW`")),
        f"own: 3/20480 [{lo3:.3e}, {hi3:.3e}] -> k {r4a[0]}..{r4a[-1]}; 4/20480 [{lo4:.3e}, {hi4:.3e}] -> k {r4b[0]}..{r4b[-1]}", n=8)

    # ====================================================================== H. run log, runner logs, manifests, mtimes, git
    print("\n# H. logs / timeline", flush=True)
    def tsl(l):
        m = re.match(r"\[fighs (\d\d)-(\d\d) (\d\d):(\d\d) CDT\]", l)
        return datetime(2026, int(m[1]), int(m[2]), int(m[3]), int(m[4]), tzinfo=CDT) if m else None
    chk("H1 run log: THREE start lines (first pass 'rows: all resume=0' 10-11 20:40; 'rows: FXALDSRP resume=1' 10-12 04:40; 'rows: FXSRPB16e4 FXALDSRP resume=1' 10-12 04:41), all on git 037c6610; three FIGHS_DONE lines (ok=5 fail=1 04:09; ok=0 fail=1 04:41; ok=2 fail=0 04:58 = the last line)",
        starts == ["[fighs 10-11 20:40 CDT] start (git 037c6610) rows: all resume=0 skip0 10000 n 81920 SNR 12 15", "[fighs 10-12 04:40 CDT] start (git 037c6610) rows: FXALDSRP resume=1 skip0 10000 n 81920 SNR 12 15",
                   "[fighs 10-12 04:41 CDT] start (git 037c6610) rows: FXSRPB16e4 FXALDSRP resume=1 skip0 10000 n 81920 SNR 12 15"] and
        done == ["[fighs 10-12 04:09 CDT] FIGHS_DONE ok=5 fail=1", "[fighs 10-12 04:41 CDT] FIGHS_DONE ok=0 fail=1", "[fighs 10-12 04:58 CDT] FIGHS_DONE ok=2 fail=0"] and LOG[-1] == done[-1], n=6)
    ops_own = [l for l in LOG if re.search(r"\] start \(git|phase C done|FIGHS_DONE|ABORT|SKIP|INVALID|FAILED|[Ff]ailed|rc=[1-9]|HEAD moved", l)]
    i61 = next(i for i, l in enumerate(S6) if l.startswith("### 6.1 ")); itab = next(i for i, l in enumerate(S6) if l.startswith("| 행 | 시작 (CDT)"))
    ops_rec = [l[3:-1] for l in S6[i61:itab] if l.startswith("- `[fighs ")]
    chk("H2 §6.1 list of operational lines (12) = every start / phase C done / FIGHS_DONE / ABORT / SKIP / INVALID / failed / rc!=0 line of the run log, verbatim and in order; the intro sentence '실행 커밋 037c6610; 시작 줄 3 개(첫 실행 + `--resume` 2 번), `FIGHS_DONE` 줄 3 개'",
        ops_rec == ops_own and len(ops_own) == 12 and any("`bash code/run_fighsx16e4.sh`, 실행 커밋 037c6610; 시작 줄 3 개(첫 실행 + `--resume` 2 번), `FIGHS_DONE` 줄 3 개." in l for l in S6), f"own {len(ops_own)} lines; record {len(ops_rec)}", n=12 + 3)
    print("   run-log lines NOT in the §6.1 list (other than run / acceptance / manifest lines): " + " || ".join(l[:150] for l in LOGALL if l and l not in ops_own and not re.search(r"\] FX\w+ (run:|acceptance rc=0)|^\{\"git_commit\"|^-> /home", l)))
    pc = [l for l in LOG if "phase C done" in l]
    chk("H3 three 'phase C done: 6 receiver control(s) OK, 2 ALD estimator control(s) OK' lines (20:44, 04:41, 04:42); ALD estimator control lines: FXALDSRB + FXALDSRP on GPU 1 at 20:40, FXALDSRP again at 04:40 and 04:41 (both resumes re-ran it on GPU 1); new-trial regen + estimate lines FXALDSRB 23:45 GPU 1, FXALDSRP 04:43 GPU 1, 'rotation none'; '[ald regen] PIL{SRB,SRP} hisnr4: 2 SNR x 81920 trials (skip 10000)'",
        [l[:23] for l in pc] == ["[fighs 10-11 20:44 CDT]", "[fighs 10-12 04:41 CDT]", "[fighs 10-12 04:42 CDT]"] and all(l.endswith("phase C done: 6 receiver control(s) OK, 2 ALD estimator control(s) OK") for l in pc) and
        [l[:23] + l.split("]")[1][:10] for l in LOG if "ALD estimator control: ald.py estimate" in l] == ["[fighs 10-11 20:40 CDT] FXALDSRB ", "[fighs 10-11 20:40 CDT] FXALDSRP ", "[fighs 10-12 04:40 CDT] FXALDSRP ", "[fighs 10-12 04:41 CDT] FXALDSRP "] and
        all("on GPU 1 " in l for l in LOG if "ALD estimator control: ald.py estimate" in l) and
        "[fighs 10-11 23:45 CDT] FXALDSRB ALD PILSRB: regen (CPU) + estimate (GPU 1) on trials 10000.., rotation none (tune record results/ald/tune_PILSRB.json)" in LOG and
        "[fighs 10-12 04:43 CDT] FXALDSRP ALD PILSRP: regen (CPU) + estimate (GPU 1) on trials 10000.., rotation none (tune record results/ald/tune_PILSRP.json)" in LOG and
        sum(bool(re.match(r"\[ald regen\] PILSR[BP] hisnr4: 2 SNR x 81920 trials \(skip 10000\) rotation=None doppler=None", l)) for l in LOGALL) == 2, n=12)
    RUN, ACC = {}, {}
    for l in LOG:
        m = re.match(r"\[fighs [^\]]+\] (FX\w+) run: (.*)$", l)
        if m: RUN.setdefault(m[1], []).append((tsl(l), m[2]))
        m = re.match(r"\[fighs [^\]]+\] (FX\w+) acceptance rc=(\d+) \((.*)\)", l)
        if m: ACC.setdefault(m[1], []).append((tsl(l), int(m[2]), m[3].strip()))
    def want_run(t):
        r = ROW[t]; a = f"--testbed D2 --prior {r['PR']} --cell C2 --chunk 40 --ntrain 160000"
        if r["CK"] != "-": a += f" --stagec-ckpt /home/HTJ/t2/conf/{r['CK']}"
        if r["PICK"] != "-": a += f" --sparse-file {r['PICK'].split(':')[0]}"
        return f"{a} {r['FL']} --snr 12 15 --n 81920 --skip0 10000 --arm {r['ARMS']}"
    chk("H4 'run:' lines: one per row, two for FXSRPB16e4 (first pass + the 04:42 resume), each carrying exactly the §1 runner flags (prior, C2, chunk 40, ntrain 160000, ckpt / pick / ald-file, SNR 12 15, n 81920, skip0 10000, the row's arms); acceptance lines rc=0 'ACCEPT: OK -- <tag> ACCEPT (f): OK' (7 = 6 rows + the re-acceptance of FXSRPB16e4)",
        {t: len(v) for t, v in RUN.items()} == {**{t: 1 for t in TAGS}, "FXSRPB16e4": 2} and all(x[1] == want_run(t) for t in TAGS for x in RUN[t]) and
        {t: len(v) for t, v in ACC.items()} == {**{t: 1 for t in TAGS}, "FXSRPB16e4": 2} and all(x[1] == 0 and x[2] == f"ACCEPT: OK -- {t} ACCEPT (f): OK" for t in TAGS for x in ACC[t]), n=14)
    rows61 = {}
    for l in S6:
        m = re.match(r"^\| (FX\w+) \| (.+?) \| (.+?) 분 · (\d+) 작업 · (\d+) 워커 \| (\d+) / (\d+) \| (.+?) \| (.*?) \| (\w+) · (\w+) \| (.*?) \|$", l)
        if m: rows61[m[1]] = m.groups()
    bad = []; RMIN = {}; MAN = {}
    for t in TAGS:
        rl = rd(f"logs/run_D2_{t}.log").split("\n")
        hd = [l for l in rl if l.startswith("# run_fighs")]
        mins = re.findall(r"\[run\] finished in ([\d.]+) min", "\n".join(rl)); tasks = re.findall(r"-> (\d+) tasks on (\d+) workers", "\n".join(rl))
        nd, ne = sum(bool(re.match(r"\d+/\d+ done ", l)) for l in rl), sum(bool(re.match(r"\d+/\d+ exists ", l)) for l in rl)
        dn = [m[1] for l in rl for m in [re.match(r"\d+/\d+ done\s+(\S+\.npz)", l)] if m]; ex = [m[1] for l in rl for m in [re.match(r"\d+/\d+ exists\s+(\S+\.npz)", l)] if m]
        af = rd(f"{RV}/{t}_accept.txt"); v = "; ".join(x.strip() for x in af.split("\n") if x.startswith("ACCEPT"))
        man = json.load(open(f"{RV}/run_manifest_{t}.json")); MAN[t] = man
        c = t.replace("FX", "FXC", 1)
        ctl = rd(f"{RV}/{c}_control.txt").strip().split("\n")[-1]
        if "ALD" in t: ctl += " · " + rd(f"{RV}/{c}_aldcontrol.txt").strip().split("\n")[-1]
        RMIN[t] = mins
        want = (t, " · ".join(f"{x[0]:%m-%d %H:%M}" for x in RUN[t]), " · ".join(mins), tasks[-1][0], tasks[-1][1], str(nd), str(ne), " · ".join(f"{x[0]:%m-%d %H:%M}" for x in ACC[t]),
                f"rc={ACC[t][-1][1]}; {v}", man["git_commit"], man["config_hash"], ctl)
        if rows61.get(t) != want: bad.append((t, rows61.get(t), want))
        files = {o["file"] for o in BY[t]}
        res_ = 1 if t == "FXALDSRP" else 0
        whd = [f"# run_fighsx16e4 git {RUNC} 2026-{RUN[t][0][0]:%m-%d %H:%M} CDT resume={res_}"] + ([f"# run_fighsx16e4 git {RUNC} 2026-{RUN[t][1][0]:%m-%d %H:%M} CDT resume=1"] if t == "FXSRPB16e4" else [])
        if hd != whd or nd != 4096 or set(dn) != files or len(dn) != 4096 or tasks != [("4096", "192")] * len(whd): bad.append((t, "runner log", hd, mins, nd, ne, tasks, len(dn)))
        if t == "FXSRPB16e4":
            i2 = rl.index(whd[1]); sec2 = rl[i2:]
            if ne != 4096 or set(ex) != files or len(ex) != 4096 or any(re.match(r"\d+/\d+ done ", l) for l in sec2) or mins != ["154.2", "0.0"]: bad.append((t, "resume section", ne, len(ex), mins))
        elif ne != 0 or len(mins) != 1: bad.append((t, "exists/mins", ne, mins))
        if re.search(r"Traceback|Error", "\n".join(rl)): bad.append((t, "Traceback/Error in runner log"))
        if man["n_raw_files"] != 4096 or sorted(man["arms"]) != sorted(ROW[t]["ARMS"].split()) or man["git_commit"] != RUNC or man["config_hash"] != "cf706d8f5999293c": bad.append((t, "manifest", man["n_raw_files"], man["arms"]))
        if man["trial_stream"].get("skip_min") != 10000 or man["trial_stream"].get("skip_max_end") != 91920 or set(man["points"].values()) != {N4} or len(man["points"]) != 2: bad.append((t, "manifest trial_stream/points", man["trial_stream"], man["points"]))
        w = datetime.strptime(man["written"], "%Y-%m-%d %H:%M:%S KST").replace(tzinfo=KST)
        if not (RUN[t][-1][0] <= w <= ACC[t][-1][0] + timedelta(minutes=1)): bad.append((t, "manifest written outside the LAST run..acceptance window", man["written"]))
        if not (RUN[t][0][0] <= cdt(MT[t][0]) and cdt(MT[t][1]) <= ACC[t][0][0] + timedelta(minutes=1)): bad.append((t, "chunk mtimes outside the FIRST run..acceptance window", cdt(MT[t][0]), cdt(MT[t][1])))
        if f"run|git ['{RUNC}']" not in af or not re.search(r"raised trials per arm \(= failures, report only\) 0\n", af) or not af.startswith(f"ACCEPT: OK -- {t}\n"): bad.append((t, "accept file", af))
    chk("H5 §6.1 per-row table (6 rows: start time(s), runner minutes 77.9 / 100.7 / 4.3 / 154.2 · 0.0 / 92.0 / 4.5, 4096 tasks, 192 workers, done / exists 4096 / 0 (FXSRPB16e4: 4096 / 4096), acceptance time(s), verdicts, manifest git 037c6610 · config_hash cf706d8f5999293c, control verdicts) = logs + files; runner logs: 4096 'done' lines naming exactly the 4096 chunk files; FXSRPB16e4's resume section = 4096 'exists' naming exactly the 4096 files, no 'done', 0.0 min; headers resume=0 except FXALDSRP (resume=1) and FXSRPB16e4's second; no Traceback; manifests 4096 files / arms / trial_stream 10000..91920 / 2 points x 81920; chunk mtimes inside each row's FIRST run..acceptance window",
        not bad and len(rows61) == 6 and [RMIN[t] for t in TAGS] == [["77.9"], ["100.7"], ["4.3"], ["154.2", "0.0"], ["92.0"], ["4.5"]], str(bad[:2]), n=6 * 12 + 6 * 8)
    print("   manifests written: " + " · ".join(f"{t} {MAN[t]['written']}" for t in TAGS))
    t_lim = datetime(2026, 10, 12, 2, 36, tzinfo=CDT)
    chk("H6 no chunk of raw_FXSRPB16e4 was rewritten by the resume: all 4096 mtimes before 10-12 02:36 CDT (inside 00:00..02:35, the first-pass window); raw_FXALDSRP chunks all inside the 04:52..04:58 CDT resume window; raw_FXSPSRP untouched after 04:09",
        cdt(MT["FXSRPB16e4"][1]) < t_lim and cdt(MT["FXSRPB16e4"][0]) >= datetime(2026, 10, 12, 0, 0, tzinfo=CDT) and datetime(2026, 10, 12, 4, 52, tzinfo=CDT) <= cdt(MT["FXALDSRP"][0]) and cdt(MT["FXALDSRP"][1]) < datetime(2026, 10, 12, 4, 59, tzinfo=CDT)
        and cdt(MT["FXSPSRP"][1]) < datetime(2026, 10, 12, 4, 10, tzinfo=CDT), f"FXSRPB16e4 {cdt(MT['FXSRPB16e4'][0]):%H:%M:%S}–{cdt(MT['FXSRPB16e4'][1]):%H:%M:%S}; FXALDSRP {cdt(MT['FXALDSRP'][0]):%H:%M:%S}–{cdt(MT['FXALDSRP'][1]):%H:%M:%S}", n=3)
    manl = [l for l in LOGALL if l.startswith('{"git_commit"') and '"FXSRPB16e4"' in l]
    chk("H7 the base row's manifest summary printed into the run log at 02:35 (first pass) and at 04:42 (resume) is the same line (git, config_hash, n_raw_files 4096, arms); the manifest file itself was rewritten ('written' 2026-10-12 18:42:43 KST = 04:42:43 CDT)",
        len(manl) == 2 and manl[0] == manl[1] and MAN["FXSRPB16e4"]["written"] == "2026-10-12 18:42:43 KST", n=2)
    fl = [l for l in S6 if l.startswith("- `(f) raw_")]
    chk("H8 §6.1 '(f)' lines (6) = the accept files' (f) lines verbatim; every one says run|git ['037c6610'] and 'raised trials per arm (= failures, report only) 0' (N-7: 0 for ALD-pilot too)",
        fl == [f"- `{x.strip()}`" for t in TAGS for x in rd(f"{RV}/{t}_accept.txt").split("\n") if x.strip().startswith("(f)")] and len(fl) == 6 and all(l.endswith("raised trials per arm (= failures, report only) 0`") for l in fl), n=6)
    okA_ = True
    for t in TAGS:
        r = ROW[t]; pk = r["PICK"].split(":")[0] if r["PICK"] != "-" else "-"; al = r["FL"].split()[-1] if r["FL"] else "-"
        own = f"ACCEPT: OK -- {t}\n  (f) raw_{t}: 4096 chunk files, run|git ['{RUNC}']; pick {pk}; rotation -; ald {al}; raised trials per arm (= failures, report only) 0\nACCEPT (f): OK\n"
        okA_ &= rd(f"{RV}/{t}_accept.txt") == own and rd(f"{AUD}/rerun_fighsx_accept_{t}.txt") == f"ACCEPT: OK -- {t}\n" if os.path.exists(f"{AUD}/rerun_fighsx_accept_{t}.txt") else rd(f"{RV}/{t}_accept.txt") == own
    chk("H8b the six accept files are byte-identical to the text that follows from my own findings (first line = my eval_accept re-run rerun_fighsx_accept_<tag>.txt; the (f) line from B2 / B3 / B5; 'ACCEPT (f): OK') -- so FXSRPB16e4_accept.txt, rewritten by the 04:42 CDT resume, holds what the unchanged raw yields",
        okA_, n=6)
    gl = sh(f"git log --format='%h %ci' {RUNC}^..{S6C}").split("\n")
    trun = datetime.strptime(sh(f"git log -1 --format=%ci {RUNC}"), "%Y-%m-%d %H:%M:%S %z"); ts6 = datetime.strptime(sh(f"git log -1 --format=%ci {S6C}"), "%Y-%m-%d %H:%M:%S %z")
    rf = [l for l in sh("git reflog --date=iso -40").split("\n") if "HEAD@{2026-10-12" in l]
    between = [l for l in rf for m in [re.search(r"HEAD@\{(\S+ \S+ \S+)\}", l)] if m and trun < datetime.strptime(m[1], "%Y-%m-%d %H:%M:%S %z") < ts6]
    chk("H9 git: no commit between 037c6610 (10-11 20:40:06 CDT, same minute as the start line) and 4c536f1b (10-12 05:04:02 CDT, after the last FIGHS_DONE 04:58); the reflog has no HEAD movement between them (no checkout / reset / amend)",
        gl == [f"{S6C} 2026-10-12 19:04:02 +0900", f"{RUNC} 2026-10-12 10:40:06 +0900"] and not between and ts6.astimezone(CDT) > cdt(os.stat("logs/run_fighsx16e4.log").st_mtime),
        f"{trun.astimezone(CDT):%m-%d %H:%M:%S} .. {ts6.astimezone(CDT):%m-%d %H:%M:%S} CDT; reflog entries strictly between: {between}", n=4)
    T0 = trun.astimezone(CDT)
    paths = [f"raw_{t}" for t in TAGS] + [f"raw_{t.replace('FX', 'FXC', 1)}" for t in TAGS] + [f"results/ald/{x}_PIL{p}_hisnr4.npz" for p in PRS for x in ("ald", "pilots")] + \
            [f"results/ald/ald_FXCALD{p}.npz" for p in PRS] + [f"results/ald/tune_FXCALD{p}.json" for p in PRS] + [f"{RV}/{t.replace('FX', 'FXC', 1)}_control.txt" for t in TAGS]
    def first_m(p): return min([os.stat(os.path.join(p, f)).st_mtime for f in os.listdir(p)] + [os.stat(p).st_mtime]) if os.path.isdir(p) else os.stat(p).st_mtime
    pre = [p for p in paths if cdt(first_m(p)) < T0]
    chk("H10 §5 '실행 시작 전 상태: raw_FX* · raw_FXC* · ald_PIL{SRB,SRP}_hisnr4.npz · FXC 대조 파일 없음': every such path (and every file in the raw dirs) has an mtime at or after the run commit 20:40:06 CDT", not pre, str(pre), n=len(paths))
    newer = sorted(os.path.join(d, f) for r in ("code", "../Demo") for d, ds, fs in os.walk(r) for f in fs + ds if os.lstat(os.path.join(d, f)).st_mtime > trun.timestamp())
    chk("H11 no file or directory under conf/code or Demo has an mtime after the run commit (os.walk); `git diff 037c6610 4c536f1b -- conf/code Demo` empty (§6.4 'conf/code · Demo 는 실행 커밋 그대로다')", not newer and not sh(f"git diff --stat {RUNC} {S6C} -- code ../Demo"), str(newer[:5]), n=2)
    W = [l for l in rd("logs/fx_resume_watch.log").split("\n") if l]
    FG = [l for l in rd("logs/fighsx_figs.log").split("\n") if l]
    chk("H12 fx_resume_watch.log: watching from 10-12 04:12 CDT, '[watch 10-12 04:39 CDT] GPU 1 free -> bash code/run_fighsx16e4.sh --resume FXALDSRP (once)', RESUME_WATCH_DONE 04:39 (the watcher's one resume = the 04:39 precondition ABORT; the 04:40 and 04:41 resumes are not in this log); fighsx_figs.log: 'SRB hsx figure OK' 00:03, 'SRP rows not all accepted -- no SRP figure' 04:10, FIGS_DONE 04:10 -> the helper never drew the SRP figure",
        W[0] == "[watch 10-12 04:12 CDT] watching for a free GPU (HEAD must stay 037c6610)" and W[1] == "[watch 10-12 04:39 CDT] GPU 1 free -> bash code/run_fighsx16e4.sh --resume FXALDSRP (once)" and W[-1] == "[watch 10-12 04:39 CDT] RESUME_WATCH_DONE" and len(W) == 4 and
        FG[0] == "[figs 10-12 00:03 CDT] SRB hsx figure OK" and FG[1] == "[figs 10-12 04:10 CDT] SRP rows not all accepted -- no SRP figure" and FG[2].startswith("[figs 10-12 04:10 CDT] FIGS_DONE (") and len(FG) == 3, n=7)
    SR = [l for l in rd("logs/seeds_SRB_train.log").split("\n") if l]
    chk("H13 seeds_SRB_train.log vs §6.4: SRB a2 on GPU 0 and a3 on GPU 2 from 10-11 19:26 CDT; a2 SEEDS_TRAIN_DONE 10-12 00:55, a3 SEEDS_TRAIN_DONE 10-12 01:33",
        SR[0] == "[seeds 10-11 19:26 CDT] SRB a2 start (git c48ee796) GPU 0 pin 20,116" and SR[1] == "[seeds 10-11 19:26 CDT] SRB a3 start (git c48ee796) GPU 2 pin 22,118" and
        "[seeds 10-12 00:55 CDT] SRB a2 SEEDS_TRAIN_DONE" in SR and "[seeds 10-12 01:33 CDT] SRB a3 SEEDS_TRAIN_DONE" in SR, n=4)

    # ====================================================================== I. §6.4 / EXPERIMENTS row / DECISIONS
    print("\n# I. §6.4, EXPERIMENTS, DECISIONS", flush=True)
    S64 = S6[next(i for i, l in enumerate(S6) if l.startswith("### 6.4 ")):]
    FT = {f: cdt(os.stat(f"{FIGD}/{f}").st_mtime) for f in ("F21srbhsx_col.pdf", "F21srbhsx_col.png", "records/paper_f21srbhsx.txt", "F21srphsx_col.pdf", "F21srphsx_col.png", "records/paper_f21srphsx.txt",
                                                            "F21srbhsx12_col.pdf", "F21srbhsx12_col.png", "records/paper_f21srbhsx12.txt", "F21srphsx12_col.pdf", "F21srphsx12_col.png", "records/paper_f21srphsx12.txt", "paper_f21dmc.py", "fighs_merge.py")}
    chk("I1 §6.4 figure times: F21srbhsx_col.{pdf,png} + record 10-12 00:03 CDT (after FXALDSRB's acceptance 00:00, while the SRP rows ran); F21srphsx_col + record 10-12 04:59 CDT (after the last FIGHS_DONE 04:58); paper_f21dmc.py mtime 10-12 00:32 CDT (between the two; the hsx12 mode), fighs_merge.py unchanged since 10-11 19:54; hsx12 files SRB 00:36, SRP 05:00; §6 header '기록 2026-10-12 05:02 CDT' = registration mtime minute",
        all(f"{FT[f]:%m-%d %H:%M}" == "10-12 00:03" for f in ("F21srbhsx_col.pdf", "F21srbhsx_col.png", "records/paper_f21srbhsx.txt")) and all(f"{FT[f]:%m-%d %H:%M}" == "10-12 04:59" for f in ("F21srphsx_col.pdf", "F21srphsx_col.png", "records/paper_f21srphsx.txt")) and
        f"{FT['paper_f21dmc.py']:%m-%d %H:%M}" == "10-12 00:32" and f"{FT['fighs_merge.py']:%m-%d %H:%M}" == "10-11 19:54" and f"{FT['F21srbhsx12_col.pdf']:%m-%d %H:%M}" == "10-12 00:36" and f"{FT['F21srphsx12_col.pdf']:%m-%d %H:%M}" == "10-12 05:00" and
        f"{cdt(os.stat(REG).st_mtime):%m-%d %H:%M}" == "10-12 05:02" and S6[0].startswith("## 6. 결과 (기록 2026-10-12 05:02 CDT, Opus 5.5") and
        any("(10-12 00:03 CDT" in l and "(10-12 04:59 CDT" in l and "(10-12 00:32 CDT" in "\n".join(S64) for l in S64), " ".join(f"{f} {t:%m-%d %H:%M:%S}" for f, t in FT.items()), n=10)
    chk("I2 §6.4 'ald_PILSRB_hisnr4.npz sha256[:16] dcdce65b032899b1, ald_PILSRP_hisnr4.npz 2608bcf1c02fe80c' = disk (A7); file mtimes 10-11 23:54 / 10-12 04:52 CDT (estimate '04:43 → 04:52 CDT': regen line 04:43, pilots file 04:43, estimate file 04:52, run line 04:52)",
        any("`ald_PILSRB_hisnr4.npz` sha256[:16] dcdce65b032899b1, `ald_PILSRP_hisnr4.npz` 2608bcf1c02fe80c." in l for l in S64) and
        f"{cdt(os.stat('results/ald/ald_PILSRP_hisnr4.npz').st_mtime):%m-%d %H:%M}" == "10-12 04:52" and f"{cdt(os.stat('results/ald/pilots_PILSRP_hisnr4.npz').st_mtime):%m-%d %H:%M}" == "10-12 04:43" and
        f"{cdt(os.stat('results/ald/ald_PILSRB_hisnr4.npz').st_mtime):%m-%d %H:%M}" == "10-11 23:54" and any("추정(GPU 1, 04:43 → 04:52 CDT) + runner 4.5 분 → 04:58 CDT `ACCEPT: OK`, `FIGHS_DONE ok=2 fail=0`" in l for l in S64), n=6)
    pre6 = "\n".join(reg[:i6])
    chk("I3 §6.4 cost line: '§1 의 비용 추정(단계 C ≈ 10 분; 80 · 103 · 13 분; SRP 160 · 90 · 13 분; 합 ≈ 8 시간) 대비 실측 runner 77.9 · 100.7 · 4.3 분, 154.2 · 92.0 · 4.5 분; 첫 실행 10-11 20:40 → 10-12 04:09 CDT (7 시간 29 분), 재개까지 04:58 CDT' = §1 estimates + runner logs + log times (04:09 − 20:40 = 7 h 29 min)",
        any("§1 의 비용 추정(단계 C ≈ 10 분; 80 · 103 · 13 분; SRP 160 · 90 · 13 분; 합 ≈ 8 시간) 대비 실측 runner 77.9 · 100.7 · 4.3 분, 154.2 · 92.0 · 4.5 분; 첫 실행 10-11 20:40 → 10-12 04:09 CDT (7 시간 29 분), 재개까지 04:58 CDT." in l for l in S64) and
        all(x in pre6 for x in ("단계 C ≈ 10 분", "FXSRBB16e4 ≈ 80 분", "FXSPSRB ≈ 103 분", "FXALDSRB ≈ 13 분", "FXSRPB16e4 ≈ 160 분", "FXSPSRP ≈ 90 분", "FXALDSRP ≈ 13 분", "합 ≈ 8 시간")) and
        (tsl(done[0]) - tsl(starts[0])) == timedelta(hours=7, minutes=29), n=10)
    DEC = rd("DECISIONS.md").split("\n")
    d1434 = [l for l in DEC if l.startswith("`[2026-10-12 14:34 KST] ")]
    chk("I4 the DECISIONS lines quoted in §6.4 exist verbatim: one '`[2026-10-12 14:34 KST] Sionna 방 그림의 원고판은 +12 dB 까지 그린다 (사용자 결정; …' line holding both user quotes ('12dB 까지만 paper에 포함시키는 방안도 고려해봐야겠어', '우리에게 유리하지 않은 것을 굳이 넣을 필요는 없어.') and '이 결정은 +15 dB 결과를 본 뒤의 제시 선택임을 여기 적어 둔다'; its numbers (Proposed 12 / 11, GMM b* 32 / 15, Perfect CSI 5 / 4; SRB rows accepted 10-12 00:00 CDT) = own; §6.4 quotes both sentences verbatim",
        len(d1434) == 1 and "Sionna 방 그림의 원고판은 +12 dB 까지 그린다 (사용자 결정; Opus 5.5; 텍사스 10-12 00:34 CDT)" in d1434[0] and "'12dB 까지만 paper에 포함시키는 방안도 고려해봐야겠어'" in d1434[0] and "'우리에게 유리하지 않은 것을 굳이 넣을 필요는 없어.'" in d1434[0] and
        "이 결정은 +15 dB 결과를 본 뒤의 제시 선택임을 여기 적어 둔다" in d1434[0] and "실패 수 / 81920 (+12 / +15 dB) Proposed 12 / 11, GMM b* 32 / 15, Perfect CSI 5 / 4" in d1434[0] and "10-12 00:00 CDT 수용" in d1434[0] and
        [K4("FXSRBB16e4", a, s) for a in (V, B, GE) for s in HX] == [12, 11, 32, 15, 5, 4] and f"{ACC['FXALDSRB'][0][0]:%m-%d %H:%M}" == "10-12 00:00" and
        any("\"12dB 까지만 paper에 포함시키는 방안도 고려해봐야겠어\" · \"우리에게 유리하지 않은 것을 굳이 넣을 필요는 없어.\"" in l and "`DECISIONS.md` 10-12 14:34 KST 줄" in l for l in S64) and
        sh(f"git log -S'원고판은 +12 dB 까지 그린다' --format=%h -- DECISIONS.md").split("\n")[-1] == S6C, n=12)
    dwork = "/tmp/claude-1005/-home-HTJ-t2/b187bcb3-67a6-4fa2-86ce-8a8ed017508c/scratchpad/DECISIONS.md.working"
    if os.path.exists(dwork):
        wk = rd(dwork).split("\n"); old_dec = sh(f"git show {RUNC}:./DECISIONS.md").split("\n")
        add = [l for l in wk if l and l not in set(old_dec)]
        print(f"   scratch DECISIONS.md.working (mtime {cdt(os.stat(dwork).st_mtime):%m-%d %H:%M:%S} CDT): {len(add)} line(s) not in the {RUNC} version: {[l[:34] for l in add]}; both are in today's DECISIONS.md verbatim: {all(l in DEC for l in add)}")
    SCR = "/tmp/claude-1005/-home-HTJ-t2/b187bcb3-67a6-4fa2-86ce-8a8ed017508c/scratchpad"      # session scratch (may vanish): supporting evidence only, no check depends on it
    if os.path.exists(f"{SCR}/srp_interim/rec_hsx.txt"):
        ir = rd(f"{SCR}/srp_interim/rec_hsx.txt").split("\n"); ic = cblock(ir); fc = cblock(RECS["SRP", "hsx"])
        print(f"   scratch srp_interim/rec_hsx.txt (mtime {cdt(os.stat(f'{SCR}/srp_interim/rec_hsx.txt').st_mtime):%m-%d %H:%M:%S} CDT, before the resumes; merge asserts raw == count table): "
              f"counts of the 10 non-ALD curves equal the final record's: {all(ic[a][0] == fc[a][0] for a in ORDER if a != 'ALD-pilot')} (so the FIRST-pass fighs_FXSRPB16e4.txt / fighs_FXSPSRP.txt held the same counts); "
              f"ALD-pilot row there: {ic['ALD-pilot'][0][5:]} = the n = 20480 points; its merge line: {[l.strip()[-80:] for l in ir if l.strip().startswith('ALD-pilot') and '@16' in l]}; stderr: {rd(f'{SCR}/srp_interim/err_hsx.txt').strip()[:200]}")
    if os.path.exists(f"{SCR}/figchk5/rec_srbhsx.txt"):
        same5 = [open(f"{SCR}/figchk5/{a}", "rb").read() == open(f"{FIGD}/{b}", "rb").read() for a, b in (("rec_srbhsx.txt", "records/paper_f21srbhsx.txt"), ("F21srbhsx_col.pdf", "F21srbhsx_col.pdf"), ("F21srbhsx_col.png", "F21srbhsx_col.png"))]
        print(f"   scratch figchk5/ (mtime {cdt(os.stat(f'{SCR}/figchk5/rec_srbhsx.txt').st_mtime):%m-%d %H:%M:%S} CDT; the author's re-render of `SRB hsx` with the hsx12-capable script): record / pdf / png byte-identical to the committed 00:03 files: {same5}")
    for f in ("fx_overlap_SRB.txt", "fx_overlap_all.txt"):
        if os.path.exists(f"{SCR}/{f}"): print(f"   scratch {f}: mtime {cdt(os.stat(f'{SCR}/{f}').st_mtime):%m-%d %H:%M:%S} CDT" + (f"; identical to results/review_next/FX_overlap_check.txt: {rd(f'{SCR}/{f}') == rd(f'{RV}/FX_overlap_check.txt')}" if f.endswith("all.txt") else ""))
    d1102 = [l for l in DEC if l.startswith("`[2026-10-12 11:02 KST] [정정] ")]
    SP_ = [l for l in rd("logs/seeds_SRP_train.log").split("\n") if l]
    af_ = rd(f"{AUD}/audit_FIGHSPATH16e4.md")
    chk("I5 DECISIONS 11:02 KST [정정] line: 'SRP 시드 a2 는 10-11 16:47 CDT, a3 는 19:20 CDT 에 끝남 (SEEDS_TRAIN_DONE 19:20 CDT; logs/seeds_SRP_train.log)' = the log; 'FIGHSPATH16e4 기록 감사 (Fable): §6 의 수치·채점 오류 0, MUST 0 · SHOULD 2 · NIT 8' = audit_FIGHSPATH16e4.md",
        len(d1102) == 1 and "SRP 시드 a2 는 10-11 16:47 CDT, a3 는 19:20 CDT 에 끝남 (SEEDS_TRAIN_DONE 19:20 CDT; logs/seeds_SRP_train.log)" in d1102[0] and SP_[1].startswith("[seeds 10-11 16:47 CDT] SRP a2 ") and SP_[2].startswith("[seeds 10-11 19:20 CDT] SRP a3 ")
        and SP_[3] == "[seeds 10-11 19:20 CDT] SEEDS_TRAIN_DONE" and "§6 의 수치·채점 오류 0, MUST 0 · SHOULD 2 · NIT 8 반영" in d1102[0] and "MUST 0 · SHOULD 2 · NIT 8." in af_ and
        (len(re.findall(r"^\*\*S\d", af_, re.M)), len(re.findall(r"^- \*\*N\d", af_, re.M))) == (2, 8) and "(Opus 5.5; 텍사스 10-11 21:02 CDT; FIGHSPATH16e4 기록 감사 N6)" in d1102[0], n=8)
    dend = [l for l in DEC if l.startswith("`[2026-10-12 19:03 KST] FIGHSX16e4 실행 끝")]
    d6 = ("(Opus 5.5; 텍사스 10-12 05:03 CDT)", "10-11 20:40 CDT 시작 @037c6610; 첫 실행 10-12 04:09 CDT FIGHS_DONE ok=5 fail=1", "04:39 CDT 전제 검사 중단", "04:40 CDT 기준 행 미지정으로 SKIP", "04:41 CDT '--resume FXSRPB16e4 FXALDSRP' -> 04:58 CDT 여섯 행 모두 ACCEPT OK",
          "SRB Proposed 12 / 11 · GMM 32 / 15 · Perfect CSI 5 / 4", "SRP Proposed 4 / 1 · GMM 14 / 6 · Perfect CSI 1 / 0", "GMM 은 씨앗 초기화", "처음 20480 시행은 n = 20480 raw 와 비트 동일 (ALD-pilot 제외)", "기록 감사 전")
    nhit = sum(v == "적중" for v in got.values())
    chk("I6 DECISIONS 19:03 KST 'FIGHSX16e4 실행 끝' line: times, commit, ok=5 fail=1, the three resume attempts, six ACCEPT OK, SRB / SRP counts of Proposed / GMM / Perfect CSI = own, GMM caveat, bit identity",
        len(dend) == 1 and all(x in dend[0] for x in d6) and [K4("FXSRPB16e4", a, s) for a in (V, B, GE) for s in HX] == [4, 1, 14, 6, 1, 0], str([x for x in d6 if x not in (dend[0] if dend else "")]), n=len(d6) + 12)
    chk(f"I6b DECISIONS 19:03 KST line prediction tally '예측 12 개 중 11 적중, 7 번 빗나감' vs §6.3: {len(got)} scored items, {nhit} hits, 1 miss",
        dend and f"예측 {len(got)} 개 중 {nhit} 적중" in dend[0], f"the line says: {re.search(r'예측 [^.]*', dend[0])[0] if dend else None}; §6.3 has {len(got)} items ({', '.join(got)}), {nhit} 적중", n=2)
    EXPL = rd("../docs/EXPERIMENTS.md").split("\n")
    exp = [l for l in EXPL if "run_fighsx16e4.sh" in l]; E = exp[0] if exp else ""
    NM = {"V1": V, "ALD-pilot": "ALD-pilot", "b\\*": B, "R2": "R2-ours-G", "R1": "R1-turbo", "BiG-AMP": "R3-bigamp", "R0@1": "R0-pilot@1", "SBL-loop": "SBL-loop", "SBL-pilot": "SBL-pilot", "OMP-pilot": "OMP-pilot", "genie": GE}
    own = {p: ", ".join(f"{k} " + " / ".join(str(K4(f"FX{srcs(p, a)}", a, s)) for s in HX) for k, a in NM.items()) for p in PRS}
    ownu = {p: " · ".join(f"{k} " + " / ".join(str(KU(f"FX{p}B16e4", a, s)) for s in HX) for k, a in (("V1", V), ("b\\*", B), ("genie", GE))) for p in PRS}
    chk("I7 EXPERIMENTS.md FIGHSX16e4 row (the last line): the 2 x 11 x 2 failure counts and the unseen-only counts of V1 / b* / genie = own recount",
        len(exp) == 1 and EXPL.index(E) == max(i for i, l in enumerate(EXPL) if l) and f"**실패 수 / 81920 (+12 / +15 dB)** — SRB: {own['SRB']} — SRP: {own['SRP']}." in E and f"보지 않은 61440 시행만: SRB {ownu['SRB']}; SRP {ownu['SRP']}." in E,
        f"own SRB: {own['SRB']} | SRP: {own['SRP']} | unseen SRB {ownu['SRB']}; SRP {ownu['SRP']}", n=44 + 12)
    i8 = ("| 2026-10-12 10:40 ~ 18:09 KST (텍사스 10-11 20:40 ~ 10-12 04:09 CDT; 그 뒤 `--resume` 로 한 행을 마저 돌려 04:58 CDT 종료) |", "NEXT_EXPERIMENTS_FIGHSX16e4 v2 = 실행 커밋 037c6610", "**보고 전용** — 새 검정·라벨 없음",
          "--snr 12 15 --n 81920 --skip0 10000", "| 037c6610 (`code/ald.py` 에 세트 hisnr4 추가) |", "20260926, **새 시행 10000..91919** (n 81920 / SNR; 처음 20480 시행은 n 20480 raw 의 시행과 같다 — 새 점은 그 점과 독립이 아님; 테스트 풀 복원 추출), C2 2 SNR, PID 13 · 15",
          "첫 실행 `FIGHS_DONE ok=5 fail=1` (FXALDSRP: 빈 GPU 없음", "같은 HEAD 에서 재개 → 여섯 행 모두 ACCEPT OK. 단계 C 대조 수신기 6 · ALD 추정기 2 OK.", "처음 20480 시행은 `raw_FH*` 와 비트 동일 (ALD-pilot 제외; 여섯 raw, `FX_overlap_check.txt`)",
          "0 실패 점: SRB 없음, SRP genie +15 dB. 오르는 칸 (보고만): 두 prior 모두 BiG-AMP +9→+12 dB 뿐.", "runner 77.9 · 100.7 · 4.3 · 154.2 · 92.0 · 4.5 분", "판정·라벨은 원 raw (n 2560) 그대로이고 다시 판정하지 않는다; SRP 의 GMM b\\* 는 씨앗 초기화 그대로",
          "(y: SRB (3e-05, 1.2), SRP (7.5e-06, 1.2))", "**원고판 `F21sr{b,p}hsx12_col` (+12 dB 까지; 사용자 결정 10-12 CDT — DECISIONS)**", "Fable 사전 검토 MUST 3 · SHOULD 8 · NIT 8 반영")
    chk("I8 EXPERIMENTS.md FIGHSX16e4 row: times (KST = CDT + 14 h), run commit, flags, seed / trials / not-independent note / PID 13 · 15, ok=5 fail=1 -> resume -> six ACCEPT OK, phase C 6 + 2, bit identity, zero-failure points, rising cells, runner minutes, 'not re-judged', GMM caveat, y ranges, paper variant, review counts",
        all(x in E for x in i8), str([x for x in i8 if x not in E]), n=len(i8))
    rv = rd(f"{RV}/prereg_reviews_2026-10-11/review_FIGHSX16e4.md"); common = rd("code/common.py")
    chk("I8b review_FIGHSX16e4.md headings: MUST 3 · SHOULD 8 · NIT 8; PID of SRB / SRP in code/common.py = 13 / 15; same number of column separators in the new row as in the row above",
        (len(re.findall(r"^### M-\d", rv, re.M)), len(re.findall(r"^### S-\d", rv, re.M)), len(re.findall(r"^- N-\d", rv, re.M))) == (3, 8, 8) and re.search(r'"SRB": 13,', common) and re.search(r'"SRP": 15}', common)
        and E.count(" | ") == EXPL[EXPL.index(E) - 1].count(" | "), f"separators {E.count(' | ')} vs {EXPL[EXPL.index(E) - 1].count(' | ')}", n=6)
    chk(f"I8c EXPERIMENTS.md row prediction tally '§3 예측 12 개 중 11 적중, 7 번 (한 번의 실행으로 ok=6) 빗나감' vs §6.3: {len(got)} scored items, {nhit} hits, 1 miss",
        f"§3 예측 {len(got)} 개 중 {nhit} 적중" in E, f"the row says: {re.search(r'§3 예측 [^.]*', E)[0] if E else None}", n=2)
    gpu_t = re.search(r"ALD 대조·추정만 GPU 1 \(([^)]*)\)", E)
    print(f"   EXPERIMENTS row GPU times: '{gpu_t and gpu_t[1]}'; run-log GPU lines (control / estimate): " + ", ".join(f"{l[7:18]}" for l in LOG if "on GPU 1" in l or "(GPU 1)" in l))

    # ====================================================================== J. corrections in the two earlier registrations (added in 4c536f1b)
    print("\n# J. corrections in NEXT_EXPERIMENTS_FIGHSROOM16e4.md / NEXT_EXPERIMENTS_FIGHSPATH16e4.md", flush=True)
    fr = rd(f"{RV}/NEXT_EXPERIMENTS_FIGHSROOM16e4.md"); fp_ = rd(f"{RV}/NEXT_EXPERIMENTS_FIGHSPATH16e4.md")
    RB = {s: {a: np.concatenate([o["arms"][a][0] for o in sorted(FB["FHSRBB16e4"], key=lambda o: o["name"][3]) if o["name"][2] == s]) for a in (V, B, "R2-ours-G", GE)} for s in HS4}
    idx = {s: np.where(RB[s][V] > 0)[0].tolist() for s in HS4}
    hf = rd(f"{RV}/FHSRBB16e4_highsnr_fail.txt")
    def sect(s): return hf.split(f"\n{s} dB  n=20480")[1].split("\n\n")[0]
    tr = {s: re.findall(r"trial\s+(\d+): share ([\d.]+).*?also fail: (.*?)  channel (\w+) \(drawn (\d+)x", sect(s), re.M) for s in ("+6", "+9", "+12", "+15")}
    stream = {s: [10000 + i for i in idx[float(s)]] for s in ("+6", "+9", "+12", "+15")}
    chk("J1 FIGHSROOM16e4 §6.6 [정정]: stream trial numbers '+12 dB 11853 · 25558 · 29518, +15 dB 13420 · 14014 · 19512 · 22742' = 10000 + my own failing positions in raw_FHSRBB16e4 (chunks in skip order) = the `trial` numbers now printed in FHSRBB16e4_highsnr_fail.txt at all four SNRs (45 / 10 / 3 / 4 V1 failures)",
        stream["+12"] == [11853, 25558, 29518] and stream["+15"] == [13420, 14014, 19512, 22742] and all([int(t[0]) for t in tr[s]] == stream[s] for s in stream) and [len(tr[s]) for s in ("+6", "+9", "+12", "+15")] == [45, 10, 3, 4] and
        "스트림 시행 번호(= 10000 + 위치)는 +12 dB 11853 · 25558 · 29518, +15 dB 13420 · 14014 · 19512 · 22742 이다 — 원 raw (시행 0..2559) 의 블록이 아니다" in fr and "+12 dB 시행 1853 · 15558 · 19518, +15 dB 시행 3420 · 4014 · 9512 · 12742 **[정정 2026-10-11 21:02 CDT" in fr,
        f"own stream trials +12 {stream['+12']} +15 {stream['+15']}", n=7 + 62)
    wd = [l for l in sh(f"git diff {RUNC} {S6C} --word-diff=porcelain -- {RV}/FHSRBB16e4_highsnr_fail.txt").split("\n") if re.match(r"^[+-][^+-]", l)]
    mi = [int(l[1:].rstrip(":")) for l in wd if l.startswith("-")]; pl_ = [int(l[1:].rstrip(":")) for l in wd if l.startswith("+")]
    sd = sh(f"git diff {RUNC} {S6C} -- {AUD}/highsnr_fail_SRB.py")
    chk("J2 FHSRBB16e4_highsnr_fail.txt was regenerated in 4c536f1b: the word diff 037c6610..4c536f1b is exactly 62 trial numbers, each old + 10000 (nothing else changed); highsnr_fail_SRB.py diff = one line (`trial {t:4d}` -> `trial {t + SK:4d}`; SK = 0 without the third argument, so the default-mode output is unchanged -- by reading); SRBB16e4_highsnr_fail.txt has no diff",
        len(mi) == len(pl_) == 62 and all(b == a + 10000 for a, b in zip(mi, pl_)) and sh(f"git diff --numstat {RUNC} {S6C} -- {AUD}/highsnr_fail_SRB.py").split()[:2] == ["1", "1"] and "trial {t + SK:4d}:" in sd and
        not sh(f"git diff {RUNC} {S6C} -- {RV}/SRBB16e4_highsnr_fail.txt"), f"{len(mi)} changed tokens; file mtime {cdt(os.stat(f'{RV}/FHSRBB16e4_highsnr_fail.txt').st_mtime):%m-%d %H:%M:%S} CDT", n=62 + 3)
    fp6 = {t[3] for t in tr["+6"]}; seven = [t[3] for t in tr["+12"] + tr["+15"]]
    both = sorted(f for f in seven if f in fp6)
    chk("J3 FIGHSROOM16e4 §6.6 fingerprint note [N8]: of the seven +12 / +15 dB failing channels exactly two -- f168bf2c and f7ba1351 -- also appear among the +6 dB V1 failures of the same file; the seven fingerprints are distinct",
        both == ["f168bf2c", "f7ba1351"] and len(set(seven)) == 7 and "(일곱 가운데 둘 — 지문 f168bf2c · f7ba1351 — 은 같은 파일에서 +6 dB 에도 V1 이 실패한 풀 채널이다 [FIGHSPATH16e4 감사 N8])" in fr,
        f"seven {seven}; also at +6 dB {both}; also at +9 dB {sorted(f for f in seven if f in {t[3] for t in tr['+9']})}", n=9)
    chk("J4 FIGHSROOM16e4 §6.4 [N3]: '3 · 4 / 20480 = 1.46e-04 · 1.95e-04' (own: %.2e of 3 / 20480 and 4 / 20480) with the old text kept in the bracket; §6.5 [N4] 'DECISIONS.md 의 08:33 KST 줄(같은 커밋)과 07:00 KST 줄(193776a1)'; §6.5 [N5] the added 'ROOM16e4 §5 [감사 S2] 의 재선택 명령(결과만 확인됨)'",
        (f"{3 / N2:.2e}", f"{4 / N2:.2e}") == ("1.46e-04", "1.95e-04") and "(3 · 4 / 20480 = 1.46e-04 · 1.95e-04 [FIGHSPATH16e4 감사 N3: 앞의 표기 1.5e-04 · 1.9e-04 는 반올림이 맞지 않았다]; 하한 5.0e-05 · 7.6e-05)" in fr and
        "`DECISIONS.md` 의 08:33 KST 줄(같은 커밋)과 07:00 KST 줄(193776a1) [FIGHSPATH16e4 감사 N4]" in fr and "풀 통계(§0)의 원 재계산, ROOM16e4 §5 [감사 S2] 의 재선택 명령(결과만 확인됨) [FIGHSPATH16e4 감사 N5]." in fr, n=5)
    a33 = [l[:24] for l in sh("git diff 193776a1 ed265304 -- DECISIONS.md").split("\n") if l.startswith("+`[")]; a07 = [l[:24] for l in sh("git diff 1404d315 193776a1 -- DECISIONS.md").split("\n") if l.startswith("+`[")]
    print(f"   DECISIONS lines added by ed265304: {a33}; by 193776a1: {a07}; 07:00 KST lines in the file: {len([l for l in DEC if l.startswith('`[2026-10-12 07:00 KST]')])}")
    c1 = "**GMM 캐비엇(머리말) [감사 S2]**: M-ours-bstar (그림의 GMM prior) 행은 PATH16e4 의 b\\* 그대로다 — EM 이 무너져 선택된 씨앗 초기화(\"kron 4096\", ll_val 244.1933, it_best 0)이고 잘 맞춘 GMM 이 아니다. 새 시행의 실패 수는 b\\* 202 / 33 / 3 / 1, Gaussian prior (R2-ours-G) 215 / 35 / 4 / 1."
    c2 = "3. +6 · +9 dB 에서 실패 수 V1 ≤ b\\* → **적중** (45 대 202, 7 대 33; b\\* 는 씨앗 초기화 GMM — 머리말 캐비엇 [감사 S2])."
    fitp = glob.glob("results/gmm_fits_D2_SRPB16e4/fit_SRP_Nr8_kronK4096_n160000.npz") + glob.glob("results/gmm_fits_D2_SRPB16e4/*kron*4096*.npz")
    itb = None
    if fitp:
        zf = np.load(fitp[0], allow_pickle=True); itb = (float(zf["ll_val"]), int(zf["it_best"]) if "it_best" in zf.files else None)
    chk("J5 FIGHSPATH16e4 §6.2 / §6.3 GMM caveat lines [S2] present verbatim; their numbers = own recount of raw_FHSRPB16e4 (b* 202 / 33 / 3 / 1, R2-ours-G 215 / 35 / 4 / 1, V1 45 / 7) and the fit file (ll_val 244.1933, it_best 0)",
        c1 in fp_ and c2 in fp_ and [FC["FHSRPB16e4"][B][s][0] for s in HS4] == [202, 33, 3, 1] and [FC["FHSRPB16e4"]["R2-ours-G"][s][0] for s in HS4] == [215, 35, 4, 1] and [FC["FHSRPB16e4"][V][s][0] for s in HS4[:2]] == [45, 7]
        and itb is not None and f"{itb[0]:.4f}" == "244.1933" and itb[1] == 0, f"fit file {fitp[:1]} (ll_val, it_best) {itb}", n=14)
    g = [FC["FHSRPB16e4"][a][s] for a in (B, "R2-ours-G") for s in (15.0,)] + [FC["FHSRPB16e4"][GE][s] for s in (9.0, 12.0)]
    low4 = [f"{wilson(k, n)[0]:.1e}" for k, n in g]
    HSP = {a: MERGED_HS("SRP", a) for a in ORDER}
    posp = {(a, ALL[i]): (wilson(k, n)[0] if a in BARS else k / n) for a in ORDER for i, (k, n) in enumerate(HSP[a]) if k > 0}
    n2e4 = len([v for v in posp.values() if v <= 2e-4]); nz = sum(k == 0 for a in ORDER for k, n in HSP[a])
    chk("J6 FIGHSPATH16e4 §6.4 [N1] sentence: three zero-failure points; '그 밖에 2e-4 이하의 점·막대 끝 12 개'; four lower Wilson bar ends at 8.6e-06 (GMM prior · Gaussian prior +15 dB, Perfect CSI +9 · +12 dB) clipped; '0 / 20480, Wilson 상한 1.88e-04' -- own recount of the hs figure's drawn values",
        nz == 3 and n2e4 == 12 and low4 == ["8.6e-06"] * 4 and f"{wilson(0, N2)[1]:.2e}" == "1.88e-04" and
        "y 축 (3e-05, 1.2) 은 0 실패 점이 셋이라 규칙의 둘째 범위다(그 밖에 2e-4 이하의 점·막대 끝 12 개; Wilson 하한 8.6e-06 인 막대 넷 — GMM prior · Gaussian prior +15 dB, Perfect CSI +9 · +12 dB — 은 축 아래로 잘린다)" in fp_ and
        "제안 곡선은 +9 dB 에서 끝나고 +12 · +15 dB 에는 표시가 없다(0 / 20480, Wilson 상한 1.88e-04)" in fp_ and "tmux `fighspath` (세션 기록 기준 [감사 N2])" in fp_,
        f"zero points {nz}; drawn values <= 2e-4: {n2e4}; the four lower ends {low4}; Wilson upper of 0/20480 {wilson(0, N2)[1]:.3e}", n=8)
    s65 = fp_.split("### 6.5 ")[1]
    j7 = [("보고서 파일 mtime 2026-10-11 21:00 CDT", f"{cdt(os.stat(f'{AUD}/audit_FIGHSPATH16e4.md').st_mtime):%Y-%m-%d %H:%M}" == "2026-10-11 21:00"),
          ("감사 대상 = 커밋 aefbfc12", "Audited version: commit **aefbfc12**" in af_),
          ("**이 문서 §6.1–6.4 의 수치·채점·인용 오류 0**", "0 numeric, scoring or citation errors in §6.1–6.4" in af_),
          ("새 raw 3 × 2048 청크(시행 10000..30479 를 SNR 당 한 번씩; 모든 청크 `run|git` c48ee796, `+dirty` 없음)", "`run|git` c48ee796 with no `+dirty`" in af_),
          ("(검사 묶음 63 개 중 62 통과; 나머지 하나는 아래 N3)", "63 check groups, 62 PASS, 1 FAIL (N3 below" in af_),
          ("genie 세 raw 비트 동일(14 / 1 / 1 / 0)", "→ 14 / 1 / 1 / 0" in af_), ("집계표 56 행과 Wilson 문자열, 6.2 의 44 칸과 원 raw 열", "All 56 count-table rows" in af_ and "the 44 cells of the §6.2 table" in af_),
          ("0 실패 점 셋, 오르는 칸 하나(BiG-AMP +9 → +12 dB, p 9e-06)", "the one rising cell with its one-sided Fisher p (BiG-AMP +9 → +12 dB, 9e-06" in af_ and "the three zero-failure points" in af_),
          ("예측 여섯의 채점", "the six §6.3 scores" in af_), ("`eval_accept` 세 행 재실행 → `ACCEPT: OK`", "→ `ACCEPT: OK` × 3, rc 0" in af_),
          ("생성기 `s6_fighsroom_gen.py SRP` 재실행이 6.1–6.3 과 바이트 동일", "**byte-identical to §6.1–6.3 of the registration**" in af_),
          ("다시 그린 기록 4 개·PDF/PNG 8 개가 커밋본과 **바이트 동일**", "the four records **byte-identical**" in af_ and "the eight files" in af_),
          ("**MUST 0 · SHOULD 2 · NIT 8 — 모두 반영", "MUST 0 · SHOULD 2 · NIT 8." in af_),
          ("기록 2026-10-11 21:02 CDT, Opus 5.5", f"{cdt(os.stat(f'{RV}/NEXT_EXPERIMENTS_FIGHSPATH16e4.md').st_mtime):%Y-%m-%d %H:%M}" == "2026-10-11 21:02")]
    chk("J7 FIGHSPATH16e4 §6.5 reports audit_FIGHSPATH16e4.md faithfully (14 quoted facts: report mtime 21:00 CDT, audited commit, error count, chunk / git facts, 63 / 62 check groups, genie, table sizes, zero points + rising cell, six scores, eval_accept re-runs, generator byte identity, 4 records + 8 figure files, MUST / SHOULD / NIT counts, the 21:02 CDT record time = file mtime)",
        all(q in s65 and ok for q, ok in j7), str([q for q, ok in j7 if not (q in s65 and ok)]), n=len(j7))
    nvsec = af_.split("## Not verified")[1]
    print(f"   audit_FIGHSPATH16e4.md 'Not verified' bullets: {len(re.findall(r'^- ', nvsec, re.M))}; items of it NOT in §6.5's '감사가 확인하지 못한 것' list: " +
          str([k for k, pat_ in (("author ran the byte-identity checks", "byte-identity"), ("GPU 3-5 held from outside at run time", "GPU 3"), ("default-mode reproduction of SRBB16e4_highsnr_fail.txt judged from the diff", "default-mode"), ("pool statistics 52,200", "52,200"))
               if pat_ in nvsec and not any(w in s65.split("감사가 확인하지 못한 것")[1] for w in {"byte-identity": ("바이트 동일",), "GPU 3": ("GPU 3", "컨테이너 밖"), "default-mode": ("기본 모드",), "52,200": ("풀 통계",)}[pat_])]))

    # ---- wording of §6
    voc = {w: [i6 + 1 + i for i, l in enumerate(S6) if w in l] for w in ("라벨", "유의", "우수", "입증", "시사", "결론", "일반화", "동치", "판정", "검정", "이긴", "우위", "개선", "낫다", "유리", "better", "significant")}
    print("\n# wording: vocabulary hits in §6 (file line numbers): " + str({w: v for w, v in voc.items() if v}))
    print("   §6 lines mentioning the GMM caveat (씨앗 초기화): " + str([i6 + 1 + i for i, l in enumerate(S6) if "씨앗 초기화" in l]) + "; lines naming M-ours-bstar / b\\* / GMM: " + str([i6 + 1 + i for i, l in enumerate(S6) if re.search(r"M-ours-bstar|b\\\*|GMM", l)]))
    print("   §6 lines with the not-independent disclosure (독립이 아니 / 명목 / 이미 본 / 본 시행 / 보지 않은): " + str({w: [i6 + 1 + i for i, l in enumerate(S6) if w in l] for w in ("독립이 아니", "명목", "이미 본", "본 시행", "보지 않은")}))

    print(f"\n# SUMMARY: {sum(ok for _, ok in CHECKS)} PASS / {sum(not ok for _, ok in CHECKS)} FAIL of {len(CHECKS)} checks; ≈ {NVAL[0]} scalar / string values, {NARR} array comparisons  ({datetime.now(CDT):%Y-%m-%d %H:%M:%S %Z})")
    for n, ok in CHECKS:
        if not ok: print("   FAIL:", n)
    POOL.close()
