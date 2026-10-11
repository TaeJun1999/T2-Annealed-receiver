"""conf/code/dmc_leak_strata.py -- NEXT_EXPERIMENTS_DMC16e4 §1 "누수 층화": REPORT-ONLY (no label, no test, no CI).

At the decision SNRs of the measurement tag (read from results/tables_D2_<TAG>.txt, the registered b* -> V1 pair), every test
trial gets  d = min over the N' training channels (stream 7) of ||h - h_train||^2 / ||h||^2  (the TDMh definition) and is put in
the stratum d < 0.1 or d >= 0.1.  Per stratum: n and the BLER@16 failures of b*, V1 and genie; the point estimate
R = (b* - V1) / (b* - genie) -- "n/a" when b* - genie <= 0, not written when n < 100.
The trial's channel comes from replaying runner.run_task's loop on the trial stream (sample -> integers(0, 2, K) ->
permutation(Ns) -> transmit); raw files are only read.  Only d and the stratum are used: no pair index, no LoS / city / BS.
Alignment check: R5-genie is run on the first 40 replayed trials and must equal the raw `R5-genie|blk_err` bit for bit.

usage: CUDA_VISIBLE_DEVICES= python code/dmc_leak_strata.py [--tag DMCB16e4] [--prior DMC] [--cell C2] [--ntrain 160000]
       (--tag / --prior exist so the replay can be exercised on another prior's raw; the registered run uses the defaults)
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import numpy as np
import arms as A
import runner
from analysis import load_raw
from recovery_ci import ARMS, fails

THR, N_CHECK, N_MIN = 0.1, 40, 100


def decision_snrs(tag):
    t = open(os.path.join(C.CONF, "results", f"tables_D2_{tag}.txt")).read()
    m = re.search(r"M-ours-bstar -> M-ours-dscore-C-V1.*?\n\s*decision SNRs \[([^\]]*)\]", t, re.S)
    return [float(x.strip("' ")) for x in m.group(1).split(",")] if m and m.group(1).strip() else []


def nn_dist(h, X):
    """min_j ||h_i - X_j||^2 / ||h_i||^2 for every row of h."""
    a2 = (np.abs(h) ** 2).sum(1)
    best = np.full(len(h), np.inf)
    for i in range(0, len(X), 20000):
        B = X[i:i + 20000]
        best = np.minimum(best, (a2[:, None] + (np.abs(B) ** 2).sum(1)[None] - 2 * (h @ B.conj().T).real).min(1))
    return np.maximum(best, 0) / a2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="DMCB16e4")
    ap.add_argument("--prior", default="DMC")
    ap.add_argument("--cell", default="C2")
    ap.add_argument("--ntrain", type=int, default=160000)
    a = ap.parse_args()
    runner._init(a.tag)
    c = C.CELLS[a.cell]
    data, _, _ = load_raw("D2", root=os.path.join(C.CONF, f"raw_{a.tag}"))
    snrs = decision_snrs(a.tag)
    X = A.training_set("D2", a.prior, c["Nr"], c["Nt"], a.ntrain)
    L = [C.header("D2", extra=[f"content     : dmc_leak_strata.py -- leakage strata of raw_{a.tag} (prior {a.prior}, cell {a.cell}), "
                               f"REPORT-ONLY ({'NEXT_EXPERIMENTS_DMC16e4 §1' if a.prior == 'DMC' else 'the NEXT_EXPERIMENTS_DMC16e4 §1 definition, registered for ' + a.prior}): d = min_train ||h - h_train||^2 / ||h||^2, N' = {a.ntrain} "
                               f"(stream 7), strata d < {THR} / d >= {THR}; decision SNRs {snrs} from tables_D2_{a.tag}.txt"]), ""]
    tot = {s: np.zeros(4) for s in ("lt", "ge")}
    ok = True
    for snr in snrs:
        P = runner.build_point("D2", a.cell, a.prior, snr, a.ntrain)
        code, gen, first = P["code"], P["gen"], P["arms"]["R5-genie"]
        b, v, g = (fails(data, a.cell, snr, arm) for arm in ARMS)
        key = [k for k in data if k[0] == a.cell and k[2] == snr][0]
        ref = np.asarray(data[key]["R5-genie"]["blk_err"])
        rng = C.trial_rng("D2", a.prior, c["Nr"], c["T"], c["Tp"], snr)
        h = np.empty((len(b), c["Nr"] * c["Nt"]), complex)
        same = True
        for tr in range(len(b)):
            H = gen.sample(rng)
            u = rng.integers(0, 2, code.K)
            perm = rng.permutation(code.Ns)
            _, Y = first.transmit(u, perm, H, rng)
            h[tr] = H.reshape(-1, order="F")
            if tr < N_CHECK:
                same &= np.array_equal(np.asarray(first.run(Y, H, u, perm, C.N_ITER)["blk_err"]), ref[tr], equal_nan=True)
        ok &= same
        d = nn_dist(h, X)
        L.append(f"{snr:+.0f} dB  n={len(b)}  alignment (R5-genie, first {N_CHECK} replayed trials vs raw, bit-identical): "
                 f"{'OK' if same else 'MISMATCH'};  d median {np.median(d):.4f}, share d < {THR} = {np.mean(d < THR):.3f}")
        for lab, m in (("lt", d < THR), ("ge", d >= THR)):
            row = np.array([m.sum(), b[m].sum(), v[m].sum(), g[m].sum()])
            tot[lab] += row
            L.append(_fmt(f"    d {'<' if lab == 'lt' else '>='} {THR}", row))
    L.append(f"pooled over the {len(snrs)} decision SNRs")
    for lab in ("lt", "ge"):
        L.append(_fmt(f"    d {'<' if lab == 'lt' else '>='} {THR}", tot[lab]))
    L += ["", f"alignment {'OK at every SNR' if ok else 'MISMATCH -- the strata are NOT attached to the right trials; do not use'}",
          "report-only: no label, no test, no CI; interpretation is the user's."]
    out = os.path.join(C.CONF, "results", "review_next", f"{a.tag}_leak_strata.txt")
    open(out, "w").write("\n".join(L) + "\n")
    print("\n".join(L))
    return 0 if ok else 1


def _fmt(lab, row):
    n, b, v, g = (int(x) for x in row)
    r = "(n < %d: R not written)" % N_MIN if n < N_MIN else ("R = n/a (b* - genie <= 0)" if b - g <= 0 else f"R = {(b - v) / (b - g):.3f}")
    return f"{lab:14s} n={n:5d}  failures b* {b:4d}  V1 {v:4d}  genie {g:4d}  {r}"


if __name__ == "__main__":
    sys.exit(main())
