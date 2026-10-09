"""conference/figures/paper_f21sel.py -- the six static scenarios of F21 (paper_f21.py) with the ONE legend of F16deep_wide
(paper_f16deep.py): every panel draws the same 11 curves (user, 2026-10-09 CDT -- paper_f16deep.USER; in that session the user then
chose this figure and kept the 11 curves -- USER2 below).

  F21sel_wide.{pdf,png}   7.16 x 4.57 in, BLER vs SNR at N' = 1.6e5, one legend above the panels
    (a) Sparse specular, 8x4   (b) Sparse specular, 16x4   (c) Sparse specular, CN gains (8x4)
    (d) Clustered SV (Saleh-Valenzuela, 8x4)   (e) 3GPP UMi 28 GHz (8x4)   (f) 3GPP mixed (8x4)
  Curves = paper_f16deep.SHOW with its shapes, sizes and legend: Proposed, Annealed Langevin (plug-in), GMM prior, Gaussian
  prior, Turbo LMMSE receiver, BiG-AMP, Pilot-only LMMSE (read after the first iteration), SBL (in loop), SBL (pilot-only),
  OMP (pilot-only), Perfect CSI.  Nine of them are the curves of F21 (same raws, same merge); the two F21 does not draw are
  the Pilot-only LMMSE (base raw, alias 'R0-pilot@1') and Annealed Langevin (plug-in) (raw_ALD<suffix>).  No error bars, as
  in F21.  Panel (a) is panel (a) of F16deep_wide without its bars.

Nothing is transcribed by hand.  Raws, cells and priors are paper_f21.SETS / SPS; the curves are read with analysis.load_raw, a
raised block counts as a failure, and the +6..+15 dB points follow FIGHS16e4 §1 through fighs_merge.merge (n = 20480 raw when
one has the arm -- the @1 reading from the base tag's raw_FH<tag>, as in paper_f16deep -- else the original n = 2560 raw at
every SNR; one point = one raw).  A zero-failure point breaks its curve; Perfect CSI gets the fighs_merge.zero_arrows arrow
from the Wilson bound of the point's own n; y from 3e-5 (FIGHS16e4 §1), as F21.  Asserted, else the script stops before saving:
  - every n = 2560 count = the 'BLER@16 failures' table of conf/results/review_next/pairB_ST<tag>.txt (8 arms x 7 SNRs per
    scenario) and, for the sparse three and the six core arms, the panel block of records/paper_f21.txt;
  - every n = 20480 count = its count table (fighs_merge.merge) and, for the nine F21 curves, the 'FIGHS16e4 merge' block of
    records/paper_f21.txt (Pilot-only LMMSE (@1): count table only);
  - same trials: the Perfect CSI error arrays of raw_SP<suffix> and raw_ALD<suffix> = the base raw's;
  - drawn = counted (points read back from the artists); shapes = paper_f16deep's table (checked there against the paper
    figures); every panel holds exactly the curves of the legend; the six axes share x and y; panel labels at the same spot,
    clear of the curves; every artist inside the canvas; every visible text >= 7 pt (nominal).
The record lists, per panel, the points where another drawn curve is at or below the proposed curve and the registered labels of
the drawn baselines (nothing is tested here).
Saved at exactly figsize, PNG at 300 dpi, TrueType fonts.  Output next to this script, or in $FIG_OUTDIR.
Run (CPU, a few minutes):
  cd ~/t2/conf && CUDA_VISIBLE_DEVICES= ~/miniforge3/envs/torch/bin/python -B ~/t2/conference/figures/paper_f21sel.py \\
      > ~/t2/conference/figures/records/paper_f21sel.txt
"""
import collections
import contextlib
import os
import re
import sys
from unittest import mock

sys.dont_write_bytecode = True                                 # no __pycache__ next to the paper_f*.py or in conf/code
import paper_f16deep as D                                      # the legend: CURVES / SHOW, shapes, sizes, the record parsers
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from paper_f16deep import BY, F21, FIG, GE, M, N0, Q, S, SHOW, SNRS, V1

REC21 = os.path.join(D.HERE, "records", "paper_f21.txt")
NAMES = ("Sparse specular, 8x4", "Sparse specular, 16x4", "Sparse specular, CN gains", "Clustered SV", "3GPP UMi 28 GHz", "3GPP mixed")
BASE = [a for a in SHOW if BY[a].orig == "B16e4k"]             # from the scenario's base raw; the others: raw_SP<suffix>, raw_ALD<suffix>
W, H = 7.16, 4.57
LEFT, RIGHT, BOTTOM, BAND, TOP, HGAP, VGAP = 0.50, 0.05, 0.36, 0.58, 0.03, 0.08, 0.10   # in; BAND = the legend band (as F16deep_wide)
YLIM, XLIM = (3e-5, 1.05), (-4, 16)                            # FIGHS16e4 §1 (1/20480 = 4.9e-5 visible), as F21
LAB_XY = (0.04, 0.035)                                         # panel label: axes fraction of its lower-left corner
USER2 = "확정은 11 곡성으로 하는게 좋을 거 같은ㄷ게"            # the user on the number of curves, verbatim (typos included), 2026-10-09 CDT


def count(d, key, arm):
    """failures, trials of an arm at one (cell, prior, SNR), read at its last iteration (R0-pilot@1 has one column); a raised block is a
    failure -- load_raw has already made it one (paper_f16deep.NOTES)"""
    e = np.asarray(d[key][arm]["blk_err"], float)[:, -1]
    assert np.isfinite(e).all(), (key, arm)
    return int(e.sum()), len(e)


def hs_source(orig, arm, cell, prior):
    """the n = 20480 raw of a curve (fighs_merge.hs_tag; the alias R0-pilot@1 follows its arm), or None when no such raw has the arm"""
    tag = M.hs_tag(orig, arm.split("@")[0])
    if not os.path.isdir(os.path.join(M.CONF, f"raw_{tag}")):
        return None
    has = [arm in D.raw(tag).get((cell, prior, s), {}) for s in M.HS]
    assert all(has) or not any(has), (tag, arm, has)
    return tag if all(has) else None


def main():
    D.check_styles()
    plt.rcParams.update(D.RC)
    fig = plt.figure(figsize=(W, H))
    w, h = (W - LEFT - RIGHT - 2 * HGAP) / 3, (H - BOTTOM - BAND - TOP - VGAP) / 2
    axs = []
    for i in range(6):
        r, c = divmod(i, 3)
        axs.append(fig.add_axes([(LEFT + c * (w + HGAP)) / W, (BOTTOM + (1 - r) * (h + VGAP)) / H, w / W, h / H],
                                sharex=axs[0] if axs else None, sharey=axs[0] if axs else None))
    txt, src_all, below_all, zero_all, near_all, lab_all, shadow_all = [], [], [], [], [], [], []
    for ax, show, (title, tag, cell, prior, status, _) in zip(axs, NAMES, F21.SETS):
        sp = F21.SPS[tag][0]
        ald = "ALD" + sp[2:]
        raws = {tag: D.raw(tag), sp: D.raw(sp), ald: D.raw(ald)}
        keys = [(cell, prior, s) for s in SNRS]
        for t, d in raws.items():                                  # same grid; same trials: Perfect CSI error arrays identical
            assert sorted(k for k in d if k[:2] == (cell, prior)) == keys, (t, sorted(d))
            for key in keys:
                assert np.array_equal(raws[tag][key][GE]["blk_err"], d[key][GE]["blk_err"], equal_nan=True), (t, key)
        tab = D.rec_rows(os.path.join(M.RV, f"pairB_ST{tag}.txt"), "BLER@16 failures / n per SNR -3 +0 +3 +6 +9 +12 +15 dB:")
        f21 = D.rec_rows(REC21, title)
        hs_rec = D.rec_fighs(REC21, f"  {title[:3]} raw_{tag} + raw_{sp}, cell {cell}:")
        assert {a for a in SHOW if BY[a].orig != "SPB16e4k"} <= set(tab) and len(hs_rec) == 9 and set(hs_rec) <= set(f21) & set(SHOW), (tag, sorted(tab), sorted(f21), sorted(hs_rec))
        with open(REC21, encoding="utf-8") as f:
            head = next(l for l in f.read().split("\n") if l.startswith(title))
        with open(os.path.join(M.RV, f"pairB_{sp}.txt"), encoding="utf-8") as f:   # the registered table-B labels of the 16 baselines vs V1
            lab = dict(re.findall(r"(\S+)=(\([iv]+\))", next(l for l in f.read().split("\n") if l.startswith("    M-ours-bstar=("))))
        assert len(lab) == 16 and {a for a in SHOW if a not in (V1, GE)} <= set(lab) <= set(BY), (tag, sorted(lab))
        odd = [[f"{BY[a].label} {lab[a]}" for a in lab if lab[a] != "(i)" and (a in SHOW) == drawn] for drawn in (True, False)]
        lab_all.append(f"    {title[:3]} drawn: " + ("all (i)" if not odd[0] else "; ".join(odd[0]) + "; the others (i)")
                       + ";  not drawn: " + ("all (i)" if not odd[1] else "; ".join(odd[1]) + "; the others (i)")
                       + f";  (i) for {sum(v == '(i)' for v in lab.values())} of the 16")
        txt += [f"{title[:3]} {show}  [{head.split(' -- ')[1].split('.  Failures')[0]}; + raw_{ald}]:"]
        cur, src = {}, {}
        for a in SHOW:
            orig = tag if a in BASE else sp if BY[a].orig == "SPB16e4k" else ald
            cnt = [count(raws[orig], key, a) for key in keys]
            k0, n0 = np.array([x[0] for x in cnt]), np.array([x[1] for x in cnt])
            assert set(n0.tolist()) == {N0}, (tag, a, n0)
            checked = 0
            for name, t in (("pairB_ST", tab), ("paper_f21.txt", f21)):
                if a in t:
                    assert k0.tolist() == t[a], (tag, name, a, k0.tolist(), t[a])
                    checked += 1
            assert checked == 1 + (a in hs_rec and a in tab), (tag, a, checked)   # the six core arms: both files; the sparse three: paper_f21.txt; ALD-pilot, R0-pilot@1: pairB_ST
            hs = hs_source(orig, a, cell, prior)
            if hs:                                                 # fighs_merge.merge: asserts n = 20480 and raw = count table
                with mock.patch.object(M, "hs_tag", lambda o, x, t=hs: t) if M.hs_tag(orig, a) != hs else contextlib.nullcontext():
                    k, n, line = M.merge(SNRS, k0, n0, orig, cell, prior, a)   # (the alias R0-pilot@1 is mapped to its arm's raw)
                assert line.rstrip().endswith(f"(raw_{hs})" + (f"   rising: {'; '.join(D.rising(k, n))}" if D.rising(k, n) else "")), line
                assert (a in hs_rec) == (a != "R0-pilot@1") and (a not in hs_rec or (k[3:].tolist(), n[3:].tolist(), hs) == hs_rec[a]), (tag, a, k, hs)
            else:
                k, n = k0.copy(), n0.copy()
            assert np.array_equal(k[:3], k0[:3]) and set(n[3:].tolist()) == ({M.N_HS} if hs else {N0}), (tag, a)
            cur[a], src[a] = (k, n), hs
            ok = k > 0
            p = np.where(ok, k / n, np.nan)                        # a zero-failure point breaks the curve
            c = BY[a]
            ax.plot(SNRS, p, color=c.color, marker=c.marker, ls=c.ls, mfc=c.color if c.filled else "white", label=c.label,
                    zorder={V1: 5, D.BS: 4, GE: 3}.get(a, 2.9 - 0.05 * SHOW.index(a)), **D.size(c))
            if a == GE:
                M.zero_arrows(ax, np.array(SNRS)[~ok], n[~ok], c.color)
            d = Q.curves(ax)[c.label]
            assert Q.same(d["x"], SNRS) and Q.same(d["y"], p), (tag, a)
            zero_all += [f"{title[:3]} {c.label} {s:+.0f} dB (0/{m})" for s, x, m in zip(SNRS, k, n) if x == 0]
            txt.append(f"    {a:<21}" + " ".join(f"{x}/{m}" for x, m in zip(k, n)) + f"   -3..+3 dB raw_{orig}, +6..+15 dB "
                       + (f"raw_{hs}" if hs else f"raw_{orig} (n = 2560 at every SNR)")
                       + (f"   rising: {'; '.join(D.rising(k, n))}" if D.rising(k, n) else ""))
        assert sorted(Q.curves(ax)) == sorted(BY[a].label for a in SHOW), tag    # the panel holds exactly the curves of the legend
        src_all.append({a: bool(t) for a, t in src.items()})
        vk, vn = cur[V1]
        below = [f"{BY[a].label} at " + ", ".join(f"{s:+.0f} dB ({x}/{m} vs {y}/{z})" for s, x, m, y, z in zip(SNRS, *cur[a], vk, vn) if x * z <= y * m)
                 for a in SHOW if a not in (V1, GE) and (cur[a][0] * vn <= vk * cur[a][1]).any()]
        above = [f"{s:+.0f} dB ({y}/{z} vs Perfect CSI {x}/{m})" for s, x, m, y, z in zip(SNRS, *cur[GE], vk, vn) if y * m <= x * z]
        below_all.append(f"    {title[:3]} " + ("; ".join(below) or "none") + ("" if not above else ";  proposed at or below Perfect CSI at " + ", ".join(above)))
    assert all(s == src_all[0] for s in src_all), src_all          # the same curves take n = 20480 points in every panel
    for i, ax in enumerate(axs):
        ax.set_yscale("log"); ax.set_ylim(*YLIM); ax.set_xticks(SNRS); ax.set_xlim(*XLIM)
        ax.tick_params(axis="x", pad=Q.XTPAD, labelbottom=i >= 3); ax.tick_params(axis="y", labelleft=i % 3 == 0)
        if i >= 3:
            ax.set_xlabel("SNR [dB]", labelpad=Q.XPAD)
        if i % 3 == 0:
            ax.set_ylabel("BLER")
    assert all(axs[0].get_shared_x_axes().joined(axs[0], a) and axs[0].get_shared_y_axes().joined(axs[0], a) for a in axs)   # the six axes share x and y
    pl = [ax.text(*LAB_XY, f"({t})", transform=ax.transAxes, ha="left", va="bottom", fontsize=D.LAB_PT, fontweight="bold", color=S.INK,
                  zorder=7) for ax, t in zip(axs, "abcdef")]
    hl = [D.proxy(BY[a]) for a in SHOW]
    hl.insert(D.LEG_GAP, Line2D([], [], ls="none", label=""))      # the legend of F16deep_wide: three columns = the families
    leg = fig.legend(hl, [x.get_label() for x in hl], loc="center", ncol=3, frameon=False, fontsize=7,
                     bbox_to_anchor=(0.5, (H - BAND / 2) / H), handlelength=2.3, columnspacing=2.2, labelspacing=0.28,
                     borderpad=0.1, handletextpad=0.5)

    # ---------------- geometry and overlap checks ----------------
    bb, small = Q.check(fig, "F21sel_wide")                       # every artist inside the canvas; every visible text >= 7 pt
    px = 72 / fig.dpi
    pos = [np.array(a.get_position().extents) * [W, H, W, H] for a in axs]
    assert all(np.allclose(q[2:] - q[:2], [w, h], rtol=0, atol=1e-9) for q in pos), pos
    lb = Q.inch(fig, leg.get_window_extent())
    assert lb[1] >= H - BAND and lb[3] <= H and lb[0] >= 0 and lb[2] <= W, ("legend outside its band", lb)
    lt = [t for t in leg.get_texts() if t.get_text()]
    cols = collections.defaultdict(set)
    for t, a in zip(lt, SHOW):
        cols[round(t.get_window_extent().x0)].add(BY[a].family)
    assert len(lt) == len(SHOW) and [cols[x] for x in sorted(cols)] == [{"diffusion", "GMM"}, {"Gaussian"}, {"sparse", "Perfect CSI"}], cols
    clear = {}
    for ax, t in zip(axs, pl):                                     # panel label: same spot, nothing drawn within 1.5 pt of it
        e = t.get_window_extent()
        assert np.allclose(ax.transAxes.inverted().transform((e.x0, e.y0)), LAB_XY, rtol=0, atol=1e-6), t.get_text()
        assert not D.hits(ax, e, 1.5 / px), (t.get_text(), D.hits(ax, e, 1.5 / px))
        clear[t.get_text()] = min(d for d in np.arange(1.5, 40.5, 0.5) if D.hits(ax, e, (d + 0.5) / px) or d == 40)
        near = D.coincide(ax, D.NEAR_PT)
        near_all.append(f"    {t.get_text()} " + ("; ".join(f"{a} / {b} at " + ", ".join(f"{x:+.0f}" for x in at) + " dB" for a, b, at in near) or "none"))
        hit = collections.defaultdict(set)                         # label -> the SNRs where another curve's marker is that close
        for a, b, at in near:
            hit[a] |= set(at); hit[b] |= set(at)
        full = [l for l, c in Q.curves(ax).items() if set(np.asarray(c["x"])[np.isfinite(c["y"])]) <= hit[l]]
        shadow_all.append(f"    {t.get_text()} " + ("; ".join(full) or "none"))
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(FIG, f"F21sel_wide.{ext}"), dpi=300, **({"metadata": {"CreationDate": None}} if ext == "pdf" else {}))

    # ---------------- record ----------------
    hs_show, n_show = [a for a in SHOW if src_all[0][a]], [a for a in SHOW if not src_all[0][a]]
    fmt = lambda arms: "; ".join(BY[a].label for a in arms)
    head = ["F21sel -- the six static scenarios of F21 with the one legend of F16deep_wide: equal budget N_train = 1.6e5, BLER@16 (Pilot-only "
            "LMMSE: after the first iteration), failures / trials per SNR -3 +0 +3 +6 +9 +12 +15 dB.  Recomputed from raw by "
            "conference/figures/paper_f21sel.py (read-only; analysis.load_raw, a raised block = a failure); no number transcribed.", "",
            f"F21sel_wide  {W} x {H} in ({W * 72:.2f} x {H * 72:.2f} pt), six panels, one legend; every panel draws the {len(SHOW)} curves of that legend "
            "(paper_f16deep.SHOW, with its shapes and sizes; no error bars, as F21).",
            "User, 2026-10-09 CDT (verbatim; paper_f16deep.USER): \"" + D.USER[0] + "\"; \"" + D.USER[1] + "\".  In the same session the user then chose this figure -- the "
            "recorder's option 'six scenarios x the same 11 curves' -- and wrote on the number of curves (verbatim): \"" + USER2 + "\".", "",
            "Curves (internal arm -> figure name): " + "; ".join(f"{a} -> {BY[a].label}" for a in SHOW) + ".", "",
            "Panels (the line in brackets is the panel line of records/paper_f21.txt) and counts, with the source raw of each point (one point = "
            "one raw, never pooled; FIGHS16e4 §1 through fighs_merge.merge; 'rising' = a cell where BLER rises with SNR, one-sided Fisher p, reported only):"]
    tail = ["", f"+6..+15 dB from n = 20480 new trials (trials 10000..30479) in every panel, {len(hs_show)} curves: " + fmt(hs_show) + ".",
            f"n = 2560 (the original test trials 0..2559) at EVERY SNR in every panel -- no n = 20480 raw has the arm -- {len(n_show)} curve(s), to be "
            "named in the caption: " + fmt(n_show) + ".",
            "Pilot-only LMMSE = R0-pilot read after the FIRST iteration (alias 'R0-pilot@1'); its n = 20480 points come from the base tag's "
            "raw_FH<tag> / raw_FHNR16B16e4 / raw_FHB16e4k (the alias rows of their count tables; NEXT_EXPERIMENTS_FIGHS16e4 §1 calls them reference rows "
            "its own figures do not use -- the same extension as in F16deep_wide, see records/paper_f16deep.txt).  F21 does not draw this curve; F22 "
            "draws the same receiver after 16 iterations.",
            "Annealed Langevin = the plug-in use (ALD-pilot); the error-aware variant is not drawn (as in F16deep_wide).",
            "Zero-failure points (the curve breaks there; Perfect CSI: a downward arrow from the 95% Wilson bound of the point's own n): "
            + ("; ".join(zero_all) or "none") + ".",
            "Raised blocks (analysis.load_raw NOTE lines; a raised block is kept and counted as a failure) in the raws read: " + ("; ".join(D.NOTES) or "none") + ".",
            "", "Drawn curves at or below the proposed curve (point estimates, exact in integers; failures/trials vs the proposed curve's) -- "
            "reported only, nothing is tested here; the registered paired tests are in conf/results/review_next/pairB_ST<tag>.txt and pairB_SP<suffix>.txt:"]
    tail += below_all
    tail += ["", f"Registered table-B labels against the proposed prior (conf/results/review_next/pairB_SP<suffix>.txt; (i) = the proposed prior fails less, "
             f"(iii) / (iv) = not decided) of the {len(SHOW) - 2} drawn baselines (every drawn curve but the proposed one and Perfect CSI, a reference without "
             "a label) and of the 7 registered baselines that are not drawn, per panel:"] + lab_all
    tail += ["", f"Markers of two curves with centres closer than {D.NEAR_PT} pt at the same SNR (one hides or touches the other):"] + near_all
    tail += ["", "Curves with such a neighbour at EVERY drawn point (their markers are nowhere free; they read by line colour and style):"] + shadow_all
    tail += ["", "Asserts passed (the script stops before saving otherwise):",
             "  n = 2560 counts = conf/results/review_next/pairB_ST<tag>.txt 'BLER@16 failures' tables (8 arms x 7 SNRs per scenario) and the panel "
             "blocks of records/paper_f21.txt (the sparse three and the six core arms); each drawn count is checked against one of the two, the six core arms against both.",
             "  n = 20480 counts = their count tables (fighs_merge.merge) and the 'FIGHS16e4 merge' blocks of records/paper_f21.txt (nine curves "
             "per panel); Pilot-only LMMSE (@1): count table only.",
             "  same trials: Perfect CSI error arrays of raw_SP<suffix> and raw_ALD<suffix> = the base raw's at the seven SNRs, in every scenario.",
             "  drawn = counted (points read back from the artists; rtol 1e-12); every panel holds exactly the curves of the legend; shapes = "
             "paper_f16deep's table (its check against the paper figures run here too).",
             "", "Layout: 2 x 3 axes, each " + f"{w:.4f} x {h:.4f} in (asserted), shared x and y; x ticks {' '.join(f'{s:+.0f}' for s in SNRS)} dB, x range {XLIM}, "
             f"y log {YLIM} (FIGHS16e4 §1, as F21); legend band {BAND} in above the axes = the legend of F16deep_wide ({len(SHOW)} entries, 4 rows x 3 "
             f"columns = the families; inside its band: asserted, [in] {np.round(lb, 3).tolist()}).",
             f"  panel labels (a)-(f): bold {D.LAB_PT} pt, lower-left corner at axes fraction {LAB_XY} in every panel (asserted); nearest drawn data "
             "(curve centre line, marker box) is farther than [pt]: " + ", ".join(f"{t} {d:g}" for t, d in clear.items()) + ".",
             f"  checks: every artist inside the canvas (tight bbox [in] {np.round(bb, 3).tolist()}); smallest visible text {small:g} pt (nominal size; "
             "the exponents of the 10^x tick labels are smaller, about 5.6 pt); STIXGeneral / mathtext stix, TrueType in the PDF; saved at figsize, "
             "PNG 300 dpi."]
    print("\n".join(head + txt + tail))


if __name__ == "__main__":
    main()
