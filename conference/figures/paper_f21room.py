"""conference/figures/paper_f21room.py -- the two Sionna RT room pools side by side with the ONE legend of F16deep_wide
(user 2026-10-12 CDT: both Sionna results go to the paper -- "일단 두개 다 푸시하자", "그래프, 피규어 다 그리고").

  F21room_wide.{pdf,png}     7.16 x 3.25 in, BLER vs SNR at N' = 1.6e5 (8x4), one legend above the two panels
      (a) Sionna RT room, random UE positions (prior SRB)      (b) Sionna RT room, moving UE (prior SRP)
  F21room12_wide.{pdf,png}   `paper_f21room.py 12`: the same DRAWN up to +12 dB (the paper variant; user decision 2026-10-12 CDT,
                             conf/DECISIONS.md -- the +15 dB counts stay in the record and in F21room_wide)

Nothing new is counted here: every panel is the single-panel figure of paper_f21dmc.py <PRIOR> hsx -- the same raws through the
same paper_f21dmc.merged() (-3/0/+3 dB: the original test trials, n = 2560, the registered judgement; +6/+9 dB: raw_FH<tag>,
n = 20480; +12/+15 dB: raw_FX<tag>, n = 81920; one point = one raw, each count asserted against its count table) -- and the merged
counts are asserted against the 'Counts:' block of records/paper_f21{srb,srp}hsx.txt.  Curves, shapes, sizes, Wilson bars and the
zero-failure handling are paper_f16deep's (draw / proxy).  The two axes share x and y; the y range is the three-tier rule of
NEXT_EXPERIMENTS_FIGHSX16e4 §1 applied to the drawn values of BOTH panels.  REPORT-ONLY (no test, no label).
Run (CPU, about a minute):
  cd ~/t2/conf && CUDA_VISIBLE_DEVICES= ~/miniforge3/envs/torch/bin/python -B ~/t2/conference/figures/paper_f21room.py [12] \\
      > ~/t2/conference/figures/records/paper_f21room[12].txt
"""
import os
import sys

sys.dont_write_bytecode = True                                 # no __pycache__ next to the paper_f*.py or in conf/code
import paper_f16deep as D
import paper_f21dmc as F                                       # SETS (raws per prior) and merged() (the hsx merge)
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from paper_f16deep import BY, FIG, GE, N0, Q, S, SHOW, SNRS, V1

PANELS = (("SRB", "Sionna RT room, random UE positions"), ("SRP", "Sionna RT room, moving UE"))
X12 = len(sys.argv) > 1 and sys.argv[1] == "12"
NAME = "F21room12_wide" if X12 else "F21room_wide"
W, H = 7.16, 3.25
LEFT, RIGHT, BOTTOM, BAND, TOP, HGAP = 0.50, 0.05, 0.36, 0.58, 0.03, 0.10   # in; BAND = the legend band (as F16deep_wide / F21sel_wide)
LAB_XY = (0.04, 0.035)                                         # panel label: axes fraction of its lower-left corner


def counts(prior):
    """{arm: (k, n, merge record line)} of one pool = the drawn counts of `paper_f21dmc.py <prior> hsx`, checked against its record"""
    F.TAG, F.SP, F.ALD, F.PRIOR, F.NAME, F.WHAT, F.REG = F.SETS[prior]
    F.HS = F.HSX = True
    raws = {t: D.raw(t) for t in (F.TAG, F.SP, F.ALD)}
    with open(os.path.join(D.HERE, "records", f"paper_f21{prior.lower()}hsx.txt"), encoding="utf-8") as f:
        rec = {l.split()[0]: [tuple(int(v) for v in x.split("/")) for x in l.split()[1:8]]
               for l in f.read().split("Counts:")[1].split("\n\n")[0].split("\n") if l.split() and l.split()[0] in SHOW}
    out = {}
    for a in SHOW:
        orig = {"SPB16e4k": F.SP, "ALDB16e4k": F.ALD}.get(BY[a].orig, F.TAG)
        k = np.array([int(np.asarray(raws[orig][(F.CELL, prior, s)][a]["blk_err"], float)[:, -1].sum()) for s in SNRS])
        k, n, line = F.merged(k, orig, a)
        assert list(zip(k.tolist(), n.tolist())) == rec[a], (prior, a, k, n, rec[a])   # = the audited single-panel figure
        assert n.tolist() == [N0] * 3 + [20480] * 2 + [81920] * 2, (prior, a, n)
        out[a] = (k, n, line)
    return out


def main():
    sl = slice(None, -1) if X12 else slice(None)               # the drawn SNR points
    C = {p: counts(p) for p, _ in PANELS}
    # the y range: NEXT_EXPERIMENTS_FIGHSX16e4 §1 (three tiers) on the drawn values of both panels
    kn = [(a, k[sl], n[sl]) for c in C.values() for a, (k, n, _) in c.items()]
    zero = any((k == 0).any() for _, k, n in kn)
    ends = [float(x) for a, k, n in kn for x in ((D.wilson(k, n)[0] if a in D.BARS else k / n)[k > 0])]
    ylim = (Q.YLO, 1.2) if not zero and min(ends) > Q.YLO else (Q.YLO_RULE, 1.2)
    if ylim[0] == Q.YLO_RULE and min([float(x) for _, k, n in kn for x in (k / n)[k > 0]]
                                     + [1.96 ** 2 / (m + 1.96 ** 2) / 1.7 for a, k, n in kn if a == GE for m in n[k == 0]]) < Q.YLO_RULE:
        ylim = (Q.YLO_RULE / 4, 1.2)
    xlim = (-4, SNRS[-2] + 1) if X12 else (-4, 16)

    D.check_styles()
    plt.rcParams.update(D.RC)
    fig = plt.figure(figsize=(W, H))
    w, h = (W - LEFT - RIGHT - HGAP) / 2, H - BOTTOM - BAND - TOP
    axs = []
    for i in range(2):
        axs.append(fig.add_axes([(LEFT + i * (w + HGAP)) / W, BOTTOM / H, w / W, h / H],
                                sharex=axs[0] if axs else None, sharey=axs[0] if axs else None))
    txt, mrg, zero_all, below_all = [], [], [], []
    for ax, (prior, title) in zip(axs, PANELS):
        txt.append(f"  ({'ab'[axs.index(ax)]}) {title} (prior {prior}):")
        for a in SHOW:
            k, n, line = C[prior][a]
            p = D.draw(ax, BY[a], SNRS[sl], k[sl], n[sl], {V1: 5, D.BS: 4, GE: 3}.get(a, 2.9 - 0.05 * SHOW.index(a)))
            assert (p[np.isfinite(p)] >= ylim[0]).all() and (p[np.isfinite(p)] <= ylim[1]).all(), (prior, a, p)
            txt.append(f"    {a:<21}" + " ".join(f"{x}/{m}" for x, m in zip(k, n)))
            mrg.append(f"  {prior} " + line.strip())
            zero_all += [f"({'ab'[axs.index(ax)]}) {BY[a].label} {s:+.0f} dB (0/{m})" for s, x, m in zip(SNRS[sl], k[sl], n[sl]) if x == 0]
        assert sorted(Q.curves(ax)) == sorted(BY[a].label for a in SHOW), prior   # the panel holds exactly the curves of the legend
        vk, vn = (v[sl] for v in C[prior][V1][:2])
        below = [f"{BY[a].label} at " + ", ".join(f"{s:+.0f} dB ({x}/{m} vs {y}/{z})" for s, x, m, y, z in zip(SNRS[sl], C[prior][a][0][sl], C[prior][a][1][sl], vk, vn) if x * z <= y * m)
                 for a in SHOW if a not in (V1, GE) and (C[prior][a][0][sl] * vn <= vk * C[prior][a][1][sl]).any()]
        below_all.append(f"  ({'ab'[axs.index(ax)]}) " + ("; ".join(below) or "none"))
    for i, ax in enumerate(axs):
        ax.set_yscale("log"); ax.set_ylim(*ylim); ax.set_xticks(SNRS[sl]); ax.set_xlim(*xlim)
        ax.tick_params(axis="x", pad=Q.XTPAD); ax.tick_params(axis="y", labelleft=i == 0)
        ax.set_xlabel("SNR [dB]", labelpad=Q.XPAD)
        if i == 0:
            ax.set_ylabel("BLER")
    assert axs[0].get_shared_x_axes().joined(*axs) and axs[0].get_shared_y_axes().joined(*axs)   # the two axes share x and y
    for ax, t in zip(axs, "ab"):
        ax.text(*LAB_XY, f"({t})", transform=ax.transAxes, ha="left", va="bottom", fontsize=D.LAB_PT, fontweight="bold", color=S.INK, zorder=7)
    hl = [D.proxy(BY[a]) for a in SHOW]
    hl.insert(D.LEG_GAP, Line2D([], [], ls="none", label=""))      # the legend of F16deep_wide: three columns = the families
    leg = fig.legend(hl, [x.get_label() for x in hl], loc="center", ncol=3, frameon=False, fontsize=7,
                     bbox_to_anchor=(0.5, (H - BAND / 2) / H), handlelength=2.3, columnspacing=2.2, labelspacing=0.28,
                     borderpad=0.1, handletextpad=0.5)
    bb, small = Q.check(fig, NAME)                                 # every artist inside the canvas; every visible text >= 7 pt
    lb = Q.inch(fig, leg.get_window_extent())
    assert lb[1] >= H - BAND and lb[3] <= H and lb[0] >= 0 and lb[2] <= W, ("legend outside its band", lb)
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(FIG, f"{NAME}.{ext}"), dpi=300, **({"metadata": {"CreationDate": None}} if ext == "pdf" else {}))

    print("\n".join(
        [f"{NAME} -- the two Sionna RT room pools (Sionna RT 2.1, built-in scene box with its metal walls as shipped at 28 GHz, LoS + first-order "
         "reflections, ONE fixed BS; cell C2 = 8x4, N_train = 1.6e5) with the one legend of F16deep_wide: BLER@16 (Pilot-only LMMSE: after the "
         "first iteration), failures / trials per SNR " + " ".join(f"{s:+.0f}" for s in SNRS) + " dB.  (a) prior SRB: random UE positions, 1 m block "
         "split; (b) prior SRP: one UE on a lawn-mower route, split by time with no guard band.  Produced by conference/figures/paper_f21room.py "
         "from the same raws and the same merge as paper_f21dmc.py <PRIOR> hsx; no number transcribed.  REPORT-ONLY.", "",
         f"{NAME}  {W} x {H} in, two panels sharing x and y, legend above; the {len(SHOW)} curves of paper_f16deep.SHOW; 95% Wilson bars on "
         + ", ".join(BY[a].label for a in D.BARS) + f".  n = {N0} (test trials 0..2559) at -3/0/+3 dB, n = 20480 (new trials 10000..30479) at "
         "+6/+9 dB, n = 81920 (new trials 10000..91919) at +12/+15 dB for every curve (NEXT_EXPERIMENTS_FIGHSROOM16e4 / _FIGHSPATH16e4 / "
         "_FIGHSX16e4; the n = 81920 point contains the 20480 trials of the earlier n = 20480 point -- not independent of it).", ""]
        + ([f"DRAWN RANGE: {SNRS[0]:+.0f} .. {SNRS[-2]:+.0f} dB only (paper variant; user decision 2026-10-12 CDT, taken after the SRB +15 dB result was seen; the "
            f"user asked for both ranges of both pools on 2026-10-12 CDT -- conf/DECISIONS.md).  The {SNRS[-1]:+.0f} dB point of every curve was measured (last entry of "
            "each row below) and is NOT drawn here; the full-range figure is F21room_wide.  The 'at or below' and 'Zero-failure' lines refer to the drawn points.", ""]
           if X12 else [])
        + ["Caveat (NEXT_EXPERIMENTS_PATH16e4 §5 / 6.1): in panel (b) the 'GMM prior' curve is the b* the registered rule selected after EM collapsed -- the seed "
           "initialisation, not a well-fitted GMM; the caption must say so.  Panel (a)'s GMM prior is the converged full-covariance K = 1024 fit.", "",
           "Curves (internal arm -> figure name): " + "; ".join(f"{a} -> {BY[a].label}" for a in SHOW) + ".", "", "Counts:"] + txt
        + ["", "Merge sources and 'rising' cells (one-sided Fisher p; reported, no smoothing, no dropped point):"] + mrg
        + ["", "Drawn baseline curves (Perfect CSI excluded) at or below the proposed curve (point estimates; nothing is tested here -- the registered "
           "paired tests are in conf/results/review_next/pairB_SP{SRB,SRP}.txt, judged on the n = 2560 raws):"] + below_all
        + ["", "Zero-failure points (the curve breaks there; Perfect CSI: fighs_merge.zero_arrows): " + ("; ".join(zero_all) or "none") + ".", "",
           "Asserts passed: merged counts = the 'Counts:' block of records/paper_f21{srb,srp}hsx.txt (11 arms x 7 SNRs per pool; those are asserted against "
           "the count tables and pairB tables by paper_f21dmc.py); n per point = 2560 / 20480 / 81920; drawn = counted (points and bar ends read back); "
           "each panel holds exactly the curves of the legend; the two axes share x and y; no point outside the y range.",
           f"Layout: x ticks at the SNR points, x range {xlim}; y log {ylim} (FIGHSX16e4 §1 rule on the drawn values of both panels); legend band {BAND} in "
           f"above the axes, 3 columns (inside its band: asserted, [in] {np.round(lb, 3).tolist()}); every artist inside the canvas (tight bbox [in] "
           f"{np.round(bb, 3).tolist()}); smallest visible text {small:g} pt; saved at figsize, PNG 300 dpi."]))


if __name__ == "__main__":
    main()
