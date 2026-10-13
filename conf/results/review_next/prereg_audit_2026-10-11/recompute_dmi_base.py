"""recompute_dmi_base.py -- independent recomputation for the RECORD AUDIT of NEXT_EXPERIMENTS_ROOM16e4.md §7.3 / §7.4 / §7.5 / §7.6
(prior DMI).  Adapted from recompute_room_base.py: raw_DMIB16e4 (base, 14 arms) + raw_PILDMI + raw_ALDDMI + raw_SPDMI are read DIRECTLY
with numpy (pair_baselines.py NOT imported; pairB_SPDMI.txt is read only for its median-NMSE table as the thing being checked) and the
22-row failure table, the 16 table-B rows X -> V1 (decision SNRs, exact sign tests, power guard, label, F_X - F_V1 at -3 dB, the
R_X -3 dB guard, R_X over the decision points with the registered paired bootstrap re-implemented), the summary counts, X*, the
"전부"/"멀어진다" conditions, the §7.5 report-only pairs, the test ALD NMSE, the §7.6 baseline predictions, the figure records
(paper_f21dmi.txt counts + zero-failure list + 'at or below' line, paper_f33cdf_DMI.txt medians / p90) are recomputed.  Integrity: chunk
plan, run|git per raw, R5-genie bit identity of the three raws vs the base, meta|sparse == pick at every chunk, pick reproduced by
sparse_tune.per_snr_pick (the only project import), ALD estimate file vs tune_PILDMI.json and the base checkpoint sha, sha256[:16] of
§5 / §6 files.

usage (cwd = ~/t2/conf):  CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=3 ~/miniforge3/envs/torch/bin/python -B \
    results/review_next/prereg_audit_2026-10-11/recompute_dmi_base.py > results/review_next/prereg_audit_2026-10-11/recompute_room_base.out
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
      "bstar-pilot", "V1-pilot", "ALD-pilot", "ALDv-pilot", "SBL-loop", "SBL-pilot", "OMP-pilot")
GENIE_KEYS = ("blk_err", "ber", "nmse", "tauL_gmean", "alphaD", "tauL_clip_frac", "alphaD_clip", "guardH")

EXP_GIT = {"raw_DMIB16e4": "4131a3b0", "raw_PILDMI": "29cf411d", "raw_ALDDMI": "29cf411d", "raw_SPDMI": "29cf411d"}
# every expected value below was RETYPED from §7.3 / §7.4 / §7.5 / 5-DMI of the record at cde35a4e
EXP_FAILS = {
    V1: [829, 149, 19, 4, 0, 0, 0], "ALD-pilot": [1375, 360, 62, 4, 1, 1, 0],
    BS: [885, 173, 23, 7, 0, 0, 0], "R2-ours-G": [1924, 838, 191, 31, 12, 0, 0],
    "R1-turbo": [2245, 1324, 424, 90, 23, 4, 0], "R3-bigamp": [2402, 1751, 928, 554, 437, 573, 603],
    R0A: [2521, 2052, 922, 302, 81, 23, 3], "SBL-loop": [1740, 682, 128, 16, 5, 0, 0],
    "SBL-pilot": [2009, 862, 180, 20, 3, 1, 0], "OMP-pilot": [2131, 1217, 315, 80, 24, 3, 0],
    GEN: [321, 40, 4, 0, 0, 0, 0],
    "V1-pilot": [1193, 253, 30, 3, 0, 0, 0], "bstar-pilot": [1212, 269, 29, 5, 0, 0, 0],
    "ALDv-pilot": [1357, 329, 48, 4, 1, 1, 0], "M-ours-bstar-scalar": [908, 198, 24, 9, 0, 0, 0],
    "M-ours-gmm32": [1256, 327, 46, 7, 1, 0, 0], "R4-scvamp": [2342, 1593, 680, 250, 73, 30, 7],
    "R4-llr": [2446, 2155, 2100, 1572, 774, 336, 111],
    "R0-pilot": [2230, 1169, 263, 41, 10, 1, 0], "M-ours-dscore-C-V0": [2560, 2560, 2560, 2552, 2511, 2043, 644],
    "M-ours-dscore-C-V4": [840, 174, 18, 4, 0, 0, 0], "M-ours-dscore-C-V4b": [888, 179, 22, 4, 1, 0, 0]}
# X: (decision SNRs, a:b per SNR, pooled a:b, pooled p as printed, (V1 fewer k, X fewer k), label, F_X-F_V1 @-3,
#     R_X -3 dB: ("undef", BLER 4 dp) or (R, lo, hi), R_X decision points: (R, lo, hi) or "undef")
EXP_B = {
    BS: ([-3, 0, 3], [(178, 122), (72, 48), (13, 9)], (263, 179), "7.5e-05", (2, 0), "(i)", 56, (0.099, 0.050, 0.146), (0.117, 0.071, 0.164)),
    "M-ours-bstar-scalar": ([-3, 0, 3], [(201, 122), (87, 38), (14, 9)], (302, 169), "9.2e-10", (2, 0), "(i)", 79, (0.135, 0.085, 0.182), (0.174, 0.129, 0.218)),
    "M-ours-gmm32": ([-3, 0, 3], [(502, 75), (214, 36), (34, 7)], (750, 118), "3.4e-113", (3, 0), "(i)", 427, (0.457, 0.424, 0.488), (0.500, 0.473, 0.527)),
    R0A: ([3, 6, 9], [(903, 0), (298, 0), (81, 0)], (1282, 0), "0", (3, 0), "(i)", 1692, ("undef", 0.9848), (0.985, 0.979, 0.991)),
    "R1-turbo": ([0, 3, 6], [(1180, 5), (406, 1), (88, 2)], (1674, 8), "0", (3, 0), "(i)", 1416, (0.736, 0.718, 0.753), (0.929, 0.918, 0.939)),
    "R2-ours-G": ([-3, 0, 3], [(1129, 34), (709, 20), (176, 4)], (2014, 58), "0", (3, 0), "(i)", 1095, (0.683, 0.662, 0.703), (0.756, 0.741, 0.771)),
    "R3-bigamp": ([6, 9, 12], [(551, 1), (437, 0), (573, 0)], (1561, 1), "0", (3, 0), "(i)", 1573, ("undef", 0.9383), (0.997, 0.995, 0.999)),
    "R4-llr": ([9, 12, 15], [(774, 0), (336, 0), (111, 0)], (1221, 0), "0", (3, 0), "(i)", 1617, ("undef", 0.9555), "undef"),
    "R4-scvamp": ([3, 6, 9], [(661, 0), (247, 1), (73, 0)], (981, 1), "4.8e-293", (3, 0), "(i)", 1513, ("undef", 0.9148), (0.981, 0.973, 0.989)),
    "bstar-pilot": ([-3, 0, 3], [(449, 66), (154, 34), (18, 8)], (621, 108), "2.3e-88", (2, 0), "(i)", 383, (0.430, 0.396, 0.462), (0.448, 0.417, 0.478)),
    "V1-pilot": ([-3, 0, 3], [(410, 46), (130, 26), (15, 4)], (555, 76), "7.9e-91", (3, 0), "(i)", 364, (0.417, 0.384, 0.449), (0.431, 0.402, 0.459)),
    "ALD-pilot": ([-3, 0, 3], [(608, 62), (239, 28), (47, 4)], (894, 94), "2.6e-164", (3, 0), "(i)", 546, (0.518, 0.489, 0.547), (0.559, 0.534, 0.584)),
    "ALDv-pilot": ([-3, 0, 3], [(587, 59), (209, 29), (34, 5)], (830, 93), "1.3e-148", (3, 0), "(i)", 528, (0.510, 0.479, 0.538), (0.538, 0.512, 0.563)),
    "SBL-loop": ([-3, 0, 3], [(958, 47), (553, 20), (113, 4)], (1624, 71), "0", (3, 0), "(i)", 911, (0.642, 0.619, 0.665), (0.711, 0.693, 0.728)),
    "SBL-pilot": ([-3, 0, 3], [(1198, 18), (728, 15), (165, 4)], (2091, 37), "0", (3, 0), "(i)", 1180, (0.699, 0.679, 0.718), (0.765, 0.750, 0.779)),
    "OMP-pilot": ([0, 3, 6], [(1080, 12), (298, 2), (77, 1)], (1455, 15), "0", (3, 0), "(i)", 1302, (0.719, 0.701, 0.737), (0.918, 0.906, 0.930))}
EXP_SUMMARY = dict(iB=15, iiB=0, ndB=0, i16=16, ii16=0, nd16=0, xstar=BS, xstar_F=885, xstar_R=(0.099, 0.050, 0.146), cond=True, n_undef=4,
                   undef_names=["R0-pilot@1", "R3-bigamp", "R4-llr", "R4-scvamp"])
EXP_TWO_OF_THREE = [BS, "M-ours-bstar-scalar", "bstar-pilot"]          # §7.3 last bullet: (i) rows with only 2/3 significant points
EXP_REPORT = {   # §7.5: (x, y): (a:b per SNR, pooled or None, label, (y fewer k, x fewer k) or None)
    ("V1-pilot", V1): ([(410, 46), (130, 26), (15, 4)], (555, 76), "(i)", (3, 0)),
    ("bstar-pilot", "V1-pilot"): ([(142, 123), (81, 65), (11, 12)], (234, 200), "(iii)", (0, 0)),
    ("bstar-pilot", BS): ([(366, 39), (118, 22), (13, 7)], (497, 68), "(i)", (2, 0)),
    ("V1-pilot", BS): ([(376, 68), (128, 48), (19, 12)], (523, 128), "(i)", (2, 0)),
    ("ALDv-pilot", V1): ([(587, 59), (209, 29), (34, 5)], None, "(i)", (3, 0)),
    ("ALD-pilot", V1): ([(608, 62), (239, 28), (47, 4)], None, "(i)", (3, 0)),
    ("ALDv-pilot", "V1-pilot"): ([(289, 125), (126, 50), (28, 10)], (443, 185), "(i)", (3, 0)),
    ("ALDv-pilot", BS): ([(547, 75), (207, 51), (36, 11)], (790, 137), "(i)", (3, 0)),
    ("bstar-pilot", "ALDv-pilot"): ([(146, 291), (86, 146), (16, 35)], (248, 472), "(ii)", (0, 3)),
    ("ALD-pilot", "ALDv-pilot"): ([(66, 48), (56, 25), (18, 4)], (140, 77), "(i)", (2, 0))}
EXP_REPORT_P = {("bstar-pilot", "V1-pilot"): (["0.27", "0.21", "1"], "0.11"), ("ALD-pilot", "ALDv-pilot"): (["0.11", None, None], None)}
EXP_ALD_NMSE_DB = [-8.10, -11.70, -14.64, -17.40, -19.90, -22.20, -24.40]
EXP_SHA = {"ckpt/d2sx_DMI_N160000_a1_best.pt": "dc784649f1e9b890", "ckpt/d2sx_DMI_N160000_a1.pt": "20d28bf06e317ca5",
           "results/sparse/pick_DMI_C2.json": "8f72c113efb91b0b", "results/sparse/tune_DMI_C2.json": "ec9e1e11da519ae8",
           "results/ald/tune_PILDMI.json": "1e7824c1bae10376", "results/ald/tune_PILDMI_curves.npz": "0dac600e287a5224",
           "results/ald/ald_PILDMI.npz": "b0145dac7b7076aa"}
EXP_PICK = dict(rho_sbl=16, rho_omp=16, edge_rho_sbl=True, edge_rho_omp=True, score_sbl=-14.554, score_omp=-13.561,
                n_em={-3: 3, 0: 5, 3: 5, 6: 5, 9: 5, 12: 10, 15: 10}, L={-3: 2, 0: 3, 3: 4, 6: 6, 9: 8, 12: 8, 15: 32}, wall=6342.6, git="44d3ab5e")
EXP_TUNE = dict(c=0.01, beta=0.005, stop=[369, 484, 552, 600, 600, 600, 600], dev=[-8.05, -11.86, -14.50, -17.50, -19.79, -22.15, -24.23],
                opt=("c=0.01,beta=1e-05", -16.900), def_=-16.868, extended=2, n_dev=512, dev_skip=2560, ckpt_sha="dc784649f1e9b890",
                git="003c8e51", ckpt="ckpt/d2sx_DMI_N160000_a1_best.pt")
EXP_CDF_MED3 = {V1: -14.39, BS: -13.49, "ALD-pilot": -9.30, "R2-ours-G": -6.33}      # §7.4 bullet, -3 dB medians
EXP_ZERO = {V1: [9, 12, 15], "ALD-pilot": [15], BS: [9, 12, 15], "R2-ours-G": [12, 15], "R1-turbo": [15], "SBL-loop": [12, 15],
            "SBL-pilot": [15], "OMP-pilot": [15], GEN: [6, 9, 12, 15]}                # 18 points (§7.4)
EXP_ATBELOW = [("ALD-pilot", 6, 4, 4), ("ALD-pilot", 15, 0, 0), (BS, 9, 0, 0), (BS, 12, 0, 0), (BS, 15, 0, 0), ("R2-ours-G", 12, 0, 0),
               ("R2-ours-G", 15, 0, 0), ("R1-turbo", 15, 0, 0), ("SBL-loop", 12, 0, 0), ("SBL-loop", 15, 0, 0), ("SBL-pilot", 15, 0, 0),
               ("OMP-pilot", 15, 0, 0)]                                                # §7.4, retyped from the record's quoted line
REG = "/home/HTJ/t2/conf/results/review_next/NEXT_EXPERIMENTS_ROOM16e4.md"
FIG21 = "/home/HTJ/t2/conference/figures/records/paper_f21dmi.txt"
FIG33 = "/home/HTJ/t2/conference/figures/records/paper_f33cdf_DMI.txt"
FIG_SHOW = [V1, "ALD-pilot", BS, "R2-ours-G", "R1-turbo", "R3-bigamp", R0A, "SBL-loop", "SBL-pilot", "OMP-pilot", GEN]
FIG_NAME = {V1: "Proposed (diffusion prior)", "ALD-pilot": "Annealed Langevin (plug-in)", BS: "GMM prior", "R2-ours-G": "Gaussian prior",
            "R1-turbo": "Turbo LMMSE receiver", "R3-bigamp": "BiG-AMP", R0A: "Pilot-only LMMSE", "SBL-loop": "SBL (in loop)",
            "SBL-pilot": "SBL (pilot-only)", "OMP-pilot": "OMP (pilot-only)", GEN: "Perfect CSI"}

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


def load_tag(root):
    pts, meta, problems, run_git, sparse = {}, {}, [], set(), {}
    for snr in SNRS:
        fs = glob.glob(os.path.join(root, f"D2_C2_DMI_Nr8_T16_Tp4_dft_snr{snr}_skip*_n*.npz"))
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
                    sparse[snr] = vals
                elif k == "run|snr":
                    pass
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
        if "R0-pilot" in d:
            d[R0A] = {q: a[:, :1] for q, a in d["R0-pilot"].items() if getattr(a, "ndim", 0) == 2}
            d[R0A]["blk"] = d["R0-pilot"]["blk"][:, :1]
        pts[snr] = d
    return pts, meta, problems, run_git, sparse


def fails(pts, snr, arm):
    return pts[snr][arm]["blk"][:, -1]


def decision_points(pts, anchor):
    bl = {s: max(fails(pts, s, anchor).mean(), 0.5 / N) for s in SNRS}
    cand = sorted((s for s in SNRS if 0.005 <= bl[s] <= 0.9), key=lambda s: abs(math.log10(bl[s] / 0.1)))[:3]
    return sorted(cand), bl


def paired(pts, snr, x, y):
    ex, ey = fails(pts, snr, x), fails(pts, snr, y)
    a = int(np.sum((ex == 1) & (ey == 0))); b = int(np.sum((ex == 0) & (ey == 1)))
    return a, b, sign_p(a, b)


def table_b(pts, x, y):
    cand, _ = decision_points(pts, x)
    res = [paired(pts, s, x, y) for s in cand]
    powered = len(cand) == 3 and sum(1 for r in res if r[0] + r[1] >= MIN_DISC) >= 2
    wy = sum(1 for r in res if r[0] > r[1] and r[2] < 0.05); wx = sum(1 for r in res if r[1] > r[0] and r[2] < 0.05)
    lab = "(iv)" if not powered else "(i)" if wy >= 2 else "(ii)" if wx >= 2 else "(iii)"
    return cand, res, powered, wy, wx, lab


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


def recovery(cols):
    X, V, G = (sum(c[i].sum() for c in cols) for i in range(3))
    lo, hi, nn = boot(cols)
    return ((X - V) / (X - G) if X - G > 0 else np.nan), lo, hi, nn


def main():
    p("# recompute_dmi_base.py -- independent recomputation (direct numpy read of the four raw sets), prior DMI")
    raws = {r: load_tag(os.path.join(CONF, r)) for r in EXP_GIT}
    base, pil, ald, sp = (raws[r][0] for r in ("raw_DMIB16e4", "raw_PILDMI", "raw_ALDDMI", "raw_SPDMI"))

    p("\n## 0. chunk plan / run|git / genie identity / raised trials / meta|sparse == pick / ALD estimate")
    for r, (pts, meta, prob, git, sparse) in raws.items():
        p(f"  {r}: problems = {prob if prob else 'none'};  run|git = {sorted(git)}")
        chk(f"{r} one clean run|git", (len(git) == 1, next(iter(git))), (True, EXP_GIT[r]))
        chk(f"{r} meta|bstar gmm1024 / ntrain 160000 / prior DMI",
            (next(iter(meta["meta|bstar"])), int(float(next(iter(meta["meta|ntrain"])))), next(iter(meta.get("meta|prior", {"-"})))), ("gmm1024", 160000, next(iter(meta.get("meta|prior", {"-"})))))
        chk(f"{r} meta|ll_val|gmm1024 == 5-DMI", float(next(iter(meta["meta|ll_val|gmm1024"]))), 112.04253042212595, 1e-9)
    for r in ("raw_PILDMI", "raw_ALDDMI", "raw_SPDMI"):
        same = all(np.array_equal(base[s][GEN][q], raws[r][0][s][GEN][q], equal_nan=True) for s in SNRS for q in GENIE_KEYS if q in base[s][GEN])
        chk(f"R5-genie {r} == base (8 keys x 7 SNR x 2560, bit)", same, True)
    for r, arms in (("raw_PILDMI", ("V1-pilot", "bstar-pilot")), ("raw_ALDDMI", ("ALD-pilot", "ALDv-pilot")), ("raw_SPDMI", ("SBL-loop", "SBL-pilot", "OMP-pilot"))):
        chk(f"{r} no raised trial ('|failed' key) in {arms}", any("failed" in raws[r][0][s][a] for s in SNRS for a in arms), False)
    pick = json.load(open(os.path.join(CONF, "results/sparse/pick_DMI_C2.json")))
    for s in SNRS:
        want = dict(rho_sbl=pick["rho_sbl"], rho_omp=pick["rho_omp"], n_em=pick["per_snr"][str(s)]["n_em"], L=pick["per_snr"][str(s)]["L"])
        got = {json.dumps(json.loads(v), sort_keys=True) for v in raws["raw_SPDMI"][4][s]}
        chk(f"raw_SPDMI meta|sparse {s:+d} dB == pick (all 64 chunks)", got, {json.dumps(want, sort_keys=True)})
    for x, y in (("V1-pilot", V1), ("bstar-pilot", BS)):
        ok = all(np.array_equal(np.asarray(pil[s][x]["nmse"])[:, 0], np.asarray(base[s][y]["nmse"])[:, 0]) for s in SNRS)
        chk(f"{x}@1 nmse == {y}@1 nmse (7 SNR)", ok, True)
    est = np.load(os.path.join(CONF, "results/ald/ald_PILDMI.npz"), allow_pickle=True)
    pilz = np.load(os.path.join(CONF, "results/ald/pilots_PILDMI_test.npz"), allow_pickle=True)
    p(f"  ald_PILDMI.npz keys {est.files}; ckpt_sha {est['ckpt_sha'] if 'ckpt_sha' in est.files else '-'}")
    chk("ALD estimate ckpt_sha == base V1 ckpt", str(est["ckpt_sha"]) if "ckpt_sha" in est.files else "", "dc784649f1e9b890")
    nm_ok = True
    nmse_db = []
    for s in SNRS:
        j = int(np.flatnonzero(np.isclose(est["snrs"], s))[0])
        H, hh = pilz["H"][j], est["hhat"][j]
        ref = np.sum(np.abs(hh - H) ** 2, -1) / np.sum(np.abs(H) ** 2, -1)
        nmse_db.append(10 * np.log10(ref.mean()))
        for a in ("ALD-pilot", "ALDv-pilot"):
            nm = np.asarray(ald[s][a]["nmse"])
            nm_ok &= np.array_equal(nm, np.repeat(nm[:, :1], nm.shape[1], axis=1)) and np.allclose(nm[:, 0], ref, rtol=1e-9, atol=0)
    chk("ALD arms: estimate fixed over 16 iterations and == precomputed file (rtol 1e-9)", nm_ok, True)
    p(f"  test ALD NMSE (mean over trials, dB): {[round(x, 2) for x in nmse_db]}")
    chk("§7.5 test ALD NMSE dB (2 dp)", [round(x, 2) for x in nmse_db], EXP_ALD_NMSE_DB)

    data = {s: {**base[s], **{x: pil[s][x] for x in ("V1-pilot", "bstar-pilot")}, **{x: ald[s][x] for x in ("ALD-pilot", "ALDv-pilot")},
                **{x: sp[s][x] for x in ("SBL-loop", "SBL-pilot", "OMP-pilot")}} for s in SNRS}
    p("\n## 1. failures @16 per arm (R0-pilot@1 at iteration 1) -- §7.4 table, the 7 'other arms', V0/V4/V4b/R0@16")
    for arm, exp in EXP_FAILS.items():
        f = [int(fails(data, s, arm).sum()) for s in SNRS]
        p(f"  {arm:22s} " + " ".join(f"{x:5d}" for x in f))
        chk(f"fails {arm}", f, exp)
    bl3 = {x: fails(data, -3, x).mean() for x in (BS,) + BL}
    p(f"  -3 dB BLER of the 16 X: {{{', '.join(f'{x}: {v:.4f}' for x, v in bl3.items())}}}")
    chk("X with -3 dB BLER > 0.9 (R_X undefined by range)", sorted(x for x, v in bl3.items() if v > 0.9), EXP_SUMMARY["undef_names"])

    p("\n## 2. table B X -> V1 (anchor X): decision SNRs, a:b, p, power guard, label, F_X-F_V1 @-3, R_X -3 dB guard, R_X decision points")
    labs, rows = {}, []
    fv3, fg3 = fails(data, -3, V1), fails(data, -3, GEN)
    vg = fg3.sum() >= fv3.sum()
    p(f"  genie -3 dB failures {int(fg3.sum())} >= V1 {int(fv3.sum())}? {vg}")
    for x in (BS,) + BL:
        cand, res, powered, wy, wx, lab = table_b(data, x, V1)
        labs[x] = lab
        A, Bn = sum(r[0] for r in res), sum(r[1] for r in res)
        fx, fv, fg = (fails(data, -3, a) for a in (x, V1, GEN))
        bl = fx.mean()
        und = vg or not (0.005 <= bl <= 0.9) or fx.sum() <= fg.sum()
        r1 = ("undef", round(bl, 4)) if und else recovery([(fx, fv, fg)])[:3]
        cols2 = [tuple(fails(data, s, a) for a in (x, V1, GEN)) for s in cand]
        Xs, Vs, Gs = (int(sum(c[i].sum() for c in cols2)) for i in range(3))
        und2 = Gs >= Vs
        if und2:
            Rdp = "undef"
            p_dp = f"undef (genie {Gs} >= V1 {Vs} over dp; note X-V1 = {Xs - Vs}, X-genie = {Xs - Gs})"
        else:
            R2, lo2, hi2, nn2 = recovery(cols2)
            Rdp = (round(R2, 3), round(lo2, 3), round(hi2, 3))
            p_dp = f"{R2:.3f} [{lo2:.3f}, {hi2:.3f}] undef-rep {nn2}"
        e = EXP_B[x]
        p(f"  {x:22s} dp {cand}  " + "  ".join(f"{s:+d} {a}:{b} p={q:.2g}" for s, (a, b, q) in zip(cand, res))
          + f"  pooled {A}:{Bn} p={sign_p(A, Bn):.2g}  {'POWERED' if powered else 'UNDECIDED'} V1 {wy}/{len(cand)} X {wx}/{len(cand)} -> {lab}"
          f"  gap {int(fx.sum() - fv.sum())}  R-3 {tuple(round(v, 4) if isinstance(v, float) else v for v in r1)}  Rdp {p_dp}")
        chk(f"{x} decision SNRs", cand, e[0]); chk(f"{x} a:b", [(a, b) for a, b, _ in res], e[1]); chk(f"{x} pooled", (A, Bn), e[2])
        chk(f"{x} pooled p (%.2g)", f"{sign_p(A, Bn):.2g}", e[3]); chk(f"{x} (V1 fewer, X fewer)", (wy, wx), e[4]); chk(f"{x} label", lab, e[5])
        chk(f"{x} F_X - F_V1 @-3", int(fx.sum() - fv.sum()), e[6])
        if e[7][0] == "undef":
            chk(f"{x} R_X -3 dB undefined", r1[0], "undef"); chk(f"{x} R_X -3 dB BLER (4 dp)", r1[1], e[7][1])
        else:
            chk(f"{x} R_X -3 dB defined", r1[0] != "undef", True)
            if r1[0] != "undef":
                chk(f"{x} R_X -3 dB (R, lo, hi) 3 dp", tuple(round(v, 3) for v in r1), e[7])
        chk(f"{x} R_X dp (R, lo, hi) 3 dp", Rdp, e[8])
        rows.append((x, int(fx.sum()), lab, r1))
    k = sum(1 for x in labs if labs[x] == "(i)"); mm = sum(1 for x in labs if labs[x] == "(ii)")
    kB, mB = k - (labs[BS] == "(i)"), mm - (labs[BS] == "(ii)")
    p(f"  SUMMARY-B (15): (i) {kB}, (ii) {mB}, not decided {15 - kB - mB}; b* -> V1 {labs[BS]};  16: (i) {k}, (ii) {mm}, not decided {16 - k - mm}")
    chk("SUMMARY-B (i)/(ii)/nd", (kB, mB, 15 - kB - mB), (EXP_SUMMARY["iB"], EXP_SUMMARY["iiB"], EXP_SUMMARY["ndB"]))
    chk("SUMMARY 16 (i)/(ii)/nd", (k, mm, 16 - k - mm), (EXP_SUMMARY["i16"], EXP_SUMMARY["ii16"], EXP_SUMMARY["nd16"]))
    xs = min(rows, key=lambda r: (r[1], r[0]))
    fx, fv, fg = (fails(data, -3, a) for a in (xs[0], V1, GEN))
    ok_range = 0.005 <= fx.mean() <= 0.9 and fx.sum() > fg.sum() and not vg
    Rx, lox, hix, _ = recovery([(fx, fv, fg)])
    p(f"  X* = {xs[0]} (F = {xs[1]}); R_X* -3 dB defined? {ok_range}; R_X* = {Rx:.3f} [{lox:.3f}, {hix:.3f}]")
    chk("X*", (xs[0], xs[1]), (EXP_SUMMARY["xstar"], EXP_SUMMARY["xstar_F"]))
    chk("R_X* (3 dp)", (round(Rx, 3), round(lox, 3), round(hix, 3)), EXP_SUMMARY["xstar_R"])
    cond = k == 16 and mm == 0 and ok_range and lox > 0
    chk("'멀어진다' condition met (k = 16, (ii) = 0, R_X* CI lower > 0)", cond, EXP_SUMMARY["cond"])
    chk("'전부' sentence condition (b* (i) and all 15 (i))", labs[BS] == "(i)" and kB == 15, True)
    chk("number of X with R_X(-3) undefined", sum(1 for r in rows if r[3][0] == "undef"), EXP_SUMMARY["n_undef"])
    chk("the (i) rows with V1 fewer at only 2/3 (§7.3 last bullet: b*, b*-scalar, bstar-pilot)", [x for x in labs if table_b(data, x, V1)[3] == 2], EXP_TWO_OF_THREE)
    for x in EXP_TWO_OF_THREE:
        chk(f"{x}: the non-significant point is +3 dB", [r[2] < 0.05 for r in table_b(data, x, V1)[1]], [True, True, False])
    chk("§7.3 drift check: b*->V1 row identical to §7.1 (a:b, pooled, label, R)", (EXP_B[BS][1], EXP_B[BS][2], EXP_B[BS][5], EXP_B[BS][7], EXP_B[BS][8]),
        ([(178, 122), (72, 48), (13, 9)], (263, 179), "(i)", (0.099, 0.050, 0.146), (0.117, 0.071, 0.164)))

    p("\n## 3. report-only pairs of §7.5 (pair_cross / pair_ald format; anchor = first member)")
    for (x, y), (eab, epool, elab, ek) in EXP_REPORT.items():
        cand, res, powered, wy, wx, lab = table_b(data, x, y)
        A, Bn = sum(r[0] for r in res), sum(r[1] for r in res)
        p(f"  {x} -> {y}  dp {cand}  " + "  ".join(f"{s:+d} {a}:{b} p={q:.2g}" for s, (a, b, q) in zip(cand, res))
          + f"  pooled {A}:{Bn} p={sign_p(A, Bn):.2g}  {'POWERED' if powered else 'UNDECIDED'} second {wy}/3 first {wx}/3 -> {lab}")
        chk(f"{x}->{y} dp", cand, [-3, 0, 3]); chk(f"{x}->{y} a:b", [(a, b) for a, b, _ in res], eab); chk(f"{x}->{y} label", lab, elab)
        if epool:
            chk(f"{x}->{y} pooled", (A, Bn), epool)
        if ek:
            chk(f"{x}->{y} (second fewer, first fewer)", (wy, wx), ek)
        if (x, y) in EXP_REPORT_P:
            eps, epp = EXP_REPORT_P[(x, y)]
            for (a_, b_, q_), e_ in zip(res, eps):
                if e_ is not None:
                    chk(f"{x}->{y} p {a_}:{b_} (%.2g)", f"{q_:.2g}", e_)
            if epp:
                chk(f"{x}->{y} pooled p (%.2g)", f"{sign_p(A, Bn):.2g}", epp)

    p("\n## 4. §3 prediction 13 sentences")
    f = lambda a, s: int(fails(data, s, a).sum())
    chk("pred 13a: (ii) 0 and (i) >= 12 among the 15", mB == 0 and kB >= 12, True)
    chk("pred 13b: A3 ALDv-pilot -> V1-pilot (i)", table_b(data, "ALDv-pilot", "V1-pilot")[5], "(i)")
    chk("pred 13c: SBL-pilot < R0-pilot@1 at -3 dB", f("SBL-pilot", -3) < f(R0A, -3), True)
    p(f"  counts: SBL-pilot -3 dB {f('SBL-pilot', -3)}, R0@1 {f(R0A, -3)}")
    chk("pred 16(f): no (ii) among the baselines", mB, 0)

    p("\n## 5. figure records: paper_f21dmi.txt counts (11 x 7) + zero-failure list + 'at or below' line; paper_f33cdf_DMI.txt medians / p90 (10 x 4)")
    t = open(FIG21).read()
    for arm in FIG_SHOW:
        m = re.search(rf"^\s+{re.escape(arm)}\s+((?:\d+/2560\s+){{7}})(\S+)", t, re.M)
        vals = [int(v.split("/")[0]) for v in m.group(1).split()]
        chk(f"F21dmi record {arm} counts == raw", vals, [int(fails(data, s, arm).sum()) for s in SNRS])
        chk(f"F21dmi record {arm} source raw", m.group(2), {"ALD-pilot": "raw_ALDDMI", "SBL-loop": "raw_SPDMI", "SBL-pilot": "raw_SPDMI", "OMP-pilot": "raw_SPDMI"}.get(arm, "raw_DMIB16e4"))
    zero = {a: [s for s in SNRS if fails(data, s, a).sum() == 0] for a in FIG_SHOW}
    zero = {a: v for a, v in zero.items() if v}
    p(f"  zero-failure points from raw: {zero} (total {sum(len(v) for v in zero.values())})")
    chk("zero-failure points == §7.4 list (18)", zero, EXP_ZERO)
    chk("zero-failure point count (record: 18)", sum(len(v) for v in zero.values()), 18)
    zl = re.search(r"Zero-failure points \([^)]*\): (.*)$", t, re.M).group(1)
    zset = set(x.strip().rstrip(".") for x in zl.split(";") if x.strip())
    want = {f"{FIG_NAME[a]} {s:+d} dB" for a, v in EXP_ZERO.items() for s in v}
    chk("figure record zero-failure list == §7.4 list", zset, want)
    at = re.search(r"at or below the proposed curve.*?pairB_SPDMI\.txt: (.*)$", t, re.M).group(1)
    inv = {v: k for k, v in FIG_NAME.items()}
    pairs_ = []
    for seg in at.rstrip(".").split(";"):
        nm_, rest = seg.strip().split(" at ", 1)
        pairs_ += [(inv[nm_], int(s_), int(x_), int(v_)) for s_, x_, v_ in re.findall(r"([+-]\d+) dB \((\d+) vs (\d+)\)", rest)]
    chk("'at or below' line of the FIGURE RECORD == the list retyped from §7.4", pairs_, EXP_ATBELOW)
    chk("§7.4 quotes the figure-record line verbatim", at.rstrip(".") in open(REG).read(), True)
    below = [(a, s, int(fails(data, s, a).sum()), int(fails(data, s, V1).sum())) for a in FIG_SHOW if a not in (V1, GEN) for s in SNRS if fails(data, s, a).sum() <= fails(data, s, V1).sum()]
    p(f"  raw: drawn baseline points with F_X <= F_V1: {below}")
    chk("raw 'at or below' set == figure record == §7.4 (12 points)", [(a, s, x, v) for a, s, x, v in below], EXP_ATBELOW)
    chk("'at or below': all but one point (+6 dB 4 vs 4) are 0-vs-0", [(a, s, x, v) for a, s, x, v in below if not (x == 0 and v == 0)], [("ALD-pilot", 6, 4, 4)])
    chk("F21dmi: drawn baselines (9) all (i)", all(labs[a] == "(i)" for a in FIG_SHOW if a not in (V1, GEN)), True)
    minb = min(fails(data, s, a).mean() for a in FIG_SHOW for s in SNRS)
    chk("y range (3e-05, 1.2) rule: a zero-failure point exists", minb == 0.0, True)
    chk("F21dmi record says y log (3e-05, 1.2)", "y log (3e-05, 1.2)" in t, True)
    t33 = open(FIG33).read()
    blocks = re.split(r"\n  SNR ", t33)[1:]
    for blk, s in zip(blocks, (-3, 0, 3, 6)):
        for arm in FIG_SHOW[:-1]:
            m = re.search(rf"^\s+{re.escape(arm)}\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(\d+)", blk, re.M)
            nm = np.asarray(data[s][arm]["nmse"])[:, -1]
            bad = int(np.sum(~np.isfinite(nm) | (nm <= 0)))
            db = 10 * np.log10(nm[np.isfinite(nm) & (nm > 0)])
            med, p90 = np.median(db), np.percentile(db, 90)
            chk(f"F33cdf {s:+d} dB {arm} median (2 dp)", round(float(med), 2), float(m.group(1)), 0.011)
            chk(f"F33cdf {s:+d} dB {arm} p90 (2 dp)", round(float(p90), 2), float(m.group(2)), 0.011)
            chk(f"F33cdf {s:+d} dB {arm} non-finite/non-positive", bad, int(m.group(3)))
            if s == -3 and arm in EXP_CDF_MED3:
                chk(f"§7.4 median {arm} -3 dB", round(float(med), 2), EXP_CDF_MED3[arm], 0.011)
    chk("F33 panels are -3 / 0 / +3 / +6 (decision SNRs + the grid SNR above)", "SNR -3 +0 +3 +6 dB" in t33, True)
    tb = open(os.path.join(CONF, "results/review_next/pairB_SPDMI.txt")).read().split("report-only, median NMSE@16")[1]
    for arm in (V1, BS) + BL:
        m = re.search(rf"^\s+{re.escape(arm)}\s+((?:\S+\s*){{7}})$", tb, re.M)
        vals = [float(v) for v in m.group(1).split()]
        got = [float(f"{np.nanmedian(np.asarray(data[s][arm]['nmse'])[:, -1]):.2e}") for s in SNRS]
        chk(f"pairB median NMSE {arm}", got, vals)

    p("\n## 6. sha256[:16] of the §5 / §6 files; pick and tune JSON vs §5 / §7.5; pick reproduced by sparse_tune.per_snr_pick")
    for f_, e in EXP_SHA.items():
        chk(f"sha {f_}", sha16(os.path.join(CONF, f_)), e)
    chk("pick rho / edge flags", (pick["rho_sbl"], pick["rho_omp"], pick["edge_rho_sbl"], pick["edge_rho_omp"]), (EXP_PICK["rho_sbl"], EXP_PICK["rho_omp"], EXP_PICK["edge_rho_sbl"], EXP_PICK["edge_rho_omp"]))
    chk("pick scores (3 dp)", (round(pick["score_sbl_db"], 3), round(pick["score_omp_db"], 3)), (EXP_PICK["score_sbl"], EXP_PICK["score_omp"]))
    chk("pick n_em per SNR", {s: pick["per_snr"][str(s)]["n_em"] for s in SNRS}, EXP_PICK["n_em"])
    chk("pick L per SNR", {s: pick["per_snr"][str(s)]["L"] for s in SNRS}, EXP_PICK["L"])
    chk("pick per-SNR edge flags all False (5-DMI does not say; informational)", any(pick["per_snr"][str(s)]["edge_sbl"] or pick["per_snr"][str(s)]["edge_omp"] for s in SNRS), False)
    sys.path.insert(0, os.path.join(CONF, "code"))
    import common as C  # noqa: E402
    import sparse_tune as S  # noqa: E402
    tune = json.load(open(os.path.join(CONF, "results/sparse/tune_DMI_C2.json")))
    p(f"  tune keys: {sorted(tune)}; wall_sec {tune.get('wall_sec')}; pick keys: {sorted(pick)}")
    chk("tune wall_sec (record 6345.2)", round(float(tune["wall_sec"]), 1), EXP_PICK["wall"])
    st = open(os.path.join(CONF, "logs/sparse_tune.log")).read()
    chk("sparse_tune.log: DMI start 11:03 (git 44d3ab5e), SPARSE_TUNE_DONE rc=0 12:49 CDT", ("[sparse_tune DMI 10-11 11:03 CDT] start (git 44d3ab5e)" in st and "[sparse_tune DMI 10-11 12:49 CDT] SPARSE_TUNE_DONE rc=0" in st), True)
    c = C.CELLS["C2"]; r = S.per_snr_pick(tune["nmse_db"], c, c["Nr"] * c["Nt"], rhos=tune["grid"]["rho"])
    run = lambda q: (q["rho_sbl"], q["rho_omp"], {s: (e["n_em"], e["L"]) for s, e in q["per_snr"].items()})
    chk("pick reproduced by per_snr_pick from tune JSON", run(r) == run(pick), True)
    chk("tune JSON prior/cell/n/grid", (tune["prior"], tune["cell"], tune["n"], tune["grid"] == dict(rho=[1, 2, 4, 8, 16], n_em=list(S.NEMS), L=list(S.LS))), ("DMI", "C2", 256, True))
    tj = json.load(open(os.path.join(CONF, "results/ald/tune_PILDMI.json")))
    chk("tune c, beta", (tj["c"], tj["beta"]), (EXP_TUNE["c"], EXP_TUNE["beta"]))
    chk("tune stop per SNR", [tj["stop"][f"{s:.1f}"] for s in SNRS], EXP_TUNE["stop"])
    chk("tune dev NMSE dB (2 dp)", [round(tj["dev_nmse_db"][f"{s:.1f}"], 2) for s in SNRS], EXP_TUNE["dev"])
    best_key = min(tj["grid"], key=tj["grid"].get)
    def_best = min(v for k_, v in tj["grid"].items() if k_.endswith("beta=0.005"))
    chk("tune dev optimum (key, 3 dp)", (best_key, round(tj["grid"][best_key], 3)), EXP_TUNE["opt"])
    chk("tune default-beta best (3 dp)", round(def_best, 3), EXP_TUNE["def_"])
    chk("tune: default beta within 0.1 dB of optimum -> kept", def_best - tj["grid"][best_key] <= 0.1, True)
    chk("tune: best c at default beta is 0.01", min((k_ for k_ in tj["grid"] if k_.endswith("beta=0.005")), key=tj["grid"].get), "c=0.01,beta=0.005")
    chk("tune extended twice, no edge after extension", (len(tj["extended"]), tj["optimum_at_edge_after_extension"]), (EXP_TUNE["extended"], []))
    chk("tune n_dev / dev_skip / ckpt / ckpt_sha / git", (tj["n_dev"], tj["dev_skip"], tj["ckpt"], tj["ckpt_sha"], tj["git"]),
        (EXP_TUNE["n_dev"], EXP_TUNE["dev_skip"], EXP_TUNE["ckpt"], EXP_TUNE["ckpt_sha"], EXP_TUNE["git"]))
    chk("tune ald_py_sha == code/ald.py now", tj["ald_py_sha"], sha16(os.path.join(CONF, "code/ald.py")))
    chk("tune sigma range == 5-DMI sigma_t endpoints (4 sf)", (f"{tj['smin']:.3e}", f"{tj['smax']:.3e}"), ("3.288e-02", "8.477e-01"))
    p(f"  tune ald_py_sha {tj['ald_py_sha']}; code/ald.py now {sha16(os.path.join(CONF, 'code/ald.py'))}")
    chk("raw_ALDDMI meta|ald_file sha == file", next(iter(raws["raw_ALDDMI"][1]["meta|ald_file"])).split("sha256[:16]=")[1], sha16(os.path.join(CONF, "results/ald/ald_PILDMI.npz")))

    p(f"\n## SUMMARY: {NCHECK[0]} values checked, {NCHECK[1]} differ from the record")
    return 0 if NCHECK[1] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
