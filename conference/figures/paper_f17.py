"""conference/figures/paper_f17.py -- paper version of conf/code/figure_f17.py (git 3f7c09ab), F17: BLER vs SNR for the
8x4 and 16x4 arrays (sparse specular channel) and the fraction of the GMM-to-perfect-CSI gap closed vs training set size.

Same data, computation, asserts, colours, markers and line styles as the original; only the rendered text differs, and
two internal-process artefacts are no longer drawn:
  - legend labels and in-panel text use the paper glossary (conference/figures/TERMS.md) instead of project-internal
    names; y labels "BLER" and "Fraction of the GMM-to-perfect-CSI gap closed", x label "Training set size N_train";
  - panel titles removed (cell names / gate status go to the caption), only the bold panel labels remain:
    (a) Sparse specular, 8x4   (b) Sparse specular, 16x4   (c) gap fraction at -3 dB vs N_train, both arrays;
  - (c): the best-validation (hollow) points and their legend entry, the registered R = 0.70 band line and its label,
    the gate shading and its PASS/FAIL labels and the "registered band value" note are not drawn (their values are
    still computed and asserted; the last-EMA lines are unchanged);
  - one-row legend (was two columns) so the taller (c) axis takes the two-line y label;
  - FIGHS16e4 merge (NEXT_EXPERIMENTS_FIGHS16e4 §1, report-only; fighs_merge.py): the (a)(b) curves keep raw_B16e4k /
    raw_NR16B16e4 (n = 2560) at -3..+3 dB and take +6..+15 dB from n = 20480 new trials (HISNR raw_HSB16e4k / raw_HSNR16);
    Wilson bars and zero-failure labels with each point's own n; zero points break the curve; merged k/n printed after the
    unchanged record ((c) unchanged);
  - reads the raw files and checkpoints from conf/ (read-only) and writes only F17_codim_C6.{pdf,png} next to this
    script (or to $FIG_OUTDIR) (no .txt; the record text is printed to stdout and keeps the internal names).
The original docstring follows.

conf/code/figure_f17.py -- F17: the co-dimension (여차원) figure, cell C6 (Nr=16) next to the headline cell C2 (Nr=8).
Report figure; every number straight from the raw files (read-only).

(a) C2 | (b) C6, sharing y: BLER@16 vs SNR at the equal budget N_train = 1.6e5: GMM b*, the learned diffusion prior V1
    and the known-channel reference R5-genie (per-arm dodge -0.45 / 0 / +0.45 dB, genie drawn above V1).  C2 = raw_B16e4k (headline, D1-sibling
    gate PASS), C6 = raw_NR16B16e4 (registered measurement tag, _best weights of §3d ladder step 2; UNGATED).  95% Wilson
    intervals; a zero-failure point is a short downward arrow from the upper end of its Wilson interval, never a made-up value.
(c) genie-gap recovery R = (b* - V1)/(b* - genie) at -3 dB vs the equal budget N_train, with the 90% PAIRED bootstrap CI of
    code/recovery_ci.py (boot([(b, v, g)], 2000, 20260926) per point; asserted against the committed recovery_*.txt for
    the four tags that have one (B16e4k, NR16run2, NR16B16e4, NR16B16e4last); the C2 1e4 / 4e4 / 3.2e5 CIs (and the 4e4 R) are
    computed here only; the 1e4 / 3.2e5 point R agree with NEXT_EXPERIMENTS_C6B16e4.md:19 and NEXT_EXPERIMENTS_B32e4.md:105-108,
    :124 and are asserted against them (REC_R)).  Lines = last-EMA weights for both cells (budget-comparison rule: C2
    NEXT_EXPERIMENTS_B32e4.md:28, :34; C6 NEXT_EXPERIMENTS_C6B16e4.md:30); hollow = _best weights (B32e4, NR16B16e4).
    Colours / markers: the shared role palette of code/figstyle.py (V1 blue, b* orange, genie ink, cells C2 / C6).
    Each point's V1 checkpoint grad_clip is read from the raw meta stagec_ckpt and asserted (clip 1.0 = C6 1.6e5 only).
Writes figs/F17_codim_C6.{pdf,png,txt}.
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
import matplotlib.ticker
import torch
from matplotlib.lines import Line2D
from analysis import load_raw, sign_p, wilson
from recovery_ci import fails, boot, rec
from figstyle import INK, V1, GMM, GENIE, CELL_C2, CELL_C6
import fighs_merge as M                              # conference/figures/fighs_merge.py (FIGHS16e4 merge)

plt.rcParams.update({"font.size": 8, "axes.labelsize": 8.5, "axes.titlesize": 8.5, "legend.fontsize": 8,
                     "xtick.labelsize": 8, "ytick.labelsize": 8, "axes.grid": True, "grid.alpha": 0.25,
                     "figure.dpi": 200, "savefig.bbox": "tight", "savefig.pad_inches": 0.02,
                     "text.color": INK, "axes.labelcolor": INK, "axes.titlecolor": INK,   # text is always ink (figstyle)
                     "xtick.labelcolor": INK, "ytick.labelcolor": INK})
FIG = M.FIG                                          # paper version: figures only, next to this script ($FIG_OUTDIR)
B, SEED, DEC = 2000, 20260926, (-3.0, 0.0, 3.0)
# (arm, legend label, colour, marker, line style [figstyle roles], SNR dodge [dB], zorder: genie drawn above V1 so its star stays visible)
ARMS = [("M-ours-bstar", "GMM prior", GMM["color"], GMM["marker"], GMM["ls"], -0.45, 3),
        ("M-ours-dscore-C-V1", "Proposed (diffusion prior)", V1["color"], V1["marker"], V1["ls"], 0.0, 4),
        ("R5-genie", "Perfect CSI", GENIE["color"], GENIE["marker"], GENIE["ls"], 0.45, 5)]
# (cell, N_train, raw tag, weights, role / gate status, on the series line?)  Series lines = last-EMA weights for both
# cells (budget-comparison rule: C2 NEXT_EXPERIMENTS_B32e4.md:28, :34; C6 NEXT_EXPERIMENTS_C6B16e4.md:30); the _best
# points are the hollow markers.
POINTS = [("C2", 1e4, "B1e4", "last-EMA", "D1-sibling gate FAIL recipe (budget-axis measurement)", True),
          ("C2", 4e4, "B4e4k", "last-EMA", "D1-sibling gate FAIL recipe (budget-axis measurement)", True),
          ("C2", 1.6e5, "B16e4k", "last-EMA (legacy d2sx_N160000_a1.pt; headline)", "D1-sibling gate PASS", True),
          ("C2", 3.2e5, "B32e4last", "last-EMA (budget-curve row; report only)", "D1-sibling gate PASS", True),
          ("C2", 3.2e5, "B32e4", "_best.pt (judging run)", "D1-sibling gate PASS", False),
          ("C6", 1e4, "NR16run2", "last-EMA (best weights not saved)", "UNGATED", True),
          ("C6", 1.6e5, "NR16B16e4", "_best (registered measurement tag; §3d ladder step 2)", "UNGATED", False),
          ("C6", 1.6e5, "NR16B16e4last", "last-EMA (§3d ladder step 2; budget-curve row; report only)", "UNGATED", True)]
HOLLOW_X = 1.22             # (c): every _best (hollow) point is drawn at N_train x 1.22; every other point at N_train exactly
# committed recovery_*.txt (results/review_next/): (-3 dB R, lo, hi), (pooled -3/0/+3 R, lo, hi)
EXPECT = {"B16e4k": ((0.470, 0.427, 0.512), (0.509, 0.470, 0.545)),
          "NR16run2": ((0.838, 0.781, 0.892), (0.858, 0.817, 0.899)),
          "NR16B16e4": ((0.809, 0.747, 0.870), (0.823, 0.771, 0.871)),
          "NR16B16e4last": ((0.815, 0.756, 0.872), (0.806, 0.757, 0.854))}
# table B b* -> V1 pooled a:b over the decision points (tables_D2_<tag>.txt, "sign test @16" line)
# committed record point R (not in a recovery_*.txt): tag -> (-3 dB R, pooled -3/0/+3 R or None)
# NEXT_EXPERIMENTS_C6B16e4.md:19 (B1e4 0.490); NEXT_EXPERIMENTS_B32e4.md:105, :108 (B32e4 0.453, pooled 0.495), :124 (B32e4last 0.463)
REC_R = {"B1e4": (0.490, None), "B32e4": (0.453, 0.495), "B32e4last": (0.463, None)}
EXPECT_AB = {"B1e4": (502, 72), "B4e4k": (459, 79), "B16e4k": (454, 78), "B32e4last": (418, 71), "B32e4": (421, 69),
             "NR16run2": (266, 13), "NR16B16e4": (213, 18), "NR16B16e4last": (208, 17)}


def raw(tag):
    d, meta, warns = load_raw("D2", root=os.path.join(CONF, f"raw_{tag}"))
    assert not warns, warns
    return d, meta


def decision_snrs(d, cell):
    """08_SPEC §2: anchor b* BLER@16 in [0.005, 0.9], the 3 SNRs with the smallest |log10(BLER/0.1)|."""
    snrs = sorted(k[2] for k in d if k[0] == cell)
    p = {s: fails(d, cell, s, "M-ours-bstar").mean() for s in snrs}
    return tuple(sorted(sorted((s for s in snrs if 0.005 <= p[s] <= 0.9), key=lambda s: abs(np.log10(p[s] / 0.1)))[:3]))


def table_b(d, cell):
    out = []
    for s in DEC:
        b, v = fails(d, cell, s, "M-ours-bstar"), fails(d, cell, s, "M-ours-dscore-C-V1")
        a_, b_ = int(((b == 1) & (v == 0)).sum()), int(((b == 0) & (v == 1)).sum())
        out.append((s, a_, b_, sign_p(a_, b_)))
    return out


def main():
    fig = plt.figure(figsize=(7.16, 3.05), layout="constrained")
    gs = fig.add_gridspec(1, 3, width_ratios=[1, 1, 1.12])
    a1 = fig.add_subplot(gs[0]); a2 = fig.add_subplot(gs[1], sharey=a1); a3 = fig.add_subplot(gs[2])
    txt = ["F17 -- co-dimension axis: cell C6 (Nr=16, UNGATED) next to the headline cell C2 (Nr=8).  Numbers recomputed "
           "from the raw files by code/figure_f17.py (read-only).", ""]

    # ---------------- (a) C2 | (b) C6: BLER@16 vs SNR at N_train = 1.6e5 ----------------
    txt.append("(a) C2 and (b) C6: BLER@16 vs SNR at the equal budget N_train = 1.6e5 (GMM EM fit and diffusion-prior "
               "training on the SAME channel set), test trials 0..2559 (n=2560 per SNR), 95% Wilson intervals:")
    cells = [(a1, "C2", "B16e4k", "C2 (8x4, T=16, Tp=4), raw_B16e4k (headline; D1-sibling gate PASS)",
              "(a) C2 ($N_r$=8): headline cell,\nD1-sibling gate PASS"),
             (a2, "C6", "NR16B16e4", "C6 (16x4, T=16, Tp=4), raw_NR16B16e4 (_best, registered measurement tag; UNGATED, "
              "geometry-axis measurement, not an arm verdict)", "(b) C6 ($N_r$=16): UNGATED,\nmeasurement, not an arm verdict")]
    zeros, fh = [], []                                         # fh: FIGHS16e4 merge record (printed after the record)
    for ax, cell, tag, desc, title in cells:
        d, meta = raw(tag)
        m = meta[(cell, "S2")]
        snrs = sorted(k[2] for k in d if k[0] == cell)
        txt.append(f"  {desc}; b* = {m['bstar']} K={m['kron_K']} ll_val {m['ll_val|kron']!r}"
                   + (f"; V1 ckpt {m['stagec_ckpt_id']}" if "stagec_ckpt_id" in m else "; V1 ckpt legacy last-EMA "
                      "d2sx_N160000_a1.pt (results/review_next/NEXT_EXPERIMENTS.md:13)"))
        cnt, cm = {}, {}
        fh.append(f"  {title[:3]} {cell}:")
        for arm, lab, col, mk, ls, dx, z in ARMS:
            f = [fails(d, cell, s, arm) for s in snrs]
            k = np.array([x.sum() for x in f]); n = np.array([len(x) for x in f])
            assert (n == 2560).all()
            zeros += [f"{cell} {arm} {s:+.0f} dB 0/2560 (95% Wilson [0, {wilson(0, 2560)[1]:.2e}])" for s, a in zip(snrs, k) if a == 0]
            txt.append(f"    {arm:<20} " + " ".join(f"{int(a)}/{int(b)}" for a, b in zip(k, n)) + "   (SNR " +
                       " ".join(f"{s:+.0f}" for s in snrs) + " dB)")
            cnt[arm] = k
            k, n, line = M.merge(snrs, k, n, tag, cell, "S2", arm); fh.append(line); cm[arm] = k   # +6..+15 dB: n = 20480 raw
            ok = k > 0
            ci = np.array([wilson(int(a), int(b)) for a, b in zip(k, n)])
            p = k / n
            x = np.array(snrs) + dx                            # per-arm dodge (ARMS): b* -0.45, V1 0, genie +0.45 dB
            ax.errorbar(x, np.where(ok, p, np.nan), yerr=[np.where(ok, p - ci[:, 0], np.nan), np.where(ok, ci[:, 1] - p, np.nan)],
                        color=col, marker=mk, ls=ls, lw=1.1, ms=(4 if mk != "*" else 6.5), capsize=1.5, elinewidth=0.9, zorder=z)
            for s, hi, nz in zip(x[~ok], ci[~ok, 1], n[~ok]):  # zero failures: arrow down from the Wilson upper end (own n)
                ax.plot([s - 0.1, s + 0.1], [hi, hi], color=col, lw=1.0, zorder=6)
                ax.annotate("", xy=(s, hi / 1.45), xytext=(s, hi), zorder=6,   # ends above the V1 marker next to it
                            arrowprops=dict(arrowstyle="-|>", color=col, lw=0.9, mutation_scale=6.5, shrinkA=0, shrinkB=0))
                ax.text(s + 0.3, hi * 1.08, f"0/{nz}", rotation=90, ha="left", va="top", fontsize=8, color=INK)
        assert (cnt["M-ours-dscore-C-V1"] < cnt["M-ours-bstar"]).all(), cell    # caption: V1 fewer at all 7 SNRs
        assert (cm["M-ours-dscore-C-V1"] < cm["M-ours-bstar"]).all(), cell      # ... also at the drawn (merged) points
        b3, v3, g3 = (int(cnt[a][snrs.index(-3.0)]) for a in ("M-ours-bstar", "M-ours-dscore-C-V1", "R5-genie"))
        ax.text(0.97, 0.965, f"Block errors at −3 dB:\nGMM prior {b3}/2560\nProposed {v3}/2560\nPerfect CSI {g3}/2560", transform=ax.transAxes,
                ha="right", va="top", fontsize=8, bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="0.75", lw=0.6))
        ax.text(0.03, 0.03, "$N_{\\rm train}=1.6\\times10^5$", transform=ax.transAxes, ha="left",
                va="bottom", fontsize=8)
        ax.set_title(title[:3], loc="left", fontweight="bold", fontsize=8.5)   # paper: panel label only
        ax.set_xlim(-3.9, 16.9); ax.set_xticks(range(-3, 16, 3)); ax.set_xlabel("SNR [dB]")
    txt.append("  zero-failure points (drawn as a short downward arrow from the upper end of the 95% Wilson interval, in "
               f"the genie slot {ARMS[2][5]:+.2f} dB, labelled 0/2560, not connected to the curve): "
               + ("; ".join(zeros) if zeros else "none"))
    a1.set_yscale("log"); a1.set_ylim(4e-5, 1.0); a1.set_ylabel("BLER")
    a2.tick_params(labelleft=False)

    # ---------------- (c) recovery at -3 dB vs budget ----------------
    txt += ["", "(c) genie-gap recovery R = (b* - V1)/(b* - genie) from failure counts @16, 90% PAIRED bootstrap CI "
            f"(trial indices resampled with the three arms together, B={B}, default_rng({SEED}), percentiles 5/95; "
            "code/recovery_ci.py fails/boot/rec).  Per point: -3 dB counts, -3 dB R, pooled -3/0/+3 dB R (the decision "
            "SNRs; recomputed by the 08_SPEC §2 anchor rule for every tag), table B b*->V1 a:b:"]
    res, gref, ckid, v3n, clip = {}, {}, {}, {}, {}
    for cell, N, tag, wts, gate, series in POINTS:
        d, meta = raw(tag)
        m = meta[(cell, "S2")]
        gv = np.concatenate([fails(d, cell, s, "R5-genie") for s in sorted(k[2] for k in d if k[0] == cell)])
        assert np.array_equal(gref.setdefault(cell, gv), gv), tag             # caption: genie identical across tags
        assert m["ntrain"] == N, (tag, m["ntrain"])
        assert decision_snrs(d, cell) == DEC, (tag, decision_snrs(d, cell))
        cols = [tuple(fails(d, cell, s, arm) for arm in ("M-ours-bstar", "M-ours-dscore-C-V1", "R5-genie")) for s in DEC]
        b, v, g = cols[0]
        r3 = rec(b, v, g); (lo3, hi3), nn3 = boot([(b, v, g)], B, SEED)
        (lop, hip), nnp = boot(cols, B, SEED)
        Bs, Vs, Gs = (sum(c[i].sum() for c in cols) for i in range(3))
        rp = (Bs - Vs) / (Bs - Gs)
        assert nn3 == 0 and nnp == 0
        if tag in EXPECT:
            (e3, el3, eh3), (ep, elp, ehp) = EXPECT[tag]
            assert (round(r3, 3), round(lo3, 3), round(hi3, 3)) == (e3, el3, eh3), (tag, r3, lo3, hi3)
            assert (round(rp, 3), round(lop, 3), round(hip, 3)) == (ep, elp, ehp), (tag, rp, lop, hip)
        if tag in REC_R:
            e3, ep = REC_R[tag]
            assert round(r3, 3) == e3 and (ep is None or round(rp, 3) == ep), (tag, r3, rp)
        tb = table_b(d, cell)
        A_, B_ = sum(t[1] for t in tb), sum(t[2] for t in tb)
        assert (A_, B_) == EXPECT_AB[tag], (tag, A_, B_)
        res[tag] = (r3, lo3, hi3)
        v3n[tag] = int(v.sum())
        ckid[tag] = m.get("stagec_ckpt_id", "not in raw meta (legacy run)").split(" | ")[0]
        clip[tag] = torch.load(m["stagec_ckpt"], map_location="cpu", weights_only=False).get("grad_clip")  # None = no field
        txt.append(f"  {cell} N={N:.1e} raw_{tag:<14} b*=kron {m['kron_K']:<5} V1 weights {wts}; {gate}; "
                   f"V1 ckpt {ckid[tag]}; grad_clip {'no field' if clip[tag] is None else clip[tag]}")
        txt.append(f"      -3 dB failures b* {int(b.sum())} / V1 {int(v.sum())} / genie {int(g.sum())} (n={len(b)});  "
                   f"R(-3 dB) = {r3:.3f} [90% {lo3:.3f}, {hi3:.3f}];  pooled -3/0/+3 dB b* {int(Bs)} V1 {int(Vs)} genie "
                   f"{int(Gs)} R = {rp:.3f} [90% {lop:.3f}, {hip:.3f}]")
        txt.append("      table B b*->V1 @16: " + "  ".join(f"{s:+.0f} dB {x}:{y} p={p:.2g}" for s, x, y, p in tb)
                   + f"   pooled {A_}:{B_} p={sign_p(A_, B_):.2g}")
    CSTY = {"C2": (CELL_C2["color"], "o", CELL_C2["ls"]), "C6": (CELL_C6["color"], "D", CELL_C6["ls"])}
    hC = {}
    for cell, (col, mk, ls) in CSTY.items():
        for series in (True,):                         # paper: last-EMA lines only (hollow _best points not drawn)
            pts = [p for p in POINTS if p[0] == cell and p[5] == series]
            xs = np.array([p[1] for p in pts]) * (1.0 if series else HOLLOW_X)
            r = np.array([res[p[2]] for p in pts])
            hC[cell, series] = a3.errorbar(xs, r[:, 0], yerr=[r[:, 0] - r[:, 1], r[:, 2] - r[:, 0]], color=col, marker=mk,
                                           ls=ls if series else "none", lw=1.1, ms=4.5, capsize=1.5, elinewidth=0.9,
                                           mfc=col if series else "white", mew=1.0, zorder=3)
    a3.text(0.03, 0.03, "SNR = −3 dB", transform=a3.transAxes, ha="left", va="bottom", fontsize=8)
    a3.annotate(f"{res['NR16run2'][0]:.3f}", (1e4, res["NR16run2"][0]), textcoords="offset points", xytext=(5, 4),
                ha="left", va="bottom", fontsize=8, color=INK)
    a3.annotate(f"{res['B16e4k'][0]:.3f}", (1.6e5, res["B16e4k"][0]), textcoords="offset points", xytext=(-5, 4),
                ha="right", va="bottom", fontsize=8, color=INK)
    a3.set_xscale("log"); a3.set_xlim(7e3, 4.8e5); a3.set_ylim(0.25, 1.06)
    a3.set_xticks([1e4, 4e4, 1.6e5, 3.2e5], ["1", "4", "16", "32"])
    a3.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
    a3.set_xlabel(r"Training set size $N_{\rm train}$ [$10^4$ channels]")
    a3.set_ylabel("Fraction of the GMM-to-\nperfect-CSI gap closed")
    a3.set_title("(c)", loc="left", fontweight="bold", fontsize=8.5)

    hA = [Line2D([], [], color=c, marker=mk, ls=ls, lw=1.1, ms=(4 if mk != "*" else 6.5), label=l)
          for _, l, c, mk, ls, _, _ in ARMS]
    hB = [(hC["C2", True], "(c) 8×4"), (hC["C6", True], "(c) 16×4")]
    fig.legend(hA + [h for h, _ in hB], [h.get_label() for h in hA] + [l for _, l in hB], loc="outside lower center",
               ncol=5, frameon=False, columnspacing=1.5)
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(FIG, f"F17_codim_C6.{ext}"))

    tb6 = table_b(raw("NR16B16e4")[0], "C6")
    gline = next(i for i, l in enumerate(open(os.path.abspath(__file__)), 1) if "np.array_equal(gref" in l)
    cb, cl = ckid["NR16B16e4"].split(), ckid["NR16B16e4last"].split()     # "sha256[:16]=<id> epoch=<e> ..."
    # record NEXT_EXPERIMENTS_C6B16e4.md:82 (best c050d611b2c714a6 @1684, last bf688d605691c7f7 @1704)
    assert cb[:2] == ["sha256[:16]=c050d611b2c714a6", "epoch=1684"] and cl[:2] == ["sha256[:16]=bf688d605691c7f7",
                                                                                   "epoch=1704"], (cb, cl)
    sha_b, ep_b, sha_l, ep_l = cb[0].split("=")[1], cb[1].split("=")[1], cl[0].split("=")[1], cl[1].split("=")[1]
    lr = res["NR16B16e4last"][0]
    # caption "Training and weights": only the C6 1.6e5 checkpoints (§3d ladder step 2) are clipped; the rest 0.0 or no field
    assert {t for t, c in clip.items() if c} == {"NR16B16e4", "NR16B16e4last"}, clip
    assert clip["NR16B16e4"] == clip["NR16B16e4last"] == 1.0 and clip["NR16run2"] == 0.0, clip
    assert all(clip[t] is None for t in ("B1e4", "B4e4k", "B16e4k")) and clip["B32e4last"] == clip["B32e4"] == 0.0, clip
    txt += ["", "Caption notes (paper order: where, how much, why, then scope and limits).",
            "WHERE: at the equal budget N_train = 1.6e5 the learned diffusion prior V1 has fewer failures than GMM b* at all 7 "
            "grid SNRs in both cells -- C2 (panel a; the headline cell, D1-sibling gate PASS) and C6 (panel b; UNGATED, so "
            "a geometry/budget-axis measurement, not an arm verdict); sign tests only at the 3 decision SNRs -3/0/+3 dB.  "
            "C6 registered measurement (NEXT_EXPERIMENTS_C6B16e4.md §1-§2, tag NR16B16e4 = _best): table B M-ours-bstar -> "
            "M-ours-dscore-C-V1 "
            + ", ".join(f"{s:+.0f} dB {x}:{y} (p={p:.2g})" for s, x, y, p in tb6)
            + f", pooled {sum(t[1] for t in tb6)}:{sum(t[2] for t in tb6)}; power guard -> POWERED; second arm fewer failures "
            "at 3/3 points (tables_D2_NR16B16e4.txt:368-372) -> §2 label (i) \"C6 equal-budget advantage maintained at "
            "N' = 1.6e5 (geometry-axis measurement, UNGATED)\" [\"C6 동일예산 우위가 N′ = 1.6e5 에서도 유지 (기하 축 측정, "
            "UNGATED)\"], quoted together with the registered recovery band (§1): -3 dB R = 0.809 [90% 0.747, 0.870] >= 0.70 "
            "-> \"most of the geometry effect retained\" [\"기하 효과 대부분 유지\"] (NEXT_EXPERIMENTS_C6B16e4.md:36, :44, "
            ":94-97; results/review_next/recovery_NR16B16e4.txt).  The label and the band sentence are cell- and "
            "budget-limited (C6, N_train = 1.6e5) and are not an arm claim.",
            "HOW MUCH: -3 dB failures b* -> V1 (genie) C6 184 -> 53 (22), C2 623 -> 371 (87); recovery R at -3 dB: C6 1.6e5 "
            "0.809 [0.747, 0.870] (_best) / 0.815 [0.756, 0.872] (last-EMA), C6 1e4 0.838 [0.781, 0.892], C2 1.6e5 "
            "(headline) 0.470 [0.427, 0.512] (recovery_NR16B16e4.txt, recovery_NR16B16e4last.txt, recovery_NR16run2.txt, "
            "recovery_B16e4k.txt in results/review_next/; reproduced exactly here).  C2 headline table B at 1.6e5: 302:50, "
            "117:21, 35:7, 3/3, SNR@0.1 gap +1.41 dB [90% +1.22, +1.64] (tables_D2_B16e4k.txt:369-372).",
            "WHY (registered design rationale, 10_SPEC_stageC.md:882 and :888-889; not a mechanism test): by design, the "
            "cells C6 and C2 differ only in Nr (T, Tp, code, SNR grid identical), which raises the co-dimension from 40~55 "
            "(Nr=8) to 104~119 (Nr=16) with rank and pilot structure unchanged.  The runs plotted in (a) and (b) also "
            "differ beyond Nr: V1 weights (C2 legacy last-EMA @1784, results/review_next/NEXT_EXPERIMENTS.md:13, no "
            "clipping -- the checkpoint has no grad_clip field, i.e. it was written by score.train code older than the "
            "§3d clip fallback of commit c343853c; C6 _best @1684 of §3d ladder "
            "step 2, grad-norm clip 1.0, NEXT_EXPERIMENTS_C6B16e4.md:82-83), b* (kron K=1024 vs K=4096) and the "
            "per-array sigma grid (C6 'NR16', NEXT_EXPERIMENTS_C6B16e4.md:32).  With the C6 last-EMA weights "
            f"(raw_NR16B16e4last, row in (c)) V1 has {v3n['NR16B16e4last']} failures at -3 dB, R = {lr:.3f}.  Measured alongside: "
            "at C6 1.6e5 the equal-budget GB' denoising-NMSE ratio diffusion/GMM, computed on the §3d ladder step-2 "
            f"last-EMA checkpoint (d2sx_NR16_N160000_a1_fb2.pt, {sha_l}; report only), is 0.261~0.508, median 0.283, "
            "below 1 at all 20 sigma points (NEXT_EXPERIMENTS_C6B16e4.md:37, :85, :110).",
            "STATUS / SCOPE (registration requirements): C6 has no D1 sibling -> every C6 checkpoint is UNGATED, so every C6 "
            "point is a geometry/budget-axis measurement, NOT an arm verdict, and C6 is NOT the headline; the headline stays "
            "C2 at N_train = 1.6e5 (raw_B16e4k) (NEXT_EXPERIMENTS_C6B16e4.md:28; 10_SPEC_stageC.md:897).  D1-sibling gate "
            "status for C2: 1e4 and 4e4 FAIL recipe (budget-axis measurements, shaded in panel c), 1.6e5 and 3.2e5 PASS "
            "(NEXT_EXPERIMENTS_B32e4.md:118-122).  The shading in (c) refers to C2 only; the C6 1e4 point inside it is "
            "UNGATED like every C6 point.",
            "Recovery R is a report-only statistic (code/recovery_ci.py docstring) except for the registered C6 band rule "
            "(NEXT_EXPERIMENTS_C6B16e4.md:36: R >= 0.70 'most of the geometry effect retained' [기하 효과 대부분 유지], "
            "0.60 <= R < 0.70 'partly retained' [일부 유지], R < 0.60 'mostly a small-budget effect' [대부분 소예산 효과]; "
            "point estimate at -3 dB of the _best tag, the hollow C6 point in (c)).  The "
            "R = 0.70 line in (c) is that C6 band threshold only; the C2 points, the C6 1e4 point and the C6 1.6e5 last-EMA "
            "point are not judged against it.  No trend test over budgets is registered (NEXT_EXPERIMENTS_C6B16e4.md:37).",
            "b* grid-edge caveats: C6 1.6e5 b* = kron K=4096, the largest fitted K (+1.193 nat over K=2048); K=8192 was not "
            "fitted by user decision (NEXT_EXPERIMENTS_C6B16e4.md:69, :81).  C2 3.2e5 b* = kron K=4096 at the grid edge "
            "(NEXT_EXPERIMENTS_B32e4.md:95, :121); C2 4e4 K=2048 at the edge; C2 1.6e5 K=1024 with K=2048 not fitted "
            "(NEXT_EXPERIMENTS_B32e4.md:15-16).  C6 1e4 b* = kron K=128, interior (NEXT_EXPERIMENTS_C6B16e4.md:13, :19).",
            "C6 SNR@0.1 gap: n/a -- b* (184/2560 = 0.072) and V1 (53/2560 = 0.021) are both already below BLER 0.1 at the "
            "lowest grid SNR -3 dB (tables_D2_NR16B16e4.txt:373); the SNR grid is not extended after results "
            "(NEXT_EXPERIMENTS_C6B16e4.md:27, :94).",
            "Training and weights: the C6 1.6e5 weights come from §3d ladder step 2 (--fallback 2, global grad-norm clip "
            "1.0; same rung D2SXNR16160000 and rung attempt a1 = the same data stream; ckpt d2sx_NR16_N160000_a1_fb2.pt / "
            "_fb2_best.pt) after ladder step 1 diverged at epoch 1064; step-1 checkpoints were not evaluated and step 3 "
            "was stopped unopened (NEXT_EXPERIMENTS_C6B16e4.md:82-83, :111).  "
            f"_best sha256[:16] {sha_b} @{ep_b}, last {sha_l} @{ep_l} (raw meta stagec_ckpt_id of raw_NR16B16e4 / "
            "raw_NR16B16e4last, printed in the (c) rows above; asserted against NEXT_EXPERIMENTS_C6B16e4.md:82).  "
            "best vs last V1 at C6 1.6e5: pooled 12:16 (p=0.57), not decided (:109).  Both lines in (c) "
            "use last-EMA weights at every budget (budget-comparison rule: C2 NEXT_EXPERIMENTS_B32e4.md:28, :34; C6 "
            "NEXT_EXPERIMENTS_C6B16e4.md:30: the C6 1e4 point raw_NR16run2 has last-EMA weights only, best not saved, so "
            "the C6 budget comparison is last-EMA): C2 = raw_B1e4, "
            "raw_B4e4k, raw_B16e4k, raw_B32e4last; C6 = raw_NR16run2, raw_NR16B16e4last.  The hollow markers are the "
            "best-validation (_best) weights: C2 3.2e5 raw_B32e4 (the B32e4 judging run) and C6 1.6e5 raw_NR16B16e4 (the "
            "registered measurement tag whose -3 dB R = 0.809 carries the band sentence, :36).  Gradient clipping differs "
            "along the C6 line: the C6 1e4 point (d2sx_NR16_N10000_a1.pt, grad_clip 0.0) and every C2 point were trained "
            "without clipping (C2 3.2e5 grad_clip 0.0; the C2 1e4 / 4e4 / 1.6e5 legacy checkpoints have no grad_clip "
            "field, i.e. score.train code older than the §3d clip fallback of commit c343853c, as in WHY); only the C6 1.6e5 points (§3d ladder step 2) use clip 1.0 (grad_clip of each raw meta "
            "stagec_ckpt, printed in the (c) rows and asserted here).  So the C6 line in (c) changes the budget and the §3d "
            "clip together (NEXT_EXPERIMENTS_C6B16e4.md:31, :111).",
            "R5-genie is a known-channel reference (same LMMSE-PIC/BCJR loop, true H), not a bound.  Its failure vectors "
            "are identical across the tags of each cell (same trials): C6 across raw_NR16run2 / raw_NR16B16e4 / "
            "raw_NR16B16e4last (NEXT_EXPERIMENTS_C6B16e4.md:90, and asserted here); C2 across raw_B1e4 / raw_B4e4k / "
            f"raw_B16e4k / raw_B32e4last / raw_B32e4 (asserted by code/figure_f17.py:{gline}; the record states equal "
            "counts for B16e4k vs B32e4 only, NEXT_EXPERIMENTS_B32e4.md:110; the other C2 tags are covered by this assert "
            "only).  C6 genie +15 dB: the measured value is 0/2560 failures; (b) draws it as a short downward arrow from "
            "the upper end of its 95% Wilson interval (1.50e-3), in the genie slot, labelled 0/2560 and not connected to "
            "the curve; the arrow's position is not a plotted estimate.",
            "In-figure terms -> record terms: 'final EMA weights' = last-EMA checkpoint; 'best-validation weights' / "
            "'best-val.' = _best.pt; 'known-channel reference (genie)' = R5-genie; 'registered band value' = the -3 dB R of "
            "the registered measurement tag NR16B16e4 (§1 band rule); 'UNGATED, measurement, not an arm verdict' = the C6 status "
            "above; 'D1-sibling gate PASS/FAIL' = the checkpoint was trained on D2 with a recipe whose D1 sibling passed / "
            "failed the gate (DECISIONS.md:120, G-1.2 form).  Colours follow the shared role palette of "
            "code/figstyle.py (the same arm keeps the same colour in F16-F18): b* orange diamonds / solid, V1 blue squares "
            "/ solid, genie black stars / dash-dot; in (c) C2 dark-grey circles / solid, C6 violet diamonds / dashed "
            "(hollow = best-validation weights), the R = 0.70 line violet dotted (C6 band only), shading light grey; all "
            "text is black or dark grey.",
            "Scope: testbed D2, prior S2, cells C2 (8x4) and C6 (16x4) only, T=16, Tp=4, SNR -3..+15 dB step 3, test trials "
            "0..2559 (n=2560 per SNR), BLER at the 16th outer iteration (a raised block counts as a failure and stays in "
            "every aggregate: 08_SPEC_analysis.md:71 (§5) forbids averages computed after dropping failed or diverged "
            "blocks; code/analysis.py:41-44 docstring), budgets 1e4..3.2e5 (C2) and 1e4, 1.6e5 (C6) only.  Nothing here "
            "is claimed beyond these cells, SNRs and budgets.",
            f"Horizontal offsets (legibility only; values unchanged): in (a) and (b) every arm is drawn at SNR "
            f"{ARMS[0][5]:+.2f} dB (b*), SNR (V1) or SNR {ARMS[2][5]:+.2f} dB (genie), with genie drawn above V1.  "
            f"In (c) every point on the two lines (last-EMA) "
            f"sits at its exact budget, and each hollow best-validation point is drawn at {HOLLOW_X} x its budget "
            f"(C6 1.6e5 at {1.6e5 * HOLLOW_X:.3g}, C2 3.2e5 at {3.2e5 * HOLLOW_X:.3g}); the x tick labels 1, 4, 16, 32 "
            "(x 1e4) are the exact budgets."]
    print("\n".join(txt + M.block(fh)))


if __name__ == "__main__":
    main()
