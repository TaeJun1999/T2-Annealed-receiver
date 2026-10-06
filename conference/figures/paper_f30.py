"""conference/figures/paper_f30.py -- paper version of conf/code/figure_f30.py (git 3f7c09ab), F30: the antenna-array
scaling axis.

Same data, computation, asserts, error bars, colours and markers as the original; only the rendered text differs:
  - axis / legend / tick labels use the paper glossary (conference/figures/TERMS.md), no project-internal names
    (x ticks "8 (C2)" -> "8"; y label of (a)/(b) = fraction of the GMM-to-perfect-CSI gap closed);
  - plot titles removed, only the bold panel labels (a)-(d) remain (datasets, CI levels go to the caption):
    (a) Sparse specular   (b) 3GPP UMi 28 GHz   (c) Sparse specular, 32x4   (d) 3GPP UMi 28 GHz, 32x4;
  - the registered-label annotations of (a)/(b) (primary Delta R / Holm / (T+) / robustness tags, the S1/S2 step labels,
    "monotone increase") are not drawn; the per-point values above the markers stay;
  - zero-failure points: the curve breaks there instead of joining its neighbours, and Perfect CSI's zero points
    are drawn as a short downward arrow from the 95% Wilson upper bound (the F17 convention; 0/2560 -> 1.5e-3);
    the record text keeps listing them as 'not drawn' (no plotted estimate);
  - reads conf/ and ~/t2_wtS/conf raws (read-only) as the original does and writes only F30_scale_trend.{pdf,png} next to
    this script (no .txt; the record text is printed to stdout unchanged, so it can be diffed against
    conf/figs/F30_scale_trend.txt).
The original docstring follows.

conf/code/figure_f30.py -- F30: the antenna-array scaling axis (SCALE16e4; report figure, read-only).

(a) D2, (b) UMi28: genie-gap recovery over the decision points R_dp = (SigmaF_b* - SigmaF_V1)/(SigmaF_b* - SigmaF_g) against
    Nr = 8 / 16 / 32 (cells C2 / C6 / C9: Nt 4, T 16, Tp 4, equal budget N' = 1.6e5), 90% paired bootstrap per cell.
    Recomputed from raw with frontier_ci.cmd_recovery -- the function and specs run_scale2.sh ran (B 2000, seed 20260926; the
    --extrap / --rstar options of the run draw nothing from the R lines' stream, so they are left out) -- and asserted against
    NEXT_EXPERIMENTS_SCALE16e4 §6.1.1 / §6.1.2 (counts, R, CIs, Delta R, p, decision points).  Each cell's CI is the one of the
    run that registers it: C2 and C9 = the primary runs, D2 C6 = step D2 S2 (R2), UMi28 C6 = step UMi28 S1 (R1).
    Annotations = the registered primary label (Delta R = R_C9 - R_C2 at its Holm level, with its qualifiers) and the step
    labels, as recorded; the figure carries English glosses (no Hangul font here), the verbatim Korean strings are in the .txt.
(c) D2 C9, (d) UMi28 C9 (32x4): BLER@16 of b*, V1, the Gaussian prior R2 and genie, 95% Wilson; counts asserted against §6.1.4 (b)
    (genie / V1 / b*) and the record file pairB_<T>.txt (R2).
Raws (read-only): the SCALE raws live in the scale worktree ~/t2_wtS/conf/raw_* (untracked), the reuse raws in conf/raw_*;
raw() takes conf/ first.  Writes figs/F30_scale_trend.{pdf,png,txt}.
"""
import contextlib
import io
import os
import sys

CONF = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "conf"))
sys.dont_write_bytecode = True                                 # conf/code is frozen: no __pycache__ writes there
sys.path.insert(0, os.path.join(CONF, "code"))
import common as C
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({"pdf.fonttype": 42, "ps.fonttype": 42})   # TrueType fonts in PDF (IEEE PDF eXpress rejects Type 3)
from analysis import decision_points, wilson
import frontier_ci as F
from figstyle import INK, INK2, V1, GMM, GENIE, GAUSS

plt.rcParams.update({"font.size": 8, "axes.labelsize": 8.5, "axes.titlesize": 8.5, "legend.fontsize": 7.5,
                     "xtick.labelsize": 7.5, "ytick.labelsize": 7.5, "axes.grid": True, "grid.alpha": 0.25,
                     "figure.dpi": 200, "savefig.bbox": "tight", "savefig.pad_inches": 0.02,
                     "text.color": INK, "axes.labelcolor": INK, "axes.titlecolor": INK,
                     "xtick.labelcolor": INK, "ytick.labelcolor": INK})
FIG = os.path.dirname(os.path.abspath(__file__))              # paper version: figures only, next to this script
RV = os.path.join(C.CONF, "results", "review_next")
WTS = os.path.join(os.path.expanduser("~"), "t2_wtS", "conf")
BS, V1A, GE, R2 = "M-ours-bstar", "M-ours-dscore-C-V1", "R5-genie", "R2-ours-G"


def zero_arrows(ax, xs, n, color):
    """Zero-failure points (0/n blocks) cannot sit on a log axis: draw a short cap at the 95% Wilson upper bound
    z^2/(n+z^2) and a downward arrow (the F17 convention), never a made-up value; the curve itself breaks there."""
    hi = 1.96 ** 2 / (n + 1.96 ** 2)
    for s in xs:
        ax.plot([s - 0.3, s + 0.3], [hi, hi], color=color, lw=1.0, zorder=6)
        ax.annotate("", xy=(s, hi / 1.7), xytext=(s, hi), zorder=6,
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=0.9, mutation_scale=6.5, shrinkA=0, shrinkB=0))


def raw(tag):
    """conf/raw_<tag> if present, else the scale worktree's (SCALE16e4 raws are untracked there)."""
    for r in (C.CONF, WTS):
        p = os.path.join(r, f"raw_{tag}")
        if os.path.isdir(p):
            return p
    raise FileNotFoundError(f"raw_{tag} in neither {C.CONF} nor {WTS}")


def rec_fails(path):
    """a record file's 'BLER@16 failures / n per SNR' block -> {arm: [failures per SNR]} (transcribed, for the asserts)."""
    out, on = {}, False
    for line in open(path, encoding="utf-8"):
        if line.startswith("BLER@16 failures"):
            on = True
        elif on:
            if not line.startswith("    "):
                break
            p = line.split()
            out[p[0]] = [int(x) for x in p[1:]]
    return out


f3 = lambda x: f"{x:.3f}"
s3 = lambda x: f"{x:+.3f}"
# (dataset, Nr) -> raw tag, cell, prior, decision SNRs (§6.1, anchor b*), (SigmaF b*, V1, genie), R [90%] as registered, source
CELLS = {("D2", 8): ("B16e4k", "C2", "S2", (-3, 0, 3), (864, 488, 125), ("0.509", "0.470", "0.544"), "primary_D2_L90:4"),
         ("D2", 16): ("NR16B16e4", "C6", "S2", (-3, 0, 3), (277, 82, 40), ("0.823", "0.774", "0.874"), "step_D2_S2:4"),
         ("D2", 32): ("NR32B16e4", "C9", "S2", (-9, -6, -3), (1161, 276, 70), ("0.811", "0.790", "0.832"), "primary_D2_L90:3"),
         ("UMi28", 8): ("U28B16e4", "C2", "UMi28", (3, 6, 9), (800, 712, 215), ("0.150", "0.108", "0.190"), "primary_U28_L90:4"),
         ("UMi28", 16): ("U28NR16B16e4", "C6", "UMi28", (0, 3, 6), (824, 636, 170), ("0.287", "0.252", "0.322"), "step_U28_S1:3"),
         ("UMi28", 32): ("U28NR32B16e4", "C9", "UMi28", (-3, 0, 3), (958, 599, 127), ("0.432", "0.401", "0.463"), "primary_U28_L90:3")}
# frontier runs: (name, spec1 cell, spec2 cell, level, recorded R1 / R2 [90%] of THAT run, recorded R1 - R2 [level] + p, file:line,
#                 cells whose registered CI this run's file carries)
RUNS = [("primary D2", ("D2", 32), ("D2", 8), 0.95, (("0.811", "0.790", "0.832"), ("0.509", "0.470", "0.544")),
         ("+0.302", "+0.254", "+0.355", "0.0000"), "primary_D2_L95:3-6", (("D2", 32), ("D2", 8))),
        ("primary UMi28", ("UMi28", 32), ("UMi28", 8), 0.90, (("0.432", "0.401", "0.463"), ("0.150", "0.108", "0.190")),
         ("+0.282", "+0.232", "+0.335", "0.0000"), "primary_U28_L90:3-6", (("UMi28", 32), ("UMi28", 8))),
        ("step D2 S2", ("D2", 32), ("D2", 16), 0.90, (("0.811", "0.790", "0.832"), ("0.823", "0.774", "0.874")),
         ("-0.012", "-0.067", "+0.041", "0.7200"), "step_D2_S2:3-6", (("D2", 16),)),
        ("step UMi28 S1", ("UMi28", 16), ("UMi28", 8), 0.90, (("0.287", "0.252", "0.322"), ("0.150", "0.108", "0.190")),
         ("+0.137", "+0.085", "+0.193", "0.0000"), "step_U28_S1:3-6", (("UMi28", 16),)),
        ("step UMi28 S2", ("UMi28", 32), ("UMi28", 16), 0.90, (("0.432", "0.401", "0.463"), ("0.287", "0.252", "0.323")),
         ("+0.145", "+0.099", "+0.193", "0.0000"), "step_U28_S2:3-6", ())]
# SCALE16e4 §6.1.4 (b): failures / 2560 of the C9 cells per grid SNR -12..+6 (genie, V1, b*)
REC_C9 = {"NR32B16e4": {GE: [347, 48, 18, 4, 3, 2, 0], V1A: [1347, 224, 42, 10, 7, 4, 2], BS: [2243, 849, 231, 81, 47, 23, 20]},
          "U28NR32B16e4": {GE: [846, 423, 227, 88, 30, 9, 3], V1A: [2219, 1068, 595, 349, 180, 70, 27],
                           BS: [2280, 1207, 761, 509, 304, 145, 62]}}
LABELS_KO = [
    "1차 라벨 (§6.1.1, §2.1 문구 그대로):",
    "  D2 — (T+): \"Nr 8→32 에서 V1 의 genie 격차 회수율(b* 대비 상대 격차)이 커진다 (D2, 동일예산 1.6e5, b* 판정점 운영점, UNGATED 배열 "
    "규모 축 측정)\" + G_D2 + \"[운영점 정합 강건]\" \"[K 상한 강건]\".",
    "  UMi28 — (T+): \"Nr 8→32 에서 V1 의 genie 격차 회수율(b* 대비 상대 격차)이 커진다 (UMi28, 동일예산 1.6e5, b* 판정점 운영점, UNGATED "
    "배열 규모 축 측정)\" + G_UMi28 + \"[운영점 정합 강건]\" \"[K 상한 민감: 외삽 불가]\" (UMi28 C9 r = 1.2799 >= 1 -> c_K = inf, §2.1 Q-K (1) "
    "로 강제; BLER 전에 정해짐).",
    "  G_D2 = \"(b* = 등록 프로토콜의 GMM — kron K ≤ 4096, 재시작 3, EM 상한 500 반복·tol/patience 정지 — 이며 최적 GMM 이 아니다; 격자 끝·tol "
    "정지 셀: D2 C9 `NR32B16e4` tol 정지 24/24 (b* kron 2048 은 적합 격자 내부, 격자 끝 아님), D2 C2 `B16e4k` 격자 끝 kron 1024 (2048 미적합))\"",
    "  G_UMi28 = \"(b* = 등록 프로토콜의 GMM — kron K ≤ 4096, 재시작 3, EM 상한 500 반복·tol/patience 정지 — 이며 최적 GMM 이 아니다; 격자 "
    "끝·tol 정지 셀: UMi28 C9 `U28NR32B16e4` 격자 끝 kron 4096 (4096 멈춤)·tol 정지 24/24, UMi28 C2 `U28B16e4` 격자 끝 kron 4096 (4096 멈춤))\"",
    "  Holm 순서: p_D2 = p_UMi28 = 0.0000 (B = 2000 이라 p < 0.001 로 읽음) -> 동률 -> D2 첫째 (95 % CI), UMi28 둘째 (90 % CI).",
    "  Q-OP L* = R*_C9 - R*_C2 (R*@0.05): D2 +0.299 [95% +0.190, +0.413], UMi28 +0.339 [90% +0.210, +0.460] -> 둘 다 \"[운영점 정합 강건]\".",
    "  Q-K D2 세 실행 (a) +0.466 [95% +0.294, +0.770] (b) +0.302 [95% +0.254, +0.355] (c) +0.466 [95% +0.294, +0.770] -> 모두 (T+) -> "
    "\"[K 상한 강건]\"; 등록 공개의 재게시: C2 끝의 c_K = 5.264 로 R+_C2 가 0.509 -> 0.346 [90% 0.106, 0.492] 로 내려가 (a)·(c) 가 '강건' 쪽으로 "
    "기울고, 그래서 실행 (b) 가 (T+) 의 실제 검사다; 미확장 D2 C2 b* 자체는 반대로 ΔR_D2 에 보수적이다.",
    "  데이터셋 문장 S_D2·S_UMi28 성립, 공동 문장 성립 (§6.1.1 문구; \"적어도 하나\" 문장은 쓰지 않는다; 데이터셋을 합치지 않는다).",
    "2차 단계 라벨 (§6.1.2, 90 %, 보정 없음, 단계마다 독립): \"D2 8→16 (기록값, 채점 없음)\" (+0.314 [90% +0.251, +0.381], §0.1); "
    "\"D2 16→32 판정하지 못함\"; \"UMi28 8→16 증가\"; \"UMi28 16→32 증가\" -> \"UMi28 단조 증가\"; D2 는 \"D2 단조 증가\" 를 붙이지 않는다.",
    "  (\"판정하지 못함\" 은 어느 쪽의 증거도 아니다 — 등록 §2 머리말.)  R* 단계 (보고, 라벨 없음): D2 S2 +0.102 [90% +0.030, +0.175]; UMi28 S1 "
    "+0.087 [90% -0.042, +0.216]; UMi28 S2 +0.252 [90% +0.140, +0.352]."]
CAVEATS = [
    "Caveats copied from SCALE16e4 §6.1.7 / §6.1.4 (facts only):",
    "  - grid edge: UMi28 C6 / C9 b* = kron 4096 (stopped at 4096); reuse UMi28 C2 and D2 C6 kron 4096, D2 C2 kron 1024 (2048 not fitted). "
    "D2 C9 is INTERIOR (merged kron 4096 ll_val 237.474 < kron 2048 242.737) -> no K2 tag, Q-K C9 slot '-'.  Convergence: the new 3 cells "
    "stopped by tol 24/24 / 22/24 (patience 2) / 24/24.",
    "  - UMi28 C6 decision points 0/+3/+6 leave one grid point (-3 dB) below; -9/-6 dB are off the grid and were not measured.",
    "  - reuse cells' registered CIs are THIS run's file values and differ from the §0.1 table in the third digit (D2 C2 [0.470, 0.544] "
    "vs [0.470, 0.545]; D2 C6 [0.774, 0.874] vs [0.771, 0.871]; UMi28 C2 [0.108, 0.190] vs [0.110, 0.189]).  UMi28 C6 appears in two runs: "
    "step S1 [0.252, 0.322] (drawn) and step S2 [0.252, 0.323] (same point estimate).",
    "  - every cell is an UNGATED array-scaling measurement, cell / budget / prior limited; seed-spread caveat (SEEDS16e4): D2 0.011, UMi28 0.028.",
    "  - last-EMA tags (report-only, §6.1.4 (f)): R_dp(last) D2 C9 0.808 [0.786, 0.829], UMi28 C6 0.278 [0.243, 0.313], UMi28 C9 0.439 "
    "[0.409, 0.469]; role sensitivity of the reuse cells: D2 C6 0.823/0.806, UMi28 C2 0.150/0.152; D2 C2 has legacy-last weights only.",
    "  - first K = 4096 chunk worker RSS was not recorded (deviation, §6.1.5); no memory-guard raise, no OOM.",
    "  - D2 C9 table-B 'all 13 baselines' sentence NOT met (X* = V1-pilot, R_X* undefined: -3 dB BLER 0.0047 < 0.005); UMi28 C6 / C9 MET."]


def main():
    specs = {k: f"{raw(v[0])}:{v[1]}:{','.join(str(s) for s in v[3])}" for k, v in CELLS.items()}
    txt = ["F30 -- the antenna-array scaling axis (SCALE16e4): recovery over the decision points R_dp vs Nr = 8 / 16 / 32 (C2 / C6 / C9, "
           "Nt 4, T 16, Tp 4, equal budget N' = 1.6e5, test trials 0..2559, n = 2560 per SNR, BLER@16) for D2 and UMi28, and the BLER "
           "curves of the two C9 cells.  Recomputed from raw by code/figure_f30.py (frontier_ci.cmd_recovery, B 2000, seed 20260926) "
           "and asserted against NEXT_EXPERIMENTS_SCALE16e4 §6.1.", "",
           "raw paths (read-only): " + "; ".join(f"{d} Nr {nr} {v[1]} = {raw(v[0])}" for (d, nr), v in CELLS.items()), ""]
    # ---------------- decision points + counts per cell ----------------
    for (dset, nr), (tag, cell, prior, dp, cnt, rr, src) in CELLS.items():
        d = F.raws(raw(tag))
        snrs = sorted(k[2] for k in d if k[:2] == (cell, prior))
        got = decision_points(d, cell, prior, snrs, BS)
        assert got == [float(s) for s in dp], (tag, got, dp)
    # ---------------- the five frontier runs ----------------
    R = {}
    fr = ["recomputed frontier_ci.cmd_recovery output (raw names = the paths above):"]
    for name, c1, c2, level, rec12, recd, src, owns in RUNS:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            out = F.cmd_recovery(specs[c1], specs[c2], F.B, F.SEED, level)
        fr += [f"  [{name}; record {src}]"] + ["  " + l for l in buf.getvalue().splitlines()]
        got = buf.getvalue()
        for c in (c1, c2):
            got = got.replace(raw(CELLS[c][0]), f"raw_{CELLS[c][0]}")
        fil = open(os.path.join(RV, f"scale2_{src.split(':')[0]}.txt"), encoding="utf-8").read().splitlines()[1:8]
        assert got.splitlines() == fil, (name, got, fil)              # byte-identical to the record file lines 2-8
        for j, c in enumerate((c1, c2)):
            r = out["r"][j]; lo, hi = F.pct(out["bo"][:, j], [5, 95])
            _, (b, v, g) = F._R(F._rec_cols(specs[c])[3])
            assert (b, v, g) == CELLS[c][4], (name, c, b, v, g)
            assert (f3(r), f3(lo), f3(hi)) == rec12[j], (name, c, r, lo, hi)
            if c in owns:                                   # the run whose file line registers this cell's CI (CELLS source)
                R[c] = (r, lo, hi)
        lo, hi, p = F.ci_p(out["bo"][:, 0] - out["bo"][:, 1], level)
        dr = out["r"][0] - out["r"][1]
        assert (s3(dr), s3(lo), s3(hi), f"{p:.4f}") == recd, (name, dr, lo, hi, p)
    assert set(R) == set(CELLS), sorted(set(CELLS) - set(R))
    for (dset, nr), (tag, cell, prior, dp, cnt, rr, src) in CELLS.items():
        r, lo, hi = R[(dset, nr)]
        assert (f3(r), f3(lo), f3(hi)) == rr, (dset, nr, r, lo, hi, rr)   # the drawn CI = the registered one
        txt.append(f"  {dset:<6} Nr {nr:>2} {cell}  raw_{tag:<13} decision SNRs {list(dp)} (recomputed, anchor b*)  SigmaF b* {cnt[0]} "
                   f"V1 {cnt[1]} genie {cnt[2]}  R_dp = {r:.3f} [90% {lo:.3f}, {hi:.3f}]  (registered CI: {src})")

    # ---------------- figure ----------------
    fig, axs = plt.subplots(2, 2, figsize=(7.16, 5.6), layout="constrained")
    for ax, dset, tl in ((axs[0, 0], "D2", "(a)"), (axs[0, 1], "UMi28", "(b)")):
        nrs = [8, 16, 32]
        y = np.array([R[(dset, n)][:3] for n in nrs])
        ax.errorbar(nrs, y[:, 0], yerr=[y[:, 0] - y[:, 1], y[:, 2] - y[:, 0]], color=INK, marker="o", ms=4.5, lw=1.1, capsize=2.5,
                    elinewidth=1.0, zorder=3)
        for n, (r, lo, hi) in zip(nrs, y):
            ax.text(n, hi + 0.02, f"{r:.3f}", va="bottom", ha="center", fontsize=7, color=INK2)
        ax.set_xscale("log", base=2); ax.set_xticks(nrs, ["8", "16", "32"]); ax.set_xlim(6.3, 45)
        ax.minorticks_off(); ax.set_ylim(0, 1.0); ax.set_xlabel(r"Receive antennas $N_r$ ($N_t = 4$)")
        ax.set_ylabel("Fraction of the GMM-to-\nperfect-CSI gap closed")
        ax.set_title(tl, loc="left", fontweight="bold", fontsize=8.2)
    rf = {}
    for ax, (dset, tag, tl) in zip(axs[1], (("D2", "NR32B16e4", "(c) D2 C9 (32×4)"), ("UMi28", "U28NR32B16e4", "(d) UMi28 C9 (32×4)"))):
        d = F.raws(raw(tag)); prior = CELLS[(dset, 32)][2]
        keys = F.points(d, "C9"); snrs = np.array([k[2] for k in keys])
        rec = {**REC_C9[tag], R2: rec_fails(os.path.join(RV, f"pairB_{tag}.txt"))[R2]}
        txt += ["", f"{tl} BLER@16 (raw_{tag}), failures / 2560 per SNR " + " ".join(f"{s:+.0f}" for s in snrs) + " dB:"]
        for arm, sty, lab in ((R2, GAUSS, "Gaussian prior"), (BS, GMM, "GMM prior"), (V1A, V1, "Proposed"),
                              (GE, GENIE, "Perfect CSI")):
            k = np.array([int(F.fails(d, key, arm).sum()) for key in keys]); n = 2560
            assert all(len(F.fails(d, key, arm)) == n for key in keys)
            assert k.tolist() == rec[arm], (tag, arm, k.tolist(), rec[arm])
            ci = np.array([wilson(int(a), n) for a in k]); p = k / n; ok = k > 0
            ax.errorbar(snrs, np.where(ok, p, np.nan), yerr=[np.where(ok, p - ci[:, 0], np.nan), np.where(ok, ci[:, 1] - p, np.nan)], color=sty["color"], marker=sty["marker"],
                        ls=sty["ls"], lw=1.1, ms=(4 if sty["marker"] != "*" else 6.5), capsize=1.5, elinewidth=0.8, label=lab,
                        zorder=4 if arm == V1A else 3)
            if arm == GE: zero_arrows(ax, snrs[~ok], n, sty["color"])
            txt.append(f"  {arm:<20} " + " ".join(f"{int(a):5d}" for a in k)
                       + ("" if ok.all() else "   (zero-failure points not drawn: " + ", ".join(f"{s:+.0f}" for s in snrs[~ok]) + " dB)"))
        ax.set_yscale("log"); ax.set_ylim(2e-4, 1.05); ax.set_xticks(range(-12, 7, 3)); ax.set_xlabel("SNR [dB]")
        ax.set_ylabel("BLER")
        ax.set_title(tl[:3], loc="left", fontweight="bold", fontsize=8.2)    # tl itself stays in the record text
    axs[1, 0].legend(loc="lower left", frameon=False, fontsize=6.8, handlelength=2.0)
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(FIG, f"F30_scale_trend.{ext}"))
    txt += ["", "Annotations in (a)/(b) are English glosses of the registered labels below (verbatim)."] + LABELS_KO + [""] + CAVEATS \
        + ["", "Asserted: lines 2-8 of each scale2_<run>.txt reproduced byte-identically (raw path -> raw_<tag>); decision points of the 6 cells (anchor b*), SigmaF (b*, V1, genie) and R_dp [90%] of every cell in every run, "
           "Delta R [level] + p of the 5 runs (§6.1.1 / §6.1.2 / the scale2_* record files), C9 failures per SNR of genie / V1 / b* "
           "(§6.1.4 (b)) and R2 (pairB_<T>.txt)."] + [""] + fr
    print("\n".join(txt))                                          # record text (internal names), not written to a file


if __name__ == "__main__":
    main()
