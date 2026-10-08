"""conference/figures/paper_f30one.py -- one-column, one-panel version of the top row of the paper figure F30 (paper_f30.py) for
Fig. 3 of the ICC manuscript:

  F30one_col.{pdf,png}  3.5 x 2.0 in   fraction of the GMM-to-perfect-CSI gap closed vs N_r = 8 / 16 / 32, both datasets on ONE
                                        axes: Sparse specular (filled circles, solid), 3GPP UMi 28 GHz (hollow squares, dotted)

Nothing is recomputed or transcribed.  paper_f30.main() runs in this process with Figure.savefig disabled (F30_scale_trend.* is
not rewritten; all its asserts against the SCALE16e4 records run), and the points, 90% bars and per-point value labels are read
from the artists of its panels (a) and (b) (asserted again after drawing, rtol 1e-12).  Asserted, else the script stops: those
values = the six R_dp cells of its record text to three decimals = the expected cells below.  Its record text is diffed against
conf/figs/F30_scale_trend.txt (the comparison target named in the head of paper_f30.py); the result goes into the record block.
Differences from F30 (a)/(b) and F30top: one axes instead of two (the manuscript refers to the figure as "Fig. 3" only), so the
datasets are told apart by marker / line style and a legend with the TERMS.md names instead of panel labels; smaller markers and
thinner lines; font STIXGeneral / mathtext 'stix' (conf/DECISIONS.md 2026-10-08 CDT, decision 3).  The value labels keep their
position, size and colour.
Asserted at the saved size: the Sparse specular N_r = 32 bar ([0.790, 0.832], about one marker tall) shows outside its marker
(the height grows in 0.05 in steps up to 2.2 in if it does not); value labels and legend do not overlap each other; every visible
text >= 7 pt; every artist inside the canvas.  Saved at exactly figsize (constrained layout, no tight crop), PNG at 300 dpi,
TrueType fonts.  Output next to this script, or in $FIG_OUTDIR.
Run (CPU, ~1 min):
  cd ~/t2/conf && CUDA_VISIBLE_DEVICES= ~/miniforge3/envs/torch/bin/python -B ~/t2/conference/figures/paper_f30one.py \\
      > ~/t2/conference/figures/records/paper_f30one.txt
"""
import contextlib
import difflib
import io
import os
import re
import sys
from unittest import mock

sys.dont_write_bytecode = True                                 # no __pycache__ next to paper_f30.py or in conf/code
import paper_f30 as P                                          # also applies paper_f30's rcParams (used by the reference run)
from paper_f30 import INK, f3
from fighs_merge import FIG                                    # this folder or $FIG_OUTDIR, as the other paper_f*.py
import matplotlib.figure
import matplotlib.text
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.container import ErrorbarContainer
from matplotlib.lines import Line2D

TARGET = os.path.join(P.CONF, "figs", "F30_scale_trend.txt")
W, H0, H_MAX = 3.5, 2.0, 2.2                                   # in
EXPECT = [("0.509", "0.470", "0.544"), ("0.823", "0.774", "0.874"), ("0.811", "0.790", "0.832"),   # Sparse specular, N_r 8 / 16 / 32
          ("0.150", "0.108", "0.190"), ("0.287", "0.252", "0.322"), ("0.432", "0.401", "0.463")]   # 3GPP UMi 28 GHz
SERIES = (("Sparse specular", "o", "-", INK), ("3GPP UMi 28 GHz", "s", ":", "white"))   # TERMS.md name, marker, line, marker fill
STY = dict(ms=3.0, mew=0.8, lw=1.0, capsize=2.0, elinewidth=0.8)
RC = {"font.family": "STIXGeneral", "mathtext.fontset": "stix", "font.size": 8, "axes.labelsize": 8, "xtick.labelsize": 8,
      "ytick.labelsize": 8, "legend.fontsize": 7.5, "text.color": INK, "axes.labelcolor": INK, "xtick.labelcolor": INK,
      "ytick.labelcolor": INK, "savefig.bbox": "standard", "pdf.fonttype": 42, "ps.fonttype": 42}


def panel(ax):
    """a top-row panel of the reference figure -> its points, 90% bar ends, value labels and axis set-up"""
    (c,) = [c for c in ax.containers if isinstance(c, ErrorbarContainer)]
    line, _, bars = c.lines
    x, y = np.asarray(line.get_xdata(), float), np.asarray(line.get_ydata(), float)
    seg = np.array(bars[0].get_segments())
    assert seg.shape == (len(x), 2, 2) and np.array_equal(seg[:, 0, 0], x) and np.array_equal(seg[:, 1, 0], x), seg
    return dict(x=x, y=y, lo=seg[:, 0, 1], hi=seg[:, 1, 1], zorder=line.get_zorder(),
                texts=[(t.get_position(), t.get_text(), t.get_fontsize(), t.get_color(), t.get_va(), t.get_ha()) for t in ax.texts],
                axis=(ax.get_xscale(), ax.get_xlim(), ax.get_ylim(), ax.get_xticks().tolist(),
                      [t.get_text() for t in ax.get_xticklabels()], ax.get_xlabel(), ax.get_ylabel()))


def same(a, b):
    return np.allclose(a, b, rtol=1e-12, atol=0, equal_nan=True)


def build(h, pa, pb):
    fig, ax = plt.subplots(figsize=(W, h), layout="constrained")
    vals = []
    for (lab, mk, ls, mfc), p in zip(SERIES, (pa, pb)):
        ax.errorbar(p["x"], p["y"], yerr=[p["y"] - p["lo"], p["hi"] - p["y"]], color=INK, marker=mk, ls=ls, mfc=mfc,
                    zorder=p["zorder"], label=lab, **STY)
        vals += [ax.text(*pos, s, va=va, ha=ha, fontsize=fs, color=col) for pos, s, fs, col, va, ha in p["texts"]]
    scale, xlim, ylim, ticks, tl, xlab, ylab = pa["axis"]
    assert scale == "log" and xlim == (6.3, 45) and ylim == (0, 1.0) and ticks == [8, 16, 32] and tl == ["8", "16", "32"], pa["axis"]
    ax.set_xscale("log", base=2); ax.set_xticks(ticks, tl); ax.set_xlim(*xlim); ax.minorticks_off(); ax.set_ylim(*ylim)
    ax.set_xlabel(xlab); ax.set_ylabel(ylab)
    leg = ax.legend(handles=[Line2D([], [], color=INK, marker=mk, ls=ls, mfc=mfc, label=lab, **{k: STY[k] for k in ("ms", "mew", "lw")})
                             for lab, mk, ls, mfc in SERIES], loc="lower right", frameon=False, fontsize=7.5)
    fig.canvas.draw()                                              # constrained layout settles the axes position
    return fig, ax, vals, leg


def main():
    # ---------------- reference: paper_f30.main() itself, in this process ----------------
    buf = io.StringIO()
    with mock.patch.object(matplotlib.figure.Figure, "savefig"), contextlib.redirect_stdout(buf):
        P.main()
    ref = buf.getvalue()
    pa, pb = (panel(a) for a in plt.gcf().axes[:2])                 # its (a) Sparse specular, (b) 3GPP UMi 28 GHz
    assert pa["axis"] == pb["axis"], (pa["axis"], pb["axis"])
    got = [(f3(y), f3(lo), f3(hi)) for p in (pa, pb) for y, lo, hi in zip(p["y"], p["lo"], p["hi"])]
    cells = re.findall(r"R_dp = (\d\.\d{3}) \[90% (\d\.\d{3}), (\d\.\d{3})\]", ref)
    if not got == cells == EXPECT:
        raise SystemExit(f"R_dp cells differ -- stopped, nothing written:\n  artists  {got}\n  record   {cells}\n  expected {EXPECT}")
    assert [t[1] for p in (pa, pb) for t in p["texts"]] == [c[0] for c in cells], "value labels != the points"
    with open(TARGET, encoding="utf-8") as f:
        tgt = f.read()
    diff = list(difflib.unified_diff(tgt.splitlines(), ref.splitlines(), "conf/figs/F30_scale_trend.txt", "paper_f30.main()", lineterm="", n=0))

    plt.rcParams.update(RC)                                        # the one-column style, only after the reference run
    need = STY["ms"] / 2 + STY["mew"] / 2 + 0.3                    # pt: marker radius + half its edge + 0.3
    h = H0
    while True:
        fig, ax, vals, leg = build(h, pa, pb)
        y0, y1 = (ax.transData.transform((32, v))[1] for v in (pa["lo"][2], pa["hi"][2]))
        half = (y1 - y0) / 2 * 72 / fig.dpi                         # half length of the Sparse specular N_r = 32 bar, pt
        if half >= need or h >= H_MAX - 1e-9:
            break
        plt.close(fig); h = round(h + 0.05, 2)
    assert half >= need, ("Sparse specular N_r = 32 bar hidden by its marker even at", h, half, need)
    for (lab, *_), p, c in zip(SERIES, (pa, pb), [c for c in ax.containers if isinstance(c, ErrorbarContainer)]):
        seg = np.array(c.lines[2][0].get_segments())
        assert same(c.lines[0].get_xdata(), p["x"]) and same(c.lines[0].get_ydata(), p["y"]) and same(seg[:, 0, 1], p["lo"]) \
            and same(seg[:, 1, 1], p["hi"]), lab
    bb = fig.get_tightbbox(fig.canvas.get_renderer()).extents
    assert bb[0] >= 0 and bb[1] >= 0 and bb[2] <= W and bb[3] <= h, (bb, (W, h))          # every artist inside the canvas
    sizes = [t.get_fontsize() for t in fig.findobj(matplotlib.text.Text) if t.get_text() and t.get_visible()]
    assert min(sizes) >= 7, min(sizes)                                                    # >= 7 pt at the saved size
    boxes = [t.get_window_extent() for t in vals] + [leg.get_window_extent()]
    assert not any(a.overlaps(b) for i, a in enumerate(boxes) for b in boxes[i + 1:]), "value labels / legend overlap"
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(FIG, f"F30one_col.{ext}"), dpi=300)

    # ---------------- record: the reference record, unchanged, then this script's block ----------------
    blk = ["", "F30 one-panel file (paper_f30one.py): drawn from the artists of panels (a), (b) of the paper_f30.main() run above; no number "
           "recomputed or transcribed.",
           f"  F30one_col  {W} x {h} in ({W * 72:.2f} x {h * 72:.2f} pt), one axes: " + "; ".join(
               f"{lab} ({'filled circles, solid' if mk == 'o' else 'hollow squares, dotted'}) " + " ".join(f"{a} [{b}, {c}]" for a, b, c in cs)
               for (lab, mk, *_), cs in zip(SERIES, (cells[:3], cells[3:]))) + " at N_r = 8 / 16 / 32 (90% bars; value labels above the points as in F30).",
           "  R_dp cells: artists = record text above = expected values, to three decimals (asserted; the script stops otherwise).",
           "  paper_f30.main() record text vs conf/figs/F30_scale_trend.txt: " + ("identical." if not diff else
                                                                                   f"{sum(l[:1] in '+-' and l[:3] not in ('+++', '---') for l in diff)} differing line(s):"),
           *["    " + l for l in diff],
           "  decision 3 (STIXGeneral, mathtext stix; TrueType in the PDF): applied.  Decisions 1-2 concern F16a_col only.",
           f"  Sparse specular N_r = 32 bar: half length {half:.2f} pt >= {need:.2f} pt (marker radius + half edge + 0.3) at height {h} in "
           f"-> shows outside its marker (asserted; height steps tried from {H0} in).",
           f"  checks: redrawn points and bar ends = the reference artists (rtol 1e-12); every artist inside the canvas (tight bbox [in] "
           f"{np.round(bb, 3).tolist()}); smallest visible text {min(sizes):g} pt (nominal size; sub/superscripts are smaller); value labels "
           "and legend do not overlap."]
    print(ref + "\n".join(blk))


if __name__ == "__main__":
    main()
