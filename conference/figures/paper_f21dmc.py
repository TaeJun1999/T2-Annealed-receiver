"""conference/figures/paper_f21dmc.py -- the DeepMIMO scenario (DeepMIMO v4, six city scenarios at 28 GHz, 20 m block split; prior
DMC, cell C2 = 8x4, equal budget N' = 1.6e5) as ONE panel with the legend of F16deep_wide (paper_f16deep.py): the same 11 curves.

  F21dmc_col.{pdf,png}   3.5 x 3.45 in (one column), BLER vs SNR, legend above the panel
  Curves = paper_f16deep.SHOW with its shapes and sizes.  n = 2560 (test trials 0..2559) at EVERY SNR for every curve --
  NEXT_EXPERIMENTS_DMCBASE16e4 §1 "그림": DMC has no n = 20480 raw.  95% Wilson bars on Proposed, GMM prior, Gaussian prior and
  Perfect CSI (paper_f16deep.BARS), as F16deep_wide (a).  y is log over YLIM: on this pool every curve, Perfect CSI included,
  stays above BLER 0.2 at +15 dB (asserted: no point outside YLIM).

Nothing is transcribed by hand.  The curves are read with analysis.load_raw (a raised block = a failure; R0-pilot@1 = the 1-pass
alias): seven from raw_DMCB16e4, Annealed Langevin (plug-in) from raw_ALDDMC, the sparse three from raw_SPDMC.  Asserted, else
the script stops before saving:
  - every count = the 'BLER@16 failures / n per SNR' table of conf/results/review_next/pairB_SPDMC.txt (11 arms x 7 SNRs);
  - same trials: the Perfect CSI error arrays of raw_ALDDMC and raw_SPDMC = raw_DMCB16e4's at the seven SNRs;
  - drawn = counted (paper_f16deep.draw reads the artists back); the panel holds exactly the curves of the legend; every artist
    inside the canvas, every visible text >= 7 pt.
Run (CPU):
  cd ~/t2/conf && CUDA_VISIBLE_DEVICES= ~/miniforge3/envs/torch/bin/python -B ~/t2/conference/figures/paper_f21dmc.py \\
      > ~/t2/conference/figures/records/paper_f21dmc.txt
"""
import os
import re
import sys

sys.dont_write_bytecode = True                                 # no __pycache__ next to the paper_f*.py or in conf/code
import paper_f16deep as D                                      # the legend: CURVES / SHOW, shapes, sizes, the record parser
import matplotlib.pyplot as plt
import numpy as np
from paper_f16deep import BY, FIG, GE, M, N0, Q, SHOW, SNRS, V1

TAG, SP, ALD, CELL, PRIOR = "DMCB16e4", "SPDMC", "ALDDMC", "C2", "DMC"
NAME, WHAT, REG = "F21dmc", "DeepMIMO (prior DMC: DeepMIMO v4, six city scenarios at 28 GHz, 20 m block split", "NEXT_EXPERIMENTS_DMCBASE16e4 §1"
W, H = 3.5, 3.45
LEFT, RIGHT, BOTTOM, BAND, TOP = 0.56, 0.06, 0.36, 0.86, 0.03  # in; BAND = the legend band above the axes
YLIM, YTICKS, XLIM = (0.2, 1.05), [0.2, 0.3, 0.5, 0.7, 1.0], (-4, 16)
# `paper_f21dmc.py SRT` (NEXT_EXPERIMENTS_SRT16e4 §1 "그림"): the same panel for the Sionna RT pool.  Its y range is set by rule
# from the data -- the largest ladder value below every point and every lower Wilson bar end (YLADDER) -- never by eye.
SETS = {"SRT": ("SRTB16e4", "SPSRT", "ALDSRT", "SRT", "F21srt",
                "Sionna RT (prior SRT: Sionna RT 2.1, built-in scenes munich / etoile / florence at 28 GHz, 20 m block split", "NEXT_EXPERIMENTS_SRT16e4 §1"),
        # room pools, ONE fixed BS (NEXT_EXPERIMENTS_ROOM16e4 §1 "그림"): the y axis of F16deep_wide (a), not the ladder -- see ROOM below
        "SRB": ("SRBB16e4", "SPSRB", "ALDSRB", "SRB", "F21srb",
                "Sionna RT room (prior SRB: Sionna RT 2.1, built-in scene box with its metal walls as shipped at 28 GHz, LoS + first-order reflections, one fixed BS, 1 m block split", "NEXT_EXPERIMENTS_ROOM16e4 §1"),
        "DMI": ("DMIB16e4", "SPDMI", "ALDDMI", "DMI", "F21dmi",
                "DeepMIMO indoor (prior DMI: DeepMIMO v4 scenario i1_2p4 at 2.4 GHz, one fixed BS, 0.5 m block split", "NEXT_EXPERIMENTS_ROOM16e4 §1"),
        "SRP": ("SRPB16e4", "SPSRP", "ALDSRP", "SRP", "F21srp",
                "Sionna RT room, moving UE (prior SRP: Sionna RT 2.1, built-in scene box with its metal walls as shipped at 28 GHz, LoS + first-order "
                "reflections, one fixed BS, one UE on a lawn-mower route, split by time with no guard band", "NEXT_EXPERIMENTS_PATH16e4 §1")}
ROOM = ("SRB", "DMI", "SRP")                                         # y by the rule of paper_f16deep (a): (Q.YLO, 1.2) while no zero-failure point and
#                                                               nothing below Q.YLO, else (Q.YLO_RULE, 1.2); zero-failure points as paper_f16deep.draw
YLADDER = (0.5, 0.3, 0.2, 0.1, 0.05, 0.02, 0.01, 0.005, 0.002, 0.001)


def main():
    D.check_styles()
    plt.rcParams.update(D.RC)
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([LEFT / W, BOTTOM / H, (W - LEFT - RIGHT) / W, (H - BOTTOM - BAND - TOP) / H])
    raws = {t: D.raw(t) for t in (TAG, SP, ALD)}
    keys = [(CELL, PRIOR, s) for s in SNRS]
    for t, d in raws.items():                                  # same grid; same trials: Perfect CSI error arrays identical
        assert sorted(k for k in d if k[:2] == (CELL, PRIOR)) == keys, (t, sorted(d))
        for key in keys:
            assert np.array_equal(raws[TAG][key][GE]["blk_err"], d[key][GE]["blk_err"], equal_nan=True), (t, key)
    tab = D.rec_rows(os.path.join(M.RV, f"pairB_{SP}.txt"), "BLER@16 failures / n per SNR -3 +0 +3 +6 +9 +12 +15 dB:")
    with open(os.path.join(M.RV, f"pairB_{SP}.txt"), encoding="utf-8") as f:   # the registered table-B labels of the 16 baselines vs V1
        lab = dict(re.findall(r"(\S+)=(\([iv]+\))", next(l for l in f.read().split("\n") if l.startswith("    M-ours-bstar=("))))
    assert set(SHOW) <= set(tab) and {a for a in SHOW if a not in (V1, GE)} <= set(lab), (sorted(tab), sorted(lab))
    cur, txt = {}, []
    for a in SHOW:
        orig = {"SPB16e4k": SP, "ALDB16e4k": ALD}.get(BY[a].orig, TAG)
        e = [np.asarray(raws[orig][key][a]["blk_err"], float)[:, -1] for key in keys]   # last iteration (R0-pilot@1 has one column)
        assert all(np.isfinite(x).all() for x in e), a
        k, n = np.array([int(x.sum()) for x in e]), np.array([len(x) for x in e])
        assert set(n.tolist()) == {N0} and k.tolist() == tab[a], (a, k.tolist(), tab[a])
        p = D.draw(ax, BY[a], SNRS, k, n, {V1: 5, D.BS: 4, GE: 3}.get(a, 2.9 - 0.05 * SHOW.index(a)))
        assert (p[np.isfinite(p)] >= YLIM[0]).all() and (p[np.isfinite(p)] <= YLIM[1]).all(), (a, p)   # a zero-failure point is NaN (the curve breaks there)
        cur[a] = k
        txt.append(f"    {a:<21}" + " ".join(f"{x}/{m}" for x, m in zip(k, n)) + f"   raw_{orig}")
    assert sorted(Q.curves(ax)) == sorted(BY[a].label for a in SHOW)   # the panel holds exactly the curves of the legend
    ax.set_yscale("log"); ax.set_ylim(*YLIM)
    if YTICKS is not None:                                         # the room pools keep the decade ticks of F16deep_wide (a)
        ax.set_yticks(YTICKS); ax.set_yticklabels([f"{y:g}" for y in YTICKS]); ax.minorticks_off()
    ax.set_xticks(SNRS); ax.set_xlim(*XLIM)
    ax.tick_params(axis="x", pad=Q.XTPAD); ax.set_xlabel("SNR [dB]", labelpad=Q.XPAD); ax.set_ylabel("BLER")
    hl = [D.proxy(BY[a]) for a in SHOW]
    leg = fig.legend(hl, [x.get_label() for x in hl], loc="center", ncol=2, frameon=False, fontsize=7,
                     bbox_to_anchor=(0.5, (H - BAND / 2) / H), handlelength=2.3, columnspacing=1.2, labelspacing=0.28,
                     borderpad=0.1, handletextpad=0.5)
    bb, small = Q.check(fig, f"{NAME}_col")                        # every artist inside the canvas; every visible text >= 7 pt
    lb = Q.inch(fig, leg.get_window_extent())
    assert lb[1] >= H - BAND and lb[3] <= H and lb[0] >= 0 and lb[2] <= W, ("legend outside its band", lb)
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(FIG, f"{NAME}_col.{ext}"), dpi=300, **({"metadata": {"CreationDate": None}} if ext == "pdf" else {}))

    below = [f"{BY[a].label} at " + ", ".join(f"{s:+.0f} dB ({x} vs {y})" for s, x, y in zip(SNRS, cur[a], cur[V1]) if x <= y)
             for a in SHOW if a not in (V1, GE) and (cur[a] <= cur[V1]).any()]
    odd = [f"{BY[a].label} {lab[a]}" for a in SHOW if a not in (V1, GE) and lab[a] != "(i)"]
    print("\n".join(
        [f"{NAME} -- {WHAT}; cell C2 = 8x4, N_train = 1.6e5) with the "
         "one legend of F16deep_wide: BLER@16 (Pilot-only LMMSE: after the first iteration), failures / trials per SNR "
         + " ".join(f"{s:+.0f}" for s in SNRS) + " dB.  Recomputed from raw by conference/figures/paper_f21dmc.py (read-only; "
         "analysis.load_raw, a raised block = a failure); no number transcribed.", "",
         f"{NAME}_col  {W} x {H} in, one panel, legend above; the {len(SHOW)} curves of paper_f16deep.SHOW with its shapes and sizes; "
         "95% Wilson bars on " + ", ".join(BY[a].label for a in D.BARS) + f".  n = {N0} (test trials 0..2559) at EVERY SNR for every "
         f"curve (no n = 20480 raw on {PRIOR}; {REG}).", "",
         "Curves (internal arm -> figure name): " + "; ".join(f"{a} -> {BY[a].label}" for a in SHOW) + ".", "", "Counts:"] + txt
        + ["", "Drawn baseline curves (Perfect CSI excluded) at or below the proposed curve (point estimates; failures vs the proposed curve's) -- reported only, nothing is "
           "tested here; the registered paired tests are in conf/results/review_next/pairB_" + SP + ".txt: " + ("; ".join(below) or "none") + ".",
           f"Registered table-B labels against the proposed prior (pairB_{SP}.txt) of the {len(SHOW) - 2} drawn baselines: "
           + ("all (i)" if not odd else "; ".join(odd) + "; the others (i)") + ".",
           "Raised blocks (analysis.load_raw NOTE lines; kept and counted as failures) in the raws read: " + ("; ".join(D.NOTES) or "none") + "."]
        + (["Zero-failure points (the curve breaks there; Perfect CSI: fighs_merge.zero_arrows): "
            + "; ".join(f"{BY[a].label} {s:+.0f} dB" for a in SHOW for s, x in zip(SNRS, cur[a]) if x == 0) + "."] if any((cur[a] == 0).any() for a in SHOW) else [])
        + [
           "", f"Asserts passed: counts = pairB_{SP}.txt 'BLER@16 failures' table (11 arms x 7 SNRs); Perfect CSI error arrays of raw_{ALD} "
           f"and raw_{SP} = raw_{TAG}'s; drawn = counted; the panel holds exactly the curves of the legend; no point outside the y range.",
           f"Layout: x ticks at the SNR points, x range {XLIM}; y log {YLIM}, ticks {YTICKS}; legend band {BAND} in above the axes, 2 columns "
           f"(inside its band: asserted, [in] {np.round(lb, 3).tolist()}); every artist inside the canvas (tight bbox [in] "
           f"{np.round(bb, 3).tolist()}); smallest visible text {small:g} pt; saved at figsize, PNG 300 dpi."]))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] != "DMC":
        TAG, SP, ALD, PRIOR, NAME, WHAT, REG = SETS[sys.argv[1]]
        d = {t: D.raw(t) for t in (TAG, SP, ALD)}                  # the y range by rule: below every point and lower Wilson bar end
        lows = []
        for a in SHOW:
            o = {"SPB16e4k": SP, "ALDB16e4k": ALD}.get(BY[a].orig, TAG)
            k = np.array([np.asarray(d[o][(CELL, PRIOR, s)][a]["blk_err"], float)[:, -1].sum() for s in SNRS])
            lows.append((D.wilson(k, np.full(len(k), N0))[0] if a in D.BARS else k / N0).min())
        if sys.argv[1] in ROOM:
            zero = any((np.array([np.asarray(d[{"SPB16e4k": SP, "ALDB16e4k": ALD}.get(BY[a].orig, TAG)][(CELL, PRIOR, s)][a]["blk_err"], float)[:, -1].sum()
                                  for s in SNRS]) == 0).any() for a in SHOW)
            pos = [x for x in lows if x > 0]
            YLIM, YTICKS = ((Q.YLO, 1.2) if not zero and min(pos) > Q.YLO else (Q.YLO_RULE, 1.2)), None
            main()
            sys.exit(0)
        YLIM = (next(y for y in YLADDER if y < min(lows)), 1.05)
        YTICKS = [y for y in (0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0) if YLIM[0] <= y and (y >= 0.2 or y in (0.001, 0.01, 0.1) or YLIM[0] >= 0.05)]
    main()
