#!/usr/bin/env python
"""s6_seedsroom_gen.py -- NEXT_EXPERIMENTS_SEEDSROOM16e4 §6.1 transcription generator.  Every number is read from a record:
  logs/run_seedsroom16e4.log, logs/run_seeds16e4_<TAG>.log, logs/run_D2_<TAG>.log     start / done lines, runner minutes
  results/tables_D2_<TAG>.txt            table B block `M-ours-bstar -> M-ours-dscore-C-V1` (decision SNRs, a:b, p, power guard, gap)
  results/review_next/recovery_<TAG>.txt R(-3 dB) and R(decision points) with their 90% paired CIs; b* / V1 / genie failure counts
  results/review_next/<TAG>_accept.txt, <TAG>_refarms.txt, run_manifest_<TAG>.json, results/guard_D2_<TAG>.txt
  logs/seeds_<PRIOR>_train.log           the report-only GB' lines of the seed checkpoints
The a1 tags (SRBB16e4, SRPB16e4) are parsed with the same code for the first row of each pool.  It does NOT read the raws.
Usage (cwd = ~/t2/conf):  python -B .../s6_seedsroom_gen.py [SRB|SRP ...] > <draft>.md      (a prior list = partial draft)
"""
import json, re, sys

sys.path.insert(0, "code")
from hisnr_report import wilson

RV = "results/review_next"
PRS = sys.argv[1:] or ["SRB", "SRP"]
QUAL = {"SRB": "", "SRP": "; b* = 씨앗 초기화 GMM"}
out = []
def P(*a): out.append(" ".join(str(x) for x in a))


def tab(tag):
    """table B `b* -> V1` of tables_D2_<tag>.txt -> dict"""
    t = open(f"results/tables_D2_{tag}.txt", encoding="utf-8").read()
    m = re.search(r"  M-ours-bstar -> M-ours-dscore-C-V1 .*?\n(.*?)\n  M-ours-bstar -> ", t, re.S)
    b = m[1]
    dp = [x.strip("' ") for x in re.search(r"decision SNRs \[([^\]]*)\]", b)[1].split(",")]
    pts = re.findall(r"([+-]\d+) dB (\d+):(\d+) p=(\S+)", b.split("pooled")[0])
    pool = re.search(r"pooled (\d+):(\d+) p=(\S+)", b)
    pw = re.search(r"power guard: (\d+) decision points, (\d+) with >= 6 discordant pairs -> (\w+)", b)
    sg = re.search(r"second arm fewer failures at (\d)/(\d) points, first arm fewer failures at (\d)/(\d) points", b)
    gap = re.search(r"SNR@0.1 gap \(M-ours-bstar minus M-ours-dscore-C-V1\): (\S+) dB\s+\[90% paired bootstrap (\S+), (\S+);", b)
    powered = pw[3] == "POWERED"
    v, f, n = int(sg[1]), int(sg[3]), int(sg[2])
    lab = "(iv)" if not powered else "(i)" if 3 * v >= 2 * n else "(ii)" if 3 * f >= 2 * n else "(iii)"   # 08_SPEC §2: >= 2/3 of the points
    return dict(dp=dp, pts=pts, pool=pool.groups(), power=pw.groups(), v=v, f=f, n=n, lab=lab, gap=gap.groups() if gap else None)


def rec(tag):
    """recovery_<tag>.txt -> ({snr: (b*, V1, genie, R, lo, hi)} of the decision-point block, the pooled-3 line)"""
    L = open(f"{RV}/recovery_{tag}.txt", encoding="utf-8").read().split("# recovery")[-1].split("\n")
    r = {}
    for l in L:
        m = re.match(r"\s+([+-]\d+) dB\s+b\* (\d+)\s+V1 (\d+)\s+genie (\d+)\s+n=2560\s+R = (\S+)\s+\[90% (\S+), (\S+)\]", l)
        if m:
            r[m[1]] = (int(m[2]), int(m[3]), int(m[4]), m[5], m[6], m[7])
        m = re.match(r"\s+pooled (\d) SNRs\s+b\* (\d+)\s+V1 (\d+)\s+genie (\d+)\s+R = (\S+)\s+\[90% (\S+), (\S+)\]", l)
        if m:
            pooled = m.groups()
    return r, pooled


LOG = [l for l in open("logs/run_seedsroom16e4.log", encoding="utf-8", errors="replace").read().split("\n") if l.startswith("[seedsroom ")]
P("### 6.1 결과 (생성기 `prereg_audit_2026-10-11/s6_seedsroom_gen.py`; 수치는 모두 기록 파일에서 읽음 — 전사만, 해석 없음)\n")
P("**실행·수용** — 드라이버 로그 `logs/run_seedsroom16e4.log` 의 시작 · 태그 종료 · 끝 줄(원문):\n")
for l in LOG:
    if re.search(r"start \(git|done:|NOT accepted|SEEDSROOM_DONE|ABORT", l):
        P(f"- `{l[:250]}`")
P("\n| 태그 | runner | 수용 | `--ref-arms all` (점 7 개의 '다른 arm' 집합) | manifest git · config_hash |")
P("|---|---|---|---|---|")
T, R, G = {}, {}, {}
for p in PRS:
    for s in (2, 3):
        t = f"{p}B16e4s{s}"
        rl = open(f"logs/run_D2_{t}.log", encoding="utf-8", errors="replace").read()
        mins = re.findall(r"\[run\] finished in ([\d.]+) min", rl); tasks = re.findall(r"-> (\d+) tasks on (\d+) workers", rl)
        acc = open(f"{RV}/{t}_accept.txt", encoding="utf-8").read().split("\n")[0]
        ra = sorted(set(re.findall(r"arms differing (\[[^\]]*\])", open(f"{RV}/{t}_refarms.txt", encoding="utf-8").read())))
        sh = sorted(set(re.findall(r"shared (\d+/\d+)", open(f"{RV}/{t}_refarms.txt", encoding="utf-8").read())))
        man = json.load(open(f"{RV}/run_manifest_{t}.json"))
        P(f"| {t} | {mins[0]} 분 · {tasks[0][0]} 작업 · {tasks[0][1]} 워커 (96 스레드에 묶음) | `{acc}` | shared {' '.join(sh)}; {' '.join(ra)} | {man.get('git_commit', '?')} · {man.get('config_hash', '?')} |")

P("\n| 태그 | 표 B `b* → V1` 판정점 a:b (p) · pooled (p) | 가드 · 방향 | 라벨 | SNR@0.1 격차 b\\*−V1 [90 %] | V1 −3 dB BLER (95 % Wilson) | b\\* · genie −3 dB 실패 수 | R (−3 dB) [90 %] | R (판정점 합) [90 %] |")
P("|---|---|---|---|---|---|---|---|---|")
for p in PRS:
    for s in (1, 2, 3):
        t = f"{p}B16e4" + ("" if s == 1 else f"s{s}")
        T[p, s], (R[p, s], pooled) = tab(t), rec(t)
        x = T[p, s]
        assert x["dp"] == ["-3", "+0", "+3"], (t, x["dp"])                    # the decision points of a1 (acceptance)
        b, v, g, r3, lo, hi = R[p, s]["-3"]
        wl, wh = wilson(v, 2560)
        assert (b, g) == R[p, 1]["-3"][:1] + R[p, 1]["-3"][2:3], (t, b, g)     # b* and genie = the a1 raw's (bit-identical arms)
        P(f"| {p} a{s} ({t}{'; §0 인용' if s == 1 else ''}) | " + " · ".join(f"{a}:{c} ({q})" for _, a, c, q in x["pts"]) + f" · {x['pool'][0]}:{x['pool'][1]} ({x['pool'][2]}) | "
          f"{x['power'][2]} ({x['power'][1]}/{x['power'][0]}), V1 {x['v']}/{x['n']} · b\\* {x['f']}/{x['n']} | {'**' + x['lab'] + '**' if s > 1 else x['lab']} | "
          + (f"{x['gap'][0]} [{x['gap'][1]}, {x['gap'][2]}]" if x["gap"] else "n/a") + f" | {v / 2560:.3f} ({wl:.3f}, {wh:.3f}), {v}/2560 | {b} · {g} | {r3} [{lo}, {hi}] | "
          f"{pooled[4]} [{pooled[5]}, {pooled[6]}] |")

P("\n**시드 강건성 라벨 (§1; 분모 3 = a1·a2·a3)**:")
AGG = {}
for p in PRS:
    labs = [T[p, s]["lab"] for s in (1, 2, 3)]
    k, m, j = labs.count("(i)"), sum(l in ("(ii)", "(iii)") for l in labs), labs.count("(iv)")
    AGG[p] = (f"시드 강건 (3/3 (i){QUAL[p]})" if k == 3 else f"시드 의존 ({k}/3 (i), {m} 다름{QUAL[p]})" if m else f"판정하지 못함 ({k}/3 (i), {j} 판정 못함{QUAL[p]})")
    P(f"- **{p}: \"{AGG[p]}\"** (시드별 라벨 a1 {labs[0]} · a2 {labs[1]} · a3 {labs[2]}).")

P("\n**보고 전용**:")
for p in PRS:
    gaps = [float(T[p, s]["gap"][0]) for s in (1, 2, 3)]; v3 = [R[p, s]["-3"][1] for s in (1, 2, 3)]; r3 = [float(R[p, s]["-3"][3]) for s in (1, 2, 3)]
    P(f"- {p} 시드 간 산포 (a1 / a2 / a3; max − min): SNR@0.1 격차 {' / '.join(f'{x:+.2f}' for x in gaps)} dB ({max(gaps) - min(gaps):.2f}); V1 −3 dB 실패 수 {' / '.join(map(str, v3))} ({max(v3) - min(v3)}); "
      f"R(−3 dB) {' / '.join(f'{x:.3f}' for x in r3)} ({max(r3) - min(r3):.3f}).")
    gl = [l for l in open(f"logs/seeds_{p}_train.log", encoding="utf-8").read().split("\n") if "GB' rc=" in l]
    for l in gl:
        m = re.search(r"\[seeds (\S+ \S+) CDT\] (\S+ a\d) GB' rc=(\d+) \(.*?GMM b\* = (.*?) @N=160000 \| diff/gmm min (\S+) max (\S+) median (\S+) \|", l)
        if m:
            P(f"  - 동일예산 GB′ {m[2]} ({m[1]} CDT, rc {m[3]}; b\\* {m[4]}): median {m[7]} (min {m[5]} · max {m[6]}).")
    for s in (2, 3):
        t = f"{p}B16e4s{s}"
        g = [l.strip() for l in open(f"results/guard_D2_{t}.txt", encoding="utf-8").read().split("\n") if "M-ours-dscore-C-V0" in l][:1]
        P(f"  - V0 가드 ({t}; `results/guard_D2_{t}.txt`): `{g[0][:200] if g else '줄 없음'}`")

P("\n**§3 예측 채점**:")
hit = lambda c: "적중" if c else "빗나감"
W = {"SRB": (0.258, 0.293), "SRP": (0.299, 0.335)}; GC = {"SRB": (0.18, 0.45), "SRP": (1.78, 2.24)}
for p, i in ((q, {"SRB": 1, "SRP": 4}[q]) for q in PRS):
    labs = [T[p, s]["lab"] for s in (2, 3)]
    P(f"{i}. {p} a2·a3 표 B 모두 (i) → **{hit(labs == ['(i)', '(i)'])}** ({labs[0]} · {labs[1]}; 집계 \"{AGG[p]}\").")
    bl = [round(R[p, s]["-3"][1] / 2560, 3) for s in (2, 3)]
    P(f"{i + 1}. {p} V1 −3 dB BLER 이 a1 의 95 % Wilson CI [{W[p][0]:.3f}, {W[p][1]:.3f}] 안 → **{hit(all(W[p][0] <= x <= W[p][1] for x in bl))}** ({bl[0]:.3f} · {bl[1]:.3f}).")
    ov = [(float(T[p, s]["gap"][1]), float(T[p, s]["gap"][2])) for s in (2, 3)]
    P(f"{i + 2}. {p} SNR@0.1 격차의 90 % CI 가 a1 의 [{GC[p][0]:+.2f}, {GC[p][1]:+.2f}] 와 겹침 → **{hit(all(lo <= GC[p][1] and hi >= GC[p][0] for lo, hi in ov))}** "
      f"([{ov[0][0]:+.2f}, {ov[0][1]:+.2f}] · [{ov[1][0]:+.2f}, {ov[1][1]:+.2f}]).")
done = [l for l in LOG if "SEEDSROOM_DONE" in l]
if done:
    m = re.search(r"SEEDSROOM_DONE ok=(\d+) fail=(\d+)", done[-1])
    P(f"7. 네 태그 모두 수용 통과(`SEEDSROOM_DONE ok=4 fail=0`), 다른 arm ⊆ {{V0, V1, V4, V4b}} → **{hit(m.groups() == ('4', '0') and len(done) == 1)}** (`{done[-1].split('] ')[1]}`).")
P("8. (채점 제외 — 경로 설명.)")
print("\n".join(out))
