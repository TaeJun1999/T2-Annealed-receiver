"""conference/figures/paper_f30top.py -- IEEE-size variants of the paper figure F30 (paper_f30.py) that keep ONLY its top row:
(a) Sparse specular, (b) 3GPP UMi 28 GHz -- fraction of the GMM-to-perfect-CSI gap closed vs N_r = 8 / 16 / 32.

  F30top_wide.{pdf,png}  figure* (7.16 in wide): (a) | (b) side by side
  F30top_col.{pdf,png}   one column (3.5 in wide): (a) above (b)

Constants, raw() and the record helpers are imported from paper_f30.py; the (a)/(b) part of its main() -- decision points,
the five frontier_ci.cmd_recovery runs with their asserts, the registered CIs, the record text, the errorbar / per-point-value
drawing -- is copied verbatim (same numbers, markers, error bars, lines, font sizes, rcParams).  Only the figure size, the
panel grid and the exact-size save (no tight crop, 300 dpi) differ.
Asserted in the same run against paper_f30.main() (its savefig disabled, so F30_scale_trend.* is not rewritten; its (c)/(d)
asserts run too): the record text printed here = paper_f30.py's record text without the two (c)/(d) BLER blocks, and every
drawn artist of (a)/(b) (line data, error-bar segments, markers, value labels, scales, limits, ticks, labels) = its top row.
Run (CPU, ~40 s): cd ~/t2/conf && CUDA_VISIBLE_DEVICES= ~/miniforge3/envs/torch/bin/python -B ~/t2/conference/figures/paper_f30top.py
"""
import contextlib
import difflib
import io
import os
import re
import sys
from unittest import mock

sys.dont_write_bytecode = True                                 # no __pycache__ next to paper_f30.py or in conf/code
import paper_f30 as P                                          # also applies paper_f30's rcParams (fonts, grid, TrueType)
from paper_f30 import BS, CAVEATS, CELLS, F, FIG, INK, INK2, LABELS_KO, RUNS, RV, decision_points, f3, raw, s3
import matplotlib.figure
import matplotlib.text
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({"pdf.fonttype": 42, "ps.fonttype": 42,   # TrueType (already set by paper_f30; restated as a requirement)
                     "savefig.bbox": "standard"})              # save at exactly figsize (paper_f30 crops 'tight')
SIZES = (("F30top_wide", (7.16, 2.5), (1, 2)),                 # figure*: (a) | (b)
         ("F30top_col", (3.5, 4.3), (2, 1)))                   # one column: (a) over (b)


def drawn(ax):
    """what a top-row panel draws, as a comparable value (for the assert against paper_f30's own (a)/(b))"""
    return ([(l.get_xydata().tolist(), l.get_marker(), l.get_markersize(), l.get_color(), l.get_linewidth(), l.get_linestyle(),
              l.get_zorder()) for l in ax.lines],
            [([s.tolist() for s in c.get_segments()], c.get_linewidth().tolist()) for c in ax.collections],
            [(t.get_position(), t.get_text(), t.get_fontsize(), t.get_color()) for t in ax.texts],
            ax.get_xscale(), ax.get_xlim(), ax.get_ylim(), ax.get_xticks().tolist(), [t.get_text() for t in ax.get_xticklabels()],
            ax.get_xlabel(), ax.get_ylabel(), ax.get_title(loc="left"))


def main():
    # ---------------- paper_f30.main() lines 146-186, verbatim ----------------
    specs = {k: f"{raw(v[0])}:{v[1]}:{','.join(str(s) for s in v[3])}" for k, v in CELLS.items()}
    txt = ["F30 -- the antenna-array scaling axis (SCALE16e4): recovery over the decision points R_dp vs Nr = 8 / 16 / 32 (C2 / C6 / C9, "
           "Nt 4, T 16, Tp 4, equal budget N' = 1.6e5, test trials 0..2559, n = 2560 per SNR, BLER@16) for D2 and UMi28, and the BLER "
           "curves of the two C9 cells.  Recomputed from raw by code/figure_f30.py (frontier_ci.cmd_recovery, B 2000, seed 20260926) "
           "and asserted against NEXT_EXPERIMENTS_SCALE16e4 §6.1.", "",
           "raw paths (read-only): " + "; ".join(f"{d} Nr {nr} {v[1]} = {raw(v[0])}" for (d, nr), v in CELLS.items()), ""]
    # ---------------- decision points + counts per cell ----------------
    for (dset, nr), (tag, cell, prior, dp, cnt, rr, src) in CELLS.items():
        d = F.raws(raw(tag))
        snrs = sorted(k[2] for k in d if k[:2] == (cell, prior))
        got = decision_points(d, cell, prior, snrs, BS)
        assert got == [float(s) for s in dp], (tag, got, dp)
    # ---------------- the five frontier runs ----------------
    R = {}
    fr = ["recomputed frontier_ci.cmd_recovery output (raw names = the paths above):"]
    for name, c1, c2, level, rec12, recd, src, owns in RUNS:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            out = F.cmd_recovery(specs[c1], specs[c2], F.B, F.SEED, level)
        fr += [f"  [{name}; record {src}]"] + ["  " + l for l in buf.getvalue().splitlines()]
        got = buf.getvalue()
        for c in (c1, c2):
            got = got.replace(raw(CELLS[c][0]), f"raw_{CELLS[c][0]}")
        fil = open(os.path.join(RV, f"scale2_{src.split(':')[0]}.txt"), encoding="utf-8").read().splitlines()[1:8]
        assert got.splitlines() == fil, (name, got, fil)              # byte-identical to the record file lines 2-8
        for j, c in enumerate((c1, c2)):
            r = out["r"][j]; lo, hi = F.pct(out["bo"][:, j], [5, 95])
            _, (b, v, g) = F._R(F._rec_cols(specs[c])[3])
            assert (b, v, g) == CELLS[c][4], (name, c, b, v, g)
            assert (f3(r), f3(lo), f3(hi)) == rec12[j], (name, c, r, lo, hi)
            if c in owns:                                   # the run whose file line registers this cell's CI (CELLS source)
                R[c] = (r, lo, hi)
        lo, hi, p = F.ci_p(out["bo"][:, 0] - out["bo"][:, 1], level)
        dr = out["r"][0] - out["r"][1]
        assert (s3(dr), s3(lo), s3(hi), f"{p:.4f}") == recd, (name, dr, lo, hi, p)
    assert set(R) == set(CELLS), sorted(set(CELLS) - set(R))
    for (dset, nr), (tag, cell, prior, dp, cnt, rr, src) in CELLS.items():
        r, lo, hi = R[(dset, nr)]
        assert (f3(r), f3(lo), f3(hi)) == rr, (dset, nr, r, lo, hi, rr)   # the drawn CI = the registered one
        txt.append(f"  {dset:<6} Nr {nr:>2} {cell}  raw_{tag:<13} decision SNRs {list(dp)} (recomputed, anchor b*)  SigmaF b* {cnt[0]} "
                   f"V1 {cnt[1]} genie {cnt[2]}  R_dp = {r:.3f} [90% {lo:.3f}, {hi:.3f}]  (registered CI: {src})")
    # ---------------- paper_f30.main() lines 224-227, verbatim (the (c)/(d) BLER blocks of lines 202-217 are not copied) ----------------
    txt += ["", "Annotations in (a)/(b) are English glosses of the registered labels below (verbatim)."] + LABELS_KO + [""] + CAVEATS \
        + ["", "Asserted: lines 2-8 of each scale2_<run>.txt reproduced byte-identically (raw path -> raw_<tag>); decision points of the 6 cells (anchor b*), SigmaF (b*, V1, genie) and R_dp [90%] of every cell in every run, "
           "Delta R [level] + p of the 5 runs (§6.1.1 / §6.1.2 / the scale2_* record files), C9 failures per SNR of genie / V1 / b* "
           "(§6.1.4 (b)) and R2 (pairB_<T>.txt)."] + [""] + fr

    # ---------------- reference: paper_f30.main() itself, in this process ----------------
    buf = io.StringIO()
    with mock.patch.object(matplotlib.figure.Figure, "savefig"), contextlib.redirect_stdout(buf):
        P.main()
    ref_axes = plt.gcf().axes[:2]                                   # its (a), (b)
    ref = re.sub(r"\n\n\([cd]\) .*(?:\n  .*)*", "", buf.getvalue())  # its record text minus the (c)/(d) BLER blocks
    mine = "\n".join(txt) + "\n"
    assert mine == ref, "\n".join(difflib.unified_diff(ref.splitlines(), mine.splitlines(), "paper_f30 (a)/(b)", "paper_f30top",
                                                       lineterm=""))

    # ---------------- figures ----------------
    for name, size, grid in SIZES:
        fig, axs = plt.subplots(*grid, figsize=size, layout="constrained")
        for ax, ref_ax, dset, tl in zip(axs, ref_axes, ("D2", "UMi28"), ("(a)", "(b)")):
            # paper_f30.main() lines 191-200, verbatim
            nrs = [8, 16, 32]
            y = np.array([R[(dset, n)][:3] for n in nrs])
            ax.errorbar(nrs, y[:, 0], yerr=[y[:, 0] - y[:, 1], y[:, 2] - y[:, 0]], color=INK, marker="o", ms=4.5, lw=1.1, capsize=2.5,
                        elinewidth=1.0, zorder=3)
            for n, (r, lo, hi) in zip(nrs, y):
                ax.text(n, hi + 0.02, f"{r:.3f}", va="bottom", ha="center", fontsize=7, color=INK2)
            ax.set_xscale("log", base=2); ax.set_xticks(nrs, ["8", "16", "32"]); ax.set_xlim(6.3, 45)
            ax.minorticks_off(); ax.set_ylim(0, 1.0); ax.set_xlabel(r"Receive antennas $N_r$ ($N_t = 4$)")
            ax.set_ylabel("Fraction of the GMM-to-\nperfect-CSI gap closed")
            ax.set_title(tl, loc="left", fontweight="bold", fontsize=8.2)
            assert drawn(ax) == drawn(ref_ax), (name, tl)            # same artists as paper_f30's (a)/(b)
        for ext in ("pdf", "png"):
            fig.savefig(os.path.join(FIG, f"{name}.{ext}"), dpi=300)
        sizes = [t.get_fontsize() for t in fig.findobj(matplotlib.text.Text) if t.get_text() and t.get_visible()]
        assert min(sizes) >= 7, (name, min(sizes))                  # >= 7 pt at final size (saved at figsize)
        plt.close(fig)
    print(mine, end="")                                             # record text (internal names), not written to a file


if __name__ == "__main__":
    main()
