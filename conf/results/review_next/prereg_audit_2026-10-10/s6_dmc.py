"""s6_dmc.py -- NEXT_EXPERIMENTS_DMC16e4 §6 transcription generator: every number is read from a record, never typed.
  logs/run_prior_eval_DMCB16e4.log, logs/run_D2_<TAG>.log     run lines (CDT), runner minutes
  results/tables_D2_<TAG>.txt                                table B blocks (verbatim)
  results/review_next/{<TAG>_accept, recovery_<TAG>, recovery_diff_<TAG>}.txt, results/guard_D2_<TAG>.txt  (verbatim)
  raw_<TAG>                                                  BLER / failure counts, best vs last V1 sign test (analysis.load_raw)
Usage (cwd = ~/t2/conf):  CUDA_VISIBLE_DEVICES= python s6_dmc.py > s6_draft_raw.md
"""
import os, re, sys

sys.path.insert(0, "code")
import numpy as np
from scipy.stats import binomtest
from analysis import load_raw
from recovery_ci import fails

T, RV, CELL = "DMCB16e4", "results/review_next", "C2"
SN = [-3.0, 0.0, 3.0, 6.0, 9.0, 12.0, 15.0]
PAIRS = ["M-ours-bstar -> M-ours-dscore-C-V1", "M-ours-bstar -> M-ours-bstar-scalar", "R2-ours-G -> M-ours-bstar",
         "M-ours-bstar -> M-ours-dscore-C-V4", "M-ours-bstar -> M-ours-dscore-C-V4b", "M-ours-bstar -> M-ours-dscore-C-V0",
         "M-ours-dscore-C-V1 -> R5-genie", "M-ours-bstar -> R5-genie"]


def cat(p, n=None):
    print(f"\n----- {p}")
    try:
        L = open(p, encoding="utf-8", errors="replace").read().rstrip("\n").split("\n")
        print("\n".join(L[:n] if n else L))
    except FileNotFoundError:
        print("(missing)")


print("## run log")
print("".join(l for l in open(f"logs/run_prior_eval_{T}.log") if l.startswith("[prior_eval")).rstrip())
for t in (T, T + "last"):
    L = open(f"logs/run_D2_{t}.log", encoding="utf-8", errors="replace").read().split("\n")
    print(t, [l for l in L if l.startswith("[run]")])
    print(f"{t} tables head:", open(f"results/tables_D2_{t}.txt").read().split("\n")[:2])

print("\n## table B blocks")
for t in (T, T + "last"):
    txt = open(f"results/tables_D2_{t}.txt").read()
    for p in PAIRS:
        m = re.search(r"^  " + re.escape(p) + r" .*?\n((?:    .*\n){5})", txt, re.M)
        print(f"[{t}] {p}\n{m[1].rstrip() if m else '    (absent)'}")

data = {t: load_raw("D2", root=f"raw_{t}")[0] for t in (T, T + "last")}
arms = sorted({a for k in data[T] if k[0] == CELL for a in data[T][k] if isinstance(data[T][k][a], dict) and "blk_err" in data[T][k][a]})
print("\n## BLER@16 (R0-pilot also @1) and failure counts, tag", T, " SNR", SN)
for a in arms:
    f = [fails(data[T], CELL, s, a) for s in SN]
    print(f"{a:22s} BLER " + " / ".join(f"{x.mean():.3f}" for x in f) + "   fails " + " / ".join(str(int(x.sum())) for x in f) + f"   n {len(f[0])}")
f = [fails(data[T], CELL, s, "R0-pilot", 0) for s in SN]
print(f"{'R0-pilot (@1)':22s} BLER " + " / ".join(f"{x.mean():.3f}" for x in f) + "   fails " + " / ".join(str(int(x.sum())) for x in f))
f = [fails(data[T + "last"], CELL, s, "M-ours-dscore-C-V1") for s in SN]
print(f"{'V1 (last tag)':22s} BLER " + " / ".join(f"{x.mean():.3f}" for x in f) + "   fails " + " / ".join(str(int(x.sum())) for x in f))

m = re.search(r"M-ours-bstar -> M-ours-dscore-C-V1.*?\n\s*decision SNRs \[([^\]]*)\]", open(f"results/tables_D2_{T}.txt").read(), re.S)
dp = [float(x.strip("' ")) for x in m[1].split(",")]
print("\n## best vs last V1, paired exact two-sided sign test at the decision SNRs", dp, "(a = only best fails, b = only last fails)")
A = B = 0
for s in dp:
    x, y = fails(data[T], CELL, s, "M-ours-dscore-C-V1"), fails(data[T + "last"], CELL, s, "M-ours-dscore-C-V1")
    a, b = int(((x == 1) & (y == 0)).sum()), int(((x == 0) & (y == 1)).sum())
    A += a; B += b
    print(f"  {s:+.0f} dB {a}:{b} p={binomtest(a, a + b, 0.5).pvalue if a + b else 1:.3g}")
print(f"  pooled {A}:{B} p={binomtest(A, A + B, 0.5).pvalue if A + B else 1:.3g}")

for p in (f"{RV}/{T}_accept.txt", f"{RV}/recovery_{T}.txt", f"{RV}/recovery_{T}last.txt", f"{RV}/recovery_diff_{T}.txt",
          f"results/guard_D2_{T}.txt", f"results/guard_D2_{T}last.txt", f"{RV}/{T}_leak_strata.txt"):
    cat(p, 60)
for t in (T, T + "last"):
    p = f"{RV}/run_manifest_{t}.json"
    print(p, "exists" if os.path.exists(p) else "MISSING", re.findall(r'"(?:git|config_hash)[^"]*": "[^"]*"', open(p).read())[:4] if os.path.exists(p) else "")
