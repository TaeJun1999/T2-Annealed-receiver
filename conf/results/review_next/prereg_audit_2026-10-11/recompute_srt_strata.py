"""recompute_srt_strata.py -- independent re-derivation of the two REPORT-ONLY strata tables of NEXT_EXPERIMENTS_SRT16e4.md §6.2
(SRTB16e4_leak_strata.txt, SRTB16e4_rank_strata.txt) WITHOUT running code/dmc_leak_strata.py or code/rank_strata.py (both write
into results/review_next/ unconditionally).  The trial stream is replayed exactly as those scripts (and runner.run_task) do:
sample -> integers(0, 2, K) -> permutation(Ns) -> transmit, on common.trial_rng("D2", "SRT", 8, 16, 4, snr); the first 40 replayed
trials are run through R5-genie and compared bit for bit with the raw blk_err (alignment).  d = min_train ||h - h_train||^2/||h||^2
over the N' = 160000 training channels (stream 7; arms.training_set) is computed with a plain non-expanded loop for the first 24
trials as a check of the block formula; the rank share s1^2 / sum s^2 by numpy SVD.  Failures of b*, V1, genie read directly
from the raw chunks.  Every number of the two record tables is compared (DIFF lines).

usage (cwd = ~/t2/conf):  CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=16 ~/miniforge3/envs/torch/bin/python -B \
    results/review_next/prereg_audit_2026-10-11/recompute_srt_strata.py > results/review_next/prereg_audit_2026-10-11/recompute_srt_strata.out
"""
import glob
import os
import re
import sys

import numpy as np

CONF = "/home/HTJ/t2/conf"
sys.path.insert(0, os.path.join(CONF, "code"))
import common as C  # noqa: E402
import arms as A  # noqa: E402
import runner  # noqa: E402

N, CHUNK, THR, N_CHECK = 2560, 40, 0.1, 40
BS, V1, GEN = "M-ours-bstar", "M-ours-dscore-C-V1", "R5-genie"
EDGES = ((0.95, 1.01), (0.80, 0.95), (0.60, 0.80), (0.0, 0.60))

# ----------------------------------------------------------------------------- record values (§6.2 tables)
EXP_LEAK = {9: (0.0545, 0.597, (1529, 1294, 1231, 1188, 0.594), (1031, 317, 273, 228, 0.494)),
            12: (0.0577, 0.607, (1553, 1241, 1189, 1143, 0.531), (1007, 254, 202, 184, 0.743)),
            15: (0.0520, 0.620, (1587, 1243, 1169, 1145, 0.755), (973, 187, 162, 132, 0.455)),
            "pooled": (None, None, (4669, 3778, 3589, 3476, 0.626), (3011, 758, 637, 544, 0.565))}
EXP_RANK = {  # snr: [(n, share, genie, V1, b*, BLER strings "g/V1/b*")] for the 4 strata
    -3: [(2063, 0.806, 1955, 2029, 2043, "0.948 / 0.984 / 0.990"), (386, 0.151, 121, 255, 303, "0.313 / 0.661 / 0.785"),
         (107, 0.042, 14, 34, 56, "0.131 / 0.318 / 0.523"), (4, 0.002, 1, 2, 2, "0.250 / 0.500 / 0.500")],
    9: [(2014, 0.787, 1410, 1487, 1587, "0.700 / 0.738 / 0.788"), (422, 0.165, 6, 13, 23, "0.014 / 0.031 / 0.055"),
        (117, 0.046, 0, 3, 1, "0.000 / 0.026 / 0.009"), (7, 0.003, 0, 1, 0, "0.000 / 0.143 / 0.000")],
    12: [(2022, 0.790, 1322, 1387, 1473, "0.654 / 0.686 / 0.728"), (410, 0.160, 3, 2, 15, "0.007 / 0.005 / 0.037"),
         (120, 0.047, 2, 2, 7, "0.017 / 0.017 / 0.058"), (8, 0.003, 0, 0, 0, "0.000 / 0.000 / 0.000")],
    15: [(2055, 0.803, 1274, 1326, 1419, "0.620 / 0.645 / 0.691"), (401, 0.157, 3, 4, 10, "0.007 / 0.010 / 0.025"),
         (99, 0.039, 0, 1, 1, "0.000 / 0.010 / 0.010"), (5, 0.002, 0, 0, 0, "0.000 / 0.000 / 0.000")]}
EXP_LABEL_SHARES = {9: 0.787, 12: 0.790, 15: 0.803}      # §6.1 label appendix "(판정점 시행에서는 0.787 / 0.790 / 0.803)"
EXP_LABEL_LEAK = {9: 0.597, 12: 0.607, 15: 0.620}         # §6.1 label appendix "(판정점 시행에서는 0.597 / 0.607 / 0.620)"

OUT, NCHECK = [], [0, 0]


def p(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s)


def chk(label, got, exp, tol=0):
    NCHECK[0] += 1
    ok = (abs(got - exp) <= tol) if isinstance(exp, (int, float)) and not isinstance(exp, bool) else got == exp
    if not ok:
        NCHECK[1] += 1
        p(f"    DIFF  {label}: recomputed {got!r}  record {exp!r}")
    return ok


def raw_fails(snr, arm):
    fs = glob.glob(os.path.join(CONF, "raw_SRTB16e4", f"D2_C2_SRT_Nr8_T16_Tp4_eig_snr{snr}_skip*_n*.npz"))
    ch = sorted((int(re.search(r"_skip(\d+)_", f)[1]), f) for f in fs)
    be = np.concatenate([np.load(f)[f"{arm}|blk_err"] for _, f in ch]).astype(float)
    return np.where(np.isfinite(be), be, 1.0)


def nn_dist(h, X):
    a2 = (np.abs(h) ** 2).sum(1)
    best = np.full(len(h), np.inf)
    for i in range(0, len(X), 20000):
        B = X[i:i + 20000]
        best = np.minimum(best, (a2[:, None] + (np.abs(B) ** 2).sum(1)[None] - 2 * (h @ B.conj().T).real).min(1))
    return np.maximum(best, 0) / a2


def main():
    p("# recompute_srt_strata.py -- trial-stream replay; leak strata (d < 0.1 / d >= 0.1) and rank strata (share of s1^2)")
    runner._init("SRTB16e4")
    c = C.CELLS["C2"]
    X = A.training_set("D2", "SRT", c["Nr"], c["Nt"], 160000)
    p(f"  training set (stream 7): {X.shape} {X.dtype}; mean ||x||^2/(NrNt) = {np.mean(np.abs(X) ** 2) :.5f}")
    tot = {"lt": np.zeros(4), "ge": np.zeros(4)}
    for snr in (-3, 9, 12, 15):
        P = runner.build_point("D2", "C2", "SRT", snr, 160000)
        code, gen, first = P["code"], P["gen"], P["arms"][GEN]
        b, v, g = (raw_fails(snr, a)[:, -1] for a in (BS, V1, GEN))
        ref = raw_fails(snr, GEN)
        rng = C.trial_rng("D2", "SRT", c["Nr"], c["T"], c["Tp"], snr)
        h = np.empty((N, c["Nr"] * c["Nt"]), complex)
        sv = np.empty((N, c["Nt"]))
        same = True
        for tr in range(N):
            H = gen.sample(rng)
            u = rng.integers(0, 2, code.K)
            perm = rng.permutation(code.Ns)
            _, Y = first.transmit(u, perm, H, rng)
            h[tr] = H.reshape(-1, order="F")
            sv[tr] = np.linalg.svd(H, compute_uv=False) ** 2
            if tr < N_CHECK:
                same &= np.array_equal(np.asarray(first.run(Y, H, u, perm, C.N_ITER)["blk_err"]), ref[tr], equal_nan=True)
        chk(f"{snr:+d} dB alignment (R5-genie, first 40 replayed trials == raw blk_err)", same, True)
        share = sv[:, 0] / sv.sum(1)
        p(f"\n  {snr:+d} dB: share median {np.median(share):.4f}; BLER genie {g.mean():.3f} V1 {v.mean():.3f} b* {b.mean():.3f}")
        for (lo, hi), e in zip(EDGES, EXP_RANK[snr]):
            m = (share >= lo) & (share < hi)
            n_, sh = int(m.sum()), m.mean()
            fg, fv, fb = int(g[m].sum()), int(v[m].sum()), int(b[m].sum())
            bl = f"{g[m].mean():.3f} / {v[m].mean():.3f} / {b[m].mean():.3f}" if n_ else "(empty)"
            p(f"    share [{lo:.2f}, {min(hi, 1):.2f})  n={n_:5d} ({sh:.3f})  BLER g/V1/b* {bl}  failures {fg} / {fv} / {fb}")
            chk(f"rank {snr:+d} [{lo:.2f},{min(hi,1):.2f}) n", n_, e[0]); chk(f"rank {snr:+d} [{lo:.2f}) share (3 dp)", round(sh, 3), e[1])
            chk(f"rank {snr:+d} [{lo:.2f}) failures g/V1/b*", (fg, fv, fb), (e[2], e[3], e[4])); chk(f"rank {snr:+d} [{lo:.2f}) BLER strings", bl, e[5])
        if snr in EXP_LABEL_SHARES:
            chk(f"§6.1 share >= 0.95 at {snr:+d} dB (3 dp)", round(float(np.mean(share >= 0.95)), 3), EXP_LABEL_SHARES[snr])
        if snr == 15:
            top = (share >= 0.95)
            chk("pred 12a: genie BLER in share >= 0.95 at +15 dB >= 0.25", g[top].mean() >= 0.25, True)
            low = share < 0.80
            p(f"    +15 dB share < 0.80: n {int(low.sum())}, genie failures {int(g[low].sum())} -> {g[low].sum() / low.sum():.4f}")
            chk("pred 12b: genie failures / n over the two share < 0.80 strata at +15 dB <= 0.02", g[low].sum() / low.sum() <= 0.02, True)
            chk("pred 12b arithmetic as written ((0 + 0) / (99 + 5))", (int(g[low].sum()), int(low.sum())), (0, 104))
        if snr in EXP_LEAK:
            d = nn_dist(h, X)
            # plain-loop check of the block formula on 24 trials
            dd = np.array([np.min(np.sum(np.abs(X - h[i]) ** 2, 1)) / np.sum(np.abs(h[i]) ** 2) for i in range(24)])
            p(f"    leak: d median {np.median(d):.4f}, share d < 0.1 = {np.mean(d < THR):.3f}; plain-loop check max|diff| {np.max(np.abs(dd - d[:24])):.1e}")
            e = EXP_LEAK[snr]
            chk(f"leak {snr:+d} d median (4 dp)", round(float(np.median(d)), 4), e[0]); chk(f"leak {snr:+d} share d<0.1 (3 dp)", round(float(np.mean(d < THR)), 3), e[1])
            chk(f"§6.1 leak share at {snr:+d} dB", round(float(np.mean(d < THR)), 3), EXP_LABEL_LEAK[snr])
            for lab, m, ee in (("lt", d < THR, e[2]), ("ge", d >= THR, e[3])):
                row = np.array([m.sum(), b[m].sum(), v[m].sum(), g[m].sum()])
                tot[lab] += row
                n_, fb, fv, fg = (int(x) for x in row)
                R = (fb - fv) / (fb - fg) if fb - fg > 0 else float("nan")
                p(f"    d {'<' if lab == 'lt' else '>='} 0.1  n={n_}  b* {fb}  V1 {fv}  genie {fg}  R = {R:.3f}")
                chk(f"leak {snr:+d} {lab} (n, b*, V1, genie)", (n_, fb, fv, fg), ee[:4]); chk(f"leak {snr:+d} {lab} R (3 dp)", round(R, 3), ee[4])
    for lab, ee in (("lt", EXP_LEAK["pooled"][2]), ("ge", EXP_LEAK["pooled"][3])):
        n_, fb, fv, fg = (int(x) for x in tot[lab])
        R = (fb - fv) / (fb - fg)
        p(f"  pooled d {'<' if lab == 'lt' else '>='} 0.1  n={n_}  b* {fb}  V1 {fv}  genie {fg}  R = {R:.3f}")
        chk(f"leak pooled {lab} (n, b*, V1, genie)", (n_, fb, fv, fg), ee[:4]); chk(f"leak pooled {lab} R (3 dp)", round(R, 3), ee[4])
    p(f"\n## SUMMARY: {NCHECK[0]} values checked, {NCHECK[1]} differ from the record")
    return 0 if NCHECK[1] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
