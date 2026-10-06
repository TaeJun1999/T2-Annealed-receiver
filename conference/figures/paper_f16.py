"""conference/figures/paper_f16.py -- paper version of conf/code/figure_f16.py (git 3f7c09ab), F16: headline BLER curves
and the training-set-size axis.

Same data, computation, error bars, colours and markers as the original for every arm the original draws; only the
rendered text differs, plus two internal-process artefacts removed from panel (b) and three curves added to panel (a):
  - (a) adds the sparse baselines SBL (in loop), SBL (pilot-only), OMP (pilot-only) on the same cell and trials (user request
    2026-10-06), from the raw and with the loading, failure count, colour / marker / line style of conf/code/figure_f31.py
    panel (b) (no error bars, as there); counts asserted against the record file pairB_SPB16e4k.txt;
  - legend / axis labels use the paper glossary (conference/figures/TERMS.md), no project-internal names;
  - plot titles removed, only the bold panel labels (a), (b) remain (cell, budget and iteration count go to the caption);
  - (a) annotation box rephrased without registration terms (the "3/3 decision points, p < 1e-4" line dropped), split into
    four lines and raised so it sits inside the axes clear of the OMP curve; x ticks pinned to the original's 0/5/10/15;
  - (b) "kron <n>" labels -> "K = <n>"; the "gate-FAIL recipe" shading + text and the best-val-weights marker (and its legend
    entry) are not drawn -- the best-val count is still computed and printed with the record text;
  - (b) adds the two NSCALE budget points (pre-registered, run commit 68d4d353, results 2026-10-06): 6.4e5 (raw_B64e4last)
    and 1.28e6 (raw_B128e4last), last-EMA like the others, b* = kron 4096 (grid edge), D1-sibling gate PASS; their _best.pt
    judging-run counts are printed with the record text (not drawn, as for 3.2e5);
  - reads the raw files from conf/ (read-only) and writes only F16_headline_budget.{pdf,png} next to this script
    (no .txt; the record text is printed to stdout unchanged, so it can be diffed against conf/figs/F16_headline_budget.txt).
The original docstring follows.

conf/code/figure_f16.py -- F16: representative result figure (report figure; numbers straight from the raw files).

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

CONF = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "conf"))
sys.dont_write_bytecode = True                                 # conf/code is frozen: no __pycache__ writes there
sys.path.insert(0, os.path.join(CONF, "code"))
import common as C
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({"pdf.fonttype": 42, "ps.fonttype": 42})   # TrueType fonts in PDF (IEEE PDF eXpress rejects Type 3)
from analysis import load_raw
import figstyle as S

plt.rcParams.update({"font.size": 9, "axes.labelsize": 9, "legend.fontsize": 8, "xtick.labelsize": 8.5,
                     "ytick.labelsize": 8.5, "axes.grid": True, "grid.alpha": 0.25, "figure.dpi": 160,
                     "savefig.bbox": "tight"})
FIG = os.path.dirname(os.path.abspath(__file__))              # paper version: figures only, next to this script
_st = lambda d: (d["color"], d["marker"], d["ls"])            # colour/marker/linestyle roles from figstyle
ARMS = [("R2-ours-G", "Gaussian prior", *_st(S.GAUSS)),
        ("M-ours-bstar", "GMM prior", *_st(S.GMM)),
        ("M-ours-dscore-C-V1", "Proposed (diffusion prior)", *_st(S.V1)),
        ("R5-genie", "Perfect CSI", *_st(S.GENIE))]
# (a) sparse baselines (user request 2026-10-06), drawn as in conf/code/figure_f31.py panel (b): same raw (raw_SPB16e4k, same
# trials as raw_B16e4k), colour, markers, line styles, no error bars; F31's legend order, SBL (in loop) on top as there,
# layered under the arms above.  (arm, label, marker, line style, filled?)
SPARSE = "#1baf7a"
SPARSE_ARMS = [("SBL-loop", "SBL (in loop)", "h", "-", True), ("SBL-pilot", "SBL (pilot-only)", "h", "--", False),
               ("OMP-pilot", "OMP (pilot-only)", "X", ":", False)]
# BLER@16 failures / 2560 at -3..+15 dB, as in the record file conf/results/review_next/pairB_SPB16e4k.txt (F31 asserts the same)
REC_SP = {"SBL-loop": [705, 222, 77, 48, 25, 27, 10], "SBL-pilot": [934, 244, 69, 51, 27, 28, 10],
          "OMP-pilot": [1023, 342, 145, 77, 62, 60, 34]}


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
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.0, 3.25), gridspec_kw={"width_ratios": [1.15, 1]})
    txt = ["F16 -- representative result.  Numbers recomputed from the raw files by code/figure_f16.py.", ""]
    txt.append("(a) D2 C2 (8x4, T=16, Tp=4), N_train=1.6e5 equal budget (raw_B16e4k), n=2560 per SNR, BLER@16:")
    for arm, lab, col, mk, ls in ARMS:
        f = [fails(H, "C2", s, arm) for s in snrs]
        k = np.array([x.sum() for x in f]); n = np.array([len(x) for x in f])
        p = k / n; lo, hi = wilson(k, n)
        a1.errorbar(snrs, np.maximum(p, 3e-4), yerr=[np.maximum(p - lo, 0), hi - p], color=col, marker=mk, ls=ls,
                    ms=5 if mk != "*" else 8, lw=1.4, capsize=2, label=lab)
        txt.append(f"  {arm:<20} " + " ".join(f"{int(x)}/{int(m)}" for x, m in zip(k, n)))
    SP, _, w = load_raw("D2", root=os.path.join(C.CONF, "raw_SPB16e4k")); assert not w, w
    assert sorted(SP) == sorted(H), (sorted(SP), sorted(H))
    for key in H:                                                 # same trials (figure_f31.load): genie bit-identical
        assert np.array_equal(H[key]["R5-genie"]["blk_err"], SP[key]["R5-genie"]["blk_err"], equal_nan=True), key
    for i, (arm, lab, mk, ls, filled) in enumerate(SPARSE_ARMS):
        f = [fails(SP, "C2", s, arm) for s in snrs]
        k = np.array([int(x.sum()) for x in f]); n = np.array([len(x) for x in f])
        assert k.tolist() == REC_SP[arm] and set(n.tolist()) == {2560}, (arm, k, n)
        ok = k > 0
        a1.plot(np.array(snrs)[ok], (k / n)[ok], color=SPARSE, marker=mk, ls=ls, lw=1.1, ms=3.4,
                mfc=SPARSE if filled else "white", mew=0.9, zorder=1.9 - 0.1 * i, label=lab)
    a1.set_yscale("log"); a1.set_ylim(1.5e-4, 0.6); a1.set_xlabel("SNR [dB]"); a1.set_ylabel("BLER")
    a1.set_xticks([0, 5, 10, 15])          # the original's auto ticks (its box overflowed the axes, which made them narrower)
    a1.set_title("(a)", loc="left", fontweight="bold", fontsize=8.8)
    a1.annotate("GMM prior → Proposed:\n−3 dB: BLER 0.243 → 0.145\n+1.41 dB at BLER 0.1\n[90% CI 1.22, 1.64]",
                xy=(0.38, 0.76), xycoords="axes fraction", fontsize=7.0, color=S.INK,   # clear of the OMP curve, inside the axes
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="0.7"))

    budgets = [(1e4, "B1e4", "kron 512", False), (4e4, "B4e4k", "kron 2048", False),
               (1.6e5, "B16e4k", "kron 1024", True), (3.2e5, "B32e4last", "kron 4096", True),
               (6.4e5, "B64e4last", "kron 4096", True), (1.28e6, "B128e4last", "kron 4096", True)]   # NSCALE points
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
    b = raw("B32e4"); v = fails(b, "C2", -3.0, "M-ours-dscore-C-V1")   # best-val weights: record text only, not drawn
    txt.append(f"  N=3.2e5 B32e4 (_best.pt, judging run): M-ours-dscore-C-V1 {int(v.sum())}/{len(v)}")
    for N, tag in ((6.4e5, "B64e4"), (1.28e6, "B128e4")):                # NSCALE judging runs: record text only, not drawn
        v = fails(raw(tag), "C2", -3.0, "M-ours-dscore-C-V1")
        txt.append(f"  N={N:.2e} {tag} (_best.pt, judging run): M-ours-dscore-C-V1 {int(v.sum())}/{len(v)}")
    for N, tag, bk, gate in budgets[:3]:                              # GMM K labels above the points, centred
        a2.annotate(bk.replace("kron", "K ="), (N, rows[N]["M-ours-bstar"].mean()), textcoords="offset points",
                    xytext=(0, 16), ha="center", fontsize=7, color=S.INK)
    a2.annotate("K = 4096", (6.4e5, rows[6.4e5]["M-ours-bstar"].mean()), textcoords="offset points",   # one label for
                xytext=(0, -20), ha="center", fontsize=7, color=S.INK)                                    # 3.2e5-1.28e6
    a2.set_xscale("log"); a2.set_ylim(0, 0.3); a2.set_xlim(6e3, 2.2e6)
    a2.set_xlabel(r"Training set size $N_{\rm train}$ (channels)"); a2.set_ylabel("BLER at −3 dB")
    a2.set_title("(b)", loc="left", fontweight="bold", fontsize=8.8)
    fig.tight_layout()
    hl = dict(zip(*a1.get_legend_handles_labels()[::-1]))         # panel (b) arms are a subset of (a)
    labs = [x[1] for x in ARMS + SPARSE_ARMS]                      # original four (column 1), then the sparse baselines
    fig.legend([hl[x] for x in labs], labs, loc="upper center", ncol=2,
               bbox_to_anchor=(0.5, 0.0), frameon=False, fontsize=8)
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(FIG, f"F16_headline_budget.{ext}"))
    txt += ["", "Caption notes: equal budget = GMM EM fit and diffusion-prior training use the same N_train channel set. "
            "R5-genie is a known-channel receiver REFERENCE (same detector + BCJR, true H), not a bound. "
            "Panel (a) annotation: tables_D2_B16e4k.txt:367-372 (b*->V1 sign tests 302:50, 117:21, 35:7; SNR@0.1 gap "
            "+1.41 dB, 90% paired bootstrap CI [+1.22, +1.64]). b* for 4e4 and 3.2e5 is at the edge of the fitted K grid (4e4: K=2048; 3.2e5: K=4096, "
            "user-decided stop); 1.6e5 b* K=1024 with K=2048 not fitted. Headline = 1.6e5. Error bars: 95% Wilson. "
            "Colours: learned diffusion prior V1 blue squares (hollow blue square = best-val weights at 3.2e5), GMM b* "
            "orange diamonds, Gaussian prior (R2) grey circles dashed (panel a only), known-channel reference R5 ink stars dash-dot; "
            "light shading = budgets whose recipe failed the D1-sibling gate; all annotation text in ink.",
            "Genie curve (checked 2026-09-25, no bug; DECISIONS [2026-09-25 14:45 KST] entry): R5-genie = true H + the SAME "
            "LMMSE-PIC / BCJR turbo loop, not a bound. Its residual failures above ~6 dB are L=3 blocks (rank H = 3 < Nt = 4, "
            "near rank 2), a slowly decaying tail, not a flat floor; 9-15 dB points are 2/2560 each (Wilson 95% [2.1e-4, "
            "2.8e-3]) and every SNR point uses independent channel draws, so 12 vs 9 (3 vs 6 dB) and 2/2/2 are within "
            "binomial noise (log-linear binomial fit p = 0.18). The same tail appears in C1/C5/C6, not on full-rank D1."]
    print("\n".join(txt))                                          # record text (internal names), not written to a file


if __name__ == "__main__":
    main()
