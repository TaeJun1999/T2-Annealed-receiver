"""conference/figures/paper_f16col.py -- one-column versions of the paper figure F16 (paper_f16.py) for Fig. 2 of the ICC
manuscript, one file per panel (the manuscript stacks them with \\subfloat, which puts the (a) / (b) labels below the panels):

  F16a_col.{pdf,png}  3.5 x 2.70 in   BLER vs SNR, the seven curves of F16 (a), with the figure's one legend in a band above the axes
  F16b_col.{pdf,png}  3.5 x 1.42 in   BLER at -3 dB vs training set size (F16 (b))

Nothing is recomputed or transcribed.  paper_f16.main() runs in this process with Figure.savefig disabled (so
F16_headline_budget.* is not rewritten), its record text must equal records/paper_f16.txt byte for byte, and every curve drawn
here takes its x, y, error-bar ends, colour, marker, line style, marker fill and zorder from the artists of that run (asserted
again after drawing, rtol 1e-12).  The GMM K of each budget is read from the record text's "b*=kron <K>" lines.

Decided for these files (conf/DECISIONS.md, 2026-10-08 CDT; layout draft by the web chat):
  1  no numeric annotation box in (a) -- the same numbers are in the manuscript's Section IV-B text and in Table I;
  2  (a) y axis from 2e-4, an exception to the FIGHS16e4 §1 rule (3e-5), taken only while (a) has no zero-failure point (no
     fighs_merge.zero_arrows arrow, no broken curve) and every point and lower error-bar end lies above 2e-4; otherwise the axis
     stays at 3e-5 (zero-failure arrows copied from the reference) and the record block says so;
  3  font STIXGeneral / mathtext 'stix' (the manuscript text and its Fig. 1 are Times); the other paper figures keep theirs.
Other differences from F16: no panel titles; (a) x ticks at the SNR points; (b) Perfect CSI -- identical at the six budgets,
asserted -- is one horizontal line; (b) a K label above every GMM point ("K = 512", then the numbers); (b) x label uses the
manuscript's N' instead of N_train (the TERMS.md exception for the ..._col files); (b) y to 0.33 (room for the K labels); thinner
lines and smaller markers for the column width; the x tick-label and x-label pads are tightened (the 0.36 in bottom margin is
fixed by the layout); the y-axis labels of the two files sit at the same x.
Both files have the same width and the same axes left / right edges (asserted), so the frames line up when stacked.  Saved at
exactly figsize (no tight crop), PNG at 300 dpi, TrueType fonts.  Output next to this script, or in $FIG_OUTDIR.
Run (CPU, a few minutes):
  cd ~/t2/conf && CUDA_VISIBLE_DEVICES= ~/miniforge3/envs/torch/bin/python -B ~/t2/conference/figures/paper_f16col.py \\
      > ~/t2/conference/figures/records/paper_f16col.txt
"""
import contextlib
import difflib
import io
import os
import re
import sys
from unittest import mock

sys.dont_write_bytecode = True                                 # no __pycache__ next to paper_f16.py or in conf/code
import paper_f16 as P                                          # also applies paper_f16's rcParams (used by the reference run)
from paper_f16 import FIG, S                                   # FIG = this folder or $FIG_OUTDIR; S = figstyle
import matplotlib.figure
import matplotlib.text
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.container import ErrorbarContainer
from matplotlib.lines import Line2D

REC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "records", "paper_f16.txt")
W, LEFT, RIGHT, BOTTOM = 3.5, 0.50, 0.06, 0.36                 # in: file width and the axes margins shared by both files
H_A, TOP_A = 2.70, 0.62                                        # (a): height, legend band above the axes
H_B, TOP_B = 1.42, 0.06                                        # (b)
K_REC = [512, 2048, 1024, 4096, 4096, 4096]                    # b* K of the six budgets, as the record text has them
YLO, YLO_RULE = 2e-4, 3e-5                                     # decision 2 / the FIGHS16e4 §1 rule it is an exception to
RC = {"font.family": "STIXGeneral", "mathtext.fontset": "stix", "font.size": 8, "axes.labelsize": 8, "xtick.labelsize": 8,
      "ytick.labelsize": 8, "legend.fontsize": 7.5, "text.color": S.INK, "axes.labelcolor": S.INK, "xtick.labelcolor": S.INK,
      "ytick.labelcolor": S.INK, "savefig.bbox": "standard", "pdf.fonttype": 42, "ps.fonttype": 42}
XPAD, XTPAD = 1.0, 2.5                                        # pt: x label pad, x tick-label pad (the defaults 4 / 3.5 overflow the 0.36 in bottom margin)
ARM = dict(lw=1.1, ms=3.6, star=6.0, capsize=1.5, elinewidth=0.7)   # the four arms
SP = dict(lw=0.9, ms=3.0, mew=0.7)                                    # the three sparse baselines


def curves(ax):
    """the curves an axes draws -> {label: x, y, lo, hi (error-bar ends; None = a plain line), colour, marker, ls, mfc, zorder}"""
    out = {}
    for c in ax.containers:
        if isinstance(c, ErrorbarContainer):
            line, _, bars = c.lines
            x, y = np.asarray(line.get_xdata(), float), np.asarray(line.get_ydata(), float)
            lo, hi = np.full(len(x), np.nan), np.full(len(x), np.nan)
            seg = [s for s in bars[0].get_segments() if len(s)]           # a NaN (zero-failure) point leaves an empty segment
            assert len(seg) == int(np.isfinite(y).sum()), (c.get_label(), len(seg))
            for s in seg:
                i = int(np.argmin(np.abs(x - s[0][0])))
                assert s[0][0] == s[1][0] == x[i], (c.get_label(), s)
                lo[i], hi[i] = s[0][1], s[1][1]
            out[c.get_label()] = dict(x=x, y=y, lo=lo, hi=hi, color=line.get_color(), marker=line.get_marker(),
                                      ls=line.get_linestyle(), mfc=line.get_markerfacecolor(), zorder=line.get_zorder())
    for l in ax.lines:
        if not l.get_label().startswith("_"):                              # plain labelled lines (the sparse baselines)
            out[l.get_label()] = dict(x=np.asarray(l.get_xdata(), float), y=np.asarray(l.get_ydata(), float), lo=None, hi=None,
                                      color=l.get_color(), marker=l.get_marker(), ls=l.get_linestyle(),
                                      mfc=l.get_markerfacecolor(), zorder=l.get_zorder())
    return out


def zero_marks(ax):
    """fighs_merge.zero_arrows artists of an axes: (cap lines, arrow annotations) -- empty unless a curve has a zero-failure point"""
    own = {id(l) for c in ax.containers if isinstance(c, ErrorbarContainer) for l in (c.lines[0], *c.lines[1])}
    caps = [l for l in ax.lines if l.get_label().startswith("_") and id(l) not in own]
    arrows = [t for t in ax.texts if isinstance(t, matplotlib.text.Annotation) and not t.get_text() and t.arrow_patch is not None]
    return caps, arrows


def same(a, b):
    return np.allclose(a, b, rtol=1e-12, atol=0, equal_nan=True)


def draw(ax, c, lab):
    """one curve from its reference record c, in the one-column style; the drawn data = the reference's (asserted)"""
    if c["lo"] is None:
        ax.plot(c["x"], c["y"], color=c["color"], marker=c["marker"], ls=c["ls"], mfc=c["mfc"], zorder=c["zorder"], label=lab, **SP)
    else:
        ax.errorbar(c["x"], c["y"], yerr=[np.maximum(c["y"] - c["lo"], 0), c["hi"] - c["y"]], color=c["color"], marker=c["marker"],
                    ls=c["ls"], mfc=c["mfc"], ms=ARM["star"] if c["marker"] == "*" else ARM["ms"], lw=ARM["lw"],
                    capsize=ARM["capsize"], elinewidth=ARM["elinewidth"], zorder=c["zorder"], label=lab)
    d = curves(ax)[lab]
    assert same(d["x"], c["x"]) and same(d["y"], c["y"]), lab
    assert (c["lo"] is None and d["lo"] is None) or (same(d["lo"], c["lo"]) and same(d["hi"], c["hi"])), lab


def proxy(c, lab):
    """legend handle: line + marker, no error bar"""
    kw = SP if c["lo"] is None else dict(lw=ARM["lw"], ms=ARM["star"] if c["marker"] == "*" else ARM["ms"])
    return Line2D([], [], color=c["color"], marker=c["marker"], ls=c["ls"], mfc=c["mfc"], label=lab, **kw)


def new_fig(h, top):
    fig = plt.figure(figsize=(W, h))
    return fig, fig.add_axes([LEFT / W, BOTTOM / h, (W - LEFT - RIGHT) / W, (h - BOTTOM - top) / h])


def inch(fig, bb):
    """a window extent (pixels) -> inches on the canvas"""
    return np.array(bb.extents) / fig.dpi


def check(fig, name):
    """every artist inside the canvas; every visible text >= 7 pt at the saved size -> (tight bbox [in], smallest text [pt])"""
    fig.canvas.draw()
    bb = fig.get_tightbbox(fig.canvas.get_renderer()).extents
    w, h = fig.get_size_inches()
    assert bb[0] >= 0 and bb[1] >= 0 and bb[2] <= w and bb[3] <= h, (name, bb, (w, h))
    sizes = [t.get_fontsize() for t in fig.findobj(matplotlib.text.Text) if t.get_text() and t.get_visible()]
    assert min(sizes) >= 7, (name, min(sizes))
    return bb, min(sizes)


def main():
    # ---------------- reference: paper_f16.main() itself, in this process ----------------
    buf = io.StringIO()
    with mock.patch.object(matplotlib.figure.Figure, "savefig"), contextlib.redirect_stdout(buf):
        P.main()
    ref = buf.getvalue()
    with open(REC, encoding="utf-8") as f:
        rec = f.read()
    if ref != rec:
        raise SystemExit("paper_f16.main() no longer prints records/paper_f16.txt -- stopped, nothing written:\n" + "\n".join(
            difflib.unified_diff(rec.splitlines(), ref.splitlines(), "records/paper_f16.txt", "paper_f16.main()", lineterm="")))
    a1, a2 = plt.gcf().axes[:2]                                    # its (a) SNR axis, (b) budget axis
    A, B = curves(a1), curves(a2)
    labs = [x[1] for x in P.ARMS + P.SPARSE_ARMS]                  # the original legend order
    assert list(A) == labs and list(B) == labs[1:4], (list(A), list(B))
    K = [int(k) for k in re.findall(r"b\*=kron (\d+)", ref)]
    assert K == K_REC, K
    caps, arrows = zero_marks(a1)
    ys = {l: c["y"] for l, c in A.items()}
    los = {l: c["lo"] for l, c in A.items() if c["lo"] is not None}
    n_zero = len(arrows) + int(sum(np.isnan(v).sum() for v in ys.values()))
    low = min(((np.nanmin(v), l, c["x"][np.nanargmin(v)]) for (l, v), c in zip(ys.items(), A.values())), key=lambda t: t[0])
    lowbar = min(((np.nanmin(v), l, A[l]["x"][np.nanargmin(v)]) for l, v in los.items()), key=lambda t: t[0])
    cond1, cond2 = n_zero == 0, min(low[0], lowbar[0]) > YLO
    ylo = YLO if cond1 and cond2 else YLO_RULE
    xlab_a, ylab_a, ylab_b = a1.get_xlabel(), a1.get_ylabel(), a2.get_ylabel()

    plt.rcParams.update(RC)                                        # the one-column style, only after the reference run
    # ---------------- F16a_col ----------------
    fa, ax = new_fig(H_A, TOP_A)
    for lab in labs:
        draw(ax, A[lab], lab)
    for l in caps:                                                 # zero-failure marks, only if the reference has any (y stays 3e-5 then)
        ax.plot(l.get_xdata(), l.get_ydata(), color=l.get_color(), lw=l.get_linewidth(), zorder=l.get_zorder())
    for t in arrows:
        ax.annotate("", xy=t.xy, xytext=t.xyann, zorder=t.get_zorder(), arrowprops=dict(
            arrowstyle="-|>", color=t.arrow_patch.get_edgecolor(), lw=0.9, mutation_scale=6.5, shrinkA=0, shrinkB=0))
    snrs = A[labs[0]]["x"]
    ax.set_yscale("log"); ax.set_ylim(ylo, 0.6); ax.set_xticks(snrs); ax.set_xlim(-4, 16)
    ax.set_xlabel(xlab_a, labelpad=XPAD); ax.set_ylabel(ylab_a); ax.tick_params(axis="x", pad=XTPAD)
    leg = fa.legend([proxy(A[l], l) for l in labs], labs, loc="center", ncol=2, frameon=False, fontsize=7.5,
                    bbox_to_anchor=((LEFT + W - RIGHT) / 2 / W, (H_A - TOP_A / 2) / H_A), handlelength=2.4, columnspacing=1.4,
                    labelspacing=0.3, borderpad=0.2, handletextpad=0.6)
    # ---------------- F16b_col ----------------
    fb, bx = new_fig(H_B, TOP_B)
    gm, v1, ge = (B[l] for l in labs[1:4])
    draw(bx, gm, labs[1]); draw(bx, v1, labs[2])
    flat = all(np.ptp(ge[k]) == 0 for k in ("y", "lo", "hi"))       # Perfect CSI: the same value and bar at the six budgets
    if flat:
        bx.axhline(ge["y"][0], color=ge["color"], ls=ge["ls"], lw=ARM["lw"], zorder=ge["zorder"])
    else:
        draw(bx, ge, labs[3])
    # K above each GMM point: baseline 1.5 pt over the upper bar end (baseline, so the mathtext "K = 512" and the plain numbers sit alike)
    kt = [bx.annotate(f"$K$ = {k}" if i == 0 else str(k), (x, hi), textcoords="offset points", xytext=(0, 1.5), ha="center",
                      va="baseline", fontsize=7, color=S.INK) for i, (x, hi, k) in enumerate(zip(gm["x"], gm["hi"], K))]
    bx.set_xscale("log"); bx.set_xlim(6e3, 2.2e6); bx.set_ylim(0, 0.33); bx.set_yticks([0, 0.1, 0.2, 0.3])
    bx.set_xlabel("Training set size $\\mathit{N}$\u2032 (channels)", labelpad=XPAD); bx.set_ylabel(ylab_b)   # N + U+2032 (a mathtext prime sits apart from N)
    bx.tick_params(axis="x", pad=XTPAD)
    # ---------------- shared geometry: same axes edges, y labels at the same x ----------------
    edge = [np.array(a.get_position().extents)[[0, 2]] * W for a in (ax, bx)]
    assert np.array_equal(edge[0], edge[1]) and np.allclose(edge[0], [LEFT, W - RIGHT], rtol=0, atol=1e-12), edge
    for f in (fa, fb):
        f.canvas.draw()
    xl = min(inch(f, a.yaxis.label.get_window_extent())[2] for f, a in ((fa, ax), (fb, bx)))   # the leftmost label (its axis-side edge)
    for a in (ax, bx):
        a.yaxis.set_label_coords((xl - LEFT) / (W - LEFT - RIGHT), 0.5)   # the y label is anchored at that edge
    out, lab_x = {}, []
    for name, f, a in (("F16a_col", fa, ax), ("F16b_col", fb, bx)):
        bb, small = check(f, name)
        lab = inch(f, a.yaxis.label.get_window_extent())
        ylo_v, yhi_v = sorted(a.get_ylim())
        tick_l = min(inch(f, t.label1.get_window_extent())[0] for t in a.yaxis.get_major_ticks()
                     if ylo_v <= t.get_loc() <= yhi_v and t.label1.get_text())      # tick labels in view
        assert lab[2] <= tick_l, (name, "y label over the tick labels", lab[2], tick_l)
        out[name] = (bb, small); lab_x.append(lab[[0, 2]])
    assert np.allclose(lab_x[0], lab_x[1], rtol=0, atol=1e-6), ("y labels not at the same x", lab_x)
    lb = inch(fa, leg.get_window_extent())
    assert lb[1] >= H_A - TOP_A and lb[3] <= H_A and lb[0] >= 0 and lb[2] <= W, ("legend outside its band", lb)
    kb = [inch(fb, t.get_window_extent()) for t in kt]
    assert all(kb[i][2] < kb[i + 1][0] for i in range(len(kb) - 1)) and max(b[3] for b in kb) <= H_B - TOP_B, ("K labels", kb)
    for name, f in (("F16a_col", fa), ("F16b_col", fb)):
        for ext in ("pdf", "png"):
            f.savefig(os.path.join(FIG, f"{name}.{ext}"), dpi=300)

    # ---------------- record: the reference record, unchanged, then this script's block ----------------
    pt = lambda v: f"{v * 72:.2f}"
    blk = ["", "F16 one-column files (paper_f16col.py): drawn from the artists of the paper_f16.main() run above; its record text = "
           "records/paper_f16.txt byte for byte (asserted); no number recomputed or transcribed.",
           f"  F16a_col  {W} x {H_A} in ({pt(W)} x {pt(H_A)} pt): {', '.join(labs)}; one legend (2 columns, line + marker handles) in the "
           f"{TOP_A} in band above the axes; x ticks {' '.join(f'{s:+.0f}' for s in snrs)} dB, x range (-4, 16); y range ({ylo:g}, 0.6).",
           f"  F16b_col  {W} x {H_B} in ({pt(W)} x {pt(H_B)} pt): {labs[1]}, {labs[2]} with their 95% Wilson bars; {labs[3]} "
           + (f"= one horizontal line at {ge['y'][0]:.6f} (the six budgets carry the same value and the same bar [{ge['lo'][0]:.6f}, "
              f"{ge['hi'][0]:.6f}]: asserted)" if flat else "drawn point by point (NOT identical at the six budgets)")
           + f"; K labels above the GMM points: {' '.join(str(k) for k in K)} (the record's b*=kron lines); x range (6e3, 2.2e6), y range (0, 0.33).",
           "  decision 1 (no annotation box in (a)): applied.",
           f"  decision 2 ((a) y from {YLO:g} instead of the FIGHS16e4 §1 {YLO_RULE:g}): {'applied' if ylo == YLO else 'NOT applied -- y stays at ' + format(YLO_RULE, 'g')}. "
           f"condition 1, zero-failure points in (a): {n_zero} (arrows {len(arrows)}, broken-curve points {n_zero - len(arrows)}) -> {'met' if cond1 else 'NOT met'}; "
           f"condition 2, lowest point {low[0]:.3e} ({low[1]}, {low[2]:+.0f} dB), lowest error-bar end {lowbar[0]:.3e} ({lowbar[1]}, "
           f"{lowbar[2]:+.0f} dB), both > {YLO:g} -> {'met' if cond2 else 'NOT met'}.",
           "  decision 3 (STIXGeneral, mathtext stix; TrueType in the PDF): applied to both files.",
           f"  axes left / right edge in both files: {edge[0][0]:.4f} / {edge[0][1]:.4f} in = {pt(edge[0][0])} / {pt(edge[0][1])} pt (equal: asserted); "
           f"y-axis label spans {pt(lab_x[0][0])}-{pt(lab_x[0][1])} pt from the left edge in both (set to the same x: asserted).",
           "  checks: redrawn x, y, error-bar ends = the reference artists (rtol 1e-12); every artist inside the canvas (tight bbox [in] "
           + "; ".join(f"{n} {np.round(v[0], 3).tolist()}" for n, v in out.items())
           + f"); smallest visible text {min(v[1] for v in out.values()):g} pt (nominal size; sub/superscripts are smaller); legend inside its band; K labels apart."]
    print(ref + "\n".join(blk))


if __name__ == "__main__":
    main()
