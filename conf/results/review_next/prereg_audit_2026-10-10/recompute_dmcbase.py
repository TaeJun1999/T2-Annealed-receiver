"""recompute_dmcbase.py -- independent recomputation for the RECORD AUDIT of NEXT_EXPERIMENTS_DMCBASE16e4.md §5/§6.

Reads the chunk files of raw_DMCB16e4 (base, 14 arms) + raw_PILDMC + raw_ALDDMC + raw_SPDMC DIRECTLY with numpy (pair_baselines.py
is NOT imported, pairB_SPDMC.txt is NOT read) and recomputes every number of §6.1-§6.4: the 22-row failure table, the 16 table-B
pairs X -> V1 (decision SNRs by the §1 rule, exact two-sided paired sign tests, power guard, label, F_X - F_V1 at -3 dB, R_X at -3 dB
and over the decision points with the registered paired bootstrap re-implemented from its definition: default_rng(20260926),
B = 2000, percentiles 5/95), the summary lines, X*, the "멀어진다" condition, the report-only pairs quoted in §6.3 (pair_cross /
pair_ald format), the test ALD NMSE, the §2 prediction scores and the 11 count rows of conference/figures/records/paper_f21dmc.txt.
Integrity: chunk plan, run|git per raw, raw meta, R5-genie bit identity of the three raws with the base raw, meta|sparse == pick,
pick reproduced by sparse_tune.per_snr_pick (the only project import), ALD estimate file vs tune_PILDMC.json, sha256[:16] of §5/§6.
Every recomputed value is compared with the value transcribed in the record (EXPECTED below, typed from the record) -> DIFF lines.

usage (cwd = ~/t2/conf):  CUDA_VISIBLE_DEVICES= ~/miniforge3/envs/torch/bin/python \
    results/review_next/prereg_audit_2026-10-10/recompute_dmcbase.py > results/review_next/prereg_audit_2026-10-10/recompute_dmcbase.out
"""
import glob
import hashlib
import json
import math
import os
import re
import sys

import numpy as np

CONF = "/home/HTJ/t2/conf"
SNRS = [-3, 0, 3, 6, 9, 12, 15]
N, CHUNK = 2560, 40
PLAN = [(CHUNK * k, CHUNK) for k in range(N // CHUNK)]
MIN_DISC, B_BOOT, SEED = 6, 2000, 20260926
V1, BS, GEN = "M-ours-dscore-C-V1", "M-ours-bstar", "R5-genie"
R0A = "R0-pilot@1"
BL = ("M-ours-bstar-scalar", "M-ours-gmm32", R0A, "R1-turbo", "R2-ours-G", "R3-bigamp", "R4-llr", "R4-scvamp",
      "bstar-pilot", "V1-pilot", "ALD-pilot", "ALDv-pilot", "SBL-loop", "SBL-pilot", "OMP-pilot")       # 𝔅 15 in pairB order
GENIE_KEYS = ("blk_err", "ber", "nmse", "tauL_gmean", "alphaD", "tauL_clip_frac", "alphaD_clip", "guardH")

# ----------------------------------------------------------------------------- values transcribed in the record
EXP_GIT = {"raw_DMCB16e4": "27737b62", "raw_PILDMC": "3ddb0831", "raw_SPDMC": "5aa7b9b4", "raw_ALDDMC": "ff736ea2"}
EXP_FAILS = {   # §6.2 table + its "11 곡선에 없는 등록 arm" line (= pairB 22-row table, V0/V4/V4b from the DMC16e4 audit)
    GEN: [1756, 1457, 1238, 1048, 927, 754, 611], V1: [2136, 1742, 1505, 1281, 1142, 952, 801],
    BS: [2232, 1826, 1586, 1372, 1223, 1021, 884], "M-ours-bstar-scalar": [2249, 1837, 1597, 1383, 1220, 1020, 887],
    "M-ours-gmm32": [2270, 1951, 1693, 1463, 1325, 1106, 973], R0A: [2527, 2413, 2227, 2077, 1913, 1705, 1590],
    "R1-turbo": [2451, 2246, 1976, 1739, 1532, 1293, 1158], "R2-ours-G": [2330, 2050, 1801, 1592, 1440, 1209, 1090],
    "R3-bigamp": [2461, 2224, 2028, 1913, 1929, 1910, 1957], "R4-llr": [2523, 2455, 2358, 2266, 2184, 2025, 1945],
    "R4-scvamp": [2477, 2322, 2125, 1978, 1820, 1656, 1554], "bstar-pilot": [2323, 1933, 1637, 1391, 1237, 1040, 903],
    "V1-pilot": [2256, 1837, 1559, 1311, 1152, 964, 807], "ALD-pilot": [2331, 1910, 1610, 1366, 1222, 1065, 981],
    "ALDv-pilot": [2345, 1927, 1621, 1363, 1211, 1043, 938], "SBL-loop": [2272, 1969, 1710, 1504, 1335, 1137, 975],
    "SBL-pilot": [2355, 2021, 1743, 1523, 1346, 1145, 999], "OMP-pilot": [2313, 2039, 1800, 1618, 1506, 1350, 1276],
    "R0-pilot": [2413, 2117, 1838, 1618, 1451, 1256, 1119], "M-ours-dscore-C-V0": [2484, 2375, 2277, 2200, 2091, 1991, 1785],
    "M-ours-dscore-C-V4": [2148, 1749, 1515, 1287, 1136, 962, 793], "M-ours-dscore-C-V4b": [2142, 1771, 1510, 1293, 1141, 961, 801]}
# §6.1: X: (decision SNRs, a:b per SNR, pooled a:b, pooled p as printed, (V1 fewer k, X fewer k), label, F_X-F_V1 @-3,
#            R_X -3 dB ("R [lo, hi]" or ("undef", BLER 4 dp)), R_X decision points "R [lo, hi]")
EXP_B = {
    BS: ([9, 12, 15], [(127, 46), (111, 42), (119, 36)], (357, 124), "3.4e-27", (3, 0), "(i)", 96, (0.202, 0.166, 0.240), (0.279, 0.241, 0.316)),
    "M-ours-bstar-scalar": ([9, 12, 15], [(130, 52), (113, 45), (119, 33)], (362, 130), "2.4e-26", (3, 0), "(i)", 113, (0.229, 0.193, 0.267), (0.278, 0.241, 0.315)),
    "M-ours-gmm32": ([9, 12, 15], [(221, 38), (185, 31), (209, 37)], (615, 106), "4.9e-88", (3, 0), "(i)", 134, (0.261, 0.222, 0.299), (0.458, 0.428, 0.489)),
    R0A: ([9, 12, 15], [(772, 1), (754, 1), (789, 0)], (2315, 2), "0", (3, 0), "(i)", 391, ("undef", 0.9871), (0.793, 0.780, 0.807)),
    "R1-turbo": ([9, 12, 15], [(406, 16), (362, 21), (374, 17)], (1142, 54), "4e-266", (3, 0), "(i)", 315, ("undef", 0.9574), (0.643, 0.621, 0.667)),
    "R2-ours-G": ([9, 12, 15], [(325, 27), (279, 22), (310, 21)], (914, 70), "2.9e-188", (3, 0), "(i)", 194, ("undef", 0.9102), (0.583, 0.558, 0.610)),
    "R3-bigamp": ([6, 9, 12], [(638, 6), (791, 4), (960, 2)], (2389, 12), "0", (3, 0), "(i)", 325, ("undef", 0.9613), (0.786, 0.773, 0.800)),
    "R4-llr": ([9, 12, 15], [(1044, 2), (1076, 3), (1149, 5)], (3269, 10), "0", (3, 0), "(i)", 387, ("undef", 0.9855), (0.844, 0.833, 0.854)),
    "R4-scvamp": ([9, 12, 15], [(682, 4), (708, 4), (756, 3)], (2146, 11), "0", (3, 0), "(i)", 341, ("undef", 0.9676), (0.780, 0.765, 0.795)),
    "bstar-pilot": ([9, 12, 15], [(147, 52), (129, 41), (131, 29)], (407, 122), "7.8e-37", (3, 0), "(i)", 187, ("undef", 0.9074), (0.321, 0.285, 0.356)),
    "V1-pilot": ([9, 12, 15], [(35, 25), (21, 9), (14, 8)], (70, 42), "0.01", (1, 0), "(iii)", 120, (0.240, 0.204, 0.277), (0.044, 0.015, 0.072)),
    "ALD-pilot": ([9, 12, 15], [(123, 43), (150, 37), (208, 28)], (481, 108), "4.1e-57", (3, 0), "(i)", 195, ("undef", 0.9105), (0.382, 0.347, 0.415)),
    "ALDv-pilot": ([9, 12, 15], [(108, 39), (126, 35), (164, 27)], (398, 101), "1.1e-42", (3, 0), "(i)", 209, ("undef", 0.9160), (0.330, 0.295, 0.364)),
    "SBL-loop": ([9, 12, 15], [(235, 42), (211, 26), (212, 38)], (658, 106), "4.2e-98", (3, 0), "(i)", 136, (0.264, 0.220, 0.305), (0.478, 0.448, 0.508)),
    "SBL-pilot": ([9, 12, 15], [(247, 43), (218, 25), (230, 32)], (695, 100), "2e-110", (3, 0), "(i)", 219, ("undef", 0.9199), (0.497, 0.466, 0.527)),
    "OMP-pilot": ([9, 12, 15], [(396, 32), (411, 13), (481, 6)], (1288, 51), "1.2e-310", (3, 0), "(i)", 177, ("undef", 0.9035), (0.672, 0.652, 0.693))}
EXP_V1PILOT_P = ["0.25", "0.043", "0.29"]                       # §6.1 text line (V1-pilot per-SNR p)
EXP_SUMMARY = dict(iB=14, iiB=0, ndB=1, i16=15, ii16=0, nd16=1, xstar=BS, xstar_F=2232, xstar_R=(0.202, 0.166, 0.240), cond=False,
                   n_undefined_R3=10)                            # "0.9 를 넘는 10 개에서 정의되지 않는다" (§6.1 last bullets)
# §6.3 report-only pairs: (x, y): (a:b per SNR, pooled or None, label, (y fewer k, x fewer k) or None)
EXP_REPORT = {
    ("bstar-pilot", "V1-pilot"): ([(136, 51), (121, 45), (126, 30)], (383, 126), "(i)", None),
    ("bstar-pilot", BS): ([(44, 30), (36, 17), (35, 16)], None, "(i)", (2, 0)),
    ("V1-pilot", BS): ([(50, 121), (51, 108), (40, 117)], (141, 346), "(ii)", (0, 3)),
    ("ALDv-pilot", V1): ([(108, 39), (126, 35), (164, 27)], None, "(i)", None),
    ("ALD-pilot", V1): ([(123, 43), (150, 37), (208, 28)], None, "(i)", None),
    ("ALDv-pilot", "V1-pilot"): ([(104, 45), (113, 34), (158, 27)], (375, 106), "(i)", None),
    ("ALDv-pilot", BS): ([(97, 109), (103, 81), (124, 70)], None, "(iii)", None),
    ("bstar-pilot", "ALDv-pilot"): ([(120, 94), (89, 92), (76, 111)], None, "(iii)", None),
    ("ALD-pilot", "ALDv-pilot"): ([(38, 27), (40, 18), (64, 21)], None, "(i)", (2, 0))}
EXP_ALD_NMSE_DB = [-8.07, -10.94, -13.41, -16.22, -18.99, -21.26, -23.92]
EXP_SHA = {"ckpt/d2sx_DMC_N160000_a1_best.pt": "65b26ddd4f6437f4", "results/sparse/pick_DMC_C2.json": "ff25622dfcb0c7d5",
           "results/sparse/tune_DMC_C2.json": "a16ae2aad0db242d", "results/ald/tune_PILDMC.json": "8c92ea491d654012",
           "results/ald/tune_PILDMC_curves.npz": "5a8c367b695c979f", "results/ald/ald_PILDMC.npz": "ddee100645e9d8ab",
           "code/ald.py": "5d38e28679cc7542"}
EXP_PICK = dict(rho_sbl=8, rho_omp=16, edge_rho_sbl=False, edge_rho_omp=True, score_sbl=-15.408, score_omp=-14.202,
                n_em={-3: 3, 0: 5, 3: 5, 6: 5, 9: 5, 12: 5, 15: 5}, L={-3: 2, 0: 2, 3: 3, 6: 4, 9: 6, 12: 8, 15: 12},
                nmse_sbl=[-7.08, -9.77, -12.67, -15.33, -17.94, -21.11, -23.96], nmse_omp=[-7.74, -9.93, -11.87, -13.87, -15.97, -18.77, -21.26])
EXP_TUNE = dict(c=0.01, beta=0.005, stop=[384, 453, 504, 598, 600, 600, 600], v=[0.1332, 0.0662, 0.0362, 0.0190, 0.0104, 0.0056, 0.0035],
                dev=[-8.06, -11.02, -13.52, -16.46, -18.94, -21.44, -23.75], opt=("c=0.01,beta=0.0001", -16.180), def_=-16.171,
                extended=["beta=0.0001", "beta=1e-05"], n_dev=512, dev_skip=2560, ckpt_sha="65b26ddd4f6437f4", ald_py_sha="5d38e28679cc7542", git="48803fe6")
FIG_REC = "/home/HTJ/t2/conference/figures/records/paper_f21dmc.txt"
FIG_SHOW = [V1, "ALD-pilot", BS, "R2-ours-G", "R1-turbo", "R3-bigamp", R0A, "SBL-loop", "SBL-pilot", "OMP-pilot", GEN]

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


def sha16(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


# ----------------------------------------------------------------------------- direct numpy read of a raw set
def load_tag(root):
    pts, meta, problems, run_git = {}, {}, [], set()
    for snr in SNRS:
        fs = glob.glob(os.path.join(root, f"D2_C2_DMC_Nr8_T16_Tp4_eig_snr{snr}_skip*_n*.npz"))
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
                elif k == "meta|sparse":
                    pass                                                       # per SNR by construction; checked below
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
                problems.append(f"{os.path.basename(root)} snr {snr}: arm {arm} has a '|failed' key "
                                f"(raised trials: {sum(int(np.asarray(z[k]).sum()) for z in zs if k in z.files)})")
                continue
            if any(k not in z.files for z in zs):
                problems.append(f"{os.path.basename(root)} snr {snr}: '{k}' missing from some chunk")
                continue
            a = np.concatenate([np.asarray(z[k]) for z in zs])
            if len(a) != N:
                problems.append(f"{os.path.basename(root)} snr {snr}: '{k}' has {len(a)} rows")
            d.setdefault(arm, {})[q] = a
        for arm, v in d.items():
            if "blk_err" in v:
                be = v["blk_err"].astype(float)
                if (~np.isfinite(be)).any():
                    problems.append(f"{os.path.basename(root)} snr {snr}: {arm} non-finite blk_err -> failures")
                v["blk"] = np.where(np.isfinite(be), be, 1.0)
        pts[snr] = d
    return pts, meta, problems, run_git


def fails(D, snr, arm, it=-1):
    if arm == R0A:
        return D[snr]["R0-pilot"]["blk"][:, 0]
    return D[snr][arm]["blk"][:, it]


def decision_points(D, anchor):
    bl = {s: max(fails(D, s, anchor).mean(), 0.5 / N) for s in SNRS}
    cand = sorted((s for s in SNRS if 0.005 <= bl[s] <= 0.9), key=lambda s: abs(math.log10(bl[s] / 0.1)))[:3]
    return sorted(cand), bl


def paired(D, snr, x, y):
    ex, ey = fails(D, snr, x), fails(D, snr, y)
    a, b = int(np.sum((ex == 1) & (ey == 0))), int(np.sum((ex == 0) & (ey == 1)))
    return a, b, sign_p(a, b)


def table_b(D, x, y):
    cand, _ = decision_points(D, x)
    res = [paired(D, s, x, y) for s in cand]
    powered = len(cand) == 3 and sum(1 for a, b, _ in res if a + b >= MIN_DISC) >= 2
    wy = sum(1 for a, b, q in res if a > b and q < 0.05)
    wx = sum(1 for a, b, q in res if b > a and q < 0.05)
    lab = "(iv)" if not powered else "(i)" if wy >= 2 else "(ii)" if wx >= 2 else "(iii)"
    return cand, res, powered, wy, wx, lab


def boot(cols):
    """recovery_ci.boot re-implemented from its definition: fresh default_rng(SEED) per call, B replicates of n indices with
    replacement, R per replicate from the summed counts, percentiles 5/95 of the finite replicates."""
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


def recovery(cols):
    X, V, G = (sum(c[i].sum() for c in cols) for i in range(3))
    lo, hi, nn = boot(cols)
    return ((X - V) / (X - G) if X - G > 0 else float("nan")), lo, hi, nn


def snr_at_flag(bler):
    lb = np.log10(np.maximum(np.asarray(bler), 0.5 / N))
    if lb[0] <= -1:
        return "lo"
    for i in range(len(lb) - 1):
        if lb[i] > -1 >= lb[i + 1]:
            return "ok"
    return "hi"


def main():
    p("# recompute_dmcbase.py -- independent recomputation (direct numpy read of the chunk files; pair_baselines.py not imported)")
    raws = {}
    for tag in ("raw_DMCB16e4", "raw_PILDMC", "raw_ALDDMC", "raw_SPDMC"):
        raws[tag] = load_tag(os.path.join(CONF, tag))

    # ------------------------------------------------------------------ 0. chunk plan, run|git, meta
    p("\n## 0. chunk plan {(40k,40): k=0..63} x 7 SNR, run|git, meta per raw")
    for tag, (pts, meta, prob, git) in raws.items():
        p(f"  {tag}: problems = {prob if prob else 'none (plan OK, no |failed key, no non-finite blk_err, keys complete)'}")
        chk(f"{tag} run|git one value over 448 chunks", len(git), 1)
        chk(f"{tag} run|git", next(iter(git)), EXP_GIT[tag])
        chk(f"{tag} run|git clean (no +dirty)", any("dirty" in g for g in git), False)
        chk(f"{tag} meta|ntrain", int(float(next(iter(meta["meta|ntrain"])))), 160000)
        chk(f"{tag} meta|bstar", next(iter(meta["meta|bstar"])), "kron")
        chk(f"{tag} meta|kron_K", int(float(next(iter(meta["meta|kron_K"])))), 4096)
        chk(f"{tag} meta|ll_val|kron", float(next(iter(meta["meta|ll_val|kron"]))), 122.37953759128766, 1e-9)
        for k in ("run|n", "run|iters", "run|seed", "run|beta", "run|t_in", "run|dtype"):
            p(f"    {k} = {sorted(meta[k])}")
        if tag == "raw_SPDMC":
            chk(f"{tag} meta|stagec_ckpt_id absent", "meta|stagec_ckpt_id" in meta, False)
            chk(f"{tag} meta|stagec_status 'not requested'", next(iter(meta["meta|stagec_status"])).startswith("not requested"), True)
        else:
            chk(f"{tag} meta|stagec_ckpt_id", next(iter(meta["meta|stagec_ckpt_id"])), "sha256[:16]=65b26ddd4f6437f4 epoch=812 best_epoch=812 role=best 8x4")
        arms = sorted(a for a in pts[9] if "blk" in pts[9][a])
        p(f"    arms with blk_err ({len(arms)}): {arms}")
    chk("PIL arms", sorted(a for a in raws["raw_PILDMC"][0][9] if "blk" in raws["raw_PILDMC"][0][9][a]), ["R5-genie", "V1-pilot", "bstar-pilot"])
    chk("ALD arms", sorted(a for a in raws["raw_ALDDMC"][0][9] if "blk" in raws["raw_ALDDMC"][0][9][a]), ["ALD-pilot", "ALDv-pilot", "R5-genie"])
    chk("SP arms", sorted(a for a in raws["raw_SPDMC"][0][9] if "blk" in raws["raw_SPDMC"][0][9][a]), ["OMP-pilot", "R5-genie", "SBL-loop", "SBL-pilot"])
    chk("base arms (14)", len([a for a in raws["raw_DMCB16e4"][0][9] if "blk" in raws["raw_DMCB16e4"][0][9][a]]), 14)
    # ALD raw: the estimate file identity written into every chunk
    m_ald = raws["raw_ALDDMC"][1]
    chk("ALDDMC meta|ald_file = path + sha ddee100645e9d8ab", next(iter(m_ald["meta|ald_file"])),
        "/home/HTJ/t2/conf/results/ald/ald_PILDMC.npz sha256[:16]=ddee100645e9d8ab")

    # ------------------------------------------------------------------ 1. R5-genie bit identity with the base raw
    p("\n## 1. R5-genie of raw_PILDMC / raw_ALDDMC / raw_SPDMC bit-identical to raw_DMCB16e4 (8 keys x 7 SNR x 2560)")
    base = raws["raw_DMCB16e4"][0]
    for tag in ("raw_PILDMC", "raw_ALDDMC", "raw_SPDMC"):
        D = raws[tag][0]
        same = all(np.array_equal(base[s][GEN][q], D[s][GEN][q], equal_nan=True) for s in SNRS for q in GENIE_KEYS)
        chk(f"{tag} R5-genie == base (all keys, all SNR)", same, True)
        p(f"  {tag}: identical = {same}")
    # pilot-only @1 == loop @1 (pair_cross integrity, re-done)
    P = raws["raw_PILDMC"][0]
    chk("V1-pilot@1 == V1@1 (7 SNR)", all(np.array_equal(P[s]["V1-pilot"]["blk_err"][:, 0], base[s][V1]["blk_err"][:, 0]) for s in SNRS), True)
    chk("bstar-pilot@1 == b*@1 (7 SNR)", all(np.array_equal(P[s]["bstar-pilot"]["blk_err"][:, 0], base[s][BS]["blk_err"][:, 0]) for s in SNRS), True)

    # ------------------------------------------------------------------ 2. SPDMC meta|sparse == pick; pick reproduced by per_snr_pick
    p("\n## 2. meta|sparse of every SPDMC chunk == pick at its SNR; pick == sparse_tune.per_snr_pick(tune JSON)")
    pick = json.load(open(os.path.join(CONF, "results/sparse/pick_DMC_C2.json")))
    tune = json.load(open(os.path.join(CONF, "results/sparse/tune_DMC_C2.json")))
    bad = 0
    for f in glob.glob(os.path.join(CONF, "raw_SPDMC", "*.npz")):
        with np.load(f) as z:
            snr = re.search(r"_snr(-?\d+)_", f).group(1); e = pick["per_snr"][snr]
            bad += json.loads(str(z["meta|sparse"])) != dict(rho_sbl=pick["rho_sbl"], rho_omp=pick["rho_omp"], n_em=e["n_em"], L=e["L"])
    chk("SPDMC chunks with meta|sparse != pick", bad, 0)
    sys.path.insert(0, os.path.join(CONF, "code"))
    import sparse_tune as S  # noqa: E402  (allowed import: the pick rule)
    import common as Cm      # noqa: E402
    cell = Cm.CELLS["C2"]; Nn = cell["Nr"] * cell["Nt"]
    chk("tune JSON prior/cell/n", (tune["prior"], tune["cell"], tune["n"]), ("DMC", "C2", 256))
    chk("tune JSON grid = v2b", tune["grid"], dict(rho=[1, 2, 4, 8, 16], n_em=list(S.NEMS), L=list(S.LS)))
    r = S.per_snr_pick(tune["nmse_db"], cell, Nn, rhos=tune["grid"]["rho"])
    strip = lambda q: (q["rho_sbl"], q["rho_omp"], q["edge_rho_sbl"], q["edge_rho_omp"],
                       {s: (e["n_em"], e["L"], e["edge_sbl"], e["edge_omp"]) for s, e in q["per_snr"].items()})
    chk("per_snr_pick(tune) == pick (rho, edges, per-SNR n_em/L/edges)", strip(r), strip(pick))
    chk("pick rho_sbl / rho_omp", (pick["rho_sbl"], pick["rho_omp"]), (EXP_PICK["rho_sbl"], EXP_PICK["rho_omp"]))
    chk("pick edge_rho_sbl / edge_rho_omp", (pick["edge_rho_sbl"], pick["edge_rho_omp"]), (EXP_PICK["edge_rho_sbl"], EXP_PICK["edge_rho_omp"]))
    chk("pick score_sbl_db (3 dp)", round(pick["score_sbl_db"], 3), EXP_PICK["score_sbl"])
    chk("pick score_omp_db (3 dp)", round(pick["score_omp_db"], 3), EXP_PICK["score_omp"])
    for s in SNRS:
        e = pick["per_snr"][str(s)]
        chk(f"pick n_em {s:+d}", e["n_em"], EXP_PICK["n_em"][s]); chk(f"pick L {s:+d}", e["L"], EXP_PICK["L"][s])
        chk(f"pick nmse_sbl {s:+d} (2 dp)", round(e["nmse_sbl_db"], 2), EXP_PICK["nmse_sbl"][SNRS.index(s)])
        chk(f"pick nmse_omp {s:+d} (2 dp)", round(e["nmse_omp_db"], 2), EXP_PICK["nmse_omp"][SNRS.index(s)])
        chk(f"pick per-SNR edges {s:+d} (none)", (e["edge_sbl"], e["edge_omp"]), (False, False))
    p(f"  pick: rho_sbl {pick['rho_sbl']} rho_omp {pick['rho_omp']} (edge {pick['edge_rho_omp']}), n_em {[pick['per_snr'][str(s)]['n_em'] for s in SNRS]}, "
      f"L {[pick['per_snr'][str(s)]['L'] for s in SNRS]}")

    # ------------------------------------------------------------------ 3. sha256, ALD tune / estimate file
    p("\n## 3. sha256[:16] of §5/§6 files; ALD tune record vs the estimate file")
    for f, e in EXP_SHA.items():
        chk(f"sha256[:16] {f}", sha16(os.path.join(CONF, f)), e)
    tj = json.load(open(os.path.join(CONF, "results/ald/tune_PILDMC.json")))
    chk("tune c / beta", (tj["c"], tj["beta"]), (EXP_TUNE["c"], EXP_TUNE["beta"]))
    chk("tune stop steps", [tj["stop"][f"{s:.1f}"] for s in SNRS], EXP_TUNE["stop"])
    chk("tune v (4 dp)", [round(tj["v"][f"{s:.1f}"], 4) for s in SNRS], EXP_TUNE["v"])
    chk("tune dev NMSE (2 dp)", [round(tj["dev_nmse_db"][f"{s:.1f}"], 2) for s in SNRS], EXP_TUNE["dev"])
    best_key = min(tj["grid"], key=lambda k: tj["grid"][k])          # dev NMSE in dB: lower is better
    chk("tune dev optimum key", best_key, EXP_TUNE["opt"][0]); chk("tune dev optimum (3 dp)", round(tj["grid"][best_key], 3), EXP_TUNE["opt"][1])
    chk("tune beta=0.005 best c = 0.01 (3 dp)", round(tj["grid"]["c=0.01,beta=0.005"], 3), EXP_TUNE["def_"])
    chk("tune beta rule: default within 0.1 dB of optimum", tj["grid"][best_key] - tj["grid"]["c=0.01,beta=0.005"] <= 0.1, True)
    chk("tune extended / edge-after-extension", (tj["extended"], tj["optimum_at_edge_after_extension"]), (EXP_TUNE["extended"], []))
    chk("tune n_dev / dev_skip", (tj["n_dev"], tj["dev_skip"]), (EXP_TUNE["n_dev"], EXP_TUNE["dev_skip"]))
    chk("tune ckpt_sha / ald_py_sha / git", (tj["ckpt_sha"], tj["ald_py_sha"], tj["git"]), (EXP_TUNE["ckpt_sha"], EXP_TUNE["ald_py_sha"], EXP_TUNE["git"]))
    chk("tune ckpt relative path (script passes the same string)", tj["ckpt"], "ckpt/d2sx_DMC_N160000_a1_best.pt")
    chk("stop <= L*M = 600", max(tj["stop"].values()) <= tj["L"] * tj["M"], True)
    z = np.load(os.path.join(CONF, "results/ald/ald_PILDMC.npz"))
    chk("estimate 'tune' json == tune_PILDMC.json", json.loads(str(z["tune"])), tj)
    chk("estimate ckpt_sha", str(z["ckpt_sha"]), EXP_TUNE["ckpt_sha"])
    prov = json.loads(str(z["prov"]))
    chk("estimate prov ckpt_sha / ald_py_sha", (prov["ckpt_sha"], prov["ald_py_sha"]), (EXP_TUNE["ckpt_sha"], EXP_TUNE["ald_py_sha"]))
    chk("estimate prov git = ff736ea2 (start 3)", prov["git"], "ff736ea2")
    chk("estimate v == tune v", np.allclose(z["v"], [tj["v"][f"{s:.1f}"] for s in SNRS], rtol=0, atol=0), True)
    chk("estimate snrs / skip", (z["snrs"].tolist(), int(z["skip"])), ([float(s) for s in SNRS], 0))
    chk("estimate hhat shape (7, 2560, 32)", z["hhat"].shape, (7, 2560, 32))
    nm_db = [round(10 * math.log10(x), 2) for x in z["nmse"]]
    chk("test ALD NMSE dB (estimate file mean)", nm_db, EXP_ALD_NMSE_DB)
    chk("ALDDMC meta|ald_tune == tune_PILDMC.json", json.loads(next(iter(m_ald["meta|ald_tune"]))), tj)
    A = raws["raw_ALDDMC"][0]
    # the receiver's ALD arms report the estimate's NMSE at @1 (fixed estimate): compare with the estimate file per SNR
    for s in SNRS:
        for arm in ("ALD-pilot", "ALDv-pilot"):
            nm = A[s][arm]["nmse"]
            chk(f"{arm} nmse fixed over 16 iterations {s:+d} dB", bool(np.all(np.abs(nm - nm[:, :1]) <= 1e-12 * np.abs(nm[:, :1]))), True)
    mean_raw = [float(np.mean(A[s]["ALD-pilot"]["nmse"][:, 0])) for s in SNRS]
    p(f"  estimate-file nmse per SNR {[f'{x:.6g}' for x in z['nmse']]}")
    p(f"  raw ALD-pilot nmse@1 mean   {[f'{x:.6g}' for x in mean_raw]}  (definition may differ; printed, not counted)")
    p(f"  estimate prov: {prov}")

    # ------------------------------------------------------------------ 4. merged data; failure table (22 rows)
    p("\n## 4. BLER@16 failure counts / 2560 (22 rows: pairB table order)")
    D = {s: {**base[s], **{x: P[s][x] for x in ("V1-pilot", "bstar-pilot")}, **{x: A[s][x] for x in ("ALD-pilot", "ALDv-pilot")},
             **{x: raws["raw_SPDMC"][0][s][x] for x in ("SBL-loop", "SBL-pilot", "OMP-pilot")}} for s in SNRS}
    F = {}
    for arm, exp in EXP_FAILS.items():
        F[arm] = [int(fails(D, s, arm).sum()) for s in SNRS]
        p(f"  {arm:22s} " + " ".join(f"{x:5d}" for x in F[arm]))
        for s, x, e in zip(SNRS, F[arm], exp):
            chk(f"fails {arm} {s:+d} dB", x, e)
    chk("genie BLER -3 dB (3 dp) = 0.686", round(F[GEN][0] / N, 3), 0.686)

    # ------------------------------------------------------------------ 5. table B: 16 pairs X -> V1
    p("\n## 5. table B X -> V1 (anchor X; exact two-sided sign test; power guard; label; F_X - F_V1 @-3; R_X -3 dB and decision points)")
    labs, rows, n_undef = {}, [], 0
    fv3, fg3 = fails(D, -3, V1), fails(D, -3, GEN)
    vg = fg3.sum() >= fv3.sum()
    chk("genie -3 dB fails < V1 (R_X defined in principle)", bool(vg), False)
    for x in (BS,) + BL:
        e = EXP_B[x]
        cand, res, powered, wy, wx, lab = table_b(D, x, V1)
        labs[x] = lab
        Aa, Bb = sum(r[0] for r in res), sum(r[1] for r in res)
        pp = sign_p(Aa, Bb)
        fx = fails(D, -3, x)
        bl = fx.mean()
        if vg or not (0.005 <= bl <= 0.9) or fx.sum() <= fg3.sum():
            r1 = ("undef", round(bl, 4)); n_undef += 1; r1s = f"undefined (BLER {bl:.4f})"
        else:
            R, lo, hi, nn = recovery([(fx, fv3, fg3)]); r1 = (round(R, 3), round(lo, 3), round(hi, 3)); r1s = f"{R:.3f} [{lo:.3f}, {hi:.3f}]" + (f" ({nn} undef)" if nn else "")
        cols2 = [tuple(fails(D, s, a) for a in (x, V1, GEN)) for s in cand]
        R2, lo2, hi2, nn2 = recovery(cols2); r2 = (round(R2, 3), round(lo2, 3), round(hi2, 3))
        _, blx = decision_points(D, x)
        p(f"  {x} -> V1  dp {cand}  BLER@16 {{{', '.join(f'{s:+d}:{blx[s]:.4f}' for s in SNRS)}}}")
        p(f"      " + "  ".join(f"{s:+d} dB {a}:{b} p={q:.2g}" for (a, b, q), s in zip(res, cand)) + f"   pooled {Aa}:{Bb} p={pp:.2g}   "
          f"{'POWERED' if powered else 'UNDECIDED'} V1 fewer {wy}/3, X fewer {wx}/3 -> {lab};  F_X-F_V1@-3 {int(fx.sum() - fv3.sum())};  "
          f"R-3 {r1s};  R dp {R2:.3f} [{lo2:.3f}, {hi2:.3f}]" + (f" ({nn2} undef)" if nn2 else ""))
        chk(f"{x} decision SNRs", cand, e[0])
        chk(f"{x} a:b per SNR", [(a, b) for a, b, _ in res], e[1])
        chk(f"{x} pooled a:b", (Aa, Bb), e[2])
        chk(f"{x} pooled p (%.2g)", f"{pp:.2g}", e[3])
        chk(f"{x} POWERED", powered, True)
        chk(f"{x} (V1 fewer, X fewer) /3", (wy, wx), e[4])
        chk(f"{x} label", lab, e[5])
        chk(f"{x} F_X - F_V1 @-3", int(fx.sum() - fv3.sum()), e[6])
        chk(f"{x} R_X -3 dB (3 dp / undefined + BLER 4 dp)", r1, e[7])
        chk(f"{x} R_X decision points (3 dp)", r2, e[8])
        rows.append((x, int(fx.sum()), lab))
        if x == "V1-pilot":
            chk("V1-pilot per-SNR p (%.2g)", [f"{q:.2g}" for _, _, q in res], EXP_V1PILOT_P)
    k = sum(1 for x in labs if labs[x] == "(i)"); mm = sum(1 for x in labs if labs[x] == "(ii)")
    kB, mB = k - (labs[BS] == "(i)"), mm - (labs[BS] == "(ii)")
    p(f"  SUMMARY-B (15 without b*): (i) {kB}, (ii) {mB}, not decided {15 - kB - mB}; b* -> V1 {labs[BS]}")
    p(f"  SUMMARY 16: (i) {k}, (ii) {mm}, not decided {16 - k - mm}")
    chk("SUMMARY-B (i)/(ii)/nd", (kB, mB, 15 - kB - mB), (EXP_SUMMARY["iB"], EXP_SUMMARY["iiB"], EXP_SUMMARY["ndB"]))
    chk("SUMMARY 16 (i)/(ii)/nd", (k, mm, 16 - k - mm), (EXP_SUMMARY["i16"], EXP_SUMMARY["ii16"], EXP_SUMMARY["nd16"]))
    chk("non-(i) arms = {V1-pilot: (iii)}", {x: l for x, l in labs.items() if l != "(i)"}, {"V1-pilot": "(iii)"})
    xs = min(rows, key=lambda r: (r[1], r[0]))
    fx = fails(D, -3, xs[0]); ok_range = 0.005 <= fx.mean() <= 0.9 and fx.sum() > fg3.sum() and not vg
    R, lo, hi, nn = recovery([(fx, fv3, fg3)])
    cond = k == 16 and mm == 0 and ok_range and lo > 0
    p(f"  X* = {xs[0]} (F={xs[1]}); R_X* -3 dB = {R:.3f} [{lo:.3f}, {hi:.3f}]; '멀어진다' condition (k=16 all (i), (ii)=0, CI lower>0): {'MET' if cond else 'NOT met'}"
      f"  (k={k}, lower>0 {lo > 0})")
    chk("X* name / F", (xs[0], xs[1]), (EXP_SUMMARY["xstar"], EXP_SUMMARY["xstar_F"]))
    chk("R_X* -3 dB (3 dp)", (round(R, 3), round(lo, 3), round(hi, 3)), EXP_SUMMARY["xstar_R"])
    chk("'멀어진다' condition", cond, EXP_SUMMARY["cond"])
    chk("'전부' condition (b* (i) and all 15 (i))", labs[BS] == "(i)" and kB == 15, False)
    p(f"  undefined R_X(-3 dB) count over the 16 X: {n_undef}  (record §6.1: '0.9 를 넘는 10 개')")
    chk("number of X with R_X(-3 dB) undefined (record says 10)", n_undef, EXP_SUMMARY["n_undefined_R3"])
    flags = {x: snr_at_flag([fails(D, s, x).mean() for s in SNRS]) for x in (BS,) + BL + (V1,)}
    chk("SNR@0.1: every X and V1 'hi' (> 15 dB) -> 16 gaps n/a", all(f == "hi" for f in flags.values()), True)
    p(f"  SNR@0.1 flags: {flags}")

    # ------------------------------------------------------------------ 6. report-only pairs (§6.3)
    p("\n## 6. report-only pairs quoted in §6.3 (pair_cross / pair_ald format; anchor = first arm)")
    for (x, y), (eab, epool, elab, ek) in EXP_REPORT.items():
        cand, res, powered, wy, wx, lab = table_b(D, x, y)
        Aa, Bb = sum(r[0] for r in res), sum(r[1] for r in res)
        p(f"  {x} -> {y}  dp {cand}  " + "  ".join(f"{s:+d} dB {a}:{b} p={q:.2g}" for (a, b, q), s in zip(res, cand))
          + f"   pooled {Aa}:{Bb} p={sign_p(Aa, Bb):.2g}  {'POWERED' if powered else 'UNDECIDED'} second fewer {wy}/3 first fewer {wx}/3 -> {lab}")
        chk(f"{x}->{y} decision SNRs +9/+12/+15", cand, [9, 12, 15])
        chk(f"{x}->{y} a:b per SNR", [(a, b) for a, b, _ in res], eab)
        if epool:
            chk(f"{x}->{y} pooled", (Aa, Bb), epool)
        chk(f"{x}->{y} label", lab, elab)
        if ek:
            chk(f"{x}->{y} (second fewer, first fewer)", (wy, wx), ek)

    # ------------------------------------------------------------------ 7. §2 predictions re-scored
    p("\n## 7. §2 predictions re-scored from the data")
    pr1 = mm == 0 and kB >= 13
    p(f"  1. (ii) 0 and (i) >= 13 among the 15: (ii) {mB}, (i) {kB} -> {'HIT' if (mB == 0 and kB >= 13) else 'MISS'}")
    chk("prediction 1 HIT", mB == 0 and kB >= 13, True)
    L3, L0 = pick["per_snr"]["-3"]["L"], pick["per_snr"]["0"]["L"]
    p(f"  2a. OMP L at -3/0 dB <= 4: {L3}, {L0} -> {'HIT' if max(L3, L0) <= 4 else 'MISS'}")
    chk("prediction 2a HIT", max(L3, L0) <= 4, True)
    p2b = all(F["OMP-pilot"][i] < F[R0A][i] and F["SBL-pilot"][i] < F[R0A][i] for i in (0, 1))
    p(f"  2b. -3/0 dB OMP-pilot < R0-pilot@1 ({F['OMP-pilot'][:2]} vs {F[R0A][:2]}) and SBL-pilot < R0-pilot@1 ({F['SBL-pilot'][:2]}) -> {'HIT' if p2b else 'MISS'}")
    chk("prediction 2b HIT", p2b, True)
    p3a = all(F["ALD-pilot"][i] > F["V1-pilot"][i] for i in (0, 1, 2))
    _, _, _, _, _, labA3 = table_b(D, "ALDv-pilot", "V1-pilot")
    p(f"  3. ALD-pilot > V1-pilot at -3/0/+3 ({F['ALD-pilot'][:3]} vs {F['V1-pilot'][:3]}) -> {'HIT' if p3a else 'MISS'}; A3 ALDv-pilot -> V1-pilot = {labA3} -> {'HIT' if labA3 == '(i)' else 'MISS'}")
    chk("prediction 3a HIT", p3a, True); chk("prediction 3b A3 (i)", labA3, "(i)")
    p(f"  4. any (ii)? {mm > 0} -> {'triggered' if mm > 0 else 'not triggered'}")
    chk("prediction 4 not triggered", mm > 0, False)

    # ------------------------------------------------------------------ 8. figure record paper_f21dmc.txt
    p("\n## 8. figure record paper_f21dmc.txt: 11 count rows; 'at or below' statement; labels of the 9 drawn baselines")
    txt = open(FIG_REC, encoding="utf-8").read().split("\n")
    rows_fig = {}
    for l in txt:
        m = re.match(r"\s{4}(\S+)\s+((?:\d+/2560\s+){7})\s*raw_(\S+)", l)
        if m:
            rows_fig[m[1]] = ([int(t.split("/")[0]) for t in m[2].split()], m[3])
    chk("figure record has the 11 SHOW rows", sorted(rows_fig), sorted(FIG_SHOW))
    src_exp = {**{a: "DMCB16e4" for a in FIG_SHOW}, "ALD-pilot": "ALDDMC", "SBL-loop": "SPDMC", "SBL-pilot": "SPDMC", "OMP-pilot": "SPDMC"}
    for a in FIG_SHOW:
        chk(f"figure counts {a}", rows_fig[a][0], F[a]); chk(f"figure raw source {a}", rows_fig[a][1], src_exp[a])
    drawn_bl = [a for a in FIG_SHOW if a not in (V1, GEN)]
    below = [a for a in drawn_bl if any(F[a][i] <= F[V1][i] for i in range(7))]
    p(f"  drawn baselines (9) at or below V1 at any SNR: {below if below else 'none'}; Perfect CSI below V1 at all SNR: {all(F[GEN][i] < F[V1][i] for i in range(7))}")
    chk("no drawn BASELINE at or below V1 (figure statement, genie excluded by the script)", below, [])
    chk("labels of the 9 drawn baselines all (i)", all(labs[a] == "(i)" for a in drawn_bl), True)
    chk("figure record says 'all (i)' for 9 drawn baselines", any("of the 9 drawn baselines: all (i)." in l for l in txt), True)
    chk("figure record says below: none", any("pairB_SPDMC.txt: none." in l for l in txt), True)

    p(f"\n## SUMMARY: {NCHECK[0]} values checked, {NCHECK[1]} differ from the record")
    return 0 if NCHECK[1] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
