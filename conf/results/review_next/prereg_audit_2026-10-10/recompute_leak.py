"""recompute_leak.py -- independent re-derivation of results/review_next/DMCB16e4_leak_strata.txt for the RECORD AUDIT.

Does NOT import or run code/dmc_leak_strata.py and writes nothing outside the audit folder.  It replays the trial stream of
raw_DMCB16e4 at the three decision SNRs exactly as runner.run_task does (sample -> integers(0,2,K) -> permutation(Ns) ->
transmit), using runner.build_point only as the generator / arm loader, and
  * checks the replay against the raw R5-genie blk_err on the first 40 trials AND on a later chunk (trials 1000..1039:
    a check the registered script does not make, since its N_CHECK = 40 covers chunk 0 only),
  * computes d = min_train ||h - h_train||^2 / ||h||^2 with its own blocked implementation, verifies 24 trials of it with the
    direct (un-expanded) formula, and
  * recomputes the strata (d < 0.1 / d >= 0.1): n, failures of b* / V1 / genie, R -- compared with the committed file.
usage (cwd = ~/t2/conf):  CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=8 ~/miniforge3/envs/torch/bin/python \
    results/review_next/prereg_audit_2026-10-10/recompute_leak.py > results/review_next/prereg_audit_2026-10-10/recompute_leak.out
"""
import glob
import os
import re
import sys

import numpy as np

CONF = "/home/HTJ/t2/conf"
sys.path.insert(0, os.path.join(CONF, "code"))
import common as C          # noqa: E402
import arms as A            # noqa: E402
import runner               # noqa: E402

TAG, PRIOR, CELL, NTRAIN, THR = "DMCB16e4", "DMC", "C2", 160000, 0.1
DP = [9.0, 12.0, 15.0]
BS, V1, GEN = "M-ours-bstar", "M-ours-dscore-C-V1", "R5-genie"
COMMITTED = os.path.join(CONF, "results", "review_next", f"{TAG}_leak_strata.txt")


def raw_point(snr):
    """direct numpy read: {arm: blk_err (2560, 16)} of one SNR, chunks in skip order."""
    fs = sorted(glob.glob(os.path.join(CONF, f"raw_{TAG}", f"D2_C2_DMC_Nr8_T16_Tp4_eig_snr{int(snr)}_skip*_n40.npz")),
                key=lambda f: int(re.search(r"_skip(\d+)_", f)[1]))
    zs = [np.load(f) for f in fs]
    return {a: np.concatenate([z[f"{a}|blk_err"] for z in zs]) for a in (BS, V1, GEN)}


def nn_dist_blocked(h, X, blk=16384):
    a2 = (np.abs(h) ** 2).sum(1)
    best = np.full(len(h), np.inf)
    for i in range(0, len(X), blk):
        B = X[i:i + blk]
        d2 = a2[:, None] + (np.abs(B) ** 2).sum(1)[None, :] - 2.0 * np.real(h @ B.conj().T)
        best = np.minimum(best, d2.min(1))
    return np.maximum(best, 0.0) / a2


def nn_dist_direct(h, X):
    """un-expanded formula, a few rows only."""
    return np.array([np.min(np.sum(np.abs(X - hi) ** 2, axis=1)) / np.sum(np.abs(hi) ** 2) for hi in h])


def parse_committed():
    t = open(COMMITTED).read()
    out = {}
    for m in re.finditer(r"^([+-]\d+) dB  n=(\d+)  alignment .*?: (\w+);  d median ([\d.]+), share d < 0\.1 = ([\d.]+)\n"
                         r"\s+d < 0\.1\s+n=\s*(\d+)\s+failures b\*\s+(\d+)\s+V1\s+(\d+)\s+genie\s+(\d+)\s+R = ([\d.]+)\n"
                         r"\s+d >= 0\.1\s+n=\s*(\d+)\s+failures b\*\s+(\d+)\s+V1\s+(\d+)\s+genie\s+(\d+)\s+R = ([\d.]+)", t, re.M):
        g = m.groups()
        out[float(g[0])] = dict(align=g[2], med=float(g[3]), share=float(g[4]),
                                lt=tuple(int(x) for x in g[5:9]) + (float(g[9]),), ge=tuple(int(x) for x in g[10:14]) + (float(g[14]),))
    m = re.search(r"pooled over the 3 decision SNRs\n\s+d < 0\.1\s+n=\s*(\d+)\s+failures b\*\s+(\d+)\s+V1\s+(\d+)\s+genie\s+(\d+)\s+R = ([\d.]+)\n"
                  r"\s+d >= 0\.1\s+n=\s*(\d+)\s+failures b\*\s+(\d+)\s+V1\s+(\d+)\s+genie\s+(\d+)\s+R = ([\d.]+)", t)
    g = m.groups()
    out["pooled"] = dict(lt=tuple(int(x) for x in g[0:4]) + (float(g[4]),), ge=tuple(int(x) for x in g[5:9]) + (float(g[9]),))
    return out


def main():
    exp = parse_committed()
    print(f"# recompute_leak.py -- committed file parsed: {sorted(exp, key=str)}")
    runner._init(TAG)
    c = C.CELLS[CELL]
    X = A.training_set("D2", PRIOR, c["Nr"], c["Nt"], NTRAIN)
    print(f"training set: shape {X.shape} dtype {X.dtype}; mean ||x||^2/(NrNt) = {np.mean(np.abs(X) ** 2):.6f}")
    # vec convention: sample(rng) reshaped column-major == sample_vecs(rng, 1)[0] (registration §1)
    g0 = C.make_gen("D2", PRIOR, c["Nr"], c["Nt"])
    # the DMC generator refuses unknown seed layouts (block split): use a legitimate trial stream (+6 dB) twice
    r1, r2 = (C.trial_rng("D2", PRIOR, c["Nr"], c["T"], c["Tp"], 6.0) for _ in range(2))
    print(f"vec convention check: sample().reshape(F) == sample_vecs()[0]: "
          f"{np.array_equal(g0.sample(r1).reshape(-1, order='F'), g0.sample_vecs(r2, 1)[0])}")
    nck, ndiff = 0, 0

    def chk(label, got, e, tol=0):
        nonlocal nck, ndiff
        nck += 1
        ok = abs(got - e) <= tol if isinstance(e, (int, float)) else got == e
        if not ok:
            ndiff += 1
            print(f"    DIFF {label}: recomputed {got!r} committed {e!r}")

    tot = {"lt": np.zeros(4, int), "ge": np.zeros(4, int)}
    for snr in DP:
        raw = raw_point(snr)
        P = runner.build_point("D2", CELL, PRIOR, snr, NTRAIN)
        code, gen, first = P["code"], P["gen"], P["arms"][GEN]
        rng = C.trial_rng("D2", PRIOR, c["Nr"], c["T"], c["Tp"], snr)
        n = len(raw[GEN])
        h = np.empty((n, c["Nr"] * c["Nt"]), complex)
        align = {0: True, 1000: True}
        for tr in range(n):
            H = gen.sample(rng)
            u = rng.integers(0, 2, code.K)
            perm = rng.permutation(code.Ns)
            _, Y = first.transmit(u, perm, H, rng)
            h[tr] = H.reshape(-1, order="F")
            for s0 in align:
                if s0 <= tr < s0 + 40:
                    align[s0] &= np.array_equal(np.asarray(first.run(Y, H, u, perm, C.N_ITER)["blk_err"]), raw[GEN][tr], equal_nan=True)
        d = nn_dist_blocked(h, X)
        ix = np.linspace(0, n - 1, 24).astype(int)
        dd = nn_dist_direct(h[ix], X)
        print(f"\n{snr:+.0f} dB: replay alignment R5-genie trials 0..39 {align[0]}, trials 1000..1039 {align[1000]}; "
              f"d (blocked) vs direct on 24 trials: max |diff| {np.max(np.abs(d[ix] - dd)):.2e}")
        med, share = float(np.median(d)), float(np.mean(d < THR))
        print(f"  d median {med:.4f}  share d < {THR} = {share:.3f}   (committed {exp[snr]['med']}, {exp[snr]['share']}, alignment {exp[snr]['align']})")
        chk(f"{snr:+.0f} alignment OK (committed says)", exp[snr]["align"], "OK")
        chk(f"{snr:+.0f} d median (4 dp)", round(med, 4), exp[snr]["med"])
        chk(f"{snr:+.0f} share d<0.1 (3 dp)", round(share, 3), exp[snr]["share"])
        for lab, m in (("lt", d < THR), ("ge", d >= THR)):
            b, v, g = (int(raw[a][m, -1].sum()) for a in (BS, V1, GEN))
            row = (int(m.sum()), b, v, g)
            R = (b - v) / (b - g) if b - g > 0 else float("nan")
            tot[lab] += np.array(row)
            print(f"  d {'<' if lab == 'lt' else '>='} {THR}: n {row[0]}  b* {b}  V1 {v}  genie {g}  R {R:.3f}   (committed {exp[snr][lab]})")
            chk(f"{snr:+.0f} {lab} counts", row, exp[snr][lab][:4])
            chk(f"{snr:+.0f} {lab} R (3 dp)", round(R, 3), exp[snr][lab][4])
    print("\npooled over the 3 decision SNRs")
    for lab in ("lt", "ge"):
        nn_, b, v, g = (int(x) for x in tot[lab])
        R = (b - v) / (b - g)
        print(f"  d {'<' if lab == 'lt' else '>='} {THR}: n {nn_}  b* {b}  V1 {v}  genie {g}  R {R:.3f}   (committed {exp['pooled'][lab]})")
        chk(f"pooled {lab} counts", (nn_, b, v, g), exp["pooled"][lab][:4])
        chk(f"pooled {lab} R (3 dp)", round(R, 3), exp["pooled"][lab][4])
    print(f"\n## SUMMARY: {nck} values checked, {ndiff} differ from the committed leak-strata file")
    return 0 if ndiff == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
