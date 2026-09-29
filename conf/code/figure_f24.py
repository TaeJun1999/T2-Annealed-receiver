"""conf/code/figure_f24.py -- F24-F26: the non-stationary experiments (report figures, read-only).

F24  D2 C2 (headline 8x4) under within-block Doppler (DOP16e4, nu = 0.005 / 0.01) and Rx-array rotation (ROT16e4, 15 / 30 deg),
     0-deg / static-trained prior; every registered baseline of SUPP16e4 on the SAME trials (raw_<T> + raw_X{L,P,A}<T>).
F25  all 24 SUPP16e4 conditions (6 datasets x 4 conditions): -3 dB BLER@16 of V1, of the closest registered baseline X*
     (fewest -3 dB failures among b* + the 12 of SUPP16e4 §1, R0-pilot read @1) and of genie.
F26  drift-trained priors (ROTMIX16e4 B', D2 C2 at 15 / 30 deg, tags RMX<d>{,PIL,ALD}) and the spatially non-stationary
     visibility-window prior (S2V16e4 C, D2 C6 16x4, tags S2vB16e4 / S2vPIL / S2vALD).
Equal budget N_train = 1.6e5, test trials 0..2559 (n = 2560 per SNR), BLER@16.  Colour roles = code/figstyle.py (V1 blue,
GMM orange, classical receivers neutral grey, genie ink); the pilot-only V1 is the V1 colour hollow/dashed, ALD violet.
Only the registered comparisons are tested (in the registration documents); the figures show, they do not test.  Record
failure counts are asserted.  Writes figs/F24_nonstationary_D2C2, F25_nonstationary_all, F26_drift_spatial .{pdf,png,txt}.
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
from figstyle import INK, V1, GMM, GENIE, GAUSS
from figure_f21 import fails

plt.rcParams.update({"font.size": 8, "axes.labelsize": 8.5, "axes.titlesize": 8.5, "legend.fontsize": 7.5,
                     "xtick.labelsize": 7.5, "ytick.labelsize": 7.5, "axes.grid": True, "grid.alpha": 0.25,
                     "figure.dpi": 200, "savefig.bbox": "tight", "savefig.pad_inches": 0.02,
                     "text.color": INK, "axes.labelcolor": INK, "axes.titlecolor": INK,
                     "xtick.labelcolor": INK, "ytick.labelcolor": INK})
FIG = os.path.join(C.CONF, "figs")
GREY, ALD = "#52514e", "#4a3aa7"
# (raw arm key, iteration index, legend label, colour, marker, line style, line width, filled?)
ARMS = [("R3-bigamp", -1, "BiG-AMP, i.i.d. prior (R3)", GREY, "v", "--", 1.0, False),
        ("R1-turbo", -1, "turbo receiver, LMMSE (R1)", GREY, "^", "-", 1.0, False),
        ("R2-ours-G", -1, "same EP receiver, Gaussian prior (R2)", GAUSS["color"], "o", "--", 1.1, True),
        ("ALD-pilot", -1, "annealed Langevin, pilot-only, plug-in (ALD)", ALD, "P", ":", 1.1, True),
        ("V1-pilot", -1, "diffusion prior V1, pilot-only", V1["color"], "s", "--", 1.1, False),
        ("M-ours-bstar", -1, r"GMM prior $b^*$ (validation-selected K)", GMM["color"], "D", "-", 1.3, True),
        ("M-ours-dscore-C-V1", -1, "diffusion prior V1 (proposed)", V1["color"], "s", "-", 1.8, True),
        ("R5-genie", -1, "known-channel reference (genie)", GENIE["color"], "*", "-.", 1.1, True)]
# SUPP16e4 §1: b* + the 12 registered baselines (R0-pilot read at iteration 1)
BASE = [("M-ours-bstar", -1), ("M-ours-bstar-scalar", -1), ("M-ours-gmm32", -1), ("R0-pilot", 0), ("R1-turbo", -1),
        ("R2-ours-G", -1), ("R3-bigamp", -1), ("R4-llr", -1), ("R4-scvamp", -1), ("bstar-pilot", -1), ("V1-pilot", -1),
        ("ALD-pilot", -1), ("ALDv-pilot", -1)]
DS = [("B16e4k", "D2 C2", "C2"), ("NR16", "D2 C6", "C6"), ("D3", "D3", "C2"), ("SV", "SV8e", "C2"), ("U28", "UMi28", "C2"),
      ("MX", "MIX3", "C2")]
CONDS = [("DOPa", "Doppler ν = 0.005"), ("DOPb", "Doppler ν = 0.01"), ("ROTa", "rotation 15°"), ("ROTb", "rotation 30°")]


def load(tags, cell):
    """merge the raws of one condition (disjoint arms; genie is in every raw and bit-identical by acceptance)."""
    out = {}
    for t in tags:
        d, _, _ = load_raw("D2", root=os.path.join(C.CONF, f"raw_{t}"))
        for (c, _, snr), arms in d.items():
            if c == cell:
                out.setdefault(snr, {}).update(arms)
    return out


def curves(ax, d, title, rec3, txt):
    snrs = np.array(sorted(d))
    got = tuple(int(fails(d, -3.0, a, -1).sum()) for a in ("M-ours-bstar", "M-ours-dscore-C-V1", "R5-genie"))
    assert got == rec3, (title, got, rec3)
    txt.append(f"{title} -- failures / 2560 at SNR " + " ".join(f"{s:+.0f}" for s in snrs) + " dB:")
    zeros, hs = [], {}
    for arm, it, lab, col, mk, ls, lw, filled in ARMS:
        k = np.array([fails(d, s, arm, it).sum() for s in snrs]); assert all(len(d[s][arm]["blk_err"]) == 2560 for s in snrs)
        ok = k > 0
        hs[lab], = ax.plot(snrs[ok], k[ok] / 2560.0, color=col, marker=mk, ls=ls, lw=lw, ms=(3.2 if mk != "*" else 5.5),
                           mfc=col if filled else "white", mew=0.9, zorder=5 if arm == "M-ours-dscore-C-V1" else 3)
        zeros += [f"{lab.split(' (')[0]} {s:+.0f}" for s, z in zip(snrs, ok) if not z]
        txt.append(f"    {arm:<20}@16  " + " ".join(f"{int(x):5d}" for x in k))
    txt.append("    zero-failure points (not drawn on the log axis): " + ("; ".join(zeros) if zeros else "none"))
    ax.set_title(title, fontsize=8); ax.set_yscale("log"); ax.set_ylim(2e-4, 1.05); ax.set_xticks(range(-3, 16, 3))
    return hs


def grid_figure(name, panels, shape, size, head, foot):
    fig, axs = plt.subplots(*shape, figsize=size, sharex=True, sharey=True, layout="constrained", squeeze=False)
    txt, hs = [head, ""], {}
    for ax, (title, tags, cell, rec3) in zip(axs.flat, panels):
        hs.update(curves(ax, load(tags, cell), title, rec3, txt))
    for ax in axs[-1]:
        ax.set_xlabel("SNR [dB]")
    for ax in axs[:, 0]:
        ax.set_ylabel("BLER")
    order = [a[2] for a in ARMS][::-1]
    fig.legend([hs[l] for l in order], order, loc="outside lower center", ncol=3, frameon=False, columnspacing=1.2,
               handlelength=2.6)
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(FIG, f"{name}.{ext}"))
    open(os.path.join(FIG, f"{name}.txt"), "w").write("\n".join(txt + ["", foot]) + "\n")
    print("\n".join(txt))


def f25():
    # record -3 dB failures (V1, X*, F_X*, genie) from SUPP16e4 §6.1, asserted
    REC = {"DOPaB16e4k": (442, "M-ours-bstar", 740, 183), "DOPbB16e4k": (756, "M-ours-bstar", 1133, 846),
           "ROTaB16e4k": (404, "M-ours-bstar", 656, 111), "ROTbB16e4k": (519, "M-ours-bstar", 781, 113),
           "DOPaNR16": (80, "V1-pilot", 129, 42), "DOPbNR16": (179, "M-ours-bstar", 422, 415),
           "ROTaNR16": (60, "V1-pilot", 108, 24), "ROTbNR16": (86, "V1-pilot", 159, 21),
           "DOPaD3": (1102, "M-ours-bstar", 1392, 644), "DOPbD3": (1418, "M-ours-bstar", 1671, 1406),
           "ROTaD3": (1056, "M-ours-bstar", 1303, 460), "ROTbD3": (1142, "M-ours-bstar", 1430, 520),
           "DOPaSV": (472, "M-ours-bstar", 541, 65), "DOPbSV": (711, "M-ours-bstar", 803, 451),
           "ROTaSV": (438, "M-ours-bstar", 511, 38), "ROTbSV": (506, "M-ours-bstar", 570, 59),
           "DOPaU28": (1324, "M-ours-bstar", 1371, 755), "DOPbU28": (1614, "M-ours-bstar", 1638, 1342),
           "ROTaU28": (1261, "M-ours-bstar", 1317, 630), "ROTbU28": (1364, "M-ours-bstar", 1389, 721),
           "DOPaMX": (1431, "M-ours-bstar", 1501, 891), "DOPbMX": (1697, "M-ours-bstar", 1749, 1483),
           "ROTaMX": (1400, "M-ours-bstar", 1460, 671), "ROTbMX": (1495, "M-ours-bstar", 1540, 802)}
    fig, axs = plt.subplots(1, 4, figsize=(7.16, 2.6), sharey=True, layout="constrained")
    txt = ["F25 -- all 24 SUPP16e4 conditions: -3 dB BLER@16 (failures / 2560) of V1, of the closest registered baseline X* "
           "(fewest -3 dB failures among b* + 𝔅 12, R0-pilot @1; ties by name) and of genie.  Recomputed from raw.", ""]
    y = np.arange(len(DS))[::-1]
    for ax, (cp, cname) in zip(axs, CONDS):
        for yi, (suf, dname, cell) in zip(y, DS):
            T = cp + suf
            d = load([T, "XL" + T, "XP" + T, "XA" + T], cell)
            F = {a: int(fails(d, -3.0, a, it).sum()) for a, it in BASE}
            xs = min(F, key=lambda a: (F[a], a))
            v1, g = (int(fails(d, -3.0, a, -1).sum()) for a in ("M-ours-dscore-C-V1", "R5-genie"))
            assert (v1, xs, F[xs], g) == REC[T], (T, v1, xs, F[xs], g, REC[T])
            ax.plot([v1 / 2560, F[xs] / 2560], [yi, yi], color="#a3a29d", lw=1.0, zorder=1)
            ax.plot(F[xs] / 2560, yi, "D", color=GMM["color"] if xs == "M-ours-bstar" else V1["color"],
                    mfc=GMM["color"] if xs == "M-ours-bstar" else "white", ms=4.2, mew=0.9, zorder=3)
            ax.plot(v1 / 2560, yi, "s", color=V1["color"], ms=4.2, zorder=4)
            ax.plot(g / 2560, yi, "*", color=GENIE["color"], ms=6, zorder=2)
            txt.append(f"    {T:<11} {dname:<6} {cname:<18} V1 {v1:5d}  X* {xs:<13} {F[xs]:5d}  genie {g:5d}")
        ax.set_title(cname, fontsize=8); ax.set_xscale("log"); ax.set_xlim(7e-3, 1.0); ax.set_xlabel("BLER at −3 dB")
    axs[0].set_yticks(y, [d[1] for d in DS])
    from matplotlib.lines import Line2D
    L = [Line2D([], [], color=V1["color"], marker="s", ls="", ms=4.2, label="diffusion prior V1 (proposed)"),
         Line2D([], [], color=GMM["color"], marker="D", ls="", ms=4.2, label=r"closest baseline X* = GMM $b^*$"),
         Line2D([], [], color=V1["color"], marker="D", mfc="white", ls="", ms=4.2, label="closest baseline X* = V1 pilot-only"),
         Line2D([], [], color=GENIE["color"], marker="*", ls="", ms=6, label="known-channel reference (genie)")]
    fig.legend(handles=L, loc="outside lower center", ncol=2, frameon=False)
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(FIG, f"F25_nonstationary_all.{ext}"))
    txt += ["", "Registered labels and sentences: NEXT_EXPERIMENTS_SUPP16e4.md §6.1 (k𝔅 = 12 in 21/24, (ii) 0/288).  Where genie "
            "fails at least as often as V1 (DOPb D2 C2, DOPb D2 C6) genie holds only H_0 of the Doppler block (registration "
            "§0).  D2 C6 and non-D2 channel models are UNGATED measurements."]
    open(os.path.join(FIG, "F25_nonstationary_all.txt"), "w").write("\n".join(txt) + "\n")
    print("\n".join(txt))


def main():
    t = lambda T: [T, "XL" + T, "XP" + T, "XA" + T]
    grid_figure("F24_nonstationary_D2C2",
                [("(a) Doppler ν = 0.005", t("DOPaB16e4k"), "C2", (740, 442, 183)),
                 ("(b) Doppler ν = 0.01", t("DOPbB16e4k"), "C2", (1133, 756, 846)),
                 ("(c) Rx rotation 15°", t("ROTaB16e4k"), "C2", (656, 404, 111)),
                 ("(d) Rx rotation 30°", t("ROTbB16e4k"), "C2", (781, 519, 113))],
                (2, 2), (7.16, 5.2),
                "F24 -- D2 C2 (8x4) under within-block Doppler and Rx-array rotation, static / 0-deg trained prior; every "
                "registered baseline on the same trials (raw_<T> + raw_X{L,P,A}<T>).  Recomputed from raw.",
                "Registered labels: DOP16e4 / ROT16e4 §6.1 (b* -> V1) and SUPP16e4 §6.1 (all 12 baselines).  In (b) genie "
                "holds only H_0 of the block and fails more often than V1 at -3 dB (SUPP16e4 §0).")
    grid_figure("F26_drift_spatial",
                [("(a) drift-trained prior, rotation 15° (B′)", ["RMX15", "RMX15PIL", "RMX15ALD"], "C2", REC_RMX[15]),
                 ("(b) drift-trained prior, rotation 30° (B′)", ["RMX30", "RMX30PIL", "RMX30ALD"], "C2", REC_RMX[30]),
                 ("(c) spatial non-stationarity S2v, 16×4 (C)", ["S2vB16e4", "S2vPIL", "S2vALD"], "C6", (202, 94, 23))],
                (1, 3), (7.16, 3.0),
                "F26 -- drift-trained priors (ROTMIX16e4 B', S2d prior, D2 C2) and the visibility-window prior (S2V16e4 C, "
                "D2 C6).  Recomputed from raw.",
                "Registered labels: ROTMIX16e4 §6.1 (RB 15°/30° (i)), S2V16e4 §6.1 (judgement 1 (i), 13/13).  UNGATED.")
    f25()


REC_RMX = {15: (625, 390, 111), 30: (645, 424, 113)}   # ROTMIX16e4 §6.1 line "−3 dB BLER@16 실패 수": b*(S2d 4096), V1(S2d best), genie

if __name__ == "__main__":
    main()
