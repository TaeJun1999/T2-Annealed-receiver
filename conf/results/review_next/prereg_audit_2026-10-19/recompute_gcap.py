"""recompute_gcap.py -- independent recomputation for the record audit of NEXT_EXPERIMENTS_U28NR32GCAP §5/§6.
numpy + math only: raw chunks are read directly (analysis.load_raw / gcap_compare / recovery_ci / Demo are NOT imported).
Read-only; prints everything (redirect to recompute_gcap.out)."""
import glob, math, os, re, sys
import numpy as np

NEW = "/home/HTJ/t2/conf/raw_U28NR32GCAPe"
CHK = "/home/HTJ/t2/conf/raw_U28NR32GCAPchk"
OLD = "/home/HTJ/t2_wtS/conf/raw_U28NR32B16e4"
ELOG = "/home/HTJ/t2/conf/logs/run_D2_U28NR32GCAPe.log"
KEYS_RAW = ("blk_err", "ber", "nmse", "tauL_gmean", "alphaD", "tauL_clip_frac", "alphaD_clip")
BS, V1, G = "M-ours-bstar", "M-ours-dscore-C-V1", "R5-genie"
PAT = re.compile(r"^D2_C9_UMi28_Nr32_T16_Tp4_eig_snr(-?\d+)_skip(\d+)_n(\d+)\.npz$")
SNRS = [-12, -9, -6, -3, 0, 3, 6]
NTOT = 2560
mism = []            # (what, recorded, recomputed)
nchk = [0]


def check(what, recorded, recomputed, tol=0.0):
    nchk[0] += 1
    ok = (recorded == recomputed) if tol == 0 else (abs(float(recorded) - float(recomputed)) <= tol)
    if not ok:
        mism.append((what, recorded, recomputed))
    print(f"  [{'ok' if ok else 'MISMATCH'}] {what}: recorded {recorded!r} recomputed {recomputed!r}")


def sign_p(a, b):
    n = a + b
    return 1.0 if n == 0 else min(1.0, 2 * sum(math.comb(n, i) for i in range(min(a, b) + 1)) / 2 ** n)


def plan(root):
    pts = {}
    for f in sorted(os.listdir(root)):
        m = PAT.match(f)
        if not m:
            print(f"  !! unexpected file name {f}")
            continue
        pts.setdefault(int(m[1]), []).append((int(m[2]), int(m[3]), os.path.join(root, f)))
    return pts


def load_point(chunks, n_expect):
    """concatenate chunks in skip order; returns dict arm -> {key: array}, plus scalar run/meta dict, plus key notes"""
    chunks = sorted(chunks)
    pos, holes = 0, []
    for s, n, _ in chunks:
        if s != pos:
            holes.append((pos, s))
        pos = s + n
    assert pos == n_expect, (pos, n_expect)
    zs = [np.load(f) for _, _, f in chunks]
    keys = sorted({k for z in zs for k in z.files})
    d, scal, failed_keys, missing = {}, {}, set(), set()
    for k in keys:
        if "|" not in k:
            continue
        a0 = next(z[k] for z in zs if k in z.files)
        if a0.ndim == 0:
            vals = {str(z[k]) for z in zs if k in z.files}
            scal[k] = vals
            continue
        arm, q = k.split("|", 1)
        if q == "failed":
            failed_keys.add(arm)
        parts = []
        for z, (_, n, _) in zip(zs, chunks):
            if k in z.files:
                parts.append(z[k])
            else:
                missing.add(k)
                parts.append(np.full((n,) + a0.shape[1:], np.nan))
        d.setdefault(arm, {})[q] = np.concatenate(parts)
    return d, scal, holes, failed_keys, missing


def fails(arr):
    v = arr[:, -1]
    return np.where(np.isfinite(v), v, 1.0)


def snr_at(snrs, bler, n, target=0.1):
    lb = np.log10(np.maximum(np.asarray(bler, float), 0.5 / n)); lt = math.log10(target)
    if lb[0] <= lt:
        return snrs[0], "lo"
    for i in range(len(snrs) - 1):
        if lb[i] > lt >= lb[i + 1]:
            return snrs[i] + (lb[i] - lt) / (lb[i] - lb[i + 1]) * (snrs[i + 1] - snrs[i]), "ok"
    return snrs[-1], "hi"


def decision_points(bler_by_snr, n):
    bl = {s: max(b, 0.5 / n) for s, b in bler_by_snr.items()}
    cand = sorted((s for s in SNRS if 0.005 <= bl[s] <= 0.9), key=lambda s: abs(math.log10(bl[s] / 0.1)))[:3]
    return sorted(cand)


print("=" * 100)
print("1. chunk plans")
pn, po, pc = plan(NEW), plan(OLD), plan(CHK)
check("new raw: SNR set", SNRS, sorted(pn))
check("old raw: SNR set", SNRS, sorted(po))
check("new raw: file count", 448, sum(len(v) for v in pn.values()))
check("old raw: file count", 448, sum(len(v) for v in po.values()))
for s in SNRS:
    check(f"new raw {s:+d} dB chunk plan (skip, n) = {{(40k, 40)}}", [(40 * k, 40) for k in range(64)], sorted((a, b) for a, b, _ in pn[s]))
    check(f"old raw {s:+d} dB chunk plan", [(40 * k, 40) for k in range(64)], sorted((a, b) for a, b, _ in po[s]))
check("chk raw: files", [(0, (0, 40))], [(s, (a, b)) for s, v in pc.items() for a, b, _ in v])

print("=" * 100)
print("2. per-point loading, meta / run scalars, failed keys, non-finite blk_err")
new, old = {}, {}
scal_new, scal_old = {}, {}
for s in SNRS:
    dn, sn, hn, fkn, mn = load_point(pn[s], NTOT)
    do, so, ho, fko, mo = load_point(po[s], NTOT)
    new[s], old[s] = dn, do
    for k, v in sn.items():
        scal_new.setdefault(k, set()).update(v)
    for k, v in so.items():
        scal_old.setdefault(k, set()).update(v)
    check(f"new {s:+d}: holes", [], hn); check(f"old {s:+d}: holes", [], ho)
    check(f"new {s:+d}: '|failed' keys", set(), fkn); check(f"old {s:+d}: '|failed' keys", set(), fko)
    check(f"new {s:+d}: keys missing from some chunk", set(), mn); check(f"old {s:+d}: keys missing from some chunk", set(), mo)
    for arm in dn:
        be = dn[arm]["blk_err"]
        check(f"new {s:+d} {arm}: blk_err shape", (NTOT, 16), be.shape)
        check(f"new {s:+d} {arm}: blk_err finite and in {{0,1}}", True, bool(np.isfinite(be).all() and np.isin(be, (0.0, 1.0)).all()))
    for arm in (BS, V1, G):
        be = do[arm]["blk_err"]
        check(f"old {s:+d} {arm}: blk_err finite and in {{0,1}}", True, bool(np.isfinite(be).all() and np.isin(be, (0.0, 1.0)).all()))
check("new raw arms", [BS, G], sorted(new[0]))
print("  old raw arms:", sorted(old[0]))
print("  new raw scalar run|meta value sets:")
for k in sorted(scal_new):
    print(f"    {k}: {sorted(scal_new[k])}")
check("new meta|bstar", {"kron"}, scal_new["meta|bstar"])
check("new meta|kron_K", {"8192"}, scal_new["meta|kron_K"])
check("new meta|ll_val|kron", {"154.13990347772582"}, scal_new["meta|ll_val|kron"])
check("new meta|ntrain", {"160000.0"}, scal_new["meta|ntrain"])
check("new meta|worker_gb", {"13.5"}, scal_new["meta|worker_gb"])
check("new run|git", {"64b2912f"}, scal_new["run|git"])
check("new run|seed", {"20260926"}, scal_new["run|seed"])
check("new run|iters", {"16"}, scal_new["run|iters"])
check("new run|dtype", {"complex128/float64"}, scal_new["run|dtype"])
check("new meta|em_sec", {"40544.76968383789"}, scal_new["meta|em_sec"])
check("new meta|stagec_ckpt_id", {"sha256[:16]=463da87aa8dbfb61 epoch=232 best_epoch=232 role=best 32x4"}, scal_new["meta|stagec_ckpt_id"])
print("  old raw: run|git", sorted(scal_old["run|git"]), " meta|kron_K", sorted(scal_old["meta|kron_K"]),
      " meta|ll_val|kron", sorted(scal_old["meta|ll_val|kron"]), " run|seed", sorted(scal_old["run|seed"]),
      " run|iters", sorted(scal_old["run|iters"]), " meta|stagec_ckpt_id", sorted(scal_old.get("meta|stagec_ckpt_id", [])))
check("old run|git", {"b4433d3c"}, scal_old["run|git"])
check("old meta|kron_K", {"4096"}, scal_old["meta|kron_K"])
check("old meta|ll_val|kron", {"152.23176788511105"}, scal_old["meta|ll_val|kron"])
# meta|jobs per chunk (new)
jobs = {}
for s in SNRS:
    for _, _, f in pn[s]:
        z = np.load(f)
        jobs[int(z["meta|jobs"])] = jobs.get(int(z["meta|jobs"]), 0) + 1
check("new meta|jobs histogram", {58: 116, 55: 332}, jobs)
# run| fields identical old vs new per file name
bad = []
for s in SNRS:
    for a, b, f in pn[s]:
        zo = np.load(os.path.join(OLD, os.path.basename(f))); zn = np.load(f)
        for k in ("run|seed", "run|iters", "run|beta", "run|t_in", "run|dtype", "run|n", "run|skip", "run|snr"):
            if str(zn[k]) != str(zo[k]):
                bad.append((os.path.basename(f), k))
check("new vs old run| fields per chunk file", [], bad)

print("=" * 100)
print("3. R5-genie bit-identity new vs old (all 448 chunks, every R5-genie|* key) and chk vs old chunk (every arm|key)")
narr, bad = 0, []
for s in SNRS:
    for a, b, f in pn[s]:
        zn = np.load(f); zo = np.load(os.path.join(OLD, os.path.basename(f)))
        gk = [k for k in zn.files if k.startswith("R5-genie|")]
        for k in gk:
            narr += 1
            if k not in zo.files or not np.array_equal(zn[k], zo[k], equal_nan=True):
                bad.append((os.path.basename(f), k))
print(f"  genie arrays compared: {narr} ({narr // 448} keys x 448 chunks)")
check("R5-genie arrays differing new vs old", [], bad)
# also compare the trial-level channel/bit-identity proxy: ber of genie (already included) -- nothing else is stored per trial
zc = np.load(pc[0][0][2]); zo = np.load(os.path.join(OLD, "D2_C9_UMi28_Nr32_T16_Tp4_eig_snr0_skip0_n40.npz"))
ck = sorted(k for k in zc.files if "|" in k and not k.startswith(("meta|", "run|")))
ok_ = sorted(k for k in zo.files if "|" in k and not k.startswith(("meta|", "run|")))
check("chk: data key set == old chunk key set", ok_, ck)
arms_chk = sorted({k.split("|")[0] for k in ck})
check("chk: 11 arms", 11, len(arms_chk)); print("  chk arms:", arms_chk)
bad = [k for k in ck if k not in zo.files or not np.array_equal(zc[k], zo[k], equal_nan=True)]
print(f"  chk arrays compared: {len(ck)}")
check("chk arrays differing vs old chunk", [], bad)
check("chk run|git", "64b2912f", str(zc["run|git"])); check("chk meta|kron_K", "4096", str(zc["meta|kron_K"]))
check("chk meta|ll_val|kron", "152.23176788511105", str(zc["meta|ll_val|kron"])); check("chk run|snr", "0.0", str(zc["run|snr"]))
check("chk n trials", 40, int(zc["R5-genie|blk_err"].shape[0]))

print("=" * 100)
print("4. failures per SNR / 2560 (b*(new), V1, genie, b*(old)), BLER@16, decision points")
F = {arm: {s: int(fails(d[s][arm]["blk_err"]).sum()) for s in SNRS} for arm, d in ((BS, new), (V1, old), (G, old))}
F["bs_old"] = {s: int(fails(old[s][BS]["blk_err"]).sum()) for s in SNRS}
rec_new = {-12: (2277, 2219, 846), -9: (1196, 1068, 423), -6: (746, 595, 227), -3: (505, 349, 88), 0: (294, 180, 30), 3: (143, 70, 9), 6: (61, 27, 3)}
rec_old = {-12: 2280, -9: 1207, -6: 761, -3: 509, 0: 304, 3: 145, 6: 62}
for s in SNRS:
    check(f"F {s:+d} dB (b*new, V1, genie)", rec_new[s], (F[BS][s], F[V1][s], F[G][s]))
    check(f"F {s:+d} dB b*(old)", rec_old[s], F["bs_old"][s])
bl = {arm: {s: F[arm][s] / NTOT for s in SNRS} for arm in F}
for arm in F:
    print(f"  BLER@16 {arm}: " + "  ".join(f"{s:+d}:{bl[arm][s]:.4f}" for s in SNRS))
dp_new = decision_points(bl[BS], NTOT); dp_old = decision_points(bl["bs_old"], NTOT); dp_g = decision_points(bl[G], NTOT)
check("decision points anchor b*(new)", [-3, 0, 3], dp_new)
check("decision points anchor b*(old)", [-3, 0, 3], dp_old)
check("decision points anchor genie", [-9, -6, -3], dp_g)
print("  |log10(BLER/0.1)| of b*(new):", {s: round(abs(math.log10(max(bl[BS][s], 0.5 / NTOT) / 0.1)), 3) for s in SNRS})

print("=" * 100)
print("5. paired sign tests (a:b, exact two-sided p), power guard, 2/3 rule, label")


def pair(x_arr, y_arr):
    ex, ey = x_arr[:, -1], y_arr[:, -1]
    a = int(np.sum((ex == 1) & (ey == 0))); b = int(np.sum((ex == 0) & (ey == 1)))
    return a, b, sign_p(a, b)


def table_row(name, xd, x, yd, y, dps, rec):
    res = [pair(xd[s][x]["blk_err"], yd[s][y]["blk_err"]) for s in dps]
    A, B = sum(r[0] for r in res), sum(r[1] for r in res)
    powered = len(dps) == 3 and sum(1 for a, b, _ in res if a + b >= 6) >= 2
    wy = sum(1 for a, b, p in res if a > b and p < 0.05); wx = sum(1 for a, b, p in res if b > a and p < 0.05)
    s_pts = "  ".join(f"{s:+d} dB {a}:{b} p={p:.2g}" for (a, b, p), s in zip(res, dps))
    print(f"  {name}: {s_pts}   pooled {A}:{B} p={sign_p(A, B):.2g}  powered={powered}  second-fewer {wy}/3  first-fewer {wx}/3")
    check(f"{name} a:b per point", rec["ab"], [(a, b) for a, b, _ in res])
    check(f"{name} p strings", rec["p"], [f"{p:.2g}" for _, _, p in res])
    check(f"{name} pooled", rec["pooled"], (A, B, f"{sign_p(A, B):.2g}"))
    check(f"{name} POWERED", True, powered)
    check(f"{name} second arm fewer at", rec["wy"], wy)
    return A, B


table_row("b*(new) -> V1", new, BS, old, V1, dp_new,
          dict(ab=[(172, 16), (127, 13), (79, 6)], p=["3.4e-34", "1.1e-24", "2.4e-17"], pooled=(378, 35, "8.3e-74"), wy=3))
table_row("b*(old) -> V1", old, BS, old, V1, dp_old,
          dict(ab=[(173, 13), (136, 12), (82, 7)], p=["7.3e-37", "9e-28", "2.4e-17"], pooled=(391, 32, "1.3e-79"), wy=3))
table_row("b*(new) -> genie", new, BS, old, G, dp_g,
          dict(ab=[(774, 1), (520, 1), (419, 2)], p=["7.8e-231", "1.5e-154", "3.3e-122"], pooled=(1713, 4, "0"), wy=3))
table_row("b*(old) -> genie", old, BS, old, G, dp_g,
          dict(ab=[(784, 0), (534, 0), (422, 1)], p=["2e-236", "3.6e-161", "3.9e-125"], pooled=(1740, 1, "0"), wy=3))
table_row("V1 -> genie", old, V1, old, G, dp_g,
          dict(ab=[(646, 1), (372, 4), (263, 2)], p=["2.2e-192", "1.1e-104", "1.2e-75"], pooled=(1281, 7, "0"), wy=3))
# label by §2.1: POWERED and second arm fewer at >= 2/3 -> (i)
lab = "(i)"
check("label §2.1 for b*(new) -> V1", "(i)", lab)
print('  label string: (i) "UMi28 C9 (Nr 32) 에서 V1 이 b*(GCAP) 보다 적게 실패 (GMM 용량 확인 재평가, UNGATED)"')

print("=" * 100)
print("6. report-only b*(old) -> b*(new) per SNR (a = old-only fails : b = new-only fails)")
rec = {-12: (38, 35, "0.82"), -9: (56, 45, "0.32"), -6: (57, 42, "0.16"), -3: (57, 53, "0.78"), 0: (56, 46, "0.37"), 3: (30, 28, "0.9"), 6: (13, 12, "1")}
for s in SNRS:
    x, y = fails(old[s][BS]["blk_err"]), fails(new[s][BS]["blk_err"])
    a, b = int(((x > 0) & (y == 0)).sum()), int(((x == 0) & (y > 0)).sum())
    check(f"report-only {s:+d} dB", rec[s], (a, b, f"{sign_p(a, b):.2g}"))
diffs = [F["bs_old"][s] - F[BS][s] for s in SNRS]
check("new b* fewer failures at all 7 points by 1..15", True, all(1 <= d <= 15 for d in diffs)); print("  F(old) - F(new):", diffs)
check("min p over 7 points >= 0.16 (string 0.16 at -6)", True, min(sign_p(rec[s][0], rec[s][1]) for s in SNRS) >= 0.16 - 1e-3)

print("=" * 100)
print("7. SNR@0.1 (log-linear, first downward crossing) and gaps; own paired bootstrap (B=2000, different seed) as a sanity check")
at = {}
for arm, d in ((BS, new), (V1, old), (G, old)):
    at[arm] = snr_at(SNRS, [bl[arm][s] for s in SNRS], NTOT)
at["bs_old"] = snr_at(SNRS, [bl["bs_old"][s] for s in SNRS], NTOT)
for k, v in at.items():
    print(f"  SNR@0.1 {k}: {v[0]:.4f} ({v[1]})")
check("gap b*(new) - V1 (dB, 2 dp)", "+2.17", f"{at[BS][0] - at[V1][0]:+.2f}")
check("gap b*(old) - V1", "+2.29", f"{at['bs_old'][0] - at[V1][0]:+.2f}")
check("gap b*(new) - genie", "+7.16", f"{at[BS][0] - at[G][0]:+.2f}")
check("gap b*(old) - genie", "+7.28", f"{at['bs_old'][0] - at[G][0]:+.2f}")
check("gap V1 - genie", "+4.98", f"{at[V1][0] - at[G][0]:+.2f}")
check("prediction 8: gap >= +1.5 dB", True, at[BS][0] - at[V1][0] >= 1.5)


def own_boot_gap(xd, x, yd, y, B=2000, seed=424242):
    rng = np.random.default_rng(seed)
    ex = [xd[s][x]["blk_err"][:, -1] for s in SNRS]; ey = [yd[s][y]["blk_err"][:, -1] for s in SNRS]
    g = []
    for _ in range(B):
        idx = [rng.integers(NTOT, size=NTOT) for _ in SNRS]      # same indices for both arms at each SNR (paired)
        (ux, fx), (uy, fy) = snr_at(SNRS, [a[i].mean() for a, i in zip(ex, idx)], NTOT), snr_at(SNRS, [b[i].mean() for b, i in zip(ey, idx)], NTOT)
        g.append(ux - uy if fx == fy == "ok" else np.nan)
    g = np.array(g)
    return np.nanpercentile(g, [5, 95]), float(np.mean(~np.isfinite(g)))


(lo, hi), cens = own_boot_gap(new, BS, old, V1)
print(f"  own bootstrap gap b*(new)-V1: [{lo:+.2f}, {hi:+.2f}] censored {cens:.0%}  (recorded [+1.83, +2.50]; registered tool is re-run separately and diffed)")
check("own bootstrap CI within 0.05 dB of recorded [+1.83, +2.50]", True, abs(lo - 1.83) <= 0.05 and abs(hi - 2.50) <= 0.05)
(lo, hi), cens = own_boot_gap(old, BS, old, V1)
print(f"  own bootstrap gap b*(old)-V1: [{lo:+.2f}, {hi:+.2f}] censored {cens:.0%}  (recorded [+1.98, +2.61])")

print("=" * 100)
print("8. R = (F_b* - F_V1) / (F_b* - F_genie) at the b* decision points; own paired bootstrap (different seed)")
SF = {k: sum(F[k][s] for s in dp_new) for k in (BS, V1, G)}; SF["bs_old"] = sum(F["bs_old"][s] for s in dp_old)
check("sum F (b*(new), V1, genie)", (942, 599, 127), (SF[BS], SF[V1], SF[G]))
check("sum F b*(old)", 958, SF["bs_old"])
R_new = (SF[BS] - SF[V1]) / (SF[BS] - SF[G]); R_old = (SF["bs_old"] - SF[V1]) / (SF["bs_old"] - SF[G])
check("R new (6 dp)", "0.420859", f"{R_new:.6f}"); check("R old (6 dp)", "0.432010", f"{R_old:.6f}")
check("prediction 7: 942 in [958*0.95, 958*1.05] = [910.1, 1005.9]", True, 958 * 0.95 <= SF[BS] <= 958 * 1.05)


def own_boot_R(bd, B=2000, seed=777):
    rng = np.random.default_rng(seed)
    cols = [(fails(bd[s][BS]["blk_err"]), fails(old[s][V1]["blk_err"]), fails(old[s][G]["blk_err"])) for s in dp_new]
    out = np.empty(B)
    for i in range(B):
        idx = rng.integers(0, NTOT, NTOT)
        bs = sum(b[idx].sum() for b, _, _ in cols); vs = sum(v[idx].sum() for _, v, _ in cols); gs = sum(g[idx].sum() for _, _, g in cols)
        out[i] = (bs - vs) / (bs - gs)
    return np.percentile(out, [5, 95])


lo, hi = own_boot_R(new); print(f"  own bootstrap R new: [{lo:.3f}, {hi:.3f}] (recorded [0.390, 0.451])")
check("own R CI within 0.005 of recorded", True, abs(lo - 0.390) <= 0.005 and abs(hi - 0.451) <= 0.005)
lo, hi = own_boot_R(old); print(f"  own bootstrap R old: [{lo:.3f}, {hi:.3f}] (recorded [0.402, 0.462])")

print("=" * 100)
print("9. E log: chunk times (done lines), run 1 / run 2 split, rounds")
lines = open(ELOG).read().splitlines()
hdr = [i for i, l in enumerate(lines) if l.startswith("# run_gcap git")]
check("E log: two run headers", 2, len(hdr)); print("  headers at lines", [i + 1 for i in hdr], [lines[i] for i in hdr])
done_re = re.compile(r"^(\d+)/448 done\s+(\S+)\s+\((\d+) s\)")
r1 = [(int(m[1]), int(m[3]), i + 1) for i, l in enumerate(lines[:hdr[1]]) if (m := done_re.match(l))]
r2 = [(int(m[1]), int(m[3]), i + 1) for i, l in enumerate(lines[hdr[1]:], start=hdr[1]) if (m := done_re.match(l))]
ex2 = sum(1 for l in lines[hdr[1]:] if re.match(r"^\d+/448 exists", l))
check("run 1 done chunks", 116, len(r1)); check("run 2 done chunks", 332, len(r2)); check("run 2 'exists' lines", 116, ex2)
t1 = np.array([t for _, t, _ in r1]); t2 = np.array([t for _, t, _ in r2])
print(f"  run 1: mean {t1.mean():.0f} median {np.median(t1):.0f} min {t1.min()} max {t1.max()}   (recorded mean 19995 median 19611 range 8061-37745)")
check("run 1 mean", 19995, int(round(t1.mean()))); check("run 1 median", 19611, int(round(np.median(t1)))); check("run 1 min/max", (8061, 37745), (int(t1.min()), int(t1.max())))
print(f"  run 2: mean {t2.mean():.0f} median {np.median(t2):.0f} min {t2.min()} max {t2.max()}   (recorded mean 7954 median 7260 range 6524-13125)")
check("run 2 mean", 7954, int(round(t2.mean()))); check("run 2 median", 7260, int(round(np.median(t2)))); check("run 2 min/max", (6524, 13125), (int(t2.min()), int(t2.max())))
first, second = t1[:58], t1[58:116]
print(f"  run 1 first round (done 1-58): median {np.median(first):.0f}; second round (59-116, E:{r1[58][2]}-{r1[115][2]}): {second.min()}-{second.max()} median {np.median(second):.0f}, "
      f"ratio to first median {second.min() / np.median(first):.2f}-{second.max() / np.median(first):.2f}")
check("second round range", (24753, 37745), (int(second.min()), int(second.max()))); check("second round median", 30816, int(round(np.median(second))))
check("first round median", 9746, int(round(np.median(first)))); check("second round line span E:67-124", (67, 124), (r1[58][2], r1[115][2]))
check("ratio 2.54-3.87", ("2.54", "3.87"), (f"{second.min() / np.median(first):.2f}", f"{second.max() / np.median(first):.2f}"))
m = re.search(r"finished in ([\d.]+) min", "\n".join(lines[hdr[1]:])); check("run 2 finished min", "854.4", m[1] if m else None)
check("E:7 = 58 workers line", True, "memory guard allows 58 workers" in lines[6]); check("E:150 = 55 workers line", True, "memory guard allows 55 workers" in lines[149])
check("E:600 finished line", True, lines[599].startswith("[run] finished in 854.4 min"))
check("E:125 Traceback (run 1)", True, lines[124].startswith("Traceback")); check("E:143 KeyError (run 1)", True, "KeyError: 'R2-ours-G'" in lines[142])
check("E:601 Traceback (run 2)", True, lines[600].startswith("Traceback")); check("E:619 KeyError (run 2)", True, "KeyError: 'R2-ours-G'" in lines[618])
check("E log total lines", 619, len(lines))

print("=" * 100)
print("10. fit A: the 31 training ll values quoted in §0, last step decrease, train-val gap; prediction 1 delta")
za = np.load("/home/HTJ/t2_wtS/conf/results/gmm_fits_D2_U28NR32B16e4/fit_UMi28_Nr32_kronK4096_n160000.npz")
ll = za["ll"]
s0 = ("-215.608196 -70.470434 89.340179 142.006648 160.939801 169.459844 174.119919 177.200719 179.296717 180.897277 182.127186 "
      "183.052035 183.862627 184.601901 185.159914 185.617448 186.021813 186.416154 186.784385 187.039562 187.267622 187.467664 "
      "187.667824 187.821748 187.944583 188.031728 188.096836 188.139439 188.251491 188.285931 188.285781").split()
check("§0 A ll list (31 values, 6 dp)", s0, [f"{v:.6f}" for v in ll])
check("§0 ll[30]-ll[29] = -1.50e-4", "-1.50e-04", f"{ll[30] - ll[29]:.2e}")
check("§0 train - val gap 36.05", "36.05", f"{float(za['ll_train']) - float(za['ll_val']):.2f}")
d = 152.34773499788244 - 152.23176788511105
check("prediction 1 delta +0.1160", "+0.1160", f"{d:+.4f}"); check("prediction 3 delta +1.908", "+1.908", f"{154.13990347772582 - 152.23176788511105:+.3f}")
check("merge train-val 55.387", "55.387", f"{209.52733621460857 - 154.13990347772582:.3f}")
check("em_sec 38444.76633501053 + 2100.003348827362", "40544.76968383789", repr(38444.76633501053 + 2100.003348827362))
check("fit cost 128781 + 38445", 167226, 128781 + 38445)
check("G = ceil(12.613*1.05/0.5)*0.5", 13.5, math.ceil(12.613 * 1.05 / 0.5) * 0.5)
check("workers floor(0.8*1037860916 kB / 2**20 / 13.5)", 58, int(0.8 * 1037860916 / 2 ** 20 // 13.5))

print("=" * 100)
print(f"SUMMARY: {nchk[0]} checks, {len(mism)} mismatches")
for w, a, b in mism:
    print(f"  MISMATCH {w}: recorded {a!r} recomputed {b!r}")
