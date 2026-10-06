"""conference/figures/paper_f31.py -- paper version of conf/code/figure_f31.py (git 3f7c09ab), F31: the proposed prior
against the model-based sparse baselines.

Same data, computation, asserts, error bars, colours and markers as the original; only the rendered text differs:
  - legend / axis / tick labels use the paper glossary (conference/figures/TERMS.md), no project-internal names
    (dataset codes -> dataset names in the (a) tick labels; x label of (a) = fraction of the baseline-to-perfect-CSI gap closed);
  - plot titles removed, only the bold panel labels (a), (b) remain ((b) = Sparse specular, 8x4 -> caption);
  - the registered-label marks "(iv)" in (a) are not drawn (TERMS.md allows "insuff." if a mark is wanted back);
  - reads the raw files and record files from conf/ (read-only; helpers incl. conf/code/figure_f30.py) and writes only
    F31_sparse_baselines.{pdf,png} next to this script (no .txt; the record text is printed to stdout unchanged, so it can be
    diffed against conf/figs/F31_sparse_baselines.txt).
The original docstring follows.

conf/code/figure_f31.py -- F31: V1 against the model-based sparse baselines (SPARSE16e4; report figure, read-only).

(a) 6 static datasets (D2 C2 headline, D3, SV8e, UMi28, MIX3 at C2 8x4; D2 C6 16x4): genie-gap recovery over each pair's decision
    points R_X = (SigmaF_X - SigmaF_V1)/(SigmaF_X - SigmaF_g), 90% paired bootstrap, for X = SBL-loop, SBL-pilot, OMP-pilot (the
    18 new labels) and, for reference, X = b* (cited from STATIC16e4).  "(iv)" marks a registered label (iv) (underpowered);
    every other point is (i).  Recomputed from raw with the registered helpers (pair_baselines.table_b / recovery: anchor = X,
    B 2000, seed 20260926) on base raw_<TAG> + raw_SP<suf> (same trials, genie bit-identical), asserted against
    NEXT_EXPERIMENTS_SPARSE16e4 §6.1 table B (decision points, pooled a:b, label, R_X -3 dB and R_X decision points) and, for b*,
    against the record file pairB_SP<suf>.txt (b* block = STATIC16e4 block, byte-identical per §6.1).
(b) D2 C2 BLER@16 curves of V1, b*, the three sparse baselines and genie; counts asserted against the record file
    pairB_SPB16e4k.txt; the -3 dB failures of all 6 datasets x 6 arms against §6.1 (b).
Colour roles = code/figstyle.py (V1 blue, GMM orange, genie ink); the sparse family is aqua (the fourth validated slot, unused
by the arms of this figure), pilot-only arms hollow / dashed like V1-pilot elsewhere; aqua always carries a legend entry.
Writes figs/F31_sparse_baselines.{pdf,png,txt}.
"""
import os
import re
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
from matplotlib.lines import Line2D
from analysis import load_raw
from pair_baselines import table_b, recovery, fails
from figstyle import INK, INK2, V1, GMM, GENIE
from figure_f30 import rec_fails, RV, raw                     # conf/code/figure_f30.py (read paths only; its rcParams too)

FIG = os.path.dirname(os.path.abspath(__file__))              # paper version: figures only, next to this script
V1A, BS, GE = "M-ours-dscore-C-V1", "M-ours-bstar", "R5-genie"
SPARSE = "#1baf7a"
NEW = ("SBL-loop", "SBL-pilot", "OMP-pilot")
# arm -> (legend label, colour, marker, line style, filled?)
STY = {BS: ("GMM prior", GMM["color"], "D", "-", True),
       "SBL-loop": ("SBL (in loop)", SPARSE, "h", "-", True),
       "SBL-pilot": ("SBL (pilot-only)", SPARSE, "h", "--", False),
       "OMP-pilot": ("OMP (pilot-only)", SPARSE, "X", ":", False),
       V1A: ("Proposed (diffusion prior)", V1["color"], "s", "-", True),
       GE: ("Perfect CSI", GENIE["color"], "*", "-.", True)}
# (suffix, name, base tag, cell, prior)
DS = [("B16e4k", "D2 C2", "B16e4k", "C2", "S2"), ("D3", "D3", "D3B16e4", "C2", "S2c"), ("SV", "SV8e", "SVB16e4", "C2", "SV8e"),
      ("U28", "UMi28", "U28B16e4", "C2", "UMi28"), ("MX", "MIX3", "MXB16e4", "C2", "MIX3"), ("NR16", "D2 C6", "NR16B16e4", "C6", "S2")]
# suffix -> paper tick label of (a) (TERMS.md); the DS names stay in the record text
TICK = {"B16e4k": "Sparse specular\n8×4", "D3": "Sparse specular\nCN gains", "SV": "Clustered SV", "U28": "3GPP UMi 28 GHz",
        "MX": "3GPP mixed", "NR16": "Sparse specular\n16×4"}
# SPARSE16e4 §6.1 table B: (suffix, arm) -> decision SNRs, pooled a:b, label, R_X -3 dB [90%], R_X decision points [90%]
REC = {("B16e4k", "SBL-loop"): ((-3, 0, 3), (588, 72), "(i)", ("0.540", "0.503", "0.579"), ("0.587", "0.554", "0.618")),
       ("B16e4k", "SBL-pilot"): ((-3, 0, 3), (811, 52), "(i)", ("0.665", "0.635", "0.694"), ("0.676", "0.651", "0.702")),
       ("B16e4k", "OMP-pilot"): ((0, 3, 6), (451, 20), "(i)", ("0.697", "0.669", "0.723"), ("0.834", "0.802", "0.863")),
       ("D3", "SBL-loop"): ((0, 3, 6), (474, 69), "(i)", ("0.406", "0.375", "0.438"), ("0.525", "0.491", "0.560")),
       ("D3", "SBL-pilot"): ((0, 3, 6), (634, 55), "(i)", ("0.506", "0.479", "0.534"), ("0.613", "0.583", "0.641")),
       ("D3", "OMP-pilot"): ((3, 6, 9), (506, 19), "(i)", ("0.528", "0.500", "0.555"), ("0.792", "0.760", "0.823")),
       ("SV", "SBL-loop"): ((-3, 0), (256, 42), "(iv)", ("0.317", "0.276", "0.355"), ("0.341", "0.303", "0.377")),
       ("SV", "SBL-pilot"): ((-3, 0, 3), (663, 23), "(i)", ("0.585", "0.557", "0.614"), ("0.604", "0.579", "0.630")),
       ("SV", "OMP-pilot"): ((-3, 0, 3), (1498, 15), "(i)", ("0.746", "0.727", "0.765"), ("0.780", "0.764", "0.795")),
       ("U28", "SBL-loop"): ((3, 6, 9), (307, 56), "(i)", ("0.262", "0.230", "0.292"), ("0.336", "0.299", "0.370")),
       ("U28", "SBL-pilot"): ((3, 6, 9), (388, 49), "(i)", ("0.447", "0.421", "0.471"), ("0.406", "0.373", "0.437")),
       ("U28", "OMP-pilot"): ((6, 9, 12), (569, 10), "(i)", ("0.629", "0.609", "0.648"), ("0.673", "0.645", "0.700")),
       ("MX", "SBL-loop"): ((3, 6, 9), (416, 56), "(i)", ("0.245", "0.216", "0.273"), ("0.456", "0.421", "0.490")),
       ("MX", "SBL-pilot"): ((3, 6, 9), (523, 49), "(i)", ("0.404", "0.378", "0.428"), ("0.524", "0.493", "0.555")),
       ("MX", "OMP-pilot"): ((6, 9, 12), (836, 8), "(i)", ("0.561", "0.539", "0.582"), ("0.789", "0.766", "0.812")),
       ("NR16", "SBL-loop"): ((-3, 0, 3), (330, 11), "(i)", ("0.865", "0.820", "0.906"), ("0.884", "0.847", "0.916")),
       ("NR16", "SBL-pilot"): ((-3, 0, 3), (383, 14), "(i)", ("0.885", "0.847", "0.920"), ("0.898", "0.867", "0.926")),
       ("NR16", "OMP-pilot"): ((-3, 0, 3), (322, 12), "(i)", ("0.832", "0.777", "0.884"), ("0.881", "0.845", "0.914"))}
# SPARSE16e4 §6.1 (b): -3 dB failures / 2560 (genie, V1, b*, SBL-loop, SBL-pilot, OMP-pilot)
REC3 = {"B16e4k": (87, 371, 623, 705, 934, 1023), "D3": (485, 1000, 1298, 1352, 1528, 1575), "SV": (31, 402, 464, 574, 926, 1493),
        "U28": (594, 1228, 1270, 1453, 1740, 2304), "MX": (679, 1354, 1421, 1573, 1811, 2215), "NR16": (22, 53, 184, 251, 291, 207)}
NUM = r"(\d+\.\d+)"


def rec_block(text, arm):
    """record file pairB_SP<suf>.txt, block 'arm -> V1' -> (label, decision SNRs, (a, b) pooled, R_X -3 dB, R_X decision points)."""
    b = re.search(rf"^{re.escape(arm)} -> {V1A}.*?(?=^\S)", text, re.S | re.M).group(0)
    dp = tuple(int(x) for x in re.findall(r"'([+-]\d+)'", re.search(r"decision SNRs \[(.*?)\]", b).group(1)))
    pooled = tuple(int(x) for x in re.search(r"pooled (\d+):(\d+)", b).groups())
    lab = re.search(r"-> (\(i+v?\)|\(iv\))\n", b).group(1)
    r1 = re.search(rf"R_X -3 dB \(primary\): {NUM} \[90% {NUM}, {NUM}\]", b).groups()
    r2 = re.search(rf"R_X decision points \(secondary\): {NUM} \[90% {NUM}, {NUM}\]", b).groups()
    return dp, pooled, lab, r1, r2


def load(suf, tag, cell, prior):
    """base raw (V1, b*, genie, ...) + raw_SP<suf> (the three sparse arms) of the same trials -> {(cell, prior, snr): {arm: ...}}."""
    b, _, w1 = load_raw("D2", root=raw(tag)); s, _, w2 = load_raw("D2", root=raw(f"SP{suf}"))
    assert not w1 and not w2, (w1, w2)
    out = {}
    for k in sorted(k for k in b if k[:2] == (cell, prior)):
        assert np.array_equal(b[k][GE]["blk_err"], s[k][GE]["blk_err"], equal_nan=True), (suf, k)   # same trials
        out[k] = {**b[k], **{x: s[k][x] for x in NEW}}
    return out


def main():
    txt = ["F31 -- V1 against the model-based sparse baselines (SPARSE16e4): per dataset R_X over the decision points (90% paired "
           "bootstrap) for X = SBL-loop, SBL-pilot, OMP-pilot (+ b* cited), and the D2 C2 BLER curves.  Equal budget N_train = 1.6e5, "
           "test trials 0..2559 (n = 2560 per SNR), BLER@16.  Recomputed from raw by code/figure_f31.py (pair_baselines.table_b / "
           "recovery) and asserted against NEXT_EXPERIMENTS_SPARSE16e4 §6.1 (b* against the record file pairB_SP<suf>.txt).", "",
           "raw paths (read-only): " + "; ".join(f"{n} = {raw(t)} + {raw('SP' + s)}" for s, n, t, _, _ in DS), "",
           "  dataset  X           decision SNRs   pooled a:b  label  R_X -3 dB [90%]        R_X decision points [90%]"]
    val, D2C2 = {}, None
    for suf, name, tag, cell, prior in DS:
        d = load(suf, tag, cell, prior)
        keys = sorted(d, key=lambda k: k[2]); snrs = [k[2] for k in keys]; k3 = (cell, prior, -3.0)
        f3 = tuple(int(fails(d[k3], a).sum()) for a in (GE, V1A, BS) + NEW)
        assert f3 == REC3[suf], (suf, f3, REC3[suf])
        text = open(os.path.join(RV, f"pairB_SP{suf}.txt"), encoding="utf-8").read()
        for x in (BS,) + NEW:
            cand, res, powered, wy, wx, lab = table_b(d, cell, prior, snrs, x, V1A)
            pooled = (sum(r[0] for r in res), sum(r[1] for r in res))
            r1 = recovery([tuple(fails(d[k3], a) for a in (x, V1A, GE))])
            r2 = recovery([tuple(fails(d[(cell, prior, s)], a) for a in (x, V1A, GE)) for s in cand])
            got = (tuple(int(s) for s in cand), pooled, lab, tuple(f"{v:.3f}" for v in r1[:3]), tuple(f"{v:.3f}" for v in r2[:3]))
            assert r1[3] == 0 and r2[3] == 0, (suf, x, "undefined replicates")
            assert got == rec_block(text, x), (suf, x, got, rec_block(text, x))
            if x != BS:
                assert got == REC[(suf, x)], (suf, x, got, REC[(suf, x)])
            val[(suf, x)] = (lab, r2[:3])
            txt.append(f"  {name:<8} {x:<12} {str(list(got[0])):<15} {got[1][0]:>5}:{got[1][1]:<5} {lab:<6} "
                       f"{got[3][0]} [{got[3][1]}, {got[3][2]}]   {got[4][0]} [{got[4][1]}, {got[4][2]}]"
                       + ("  (cited, STATIC16e4)" if x == BS else ""))
        if suf == "B16e4k":
            D2C2 = (d, keys, rec_fails(os.path.join(RV, "pairB_SPB16e4k.txt")))

    fig = plt.figure(figsize=(7.16, 3.4), layout="constrained")
    gs = fig.add_gridspec(1, 2, width_ratios=[1.1, 1])
    a1, a2 = fig.add_subplot(gs[0]), fig.add_subplot(gs[1])
    # ---------------- (a) R_X at the decision points ----------------
    y0 = np.arange(len(DS))[::-1]
    off = dict(zip((BS,) + NEW, (0.27, 0.09, -0.09, -0.27)))
    for yi, (suf, name, _, _, _) in zip(y0, DS):
        for x in (BS,) + NEW:
            lab, (r, lo, hi) = val[(suf, x)]
            _, col, mk, _, filled = STY[x]
            a1.errorbar(r, yi + off[x], xerr=[[r - lo], [hi - r]], fmt=mk, color=col, mfc=col if filled else "white", ms=4,
                        mew=0.9, elinewidth=0.9, capsize=0)
    a1.set_yticks(y0, [TICK[d[0]] for d in DS]); a1.set_xlim(0, 1.0); a1.set_ylim(-0.6, len(DS) - 0.4)
    a1.set_xlabel("Fraction of the baseline-to-perfect-CSI gap closed (90% CI)")
    a1.set_title("(a)", loc="left", fontweight="bold", fontsize=8.2)
    a1.grid(axis="y", visible=False)
    # ---------------- (b) D2 C2 curves ----------------
    d, keys, rec = D2C2
    snrs = np.array([k[2] for k in keys])
    txt += ["", "(b) D2 C2 (raw_B16e4k + raw_SPB16e4k), failures / 2560 per SNR " + " ".join(f"{s:+.0f}" for s in snrs) + " dB:"]
    for x in ("OMP-pilot", "SBL-pilot", "SBL-loop", BS, V1A, GE):
        lab, col, mk, ls, filled = STY[x]
        k = np.array([int(fails(d[key], x).sum()) for key in keys])
        assert k.tolist() == rec[x], (x, k.tolist(), rec[x]); assert all(len(d[key][x]["blk_err"]) == 2560 for key in keys)
        ok = k > 0
        a2.plot(snrs[ok], k[ok] / 2560, color=col, marker=mk, ls=ls, lw=1.8 if x == V1A else 1.1,
                ms=3.4 if mk != "*" else 5.5, mfc=col if filled else "white", mew=0.9, zorder=5 if x == V1A else 3)
        txt.append(f"    {x:<20}@16  " + " ".join(f"{int(v):5d}" for v in k)
                   + ("" if ok.all() else "   (zero-failure points not drawn)"))
    a2.set_yscale("log"); a2.set_ylim(5e-4, 1.0); a2.set_xticks(range(-3, 16, 3)); a2.set_xlabel("SNR [dB]"); a2.set_ylabel("BLER")
    a2.set_title("(b)", loc="left", fontweight="bold", fontsize=8.2)
    L = [Line2D([], [], color=STY[x][1], marker=STY[x][2], ls=STY[x][3], mfc=STY[x][1] if STY[x][4] else "white",
                ms=4 if STY[x][2] != "*" else 6, label=STY[x][0]) for x in (V1A, BS, "SBL-loop", "SBL-pilot", "OMP-pilot", GE)]
    fig.legend(handles=L, loc="outside lower center", ncol=2, frameon=False, handlelength=2.6)
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(FIG, f"F31_sparse_baselines.{ext}"))
    txt += ["", "Registered labels and sentences (SPARSE16e4 §6.1, verbatim): 새 18 라벨 중 (i) 17, (iv) 1 (SV8e SBL-loop), (ii) 0.  주 라벨 "
            "(D2 C2): (A) \"V1 이 희소 baseline 3 개(SBL-loop, SBL-pilot, OMP-pilot) 전부보다 적게 실패\" (A1 = `SBL-loop → V1` (i) 588:72).  "
            "\"전부\" 문장 (16 개): D2 C2·D3·UMi28·MIX3 충족 -> \"데이터셋 d 에서 등록된 baseline 전부(16 개, 희소 baseline 포함)와 멀어진다\"; "
            "C6·SV8e 불충족 (STATIC16e4 의 (iv) 로 결과와 무관하게 불가능).  X* (16 개 중 -3 dB 실패 최소) = b* in D2 C2 / D3 / SV8e / UMi28 / "
            "MIX3, V1-pilot in D2 C6 (R_X* 0.492 [0.355, 0.630]).  보정 없음, 개수 문장만; 개별 (i) 을 독립 주장으로 쓰지 않는다.",
            "Caveats (SPARSE16e4 §2 / §5.3 / §6.1, as recorded): rho is the grid edge 16 (the 2nd extension step was stopped for cost; "
            "SBL rho 16 edge in D2 C2 / D3 / SV8e / MIX3 / C6, UMi28 rho_SBL 8 interior; OMP rho 16 edge in all 6).  On-grid oversampled "
            "2-D DFT dictionary; off-grid methods (NOMP etc.) out of scope.  SBL = MacKay fixed point, n_em per SNR tuned on pilot-only "
            "development NMSE and used unchanged inside the loop (no loop tuning; possible loss up to D3 0.85 dB, direction against "
            "SBL-loop = toward V1).  OMP = fixed L per SNR, no noise-based stop, plug-in belief (v = 1e-8).  Where L = N (D2 C2 +15 dB; "
            "SV8e, UMi28 +3..+15 dB; MIX3 +6..+15 dB) OMP-pilot equals the pilot LS estimate and is not called 'sparse recovery'; among "
            "OMP-pilot decision points this is SV8e +3 dB, UMi28 all three, MIX3 all three.  Raised trials of the new arms: 0 (all 6 rows).  "
            "D2 C6 and the non-D2 channel models are UNGATED measurements; D2 C2 is the headline (gate PASS recipe)."]
    print("\n".join(txt))                                          # record text (internal names), not written to a file


if __name__ == "__main__":
    main()
