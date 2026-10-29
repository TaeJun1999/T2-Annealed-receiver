"""conference/figures/paper_f2h18.py -- the three panels of the manuscript's Fig. 3 (files F2*) redrawn at a height of 1.80 in
(user 2026-10-28 19:07 CDT, web chat: "figure 크기도 조금 줄여"; the manuscript's scale = 0.9 had made the text 7.2 pt, and a 1.80 in
panel takes the same place on the page as 1.75 in, so only the height changes -- widths, text sizes (8 pt, legend band 7 pt), curves,
points and axis set-up stay those of the current panels):

  F2a_snr_h18.{pdf,png}     3.00 x 1.80 in  = F2a_snr_sel    (manuscript figures/, by its paper_f2sel.py; 8 curves)
  F2b_budget_h18.{pdf,png}  2.05 x 1.80 in  = F2b_budget_sel (idem)
  F2c_umi32_h18.{pdf,png}   2.00 x 1.80 in  = F2c_umi32      (paper_f2cumi32.py; 7 curves)
The legend band F2legend_sel stays as it is.  No new trial, no number changed; no other file is rewritten.

One drawing code for both heights: it is run at the current height 2.00 in first, and the three PDFs it renders there must equal the
current files byte for byte (sha256 below: F2a_snr_sel / F2b_budget_sel as the manuscript's figures/paper_f2sel.txt records them,
F2c_umi32 as records/paper_f2cumi32.txt does), so the style, points, axes and rcParams copied here are those of the current panels.
The 1.80 in panels are then drawn by the same code with only the figure height changed (axes top 1.75 in instead of 1.95 in).
  - rcParams = paper_f2sel.RC (copied; asserted = paper_f16deep.RC, which paper_f2cumi32 draws with); curve shapes from
    paper_f16deep.BY / size() and the zorder rule of paper_f2sel; every curve is drawn by paper_f2sub.draw (as in paper_f2cumi32).
  - (a), (b): failures read from records/paper_f16deep.txt (the parsing of paper_f2sel.py), asserted = the task prompt's table.
  - (c): failures counted from raw by paper_f2cumi32.sources() / load() and frontier_ci.points / fails (the counting of its main(),
    which is nested there and not importable), asserted = records/paper_f2cumi32.txt, raw content digests = those it records.
  A difference stops the script with the diff before anything is saved.
Asserted for the 1.80 in panels: size; axes bottom 0.36 / top 1.75 in for all three, left / right margins of the current panels;
colour, marker, line style, fill, edge, widths, sizes, zorder and points = the 2.00 in render of the same name; no bar, legend, label
or title; every marker inside the axes box; x and y tick labels clear of each other; every artist inside the canvas; every visible
text >= 7 pt; PDF size, TrueType and no Type 3, PNG 300 dpi size (on the rendered bytes, before the files are written).
Output next to this script, or in $FIG_OUTDIR.
Run (CPU, about 1 minute):
  cd ~/t2/conf && CUDA_VISIBLE_DEVICES= taskset -c 0-15 ~/miniforge3/envs/torch/bin/python -B ~/t2/conference/figures/paper_f2h18.py \\
      > ~/t2/conference/figures/records/paper_f2h18.txt
The typesetting test block at the end of that record is appended by hand after the run (a re-run with '>' drops it; append it again).
"""
import hashlib
import io
import os
import re
import sys

sys.dont_write_bytecode = True                                 # no __pycache__ next to the paper_f*.py or in conf/code
import paper_f2cumi32 as U                                     # sources(), load(), ROLE, SNRS, N, CELL, png_size()
import paper_f2sub as S                                        # draw(), grab()
import paper_f16deep as D                                      # BY, SHOW, size(), RC, coincide(), NEAR_PT, Q.check / same, FIG
import frontier_ci as F                                        # points(), fails() (conf/code, on sys.path after paper_f16deep)
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
H, H0 = 1.80, 2.00                                             # in: new / current height
BOTTOM, TOP = 0.36, 0.05                                       # in: axes margins (paper_f2sel); top end = H - TOP = 1.75 in
W = {"a": 3.00, "b": 2.05, "c": 2.00}
SIDE = {"a": (0.50, 0.06), "b": (0.47, 0.07), "c": (0.48, 0.04)}   # in: left, right margin of the current panels
NAME = {"a": "F2a_snr_h18", "b": "F2b_budget_h18", "c": "F2c_umi32_h18"}
CUR = {"a": ("F2a_snr_sel", "f2c87c07e003fb90317d76a9b19c1a6908ce93fe595b0c84019af36952f47e5c"),   # manuscript figures/paper_f2sel.txt
       "b": ("F2b_budget_sel", "f875ef7b2206386224977c55c62882c300265e6b1376c5adcfffb41de35e0540"),
       "c": ("F2c_umi32", "b836987ae7ec4db90bae6ff0c151ba1cca21cfe9bb3037ef15eb9dd4d07bdfb0")}   # records/paper_f2cumi32.txt:27
INK = "#0b0b0b"
RC = {"font.family": "STIXGeneral", "mathtext.fontset": "stix", "font.size": 8, "axes.labelsize": 8, "xtick.labelsize": 8,   # paper_f2sel.RC
      "ytick.labelsize": 8, "legend.fontsize": 7, "text.color": INK, "axes.labelcolor": INK, "xtick.labelcolor": INK,
      "ytick.labelcolor": INK, "savefig.bbox": "standard", "pdf.fonttype": 42, "ps.fonttype": 42,
      "axes.grid": True, "grid.alpha": 0.25, "grid.linewidth": 0.5, "figure.dpi": 200}
XPAD, XTPAD = 1.0, 2.5                                         # pt (paper_f2sel)
SNR_A = [-3.0, 0.0, 3.0, 6.0, 9.0, 12.0, 15.0]
NB = [1e4, 4e4, 1.6e5, 3.2e5, 6.4e5, 1.28e6]
V1, BS, GE = D.V1, D.BS, D.GE
KEEP = ("M-ours-dscore-C-V1", "ALD-pilot", "M-ours-bstar", "R2-ours-G", "R0-pilot@1", "SBL-loop", "OMP-pilot", "R5-genie")   # paper_f2sel
ALL6 = (V1, BS, "R2-ours-G", "R1-turbo", "R3-bigamp", "R0-pilot@1", GE)                     # (b): at the six budgets; the rest at 1.6e5
# the task prompt's table: (a) failures/n at -3 .. +15 dB; (b) failures/2560 at -3 dB per budget (None = not run)
n_a = (2560,) * 3 + (20480,) * 4
PA = {V1: (371, 88, 29, 111, 59, 39, 23), "ALD-pilot": (833, 213, 66, 39, 11, 11, 9), BS: (623, 184, 57, 235, 149, 81, 72),
      "R2-ours-G": (839, 261, 97, 467, 292, 182, 133), "R0-pilot@1": (1918, 993, 462, 2216, 1379, 951, 715),
      "SBL-loop": (705, 222, 77, 363, 204, 116, 87), "OMP-pilot": (1023, 342, 145, 618, 472, 368, 298), GE: (87, 26, 12, 66, 36, 16, 13)}
NA = {a: (2560,) * 7 if a == "ALD-pilot" else n_a for a in PA}
PB = {V1: (372, 370, 371, 368, 375, 369), BS: (646, 635, 623, 610, 591, 583), "R2-ours-G": (841, 837, 839, 838, 841, 846),
      "R0-pilot@1": (1927, 1920, 1918, 1920, 1919, 1919), GE: (87,) * 6,
      **{a: (None, None, k, None, None, None) for a, k in (("ALD-pilot", 833), ("SBL-loop", 705), ("OMP-pilot", 1023))}}


def shape(arm):
    """paper_f2sel.kw() / zorder(): colour, marker, line style, fill from paper_f16deep.BY, widths and sizes from paper_f16deep.size()"""
    c = D.BY[arm]
    z = {V1: 5, BS: 4, GE: 3}.get(arm, 2.9 - 0.05 * D.SHOW.index(arm))
    return dict({"mew": plt.rcParams["lines.markeredgewidth"], **D.size(c)}, color=c.color, marker=c.marker, ls=c.ls,
                mfc=c.color if c.filled else "white", mec=c.color, zorder=z)


def block(text, head):
    """paper_f2sel.block(): the lines of a record block that starts with `head`, up to the first empty line"""
    return text.split(head, 1)[1].split("\n", 1)[1].split("\n\n")[0].split("\n")


def diff_stop(what, got, want):
    bad = {a: (got.get(a), want.get(a)) for a in sorted(set(got) | set(want)) if got.get(a) != want.get(a)}
    if bad:
        raise SystemExit(f"{what}: counted != recorded -- stopped, nothing written:\n" + "\n".join(f"  {a}: got {g} / record {w}" for a, (g, w) in bad.items()))


def render(h, pts):
    """the three panels at height h -> {p: (fig, ax)}; the code of paper_f2sel (a), (b) and paper_f2cumi32 (c)"""
    out = {}
    for p in "abc":
        w = W[p]
        fig = plt.figure(figsize=(w, h))
        ax = fig.add_axes([SIDE[p][0] / w, BOTTOM / h, (w - sum(SIDE[p])) / w, (h - BOTTOM - TOP) / h])
        for arm, (x, y) in pts[p].items():
            S.draw(ax, dict(shape(arm), x=x, y=y, lo=None, hi=None), D.BY[arm].label)
        if p == "b":
            ax.set_xscale("log"); ax.set_xlim(6e3, 2.2e6); ax.set_ylim(0, 0.9); ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8])
            ax.set_xlabel("Training set size $\\mathit{N}$′ (channels)", labelpad=XPAD); ax.set_ylabel("BLER at −3 dB")
        else:
            ax.set_yscale("log"); ax.set_ylim(*((2e-4, 1.2) if p == "a" else (5e-4, 1.2)))
            ax.set_xticks(SNR_A if p == "a" else list(U.SNRS)); ax.set_xlim(*((-4, 16) if p == "a" else (-13, 7)))
            ax.set_xlabel("SNR [dB]", labelpad=XPAD); ax.set_ylabel("BLER")
        ax.tick_params(axis="x", pad=XTPAD)
        out[p] = (fig, ax)
    return out


def blobs(fig):
    """PDF and PNG bytes as savefig writes them (exactly figsize, PNG 300 dpi, no PDF date)"""
    out = {}
    for ext in ("pdf", "png"):
        buf = io.BytesIO()
        fig.savefig(buf, format=ext, dpi=300, **({"metadata": {"CreationDate": None}} if ext == "pdf" else {}))
        out[ext] = buf.getvalue()
    return out


def cut(fig, ax):
    """drawn points whose marker (its outline + the stroke beyond it) leaves the axes box; paper_f2cumi32.main().cut with the
    marker's own extents instead of (ms + mew) / 2, which is short for 'D' (half width 0.707 ms)"""
    from matplotlib.markers import MarkerStyle
    fig.canvas.draw()
    ab, out = ax.get_window_extent(), []
    for lab, c in S.grab(ax)["curves"].items():
        m = MarkerStyle(c["marker"])
        e = m.get_path().transformed(m.get_transform()).get_extents()
        # ponytail: a mitred 90-degree corner (D, X) sticks out mew / sqrt(2); conservative for s, P, h -- sharper corners (^, 60 deg) need mew
        k = 2 ** -0.5 if str(m.get_joinstyle()) == "miter" else 0.5
        rx, ry = ((max(abs(e.x0), abs(e.x1)) * c["ms"] + k * c["mew"]) * fig.dpi / 72, (max(abs(e.y0), abs(e.y1)) * c["ms"] + k * c["mew"]) * fig.dpi / 72)
        xy = ax.transData.transform(np.column_stack([c["x"], c["y"]]))
        out += [f"{lab} at {s:g}" for s, q in zip(c["x"], xy) if not (ab.x0 <= q[0] - rx and q[0] + rx <= ab.x1 and ab.y0 <= q[1] - ry and q[1] + ry <= ab.y1)]
    return out


def gaps(fig, ax, axis):
    """gaps [pt] between neighbouring visible tick labels (major and minor) inside the view limits; < 0 = overlap"""
    fig.canvas.draw()
    i = 0 if axis == "x" else 1
    lo, hi = sorted(ax.get_xlim() if axis == "x" else ax.get_ylim())
    get = ax.get_xticklabels if axis == "x" else ax.get_yticklabels
    ext = sorted((t.get_window_extent() for m in (False, True) for t in get(minor=m)
                  if t.get_text() and t.get_visible() and lo <= t.get_position()[i] <= hi), key=lambda e: e.extents[i])
    return [(b.extents[i] - a.extents[i + 2]) * 72 / fig.dpi for a, b in zip(ext, ext[1:])], len(ext)


def near(ax, p):
    fx = (lambda v: f"N' {v:g}") if p == "b" else (lambda v: f"{v:+.0f} dB")
    return [(a, b, fx(v)) for a, b, at in D.coincide(ax, D.NEAR_PT) for v in at]


def main():
    assert RC == D.RC, "paper_f2sel.RC != paper_f16deep.RC"
    plt.rcParams.update(RC)
    assert plt.rcParams["savefig.bbox"] is None and plt.rcParams["pdf.fonttype"] == 42   # "standard" is stored as None: no tight crop
    rec = os.path.join(HERE, "records")
    txt = {}
    for f in ("paper_f16deep.txt", "paper_f2cumi32.txt"):
        with open(os.path.join(rec, f), encoding="utf-8") as g:
            txt[f] = g.read()
    sha_in = {f: hashlib.sha256(t.encode()).hexdigest() for f, t in txt.items()}

    # ---------------- (a), (b): records/paper_f16deep.txt = the task prompt's table ----------------
    r16 = txt["paper_f16deep.txt"]
    ka = {}
    for line in block(r16, "\n(a) Failures / trials per SNR"):
        t = line.split()
        if len(t) > 1 and re.fullmatch(r"\d+/\d+", t[1]):
            ka[t[0]] = tuple(tuple(int(v) for v in s.split("/")) for s in t[1:8])
    rows_b = [l.split() for l in block(r16, "\n(b) Failures / 2560 at -3 dB")]
    assert [float(v) for v in next(r for r in rows_b if r and r[0] == "N_train")[1:7]] == NB
    kb = {t[0]: tuple(None if v == "-" else int(v) for v in t[1:7]) for t in rows_b if t and t[0] in ka}
    diff_stop("(a) records/paper_f16deep.txt vs the task prompt", {a: ka.get(a) for a in KEEP}, {a: tuple(zip(PA[a], NA[a])) for a in KEEP})
    diff_stop("(b) records/paper_f16deep.txt vs the task prompt", {a: kb.get(a) for a in KEEP}, {a: PB[a] for a in KEEP})
    assert all(kb[a][2] == ka[a][0][0] for a in KEEP) and all((v is None) == (a not in ALL6) for a in KEEP for i, v in enumerate(kb[a]) if i != 2)

    # ---------------- (c): counted from raw (paper_f2cumi32.sources / load) = records/paper_f2cumi32.txt ----------------
    r2c = txt["paper_f2cumi32.txt"]
    src = U.sources()
    roles = sorted(set(U.ROLE.values()))                           # base, ald, gcap, sbl (the PIL raw holds no drawn curve)
    raws = {r: U.load(*src[r]) for r in roles}
    for r, (_, _, (nf, dig)) in raws.items():                      # the raws are those paper_f2cumi32 read: same path, commit, content
        assert re.search(rf": {re.escape(src[r][0])}  run\|git {src[r][1]}  {nf} files  digest {dig}  ", r2c), (r, src[r], nf, dig)
    keys = F.points(raws["base"][0], U.CELL)
    assert [k[2] for k in keys] == list(U.SNRS)
    for r, (d, _, _) in raws.items():                              # the same blocks: Perfect CSI error arrays identical
        assert F.points(d, U.CELL) == keys and all(np.array_equal(d[k][GE]["blk_err"], raws["base"][0][k][GE]["blk_err"]) for k in keys), r
    arms_c = [a for a in D.SHOW if a in U.ROLE]
    kc = {}
    for a in arms_c:
        d = raws[U.ROLE[a]][0]
        assert all(len(F.fails(d, k, a)) == U.N for k in keys)
        kc[a] = tuple(int(F.fails(d, k, a).sum()) for k in keys)
    rc = {}
    for a in arms_c:
        m = re.search(rf"^  {re.escape(D.BY[a].label)} +{re.escape(a)} +((?:\d+ +){{6}}\d+)   = ", r2c, re.M)
        rc[a] = tuple(int(v) for v in m[1].split()) if m else None
    diff_stop("(c) raw vs records/paper_f2cumi32.txt", kc, rc)

    pts = {"a": {a: (SNR_A, np.array([k for k, _ in ka[a]], float) / np.array([n for _, n in ka[a]], float)) for a in D.SHOW if a in KEEP},
           "b": {a: ((NB, [v / 2560 for v in kb[a]]) if a in ALL6 else (NB[2:3], [kb[a][2] / 2560])) for a in D.SHOW if a in KEEP},
           "c": {a: (np.array(U.SNRS), np.array(kc[a]) / U.N) for a in arms_c}}
    assert [a for a in D.SHOW if a in KEEP] == list(KEEP) and len(arms_c) == 7

    # ---------------- the current height: byte for byte = the current PDFs ----------------
    ref = render(H0, pts)
    for p, (fig, ax) in ref.items():
        got = hashlib.sha256(blobs(fig)["pdf"]).hexdigest()
        if got != CUR[p][1]:
            raise SystemExit(f"{CUR[p][0]}: the 2.00 in render is not the current file ({got} != {CUR[p][1]}) -- stopped, nothing written")
    near0 = {p: near(ax, p) for p, (_, ax) in ref.items()}
    line7 = "; ".join(f"{a} / {b} at " + ", ".join(f"{v:+.0f} dB" for v in at) for a, b, at in D.coincide(ref["c"][1], D.NEAR_PT))
    assert f"at this panel size (positions unchanged): {line7}.\n" in r2c, line7   # = the list records/paper_f2cumi32.txt has

    # ---------------- 1.80 in: checks on the rendered bytes, then the files ----------------
    new, res = render(H, pts), {}
    for p, (fig, ax) in new.items():
        w = W[p]
        g0, g = S.grab(ref[p][1])["curves"], S.grab(ax)["curves"]     # grab() stops on any collection, patch or unlabelled line
        assert list(g) == list(g0) == [D.BY[a].label for a in pts[p]]
        for lab in g:
            assert D.Q.same(g[lab]["x"], g0[lab]["x"]) and D.Q.same(g[lab]["y"], g0[lab]["y"]), lab
            assert all(g[lab][k] == g0[lab][k] for k in ("color", "marker", "ls", "mfc", "mec", "lw", "ms", "mew", "zorder")), lab
        assert not ax.containers and not ax.collections and len(ax.lines) == len(pts[p])               # no bar artist
        assert not ax.get_legend() and not fig.legends and not ax.get_title() and not ax.texts and not fig.texts
        for k in ("xlim", "ylim", "xscale", "yscale", "xlabel", "ylabel", "xticks", "yticks"):
            assert S.grab(ax)[k] == S.grab(ref[p][1])[k], (p, k)
        assert not cut(fig, ax), (p, cut(fig, ax))
        tight, small = D.Q.check(fig, NAME[p])                     # every artist inside the canvas; every visible text >= 7 pt
        box = np.array(ax.get_position().extents) * np.tile((w, H), 2)
        assert tuple(fig.get_size_inches()) == (w, H) and np.allclose(box, [SIDE[p][0], 0.36, w - SIDE[p][1], 1.75], rtol=0, atol=1e-12), (p, box)
        (gx, nx), (gy, ny) = gaps(fig, ax, "x"), gaps(fig, ax, "y")
        assert min(gx) > 0 and min(gy) > 0 and nx == (3 if p == "b" else 7), (p, gx, gy, nx)   # (b): 10^4, 10^5, 10^6
        yt = [t.get_text() for t in ax.get_yticklabels() if t.get_text() and t.get_visible() and min(ax.get_ylim()) <= t.get_position()[1] <= max(ax.get_ylim())]
        b = blobs(fig)
        box_pt = [float(v) for v in re.search(rb"/MediaBox \[ *([\d. ]+?) *\]", b["pdf"])[1].split()]
        assert box_pt == [0, 0, w * 72, H * 72] and b"/FontFile2" in b["pdf"] and b"/Type3" not in b["pdf"], (p, box_pt)
        assert U.png_size(b["png"]) == (round(w * 300), round(H * 300)), U.png_size(b["png"])
        res[p] = dict(b=b, box=box, tight=tight, small=small, gx=min(gx), gy=min(gy), nx=nx, ny=ny, yt=yt, near=near(ax, p))
    sums = {}
    for p, r in res.items():                                       # only now: every check has passed
        for ext, b in r["b"].items():
            with open(os.path.join(D.FIG, f"{NAME[p]}.{ext}"), "wb") as f:
                f.write(b)
            sums[f"{NAME[p]}.{ext}"] = (len(b), hashlib.sha256(b).hexdigest())

    # ---------------- record ----------------
    lab = lambda a: D.BY[a].label
    out = [f"paper_f2h18 -- the three panels of the manuscript's Fig. 3 (F2*) at a height of {H:.2f} in (was {H0:.2f}); widths, text, curves, points "
           f"and axis set-up of the current panels; legend band F2legend_sel unchanged.  No new trial, no number changed.  matplotlib "
           f"{plt.matplotlib.__version__}.", "",
           "Inputs (read-only):",
           *[f"  records/{f}  sha256 {s}" for f, s in sha_in.items()],
           "  raws of (c) (path, run|git, files and content digest = the lines of records/paper_f2cumi32.txt, asserted):",
           *[f"    {r}: {src[r][0]}  run|git {src[r][1]}  {raws[r][2][0]} files  digest {raws[r][2][1]}" for r in roles],
           "    every raw: C9 / UMi28, -12 .. +6 dB, test trials 0..2559 in contiguous chunks, no load_raw WARNING (paper_f2cumi32.load); "
           "the Perfect CSI error arrays of the four raws identical (same blocks); " + ("NOTE lines: " + "; ".join(U.NOTES) if U.NOTES else "no NOTE line") + ".", "",
           "Current panels re-rendered at 2.00 in by this code: PDF sha256 = the current files byte for byte (asserted) -- "
           + "; ".join(f"{CUR[p][0]}.pdf {CUR[p][1][:16]}" for p in "abc")
           + " (F2a_snr_sel / F2b_budget_sel: the manuscript's figures/paper_f2sel.txt; F2c_umi32: records/paper_f2cumi32.txt).", "",
           "(a) failures / n at SNR -3 0 +3 +6 +9 +12 +15 dB  = records/paper_f16deep.txt (a) block = the task prompt's table (asserted):"]
    out += [f"  {lab(a):<28} " + " ".join(f"{k}/{n}" for k, n in ka[a]) for a in KEEP]
    out += ["(b) failures / 2560 at -3 dB, N' 1e4 4e4 1.6e5 3.2e5 6.4e5 1.28e6  = records/paper_f16deep.txt (b) block = the task prompt's table "
            "(asserted; the 1.6e5 value = the -3 dB point of (a)):"]
    out += [f"  {lab(a):<28} " + " ".join("-" if v is None else str(v) for v in kb[a]) for a in KEEP]
    out += [f"(c) failures / {U.N} at SNR -12 -9 -6 -3 +0 +3 +6 dB  counted from raw (paper_f2cumi32.load, frontier_ci.fails) = "
            "records/paper_f2cumi32.txt (asserted):"]
    out += [f"  {lab(a):<28} " + " ".join(f"{k:5d}" for k in kc[a]) + ("  [after the first iteration]" if a == "R0-pilot@1" else "") for a in arms_c]
    out += ["", "Files (saved at exactly figsize, savefig.bbox standard; PNG 300 dpi; PDF TrueType, no Type 3 -- asserted on the rendered bytes before writing):"]
    for p in "abc":
        for ext in ("pdf", "png"):
            n, s = sums[f"{NAME[p]}.{ext}"]
            dim = f"{W[p]:.2f} x {H:.2f} in ({W[p] * 72:.2f} x {H * 72:.2f} pt)" if ext == "pdf" else f"{round(W[p] * 300)} x {round(H * 300)} px"
            out.append(f"  {NAME[p]}.{ext:<4} {dim}  {n} bytes  sha256 {s}")
    out += ["", "Axes, from the bottom-left corner of the file [in] (left, bottom, right, top); bottom 0.36 / top 1.75 for all three (asserted), "
            "left / right margins = the current panels:"]
    out += [f"  {NAME[p]:<15} [{', '.join(f'{v:.2f}' for v in res[p]['box'])}]   (current {CUR[p][0]}: [{SIDE[p][0]:.2f}, 0.36, {W[p] - SIDE[p][1]:.2f}, 1.95])"
            for p in "abc"]
    out += ["", "Curves: colour, marker, line style, fill, edge colour, line width, marker size, edge width, zorder and points = the 2.00 in render "
            "of the same name (= the current panels, byte for byte), asserted; no bar (no container, no collection), no legend, panel label or "
            "title (asserted); every marker inside the axes box (asserted).  Axis limits, scales, ticks and labels = the 2.00 in render (asserted):",
            "  (a) x (-4, 16), ticks -3..15; y log (2e-4, 1.2); 'SNR [dB]' / 'BLER'",
            "  (b) x log (6e3, 2.2e6); y (0, 0.9), ticks 0..0.8; 'Training set size N′ (channels)' / 'BLER at −3 dB'",
            "  (c) x (-13, 7), ticks -12..6; y log (5e-4, 1.2); 'SNR [dB]' / 'BLER'", "",
            "Text: rcParams = paper_f2sel.RC (= paper_f16deep.RC, asserted): STIXGeneral / mathtext stix, 8 pt; smallest visible text (nominal; the "
            "exponents of the 10^x labels are smaller, as before) and the narrowest gap between neighbouring tick labels (x: horizontal, y: "
            "vertical; all > 0, asserted):"]
    yfmt = lambda s: re.sub(r"\$\\mathdefault\{10\^\{(-?\d+)\}\}\$", r"10^\1", s)
    out += [f"  {NAME[p]:<15} smallest text {res[p]['small']:g} pt; x labels {res[p]['nx']}, gap {res[p]['gx']:.2f} pt; y labels {res[p]['ny']} "
            f"({' '.join(yfmt(s) for s in res[p]['yt'])}), gap {res[p]['gy']:.2f} pt; tight bbox [in] {np.round(res[p]['tight'], 3).tolist()}"
            for p in "abc"]
    out += ["", f"Item 8 -- markers of two drawn curves with centres closer than {D.NEAR_PT} pt (positions unchanged); [new] = not in the 2.00 in "
            "panel (the (c) list at 2.00 in = records/paper_f2cumi32.txt, asserted):"]
    for p in "abc":
        old = set(near0[p])
        cur = res[p]["near"]
        out.append(f"  ({p}) {len(cur)} at 1.80 in (2.00 in: {len(old)}): " + ("; ".join(f"{a} / {b} at {v}" + (" [new]" if (a, b, v) not in old else "")
                                                                                  for a, b, v in cur) or "none"))
        gone = [x for x in near0[p] if x not in cur]
        if gone:
            out.append(f"      no longer closer than {D.NEAR_PT} pt: " + "; ".join(f"{a} / {b} at {v}" for a, b, v in gone))
    print("\n".join(out))


if __name__ == "__main__":
    main()
