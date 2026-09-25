"""conf/code/figure_f16.py -- F16: representative result figure (report figure; numbers straight from the raw files).

(a) BLER@16 vs SNR on the headline cell D2 C2 at the headline equal budget N_train = 1.6e5 (raw_B16e4k): Gaussian
    sample-covariance prior (R2), GMM b* (kron K=1024, validation log-likelihood), the learned diffusion prior V1, and the
    known-channel reference R5-genie.  95% Wilson intervals.
(b) C2 -3 dB BLER@16 vs the equal training budget N_train (GMM and diffusion prior trained on the SAME channel set):
    1e4 (raw_B1e4), 4e4 (raw_B4e4k), 1.6e5 (raw_B16e4k), 3.2e5 (raw_B32e4last; last-EMA like the others) + the 3.2e5
    _best.pt judging run (raw_B32e4, hollow marker).  1e4 / 4e4 are budget-axis measurements (D1-sibling gate FAIL recipe).
Writes figs/F16_headline_budget.{pdf,png,txt}.  Read-only on the raw files.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from analysis import load_raw

plt.rcParams.update({"font.size": 9, "axes.labelsize": 9, "legend.fontsize": 7.4, "xtick.labelsize": 8.5,
                     "ytick.labelsize": 8.5, "axes.grid": True, "grid.alpha": 0.25, "figure.dpi": 160,
                     "savefig.bbox": "tight"})
FIG = os.path.join(C.CONF, "figs")
ARMS = [("R2-ours-G", "Gaussian prior (sample covariance)", "tab:blue", "o", "-"),
        ("M-ours-bstar", "GMM prior $b^*$ (K by validation log-lik.)", "tab:red", "D", "-"),
        ("M-ours-dscore-C-V1", "learned diffusion prior (proposed, V1)", "tab:green", "s", "-"),
        ("R5-genie", "known-channel reference (R5)", "k", "*", "-.")]


def fails(data, cell, snr, arm):
    k = [x for x in data if x[0] == cell and x[2] == snr][0]
    v = np.asarray(data[k][arm]["blk_err"])[:, -1]
    return np.where(np.isfinite(v), v, 1.0)                  # a raised block is a block error (01_RULES §4)


def wilson(k, n, z=1.96):
    p = k / n; c = p + z * z / (2 * n); h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)); d = 1 + z * z / n
    return (c - h) / d, (c + h) / d


def main():
    raw = lambda t: load_raw("D2", root=os.path.join(C.CONF, f"raw_{t}"))[0]
    H = raw("B16e4k")
    snrs = sorted(k[2] for k in H if k[0] == "C2")
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.6, 3.25), gridspec_kw={"width_ratios": [1.15, 1]})
    txt = ["F16 -- representative result.  Numbers recomputed from the raw files by code/figure_f16.py.", ""]
    txt.append("(a) D2 C2 (8x4, T=16, Tp=4), N_train=1.6e5 equal budget (raw_B16e4k), n=2560 per SNR, BLER@16:")
    for arm, lab, col, mk, ls in ARMS:
        f = [fails(H, "C2", s, arm) for s in snrs]
        k = np.array([x.sum() for x in f]); n = np.array([len(x) for x in f])
        p = k / n; lo, hi = wilson(k, n)
        a1.errorbar(snrs, np.maximum(p, 3e-4), yerr=[np.maximum(p - lo, 0), hi - p], color=col, marker=mk, ls=ls,
                    ms=5 if mk != "*" else 8, lw=1.4, capsize=2, label=lab)
        txt.append(f"  {arm:<20} " + " ".join(f"{int(x)}/{int(m)}" for x, m in zip(k, n)))
    a1.set_yscale("log"); a1.set_ylim(5e-4, 0.6); a1.set_xlabel("SNR [dB]"); a1.set_ylabel("BLER (16 outer iterations)")
    a1.set_title(r"(a) headline cell, equal budget $N_{\rm train}=1.6\times10^5$", fontsize=8.8)
    a1.annotate("GMM $b^*$ → diffusion prior:\n−3 dB BLER 0.243 → 0.145\n+1.41 dB at BLER 0.1 [90% CI 1.22, 1.64]\n"
                "3/3 decision points, p < 1e-4", xy=(0.36, 0.72), xycoords="axes fraction", fontsize=7.0,
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="0.7"))

    budgets = [(1e4, "B1e4", "kron 512", False), (4e4, "B4e4k", "kron 2048", False),
               (1.6e5, "B16e4k", "kron 1024", True), (3.2e5, "B32e4last", "kron 4096", True)]
    txt += ["", "(b) C2 -3 dB, BLER@16 vs equal budget (last-EMA weights; GMM fit and score net on the same N_train channels):"]
    rows = {}
    for N, tag, bk, gate in budgets:
        d = raw(tag)
        rows[N] = {arm: fails(d, "C2", -3.0, arm) for arm in ("M-ours-bstar", "M-ours-dscore-C-V1", "R5-genie")}
        txt.append(f"  N={N:.1e} {tag:<10} b*={bk:<9} D1-sibling gate {'PASS' if gate else 'FAIL (budget-axis measurement)'}: "
                   + ", ".join(f"{a} {int(v.sum())}/{len(v)}" for a, v in rows[N].items()))
    Ns = [b[0] for b in budgets]
    for arm, lab, col, mk, ls in ARMS[1:]:
        k = np.array([rows[N][arm].sum() for N in Ns]); n = np.array([len(rows[N][arm]) for N in Ns])
        p = k / n; lo, hi = wilson(k, n)
        a2.errorbar(Ns, p, yerr=[p - lo, hi - p], color=col, marker=mk, ls=ls, ms=5 if mk != "*" else 8, lw=1.4,
                    capsize=2, label=lab)
    b = raw("B32e4"); v = fails(b, "C2", -3.0, "M-ours-dscore-C-V1")
    a2.plot([3.2e5], [v.mean()], marker="s", mfc="none", mec="tab:green", ms=8, ls="none",
            label=r"diffusion prior, best-val weights ($N=3.2\times10^5$)")
    txt.append(f"  N=3.2e5 B32e4 (_best.pt, judging run): M-ours-dscore-C-V1 {int(v.sum())}/{len(v)}")
    a2.axvspan(6e3, 6.5e4, color="0.92", zorder=0)
    a2.text(2.0e4, 0.205, "gate-FAIL\nrecipe", ha="center", fontsize=6.8, color="0.35")
    for N, tag, bk, gate in budgets:
        a2.annotate(bk, (N, rows[N]["M-ours-bstar"].mean()), textcoords="offset points",
                    xytext={1.6e5: (-10, 8), 3.2e5: (12, 8)}.get(N, (0, 8)), ha="center", fontsize=6.3, color="tab:red")
    a2.set_xscale("log"); a2.set_ylim(0, 0.3); a2.set_xlim(6e3, 5e5)
    a2.set_xlabel(r"equal training budget $N_{\rm train}$ (channels)"); a2.set_ylabel("BLER at −3 dB")
    a2.set_title("(b) the advantage holds at every budget", fontsize=8.8)
    fig.tight_layout()
    h1, l1 = a1.get_legend_handles_labels(); h2, l2 = a2.get_legend_handles_labels()
    extra = [(h, l) for h, l in zip(h2, l2) if l not in l1]            # the hollow best-val marker of panel (b)
    fig.legend(h1 + [h for h, _ in extra], l1 + [l for _, l in extra], loc="upper center", ncol=3,
               bbox_to_anchor=(0.5, 0.0), frameon=False, fontsize=7.4)
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(FIG, f"F16_headline_budget.{ext}"))
    txt += ["", "Caption notes: equal budget = GMM EM fit and diffusion-prior training use the same N_train channel set. "
            "R5-genie is a known-channel receiver REFERENCE (same detector + BCJR, true H), not a bound. "
            "Panel (a) annotation: tables_D2_B16e4k.txt:367-372 (b*->V1 sign tests 302:50, 117:21, 35:7; SNR@0.1 gap "
            "+1.41 dB [+1.22, +1.64]). b* for 4e4 and 3.2e5 is at the edge of the fitted K grid (4e4: K=2048; 3.2e5: K=4096, "
            "user-decided stop); 1.6e5 b* K=1024 with K=2048 not fitted. Headline = 1.6e5. Error bars: 95% Wilson."]
    open(os.path.join(FIG, "F16_headline_budget.txt"), "w").write("\n".join(txt) + "\n")
    print("\n".join(txt))


if __name__ == "__main__":
    main()
