"""conference/figures/paper_f2cpilot.py -- Fig. 2 (c) candidate: SNR needed for BLER 0.1 against the pilot length T_p
(D2 8x4, T = 16, QPSK, headline checkpoint and fits; cells C2 / C7 / C8 = T_p 4 / 6 / 8, K_b 42 / 34 / 26).
Two versions of the same panel (user, 2026-10-18: "둘다 해보고 보기 편한거로 하자"): F2c_pilot = x tick labels "T_p (K_b)" in one
row + an x label, axes bottom 0.36 in like the other Fig. 2 panels; F2c_pilot2r = T_p over K_b in two tick rows named at their
left, axes bottom raised in 0.01 in steps to the smallest value that keeps every text on the canvas.

No new trials: the barred curves and the caption numbers are read from committed records and asserted against the values the
task prompt lists (conf/results/review_next/prompts/PROMPT_FIG_PILOT.md, 2026-10-18); the three thin curves are computed from
the raws and asserted against the SNR@0.1 column of the tables' per-arm block.
  - Proposed (V1) / GMM prior (b*) / Perfect CSI (genie): SNR@0.1 and its 90% interval from
    conf/results/review_next/frontier_PARB16e4.txt (the prompt's source; unpaired bootstrap across cells);
  - Gaussian prior (R2): drawn because its interval is on record -- conf/figs/F19_pilot_pareto.txt (b), the single-spec
    bootstrap of the same frontier_ci (B = 2000, seed 20260926); frontier_PARB16e4.txt has no R2 line (user: "일단 포함시켜");
  - the other curves of the Fig. 2 legend band that exist in all three cells' raws -- turbo LMMSE (R1), BiG-AMP (R3) at
    iteration 16 and pilot-only LMMSE at iteration 1 (R0-pilot@1) -- as point values only (no bars, as in Fig. 2), computed
    from the raws (read-only) with frontier_ci.snr_at and asserted against the SNR@0.1 column of tables_D2_B16e4k.txt (C2) /
    tables_D2_PARB16e4.txt (C7, C8); ALD, SBL (loop / pilot-only) and OMP were never run in C7 / C8 and are
    left out (caption; user: "다른 arm에서 측정이 불가능하면 빼고 캡션에 밝혀야지").  The four barred curves are recomputed
    from the raws too and asserted equal to their records;
  - the caption numbers (P-a, P-b, the genie payload effect; same-T_p paired gaps) from frontier_PARB16e4.txt,
    results/tables_D2_PARB16e4.txt (C7, C8) and results/tables_D2_B16e4k.txt (C2).
Panel = F2c_room_sel of the paper repo (figures/paper_f2sel.py): 2.00 x 2.00 in, axes margins left 0.48 / right 0.04 /
bottom 0.36 / top 0.05 in, its rcParams; curve colour / marker / line / fill / size = paper_f16deep (the Fig. 2 legend band
F2legend_*); no legend, panel label or title inside.
    python conference/figures/paper_f2cpilot.py   -> F2c_pilot{,2r}.{pdf,png}, records/paper_f2cpilot.txt
"""
import hashlib
import itertools
import os
import re
import sys

import paper_f16deep as D                                      # curve shapes and sizes (puts conf/code on sys.path)
from frontier_ci import points, raws, snr_at
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CONF = os.path.normpath(os.path.join(HERE, "..", "..", "conf"))
FRONTIER = os.path.join(CONF, "results/review_next/frontier_PARB16e4.txt")
F19 = os.path.join(CONF, "figs/F19_pilot_pareto.txt")
TAB_PAR, TAB_C2 = os.path.join(CONF, "results/tables_D2_PARB16e4.txt"), os.path.join(CONF, "results/tables_D2_B16e4k.txt")
INK = "#0b0b0b"
RC = {"font.family": "STIXGeneral", "mathtext.fontset": "stix", "font.size": 8, "axes.labelsize": 8,       # paper_f2sel.py 35-39
      "xtick.labelsize": 8, "ytick.labelsize": 8, "legend.fontsize": 7, "text.color": INK,
      "axes.labelcolor": INK, "xtick.labelcolor": INK, "ytick.labelcolor": INK,
      "savefig.bbox": "standard", "pdf.fonttype": 42, "ps.fonttype": 42,
      "axes.grid": True, "grid.alpha": 0.25, "grid.linewidth": 0.5, "figure.dpi": 200}
XPAD, XTPAD = 1.0, 2.5                                         # x label labelpad, x tick pad [pt], paper_f2sel.py
W, H, LEFT, RIGHT, BOTTOM, TOP = 2.00, 2.00, 0.48, 0.04, 0.36, 0.05   # F2c_room_sel [in]
CELLS = (("C2", 4, 42), ("C7", 6, 34), ("C8", 8, 26))
V1, BS, R2, GE = D.V1, D.BS, "R2-ours-G", D.GE
BARS = (V1, BS, R2, GE)                                        # 90% bars (= paper_f16deep.BARS)
THIN = ("R1-turbo", "R3-bigamp", "R0-pilot@1")                 # point values only
DROPPED = ("ALD-pilot", "SBL-loop", "SBL-pilot", "OMP-pilot")  # not run in C7 / C8
ARMS = ("R0-pilot@1", "R3-bigamp", "R1-turbo", R2, GE, BS, V1)  # drawing order = zorder: proposed on top, then b*, genie (paper_f16deep)
SRC = {"C2": "raw_B16e4k+raw_PARB16e4", "C7": "raw_PARB16e4", "C8": "raw_PARB16e4"}   # = frontier_PARB16e4 / F19
SHORT = {V1: "V1", BS: "bstar", GE: "genie"}                   # names in frontier_PARB16e4.txt
YLIM, YTICKS = (-6.0, 7.0), [-6, -4, -2, 0, 2, 4, 6]
NEAR_PT = 1.5                                                  # record: marker centres closer than this (listed, never moved)
# the values the prompt lists (asserted against the records)
PROMPT_PT = {(V1, "C2"): -2.23, (V1, "C7"): -2.92, (V1, "C8"): -3.57, (BS, "C2"): -0.81, (BS, "C7"): -1.83, (BS, "C8"): -2.60,
             (GE, "C2"): -4.81, (GE, "C7"): -4.84, (GE, "C8"): -5.26}
PROMPT_PA, PROMPT_PB, PROMPT_GE48 = (-0.40, -0.64, -0.17), (+0.38, +0.14, +0.63), (+0.45, +0.24, +0.66)
PROMPT_GAP = {"C2": (1.41, None, None), "C7": (1.09, 0.90, 1.28), "C8": (0.97, 0.79, 1.14)}
NUM = r"([+-]?\d+\.\d+)"


def read_frontier():
    """frontier_PARB16e4.txt: '<name>_<cell>: ... SNR@0.1 = v dB  [90% lo, hi; censored c%]' (a spec printed in several pairs
    must agree with itself) and 'Delta = A - B = d dB  [90% lo, hi]  [95% ...]'"""
    pt, delta = {}, {}
    for line in open(FRONTIER):
        m = re.match(rf"\s+(\w+)_(C\d): .* SNR@0\.1 = {NUM} dB  \[90% {NUM}, {NUM}; censored ([\d.]+)%\]", line)
        if m:
            v = tuple(float(x) for x in m.group(3, 4, 5, 6))
            assert pt.setdefault((m[1], m[2]), v) == v, (m[1], m[2], v)
        m = re.match(rf"\s+Delta = (\w+) - (\w+) = {NUM} dB  \[90% {NUM}, {NUM}\]", line)
        if m:
            delta[(m[1], m[2])] = tuple(float(x) for x in m.group(3, 4, 5))
    return pt, delta


def read_f19_r2():
    out = {}
    for line in open(F19):
        m = re.match(rf"\s+(C\d) Tp/T=[\d.]+ R2-ours-G\s+{NUM} \[90% {NUM}, {NUM}\] censored ([\d.]+)%", line)
        if m:
            out[m[1]] = tuple(float(x) for x in m.group(2, 3, 4, 5))
    return out


def read_gap(path, want_cells):
    """table B section 'M-ours-bstar -> M-ours-dscore-C-V1' of each '--- cell Cx' block: its 'SNR@0.1 gap' line"""
    cell, pair, out = None, None, {}
    for line in open(path):
        m = re.match(r"--- cell (C\d) ", line)
        cell = m[1] if m else cell
        m = re.match(r"\s+(\S+) -> (\S+)\s+\[decision-point anchor", line)
        pair = (m[1], m[2]) if m else pair
        m = re.match(rf"\s+SNR@0\.1 gap \(M-ours-bstar minus M-ours-dscore-C-V1\): {NUM} dB  \[90% paired bootstrap {NUM}, {NUM};", line)
        if m and cell in want_cells and pair == (BS, V1):
            assert cell not in out, cell
            out[cell] = tuple(float(x) for x in m.group(1, 2, 3))
    return out


def read_snr01(path, cells):
    """the per-arm block 'arm  SNR@0.1  SNR@0.1 gap (this arm minus R2-ours-G)' of each '--- cell Cx': {(arm, cell): SNR@0.1}"""
    cell, out = None, {}
    for line in open(path):
        m = re.match(r"--- cell (C\d) ", line)
        cell = m[1] if m else cell
        m = re.match(rf"    (R0-pilot \(@1\)|R1-turbo|R3-bigamp)\s+{NUM}\s", line)
        if m and cell in cells:
            arm = "R0-pilot@1" if m[1].startswith("R0") else m[1]
            assert (arm, cell) not in out, (arm, cell)
            out[(arm, cell)] = float(m[2])
    return out


def sha16(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]


def from_raw(arm, cell):
    """SNR@0.1 of one (arm, cell) from the raws: BLER at iteration 16 (column -1), or 1 for the '@1' arm (column 0);
    a raised block counts as a failure (frontier_ci.fails)"""
    d = raws(SRC[cell]); keys = points(d, cell)
    name, col = (arm[:-2], 0) if arm.endswith("@1") else (arm, -1)
    cols = [np.where(np.isfinite(v := np.asarray(d[k][name]["blk_err"])[:, col]), v, 1.0) for k in keys]
    assert all(len(c) == 2560 for c in cols)
    v, flag = snr_at([k[2] for k in keys], [c.mean() for c in cols], len(cols[0]))
    return v, flag


def draw(est, xs, two_rows):
    fig = plt.figure(figsize=(W, H))
    bottom = BOTTOM
    while True:                                                # 2r: raise the bottom by 0.01 in until every text is on the canvas
        fig.clear()
        ax = fig.add_axes([LEFT / W, bottom / H, (W - LEFT - RIGHT) / W, (H - bottom - TOP) / H])
        for z, a in enumerate(ARMS):
            c = D.BY[a]; e = np.array([est[(a, cell)] for cell, _, _ in CELLS])
            kw = dict(color=c.color, marker=c.marker, ls=c.ls, mfc=c.color if c.filled else "white", zorder=3 + z, **D.size(c))
            if a in BARS:
                ax.errorbar(xs, e[:, 0], yerr=[e[:, 0] - e[:, 1], e[:, 2] - e[:, 0]], capsize=D.ARM["capsize"],
                            elinewidth=D.ARM["elinewidth"], **kw)
            else:
                ax.plot(xs, e[:, 0], **kw)
        ax.set_xlim(3.2, 8.8); ax.tick_params(axis="x", pad=XTPAD)
        ax.set_ylim(*YLIM); ax.set_yticks(YTICKS)
        ax.set_ylabel("SNR at BLER 0.1 [dB]")                   # one-line y label: default labelpad, as F2a / F2b / F2c_room
        if two_rows:
            ax.set_xticks(xs, [f"{tp}\n{kb}" for _, tp, kb in CELLS])
        else:
            ax.set_xticks(xs, [f"{tp} ({kb})" for _, tp, kb in CELLS])
            ax.set_xlabel("Pilots $T_p$ (payload $K_b$)", labelpad=XPAD)
        fig.canvas.draw(); r = fig.canvas.get_renderer()
        if two_rows:                                           # row names, right-aligned left of the first tick label
            bb0 = ax.get_xticklabels()[0].get_window_extent(r)
            for frac, name in ((0.75, "$T_p$"), (0.25, "$K_b$")):
                fig.text((bb0.x0 - 3 * fig.dpi / 72) / fig.dpi / W, (bb0.y0 + frac * bb0.height) / fig.dpi / H, name, ha="right", va="center")
            fig.canvas.draw()
        low = min(t.get_window_extent(r).y0 for t in fig.findobj(plt.Text) if t.get_visible() and t.get_text().strip())
        if low >= 0 or not two_rows:
            break
        bottom = round(bottom + 0.01, 2)
    # checks: everything inside the canvas, no visible text below 7 pt, no two texts overlap, the axes box where it was put
    texts = [t for t in fig.findobj(plt.Text) if t.get_visible() and t.get_text().strip()]
    boxes = [(t.get_text(), t.get_window_extent(r)) for t in texts]
    for s, b in boxes:
        assert b.x0 >= 0 and b.y0 >= 0 and b.x1 <= fig.bbox.x1 and b.y1 <= fig.bbox.y1, (s, b)
    assert all(t.get_fontsize() >= 7 for t in texts)
    for (s1, b1), (s2, b2) in itertools.combinations(boxes, 2):
        assert not b1.overlaps(b2), (s1, s2)
    axb = ax.get_window_extent(r)
    ax_in = [round(v / fig.dpi, 3) for v in (axb.x0, axb.y0, axb.x1, axb.y1)]
    assert np.allclose(ax_in, [LEFT, bottom, W - RIGHT, H - TOP], atol=1e-3), ax_in
    pts = {a: ax.transData.transform(np.c_[xs, [est[(a, c)][0] for c, _, _ in CELLS]]) * 72 / fig.dpi for a in ARMS}
    near = [f"{a1} / {a2} at T_p {int(x)}: {np.hypot(*(p1 - p2)):.2f} pt" for a1, a2 in itertools.combinations(ARMS, 2)
            for x, p1, p2 in zip(xs, pts[a1], pts[a2]) if np.hypot(*(p1 - p2)) < NEAR_PT]
    name = "F2c_pilot2r" if two_rows else "F2c_pilot"
    outs = {}
    for ext in ("pdf", "png"):
        p = os.path.join(HERE, f"{name}.{ext}")
        fig.savefig(p, dpi=300, **({"metadata": {"CreationDate": None}} if ext == "pdf" else {}))
        outs[ext] = sha16(p)
    plt.close(fig)
    return (f"  {name:<12} {W} x {H} in, axes [{LEFT}, {bottom}] .. [{W - RIGHT}, {H - TOP}] in; x tick labels "
            + ("'T_p' over 'K_b' (two rows, named at their left), no x label" if two_rows else "'T_p (K_b)', x label 'Pilots T_p (payload K_b)'")
            + f"; sha256[:16] pdf {outs['pdf']}  png {outs['png']}"), near


def main():
    assert (XPAD, XTPAD) == (D.Q.XPAD, D.Q.XTPAD)                  # the pads of every Fig. 2 panel script here
    pt, delta = read_frontier()
    r2 = read_f19_r2()
    gap = {**read_gap(TAB_PAR, ("C7", "C8")), **read_gap(TAB_C2, ("C2",))}
    est = {(a, c): pt[(SHORT[a], c)][:3] for a in (V1, BS, GE) for c, _, _ in CELLS}
    est.update({(R2, c): r2[c][:3] for c, _, _ in CELLS})
    assert set(ARMS) | set(DROPPED) == set(D.SHOW) and set(BARS) == set(D.BARS) and not set(ARMS) & set(DROPPED)
    for c in ("C7", "C8"):                                     # the left-out curves: no column in the C7 / C8 raws
        have = set(raws(SRC[c])[points(raws(SRC[c]), c)[0]])
        assert not {a.removesuffix("@1") for a in DROPPED} & have and {a.removesuffix("@1") for a in ARMS} <= have, (c, have)
    raw = {(a, c): from_raw(a, c) for a in ARMS for c, _, _ in CELLS}
    assert all(f == "ok" for _, f in raw.values()), raw          # every drawn curve crosses BLER 0.1 inside its grid
    for (a, c), (v, _) in raw.items():
        if a in BARS:
            assert round(v, 2) == est[(a, c)][0], (a, c, v)    # the records' point values = the raws
        else:
            est[(a, c)] = (v, v, v)
    tab = {**read_snr01(TAB_C2, ("C2",)), **read_snr01(TAB_PAR, ("C7", "C8"))}
    assert all(round(est[(a, c)][0], 2) == tab[(a, c)] for a in THIN for c, _, _ in CELLS), tab   # the thin curves = the tables
    assert all(pt[(SHORT[a], c)][3] == 0 for a in (V1, BS, GE) for c, _, _ in CELLS) and all(r2[c][3] == 0 for c in r2)  # no censoring
    for k, v in PROMPT_PT.items():
        assert est[k][0] == v, (k, est[k], v)
    assert delta[("V1_C2", "bstar_C7")] == PROMPT_PA and delta[("V1_C2", "bstar_C8")] == PROMPT_PB
    assert delta[("genie_C2", "genie_C8")] == PROMPT_GE48
    for c, (g, lo, hi) in PROMPT_GAP.items():
        assert gap[c][0] == g and (lo is None or gap[c][1:] == (lo, hi)), (c, gap[c])
    for a, c in est:
        assert est[(a, c)][1] <= est[(a, c)][0] <= est[(a, c)][2] and YLIM[0] < est[(a, c)][1] and est[(a, c)][2] < YLIM[1], (a, c)

    plt.rcParams.update(RC)
    xs = np.array([tp for _, tp, _ in CELLS], float)
    files, nears = zip(*(draw(est, xs, two) for two in (False, True)))
    near = sorted(set(nears[0]) | set(nears[1]))
    m = lambda v: f"{v:+.2f}"
    lab = {V1: "Proposed (V1)", BS: "GMM prior (b*)", R2: "Gaussian prior (R2)", GE: "Perfect CSI (genie)",
           "R1-turbo": "Turbo LMMSE (R1) @16", "R3-bigamp": "BiG-AMP (R3) @16", "R0-pilot@1": "Pilot-only (R0) @1"}
    src = {V1: "frontier_PARB16e4.txt", BS: "frontier_PARB16e4.txt", GE: "frontier_PARB16e4.txt", R2: "conf/figs/F19_pilot_pareto.txt (b)",
           **{a: "raws (frontier_ci.snr_at) = tables_D2_{B16e4k,PARB16e4}.txt" for a in THIN}}
    txt = ["F2c_pilot -- Fig. 2 (c) candidate: SNR needed for BLER 0.1 vs the pilot length T_p (D2 8x4, T = 16, QPSK; headline "
           "checkpoint d2sx_N160000_a1.pt, headline fits b* kron K = 1024; cells C2 / C7 / C8).  No new trials: barred curves "
           "and caption numbers read from the records below, thin curves computed from the raws; all asserted against the "
           "records (task prompt conf/results/review_next/prompts/PROMPT_FIG_PILOT.md).", "",
           "Files (PNG 300 dpi; PDF TrueType; same curves, only the x tick labelling and the axes bottom differ):", *files,
           f"  (F2c_room_sel: axes [{LEFT}, {BOTTOM}] .. [{W - RIGHT}, {H - TOP}] in)", "",
           "SNR@0.1 [dB]; barred curves with the 90% bootstrap interval of their record (B = 2000, seed 20260926; censored 0% "
           "everywhere), the others point values from the raws:",
           "  arm                    " + "".join(f"T_p {tp} (K_b {kb})          " for _, tp, kb in CELLS) + "source"]
    for a in ARMS[::-1]:
        txt.append(f"  {lab[a]:<22} " + "".join((f"{m(est[(a, c)][0])} [{m(est[(a, c)][1])}, {m(est[(a, c)][2])}]    " if a in BARS
                                                  else f"{m(est[(a, c)][0])}                  ") for c, _, _ in CELLS) + src[a])
    txt.append(f"  left out (no C7 / C8 raw: never run there): {', '.join(DROPPED)}")
    txt += ["", "Caption / text numbers (from the records; asserted against the prompt):",
            f"  P-a (registered): V1 (T_p 4) - b* (T_p 6) = {m(PROMPT_PA[0])} dB [90% {m(PROMPT_PA[1])}, {m(PROMPT_PA[2])}]"
            f" (frontier_PARB16e4.txt; the registered Holm-first 95% CI is [-0.67, -0.13])",
            f"  P-b (registered): V1 (T_p 4) - b* (T_p 8) = {m(PROMPT_PB[0])} dB [90% {m(PROMPT_PB[1])}, {m(PROMPT_PB[2])}]"
            " (frontier_PARB16e4.txt)",
            "  same-T_p paired gap b* - V1 (table B section M-ours-bstar -> M-ours-dscore-C-V1, 90% paired bootstrap): "
            + "; ".join(f"T_p {tp} {m(gap[c][0])} [{m(gap[c][1])}, {m(gap[c][2])}]" for c, tp, _ in CELLS)
            + "  (C2: tables_D2_B16e4k.txt, grid -3..+15 dB; C7 / C8: tables_D2_PARB16e4.txt)",
            f"  Perfect CSI T_p 4 -> 8 (payload only): genie C2 - genie C8 = {m(PROMPT_GE48[0])} dB [90% {m(PROMPT_GE48[1])},"
            f" {m(PROMPT_GE48[2])}] (frontier_PARB16e4.txt)",
            "", "Notes for the caption:",
            "  - cross-cell intervals are UNPAIRED bootstraps (different cells = different trial streams); the same-T_p gaps are paired.",
            "  - fixed frame T = 16, variable payload K_b = Nt (T - T_p) - 6: not 'the same message with fewer pilots'; the "
            "best-T_p envelope on the test set is not a policy.",
            "  - Gaussian prior from F19's single-spec bootstrap; for V1 / b* / genie the frontier file and the F19 record "
            "differ by <= 0.02 dB at some interval ends (draw order of the bootstrap), never in the point values.",
            "  - the panel draws 7 of the 11 curves of the Fig. 2 legend band: ALD, SBL (in loop), SBL (pilot-only) and OMP "
            "(pilot-only) were never run in the T_p = 6 / 8 cells (caption: say so).",
            "  - bars only on Proposed / GMM / Gaussian / Perfect CSI (as in Fig. 2); pilot-only LMMSE is its 1-pass BLER (as in Fig. 2).",
            "  - geometry: no legend / panel label / title inside; y not inverted (lower = better); F2c_pilot keeps the axes "
            "bottom 0.36 in of the other panels, F2c_pilot2r raises it (two 8 pt tick rows do not fit under 0.36 in).",
            f"  - marker centres closer than {NEAR_PT} pt: " + ("; ".join(near) if near else "none"),
            "", f"Records read: frontier_PARB16e4.txt sha256[:16] {sha16(FRONTIER)}, F19_pilot_pareto.txt {sha16(F19)}, "
            f"tables_D2_PARB16e4.txt {sha16(TAB_PAR)}, tables_D2_B16e4k.txt {sha16(TAB_C2)}."]
    os.makedirs(os.path.join(HERE, "records"), exist_ok=True)
    with open(os.path.join(HERE, "records", "paper_f2cpilot.txt"), "w") as f:
        f.write("\n".join(txt) + "\n")
    print("\n".join(txt))


if __name__ == "__main__":
    sys.exit(main())
