"""conf/code/figure_f22.py -- F22: the learned prior used once on the pilots vs inside the turbo loop (report figure, read-only).

NEXT_EXPERIMENTS_PILOT16e4 (frozen 92d26757, results §6.1): the Arvinte–Tamir-type SETTING (learned prior used once on the
pilots, channel estimate frozen, 16 detection/decoding iterations) rebuilt with the SAME V1 weights, GMM b* fits and trials
as each base tag -- not a reproduction of the original Langevin estimator.  One panel per dataset, BLER@16 vs SNR, n = 2560:
pilot-only Gaussian (R0-pilot), pilot-only GMM (bstar-pilot), pilot-only V1 (V1-pilot) -- dashed, hollow markers -- and the
loop b*, loop V1 -- solid, filled -- plus the genie.  Colour = prior (Gaussian grey, GMM orange, V1 blue; code/figstyle.py),
line style + fill = pilot-only vs loop, so identity is never colour alone.  Base raws hold the loop arms and R0-pilot, the
PIL* raws the two pilot-only learned/GMM arms (same trial streams).  -3 dB values asserted against §6.1.  Zero-failure
points are omitted from the log axis and listed in the .txt.  Writes figs/F22_pilot_only.{pdf,png,txt}.
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
from figstyle import INK, V1, GMM, GENIE, GAUSS

plt.rcParams.update({"font.size": 8, "axes.labelsize": 8.5, "axes.titlesize": 8.5, "legend.fontsize": 7.5,
                     "xtick.labelsize": 7.5, "ytick.labelsize": 7.5, "axes.grid": True, "grid.alpha": 0.25,
                     "figure.dpi": 200, "savefig.bbox": "tight", "savefig.pad_inches": 0.02,
                     "text.color": INK, "axes.labelcolor": INK, "axes.titlecolor": INK,
                     "xtick.labelcolor": INK, "ytick.labelcolor": INK})
FIG = os.path.join(C.CONF, "figs")
# (arm, source 'base'|'pil', legend label, style, dashed pilot-only?)
ARMS = [("R0-pilot", "base", "pilot-only, Gaussian prior (R0)", GAUSS, True),
        ("bstar-pilot", "pil", r"pilot-only, GMM prior $b^*$", GMM, True),
        ("V1-pilot", "pil", "pilot-only, diffusion prior V1", V1, True),
        ("M-ours-bstar", "base", r"turbo loop, GMM prior $b^*$", GMM, False),
        ("M-ours-dscore-C-V1", "base", "turbo loop, diffusion prior V1 (proposed)", V1, False),
        ("R5-genie", "base", "known-channel reference (genie)", GENIE, False)]
# (title, base tag, pilot tag, cell, prior, §6.1 -3 dB BLER@16 of (bstar-pilot, V1-pilot) asserted)
SETS = [("(a) D2 sparse specular, 8×4 (headline)", "B16e4k", "PILB16e4k", "C2", "S2", (0.382, 0.245)),
        ("(b) D2 sparse specular, 16×4 (C6)", "NR16B16e4", "PILNR16", "C6", "S2", (0.094, 0.032)),
        ("(c) D3: D2 geometry, CN path gains", "D3B16e4", "PILD3", "C2", "S2c", (0.606, 0.521)),
        ("(d) SV8e: clustered Saleh–Valenzuela", "SVB16e4", "PILSV", "C2", "SV8e", (0.341, 0.314)),
        ("(e) 3GPP 38.901 UMi 28 GHz", "U28B16e4", "PILU28", "C2", "UMi28", (0.638, 0.616)),
        ("(f) 3GPP 38.901 MIX3 (side point)", "MXB16e4", "PILMX", "C2", "MIX3", (0.670, 0.648))]


def fails(d, key, arm):
    return np.nan_to_num(np.asarray(d[key][arm]["blk_err"])[:, -1], nan=1.0)   # a raised block is a failure


def main():
    fig, axs = plt.subplots(2, 3, figsize=(7.16, 5.0), sharex=True, sharey=True, layout="constrained")
    txt = ["F22 -- learned prior used once on the pilots (Arvinte–Tamir-type setting, same V1 weights / GMM fits / trials) vs "
           "inside the turbo loop; NEXT_EXPERIMENTS_PILOT16e4 §6.1; BLER@16, n = 2560 per SNR.  Recomputed from raw by "
           "code/figure_f22.py (read-only).", ""]
    handles = {}
    for ax, (title, tb, tp, cell, prior, rec3) in zip(axs.flat, SETS):
        src = {"base": load_raw("D2", root=os.path.join(C.CONF, f"raw_{tb}"))[0],
               "pil": load_raw("D2", root=os.path.join(C.CONF, f"raw_{tp}"))[0]}
        keys = sorted((k for k in src["pil"] if k[:2] == (cell, prior)), key=lambda k: k[2])
        snrs = np.array([k[2] for k in keys])
        k3 = [k for k in keys if k[2] == -3.0][0]
        got = tuple(round(float(fails(src["pil"], k3, a).mean()), 3) for a in ("bstar-pilot", "V1-pilot"))
        assert got == rec3, (tp, got, rec3)
        txt.append(f"{title} -- raw_{tb} + raw_{tp}, cell {cell}, prior {prior}.  Failures / 2560 at SNR "
                   + " ".join(f"{s:+.0f}" for s in snrs) + " dB:")
        zeros = []
        for arm, s, lab, sty, pil in ARMS:
            k = np.array([fails(src[s], key, arm).sum() for key in keys]); p = k / 2560.0; ok = k > 0
            h, = ax.plot(snrs[ok], p[ok], color=sty["color"], marker=sty["marker"], ls="--" if pil else sty["ls"],
                         lw=1.0 if pil else 1.5, ms=5.5 if sty["marker"] == "*" else 3.4,
                         mfc="white" if pil else sty["color"], mew=0.9, zorder=4 if "V1" in arm else 3)
            handles.setdefault(lab, h)
            zeros += [f"{arm} {x:+.0f}" for x, z in zip(snrs, ok) if not z]
            txt.append(f"    {arm:<20}" + " ".join(f"{int(x):5d}" for x in k))
        txt.append("    zero-failure points (not drawn on the log axis): " + ("; ".join(zeros) if zeros else "none"))
        ax.set_title(title, fontsize=8)
        ax.set_yscale("log"); ax.set_ylim(2e-4, 1.05); ax.set_xticks(range(-3, 16, 3))
    for ax in axs[1]:
        ax.set_xlabel("SNR [dB]")
    for ax in axs[:, 0]:
        ax.set_ylabel("BLER")
    labs = [a[2] for a in ARMS]
    fig.legend([handles[l] for l in labs], labs, loc="outside lower center", ncol=3, frameon=False, columnspacing=1.2,
               handlelength=2.6)
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(FIG, f"F22_pilot_only.{ext}"))
    txt += ["", "Registered labels (§6.1): primary D2 C2 -- P1 V1-pilot -> loop V1 (i), P2 bstar-pilot -> V1-pilot (i); "
            "measurement: P1 (i) at D3, UMi28, MIX3, (iv) at C6, SV8e (two decision points); P2 (i) at all six.  "
            "P1 cannot separate data-aided re-estimation from repeated prior application (16 vs 1 Module H passes).  "
            "Not a reproduction of the Langevin estimator of Arvinte & Tamir."]
    open(os.path.join(FIG, "F22_pilot_only.txt"), "w").write("\n".join(txt) + "\n")
    print("\n".join(txt))


if __name__ == "__main__":
    main()
