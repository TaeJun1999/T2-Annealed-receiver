"""conference/figures/paper_f16deep.py -- Fig. 2 of the ICC manuscript as ONE two-column figure (figure*, 7.16 in wide) of the
headline cell (Sparse specular 8x4 = D2 C2, prior S2; checkpoint d2sx_N160000_a1.pt, last-epoch EMA at N' = 1.6e5):

  F16deep_wide.{pdf,png}   7.16 x 2.75 in
    (a) BLER vs SNR at N' = 1.6e5                 11 curves
    (b) BLER at -3 dB vs training set size        the same 11 curves: seven at the six budgets, four at 1.6e5 only
  One legend above the panels; every panel draws the curves of that legend.  The user's two instructions (2026-10-09 CDT, in the
  session that made this file) are the constant USER below: every panel shows the graphs of the same legend; not all 20 curves
  -- the ones where the proposed prior stands out, with the essential baselines (OMP etc.).  Rule applied by the recorder:
  drawn (SHOW) = the seven curves of the present Fig. 2 (a) -- Proposed, GMM prior, Gaussian prior, Perfect CSI, SBL (in
  loop), SBL (pilot-only), OMP (pilot-only) -- and the receivers / estimators in the form the literature gives them: Turbo
  LMMSE receiver, BiG-AMP, Pilot-only LMMSE, Annealed Langevin (plug-in).  Not drawn (still read, asserted and listed in the
  record text) = the authors' own variants, adaptations and controls: GMM prior (K = 32), GMM prior, scalar site, GMM prior,
  pilot-only, SC-VAMP, SC-VAMP (LLR), Annealed Langevin (error-aware), Proposed prior, pilot-only, Diffusion prior,
  unrepaired (V0), Diffusion prior, scalar site (V4); V4b.  Four of the five registered-nearest baselines are among them, so
  the record prints the registered SNR gains and labels of all 16 baselines and, for every not-drawn curve, the points where
  it reaches the proposed curve or lies inside its drawn bar.  Selection condition, asserted (point estimates): the proposed
  curve is below every other drawn curve except Perfect CSI at every SNR of (a) and every budget of (b).

Nothing is transcribed by hand.  The curves are read from the raw files with analysis.load_raw (as paper_f16 / f21 / f22 / f24 /
f31 do; the pilot-only LMMSE is its alias 'R0-pilot@1', the reading pair_baselines --r0 at1 uses), a raised block counts as a
failure, and the +6..+15 dB points of (a) follow FIGHS16e4 §1 through fighs_merge.merge: -3/0/+3 dB = the original raw
(n = 2560), +6/+9/+12/+15 dB = the arm's n = 20480 raw when one has the arm, else the original raw at every SNR (one point = one
raw, never pooled; no new trial is run).  The @1 reading takes its n = 20480 points from raw_FHB16e4k (run for the @16 reading
of F22): an extension of that rule to a row the registration's own figures do not use -- stated in the record.  Asserted, else
the script stops before anything is saved:
  - every n = 2560 count of (a) = the 'BLER@16 failures' table of conf/results/review_next/pairB_STB16e4k.txt (17 arms x 7
    SNRs), the sparse three = records/paper_f31.txt (b) and records/paper_f21.txt (a), and the -3 dB values of the task prompt;
  - every n = 20480 count = its count table (fighs_merge.merge) and, for all but the @1 reading, the 'FIGHS16e4 merge' blocks of
    records/paper_f16.txt, paper_f21.txt, paper_f22.txt (D2 C2 lines; Pilot-only LMMSE (@1): count table fighs_FHB16e4k.txt only);
    which curves have an n = 20480 raw = the two lists below (HS20480 / N2560);
  - (b): every -3 dB BLER and its Wilson interval at the six budgets = the cell C2 block of conf/results/tables_D2_<tag>.txt
    (TABLE A, three decimals); GMM prior, Proposed, Perfect CSI = the panel (b) artists of paper_f16.main(), which is run here
    with Figure.savefig disabled and must print records/paper_f16.txt byte for byte (its panel (a) artists = the seven curves
    it shares with (a) here); Perfect CSI is the same at the six budgets;
  - same trials: the Perfect CSI error arrays of raw_PILB16e4k / raw_ALDB16e4k / raw_SPB16e4k = raw_B16e4k's (figure_f31.load);
  - drawn = counted: the points and Wilson bar ends of every drawn curve are read back from the artists;
  - a curve that is already in a paper figure keeps that figure's colour / marker / line style / fill (checked against the ARMS
    tables of paper_f16, f18, f21, f22, f24); the (colour, marker, line style, fill) of the curves are distinct, and so are their
    (marker, line style, fill) -- no two curves differ by colour alone.  Line width and marker size are not part of a shape.
Layout (conf/DECISIONS.md, 2026-10-09 CDT; the web chat's prompt, then the user's two instructions): pilot-only LMMSE read after
the first iteration (F22 (a) draws the same receiver after 16); 95% Wilson bars (each point's own n) only on Proposed, GMM prior,
Gaussian prior, Perfect CSI; (a) y log (2e-4, 1.2) -- kept only while no point is a zero-failure point and no point or lower bar
end is below 2e-4, else the FIGHS16e4 §1 limit 3e-5 with fighs_merge.zero_arrows (the record says which); x ticks at the SNR
points, range (-4, 16); (b) x as F16b_col, y linear, a K label under a GMM point only where K changes; one legend band whose
three columns are the families, 7 pt; bold 7.5 pt panel labels at the same spot inside both panels; STIXGeneral.
Saved at exactly figsize (no tight crop), PNG at 300 dpi, TrueType fonts.  Output next to this script, or in $FIG_OUTDIR.
Run (CPU, about 3 minutes):
  cd ~/t2/conf && CUDA_VISIBLE_DEVICES= ~/miniforge3/envs/torch/bin/python -B ~/t2/conference/figures/paper_f16deep.py \\
      > ~/t2/conference/figures/records/paper_f16deep.txt
"""
import collections
import contextlib
import difflib
import functools
import io
import os
import re
import sys
from unittest import mock

sys.dont_write_bytecode = True                                 # no __pycache__ next to the paper_f*.py or in conf/code
import paper_f16 as P                                          # the reference run for (b); puts conf/code on sys.path
import matplotlib.pyplot as plt
RC16 = plt.rcParams.copy()                                     # paper_f16's rcParams: restored for its reference run
import paper_f16col as Q                                       # curves(), same(), inch(), check(), the one-column sizes
import paper_f18 as F18                                        # only their ARMS style tables are read (no main())
import paper_f21 as F21
import paper_f22 as F22
import paper_f24 as F24
import fighs_merge as M
import matplotlib.figure
import numpy as np
from analysis import load_raw
from matplotlib.lines import Line2D
from matplotlib.path import Path
from matplotlib.transforms import Bbox
from paper_f16 import FIG, S, wilson                          # FIG = this folder or $FIG_OUTDIR; S = figstyle
from scipy.stats import fisher_exact

HERE = os.path.dirname(os.path.abspath(__file__))
REC16 = os.path.join(HERE, "records", "paper_f16.txt")
CELL, PRIOR, SNRS, N0 = "C2", "S2", [-3.0, 0.0, 3.0, 6.0, 9.0, 12.0, 15.0], 2560
BLUE, ORANGE, GREEN, VIOLET, GREY, GREYL = S.V1["color"], S.GMM["color"], P.SPARSE, F24.ALD, F21.GREY, S.GAUSS["color"]
Curve = collections.namedtuple("Curve", "arm orig label family color marker ls filled shape")
# raw arm (load_raw name), its original raw tag, figure name (TERMS.md), legend family, colour, marker, line style, filled?,
# where the shape comes from.  New curves: colour = family, filled = in the loop / hollow = pilot-only, line style = variant.
# All 20 curves of the cell are read and asserted; SHOW below picks the drawn ones (so a different choice is one line).
CURVES = [Curve(*c) for c in (
    ("M-ours-dscore-C-V1", "B16e4k", "Proposed (diffusion prior)", "diffusion", BLUE, "s", "-", True, "paper_f16"),
    ("M-ours-dscore-C-V4", "B16e4k", "Diffusion prior, scalar site", "diffusion", BLUE, "o", "-.", True, "new"),
    ("M-ours-dscore-C-V0", "B16e4k", "Diffusion prior, unrepaired", "diffusion", BLUE, "X", ":", True, "new"),
    ("V1-pilot", "PILB16e4k", "Proposed prior, pilot-only", "diffusion", BLUE, "s", "--", False, "paper_f22"),
    ("ALD-pilot", "ALDB16e4k", "Annealed Langevin (plug-in)", "diffusion", VIOLET, "P", ":", True, "paper_f24"),
    ("ALDv-pilot", "ALDB16e4k", "Annealed Langevin (error-aware)", "diffusion", VIOLET, "P", "--", False, "new"),
    ("M-ours-bstar", "B16e4k", "GMM prior", "GMM", ORANGE, "D", "-", True, "paper_f16"),
    ("M-ours-gmm32", "B16e4k", "GMM prior (K = 32)", "GMM", ORANGE, "p", ":", True, "new"),
    ("M-ours-bstar-scalar", "B16e4k", "GMM prior, scalar site", "GMM", ORANGE, "v", "-.", True, "paper_f18 (points only there: line style new)"),
    ("bstar-pilot", "PILB16e4k", "GMM prior, pilot-only", "GMM", ORANGE, "D", "--", False, "paper_f22"),
    ("R2-ours-G", "B16e4k", "Gaussian prior", "Gaussian", GREYL, "o", "--", True, "paper_f16"),
    ("R1-turbo", "B16e4k", "Turbo LMMSE receiver", "Gaussian", GREY, "^", "-", False, "paper_f21"),
    ("R3-bigamp", "B16e4k", "BiG-AMP", "Gaussian", GREY, "v", "--", False, "paper_f21"),
    ("R4-scvamp", "B16e4k", "SC-VAMP", "Gaussian", GREY, "<", "-.", True, "new"),
    ("R4-llr", "B16e4k", "SC-VAMP (LLR)", "Gaussian", GREY, ">", ":", True, "new"),
    ("R0-pilot@1", "B16e4k", "Pilot-only LMMSE", "Gaussian", GREYL, "o", "--", False, "paper_f22"),
    ("SBL-loop", "SPB16e4k", "SBL (in loop)", "sparse", GREEN, "h", "-", True, "paper_f16"),
    ("SBL-pilot", "SPB16e4k", "SBL (pilot-only)", "sparse", GREEN, "h", "--", False, "paper_f16"),
    ("OMP-pilot", "SPB16e4k", "OMP (pilot-only)", "sparse", GREEN, "X", ":", False, "paper_f16"),
    ("R5-genie", "B16e4k", "Perfect CSI", "Perfect CSI", S.GENIE["color"], "*", "-.", True, "paper_f16"))]
BY = {c.arm: c for c in CURVES}
V1, BS, GE = "M-ours-dscore-C-V1", "M-ours-bstar", "R5-genie"
# the drawn curves, in legend order (column by column): diffusion network | GMM | Gaussian, LMMSE, AMP | sparse | Perfect CSI
SHOW = (V1, "ALD-pilot", BS, "R2-ours-G", "R1-turbo", "R3-bigamp", "R0-pilot@1", "SBL-loop", "SBL-pilot", "OMP-pilot", GE)
ALL6 = (V1, BS, "R2-ours-G", "R1-turbo", "R3-bigamp", "R0-pilot@1", GE)   # (b): the drawn arms the six budget raws hold;
#                                                                           the other four exist at N' = 1.6e5 only (their own raws)
BARS = (V1, BS, "R2-ours-G", GE)                              # 95% Wilson bars, as in F16a_col
# which curves take +6..+15 dB from an n = 20480 raw (found from the raws in main(); a change stops the script: the caption lists them)
HS20480 = {V1: "HSB16e4k", BS: "HSB16e4k", "R2-ours-G": "HSB16e4k", "R1-turbo": "HSB16e4k", "R3-bigamp": "HSB16e4k",
           GE: "HSB16e4k", "R0-pilot@1": "FHB16e4k", "SBL-loop": "FHSPB16e4k", "SBL-pilot": "FHSPB16e4k",
           "OMP-pilot": "FHSPB16e4k", "bstar-pilot": "FHPILB16e4k", "V1-pilot": "FHPILB16e4k"}
N2560 = ("M-ours-dscore-C-V4", "M-ours-dscore-C-V0", "ALD-pilot", "ALDv-pilot", "M-ours-gmm32", "M-ours-bstar-scalar",
         "R4-scvamp", "R4-llr")
# -3 dB failures / 2560 as the task prompt lists them (a second anchor next to the record files read in main())
REC3 = {GE: 87, V1: 371, BS: 623, "M-ours-bstar-scalar": 657, "M-ours-gmm32": 675, "R0-pilot@1": 1918, "R1-turbo": 1389,
        "R2-ours-G": 839, "R3-bigamp": 1391, "R4-llr": 2217, "R4-scvamp": 1561, "bstar-pilot": 978, "V1-pilot": 626,
        "ALD-pilot": 833, "ALDv-pilot": 852, "M-ours-dscore-C-V0": 1517, "M-ours-dscore-C-V4": 394, "SBL-loop": 705,
        "SBL-pilot": 934, "OMP-pilot": 1023}
W, H = 7.16, 2.75                                             # in (prompt item 5: height <= 2.9, target 2.75)
LEFT, RIGHT, BOTTOM, BAND, TOP = 0.50, 0.05, 0.36, 0.58, 0.03  # margins; BAND = the legend band above the axes, TOP = air under it
GAP_B, W_B = 0.47, 2.00                                        # before (b) (its y ticks + label); width of (b)
YLIM, XLIM = (Q.YLO, 1.2), (-4, 16)
YLIM_B, YTICKS_B = (0, 0.9), [0, 0.2, 0.4, 0.6, 0.8]           # (b): linear, wide enough for every drawn curve; the panel label clears the 0.8 grid line
LAB_XY, LAB_PT, K_PT, K_GAP = (0.985, 0.97), 7.5, 7, 1.0       # panel label: axes fraction of its upper-right corner; sizes, K-label gap [pt]
RC = {**Q.RC, "legend.fontsize": 7, "axes.grid": True, "grid.alpha": 0.25, "grid.linewidth": 0.5, "figure.dpi": 200}
ARM, THIN = dict(lw=1.1, ms=3.4, star=5.6, capsize=1.4, elinewidth=0.7), dict(lw=0.85, ms=3.0, mew=0.7)
LW_V1, MS_V1, MS_HEX = 1.6, 4.0, 3.8   # the proposed curve heavier (F21 does the same); the two hexagons larger, so the hollow 'h' of
#                                         SBL (pilot-only) reads next to the hollow 'o' of Pilot-only LMMSE in greyscale too
LEG_GAP = 3                            # legend: one empty slot after the learned priors, so that its three columns are the families
NEAR_PT = 1.5                          # record: marker centres of two curves closer than this are listed (one hides or touches the other)
USER = ("모든 figure에 같은 legend의 그래프가 포함되어야 해.",  # the user's two instructions, verbatim (session of 2026-10-09 CDT)
        "한 figure에 20개를 다 넣을 수는 없지 않아? 우리 proposed 가 잘 부각되는 것으로 골라서 그리자. 필수 baseline(OMP 등등)은 반드시 포함시키고")


@functools.lru_cache(maxsize=None)                             # each raw is read once (the n = 20480 raws serve several arms)
def raw(tag):
    d, _, w = load_raw("D2", root=os.path.join(M.CONF, f"raw_{tag}"))
    assert not [x for x in w if "WARNING" in x], (tag, w)      # NOTE lines = raised blocks, kept as failures (fighs_merge._load)
    return d


def count(d, snr, arm):
    """failures, trials, raised blocks of an arm at one SNR, read at its last iteration (the alias R0-pilot@1 has one column)"""
    e = np.asarray(d[(CELL, PRIOR, snr)][arm]["blk_err"], float)[:, -1]
    return int(np.where(np.isfinite(e), e, 1.0).sum()), len(e), int((~np.isfinite(e)).sum())   # a raised block is a failure


def hs_source(orig, arm):
    """the n = 20480 raw of a curve (FIGHS16e4 §0.1 = fighs_merge.hs_tag; the alias R0-pilot@1 follows its arm R0-pilot), or
    None when that raw does not exist or does not have the arm (the curve then keeps its original raw at every SNR)"""
    tag = M.hs_tag(orig, arm.split("@")[0])
    if not os.path.isdir(os.path.join(M.CONF, f"raw_{tag}")):
        return None
    d = raw(tag)
    has = [arm in d.get((CELL, PRIOR, s), {}) for s in M.HS]
    assert all(has) or not any(has), (tag, arm, has)
    return tag if all(has) else None


def rising(k, n):
    """cells where BLER rises with SNR, with the one-sided Fisher p -- the 'rising' text of fighs_merge.merge"""
    return [f"{SNRS[i]:+.0f}->{SNRS[i + 1]:+.0f} dB p={fisher_exact([[k[i + 1], n[i + 1] - k[i + 1]], [k[i], n[i] - k[i]]], alternative='greater').pvalue:.2g}"
            for i in range(len(k) - 1) if k[i + 1] * n[i] > k[i] * n[i + 1]]


def rec_rows(path, start, n_int=7):
    """{arm: [counts]} from a record file: the count rows after the first line starting with `start`, up to the first other line"""
    with open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    i = next(j for j, l in enumerate(lines) if l.startswith(start))
    out = {}
    for l in lines[i + 1:]:
        m = re.match(r"\s+(?:\(not drawn\) )?(\S+?)(?:\s+@16)?((?:\s+\d+){%d})(?:\s+\(raw_\w+\))?\s*$" % n_int, l)
        if not m:
            break
        out[m[1]] = [int(x) for x in m[2].split()]
    return out


def rec_fighs(path, head):
    """{arm: (k x4, n x4, raw tag)} from a record's 'FIGHS16e4 merge' block: the rows under the panel line starting with `head`"""
    with open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    lines = lines[next(j for j, l in enumerate(lines) if l.startswith("FIGHS16e4 merge")):]
    out = {}
    for l in lines[next(j for j, l in enumerate(lines) if l.startswith(head)) + 1:]:
        m = re.match(r"    (\S+)\s+@16  ((?:\d+/\d+ ?){4})\s+\(raw_(\w+)\)", l)
        if not m:
            break
        kn = [tuple(int(x) for x in t.split("/")) for t in m[2].split()]
        out[m[1]] = ([a for a, _ in kn], [b for _, b in kn], m[3])
    return out


def rec_table_a(tag):
    """{arm: 'BLER(lo,hi)' at -3 dB} from the cell C2 block of conf/results/tables_D2_<tag>.txt (TABLE A; R0-pilot = its '(@1)' row)"""
    with open(os.path.join(M.CONF, "results", f"tables_D2_{tag}.txt"), encoding="utf-8") as f:
        lines = f.read().split("\n")
    i = next(j for j, l in enumerate(lines) if l.startswith(f"--- cell {CELL} (") and f"prior {PRIOR} " in l)
    i = next(j for j in range(i, i + 4) if re.match(r"  arm\s+SNR -3 dB\s", lines[j]))        # the first SNR column is -3 dB
    out = {}
    for l in lines[i + 1:]:
        if not l.strip():
            break
        m = re.match(r"  (\S+)( \(@1\))?\s+(\d\.\d{3}\(\d\.\d{3},\d\.\d{3}\)) ", l)
        if m:
            out[m[1] + ("@1" if m[2] else "")] = m[3]
    return out


def style(c):
    return (c.color, c.marker, c.ls, c.filled)


def check_styles():
    """a curve already in a paper figure keeps that figure's shape; the shapes (all 20, so any selection) are distinct, also without the colour"""
    old = {lab: (col, mk, ls, True) for _, lab, col, mk, ls in P.ARMS}
    old.update({lab: (P.SPARSE, mk, ls, filled) for _, lab, mk, ls, filled in P.SPARSE_ARMS})
    for src, rows in (("paper_f21", F21.ARMS + F21.SP_ARMS), ("paper_f24", F24.ARMS)):
        for _, _, lab, col, mk, ls, _, filled in rows:
            assert old.setdefault(lab, (col, mk, ls, filled)) == (col, mk, ls, filled), (src, lab)   # the scripts agree
    for _, _, lab, sty, pil in F22.ARMS:                           # paper_f22: pilot-only = the prior's colour, dashed, hollow
        got = (sty["color"], sty["marker"], "--" if pil else sty["ls"], not pil)
        assert old.setdefault(lab, got) == got, ("paper_f22", lab)
    f18 = {lab: (col, mk) for _, _, lab, col, mk in F18.ARMS}      # paper_f18 draws points only (fill = test / development there)
    for c in CURVES:
        if c.shape.startswith("paper_f18"):
            assert c.label not in old and style(c)[:2] == f18[c.label] and c.filled, (c.label, style(c), f18[c.label])
        else:
            assert (c.label in old) == (c.shape != "new") and (c.shape == "new" or style(c) == old[c.label]), (c.label, style(c), old.get(c.label))
    assert len({style(c) for c in CURVES}) == len({style(c)[1:] for c in CURVES}) == len({c.label for c in CURVES}) == len(CURVES) == 20
    assert len(set(SHOW)) == len(SHOW) and set(ALL6) <= set(SHOW) <= set(BY), SHOW


def size(c):
    """line width / marker size -- not part of a curve's kept shape: the proposed curve heavier, the other bar arms ARM, the rest THIN"""
    if c.arm == V1:
        return dict(lw=LW_V1, ms=MS_V1)
    if c.arm in BARS:
        return dict(lw=ARM["lw"], ms=ARM["star"] if c.marker == "*" else ARM["ms"])
    return dict(THIN, ms=MS_HEX) if c.marker == "h" else dict(THIN)


def draw(ax, c, x, k, n, z):
    """one curve: BLER = k/n, each point's own n; a zero-failure point breaks the curve (fighs_merge: Perfect CSI gets the arrow)"""
    ok = k > 0
    p = np.where(ok, k / n, np.nan)
    kw = dict(color=c.color, marker=c.marker, ls=c.ls, mfc=c.color if c.filled else "white", label=c.label, **size(c))
    if c.arm in BARS:                                              # errorbar puts its data line at zorder + 0.1: the curve at z, its bars and caps under it
        lo, hi = (np.where(ok, v, np.nan) for v in wilson(k, n))
        ax.errorbar(x, p, yerr=[np.maximum(p - lo, 0), hi - p], capsize=ARM["capsize"], elinewidth=ARM["elinewidth"], zorder=z - 0.1, **kw)
    else:
        ax.plot(x, p, zorder=z, **kw)
    if c.arm == GE:
        M.zero_arrows(ax, np.asarray(x)[~ok], n[~ok], c.color)
    d = Q.curves(ax)[c.label]                                      # what is drawn = what was counted: points and bar ends read back
    assert Q.same(d["x"], x) and Q.same(d["y"], p) and (c.arm not in BARS or (Q.same(d["lo"], lo) and Q.same(d["hi"], hi))), c.label
    return p


def proxy(c):
    """legend handle: line + marker, no error bar"""
    return Line2D([], [], color=c.color, marker=c.marker, ls=c.ls, mfc=c.color if c.filled else "white",
                  label=c.label.replace("(K =", "($K$ ="), **size(c))


def hits(ax, bb, pad):
    """labels of the drawn data of `ax` (curve segments, markers, error bars and caps, reference lines) within `pad` px of the box bb"""
    bb = Bbox.from_extents(bb.x0 - pad, bb.y0 - pad, bb.x1 + pad, bb.y1 + pad)
    out = set()
    for l in ax.lines:
        xy = l.get_transform().transform(l.get_xydata())
        fin = np.isfinite(xy).all(axis=1)
        r = l.get_markersize() / 2 * ax.figure.dpi / 72 if l.get_marker() not in ("None", "", None) else 0.0
        ry = 0.0 if l.get_marker() == "_" else r                   # an error-bar cap is a horizontal tick
        if any(bb.overlaps(Bbox.from_extents(x - r, y - ry, x + r, y + ry)) or bb.contains(x, y) for x, y in xy[fin]):
            out.add(l.get_label())
        if l.get_linestyle() not in ("None", "", " "):
            out |= {l.get_label() for i in range(len(xy) - 1) if fin[i] and fin[i + 1] and Path(xy[i:i + 2]).intersects_bbox(bb, filled=False)}
    for col in ax.collections:                                     # error bars
        out |= {"error bar" for s in col.get_segments() if len(s) and Path(col.get_transform().transform(s)).intersects_bbox(bb, filled=False)}
    return sorted(out)


def coincide(ax, pt):
    """pairs of drawn curves whose marker centres at the same x are closer than `pt` points: [(label, label, [x, ...])]"""
    xy = {l: (c["x"], ax.transData.transform(np.column_stack([c["x"], c["y"]]))) for l, c in Q.curves(ax).items()}
    out = []
    for i, a in enumerate(xy):
        for b in list(xy)[i + 1:]:
            at = [x for x, p in zip(*xy[a]) for y, q in zip(*xy[b])
                  if x == y and np.isfinite(p).all() and np.isfinite(q).all() and np.hypot(*(p - q)) * 72 / ax.figure.dpi < pt]
            if at:
                out.append((a, b, at))
    return out


def main():
    check_styles()
    # ---------------- reference: paper_f16.main() itself, in this process (its (b) artists; the seven curves of its (a)) ----------------
    plt.rcParams.update(RC16)
    buf = io.StringIO()
    with mock.patch.object(matplotlib.figure.Figure, "savefig"), contextlib.redirect_stdout(buf):
        P.main()
    ref = buf.getvalue()
    with open(REC16, encoding="utf-8") as f:
        rec = f.read()
    if ref != rec:
        raise SystemExit("paper_f16.main() no longer prints records/paper_f16.txt -- stopped, nothing written:\n" + "\n".join(
            difflib.unified_diff(rec.splitlines(), ref.splitlines(), "records/paper_f16.txt", "paper_f16.main()", lineterm="")))
    a1, a2 = plt.gcf().axes[:2]                                    # its (a) SNR axis, (b) budget axis
    A, B = Q.curves(a1), Q.curves(a2)
    bud = re.findall(r"^  N=\S+ (\S+)\s+b\*=kron (\d+)\s+D1-sibling gate (PASS|FAIL)", ref, re.M)   # (raw tag, GMM K, recipe gate) of the six budgets
    tags, K, gate = [t for t, _, _ in bud], [int(k) for _, k, _ in bud], [g for _, _, g in bud]
    NB = B[BY[BS].label]["x"]                                      # the six budgets = the x of its GMM curve
    assert K == Q.K_REC and len(tags) == len(NB) == 6 and (tags[2], NB[2]) == ("B16e4k", 1.6e5), (tags, K, NB)

    # ---------------- (a): the 20 curves of the cell from raw (-3..+15 dB, n = 2560), then the FIGHS16e4 merge ----------------
    src = {t: raw(t) for t in ("B16e4k", "PILB16e4k", "ALDB16e4k", "SPB16e4k")}
    keys = [(CELL, PRIOR, s) for s in SNRS]
    for t, d in src.items():                                       # same grid; same trials: Perfect CSI error arrays identical
        assert sorted(k for k in d if k[:2] == (CELL, PRIOR)) == keys, (t, sorted(d))
        for key in keys:
            assert np.array_equal(src["B16e4k"][key][GE]["blk_err"], d[key][GE]["blk_err"], equal_nan=True), (t, key)
    tab = rec_rows(os.path.join(M.RV, "pairB_STB16e4k.txt"), "BLER@16 failures / n per SNR -3 +0 +3 +6 +9 +12 +15 dB:")
    f31 = rec_rows(os.path.join(HERE, "records", "paper_f31.txt"), "(b) D2 C2 (raw_B16e4k + raw_SPB16e4k), failures / 2560 per SNR -3 +0 +3 +6 +9 +12 +15 dB:")
    f21 = rec_rows(os.path.join(HERE, "records", "paper_f21.txt"), "(a) D2 sparse specular, 8×4 (headline) -- raw_B16e4k, cell C2, prior S2")
    f22 = rec_rows(os.path.join(HERE, "records", "paper_f22.txt"), "(a) D2 sparse specular, 8×4 (headline) -- raw_B16e4k + raw_PILB16e4k, cell C2, prior S2")
    assert len(tab) == 19 and len(f31) == 6 and len(f21) == 17 and len(f22) == 6, (len(tab), len(f31), len(f21), len(f22))
    hs_rec = {}                                                    # arm -> (k, n, tag) of the +6..+15 dB points, per record
    for name, head in (("paper_f16.txt", "  (a) D2 C2:"), ("paper_f21.txt", "  (a) raw_B16e4k + raw_SPB16e4k, cell C2:"),
                       ("paper_f22.txt", "  (a) raw_B16e4k + raw_PILB16e4k, cell C2:")):
        for arm, v in rec_fighs(os.path.join(HERE, "records", name), head).items():
            assert hs_rec.setdefault(arm, v) == v, (name, arm, v, hs_rec[arm])   # the three records agree where they overlap
    assert len(hs_rec) == 12, sorted(hs_rec)                       # 11 of the curves below + R0-pilot read @16 (F22)
    cur, lines, checked = {}, {}, collections.Counter()
    for c in CURVES + [Curve("R0-pilot", "B16e4k", "(not drawn: the pilot-only LMMSE after 16 iterations, as F22 (a))", *[None] * 6)]:
        cnt = [count(src[c.orig], s, c.arm) for s in SNRS]
        k0, n0, raised = np.array([x[0] for x in cnt]), np.array([x[1] for x in cnt]), sum(x[2] for x in cnt)
        assert set(n0.tolist()) == {N0}, (c.arm, n0)
        for name, t in (("pairB_STB16e4k.txt", tab), ("paper_f31.txt (b)", f31), ("paper_f21.txt (a)", f21), ("paper_f22.txt (a)", f22)):
            if c.arm in t:
                assert k0.tolist() == t[c.arm], (name, c.arm, k0.tolist(), t[c.arm])
                checked[c.arm] += 1
        assert c.arm not in REC3 or k0[0] == REC3[c.arm], (c.arm, k0[0])
        tag = hs_source(c.orig, c.arm)
        if tag:                                                    # fighs_merge.merge: asserts n = 20480 and raw = count table
            with mock.patch.object(M, "hs_tag", lambda o, a, t=tag: t) if M.hs_tag(c.orig, c.arm) != tag else contextlib.nullcontext():
                k, n, line = M.merge(SNRS, k0, n0, c.orig, CELL, PRIOR, c.arm)   # (the alias R0-pilot@1 is mapped to its arm's raw)
            assert line.rstrip().endswith(f"(raw_{tag})" + (f"   rising: {'; '.join(rising(k, n))}" if rising(k, n) else "")), line
            if c.arm in hs_rec:
                assert (k[3:].tolist(), n[3:].tolist(), tag) == hs_rec[c.arm], (c.arm, k, n, tag, hs_rec[c.arm])
                checked[c.arm] += 1
            else:
                assert c.arm == "R0-pilot@1", c.arm                # in no figure record yet: count table only (fighs_FHB16e4k.txt)
        else:
            k, n = k0.copy(), n0.copy()
        assert np.array_equal(k[:3], k0[:3]) and np.array_equal(n[:3], n0[:3]) and set(n[3:].tolist()) == ({M.N_HS} if tag else {N0})
        cur[c.arm] = (k, n, tag, raised)
        lines[c.arm] = (f"    {c.arm:<21}" + " ".join(f"{a}/{b}" for a, b in zip(k, n)) + f"   -3..+3 dB raw_{c.orig}, +6..+15 dB "
                        + (f"raw_{tag}" if tag else f"raw_{c.orig} (n = 2560 at every SNR: no n = 20480 raw has this arm)")
                        + (f"; raised blocks counted as failures: {raised}" if raised else "")
                        + (f"   rising: {'; '.join(rising(k, n))}" if rising(k, n) else ""))
    r16 = cur.pop("R0-pilot"); line16 = lines.pop("R0-pilot")
    assert all(checked[c.arm] >= (2 if cur[c.arm][2] and c.arm != "R0-pilot@1" else 1) for c in CURVES), checked
    assert set(REC3) == set(cur), set(REC3) ^ set(cur)             # the prompt's -3 dB values: all 20 curves
    got = {a: v[2] for a, v in cur.items() if v[2]}
    assert got == HS20480 and sorted(set(cur) - set(got)) == sorted(N2560), (got, sorted(set(cur) - set(got)))
    for lab, a in A.items():                                       # the seven curves F16 (a) draws: all drawn here, same points, same bar ends
        c = next(c for c in CURVES if c.label == lab)
        k, n = cur[c.arm][:2]
        y, (lo, hi) = np.where(k > 0, k / n, np.nan), (np.where(k > 0, v, np.nan) for v in wilson(k, n))   # a zero-failure point is NaN there (paper_f16.py:98)
        assert c.arm in SHOW and Q.same(a["x"], SNRS) and Q.same(a["y"], y), lab
        assert (a["lo"] is None) == (c.arm not in BARS) and (a["lo"] is None or (Q.same(a["lo"], lo) and Q.same(a["hi"], hi))), lab
    zero = [(BY[a].label, s) for a in SHOW for s, x in zip(SNRS, cur[a][0]) if x == 0]
    pts = [(x / m, BY[a].label, s) for a in SHOW for s, x, m in zip(SNRS, *cur[a][:2]) if x > 0]
    ends = [(wilson(x, m)[0], BY[a].label, s) for a in BARS for s, x, m in zip(SNRS, *cur[a][:2]) if x > 0]
    low, lowbar = min(pts), min(ends)
    cond = not zero and min(low[0], lowbar[0]) > YLIM[0]
    ylim = YLIM if cond else (Q.YLO_RULE, YLIM[1])                 # the prompt's 2e-4, else the FIGHS16e4 §1 limit (zero_arrows visible)
    assert set(BARS) <= set(SHOW) and max(p[0] for p in pts) < ylim[1] and (cond or min(low[0], lowbar[0]) > ylim[0]), (low, lowbar, ylim)

    # ---------------- (b): -3 dB at the six budgets for the arms the budget raws hold; the other drawn curves at 1.6e5 only ----------------
    hidden = [c.arm for c in CURVES if c.arm not in SHOW]
    hid6 = tuple(a for a in hidden if BY[a].orig == "B16e4k")      # not drawn, but in the six budget raws: counted for the record only
    bud_k = {a: [] for a in ALL6 + hid6}
    for tag in tags:
        d, ta = raw(tag), rec_table_a(tag)
        for a in bud_k:
            k, n, _ = count(d, -3.0, a)
            lo, hi = wilson(k, n)
            assert n == N0 and ta[a] == f"{k / n:.3f}({lo:.3f},{hi:.3f})", (tag, a, k, n, ta.get(a))   # = TABLE A of that budget
            bud_k[a].append(k)
    bud_k = {a: np.array(v) for a, v in bud_k.items()}
    for a in (BS, V1, GE):                                         # = the (b) artists of paper_f16 (points and Wilson bar ends)
        b, (lo, hi) = B[BY[a].label], wilson(bud_k[a], N0)
        assert Q.same(b["x"], NB) and Q.same(b["y"], bud_k[a] / N0) and Q.same(b["lo"], lo) and Q.same(b["hi"], hi), a
    assert np.ptp(bud_k[GE]) == 0 and all(bud_k[a][2] == cur[a][0][0] for a in ALL6), bud_k   # Perfect CSI flat; 1.6e5 = the -3 dB point of (a)
    one = [a for a in SHOW if a not in ALL6]                       # measured at N' = 1.6e5 only: their -3 dB point of (a)
    v_k, v_n = cur[V1][:2]
    for a in SHOW:                                                 # the proposed curve is below every other drawn curve but Perfect CSI
        if a not in (V1, GE):
            assert (v_k * cur[a][1] < cur[a][0] * v_n).all() and (a not in ALL6 or (bud_k[V1] < bud_k[a]).all()), a   # exact in integers
    assert all(bud_k[V1].max() < cur[a][0][0] for a in one) and (bud_k[GE] < bud_k[V1]).all() and (cur[GE][0] * v_n < v_k * cur[GE][1]).all()
    v_hi, b_hi = wilson(v_k, v_n)[1], wilson(bud_k[V1], N0)[1]     # the upper ends of the proposed curve's drawn 95% Wilson bars
    reach = {a: [f"{s:+.0f} dB {x}/{m} vs {vk}/{vn}" for s, x, m, vk, vn in zip(SNRS, *cur[a][:2], v_k, v_n) if x * vn <= vk * m] for a in hidden}
    inbar = {a: [f"{s:+.0f}" for s, x, m, vk, vn, hi in zip(SNRS, *cur[a][:2], v_k, v_n, v_hi) if x * vn > vk * m and x / m <= hi] for a in hidden}
    reach_b = {a: [f"raw_{t} {x} vs {vk}" for t, x, vk in zip(tags, bud_k[a], bud_k[V1]) if x <= vk] for a in hid6}
    inbar_b = {a: [t for t, x, vk, hi in zip(tags, bud_k[a], bud_k[V1], b_hi) if x > vk and x / N0 <= hi] for a in hid6}
    with open(os.path.join(M.RV, "pairB_SPB16e4k.txt"), encoding="utf-8") as f:   # the registered gaps and labels of the 16 baselines
        sp = f.read()
    gap = dict(re.findall(r"SNR@0\.1 gap \((\S+) minus V1\): ((?:>= )?[+-]\d+\.\d+) dB", sp))
    lab = dict(re.findall(r"(\S+)=(\([iv]+\))", next(l for l in sp.split("\n") if l.startswith("    M-ours-bstar=("))))
    assert len(gap) == 16 and set(gap) == set(lab) == set(BY) - {V1, GE, "M-ours-dscore-C-V0", "M-ours-dscore-C-V4"}, (sorted(gap), sorted(lab))
    order = sorted(gap, key=lambda a: (gap[a].startswith(">"), float(gap[a].lstrip(">= "))))
    with open(os.path.join(M.RV, "pairB_SITEB16e4k.txt"), encoding="utf-8") as f:   # V4 -> V1 (SITE16e4)
        site = f.read().split("# step 2")[1]
    v4 = (re.search(r"gap \(M-ours-dscore-C-V4 minus M-ours-dscore-C-V1\): ([+-]\d+\.\d+) dB", site)[1], re.search(r"-> (\([iv]+\))", site.split("POWERED")[1])[1])
    top_b = max(max(wilson(bud_k[a], N0)[1].max() if a in BARS else bud_k[a].max() / N0 for a in ALL6), max(cur[a][0][0] / N0 for a in one))
    assert top_b < YLIM_B[1], top_b

    # ---------------- draw ----------------
    plt.rcParams.update(RC)                                        # this figure's style, only after the reference run
    fig = plt.figure(figsize=(W, H))
    h = H - BOTTOM - BAND - TOP
    ax = fig.add_axes([LEFT / W, BOTTOM / H, (W - LEFT - RIGHT - GAP_B - W_B) / W, h / H])
    bx = fig.add_axes([(W - RIGHT - W_B) / W, BOTTOM / H, W_B / W, h / H])
    for a in SHOW:                                                 # Proposed on top, then GMM prior, Perfect CSI, the rest in legend order
        z = {V1: 5, BS: 4, GE: 3}.get(a, 2.9 - 0.05 * SHOW.index(a))
        draw(ax, BY[a], SNRS, *cur[a][:2], z)
        if a in ALL6:
            draw(bx, BY[a], NB, bud_k[a], np.full(6, N0), z)
        else:
            draw(bx, BY[a], NB[2:3], cur[a][0][:1], cur[a][1][:1], z)
    ax.set_yscale("log"); ax.set_ylim(*ylim); ax.set_xticks(SNRS); ax.set_xlim(*XLIM)
    ax.set_xlabel(a1.get_xlabel(), labelpad=Q.XPAD); ax.set_ylabel(a1.get_ylabel()); ax.tick_params(axis="x", pad=Q.XTPAD)
    bx.set_xscale("log"); bx.set_xlim(6e3, 2.2e6); bx.set_ylim(*YLIM_B); bx.set_yticks(YTICKS_B)
    bx.set_xlabel("Training set size $\\mathit{N}$′ (channels)", labelpad=Q.XPAD); bx.set_ylabel(a2.get_ylabel())   # as F16b_col
    bx.tick_params(axis="x", pad=Q.XTPAD)
    g_lo = wilson(bud_k[BS], N0)[0]
    k_at = [i for i in range(len(K)) if i == 0 or K[i] != K[i - 1]]   # a K label only where K changes; under the GMM point
    kt = [bx.annotate(f"$K$ = {K[i]}" if i == 0 else str(K[i]), (NB[i], g_lo[i]), textcoords="offset points", xytext=(0, -K_GAP),
                      ha="center", va="top", fontsize=K_PT, color=S.INK) for i in k_at]
    pl = [a.text(*LAB_XY, tag, transform=a.transAxes, ha="right", va="top", fontsize=LAB_PT, fontweight="bold", color=S.INK, zorder=7)
          for a, tag in ((ax, "(a)"), (bx, "(b)"))]
    hl = [proxy(BY[a]) for a in SHOW]
    hl.insert(LEG_GAP, Line2D([], [], ls="none", label=""))        # the empty slot that makes the three columns the families
    leg = fig.legend(hl, [x.get_label() for x in hl], loc="center", ncol=3, frameon=False, fontsize=7,
                     bbox_to_anchor=(0.5, (H - BAND / 2) / H), handlelength=2.3, columnspacing=2.2, labelspacing=0.28,
                     borderpad=0.1, handletextpad=0.5)

    # ---------------- geometry and overlap checks ----------------
    fig.canvas.draw()
    px = 72 / fig.dpi                                              # pt per pixel
    k_shift = max(0.0, (bx.get_window_extent().x0 + 2.0 / px - kt[0].get_window_extent().x0) * px)
    kt[0].xyann = (k_shift, -K_GAP)                                # "K = 512" is centred on its point unless it would reach the left axis: 2 pt kept
    bb, small = Q.check(fig, "F16deep_wide")                      # every artist inside the canvas; every visible text >= 7 pt
    pos = [np.array(a.get_position().extents) * [W, H, W, H] for a in (ax, bx)]
    assert np.allclose(pos[0][[1, 3]], pos[1][[1, 3]], rtol=0, atol=1e-12), pos                    # same bottom, top (and height)
    lb = Q.inch(fig, leg.get_window_extent())
    assert lb[1] >= H - BAND and lb[3] <= H and lb[0] >= 0 and lb[2] <= W, ("legend outside its band", lb)
    lt = [t for t in leg.get_texts() if t.get_text()]
    rows = sorted({round(t.get_window_extent().y0) for t in lt})
    cols = collections.defaultdict(set)
    for t, a in zip(lt, SHOW):
        cols[round(t.get_window_extent().x0)].add(BY[a].family)
    assert len(lt) == len(SHOW) and len(rows) <= 4 and [cols[x] for x in sorted(cols)] == [{"diffusion", "GMM"}, {"Gaussian"}, {"sparse", "Perfect CSI"}], (rows, cols)
    clear = {}
    for a, t in zip((ax, bx), pl):                                 # panel label: same spot, nothing drawn within 1.5 pt of it
        e = t.get_window_extent()
        at = a.transAxes.inverted().transform((e.x1, e.y1))
        assert np.allclose(at, LAB_XY, rtol=0, atol=1e-6), (t.get_text(), at)
        near = hits(a, e, 1.5 / px)
        assert not near, (t.get_text(), near)
        clear[t.get_text()] = min(d for d in np.arange(1.5, 40.5, 0.5) if hits(a, e, (d + 0.5) / px) or d == 40)
    kb = [t.get_window_extent() for t in kt]
    for i, e in enumerate(kb):                                     # K labels: 2 pt apart, off the left axis, 0.5 pt clear of curves, markers, bars
        assert all(o.x0 - e.x1 >= 2.0 / px for o in kb[i + 1:i + 2]) and e.x0 - bx.get_window_extent().x0 >= 2.0 / px - 1e-6, ("K labels", i)
        assert not hits(bx, e, 0.5 / px), ("K label over data", i, hits(bx, e, 0.5 / px))
    near_a, near_b = ("; ".join(f"{a} / {b} at " + ", ".join(f(x) for x in at) for a, b, at in coincide(a_, NEAR_PT)) or "none"
                      for a_, f in ((ax, lambda x: f"{x:+.0f} dB"), (bx, lambda x: f"{x:.3g}")))
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(FIG, f"F16deep_wide.{ext}"), dpi=300, **({"metadata": {"CreationDate": None}} if ext == "pdf" else {}))

    # ---------------- record ----------------
    name = lambda a: BY[a].label
    fmt = lambda arms: "; ".join(name(a) for a in arms)                # the names have commas
    k_txt = ", ".join(f"{K[i]} at {NB[i]:.3g}" for i in k_at)
    hs_show, n_show = [a for a in SHOW if cur[a][2]], [a for a in SHOW if not cur[a][2]]
    txt = ["F16deep -- the headline cell: D2 C2 (Sparse specular 8x4, T=16, Tp=4), prior S2, BLER@16 unless stated; (a) at the equal budget "
           "N_train = 1.6e5 (checkpoint d2sx_N160000_a1.pt, last-epoch EMA; b* = kron K=1024), (b) at -3 dB over the six budgets.  Recomputed "
           "from raw by conference/figures/paper_f16deep.py (read-only; analysis.load_raw, a raised block = a failure); no number transcribed.", "",
           f"F16deep_wide  {W} x {H} in ({W * 72:.2f} x {H * 72:.2f} pt), one figure* file, two panels, one legend; every panel draws the "
           f"curves of that legend ({len(SHOW)} curves).", "",
           "Selection.  User, 2026-10-09 CDT, in the session that made this file (verbatim): \"" + USER[0] + "\"; \"" + USER[1] + "\".  "
           "Rule applied by the recorder: drawn = the seven curves of the present Fig. 2 (a) + the receivers / estimators in the form the "
           "literature gives them (Turbo LMMSE receiver, BiG-AMP, Pilot-only LMMSE, Annealed Langevin with the plug-in use of the estimate); not "
           "drawn = the authors' own variants, adaptations and controls (GMM prior with K = 32 / scalar site / pilots only; the two SC-VAMP "
           "adaptations; the error-aware Annealed Langevin variant; the proposed prior on the pilots only; V0; V4).  Selection condition "
           "(asserted, point estimates, exact in integers -- a condition the drawn set was chosen to meet, not a test result): the proposed curve "
           "is below every other drawn curve except Perfect CSI at each of the 7 SNRs of (a) and at each budget of (b), and above Perfect CSI "
           "everywhere.  This figure tests nothing; the registered paired tests are in the files named below.", "",
           f"Drawn, in legend order (internal arm -> figure name; where it is in (b)) -- {len(SHOW)} curves:"]
    txt += [f"    {a:<21}-> {name(a):<28} (b): " + ("the six budgets" if a in ALL6 else "N' = 1.6e5 only (no raw at the other budgets)") for a in SHOW]
    txt += ["", "Registered SNR gain at BLER 0.1 of the proposed prior over each of the 16 baselines [dB] and the table-B label "
            "(results/review_next/pairB_SPB16e4k.txt), smallest gain first; * = not drawn:",
            "    " + "; ".join(f"{'' if a in SHOW else '*'}{name(a)} {gap[a]} {lab[a]}" for a in order) + ".",
            f"    The {sum(a not in SHOW for a in order)} not-drawn baselines are ranks {', '.join(str(i + 1) for i, a in enumerate(order) if a not in SHOW)} of 16 (1 = nearest to "
            "the proposed prior).  Annealed Langevin: the drawn curve is the plug-in use; the error-aware variant (the authors' addition, the "
            "stronger of the two in NEXT_EXPERIMENTS_ALD16e4) is not drawn.  Diffusion prior, scalar site (V4) is a control, not one of the 16: "
            f"SNR gain {v4[0]} dB, label {v4[1]} = not decided (results/review_next/pairB_SITEB16e4k.txt; rule-fixed post-hoc computation SITE16e4).",
            "", "(a) Failures / trials per SNR -3 +0 +3 +6 +9 +12 +15 dB and the source raw of each point (one point = one raw, never pooled; "
            "FIGHS16e4 §1 through fighs_merge.merge; 'rising' = a cell where BLER rises with SNR, one-sided Fisher p, reported only):"]
    txt += [lines[a] for a in SHOW]
    txt += ["", "(b) Failures / 2560 at -3 dB over the training budgets (test trials 0..2559 at every budget; last-epoch EMA weights; the GMM "
            "fit and the score network use the same N_train channels; the same six raws as F16 (b)):",
            f"    {'N_train':<21}" + " ".join(f"{x:>9.3g}" for x in NB),
            f"    {'raw_':<21}" + " ".join(f"{t:>9}" for t in tags),
            f"    {'K of the GMM prior':<21}" + " ".join(f"{x:>9}" for x in K),
            f"    {'D1-sibling gate':<21}" + " ".join(f"{g:>9}" for g in gate) + "   (recipe gate, as records/paper_f16.txt; FAIL = budget-axis measurement)"]
    txt += [f"    {a:<21}" + " ".join(f"{x:>9}" for x in bud_k[a]) for a in ALL6]
    txt += [f"    {a:<21}" + " ".join(f"{(cur[a][0][0] if i == 2 else '-'):>9}" for i in range(6)) + f"   (raw_{BY[a].orig}: N' = 1.6e5 only)" for a in one]
    txt += ["  The sparse baselines use no training set and Annealed Langevin uses the 1.6e5 network of the proposed prior; they were run at "
            "1.6e5 only, so (b) shows their one point.  Perfect CSI is the same at the six budgets (asserted).",
            "", f"(a): +6..+15 dB from n = 20480 new trials (trials 10000..30479), {len(hs_show)} of the drawn curves: " + "; ".join(
                f"{name(a)} (raw_{cur[a][2]})" for a in hs_show) + ".",
            f"(a): n = 2560 (the original test trials 0..2559) at EVERY SNR -- no n = 20480 raw has the arm -- {len(n_show)} of the drawn "
            "curves, to be named in the caption: " + fmt(n_show) + ".",
            "Pilot-only LMMSE = R0-pilot read after the FIRST iteration (alias 'R0-pilot@1' of analysis.load_raw = blk_err[:, 0]; the "
            "manuscript's definition and the registered baseline, pair_baselines --r0 at1).  raw_FHB16e4k holds R0-pilot with all 16 iterations, "
            "so this reading has n = 20480 points (asserted against the 'R0-pilot@1' rows of results/review_next/fighs_FHB16e4k.txt; the task "
            "prompt expected n = 2560).  NEXT_EXPERIMENTS_FIGHS16e4 §1 calls that alias row a reference row its own figures and predictions do "
            "not use (they read every arm @16; raw_FHB16e4k was run for the @16 reading of F22 (a)), and fighs_merge.hs_tag does not route the "
            "alias (this script maps it to its arm's raw): F16deep_wide is the first figure that draws those n = 20480 points -- the §1 'one "
            "point = one raw' rule extended to the @1 reading; same accepted raw, report-only.  From the original raw at every SNR the curve "
            "would be " + " ".join(f"{x}/{N0}" for x in tab["R0-pilot@1"]) + ".  F22 (a) draws the same receiver after 16 iterations: "
            + line16.strip() + f".  At -3 dB: @1 {cur['R0-pilot@1'][0][0]}/{N0}, @16 {r16[0][0]}/{N0}.",
            "Error bars (95% Wilson, each point's own n): " + fmt(BARS) + " only, in both panels; the other curves have none.",
            "Drawn curves with a cell where BLER rises with SNR: " + ("; ".join(f"{name(a)} ({'; '.join(rising(*cur[a][:2]))})" for a in SHOW if rising(*cur[a][:2])) or "none") + ".",
            "Zero-failure points: " + ("; ".join(f"{l} {s:+.0f} dB" for l, s in zero) + " -- the curve breaks there (Perfect CSI: fighs_merge.zero_arrows)" if zero else "none (no arrow, no broken curve)") + ".",
            f"y axis of (a): ({ylim[0]:g}, {ylim[1]:g}) -- " + (f"the prompt's limit {YLIM[0]:g} applied" if cond else f"the prompt's limit {YLIM[0]:g} NOT applied, FIGHS16e4 §1 limit {Q.YLO_RULE:g} instead")
            + f": lowest point {low[0]:.3e} ({low[1]}, {low[2]:+.0f} dB), lowest error-bar end {lowbar[0]:.3e} ({lowbar[1]}, {lowbar[2]:+.0f} dB), zero-failure points {len(zero)}.",
            f"Markers of two drawn curves with centres closer than {NEAR_PT} pt (one hides or touches the other): (a) " + near_a + "; (b) " + near_b + ".",
            "", f"Not drawn ({len(hidden)} of the 20 curves read; manuscript main c7b6762: Table I covers the 16 baselines of this cell in five rows -- "
            "GMM prior, Pilot-only proposed prior, Annealed Langevin (error-aware) and SBL (in loop) by name, the other 12 as one range row; V0 "
            "and V4 are in its text) -- counts as above; the points of (a) where the curve's point estimate is at or below the proposed curve's "
            "(failures/trials vs the proposed curve's), and the SNRs where it is above but inside the proposed curve's drawn 95% Wilson bar:"]
    for a in hidden:
        txt += [f"    {name(a)}:", "    " + lines[a], "        at or below the proposed curve: " + ("; ".join(reach[a]) if reach[a] else "nowhere")
                + ";  inside its bar: " + (", ".join(inbar[a]) + " dB" if inbar[a] else "nowhere")]
    txt += [f"  (b), -3 dB at the six budgets, for the {len(hid6)} not-drawn arms the budget raws hold (failures / 2560; the proposed curve: "
            + " ".join(str(x) for x in bud_k[V1]) + "):"]
    txt += [f"    {a:<21}" + " ".join(f"{x:>5}" for x in bud_k[a]) + "   at or below: " + ("; ".join(reach_b[a]) or "nowhere") + ";  inside its bar at raw_: "
            + (", ".join(inbar_b[a]) or "nowhere") for a in hid6]
    txt += ["    M-ours-dscore-C-V4b (Diffusion prior, scalar site (b)): not read as a curve -- it is not in the manuscript and its definition is "
            "not in the paper-branch records (prompt item 1).  In the code it is V4 with scal='site' instead of 'belief': the denoiser query comes from "
            "the likelihood-only site scalarisation instead of the belief (conf/code/arms.py:361, 366-367; Demo/t2_route_a.py:347-356).  Its counts "
            f"(pairB_STB16e4k.txt): {' '.join(str(x) for x in tab['M-ours-dscore-C-V4b'])} / 2560.",
            "", "Asserts passed (the script stops before saving otherwise):",
            f"  (a) n = 2560 counts = conf/results/review_next/pairB_STB16e4k.txt 'BLER@16 failures' table ({sum(a in tab for a in cur)} arms x 7 SNRs; also R0-pilot @16), "
            f"records/paper_f31.txt (b) ({sum(a in f31 for a in cur)} arms), records/paper_f21.txt (a) ({sum(a in f21 for a in cur)} arms), records/paper_f22.txt (a) "
            f"({sum(a in f22 for a in cur)} arms + R0-pilot @16); -3 dB = the task prompt's {len(REC3)} values -- for all 20 curves, drawn or not.",
            f"  (a) n = 20480 counts = their count tables (fighs_merge.merge) and the 'FIGHS16e4 merge' D2 C2 lines of records/paper_f16.txt, paper_f21.txt, "
            f"paper_f22.txt ({sum(a in hs_rec for a in cur)} curves + R0-pilot @16); Pilot-only LMMSE (@1): count table only.",
            f"  (b) BLER and Wilson interval of the {len(ALL6)} drawn and {len(hid6)} not-drawn arms at the six budgets = the cell C2 block of "
            "conf/results/tables_D2_<raw tag>.txt (TABLE A, three decimals); GMM prior, Proposed, Perfect CSI = the (b) artists of paper_f16.main() "
            "(points, Wilson bar ends; rtol 1e-12); the 1.6e5 column = the -3 dB points of (a).",
            "  same trials: Perfect CSI error arrays of raw_PILB16e4k, raw_ALDB16e4k, raw_SPB16e4k = raw_B16e4k's at the seven SNRs.",
            f"  paper_f16.main() record text = records/paper_f16.txt byte for byte; its (a) artists = the {len(A)} curves it shares with (a) here "
            "(points, Wilson bar ends; rtol 1e-12).",
            "  drawn = counted: the points and the Wilson bar ends of every drawn curve are read back from the artists (rtol 1e-12).",
            "  shapes: curves already in a paper figure = that figure's ARMS table (paper_f16, f18, f21, f22, f24); distinct (colour, marker, "
            "line style, fill) and distinct (marker, line style, fill) over all 20 curves, so over the drawn ones.",
            "", "Shapes (colour, marker, line style, fill) of the 20 curves; 'new' = not in a paper figure before (colour = family, filled = in "
            "the loop / hollow = pilot-only, line style = variant).  Line width and marker size are not part of a shape: the proposed curve is "
            f"drawn heavier (lw {LW_V1}, marker {MS_V1} pt; the other bar curves lw {ARM['lw']}, the rest lw {THIN['lw']}), the two hexagons {MS_HEX} pt:"]
    txt += [f"    {c.label:<32} {c.family:<12} {c.color}  {c.marker!r:<4} {c.ls!r:<5} {'filled' if c.filled else 'hollow':<7} "
            f"{'drawn    ' if c.arm in SHOW else 'not drawn'} {'new' if c.shape == 'new' else 'as ' + c.shape}" for c in CURVES]
    txt += ["", "Layout: axes (left, bottom, right, top) [in] " + "; ".join(f"({t}) {np.round(q, 4).tolist()}" for t, q in zip("ab", pos))
            + f" -- the same bottom / top (asserted); legend band {BAND} in above the axes: one legend, {len(SHOW)} entries in {len(rows)} rows x 3 "
            "columns = the families (learned priors | Gaussian, LMMSE, AMP | sparse, Perfect CSI; one empty slot under the first column; asserted), "
            f"7 pt, no frame, line + marker handles (inside its band: asserted, [in] {np.round(lb, 3).tolist()}).",
            f"  (a) x ticks {' '.join(f'{s:+.0f}' for s in SNRS)} dB, x range {XLIM}; (b) x range (6e3, 2.2e6), y range {YLIM_B} (linear; F16b_col's 0.33 "
            f"does not hold the other curves), K labels where K changes: {k_txt} (K of the six budgets: {' '.join(map(str, K))}); each {K_GAP} pt under "
            f"the lower bar end of its GMM point, centred on it (the first one moved right by {k_shift:.1f} pt to keep 2 pt from the left axis), at "
            "least 2 pt apart; no curve centre line, marker box or bar within 0.5 pt of a label box (asserted).",
            f"  panel labels (a), (b): bold {LAB_PT} pt, upper-right corner at axes fraction {LAB_XY} in both panels (asserted); nearest drawn data "
            "(curve centre line, marker box, error bar) is farther than [pt]: " + ", ".join(f"{t} {d:g}" for t, d in clear.items()) + ".",
            f"  checks: every artist inside the canvas (tight bbox [in] {np.round(bb, 3).tolist()}); smallest visible text {small:g} pt (nominal "
            "size; the exponents of the 10^x tick labels and other sub/superscripts are smaller, about 5.6 pt, as in F16a_col); STIXGeneral / "
            "mathtext stix, TrueType in the PDF; saved at figsize, PNG 300 dpi."]
    print("\n".join(txt))


if __name__ == "__main__":
    main()
