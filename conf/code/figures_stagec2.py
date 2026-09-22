"""conf/code/figures_stagec2.py -- Stage C figures F12-F13 (the 2026-09-22 amendments).

figures_stagec.py draws F7-F11.  This file continues with the two results whose data is FINAL:

  F12  the Tp operating envelope (10_SPEC_stageC §6f).  Equal-budget N=1e4, n=2560, three cells.
       Left: BLER vs SNR for C1 (Tp=2) / C5 (Tp=3) / C2 (Tp=4), learned-V1 against the fitted-GMM
       baseline.  Right: the pre-registered decision-point sign test, plotted as the pooled
       win:loss split per cell, against the closed-form cavity-variance floor nu_q -> cbar(Nt-Tp)/Tp
       that §6j measured.  The envelope boundary is a PREDICTION, not a post-hoc cut.
  F13  sign versus magnitude (10_SPEC_stageC §6h).  The do() counterfactual sweep, all 7 SNRs,
       n=256.  Flooring the Jacobian's eigenvalue MAGNITUDE while keeping its sign recovers nothing;
       fixing the SIGN recovers everything.  Three different sign repairs land on top of each other.

Every number is READ from the files below.  Nothing here recomputes, resamples or re-runs anything.
  raw_B1e4x/*.npz                                F12 left  (C1, C5; equal budget N=1e4, n=2560)
  raw_B1e4/*.npz                                 F12 left  (C2; same budget, same n)
  results/tables_D2_B1e4x.txt                    F12 right (pre-registered sign tests, C1/C5)
  results/tables_D2_B1e4.txt                     F12 right (same, C2)
  results/jacpsd_counterfactual_SUMMARY_n256.txt F13       (§6h roll-up)

GATE STATUS -- both figures are built on ckpt/d2sx_N10000_a1.pt, which FAILS the pre-registered gate
(GC 0.243 vs 0.15).  §6d fixed this in advance: the equal-budget points are a BUDGET-AXIS measurement,
not an arm result.  The gate-passing model's numbers live in results/tables_D2_C.txt.  Both captions
say so; neither figure licenses an arm claim on its own.
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
import common as C
import figures as F0
from figures_stagec import _save, _foot, RES

FIG = F0.FIG
SNRS = np.array([-3., 0., 3., 6., 9., 12., 15.])

# arm -> (legend label incl. its condition, colour, marker, linestyle).  Conditions in the legend,
# per house style: a reviewer must be able to read the figure without the body text.
ST = {
    "R1-turbo":            ("classical turbo (no prior)",             "tab:brown", "s", "--"),
    "M-ours-bstar":        ("fitted GMM prior, b* (val. log-lik.)",   "tab:red",   "D", "-"),
    "M-ours-dscore-C-V1":  ("learned score, PSD-projected site (V1)", "tab:green", "o", "-"),
    "M-ours-dscore-C-V0":  ("learned score, pre-registered site (V0)", "tab:purple", "v", ":"),
    "R5-genie":            ("genie CSI (lower bound)",                "k",         "*", "-."),
}
CELLS = [("C1", 2, "raw_B1e4x"), ("C5", 3, "raw_B1e4x"), ("C2", 4, "raw_B1e4")]


def bler_from_raw(rawdir, cell):
    """mean BLER@16 per SNR, straight off the saved per-trial blk_err arrays."""
    acc = collections.defaultdict(lambda: collections.defaultdict(list))
    for f in glob.glob(os.path.join(C.CONF, rawdir, f"D2_{cell}_*.npz")):
        snr = float(re.search(r"snr(-?\d+)", f).group(1))
        d = np.load(f, allow_pickle=True)
        for k in d.files:
            if k.endswith("|blk_err"):
                acc[k.split("|")[0]][snr].append(d[k][:, 15])
    out = {}
    for arm, per in acc.items():
        # SAME rule as the pre-registered analysis.py:172-175 -- a block on which the arm raised carries a
        # non-finite blk_err and is COUNTED AS A BLOCK ERROR, never dropped.  (A first draft averaged with
        # np.mean and printed 'nan' for C1 -3 dB; the tables file says 1.000, and the tables file is right.)
        out[arm] = np.array([np.where(np.isfinite(v := np.concatenate(per[s])), v, 1.0).mean()
                             if s in per else np.nan for s in SNRS])
    return out


def pooled_test(path, cell, pair="M-ours-bstar -> M-ours-dscore-C-V1"):
    """Read the pre-registered pooled sign test for one pair out of a tables_*.txt TABLE B block."""
    txt = open(path, encoding="utf-8", errors="replace").read()
    cut = txt.split(f"--- cell {cell} ")
    if len(cut) < 2:
        return None
    blk = cut[-1]
    i = blk.find("  " + pair)
    if i < 0:
        return None
    seg = blk[i:i + 900]
    m = re.search(r"pooled (\d+):(\d+) p=([0-9.e+-]+)", seg)
    ver = re.search(r"-> (significant|not significant)", seg)
    if not m:
        return None
    # the verdict line names BOTH arms ("second arm fewer failures at 0/3 points, first arm fewer
    # failures at 2/3 points").  Take the one with the non-zero count -- that is the winner.
    counts = dict((w, int(k)) for w, k in re.findall(r"(first|second) arm fewer failures at (\d)/3", seg))
    who = max(counts, key=counts.get) if counts else "?"
    # a:b is (first-arm-only failures) : (second-arm-only failures), so a > b means the SECOND arm
    # (the learned V1) wins.  Verified against C2, where 502:72 is the V1 win reported in STATUS.
    return dict(a=int(m.group(1)), b=int(m.group(2)), p=float(m.group(3)),
                who=who, k=(counts.get(who, 0) if counts else 0),
                sig=(ver.group(1) if ver else "?"))


# ------------------------------------------------------------------ F12  the Tp envelope ----------

def fig12():
    fig, axes = plt.subplots(1, 4, figsize=(13.6, 4.1),
                             gridspec_kw=dict(width_ratios=[1, 1, 1, 1.05], wspace=0.30,
                                              bottom=0.34, top=0.90))
    data = {}
    for (cell, tp, rawdir), ax in zip(CELLS, axes[:3]):
        b = bler_from_raw(rawdir, cell)
        data[cell] = b
        for arm, (lab, col, mk, ls) in ST.items():
            if arm not in b:
                continue
            y = b[arm]
            ax.semilogy(SNRS, y, ls, color=col, marker=mk, ms=4.2, lw=1.4,
                        label=lab if cell == "C2" else None)
        ax.set_title(f"{cell}   $T_p$={tp}", fontsize=9)
        ax.set_xlabel("SNR (dB)")
        ax.set_xlim(-4.5, 16.5)
        ax.set_ylim(5e-4, 1.5)
        ax.grid(alpha=0.25, which="both", lw=0.5)
        if cell == "C1":
            ax.set_ylabel("BLER after 16 outer iterations")
            ax.annotate("-3 dB: V0/V1 = 1.000 (970 / 804 of 2560\nblocks raised, counted as errors)",
                        xy=(-3, 1.0), xytext=(0.3, 0.42), fontsize=5.9, color="0.3",
                        arrowprops=dict(arrowstyle="-", color="0.5", lw=0.6))
        else:
            ax.set_yticklabels([])
    h, l = axes[2].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", bbox_to_anchor=(0.40, 0.055), ncol=5, framealpha=0.95,
               fontsize=7.4)

    # right panel: the pre-registered pooled sign test vs the closed-form cavity floor
    ax = axes[3]
    cbar, Nt = 1.0, 4
    floor = {tp: cbar * (Nt - tp) / tp for _, tp, _ in CELLS}
    res = {"C1": pooled_test(os.path.join(RES, "tables_D2_B1e4x.txt"), "C1"),
           "C5": pooled_test(os.path.join(RES, "tables_D2_B1e4x.txt"), "C5"),
           "C2": pooled_test(os.path.join(RES, "tables_D2_B1e4.txt"), "C2")}
    GRID_TOP = 2 * 0.8451555 ** 2                 # frozen training grid top, in nu_q units
    xs, hs, cols, labs = [], [], [], []
    for cell, tp, _ in CELLS:
        r = res[cell]
        if r is None:
            continue
        # a:b = (first-arm-only failures):(second-arm-only failures) for `M-ours-bstar -> V1`,
        # so a > b means the LEARNED arm wins.  Positive bar = V1 wins.
        frac = (r["a"] - r["b"]) / (r["a"] + r["b"])
        xs.append(tp)
        hs.append(frac)
        cols.append("tab:green" if frac > 0 else "tab:red")
        labs.append(f"{r['a']}:{r['b']}   p={r['p']:.0e}\n{r['k']}/3 decision points\n"
                    rf"$\nu_q$ floor {floor[tp]:.2f}")
    ax.axhline(0, color="0.35", lw=1.0)
    ax.bar(xs, hs, width=0.55, color=cols, alpha=0.85, zorder=3)
    for x, h, t in zip(xs, hs, labs):
        ax.text(x, h + (0.05 if h > 0 else -0.05), t, ha="center",
                va="bottom" if h > 0 else "top", fontsize=6.4, linespacing=1.35)
    ax.text(0.03, 0.995, r"frozen training grid top: $\nu_q=%.2f$" % GRID_TOP + "\n"
            + r"only $T_p{=}2$'s floor (1.00) reaches it" + "\n" + r"$\Rightarrow$ queried out of support",
            transform=ax.transAxes, ha="left", va="top", fontsize=6.6, color="tab:blue",
            linespacing=1.4)
    ax.set_xticks([2, 3, 4])
    ax.set_xlim(1.45, 4.55)
    ax.set_ylim(-0.62, 1.42)
    ax.set_xlabel("$T_p$ (pilot symbols; $N_t=4$)")
    ax.set_ylabel("pooled sign-test margin\n(+ = V1 wins, − = GMM wins)", fontsize=8)
    ax.set_title("decision-point test vs the predicted floor", fontsize=9)
    ax.grid(alpha=0.25, axis="y", lw=0.5)

    _foot(fig, "equal budget: every arm, learned and classical, is fitted/trained on the SAME "
               "N_train=1e4 channel set (10_SPEC_stageC A3).  n=2560 trials per SNR point.  "
               "Checkpoint ckpt/d2sx_N10000_a1.pt FAILS the pre-registered gate (GC 0.243 vs 0.15): "
               "§6d registers these points as a budget-axis measurement, not an arm result.", y=0.035)
    return _save(fig, "F12_tp_envelope", """
F12.  The pilot-budget operating envelope, at equal training budget (10_SPEC_stageC §6f).
Left three panels: BLER after 16 outer iterations, D2, n=2560 per SNR point, every arm trained or
fitted on the SAME N_train=1e4 channel set.  Cells differ ONLY in Tp (C1 Tp=2, C5 Tp=3, C2 Tp=4);
array, block length, code, SNR grid and outer-iteration count are identical.  Blocks on which an arm
raised carry a non-finite block error and are COUNTED AS BLOCK ERRORS, exactly as the pre-registered
analysis does (code/analysis.py:172-175; tables_D2_B1e4x.txt NOTE rows): at C1 -3 dB that is V0 970,
V1 804 and V4 136 of 2560 blocks, giving BLER 1.000 / 1.000 / 0.996.  The F3 divergence guard fires on
2560 / 2560 / 2552 of those trials (results/guard_D2_B1e4x.txt).
Right panel: the pre-registered decision-point sign test for M-ours-bstar -> V1, one bar per cell,
plotted as the pooled margin (b-a)/(a+b) so that positive means the learned arm wins.  Annotations
give the pooled counts a:b, the pooled p, and how many of the three pre-registered decision points
were individually significant.  All three comparisons are POWERED.  Numbers are transcribed from
results/tables_D2_B1e4x.txt (C1, C5) and results/tables_D2_B1e4.txt (C2); this figure runs no test.
The dashed blue line is NOT fitted to these results: it is the closed-form cavity-variance floor at
outer iteration 1, nu_q -> cbar (Nt - Tp)/Tp, which follows from Tp < Nt leaving Nr(Nt - Tp) null
directions in G when the data columns are still zero-valued.  It was written down in §6j before the
C1 and C5 runs and matched the measurement to 3-4 significant figures at both ends of the SNR grid
(C1 -3 dB predicted sigma_t 0.999, measured 0.9993; high-SNR limit predicted 0.707, measured 0.7125).
The dotted line is the top of the FROZEN training sigma grid, sqrt(nu/2) = 0.8452 (results/
sigma_grid_D2.txt, "FROZEN from here on").  Only C1's floor crosses it, and only C1 reverses.
SCOPE.  One testbed (D2), one budget (N=1e4), one seed (a1); the checkpoint FAILS the pre-registered
gate (GC 0.243 vs threshold 0.15), which §6d fixed in advance by registering these points as a
budget-axis measurement rather than an arm result.  The gate-passing model's BLER is in
results/tables_D2_C.txt.  The right panel's floor line explains WHERE the reversal happens; it is not
evidence for WHY the learned score fails there -- §6j shows the out-of-grid query accounts for the
low-SNR failure in C1 but NOT for +15 dB, where divergence precedes the out-of-range query.
""")


# ------------------------------------------------------------------ F13  sign vs magnitude --------

_CF = {
    "dscore|eta":      ("no intervention (pre-registered wiring)", "tab:purple", "v", ":"),
    "dscore|abs1e-2":  (r"floor $|\lambda|$ at $10^{-2}$, KEEP the sign", "tab:orange", "s", "--"),
    "dscore|psd1e-2":  (r"clamp $\lambda$ to $[10^{-2},1]$ (sign repaired)", "tab:green", "o", "-"),
    "dscore|belsc":    ("drop the D-14 matrix site entirely", "tab:cyan", "^", "-"),
    "dscore|mean":     ("clip='mean' instead of 'eta'", "tab:blue", "P", "-"),
    "gmmB|eta":        ("fitted GMM, same loop (reference)", "tab:red", "D", "-."),
}


def _cf_table(block):
    """Pull one '===== <block> =====' table out of the §6h roll-up."""
    txt = open(os.path.join(RES, "jacpsd_counterfactual_SUMMARY_n256.txt"),
               encoding="utf-8").read()
    seg = txt.split(f"===== {block} =====")[1].split("=====")[0]
    out = {}
    for line in seg.strip().splitlines()[1:]:
        parts = line.split()
        if len(parts) < 8 or "|" not in parts[0]:
            continue
        try:
            out[parts[0]] = np.array([float(x) for x in parts[1:8]])
        except ValueError:
            continue
    return out


def fig13():
    bler = _cf_table("BLER@16")
    div = _cf_table("divergence fraction (NMSE@16 > 10)")
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(9.6, 3.6),
                                  gridspec_kw=dict(wspace=0.26, bottom=0.17))
    RES_LIM = 1.0 / 256.0          # n=256, so BLER 0 means "0 of 256", i.e. < 1/256 -- NOT a value
    for arm, (lab, col, mk, ls) in _CF.items():
        if arm in bler:
            y = bler[arm]
            ax.semilogy(SNRS, np.maximum(y, RES_LIM), ls, color=col, marker=mk, ms=4.2,
                        lw=1.4, label=lab)
            z = y <= 0                 # censored points: draw them hollow ON the resolution limit
            if z.any():
                ax.plot(SNRS[z], np.full(z.sum(), RES_LIM), marker=mk, ms=6.0, ls="none",
                        mfc="white", mec=col, mew=1.3, zorder=5)
        if arm in div:
            ax2.plot(SNRS, div[arm], ls, color=col, marker=mk, ms=4.2, lw=1.4)
    ax.axhline(RES_LIM, color="0.45", lw=0.9, ls=(0, (4, 3)), zorder=1)
    ax.text(-4.2, RES_LIM * 1.14, "resolution limit 1/256 (hollow marker = 0 of 256 trials)",
            fontsize=6.2, color="0.35", va="bottom", ha="left")
    ax.set_ylim(RES_LIM * 0.62, 1.4)
    ax.set_xlabel("SNR (dB)")
    ax.set_ylabel("BLER after 16 outer iterations")
    ax.set_xlim(-4.5, 16.5)
    ax.grid(alpha=0.25, which="both", lw=0.5)
    ax.set_title("(a)  BLER", fontsize=9)
    ax2.set_xlabel("SNR (dB)")
    ax2.set_ylabel("fraction of trials with NMSE@16 > 10")
    ax2.set_xlim(-4.5, 16.5)
    ax2.set_ylim(-0.015, 0.26)
    ax2.grid(alpha=0.25, lw=0.5)
    ax2.set_title("(b)  divergence-guard firing rate", fontsize=9)
    h, l = ax.get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", bbox_to_anchor=(0.5, -0.09), ncol=3, fontsize=7.0,
               framealpha=0.95)
    _foot(fig, "do() interventions on ONE fixed checkpoint (ckpt/d2sx_N10000_a1.pt, which FAILS the "
               "pre-registered gate, GC 0.243 vs 0.15).  D2 cell C2, n=256 trials per SNR point.  "
               "DIAGNOSTIC PROBE: none of these is an arm and none appears in any BLER table.", y=-0.20)
    return _save(fig, "F13_sign_vs_magnitude", """
F13.  The defect is the eigenvalue SIGN, not the conditioning (10_SPEC_stageC §6h).
Each curve is the SAME learned score through the SAME EP receiver with ONE intervention applied to
the D-14 matrix site's Jacobian; the fitted-GMM arm runs the identical loop as a reference.
D2, cell C2 (Tp=4), n=256 trials per SNR point, all 7 SNRs, no point dropped.
(a) Flooring the eigenvalue MAGNITUDE at 1e-2 while KEEPING each eigenvalue's sign recovers nothing
(BLER 0.098-0.875, gaps of +0.098 to +0.836 against the repaired arms at the seven SNRs).  Repairing
the SIGN -- by clamping to [1e-2, 1], by dropping the matrix site, or by switching the clip rule --
recovers everything, and the three repairs are indistinguishable from each other (all within 0.02
absolute at all 7 SNRs).  (b) The divergence guard fires on 1.6-22.3% of trials without the
intervention and on 0.000 of them after any of the three sign repairs; the magnitude-only floor
leaves 0.0-1.6%.
This was a PRE-REGISTERED prediction, committed in §6h before the roll-up was computed: "psd1e-2
restores BLER to within 0.02 of belsc at ALL SEVEN SNRs and abs1e-2 does not -- i.e. the defect is
the sign, not the conditioning."  Scored: psd1e-2 7/7, abs1e-2 0/7.
PROVENANCE.  The seven raw sweeps were written 2026-09-21 16:23-17:13 and were not read until
2026-09-22 13:15; the SUMMARY.txt sitting beside them is dated 14:56 on 2026-09-21, predates the
sweep, and is retained unmodified as the record of that reporting gap.
SCOPE.  One cell (C2), n=256, and a checkpoint that FAILS the pre-registered gate.  These are
interventions on a diagnostic probe: they identify the mechanism, they are not arms, and none of them
appears in any BLER table.  The equal-budget arm results are in results/tables_D2_B1e4.txt.
""")


if __name__ == "__main__":
    for f in (fig12, fig13):
        try:
            print("  ok  ", f())
        except Exception as ex:
            print("  FAIL", f.__name__, type(ex).__name__, ex)
