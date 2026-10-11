"""recompute_path_base.py -- independent recomputation for the RECORD AUDIT of NEXT_EXPERIMENTS_PATH16e4.md §6.3 / §6.4 / §6.5 / §6.6
(prior SRP).  Adapted from recompute_srt_base.py: raw_SRPB16e4 (base, 14 arms) + raw_PILSRP + raw_ALDSRP + raw_SPSRP are read DIRECTLY
with numpy (pair_baselines.py NOT imported; pairB_SPSRP.txt is read only for its median-NMSE table as the thing being checked) and the
22-row failure table, the 16 table-B rows X -> V1 (decision SNRs, exact sign tests, power guard, label, F_X - F_V1 at -3 dB, the
R_X -3 dB guard, R_X over the decision points with the registered paired bootstrap re-implemented), the summary counts, X*, the
"전부"/"멀어진다" conditions, the §6.5 report-only pairs, the test ALD NMSE, the §6.6 baseline predictions, the figure records
(paper_f21srp.txt counts + zero-failure list, paper_f33cdf_SRP.txt medians / p90) are recomputed.  Integrity: chunk plan, run|git per
raw, R5-genie bit identity of the three raws vs the base, meta|sparse == pick at every chunk, pick reproduced by sparse_tune.per_snr_pick
(the only project import), ALD estimate file vs tune_PILSRP.json and the base checkpoint sha, sha256[:16] of §5 / §6 files.

usage (cwd = ~/t2/conf):  CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=3 ~/miniforge3/envs/torch/bin/python -B \
    results/review_next/prereg_audit_2026-10-11/recompute_path_base.py > results/review_next/prereg_audit_2026-10-11/recompute_path_base.out
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

EXP_GIT = {"raw_SRPB16e4": "99039ef5", "raw_PILSRP": "9ad4caa0", "raw_ALDSRP": "9ad4caa0", "raw_SPSRP": "9ad4caa0"}
EXP_FAILS = {
    V1: [812, 204, 24, 4, 0, 0, 0], "ALD-pilot": [1315, 360, 64, 15, 1, 0, 0],
    BS: [1356, 498, 133, 29, 3, 2, 0], "R2-ours-G": [1491, 544, 139, 27, 1, 2, 0],
    "R1-turbo": [1792, 930, 283, 60, 6, 6, 0], "R3-bigamp": [2311, 1583, 763, 410, 298, 356, 332],
    R0A: [2351, 1755, 882, 313, 53, 30, 4], "SBL-loop": [1621, 623, 154, 32, 2, 0, 0],
    "SBL-pilot": [1857, 799, 224, 33, 2, 0, 0], "OMP-pilot": [2020, 940, 271, 81, 9, 3, 1],
    GEN: [428, 81, 7, 1, 0, 0, 0],
    "V1-pilot": [1113, 289, 48, 6, 0, 0, 0], "bstar-pilot": [1584, 688, 183, 35, 5, 2, 0],
    "ALDv-pilot": [1340, 345, 57, 12, 0, 0, 0], "M-ours-bstar-scalar": [1338, 482, 121, 26, 2, 2, 0],
    "M-ours-gmm32": [1467, 553, 125, 29, 3, 2, 0], "R4-scvamp": [1893, 1148, 511, 227, 59, 33, 14],
    "R4-llr": [2193, 1938, 1968, 1998, 1616, 1084, 539],
    "R0-pilot": [1767, 776, 215, 42, 6, 2, 0], "M-ours-dscore-C-V0": [2560, 2560, 2560, 2559, 2553, 2484, 1345],
    "M-ours-dscore-C-V4": [830, 203, 28, 5, 0, 0, 0], "M-ours-dscore-C-V4b": [843, 208, 28, 5, 0, 0, 0]}
# X: (decision SNRs, a:b per SNR, pooled a:b, pooled p as printed, (V1 fewer k, X fewer k), label, F_X-F_V1 @-3,
#     R_X -3 dB: ("undef", BLER 4 dp) or (R, lo, hi), R_X decision points: (R, lo, hi) or "undef")
EXP_B = {
    BS: ([-3, 0, 3], [(606, 62), (321, 27), (117, 8)], (1044, 97), "4.1e-201", (3, 0), "(i)", 544, (0.586, 0.554, 0.618), (0.644, 0.620, 0.667)),
    "M-ours-bstar-scalar": ([-3, 0, 3], [(590, 64), (311, 33), (104, 7)], (1005, 104), "1e-185", (3, 0), "(i)", 526, (0.578, 0.545, 0.609), (0.632, 0.608, 0.657)),
    "M-ours-gmm32": ([-3, 0, 3], [(706, 51), (382, 33), (108, 7)], (1196, 91), "2.2e-246", (3, 0), "(i)", 655, (0.630, 0.601, 0.659), (0.678, 0.657, 0.699)),
    R0A: ([3, 6, 9], [(858, 0), (309, 0), (53, 0)], (1220, 0), "0", (3, 0), "(i)", 1539, ("undef", 0.9184), (0.984, 0.977, 0.991)),
    "R1-turbo": ([0, 3, 6], [(740, 14), (265, 6), (57, 1)], (1062, 21), "1.7e-282", (3, 0), "(i)", 980, (0.718, 0.695, 0.741), (0.879, 0.861, 0.897)),
    "R2-ours-G": ([-3, 0, 3], [(726, 47), (376, 36), (123, 8)], (1225, 91), "3.3e-254", (3, 0), "(i)", 679, (0.639, 0.610, 0.666), (0.684, 0.662, 0.705)),
    "R3-bigamp": ([9, 12, 15], [(298, 0), (356, 0), (332, 0)], (986, 0), "3.1e-297", (3, 0), "(i)", 1499, ("undef", 0.9027), "undef"),
    "R4-llr": ([9, 12, 15], [(1616, 0), (1084, 0), (539, 0)], (3239, 0), "0", (3, 0), "(i)", 1381, (0.782, 0.764, 0.800), "undef"),
    "R4-scvamp": ([3, 6, 9], [(489, 2), (223, 0), (59, 0)], (771, 2), "1.2e-227", (3, 0), "(i)", 1081, (0.738, 0.717, 0.759), (0.975, 0.963, 0.986)),
    "bstar-pilot": ([-3, 0, 3], [(798, 26), (506, 22), (162, 3)], (1466, 51), "0", (3, 0), "(i)", 772, (0.668, 0.641, 0.693), (0.730, 0.711, 0.748)),
    "V1-pilot": ([-3, 0, 3], [(331, 30), (111, 26), (29, 5)], (471, 61), "1.7e-79", (3, 0), "(i)", 301, (0.439, 0.404, 0.476), (0.439, 0.408, 0.471)),
    "ALD-pilot": ([-3, 0, 3], [(555, 52), (177, 21), (44, 4)], (776, 77), "3.6e-146", (3, 0), "(i)", 503, (0.567, 0.535, 0.600), (0.572, 0.545, 0.599)),
    "ALDv-pilot": ([-3, 0, 3], [(571, 43), (170, 29), (38, 5)], (779, 77), "5.9e-147", (3, 0), "(i)", 528, (0.579, 0.547, 0.609), (0.573, 0.546, 0.600)),
    "SBL-loop": ([-3, 0, 3], [(843, 34), (443, 24), (136, 6)], (1422, 64), "0", (3, 0), "(i)", 809, (0.678, 0.652, 0.703), (0.722, 0.702, 0.740)),
    "SBL-pilot": ([-3, 0, 3], [(1065, 20), (609, 14), (204, 4)], (1878, 38), "0", (3, 0), "(i)", 1045, (0.731, 0.709, 0.753), (0.778, 0.762, 0.794)),
    "OMP-pilot": ([0, 3, 6], [(753, 17), (255, 8), (77, 0)], (1085, 25), "9.8e-284", (3, 0), "(i)", 1208, (0.759, 0.738, 0.778), (0.881, 0.863, 0.899))}
EXP_SUMMARY = dict(iB=15, iiB=0, ndB=0, i16=16, ii16=0, nd16=0, xstar="V1-pilot", xstar_F=1113, xstar_R=(0.439, 0.404, 0.476), cond=True, n_undef=2,
                   undef_names=["R0-pilot@1", "R3-bigamp"])
EXP_REPORT = {   # §6.5: (x, y): (a:b per SNR, pooled or None, label, (y fewer k, x fewer k) or None)
    ("bstar-pilot", "V1-pilot"): ([(513, 42), (439, 40), (147, 12)], (1099, 94), "(i)", None),
    ("bstar-pilot", BS): ([(284, 56), (252, 62), (74, 24)], (610, 142), "(i)", None),
    ("V1-pilot", BS): ([(131, 374), (65, 274), (18, 103)], (214, 751), "(ii)", (0, 3)),
    ("ALDv-pilot", V1): ([(571, 43), (170, 29), (38, 5)], None, "(i)", None),
    ("ALD-pilot", V1): ([(555, 52), (177, 21), (44, 4)], None, "(i)", None),
    ("ALDv-pilot", "V1-pilot"): ([(297, 70), (103, 47), (26, 17)], (426, 134), "(i)", (2, 0)),
    ("ALDv-pilot", BS): ([(239, 255), (93, 246), (26, 102)], (358, 603), "(ii)", (0, 2)),
    ("bstar-pilot", "ALDv-pilot"): ([(359, 115), (406, 63), (141, 15)], (906, 193), "(i)", None),
    ("ALD-pilot", "ALDv-pilot"): ([(37, 62), (36, 21), (15, 8)], (88, 91), "(iii)", (0, 1))}
EXP_ALD_NMSE_DB = [-7.26, -10.62, -13.79, -16.17, -18.83, -21.09, -23.32]
EXP_SHA = {"ckpt/d2sx_SRP_N160000_a1_best.pt": "ac4699c78b3e2d80", "ckpt/d2sx_SRP_N160000_a1.pt": "f82762a7002308db",
           "results/sparse/pick_SRP_C2.json": "6ae22a15de019833", "results/sparse/tune_SRP_C2.json": "fb47a9e1bb47ef9d",
           "results/ald/tune_PILSRP.json": "858087f53952bcbf", "results/ald/tune_PILSRP_curves.npz": "5c79f21bac01f91e",
           "results/ald/ald_PILSRP.npz": "ebb14a8952f0ae17"}
EXP_PICK = dict(rho_sbl=16, rho_omp=16, edge_rho_sbl=True, edge_rho_omp=True, score_sbl=-15.103, score_omp=-13.753,
                n_em={-3: 3, 0: 5, 3: 5, 6: 5, 9: 5, 12: 5, 15: 10}, L={-3: 2, 0: 3, 3: 4, 6: 6, 9: 6, 12: 8, 15: 32}, wall=8818.7, git="ce5fdacc")
EXP_TUNE = dict(c=0.01, beta=0.005, stop=[379, 474, 525, 575, 587, 600, 600], dev=[-7.09, -10.77, -13.66, -16.46, -18.79, -21.30, -23.40],
                opt=("c=0.01,beta=0.0001", -15.954), def_=-15.925, extended=2, n_dev=512, dev_skip=2560, ckpt_sha="ac4699c78b3e2d80",
                git="45c4ae07", ckpt="ckpt/d2sx_SRP_N160000_a1_best.pt")
EXP_CDF_MED3 = {V1: -14.16, BS: -9.67, "ALD-pilot": -8.90, "R2-ours-G": -8.16}      # §6.4 bullet, -3 dB medians
EXP_ZERO = {V1: [9, 12, 15], "ALD-pilot": [12, 15], BS: [15], "R2-ours-G": [15], "R1-turbo": [15], "SBL-loop": [12, 15], "SBL-pilot": [12, 15], GEN: [9, 12, 15]}
FIG21 = "/home/HTJ/t2/conference/figures/records/paper_f21srp.txt"
FIG33 = "/home/HTJ/t2/conference/figures/records/paper_f33cdf_SRP.txt"
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
        fs = glob.glob(os.path.join(root, f"D2_C2_SRP_Nr8_T16_Tp4_dft_snr{snr}_skip*_n*.npz"))
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
    p("# recompute_path_base.py -- independent recomputation (direct numpy read of the four raw sets), prior SRP")
    raws = {r: load_tag(os.path.join(CONF, r)) for r in EXP_GIT}
    base, pil, ald, sp = (raws[r][0] for r in ("raw_SRPB16e4", "raw_PILSRP", "raw_ALDSRP", "raw_SPSRP"))

    p("\n## 0. chunk plan / run|git / genie identity / raised trials / meta|sparse == pick / ALD estimate")
    for r, (pts, meta, prob, git, sparse) in raws.items():
        p(f"  {r}: problems = {prob if prob else 'none'};  run|git = {sorted(git)}")
        chk(f"{r} one clean run|git", (len(git) == 1, next(iter(git))), (True, EXP_GIT[r]))
    for r in ("raw_PILSRP", "raw_ALDSRP", "raw_SPSRP"):
        same = all(np.array_equal(base[s][GEN][q], raws[r][0][s][GEN][q], equal_nan=True) for s in SNRS for q in GENIE_KEYS if q in base[s][GEN])
        chk(f"R5-genie {r} == base (8 keys x 7 SNR x 2560, bit)", same, True)
    for r, arms in (("raw_PILSRP", ("V1-pilot", "bstar-pilot")), ("raw_ALDSRP", ("ALD-pilot", "ALDv-pilot")), ("raw_SPSRP", ("SBL-loop", "SBL-pilot", "OMP-pilot"))):
        chk(f"{r} no raised trial ('|failed' key) in {arms}", any("failed" in raws[r][0][s][a] for s in SNRS for a in arms), False)
    pick = json.load(open(os.path.join(CONF, "results/sparse/pick_SRP_C2.json")))
    for s in SNRS:
        want = dict(rho_sbl=pick["rho_sbl"], rho_omp=pick["rho_omp"], n_em=pick["per_snr"][str(s)]["n_em"], L=pick["per_snr"][str(s)]["L"])
        got = {json.dumps(json.loads(v), sort_keys=True) for v in raws["raw_SPSRP"][4][s]}
        chk(f"raw_SPSRP meta|sparse {s:+d} dB == pick (all 64 chunks)", got, {json.dumps(want, sort_keys=True)})
    for x, y in (("V1-pilot", V1), ("bstar-pilot", BS)):
        ok = all(np.array_equal(np.asarray(pil[s][x]["nmse"])[:, 0], np.asarray(base[s][y]["nmse"])[:, 0]) for s in SNRS)
        chk(f"{x}@1 nmse == {y}@1 nmse (7 SNR)", ok, True)
    est = np.load(os.path.join(CONF, "results/ald/ald_PILSRP.npz"), allow_pickle=True)
    pilz = np.load(os.path.join(CONF, "results/ald/pilots_PILSRP_test.npz"), allow_pickle=True)
    p(f"  ald_PILSRP.npz keys {est.files}; ckpt_sha {est['ckpt_sha'] if 'ckpt_sha' in est.files else '-'}")
    chk("ALD estimate ckpt_sha == base V1 ckpt", str(est["ckpt_sha"]) if "ckpt_sha" in est.files else "", "ac4699c78b3e2d80")
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

    data = {s: {**base[s], **{x: pil[s][x] for x in ("V1-pilot", "bstar-pilot")}, **{x: ald[s][x] for x in ("ALD-pilot", "ALDv-pilot")},
                **{x: sp[s][x] for x in ("SBL-loop", "SBL-pilot", "OMP-pilot")}} for s in SNRS}
    p("\n## 1. failures @16 per arm (R0-pilot@1 at iteration 1) -- §6.4 table, the 7 'other arms', V0/V4/V4b/R0@16")
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
        if e[8] == "undef":
            chk(f"{x} R_X dp undefined (genie >= V1 guard)", Rdp, "undef")
        else:
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

    p("\n## 3. report-only pairs of §6.5 (pair_cross / pair_ald format; anchor = first member)")
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

    p("\n## 4. §3 prediction 13 sentences")
    f = lambda a, s: int(fails(data, s, a).sum())
    chk("pred 13a: (ii) 0 and (i) >= 12 among the 15", mB == 0 and kB >= 12, True)
    chk("pred 13b: A3 ALDv-pilot -> V1-pilot (i)", table_b(data, "ALDv-pilot", "V1-pilot")[5], "(i)")
    chk("pred 13c: SBL-pilot < R0-pilot@1 at -3 dB", f("SBL-pilot", -3) < f(R0A, -3), True)
    p(f"  counts: SBL-pilot -3 dB {f('SBL-pilot', -3)}, R0@1 {f(R0A, -3)}")

    p("\n## 5. figure records: paper_f21srp.txt counts (11 x 7) + zero-failure list + 'at or below' line; paper_f33cdf_SRP.txt medians / p90 (10 x 4)")
    t = open(FIG21).read()
    for arm in FIG_SHOW:
        m = re.search(rf"^\s+{re.escape(arm)}\s+((?:\d+/2560\s+){{7}})(\S+)", t, re.M)
        vals = [int(v.split("/")[0]) for v in m.group(1).split()]
        chk(f"F21srp record {arm} counts == raw", vals, [int(fails(data, s, arm).sum()) for s in SNRS])
        chk(f"F21srp record {arm} source raw", m.group(2), {"ALD-pilot": "raw_ALDSRP", "SBL-loop": "raw_SPSRP", "SBL-pilot": "raw_SPSRP", "OMP-pilot": "raw_SPSRP"}.get(arm, "raw_SRPB16e4"))
    zero = {a: [s for s in SNRS if fails(data, s, a).sum() == 0] for a in FIG_SHOW}
    zero = {a: v for a, v in zero.items() if v}
    p(f"  zero-failure points from raw: {zero} (total {sum(len(v) for v in zero.values())})")
    chk("zero-failure points == §6.4 list (15)", zero, EXP_ZERO)
    zl = re.search(r"Zero-failure points.*?: (.*)$", t, re.M).group(1)
    zset = set(x.strip() for x in zl.split(";") if x.strip())
    want = {f"{FIG_NAME[a]} {s:+d} dB" for a, v in EXP_ZERO.items() for s in v}
    chk("figure record zero-failure list == §6.4 list", zset, want)
    at = re.search(r"at or below the proposed curve.*?pairB_SPSRP\.txt: (.*)$", t, re.M).group(1)
    pairs_ = re.findall(r"([+-]\d+) dB \((\d+) vs (\d+)\)", at)
    chk("'at or below' line: every item is 0 vs 0 at +12 / +15", all(a == b == "0" and s in ("+12", "+15") for s, a, b in pairs_) and len(pairs_) > 0, True)
    chk("F21srp: drawn baselines (9) all (i)", all(labs[a] == "(i)" for a in FIG_SHOW if a not in (V1, GEN)), True)
    minb = min(fails(data, s, a).mean() for a in FIG_SHOW for s in SNRS)
    chk("y range (3e-05, 1.2) rule: a zero-failure point exists", minb == 0.0, True)
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
                chk(f"§6.4 median {arm} -3 dB", round(float(med), 2), EXP_CDF_MED3[arm], 0.011)
    chk("F33 panels are -3 / 0 / +3 / +6 (decision SNRs + the grid SNR above)", "SNR -3 +0 +3 +6 dB" in t33, True)
    tb = open(os.path.join(CONF, "results/review_next/pairB_SPSRP.txt")).read().split("report-only, median NMSE@16")[1]
    for arm in (V1, BS) + BL:
        m = re.search(rf"^\s+{re.escape(arm)}\s+((?:\S+\s*){{7}})$", tb, re.M)
        vals = [float(v) for v in m.group(1).split()]
        got = [float(f"{np.nanmedian(np.asarray(data[s][arm]['nmse'])[:, -1]):.2e}") for s in SNRS]
        chk(f"pairB median NMSE {arm}", got, vals)

    p("\n## 6. sha256[:16] of the §5 / §6 files; pick and tune JSON vs §5 / §6.5; pick reproduced by sparse_tune.per_snr_pick")
    for f_, e in EXP_SHA.items():
        chk(f"sha {f_}", sha16(os.path.join(CONF, f_)), e)
    chk("pick rho / edge flags", (pick["rho_sbl"], pick["rho_omp"], pick["edge_rho_sbl"], pick["edge_rho_omp"]), (EXP_PICK["rho_sbl"], EXP_PICK["rho_omp"], EXP_PICK["edge_rho_sbl"], EXP_PICK["edge_rho_omp"]))
    chk("pick scores (3 dp)", (round(pick["score_sbl_db"], 3), round(pick["score_omp_db"], 3)), (EXP_PICK["score_sbl"], EXP_PICK["score_omp"]))
    chk("pick n_em per SNR", {s: pick["per_snr"][str(s)]["n_em"] for s in SNRS}, EXP_PICK["n_em"])
    chk("pick L per SNR", {s: pick["per_snr"][str(s)]["L"] for s in SNRS}, EXP_PICK["L"])
    chk("pick per-SNR edge flags all False ('끝값 없음')", any(pick["per_snr"][str(s)]["edge_sbl"] or pick["per_snr"][str(s)]["edge_omp"] for s in SNRS), False)
    p(f"  pick keys: {sorted(pick)}; git {pick.get('git')}; wall_sec {pick.get('wall_sec')}; prior {pick.get('prior')} cell {pick.get('cell')}")
    chk("pick git / wall_sec", (pick.get("git"), round(float(pick.get("wall_sec", 0)), 1)), (EXP_PICK["git"], EXP_PICK["wall"]))
    sys.path.insert(0, os.path.join(CONF, "code"))
    import common as C  # noqa: E402
    import sparse_tune as S  # noqa: E402
    tune = json.load(open(os.path.join(CONF, "results/sparse/tune_SRP_C2.json")))
    c = C.CELLS["C2"]; r = S.per_snr_pick(tune["nmse_db"], c, c["Nr"] * c["Nt"], rhos=tune["grid"]["rho"])
    run = lambda q: (q["rho_sbl"], q["rho_omp"], {s: (e["n_em"], e["L"]) for s, e in q["per_snr"].items()})
    chk("pick reproduced by per_snr_pick from tune JSON", run(r) == run(pick), True)
    chk("tune JSON prior/cell/n/grid", (tune["prior"], tune["cell"], tune["n"], tune["grid"] == dict(rho=[1, 2, 4, 8, 16], n_em=list(S.NEMS), L=list(S.LS))), ("SRP", "C2", 256, True))
    tj = json.load(open(os.path.join(CONF, "results/ald/tune_PILSRP.json")))
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
    chk("raw_ALDSRP meta|ald_file sha == file", next(iter(raws["raw_ALDSRP"][1]["meta|ald_file"])).split("sha256[:16]=")[1], sha16(os.path.join(CONF, "results/ald/ald_PILSRP.npz")))

    p(f"\n## SUMMARY: {NCHECK[0]} values checked, {NCHECK[1]} differ from the record")
    return 0 if NCHECK[1] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
