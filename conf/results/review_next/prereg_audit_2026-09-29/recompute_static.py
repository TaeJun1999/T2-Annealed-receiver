"""Independent re-derivation of NEXT_EXPERIMENTS_STATIC16e4.md §6.1, the STATIC16e4 row of docs/EXPERIMENTS.md and the
DECISIONS line of faebac20 (record audit 2026-09-29/30, Fable 5.1).

Reads ONLY the 18 raw npz chunk dirs (raw_<TAG> 14 arms, raw_PIL<suf>, raw_ALD<suf>), results/review_next/run_manifest_*.json,
results/ald/{ald,pilots}_PIL<suf>.*, the base V1 checkpoint file (sha), results/tables_D2_<TAG>.txt (§0 b*/R2 quotation
only), logs/run_static16e4.log and git.  pair_baselines.py / analysis.py are NOT called; the pairB_ST<TAG>.txt files are
parsed only to be COMPARED against this file's own numbers.

Reused from prereg_audit_2026-09-28/recompute.py (own implementations, verified there against analysis.load_raw
field-for-field and a reader-free hand count): Raw, fails, raised, table_b, dpoints, sign_p, recovery, merged, same, git,
sha16.  The --provenance manifest checks and the chunks-sha digest are re-implemented here from the STATIC16e4 §1 text.

    OMP_NUM_THREADS=4 CUDA_VISIBLE_DEVICES= ~/miniforge3/envs/torch/bin/python \
        results/review_next/prereg_audit_2026-09-29/recompute_static.py > .../recompute_static.out 2>&1
"""
import datetime
import glob
import hashlib
import json
import os
import re
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "prereg_audit_2026-09-28"))
from recompute import (Raw, fails, raised, table_b, recovery, merged, same, git, sha16,   # noqa: E402
                       KEYS4, GRID, V1, BSTAR, GENIE, R2, BASELINES, CONF, T2)

P = lambda *a: print(*a, flush=True)
RN = os.path.join(CONF, "results/review_next")
DOC = os.path.join(RN, "NEXT_EXPERIMENTS_STATIC16e4.md")
FREEZE, RECORD = "2139f082", "faebac20"
BL = tuple("R0-pilot@1" if x == "R0-pilot" else x for x in BASELINES)          # 𝔅 (12) with R0 read at iteration 1
X13 = (BSTAR,) + BL
BASE14 = {"M-ours-dscore-C-V0", V1, "M-ours-dscore-C-V4", "M-ours-dscore-C-V4b", BSTAR, "M-ours-bstar-scalar", "M-ours-gmm32",
          "R0-pilot", "R1-turbo", R2, "R3-bigamp", "R4-llr", "R4-scvamp", GENIE}
NEW8 = ("M-ours-bstar-scalar", "M-ours-gmm32", "R0-pilot@1", "R1-turbo", "R3-bigamp", "R4-llr", "R4-scvamp", "bstar-pilot")
# (TAG, suf, cell, prior, doc name, §0 b*, §0 P1, §0 A1, §0 A2, §0 R2 pooled, §0 X*, §0 F(X*), §0 R_X* string or None)
DS = (("B16e4k", "B16e4k", "C2", "S2", "D2 C2 (헤드라인)", "(i)", "(i)", "(i)", "(i)", "778:69", BSTAR, 623, "0.470 [0.427, 0.512]"),
      ("NR16B16e4", "NR16", "C6", "S2", "D2 C6", "(i)", "(iv)", "(i)", "(i)", "396:10", "V1-pilot", 83, None),
      ("D3B16e4", "D3", "C2", "S2c", "D3", "(i)", "(i)", "(i)", "(i)", "705:50", BSTAR, 1298, "0.367 [0.335, 0.399]"),
      ("SVB16e4", "SV", "C2", "SV8e", "SV8e", "(iv)", "(iv)", "(i)", "(i)", "302:59", BSTAR, 464, "0.143 [0.095, 0.188]"),
      ("U28B16e4", "U28", "C2", "UMi28", "UMi28", "(i)", "(i)", "(i)", "(i)", "409:41", BSTAR, 1270, "0.062 [0.033, 0.089]"),
      ("MXB16e4", "MX", "C2", "MIX3", "MIX3 (보고 전용)", "(i)", "(i)", "(i)", "(i)", "387:30", BSTAR, 1421, "0.090 [0.062, 0.117]"))
# §0: the b* runner-up at -3 dB quoted for D2 C2 / C6 (626 = V1-pilot, 184 = b*)
KST = datetime.timezone(datetime.timedelta(hours=9))


def dp_str(cand):
    return "/".join(f"{s:+.0f}" for s in cand)


def norm(s):
    return re.sub(r"\s+", " ", s.replace("−", "-").replace("\\*", "*").replace("**", "")).strip()


def r_str(defined, R, lo, hi):
    return f"{R:.3f} [{lo:.3f}, {hi:.3f}]" if defined else "undefined"


# ----------------------------------------------------------------------------------------------- provenance (STATIC16e4 §1)
def manifest_audit(tag, raw):
    """Own re-implementation of pair_baselines.manifest_check: returns (problems, header string)."""
    bad = []
    f = os.path.join(RN, f"run_manifest_{tag}.json")
    root = os.path.join(CONF, f"raw_{tag}")
    if not os.path.exists(f):
        return [f"{tag}: no manifest"], "(none)"
    rel = os.path.relpath(f, T2)
    if not git("ls-files", rel):
        bad.append(f"{tag}: manifest not tracked")
    if git("status", "--porcelain", rel):
        bad.append(f"{tag}: manifest dirty")
    m = json.load(open(f))
    chunks = sorted(glob.glob(os.path.join(root, "*.npz")))
    if m.get("n_raw_files") != len(chunks) or len(chunks) != raw.nfiles or not m.get("git_commit"):
        bad.append(f"{tag}: n_raw_files {m.get('n_raw_files')} vs {len(chunks)} chunks (reader {raw.nfiles}), git {m.get('git_commit')}")
    pts = {os.path.basename(c).rsplit("_skip", 1)[0] for c in chunks}
    if set(m.get("points", [])) != pts:
        bad.append(f"{tag}: manifest points {sorted(m.get('points', []))[:2]} != raw {sorted(pts)[:2]}")
    w = datetime.datetime.strptime(m["written"][:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=KST).timestamp()
    mt = [os.path.getmtime(c) for c in chunks]
    late = sum(1 for t in mt if t > w)
    if late:
        bad.append(f"{tag}: {late} chunks newer than manifest written {m['written']}")
    rroot = os.path.relpath(root, T2)
    tracked = bool(git("ls-files", rroot))
    if tracked and git("status", "--porcelain", rroot):
        bad.append(f"{tag}: tracked raw dir dirty")
    digest = hashlib.sha256("".join(hashlib.sha256(open(c, "rb").read()).hexdigest() for c in chunks).encode()).hexdigest()[:16]
    info = (f"manifest written {m['written']} head {m['git_commit']} n {m.get('n_raw_files')} ckpt_id {str(m.get('stagec_ckpt_id'))[:40]!r}; "
            f"chunks {len(chunks)} mtime {datetime.datetime.fromtimestamp(min(mt), KST):%m-%d %H:%M}..{datetime.datetime.fromtimestamp(max(mt), KST):%m-%d %H:%M} KST "
            f"(written - last chunk = {(w - max(mt)) / 60:.0f} min); raw tracked {tracked}")
    return bad, f"manifest-head:{m.get('git_commit')}/chunks-sha:{digest}", m, info


# ----------------------------------------------------------------------------------------------- pairB_ST parser (for comparison only)
def parse_pairb(TAG):
    lines = open(os.path.join(RN, f"pairB_ST{TAG}.txt"), encoding="utf-8").read().splitlines()
    out = dict(head=lines[0], git_hdr=None, prov=None, ckpt=None, X={}, summ=None, xstar=None, cond=None, fails={})
    cur = None
    for l in lines:
        if l.startswith("# run_static16e4 git"):
            out["git_hdr"] = l.split()[3]
        elif l.startswith("# pair_baselines"):
            out["prov"] = re.search(r"git (.*); integrity: (\w+)", l).groups()
        elif l.startswith("# base V1 checkpoint id"):
            out["ckpt"] = l
        elif re.match(r"^\S+ -> M-ours-dscore-C-V1 ", l):
            cur = l.split()[0]
            out["X"][cur] = dict(dp=re.search(r"decision SNRs \[(.*)\]", l)[1].replace("'", "").replace(", ", "/"))
        elif cur and "pooled" in l and "sign test" in l:
            out["X"][cur]["pooled"] = re.search(r"pooled (\d+:\d+)", l)[1]
        elif cur and l.strip().startswith("POWERED"):
            out["X"][cur]["lab"] = l.strip().split("-> ")[-1]
            out["X"][cur]["wy"] = re.search(r"second arm fewer at (\d)/", l)[1]
        elif cur and "R_X -3 dB (primary)" in l:
            out["X"][cur]["r1"] = l.split(": ", 1)[1].replace("[90% ", "[")
        elif cur and "absolute gap -3 dB" in l:
            out["X"][cur]["abs"] = int(re.search(r"= (-?\d+) blocks", l)[1])
        elif l.startswith("SUMMARY-B"):
            out["summ"] = l; cur = None
        elif l.startswith("X* "):
            out["xstar"] = l
        elif l.startswith("'등록된"):
            out["cond"] = l.split(": ")[-1]
        elif re.match(r"^    \S+ +(\d+ +){6}\d+$", l):
            p = l.split(); out["fails"][p[0]] = [int(v) for v in p[1:]]
    return out


# ----------------------------------------------------------------------------------------------- doc §6.1 parser
def doc_tables():
    lines = open(DOC, encoding="utf-8").read().splitlines()
    i61 = next(i for i, l in enumerate(lines) if l.startswith("### 6.1"))
    t6, xt, hdr, pred = {}, {}, {}, {}
    for i, l in enumerate(lines[i61:], i61):
        c = [norm(x) for x in l.strip().strip("|").split("|")] if l.startswith("| ") else None
        if c and len(c) == 6 and c[0] in {d[4] for d in DS}:
            t6[c[0]] = (i + 1, c[1:])
        elif c and len(c) == 4 and c[0] in X13:
            xt[c[0]] = (i + 1, c[1:])
        elif c and len(c) == 4 and re.fullmatch(r"\d[ab]?", c[0]):
            pred[c[0]] = (i + 1, c[1:])
        elif l.startswith("- ") and "chunks-sha" in l:
            name, rest = l[2:].split(": ", 1)
            hdr[name] = (i + 1, rest.strip())
    return lines, i61, t6, xt, hdr, pred


# ----------------------------------------------------------------------------------------------- per dataset
def audit_dataset(TAG, suf, cell, prior):
    base, pil, ald = Raw(TAG), Raw("PIL" + suf), Raw("ALD" + suf)
    raws = dict(base=base, pil=pil, ald=ald)
    tags = dict(base=TAG, pil="PIL" + suf, ald="ALD" + suf)
    cp = (cell, prior)
    bad = []
    for n, r in raws.items():
        if r.cp != [cp]:
            bad.append(f"{n}: (cell, prior) {r.cp}")
        if tuple(r.snrs(cp)) != GRID:
            bad.append(f"{n}: grid {r.snrs(cp)}")
        if r.holes or r.fill:
            bad.append(f"{n}: holes/NaN-fill {r.holes[:2]} {r.fill[:2]}")
        if r.scal["run|git"] != {"(none)"}:
            bad.append(f"{n}: run|git present {sorted(r.scal['run|git'])} (expected none -> manifest provenance)")
    for mk in ("meta|rotation", "meta|doppler"):
        vals = {n: r.scal[mk] for n, r in raws.items()}
        if any(v != vals["base"] for v in vals.values()):
            bad.append(f"{mk} differs {vals}")
    # provenance: manifests
    prov, mani, minfo = {}, {}, {}
    for n in ("base", "pil", "ald"):
        b, h, m, info = manifest_audit(tags[n], raws[n])
        bad += b; prov[n] = h; mani[n] = m; minfo[n] = info
    # arms
    arms = {n: set(r.arms(cp)) for n, r in raws.items()}
    if arms["base"] != BASE14:
        bad.append(f"base arms {sorted(arms['base'] ^ BASE14)}")
    if arms["pil"] - {GENIE} != {"V1-pilot", "bstar-pilot"} or arms["ald"] - {GENIE} != {"ALD-pilot", "ALDv-pilot"}:
        bad.append(f"pil/ald arms {sorted(arms['pil'])} {sorted(arms['ald'])}")
    for s in GRID:
        db = base.d(cp, s)
        for n in ("pil", "ald"):
            if GENIE not in raws[n].d(cp, s) or any(not same(db[GENIE][q], raws[n].d(cp, s)[GENIE][q]) for q in KEYS4):
                bad.append(f"{s:+.0f} {n}: genie != base")
        if any(len(r.d(cp, s)[a]["blk_err"]) != 2560 for r in raws.values() for a in r.d(cp, s)):
            bad.append(f"{s:+.0f}: n != 2560")
        for arm, r in (("V1-pilot", pil), ("bstar-pilot", pil), ("ALD-pilot", ald), ("ALDv-pilot", ald)):
            if raised(r.d(cp, s), arm).any():
                bad.append(f"{s:+.0f} {arm}: raised {int(raised(r.d(cp, s), arm).sum())}")
        for x, y in (("V1-pilot", V1), ("bstar-pilot", BSTAR)):
            ok = ~(raised(pil.d(cp, s), x) | raised(db, y))
            if not same(np.asarray(pil.d(cp, s)[x]["nmse"])[ok, 0], np.asarray(db[y]["nmse"])[ok, 0]):
                bad.append(f"{s:+.0f} {x}@1 != {y}@1")
    # base V1 checkpoint id: meta|stagec_ckpt_id, else manifest, else file sha (§1)
    bm = base.m(cp)
    sid = str(bm.get("meta|stagec_ckpt_id", "")).split()
    bsha = sid[0].replace("sha256[:16]=", "") if sid else ""
    ckpt_note = f"meta|stagec_ckpt_id {bsha or '(absent)'}"
    if not bsha:
        msid = str(mani["base"].get("stagec_ckpt_id", "")).split()
        msha = msid[0].replace("sha256[:16]=", "") if msid and msid[0] != "(none)" else ""
        cf = str(bm.get("meta|stagec_ckpt", ""))
        fsha = sha16(cf) if cf and os.path.exists(cf) else ""
        ckpt_note += f"; manifest {msha or '(none)'}; file {os.path.basename(cf)} sha {fsha or '(missing)'}"
        if msha and msha != fsha:
            bad.append(f"base ckpt manifest {msha} != file {fsha}")
        bsha = msha or fsha
    else:
        msid = str(mani["base"].get("stagec_ckpt_id", "")).split()
        msha = msid[0].replace("sha256[:16]=", "") if msid else ""
        ckpt_note += f"; manifest {msha}"
        if msha != bsha:
            bad.append(f"base ckpt meta {bsha} != manifest {msha}")
    # ALD estimate: fixed over iterations, equal to the precomputed file, ckpt = base V1 ckpt, no rotation/doppler
    est = np.load(os.path.join(CONF, "results/ald", f"ald_PIL{suf}.npz"), allow_pickle=True)
    pilf = np.load(os.path.join(CONF, "results/ald", f"pilots_PIL{suf}_test.npz"), allow_pickle=True)
    provj = json.loads(str(est["prov"])) if "prov" in est.files else {}
    esha = str(est["ckpt_sha"]) if "ckpt_sha" in est.files else ""
    if not bsha or provj.get("ckpt_sha") != bsha or esha != bsha:
        bad.append(f"ALD est ckpt {provj.get('ckpt_sha')}/{esha} != base {bsha!r}")
    for k, arr in (("rotation", pilf), ("doppler", pilf), ("rotation", est), ("doppler", est)):
        if k in arr.files and float(arr[k]) not in (-1.0, 0.0):
            bad.append(f"ALD {k} {float(arr[k])} (static expected)")
    nm_test = []
    for j, s in enumerate(est["snrs"]):
        H, hh = pilf["H"][j], est["hhat"][j]
        ref = np.sum(np.abs(hh - H) ** 2, -1) / np.sum(np.abs(H) ** 2, -1); nm_test.append(float(np.median(ref)))
        if not (len(H) == len(hh) == 2560):
            bad.append(f"{s:+.0f}: est/pilot trials {len(H)}/{len(hh)}")
        for arm in ("ALD-pilot", "ALDv-pilot"):
            nm = np.asarray(ald.d(cp, float(s))[arm]["nmse"])
            if not same(nm, np.repeat(nm[:, :1], nm.shape[1], axis=1)) or not np.allclose(nm[:, 0], ref, rtol=1e-9, atol=0):
                bad.append(f"{s:+.0f} {arm}: estimate not fixed / not the precomputed one")
    P(f"\n  [{TAG}] files base {base.nfiles} pil {pil.nfiles} ald {ald.nfiles}; run|git base {sorted(base.scal['run|git'])} pil {sorted(pil.scal['run|git'])} ald {sorted(ald.scal['run|git'])}; "
      f"rotation {sorted(base.scal['meta|rotation'])} doppler {sorted(base.scal['meta|doppler'])}")
    for n in ("base", "pil", "ald"):
        P(f"    {n:<4} raw_{tags[n]:<10} {minfo[n]}")
        P(f"         -> {prov[n]}")
    P(f"    base V1 ckpt: {ckpt_note}; ALD est prov git {provj.get('git')} ckpt {provj.get('ckpt_sha')} est ckpt_sha {esha}; ALD median NMSE@16 -3 dB {nm_test[0]:.2e}")
    P(f"    integrity (grid, holes, run|git absent on all 3 raws, rotation/doppler equal, manifest tracked+clean / n_raw_files / point list / chunk mtime <= written / tracked raw clean, "
      f"base 14 arms, PIL/ALD arm sets, genie 4 keys PIL/ALD = base, n 2560, PIL/ALD raised 0, pilot@1 = loop@1, base ckpt id chain, ALD estimate fixed = precomputed, ALD ckpt = base V1): "
      f"{'OK' if not bad else 'FAILED ' + '; '.join(bad[:8])}")
    # ---- merged data; R0-pilot@1 = trajectory truncated at iteration 1
    D = merged(cp, (base, {a: a for a in (V1, BSTAR, R2, GENIE, "M-ours-bstar-scalar", "M-ours-gmm32", "R0-pilot", "R1-turbo", "R3-bigamp", "R4-llr", "R4-scvamp",
                                              "M-ours-dscore-C-V0", "M-ours-dscore-C-V4", "M-ours-dscore-C-V4b")}),
               (pil, {"V1-pilot": "V1-pilot", "bstar-pilot": "bstar-pilot"}), (ald, {"ALD-pilot": "ALD-pilot", "ALDv-pilot": "ALDv-pilot"}))
    for s in D:
        D[s]["R0-pilot@1"] = {q: np.asarray(a)[:, :1] for q, a in D[s]["R0-pilot"].items() if getattr(a, "ndim", 0) == 2}
    fv3, fg3 = fails(D[-3.0], V1), fails(D[-3.0], GENIE)
    vg = fg3.sum() >= fv3.sum()
    P(f"    -3 dB genie {int(fg3.sum())} · V1 {int(fv3.sum())} -> genie >= V1 guard {'FIRED' if vg else 'not fired'}")
    res = {}
    for x in X13:
        t = table_b(D, x, V1)
        fx = fails(D[-3.0], x); F = int(fx.sum()); absgap = F - int(fv3.sum()); bl = fx.mean()
        if vg or not (0.005 <= bl <= 0.9) or F <= fg3.sum():
            defined, R, lo, hi = False, np.nan, np.nan, np.nan
        else:
            R, lo, hi, nn, _ = recovery([(fx, fv3, fg3)]); defined = nn <= 0.05 * 2000
        res[x] = dict(t=t, lab=t["lab"], F=F, absgap=absgap, defined=defined, R=R, lo=lo, hi=hi, r1=r_str(defined, R, lo, hi))
        P(f"      {x:<20} {dp_str(t['cand']):<12} " + " · ".join(f"{a}:{b} (p {p:.2g})" for a, b, p in t["res"]) + f"  pooled {t['A']}:{t['B']} -> {t['lab']} {t['wy']}/{len(t['cand'])} "
          f"(powered {t['powered']}); F -3 dB {F}; abs gap {absgap}; R_X {res[x]['r1']}")
    kB = sum(1 for x in BL if res[x]["lab"] == "(i)"); mB = sum(1 for x in BL if res[x]["lab"] == "(ii)")
    order = sorted(X13, key=lambda x: (res[x]["F"], x)); xs = order[0]
    fr = {a: [int(fails(D[s], a).sum()) for s in GRID] for a in D[-3.0]}
    return dict(res=res, kB=kB, mB=mB, xs=xs, runner=order[1], vg=vg, Fg=int(fg3.sum()), Fv=int(fv3.sum()), integrity=not bad, bad=bad, prov=prov, fails=fr,
                nm3=nm_test[0])


# ----------------------------------------------------------------------------------------------- git / log
def sec_git_log():
    P("\n## G. git / documents / log")
    P("  HEAD", git("rev-parse", "--short", "HEAD"), "| dirty conf/code Demo:", repr(git("status", "--porcelain", "conf/code", "Demo")),
      "| dirty records:", repr(git("status", "--porcelain", "conf/results/review_next/NEXT_EXPERIMENTS_STATIC16e4.md", "docs/EXPERIMENTS.md", "conf/DECISIONS.md",
                                   "conf/results/review_next")))
    for h in (FREEZE, RECORD, "HEAD"):
        P(f"  {h}: {git('log', '-1', '--format=%h %p %ad %s', '--date=format-local:%Y-%m-%d %H:%M:%S KST', h)[:150]}")
    f = "conf/results/review_next/NEXT_EXPERIMENTS_STATIC16e4.md"
    dl = git("diff", FREEZE, "HEAD", "--", f).splitlines()
    P(f"  doc freeze {FREEZE} -> HEAD: hunks {[l for l in dl if l.startswith('@@')]}; removed lines {[l[:60] for l in dl if l.startswith('-') and not l.startswith('---')]}")
    txt = git("show", f"{FREEZE}:{f}").splitlines()
    P("    section lines at freeze: " + ", ".join(f"{l[:6]}@{i + 1}" for i, l in enumerate(txt) if l.startswith("## ")) + f"; freeze doc lines {len(txt)}")
    P(f"  diff {FREEZE}..HEAD -- conf/code Demo: {git('diff', FREEZE, 'HEAD', '--stat', '--', 'conf/code', 'Demo')!r}")
    P(f"  files in {RECORD}: " + git("show", "--stat=200", "--format=", RECORD).replace("\n", "\n    "))
    P(f"  commits {RECORD}..HEAD: {git('log', '--oneline', f'{RECORD}..HEAD')!r}")
    P("  logs/run_static16e4.log:")
    for l in open(os.path.join(CONF, "logs/run_static16e4.log"), encoding="utf-8", errors="replace"):
        P("    " + l.rstrip()[:140])
    cdt = lambda p: datetime.datetime.fromtimestamp(os.path.getmtime(p), datetime.timezone(datetime.timedelta(hours=-5))).strftime("%m-%d %H:%M")
    P("  pairB_ST mtimes (CDT): " + ", ".join(f"{os.path.basename(p)} {cdt(p)}" for p in sorted(glob.glob(os.path.join(RN, "pairB_ST*.txt")))))
    P(f"  run_static16e4.sh at {FREEZE} == HEAD: {git('diff', FREEZE, 'HEAD', '--', 'conf/code/run_static16e4.sh') == ''}")
    # §0 quotations: tables_D2_<TAG>.txt table B rows for b* and R2
    P("  §0 quotation sources (tables_D2_<TAG>.txt, analysis table B): b* / R2 pooled + verdict")
    q = {}
    for TAG, *_ in DS:
        lines = open(os.path.join(CONF, "results", f"tables_D2_{TAG}.txt"), encoding="utf-8", errors="replace").read().splitlines()
        for x in (BSTAR, R2):
            i = next(i for i, l in enumerate(lines) if l.strip().startswith(f"{x} -> {V1}"))
            blk = lines[i:i + 5]
            pooled = re.search(r"pooled (\d+:\d+)", blk[2])[1]
            dp = re.search(r"decision SNRs \[(.*?)\]", blk[1])[1].replace("'", "").replace(", ", "/")
            lab = "(iv)" if "UNDECIDED" in blk[3] else ("(i)" if "second arm fewer failures at 2/3" in blk[4] or "second arm fewer failures at 3/3" in blk[4] else "?")
            q[(TAG, x)] = (dp, pooled, lab)
        P(f"    {TAG:<10} b* {q[(TAG, BSTAR)]}  R2 {q[(TAG, R2)]}")
    return q


# ----------------------------------------------------------------------------------------------- main
def main():
    P("# recompute_static.py -- record audit STATIC16e4 (Fable 5.1, 2026-09-30 KST); raw npz / manifests / ald files / log / git only; git HEAD", git("rev-parse", "--short", "HEAD"))
    P(f"  𝔅 (12) = {BL}")
    lines, i61, t6, xt, hdr, pred = doc_tables()
    P(f"  doc parsed: §6.1 @ line {i61 + 1}; 6-row table {len(t6)}, D2 C2 X-table {len(xt)}, header lines {len(hdr)}, prediction rows {len(pred)}")
    q = sec_git_log()
    P("\n## 1. 6 datasets: integrity, provenance, 13 x table B, R_X, X*, sentence")
    R = {}
    for TAG, suf, cell, prior, *_ in DS:
        R[TAG] = audit_dataset(TAG, suf, cell, prior)
    P("\n## 2. per dataset summary (own numbers) and comparison with pairB_ST<TAG>.txt (all 13 X: dp, pooled, label, k/3, abs gap, R_X primary; X*, R_X*, condition, failure rows)")
    nb_pb = 0
    for TAG, suf, cell, prior, name, b0, p1, a1, a2, r2p, xs0, F0, rx0 in DS:
        r = R[TAG]; xs = r["xs"]; res = r["res"]
        sent = (b0 == "(i)") and r["kB"] == 12 and r["mB"] == 0 and res[xs]["defined"] and res[xs]["lo"] > 0
        r["sent"] = sent
        P(f"  {TAG:<10} k𝔅 {r['kB']} m𝔅 {r['mB']} undecided {12 - r['kB'] - r['mB']}; b* {res[BSTAR]['lab']} (§0 {b0}); non-(i) 𝔅: "
          + (", ".join(f"{x} {res[x]['lab']}" for x in BL if res[x]["lab"] != "(i)") or "—")
          + f"; X* {xs} (F {res[xs]['F']}; runner-up {r['runner']} F {res[r['runner']]['F']}); R_X* {res[xs]['r1']}; sentence {'MET' if sent else 'NOT met'}; "
          f"main (D2 C2 only) {'(A)' if r['kB'] == 12 and r['mB'] == 0 else '(B)'}")
        pb = parse_pairb(TAG)
        d = []
        if pb["git_hdr"] != FREEZE:
            d.append(f"header git {pb['git_hdr']}")
        want_prov = f"base={r['prov']['base']} pil={r['prov']['pil']} ald={r['prov']['ald']}"
        if pb["prov"][0] != want_prov or pb["prov"][1] != "OK":
            d.append(f"prov line {pb['prov']} vs mine {want_prov}")
        for x in X13:
            t = res[x]["t"]; px = pb["X"].get(x, {})
            mine = (dp_str(t["cand"]), f"{t['A']}:{t['B']}", t["lab"], str(t["wy"]), res[x]["absgap"], res[x]["r1"])
            theirs = (px.get("dp"), px.get("pooled"), px.get("lab"), px.get("wy"), px.get("abs"), re.sub(r"^undefined.*", "undefined", px.get("r1", "")))
            if mine != theirs:
                d.append(f"{x}: mine {mine} vs file {theirs}")
        ms = f"SUMMARY-B (baselines without b*, 12): (i) {r['kB']}, (ii) {r['mB']}, not decided {12 - r['kB'] - r['mB']}; b* -> V1 {res[BSTAR]['lab']}"
        if pb["summ"] != ms:
            d.append(f"SUMMARY-B {pb['summ']!r} vs {ms!r}")
        mx = f"X* (fewest -3 dB failures, ties by name) = {xs} (F={res[xs]['F']}); R_X* -3 dB = " + (f"{res[xs]['R']:.3f} [90% {res[xs]['lo']:.3f}, {res[xs]['hi']:.3f}]" if res[xs]["defined"] else "undefined (out of range)")
        if pb["xstar"] != mx:
            d.append(f"X* line {pb['xstar']!r} vs {mx!r}")
        # the file's condition = k = 13 & (ii) = 0 & lower > 0 (recomputed b*, not §0 b*): compare on that definition
        fcond = (res[BSTAR]["lab"] == "(i)") and r["kB"] == 12 and r["mB"] == 0 and res[xs]["defined"] and res[xs]["lo"] > 0
        if pb["cond"] != ("MET" if fcond else "NOT met"):
            d.append(f"condition {pb['cond']} vs {'MET' if fcond else 'NOT met'}")
        for a, row in pb["fails"].items():
            if r["fails"].get(a) != row:
                d.append(f"fail row {a}: file {row} vs mine {r['fails'].get(a)}")
        nb_pb += bool(d)
        P(f"    vs pairB_ST{TAG}.txt: {'identical (13 X x 6 fields, SUMMARY-B, X*, condition, ' + str(len(pb['fails'])) + ' failure rows, provenance header)' if not d else 'DIFF ' + '; '.join(d)}")
    P(f"  pairB_ST files matching own recomputation: {6 - nb_pb}/6")
    # ---- §0
    P("\n## 3. §0 'already known' labels vs recomputation and vs their quoted sources")
    nb0 = 0
    for TAG, suf, cell, prior, name, b0, p1, a1, a2, r2p, xs0, F0, rx0 in DS:
        r = R[TAG]; res = r["res"]
        chk = {"b*": (res[BSTAR]["lab"], b0), "P1 V1-pilot": (res["V1-pilot"]["lab"], p1), "A1 ALDv-pilot": (res["ALDv-pilot"]["lab"], a1), "A2 ALD-pilot": (res["ALD-pilot"]["lab"], a2),
               "R2": (res[R2]["lab"], "(i)"), "R2 pooled": (f"{res[R2]['t']['A']}:{res[R2]['t']['B']}", r2p), "X*": (r["xs"], xs0), "F(X*)": (res[r["xs"]]["F"], F0)}
        if rx0:
            chk["R_X*"] = (res[r["xs"]]["r1"], rx0)
        # tables_D2 sources
        chk["b* vs tables_D2"] = ((dp_str(res[BSTAR]["t"]["cand"]), f"{res[BSTAR]['t']['A']}:{res[BSTAR]['t']['B']}", res[BSTAR]["lab"]), q[(TAG, BSTAR)])
        chk["R2 vs tables_D2"] = ((dp_str(res[R2]["t"]["cand"]), f"{res[R2]['t']['A']}:{res[R2]['t']['B']}", res[R2]["lab"]), q[(TAG, R2)])
        bad = {k: v for k, v in chk.items() if v[0] != v[1]}
        nb0 += bool(bad)
        P(f"  {TAG:<10} {'all match (' + str(len(chk)) + ' items)' if not bad else 'MISMATCH ' + str(bad)}")
    P(f"  §0 rows consistent: {6 - nb0}/6")
    # ---- doc §6.1 6-row table
    P("\n## 4. doc §6.1 6-row table vs recomputation")
    nb = 0
    for TAG, suf, cell, prior, name, b0, *_ in DS:
        r = R[TAG]; res = r["res"]; xs = r["xs"]; ln, c = t6[name]
        noni = ", ".join(f"{x} {res[x]['lab']}" for x in BL if res[x]["lab"] != "(i)") or "—"
        mine = [b0, f"{r['kB']} · {r['mB']} · {12 - r['kB'] - r['mB']}", noni, f"{xs} ({res[xs]['F']}) · {res[xs]['r1']}", "충족" if r["sent"] else "불충족"]
        diff = [(k, d, m) for k, (d, m) in enumerate(zip(c, mine)) if norm(d) != norm(m)]
        if diff:
            nb += 1; P(f"  MISMATCH line {ln} {name}: {diff}")
        else:
            P(f"  line {ln} {name}: OK")
    P(f"  6-row table: {6 - nb}/6 rows match")
    # ---- D2 C2 X-table
    P("\n## 5. doc §6.1 D2 C2 X-table (13 x 3) vs recomputation")
    nb = 0
    for x in X13:
        ln, c = xt[x]; t = R["B16e4k"]["res"][x]["t"]
        mine = [dp_str(t["cand"]), f"{t['A']}:{t['B']}", f"{t['lab']} {t['wy']}/{len(t['cand'])}"]
        diff = [(k, d, m) for k, (d, m) in enumerate(zip(c, mine)) if norm(d) != norm(m)]
        if diff:
            nb += 1; P(f"  MISMATCH line {ln} {x}: {diff}")
    P(f"  D2 C2 X-table: {13 - nb}/13 rows match")
    # ---- header lines
    P("\n## 6. doc §6.1 provenance header lines vs own manifest-head / chunks-sha")
    nb = 0
    for TAG, suf, cell, prior, name, *_ in DS:
        ln, s = hdr[name]; r = R[TAG]
        mine = f"base={r['prov']['base']} pil={r['prov']['pil']} ald={r['prov']['ald']}"
        if s != mine:
            nb += 1; P(f"  MISMATCH line {ln} {name}: doc {s!r} vs mine {mine!r}")
    P(f"  header lines: {6 - nb}/6 match")
    # ---- aggregates
    P("\n## 7. aggregates")
    new = [(TAG, x) for TAG, *_ in DS for x in NEW8]
    cnt = {}
    for TAG, x in new:
        cnt.setdefault(R[TAG]["res"][x]["lab"], []).append((TAG, x))
    P(f"  new 48 labels: " + "; ".join(f"{lab} {len(v)}" + ("" if lab == "(i)" else f" {v}") for lab, v in sorted(cnt.items())))
    all72 = {lab: sum(1 for TAG, *_ in DS for x in BL if R[TAG]["res"][x]["lab"] == lab) for lab in ("(i)", "(ii)", "(iii)", "(iv)")}
    P(f"  72 labels (𝔅 x 6): {all72}; b* 6: {[R[TAG]['res'][BSTAR]['lab'] for TAG, *_ in DS]}")
    k12 = [TAG for TAG, *_ in DS if R[TAG]["kB"] == 12]; sent = [TAG for TAG, *_ in DS if R[TAG]["sent"]]
    poss = [TAG for TAG, suf, cell, prior, name, b0, p1, *_ in DS if b0 == "(i)" and p1 == "(i)"]
    P(f"  k𝔅 = 12: {len(k12)}/6 {k12}; k𝔅 < 12: {[(TAG, R[TAG]['kB']) for TAG, *_ in DS if R[TAG]['kB'] < 12]}")
    P(f"  sentence met {len(sent)}/6 {sent}; possible per §0 (b* (i) and P1 (i)) {len(poss)} {poss}; met among possible {len([t for t in poss if t in sent])}/{len(poss)}")
    P(f"  genie >= V1 guard fired: {[TAG for TAG, *_ in DS if R[TAG]['vg']]}; R_X primary undefined (dataset, X): {[(TAG, x) for TAG, *_ in DS for x in X13 if not R[TAG]['res'][x]['defined']]}")
    P(f"  D2 C2 main label: k𝔅 {R['B16e4k']['kB']} m𝔅 {R['B16e4k']['mB']} -> {'(A)' if R['B16e4k']['kB'] == 12 and R['B16e4k']['mB'] == 0 else '(B)'}; b* {R['B16e4k']['res'][BSTAR]['lab']}; "
      f"R_X* lower {R['B16e4k']['res'][R['B16e4k']['xs']]['lo']:.3f} > 0: {R['B16e4k']['res'][R['B16e4k']['xs']]['lo'] > 0}")
    P(f"  C6 R_V1-pilot (new value): {R['NR16B16e4']['res']['V1-pilot']['r1']}; -3 dB F: V1-pilot {R['NR16B16e4']['res']['V1-pilot']['F']} b* {R['NR16B16e4']['res'][BSTAR]['F']} V1 {R['NR16B16e4']['Fv']} genie {R['NR16B16e4']['Fg']}")
    P(f"  ALD median NMSE@16 at -3 dB per dataset: {[(TAG, f'{R[TAG]['nm3']:.2e}') for TAG, *_ in DS]}")
    # ---- §3 predictions
    P("\n## 8. §3 predictions (scored on the open 48 labels only)")
    lab = lambda TAG, x: R[TAG]["res"][x]["lab"]
    s = {}
    s["1"] = R["B16e4k"]["kB"] == 12 and R["B16e4k"]["mB"] == 0
    s["2"] = all(lab("D3B16e4", x) == "(i)" for x in NEW8)
    s["3"] = all(lab("U28B16e4", x) == "(i)" for x in NEW8)
    s["4"] = all(lab("MXB16e4", x) == "(i)" for x in NEW8)
    s["5"] = all(lab("NR16B16e4", x) == "(i)" for x in NEW8) and R["NR16B16e4"]["kB"] == 11
    s["6a"] = lab("SVB16e4", "M-ours-bstar-scalar") == "(iv)" and lab("SVB16e4", "M-ours-gmm32") == "(iv)"
    s["6b"] = all(lab("SVB16e4", x) == "(i)" for x in NEW8 if x not in ("M-ours-bstar-scalar", "M-ours-gmm32"))
    s["7"] = not any(lab(TAG, x) == "(ii)" for TAG, x in new)
    for k, v in s.items():
        dv = pred.get(k, (None, ["?", "?", "?"]))[1][2]
        P(f"  {k}: {'✓' if v else '✗'} (doc {dv}{'' if (v and '✓' in dv) or (not v and '✗' in dv) else ' <- MISMATCH'})")
    P(f"  hits {sum(s.values())}/{len(s)}; §3 item 8 (invalid / drift): {sum(1 for TAG, *_ in DS if not R[TAG]['integrity'])} / "
      f"{sum(1 for TAG, suf, cell, prior, name, b0, p1, a1, a2, *_ in DS if (R[TAG]['res'][BSTAR]['lab'], R[TAG]['res']['V1-pilot']['lab'], R[TAG]['res']['ALDv-pilot']['lab'], R[TAG]['res']['ALD-pilot']['lab'], R[TAG]['res'][R2]['lab']) != (b0, p1, a1, a2, '(i)'))}")
    P(f"  SV8e new 6 (non-scalar/gmm32) labels: {[(x, lab('SVB16e4', x)) for x in NEW8 if x not in ('M-ours-bstar-scalar', 'M-ours-gmm32')]}; SV8e b*-scalar dp {dp_str(R['SVB16e4']['res']['M-ours-bstar-scalar']['t']['cand'])}, gmm32 dp {dp_str(R['SVB16e4']['res']['M-ours-gmm32']['t']['cand'])}, b* dp {dp_str(R['SVB16e4']['res'][BSTAR]['t']['cand'])}")
    P("\n# done")


if __name__ == "__main__":
    main()
