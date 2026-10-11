"""conf/code/path_strata.py -- REPORT-ONLY (no label, no test, no CI): BLER@16 of b*, V1 and Perfect CSI on the route pool (prior SRP)
by how far into the test area the trial's snapshot lies.  Registered in NEXT_EXPERIMENTS_PATH16e4 §1 before any SRP BLER.

The test pool is the last 87 rows of the UE's route (srp_build.py); rows are 1.5 cm apart, so row r of the test area is
(r + 1) x 1.5 cm beyond the last row walked in training.  At -3 dB and at the decision SNRs of the measurement tag
(results/tables_D2_<TAG>.txt, the registered b* -> V1 pair; whatever their number) every test trial's pool index is obtained by
replaying runner.run_task's loop on the trial stream (as code/rank_strata.py does; raw files are only read) and its row is put in
one of three strata: the first 29 test rows (nearest the training area), the middle 29, the last 29.  Per stratum: n, the
failures of b* / V1 / R5-genie and the point estimate R = (b* - V1) / (b* - genie) (blank when b* <= genie).
Alignment check: R5-genie is run on the first 40 replayed trials and must equal the raw `R5-genie|blk_err` bit for bit.

usage: CUDA_VISIBLE_DEVICES= python code/path_strata.py --tag SRPB16e4 [--prior SRP] [--cell C2] [--ntrain 160000]
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import dmimo
import numpy as np
import runner
from analysis import load_raw
from rank_strata import ARMS, N_CHECK, decision_snrs, fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--prior", default="SRP")
    ap.add_argument("--cell", default="C2")
    ap.add_argument("--ntrain", type=int, default=160000)
    a = ap.parse_args()
    import srp_build
    runner._init(a.tag)
    c = C.CELLS[a.cell]
    meta = np.load(os.path.join(dmimo.pool_dir(a.prior, c["Nr"]), "meta.npz"))
    n_test = int(np.ceil(srp_build.TEST_SHARE * srp_build.NY)); first = srp_build.NY - n_test
    assert n_test == 87 and n_test % 3 == 0
    data, _, _ = load_raw("D2", root=os.path.join(C.CONF, f"raw_{a.tag}"))
    snrs = sorted({-3.0, *decision_snrs(a.tag)})
    L = [C.header("D2", extra=[f"content     : path_strata.py -- BLER@16 of raw_{a.tag} (prior {a.prior}, cell {a.cell}) by the trial snapshot's row inside the "
                               f"test area (rows {first}..{srp_build.NY - 1} of the route; three strata of {n_test // 3} rows), REPORT-ONLY; SNRs {snrs}"]), ""]
    ok = True
    for snr in snrs:
        P = runner.build_point("D2", a.cell, a.prior, snr, a.ntrain)
        code, gen, genie = P["code"], P["gen"], P["arms"]["R5-genie"]
        b, v, g = (fails(data, a.cell, snr, arm) for arm in ARMS)
        ref = np.asarray(data[[k for k in data if k[0] == a.cell and k[2] == snr][0]]["R5-genie"]["blk_err"])
        rng = C.trial_rng("D2", a.prior, c["Nr"], c["T"], c["Tp"], snr)
        rec = []

        def draw(rng, n, G=gen):                               # DMGen._draw with the drawn pool index recorded
            w = dmimo._which(rng, G.kind, G.Nr)
            assert w == "test" and n == 1, (w, n)
            i = G.idx[w][rng.integers(0, len(G.idx[w]), n)]
            rec.append(int(i[0]))
            return np.asarray(G.H[i], dtype=complex) / G.s
        gen._draw = draw
        same = True
        for tr in range(len(g)):
            H = gen.sample(rng)
            u = rng.integers(0, 2, code.K)
            perm = rng.permutation(code.Ns)
            _, Y = genie.transmit(u, perm, H, rng)
            if tr < N_CHECK:
                same &= np.array_equal(np.asarray(genie.run(Y, H, u, perm, C.N_ITER)["blk_err"]), ref[tr], equal_nan=True)
        ok &= same
        r = meta["row"][np.array(rec)] - first
        assert (r >= 0).all() and (r < n_test).all()
        L.append(f"{snr:+.0f} dB  n={len(g)}  alignment (R5-genie, first {N_CHECK} replayed trials vs raw, bit-identical): {'OK' if same else 'MISMATCH'};  "
                 f"failures b* {int(b.sum())}  V1 {int(v.sum())}  genie {int(g.sum())}")
        for k, lab in enumerate(("first 29 test rows (0.015-0.435 m beyond the training area)", "middle 29 test rows (0.45-0.87 m)", "last 29 test rows (0.885-1.305 m)")):
            m = r // (n_test // 3) == k
            fb, fv, fg = int(b[m].sum()), int(v[m].sum()), int(g[m].sum())
            L.append(f"    {lab:<62} n={int(m.sum()):5d}  failures b* {fb:5d}  V1 {fv:5d}  genie {fg:5d}  R = " + (f"{(fb - fv) / (fb - fg):.3f}" if fb > fg else "(b* <= genie)"))
    L += ["", f"alignment {'OK at every SNR' if ok else 'MISMATCH -- the strata are NOT attached to the right trials; do not use'}",
          "report-only: no label, no test, no CI; interpretation is the user's."]
    print("\n".join(L))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
