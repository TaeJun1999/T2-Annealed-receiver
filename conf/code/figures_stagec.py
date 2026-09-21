"""conf/code/figures_stagec.py -- Stage C result figures (10_SPEC_stageC.md).

figures.py draws F2-F6 (Stage A/B).  This file continues the numbering with the Stage C set:

  F7   mechanism: eigenvalue spectrum of sym(Jr), D1 (learned / TRUE grid GMM / fitted GMM K=32)
       vs D2 (learned / fitted kron GMM K=512).  D2's learned spectrum crosses zero; nothing else does.
  F8   budget: f(lmin(Jr) < 0) and asym(Jr) on the frozen 20-point sigma grid, one line per training
       budget, plus the epoch pair at N=1.6e5, the FITTED GMM, and D1's learned model as the contrast.
  F9   the sigma band and the SNR shape: shift_med on the sigma grid against the settling experiment's
       divergence rate on the SNR grid, linked ONLY by the separately measured sigma_t(SNR) the
       receiver actually queries.  The two x axes are different quantities and are NOT forced onto one.
  F10  the D1 confirmatory BLER run, n=2560, cells C5 / C2 / C1, with the power guard's UNDECIDED
       pairs marked and C1's -3 dB collapse left visible.
  F11  the D2 CONFIRMATORY BLER run -- the headline.  n=2560, C2 (Tp=4) as the main panel with C5
       (Tp=3) and C1 (Tp=2) beside it; the pre-registered wiring V0 sits above classical turbo, the
       repaired wirings V1/V4 are the best non-genie arms on C2 and lose that ordering on C1, every
       high-rate divergence-guard firing is ringed, and the UNDECIDED pairs are banded.

Every number is READ from the files below; nothing here recomputes, resamples or re-runs anything.
  results/jac_spectrum.txt            F7 provenance (the ADDENDUM's D1 table is the log below)
  logs/jacspec_D1_true.log            F7 left   (learned / TRUE 1024-comp grid GMM / fitted GMM K=32)
  logs/jacspec_D2_N10000.log          F7 right, F8 context
  logs/jacspec_D2_final.log           F7 right  (ckpt/d2sx_N160000_a1.pt, 1784 ep., REPRODUCIBLE)
  logs/jacpsd_N{10000_a1,40000_a1,160000,160000_late}.log   F8, F9 top
  logs/jacpsd_D1_N160000.log          F8 contrast (gate-passing D1 checkpoint)
  logs/diag_sigma_coverage.log        F9  the measured sigma_t(SNR) link, n=12
  results/settling_D2.txt             F9 bottom (n=256 paired trials per SNR)
  results/tables_D1_C.txt             F10 (TABLE A BLER, TABLE B power guard)
  results/guard_D1_C.txt              F10 (divergence-guard firings)
  results/tables_D2_C.txt             F11 (TABLE A BLER, TABLE B power guard)
  results/guard_D2_C.txt              F11 (divergence-guard firings)

House style (rcParams, PDF+PNG export, legend-carries-the-condition) is inherited from figures.py by
importing it; the STYLE table is reused verbatim and only EXTENDED with the Stage C arms.

GATE STATUS, because two of these figures are diagnostic probes and must say so:
  D1  ckpt/sx_N160000_D1.pt           PASSES all four pre-registered gates (results/samplecx_D1.txt,
                                      LADDER_C.md SX160000: GA 9.9e-16 GB +0.27% GC 0.0999 GD 0.0718).
  D2  ckpt/d2sx_N10000_a1.pt          FAILS (GC 0.224 vs 0.15).  Everything D2 in F7/F8/F9 is an
      d2sx_N160000 snap / late        UN-GATED diagnostic probe and licenses no claim.
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, NullFormatter
from matplotlib.transforms import blended_transform_factory
import common as C
import figures as F0                      # house style: rcParams, FIG dir, STYLE

FIG, RES, LOG = F0.FIG, os.path.join(C.CONF, "results"), os.path.join(C.CONF, "logs")
SNRS = np.array([-3., 0., 3., 6., 9., 12., 15.])

# ------------------------------------------------------------------ readers (text -> arrays) ------

_JACPSD = ["k", "sigma", "nu", "asym_r", "lmin_r", "lmax_r", "f_neg_r", "herm_c", "lmin_c", "lmax_c",
           "f_neg_c", "f_gt1_c", "clipfrac", "shift_med", "shift_max"]
_JACSPEC = ["k", "sigma", "nneg_mean", "nneg_med", "nneg_p90", "n_lt_001", "n_lt_01",
            "lmin", "l25", "lmed", "lmax"]


def _sections(path, names):
    """Read the '=== model ===' blocks of a jacpsd/jacspec log into {model: {col: array}}."""
    out, cur = {}, None
    for ln in open(path):
        m = re.match(r"^=== (.+?) ===\s*$", ln)
        if m:
            cur = out.setdefault(m.group(1), [])
            continue
        if cur is None or "|" not in ln or ln.lstrip().startswith(("k ", "#")):
            continue
        tok = [t for part in ln.split("|") for t in part.split()]
        if len(tok) != len(names):
            continue
        try:
            cur.append([float(t) for t in tok])
        except ValueError:
            continue
    return {k: dict(zip(names, np.array(v, float).T)) for k, v in out.items() if v}


def jacpsd(tag):
    return _sections(os.path.join(LOG, f"jacpsd_{tag}.log"), _JACPSD)


def jacspec(tag):
    return _sections(os.path.join(LOG, f"jacspec_{tag}.log"), _JACSPEC)


def settling(block="fraction of trials"):
    """results/settling_D2.txt -> {arm: array(7)} of the requested block, in SNR order."""
    out, on = {}, False
    for ln in open(os.path.join(RES, "settling_D2.txt")):
        if ln.startswith(block):
            on = True
            continue
        if on:
            if ln.startswith(("-", "arm", "\n", "READING")):
                if ln.startswith("READING"):
                    break
                continue
            t = ln.split()
            if len(t) >= 8 and "|" in t[0]:
                out[t[0]] = np.array(t[1:8], float)
    return out


def sigma_of_snr():
    """logs/diag_sigma_coverage.log -> {snr: (median, lo, hi)} of the sigma_t M-ours-dscore QUERIES.

    n = 12 trials per point, cell C2, ckpt/d2sx_N10000_a1.pt -- a separate, smaller diagnostic than
    the settling run.  This is the ONLY measured link between F9's two x axes.

    NOTE on the bracket: diag_sigma_coverage.py prints [nanmin, nanmax] of the 12 x 16 = 192 queried
    sigma_t, NOT an inter-quartile range.  It is the FULL range and is labelled as such."""
    out, snr, arm = {}, None, None
    for ln in open(os.path.join(LOG, "diag_sigma_coverage.log")):
        m = re.match(r"^===== SNR ([+-]?\d+) dB", ln)
        if m:
            snr = float(m.group(1))
        if ln.strip().startswith("---"):
            arm = ln.strip().lstrip("- ").strip()
        m = re.search(r"sigma_t queried : median ([\d.e+-]+)\s+\[([\d.e+-]+), ([\d.e+-]+)\]", ln)
        if m and arm == "M-ours-dscore":
            out[snr] = tuple(float(g) for g in m.groups())
    return out


def tableA(cell, path=os.path.join(RES, "tables_D1_C.txt")):
    """TABLE A of results/tables_D1_C.txt -> {arm: array(7)} of BLER at the arm's reporting iteration."""
    out, on = {}, False
    for ln in open(path):
        if ln.startswith(f"--- cell {cell} ("):
            on = True
            continue
        if on:
            if "per-point detail rows" in ln:
                break
            v = re.findall(r"(-?\d+\.\d+)\(", ln)
            if len(v) == 7:
                out[ln.split()[0]] = np.array(v, float)
    return out


def guard(path=os.path.join(RES, "guard_D1_C.txt")):
    """results/guard_D1_C.txt -> {(cell, snr, arm): (fired, of)}"""
    out = {}
    for ln in open(path):
        t = ln.split()
        if len(t) == 7 and t[0].startswith("C") and t[2].startswith(("M-", "R")):
            out[(t[0], float(t[1]), t[2])] = (int(t[3]), int(t[4]))
    return out


def undecided(cell, path=os.path.join(RES, "tables_D1_C.txt")):
    """TABLE B -> ([(pair, [snr...])], set(snr)) for the pairs the power guard left UNDECIDED."""
    pairs, snrs, cur, dsnr, on = [], set(), None, [], False
    for ln in open(path):
        if re.match(rf"^--- cell {cell}\s+prior", ln):
            on = True
            continue
        if on:
            if ln.startswith("--- cell ") or ln.startswith("="):
                break
            m = re.match(r"^  (\S+) -> (\S+)\s+\[decision", ln)
            if m:
                cur, dsnr = f"{m.group(1)} -> {m.group(2)}", []
            m = re.search(r"decision SNRs \[([^\]]*)\]", ln)
            if m:
                dsnr = [float(x.strip().strip("'")) for x in m.group(1).split(",") if x.strip()]
            if "-> UNDECIDED" in ln and cur:
                pairs.append((cur, dsnr))
                snrs.update(dsnr)
                cur = None
    return pairs, snrs


def _save(fig, name, caption):
    for e in ("pdf", "png"):
        fig.savefig(os.path.join(FIG, f"{name}.{e}"))
    with open(os.path.join(FIG, f"{name}.txt"), "w") as fh:
        fh.write(caption.strip() + "\n")
    plt.close(fig)
    return name


def _foot(fig, txt, y=-0.02):
    fig.text(0.5, y, txt, ha="center", va="top", fontsize=6.2, color="0.35")


# ------------------------------------------------------------------ F7  the mechanism -------------

def fig7():
    """Spectrum of sym(Jr): D1 (three models) vs D2 (two), quantile ladder per sigma.

    Per model and sigma the log gives lmin / 25th pct / median / lmax over n=48 held-out samples x 64
    eigenvalues.  Drawn as a whisker (lmin..lmax) with a bar on the 25th-percentile..median body, so the
    reader sees the WHOLE spectrum's position relative to zero, not one order statistic."""
    d1 = jacspec("D1_true")
    d2a = jacspec("D2_final")        # ckpt/d2sx_N160000_a1.pt -- permanent ckpt, 1784 ep. (patience).
    #  NOT jacspec_D2_N160000.log: that one was measured on /tmp/.../d2sx_N160000_snap.pt, a
    #  session-scoped temp-dir snapshot the 18:20 audit flagged as irreproducible and which the
    #  23:50 re-measurement supersedes (results/jac_spectrum.txt ADDENDUM 2026-09-21 23:50).
    L = [("learned  N=1.6e5 (gate-PASS)", "tab:purple", d1["diffusion"]),
         ("TRUE prior: grid GMM, 1024 comp.", "k", d1["TRUE-prior(grid GMM, 1024 comp)"]),
         ("fitted GMM  b*=kron, K=32, N=1e4", "tab:orange", d1["FITTED-GMM(b*=kron,K=32,N=10000)"])]
    R = [("learned  N=1.6e5, final 1784 ep. (UN-GATED)", "tab:purple", d2a["diffusion"]),
         ("fitted GMM  b*=kron, K=512", "tab:orange", d2a["FITTED-GMM(b*=kron,K=512,N=10000)"])]

    fig, axes = plt.subplots(1, 2, figsize=(7.8, 3.7), sharey=True)
    for ax, sets, ttl in zip(axes, (L, R),
                             ("(a) D1  grid-GMM prior, full support in $\\mathbb{R}^{64}$",
                              "(b) D2  sparse specular, support $=\\bigcup$ 3L-dim manifolds")):
        off = np.linspace(-0.105, 0.105, len(sets))
        for j, (lab, col, d) in enumerate(sets):
            x = d["sigma"] * 10 ** off[j]
            ax.vlines(x, d["lmin"], d["lmax"], color=col, lw=1.0, alpha=0.85)
            ax.vlines(x, d["l25"], d["lmed"], color=col, lw=4.4, alpha=0.95)
            ax.plot(x, d["lmin"], marker="_", color=col, ms=7, mew=1.6, ls="none", label=lab)
            ax.plot(x, d["lmax"], marker="_", color=col, ms=7, mew=1.6, ls="none")
        ax.axhline(0.0, color="tab:red", lw=1.1)
        ax.set_xscale("log")
        ax.set_yscale("symlog", linthresh=1e-3, linscale=0.55)
        # headroom both ends: lmax reaches 5.90 (at top=8 it collided with the n_neg row and the
        # upper whisker caps were lost) and lmin reaches -0.45, so the legend needs empty space
        # BELOW the data -- at bottom=-1 it was sitting on top of the negative whiskers.
        # The symlog linear band (+-1e-3, linscale 0.55) keeps its size, so widening the limits costs
        # no resolution where it matters.  It buys two things the earlier limits (-1, 8) lost:
        # lmax reaches 5.90 and its whisker caps were hidden under the n_neg row, and lmin reaches
        # -0.45 and its caps were hidden under the legend.  Both ends are now clear of both.
        ax.set_ylim(-30.0, 30.0)
        ax.set_xlim(0.018, 1.75)   # room for the leftmost n_neg label, which was clipped at 0.022
        ax.set_xlabel(r"noise level $\sigma$ of the frozen grid")
        ax.set_title(ttl, fontsize=8.6)
        ax.legend(loc="lower left", fontsize=6.8, frameon=True, framealpha=0.9, edgecolor="none")
    axes[1].legend(loc="lower right", fontsize=6.8, frameon=True, framealpha=0.9, edgecolor="none")
    axes[0].set_ylabel(r"eigenvalues of $\mathrm{sym}(J_r)$" "\n" r"(n=48 samples $\times$ 64 each)")
    axes[0].text(0.0195, 4e-4, "zero", fontsize=6.6, color="tab:red")
    axes[0].text(0.40, 0.29, r"$n_{\rm neg}=0$ for all three models" "\n" r"at all four $\sigma$",
                 transform=axes[0].transAxes, fontsize=7.2, color="0.25")

    dl, dg = d2a["diffusion"], d2a["FITTED-GMM(b*=kron,K=512,N=10000)"]
    blend = blended_transform_factory(axes[1].transData, axes[1].transAxes)
    for i, s in enumerate(dl["sigma"]):
        axes[1].text(s * 10 ** -0.105, 0.965, f"$n_{{\\rm neg}}$ {dl['nneg_mean'][i]:.1f}",
                     transform=blend, ha="center", va="top", fontsize=6.6, color="tab:purple")
        axes[1].annotate(f"{dg['lmin'][i]:.0e}", (s * 10 ** 0.105, dg["lmin"][i]),
                         textcoords="offset points", xytext=(6, -7), ha="left", fontsize=6.0,
                         color="tab:orange")
    _foot(fig, "Whisker = $[\\lambda_{\\min},\\lambda_{\\max}]$, bar = 25th percentile..median of the 48x64 "
               "eigenvalues at that $\\sigma$.  y is symlog (linear below $10^{-3}$): the sign change and the "
               "near-zero bulk are both on the page, nothing is clipped.\n"
               "On D2 at N=1e4 the same $n_{\\rm neg}$ counts are 8.0 / 10.6 / 11.2 / 7.8 "
               "(logs/jacspec_D2_N10000.log): 16x the data moves them 8.0$\\to$6.7, 10.6$\\to$19.8, "
               "11.2$\\to$13.5, 7.8$\\to$0.7 -- worse at two of four $\\sigma$, not merely no better.\n"
               "At $\\sigma=0.092$ the learned 25th percentile is $-0.0104$: over a quarter of the 64 "
               "eigenvalues are below zero, which is why that bar starts under the red line.  The fitted "
               "GMM on D2 stays POSITIVE but falls to $7.6\\times10^{-5}$ (per-point values beside its "
               "lower whisker, rounded to one significant figure): near the PSD boundary, not on it.")
    fig.suptitle("The EP matrix site (D-14) inverts $\\nu\\,\\mathrm{Herm}(J)$ and therefore needs $J$ "
                 "PSD.  It is, on D1.  It is not, on D2.", fontsize=9, y=1.03)
    return _save(fig, "F7_jacspectrum_D1_D2", f"""
F7.  Eigenvalue spectrum of sym(J_r), the symmetrised real Jacobian of the Tweedie denoiser that
RouteAClip._matrix_site consumes, at four points of the frozen sigma grid (k = 0, 6, 12, 18).

PLOTTED.  Per model and sigma: whisker = [lambda_min, lambda_max], bar = [25th percentile, median],
over n = 48 held-out channel samples x 64 eigenvalues each.  The red line is zero.  y is symlog with a
linear region below 1e-3, so negative eigenvalues and the near-zero bulk are both visible; no axis is
truncated and no curve is smoothed.
(a) D1: learned score, the TRUE prior (t2_gmm.angle_grid_prior, 32x32 = 1024 components, closed form),
    and the fitted GMM (b* = kron, K = 32, N = 1e4).  n_neg = 0 for all three at all four sigma.
(b) D2: learned score at N = 1.6e5, at the FINAL checkpoint of that run, and the fitted 512-component
    Kronecker GMM.  The learned spectrum crosses zero at all four sigma; mean n_neg out of 64 is
    annotated (6.7 / 19.8 / 13.5 / 0.7, exactly as the log prints them).  At sigma = 0.092 the 25th
    percentile itself is negative (-0.0104), so the drawn bar starts below the zero line: more than a
    quarter of the 64 eigenvalues are below zero there.  At N = 1e4 the same counts are
    8.0 / 10.6 / 11.2 / 7.8, so 16x the data moves them 8.0->6.7, 10.6->19.8, 11.2->13.5, 7.8->0.7 --
    worse at two of the four sigma.  "More data does not fix it" is the weak reading; the measured
    direction is not favourable.

SOURCE.  logs/jacspec_D1_true.log (panel a), logs/jacspec_D2_final.log (panel b), with
logs/jacspec_D2_N10000.log for the N = 1e4 counts quoted above; both tables are transcribed in
results/jac_spectrum.txt (ADDENDUM 2026-09-21 21:55 for D1, ADDENDUM 2026-09-21 23:50 for D2).
n = 48 per grid point.

WHICH D2 CHECKPOINT, AND WHY NOT THE EARLIER ONE.  Panel (b) is measured on ckpt/d2sx_N160000_a1.pt,
the permanent checkpoint at which that run stopped (patience, 1784 epochs, best val 3.519379e-01 at
epoch 1764).  It is NOT the epoch-240 snapshot of logs/jacspec_D2_N160000.log: that measurement was
taken against a session-scoped temp-directory file, which the 18:20 audit flagged as irreproducible
and which the 23:50 re-measurement supersedes.  Reproduce this panel with
  OMP_NUM_THREADS=2 python code/jac_spectrum.py --testbed D2 --ckpt ckpt/d2sx_N160000_a1.pt --n 48

GATE STATUS.  (a) uses ckpt/sx_N160000_D1.pt, which PASSES all four pre-registered gates
(results/samplecx_D1.txt: GB 0.0027, GC 0.0999, GD 0.0718).  (b) uses the final N = 1.6e5 D2 checkpoint,
which is NOT gate-verified and cannot be: D2 has no true score, so the GA-GD gates are D1-only
(04_SPEC Sec.5, LADDER_C.md).  It is a DIAGNOSTIC PROBE on an UN-GATED checkpoint.  The D2
panel licenses no arm claim; 10_SPEC_stageC Sec.3c governs what may.

CAVEAT the picture cannot carry on its own.  The fitted GMM is NOT ground truth on D2 -- D2 has no
closed-form score (05_SPEC Sec.3).  A full-rank mixture cannot represent a density supported near a
low-dimensional set, so its Jacobian stays near the identity and is PSD for free; its lambda_min is
positive but reaches 7.6e-5 (annotated).  Its PSD-ness is therefore not evidence that the learned model
is wrong, only that the two models disagree about the local geometry.
""")


# ------------------------------------------------------------------ F8  data does not fix it ------

def fig8():
    """f(lmin(Jr)<0) and asym(Jr) over the whole 20-point sigma grid, one line per training budget."""
    # The reproducible 20-point re-measurement on the permanent ckpt/d2sx_N160000_a1.pt was still
    # being written when this was first drawn.  Read its state now instead of quoting a stale count:
    # a partial curve is not plotted, but the caption says how far it has got and what it says there.
    fin = jacpsd("D2_final")["diffusion"]
    fin_txt = (f"{len(fin['sigma'])} of 20 grid points written at draw time, and on those it reads "
               f"f = {', '.join(f'{v:.3f}' for v in fin['f_neg_r'])}")
    runs = [("D2 learned  N=1e4   (200 ep.)", "tab:blue", "o", "-", jacpsd("N10000_a1")["diffusion"]),
            ("D2 learned  N=4e4   (200 ep.)", "tab:green", "s", "-", jacpsd("N40000_a1")["diffusion"]),
            ("D2 learned  N=1.6e5 (ep. 240)", "tab:purple", "^", "-", jacpsd("N160000")["diffusion"]),
            ("D2 learned  N=1.6e5 (later snap.)", "tab:pink", "v", "--",
             jacpsd("N160000_late")["diffusion"]),
            ("D2 fitted GMM  b*=kron, K=512", "tab:orange", "D", ":",
             jacpsd("N10000_a1")["GMM-exact(b*=kron,K=512)"]),
            ("D1 learned  N=1.6e5 (gate-PASS)", "tab:red", "*", "-.",
             jacpsd("D1_N160000")["diffusion"])]

    fig, axes = plt.subplots(2, 1, figsize=(5.8, 5.6), sharex=True,
                             gridspec_kw=dict(hspace=0.10))
    for lab, col, mk, ls, d in runs:
        axes[0].plot(d["sigma"], d["f_neg_r"], marker=mk, color=col, ls=ls, ms=3.6, lw=1.3, label=lab)
        axes[1].semilogy(d["sigma"], d["asym_r"], marker=mk, color=col, ls=ls, ms=3.6, lw=1.3)
    for ax in axes:
        ax.set_xscale("log")
        ax.set_xticks([0.03, 0.05, 0.1, 0.2, 0.4, 0.8])
        ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
        ax.xaxis.set_minor_formatter(NullFormatter())
    axes[0].set_ylim(-0.07, 1.14)
    axes[0].set_ylabel(r"$f(\lambda_{\min}(J_r) < 0)$" "\n" "over n=128 held-out samples")
    axes[0].axhline(0.0, color="0.4", lw=0.8, ls=(0, (1, 3)))
    axes[0].text(0.30, 0.055, "PSD at every sample", fontsize=6.8, color="0.35")
    axes[0].legend(loc="lower left", bbox_to_anchor=(0.012, 0.13), fontsize=6.5, frameon=True,
                   framealpha=0.9, edgecolor="none")   # clear of the two curves that sit AT f = 0
    axes[1].set_ylabel(r"$\mathrm{asym}(J_r)=\|J_r-J_r^{\!\top}\|\,/\,\|J_r\|$")
    axes[1].set_xlabel(r"noise level $\sigma$  (the frozen 20-point grid)")
    axes[1].set_ylim(1e-17, 6.0)
    axes[1].set_yticks([1e-16, 1e-12, 1e-8, 1e-4, 1e0])
    axes[1].text(0.055, 3e-13, "machine precision: the FITTED GMM's\nscore is symmetric by construction",
                 fontsize=6.5, color="tab:orange")
    axes[0].set_title("16x the data and a later epoch do not restore PSD-ness on D2;\n"
                      "the same code and budget on D1 is valid everywhere", fontsize=8.8)
    _foot(fig, "D1 and D2 have their own frozen sigma grids (0.0329-0.791 and 0.0331-0.845); each curve "
               "is drawn against its OWN grid.\nD1's $f(\\lambda_{\\min}<0)$ is 0.000 at all 20 points, but "
               "its $\\mathrm{asym}(J_r)$ is NOT zero -- it rises from 1.9e-3 to 9.8e-2.\nThe learned D1 "
               "Jacobian is PSD everywhere and only approximately symmetric, which is why both panels "
               "are drawn.", y=0.015)
    return _save(fig, "F8_budget_psd_asym", """
F8.  Two validity diagnostics of the learned Jacobian over the whole frozen 20-point sigma grid, one
line per training budget.

PLOTTED.  Top: f(lambda_min(J_r) < 0), the fraction of held-out samples whose symmetrised real
Jacobian has a negative eigenvalue.  Bottom (log scale): asym(J_r), the relative asymmetry of J_r.
Both are required of a true posterior-mean denoiser, for which J_r = Cov(h|q)/sigma^2 is symmetric PSD.
n = 128 held-out samples per grid point for every curve.

THE MESSAGE, WITH ITS RANGE.  Over sigma <= 0.26 -- which contains the whole band F9 measures the
site to be damaged in -- the four D2 learned curves lie on top of each other at f = 0.95 to 1.00:
N = 1e4 -> 4e4 -> 1.6e5 is a 16x increase in data and moves neither quantity, and the later epoch
snapshot at N = 1.6e5 changes neither.  They do NOT coincide at large sigma, and the panel shows it:
at sigma = 0.713 the four read 0.711 / 0.203 / 0.422 / 0.359 and at sigma = 0.845 they read 0.594 /
0.633 / 0.359 / 0.570.  That spread is not ordered by budget, it is at the sigma where the damage has
already vanished, and it is drawn rather than smoothed over.  What no budget changes is that f is
pinned near 1 across the whole damaged band.  The fitted GMM sits at f = 0 and at machine-precision
asymmetry -- but it is a FIT selected by validation log-likelihood, NOT ground truth: D2 has no
closed-form prior (05_SPEC Sec.3), and a full-rank mixture is symmetric PSD for free.  It is a sanity
reference for the measurement, not a target the learned model failed to reach.  D1's learned model --
SAME architecture, SAME recipe, SAME budget -- sits at f = 0 too.  The one thing that differs between
the D1 and D2 learned curves is the data distribution.

SOURCE.  logs/jacpsd_N10000_a1.log, jacpsd_N40000_a1.log, jacpsd_N160000.log, jacpsd_N160000_late.log,
jacpsd_D1_N160000.log.  The GMM reference is the block those logs head "GMM-exact(b*=kron,K=512)" in
the N=1e4 log; it is identical in all four D2 logs because the fit is the same object.  That heading
means the EXACT SCORE OF A FITTED mixture, not an exact prior -- the newer logs spell it
"FITTED-GMM(b*=kron,K=512,N=10000)", and this figure uses the newer wording.

EPOCH LABELS, AND A PROVENANCE LIMIT THE PANEL CANNOT SHOW.  The two N = 1.6e5 curves are the
epoch-240 snapshot (logs/jacpsd_N160000.log) and a later snapshot of the SAME run
(logs/jacpsd_N160000_late.log).  BOTH were measured against session-scoped TEMP-DIRECTORY checkpoint
files (/tmp/.../d2sx_N160000_snap.pt and _late.pt), which the 18:20 audit flagged as IRREPRODUCIBLE:
the checkpoints no longer exist, so these two rows can be read but not re-run.  The only record of the
later snapshot's epoch is STATUS.md line 489, naming the best-val checkpoint at epoch 816 when the
probe was launched, which is why the figure says "later snap." rather than a number.  The run has
since finished (patience, 1784 epochs) onto the permanent ckpt/d2sx_N160000_a1.pt, and the
reproducible re-measurement on it is what F7(b) draws.  The matching 20-point jacpsd re-measurement
(logs/jacpsd_D2_final.log) was still running when this figure was drawn, so it is NOT plotted here
rather than plotted as a partial curve: """ + fin_txt + """, i.e. on top of the curves that ARE drawn.
Redraw this figure once that log reaches 20 rows.

GATE STATUS.  All four D2 curves are DIAGNOSTIC PROBES on UN-GATED checkpoints: ckpt/d2sx_N10000_a1.pt
fails the pre-registered gates (GC 0.224 vs 0.15) and the two N = 1.6e5 snapshots are not gate-verified.
The D1 curve uses ckpt/sx_N160000_D1.pt, which PASSES all four gates.

HONESTY NOTE that the top panel alone would hide.  D1's f(lambda_min < 0) is exactly 0.000 at all 20
points, but D1's asym(J_r) is NOT zero: it rises monotonically from 1.9e-3 at sigma = 0.033 to 9.8e-2
at sigma = 0.791.  The learned D1 Jacobian is PSD everywhere and only approximately symmetric.  That is
why both panels are drawn.
""")


# ------------------------------------------------------------------ F9  the sigma band -------------

def fig9():
    """Where on the sigma grid the site is damaged, against where on the SNR grid the receiver diverges."""
    d = jacpsd("N10000_a1")["diffusion"]
    g = jacpsd("N10000_a1")["GMM-exact(b*=kron,K=512)"]
    band = d["sigma"][d["shift_med"] >= d["shift_med"].max() / 2.0]        # measured, not chosen
    lo, hi = band.min(), band.max()
    frac = settling()
    sq = sigma_of_snr()

    fig = plt.figure(figsize=(5.9, 6.3))
    gs = fig.add_gridspec(2, 1, height_ratios=[2.75, 2.0], hspace=0.46)
    g0 = gs[0].subgridspec(2, 1, height_ratios=[0.78, 2.0], hspace=0.34)
    axr = fig.add_subplot(g0[0])
    ax = fig.add_subplot(g0[1], sharex=axr)
    axb = fig.add_subplot(gs[1])

    # --- the ruler: the sigma_t the receiver ACTUALLY queries, per SNR (separate n=12 probe)
    blend = blended_transform_factory(axr.transData, axr.transAxes)
    for i, (snr, (med, q_lo, q_hi)) in enumerate(sorted(sq.items(), reverse=True)):
        y = 0.88 - 0.155 * i
        axr.plot([q_lo, q_hi], [y, y], transform=blend, color="0.5", lw=1.2, solid_capstyle="butt")
        axr.plot([med], [y], transform=blend, marker="o", ms=3.4, color="0.15")
        axr.text(q_hi * 1.10, y, f"{int(snr):+d} dB", transform=blend, fontsize=6.3, va="center",
                 color="0.2")
    axr.axvspan(lo, hi, color="tab:red", alpha=0.10, lw=0)
    axr.set_yticks([])
    axr.tick_params(labelbottom=False, bottom=False)
    axr.set_ylabel("SNR", fontsize=7, rotation=0, ha="right", va="center", labelpad=4)
    axr.set_title(r"median $\sigma_t$ Module H is actually queried with, per SNR"
                  "   (n=12 trials, separate probe; bar = full min..max)", fontsize=7.2, pad=3,
                  color="0.25")

    ax.axvspan(lo, hi, color="tab:red", alpha=0.10, lw=0)
    ax.loglog(d["sigma"], d["shift_med"], marker="o", color="tab:blue", ms=3.8, lw=1.4,
              label="learned score, N=1e4 (the settling run's ckpt)")
    ax.loglog(g["sigma"], np.maximum(g["shift_med"], 1e-7), marker="D", color="tab:orange", ms=3.4,
              lw=1.2, ls=":", label="fitted GMM b*=kron, K=512 (6 exact zeros floored to $10^{-7}$)")
    ax.set_xlim(0.026, 2.6)
    ax.set_ylim(1e-7, 60)
    ax.set_xticks([0.03, 0.05, 0.1, 0.2, 0.4, 0.8])
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.set_xlabel(r"noise level $\sigma$  (frozen 20-point grid)", labelpad=1)
    ax.set_ylabel("median PSD-repair shift of\nthe D-14 site,  shift_med")
    ax.set_title(f"(a) where the site is damaged: shift_med peaks on "
                 f"$\\sigma\\in[{lo:.3f},\\,{hi:.3f}]$", fontsize=8.6)
    ax.legend(loc="lower right", fontsize=6.5, frameon=True, framealpha=0.9, edgecolor="none")
    ax.text(lo * 1.02, 26, "shaded: shift_med within 2x of its maximum", fontsize=6.3,
            color="tab:red")

    for arm, col, mk, lab in (("dscore|eta", "tab:blue", "o", "eta  (D-14 matrix site as spec'd)"),
                              ("dscore|abs1e-2", "tab:green", "s", r"abs1e-2  ($|\lambda|$ floored, SIGN KEPT)"),
                              ("dscore|psd1e-2", "tab:purple", "^", "psd1e-2  (eig clipped into [1e-2,1])"),
                              ("dscore|belsc", "tab:brown", "v", "belsc  (D-14 dropped, scalar site)")):
        axb.plot(SNRS, frac[arm], marker=mk, color=col, ms=4.2, lw=1.4, label=lab)
    axb.axvline(6, color="tab:red", lw=0.9, ls="--", alpha=0.7)
    axb.text(6.3, 0.055, "eta peaks at +6 dB\n(abs1e-2 peaks at 0 dB)", fontsize=6.8,
             color="tab:red")
    axb.set_xlabel("SNR [dB]")
    axb.set_ylabel("fraction of trials with channel\nNMSE > 1 after 16 iterations")
    axb.set_ylim(-0.035, 0.80)
    axb.set_xticks(SNRS)
    axb.set_title("(b) what it costs the receiver: settling experiment,\nD2 cell C2, n=256 paired trials",
                  fontsize=8.6)
    axb.legend(loc="upper right", fontsize=6.5, frameon=True, framealpha=0.9, edgecolor="none",
               title="learned score, Module H site =", title_fontsize=6.5)
    _foot(fig, "(a) and (b) have DIFFERENT x quantities and are NOT forced onto one axis.  The only link "
               "drawn is the ruler above (a):\nthe median $\\sigma_t$ the receiver queries at each SNR, "
               "measured separately at n=12 (logs/diag_sigma_coverage.log);\ngrey bars are the FULL "
               "min..max of the 192 queries, NOT an inter-quartile range.\n+12 dB was not measured "
               "there, so it has no row.", y=0.012)
    return _save(fig, "F9_sigma_band_vs_snr", """
F9.  The sigma band where the D-14 site is damaged, and the SNR band where the receiver diverges.

PLOTTED.
(a) shift_med, the median shift the PSD repair has to apply to the D-14 site, over the frozen 20-point
    sigma grid, for the learned score at N = 1e4 and for the FITTED 512-component Kronecker GMM
    (log-log; the GMM's exact zeros at the SIX smallest sigma -- k = 0..5, sigma 0.0331 to 0.0776 --
    are floored to 1e-7 so a log axis can show them, which is stated here rather than hidden).  The
    GMM is a fit selected by validation log-likelihood, NOT ground truth: D2 has no closed-form prior
    (05_SPEC Sec.3).  The shaded band is sigma where shift_med is within a
    factor 2 of its maximum -- a rule applied in the code, not a band drawn by eye.
(b) fraction of trials whose channel-estimate NMSE exceeds 1 after 16 iterations (NMSE > 1 = worse than
    h_hat = 0), against SNR, for the four interventional arms of the settling experiment: the site as
    specified, the magnitude-floored site that KEEPS the sign, the PSD-clipped site, and the scalar
    site.  n = 256 paired trials per SNR, D2 cell C2 (8x4, T = 16, Tp = 4).

THE CORRESPONDENCE, AND ITS LIMIT.  The two panels' x axes are different physical quantities and the
figure does NOT map one onto the other.  The only link drawn is the ruler on top of (a): the median
sigma_t that Module H is actually queried with at each SNR, measured in a separate and much smaller
diagnostic (logs/diag_sigma_coverage.log, n = 12 trials per point, same cell, same checkpoint), with the
grey bars giving the FULL min..max of the 12 x 16 = 192 queried sigma_t -- that is what the log prints,
it is NOT an inter-quartile range, and it is therefore the widest possible reading of the spread.  Read together: +6 dB lands inside the shaded band, and +6 dB
is where (b)'s eta arm peaks.  (The magnitude-floored arm abs1e-2 peaks at 0 dB, not +6; the marked peak is
the arm that runs the site as specified.)  +12 dB was not measured in the sigma_t diagnostic and
therefore has no tick.
n = 12 is small; this is a consistency check, not a fitted relationship.

SOURCE.  (a) logs/jacpsd_N10000_a1.log, n = 128 held-out samples per grid point.  (b)
results/settling_D2.txt, second block, n = 256; the same numbers with more columns are in
logs/psd_cf_snr*.log.  Ruler: logs/diag_sigma_coverage.log, n = 12.

GATE STATUS.  Every row of this figure uses ckpt/d2sx_N10000_a1.pt, which FAILED the pre-registered
gates (GC 0.224 against a bar of 0.15).  These are DIAGNOSTIC PROBES on an UN-GATED checkpoint.  They
may not enter a result table and they license no claim; 10_SPEC_stageC Sec.6/6c specifies the
confirmatory run with a gate-passing checkpoint at n >= 2560.
""")


# ------------------------------------------------------------------ F10  the D1 confirmatory ------

_ARMS = [
    ("R1-turbo", "R1  classical turbo (APP feedback, no LOO)", "tab:brown", "s", "--"),
    ("R2-ours-G", "R2  D-15+LOO, Gaussian sample-cov. prior", "tab:blue", "o", "-"),
    ("M-ours-bstar", "M   Module H = GMM, b* (val. log-lik.)", "tab:red", "D", "-"),
    ("M-ours-score", "M   EXACT-score ORACLE (true prior, not learned)", "tab:green", "P", ":"),
    ("M-ours-dscore-C-V0", "V0  learned score, D-14 MATRIX site (primary)", "tab:purple", "^", "-"),
    ("M-ours-dscore-C-V4", "V4  learned score, D-13 scalar site (post-hoc)", "tab:pink", "v", "-"),
    ("R5-genie", "R5  genie CSI (lower bound)", "k", "*", "-."),
]


def fig10(n=2560):
    cells = [("C5", r"(a) C5  $T_p=3$"), ("C2", r"(b) C2  $T_p=4$  (headline)"),
             ("C1", r"(c) C1  $T_p=2$  (first pass uninformative)")]
    gd, floor = guard(), 0.5 / n
    band_lab = ["SNR where a pre-registered pair is\nUNDECIDED (power guard)"]   # used once, then cleared
    fig, axes = plt.subplots(1, 3, figsize=(9.6, 3.5), sharey=True)
    for ax, (cell, ttl) in zip(axes, cells):
        A = tableA(cell)
        und_pairs, und_snr = undecided(cell)
        for s in sorted(und_snr):
            ax.axvspan(s - 0.55, s + 0.55, color="0.75", alpha=0.35, lw=0,
                       label=band_lab.pop() if band_lab else None)
        for arm, lab, col, mk, ls in _ARMS:
            if arm not in A:
                continue
            ax.semilogy(SNRS, np.maximum(A[arm], floor), marker=mk, color=col, ls=ls, ms=4, lw=1.3,
                        label=lab if cell == "C5" else None)
        for (c, s, arm), (f, of) in gd.items():
            if c == cell and arm in dict((a[0], a) for a in _ARMS) and f == of:
                ax.plot(s, min(max(A[arm][list(SNRS).index(s)], floor), 1.0), marker="o", ms=11,
                        mfc="none", mec="tab:red", mew=1.4, ls="none",
                        label="divergence guard fired in ALL 2560 trials"
                        if cell == "C1" and arm == "M-ours-dscore-C-V0" else None)
        ax.axhline(0.1, color="0.4", lw=0.8, ls=(0, (1, 3)))
        ax.set_xlabel("SNR [dB]")
        ax.set_xticks(SNRS)
        ax.set_title(ttl, fontsize=9)
        ax.set_ylim(1.2e-4, 1.6)
        if und_pairs:
            ax.text(0.44, 0.26, f"{len(und_pairs)} UNDECIDED pair(s)\n(listed in the caption file)",
                    transform=ax.transAxes, fontsize=6.2, color="0.3")
    axes[0].set_ylabel("BLER after 16 iterations")
    axes[2].annotate("every learned arm collapses here:\nV0 1.000, V1 0.996, V4 0.945,\nguard 2560/2560",
                     xy=(-3, 1.0), xytext=(0.6, 4e-3), fontsize=6.6, color="tab:red",
                     arrowprops=dict(arrowstyle="->", color="tab:red", lw=0.9))
    hs, ls_ = [], []
    for ax in axes:
        for h, l in zip(*ax.get_legend_handles_labels()):
            if l not in ls_:
                hs.append(h); ls_.append(l)
    fig.legend(hs, ls_, loc="center left", bbox_to_anchor=(0.995, 0.5), frameon=False)
    fig.suptitle("D1 confirmatory run, n=2560 per point: $8\\times4$ MIMO, QPSK, rate-1/2 "
                 "$(133,171)_8$, $T=16$, 16 iterations", fontsize=8.8, y=1.03)
    _foot(fig, "BLER exactly 0 is drawn at the 0.5/n floor = 1.95e-4, not at the axis edge.  The power "
               "guard is a PAIR-level verdict, so the grey bands mark the decision SNRs of the "
               "UNDECIDED pairs, not individual curve points.", y=-0.03)

    lines = []
    for cell, _ in cells:
        p, _ = undecided(cell)
        lines.append(f"  cell {cell}: " + ("none" if not p else ""))
        lines += [f"      {nm}   decision SNRs {[int(x) for x in ds]} dB" for nm, ds in p]
    return _save(fig, "F10_bler_D1_confirmatory", """
F10.  The D1 confirmatory BLER run.

PLOTTED.  BLER after 16 outer iterations against SNR, n = 2560 trials per point, for cells C5 (Tp = 3),
C2 (Tp = 4) and C1 (Tp = 2).  Arms: R1-turbo, R2-ours-G, M-ours-bstar, M-ours-score (the EXACT-score
oracle on the true prior -- not a learned prior, and no learned-prior claim follows from it),
M-ours-dscore-C-V0 (learned score through the D-14 matrix site, the Stage C primary) and
M-ours-dscore-C-V4 (the same model through the D-13 belief scalarisation), and R5-genie.  A BLER of
exactly 0 is drawn at the 0.5/n floor (1.95e-4); the axis is not truncated to hide it.

WHAT IS MARKED.
  - Grey bands: the decision SNRs of the arm pairs that the pre-registered power guard left UNDECIDED
    (>= 3 decision points AND >= 6 discordant pairs at >= 2 of them; otherwise no significance call is
    made, 08_SPEC Sec.2).  The guard is a PAIR-level verdict, so a band marks SNRs at which a
    comparison was not decided -- it does not mean the plotted BLER values are uncertain.  The pairs:
""" + "\n".join(lines) + """
  - Red rings: points where the (F3) divergence guard, DIVERGE_NMSE = 10.0, fired in ALL 2560 trials.
    That is C1 / -3 dB only, for V0 (drawn at BLER 1.000) and V4 (at 0.945); the two rings overlap
    because those values are 0.02 of a decade apart.  V1 is 2560/2560 there too but is not plotted.
    NOT RINGED, and said here because the all-2560 ring rule would otherwise hide it: the guard also
    fired at C1 / +3 dB for V0, in 11 of 2560 trials (rate 0.004, worst NMSE 3.6e5).  Those four rows
    are the whole of results/guard_D1_C.txt; the other eleven arms never fired anywhere in this run.
  - Cell C1 at -3 dB is the failure it looks like.  M-ours-dscore-C-V0 is at BLER 1.000 with the guard
    firing 2560/2560 and a worst NMSE of 4.5e18; V1 (not plotted, identical to V0 elsewhere) is at
    0.996 with 2560/2560 and 1.7e20; V4 is at 0.945 with 2560/2560 and 1.4e84, and 3 of its 2560 blocks
    carry a non-finite BLER@16, which are KEPT and counted as block errors.  The non-learned arms at the
    same point are at 0.66-0.84.  "Every learned arm is at BLER 1.0" is the right story only for V0;
    V1 and V4 are at 0.996 and 0.945, and the annotation gives all three.

SOURCE.  results/tables_D1_C.txt -- TABLE A for the BLER values, TABLE B for the power-guard verdicts.
results/guard_D1_C.txt for the divergence-guard firings.  n = 2560 per SNR in all three cells.

GATE STATUS.  The Stage C arms use ckpt/sx_N160000_D1.pt, which PASSES all four pre-registered gates
(LADDER_C.md SX160000: GA 9.879e-16, GB +0.27%, GC 0.0999, GD 0.0718).  This is a gate-passing
confirmatory run, not a probe.

THE STANDING CAVEAT ON THIS TESTBED, from the file's own header.  D1 is CIRCULAR: its true prior is
defined as a grid GMM, so the GMM arm is correctly specified by construction.  No claim about learned
priors transfers from this table to D2.
""")


# ------------------------------------------------------------------ F11  the D2 confirmatory ------

# Arms of the D2 confirmatory figure.  figures.py's STYLE is reused where it already names an arm
# (R1/R2/M-b*/R5) so F11 matches F3/F10; the Stage C arms it does not know are added here only.
_ARMS_D2 = [
    ("R1-turbo",            "R1   classical turbo (APP feedback, no LOO)",      "tab:brown",  "s",  "--"),
    ("R2-ours-G",           "R2   D-15+LOO, Gaussian sample-cov. prior",        "tab:blue",   "o",  "-"),
    ("M-ours-bstar",        "M    Module H = GMM, b* (val. log-lik.), N=1e4",   "tab:red",    "D",  "-"),
    ("M-ours-bstar-scalar", "M    b* GMM through V4's wiring (CONTROL)",        "tab:orange", "d",  "--"),
    ("M-ours-dscore-C-V0",  "V0   learned score, D-14 matrix site (PRE-REG.)",  "tab:purple", "^",  "-"),
    ("M-ours-dscore-C-V1",  "V1   V0 + symmetric-PSD projection of the site",   "tab:green",  "s",  "-"),
    ("M-ours-dscore-C-V4",  "V4   D-13 belief scalarisation (post-hoc reg.)",   "tab:pink",   "v",  "-"),
    ("M-ours-dscore-C-V4b", "V4b  as V4 but scal=site (side report)",           "tab:olive",  "<",  ":"),
    ("R5-genie",            "R5   genie CSI (lower bound)",                     "k",          "*",  "-."),
]
_GUARD_HI = 0.5          # "fired at a high rate": the point is a diverging receiver, not a BLER


def fig11(n=2560):
    """D2 confirmatory BLER, C2 main + C5/C1 beside it, with the divergence guard and the power
    guard's UNDECIDED verdicts drawn on top of the curves."""
    tabA = os.path.join(RES, "tables_D2_C.txt")
    cells = [("C2", r"(a) C2  $T_p=4$  — CLAIM cell", 1.45),
             ("C5", r"(b) C5  $T_p=3$", 1.0),
             ("C1", r"(c) C1  $T_p=2$", 1.0)]
    gd, floor = guard(os.path.join(RES, "guard_D2_C.txt")), 0.5 / n
    plotted = {a[0] for a in _ARMS_D2}
    BAND = "SNR of a comparison the power guard\nleft UNDECIDED (no significance call)"
    HI = (f"divergence guard fired in > {_GUARD_HI:.0%} of trials at this point:\n"
          f"the receiver DIVERGED — this is not an ordinary BLER")
    LO = "divergence guard fired in some (but not most) trials"
    band_lab, hi_lab, lo_lab = [BAND], [HI], [LO]

    fig = plt.figure(figsize=(11.2, 4.6))
    gs = fig.add_gridspec(1, 3, width_ratios=[c[2] for c in cells], wspace=0.07)
    axes = [fig.add_subplot(gs[0, i]) for i in range(3)]
    for ax, (cell, ttl, _) in zip(axes, cells):
        main = cell == "C2"
        A = tableA(cell, tabA)
        und_pairs, und_snr = undecided(cell, tabA)
        for s in sorted(und_snr):
            ax.axvspan(s - 0.75, s + 0.75, color="0.72", alpha=0.32, lw=0, zorder=0,
                       label=band_lab.pop() if band_lab else None)
        for arm, lab, col, mk, ls in _ARMS_D2:
            if arm not in A:
                continue
            y = np.maximum(A[arm], floor)
            rate = np.array([gd.get((cell, s, arm), (0, n))[0] / n for s in SNRS])
            # red halo along the part of the curve where the receiver was diverging
            ax.semilogy(SNRS, np.where(rate > _GUARD_HI, y, np.nan), color="tab:red", lw=5.5,
                        alpha=0.20, solid_capstyle="round", zorder=1)
            ax.semilogy(SNRS, y, marker=mk, color=col, ls=ls, ms=5.0 if main else 3.8,
                        lw=1.7 if main else 1.2, zorder=3, label=lab if main else None)
            for s, yy, r in zip(SNRS, y, rate):
                if r <= 0:
                    continue
                big = r > _GUARD_HI
                ax.plot(s, yy, marker="o", ms=12 if big else 6.5, mfc="none", mec="tab:red",
                        mew=1.5 if big else 0.9, ls="none", zorder=4,
                        label=(hi_lab.pop() if big and hi_lab else
                               lo_lab.pop() if not big and lo_lab else None))
        ax.axhline(0.1, color="0.4", lw=0.8, ls=(0, (1, 3)), zorder=2)
        ax.set_xlabel("SNR [dB]")
        ax.set_xticks(SNRS)
        ax.set_title(ttl, fontsize=9, fontweight="bold" if main else "normal")
        ax.set_ylim(1.2e-4, 2.4)
        ax.set_xlim(-5.2, 17.2)
        if not main:
            ax.set_yticklabels([])
        if not und_pairs:
            note = "power guard: no UNDECIDED pair in this cell"
        elif all(p.endswith("R5-genie") for p, _ in und_pairs):
            note = f"UNDECIDED: all {len(und_pairs)} arm $\\to$ R5-genie pairs"
        else:
            note = "UNDECIDED: " + ", ".join(p.replace("M-ours-", "") for p, _ in und_pairs)
        ax.text(0.5, 0.015, note + "\n(pairs and decision SNRs in the caption file)",
                transform=ax.transAxes, fontsize=5.8, color="0.30", va="bottom", ha="center")
    axes[0].set_ylabel("BLER after 16 iterations")

    # --- the three things the reader must get without the caption -------------------------------
    a0 = axes[0]
    a0.annotate("V0 — the PRE-REGISTERED wiring —\nis WORSE than classical turbo (R1)\nat every SNR of the claim cell",
                xy=(6, 0.950), xytext=(2.4, 0.115), fontsize=6.8, color="tab:purple", ha="left",
                va="bottom", arrowprops=dict(arrowstyle="->", color="tab:purple", lw=1.0))
    a0.annotate("V1 / V4 — the repaired wiring —\nare the lowest NON-GENIE arms here\n(b* GMM 0.252 $\\to$ V1 0.145; V4b alongside)",
                xy=(0, 0.034), xytext=(-4.9, 3.4e-4), fontsize=6.8, color="tab:green", ha="left",
                va="bottom", arrowprops=dict(arrowstyle="->", color="tab:green", lw=0.9, ls=":",
                                             shrinkB=5, connectionstyle="arc3,rad=-0.25"))
    axes[2].annotate("that ordering does NOT hold on C1:\nV1/V4 are not better than the b* GMM\n"
                     "(TABLE B: not significant), and at $-$3 dB\nevery learned arm diverges (2560/2560)",
                     xy=(-3, 0.979), xytext=(0.6, 1.3e-2), fontsize=6.8, color="0.15", ha="left",
                     va="bottom", arrowprops=dict(arrowstyle="->", color="0.35", lw=0.9, ls=":",
                                                  shrinkB=9, connectionstyle="arc3,rad=0.30"))
    a0.text(-5.0, 0.052, "BLER = 0.1", fontsize=6.4, color="0.4", ha="left", va="center")

    H = {}
    for ax in axes:
        H.update(dict(zip(*reversed(ax.get_legend_handles_labels()))))
    order = [a[1] for a in _ARMS_D2] + [HI, LO, BAND]
    fig.legend([H[l] for l in order if l in H], [l for l in order if l in H],
               loc="center left", bbox_to_anchor=(0.995, 0.5), frameon=False)
    fig.suptitle("D2 CONFIRMATORY run (CLAIM testbed, sparse specular), n=2560 per point: $8\\times4$ "
                 "MIMO, QPSK, rate-1/2 $(133,171)_8$, $T=16$, 16 outer iterations", fontsize=8.8, y=1.00)
    _foot(fig, "NOT an equal-budget comparison: the learned arms V0/V1/V4 train on N'=1.6e5 channels "
               "(ckpt/d2sx_N160000_a1.pt, no gate record), the GMM arms fit N=1e4.\nThe learned-vs-GMM "
               "contrast is therefore SECONDARY; the primary contrast is the WIRING, V0 vs V1/V4 at the "
               "same checkpoint and budget.\nThe pre-registered arm M-ours-dscore stays BLOCKED in the "
               "pre-registered table.  BLER exactly 0 is drawn at the 0.5/n floor = 1.95e-4.",
          y=0.005)

    # ---- caption file: everything marked above, listed from the two source files -----------------
    und_lines = []
    for cell, _, _ in cells:
        p, _ = undecided(cell, tabA)
        und_lines.append(f"    cell {cell}: " + ("none" if not p else f"{len(p)} pair(s)"))
        und_lines += [f"        {nm}   decision SNRs {[int(x) for x in ds]} dB" for nm, ds in p]
    hi, lo, other = [], [], []
    for (c, s, arm), (f, of) in sorted(gd.items()):
        row = f"        {c}  {int(s):+3d} dB  {arm:22s} {f}/{of} = {f / of:.3f}"
        (other if arm not in plotted else hi if f / of > _GUARD_HI else lo).append(row)
    return _save(fig, "F11_bler_D2_confirmatory", """
F11.  The D2 confirmatory BLER run -- the CLAIM testbed.

PLOTTED.  BLER after 16 outer iterations against SNR, n = 2560 trials per point, cell C2 (Tp = 4) as the
main panel with C5 (Tp = 3) and C1 (Tp = 2) beside it, so the pilot-budget dependence is visible.  Nine
arms: R1-turbo, R2-ours-G, M-ours-bstar, M-ours-bstar-scalar, M-ours-dscore-C-V0, -C-V1, -C-V4, -C-V4b,
R5-genie.  A BLER of exactly 0 is drawn at the 0.5/n floor (1.95e-4); the axis is not truncated.

THE THREE THINGS THE FIGURE IS DRAWN TO SHOW, all from TABLE A of results/tables_D2_C.txt:
  (a) On C2, M-ours-dscore-C-V0 -- the PRE-REGISTERED score wiring -- is above classical turbo at every
      SNR: 0.593 / 0.845 / 0.954 / 0.950 / 0.909 / 0.818 / 0.446 against R1-turbo's 0.537 / 0.213 /
      0.079 / 0.041 / 0.025 / 0.019 / 0.009.  The same holds at every SNR of C1 and at six of the seven
      SNRs of C5; the one exception in the whole figure is C5 / -3 dB, where V0 is 0.769 against
      R1-turbo's 0.795.
  (b) On C2, V1, V4 and V4b occupy the three lowest non-genie positions at EVERY SNR, clear of the
      fourth-placed arm at all seven (at -3 dB: V1 0.145, V4 0.154, V4b 0.161, then M-ours-bstar 0.252
      and R2-ours-G 0.329; at +9 dB: 0.003 / 0.003 / 0.003, then 0.008).  Which of the three is lowest
      is NOT resolved by this figure: V1 is lowest at five of the seven SNRs, V4 at +3 dB (0.008
      against V1's 0.011), and at +6 dB all three print 0.006.  R5-genie is at or below them at every
      SNR (0.034 at -3 dB), and at +15 dB the table prints 0.001 for both genie and V1.
  (c) On C1 that ordering does not hold.  At -3 dB V1 is 0.979 and V4 0.953 against M-ours-bstar's
      0.778 and R1-turbo's 0.918.  TABLE B's M-ours-bstar -> V1 and M-ours-bstar -> V4 pairs, decided
      on C1 at the anchor's decision SNRs ['+6', '+12', '+15'], are BOTH 'not significant'; the same
      two pairs on C2, decided at ['-3', '+0', '+3'], are significant at 3/3 decision points
      (bstar -> V1 pooled 511:78, p = 5.8e-79).

WHAT IS MARKED.
  - Grey bands: the decision SNRs of the pairs the pre-registered power guard left UNDECIDED (>= 3
    decision points AND >= 6 discordant pairs at >= 2 of them, otherwise no significance call is made,
    08_SPEC Sec.2).  The guard is a PAIR-level verdict: a band marks SNRs at which a comparison was not
    decided, NOT that the plotted BLER values there are uncertain.  On C1 the single UNDECIDED pair is
    between two arms that are not plotted in this figure (R4-llr, R4-scvamp); its band is still drawn
    because the instruction is to mark every UNDECIDED comparison.  The full list:
""" + "\n".join(und_lines) + """
    On C2 every arm-vs-R5-genie comparison is UNDECIDED.  R5-genie is the anchor arm of those pairs and
    its decision-SNR line yields only two SNRs, -3 and +0 dB, instead of the required three: TABLE A
    puts genie at 0.034 and 0.010 there and at 0.005 or below from +3 dB up, i.e. at the edge of and
    then outside the anchor window BLER in [0.005, 0.9].  No arm in this figure is therefore claimed to
    differ from the genie bound on C2, however far apart the two curves look.
  - Red rings and the red halo along a curve: the (F3) Module-H divergence guard (DIVERGE_NMSE = 10.0,
    results/guard_D2_C.txt).  A LARGE ring plus the halo is a point where the guard fired in more than
    50% of the 2560 trials -- the receiver was diverging, and the plotted value is not an ordinary
    error rate.  A small ring is a point where it fired in some but not most trials.  The guard is
    detection and classification only: no arm's trajectory was altered by it.
    Fired in > 50% of trials (large rings + halo):
""" + "\n".join(hi) + """
    Fired in <= 50% of trials (small rings):
""" + "\n".join(lo) + """
    Fired for arms NOT plotted in this figure, so not ringed anywhere above:
""" + ("\n".join(other) if other else "        none") + """
    Arms that never fired the guard anywhere in this raw set: R0-pilot, R1-turbo, R2-ours-G, R4-llr,
    R4-scvamp.  R5-genie has no channel estimate and so no Module H path.
  - Read together with the rings, cell by cell.  On C2, V0 alone fires at a high rate, and it does so
    at EVERY SNR (0.529 to 0.932): the whole V0 curve of the claim panel is a diverging receiver, so
    its BLER is not comparable with the others as an error rate.  On C5, V0 (0.623 to 0.932) and V4b
    (2560/2560 at every SNR) do.  On C1, V0 (0.786 to 1.000) and V4b (2560/2560) fire at every SNR,
    and V1 and V4 fire 2560/2560 in addition at -3 dB.  V1's firing rate on C1 then falls to
    0.000-0.179 from +0 dB up, which is why its C1 curve carries small rings and not large ones.

BUDGETS -- READ THE NUMBERS, NOT THE ARM NAMES (the run header of results/tables_D2_C.txt).
  M-ours-dscore-C-V0 / -C-V1 / -C-V4 : N_train = 160000, rung D2SX160000, ckpt/d2sx_N160000_a1.pt.
  R1-turbo, R2-ours-G, M-ours-bstar, M-ours-bstar-scalar : N_train = 10000 (the ONE channel set).
  R5-genie : n/a, the true H is given.
  M-ours-dscore-C-V4b : the header records N_train = 10000 with the note 'unclassified arm, quoting the
  point's channel-set size'.  That is what the file says; this figure does not resolve it.
  The learned arms therefore have 16x the GMM arms' channel budget.  This is NOT an equal-budget
  comparison, so the learned-vs-GMM contrast is SECONDARY and the primary reading of this figure is the
  WIRING contrast (V0 vs V1/V4 -- same checkpoint, same budget, different Module-H site).
  M-ours-bstar-scalar is the pre-registered MANDATORY CONTROL for exactly that (10_SPEC Sec.3c: the b*
  GMM through V4's EXACT wiring -- 'if scalarisation also helps the GMM, the gain belongs to the SITE,
  not to the learned prior').  The numbers on C2 at -3 dB: b* 0.252, b*-scalar 0.261, V4 0.154, and
  TABLE B's M-ours-bstar -> M-ours-bstar-scalar pair is 'not significant' (pooled 125:149, p = 0.16,
  SNR@0.1 gap +0.04 dB [-0.12, +0.19]).

CHECKPOINT AND GATE STATUS -- stated because it qualifies every learned curve here.
  ckpt/d2sx_N160000_a1.pt.  The run header records: 'NO GATE RECORD mentions d2sx_N160000_a1.pt --
  UNVERIFIED here', and dscore_status 'ABSENT -- no GATE-PASSING checkpoint (04_SPEC Sec.5 gates
  GA-GD): no gate-passing checkpoint for D2; recorded PASS rows: none'.  The pre-registered arm
  M-ours-dscore stays BLOCKED in the pre-registered table and is absent from the raw files of all three
  cells; V0/V1/V4/V4b are the Stage C arms (10_SPEC Sec.3b/Sec.3c) and do not lift that block.

NON-FINITE BLOCKS, kept and counted as block errors, never dropped (the NOTE lines of the source file):
  C1 / -3 dB: V0 1077/2560, V1 294/2560, V4 126/2560 blocks carry a non-finite blk_err@16.  No NOTE
  line exists for C2 or C5.

SOURCE.  results/tables_D2_C.txt -- TABLE A for every BLER value, TABLE B for the power-guard verdicts
and the paired sign tests; results/guard_D2_C.txt for every guard firing.  Both files are dated
2026-09-22 and carry git commit f6062a0.  n = 2560 per SNR in all three cells, 16 outer iterations for
every arm.  Nothing in this figure is recomputed, resampled or re-run from the raw .npz files.

THE STANDING CAVEAT ON THIS TESTBED, from the file's own header.  D2 is the CLAIM testbed: sparse
specular, conditional Gaussianity broken, and the upper bound is the genie only.
""")

def check11():
    """F11 draws nothing it cannot cite, so the claims it makes IN THE FIGURE are asserted against the
    two source files here.  Run by __main__ before fig11; it fails loudly if a re-run of the D2
    confirmatory tables moves a number the figure's annotations assert."""
    tab = os.path.join(RES, "tables_D2_C.txt")
    A = {c: tableA(c, tab) for c in ("C1", "C2", "C5")}
    gd = guard(os.path.join(RES, "guard_D2_C.txt"))
    for c in A:                                   # every plotted arm exists in every cell
        for arm, *_ in _ARMS_D2:
            assert arm in A[c], (c, arm)
    # (a) V0 above classical turbo -- everywhere on C2 and C1, all but -3 dB on C5
    assert all(A["C2"]["M-ours-dscore-C-V0"] > A["C2"]["R1-turbo"]), "(a) C2"
    assert all(A["C1"]["M-ours-dscore-C-V0"] > A["C1"]["R1-turbo"]), "(a) C1"
    assert [i for i in range(7) if A["C5"]["M-ours-dscore-C-V0"][i] <= A["C5"]["R1-turbo"][i]] == [0], "(a) C5"
    # (b) V1/V4/V4b are the three lowest non-genie arms at every C2 SNR, genie at or below them
    ng = [a for a in A["C2"] if a not in ("R5-genie", "R0-pilot", "pilot_C")]
    top3 = {"M-ours-dscore-C-V1", "M-ours-dscore-C-V4", "M-ours-dscore-C-V4b"}
    for i in range(7):
        assert set(sorted(ng, key=lambda a: A["C2"][a][i])[:3]) == top3, ("(b)", i)
    assert all(A["C2"]["R5-genie"] <= A["C2"]["M-ours-dscore-C-V1"]), "(b) genie"
    # (c) the ordering is gone on C1
    assert A["C1"]["M-ours-dscore-C-V1"][0] > A["C1"]["M-ours-bstar"][0], "(c)"
    # rings account for every guard row; the 2 unplotted ones are named in the caption
    pl = {a[0] for a in _ARMS_D2}
    assert sum(k[2] in pl for k in gd) + 2 == len(gd), "guard rows unaccounted for"
    # the UNDECIDED bands
    assert (len(undecided("C2", tab)[0]), undecided("C5", tab)[0], len(undecided("C1", tab)[0])) == (7, [], 1)
    assert undecided("C2", tab)[1] == {-3.0, 0.0} and undecided("C1", tab)[1] == {3.0}
    return "check11 ok"


if __name__ == "__main__":
    print("  ", check11())
    for f in (fig7, fig8, fig9, fig10, fig11):
        try:
            print("  ok  ", f())
        except Exception as ex:
            print("  FAIL", f.__name__, type(ex).__name__, ex)
