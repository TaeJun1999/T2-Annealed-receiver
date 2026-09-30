"""conf/code/genie_floor.py -- report-only diagnostic (user question 2026-09-29 CDT: why does the known-channel genie keep a
high-SNR BLER floor?).  Re-draws the TEST trials' channels exactly as runner.run_task does (trial_rng stream: H, u, perm, then
transmit() noise) and relates the genie's failures (R5-genie|blk_err@16 of an existing raw) to channel properties: number of paths
L (D2 / D3 only), singular-value spread of H (condition number, smallest singular value) and ||H||_F^2.  No receiver is run.
    python code/genie_floor.py --raw raw_B16e4k --prior S2 --cell C2 --snrs 9 12 15
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import common as C
from analysis import load_raw
from t2_route_a import dft_pilots


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True); ap.add_argument("--prior", required=True); ap.add_argument("--cell", required=True)
    ap.add_argument("--snrs", nargs="+", type=int, required=True)
    a = ap.parse_args()
    cell = C.CELLS[a.cell]; Nr, Nt, T, Tp = cell["Nr"], cell["Nt"], cell["T"], cell["Tp"]
    code = C.QAMCode(C.GENS, C.NU, C.M_QAM, Nt * (T - Tp)); gen = C.make_gen("D2", a.prior, Nr, Nt)
    d, _, _ = load_raw("D2", root=os.path.join(C.CONF, a.raw))
    rows = []
    for snr in a.snrs:
        fails = np.asarray(d[(a.cell, a.prior, float(snr))]["R5-genie"]["blk_err"])[:, -1]
        rng = C.trial_rng("D2", a.prior, Nr, T, Tp, snr); sigma2 = 10 ** (-snr / 10)
        for tr in range(len(fails)):
            st = rng.bit_generator.state if hasattr(gen, "_draw") else None
            H = gen.sample(rng)
            L = None
            if st is not None:                                   # D2 / D3: recover L from the same draw
                r2 = np.random.default_rng(); r2.bit_generator.state = st; L = int((np.abs(gen._draw(r2, 1)[2][0]) > 0).sum())
            rng.integers(0, 2, code.K); rng.permutation(code.Ns)
            rng.standard_normal((Nr, T)); rng.standard_normal((Nr, T))          # transmit() noise (same consumption)
            s = np.linalg.svd(H, compute_uv=False)
            rows.append((snr, tr, int(fails[tr] > 0), L, s[0] / s[-1], s[-1], np.sum(np.abs(H) ** 2)))
    R = np.array([(r[0], r[2], -1 if r[3] is None else r[3], r[4], r[5], r[6]) for r in rows], float)
    fl, ok = R[R[:, 1] == 1], R[R[:, 1] == 0]
    print(f"# genie_floor {a.raw} {a.prior} {a.cell} SNR {a.snrs}: trials {len(R)}, genie failures {len(fl)}")
    q = lambda x: f"median {np.median(x):.3g} [p10 {np.percentile(x, 10):.3g}, p90 {np.percentile(x, 90):.3g}]"
    for name, col in (("cond(H)", 3), ("sigma_min(H)", 4), ("||H||_F^2", 5)):
        print(f"  {name:<13} failed: {q(fl[:, col]) if len(fl) else 'n/a'} | ok: {q(ok[:, col])}")
    if (R[:, 2] >= 0).all():
        for L in range(3, 9):
            m = R[:, 2] == L
            print(f"  L={L}: trials {int(m.sum()):5d}, genie failures {int(R[m, 1].sum()):3d} ({R[m, 1].mean():.4f})")
    thr = np.percentile(R[:, 3], 95)
    print(f"  genie failure rate: cond(H) >= p95 ({thr:.3g}) {R[R[:, 3] >= thr, 1].mean():.4f} vs below {R[R[:, 3] < thr, 1].mean():.4f}")
    for r in rows:
        if r[2]:
            print(f"    fail snr {r[0]:+d} trial {r[1]:4d} L={r[3]} cond={r[4]:.3g} smin={r[5]:.3g} |H|^2={r[6]:.3g}")


if __name__ == "__main__":
    main()
