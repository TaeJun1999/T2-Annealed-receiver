"""conf/code/figures_stagec2.py -- Stage C figures F12-F13 (the 2026-09-22 amendments), print-size.

figures_stagec.py draws F7-F11.  This file continues with the two results whose data is FINAL.
Second revision (14:55 KST) after an independent three-lens verification (wf_49dc79b9-4cf) confirmed
that every plotted number was right and that the CAPTIONS and ANNOTATIONS were not.  The 38 confirmed
items are addressed below and named in the captions where they change a reading.

  F12  the Tp operating envelope (10_SPEC_stageC §6f).  Equal-budget N=1e4, n=2560, three cells.
       Top: BLER vs SNR for C1 (Tp=2) / C5 (Tp=3) / C2 (Tp=4).  Bottom: the pre-registered decision-
       point sign test per cell as a margin over DISCORDANT pairs, with the cavity-variance quantities
       on a real right-hand nu_q axis: the closed-form iteration-1 floor cbar(Nt-Tp)/Tp (all three
       INSIDE the frozen grid), the MEASURED iteration-1 nu_q at -3 dB where it exists, and the grid
       top.  Only the measured C1 value leaves the grid.
  F13  sign versus magnitude (10_SPEC_stageC §6h).  The do() counterfactual sweep, all 7 SNRs, n=256,
       with Clopper-Pearson 95% intervals, censored zeros drawn on a resolution line, and the two
       GMM-side interventions (flip4 / tiny4) that isolate sign from magnitude cleanly.

Every number is READ from the files below.  Nothing here recomputes, resamples or re-runs anything.
  raw_B1e4x/*.npz                                F12 top (C1, C5)   equal budget N=1e4, n=2560
  raw_B1e4/*.npz                                 F12 top (C2), F13 V1 reference; same budget, same n
  results/tables_D2_B1e4x.txt, tables_D2_B1e4.txt   F12 bottom (pre-registered sign tests, verbatim)
  results/sigma_grid_D2.txt                      F12 bottom (measured it-1 nu_q, 2026-09-20, n=64; grid top)
  results/jacpsd_counterfactual_SUMMARY_n256.txt F13 (§6h roll-up)

Print size: authored at 7.16 in (IEEE two-column text width) so authored point sizes ARE printed
point sizes; nothing below 6.0 pt.

GATE STATUS -- both figures are built on ckpt/d2sx_N10000_a1.pt.  The tables record NO GATE RECORD for
that checkpoint on D2 (gates are measurable on D1 only); its D1 sibling at the same N_train FAILS GC
(0.243 vs 0.15, results/samplecx_D1.txt).  §6d registered these points as a BUDGET-AXIS measurement, not
an arm result.  The gate-passing model's numbers live in results/tables_D2_C.txt.
"""
import os
import re
import sys
import glob
import collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from scipy.stats import beta as _beta
import common as C
import figures as F0
from figures_stagec import _save, RES

FIG = F0.FIG
SNRS = np.array([-3., 0., 3., 6., 9., 12., 15.])
GRID_TOP_SIGMA = 0.8451555                     # results/sigma_grid_D2.txt CHOSEN GRID k=19, FROZEN
GRID_TOP_NU = 2 * GRID_TOP_SIGMA ** 2          # nu_q = 2 sigma_t^2   (the file's own convention line)
# measured iteration-1 nu_q at -3 dB, results/sigma_grid_D2.txt lines 22 / 29 (2026-09-20, n=64).
# C5 was NOT in that measurement; its value below is the §6j closed form and is drawn hollow.
MEASURED_NU_M3 = {2: 1.997, 4: 0.4988}
CLOSED_NU_M3 = {3: 0.998}
GATE_LINE = ("checkpoint ckpt/d2sx_N10000_a1.pt: the table records NO GATE RECORD for it on D2 "
             "(GA-GD are measurable on D1 only); its D1 sibling at N_train=1e4 FAILS GC 0.243 vs 0.15.")
GATE_LINE_PASS = ("checkpoint ckpt/d2sx_N160000_a1.pt: gates are measurable on D1 only, so this D2 checkpoint "
                  "is qualified through its D1 sibling sx_N160000_D1.pt, which PASSES GB 2.66e-3 / GC 0.0999 / "
                  "GD 0.0718 (LADDER_C.md:1); GA is a structural zero for this model family.")

ST = {   # arm -> (legend label incl. condition, colour, marker, linestyle)
    "R1-turbo":            ("classical turbo (no channel prior)",       "tab:brown",  "s", "--"),
    "M-ours-bstar":        ("fitted GMM prior, b* by val. log-lik.",    "tab:red",    "D", "-"),
    "M-ours-dscore-C-V1":  ("learned score, PSD-projected site (V1)",   "tab:green",  "o", "-"),
    "M-ours-dscore-C-V0":  ("learned score, pre-registered site (V0)",  "tab:purple", "v", ":"),
    "R5-genie":            ("genie CSI (lower bound)",                  "k",          "*", "-."),
}
CELLS = [("C1", 2, "raw_B16e4", 50), ("C5", 3, "raw_B16e4", 46), ("C2", 4, "raw_B16e4", 42)]
TBL_F12 = "tables_D2_B16e4.txt"


# ------------------------------------------------------------------ readers ---------------------

def bler_from_raw(rawdir, cell):
    """mean BLER@16 per SNR, with the pre-registered analysis rule (code/analysis.py:172-175): a block on
    which the arm RAISED carries a non-finite blk_err and is counted as a block error, never dropped."""
    acc = collections.defaultdict(lambda: collections.defaultdict(list))
    fails = collections.defaultdict(lambda: collections.defaultdict(int))
    for f in glob.glob(os.path.join(C.CONF, rawdir, f"D2_{cell}_*.npz")):
        snr = float(re.search(r"snr(-?\d+)", f).group(1))
        d = np.load(f, allow_pickle=True)
        for k in d.files:
            if k.endswith("|blk_err"):
                v = d[k][:, 15]
                acc[k.split("|")[0]][snr].append(np.where(np.isfinite(v), v, 1.0))
                fails[k.split("|")[0]][snr] += int((~np.isfinite(v)).sum())
    out, nf = {}, {}
    for arm, per in acc.items():
        out[arm] = np.array([np.concatenate(per[s]).mean() if s in per else np.nan for s in SNRS])
        nf[arm] = np.array([fails[arm][s] for s in SNRS])
    return out, nf


def pooled_test(path, cell, pair="M-ours-bstar -> M-ours-dscore-C-V1"):
    """The pre-registered pooled sign test for one pair, straight out of a tables_*.txt TABLE B block.
    The block is cut at the NEXT pair line (not a fixed width -- a fixed window overran into the next
    pair's verdict, which happened to be harmless; verification item 30)."""
    txt = open(path, encoding="utf-8", errors="replace").read()
    cut = txt.split(f"--- cell {cell} ")
    if len(cut) < 2:
        return None
    blk = cut[-1]
    i = blk.find("  " + pair)
    if i < 0:
        return None
    seg = re.split(r"\n  (?=[A-Z])", blk[i:], maxsplit=1)[0]
    m = re.search(r"pooled (\d+):(\d+) p=([0-9.e+-]+)", seg)
    if not m:
        return None
    ver = re.search(r"-> (not significant|significant)", seg)
    counts = dict((w, int(k)) for w, k in re.findall(r"(first|second) arm fewer failures at (\d)/3", seg))
    who = max(counts, key=counts.get) if counts else "?"
    dsn = re.search(r"decision SNRs \[([^\]]*)\]", seg)
    per = [(float(s), int(a), int(b), float(p)) for s, a, b, p in
           re.findall(r"([+-]?\d+) dB (\d+):(\d+) p=([0-9.e+-]+)", seg)]
    return dict(a=int(m.group(1)), b=int(m.group(2)), p=float(m.group(3)),
                who=who, k=(counts.get(who, 0) if counts else 0),
                sig=(ver.group(1) == "significant") if ver else None,
                snrs=(dsn.group(1).replace("'", "") if dsn else "?"), per=per)


def cp95(k, n):
    """Clopper-Pearson 95% interval for k of n."""
    lo = 0.0 if k == 0 else _beta.ppf(0.025, k, n - k + 1)
    hi = 1.0 if k == n else _beta.ppf(0.975, k + 1, n - k)
    return lo, hi


# ------------------------------------------------------------------ F12  the Tp envelope ----------

def fig12():
    plt.rcParams.update({"font.size": 7.5, "axes.labelsize": 7.5, "axes.titlesize": 8,
                         "xtick.labelsize": 6.8, "ytick.labelsize": 6.8, "legend.fontsize": 6.8})
    fig = plt.figure(figsize=(7.16, 6.2))
    gs = GridSpec(2, 3, figure=fig, height_ratios=[1.0, 1.08], hspace=0.40, wspace=0.14,
                  left=0.085, right=0.985, top=0.955, bottom=0.145)
    top = [fig.add_subplot(gs[0, j]) for j in range(3)]
    RESL = 1.0 / 2560.0
    handles = {}
    for (cell, tp, rawdir, K), ax in zip(CELLS, top):
        b, nf = bler_from_raw(rawdir, cell)
        for arm, (lab, col, mk, ls) in ST.items():
            if arm not in b:
                continue
            y = b[arm]
            z = y <= 0
            h, = ax.semilogy(SNRS, np.maximum(y, 0.5 * RESL), ls, color=col, marker=mk, ms=3.6,
                             lw=1.2, label=lab)
            handles[arm] = h
            if z.any():                                 # 0 of 2560: censored, drawn hollow ON the line
                ax.plot(SNRS[z], np.full(z.sum(), 0.5 * RESL), marker=mk, ms=5.0, ls="none",
                        mfc="white", mec=col, mew=1.1, zorder=5)
        ax.axhline(0.5 * RESL, color="0.45", lw=0.7, ls=(0, (4, 3)))
        ax.set_title(f"{cell}   $T_p$ = {tp}   (K = {K} info bits)")
        ax.set_xlabel("SNR (dB)")
        ax.set_xlim(-4.5, 16.5)
        ax.set_ylim(0.3 * RESL, 1.6)
        ax.grid(alpha=0.25, which="both", lw=0.4)
        if cell == "C1":
            ax.set_ylabel("BLER after 16 outer iterations")
            v0, v1 = nf["M-ours-dscore-C-V0"][0], nf["M-ours-dscore-C-V1"][0]
            b0, b1 = b["M-ours-dscore-C-V0"][0], b["M-ours-dscore-C-V1"][0]
            ax.text(0.97, 0.72, f"-3 dB: V0 {b0:.3f}, V1 {b1:.3f}\n({v0} / {v1} of 2560 blocks raised;\n"
                                f"counted as block errors)", transform=ax.transAxes, fontsize=6.3,
                    color="0.25", va="top", ha="right")
            ax.text(0.03, 0.055, "hollow on dashed line = 0 of 2560", transform=ax.transAxes,
                    fontsize=6.0, color="0.35", va="bottom", ha="left")
        else:
            ax.set_yticklabels([])

    # ---- bottom-left: the pre-registered sign tests, margin over discordant pairs, + nu_q twin axis
    ax = fig.add_subplot(gs[1, 0:2])
    res = {c: pooled_test(os.path.join(RES, TBL_F12), c) for c in ("C1", "C5", "C2")}
    floor = {tp: (4 - tp) / tp for _, tp, _, _ in CELLS}          # cbar (Nt - Tp) / Tp, Nt = 4, cbar = 1
    for cell, tp, _, _ in CELLS:
        r = res[cell]
        if r is None:
            continue
        frac = (r["a"] - r["b"]) / (r["a"] + r["b"])            # a:b = only-first-fails : only-second-fails
        # pair is bstar -> V1, so a > b means V1 wins.  A bar the 3-point rule calls NOT significant is
        # a tie and is drawn grey: colouring it as a win for either arm would assert what the test denies.
        col = "0.55" if r["sig"] is False else ("tab:green" if frac > 0 else "tab:red")
        ax.bar(tp, frac, width=0.42, color=col, alpha=0.85, zorder=3)
        winner = ("neither (TIE by the 3-point rule)" if r["sig"] is False
                  else ("V1" if r["who"] == "second" else "GMM"))
        rev = [(s, a, b_, p) for s, a, b_, p in r["per"] if (a - b_) * frac < 0]
        # Keep the in-figure label to what a reader needs at a glance; the decision SNRs, the
        # reversal and the per-SNR counts are in the caption, which is the file of record.
        short = winner if winner in ("V1", "GMM") else "TIE"
        txt = f"{r['a']}:{r['b']},  p = {r['p']:.1e}\n{r['k']}/3 to {short}"
        ax.text(tp, frac + (0.05 if frac > 0 else -0.05), txt, ha="center",
                va="bottom" if frac > 0 else "top", fontsize=6.2, linespacing=1.35)
    ax.axhline(0, color="0.35", lw=0.9)
    ax.set_xticks([2, 3, 4])
    ax.set_xlim(1.30, 4.70)
    ax.set_ylim(-0.50, 1.45)
    ax.set_xlabel("$T_p$ (pilot symbols; $N_t$ = 4)")
    ax.set_ylabel("sign-test margin among discordant pairs\n(a$-$b)/(a+b);  + = V1 wins, $-$ = GMM wins",
                  fontsize=7)
    ax.set_title("pre-registered decision-point test (left axis)  vs  cavity variance $\\nu_q$ (right axis)")
    ax.grid(alpha=0.25, axis="y", lw=0.4)
    ax.text(0.5, -0.19, "decision SNRs (anchor rule): C1 and C5 at +6/+12/+15 dB, C2 at $-$3/+0/+3 dB;  C5 reverses at +6 dB (232:156, p = 1.3e-04)",
            transform=ax.transAxes, ha="center", va="top", fontsize=6.0, color="0.3")
    ax2 = ax.twinx()
    tps = np.array([2, 3, 4])
    ax2.plot(tps, [floor[t] for t in tps], color="tab:blue", marker="s", ms=4.2, lw=1.1, ls="--",
             label=r"closed-form floor $\bar c\,(N_t-T_p)/T_p$ (§6j)")
    ax2.plot([2, 4], [MEASURED_NU_M3[2], MEASURED_NU_M3[4]], color="tab:blue", marker="o", ms=4.6,
             ls="none", label="measured, $-$3 dB, it. 1 (sigma_grid_D2.txt, n=64)")
    ax2.plot([3], [CLOSED_NU_M3[3]], color="tab:blue", marker="o", ms=4.6, ls="none", mfc="white",
             mew=1.1, label="closed form, $-$3 dB, NOT measured (C5)")
    ax2.axhline(GRID_TOP_NU, color="tab:blue", lw=0.8, ls=":",
                label=f"frozen grid top, $\\nu_q$ = {GRID_TOP_NU:.2f}")
    ax2.set_ylim(-0.12, 2.45)
    ax2.set_ylabel("$\\nu_q$ (it. 1)", color="tab:blue", fontsize=7)
    ax2.tick_params(axis="y", colors="tab:blue", labelsize=6.8)
    ax2.text(1.42, 2.42, "all closed-form floors are INSIDE the grid; measured C1 $-$3 dB $\\nu_q$ = 2.00\n"
                         "= 1.40 x grid top.  Leaving the grid is NOT sufficient, though: C2 at $-$9 dB\n"
                         "has the same $\\nu_q$ = 1.99 and does not collapse (§6p)",
             fontsize=5.8, color="tab:blue", va="top", ha="left", linespacing=1.3)
    h2, l2 = ax2.get_legend_handles_labels()

    # ---- bottom-right: the legend of the top row, as its own panel
    axl = fig.add_subplot(gs[1, 2])
    axl.axis("off")
    lg1 = axl.legend([handles[a] for a in ST if a in handles], [ST[a][0] for a in ST if a in handles],
                     loc="upper left", fontsize=6.6, framealpha=0.95, bbox_to_anchor=(-0.02, 1.02),
                     title="top row", title_fontsize=6.6)
    axl.add_artist(lg1)
    axl.legend(h2, l2, loc="lower left", fontsize=5.9, framealpha=0.95, bbox_to_anchor=(-0.02, -0.05),
               title="bottom-left, blue (right axis)", title_fontsize=6.0, handlelength=1.6)

    fig.text(0.5, 0.058, "EQUAL BUDGET: every arm, learned and classical, is fitted / trained on the SAME "
                         "N_train = 1.6e5 channel set (10_SPEC_stageC A3).  n = 2560 trials per SNR point.  "
                         "GMM b* = kron K=512, by validation log-likelihood over all 12 configurations "
                         "of the K <= 512 grid; the extended K=1024 grid moves b* (F15c).",
             ha="center", fontsize=6.8, color="0.3")
    fig.text(0.5, 0.030, GATE_LINE_PASS.split("; GA")[0] + ".", ha="center", fontsize=6.8, color="0.3")
    fig.text(0.5, 0.006, "At this budget C2's GMM improves to 0.2434 on the extended K=1024 grid "
                         "(results/tables_D2_B16e4k.txt); V1 is 0.1449 there.  See F15.",
             ha="center", fontsize=6.8, color="0.3")
    return _save(fig, "F12_tp_envelope", """
F12.  The pilot-budget operating envelope at equal training budget, GATE-PASSING checkpoint
(10_SPEC_stageC §6f, run B16e4).
TOP: BLER after 16 outer iterations, D2, n = 2560 per SNR point, every arm -- learned and classical --
fitted or trained on the SAME N_train = 1.6e5 channel set.  The GMM arm is b* = kron K=512, chosen by
validation log-likelihood over all 12 configurations of the Nr=8 grid up to K = 512 (all present; see
code/check_fits_n16e4.sh).  That grid is NOT the widest one available: §6l later fitted K = 1024 at
this budget, b* moved there, and the C2 GMM improves from 0.2527 to 0.2434 (F14, F15c).  This figure
keeps K <= 512 because that is the grid measured for all three cells.  Array (8x4), frame length T = 16, code and SNR grid are identical across
the three panels; the information block SHRINKS with Tp (K = 50 / 46 / 42 bits), so absolute BLER
levels are not on a common codeword footing across panels -- only the within-panel arm ordering is
compared.  A block on which an arm raised carries a non-finite block error and is COUNTED AS A BLOCK
ERROR, exactly as the pre-registered analysis does (code/analysis.py:172-175).  A point drawn hollow
on the dashed line is 0 of 2560 blocks (resolution 1/2560).
READING THE THREE PANELS.  At Tp = 4 the learned arm (V1) is below the GMM at every SNR.  At Tp = 3
the two curves CROSS: V1 is below the GMM from -3 to +9 dB and above it at +12 and +15 dB.  At Tp = 2 the
GMM is below V1 everywhere except +0 dB, and at -3 dB every learned arm collapses (V0 BLER 1.000,
V1 0.982; the F3 divergence guard fires on 2560/2560 trials, results/guard_D2_B16e4.txt).
BOTTOM-LEFT, bars (left axis): the pre-registered decision-point sign test for M-ours-bstar -> V1 in
each cell, as the margin (a - b)/(a + b) over DISCORDANT pairs, where a:b = only-first-fails :
only-second-fails, so positive = the learned arm wins.  This is a margin among discordant pairs, not
an effect size.  Each annotation gives a:b, the number of discordant pairs out of 3 x 2560, the
pooled p, how many of the three decision points went to which arm, and WHICH SNRs those decision
points were -- the anchor rule (|log10(BLER/0.1)| smallest, BLER in [0.005, 0.9]) places them at
-3/+0/+3 dB for C2 and at +6/+12/+15 dB for C5 and C1, so the three bars are NOT read at a common
SNR.  That is why C5's bar is a tie (623:640, p = 0.65) although its curve is below the GMM's over
-3..+6 dB: its decision points sit in the high-SNR region where the curves have already crossed.
All three comparisons are POWERED.  Numbers are transcribed from results/tables_D2_B16e4.txt; this
figure runs no test.
BOTTOM-LEFT, blue (right axis, in nu_q units): the closed-form iteration-1 cavity-variance floor
nu_q -> cbar (Nt - Tp)/Tp (squares, dashed) = 1.00 / 0.33 / 0.00, which follows from Tp < Nt leaving
Nr(Nt - Tp) null directions in G while the data columns are still zero-valued; the MEASURED
iteration-1 nu_q at -3 dB where a measurement exists (filled circles: C1 1.997 and C2 0.499 from
results/sigma_grid_D2.txt, 2026-09-20, n = 64; C5 was not in that measurement and its -3 dB value
0.998 is the closed form, drawn hollow); and the top of the FROZEN training sigma grid (dotted),
nu_q = 1.43.  ALL THREE FLOORS ARE INSIDE THE GRID.  What leaves the grid is the measured C1 value at
-3 dB, 2.00 = 1.40 x the top.
LIMIT OF THAT EXPLANATION, measured later and reported here: leaving the grid is NOT sufficient for
collapse.  §6p put C2 at -9 dB, where nu_q = 1.99 -- the same place as C1 at -3 dB -- and V1 did not
collapse there (guard 0.000, and V1 still beat the GMM 41:3).  What separates the cells is the
Nr(Nt - Tp) null directions of an anisotropic cavity, not the size of the scalar nu_q.
PROVENANCE OF THE PREDICTION.  The cell-level envelope prediction is §6f, commit 8880d33 at 12:23:43,
before the first run started at 12:33:04; §6f itself discloses that those cell predictions were made
after seeing the NON-equal-budget N = 1.6e5 C1/C5 results, so only the equal-budget ordering was
blind.  The closed form was registered in §6j (commit 7737551, 13:06:25) while that run was still
executing, and its agreement with 1.997 at -3 dB is a consistency check against a value on disk since
2026-09-20, not a blind prediction.
SCOPE.  One testbed (D2), one seed (a1; the C2 numbers reproduce on seeds a2/a3 within 0.005 BLER at
N = 1e4, §6g), GMM grid truncated at K = 512 for this run.  """ + GATE_LINE_PASS + """  On the
extended K = 1024 grid at the same budget the C2 GMM improves from 0.2527 to 0.2434 while V1 is
0.1449 (results/tables_D2_B16e4k.txt); F15 shows that the gap is insensitive to both the training
budget and the number of mixture components.
""")


# ------------------------------------------------------------------ F13  sign vs magnitude --------

_CF = {   # key -> (label, colour, marker, linestyle, group)
    "gmmB|eta":        ("fitted GMM, same loop (reference)",                     "tab:red",    "D", "-.", "ref"),
    "gmmB|flip4":      ("fitted GMM, SIGN of 4 eigenvalues flipped (flip4)",     "0.35",       "x", "--", "ref"),
    "gmmB|tiny4":      ("fitted GMM, 4 eigenvalues shrunk to 1e-4, sign kept (tiny4)", "0.35", "+", ":", "ref"),
    "dscore|eta":      ("learned score, no intervention (pre-registered wiring)", "tab:purple", "v", ":", "arm"),
    "dscore|abs1e-2":  (r"learned, floor $|\lambda|$ at $10^{-2}$, sign KEPT (abs1e-2)", "tab:orange", "s", "--", "arm"),
    "dscore|psd1e-2":  (r"learned, clamp $\lambda$ to $[10^{-2},1]$, sign repaired (psd1e-2)", "tab:green", "o", "-", "arm"),
    "dscore|belsc":    ("learned, D-14 matrix site removed (belsc)",             "tab:cyan",   "^", "-", "arm"),
    "dscore|mean":     ("learned, clip='mean' instead of 'eta' (mean)",          "tab:blue",   "P", "-", "arm"),
}
N_CF = 256


def _cf_table(block):
    txt = open(os.path.join(RES, "jacpsd_counterfactual_SUMMARY_n256.txt"), encoding="utf-8").read()
    seg = txt.split(f"===== {block} =====")[1].split("=====")[0]
    out = {}
    for line in seg.strip().splitlines()[1:]:
        parts = line.split()
        if len(parts) < 8 or "|" not in parts[0]:
            continue
        try:
            out[parts[0]] = np.array([float(x) for x in parts[1:8]])
        except ValueError:
            continue
    return out


def fig13():
    plt.rcParams.update({"font.size": 7.5, "axes.labelsize": 7.5, "axes.titlesize": 8,
                         "xtick.labelsize": 6.8, "ytick.labelsize": 6.8, "legend.fontsize": 6.5})
    bler = _cf_table("BLER@16")
    div = _cf_table("divergence fraction (NMSE@16 > 10)")
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(7.16, 3.6),
                                  gridspec_kw=dict(wspace=0.28, left=0.09, right=0.985, top=0.93,
                                                   bottom=0.36))
    RESL = 1.0 / N_CF
    LINE = 0.5 * RESL                       # a real 1/256 sits ABOVE the line; only censored zeros sit on it
    order = [k for k in _CF if _CF[k][4] == "ref"] + [k for k in _CF if _CF[k][4] == "arm"]
    for j, key in enumerate(order):        # reference arms first so they never cover the learned arms
        lab, col, mk, ls, grp = _CF[key]
        if key not in bler:
            continue
        y = bler[key]
        k = np.round(y * N_CF).astype(int)
        lo = np.array([cp95(int(kk), N_CF)[0] for kk in k])
        hi = np.array([cp95(int(kk), N_CF)[1] for kk in k])
        z = k == 0
        jit = (j - len(order) / 2) * 0.09
        yy = np.maximum(y, LINE)
        ax.semilogy(SNRS, yy, ls, color=col, marker=mk, ms=3.4, lw=1.0, label=lab,
                    zorder=2 if grp == "ref" else 3)
        ok = ~z
        ax.errorbar(SNRS[ok], yy[ok], yerr=[yy[ok] - np.maximum(lo[ok], LINE), hi[ok] - yy[ok]],
                    fmt="none", ecolor=col, elinewidth=0.6, capsize=1.5, alpha=0.7, zorder=2)
        if z.any():
            ax.plot(SNRS[z] + jit, np.full(z.sum(), LINE), marker=mk, ms=5.2, ls="none",
                    mfc="white", mec=col, mew=1.1, zorder=5)
            ax.errorbar(SNRS[z] + jit, np.full(z.sum(), LINE), yerr=[np.zeros(z.sum()), hi[z] - LINE],
                        fmt="none", ecolor=col, elinewidth=0.6, capsize=1.5, alpha=0.7, zorder=2)
        if key in div:
            ax2.plot(SNRS, div[key], ls, color=col, marker=mk, ms=3.4, lw=1.0,
                     zorder=2 if grp == "ref" else 3)
    ax.axhline(LINE, color="0.45", lw=0.7, ls=(0, (4, 3)), zorder=1)
    ax.text(-4.2, LINE * 0.82, "hollow = 0 of 256 (resolution 1/256; bars = Clopper-Pearson 95%)",
            fontsize=6.0, color="0.35", va="top", ha="left")
    ax.set_ylim(LINE * 0.42, 1.4)
    ax.set_xlim(-4.5, 16.5)
    ax.set_xlabel("SNR (dB)")
    ax.set_ylabel("BLER after 16 outer iterations")
    ax.grid(alpha=0.25, which="both", lw=0.4)
    ax.set_title("(a)  BLER, n = 256 per point")
    ax2.set_xlabel("SNR (dB)")
    ax2.set_ylabel("fraction of trials with NMSE@16 > 10")
    ax2.set_xlim(-4.5, 16.5)
    ax2.set_ylim(-0.015, 0.26)
    ax2.grid(alpha=0.25, lw=0.4)
    ax2.set_title("(b)  divergence-guard firing rate")
    ax2.text(0.97, 0.10, "psd1e-2, belsc, mean, GMM (all 4):\n0.000 at every SNR (overplotted)",
             transform=ax2.transAxes, fontsize=6.2, color="0.3", ha="right", va="bottom")
    h, l = ax.get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", bbox_to_anchor=(0.5, 0.075), ncol=2, fontsize=6.3,
               framealpha=0.95)
    fig.text(0.5, 0.030, "do() interventions on ONE fixed checkpoint, D2 cell C2, n = 256 per SNR.  DIAGNOSTIC "
                         "PROBE: none is an arm, none appears in any BLER table, no paired test is computed "
                         "here (the pre-registered power guard does not apply).", ha="center", fontsize=6.6,
             color="0.3")
    fig.text(0.5, 0.008, GATE_LINE + "  The GMM reference uses the N = 1e4 fit: equal budget.",
             ha="center", fontsize=6.6, color="0.3")
    return _save(fig, "F13_sign_vs_magnitude", """
F13.  Sign versus magnitude of the site Jacobian's eigenvalues (10_SPEC_stageC §6h).
Each learned-score curve is the SAME checkpoint through the SAME EP receiver with ONE change to the
D-14 site: to its Jacobian eigenvalues (abs1e-2, psd1e-2), to the site itself (belsc removes it), or
to the clip rule (mean).  Only the psd1e-2 / abs1e-2 pair is the sign contrast; belsc and mean are two
other ways of removing the indefinite site, and their coincidence with psd1e-2 is an observation, not
part of the pre-registered score.  The fitted-GMM reference (N = 1e4 fit, equal budget) runs the
identical loop, and two GMM-side interventions isolate the two axes cleanly on a VALID Jacobian:
flip4 flips the SIGN of four eigenvalues (BLER 0.418 / 0.117 at -3 / 0 dB against the untouched
GMM's 0.301 / 0.090) while tiny4 shrinks the same four to 1e-4 with sign kept (0.305 / 0.090,
unchanged).  Note that the psd1e-2 / abs1e-2 pair confounds magnitude for eigenvalues below -1e-2
(psd1e-2 maps them to +1e-2, abs1e-2 leaves them), which is why the GMM-side pair is shown.
D2, cell C2 (Tp = 4), n = 256 trials per SNR point, all 7 SNRs, no point dropped; error bars are
Clopper-Pearson 95% intervals; a hollow marker on the dashed line is 0 of 256 (resolution 1/256),
a real 1/256 plots above the line.
(a) The magnitude-only floor does not reach the sign-repaired band at any of the seven SNRs
(0/7, gaps +0.098 to +0.836 against dscore|belsc), although it does reduce BLER against the
un-intervened arm (0.332 -> 0.098 at +15 dB) and, in (b), nearly eliminates guard firings.
Repairing the sign, removing the site or changing the clip rule all recover the receiver; at n = 256
the three are statistically indistinguishable (all within the pre-registered 0.02 absolute band of
each other at all 7 SNRs).  The GMM reference's +12 dB point is 4/256; §6h records an unexplained
normalisation kink at 12 dB.  (b) The guard fires on 1.6-22.3% of trials without the intervention
and on 0.000 after any of the three repairs; the magnitude-only floor leaves 0.0-1.6%.
SCORING AGAINST THE PRE-REGISTERED SENTENCE.  §6h (commit 7ec3d37, before the roll-up) reads,
verbatim: "dscore|psd1e-2(부호 교정)가 7 SNR 전부에서 C2 BLER 을 V1 대역(절대 0.02 이내)으로 회복시키고,
dscore|abs1e-2(크기만 바닥치고 부호 유지)는 회복시키지 못한다" -- the reference band is the V1 ARM
(tables_D2_B1e4.txt, n = 2560).  Scored against that literal reference, psd1e-2 is within 0.02 at
6/7 SNRs (gap +0.031 at -3 dB, about 1.3 sigma at n = 256) and abs1e-2 at 0/7.  The roll-up file
scored against dscore|belsc instead (7/7 and 0/7).  Both scorings are reported; the substituted
reference was an error of the roll-up, not of the pre-registration.
SCOPE.  One cell (C2), n = 256, and a checkpoint with NO D2 gate record whose D1 sibling fails GC.
These are interventions on a diagnostic probe: they identify the mechanism, they are not arms, and
none appears in any BLER table.  The equal-budget arm results are in results/tables_D2_B1e4.txt.
Because dropping the matrix site performs identically to PSD-projecting it here, these data do not
isolate the PSD projection as the mechanism behind the V1 curve.
BUDGET NOTE (added 2026-09-22 22:20).  F12 and F14 were re-drawn on the gate-passing N = 1.6e5 run
(checkpoint ckpt/d2sx_N160000_a1.pt, n = 2560).  This figure was NOT: it stays on the n = 256
diagnostic sweep of ckpt/d2sx_N10000_a1.pt, whose D1 sibling FAILS GC.  So the V1 reference band
quoted above is from tables_D2_B1e4.txt (N = 1e4), the budget these interventions were run at, and
these curves are NOT directly comparable to the arms plotted in F12 or F14.  They identify the
mechanism; the arm results are in the tables.
""")


if __name__ == "__main__":
    for f in (fig12, fig13):
        try:
            print("  ok  ", f())
        except Exception as ex:
            import traceback
            traceback.print_exc()
            print("  FAIL", f.__name__, type(ex).__name__, ex)
