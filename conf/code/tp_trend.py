"""Cross-cell read of the structured-prior gain against the PILOT BUDGET Tp.

WHY.  The pre-registered headline pairs R2-ours-G -> M-ours-bstar at each cell's own three
decision points, and those points differ between cells (C1/C3/C5 use the high-SNR end, C2/C4 the
low end).  A Tp trend read off those numbers would confound Tp with SNR.  This script instead
pairs the two arms at EVERY SNR the cell actually ran, so Tp moves and SNR is held fixed.

Nothing here re-runs or re-selects anything: it is a different reading of conf/raw/*.npz, which is
frozen.  It adds no arm and changes no table.
"""
import glob, os, re, sys
import numpy as np
from scipy.stats import binomtest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

A, B = "R2-ours-G", "M-ours-bstar"
CELLS = {"C1": (8, 2), "C5": (8, 3), "C2": (8, 4), "C3": (4, 2), "C4": (4, 4)}


def load(cell):
    """-> {snr: (wins_B, wins_A, n_pairs)} pooled over every chunk of that cell."""
    out = {}
    for f in sorted(glob.glob(os.path.join(C.CONF, "raw", f"D2_{cell}_*.npz"))):
        d = np.load(f, allow_pickle=True)
        if f"{A}|blk_err" not in d or f"{B}|blk_err" not in d:
            continue
        snr = float(d["run|snr"])
        a, b = d[f"{A}|blk_err"][:, -1], d[f"{B}|blk_err"][:, -1]   # after 16 iterations
        wb = int(np.sum((a > 0) & (b == 0)))       # B fixes a block A lost
        wa = int(np.sum((a == 0) & (b > 0)))       # B breaks a block A won
        p = out.get(snr, (0, 0, 0))
        out[snr] = (p[0] + wb, p[1] + wa, p[2] + len(a))
    return out


rows = {c: load(c) for c in CELLS}
snrs = sorted({s for v in rows.values() for s in v})

print(C.header("D2", extra=[
    "content     : structured-prior gain (R2-ours-G -> M-ours-bstar) vs pilot budget Tp,",
    "              paired at EVERY SNR rather than at each cell's own decision points, so that",
    "              Tp varies and SNR is held fixed.  Discordant pairs only (a two-sided sign test).",
    "reading     : 'wins' = blocks the GMM prior fixes; 'loss' = blocks it breaks.  p is exact binomial.",
    "NOT a new arm, NOT a new run: a re-read of the frozen conf/raw/*.npz.",
]))
print(C.D2_WARNING, "\n")

for nr in (8, 4):
    cs = [c for c in CELLS if CELLS[c][0] == nr]
    cs.sort(key=lambda c: CELLS[c][1])
    if not cs:
        continue
    print(f"--- {nr}x4 array " + "-" * 92)
    print(f"{'SNR':>5} | " + " | ".join(f"{c}(Tp={CELLS[c][1]}) {'win:loss':>9} {'p':>8}" for c in cs))
    for s in snrs:
        cell_txt = []
        any_data = False
        for c in cs:
            if s not in rows[c]:
                cell_txt.append(f"{'':>21}")
                continue
            any_data = True
            wb, wa, n = rows[c][s]
            p = binomtest(wb, wb + wa, 0.5).pvalue if wb + wa else 1.0
            star = "*" if p < 0.05 else " "
            cell_txt.append(f"{wb:>5}:{wa:<5}{p:>8.1e}{star}")
        if any_data:
            print(f"{s:>+5.0f} | " + " | ".join(cell_txt))
    # pooled over all SNRs
    print(f"{'pool':>5} | " + " | ".join(
        (lambda t: f"{t[0]:>5}:{t[1]:<5}{binomtest(t[0], t[0]+t[1], 0.5).pvalue if t[0]+t[1] else 1.0:>8.1e}"
                   + ("*" if (binomtest(t[0], t[0]+t[1], 0.5).pvalue if t[0]+t[1] else 1.0) < 0.05 else " "))
        (tuple(map(sum, zip(*[rows[c][s] for s in rows[c]]))) if rows[c] else (0, 0, 0)) for c in cs))
    print()

print("READING.  * marks p < 0.05 (two-sided exact binomial on discordant pairs).")
print("The comparison is paired within a cell and within an SNR; cells are NOT pooled with each other,")
print("because Nr, T and the pilot overhead all differ and a pooled number would not mean anything.")
