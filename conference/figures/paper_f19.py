"""conference/figures/paper_f19.py -- paper version of conf/code/figure_f19.py (git 3f7c09ab), F19: pilot overhead.

Same data, computation, bootstrap, asserts, colours, markers and line styles as the original; only the rendered text differs:
  - legend labels, annotations and tick labels use the paper glossary (conference/figures/TERMS.md): V1 -> Proposed,
    b* -> GMM prior, R2 -> Gaussian prior, genie -> Perfect CSI; the cell codes (C2/C7/C8) are dropped from the
    x tick labels (the pilot fraction 4/16, 6/16, 8/16 is the tick); y label "BLER" (iterations go to the caption);
  - panel titles removed (setup goes to the caption), only the bold panel labels (a), (b) remain;
  - the registered comparison names P-a / P-b are not drawn: the two recorded differences are labelled
    "Proposed (Tp=4) - GMM prior: Tp=6 / Tp=8" with their recorded 95% / 90% intervals (Holm order -> caption);
  - reads the raw files from conf/ (read-only) and writes only F19_pilot_pareto.{pdf,png} next to this script
    (no .txt; the record text is printed to stdout and keeps the internal names).
The original docstring follows.

conf/code/figure_f19.py -- F19: pilot overhead (Tp >= Nt Pareto; NEXT_EXPERIMENTS_PARETO v2, frozen eee1d669, results §6).
Report figure; every number straight from the raw files (read-only), asserted against the committed record.

(a) BLER@16 vs SNR, 8x4, T=16, headline checkpoint and headline fits (equal budget N_train = 1.6e5): the diffusion prior V1
    with Tp=4 pilots (cell C2) next to the GMM prior b* with Tp=4 / 6 / 8 pilots (cells C2 / C7 / C8), and the known-channel
    reference (genie) at Tp=4.  C2 = raw_B16e4k (-3..15 dB) + raw_PARB16e4 (the registered -6 dB point); C7/C8 = raw_PARB16e4.
    95% Wilson intervals; zero-failure points are omitted from the log axis and listed in the .txt.
(b) SNR@0.1 (log-linear interpolation of BLER@16, exp_0925 snr_at) against the pilot fraction Tp/T for b*, V1, the Gaussian
    prior R2 and the genie, with the UNPAIRED bootstrap 90% interval of frontier_ci.py (B=2000, default_rng(20260926), one
    index draw per (raw set, cell, SNR)); the two registered cross-cell comparisons P-a (V1@Tp4 vs b*@Tp6) and P-b (V1@Tp4
    vs b*@Tp8) are annotated with their registered labels (Holm m=2: P-a first, 95% CI; P-b second, 90% CI).
Writes figs/F19_pilot_pareto.{pdf,png,txt}.
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
from matplotlib.lines import Line2D
from analysis import wilson
from frontier_ci import raws, points, fails, snr_at, Resampler
from figstyle import INK, INK2, V1, GMM, GENIE, GAUSS

plt.rcParams.update({"font.size": 8, "axes.labelsize": 8.5, "axes.titlesize": 8.5, "legend.fontsize": 8,
                     "xtick.labelsize": 8, "ytick.labelsize": 8, "axes.grid": True, "grid.alpha": 0.25,
                     "figure.dpi": 200, "savefig.bbox": "tight", "savefig.pad_inches": 0.02,
                     "text.color": INK, "axes.labelcolor": INK, "axes.titlecolor": INK,
                     "xtick.labelcolor": INK, "ytick.labelcolor": INK})
FIG = os.path.dirname(os.path.abspath(__file__))     # paper version: figures only, next to this script
B, SEED = 2000, 20260926
BS, V1A, GE, R2 = "M-ours-bstar", "M-ours-dscore-C-V1", "R5-genie", "R2-ours-G"
SRC = {"C2": "raw_B16e4k+raw_PARB16e4", "C7": "raw_PARB16e4", "C8": "raw_PARB16e4"}
TP = {"C2": 4, "C7": 6, "C8": 8}
# committed record (NEXT_EXPERIMENTS_PARETO.md §6.2/§6.3): SNR@0.1 point estimates and the registered comparisons
REC = {("C2", BS): -0.81, ("C7", BS): -1.83, ("C8", BS): -2.60, ("C2", V1A): -2.23, ("C7", V1A): -2.92, ("C8", V1A): -3.57,
       ("C2", GE): -4.81, ("C7", GE): -4.84, ("C8", GE): -5.26, ("C2", R2): 0.06, ("C7", R2): -0.89, ("C8", R2): -1.59}
REC_PA = (-0.40, -0.67, -0.13, 0.0040)      # Delta_6, 95% CI (Holm first), bootstrap p
REC_PB = (+0.38, +0.14, +0.63, 0.0070)      # Delta_8, 90% CI (Holm second), bootstrap p


def curve(cell, arm):
    d = raws(SRC[cell])
    keys = points(d, cell)
    return [k[2] for k in keys], [fails(d, k, arm) for k in keys], keys


def boot(specs):
    """frontier_ci.cmd_pair's bootstrap for a list of (cell, arm): per replicate ONE index draw per (raw set, cell, SNR), drawn
    in spec order and shared by every later spec of the same point.  With the pair (A, B) this is exactly frontier_ci --pair
    (so P-a / P-b reproduce the registered numbers); with a single spec it is that spec's own unpaired interval."""
    rs = Resampler(SEED)
    cur = [curve(*s) for s in specs]
    out = np.full((B, len(specs)), np.nan)
    for i in range(B):
        rs.new_replicate()
        for j, ((cell, arm), (snrs, cols, keys)) in enumerate(zip(specs, cur)):
            v, f = snr_at(snrs, [rs.take(SRC[cell], k, x).mean() for k, x in zip(keys, cols)], len(cols[0]))
            out[i, j] = v if f == "ok" else np.nan
    return out


def main():
    fig = plt.figure(figsize=(7.16, 2.9), layout="constrained")
    gs = fig.add_gridspec(1, 2, width_ratios=[1.15, 1])
    a1, a2 = fig.add_subplot(gs[0]), fig.add_subplot(gs[1])
    txt = ["F19 -- pilot overhead: Tp >= Nt Pareto cells (NEXT_EXPERIMENTS_PARETO v2, frozen eee1d669; results §6).  "
           "Numbers recomputed from raw by code/figure_f19.py (read-only); headline checkpoint d2sx_N160000_a1.pt "
           "(legacy last-EMA, sha 4443921ce8d5c4a1), headline fits (b* = kron K=1024, grid-edge caveat).", ""]

    # ---------------- (a) BLER curves ----------------
    series = [("C2", V1A, "Proposed, $T_p$=4", V1["color"], V1["marker"], "-"),
              ("C2", BS, "GMM prior, $T_p$=4", GMM["color"], GMM["marker"], "-"),
              ("C7", BS, "GMM prior, $T_p$=6", GMM["color"], "^", "--"),
              ("C8", BS, "GMM prior, $T_p$=8", GMM["color"], "v", ":"),
              ("C2", GE, "Perfect CSI, $T_p$=4", GENIE["color"], GENIE["marker"], GENIE["ls"])]
    txt.append("(a) BLER@16 (failures / 2560) vs SNR:")
    zeros = []
    for cell, arm, lab, col, mk, ls in series:
        snrs, cols, _ = curve(cell, arm)
        k = np.array([x.sum() for x in cols]); n = np.array([len(x) for x in cols])
        assert (n == 2560).all()
        ci = np.array([wilson(int(a), int(b)) for a, b in zip(k, n)]); p = k / n; ok = k > 0
        a1.errorbar(np.array(snrs)[ok], p[ok], yerr=[p[ok] - ci[ok, 0], ci[ok, 1] - p[ok]], color=col, marker=mk, ls=ls,
                    lw=1.1, ms=(4 if mk != "*" else 6.5), capsize=1.5, elinewidth=0.8, label=lab,
                    mfc=col if cell == "C2" else "white", zorder=4 if arm == V1A else 3)
        zeros += [f"{cell} {arm} {s:+.0f} dB 0/2560" for s, z in zip(snrs, ok) if not z]
        txt.append(f"  {cell} (Tp={TP[cell]}) {arm:<20} " + " ".join(f"{s:+.0f}:{int(a)}" for s, a in zip(snrs, k)))
    txt.append("  zero-failure points (not drawn on the log axis): " + ("; ".join(zeros) if zeros else "none"))
    a1.set_yscale("log"); a1.set_ylim(3e-4, 1.0); a1.set_xlim(-9.8, 15.8); a1.set_xticks(range(-9, 16, 3))
    a1.set_xlabel("SNR [dB]"); a1.set_ylabel("BLER")
    a1.axhline(0.1, color=INK2, lw=0.7, ls=(0, (2, 2)), zorder=1)
    a1.text(15.5, 0.108, "BLER 0.1", ha="right", va="bottom", fontsize=8, color=INK2)
    a1.set_title("(a)", loc="left", fontweight="bold", fontsize=8.5)   # paper: panel label only
    a1.legend(loc="upper center", bbox_to_anchor=(0.5, -0.19), frameon=False, ncol=3, handlelength=2.4, fontsize=7,
              columnspacing=1.0)

    # ---------------- (b) frontier ----------------
    specs = [(c, a) for a in (BS, V1A, R2, GE) for c in ("C2", "C7", "C8")]
    est = {}
    txt += ["", "(b) SNR@0.1 [dB] per (cell, arm) with its own unpaired bootstrap 90% interval (single-spec frontier_ci "
            "bootstrap, B=2000, seed 20260926):"]
    for cell, arm in specs:
        snrs, cols, _ = curve(cell, arm)
        v, f = snr_at(snrs, [x.mean() for x in cols], len(cols[0]))
        assert f == "ok" and round(v, 2) == REC[(cell, arm)], (cell, arm, v, f)
        bo = boot([(cell, arm)])[:, 0]
        lo, hi = np.nanpercentile(bo, [5, 95]); est[(cell, arm)] = (v, lo, hi)
        txt.append(f"  {cell} Tp/T={TP[cell] / 16:.3f} {arm:<20} {v:+.2f} [90% {lo:+.2f}, {hi:+.2f}] "
                   f"censored {100 * np.mean(~np.isfinite(bo)):.1f}%")
    # registered comparisons: exactly frontier_ci --pair (A = V1 C2, B = b* C7 / C8), asserted against the record
    for name, cb, rec, q in (("P-a", "C7", REC_PA, (2.5, 97.5)), ("P-b", "C8", REC_PB, (5, 95))):
        bo = boot([("C2", V1A), (cb, BS)]); dd = bo[:, 0] - bo[:, 1]; df = dd[np.isfinite(dd)]
        dv = est[("C2", V1A)][0] - est[(cb, BS)][0]; lo, hi = np.percentile(df, q)
        pb = 2 * min(np.mean(df <= 0), np.mean(df >= 0))
        assert (round(dv, 2), round(lo, 2), round(hi, 2), round(pb, 4)) == rec, (name, dv, lo, hi, pb)
        txt.append(f"  {name}: SNR@0.1(V1, C2) - SNR@0.1(b*, {cb}) = {dv:+.2f} dB [{q[1] - q[0]:.0f}% {lo:+.2f}, {hi:+.2f}] "
                   f"bootstrap p {pb:.4f} (= record §6.2)")
    x = {c: TP[c] / 16 for c in TP}
    for arm, sty, lab, dx in ((BS, GMM, "GMM prior", 0.004), (V1A, V1, "Proposed (diffusion prior)", -0.004),
                              (R2, GAUSS, "Gaussian prior", 0.0), (GE, GENIE, "Perfect CSI", 0.0)):
        xs = np.array([x[c] + dx for c in ("C2", "C7", "C8")]); e = np.array([est[(c, arm)] for c in ("C2", "C7", "C8")])
        a2.errorbar(xs, e[:, 0], yerr=[e[:, 0] - e[:, 1], e[:, 2] - e[:, 0]], color=sty["color"], marker=sty["marker"],
                    ls=sty["ls"], lw=1.1, ms=(4 if sty["marker"] != "*" else 6.5), capsize=1.5, elinewidth=0.8, label=lab,
                    zorder=4 if arm == V1A else 3)
    # P-a / P-b: the V1 (Tp=4) level as a horizontal reference; b* at Tp=6 lies below it (worse), at Tp=8 above (better)
    yv = est[("C2", V1A)][0]
    a2.axhline(yv, color=V1["color"], lw=0.8, ls=(0, (1, 2)), zorder=1)
    # paper: label moved under the line, between the 4/16 and 6/16 points (it crossed the Proposed curve at 0.205)
    a2.text(0.265, yv + 0.08, "Proposed, $T_p$=4", fontsize=7, color=INK2, ha="left", va="top")
    m = lambda v: f"{v:+.2f}".replace("-", "−")         # typographic minus, as on the tick labels
    a2.text(0.205, -4.58, "Proposed ($T_p$=4) − GMM prior:\n"
            f"$T_p$=6: {m(REC_PA[0])} dB [95% CI {m(REC_PA[1])}, {m(REC_PA[2])}]\n"
            f"$T_p$=8: {m(REC_PB[0])} dB [90% CI {m(REC_PB[1])}, {m(REC_PB[2])}]",
            fontsize=6.5, color=INK, ha="left", va="top")
    a2.set_xticks([x[c] for c in ("C2", "C7", "C8")], [f"{TP[c]}/16" for c in ("C2", "C7", "C8")])
    a2.set_xlabel("Pilot fraction $T_p/T$")
    a2.set_ylabel("SNR at BLER 0.1 [dB]"); a2.set_ylim(0.6, -5.7); a2.set_xlim(0.2, 0.555)          # inverted: lower SNR (better) at the top
    a2.set_title("(b)", loc="left", fontweight="bold", fontsize=8.5)   # paper: panel label only
    a2.legend(loc="upper center", bbox_to_anchor=(0.5, -0.19), frameon=False, fontsize=7, ncol=2, columnspacing=1.0,
              handlelength=2.2)

    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(FIG, f"F19_pilot_pareto.{ext}"))
    txt += ["", "Registered labels (NEXT_EXPERIMENTS_PARETO.md §6): (A) table B b*->V1 in C7 and C8: (i) V1 fewer failures, "
            "POWERED 3/3 (pooled 287:60, 607:113).  (B) P-a \"V1(Tp=4) has a lower SNR@0.1 than b*(Tp=6)\" (Holm first); "
            "P-b \"b*(Tp=8) has a lower SNR@0.1 than V1(Tp=4)\" (reverse, significant).  Headline (C2 B16e4k) unchanged.",
            "Caveats: headline weights are legacy last-EMA (best weights not saved); b* kron K=1024 is at the fitted grid "
            "edge; C2 -6 dB trials were previously observed with 1e4 arms (genie bit-identical to raw_B1e4lo); cross-cell "
            "comparisons are unpaired."]
    print("\n".join(txt))                                # paper version: no .txt (the record is conf/figs/F19_pilot_pareto.txt)


if __name__ == "__main__":
    main()
