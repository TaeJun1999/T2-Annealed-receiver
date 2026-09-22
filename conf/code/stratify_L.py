"""Stratify an existing D2 BLER run by the number of propagation paths L of each block.

D2 draws L ~ Unif{3..8} FRESH PER BLOCK (05_SPEC §1), so the sparsity axis is already inside every raw
file we have -- it was simply never read.  The mechanism claim of this project is that the learned
score beats the fitted GMM because D2's support is a union of low-dimensional manifolds (3L real
dimensions inside 2*Nr*Nt = 64) and a mixture of K ellipsoids covers a thin manifold badly.  If that
is right, the advantage must GROW as L falls.  This script tests exactly that, with zero new
simulation: it replays the trial RNG stream, which is deterministic, and recovers L per trial.

Reproducing the stream (runner.py:354-360): for every trial the run consumes, in order,
    gen.sample(rng)                      <- draws L first (d2.D2Gen._draw)
    rng.integers(0, 2, code.K)
    rng.permutation(code.Ns)
    first.transmit(u, perm, H, rng)      <- 2 * Nr * T standard normals; ARM-INDEPENDENT
so replaying those four calls in order reproduces the same L sequence without running any receiver.
The check below verifies the reproduction against a quantity stored in the raw file itself.

Report-only.  Selects nothing, changes no arm, runs no receiver.
"""
import argparse
import glob
import os
import re
import sys
import collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from scipy.stats import binomtest
import common as C
import d2

ARMS = ["R1-turbo", "R2-ours-G", "M-ours-bstar", "M-ours-dscore-C-V1", "M-ours-dscore-C-V4", "R5-genie"]


def replay_L(cell, snr, total, prior="S2"):
    """The L of trials 0..total-1 of one (cell, SNR) point, from the deterministic stream."""
    c = C.CELLS[cell]
    Nr, Nt, T, Tp = c["Nr"], c["Nt"], c["T"], c["Tp"]
    gen = C.make_gen("D2", prior, Nr, Nt)
    code = C.QAMCode(C.GENS, C.NU, C.M_QAM, Nt * (T - Tp))
    rng = C.trial_rng("D2", prior, Nr, T, Tp, snr)
    out = np.empty(total, int)
    for tr in range(total):
        th, ph, al, L = gen._draw(rng, 1)          # same call gen.sample() makes
        out[tr] = int(L[0])
        rng.integers(0, 2, code.K)
        rng.permutation(code.Ns)
        rng.standard_normal((Nr, T))               # transmit(): real part
        rng.standard_normal((Nr, T))               # transmit(): imaginary part
    return out


def load(rawdir, cell):
    """blk_err@16 and nmse@16 per arm, concatenated in the file order the run wrote them."""
    per = collections.defaultdict(dict)
    for f in glob.glob(os.path.join(C.CONF, rawdir, f"D2_{cell}_*.npz")):
        m = re.search(r"snr(-?\d+)_skip(\d+)_n(\d+)", f)
        snr, skip = int(m.group(1)), int(m.group(2))
        d = np.load(f, allow_pickle=True)
        per[snr][skip] = {a: (np.where(np.isfinite(d[f"{a}|blk_err"][:, 15]), d[f"{a}|blk_err"][:, 15], 1.0),
                              d[f"{a}|nmse"][:, 15]) for a in ARMS if f"{a}|blk_err" in d.files}
    return per


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default="raw_B16e4k")
    ap.add_argument("--cell", default="C2")
    ap.add_argument("--snr", type=int, default=-3)
    a = ap.parse_args()
    per = load(a.raw, a.cell)
    assert a.snr in per, f"{a.snr} dB not in {a.raw}/{a.cell}: have {sorted(per)}"
    chunks = sorted(per[a.snr])
    total = max(chunks) + len(per[a.snr][max(chunks)][ARMS[0]][0])
    L = replay_L(a.cell, a.snr, total)

    # assemble the trials in stream order
    blk = {arm: np.full(total, np.nan) for arm in ARMS}
    nms = {arm: np.full(total, np.nan) for arm in ARMS}
    for skip, d in per[a.snr].items():
        for arm, (b, nm) in d.items():
            blk[arm][skip:skip + len(b)] = b
            nms[arm][skip:skip + len(nm)] = nm
    ok = np.isfinite(blk["R5-genie"])
    n = int(ok.sum())

    out = []
    w = out.append
    w(f"# L-stratification of {a.raw} / D2 {a.cell} / {a.snr:+d} dB   (report-only, no new simulation)")
    w(f"# D2 draws L ~ Unif{{{d2.L_MIN}..{d2.L_MAX}}} per block (05_SPEC §1); L is recovered by replaying")
    w(f"# the deterministic trial stream, runner.py:354-360.  n = {n} trials.")
    w(f"# manifold dimension of a block = 3L real dims inside 2*Nr*Nt = {2 * C.CELLS[a.cell]['Nr'] * C.CELLS[a.cell]['Nt']}")
    w("")
    w(f"{'L':>3} {'3L':>4} {'codim':>6} {'n':>5} | " + " ".join(f"{x.replace('M-ours-','').replace('dscore-C-',''):>11}" for x in ARMS)
      + " | GMM/V1  GMM-V1  bstar->V1 (a:b, p)")
    for Lv in range(d2.L_MIN, d2.L_MAX + 1):
        s = ok & (L == Lv)
        if s.sum() < 30:
            continue
        row = f"{Lv:>3} {3*Lv:>4} {2*C.CELLS[a.cell]['Nr']*C.CELLS[a.cell]['Nt'] - 3*Lv:>6} {int(s.sum()):>5} | "
        vals = {}
        for arm in ARMS:
            vals[arm] = float(np.nanmean(blk[arm][s]))
            row += f"{vals[arm]:>11.4f} "
        g, v = vals["M-ours-bstar"], vals["M-ours-dscore-C-V1"]
        gm, vv = blk["M-ours-bstar"][s], blk["M-ours-dscore-C-V1"][s]
        aa = int(((gm == 1) & (vv == 0)).sum()); bb = int(((gm == 0) & (vv == 1)).sum())
        p = binomtest(aa, aa + bb, 0.5).pvalue if aa + bb else 1.0
        row += f"| {g/v if v else float('inf'):>6.2f}  {g-v:>6.4f}  {aa}:{bb}, p={p:.1e}"
        w(row)
    w("")
    w("READ: if the learned prior's advantage comes from the manifold geometry, the GMM/V1 ratio and the")
    w("paired a:b split must grow as L falls (thinner manifold, higher co-dimension).  If they are flat in")
    w("L, the geometry story does not explain the advantage and a sparser testbed will not enlarge it.")
    txt = "\n".join(out) + "\n"
    path = os.path.join(C.CONF, "results", f"Lstrat_{a.raw.replace('raw_','')}_{a.cell}_{a.snr:+d}dB.txt")
    open(path, "w").write(txt)
    print(txt)
    print("->", path)


if __name__ == "__main__":
    main()
