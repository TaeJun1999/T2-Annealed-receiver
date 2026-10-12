"""conference/figures/paper_f34seed.py -- seed repeats of the proposed prior on the two Sionna RT room pools
(NEXT_EXPERIMENTS_SEEDSROOM16e4; user 2026-10-12 CDT: "그래프, 피규어 다 그리고").

  F34seed_wide.{pdf,png}   7.16 x 2.9 in, BLER vs SNR at N' = 1.6e5 (8x4), all points n = 2560 (test trials 0..2559)
      (a) Sionna RT room, random UE positions (prior SRB)      (b) Sionna RT room, moving UE (prior SRP)
  Curves: Proposed with the diffusion checkpoint of seed 1 (the evaluated a1; with its 95% Wilson bars), seed 2, seed 3 (same
  recipe, budget, GMM, trials; only the network's initialisation and batch order differ), GMM prior, Perfect CSI.

Counts are read from the raws (raw_<P>B16e4, raw_<P>B16e4s2, raw_<P>B16e4s3; analysis.load_raw, a raised block = a failure).
Asserted: GMM prior and Perfect CSI have the same failure counts in the three raws of a pool (they are bit-identical arms by the
registration's acceptance); the -3/0/+3 dB counts of every seed = results/review_next/recovery_<TAG>.txt; drawn = counted.
A zero-failure point breaks its curve (Perfect CSI: the fighs_merge.zero_arrows arrow).  REPORT-ONLY drawing of registered runs.
Run:  cd ~/t2/conf && CUDA_VISIBLE_DEVICES= ~/miniforge3/envs/torch/bin/python -B ~/t2/conference/figures/paper_f34seed.py \\
          > ~/t2/conference/figures/records/paper_f34seed.txt
"""
import os
import re
import sys

sys.dont_write_bytecode = True
import paper_f16deep as D
import matplotlib.pyplot as plt
import numpy as np
from paper_f16deep import BS, BY, FIG, GE, M, N0, Q, S, SNRS, V1

PANELS = (("SRB", "Sionna RT room, random UE positions"), ("SRP", "Sionna RT room, moving UE"))
NAME, CELL = "F34seed_wide", "C2"
W, H = 7.16, 2.9
LEFT, RIGHT, BOTTOM, BAND, TOP, HGAP = 0.50, 0.05, 0.36, 0.26, 0.03, 0.10   # in; BAND = the legend band above the axes
LAB_XY = (0.04, 0.035)
SEED23 = (("^", "--"), ("v", ":"))                             # marker, line style of seeds 2 and 3 (hollow, thin; seed 1 = the paper's curve)
RV = os.path.join(M.CONF, "results", "review_next")


def fails(raw, prior, arm):
    return np.array([int(np.where(np.isfinite(e := np.asarray(raw[(CELL, prior, s)][arm]["blk_err"], float)[:, -1]), e, 1.0).sum()) for s in SNRS])


def main():
    C, txt = {}, []
    for prior, _ in PANELS:
        tags = [f"{prior}B16e4", f"{prior}B16e4s2", f"{prior}B16e4s3"]
        raws = [D.raw(t) for t in tags]
        v = [fails(r, prior, V1) for r in raws]
        b, g = fails(raws[0], prior, BS), fails(raws[0], prior, GE)
        for r, t, x in zip(raws, tags, v):
            assert np.array_equal(fails(r, prior, BS), b) and np.array_equal(fails(r, prior, GE), g), t   # the same GMM / Perfect CSI in every seed raw
            with open(os.path.join(RV, f"recovery_{t}.txt"), encoding="utf-8") as f:
                rec = {m[0]: (int(m[1]), int(m[2]), int(m[3])) for m in re.findall(r"([+-]\d+) dB\s+b\* (\d+)\s+V1 (\d+)\s+genie (\d+)\s+n=2560", f.read().split("# recovery")[-1])}
            for i, s in enumerate(("-3", "+0", "+3")):
                assert rec[s] == (int(b[i]), int(x[i]), int(g[i])), (t, s, rec[s], b[i], x[i], g[i])
        C[prior] = (v, b, g)
        txt += [f"  {prior}:"] + [f"    Proposed, seed {i + 1} (raw_{t}): " + " ".join(f"{k}/{N0}" for k in x) for i, (t, x) in enumerate(zip(tags, v))] \
            + ["    GMM prior:            " + " ".join(f"{k}/{N0}" for k in b), "    Perfect CSI:          " + " ".join(f"{k}/{N0}" for k in g)]
    n = np.full(len(SNRS), N0)
    allk = [k for v, b, g in C.values() for k in (*v, b, g)]
    zero = any((k == 0).any() for k in allk)
    ylim = (Q.YLO, 1.2) if not zero and min(float((k / N0)[k > 0].min()) for k in allk) > Q.YLO else (Q.YLO_RULE, 1.2)

    D.check_styles()
    plt.rcParams.update(D.RC)
    fig = plt.figure(figsize=(W, H))
    w, h = (W - LEFT - RIGHT - HGAP) / 2, H - BOTTOM - BAND - TOP
    axs = [fig.add_axes([LEFT / W, BOTTOM / H, w / W, h / H])]
    axs.append(fig.add_axes([(LEFT + w + HGAP) / W, BOTTOM / H, w / W, h / H], sharex=axs[0], sharey=axs[0]))
    c1 = BY[V1]._replace(label="Proposed, seed 1")
    for ax, (prior, _) in zip(axs, PANELS):
        v, b, g = C[prior]
        D.draw(ax, BY[GE], SNRS, g, n, 3)
        D.draw(ax, BY[BS], SNRS, b, n, 4)
        for i, (mk, ls) in enumerate(SEED23):
            k = v[i + 1]
            p = np.where(k > 0, k / N0, np.nan)
            ax.plot(SNRS, p, color=c1.color, marker=mk, ls=ls, mfc="white", lw=D.THIN["lw"], ms=D.THIN["ms"], label=f"Proposed, seed {i + 2}", zorder=4.5)
            d = Q.curves(ax)[f"Proposed, seed {i + 2}"]
            assert Q.same(d["x"], SNRS) and Q.same(d["y"], p), (prior, i)
        D.draw(ax, c1, SNRS, v[0], n, 5)
    for i, ax in enumerate(axs):
        ax.set_yscale("log"); ax.set_ylim(*ylim); ax.set_xticks(SNRS); ax.set_xlim(-4, 16)
        ax.tick_params(axis="x", pad=Q.XTPAD); ax.tick_params(axis="y", labelleft=i == 0)
        ax.set_xlabel("SNR [dB]", labelpad=Q.XPAD)
        if i == 0:
            ax.set_ylabel("BLER")
        ax.text(*LAB_XY, f"({'ab'[i]})", transform=ax.transAxes, ha="left", va="bottom", fontsize=D.LAB_PT, fontweight="bold", color=S.INK, zorder=7)
    hd, lb = axs[0].get_legend_handles_labels()
    order = ["Proposed, seed 1", "Proposed, seed 2", "Proposed, seed 3", BY[BS].label, BY[GE].label]
    leg = fig.legend([hd[lb.index(x)] for x in order], order, loc="center", ncol=5, frameon=False, fontsize=7,
                     bbox_to_anchor=(0.5, (H - BAND / 2) / H), handlelength=2.3, columnspacing=1.6, borderpad=0.1, handletextpad=0.5)
    bb, small = Q.check(fig, NAME)
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(FIG, f"{NAME}.{ext}"), dpi=300, **({"metadata": {"CreationDate": None}} if ext == "pdf" else {}))
    print("\n".join(
        [f"{NAME} -- seed repeats of the proposed prior on the two Sionna RT room pools (NEXT_EXPERIMENTS_SEEDSROOM16e4): BLER@16, failures / trials per "
         "SNR " + " ".join(f"{s:+.0f}" for s in SNRS) + f" dB, every point n = {N0} (test trials 0..2559; the same trials for every seed).  (a) prior SRB, "
         "(b) prior SRP.  Seed 1 = the evaluated checkpoint a1 of ROOM16e4 / PATH16e4; seeds 2, 3 = attempts 2, 3 of the same recipe (only initialisation and "
         "batch order differ).  Produced by conference/figures/paper_f34seed.py; no number transcribed.  The registered seed labels are in the registration §6.", "",
         "Caveat: in (b) the GMM prior is the seed initialisation selected when EM collapsed (NEXT_EXPERIMENTS_PATH16e4 §5 / 6.1), not a well-fitted GMM.", "",
         "Counts:"] + txt
        + ["", "Asserts passed: GMM prior and Perfect CSI counts identical in the three raws of each pool; -3/0/+3 dB counts = recovery_<TAG>.txt; drawn = counted.",
           f"Layout: {W} x {H} in, two panels sharing x and y; x range (-4, 16); y log {ylim}; 95% Wilson bars on seed 1, GMM prior, Perfect CSI; a zero-failure "
           f"point breaks its curve (Perfect CSI: arrow from the 95% Wilson upper bound of 0/{N0}); every artist inside the canvas (tight bbox [in] "
           f"{np.round(bb, 3).tolist()}); smallest visible text {small:g} pt; PNG 300 dpi."]))


if __name__ == "__main__":
    main()
