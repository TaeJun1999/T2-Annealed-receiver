"""conf/code/figure_f20.py -- F20: the learned prior across channel models (cell C2, 8x4, T=16, Tp=4, equal budget 1.6e5).
Report figure; every number straight from the raw files (read-only), asserted against the committed records
(NEXT_EXPERIMENTS_{D3B16e4,SVB16e4,38901}.md §6, frozen eee1d669; headline raw_B16e4k).

(a) SNR@0.1 gap b* - V1 (positive = the diffusion prior V1 needs less SNR for BLER 0.1), 90% PAIRED bootstrap
    (analysis.gain: exp_0925 rule, seed 20260925), per testbed, with the registered table-B label of each measurement tag:
    D2 sparse specular (headline, D1-sibling gate PASS), D3 = D2 geometry with CN path gains, SV8e clustered Saleh-Valenzuela,
    3GPP TR 38.901 UMi 28 GHz (main standard-model point) and MIX3 (UMi28+UMa28+RMa3.5; registered report-only side point).
    D3 / SV8e / 38.901 checkpoints are UNGATED (measurement, not an arm verdict).
(b) BLER@16 vs SNR on 3GPP 38.901 UMi 28 GHz (raw_U28B16e4): b*, V1, the Gaussian prior R2 and the genie; 95% Wilson.
(c) genie-gap recovery R = (b* - V1)/(b* - genie) at -3 dB, 90% paired bootstrap (recovery_ci.py, seed 20260926), per testbed.
Writes figs/F20_channel_models.{pdf,png,txt}.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from analysis import load_raw, gain, wilson
from recovery_ci import fails, boot, rec
from figstyle import INK, INK2, SHADE, V1, GMM, GENIE, GAUSS

plt.rcParams.update({"font.size": 8, "axes.labelsize": 8.5, "axes.titlesize": 8.5, "legend.fontsize": 8,
                     "xtick.labelsize": 8, "ytick.labelsize": 8, "axes.grid": True, "grid.alpha": 0.25,
                     "figure.dpi": 200, "savefig.bbox": "tight", "savefig.pad_inches": 0.02,
                     "text.color": INK, "axes.labelcolor": INK, "axes.titlecolor": INK,
                     "xtick.labelcolor": INK, "ytick.labelcolor": INK})
FIG = os.path.join(C.CONF, "figs")
BS, V1A, GE, R2 = "M-ours-bstar", "M-ours-dscore-C-V1", "R5-genie", "R2-ours-G"
# (label, raw tag, prior, table-B label as registered, record gap (est, lo, hi), record R(-3 dB) (R, lo, hi), note)
TB = [("D2 sparse specular\n(headline)", "B16e4k", "S2", "(i) 3/3", (1.41, 1.22, 1.64), (0.470, 0.427, 0.512), "gate PASS"),
      ("D3: D2 with CN\npath gains", "D3B16e4", "S2c", "(i) 3/3", (1.41, 1.19, 1.67), (0.367, 0.335, 0.399), "UNGATED"),
      ("SV8e clustered\nSaleh–Valenzuela", "SVB16e4", "SV8e", "(iv) underpowered", (0.25, 0.16, 0.33), (0.143, 0.095, 0.188), "UNGATED"),
      ("3GPP 38.901\nUMi 28 GHz", "U28B16e4", "UMi28", "(i) 3/3", (0.60, 0.33, 0.87), (0.062, 0.033, 0.089), "UNGATED"),
      ("3GPP 38.901 MIX3\n(side point)", "MXB16e4", "MIX3", "(i) 3/3, report-only", (0.98, 0.68, 1.31), (0.090, 0.062, 0.117), "UNGATED")]


def main():
    fig = plt.figure(figsize=(7.16, 2.85), layout="constrained")
    gs = fig.add_gridspec(1, 3, width_ratios=[1.25, 1, 0.95])
    a1, a2, a3 = (fig.add_subplot(gs[i]) for i in range(3))
    txt = ["F20 -- the learned prior across channel models, cell C2 (8x4, T=16, Tp=4), equal budget N_train = 1.6e5 "
           "(GMM fit and diffusion training on the SAME channel set), test trials 0..2559.  Numbers recomputed from raw by "
           "code/figure_f20.py (read-only) and asserted against the registration records.", ""]
    gaps, recs = [], []
    for lab, tag, prior, lb, rg, rr, note in TB:
        d, meta, _ = load_raw("D2", root=os.path.join(C.CONF, f"raw_{tag}"))
        snrs = sorted(k[2] for k in d if k[0] == "C2")
        g = gain(d, "C2", prior, snrs, BS, V1A)
        assert (round(g["est"], 2), round(g["lo"], 2), round(g["hi"], 2)) == rg, (tag, g)
        b, v, ge = (fails(d, "C2", -3.0, a) for a in (BS, V1A, GE))
        r = rec(b, v, ge); (lo, hi), nn = boot([(b, v, ge)], 2000, 20260926)
        assert (round(r, 3), round(lo, 3), round(hi, 3)) == rr and nn == 0, (tag, r, lo, hi)
        m = meta[("C2", prior)]
        gaps.append(g); recs.append((r, lo, hi))
        txt.append(f"  {lab.replace(chr(10), ' '):<34} raw_{tag:<9} b* {('kron K=' + str(m['kron_K'])) if m['bstar'] == 'kron' else ('full K=' + m['bstar'][3:])}  table B b*->V1 {lb} ({note});  "
                   f"SNR@0.1 gap b*-V1 {g['est']:+.2f} dB [90% {g['lo']:+.2f}, {g['hi']:+.2f}];  -3 dB failures b* {int(b.sum())} "
                   f"V1 {int(v.sum())} genie {int(ge.sum())}, R = {r:.3f} [90% {lo:.3f}, {hi:.3f}]")

    # ---------------- (a) gap per testbed ----------------
    y = np.arange(len(TB))[::-1]
    for yi, (lab, tag, prior, lb, rg, rr, note), g in zip(y, TB, gaps):
        side = "side" in lab
        a1.errorbar(g["est"], yi, xerr=[[g["est"] - g["lo"]], [g["hi"] - g["est"]]], color=V1["color"], marker=V1["marker"],
                    ms=4.5, capsize=2, elinewidth=1.0, ls="none", mfc="white" if side else V1["color"], zorder=3)
        a1.text(g["hi"] + 0.07, yi, lb, va="center", ha="left", fontsize=7, color=INK2)
    a1.axvline(0, color=INK, lw=0.8)
    a1.axhspan(3.5, 4.5, color=SHADE, zorder=0, lw=0)
    a1.set_yticks(y, [t[0] for t in TB], fontsize=7.2)
    a1.set_xlim(-0.2, 2.75); a1.set_ylim(-0.6, len(TB) - 0.4)
    a1.set_xlabel(r"SNR@0.1 gap $b^*-$V1 [dB] (> 0: V1 better)")
    a1.set_title("(a) V1 vs equal-budget GMM $b^*$,\nper channel model (90% paired CI)", fontsize=8.5)
    a1.grid(axis="y", visible=False)

    # ---------------- (b) UMi28 BLER curves ----------------
    d, meta, _ = load_raw("D2", root=os.path.join(C.CONF, "raw_U28B16e4"))
    snrs = sorted(k[2] for k in d if k[0] == "C2")
    txt += ["", "(b) 3GPP 38.901 UMi 28 GHz (raw_U28B16e4, V1 = _best weights), failures / 2560 per SNR "
            + " ".join(f"{s:+.0f}" for s in snrs) + " dB:"]
    for arm, sty, lab in ((R2, GAUSS, "Gaussian prior (R2)"), (BS, GMM, r"GMM prior $b^*$"), (V1A, V1, "V1 (proposed)"),
                          (GE, GENIE, "genie")):
        k = np.array([fails(d, "C2", s, arm).sum() for s in snrs]); n = 2560
        ci = np.array([wilson(int(a), n) for a in k]); p = k / n; ok = k > 0
        a2.errorbar(np.array(snrs)[ok], p[ok], yerr=[p[ok] - ci[ok, 0], ci[ok, 1] - p[ok]], color=sty["color"],
                    marker=sty["marker"], ls=sty["ls"], lw=1.1, ms=(4 if sty["marker"] != "*" else 6.5), capsize=1.5,
                    elinewidth=0.8, label=lab, zorder=4 if arm == V1A else 3)
        txt.append(f"  {arm:<20} " + " ".join(str(int(a)) for a in k))
    a2.set_yscale("log"); a2.set_ylim(2e-4, 1.0); a2.set_xticks(range(-3, 16, 3)); a2.set_xlabel("SNR [dB]")
    a2.set_ylabel("BLER (16 outer iterations)")
    a2.set_title("(b) BLER on 3GPP 38.901\nUMi 28 GHz (UNGATED)", fontsize=8.5)
    a2.legend(loc="lower left", frameon=False, fontsize=6.8, handlelength=2.0)

    # ---------------- (c) recovery ----------------
    for yi, (lab, tag, prior, lb, rg, rr, note), (r, lo, hi) in zip(y, TB, recs):
        side = "side" in lab
        a3.errorbar(r, yi, xerr=[[r - lo], [hi - r]], color=INK, marker="o", ms=4, capsize=2, elinewidth=1.0, ls="none",
                    mfc="white" if side else INK, zorder=3)
        a3.text(hi + 0.02, yi, f"{r:.2f}", va="center", ha="left", fontsize=7, color=INK2)
    a3.axhspan(3.5, 4.5, color=SHADE, zorder=0, lw=0)
    a3.set_yticks(y, ["" for _ in TB]); a3.set_ylim(-0.6, len(TB) - 0.4); a3.set_xlim(0, 0.62)
    a3.set_xlabel(r"recovery $R$ at −3 dB")
    a3.set_title("(c) $b^*$→genie gap closed\nby V1, −3 dB (90% CI)", fontsize=8.5)
    a3.grid(axis="y", visible=False)

    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(FIG, f"F20_channel_models.{ext}"))
    txt += ["", "Registered readings (not a new test): Delta R = R(testbed) - R(D2), -3 dB, unpaired 90%: D3 -0.104 [-0.156, "
            "-0.049], SV8e -0.327 [-0.392, -0.262], UMi28 -0.408 [-0.458, -0.358] (all 'lower than D2'); MIX3 -0.380 "
            "(report-only).  Joint boundary reading (38901 §2.3): SV8e (iv) x UMi28 (i) = 'undecided'.  The registered "
            "38.901 prediction ('no V1 advantage') missed.",
            "Caveats: D3/SV8e/38.901 checkpoints are UNGATED (measurement, not an arm verdict); one diffusion seed per testbed "
            "(seed repeats registered in NEXT_EXPERIMENTS_SEEDS16e4); b* of D3/UMi28/MIX3 is kron K=4096 at the grid edge with "
            "a tol-rule convergence caveat; testbeds are not paired with D2 (different streams)."]
    open(os.path.join(FIG, "F20_channel_models.txt"), "w").write("\n".join(txt) + "\n")
    print("\n".join(txt))


if __name__ == "__main__":
    main()
