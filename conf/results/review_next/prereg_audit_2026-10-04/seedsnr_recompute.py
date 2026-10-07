#!/usr/bin/env python
"""prereg_audit_2026-10-04/seedsnr_recompute.py -- independent recomputation for the SEEDSNR16e4 §6.1 record audit.

Reads ONLY: raw npz (seed tags, chk tags, a1 raws, C2 raws), results files (tables/recovery/dR/accept/refarms/manifest),
logs/run_seedsnr16e4.log, logs/run_D2_<T>.log, results/scale/*_s5.txt, git.  Does NOT import analysis / recovery_ci /
frontier_ci / eval_accept; the registered definitions (§1 / SEEDS16e4 §1 / recovery_ci.py docstring / frontier_ci.py
docstring) are re-implemented here and the file values are compared.  CPU only, single process, GPUs hidden.
"""
import glob, json, os, re, subprocess, sys
from math import comb, sqrt
import numpy as np

os.environ["CUDA_VISIBLE_DEVICES"] = ""
CONF = "/home/HTJ/t2_wtS/conf"
RN = f"{CONF}/results/review_next"
os.chdir(CONF)
CHECKS = []  # (name, expected, got, ok)


def chk(name, exp, got, tol=None):
    ok = (abs(float(exp) - float(got)) <= tol) if tol is not None else (exp == got)
    CHECKS.append((name, exp, got, ok))
    print(("  OK   " if ok else "  MISMATCH ") + f"{name}: record={exp!r} recomputed={got!r}")
    return ok


PAT = re.compile(r"D2_(C\d+)_([A-Za-z0-9]+)_Nr(\d+)_T(\d+)_Tp(\d+)_(\w+)_snr(-?\d+(?:\.\d+)?)_skip(\d+)_n(\d+)\.npz")
ARMS11 = ["M-ours-dscore-C-V1", "M-ours-bstar", "M-ours-bstar-scalar", "M-ours-gmm32", "R0-pilot", "R1-turbo",
          "R2-ours-G", "R3-bigamp", "R4-llr", "R4-scvamp", "R5-genie"]
BS, V1, GEN = "M-ours-bstar", "M-ours-dscore-C-V1", "R5-genie"


def load(rawdir):
    """-> points[(cell, prior, snr)] = {arm: blk_err (n,16) concatenated in skip order}, meta dict of sets, nfiles, skips"""
    files = sorted(glob.glob(f"{rawdir}/D2_*.npz"))
    pts, meta = {}, {}
    for f in files:
        m = PAT.match(os.path.basename(f))
        key = (m[1], m[2], float(m[7]))
        pts.setdefault(key, []).append((int(m[8]), int(m[9]), f))
    out, skips = {}, {}
    for key, ch in sorted(pts.items()):
        ch.sort()
        skips[key] = [(s, n) for s, n, _ in ch]
        d = {}
        for s, n, f in ch:
            with np.load(f) as z:
                for k in z.files:
                    if k.startswith("meta|") or k.startswith("run|"):
                        v = z[k]; meta.setdefault(k, set()).add(str(v.item() if v.shape == () else v.tolist()))
                        continue
                    if "|" not in k:
                        continue
                    arm, q = k.split("|", 1)
                    if q in ("blk_err", "ber", "nmse"):
                        d.setdefault(arm, {}).setdefault(q, []).append(z[k])
        out[key] = {a: {q: np.concatenate(v) for q, v in dd.items()} for a, dd in d.items()}
    return out, meta, len(files), skips


def fails(pt, arm):
    v = np.asarray(pt[arm]["blk_err"])[:, -1]
    return np.where(np.isfinite(v), v, 1.0)


def sign_p(a, b):
    n = a + b
    return 1.0 if n == 0 else min(1.0, 2 * sum(comb(n, i) for i in range(min(a, b) + 1)) / 2 ** n)


def wilson(k, n, z=1.96):
    p = k / n; c = p + z * z / (2 * n); h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)); den = 1 + z * z / n
    return (c - h) / den, (c + h) / den


def boot_paired(cols, B=2000, seed=20260926):
    """recovery_ci.py definition: one index draw per replicate shared by the listed SNR columns (same n), three arms together."""
    rng = np.random.default_rng(seed); n = len(cols[0][0]); out = np.empty(B)
    for i in range(B):
        idx = rng.integers(0, n, n)
        bs = sum(b[idx].sum() for b, _, _ in cols); vs = sum(v[idx].sum() for _, v, _ in cols); gs = sum(g[idx].sum() for _, _, g in cols)
        out[i] = (bs - vs) / (bs - gs) if bs - gs > 0 else np.nan
    ok = np.isfinite(out)
    return np.percentile(out[ok], [5, 95]), int((~ok).sum())


def R(cols):
    b = sum(c[0].sum() for c in cols); v = sum(c[1].sum() for c in cols); g = sum(c[2].sum() for c in cols)
    return (b - v) / (b - g), (int(b), int(v), int(g))


def frontier(set1, set2, B=2000, seed=20260926, level=0.95):
    """frontier_ci.py --recovery definition: per replicate one index draw per (raw, point), paired within a point, the two raw
    sets independent; R1 - R2 unpaired; percentile CIs 90 % and `level`; p = min(1, 2 min(P[D<=0], P[D>=0]))."""
    rng = np.random.default_rng(seed)
    bo = np.full((B, 2), np.nan); ga = np.full((B, 2, 2), np.nan)
    for i in range(B):
        idx = {}
        for j, (raw, keys, cols) in enumerate((set1, set2)):
            rc = []
            for k, c in zip(keys, cols):
                kk = (raw, k)
                if kk not in idx:
                    idx[kk] = rng.integers(0, len(c[0]), len(c[0]))
                rc.append(tuple(x[idx[kk]] for x in c))
            bo[i, j], (b, v, g) = R(rc)
            ga[i, j] = v - g, b - g
    r1, r2 = R(set1[2])[0], R(set2[2])[0]
    ci = lambda v, q: np.percentile(v[np.isfinite(v)], q)
    d = bo[:, 0] - bo[:, 1]
    q = round(50 * (1 - level), 9)
    lo95, hi95 = ci(d, [q, 100 - q]); df = d[np.isfinite(d)]
    p = min(1.0, 2 * min(np.mean(df <= 0), np.mean(df >= 0)))
    return dict(R1=r1, R1ci=ci(bo[:, 0], [5, 95]), R2=r2, R2ci=ci(bo[:, 1], [5, 95]), d=r1 - r2, d90=ci(d, [5, 95]),
                dL=(lo95, hi95), p=p, und=int((~np.isfinite(d)).sum()),
                gaps1=(R(set1[2])[1], ci(ga[:, 0, 0], [5, 95]), ci(ga[:, 0, 1], [5, 95])),
                gaps2=(R(set2[2])[1], ci(ga[:, 1, 0], [5, 95]), ci(ga[:, 1, 1], [5, 95])))


# ------------------------------------------------------------------ registered constants (§0 / §1 / scale2_s5 / run script)
CELLS = {  # a1 tag: (cell, prior, Nr, decision SNRs, C2 raw spec, label cell name, a1 R_dp record, a1 CI record, a1 first-point V1 CI)
    "U28NR16B16e4": ("C6", "UMi28", 16, [0.0, 3.0, 6.0], ("raw_U28B16e4", "C2", [3.0, 6.0, 9.0]), "UMi28 C6", 0.287, (0.253, 0.322), (0.130, 0.157)),
    "U28NR32B16e4": ("C9", "UMi28", 32, [-3.0, 0.0, 3.0], ("raw_U28B16e4", "C2", [3.0, 6.0, 9.0]), "UMi28 C9", 0.432, (0.402, 0.462), (0.124, 0.150)),
    "NR32B16e4": ("C9", "S2", 32, [-9.0, -6.0, -3.0], ("raw_B16e4k", "C2", [-3.0, 0.0, 3.0]), "D2 C9", 0.811, (0.790, 0.832), (0.077, 0.099)),
}
# §6.1 record values to compare (transcribed from the appended §6.1 / EXPERIMENTS / DECISIONS)
REC = {
    "U28NR16B16e4s2": dict(ab=[(113, 33), (80, 13), (37, 8)], pooled=(230, 54), pp="5e-27", V1=[375, 190, 83], Rdp=0.269, ci=(0.231, 0.305), R6="0.269113",
                           Rpt=[(0.238, 0.184, 0.288), (0.306, 0.245, 0.366), (0.293, 0.194, 0.384)], w=(0.146, 0.133, 0.161), w4=(0.1333, 0.1607),
                           dR=(0.119, 0.064, 0.175), dR95=(0.053, 0.186), R1ci=(0.232, 0.305), gaps=(478, 443, 514, 654, 616, 696), git="d59b4c6c", jobs=None, cfg="d2e7f64a6e1fb841"),
    "U28NR16B16e4s3": dict(ab=[(115, 28), (81, 11), (42, 8)], pooled=(238, 47), pp="6.6e-32", V1=[368, 187, 78], Rdp=0.292, ci=(0.255, 0.328), R6="0.292049",
                           Rpt=[(0.259, 0.207, 0.307), (0.320, 0.256, 0.379), (0.343, 0.244, 0.438)], w=(0.144, 0.131, 0.158), w4=(0.1307, 0.1579),
                           dR=(0.142, 0.085, 0.197), dR95=(0.078, 0.207), R1ci=(0.256, 0.327), gaps=(463, 430, 499, 654, 616, 696), git="d59b4c6c", jobs=None, cfg="d2e7f64a6e1fb841"),
    "U28NR32B16e4s2": dict(ab=[(168, 15), (150, 13), (85, 7)], pooled=(403, 35), pp="2.1e-80", V1=[356, 167, 67], Rdp=0.443, ci=(0.412, 0.474), R6="0.442840",
                           Rpt=[(0.363, 0.321, 0.406), (0.500, 0.443, 0.555), (0.574, 0.500, 0.648)], w=(0.139, 0.126, 0.153), w4=(0.1262, 0.1530),
                           dR=(0.292, 0.243, 0.344), dR95=(0.233, 0.355), R1ci=(0.413, 0.474), gaps=(463, 430, 495, 831, 786, 871), git="d59b4c6c", jobs="99", cfg="be3c3e0d438468f4"),
    "U28NR32B16e4s3": dict(ab=[(169, 13), (143, 7), (86, 7)], pooled=(398, 27), pp="9.1e-86", V1=[353, 168, 66], Rdp=0.446, ci=(0.416, 0.476), R6="0.446450",
                           Rpt=[(0.371, 0.329, 0.413), (0.496, 0.444, 0.548), (0.581, 0.504, 0.655)], w=(0.138, 0.125, 0.152), w4=(0.1251, 0.1518),
                           dR=(0.296, 0.247, 0.347), dR95=(0.237, 0.358), R1ci=(0.417, 0.477), gaps=(460, 426, 492, 831, 786, 871), git="d59b4c6c", jobs="99", cfg="be3c3e0d438468f4"),
    "NR32B16e4s2": dict(ab=[(638, 13), (201, 5), (70, 4)], pooled=(909, 22), pp="1.6e-236", V1=[224, 35, 15], Rdp=0.813, ci=(0.790, 0.834), R6="0.813016",
                        Rpt=[(0.780, 0.754, 0.806), (0.920, 0.876, 0.961), (0.857, 0.780, 0.921)], w=(0.087, 0.077, 0.099), w4=(0.0772, 0.0991),
                        dR=(0.304, 0.264, 0.350), dR95=(0.256, 0.357), R1ci=(0.791, 0.835), gaps=(204, 179, 228, 1091, 1045, 1135), git="d59b4c6c", jobs="98", cfg="a501d45987ffbb39"),
    "NR32B16e4s3": dict(ab=[(637, 19), (190, 10), (72, 2)], pooled=(899, 31), pp="1.8e-222", V1=[231, 51, 11], Rdp=0.796, ci=(0.774, 0.816), R6="0.795600",
                        Rpt=[(0.772, 0.745, 0.798), (0.845, 0.796, 0.890), (0.909, 0.851, 0.961)], w=(0.090, 0.080, 0.102), w4=(0.0797, 0.1020),
                        dR=(0.287, 0.247, 0.332), dR95=(0.239, 0.341), R1ci=(0.774, 0.817), gaps=(223, 198, 248, 1091, 1045, 1135), git="b53a8529", jobs="98", cfg="3b35f7b7006763c7"),
}
A1REC = {"U28NR16B16e4": dict(bs=[455, 257, 112], g=[119, 38, 13], V1=[367, 187, 82], ab=[(114, 26), (81, 11), (37, 7)], pooled=(232, 44), R6="0.287462", gaps=(466, 654)),
         "U28NR32B16e4": dict(bs=[509, 304, 145], g=[88, 30, 9], V1=[349, 180, 70], ab=[(173, 13), (136, 12), (82, 7)], pooled=(391, 32), R6="0.432010", gaps=(472, 831)),
         "NR32B16e4": dict(bs=[849, 231, 81], g=[48, 18, 4], V1=[224, 42, 10], ab=[(641, 16), (198, 9), (75, 4)], pooled=(914, 29), R6="0.811182", gaps=(206, 1091))}
C2REC = {"raw_U28B16e4": dict(R=0.150, ci=(0.108, 0.190), cnt=(800, 712, 215), gaps=(497, 461, 532, 585, 547, 623)),
         "raw_B16e4k": dict(R=0.509, ci=(0.470, 0.544), cnt=(864, 488, 125), gaps=(363, 332, 396, 739, 697, 781))}

print("=" * 100); print("§1 raw meta / run keys (independent read)")
raws = {}
for T in list(CELLS) + list(REC) + ["U28NR16B16e4chkS", "U28NR16B16e4chkS2"]:
    pts, meta, nf, skips = load(f"raw_{T}")
    raws[T] = (pts, meta, nf, skips)
    g = meta.get("run|git"); jb = meta.get("meta|jobs"); wg = meta.get("meta|worker_gb")
    print(f"raw_{T}: files {nf}  run|git {sorted(g)}  ntrain {sorted(meta['meta|ntrain'])} bstar {sorted(meta['meta|bstar'])} kron_K {sorted(meta['meta|kron_K'])} "
          f"ll_val|kron {sorted(meta['meta|ll_val|kron'])} em_sec {sorted(meta['meta|em_sec'])} jobs {sorted(jb) if jb else None} worker_gb {sorted(wg) if wg else None} "
          f"n {sorted(meta['run|n'])} iters {sorted(meta['run|iters'])} seed {sorted(meta['run|seed'])}")
    print(f"   ckpt_id {sorted(meta['meta|stagec_ckpt_id'])}")
    for key, sk in skips.items():
        exp = [(40 * k, 40) for k in range(64)] if nf >= 192 else [(0, 40)]
        if sk != exp or (nf == 448 and len(sk) != 64):
            if not (nf == 448 and sk == exp):
                print(f"   NOTE chunk plan {key}: {sk[:3]}... ({len(sk)} chunks)")
    if T in REC:
        chk(f"{T} run|git", {REC[T]["git"]}, set(g))
        chk(f"{T} n files", 192, nf)
        chk(f"{T} meta|jobs", REC[T]["jobs"], (sorted(jb)[0] if jb else None))
    elif T.startswith("U28NR16B16e4chk"):
        chk(f"{T} run|git", {"d59b4c6c" if T.endswith("chkS") else "b53a8529"}, set(g)); chk(f"{T} n files", 1, nf)
    else:
        chk(f"{T} (a1) run|git", {"b4433d3c"}, set(g)); chk(f"{T} (a1) n files", 448, nf)

print("=" * 100); print("§2 decision points, failures, table B, R_dp (per seed; a1 bit identity of non-V1 arms)")
RES = {}
for A, (cell, prior, nr, DP, c2, cname, a1R, a1ci, a1w) in CELLS.items():
    a1pts = raws[A][0]
    # anchor rule on the 3-point subset of the a1 raw and of each seed raw
    for T in [A, A + "s2", A + "s3"]:
        pts = raws[T][0]
        keys = [(cell, prior, s) for s in DP]
        bl = {s: max(fails(pts[(cell, prior, s)], BS).mean(), 0.5 / 2560) for s in DP}
        cand = sorted(sorted((s for s in DP if 0.005 <= bl[s] <= 0.9), key=lambda s: abs(np.log10(bl[s] / 0.1)))[:3])
        chk(f"{T} anchor-b* decision SNRs (3-pt subset)", DP, cand)
        cols = [(fails(pts[k], BS), fails(pts[k], V1), fails(pts[k], GEN)) for k in keys]
        bsum = [int(c[0].sum()) for c in cols]; vsum = [int(c[1].sum()) for c in cols]; gsum = [int(c[2].sum()) for c in cols]
        ab = []
        for c in cols:
            a = int(np.sum((c[0] == 1) & (c[1] == 0))); b = int(np.sum((c[0] == 0) & (c[1] == 1))); ab.append((a, b, sign_p(a, b)))
        A_, B_ = sum(x[0] for x in ab), sum(x[1] for x in ab)
        powered = len(cand) == 3 and sum(1 for a, b, _ in ab if a + b >= 6) >= 2
        wy = sum(1 for a, b, p in ab if a > b and p < 0.05); wx = sum(1 for a, b, p in ab if b > a and p < 0.05)
        label = "(iv)" if not powered else ("(i)" if wy >= 2 else "(ii)" if wx >= 2 else "(iii)")
        r, cnt = R(cols); (lo, hi), und = boot_paired(cols)
        perpt = []
        for c in cols:
            rr, _ = R([c]); (l, h), _ = boot_paired([c]); perpt.append((rr, l, h))
        RES[T] = dict(bs=bsum, v=vsum, g=gsum, ab=ab, pooled=(A_, B_), pp=sign_p(A_, B_), label=label, R=r, ci=(lo, hi), cnt=cnt, perpt=perpt, cols=cols, keys=keys)
        print(f"{T}: b* {bsum} V1 {vsum} genie {gsum}  a:b {[(a, b, f'{p:.2g}') for a, b, p in ab]} pooled {A_}:{B_} p={sign_p(A_, B_):.2g}  POWERED={powered} "
              f"second-fewer {wy}/3 first-fewer {wx}/3 -> {label}  R_dp={r:.6f} [90% {lo:.3f}, {hi:.3f}] und {und}  SigmaF {cnt}")
        rec = REC.get(T) or A1REC.get(T)
        if T in REC:
            chk(f"{T} a:b per point", rec["ab"], [(a, b) for a, b, _ in ab]); chk(f"{T} pooled a:b", rec["pooled"], (A_, B_))
            chk(f"{T} pooled p (2 sig)", rec["pp"], f"{sign_p(A_, B_):.2g}")
            chk(f"{T} V1 failures", rec["V1"], vsum); chk(f"{T} b* failures = a1", A1REC[A]["bs"], bsum); chk(f"{T} genie failures = a1", A1REC[A]["g"], gsum)
            chk(f"{T} table B label", "(i)", label)
            chk(f"{T} R_dp 3 dp", f"{rec['Rdp']:.3f}", f"{r:.3f}"); chk(f"{T} R_dp 6 dp", rec["R6"], f"{r:.6f}")
            chk(f"{T} R_dp 90% CI", rec["ci"], (round(float(lo), 3), round(float(hi), 3)))
            chk(f"{T} per-point R [CI]", rec["Rpt"], [(round(float(x), 3), round(float(l), 3), round(float(h), 3)) for x, l, h in perpt])
            w = wilson(vsum[0], 2560)
            chk(f"{T} first-point V1 BLER (3 dp) + Wilson", rec["w"], (round(vsum[0] / 2560, 3), round(w[0], 3), round(w[1], 3)))
            chk(f"{T} Wilson 4 dp", rec["w4"], (round(w[0], 4), round(w[1], 4)))
            # non-V1 arm bit identity vs a1 raw (blk_err, ber, nmse; all iterations) -- the --ref-arms all gate, independently
            diff = []
            for k in keys:
                for arm in ARMS11:
                    for q in ("blk_err", "ber", "nmse"):
                        x, y = pts[k][arm][q], a1pts[k][arm][q]
                        same = x.shape == y.shape and np.array_equal(x, y, equal_nan=True)
                        if not same:
                            diff.append(arm)
            chk(f"{T} arms differing from a1 raw (blk_err/ber/nmse, 3 points)", ["M-ours-dscore-C-V1"], sorted(set(diff)))
        else:
            chk(f"{T} (a1) a:b per point", rec["ab"], [(a, b) for a, b, _ in ab]); chk(f"{T} (a1) pooled", rec["pooled"], (A_, B_))
            chk(f"{T} (a1) V1 failures", rec["V1"], vsum); chk(f"{T} (a1) label", "(i)", label)
            chk(f"{T} (a1) R_dp 3 dp", f"{a1R:.3f}", f"{r:.3f}"); chk(f"{T} (a1) R_dp 6 dp", rec["R6"], f"{r:.6f}")
            chk(f"{T} (a1) R_dp CI", a1ci, (round(float(lo), 3), round(float(hi), 3)))
            w = wilson(vsum[0], 2560); chk(f"{T} (a1) first-point Wilson", a1w, (round(w[0], 3), round(w[1], 3)))
    # chk tags: 11 arms bit-identical to the a1 raw at -3 dB chunk 0 (UMi28 C6 only)
    if A == "U28NR16B16e4":
        k = (cell, prior, -3.0)
        with np.load(sorted(glob.glob("raw_U28NR16B16e4/D2_*snr-3_skip0_n40.npz"))[0]) as z0:
            for C in ("U28NR16B16e4chkS", "U28NR16B16e4chkS2"):
                with np.load(sorted(glob.glob(f"raw_{C}/D2_*.npz"))[0]) as zc:
                    ks = [x for x in z0.files if "|" in x and not x.startswith(("meta|", "run|"))]
                    bad = [x for x in ks if x not in zc.files or not (z0[x].shape == zc[x].shape and np.array_equal(z0[x], zc[x], equal_nan=True))]
                    chk(f"{C} all arm keys bit-identical to a1 chunk 0 ({len(ks)} keys)", [], bad)

print("=" * 100); print("§3 seed robustness labels (§1 rule: denominator 3 = a1·a2·a3), spreads, predictions")
LAB = {}
for A, (cell, prior, nr, DP, c2, cname, a1R, a1ci, a1w) in CELLS.items():
    labs = [RES[A]["label"], RES[A + "s2"]["label"], RES[A + "s3"]["label"]]
    k = labs.count("(i)"); m = sum(1 for x in labs if x in ("(ii)", "(iii)")); j = 3 - k - m
    ladder = "; a3 = §3d fb2" if A == "NR32B16e4" else ""
    if k == 3:
        lab = f"시드 강건 (3/3 (i){ladder})"
    elif m:
        lab = f"시드 의존 ({k}/3 (i), {m} 다름{ladder})"
    else:
        lab = f"판정하지 못함 ({k}/3 (i), {j} 판정 못함{ladder})"
    # precedent rule (no ladder): D2 C9 a3 = training failure -> 판정 못함
    plabs = labs if A != "NR32B16e4" else labs[:2] + ["학습 실패"]
    pk = plabs.count("(i)"); pm = sum(1 for x in plabs if x in ("(ii)", "(iii)")); pj = 3 - pk - pm
    plab = f"시드 강건 (3/3 (i))" if pk == 3 else (f"시드 의존 ({pk}/3 (i), {pm} 다름)" if pm else f"판정하지 못함 ({pk}/3 (i), {pj} 판정 못함)")
    Rs = [RES[A]["R"], RES[A + "s2"]["R"], RES[A + "s3"]["R"]]; Vs = [RES[A]["cnt"][1], RES[A + "s2"]["cnt"][1], RES[A + "s3"]["cnt"][1]]
    LAB[A] = dict(lab=lab, plab=plab, spreadR=max(Rs) - min(Rs), spreadV=max(Vs) - min(Vs), labs=labs)
    print(f"{cname}: per-seed {labs} -> registered label {lab!r}; precedent-rule label {plab!r}; R_dp spread {max(Rs) - min(Rs):.6f}; SigmaF_V1 {Vs} spread {max(Vs) - min(Vs)}")
chk("label UMi28 C6", "시드 강건 (3/3 (i))", LAB["U28NR16B16e4"]["lab"]); chk("label UMi28 C9", "시드 강건 (3/3 (i))", LAB["U28NR32B16e4"]["lab"])
chk("label D2 C9 (registered, ladder qualifier)", "시드 강건 (3/3 (i); a3 = §3d fb2)", LAB["NR32B16e4"]["lab"])
chk("label D2 C9 (precedent rule, report-only)", "판정하지 못함 (2/3 (i), 1 판정 못함)", LAB["NR32B16e4"]["plab"])
chk("precedent label UMi28 C6 = same", "시드 강건 (3/3 (i))", LAB["U28NR16B16e4"]["plab"]); chk("precedent label UMi28 C9 = same", "시드 강건 (3/3 (i))", LAB["U28NR32B16e4"]["plab"])
chk("R_dp spread UMi28 C6 (3 dp)", 0.023, round(LAB["U28NR16B16e4"]["spreadR"], 3)); chk("R_dp spread UMi28 C6 (6 dp)", "0.022936", f"{LAB['U28NR16B16e4']['spreadR']:.6f}")
chk("R_dp spread UMi28 C9", 0.014, round(LAB["U28NR32B16e4"]["spreadR"], 3)); chk("R_dp spread UMi28 C9 (6 dp)", "0.014440", f"{LAB['U28NR32B16e4']['spreadR']:.6f}")
chk("R_dp spread D2 C9", 0.017, round(LAB["NR32B16e4"]["spreadR"], 3)); chk("R_dp spread D2 C9 (6 dp)", "0.017415", f"{LAB['NR32B16e4']['spreadR']:.6f}")
chk("SigmaF_V1 spread", [15, 12, 19], [LAB[a]["spreadV"] for a in CELLS])

print("=" * 100); print("§4 frontier dR / S1 (unpaired difference vs C2 a1 raw), gaps")
DR = {}
for A, (cell, prior, nr, DP, (c2raw, c2cell, c2snr), cname, *_) in CELLS.items():
    c2pts, c2meta, c2n, _ = load(c2raw)
    c2keys = [(c2cell, "UMi28" if "U28" in c2raw else "S2", s) for s in c2snr]
    c2cols = [(fails(c2pts[k], BS), fails(c2pts[k], V1), fails(c2pts[k], GEN)) for k in c2keys]
    print(f"{c2raw}: files {c2n} run|git {sorted(c2meta.get('run|git', {'(no run|git key -- legacy raw)'}))} C2 points {[k[2] for k in c2keys]} counts {R(c2cols)[1]}")
    for T in [A + "s2", A + "s3"]:
        r = frontier((f"raw_{T}", RES[T]["keys"], RES[T]["cols"]), (c2raw, c2keys, c2cols))
        DR[T] = r
        rec = REC[T]
        print(f"{T}: R1 {r['R1']:.3f} [{r['R1ci'][0]:.3f}, {r['R1ci'][1]:.3f}]  R2 {r['R2']:.3f} [{r['R2ci'][0]:.3f}, {r['R2ci'][1]:.3f}]  "
              f"R1-R2 {r['d']:+.3f} [90% {r['d90'][0]:+.3f}, {r['d90'][1]:+.3f}] [95% {r['dL'][0]:+.3f}, {r['dL'][1]:+.3f}] p={r['p']:.4f} und {r['und']}  "
              f"gaps R1 {r['gaps1'][0][1] - r['gaps1'][0][2]} [{r['gaps1'][1][0]:.0f}, {r['gaps1'][1][1]:.0f}] / {r['gaps1'][0][0] - r['gaps1'][0][2]} [{r['gaps1'][2][0]:.0f}, {r['gaps1'][2][1]:.0f}]  "
              f"gaps R2 {r['gaps2'][0][1] - r['gaps2'][0][2]} [{r['gaps2'][1][0]:.0f}, {r['gaps2'][1][1]:.0f}] / {r['gaps2'][0][0] - r['gaps2'][0][2]} [{r['gaps2'][2][0]:.0f}, {r['gaps2'][2][1]:.0f}]")
        chk(f"{T} dR point + 90% CI", rec["dR"], (round(r["d"], 3), round(float(r["d90"][0]), 3), round(float(r["d90"][1]), 3)))
        chk(f"{T} dR 95% CI", rec["dR95"], (round(float(r["dL"][0]), 3), round(float(r["dL"][1]), 3)))
        chk(f"{T} p", "0.0000", f"{r['p']:.4f}"); chk(f"{T} undefined replicates", 0, r["und"])
        chk(f"{T} R1 (frontier) CI", rec["R1ci"], (round(float(r["R1ci"][0]), 3), round(float(r["R1ci"][1]), 3)))
        chk(f"{T} R2 = C2 a1 R", C2REC[c2raw]["R"], round(r["R2"], 3)); chk(f"{T} R2 CI", C2REC[c2raw]["ci"], (round(float(r["R2ci"][0]), 3), round(float(r["R2ci"][1]), 3)))
        chk(f"{T} R2 counts", C2REC[c2raw]["cnt"], r["gaps2"][0])
        g1 = r["gaps1"]; chk(f"{T} gaps R1", rec["gaps"], (g1[0][1] - g1[0][2], int(round(g1[1][0])), int(round(g1[1][1])), g1[0][0] - g1[0][2], int(round(g1[2][0])), int(round(g1[2][1]))))
        g2 = r["gaps2"]; chk(f"{T} gaps R2", C2REC[c2raw]["gaps"], (g2[0][1] - g2[0][2], int(round(g2[1][0])), int(round(g2[1][1])), g2[0][0] - g2[0][2], int(round(g2[2][0])), int(round(g2[2][1]))))
# a1 gaps (SCALE16e4 §6.1.4 (c)) at the 3 decision points, for the §6.1.5 (d) a1 line
for A in CELLS:
    r = frontier((f"raw_{A}", RES[A]["keys"], RES[A]["cols"]), (f"raw_{A}", RES[A]["keys"], RES[A]["cols"]))
    g1 = r["gaps1"]; chk(f"{A} (a1) gaps point (V1-g, b*-g)", A1REC[A]["gaps"], (g1[0][1] - g1[0][2], g1[0][0] - g1[0][2]))

print("=" * 100); print("§5 statement conditions (S1)-(S3) and §3 prediction scoring (literal wording)")
s2 = {"D2": [DR["NR32B16e4s2"]["dL"][0] > 0, DR["NR32B16e4s3"]["dL"][0] > 0], "UMi28": [DR["U28NR32B16e4s2"]["d90"][0] > 0, DR["U28NR32B16e4s3"]["d90"][0] > 0]}
s3 = [DR["U28NR16B16e4s2"]["d90"][0] > 0, DR["U28NR16B16e4s3"]["d90"][0] > 0]
chk("(S2) D2 95% lower > 0 both", [True, True], s2["D2"]); chk("(S2) UMi28 90% lower > 0 both", [True, True], s2["UMi28"]); chk("(S3) UMi28 S1 90% lower > 0 both", [True, True], s3)
chk("(S1) all three labels start with 시드 강건 (3/3 (i)", True, all(LAB[a]["lab"].startswith("시드 강건 (3/3 (i)") for a in CELLS))
pred = {}
pred[1] = LAB["U28NR16B16e4"]["lab"] == "시드 강건 (3/3 (i))"
pred[2] = LAB["U28NR32B16e4"]["lab"] == "시드 강건 (3/3 (i))"
pred[3] = LAB["NR32B16e4"]["lab"] == "시드 강건 (3/3 (i))"          # literal string
pred["3-bold"] = LAB["NR32B16e4"]["labs"][1:] == ["(i)", "(i)"]  # bold condition only
pred[4] = all(CELLS["U28NR16B16e4"][8][0] <= RES[t]["cnt"][1] * 0 + RES[t]["v"][0] / 2560 <= CELLS["U28NR16B16e4"][8][1] for t in ("U28NR16B16e4s2", "U28NR16B16e4s3"))
pred[5] = all(CELLS["U28NR32B16e4"][8][0] <= RES[t]["v"][0] / 2560 <= CELLS["U28NR32B16e4"][8][1] for t in ("U28NR32B16e4s2", "U28NR32B16e4s3"))
pred[6] = all(CELLS["NR32B16e4"][8][0] <= RES[t]["v"][0] / 2560 <= CELLS["NR32B16e4"][8][1] for t in ("NR32B16e4s2", "NR32B16e4s3"))
# also with 3-dp rounded value (the prediction quotes 3-digit values); both readings
pred["4-6 rounded"] = all(CELLS[a][8][0] <= round(RES[a + s]["v"][0] / 2560, 3) <= CELLS[a][8][1] for a in CELLS for s in ("s2", "s3"))
pred[7] = all(max(RES[a + s]["ci"][0], CELLS[a][7][0]) <= min(RES[a + s]["ci"][1], CELLS[a][7][1]) for a in CELLS for s in ("s2", "s3"))
pred[8] = all(LAB[a]["spreadR"] <= 0.05 for a in CELLS)
pred[9] = RES["NR32B16e4s2"]["R"] < 0.811
pred[10] = all(s2["D2"]) and all(s2["UMi28"]) and all(s3)
for k, v in pred.items():
    print(f"  prediction {k}: {'적중' if v else '빗나감'}  ({v})")
chk("pred 1", True, pred[1]); chk("pred 2", True, pred[2]); chk("pred 3 literal string", False, pred[3]); chk("pred 3 bold condition", True, pred["3-bold"])
chk("pred 4", True, pred[4]); chk("pred 5", True, pred[5]); chk("pred 6", True, pred[6]); chk("pred 4-6 with 3-digit rounding", True, pred["4-6 rounded"])
chk("pred 7", True, pred[7]); chk("pred 8", True, pred[8]); chk("pred 9", False, pred[9]); chk("pred 10", True, pred[10])
print(f"  D2 C9 a2 R_dp {RES['NR32B16e4s2']['R']:.6f} vs a1 {RES['NR32B16e4']['R']:.6f}: a2 < a1 = {pred[9]}")
print(f"  pred 6 raw BLER: a2 {RES['NR32B16e4s2']['v'][0]}/2560 = {RES['NR32B16e4s2']['v'][0] / 2560:.4f}, a3 {RES['NR32B16e4s3']['v'][0]}/2560 = {RES['NR32B16e4s3']['v'][0] / 2560:.4f}")

print("=" * 100); print("§6 files: recovery / dR / accept / refarms / tables / manifest / guard / logs")
for T, rec in REC.items():
    txt = open(f"{RN}/recovery_{T}.txt").read().splitlines()
    chk(f"recovery_{T}.txt line count", 5, len(txt))
    m = re.search(r"pooled 3 SNRs  b\* (\d+)  V1 (\d+)  genie (\d+)  R = ([\d.]+)  \[90% ([\d.]+), ([\d.]+)\]", txt[4])
    chk(f"recovery_{T}.txt:5 counts", RES[T]["cnt"], tuple(int(m[i]) for i in (1, 2, 3)))
    chk(f"recovery_{T}.txt:5 R [CI] = my bootstrap", (f"{RES[T]['R']:.3f}", f"{RES[T]['ci'][0]:.3f}", f"{RES[T]['ci'][1]:.3f}"), (m[4], m[5], m[6]))
    for i, (rr, l, h) in enumerate(RES[T]["perpt"]):
        mm = re.search(r"R = ([\d.]+)  \[90% ([\d.]+), ([\d.]+)\]", txt[1 + i])
        chk(f"recovery_{T}.txt:{2 + i} per-point", (f"{rr:.3f}", f"{l:.3f}", f"{h:.3f}"), (mm[1], mm[2], mm[3]))
    d = open(f"{RN}/seedsnr_dR_{T}.txt").read().splitlines()
    chk(f"seedsnr_dR_{T}.txt header git", "b53a8529", re.search(r"git (\w+)", d[0])[1])
    r = DR[T]
    want3 = f"  R1: raw_{T} {CELLS[T[:-2]][0]} SNR {[f'{k[2]:+.0f}' for k in RES[T]['keys']]}  b* {r['gaps1'][0][0]} V1 {r['gaps1'][0][1]} genie {r['gaps1'][0][2]}  R = {r['R1']:.3f}  [90% {r['R1ci'][0]:.3f}, {r['R1ci'][1]:.3f}]"
    chk(f"seedsnr_dR_{T}.txt:3 byte-equal", want3, d[2])
    want5 = f"  R1 - R2 = {r['d']:+.3f}  [90% unpaired {r['d90'][0]:+.3f}, {r['d90'][1]:+.3f}]  undefined replicates {r['und']}"
    chk(f"seedsnr_dR_{T}.txt:5 byte-equal", want5, d[4])
    want6 = f"  R1 - R2 = {r['d']:+.3f}  [95% unpaired {r['dL'][0]:+.3f}, {r['dL'][1]:+.3f}]  bootstrap two-sided p = {r['p']:.4f}  (--level 0.95)"
    chk(f"seedsnr_dR_{T}.txt:6 byte-equal", want6, d[5])
    acc = open(f"{RN}/{T}_accept.txt").read().splitlines()
    chk(f"{T}_accept.txt:1", f"ACCEPT: OK -- {T}", acc[0])
    if rec["jobs"]:
        chk(f"{T}_accept.txt:2 (k)", f"  (k) raw_{T}: meta|worker_gb ['8.0']  meta|jobs ['{rec['jobs']}']", acc[1]); chk(f"{T}_accept.txt:3", "ACCEPT (k): OK", acc[2])
    else:
        chk(f"{T}_accept.txt lines", 1, len(acc))
    ref = open(f"{RN}/{T}_refarms.txt").read().splitlines()
    chk(f"{T}_refarms.txt:1", "ACCEPT: FAILED", ref[0]); chk(f"{T}_refarms.txt lines", 4, len(ref))
    pat = re.compile(rf"^  {T} \('{CELLS[T[:-2]][0]}', -?\d+\): replay vs raw_{T[:-2]} \(all\): shared 2560/2560, arms differing \['M-ours-dscore-C-V1'\] \(max \|diff\| [^)]*\)$")
    chk(f"{T}_refarms.txt:2-4 gate pattern", [True] * 3, [bool(pat.match(x)) for x in ref[1:]])
    tab = open(f"results/tables_D2_{T}.txt").read().splitlines()
    chk(f"tables_D2_{T}.txt:2 git", "# git commit  : b53a8529", tab[1])
    chk(f"tables_D2_{T}.txt:49 raw git", rec["git"], re.search(r"git=(\w+)", tab[48])[1])
    blocks = [i for i, l in enumerate(tab) if l.startswith("  M-ours-bstar -> M-ours-dscore-C-V1 ")]
    chk(f"tables_D2_{T}.txt b*->V1 block count", 1, len(blocks))
    i = blocks[0]
    chk(f"tables_D2_{T}.txt b*->V1 block line", 260 if "U28" in T else 257, i + 1)
    ab = RES[T]["ab"]; dpstr = "  ".join(f"{s:+.0f} dB {a}:{b} p={p:.2g}" for (a, b, p), s in zip(ab, CELLS[T[:-2]][3]))
    chk(f"tables_D2_{T}.txt:{i + 3} sign test byte-equal", f"    sign test @16: {dpstr}   pooled {RES[T]['pooled'][0]}:{RES[T]['pooled'][1]} p={RES[T]['pp']:.2g}", tab[i + 2])
    chk(f"tables_D2_{T}.txt:{i + 4} POWERED", "    power guard: 3 decision points, 3 with >= 6 discordant pairs -> POWERED", tab[i + 3])
    chk(f"tables_D2_{T}.txt:{i + 5} 3/3", "    two-sided sign test at p < .05: second arm fewer failures at 3/3 points, first arm fewer failures at 0/3 points -> significant", tab[i + 4])
    v1row = [l for l in tab[60:80] if l.startswith("  M-ours-dscore-C-V1 ")][0]; mm = re.match(r"  M-ours-dscore-C-V1\s+([\d.]+)\(([\d.]+),([\d.]+)\)", v1row)
    chk(f"tables_D2_{T}.txt table A V1 first point (BLER, Wilson)", (f"{rec['w'][0]:.3f}", f"{rec['w'][1]:.3f}", f"{rec['w'][2]:.3f}"), (mm[1], mm[2], mm[3]))
    chk(f"tables_D2_{T}.txt table A V1 row line", 74 if "U28" in T else 71, tab.index(v1row) + 1)
    chk(f"tables_D2_{T}.txt:47 ckpt id", True, tab[46].startswith("#   stagec_ckpt_id      : sha256[:16]=") and tab[46].split("=", 1)[1] in " ".join(raws[T][1]["meta|stagec_ckpt_id"]))
    chk(f"tables_D2_{T}.txt:29-31,33-36,41 N_train=160000 (GMM arms)", True, all("N_train=160000" in tab[j] for j in [28, 29, 30, 32, 33, 34, 35, 40]))
    chk(f"tables_D2_{T}.txt:32 is R3-bigamp N_train=0 (NOT a GMM arm; record cites :29-36)", True, tab[31].startswith("#   R3-bigamp") and "N_train=0" in tab[31])
    chk(f"tables_D2_{T}.txt:38 V1 budget line", "N_train=28160000" if "U28" in T else "N_train=160000", re.search(r"N_train=(\d+)", tab[37])[0])
    chk(f"tables_D2_{T}.txt:51 UMi28 banner", "U28" in T, tab[50].startswith("# SECOND TESTBED, STANDARD-MODEL SIDE (prior UMi28)"))
    chk(f"tables_D2_{T}.txt:48 cell line prior", "UMi28" if "U28" in T else "S2", re.search(r"prior (\w+)", tab[47])[1])
    man = json.load(open(f"{RN}/run_manifest_{T}.json"))
    chk(f"run_manifest_{T}.json git_commit/config_hash/n_raw/run_params.git", ("b53a8529", rec["cfg"], 192, rec["git"]), (man["git_commit"], man["config_hash"], man["n_raw_files"], man["run_params"]["git"]))
    chk(f"run_manifest_{T}.json stagec_ckpt_id = raw", True, man["stagec_ckpt_id"] in " ".join(raws[T][1]["meta|stagec_ckpt_id"]))
    gd = open(f"results/guard_D2_{T}.txt").read().splitlines()
    chk(f"guard_D2_{T}.txt:16", True, gd[15].startswith("NO GUARD FIRINGS in this raw set."))
for C in ("U28NR16B16e4chkS", "U28NR16B16e4chkS2"):
    chk(f"{C}_accept.txt", [f"ACCEPT: OK -- {C}"], open(f"{RN}/{C}_accept.txt").read().splitlines())

print("=" * 100); print("§7 run log / runner logs / git / times")
L = open("logs/run_seedsnr16e4.log").read().splitlines()
chk("run log lines", 142, len(L))
chk("L:65", "[seedsnr 10-04 17:34 CDT] SEEDSNR_DONE ok=47 fail=0 pending= NR32B16e4s3 trainfail= none", L[64])
chk("L:66", "SEEDSNR_EXIT=0", L[65]); chk("L:142", "[seedsnr 10-04 22:53 CDT] SEEDSNR_DONE ok=51 fail=0 pending= none trainfail= none", L[141])
chk("L:1 start", True, L[0].startswith("[seedsnr 10-03 23:03 CDT] start (git d59b4c6c, freeze cd85bef199b0190d372da4a12996f4796f93d765, resume 0, chk U28NR16B16e4chkS, WGB 8.0 (run 8.0), CUDA_VISIBLE_DEVICES='')"))
chk("L:67 start", True, L[66].startswith("[seedsnr 10-04 17:36 CDT] start (git b53a8529, freeze cd85bef199b0190d372da4a12996f4796f93d765, resume 1, chk U28NR16B16e4chkS2, WGB 8.0 (run 8.0), CUDA_VISIBLE_DEVICES='')"))
rc0 = sum(1 for l in L[:66] if l.rstrip().endswith("rc=0")); rcx = sum(1 for l in L[:66] if re.search(r"rc=(?!0\b)\d+$", l))
chk("batch 1 rc=0 count = ok 47", 47, rc0); chk("batch 1 rc!=0 = 0", 0, rcx)
rc0b = sum(1 for l in L[66:] if l.rstrip().endswith("rc=0")); rcxb = sum(1 for l in L[66:] if re.search(r"rc=(?!0\b)\d+$", l))
chk("batch 2 rc=0 count = ok 51", 51, rc0b); chk("batch 2 rc!=0 = 0", 0, rcxb)
chk("ABORT/SKIPPED/fail lines", 0, sum(1 for l in L if re.search(r"ABORT|SKIPPED|training failed", l)))
chk("skip lines batch 2", [71, 83, 95, 107, 119], [i + 1 for i, l in enumerate(L) if "skip: raw complete" in l])
chk("manifest JSON lines", [8, 20, 32, 44, 56, 74, 86, 98, 110, 122, 134], [i + 1 for i, l in enumerate(L) if l.startswith("{")])
chk("L:64 PENDING", "[seedsnr 10-04 17:34 CDT] NR32B16e4s3 PENDING: no SEED line yet (§3d ladder open) -> batch 2 (§5 addendum commit, --resume)", L[63])
from datetime import datetime
t = lambda s: datetime.strptime("2026-" + re.search(r"(\d\d-\d\d \d\d:\d\d)", s)[1], "%Y-%m-%d %H:%M")
e1 = t(L[64]) - t(L[0]); e2 = t(L[141]) - t(L[66])
chk("batch 1 elapsed", "18 h 31 min", f"{e1.seconds // 3600 + e1.days * 24} h {e1.seconds % 3600 // 60} min")
chk("batch 2 elapsed", "5 h 17 min", f"{e2.seconds // 3600} h {e2.seconds % 3600 // 60} min")
# step-end times quoted in §6.1 runner table note
ends = {15: "00:14", 27: "01:06", 39: "06:55", 51: "12:47", 63: "17:34", 141: "22:53", 81: "17:58", 93: "18:00", 105: "18:02", 117: "18:03", 129: "18:05"}
chk("frontier dR line times", list(ends.values()), [re.search(r"\d\d-\d\d (\d\d:\d\d)", L[i - 1])[1] for i in ends])
chk("frontier dR lines are frontier lines", True, all("frontier dR" in L[i - 1] for i in ends))
runs = {"U28NR16B16e4chkS": (1, 1176, "19.6", 9), "U28NR16B16e4s2": (192, 2735, "50.1", 200), "U28NR16B16e4s3": (192, 2726, "50.3", 200),
        "U28NR32B16e4s2": (99, 10242, "347.0", 201), "U28NR32B16e4s3": (99, 10120, "350.1", 201), "NR32B16e4s2": (98, 8093, "286.0", 201),
        "U28NR16B16e4chkS2": (1, 1211, "20.2", 9), "NR32B16e4s3": (98, 8152, "286.3", 201)}
for T, (w, s, mins, nl) in runs.items():
    r = open(f"logs/run_D2_{T}.log").read().splitlines()
    chk(f"run_D2_{T}.log lines / headers", (nl, 1), (len(r), sum(1 for l in r if l.startswith("# run_seedsnr16e4"))))
    chk(f"run_D2_{T}.log workers", w, int(re.search(r"on (\d+) workers", [l for l in r if " tasks on " in l][0])[1]))
    chk(f"run_D2_{T}.log first done chunk s", s, int(re.search(r"\((\d+) s\)", [l for l in r if " done " in l][0])[1]))
    chk(f"run_D2_{T}.log finished min", mins, re.search(r"finished in ([\d.]+) min", r[-1])[1])
    chk(f"run_D2_{T}.log warn/error/traceback", 0, sum(1 for l in r if re.search(r"(?i)warn|error|traceback|exception", l)))
    if "chk" not in T:
        chk(f"run_D2_{T}.log done chunks", 192, sum(1 for l in r if re.search(r"^\d+/192 done", l)))
g = lambda *a: subprocess.run(["git", *a], capture_output=True, text=True).stdout.strip()
chk("HEAD", "b53a8529", g("rev-parse", "--short", "HEAD")); chk("commits after b53a8529", "", g("rev-list", "b53a8529..HEAD"))
chk("status code ../Demo clean", "", g("status", "--porcelain", "code", "../Demo"))
chk("diff cd85bef1 d59b4c6c code/Demo bytes", "", g("diff", "cd85bef1", "d59b4c6c", "--", "code", "../Demo"))
chk("diff d59b4c6c b53a8529 code/Demo bytes", "", g("diff", "d59b4c6c", "b53a8529", "--", "code", "../Demo"))
chk("name-status b4433d3c b53a8529 code/Demo", "A\tconf/code/run_seedsnr16e4.sh", g("diff", "--name-status", "b4433d3c", "b53a8529", "--", "code", "../Demo"))
chk("files changed cd85bef1..d59b4c6c", "conf/results/review_next/NEXT_EXPERIMENTS_SEEDSNR16e4.md\nconf/results/scale/seedsnr_s5.txt", g("diff", "--name-only", "cd85bef1", "d59b4c6c"))
chk("files changed d59b4c6c..b53a8529", "conf/results/review_next/NEXT_EXPERIMENTS_SEEDSNR16e4.md\nconf/results/scale/seedsnr_s5.txt", g("diff", "--name-only", "d59b4c6c", "b53a8529"))
env = dict(os.environ, TZ="America/Chicago")
dt = lambda c: subprocess.run(["git", "log", "-1", "--format=%ad", "--date=format-local:%Y-%m-%d %H:%M:%S %Z", c], capture_output=True, text=True, env=env).stdout.strip()
chk("freeze commit time", "2026-10-03 22:59:56 CDT", dt("cd85bef1")); chk("run commit 1 time", "2026-10-03 23:03:15 CDT", dt("d59b4c6c")); chk("run commit 2 time", "2026-10-04 17:36:46 CDT", dt("b53a8529"))
chk("full hashes", ("d59b4c6ca15004c75b90068eeaaf379f43e97fc4", "b53a8529c55d3c5f58ab480c986fd530cd60a0cd", "cd85bef199b0190d372da4a12996f4796f93d765"), (g("rev-parse", "d59b4c6c"), g("rev-parse", "b53a8529"), g("rev-parse", "cd85bef1")))
s5 = open("results/scale/seedsnr_s5.txt").read().splitlines()
chk("seedsnr_s5.txt:11", "SEED NR32B16e4s3 d2sx_NR32_N160000_a3_fb2 03a5d4b2acabde01", s5[10])
chk("seedsnr_s5.txt tracked = HEAD", g("show", "HEAD:conf/results/scale/seedsnr_s5.txt"), "\n".join(s5))
# §0-§5 unchanged: working copy lines 1-157 == HEAD lines
head_doc = g("show", "HEAD:conf/results/review_next/NEXT_EXPERIMENTS_SEEDSNR16e4.md").split("\n")
wc_doc = open(f"{RN}/NEXT_EXPERIMENTS_SEEDSNR16e4.md").read().split("\n")
chk("HEAD doc length (lines)", 157, len([x for x in head_doc if True]) - (1 if head_doc[-1] == "" else 0))
chk("§0-§5 (:1-157) byte-identical to HEAD", True, wc_doc[:157] == head_doc[:157])
chk("working doc lines", 339, len(wc_doc) - (1 if wc_doc[-1] == "" else 0))
chk(":158 blank, :159 §6.1 heading", True, wc_doc[157] == "" and wc_doc[158].startswith("### 6.1 결과 (기록 2026-10-04 23:09 CDT (= 10-05 13:09 KST)"))
# manifest written (KST) vs log run_manifest line (CDT): -14 h
for T, Lno in {"U28NR16B16e4s2": 76, "U28NR16B16e4s3": 88, "U28NR32B16e4s2": 100, "U28NR32B16e4s3": 112, "NR32B16e4s2": 124, "NR32B16e4s3": 136}.items():
    w = json.load(open(f"{RN}/run_manifest_{T}.json"))["written"]
    kst = datetime.strptime(w, "%Y-%m-%d %H:%M:%S KST"); cdt = kst - __import__("datetime").timedelta(hours=14)
    chk(f"manifest {T} written KST-14h = log L:{Lno} (minute)", re.search(r"\d\d-\d\d \d\d:\d\d", L[Lno - 1])[0], cdt.strftime("%m-%d %H:%M"))
# ckpt sha
import hashlib
for stem, sha in [("d2sx_UMi28NR16_N160000_a2", "f956a85c82ed4fb3"), ("d2sx_UMi28NR16_N160000_a3", "9c38545ab009f307"), ("d2sx_UMi28NR32_N160000_a2", "c11bb951ff7be4d4"),
                  ("d2sx_UMi28NR32_N160000_a3", "7f72480c42fcd6c9"), ("d2sx_NR32_N160000_a2", "0c887ee786ff9dfa"), ("d2sx_NR32_N160000_a3_fb2", "03a5d4b2acabde01"),
                  ("d2sx_UMi28NR16_N160000_a1", "34136808b1e367ac"), ("d2sx_UMi28NR32_N160000_a1", "463da87aa8dbfb61"), ("d2sx_NR32_N160000_a1", "3cf5d3eff96f0341")]:
    h = hashlib.sha256(open(f"/home/HTJ/t2/conf/ckpt/{stem}_best.pt", "rb").read()).hexdigest()[:16]
    chk(f"ckpt sha {stem}", sha, h)

print("=" * 100)
bad = [c for c in CHECKS if not c[3]]
print(f"TOTAL checks {len(CHECKS)}  mismatches {len(bad)}")
for c in bad:
    print("  MISMATCH:", c)
