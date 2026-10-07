#!/usr/bin/env python3
"""s6_gen.py -- NSCALE §6 (결과 전사) 초안 생성기.  스크래치 전용 (커밋하지 않는다).

파일만 읽는다: run_nscale.sh eval 산출물 (logs/run_nscale.log, logs/run_D2_<T>.log, logs/analysis_<T>.log, results/tables_D2_<T>.txt,
results/guard_D2_<T>.txt, results/review_next/{nscale_*.txt, <K>_accept.txt, recovery_<T>.txt, run_manifest_<T>.json}), S5·prep
(results/nscale/nscale_{s5,prep}.txt), 등록 문서, raw_<T>/ 의 meta·run 키와 best/last V1 blk_err, fits npz 의 n_iter/it_best, git (읽기 전용),
date.  손으로 친 숫자·시각은 없다 (등록 문서의 규칙 상수 — 범위·임계 — 는 등록 줄 번호와 함께 쓰고, 그 줄에 같은 문자열이 있는지 검사한다).
숫자마다 출처 `파일:줄` 을 붙이고, 판단이 필요한 자리는 [판단 필요: …], 없는 입력은 **[입력 없음: …]** 으로 남긴다 (중단하지 않는다).

  CUDA_VISIBLE_DEVICES= ~/miniforge3/envs/torch/bin/python s6_gen.py OUT.md [--conf /home/HTJ/t2/conf] [--author "…"]
  CUDA_VISIBLE_DEVICES= ~/miniforge3/envs/torch/bin/python s6_gen.py --selftest      (SCALE16e4·B32e4 기록 출력으로 파서 검사 + 가짜 트리 끝-끝)
"""
import argparse, datetime as dt, glob, hashlib, json, os, re, subprocess, sys
from math import comb

os.environ["CUDA_VISIBLE_DEVICES"] = ""
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REG = "results/review_next/NEXT_EXPERIMENTS_NSCALE.md"
S5R, PREPR, LOGR, RV = "results/nscale/nscale_s5.txt", "results/nscale/nscale_prep.txt", "logs/run_nscale.log", "results/review_next"
NEWPTS = (("B64e4", "C2", 640000), ("B128e4", "C2", 1280000), ("NR16B64e4", "C6", 640000))
BASE = {"C2": dict(tag="B32e4", n=320000, br="BRB32e4", k2="K2B32e4", nr=8),
        "C6": dict(tag="NR16B16e4", n=160000, br="BRNR16B16e4", k2="K2NR16B16e4", nr=16)}
NEWRAW = ("BRB32e4 BRNR16B16e4 B64e4 B128e4 B64e4chk B128e4chk B64e4last B128e4last K2B32e4 K2B64e4 K2B128e4 "
          "NR16B64e4 NR16B64e4chk NR16B64e4last K2NR16B64e4 B64e4k8").split()
V1, BS, BSS, GE = "M-ours-dscore-C-V1", "M-ours-bstar", "M-ours-bstar-scalar", "R5-genie"
PV1, PSC = f"{BS} -> {V1}", f"{BS} -> {BSS}"
MARKS = []


# ====================================================================== small helpers
def miss(rel, why=""):
    MARKS.append(("입력 없음", rel + (f" — {why}" if why else "")))
    return f"**[입력 없음: `{rel}`" + (f" — {why}" if why else "") + "]**"


def judge(text):
    MARKS.append(("판단 필요", text))
    return f"**[판단 필요: {text}]**"


def badfmt(rel, n, what):
    MARKS.append(("형식 불일치", f"{rel}:{n} {what}"))
    return f"**[형식 불일치: `{short(rel)}:{n}` — {what}]**"


def esc(s):
    return str(s).replace("|", "\\|")


def fl(s):
    try:
        return float(str(s).replace("−", "-"))
    except (TypeError, ValueError):
        return float("nan")


def nf(n):                                              # 640000 -> 6.4e5 (the registration's notation)
    m, e = f"{int(n):.3g}".split("e+")
    return f"{m}e{int(e)}"


def lab(lo, hi):
    return "(T+)" if lo > 0 else "(T−)" if hi < 0 else "(T0)"


def sign_p(a, b):                                       # exp_0921_analysis.sign_p (exact two-sided)
    n = a + b
    return 1.0 if n == 0 else min(1.0, 2 * sum(comb(n, i) for i in range(min(a, b) + 1)) / 2 ** n)


def rx(b, v, g):                                        # R = (b - v)/(b - g), exact from the integer failure counts
    return (b - v) / (b - g) if b - g > 0 else float("nan")


_SHORT = ((r"logs/run_nscale\.log", "L"), (r"results/review_next/nscale_(.+)\.txt", r"\1"),
          (r"results/review_next/(.+)_accept\.txt", r"acc_\1"), (r"results/review_next/recovery_(.+)\.txt", r"rec_\1"),
          (r"results/review_next/run_manifest_(.+)\.json", r"man_\1"), (r"results/tables_D2_(.+)\.txt", r"tab_\1"),
          (r"results/guard_D2_(.+)\.txt", r"guard_\1"), (r"logs/run_D2_(.+)\.log", r"run_\1"), (r"logs/analysis_(.+)\.log", r"an_\1"),
          (r"results/nscale/nscale_s5\.txt", "S5"), (r"results/nscale/nscale_prep\.txt", "prep"), (re.escape(REG), "reg"))


def short(rel):
    for p, rep in _SHORT:
        if re.fullmatch(p, rel):
            return re.sub("^" + p + "$", rep, rel)
    return rel


def cite(rel, a=None, b=None):
    s = short(rel)
    return f"`{s}`" if a is None else f"`{s}:{a}`" if b is None or b == a else f"`{s}:{a}–{b}`"


class Files:
    def __init__(self, conf):
        self.conf, self.c = conf, {}

    def p(self, rel):
        return rel if os.path.isabs(rel) else os.path.join(self.conf, rel)

    def ex(self, rel):
        return os.path.exists(self.p(rel))

    def lines(self, rel):
        if rel not in self.c:
            try:
                with open(self.p(rel), errors="replace") as f:
                    self.c[rel] = f.read().split("\n")
            except OSError:
                self.c[rel] = None
        return self.c[rel]


def find(L, pat, start=0):                              # -> (1-based line, match) of the first match at index >= start
    for i in range(start, len(L or [])):
        m = re.search(pat, L[i])
        if m:
            return i + 1, m
    return None, None


def run(args, cwd=None, tz=None, raw=False):            # -> (rc, stdout) ; (None, '') when it cannot run
    try:
        r = subprocess.run(args, cwd=cwd, env=dict(os.environ, **({"TZ": tz} if tz else {})), capture_output=True, text=True, timeout=300)
        return r.returncode, (r.stdout if raw else r.stdout.rstrip("\n"))
    except (OSError, subprocess.SubprocessError):
        return None, ""


def date_now():
    return run(["date", "+%Y-%m-%d %H:%M %Z"], tz="America/Chicago")[1], run(["date", "+%m-%d %H:%M %Z"], tz="Asia/Seoul")[1]


def date_at(epoch):
    return run(["date", "-d", f"@{epoch}", "+%Y-%m-%d %H:%M:%S %Z"], tz="America/Chicago")[1]


def git(F, *a):
    rc, out = run(["git", *a], cwd=F.conf)
    return out if rc == 0 else None


# ====================================================================== parsers (one per output format)
PT_KEYS = "cell ntrain stem bsha lsha bs kk ll fk kr k2k k2ll ck gate".split()


def parse_s5(F):
    L = F.lines(S5R)
    if L is None:
        return None
    d = dict(PT={}, K8=None, FREEZE=None, FALLBACK=None, bad=[], k8c=None)
    for i, l in enumerate(L, 1):
        t = l.split()
        if not t:
            continue
        if t[0] == "#" and len(t) > 1 and t[1] == "K8":
            d["k8c"] = (l, i)
        if t[0].startswith("#"):
            continue
        if t[0] == "FREEZE" and len(t) == 2:
            d["FREEZE"] = (t[1], i)
        elif t[0] == "FALLBACK" and len(t) == 2:
            d["FALLBACK"] = (t[1], i)
        elif t[0] == "PT" and len(t) == 3 and t[2] == "-":
            d["PT"][t[1]] = dict(fail=True, ln=i)
        elif t[0] == "PT" and len(t) == 16:
            d["PT"][t[1]] = dict(zip(PT_KEYS, t[2:]), fail=False, ln=i)
        elif t[0] == "K8" and len(t) == 4:
            d["K8"] = dict(k=t[1], ll=t[2], run=t[3], ln=i)
        else:
            d["bad"].append((i, l))
    return d


GRID_RX = (r"^(full|kron) K=(\d+)\s+ll_val (\S+)\s+r(\d) kappa (\S+) n_iter (\d+) it_best (\d+) stop (\S+) reseed (\d+) sec (\d+)"
           r"\s*(.*?)\s*cand (\d+)")


def parse_prep(F):
    L = F.lines(PREPR)
    if L is None:
        return None
    out, cur = {}, None
    for i, l in enumerate(L, 1):
        m = re.match(r"^== (\S+) \((C\d), Nr (\d+), N' (\d+)\)", l)
        if m:
            cur = out[m[1]] = dict(cell=m[2], nr=int(m[3]), n=int(m[4]), ln=i, grid={}, k8grid={}, fb=[], d1=[], d1ck=[], d1warn=[], draft=None)
            continue
        if l.startswith("== base points"):
            cur = out["_base"] = dict(ln=i, lines=[])
            continue
        x = l.strip()
        if cur is None or not x:
            continue
        if "lines" in cur:
            cur["lines"].append((x, i))
            continue
        g = re.match(GRID_RX, x)
        if g:
            (cur["k8grid"] if cur["draft"] else cur["grid"])[(g[1], int(g[2]))] = dict(
                ll=g[3], r=g[4], kap=g[5], ni=int(g[6]), ib=int(g[7]), stop=g[8], rs=int(g[9]), sec=int(g[10]), path=g[11], cand=int(g[12]), ln=i)
            continue
        for key, pre in (("bc", "batched check"), ("oom", "fit logs with OOM"), ("miss", "grid missing"), ("bstar", "b* ="),
                         ("qk", "Q-K:"), ("ident", "best.epoch =="), ("other", "other attempts"), ("train", "training:"),
                         ("gbcsv", "GB' csv"), ("gblog", "GB' log lines"), ("gbnpz", "GB' npz"), ("k8", "K8:"), ("draftk8", "DRAFT  K8")):
            if x.startswith(pre):
                cur[key] = (x, i)
                break
        else:
            if x.startswith("ckpt "):
                cur["ckb" if "_best.pt:" in x else "ckl"] = (x, i)
            elif x.startswith("DRAFT  PT"):
                cur["draft"] = (x, i)
            elif x.startswith("D1 sibling (samplecx"):
                cur["d1"].append((x, i))
            elif x.startswith("D1 sibling:"):
                cur["d1warn"].append((x, i))
            elif x.startswith("D1 ckpt"):
                cur["d1ck"].append((x, i))
            elif x.startswith("[§3d"):
                cur["fb"].append((x, i))
    return out


DONE_RX = r"# done\s*: (\d+) epochs, stopped_by=(\w+), aborted=(\w+), best val (\S+) @ epoch (\d+), wall ([\d.]+) s"


def segrule(train):
    """§5 체크포인트 행의 구간 규칙: 구간 = '# =====' 머리말 하나; '# resume … no epoch trained' 를 품은 구간 = GB′ 재실행, 나머지 = 학습;
    학습 최종 줄 = 학습 구간 중 마지막 '# done', 학습 초 = 학습 구간 '# done' wall 합, '# done' 없는 학습 구간 수 (있으면 합은 하한)."""
    if not train or "# done" not in train:
        return None
    segs = []
    for p in (x.strip() for x in train.split(" || ")):
        if p.startswith("# =====") or not segs:
            segs.append([p] if p.startswith("# =====") else ["(머리말 없음)", p])
        else:
            segs[-1].append(p)
    tr = [s for s in segs if not any(x.startswith("# resume") for x in s)]
    dones = [x for s in tr for x in s if x.startswith("# done")]
    walls = [fl(m[1]) for m in (re.search(r"wall ([\d.]+) s", x) for x in dones) if m]
    return dict(nseg=len(segs), ntr=len(tr), ngb=len(segs) - len(tr), final=dones[-1] if dones else None, wall=sum(walls),
                dead=sum(1 for s in tr if not any(x.startswith("# done") for x in s)), nab=sum("aborted=True" in x for x in dones))


def parse_log(F):
    L = F.lines(LOGR)
    if L is None:
        return None
    d = dict(run={}, skip={}, an={}, man={}, mjson={}, guard={}, rec={}, integ={}, acc={}, p1={}, fr={}, holm=None,
             starts=[], done=None, abort=[], fail=[], ptfail=[], marker=[], all=[], skipped=[])
    for i, l in enumerate(L, 1):
        if l.startswith("{"):
            try:
                j = json.loads(l)
                d["mjson"][j.get("result_tag")] = (j, i)
            except ValueError:
                pass
            continue
        m = re.match(r"^\[(?:nscale|scale2) (\d\d-\d\d \d\d:\d\d) (\w+)\] (.*)$", l)
        if not m:
            continue
        t, msg = f"{m[1]} {m[2]}", m[3]
        d["all"].append((i, t, msg))
        r = re.search(r" rc=(\d+)$", msg)
        if r and r[1] != "0":
            d["fail"].append((i, msg))
        if "SKIPPED" in msg:
            d["skipped"].append((i, msg))
        x = None
        if msg.startswith("start eval"):
            d["starts"].append((i, t, msg))
        elif msg.startswith("ABORT"):
            d["abort"].append((i, msg))
        elif msg.startswith("single-shot marker"):
            d["marker"].append((i, msg))
        elif (x := re.match(r"NSCALE_DONE ok=(\d+) fail=(\d+)", msg)):
            d["done"] = (i, t, int(x[1]), int(x[2]))
        elif (x := re.match(r"run (\S+) \((\d+)/(\d+) files\) rc=(\d+)$", msg)):
            d["run"][x[1]] = dict(n=int(x[2]), N=int(x[3]), rc=int(x[4]), ln=i, t=t)
        elif (x := re.match(r"run (\S+) skip: raw complete \((\d+) files\)", msg)):
            d["skip"][x[1]] = (i, t)
        elif (x := re.match(r"analysis (\S+) rc=(\d+)$", msg)):
            d["an"][x[1]] = (int(x[2]), i)
        elif (x := re.match(r"run_manifest (\S+) rc=(\d+)$", msg)):
            d["man"][x[1]] = (int(x[2]), i)
        elif (x := re.match(r"guard_report (\S+) rc=(\d+)$", msg)):
            d["guard"][x[1]] = (int(x[2]), i)
        elif (x := re.match(r"recovery_ci (\S+) (?:\((.*)\) )?rc=(\d+)$", msg)):
            d["rec"][x[1]] = (int(x[3]), i, x[2])
        elif (x := re.match(r"(.+?) \(report-only integrity line(?:, not a gate)?\) rc=(\d+)$", msg)):
            d["integ"][x[1]] = (int(x[2]), i)
        elif (x := re.match(r"accept (\S+) \((.*)\) rc=(\d+)$", msg)):
            d["acc"][x[1]] = dict(rc=int(x[3]), ln=i, txt=x[2].strip())
        elif (x := re.match(r"P1 (\S+) SKIPPED: (.*) rc=(\d+)$", msg)):
            d["p1"][x[1]] = dict(rc=int(x[3]), ln=i, txt=x[2], skipped=True)
        elif (x := re.match(r"P1 (\S+) \((.*)\) rc=(\d+)$", msg)):
            d["p1"][x[1]] = dict(rc=int(x[3]), ln=i, txt=x[2], skipped=False)
        elif (x := re.match(r"frontier (\S+) SKIPPED: (.*) rc=(\d+)$", msg)):
            d["fr"][x[1]] = dict(rc=int(x[3]), ln=i, txt=x[2], skipped=True)
        elif (x := re.match(r"frontier (\S+) \((.*)\) rc=(\d+)$", msg)):
            d["fr"][x[1]] = dict(rc=int(x[3]), ln=i, txt=x[2], skipped=False)
        elif (x := re.match(r"P2 Holm helper \((.*)\) rc=(\d+)$", msg)):
            d["holm"] = dict(rc=int(x[2]), ln=i, txt=x[1])
        elif (x := re.match(r"(\S+): PT '-' = point failed", msg)):
            d["ptfail"].append((x[1], i))
    return d


def parse_runner(F, T):
    rel = f"logs/run_D2_{T}.log"
    L = F.lines(rel)
    if L is None:
        return None
    d = dict(rel=rel, heads=[], ck=None, wk=None, first=None, fin=[], bad=[], rss=[], oom=[], gd=None)
    for i, l in enumerate(L, 1):
        if l.startswith("# run_"):
            d["heads"].append((l, i))
        elif l.startswith("[run] Stage C checkpoint:") and d["ck"] is None:
            d["ck"] = (l.split(": ", 1)[1], i)
        elif re.match(r"\[run\] D2 \d+ points x n=\d+", l):
            d["wk"] = (l, i)
        elif l.startswith("[run] --worker-gb"):
            d["gd"] = (l, i)
        elif d["first"] is None and re.match(r"\d+/\d+ done ", l):
            m = re.search(r"\((\d+) s\)", l)
            d["first"] = (m[1] if m else "?", i)
        elif l.startswith("[run] finished in"):
            m = re.search(r"finished in ([\d.]+) min", l)
            d["fin"].append((m[1] if m else "?", i))
        if re.search(r"warn|error|traceback|exception", l, re.I):
            d["bad"].append(i)
        if re.search(r"\brss\b|maxrss", l, re.I):
            d["rss"].append(i)
        if re.search(r"out of memory|OutOfMemory|MemoryError|Killed", l):
            d["oom"].append(i)
    return d


def parse_acc(F, K):
    rel = f"{RV}/{K}_accept.txt"
    L = F.lines(rel)
    if L is None:
        return None
    L = L or [""]
    fails = [(x.strip(), i) for i, x in enumerate(L, 1) if i > 1 and x.startswith("  ") and not re.match(r"\s+\((f|k)\) ", x)]
    ff = [(x.strip(), i) for i, x in enumerate(L, 1) if re.match(r"\s+\(f\) ", x)]
    fok = [(x.strip(), i) for i, x in enumerate(L, 1) if x.startswith("ACCEPT (f):")]
    tb = [(x.strip(), i) for i, x in enumerate(L, 1) if re.search(r"Traceback|Error", x)]
    ok = L[0].startswith("ACCEPT: OK") and all(x.startswith("ACCEPT (f): OK") for x, _ in fok) and not tb
    return dict(rel=rel, first=L[0], fails=fails, f=ff, fok=fok, tb=tb, ok=ok, L=L)


def parse_blockB(L, i0, rel):                           # i0 = 0-based index of '  x -> y        [decision-point anchor arm: …]'
    b = L[i0:i0 + 6]
    if len(b) < 6:
        return None
    d = dict(ln=i0 + 1, end=i0 + 6, lines=b, rel=rel)
    m = re.search(r"decision SNRs \[([^\]]*)\]", b[1])
    d["dec"] = [int(x.strip().strip("'")) for x in m[1].split(",")] if m and m[1].strip() else []
    d["pts"] = re.findall(r"([+-]\d+) dB (\d+):(\d+) p=(\S+)", b[2])
    m = re.search(r"pooled (\d+):(\d+) p=(\S+)", b[2])
    d["pooled"] = (m[1], m[2], m[3]) if m else None
    d["guard"], d["powered"] = b[3].strip(), b[3].rstrip().endswith("-> POWERED")
    m = re.search(r"second arm fewer failures at (\d)/(\d) points, first arm fewer failures at (\d)/(\d) points -> (.*)$", b[4])
    d["k2"], d["k1"], d["sig"] = (int(m[1]), int(m[3]), m[5].strip()) if m else (0, 0, None)
    d["l5"] = b[4].strip()
    m = re.search(r"SNR@0\.1 gap \([^)]*\): (.*)$", b[5])
    d["gap"] = m[1].strip() if m else None
    return d


def blockB(F, rel, pair):                               # -> (block dict | None, number of blocks found)
    L = F.lines(rel)
    if L is None:
        return None, None
    idx = [i for i, l in enumerate(L) if l.startswith("  " + pair + " ")]
    return (parse_blockB(L, idx[0], rel) if len(idx) == 1 else None), len(idx)


def tableA(F, rel, arm):
    L = F.lines(rel)
    i0, _ = find(L, r"^=+ TABLE A")
    if i0 is None:
        return None
    ih, _ = find(L, r"^\s+arm\s+SNR ", i0)
    snrs = [int(x) for x in re.findall(r"SNR ([+-]?\d+) dB", L[ih - 1])] if ih else []
    ir, _ = find(L, r"^  " + re.escape(arm) + r"\s+\d", ih or i0)
    if ir is None:
        return None
    return dict(snrs=snrs, vals=re.findall(r"(\d\.\d+)\((\d\.\d+),(\d\.\d+)\)", L[ir - 1]), ln=ir)


def snr01(F, rel, arm):
    L = F.lines(rel)
    i0, _ = find(L, r"SNR@BLER 0\.1 \(log-linear")
    if i0 is None:
        return None
    ir, m = find(L, r"^    " + re.escape(arm) + r"\s+((?:<=|>)?\s*-?\d+(?:\.\d+)?)\s{2,}", i0)
    return (m[1].strip(), ir) if ir else None


def parse_p1(F, T):
    rel = f"{RV}/nscale_P1_{T}.txt"
    L = F.lines(rel)
    if L is None:
        return None
    d = dict(rel=rel, head=(L[0], 1) if L else None, auto=None, notes=[])
    d["v1"], d["nv1"] = blockB(F, rel, PV1)
    d["sc"], d["nsc"] = blockB(F, rel, PSC)
    i, m = find(L, r"^AUTO-LABEL (\S+): (.*)$")
    if i:
        d["auto"] = (m[2], i)
    d["notes"] = [(l, k) for k, l in enumerate(L, 1) if "blocks (exactly 1 expected)" in l]
    return d


def parse_rec(F, rel):
    L = F.lines(rel)
    if L is None:
        return None
    blocks, same = [], None
    for i, l in enumerate(L, 1):
        m = re.match(r"^# recovery R = .*?, (\S+) (C\d), paired bootstrap", l)
        if m:
            blocks.append(dict(raw=m[1], cell=m[2], ln=i, rows=[], pooled=None))
            continue
        m = re.match(r"^  ([+-]\d+) dB  b\* (\d+)  V1 (\d+)  genie (\d+)  n=(\d+)  R = (\S+)  \[90% (\S+), (\S+)\](.*)$", l)
        if m and blocks:
            blocks[-1]["rows"].append(dict(snr=int(m[1]), b=int(m[2]), v=int(m[3]), g=int(m[4]), n=int(m[5]), R=m[6], lo=m[7], hi=m[8],
                                           tail=m[9].strip(), ln=i))
            continue
        m = re.match(r"^  pooled (\d+) SNRs  b\* (\d+)  V1 (\d+)  genie (\d+)  R = (\S+)  \[90% (\S+), (\S+)\](.*)$", l)
        if m and blocks:
            blocks[-1]["pooled"] = dict(k=int(m[1]), b=int(m[2]), v=int(m[3]), g=int(m[4]), R=m[5], lo=m[6], hi=m[7], tail=m[8].strip(), ln=i)
            continue
        m = re.search(r"(\d+) of (\d+) \(chunk, key\) pairs differ -> (OK|FAIL)", l)
        if m:
            same = dict(txt=l.strip(), bad=int(m[1]), n=int(m[2]), res=m[3], ln=i)
    return dict(rel=rel, blocks=blocks, same=same)


R_LINE = r"^  R(\d): (\S+) (C\d) SNR \[([^\]]*)\]  (?:n=(\d+)  )?b\* (\d+) V1 (\d+) genie (\d+)  R = (\S+)  \[90% (\S+), (\S+)\](.*)$"


def parse_fr(F, rel):
    L = F.lines(rel)
    if L is None:
        return None
    d = dict(rel=rel, head=None, note=None, B=None, R={}, d90=None, dlv=None, dR=None, gaps={}, Rp={}, Rpd=None, Rpna=None,
             Rs={}, Rsd=None, Rsna=None, pairs=[], err=[], L=L)
    for i, l in enumerate(L, 1):
        if (m := re.match(r"^# run_\w+ git (\S+) (.+?): frontier_ci\.py (.*)$", l)):
            d["head"] = dict(git=m[1], t=m[2], args=m[3], ln=i)
        elif (m := re.match(r"^# Q-K: (.*)$", l)):
            d["note"] = (m[1], i)
        elif l.startswith("#") and d["B"] is None and (m := re.search(r"B=(\d+), seed=", l)):
            d["B"] = int(m[1])
        elif (m := re.match(R_LINE, l)):
            d["R"][int(m[1])] = dict(raw=m[2], cell=m[3], snrs=m[4], n=m[5], b=int(m[6]), v=int(m[7]), g=int(m[8]), R=m[9], lo=m[10], hi=m[11],
                                     tail=m[12].strip(), ln=i)
        elif (m := re.match(r"^  R1 - R2 = (\S+)  \[90% unpaired (\S+), (\S+)\]  undefined replicates (\d+)$", l)):
            d["d90"] = dict(v=m[1], lo=m[2], hi=m[3], und=int(m[4]), ln=i)
        elif (m := re.match(r"^  R1 - R2 = (\S+)  \[(\S+)% unpaired (\S+), (\S+)\]  bootstrap two-sided p = (\S+)  \(--level (\S+)\)$", l)):
            d["dlv"] = dict(v=m[1], L=m[2], lo=m[3], hi=m[4], p=m[5], lev=m[6], ln=i)
        elif (m := re.match(r"^  dR = R1 - R2 = (\S+)  \[90% paired (\S+), (\S+)\]  \[95% paired (\S+), (\S+)\]  bootstrap two-sided p = (\S+)"
                            r"  undefined replicates (\d+)$", l)):
            d["dR"] = dict(v=m[1], lo90=m[2], hi90=m[3], lo95=m[4], hi95=m[5], p=m[6], und=int(m[7]), ln=i)
        elif (m := re.match(r"^  gaps R(\d): SigmaF_V1 - SigmaF_g = (-?\d+)  \[90% (\S+), (\S+)\]   SigmaF_b\* - SigmaF_g = (-?\d+)  \[90% (\S+), (\S+)\]", l)):
            d["gaps"][int(m[1])] = dict(vg=m[2], vlo=m[3], vhi=m[4], bg=m[5], blo=m[6], bhi=m[7], ln=i)
        elif (m := re.match(r"^  R(\d)\+: (.*)$", l)):
            x = m[2]
            q = dict(txt=x.strip(), ln=i, forced="[K 상한 민감: 외삽 불가]" in x, r1=("(r >= 1)" in x),
                     strong=re.search(r"\[K 상한 강건 \(K/2 가 더 낫지 않음, ΔF_K = ([^)]*)\)\]", x))
            for k, p in (("bk2", r"b\*\(K/2\) (\d+)"), ("dF", r"dF = ([+-]?\d+)"), ("ck", r"c_K = (\S+)"), ("fp", r"SigmaF\+ = (\S+)"),
                         ("Rp", r"R\+ = (\S+)"), ("ci", r"R\+ = \S+  \[90% (\S+, \S+)\]"), ("und", r"in (\S+)% of replicates")):
                mm = re.search(p, x)
                q[k] = mm[1] if mm else None
            d["Rp"][int(m[1])] = q
        elif (m := re.match(r"^  R1\+ - R2\+ = (\S+)  \[(\S+)% unpaired (\S+), (\S+)\]  bootstrap two-sided p = (\S+)  undefined replicates (\d+)$", l)):
            d["Rpd"] = dict(v=m[1], L=m[2], lo=m[3], hi=m[4], p=m[5], und=int(m[6]), ln=i)
        elif l.startswith("  R1+ - R2+: n/a"):
            d["Rpna"] = (l.strip(), i)
        elif (m := re.match(r"^  R\*(\d): (.*)$", l)):
            x = m[2]
            q = dict(txt=x.strip(), ln=i, undef_mark="[운영점 한정어 정의 불가]" in x)
            for k, p in (("s", r"s\* = (\S+) dB"), ("bv", r"B_V1\(s\*\) = (\S+)"), ("bg", r"B_g\(s\*\) = (\S+)"), ("R", r"R\* = (\S+)"),
                         ("ci", r"\[\S+% (\S+, \S+)\]"), ("und", r"undefined replicates (\S+)%")):
                mm = re.search(p, x)
                q[k] = mm[1] if mm else None
            d["Rs"][int(m[1])] = q
        elif (m := re.match(r"^  R\*1 - R\*2 = (\S+)  \[(\S+)% unpaired (\S+), (\S+)\]  bootstrap two-sided p = (\S+)  undefined replicates (\d+)$", l)):
            d["Rsd"] = dict(v=m[1], L=m[2], lo=m[3], hi=m[4], p=m[5], und=int(m[6]), ln=i)
        elif l.startswith("  R*1 - R*2: n/a"):
            d["Rsna"] = (l.strip(), i)
        elif (m := re.match(r"^  (\w+): (\S+) (C\d) (\S+)  grid \[([^\]]*)\] n=(\d+)  SNR@0\.1 = (.+?) dB  \[90% (\S+), (\S+); censored (\S+)%\]$", l)):
            if not d["pairs"] or "delta" in d["pairs"][-1]:
                d["pairs"].append(dict(specs=[]))
            d["pairs"][-1]["specs"].append(dict(name=m[1], raw=m[2], cell=m[3], arm=m[4], v=m[7], lo=m[8], hi=m[9], cens=m[10], ln=i))
        elif (m := re.match(r"^  Delta = (\S+) - (\S+) = (\S+) dB  \[90% (\S+), (\S+)\]  \[95% (\S+), (\S+)\]  bootstrap two-sided p = (\S+)"
                            r"  censored replicates (\S+)%$", l)):
            if d["pairs"]:
                d["pairs"][-1]["delta"] = dict(v=m[3], lo90=m[4], hi90=m[5], lo95=m[6], hi95=m[7], p=m[8], cens=m[9], ln=i, na=None)
        elif (m := re.match(r"^  Delta = (\S+) - (\S+): n/a (.*)$", l)):
            if d["pairs"]:
                d["pairs"][-1]["delta"] = dict(na=m[3], ln=i)
        if re.search(r"Traceback|Error|genie differs", l):
            d["err"].append((l.strip(), i))
    return d


def parse_holm(F):
    rel = f"{RV}/nscale_P2_holm.txt"
    L = F.lines(rel)
    if L is None:
        return None
    rows = {}
    for i, l in enumerate(L, 1):
        m = re.match(r"^(first|second)\s+(C\d): (.*?)-> AUTO-LABEL (.*)$", l)
        if m:
            rows[m[2]] = dict(pos=m[1], body=m[3].strip(), label=m[4].strip(), ln=i)
    return dict(rel=rel, rows=rows)


def parse_guard(F, T):
    rel = f"results/guard_D2_{T}.txt"
    L = F.lines(rel)
    if L is None:
        return None
    i, _ = find(L, r"NO GUARD FIRINGS")
    rows = [(l.strip(), k) for k, l in enumerate(L, 1) if re.match(r"^C\d\s+[+-]\d+\s+\S+\s+\d+\s+\d+\s+\d", l)]
    j, _ = find(L, r"^not applicable")
    return dict(rel=rel, none=i, rows=rows, na=(L[j - 1].strip(), j) if j else None)


RAWKEYS = ("run|git", "meta|ntrain", "meta|bstar", "meta|kron_K", "meta|stagec_ckpt_id", "meta|em_sec", "meta|jobs", "meta|worker_gb",
           "run|iters", "run|n", "run|seed")


def raw_meta(F, T):
    files = sorted(glob.glob(os.path.join(F.p(f"raw_{T}"), "D2_*.npz")))
    if not files:
        return None
    v = {k: set() for k in RAWKEYS}
    v["ll"], v["err"], v["n"] = set(), set(), len(files)
    for f in files:
        try:
            with np.load(f) as z:
                for k in RAWKEYS:
                    v[k].add((str(z[k].item() if z[k].shape == () else z[k])) if k in z.files else "(키 없음)")
                b = str(z["meta|bstar"].item()) if "meta|bstar" in z.files else None
                if b and f"meta|ll_val|{b}" in z.files:
                    v["ll"].add(repr(float(z[f"meta|ll_val|{b}"])))
        except Exception as e:                          # a broken chunk is reported, never fatal
            v["err"].add(f"{os.path.basename(f)}: {type(e).__name__}")
    return v


def best_last(F, T):
    """best 대 last V1 짝 부호검정 (B32e4 §6.2 형식; a = best 실패·last 성공): analysis.paired 와 같은 셈 (blk_err[:, -1] == 1/0)."""
    fa = sorted(glob.glob(os.path.join(F.p(f"raw_{T}"), "D2_*.npz")))
    bdir = F.p(f"raw_{T}last")
    if not fa or not os.path.isdir(bdir):
        return None
    per, nmiss, k = {}, 0, f"{V1}|blk_err"
    for f in fa:
        g = os.path.join(bdir, os.path.basename(f))
        if not os.path.exists(g):
            nmiss += 1
            continue
        s = int(re.search(r"_snr(-?\d+)_", os.path.basename(f))[1])
        with np.load(f) as za, np.load(g) as zb:
            if k not in za.files or k not in zb.files:
                continue
            ea, eb = za[k][:, -1], zb[k][:, -1]
        a, b = per.get(s, (0, 0))
        per[s] = (a + int(np.sum((ea == 1) & (eb == 0))), b + int(np.sum((ea == 0) & (eb == 1))))
    return dict(per=per, nmiss=nmiss, nfiles=len(fa))


def fit_stop(F, tag, nr, n):                            # base point kron 4096 stop rule from its fits npz (§1 정지 사유 규칙)
    rel = f"results/gmm_fits_D2_{tag}/fit_S2_Nr{nr}_kronK4096_n{n}.npz"
    try:
        with np.load(F.p(rel)) as z:
            ni, ib = int(z["n_iter"]), int(z["it_best"])
    except Exception:
        return None
    return dict(rel=rel, ni=ni, ib=ib, stop="cap500" if ni >= 500 else ("patience" if ni - ib >= 40 else "tol"))


# ====================================================================== context (parsed inputs + derived values)
class Ctx:
    def __init__(self, F):
        self.F = F
        self.s5, self.prep, self.lg = parse_s5(F), parse_prep(F), parse_log(F)
        self.reg = F.lines(REG)
        self.FB = self.s5["FALLBACK"][0] if self.s5 and self.s5["FALLBACK"] else None
        self.N2 = "B64e4" if self.FB == "1" else "B128e4"
        self.acc = {}
        self.res = {}                                    # results reused by the scoring section

    def pt(self, T):
        return (self.s5 or {}).get("PT", {}).get(T)

    def ptok(self, T):
        p = self.pt(T)
        return bool(p) and not p.get("fail")

    def a(self, K):
        if K not in self.acc:
            self.acc[K] = parse_acc(self.F, K)
        return self.acc[K]

    def ok(self, *Ks):
        return all((self.a(K) or {}).get("ok", False) for K in Ks)

    def ok3(self, *Ks):                                 # True all OK / False one FAILED / None one file missing (never a verdict)
        st = [None if self.a(K) is None else self.a(K)["ok"] for K in Ks]
        return False if False in st else None if None in st else True

    def gates(self):                                    # §1 수용 검사 행 끝의 게이트 (tri-state)
        N2 = self.N2
        return dict(P1={T: self.ok3(T) for T, _, _ in NEWPTS if self.ptok(T)},
                    P2_C2=self.ok3(N2, N2 + "chk", "BRB32e4") if self.ptok(N2) else False,
                    P2_C6=self.ok3("NR16B64e4", "NR16B64e4chk", "BRNR16B16e4") if self.ptok("NR16B64e4") else False,
                    S1=self.ok3("B64e4", "B64e4chk", "BRB32e4"), S2=self.ok3("B128e4", "B128e4chk", "B64e4", "B64e4chk"),
                    E=self.ok3(N2, N2 + "chk"), K8=self.ok3("B64e4k8", "B64e4"))


    def regl(self, pat):                                # registration line of a fixed rule text (or a loud marker)
        i, _ = find(self.reg, pat)
        return i

    def rc(self, pat, txt=None):
        i = self.regl(pat)
        if i is None:
            return badfmt(REG, "?", f"등록 문서에서 '{txt or pat}' 를 찾지 못함")
        return cite(REG, i)


def g3(v):
    return "통과" if v else "실패" if v is False else "입력 없음"


def gblines(pp, T):                                     # the prep 'GB' log lines' entries of this tag (the prefix itself holds a quote)
    return re.findall(r"'(gbp_" + re.escape(T) + r"\.log: [^']*)'", pp["gblog"][0]) if pp.get("gblog") else []


def mn(s):                                              # display a signed SNR list with the registration's minus sign
    return "/".join(f"{x:+d}".replace("-", "−") for x in s)


def acc_cell(X, K):
    a = X.a(K)
    if a is None:
        return miss(f"{RV}/{K}_accept.txt")
    parts = [f"`{esc(a['first'])}` ({cite(a['rel'], 1)})"]
    parts += [f"`{esc(x)}` (:{i})" for x, i in a["fails"][:6]]
    if len(a["fails"]) > 6:
        parts.append(f"… 실패 줄 {len(a['fails'])} 개")
    parts += [f"`{esc(x)}` (:{i})" for x, i in a["f"] + a["fok"]]
    parts += [f"`{esc(x)}` (:{i})" for x, i in a["tb"][:2]]
    return " / ".join(parts)


# ====================================================================== section writers
def sec_head(X, w, author):
    cdt, kst = date_now()
    w(f"### 6.1 결과 (기록 {cdt or judge('date 실패')} (= {kst}), {author or judge('기록자 (모델·역할)')} — 전사만, 해석 없음; "
      "초안 = 스크래치 생성기 `s6_gen.py` 의 출력 (자리표시 **[판단 필요: …]**·**[입력 없음: …]** 은 기록자가 채운다); "
      "원본 `logs/run_nscale.log`·`logs/run_D2_<T>.log` (청크별 BLER 줄은 옮기지 않음)·`logs/analysis_<T>.log`, "
      "`results/tables_D2_<T>.txt`·`results/guard_D2_<T>.txt`, `results/review_next/nscale_{P1_<T>,P2_C2,P2_C6,P2_holm,qk_<c>_L<L>{,_qkN,_qkB},"
      "S1_C2,S2_C2,eff_C2,eff128_C2,K8,K8_V1}.txt`·`<K>_accept.txt`·`recovery_<T>{,last}.txt`·`run_manifest_<T>.json`, "
      "`results/nscale/nscale_s5.txt`·`nscale_prep.txt`·`logs/nscale/nscale_s5.start`, raw `raw_<T>/` (meta·run 키, best/last V1 blk_err))")
    w("")
    w("표기: `L:n` = `logs/run_nscale.log` n 행. 접두 없는 이름은 `results/review_next/nscale_<이름>.txt` (예: `P2_C2:4`), "
      "`acc_<K>` = `results/review_next/<K>_accept.txt`, `rec_<T>` = `results/review_next/recovery_<T>.txt`, `man_<T>` = "
      "`results/review_next/run_manifest_<T>.json`, `tab_<T>` = `results/tables_D2_<T>.txt`, `guard_<T>` = `results/guard_D2_<T>.txt`, "
      "`run_<T>` = `logs/run_D2_<T>.log`, `an_<T>` = `logs/analysis_<T>.log`, `S5` = `results/nscale/nscale_s5.txt`, `prep` = "
      "`results/nscale/nscale_prep.txt` (§5 커밋본), `reg` = 이 문서; `:n` = 그 파일 n 행. 시각은 로그 원값 CDT (KST 는 `date` 로 환산). "
      "\"기록자 산술\" = 파일의 정수 실패 수·값에서 Python 으로 계산 (`s6_gen.py`; 정확한 R 은 실패 수의 분수, 표시 값은 파일의 세 자리).")
    w("")


def sec_commits(X, w):
    F, s5 = X.F, X.s5
    if s5 is None:
        w(f"**동결·실행 커밋**: {miss(S5R)}")
        w("")
        return
    fr = s5["FREEZE"]
    frs = f"`{fr[0]}` ({cite(S5R, fr[1])})" if fr else badfmt(S5R, "?", "FREEZE 줄 없음")
    runc = git(F, "log", "-1", "--format=%H", "--", S5R)
    if not runc:
        w(f"**동결·실행 커밋**: 동결 {frs}. 실행 커밋 (= §5 커밋, S5 를 바꾼 마지막 커밋): "
          f"{miss(S5R, 'git log 에 S5 커밋이 없음 (아직 커밋되지 않았거나 git 저장소가 아님)')}")
        w("")
        return
    ct = git(F, "log", "-1", "--format=%ct", runc)
    diffc = run(["git", "diff", fr[0], runc, "--", "code", "../Demo"], cwd=F.conf, raw=True) if fr else (None, "")
    names = git(F, "diff", "--name-status", fr[0], runc) if fr else None
    anc = run(["git", "merge-base", "--is-ancestor", fr[0], runc], cwd=F.conf)[0] if fr else None
    head = git(F, "rev-parse", "HEAD")
    after = git(F, "rev-list", "--count", f"{runc}..HEAD")
    st = git(F, "status", "--porcelain", "code", "../Demo")
    nm = "; ".join(x.replace("\t", " ") for x in (names or "").split("\n") if x) or "(없음)"
    w(f"**동결·실행 커밋**: 동결 {frs}. 실행 커밋 = §5 커밋 **{runc[:8]}** ({runc}, 커밋 시각 {date_at(ct) if ct else '?'}; "
      f"`git log -1 -- {S5R}`) — 동결이 조상: {'예' if anc == 0 else judge('merge-base --is-ancestor 실패')}; "
      f"`git diff {fr[0][:8] if fr else '?'} {runc[:8]} -- code ../Demo` {len(diffc[1].encode()) if diffc[0] == 0 else '?'} 바이트 (수용 (f)·실행 위치 행); "
      f"동결 대비 바뀐 파일 `git diff --name-status`: {esc(nm)}. 이 기록 시점 HEAD = {head[:8] if head else '?'} "
      f"(실행 커밋 뒤 커밋 {after if after is not None else '?'} 개), `git status --porcelain code ../Demo` {len(st.splitlines()) if st is not None else '?'} 줄.")
    mk = F.lines("logs/nscale/nscale_s5.start")
    if mk is None:
        w(f"- 단일 S5 표시 파일: {miss('logs/nscale/nscale_s5.start')}")
    else:
        sha = hashlib.sha256(open(F.p(S5R), "rb").read()).hexdigest()
        want = f"{sha} {runc}"
        w(f"- 단일 S5 표시 파일 `logs/nscale/nscale_s5.start:1` = `{esc(mk[0])}`; 지금 S5 의 sha256 + 실행 커밋 = `{want}` → "
          f"{'같다' if mk[0].strip() == want else judge('표시 파일과 S5 sha256·실행 커밋이 다르다 — §1 단일 S5 규칙')}.")
    w("")


def sec_exec(X, w):
    lg = X.lg
    w("**실행 (`logs/run_nscale.log`)**:")
    if lg is None:
        w(f"- {miss(LOGR, 'eval 이 시작되지 않았거나 다른 위치')}")
        w("")
        return
    for i, t, msg in lg["starts"]:
        w(f"- `L:{i}` {t} `{esc(msg)}`")
    for i, msg in lg["marker"]:
        w(f"- `L:{i}` `{esc(msg)}`")
    if not lg["starts"]:
        w(f"- {badfmt(LOGR, '?', 'start eval 줄 없음')}")
    if lg["done"]:
        i, t, ok, fail = lg["done"]
        w(f"- `L:{i}` {t} **`NSCALE_DONE ok={ok} fail={fail}`**.")
        if lg["starts"]:
            t0 = lg["starts"][0][1]
            yr = date_now()[0][:4]
            try:
                a = dt.datetime.strptime(f"{yr}-{t0[:11]}", "%Y-%m-%d %H:%M")
                b = dt.datetime.strptime(f"{yr}-{t[:11]}", "%Y-%m-%d %H:%M")
                mins = int((b - a).total_seconds() // 60)
                w(f"- 경과 {mins // 60} h {mins % 60:02d} min (`L:{lg['starts'][0][0]}` → `L:{i}`, 로그 시각의 기록자 산술; 연도 = `date`). "
                  f"§1 비용 행의 CPU 추정 ({X.rc(r'합 ≈ 7\.5–9\.5 h', '합 ≈ 7.5–9.5 h')}) 과 나란히 적는다 (§6.1.6).")
            except ValueError:
                w(f"- 경과: {badfmt(LOGR, i, '시각 형식')}")
    else:
        w(f"- {judge('NSCALE_DONE 줄이 없다 — 실행이 끝나지 않았거나 중단됨 (로그 끝을 확인)')}")
    nrc0 = sum(1 for _, _, m in lg["all"] if re.search(r" rc=0$", m))
    w(f"- rc=0 줄 {nrc0} 개 (기록자 셈) — `NSCALE_DONE` 의 ok 와 "
      + (("같다" if lg["done"] and lg["done"][2] == nrc0 else judge(f"ok 와 rc=0 줄 수가 다르다 ({lg['done'][2] if lg['done'] else '?'} vs {nrc0})"))) + ".")
    if lg["fail"] or lg["abort"] or lg["skipped"]:
        for i, msg in lg["abort"] + lg["fail"] + [x for x in lg["skipped"] if x not in lg["fail"]]:
            w(f"  - `L:{i}` `{esc(msg)}`")
        w(f"  - {judge('위 ABORT / rc≠0 / SKIPPED 줄의 원인 기록 (§1 수용 검사: 재실행은 사용자 승인)')}")
    else:
        w("- ABORT·rc≠0·SKIPPED 줄 0 (기록자 grep).")
    if len(lg["starts"]) > 1 or lg["skip"]:
        w(f"- 재개: `start eval` {len(lg['starts'])} 회, `skip: raw complete` 줄 {len(lg['skip'])} 개 "
          f"({', '.join(f'`L:{v[0]}` {k}' for k, v in lg['skip'].items()) or '없음'}) — 뒤 단계는 매번 다시 돈다 (스크립트 머리말).")
    for T, i in lg["ptfail"]:
        w(f"- `L:{i}` {T}: S5 의 `PT {T} -` → 건너뜀 (§1 대체 규칙).")
    nbad, nhead, nan = [], [], []
    for T in NEWRAW:
        r = parse_runner(X.F, T)
        if r:
            nbad += [(T, i) for i in r["bad"]]
            nhead.append((T, len(r["heads"])))
    for T in ("B64e4", "B128e4", "B64e4last", "B128e4last", "NR16B64e4"):
        L = X.F.lines(f"logs/analysis_{T}.log")
        if L is not None:
            nan += [(T, i) for i, l in enumerate(L, 1) if "WARNING" in l]
    w(f"- runner 로그 머리말 `# run_nscale …` 수: {', '.join(f'{T} {n}' for T, n in nhead) or '(로그 없음)'}; warn/error/traceback/exception 줄 "
      f"{len(nbad)} 개" + (f" ({', '.join(f'`run_{T}:{i}`' for T, i in nbad[:10])})" if nbad else "") + " (기록자 grep, 대소문자 무시). "
      f"analysis 로그의 `WARNING` 줄 {len(nan)} 개" + (f" ({', '.join(f'`an_{T}:{i}`' for T, i in nan[:10])})" if nan else "") + ".")
    w("")


def sec_runner(X, w):
    w("**runner 실행 (태그별; `run_<T>` 의 머리말 · `Stage C checkpoint` 줄 · workers 줄 · 첫 `done` 줄의 청크 초 · 끝 줄 `finished in`; 완료 시각 = `L:` 의 `run` 줄)**")
    w("")
    w("| 태그 | 명령 (머리말 줄의 `--cell`·`--snr`·`--n`) | 체크포인트 | 워커 (줄) | 첫 `done` 청크 (줄) | 소요 (줄) | 파일 · 완료 CDT (`L:`) |")
    w("|---|---|---|---|---|---|---|")
    lg = X.lg or {}
    for T in NEWRAW:
        r, rl = parse_runner(X.F, T), lg.get("run", {}).get(T)
        if r is None and rl is None:
            if T == "B64e4k8" and (X.s5 or {}).get("K8") and X.s5["K8"]["run"] == "0":
                w(f"| {T} | — | — | — | — | — | 실행 안 함 (S5 `K8 … 0`, {cite(S5R, X.s5['K8']['ln'])}) |")
            elif T.startswith("K2") and T != "K2B32e4" and X.pt(T[2:]) and X.pt(T[2:]).get("k2k") == "-":
                w(f"| {T} | — | — | — | — | — | 실행 안 함 (S5 K2 `-`) |")
            elif any(T.startswith(p) for p in ("B128e4", "K2B128e4")) and X.FB == "1":
                w(f"| {T} | — | — | — | — | — | 실행 안 함 (F1, `FALLBACK 1`) |")
            else:
                w(f"| {T} | {miss(f'logs/run_D2_{T}.log')} | | | | | (로그 줄 없음) |")
            continue
        if r is None:
            w(f"| {T} | {miss(f'logs/run_D2_{T}.log')} | | | | | {rl['n']}/{rl['N']} · {rl['t']} (`L:{rl['ln']}`) rc={rl['rc']} |")
            continue
        h = r["heads"][-1][0] if r["heads"] else ""
        cmd = " ".join(x for x in re.findall(r"--(?:cell \S+|n \d+|snr(?: -?\d+)+|worker-gb \S+)", h))
        ck = f"`{esc(r['ck'][0].split(' | ')[0])}`" + (" \\| …" if " | " in r["ck"][0] else "") + f" (:{r['ck'][1]})" if r["ck"] else "—"
        wk = re.search(r"on (\d+) workers", r["wk"][0]) if r["wk"] else None
        fin = r["fin"][-1] if r["fin"] else None
        w(f"| {T} | `{cmd}` (:{r['heads'][-1][1] if r['heads'] else '?'}; 머리말 {len(r['heads'])} 개) | {ck} | "
          f"{wk[1] if wk else '?'} (:{r['wk'][1] if r['wk'] else '?'}) | {r['first'][0] + ' s (:' + str(r['first'][1]) + ')' if r['first'] else '—'} | "
          f"{fin[0] + ' min (:' + str(fin[1]) + ')' if fin else '—'} | "
          + (f"{rl['n']}/{rl['N']} · {rl['t']} (`L:{rl['ln']}`) rc={rl['rc']}" if rl else "(로그 줄 없음)") + " |")
    w("")
    w("(첫 `done` 청크 초는 그 줄에 찍힌 청크 하나의 소요이고, 워커가 동시에 돌므로 첫 시작 청크의 시간은 아니다. 실행 순서 = §1 실행 순서 행: "
      "bridge 2 → C2 A·analysis → chk → last·analysis → K2B32e4·K2<T> → C6 A·analysis·chk·last·K2 → B64e4k8.)")
    seen = [(T, lg["run"][T]["ln"]) for T in NEWRAW if T in lg.get("run", {})]
    if [n for _, n in seen] != sorted(n for _, n in seen):
        w("- " + judge("run 줄의 순서가 §1 실행 순서와 다르다: " + ", ".join(f"{T} L:{n}" for T, n in seen)))
    w("")


def expect_meta(X, T):                                  # -> (ntrain, kron_K, ll_val repr, ckpt sha, role) the raw must carry (§5 / BASE)
    if T in ("BRB32e4", "K2B32e4"):
        n, kk, ll, sha = 320000, "4096", None, None
    elif T == "BRNR16B16e4":
        n, kk, ll, sha = 160000, "4096", None, None
    else:
        base = re.sub(r"^K2|chk$|last$|k8$", "", T)
        p = X.pt(base)
        if not p or p.get("fail"):
            return None
        n, kk, ll = int(p["ntrain"]), p["kk"], p["ll"]
        sha = p["lsha"] if T.endswith("last") else p["bsha"]
        if T.startswith("K2"):
            kk, ll = p["k2k"], p["k2ll"]
        if T == "B64e4k8":
            k8 = (X.s5 or {}).get("K8") or {}
            kk, ll = k8.get("k"), k8.get("ll")
    if T == "K2B32e4":
        kk = "2048"
    return dict(n=n, kk=kk, ll=ll, sha=sha, role="last" if T.endswith("last") else "best")


def sec_raw(X, w):
    w("**raw (기록자 확인, 단일 프로세스·GPU 숨김; `meta|*`·`run|*` 키만 읽음 — 청크마다 값 집합)**:")
    w("")
    w("| raw | 파일 | `run\\|git` | `meta\\|ntrain` | `meta\\|bstar` · `kron_K` · `ll_val\\|<b*>` | `meta\\|stagec_ckpt_id` | `meta\\|em_sec` | `jobs` · `worker_gb` | §5 대조 |")
    w("|---|---|---|---|---|---|---|---|---|")
    X.res["rawmeta"] = {}
    for T in NEWRAW:
        v = raw_meta(X.F, T)
        if v is None:
            if X.F.ex(f"raw_{T}") or (X.lg and T in X.lg["run"]):
                w(f"| `raw_{T}` | {miss(f'raw_{T}/D2_*.npz')} | | | | | | | |")
            continue
        X.res["rawmeta"][T] = v
        ids = sorted({x.split(" | ")[0] + (" | …" if " | " in x else "") for x in v["meta|stagec_ckpt_id"]})
        e = expect_meta(X, T)
        chk = []
        if e:
            chk.append("ntrain " + ("✓" if v["meta|ntrain"] == {f"{float(e['n'])}"} or v["meta|ntrain"] == {str(e["n"])} else "✗"))
            if e["kk"]:
                chk.append("kron_K " + ("✓" if v["meta|kron_K"] in ({e["kk"]}, {f"{float(e['kk'])}"}) else "✗"))
            if e["ll"]:
                chk.append("ll_val " + ("✓" if len(v["ll"]) == 1 and abs(fl(next(iter(v["ll"]))) - fl(e["ll"])) <= 1e-9 else "✗"))
            if e["sha"]:
                chk.append("ckpt sha·role " + ("✓" if all(f"sha256[:16]={e['sha']}" in x and f"role={e['role']}" in x for x in ids) else "✗"))
        w(f"| `raw_{T}` | {v['n']} | {esc(', '.join(sorted(v['run|git'])))} | {esc(', '.join(sorted(v['meta|ntrain'])))} | "
          f"{esc(', '.join(sorted(v['meta|bstar'])))} · {esc(', '.join(sorted(v['meta|kron_K'])))} · {esc(', '.join(sorted(v['ll'])) or '—')} | "
          f"{esc('; '.join(ids))} | {esc(', '.join(sorted(v['meta|em_sec'])))} | {esc(', '.join(sorted(v['meta|jobs'])))} · "
          f"{esc(', '.join(sorted(v['meta|worker_gb'])))} | {', '.join(chk) or '—'}{(' / 오류 ' + esc('; '.join(sorted(v['err'])))) if v['err'] else ''} |")
    if not X.res["rawmeta"]:
        w(f"| — | {miss('raw_<T>/', 'NSCALE raw 가 하나도 없다')} | | | | | | | |")
    w("")
    hz = git(X.F, "log", "-1", "--format=%h", "--", S5R)
    if X.res["rawmeta"]:
        gits = {T: v["run|git"] for T, v in X.res["rawmeta"].items()}
        bad = [T for T, g in gits.items() if not hz or g != {hz}]
        w(f"- `run|git` = 실행 커밋 {hz or '?'}: {len(gits) - len(bad)}/{len(gits)} raw" + (f"; 아님: {', '.join(bad)} " + judge('수용 (f) 확인') if bad else "") + ".")
        for T, _, n in NEWPTS:
            a, l_ = X.res["rawmeta"].get(T), X.res["rawmeta"].get(T + "last")
            if a and l_:
                ea = sorted({re.search(r"epoch=(\d+)", x)[1] for x in a["meta|stagec_ckpt_id"] if re.search(r"epoch=(\d+)", x)})
                lb = sorted({re.search(r"best_epoch=(\d+)", x)[1] for x in l_["meta|stagec_ckpt_id"] if re.search(r"best_epoch=(\d+)", x)})
                w(f"- 수용 (c) 수동 대조 {T}: A raw `epoch=` {ea} · last raw `best_epoch=` {lb} → {'일치' if ea == lb and len(ea) == 1 else judge('불일치')}.")
    lg = X.lg or {}
    if lg.get("mjson"):
        w("- run_manifest (`L:` 의 JSON 줄): " + "; ".join(f"{t} config_hash {j.get('config_hash')} · n_raw_files {j.get('n_raw_files')} · git {j.get('git_commit')} (`L:{i}`)"
                                                for t, (j, i) in lg["mjson"].items()) + ".")
    for T, _, _ in NEWPTS:
        g = parse_guard(X.F, T)
        if g is None:
            if X.ptok(T):
                w(f"- 가드 보고 {T}: {miss(f'results/guard_D2_{T}.txt')}")
            continue
        if g["none"]:
            w(f"- 가드 보고 {T} ({cite(g['rel'], g['none'])}): \"NO GUARD FIRINGS in this raw set.\"" + (f" ({cite(g['rel'], g['na'][1])} `{esc(g['na'][0][:120])}`)" if g["na"] else ""))
        else:
            w(f"- 가드 보고 {T}: 발동 줄 {len(g['rows'])} 개 — " + "; ".join(f"`{esc(x)}` (:{i})" for x, i in g["rows"][:12]))
    w("")


def sec_accept(X, w):
    w("**수용 (`<K>_accept.txt` 원문; 로그 줄)**:")
    w("")
    w("| 태그 (게이트) | 원문 | 로그 |")
    w("|---|---|---|")
    rows = [("BRB32e4", "bridge → C2 P2·S1"), ("BRNR16B16e4", "bridge → C6 P2"), ("K2B32e4", "Q-K 기준 끝 C2")]
    for T, cell, _ in NEWPTS:
        rows += [(T, "A: P1·P2·(E); (a)(b)(d)"), (T + "chk", "chk: P2·(E); (e)"), (T + "last", "last: 보고 전용"), ("K2" + T, "Q-K 새 끝")]
    rows += [("B64e4k8", "보고 전용 K8")]
    for K, g in rows:
        if X.a(K) is None and K not in (X.lg or {}).get("acc", {}):
            base = re.sub(r"^K2|chk$|last$", "", K)
            if K != "B64e4k8" and base in ("B64e4", "B128e4", "NR16B64e4") and not X.ptok(base):
                w(f"| {K} ({g}) | 실행 안 함 (S5 `PT {base} -` 또는 없음) | — |")
                continue
            if K.startswith("K2") and K != "K2B32e4" and X.pt(K[2:]) and X.pt(K[2:]).get("k2k") == "-":
                w(f"| {K} ({g}) | 실행 안 함 (K2 없음, S5 `- - -`) | — |")
                continue
            if K == "B64e4k8" and (X.s5 or {}).get("K8", {}) and X.s5["K8"]["run"] == "0":
                w(f"| {K} ({g}) | 실행 안 함 (S5 `K8 … 0`) | — |")
                continue
        lr = (X.lg or {}).get("acc", {}).get(K)
        w(f"| {K} ({g}) | {acc_cell(X, K)} | " + (f"`L:{lr['ln']}` rc={lr['rc']}" if lr else "(로그 줄 없음)") + " |")
    k2r = X.a("K2NR16B16e4")
    w(f"| K2NR16B16e4 (Q-K 기준 끝 C6; SCALE16e4 기록, 링크) | {acc_cell(X, 'K2NR16B16e4') if k2r else miss(RV + '/K2NR16B16e4_accept.txt')} | (기록 파일) |")
    w("")
    for K, lr in ((X.lg or {}).get("acc", {})).items():          # file verdict vs the logged rc
        a = X.a(K)
        if a and (lr["rc"] == 0) != a["ok"]:
            w("- " + judge(f"{K}: 로그 rc={lr['rc']} 와 파일 판정 (ok={a['ok']}) 이 다르다"))
        if a and not a["fok"] and K != "K2NR16B16e4":
            w("- " + judge(f"{K}: (f) run|git 줄이 파일에 없다 (gitchk 출력 누락)"))
    g = X.gates()
    allf = [(K, x) for K in [r[0] for r in rows] if X.a(K) for x in X.a(K)["f"]]
    w("→ **수용 (a)–(k)** (§1 수용 검사 행):")
    w(f"- (a) 격자 완전성 (A 호출의 `--grid`): A 파일의 `grid:` 실패 줄 "
      f"{sum(1 for T, _, _ in NEWPTS if X.a(T) for x, _ in X.a(T)['fails'] if x.startswith('grid:'))} 개; K2 호출 (`--cand-dir`) 포함 전체 `grid:` 줄 "
      f"{sum(1 for K in [r[0] for r in rows] if X.a(K) for x, _ in X.a(K)['fails'] if x.startswith('grid:'))} 개.")
    w("- (b) 태그별 meta (청크 계획·ntrain·b\\*·kron_K·ll_val·ckpt sha·role·run\\|iters): 위 원문 (실패 줄이 있으면 그 줄).")
    w(f"- (c) 체크포인트: §5 (`prep` 출력) + 위 raw 절의 수동 대조.")
    w(f"- (d) genie 재생 (A 의 `--ref-raw` = 기준 raw): A 파일의 `replay vs` 실패 줄 "
      f"{sum(1 for T, _, _ in NEWPTS if X.a(T) for x, _ in X.a(T)['fails'] if 'replay vs' in x)} 개.")
    w(f"- (e) 재현 (`--ref-arms all`): bridge BRB32e4 {g3(X.ok3('BRB32e4'))}, BRNR16B16e4 {g3(X.ok3('BRNR16B16e4'))}; "
      f"chk {', '.join(f'{T}chk ' + g3(X.ok3(T + 'chk')) for T, _, _ in NEWPTS if X.ptok(T))}. "
      "**bridge 실패 → 그 셀의 1차는 (T-iv) \"수용 실패\"** (§1 (e)).")
    w(f"- (f) `run|git` (gitchk): (f) 줄 {len(allf)} 개, 값 = " + (", ".join(sorted({re.sub(r'^\(f\) \S+: run\|git ', '', x) for _, (x, _) in allf})) or "—")
      + f" (실행 커밋 {git(X.F, 'log', '-1', '--format=%h', '--', S5R) or '?'}); `ACCEPT (f): OK` 아닌 파일: "
      + (", ".join(K for K in [r[0] for r in rows] if X.a(K) and any(not x.startswith('ACCEPT (f): OK') for x, _ in X.a(K)['fok'])) or "없음") + ".")
    w("- (g) b\\*·K2·K8 구성: §5 (`S5` PT·K8 줄, `prep` 의 `K2 set b* = kron 2048 … OK`) + 위 raw 절의 `kron_K` (K2 raw 2048, B64e4k8 8192).")
    w("- (h) GB′ (보고 전용, 게이트 아님) · (i) D1 게이트 행 · (j) 메모리 (적합 로그 OOM 없음): §5 그대로 (§6.1.5 (c)·§6.1.7).")
    w("- (k) 무결성 줄 (보고 전용, 게이트 아님): §6.1.5 (j)·(k).")
    w(f"- 게이트 (§1 수용 검사 행 끝): P1 = A ({', '.join(f'{T} ' + g3(v) for T, v in g['P1'].items()) or '—'}); "
      f"P2·2차 (S) = 새 A + 새 chk + 기준 bridge (C2 {g3(g['P2_C2'])}, C6 {g3(g['P2_C6'])}); "
      f"S2 = 두 새 점의 A·chk ({g3(g['S2'])}); (E) = 새 A + chk ({g3(g['E'])}); "
      f"Q-K = 추가로 두 끝의 K2 (기준 C6 K2 = 기록 `K2NR16B16e4_accept.txt` {g3(X.ok3('K2NR16B16e4'))}).")
    w("")


def label_c2(X, T, blk, gate):
    n = nf(int(X.pt(T)["ntrain"]))
    tg = blk["powered"] and blk["k2"] >= 2
    if gate == "FAIL":
        return tg, f"\"예산 축 측정\" ({X.rc(r'\| FAIL \| \(어느 쪽이든\)', '§2.1 FAIL 행')}) — 학습 arm 결과가 아님; 표는 싣되 arm 주장에 쓰지 않는다 (표 B 출력: {'통과' if tg else '통과 못함'})"
    if tg:
        cav = " + \"격자 끝 (상한)\" 캐비엇 (b\\* = kron 4096, S5)" if X.pt(T)["bs"] == "kron" and X.pt(T)["kk"] == "4096" else ""
        return tg, f"**\"동일예산 우위가 N′ = {n} 에서도 유지\"** ({X.rc('동일예산 우위가 N′ = <N′> 에서도 유지')}) — arm 결과, 예산 곡선의 점. 헤드라인 불변{cav}"
    return tg, (f"**\"N′ = {n} 에서 우위 없음 / 판정 불가\"** ({X.rc('에서 우위 없음 / 판정 불가')}; 출력 문자열 그대로: `{esc(blk['guard'])}` / `{esc(blk['l5'])}`) — "
                "헤드라인 불변, 예산 곡선 표에 실림; 원고의 범위 문장은 사용자가 다시 정한다")


def label_c6(blk):
    if not blk["powered"]:
        return "(iv)", "\"판정하지 못함 (검정력 미달)\""
    if blk["k2"] >= 2:
        return "(i)", "**\"C6 동일예산 우위가 N′ = 6.4e5 에서도 유지 (기하 축 측정, UNGATED)\"**"
    if blk["k1"] >= 2:
        return "(ii)", "**\"N′ = 6.4e5 에서 C6 우위 없음 (GMM 우세)\"**"
    return "(iii)", "\"판정하지 못함 (유의 방향 없음)\""


def band(X, T):                                         # C6 회수율 대역 from recovery_<T>.txt (-3 dB row of the first block)
    rel = f"{RV}/recovery_{T}.txt"
    r = parse_rec(X.F, rel)
    if r is None:
        return None, miss(rel)
    rows = [x for b in r["blocks"] for x in b["rows"] if x["snr"] == -3]
    if not rows:
        return None, badfmt(rel, "?", "−3 dB 줄 없음")
    x = rows[0]
    R = rx(x["b"], x["v"], x["g"])
    txt = "기하 효과 대부분 유지" if R >= 0.70 else "일부 유지" if R >= 0.60 else "대부분 소예산 효과"
    rc = X.rc(r'R ≥ 0\.70 "기하 효과 대부분 유지"', "§1 P1 행 회수율 대역")
    return (R, x), (f"회수율 대역: R(−3 dB) = {x['R']} [90% {x['lo']}, {x['hi']}] (b\\* {x['b']} · V1 {x['v']} · genie {x['g']}, n={x['n']}; "
                    f"{cite(rel, x['ln'])}; 기록자 산술 정확값 {R!r}) → **\"{txt}\"** ({rc})")


def sec_p1(X, w):
    w("#### 6.1.1 P1 점별 (새 점마다; §2.1, 표 B `M-ours-bstar → M-ours-dscore-C-V1`, 판정점 = 앵커 b\\* 자동)")
    w("")
    w("| 점 (태그) | 게이트 (S5) | 판정점 | 점별 a:b (p) | pooled (p) | 가드 · 유의 | AUTO-LABEL (도우미) | §2.1 기록 | SNR@0.1 격차 b\\* − V1 | 출처 |")
    w("|---|---|---|---|---|---|---|---|---|---|")
    X.res["p1"] = {}
    notes = []
    for T, cell, n in NEWPTS:
        p = X.pt(T)
        if p is None:
            w(f"| {T} | {miss(S5R) if X.s5 is None else badfmt(S5R, '?', f'PT {T} 줄 없음')} | | | | | | | | |")
            continue
        if p.get("fail"):
            why = "\"적합 실패 (F1)\"" if T == "B128e4" and X.FB == "1" else "\"학습 실패\" / \"적합 실패\" " + judge(f"{T}: §5 의 실패 사유로 둘 중 하나")
            w(f"| {T} | `PT {T} -` ({cite(S5R, p['ln'])}) | — | — | — | — | — | BLER 미실행, {why} | — | {cite(S5R, p['ln'])} |")
            X.res["p1"][T] = dict(state="fail")
            continue
        lp = (X.lg or {}).get("p1", {}).get(T)
        if lp and lp["skipped"]:
            w(f"| {T} | {p['gate']} | — | — | — | — | — | **수용 실패 (표 B 없음)** (`L:{lp['ln']}` `{esc(lp['txt'])}`) | — | `L:{lp['ln']}` |")
            X.res["p1"][T] = dict(state="acc")
            continue
        P = parse_p1(X.F, T)
        if P is None or P["v1"] is None:
            why = miss(f"{RV}/nscale_P1_{T}.txt") if P is None else badfmt(P["rel"], "?", f"V1 블록 {P['nv1']} 개 (정확히 1 개여야)")
            w(f"| {T} | {p['gate']} | {why} | | | | | | | |")
            X.res["p1"][T] = dict(state="missing")
            continue
        b = P["v1"]
        tb, ntb = blockB(X.F, f"results/tables_D2_{T}.txt", PV1)
        tsrc = cite(f"results/tables_D2_{T}.txt", tb["ln"], tb["end"]) if tb else miss(f"results/tables_D2_{T}.txt")
        pts = " · ".join(f"{s} dB {a}:{c} ({pp})" for s, a, c, pp in b["pts"])
        pool = f"{b['pooled'][0]}:{b['pooled'][1]} ({b['pooled'][2]})" if b["pooled"] else "—"
        gd = (f"POWERED, second arm fewer {b['k2']}/3, first {b['k1']}/3 (`{b['sig']}`)" if b["powered"] else f"`{esc(b['guard'])}`")
        auto = f"`{esc(P['auto'][0])}` (:{P['auto'][1]})" if P["auto"] else badfmt(P["rel"], "?", "AUTO-LABEL 줄 없음")
        if cell == "C2":
            tg, rec = label_c2(X, T, b, p["gate"])
            mine = "통과" if tg else "통과 못함"
            agree = P["auto"] and P["auto"][0].startswith(mine + (" (" if tg else ""))
            X.res["p1"][T] = dict(state="ok", pass_=tg, blk=b, gate=p["gate"])
        else:
            c6, rec = label_c6(b)
            bd, btxt = band(X, T)
            rec = f"{c6} {rec} — {btxt}"                # §1 P1 행: C6 은 (i)–(iv) 와 회수율 대역을 반드시 함께 인용
            agree = P["auto"] and P["auto"][0].startswith(c6)
            X.res["p1"][T] = dict(state="ok", lab=c6, blk=b, band=bd)
        if not agree:
            rec += " " + judge(f"{T}: AUTO-LABEL 과 §2.1 규칙 적용 결과가 다르다 — 등록 규칙이 우선")
        w(f"| {T} ({cell}, N′ {nf(n)}) | {p['gate']} ({cite(S5R, p['ln'])}) | {mn(b['dec'])} | {pts} | {pool} | {gd} | {auto} | {rec} | "
          f"{esc(b['gap'] or '—')} | {cite(P['rel'], b['ln'], b['end'])} = {tsrc} |")
        if b["dec"] != [-3, 0, 3]:
            notes.append(f"{T}: 자동 판정점 {b['dec']} ≠ −3/0/+3 → P1 은 자동 판정점, P2 는 −3/0/+3 ({X.rc(r'10\. \*\*P2 의 SNR 은 고정', '공개 10')}).")
    w("")
    for x in notes:
        w(f"- {x}")
    w(f"- C2 의 \"통과\" = 출력 줄 `power guard … -> POWERED` 이고 `second arm fewer failures at k/3 points` 의 k ≥ 2 ({X.rc(r'통과 = 출력 줄', '§1 P1 행')}); "
      "`significant` 토큰은 판정 기준이 아니다. C6 라벨 (i)–(iv) 는 §2.1 C6 표.")
    w("- (ii)(iii)(iv) 어디에도 \"소예산 효과\" 문구를 만들지 않는다 — 그 문구는 회수율 대역에서만 나온다. 어느 결과도 헤드라인·C2 판정·기존 C6 기록을 바꾸지 않는다 (§2.1).")
    w("")
    w("**필수 대조군 `M-ours-bstar → M-ours-bstar-scalar` (보고만, 같은 형식)**:")
    for T, cell, n in NEWPTS:
        if X.res["p1"].get(T, {}).get("state") != "ok":
            continue
        P = parse_p1(X.F, T)
        s = P["sc"]
        if s is None:
            w(f"- {T}: " + badfmt(P["rel"], "?", f"대조군 블록 {P['nsc']} 개"))
            continue
        X.res["p1"][T]["sc"] = s
        w(f"- {T} ({cite(P['rel'], s['ln'], s['end'])}): 판정점 {mn(s['dec'])}, "
          + " · ".join(f"{a}:{c} ({pp})" for _, a, c, pp in s["pts"]) + (f", pooled {s['pooled'][0]}:{s['pooled'][1]} ({s['pooled'][2]})" if s["pooled"] else "")
          + (f", POWERED, `second arm fewer failures at {s['k2']}/3 points, first arm fewer failures at {s['k1']}/3 points -> {s['sig']}`" if s["powered"] else f", `{esc(s['guard'])}`")
          + f"; SNR@0.1 격차 {esc(s['gap'] or '—')}.")
    w("")


def p2_guard(X, c, T, rel, d, B):
    """§1 가드 행 → (T-iv) 사유 ('' = 없음, None = 입력이 없어 정할 수 없음) and the list of checked facts."""
    facts, why = [], ""
    p = X.pt(T)
    if p is None:
        return None, [miss(S5R) if X.s5 is None else badfmt(S5R, "?", f"PT {T} 줄 없음")]
    if p.get("fail"):
        return "학습 실패 / 적합 실패 (§5)", [f"S5 `PT {T} -` ({cite(S5R, p['ln'])})"]
    gk = X.gates()["P2_" + c]
    if gk is False:
        why = "수용 실패"
    elif gk is None:
        facts.append("수용 파일 일부 없음 (A·chk·bridge) " + judge(f"{c}: P2 게이트를 정할 수 없다 — 수용 파일 확인"))
    fr = (X.lg or {}).get("fr", {}).get(f"nscale_P2_{c}")
    if d is None:
        if why:
            return why, facts
        if fr and fr["skipped"]:
            return "수용 실패", facts + [f"`L:{fr['ln']}` `{esc(fr['txt'][:90])}`"]
        return None, facts + [miss(rel)]
    if any("genie differs" in x for x, _ in d["err"]):
        return why or "수용 실패 (--paired genie assert)", facts + [f"`genie differs` ({cite(rel, [i for x, i in d['err'] if 'genie differs' in x][0])})"]
    if fr and fr["rc"] != 0 and not fr["skipped"]:
        why = why or f"정의 불가 (frontier_ci rc {fr['rc']})"
    for j in (1, 2):
        r = d["R"].get(j)
        if r is None:
            return why or "정의 불가 (출력 형식)", facts
        facts.append(f"R{j}: ΣF_b\\* {r['b']} {'>' if r['b'] > r['g'] else '≤'} ΣF_g {r['g']}, ΣF_g {r['g']} {'<' if r['g'] < r['v'] else '≥'} ΣF_V1 {r['v']} "
                     f"({cite(rel, r['ln'])})")
        if r["b"] <= r["g"] or r["R"] == "nan":
            why = why or "정의 불가 (ΣF_b* ≤ ΣF_g)"
        elif r["g"] >= r["v"]:
            why = why or "범위 밖 (ΣF_g ≥ ΣF_V1, genie 가드)"
    if d["dR"]:
        lim = (B or 2000) * 0.05
        facts.append(f"정의 불가 복제 {d['dR']['und']} / B={B} ({'≤' if d['dR']['und'] <= lim else '>'} 5 %; {cite(rel, d['dR']['ln'])})")
        if d["dR"]["und"] > lim:
            why = why or "정의 불가 (정의 불가 복제 > 5 %)"
    else:
        why = why or "정의 불가 (출력 형식)"
    return why, facts


def gn_text(X, pts):
    """G_N (§2 첫 줄): pts = [(N′, tag, stopinfo|None, edge bool, src)]."""
    nk = ", ".join(f"{nf(n)} {n // 4096}" for n, *_ in pts)
    lst = []
    for n, tag, si, edge, src in pts:
        bits = []
        if edge:
            bits.append("격자 끝 kron 4096 (상한)")
        if si and si["stop"] == "tol":
            bits.append(f"tol 정지 ({si['ni']}/{si['ib']})")
        if si is None:
            bits.append(judge(f"{tag} 의 kron 4096 정지 사유 (적합 npz/prep 없음)"))
        if bits:
            lst.append(f"{nf(n)} `{tag}` " + "·".join(bits) + f" ({src})")
    return (f"(b\\* = 등록 프로토콜의 GMM — full K ≤ 512 (κ 4 개), kron K ≤ 4096, 재시작 3, EM 상한 500 반복·tol/patience 정지 — 이며 최적 GMM 이 아니다; "
            f"상한 4096 대비 N′/K: {nk}; 격자 끝·tol 정지 점: {'; '.join(lst) or '없음'})")


def pt_gn(X, T):                                        # one new point's G_N entry from S5 + prep
    p = X.pt(T)
    pp = (X.prep or {}).get(T, {})
    g = pp.get("grid", {}).get(("kron", 4096))
    si = dict(ni=g["ni"], ib=g["ib"], stop=g["stop"]) if g else None
    edge = bool(p) and p.get("bs") == "kron" and p.get("kk") == "4096"
    return (int(p["ntrain"]) if p and not p.get("fail") else 0, T, si, edge, (cite(PREPR, g["ln"]) if g else "§5") + ", " + (cite(S5R, p["ln"]) if p else ""))


def base_gn(X, c):
    b = BASE[c]
    si = fit_stop(X.F, b["tag"], b["nr"], b["n"])
    return (b["n"], b["tag"], si, True, (f"`{si['rel']}` n_iter/it_best; §0.4 {X.rc('kron 1024 / 2048 / 4096 병합 ll_val', '§0.4 표')}" if si else "§0.4"))


def qual(X, c, Llev, L1):
    """Q-OP / Q-K (§2.2) for cell c at its Holm level; L1 = the primary label."""
    F = X.F
    V = f"L{Llev}"
    fa, fn, fb = (f"{RV}/nscale_qk_{c}_{V}{s}.txt" for s in ("", "_qkN", "_qkB"))
    A = parse_fr(F, fa)
    out = dict(rows=[], L0=None)
    if A is None:
        out["qop"] = out["qk"] = miss(fa, "Q-K/Q-OP 실행 (a) — P2 가 rc≠0 이거나 PT '-' 이면 만들지 않는다 (스크립트 :470–471)")
        return out
    if A["dlv"] is None:
        out["qop"] = out["qk"] = badfmt(fa, "?", "R1 - R2 (--level) 줄 없음")
        return out
    L0 = lab(fl(A["dlv"]["lo"]), fl(A["dlv"]["hi"]))
    out["L0"] = L0
    out["rows"].append(f"L⁰ (실행 (a) 의 비짝 `R1 - R2` `--level` 줄, {cite(fa, A['dlv']['ln'])}): {A['dlv']['v']} [{A['dlv']['L']}% unpaired {A['dlv']['lo']}, "
                       f"{A['dlv']['hi']}], p {A['dlv']['p']} → **L⁰ = {L0}**")
    # forced Q-K
    files = [(k, f, parse_fr(F, f)) for k, f in (("a", fa), ("b", fn), ("c", fb))]
    forced = []
    if A["note"]:
        m = re.search(r"Q-K \(1\): (.*?) -> run \(a\)", A["note"][0])
        forced.append(f"{m[1] if m else A['note'][0]} ({cite(fa, A['note'][1])})")
    for k, f, d in files:
        if d is None:
            continue
        for j, q in d["Rp"].items():
            if q["forced"]:
                rs = "r ≥ 1 (c_K inf)" if q["r1"] else ("점 R⁺ 정의 불가" if (d["Rpna"] or q["Rp"] in (None, "nan")) else f"분모 ≤ 0 복제 {q['und']} % > 5 %")
                forced.append(f"실행 ({k}) `R{j}+` 줄 끝의 '[K 상한 민감: 외삽 불가]' — {rs} ({cite(f, q['ln'])})")
    for k, f, d in files:
        if d is None:
            if not A["note"]:
                out["rows"].append(f"실행 ({k}): {miss(f)}")
            continue
        for j, q in sorted(d["Rp"].items()):
            out["rows"].append(f"실행 ({k}) `R{j}+` ({cite(f, q['ln'])}): `{esc(q['txt'])}`")
        if d["Rpd"]:
            out["rows"].append(f"실행 ({k}) `R1+ - R2+` ({cite(f, d['Rpd']['ln'])}): {d['Rpd']['v']} [{d['Rpd']['L']}% unpaired {d['Rpd']['lo']}, {d['Rpd']['hi']}], "
                               f"p {d['Rpd']['p']}, undefined {d['Rpd']['und']} → L⁺ = {lab(fl(d['Rpd']['lo']), fl(d['Rpd']['hi']))}")
        elif d["Rpna"]:
            out["rows"].append(f"실행 ({k}) ({cite(f, d['Rpna'][1])}): `{d['Rpna'][0]}`")
    if forced:
        qk = f"**\"[K 상한 민감: 외삽 불가]\" ({'; '.join(forced)})** — 강제 (L⁰ 와 무관, §2.2 Q-K (1)); 강제 조건 파일의 `R1+ - R2+` CI 는 보고 전용"
    elif L0 != L1:
        qk = f"**'[한정어 판정 불가: 비짝 CI 폭 (L⁰ = {L0})]'** (§2.2 L⁰ 규칙)"
    else:
        Lp, dfs = {}, []
        for k, f, d in files:
            if d is None:
                Lp[k] = None
                continue
            if d["Rpd"]:
                Lp[k] = lab(fl(d["Rpd"]["lo"]), fl(d["Rpd"]["hi"]))
            elif not d["Rp"] and d["dlv"]:
                Lp[k] = lab(fl(d["dlv"]["lo"]), fl(d["dlv"]["hi"]))
            else:
                Lp[k] = None
            dfs += [f"R{j}⁺ 끝 ΔF_K = {q['strong'][1]}" for j, q in d["Rp"].items() if q["strong"] and k == "a"]
        if any(v is None for v in Lp.values()):
            qk = judge(f"{c}: 실행 (a)(b)(c) 중 L⁺ 를 읽지 못한 파일 — {Lp}")
        elif all(v == L0 for v in Lp.values()):
            qk = "**\"[K 상한 강건]\"**" + (f" ((K/2 가 더 낫지 않음, {', '.join(dfs)}))" if dfs else "")
        else:
            qk = "**\"[K 상한 민감: " + "/".join(f"실행 ({k})" for k, v in Lp.items() if v != L0) + " 의 b\\*⁺ 에서 " \
                 + "/".join(sorted({v for v in Lp.values() if v != L0})) + "]\"**"
        out["Lp"] = Lp
    out["forced"] = forced
    out["qk"] = qk
    # Q-OP
    rs, rsd = A["Rs"], A["Rsd"]
    for j in (1, 2):
        if j in rs:
            out["rows"].append(f"R\\*{j} ({cite(fa, rs[j]['ln'])}): `{esc(rs[j]['txt'])}`")
    if rsd:
        out["rows"].append(f"L\\* = R\\*1 − R\\*2 ({cite(fa, rsd['ln'])}): {rsd['v']} [{rsd['L']}% unpaired {rsd['lo']}, {rsd['hi']}], p {rsd['p']}, undefined {rsd['und']}")
    if L0 != L1:
        qop = f"**'[한정어 판정 불가: 비짝 CI 폭 (L⁰ = {L0})]'**"
    elif A["Rsna"] or any(q["undef_mark"] for q in rs.values()) or not rsd:
        qop = "**\"[운영점 한정어 정의 불가]\"**" + (f" ({cite(fa, A['Rsna'][1])})" if A["Rsna"] else "")
    else:
        Ls = lab(fl(rsd["lo"]), fl(rsd["hi"]))
        qop = "**\"[운영점 정합 강건]\"**" if Ls == L0 and Ls != "(T0)" else f"**\"[운영점 민감: R\\*@0.05 에서 {Ls}]\"**"
    out["qop"] = qop
    out["gaps"] = A["gaps"]
    out["fa"] = fa
    return out


def lines_only(q):                                     # (T0)/(T0-Holm): qualifier lines are only reported, never attached (§2.2)
    return ("한정어는 붙이지 않는다 ((T±) 일 때만; §2.2) — 아래 줄은 보고만" + (f"; Q-K 강제 조건 사실: {'; '.join(q['forced'])}" if q.get("forced") else "") + ".")


def sentence_T(X, c, L1, n_base, n_new, gate_new):
    br = (f"D1 형제 게이트 기준 PASS / 새 {gate_new}" if c == "C2" else "UNGATED 예산 축 측정")
    k = n_new // n_base if n_new % n_base == 0 else round(n_new / n_base, 3)
    verb = "커진다" if L1 == "(T+)" else "작아진다"
    return (f"\"N′ 를 {nf(n_base)} → {nf(n_new)} ({k} 배) 로 늘릴 때 V1 의 genie 격차 회수율 (b\\* 대비 상대 격차) 이 {verb} ({c}, 같은 테스트 시행 짝 비교, "
            f"b\\* 판정점 −3/0/+3 dB, attempt 1 · 학습 집합 1 개 (공개 3·5), {br})\"")


def sec_p2(X, w):
    F = X.F
    N2 = X.N2
    w("#### 6.1.2 P2 1차 (짝 추세 ΔR, Holm m = 2; §1 P2·다중성·가드 행, §2.2)")
    w("")
    if X.FB is None:
        w(f"- {judge('S5 의 FALLBACK 을 읽지 못해 C2 대비가 정해지지 않는다 (F1 이면 R(6.4e5) − R(3.2e5))')}")
    w(f"- 대비: ΔR_C2 = R({nf(int(X.pt(N2)['ntrain'])) if X.ptok(N2) else N2}) − R(3.2e5) (`FALLBACK {X.FB}`"
      + (f", {cite(S5R, X.s5['FALLBACK'][1])}" if X.s5 and X.s5["FALLBACK"] else "") + "), ΔR_C6 = R(6.4e5) − R(1.6e5); 고정 SNR −3/0/+3 dB 합, "
      f"`frontier_ci.py --paired` (B 2000, seed 20260926).")
    w("")
    w("| 셀 | R(새) [90%] (b\\* · V1 · genie) | R(기준) [90%] | ΔR [90% paired] | ΔR [95% paired] | 부트스트랩 p | 정의 불가 복제 | 출처 |")
    w("|---|---|---|---|---|---|---|---|")
    P = {}
    for c, T in (("C2", N2), ("C6", "NR16B64e4")):
        rel = f"{RV}/nscale_P2_{c}.txt"
        d = parse_fr(F, rel)
        fr = (X.lg or {}).get("fr", {}).get(f"nscale_P2_{c}")
        why, facts = p2_guard(X, c, T, rel, d, d["B"] if d else None)
        P[c] = dict(rel=rel, d=d, why=why, facts=facts, T=T, fr=fr)
        if d is None or not d["dR"]:
            src = (f"`L:{fr['ln']}` `{esc(fr['txt'][:90])}`" if fr else miss(rel)) if d is None else badfmt(rel, "?", "dR 줄 없음")
            w(f"| {c} | — | — | — | — | — | — | {src} |")
            continue
        r1, r2, dr = d["R"].get(1), d["R"].get(2), d["dR"]
        f1 = lambda r: f"{r['R']} [{r['lo']}, {r['hi']}] (`{r['raw']}`: {r['b']} · {r['v']} · {r['g']})" if r else "—"
        w(f"| {c} | {f1(r1)} | {f1(r2)} | {dr['v']} [{dr['lo90']}, {dr['hi90']}] | {dr['v']} [{dr['lo95']}, {dr['hi95']}] | {dr['p']} | {dr['und']} | "
          f"{cite(rel, r1['ln'] if r1 else dr['ln'], dr['ln'])}" + (f"; `L:{fr['ln']}` rc={fr['rc']}" if fr else "") + " |")
    w("")
    w("**가드 점검 (§1 가드 행; 셀마다)**:")
    for c in ("C2", "C6"):
        v = P[c]["why"]
        w(f"- {c}: " + ("; ".join(P[c]["facts"]) or "—") + " → " + (f"**(T-iv) {v}**" if v else "**(T-iv) 없음**" if v == "" else judge(f"{c}: 입력이 없어 가드를 정할 수 없다")) + ".")
    unk = [c for c in ("C2", "C6") if P[c]["why"] is None]
    if unk:
        w("")
        w(f"**Holm 순서·1차 라벨**: " + judge("입력 없음 (" + ", ".join(unk) + ") — Holm 순서와 라벨을 정할 수 없다; 위 표·가드의 입력 없음 표시를 먼저 해소"))
        X.res["p2"] = dict(P=P, labels={c: ("?", None, None) for c in ("C2", "C6")}, order=[])
        X.res["qual"] = {}
        w("")
        return
    # Holm
    cand = {}
    for c in ("C2", "C6"):
        d = P[c]["d"]
        p = 1.0 if P[c]["why"] or not d or not d["dR"] else fl(d["dR"]["p"])
        cand[c] = p
    order = sorted(("C2", "C6"), key=lambda k: (bool(P[k]["why"]), cand[k], k != "C2"))
    labels, first = {}, None
    for i, c in enumerate(order):
        d = P[c]["d"]
        lv = 95 if i == 0 else 90
        if P[c]["why"]:
            L = "(T-iv)"
        elif i == 1 and first not in ("(T+)", "(T−)"):
            L = "(T0-Holm)"
        else:
            lo, hi = (fl(d["dR"]["lo95"]), fl(d["dR"]["hi95"])) if lv == 95 else (fl(d["dR"]["lo90"]), fl(d["dR"]["hi90"]))
            L = lab(lo, hi)
        if i == 0:
            first = L
        labels[c] = (L, lv, i)
    X.res["p2"] = dict(P=P, labels=labels, order=order)
    w("")
    w(f"**Holm 순서 (§1 다중성 행)**: p_C2 = {P['C2']['d']['dR']['p'] if P['C2']['d'] and P['C2']['d']['dR'] and not P['C2']['why'] else '1 (p := 1, (T-iv))' if P['C2']['why'] else '—'}, "
      f"p_C6 = {P['C6']['d']['dR']['p'] if P['C6']['d'] and P['C6']['d']['dR'] and not P['C6']['why'] else '1 (p := 1, (T-iv))' if P['C6']['why'] else '—'} → "
      f"**{order[0]} 첫째 (95 % CI), {order[1]} 둘째 (90 % CI)** (p 가 작은 쪽이 첫째, 동률이면 C2 첫째, (T-iv) 는 항상 둘째; "
      f"{X.rc('동률이면 \\(두 p 가 모두 0\\.0000 포함\\)', '§1 다중성 행')}).")
    H = parse_holm(F)
    for c in order:
        L, lv, i = labels[c]
        d = P[c]["d"]
        if L == "(T-iv)":
            body = f"(T-iv) — 사유 \"{P[c]['why']}\""
        elif L == "(T0-Holm)":
            body = f"첫째가 (T±) 가 아니므로 **(T0-Holm)** (자체 90 % CI {d['dR']['v']} [{d['dR']['lo90']}, {d['dR']['hi90']}] = 보고 전용)"
        else:
            lo, hi = (d["dR"]["lo95"], d["dR"]["hi95"]) if lv == 95 else (d["dR"]["lo90"], d["dR"]["hi90"])
            body = f"{d['dR']['v']} [{lv}% {lo}, {hi}] → **{L}**"
        hr = (H or {}).get("rows", {}).get(c)
        chk = (f"; 도우미 `{esc(hr['label'])}` ({cite(H['rel'], hr['ln'])}) " + ("같음" if hr["label"].split()[0] == L else judge(f"{c}: Holm 도우미와 등록 규칙 적용이 다르다 — 등록 규칙이 우선"))) \
            if hr else ("; " + (miss(f"{RV}/nscale_P2_holm.txt") if H is None else badfmt(H["rel"], "?", f"{c} 줄 없음")))
        w(f"- **{c} ({'첫째' if i == 0 else '둘째'}, {lv} %)**: {body}{chk}.")
    w("")
    # labels + qualifiers
    w("**1차 라벨 (§2.2 문구 그대로)과 한정어 (Q-OP·Q-K; (T±) 일 때 반드시 붙임, (T0) 에서는 줄만 보고)**:")
    X.res["qual"] = {}
    for c in ("C2", "C6"):
        L, lv, i = labels[c]
        T = P[c]["T"]
        b = BASE[c]
        if L == "(T-iv)":
            w(f"- **{c} — (T-iv)**: \"판정하지 못함 ({P[c]['why']})\" ({X.rc(r'\(T-iv\) 가드 발동', '§2.2 (T-iv) 행')}). 한정어 없음 (실행 (a) 는 P2 rc 0 일 때만).")
            continue
        q = qual(X, c, lv, L)
        X.res["qual"][c] = q
        pts = [base_gn(X, c), pt_gn(X, T)]
        G = gn_text(X, pts)
        if L in ("(T+)", "(T−)"):
            s = sentence_T(X, c, L, b["n"], int(X.pt(T)["ntrain"]), X.pt(T).get("gate"))
            w(f"- **{c} — {L}**: {s} + G_N {G} + Q-OP {q['qop']} + Q-K {q['qk']}.")
        elif L == "(T0)":
            w(f"- **{c} — (T0)**: **\"판정하지 못함 (방향 없음)\"**. 동등성의 증거가 아니다; (T0) 은 이 설계의 예상 결과다 (§0.3 검정력) — 그것이 \"예산과 무관하다\" 의 증거가 아니다 "
              f"({X.rc(r'\(T0\) 은 이 설계의 \*\*예상 결과\*\*다', '§2.4')}). {lines_only(q)}")
        else:
            w(f"- **{c} — (T0-Holm)**: **\"판정하지 못함 (Holm 첫째 미판정)\"** (자체 90 % CI 는 위 Holm 줄, 보고 전용). {lines_only(q)}")
        for r in q["rows"]:
            w(f"  - {r}")
    w(f"- 기준 C2 끝의 c_K = 2.02 는 이미 알려진 값이다 (공개 2; {X.rc(r'기준 C2 끝의 c_K = 2\.02 는 이미 알려진 값이다', '§2.2 Q-K')}). Q-K 는 1차에만 붙이고 2차에는 붙이지 않는다.")
    w("")


def sec_secondary(X, w):
    F = X.F
    w("#### 6.1.3 2차 (측정, 90 %, 보정 없음; §1 2차 행, §2.2 (E)·§2.3)")
    w("")
    if X.FB == "1":
        w("- (S) 단계: **F1 → 2차 단계 S1·S2 는 채점하지 않는다** (S1 이 1차가 됨; §1 F1, §2.3 머리).")
    else:
        res = {}
        for k, a, b2, gk in (("S1", "3.2e5", "6.4e5", "S1"), ("S2", "6.4e5", "1.28e6", "S2")):
            rel = f"{RV}/nscale_{k}_C2.txt"
            d = parse_fr(F, rel)
            fr = (X.lg or {}).get("fr", {}).get(f"nscale_{k}_C2")
            gv = X.gates()[gk]
            why = "수용 실패" if gv is False else ""
            if any((X.pt(T_) or {}).get("fail") for T_ in {"S1": ("B64e4",), "S2": ("B128e4", "B64e4")}[k]):
                why = "학습 실패 / 적합 실패 (§5)"
            note = (" " + judge(f"{k}: 수용 파일 일부 없음 — 게이트 확인")) if gv is None else ""
            if d is None:
                res[k] = None
                w(f"- **{k} ({a}→{b2})**: " + (f"`L:{fr['ln']}` `{esc(fr['txt'][:100])}` → \"C2 {a}→{b2} 판정하지 못함 ({why or '출력 없음'})\"" if fr else miss(rel)))
                continue
            if d["dR"] is None:
                w(f"- **{k}**: {badfmt(rel, '?', 'dR 줄 없음')}" + (f" (오류 `{esc(d['err'][0][0][:100])}` :{d['err'][0][1]})" if d["err"] else ""))
                res[k] = None
                continue
            for j in (1, 2):
                r = d["R"].get(j)
                if r and (r["b"] <= r["g"] or r["R"] == "nan"):
                    why = why or "정의 불가"
                elif r and r["g"] >= r["v"]:
                    why = why or "범위 밖"
            if d["dR"]["und"] > (d["B"] or 2000) * 0.05:
                why = why or "정의 불가 (정의 불가 복제 > 5 %)"
            lo, hi = fl(d["dR"]["lo90"]), fl(d["dR"]["hi90"])
            L = "판정하지 못함" if why else ("증가" if lo > 0 else "감소" if hi < 0 else "판정하지 못함")
            res[k] = L
            r1, r2 = d["R"].get(1), d["R"].get(2)
            w(f"- **{k} ({a}→{b2})**: R1 {r1['R'] if r1 else '?'} [{r1['lo'] if r1 else '?'}, {r1['hi'] if r1 else '?'}] (`{r1['raw'] if r1 else '?'}`: "
              f"{r1['b'] if r1 else '?'} · {r1['v'] if r1 else '?'} · {r1['g'] if r1 else '?'}), R2 {r2['R'] if r2 else '?'} (`{r2['raw'] if r2 else '?'}`), "
              f"ΔR {d['dR']['v']} [90% {d['dR']['lo90']}, {d['dR']['hi90']}] (95 % 보고 [{d['dR']['lo95']}, {d['dR']['hi95']}]), p {d['dR']['p']}, "
              f"undefined {d['dR']['und']} ({cite(rel, r1['ln'] if r1 else d['dR']['ln'], d['dR']['ln'])}) → **\"C2 {a}→{b2} {L}{(' (' + why + ')') if why else ''}\"**{note}.")
        X.res["steps"] = res
        if res.get("S1") and res.get("S1") == res.get("S2") and res["S1"] in ("증가", "감소"):
            w(f"- 요약 문구 (§2.3): 두 단계 모두 \"{res['S1']}\" → **\"단조 {res['S1']}\"**.")
        else:
            w("- 요약 문구 \"단조 증가/감소\" 는 두 단계가 모두 같은 방향일 때만 — 해당 없음.")
    # (E)
    N2 = X.N2
    rel = f"{RV}/nscale_eff_C2.txt"
    d = parse_fr(F, rel)
    fr = (X.lg or {}).get("fr", {}).get("nscale_eff_C2")
    X.res["E"] = None
    if d is None or not d["pairs"]:
        w(f"- **(E) 데이터 효율**: " + (f"`L:{fr['ln']}` `{esc(fr['txt'][:100])}` → \"판정하지 못함 (수용 실패)\"" if fr and fr["skipped"] else miss(rel)))
    else:
        pr = d["pairs"][0]
        A_, B_ = (pr["specs"] + [None, None])[:2]
        de = pr.get("delta")
        n2 = int(X.pt(N2)["ntrain"]) if X.ptok(N2) else None
        G = gn_text(X, [pt_gn(X, N2)]) if X.ptok(N2) else judge("G_N (N2 점 없음)")
        if de is None:
            w(f"- **(E)**: {badfmt(rel, '?', 'Delta 줄 없음')}")
        elif de.get("na"):
            X.res["E"] = dict(state="na", de=de)
            w(f"- **(E)**: `Delta … n/a {esc(de['na'])}` ({cite(rel, de['ln'])}) → **\"판정하지 못함 (정의 불가)\"**.")
        else:
            lo, hi, cen = fl(de["lo90"]), fl(de["hi90"]), fl(de["cens"])
            if cen > 5:
                s = "**\"판정하지 못함 (정의 불가)\"** (검열 복제 > 5 %)"
            elif lo > 0 or hi < 0:
                s = (f"**\"C2 에서 N′ = 1.6e5 로 학습한 V1 (D1 형제 게이트 PASS 레시피, 헤드라인 legacy-last 가중치) 이 {n2 // 160000 if n2 else '?'} 배의 데이터로 적합한 b\\* "
                     f"(N′ = {nf(n2) if n2 else '?'}) 보다 SNR@0.1 이 {de['v'].lstrip('+-')} dB {'낮다' if lo > 0 else '높다'} (같은 테스트 시행, raw 사이 비짝 90 % CI)\"** + G_N {G}")
            else:
                s = "**\"판정하지 못함\"**"
            X.res["E"] = dict(state="ok", de=de, lo=lo, hi=hi, cen=cen, A=A_, B=B_)
            w(f"- **(E) 데이터 효율** ({cite(rel, A_['ln'] if A_ else de['ln'], de['ln'])}): A = `{A_['raw'] if A_ else '?'}` {A_['arm'] if A_ else ''} SNR@0.1 {A_['v'] if A_ else '?'} dB "
              f"[90% {A_['lo'] if A_ else '?'}, {A_['hi'] if A_ else '?'}; censored {A_['cens'] if A_ else '?'}%], B = `{B_['raw'] if B_ else '?'}` {B_['arm'] if B_ else ''} "
              f"{B_['v'] if B_ else '?'} dB; Δ = A − B = {de['v']} dB [90% {de['lo90']}, {de['hi90']}] (95 % 보고 [{de['lo95']}, {de['hi95']}]), p {de['p']}, "
              f"censored {de['cens']}% → {s}" + (f"; `L:{fr['ln']}` rc={fr['rc']}" if fr else "") + ".")
    w("- (R) C6 회수율 대역은 P1 C6 기록의 일부 (§6.1.1).")
    w("")


def sec_sn(X, w):
    w("#### 6.1.4 합성 문장 S_N (원고용; §2.2 S_N — 조건은 동결 때 고정)")
    w("")
    fb1 = X.FB == "1"
    newc2 = ["B64e4"] + ([] if fb1 else ["B128e4"])
    k, reasons = 4, []
    for T in newc2:
        r = X.res["p1"].get(T, {})
        st = r.get("state")
        if st == "ok" and r["pass_"]:
            k += 1
            if r["gate"] == "FAIL":
                reasons.append(f"{T} '통과' (D1 게이트 FAIL → '예산 축 측정' 표기, arm 주장에 쓰지 않음)")
        elif st == "fail":
            reasons.append(f"{T} 통과 아님 (`PT {T} -` (학습·적합 실패))")
        elif st == "acc":
            reasons.append(f"{T} 통과 아님 (수용 실패 (표 B 없음))")
        elif st == "ok":
            reasons.append(f"{T} 통과 아님 (통과 못함 (출력 문자열: `{esc(r['blk']['guard'])}` / `{esc(r['blk']['l5'])}`))")
        else:
            reasons.append(f"{T} 통과 아님 (" + judge(f"{T} P1 출력 없음 — 사유") + ")")
    n = 5 if fb1 else 6
    w(f"- **C2** 점 집합 = `FALLBACK {X.FB}` → " + ("{1e4, 4e4, 1.6e5, 3.2e5, 6.4e5} (n = 5, 64 배; 문장 끝 \"(F1: 1.28e6 미실행)\")" if fb1 else
                                                 "{1e4, 4e4, 1.6e5, 3.2e5, 6.4e5, 1.28e6} (n = 6, 128 배)")
      + f"; 기준점 4 개는 기록값으로 '통과' 고정 ({X.rc(r'기준점 몫은 기록값으로 지금 고정한다', '§2.2 S_N')}); 새 점: {', '.join(reasons) or '모두 통과'}.")
    unk2 = [T for T in newc2 if X.res["p1"].get(T, {}).get("state") in (None, "missing")]
    if unk2:
        w("  - **S_N (C2)**: " + judge("입력 없음 (" + ", ".join(unk2) + " 의 P1) — S_N 성립 여부와 개수 문장을 정할 수 없다"))
    elif k == n:
        Gs = judge("S_N 의 G_N 목록 — 새 점 몫은 아래, 1e4·4e4·1.6e5·3.2e5 의 격자 끝·tol 정지는 §0.1 표·§0.4 에서 옮길 것")
        w(f"  - **S_N (C2) 성립**: \"D2 C2 에서 동일예산 표 B `b* → V1` 이 N′ = 1e4 … {'6.4e5 (64' if fb1 else '1.28e6 (128'} 배) 의 등록된 모든 예산 점에서 '통과' (C6 의 (i) 에 해당) 이다 "
          "(1e4·4e4 는 D1 형제 게이트 FAIL = 예산 축 측정, 1.6e5·3.2e5 는 PASS 레시피, 새 점은 §5 게이트대로; 게이트 FAIL 인 새 점은 표 B 가 통과여도 '예산 축 측정' 으로 표기하고 "
          f"arm 주장에는 쓰지 않는다 (§2.1 FAIL 행))\"{' (F1: 1.28e6 미실행)' if fb1 else ''} + G_N (새 점 몫: {gn_text(X, [pt_gn(X, T) for T in newc2])}) {Gs}.")
    else:
        w(f"  - **S_N (C2) 불성립** → 개수 문장: **\"위 집합 {n} 개 예산 점 중 {k} 개에서 통과\"** ({'; '.join(r for r in reasons if '통과 아님' in r)}).")
    r6 = X.res["p1"].get("NR16B64e4", {})
    unk6 = r6.get("state") in (None, "missing")
    if unk6:
        w("- **C6**: " + judge("입력 없음 (NR16B64e4 의 P1) — S_N (C6) 를 정할 수 없다"))
    elif r6.get("state") == "ok" and r6["lab"] == "(i)":
        bd = band(X, "NR16B64e4")[1]
        w(f"- **C6**: `NR16B64e4` = (i) → **S_N (C6) 성립**: \"D2 C6 에서 N′ = 1e4 … 6.4e5 (64 배) 의 모든 예산 점에서 (i) (UNGATED 측정)\" + {bd} + G_N "
          f"{gn_text(X, [pt_gn(X, 'NR16B64e4')])} {judge('S_N (C6) G_N 의 1e4·1.6e5 몫 (§0.2 표)')}.")
    else:
        why = {"fail": "`PT NR16B64e4 -`", "acc": "수용 실패"}.get(r6.get("state"), r6.get("lab", "출력 없음"))
        w(f"- **C6**: `NR16B64e4` 가 (i) 아님 ({why}) → 개수 문장 **\"위 집합 3 개 예산 점 중 2 개에서 (i)\"** (C6 n = 3 {{1e4, 1.6e5, 6.4e5}}, 기준점 2 개 고정).")
    X.res["SN"] = dict(c2=None if unk2 else (k == n), c6=None if unk6 else (r6.get("state") == "ok" and r6.get("lab") == "(i)"), k=k, n=n)
    i = X.regl(r"^- \*\*다중성 문장\*\*")
    if i:
        w(f"- **집계 (§2.4 다중성 문장 그대로, {cite(REG, i)})**: {X.reg[i - 1].split('**:', 1)[1].strip()}")
    w("")


def rec_cells(X, T):                                    # (-3 dB row, pooled -3/0/+3) from recovery_<T>.txt
    rel = f"{RV}/recovery_{T}.txt"
    r = parse_rec(X.F, rel)
    if r is None:
        return None, None, rel
    m3 = next((x for b in r["blocks"] for x in b["rows"] if x["snr"] == -3), None)
    pl = next((b["pooled"] for b in r["blocks"] if b["pooled"] and b["pooled"]["k"] == 3), None)
    return m3, pl, rel


def sec_report(X, w):
    F = X.F
    w("#### 6.1.5 보고 전용 (§1 보고 전용 행; 라벨에 쓰지 않음)")
    w("")
    w("(a) **예산 곡선 (기준점 행 = §0.1·§0.2 표 그대로 옮김; 새 점 = 이 실행)**:")
    w("")
    w("| 셀 · N′ (raw, 가중치) | b\\* | b\\* −3 dB | V1 −3 dB | 표 B b\\*→V1 pooled | SNR@0.1 격차 [90%] | D1 게이트 | **R** [90% paired] (ΣF b\\* / V1 / genie) | R(−3 dB) [90%] | 출처 |")
    w("|---|---|---|---|---|---|---|---|---|---|")
    for sec, rows_rx in (("0.1", r"^\| (1e4|4e4|1\.6e5|3\.2e5) \(`raw_"), ("0.2", r"^\| (1e4|1\.6e5) \(`raw_")):
        i0 = X.regl(rf"^### {re.escape(sec)} ")
        cell = "C2" if sec == "0.1" else "C6"
        if i0 is None:
            w(f"| {cell} 기준점 | {badfmt(REG, '?', f'§{sec} 표 없음')} | | | | | | | | |")
            continue
        for k in range(i0, len(X.reg)):
            l = X.reg[k]
            if sec == "0.1" and l.startswith("### 0.2"):
                break
            if sec == "0.2" and l.startswith("### 0.3"):
                break
            if re.match(rows_rx, l):
                c = [x.strip() for x in l.strip().strip("|").split("|")]
                if sec == "0.1" and len(c) >= 8:
                    w(f"| {cell} {c[0]} | {c[1]} | {c[2]} | {c[3]} | {c[4]} | — | {c[5]} | {c[6]} | — | {cite(REG, k + 1)} |")
                elif sec == "0.2" and len(c) >= 7:
                    w(f"| {cell} {c[0]} | {c[1]} | ({c[2]}) | | {c[3]} | — | UNGATED | {c[4]} | {c[5]} | {cite(REG, k + 1)} |")
    for T, cell, n in NEWPTS:
        if not X.ptok(T):
            w(f"| {cell} {nf(n)} (`raw_{T}`) | — | — | — | — | — | — | 실행 안 함 (S5) | | |")
            continue
        p = X.pt(T)
        for tag, wt in ((T, f"`_best` {p['bsha']}"), (T + "last", f"last-EMA {p['lsha']}")):
            trel = f"results/tables_D2_{tag}.txt"
            ab, av = tableA(F, trel, BS), tableA(F, trel, V1)
            blk, _ = blockB(F, trel, PV1)
            m3, pl, rrel = rec_cells(X, tag)
            if F.lines(trel) is None and m3 is None and pl is None:
                w(f"| {cell} {nf(n)} (`raw_{tag}`, {wt}) | {miss(trel)} {miss(rrel)} | | | | | | | | |")
                continue

            def i3(a):                                  # table A BLER (95% Wilson) at -3 dB
                if not a or -3 not in a["snrs"] or a["snrs"].index(-3) >= len(a["vals"]):
                    return "—"
                v = a["vals"][a["snrs"].index(-3)]
                return f"{v[0]} ({v[1]}, {v[2]})"
            src = [cite(trel, ab["ln"]) if ab else "", cite(trel, av["ln"]) if av else "", cite(trel, blk["ln"], blk["end"]) if blk else "",
                   cite(rrel, m3["ln"]) if m3 else "", cite(rrel, pl["ln"]) if pl else ""]
            w(f"| {cell} {nf(n)} (`raw_{tag}`, {wt}) | {p['bs']} {p['kk']} ({cite(S5R, p['ln'])}) | {i3(ab)} | {i3(av)} | "
              f"{(blk['pooled'][0] + ':' + blk['pooled'][1]) if blk and blk['pooled'] else ('n/a (analysis 미실행)' if F.lines(trel) is None else '—')} | "
              f"{esc(blk['gap']) if blk else '—'} | {p['gate']} | "
              f"{(pl['R'] + ' [' + pl['lo'] + ', ' + pl['hi'] + '] (' + str(pl['b']) + ' / ' + str(pl['v']) + ' / ' + str(pl['g']) + ')') if pl else miss(rrel)} | "
              f"{(m3['R'] + ' [' + m3['lo'] + ', ' + m3['hi'] + ']') if m3 else '—'} | {' '.join(s for s in src if s)} |")
    w("")
    w("(기준점 행의 칸 이름은 §0.1/§0.2 표의 칸을 옮긴 것이다 (§0.2 의 −3 dB 칸은 실패 수 원문). b\\* −3 dB·V1 −3 dB = `tab_<T>` 표 A 의 BLER (95% Wilson). "
      "R 의 CI 는 `recovery_ci` (paired); frontier 의 R1 CI 와 셋째 자리가 다를 수 있다.)")
    sn01 = []
    for T, cell, n in NEWPTS:
        trel = f"results/tables_D2_{T}.txt"
        v = [(arm, snr01(F, trel, a_)) for arm, a_ in (("b\\*", BS), ("V1", V1), ("genie", GE))] if X.ptok(T) and F.lines(trel) else []
        if v:
            sn01.append(f"{T} " + " · ".join(f"{arm} {x[0]} (:{x[1]})" if x else f"{arm} ?" for arm, x in v))
    if sn01:
        w(f"- SNR@0.1 (dB; `tab_<T>` 의 SNR@BLER 0.1 표, '<=x'·'>x' 는 격자 밖 그대로): " + "; ".join(sn01) + ".")
    w("")
    # (b) ll ladder
    w("(b) **GMM ll 사다리 (`prep` = §5; 병합 ll_val, 선택 재시작의 정지·재시드·sec·경로)**:")
    if X.prep is None:
        w(f"- {miss(PREPR)}")
    else:
        for T, cell, n in NEWPTS:
            pp = X.prep.get(T)
            if not pp:
                w(f"- {T}: {badfmt(PREPR, '?', f'{T} 절 없음')}")
                continue
            g = pp["grid"]
            kr = [g[k] for k in sorted(g) if k[0] == "kron"]
            fu = [g[k] for k in sorted(g) if k[0] == "full"]
            l4, l2, l1 = (g.get(("kron", K)) for K in (4096, 2048, 1024))
            d42 = fl(l4["ll"]) - fl(l2["ll"]) if l4 and l2 else None
            d21 = fl(l2["ll"]) - fl(l1["ll"]) if l2 and l1 else None
            stops = {}
            for x in g.values():
                stops[x["stop"]] = stops.get(x["stop"], 0) + 1
            w(f"- **{T}** (`prep:{pp['ln']}`–): kron " + ", ".join(f"{K}: {x['ll']}" for K, x in zip([k[1] for k in sorted(g) if k[0] == 'kron'], kr))
              + "; full " + ", ".join(f"{K}: {x['ll']}" for K, x in zip([k[1] for k in sorted(g) if k[0] == 'full'], fu))
              + (f" ({cite(PREPR, min(x['ln'] for x in g.values()), max(x['ln'] for x in g.values()))})" if g else "")
              + f"; Δll(4096 − 2048) = {d42!r}, Δll(2048 − 1024) = {d21!r} (기록자 산술, Python float)"
              + (f"; `{esc(pp['qk'][0])}` ({cite(PREPR, pp['qk'][1])})" if pp.get("qk") else "")
              + (f"; kron 4096 재시드 {l4['rs']}, 정지 {l4['stop']} ({l4['ni']}/{l4['ib']}), 경로 `{esc(l4['path'])}`, sec {l4['sec']} ({cite(PREPR, l4['ln'])})" if l4 else "")
              + f"; 정지 사유 수 (병합 {len(g)}): {', '.join(f'{k} {v}' for k, v in sorted(stops.items()))}.")
            tr = segrule(pp["train"][0][len("training: "):]) if pp.get("train") else None
            if tr and tr["final"]:
                w(f"  - 학습 (구간 규칙, {cite(PREPR, pp['train'][1])}): 구간 {tr['nseg']} (학습 {tr['ntr']}, GB′ {tr['ngb']}), 최종 `{esc(tr['final'])}`, "
                  f"학습 초 = 학습 구간 wall 합 {tr['wall']:.1f} s" + (f" (죽은 구간 {tr['dead']} — 하한)" if tr["dead"] else "") + (f", 중단 줄 {tr['nab']}" if tr["nab"] else "") + ".")
            em = (X.res.get("rawmeta", {}).get(T) or {}).get("meta|em_sec")
            if em:
                w(f"  - em_sec (raw `meta|em_sec`): {', '.join(sorted(em))}.")
    w("")
    # (c) GB'
    w("(c) **GB′ (재실행본, 보고 전용; `prep`)**:")
    for T, cell, n in NEWPTS:
        pp = (X.prep or {}).get(T, {})
        bits = [f"`{esc(pp[k][0])}` ({cite(PREPR, pp[k][1])})" for k in ("gbcsv", "gbnpz") if pp.get(k)]
        bits += [f"`{esc(x)}` ({cite(PREPR, pp['gblog'][1])})" for x in gblines(pp, T)]
        npz = f"results/d2_gbprime_{'NR16_' if cell == 'C6' else ''}N{n}_a1.npz"
        try:
            with np.load(F.p(npz)) as z:
                rr = z["nmse_model"] / z["nmse_gmm"]
            bits.append(f"npz `{npz}` 의 비 nmse_model/nmse_gmm: min {rr.min():.6f} · max {rr.max():.6f} · median {np.median(rr):.6f}, worst excess (= max − 1) {rr.max() - 1:+.6f} (기록자 산술)")
        except Exception:
            bits.append(miss(npz))
        w(f"- {T}: " + "; ".join(bits) + ".")
    w("")
    w(f"(d) **D1 `_best` 파일 게이트**: §5 D1 형제 행 — \"그 GA~GD 는 재지 않았다 (`run_samplecx.py` 는 last 파일만 잰다)\" "
      f"({X.rc('그 GA~GD 는 재지 않았다', '§5 D1 형제 행')}). 이 기록에서 계산하지 않음.")
    w("")
    # (e) F3 guard + V0/V4/V4b
    w("(e) **F3 가드 발동률·V0·V4·V4b (C2 A)**:")
    for T, cell, n in NEWPTS:
        if cell != "C2" or not X.ptok(T):
            continue
        g = parse_guard(F, T)
        gtxt = (f"NO GUARD FIRINGS ({cite(g['rel'], g['none'])})" if g and g["none"] else
                ("; ".join(f"`{esc(x)}` (:{i})" for x, i in g["rows"][:12]) if g else miss(f"results/guard_D2_{T}.txt")))
        trel = f"results/tables_D2_{T}.txt"
        vs = []
        for arm in ("M-ours-dscore-C-V0", "M-ours-dscore-C-V4", "M-ours-dscore-C-V4b"):
            b, _ = blockB(F, trel, f"{BS} -> {arm}")
            a = tableA(F, trel, arm)
            v3 = a["vals"][a["snrs"].index(-3)][0] if a and -3 in a["snrs"] else "?"
            vs.append(f"{arm.split('-')[-1]}: −3 dB {v3}" + (f", b\\*→{arm.split('-')[-1]} pooled {b['pooled'][0]}:{b['pooled'][1]}, "
                                                          f"{'POWERED ' + str(b['k2']) + '/3 · ' + str(b['k1']) + '/3' if b['powered'] else 'UNDECIDED'} ({cite(trel, b['ln'], b['end'])})" if b and b["pooled"] else ""))
        w(f"- {T}: 가드 {gtxt}; " + "; ".join(vs) + ".")
    w("")
    w("(f) **대조군 `b* → b*-scalar`**: §6.1.1 끝.")
    w("")
    # (g) best vs last
    w("(g) **best 대 last V1 짝 부호검정 (B32e4 §6.2 형식; a = best 실패·last 성공; 기록자 산술 — raw 의 `M-ours-dscore-C-V1|blk_err[:, -1]`, `analysis.paired` 와 같은 셈)**:")
    for T, cell, n in NEWPTS:
        if not X.ptok(T):
            continue
        r = best_last(F, T)
        if r is None:
            w(f"- {T}: {miss(f'raw_{T}/ · raw_{T}last/')}")
            continue
        per = r["per"]
        dec = (X.res["p1"].get(T, {}).get("blk") or {}).get("dec") or []
        lack = [s for s in dec if s not in per]           # C6 last holds -3/0/+3 only
        sa = sum(per[s][0] for s in dec if s in per)
        sb = sum(per[s][1] for s in dec if s in per)
        w(f"- {T} (`raw_{T}` vs `raw_{T}last`, 공유 청크 {r['nfiles'] - r['nmiss']}/{r['nfiles']}): "
          + ", ".join(f"{mn([s])} dB {a}:{b} (p={sign_p(a, b):.2g})" for s, (a, b) in sorted(per.items()))
          + (f"; 판정점 {mn(dec)} 합 {sa}:{sb} (p={sign_p(sa, sb):.2g})" if dec and not lack else "")
          + (f"; 판정점 {mn(dec)} 중 last raw 에 없는 점 {mn(lack)} — 판정점 합은 적지 않음" if lack else "") + ".")
    w("")
    # (h) gaps
    w("(h) **셀별 절대 격차 ΣF_V1 − ΣF_g, ΣF_b\\* − ΣF_g (−3/0/+3 합, 블록 수, 90 %; Q-K 실행 (a) 파일의 `gaps` 줄)**:")
    for c in ("C2", "C6"):
        q = X.res.get("qual", {}).get(c)
        if not q or not q.get("gaps"):
            w(f"- {c}: " + (miss(f"{RV}/nscale_qk_{c}_L95.txt") if not q else "gaps 줄 없음"))
            continue
        for j, gg in sorted(q["gaps"].items()):
            w(f"- {c} R{j} ({'새' if j == 1 else '기준'}): {gg['vg']} [90% {gg['vlo']}, {gg['vhi']}] / {gg['bg']} [90% {gg['blo']}, {gg['bhi']}] ({cite(q['fa'], gg['ln'])})")
    w("")
    # (i) last tags
    w("(i) **`<T>last` (last-EMA, 보고 전용) 의 R [90% paired] 와 무결성 줄 `b* last == A`**:")
    for T, cell, n in NEWPTS:
        if not X.ptok(T):
            continue
        rel = f"{RV}/recovery_{T}last.txt"
        r = parse_rec(F, rel)
        if r is None:
            w(f"- {T}last: {miss(rel)}")
            continue
        pl = next((b["pooled"] for b in r["blocks"] if b["pooled"]), None)
        rows = [x for b in r["blocks"] for x in b["rows"]]
        integ = (X.lg or {}).get("integ", {}).get(f"b* {T}last == {T}")
        w(f"- {T}last: R {pl['R']} [90% {pl['lo']}, {pl['hi']}] ({pl['b']} · {pl['v']} · {pl['g']}; {cite(rel, pl['ln'])})" if pl else f"- {T}last: {badfmt(rel, '?', 'pooled 줄 없음')}")
        if rows:
            w("  - 점별 R(last): " + " · ".join(f"{mn([x['snr']])} {x['R']} [{x['lo']}, {x['hi']}]" for x in rows) + f" ({cite(rel, rows[0]['ln'], rows[-1]['ln'])})")
        w(f"  - 무결성 줄: " + (f"`{esc(r['same']['txt'])}` ({cite(rel, r['same']['ln'])})" if r["same"] else badfmt(rel, "?", "same 줄 없음"))
          + (f"; `L:{integ[1]}` rc={integ[0]}" if integ else "") + " (게이트 아님).")
    w("")
    # (j) K8
    w("(j) **kron 8192 (보고 전용; 어떤 등록 b\\* 에도 들어가지 않음 — 공개 8)**:")
    pp = (X.prep or {}).get("B64e4", {})
    k8 = (X.s5 or {}).get("K8")
    for key in ("k8", "draftk8"):
        if pp.get(key):
            w(f"- `{esc(pp[key][0])}` ({cite(PREPR, pp[key][1])})")
    for (fam, K), x in sorted(pp.get("k8grid", {}).items()):
        w(f"- K8 적합 `{fam} K={K}` ll_val {x['ll']} (r{x['r']}; {x['ni']}/{x['ib']} {x['stop']}; 재시드 {x['rs']}; sec {x['sec']}; 후보 {x['cand']}; `{esc(x['path'])}`) ({cite(PREPR, x['ln'])})")
    w(f"- S5: " + (f"`K8 {k8['k']} {k8['ll']} {k8['run']}` ({cite(S5R, k8['ln'])})" if k8 else (miss(S5R) if X.s5 is None else badfmt(S5R, "?", "K8 줄 없음"))))
    if k8 and k8["run"] == "1":
        rel = f"{RV}/nscale_K8.txt"
        d = parse_fr(F, rel)
        if d and d["dR"]:
            r1, r2 = d["R"].get(1), d["R"].get(2)
            w(f"- `--paired raw_B64e4k8 raw_B64e4`: ΣF_b\\*(8192) {r1['b'] if r1 else '?'} vs ΣF_b\\*(4096) {r2['b'] if r2 else '?'} (−3/0/+3 합; V1 {r1['v'] if r1 else '?'}/{r2['v'] if r2 else '?'}, "
              f"genie {r1['g'] if r1 else '?'}/{r2['g'] if r2 else '?'}), ΔR {d['dR']['v']} [90% {d['dR']['lo90']}, {d['dR']['hi90']}] [95% {d['dR']['lo95']}, {d['dR']['hi95']}], "
              f"p {d['dR']['p']} ({cite(rel, r1['ln'] if r1 else d['dR']['ln'], d['dR']['ln'])}) — ΔR 은 b\\* 만의 차이.")
            X.res["K8"] = d
        else:
            w(f"- {miss(rel) if d is None else badfmt(rel, '?', 'dR 줄 없음')}")
        rv = parse_rec(F, f"{RV}/nscale_K8_V1.txt")
        il = (X.lg or {}).get("integ", {}).get("V1 B64e4k8 == B64e4")
        w(f"- V1 무결성 (`nscale_K8_V1.txt`, 게이트 아님): " + (f"`{esc(rv['same']['txt'])}` ({cite(rv['rel'], rv['same']['ln'])})" if rv and rv["same"] else miss(f"{RV}/nscale_K8_V1.txt"))
          + (f"; `L:{il[1]}` rc={il[0]}" if il else ""))
        r = parse_runner(F, "B64e4k8")
        w(f"- 첫 청크 RSS (§1 비용 행 \"첫 청크 RSS 를 §6 전사 때 적는다\"): runner 로그의 RSS 줄 {len(r['rss']) if r else 0} 개"
          + (f" ({', '.join(f'`run_B64e4k8:{i}`' for i in r['rss'])})" if r and r["rss"] else " — " + judge("RSS 가 기록되지 않음 (run_nscale.sh·runner 가 RSS 를 찍지 않는다); 편차로 적을지")) + ".")
    elif k8:
        w(f"- K8 run 0 → `B64e4k8` 미실행 (F5; §1 대체 규칙).")
    w("")
    # (k) E128
    rel = f"{RV}/nscale_eff128_C2.txt"
    d = parse_fr(F, rel)
    w("(k) **E128 (`--pair` b\\*@N2 vs V1@1e4; V1 @ 1e4 는 D1 게이트 FAIL = 예산 축 측정 — 공개 12)**: " + (
        (" / ".join(f"{s['name']} `{s['raw']}` {s['arm']} SNR@0.1 {s['v']} dB [90% {s['lo']}, {s['hi']}; censored {s['cens']}%] (:{s['ln']})" for s in d["pairs"][0]["specs"])
         + ("; Δ " + (f"{d['pairs'][0]['delta']['v']} dB [90% {d['pairs'][0]['delta']['lo90']}, {d['pairs'][0]['delta']['hi90']}], p {d['pairs'][0]['delta']['p']}, censored {d['pairs'][0]['delta']['cens']}%"
                      if not d['pairs'][0]['delta'].get('na') else f"n/a {esc(d['pairs'][0]['delta']['na'])}") + f" ({cite(rel, d['pairs'][0]['delta']['ln'])})" if d["pairs"][0].get("delta") else ""))
        if d and d["pairs"] else miss(rel)) + ".")
    w("")
    i = X.regl(r"시드 산포 \(SEEDS16e4")
    w(f"(l) **시드 산포 캐비엇**: §0.1 의 SEEDS16e4 줄 ({cite(REG, i) if i else badfmt(REG, '?', 'SEEDS16e4 줄')}) 그대로 — 시드 분산은 부트스트랩에 없다 (공개 3).")
    w("")
    w("(m) **이 기록에서 계산하지 않은 보고 전용 항목** (`run_nscale.sh` 가 출력하지 않고, 이 생성기는 결과 뒤 새 통계를 만들지 않는다): 기존 예산 (1e4·4e4·1.6e5) 과 새 점 사이의 짝 ΔR "
      "(§0.3 형식 — P2·S1·S2·K8 줄만 있음), D1 `_best` 파일의 GA~GD.")
    w("")


def sec_41(X, w):
    w("#### 6.1.6 §4.1 이관분 (§1 비용 행·§4.1 표가 §6 으로 미룬 값 — §0–§5 는 편집하지 않으므로 여기 적는다)")
    tot, parts = 0.0, []
    for T in NEWRAW:
        r = parse_runner(X.F, T)
        if r and r["fin"]:
            m = fl(r["fin"][-1][0])
            tot += m
            parts.append(f"{T} {r['fin'][-1][0]}")
    w(f"- 태그 소요 합 (runner `finished in` — 줄 번호는 위 runner 표, 기록자 합산): {tot:.1f} min = {tot / 60:.2f} h ({', '.join(parts) or '로그 없음'}); §1 비용 행 추정 "
      f"\"합 ≈ 7.5–9.5 h\" ({X.rc(r'합 ≈ 7\.5–9\.5 h', '합 ≈ 7.5–9.5 h')}). eval 전체 경과는 위 실행 절.")
    w("- B64e4k8 첫 청크 RSS: §6.1.5 (j).")
    w("")


def sec_fallback(X, w):
    w("#### 6.1.7 대체 규칙 상태 (§1 대체 규칙 행; 판정 근거는 적합·학습·검사 사실뿐 — §5 그대로)")
    s5, pp = X.s5, X.prep or {}
    if s5 is None:
        w(f"- {miss(S5R)}")
        w("")
        return
    w(f"- **F1**: `FALLBACK {X.FB}` ({cite(S5R, s5['FALLBACK'][1]) if s5['FALLBACK'] else '?'}); `PT B128e4` = "
      + ("`-`" if (X.pt("B128e4") or {}).get("fail") else "14 필드") + (f" ({cite(S5R, X.pt('B128e4')['ln'])})" if X.pt("B128e4") else "") + ".")
    w(f"- **F2** (C6 6.4e5 실패): `PT NR16B64e4` " + ("`-` → ΔR_C6 (T-iv)" if (X.pt("NR16B64e4") or {}).get("fail") else "정상 → 미발동") + ".")
    fb = [p["stem"] for p in (s5["PT"] or {}).values() if not p.get("fail") and re.search(r"_fb[23]$", p.get("stem", ""))]
    w(f"- **F3** (발산 → §3d): S5 stem 의 `_fb<k>` {fb or '없음'}; `prep` 의 `other attempts of this stem`: "
      + "; ".join(f"{T} `{esc(pp[T]['other'][0])}` ({cite(PREPR, pp[T]['other'][1])})" for T, _, _ in NEWPTS if pp.get(T, {}).get("other")) + ".")
    w(f"- **F4** (일괄 검사 FAIL): " + "; ".join(f"{T} `{esc(pp[T]['bc'][0])}` ({cite(PREPR, pp[T]['bc'][1])})" for T, _, _ in NEWPTS if pp.get(T, {}).get("bc")) + ".")
    k8 = s5.get("K8")
    if k8:
        why = "b\\* = kron 8192 → 실행" if k8["run"] == "1" else ("`PT B64e4 -`" if not X.ptok("B64e4") else
                                                              "b\\* 아님 (K8 집합 b\\* = kron " + k8["k"] + ")" if k8["k"] not in ("-", "8192") else judge("F5 사유 (OOM / 미완료) — 적합 로그 확인"))
        w(f"- **F5** (kron 8192): `K8 {k8['k']} {k8['ll']} {k8['run']}` ({cite(S5R, k8['ln'])}) — {why}.")
    else:
        w(f"- **F5**: {badfmt(S5R, '?', 'K8 줄 없음') if not s5.get('k8c') else badfmt(S5R, s5['k8c'][1], '주석 K8 줄만 있음 (병합 대기 자리표시)')}")
    w(f"- **F6** (GB′): " + "; ".join(f"{T} `GMM b* =` 줄 {len(gblines(pp.get(T, {}), T))} 개" + (f" ({cite(PREPR, pp[T]['gblog'][1])})" if pp.get(T, {}).get('gblog') else "")
                                       for T, _, _ in NEWPTS) + " (실패해도 보고 항목이 빌 뿐; §6.1.5 (c)).")
    w("")


def regpred(X, n):
    i = X.regl(rf"^{n}\. \*\*")
    return i, (X.reg[i - 1] if i else "")


def sec_predictions(X, w):
    fb1 = X.FB == "1"
    w("#### 6.1.8 §3 예측 채점 (적중/빗나감 이분; 범위 밖은 빗나감; F1 이면 1.28e6 몫은 '채점하지 않음 (F1)'; '동결 전 확인' 은 채점 제외)")
    w("")
    w("| # | 예측 (요지, 등록 줄) | 결정하는 수 | 채점 |")
    w("|---|---|---|---|")
    tally = {"적중": [], "빗나감": [], "제외": [], "판단": []}

    def row(n, ev, sc, key):
        i, txt = regpred(X, n)
        m = re.match(rf"^{n}\. \*\*(.+?)\*\*", txt)
        w(f"| {n} | {esc(m[1]) if m else '?'} ({cite(REG, i) if i else badfmt(REG, '?', f'예측 {n} 줄')}) | {ev} | {sc} |")
        tally[key].append(n)

    def inr(n, s, v):                                   # v in the closed range s, s exactly as written on prediction n's registration line
        if s not in regpred(X, n)[1]:
            return f"∈ {s} (등록 줄에 이 문구 없음)", None
        a, b = (fl(x) for x in s.strip("[]").split(", "))
        return f"∈ {s}", a <= v <= b

    def has(n, s):                                      # a threshold text ('< 3170', '≥ 0.70') must still be on the line
        return s in regpred(X, n)[1]

    def score(n, parts, f1parts=()):
        ev = "; ".join(f"{d} {'✓' if ok else '✗' if ok is False else '?'}" for d, ok in parts)
        if f1parts:
            ev += ("; " if ev else "") + "; ".join(f"{d}: 채점하지 않음 (F1)" for d in f1parts)
        if not parts:
            return row(n, ev or "—", "채점하지 않음 (F1)", "제외")
        if any(ok is None for _, ok in parts):
            return row(n, ev, judge(f"예측 {n}: 입력 없음·형식·경계 — 채점 보류"), "판단")
        hit = all(ok for _, ok in parts)
        return row(n, ev, "**적중**" if hit else "**빗나감**", "적중" if hit else "빗나감")

    pp = X.prep or {}
    pts = [T for T, _, _ in NEWPTS]
    f1 = lambda T: fb1 and T == "B128e4"
    # 1 -- 동결 전 확인 (§3 머리말·§4.1)
    bcs = [f"{T} `{esc(pp[T]['bc'][0])}` ({cite(PREPR, pp[T]['bc'][1])})" for T in pts if pp.get(T, {}).get("bc")]
    row(1, "; ".join(bcs) or miss(PREPR), "동결 전 확인 (세 개 모두 PASS, §0.5) — 적중·빗나감 어느 쪽으로도 세지 않음"
        if len(bcs) == 3 and all("VERDICT: PASS" in b for b in bcs) else judge("예측 1: 동결 전 확인 값 대조"), "제외")
    # 2
    parts, fp = [], []
    for T, s in (("B64e4", "[+1.5, +3.5]"), ("B128e4", "[+1.5, +4.0]"), ("NR16B64e4", "[+0.8, +3.0]")):
        if f1(T):
            fp.append(T)
            continue
        p, g = X.pt(T), pp.get(T, {}).get("grid", {})
        if not p or p.get("fail") or not g:
            parts.append((f"{T} 입력 (S5·prep)", None))
            continue
        l4, l2 = g.get(("kron", 4096)), g.get(("kron", 2048))
        fmax = max((fl(x["ll"]) for k, x in g.items() if k[0] == "full"), default=float("nan"))
        d = fl(l4["ll"]) - fl(l2["ll"]) if l4 and l2 else float("nan")
        t, ok = inr(2, s, d)
        parts += [(f"{T} b\\* = {p['bs']} {p['kk']} ({cite(S5R, p['ln'])})", p["bs"] == "kron" and p["kk"] == "4096"),
                  (f"full 최고 {fmax!r} 가 b\\* {p['ll']} 보다 {fl(p['ll']) - fmax:.3f} nat 낮음 (≥ 3)", fl(p["ll"]) - fmax >= 3),
                  (f"Δll(4096−2048) {d:.4f} {t} ({cite(PREPR, l4['ln']) if l4 else '?'})", ok),
                  (f"c_K {p['ck']} (r < 1)", p["ck"] not in ("inf", "-")), (f"K2 {p['k2k']} (구성 가능)", p["k2k"] == "2048")]
    score(2, parts, fp)
    # 3
    parts, fp = [], []
    for T, s in (("B128e4", "< 3170"), ("NR16B64e4", "< 85594")):
        if f1(T):
            fp.append(T)
            continue
        g = pp.get(T, {}).get("grid", {}).get(("kron", 4096))
        lim = int(s.split()[1])
        parts.append((f"{T} kron 4096 재시드 {g['rs']} {s} ({cite(PREPR, g['ln'])})" if g else f"{T} 입력",
                      ((g["rs"] < lim) if has(3, s) else None) if g else None))
    score(3, parts, fp)
    # 4
    k8, kl = (X.s5 or {}).get("K8"), pp.get("B64e4", {}).get("k8")
    if kl:
        m = re.search(r"dll\(8192-4096\) ([+-][\d.]+)", kl[0])
        dd = fl(m[1]) if m else float("nan")
        t, ok = inr(4, "[+0.5, +2.5]", dd)
        score(4, [(f"Δll(8192−4096) {m[1] if m else '?'} > 0 ({cite(PREPR, kl[1])})", dd > 0), (f"Δll {t}", ok),
                  (f"K8 run = {k8['run'] if k8 else '?'}" + (f" ({cite(S5R, k8['ln'])})" if k8 else ""), (k8["run"] == "1") if k8 else None)])
    else:
        row(4, "`prep` 에 K8 줄 없음 (병합 kron 8192 적합 없음)" + (f"; S5 `K8 {k8['k']} {k8['ll']} {k8['run']}`" if k8 else ""),
            judge("예측 4: kron 8192 병합 적합이 없으면 (F5) 빗나감으로 셀지"), "판단")
    # 5 -- not in §3's F1 exclusion list: the 1.28e6 trainings are scored, and F1 itself is scored here ('F1 미발동') and in 18 (a)
    parts = []
    for T in pts:
        q = pp.get(T, {})
        tr = segrule(q["train"][0][len("training: "):]) if q.get("train") else None
        fin = re.search(DONE_RX, tr["final"]) if tr and tr["final"] else None
        other = q.get("other", ("",))[0].endswith("none")
        parts.append((f"V1 {T}: `stopped_by={fin[2]}, aborted={fin[3]}`, 다른 시행 {'없음' if other else '있음'} ({cite(PREPR, q['train'][1])})" if fin else f"V1 {T} 입력",
                      (fin[2] == "patience" and fin[3] == "False" and other) if fin else None))
    for T, n in (("B64e4", 640000), ("B128e4", 1280000)):
        ck = pp.get(T, {}).get("d1ck", [])
        tr = segrule(ck[0][0].split("training: ", 1)[1]) if ck and "training: " in ck[0][0] else None
        fin = re.search(DONE_RX, tr["final"]) if tr and tr["final"] else None
        parts.append((f"D1 {nf(n)}: `stopped_by={fin[2]}, aborted={fin[3]}`, last 파일 {len(ck)} 개 ({cite(PREPR, ck[0][1])})" if fin else f"D1 {nf(n)} 입력",
                      (fin[2] == "patience" and fin[3] == "False" and len(ck) == 1) if fin else None))
    parts.append((f"F1 미발동 (`FALLBACK {X.FB}`)", (X.FB == "0") if X.FB else None))
    score(5, parts)
    # 6
    parts, fp = [], []
    for T, n in (("B64e4", 640000), ("B128e4", 1280000)):
        if f1(T):
            fp.append(nf(n))
            continue
        d1 = pp.get(T, {}).get("d1", [])
        m = re.search(r"GC (\S+) .*-> thresholds (\w+)", d1[0][0]) if len(d1) == 1 else None
        if m:
            t, ok = inr(6, "[0.07, 0.11]", fl(m[1]))
            parts.append((f"{nf(n)}: {m[2]}, GC {m[1]} {t} ({cite(PREPR, d1[0][1])})", (m[2] == "PASS" and ok) if ok is not None else None))
        else:
            parts.append((f"{nf(n)} D1 행 {len(d1)} 개", None))
    score(6, parts, fp)
    # 7
    parts = [(f"bridge {K} ACCEPT {g3(X.ok3(K))}", X.ok3(K)) for K in ("BRB32e4", "BRNR16B16e4")]
    for T in pts:
        if f1(T) or not X.ptok(T):
            continue
        a = X.a(T)
        parts.append((f"{T}chk ACCEPT {g3(X.ok3(T + 'chk'))}", X.ok3(T + "chk")))
        parts.append((f"{T} genie 재생 (A 파일의 `replay vs` 실패 줄 {sum('replay vs' in x for x, _ in a['fails']) if a else '?'})",
                      (not any("replay vs" in x for x, _ in a["fails"])) if a else None))
    score(7, parts, ["B128e4"] if fb1 else ())
    # 8
    parts, fp = [], []
    for T in pts:
        if f1(T):
            fp.append(T)
            continue
        r = X.res.get("p1", {}).get(T, {})
        b = r.get("blk")
        parts.append((f"{T}: " + (f"POWERED={b['powered']}, second {b['k2']}/3, 판정점 {mn(b['dec'])}" if b else str(r.get("state", "?"))),
                      (b["powered"] and b["k2"] == 3 and b["dec"] == [-3, 0, 3]) if b else (False if r.get("state") in ("fail", "acc") else None)))
    sn = X.res.get("SN", {})
    parts.append((f"S_N C2 {g3(sn.get('c2')).replace('통과', '성립').replace('실패', '불성립')}" + (" (5 점 집합)" if fb1 else ""), sn.get("c2")))
    parts.append((f"S_N C6 {g3(sn.get('c6')).replace('통과', '성립').replace('실패', '불성립')}", sn.get("c6")))
    score(8, parts, fp)
    # 9 (exact = count / n from recovery_ci; the table shows three decimals)
    parts, fp = [], []
    for T, sb in (("B64e4", "[0.222, 0.240]"), ("B128e4", "[0.212, 0.238]")):
        if f1(T):
            fp.append(T)
            continue
        m3, _, rrel = rec_cells(X, T)
        if not m3:
            parts.append((f"{T} 입력", None))
            continue
        for arm, cnt, s in (("V1", m3["v"], "[0.135, 0.155]"), ("b\\*", m3["b"], sb)):
            v = cnt / m3["n"]
            t, ok = inr(9, s, v)
            _, ok3 = inr(9, s, round(v, 3))
            parts.append((f"{T} {arm} {cnt}/{m3['n']} = {v:.4f} {t} ({cite(rrel, m3['ln'])})", ok if ok == ok3 else None))
    score(9, parts, fp)
    # 10
    parts, fp = [], []
    for T, s in (("B64e4", "[0.46, 0.51]"), ("B128e4", "[0.44, 0.50]"), ("NR16B64e4", "[0.76, 0.84]")):
        if f1(T):
            fp.append(T)
            continue
        _, pl, rrel = rec_cells(X, T)
        if not pl:
            parts.append((f"{T} 입력", None))
            continue
        R = rx(pl["b"], pl["v"], pl["g"])
        t, ok = inr(10, s, R)
        parts.append((f"{T} R {pl['R']} (정확 {R:.5f}) {t} ({cite(rrel, pl['ln'])})", ok))
    score(10, parts, fp)
    # 11
    parts, fp, holm_note = [], [], None
    p2 = X.res.get("p2", {})
    for c, s in (("C2", "[−0.06, +0.01]"), ("C6", "[−0.07, +0.02]")):
        if c == "C2" and fb1:
            fp.append("ΔR_C2 (F1 이면 대비가 바뀜)")
            continue
        d = p2.get("P", {}).get(c, {}).get("d")
        L = p2.get("labels", {}).get(c, ("?",))[0]
        if not d or not d["dR"]:
            parts.append((f"ΔR_{c} 입력", None))
            continue
        r1, r2 = d["R"].get(1), d["R"].get(2)
        ex = rx(r1["b"], r1["v"], r1["g"]) - rx(r2["b"], r2["v"], r2["g"]) if r1 and r2 else fl(d["dR"]["v"])
        t, ok = inr(11, s, ex)
        parts.append((f"ΔR_{c} {d['dR']['v']} (정확 {ex:+.5f}) {t} ({cite(d['rel'], d['dR']['ln'])})", ok))
        parts.append((f"라벨 {L}", True if L == "(T0)" else (None if L in ("(T0-Holm)", "?") else False)))
        if L == "(T0-Holm)":
            holm_note = c
    if holm_note and not any(ok is False for _, ok in parts):
        row(11, "; ".join(f"{d} {'✓' if ok else '✗' if ok is False else '?'}" for d, ok in parts),
            judge(f"예측 11: {holm_note} 가 (T0-Holm) — 예측의 \"(T0)\" (\"Holm 순서 무관\") 으로 읽으면 적중, 문자열 그대로면 빗나감"), "판단")
    else:
        score(11, parts, fp)
    # 12
    if fb1:
        row(12, "F1 → 2차 단계 미채점", "채점하지 않음 (F1)", "제외")
    else:
        st = X.res.get("steps", {})
        score(12, [(f"S1 \"{st.get('S1') or '출력 없음'}\"", (st.get("S1") == "판정하지 못함") if st.get("S1") else None),
                   (f"S2 \"{st.get('S2') or '출력 없음'}\"", (st.get("S2") == "판정하지 못함") if st.get("S2") else None)])
    # 13
    if fb1:
        row(13, "F1 → N2 = 6.4e5", "채점하지 않음 (F1)", "제외")
    else:
        E = X.res.get("E")
        if not E or E["state"] != "ok":
            score(13, [("(E) 출력 " + ("없음" if not E else "n/a (정의 불가)"), None if not E else False)])
        else:
            t, ok = inr(13, "[+0.9, +1.5]", fl(E["de"]["v"]))
            score(13, [(f"Δ {E['de']['v']} dB {t}", ok), (f"90% 하한 {E['de']['lo90']} > 0 (검열 {E['de']['cens']}% ≤ 5)", E["lo"] > 0 and E["cen"] <= 5)])
    # 14
    bd = X.res.get("p1", {}).get("NR16B64e4", {}).get("band")
    score(14, [(f"R(−3 dB) {bd[1]['R']} (정확 {bd[0]:.5f}) ≥ 0.70" if bd else "C6 −3 dB 입력", ((bd[0] >= 0.70) if has(14, "≥ 0.70") else None) if bd else None)])
    # 15
    parts, fp = [], []
    for T in pts:
        if f1(T):
            fp.append(T)
            continue
        s = X.res.get("p1", {}).get(T, {}).get("sc")
        if not s:
            parts.append((f"{T} 대조군", None))
        elif T == "NR16B64e4":
            parts.append((f"C6 `first arm fewer failures at {s['k1']}/3` (≥ 2/3)", s["powered"] and s["k1"] >= 2))
        else:
            parts.append((f"{T} `second arm fewer failures at {s['k2']}/3` (= 0/3)", s["powered"] and s["k2"] == 0))
    score(15, parts, fp)
    # 16
    parts, fp = [], []
    for T, s in (("B64e4", "[0.45, 0.62]"), ("B128e4", "[0.45, 0.62]"), ("NR16B64e4", "[0.22, 0.40]")):
        if f1(T):
            fp.append(T)
            continue
        q = pp.get(T, {})
        m = re.search(r"ratio min/max/median (\S+)/(\S+)/(\S+) worst_excess (\S+)", q["gbcsv"][0]) if q.get("gbcsv") else None
        if m:
            t, ok = inr(16, s, fl(m[3]))
            parts.append((f"{T} median {m[3]} {t}, worst {m[4]} < 0 ({cite(PREPR, q['gbcsv'][1])})", (ok and fl(m[4]) < 0) if ok is not None else None))
            continue
        lg_ = gblines(q, T)
        mm = re.search(r"max (\S+) median (\S+)", lg_[0]) if lg_ else None
        if mm:
            t, ok = inr(16, s, fl(mm[2]))
            parts.append((f"{T} median {mm[2]} {t}, max {mm[1]} < 1 (worst excess = max − 1 < 0) ({cite(PREPR, q['gblog'][1])})",
                          (ok and fl(mm[1]) < 1) if ok is not None else None))
        else:
            parts.append((f"{T} GB′ 입력", None))
    score(16, parts, fp)
    # 17
    d = X.res.get("K8")
    if d and d["dR"] and 1 in d["R"] and 2 in d["R"]:
        t, ok = inr(17, "[−0.03, 0]", fl(d["dR"]["v"]))
        score(17, [(f"ΣF_b\\*(8192) {d['R'][1]['b']} ≤ ΣF_b\\*(4096) {d['R'][2]['b']}", d["R"][1]["b"] <= d["R"][2]["b"]),
                   (f"ΔR {d['dR']['v']} {t} ({cite(d['rel'], d['dR']['ln'])})", ok)])
    else:
        row(17, "K8 미실행 또는 `nscale_K8.txt` 없음", judge("예측 17: K8 run 0 이면 예측한 양이 없다 — 빗나감/해당 없음"), "판단")
    # 18 (paths, not a prediction)
    labs = X.res.get("p2", {}).get("labels", {})
    quals = X.res.get("qual", {})
    occ = [f"(a) F1 {'발동' if fb1 else '미발동'}",
           f"(b) C6 시행 1 발산 {'발동 (§3d stem)' if re.search(r'_fb[23]$', (X.pt('NR16B64e4') or {}).get('stem', '')) else '미발동'}",
           f"(c) D1 게이트 FAIL {'발동' if any((X.pt(T) or {}).get('gate') == 'FAIL' for T in ('B64e4', 'B128e4')) else '미발동'}",
           "(d) (T−) " + ("입력 없음" if not labs or any(v[0] == "?" for v in labs.values()) else
                         "발동 (" + ", ".join(c for c, v in labs.items() if v[0] == "(T−)") + ")" if any(v[0] == "(T−)" for v in labs.values()) else "미발동"),
           f"(e) bridge 실패 {'발동' if False in (X.ok3('BRB32e4'), X.ok3('BRNR16B16e4')) else '미발동' if X.ok3('BRB32e4') and X.ok3('BRNR16B16e4') else '입력 없음'}",
           "(f) Q-K 강제 " + ("입력 없음" if not labs or any(v[0] == "?" for v in labs.values()) else
                            "발동 (" + ", ".join(c for c, q in quals.items() if q.get("forced")) + ")" if any(q.get("forced") for q in quals.values()) else "미발동")]
    i, _ = regpred(X, 18)
    w(f"| 18 | 빗나갈 경로 ({cite(REG, i) if i else '?'}) | {'; '.join(occ)}. 격자·K·SNR·시드를 늘리지 않았다 | 예측 항목 아님 |")
    w("")
    w(f"합계: 적중 {len(tally['적중'])} ({', '.join(map(str, tally['적중']))}), 빗나감 {len(tally['빗나감'])} ({', '.join(map(str, tally['빗나감']))}), "
      f"채점 제외 {len(tally['제외'])} ({', '.join(map(str, tally['제외']))}; 동결 전 확인·F1), 판단 필요 {len(tally['판단'])} ({', '.join(map(str, tally['판단']))}); 18 은 경로 기록.")
    w("")


def sec_disclosures(X, w):
    w("#### 6.1.9 공개 1–12 (§2.4 \"원고·§6 에 그대로\" — 등록 문장을 바꾸지 않고 옮김)")
    i0 = X.regl(r"^- \*\*공개 \(원고·§6 에 그대로\)\*\*")
    if i0 is None:
        w(f"- {badfmt(REG, '?', '공개 목록 머리 줄 없음')}")
        w("")
        return
    n = 0
    for k in range(i0, len(X.reg)):
        l = X.reg[k]
        if l.startswith("## "):
            break
        m = re.match(r"^\s+(\d{1,2})\. (.*)$", l)
        if m:
            n += 1
            w(f"{m[1]}. {m[2]} ({cite(REG, k + 1)})")
    if n != 12:
        w(f"- {badfmt(REG, i0, f'공개 항목 {n} 개 (12 개여야)')}")
    w("")


def sec_deviations(X, w):
    w("#### 6.1.10 편차·캐비엇 (사실만) · 남은 자리표시")
    lg = X.lg or {}
    for c in ("C2", "C6"):
        d = X.res.get("p2", {}).get("P", {}).get(c, {}).get("d")
        T = X.res.get("p2", {}).get("P", {}).get(c, {}).get("T")
        _, pl, rrel = rec_cells(X, T) if T else (None, None, None)
        if d and 1 in d["R"] and pl:
            r1 = d["R"][1]
            if (r1["lo"], r1["hi"]) != (pl["lo"], pl["hi"]):
                w(f"- R CI 두 출처 ({c} 새 점): `recovery_ci` {pl['R']} [{pl['lo']}, {pl['hi']}] ({cite(rrel, pl['ln'])}) vs `--paired` R1 [{r1['lo']}, {r1['hi']}] "
                  f"({cite(d['rel'], r1['ln'])}) — 난수 흐름이 달라 셋째 자리가 다를 수 있다 (SCALE16e4 §6.1.4 (a) 와 같은 사정).")
    if X.s5 and X.s5["bad"]:
        for i, l in X.s5["bad"]:
            w(f"- S5 의 알 수 없는 줄 {cite(S5R, i)}: `{esc(l)}` {judge('S5 형식')}")
    # §0–§5 placeholders that the freeze rule keeps unedited
    ph = []
    for k, l in enumerate(X.reg or [], 1):
        if l.startswith("## 6."):
            break
        for p in ("[K8 병합 대기]", "[links 대기]", "[§5 커밋 때 채움]"):
            if p in l:
                ph.append((k, p))
    j0, j1 = X.regl(r"^### 4\.1 "), X.regl(r"^### 4\.2 ")
    if j0 and j1:
        for k in range(j0, j1 - 1):
            l = X.reg[k]
            m = re.match(r"^\| (.+?) \| (대기|예정)\b", l)
            if m:
                ph.append((k + 1, f"§4.1 '{m[2]}' 칸 ({m[1][:40]})"))
    if ph:
        w("- **§0–§5 의 미갱신 칸** (편집 금지라 값은 여기 적는다): " + "; ".join(f"{cite(REG, k)} {esc(p)}" for k, p in ph) + " — "
          + judge("각 칸의 지금 값 (예: §5 K8 행 = S5 K8 줄·`prep` K8 줄, links = `NSCALE_LINKS_DONE` 로그, §5 커밋 해시 = 위 커밋 절)"))
    w("- p 값은 서술용; 1차는 Holm 규칙, P1·2차는 보정 없음 (§1·§2.4).")
    w(f"- 다음 단계 (§4.1): Fable 기록 감사 → `docs/EXPERIMENTS.md` 행.")
    w("")
    cnt = {}
    for k, _ in set(MARKS):
        cnt[k] = cnt.get(k, 0) + 1
    w(f"<!-- s6_gen.py 표시 집계 (중복 제거): {', '.join(f'{k} {v}' for k, v in cnt.items()) or '없음'} — 기록 전에 모두 해소할 것 -->")


def compose(conf, author=None):
    MARKS.clear()
    X = Ctx(Files(conf))
    out = []
    w = out.append
    if X.reg is None:
        w(f"**[입력 없음: 등록 문서 `{REG}`]**")
    sec_head(X, w, author)
    for f in (sec_commits, sec_exec, sec_runner, sec_raw, sec_accept, sec_p1, sec_p2, sec_secondary, sec_sn, sec_report, sec_41, sec_fallback,
              sec_predictions, sec_disclosures, sec_deviations):
        try:
            f(X, w)
        except Exception as e:                          # a section never takes the document down: loud marker + the traceback line
            import traceback
            tb = traceback.extract_tb(e.__traceback__)[-1]
            w(f"\n**[생성기 오류: {f.__name__} — {type(e).__name__}: {esc(str(e))[:200]} (s6_gen.py:{tb.lineno})]**\n")
            MARKS.append(("생성기 오류", f"{f.__name__}: {e}"))
    return "\n".join(out) + "\n", X


# ====================================================================== self-test
def selftest():
    """Parsers vs values already recorded (SCALE16e4 §6.1, B32e4 §6.2, NSCALE §0.3/§5), the script's own P1 / Holm helpers on fixtures,
    and an end-to-end run on a fake tree.  Read-only on ~/t2 and ~/t2_wtS; writes only under s6/selftest_tree/."""
    WTS, MAIN = Files("/home/HTJ/t2_wtS/conf"), Files("/home/HTJ/t2/conf")
    SCR = os.path.dirname(HERE)
    # --- frontier --recovery with Q-K (one end) and Q-OP: SCALE16e4 §6.1.1 / Q-OP / Q-K tables
    d = parse_fr(WTS, f"{RV}/scale2_primary_D2_L95.txt")
    assert (d["R"][1]["b"], d["R"][1]["v"], d["R"][1]["g"], d["R"][1]["R"], d["R"][1]["lo"], d["R"][1]["hi"]) == (1161, 276, 70, "0.811", "0.790", "0.832")
    assert (d["R"][2]["b"], d["R"][2]["v"], d["R"][2]["g"], d["R"][2]["R"]) == (864, 488, 125, "0.509")
    assert (d["dlv"]["v"], d["dlv"]["lo"], d["dlv"]["hi"], d["dlv"]["p"], d["dlv"]["lev"], d["dlv"]["ln"]) == ("+0.302", "+0.254", "+0.355", "0.0000", "0.95", 6)
    assert d["Rp"][2]["dF"] == "+35" and d["Rp"][2]["Rp"] == "0.346" and d["Rp"][2]["ci"] == "0.106, 0.492" and not d["Rp"][2]["forced"]
    assert (d["Rpd"]["v"], d["Rpd"]["lo"], d["Rpd"]["hi"]) == ("+0.466", "+0.294", "+0.770")
    assert d["Rs"][1]["R"] == "0.909" and d["Rs"][1]["s"] == "-4.31" and d["Rs"][2]["R"] == "0.610" and d["Rsd"]["v"] == "+0.299" and d["Rsd"]["lo"] == "+0.190"
    assert d["gaps"][2]["vg"] == "363" and d["gaps"][1]["bg"] == "1091" and d["head"]["args"].startswith("--recovery raw_NR32B16e4")
    u = parse_fr(WTS, f"{RV}/scale2_primary_U28_L90.txt")
    assert u["Rp"][1]["forced"] and u["Rp"][1]["r1"] and u["Rpna"] and u["Rpna"][1] == 12 and u["Rs"][2]["R"] == "0.218"
    k = parse_fr(WTS, f"{RV}/scale2_primary_D2_L95_qkC9.txt")
    assert not k["Rp"] and k["dlv"]["lo"] == "+0.254" and lab(fl(k["dlv"]["lo"]), fl(k["dlv"]["hi"])) == "(T+)"
    # --- --paired (registration-stage outputs) = NSCALE §0.3 row C2 R(3.2e5) - R(1.6e5)
    pd = parse_fr(Files(SCR), "nscale_reg/v_paired_C2_32v16.txt")
    assert (pd["dR"]["v"], pd["dR"]["lo90"], pd["dR"]["hi90"], pd["dR"]["lo95"], pd["dR"]["hi95"], pd["dR"]["p"], pd["dR"]["und"]) == \
        ("-0.014", "-0.046", "+0.020", "-0.052", "+0.028", "0.4860", 0)
    assert pd["R"][1]["n"] == "2560" and pd["R"][1]["b"] == 836 and pd["B"] == 2000
    # --- --pair
    pr = parse_fr(MAIN, f"{RV}/frontier_PARB16e4.txt")
    assert pr["pairs"][0]["specs"][0]["v"] == "-2.23" and pr["pairs"][0]["delta"]["v"] == "-0.40" and pr["pairs"][0]["delta"]["cens"] == "0.0"
    # --- recovery_ci (+ the integrity line of run_scale2's same())
    r = parse_rec(WTS, f"{RV}/recovery_NR32B16e4.txt")
    assert r["blocks"][0]["rows"][0]["b"] == 81 and r["blocks"][0]["rows"][0]["R"] == "0.922" and r["blocks"][1]["pooled"]["R"] == "0.811" and r["blocks"][1]["pooled"]["ln"] == 8
    r = parse_rec(WTS, f"{RV}/recovery_NR32B16e4last.txt")
    assert r["blocks"][0]["pooled"]["R"] == "0.808" and r["same"]["bad"] == 0 and r["same"]["n"] == 1344 and r["same"]["res"] == "OK"
    # --- tables: table B block, table A, SNR@0.1 (SCALE16e4 §6.1.3 / §6.1.4 (g))
    b, nb = blockB(WTS, "results/tables_D2_NR32B16e4.txt", PV1)
    assert nb == 1 and (b["ln"], b["end"]) == (305, 310) and b["pooled"][:2] == ("914", "29") and b["powered"] and b["k2"] == 3 and b["dec"] == [-9, -6, -3]
    assert b["pts"][0] == ("-9", "641", "16", "1.6e-166") and b["gap"].startswith("+2.99 dB")
    assert snr01(WTS, "results/tables_D2_NR32B16e4.txt", BS) == ("-6.24", 175) and snr01(WTS, "results/tables_D2_NR32B16e4.txt", V1)[0] == "-9.22"
    a = tableA(MAIN, "results/tables_D2_B32e4.txt", BS)
    assert a["snrs"][0] == -3 and a["vals"][0] == ("0.238", "0.222", "0.255")
    s, _ = blockB(MAIN, "results/tables_D2_B32e4.txt", PSC)
    assert s["k2"] == 0 and s["k1"] == 0 and s["sig"] == "not significant" and s["pooled"][:2] == ("107", "141")
    # --- accept, runner log, guard, run log (SCALE16e4 formats)
    ac = parse_acc(WTS, "U28NR32B16e4")
    assert ac["ok"] and ac["first"] == "ACCEPT: OK -- U28NR32B16e4" and not ac["fails"]
    rn = parse_runner(WTS, "NR32B16e4")
    assert re.search(r"on (\d+) workers", rn["wk"][0])[1] == "99" and rn["first"] == ("8049", 9) and rn["fin"][-1] == ("661.9", 457) and not rn["bad"]
    g = parse_guard(WTS, "NR32B16e4")
    assert g["none"] == 16
    F2 = Files("/home/HTJ/t2_wtS/conf")
    F2.c[LOGR] = F2.lines("logs/run_scale2.log")
    lg = parse_log(F2)
    assert lg["run"]["K2NR16B16e4"]["ln"] == 27 and lg["acc"]["BRB16e4k"]["ln"] == 35 and lg["fr"]["scale2_primary_D2_L95"]["rc"] == 0 and not lg["fail"]
    # --- prep (the §5 draft output) and the training segment rule
    F3 = Files(SCR)
    F3.c[PREPR] = F3.lines("nscale_prep_s5draft.txt")
    pp = parse_prep(F3)
    assert len(pp["B64e4"]["grid"]) == 15 and pp["B64e4"]["grid"][("kron", 4096)]["rs"] == 898 and pp["NR16B64e4"]["grid"][("kron", 4096)]["stop"] == "tol"
    tr = segrule(pp["B64e4"]["train"][0][len("training: "):])
    assert tr["ntr"] == 1 and tr["ngb"] == 1 and abs(tr["wall"] - 58319.3) < 1e-9 and "stopped_by=patience, aborted=False" in tr["final"]
    assert "GC 0.09603" in pp["B64e4"]["d1"][0][0] and "worst_excess -0.120408" in pp["B64e4"]["gbcsv"][0]
    # --- best vs last V1 sign test = B32e4 §6.2 (NEXT_EXPERIMENTS_B32e4.md:126)
    bl = best_last(Files("/home/HTJ/t2/conf"), "B32e4")
    assert bl["per"][-3] == (21, 16) and bl["per"][0] == (8, 13) and bl["per"][3] == (2, 7) and bl["per"][9] == (3, 0)
    assert f"{sign_p(21, 16):.2g}" == "0.51" and f"{sign_p(31, 36):.2g}" == "0.63"
    # --- the script's own P1 and Holm helpers (extracted verbatim from run_nscale.sh) on fixtures -> our parsers / our Holm
    sh_ = open("/home/HTJ/t2/conf/code/run_nscale.sh").read()
    p1py = re.search(r"p1 \(\) \{.*?<<'PY'\n(.*?)\nPY\n", sh_, re.S)[1]
    holmpy = re.search(r"nscale_P2_holm\.txt 2>&1 <<'PY'\n(.*?)\nPY\n", sh_, re.S)[1]
    tree = os.path.join(HERE, "selftest_tree2")            # selftest_tree (first version) is a stray left in place
    build_tree(tree, p1py, holmpy)
    Ft = Files(tree)
    P = parse_p1(Ft, "B64e4")
    assert P["auto"][0].startswith("통과 (POWERED") and P["v1"]["pooled"][:2] == ("421", "69") and P["sc"]["pooled"][:2] == ("107", "141")
    H = parse_holm(Ft)
    assert H["rows"]["C6"]["pos"] == "first" and H["rows"]["C6"]["label"].startswith("(T0)") and H["rows"]["C2"]["label"].startswith("(T0-Holm)")
    # --- end-to-end on the fake tree and on the real (pre-run) conf: no exception, citations present
    txt, X = compose(tree, "selftest")
    n1 = len(set(MARKS))
    assert "생성기 오류" not in txt, [l for l in txt.split("\n") if "생성기 오류" in l]
    for frag in ("`P1_B64e4:2–7`", "421:69", "`P2_C2:", "**C6 (첫째, 95 %)**", "(T0-Holm)", "`acc_BRB32e4:1`", "−3 dB 21:16 (p=0.51)", "`reg:226`",
                 "한정어는 붙이지 않는다", "median 0.2913", "dll(8192-4096) +0.3936", "worst excess (= max − 1) -0.483036", "| 4 | kron 8192"):
        assert frag in txt, frag
    open(os.path.join(HERE, "selftest_tree_s6.md"), "w").write(txt)
    # --- branch scenarios on guarded copies of the fake tree (content taken from the base tree every run -> idempotent)
    hdr = "# run_nscale git abcdef12 2026-10-07 01:00 CDT: frontier_ci.py --paired x y\n"
    fake = lambda f: hdr + "".join(l for l in open(f"{SCR}/nscale_reg/{f}") if not l.startswith("rc="))
    S = {"TT": ({f"{RV}/nscale_P2_C2.txt": lambda t: fake("fake_C2.txt"), f"{RV}/nscale_P2_C6.txt": lambda t: fake("fake_C6.txt")},
                ["**C2 — (T+)**", "\"N′ 를 3.2e5 → 1.28e6 (4 배) 로 늘릴 때 V1 의 genie 격차 회수율 (b\\* 대비 상대 격차) 이 커진다 (C2,", "D1 형제 게이트 기준 PASS / 새 PASS",
                 "Q-OP **\"[운영점 정합 강건]\"**", "Q-K **\"[K 상한 강건]\"**", "**C6 — (T−)**", "작아진다 (C6,", "UNGATED 예산 축 측정",
                 "Q-OP **'[한정어 판정 불가: 비짝 CI 폭 (L⁰ = (T+))]'**", "Q-K **\"[K 상한 민감: 외삽 불가]\" (실행 (a)", "(d) (T−) 발동 (C6)",
                 "3.2e5 `B32e4` 격자 끝 kron 4096 (상한) (`results/gmm_fits_D2_B32e4/fit_S2_Nr8_kronK4096_n320000.npz`",
                 "1.6e5 `NR16B16e4` 격자 끝 kron 4096 (상한)·tol 정지 (163/160)"]),
         "F1": ({S5R: lambda t: re.sub(r"(?m)^PT B128e4 .*$", "PT B128e4 -", t.replace("FALLBACK 0", "FALLBACK 1"))},
                ["\"적합 실패 (F1)\"", "채점하지 않음 (F1)", "(n = 5, 64 배", "F1 → 2차 단계 S1·S2 는 채점하지 않는다", "ΔR_C2 = R(6.4e5) − R(3.2e5) (`FALLBACK 1`"]),
         "ACC": ({f"{RV}/BRB32e4_accept.txt": lambda t: "ACCEPT: FAILED\n  BRB32e4 ('C2', -3): replay vs raw_B32e4 (all): shared 40/40, arms differing "
                  "['R1-turbo'] (max |diff| 1)\n  (f) raw_BRB32e4: run|git ['abcdef12']\nACCEPT (f): OK\n",
                  f"{RV}/B128e4_accept.txt": lambda t: "ACCEPT: FAILED\n  B128e4: points [('C2', 15)] missing/extra\n  (f) raw_B128e4: run|git ['abcdef12']\nACCEPT (f): OK\n",
                  LOGR: lambda t: t.replace("accept BRB32e4 (ACCEPT: OK -- BRB32e4 ACCEPT (f): OK ) rc=0", "accept BRB32e4 (ACCEPT: FAILED ACCEPT (f): OK ) rc=1")
                  .replace("accept B128e4 (ACCEPT: OK -- B128e4 ACCEPT (f): OK ) rc=0", "accept B128e4 (ACCEPT: FAILED ACCEPT (f): OK ) rc=1")
                  .replace("P1 B128e4 (AUTO-LABEL B128e4: x) rc=0", "P1 B128e4 SKIPPED: acceptance of B128e4 failed (label: 수용 실패) rc=1")},
                 ["**(T-iv) 수용 실패**", "**수용 실패 (표 B 없음)**", "C2 3.2e5→6.4e5 판정하지 못함 (수용 실패)", "(e) bridge 실패 발동",
                  "`L:19` `accept BRB32e4 (ACCEPT: FAILED ACCEPT (f): OK ) rc=1`", "B128e4 통과 아님 (수용 실패 (표 B 없음))"])}
    for name, (edits, frags) in S.items():
        d = os.path.join(HERE, f"selftest_tree2_{name}")
        sync_tree(tree, d)
        for rel, fn in edits.items():
            p = os.path.join(d, rel)
            assert not os.path.islink(p), p
            with open(p, "w") as f:
                f.write(fn(open(os.path.join(tree, rel)).read()))
        why2 = "수용 실패" if name == "ACC" else ""      # what run_nscale.sh's why() hands the helper in that scenario
        r_ = subprocess.run([sys.executable, "-", f"{RV}/nscale_P2_C2.txt", why2, f"{RV}/nscale_P2_C6.txt", ""], input=holmpy, cwd=d,
                            capture_output=True, text=True)              # the script's own Holm helper on the scenario's P2 files
        assert not os.path.islink(os.path.join(d, f"{RV}/nscale_P2_holm.txt"))
        open(os.path.join(d, f"{RV}/nscale_P2_holm.txt"), "w").write(r_.stdout + r_.stderr)
        tx, _ = compose(d, "selftest")
        assert "생성기 오류" not in tx, (name, [l for l in tx.split("\n") if "생성기 오류" in l])
        for fr_ in frags:
            assert fr_ in tx, (name, fr_)
        assert "Holm 도우미와 등록 규칙 적용이 다르다" not in tx, name
        open(os.path.join(HERE, f"selftest_tree2_{name}_s6.md"), "w").write(tx)
    txt2, _ = compose("/home/HTJ/t2/conf", "selftest")
    assert "생성기 오류" not in txt2, [l for l in txt2.split("\n") if "생성기 오류" in l]
    assert "(T-iv) 수용 실패" not in txt2 and "**적중**" not in txt2       # missing inputs never turn into a verdict
    open(os.path.join(HERE, "selftest_realconf_s6.md"), "w").write(txt2)
    print("SELFTEST OK — parsers match SCALE16e4 / B32e4 / NSCALE §0.3 records; P1 / Holm helpers agree; end-to-end runs "
          f"(markers: fake tree {n1}, real pre-run conf {len(set(MARKS))}; outputs selftest_tree_s6.md, selftest_realconf_s6.md)")


def sync_tree(src, dst):                                # copy a fixture tree: links stay links, files are copied; never through a link
    import shutil
    for root, dirs, files in os.walk(src):
        rel = os.path.relpath(root, src)
        os.makedirs(os.path.join(dst, rel), exist_ok=True)
        for f in files + [x for x in dirs if os.path.islink(os.path.join(root, x))]:
            s_, d_ = os.path.join(root, f), os.path.join(dst, rel, f)
            if os.path.islink(s_):
                if not os.path.lexists(d_):
                    os.symlink(os.readlink(s_), d_)
                assert os.path.islink(d_) and os.readlink(d_) == os.readlink(s_), d_
            else:
                assert not os.path.islink(d_), d_
                shutil.copyfile(s_, d_)


def build_tree(dst, p1py, holmpy):
    """Fake conf tree: SCALE16e4 / B32e4 / registration-stage outputs under NSCALE names (symlinks; written fixtures only where the
    NSCALE format differs).  Numbers inside are old recorded results, NOT NSCALE results."""
    WTS, MAIN, SCR = "/home/HTJ/t2_wtS/conf", "/home/HTJ/t2/conf", os.path.dirname(HERE)
    for sub in ("logs/nscale", "results/review_next", "results/nscale", "code"):
        os.makedirs(os.path.join(dst, sub), exist_ok=True)

    def ln(src, rel):                                   # create once; an existing path must already be this very link
        p = os.path.join(dst, rel)
        if not os.path.lexists(p):
            os.symlink(src, p)
        elif not (os.path.islink(p) and os.readlink(p) == src):
            raise SystemExit(f"selftest tree: {p} exists and is not the link to {src} -- use a fresh tree directory")

    def wr(rel, text):                                  # never write THROUGH a link (it would change the link's target)
        p = os.path.join(dst, rel)
        if os.path.islink(p):
            raise SystemExit(f"selftest tree: refusing to write through the symlink {p} -- use a fresh tree directory")
        with open(p, "w") as f:
            f.write(text)

    ln(f"{MAIN}/{REG}", REG)
    prep = open(f"{SCR}/nscale_prep_s5draft.txt").read()                    # + fixture K8 lines in run_nscale.sh prep's format
    assert "  DRAFT  K8 - - 0   (no merged kron 8192 fit)\n" in prep
    wr(PREPR, prep.replace("  DRAFT  K8 - - 0   (no merged kron 8192 fit)\n",
                           "    kron K=8192  ll_val -3.9                   r1 kappa 0 n_iter 300 it_best 260 stop patience reseed 0 sec 90000 "
                           "batched [1.0, 1.0, 1.0] cand 3\n  K8: B64e4 grid + kron 8192 -> b* kron 8192 -3.9; dll(8192-4096) +0.3936\n"
                           "  DRAFT  K8 8192 -3.9 1\n"))
    s5 = open(f"{MAIN}/{S5R}").read().replace("# K8 [K8 병합 대기]", "K8 8192 -3.9 1")      # fixture K8 line (test only)
    wr(S5R, s5)
    hdr = "# run_nscale git abcdef12 2026-10-07 01:00 CDT: frontier_ci.py --paired x y\n"
    for c, f in (("C2", "nscale_reg/v_paired_C2_32v16.txt"), ("C6", "nscale_reg/v_paired_C6_16v1.txt")):
        wr(f"{RV}/nscale_P2_{c}.txt", hdr + "".join(l for l in open(f"{SCR}/{f}") if not l.startswith("rc=")))
    for k, f in (("S1_C2", "nscale_reg/v_paired_C2_32v16.txt"), ("S2_C2", "nscale/v_paired_b16e4.txt"), ("K8", "nscale_reg/v_paired_ident.txt")):
        wr(f"{RV}/nscale_{k}.txt", hdr + "".join(l for l in open(f"{SCR}/{f}") if not l.startswith("rc=")))
    for c, dd in (("C2", "D2"), ("C6", "U28")):
        for L in ("95", "90"):
            for suf, src in (("", ""), ("_qkN", "_qkC9"), ("_qkB", "_qkC2")):
                ln(f"{WTS}/{RV}/scale2_primary_{dd}_L{L}{src}.txt", f"{RV}/nscale_qk_{c}_L{L}{suf}.txt")
    ln(f"{MAIN}/{RV}/frontier_PARB16e4.txt", f"{RV}/nscale_eff_C2.txt")
    ln(f"{MAIN}/{RV}/frontier_PARB16e4.txt", f"{RV}/nscale_eff128_C2.txt")
    tabs = {"B64e4": "B32e4", "B128e4": "B32e4", "B64e4last": "B32e4last", "B128e4last": "B32e4last", "NR16B64e4": "NR16B16e4"}
    for T, s in tabs.items():
        ln(f"{MAIN}/results/tables_D2_{s}.txt", f"results/tables_D2_{T}.txt")
    for T, s in (("B64e4", "B32e4"), ("B128e4", "B32e4"), ("NR16B64e4", "NR16B16e4")):
        ln(f"{MAIN}/results/guard_D2_{s}.txt", f"results/guard_D2_{T}.txt")
    rec = {"B64e4": "B16e4k", "B128e4": "B16e4k", "NR16B64e4": "NR16B16e4"}
    for T, s in rec.items():
        ln(f"{MAIN}/{RV}/recovery_{s}.txt", f"{RV}/recovery_{T}.txt")
    for T in ("B64e4", "B128e4", "NR16B64e4"):
        src = open(f"{MAIN}/{RV}/recovery_NR16B16e4last.txt").read() if T.startswith("NR16") else \
            "".join(open(f"{MAIN}/{RV}/recovery_B16e4k.txt").readlines()[:5])
        wr(f"{RV}/recovery_{T}last.txt", src + f"M-ours-bstar raw_{T}last == raw_{T} (report-only integrity, not a gate): 0 of 1344 (chunk, key) pairs differ -> OK\n")
    wr(f"{RV}/nscale_K8_V1.txt", "M-ours-dscore-C-V1 raw_B64e4k8 == raw_B64e4 (report-only integrity, not a gate): 0 of 1344 (chunk, key) pairs differ -> OK\n")
    for K in NEWRAW:
        wr(f"{RV}/{K}_accept.txt", f"ACCEPT: OK -- {K}\n  (f) raw_{K}: run|git ['abcdef12']\nACCEPT (f): OK\n")
    ln(f"{MAIN}/{RV}/K2NR16B16e4_accept.txt", f"{RV}/K2NR16B16e4_accept.txt")
    runs = {"BRB32e4": "BRB16e4k", "BRNR16B16e4": "BRNR16", "B64e4": "U28NR16B16e4", "B128e4": "U28NR16B16e4", "NR16B64e4": "U28NR16B16e4",
            "B64e4chk": "U28NR16B16e4chk", "B128e4chk": "U28NR16B16e4chk", "NR16B64e4chk": "U28NR16B16e4chk", "B64e4last": "U28NR16B16e4last",
            "B128e4last": "U28NR16B16e4last", "NR16B64e4last": "U28NR16B16e4last", "K2B32e4": "K2NR16B16e4", "K2B64e4": "K2NR16B16e4",
            "K2B128e4": "K2NR16B16e4", "K2NR16B64e4": "K2NR16B16e4", "B64e4k8": "K2NR16B16e4"}
    for T, s in runs.items():
        ln(f"{WTS}/logs/run_D2_{s}.log", f"logs/run_D2_{T}.log")
    for fd in ("gmm_fits_D2_B32e4", "gmm_fits_D2_NR16B16e4"):                 # base fits (G_N stop rule of the base ends)
        ln(f"{MAIN}/results/{fd}", f"results/{fd}")
    for npz in ("d2_gbprime_N640000_a1.npz", "d2_gbprime_N1280000_a1.npz", "d2_gbprime_NR16_N640000_a1.npz"):
        ln(f"{MAIN}/results/{npz}", f"results/{npz}")
    for T, s_ in (("B64e4", "B32e4"), ("B64e4last", "B32e4last"), ("NR16B64e4", "NR16B16e4")):
        ln(f"{MAIN}/logs/analysis_{s_}.log", f"logs/analysis_{T}.log")
    ln(f"{MAIN}/raw_B32e4", "raw_B64e4")
    ln(f"{MAIN}/raw_B32e4last", "raw_B64e4last")
    # run log in the run_nscale.sh log() format (fixture)
    L = ["[nscale 10-07 01:00 CDT] single-shot marker logs/nscale/nscale_s5.start written (first eval start)",
         "[nscale 10-07 01:00 CDT] start eval (git abcdef12, freeze 2d50dab51629c1731ec41db2f7ed1449ae7ea9d1, fallback 0, K8 run 1, resume 0, S5+HEAD x y)"]
    for T in NEWRAW:
        n = 1 if T.startswith("BR") or T.endswith("chk") else 192 if T.startswith("K2") or T in ("B64e4k8", "NR16B64e4last") else 448
        L.append(f"[nscale 10-07 02:00 CDT] run {T} ({n}/{n} files) rc=0")
    for K in NEWRAW:
        L.append(f"[nscale 10-07 08:00 CDT] accept {K} (ACCEPT: OK -- {K} ACCEPT (f): OK ) rc=0")
    for T in ("B64e4", "B128e4", "NR16B64e4"):
        L.append(f"[nscale 10-07 08:01 CDT] P1 {T} (AUTO-LABEL {T}: x) rc=0")
        L.append(f"[nscale 10-07 08:01 CDT] b* {T}last == {T} (report-only integrity line) rc=0")
    for F_ in ("nscale_P2_C2", "nscale_P2_C6", "nscale_S1_C2", "nscale_S2_C2", "nscale_eff_C2", "nscale_eff128_C2", "nscale_K8"):
        L.append(f"[nscale 10-07 08:02 CDT] frontier {F_} (--paired x y) rc=0")
    L.append("[nscale 10-07 08:03 CDT] P2 Holm helper ((T0); (T0-Holm)) rc=0")
    L.append(f"[nscale 10-07 08:05 CDT] NSCALE_DONE ok={sum(l.endswith(' rc=0') for l in L)} fail=0")
    wr(LOGR, "\n".join(L) + "\n")
    # the script's own P1 helper (verbatim) on the tables fixtures, and its Holm helper on the P2 fixtures
    for T, cell in (("B64e4", "C2"), ("B128e4", "C2"), ("NR16B64e4", "C6")):
        r_ = subprocess.run([sys.executable, "-", T, cell], input=p1py, cwd=dst, capture_output=True, text=True)
        wr(f"{RV}/nscale_P1_{T}.txt", r_.stdout + r_.stderr)
    r_ = subprocess.run([sys.executable, "-", f"{RV}/nscale_P2_C2.txt", "", f"{RV}/nscale_P2_C6.txt", ""], input=holmpy, cwd=dst, capture_output=True, text=True)
    wr(f"{RV}/nscale_P2_holm.txt", r_.stdout + r_.stderr)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out", nargs="?")
    ap.add_argument("--conf", default="/home/HTJ/t2/conf")
    ap.add_argument("--author", default=None)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.out:
        ap.error("OUT.md is required (or --selftest)")
    txt, _ = compose(a.conf, a.author)
    with open(a.out, "w") as f:
        f.write(txt)
    uniq = sorted(set(MARKS))
    cnt = {}
    for k, v in uniq:
        cnt[k] = cnt.get(k, 0) + 1
    print(f"wrote {a.out} ({len(txt.splitlines())} lines); markers (deduplicated): {cnt or 'none'}")
    for k, v in uniq[:80]:
        print(f"  [{k}] {v}")


if __name__ == "__main__":
    main()
