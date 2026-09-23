"""conf/code/figures_stagec3.py -- F15: the gap is not explained by data, by mixture components, or by
the checkpoint seed.

This is the defensive figure.  Every panel answers one reviewer objection to the headline result
(C2, equal budget, V1 below the fitted-GMM prior), using measurements that already exist:

  (a) WHERE the gap lives on the SNR axis.  C2 at equal budget N=1e4 over ELEVEN SNRs (-9..+15 dB;
      the four lowest come from the §6p extension), GMM and V1, with the BLER ratio on a twin axis.
      V1 is below the GMM at every one of the eleven points and its divergence guard never fires.
  (b) "You just gave the learned prior more data."  V1 and the GMM against the training budget
      N = 1e4 / 4e4 / 1.6e5, all arms equal-budget within each point.  Both curves are flat.
  (c) "Your GMM is under-parameterised."  The GMM arm against the number of mixture components,
      K = 512 / 1024 / 2048 at N=4e4 and K = 512 / 1024 at N=1.6e5, each re-selected by validation
      log-likelihood on the extended grid.  The likelihood rises by 2.2-3.2 nat; the BLER does not move.
  (d) "That checkpoint was lucky."  V1 and V0 at the three independently trained seeds a1/a2/a3.

Every number is READ from the files below.  Nothing here recomputes, resamples or re-runs anything.
  raw_B1e4lo/  (C2, -9/-7/-6/-5 dB)  +  raw_B1e4/ (C2, -3..+15)                     panel (a)
  raw_B1e4/, raw_B4e4/, raw_B16e4/   (C2, -3 dB, three budgets)                     panel (b)
  raw_B4e4/, raw_B4e4k1/, raw_B4e4k/, raw_B16e4/, raw_B16e4k/  (C2, -3 dB)          panel (c)
  raw_B1e4/, raw_B1e4s2/, raw_B1e4s3/ (C2, -3 dB, seeds a1/a2/a3)                   panel (d)
  the .npz GMM fits for the ll_val annotations in (c)
"""
import os
import re
import sys
import glob
import collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import common as C
import figures as F0
from figures_stagec import _save, RES
from figures_stagec2 import GATE_LINE, GATE_LINE_PASS

GMM, V1, V0 = "M-ours-bstar", "M-ours-dscore-C-V1", "M-ours-dscore-C-V0"
DIV = 10.0


def cell_arm(rawdir, cell, arm, snr=None):
    """(mean BLER@16, guard rate) per SNR, with the pre-registered non-finite rule."""
    b = collections.defaultdict(list)
    g = collections.defaultdict(list)
    pat = f"D2_{cell}_*snr{int(snr)}_*.npz" if snr is not None else f"D2_{cell}_*.npz"
    for f in glob.glob(os.path.join(C.CONF, rawdir, pat)):
        s = int(re.search(r"snr(-?\d+)", f).group(1))
        d = np.load(f, allow_pickle=True)
        if f"{arm}|blk_err" not in d.files:
            continue
        v = d[f"{arm}|blk_err"][:, 15]
        b[s].append(np.where(np.isfinite(v), v, 1.0))
        m = d[f"{arm}|nmse"][:, 15]
        g[s].append(~np.isfinite(m) | (m > DIV))
    return ({s: float(np.concatenate(v).mean()) for s, v in b.items()},
            {s: float(np.concatenate(v).mean()) for s, v in g.items()})


def llv(path):
    return float(np.load(os.path.join(C.CONF, path))["ll_val"])


def fig15():
    plt.rcParams.update({"font.size": 7.5, "axes.labelsize": 7.5, "axes.titlesize": 8,
                         "xtick.labelsize": 6.8, "ytick.labelsize": 6.8, "legend.fontsize": 6.4})
    fig = plt.figure(figsize=(7.16, 5.4))
    gs = GridSpec(2, 2, figure=fig, hspace=0.62, wspace=0.42, left=0.095, right=0.93,
                  top=0.915, bottom=0.145)

    # ---------- (a) the SNR axis, eleven points, equal budget N=1e4
    ax = fig.add_subplot(gs[0, 0])
    bg, _ = cell_arm("raw_B1e4lo", "C2", GMM)
    bv, gv = cell_arm("raw_B1e4lo", "C2", V1)
    bg2, _ = cell_arm("raw_B1e4", "C2", GMM)
    bv2, gv2 = cell_arm("raw_B1e4", "C2", V1)
    bg.update(bg2); bv.update(bv2); gv.update(gv2)
    S = np.array(sorted(bg))
    yg = np.array([bg[s] for s in S]); yv = np.array([bv[s] for s in S])
    ax.semilogy(S, yg, "-D", color="tab:red", ms=3.2, lw=1.1, label="fitted GMM, b*")
    ax.semilogy(S, yv, "-o", color="tab:green", ms=3.2, lw=1.1, label="learned score, V1")
    ax.fill_between(S, yv, yg, color="tab:green", alpha=0.13, lw=0)
    ax.set_xlabel("SNR (dB)"); ax.set_ylabel("BLER after 16 outer iterations")
    ax.set_title(f"(a)  C2, equal budget $N$ = 1e4, 11 SNRs\n"
                 f"V1 below the GMM at {int((yv < yg).sum())}/{len(S)};  V1 guard max "
                 f"{max(gv[s] for s in S):.3f}", fontsize=7.6, linespacing=1.35)
    ax.grid(alpha=0.25, which="both", lw=0.4); ax.legend(loc="lower left", fontsize=6.2,
                                                         bbox_to_anchor=(0.0, 0.20))
    axr = ax.twinx()
    axr.plot(S, yg / yv, ":s", color="0.35", ms=2.8, lw=0.9)
    axr.set_ylabel("GMM / V1 ratio", color="0.35", fontsize=6.8, labelpad=1)
    axr.tick_params(axis="y", colors="0.35", labelsize=6.8)
    axr.set_ylim(0.8, 3.8)
    k = int(np.argmax(yg - yv)); r = int(np.argmax(yg / yv))
    ax.annotate(f"largest absolute gap\n{S[k]:+.0f} dB: {yg[k]:.3f} - {yv[k]:.3f} = {yg[k]-yv[k]:.3f}",
                xy=(S[k], np.sqrt(yg[k] * yv[k])), xytext=(0.30, 0.86), textcoords="axes fraction",
                fontsize=5.8, color="0.25", ha="left",
                arrowprops=dict(arrowstyle="->", color="0.5", lw=0.6))
    axr.annotate(f"largest ratio {S[r]:+.0f} dB: {yg[r]/yv[r]:.1f}x", xy=(S[r], yg[r] / yv[r]),
                 xytext=(0.42, 0.45), textcoords="axes fraction", fontsize=5.8, color="0.35",
                 arrowprops=dict(arrowstyle="->", color="0.5", lw=0.6))


    # ---------- (b) the budget axis
    ax = fig.add_subplot(gs[0, 1])
    # Two GMM series, because §6l changed what b* is at the larger budgets and the two readings differ:
    #   K held at 512  -> the like-for-like budget axis (only N moves)
    #   b* on the extended grid -> the baseline the project is actually obliged to use (§6l 무결성 조건:
    #   "새 b* 가 나오면 그것이 GMM arm 이 된다. 기존 K=512 결과로 되돌아가지 않는다.")
    B512 = [(1e4, "raw_B1e4"), (4e4, "raw_B4e4"), (1.6e5, "raw_B16e4")]
    BSTAR = [(1e4, "raw_B1e4", 512), (4e4, "raw_B4e4k", 2048), (1.6e5, "raw_B16e4k", 1024)]
    xs = [n for n, _ in B512]
    g512 = [cell_arm(d, "C2", GMM, -3)[0][-3] for _, d in B512]
    gstar = [cell_arm(d, "C2", GMM, -3)[0][-3] for _, d, _ in BSTAR]
    yv = [cell_arm(d, "C2", V1, -3)[0][-3] for _, d, _ in BSTAR]
    ax.semilogx(xs, g512, ":D", color="tab:red", ms=3.6, lw=1.0, mfc="white",
                label="GMM, $K$ held at 512")
    ax.semilogx(xs, gstar, "-D", color="tab:red", ms=4.0, lw=1.3,
                label="GMM, $b^*$ on the extended $K$ grid")
    ax.semilogx(xs, yv, "-o", color="tab:green", ms=4.0, lw=1.3, label="learned score, V1")
    for x, gv_, kk in zip(xs, gstar, [k for _, _, k in BSTAR]):   # NOT `gs`: that is the GridSpec
        ax.text(x, gv_ - 0.008, f"{gv_:.3f}\n$K$={kk}", ha="center", va="top", fontsize=5.9,
                color="tab:red", linespacing=1.2)
    for x, v in zip(xs, yv):
        ax.text(x, v - 0.010, f"{v:.3f}", ha="center", va="top", fontsize=6.0, color="tab:green")
    ax.set_xlabel("$N_{\\rm train}$ (channel samples, SAME set for every arm)")
    ax.set_ylabel("BLER at $-$3 dB")
    ax.set_title("(b)  the budget axis: 16x data")
    ax.set_ylim(0.09, 0.33); ax.grid(alpha=0.25, which="both", lw=0.4)
    ax.legend(loc="upper left", fontsize=5.8, framealpha=0.95)
    ax.text(0.97, 0.38, "gap, $K$ = 512:  " + " / ".join(f"{a-b:.3f}" for a, b in zip(g512, yv))
            + "\ngap, $b^*$ extended:  " + " / ".join(f"{a-b:.3f}" for a, b in zip(gstar, yv)),
            transform=ax.transAxes, ha="right", fontsize=6.0, color="0.25", linespacing=1.35)

    # ---------- (c) the K axis
    ax = fig.add_subplot(gs[1, 0])
    K4 = [(512, "raw_B4e4", "gmm_fits_D2_n4e4/fit_S2_Nr8_kronK512_n40000.npz"),
          (1024, "raw_B4e4k1", "gmm_fits_D2_K1024n40000/fit_S2_Nr8_kronK1024_n40000.npz"),
          (2048, "raw_B4e4k", "gmm_fits_D2_K2048n40000/fit_S2_Nr8_kronK2048_n40000.npz")]
    K16 = [(512, "raw_B16e4", "gmm_fits_D2_n16e4/fit_S2_Nr8_kronK512_n160000.npz"),
           (1024, "raw_B16e4k", "gmm_fits_D2_K1024n160000/fit_S2_Nr8_kronK1024_n160000.npz")]
    for lab, grp, col, mk in (("$N$ = 4e4", K4, "tab:red", "D"), ("$N$ = 1.6e5", K16, "tab:orange", "s")):
        ks = [k for k, _, _ in grp]
        ys = [cell_arm(d, "C2", GMM, -3)[0][-3] for _, d, _ in grp]
        ls = [llv(os.path.join("results", f)) for _, _, f in grp]
        ax.semilogx(ks, ys, "-", color=col, marker=mk, ms=4.0, lw=1.2, base=2,
                    label=f"fitted GMM, {lab}")
        up = lab.endswith("1.6e5")
        for k, y, l in zip(ks, ys, ls):
            ax.text(k, y + (0.013 if up else -0.013), f"{y:.4f}   $\\ell_{{\\rm val}}$ {l:.2f}",
                    ha="center", va="bottom" if up else "top", fontsize=5.8, color=col)
    v1_4 = cell_arm("raw_B4e4", "C2", V1, -3)[0][-3]
    v1_16 = cell_arm("raw_B16e4k", "C2", V1, -3)[0][-3]
    ax.axhline(v1_4, color="tab:green", ls="--", lw=1.0)
    ax.text(470, v1_4 + 0.004, f"V1 {v1_4:.4f}", color="tab:green", fontsize=6.2,
            va="bottom", ha="left")
    ax.set_xticks([512, 1024, 2048]); ax.set_xticklabels(["512", "1024", "2048"])
    ax.set_xlabel("$K$ (mixture components; $b^*$ re-selected on the extended grid)", fontsize=7)
    ax.set_ylabel("BLER at $-$3 dB")
    ax.set_title("(c)  the component axis: 4x $K$, $\\leq$ 4% change")
    ax.set_xlim(430, 2600)
    ax.set_ylim(0.13, 0.30); ax.grid(alpha=0.25, which="both", lw=0.4)
    ax.legend(loc="lower right", fontsize=6.0, bbox_to_anchor=(1.0, 0.03))

    # ---------- (d) the seed axis
    ax = fig.add_subplot(gs[1, 1])
    SD = [("a1", "raw_B1e4"), ("a2", "raw_B1e4s2"), ("a3", "raw_B1e4s3")]
    x = np.arange(3)
    v1 = [cell_arm(d, "C2", V1, -3)[0][-3] for _, d in SD]
    v0 = [cell_arm(d, "C2", V0, -3)[0][-3] for _, d in SD]
    gm = cell_arm("raw_B1e4", "C2", GMM, -3)[0][-3]
    ax.bar(x - 0.19, v0, 0.36, color="tab:purple", alpha=0.85, label="V0 (pre-registered site)")
    ax.bar(x + 0.19, v1, 0.36, color="tab:green", alpha=0.85, label="V1 (PSD-projected site)")
    ax.axhline(gm, color="tab:red", ls="--", lw=1.0)
    ax.text(-0.42, gm + 0.02, f"GMM {gm:.3f}", color="tab:red", fontsize=6.2, va="bottom", ha="left")
    for xi, a, b in zip(x, v0, v1):
        ax.text(xi - 0.19, a + 0.015, f"{a:.3f}", ha="center", fontsize=6.0, color="tab:purple")
        ax.text(xi + 0.19, b + 0.015, f"{b:.3f}", ha="center", fontsize=6.0, color="tab:green")
    ax.set_xticks(x); ax.set_xticklabels([f"seed {s}" for s, _ in SD])
    ax.set_ylabel("BLER at $-$3 dB"); ax.set_ylim(0, 1.12)
    ax.set_title("(d)  the seed axis: 3 independent checkpoints")
    ax.grid(alpha=0.25, axis="y", lw=0.4); ax.legend(loc="upper center", fontsize=6.0, ncol=1)
    ax.text(0.5, 0.36, f"V1 spread {max(v1)-min(v1):.4f}    V0 spread {max(v0)-min(v0):.4f}",
            transform=ax.transAxes, ha="center", fontsize=6.2, color="0.25")

    fig.text(0.5, 0.055, "All panels: D2, cell C2 (Tp = 4), n = 2560 trials per point, receiver identical "
                         "across arms; within every point the GMM and the learned prior see the SAME channel set.",
             ha="center", fontsize=6.5, color="0.3")
    # NOTE (2026-09-23, review_next G-1.2): the two footer strings below are printed INTO the figure
    # (figs/F15_gap_robustness.png/.pdf); they are NOT changed here and F15 is NOT regenerated.
    # "the gate-passing d2sx_N160000_a1" is shorthand: that D2 checkpoint has no gate row
    # (results/tables_D2_B16e4k.txt:45); it is qualified through its D1 sibling sx_N160000_D1.pt
    # (LADDER_C.md:1).  "the gate-failing points" are points whose D1 siblings FAIL GC
    # (results/samplecx_D1.txt:28-29).  At the next regeneration read: "... use d2sx_N160000_a1, whose
    # D1 sibling passes the gates." and "§6d registers the points whose D1 siblings fail GC as
    # budget-axis measurements, not arm results."  (Optional: the caption's "use the gate-passing
    # checkpoint:" is followed by GATE_LINE_PASS, which already carries the sibling qualifier.)
    fig.text(0.5, 0.028, "(a), (c) N=4e4 column and (d) use checkpoints whose D1 siblings FAIL GC "
                         "(0.243 at N=1e4, 0.167 at N=4e4); (b) rightmost point and (c) N=1.6e5 use the "
                         "gate-passing d2sx_N160000_a1.", ha="center", fontsize=6.5, color="0.3")
    fig.text(0.5, 0.004, "§6d registers the gate-failing points as budget-axis measurements, not arm results.",
             ha="center", fontsize=6.5, color="0.3")
    return _save(fig, "F15_gap_robustness", """
F15.  The gap is not explained by training data, by mixture components, or by the checkpoint seed.
All panels: D2, cell C2 (Tp = 4), n = 2560 trials per point, the same receiver for every arm, and
within each point the fitted GMM and the learned score are given the SAME channel set (equal budget,
10_SPEC_stageC A3).
(a) WHERE THE GAP LIVES.  Eleven SNRs from -9 to +15 dB at N_train = 1e4; the four lowest points are
the §6p extension (results/tables_D2_B1e4lo.txt), the rest are results/tables_D2_B1e4.txt.  V1 is
below the GMM at all eleven, and its F3 divergence guard never exceeds 0.000 across the whole range.
The two summaries of "gap" peak in different places and both are marked: the largest ABSOLUTE
reduction is at -6 dB (0.791 -> 0.601) and the largest RATIO is at +6 dB (0.0125 / 0.0039 = 3.2x).
§6p predicted the ratio would peak at -6/-7 dB; that prediction FAILED -- the ratio falls monotonically
below -3 dB because every arm's BLER is compressed towards 1.  The prediction was registered at commit
279512b before the run.
(b) THE BUDGET AXIS.  BLER at -3 dB against N_train = 1e4 / 4e4 / 1.6e5, every arm equal-budget within
each point.  V1 is 0.1453 / 0.1445 / 0.1449 -- flat to the third decimal across a 16-fold change in
training data.  The GMM is drawn twice because §6l changed what its b* is: with K HELD at 512 it is
0.2523 / 0.2504 / 0.2527 (gap 0.107 / 0.106 / 0.108, flat), and with b* taken from the EXTENDED K grid
at each budget -- which §6l's integrity condition obliges us to use, "새 b* 가 나오면 그것이 GMM arm 이
된다" -- it is 0.2523 (K=512) / 0.2480 (K=2048) / 0.2434 (K=1024) and the gap FALLS 0.107 / 0.104 /
0.098, about 8% over the range.  Read the solid red series: the honest statement is that the budget
alone does not move the gap, and that the larger budgets let the GMM use more components, which
narrows it slightly.  §6d predicted the gap would GROW with budget; that prediction FAILED.
(c) THE COMPONENT AXIS.  The GMM arm against K, with b* re-selected by validation log-likelihood on
the extended grid at each point (§6l; raw meta kron_K confirms the selection moved).  At N = 4e4 the
validation log-likelihood rises 2.16 nat from K=512 to K=2048 while the BLER moves from 0.2504 to
0.2480; at N = 1.6e5 it rises 3.18 nat from K=512 to K=1024 while the BLER moves from 0.2527 to
0.2434.  The mixture keeps improving as a density model far faster than it improves as a receiver
prior: 2.16 nat buys 1.0% of BLER at N = 4e4 and 3.18 nat buys 3.7% at N = 1.6e5.  §6l's own
prediction -- that extending the grid would move b* and SHRINK the 42% gap -- is therefore scored
PARTLY CORRECT: b* did move at both budgets, and the gap shrank from 42.7% to 40.5% at N = 1.6e5,
far less than the likelihood gain would suggest.  The consequence for the claim is that the earlier
grid truncation did not weaken the baseline (01_RULES:76).  K = 2048 was not fitted at N = 1.6e5: the
N = 4e4 measurement shows the BLER effect of that step is about 1%, and one restart costs roughly
nine GPU-hours; that is a stated limit, not a measurement.
(d) THE SEED AXIS.  V0 and V1 at -3 dB for three independently trained checkpoints (a1/a2/a3, same
recipe, same budget, selected among themselves by validation loss only -- never by BLER, §6g).  V1 is
0.1453 / 0.1496 / 0.1477 (spread 0.0043) against the GMM's 0.2523; V0 is 0.789 / 0.881 / 0.812
(spread 0.092).  The repaired wiring is insensitive to the seed and the pre-registered one is not.
The cause of that difference was not measured and is not claimed.
SCOPE.  One cell (C2, Tp = 4) and one testbed.  The envelope over Tp is F12, where the ordering
reverses at Tp = 2.  Panels (a), (d) and the N = 4e4 column of (c) use checkpoints whose D1 siblings
FAIL the pre-registered GC gate (0.243 at N = 1e4, 0.167 at N = 4e4); §6d registered those points in
advance as budget-axis measurements rather than arm results.  The rightmost point of (b) and the
N = 1.6e5 curve of (c) use the gate-passing checkpoint: """ + GATE_LINE_PASS + """
""")


if __name__ == "__main__":
    for f in (fig15,):
        try:
            print("  ok  ", f())
        except Exception as ex:
            import traceback
            traceback.print_exc()
            print("  FAIL", f.__name__, type(ex).__name__, ex)
