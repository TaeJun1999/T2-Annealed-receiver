"""conference/figures/paper_f18.py -- paper version of conf/code/figure_f18.py (git 3f7c09ab), F18: the out-of-grid
query rule at 8x4 with 2 pilots, -3 dB.

Same data, computation, asserts, colours, markers and error bars as the original; only the rendered text differs:
  - arm names (legend, tick labels, annotations) use the paper glossary (conference/figures/TERMS.md): GMM b* -> GMM prior,
    V1 frozen -> Proposed (extrapolates), V1-edge -> Proposed, out-of-grid rule, V1-clamp -> Proposed, clamped queries,
    genie (R5) -> Perfect CSI; "b* in V1's wiring" -> GMM prior, proposed wiring (not in the glossary); tight spots
    use the short forms "out-of-grid rule" / "clamped queries";
  - registration roles removed from the annotations and the legend ("primary", "confirmation", "mechanism", "registered,
    report-only", "not decided" -> "n.s.", n_d / MDD / |Delta|, "report points", trial index ranges -> n);
  - cell codes -> "8x4, 2 / 3 pilots"; "BLER at t=16" -> "BLER"; the dagger note no longer says "registered";
  - text placement only, for the longer strings: (c) header / a:b numbers / direct label / dagger note moved, the figure
    legend lowered by 0.025 (figure fraction);
  - titles removed, only the bold panel labels remain.  Panel mapping, for the caption:
      (a) 8x4, 2 pilots, -3 dB (filled: test trials, hollow: development trials)
      (b) same point, test trials: BLER after each outer iteration t (top) and the share of blocks whose prior query is
          above the noise-level grid, nu_q > nu_hi (bottom)
      (c) development trials: 8x4, 2 pilots, 0 dB and 8x4, 3 pilots, -6 dB;
  - reads conf/ (read-only) and writes only F18_oog_rule_K2.{pdf,png} next to this script (no table .tex, no .txt; the
    record text is printed to stdout with the internal names).
The original docstring follows.

conf/code/figure_f18.py -- F18 + table T_K2: the K2 out-of-grid query rule (V1-edge, a separate registered arm;
NEXT_EXPERIMENTS_K1K2 §2).  Numbers straight from the raw files; cost table from results/review_next/oog_cost.txt
(code/bench_oog.py; not rerun here).

(a) C1 -3 dB BLER@16 per arm: TEST trials 0..2559 (raw_review_next_K2test, n=2560; the confirmation, run once) filled,
    the registered primary-test trials 3200..4479 (raw_review_next_K2, n=1280) hollow.  95% Wilson.  Broken y axis, both
    halves on one scale.
(b) mechanism at C1 -3 dB TEST: BLER after each outer iteration t = 1..16, and the share of blocks whose prior query is
    above the sigma grid (nu_q > nu_hi) at iteration t (frozen V1: its recorded, non-raised blocks).
(c) report points (development trials 2560..3199, n=640): C1 0 dB and C5 -6 dB (outside the registered SNR grid).
Writes figs/F18_oog_rule_K2.{pdf,png,txt} and figs/T_K2_oog_rule.tex.  Read-only on raw and on every record.
"""
import datetime as dt
import decimal
import os
import re
import sys

sys.dont_write_bytecode = True                         # never write __pycache__ into the frozen conf/code
CONF = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "conf"))
sys.path.insert(0, os.path.join(CONF, "code"))
import common as C
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({"pdf.fonttype": 42, "ps.fonttype": 42})   # TrueType fonts in PDF (IEEE PDF eXpress rejects Type 3)
from matplotlib.lines import Line2D
from analysis import load_raw, sign_p
from figure_f16 import wilson                                   # house rcParams come with it
from pair_tags import mdd
import diag_prior_swap as DPS
import figstyle as S
from figstyle import INK, INK2

assert os.path.samefile(C.CONF, CONF)
FIG = os.path.dirname(os.path.abspath(__file__))     # paper version: figures only, next to this script
NU_HI = 1.4285757304853552
# (arm id, tick label, legend label, colour, marker); roles from figstyle: GMM b* orange (variants: same orange, other
# markers), V1 blue, V1-edge aqua (V1-clamp: same aqua, triangle; open + dashed in (b)), genie ink.  In (a) filled / open
# encodes test / development, so V1-clamp is told apart by its marker there, not by an open marker.
# paper version: tick (2nd) and legend (3rd) strings are display only, in the paper glossary (TERMS.md)
ARMS = [("M-ours-bstar", "GMM prior", "GMM prior (K = 1024, exact site)", S.GMM["color"], S.GMM["marker"]),
        ("M-ours-bstar-scalar", "GMM, scalar site", "GMM prior, scalar site", S.GMM["color"], "v"),
        ("gmmB-scorew-eta", "GMM, prop. wiring", "GMM prior, proposed wiring", S.GMM["color"], "P"),
        ("M-ours-dscore-C-V1", "Proposed", "Proposed (extrapolates)", S.V1["color"], S.V1["marker"]),
        ("V1-edge", "Out-of-grid rule", "Proposed, out-of-grid rule", S.EDGE["color"], S.EDGE["marker"]),
        ("V1-clamp", "Clamped queries", "Proposed, clamped queries", S.EDGE["color"], "^"),
        ("R5-genie", "Perfect CSI", "Perfect CSI", S.GENIE["color"], S.GENIE["marker"])]
TEXNAME = {"M-ours-bstar": (r"GMM $b^*$ (exact site)", ""), "M-ours-bstar-scalar": (r"$b^*$, scalar site", ""),
           "gmmB-scorew-eta": (r"$b^*$ in V1's wiring", ""), "M-ours-dscore-C-V1": (r"V1 frozen", r"\quad(extrapolates)"),
           "V1-edge": (r"\textbf{V1-edge}", r"\quad(primary variant)"),
           "V1-clamp": (r"V1-clamp", r"\quad(secondary variant)"),
           "R5-genie": (r"genie (R5)", "")}
# records cited by line; every citation is checked against the file's current text
REC = {"K1K2": "results/review_next/NEXT_EXPERIMENTS_K1K2.md", "DEC": "DECISIONS.md", "TB": "results/tables_D2_B32e4x.txt",
       "K2": "results/review_next/K2_report.txt", "K2T": "results/review_next/K2test_report.txt",
       "COST": "results/review_next/oog_cost.txt", "SPEC": "10_SPEC_stageC.md"}
# first log line of each K2 run: "... trials a..b: N tasks on W workers"
WLOG = {"dev": "logs/review_next/k2_C1_m3.log", "test": "logs/review_next/k2test_C1_m3.log",
        "C1 0 dB": "logs/review_next/k2_C1_p0.log", "C5 -6 dB": "logs/review_next/k2_C5_m6.log"}
CITE = [("K1K2", 4, "§6j"), ("K1K2", 17, "K=1024 의 C1 테스트는 미실행"), ("K1K2", 21, "0..2559 (B16e4·B1e4x·B32e4x·C)"), ("K1K2", 23, "P3 채택 규칙, A1, K2"),
        ("K1K2", 23, "판정 기준(p<0.05)과 함께 Holm m=3"), ("K1K2", 64, "4443921ce8d5c4a1"), ("K1K2", 65, "셀 선택은 사후"),
        ("K1K2", 67, "등록 SNR 격자 밖 점"), ("K1K2", 82, "배선을 맞춘 대조"),
        ("K1K2", 83, "격자 밖 규칙\" 표"), ("K1K2", 83, "비용 열(격자 밖 질의당 네트워크 호출 수·초)"), ("K1K2", 97, "확증의 새 정보는 V1-edge"), ("K1K2", 97, "B32e4x 0.995 / 0.749"),
        ("K1K2", 97, "한 번만 실행한다"), ("K1K2", 97, "`V1 → V1-edge` 기전 확인"), ("K1K2", 118, "V1-edge·V1-clamp == V1 비트 동일(n_oog 0)"),
        ("K1K2", 132, "크기 64 블록(0.050), 격차 위치 +0.070"), ("K1K2", 132, "198:134"), ("K1K2", 134, "32:42"), ("K1K2", 137, "보고 점 (라벨 없음)"),
        ("K1K2", 148, "사용자 결정 2026-09-25 09:29 CDT"), ("K1K2", 148, "한 번"), ("K1K2", 160, "400:264"), ("K1K2", 160, "758:13 (p=8.1e-205)"),
        ("K1K2", 162, "불변"), ("K1K2", 187, "비트 동일"), ("K1K2", 190, "MDD 25"),
        ("DEC", 22, "clamp 하지 않고 외삽"), ("DEC", 96, "Tp<Nt 영방향"), ("DEC", 191, "K2 테스트 확증"),
        ("TB", 506, "--- cell C1"), ("TB", 591, "M-ours-bstar -> M-ours-dscore-C-V1"), ("TB", 595, "first arm fewer failures at 3/3"),
        ("TB", 592, "decision SNRs ['+6', '+9', '+15']"), ("TB", 646, "--- cell C5"), ("TB", 731, "M-ours-bstar -> M-ours-dscore-C-V1"),
        ("TB", 732, "decision SNRs ['+6', '+12', '+15']"),
        ("TB", 735, "second arm fewer failures at 1/3 points, first arm fewer failures at 1/3 points -> not significant"),
        ("K1K2", 4, "셀 C1·C5 의 기존 판정(§6f, B32e4x)"), ("K1K2", 80, "### 2.3 기전·대조 비교 (보고; 라벨 없음"),
        ("K1K2", 83, "`V1-clamp ↔ V1-edge` 는 세 갈래로만 기록한다"), ("K1K2", 96, "### 2.6 테스트 확증"),
        ("SPEC", 702, "# §6j"), ("SPEC", 719, "별도 사전 등록이 필요하다"), ("SPEC", 740, "# §6p — SNR 축을 아래로 연장"),
        ("SPEC", 774, "셀 **C2 와 C5**, SNR **{−9, −7, −6, −5} dB** 추가"),
        ("K2", 12, "198:134"), ("K2", 13, "372:8"), ("K2", 14, "183:74"), ("K2", 15, "199:70"), ("K2", 16, "199:125"),
        ("K2", 20, "32:42"), ("K2", 21, "13:313"), ("K2", 33, "112:73"), ("K2", 54, "86:12"),
        ("K2T", 7, "above-grid it1 0.88 it2-16 0.793"), ("K2T", 12, "400:264"), ("K2T", 13, "758:13"), ("K2T", 14, "379:122"),
        ("K2T", 15, "406:105"), ("K2T", 16, "402:279"), ("K2T", 18, "75:62"), ("K2T", 19, "20:629")]


def point(tag, cell, snr):
    return load_raw("D2", root=os.path.join(C.CONF, f"raw_{tag}"))[0][(cell, "S2", float(snr))]


def be(d, arm):
    v = np.asarray(d[arm]["blk_err"], float)
    return np.where(np.isfinite(v), v, 1.0)                  # a raised block is a block error at every t (01_RULES §4)


def st(d, x, y, it=-1):
    a, b = int(np.sum((be(d, x)[:, it] == 1) & (be(d, y)[:, it] == 0))), int(np.sum((be(d, x)[:, it] == 0) & (be(d, y)[:, it] == 1)))
    return a, b, sign_p(a, b)


def summ(d):
    """per arm: failures@16, n, BLER, Wilson, guard, exceptions, above-grid it1 / it2-16 (None = no grid query)."""
    out = {}
    for arm, *_ in ARMS:
        f = be(d, arm)[:, -1]; k, n = int(f.sum()), len(f)
        nq = np.asarray(d[arm]["nu_q"], float)
        ab = None if np.isnan(nq).all() else ((nq[:, 0] > NU_HI).mean(), (nq[:, 1:] > NU_HI).mean(), int((nq[:, 1:] > NU_HI).sum()))
        g = np.asarray(d[arm]["guardH"], float)
        out[arm] = dict(k=k, n=n, p=k / n, ci=wilson(k, n), guard=None if np.isnan(g).all() else int(np.nansum(g)),
                        exc=int(np.sum(d[arm].get("failed", 0))), ab=ab)
    g, r = out["M-ours-bstar"]["k"], out["R5-genie"]["k"]
    for arm in out:
        out[arm]["gap"] = (g - out[arm]["k"]) / (g - r)
    return out


def cost():
    L = open(os.path.join(C.CONF, REC["COST"])).read().splitlines()
    c = {}
    for i, l in enumerate(L, 1):
        m = re.match(r"\s+(M-ours-dscore-C-V1|V1-clamp|V1-edge|V1 in-grid)\s+median ([\d.]+) s\s+min ([\d.]+)\s+max ([\d.]+)\s+reps (\d+)", l)
        if m:
            c.setdefault(m[1], {}).update(s=float(m[2]), lo=float(m[3]), hi=float(m[4]), reps=int(m[5]), ls=i)
        m = re.match(r"\s+(M-ours-dscore-C-V1|V1-clamp|V1-edge)\s+(\d+) network forwards \(([^;]*); (\d+) sample-forwards\), (\d+) jacrev", l)
        if m:
            c.setdefault(m[1], {}).update(fw=int(m[2]), fwd=m[3], jac=int(m[5]), ln=i)
        m = re.match(r"\s+(M-ours-dscore-C-V1|V1-clamp|V1-edge)\s+above-grid queries/block ([\d.]+)\s+->\s+([\d.]+) s/block = ([\d.]+) x", l)
        if m:
            c.setdefault(m[1], {}).update(qpb=float(m[2]), sblk=float(m[3]), xblk=float(m[4]), lb=i)
        if l.startswith("date"):
            c["date"] = l.split(":", 1)[1].strip()
        m = re.search(r"load average at end ([\d.]+) / (\d+) cores", l)
        if m:
            c["load"] = f"{m[1]} / {m[2]} cores"
        m = re.match(r"wall time of this benchmark: (\d+) s", l)
        if m:
            c["wall"] = int(m[1])
        m = re.match(r"nu_above = ([\d.]+)", l)
        if m:
            c["nu_above"] = float(m[1])
        m = re.search(r"\(16 in-grid V1 queries = ([\d.]+) s\)", l)
        if m:
            c["ref16"] = float(m[1])
    return c


def bit_identity():
    """audit §5.3 re-check: frozen V1 and R5-genie of the TEST run == raw_B16e4 C1 -3 dB, every KEYS_RAW field @1..16."""
    X, R = DPS.load("raw_review_next_K2test", "C1", -3.0), DPS.load("raw_B16e4", "C1", -3.0)
    tr = sorted(X); assert tr == list(range(2560)) and set(tr) <= set(R)
    return {arm: all(np.array_equal(np.asarray(X[t][f"{arm}|{q}"], float), np.asarray(R[t][f"{arm}|{q}"], float), equal_nan=True)
                     for t in tr for q in C.KEYS_RAW) for arm in ("M-ours-dscore-C-V1", "R5-genie")}


def c2_precheck():
    """registered pre-check (b): C2 -3 dB dev 2560..2599, V1-edge / V1-clamp == V1 on every KEYS_RAW field, n_oog 0."""
    X = DPS.load("raw_review_next_K2pre_c2", "C2", -3.0); tr = sorted(X); assert tr == list(range(2560, 2600)), tr
    same = {a: all(np.array_equal(np.asarray(X[t][f"{a}|{q}"], float), np.asarray(X[t][f"M-ours-dscore-C-V1|{q}"], float),
                                  equal_nan=True) for t in tr for q in C.KEYS_RAW) for a in ("V1-edge", "V1-clamp")}
    return same, {a: float(sum(np.nansum(X[t][f"{a}|n_oog"]) for t in tr)) for a in ("V1-edge", "V1-clamp")}, len(tr)


def observed_before():
    """failures@16 of the arms of this table in the earlier runs on the same test trials 0..2559 (C1 -3 dB)."""
    out = {}
    for tag in ("raw_B1e4x", "raw_C", "raw_B16e4", "raw_B32e4x"):
        X = DPS.load(tag, "C1", -3.0); tr = [t for t in sorted(X) if t < 2560]; assert tr == list(range(2560)), tag
        arms = {k.split("|")[0] for t in tr for k in X[t] if k.endswith("|blk_err")}
        assert not arms & {"gmmB-scorew-eta", "V1-edge", "V1-clamp"}, (tag, arms)     # no earlier run of these arms
        out[tag] = {a: int(sum(1.0 if not np.isfinite(X[t][f"{a}|blk_err"][-1]) else float(X[t][f"{a}|blk_err"][-1]) for t in tr))
                    for a in ("M-ours-bstar", "M-ours-bstar-scalar", "M-ours-dscore-C-V1", "R5-genie")}
    return out



def pe(p):
    """plain-text p, one rule for figure, table and captions: p < 0.01 as m.me-k, otherwise two decimals."""
    if p == 0:
        return "<1e-300"
    if p < 0.01:
        m, e = f"{p:.1e}".split("e")
        return f"{m}e{int(e)}"
    return "1" if p > 0.995 else f"{p:.2f}"


decimal.getcontext().rounding = decimal.ROUND_HALF_UP


def R(x):
    """x as the Decimal of its shortest repr, for display: ties of exact fractions round half up (344/640 = 0.5375 -> 0.538;
    the float 0.53749999... would print 0.537)."""
    return decimal.Decimal(repr(float(x)))


def pt(p):
    """pe() in TeX math (no $): m{\\times}10^{k}."""
    s = pe(p)
    if s.startswith("<"):
        return r"<10^{-300}"
    if "e" in s:
        m, e = s.split("e")
        return rf"{m}{{\times}}10^{{{e}}}"
    return s


def main():
    for key, ln, must in CITE:                                    # fail loudly if a cited line moved
        line = open(os.path.join(C.CONF, REC[key])).read().splitlines()[ln - 1]
        assert must in line, (REC[key], ln, must)
    TBL = open(os.path.join(C.CONF, REC["TB"])).read().splitlines()      # cited verdict lines sit in table B, in their cell
    for ln, cell in ((591, "C1"), (731, "C5")):
        hdr = [l for l in TBL[:ln] if l.startswith("--- cell") or l.startswith("=====")]
        assert hdr[-1].startswith(f"--- cell {cell} ") and "TABLE B" in [h for h in hdr if h.startswith("=")][-1], (ln, hdr[-2:])
    T, D = point("review_next_K2test", "C1", -3), point("review_next_K2", "C1", -3)
    P0, P5 = point("review_next_K2", "C1", 0), point("review_next_K2", "C5", -6)
    sT, sD, s0, s5 = summ(T), summ(D), summ(P0), summ(P5)
    B, E = "M-ours-bstar", "V1-edge"
    # comparison columns: b*->X only for V1 frozen / V1-edge / V1-clamp; X->V1-edge for the registered controls,
    # the mechanism check and V1-clamp (NEXT_EXPERIMENTS_K1K2 §2.2-2.3)
    BX = ("M-ours-dscore-C-V1", E, "V1-clamp")
    XE = ("M-ours-bstar-scalar", "gmmB-scorew-eta", "M-ours-dscore-C-V1", "V1-clamp")
    bxT, bxD = {a: st(T, B, a) for a in BX}, {a: st(D, B, a) for a in BX}
    xeT, xeD = {a: st(T, a, E) for a in XE}, {a: st(D, a, E) for a in XE}
    ceT, ceD = xeT["V1-clamp"], xeD["V1-clamp"]
    v1T, v1D = xeT["M-ours-dscore-C-V1"], xeD["M-ours-dscore-C-V1"]
    st0, st5 = st(P0, B, E), st(P5, B, E)
    v10, v15 = st(P0, "M-ours-dscore-C-V1", E), st(P5, "M-ours-dscore-C-V1", E)
    # the recorded numbers (K2_report.txt, K2test_report.txt, NEXT_EXPERIMENTS_K1K2 §5.1/§5.3) must come out of raw unchanged
    assert [sT[a]["k"] for a, *_ in ARMS] == [1906, 2071, 2027, 2515, 1770, 1783, 95]
    assert [sD[a]["k"] for a, *_ in ARMS] == [959, 1024, 1004, 1259, 895, 885, 42]
    assert [s0[a]["k"] for a, *_ in ARMS] == [344, 389, 379, 306, 305, 299, 9]
    assert [s5[a]["k"] for a, *_ in ARMS] == [579, 581, 569, 639, 505, 503, 131]
    assert bxT[E][:2] == (400, 264) and bxD[E][:2] == (198, 134) and v1T[:2] == (758, 13) and v1D[:2] == (372, 8)
    assert bxT["M-ours-dscore-C-V1"][:2] == (20, 629) and bxD["M-ours-dscore-C-V1"][:2] == (13, 313)
    assert bxT["V1-clamp"][:2] == (402, 279) and bxD["V1-clamp"][:2] == (199, 125)
    assert xeT["M-ours-bstar-scalar"][:2] == (406, 105) and xeD["M-ours-bstar-scalar"][:2] == (199, 70)
    assert xeT["gmmB-scorew-eta"][:2] == (379, 122) and xeD["gmmB-scorew-eta"][:2] == (183, 74)
    assert ceT[:2] == (75, 62) and ceD[:2] == (32, 42) and mdd(137) == 25 and mdd(74) == 18
    assert st0[:2] == (112, 73) and st5[:2] == (86, 12) and v10[:2] == (27, 26) and v15[:2] == (134, 0)
    assert sD[B]["k"] - sD[E]["k"] == 64 and f"{R(64 / 1280):.3f}" == "0.050" and f"{R(sD[E]['gap']):+.3f}" == "+0.070"
    assert pe(bxD[E][2]) == "5.3e-4" and bxD[E][2] < 0.05 / 3 and pe(bxT[E][2]) == "1.5e-7"
    bits = bit_identity(); assert all(bits.values()), bits
    ob = observed_before()
    c2same, c2oog, c2n = c2_precheck()
    assert all(c2same.values()) and c2oog == {"V1-edge": 0.0, "V1-clamp": 0.0} and c2n == 40, (c2same, c2oog, c2n)
    assert ob == {"raw_B1e4x": {"M-ours-bstar": 1991, "M-ours-bstar-scalar": 2042, "M-ours-dscore-C-V1": 2560, "R5-genie": 95},
                  "raw_C": {"M-ours-bstar": 1991, "M-ours-bstar-scalar": 2042, "M-ours-dscore-C-V1": 2506, "R5-genie": 95},
                  "raw_B16e4": {"M-ours-bstar": 1946, "M-ours-bstar-scalar": 2066, "M-ours-dscore-C-V1": 2515, "R5-genie": 95},
                  "raw_B32e4x": {"M-ours-bstar": 1918, "M-ours-bstar-scalar": 2037, "M-ours-dscore-C-V1": 2546, "R5-genie": 95}}, ob
    assert f"{R(1918 / 2560):.3f}" == "0.749" and f"{R(2546 / 2560):.3f}" == "0.995"   # the record's B32e4x b* / V1 (K1K2:17, :97)
    cs = cost()
    LOADW = f"1-min load average {cs['load']}, read once at the end of the {cs['wall']} s run"
    wk = {k: int(re.search(r" tasks on (\d+) workers", open(os.path.join(C.CONF, v)).readline())[1]) for k, v in WLOG.items()}
    assert wk == {"dev": 128, "test": 192, "C1 0 dB": 64, "C5 -6 dB": 64}, wk
    CONT = (f"not under the multi-worker contention of the K2 runs ({wk['dev']} workers dev 3200..4479, {wk['test']} test "
            f"0..2559, {wk['C1 0 dB']} per report point)")
    n = sT[E]["n"]
    kst = dt.datetime(*map(int, re.match(r"(\d{4})\. (\d\d)\. (\d\d)\. \(.\) (\d\d):(\d\d):(\d\d) KST", cs["date"]).groups()))
    cdt = kst - dt.timedelta(hours=14)                            # server KST = Texas CDT + 14 h
    WHEN = f"{cdt:%Y-%m-%d %H:%M:%S} CDT (= {kst:%m-%d %H:%M:%S} KST, from date)"

    # ---- per-iteration series (TEST)
    nqV = np.asarray(T["M-ours-dscore-C-V1"]["nu_q"], float); recV = np.isfinite(nqV).all(1)
    nqE = np.asarray(T[E]["nu_q"], float); nqC = np.asarray(T["V1-clamp"]["nu_q"], float)
    assert np.isnan(nqV[~recV]).all() and np.isfinite(nqE).all() and np.isfinite(nqC).all()
    abV, abVrec, abE, abC = (nqV > NU_HI).mean(0), (nqV[recV] > NU_HI).mean(0), (nqE > NU_HI).mean(0), (nqC > NU_HI).mean(0)
    rec1, rec216 = abVrec[0], (nqV[recV][:, 1:] > NU_HI).mean()
    all1, all216 = abV[0], (nqV[:, 1:] > NU_HI).mean()
    assert int(recV.sum()) == 2246 and f"{rec1:.2f} / {rec216:.3f}" == "1.00 / 0.903" and f"{all1:.2f} / {all216:.3f}" == "0.88 / 0.793"
    nu1 = np.unique(np.concatenate([nqE[:, 0], nqC[:, 0], nqV[recV, 0]]))
    assert len(nu1) == 1 and abs(nu1[0] - cs["nu_above"]) < 1e-6
    nuG = np.unique(np.concatenate([np.asarray(T[a]["nu_q"], float)[:, 0] for a in ("M-ours-bstar-scalar", "gmmB-scorew-eta")]))
    assert len(nuG) == 1
    n216 = {a: int((np.asarray(T[a]["nu_q"], float)[:, 1:] > NU_HI).sum()) for a in XE[:2] + (E, "V1-clamp")}
    assert n216 == {"M-ours-bstar-scalar": 13, "gmmB-scorew-eta": 0, E: 1, "V1-clamp": 0}, n216
    NQ = nqE[:, 1:].size
    it_arms = [B, "M-ours-dscore-C-V1", E, "V1-clamp", "R5-genie"]
    blt = {a: be(T, a).mean(0) for a in it_arms}
    COL = {a[0]: a[3] for a in ARMS}; MK = {a[0]: a[4] for a in ARMS}

    # ---- figure (IEEE two-column figure*: <= 7.16 in after the tight bbox; text >= 8 pt, dense annotations 7 pt)
    plt.rcParams.update({"font.size": 8, "axes.labelsize": 8, "axes.titlesize": 8.5, "xtick.labelsize": 8,
                         "ytick.labelsize": 8, "legend.fontsize": 8, "text.color": INK, "axes.labelcolor": INK,
                         "axes.titlecolor": INK, "xtick.labelcolor": INK, "ytick.labelcolor": INK})
    AN = 7                                                           # dense in-axes annotations
    fig = plt.figure(figsize=(7.1, 3.9))
    G = fig.add_gridspec(1, 3, width_ratios=[1.45, 1.15, 1.05], wspace=0.42, left=0.075, right=0.995, bottom=0.18, top=0.935)
    HT = 3                                                           # (a) top : bottom height ratio = scale ratio
    ga = G[0].subgridspec(2, 1, height_ratios=[HT, 1], hspace=0.06)
    gb = G[1].subgridspec(2, 1, height_ratios=[2.0, 1], hspace=0.09)
    aT = fig.add_subplot(ga[0]); aB = fig.add_subplot(ga[1], sharex=aT)
    bT = fig.add_subplot(gb[0]); bB = fig.add_subplot(gb[1], sharex=bT)
    cc = fig.add_subplot(G[2])

    # (a)
    for i, (arm, sh, lab, col, mk) in enumerate(ARMS):
        ms = 6.5 if mk == "*" else 5
        for ax in (aT, aB):
            for S_, dx, fill in ((sT, -0.2, True), (sD, 0.2, False)):
                p, (lo, hi) = S_[arm]["p"], S_[arm]["ci"]
                ax.errorbar([i + dx], [p], yerr=[[p - lo], [hi - p]], color=col, marker=mk, ms=ms, mfc=col if fill else "white",
                            mec=col, ls="none", capsize=2, lw=1.2, label=lab if (ax is aT and fill) else None)
    TOP = (0.60, 1.0)
    aT.set_ylim(*TOP); aT.set_yticks([0.7, 0.8, 0.9, 1.0])
    aB.set_ylim(0.0, (TOP[1] - TOP[0]) / HT); aB.set_yticks([0, 0.05, 0.10])          # same BLER per inch in both halves
    aT.spines["bottom"].set_visible(False); aB.spines["top"].set_visible(False)
    aT.tick_params(axis="x", bottom=False, labelbottom=False)
    d = 0.018
    for ax, y, k in ((aT, 0, 1), (aB, 1, HT)):                                         # break marks, both spines
        for x in (0, 1):
            ax.plot([x - d, x + d], [y - d * k, y + d * k], transform=ax.transAxes, color=INK, lw=0.8, clip_on=False)
    aB.set_xticks(range(len(ARMS))); aB.set_xticklabels([a[1] for a in ARMS], rotation=40, ha="right")
    aB.set_xlim(-0.6, len(ARMS) - 0.4)
    aT.set_ylabel("BLER"); aT.yaxis.set_label_coords(-0.15, 0.4)
    aT.set_title("(a)", loc="left", fontweight="bold")   # paper: panel label only
    aT.text(6.38, 0.955, f"GMM prior →\nout-of-grid rule\ndev.: {bxD[E][0]}:{bxD[E][1]}\n$p={pt(bxD[E][2])}$\n"
            f"test: {bxT[E][0]}:{bxT[E][1]}\n$p={pt(bxT[E][2])}$\nProposed →\nout-of-grid rule\ntest: {v1T[0]}:{v1T[1]}\n"
            f"$p={pt(v1T[2])}$",
            ha="right", va="top", fontsize=AN, linespacing=1.1,
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="0.7", lw=0.6))
    aB.text(-0.5, 0.125, f"test: clamped queries\n→ out-of-grid rule\n{ceT[0]}:{ceT[1]}, $p={pt(ceT[2])}$ (n.s.)", ha="left", va="top", fontsize=AN,
            linespacing=1.15)

    # (b)
    t = np.arange(1, 17)
    for arm in it_arms:
        clamp = arm == "V1-clamp"
        bT.plot(t, blt[arm], color=COL[arm], marker=MK[arm], ms=5 if MK[arm] == "*" else 3.6, lw=1.1 if clamp else 1.3,
                ls="--" if clamp else S.GENIE["ls"] if arm == "R5-genie" else "-", mfc="white" if clamp else COL[arm],
                markevery=(1, 2) if clamp else ((0, 2) if arm == E else 1), zorder=4 if clamp else 3 if arm == E else 2)
    bT.set_ylim(0, 1.03); bT.set_ylabel("BLER after iteration $t$")
    bT.tick_params(axis="x", labelbottom=False)
    bT.set_title("(b)", loc="left", fontweight="bold")   # paper: panel label only
    bT.legend([Line2D([], [], color=COL[E], marker="o", ms=3.6, lw=1.3),
               Line2D([], [], color=COL["V1-clamp"], marker="^", mfc="white", ms=3.6, lw=1.1, ls="--")],
              ["Out-of-grid rule", "Clamped queries"], loc="center right", bbox_to_anchor=(1.0, 0.45), fontsize=8,
              frameon=False, handlelength=2.2)
    bB.step(t, abVrec, where="mid", color=COL["M-ours-dscore-C-V1"], lw=1.3)
    bB.step(t, abE, where="mid", color=COL[E], lw=1.3)
    bB.step(t, abC, where="mid", color=COL["V1-clamp"], lw=1.1, ls="--")
    bB.set_ylim(-0.1, 1.15); bB.set_yticks([0, 0.5, 1]); bB.set_xticks([1, 4, 8, 12, 16]); bB.set_xlim(0.5, 16.5)
    bB.set_xlabel("outer iteration $t$"); bB.set_ylabel("share of blocks\nwith $\\nu_q>\\nu_{\\rm hi}$")
    for ax in (bT, bB):
        ax.yaxis.set_label_coords(-0.19, 0.5)
    bB.text(16.2, 0.8, f"Proposed\n({int(recV.sum())} non-aborted blocks)", color=INK, fontsize=AN,
            ha="right", va="top", linespacing=1.1)
    bB.text(16.2, 0.08, "Out-of-grid rule, clamped\nqueries (curves overlap)", color=INK, fontsize=AN, ha="right", va="bottom",
            linespacing=1.1)

    # (c)
    xs = np.linspace(-0.3, 0.3, len(ARMS))
    for gi, S_ in enumerate((s0, s5)):
        for dx, (arm, sh, lab, col, mk) in zip(xs, ARMS):
            p, (lo, hi) = S_[arm]["p"], S_[arm]["ci"]
            cc.errorbar([gi + dx], [p], yerr=[[p - lo], [hi - p]], color=col, marker=mk, ms=7 if mk == "*" else 4.2, mfc="white",
                        mec=col, ls="none", capsize=1.5, lw=1.0)
    cc.text(0.5, 1.31, "GMM prior →\nout-of-grid rule: $a{:}b$, $p$", ha="center", va="top", fontsize=AN, linespacing=1.1)
    for gi, (a, b, p) in enumerate((st0, st5)):
        cc.text(gi, 1.19, f"{a}:{b}\n${pt(p)}$", ha="center", va="top", fontsize=AN, linespacing=1.15)
    cc.set_xticks([0, 1]); cc.set_xticklabels(["8×4\n2 pilots\n0 dB", "8×4\n3 pilots\n−6 dB$^{\\dagger}$"]); cc.set_xlim(-0.55, 1.55)
    cc.set_ylim(-0.03, 1.32); cc.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    cc.set_ylabel("BLER")
    cc.set_title("(c)", loc="left", fontweight="bold")   # paper: panel label only
    cc.text(1.52, s5[E]["ci"][0] - 0.03, "Out-of-grid rule,\nclamped queries", ha="right", va="top", fontsize=AN, linespacing=1.1)  # aqua: direct label
    cc.text(0.5, -0.2, "$^{\\dagger}$below the main SNR\ngrid (−3 to 15 dB)", transform=cc.transAxes,
            ha="center", va="top", fontsize=AN, linespacing=1.1)

    h, l = aT.get_legend_handles_labels()
    h += [Line2D([], [], color=INK2, marker="o", ls="none", ms=5),
          Line2D([], [], color=INK2, marker="o", mfc="white", ls="none", ms=5)]
    l += ["(a) filled: test trials (n = 2560)", "(a) hollow: development trials (n = 1280);\n(c): development trials (n = 640)"]
    fig.legend(h, l, loc="upper center", ncol=3, bbox_to_anchor=(0.5, -0.025), frameon=False, columnspacing=0.9,
               handletextpad=0.35, handlelength=1.4)
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(FIG, f"F18_oog_rule_K2.{ext}"))

    # ---- table T_K2 (LaTeX + plain)
    ROLE = {("bx", "T", E): "C", ("bx", "D", E): "P", ("xe", "M-ours-dscore-C-V1"): "M",
            ("xe", "M-ours-bstar-scalar"): "W", ("xe", "gmmB-scorew-eta"): "W", ("xe", "V1-clamp"): "\\|"}

    def mk(mark):
        return "" if not mark else (r"$^{\|}$" if mark == "\\|" else rf"$^{{\rm {mark}}}$")

    def cmp_tex(r, mark):
        """(a:b with its role mark, (p) for the row below)."""
        a, b, p = r
        return f"{a}:{b}{mk(mark)}", f"(${pt(p)}$)"

    def ab_tex(arm):
        if arm == "M-ours-dscore-C-V1":
            return rf"{R(rec1):.2f} / {R(rec216):.3f}$^{{\S}}$"
        a = sT[arm]["ab"]
        return "--" if a is None else f"{R(a[0]):.2f} / {R(a[1]):.3f}"

    pl = lambda x: (re.sub(r"\$\^\{\\rm (\w)\}\$", r"[\1]", re.sub(r"\$\^\{\\\|\}\$", "[||]", x))
                    .replace("{\\times}10^{", "e").replace("$^{\\S}$", "[S]").replace("}$", "").replace("$", ""))
    TX, TP = [], []
    for arm, *_ in ARMS:
        r, dv = sT[arm], sD[arm]
        bT_, pbT = cmp_tex(bxT[arm], ROLE.get(("bx", "T", arm))) if arm in BX else ("", "")
        xT_, pxT = cmp_tex(xeT[arm], ROLE.get(("xe", arm))) if arm in XE else ("", "")
        bD_ = cmp_tex(bxD[arm], ROLE.get(("bx", "D", arm)))[0] if arm in BX else ""
        xD_ = cmp_tex(xeD[arm], ROLE.get(("xe", arm)))[0] if arm in XE else ""
        nm, sub = TEXNAME[arm]
        TX.append(" & ".join([nm, str(r["k"]), f"{R(r['p']):.3f} [{r['ci'][0]:.3f}, {r['ci'][1]:.3f}]", f"${R(r['gap']):+.3f}$",
                              bT_, xT_, "--" if r["guard"] is None else str(r["guard"]), str(r["exc"]), ab_tex(arm),
                              str(dv["k"]), bD_, xD_]) + r" \\")
        if sub or pbT or pxT:                                    # second line: role of the arm, p under each test a:b
            TX.append(" & ".join([sub, "", "", "", pbT, pxT] + [""] * 6) + r" \\[1pt]")
        TP.append(f"{arm:<20} {r['k']:>5} {R(r['p']):.3f} [{r['ci'][0]:.3f}, {r['ci'][1]:.3f}] {R(r['gap']):>+7.3f} "
                  f"{pl(bT_ + ' ' + pbT if bT_ else ''):>24} {pl(xT_ + ' ' + pxT if xT_ else ''):>24} "
                  f"{'--' if r['guard'] is None else r['guard']:>5} {r['exc']:>4} {pl(ab_tex(arm)):>16} | "
                  f"{dv['k']:>5} {pl(bD_):>11} {pl(xD_):>10}")
    e, cl, v1 = cs["V1-edge"], cs["V1-clamp"], cs["M-ours-dscore-C-V1"]
    fwd_tex = e["fwd"].replace(" x batch ", r"{\times}").replace(" + ", "+")
    assert fwd_tex == r"16{\times}1+300{\times}16", fwd_tex
    CT = [("M-ours-dscore-C-V1", v1, f"{v1['fw']}"), (E, e, rf"{e['fw']} (${fwd_tex}$)"), ("V1-clamp", cl, f"{cl['fw']}")]
    CTN = {"M-ours-dscore-C-V1": "V1 frozen (extrapolates)", E: r"\textbf{V1-edge} (registered primary variant)",
           "V1-clamp": "V1-clamp (registered secondary variant)"}          # the cost table has room for the full role
    ctx = [" & ".join([CTN[a], fw, str(c["jac"]), f"{c['s']:.3f} [{c['lo']:.3f}--{c['hi']:.3f}]", str(c["reps"]), f"{c['qpb']:.2f}",
                       rf"{c['xblk']:.2f}$\times$"]) + r" \\" for a, c, fw in CT]
    dp = lambda arm, X, key: f"${pt(X[arm][2])}$" + mk(ROLE.get(key))          # development p with its cell's role mark
    cap = (r"\caption{Out-of-grid query rule (K2) at cell C1 (8$\times$4, $T{=}16$, $T_p{=}2$) $-3$\,dB, "
           r"$N_{\rm train}{=}1.6{\times}10^5$: V1-edge, the registered primary variant, is a separate registered arm (grid-related changes need their own registration). "
           r"Where: V1-edge fails less often than the GMM prior $b^*$. Registered primary test on fresh development trials "
           rf"3200..4479: $b^*{{\to}}$V1-edge {bxD[E][0]}:{bxD[E][1]}, $p{{=}}{pt(bxD[E][2])}<0.05$ (registered criterion) "
           r"$\Rightarrow$ branch (i); it also holds under Holm $m{=}3$ ($p{<}0.0167$; family = the 3 registered primary tests "
           r"P3, A1, K2). Test confirmation on test trials 0..2559, run once by user decision: "
           rf"{sT[E]['k']} vs {sT[B]['k']} fails of {n}, $b^*{{\to}}$V1-edge {bxT[E][0]}:{bxT[E][1]}, $p{{=}}{pt(bxT[E][2])}$. "
           rf"How much: {sT[B]['k'] - sT[E]['k']} fewer failed blocks on test (BLER $-{R((sT[B]['k'] - sT[E]['k']) / n):.3f}$); "
           rf"gap position ${R(sT[E]['gap']):+.3f}$ (development: {sD[B]['k'] - sD[E]['k']} fewer of {sD[E]['n']}, BLER "
           rf"$-{R((sD[B]['k'] - sD[E]['k']) / sD[E]['n']):.3f}$, gap position ${R(sD[E]['gap']):+.3f}$): most of the gap to the "
           r"known-channel reference (R5) remains. "
           r"Why: the frozen V1 extrapolates its above-grid iteration-1 query and runs away (F3 guard on every block); V1-edge "
           rf"answers that query from the in-grid learned score and the later queries are in-grid ({n216[E]} of {NQ} above); "
           rf"mechanism check V1 frozen$\to$V1-edge {v1T[0]}:{v1T[1]} ($p{{=}}{pt(v1T[2])}$). "
           rf"V1-clamp$\to$V1-edge is not decided: test {ceT[0]}:{ceT[1]}, $p{{=}}{pt(ceT[2])}$, $n_d$ {sum(ceT[:2])}, "
           rf"MDD {mdd(sum(ceT[:2]))}, $|\Delta|$ {abs(sT['V1-clamp']['k'] - sT[E]['k'])}; development {ceD[0]}:{ceD[1]}, "
           rf"$p{{=}}{pt(ceD[2])}$, $n_d$ {sum(ceD[:2])}, MDD {mdd(sum(ceD[:2]))}, $|\Delta|$ {abs(sD['V1-clamp']['k'] - sD[E]['k'])}. "
           r"Limits: an above-grid query is not by itself sufficient for collapse (the $T_p{<}N_t$ null directions decide); this "
           r"shows only that the rule removes the frozen V1's runaway at this point. The headline checkpoint (sha256[:16] "
           r"4443921ce8d5c4a1) and V1's definition (extrapolation above the grid) are unchanged; every other V1 number is the "
           r"frozen V1. The cell was chosen post hoc (after the C1/C5 low-SNR collapse was seen). Observed before on these test "
           r"trials: the frozen V1 and R5 (both bit-identical to the earlier run), $b^*$ and the scalar-site $b^*$ at older fits "
           rf"($N_{{\rm train}}{{=}}10^4$; $1.6{{\times}}10^5$ with $K{{\le}}512$: $b^*$ {ob['raw_B16e4']['M-ours-bstar']} fails; "
           rf"$3.2{{\times}}10^5$: $b^*$ BLER {R(ob['raw_B32e4x']['M-ours-bstar'] / n):.3f}) and earlier V1 runs (incl. the "
           rf"$3.2{{\times}}10^5$ V1: BLER {R(ob['raw_B32e4x']['M-ours-dscore-C-V1'] / n):.3f}); new there: the $K{{=}}1024$ runs of $b^*$ "
           rf"({sT[B]['k']}), the scalar-site $b^*$ ({sT['M-ours-bstar-scalar']['k']}) and $b^*$ in V1's wiring "
           rf"({sT['gmmB-scorew-eta']['k']}), V1-edge and V1-clamp. V1-edge was measured only at C1 $-3$\,dB (plus the report "
           r"points C1 0\,dB and C5 $-6$\,dB, the latter outside the registered SNR grid (a pre-registered low-SNR extension point); "
           r"report-only, Fig.~\ref{fig:k2_oog_rule}(c); apart from these, only the registered " + str(c2n) + r"-trial C2 $-3$\,dB "
           r"pre-check on development trials 2560..2599, where V1-edge and V1-clamp are bit-identical to V1, "
           r"$n_{\rm oog}{=}0$), not at the decision points of C1 or C5, and only at $N_{\rm train}{=}1.6{\times}10^5$. "
           r"The registered verdicts of cells C1 and C5 (table B, $N_{\rm train}{=}3.2{\times}10^5$, $b^*{\to}$V1: C1 GMM better at "
           r"3/3 decision points, +6/+9/+15\,dB; C5 not significant, GMM better at 1/3 and V1 at 1/3, +6/+12/+15\,dB) and the "
           r"headline are unchanged.}")
    notes = (r"\par\smallskip\parbox{\textwidth}{\scriptsize V1-edge / V1-clamp: the registered primary / secondary "
             r"variants of the out-of-grid query rule. BLER after 16 outer iterations; fails = failed blocks; a block whose "
             r"arm raised is a block error; F3 guard: blocks in which the F3 guard fired; exc.: blocks whose arm raised. Gap "
             r"position $(b^*-X)/(b^*-\mathrm{genie})$. $a{:}b$: $a$ = the first arm fails and "
             r"the second succeeds, $b$ = the reverse; two-sided exact sign test on paired blocks. Roles: $^{\rm P}$registered "
             r"primary test (decides); $^{\rm C}$test confirmation (run once by user decision); $^{\rm M}$mechanism check V1 "
             r"frozen$\to$V1-edge (test: part of the registered confirmation; development: registered, report-only); "
             r"$^{\rm W}$wiring-matched controls (registered, report-only, no verdict label); $^{\|}$registered report-only "
             r"comparison, recorded three-way (clamp fewer failures / not decided / edge fewer failures); here: not decided "
             r"($n_d$, MDD, $|\Delta|$ in the caption); unmarked: report-only; blank: "
             r"comparison not listed. "
             rf"Development $p$: $b^*{{\to}}X$ V1 frozen {dp('M-ours-dscore-C-V1', bxD, ('bx', 'D', 'M-ours-dscore-C-V1'))}, "
             rf"V1-edge {dp(E, bxD, ('bx', 'D', E))}, V1-clamp {dp('V1-clamp', bxD, ('bx', 'D', 'V1-clamp'))}; $X{{\to}}$V1-edge "
             rf"{dp('M-ours-bstar-scalar', xeD, ('xe', 'M-ours-bstar-scalar'))} (scalar site), "
             rf"{dp('gmmB-scorew-eta', xeD, ('xe', 'gmmB-scorew-eta'))} (V1's wiring), "
             rf"{dp('M-ours-dscore-C-V1', xeD, ('xe', 'M-ours-dscore-C-V1'))} (V1 frozen), "
             rf"{dp('V1-clamp', xeD, ('xe', 'V1-clamp'))} (V1-clamp). "
             r"genie (R5): known-channel reference (same LMMSE-PIC/BCJR loop, true $H$), not a bound. "
             rf"$^{{\dagger}}$Share of blocks whose prior query has $\nu_q>\nu_{{\rm hi}}={NU_HI:.4f}$ (top of the $\sigma$ grid), at "
             rf"$t{{=}}1$ / over $t{{=}}2$--16. The score arms' iteration-1 query has $\nu_q={nu1[0]:.3f}$ in every recorded block; "
             rf"the two GMM arms with a scalar query level query at $\nu_q={nuG[0]:.3f}$ (GMM priors are closed form with no "
             r"$\sigma$ grid; listed for the query level only). --: $b^*$ (exact site) and genie (R5) have no scalar query level "
             rf"$\nu_q$ (not recorded); genie has no F3 guard. 0.000 is rounded: V1-edge {n216[E]}, $b^*$ scalar site "
             rf"{n216['M-ours-bstar-scalar']}, the others 0 of {NQ} queries. $^{{\S}}$Over the frozen V1's {int(recV.sum())} "
             rf"recorded (non-raised) blocks; the registered report counts its {int((~recV).sum())} raised blocks (no $\nu_q$ "
             rf"record) as not above: {R(all1):.2f} / {R(all216):.3f}.}}")
    cnotes = (r"\par\smallskip\parbox{\textwidth}{\scriptsize $^{\ddagger}$Method: median of $N$ timed calls "
              r"(\texttt{time.perf\_counter}) of \texttt{prior.\_eval} on one above-grid query; one CPU thread (torch, OMP, MKL "
              rf"threads = 1), float64; synthetic $q = h + \mathcal{{CN}}(0,\nu I)$ at the recorded iteration-1 $\nu={cs['nu_above']:.3f}$ "
              rf"(the receiver's $q$ is not stored), a new $q$ per call after one untimed warm-up; {LOADW}, "
              rf"{CONT}; LMMSE-PIC and BCJR excluded. Forwards count "
              r"network calls (V1-edge: 16 at batch 1 + 300 at batch 16); a Jacobian is one reverse-mode \texttt{jacrev} of the "
              r"64-dim real denoiser. Prior time per block: measured above-grid queries per block at C1 $-3$\,dB test (frozen V1: "
              rf"over its {int(recV.sum())} recorded blocks) times the median, plus in-grid V1 queries for the rest of the 16 "
              rf"iterations, relative to 16 in-grid V1 queries ({cs['ref16']:.3f}\,s). oog\_cost.txt (code/bench\_oog.py), run "
              rf"{cdt:%Y-%m-%d %H:%M} CDT.}}")
    tex = [r"% T_K2 -- generated by conf/code/figure_f18.py from raw_review_next_K2test / raw_review_next_K2 and results/review_next/oog_cost.txt.",
           r"% Requires \usepackage{booktabs,amsmath}. Natural width <= \textwidth (no \resizebox). Do not edit by hand; rerun the script.",
           r"% The caption cites Fig.~\ref{fig:k2_oog_rule}(c): the F18 figure environment must carry \label{fig:k2_oog_rule}.",
           r"\begin{table*}[t]", r"\centering", r"\scriptsize", r"\setlength{\tabcolsep}{2.4pt}", cap, r"\label{tab:k2_oog_rule}",
           r"\begin{tabular}{lrcrccrrcrcc}", r"\toprule",
           r" & \multicolumn{8}{c}{test trials 0..2559 ($n{=}2560$); confirmation, run once by user decision} & "
           r"\multicolumn{3}{c}{dev.\ 3200..4479 ($n{=}1280$)} \\",
           r"\cmidrule(lr){2-9}\cmidrule(lr){10-12}",
           r" & & BLER & gap & $b^*{\to}X$ & $X{\to}$V1-edge & F3 & & $\nu_q{>}\nu_{\rm hi}$$^{\dagger}$ & & $b^*{\to}X$ & $X{\to}$V1-edge \\",
           r"arm & fails & [95\% Wilson] & pos. & $a{:}b$, ($p$) & $a{:}b$, ($p$) & guard & exc. & $t{=}1$ / 2--16 & fails & $a{:}b$ & $a{:}b$ \\",
           r"\midrule"] + TX + [r"\bottomrule", r"\end{tabular}", notes,
           r"\par\medskip", r"\begin{tabular}{llrcrrr}", r"\toprule",
           r"\multicolumn{7}{l}{cost per above-grid prior query$^{\ddagger}$} \\", r"\cmidrule(lr){1-7}",
           r" & network & & seconds & & above-grid & prior time \\",
           r"arm & forwards & Jacobians & median [min--max] & $N$ & queries / block & per block \\", r"\midrule"] + ctx + [
           r"\bottomrule", r"\end{tabular}", cnotes, r"\end{table*}"]
    texs = "\n".join(tex) + "\n"
    assert not re.search(r"[\x00-\x09\x0b-\x1f\x7f]", texs), "control character in T_K2"          # e.g. a TAB from '\t'
    assert texs.count("{") == texs.count("}") and "\\resizebox" not in texs.split("\n", 2)[2]
    # paper version: the table T_K2 is built and checked as in the original but not written

    # ---- caption / numbers file
    W = lambda S_, a: f"{S_[a]['k']}/{S_[a]['n']} = {R(S_[a]['p']):.4f} [{S_[a]['ci'][0]:.4f}, {S_[a]['ci'][1]:.4f}]"
    txt = ["F18 -- out-of-grid query rule (K2): V1-edge, a separate registered arm.  Numbers recomputed from the raw files by "
           "code/figure_f18.py; cost from results/review_next/oog_cost.txt (code/bench_oog.py).  p: < 0.01 as m.me-k.", "",
           "(a) C1 (8x4, T=16, Tp=2) -3 dB, BLER@16 (blk_err at the 16th outer iteration, non-finite -> failure), 95% Wilson:",
           f"  {'arm':<20} {'TEST 0..2559 raw_review_next_K2test':<40} {'DEV 3200..4479 raw_review_next_K2':<40}"]
    for arm, *_ in ARMS:
        txt.append(f"  {arm:<20} {W(sT, arm):<40} {W(sD, arm):<40}")
    txt += [f"  test: b* -> V1-edge {bxT[E][0]}:{bxT[E][1]} p={pe(bxT[E][2])} (confirmation, K2test_report.txt:12); V1 frozen -> "
            f"V1-edge {v1T[0]}:{v1T[1]} p={pe(v1T[2])} (mechanism, part of the registered confirmation, :13); V1-clamp -> V1-edge "
            f"{ceT[0]}:{ceT[1]} p={pe(ceT[2])} ([||] registered report-only, recorded three-way: not decided, :18)",
            f"  dev: b* -> V1-edge {bxD[E][0]}:{bxD[E][1]} p={pe(bxD[E][2])} (registered primary test, K2_report.txt:12); V1 -> "
            f"V1-edge {v1D[0]}:{v1D[1]} p={pe(v1D[2])} (mechanism, report-only, :13); V1-clamp -> V1-edge {ceD[0]}:{ceD[1]} "
            f"p={pe(ceD[2])} ([||] registered report-only, recorded three-way: not decided, :20)",
            f"  wiring-matched controls X -> V1-edge (report-only, NEXT_EXPERIMENTS_K1K2.md:82): scalar site test "
            f"{xeT['M-ours-bstar-scalar'][0]}:{xeT['M-ours-bstar-scalar'][1]} / dev {xeD['M-ours-bstar-scalar'][0]}:"
            f"{xeD['M-ours-bstar-scalar'][1]}; V1's wiring test {xeT['gmmB-scorew-eta'][0]}:{xeT['gmmB-scorew-eta'][1]} / dev "
            f"{xeD['gmmB-scorew-eta'][0]}:{xeD['gmmB-scorew-eta'][1]} (K2test_report.txt:14-15, K2_report.txt:14-15)",
            "", "(b) C1 -3 dB TEST (n=2560): BLER after outer iteration t = 1..16 (a raised block has no per-iteration record and "
            "counts as a failure at every t):"]
    for arm in it_arms:
        txt.append(f"  {arm:<20} " + " ".join(f"{R(x):.3f}" for x in blt[arm]))
    txt += [f"  share of blocks with nu_q > nu_hi = {NU_HI} at iteration t (plotted: the frozen V1's recorded blocks):",
            f"  V1 frozen ({int(recV.sum())} rec.) " + " ".join(f"{R(x):.3f}" for x in abVrec),
            "  V1 frozen (all 2560)  " + " ".join(f"{R(x):.3f}" for x in abV) + "   <- registered report's definition "
            "(raised block = not above; K2test_report.txt:7)",
            "  V1-edge               " + " ".join(f"{R(x):.4f}" for x in abE),
            "  V1-clamp              " + " ".join(f"{R(x):.4f}" for x in abC),
            f"  iteration-1 nu_q is the same in every recorded block of the three score arms: {nu1[0]:.6f} (> nu_hi); the two GMM "
            f"arms with a scalar query level (scalar site, V1's wiring): {nuG[0]:.6f}.  Iterations 2..16: V1 frozen "
            f"{R(rec216):.3f} of its {int(recV.sum())} recorded blocks ({R(all216):.3f} counting its {int((~recV).sum())} raised blocks, "
            f"which carry no nu_q, as not above); V1-edge {n216[E]} of {NQ} queries (one block, t=2); V1-clamp {n216['V1-clamp']}; "
            f"b* scalar site {n216['M-ours-bstar-scalar']}; b* in V1's wiring {n216['gmmB-scorew-eta']}.  n_oog (unique above-grid "
            f"queries/block): V1-edge {np.mean(T[E]['n_oog']):.4f}, V1-clamp {np.mean(T['V1-clamp']['n_oog']):.4f}.",
            "", "(c) report points, development trials 2560..3199 (raw_review_next_K2, n=640), BLER@16, 95% Wilson (report-only, "
            "no labels; C5 -6 dB is outside the registered SNR grid):"]
    for nm, S_, a1, a2 in (("C1 0 dB", s0, st0, v10), ("C5 -6 dB", s5, st5, v15)):
        txt.append(f"  {nm}: " + "; ".join(f"{a} {S_[a]['k']} ({R(S_[a]['p']):.3f} [{S_[a]['ci'][0]:.3f}, {S_[a]['ci'][1]:.3f}])" for a, *_ in ARMS))
        txt.append(f"    b* -> V1-edge {a1[0]}:{a1[1]} p={pe(a1[2])}; V1 frozen -> V1-edge {a2[0]}:{a2[1]} p={pe(a2[2])}; F3 guard "
                   f"V1 frozen {S_['M-ours-dscore-C-V1']['guard']}, V1-edge {S_[E]['guard']}")
    txt += ["  (K2_report.txt:26-42 C1 0 dB, :47-63 C5 -6 dB; b*->V1-edge at :33 and :54)", "",
            f"Re-check of audit §5.3 (NEXT_EXPERIMENTS_K1K2.md:187): TEST frozen V1 and R5-genie vs raw_B16e4 C1 -3 dB trials 0..2559, "
            f"every KEYS_RAW field @1..16 bit-identical: {bits}",
            f"Re-check of the registered C2 -3 dB pre-check (NEXT_EXPERIMENTS_K1K2.md:118): raw_review_next_K2pre_c2 dev trials "
            f"2560..2599 (n={c2n}), V1-edge / V1-clamp == V1 on every KEYS_RAW field @1..16: {c2same}; n_oog sum {c2oog}", "",
            "Table T_K2 (figs/T_K2_oog_rule.tex), plain text.  Roles: [P] registered primary test, [C] test confirmation, "
            "[M] mechanism check V1 frozen -> V1-edge (test: part of the registered confirmation content, NEXT_EXPERIMENTS_K1K2.md "
            "§2.6 :96-97; dev: registered, report-only, §2.3 :80-81), [W] wiring-matched control (registered, report-only, :82), "
            "[||] registered report-only comparison V1-clamp -> V1-edge, recorded three-way (clamp fewer failures / not decided / "
            "edge fewer failures; §2.3 :83), here: not decided (n_d, MDD, |Delta| in the caption), unmarked report-only;",
            "  [S] recorded (non-raised) blocks; the dev columns carry no p (listed in the notes).",
            f"  {'arm':<20} {'fails':>5} {'BLER [95% Wilson]':<20} {'gap':>7} {'test b*->X a:b (p)':>24} {'test X->V1-edge a:b (p)':>24} "
            f"{'guard':>5} {'exc.':>4} {'nu_q>nu_hi t1/2-16':>16} | {'dev':>5} {'b*->X':>11} {'X->edge':>10}"]
    txt += ["  " + x for x in TP]
    txt += [f"  cost (per above-grid query; oog_cost.txt run {WHEN}): network work lines {v1['ln']}, {cl['ln']}, {e['ln']}; "
            f"seconds lines {v1['ls']}, {cl['ls']}, {e['ls']}; per-block lines {v1['lb']}, {cl['lb']}, {e['lb']}"]
    for nm, c in (("V1 frozen", v1), ("V1-edge", e), ("V1-clamp", cl)):
        txt.append(f"    {nm:<10} {c['fw']:>3} forwards ({c['fwd']}), {c['jac']:>2} Jacobian{'s' if c['jac'] != 1 else ''}, {c['s']:.3f} s median [{c['lo']:.3f}-"
                   f"{c['hi']:.3f}] over {c['reps']} calls; {c['qpb']:.4f} above-grid queries/block -> {c['xblk']:.2f}x the "
                   f"prior time of 16 in-grid V1 queries ({cs['ref16']:.3f} s)")
    txt += ["", "CAPTION (paper order: where, how much, why, then scope):",
            f"Where. In cell C1 (8x4, T=16, Tp=2 < Nt=4: pilot-deficient) at -3 dB, V1-edge -- the registered primary variant of "
            f"the out-of-grid query rule, a separate registered arm (10_SPEC_stageC.md §6j :702, :719) -- fails less often than the GMM prior b* (kron K=1024, "
            f"B16e4k fits).  Registered primary test on the fresh development trials 3200..4479 (n=1280): b* -> V1-edge "
            f"{bxD[E][0]}:{bxD[E][1]}, p = {pe(bxD[E][2])} < 0.05 (the registered criterion) -> branch (i) "
            "(NEXT_EXPERIMENTS_K1K2.md:132; K2_report.txt:12); it also holds under Holm m = 3 (p < 0.0167), the family being the "
            "3 registered primary tests P3, A1 and K2 (NEXT_EXPERIMENTS_K1K2.md:23).  Test confirmation on trials 0..2559 (n=2560), "
            "run once by user decision (DECISIONS.md:191; NEXT_EXPERIMENTS_K1K2.md:97, :148): V1-edge "
            f"{W(sT, E)} vs b* {W(sT, B)}; b* -> V1-edge {bxT[E][0]}:{bxT[E][1]}, p = {pe(bxT[E][2])} "
            f"(NEXT_EXPERIMENTS_K1K2.md:160), with the registered mechanism check V1 frozen -> V1-edge {v1T[0]}:{v1T[1]}, "
            f"p = {pe(v1T[2])} (registered in §2.6, NEXT_EXPERIMENTS_K1K2.md:97; value :160; K2test_report.txt:13).",
            f"How much. {sT[B]['k'] - sT[E]['k']} fewer failed blocks of {n} on test (BLER -{R((sT[B]['k'] - sT[E]['k']) / n):.3f}), "
            f"{sD[B]['k'] - sD[E]['k']} of 1280 on development (-{R((sD[B]['k'] - sD[E]['k']) / sD[E]['n']):.3f}).  Gap position "
            f"(b* - X)/(b* - genie) = {R(sT[E]['gap']):+.3f} (test) / {R(sD[E]['gap']):+.3f} (development), i.e. about +0.07: V1-edge passes b* but most of the "
            f"gap to the known-channel reference (R5) remains (genie (R5) {sT['R5-genie']['k']}/{n}; the known-channel reference is "
            "the same LMMSE-PIC/BCJR loop with the true H, not a bound).",
            f"Why (panel b). The score arms' iteration-1 prior query has nu_q = {nu1[0]:.3f} > nu_hi = {NU_HI:.4f} (top of the "
            f"measured sigma grid) in every recorded block (the two GMM arms with a scalar query level query at {nuG[0]:.3f}; GMM "
            f"priors are closed form, with no sigma grid).  The frozen V1 extrapolates it (its registered definition), the loop runs "
            f"away (F3 guard {sT['M-ours-dscore-C-V1']['guard']}/{n}, {sT['M-ours-dscore-C-V1']['exc']} raised blocks) and keeps "
            f"querying above the grid ({R(rec216):.2f} of iterations 2..16 over its {int(recV.sum())} recorded blocks; the registered "
            f"report counts the {int((~recV).sum())} raised blocks, which carry no nu_q, as not above: {R(all216):.2f}): BLER "
            f"{R(sT['M-ours-dscore-C-V1']['p']):.3f}.  V1-edge answers only that above-grid query, from the in-grid learned score (exact "
            "noise split q = z + e2, Langevin sampling of z | q at nu_hi; NEXT_EXPERIMENTS_K1K2.md:64); from t = 2 the loop's "
            f"queries are in-grid ({n216[E]} above-grid query in {NQ}), F3 guard {sT[E]['guard']}, exceptions {sT[E]['exc']}; "
            f"mechanism check V1 frozen -> V1-edge {v1T[0]}:{v1T[1]} (p = {pe(v1T[2])}).  The registered secondary variant V1-clamp (D(q, nu_hi)) "
            f"also removes the runaway: its queries are above the grid only at t = 1 ({n216['V1-clamp']} of {NQ} later), F3 guard "
            f"{sT['V1-clamp']['guard']}, exceptions {sT['V1-clamp']['exc']}, {sT['V1-clamp']['k']}/{n} failed; in panel (b) its "
            f"curves (dashed, open triangles) lie on V1-edge's.",
            "Report points (panel c; development trials 2560..3199, n=640; report-only, no labels: NEXT_EXPERIMENTS_K1K2.md:137; "
            f"K2_report.txt:26-63).  C1 0 dB: b* {s0[B]['k']} / V1 {s0['M-ours-dscore-C-V1']['k']} / V1-edge {s0[E]['k']} / clamp "
            f"{s0['V1-clamp']['k']} / genie {s0['R5-genie']['k']}; b* -> V1-edge {st0[0]}:{st0[1]}, p = {pe(st0[2])}; V1 frozen -> "
            f"V1-edge {v10[0]}:{v10[1]}, p = {pe(v10[2])} (the frozen V1 does not run away at 0 dB: F3 guard "
            f"{s0['M-ours-dscore-C-V1']['guard']}).  C5 (Tp=3) -6 dB, a point outside the registered SNR grid (10_SPEC_stageC.md §6p "
            f":740, :774 low-SNR extension point; NEXT_EXPERIMENTS_K1K2.md:67): b* {s5[B]['k']} / V1 {s5['M-ours-dscore-C-V1']['k']} / V1-edge "
            f"{s5[E]['k']} / clamp {s5['V1-clamp']['k']} / genie {s5['R5-genie']['k']}; b* -> V1-edge {st5[0]}:{st5[1]}, "
            f"p = {pe(st5[2])}.",
            "V1-clamp and cost (table T_K2).  V1-clamp -> V1-edge, a registered report-only comparison recorded three-way "
            f"(NEXT_EXPERIMENTS_K1K2.md:83), is not decided: test {ceT[0]}:{ceT[1]}, "
            f"p = {pe(ceT[2])}, n_d {sum(ceT[:2])}, MDD {mdd(sum(ceT[:2]))}, |Delta| {abs(sT['V1-clamp']['k'] - sT[E]['k'])}; "
            f"development {ceD[0]}:{ceD[1]}, p = {pe(ceD[2])}, n_d {sum(ceD[:2])}, MDD {mdd(sum(ceD[:2]))}, |Delta| "
            f"{abs(sD['V1-clamp']['k'] - sD[E]['k'])} (NEXT_EXPERIMENTS_K1K2.md:134, :190).  "
            f"Cost per above-grid query (oog_cost.txt, code/bench_oog.py; run {cdt:%Y-%m-%d %H:%M} CDT): median of {v1['reps']} "
            f"(V1 frozen, V1-clamp) / {e['reps']} (V1-edge) timed calls (time.perf_counter) of prior._eval, one CPU thread, float64, "
            f"on synthetic q = h + CN(0, nu I) at the recorded iteration-1 nu = {cs['nu_above']:.3f} (the receiver's q is not "
            f"stored in raw; a new q per call after one untimed warm-up), on this host ({LOADW}; {CONT}), "
            f"LMMSE-PIC/BCJR excluded: V1 frozen and V1-clamp {v1['fw']} network "
            f"forwards + {v1['jac']} Jacobian ({v1['s']:.3f} / {cl['s']:.3f} s), V1-edge {e['fw']} forwards ({e['fwd']}) + "
            f"{e['jac']} Jacobians ({e['s']:.2f} s, range {e['lo']:.2f}-{e['hi']:.2f}); with {e['qpb']:.2f} above-grid query per "
            f"block the prior-network time per block is {e['xblk']:.2f}x (edge) and {cl['xblk']:.2f}x (clamp) that of 16 in-grid "
            "V1 queries.",
            "Scope and limits.  V1-edge is a separate registered arm (10_SPEC_stageC.md §6j :702, :719: grid-related changes are "
            "separate registrations; "
            "NEXT_EXPERIMENTS_K1K2.md:4, :65).  The headline checkpoint is unchanged (ckpt/d2sx_N160000_a1.pt, sha256[:16] "
            "4443921ce8d5c4a1, last-EMA; NEXT_EXPERIMENTS_K1K2.md:64) and V1's own definition -- extrapolate above the grid, never "
            "clamp (DECISIONS.md:22) -- is unchanged: every other V1 number in the record is still that V1.  The cell choice is post "
            "hoc (after the C1/C5 low-SNR collapse was seen), hence fresh development trials 3200..4479 and pre-written branches "
            "(NEXT_EXPERIMENTS_K1K2.md:65).  The REGISTERED verdicts of cells C1 AND C5 are UNCHANGED (NEXT_EXPERIMENTS_K1K2.md:4): "
            "table B at N_train = 3.2e5, b* -> V1: C1 GMM better at 3/3 decision points, +6/+9/+15 dB (tables_D2_B32e4x.txt:591-596, "
            "cell C1 header :506); C5 not significant, GMM better at 1/3 and V1 at 1/3, +6/+12/+15 dB (tables_D2_B32e4x.txt:731-735, "
            "cell C5 header :646).  V1-edge "
            "was measured only at C1 -3 dB (and the report points C1 0 dB, C5 -6 dB; apart from these, only the registered "
            f"{c2n}-trial C2 -3 dB pre-check on development trials 2560..2599 (raw_review_next_K2pre_c2), where V1-edge and "
            "V1-clamp are bit-identical to V1 with n_oog 0: NEXT_EXPERIMENTS_K1K2.md:118, re-checked above), not at the decision points of C1 "
            "or C5, and only at the equal budget N_train = 1.6e5; nothing here extends to other SNRs, cells or budgets.  The "
            "headline (C2, 1.6e5) is unchanged (NEXT_EXPERIMENTS_K1K2.md:162); on those 40 C2 pre-check trials the rule does not "
            "engage (no above-grid query, as the registration expects for C2: NEXT_EXPERIMENTS_K1K2.md:67).  Observed before on the test trials 0..2559 (failures re-counted here from "
            "raw): the frozen V1 (this run is bit-identical to raw_B16e4 C1 -3 dB: audit §5.3, NEXT_EXPERIMENTS_K1K2.md:187, "
            "re-checked above) and R5 (bit-identical likewise); b* and the scalar-site b* at older fits (raw_B1e4x and raw_C, "
            f"N_train = 1e4: {ob['raw_B1e4x']['M-ours-bstar']} / {ob['raw_B1e4x']['M-ours-bstar-scalar']}; raw_B16e4, 1.6e5, "
            f"K <= 512: {ob['raw_B16e4']['M-ours-bstar']} / {ob['raw_B16e4']['M-ours-bstar-scalar']}; raw_B32e4x, 3.2e5: "
            f"{ob['raw_B32e4x']['M-ours-bstar']} (BLER {R(ob['raw_B32e4x']['M-ours-bstar'] / n):.3f}) / "
            f"{ob['raw_B32e4x']['M-ours-bstar-scalar']}); earlier V1 runs (raw_C {ob['raw_C']['M-ours-dscore-C-V1']}, raw_B1e4x "
            f"{ob['raw_B1e4x']['M-ours-dscore-C-V1']}, the 3.2e5 V1 in raw_B32e4x {ob['raw_B32e4x']['M-ours-dscore-C-V1']} = "
            f"{R(ob['raw_B32e4x']['M-ours-dscore-C-V1'] / n):.3f}).  New there: the K=1024 runs of b* ({sT[B]['k']}), the "
            f"scalar-site b* ({sT['M-ours-bstar-scalar']['k']}) and b* in V1's wiring ({sT['gmmB-scorew-eta']['k']}; no earlier "
            "run of this arm on these trials), V1-edge and V1-clamp (NEXT_EXPERIMENTS_K1K2.md:17, :21, :97).  An above-grid "
            "scalar query is not by itself sufficient for collapse (DECISIONS.md:96: the Tp < Nt null directions decide); this "
            "figure shows only that, at this point, the rule removes the frozen V1's runaway.  Error bars: 95% Wilson; a raised "
            "block is a block error (01_RULES §4).  Colours: GMM b* orange diamonds, its variants orange (scalar site: "
            "down-triangles; V1's wiring: plus signs); frozen V1 (learned diffusion prior) blue squares; V1-edge aqua circles, "
            "V1-clamp aqua triangles (dashed with open triangles in panel b); known-channel reference (R5) ink stars (dash-dot in "
            "panel b); in (a) filled = test, hollow = development, in (c) all hollow; every aqua series carries a legend entry and a "
            "tick or direct label; all annotation text in ink.  The manuscript table (T_K2) carries V1-edge with V1-clamp next to it and the "
            "registered cost columns (network forwards, seconds per above-grid query; NEXT_EXPERIMENTS_K1K2.md:83), set as a "
            "sub-table under the arm table; replacing edge by clamp would be a user decision and is not made here."]
    print("\n".join(txt))                              # paper version: printed only, no .txt file


if __name__ == "__main__":
    main()
