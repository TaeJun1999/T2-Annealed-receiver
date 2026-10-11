"""recompute_srt_main.py -- independent recomputation for the RECORD AUDIT of NEXT_EXPERIMENTS_SRT16e4.md §6.1 / §6.2 (main run).

Reads the raw chunk files of raw_SRTB16e4 / raw_SRTB16e4last (+ raw_B16e4k for the D2 reference) DIRECTLY with numpy
(no s6_gen.py, no tables_*.txt) and recomputes: failure counts / BLER@16 per arm (the §6.2 table, 16 rows x 7 SNR), decision
SNRs by the §1 rule, exact two-sided paired sign tests + power guard + label for every pair quoted in §6.1 / §6.2, best-vs-last V1,
recovery R point estimates and the paired bootstrap CI (recovery_ci.boot re-implemented from its definition: default_rng(20260926),
B = 2000, 5/95 percentiles), the saturation guard, the unpaired Delta R point estimate, SNR@0.1 flags, F3 guard firing, raw meta,
chunk plan, R5-genie bit identity of the two tags, GB' numbers.  analysis.load_raw is used ONLY as a cross-check (§9).
Every recomputed value is compared with the value transcribed in §6 (EXPECTED below, typed from the record) -> DIFF lines.

usage (cwd = ~/t2/conf):  CUDA_VISIBLE_DEVICES= ~/miniforge3/envs/torch/bin/python -B \
    results/review_next/prereg_audit_2026-10-11/recompute_srt_main.py > results/review_next/prereg_audit_2026-10-11/recompute_srt_main.out
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

# ----------------------------------------------------------------------------- values transcribed in the record (§6)
EXP_FAILS = {   # §6.2 table (best tag): failures, and the BLER string printed (3 dp)
    V1: ([2320, 2056, 1781, 1661, 1504, 1391, 1331], "0.906 0.803 0.696 0.649 0.588 0.543 0.520"),
    "V1last": ([2318, 2061, 1788, 1663, 1503, 1391, 1336], "0.905 0.805 0.698 0.650 0.587 0.543 0.522"),
    V4: ([2329, 2054, 1767, 1662, 1496, 1396, 1321], "0.910 0.802 0.690 0.649 0.584 0.545 0.516"),
    V4B: ([2323, 2051, 1772, 1662, 1501, 1400, 1328], "0.907 0.801 0.692 0.649 0.586 0.547 0.519"),
    BS: ([2404, 2169, 1941, 1774, 1611, 1495, 1430], "0.939 0.847 0.758 0.693 0.629 0.584 0.559"),
    SC: ([2408, 2171, 1940, 1774, 1617, 1497, 1439], "0.941 0.848 0.758 0.693 0.632 0.585 0.562"),
    "M-ours-gmm32": ([2438, 2214, 2019, 1828, 1673, 1551, 1495], "0.952 0.865 0.789 0.714 0.654 0.606 0.584"),
    R2: ([2461, 2291, 2093, 1924, 1822, 1692, 1607], "0.961 0.895 0.818 0.752 0.712 0.661 0.628"),
    "R1-turbo": ([2507, 2396, 2205, 2047, 1906, 1754, 1676], "0.979 0.936 0.861 0.800 0.745 0.685 0.655"),
    "R0-pilot@1": ([2547, 2500, 2389, 2289, 2202, 2092, 2029], "0.995 0.977 0.933 0.894 0.860 0.817 0.793"),
    "R0-pilot": ([2491, 2326, 2121, 1948, 1832, 1696, 1626], "0.973 0.909 0.829 0.761 0.716 0.662 0.635"),
    "R4-scvamp": ([2526, 2440, 2313, 2206, 2109, 2045, 1977], "0.987 0.953 0.904 0.862 0.824 0.799 0.772"),
    "R3-bigamp": ([2502, 2399, 2284, 2191, 2187, 2214, 2232], "0.977 0.937 0.892 0.856 0.854 0.865 0.872"),
    "R4-llr": ([2544, 2496, 2458, 2381, 2322, 2234, 2143], "0.994 0.975 0.960 0.930 0.907 0.873 0.837"),
    V0: ([2531, 2495, 2473, 2460, 2460, 2429, 2236], "0.989 0.975 0.966 0.961 0.961 0.949 0.873"),
    GEN: ([2091, 1871, 1626, 1546, 1416, 1327, 1277], "0.817 0.731 0.635 0.604 0.553 0.518 0.499")}
EXP_PAIRS = {  # (tag, x, y): ([a:b per decision SNR], pooled a:b, [p per SNR as printed] or None, pooled p as printed or None)
    ("best", BS, V1): ([(145, 38), (126, 22), (132, 33)], (403, 93), ["6.3e-16", "6.5e-19", "3.2e-15"], "5.2e-47"),
    ("last", BS, V1): ([(148, 40), (128, 24), (130, 36)], (406, 100), ["9e-16", "2.4e-18", "1.1e-13"], "9.7e-45"),
    ("best", BS, SC): ([(29, 35), (37, 39), (33, 42)], (99, 116), ["0.53", "0.91", "0.36"], "0.28"),
    ("best", R2, BS): ([(265, 54), (237, 40), (219, 42)], (721, 136), None, None),
    ("best", BS, V4): ([(156, 41), (120, 21), (140, 31)], (416, 93), None, None),
    ("best", BS, V4B): ([(154, 44), (118, 23), (135, 33)], (407, 100), None, None),
    ("best", BS, V0): ([(0, 849), (1, 935), (2, 808)], (3, 2592), None, None),
    ("best", V1, GEN): ([(111, 23), (89, 25), (73, 19)], (273, 67), None, None),
    ("best", BS, GEN): ([(223, 28), (181, 13), (172, 19)], (576, 60), None, None)}
EXP_BEST_LAST = ([(11, 10), (12, 12), (11, 16)], (34, 38), [1.0, 1.0, 0.442], 0.724)   # p to 3 dp as the record prints
EXP_DP = [9, 12, 15]
EXP_REC = {"best": {-3: (2404, 2320, 2091, 0.268, 0.221, 0.315), 9: (1611, 1504, 1416, 0.549, 0.463, 0.628),
                    12: (1495, 1391, 1327, 0.619, 0.535, 0.708), 15: (1430, 1331, 1277, 0.647, 0.554, 0.738),
                    "pooled": (4536, 4226, 4020, 0.601, 0.553, 0.650)},
           "last": {-3: (2404, 2318, 2091, 0.275, 0.226, 0.323), "pooled": (4536, 4230, 4020, 0.593, 0.542, 0.643)},
           "D2-3": (623, 371, 87, 0.470), "D2-303": (864, 488, 125, 0.509), "dR2": 0.092,
           "gap_dp": (206, 516), "gapD2_303": (363, 739)}
EXP_SAT = dict(bler=0.939, bler4=0.9391, fires=True)
EXP_GUARD_V0 = {"best": [2471, 2458, 2374, 2363, 2315, 2255, 2022], "last": [2478, 2469, 2396, 2356, 2338, 2266, 2020]}
EXP_GUARD_V0_RATE = {"best": [0.965, 0.960, 0.927, 0.923, 0.904, 0.881, 0.790],
                     "last": [0.968, 0.964, 0.936, 0.920, 0.913, 0.885, 0.789]}
EXP_GUARD_OTHERS = sorted([(3, a) for a in ("M-ours-gmm32", "R0-pilot", "R1-turbo", R2, "R4-llr", "R4-scvamp")])
EXP_GUARD_NEVER = sorted([BS, SC, V1, V4, V4B, "R3-bigamp"])
EXP_META = dict(git="28f38d55", ntrain=160000, bstar="kron", kron_K=4096, ll_val=208.1279194544014, em_sec=13117.145124912262,
                ckpt={"best": "sha256[:16]=7c7354bef3bb1e40 epoch=597 best_epoch=597 role=best 8x4",
                      "last": "sha256[:16]=918a424724fcb0ab epoch=617 best_epoch=597 role=last 8x4"})
EXP_SUMS = dict(dp=(4226, 4213, 4229), all=(12044, 12025, 12037))
EXP_GBP = dict(median=0.5425, mn=0.4535, mx=0.8722)
EXP_TRAIN = dict(best_epoch=597, last_epoch=617, best_val=0.14180772006511688, stopped="patience", wall_last=13862.3, s_per_epoch=22.47)

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
    """exact two-sided sign test (binomial p = 1/2), as Demo/exp_0921_analysis.sign_p."""
    n = a + b
    return 1.0 if n == 0 else min(1.0, 2 * sum(math.comb(n, i) for i in range(min(a, b) + 1)) / 2 ** n)


def boot(cols):
    """recovery_ci.boot re-implemented from its definition (fresh default_rng(SEED), B replicates of n indices with replacement,
    the SAME index draw applied to every (b*, V1, genie) column of every SNR in cols, R from the summed counts, 5/95 pct)."""
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


# ----------------------------------------------------------------------------- direct numpy read of a raw set
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


def paired(pts_x, pts_y, snr, x, y):
    ex, ey = fails(pts_x, snr, x), fails(pts_y, snr, y)
    a = int(np.sum((ex == 1) & (ey == 0)))
    b = int(np.sum((ex == 0) & (ey == 1)))
    return a, b, sign_p(a, b)


def rec(b, v, g):
    return (b - v) / (b - g) if b - g > 0 else float("nan")


def snr_at_flag(bler):
    lb = np.log10(np.maximum(np.asarray(bler), 0.5 / N))
    if lb[0] <= -1:
        return "lo"
    for i in range(len(lb) - 1):
        if lb[i] > -1 >= lb[i + 1]:
            return "ok"
    return "hi"


def main():
    p("# recompute_srt_main.py -- independent recomputation (direct numpy read of the chunk files)")
    best, mb, prob_b, git_b = load_tag(os.path.join(CONF, "raw_SRTB16e4"), "SRT", "eig")
    last, ml, prob_l, git_l = load_tag(os.path.join(CONF, "raw_SRTB16e4last"), "SRT", "eig")
    d2, md2, prob_d2, git_d2 = load_tag(os.path.join(CONF, "raw_B16e4k"), "S2", "dft")
    tags = {"best": best, "last": last}

    # ------------------------------------------------------------------ 0. chunk plan, raw meta, run|git
    p("\n## 0. chunk plan / raw meta (both tags; every chunk) + the D2 reference raw")
    for name, pr in (("raw_SRTB16e4", prob_b), ("raw_SRTB16e4last", prob_l), ("raw_B16e4k", prob_d2)):
        p(f"  {name}: problems = {pr if pr else 'none (plan {(40k,40): k=0..63} x 7 SNR, no raised/non-finite blk_err, keys complete)'}")
    for tag, m, g in (("best", mb, git_b), ("last", ml, git_l)):
        chk(f"{tag} run|git identical across 448 chunks", len(g), 1)
        chk(f"{tag} run|git", next(iter(g)), EXP_META["git"])
        chk(f"{tag} run|git has no '+dirty'", any("dirty" in x for x in g), False)
        chk(f"{tag} meta|ntrain", int(float(next(iter(m["meta|ntrain"])))), EXP_META["ntrain"])
        chk(f"{tag} meta|bstar", next(iter(m["meta|bstar"])), EXP_META["bstar"])
        chk(f"{tag} meta|kron_K", int(float(next(iter(m["meta|kron_K"])))), EXP_META["kron_K"])
        chk(f"{tag} meta|ll_val|kron (|d| <= 1e-9)", float(next(iter(m["meta|ll_val|kron"]))), EXP_META["ll_val"], 1e-9)
        chk(f"{tag} meta|em_sec", float(next(iter(m["meta|em_sec"]))), EXP_META["em_sec"], 1e-6)
        chk(f"{tag} meta|stagec_ckpt_id", next(iter(m["meta|stagec_ckpt_id"])).split(" | ")[0], EXP_META["ckpt"][tag])
        for k in ("run|n", "run|iters", "run|seed", "run|beta", "run|t_in", "run|dtype"):
            p(f"  {tag} {k} = {sorted(m[k])}")
        p(f"  {tag} meta|stagec_ckpt = {sorted(m['meta|stagec_ckpt'])}")
        bud = {k[12:]: next(iter(v)) for k, v in m.items() if k.startswith("meta|budget|")}
        nt = {a: re.match(r"N_train=(\S+)", s).group(1) for a, s in bud.items()}
        p(f"  {tag} N_train per arm: {nt}")
        chk(f"{tag} N_train=160000 for every arm except R3-bigamp (0) and genie (n/a)",
            all(v == "160000" for a, v in nt.items() if a not in ("R3-bigamp", GEN)) and nt["R3-bigamp"] == "0" and nt[GEN] == "n/a", True)
    p(f"  D2 reference raw_B16e4k: run|git {sorted(git_d2)}, bstar {sorted(md2['meta|bstar'])} kron_K {sorted(md2['meta|kron_K'])} ntrain {sorted(md2['meta|ntrain'])}")
    chk("arms present with blk_err (14)", len([a for a in best[9] if "blk" in best[9][a]]), 14)
    chk("arm set", sorted(a for a in best[9] if "blk" in best[9][a]), sorted(ARMS))

    # ------------------------------------------------------------------ 1. failure counts / BLER@16 per arm
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
    g3, g15 = fails(best, -3, GEN).mean(), fails(best, 15, GEN).mean()
    p(f"  genie BLER@16: -3 dB {g3:.4f}, +15 dB {g15:.4f}  (§6.1 label appendix / predictions 2a, 2b)")
    chk("genie BLER -3 dB (3 dp)", round(g3, 3), 0.817); chk("genie BLER +15 dB (3 dp)", round(g15, 3), 0.499)

    # ------------------------------------------------------------------ 2. decision SNRs (§1 rule)
    p("\n## 2. decision SNRs by the §1 rule (anchor BLER@16 in [0.005, 0.9], 3 smallest |log10(BLER/0.1)|)")
    for tag, pts in tags.items():
        for anc in (BS, R2, GEN):
            dp, bl = decision_points(pts, anc)
            p(f"  {tag} anchor {anc:14s}: {dp}   BLER@16 {{{', '.join(f'{s:+d}: {bl[s]:.4f}' for s in SNRS)}}}  "
              f"|log10(./0.1)| at chosen: {[round(abs(math.log10(bl[s] / 0.1)), 3) for s in dp]}")
            chk(f"{tag} decision SNRs anchor {anc}", dp, EXP_DP)
    DP = decision_points(best, BS)[0]
    # also: every arm's -3 dB BLER > 0.9 (the §6.3 bullet 'R_X(-3) undefined for all 16' is checked in the base script)

    # ------------------------------------------------------------------ 3. paired sign tests, power guard, label
    p("\n## 3. paired exact two-sided sign tests at the decision SNRs (a:b = only-first-fails : only-second-fails)")
    for (tag, x, y), (eab, epool, eps, epp) in EXP_PAIRS.items():
        pts = tags[tag]
        anc = GEN if y == GEN else (R2 if x == R2 else BS)        # anchor = the baseline member (analysis.pair_list)
        dp, _ = decision_points(pts, anc)
        res = [paired(pts, pts, s, x, y) for s in dp]
        A, Bn = sum(r[0] for r in res), sum(r[1] for r in res)
        pp = sign_p(A, Bn)
        powered = len(dp) == 3 and sum(1 for a, b, _ in res if a + b >= MIN_DISC) >= 2
        wy = sum(1 for a, b, q in res if a > b and q < 0.05)
        wx = sum(1 for a, b, q in res if b > a and q < 0.05)
        p(f"  [{tag}] {x} -> {y}  anchor {anc}  dp {dp}: " + "  ".join(f"{s:+d} dB {a}:{b} p={q:.2g}" for (a, b, q), s in zip(res, dp))
          + f"   pooled {A}:{Bn} p={pp:.2g}   {'POWERED' if powered else 'UNDECIDED'}  second fewer {wy}/3  first fewer {wx}/3")
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
            chk("R2->b* b* fewer at 3/3", wy, 3)
        if (x, y) == (BS, V0):
            chk("b*->V0 first arm (b*) fewer 3/3", wx, 3)
        if (x, y) in ((BS, V4), (BS, V4B), (V1, GEN), (BS, GEN)):
            chk(f"{x}->{y} second fewer 3/3", wy, 3)

    # ------------------------------------------------------------------ 4. best vs last V1
    p("\n## 4. best vs last V1, paired exact two-sided sign test (a = only best fails, b = only last fails)")
    res = [paired(best, last, s, V1, V1) for s in DP]
    A, Bn = sum(r[0] for r in res), sum(r[1] for r in res)
    p("  " + "  ".join(f"{s:+d} dB {a}:{b} p={q:.3f}" for (a, b, q), s in zip(res, DP)) + f"   pooled {A}:{Bn} p={sign_p(A, Bn):.3f}")
    chk("best-vs-last a:b per SNR", [(a, b) for a, b, _ in res], EXP_BEST_LAST[0])
    chk("best-vs-last pooled", (A, Bn), EXP_BEST_LAST[1])
    chk("best-vs-last p per SNR (3 dp)", [round(q, 3) for _, _, q in res], EXP_BEST_LAST[2])
    chk("best-vs-last pooled p (3 dp)", round(sign_p(A, Bn), 3), EXP_BEST_LAST[3])
    chk("best-vs-last pooled p > 0.05 (prediction 9)", sign_p(A, Bn) > 0.05, True)

    # ------------------------------------------------------------------ 5. recovery R, bootstrap CI, saturation guard, Delta R
    p("\n## 5. recovery R = (b* - V1)/(b* - genie): point estimates + re-implemented paired bootstrap 90% CI; saturation guard; Delta R")
    def cols(pts, snrs):
        return [tuple(fails(pts, s, a) for a in (BS, V1, GEN)) for s in snrs]
    R = {}
    for tag, pts in tags.items():
        for key, snrs in [(-3, [-3])] + [(s, [s]) for s in DP] + [("pooled", DP)]:
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
    c = cols(d2, [-3]); b, v, g = (int(sum(x[i].sum() for x in c)) for i in range(3)); r_d2 = rec(b, v, g)
    lo, hi, nn = boot(c)
    p(f"  D2 B16e4k -3 dB  b* {b} V1 {v} genie {g}  R = {r_d2:.3f}  [90% {lo:.3f}, {hi:.3f}]")
    chk("D2 -3 counts", (b, v, g), EXP_REC["D2-3"][:3]); chk("D2 -3 R", round(r_d2, 3), EXP_REC["D2-3"][3])
    c2 = cols(d2, [-3, 0, 3]); b2, v2, g2 = (int(sum(x[i].sum() for x in c2)) for i in range(3)); r_d2b = rec(b2, v2, g2)
    lo2, hi2, _ = boot(c2)
    p(f"  D2 B16e4k -3,0,3  b* {b2} V1 {v2} genie {g2}  R = {r_d2b:.3f}  [90% {lo2:.3f}, {hi2:.3f}]  (record: 0.509 [0.470, 0.544] from frontier_ci's own resampler)")
    chk("D2 -3,0,3 counts", (b2, v2, g2), EXP_REC["D2-303"][:3]); chk("D2 -3,0,3 R", round(r_d2b, 3), EXP_REC["D2-303"][3])
    dR1, dR2 = R[("best", -3)] - r_d2, R[("best", "pooled")] - r_d2b
    p(f"  Delta R primary (-3 dB, NOT reported: guard) = {dR1:+.3f};  secondary (decision sum vs D2 -3,0,3) = {dR2:+.3f}")
    chk("Delta R secondary (3 dp)", round(dR2, 3), EXP_REC["dR2"])
    bb, vv, gg = (int(sum(x[i].sum() for x in cols(best, DP))) for i in range(3))
    p(f"  failure-count gaps, decision sum: V1-genie {vv - gg}, b*-genie {bb - gg};  D2 -3,0,3: {v2 - g2}, {b2 - g2}")
    chk("gaps SRT decision sum", (vv - gg, bb - gg), EXP_REC["gap_dp"]); chk("gaps D2 -3,0,3", (v2 - g2, b2 - g2), EXP_REC["gapD2_303"])
    bl_bs = fails(best, -3, BS).mean(); b3, g3 = int(fails(best, -3, BS).sum()), int(fails(best, -3, GEN).sum())
    sat_range = not (0.005 <= bl_bs <= 0.9); sat_gen = b3 <= g3
    p(f"  saturation guard (-3 dB): b* BLER@16 = {bl_bs:.4f} in [0.005, 0.9]? {not sat_range}; b* fails {b3} <= genie {g3}? {sat_gen}"
      f" -> guard {'FIRES' if sat_range or sat_gen else 'does not fire'} (by the range condition: {sat_range}; by the genie condition: {sat_gen})")
    chk("saturation guard fires", sat_range or sat_gen, EXP_SAT["fires"])
    chk("guard fires by the RANGE condition (prediction 3)", sat_range, True)
    chk("guard does NOT fire by the genie condition", sat_gen, False)
    chk("b* BLER@16 -3 dB (3 dp)", round(bl_bs, 3), EXP_SAT["bler"]); chk("b* BLER@16 -3 dB (4 dp)", round(bl_bs, 4), EXP_SAT["bler4"])
    chk("prediction 4: pooled R in [0.10, 0.40]?", 0.10 <= R[("best", "pooled")] <= 0.40, False)

    # ------------------------------------------------------------------ 6. SNR@0.1
    p("\n## 6. SNR@0.1 flags (first downward crossing of 0.1 on the grid; 'hi' = never reached -> gap n/a)")
    for tag, pts in tags.items():
        flags = {a: snr_at_flag([fails(pts, s, a).mean() for s in SNRS]) for a in ARMS}
        flags["R0-pilot@1"] = snr_at_flag([fails(pts, s, "R0-pilot", 0).mean() for s in SNRS])
        p(f"  [{tag}] {flags}")
        chk(f"{tag} all 15 readings 'hi' -> every gap n/a", all(f == "hi" for f in flags.values()) and len(flags) == 15, True)
    p(f"  min BLER@16 at +15 dB over arms (best) = {min(fails(best, 15, a).mean() for a in ARMS):.3f} (genie)")

    # ------------------------------------------------------------------ 7. F3 guard firing rates
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
        chk(f"{tag} other firings exactly at the listed (SNR, arm)", others, EXP_GUARD_OTHERS)
        chk(f"{tag} other firings all == 1 trial", all(rows[k] == 1 for k in others), True)
        never = [a for a in ARMS if a != GEN and not any((s, a) in rows for s in SNRS)]
        chk(f"{tag} arms that never fired", sorted(never), EXP_GUARD_NEVER)
    chk("prediction 9: V0 guard rate >= 0.5 at every SNR (best) and V0 BLER -3/0 dB >= 0.9",
        all(x / N >= 0.5 for x in EXP_GUARD_V0["best"]) and fails(best, -3, V0).mean() >= 0.9 and fails(best, 0, V0).mean() >= 0.9, True)

    # ------------------------------------------------------------------ 8. R5-genie bit identity best vs last
    p("\n## 8. R5-genie of the last tag bit-identical to the best tag (every key, every SNR, every trial)")
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

    # ------------------------------------------------------------------ 9. loader cross-check
    p("\n## 9. loader cross-check: analysis.load_raw vs this direct read (+9 / -3 dB; b*, V1, genie, V0; R0-pilot@1 alias)")
    sys.path.insert(0, os.path.join(CONF, "code"))
    from analysis import load_raw  # noqa: E402
    data, meta, warns = load_raw("D2", root=os.path.join(CONF, "raw_SRTB16e4"))
    p(f"  load_raw warnings: {warns if warns else 'none'}")
    for s in (9, -3):
        for a in (BS, V1, GEN, V0):
            chk(f"load_raw == direct read {a} {s:+d} dB", np.array_equal(np.asarray(data[('C2', 'SRT', float(s))][a]['blk_err']), best[s][a]['blk']), True)
    chk("load_raw meta ll_val|kron", float(meta[("C2", "SRT")]["ll_val|kron"]), EXP_META["ll_val"], 1e-9)
    chk("load_raw R0-pilot@1 alias +9 dB == direct @1", int(np.asarray(data[('C2', 'SRT', 9.0)]['R0-pilot@1']['blk_err'])[:, -1].sum()),
        int(fails(best, 9, "R0-pilot", 0).sum()))

    # ------------------------------------------------------------------ 10. GB' and checkpoints
    p("\n## 10. GB' (csv / npz / log) and the checkpoint records")
    import csv
    rows = list(csv.DictReader(open(os.path.join(CONF, "results", "d2_gbprime_SRT.csv"))))
    r = rows[-1]
    p(f"  csv: {r}")
    chk("GB' median (4 dp)", round(float(r["ratio_median"]), 4), EXP_GBP["median"]); chk("GB' min", round(float(r["ratio_min"]), 4), EXP_GBP["mn"])
    chk("GB' max", round(float(r["ratio_max"]), 4), EXP_GBP["mx"]); chk("GB' b*", (r["gmm_bstar"], int(r["gmm_K"])), ("kron", 4096))
    chk("GB' equal_budget", r["equal_budget"], "True"); chk("GB' epochs", int(r["epochs"]), 617)
    z = np.load(os.path.join(CONF, "results", "d2_gbprime_SRT_N160000_a1_fb2.npz"), allow_pickle=True)
    p(f"  npz keys: {z.files}")
    for k in z.files:
        v = z[k]
        if v.ndim == 1 and v.size in (20, 21) and np.issubdtype(v.dtype, np.floating):
            p(f"    {k}: n={v.size} median {np.median(v):.4f} min {v.min():.4f} max {v.max():.4f}")
    chk("GB' median <= 0.90 (prediction 6)", float(r["ratio_median"]) <= 0.90, True)
    import torch  # noqa: E402
    for role, f in (("best", "ckpt/d2sx_SRT_N160000_a1_fb2_best.pt"), ("last", "ckpt/d2sx_SRT_N160000_a1_fb2.pt")):
        ck = torch.load(os.path.join(CONF, f), map_location="cpu", weights_only=False)
        keys = {k: ck.get(k) for k in ("epoch", "best_epoch", "best_val", "stopped_by", "role", "prior", "sigma_tag", "rung", "attempt", "grad_clip", "wall_sec", "split_hash")}
        keys["train_wall_sec"] = keys["wall_sec"]
        p(f"  {role} {f}: {keys}")
        chk(f"{role} ckpt prior/sigma_tag", (keys["prior"], keys["sigma_tag"]), ("SRT", "SRT"))
        chk(f"{role} ckpt role", keys["role"], role)
        chk(f"{role} ckpt epoch", keys["epoch"], EXP_TRAIN["best_epoch"] if role == "best" else EXP_TRAIN["last_epoch"])
        chk(f"{role} ckpt best_epoch", keys["best_epoch"], EXP_TRAIN["best_epoch"])
        chk(f"{role} ckpt best_val", float(keys["best_val"]), EXP_TRAIN["best_val"], 1e-12)
        chk(f"{role} ckpt grad_clip 1.0 (ladder attempt 2)", float(keys["grad_clip"] or 0), 1.0)
        if role == "last":
            chk("last ckpt stopped_by", keys["stopped_by"], EXP_TRAIN["stopped"])
            chk("last ckpt wall (0.1 s)", round(float(keys["train_wall_sec"]), 1), EXP_TRAIN["wall_last"])
            chk("last s/epoch (2 dp)", round(float(keys["train_wall_sec"]) / keys["epoch"], 2), EXP_TRAIN["s_per_epoch"])

    p(f"\n## SUMMARY: {NCHECK[0]} values checked, {NCHECK[1]} differ from the record")
    return 0 if NCHECK[1] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
