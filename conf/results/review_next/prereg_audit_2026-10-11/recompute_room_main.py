"""recompute_room_main.py -- independent recomputation for the RECORD AUDIT of NEXT_EXPERIMENTS_ROOM16e4.md §6.1 / §6.2 (main run,
prior SRB, tags SRBB16e4 / SRBB16e4last).  Adapted from recompute_path_main.py (same method): the raw chunk files are read DIRECTLY with
numpy (no s6_gen.py, no tables_*.txt); failure counts / BLER@16 (the §6.2 table), decision SNRs by the §1 rule, exact two-sided paired
sign tests + power guard + label, best-vs-last V1, recovery R + paired bootstrap 90 % CI (recovery_ci.boot re-implemented:
default_rng(20260926), B = 2000, 5/95 pct), the saturation guard, Delta R (own unpaired resampler), SNR@0.1 by the tool's log-linear
rule, F3 guard firing, raw meta, chunk plan, R5-genie bit identity, checkpoint facts.  analysis.load_raw ONLY as a cross-check.

usage (cwd = ~/t2/conf):  CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=3 ~/miniforge3/envs/torch/bin/python -B \
    results/review_next/prereg_audit_2026-10-11/recompute_room_main.py > results/review_next/prereg_audit_2026-10-11/recompute_room_main.out
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
    V1: ([704, 126, 17, 3, 4, 0, 0], "0.275 0.049 0.007 0.001 0.002 0.000 0.000"),
    "V1last": ([734, 128, 22, 3, 1, 2, 0], "0.287 0.050 0.009 0.001 0.000 0.001 0.000"),
    V4: ([742, 133, 27, 4, 4, 0, 0], "0.290 0.052 0.011 0.002 0.002 0.000 0.000"),
    V4B: ([740, 130, 23, 4, 3, 0, 0], "0.289 0.051 0.009 0.002 0.001 0.000 0.000"),
    BS: ([827, 153, 40, 6, 5, 1, 1], "0.323 0.060 0.016 0.002 0.002 0.000 0.000"),
    SC: ([865, 184, 48, 10, 4, 0, 1], "0.338 0.072 0.019 0.004 0.002 0.000 0.000"),
    "M-ours-gmm32": ([1242, 345, 82, 15, 11, 1, 3], "0.485 0.135 0.032 0.006 0.004 0.000 0.001"),
    R2: ([1685, 670, 178, 49, 18, 4, 2], "0.658 0.262 0.070 0.019 0.007 0.002 0.001"),
    "R1-turbo": ([2089, 1198, 406, 108, 44, 10, 6], "0.816 0.468 0.159 0.042 0.017 0.004 0.002"),
    "R0-pilot@1": ([2420, 1807, 860, 318, 140, 53, 17], "0.945 0.706 0.336 0.124 0.055 0.021 0.007"),
    "R0-pilot": ([2061, 931, 246, 69, 21, 7, 3], "0.805 0.364 0.096 0.027 0.008 0.003 0.001"),
    "R4-scvamp": ([2228, 1482, 690, 301, 149, 73, 21], "0.870 0.579 0.270 0.118 0.058 0.029 0.008"),
    "R3-bigamp": ([2252, 1369, 634, 382, 291, 342, 331], "0.880 0.535 0.248 0.149 0.114 0.134 0.129"),
    "R4-llr": ([2401, 2174, 2003, 1500, 931, 531, 273], "0.938 0.849 0.782 0.586 0.364 0.207 0.107"),
    V0: ([2560, 2560, 2559, 2557, 2519, 2304, 1674], "1.000 1.000 1.000 0.999 0.984 0.900 0.654"),
    GEN: ([299, 36, 9, 1, 0, 0, 0], "0.117 0.014 0.004 0.000 0.000 0.000 0.000")}
EXP_PAIRS = {  # (tag, x, y): ([a:b per decision SNR], pooled a:b, [p per SNR as printed] or None, pooled p as printed or None)
    ("best", BS, V1): ([(209, 86), (65, 38), (28, 5)], (302, 129), ["5.6e-13", "0.01", "6.6e-05"], "4.5e-17"),
    ("last", BS, V1): ([(196, 103), (70, 45), (24, 6)], (290, 154), ["8.2e-08", "0.025", "0.0014"], "1.1e-10"),
    ("best", BS, SC): ([(56, 94), (19, 50), (6, 14)], (81, 158), ["0.0024", "0.00024", "0.12"], "7.1e-07"),
    ("best", R2, BS): ([(534, 17), (145, 7), (46, 3)], (725, 27), None, None),
    ("best", BS, V4): ([(200, 115), (66, 46), (23, 10)], (289, 171), ["1.9e-06", "0.072", "0.035"], None),
    ("best", BS, V4B): ([(201, 114), (66, 43), (24, 7)], (291, 164), None, None),
    ("best", BS, V0): ([(0, 1733), (0, 2407), (0, 2519)], (0, 6659), None, None),
    ("best", V1, GEN): ([(427, 22), (95, 5)], (522, 27), None, None),
    ("best", BS, GEN): ([(552, 24), (127, 10)], (679, 34), None, None)}
EXP_BEST_LAST = ([(45, 75), (20, 22), (4, 9)], (69, 106), ["0.00785", "0.878", "0.267"], "0.00634")
EXP_DP = [-3, 0, 3]
EXP_DP_R2 = [0, 3, 6]
EXP_REC = {"best": {-3: (827, 704, 299, 0.233, 0.187, 0.279), 0: (153, 126, 36, 0.231, 0.100, 0.347),
                    3: (40, 17, 9, 0.742, 0.536, 0.930), "pooled": (1020, 847, 344, 0.256, 0.212, 0.299)},
           "last": {-3: (827, 734, 299, 0.176, 0.126, 0.224)},            # the record quotes recovery_diff ([0.126, 0.224]); recovery_SRBB16e4last.txt prints [0.128, 0.223]
           "D2-3": (623, 371, 87, 0.470), "D2-303": (864, 488, 125, 0.509), "dR1": -0.237, "dR1last": -0.294, "dR2": -0.253,
           "gap3": (405, 528), "gapD2_3": (284, 536)}
EXP_DR_CI = {"best": (-0.302, -0.174), "last": (-0.363, -0.229), "sec": (-0.308, -0.196)}
EXP_SAT = dict(bler=0.323, fires=False)
EXP_GUARD_V0 = {"best": [2553, 2555, 2544, 2518, 2433, 2179, 1711], "last": [2530, 2535, 2457, 2423, 1315, 1621, 216]}
EXP_GUARD_V0_RATE = {"best": [0.997, 0.998, 0.994, 0.984, 0.950, 0.851, 0.668],
                     "last": [0.988, 0.990, 0.960, 0.946, 0.514, 0.633, 0.084]}
EXP_GUARD_NEVER = sorted([a for a in ARMS if a not in (V0, GEN)])
EXP_META = dict(git="9ad4caa0", ntrain=160000, bstar="gmm1024", kron_K=2048, ll_val=97.00871495382869, ll_key="meta|ll_val|gmm1024",
                ckpt={"best": "sha256[:16]=ed437f21af15c305 epoch=1660 best_epoch=1660 role=best 8x4",
                      "last": "sha256[:16]=b5f74923f2bd2920 epoch=1680 best_epoch=1660 role=last 8x4"})
EXP_SUMS = dict(dp=(847, 902, 893), all=(854, 910, 900))
EXP_SNR01_2DP = {GEN: -2.78, V1: -1.24, V4: -1.14, V4B: -1.17, SC: -0.64, BS: -0.92, "M-ours-gmm32": 0.62, R2: 2.18,
                 "R0-pilot": 2.91, "R1-turbo": 4.04, "R4-scvamp": 6.69, "R0-pilot@1": 6.79}
EXP_SNR01_FLAG = {"R3-bigamp": ">15", "R4-llr": ">15", V0: ">15"}
EXP_GAPS = {"b*-V1": 0.32, "b*-V1 last": 0.28, "V1-genie": 1.54, "b*-genie": 1.86, "b*-scalar": -0.28, "R2-b*": 3.09, "b*-V4": 0.23, "b*-V4b": 0.25}
EXP_TRAIN = dict(best_epoch=1660, last_epoch=1680, best_val=0.24769899249076843, stopped="patience", split_hash="c009329584978bd9",
                 rung="D2SXSRB160000", attempt=1)

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
            return f"{v:.2f}", v
    return f">{SNRS[-1]:.0f}", None


def main():
    p("# recompute_room_main.py -- independent recomputation (direct numpy read of the chunk files), prior SRB")
    best, mb, prob_b, git_b = load_tag(os.path.join(CONF, "raw_SRBB16e4"), "SRB", "dft")
    last, ml, prob_l, git_l = load_tag(os.path.join(CONF, "raw_SRBB16e4last"), "SRB", "dft")
    d2, md2, prob_d2, git_d2 = load_tag(os.path.join(CONF, "raw_B16e4k"), "S2", "dft")
    tags = {"best": best, "last": last}

    p("\n## 0. chunk plan / raw meta (both tags; every chunk) + the D2 reference raw")
    for name, pr in (("raw_SRBB16e4", prob_b), ("raw_SRBB16e4last", prob_l), ("raw_B16e4k", prob_d2)):
        p(f"  {name}: problems = {pr if pr else 'none (plan {(40k,40): k=0..63} x 7 SNR, no raised/non-finite blk_err, keys complete)'}")
    for tag, m, g in (("best", mb, git_b), ("last", ml, git_l)):
        chk(f"{tag} run|git identical across 448 chunks", len(g), 1)
        chk(f"{tag} run|git", next(iter(g)), EXP_META["git"])
        chk(f"{tag} run|git has no '+dirty'", any("dirty" in x for x in g), False)
        chk(f"{tag} meta|ntrain", int(float(next(iter(m["meta|ntrain"])))), EXP_META["ntrain"])
        chk(f"{tag} meta|bstar == gmm1024 (the FULL-family K = 1024 mixture is the arm evaluated as M-ours-bstar)", next(iter(m["meta|bstar"])), EXP_META["bstar"])
        chk(f"{tag} meta|kron_K (best kron K, informational; b* is a full family)", int(float(next(iter(m["meta|kron_K"])))), EXP_META["kron_K"])
        chk(f"{tag} {EXP_META['ll_key']} (|d| <= 1e-9)", float(next(iter(m[EXP_META["ll_key"]]))), EXP_META["ll_val"], 1e-9)
        llk = {k.split("|")[-1]: float(next(iter(v))) for k, v in m.items() if k.startswith("meta|ll_val|")}
        p(f"  {tag} meta|ll_val|*: {llk}")
        chk(f"{tag} meta|ll_val: gmm1024 is the maximum over every family key (b* = argmax)", max(llk, key=llk.get), "gmm1024")
        chk(f"{tag} meta|stagec_ckpt_id", next(iter(m["meta|stagec_ckpt_id"])).split(" | ")[0], EXP_META["ckpt"][tag])
        for k in ("run|n", "run|iters", "run|seed", "run|beta", "run|t_in", "run|dtype"):
            if k in m:
                p(f"  {tag} {k} = {sorted(m[k])}")
        pr_keys = [k for k in m if "prior" in k or "sigma" in k]
        p(f"  {tag} prior/sigma-related meta keys: {{{', '.join(f'{k}: {sorted(m[k])}' for k in pr_keys)}}}")
        bud = {k[12:]: next(iter(v)) for k, v in m.items() if k.startswith("meta|budget|")}
        nt = {a: re.match(r"N_train=(\S+)", s).group(1) for a, s in bud.items()}
        p(f"  {tag} N_train per arm: {nt}")
        chk(f"{tag} N_train=160000 for every arm except R3-bigamp (0) and genie (n/a)",
            all(v == "160000" for a, v in nt.items() if a not in ("R3-bigamp", GEN)) and nt["R3-bigamp"] == "0" and nt[GEN] == "n/a", True)
        chk(f"{tag} meta|stagec_ckpt = d2sx_SRB_N160000_a1_{'best' if tag == 'best' else ''}.pt",
            os.path.basename(next(iter(m["meta|stagec_ckpt"]))), "d2sx_SRB_N160000_a1_best.pt" if tag == "best" else "d2sx_SRB_N160000_a1.pt")
    chk("raw names use 'dft' pilots (448 files per tag found by the dft glob)", all(len(glob.glob(os.path.join(CONF, r, "D2_C2_SRB_Nr8_T16_Tp4_dft_snr*_skip*_n40.npz"))) == 448 for r in ("raw_SRBB16e4", "raw_SRBB16e4last")), True)
    chk("no 'eig' raw names", sum(len(glob.glob(os.path.join(CONF, r, "*_eig_*.npz"))) for r in ("raw_SRBB16e4", "raw_SRBB16e4last")), 0)
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

    p("\n## 2. decision SNRs by the §1 rule (anchor BLER@16 in [0.005, 0.9], 3 smallest |log10(BLER/0.1)|)")
    for tag, pts in tags.items():
        for anc in (BS, R2, GEN):
            dp, bl = decision_points(pts, anc)
            p(f"  {tag} anchor {anc:14s}: {dp}   BLER@16 {{{', '.join(f'{s:+d}: {bl[s]:.4f}' for s in SNRS)}}}  "
              f"|log10(./0.1)| at chosen: {[round(abs(math.log10(bl[s] / 0.1)), 3) for s in dp]}  in-range SNRs: {[s for s in SNRS if 0.005 <= bl[s] <= 0.9]}")
            chk(f"{tag} decision SNRs anchor {anc}", dp, EXP_DP if anc == BS else EXP_DP_R2 if anc == R2 else [-3, 0])
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
        if epp:
            chk(f"{tag} {x}->{y} pooled p (%.2g)", f"{pp:.2g}", epp)
        label = ("(i)" if powered and wy >= 2 else "(ii)" if powered and wx >= 2 else "(iii)" if powered else "(iv)")
        if (x, y) == (BS, V1):
            p(f"    -> §2 label for tag {tag}: {label}   (POWERED={powered}, second arm fewer at {wy}/3, first arm fewer at {wx}/3)")
            chk(f"{tag} §2 label", label, "(i)"); chk(f"{tag} power guard", powered, True); chk(f"{tag} second arm fewer k/3", wy, 3)
        if (x, y) == (BS, SC):
            p(f"    -> control label by the registered rule: {label}  (record (ii): first arm b* fewer at 2/3, second arm fewer at 0/3)")
            chk("control b*->scalar label (ii)", label, "(ii)"); chk("control (second fewer, first fewer)", (wy, wx), (0, 2))
            chk("control: the arm with FEWER failures is b* (first arm), i.e. b*-scalar fails more at -3/0 dB", all(b > a for a, b, _ in res[:2]), True)
        if (x, y) == (R2, BS):
            chk("R2->b* b* fewer at 3/3 (prediction 6: >= 2/3)", wy, 3); chk("R2->b* POWERED", powered, True)
        if (x, y) == (BS, V0):
            chk("b*->V0 first arm (b*) fewer 3/3", wx, 3)
        if (x, y) == (BS, V4):
            chk("b*->V4 second fewer 2/3", wy, 2)
        if (x, y) == (BS, V4B):
            chk("b*->V4b second fewer 3/3", wy, 3)
        if y == GEN:
            chk(f"{x}->genie UNDECIDED (2 decision points)", (powered, len(dp)), (False, 2))

    p("\n## 4. best vs last V1, paired exact two-sided sign test (a = only best fails, b = only last fails)")
    res = [paired(best, last, s, V1, V1) for s in DP]
    A, Bn = sum(r[0] for r in res), sum(r[1] for r in res)
    p("  " + "  ".join(f"{s:+d} dB {a}:{b} p={q:.3g}" for (a, b, q), s in zip(res, DP)) + f"   pooled {A}:{Bn} p={sign_p(A, Bn):.3g}")
    chk("best-vs-last a:b per SNR", [(a, b) for a, b, _ in res], EXP_BEST_LAST[0])
    chk("best-vs-last pooled", (A, Bn), EXP_BEST_LAST[1])
    chk("best-vs-last p per SNR (3 sf)", [f"{q:.3g}" for _, _, q in res], EXP_BEST_LAST[2])
    chk("best-vs-last pooled p (3 sf)", f"{sign_p(A, Bn):.3g}", EXP_BEST_LAST[3])
    chk("best-vs-last: a (only best fails) < b (only last fails) pooled -> 'best fewer failures' is the right direction", A < Bn, True)
    chk("best-vs-last pooled p > 0.05 (prediction 11 second sentence) -> FALSE = miss", sign_p(A, Bn) > 0.05, False)
    chk("best-vs-last: only -3 dB is significant at p < .05 (so 'significant' rests on -3 dB + pooled)", [q < 0.05 for _, _, q in res], [True, False, False])

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
                tol = 0.0025 if tag == "last" else 0     # the record's last-tag CI comes from frontier_ci (a different resampler): +-0.002
                chk(f"R {tag} {key} CI lo (3 dp{', tol 0.0025' if tol else ''})", round(lo, 3), e[4], tol); chk(f"R {tag} {key} CI hi (3 dp{', tol 0.0025' if tol else ''})", round(hi, 3), e[5], tol)
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
    def boot_vals(cs):
        rng = np.random.default_rng(SEED); n = len(cs[0][0]); out = np.empty(B_BOOT)
        for i in range(B_BOOT):
            idx = rng.integers(0, n, n)
            bs = sum(b_[idx].sum() for b_, _, _ in cs); vs = sum(v_[idx].sum() for _, v_, _ in cs); gs = sum(g_[idx].sum() for _, _, g_ in cs)
            out[i] = (bs - vs) / (bs - gs) if bs - gs > 0 else np.nan
        return out
    for tag, e in (("best", EXP_DR_CI["best"]), ("last", EXP_DR_CI["last"])):
        d = boot_vals(cols(tags[tag], [-3])) - boot_vals(cols(d2, [-3]))
        lo_, hi_ = np.percentile(d[np.isfinite(d)], [5, 95])
        p(f"  Delta R {tag} -3 dB unpaired CI (my resampler, same seed for both sets): [{lo_:+.3f}, {hi_:+.3f}]  (record [{e[0]:+.3f}, {e[1]:+.3f}] from frontier_ci)")
        chk(f"Delta R {tag} CI upper < 0 (-> '회수율이 D2 보다 낮다' by the registered three-way rule)", hi_ < 0 and e[1] < 0, True)
        chk(f"Delta R {tag} CI (3 dp, tolerance 0.006: resampler details may differ)", (abs(round(lo_, 3) - e[0]) <= 0.006, abs(round(hi_, 3) - e[1]) <= 0.006), (True, True))
    d = boot_vals(cols(best, DP)) - boot_vals(cols(d2, [-3, 0, 3]))
    lo_, hi_ = np.percentile(d[np.isfinite(d)], [5, 95])
    p(f"  Delta R secondary unpaired CI (my resampler): [{lo_:+.3f}, {hi_:+.3f}]  (record [{EXP_DR_CI['sec'][0]:+.3f}, {EXP_DR_CI['sec'][1]:+.3f}])")
    chk("Delta R secondary CI (3 dp, tol 0.006)", (abs(round(lo_, 3) - EXP_DR_CI["sec"][0]) <= 0.006, abs(round(hi_, 3) - EXP_DR_CI["sec"][1]) <= 0.006), (True, True))
    b3, v3, g3 = (int(fails(best, -3, a).sum()) for a in (BS, V1, GEN))
    p(f"  failure-count gaps -3 dB: V1-genie {v3 - g3}, b*-genie {b3 - g3};  D2 -3: {v - g}, {b - g}")
    chk("gaps SRB -3 dB", (v3 - g3, b3 - g3), EXP_REC["gap3"]); chk("gaps D2 -3 dB", (v - g, b - g), EXP_REC["gapD2_3"])
    bl_bs = fails(best, -3, BS).mean()
    sat_range = not (0.005 <= bl_bs <= 0.9); sat_gen = b3 <= g3
    p(f"  saturation guard (-3 dB): b* BLER@16 = {bl_bs:.4f} in [0.005, 0.9]? {not sat_range}; b* fails {b3} <= genie {g3}? {sat_gen}"
      f" -> guard {'FIRES' if sat_range or sat_gen else 'does not fire'}")
    chk("saturation guard fires", sat_range or sat_gen, EXP_SAT["fires"])
    chk("b* BLER@16 -3 dB (3 dp)", round(bl_bs, 3), EXP_SAT["bler"])
    chk("prediction 5: R(-3 dB) CI lower > 0", EXP_REC["best"][-3][4] > 0, True)

    p("\n## 6. SNR@0.1 by the tool's log-linear rule (exp_0921_analysis.snr_at re-implemented; 2 dp as table A prints)")
    for tag, pts in tags.items():
        vals = {}
        for a in ARMS:
            vals[a] = snr_at([fails(pts, s, a).mean() for s in SNRS])
        vals["R0-pilot@1"] = snr_at([fails(pts, s, "R0-pilot", 0).mean() for s in SNRS])
        p(f"  [{tag}] " + ", ".join(f"{a}: {v[0]}" for a, v in vals.items()))
        if tag == "best":
            for a, e in EXP_SNR01_2DP.items():
                chk(f"SNR@0.1 best {a} (2 dp)", round(vals[a][1], 2), e, 0.0051)
            for a, e in EXP_SNR01_FLAG.items():
                chk(f"SNR@0.1 best {a} flag", vals[a][0], e)
            g_ = {"b*-V1": vals[BS][1] - vals[V1][1], "V1-genie": vals[V1][1] - vals[GEN][1], "b*-genie": vals[BS][1] - vals[GEN][1],
                  "b*-scalar": vals[BS][1] - vals[SC][1], "R2-b*": vals[R2][1] - vals[BS][1], "b*-V4": vals[BS][1] - vals[V4][1], "b*-V4b": vals[BS][1] - vals[V4B][1]}
            p("  best gaps: " + ", ".join(f"{k} {v:+.2f} (record {EXP_GAPS[k]:+.2f})" for k, v in g_.items()))
            for k, v in g_.items():
                chk(f"gap {k} (2 dp)", round(v, 2), EXP_GAPS[k], 0.0051)
            chk("prediction 7: V1 and b* SNR@0.1 both numbers and gap > 0", vals[V1][1] is not None and vals[BS][1] is not None and g_["b*-V1"] > 0, True)
            chk("SNR@0.1 ordering of the §6.2 bullet (genie < V1 < V4b < V4 < b* < scalar < gmm32 < R2 < R0@16 < R1 < R4-scvamp < R0@1)",
                [vals[a][1] for a in (GEN, V1, V4B, V4, BS, SC, "M-ours-gmm32", R2, "R0-pilot", "R1-turbo", "R4-scvamp", "R0-pilot@1")] ==
                sorted(vals[a][1] for a in (GEN, V1, V4B, V4, BS, SC, "M-ours-gmm32", R2, "R0-pilot", "R1-turbo", "R4-scvamp", "R0-pilot@1")), True)
        else:
            chk("last gap b*-V1 (2 dp)", round(vals[BS][1] - vals[V1][1], 2), EXP_GAPS["b*-V1 last"], 0.0051)

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
    chk("V0 -3 dB BLER = 1.000 (record)", round(fails(best, -3, V0).mean(), 3), 1.0)

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
    data, meta, warns = load_raw("D2", root=os.path.join(CONF, "raw_SRBB16e4"))
    p(f"  load_raw warnings: {warns if warns else 'none'}")
    for s in (-3, 3):
        for a in (BS, V1, GEN, V0):
            chk(f"load_raw == direct read {a} {s:+d} dB", np.array_equal(np.asarray(data[('C2', 'SRB', float(s))][a]['blk_err']), best[s][a]['blk']), True)
    chk("load_raw meta ll_val|gmm1024", float(meta[("C2", "SRB")]["ll_val|gmm1024"]), EXP_META["ll_val"], 1e-9)
    chk("load_raw R0-pilot@1 alias -3 dB == direct @1", int(np.asarray(data[('C2', 'SRB', -3.0)]['R0-pilot@1']['blk_err'])[:, -1].sum()),
        int(fails(best, -3, "R0-pilot", 0).sum()))

    p("\n## 10. checkpoint records (torch.load, CPU)")
    import hashlib
    import torch  # noqa: E402
    for role, f, esha in (("best", "ckpt/d2sx_SRB_N160000_a1_best.pt", "ed437f21af15c305"), ("last", "ckpt/d2sx_SRB_N160000_a1.pt", "b5f74923f2bd2920")):
        sha = hashlib.sha256(open(os.path.join(CONF, f), "rb").read()).hexdigest()[:16]
        ck = torch.load(os.path.join(CONF, f), map_location="cpu", weights_only=False)
        keys = {k: ck.get(k) for k in ("epoch", "best_epoch", "best_val", "stopped_by", "role", "prior", "sigma_tag", "rung", "attempt", "grad_clip", "wall_sec", "split_hash")}
        p(f"  {role} {f}: sha256[:16]={sha} {keys}")
        chk(f"{role} ckpt sha256[:16]", sha, esha)
        chk(f"{role} ckpt prior/sigma_tag", (keys["prior"], keys["sigma_tag"]), ("SRB", "SRB"))
        chk(f"{role} ckpt role", keys["role"], role)
        chk(f"{role} ckpt epoch", keys["epoch"], EXP_TRAIN["best_epoch"] if role == "best" else EXP_TRAIN["last_epoch"])
        chk(f"{role} ckpt best_epoch", keys["best_epoch"], EXP_TRAIN["best_epoch"])
        chk(f"{role} ckpt best_val", float(keys["best_val"]), EXP_TRAIN["best_val"], 1e-12)
        chk(f"{role} ckpt rung / attempt / split_hash", (keys["rung"], keys["attempt"], keys["split_hash"]), (EXP_TRAIN["rung"], EXP_TRAIN["attempt"], EXP_TRAIN["split_hash"]))
        chk(f"{role} ckpt grad_clip none (attempt 1, no clipping)", not keys["grad_clip"], True)
        if role == "last":
            chk("last ckpt stopped_by", keys["stopped_by"], EXP_TRAIN["stopped"])
            chk("last ckpt wall_sec (record 8627.0 s)", round(float(keys["wall_sec"]), 1), 8627.0, 0.06)
            chk("prediction 9: patience stop and epoch in [300, 1500] -> FALSE = miss (epoch 1680)", keys["stopped_by"] == "patience" and 300 <= keys["epoch"] <= 1500, False)

    p(f"\n## SUMMARY: {NCHECK[0]} values checked, {NCHECK[1]} differ from the record")
    return 0 if NCHECK[1] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
