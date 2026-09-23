"""conf/code/figures.py -- result figures (08_SPEC_analysis.md §4).

F2 lemma is produced by lemma.py.  This file makes the result figures:
  F3  BLER vs SNR on the headline cell (D2 C2) and on the Tp=2 cell (D2 C1)
  F4  where the channel prior helps: Module H gain vs SNR across the pilot budgets Tp = 2, 3, 4
  F5  sample complexity of the learned score against the pre-registered gate GC
  F6  architecture comparison at EQUAL trials per architecture

Every figure is exported as PDF (for the paper) and PNG (for quick viewing).  Legends carry the condition,
not just the arm name, because a reviewer reads the figure before the text.
"""
import os, sys, csv, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import common as C
import analysis as AN

plt.rcParams.update({"font.size": 9, "axes.labelsize": 9, "legend.fontsize": 7.6,
                     "xtick.labelsize": 8.5, "ytick.labelsize": 8.5, "axes.grid": True,
                     "grid.alpha": 0.25, "figure.dpi": 160, "savefig.bbox": "tight"})
FIG = os.path.join(C.CONF, "figs")
os.makedirs(FIG, exist_ok=True)

STYLE = {                                    # (label incl. condition, colour, marker, linestyle)
    "R0-pilot":     ("R0  pilot-only LMMSE, 1 pass (no turbo loop)", "0.55", "v", ":"),
    "R1-turbo":     ("R1  classical turbo (APP feedback, no LOO)",   "tab:brown", "s", "--"),
    "R2-ours-G":    ("R2  D-15+LOO, Gaussian sample-cov. prior",     "tab:blue", "o", "-"),
    "R3-bigamp":    ("R3  BiG-AMP + BCJR (i.i.d. prior, structural)", "tab:gray", "P", "--"),
    "R4-scvamp":    ("R4  3-module SC-VAMP-type (Onsager interface)", "tab:olive", "X", "--"),
    "M-ours-gmm32": ("M   Module H = GMM, K=32 (literal)",           "tab:orange", "^", "-"),
    "M-ours-bstar": ("M   Module H = GMM, b* (val. log-lik.)",       "tab:red", "D", "-"),
    "R5-genie":     ("R5  genie CSI (known-H reference)",            "k", "*", "-."),
}
ORDER = ["R0-pilot", "R1-turbo", "R3-bigamp", "R4-scvamp", "R2-ours-G", "M-ours-gmm32", "M-ours-bstar", "R5-genie"]


def bler(data, cell, prior, snrs, arm, it=-1):
    return np.array([data[(cell, prior, s)][arm]["blk_err"][:, it].mean() for s in snrs])


def load(tb):
    d, m, warns = AN.load_raw(tb)
    for w in warns:
        print("  [load]", w)
    return d, m


def fig3(tb="D2"):
    d, _ = load(tb)
    pr = C.PRIOR_OF[tb]
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.2), sharey=True)
    for ax, cell, ttl in zip(axes, ("C2", "C1"),
                             (r"(a) headline cell: $T_p=4$", r"(b) $T_p=2$: first pass uninformative")):
        snrs = sorted(k[2] for k in d if k[:2] == (cell, pr))
        n = len(d[(cell, pr, snrs[0])]["R5-genie"]["blk_err"])
        for a in ORDER:
            if a not in d[(cell, pr, snrs[0])]:
                continue
            lab, col, mk, ls = STYLE[a]
            y = bler(d, cell, pr, snrs, a, 0 if a == "R0-pilot" else -1)
            ax.semilogy(snrs, np.maximum(y, 0.5 / n), marker=mk, color=col, ls=ls, ms=4, lw=1.3,
                        label=lab if cell == "C2" else None)
        ax.axhline(0.1, color="0.4", lw=0.8, ls=(0, (1, 3)))
        ax.set_xlabel("SNR [dB]")
        ax.set_title(ttl, fontsize=9)
        ax.set_ylim(3e-3, 1.3)
    axes[0].set_ylabel("BLER after 16 iterations")
    axes[0].text(-2.6, 0.115, "BLER = 0.1", fontsize=7, color="0.4")
    fig.legend(loc="center left", bbox_to_anchor=(1.0, 0.5), frameon=False)
    fig.suptitle(f"{tb}: sparse specular multipath, $8\\times4$ MIMO, QPSK, rate-1/2 $(133,171)_8$, "
                 f"$T=16$, 16 iterations", fontsize=8.6, y=1.04)
    for e in ("pdf", "png"):
        fig.savefig(os.path.join(FIG, f"F3_bler_{tb}.{e}"))
    plt.close(fig)
    return f"F3_bler_{tb}"


def fig4(tb="D2", min_err=15, B=2000):
    """Where the prior helps, WITH uncertainty.  The raw BLER ratio is unusable at high SNR: at BLER ~ 0.006
    and n = 640 a point carries ~4 block errors, so the ratio swings on single events.  We therefore plot a
    PAIRED bootstrap (the two arms share every channel/noise realisation) and draw a point only where BOTH
    arms produced at least `min_err` block errors; points below that are marked on the axis instead of being
    silently dropped."""
    d, m, warns = AN.load_raw(tb)
    for w in warns:
        print("  [load]", w)
    pr = C.PRIOR_OF[tb]
    rng = np.random.default_rng(C.SEED)
    fig, ax = plt.subplots(figsize=(4.6, 3.2))
    for cell, tp, col, mk in (("C1", 2, "tab:blue", "o"), ("C5", 3, "tab:purple", "s"), ("C2", 4, "tab:red", "D")):
        snrs = sorted(k[2] for k in d if k[:2] == (cell, pr))
        if not snrs:
            continue
        xs, ys, lo, hi, weak = [], [], [], [], []
        for sv in snrs:
            g = d[(cell, pr, sv)]["R2-ours-G"]["blk_err"][:, -1]
            b = d[(cell, pr, sv)]["M-ours-bstar"]["blk_err"][:, -1]
            if min(g.sum(), b.sum()) < min_err:
                weak.append(sv)
                continue
            r = [100 * (1 - b[i].mean() / max(g[i].mean(), 1e-9))
                 for i in (rng.integers(len(g), size=len(g)) for _ in range(B))]
            xs.append(sv); ys.append(100 * (1 - b.mean() / g.mean()))
            lo.append(np.percentile(r, 5)); hi.append(np.percentile(r, 95))
        if xs:
            ax.errorbar(xs, ys, yerr=[np.array(ys) - lo, np.array(hi) - np.array(ys)], marker=mk, color=col,
                        ms=4, lw=1.4, capsize=2.5, elinewidth=0.8,
                        label=fr"$T_p={tp}$" + ("  (headline)" if tp == 4 else
                                                "  (first pass uninformative)" if tp == 2 else ""))
        for sv in weak:
            ax.plot(sv, 0, marker="|", color=col, ms=9, mew=1.2)
    ax.axhline(0, color="0.3", lw=0.9)
    ax.set_xlabel("SNR [dB]")
    ax.set_ylabel("BLER reduction of Module H\nover the Gaussian prior [%]")
    ax.set_title("Where a fitted channel prior helps", fontsize=9)
    ax.legend(frameon=False, loc="lower left")
    ax.text(0.99, 0.03, f"bars: 90% paired bootstrap\nticks on 0: fewer than {min_err} block errors,\nratio not estimable",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=6.4, color="0.35")
    for e in ("pdf", "png"):
        fig.savefig(os.path.join(FIG, f"F4_regime_{tb}.{e}"))
    plt.close(fig)
    return f"F4_regime_{tb}"


def fig5():
    rows = sorted(csv.DictReader(open(os.path.join(C.CONF, "results", "samplecx.csv"))),
                  key=lambda r: int(r["N_train"]))
    N = np.array([int(r["N_train"]) for r in rows], float)
    fig, ax = plt.subplots(figsize=(4.3, 3.1))
    for key, tol, col, mk, lab in (("GC", 0.15, "tab:red", "o", r"$G_C$  relative score error"),
                                   ("GB", 0.05, "tab:blue", "s", r"$G_B$  denoising NMSE excess"),
                                   ("GD", 0.20, "tab:green", "^", r"$G_D$  Jacobian error (full matrix)")):
        y = np.array([float(r[key]) for r in rows])
        ax.loglog(N, y, marker=mk, color=col, ms=4.5, lw=1.4, label=lab)
        ax.axhline(tol, color=col, lw=0.8, ls=":")
    sl, ic = np.polyfit(np.log(N), np.log([float(r["GC"]) for r in rows]), 1)
    xs = np.array([N[0], N[-1]])
    ax.loglog(xs, np.exp(ic) * xs ** sl, color="tab:red", lw=0.8, ls="--", alpha=0.6)
    ax.axvline(1e4, color="0.4", lw=0.9)
    ax.text(1.12e4, 0.55, "budget given to\nboth priors", fontsize=6.8, color="0.3")
    ax.text(N[0] * 1.15, 0.155, "pre-registered gates (dotted)", fontsize=6.8, color="0.3")
    ax.set_xlabel(r"training samples $N$")
    ax.set_ylabel("gate quantity (lower is better)")
    ax.set_title(fr"Learned score vs the frozen gates:  $G_C \propto N^{{{sl:.2f}}}$", fontsize=9)
    ax.legend(frameon=False, loc="lower left")
    for e in ("pdf", "png"):
        fig.savefig(os.path.join(FIG, f"F5_samplecx.{e}"))
    plt.close(fig)
    return "F5_samplecx"


def fig6(neq=30):
    o = collections.defaultdict(list)
    for r in csv.DictReader(open(os.path.join(C.CONF, "results", "hpo_strat_trials.csv"))):
        if r["gate_score"] and np.isfinite(float(r["gate_score"])):
            o[r["arch"]].append((int(r["trial"]), float(r["gate_score"])))
    by = {k: np.array([g for _, g in sorted(v)[:neq]]) for k, v in o.items()}
    ks = sorted(by, key=lambda k: by[k].min())
    fig, ax = plt.subplots(figsize=(4.6, 3.1))
    for i, k in enumerate(ks):
        v = by[k]
        ax.scatter(np.full(len(v), i) + np.linspace(-.16, .16, len(v)), v, s=7, alpha=.45,
                   color="tab:blue", edgecolor="none")
        ax.plot([i - .3, i + .3], [v.min()] * 2, color="tab:red", lw=1.8)
        ax.plot([i - .22, i + .22], [np.median(v)] * 2, color="k", lw=1.2)
    ax.axhline(1.0, color="tab:green", lw=1.1, ls="--")
    ax.text(len(ks) - .55, 1.06, "all four gates pass", fontsize=7, color="tab:green")
    ax.set_yscale("log")
    ax.set_xticks(range(len(ks)))
    ax.set_xticklabels(ks)
    ax.set_ylabel("gate score  (max over $G_A..G_D$ of\nvalue / tolerance;  lower is better)")
    ax.set_title(f"Architecture at equal budget: {neq} random trials each", fontsize=9)
    ax.plot([], [], color="tab:red", lw=1.8, label="best of 30")
    ax.plot([], [], color="k", lw=1.2, label="median")
    ax.legend(frameon=False, loc="upper left")
    for e in ("pdf", "png"):
        fig.savefig(os.path.join(FIG, f"F6_arch.{e}"))
    plt.close(fig)
    return "F6_arch"


if __name__ == "__main__":
    for f in (lambda: fig3("D2"), lambda: fig3("D1"), lambda: fig4("D2"), fig5, fig6):
        try:
            print("  ok ", f())
        except Exception as ex:
            print("  FAIL", type(ex).__name__, ex)
