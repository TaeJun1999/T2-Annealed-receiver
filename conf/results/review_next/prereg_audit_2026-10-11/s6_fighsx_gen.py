#!/usr/bin/env python
"""s6_fighsx_gen.py -- NEXT_EXPERIMENTS_FIGHSX16e4 §6 transcription generator (REPORT-ONLY registration; no test, no label).
Every number is read from a record, never typed:
  logs/run_fighsx16e4.log                             start / phase C / run / acceptance / FIGHS_DONE lines (CDT)
  logs/run_D2_FX<TAG>.log                             runner minutes, tasks, done / exists chunk lines
  results/review_next/FX<TAG>_accept.txt, fighs_FX<TAG>.txt (count lines + '# split' lines), run_manifest_FX<TAG>.json,
  FXC*_control.txt, FXCALD*_aldcontrol.txt, fighs_FH<TAG>.txt (the n = 20480 counts)
  conference/figures/records/paper_f21{srb,srp}hsx.txt  merged counts, rising cells, zero-failure points
  <overlap file>                                       the output of fx_overlap_check.py (prediction 8)
It does NOT read the raws.  Usage (cwd = ~/t2/conf):  python -B .../s6_fighsx_gen.py <overlap file> [SRB|SRP ...] > <draft>.md
(a prior list = a partial draft while the run is still going: only those priors' rows, no FIGHS_DONE required)
"""
import glob, json, re, sys

RV, REC = "results/review_next", "../conference/figures/records"
ORDER = ["M-ours-dscore-C-V1", "ALD-pilot", "M-ours-bstar", "R2-ours-G", "R1-turbo", "R3-bigamp", "R0-pilot@1", "SBL-loop", "SBL-pilot",
         "OMP-pilot", "R5-genie"]
HS, N = (12, 15), 81920
PRS = sys.argv[2:] or ["SRB", "SRP"]
NONE = "없음"
out = []
def P(*a): out.append(" ".join(str(x) for x in a))
def src(p, a): return {"ALD-pilot": f"ALD{p}", "SBL-loop": f"SP{p}", "SBL-pilot": f"SP{p}", "OMP-pilot": f"SP{p}"}.get(a, f"{p}B16e4")


def table(tag):
    """count table -> {(snr, arm): (k, n, bler, lo, hi)}, {(snr, arm): (seen k, unseen k, unseen n, bler, lo, hi)}, header line."""
    L = open(f"{RV}/fighs_{tag}.txt", encoding="utf-8").read().split("\n")
    t, sp = {}, {}
    for l in L:
        m = re.match(r"SNR \+?(-?\d+)\s+(\S+)\s+(\d+) / (\d+)\s+BLER (\S+)\s+95% \[(\S+), (\S+)\]", l)
        if m:
            t[int(m[1]), m[2]] = (int(m[3]), int(m[4]), m[5], m[6], m[7])
        m = re.match(r"# split SNR \+?(-?\d+)\s+(\S+)\s+trials 10000\.\.30479 \(seen, raw_FH\*\): (\d+) of 20480;  trials 30480\.\.91919 "
                     r"\(unseen\): (\d+) of (\d+)\s+BLER (\S+)\s+95% \[(\S+), (\S+)\]", l)
        if m:
            sp[int(m[1]), m[2]] = (int(m[3]), int(m[4]), int(m[5]), m[6], m[7], m[8])
    return t, sp, L[0]


LOG = [l for l in open("logs/run_fighsx16e4.log", encoding="utf-8", errors="replace").read().split("\n") if l.startswith("[fighs ")]
starts = [l for l in LOG if "start (git" in l]
GIT = re.search(r"start \(git (\w+)\)", starts[0])[1]
assert all(f"start (git {GIT})" in l for l in starts), starts                  # every (re)start on the run commit
done = [l for l in LOG if "FIGHS_DONE" in l]
assert done or len(sys.argv) > 2, done
OKN, FAILN = (int(x) for x in re.search(r"FIGHS_DONE ok=(\d+) fail=(\d+)", done[0]).groups()) if done else (None, None)   # the FIRST pass
TAGS = [f"FX{x}" for p in PRS for x in (f"{p}B16e4", f"SP{p}", f"ALD{p}")]
ops = [l for l in LOG if re.search(r"start \(git|phase C done|FIGHS_DONE|ABORT|SKIP|INVALID|failed", l)]

P(f"### 6.1 실행·운영 기록 (생성기 `prereg_audit_2026-10-11/s6_fighsx_gen.py`; 수치는 모두 기록 파일에서 읽음)\n")
P(f"`bash code/run_fighsx16e4.sh`, 실행 커밋 {GIT}; 시작 줄 {len(starts)} 개(첫 실행 + `--resume` {len(starts) - 1} 번), `FIGHS_DONE` 줄 {len(done)} 개. "
  "운영 로그 `logs/run_fighsx16e4.log` 의 시작 · 단계 C · 종료 · 중단 줄 전부(원문, 시간순):\n")
for l in ops:
    P(f"- `{l[:230]}`")
P("")
P("| 행 | 시작 (CDT) | runner | 작업 (done / exists) | 수용 (CDT) | 수용 판정 | manifest git · config_hash | 대조 |")
P("|---|---|---|---|---|---|---|---|")
for t in TAGS:
    rl = open(f"logs/run_D2_{t}.log", encoding="utf-8", errors="replace").read()
    mins = re.findall(r"\[run\] finished in ([\d.]+) min", rl)
    tasks = re.findall(r"-> (\d+) tasks on (\d+) workers", rl)
    nd, ne = len(re.findall(r"\bdone\b", rl)), len(re.findall(r"\bexists\b", rl))
    acc = [l for l in LOG if re.search(rf"\] {t} acceptance rc=", l)]
    af = open(f"{RV}/{t}_accept.txt", encoding="utf-8").read()
    man = json.load(open(f"{RV}/run_manifest_{t}.json"))
    c = t.replace("FX", "FXC", 1)
    ctl = open(f"{RV}/{c}_control.txt", encoding="utf-8").read().strip().split("\n")[-1]
    ac = glob.glob(f"{RV}/{c}_aldcontrol.txt")
    if ac:
        ctl += " · " + open(ac[0], encoding="utf-8").read().strip().split("\n")[-1]
    runs = [re.match(r"\[fighs (\d\d-\d\d \d\d:\d\d) CDT\]", l)[1] for l in LOG if re.search(rf"\] {t} run:", l)]
    accs = [re.match(r"\[fighs (\d\d-\d\d \d\d:\d\d) CDT\]", l)[1] for l in acc]
    P(f"| {t} | {' · '.join(runs)} | {' · '.join(mins)} 분 · {tasks[-1][0]} 작업 · {tasks[-1][1]} 워커 | {nd} / {ne} | {' · '.join(accs)} | "
      f"rc={re.search(r'rc=(\d+)', acc[-1])[1]}; {'; '.join(l.strip() for l in af.split(chr(10)) if l.startswith('ACCEPT'))} | "
      f"{man.get('git_commit', '?')} · {man.get('config_hash', '?')} | {ctl} |")
P("\n수용 파일의 (f) 줄:\n")
for t in TAGS:
    for l in open(f"{RV}/{t}_accept.txt", encoding="utf-8").read().split("\n"):
        if l.strip().startswith("(f)"):
            P(f"- `{l.strip()}`")

K, U, RIS = {}, {}, {}
for p, room in ((q, {"SRB": "방, 무작위 위치", "SRP": "경로, 이동 단말"}[q]) for q in PRS):
    T, SPL = {}, {}
    for x in (f"{p}B16e4", f"SP{p}", f"ALD{p}"):
        T[x], SPL[x], head = table(f"FX{x}")
        P(f"\n집계표 머리말: `{head}`")
    FH = {x: table(f"FH{x}")[0] for x in T}
    rec = open(f"{REC}/paper_f21{p.lower()}hsx.txt", encoding="utf-8").read()
    cnt = {}
    for l in rec.split("Counts:")[1].split("\n\n")[0].split("\n"):
        f = l.split()
        if f and f[0] in ORDER:
            cnt[f[0]] = [tuple(int(v) for v in x.split("/")) for x in f[1:8]]
    P(f"\n### 6.2{'ab'[p == 'SRP']} {p} ({room}) — 범례 11 곡선의 +12 / +15 dB 실패 수: n = 81920 전체, 보지 않은 61440 시행만, 앞선 n = 20480\n")
    P("| 곡선 (arm) | 출처 | " + " | ".join(f"{s:+d} dB: k / 81920 (BLER, 95 % Wilson) · 보지 않은 시행 k / 61440 (BLER) · 본 시행 k / 20480 [raw_FH 의 k]" for s in HS) + " |")
    P("|---|---|---|---|")
    for a in ORDER:
        x = src(p, a); cells = []
        for i, s in enumerate(HS):
            k, n, b, lo, hi = T[x][s, a]
            g, u, m, ub, _, _ = SPL[x][s, a]
            assert n == N and m == 61440 and g + u == k and cnt[a][5 + i] == (k, n), (p, a, s)
            fh = FH[x][s, a][0]
            assert a == "ALD-pilot" or g == fh, (p, a, s, g, fh)          # the seen trials reproduce raw_FH (not ALD-pilot: new posterior sample)
            cells.append(f"{k} ({b}, [{lo}, {hi}]) · {u} ({ub}) · {g} [{fh}]")
        P(f"| {a} | raw_FX{x} | " + " | ".join(cells) + " |")
        K[p, a] = [T[x][s, a][0] for s in HS]; U[p, a] = [SPL[x][s, a][1] for s in HS]
    g = {x: [T[x][s, "R5-genie"][0] for s in HS] for x in T}
    P(f"\nPerfect CSI (R5-genie) 의 실패 수는 세 raw 에서 같다: " + " · ".join(f"FX{x} {v}" for x, v in g.items()) + f" → {'동일' if len({tuple(v) for v in g.values()}) == 1 else '**다름**'}. "
      "\"본 시행\" 의 수는 ALD-pilot 을 뺀 모든 arm 에서 n = 20480 raw 의 수와 같다(assert); ALD-pilot 은 새 사후 표본이라 다를 수 있다(등록 머리말 '시행').")
    zero = [f"{a} {s:+d} dB" for a in ORDER for s, k in zip(HS, K[p, a]) if k == 0]
    P(f"\n0 실패 점 (n = 81920): {', '.join(zero) if zero else '없음'}.")
    RIS[p] = [l.strip() for l in rec.split("\n") if "rising:" in l]
    P(f"\n그림 기록 `records/paper_f21{p.lower()}hsx.txt` 의 '오르는 칸' (한쪽 Fisher p; 보고만): {len(RIS[p])} 줄." + f" y 축 {re.search(r'y log (\([^)]*\))', rec)[1]}.")
    for l in RIS[p]:
        P(f"- `{l}`")

P("\n### 6.3 §3 예측 채점 (n = 81920 으로 채점; 괄호 안의 둘째 수는 보지 않은 61440 시행만의 수)\n")
hit = lambda c: "적중" if c else "빗나감"
V, B, GE = "M-ours-dscore-C-V1", "M-ours-bstar", "R5-genie"
def rise_p(p, a):
    return [float(x) for l in RIS[p] if l.split("@16")[0].strip() == a for x in re.findall(r"p=([\d.e+-]+)", l.split("rising:")[1])]
for p, i in ((q, {"SRB": 1, "SRP": 5}[q]) for q in PRS):
    P(f"{i}. {p}: V1 의 실패 수 +15 dB ≤ +12 dB → **{hit(K[p, V][1] <= K[p, V][0])}** ({K[p, V][0]} → {K[p, V][1]}; 보지 않은 시행 {U[p, V][0]} → {U[p, V][1]}).")
    if p == "SRB":
        r2 = {a: rise_p(p, a) for a in (V, B, GE)}
        P(f"2. SRB: V1 · b\\* · Perfect CSI 에 Fisher p < 0.05 인 오르는 칸 없음 → **{hit(all(x >= 0.05 for v in r2.values() for x in v))}** "
          f"(오르는 칸의 p: {', '.join(f'{a} {v if v else NONE}' for a, v in r2.items())}).")
    j = 3 if p == "SRB" else 6
    for q, s in zip("ab", (0, 1)):
        P(f"{j}{q}. {p}: {HS[s]:+d} dB 에서 실패 수 V1 ≤ b\\* → **{hit(K[p, V][s] <= K[p, B][s])}** ({K[p, V][s]} 대 {K[p, B][s]}; 보지 않은 시행 {U[p, V][s]} 대 {U[p, B][s]}).")
    if p == "SRB":
        P(f"4a. SRB: V1 의 +12 dB 실패 수가 5..35 → **{hit(5 <= K[p, V][0] <= 35)}** ({K[p, V][0]}).")
        P(f"4b. SRB: V1 의 +15 dB 실패 수가 7..41 → **{hit(7 <= K[p, V][1] <= 41)}** ({K[p, V][1]}).")
acc6 = [t for t in TAGS if open(f"{RV}/{t}_accept.txt", encoding="utf-8").read().startswith(f"ACCEPT: OK -- {t}")] if done else []
P(f"7. 여섯 행 모두 대조·수용 통과(`FIGHS_DONE ok=6 fail=0`) → **{hit((OKN, FAILN) == (6, 0) and len(starts) == 1)}** (첫 실행의 종료 줄 ok={OKN} fail={FAILN}; "
  f"시작 줄 {len(starts)} 개; 재개까지 마친 뒤 수용 파일이 `ACCEPT: OK` 인 행 {len(acc6)} / {len(TAGS)} — 엄격 채점: 한 번의 실행으로 ok=6 이 아니면 빗나감).")
ov = open(sys.argv[1], encoding="utf-8").read().strip().split("\n")
P(f"8. 처음 20480 시행이 `raw_FH*` 와 비트 동일(ALD-pilot 제외) → **{hit(ov[-1] == 'OVERLAP: OK' and sum(l.startswith('raw_FX') for l in ov) == 3 * len(PRS))}** "
  "(작성자의 확인 `prereg_audit_2026-10-11/fx_overlap_check.py`; 기록 감사가 따로 확인한다):")
for l in ov:
    P(f"   - `{l}`")
print("\n".join(out))
