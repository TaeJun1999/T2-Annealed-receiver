"""conference/figures/paper_f20.py -- paper version of conf/code/figure_f20.py (git 3f7c09ab), F20: channel models.

Same data, computation, bootstrap, asserts, colours, markers and shading as the original; only the rendered text differs:
  - channel-model tick labels, legend labels and axis labels use the paper glossary (conference/figures/TERMS.md):
    D2 -> Sparse specular, D3 -> Sparse specular, CN gains, SV8e -> Clustered SV (Saleh-Valenzuela),
    UMi28 -> 3GPP UMi 28 GHz, MIX3 -> 3GPP mixed; V1 -> Proposed, b* -> GMM prior, R2 -> Gaussian prior,
    genie -> Perfect CSI; "(headline)" / "(side point)" dropped from the tick labels (the shading and the hollow
    marker stay; their meaning goes to the caption);
  - (a): the registered table-B label annotations ("(i) 3/3", "(iv) underpowered", "(i) 3/3, report-only") are not
    drawn (markers and data unchanged);
  - panel titles removed (setup, CI levels and "UMi 28 GHz" of (b) go to the caption), only the bold panel labels
    (a), (b), (c) remain;
  - FIGHS16e4 merge (NEXT_EXPERIMENTS_FIGHS16e4 §1, report-only; fighs_merge.py): the (b) curves keep raw_U28B16e4 (n = 2560)
    at -3..+3 dB and take +6..+15 dB from n = 20480 new trials (raw_FHU28B16e4); BLER and Wilson bars with each point's own n
    (was a fixed n = 2560); zero-failure points break the curve (Perfect CSI: arrow from its own-n Wilson bound); y from 3e-5;
    merged k/n printed after the unchanged record ((a), (c) unchanged);
  - reads the raw files from conf/ (read-only) and writes only F20_channel_models.{pdf,png} next to this script (or to
    $FIG_OUTDIR) (no .txt; the record text is printed to stdout and keeps the internal names).
The original docstring follows.

conf/code/figure_f20.py -- F20: the learned prior across channel models (cell C2, 8x4, T=16, Tp=4, equal budget 1.6e5).
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

CONF = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "conf"))
sys.path.insert(0, os.path.join(CONF, "code"))
import common as C  # noqa: F401  (same import order as the original: BLAS thread env before numpy)
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({"pdf.fonttype": 42, "ps.fonttype": 42})   # TrueType fonts in PDF (IEEE PDF eXpress rejects Type 3)
from analysis import load_raw, gain, wilson
from recovery_ci import fails, boot, rec
from figstyle import INK, INK2, SHADE, V1, GMM, GENIE, GAUSS
import fighs_merge as M                              # conference/figures/fighs_merge.py (FIGHS16e4 merge)

plt.rcParams.update({"font.size": 8, "axes.labelsize": 8.5, "axes.titlesize": 8.5, "legend.fontsize": 8,
                     "xtick.labelsize": 8, "ytick.labelsize": 8, "axes.grid": True, "grid.alpha": 0.25,
                     "figure.dpi": 200, "savefig.bbox": "tight", "savefig.pad_inches": 0.02,
                     "text.color": INK, "axes.labelcolor": INK, "axes.titlecolor": INK,
                     "xtick.labelcolor": INK, "ytick.labelcolor": INK})
FIG = M.FIG                                          # paper version: figures only, next to this script ($FIG_OUTDIR)
BS, V1A, GE, R2 = "M-ours-bstar", "M-ours-dscore-C-V1", "R5-genie", "R2-ours-G"
# (label, raw tag, prior, table-B label as registered, record gap (est, lo, hi), record R(-3 dB) (R, lo, hi), note)
TB = [("D2 sparse specular\n(headline)", "B16e4k", "S2", "(i) 3/3", (1.41, 1.22, 1.64), (0.470, 0.427, 0.512), "gate PASS"),
      ("D3: D2 with CN\npath gains", "D3B16e4", "S2c", "(i) 3/3", (1.41, 1.19, 1.67), (0.367, 0.335, 0.399), "UNGATED"),
      ("SV8e clustered\nSaleh–Valenzuela", "SVB16e4", "SV8e", "(iv) underpowered", (0.25, 0.16, 0.33), (0.143, 0.095, 0.188), "UNGATED"),
      ("3GPP 38.901\nUMi 28 GHz", "U28B16e4", "UMi28", "(i) 3/3", (0.60, 0.33, 0.87), (0.062, 0.033, 0.089), "UNGATED"),
      ("3GPP 38.901 MIX3\n(side point)", "MXB16e4", "MIX3", "(i) 3/3, report-only", (0.98, 0.68, 1.31), (0.090, 0.062, 0.117), "UNGATED")]
# paper tick labels (TERMS.md), keyed by raw tag; TB's own labels stay for the record text and the hollow-marker rule
NAME = {"B16e4k": "Sparse specular", "D3B16e4": "Sparse specular,\nCN gains", "SVB16e4": "Clustered SV\n(Saleh–Valenzuela)",
        "U28B16e4": "3GPP UMi\n28 GHz", "MXB16e4": "3GPP mixed"}


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
        # paper: the registered label annotation (lb) is not drawn
    a1.axvline(0, color=INK, lw=0.8)
    a1.axhspan(3.5, 4.5, color=SHADE, zorder=0, lw=0)
    a1.set_yticks(y, [NAME[t[1]] for t in TB], fontsize=7.2)
    a1.set_xlim(-0.2, 2.75); a1.set_ylim(-0.6, len(TB) - 0.4)
    a1.set_xlabel("SNR gain at BLER 0.1 [dB]\n(> 0: proposed better)")
    a1.set_title("(a)", loc="left", fontweight="bold", fontsize=8.5)   # paper: panel label only
    a1.grid(axis="y", visible=False)

    # ---------------- (b) UMi28 BLER curves ----------------
    d, meta, _ = load_raw("D2", root=os.path.join(C.CONF, "raw_U28B16e4"))
    snrs = sorted(k[2] for k in d if k[0] == "C2")
    txt += ["", "(b) 3GPP 38.901 UMi 28 GHz (raw_U28B16e4, V1 = _best weights), failures / 2560 per SNR "
            + " ".join(f"{s:+.0f}" for s in snrs) + " dB:"]
    fh = ["  (b) UMi28 C2:"]                                   # FIGHS16e4 merge record (printed after the record)
    for arm, sty, lab in ((R2, GAUSS, "Gaussian prior"), (BS, GMM, "GMM prior"), (V1A, V1, "Proposed"),
                          (GE, GENIE, "Perfect CSI")):
        f = [fails(d, "C2", s, arm) for s in snrs]
        k = np.array([x.sum() for x in f]); n = np.array([len(x) for x in f]); assert (n == 2560).all(), (arm, n)
        txt.append(f"  {arm:<20} " + " ".join(str(int(a)) for a in k))
        k, n, line = M.merge(snrs, k, n, "U28B16e4", "C2", "UMi28", arm); fh.append(line)   # +6..+15 dB: n = 20480 raw
        ci = np.array([wilson(int(a), int(m)) for a, m in zip(k, n)]); p = k / n; ok = k > 0
        a2.errorbar(snrs, np.where(ok, p, np.nan), yerr=[np.where(ok, p - ci[:, 0], np.nan), np.where(ok, ci[:, 1] - p, np.nan)],
                    color=sty["color"], marker=sty["marker"], ls=sty["ls"], lw=1.1, ms=(4 if sty["marker"] != "*" else 6.5),
                    capsize=1.5, elinewidth=0.8, label=lab, zorder=4 if arm == V1A else 3)
        if arm == GE: M.zero_arrows(a2, np.array(snrs)[~ok], n[~ok], sty["color"])
    a2.set_yscale("log"); a2.set_ylim(3e-5, 1.0); a2.set_xticks(range(-3, 16, 3)); a2.set_xlabel("SNR [dB]")   # §1: 3e-5 (1/20480 visible)
    a2.set_ylabel("BLER")
    a2.set_title("(b)", loc="left", fontweight="bold", fontsize=8.5)   # paper: panel label only
    a2.legend(loc="lower left", frameon=False, fontsize=6.8, handlelength=2.0)

    # ---------------- (c) recovery ----------------
    for yi, (lab, tag, prior, lb, rg, rr, note), (r, lo, hi) in zip(y, TB, recs):
        side = "side" in lab
        a3.errorbar(r, yi, xerr=[[r - lo], [hi - r]], color=INK, marker="o", ms=4, capsize=2, elinewidth=1.0, ls="none",
                    mfc="white" if side else INK, zorder=3)
        a3.text(hi + 0.02, yi, f"{r:.2f}", va="center", ha="left", fontsize=7, color=INK2)
    a3.axhspan(3.5, 4.5, color=SHADE, zorder=0, lw=0)
    a3.set_yticks(y, ["" for _ in TB]); a3.set_ylim(-0.6, len(TB) - 0.4); a3.set_xlim(0, 0.62)
    a3.set_xlabel("Fraction of the\nGMM-to-perfect-CSI\ngap closed at −3 dB")
    a3.set_title("(c)", loc="left", fontweight="bold", fontsize=8.5)   # paper: panel label only
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
    print("\n".join(txt + M.block(fh)))                              # paper version: no .txt (the record is conf/figs/F20_channel_models.txt)


if __name__ == "__main__":
    main()
