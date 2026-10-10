"""conference/figures/paper_f2sub.py -- Fig. 2 of the ICC manuscript as three \\subfloat panels under one legend band (figure*):

  F2legend_wide.{pdf,png}  7.05 x 0.40 in  the legend of F16deep_wide: its 11 entries, 4 columns x 3 rows, no frame
  F2a_snr.{pdf,png}        3.00 x 2.00 in  = F16deep_wide (a): BLER vs SNR, headline cell, the 11 curves
  F2b_budget.{pdf,png}     2.05 x 2.00 in  = F16deep_wide (b): BLER at -3 dB vs training set size, the same curves
  F2c_scale.{pdf,png}      2.00 x 2.00 in  = F30one_col: fraction of the GMM-to-perfect-CSI gap closed vs N_r, two datasets
The manuscript places the four PDFs at scale 1 (\\textwidth 7.14 in >= 3.00 + 2.05 + 2.00 = 7.05 in) and subfig puts (a) (b) (c)
under the panels, so the files carry no panel label and no title.

Nothing is recomputed or transcribed.  paper_f16deep.main() and paper_f30one.main() each run in a fresh interpreter (spawn) with
Figure.savefig disabled -- the state of a stand-alone run, and none of their figure files is rewritten -- and return their
record text and the drawn content of their axes (points, error-bar ends, shapes, sizes, axis set-up, labels).  Asserted, else
the script stops before anything is saved: the two record texts = records/paper_f16deep.txt and records/paper_f30one.txt byte
for byte; every curve redrawn here = the reference artist (x, y, bar ends rtol 1e-12; colour, marker, line style, fill, sizes,
zorder equal); the reference axes and figures hold nothing that is not read (no other collection, patch, image, inset or
figure-level text); the three panel files have the same height and the same axes bottom / top (so the axes line up in a row); every
artist inside its canvas; every visible text >= 7 pt (nominal).
Decided for these files (conf/DECISIONS.md, 2026-10-09 CDT; the web chat's prompt after the user's decisions of 21:46-21:50 CDT):
no panel labels, no titles; the legend keeps a family in one column where three rows allow it; (b) a K label only where K changes, staggered above / below
the GMM curve where two would collide, left out altogether if they still collide (the record says which; the caption then
carries K); (b) the Annealed Langevin point at 1.6e5 lies on the Gaussian prior point -- positions unchanged, the smaller plus is drawn
on top of the larger circle (zorder, as in F16deep_wide) and the pixels of both markers that show are counted and asserted (a
white outline was tried and left out: it hides the circle); (c) the value labels above the points stay only if they are clear of the curves
(lines, points, bars), each other and the legend; STIXGeneral, TrueType in the PDF, saved at exactly figsize, PNG at 300 dpi.
Output next to this script, or in $FIG_OUTDIR.
Run (CPU, about 2 minutes):
  cd ~/t2/conf && CUDA_VISIBLE_DEVICES= ~/miniforge3/envs/torch/bin/python -B ~/t2/conference/figures/paper_f2sub.py \\
      > ~/t2/conference/figures/records/paper_f2sub.txt
"""
import concurrent.futures
import contextlib
import difflib
import hashlib
import importlib
import io
import multiprocessing
import os
import sys
from unittest import mock

sys.dont_write_bytecode = True                                 # no __pycache__ next to the paper_f*.py or in conf/code
HERE = os.path.dirname(os.path.abspath(__file__))
REFS = {"paper_f16deep": "paper_f16deep.txt", "paper_f30one": "paper_f30one.txt"}   # reference script -> its record file
SIZE = {"F2legend_wide": (7.05, 0.40), "F2a_snr": (3.00, 2.00), "F2b_budget": (2.05, 2.00), "F2c_scale": (2.00, 2.00)}   # in
BOTTOM, TOP = 0.36, 0.05                                       # in: the axes margins shared by the three panels (same axes bottom / top)
SIDE = {"F2a_snr": (0.50, 0.06), "F2b_budget": (0.47, 0.07), "F2c_scale": (0.61, 0.04)}   # in: left, right margin of each panel
K_GAP, SEE_PX = 1.0, 15                                        # pt: K label off its bar end; pixels of each of two stacked markers that must show
ALD, GAUSS, GMM = "Annealed Langevin (plug-in)", "Gaussian prior", "GMM prior"
LEG_LOCS = ("lower right", "upper left", "center right", "lower center", "upper center")   # (c): the first spot clear of the data


def style(l):
    return dict(color=l.get_color(), marker=l.get_marker(), ls=l.get_linestyle(), mfc=l.get_markerfacecolor(), mec=l.get_markeredgecolor(),
                lw=l.get_linewidth(), ms=l.get_markersize(), mew=l.get_markeredgewidth(), zorder=l.get_zorder())


def grab(ax):
    """the drawn content of an axes as plain data: curves (error-bar curves with their bar ends, plain lines), texts, legend, axis set-up"""
    import matplotlib.text
    import numpy as np
    from matplotlib.container import ErrorbarContainer
    own, curves = set(), {}
    for c in ax.containers:
        if isinstance(c, ErrorbarContainer):
            line, caps, bars = c.lines
            own |= {id(line), *map(id, caps)}
            x, y = np.asarray(line.get_xdata(), float), np.asarray(line.get_ydata(), float)
            lo, hi = np.full(len(x), np.nan), np.full(len(x), np.nan)
            for s in (s for s in bars[0].get_segments() if len(s)):   # a NaN (zero-failure) point leaves an empty segment
                i = int(np.argmin(np.abs(x - s[0][0])))
                assert s[0][0] == s[1][0] == x[i], (c.get_label(), s)
                lo[i], hi[i] = s[0][1], s[1][1]
            curves[c.get_label()] = dict(x=x, y=y, lo=lo, hi=hi, capsize=caps[0].get_markersize() / 2, ezorder=bars[0].get_zorder(),
                                         elinewidth=float(np.ravel(bars[0].get_linewidth())[0]), **style(line))
    for l in ax.lines:
        if id(l) not in own:                                       # plain labelled lines; anything else (zero-failure caps, reference lines) stops
            assert not l.get_label().startswith("_") and l.get_label() not in curves, l.get_label()
            curves[l.get_label()] = dict(x=np.asarray(l.get_xdata(), float), y=np.asarray(l.get_ydata(), float), lo=None, hi=None, **style(l))
    assert len(ax.collections) == sum(isinstance(c, ErrorbarContainer) for c in ax.containers) and not (
        ax.patches or ax.artists or ax.images or ax.tables or ax.child_axes), "content grab() does not read"   # nothing is dropped silently
    texts = [dict(note=isinstance(t, matplotlib.text.Annotation), in_axes=t.get_transform() == ax.transAxes, s=t.get_text(),
                  pos=tuple(t.xy) if isinstance(t, matplotlib.text.Annotation) else t.get_position(), size=t.get_fontsize(),
                  color=t.get_color(), ha=t.get_ha(), va=t.get_va()) for t in ax.texts]
    leg = ax.get_legend()
    return dict(curves=curves, texts=texts, xlabel=ax.get_xlabel(), ylabel=ax.get_ylabel(), xscale=ax.get_xscale(), yscale=ax.get_yscale(),
                xbase=getattr(ax.xaxis.get_transform(), "base", None), xlim=ax.get_xlim(), ylim=ax.get_ylim(),
                xticks=[float(v) for v in ax.get_xticks()], xticklabels=[t.get_text() for t in ax.get_xticklabels()],
                yticks=[float(v) for v in ax.get_yticks()],
                legend=None if leg is None else dict(labels=[t.get_text() for t in leg.get_texts()], size=leg.get_texts()[0].get_fontsize(),
                                                     handles=[style(h) for h in leg.legend_handles]))


def ref(name):
    """runs in a fresh interpreter: the reference script's main() with Figure.savefig disabled -> its record text, the content of its
    axes, the entries of its figure legend (if any), its rcParams"""
    import matplotlib.figure
    mod = importlib.import_module(name)
    import matplotlib.pyplot as plt
    buf = io.StringIO()
    with mock.patch.object(matplotlib.figure.Figure, "savefig"), contextlib.redirect_stdout(buf):
        mod.main()
    fig = plt.gcf()                                                # the figure the script made last = the one it saves
    assert not (fig.texts or fig.lines or fig.patches or fig.artists or fig.images), "figure-level content ref() does not read"
    return buf.getvalue(), [grab(a) for a in fig.axes], [[t.get_text() for t in g.get_texts()] for g in fig.legends], dict(mod.RC)


def draw(ax, c, lab, **over):
    """one curve from its reference record, same shape and size"""
    import numpy as np
    kw = dict({k: c[k] for k in ("color", "marker", "ls", "mfc", "mec", "lw", "ms", "mew")}, label=lab, **over)
    if c["lo"] is None:
        ax.plot(c["x"], c["y"], zorder=c["zorder"], **kw)
    else:                                                          # errorbar puts its data line at zorder + 0.1: bars and caps at ezorder
        ax.errorbar(c["x"], c["y"], yerr=[np.maximum(c["y"] - c["lo"], 0), c["hi"] - c["y"]], capsize=c["capsize"],
                    elinewidth=c["elinewidth"], zorder=c["ezorder"], **kw)


def touched(D, ax, bb, pad):
    """what paper_f16deep.hits() finds within `pad` px of the box, by curve: 'name' when a marker, cap or bar of the curve is that near,
    'name (line only)' when only its connecting line is -- the same test, so no decision changes (asserted)"""
    import numpy as np
    from matplotlib.container import ErrorbarContainer
    from matplotlib.path import Path
    from matplotlib.transforms import Bbox
    box = Bbox.from_extents(bb.x0 - pad, bb.y0 - pad, bb.x1 + pad, bb.y1 + pad)

    def near(l):                                                   # (a marker or cap box, a line segment) of one Line2D
        xy = l.get_transform().transform(l.get_xydata())
        fin = np.isfinite(xy).all(axis=1)
        r = l.get_markersize() / 2 * ax.figure.dpi / 72 if l.get_marker() not in ("None", "", None) else 0.0
        ry = 0.0 if l.get_marker() == "_" else r
        solid = any(box.overlaps(Bbox.from_extents(x - r, y - ry, x + r, y + ry)) or box.contains(x, y) for x, y in xy[fin])
        line = l.get_linestyle() not in ("None", "", " ") and any(
            fin[i] and fin[i + 1] and Path(xy[i:i + 2]).intersects_bbox(box, filled=False) for i in range(len(xy) - 1))
        return solid, line
    out, own = [], set()
    for c in ax.containers:
        if isinstance(c, ErrorbarContainer):
            line, caps, bars = c.lines
            own |= {id(line), *map(id, caps)}
            solid, ln = near(line)
            solid = solid or any(near(k)[0] for k in caps) or any(
                len(g) and Path(b.get_transform().transform(g)).intersects_bbox(box, filled=False) for b in bars for g in b.get_segments())
            out += [c.get_label() + ("" if solid else " (line only)")] if solid or ln else []
    for l in ax.lines:
        if id(l) not in own and any(near(l)):
            out.append(l.get_label() + ("" if near(l)[0] else " (line only)"))
    assert bool(out) == bool(D.hits(ax, bb, pad)), (out, D.hits(ax, bb, pad))
    return out


def same_curves(ax, refc, Q):
    """the curves redrawn on ax = the reference curves: data (rtol 1e-12), bar ends, shapes, sizes, zorder"""
    got = grab(ax)["curves"]
    assert list(sorted(got)) == sorted(refc), (sorted(got), sorted(refc))
    for lab, c in refc.items():
        g = got[lab]
        assert Q.same(g["x"], c["x"]) and Q.same(g["y"], c["y"]) and (c["lo"] is None) == (g["lo"] is None), lab
        assert c["lo"] is None or (Q.same(g["lo"], c["lo"]) and Q.same(g["hi"], c["hi"]) and (g["capsize"], g["elinewidth"], g["ezorder"]) == (c["capsize"], c["elinewidth"], c["ezorder"])), lab
        keys = ("color", "marker", "ls", "mfc", "mec", "lw", "ms", "mew", "zorder")
        assert all(g[k] == c[k] for k in keys), (lab, {k: (g[k], c[k]) for k in keys if g[k] != c[k]})


def proxy(c, lab):
    from matplotlib.lines import Line2D
    return Line2D([], [], label=lab, **{k: c[k] for k in ("color", "marker", "ls", "mfc", "mec", "lw", "ms", "mew")})


def main():
    # ---------------- references: the two scripts themselves, each in a fresh interpreter ----------------
    with concurrent.futures.ProcessPoolExecutor(2, mp_context=multiprocessing.get_context("spawn")) as ex:
        out = dict(zip(REFS, ex.map(ref, REFS)))
    shas = {}
    for name, f in REFS.items():
        with open(os.path.join(HERE, "records", f), encoding="utf-8") as fh:
            rec = fh.read()
        if out[name][0] != rec:
            raise SystemExit(f"{name}.main() no longer prints records/{f} -- stopped, nothing written:\n" + "\n".join(
                difflib.unified_diff(rec.splitlines(), out[name][0].splitlines(), f"records/{f}", f"{name}.main()", lineterm="")))
        shas[f] = (hashlib.sha256(rec.encode()).hexdigest()[:16], rec.count("\n"))
    (A, B), (order,), RC = out["paper_f16deep"][1:]                # F16deep_wide: its (a), (b) axes and its one figure legend
    (C,), no_leg, _ = out["paper_f30one"][1:]                      # F30one_col: one axes with its own legend
    assert not no_leg and A["legend"] is None and B["legend"] is None and C["legend"] is not None
    assert sorted(A["curves"]) == sorted(B["curves"]) == sorted(x for x in order if x) and len(A["curves"]) == 11, sorted(A["curves"])

    import matplotlib.colors
    import matplotlib.pyplot as plt
    import numpy as np
    import paper_f16deep as D                                      # hits(), the canvas / text checks (Q), the output folder; no main() here
    from matplotlib.transforms import Bbox
    Q, FIG = D.Q, D.FIG
    plt.rcParams.update(RC)                                        # the style F16deep_wide is drawn with
    px = 72 / plt.rcParams["figure.dpi"]                           # pt per pixel
    figs, notes = {}, {}

    def panel(name):
        w, h = SIZE[name]
        fig = plt.figure(figsize=(w, h))
        figs[name] = fig
        return fig, fig.add_axes([SIDE[name][0] / w, BOTTOM / h, (w - sum(SIDE[name])) / w, (h - BOTTOM - TOP) / h])

    # ---------------- F2a_snr = F16deep_wide (a) ----------------
    fa, ax = panel("F2a_snr")
    for lab, c in A["curves"].items():
        draw(ax, c, lab)
    ax.set_yscale(A["yscale"]); ax.set_ylim(*A["ylim"]); ax.set_xticks(A["xticks"]); ax.set_xlim(*A["xlim"])
    ax.set_xlabel(A["xlabel"], labelpad=Q.XPAD); ax.set_ylabel(A["ylabel"]); ax.tick_params(axis="x", pad=Q.XTPAD)
    same_curves(ax, A["curves"], Q)
    assert [t["s"] for t in A["texts"]] == ["(a)"] and A["texts"][0]["in_axes"], A["texts"]   # its only text: the panel label, not redrawn

    # ---------------- F2b_budget = F16deep_wide (b) ----------------
    fb, bx = panel("F2b_budget")
    for lab, c in B["curves"].items():
        draw(bx, c, lab)
    bx.set_xscale(B["xscale"]); bx.set_xlim(*B["xlim"]); bx.set_ylim(*B["ylim"]); bx.set_yticks([v for v in B["yticks"] if B["ylim"][0] <= v <= B["ylim"][1]])
    bx.set_xlabel(B["xlabel"], labelpad=Q.XPAD); bx.set_ylabel(B["ylabel"]); bx.tick_params(axis="x", pad=Q.XTPAD)
    same_curves(bx, B["curves"], Q)
    ald, gau, gm = (B["curves"][k] for k in (ALD, GAUSS, GMM))
    assert len(ald["x"]) == 1 and ald["zorder"] > gau["zorder"], (ald["zorder"], gau["zorder"])   # drawn over the Gaussian prior point
    i16 = int(np.argmin(np.abs(gau["x"] - ald["x"][0])))
    gap_pt = float(np.hypot(*(bx.transData.transform((ald["x"][0], ald["y"][0])) - bx.transData.transform((gau["x"][i16], gau["y"][i16])))) * px)
    kref = [t for t in B["texts"] if t["note"]]                    # its K labels: text and the GMM point each belongs to
    assert [t["s"] for t in B["texts"] if not t["note"]] == ["(b)"] and len(kref) == 4, B["texts"]
    ki = [int(np.argmin(np.abs(gm["x"] - t["pos"][0]))) for t in kref]
    assert all(np.allclose(t["pos"], (gm["x"][i], gm["lo"][i]), rtol=1e-9, atol=0) for t, i in zip(kref, ki)), kref   # anchored at the GMM points' lower bar ends
    fb.canvas.draw()
    # decision 5: how much of each of the two stacked markers shows -- pixels of each colour within 2.2 pt of the Gaussian prior point on
    # the canvas as drawn; for the grey circle only those outside the bands of its own dashed line (|dy| < 0.9 pt) and error bar (|dx| < 0.6 pt)
    buf = np.asarray(fb.canvas.buffer_rgba())[::-1, :, :3].astype(int)              # row 0 = the bottom of the figure, as display coordinates
    cxy = bx.transData.transform((gau["x"][i16], gau["y"][i16]))
    yy, xx = np.mgrid[:buf.shape[0], :buf.shape[1]]
    spot = np.hypot(xx + 0.5 - cxy[0], yy + 0.5 - cxy[1]) <= 2.2 / px
    free = (np.abs(yy + 0.5 - cxy[1]) >= 0.9 / px) & (np.abs(xx + 0.5 - cxy[0]) >= 0.6 / px)
    rgb = lambda col: (np.array(matplotlib.colors.to_rgb(col)) * 255).astype(int)
    seen = {k: int((m & (np.abs(buf - rgb(c["color"])).max(axis=2) <= 40)).sum()) for k, c, m in ((GAUSS, gau, spot & free), (ALD, ald, spot))}
    assert min(seen.values()) >= SEE_PX, seen

    def k_try(up):
        """K labels under their GMM points, those with index in `up` above instead -> (artists or None, pairs that collide, labels over the data)"""
        kt = [bx.annotate(t["s"], (gm["x"][i], gm["hi" if j in up else "lo"][i]), textcoords="offset points",
                          xytext=(0, K_GAP if j in up else -K_GAP), ha="center", va="bottom" if j in up else "top", fontsize=t["size"],
                          color=t["color"]) for j, (t, i) in enumerate(zip(kref, ki))]
        fb.canvas.draw()
        left = bx.get_window_extent().x0 + 2.0 / px
        for t in kt:                                               # keep 2 pt from the left axis
            e = t.get_window_extent()
            if e.x0 < left:
                t.xyann = (t.xyann[0] + (left - e.x0) * px, t.xyann[1])
        fb.canvas.draw()
        box = [t.get_window_extent() for t in kt]
        wide = [Bbox.from_extents(e.x0 - 1.0 / px, e.y0, e.x1 + 1.0 / px, e.y1) for e in box]   # 2 pt between two labels side by side
        clash = [(i, j) for i in range(len(kt)) for j in range(i + 1, len(kt)) if wide[i].overlaps(wide[j])]
        over = [f"{t['s']} -- {', '.join(touched(D, bx, e, 0.5 / px)) or 'outside the axes'}" for t, e in zip(kref, box)
                if D.hits(bx, e, 0.5 / px) or e.y1 > bx.get_window_extent().y1]
        if clash or over:
            for t in kt:
                t.remove()
            kt = None
        return kt, clash, over
    say = lambda clash, over: (f"labels that collide: {', '.join(kref[i]['s'] + ' / ' + kref[j]['s'] for i, j in clash) or 'none'}; labels within 0.5 pt "
                               f"of a curve (its line, marker, bar or cap): {'; '.join(over) or 'none'}")
    kt, clash0, over0 = k_try(())
    k_how = "all under their GMM points, as in F16deep_wide"
    if kt is None:                                                 # stagger: a label that collides with its left neighbour goes above its point
        up = tuple(sorted({j for _, j in clash0}))
        kt, clash1, over1 = k_try(up)
        k_how = f"staggered: {', '.join(kref[j]['s'] for j in up)} above the GMM curve, the others under it"
        if kt is None:
            k_how = (f"NOT DRAWN -- all under the GMM points: {say(clash0, over0)}; staggered ({', '.join(kref[j]['s'] for j in up) or 'none'} above): "
                     f"{say(clash1, over1)}.  The caption carries K: " + ", ".join(f"{t['s'].replace('$K$ = ', '')} at {gm['x'][i]:.3g}" for t, i in zip(kref, ki))
                     + " (4096 from there on)")
    notes["K"] = k_how
    near = ["; ".join(f"{a} / {b} at " + ", ".join(f(x) for x in at) for a, b, at in D.coincide(a_, D.NEAR_PT)) or "none"
            for a_, f in ((ax, lambda x: f"{x:+.0f} dB"), (bx, lambda x: f"{x:.3g}"))]   # as the F16deep_wide record, at these panel sizes

    # ---------------- F2c_scale = F30one_col ----------------
    fc, cx = panel("F2c_scale")
    for lab, c in C["curves"].items():
        draw(cx, c, lab)
    cx.set_xscale(C["xscale"], base=C["xbase"]); cx.set_xticks(C["xticks"], C["xticklabels"]); cx.set_xlim(*C["xlim"]); cx.minorticks_off()
    cx.set_ylim(*C["ylim"]); cx.set_yticks([v for v in C["yticks"] if C["ylim"][0] <= v <= C["ylim"][1]])
    cx.set_xlabel(C["xlabel"], labelpad=Q.XPAD); cx.set_ylabel(C["ylabel"], labelpad=2); cx.tick_params(axis="x", pad=Q.XTPAD)   # two-line y label
    same_curves(cx, C["curves"], Q)
    assert C["legend"]["labels"] == list(C["curves"]) and all(not t["note"] and not t["in_axes"] for t in C["texts"]) and len(C["texts"]) == 6, C["legend"]
    for size, loc in [(z, l) for z in dict.fromkeys((C["legend"]["size"], 7)) for l in LEG_LOCS]:   # its two-entry legend, inside the axes: the
        leg_c = cx.legend(handles=[proxy(h, l) for h, l in zip(C["legend"]["handles"], C["legend"]["labels"])], loc=loc, frameon=False,   # first spot
                          fontsize=size, handlelength=1.2, handletextpad=0.4, borderaxespad=0.2, borderpad=0.1, labelspacing=0.25)        # 1 pt clear
        fc.canvas.draw()                                                                                                                   # of the data,
        if not D.hits(cx, leg_c.get_window_extent(), 1.0 / px):                                                                            # at its own
            break                                                                                                                          # size, else 7 pt
    else:
        raise SystemExit("F2c_scale: no legend spot clear of the data among " + ", ".join(LEG_LOCS))
    vt = [cx.text(*t["pos"], t["s"], va=t["va"], ha=t["ha"], fontsize=t["size"], color=t["color"]) for t in C["texts"]]
    fc.canvas.draw()
    vb, lbox = [t.get_window_extent() for t in vt], leg_c.get_window_extent()
    v_bad = ([f"{C['texts'][i]['s']} / {C['texts'][j]['s']}" for i in range(6) for j in range(i + 1, 6) if vb[i].overlaps(vb[j])]
             + [f"{t['s']} / legend" for t, e in zip(C["texts"], vb) if e.overlaps(lbox)]
             + [f"{t['s']} / {', '.join(touched(D, cx, e, 0.0))}" for t, e in zip(C["texts"], vb) if D.hits(cx, e, 0.0)]
             + [f"{t['s']} / outside the axes" for t, e in zip(C["texts"], vb) if e.y1 > cx.get_window_extent().y1])
    if v_bad:                                                      # decision 6: the value labels stay only if they are clear of everything (lines too)
        for t in vt:
            t.remove()
    notes["values"] = ("drawn above the points as in F30one_col (clear of the curves' lines, points and bars, of each other and of the legend: asserted)"
                       if not v_bad else "NOT DRAWN -- a label box would touch (tested against the curves' connecting lines as well as the points, bars, "
                       "other labels and legend the decision names): " + "; ".join(v_bad) + ".  The six values and their 90% intervals are in "
                       "records/paper_f30one.txt; the caption or the text has to carry them")
    notes["legend_c"] = f"'{loc}', {size:g} pt (F30one_col: {C['legend']['size']:g} pt)"

    # ---------------- F2legend_wide = the legend of F16deep_wide, 4 columns x 3 rows, a family per column where it fits ----------------
    fam = [order[:3], order[4:8], order[8:11], order[11:]]         # learned priors | Gaussian, LMMSE, AMP | sparse | Perfect CSI (order[3] = its empty slot)
    assert order[3] == "" and [len(f) for f in fam] == [3, 4, 3, 1], order
    seq = fam[0] + fam[1][:3] + [fam[1][3], fam[3][0], ""] + fam[2]   # column by column; Perfect CSI under the fourth entry of the second family
    fl = plt.figure(figsize=SIZE["F2legend_wide"])
    figs["F2legend_wide"] = fl
    from matplotlib.lines import Line2D
    hl = [proxy(A["curves"][l], l) if l else Line2D([], [], ls="none", label="") for l in seq]
    leg = fl.legend(hl, seq, loc="center", ncol=4, frameon=False, fontsize=plt.rcParams["legend.fontsize"], handlelength=2.3, columnspacing=2.6,
                    labelspacing=0.28, borderpad=0.1, handletextpad=0.5)
    fl.canvas.draw()
    lt = [t for t in leg.get_texts() if t.get_text()]
    cols = {}
    for t in lt:
        cols.setdefault(round(t.get_window_extent().x0), []).append(t.get_text())
    rows = sorted({round(t.get_window_extent().y0) for t in lt})
    assert [cols[x] for x in sorted(cols)] == [seq[0:3], seq[3:6], seq[6:8], seq[9:12]] and len(rows) == 3 and len(lt) == 11, cols

    # ---------------- geometry: same height, same axes bottom / top; everything inside its canvas; text >= 7 pt ----------------
    edge, tight, small = {}, {}, {}
    for name, fig in figs.items():
        tight[name], small[name] = Q.check(fig, name)              # every artist inside the canvas; every visible text >= 7 pt
        assert tuple(fig.get_size_inches()) == SIZE[name], name
        if name in SIDE:
            p = np.array(fig.axes[0].get_position().extents) * np.tile(SIZE[name], 2)
            edge[name] = (p[1], p[3])
            assert np.allclose(p, [SIDE[name][0], BOTTOM, SIZE[name][0] - SIDE[name][1], SIZE[name][1] - TOP], rtol=0, atol=1e-12), (name, p)
    assert len({SIZE[n][1] for n in SIDE}) == 1 and len(set(edge.values())) == 1, edge
    assert abs(sum(SIZE[n][0] for n in SIDE) - SIZE["F2legend_wide"][0]) < 1e-9, SIZE
    for name, fig in figs.items():
        for ext in ("pdf", "png"):
            fig.savefig(os.path.join(FIG, f"{name}.{ext}"), dpi=300, **({"metadata": {"CreationDate": None}} if ext == "pdf" else {}))

    # ---------------- record ----------------
    b0, t0 = next(iter(edge.values()))
    lim = lambda v: "(" + ", ".join(f"{float(x):g}" for x in v) + ")"
    txt = ["F2sub -- Fig. 2 of the manuscript as three \\subfloat panels under one legend band: (a) = F16deep_wide (a), (b) = F16deep_wide (b), "
           "(c) = F30one_col.  Nothing recomputed or transcribed: paper_f16deep.main() and paper_f30one.main() ran in fresh interpreters with "
           "Figure.savefig disabled, and every curve here is drawn from the artists of those runs.", "",
           "Reference record texts = the record files, byte for byte (asserted): " + "; ".join(
               f"{n}.main() = records/{f} ({shas[f][1]} lines, sha256[:16] {shas[f][0]})" for n, f in REFS.items()) + ".", "",
           "Files (saved at exactly figsize; PNG 300 dpi; PDF with TrueType fonts):"]
    txt += [f"  {n:<14} {w} x {h} in ({w * 72:.2f} x {h * 72:.2f} pt)" for n, (w, h) in SIZE.items()]
    txt += [f"  panel widths {' + '.join(str(SIZE[n][0]) for n in SIDE)} = {sum(SIZE[n][0] for n in SIDE):.2f} in = the legend band's width (asserted); "
            "IEEEtran conference \\textwidth = 516 pt = 7.14 in.",
            "", "Axes of the three panels, from the bottom of the file [in] (left, bottom, right, top):"]
    txt += [f"  {n:<14} [{SIDE[n][0]:.2f}, {edge[n][0]:.2f}, {SIZE[n][0] - SIDE[n][1]:.2f}, {edge[n][1]:.2f}]" for n in SIDE]
    txt += [f"  the same height {SIZE['F2a_snr'][1]} in and the same axes bottom {b0:.2f} in / top {t0:.2f} in in all three (asserted): placed side by "
            "side the three axes line up.  No panel label and no title in any file (decision 3).",
            "", f"(a) F2a_snr: the {len(A['curves'])} curves of F16deep_wide (a) -- " + "; ".join(A["curves"]) + f" -- x {lim(A['xlim'])}, ticks "
            + " ".join(f"{v:+.0f}" for v in A["xticks"]) + f" dB; y {A['yscale']} {lim(A['ylim'])}; error bars on "
            + "; ".join(l for l, c in A["curves"].items() if c["lo"] is not None) + ".",
            f"(b) F2b_budget: the same {len(B['curves'])} curves as F16deep_wide (b); x {B['xscale']} {lim(B['xlim'])}, y linear {lim(B['ylim'])}; error bars on "
            + "; ".join(l for l, c in B["curves"].items() if c["lo"] is not None) + "; curves with one point (1.6e5 only): "
            + "; ".join(l for l, c in B["curves"].items() if len(c["x"]) == 1) + ".",
            f"(c) F2c_scale: the two curves of F30one_col -- " + "; ".join(C["curves"]) + f" -- with their 90% bars; x log2 {lim(C['xlim'])}, ticks "
            + " ".join(C["xticklabels"]) + f"; y {lim(C['ylim'])}; its two-entry legend inside the axes at {notes['legend_c']} -- the first of "
            + ", ".join(LEG_LOCS) + " that is 1 pt clear of the points, bars and lines, tried at its own size and then at 7 pt -- no frame.",
            "", "Decision 4, K labels of (b): " + notes["K"] + ".",
            f"Decision 5, the Annealed Langevin (plug-in) point of (b) at 1.6e5: its marker centre is {gap_pt:.2f} pt from the Gaussian prior "
            f"point's ({ald['y'][0]:.4f} vs {gau['y'][i16]:.4f}; positions unchanged).  It is drawn over the Gaussian prior point (zorder "
            f"{ald['zorder']:g} > {gau['zorder']:g}, as in F16deep_wide): the smaller plus ({ald['ms']:g} pt) sits on the larger circle ({gau['ms']:g} pt), "
            f"so both show -- pixels of each colour within 2.2 pt of the point on the {plt.rcParams['figure.dpi']:g} dpi canvas: Gaussian prior "
            f"{seen[GAUSS]} (counted outside the bands of its dashed line and its error bar), Annealed Langevin {seen[ALD]} (asserted >= {SEE_PX} each).  A white "
            "outline around the plus was tried and left out: it covers the circle (the outline's corners reach past the circle's radius).",
            "Decision 6, value labels of (c): " + notes["values"] + ".",
            f"Markers of two drawn curves with centres closer than {D.NEAR_PT} pt at these panel sizes (the list of the F16deep_wide record, "
            "recomputed): (a) " + near[0] + "; (b) " + near[1] + ".",
            "", "F2legend_wide: the 11 entries of the legend of F16deep_wide with their shapes and sizes, 4 columns x 3 rows, no frame, "
            f"{plt.rcParams['legend.fontsize']:g} pt; column by column: " + " | ".join("; ".join(cols[x]) for x in sorted(cols))
            + ".  One family per column where the three rows allow it: the learned priors, three of the four Gaussian / LMMSE / AMP entries, and "
            "the sparse three; the third column holds the fourth entry of that family (Pilot-only LMMSE) and Perfect CSI.  (F16deep_wide lists "
            "Perfect CSI last; here it sits under Pilot-only LMMSE so that the sparse three share a column -- the entries and their shapes "
            "are unchanged.)",
            "", "Asserts passed (the script stops before saving otherwise): the two record texts above; every redrawn curve = its reference "
            "artist (x, y, error-bar ends rtol 1e-12; colour, marker, line style, fill, edge, line width, marker size, cap size, zorder equal); "
            "panel sizes and axes edges as listed; every artist inside its canvas (tight bbox [in]: " + "; ".join(
                f"{n} {np.round(v, 3).tolist()}" for n, v in tight.items()) + "); smallest visible text "
            + f"{min(small.values()):g} pt (nominal size; the exponents of the 10^x tick labels and other sub/superscripts are smaller, as in the "
            "reference figures); STIXGeneral / mathtext stix."]
    print("\n".join(txt))


if __name__ == "__main__":
    main()
