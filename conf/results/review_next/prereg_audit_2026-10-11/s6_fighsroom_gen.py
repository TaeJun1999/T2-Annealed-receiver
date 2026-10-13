#!/usr/bin/env python
"""s6_fighsroom_gen.py -- NEXT_EXPERIMENTS_FIGHSROOM16e4 §6 transcription generator (REPORT-ONLY registration; no test, no label).
Every number is read from a record, never typed:
  logs/run_fighsroom16e4.log                         start / phase C / run / acceptance / FIGHS_DONE lines (CDT)
  logs/run_D2_<TAG>.log                              runner minutes, tasks, done / exists chunk lines
  results/review_next/<TAG>_accept.txt               acceptance verdicts
  results/review_next/fighs_<TAG>.txt                count tables (failures / n, BLER, 95% Wilson)
  results/review_next/run_manifest_<TAG>.json        manifests
  results/review_next/FHC*_control.txt, *_aldcontrol.txt
  conference/figures/records/paper_f21srb{,hs}.txt   original (n = 2560) and merged counts, rising cells, zero-failure points
It does NOT read the new raws (raw_FH*): their counts come from the count tables (the figure script asserts raw == table).
Usage (cwd = ~/t2/conf):  python -B results/review_next/prereg_audit_2026-10-11/s6_fighsroom_gen.py [SRB|SRP] > <draft>.md
SRP = NEXT_EXPERIMENTS_FIGHSPATH16e4 (logs/run_fighspath16e4.log, tags FH*SRP*, records paper_f21srp{,hs}.txt, its own §3 predictions).
"""
import glob, json, re, sys

RV, REC = "results/review_next", "../conference/figures/records"
PR = sys.argv[1] if len(sys.argv) > 1 else "SRB"
RUN = {"SRB": "fighsroom", "SRP": "fighspath", "DMI": "fighsdmi"}[PR]   # DMI = NEXT_EXPERIMENTS_FIGHSDMI16e4 (its §3 = the SRP form)
TAGS = {f"FH{PR}B16e4": f"{PR}B16e4", f"FHSP{PR}": f"SP{PR}", f"FHALD{PR}": f"ALD{PR}"}
HS = (6, 9, 12, 15)
ORDER = ["M-ours-dscore-C-V1", "ALD-pilot", "M-ours-bstar", "R2-ours-G", "R1-turbo", "R3-bigamp", "R0-pilot@1", "SBL-loop", "SBL-pilot",
         "OMP-pilot", "R5-genie"]
SRC = {a: f"FH{PR}B16e4" for a in ORDER}
SRC.update({"ALD-pilot": f"FHALD{PR}", "SBL-loop": f"FHSP{PR}", "SBL-pilot": f"FHSP{PR}", "OMP-pilot": f"FHSP{PR}"})
out = []
def P(*a): out.append(" ".join(str(x) for x in a))


def table(tag):
    """count table -> {(snr, arm): (k, n, bler, lo, hi)} + its header line."""
    L = open(f"{RV}/fighs_{tag}.txt", encoding="utf-8").read().split("\n")
    t = {}
    for l in L:
        m = re.match(r"SNR \+?(-?\d+)\s+(\S+)\s+(\d+) / (\d+)\s+BLER (\S+)\s+95% \[(\S+), (\S+)\]", l)
        if m:
            t[int(m[1]), m[2]] = (int(m[3]), int(m[4]), m[5], m[6], m[7])
    return t, L[0]


def counts(path):
    """figure record 'Counts:' block -> {arm: [(k, n) x 7]} and the whole text."""
    s = open(path, encoding="utf-8").read()
    c = {}
    for l in s.split("Counts:")[1].split("\n\n")[0].split("\n"):
        f = l.split()
        if f and f[0] in ORDER:
            c[f[0]] = [tuple(int(x) for x in v.split("/")) for v in f[1:8]]
    assert sorted(c) == sorted(ORDER), sorted(c)
    return c, s


LOG = [l for l in open(f"logs/run_{RUN}16e4.log", encoding="utf-8", errors="replace").read().split("\n") if l.startswith("[fighs ")]
def when(pat):
    h = [re.match(r"\[fighs (\d\d-\d\d \d\d:\d\d) CDT\]", l)[1] for l in LOG if re.search(pat, l)]
    assert len(h) == 1, (pat, h)
    return h[0]
starts = [l for l in LOG if "start (git" in l]
assert len(starts) == 1, starts
GIT = re.search(r"start \(git (\w+)\)", starts[0])[1]
done = [l for l in LOG if "FIGHS_DONE" in l]
assert len(done) == 1, done
OKN, FAILN = (int(x) for x in re.search(r"FIGHS_DONE ok=(\d+) fail=(\d+)", done[0]).groups())
bad = [l for l in LOG if re.search(r"ABORT|SKIP|INVALID|failed", l)]

T, HEAD = {}, {}
for t in TAGS:
    T[t], HEAD[t] = table(t)
O, _ = counts(f"{REC}/paper_f21{PR.lower()}.txt")
Mg, HSREC = counts(f"{REC}/paper_f21{PR.lower()}hs.txt")
for a in ORDER:                                    # merged record == count table at +6..+15, == original record at -3/0/+3
    assert Mg[a][:3] == O[a][:3], a
    for i, s in enumerate(HS):
        assert Mg[a][3 + i] == T[SRC[a]][s, a][:2], (a, s, Mg[a][3 + i], T[SRC[a]][s, a])

P(f"### 6.1 실행·운영 기록 (생성기 `prereg_audit_2026-10-11/s6_fighsroom_gen.py`; 수치는 모두 기록 파일에서 읽음)\n")
P(f"`bash code/run_{RUN}16e4.sh` **한 번**, tmux `{RUN}`, {when('start .git')} CDT 시작(git {GIT} = 실행 커밋; 시작 줄 하나, 재개 없음). "
  f"단계 C (관측된 시험 청크 0 의 대조) {when('phase C done')} CDT: {[l for l in LOG if 'phase C done' in l][0].split('phase C done: ')[1]}. "
  f"`{done[0].split('] ')[1]}` {when('FIGHS_DONE')} CDT. ABORT · SKIP · INVALID 줄: {len(bad)} 개.\n")
P("| 행 | 시작 (CDT) | runner | 작업 (done / exists) | 수용 (CDT) | 수용 판정 | manifest git · config_hash | 대조 |")
P("|---|---|---|---|---|---|---|---|")
for t in TAGS:
    rl = open(f"logs/run_D2_{t}.log", encoding="utf-8", errors="replace").read()
    mins = re.findall(r"\[run\] finished in ([\d.]+) min", rl)
    tasks = re.findall(r"-> (\d+) tasks on (\d+) workers", rl)
    assert len(mins) == 1 and len(tasks) == 1, (t, mins, tasks)
    nd, ne = len(re.findall(r"\bdone\b", rl)), len(re.findall(r"\bexists\b", rl))
    acc = [l for l in LOG if re.search(rf"\] {t} acceptance rc=", l)]
    assert len(acc) == 1, acc
    af = open(f"{RV}/{t}_accept.txt", encoding="utf-8").read()
    man = json.load(open(f"{RV}/run_manifest_{t}.json"))
    ctl = open(f"{RV}/{t.replace('FH', 'FHC', 1)}_control.txt", encoding="utf-8").read().strip().split("\n")[-1]
    ac = glob.glob(f"{RV}/{t.replace('FH', 'FHC', 1)}_aldcontrol.txt")
    if ac:
        ctl += " · " + open(ac[0], encoding="utf-8").read().strip().split("\n")[-1]
    t_run, t_acc = when(rf"\] {t} run:"), when(rf"\] {t} acceptance rc=")
    P(f"| {t} | {t_run} | {mins[0]} 분 · {tasks[0][0]} 작업 · {tasks[0][1]} 워커 | {nd} / {ne} | {t_acc} | "
      f"rc={re.search(r'rc=(\d+)', acc[0])[1]}; {'; '.join(l.strip() for l in af.split(chr(10)) if l.startswith('ACCEPT'))} | "
      f"{man.get('git_commit', '?')} · {man.get('config_hash', '?')} | {ctl} |")
P("\n수용 파일의 (f) 줄(raw 당 청크 수 · `run|git` · pick · ald · raised):\n")
for t in TAGS:
    for l in open(f"{RV}/{t}_accept.txt", encoding="utf-8").read().split("\n"):
        if l.strip().startswith("(f)"):
            P(f"- `{l.strip()}`")
P("\n집계표 머리말:\n")
for t in TAGS:
    P(f"- `{HEAD[t]}`")

P("\n### 6.2 원고 범례 11 곡선 — BLER@16 실패 수 (+6 / +9 / +12 / +15 dB; 새 시행 n = 20480 과 원 raw n = 2560)\n")
P("| 곡선 (arm) | 출처 | " + " | ".join(f"{s:+d} dB: k / 20480 (BLER, 95 % Wilson)" for s in HS) + " | 원 raw k / 2560 (+6 / +9 / +12 / +15) |")
P("|---|---|" + "---|" * (len(HS) + 1))
for a in ORDER:
    cells = []
    for s in HS:
        k, n, b, lo, hi = T[SRC[a]][s, a]
        assert n == 20480, (a, s, n)
        cells.append(f"{k} ({b}, [{lo}, {hi}])")
    P(f"| {a} | raw_{SRC[a]} | " + " | ".join(cells) + " | " + " / ".join(str(k) for k, _ in O[a][3:]) + " |")
g = {t: [T[t][s, "R5-genie"][0] for s in HS] for t in TAGS}
P(f"\nPerfect CSI (R5-genie) 의 실패 수는 세 raw 에서 같다: " + " · ".join(f"{t} {v}" for t, v in g.items()) + f" → {'동일' if len({tuple(v) for v in g.values()}) == 1 else '**다름**'}.")
zero = [f"{a} {s:+d} dB" for a in ORDER for s in HS if T[SRC[a]][s, a][0] == 0]
P(f"\n0 실패 점 (n = 20480): {', '.join(zero) if zero else '없음'}.")
rising = [l.strip() for l in HSREC.split("\n") if "rising:" in l]
P(f"\n그림 기록 `records/paper_f21{PR.lower()}hs.txt` 의 '오르는 칸' (SNR 이 오를 때 BLER 이 오르는 칸, 한쪽 Fisher p; 보고만): {len(rising)} 줄.")
for l in rising:
    P(f"- `{l}`")

P("\n### 6.3 §3 예측 채점\n")
k = {a: [T[SRC[a]][s, a][0] for s in HS] for a in ORDER}
V, B = k["M-ours-dscore-C-V1"], k["M-ours-bstar"]
def rise_p(a):
    return [float(p) for l in rising if l.split("@16")[0].strip() == a for p in re.findall(r"p=([\d.e+-]+)", l.split("rising:")[1])]
NONE = "없음"
r2 = {a: rise_p(a) for a in ("M-ours-dscore-C-V1", "M-ours-bstar", "R5-genie")}
hit = lambda c: "적중" if c else "빗나감"
p2 = f"(오르는 칸의 p: {', '.join(f'{a} {v if v else NONE}' for a, v in r2.items())})"
if PR == "SRB":
    P(f"1. V1 의 실패 수 +6 dB > +9 dB → **{hit(V[0] > V[1])}** ({V[0]} 대 {V[1]}).")
    P(f"2. V1 · b\\* · Perfect CSI 에 Fisher p < 0.05 인 오르는 칸 없음 → **{hit(all(p >= 0.05 for v in r2.values() for p in v))}** {p2}.")
    P(f"3. +6 · +9 dB 에서 실패 수 V1 ≤ b\\* → **{hit(V[0] <= B[0] and V[1] <= B[1])}** ({V[0]} 대 {B[0]}, {V[1]} 대 {B[1]}).")
    P(f"4. +15 dB 에서 V1 실패 수 ≤ 5 / 20480 → **{hit(V[3] <= 5)}** ({V[3]}).")
else:
    P(f"1. V1 의 실패 수가 +6 ≥ +9 ≥ +12 ≥ +15 dB 로 줄기만 한다 → **{hit(V[0] >= V[1] >= V[2] >= V[3])}** ({' / '.join(map(str, V))}).")
    P(f"2. V1 · b\\* · Perfect CSI 에 Fisher p < 0.05 인 오르는 칸 없음 → **{hit(all(p >= 0.05 for v in r2.values() for p in v))}** {p2}.")
    P(f"3. +6 · +9 dB 에서 실패 수 V1 ≤ b\\* → **{hit(V[0] <= B[0] and V[1] <= B[1])}** ({V[0]} 대 {B[0]}, {V[1]} 대 {B[1]}).")
    P(f"4a. V1 의 +9 dB 실패 수 ≥ 1 / 20480 → **{hit(V[1] >= 1)}** ({V[1]}).")
    P(f"4b. V1 의 +15 dB 실패 수 ≤ 5 / 20480 → **{hit(V[3] <= 5)}** ({V[3]}).")
NST = len(re.findall(r"\] start \(git", open(f"logs/run_{RUN}16e4.log", encoding="utf-8").read()))
P(f"5. `FIGHS_DONE ok=3 fail=0`" + (", 재개 없이 한 번에(시작 줄 1 개)" if PR == "DMI" else "") + f" → **{hit((OKN, FAILN) == (3, 0) and (PR != "DMI" or NST == 1))}** (ok={OKN} fail={FAILN}" + (f"; 시작 줄 {NST} 개" if PR == "DMI" else "") + ").")
print("\n".join(out))
