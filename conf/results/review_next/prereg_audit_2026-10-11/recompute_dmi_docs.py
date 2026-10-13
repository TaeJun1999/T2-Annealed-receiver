"""recompute_dmi_docs.py -- RECORD AUDIT of NEXT_EXPERIMENTS_ROOM16e4.md §7 (prior DMI): text-level checks.
 (A) the three markdown tables of §7 (7.2 BLER table, 7.3 baseline table, 7.4 11-curve table) are PARSED from the record text and
     compared with the expected-value blocks that recompute_dmi_main.py / recompute_dmi_base.py verified against the raw files
     (guards against a retyping slip of the auditor: record text == retyped values == raw);
 (B) table-A SNR@0.1 and the table-B SNR@0.1 gaps with their paired-bootstrap CIs, as printed in results/tables_D2_DMIB16e4{,last}.txt,
     vs the strings of 7.1 / 7.2;
 (C) guard files vs the 7.2 rates;  (D) pair_PILDMI.txt / pair_ALDDMI.txt lines vs 7.5;  (E) GB' npz vs 7.2;
 (F) the two EXPERIMENTS.md rows vs §7 and the files;  (G) internal consistency of §7 and wording checks.

usage (cwd = ~/t2/conf):  CUDA_VISIBLE_DEVICES= ~/miniforge3/envs/torch/bin/python -B results/review_next/prereg_audit_2026-10-11/recompute_dmi_docs.py
"""
import os
import re
import sys

import numpy as np

CONF = "/home/HTJ/t2/conf"
HERE = os.path.join(CONF, "results/review_next/prereg_audit_2026-10-11")
sys.path.insert(0, HERE)
import recompute_dmi_base as B  # noqa: E402  (expected-value blocks only; nothing is executed)
import recompute_dmi_main as M  # noqa: E402

NC = [0, 0]


def chk(label, got, exp):
    NC[0] += 1
    if got != exp:
        NC[1] += 1
        print(f"    DIFF  {label}: found {got!r}  expected {exp!r}")


def main():
    rec = open(os.path.join(CONF, "results/review_next/NEXT_EXPERIMENTS_ROOM16e4.md")).read()
    s7 = rec[rec.index("## 7. 결과 — DMI"):]
    s71, s72, s73, s74, s75, s76, s77 = (s7[s7.index(f"### 7.{i}"):s7.index(f"### 7.{i + 1}")] if i < 7 else s7[s7.index("### 7.7"):] for i in range(1, 8))
    print("# recompute_dmi_docs.py -- text-level checks of §7 (prior DMI)")

    print("\n## A. markdown tables parsed from the record vs the raw-verified expected blocks")
    name72 = {"**V1**": M.V1, "V1 (last 태그)": "V1last", "V4": M.V4, "V4b": M.V4B, "**b\\***": M.BS, "b\\*-scalar": M.SC, "gmm32": "M-ours-gmm32", "R2-ours-G": M.R2, "R1-turbo": "R1-turbo",
              "R0-pilot (@1)": "R0-pilot@1", "pilot_C (@16; 문맥)": "R0-pilot", "R4-scvamp": "R4-scvamp", "R3-bigamp": "R3-bigamp", "R4-llr": "R4-llr", "V0": M.V0, "**genie**": M.GEN}
    rows = [l for l in s72.split("\n") if l.startswith("| ") and "(" in l and "dB" not in l.split("|")[1]]
    chk("7.2 table: 16 rows", len(rows), 16)
    for l in rows:
        c = [x.strip() for x in l.strip("|").split("|")]
        arm = name72[c[0]]
        cnt = [int(re.search(r"\((\d+)\)", x)[1]) for x in c[1:8]]
        bl = " ".join(re.match(r"([\d.]+)", x)[1] for x in c[1:8])
        chk(f"7.2 row {c[0]} counts", cnt, M.EXP_FAILS[arm][0]); chk(f"7.2 row {c[0]} BLER strings", bl, M.EXP_FAILS[arm][1])
        chk(f"7.2 row {c[0]} BLER = count/2560 (3 dp)", bl, " ".join(f"{x / 2560:.3f}" for x in cnt))
    name74 = {"Proposed (V1)": B.V1, "Annealed Langevin (plug-in) = ALD-pilot": "ALD-pilot", "GMM prior = b\\*": B.BS, "Gaussian prior = R2-ours-G": "R2-ours-G", "Turbo LMMSE = R1-turbo": "R1-turbo",
              "BiG-AMP = R3-bigamp": "R3-bigamp", "Pilot-only LMMSE = R0-pilot@1": B.R0A, "SBL (in loop)": "SBL-loop", "SBL (pilot-only)": "SBL-pilot", "OMP (pilot-only)": "OMP-pilot", "Perfect CSI = genie": B.GEN}
    rows = [l for l in s74.split("\n") if l.startswith("| ") and not l.startswith("| 곡선") and not l.startswith("|---")]
    chk("7.4 table: 11 rows", len(rows), 11)
    for l in rows:
        c = [x.strip() for x in l.strip("|").split("|")]
        chk(f"7.4 row {c[0]}", [int(x) for x in c[1:8]], B.EXP_FAILS[name74[c[0]]])
    other = re.search(r"11 곡선에 없는 등록 arm \(같은 순서\): (.*)\n", s74)[1]
    for seg in other.rstrip(".").split(";"):
        nm, vals = seg.strip().rsplit(" ", 13)[0], [int(x) for x in re.findall(r"\d+", seg.strip().split(" ", 1)[1])]
        nm = seg.strip().split(" ")[0]
        chk(f"7.4 other arm {nm}", [int(x) for x in seg.strip()[len(nm):].split("/")], B.EXP_FAILS[nm])
    name73 = {"b\\* (주 라벨, 7.1)": B.BS, "b\\*-scalar": "M-ours-bstar-scalar", "gmm32": "M-ours-gmm32", "R0-pilot@1": B.R0A}
    rows = [l for l in s73.split("\n") if l.startswith("| ") and "POWERED" in l]
    chk("7.3 table: 16 rows", len(rows), 16)
    for l in rows:
        c = [x.strip() for x in l.strip("|").split("|")]
        x = name73.get(c[0], c[0])
        e = B.EXP_B[x]
        dp = [int(v) for v in c[1].replace("+", "").split("/")]
        ab = [tuple(int(v) for v in t.split(":")) for t in c[2].split("·")]
        pool = tuple(int(v) for v in re.match(r"(\d+):(\d+)", c[3]).groups()); pp = re.search(r"\(([^)]*)\)", c[3])[1]
        k = tuple(int(v) for v in re.search(r"V1 (\d)/3 · X (\d)/3", c[4]).groups())
        lab = c[5].strip("*")
        r3 = ("undef", float(re.search(r"범위 밖: ([\d.]+)", c[7])[1])) if "정의 안 됨" in c[7] else tuple(float(v) for v in re.findall(r"-?[\d.]+", c[7]))
        rd = "undef" if "정의 안 됨" in c[8] else tuple(float(v) for v in re.findall(r"-?[\d.]+", c[8]))
        chk(f"7.3 row {c[0]}", (dp, ab, pool, pp, k, lab, int(c[6]), r3, rd), e)
        chk(f"7.3 row {c[0]} 'POWERED'", c[4].startswith("POWERED"), True)

    print("\n## B. tables_D2_DMIB16e4{,last}.txt: table A SNR@0.1 and table-B gaps (text) vs 7.1 / 7.2")
    tb, tl = (open(os.path.join(CONF, f"results/tables_D2_{t}.txt")).read() for t in ("DMIB16e4", "DMIB16e4last"))

    def gap(t, x, y):
        m = re.search(rf"\n  {re.escape(x)} -> {re.escape(y)}\s+\[decision-point anchor arm[^\n]*\n\s+decision SNRs (\[[^\]]*\])[^\n]*\n\s+sign test @16: ([^\n]*)\n\s+power guard: ([^\n]*)\n\s+(?:two-sided sign test[^\n]*: |UNDECIDED -- )([^\n]*)\n\s+SNR@0\.1 gap \([^)]*\): ([+-][\d.]+) dB\s+\[90% paired bootstrap ([+-][\d.]+), ([+-][\d.]+)", t)
        return m.groups() if m else None
    exp = {("best", M.BS, M.V1): ("+0.23", "+0.08", "+0.37"), ("last", M.BS, M.V1): ("+0.24", "+0.11", "+0.39"), ("best", M.BS, M.SC): ("-0.21", "-0.31", "-0.12"),
           ("best", M.R2, M.BS): ("+3.13", "+2.89", "+3.38"), ("best", M.V1, M.GEN): ("+1.73", "+1.56", "+1.90"), ("best", M.BS, M.GEN): ("+1.95", "+1.76", "+2.14"),
           ("best", M.BS, M.V4): ("+0.02", "-0.13", "+0.17"), ("best", M.BS, M.V4B): ("-0.05", "-0.20", "+0.10")}
    for (tag, x, y), e in exp.items():
        g = gap(tb if tag == "best" else tl, x, y)
        chk(f"table B gap {tag} {x} -> {y} (value, CI lo, CI hi)", g[4:7] if g else None, e)
        eab, epool = M.EXP_PAIRS[(tag, x, y)][:2]
        st = "  ".join(f"{s:+d} dB {a}:{b}" for s, (a, b) in zip(([-3, 0, 3] if y != M.GEN else [-3, 0]), eab))
        chk(f"table B sign-test line {tag} {x} -> {y} holds the record's a:b and pooled", all(f"{a}:{b} p=" in g[1] for a, b in eab) and f"pooled {epool[0]}:{epool[1]} p=" in g[1], True)
    g = gap(tb, M.BS, M.V1)
    chk("table B b*->V1 best: decision SNRs / power guard / verdict line", (g[0], "POWERED" in g[2], g[3]), ("['-3', '+0', '+3']", True, "second arm fewer failures at 2/3 points, first arm fewer failures at 0/3 points -> significant"))
    chk("table B b*->V1 best: p strings", re.findall(r"p=([\d.e-]+)", g[1]), ["0.0015", "0.035", "0.52", "7.5e-05"])
    g = gap(tl, M.BS, M.V1)
    chk("table B b*->V1 last: p strings", re.findall(r"p=([\d.e-]+)", g[1]), ["6e-05", "0.03", "0.4", "2.4e-06"])
    g = gap(tb, M.BS, M.SC)
    chk("table B control: verdict", g[3].startswith("second arm fewer failures at 0/3 points, first arm fewer failures at 2/3 points"), True)
    for x, y in ((M.V1, M.GEN), (M.BS, M.GEN)):
        g = gap(tb, x, y)
        chk(f"table B {x} -> genie: decision SNRs -3 / +0 only and UNDECIDED", (g[0], "-> UNDECIDED" in g[2]), ("['-3', '+0']", True))
    ta = {m[0].strip(): m[1].replace(" ", "") for m in re.findall(r"\n    ((?:R\d|M-ours|pilot_C)[^\n]*?)\s{2,}(>\s*15|-?[\d.]+)   ", tb[tb.index("    arm                  SNR@0.1"):tb.index("failure classes at @16")])}
    exp_a = {"R5-genie": "-2.67", "M-ours-dscore-C-V1": "-0.95", "M-ours-dscore-C-V4": "-0.74", "M-ours-bstar": "-0.72", "M-ours-dscore-C-V4b": "-0.67", "M-ours-bstar-scalar": "-0.51", "M-ours-gmm32": "0.37",
             "R2-ours-G": "2.41", "pilot_C (@16)": "3.04", "R1-turbo": "3.98", "R4-scvamp": "5.93", "R0-pilot (@1)": "6.38", "R4-llr": "12.74", "R3-bigamp": ">15", "M-ours-dscore-C-V0": ">15"}
    chk("table A SNR@0.1 (15 arms) == the 7.2 bullet", ta, exp_a)
    bullet = re.search(r"\*\*SNR@0\.1\*\* \(표 A; dB\): ([^\n]*)", s72)[1]
    for nm, v in (("genie", "−2.67"), ("V1", "−0.95"), ("V4", "−0.74"), ("b\\*", "−0.72"), ("V4b", "−0.67"), ("b\\*-scalar", "−0.51"), ("gmm32", "0.37"), ("R2-ours-G", "2.41"), ("pilot_C (@16)", "3.04"), ("R1-turbo", "3.98"),
                  ("R4-scvamp", "5.93"), ("R0-pilot (@1)", "6.38"), ("R4-llr", "12.74")):
        chk(f"7.2 SNR@0.1 bullet holds '{nm} {v}'", f"{nm} {v}" in bullet, True)

    print("\n## C. guard files vs 7.2")
    for tag, e in (("DMIB16e4", M.EXP_GUARD_V0_RATE["best"]), ("DMIB16e4last", M.EXP_GUARD_V0_RATE["last"])):
        t = open(os.path.join(CONF, f"results/guard_D2_{tag}.txt")).read()
        r = [float(x) for x in re.findall(r"^C2\s+[+-]\d+ M-ours-dscore-C-V0\s+\d+\s+2560\s+([\d.]+)", t, re.M)]
        chk(f"guard {tag}: V0 rates", r, e)
        chk(f"guard {tag}: only V0 rows fire; 12 arms never fired", (len(re.findall(r"^C2\s+[+-]\d+ (?!M-ours-dscore-C-V0)", t, re.M)),
            "arms that NEVER fired the guard anywhere in this raw set (12): M-ours-bstar, M-ours-bstar-scalar, M-ours-dscore-C-V1, M-ours-dscore-C-V4, M-ours-dscore-C-V4b, M-ours-gmm32, R0-pilot, R1-turbo, R2-ours-G, R3-bigamp, R4-llr, R4-scvamp" in t), (0, True))
    chk("7.2 F3 strings", ("1.000 / 1.000 / 0.999 / 0.996 / 0.963 / 0.820 / 0.509" in s72, "1.000 / 1.000 / 1.000 / 0.990 / 0.958 / 0.782 / 0.552" in s72), (True, True))

    print("\n## D. pair_PILDMI.txt / pair_ALDDMI.txt vs 7.5")
    tp, ta_ = (open(os.path.join(CONF, f"results/review_next/pair_{t}.txt")).read() for t in ("PILDMI", "ALDDMI"))
    for t, head, ab, pool, verdict in (
            (tp, "P1:", "410:46 p=4.3e-74  +0 dB 130:26 p=7.8e-18  +3 dB 15:4", "pooled 555:76", "second arm fewer at 3/3, first arm fewer at 0/3  -> (i)"),
            (tp, "P2:", "142:123 p=0.27  +0 dB 81:65 p=0.21  +3 dB 11:12 p=1", "pooled 234:200 p=0.11", "second arm fewer at 0/3, first arm fewer at 0/3  -> (iii)"),
            (tp, "report: pilot-only b* -> loop b*", "366:39 p=9.8e-68  +0 dB 118:22 p=4.5e-17  +3 dB 13:7", "pooled 497:68", "second arm fewer at 2/3, first arm fewer at 0/3  -> (i)"),
            (tp, "report: pilot-only V1 -> loop b*", "376:68 p=1e-52  +0 dB 128:48 p=1.4e-09  +3 dB 19:12", "pooled 523:128", "second arm fewer at 2/3, first arm fewer at 0/3  -> (i)"),
            (ta_, "A1:", "587:59 p=2.3e-110  +0 dB 209:29 p=8.4e-35  +3 dB 34:5", "pooled 830:93", "second arm fewer at 3/3, first arm fewer at 0/3  -> (i)"),
            (ta_, "A2:", "608:62 p=1.3e-113  +0 dB 239:28 p=6.3e-43  +3 dB 47:4", "pooled 894:94", "second arm fewer at 3/3, first arm fewer at 0/3  -> (i)"),
            (ta_, "A3:", "289:125 p=4.7e-16  +0 dB 126:50 p=9.3e-09  +3 dB 28:10", "pooled 443:185", "second arm fewer at 3/3, first arm fewer at 0/3  -> (i)"),
            (ta_, "report: ALD pilot-only -> loop b*", "547:75 p=1.8e-89  +0 dB 207:51 p=1.8e-23  +3 dB 36:11", "pooled 790:137", "second arm fewer at 3/3, first arm fewer at 0/3  -> (i)"),
            (ta_, "report: pilot-only b* -> ALD pilot-only", "146:291 p=3.6e-12  +0 dB 86:146 p=9.9e-05  +3 dB 16:35", "pooled 248:472", "second arm fewer at 0/3, first arm fewer at 3/3  -> (ii)"),
            (ta_, "report: plug-in -> error-aware", "66:48 p=0.11  +0 dB 56:25 p=0.00075  +3 dB 18:4", "pooled 140:77", "second arm fewer at 2/3, first arm fewer at 0/3  -> (i)")):
        blk = t[t.index(head):].split("\n")[:3]
        chk(f"pair file block '{head}'", (ab in blk[1], pool in blk[1], verdict in blk[2]), (True, True, True))
    chk("pair_ALDDMI.txt test ALD NMSE line == 7.5", "-3:-8.10dB +0:-11.70dB +3:-14.64dB +6:-17.40dB +9:-19.90dB +12:-22.20dB +15:-24.40dB" in ta_, True)
    chk("7.5 holds the ten a:b strings", all(s in s75 for s in ("410:46 · 130:26 · 15:4, pooled 555:76", "142:123 (0.27) · 81:65 (0.21) · 11:12 (1), pooled 234:200 (p 0.11)", "366:39 · 118:22 · 13:7, pooled 497:68", "376:68 · 128:48 · 19:12, pooled 523:128",
                                                                 "587:59 · 209:29 · 34:5", "608:62 · 239:28 · 47:4", "289:125 · 126:50 · 28:10, pooled 443:185", "547:75 · 207:51 · 36:11, pooled 790:137", "146:291 · 86:146 · 16:35, pooled 248:472",
                                                                 "66:48 (0.11) · 56:25 · 18:4, pooled 140:77", "−8.10 / −11.70 / −14.64 / −17.40 / −19.90 / −22.20 / −24.40 dB")), True)

    print("\n## E. GB' npz vs 7.2")
    gz = np.load(os.path.join(CONF, "results/d2_gbprime_DMI_N160000_a1.npz"))
    ratio = gz["nmse_model"] / gz["nmse_gmm"]
    print("  ratio per level:", np.round(ratio, 4))
    chk("GB' 20 levels; 19 with ratio < 1; the only one >= 1 is the largest sigma", (len(ratio), int((ratio < 1).sum()), int(np.argmax(ratio))), (20, 19, 19))
    chk("GB' median / min / max (4 dp)", (round(float(np.median(ratio)), 4), round(float(ratio.min()), 4), round(float(ratio.max()), 4)), (0.8038, 0.7272, 1.0217))
    chk("GB' at the largest level: sigma 0.848, ratio 1.022, model NMSE 0.2233, GMM 0.2186", (round(float(gz["sigma"][-1]), 3), round(float(ratio[-1]), 3), round(float(gz["nmse_model"][-1]), 4), round(float(gz["nmse_gmm"][-1]), 4)), (0.848, 1.022, 0.2233, 0.2186))
    chk("7.2 GB' strings", all(s in s72 for s in ("median **0.8038** (min 0.7272 · max 1.0217", "19 개에서 비 < 1", "σ 0.848 (격자 끝)에서 1.022 (모델 NMSE 0.2233 대 GMM 0.2186)", "16:24:17 CDT > full 1024 적합 파일 mtime 16:11:10 CDT")), True)

    print("\n## F. docs/EXPERIMENTS.md: the two DMI rows")
    ex = open("/home/HTJ/t2/docs/EXPERIMENTS.md").read().rstrip("\n").split("\n")
    r1, r2 = ex[-2], ex[-1]
    chk("the last two rows are the DMI main-run row and the run_dmi_base.sh row", ("run_prior_eval.sh DMI DMIB16e4" in r1, "run_dmi_base.sh d2sx_DMI_N160000_a1" in r2), (True, True))
    need1 = ["2026-10-13 06:15 ~ 07:54 KST (텍사스 10-12 16:15 ~ 17:54 CDT; CPU 96 스레드)", "gmm1024 - 112.04253042212595 dc784649f1e9b890 20d28bf06e317ca5", "taskset -c 24-47,120-143,72-95,168-191", "동결 b737fd55; 5-DMI = 실행 커밋 4131a3b0",
             "PID 14", "70,801 위치 × yaw 5 회", "학습 273,305 / 검증 20,000 / 테스트 60,700", "dec5e7a1ea1e4605", "erank(Rt) 3.839", "| 4131a3b0 |", "학습 (10-11 11:03 ~ 12:44 CDT)", "GMM 격자 21 작업 (10-12 14:01 ~ 14:35 CDT)",
             "full 1024 추가 적합 (15:46 ~ 16:11 CDT)", "ALD 개발 조정 (15:46 ~ 15:55 CDT)", "GB′ (16:16 ~ 16:24 CDT)", "178:122 · 72:48 · 13:9 pooled 263:179 (p 7.5e-05) POWERED 2/3", "+0.23 dB [+0.08, +0.37]",
             "genie −2.67, V1 −0.95, b\\* −0.72, R2 +2.41 dB", "genie 0.125 / 0.016 / 0.002, V1 0.324 / 0.058 / 0.007, b\\* 0.346 / 0.068 / 0.009, R2 0.752 / 0.327 / 0.075", "R(−3 dB) 0.099 [0.050, 0.146]",
             "ΔR(−3 dB) −0.371 [−0.439, −0.308]", "b\\*→b\\*-scalar (ii)", "pooled 71:55 (p 0.181)", "last 태그 pooled 272:172, 격차 +0.24 dB", "+6.192 nat", "이웃 0.058", "1162 epoch patience 정지 (best @1142)",
             "GB′ median 0.8038 (20 잡음 수준 중 19 에서 < 1; 격자 끝 σ 0.848 에서 1.022)", "10 (b\\* 계열) · 12 (대조군) 빗나감", "태그당 46.6 · 49.9 분"]
    for s in need1:
        chk(f"EXPERIMENTS row 1 holds '{s[:60]}'", s in r1, True)
    need2 = ["2026-10-13 07:56 ~ 08:15 KST (텍사스 10-12 17:56 ~ 18:15 CDT; 한 번 시작; CPU 96 스레드)", "run_dmi_base.sh d2sx_DMI_N160000_a1 dc784649f1e9b890 8f72c113efb91b0b 1e7824c1bae10376 gmm1024 - 112.04253042212595",
             "ALD 시행 2560..3071", "| 29cf411d (세 raw 모두; `conf/code` 는 4131a3b0 와 동일) |", "ALD 추정만 GPU 0 (17:59 CDT)", "X\\* = M-ours-bstar (F 885), R_X\\* 0.099 [0.050, 0.146]",
             "V1 829 / 19, ALD-pilot 1375 / 62, b\\* 885 / 23, R2 1924 / 191, R1 2245 / 424, BiG-AMP 2402 / 928, R0@1 2521 / 922, SBL-loop 1740 / 128, SBL-pilot 2009 / 180, OMP-pilot 2131 / 315, genie 321 / 4",
             "V1 +6 / +9 / +12 / +15 dB = 4 / 0 / 0 / 0 건", "b\\* · b\\*-scalar · bstar-pilot", "SBL ρ 16 · OMP ρ 16", "ALD c 0.01 · β 0.005", "0 실패 점 18 개"]
    for s in need2:
        chk(f"EXPERIMENTS row 2 holds '{s[:60]}'", s in r2, True)
    f = B.EXP_FAILS
    chk("EXPERIMENTS row 2 failure pairs (-3 / +3 dB) == raw-verified counts", [(f[a][0], f[a][2]) for a in (B.V1, "ALD-pilot", B.BS, "R2-ours-G", "R1-turbo", "R3-bigamp", B.R0A, "SBL-loop", "SBL-pilot", "OMP-pilot", B.GEN)],
        [(829, 19), (1375, 62), (885, 23), (1924, 191), (2245, 424), (2402, 928), (2521, 922), (1740, 128), (2009, 180), (2131, 315), (321, 4)])
    print("  EXPERIMENTS row 1 wording on b*: " + re.search(r"\*\*b\\\* = full 공분산 K 1024[^)]*\)", r1)[0])

    print("\n## G. internal consistency / wording of §7")
    chk("7.1 counts in the recovery sentence == 7.2 table (b* 885 / V1 829 / genie 321; 1081 / 997 / 365)", ("(b\\* 885 / V1 829 / genie 321)" in s71, "(b\\* 1081 / V1 997 / genie 365)" in s71,
        sum(M.EXP_FAILS[M.BS][0][:3]), sum(M.EXP_FAILS[M.V1][0][:3]), sum(M.EXP_FAILS[M.GEN][0][:3])), (True, True, 1081, 997, 365))
    chk("7.1 label string == the §2 name + (i) sentence", '"DeepMIMO 실내 (`i1_2p4` 2.4 GHz, 고정 기지국 한 곳, block split) 에서 V1 이 b\\* 보다 적게 실패 (prior·기전 축 측정, UNGATED)"' in s71, True)
    chk("7.1 attaches caveats (1), (2), (4) and the scope sentence; the grid-edge caveat is in 7.1 itself", all(s in s71 for s in ("**(1) 유한 풀·한 장소**", "**(2) 가까운 이웃**", "**(4) 선택 편향**", "범위: 이 방·이 기지국·이 split·이 크기 한정", "**격자 끝 캐비엇**", "+6.192 nat")), True)
    chk("7.3 sentences carry (6) and the scope sentence", ("§1 고유 사항 (6)" in s73, "범위: 이 방·이 기지국·이 split·이 크기 한정" in s73), (True, True))
    chk("7.3 '전부' / '멀어진다' strings use the §2 name", s73.count("DeepMIMO 실내 (`i1_2p4` 2.4 GHz, 고정 기지국 한 곳, block split) 에서 V1 이 등록된 baseline 전부(16 개, 희소 baseline 포함)보다 적게 실패 (UNGATED 측정)"), 1)
    chk("7.6 scoring strings", [s in s76 for s in ("1. 표 B (i) → 결과 (i) → **적중**", "2. 판정점 −3 / 0 / +3 dB 이고 POWERED (DMI 확신 낮음) → **적중**", "8. GB′ median ≤ 0.90 → **적중** (0.8038)", "9. 학습(patience · epoch ∈ [300, 1500]) → **적중**",
                                                    "10. b\\* = kron 계열, K ≥ 1024 → **빗나감**", "12. 대조군 `b* → b*-scalar` (iii) → **빗나감**")], [True] * 6)
    zero_pts = sum(1 for a in B.FIG_SHOW for x in B.EXP_FAILS[a] if x == 0)
    chk("7.4 '0 실패 점 18 개' == zeros in the 11-curve table", zero_pts, 18)
    chk("7.7 '태그당 46.6 · 49.9 분; SRB 는 28.3 · 24.8 분' present", "태그당 46.6 · 49.9 분; SRB 는 28.3 · 24.8 분" in s77, True)
    print("  7.2 leak-strata threads wording: " + re.search(r"10-12 17:57 CDT 실행\(([^;]*);", s72)[1] + "   |   7.7: " + re.search(r"보고 전용 층화 둘[^\n]*", s77)[0][:90])
    print("  7.3 baseline-input files tracked in 29cf411d (as listed): " + re.search(r"baseline 입력\(([^)]*)\)", s73)[1][:160] + "   |   7.7: " + re.search(r"baseline 입력 파일 [^\n]*", s77)[0][:60])
    print(f"\n## SUMMARY: {NC[0]} values checked, {NC[1]} differ")


if __name__ == "__main__":
    main()
