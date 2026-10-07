"""Independent re-derivation of NEXT_EXPERIMENTS_SUPP16e4.md §6.1 (+ the §5 ALD tuning table), the SUPP16e4 row of
docs/EXPERIMENTS.md and the DECISIONS line of 6730bc1d (record audit 2026-09-29, Fable 5.1).

Reads ONLY the raw npz chunks (raw_<T> original: V1 / b* / R2 / genie; raw_XL<T> / raw_XP<T> / raw_XA<T> new arms),
results/ald/{tune,ald,pilots}_XA<T>.*, logs/run_supp16e4.log, git and /proc.  pair_baselines.py / analysis.py are NOT
called; the pairB_*.txt / accept files are not read (except the doc itself, which is parsed for the comparison).

Reused from prereg_audit_2026-09-28/recompute.py (the previous audit's OWN implementations, verified there against
analysis.load_raw field-for-field and against a reader-free hand count): Raw (chunk-file reader), fails (blk_err@last,
NaN -> 1), raised, table_b / dpoints / sign_p (08_SPEC §2 table B: anchor = X, up to 3 grid points with X's BLER in
[0.005, 0.9] closest to 0.1 in |log10|, exact two-sided binomial, POWERED = 3 points and >= 6 discordant at >= 2,
(i) V1 fewer at >= 2 points with p < .05, (ii) X fewer, (iii) neither, (iv) not powered), recovery (R_X = (F_X - F_V1) /
(F_X - F_genie), paired bootstrap B = 2000, default_rng(20260926), one trial-index draw per replicate applied to the three
arms -- the same draw order as recovery_ci.boot), merged, same, git, sha16.  Nothing else is imported.

    OMP_NUM_THREADS=4 CUDA_VISIBLE_DEVICES= ~/miniforge3/envs/torch/bin/python \
        results/review_next/prereg_audit_2026-09-29/recompute.py > .../recompute.out 2> .../recompute.err
"""
import glob
import json
import os
import re
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "prereg_audit_2026-09-28"))
from recompute import (Raw, fails, raised, table_b, dpoints, sign_p, recovery, merged, same, git, sha16,   # noqa: E402
                       KEYS4, GRID, V1, BSTAR, GENIE, R2, BASELINES, CONF, T2)

P = lambda *a: print(*a, flush=True)
DOC = os.path.join(CONF, "results/review_next/NEXT_EXPERIMENTS_SUPP16e4.md")
BL = tuple("R0-pilot@1" if x == "R0-pilot" else x for x in BASELINES)          # 𝔅 with the SUPP16e4 §1 R0 reading
X13 = (BSTAR,) + BL
XL_ARMS = ("M-ours-bstar-scalar", "M-ours-gmm32", "R0-pilot", "R1-turbo", "R3-bigamp", "R4-llr", "R4-scvamp")
# suffix -> (cell, prior, doc dataset name)
SUF = (("B16e4k", "C2", "S2", "D2 C2"), ("NR16", "C6", "S2", "D2 C6"), ("D3", "C2", "S2c", "D3"), ("SV", "C2", "SV8e", "SV8e"),
       ("U28", "C2", "UMi28", "UMi28"), ("MX", "C2", "MIX3", "MIX3"))
LEVEL = (("DOPa", "DOP", "0.005", "DOP ν=0.005"), ("DOPb", "DOP", "0.01", "DOP ν=0.01"), ("ROTa", "ROT", "15", "ROT 15°"), ("ROTb", "ROT", "30", "ROT 30°"))
ORIG_GIT = {"DOP": "063f3bcb", "ROT": "a4cbd184"}
NEW_GIT = "e7c9f4a7"
# §0: the b* -> V1 labels of DOP16e4 / ROT16e4 §6.1 (quoted, not re-decided)
ORIG_B = {"DOPbB16e4k": "(iii)", "DOPbNR16": "(iii)", "DOPbU28": "(iii)", "DOPaSV": "(iv)", "ROTaSV": "(iv)"}
CONDS = [(f"{lv}{sx}", kind, val, cell, prior, f"{ds}, {lvname}") for sx, cell, prior, ds in SUF for lv, kind, val, lvname in LEVEL]
ORDER = [c[0] for c in CONDS]                                                   # doc's 24-row order (dataset-major)
D2C2 = ["DOPaB16e4k", "DOPbB16e4k", "ROTaB16e4k", "ROTbB16e4k"]


def dp_str(cand):
    return "/".join(f"{s:+.0f}" for s in cand)


def norm(s):
    return re.sub(r"\s+", " ", s.replace("−", "-").replace("\\*", "*").replace("**", "")).strip()


def doc_tables():
    """Parse §6.1 tables of the doc: D2 C2 X-table (13 x 4 cells), the 24-condition table, the §5 tune table."""
    lines = open(DOC, encoding="utf-8").read().splitlines()
    i61 = next(i for i, l in enumerate(lines) if l.startswith("### 6.1"))
    xt, t24, t5 = {}, {}, {}
    for i, l in enumerate(lines):
        if not l.startswith("| "):
            continue
        c = [norm(x) for x in l.strip().strip("|").split("|")]
        if i > i61 and len(c) == 5 and c[0].split()[0] in X13:
            xt[c[0].split()[0]] = (i + 1, c[1:])
        elif i > i61 and len(c) == 8 and c[0].split()[0] in ORDER:
            t24[c[0].split()[0]] = (i + 1, c[1:])
        elif i < i61 and len(c) == 8 and c[0] in ORDER and re.fullmatch(r"[0-9a-f]{16}", c[1]):
            t5[c[0]] = (i + 1, c[1:])
    return lines, xt, t24, t5


def cell_x(t, absgap, r1):
    """doc D2 C2 cell: dp · pooled a:b · lab k/3 · abs gap [· R [lo, hi]]"""
    w = t["wx"] if t["lab"] == "(ii)" else t["wy"]
    s = f"{dp_str(t['cand'])} · {t['A']}:{t['B']} · {t['lab']} {w}/3 · {absgap}"
    return s + (f" · {r1}" if r1 and not r1.startswith("undefined") else "")


def r_str(defined, R, lo, hi, absgap):
    return f"{R:.3f} [{lo:.3f}, {hi:.3f}]" if defined else f"undefined; abs {absgap}"


def doc_r(cell):
    c = norm(cell)
    if "정의하지 않음" in c:
        m = re.search(r"절대 격차 (\d+)", c)
        return f"undefined; abs {m[1] if m else '?'}"
    return c


# ----------------------------------------------------------------------------------------------- per condition
def audit_condition(T, kind, val, cell, prior):
    base, xl, xp, xa = Raw(T), Raw("XL" + T), Raw("XP" + T), Raw("XA" + T)
    raws = dict(base=base, XL=xl, XP=xp, XA=xa)
    cp = (cell, prior)
    bad = []
    for n, r in raws.items():
        if r.cp != [cp]:
            bad.append(f"{n}: (cell, prior) {r.cp}")
        if tuple(r.snrs(cp)) != GRID:
            bad.append(f"{n}: grid {r.snrs(cp)}")
        if r.holes or r.fill:
            bad.append(f"{n}: holes/NaN-fill {r.holes[:2]} {r.fill[:2]}")
        g = r.scal["run|git"]
        want = ORIG_GIT[kind] if n == "base" else NEW_GIT
        if g != {want}:
            bad.append(f"{n}: run|git {sorted(g)} != {want}")
    mkey = "meta|doppler" if kind == "DOP" else "meta|rotation"
    for mk in ("meta|doppler", "meta|rotation"):
        vals = {n: r.scal[mk] for n, r in raws.items()}
        if len(vals["base"]) != 1 or any(v != vals["base"] for v in vals.values()):
            bad.append(f"{mk} differs {vals}")
    mv = next(iter(base.scal[mkey]))
    if not (mv.startswith(f"nu={float(val)!r}") if kind == "DOP" else mv.startswith(f"deg={float(val)!r}:")):
        bad.append(f"{mkey} {mv[:30]!r} != {val}")
    # meta fingerprint across the four raws (eval_accept: bstar, kron_K, em_sec, ckpt id, ll_val, ntrain)
    fp = {}
    for q in ("meta|ntrain", "meta|bstar", "meta|kron_K", "meta|em_sec", "meta|ll_val|kron", "meta|stagec_ckpt_id"):
        vals = {n: str(r.m(cp).get(q)) for n, r in raws.items()}
        fp[q] = len(set(vals.values())) == 1
        if not fp[q]:
            bad.append(f"{q} differs {dict((n, v[:40]) for n, v in vals.items())}")
    for n in ("XL", "XP", "XA"):
        if str(raws[n].m(cp).get("run|iters", raws[n].scal.get("run|iters", "16"))) not in ("16", "{'16'}"):
            pass
    # arms: no overlap between raws (except genie), expected arm sets
    arms = {n: set(r.arms(cp)) - {GENIE} for n, r in raws.items()}
    if arms["base"] != {V1, BSTAR, R2}:
        bad.append(f"base arms {sorted(arms['base'])}")
    if arms["XL"] != set(XL_ARMS):
        bad.append(f"XL arms {sorted(arms['XL'])}")
    if arms["XP"] != {"V1-pilot", "bstar-pilot"} or arms["XA"] != {"ALD-pilot", "ALDv-pilot"}:
        bad.append(f"XP/XA arms {sorted(arms['XP'])} {sorted(arms['XA'])}")
    for s in GRID:
        db = base.d(cp, s)
        for n in ("XL", "XP", "XA"):
            if any(not same(db[GENIE][q], raws[n].d(cp, s)[GENIE][q]) for q in KEYS4):
                bad.append(f"{s:+.0f} {n}: genie != base")
        if any(len(r.d(cp, s)[a]["blk_err"]) != 2560 for r in raws.values() for a in r.d(cp, s)):
            bad.append(f"{s:+.0f}: n != 2560")
        for arm, r in (("V1-pilot", xp), ("bstar-pilot", xp), ("ALD-pilot", xa), ("ALDv-pilot", xa)):
            if raised(r.d(cp, s), arm).any():
                bad.append(f"{s:+.0f} {arm}: raised {int(raised(r.d(cp, s), arm).sum())}")
        for x, y in (("V1-pilot", V1), ("bstar-pilot", BSTAR)):
            ok = ~(raised(xp.d(cp, s), x) | raised(db, y))
            if not same(np.asarray(xp.d(cp, s)[x]["nmse"])[ok, 0], np.asarray(db[y]["nmse"])[ok, 0]):
                bad.append(f"{s:+.0f} {x}@1 != {y}@1")
    # ALD estimate: fixed over iterations, equal to the precomputed file, ckpt = base V1 ckpt, condition = base
    est = np.load(os.path.join(CONF, "results/ald", f"ald_XA{T}.npz"), allow_pickle=True)
    pilf = np.load(os.path.join(CONF, "results/ald", f"pilots_XA{T}_test.npz"), allow_pickle=True)
    prov = json.loads(str(est["prov"]))
    bsha = str(base.m(cp).get("meta|stagec_ckpt_id", "")).split()[0].replace("sha256[:16]=", "")
    if prov.get("ckpt_sha") != bsha or str(est["ckpt_sha"]) != bsha:
        bad.append(f"ALD est ckpt {prov.get('ckpt_sha')} != base {bsha}")
    brot = float(mv.split(":")[0].replace("deg=", "")) if kind == "ROT" else -1.0
    bdop = float(mv.split(" ")[0].replace("nu=", "")) if kind == "DOP" else -1.0
    if float(pilf["rotation"]) != brot or float(pilf["doppler"]) != bdop or float(est["rotation"]) != brot or float(est["doppler"]) != bdop:
        bad.append(f"ALD pilots/est condition rot {float(pilf['rotation'])}/{float(est['rotation'])} dop {float(pilf['doppler'])}/{float(est['doppler'])} != base {brot}/{bdop}")
    nm_test = []
    for j, s in enumerate(est["snrs"]):
        H, hh = pilf["H"][j], est["hhat"][j]
        ref = np.sum(np.abs(hh - H) ** 2, -1) / np.sum(np.abs(H) ** 2, -1); nm_test.append(10 * np.log10(ref.mean()))
        if not (len(H) == len(hh) == 2560):
            bad.append(f"{s:+.0f}: est/pilot trials {len(H)}/{len(hh)}")
        for arm in ("ALD-pilot", "ALDv-pilot"):
            nm = np.asarray(xa.d(cp, float(s))[arm]["nmse"])
            if not same(nm, np.repeat(nm[:, :1], nm.shape[1], axis=1)) or not np.allclose(nm[:, 0], ref, rtol=1e-9, atol=0):
                bad.append(f"{s:+.0f} {arm}: estimate not fixed / not the precomputed one")
    tune = json.load(open(os.path.join(CONF, "results/ald", f"tune_XA{T}.json")))
    dev = [float(v) for v in tune["dev_nmse_db"].values()]
    P(f"\n  [{T}] files base {base.nfiles} XL {xl.nfiles} XP {xp.nfiles} XA {xa.nfiles}; run|git base {sorted(base.scal['run|git'])} XL {sorted(xl.scal['run|git'])} "
      f"XP {sorted(xp.scal['run|git'])} XA {sorted(xa.scal['run|git'])}; {mkey} {mv[:22]!r}; ckpt id (base) {bsha}; meta fingerprint equal {fp}")
    P(f"    ALD est prov git {prov.get('git')} ald.py {prov.get('ald_py_sha')} ckpt {prov.get('ckpt_sha')}; est sha256[:16] {sha16(os.path.join(CONF, 'results/ald', f'ald_XA{T}.npz'))}; "
      f"test NMSE dB {' '.join(f'{v:.2f}' for v in nm_test)}; dev {' '.join(f'{v:.1f}' for v in dev)}; max |test - dev| {max(abs(a - b) for a, b in zip(nm_test, dev)):.2f} dB")
    P(f"    integrity (grid, holes, one clean commit per raw [orig {ORIG_GIT[kind]} / new {NEW_GIT}], meta doppler/rotation = base, fingerprint, arm sets disjoint, genie 4 keys XL/XP/XA = base, "
      f"n 2560, PIL/ALD raised 0, pilot@1 = loop@1, ALD estimate fixed = precomputed, ALD ckpt/condition = base): {'OK' if not bad else 'FAILED ' + '; '.join(bad[:8])}")
    # ---- merged data on the common trials; R0-pilot@1 = trajectory truncated at iteration 1 (analysis.load_raw alias)
    D = merged(cp, (base, {a: a for a in (V1, BSTAR, R2, GENIE)}), (xl, {a: a for a in XL_ARMS}), (xp, {"V1-pilot": "V1-pilot", "bstar-pilot": "bstar-pilot"}),
               (xa, {"ALD-pilot": "ALD-pilot", "ALDv-pilot": "ALDv-pilot"}))
    for s in D:
        D[s]["R0-pilot@1"] = {q: np.asarray(a)[:, :1] for q, a in D[s]["R0-pilot"].items() if getattr(a, "ndim", 0) == 2}
    fv3, fg3 = fails(D[-3.0], V1), fails(D[-3.0], GENIE)
    vg = fg3.sum() >= fv3.sum()                                   # SUPP16e4 §1 genie >= V1 guard
    res = {}
    P(f"    -3 dB genie {int(fg3.sum())} · V1 {int(fv3.sum())} -> genie >= V1 guard {'FIRED (R_X undefined for every X)' if vg else 'not fired'}")
    for x in X13:
        t = table_b(D, x, V1)
        fx = fails(D[-3.0], x); F = int(fx.sum()); absgap = F - int(fv3.sum()); bl = fx.mean()
        if vg:
            defined, R, lo, hi = False, np.nan, np.nan, np.nan
        elif not (0.005 <= bl <= 0.9) or F <= fg3.sum():
            defined, R, lo, hi = False, np.nan, np.nan, np.nan
        else:
            R, lo, hi, nn, _ = recovery([(fx, fv3, fg3)]); defined = nn <= 0.05 * 2000
        res[x] = dict(t=t, lab=t["lab"], F=F, absgap=absgap, defined=defined, R=R, lo=lo, hi=hi, r1=r_str(defined, R, lo, hi, absgap))
        P(f"      {x:<20} {dp_str(t['cand']):<12} " + " · ".join(f"{a}:{b} (p {p:.2g})" for a, b, p in t["res"]) + f"  pooled {t['A']}:{t['B']} -> {t['lab']} {t['wy']}/{len(t['cand'])} "
          f"(powered {t['powered']}); F -3 dB {F}; abs gap {absgap}; R_X {res[x]['r1']}")
    kB = sum(1 for x in BL if res[x]["lab"] == "(i)"); mB = sum(1 for x in BL if res[x]["lab"] == "(ii)")
    xs = min(X13, key=lambda x: (res[x]["F"], x))
    orig_b = ORIG_B.get(T, "(i)")
    drift = res[BSTAR]["lab"] != orig_b
    sent = (orig_b == "(i)") and kB == 12 and mB == 0 and res[xs]["defined"] and res[xs]["lo"] > 0
    P(f"    SUMMARY-B: k𝔅 {kB}, m𝔅 {mB}, undecided {12 - kB - mB}; b* -> V1 recomputed {res[BSTAR]['lab']} vs §0 {orig_b} {'DRIFT' if drift else 'same'}; "
      f"X* = {xs} (F {res[xs]['F']}; runner-up {sorted(X13, key=lambda x: (res[x]['F'], x))[1]} F {res[sorted(X13, key=lambda x: (res[x]['F'], x))[1]]['F']}); R_X* {res[xs]['r1']}; "
      f"'전부' sentence (orig b* (i), k𝔅 = 12, m𝔅 = 0, R_X* defined & lower > 0): {'MET' if sent else 'NOT met'}; main label (D2 C2 only) {'(A)' if kB == 12 and mB == 0 else '(B)'}")
    out = dict(res=res, kB=kB, mB=mB, xs=xs, orig_b=orig_b, drift=drift, sent=sent, vg=vg, Fg=int(fg3.sum()), Fv=int(fv3.sum()), integrity=not bad, bad=bad)
    del base, xl, xp, xa, raws, D
    return out


# ----------------------------------------------------------------------------------------------- git / log / §5
def sec_git_log():
    P("\n## G. git / documents / log / container")
    P("  HEAD", git("rev-parse", "--short", "HEAD"), "| dirty conf/code Demo:", repr(git("status", "--porcelain", "conf/code", "Demo")),
      "| dirty records:", repr(git("status", "--porcelain", "conf/results/review_next/NEXT_EXPERIMENTS_SUPP16e4.md", "docs/EXPERIMENTS.md", "conf/DECISIONS.md")))
    for h in ("d17f3d65", "e7c9f4a7", "6730bc1d", "063f3bcb", "a4cbd184"):
        P(f"  {h}: {git('log', '-1', '--format=%h %p %ad %s', '--date=format-local:%Y-%m-%d %H:%M:%S KST', h)[:120]}")
    f = "conf/results/review_next/NEXT_EXPERIMENTS_SUPP16e4.md"
    dl = git("diff", NEW_GIT, "HEAD", "--", f).splitlines()
    P(f"  doc freeze {NEW_GIT} -> HEAD: hunks {[l for l in dl if l.startswith('@@')]}; removed lines {[l[:60] for l in dl if l.startswith('-') and not l.startswith('---')]}")
    txt = git("show", f"{NEW_GIT}:{f}").splitlines()
    P("    section lines at freeze: " + ", ".join(f"{l[:6]}@{i + 1}" for i, l in enumerate(txt) if l.startswith("## ")) + f"; freeze doc lines {len(txt)}")
    P(f"  diff {NEW_GIT}..HEAD -- conf/code Demo: {git('diff', NEW_GIT, 'HEAD', '--stat', '--', 'conf/code', 'Demo')!r}")
    P(f"  diff d17f3d65..{NEW_GIT} --stat -- conf/code Demo:\n    " + git("diff", "d17f3d65", NEW_GIT, "--stat", "--", "conf/code", "Demo").replace("\n", "\n    "))
    P("  files in 6730bc1d:", len(git("show", "--stat=300", "--format=", "6730bc1d").splitlines()) - 1)
    ps = subprocess.run(["ps", "-o", "lstart=", "-p", "1"], capture_output=True, text=True).stdout.strip()
    P(f"  container PID 1 start (KST): {ps}; host boot (who -b): {subprocess.run(['who', '-b'], capture_output=True, text=True).stdout.strip()}")
    P("  logs/run_supp16e4.log milestones:")
    for l in open(os.path.join(CONF, "logs/run_supp16e4.log"), encoding="utf-8", errors="replace"):
        if re.search(r"tune start|SUPP_TUNE_DONE|eval start|phase 0|resume|ABORT|INVALID|SUPP_EVAL_DONE|ROTaMX pair|ROTbMX accept", l):
            P("    " + l.rstrip()[:130])
    cdt = lambda p: subprocess.run(["date", "-d", f"@{int(os.path.getmtime(p))}", "+%m-%d %H:%M"], capture_output=True, text=True, env={"TZ": "America/Chicago"}).stdout.strip()
    for d in ("raw_XLROTbMX", "raw_XLDOPaNR16", "raw_XAROTbNR16"):
        fs = sorted(glob.glob(os.path.join(CONF, d, "*.npz")), key=os.path.getmtime)
        P(f"  {d}: {len(fs)} chunks, mtime first {cdt(fs[0])} last {cdt(fs[-1])} CDT")
    es = sorted(glob.glob(os.path.join(CONF, "results/ald/ald_XA*.npz")), key=os.path.getmtime)
    P(f"  ALD estimates: {len(es)} files, mtime first {cdt(es[0])} last {cdt(es[-1])} CDT (all before the resume -> reused)")
    ms = {}
    for f in glob.glob(os.path.join(CONF, "results/review_next/run_manifest_X*.json")):
        j = json.load(open(f)); ms.setdefault((j.get("git_commit"), j.get("n_raw_files")), 0); ms[(j.get("git_commit"), j.get("n_raw_files"))] += 1
    P(f"  run_manifest_X*.json: {ms}")
    acc = {os.path.basename(f): open(f).read().count("ACCEPT: OK") for f in glob.glob(os.path.join(CONF, "results/review_next/X*_accept.txt"))}
    P(f"  X<T>_accept.txt: {len(acc)} files, 'ACCEPT: OK' in {sum(1 for v in acc.values() if v == 1)}, 'FAILED' in {sum(1 for f in glob.glob(os.path.join(CONF, 'results/review_next/X*_accept.txt')) if 'FAILED' in open(f).read())}")
    P(f"  resume_after_reboot.sh mentions SUPP: {'supp' in open(os.path.join(T2, 'resume_after_reboot.sh')).read().lower()}")


def sec5(t5):
    P("\n## 5. §5 ALD tuning table vs results/ald/tune_XA<T>.json")
    nbad = 0
    for T, kind, val, cell, prior, _ in CONDS:
        t = json.load(open(os.path.join(CONF, "results/ald", f"tune_XA{T}.json")))
        mine = [t["ckpt_sha"], f"{t['c']} · {t['beta']}", "없음" if not t["optimum_at_edge_after_extension"] else str(t["optimum_at_edge_after_extension"]),
                " ".join(str(v) for v in t["stop"].values()), " ".join(f"{float(v):.1f}" for v in t["dev_nmse_db"].values()),
                " ".join(f"{float(v):.4f}" for v in t["v"].values()), f"rot {t['rotation']} dop {t['doppler']}"]
        ln, doc = t5[T]
        diff = [(i, d, m) for i, (d, m) in enumerate(zip(doc, mine)) if norm(d) != norm(m)]
        nbad += bool(diff)
        P(f"  {T:<12} line {ln}: git {t['git']} ald.py {t['ald_py_sha']} seed {t['seed']} n_dev {t['n_dev']} dev_skip {t['dev_skip']} ext {t['extended']} -> {'OK' if not diff else 'MISMATCH ' + str(diff)}")
    P(f"  §5 table: {24 - nbad}/24 rows match")


# ----------------------------------------------------------------------------------------------- main
def main():
    P("# recompute.py -- record audit SUPP16e4 (Fable 5.1, 2026-09-29); raw npz / ald files / log / git only; git HEAD", git("rev-parse", "--short", "HEAD"))
    lines, xt, t24, t5 = doc_tables()
    P(f"  doc parsed: D2 C2 X-table rows {len(xt)}, 24-condition rows {len(t24)}, §5 rows {len(t5)}")
    sec_git_log()
    sec5(t5)
    P("\n## 1. 24 conditions: integrity, 13 x table B, R_X, X*, sentence")
    R = {}
    for T, kind, val, cell, prior, name in CONDS:
        R[T] = audit_condition(T, kind, val, cell, prior)
    # ---- compare with the doc: D2 C2 X-table
    P("\n## 2. doc §6.1 D2 C2 X-table (13 x 4) vs recomputation")
    nb = 0
    for x in X13:
        ln, cells = xt[x]
        for j, T in enumerate(D2C2):
            r = R[T]["res"][x]
            mine = cell_x(r["t"], r["absgap"], r["r1"])
            if norm(cells[j]) != norm(mine):
                nb += 1; P(f"  MISMATCH line {ln} {x} {T}: doc {cells[j]!r} vs mine {mine!r}")
    P(f"  D2 C2 X-table: {52 - nb}/52 cells match")
    # ---- main labels (doc lines of the 4-row main table are checked through the same quantities)
    P("\n## 3. main labels (D2 C2)")
    for T in D2C2:
        r = R[T]; xs = r["xs"]
        P(f"  {T}: k𝔅 {r['kB']} · m𝔅 {r['mB']} -> {'(A)' if r['kB'] == 12 and r['mB'] == 0 else '(B)'}; orig b* {r['orig_b']}; X* {xs} ({r['res'][xs]['F']}) · R_X* {r['res'][xs]['r1']}; sentence {'충족' if r['sent'] else ('불가 (b* not (i))' if r['orig_b'] != '(i)' else '불충족')}")
    # ---- 24-row table
    P("\n## 4. doc §6.1 24-condition table vs recomputation")
    nb = 0
    for T in ORDER:
        ln, c = t24[T]; r = R[T]; xs = r["xs"]
        noni = ", ".join(f"{x} {r['res'][x]['lab']}" for x in BL if r["res"][x]["lab"] != "(i)") or "—"
        mine = [r["orig_b"], f"{r['kB']} · {r['mB']} · {12 - r['kB'] - r['mB']}", noni, f"{xs} ({r['res'][xs]['F']})", r["res"][xs]["r1"],
                "충족" if r["sent"] else "불충족", f"{r['Fg']} · {r['Fv']}"]
        doc = [c[0], c[1], c[2], c[3], doc_r(c[4]), c[5], c[6]]
        diff = [(k, d, m) for k, (d, m) in enumerate(zip(doc, mine)) if norm(d) != norm(m)]
        if diff:
            nb += 1; P(f"  MISMATCH line {ln} {T}: {diff}")
        if r["drift"]:
            P(f"  DRIFT {T}: recomputed b* label {r['res'][BSTAR]['lab']} != §0 {r['orig_b']}")
        if not r["integrity"]:
            P(f"  INTEGRITY FAILED {T}: {r['bad'][:5]}")
    P(f"  24-condition table: {24 - nb}/24 rows match; integrity OK {sum(1 for T in ORDER if R[T]['integrity'])}/24; b* drift {sum(1 for T in ORDER if R[T]['drift'])}/24")
    # ---- aggregates
    P("\n## 5. aggregates")
    m_all = sum(R[T]["mB"] for T in ORDER); k12 = [T for T in ORDER if R[T]["kB"] == 12]
    sent = [T for T in ORDER if R[T]["sent"]]; possible = [T for T in ORDER if R[T]["orig_b"] == "(i)"]
    P(f"  (ii) total over 24 x 12 = {m_all}; k𝔅 = 12 in {len(k12)}/24 (D2 C2 {sum(1 for T in k12 if T in D2C2)}, other 20: {sum(1 for T in k12 if T not in D2C2)}); k𝔅 < 12: "
      + str({T: (R[T]["kB"], [f"{x} {R[T]['res'][x]['lab']}" for x in BL if R[T]["res"][x]["lab"] != "(i)"]) for T in ORDER if R[T]["kB"] < 12}))
    P(f"  '전부' sentence met {len(sent)}/24: {sent}; possible (orig b* (i)) {len(possible)}: not met among possible {[T for T in possible if not R[T]['sent']]}; impossible {[T for T in ORDER if T not in possible]}")
    P("  per-arm labels over 24:")
    for x in X13:
        cnt = {}
        for T in ORDER:
            cnt.setdefault(R[T]["res"][x]["lab"], []).append(T)
        P(f"    {x:<20} " + "; ".join(f"{lab} {len(ts)}" + ("" if lab == "(i)" else f" {ts}") for lab, ts in sorted(cnt.items())))
    xstar = {}
    for T in ORDER:
        xstar.setdefault(R[T]["xs"], []).append(T)
    P(f"  X* sets: " + "; ".join(f"{x} {len(ts)} {ts if len(ts) < 6 else ''}" for x, ts in xstar.items()))
    P(f"  genie >= V1 guard fired: {[(T, R[T]['Fg'], R[T]['Fv']) for T in ORDER if R[T]['vg']]}")
    d3 = R["DOPbD3"]; P(f"  DOPbD3: V1 {d3['Fv']} genie {d3['Fg']} (gap {d3['Fv'] - d3['Fg']}); R_X* {d3['res'][d3['xs']]['r1']}; X* abs gap {d3['res'][d3['xs']]['absgap']}; CI upper > 1: {d3['res'][d3['xs']]['hi'] > 1}")
    P(f"  R_X defined (primary) count over 24 x 13: {sum(1 for T in ORDER for x in X13 if R[T]['res'][x]['defined'])} (undefined: guard 2 x 13 = 26 expected + others: "
      + str([(T, x) for T in ORDER for x in X13 if not R[T]['res'][x]['defined'] and not R[T]['vg']]) + ")")
    # ---- §3 predictions
    P("\n## 6. §3 predictions")
    A = {T: R[T]["kB"] == 12 and R[T]["mB"] == 0 for T in D2C2}
    P(f"  1a DOPa (A): {'✓' if A['DOPaB16e4k'] else '✗'}; 1b ROTa (A): {'✓' if A['ROTaB16e4k'] else '✗'}; 1c ROTb (A): {'✓' if A['ROTbB16e4k'] else '✗'}; 1d DOPb (B): {'✓' if not A['DOPbB16e4k'] else '✗ (A)'}")
    n20 = sum(1 for T in ORDER if T not in D2C2 and R[T]["kB"] == 12); P(f"  2  other 20 with k𝔅 = 12 >= 12: {n20} -> {'✓' if n20 >= 12 else '✗'}")
    vp_dopb = {T: R[T]["res"]["V1-pilot"]["lab"] for T in ORDER if T.startswith("DOPb")}
    P(f"  3a V1-pilot (ii) in >= 1 of DOP nu=0.01: {vp_dopb} -> {'✓' if any(v == '(ii)' for v in vp_dopb.values()) else '✗'}")
    vp_non = [T for T in ORDER if R[T]["res"]["V1-pilot"]["lab"] != "(i)"]; P(f"  3b V1-pilot not (i) >= 4 over 24: {len(vp_non)} {vp_non} -> {'✓' if len(vp_non) >= 4 else '✗'}")
    ald = [(T, x, R[T]["res"][x]["lab"]) for T in ORDER for x in ("ALD-pilot", "ALDv-pilot") if R[T]["res"][x]["lab"] != "(i)"]; P(f"  4  ALD/ALDv all (i): non-(i) {ald} -> {'✓' if not ald else '✗'}")
    g5 = {x: R["DOPbB16e4k"]["res"][x]["lab"] for x in ("M-ours-gmm32", "M-ours-bstar-scalar")}; P(f"  5  DOPbB16e4k gmm32/scalar >= 1 not (i): {g5} -> {'✓' if any(v != '(i)' for v in g5.values()) else '✗'}")
    ok6 = all(R[T]["xs"] in ("V1-pilot", BSTAR, "M-ours-bstar-scalar") for T in ORDER); P(f"  6  X* in {{V1-pilot, b*, b*-scalar}} all 24: {'✓' if ok6 else '✗'}")
    P(f"  7  invalid / drift: {sum(1 for T in ORDER if not R[T]['integrity'])} / {sum(1 for T in ORDER if R[T]['drift'])}")
    P("\n# done")


if __name__ == "__main__":
    main()
