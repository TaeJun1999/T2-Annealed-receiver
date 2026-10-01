"""Independent re-derivation of NEXT_EXPERIMENTS_SPARSE16e4.md §6.1, the SPARSE16e4 row of docs/EXPERIMENTS.md and the
'[2026-10-01 10:30 KST] SPARSE16e4 결과 기록' line of conf/DECISIONS.md (record audit 2026-10-01, Fable 5.1).

Reads ONLY the raw npz chunk dirs (raw_<TAG> 14 arms, raw_PIL<suf>, raw_ALD<suf>, raw_SP<suf>), results/sparse/{pick,tune}_*.json,
results/review_next/run_manifest_SP*.json, SP*_accept.txt, the logs and git.  pair_baselines.py / analysis.py / eval_accept.py
are NOT called; pairB_SP<suf>.txt and the three record files are parsed only to be COMPARED against this file's own numbers.
sparse_tune.per_snr_pick (the registered §1 rule itself, frozen in 02dafa1c) is applied to the tune JSONs to re-check the
pick reproduction the script logged.

Reused from prereg_audit_2026-09-28/recompute.py (own implementations, verified there against analysis.load_raw field-for-field
and a reader-free hand count; reused again by prereg_audit_2026-09-29/recompute_static.py): Raw, fails, raised, table_b,
dpoints, sign_p, recovery, gap (= Demo/exp_0925_analysis.gain, seed 20260925), merged, same, git, sha16.

    OMP_NUM_THREADS=4 CUDA_VISIBLE_DEVICES= ~/miniforge3/envs/torch/bin/python \
        results/review_next/prereg_audit_2026-10-01/sparse_recompute.py > .../sparse_recompute.out 2> .../sparse_recompute.err
"""
import datetime
import glob
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "prereg_audit_2026-09-28"))
from recompute import (Raw, fails, raised, table_b, recovery, gap, merged, same, git, sha16,   # noqa: E402
                       KEYS4, GRID, V1, BSTAR, GENIE, BASELINES, CONF, T2, PAT)

P = lambda *a: print(*a, flush=True)
RN = os.path.join(CONF, "results/review_next")
DOC = os.path.join(RN, "NEXT_EXPERIMENTS_SPARSE16e4.md")
FREEZE = "02dafa1c"
NEW = ("SBL-loop", "SBL-pilot", "OMP-pilot")
BL = tuple("R0-pilot@1" if x == "R0-pilot" else x for x in BASELINES) + NEW          # 𝔅 15
X16 = (BSTAR,) + BL
CDT = datetime.timezone(datetime.timedelta(hours=-5))
KST = datetime.timezone(datetime.timedelta(hours=9))
# suf, TAG, cell, prior, pick file, §5 pick sha, §5 tune sha, doc name, summary-table name, §0 original b* (STATIC16e4), STATIC (iv) arms
ROWS = (("B16e4k", "B16e4k", "C2", "S2", "pick_S2_C2.json", "2a6d79a23b6b6501", "6f1e19bd6ce05bd3", "D2 C2", "D2 C2 (헤드라인)", "(i)", ()),
        ("D3", "D3B16e4", "C2", "S2c", "pick_S2c_C2.json", "afdb48498c76b88c", "42b078018bea5471", "D3", "D3", "(i)", ()),
        ("SV", "SVB16e4", "C2", "SV8e", "pick_SV8e_C2.json", "72a6500e72950141", "1b737191fdf8e668", "SV8e", "SV8e", "(iv)", ("M-ours-bstar-scalar", "M-ours-gmm32", "V1-pilot")),
        ("U28", "U28B16e4", "C2", "UMi28", "pick_UMi28_C2.json", "3d27f1bb72865fa5", "4099975241c07a0d", "UMi28", "UMi28", "(i)", ()),
        ("MX", "MXB16e4", "C2", "MIX3", "pick_MIX3_C2.json", "baffec3e463ad6b3", "b02e6acacfb7aa5e", "MIX3", "MIX3", "(i)", ()),
        ("NR16", "NR16B16e4", "C6", "S2", "pick_S2_C6.json", "3958df589e385522", "81dba7612d964a06", "D2 C6", "D2 C6", "(i)", ("V1-pilot",)))
CELLN = {"C2": 32, "C6": 64}                   # Nr * Nt (C2: 8 x 4, C6: 16 x 4)
SNRS = ("-3", "0", "3", "6", "9", "12", "15")
NCHK = [0]
MISS = []


def chk(what, mine, theirs, where=""):
    """one audited fact: own value vs the record's value; a mismatch is listed, never silently passed."""
    NCHK[0] += 1
    if norm(str(mine)) != norm(str(theirs)):
        MISS.append(f"{where} {what}: mine {mine!r} vs record {theirs!r}")
        P(f"    MISMATCH {where} {what}: mine {mine!r} vs record {theirs!r}")


def norm(s):
    return re.sub(r"\s+", " ", s.replace("−", "-").replace("–", "-").replace("\\*", "*").replace("**", "").replace("\\|", "|")).strip()


def dp_str(cand):
    return "/".join(f"{s:+.0f}" for s in cand)


def cdt(t):
    return datetime.datetime.fromtimestamp(t, CDT).strftime("%m-%d %H:%M:%S")


def gap_text(g, x):
    """the pair_baselines (exp_0925_analysis.gain) wording rebuilt from the own gap() result."""
    t = g["text"]
    if t.startswith("n/a"):
        return "n/a (<= -3 vs <= -3) — extend the SNR grid" if "lo vs" in t and t.endswith("lo)") else t
    if "never reaches" in t:
        return f">= {g['est']:+.2f} dB ({x} never reaches 0.1 on the grid)"
    if "already" in t:
        return f">= {g['est']:+.2f} dB ({V1} is already below 0.1 at the lowest grid SNR)"
    return f"{g['est']:+.2f} [{g['lo']:+.2f}, {g['hi']:+.2f}]"


# ----------------------------------------------------------------------------------------------- pairB_SP parser (comparison only)
def parse_pairb(suf):
    lines = open(os.path.join(RN, f"pairB_SP{suf}.txt"), encoding="utf-8").read().splitlines()
    out = dict(lines=lines, X={}, fails={}, nmse={}, blockline={})
    cur = None
    for i, l in enumerate(lines, 1):
        if l.startswith("# run_sparse16e4 git"):
            out["git_hdr"] = l.split()[3]; out["hdr_time"] = " ".join(l.split()[4:])
        elif l.startswith("# pair_baselines"):
            out["prov"], out["integrity"] = re.search(r"git (.*); integrity: (\w+)", l).groups()
        elif l.startswith("# base V1 checkpoint id"):
            out["ckpt"] = l
        elif re.match(r"^\S+ -> M-ours-dscore-C-V1 ", l):
            cur = l.split()[0]; out["blockline"][cur] = i
            out["X"][cur] = dict(dp=re.search(r"decision SNRs \[(.*)\]", l)[1].replace("'", "").replace(", ", "/"))
        elif cur and "pooled" in l and "sign test" in l:
            out["X"][cur]["pts"] = " · ".join(re.findall(r"dB (\d+:\d+) p=", l)); out["X"][cur]["pooled"] = re.search(r"pooled (\d+:\d+)", l)[1]
            out["X"][cur]["pps"] = re.findall(r"p=(\S+)", l)
        elif cur and l.strip().startswith("POWERED"):
            out["X"][cur]["lab"] = l.strip().split("-> ")[-1]; out["X"][cur]["powered"] = "POWERED=True" in l
            out["X"][cur]["wy"], out["X"][cur]["npt"] = re.search(r"second arm fewer at (\d)/(\d)", l).groups()
        elif cur and "SNR@0.1 gap" in l:
            out["X"][cur]["gap"] = l.split("): ", 1)[1]
        elif cur and "absolute gap -3 dB" in l:
            out["X"][cur]["abs"] = int(re.search(r"= (-?\d+) blocks of (\d+)", l)[1]); out["X"][cur]["n"] = int(re.search(r"of (\d+)", l)[1])
        elif cur and "R_X -3 dB (primary)" in l:
            out["X"][cur]["r1"] = l.split(": ", 1)[1].replace("[90% ", "[")
        elif cur and "R_X decision points (secondary)" in l:
            out["X"][cur]["r2"] = l.split(": ", 1)[1].replace("[90% ", "[")
        elif l.startswith("SUMMARY-B"):
            out["summB"] = l; out["summB_line"] = i; cur = None
        elif l.startswith("SUMMARY registered"):
            out["summ16"] = l; out["summ16_line"] = i
        elif l.startswith("    M-ours-bstar=("):
            out["labels"] = dict(x.split("=") for x in l.split())
        elif l.startswith("X* "):
            out["xstar"] = l; out["xstar_line"] = i
        elif l.startswith("'등록된"):
            out["cond"] = l.split(": ")[-1]; out["cond_line"] = i
        elif l.startswith("BLER@16 failures"):
            out["fails_line"] = i; cur = None; mode = "f"
        elif l.startswith("report-only, median NMSE"):
            out["nmse_line"] = i; mode = "n"
        elif re.match(r"^    \S+ +(\d+ +){6}\d+$", l):
            p = l.split(); out["fails"][p[0]] = [int(v) for v in p[1:]]; out["fails"].setdefault("_line", {})[p[0]] = i
        elif re.match(r"^    \S+ +(\S+e[-+]\d+ +){6}\S+e[-+]\d+$", l):
            p = l.split(); out["nmse"][p[0]] = p[1:]; out["nmse"].setdefault("_line", {})[p[0]] = i
    return out


# ----------------------------------------------------------------------------------------------- doc §6.1 parser
def doc_tables():
    lines = open(DOC, encoding="utf-8").read().splitlines()
    i61 = next(i for i, l in enumerate(lines) if l.startswith("### 6.1"))
    tabs = []; cur = None
    for i, l in enumerate(lines[i61:], i61 + 1):
        if l.startswith("| ") and "|---" not in l:
            c = [x.strip() for x in l.strip().strip("|").split("|")]
            if cur is None or lines[i - 2].strip() == "" or not lines[i - 2].startswith("|"):
                cur = (tuple(c), []); tabs.append(cur)
                continue
            cur[1].append((i, c))
    return lines, i61 + 1, tabs


def find_table(tabs, h0, h1=None, n=None):
    return next(v for k, v in tabs if k[0] == h0 and (h1 is None or k[1] == h1 or k[1].startswith(h1)) and (n is None or len(v) == n))


# ----------------------------------------------------------------------------------------------- git / log / files
def sec_git_log():
    P("\n## G. git / documents / logs / manifests / accept files")
    head = git("rev-parse", "--short", "HEAD")
    P("  HEAD", head, "| dirty conf/code Demo:", repr(git("status", "--porcelain", "conf/code", "Demo")),
      "| pick/tune tracked:", len(git("ls-files", "conf/results/sparse/pick_S2_C2.json", "conf/results/sparse/tune_S2_C2.json", "conf/results/sparse/pick_S2c_C2.json",
                                      "conf/results/sparse/tune_S2c_C2.json", "conf/results/sparse/pick_SV8e_C2.json", "conf/results/sparse/tune_SV8e_C2.json",
                                      "conf/results/sparse/pick_UMi28_C2.json", "conf/results/sparse/tune_UMi28_C2.json", "conf/results/sparse/pick_MIX3_C2.json",
                                      "conf/results/sparse/tune_MIX3_C2.json", "conf/results/sparse/pick_S2_C6.json", "conf/results/sparse/tune_S2_C6.json").splitlines()),
      "| dirty results/sparse:", repr(git("status", "--porcelain", "conf/results/sparse")))
    chk("HEAD == freeze", head, FREEZE, "git")
    P(f"  {FREEZE}: {git('log', '-1', '--format=%h %p %ad %s', '--date=format-local:%Y-%m-%d %H:%M:%S KST', FREEZE)[:140]}")
    P(f"  be0a5540: {git('log', '-1', '--format=%h %p %ad %s', '--date=format-local:%Y-%m-%d %H:%M:%S KST', 'be0a5540')[:100]}")
    f = "conf/results/review_next/NEXT_EXPERIMENTS_SPARSE16e4.md"
    P(f"  doc freeze {FREEZE} -> HEAD diff: {git('diff', FREEZE, 'HEAD', '--', f)!r}")
    dl = git("diff", "HEAD", "--", f).splitlines()
    hunks = [l for l in dl if l.startswith("@@")]; removed = [l[:60] for l in dl if l.startswith("-") and not l.startswith("---")]
    added = [l for l in dl if l.startswith("+") and not l.startswith("+++")]
    txt = git("show", f"{FREEZE}:{f}").splitlines()
    sec6 = next(i + 1 for i, l in enumerate(txt) if l.startswith("## 6."))
    P(f"  working tree vs HEAD: hunks {hunks}; removed {len(removed)} {removed}; added {len(added)}; '## 6.' at line {sec6} of the frozen doc ({len(txt)} lines); "
      f"first added line starts with {added[0][:12]!r}")
    chk("§0-§5 untouched (removed lines)", len(removed), 0, "doc"); chk("added lines", len(added), 165, "doc")
    chk("hunk after §6 header", int(re.search(r"\+(\d+)", hunks[0])[1]) + 3 >= sec6, True, "doc")
    for ff, want in (("docs/EXPERIMENTS.md", (1, 0)), ("conf/DECISIONS.md", (2, 0))):
        ns = git("diff", "--numstat", "--", ff).split()
        chk(f"{ff} numstat", (int(ns[0]), int(ns[1])), want, "git")
    P(f"  commits between 09:04 and 10:22 KST: {git('log', '--since=2026-10-01 09:04:00 +0900', '--until=2026-10-01 10:22:30 +0900', '--format=%h %ci')!r}")
    chk("main commits in the run window", git("log", "--since=2026-10-01 09:04:00 +0900", "--until=2026-10-01 10:22:30 +0900", "--format=%h"), "", "git")
    P(f"  diff {FREEZE}..HEAD -- conf/code Demo: {git('diff', FREEZE, 'HEAD', '--stat', '--', 'conf/code', 'Demo')!r}")
    P(f"  .git/index mtime: {datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(T2, '.git/index')), KST):%m-%d %H:%M:%S} KST (the script's git status / ls-files calls refresh it)")
    # files written in the window (main tree, raw_SP* pruned)
    import subprocess
    out = subprocess.run(["find", ".", "-path", "./conf/raw_SP*", "-prune", "-o", "(", "-newermt", "2026-10-01 09:04:00", "!", "-newermt", "2026-10-01 10:22:10", ")",
                          "(", "-type", "f", "-o", "-type", "l", ")", "-print"], cwd=T2, capture_output=True, text=True).stdout.split()
    out = sorted(x for x in out if not x.startswith("./.git/"))
    P(f"  files/links written in the run window (main tree, raw_SP* pruned, .git excluded): {len(out)}: " + " ".join(os.path.relpath(x, '.') for x in out))
    # run log
    L = open(os.path.join(CONF, "logs/run_sparse16e4.log"), encoding="utf-8").read().splitlines()
    P(f"  logs/run_sparse16e4.log: {len(L)} lines; start {L[0]!r}; last two {L[-2]!r} {L[-1]!r}")
    chk("log start", L[0], f"[sparse 09-30 19:04 CDT] start (git {FREEZE}) rows: all", "log:1")
    chk("log SPARSE_DONE", L[49], "[sparse 09-30 20:22 CDT] SPARSE_DONE ok=6 fail=0", "log:50"); chk("log exit", L[50], "SPARSE_EXIT=0", "log:51")
    chk("start lines", sum(l.count("] start (") for l in L), 1, "log"); chk("ABORT/INVALID/resume/waiting/copied lines", sum(bool(re.search(r"ABORT|INVALID|resume|waiting|copied", l)) for l in L), 0, "log")
    chk("rc=0 lines", sum(" rc=0" in l for l in L), 18, "log"); chk("rc!=0 lines", sum(bool(re.search(r" rc=[1-9]", l)) for l in L), 0, "log")
    return L


def manifest_facts(suf):
    m = json.load(open(os.path.join(RN, f"run_manifest_SP{suf}.json")))
    ml = open(os.path.join(RN, f"run_manifest_SP{suf}.json")).read().splitlines()
    ln = lambda key: next(i + 1 for i, l in enumerate(ml) if l.strip().startswith(f'"{key}"'))
    link = os.readlink(os.path.join(CONF, "results", f"gmm_fits_D2_SP{suf}"))
    return dict(written=m["written"], git=m["git_commit"], n=m["n_raw_files"], ch=m["config_hash"], arms=m["arms"], ck=m["stagec_ckpt_id"], bstar=m["gmm"]["bstar"],
                kK=m["gmm"]["kron_K"], fits=os.path.basename(m["gmm"]["fits_dir"]), cpu=m["versions"]["cpu_count"], link=link,
                lines=dict(written=ln("written"), git=ln("git_commit"), n=ln("n_raw_files"), ch=ln("config_hash"), bstar=ln("bstar"), kK=ln("kron_K"), fits=ln("fits_dir"),
                           ck=ln("stagec_ckpt_id"), arms=ln("arms"), cpu=ln("cpu_count")), pts=m.get("points", []))


# ----------------------------------------------------------------------------------------------- per dataset
def audit_dataset(suf, TAG, cell, prior, pickf, psha, tsha):
    cp = (cell, prior); N = CELLN[cell]
    base, pil, ald, sp = Raw(TAG), Raw("PIL" + suf), Raw("ALD" + suf), Raw("SP" + suf)
    bad = []
    # ---- SP raw integrity (own pass over every chunk)
    pick = json.load(open(os.path.join(CONF, "results/sparse", pickf)))
    tunef = os.path.join(CONF, "results/sparse", pickf.replace("pick_", "tune_"))
    files = sorted(glob.glob(os.path.join(CONF, f"raw_SP{suf}", "D2_*.npz")))
    gits, iters, seeds, mism, ck, fk, nonfin, cov = set(), set(), set(), 0, 0, 0, {a: 0 for a in NEW}, {}
    meta_eq = {k: True for k in ("meta|ntrain", "meta|bstar", "meta|kron_K", "meta|em_sec")}
    bm = base.m(cp)
    llk = f"meta|ll_val|{str(bm['meta|bstar'])}"
    meta_eq[llk] = True
    for f in files:
        with np.load(f) as z:
            snr = re.search(r"_snr(-?\d+)_", f).group(1); e = pick["per_snr"][snr]
            gits.add(str(z["run|git"])); iters.add(int(z["run|iters"])); seeds.add(int(z["run|seed"]))
            mism += json.loads(str(z["meta|sparse"])) != dict(rho_sbl=pick["rho_sbl"], rho_omp=pick["rho_omp"], n_em=e["n_em"], L=e["L"])
            ck += "meta|stagec_ckpt_id" in z.files; fk += sum(k.endswith("|failed") for k in z.files)
            cov.setdefault(snr, []).append((int(z["run|skip"]), int(z["run|n"])))
            for a in NEW:
                nonfin[a] += int((~np.isfinite(np.asarray(z[a + "|blk_err"], float))).sum())
            for k in meta_eq:
                v, w = z[k], bm[k]
                v = v.item() if v.shape == () else v
                if str(v) != str(w) and not (isinstance(w, float) and abs(float(v) - float(w)) <= 1e-9):
                    meta_eq[k] = False
    plan = sorted(set(tuple(sorted(v)) for v in cov.values()))
    plan_ok = len(cov) == 7 and plan == [tuple((40 * k, 40) for k in range(64))]
    mt = [os.path.getmtime(f) for f in files]
    for s in GRID:
        d0, d1 = base.d(cp, s), sp.d(cp, s)
        if GENIE not in d1 or any(not same(d0[GENIE][q], d1[GENIE][q]) for q in KEYS4):
            bad.append(f"{s:+.0f} genie != base")
        if any(len(d1[a]["blk_err"]) != 2560 for a in d1):
            bad.append(f"{s:+.0f} n != 2560")
    if sp.nfiles != 448 or tuple(sp.snrs(cp)) != GRID or sp.holes or sp.fill or sp.cp != [cp]:
        bad.append(f"SP raw files {sp.nfiles} grid {sp.snrs(cp)} holes {sp.holes[:2]} fill {sp.fill[:2]}")
    if gits != {FREEZE} or iters != {16} or seeds != {20260926} or mism or ck or fk or any(nonfin.values()) or not plan_ok or not all(meta_eq.values()):
        bad.append(f"git {gits} iters {iters} seed {seeds} meta|sparse mism {mism} ckpt_id {ck} failed keys {fk} nonfinite {nonfin} plan {plan_ok} meta_eq {meta_eq}")
    if set(sp.arms(cp)) != set(NEW) | {GENIE}:
        bad.append(f"SP arms {sp.arms(cp)}")
    # ---- rule reproduction (registered rule on the tune JSON), sha, memory guard
    sys.path.insert(0, os.path.join(CONF, "code")); import sparse_tune as S, common as C   # noqa: E402  (the frozen rule, 02dafa1c)
    t = json.load(open(tunef))
    grid_ok = t["n"] == 256 and t["grid"] == dict(rho=[1, 2, 4, 8, 16], n_em=list(S.NEMS), L=list(S.LS)) and t["prior"] == prior and t["cell"] == cell
    r = S.per_snr_pick(t["nmse_db"], C.CELLS[cell], N, rhos=t["grid"]["rho"])
    run = lambda p: (p["rho_sbl"], p["rho_omp"], {s: (e["n_em"], e["L"]) for s, e in p["per_snr"].items()})
    rule_ok = run(r) == run(pick)
    edges_ok = all(r["per_snr"][s][k] == pick["per_snr"][s][k] for s in SNRS for k in ("edge_sbl", "edge_omp")) and all(r[k] == pick[k] for k in ("edge_rho_sbl", "edge_rho_omp"))
    need = 192 * (16 * (pick["rho_omp"] ** 2 * N) ** 2 / 1e9 + 0.3)
    psha_m, tsha_m = sha16(os.path.join(CONF, "results/sparse", pickf)), sha16(tunef)
    edge_flags = sum(pick["per_snr"][s][k] for s in SNRS for k in ("edge_sbl", "edge_omp"))
    ls_pts = [s for s in SNRS if pick["per_snr"][s]["L"] == N]
    P(f"\n  [{suf} = raw_SP{suf}; base raw_{TAG}, PIL raw_PIL{suf}, ALD raw_ALD{suf}] files {sp.nfiles}; run|git {sorted(gits)} iters {sorted(iters)} seed {sorted(seeds)}; "
      f"chunk plan {{(40k,40)}} x 7 = {plan_ok}; meta|sparse mismatching chunks {mism}; stagec_ckpt_id keys {ck}; '|failed' keys {fk}; non-finite blk_err (16 it) {nonfin}; "
      f"meta == base {meta_eq}; genie 4 keys == base 7/7, n 2560: {'OK' if not bad else bad}")
    P(f"    chunk mtime first {cdt(min(mt))} last {cdt(max(mt))} CDT; pick sha {psha_m} (§5 {psha}) tune sha {tsha_m} (§5 {tsha}); tune n/grid/prior/cell v2b {grid_ok}; "
      f"rule reproduced (rho, per-SNR n_em/L) {rule_ok}; edge flags reproduced {edges_ok}; memory need {need:.0f} GB; pick rho_sbl {pick['rho_sbl']} rho_omp {pick['rho_omp']} "
      f"edge_rho {pick['edge_rho_sbl']}/{pick['edge_rho_omp']}; per-SNR edge flags true {edge_flags}/14; n_em {[pick['per_snr'][s]['n_em'] for s in SNRS]} L {[pick['per_snr'][s]['L'] for s in SNRS]}; "
      f"L = N ({N}) at {ls_pts}")
    chk("pick sha", psha_m, psha, suf); chk("tune sha", tsha_m, tsha, suf); chk("rule reproduced", rule_ok, True, suf); chk("tune v2b", grid_ok, True, suf)
    chk("integrity", bad, [], suf)
    # ---- merged data (V1 / b* / genie / 12 base arms from base, PIL, ALD, 3 new arms from SP), R0-pilot@1 = trajectory cut at iteration 1
    D = merged(cp, (base, {a: a for a in (V1, BSTAR, GENIE, "M-ours-bstar-scalar", "M-ours-gmm32", "R0-pilot", "R1-turbo", "R2-ours-G", "R3-bigamp", "R4-llr", "R4-scvamp",
                                              "M-ours-dscore-C-V0", "M-ours-dscore-C-V4", "M-ours-dscore-C-V4b")}),
               (pil, {"V1-pilot": "V1-pilot", "bstar-pilot": "bstar-pilot"}), (ald, {"ALD-pilot": "ALD-pilot", "ALDv-pilot": "ALDv-pilot"}), (sp, {a: a for a in NEW}))
    for s in D:
        D[s]["R0-pilot@1"] = {q: np.asarray(a)[:, :1] for q, a in D[s]["R0-pilot"].items() if getattr(a, "ndim", 0) == 2}
    fv3, fg3 = fails(D[-3.0], V1), fails(D[-3.0], GENIE)
    vg = fg3.sum() >= fv3.sum()
    res = {}
    for x in X16:
        t = table_b(D, x, V1)
        fx = fails(D[-3.0], x); F = int(fx.sum()); absgap = F - int(fv3.sum()); bl = fx.mean()
        if vg or not (0.005 <= bl <= 0.9) or F <= fg3.sum():
            defined, R, lo, hi = False, np.nan, np.nan, np.nan
        else:
            R, lo, hi, nn, _ = recovery([(fx, fv3, fg3)]); defined = nn <= 0.05 * 2000
        cols2 = [tuple(fails(D[s], arm) for arm in (x, V1, GENIE)) for s in t["cand"]]
        if t["cand"] and sum(c[2].sum() for c in cols2) < sum(c[1].sum() for c in cols2):
            R2, lo2, hi2, nn2, _ = recovery(cols2); r2 = f"{R2:.3f} [{lo2:.3f}, {hi2:.3f}] over {len(t['cand'])} point(s)" + (f" ({nn2} undefined)" if nn2 else "")
        else:
            r2 = "undefined"
        g = gap(D, x, V1)
        res[x] = dict(t=t, lab=t["lab"], F=F, absgap=absgap, defined=defined, R=R, lo=lo, hi=hi, r1=(f"{R:.3f} [{lo:.3f}, {hi:.3f}]" if defined else "undefined"), r2=r2,
                      r2doc=(f"{R2:.3f} [{lo2:.3f}, {hi2:.3f}]" + (f" ({len(t['cand'])} 점)" if len(t["cand"]) != 3 else "")) if r2 != "undefined" else "undefined",
                      gap=g, gaptxt=gap_text(g, x))
        if x in NEW:
            P(f"      {x:<10} {dp_str(t['cand']):<10} " + " · ".join(f"{a}:{b} (p {p:.2g})" for a, b, p in t["res"]) + f"  pooled {t['A']}:{t['B']} (p {t['pp']:.2g}) -> {t['lab']} "
              f"{t['wy']}/{len(t['cand'])} (powered {t['powered']}); F -3 dB {F}; abs gap {absgap}; R_X {res[x]['r1']}; R_X dp {r2}; gap {res[x]['gaptxt']}")
    kB = sum(1 for x in BL if res[x]["lab"] == "(i)"); mB = sum(1 for x in BL if res[x]["lab"] == "(ii)")
    k16 = kB + (res[BSTAR]["lab"] == "(i)"); m16 = mB + (res[BSTAR]["lab"] == "(ii)")
    order = sorted(X16, key=lambda x: (res[x]["F"], x)); xs = order[0]
    fr = {a: [int(fails(D[s], a).sum()) for s in GRID] for a in D[-3.0]}
    med = {a: [f"{np.nanmedian(np.asarray(D[s][a]['nmse'])[:, -1]):.2e}" for s in GRID] for a in (V1, BSTAR) + BL if "nmse" in D[-3.0][a]}
    nm1 = {}
    for a, key in (("SBL-pilot", "nmse_sbl_db"), ("OMP-pilot", "nmse_omp_db")):
        nm1[a] = []
        for s, ss in zip(GRID, SNRS):
            v = np.asarray(D[s][a]["nmse"], float)[:, 0]
            nm1[a].append((10 * np.log10(v.mean()), pick["per_snr"][ss][key], bool(np.isfinite(v).all()), v.size))
    P(f"    -3 dB genie {int(fg3.sum())} V1 {int(fv3.sum())} guard {'FIRED' if vg else 'not fired'}; k𝔅(15) {kB} m𝔅 {mB} undecided {15 - kB - mB}; 16: (i) {k16} (ii) {m16} undecided {16 - k16 - m16}; "
          f"b* {res[BSTAR]['lab']}; X* {xs} (F {res[xs]['F']}; runner-up {order[1]} F {res[order[1]]['F']}); R_X* {res[xs]['r1']}; file-condition (recomputed b*) "
          f"{'MET' if res[BSTAR]['lab'] == '(i)' and kB == 15 and mB == 0 and res[xs]['defined'] and res[xs]['lo'] > 0 else 'NOT met'}")
    return dict(res=res, kB=kB, mB=mB, k16=k16, m16=m16, xs=xs, vg=vg, fails=fr, med=med, nm1=nm1, mt=(min(mt), max(mt)), pick=pick, ls_pts=ls_pts, edge_flags=edge_flags,
                need=need, N=N, D=D)


# ----------------------------------------------------------------------------------------------- main
def main():
    P(f"# sparse_recompute.py -- record audit SPARSE16e4 (Fable 5.1); raw npz / pick+tune JSON / manifests / accept / logs / git only; "
      f"git HEAD {git('rev-parse', '--short', 'HEAD')}; now {datetime.datetime.now(CDT):%Y-%m-%d %H:%M} CDT = {datetime.datetime.now(KST):%H:%M} KST")
    P(f"  𝔅 (15) = {BL}")
    L = sec_git_log()
    lines, i61, tabs = doc_tables()
    P(f"  doc parsed: §6.1 @ line {i61}; tables {[(k[0], len(v)) for k, v in tabs]}")
    # ---- script line numbers quoted by §6.1 (21, 34-39, 41-43, 47-48, 60-62)
    sh = open(os.path.join(CONF, "code/run_sparse16e4.sh")).read().splitlines()
    chk("script line 21 = NR16 row with PSHA", "NR16B16e4 NR16 C6 S2 NR16B16e4 kron 4096 63.1751571838059 results/sparse/pick_S2_C6.json 3958df589e385522" in sh[20], True, "sh")
    chk("script 34-39 = gate block", sh[33].strip().startswith("if [ ! -f \"$SP\" ] && [ \"$PSHA\" = \"-\" ]") and sh[38].strip() == "fi", True, "sh")
    chk("script 41 = sha check", "sha256 != §5" in sh[40], True, "sh"); chk("script 42-43 = tracked+clean", "not tracked+clean" in sh[42], True, "sh")
    chk("script 47-48 = prior/cell + v2b asserts", "assert t[\"prior\"] == prior" in sh[46] and "assert t[\"n\"] == 256" in sh[47], True, "sh")
    chk("script CUDA hidden", "export CUDA_VISIBLE_DEVICES=" in sh[9], True, "sh")
    # ---- datasets
    P("\n## 1. 6 datasets: SP raw integrity, rule reproduction, 16 x table B (3 new + 13 cited), R_X, X*, sentence")
    R = {}
    for suf, TAG, cell, prior, pickf, psha, tsha, *_ in ROWS:
        R[suf] = audit_dataset(suf, TAG, cell, prior, pickf, psha, tsha)
    # ---- vs pairB_SP files
    P("\n## 2. own numbers vs pairB_SP<suf>.txt (16 X blocks x 9 fields, SUMMARY-B, 16-summary, labels, X*, condition, failure rows, NMSE rows, header)")
    PB = {}
    st_hdr = {l.split(": ", 1)[0][2:]: l.split(": ", 1)[1].strip() for l in open(os.path.join(RN, "NEXT_EXPERIMENTS_STATIC16e4.md"), encoding="utf-8") if l.startswith("- ") and "chunks-sha" in l}
    stname = {"B16e4k": "D2 C2 (헤드라인)", "D3": "D3", "SV": "SV8e", "U28": "UMi28", "MX": "MIX3 (보고 전용)", "NR16": "D2 C6"}
    for suf, TAG, cell, prior, pickf, psha, tsha, dname, sname, b0, noni0 in ROWS:
        r = R[suf]; res = r["res"]; pb = parse_pairb(suf); PB[suf] = pb
        chk("header git", pb["git_hdr"], FREEZE, f"pairB_SP{suf}"); chk("integrity", pb["integrity"], "OK", f"pairB_SP{suf}")
        prov = pb["prov"].replace(f" extra0={FREEZE}", "")
        chk("provenance = STATIC §6.1 header line", prov.replace("base=", "base=").replace(" pil=", " pil=").replace(" ald=", " ald="), st_hdr[stname[suf]], f"pairB_SP{suf}")
        chk("extra0 run|git in header", f"extra0={FREEZE}" in pb["prov"], True, f"pairB_SP{suf}")
        for x in X16:
            t = res[x]["t"]; px = pb["X"][x]
            chk(f"{x} decision points", dp_str(t["cand"]), px["dp"], f"pairB_SP{suf}")
            chk(f"{x} per-point a:b", " · ".join(f"{a}:{b}" for a, b, p in t["res"]), px["pts"], f"pairB_SP{suf}")
            pm = [f"{p:.2g}" for a, b, p in t["res"]] + [f"{t['pp']:.2g}"]
            chk(f"{x} per-point + pooled p (both sides > 1e-300; smaller = underflow, both ~0)", [a if float(a) > 1e-300 and float(b) > 1e-300 else "~0" for a, b in zip(pm, px["pps"])],
                [b if float(a) > 1e-300 and float(b) > 1e-300 else "~0" for a, b in zip(pm, px["pps"])], f"pairB_SP{suf}")
            chk(f"{x} pooled", f"{t['A']}:{t['B']}", px["pooled"], f"pairB_SP{suf}")
            chk(f"{x} label", t["lab"], px["lab"], f"pairB_SP{suf}"); chk(f"{x} powered", t["powered"], px["powered"], f"pairB_SP{suf}")
            chk(f"{x} wy/n", (str(t["wy"]), str(len(t["cand"]))), (px["wy"], px["npt"]), f"pairB_SP{suf}")
            chk(f"{x} abs gap", res[x]["absgap"], px["abs"], f"pairB_SP{suf}"); chk(f"{x} n", 2560, px["n"], f"pairB_SP{suf}")
            chk(f"{x} R_X primary", res[x]["r1"], re.sub(r"^undefined.*", "undefined", px["r1"]), f"pairB_SP{suf}")
            chk(f"{x} R_X decision points", res[x]["r2"], re.sub(r"^undefined.*", "undefined", px["r2"]), f"pairB_SP{suf}")
            g = res[x]["gap"]; fg = px["gap"]
            if g["text"].startswith("n/a") or "never" in g["text"] or "already" in g["text"]:
                chk(f"{x} SNR@0.1 gap text", res[x]["gaptxt"], fg, f"pairB_SP{suf}")
            else:
                m = re.match(r"([+-]\d+\.\d+) dB  \[90% paired bootstrap ([+-]\d+\.\d+), ([+-]\d+\.\d+); censored replicates (\d+)%\]", fg)
                chk(f"{x} SNR@0.1 gap", res[x]["gaptxt"], f"{m[1]} [{m[2]}, {m[3]}]" if m else fg, f"pairB_SP{suf}")
                if x in NEW:
                    chk(f"{x} censored replicates 0% (doc omits the field)", m[4] if m else None, "0", f"pairB_SP{suf}")
                else:
                    cm = re.search(r"censored (\d+)%", g["text"])
                    chk(f"{x} censored replicates (cited arm; own bootstrap)", cm[1] if cm else "0", m[4] if m else None, f"pairB_SP{suf}")
        chk("SUMMARY-B", pb["summB"], f"SUMMARY-B (baselines without b*, 15): (i) {r['kB']}, (ii) {r['mB']}, not decided {15 - r['kB'] - r['mB']}; b* -> V1 {res[BSTAR]['lab']}", f"pairB_SP{suf}")
        chk("SUMMARY 16", pb["summ16"], f"SUMMARY registered baselines 16 (b* + 𝔅 15): (i) {r['k16']}, (ii) {r['m16']}, not decided {16 - r['k16'] - r['m16']}", f"pairB_SP{suf}")
        chk("labels line", pb["labels"], {x: res[x]["lab"] for x in X16}, f"pairB_SP{suf}")
        xs = r["xs"]
        chk("X* line", pb["xstar"], f"X* (fewest -3 dB failures, ties by name) = {xs} (F={res[xs]['F']}); R_X* -3 dB = " + (f"{res[xs]['R']:.3f} [90% {res[xs]['lo']:.3f}, {res[xs]['hi']:.3f}]" if res[xs]["defined"] else "undefined (out of range)"), f"pairB_SP{suf}")
        fcond = res[BSTAR]["lab"] == "(i)" and r["kB"] == 15 and r["mB"] == 0 and res[xs]["defined"] and res[xs]["lo"] > 0
        chk("condition line", pb["cond"], "MET" if fcond else "NOT met", f"pairB_SP{suf}")
        for a, row in pb["fails"].items():
            if a != "_line":
                chk(f"failure row {a}", r["fails"].get(a), row, f"pairB_SP{suf}")
        chk("failure rows count", len([a for a in pb["fails"] if a != "_line"]), 22, f"pairB_SP{suf}")
        for a, row in pb["nmse"].items():
            if a != "_line":
                chk(f"median NMSE@16 row {a}", r["med"].get(a), row, f"pairB_SP{suf}")
        chk("NMSE rows count", len([a for a in pb["nmse"] if a != "_line"]), 17, f"pairB_SP{suf}")
        # --expect (STATIC labels) and the 13-arm block identity with pairB_ST
        for x in X16[:13]:
            chk(f"{x} = STATIC label", res[x]["lab"], "(iv)" if (x in noni0 or (x == BSTAR and b0 == "(iv)")) else "(i)", f"pairB_SP{suf} --expect")
        a0 = 5 if suf == "B16e4k" else 4
        spl = pb["lines"][a0 - 1:a0 + 90]; stl = open(os.path.join(RN, f"pairB_ST{TAG}.txt"), encoding="utf-8").read().splitlines()[a0 - 1:a0 + 90]
        chk("13-arm block (91 lines) byte-identical to pairB_ST", spl == stl and len(spl) == 91 and spl[0].startswith("M-ours-bstar ->") and spl[-1].strip().startswith("R_X decision"), True, f"pairB_SP{suf}")
        P(f"  pairB_SP{suf}: compared; header time {pb['hdr_time']}; new-arm blocks at lines {[pb['blockline'][x] for x in NEW]}; SUMMARY-B line {pb['summB_line']}, 16-summary {pb['summ16_line']}, "
          f"X* {pb['xstar_line']}, condition {pb['cond_line']}; fails rows genie/V1/b* at {[pb['fails']['_line'][a] for a in (GENIE, V1, BSTAR)]}, new at {[pb['fails']['_line'][a] for a in NEW]}; "
          f"NMSE rows new at {[pb['nmse']['_line'][a] for a in NEW]}")
    # ---- manifests / accept / runner logs / links
    P("\n## 3. manifests, accept files, runner logs, fits links, log line quotes")
    MF = {}
    rowlog = {"B16e4k": (2, 5, 6, 7, 8, 9, "19:13", "19:13", "19:14", "1029"), "D3": (10, 13, 14, 15, 16, 17, "19:23", "19:23", "19:23", "1028"), "SV": (18, 21, 22, 23, 24, 25, "19:30", "19:30", "19:30", "1028"),
              "U28": (26, 29, 30, 31, 32, 33, "19:35", "19:35", "19:35", "1028"), "MX": (34, 37, 38, 39, 40, 41, "19:43", "19:43", "19:44", "1028"), "NR16": (42, 45, 46, 47, 48, 49, "20:21", "20:21", "20:22", "1028")}
    mins = {}
    for suf, TAG, cell, prior, pickf, psha, tsha, *_ in ROWS:
        mf = manifest_facts(suf); MF[suf] = mf; r = R[suf]
        chk("manifest git", mf["git"], FREEZE, f"manifest SP{suf}"); chk("manifest n_raw_files", mf["n"], 448, f"manifest SP{suf}")
        chk("manifest arms", mf["arms"], ["OMP-pilot", "R5-genie", "SBL-loop", "SBL-pilot"], f"manifest SP{suf}"); chk("manifest stagec_ckpt_id", mf["ck"], "(none)", f"manifest SP{suf}")
        chk("manifest cpu_count", mf["cpu"], 192, f"manifest SP{suf}"); chk("manifest config_hash", mf["ch"], "a936007de9918754" if suf == "NR16" else "ba9bc0a2cb5fbb84", f"manifest SP{suf}")
        chk("fits link target", mf["link"], f"gmm_fits_D2_{TAG}", f"manifest SP{suf}"); chk("manifest fits_dir", mf["fits"], f"gmm_fits_D2_SP{suf}", f"manifest SP{suf}")
        w = datetime.datetime.strptime(mf["written"][:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=KST)
        chk("manifest written >= last chunk", w.timestamp() >= r["mt"][1], True, f"manifest SP{suf}")
        chk("manifest written (KST) -> CDT = log run_manifest time", w.astimezone(CDT).strftime("%H:%M"), rowlog[suf][6], f"manifest SP{suf}")
        chk("manifest line numbers (written/git/n/config_hash)", (mf["lines"]["written"], mf["lines"]["git"], mf["lines"]["n"], mf["lines"]["ch"]), (3, 4, 8, 9), f"manifest SP{suf}")
        off = 1 if suf in ("SV", "U28", "MX") else 0
        chk("manifest line numbers (bstar/kron_K/fits_dir/stagec_ckpt_id/arms)", (mf["lines"]["bstar"], mf["lines"]["kK"], mf["lines"]["fits"], mf["lines"]["ck"], mf["lines"]["arms"]),
            (94 + off, 95 + off, 98 + off, 112 + off, 113 + off), f"manifest SP{suf}")
        acc = open(os.path.join(RN, f"SP{suf}_accept.txt"), encoding="utf-8").read()
        chk("accept file", acc, f"ACCEPT: OK -- SP{suf}\n", f"SP{suf}_accept")
        rl = open(os.path.join(CONF, f"logs/run_D2_SP{suf}.log"), encoding="utf-8", errors="replace").read().splitlines()
        m = re.search(r"\[run\] finished in ([\d.]+) min", rl[451]); mins[suf] = m[1] if m else None
        chk("runner log 452 lines, last = finished", (len(rl), bool(m)), (452, True), f"run_D2_SP{suf}")
        chk("runner done lines", sum("/448 done" in l for l in rl), 448, f"run_D2_SP{suf}"); chk("runner Traceback/Error", sum(bool(re.search(r"Traceback|Error", l)) for l in rl), 0, f"run_D2_SP{suf}")
        i0, i1, i2, i3, i4, i5, tm, ta, tp, avail = rowlog[suf]
        chk("log sha line", L[i0 - 1], f"[sparse] results/sparse/{pickf} sha256[:16]={psha} tune sha256[:16]={tsha} rule-reproduced=True (rho, per-SNR n_em / L) memory need ~{r['need']:.0f} GB, available {avail} GB", f"log:{i0}")
        chk("log manifest rc", L[i1 - 1], f"[sparse 09-30 {tm} CDT] {TAG} run_manifest rc=0", f"log:{i1}")
        chk("log acceptance", L[i2 - 1], f"[sparse 09-30 {ta} CDT] {TAG} acceptance rc=0 (ACCEPT: OK -- SP{suf})", f"log:{i2}")
        chk("log raised", L[i3 - 1], "[sparse] raised trials per new arm (= failures, 01_RULES §4; report only, §6): {'SBL-loop': 0, 'SBL-pilot': 0, 'OMP-pilot': 0}", f"log:{i3}")
        chk("log meta|sparse", L[i4 - 1], f"[sparse] meta|sparse check raw_SP{suf}: 0 mismatching chunks", f"log:{i4}")
        chk("log pair_baselines", L[i5 - 1], f"[sparse 09-30 {tp} CDT] {TAG} pair_baselines rc=0 ({PB[suf]['summB'][:110]})", f"log:{i5}")
        chk("log manifest json line git/tag/n/arms", json.loads(L[i0])["git_commit"] == FREEZE and json.loads(L[i0])["result_tag"] == f"SP{suf}" and json.loads(L[i0])["n_raw_files"] == 448, True, f"log:{i0 + 1}")
        chk("pairB header time = log pair_baselines time", PB[suf]["hdr_time"].startswith(f"2026-09-30 {tp}") or PB[suf]["hdr_time"].startswith(f"2026-09-30 {ta}"), True, f"pairB_SP{suf}")
        P(f"  SP{suf}: manifest written {mf['written']} git {mf['git']} n {mf['n']} ch {mf['ch']} bstar {mf['bstar']} kron_K {mf['kK']} link -> {mf['link']}; runner {mins[suf]} min; "
          f"chunks {cdt(r['mt'][0])}..{cdt(r['mt'][1])} CDT; accept {acc.strip()!r}")
    chk("runner minutes", [mins[s] for s in ("B16e4k", "D3", "SV", "U28", "MX", "NR16")], ["9.5", "9.2", "6.2", "4.8", "7.6", "37.6"], "runner")
    # ---- doc §6.1 tables
    P("\n## 4. doc §6.1 tables vs own numbers")
    rowtab = find_table(tabs, "행 (태그)")
    for (ln, c), (suf, TAG, cell, prior, pickf, psha, tsha, dname, *_) in zip(rowtab, ROWS):
        r = R[suf]; mf = MF[suf]
        chk("row name", c[0], f"{dname} (SP{suf})", f"doc:{ln}")
        chk("row sha/rule/memory", all(s in c[1] for s in (f"`{psha}`", f"`{tsha}`", "True", f"~{r['need']:.0f} GB")), True, f"doc:{ln}")
        chk("row runner min + chunk mtimes", c[2], f"{mins[suf]} min · {cdt(r['mt'][0])[6:]}–{cdt(r['mt'][1])[6:]}", f"doc:{ln}")
        chk("row manifest written", f"{mf['written'][5:7]}-{mf['written'][8:10]} {mf['written'][11:19]} KST".replace("10-01 ", "10-01 ") in c[3] or mf["written"][11:19] + " KST" in c[3], True, f"doc:{ln}")
        chk("row accept text", f"ACCEPT: OK -- SP{suf}" in c[3], True, f"doc:{ln}")
        chk("row raised", "0" in c[4] and "SBL-loop': 0" in c[4] if suf == "B16e4k" else c[4].startswith("0 · 0 · 0"), True, f"doc:{ln}")
        chk("row meta|sparse", c[5].startswith("0"), True, f"doc:{ln}")
    tb = find_table(tabs, "데이터셋", "X")
    chk("table B rows", len(tb), 18, "doc")
    for ln, c in tb:
        suf = next(s for s, *_r, dn, sn, b0, n0 in ROWS if dn == c[0] for s in [s]); r = R[suf]; x = c[1]; t = r["res"][x]["t"]; rx = r["res"][x]
        a0 = PB[suf]["blockline"][x]
        chk("dp", c[2], dp_str(t["cand"]), f"doc:{ln} {x}"); chk("per point", c[3], " · ".join(f"{a}:{b}" for a, b, p in t["res"]), f"doc:{ln} {x}")
        chk("pooled", c[4], f"{t['A']}:{t['B']}", f"doc:{ln} {x}")
        lab = f"(i) {t['wy']}/{len(t['cand'])}" if t["lab"] == "(i)" else f"(iv) (POWERED=False, 판정점 {len(t['cand'])}; V1 쪽 적음 {t['wy']}/{len(t['cand'])})" if t["lab"] == "(iv)" else t["lab"]
        chk("label", c[5], lab, f"doc:{ln} {x}")
        chk("R_X -3", c[6], rx["r1"], f"doc:{ln} {x}"); chk("R_X dp", c[7], rx["r2doc"], f"doc:{ln} {x}"); chk("abs gap", c[8], str(rx["absgap"]), f"doc:{ln} {x}")
        chk("SNR@0.1 gap", c[9], rx["gaptxt"], f"doc:{ln} {x}")
        chk("source lines", c[10], (f"SP{suf}:" if x == "SBL-loop" else ":") + f"{a0}–{a0 + 6}", f"doc:{ln} {x}")
    st = find_table(tabs, "데이터셋", "원 b")
    for (ln, c), (suf, TAG, cell, prior, pickf, psha, tsha, dname, sname, b0, noni0) in zip(st, ROWS):
        r = R[suf]; res = r["res"]; xs = r["xs"]
        chk("name", c[0], sname, f"doc:{ln}"); chk("original b*", c[1], b0, f"doc:{ln}")
        chk("SUMMARY-B counts", c[2], f"{r['kB']} · {r['mB']} · {15 - r['kB'] - r['mB']}", f"doc:{ln}"); chk("16 counts", c[3], f"{r['k16']} · {r['m16']} · {16 - r['k16'] - r['m16']}", f"doc:{ln}")
        noni = ", ".join(f"{'b*' if x == BSTAR else x} {res[x]['lab']}" for x in X16 if res[x]["lab"] != "(i)") or "—"
        chk("non-(i) X", c[4], noni, f"doc:{ln}"); chk("X* / R_X*", c[5], f"{xs} ({res[xs]['F']}) · {res[xs]['r1']}", f"doc:{ln}")
        sent = b0 == "(i)" and r["kB"] == 15 and r["mB"] == 0 and res[xs]["defined"] and res[xs]["lo"] > 0
        chk("sentence (registered: original b*)", c[6], "MET" if sent else "NOT met", f"doc:{ln}"); r["sent"] = sent
        chk("sentence (file: recomputed b*) same", PB[suf]["cond"], "MET" if sent else "NOT met", f"doc:{ln}")
    # (b) -3 dB failures
    fb = find_table(tabs, "데이터셋", "R5-genie")
    for (ln, c), (suf, *_r, dname, sn, b0, n0) in zip(fb, ROWS):
        chk("(b) row", c, [dname] + [str(R[suf]["fails"][a][0]) for a in (GENIE, V1, BSTAR) + NEW], f"doc:{ln}")
    # (c) median NMSE@16
    fc = find_table(tabs, "데이터셋", "arm", 18)
    for ln, c in fc:
        suf = next(s for s, *_r, dn, sn, b0, n0 in ROWS if dn == c[0]); chk("(c) row", c[2:], R[suf]["med"][c[1]], f"doc:{ln} {c[1]}")
    # (d) 10 log10 ratio of the printed medians
    fd = find_table(tabs, "데이터셋", "−3 dB", 6)
    for (ln, c), (suf, *_r, dname, sn, b0, n0) in zip(fd, ROWS):
        md = R[suf]["med"]; mine = [f"{10 * np.log10(float(a) / float(b)):.2f}" for a, b in zip(md["SBL-loop"], md["SBL-pilot"])]
        chk("(d) row", c, [dname] + mine, f"doc:{ln}")
        raw_ratio = [10 * np.log10(np.nanmedian(np.asarray(R[suf]['D'][s]['SBL-loop']['nmse'])[:, -1]) / np.nanmedian(np.asarray(R[suf]['D'][s]['SBL-pilot']['nmse'])[:, -1])) for s in GRID]
        P(f"  (d) {dname}: from printed medians {mine}; from raw medians {[f'{v:.2f}' for v in raw_ratio]} (max |diff| {max(abs(float(a) - b) for a, b in zip(mine, raw_ratio)):.3f} dB)")
    # (e) test NMSE@1 vs dev
    fe = find_table(tabs, "데이터셋", "arm", 12)
    for ln, c in fe:
        suf = next(s for s, *_r, dn, sn, b0, n0 in ROWS if dn == c[0]); nm = R[suf]["nm1"][c[1]]
        chk("(e) row", c[2:], [f"{t:.2f} ({t - d:+.2f})" for t, d, fin, n in nm], f"doc:{ln} {c[1]}"); chk("(e) finite, n", all(fin and n == 2560 for t, d, fin, n in nm), True, f"doc:{ln} {c[1]}")
    # predictions
    pr = find_table(tabs, "#")
    chk("prediction rows", [c[0] for ln, c in pr], ["1", "2 (D3)", "2 (C6)", "3", "4", "5", "6", "7"], "doc pred")
    lab = lambda suf, x: R[suf]["res"][x]["lab"]
    p1 = all(lab("B16e4k", x) == "(i)" for x in NEW); p2d3 = all(lab("D3", x) == "(i)" for x in NEW); p2c6 = all(lab("NR16", x) == "(i)" for x in NEW)
    p3 = all(lab(s, "OMP-pilot") == "(i)" for s in ("U28", "MX", "SV")); n4 = sum(lab(s, "SBL-loop") != "(i)" for s in ("U28", "MX", "SV")); p4 = n4 >= 1
    new18 = [lab(s, x) for s in R for x in NEW]; p5 = new18.count("(ii)") <= 1
    for (ln, c), want in zip(pr, (p1, p2d3, p2c6, p3, p4, p5, None, None)):
        chk("prediction score", c[3], "✓" if want else "✗" if want is not None else c[3], f"doc:{ln} pred {c[0]}")
    P(f"  predictions: 1 {p1}, 2(D3) {p2d3}, 2(C6) {p2c6}, 3 {p3}, 4 {p4} (non-(i) SBL-loop datasets among U28/MX/SV = {n4}), 5 {p5} ((ii) = {new18.count('(ii)')}); 6 not scored, 7 not an item")
    chk("sum line", "합계: 적중 6, 빗나감 0 (채점 안 함 1 — 6)." in "\n".join(lines[i61:]), sum([p1, p2d3, p2c6, p3, p4, p5]) == 6, "doc")
    # aggregates
    cnt = {k: new18.count(k) for k in ("(i)", "(ii)", "(iii)", "(iv)")}
    iv = [(s, x) for s in R for x in NEW if lab(s, x) == "(iv)"]
    sent = [s for s in R if R[s]["sent"]]
    P(f"  new 18 labels: {cnt}; (iv) at {iv}; sentence MET at {sent}; main label D2 C2 {'(A)' if p1 else '(B)'}")
    body = "\n".join(lines[i61 - 1:])
    chk("aggregate sentence", "새 18 라벨 중 (i) 17, (iv) 1 (SV8e SBL-loop), (ii) 0" in body, cnt == {"(i)": 17, "(ii)": 0, "(iii)": 0, "(iv)": 1} and iv == [("SV", "SBL-loop")], "doc")
    chk("sentence 4/6 list", "**D2 C2·D3·UMi28·MIX3 충족**" in body, sent == ["B16e4k", "D3", "U28", "MX"], "doc")
    chk("main label (A) with A1 pooled", "(A1 = `SBL-loop → V1` (i) 588:72)" in body, p1 and f"{R['B16e4k']['res']['SBL-loop']['t']['A']}:{R['B16e4k']['res']['SBL-loop']['t']['B']}" == "588:72", "doc")
    # raw paragraph / caveats / C6 pick
    chk("raw paragraph", "`run|git` 2688/2688 이 02dafa1c; `meta|sparse` 가 그 SNR 의 pick 값과 다른 청크 0; `meta|stagec_ckpt_id` 키 0; `<arm>|failed` 키 0; 새 3 arm `blk_err` 비유한 값 0 (16 반복 전부)" in body, True, "doc")
    c6 = R["NR16"]["pick"]
    chk("C6 pick sentence", f"ρ_SBL {c6['rho_sbl']} (끝), ρ_OMP {c6['rho_omp']} (끝); SNR −3..+15 dB 의 n_em {'·'.join(str(c6['per_snr'][s]['n_em']) for s in SNRS)}, L {'·'.join(str(c6['per_snr'][s]['L']) for s in SNRS)}" in body,
        c6["edge_rho_sbl"] and c6["edge_rho_omp"], "doc")
    chk("edge flags all false (C2 70 + C6 14)", sum(R[s]["edge_flags"] for s in R), 0, "doc")
    chk("edge_rho_sbl pattern", [R[s]["pick"]["edge_rho_sbl"] for s in ("B16e4k", "D3", "SV", "U28", "MX", "NR16")], [True, True, True, False, True, True], "doc")
    chk("edge_rho_omp all", [R[s]["pick"]["edge_rho_omp"] for s in R], [True] * 6, "doc")
    ls = {s: R[s]["ls_pts"] for s in R}
    chk("OMP = LS points", ls, {"B16e4k": ["15"], "D3": [], "SV": ["3", "6", "9", "12", "15"], "U28": ["3", "6", "9", "12", "15"], "MX": ["6", "9", "12", "15"], "NR16": []}, "doc")
    chk("OMP = LS count 15", sum(len(v) for v in ls.values()), 15, "doc")
    dpo = {s: [f"{x:+.0f}" for x in R[s]["res"]["OMP-pilot"]["t"]["cand"]] for s in R}
    chk("OMP = LS on OMP decision points", {s: [p for p in dpo[s] if p.lstrip("+") in ls[s]] for s in R}, {"B16e4k": [], "D3": [], "SV": ["+3"], "U28": ["+6", "+9", "+12"], "MX": ["+6", "+9", "+12"], "NR16": []}, "doc")
    chk("C6 L <= 12 < 64", max(c6["per_snr"][s]["L"] for s in SNRS), 12, "doc")
    # durations
    chk("script wall", "19:04–20:22 CDT (1 h 18 min)" in body, True, "doc")
    # ---- EXPERIMENTS row / DECISIONS line
    P("\n## 5. EXPERIMENTS row and DECISIONS line")
    er = [l for l in open(os.path.join(T2, "docs/EXPERIMENTS.md"), encoding="utf-8") if "run_sparse16e4.sh" in l][-1]
    dl = [l for l in open(os.path.join(CONF, "DECISIONS.md"), encoding="utf-8") if "SPARSE16e4 결과 기록" in l][-1]
    for name, s, want in (("EXP time", "| 2026-10-01 09:04 ~ 10:22 KST (텍사스 09-30 19:04 ~ 20:22 CDT) |", True), ("EXP freeze", "병합 02dafa1c", True), ("EXP git col", "| 02dafa1c | 없음 (CPU) |", True),
                          ("EXP core", "6/6 ACCEPT OK, `meta\\|sparse` 불일치 0, 새 arm 예외 시행 0, `--expect` 드리프트 없음", True),
                          ("EXP labels", "새 18 라벨 (i) 17·(iv) 1 (SV8e SBL-loop)·(ii) 0", cnt == {"(i)": 17, "(ii)": 0, "(iii)": 0, "(iv)": 1}),
                          ("EXP sentence", "4/6 (D2 C2·D3·UMi28·MIX3; C6·SV8e 는 §1 에서 불가)", sent == ["B16e4k", "D3", "U28", "MX"]),
                          ("EXP runner", "runner C2 4.8–9.5 min·C6 37.6 min", sorted(float(mins[s]) for s in ("B16e4k", "D3", "SV", "U28", "MX")) [0] == 4.8 and max(float(mins[s]) for s in ("B16e4k", "D3", "SV", "U28", "MX")) == 9.5 and mins["NR16"] == "37.6"),
                          ("EXP LS", "OMP = LS 점 15 개 (§2, C6 없음)", True), ("EXP pred", "§3 예측 6/6 적중 (예측 6 보고 전용·채점 안 함)", True), ("EXP main", "(A) \"V1 이 희소 baseline 3 개(SBL-loop, SBL-pilot, OMP-pilot) 전부보다 적게 실패\"", p1)):
        chk(name, s in er, want, "EXPERIMENTS")
    for name, s, want in (("DEC time", "[2026-10-01 10:30 KST] SPARSE16e4 결과 기록 (Opus 5.5; 텍사스 09-30 20:30 CDT)", True), ("DEC run", "09-30 19:04 CDT 시작 (start git 02dafa1c = 동결 병합 커밋; raw run|git 2688/2688 같음), 20:22 CDT SPARSE_DONE ok=6 fail=0", True),
                          ("DEC labels", "새 18 라벨 (i) 17, (iv) 1 (SV8e SBL-loop, 판정점 2), (ii) 0", cnt == {"(i)": 17, "(ii)": 0, "(iii)": 0, "(iv)": 1} and len(R["SV"]["res"]["SBL-loop"]["t"]["cand"]) == 2),
                          ("DEC sentence", "4/6 (D2 C2·D3·UMi28·MIX3; C6·SV8e 는 §1 에서 불가)", sent == ["B16e4k", "D3", "U28", "MX"]), ("DEC pred", "§3 예측 6/6 (예측 6 채점 안 함)", True),
                          ("DEC main", "(A) \"V1 이 희소 baseline 3 개(SBL-loop, SBL-pilot, OMP-pilot) 전부보다 적게 실패\"", p1), ("DEC gate", "C6 게이트 건너뜀 (pick sha 고정, §5.2 (가))", True)):
        chk(name, s in dl, want, "DECISIONS")
    # ---- placeholders / interpretation vocabulary (three additions)
    add = "\n".join(lines[i61 - 1:]) + er + dl
    chk("placeholders", re.findall(r"x CDT|x KST|xx:xx|TODO|TBD", add), [], "records")
    chk("interpretation words", re.findall(r"유의하게|우수|개선|여지|headroom|최적|비긴다|significant|강건", add), [], "records")
    P(f"\n## checks {NCHK[0]}, mismatches {len(MISS)}")
    for m in MISS:
        P("  " + m)


if __name__ == "__main__":
    main()
