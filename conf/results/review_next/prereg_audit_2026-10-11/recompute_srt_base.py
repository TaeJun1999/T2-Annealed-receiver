"""recompute_srt_base.py -- independent recomputation for the RECORD AUDIT of NEXT_EXPERIMENTS_SRT16e4.md §6.3 / §6.4 / §6.5 / §6.6.

Reads raw_SRTB16e4 (base, 14 arms) + raw_PILSRT + raw_ALDSRT + raw_SPSRT DIRECTLY with numpy (pair_baselines.py NOT imported,
pairB_SPSRT.txt NOT read) and recomputes: the 22-row failure table (§6.4 11 curves + the 7 other arms + V0/V4/V4b/R0@16), the
16 table-B rows X -> V1 (decision SNRs by the §1 rule, exact two-sided sign tests, power guard, label, F_X - F_V1 at -3 dB, the
R_X -3 dB guard, R_X over the decision points with the registered paired bootstrap re-implemented: default_rng(20260926), B = 2000,
5/95 pct), the summary counts, X*, the "멀어진다" condition, the report-only pairs of §6.5 (pair_cross / pair_ald format), the test
ALD NMSE, the §6.6 baseline predictions, the figure records (paper_f21srt.txt counts, paper_f33cdf_SRT.txt medians / p90), and the
median-NMSE table of pairB.  Integrity: chunk plan, run|git per raw, R5-genie bit identity (8 keys) of the three raws vs the base,
meta|sparse == pick at every chunk, pick reproduced by sparse_tune.per_snr_pick (the only project import), ALD estimate file vs
tune_PILSRT.json and the base checkpoint sha, sha256[:16] of §5 / §6 files.  DIFF lines where the record differs.

usage (cwd = ~/t2/conf):  CUDA_VISIBLE_DEVICES= ~/miniforge3/envs/torch/bin/python -B \
    results/review_next/prereg_audit_2026-10-11/recompute_srt_base.py > results/review_next/prereg_audit_2026-10-11/recompute_srt_base.out
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
EXP_GIT = {"raw_SRTB16e4": "28f38d55", "raw_PILSRT": "6cbf9a5e", "raw_ALDSRT": "6cbf9a5e", "raw_SPSRT": "6cbf9a5e"}
EXP_FAILS = {   # §6.4 table + its "11 곡선에 없는 등록 arm" line + §6.2 (V0 / V4 / V4b / R0-pilot@16)
    V1: [2320, 2056, 1781, 1661, 1504, 1391, 1331], "ALD-pilot": [2441, 2188, 1907, 1738, 1558, 1496, 1514],
    BS: [2404, 2169, 1941, 1774, 1611, 1495, 1430], "R2-ours-G": [2461, 2291, 2093, 1924, 1822, 1692, 1607],
    "R1-turbo": [2507, 2396, 2205, 2047, 1906, 1754, 1676], "R3-bigamp": [2502, 2399, 2284, 2191, 2187, 2214, 2232],
    R0A: [2547, 2500, 2389, 2289, 2202, 2092, 2029], "SBL-loop": [2423, 2212, 2001, 1846, 1684, 1585, 1535],
    "SBL-pilot": [2456, 2253, 2028, 1854, 1718, 1599, 1528], "OMP-pilot": [2535, 2211, 1974, 1878, 1759, 1655, 1647],
    GEN: [2091, 1871, 1626, 1546, 1416, 1327, 1277],
    "V1-pilot": [2379, 2118, 1825, 1687, 1507, 1394, 1331], "bstar-pilot": [2430, 2205, 1977, 1784, 1616, 1502, 1443],
    "ALDv-pilot": [2449, 2207, 1916, 1741, 1546, 1480, 1480], "M-ours-bstar-scalar": [2408, 2171, 1940, 1774, 1617, 1497, 1439],
    "M-ours-gmm32": [2438, 2214, 2019, 1828, 1673, 1551, 1495], "R4-scvamp": [2526, 2440, 2313, 2206, 2109, 2045, 1977],
    "R4-llr": [2544, 2496, 2458, 2381, 2322, 2234, 2143],
    "R0-pilot": [2491, 2326, 2121, 1948, 1832, 1696, 1626], "M-ours-dscore-C-V0": [2531, 2495, 2473, 2460, 2460, 2429, 2236],
    "M-ours-dscore-C-V4": [2329, 2054, 1767, 1662, 1496, 1396, 1321], "M-ours-dscore-C-V4b": [2323, 2051, 1772, 1662, 1501, 1400, 1328]}
# §6.3: X: (decision SNRs, a:b per SNR, pooled a:b, pooled p as printed, (V1 fewer k, X fewer k), label, F_X-F_V1 @-3,
#            R_X -3 dB ("undef", BLER 4 dp), R_X decision points (R, lo, hi))
EXP_B = {
    BS: ([9, 12, 15], [(145, 38), (126, 22), (132, 33)], (403, 93), "5.2e-47", (3, 0), "(i)", 84, ("undef", 0.9391), (0.601, 0.553, 0.650)),
    "M-ours-bstar-scalar": ([9, 12, 15], [(147, 34), (135, 29), (137, 29)], (419, 92), "7.4e-51", (3, 0), "(i)", 88, ("undef", 0.9406), (0.614, 0.566, 0.661)),
    "M-ours-gmm32": ([9, 12, 15], [(208, 39), (189, 29), (186, 22)], (583, 90), "2.6e-89", (3, 0), "(i)", 118, ("undef", 0.9523), (0.705, 0.668, 0.742)),
    R0A: ([9, 12, 15], [(698, 0), (703, 2), (698, 0)], (2099, 2), "0", (3, 0), "(i)", 227, ("undef", 0.9949), (0.911, 0.899, 0.923)),
    "R1-turbo": ([9, 12, 15], [(419, 17), (378, 15), (362, 17)], (1159, 49), "3e-276", (3, 0), "(i)", 187, ("undef", 0.9793), (0.843, 0.823, 0.864)),
    "R2-ours-G": ([9, 12, 15], [(341, 23), (319, 18), (298, 22)], (958, 63), "2.5e-206", (3, 0), "(i)", 141, ("undef", 0.9613), (0.813, 0.789, 0.838)),
    "R3-bigamp": ([6, 9, 12], [(541, 11), (687, 4), (825, 2)], (2053, 17), "0", (3, 0), "(i)", 182, ("undef", 0.9773), (0.884, 0.871, 0.898)),
    "R4-llr": ([12, 15], [(846, 3), (815, 3)], (1661, 6), "0", (2, 0), "(iv)", 224, ("undef", 0.9938), (0.933, 0.921, 0.947)),
    "R4-scvamp": ([9, 12, 15], [(611, 6), (658, 4), (649, 3)], (1918, 13), "0", (3, 0), "(i)", 206, ("undef", 0.9867), (0.902, 0.890, 0.916)),
    "bstar-pilot": ([9, 12, 15], [(155, 43), (135, 24), (140, 28)], (430, 95), "6.8e-52", (3, 0), "(i)", 110, ("undef", 0.9492), (0.619, 0.572, 0.668)),
    "V1-pilot": ([9, 12, 15], [(26, 23), (18, 15), (7, 7)], (51, 45), "0.61", (0, 0), "(iii)", 59, ("undef", 0.9293), (0.028, -0.047, 0.102)),
    "ALD-pilot": ([9, 12, 15], [(103, 49), (151, 46), (207, 24)], (461, 119), "1.9e-48", (3, 0), "(i)", 121, ("undef", 0.9535), (0.624, 0.579, 0.670)),
    "ALDv-pilot": ([9, 12, 15], [(90, 48), (132, 43), (179, 30)], (401, 121), "4.8e-36", (3, 0), "(i)", 129, ("undef", 0.9566), (0.576, 0.524, 0.629)),
    "SBL-loop": ([9, 12, 15], [(215, 35), (222, 28), (229, 25)], (666, 88), "1.1e-110", (3, 0), "(i)", 103, ("undef", 0.9465), (0.737, 0.705, 0.771)),
    "SBL-pilot": ([9, 12, 15], [(244, 30), (239, 31), (228, 31)], (711, 92), "2.6e-119", (3, 0), "(i)", 136, ("undef", 0.9594), (0.750, 0.719, 0.783)),
    "OMP-pilot": ([9, 12, 15], [(279, 24), (286, 22), (336, 20)], (901, 66), "3.6e-188", (3, 0), "(i)", 215, ("undef", 0.9902), (0.802, 0.777, 0.828))}
EXP_V1PILOT_P = ["0.78", "0.73", "1"]                           # §6.3 bullet (V1-pilot per-SNR p)
EXP_R4LLR_BLER9 = 0.907                                         # §6.3 bullet: +9 dB BLER of R4-llr out of range
EXP_SUMMARY = dict(iB=13, iiB=0, ndB=2, i16=14, ii16=0, nd16=2, xstar="V1-pilot", xstar_F=2379, cond=False, n_undef=16, min_bler3=0.9293)
# §6.5 report-only pairs: (x, y): (a:b per SNR, pooled or None, label, (y fewer k, x fewer k) or None)
EXP_REPORT = {
    ("bstar-pilot", "V1-pilot"): ([(153, 44), (130, 22), (141, 29)], (424, 95), "(i)", None),
    ("bstar-pilot", BS): ([(30, 25), (20, 13), (24, 11)], (74, 49), "(iii)", (1, 0)),
    ("V1-pilot", BS): ([(40, 144), (24, 125), (32, 131)], (96, 400), "(ii)", (0, 3)),
    ("ALDv-pilot", V1): ([(90, 48), (132, 43), (179, 30)], None, "(i)", None),
    ("ALD-pilot", V1): ([(103, 49), (151, 46), (207, 24)], None, "(i)", None),
    ("ALDv-pilot", "V1-pilot"): ([(85, 46), (122, 36), (177, 28)], (384, 110), "(i)", None),
    ("ALDv-pilot", BS): ([(60, 125), (77, 92), (119, 69)], (256, 286), "(iii)", (1, 1)),
    ("bstar-pilot", "ALDv-pilot"): ([(134, 64), (103, 81), (74, 111)], (311, 256), "(iii)", (1, 1)),
    ("ALD-pilot", "ALDv-pilot"): ([(26, 14), (33, 17), (45, 11)], (104, 42), "(i)", (2, 0))}
EXP_ALD_NMSE_DB = [-9.30, -12.46, -14.94, -18.26, -21.05, -23.55, -25.83]
EXP_SHA = {"ckpt/d2sx_SRT_N160000_a1_fb2_best.pt": "7c7354bef3bb1e40", "ckpt/d2sx_SRT_N160000_a1_fb2.pt": "918a424724fcb0ab",
           "results/sparse/pick_SRT_C2.json": "d7fac04ee4e601fe", "results/sparse/tune_SRT_C2.json": "43df40e773c2a643",
           "results/ald/tune_PILSRT.json": "42d51362230f5e25", "results/ald/tune_PILSRT_curves.npz": "015e04645fa76df9",
           "results/ald/ald_PILSRT.npz": "2c3de1268dc25017"}
EXP_PICK = dict(rho_sbl=16, rho_omp=16, edge_rho_sbl=True, edge_rho_omp=True, score_sbl=-16.147, score_omp=-15.528,
                n_em={-3: 3, 0: 5, 3: 5, 6: 5, 9: 5, 12: 5, 15: 5}, L={-3: 1, 0: 2, 3: 2, 6: 3, 9: 4, 12: 4, 15: 6})
EXP_TUNE = dict(c=0.01, beta=0.005, stop=[425, 476, 543, 600, 600, 600, 600], dev=[-9.34, -11.72, -15.35, -18.15, -20.97, -23.47, -25.61],
                opt=("c=0.01,beta=1e-05", -17.827), def_=-17.801, extended=2, n_dev=512, dev_skip=2560, ckpt_sha="7c7354bef3bb1e40",
                git="2e50f269", ckpt="ckpt/d2sx_SRT_N160000_a1_fb2_best.pt")
EXP_CDF_MED = {V1: [-14.76, -26.88, -29.90, -32.53], BS: [-12.76, -23.23, -25.90, -28.86], "ALD-pilot": [-11.14, -23.46, -25.71, -27.66],
               "R2-ours-G": [-5.70, -15.42, -18.51, -21.72]}                                   # §6.4 bullet (median dB at -3/+9/+12/+15)
FIG21 = "/home/HTJ/t2/conference/figures/records/paper_f21srt.txt"
FIG33 = "/home/HTJ/t2/conference/figures/records/paper_f33cdf_SRT.txt"
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
    pts, meta, problems, run_git, sparse = {}, {}, [], set(), {}
    for snr in SNRS:
        fs = glob.glob(os.path.join(root, f"D2_C2_SRT_Nr8_T16_Tp4_eig_snr{snr}_skip*_n*.npz"))
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
        if "R0-pilot" in d:                                   # the 1-pass alias, as analysis.load_raw
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
    p("# recompute_srt_base.py -- independent recomputation (direct numpy read of the four raw sets)")
    raws = {r: load_tag(os.path.join(CONF, r)) for r in EXP_GIT}
    base, pil, ald, sp = (raws[r][0] for r in ("raw_SRTB16e4", "raw_PILSRT", "raw_ALDSRT", "raw_SPSRT"))

    # ------------------------------------------------------------------ 0. integrity
    p("\n## 0. chunk plan / run|git / genie identity / raised trials / meta|sparse == pick")
    for r, (pts, meta, prob, git, sparse) in raws.items():
        p(f"  {r}: problems = {prob if prob else 'none'};  run|git = {sorted(git)}")
        chk(f"{r} one clean run|git", (len(git) == 1, next(iter(git))), (True, EXP_GIT[r]))
    for r in ("raw_PILSRT", "raw_ALDSRT", "raw_SPSRT"):
        same = all(np.array_equal(base[s][GEN][q], raws[r][0][s][GEN][q], equal_nan=True) for s in SNRS for q in GENIE_KEYS if q in base[s][GEN])
        chk(f"R5-genie {r} == base (8 keys x 7 SNR x 2560, bit)", same, True)
    for r, arms in (("raw_PILSRT", ("V1-pilot", "bstar-pilot")), ("raw_ALDSRT", ("ALD-pilot", "ALDv-pilot")), ("raw_SPSRT", ("SBL-loop", "SBL-pilot", "OMP-pilot"))):
        chk(f"{r} no raised trial ('|failed' key) in {arms}", any("failed" in raws[r][0][s][a] for s in SNRS for a in arms), False)
    pick = json.load(open(os.path.join(CONF, "results/sparse/pick_SRT_C2.json")))
    for s in SNRS:
        want = dict(rho_sbl=pick["rho_sbl"], rho_omp=pick["rho_omp"], n_em=pick["per_snr"][str(s)]["n_em"], L=pick["per_snr"][str(s)]["L"])
        got = {json.dumps(json.loads(v), sort_keys=True) for v in raws["raw_SPSRT"][4][s]}
        chk(f"raw_SPSRT meta|sparse {s:+d} dB == pick (all 64 chunks)", got, {json.dumps(want, sort_keys=True)})
    # pilot-only @1 == loop @1 (pair_cross integrity), ALD estimate fixed over iterations and == precomputed file
    for x, y in (("V1-pilot", V1), ("bstar-pilot", BS)):
        ok = all(np.array_equal(np.asarray(pil[s][x]["nmse"])[:, 0], np.asarray(base[s][y]["nmse"])[:, 0]) for s in SNRS)
        chk(f"{x}@1 nmse == {y}@1 nmse (7 SNR)", ok, True)
    est = np.load(os.path.join(CONF, "results/ald/ald_PILSRT.npz"), allow_pickle=True)
    pilz = np.load(os.path.join(CONF, "results/ald/pilots_PILSRT_test.npz"), allow_pickle=True)
    p(f"  ald_PILSRT.npz keys {est.files}; ckpt_sha {est['ckpt_sha'] if 'ckpt_sha' in est.files else '-'}; prov {str(est['prov'])[:120] if 'prov' in est.files else '-'}")
    chk("ALD estimate ckpt_sha == base V1 ckpt", str(est["ckpt_sha"]) if "ckpt_sha" in est.files else "", "7c7354bef3bb1e40")
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
    chk("§6.5 test ALD NMSE dB (2 dp)", [round(x, 2) for x in nmse_db], EXP_ALD_NMSE_DB)

    # ------------------------------------------------------------------ 1. merged data + failure table
    data = {s: {**base[s], **{x: pil[s][x] for x in ("V1-pilot", "bstar-pilot")}, **{x: ald[s][x] for x in ("ALD-pilot", "ALDv-pilot")},
                **{x: sp[s][x] for x in ("SBL-loop", "SBL-pilot", "OMP-pilot")}} for s in SNRS}
    p("\n## 1. failures @16 per arm (R0-pilot@1 at iteration 1) -- §6.4 table, the 7 'other arms', V0/V4/V4b/R0@16")
    for arm, exp in EXP_FAILS.items():
        f = [int(fails(data, s, arm).sum()) for s in SNRS]
        p(f"  {arm:22s} " + " ".join(f"{x:5d}" for x in f))
        chk(f"fails {arm}", f, exp)
    for arm in (BS,) + BL:
        bl3 = fails(data, -3, arm).mean()
        chk(f"{arm} -3 dB BLER > 0.9 (R_X undefined for all 16)", bl3 > 0.9, True)
    p(f"  (context, not one of the 16) V1 -3 dB BLER {fails(data, -3, V1).mean():.4f}, genie {fails(data, -3, GEN).mean():.4f}")
    bl3 = {x: fails(data, -3, x).mean() for x in (BS,) + BL}
    p(f"  min -3 dB BLER over the 16 X = {min(bl3.values()):.4f} ({min(bl3, key=bl3.get)})")
    chk("min -3 dB BLER over the 16 (4 dp) = V1-pilot", (round(min(bl3.values()), 4), min(bl3, key=bl3.get)), (EXP_SUMMARY["min_bler3"], "V1-pilot"))

    # ------------------------------------------------------------------ 2. table B X -> V1
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
        R2, lo2, hi2, nn2 = recovery(cols2)
        e = EXP_B[x]
        p(f"  {x:22s} dp {cand}  " + "  ".join(f"{s:+d} {a}:{b} p={q:.2g}" for s, (a, b, q) in zip(cand, res))
          + f"  pooled {A}:{Bn} p={sign_p(A, Bn):.2g}  {'POWERED' if powered else 'UNDECIDED'} V1 {wy}/{len(cand)} X {wx}/{len(cand)} -> {lab}"
          f"  gap {int(fx.sum() - fv.sum())}  R-3 {r1}  Rdp {R2:.3f} [{lo2:.3f}, {hi2:.3f}] undef {nn2}")
        chk(f"{x} decision SNRs", cand, e[0]); chk(f"{x} a:b", [(a, b) for a, b, _ in res], e[1]); chk(f"{x} pooled", (A, Bn), e[2])
        chk(f"{x} pooled p (%.2g)", f"{sign_p(A, Bn):.2g}", e[3]); chk(f"{x} (V1 fewer, X fewer)", (wy, wx), e[4]); chk(f"{x} label", lab, e[5])
        chk(f"{x} F_X - F_V1 @-3", int(fx.sum() - fv.sum()), e[6])
        chk(f"{x} R_X -3 dB undefined", r1[0], e[7][0]); chk(f"{x} R_X -3 dB BLER (4 dp)", r1[1], e[7][1])
        chk(f"{x} R_X dp (3 dp)", round(R2, 3), e[8][0]); chk(f"{x} R_X dp lo", round(lo2, 3), e[8][1]); chk(f"{x} R_X dp hi", round(hi2, 3), e[8][2])
        chk(f"{x} undefined replicates", nn2, 0)
        if x == "V1-pilot":
            chk("V1-pilot p per SNR (%.2g)", [f"{q:.2g}" for _, _, q in res], EXP_V1PILOT_P)
        if x == "R4-llr":
            bl9 = fails(data, 9, x).mean()
            p(f"    R4-llr BLER@16 per SNR: {[round(fails(data, s, x).mean(), 4) for s in SNRS]} -> in [0.005, 0.9]: {[s for s in SNRS if 0.005 <= fails(data, s, x).mean() <= 0.9]}")
            chk("R4-llr +9 dB BLER (3 dp) out of range", round(bl9, 3), EXP_R4LLR_BLER9); chk("R4-llr in-range SNRs == {12, 15}", [s for s in SNRS if 0.005 <= fails(data, s, x).mean() <= 0.9], [12, 15])
        rows.append((x, int(fx.sum()), lab, r1))
    k = sum(1 for x in labs if labs[x] == "(i)"); mm = sum(1 for x in labs if labs[x] == "(ii)")
    kB, mB = k - (labs[BS] == "(i)"), mm - (labs[BS] == "(ii)")
    p(f"  SUMMARY-B (15): (i) {kB}, (ii) {mB}, not decided {15 - kB - mB}; b* -> V1 {labs[BS]};  16: (i) {k}, (ii) {mm}, not decided {16 - k - mm}")
    chk("SUMMARY-B (i)/(ii)/nd", (kB, mB, 15 - kB - mB), (EXP_SUMMARY["iB"], EXP_SUMMARY["iiB"], EXP_SUMMARY["ndB"]))
    chk("SUMMARY 16 (i)/(ii)/nd", (k, mm, 16 - k - mm), (EXP_SUMMARY["i16"], EXP_SUMMARY["ii16"], EXP_SUMMARY["nd16"]))
    chk("non-(i) arms", sorted(x for x in labs if labs[x] != "(i)"), ["R4-llr", "V1-pilot"])
    xs = min(rows, key=lambda r: (r[1], r[0]))
    fx, fv, fg = (fails(data, -3, a) for a in (xs[0], V1, GEN))
    ok_range = 0.005 <= fx.mean() <= 0.9 and fx.sum() > fg.sum() and not vg
    p(f"  X* = {xs[0]} (F = {xs[1]}); R_X* -3 dB defined? {ok_range}")
    chk("X*", (xs[0], xs[1]), (EXP_SUMMARY["xstar"], EXP_SUMMARY["xstar_F"]))
    cond = k == 16 and mm == 0 and ok_range
    chk("'멀어진다' condition met", cond, EXP_SUMMARY["cond"])
    chk("'전부' sentence condition (b* (i) and all 15 (i))", labs[BS] == "(i)" and kB == 15, False)
    chk("number of X with R_X(-3) undefined", sum(1 for r in rows if r[3][0] == "undef"), EXP_SUMMARY["n_undef"])

    # ------------------------------------------------------------------ 3. report-only pairs (§6.5)
    p("\n## 3. report-only pairs of §6.5 (pair_cross / pair_ald format; anchor = first member)")
    for (x, y), (eab, epool, elab, ek) in EXP_REPORT.items():
        cand, res, powered, wy, wx, lab = table_b(data, x, y)
        A, Bn = sum(r[0] for r in res), sum(r[1] for r in res)
        p(f"  {x} -> {y}  dp {cand}  " + "  ".join(f"{s:+d} {a}:{b} p={q:.2g}" for s, (a, b, q) in zip(cand, res))
          + f"  pooled {A}:{Bn} p={sign_p(A, Bn):.2g}  {'POWERED' if powered else 'UNDECIDED'} second {wy}/3 first {wx}/3 -> {lab}")
        chk(f"{x}->{y} dp", cand, [9, 12, 15]); chk(f"{x}->{y} a:b", [(a, b) for a, b, _ in res], eab); chk(f"{x}->{y} label", lab, elab)
        if epool:
            chk(f"{x}->{y} pooled", (A, Bn), epool)
        if ek:
            chk(f"{x}->{y} (second fewer, first fewer)", (wy, wx), ek)

    # ------------------------------------------------------------------ 4. predictions (§6.6 item 11) and the §6.2 'pilot_C' row
    p("\n## 4. §3 prediction 11 sentences")
    f = lambda a, s: int(fails(data, s, a).sum())
    chk("pred 11a: (ii) 0 and (i) >= 13 among the 15", mB == 0 and kB >= 13, True)
    chk("pred 11b: V1-pilot not (i)", labs["V1-pilot"] != "(i)", True)
    chk("pred 11c: A3 ALDv-pilot -> V1-pilot (i)", table_b(data, "ALDv-pilot", "V1-pilot")[5], "(i)")
    chk("pred 11d: OMP-pilot < R0-pilot@1 at -3 and 0 dB", (f("OMP-pilot", -3) < f(R0A, -3), f("OMP-pilot", 0) < f(R0A, 0)), (True, True))
    chk("pred 11d: SBL-pilot < R0-pilot@1 at -3 and 0 dB", (f("SBL-pilot", -3) < f(R0A, -3), f("SBL-pilot", 0) < f(R0A, 0)), (True, True))
    p(f"  counts: OMP {f('OMP-pilot', -3)}/{f('OMP-pilot', 0)}, SBL-pilot {f('SBL-pilot', -3)}/{f('SBL-pilot', 0)}, R0@1 {f(R0A, -3)}/{f(R0A, 0)}")

    # ------------------------------------------------------------------ 5. figure records
    p("\n## 5. figure records: paper_f21srt.txt counts (11 x 7) and paper_f33cdf_SRT.txt medians / 90th pct (10 x 4)")
    t = open(FIG21).read()
    nrec = 0
    for arm in FIG_SHOW:
        m = re.search(rf"^\s+{re.escape(arm)}\s+((?:\d+/2560\s+){{7}})(\S+)", t, re.M)
        vals = [int(v.split("/")[0]) for v in m.group(1).split()]
        chk(f"F21srt record {arm} counts == raw", vals, [int(fails(data, s, arm).sum()) for s in SNRS]); nrec += 1
        chk(f"F21srt record {arm} source raw", m.group(2), {"ALD-pilot": "raw_ALDSRT", "SBL-loop": "raw_SPSRT", "SBL-pilot": "raw_SPSRT", "OMP-pilot": "raw_SPSRT"}.get(arm, "raw_SRTB16e4"))
    chk("F21srt: drawn baselines (9) all (i)", all(labs[a] == "(i)" for a in FIG_SHOW if a not in (V1, GEN)), True)
    chk("F21srt: no drawn baseline at/below Proposed at any SNR (point estimates)",
        any(fails(data, s, a).sum() <= fails(data, s, V1).sum() for a in FIG_SHOW if a not in (V1, GEN) for s in SNRS), False)
    allb = np.concatenate([fails(data, s, a) for a in FIG_SHOW for s in SNRS]).mean()
    minb = min(fails(data, s, a).mean() for a in FIG_SHOW for s in SNRS)
    p(f"  min BLER among the 11 drawn curves = {minb:.4f} (y floor 0.3 from the ladder {{0.5, 0.3, 0.2, 0.1}}: largest value below every point and Wilson lower end)")
    from math import sqrt
    def wilson_lo(k_, n, z=1.96):
        pp = k_ / n; c = pp + z * z / (2 * n); h = z * sqrt(pp * (1 - pp) / n + z * z / (4 * n * n)); return (c - h) / (1 + z * z / n)
    wmin = min(wilson_lo(int(fails(data, s, a).sum()), N) for a in (V1, BS, "R2-ours-G", GEN) for s in SNRS)
    p(f"  min Wilson lower end among the 4 barred curves = {wmin:.4f}")
    chk("ladder floor 0.3 is the largest of {0.5,0.3,0.2,0.1} below min point and min Wilson end", max(v for v in (0.5, 0.3, 0.2, 0.1) if v < min(minb, wmin)), 0.3)
    t33 = open(FIG33).read()
    blocks = re.split(r"\n  SNR ", t33)[1:]
    for blk, s in zip(blocks, (-3, 9, 12, 15)):
        for arm in FIG_SHOW[:-1]:
            m = re.search(rf"^\s+{re.escape(arm)}\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(\d+)", blk, re.M)
            nm = np.asarray(data[s][arm]["nmse"])[:, -1]
            bad = int(np.sum(~np.isfinite(nm) | (nm <= 0)))
            db = 10 * np.log10(nm[np.isfinite(nm) & (nm > 0)])
            med, p90 = np.median(db), np.percentile(db, 90)
            chk(f"F33cdf {s:+d} dB {arm} median (2 dp)", round(float(med), 2), float(m.group(1)), 0.011)
            chk(f"F33cdf {s:+d} dB {arm} p90 (2 dp)", round(float(p90), 2), float(m.group(2)), 0.011)
            chk(f"F33cdf {s:+d} dB {arm} non-finite/non-positive", bad, int(m.group(3)))
            if arm in EXP_CDF_MED:
                chk(f"§6.4 median {arm} {s:+d} dB", round(float(med), 2), EXP_CDF_MED[arm][(-3, 9, 12, 15).index(s)], 0.011)
    # pairB's median NMSE table (report-only) -- recompute from raw, compare to the record file's lines
    tb = open(os.path.join(CONF, "results/review_next/pairB_SPSRT.txt")).read().split("report-only, median NMSE@16")[1]
    for arm in (V1, BS) + BL:
        m = re.search(rf"^\s+{re.escape(arm)}\s+((?:\S+\s*){{7}})$", tb, re.M)
        vals = [float(v) for v in m.group(1).split()]
        got = [float(f"{np.nanmedian(np.asarray(data[s][arm]['nmse'])[:, -1]):.2e}") for s in SNRS]
        chk(f"pairB median NMSE {arm}", got, vals)

    # ------------------------------------------------------------------ 6. sha256, pick / tune JSON vs §5 / §6.5
    p("\n## 6. sha256[:16] of the §5 / §6 files; pick and tune JSON vs §5 / §6.5; pick reproduced by sparse_tune.per_snr_pick")
    for f_, e in EXP_SHA.items():
        chk(f"sha {f_}", sha16(os.path.join(CONF, f_)), e)
    chk("pick rho", (pick["rho_sbl"], pick["rho_omp"], pick["edge_rho_sbl"], pick["edge_rho_omp"]), (EXP_PICK["rho_sbl"], EXP_PICK["rho_omp"], EXP_PICK["edge_rho_sbl"], EXP_PICK["edge_rho_omp"]))
    chk("pick scores (3 dp)", (round(pick["score_sbl_db"], 3), round(pick["score_omp_db"], 3)), (EXP_PICK["score_sbl"], EXP_PICK["score_omp"]))
    chk("pick n_em per SNR", {s: pick["per_snr"][str(s)]["n_em"] for s in SNRS}, EXP_PICK["n_em"])
    chk("pick L per SNR", {s: pick["per_snr"][str(s)]["L"] for s in SNRS}, EXP_PICK["L"])
    chk("pick per-SNR edge flags all False", any(pick["per_snr"][str(s)]["edge_sbl"] or pick["per_snr"][str(s)]["edge_omp"] for s in SNRS), False)
    sys.path.insert(0, os.path.join(CONF, "code"))
    import common as C  # noqa: E402
    import sparse_tune as S  # noqa: E402
    tune = json.load(open(os.path.join(CONF, "results/sparse/tune_SRT_C2.json")))
    c = C.CELLS["C2"]; r = S.per_snr_pick(tune["nmse_db"], c, c["Nr"] * c["Nt"], rhos=tune["grid"]["rho"])
    run = lambda q: (q["rho_sbl"], q["rho_omp"], {s: (e["n_em"], e["L"]) for s, e in q["per_snr"].items()})
    chk("pick reproduced by per_snr_pick from tune JSON", run(r) == run(pick), True)
    chk("tune JSON prior/cell/n/grid v2b", (tune["prior"], tune["cell"], tune["n"], tune["grid"] == dict(rho=[1, 2, 4, 8, 16], n_em=list(S.NEMS), L=list(S.LS))), ("SRT", "C2", 256, True))
    tj = json.load(open(os.path.join(CONF, "results/ald/tune_PILSRT.json")))
    chk("tune c, beta", (tj["c"], tj["beta"]), (EXP_TUNE["c"], EXP_TUNE["beta"]))
    chk("tune stop per SNR", [tj["stop"][f"{s:.1f}"] for s in SNRS], EXP_TUNE["stop"])
    chk("tune dev NMSE dB (2 dp)", [round(tj["dev_nmse_db"][f"{s:.1f}"], 2) for s in SNRS], EXP_TUNE["dev"])
    best_key = min(tj["grid"], key=tj["grid"].get)                      # NMSE in dB: lower is better
    def_best = min(v for k_, v in tj["grid"].items() if k_.endswith("beta=0.005"))
    chk("tune dev optimum (key, 3 dp)", (best_key, round(tj["grid"][best_key], 3)), EXP_TUNE["opt"])
    chk("tune default-beta best (3 dp)", round(def_best, 3), EXP_TUNE["def_"])
    chk("tune: default beta within 0.1 dB of optimum -> kept", def_best - tj["grid"][best_key] <= 0.1, True)
    chk("tune: best c at default beta is 0.01", min((k_ for k_ in tj["grid"] if k_.endswith("beta=0.005")), key=tj["grid"].get), "c=0.01,beta=0.005")
    chk("tune extended twice, no edge after extension", (len(tj["extended"]), tj["optimum_at_edge_after_extension"]), (EXP_TUNE["extended"], []))
    chk("tune n_dev / dev_skip / ckpt / ckpt_sha / git", (tj["n_dev"], tj["dev_skip"], tj["ckpt"], tj["ckpt_sha"], tj["git"]),
        (EXP_TUNE["n_dev"], EXP_TUNE["dev_skip"], EXP_TUNE["ckpt"], EXP_TUNE["ckpt_sha"], EXP_TUNE["git"]))
    chk("tune ald_py_sha == code/ald.py now", tj["ald_py_sha"], sha16(os.path.join(CONF, "code/ald.py")))
    p(f"  ALD estimate meta|ald_tune of raw_ALDSRT starts: {next(iter(raws['raw_ALDSRT'][1]['meta|ald_tune']))[:160]}")
    chk("raw_ALDSRT meta|ald_file sha == file", next(iter(raws["raw_ALDSRT"][1]["meta|ald_file"])).split("sha256[:16]=")[1], sha16(os.path.join(CONF, "results/ald/ald_PILSRT.npz")))

    p(f"\n## SUMMARY: {NCHECK[0]} values checked, {NCHECK[1]} differ from the record")
    return 0 if NCHECK[1] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
