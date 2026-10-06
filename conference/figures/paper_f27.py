"""conference/figures/paper_f27.py -- paper version of conf/code/figure_f27.py (git 3f7c09ab), F27-F29: non-stationary
summaries.

Same data, parsing, computation, asserts, colours, markers and line styles as the original; only the rendered text differs:
  - dataset, condition and method names use the paper glossary (conference/figures/TERMS.md): D2 C2 -> Sparse specular,
    8x4; D2 C6 -> Sparse specular, 16x4; D3 -> Sparse specular, CN gains; SV8e -> Clustered SV; UMi28 -> 3GPP UMi 28 GHz;
    MIX3 -> 3GPP mixed; rotation -> Array rotation; V1 -> Proposed, b* -> GMM prior, R0/R1/R2/R3/R4 -> Pilot-only
    LMMSE / Turbo LMMSE receiver / Gaussian prior / BiG-AMP / SC-VAMP, ALD -> Annealed Langevin, genie -> Perfect CSI;
  - titles removed: F27 and F28 keep only the bold panel labels; F29 (one panel) has no label and its colour key
    (the old title) is a patch legend ("Proposed fails less", "n.s.", "insuff.", "Proposed fails more (none)");
  - registered labels are not written out: F29 cells (iii) -> "n.s.", (iv) -> "insuff."; the F27 hollow-marker key
    reads "Hollow: n.s. or insuff." instead of "registered label (iii)/(iv)";
  - F28 uses a local copy of figure_f24.grid_figure (same curves via figure_f24.curves) that writes figures only;
  - reads raw files and record files from conf/ (read-only) and writes only F27_nonstationary_gap_recovery,
    F28_nonstationary_C6 and F29_label_grid .{pdf,png} next to this script (no .txt; the record text is printed to
    stdout and keeps the internal names).
The original docstring follows.

conf/code/figure_f27.py -- F27-F29: summaries of the non-stationary experiments (report figures, read-only).

F27  6 datasets x {static, Doppler nu 0.005 / 0.01, rotation 15 / 30 deg}: (a) SNR@0.1 gap b* - V1 [dB] and (b) genie-gap
     recovery R = (F_b* - F_V1)/(F_b* - F_genie) at -3 dB, both with their 90% paired-bootstrap CIs, marker fill = the
     registered b* -> V1 label ((i) filled, (iii)/(iv) hollow).  Values are TRANSCRIBED from the record files, which the
     record audits re-derived from raw: static = figs/F20_channel_models.txt (D2 C2, D3, SV8e, UMi28, MIX3) and
     figs/F17_codim_C6.txt (C6 R; its gap is censored on the grid); non-stationary = results/review_next/pairB_X<T>.txt
     (SUPP16e4, b* block).  Censored gaps ("n/a" / ">=") and undefined R (genie >= V1 guard) are not drawn; they are listed.
F28  D2 C6 (16x4) under the same four conditions: BLER curves of every drawn baseline (same arms as F24), from raw.
F29  the 24 x 13 grid of registered table-B labels X -> V1 of SUPP16e4 (b* + the 12 baselines), from the pairB records.
Writes figs/F27_nonstationary_gap_recovery, F28_nonstationary_C6, F29_label_grid .{pdf,png,txt}.
"""
import os
import re
import sys

CONF = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "conf"))
sys.path.insert(0, os.path.join(CONF, "code"))
import common as C
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({"pdf.fonttype": 42, "ps.fonttype": 42})   # TrueType fonts in PDF (IEEE PDF eXpress rejects Type 3)
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from figstyle import INK, V1, GMM
import figure_f24 as F24
from figure_f24 import DS, CONDS, FIG          # FIG = conf/figs: READ only (the F20 / F17 record .txt files)

OUT = os.path.dirname(os.path.abspath(__file__))     # paper version: figures only, next to this script
RV = os.path.join(C.CONF, "results", "review_next")
NUM = r"([+-]?\d+\.\d+)"
COND5 = [("static", "static")] + CONDS
COLS = ["#3d3c39", "#2a78d6", "#1f4f8f", "#eb6834", "#a8431a"]        # static ink; Doppler blues; rotation oranges
MKS = ["o", "s", "s", "D", "D"]
# paper display names (TERMS.md); DS / CONDS / ARMS keep the internal names for the record text and the data lookups
DNAME = {"B16e4k": "Sparse specular,\n8×4", "NR16": "Sparse specular,\n16×4", "D3": "Sparse specular,\nCN gains",
         "SV": "Clustered SV", "U28": "3GPP UMi\n28 GHz", "MX": "3GPP mixed"}
CNAME = {"static": "Static", "DOPa": "Doppler ν = 0.005", "DOPb": "Doppler ν = 0.01", "ROTa": "Array rotation 15°",
         "ROTb": "Array rotation 30°"}
LABEL = {"R3-bigamp": "BiG-AMP", "R1-turbo": "Turbo LMMSE receiver", "R2-ours-G": "Gaussian prior",
         "ALD-pilot": "Annealed Langevin (plug-in)", "V1-pilot": "Proposed prior, pilot-only", "M-ours-bstar": "GMM prior",
         "M-ours-dscore-C-V1": "Proposed (diffusion prior)", "R5-genie": "Perfect CSI"}


def grid_figure(name, panels, shape, size, head, foot):
    """figure_f24.grid_figure with the paper text (bold panel label only, LABEL legend) writing figures only, no .txt."""
    fig, axs = plt.subplots(*shape, figsize=size, sharex=True, sharey=True, layout="constrained", squeeze=False)
    txt, hs = [head, ""], {}
    for ax, (title, tags, cell, rec3) in zip(axs.flat, panels):
        hs.update(F24.curves(ax, F24.load(tags, cell), title, rec3, txt))
        ax.set_title(""); ax.set_title(title[:3], loc="left", fontweight="bold", fontsize=8)   # paper: panel label only
    for ax in axs[-1]:
        ax.set_xlabel("SNR [dB]")
    for ax in axs[:, 0]:
        ax.set_ylabel("BLER")
    order = F24.ARMS[::-1]
    fig.legend([hs[a[2]] for a in order], [LABEL[a[0]] for a in order], loc="outside lower center", ncol=3, frameon=False,
               columnspacing=1.2, handlelength=2.6)
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(OUT, f"{name}.{ext}"))
    print("\n".join(txt + ["", foot]))


def parse_block(text, anchor):
    b = re.search(rf"^{re.escape(anchor)} -> M-ours-dscore-C-V1.*?(?=^\S)", text, re.S | re.M).group(0)
    lab = re.search(r"-> (\(i+v?\)|\(iv\))", b).group(1)
    g = re.search(rf"gap .*?: {NUM} dB  \[90% paired bootstrap {NUM}, {NUM}", b)
    r = re.search(rf"R_X -3 dB \(primary\): {NUM} \[90% {NUM}, {NUM}\]", b)
    graw = re.search(r"SNR@0.1 gap .*?: (.*)", b).group(1)
    rraw = re.search(r"R_X -3 dB \(primary\): (.*)", b).group(1)
    return lab, (tuple(map(float, g.groups())) if g else None), (tuple(map(float, r.groups())) if r else None), graw, rraw


def static_values():
    out = {}
    names = {"D2 sparse specular": "B16e4k", "D3:": "D3", "SV8e": "SV", "UMi 28": "U28", "MIX3": "MX"}
    for line in open(os.path.join(FIG, "F20_channel_models.txt")):
        for key, suf in names.items():
            if line.startswith("  ") and key in line and "table B" in line:
                lab = re.search(r"b\*->V1 (\(i+v?\)|\(iv\))", line).group(1)
                g = tuple(map(float, re.search(rf"gap b\*-V1 {NUM} dB \[90% {NUM}, {NUM}\]", line).groups()))
                r = tuple(map(float, re.search(rf"R = {NUM} \[90% {NUM}, {NUM}\]", line).groups()))
                out[suf] = (lab, g, r, f"{g[0]:+.2f} dB", f"{r[0]:.3f}")
    t = open(os.path.join(FIG, "F17_codim_C6.txt")).read()
    r = tuple(map(float, re.search(rf"C6 1\.6e5 {NUM} \[{NUM}, {NUM}\] \(_best\)", t).groups()))
    out["NR16"] = ("(i)", None, r, "censored (V1 below 0.1 at the lowest grid SNR)", f"{r[0]:.3f}")
    assert set(out) == {d[0] for d in DS}, out.keys()
    return out


def f27():
    st = static_values()
    vals = {}
    for suf, _, _ in DS:
        vals[(suf, "static")] = st[suf]
        for cp, _ in CONDS:
            vals[(suf, cp)] = parse_block(open(os.path.join(RV, f"pairB_X{cp}{suf}.txt")).read(), "M-ours-bstar")
    fig, axs = plt.subplots(1, 2, figsize=(7.16, 3.3), sharey=True, layout="constrained")
    y0 = np.arange(len(DS))[::-1]
    off = np.linspace(-0.3, 0.3, 5)
    txt = ["F27 -- SNR@0.1 gap b* - V1 [dB] and recovery R at -3 dB (90% paired-bootstrap CIs), static vs the four non-stationary "
           "conditions.  Transcribed from the record files (static: F20 / F17 .txt; non-stationary: pairB_X<T>.txt, b* block).", ""]
    for j, (cp, cname) in enumerate(COND5):
        for yi, (suf, dname, _) in zip(y0, DS):
            lab, g, r, graw, rraw = vals[(suf, cp)]
            filled = lab == "(i)"
            for ax, v in ((axs[0], g), (axs[1], r)):
                if v is None:
                    continue
                ax.errorbar(v[0], yi + off[j], xerr=[[v[0] - v[1]], [v[2] - v[0]]], fmt=MKS[j], color=COLS[j], ms=3.8,
                            mfc=COLS[j] if filled else "white", mew=0.9, elinewidth=0.8, capsize=0)
            txt.append(f"    {dname:<6} {cname:<18} label {lab:<5} gap {graw[:60]:<60} R {rraw[:60]}")
    for ax in axs:
        ax.axvline(0, color=INK, lw=0.6)
    axs[0].set_xlabel("SNR gain at BLER 0.1 [dB]\n(> 0: proposed better)")
    axs[1].set_xlabel("Fraction of the GMM-to-perfect-CSI gap\nclosed at −3 dB")
    axs[0].set_yticks(y0, [DNAME[d[0]] for d in DS]); axs[1].set_xlim(-0.05, 1.12)
    axs[0].set_title("(a)", loc="left", fontweight="bold", fontsize=8)   # paper: panel labels only
    axs[1].set_title("(b)", loc="left", fontweight="bold", fontsize=8)
    L = [Line2D([], [], color=c, marker=m, ls="", ms=4, label=CNAME[cp]) for (cp, _), c, m in zip(COND5, COLS, MKS)]
    L.append(Line2D([], [], color=INK, marker="o", mfc="white", ls="", ms=4, label="Hollow: n.s. or insuff."))
    fig.legend(handles=L, loc="outside lower center", ncol=3, frameon=False)
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(OUT, f"F27_nonstationary_gap_recovery.{ext}"))
    txt += ["", "Not drawn: censored gaps (V1 or b* outside the SNR grid at 0.1) and R left undefined by the genie >= V1 guard "
            "(Doppler nu = 0.01, D2 C2 and C6: genie holds only H_0 of the block).  A hollow marker's value is report-only: its "
            "registered decision points were not significant.  D2 C2 is the headline (gate PASS recipe); every other dataset "
            "is an UNGATED measurement."]
    print("\n".join(txt))                                # paper version: no .txt (record: conf/figs/F27_*.txt)


def f29():
    arms = ["M-ours-bstar", "M-ours-bstar-scalar", "M-ours-gmm32", "R0-pilot@1", "R1-turbo", "R2-ours-G", "R3-bigamp", "R4-llr",
            "R4-scvamp", "bstar-pilot", "V1-pilot", "ALD-pilot", "ALDv-pilot"]
    short = ["GMM prior", "GMM prior, scalar site", "GMM prior (K = 32)", "Pilot-only LMMSE", "Turbo LMMSE receiver",
             "Gaussian prior", "BiG-AMP", "SC-VAMP (LLR)", "SC-VAMP", "GMM prior, pilot-only", "Proposed prior, pilot-only",
             "Annealed Langevin (plug-in)", "Annealed Langevin (error-aware)"]
    code = {"(i)": 0, "(iii)": 1, "(iv)": 2, "(ii)": 3}
    rows, M, txt = [], [], ["F29 -- registered table-B labels X -> V1 (SUPP16e4 §1: b* + 𝔅 12, R0-pilot @1), 24 conditions.  "
                            "From results/review_next/pairB_X<T>.txt.", ""]
    for cp, cname in CONDS:
        for suf, dname, _ in DS:
            t = open(os.path.join(RV, f"pairB_X{cp}{suf}.txt")).read()
            labs = [parse_block(t, a)[0] for a in arms]
            rows.append(f"{DNAME[suf].replace(chr(10), ' ')}, {CNAME[cp]}"); M.append([code[l] for l in labs])
            txt.append(f"    {dname:<6} {cname:<18} " + " ".join(f"{l:<5}" for l in labs))
    M = np.array(M)
    assert (M == 3).sum() == 0 and (M[:, 1:] == 0).all(axis=1).sum() == 21, "SUPP16e4 §6.1: (ii) 0/288, k = 12 in 21/24"
    from matplotlib.colors import ListedColormap
    cmap = ListedColormap(["#2a78d6", "#d9d8d4", "#ffffff", "#eb6834"])
    fig, ax = plt.subplots(figsize=(7.16, 5.4), layout="constrained")
    ax.imshow(M, cmap=cmap, vmin=-0.5, vmax=3.5, aspect="auto")
    for (i, j), v in np.ndenumerate(M):
        if v:
            ax.text(j, i, ["", "n.s.", "insuff.", ""][v], ha="center", va="center", fontsize=6.5, color=INK)   # (ii): 0 by assert
    ax.set_xticks(range(len(arms)), short, rotation=40, ha="right"); ax.set_yticks(range(len(rows)), rows, fontsize=7)
    ax.set_xticks(np.arange(-0.5, len(arms)), minor=True); ax.set_yticks(np.arange(-0.5, len(rows)), minor=True)
    ax.grid(which="minor", color="white", lw=1.2); ax.grid(which="major", visible=False); ax.tick_params(which="minor", length=0)
    for k in (6, 12, 18):
        ax.axhline(k - 0.5, color=INK, lw=0.8)
    # paper: the old title (colour key) becomes a patch legend; the white patch needs an edge to be visible
    key = [Patch(facecolor=c, edgecolor="#a3a29d", lw=0.6, label=l) for c, l in
           zip(cmap.colors, ["Proposed fails less", "n.s.", "insuff.", "Proposed fails more (none)"])]
    fig.legend(handles=key, loc="outside upper center", ncol=4, frameon=False)
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(OUT, f"F29_label_grid.{ext}"))
    txt += ["", f"(i) {(M == 0).sum()}, (iii) {(M == 1).sum()}, (iv) {(M == 2).sum()}, (ii) {(M == 3).sum()} of {M.size}.  The b* column "
            "cites the DOP16e4 / ROT16e4 labels (re-derived with --expect-bstar); R2 is a cited label (SUPP16e4 §0).  No "
            "multiplicity correction; count statements only (SUPP16e4 §1)."]
    print("\n".join(txt))                                # paper version: no .txt (record: conf/figs/F29_label_grid.txt)


def main():
    t = lambda T: [T, "XL" + T, "XP" + T, "XA" + T]
    grid_figure("F28_nonstationary_C6",
                [("(a) Doppler ν = 0.005, 16×4", t("DOPaNR16"), "C6", (224, 80, 42)),
                 ("(b) Doppler ν = 0.01, 16×4", t("DOPbNR16"), "C6", (422, 179, 415)),
                 ("(c) Rx rotation 15°, 16×4", t("ROTaNR16"), "C6", (213, 60, 24)),
                 ("(d) Rx rotation 30°, 16×4", t("ROTbNR16"), "C6", (375, 86, 21))],
                (2, 2), (7.16, 5.2),
                "F28 -- D2 C6 (16x4) under within-block Doppler and Rx-array rotation, static / 0-deg trained prior; every "
                "registered baseline on the same trials (raw_<T> + raw_X{L,P,A}<T>).  Recomputed from raw.",
                "Registered labels: DOP16e4 / ROT16e4 §6.1 and SUPP16e4 §6.1.  C6 is UNGATED (no D1 sibling).  In (b) genie holds "
                "only H_0 of the block and fails about as often as b* at -3 dB (SUPP16e4 §0).")
    f27()
    f29()


if __name__ == "__main__":
    main()
