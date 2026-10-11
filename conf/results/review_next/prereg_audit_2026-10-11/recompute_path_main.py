"""recompute_path_main.py -- independent recomputation for the RECORD AUDIT of NEXT_EXPERIMENTS_PATH16e4.md §6.1 / §6.2 (main run,
prior SRP).  Adapted from recompute_srt_main.py (same method): the raw chunk files of raw_SRPB16e4 / raw_SRPB16e4last (+ raw_B16e4k
for the D2 reference) are read DIRECTLY with numpy (no s6_gen.py, no tables_*.txt); failure counts / BLER@16 (the §6.2 table), decision
SNRs by the §1 rule, exact two-sided paired sign tests + power guard + label, best-vs-last V1, recovery R + paired bootstrap 90 % CI
(recovery_ci.boot re-implemented: default_rng(20260926), B = 2000, 5/95 pct), the saturation guard, Delta R, SNR@0.1 by the tool's
log-linear rule (Demo/exp_0921_analysis.snr_at re-implemented), F3 guard firing, raw meta, chunk plan, R5-genie bit identity,
checkpoint facts.  analysis.load_raw is used ONLY as a cross-check.  DIFF lines where the record differs.

usage (cwd = ~/t2/conf):  CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=3 ~/miniforge3/envs/torch/bin/python -B \
    results/review_next/prereg_audit_2026-10-11/recompute_path_main.py > results/review_next/prereg_audit_2026-10-11/recompute_path_main.out
"""
import glob
import math
import os
import re
import sys

import numpy as np

CONF = "/home/HTJ/t2/conf"
SNRS = [-3, 0, 3, 6, 9, 12, 15]
N, CHUNK = 2560, 40
PLAN = [(CHUNK * k, CHUNK) for k in range(N // CHUNK)]
ARMS = ["R0-pilot", "R1-turbo", "R2-ours-G", "R3-bigamp", "R4-scvamp", "R4-llr", "R5-genie", "M-ours-gmm32", "M-ours-bstar",
        "M-ours-dscore-C-V1", "M-ours-dscore-C-V0", "M-ours-dscore-C-V4", "M-ours-dscore-C-V4b", "M-ours-bstar-scalar"]
BS, V1, GEN, R2, SC = "M-ours-bstar", "M-ours-dscore-C-V1", "R5-genie", "R2-ours-G", "M-ours-bstar-scalar"
V0, V4, V4B = "M-ours-dscore-C-V0", "M-ours-dscore-C-V4", "M-ours-dscore-C-V4b"
MIN_DISC, B_BOOT, SEED = 6, 2000, 20260926

# ----------------------------------------------------------------------------- values transcribed in the record (§6.1 / §6.2)
EXP_FAILS = {
    V1: ([812, 204, 24, 4, 0, 0, 0], "0.317 0.080 0.009 0.002 0.000 0.000 0.000"),
    "V1last": ([823, 201, 22, 3, 0, 0, 0], "0.321 0.079 0.009 0.001 0.000 0.000 0.000"),
    V4: ([830, 203, 28, 5, 0, 0, 0], "0.324 0.079 0.011 0.002 0.000 0.000 0.000"),
    V4B: ([843, 208, 28, 5, 0, 0, 0], "0.329 0.081 0.011 0.002 0.000 0.000 0.000"),
    BS: ([1356, 498, 133, 29, 3, 2, 0], "0.530 0.195 0.052 0.011 0.001 0.001 0.000"),
    SC: ([1338, 482, 121, 26, 2, 2, 0], "0.523 0.188 0.047 0.010 0.001 0.001 0.000"),
    "M-ours-gmm32": ([1467, 553, 125, 29, 3, 2, 0], "0.573 0.216 0.049 0.011 0.001 0.001 0.000"),
    R2: ([1491, 544, 139, 27, 1, 2, 0], "0.582 0.212 0.054 0.011 0.000 0.001 0.000"),
    "R1-turbo": ([1792, 930, 283, 60, 6, 6, 0], "0.700 0.363 0.111 0.023 0.002 0.002 0.000"),
    "R0-pilot@1": ([2351, 1755, 882, 313, 53, 30, 4], "0.918 0.686 0.345 0.122 0.021 0.012 0.002"),
    "R0-pilot": ([1767, 776, 215, 42, 6, 2, 0], "0.690 0.303 0.084 0.016 0.002 0.001 0.000"),
    "R4-scvamp": ([1893, 1148, 511, 227, 59, 33, 14], "0.739 0.448 0.200 0.089 0.023 0.013 0.005"),
    "R3-bigamp": ([2311, 1583, 763, 410, 298, 356, 332], "0.903 0.618 0.298 0.160 0.116 0.139 0.130"),
    "R4-llr": ([2193, 1938, 1968, 1998, 1616, 1084, 539], "0.857 0.757 0.769 0.780 0.631 0.423 0.211"),
    V0: ([2560, 2560, 2560, 2559, 2553, 2484, 1345], "1.000 1.000 1.000 1.000 0.997 0.970 0.525"),
    GEN: ([428, 81, 7, 1, 0, 0, 0], "0.167 0.032 0.003 0.000 0.000 0.000 0.000")}
EXP_PAIRS = {  # (tag, x, y): ([a:b per decision SNR], pooled a:b, [p per SNR as printed] or None, pooled p as printed or None)
    ("best", BS, V1): ([(606, 62), (321, 27), (117, 8)], (1044, 97), ["4.3e-113", "5.2e-65", "5.9e-26"], "4.1e-201"),
    ("last", BS, V1): ([(593, 60), (320, 23), (118, 7)], (1031, 90), ["3.4e-111", "4.5e-68", "4e-27"], "3.8e-203"),
    ("best", BS, SC): ([(95, 77), (72, 56), (33, 21)], (200, 154), ["0.19", "0.18", "0.13"], "0.017"),
    ("best", R2, BS): ([(197, 62), (115, 69), (31, 25)], (343, 156), ["1.5e-17", "0.00086", "0.5"], None),
    ("best", BS, V4): ([(595, 69), (320, 25), (113, 8)], (1028, 102), None, None),
    ("best", BS, V4B): ([(581, 68), (314, 24), (114, 9)], (1009, 101), None, None),
    ("best", BS, V0): ([(0, 1204), (0, 2062), (0, 2427)], (0, 5693), None, None),
    ("best", V1, GEN): ([(422, 38), (137, 14)], (559, 52), None, None),
    ("best", BS, GEN): ([(951, 23), (427, 10)], (1378, 33), None, None)}
EXP_BEST_LAST = ([(17, 28), (14, 11), (4, 2)], (35, 41), [0.135, 0.69, 0.688], 0.567)
EXP_DP = [-3, 0, 3]
EXP_REC = {"best": {-3: (1356, 812, 428, 0.586, 0.554, 0.618), 0: (498, 204, 81, 0.705, 0.661, 0.749),
                    3: (133, 24, 7, 0.865, 0.801, 0.928), "pooled": (1987, 1040, 516, 0.644, 0.620, 0.667)},
           "last": {-3: (1356, 823, 428, 0.574, 0.542, 0.604), "pooled": (1987, 1046, 516, 0.640, 0.616, 0.662)},
           "D2-3": (623, 371, 87, 0.470), "D2-303": (864, 488, 125, 0.509), "dR1": 0.116, "dR1last": 0.104, "dR2": 0.135,
           "gap3": (384, 928), "gapD2_3": (284, 536)}
EXP_SAT = dict(bler=0.530, fires=False)
EXP_GUARD_V0 = {"best": [2560, 2560, 2560, 2559, 2546, 2454, 2020], "last": [2560, 2560, 2560, 2559, 2543, 2470, 2054]}
EXP_GUARD_V0_RATE = {"best": [1.000, 1.000, 1.000, 1.000, 0.995, 0.959, 0.789],
                     "last": [1.000, 1.000, 1.000, 1.000, 0.993, 0.965, 0.802]}
EXP_GUARD_NEVER = sorted([a for a in ARMS if a not in (V0, GEN)])
EXP_META = dict(git="99039ef5", ntrain=160000, bstar="kron", kron_K=4096, ll_val=244.1932863626755,
                ckpt={"best": "sha256[:16]=ac4699c78b3e2d80 epoch=694 best_epoch=694 role=best 8x4",
                      "last": "sha256[:16]=f82762a7002308db epoch=714 best_epoch=694 role=last 8x4"})
EXP_SUMS = dict(dp=(1040, 1061, 1079), all=(1044, 1066, 1084))
EXP_SNR01 = {"best": {GEN: "-2.1", V1: "-0.5", V4: "-0.5", V4B: "-0.4", SC: "1.4", BS: "1.5", "M-ours-gmm32": "1.6", R2: "1.7",
                      "R0-pilot": "2.6", "R1-turbo": "3.2", "R4-scvamp": "5.6", "R0-pilot@1": "6.3",
                      "R3-bigamp": ">15", "R4-llr": ">15", V0: ">15"}}
EXP_SNR01_2DP = {GEN: -2.07, V1: -0.49, V4: -0.49, V4B: -0.45, SC: 1.37, BS: 1.51, "M-ours-gmm32": 1.55, R2: 1.66,
                 "R0-pilot": 2.59, "R1-turbo": 3.19, "R4-scvamp": 5.56, "R0-pilot@1": 6.34}
EXP_TRAIN = dict(best_epoch=694, last_epoch=714, best_val=0.1495504230260849, stopped="patience", split_hash="27af93705c6dc289",
                 rung="D2SXSRP160000", attempt=1)
EXP_RANKCAVEAT = {-3: (1356, 1491), 0: (498, 544), 3: (133, 139)}   # §6.1 'b* close to R2' numbers

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


def sign_p(a, b):
    n = a + b
    return 1.0 if n == 0 else min(1.0, 2 * sum(math.comb(n, i) for i in range(min(a, b) + 1)) / 2 ** n)


def boot(cols):
    rng = np.random.default_rng(SEED)
    n = len(cols[0][0])
    out = np.empty(B_BOOT)
    for i in range(B_BOOT):
        idx = rng.integers(0, n, n)
        bs = sum(b[idx].sum() for b, _, _ in cols); vs = sum(v[idx].sum() for _, v, _ in cols); gs = sum(g[idx].sum() for _, _, g in cols)
        out[i] = (bs - vs) / (bs - gs) if bs - gs > 0 else np.nan
    ok = np.isfinite(out)
    lo, hi = np.percentile(out[ok], [5, 95])
    return lo, hi, int((~ok).sum())


def load_tag(root, prior, pil):
    pts, meta, problems, run_git = {}, {}, [], set()
    for snr in SNRS:
        fs = glob.glob(os.path.join(root, f"D2_C2_{prior}_Nr8_T16_Tp4_{pil}_snr{snr}_skip*_n*.npz"))
        ch = sorted((int(re.search(r"_skip(\d+)_n(\d+)\.npz$", f)[1]), int(re.search(r"_skip(\d+)_n(\d+)\.npz$", f)[2]), f) for f in fs)
        if [(s, n) for s, n, _ in ch] != PLAN:
            problems.append(f"{os.path.basename(root)} snr {snr}: chunk plan != {{(40k,40)}} ({len(ch)} chunks)")
        zs = [np.load(f) for _, _, f in ch]
        d, keys = {}, sorted({k for z in zs for k in z.files})
        for k in keys:
            if k.startswith("run|") or k.startswith("meta|"):
                vals = {str(z[k].item()) if z[k].shape == () else str(z[k]) for z in zs if k in z.files}
                if k == "run|skip":
                    if sorted(int(float(v)) for v in vals) != [s for s, _ in PLAN]:
                        problems.append(f"{os.path.basename(root)} snr {snr}: run|skip set != plan")
                elif k == "run|snr":
                    if vals != {f"{float(snr)}"}:
                        problems.append(f"{os.path.basename(root)} snr {snr}: run|snr {vals}")
                elif len(vals) != 1:
                    problems.append(f"{os.path.basename(root)} snr {snr}: '{k}' differs across chunks: {sorted(vals)[:3]}")
                if k == "run|git":
                    run_git |= vals
                meta.setdefault(k, set()).update(vals)
                continue
            if "|" not in k:
                continue
            arm, q = k.split("|", 1)
            if q == "failed":
                tot = sum(int(np.asarray(z[k]).sum()) for z in zs if k in z.files)
                problems.append(f"{os.path.basename(root)} snr {snr}: arm {arm} has a '|failed' key (raised trials: {tot})")
                continue
            if any(k not in z.files for z in zs):
                problems.append(f"{os.path.basename(root)} snr {snr}: '{k}' missing from some chunk")
                continue
            a = np.concatenate([np.asarray(z[k]) for z in zs])
            if a.ndim >= 1 and len(a) != N:
                problems.append(f"{os.path.basename(root)} snr {snr}: '{k}' has {len(a)} rows")
            d.setdefault(arm, {})[q] = a
        for arm, v in d.items():
            if "blk_err" in v:
                be = v["blk_err"].astype(float)
                bad = ~np.isfinite(be)
                if bad.any():
                    problems.append(f"{os.path.basename(root)} snr {snr}: {arm} non-finite blk_err rows {int(bad[:, -1].sum())} -> counted as failures")
                v["blk"] = np.where(bad, 1.0, be)
        pts[snr] = d
    return pts, meta, problems, run_git


def fails(pts, snr, arm, it=-1):
    return pts[snr][arm]["blk"][:, it]


def decision_points(pts, anchor, it=-1):
    bl = {s: max(fails(pts, s, anchor, it).mean(), 0.5 / N) for s in SNRS}
    cand = sorted((s for s in SNRS if 0.005 <= bl[s] <= 0.9), key=lambda s: abs(math.log10(bl[s] / 0.1)))[:3]
    return sorted(cand), bl


def paired(pts_x, pts_y, snr, x, y, itx=-1, ity=-1):
    ex, ey = fails(pts_x, snr, x, itx), fails(pts_y, snr, y, ity)
    a = int(np.sum((ex == 1) & (ey == 0)))
    b = int(np.sum((ex == 0) & (ey == 1)))
    return a, b, sign_p(a, b)


def rec(b, v, g):
    return (b - v) / (b - g) if b - g > 0 else float("nan")


def snr_at(bler, target=0.1):
    """Demo/exp_0921_analysis.snr_at re-implemented (log-linear interpolation, floor 0.5/n)."""
    lb = np.log10(np.maximum(np.asarray(bler, float), 0.5 / N)); lt = math.log10(target)
    if lb[0] <= lt:
        return f"<={SNRS[0]:.0f}", None
    for i in range(len(SNRS) - 1):
        if lb[i] > lt >= lb[i + 1]:
            v = SNRS[i] + (lb[i] - lt) / (lb[i] - lb[i + 1]) * (SNRS[i + 1] - SNRS[i])
            return f"{v:.1f}", v
    return f">{SNRS[-1]:.0f}", None


def main():
    p("# recompute_path_main.py -- independent recomputation (direct numpy read of the chunk files), prior SRP")
    best, mb, prob_b, git_b = load_tag(os.path.join(CONF, "raw_SRPB16e4"), "SRP", "dft")
    last, ml, prob_l, git_l = load_tag(os.path.join(CONF, "raw_SRPB16e4last"), "SRP", "dft")
    d2, md2, prob_d2, git_d2 = load_tag(os.path.join(CONF, "raw_B16e4k"), "S2", "dft")
    tags = {"best": best, "last": last}

    p("\n## 0. chunk plan / raw meta (both tags; every chunk) + the D2 reference raw")
    for name, pr in (("raw_SRPB16e4", prob_b), ("raw_SRPB16e4last", prob_l), ("raw_B16e4k", prob_d2)):
        p(f"  {name}: problems = {pr if pr else 'none (plan {(40k,40): k=0..63} x 7 SNR, no raised/non-finite blk_err, keys complete)'}")
    for tag, m, g in (("best", mb, git_b), ("last", ml, git_l)):
        chk(f"{tag} run|git identical across 448 chunks", len(g), 1)
        chk(f"{tag} run|git", next(iter(g)), EXP_META["git"])
        chk(f"{tag} run|git has no '+dirty'", any("dirty" in x for x in g), False)
        chk(f"{tag} meta|ntrain", int(float(next(iter(m["meta|ntrain"])))), EXP_META["ntrain"])
        chk(f"{tag} meta|bstar", next(iter(m["meta|bstar"])), EXP_META["bstar"])
        chk(f"{tag} meta|kron_K", int(float(next(iter(m["meta|kron_K"])))), EXP_META["kron_K"])
        chk(f"{tag} meta|ll_val|kron (|d| <= 1e-9)", float(next(iter(m["meta|ll_val|kron"]))), EXP_META["ll_val"], 1e-9)
        chk(f"{tag} meta|stagec_ckpt_id", next(iter(m["meta|stagec_ckpt_id"])).split(" | ")[0], EXP_META["ckpt"][tag])
        for k in ("run|n", "run|iters", "run|seed", "run|beta", "run|t_in", "run|dtype", "meta|prior", "meta|sigma_tag"):
            if k in m:
                p(f"  {tag} {k} = {sorted(m[k])}")
        pr_keys = [k for k in m if "prior" in k or "sigma" in k]
        p(f"  {tag} prior/sigma-related meta keys: {{{', '.join(f'{k}: {sorted(m[k])}' for k in pr_keys)}}}")
        bud = {k[12:]: next(iter(v)) for k, v in m.items() if k.startswith("meta|budget|")}
        nt = {a: re.match(r"N_train=(\S+)", s).group(1) for a, s in bud.items()}
        p(f"  {tag} N_train per arm: {nt}")
        chk(f"{tag} N_train=160000 for every arm except R3-bigamp (0) and genie (n/a)",
            all(v == "160000" for a, v in nt.items() if a not in ("R3-bigamp", GEN)) and nt["R3-bigamp"] == "0" and nt[GEN] == "n/a", True)
    chk("raw names use 'dft' pilots (448 files per tag found by the dft glob)", all(len(glob.glob(os.path.join(CONF, r, "D2_C2_SRP_Nr8_T16_Tp4_dft_snr*_skip*_n40.npz"))) == 448 for r in ("raw_SRPB16e4", "raw_SRPB16e4last")), True)
    p(f"  D2 reference raw_B16e4k: run|git {sorted(git_d2)}, bstar {sorted(md2['meta|bstar'])} kron_K {sorted(md2['meta|kron_K'])} ntrain {sorted(md2['meta|ntrain'])}")
    chk("arms present with blk_err (14)", len([a for a in best[9] if "blk" in best[9][a]]), 14)
    chk("arm set", sorted(a for a in best[9] if "blk" in best[9][a]), sorted(ARMS))

    p("\n## 1. failure counts and BLER@16 (best tag; R0-pilot also @1; V1 of the last tag) -- the §6.2 table")
    p(f"  {'arm':22s} " + "  ".join(f"{s:+3d} dB" for s in SNRS))
    for arm, (exp, bstr) in EXP_FAILS.items():
        pts, it, a = best, -1, arm
        if arm == "R0-pilot@1":
            it, a = 0, "R0-pilot"
        if arm == "V1last":
            pts, a = last, V1
        f = [int(fails(pts, s, a, it).sum()) for s in SNRS]
        bl = [fails(pts, s, a, it).mean() for s in SNRS]
        p(f"  {arm:22s} " + "  ".join(f"{x:4d} {b:.3f}" for x, b in zip(f, bl)))
        for s, x, e in zip(SNRS, f, exp):
            chk(f"fails best {arm} {s:+d} dB", x, e)
        chk(f"BLER string {arm} (3 dp)", " ".join(f"{b:.3f}" for b in bl), bstr)
    dp_sum = tuple(sum(int(fails(best, s, a).sum()) for s in EXP_DP) for a in (V1, V4, V4B))
    all_sum = tuple(sum(int(fails(best, s, a).sum()) for s in SNRS) for a in (V1, V4, V4B))
    p(f"  decision-point sums V1/V4/V4b = {dp_sum}; 7-SNR sums = {all_sum}")
    chk("decision-point sums V1/V4/V4b", dp_sum, EXP_SUMS["dp"])
    chk("7-SNR sums V1/V4/V4b", all_sum, EXP_SUMS["all"])
    for s, (eb, er) in EXP_RANKCAVEAT.items():
        chk(f"§6.1 caveat b* vs R2 at {s:+d} dB", (int(fails(best, s, BS).sum()), int(fails(best, s, R2).sum())), (eb, er))

    p("\n## 2. decision SNRs by the §1 rule (anchor BLER@16 in [0.005, 0.9], 3 smallest |log10(BLER/0.1)|)")
    for tag, pts in tags.items():
        for anc in (BS, R2, GEN):
            dp, bl = decision_points(pts, anc)
            p(f"  {tag} anchor {anc:14s}: {dp}   BLER@16 {{{', '.join(f'{s:+d}: {bl[s]:.4f}' for s in SNRS)}}}  "
              f"|log10(./0.1)| at chosen: {[round(abs(math.log10(bl[s] / 0.1)), 3) for s in dp]}  in-range SNRs: {[s for s in SNRS if 0.005 <= bl[s] <= 0.9]}")
            chk(f"{tag} decision SNRs anchor {anc}", dp, EXP_DP if anc != GEN else [-3, 0])
    DP = decision_points(best, BS)[0]
    chk("genie +3 dB BLER < 0.005 (so only two in-range SNRs -> UNDECIDED for *->genie)", fails(best, 3, GEN).mean() < 0.005, True)

    p("\n## 3. paired exact two-sided sign tests at the decision SNRs (a:b = only-first-fails : only-second-fails)")
    for (tag, x, y), (eab, epool, eps, epp) in EXP_PAIRS.items():
        pts = tags[tag]
        anc = GEN if y == GEN else (R2 if x == R2 else BS)
        dp, _ = decision_points(pts, anc)
        res = [paired(pts, pts, s, x, y) for s in dp]
        A, Bn = sum(r[0] for r in res), sum(r[1] for r in res)
        pp = sign_p(A, Bn)
        powered = len(dp) == 3 and sum(1 for a, b, _ in res if a + b >= MIN_DISC) >= 2
        wy = sum(1 for a, b, q in res if a > b and q < 0.05)
        wx = sum(1 for a, b, q in res if b > a and q < 0.05)
        p(f"  [{tag}] {x} -> {y}  anchor {anc}  dp {dp}: " + "  ".join(f"{s:+d} dB {a}:{b} p={q:.2g}" for (a, b, q), s in zip(res, dp))
          + f"   pooled {A}:{Bn} p={pp:.2g}   {'POWERED' if powered else 'UNDECIDED'}  second fewer {wy}/{len(dp)}  first fewer {wx}/{len(dp)}")
        chk(f"{tag} {x}->{y} a:b per SNR", [(a, b) for a, b, _ in res], eab)
        chk(f"{tag} {x}->{y} pooled", (A, Bn), epool)
        if eps:
            chk(f"{tag} {x}->{y} p per SNR (%.2g)", [f"{q:.2g}" for _, _, q in res], eps)
            chk(f"{tag} {x}->{y} pooled p (%.2g)", f"{pp:.2g}", epp)
        label = ("(i)" if powered and wy >= 2 else "(ii)" if powered and wx >= 2 else "(iii)" if powered else "(iv)")
        if (x, y) == (BS, V1):
            p(f"    -> §2 label for tag {tag}: {label}   (POWERED={powered}, second arm fewer at {wy}/3, first arm fewer at {wx}/3)")
            chk(f"{tag} §2 label", label, "(i)"); chk(f"{tag} power guard", powered, True); chk(f"{tag} second arm fewer k/3", wy, 3)
        if (x, y) == (BS, SC):
            p(f"    -> control label: {label}  (record (iii), 0/3 . 0/3)")
            chk("control b*->scalar label", label, "(iii)"); chk("control wy/wx", (wy, wx), (0, 0))
        if (x, y) == (R2, BS):
            chk("R2->b* b* fewer at 2/3 (prediction 6: >= 2/3)", wy, 2); chk("R2->b* POWERED", powered, True)
        if (x, y) == (BS, V0):
            chk("b*->V0 first arm (b*) fewer 3/3", wx, 3)
        if (x, y) in ((BS, V4), (BS, V4B)):
            chk(f"{x}->{y} second fewer 3/3", wy, 3)
        if y == GEN:
            chk(f"{x}->genie UNDECIDED (2 decision points)", (powered, len(dp)), (False, 2))

    p("\n## 4. best vs last V1, paired exact two-sided sign test (a = only best fails, b = only last fails)")
    res = [paired(best, last, s, V1, V1) for s in DP]
    A, Bn = sum(r[0] for r in res), sum(r[1] for r in res)
    p("  " + "  ".join(f"{s:+d} dB {a}:{b} p={q:.3f}" for (a, b, q), s in zip(res, DP)) + f"   pooled {A}:{Bn} p={sign_p(A, Bn):.3f}")
    chk("best-vs-last a:b per SNR", [(a, b) for a, b, _ in res], EXP_BEST_LAST[0])
    chk("best-vs-last pooled", (A, Bn), EXP_BEST_LAST[1])
    chk("best-vs-last p per SNR (3 dp)", [round(q, 3) for _, _, q in res], EXP_BEST_LAST[2])
    chk("best-vs-last pooled p (3 dp)", round(sign_p(A, Bn), 3), EXP_BEST_LAST[3])
    chk("best-vs-last pooled p > 0.05 (prediction 11)", sign_p(A, Bn) > 0.05, True)

    p("\n## 5. recovery R = (b* - V1)/(b* - genie): point estimates + re-implemented paired bootstrap 90% CI; saturation guard; Delta R")
    def cols(pts, snrs):
        return [tuple(fails(pts, s, a) for a in (BS, V1, GEN)) for s in snrs]
    R = {}
    for tag, pts in tags.items():
        for key, snrs in [(-3, [-3])] + [(s, [s]) for s in DP if s != -3] + [("pooled", DP)]:
            c = cols(pts, snrs)
            b, v, g = (int(sum(x[i].sum() for x in c)) for i in range(3))
            R[(tag, key)] = rec(b, v, g)
            lo, hi, nn = boot(c)
            p(f"  {tag} {str(key):6s} b* {b} V1 {v} genie {g}  R = {R[(tag, key)]:.3f}  [90% {lo:.3f}, {hi:.3f}]  undefined {nn}")
            if key in EXP_REC[tag]:
                e = EXP_REC[tag][key]
                chk(f"R {tag} {key} counts", (b, v, g), e[:3])
                chk(f"R {tag} {key} (3 dp)", round(R[(tag, key)], 3), e[3])
                chk(f"R {tag} {key} CI lo (3 dp)", round(lo, 3), e[4]); chk(f"R {tag} {key} CI hi (3 dp)", round(hi, 3), e[5])
                chk(f"R {tag} {key} undefined replicates == 0", nn, 0)
    c = cols(d2, [-3]); b, v, g = (int(sum(x[i].sum() for x in c)) for i in range(3)); r_d2 = rec(b, v, g)
    lo, hi, nn = boot(c)
    p(f"  D2 B16e4k -3 dB  b* {b} V1 {v} genie {g}  R = {r_d2:.3f}  [90% {lo:.3f}, {hi:.3f}]")
    chk("D2 -3 counts", (b, v, g), EXP_REC["D2-3"][:3]); chk("D2 -3 R", round(r_d2, 3), EXP_REC["D2-3"][3])
    chk("D2 -3 CI (3 dp)", (round(lo, 3), round(hi, 3)), (0.427, 0.512))
    c2 = cols(d2, [-3, 0, 3]); b2, v2, g2 = (int(sum(x[i].sum() for x in c2)) for i in range(3)); r_d2b = rec(b2, v2, g2)
    p(f"  D2 B16e4k -3,0,3  b* {b2} V1 {v2} genie {g2}  R = {r_d2b:.3f}")
    chk("D2 -3,0,3 counts", (b2, v2, g2), EXP_REC["D2-303"][:3]); chk("D2 -3,0,3 R", round(r_d2b, 3), EXP_REC["D2-303"][3])
    dR1, dR1l, dR2 = R[("best", -3)] - r_d2, R[("last", -3)] - r_d2, R[("best", "pooled")] - r_d2b
    p(f"  Delta R primary (-3 dB) = {dR1:+.3f} (last {dR1l:+.3f});  secondary (decision sum vs D2 -3,0,3) = {dR2:+.3f}")
    chk("Delta R primary point (3 dp)", round(dR1, 3), EXP_REC["dR1"]); chk("Delta R primary last (3 dp)", round(dR1l, 3), EXP_REC["dR1last"])
    chk("Delta R secondary (3 dp)", round(dR2, 3), EXP_REC["dR2"])
    # unpaired difference CI: the two raw sets resampled independently, same B and seed, as frontier_ci --recovery describes
    def boot_vals(cs):
        rng = np.random.default_rng(SEED); n = len(cs[0][0]); out = np.empty(B_BOOT)
        for i in range(B_BOOT):
            idx = rng.integers(0, n, n)
            bs = sum(b_[idx].sum() for b_, _, _ in cs); vs = sum(v_[idx].sum() for _, v_, _ in cs); gs = sum(g_[idx].sum() for _, _, g_ in cs)
            out[i] = (bs - vs) / (bs - gs) if bs - gs > 0 else np.nan
        return out
    for tag, e in (("best", (0.062, 0.168)), ("last", (0.052, 0.157))):
        d = boot_vals(cols(tags[tag], [-3])) - boot_vals(cols(d2, [-3]))
        lo_, hi_ = np.percentile(d[np.isfinite(d)], [5, 95])
        p(f"  Delta R {tag} -3 dB unpaired CI (my resampler, same seed for both sets): [{lo_:+.3f}, {hi_:+.3f}]  (record [{e[0]:+.3f}, {e[1]:+.3f}] from frontier_ci)")
        chk(f"Delta R {tag} CI lower > 0 (-> '높다' by the registered three-way rule)", lo_ > 0 and e[0] > 0, True)
        chk(f"Delta R {tag} CI (3 dp, tolerance 0.006: resampler details may differ)", (abs(round(lo_, 3) - e[0]) <= 0.006, abs(round(hi_, 3) - e[1]) <= 0.006), (True, True))
    d = boot_vals(cols(best, DP)) - boot_vals(cols(d2, [-3, 0, 3]))
    lo_, hi_ = np.percentile(d[np.isfinite(d)], [5, 95])
    p(f"  Delta R secondary unpaired CI (my resampler): [{lo_:+.3f}, {hi_:+.3f}]  (record [+0.092, +0.180])")
    b3, v3, g3 = (int(fails(best, -3, a).sum()) for a in (BS, V1, GEN))
    p(f"  failure-count gaps -3 dB: V1-genie {v3 - g3}, b*-genie {b3 - g3};  D2 -3: {v - g}, {b - g}")
    chk("gaps SRP -3 dB", (v3 - g3, b3 - g3), EXP_REC["gap3"]); chk("gaps D2 -3 dB", (v - g, b - g), EXP_REC["gapD2_3"])
    bl_bs = fails(best, -3, BS).mean()
    sat_range = not (0.005 <= bl_bs <= 0.9); sat_gen = b3 <= g3
    p(f"  saturation guard (-3 dB): b* BLER@16 = {bl_bs:.4f} in [0.005, 0.9]? {not sat_range}; b* fails {b3} <= genie {g3}? {sat_gen}"
      f" -> guard {'FIRES' if sat_range or sat_gen else 'does not fire'}")
    chk("saturation guard fires", sat_range or sat_gen, EXP_SAT["fires"])
    chk("b* BLER@16 -3 dB (3 dp)", round(bl_bs, 3), EXP_SAT["bler"])
    chk("prediction 5: R(-3 dB) CI lower > 0", EXP_REC["best"][-3][4] > 0, True)

    p("\n## 6. SNR@0.1 by the tool's log-linear rule (exp_0921_analysis.snr_at re-implemented; 1 dp as the tool prints, 2 dp vs the record)")
    for tag, pts in tags.items():
        vals = {}
        for a in ARMS:
            vals[a] = snr_at([fails(pts, s, a).mean() for s in SNRS])
        vals["R0-pilot@1"] = snr_at([fails(pts, s, "R0-pilot", 0).mean() for s in SNRS])
        p(f"  [{tag}] " + ", ".join(f"{a}: {v[0]}" + (f" ({v[1]:.2f})" if v[1] is not None else "") for a, v in vals.items()))
        if tag == "best":
            for a, e in EXP_SNR01["best"].items():
                chk(f"SNR@0.1 best {a} (1 dp / flag)", vals[a][0], e)
            for a, e in EXP_SNR01_2DP.items():
                chk(f"SNR@0.1 best {a} (2 dp)", round(vals[a][1], 2), e, 0.0051)
            gap = vals[BS][1] - vals[V1][1]
            p(f"  best: gap b* - V1 = {gap:+.2f} dB (record +2.01); V1 - genie = {vals[V1][1] - vals[GEN][1]:+.2f} (record +1.58); b* - genie = {vals[BS][1] - vals[GEN][1]:+.2f} (record +3.59); b* - scalar = {vals[BS][1] - vals[SC][1]:+.2f} (record +0.14); R2 - b* = {vals[R2][1] - vals[BS][1]:+.2f} (record +0.15)")
            chk("gap b*-V1 (2 dp)", round(gap, 2), 2.01, 0.0051); chk("gap V1-genie", round(vals[V1][1] - vals[GEN][1], 2), 1.58, 0.0051)
            chk("gap b*-genie", round(vals[BS][1] - vals[GEN][1], 2), 3.59, 0.0051); chk("gap b*-scalar", round(vals[BS][1] - vals[SC][1], 2), 0.14, 0.0051)
            chk("gap R2-b*", round(vals[R2][1] - vals[BS][1], 2), 0.15, 0.0051)
            chk("gap b*-V4", round(vals[BS][1] - vals[V4][1], 2), 2.01, 0.0051); chk("gap b*-V4b", round(vals[BS][1] - vals[V4B][1], 2), 1.96, 0.0051)
            chk("prediction 7: V1 and b* SNR@0.1 both numbers and gap > 0", vals[V1][1] is not None and vals[BS][1] is not None and gap > 0, True)
        else:
            chk("last gap b*-V1 (2 dp)", round(vals[BS][1] - vals[V1][1], 2), 2.03, 0.0051)

    p("\n## 7. F3 guard firing (NMSE > 10 or non-finite at any of the 16 iterations), per arm / SNR / tag")
    for tag, pts in tags.items():
        rows = {}
        for s in SNRS:
            for a in ARMS:
                if a == GEN:
                    continue
                nm = pts[s][a]["nmse"]
                fired = int(np.sum(np.any(~np.isfinite(nm) | (nm > 10.0), axis=1)))
                if fired:
                    rows[(s, a)] = fired
        p(f"  [{tag}] fired: " + ", ".join(f"{s:+d} dB {a} {n}" for (s, a), n in sorted(rows.items(), key=lambda t: (t[0][0], t[0][1]))))
        v0 = [rows.get((s, V0), 0) for s in SNRS]
        chk(f"{tag} V0 fired counts", v0, EXP_GUARD_V0[tag])
        chk(f"{tag} V0 fired rates (3 dp)", [round(x / N, 3) for x in v0], EXP_GUARD_V0_RATE[tag])
        others = sorted((s, a) for (s, a) in rows if a != V0)
        chk(f"{tag} no firing outside V0", others, [])
        never = [a for a in ARMS if a != GEN and not any((s, a) in rows for s in SNRS)]
        chk(f"{tag} arms that never fired (12)", sorted(never), EXP_GUARD_NEVER)
    chk("prediction 11: V0 guard rate at -3 dB >= 0.5 and V0 BLER -3 dB >= 0.9",
        EXP_GUARD_V0["best"][0] / N >= 0.5 and fails(best, -3, V0).mean() >= 0.9, True)

    p("\n## 8. R5-genie of the last tag bit-identical to the best tag (every key, every SNR, every trial); non-ckpt arms identical")
    same = True
    for s in SNRS:
        for q, a in best[s][GEN].items():
            if q == "blk":
                continue
            same &= np.array_equal(a, last[s][GEN][q], equal_nan=True)
    p(f"  identical = {same}  (keys: {sorted(q for q in best[-3][GEN] if q != 'blk')})")
    chk("R5-genie best == last (bit)", same, True)
    for a in (BS, SC, "M-ours-gmm32", R2, "R1-turbo", "R3-bigamp", "R4-llr", "R4-scvamp", "R0-pilot"):
        eq = all(np.array_equal(best[s][a]["blk_err"], last[s][a]["blk_err"], equal_nan=True) for s in SNRS)
        chk(f"non-ckpt arm {a} blk_err identical across tags", eq, True)

    p("\n## 9. loader cross-check: analysis.load_raw vs this direct read")
    sys.path.insert(0, os.path.join(CONF, "code"))
    from analysis import load_raw  # noqa: E402
    data, meta, warns = load_raw("D2", root=os.path.join(CONF, "raw_SRPB16e4"))
    p(f"  load_raw warnings: {warns if warns else 'none'}")
    for s in (-3, 3):
        for a in (BS, V1, GEN, V0):
            chk(f"load_raw == direct read {a} {s:+d} dB", np.array_equal(np.asarray(data[('C2', 'SRP', float(s))][a]['blk_err']), best[s][a]['blk']), True)
    chk("load_raw meta ll_val|kron", float(meta[("C2", "SRP")]["ll_val|kron"]), EXP_META["ll_val"], 1e-9)
    chk("load_raw R0-pilot@1 alias -3 dB == direct @1", int(np.asarray(data[('C2', 'SRP', -3.0)]['R0-pilot@1']['blk_err'])[:, -1].sum()),
        int(fails(best, -3, "R0-pilot", 0).sum()))

    p("\n## 10. checkpoint records (torch.load, CPU)")
    import hashlib
    import torch  # noqa: E402
    for role, f, esha in (("best", "ckpt/d2sx_SRP_N160000_a1_best.pt", "ac4699c78b3e2d80"), ("last", "ckpt/d2sx_SRP_N160000_a1.pt", "f82762a7002308db")):
        sha = hashlib.sha256(open(os.path.join(CONF, f), "rb").read()).hexdigest()[:16]
        ck = torch.load(os.path.join(CONF, f), map_location="cpu", weights_only=False)
        keys = {k: ck.get(k) for k in ("epoch", "best_epoch", "best_val", "stopped_by", "role", "prior", "sigma_tag", "rung", "attempt", "grad_clip", "wall_sec", "split_hash")}
        p(f"  {role} {f}: sha256[:16]={sha} {keys}")
        chk(f"{role} ckpt sha256[:16]", sha, esha)
        chk(f"{role} ckpt prior/sigma_tag", (keys["prior"], keys["sigma_tag"]), ("SRP", "SRP"))
        chk(f"{role} ckpt role", keys["role"], role)
        chk(f"{role} ckpt epoch", keys["epoch"], EXP_TRAIN["best_epoch"] if role == "best" else EXP_TRAIN["last_epoch"])
        chk(f"{role} ckpt best_epoch", keys["best_epoch"], EXP_TRAIN["best_epoch"])
        chk(f"{role} ckpt best_val", float(keys["best_val"]), EXP_TRAIN["best_val"], 1e-12)
        chk(f"{role} ckpt rung / attempt / split_hash", (keys["rung"], keys["attempt"], keys["split_hash"]), (EXP_TRAIN["rung"], EXP_TRAIN["attempt"], EXP_TRAIN["split_hash"]))
        chk(f"{role} ckpt grad_clip none (attempt 1, no clipping)", not keys["grad_clip"], True)
        if role == "last":
            chk("last ckpt stopped_by", keys["stopped_by"], EXP_TRAIN["stopped"])
            chk("prediction 9: patience stop and epoch in [300, 1500]", keys["stopped_by"] == "patience" and 300 <= keys["epoch"] <= 1500, True)

    p(f"\n## SUMMARY: {NCHECK[0]} values checked, {NCHECK[1]} differ from the record")
    return 0 if NCHECK[1] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
