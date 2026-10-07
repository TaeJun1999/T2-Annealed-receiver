#!/usr/bin/env python
"""s6_gen.py -- NEXT_EXPERIMENTS_FIGHS16e4 §6.1 transcription generator (REPORT-ONLY registration; no test, no label).
Every number in the draft is read from a record, never typed:
  code/run_fighs16e4.sh (ROWS)                      the 24 registered rows
  logs/run_fighs16e4.log                            start / phase C / run / acceptance / FIGHS_DONE lines (CDT), both starts
  logs/run_D2_<TAG>.log                             runner minutes, done / exists chunk lines
  logs/fighs_interrupt_20261006CDT/                 recover.log, before/ (+ before.sha256), envchk/cmp_ZZ*.txt, figs_pushed.txt
  results/review_next/<TAG>_accept.txt              acceptance verdicts ((a) + (f)), raised trials
  results/review_next/fighs_<TAG>.txt               count tables (failures / n, BLER, 95% Wilson)
  results/review_next/run_manifest_<TAG>.json       manifests
  results/review_next/FHC*_control.txt, *_aldcontrol.txt   control verdicts
  raw_<ORIG>                                        the ORIGINAL raws (test trials 0..2559, n = 2560), through analysis.load_raw
  results/review_next/NEXT_EXPERIMENTS_FIGHS16e4.md §0.4 (cross-check of the original counts), §1b (cost estimates)
It does NOT read the new raws (raw_FH*): their counts come from the count tables; the record audit re-derives them from raw.
Usage (cwd = ~/t2/conf):  python s6_gen.py [--cells OUT.tsv] > s6_draft_raw.md
"""
import glob, hashlib, json, os, re, sys
from datetime import datetime

sys.path.insert(0, "code")
import numpy as np
from scipy.stats import fisher_exact
from analysis import load_raw
from hisnr_report import wilson

RV = "results/review_next"; REG = f"{RV}/NEXT_EXPERIMENTS_FIGHS16e4.md"; D = "logs/fighs_interrupt_20261006CDT"
SN = [6.0, 9.0, 12.0, 15.0]; N2 = 20480
F = "TAG CELL PR BF CK SHA ROLE BS KK LL REF ORIG PICK FL ARMS".split()
ROWS = [dict(zip(F, l.split("|"))) for l in re.search(r"^ROWS='(.*?)'$", open("code/run_fighs16e4.sh").read(), re.S | re.M)[1].split("\n")]
assert len(ROWS) == 24, len(ROWS)
TAGS = [r["TAG"] for r in ROWS]
GROUPS = [("D2 C2 (Sparse specular 8×4)", TAGS[0:3]), ("D3 (S2c) C2", TAGS[3:6]), ("SV8e C2", TAGS[6:9]), ("UMi28 C2", TAGS[9:12]),
          ("MIX3 C2", TAGS[12:15]), ("D2 C2 회전 15°", TAGS[15:18]), ("D2 C2 회전 30°", TAGS[18:21]), ("D2 C6 (Sparse specular 16×4)", TAGS[21:24])]
out = []
def P(*a): out.append(" ".join(str(x) for x in a))
def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
def esc(x): return str(x).replace("|", "\\|")      # a '|' inside a markdown table cell


# ------------------------------------------------------------------ run log
def ts(l):
    m = re.match(r"\[fighs (\d\d)-(\d\d) (\d\d):(\d\d) CDT\]", l)
    return datetime(2026, int(m[1]), int(m[2]), int(m[3]), int(m[4])) if m else None
LOG = open("logs/run_fighs16e4.log", encoding="utf-8", errors="replace").read().split("\n")
runs = []                                    # one dict per 'start (git' line
for l in LOG:
    if "start (git" in l:
        runs.append(dict(start=ts(l), line=l, run={}, acc={}, ald={}, other=[], done=None, phasec=None))
        continue
    if not runs:
        continue
    r = runs[-1]
    if ts(l): r["lastline"] = l
    m = re.match(r"\[fighs [^\]]+\] (FH\w+) run:", l)
    if m: r["run"][m[1]] = ts(l)
    m = re.match(r"\[fighs [^\]]+\] (FH\w+) acceptance rc=(\d+) \((.*)\)", l)
    if m: r["acc"][m[1]] = (ts(l), int(m[2]), m[3].strip())
    m = re.match(r"\[fighs [^\]]+\] (FH\w+) ALD (\w+): (regen.*)", l)
    if m: r["ald"][m[1]] = (ts(l), m[3])
    if "phase C done" in l: r["phasec"] = (ts(l), l.split("phase C done: ")[1])
    if "FIGHS_DONE" in l: r["done"] = (ts(l), l.split("] ")[1])
    if re.search(r"ABORT|INVALID|SKIP|FAILED|rc=[1-9]", l): r["other"].append(l)
resume_scan = [l for l in LOG if l.startswith("[fighs] resume:")]
hm = lambda t: t.strftime("%m-%d %H:%M") if t else "—"

def runner_segments(tag):                    # [(header date, resume flag, n done, n exists, finished-min or None)]
    seg = []
    try:
        for l in open(f"logs/run_D2_{tag}.log", encoding="utf-8", errors="replace"):
            m = re.match(r"# run_fighs16e4 git (\w+) (\S+ \S+) CDT resume=(\d)", l)
            if m: seg.append([m[2], int(m[3]), 0, 0, None]); continue
            if not seg: continue
            if re.match(r"\d+/\d+ done ", l): seg[-1][2] += 1
            elif re.match(r"\d+/\d+ exists", l): seg[-1][3] += 1
            m = re.search(r"\[run\] finished in ([\d.]+) min", l)
            if m: seg[-1][4] = float(m[1])
    except FileNotFoundError:
        pass
    return seg

def table(tag):                              # count table -> {arm: {snr: (f, n, bler str, lo str, hi str)}}, header
    p = f"{RV}/fighs_{tag}.txt"
    if not os.path.exists(p) or not os.path.getsize(p):
        return None, None
    t, head = {}, None
    for l in open(p):
        if l.startswith("# run_fighs16e4"): head = l.strip(); continue
        m = re.match(r"SNR ([+-]\d+)\s+(\S+)\s+(\d+) / (\d+)\s+BLER (\S+)\s+95% \[(\S+), (\S+)\]", l)
        if m: t.setdefault(m[2], {})[float(m[1])] = (int(m[3]), int(m[4]), m[5], m[6], m[7])
    return t, head
TAB = {t: table(t) for t in TAGS}
have = [t for t in TAGS if TAB[t][0]]


# ------------------------------------------------------------------ §6.1 head: run, interruption, resume
P(f"<!-- s6_gen.py draft: {len(have)}/24 count tables present; missing {[t for t in TAGS if t not in have] or 'none'} -->\n")
P("**실행·수용** (`logs/run_fighs16e4.log` 의 줄 그대로; 시각 CDT)\n")
for i, r in enumerate(runs):
    P(f"- 시작 {i + 1}: `{r['line'].strip()}`" + (f" — phase C `{r['phasec'][1]}` ({hm(r['phasec'][0])})" if r["phasec"] else "")
      + (f" — 끝 `{r['done'][1]}` ({hm(r['done'][0])})" if r["done"] else " — FIGHS_DONE 줄 없음")
      + f"; 이 구간의 ABORT/INVALID/SKIP/FAILED/rc≠0 줄 {len(r['other'])}")
P(f"- `--resume` 의 청크 검사 줄: {resume_scan or '없음'}")
P("\n**중단·재개 기록** (`logs/fighs_interrupt_20261006CDT/recover.log` 그대로)\n")
for l in open(f"{D}/recover.log", encoding="utf-8", errors="replace"):
    P("    " + l.rstrip())
cmps = sorted(glob.glob(f"{D}/envchk/cmp_ZZ*.txt"))
ncmp = sum(int(re.search(r"(\d+) \(chunk, arm, key\) comparisons", open(c).read())[1]) for c in cmps)
ndif = sum(int(re.search(r"comparisons, (\d+) differ", open(c).read())[1]) for c in cmps)
oth = sorted({k for c in cmps for k in re.findall(r"'([^']+)'", re.search(r"information only\): (.*)", open(c).read())[1])})
P(f"\n- 환경 검사 (등록 밖; 스크래치 태그 `ZZ<행>`, 시험 청크 0 = 시행 0..39, +6/+9/+12/+15 dB): 비교 파일 {len(cmps)}, `ENVCHK: OK` "
  f"{sum('ENVCHK: OK' in open(c).read().split(chr(10)) for c in cmps)}, (청크, arm, 키) 비교 {ncmp}, 다름 {ndif}; 파일 전체에서 다른 키 (정보용): {oth}")
bs, same, diff = sorted(os.listdir(f"{D}/before")), 0, []
for f in bs:
    if f in ("run_fighs16e4.log", "fighs_tmux.out"):
        continue
    cur = f"results/ald/{f}" if f.startswith("ald_") else f"{RV}/{f}"
    if sha(f"{D}/before/{f}") == sha(cur): same += 1
    else: diff.append(f)
P(f"- 재개가 다시 만든 산출물 대 중단 전 사본 (`before/`, {len(bs) - 2} 파일; sha256): 바이트 동일 {same}, 다름 {len(diff)} {diff}")
for f in diff:
    if f.endswith(".json"):
        a, b = json.load(open(f"{D}/before/{f}")), json.load(open(f"{RV}/{f}"))
        ks = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
        P(f"    - `{f}`: 다른 키 {ks}" + "".join(f"; {k}: {json.dumps(a.get(k), ensure_ascii=False)[:110]} → {json.dumps(b.get(k), ensure_ascii=False)[:110]}" for k in ks))
for t in ("a", "b"):
    P(f"    - `ald_FHCXAROT{t}B16e4k.npz` sha256[:16] 중단 전 {sha(f'{D}/before/ald_FHCXAROT{t}B16e4k.npz')[:16]} · 지금 "
      f"{sha(f'results/ald/ald_FHCXAROT{t}B16e4k.npz')[:16]} (mtime {datetime.fromtimestamp(os.path.getmtime(f'results/ald/ald_FHCXAROT{t}B16e4k.npz')):%m-%d %H:%M:%S} KST)")
P("- 그림 스크립트 실행 (실행 구간 중; `figs_pushed.txt` 그대로):")
for l in open(f"{D}/figs_pushed.txt"):
    if not l.startswith("#"): P("    " + l.rstrip())

# ------------------------------------------------------------------ per-row table
EST = {m[1]: m[2] for m in re.finditer(r"^\| \d+ \| (FH\w+) \|.*\| ([^|]+) \| [^|]*\|\s*$", open(REG, encoding="utf-8").read(), re.M)}
P("\n**행별 실행·수용** (runner 분 = `logs/run_D2_<TAG>.log` 의 `finished in`; 수용 = 마지막 시작 뒤의 `acceptance` 줄; 추정 = §1b)\n")
P("| # | TAG | runner 구간 (머리 줄 시각 CDT · resume · done 청크 · exists 청크 · 분) | 수용 (마지막 시작 뒤) | `<TAG>_accept.txt` | raised 시행 | §1b 추정 (min) |")
P("|---|---|---|---|---|---|---|")
last = runs[-1]
for i, r in enumerate(ROWS):
    t = r["TAG"]; seg = runner_segments(t)
    s = "; ".join(f"{d} · r{rs} · {nd} · {ne} · {'미완' if fm is None else fm}" for d, rs, nd, ne, fm in seg) or "—"
    a = last["acc"].get(t)
    try:
        acc = open(f"{RV}/{t}_accept.txt").read()
        v = " / ".join(l.strip() for l in acc.split("\n") if l.startswith("ACCEPT"))
        rz = re.search(r"raised trials per arm \(= failures, report only\) (.*)", acc); rz = rz[1].strip() if rz else "?"
    except FileNotFoundError:
        v, rz = "(없음)", "?"
    P(f"| {i + 1} | {t} | {s} | {hm(a[0]) + f' rc={a[1]}' if a else '—'} | {v} | {rz} | {EST.get(t, '?').strip()} |")
P("\n**대조 (phase C; 마지막 시작에서 다시 만든 판정 파일)**\n")
P("| 대조 태그 | 판정 파일 첫 줄 | 판정 |")
P("|---|---|---|")
for r in ROWS:
    c = r["TAG"].replace("FH", "FHC", 1)
    for suf in ("control", "aldcontrol"):
        p = f"{RV}/{c}_{suf}.txt"
        if os.path.exists(p):
            ls = [l for l in open(p).read().split("\n") if l.strip()]
            P(f"| {c} ({suf}) | {esc(ls[0][:230]) if ls else '(빈 파일)'} | {ls[-1] if ls else '—'} |")

# ------------------------------------------------------------------ manifests
P("\n**매니페스트 요지** (`run_manifest_<TAG>.json`)\n")
P("| TAG | git | n_raw_files | config_hash | 적합 링크 → 대상 | ckpt sha256[:16] · id | skip_min..skip_max_end | arms | host · 작성 |")
P("|---|---|---|---|---|---|---|---|---|")
for r in ROWS:
    t = r["TAG"]; p = f"{RV}/run_manifest_{t}.json"
    if not os.path.exists(p):
        P(f"| {t} | (없음) |||||||"); continue
    m = json.load(open(p)); ck = m.get("stagec_checkpoint") or {}; tsr = m.get("trial_stream", {})
    lk = f"results/gmm_fits_D2_{t}"
    P(f"| {t} | {m['git_commit']} | {m['n_raw_files']} | {m['config_hash']} | `{os.path.basename(lk)}` → `{os.readlink(lk) if os.path.islink(lk) else '?'}` | "
      f"{ck.get('sha256_16', '—')} · {esc(m.get('stagec_ckpt_id', '—'))} | {tsr.get('skip_min')}..{tsr.get('skip_max_end')} | {', '.join(m['arms'])} | "
      f"{m['versions']['host']} · {m['written']} |")

# ------------------------------------------------------------------ count tables (new trials)
P("\n**보고 표 (전부 보고 전용 — 판정 아님; `fighs_<TAG>.txt` 의 실패 / 20480 · BLER; 95% Wilson 은 그 파일에)** — 반복 16\n")
for g, tags in GROUPS:
    P(f"**{g}**\n")
    P("| arm (TAG) | +6 dB | +9 dB | +12 dB | +15 dB |")
    P("|---|---|---|---|---|")
    gen = {}
    for t in tags:
        tb, head = TAB[t]
        if not tb:
            P(f"| ({t}: 집계표 없음) |||||"); continue
        assert all(tb[a][s][1] == N2 for a in tb for s in SN), (t, "n != 20480")
        for a in sorted(tb):
            cells = " | ".join(f"{tb[a][s][0]} · {tb[a][s][2]}" for s in SN)
            if a == "R5-genie":
                gen[t] = tuple(tb[a][s][0] for s in SN); continue
            P(f"| {a} ({t}) | {cells} |")
    if gen:
        vals = sorted(set(gen.values()))
        t0 = next(iter(gen)); tb = TAB[t0][0]
        P(f"| R5-genie ({', '.join(gen)}: {'같은 수' if len(vals) == 1 else '수가 다름 ' + str(gen)}) | " + " | ".join(f"{tb['R5-genie'][s][0]} · {tb['R5-genie'][s][2]}" for s in SN) + " |")
    P("")
heads = {t: TAB[t][1] for t in have}
P(f"집계표 머리말의 `load_raw warnings`: " + (", ".join(sorted({re.search(r"load_raw warnings (\d+)", h)[1] for h in heads.values()})) or "—") + f" (표 {len(heads)} 개의 값 집합)")

# ------------------------------------------------------------------ the 76 curves: original (n = 2560) vs new (n = 20480)
_orig = {}
def orig(raw):
    if raw not in _orig:
        d, _, w = load_raw("D2", root=raw); _orig[raw] = (d, w)
    return _orig[raw]
def fails(e):                                 # failures at iteration 16; a non-finite block = failure (hisnr_report rule)
    e = np.asarray(e, float)[:, -1]; e = np.where(np.isfinite(e), e, 1.0); return int(e.sum()), len(e)
curves = []                                   # (group, tag, arm, orig raw, {snr: (f, n)} original incl. +3, {snr: f} new)
for g, tags in GROUPS:
    for t in tags:
        r = ROWS[TAGS.index(t)]
        for a in r["ARMS"].split():
            if a == "R5-genie" and r["REF"] != "-":
                continue                      # genie copies of dependent rows / HISNR genie: not one of the 76 redrawn curves
            src = None
            for o in r["ORIG"].split(","):
                d, w = orig(f"raw_{o}")
                ks = [k for k in d if k[0] == r["CELL"]]
                if ks and all(a in d[k] and getattr(d[k][a].get("blk_err"), "ndim", 0) == 2 for k in ks if k[2] in SN):
                    src = o; break
            assert src, (t, a, "in no original raw")
            d, w = orig(f"raw_{src}")
            oc = {k[2]: fails(d[k][a]["blk_err"]) for k in d if k[0] == r["CELL"] and k[2] in [3.0] + SN}
            nw = {s: TAB[t][0][a][s][0] for s in SN} if TAB[t][0] else None
            curves.append((g, t, a, src, oc, nw))
assert len(curves) == 76, len(curves)
warn_o = {k: len(v[1]) for k, v in _orig.items()}

# §0.4 cross-check of the original counts
NM = {"R0-pilot": "R0-pilot", "R1": "R1-turbo", "R2": "R2-ours-G", "R3": "R3-bigamp", "b\\*": "M-ours-bstar", "V1": "M-ours-dscore-C-V1",
      "genie": "R5-genie", "SBL-loop": "SBL-loop", "SBL-pilot": "SBL-pilot", "OMP-pilot": "OMP-pilot", "V1-pilot": "V1-pilot",
      "bstar-pilot": "bstar-pilot", "ALD-pilot": "ALD-pilot"}
G04 = {"D2 C2 (새 arm 만)": 0, "D2 C6 (새 arm 만)": 7, "D3": 1, "SV8e": 2, "UMi28": 3, "MIX3": 4, "회전 15°": 5, "회전 30°": 6}
reg04, up04 = {}, set()
for l in open(REG, encoding="utf-8"):
    m = re.match(r"\| ([^|]+?) \| (.*\d+/\d+/\d+/\d+.*) \|\s*$", l)
    if m and m[1].strip() in G04:
        for it in m[2].split(";"):
            q = re.match(r"\s*(\S+) (\d+)/(\d+)/(\d+)/(\d+)( ↑)?", it)
            if q:
                reg04[(GROUPS[G04[m[1].strip()]][0], NM[q[1]])] = tuple(int(q[i]) for i in range(2, 6))
                if q[6]: up04.add((GROUPS[G04[m[1].strip()]][0], NM[q[1]]))
mism = [(g, a, tuple(oc[s][0] for s in SN), reg04.get((g, a))) for g, t, a, src, oc, nw in curves if reg04.get((g, a)) != tuple(oc[s][0] for s in SN)]
P(f"\n**원 raw (n = 2560) 실패 수** — `analysis.load_raw` (경고 수 {warn_o}) 로 다시 계산, 반복 16, 비유한 → 실패. 등록 §0.4 와 대조: "
  f"곡선 {len(curves)} 개 중 §0.4 에 있는 {sum((g, a) in reg04 for g, t, a, *_ in curves)} 개, 불일치 {len(mism)} {mism if mism else ''}; "
  f"원 raw 의 n: {sorted({oc[s][1] for *_, oc, nw in curves for s in oc})}")

def rising(seq):                              # indices i where BLER(i) > BLER(i-1); seq = [(f, n), ...]
    return [i for i in range(1, len(seq)) if seq[i][0] / seq[i][1] > seq[i - 1][0] / seq[i - 1][1]]
def fp(hi, lo):
    return fisher_exact([[hi[0], hi[1] - hi[0]], [lo[0], lo[1] - lo[0]]], alternative="greater")[1]

# prediction 1
done = [c for c in curves if c[5]]
cells, inside, outside = 0, 0, []
rowsout = []
for g, t, a, src, oc, nw in done:
    for s in SN:
        lo, hi = wilson(*oc[s]); p = nw[s] / N2; ok = lo <= p <= hi
        cells += 1; inside += ok
        rowsout.append((g, t, a, src, s, oc[s][0], oc[s][1], lo, hi, nw[s], N2, p, ok))
        if not ok: outside.append((g, a, s, oc[s][0], f"[{lo:.2e}, {hi:.2e}]", nw[s], f"{p:.2e}"))
P(f"\n**§3 예측 1** — 다시 그리는 곡선 {len(done)} 개 (실행·수용된 것; 76 개 중) × 4 SNR = {cells} 칸: 새 점추정 (n = 20480) ∈ 원 raw (n = 2560) 95% Wilson "
  f"구간 (닫힌 구간) {inside}/{cells} = {inside / max(cells, 1):.4f} (기준 ≥ 0.90)")
P("\n| 묶음 | 곡선 수 | 칸 | 구간 안 |")
P("|---|---|---|---|")
for g, tags in GROUPS:
    rr = [x for x in rowsout if x[0] == g]
    P(f"| {g} | {len({(x[1], x[2]) for x in rr})} | {len(rr)} | {sum(x[-1] for x in rr)} |")
P(f"\n구간 밖 {len(outside)} 칸 (묶음, arm, SNR, 원 실패 / 2560, 원 95% Wilson, 새 실패 / 20480, 새 BLER):")
for o in outside:
    P(f"- {o[0]} · {o[1]} · {o[2]:+.0f} dB · {o[3]} · {o[4]} · {o[5]} · {o[6]}")

# prediction 2 + the figure rule's rising cells
P("\n**§3 예측 2 · 오르는 칸** (BLER 이 바로 아래 SNR 점보다 큰 칸; 동률 아님; +3 → +6 dB 칸은 두 시행 집합 비교이며 기록만 — 예측 2 의 분자에 넣지 않는다)\n")
no3 = [c for c in done if c[2] != "R3-bigamp"]
new_up = [(g, a) for g, t, a, src, oc, nw in no3 if rising([(nw[s], N2) for s in SN])]
old_up = [(g, a) for g, t, a, src, oc, nw in curves if a != "R3-bigamp" and rising([oc[s] for s in SN])]
old_all = [(g, a) for g, t, a, src, oc, nw in curves if rising([oc[s] for s in SN])]
P(f"- 원 raw (n = 2560), +6..+15 dB 에 오르는 칸이 있는 곡선: R3 제외 {len(old_up)}/{sum(c[2] != 'R3-bigamp' for c in curves)} {old_up}; 전체 {len(old_all)}/76 "
  f"(등록 §0.4 의 ↑ 표시 {len(up04)} 개와 {'일치' if set(old_all) == up04 else '불일치: ' + str(sorted(set(old_all) ^ up04))})")
P(f"- 새 raw (n = 20480), +6..+15 dB 에 오르는 칸이 있는 곡선: R3 제외 **{len(new_up)}/{len(no3)}** {new_up} (예측: 원 raw 의 9 개보다 적다)")
P("\n| 묶음 | arm | 칸 | 아래 점 (실패 / n) | 위 점 (실패 / n) | 단측 Fisher p (greater) | 예측 2 분자 |")
P("|---|---|---|---|---|---|---|")
for g, t, a, src, oc, nw in done:
    seq = [(3.0, oc[3.0])] + [(s, (nw[s], N2)) for s in SN]
    for i in rising([x[1] for x in seq]):
        (s0, lo), (s1, hi) = seq[i - 1], seq[i]
        P(f"| {g} | {a} | {s0:+.0f} → {s1:+.0f} dB | {lo[0]} / {lo[1]} | {hi[0]} / {hi[1]} | {fp(hi, lo):.2g} | "
          f"{'—  (기록만)' if s0 == 3.0 else ('R3 제외' if a == 'R3-bigamp' else '예')} |")

# prediction 3
P("\n**§3 예측 3** — V1 실패 ≤ b\\* 실패 (같은 시행, 동률 포함), D3·SV8e·UMi28·MIX3·회전 15°·30° × 4 SNR\n")
P("| 묶음 (TAG) | +6 dB V1 : b\\* | +9 dB | +12 dB | +15 dB | 성립 칸 |")
P("|---|---|---|---|---|---|")
tot = n3 = 0
for g, tags in GROUPS[1:7]:
    tb = TAB[tags[0]][0]
    if not tb:
        P(f"| {g} ({tags[0]}) | (집계표 없음) |||||"); continue
    pr = [(tb["M-ours-dscore-C-V1"][s][0], tb["M-ours-bstar"][s][0]) for s in SN]
    k = sum(v <= b for v, b in pr); tot += k; n3 += 4
    P(f"| {g} ({tags[0]}) | " + " | ".join(f"{v} : {b}" for v, b in pr) + f" | {k}/4 |")
P(f"\n합 **{tot}/{n3}** (기준 ≥ 22/24)")

# ------------------------------------------------------------------ durations
P("\n**소요** (실행 로그의 분 단위 시각)\n")
r1, r2 = runs[0], runs[-1]
P(f"- 첫 시작 {hm(r1['start'])}; 그 구간의 마지막 시각 줄: `{r1.get('lastline', '—')[:70]}`")
if r2["done"]:
    P(f"- 재개 {hm(r2['start'])} → FIGHS_DONE {hm(r2['done'][0])}: {(r2['done'][0] - r2['start']).total_seconds() / 3600:.2f} h; "
      f"첫 구간 {hm(r1['start'])} 부터의 벽시계 {(r2['done'][0] - r1['start']).total_seconds() / 3600:.2f} h")
mins = {t: [fm for *_, fm in runner_segments(t) if fm] for t in TAGS}
P(f"- runner `finished in` 분의 합 (청크를 계산한 구간만, 0.5 분 미만의 exists-only 구간 제외): "
  f"{sum(x for v in mins.values() for x in v if x >= 0.5):.1f} min; §1b 합계 추정 ≈ 1151 min")

# ------------------------------------------------------------------ §3 scoring
P("\n**§3 예측 채점** (보고 전용; 적중/빗나감만; 분모 = 실행·수용된 곡선)\n")
P("| # | 예측 | 결정하는 수 | 채점 |")
P("|---|---|---|---|")
r1ok = cells > 0 and inside / cells >= 0.90
P(f"| 1 | 다시 그리는 곡선 × 4 SNR 칸의 ≥ 90 % 에서 새 점추정 ∈ 원 raw 95% Wilson | {inside}/{cells} = {inside / max(cells, 1):.4f} | {'✓' if r1ok else '✗'} |")
P(f"| 2 | R3-bigamp 를 뺀 곡선 중 +6 → +9 → +12 → +15 dB 에 오르는 칸이 있는 곡선이 원 raw 의 9 개보다 적다 | 새 raw {len(new_up)}/{len(no3)} (원 raw 재계산 {len(old_up)}/{sum(c[2] != 'R3-bigamp' for c in curves)}) | {'✓' if len(new_up) < 9 else '✗'} |")
P(f"| 3 | V1 실패 ≤ b\\* 실패, 24 칸 중 ≥ 22 | {tot}/{n3} | {'✓' if tot >= 22 else '✗'} |")
hits = sum([r1ok, len(new_up) < 9, tot >= 22])
P(f"\n합계: 적중 {hits}, 빗나감 {3 - hits}.")

# ------------------------------------------------------------------ environment (read when this record is generated) + other CPU jobs
import subprocess
def sh(c): return subprocess.run(c, shell=True, capture_output=True, text=True).stdout.strip()
P("\n**환경 (이 초안을 만들 때 읽은 값)**\n")
P(f"- hostname `{sh('hostname')}`; 컨테이너 PID 1 시작 `{sh('TZ=America/Chicago ps -o lstart= -p 1')}` (CDT, `TZ=America/Chicago ps -o lstart= -p 1`); "
  f"호스트 uptime `{sh('uptime -p')}`; NVIDIA 드라이버 `{sh('nvidia-smi --query-gpu=driver_version --format=csv,noheader | sort -u')}`; "
  f"`{sh('ldd --version | head -1')}`; `/var/log/apt/history.log` 마지막 Start-Date `{sh('grep ^Start-Date /var/log/apt/history.log | tail -1')}`")
P(f"- 중단 전 매니페스트 (`before/run_manifest_FHB16e4k.json`) 의 versions: `{json.dumps(json.load(open(D + '/before/run_manifest_FHB16e4k.json'))['versions'])}`")
P(f"- 새 시행 ALD 추정 파일: " + "; ".join(f"`{os.path.basename(f)}` sha256[:16] {sha(f)[:16]}, mtime {datetime.fromtimestamp(os.path.getmtime(f)):%m-%d %H:%M:%S} KST, prov git "
  f"{json.loads(str(np.load(f)['prov']))['git']}" for f in sorted(glob.glob('results/ald/ald_*_hisnr.npz'))))
P("\n**실행 구간 (첫 시작 ~ FIGHS_DONE) 에 주 세션이 돌린 다른 CPU 작업** (세션 기록 `~/.claude/projects/-home-HTJ-t2/<세션>.jsonl` 의 Bash 도구 호출·결과 시각, UTC−5 로 환산; "
  "대상: 그림 스크립트 `paper_f*.py`·`fighs_merge.py`, 이 생성기 `s6_gen.py`, `sync_paper_branch.sh`)\n")
from datetime import timedelta
z0 = (runs[0]["start"] + timedelta(hours=5)).strftime("%Y-%m-%dT%H:%M")
z1 = ((runs[-1]["done"][0] if runs[-1]["done"] else datetime(2099, 1, 1)) + timedelta(hours=5, minutes=1)).strftime("%Y-%m-%dT%H:%M")
cdt = lambda z: (datetime.strptime(z[:19], "%Y-%m-%dT%H:%M:%S") - timedelta(hours=5)).strftime("%m-%d %H:%M:%S")
for sess in ("6cbef450-8bb7-430d-b07a-4c32854f5588", "8a735dc6-ef2e-41fe-9aca-aa15c17162ed"):
    calls, res = {}, {}
    with open(f"/home/HTJ/.claude/projects/-home-HTJ-t2/{sess}.jsonl", "rb") as fh:
        fh.seek(0, 2); sz = fh.tell(); fh.seek(max(0, sz - 12_000_000)); tail = fh.read().decode("utf-8", "replace").split("\n")[1:]
    for ln in tail:
        try: o = json.loads(ln)
        except Exception: continue
        c = (o.get("message") or {}).get("content"); t = o.get("timestamp", "")
        if not isinstance(c, list): continue
        for b in c:
            if b.get("type") == "tool_use" and b.get("name") == "Bash" and z0 <= t < z1:
                cmd = b.get("input", {}).get("command", "")
                nm = sorted(set(re.findall(r"python[^|;&\n]*?(paper_f\$?\{?\w*\}?|fighs_merge|s6_gen)\.py", cmd)))
                if "for f in paper_f16 paper_f31" in cmd: nm = ["paper_f16", "paper_f31"]
                if "sync_paper_branch.sh" in cmd and "bash conference/tools/sync_paper_branch.sh" in cmd: nm.append("sync_paper_branch.sh")
                if nm: calls[b["id"]] = (t, nm)
            if b.get("type") == "tool_result" and b.get("tool_use_id") in calls:
                res[b["tool_use_id"]] = t
    P(f"- 세션 {sess[:8]}:")
    for k, (t0, names) in sorted(calls.items(), key=lambda kv: kv[1][0]):
        P(f"    - {', '.join(names)}: {cdt(t0)} – {cdt(res[k]) if k in res else '?'} CDT")

# group sums of runner minutes vs the §1b estimates
P("\n**묶음별 runner 분** (청크를 계산한 구간의 `finished in` 합 대 §1b 추정 합)\n")
P("| 묶음 | runner 분 | §1b 추정 (min) |")
P("|---|---|---|")
num = lambda x: int(re.search(r"\d+", x)[0])
for g, tags in GROUPS:
    P(f"| {g} | {sum(x for t in tags for x in mins[t] if x >= 0.5):.1f} | {sum(num(EST[t]) for t in tags)} |")

# rising cells printed by the regenerated figure scripts (verbatim)
P("\n**다시 그린 그림의 기록 텍스트가 적은 오르는 칸** (`conference/figures/records/paper_f<NN>.txt` 의 `rising:` 줄 그대로; HISNR raw 에서 오는 곡선 포함)\n")
for f in sorted(glob.glob("/home/HTJ/t2/conference/figures/records/paper_f*.txt")):
    ls = [re.sub(r"\s+", " ", l.strip()) for l in open(f, encoding="utf-8") if "rising:" in l]
    P(f"- `{os.path.basename(f)}` ({datetime.fromtimestamp(os.path.getmtime(f)):%m-%d %H:%M:%S} KST, {sum(1 for _ in open(f, encoding='utf-8'))} 줄): " + ("없음" if not ls else ""))
    for l in ls: P(f"    - {l}")

print("\n".join(out))
if "--cells" in sys.argv:
    with open(sys.argv[sys.argv.index("--cells") + 1], "w") as fo:
        fo.write("group\ttag\tarm\torig_raw\tsnr\torig_fail\torig_n\torig_wilson_lo\torig_wilson_hi\tnew_fail\tnew_n\tnew_bler\tinside\n")
        for x in rowsout:
            fo.write("\t".join(str(v) if not isinstance(v, float) else f"{v:.6e}" for v in x) + "\n")
