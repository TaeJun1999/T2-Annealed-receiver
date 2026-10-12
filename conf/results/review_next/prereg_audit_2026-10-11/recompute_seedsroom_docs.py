"""SEEDSROOM16e4 record audit -- companion records: every number-like token of a text must occur verbatim in its cited sources.
  A. docs/EXPERIMENTS.md last row           vs the registration (whole file) + the run's logs
  B. docs/RESULTS.md §25.1-25.4             vs the EXPERIMENTS.md rows named in the §25 header (KST heads)
  C. docs/RESULTS.md §25.5                  vs the registration §6 (and, separately, the EXPERIMENTS.md SEEDSROOM row)
  D. conference/figures/README.md section   vs the §6 of the eight ray-traced registrations + SEEDSROOM §6 + records/paper_f21*.txt, paper_f33cdf_*.txt, paper_f34seed.txt
  E. the two newest conf/DECISIONS.md lines vs the registration + logs
A token = a:b count pair, signed/unsigned decimal, scientific p value, 8-16 hex id, or an integer of >= 2 digits.  Unicode minus,
thin spaces and the multiplication-sign scientific form are normalised on both sides.  A token "not found" is only a pointer for
reading by hand -- it is not by itself a finding.   Read-only.
    ~/miniforge3/envs/torch/bin/python -B recompute_seedsroom_docs.py > recompute_seedsroom_docs.out
"""
import glob
import re

T2 = "/home/HTJ/t2"
RN = f"{T2}/conf/results/review_next"
SUP = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁻", "0123456789-")
TOK = re.compile(r"\d+:\d+|[+-]?\d+\.\d+(?:e[+-]?\d+)?|\d(?:\.\d+)?e-\d+|\b[0-9a-f]{8,16}\b|\b\d{2,}\b")


def norm(s):
    s = s.replace("−", "-").replace("\u202f", " ").replace("\u2009", " ").replace("\\*", "*")
    s = re.sub(r"(\d(?:\.\d+)?)\s*×\s*10([⁰¹²³⁴⁵⁶⁷⁸⁹⁻]+)", lambda m: f"{m[1]}e{m[2].translate(SUP)}", s)   # 1.5×10⁻⁴ -> 1.5e-4
    return s


def rd(p):
    return norm(open(p, encoding="utf-8", errors="replace").read())


def sec(text, start, stop=None):
    i = text.index(start); j = text.index(stop, i + len(start)) if stop else len(text)
    return text[i:j]


def check(name, src, ref, ctx=38):
    toks = [(m.group(0), m.start()) for m in TOK.finditer(src)]
    miss = [(t, src[max(0, p - ctx):p + len(t) + ctx].replace("\n", " ")) for t, p in toks if t not in ref and t.lstrip("+") not in ref]
    print(f"\n## {name}: {len(toks)} tokens ({len({t for t, _ in toks})} distinct), not found verbatim in the sources: {len(miss)}")
    for t, c in miss:
        print(f"  [{t}]  ...{c}...")
    return len(toks), len(miss)


def main():
    exp = rd(f"{T2}/docs/EXPERIMENTS.md").split("\n"); res = rd(f"{T2}/docs/RESULTS.md"); dec = rd(f"{T2}/conf/DECISIONS.md").split("\n")
    reg = rd(f"{RN}/NEXT_EXPERIMENTS_SEEDSROOM16e4.md"); reg6 = sec(reg, "## 6. 결과")
    logs = "\n".join(rd(f) for f in [f"{T2}/conf/logs/run_seedsroom16e4.log"] + glob.glob(f"{T2}/conf/logs/run_seeds16e4_SR[BP]B16e4s[23].log")
                     + glob.glob(f"{T2}/conf/logs/seeds_SR[BP]_train.log") + glob.glob(f"{T2}/conf/code/run_seed*16e4.sh"))
    last = [l for l in exp if l.startswith("|")][-1]
    assert "run_seedsroom16e4.sh" in last
    check("A. EXPERIMENTS.md last row vs registration + logs + runner scripts", last, reg + logs)

    s25 = sec(res, "## 25. 레이 트레이싱 풀")
    heads = re.findall(r"`(2026-10-1\d \d\d:\d\d ~ (?:2026-10-1\d )?\d\d:\d\d KST)`", s25)
    rows = {}
    for h in heads:
        m = [l for l in exp if l.startswith("| " + h)]
        rows[h] = m
    print("\n# RESULTS §25 cites", len(heads), "EXPERIMENTS.md row heads; rows found per head:", {h: len(v) for h, v in rows.items()})
    cited = "\n".join(l for v in rows.values() for l in v)
    seedrow = "\n".join(rows[heads[-1]])
    assert "run_seedsroom16e4.sh" in seedrow, heads[-1]
    for a, b in (("### 25.1", "### 25.2"), ("### 25.2", "### 25.3"), ("### 25.3", "### 25.4"), ("### 25.4", "### 25.5")):
        check(f"B. RESULTS {a[4:]} vs the cited EXPERIMENTS.md rows", sec(s25, a, b), cited)
    s255 = sec(s25, "### 25.5")
    check("C1. RESULTS 25.5 vs the registration §6 (+ §5 for GB')", s255, reg6 + sec(reg, "## 5. 평가 전", "## 6. 결과"))
    check("C2. RESULTS 25.5 vs the EXPERIMENTS.md SEEDSROOM row", s255, seedrow)
    check("B0. RESULTS §25 header paragraphs vs the cited EXPERIMENTS.md rows", sec(s25, "## 25.", "### 25.1"), cited)

    rm = rd(f"{T2}/conference/figures/README.md"); rs = sec(rm, "## 레이 트레이싱 풀 그림")
    nxt = re.search(r"\n## ", rs[5:]); rs = rs[:nxt.start() + 5] if nxt else rs
    src6 = ""
    for n in ("DMC16e4", "DMCBASE16e4", "SRT16e4", "ROOM16e4", "PATH16e4", "FIGHSROOM16e4", "FIGHSPATH16e4", "FIGHSX16e4", "SEEDSROOM16e4"):
        t = rd(f"{RN}/NEXT_EXPERIMENTS_{n}.md"); src6 += t[t.index("\n## 6"):]
    recs = "\n".join(rd(f) for f in glob.glob(f"{T2}/conference/figures/records/paper_f21*.txt") + glob.glob(f"{T2}/conference/figures/records/paper_f33cdf_*.txt")
                     + [f"{T2}/conference/figures/records/paper_f34seed.txt"])
    check("D. README section '레이 트레이싱 풀 그림' vs the nine registrations' §6 + figure records", rs, src6 + recs)
    check("D'. the two README lines added in 36022add (F34seed row, seed row) vs the SEEDSROOM registration §6 + paper_f34seed.txt",
          "\n".join(l for l in rs.split("\n") if l.startswith("| F34seed_wide") or l.startswith("| 시드 강건성")), reg6 + rd(f"{T2}/conference/figures/records/paper_f34seed.txt"))

    d2 = [l for l in dec if l.startswith("`[")][-2:]
    for l in d2:
        check(f"E. DECISIONS line {l[:24]} vs registration + logs", l, reg + logs)


if __name__ == "__main__":
    main()
