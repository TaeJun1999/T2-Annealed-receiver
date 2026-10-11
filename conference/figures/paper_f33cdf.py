"""conference/figures/paper_f33cdf.py -- REPORT-ONLY figure for the ray-traced pools (DeepMIMO = prior DMC, Sionna RT = prior SRT):
the empirical CDF, over the 2560 test trials of a point, of the per-trial channel-estimation NMSE, for the legend curves of
F16deep_wide that have a channel estimate (paper_f16deep.SHOW without Perfect CSI: 10 curves, same colours and line styles).

  F33cdf_<prior>_wide.{pdf,png}   7.16 x 2.55 in, four panels = -3 dB and the three decision SNRs of the registered b* -> V1 pair
                                  (read from conf/results/tables_D2_<tag>.txt; never chosen by hand), one legend above

User, 2026-10-10 CDT (verbatim, after the DeepMIMO BLER curves came out high for every receiver, Perfect CSI included):
"아니면 CDF를 그려볼까?".  Registered as a report-only item in NEXT_EXPERIMENTS_SRT16e4 §1 before any SRT BLER; for DeepMIMO it
is post hoc (the DMC BLER had been seen).  No label, no test, no CI -- the registered judgement is the paired BLER sign test.

Fixed here (nothing is tuned after a result): NMSE = the raw files' `nmse` field (||H_hat - H||_F^2 / ||H||_F^2 per trial) at the
arm's reporting iteration -- the last column (@16; Pilot-only LMMSE = the alias R0-pilot@1, its single column = iteration 1);
x = 10 log10 NMSE, drawn over XLIM (a value outside is clipped only in the drawing); the CDF is over ALL 2560 trials, a
non-finite or non-positive NMSE counts as +inf (the right end; counted in the record); the record lists median and 90th
percentile per curve and panel.  Same raws, same trials as F21dmc / F21srt.
Run (CPU):
  cd ~/t2/conf && CUDA_VISIBLE_DEVICES= ~/miniforge3/envs/torch/bin/python -B ~/t2/conference/figures/paper_f33cdf.py DMC \\
      > ~/t2/conference/figures/records/paper_f33cdf_DMC.txt
"""
import os
import re
import sys

sys.dont_write_bytecode = True
import paper_f21dmc as F                                       # tags per prior (SETS) and the layout checks
import paper_f16deep as D
import matplotlib.pyplot as plt
import numpy as np
from paper_f16deep import BY, FIG, GE, M, N0, Q, SHOW, V1

W, H = 7.16, 2.55
LEFT, RIGHT, BOTTOM, BAND, TOP, GAP = 0.47, 0.06, 0.36, 0.52, 0.16, 0.10      # in; BAND = the legend band, TOP = the panel titles
XLIM, XTICKS = (-35.0, 5.0), [-30, -20, -10, 0]
CURVES = tuple(a for a in SHOW if a != GE)


def decision_snrs(tag):
    with open(os.path.join(M.CONF, "results", f"tables_D2_{tag}.txt"), encoding="utf-8") as f:
        m = re.search(r"M-ours-bstar -> M-ours-dscore-C-V1.*?\n\s*decision SNRs \[([^\]]*)\]", f.read(), re.S)
    return [float(x.strip("' ")) for x in m.group(1).split(",")]


def main(prior):
    tag, sp, ald, prior, name, what, _ = (F.TAG, F.SP, F.ALD, F.PRIOR, F.NAME, F.WHAT, F.REG) if prior == "DMC" else F.SETS[prior]
    dec = decision_snrs(tag)
    snrs = sorted({-3.0, *dec})
    if len(snrs) == 3:                                         # -3 dB is itself a decision SNR (NEXT_EXPERIMENTS_ROOM16e4 §1): the fourth panel
        snrs.append(next(s for s in F.SNRS if s > max(dec)))   # = the next grid SNR above the decision SNRs
    assert len(snrs) == 4, snrs
    D.check_styles()
    plt.rcParams.update(D.RC)
    raws = {t: D.raw(t) for t in (tag, sp, ald)}
    fig = plt.figure(figsize=(W, H))
    w, h = (W - LEFT - RIGHT - 3 * GAP) / 4, H - BOTTOM - BAND - TOP
    axs, rec = [], []
    for i, s in enumerate(snrs):
        ax = fig.add_axes([(LEFT + i * (w + GAP)) / W, BOTTOM / H, w / W, h / H], sharey=axs[0] if axs else None)
        axs.append(ax)
        rec.append(f"  SNR {s:+.0f} dB (median / 90th percentile of 10 log10 NMSE [dB]; non-finite or non-positive trials):")
        for a in CURVES:
            orig = {"SPB16e4k": sp, "ALDB16e4k": ald}.get(BY[a].orig, tag)
            x = np.asarray(raws[orig][(F.CELL, prior, s)][a]["nmse"], float)[:, -1]
            assert len(x) == N0, (a, s, len(x))
            bad = ~(np.isfinite(x) & (x > 0))
            v = np.sort(np.where(bad, np.inf, 10 * np.log10(np.where(bad, 1.0, x))))
            c = BY[a]
            ax.plot(np.clip(v, *XLIM), np.arange(1, N0 + 1) / N0, color=c.color, ls=c.ls, lw=D.size(c)["lw"], label=c.label,
                    zorder=5 if a == V1 else 3)
            rec.append(f"    {a:<21}{np.median(v):8.2f} {np.percentile(v, 90):8.2f}   {int(bad.sum())}")
        ax.set_xlim(*XLIM); ax.set_xticks(XTICKS); ax.set_ylim(0, 1); ax.tick_params(axis="x", pad=Q.XTPAD)
        ax.tick_params(axis="y", labelleft=i == 0)
        ax.set_title(f"SNR = {s:+.0f} dB", fontsize=8, pad=3)
        ax.set_xlabel("NMSE [dB]", labelpad=Q.XPAD)
    axs[0].set_ylabel("CDF")
    hl, ll = axs[0].get_legend_handles_labels()
    leg = fig.legend(hl, ll, loc="center", ncol=5, frameon=False, fontsize=7, bbox_to_anchor=(0.5, (H - BAND / 2) / H),
                     handlelength=2.3, columnspacing=1.4, labelspacing=0.28, borderpad=0.1, handletextpad=0.5)
    bb, small = Q.check(fig, f"F33cdf_{prior}_wide")
    lb = Q.inch(fig, leg.get_window_extent())
    assert lb[1] >= H - BAND and lb[3] <= H and lb[0] >= 0 and lb[2] <= W, ("legend outside its band", lb)
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(FIG, f"F33cdf_{prior}_wide.{ext}"), dpi=300, **({"metadata": {"CreationDate": None}} if ext == "pdf" else {}))
    print("\n".join(
        [f"F33cdf -- {what}; cell C2 = 8x4, N_train = 1.6e5): empirical CDF over the {N0} test trials of the per-trial channel-estimation "
         "NMSE at the reporting iteration (@16; Pilot-only LMMSE @1).  REPORT-ONLY: no label, no test, no CI.  Recomputed from raw by "
         "conference/figures/paper_f33cdf.py (read-only; analysis.load_raw); no number transcribed.", "",
         f"F33cdf_{prior}_wide  {W} x {H} in, four panels: SNR {' '.join(f'{s:+.0f}' for s in snrs)} dB = -3 dB and the decision SNRs of the registered "
         f"b* -> V1 pair (conf/results/tables_D2_{tag}.txt); {len(CURVES)} curves = paper_f16deep.SHOW without Perfect CSI (no estimate), same "
         f"colours and line styles; x drawn over {XLIM} dB (clipped in the drawing only).", "",
         "Curves (internal arm -> figure name): " + "; ".join(f"{a} -> {BY[a].label}" for a in CURVES) + ".", ""] + rec
        + ["", "Raised blocks (analysis.load_raw NOTE lines) in the raws read: " + ("; ".join(D.NOTES) or "none") + ".",
           f"Layout: legend band {BAND} in (inside its band: asserted, [in] {np.round(lb, 3).tolist()}); every artist inside the canvas (tight bbox [in] "
           f"{np.round(bb, 3).tolist()}); smallest visible text {small:g} pt; saved at figsize, PNG 300 dpi."]))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "DMC")
