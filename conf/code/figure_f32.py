"""conf/code/figure_f32.py -- F32: the high-SNR supplement (HISNR16e4; REPORT-ONLY, no registered label; report figure, read-only).

(a) D2 C2 (8x4, headline weights), (b) D2 C6 (16x4): BLER@16 at +6 / +9 / +12 / +15 dB of V1, b*, the Gaussian prior R2 and genie
with 95% Wilson intervals, on the NEW trials 10000..30479 (n = 20480 per SNR; filled markers, solid) next to the original test
tags (trials 0..2559, n = 2560; hollow markers, offset left).  The two are drawn side by side and never pooled (HISNR16e4 §1);
the registered decision points and labels stay those of the original tags.  R1-turbo and R3-bigamp are listed in the .txt only.
Recomputed from raw (raw_HSB16e4k / raw_HSNR16 and raw_B16e4k / raw_NR16B16e4) with hisnr_report.wilson (the registered report's
formula; a raised block is a failure) and asserted against NEXT_EXPERIMENTS_HISNR16e4 §6.1: the n = 20480 failures of all 6 arms,
the paired b*-only : V1-only counts, the original-tag V1 / b* failures of the side-by-side table, the original genie failures
(§6.1 '기대 실패 수' line) and prediction 3 (16/16 inside); original R2 against the record files pairB_SP{B16e4k,NR16}.txt.
Writes figs/F32_hisnr_highsnr.{pdf,png,txt}.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from analysis import load_raw, paired
from hisnr_report import wilson
from figstyle import INK, V1, GMM, GENIE, GAUSS
from figure_f30 import rec_fails, RV, FIG, raw

V1A, BS, GE, R2, R1, R3 = "M-ours-dscore-C-V1", "M-ours-bstar", "R5-genie", "R2-ours-G", "R1-turbo", "R3-bigamp"
SNRS = (6.0, 9.0, 12.0, 15.0)
DRAW = [(R2, GAUSS, "same EP receiver, Gaussian prior (R2)"), (BS, GMM, r"GMM prior $b^*$"),
        (V1A, V1, "diffusion prior V1 (proposed)"), (GE, GENIE, "known-channel reference (genie)")]
# HISNR16e4 §6.1 (n = 20480, +6/+9/+12/+15 dB)
REC_HS = {"C2": {V1A: [111, 59, 39, 23], BS: [235, 149, 81, 72], R2: [467, 292, 182, 133], R1: [903, 521, 291, 204],
                 R3: [1083, 1033, 1116, 1100], GE: [66, 36, 16, 13]},
          "C6": {V1A: [29, 24, 20, 13], BS: [178, 130, 72, 46], R2: [309, 213, 125, 80], R1: [621, 433, 264, 157],
                 R3: [1090, 1265, 1418, 1099], GE: [17, 16, 7, 7]}}
REC_PAIR = {"C2": [(158, 34), (106, 16), (61, 19), (57, 8)], "C6": [(156, 7), (111, 5), (63, 11), (38, 5)]}   # b* only : V1 only
# original tags (n = 2560): V1 / b* = §6.1 side-by-side table; genie = §6.1 '기대 실패 수' line; R2 = record file (below)
REC_OR = {"C2": {V1A: [16, 7, 5, 3], BS: [28, 17, 16, 8], GE: [9, 2, 2, 2]},
          "C6": {V1A: [6, 2, 2, 2], BS: [22, 14, 10, 5], GE: [6, 1, 2, 0]}}
CELLS = [("C2", "(a) D2 C2 (8×4, headline)", "HSB16e4k", "B16e4k", "SPB16e4k"),
         ("C6", "(b) D2 C6 (16×4, UNGATED)", "HSNR16", "NR16B16e4", "SPNR16")]


def counts(d, cell, arm):
    """failures @16 per SNR of SNRS (a raised block = failure) and n."""
    out, ns = [], set()
    for s in SNRS:
        e = np.asarray(d[(cell, "S2", s)][arm]["blk_err"], float)[:, -1]
        out.append(int(np.where(np.isfinite(e), e, 1.0).sum())); ns.add(len(e))
    assert len(ns) == 1, ns
    return out, ns.pop()


def main():
    fig, axs = plt.subplots(1, 2, figsize=(7.16, 3.3), sharey=True, layout="constrained")
    txt = ["F32 -- high-SNR supplement (HISNR16e4, REPORT-ONLY): BLER@16 at +6..+15 dB on the new trials 10000..30479 (n = 20480 "
           "per SNR) next to the original test tags (trials 0..2559, n = 2560), 95% Wilson; never pooled.  Recomputed from raw by "
           "code/figure_f32.py and asserted against NEXT_EXPERIMENTS_HISNR16e4 §6.1.", "",
           "raw paths (read-only): " + "; ".join(f"{c} new = {raw(h)}, original = {raw(o)}" for c, _, h, o, _ in CELLS), ""]
    inside = 0
    for ax, (cell, title, hs, orig, sp) in zip(axs, CELLS):
        dh, _, wh = load_raw("D2", root=raw(hs)); do, _, wo = load_raw("D2", root=raw(orig))
        assert not wh and not wo, (wh, wo)
        rec_or = {**REC_OR[cell], R2: rec_fails(os.path.join(RV, f"pairB_{sp}.txt"))[R2][-4:]}   # columns +6..+15 of -3..+15
        txt.append(f"{title}: failures / n  BLER [95% Wilson] per SNR " + " ".join(f"{s:+.0f}" for s in SNRS) + " dB")
        for arm in (V1A, BS, R2, R1, R3, GE):
            k, n = counts(dh, cell, arm)
            assert n == 20480 and k == REC_HS[cell][arm], (cell, arm, n, k)
            txt.append(f"    n=20480  {arm:<20} " + "  ".join(f"{a:5d} {a / n:.2e} [{wilson(a, n)[0]:.2e}, {wilson(a, n)[1]:.2e}]" for a in k))
            if arm in rec_or:
                ko, no = counts(do, cell, arm)
                assert no == 2560 and ko == rec_or[arm], (cell, arm, no, ko, rec_or[arm])
                txt.append(f"    n=2560   {arm:<20} " + "  ".join(f"{a:5d} {a / no:.2e} [{wilson(a, no)[0]:.2e}, {wilson(a, no)[1]:.2e}]"
                                                             for a in ko))
                if arm in (V1A, BS):                       # §3 prediction 3: new point estimate inside the original 95% Wilson
                    inside += sum(wilson(b, no)[0] <= a / n <= wilson(b, no)[1] for a, b in zip(k, ko))
        pr = [paired(dh[(cell, "S2", s)], BS, V1A)[:2] for s in SNRS]
        assert [tuple(int(v) for v in p) for p in pr] == REC_PAIR[cell], (cell, pr)
        txt.append("    paired b* only : V1 only (n = 20480, report-only) " + "  ".join(f"{s:+.0f} dB {a}:{b}" for s, (a, b) in zip(SNRS, pr)))
        zeros = []
        for (arm, sty, lab), jit in zip(DRAW, (-0.09, -0.03, 0.03, 0.09)):     # small per-arm jitter: equal counts overlap
            for dd, dx, filled in ((do, -0.35, False), (dh, 0.35, True)):
                k, n = counts(dd, cell, arm)
                k = np.array(k); p = k / n; ci = np.array([wilson(int(a), n) for a in k]); ok = k > 0
                x = np.array(SNRS) + dx + jit
                ax.errorbar(x[ok], p[ok], yerr=[p[ok] - ci[ok, 0], ci[ok, 1] - p[ok]], color=sty["color"], marker=sty["marker"],
                            ls=sty["ls"] if filled else "none", lw=1.1, ms=(3.8 if sty["marker"] != "*" else 6),
                            mfc=sty["color"] if filled else "white", mew=0.9, capsize=1.5, elinewidth=0.8,
                            zorder=4 if arm == V1A else 3)
                zeros += [f"{arm} n={n} {s:+.0f} dB" for s, z in zip(SNRS, ok) if not z]
        txt.append("    zero-failure points (not drawn on the log axis): " + ("; ".join(zeros) if zeros else "none"))
        txt.append("")
        ax.set_title(title, fontsize=8.2); ax.set_yscale("log"); ax.set_xticks(SNRS, [f"+{s:.0f}" for s in SNRS])
        ax.set_xlabel("SNR [dB]"); ax.set_ylim(5e-5, 5e-2)
    assert inside == 16, inside
    axs[0].set_ylabel("BLER (16 outer iterations)")
    L = [Line2D([], [], color=sty["color"], marker=sty["marker"], ls=sty["ls"], ms=4 if sty["marker"] != "*" else 6, label=lab)
         for arm, sty, lab in DRAW[::-1]]
    L += [Line2D([], [], color=INK, marker="o", ls="-", ms=4, label="filled, right: new trials, n = 20480"),
          Line2D([], [], color=INK, marker="o", mfc="white", ls="none", ms=4, label="hollow, left: original test tags, n = 2560")]
    fig.legend(handles=L, loc="outside lower center", ncol=3, frameon=False, handlelength=2.4, fontsize=7)
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(FIG, f"F32_hisnr_highsnr.{ext}"))
    txt += [f"§3 prediction 3 recomputed: new V1 / b* point estimate inside the original 95% Wilson in {inside}/16 (recorded 16/16).",
            "As recorded (HISNR16e4 §1 / §2 / §6.1): 보고 전용 — 새 판정 라벨을 만들지 않는다; 원 태그 (n = 2560) 와 나란히 적되 합치지 않는다; 그림은 "
            "등록된 곡선을 대체하지 않고 별도 패널·표기로 싣는다; 원고 문장은 \"고SNR 구간의 BLER 은 추가 n = 20480 시행에서 …\" 처럼 보고 전용 보강으로만 "
            "쓰고, 등록된 판정점·라벨·\"전부\" 문장은 원 태그의 것이다.  p 값은 서술용 (라벨 없음).  §3 예측 3/3 적중.",
            "genie floor (genie_floor.py --skip0 10000, §6.1): C2 genie failures 131 over the 4 SNRs, 114 of them in L = 3 blocks; C6 47, "
            "44 in L = 3 (rank-deficient L = 3 < Nt = 4 blocks, cond(H) ~ 1e16).",
            "Deviations recorded in §6.1: run HEAD 6b1de688 != freeze 32444c91 (DECISIONS.md / WORK_QUEUE.md only, no code difference); "
            "other CPU work ran during the HISNR window (SEEDS3 audit scripts, SPARSE re-tuning, stage-2 GPU fits + bash loops; "
            "concurrent_processes.txt, a lower bound).  D2 C6 is UNGATED (no D1 sibling)."]
    open(os.path.join(FIG, "F32_hisnr_highsnr.txt"), "w", encoding="utf-8").write("\n".join(txt) + "\n")
    print("\n".join(txt))


if __name__ == "__main__":
    main()
