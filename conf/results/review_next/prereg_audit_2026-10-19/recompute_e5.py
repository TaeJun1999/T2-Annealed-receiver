"""recompute_e5.py -- independent recomputation of NEXT_EXPERIMENTS_E5QAM16 §6 (test raw raw_U28QAM16 / raw_D2QAM16).

Reads the 448 npz chunks of each tag with numpy only (no import of conf/code).  Re-implements, from the frozen rules
(§1.4 / §2.1 and the definitions in Demo/exp_0921_analysis.py, Demo/exp_0925_analysis.py, code/recovery_ci.py read for
this audit): failures@16, BLER, decision points (anchor arm, |log10(BLER/0.1)| smallest, BLER in [0.005, 0.9]),
paired sign test (a:b, exact two-sided p), power guard (3 points, >= 6 discordant at >= 2), 2/3 rule, §2.1 label,
SNR@0.1 (first downward crossing, log-linear) and the 90 % paired bootstrap of the gap (B 2000, seed 20260925, same
draw order as gain()), sum F / R and its paired bootstrap (B 2000, seed 20260926, one index draw shared by the decision
SNRs, as recovery_ci.boot), plus an independent-seed bootstrap as a sanity check; the §6.4 trajectory numbers
(failures at iterations 1/2/4/8/16, median NMSE, monotonicity, iteration-1 identity V1 == V1-pilot, success@1 -> fail@16
transitions).  Every recomputed value is compared with the value transcribed in §6 / compare_*.txt / traj_*.out.

    CUDA_VISIBLE_DEVICES= nice -n 10 taskset -c 10-13 python -B recompute_e5.py > recompute_e5.out
"""
import glob
import math
import os
import re
import sys
from collections import defaultdict

import numpy as np

CONF = "/home/HTJ/t2/conf"
QAM = os.path.join(CONF, "results/review_next/qam16")
V1, BS, R2, G, VP = "M-ours-dscore-C-V1", "M-ours-bstar", "R2-ours-G", "R5-genie", "V1-pilot"
ARMS5 = (V1, BS, R2, G, VP)
KEYS_RAW = ("blk_err", "ber", "nmse", "tauL_gmean", "alphaD", "tauL_clip_frac", "alphaD_clip")
PAT = re.compile(r"^D2_(C\d)_(\w+?)_Nr(\d+)_T(\d+)_Tp(\d+)_(dft|eig)_snr(-?\d+)_skip(\d+)_n(\d+)\.npz$")
MIN_DISC = 6
GRID = [3, 6, 9, 12, 15, 18, 21]

# ------------------------------------------------------------------ values transcribed from §6.2 (and compare_*.txt)
EXPECTED = {
    "U28QAM16": dict(
        prior="UMi28", pilot="eig", git="13f05fb1", kron_K=4096, ll_val=5.797910431000217, worker_gb=1.5,
        ckpt_id="sha256[:16]=6f3a1b9490864af1 epoch=379 best_epoch=379 role=best 8x4",
        ckpt="/home/HTJ/t2/conf/ckpt/d2sx_UMi28_N160000_a1_best.pt",
        fails={3: (1549, 1560, 1669, 1054, 1755), 6: (1022, 1060, 1168, 704, 1107), 9: (718, 753, 868, 428, 761),
               12: (461, 516, 611, 246, 501), 15: (277, 306, 384, 136, 293), 18: (1844, 182, 243, 56, 171),
               21: (2543, 107, 142, 29, 91)},
        pairs={
            (R2, BS, R2): dict(dp=[15, 18, 21], ab=[(93, 15), (74, 13), (47, 12)], p=["6.4e-15", "1.6e-11", "5.1e-06"],
                               pooled=(214, 40), pp="6.3e-30", wy=3, wx=0, gap="+1.63 dB  [90% paired bootstrap +1.22, +2.19; censored replicates 0%]"),
            (BS, G, G): dict(dp=[9, 12, 15], ab=[(332, 7), (270, 0), (174, 4)], p=["1.7e-88", "1.1e-81", "2.2e-46"],
                             pooled=(776, 11), pp="4.2e-213", wy=3, wx=0, gap="+4.25 dB  [90% paired bootstrap +3.63, +4.87; censored replicates 0%]"),
            (R2, V1, R2): dict(dp=[15, 18, 21], ab=[(122, 15), (6, 1607), (0, 2401)], p=["5.1e-22", "0", "0"],
                               pooled=(128, 4023), pp="0", wy=1, wx=2, gap="n/a (17.66 vs >  21) — extend the SNR grid"),
            (BS, V1, BS): dict(dp=[12, 15, 18], ab=[(72, 17), (49, 20), (4, 1666)], p=["3.2e-09", "0.00064", "0"],
                               pooled=(125, 1703), pp="0", wy=2, wx=1, gap="n/a (16.03 vs >  21) — extend the SNR grid"),
            (V1, G, G): dict(dp=[9, 12, 15], ab=[(294, 4), (217, 2), (146, 5)], p=["1.3e-81", "5.7e-62", "4.4e-37"],
                             pooled=(657, 11), pp="4.5e-178", wy=3, wx=0, gap=">= +9.22 dB (M-ours-dscore-C-V1 never reaches 0.1 on the grid)"),
            (BS, VP, BS): dict(dp=[12, 15, 18], ab=[(50, 35), (41, 28), (33, 22)], p=["0.13", "0.15", "0.18"],
                               pooled=(124, 85), pp="0.0084", wy=0, wx=0, gap="+0.28 dB  [90% paired bootstrap +0.06, +0.53; censored replicates 0%]"),
        },
        sumF=(1004, 2582, 438), R="-2.787986", Rci=("-3.027", "-2.572"), label="(i)",
        traj_first={18: (511, 542, 577, 310), 21: (361, 382, 393, 167)}, traj_v1_it2={18: 1951, 21: 2458},
        nmse={18: ("2.90e-03", "8.18e-02"), 21: ("1.54e-03", "4.33e+00")},
        codex_trans={18: (1347, 14), 21: (2183, 1)},
    ),
    "D2QAM16": dict(
        prior="S2", pilot="dft", git="13f05fb1", kron_K=1024, ll_val=-11.459169831224418, worker_gb=1.0,
        ckpt_id="sha256[:16]=4443921ce8d5c4a1 epoch=1784 best_epoch=1764 role=legacy-last 8x4",
        ckpt="/home/HTJ/t2/conf/ckpt/d2sx_N160000_a1.pt",
        fails={3: (828, 1189, 1336, 546, 1000), 6: (470, 675, 831, 317, 503), 9: (286, 420, 522, 217, 307),
               12: (184, 288, 361, 140, 187), 15: (137, 214, 285, 108, 135), 18: (2485, 147, 202, 75, 97),
               21: (2557, 123, 166, 49, 72)},
        pairs={
            (R2, BS, R2): dict(dp=[12, 15, 18], ab=[(105, 32), (101, 30), (76, 21)], p=["2.9e-10", "3.5e-10", "1.7e-08"],
                               pooled=(282, 83), pp="1.8e-26", wy=3, wx=0, gap="+2.75 dB  [90% paired bootstrap +1.91, +3.68; censored replicates 0%]"),
            (BS, G, G): dict(dp=[6, 9, 12], ab=[(372, 14), (218, 15), (159, 11)], p=["1.9e-91", "2.4e-47", "8.8e-35"],
                             pooled=(749, 40), pp="2.2e-170", wy=3, wx=0, gap="+5.50 dB  [90% paired bootstrap +4.41, +6.46; censored replicates 0%]"),
            (R2, V1, R2): dict(dp=[12, 15, 18], ab=[(190, 13), (161, 13), (1, 2284)], p=["1.8e-41", "1.2e-33", "0"],
                               pooled=(352, 2310), pp="0", wy=2, wx=1, gap="+6.18 dB  [90% paired bootstrap +5.24, +7.03; censored replicates 0%]"),
            (BS, V1, BS): dict(dp=[9, 12, 15], ab=[(157, 23), (121, 17), (93, 16)], p=["1e-25", "1.6e-20", "2.2e-14"],
                               pooled=(371, 56), pp="4.4e-58", wy=3, wx=0, gap="+3.44 dB  [90% paired bootstrap +2.62, +4.33; censored replicates 0%]"),
            (V1, G, G): dict(dp=[6, 9, 12], ab=[(169, 16), (83, 14), (58, 14)], p=["2.1e-33", "4.2e-13", "1.6e-07"],
                             pooled=(310, 44), pp="2.1e-50", wy=3, wx=0, gap="+2.06 dB  [90% paired bootstrap +1.49, +2.57; censored replicates 0%]"),
            (BS, VP, BS): dict(dp=[9, 12, 15], ab=[(144, 31), (116, 15), (92, 13)], p=["1.3e-18", "1.6e-20", "8e-16"],
                               pooled=(352, 59), pp="6.8e-52", wy=3, wx=0, gap="+3.09 dB  [90% paired bootstrap +2.34, +3.87; censored replicates 0%]"),
        },
        sumF=(922, 607, 465), R="0.689278", Rci=("0.642", "0.736"), label="(none: D2 is report-only; table_B rule would say (i))",
        traj_first={18: (503, 619, 654, 459), 21: (460, 536, 575, 398)}, traj_v1_it2={18: 2060, 21: 2336},
        nmse={18: ("1.51e-03", "2.71e-01"), 21: ("8.16e-04", "4.59e+00")},
        codex_trans={18: (1985, 3), 21: (2098, 1)},
    ),
}

N_OK = N_BAD = 0
BAD = []


def check(name, got, want):
    global N_OK, N_BAD
    ok = got == want
    if ok:
        N_OK += 1
    else:
        N_BAD += 1
        BAD.append(f"{name}: got {got!r} want {want!r}")
    print(f"  [{'ok' if ok else 'MISMATCH'}] {name}: {got!r}" + ("" if ok else f"   (expected {want!r})"))
    return ok


# ------------------------------------------------------------------ statistics (own implementation)
def sign_p(a, b):
    n = a + b
    if n == 0:
        return 1.0
    s = sum(math.comb(n, i) for i in range(min(a, b) + 1))
    return min(1.0, 2 * s / 2 ** n)


def log10_sign_p(a, b):
    n = a + b
    s = sum(math.comb(n, i) for i in range(min(a, b) + 1))
    return math.log10(2) + math.log10(s) - n * math.log10(2)


def paired(ex, ey):
    a = int(np.sum((ex == 1) & (ey == 0)))
    b = int(np.sum((ex == 0) & (ey == 1)))
    return a, b, sign_p(a, b)


def decision_points(be16, snrs, ref):
    n = len(be16[(snrs[0], ref)])
    bl = {s: max(be16[(s, ref)].mean(), 0.5 / n) for s in snrs}
    cand = sorted((s for s in snrs if 0.005 <= bl[s] <= 0.9), key=lambda s: abs(np.log10(bl[s] / 0.1)))[:3]
    return sorted(cand)


def snr_at(snrs, bler, n, target=0.1):
    lb = np.log10(np.maximum(np.asarray(bler, float), 0.5 / n))
    lt = np.log10(target)
    if lb[0] <= lt:
        return snrs[0], "lo"
    for i in range(len(snrs) - 1):
        if lb[i] > lt >= lb[i + 1]:
            return snrs[i] + (lb[i] - lt) / (lb[i] - lb[i + 1]) * (snrs[i + 1] - snrs[i]), "ok"
    return snrs[-1], "hi"


def fmt_at(v, f):
    return {"ok": f"{v:6.2f}", "lo": f"<={v:4.0f}", "hi": f" >{v:4.0f}"}[f]


def gap_text(be16, snrs, x, y, B=2000, seed=20260925):
    ex = [be16[(s, x)] for s in snrs]
    ey = [be16[(s, y)] for s in snrs]
    n = min(len(e) for e in ex)
    (vx, fx), (vy, fy) = snr_at(snrs, [e.mean() for e in ex], n), snr_at(snrs, [e.mean() for e in ey], n)
    if fx == "hi" and fy == "ok":
        return f">= {vx - vy:+.2f} dB ({x} never reaches 0.1 on the grid)", (vx, fx, vy, fy), None
    if fx == "ok" and fy == "lo":
        return f">= {vx - vy:+.2f} dB ({y} is already below 0.1 at the lowest grid SNR)", (vx, fx, vy, fy), None
    if fx != "ok" or fy != "ok":
        return f"n/a ({fmt_at(vx, fx).strip()} vs {fmt_at(vy, fy).strip()}) — extend the SNR grid", (vx, fx, vy, fy), None
    rng = np.random.default_rng(seed)
    g = np.full(B, np.nan)
    for k in range(B):
        bx, by = [], []
        for a, b in zip(ex, ey):
            i = rng.integers(len(a), size=len(a))
            bx.append(a[i].mean()); by.append(b[i].mean())
        (ux, gx), (uy, gy) = snr_at(snrs, bx, n), snr_at(snrs, by, n)
        if gx == gy == "ok":
            g[k] = ux - uy
    cens = np.mean(~np.isfinite(g))
    lo, hi = np.nanpercentile(g, [5, 95])
    return f"{vx - vy:+.2f} dB  [90% paired bootstrap {lo:+.2f}, {hi:+.2f}; censored replicates {100 * cens:.0f}%]", (vx, fx, vy, fy), (lo, hi, cens)


def boot_R(cols, B=2000, seed=20260926):
    """cols = [(b, v, g) per decision SNR]; one index draw per replicate shared by the SNRs (recovery_ci.boot)."""
    rng = np.random.default_rng(seed)
    n = len(cols[0][0])
    out = np.empty(B)
    for i in range(B):
        idx = rng.integers(0, n, n)
        bs = sum(b[idx].sum() for b, _, _ in cols); vs = sum(v[idx].sum() for _, v, _ in cols); gs = sum(g[idx].sum() for _, _, g in cols)
        out[i] = (bs - vs) / (bs - gs) if bs - gs > 0 else np.nan
    ok = np.isfinite(out)
    return np.percentile(out[ok], [5, 95]), int((~ok).sum())


# ------------------------------------------------------------------ one tag
def audit_tag(tag):
    E = EXPECTED[tag]
    root = os.path.join(CONF, f"raw_{tag}")
    files = sorted(glob.glob(os.path.join(root, "D2_*.npz")))
    print(f"\n{'=' * 100}\n{tag}: {len(files)} chunk files in {root}")
    check(f"{tag} chunk count", len(files), 448)
    plan = defaultdict(list)
    vals = defaultdict(set)
    n_failed_keys = n_nonfinite = n_shape_bad = 0
    be_vals = set()
    per_snr = defaultdict(lambda: defaultdict(list))          # per_snr[snr][arm|key] -> list of arrays in skip order
    for f in files:
        m = PAT.match(os.path.basename(f))
        assert m, f
        cell, prior, snr, skip, n = m[1], m[2], int(m[7]), int(m[8]), int(m[9])
        plan[snr].append((skip, n))
        z = np.load(f)
        vals["cell"].add(cell); vals["prior"].add(prior); vals["pilot"].add(m[6]); vals["Nr"].add(m[3]); vals["T"].add(m[4]); vals["Tp"].add(m[5])
        for k in ("run|git", "meta|modulation", "meta|payload_bits", "meta|protocol", "meta|bstar", "run|iters", "run|seed",
                  "meta|ntrain", "meta|jobs", "meta|kron_K", "meta|ll_val|kron", "meta|worker_gb", "meta|stagec_ckpt_id",
                  "meta|stagec_ckpt", "run|dtype", "run|beta", "run|t_in", "run|n", "meta|em_sec"):
            vals[k].add(z[k].item() if z[k].ndim == 0 else str(z[k]))
        vals["run|skip==name"].add(int(z["run|skip"]) == skip)
        vals["run|snr==name"].add(float(z["run|snr"]) == float(snr))
        vals["arms(blk_err)"].add(tuple(sorted(k.split("|")[0] for k in z.files if k.endswith("|blk_err"))))
        n_failed_keys += sum(1 for k in z.files if k.endswith("|failed"))
        for a in ARMS5:
            for k in KEYS_RAW:
                arr = z[f"{a}|{k}"]
                if arr.shape != (40, 16):
                    n_shape_bad += 1
                if k == "blk_err":
                    n_nonfinite += int((~np.isfinite(arr)).sum())
                    be_vals |= set(np.unique(arr[np.isfinite(arr)]).tolist())
        for a in ARMS5:
            per_snr[snr][f"{a}|blk_err"].append((skip, z[f"{a}|blk_err"]))
            per_snr[snr][f"{a}|nmse"].append((skip, z[f"{a}|nmse"]))
    # chunk plan
    snrs = sorted(plan)
    check(f"{tag} SNR grid", snrs, GRID)
    plan_ok = all(sorted(plan[s]) == [(40 * k, 40) for k in range(64)] for s in snrs)
    check(f"{tag} chunk plan {{(40k, 40): k = 0..63}} x 7 (no holes / duplicates)", plan_ok, True)
    check(f"{tag} '<arm>|failed' keys (raised trials)", n_failed_keys, 0)
    check(f"{tag} non-finite blk_err entries (five arms)", n_nonfinite, 0)
    check(f"{tag} five arms x KEYS_RAW shape != (40, 16)", n_shape_bad, 0)
    check(f"{tag} blk_err value set", sorted(be_vals), [0.0, 1.0])
    check(f"{tag} run|git", vals["run|git"], {E["git"]})
    check(f"{tag} meta|modulation", vals["meta|modulation"], {"16qam"})
    check(f"{tag} meta|payload_bits", vals["meta|payload_bits"], {90})
    check(f"{tag} meta|protocol", vals["meta|protocol"], {"E5-qam16-v1"})
    check(f"{tag} meta|bstar", vals["meta|bstar"], {"kron"})
    check(f"{tag} run|iters", vals["run|iters"], {16})
    check(f"{tag} run|seed", vals["run|seed"], {20260926})
    check(f"{tag} meta|ntrain", vals["meta|ntrain"], {160000.0})
    check(f"{tag} meta|jobs", vals["meta|jobs"], {96})
    check(f"{tag} meta|kron_K", vals["meta|kron_K"], {E["kron_K"]})
    check(f"{tag} meta|ll_val|kron", vals["meta|ll_val|kron"], {E["ll_val"]})
    check(f"{tag} meta|worker_gb", vals["meta|worker_gb"], {E["worker_gb"]})
    check(f"{tag} meta|stagec_ckpt_id", vals["meta|stagec_ckpt_id"], {E["ckpt_id"]})
    check(f"{tag} meta|stagec_ckpt", vals["meta|stagec_ckpt"], {E["ckpt"]})
    check(f"{tag} run|n", vals["run|n"], {40})
    check(f"{tag} run|skip == file name", vals["run|skip==name"], {True})
    check(f"{tag} run|snr == file name", vals["run|snr==name"], {True})
    check(f"{tag} file-name prior / pilot / cell", (vals["prior"], vals["pilot"], vals["cell"]), ({E["prior"]}, {E["pilot"]}, {"C2"}))
    check(f"{tag} arm set (blk_err keys)", vals["arms(blk_err)"], {tuple(sorted(ARMS5))})
    print(f"  info: run|dtype {vals['run|dtype']}  run|beta {vals['run|beta']}  run|t_in {vals['run|t_in']}  meta|em_sec {vals['meta|em_sec']}  Nr/T/Tp {vals['Nr']}/{vals['T']}/{vals['Tp']}")

    # concatenate in skip order; failures @ every iteration (non-finite = failure)
    BE, NM = {}, {}
    for s in snrs:
        for a in ARMS5:
            parts = sorted(per_snr[s][f"{a}|blk_err"], key=lambda t: t[0])
            be = np.concatenate([p[1] for p in parts]).astype(float)
            be = np.where(np.isfinite(be), be, 1.0)
            BE[(s, a)] = be
            NM[(s, a)] = np.concatenate([p[1] for p in sorted(per_snr[s][f"{a}|nmse"], key=lambda t: t[0])])
            assert be.shape == (2560, 16), be.shape
    be16 = {k: v[:, -1] for k, v in BE.items()}

    print(f"\n  -- failures @16 / 2560 (V1, b*, R2, genie, V1-pilot)")
    for s in snrs:
        got = tuple(int(be16[(s, a)].sum()) for a in ARMS5)
        check(f"{tag} {s:+d} dB failures", got, E["fails"][s])
    v1min = min(be16[(s, V1)].mean() for s in snrs)
    print(f"  info: V1 min BLER@16 on the grid = {v1min:.4f} ({int(round(v1min * 2560))}/2560) -> {'never' if v1min > 0.1 else 'does'} reach 0.1")
    check(f"{tag} V1 never reaches BLER 0.1 on the grid", bool(v1min > 0.1), True if tag == "U28QAM16" else False)

    # table B pairs + report-only pair
    print(f"\n  -- paired comparisons (decision points anchored on the pair's baseline member)")
    for (x, y, anc), ex in E["pairs"].items():
        dp = decision_points(be16, snrs, anc)
        res = [paired(be16[(s, x)], be16[(s, y)]) for s in dp]
        A, Bsum = sum(r[0] for r in res), sum(r[1] for r in res)
        powered = len(dp) == 3 and sum(1 for a, b, _ in res if a + b >= MIN_DISC) >= 2
        wy = sum(1 for a, b, p in res if a > b and p < 0.05)
        wx = sum(1 for a, b, p in res if b > a and p < 0.05)
        name = f"{tag} {x} -> {y}"
        check(f"{name} decision SNRs", dp, ex["dp"])
        check(f"{name} a:b", [(a, b) for a, b, _ in res], ex["ab"])
        check(f"{name} p (%.2g)", [f"{p:.2g}" for _, _, p in res], ex["p"])
        check(f"{name} pooled a:b", (A, Bsum), ex["pooled"])
        check(f"{name} pooled p", f"{sign_p(A, Bsum):.2g}", ex["pp"])
        check(f"{name} POWERED", powered, True)
        check(f"{name} (second fewer, first fewer) at p<.05", (wy, wx), (ex["wy"], ex["wx"]))
        verdict = "significant" if max(wx, wy) >= 2 else "not significant"
        print(f"      verdict string: {verdict}; log10 p per point: " + ", ".join(f"{log10_sign_p(a, b):.1f}" for a, b, _ in res)
              + f"; pooled log10 p {log10_sign_p(A, Bsum):.1f}")
        txt, (vx, fx, vy, fy), ci = gap_text(be16, snrs, x, y)
        check(f"{name} SNR@0.1 gap text", txt, ex["gap"])
        print(f"      SNR@0.1: {x} {fmt_at(vx, fx).strip()} ({fx}), {y} {fmt_at(vy, fy).strip()} ({fy})")
        if ci is not None:
            txt2, _, ci2 = gap_text(be16, snrs, x, y, seed=1)
            print(f"      independent-seed (1) bootstrap of the same gap: [{ci2[0]:+.2f}, {ci2[1]:+.2f}] (registered seed gives [{ci[0]:+.2f}, {ci[1]:+.2f}])")
        if (x, y) == (BS, V1):
            label = ("(i)" if powered and wy >= 2 else "(ii)" if powered and wx >= 2 else "(iii)" if powered else "(iv)")
            print(f"      §2.1 label from the recomputed values: {label}  (POWERED={powered}, second-arm-fewer {wy}/3, first-arm-fewer {wx}/3)")
            if tag == "U28QAM16":
                check(f"{tag} §2.1 mechanical label", label, E["label"])
            else:
                print(f"      (D2: §2.2 gives no label; the rule's output would be {label})")

    # sum F and R at the b* -> V1 decision points
    dp = decision_points(be16, snrs, BS)
    cols = [(be16[(s, BS)], be16[(s, V1)], be16[(s, G)]) for s in dp]
    F = tuple(int(sum(c[i].sum() for c in cols)) for i in range(3))
    check(f"{tag} sum F (b*, V1, genie) at {dp}", F, E["sumF"])
    R = (F[0] - F[1]) / (F[0] - F[2])
    check(f"{tag} R", f"{R:.6f}", E["R"])
    (lo, hi), nn = boot_R(cols)
    check(f"{tag} R 90% paired bootstrap (seed 20260926)", (f"{lo:.3f}", f"{hi:.3f}"), E["Rci"])
    (lo2, hi2), nn2 = boot_R(cols, seed=1)
    print(f"      independent-seed (1) bootstrap of R: [{lo2:.3f}, {hi2:.3f}] ({nn2} undefined); registered-seed replicates undefined: {nn}")
    print(f"      per-point failures at the decision points: " + "; ".join(f"{s:+d} dB b* {int(be16[(s, BS)].sum())} V1 {int(be16[(s, V1)].sum())} genie {int(be16[(s, G)].sum())}" for s in dp))

    # ---- §6.4 trajectory (post hoc, report only)
    print(f"\n  -- trajectory (§6.4): failures at iterations 1/2/4/8/16, median NMSE @1/@16; compare with traj_{tag}.out")
    traj = {}
    with open(os.path.join(QAM, f"traj_{tag}.out")) as fh:
        for line in fh:
            m = re.match(r"\s*([+-]\d+) dB (\S+)\s+failures @1\s+(\d+) @2\s+(\d+) @4\s+(\d+) @8\s+(\d+) @16\s+(\d+) / (\d+)\s+raised (\d+)\s+median NMSE @1 (\S+) @16 (\S+)", line)
            if m:
                traj[(int(m[1]), m[2])] = (tuple(int(m[i]) for i in range(3, 8)), int(m[8]), int(m[9]), m[10], m[11])
    n_traj_ok = n_traj_bad = 0
    for s in snrs:
        for a in ARMS5:
            be = BE[(s, a)]
            got = tuple(int((be[:, i] != 0).sum()) for i in (0, 1, 3, 7, 15))
            nm = NM[(s, a)]
            with np.errstate(all="ignore"):
                import warnings
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    m1, m16 = np.nanmedian(nm[:, 0]), np.nanmedian(nm[:, 15])
            want = traj.get((s, a))
            ok = want is not None and want[0] == got and want[1] == 2560 and want[2] == 0 and want[3] == f"{m1:.2e}" and want[4] == f"{m16:.2e}"
            n_traj_ok += ok; n_traj_bad += (not ok)
            if not ok:
                print(f"    MISMATCH traj {s:+d} {a}: got {got} nmse {m1:.2e} {m16:.2e} vs file {want}")
    check(f"{tag} traj_{tag}.out lines reproduced (35 lines x failures@1/2/4/8/16, n, raised, NMSE@1/@16)", (n_traj_ok, n_traj_bad), (35, 0))
    for s in (18, 21):
        got = tuple(int((BE[(s, a)][:, 0] != 0).sum()) for a in (V1, BS, R2, G))
        check(f"{tag} {s:+d} dB failures @1 (V1, b*, R2, genie)", got, E["traj_first"][s])
        check(f"{tag} {s:+d} dB V1 failures @2", int((BE[(s, V1)][:, 1] != 0).sum()), E["traj_v1_it2"][s])
        with np.errstate(all="ignore"):
            nm = NM[(s, V1)]
            check(f"{tag} {s:+d} dB V1 median NMSE @1 -> @16", (f"{np.nanmedian(nm[:, 0]):.2e}", f"{np.nanmedian(nm[:, 15]):.2e}"), E["nmse"][s])
        # Codex transitions: V1 success @1 -> failure @16, and the reverse
        v = BE[(s, V1)]
        s2f = int(((v[:, 0] == 0) & (v[:, 15] != 0)).sum()); f2s = int(((v[:, 0] != 0) & (v[:, 15] == 0)).sum())
        check(f"{tag} {s:+d} dB V1 success@1 -> fail@16 (and reverse)", (s2f, f2s), E["codex_trans"][s])
        # "V1 is the fewest of the four non-genie arms at iteration 1" (V1 = V1-pilot at iteration 1)
        f1 = {a: int((BE[(s, a)][:, 0] != 0).sum()) for a in (V1, BS, R2, VP)}
        check(f"{tag} {s:+d} dB iteration-1 failures: V1 <= b*, R2 and V1 == V1-pilot", (f1[V1] <= min(f1[BS], f1[R2]), f1[V1] == f1[VP]), (True, True))
    # iteration-1 identity V1 == V1-pilot (blk_err and nmse) at every SNR
    ident = all(np.array_equal(BE[(s, V1)][:, 0], BE[(s, VP)][:, 0]) and np.array_equal(NM[(s, V1)][:, 0], NM[(s, VP)][:, 0], equal_nan=True) for s in snrs)
    check(f"{tag} iteration-1 blk_err and nmse of V1 == V1-pilot at all 7 SNRs", ident, True)
    # monotonicity over all 16 iterations
    def mono(a, s):
        f = [int((BE[(s, a)][:, i] != 0).sum()) for i in range(16)]
        return all(f[i + 1] <= f[i] for i in range(15)), f
    for a in (BS, VP):
        for s in (18, 21):
            ok, f = mono(a, s)
            check(f"{tag} {a} {s:+d} dB failures non-increasing over the 16 iterations", ok, True)
            print(f"      sequence: {f}")
    for s in snrs:
        ok, f = mono(V1, s)
        print(f"  info: V1 {s:+d} dB failures per iteration non-increasing over 16 = {ok}; at 1/2/4/8/16 = {[f[i] for i in (0, 1, 3, 7, 15)]}")
        if s <= 15:
            check(f"{tag} V1 {s:+d} dB failures decrease over iterations 1/2/4/8/16", all(f[j] < f[i] for i, j in ((0, 1), (1, 3), (3, 7), (7, 15))), True)
    for a in (R2, G):
        for s in (18, 21):
            ok, f = mono(a, s)
            print(f"  info: {a} {s:+d} dB non-increasing over 16 = {ok}; 1/2/4/8/16 = {[f[i] for i in (0, 1, 3, 7, 15)]}")
    return be16


def main():
    for tag in ("U28QAM16", "D2QAM16"):
        audit_tag(tag)
    print(f"\n{'=' * 100}\nSUMMARY: {N_OK} comparisons match, {N_BAD} mismatch")
    for b in BAD:
        print("  MISMATCH " + b)


if __name__ == "__main__":
    main()
