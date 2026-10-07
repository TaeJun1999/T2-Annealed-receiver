"""conference/figures/paper_f21.py -- paper version of conf/code/figure_f21.py (git 3f7c09ab), F21: every core baseline and
the proposed prior on every channel model.

Same data, computation, asserts, colours, markers and line styles as the original; only the rendered text differs:
  - legend labels use the paper glossary (conference/figures/TERMS.md) instead of project-internal arm names;
  - panel titles removed (dataset names go to the caption), only the bold panel labels (a)-(f) remain:
    (a) Sparse specular, 8x4   (b) Sparse specular, 16x4   (c) Sparse specular, CN gains (8x4)
    (d) Clustered SV (Saleh-Valenzuela, 8x4)   (e) 3GPP UMi 28 GHz (8x4)   (f) 3GPP mixed (8x4);
  - zero-failure points: the curve breaks there instead of joining its neighbours, and Perfect CSI's zero points
    are drawn as a short downward arrow from the 95% Wilson upper bound (the F17 convention; 0/2560 -> 1.5e-3);
    the record text keeps listing them as 'not drawn' (no plotted estimate);
  - FIGHS16e4 merge (NEXT_EXPERIMENTS_FIGHS16e4 §1, report-only; fighs_merge.py): every curve keeps its original raw (n = 2560)
    at -3..+3 dB and takes +6..+15 dB from n = 20480 new trials (raw_FH<tag>; (a)(b) core arms: HISNR raw_HSB16e4k /
    raw_HSNR16); BLER = k/n and the zero-failure arrow with each point's own n (0/20480 -> 1.87e-4); y from 3e-5; merged k/n
    printed after the unchanged record;
  - reads the raw files from conf/ (read-only) and writes only F21_all_baselines.{pdf,png} next to this script (or to
    $FIG_OUTDIR) (no .txt; the record text is printed to stdout and keeps the internal names).
The original docstring follows.

conf/code/figure_f21.py -- F21: every baseline and the proposed V1 on every channel model (report figure, read-only).

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

CONF = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "conf"))
sys.path.insert(0, os.path.join(CONF, "code"))
import common as C  # noqa: F401  (same import order as the original: BLAS thread env before numpy)
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({"pdf.fonttype": 42, "ps.fonttype": 42})   # TrueType fonts in PDF (IEEE PDF eXpress rejects Type 3)
from analysis import load_raw
from figstyle import INK, INK2, V1, GMM, GENIE, GAUSS
import fighs_merge as M                              # conference/figures/fighs_merge.py (FIGHS16e4 merge, zero_arrows)

plt.rcParams.update({"font.size": 8, "axes.labelsize": 8.5, "axes.titlesize": 8.5, "legend.fontsize": 7.5,
                     "xtick.labelsize": 7.5, "ytick.labelsize": 7.5, "axes.grid": True, "grid.alpha": 0.25,
                     "figure.dpi": 200, "savefig.bbox": "tight", "savefig.pad_inches": 0.02,
                     "text.color": INK, "axes.labelcolor": INK, "axes.titlecolor": INK,
                     "xtick.labelcolor": INK, "ytick.labelcolor": INK})
FIG = M.FIG                                          # paper version: figures only, next to this script ($FIG_OUTDIR)
GREY, LIGHT = "#52514e", "#a3a29d"
# (raw arm key, iteration index, legend label, colour, marker, line style, line width, filled?)
ARMS = [("R3-bigamp", -1, "BiG-AMP", GREY, "v", "--", 1.0, False),
        ("R1-turbo", -1, "Turbo LMMSE receiver", GREY, "^", "-", 1.0, False),
        ("R2-ours-G", -1, "Gaussian prior", GAUSS["color"], "o", "--", 1.1, True),
        ("M-ours-bstar", -1, "GMM prior", GMM["color"], "D", "-", 1.3, True),
        ("M-ours-dscore-C-V1", -1, "Proposed (diffusion prior)", V1["color"], "s", "-", 1.8, True),
        ("R5-genie", -1, "Perfect CSI", GENIE["color"], "*", "-.", 1.1, True)]
# sparse baselines (user request 2026-10-05 CDT): SPARSE16e4 raws raw_SP<suf>, merged onto the base raw exactly as
# conf/code/figure_f31.load does (same trials: perfect-CSI error vectors asserted identical); styles = F31's sparse family.
SPARSE = "#1baf7a"
SP_ARMS = [("SBL-loop", -1, "SBL (in loop)", SPARSE, "h", "-", 1.1, True),
           ("SBL-pilot", -1, "SBL (pilot-only)", SPARSE, "h", "--", 1.1, False),
           ("OMP-pilot", -1, "OMP (pilot-only)", SPARSE, "X", ":", 1.1, False)]
# base raw tag -> (sparse raw tag, record -3 dB failures of SBL-loop, SBL-pilot, OMP-pilot = SPARSE16e4 §6.1 (b) / F31 REC3)
SPS = {"B16e4k": ("SPB16e4k", (705, 934, 1023)), "NR16B16e4": ("SPNR16", (251, 291, 207)),
       "D3B16e4": ("SPD3", (1352, 1528, 1575)), "SVB16e4": ("SPSV", (574, 926, 1493)),
       "U28B16e4": ("SPU28", (1453, 1740, 2304)), "MXB16e4": ("SPMX", (1573, 1811, 2215))}
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
    handles, fh = {}, []                                  # fh: FIGHS16e4 merge record (printed after the record)
    for ax, (title, tag, cell, prior, status, rec3) in zip(axs.flat, SETS):
        d, meta, w1 = load_raw("D2", root=os.path.join(CONF, f"raw_{tag}"))
        sp_tag, sp_rec = SPS[tag]
        sp, _, w2 = load_raw("D2", root=os.path.join(CONF, f"raw_{sp_tag}"))
        assert not w1 and not w2, (tag, w1, w2)
        keys = sorted((k for k in d if k[0] == cell), key=lambda k: k[2])
        for key in keys:                                  # same trials, then merge the three sparse arms (figure_f31.load)
            assert np.array_equal(d[key]["R5-genie"]["blk_err"], sp[key]["R5-genie"]["blk_err"], equal_nan=True), (tag, key)
            assert not set(a for a, *_ in SP_ARMS) & set(d[key]), (tag, key)
            d[key] = {**d[key], **{a: sp[key][a] for a, *_ in SP_ARMS}}
        snrs = np.array([k[2] for k in keys])
        k3 = [k for k in keys if k[2] == -3.0][0]
        got = tuple(int(fails(d, k3, a, -1).sum()) for a in ("M-ours-bstar", "M-ours-dscore-C-V1", "R5-genie"))
        assert got == rec3, (tag, got, rec3)
        got_sp = tuple(int(fails(d, k3, a, -1).sum()) for a, *_ in SP_ARMS)
        assert got_sp == sp_rec, (tag, got_sp, sp_rec)
        m = meta[(cell, prior)]
        bs = f"kron K={m['kron_K']}" if m["bstar"] == "kron" else f"full K={m['bstar'][3:]}"
        txt.append(f"{title} -- raw_{tag}, cell {cell}, prior {prior}, {status}; b* = {bs}.  Failures / 2560 at SNR "
                   + " ".join(f"{s:+.0f}" for s in snrs) + " dB:")
        zeros = []                                        # record: the original raws' zero-failure points
        fh.append(f"  {title[:3]} raw_{tag} + raw_{sp_tag}, cell {cell}:")
        for arm, it, lab, col, mk, ls, lw, filled in SP_ARMS:   # drawn first: the original curves stay on top, unchanged
            k = np.array([fails(d, key, arm, it).sum() for key in keys]); assert all(len(d[key][arm]["blk_err"]) == 2560 for key in keys)
            km, nm, line = M.merge(snrs, k, 2560, sp_tag, cell, prior, arm); fh.append(line)   # +6..+15 dB: n = 20480 raw
            ok = km > 0
            h, = ax.plot(snrs, np.where(ok, km / nm, np.nan), color=col, marker=mk, ls=ls, lw=lw, ms=3.2, mfc=col if filled else "white",
                         mew=0.9, zorder=1)
            handles.setdefault(lab, h)
            zeros += [f"{lab} {s:+.0f}" for s, z in zip(snrs, k > 0) if not z]
            txt.append(f"    {arm:<20}@16  " + " ".join(f"{int(x):5d}" for x in k) + f"   (raw_{sp_tag})")
        for arm, it, lab, col, mk, ls, lw, filled in ARMS:
            k = np.array([fails(d, key, arm, it).sum() for key in keys]); assert all(len(d[key][arm]["blk_err"]) == 2560 for key in keys)
            km, nm, line = M.merge(snrs, k, 2560, tag, cell, prior, arm); fh.append(line)
            ok = km > 0
            h, = ax.plot(snrs, np.where(ok, km / nm, np.nan), color=col, marker=mk, ls=ls, lw=lw, ms=(3.2 if mk not in "*" else 5.5),
                         mfc=col if filled else "white", mew=0.9, zorder=5 if "V1" in arm else 3 if arm == "M-ours-bstar" else 2)
            handles.setdefault(lab, h)
            if arm == "R5-genie": M.zero_arrows(ax, snrs[~ok], nm[~ok], col)
            zeros += [f"{lab.split(' (')[0]} {s:+.0f}" for s, z in zip(snrs, k > 0) if not z]
            txt.append(f"    {arm:<20}{'@1 ' if it == 0 else '@16'}  " + " ".join(f"{int(x):5d}" for x in k))
        for arm in ABLATIONS:
            if arm in d[keys[0]]:
                txt.append(f"    (not drawn) {arm:<20}  " + " ".join(f"{int(fails(d, key, arm, -1).sum()):5d}" for key in keys))
        txt.append("    zero-failure points (not drawn on the log axis): " + ("; ".join(zeros) if zeros else "none"))
        ax.set_title(title[:3], loc="left", fontweight="bold", fontsize=8)   # paper: panel label only
        ax.set_yscale("log"); ax.set_ylim(3e-5, 1.05); ax.set_xticks(range(-3, 16, 3))   # §1: 3e-5 (1/20480 = 4.9e-5 visible)
    for ax in axs[1]:
        ax.set_xlabel("SNR [dB]")
    for ax in axs[:, 0]:
        ax.set_ylabel("BLER")
    order = [a[2] for a in ARMS][::-1] + [a[2] for a in SP_ARMS]      # columns: references | other baselines | sparse
    fig.legend([handles[l] for l in order], order, loc="outside lower center", ncol=3, frameon=False, columnspacing=1.2,
               handlelength=2.6)
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(FIG, f"F21_all_baselines.{ext}"))
    txt += ["", "Only the registered comparison is tested (table B b* -> V1 per registration); every other arm is shown, "
            "not tested.  D2 C6 and every non-D2 channel model are UNGATED measurements; MIX3 is a registered report-only side "
            "point.  R3-bigamp cannot take a correlated prior (structural); R4 arms are interface adaptations of the cited "
            "method.  genie is a known-channel reference, not a bound."]
    print("\n".join(txt + M.block(fh)))


if __name__ == "__main__":
    main()
