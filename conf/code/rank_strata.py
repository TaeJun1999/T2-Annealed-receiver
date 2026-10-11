"""conf/code/rank_strata.py -- REPORT-ONLY (no label, no test, no CI): BLER@16 of b*, V1 and Perfect CSI by the rank of the trial's
channel, for a ray-traced pool prior (DMC / SRT / SRB / DMI).  Registered as a report-only item in NEXT_EXPERIMENTS_SRT16e4 §1; on DeepMIMO
the same split was made post hoc (results/review_next/DMCB16e4_genie_rank.txt, prereg_audit_2026-10-10/genie_rank.py).

At -3 dB and at the decision SNRs of the measurement tag (results/tables_D2_<TAG>.txt, the registered b* -> V1 pair) every test
trial's channel H is obtained by replaying runner.run_task's loop on the trial stream (as code/dmc_leak_strata.py does; raw files
are only read) and put in one of four strata by the energy share of its largest singular value, s1^2 / sum s^2:
>= 0.95, 0.80-0.95, 0.60-0.80, < 0.60.  Per stratum: n, its share, and the BLER@16 of R5-genie, V1 and b*.
Alignment check: R5-genie is run on the first 40 replayed trials and must equal the raw `R5-genie|blk_err` bit for bit.

usage: CUDA_VISIBLE_DEVICES= python code/rank_strata.py --tag SRTB16e4 --prior SRT [--cell C2] [--ntrain 160000]
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import numpy as np
import runner
from analysis import load_raw
from dmc_leak_strata import decision_snrs
from recovery_ci import ARMS, fails

EDGES, N_CHECK = ((0.95, 1.01), (0.80, 0.95), (0.60, 0.80), (0.0, 0.60)), 40


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--prior", required=True)
    ap.add_argument("--cell", default="C2")
    ap.add_argument("--ntrain", type=int, default=160000)
    a = ap.parse_args()
    runner._init(a.tag)
    c = C.CELLS[a.cell]
    data, _, _ = load_raw("D2", root=os.path.join(C.CONF, f"raw_{a.tag}"))
    snrs = sorted({-3.0, *decision_snrs(a.tag)})
    L = [C.header("D2", extra=[f"content     : rank_strata.py -- BLER@16 of raw_{a.tag} (prior {a.prior}, cell {a.cell}) by the energy share of the "
                               f"channel's largest singular value, REPORT-ONLY; SNRs {snrs} (-3 dB + the decision SNRs of tables_D2_{a.tag}.txt)"]), ""]
    ok = True
    for snr in snrs:
        P = runner.build_point("D2", a.cell, a.prior, snr, a.ntrain)
        code, gen, first = P["code"], P["gen"], P["arms"]["R5-genie"]
        b, v, g = (fails(data, a.cell, snr, arm) for arm in ARMS)
        key = [k for k in data if k[0] == a.cell and k[2] == snr][0]
        ref = np.asarray(data[key]["R5-genie"]["blk_err"])
        rng = C.trial_rng("D2", a.prior, c["Nr"], c["T"], c["Tp"], snr)
        sv = np.empty((len(g), c["Nt"]))
        same = True
        for tr in range(len(g)):
            H = gen.sample(rng)
            u = rng.integers(0, 2, code.K)
            perm = rng.permutation(code.Ns)
            _, Y = first.transmit(u, perm, H, rng)
            sv[tr] = np.linalg.svd(H, compute_uv=False) ** 2
            if tr < N_CHECK:
                same &= np.array_equal(np.asarray(first.run(Y, H, u, perm, C.N_ITER)["blk_err"]), ref[tr], equal_nan=True)
        ok &= same
        share = sv[:, 0] / sv.sum(1)
        L.append(f"{snr:+.0f} dB  n={len(g)}  alignment (R5-genie, first {N_CHECK} replayed trials vs raw, bit-identical): {'OK' if same else 'MISMATCH'};  "
                 f"BLER genie {g.mean():.3f}  V1 {v.mean():.3f}  b* {b.mean():.3f};  share median {np.median(share):.3f}")
        for lo, hi in EDGES:
            m = (share >= lo) & (share < hi)
            L.append(f"    share [{lo:.2f}, {min(hi, 1):.2f}{']' if hi > 1 else ')'}  n={m.sum():5d} ({m.mean():.3f})  " + (
                f"BLER genie {g[m].mean():.3f}  V1 {v[m].mean():.3f}  b* {b[m].mean():.3f}   failures {int(g[m].sum())} / {int(v[m].sum())} / {int(b[m].sum())}"
                if m.any() else "(empty)"))
    L += ["", f"alignment {'OK at every SNR' if ok else 'MISMATCH -- the strata are NOT attached to the right trials; do not use'}",
          "report-only: no label, no test, no CI; interpretation is the user's."]
    out = os.path.join(C.CONF, "results", "review_next", f"{a.tag}_rank_strata.txt")
    open(out, "w").write("\n".join(L) + "\n")
    print("\n".join(L))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
