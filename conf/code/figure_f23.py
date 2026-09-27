"""conf/code/figure_f23.py -- F23: train/test channel-model mismatch (report figure, read-only).

NEXT_EXPERIMENTS_MISMATCH16e4 (frozen 92e31706, results §6.1): V1 and b* both taken from the TRAIN channel model (checkpoint,
GMM fits, sample covariance -- the same N'=1.6e5 train set) and evaluated on another TEST model's test trials; the matched
arms come from the test model's base raw (same trial streams).  Cell C2 (8x4, T=16, Tp=4), n = 2560 per SNR, BLER@16.
(a) SNR@0.1 gap b* - V1 (> 0: V1 needs less SNR), 90% paired bootstrap (analysis.gain, seed 20260925): under mismatch
    (filled, with the registered MM label) and matched on the same test model (hollow).
(b) cost of the mismatch, SNR@0.1(mismatched) - SNR@0.1(matched), for V1 and for b*, 90% paired bootstrap.
MM values asserted against §6.1.  Writes figs/F23_mismatch.{pdf,png,txt}.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from analysis import load_raw, gain
from figstyle import INK, INK2, V1, GMM

plt.rcParams.update({"font.size": 8, "axes.labelsize": 8.5, "axes.titlesize": 8.5, "legend.fontsize": 7.5,
                     "xtick.labelsize": 7.5, "ytick.labelsize": 7.5, "axes.grid": True, "grid.alpha": 0.25,
                     "figure.dpi": 200, "savefig.bbox": "tight", "savefig.pad_inches": 0.02,
                     "text.color": INK, "axes.labelcolor": INK, "axes.titlecolor": INK,
                     "xtick.labelcolor": INK, "ytick.labelcolor": INK})
FIG = os.path.join(C.CONF, "figs")
REN = {"M-ours-dscore-C-V1": "V1-mis", "M-ours-bstar": "bstar-mis"}
# (label, mismatch tag, test base raw, test prior, registered MM label, §6.1 MM gap (est, lo, hi))
PAIRS = [("D2 → D3", "MMs2s2c", "D3B16e4", "S2c", "(i)", (1.33, 1.11, 1.61)),
         ("D3 → D2", "MMs2cs2", "B16e4k", "S2", "(i)", (1.18, 1.00, 1.39)),
         ("UMi28 → MIX3", "MMu28mx", "MXB16e4", "MIX3", "(i)", (0.61, 0.33, 0.92)),
         ("MIX3 → UMi28", "MMmxu28", "U28B16e4", "UMi28", "(i)", (1.04, 0.73, 1.30)),
         ("D2 → UMi28", "MMs2u28", "U28B16e4", "UMi28", "(i)", (0.35, 0.12, 0.61)),
         ("UMi28 → D2", "MMu28s2", "B16e4k", "S2", "(i)", (0.82, 0.66, 0.99)),
         ("D2 → SV8e", "MMs2sv", "SVB16e4", "SV8e", "(iv)", (-0.11, -0.23, 0.01)),
         ("SV8e → D2", "MMsvs2", "B16e4k", "S2", "(i)", (1.00, 0.82, 1.19))]


def main():
    fig = plt.figure(figsize=(7.16, 3.0), layout="constrained")
    gs = fig.add_gridspec(1, 2, width_ratios=[1.15, 1])
    a1, a2 = fig.add_subplot(gs[0]), fig.add_subplot(gs[1])
    txt = ["F23 -- train/test channel-model mismatch (NEXT_EXPERIMENTS_MISMATCH16e4 §6.1), cell C2, n = 2560 per SNR, "
           "BLER@16; SNR@0.1 gaps in dB with 90% paired bootstrap.  Recomputed from raw by code/figure_f23.py (read-only).", ""]
    y = np.arange(len(PAIRS))[::-1]
    for yi, (lab, tag, base, prior, mm, rec) in zip(y, PAIRS):
        b, _, _ = load_raw("D2", root=os.path.join(C.CONF, f"raw_{base}"))
        m, _, _ = load_raw("D2", root=os.path.join(C.CONF, f"raw_{tag}"))
        keys = sorted((k for k in m if k[:2] == ("C2", prior)), key=lambda k: k[2])
        snrs = [k[2] for k in keys]
        data = {k: {**b[k], **{REN[a]: m[k][a] for a in REN}} for k in keys}
        g = lambda x, z: gain(data, "C2", prior, snrs, x, z)
        gm, g0 = g("bstar-mis", "V1-mis"), g("M-ours-bstar", "M-ours-dscore-C-V1")
        assert (round(gm["est"], 2), round(gm["lo"], 2), round(gm["hi"], 2)) == rec, (tag, gm)
        cv, cb = g("V1-mis", "M-ours-dscore-C-V1"), g("bstar-mis", "M-ours-bstar")
        for ax, pts in ((a1, ((gm, V1["color"], "full", 0.12), (g0, INK2, "none", -0.12))),
                        (a2, ((cv, V1["color"], "full", 0.12), (cb, GMM["color"], "full", -0.12)))):
            for r, col, fill, dy in pts:
                ax.errorbar(r["est"], yi + dy, xerr=[[r["est"] - r["lo"]], [r["hi"] - r["est"]]], color=col, marker="o",
                            ms=4, capsize=2, elinewidth=1.0, ls="none", mfc=col if fill == "full" else "white", zorder=3)
        a1.text(max(gm["hi"], g0["hi"]) + 0.06, yi, mm, va="center", ha="left", fontsize=7, color=INK2)
        f = lambda r: f"{r['est']:+.2f} [{r['lo']:+.2f}, {r['hi']:+.2f}]"
        txt.append(f"  {lab:<14} raw_{tag} x raw_{base} ({prior}): MM {mm}; gap b*-V1 mismatched {f(gm)}, matched {f(g0)}; "
                   f"cost V1 {f(cv)}, cost b* {f(cb)}")
    for ax in (a1, a2):
        ax.axvline(0, color=INK, lw=0.8); ax.set_yticks(y, [p[0] for p in PAIRS]); ax.set_ylim(-0.6, len(PAIRS) - 0.4)
        ax.grid(axis="y", visible=False)
    a2.set_yticklabels([])
    a1.set_xlim(right=1.95)
    a1.set_xlabel(r"SNR@0.1 gap $b^*-$V1 [dB] (> 0: V1 better)")
    a1.set_title("(a) V1 vs GMM $b^*$ under the SAME mismatch (filled)\nand matched on the test model (hollow)", fontsize=8.5)
    a2.set_xlabel("SNR@0.1 cost of the mismatch [dB] (> 0: worse)")
    a2.set_title("(b) mismatch cost: V1 (blue) and GMM $b^*$ (orange)", fontsize=8.5)
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(FIG, f"F23_mismatch.{ext}"))
    txt += ["", "Registered measurement labels (MM bstar-mis -> V1-mis): (i) at 7 of 8 train/test pairs, (iv) at D2 -> SV8e "
            "(two decision points).  Report-only elsewhere; no first-order test.  Only the prior side is mismatched "
            "(pilots, sigma^2 and the receiver are the test model's)."]
    open(os.path.join(FIG, "F23_mismatch.txt"), "w").write("\n".join(txt) + "\n")
    print("\n".join(txt))


if __name__ == "__main__":
    main()
