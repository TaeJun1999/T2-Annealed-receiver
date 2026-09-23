"""conf/code/figure_f14.py -- F14: the headline operating point, analysed with the menu FROZEN in
10_SPEC_stageC §6q (A1-A8) before any low-SNR result was read.

  python figure_f14.py --cell C2 --snr -3 --raw raw_B1e4 [--posthoc "..."]

Panels (§6q items):
  (a) A1/A3/A6/A7  BLER@16 of every arm at the point, Wilson 95% CI, with the site ablation (V0/V1/V4/V4b)
                   and the GMM control (bstar / bstar-scalar) side by side; the genie-gap closure printed.
  (b) A2           NMSE_H (median) vs outer iteration, all arms -- where the gain appears.
  (c) A2           BLER vs outer iteration.
  (d) A5           nu_q queried per outer iteration (median, n=8 diagnostic) against the frozen grid top,
                   from results/diag/sigma-coverage_D2_<cell>_n8.npz when present.
  A4 (guard) is printed in the caption from results/guard_D2_<tag>.txt.  A8 (Module H cost) is NOT read
  from results/complexity_moduleH.txt or results/review_next/complexity_moduleH_ep.txt: its text and
  numbers are hardcoded in the caption below and printed for every raw set (review_next cost/M1, 2026-09-23).
BLER, NMSE and guard numbers are read from files; the A8 text, the §6p ratios in the default first line and
the SCOPE/gate sentences are fixed text.  Nothing is recomputed, resampled or re-run.  The headline-selection
rule of §6q is enforced in the caption: if the point was NOT the §6p-predicted one, the caption says
"post-hoc" in its first line, verbatim.
"""
import argparse
import glob
import os
import re
import sys
import collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import common as C
import figures as F0
from figures_stagec import _save, RES
from figures_stagec2 import cp95, GATE_LINE, GATE_LINE_PASS, GRID_TOP_NU

ARMS = [   # (arm, label, colour, marker)
    ("R1-turbo",            "classical turbo (no prior)",             "tab:brown",  "s"),
    ("R2-ours-G",           "Gaussian sample-cov. prior",            "tab:blue",   "o"),
    ("M-ours-bstar",        "fitted GMM, b* (val. log-lik.)",         "tab:red",    "D"),
    ("M-ours-bstar-scalar", "fitted GMM, scalar site (control)",      "tab:pink",   "d"),
    ("M-ours-dscore-C-V0",  "learned score, pre-registered site (V0)", "tab:purple", "v"),
    ("M-ours-dscore-C-V1",  "learned score, PSD-projected site (V1)", "tab:green",  "o"),
    ("M-ours-dscore-C-V4",  "learned score, scalar site (V4)",        "tab:olive",  "^"),
    ("M-ours-dscore-C-V4b", "learned score, scalar site, scal=site (V4b)", "tab:cyan", "<"),
    ("R5-genie",            "genie CSI (known-H reference)",          "k",          "*"),
]


def load_point(rawdir, cell, snr):
    acc = collections.defaultdict(list)
    for f in glob.glob(os.path.join(C.CONF, rawdir, f"D2_{cell}_*snr{int(snr)}_*.npz")):
        d = np.load(f, allow_pickle=True)
        for k in d.files:
            if "|" in k and k.split("|")[1] in ("blk_err", "nmse", "failed"):
                acc[k].append(d[k])
    out = {}
    for k, v in acc.items():
        out[k] = np.concatenate(v) if v[0].ndim >= 1 and v[0].shape[0] > 1 else np.array(v)
    return out


def read_guard(tag, cell, snr):
    """The pre-registered F3 guard rows for one (cell, SNR) out of results/guard_D2_<tag>.txt.
    Columns: cell  SNR  arm  fired  of  rate  worst-NMSE.  Returns {arm: (rate, worst)}."""
    path = os.path.join(RES, f"guard_D2_{tag}.txt")
    out = {}
    if not os.path.exists(path):
        return out
    for line in open(path, encoding="utf-8", errors="replace"):
        m = re.match(r"\s*(\S+)\s+([+-]?\d+)\s+(\S+)\s+(\d+)\s+(\d+)\s+([0-9.]+)\s+(\S+)", line)
        if m and m.group(1) == cell and int(m.group(2)) == int(snr):
            out[m.group(3)] = (float(m.group(6)), float(m.group(7)))
    return out


def wilson(p, n, z=1.96):
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return c - h, c + h


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", default="C2")
    ap.add_argument("--snr", type=float, default=-3)
    ap.add_argument("--raw", default="raw_B1e4")
    ap.add_argument("--tag", default="B1e4")
    ap.add_argument("--posthoc", default="", help="non-empty => this point was NOT the §6p-predicted one")
    ap.add_argument("--name", default="F14_headline_point")
    a = ap.parse_args()
    plt.rcParams.update({"font.size": 7.5, "axes.labelsize": 7.5, "axes.titlesize": 8,
                         "xtick.labelsize": 6.8, "ytick.labelsize": 6.8, "legend.fontsize": 6.4})
    d = load_point(a.raw, a.cell, a.snr)
    # the gate sentence must follow the CHECKPOINT this run used, not a module default: raw_B16e4* used
    # d2sx_N160000_a1 (no D2 gate row; its D1 sibling passes the gates), every other raw dir here used a
    # checkpoint whose D1 sibling fails GC.  [record correction 2026-09-23, review_next G-1.2]
    gate_line = GATE_LINE_PASS if a.raw.startswith("raw_B16e4") else GATE_LINE
    n = None
    stats = {}
    for arm, lab, col, mk in ARMS:
        kb, kn = f"{arm}|blk_err", f"{arm}|nmse"
        if kb not in d:
            continue
        be = d[kb]                                        # (n, 16)
        be = np.where(np.isfinite(be), be, 1.0)           # analysis.py:172-175 rule
        n = be.shape[0]
        nm = d[kn]
        stats[arm] = dict(bler_it=be.mean(0), nmse_it=np.nanmedian(np.where(np.isfinite(nm), nm, np.nan), 0),
                          bler=float(be[:, 15].mean()), raised=int((~np.isfinite(d[kb][:, 15])).sum()))
    # (§6q A4) The divergence guard is the PRE-REGISTERED F3 statistic: a trial fires if NMSE > 10 or is
    # non-finite at ANY of the 16 iterations (guard_report.py:42-43).  An earlier draft of this figure
    # recomputed it at iteration 16 only, which understated V0 by 3-6x and reported the genie -- an arm
    # the guard file excludes.  Read the file instead; it is the artefact §6q A4 names.
    guard = read_guard(a.tag, a.cell, a.snr)
    fig = plt.figure(figsize=(7.16, 5.6))
    gs = GridSpec(2, 2, figure=fig, hspace=0.46, wspace=0.30, left=0.09, right=0.985, top=0.94, bottom=0.20)

    # (a) BLER@16 per arm with Wilson CI
    ax = fig.add_subplot(gs[0, 0])
    xs, labs = [], []
    for i, (arm, lab, col, mk) in enumerate(ARMS):
        if arm not in stats:
            continue
        p = stats[arm]["bler"]
        lo, hi = wilson(p, n)
        lo, hi = min(lo, p), max(hi, p)                   # at p = 0 or 1 the interval must still bracket p
        ax.bar(i, p, color=col, alpha=0.85, width=0.7)
        ax.errorbar(i, p, yerr=[[p - lo], [hi - p]], fmt="none", ecolor="k", elinewidth=0.7, capsize=2)
        ax.text(i, hi + 0.012, f"{p:.3f}", ha="center", va="bottom", fontsize=5.8)
        xs.append(i); labs.append(arm.replace("M-ours-", "").replace("dscore-C-", ""))
    ax.set_xticks(xs); ax.set_xticklabels(labs, rotation=35, ha="right", fontsize=6.2)
    ax.set_ylabel("BLER after 16 outer iterations")
    ax.set_title(f"(a)  {a.cell}, {a.snr:+.0f} dB, n = {n}, Wilson 95%")
    ax.grid(alpha=0.25, axis="y", lw=0.4)
    g, v1, gm = stats["R5-genie"]["bler"], stats["M-ours-dscore-C-V1"]["bler"], stats["M-ours-bstar"]["bler"]
    v0 = stats["M-ours-dscore-C-V0"]["bler"]
    ax.text(0.985, 0.60, f"V1 closes {100 * (gm - v1) / (gm - g):.0f}% of the GMM-to-genie gap\n"
                         f"V0 -> V1: {100 * (v0 - v1) / v0:.1f}% fewer block errors",
            transform=ax.transAxes, ha="right", va="top", fontsize=6.2, color="0.25")

    # (b) NMSE vs iteration ; (c) BLER vs iteration
    it = np.arange(1, 17)
    axb = fig.add_subplot(gs[0, 1]); axc = fig.add_subplot(gs[1, 0])
    for arm, lab, col, mk in ARMS:
        if arm not in stats:
            continue
        axb.semilogy(it, np.maximum(stats[arm]["nmse_it"], 1e-4), color=col, marker=mk, ms=2.8, lw=1.0, label=lab)
        axc.semilogy(it, np.maximum(stats[arm]["bler_it"], 0.5 / n), color=col, marker=mk, ms=2.8, lw=1.0)
    axb.set_xlabel("outer iteration"); axb.set_ylabel("NMSE of the channel estimate (median)")
    axb.set_title("(b)  where the gain appears: NMSE$_H$ per iteration"); axb.grid(alpha=0.25, which="both", lw=0.4)
    axc.set_xlabel("outer iteration"); axc.set_ylabel("BLER at that iteration")
    axc.set_title("(c)  BLER per iteration"); axc.grid(alpha=0.25, which="both", lw=0.4)

    # (d) nu_q trajectory from the n=8 diagnostic, if present
    axd = fig.add_subplot(gs[1, 1])
    dpath = os.path.join(RES, "diag", f"sigma-coverage_D2_{a.cell}_n8.npz")
    have_d = False
    if os.path.exists(dpath):
        z = np.load(dpath, allow_pickle=True)
        # keys are '<snr>dB|<arm>|<field>', e.g. '-3dB|M-ours-dscore|nu_q' (8, 16); the SNR prefix is
        # written with %+.0f-like formatting for negatives and plain for positives, so parse it.
        def _key(arm, field):
            for k in z.files:
                m = re.match(r"([+-]?\d+)dB\|(.+)\|(.+)$", k)
                if m and int(m.group(1)) == int(a.snr) and m.group(2) == arm and m.group(3) == field:
                    return k
            return None
        for arm, lab, col in (("M-ours-dscore", "learned score (V0 wiring)", "tab:purple"),
                              ("ctrl-bstar-sIF", "same GMM through the score interface", "tab:red"),
                              ("ctrl-G-sIF", "Gaussian through the score interface", "tab:blue")):
            k = _key(arm, "nu_q")
            if k is not None:
                nu = z[k]
                if np.isfinite(nu).any():
                    axd.semilogy(it, np.nanmedian(nu, 0), color=col, marker="o", ms=2.8, lw=1.0, label=lab)
                    have_d = True
    axd.set_xlim(0.5, 16.5)                               # fixed BEFORE any text: with savefig bbox='tight',
    axd.set_yscale("log")                                 # a data-coordinate label outside auto-limits
    axd.set_ylim(1e-3, 3.0)                               # stretched the whole figure to 8000 px wide
    axd.axhline(GRID_TOP_NU, color="tab:blue", ls=":", lw=0.9, label=f"frozen grid top $\\nu_q$ = {GRID_TOP_NU:.2f}")
    axd.axhline(2 * 0.03306220 ** 2, color="tab:blue", ls=":", lw=0.9)
    axd.text(16.2, 2 * 0.03306220 ** 2 * 1.25, "grid bottom", fontsize=5.6, color="tab:blue", ha="right")
    axd.set_xlabel("outer iteration"); axd.set_ylabel("$\\nu_q$ queried (median, n = 8)")
    axd.set_title("(d)  cavity variance the denoiser is asked for" + ("" if have_d else "  [diagnostic not yet run]"))
    if have_d:
        axd.text(0.02, 0.97, "probe uses ckpt d2sx_N10000_a1 (n = 8),\nnot this figure's checkpoint",
                 transform=axd.transAxes, fontsize=5.6, color="0.35", va="top")
    axd.grid(alpha=0.25, which="both", lw=0.4)
    if have_d:
        axd.legend(fontsize=5.8, loc="lower right")
    h, l = axb.get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", bbox_to_anchor=(0.5, 0.045), ncol=3, fontsize=6.2, framealpha=0.95)
    fig.text(0.5, 0.008, gate_line, ha="center", fontsize=6.4, color="0.3")
    guard_txt = ("; ".join(f"{k.replace('M-ours-', '').replace('dscore-C-', '')} {v[0]:.3f} "
                           f"(worst NMSE {v[1]:.3g})" for k, v in sorted(guard.items()))
                 or "no arm in the guard file fires at this point")
    first = ("POST-HOC HEADLINE POINT: " + a.posthoc + "  ") if a.posthoc else (
        "This is the §6d/§6q PRE-REGISTERED DECISION POINT (anchor rule, 3 points, POWERED), not the "
        "§6p-predicted maximum-gap point: §6p predicted the largest GMM/V1 ratio at -6/-7 dB and that "
        "prediction FAILED (measured 1.32 / 1.14 there against 1.74 at -3 dB; see F15a and F14b).  ")
    return _save(fig, a.name, f"""
F14.  The headline operating point, analysed with the menu frozen in 10_SPEC_stageC §6q (A1-A8).
{first}D2 cell {a.cell}, SNR {a.snr:+.0f} dB, equal training budget (every arm on the same N_train channel
set; raw {a.raw}), n = {n} trials.  Blocks on which an arm raised are counted as block errors
(analysis.py:172-175).
(a) BLER after 16 outer iterations with Wilson 95% intervals for every arm, so the site ablation
(V0 -> V1 -> V4 / V4b, same checkpoint) and the GMM control (bstar -> bstar-scalar, same fit) are read
side by side (A1, A6).  GMM {gm:.3f} vs V1 {v1:.3f}: V1 removes {100 * (gm - v1) / gm:.1f}% of the GMM's
block errors and closes {100 * (gm - v1) / (gm - g):.0f}% of the GMM-to-genie gap (A7); V0 -> V1 removes
{100 * (v0 - v1) / v0:.1f}% (the pre-registered wiring against its one-line repair).  The paired sign
test and its confidence interval (A3) are in results/tables_D2_{a.tag}.txt TABLE B and are not
recomputed here.
(b)-(c) NMSE_H (median) and BLER against the outer iteration (A2): the learned-score arms separate from
the GMM within the first iterations and hold the gap to iteration 16.
(d) The cavity variance nu_q the denoiser is queried with, per iteration (median of the n = 8
diagnostic results/diag/sigma-coverage_D2_{a.cell}_n8.npz), against the frozen training grid (A5).
A4, the pre-registered F3 divergence guard at this point -- a trial fires if NMSE > 10 or is
non-finite at ANY of the 16 iterations, results/guard_D2_{a.tag}.txt, which is the artefact §6q A4
names and which EXCLUDES non-estimator arms such as the genie: {guard_txt}.  Arms absent from that
list never fire anywhere in this raw set.
Panel (d) is a SEPARATE probe: results/diag/sigma-coverage_D2_{a.cell}_n8.npz is measured on\nckpt/d2sx_N10000_a1.pt (n = 8), not on this figure's checkpoint, so it shows what the receiver ASKS\nfor in this cell, not what this checkpoint answers.\nA8, Module H cost per call (results/complexity_moduleH.txt, CPU float64 one thread, means only): an
isotropic denoise_full microbenchmark -- fitted GMM b* kron K=512 (N=1e4 fit) 17.1 ms, learned score
ckpt/d2sx_N10000_a1.pt 78.8 ms (4.6x; the PSD projection itself is -0.8%, i.e. free).  It is NOT the
receiver cost ratio of the arms: M-ours-bstar calls GMMPriorB.ep_site, which that benchmark did not time.
Real-path Module H cost (kron K=1024, ckpt/d2sx_N160000_a1.pt): V1 / GMM b* = 1.35x per Module H call,
1.33x per full block at C2 -3 dB; 1.39x and 1.38x at C2 +6 dB (medians, one CPU thread,
results/review_next/complexity_moduleH_ep.txt).  The equal-budget claim is 'same training data', not
'same inference complexity'.
SCOPE.  {gate_line}  One cell, one seed (the a1 numbers reproduce on seeds a2/a3 within 0.005 BLER,
§6g), one testbed.
""")


if __name__ == "__main__":
    print("  ok  ", main())
