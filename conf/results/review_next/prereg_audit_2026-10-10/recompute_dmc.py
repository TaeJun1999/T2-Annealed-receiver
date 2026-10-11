"""recompute_dmc.py -- independent recomputation for the RECORD AUDIT of NEXT_EXPERIMENTS_DMC16e4.md §5/§6.

Reads the raw chunk files of raw_DMCB16e4 / raw_DMCB16e4last (+ raw_B16e4k for the D2 reference) DIRECTLY with numpy
(no s6_dmc.py, no tables_*.txt) and recomputes every number of §6: failure counts / BLER@16 per arm, decision SNRs by the
§1 rule, exact two-sided paired sign tests, power guard and label, best-vs-last V1 sign test, recovery R point estimates and
the unpaired Delta R, saturation guard, F3 guard firing rates, SNR@0.1 "n/a", raw-meta facts, chunk plan and the R5-genie
bit identity of the two tags.  analysis.load_raw is used ONLY as a cross-check of the loader at one SNR.
Every recomputed value is compared with the value transcribed in §6 (EXPECTED below, typed from the record) -> MATCH / DIFF.

usage (cwd = ~/t2/conf):  CUDA_VISIBLE_DEVICES= ~/miniforge3/envs/torch/bin/python \
    results/review_next/prereg_audit_2026-10-10/recompute_dmc.py > results/review_next/prereg_audit_2026-10-10/recompute_dmc.out
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
MIN_DISC = 6

# ----------------------------------------------------------------------------- values transcribed in the record (§6)
EXP_FAILS = {   # §6.2 table, best tag (R0-pilot row is @1; "pilot_C" = R0-pilot @16)
    V1: [2136, 1742, 1505, 1281, 1142, 952, 801], V4: [2148, 1749, 1515, 1287, 1136, 962, 793],
    V4B: [2142, 1771, 1510, 1293, 1141, 961, 801], BS: [2232, 1826, 1586, 1372, 1223, 1021, 884],
    SC: [2249, 1837, 1597, 1383, 1220, 1020, 887], "M-ours-gmm32": [2270, 1951, 1693, 1463, 1325, 1106, 973],
    R2: [2330, 2050, 1801, 1592, 1440, 1209, 1090], "R1-turbo": [2451, 2246, 1976, 1739, 1532, 1293, 1158],
    "R0-pilot@1": [2527, 2413, 2227, 2077, 1913, 1705, 1590], "R0-pilot": [2413, 2117, 1838, 1618, 1451, 1256, 1119],
    "R4-scvamp": [2477, 2322, 2125, 1978, 1820, 1656, 1554], "R3-bigamp": [2461, 2224, 2028, 1913, 1929, 1910, 1957],
    "R4-llr": [2523, 2455, 2358, 2266, 2184, 2025, 1945], V0: [2484, 2375, 2277, 2200, 2091, 1991, 1785],
    GEN: [1756, 1457, 1238, 1048, 927, 754, 611]}
EXP_V1_LAST = [2136, 1745, 1518, 1286, 1141, 957, 796]
EXP_PAIRS = {  # (tag, x, y): ([a:b per decision SNR], pooled a:b, [p per SNR as printed], pooled p as printed)
    ("best", BS, V1): ([(127, 46), (111, 42), (119, 36)], (357, 124), ["5.8e-10", "2.2e-08", "1.4e-11"], "3.4e-27"),
    ("last", BS, V1): ([(126, 44), (110, 46), (124, 36)], (360, 126), ["2.3e-10", "3.2e-07", "1.6e-12"], "3.9e-27"),
    ("best", BS, SC): ([(45, 42), (36, 35), (35, 38)], (116, 115), ["0.83", "1", "0.82"], "1"),
    ("best", R2, BS): ([(266, 49), (236, 48), (254, 48)], (756, 145), None, None),
    ("best", BS, V4): ([(131, 44), (110, 51), (124, 33)], (365, 128), None, None),
    ("best", BS, V4B): ([(132, 50), (112, 52), (123, 40)], (367, 142), None, None),
    ("best", BS, V0): ([(17, 885), (15, 985), (28, 929)], (60, 2799), None, None),
    ("best", V1, GEN): ([(237, 22), (215, 17), (208, 18)], (660, 57), None, None),
    ("best", BS, GEN): ([(319, 23), (289, 22), (282, 9)], (890, 54), None, None)}
EXP_BEST_LAST = ([(18, 17), (10, 15), (17, 12)], (45, 44), ["1", "0.42", "0.46"], "1")
EXP_DP = [9, 12, 15]
EXP_REC = {"best": {-3: (2232, 2136, 1756, 0.202), 9: (1223, 1142, 927, 0.274), 12: (1021, 952, 754, 0.258),
                    15: (884, 801, 611, 0.304), "pooled": (3128, 2895, 2292, 0.279)},
           "last": {-3: (2232, 2136, 1756, 0.202), "pooled": (3128, 2894, 2292, 0.280)},
           "D2-3": (623, 371, 87, 0.470), "D2-303": (864, 488, 125, 0.509), "dR1": -0.268, "dR2": -0.230,
           "gap1": (380, 476), "gapD2": (284, 536)}
EXP_GUARD_V0 = {"best": [2295, 2181, 1824, 1734, 1480, 1403, 1070], "last": [2290, 2153, 1823, 1683, 1478, 1418, 1114]}
EXP_GUARD_V0_RATE = {"best": [0.896, 0.852, 0.713, 0.677, 0.578, 0.548, 0.418],
                     "last": [0.895, 0.841, 0.712, 0.657, 0.577, 0.554, 0.435]}
EXP_META = dict(git="27737b62", ntrain=160000, bstar="kron", kron_K=4096, ll_val=122.37953759128766,
                em_sec=10073.224403858185,
                ckpt={"best": "sha256[:16]=65b26ddd4f6437f4 epoch=812 best_epoch=812 role=best 8x4",
                      "last": "sha256[:16]=92dc9f53c31af875 epoch=832 best_epoch=812 role=last 8x4"})
EXP_SUMS = dict(dp=(2895, 2891, 2903), all=(9559, 9590, 9619))

OUT = []
NCHECK = [0, 0]      # values checked, values differing


def p(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s)


def chk(label, got, exp, tol=0):
    """Count one checked value; print only on DIFF (and a summary line per block)."""
    NCHECK[0] += 1
    ok = (abs(got - exp) <= tol) if isinstance(exp, (int, float)) and not isinstance(exp, bool) else got == exp
    if not ok:
        NCHECK[1] += 1
        p(f"    DIFF  {label}: recomputed {got!r}  record {exp!r}")
    return ok


def sign_p(a, b):
    """exact two-sided sign test, as Demo/exp_0921_analysis.sign_p (binomial, p = 1/2)."""
    n = a + b
    if n == 0:
        return 1.0
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(min(a, b) + 1)) / 2 ** n)


# ----------------------------------------------------------------------------- direct numpy read of a raw set
def load_tag(root, prior, pil):
    """-> per SNR: {arm: {"blk": (N,16) float (non-finite -> 1), "nmse": (N,16), <genie keys>}}, meta (first chunk), problems."""
    pts, meta, problems, run_git = {}, {}, [], set()
    for snr in SNRS:
        fs = glob.glob(os.path.join(root, f"D2_C2_{prior}_Nr8_T16_Tp4_{pil}_snr{snr}_skip*_n*.npz"))
        ch = sorted((int(re.search(r"_skip(\d+)_n(\d+)\.npz$", f)[1]), int(re.search(r"_skip(\d+)_n(\d+)\.npz$", f)[2]), f)
                    for f in fs)
        if [(s, n) for s, n, _ in ch] != PLAN:
            problems.append(f"{os.path.basename(root)} snr {snr}: chunk plan {[(s, n) for s, n, _ in ch][:5]}... != {{(40k,40)}}")
        zs = [np.load(f) for _, _, f in ch]
        d = {}
        keys = sorted({k for z in zs for k in z.files})
        for k in keys:
            if k.startswith("run|") or k.startswith("meta|"):
                vals = {str(z[k].item()) if z[k].shape == () else str(z[k]) for z in zs if k in z.files}
                if len(vals) != 1 and k != "run|skip":          # run|skip is per chunk by construction
                    problems.append(f"{os.path.basename(root)} snr {snr}: '{k}' differs across chunks: {sorted(vals)[:3]}")
                if k == "run|skip" and sorted(int(float(v)) for v in vals) != [s for s, _ in PLAN]:
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


def decision_points(pts, anchor):
    bl = {s: max(fails(pts, s, anchor).mean(), 0.5 / N) for s in SNRS}
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
    """'hi' when BLER@16 never reaches 0.1 on the grid (exp_0925_analysis.snr_at)."""
    lb = np.log10(np.maximum(np.asarray(bler), 0.5 / N))
    if lb[0] <= -1:
        return "lo"
    for i in range(len(lb) - 1):
        if lb[i] > -1 >= lb[i + 1]:
            return "ok"
    return "hi"


def main():
    p("# recompute_dmc.py -- independent recomputation (direct numpy read of the chunk files)")
    best, mb, prob_b, git_b = load_tag(os.path.join(CONF, "raw_DMCB16e4"), "DMC", "eig")
    last, ml, prob_l, git_l = load_tag(os.path.join(CONF, "raw_DMCB16e4last"), "DMC", "eig")
    d2, md2, prob_d2, git_d2 = load_tag(os.path.join(CONF, "raw_B16e4k"), "S2", "dft")
    tags = {"best": best, "last": last}

    # ------------------------------------------------------------------ 0. chunk plan, raw meta, run|git
    p("\n## 0. chunk plan / raw meta (both tags; every chunk)")
    for name, pr in (("raw_DMCB16e4", prob_b), ("raw_DMCB16e4last", prob_l), ("raw_B16e4k", prob_d2)):
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
    p(f"  D2 reference raw_B16e4k: run|git {sorted(git_d2)}, bstar {sorted(md2['meta|bstar'])} kron_K {sorted(md2['meta|kron_K'])} ntrain {sorted(md2['meta|ntrain'])}")
    arms_present = sorted(best[9].keys())
    chk("arms present (14)", len([a for a in arms_present if "blk" in best[9][a]]), 14)
    p(f"  arms with blk_err: {[a for a in arms_present if 'blk' in best[9][a]]}")

    # ------------------------------------------------------------------ 1. failure counts / BLER@16 per arm
    p("\n## 1. failure counts and BLER@16 (best tag), R0-pilot also @1; V1 of the last tag")
    p(f"  {'arm':22s} " + "  ".join(f"{s:+3d} dB" for s in SNRS))
    for arm, exp in EXP_FAILS.items():
        it = 0 if arm == "R0-pilot@1" else -1
        a = "R0-pilot" if arm == "R0-pilot@1" else arm
        f = [int(fails(best, s, a, it).sum()) for s in SNRS]
        bl = [fails(best, s, a, it).mean() for s in SNRS]
        p(f"  {arm:22s} " + "  ".join(f"{x:4d} {b:.3f}" for x, b in zip(f, bl)))
        for s, x, e in zip(SNRS, f, exp):
            chk(f"fails best {arm} {s:+d} dB", x, e)
            chk(f"BLER best {arm} {s:+d} dB (3 dp)", round(x / N, 3), round(e / N, 3))
    f = [int(fails(last, s, V1).sum()) for s in SNRS]
    p(f"  {'V1 (last tag)':22s} " + "  ".join(f"{x:4d} {x / N:.3f}" for x in f))
    for s, x, e in zip(SNRS, f, EXP_V1_LAST):
        chk(f"fails last V1 {s:+d} dB", x, e)
    # sums quoted in §6.2
    dp_sum = tuple(sum(int(fails(best, s, a).sum()) for s in EXP_DP) for a in (V1, V4, V4B))
    all_sum = tuple(sum(int(fails(best, s, a).sum()) for s in SNRS) for a in (V1, V4, V4B))
    p(f"  decision-point sums V1/V4/V4b = {dp_sum}; 7-SNR sums = {all_sum}")
    chk("decision-point sums V1/V4/V4b", dp_sum, EXP_SUMS["dp"])
    chk("7-SNR sums V1/V4/V4b", all_sum, EXP_SUMS["all"])

    # ------------------------------------------------------------------ 2. decision SNRs (§1 rule) for the anchors used
    p("\n## 2. decision SNRs by the §1 rule (anchor BLER@16 in [0.005, 0.9], 3 smallest |log10(BLER/0.1)|)")
    for tag, pts in tags.items():
        for anc in (BS, R2, GEN):
            dp, bl = decision_points(pts, anc)
            p(f"  {tag} anchor {anc:14s}: {dp}   BLER@16 {{{', '.join(f'{s:+d}: {bl[s]:.4f}' for s in SNRS)}}}  "
              f"|log10(./0.1)| at chosen: {[round(abs(math.log10(bl[s] / 0.1)), 3) for s in dp]}")
            chk(f"{tag} decision SNRs anchor {anc}", dp, EXP_DP)
    DP = decision_points(best, BS)[0]

    # ------------------------------------------------------------------ 3. paired sign tests, power guard, label
    p("\n## 3. paired exact two-sided sign tests at the decision SNRs (a:b = only-first-fails : only-second-fails)")
    for (tag, x, y), (eab, epool, eps, epp) in EXP_PAIRS.items():
        pts = tags[tag]
        anc = x if x in (BS, R2) and y != GEN else GEN      # anchor = baseline member (b* / R2 / genie), as analysis.pair_list
        if x == R2 and y == BS:
            anc = R2
        dp, _ = decision_points(pts, anc)
        res = [paired(pts, pts, s, x, y) for s in dp]
        A, B = sum(r[0] for r in res), sum(r[1] for r in res)
        pp = sign_p(A, B)
        powered = len(dp) == 3 and sum(1 for a, b, _ in res if a + b >= MIN_DISC) >= 2
        wy = sum(1 for a, b, q in res if a > b and q < 0.05)
        wx = sum(1 for a, b, q in res if b > a and q < 0.05)
        p(f"  [{tag}] {x} -> {y}  anchor {anc}  dp {dp}: " + "  ".join(f"{s:+d} dB {a}:{b} p={q:.2g}" for (a, b, q), s in zip(res, dp))
          + f"   pooled {A}:{B} p={pp:.2g}   {'POWERED' if powered else 'UNDECIDED'}  second fewer {wy}/3  first fewer {wx}/3")
        chk(f"{tag} {x}->{y} a:b per SNR", [(a, b) for a, b, _ in res], eab)
        chk(f"{tag} {x}->{y} pooled", (A, B), epool)
        if eps:
            chk(f"{tag} {x}->{y} p per SNR (%.2g)", [f"{q:.2g}" for _, _, q in res], eps)
            chk(f"{tag} {x}->{y} pooled p (%.2g)", f"{pp:.2g}", epp)
        if (x, y) == (BS, V1):
            label = ("(i)" if powered and wy >= 2 else "(ii)" if powered and wx >= 2 else "(iii)" if powered else "(iv)")
            p(f"    -> §2 label for tag {tag}: {label}   (POWERED={powered}, second arm fewer at {wy}/3, first arm fewer at {wx}/3)")
            chk(f"{tag} §2 label", label, "(i)")
            chk(f"{tag} power guard", "POWERED" if powered else "UNDECIDED", "POWERED")
            chk(f"{tag} second arm fewer k/3", wy, 3)

    # ------------------------------------------------------------------ 4. best vs last V1
    p("\n## 4. best vs last V1, paired exact two-sided sign test (a = only best fails, b = only last fails)")
    res = [paired(best, last, s, V1, V1) for s in DP]
    A, B = sum(r[0] for r in res), sum(r[1] for r in res)
    p("  " + "  ".join(f"{s:+d} dB {a}:{b} p={q:.2g}" for (a, b, q), s in zip(res, DP)) + f"   pooled {A}:{B} p={sign_p(A, B):.2g}")
    chk("best-vs-last a:b per SNR", [(a, b) for a, b, _ in res], EXP_BEST_LAST[0])
    chk("best-vs-last pooled", (A, B), EXP_BEST_LAST[1])
    chk("best-vs-last p per SNR", [f"{q:.2g}" for _, _, q in res], EXP_BEST_LAST[2])
    chk("best-vs-last pooled p", f"{sign_p(A, B):.2g}", EXP_BEST_LAST[3])

    # ------------------------------------------------------------------ 5. recovery R point estimates, saturation guard, Delta R
    p("\n## 5. recovery R = (b* - V1)/(b* - genie) point estimates; saturation guard; unpaired Delta R point estimate")
    def counts(pts, snrs):
        return tuple(int(sum(fails(pts, s, a).sum() for s in snrs)) for a in (BS, V1, GEN))
    R = {}
    for tag, pts in tags.items():
        for key, snrs in [(-3, [-3])] + [(s, [s]) for s in DP] + [("pooled", DP)]:
            b, v, g = counts(pts, snrs)
            R[(tag, key)] = rec(b, v, g)
            p(f"  {tag} {str(key):6s} b* {b} V1 {v} genie {g}  R = {R[(tag, key)]:.3f}")
            if key in EXP_REC[tag]:
                e = EXP_REC[tag][key]
                chk(f"R {tag} {key} counts", (b, v, g), e[:3])
                chk(f"R {tag} {key} (3 dp)", round(R[(tag, key)], 3), e[3])
    b, v, g = counts(d2, [-3]); r_d2 = rec(b, v, g)
    p(f"  D2 B16e4k -3 dB  b* {b} V1 {v} genie {g}  R = {r_d2:.3f}")
    chk("D2 -3 counts", (b, v, g), EXP_REC["D2-3"][:3]); chk("D2 -3 R", round(r_d2, 3), EXP_REC["D2-3"][3])
    b2, v2, g2 = counts(d2, [-3, 0, 3]); r_d2b = rec(b2, v2, g2)
    p(f"  D2 B16e4k -3,0,3  b* {b2} V1 {v2} genie {g2}  R = {r_d2b:.3f}")
    chk("D2 -3,0,3 counts", (b2, v2, g2), EXP_REC["D2-303"][:3]); chk("D2 -3,0,3 R", round(r_d2b, 3), EXP_REC["D2-303"][3])
    dR1, dR2 = R[("best", -3)] - r_d2, R[("best", "pooled")] - r_d2b
    p(f"  Delta R primary (-3 dB) = {dR1:+.3f};  secondary (decision sum vs D2 -3,0,3) = {dR2:+.3f}")
    chk("Delta R primary (3 dp)", round(dR1, 3), EXP_REC["dR1"]); chk("Delta R secondary (3 dp)", round(dR2, 3), EXP_REC["dR2"])
    bb, vv, gg = counts(best, [-3])
    p(f"  failure-count gaps -3 dB: V1-genie {vv - gg}, b*-genie {bb - gg};  D2: {v - g}, {b - g}")
    chk("gaps DMC -3", (vv - gg, bb - gg), EXP_REC["gap1"]); chk("gaps D2 -3", (v - g, b - g), EXP_REC["gapD2"])
    bl_bs = fails(best, -3, BS).mean()
    sat = not (0.005 <= bl_bs <= 0.9) or bb <= gg
    p(f"  saturation guard (-3 dB): b* BLER@16 = {bl_bs:.4f} in [0.005, 0.9]? {0.005 <= bl_bs <= 0.9}; b* fails {bb} > genie {gg}? {bb > gg}"
      f" -> guard {'FIRES' if sat else 'does not fire'}")
    chk("saturation guard fires", sat, False)
    chk("b* BLER@16 -3 dB (3 dp)", round(bl_bs, 3), 0.872)
    p(f"  point estimate of Delta R defined? {np.isfinite(dR1)}  (undefined-replicate rule needs the bootstrap: see recovery_diff re-run)")

    # ------------------------------------------------------------------ 6. SNR@0.1
    p("\n## 6. SNR@0.1 flags (first downward crossing of 0.1 on the grid; 'hi' = never reached -> gap n/a)")
    flags = {a: snr_at_flag([fails(best, s, a).mean() for s in SNRS]) for a in ARMS}
    flags["R0-pilot@1"] = snr_at_flag([fails(best, s, "R0-pilot", 0).mean() for s in SNRS])
    p(f"  {flags}")
    chk("all arms (incl. genie, R0-pilot@1) 'hi' -> every gap n/a", all(f == "hi" for f in flags.values()), True)
    p(f"  min BLER@16 at +15 dB over arms = {min(fails(best, 15, a).mean() for a in ARMS):.3f} (genie)")

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
        exp_others = sorted([(-3, a) for a in (V1, V4, V4B, "M-ours-gmm32", "R1-turbo", R2, "R4-llr", "R4-scvamp")]
                            + [(0, a) for a in ("R1-turbo", R2, "R4-llr", "R4-scvamp")])
        chk(f"{tag} other firings exactly 1 trial each at the listed (SNR, arm)", others, exp_others)
        chk(f"{tag} other firings all == 1", all(rows[k] == 1 for k in others), True)
        never = [a for a in ARMS if a != GEN and not any((s, a) in rows for s in SNRS)]
        chk(f"{tag} arms that never fired", sorted(never), sorted([BS, SC, "R0-pilot", "R3-bigamp"]))

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
    # the TEST channels/noise are the same stream for both tags -> every arm that does not use the ckpt must also agree
    for a in (BS, SC, "M-ours-gmm32", R2, "R1-turbo", "R3-bigamp", "R4-llr", "R4-scvamp", "R0-pilot"):
        eq = all(np.array_equal(best[s][a]["blk_err"], last[s][a]["blk_err"]) for s in SNRS)
        p(f"  non-ckpt arm {a:20s} blk_err best == last: {eq}")
        chk(f"non-ckpt arm {a} identical across tags", eq, True)

    # ------------------------------------------------------------------ 9. loader cross-check (analysis.load_raw) at one SNR
    p("\n## 9. loader cross-check: analysis.load_raw vs this direct read at +9 dB and -3 dB (b*, V1, genie, V0)")
    sys.path.insert(0, os.path.join(CONF, "code"))
    from analysis import load_raw  # noqa: E402
    data, meta, warns = load_raw("D2", root=os.path.join(CONF, "raw_DMCB16e4"))
    p(f"  load_raw warnings: {warns if warns else 'none'}")
    for s in (9, -3):
        for a in (BS, V1, GEN, V0):
            x = np.asarray(data[("C2", "DMC", float(s))][a]["blk_err"])
            eq = np.array_equal(x, best[s][a]["blk"])
            chk(f"load_raw == direct read {a} {s:+d} dB", eq, True)
    chk("load_raw meta ll_val|kron", float(meta[("C2", "DMC")]["ll_val|kron"]), EXP_META["ll_val"], 1e-9)
    p(f"  load_raw R0-pilot@1 alias +9 dB fails = {int(np.asarray(data[('C2', 'DMC', 9.0)]['R0-pilot@1']['blk_err'])[:, -1].sum())}"
      f" vs direct {int(fails(best, 9, 'R0-pilot', 0).sum())}")

    p(f"\n## SUMMARY: {NCHECK[0]} values checked, {NCHECK[1]} differ from the record")
    return 0 if NCHECK[1] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
