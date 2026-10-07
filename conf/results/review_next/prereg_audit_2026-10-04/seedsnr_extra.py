#!/usr/bin/env python
"""prereg_audit_2026-10-04/seedsnr_extra.py -- text-level checks for the SEEDSNR16e4 §6.1 record audit (read-only):
§5 addendum vs §6.1.7 fb3 disclosure, batch-1 vs batch-2 log strings, interpretive vocabulary, placeholders, stale §0-§5
cells, cited table lines, EXPERIMENTS/DECISIONS strings, file mtimes."""
import re, os, subprocess, difflib
from datetime import datetime, timezone, timedelta
CONF = "/home/HTJ/t2_wtS/conf"; os.chdir(CONF)
RN = f"{CONF}/results/review_next"
doc = open(f"{RN}/NEXT_EXPERIMENTS_SEEDSNR16e4.md").read().split("\n")
app = doc[157:339]
exp = open("../docs/EXPERIMENTS.md").read().split("\n")
dec = open("DECISIONS.md").read().split("\n")
n = 0; bad = 0
def chk(name, ok, detail=""):
    global n, bad
    n += 1; bad += (not ok)
    print(("  OK   " if ok else "  FAIL ") + name + (f" -- {detail}" if detail else ""))

print("== fb3 disclosure: §5 addendum (:138) vs §6.1.7 (:330)")
a, b = doc[137], doc[329]
ca, cb = a[a.index("§1 은 fb3"):], b[b.index("§1 은 fb3"):]
tail_a = "§6 에도 같은 공개를 적는다."; tail_b = "(이 기록자는 fb3 로그·체크포인트를 열지 않았다.)"
chk("§6.1.7 text = §5 text with only the closing sentence replaced", ca.replace(tail_a, "") == cb.replace(tail_b, ""), f"{len(ca)} vs {len(cb)} chars")
ta = re.findall(r"10-0\d \d\d:\d\d CDT", a); tb = re.findall(r"10-0\d \d\d:\d\d CDT", b)
chk("same 18 CDT times in both", ta == tb and len(ta) == 18)
before = [t for t in ta[1:11]]; after = ta[11:15]
chk("10 before-freeze times all < 22:59:56 (freeze)", all(t < "10-03 22:59" for t in before), str(before))
chk("4 after-freeze times all > freeze and < fb2 decision 01:56", all("10-03 23:00" < t < "10-04 01:56" for t in after), str(after))
chk("design-subagent read 03:27 after SIGINT 02:24", ta[15] == "10-04 03:27 CDT" and ta[17] == "10-04 02:24 CDT")
chk("count 10 + 4 = 14 as stated", "14 회" in b and "동결 전 10 회" in b and "동결 뒤 4 회" in b)
msg = subprocess.run(["git", "log", "-1", "--format=%B", "b53a8529"], capture_output=True, text=True).stdout
chk("commit b53a8529 message carries the same count (14: 10·4, design 1)", "브리핑 14 회: 동결 전 10·뒤 4, 설계 서브에이전트 1 회" in msg)
sched = open("logs/gpu_sched.log").read().split("\n")
chk("gpu_sched.log:92 fb2 done rc=0 10-04 01:56", sched[91].startswith("[sched 10-04 01:56 CDT] done rc=0 job_g0") and "--fallback 2" in sched[91])
chk("gpu_sched.log:93-94 fb3 end 10-04 02:24 (SIGINT, main-session line)", sched[92].startswith("[sched 10-04 02:24 CDT] done rc=0 job_g1") and "--fallback 3" in sched[92] and "fb3 SIGINTed" in sched[93])
print("  NOTE gpu_sched.log:94 (02:24 CDT) says fb3 'NOT opened (log/ckpt not read)'; the §5 addendum (17:36 CDT) later disclosed 14 briefing tail reads, all before 02:24.")

print("== batch 1 vs batch 2 post-run log strings (timestamps stripped, manifest git_commit masked)")
L = open("logs/run_seedsnr16e4.log").read().split("\n")
st = lambda s: re.sub(r"^\[seedsnr \d\d-\d\d \d\d:\d\d CDT\] ", "", s)
diffs = 0
for a1, b1 in [(6, 72), (18, 84), (30, 96), (42, 108), (54, 120)]:
    for k in range(10):
        x, y = L[a1 - 1 + k], L[b1 - 1 + k]
        if x.startswith("{"):
            x = x.replace('"git_commit": "d59b4c6c"', "G"); y = y.replace('"git_commit": "b53a8529"', "G")
        diffs += st(x) != st(y)
chk("50 line pairs identical", diffs == 0, f"diffs {diffs}")

print("== interpretive vocabulary / placeholders in the appended text (§6.1 :158-339, EXPERIMENTS:59, DECISIONS:315)")
text = "\n".join(app) + "\n" + exp[58] + "\n" + dec[314]
words = ["유의하게", "우수", "개선", "여지", "headroom", "비긴다", "significant", "입증", "따라서", "시사", "보여준다", "운이 좋", "결론", "증명", "확인된다", "뒷받침"]
hits = {w: text.count(w) for w in words if text.count(w)}
chk("interpretive vocabulary absent", not hits, str(hits))
ctx = {w: [m.group(0) for m in re.finditer(r".{0,25}" + w + r".{0,25}", text)] for w in ("최적", "동등", "해석", "강건성")}
for w, c in ctx.items():
    print(f"   context {w!r}: {c}")
chk("'최적' only inside the quoted G_d strings", all("최적 GMM 이 아니다" in c for c in ctx["최적"]))
chk("'동등' only as '동등성은 주장하지 않는다' (§1 wording)", all("동등성은 주장하지 않는다" in c for c in ctx["동등"]))
chk("no placeholders (x CDT / __NOW / TODO)", not re.search(r"x CDT|__NOW|TODO|XXX", text))
tbd = [l for l in app if "TBD" in l]
chk("'TBD' only when quoting §5's own TBD cell", all("실행 커밋 1·2 해시: TBD" in l for l in tbd) and len(tbd) == 2)

print("== §0-§5 stale cells named in §6.1.7 exist as quoted")
chk("§0 :30 'a3 fb2 [학습 중]'", "a3 fb2 [학습 중]" in doc[29])
chk("§4.1 :101-102 '진행 중'", "진행 중" in doc[100] and "진행 중" in doc[101])
chk("§4.3 :120 '대기'", doc[119].rstrip().endswith("| 대기 |"))
chk("§5 :139 'TBD'", "실행 커밋 1·2 해시: TBD" in doc[138])

print("== cited table lines")
for T in ["U28NR16B16e4s2", "U28NR16B16e4s3", "U28NR32B16e4s2", "U28NR32B16e4s3", "NR32B16e4s2", "NR32B16e4s3"]:
    tab = open(f"results/tables_D2_{T}.txt").read().split("\n")
    chk(f"{T} :32 = R3-bigamp N_train=0 (record cites :29-36 as N_train=160000 lines)", tab[31].startswith("#   R3-bigamp") and "N_train=0" in tab[31])
    chk(f"{T} :29-31,33-36,41 N_train=160000", all("N_train=160000" in tab[j] for j in (28, 29, 30, 32, 33, 34, 35, 40)))
    chk(f"{T} :38 V1 budget", ("N_train=28160000" if "U28" in T else "N_train=160000") in tab[37])
    chk(f"{T} :47 stagec_ckpt_id", tab[46].startswith("#   stagec_ckpt_id"))
    chk(f"{T} :49 raw run params git", ("git=d59b4c6c" if T != "NR32B16e4s3" else "git=b53a8529") in tab[48])
    bl = 260 if "U28" in T else 257
    chk(f"{T} :{bl}-{bl + 5} b*->V1 block", tab[bl - 1].startswith("  M-ours-bstar -> M-ours-dscore-C-V1") and tab[bl].startswith("    decision SNRs") and tab[bl + 4].startswith("    SNR@0.1 gap (M-ours-bstar minus M-ours-dscore-C-V1)"))
    v1 = 74 if "U28" in T else 71
    chk(f"{T} :{v1} table A V1 row, :{v1 - 1} b*, :{v1 + 2} genie", tab[v1 - 1].startswith("  M-ours-dscore-C-V1") and tab[v1 - 2].startswith("  M-ours-bstar ") and tab[v1 + 1].startswith("  R5-genie"))
for T in ["U28NR16B16e4", "U28NR32B16e4"]:
    chk(f"a1 {T} :38 N_train=28160000 (same display as seed tags)", "N_train=28160000" in open(f"results/tables_D2_{T}.txt").read().split("\n")[37])
chk("SEEDS16e4 tab_U28B16e4s2:38 N_train=28160000", "N_train=28160000" in open("results/tables_D2_U28B16e4s2.txt").read().split("\n")[37])

print("== EXPERIMENTS row / DECISIONS line")
row = exp[58]
chk("EXPERIMENTS :59 has 8 columns", row.replace("\\|", "").count("|") == 9)
chk("EXPERIMENTS :59 KST range = CDT + 14 h", "2026-10-04 13:03 ~ 10-05 12:53 KST (텍사스 10-03 23:03 ~ 10-04 22:53 CDT)" in row)
for s in ["ok=47 fail=0", "ok=51 fail=0", "230:54 · 238:47", "403:35 · 398:27", "909:22 · 899:31", "0.269 / 0.292 (a1 0.287)", "0.443 / 0.446 (a1 0.432)", "0.813 / 0.796 (a1 0.811)",
          "+0.256·+0.239", "+0.243·+0.247", "+0.064·+0.085", "d59b4c6c", "b53a8529", "cd85bef1", "적중 10·빗나감 2", "18 h 31 min", "5 h 17 min", "jobs 98"]:
    chk(f"EXPERIMENTS :59 contains {s!r}", s in row)
d = dec[314]
chk("DECISIONS :315 KST/CDT", d.startswith("`[2026-10-05 13:09 KST] SEEDSNR16e4 결과 기록") and "텍사스 10-04 23:09 CDT" in d)
for s in ["10-03 23:03 ~ 10-04 17:34 CDT", "17:36 ~ 22:53 CDT", "ok=47 fail=0", "ok=51 fail=0", "1 묶음 6 개 d59b4c6c, 2 묶음 2 개 b53a8529", "jobs 99 (UMi28 C9)·98 (D2 C9)",
          "시드 강건 (3/3 (i); a3 = §3d fb2)", "판정하지 못함 (2/3 (i), 1 판정 못함)", "적중 10·빗나감 2 (3: 문자열 한정어, 9)", "14 회 — 동결 전 10·뒤 4, 설계 서브에이전트 1 회"]:
    chk(f"DECISIONS :315 contains {s!r}", s in d)
chk("DECISIONS :314 blank, :313 = freeze line", dec[313] == "" and dec[312].startswith("`[2026-10-04 12:59 KST] 동결 — SEEDSNR16e4 v2"))

print("== mtimes (KST) of the three edited files vs recorded 13:09 KST")
kst = timezone(timedelta(hours=9))
for f in [f"{RN}/NEXT_EXPERIMENTS_SEEDSNR16e4.md", "../docs/EXPERIMENTS.md", "DECISIONS.md"]:
    m = datetime.fromtimestamp(os.stat(f).st_mtime, kst).strftime("%Y-%m-%d %H:%M")
    chk(f"mtime {os.path.basename(f)} = 2026-10-05 13:09 KST", m == "2026-10-05 13:09", m)
print(f"TOTAL {n} checks, failures {bad}")
