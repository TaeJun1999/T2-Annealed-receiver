"""conf/code/figure_f21.py -- F21: every baseline and the proposed V1 on every channel model (report figure, read-only).

Small multiples, one panel per dataset (core baselines only, user request 2026-09-26), all at the equal budget N_train = 1.6e5, test trials 0..2559 (n = 2560 per SNR), 16 outer
iterations, BLER@16 (R0-pilot also at iteration 1, its one-pass reading):
  D2 C2 (8x4, headline, raw_B16e4k) | D2 C6 (16x4, raw_NR16B16e4, UNGATED) | D3 (raw_D3B16e4) | SV8e (raw_SVB16e4)
  | 3GPP 38.901 UMi 28 GHz (raw_U28B16e4) | 3GPP 38.901 MIX3 (raw_MXB16e4, report-only side point)
Arms: the proposed diffusion prior V1; GMM priors b* (validation-selected K) and K=32; the Gaussian (sample-covariance) prior
R2 in the same EP receiver; the classical receivers R1-turbo, R3-bigamp (i.i.d. prior), R4-scvamp and R4-llr (interface
adaptations); pilot-only R0 (iteration 1) and pilot_C (pilot-only estimate, 16 detection iterations); the known-channel
reference (genie).  Our own ablations (V0, V4, V4b, b*-scalar) are left out of the plot and listed in the .txt.
Colour roles (code/figstyle.py): V1 blue, GMM orange, every non-learned classical receiver a neutral grey distinguished by
marker and line style (identity is never colour alone), genie ink.  Zero-failure points cannot sit on the log axis; they are
omitted and listed in the .txt.  Writes figs/F21_all_baselines.{pdf,png,txt}.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from analysis import load_raw
from figstyle import INK, INK2, V1, GMM, GENIE, GAUSS

plt.rcParams.update({"font.size": 8, "axes.labelsize": 8.5, "axes.titlesize": 8.5, "legend.fontsize": 7.5,
                     "xtick.labelsize": 7.5, "ytick.labelsize": 7.5, "axes.grid": True, "grid.alpha": 0.25,
                     "figure.dpi": 200, "savefig.bbox": "tight", "savefig.pad_inches": 0.02,
                     "text.color": INK, "axes.labelcolor": INK, "axes.titlecolor": INK,
                     "xtick.labelcolor": INK, "ytick.labelcolor": INK})
FIG = os.path.join(C.CONF, "figs")
GREY, LIGHT = "#52514e", "#a3a29d"
# (raw arm key, iteration index, legend label, colour, marker, line style, line width, filled?)
ARMS = [("R3-bigamp", -1, "BiG-AMP, i.i.d. prior (R3)", GREY, "v", "--", 1.0, False),
        ("R1-turbo", -1, "turbo receiver, LMMSE (R1)", GREY, "^", "-", 1.0, False),
        ("R2-ours-G", -1, "same EP receiver, Gaussian prior (R2)", GAUSS["color"], "o", "--", 1.1, True),
        ("M-ours-bstar", -1, r"GMM prior $b^*$ (validation-selected K)", GMM["color"], "D", "-", 1.3, True),
        ("M-ours-dscore-C-V1", -1, "diffusion prior V1 (proposed)", V1["color"], "s", "-", 1.8, True),
        ("R5-genie", -1, "known-channel reference (genie)", GENIE["color"], "*", "-.", 1.1, True)]
# not drawn (listed in the .txt): the other baselines and our ablations
ABLATIONS = ("R0-pilot", "R4-scvamp", "R4-llr", "M-ours-gmm32", "M-ours-dscore-C-V0", "M-ours-dscore-C-V4", "M-ours-dscore-C-V4b",
             "M-ours-bstar-scalar")
# (panel title, raw tag, cell, prior, status, record -3 dB failures (b*, V1, genie) asserted)
SETS = [("(a) D2 sparse specular, 8×4 (headline)", "B16e4k", "C2", "S2", "D1-sibling gate PASS", (623, 371, 87)),
        ("(b) D2 sparse specular, 16×4 (C6)", "NR16B16e4", "C6", "S2", "UNGATED", (184, 53, 22)),
        ("(c) D3: D2 geometry, CN path gains", "D3B16e4", "C2", "S2c", "UNGATED", (1298, 1000, 485)),
        ("(d) SV8e: clustered Saleh–Valenzuela", "SVB16e4", "C2", "SV8e", "UNGATED", (464, 402, 31)),
        ("(e) 3GPP 38.901 UMi 28 GHz", "U28B16e4", "C2", "UMi28", "UNGATED", (1270, 1228, 594)),
        ("(f) 3GPP 38.901 MIX3 (side point)", "MXB16e4", "C2", "MIX3", "UNGATED, report-only", (1421, 1354, 679))]


def fails(d, key, arm, it):
    v = np.asarray(d[key][arm]["blk_err"])[:, it]
    return np.where(np.isfinite(v), v, 1.0)          # a raised block is a failure (01_RULES §4)


def main():
    fig, axs = plt.subplots(2, 3, figsize=(7.16, 5.0), sharex=True, sharey=True, layout="constrained")
    txt = ["F21 -- every baseline and the proposed V1 on every channel model; equal budget N_train = 1.6e5, n = 2560 per SNR, "
           "BLER@16 unless stated.  Recomputed from raw by code/figure_f21.py (read-only).", ""]
    handles = {}
    for ax, (title, tag, cell, prior, status, rec3) in zip(axs.flat, SETS):
        d, meta, _ = load_raw("D2", root=os.path.join(C.CONF, f"raw_{tag}"))
        keys = sorted((k for k in d if k[0] == cell), key=lambda k: k[2])
        snrs = np.array([k[2] for k in keys])
        k3 = [k for k in keys if k[2] == -3.0][0]
        got = tuple(int(fails(d, k3, a, -1).sum()) for a in ("M-ours-bstar", "M-ours-dscore-C-V1", "R5-genie"))
        assert got == rec3, (tag, got, rec3)
        m = meta[(cell, prior)]
        bs = f"kron K={m['kron_K']}" if m["bstar"] == "kron" else f"full K={m['bstar'][3:]}"
        txt.append(f"{title} -- raw_{tag}, cell {cell}, prior {prior}, {status}; b* = {bs}.  Failures / 2560 at SNR "
                   + " ".join(f"{s:+.0f}" for s in snrs) + " dB:")
        zeros = []
        for arm, it, lab, col, mk, ls, lw, filled in ARMS:
            k = np.array([fails(d, key, arm, it).sum() for key in keys]); assert all(len(d[key][arm]["blk_err"]) == 2560 for key in keys)
            p = k / 2560.0; ok = k > 0
            h, = ax.plot(snrs[ok], p[ok], color=col, marker=mk, ls=ls, lw=lw, ms=(3.2 if mk not in "*" else 5.5),
                         mfc=col if filled else "white", mew=0.9, zorder=5 if "V1" in arm else 3 if arm == "M-ours-bstar" else 2)
            handles.setdefault(lab, h)
            zeros += [f"{lab.split(' (')[0]} {s:+.0f}" for s, z in zip(snrs, ok) if not z]
            txt.append(f"    {arm:<20}{'@1 ' if it == 0 else '@16'}  " + " ".join(f"{int(x):5d}" for x in k))
        for arm in ABLATIONS:
            if arm in d[keys[0]]:
                txt.append(f"    (not drawn) {arm:<20}  " + " ".join(f"{int(fails(d, key, arm, -1).sum()):5d}" for key in keys))
        txt.append("    zero-failure points (not drawn on the log axis): " + ("; ".join(zeros) if zeros else "none"))
        ax.set_title(title + f"\n({status})", fontsize=8)
        ax.set_yscale("log"); ax.set_ylim(2e-4, 1.05); ax.set_xticks(range(-3, 16, 3))
    for ax in axs[1]:
        ax.set_xlabel("SNR [dB]")
    for ax in axs[:, 0]:
        ax.set_ylabel("BLER")
    order = [a[2] for a in ARMS][::-1]                                 # proposed and strongest first in the legend
    fig.legend([handles[l] for l in order], order, loc="outside lower center", ncol=3, frameon=False, columnspacing=1.2,
               handlelength=2.6)
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(FIG, f"F21_all_baselines.{ext}"))
    txt += ["", "Only the registered comparison is tested (table B b* -> V1 per registration); every other arm is shown, "
            "not tested.  D2 C6 and every non-D2 channel model are UNGATED measurements; MIX3 is a registered report-only side "
            "point.  R3-bigamp cannot take a correlated prior (structural); R4 arms are interface adaptations of the cited "
            "method.  genie is a known-channel reference, not a bound."]
    open(os.path.join(FIG, "F21_all_baselines.txt"), "w").write("\n".join(txt) + "\n")
    print("\n".join(txt))


if __name__ == "__main__":
    main()
