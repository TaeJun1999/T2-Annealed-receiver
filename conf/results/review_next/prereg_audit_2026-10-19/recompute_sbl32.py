"""recompute_sbl32.py -- independent recomputation for the record audit of NEXT_EXPERIMENTS_U28NR32SBL (E3', UMi28 C9 32x4).

Reads the npz chunks directly with numpy.  Does NOT import conf/code or Demo (pair_baselines / analysis / select_dev are not
used); every rule of the registration (§1.2 selection, §1.3 / §2 table B: anchor decision points, exact two-sided sign test,
2/3 rule, power guard, label strings, SNR@0.1 log-linear interpolation with the 90 % paired bootstrap, R_X with its paired
bootstrap) is re-implemented here and the results are compared with the committed outputs
(pairB_U28NR32SBL.txt, pairB_U28NR32SBL_bstar.txt, select_dev_cold.out, select_dev_final.out, §5 / §6 of the registration).
Read-only; writes nothing but stdout (the caller tees recompute_sbl32.out) and recompute_sbl32.json next to it.
"""
import glob
import json
import math
import os
import re
import sys

import numpy as np

MAIN, WTS, WTE3 = "/home/HTJ/t2/conf", "/home/HTJ/t2_wtS/conf", "/home/HTJ/t2_wtE3/conf"
RN = os.path.join(MAIN, "results", "review_next")
HERE = os.path.dirname(os.path.abspath(__file__))
SNRS = [-12, -9, -6, -3, 0, 3, 6]
PAT = re.compile(r"D2_(C\d)_UMi28_Nr32_T16_Tp4_eig_snr(-?\d+)_skip(\d+)_n(\d+)\.npz$")
KEYS_RAW = ("blk_err", "ber", "nmse", "tauL_gmean", "alphaD", "tauL_clip_frac", "alphaD_clip")
V1, BSTAR, GENIE, SBL = "M-ours-dscore-C-V1", "M-ours-bstar", "R5-genie", "SBL-loop"
BASELINES = ("M-ours-bstar-scalar", "M-ours-gmm32", "R0-pilot", "R1-turbo", "R2-ours-G", "R3-bigamp", "R4-llr", "R4-scvamp",
             "bstar-pilot", "V1-pilot", "ALD-pilot", "ALDv-pilot", SBL)
MIN_DISC = 6
RESULT = {}
N_OK = N_BAD = 0
BADS = []


def cmp(name, got, want, tol=None):
    """count one comparison; strings compared exactly, numbers with |diff| <= tol (tol None -> exact)."""
    global N_OK, N_BAD
    ok = (got == want) if tol is None else (abs(float(got) - float(want)) <= tol)
    if ok:
        N_OK += 1
    else:
        N_BAD += 1
        BADS.append(f"{name}: recomputed {got!r} != recorded {want!r}")
    return ok


def sign_p(a, b):
    n = a + b
    if n == 0:
        return 1.0
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(min(a, b) + 1)) / (1 << n))   # exact big-int arithmetic (n up to 2612)


def fails(be):
    """blk_err@16 per trial -> 1.0 if failed (non-zero) or non-finite (raised), else 0.0."""
    v = np.asarray(be, dtype=float)[:, -1]
    return np.where(np.isfinite(v), (v != 0).astype(float), 1.0)


def snr_at(snrs, bler, n, target=0.1):
    lb = np.log10(np.maximum(np.asarray(bler, float), 0.5 / n)); lt = math.log10(target)
    if lb[0] <= lt:
        return snrs[0], "lo"
    for i in range(len(snrs) - 1):
        if lb[i] > lt >= lb[i + 1]:
            return snrs[i] + (lb[i] - lt) / (lb[i] - lb[i + 1]) * (snrs[i + 1] - snrs[i]), "ok"
    return snrs[-1], "hi"


# ----------------------------------------------------------------------------------------------------------------------------
# 1. loading (chunk plan, meta sets, per-arm concatenation in skip order)
# ----------------------------------------------------------------------------------------------------------------------------
def load_raw(root, cell="C9", keys=KEYS_RAW, extra_keys=("guardH",), want_plan=None, meta_keys=()):
    """-> arms[snr][arm][key] (concatenated in skip order), metas (dict key -> set of str), plans (snr -> [(skip, n)]), failed keys."""
    pts = {}
    for f in glob.glob(os.path.join(root, f"D2_{cell}_UMi28_Nr32_*.npz")):
        m = PAT.search(f); pts.setdefault(int(m[2]), []).append((int(m[3]), int(m[4]), f))
    arms, metas, plans, failed_keys, nonfinite = {}, {}, {}, [], {}
    for s in sorted(pts):
        ch = sorted(pts[s]); plans[s] = [(a, b) for a, b, _ in ch]
        if want_plan is not None and plans[s] != want_plan:
            raise SystemExit(f"{root} {s:+d} dB: chunk plan {plans[s][:3]}.. != expected")
        d = {}
        for skip, n, f in ch:
            with np.load(f, allow_pickle=False) as z:
                files = set(z.files)
                failed_keys += [f"{os.path.basename(f)}:{k}" for k in files if k.endswith("|failed")]
                for mk in meta_keys:
                    metas.setdefault(mk, set()).add(str(z[mk]) if mk in files else "(absent)")
                # run|skip / run|n / run|snr must agree with the file name
                if int(z["run|skip"]) != skip or int(z["run|n"]) != n or float(z["run|snr"]) != float(s):
                    raise SystemExit(f"{f}: run|skip/n/snr {z['run|skip']}/{z['run|n']}/{z['run|snr']} != file name")
                for k in files:
                    if "|" not in k or k.startswith(("meta|", "run|")):
                        continue
                    arm, q = k.split("|", 1)
                    if q in keys or q in extra_keys:
                        a = z[k]
                        if a.shape[0] != n:
                            raise SystemExit(f"{f}: {k} has {a.shape[0]} rows, chunk n = {n}")
                        d.setdefault(arm, {}).setdefault(q, []).append(a)
        arms[s] = {arm: {q: np.concatenate(v) for q, v in qa.items()} for arm, qa in d.items()}
        for arm in arms[s]:
            be = arms[s][arm].get("blk_err")
            if be is not None and not np.all(np.isfinite(be)):
                nonfinite[(s, arm)] = int((~np.isfinite(be[:, -1])).sum())
    return arms, metas, plans, failed_keys, nonfinite


def table_b(dat, x, y, snrs, fixed=None):
    """anchor rule on x (BLER@16 in [0.005, 0.9], 3 closest to 0.1 in |log10|), per-point exact sign test, power guard, label."""
    n = len(dat[snrs[0]][x]["blk_err"])
    bl = {s: max(fails(dat[s][x]["blk_err"]).mean(), 0.5 / n) for s in snrs}
    auto = sorted(sorted((s for s in snrs if 0.005 <= bl[s] <= 0.9), key=lambda s: abs(math.log10(bl[s] / 0.1)))[:3])
    cand = auto if fixed is None else fixed
    res = []
    for s in cand:
        fx, fy = fails(dat[s][x]["blk_err"]), fails(dat[s][y]["blk_err"])
        a = int(np.sum((fx == 1) & (fy == 0))); b = int(np.sum((fx == 0) & (fy == 1)))
        res.append((a, b, sign_p(a, b)))
    powered = len(cand) == 3 and sum(1 for a, b, _ in res if a + b >= MIN_DISC) >= 2
    wy = sum(1 for a, b, p in res if a > b and p < 0.05); wx = sum(1 for a, b, p in res if b > a and p < 0.05)
    lab = "(iv)" if not powered else "(i)" if wy >= 2 else "(ii)" if wx >= 2 else "(iii)"
    return dict(cand=cand, auto=auto, res=res, powered=powered, wy=wy, wx=wx, lab=lab, bl=bl)


def gain(dat, x, y, snrs, B=2000, seed=20260925):
    ex = [fails(dat[s][x]["blk_err"]) for s in snrs]; ey = [fails(dat[s][y]["blk_err"]) for s in snrs]
    n = min(len(e) for e in ex)
    (vx, fx), (vy, fy) = snr_at(snrs, [e.mean() for e in ex], n), snr_at(snrs, [e.mean() for e in ey], n)
    if fx == "hi" and fy == "ok":
        return dict(text=f">= {vx - vy:+.2f} dB ({x} never reaches 0.1 on the grid)", est=vx - vy, lo=None, hi=None, cens=None)
    if fx != "ok" or fy != "ok":
        return dict(text=f"n/a ({fx} vs {fy})", est=None, lo=None, hi=None, cens=None)
    rng = np.random.default_rng(seed); g = np.empty(B)
    for r in range(B):
        bx, by = [], []
        for a, b in zip(ex, ey):
            i = rng.integers(len(a), size=len(a)); bx.append(a[i].mean()); by.append(b[i].mean())
        (ux, gx), (uy, gy) = snr_at(snrs, bx, n), snr_at(snrs, by, n)
        g[r] = ux - uy if gx == gy == "ok" else np.nan
    cens = float(np.mean(~np.isfinite(g))); lo, hi = np.nanpercentile(g, [5, 95])
    return dict(text=f"{vx - vy:+.2f} dB  [90% paired bootstrap {lo:+.2f}, {hi:+.2f}; censored replicates {100 * cens:.0f}%]",
                est=vx - vy, lo=float(lo), hi=float(hi), cens=cens, sx=vx, sy=vy)


def gain_other_seed(dat, x, y, snrs, B=2000, seed=1):
    """robustness only: a different RNG seed / scheme (independent resampling per replicate, one index set shared by x and y)."""
    ex = [fails(dat[s][x]["blk_err"]) for s in snrs]; ey = [fails(dat[s][y]["blk_err"]) for s in snrs]; n = len(ex[0])
    rng = np.random.default_rng(seed); g = np.empty(B)
    for r in range(B):
        idx = [rng.integers(0, n, n) for _ in snrs]
        (ux, gx) = snr_at(snrs, [a[i].mean() for a, i in zip(ex, idx)], n)
        (uy, gy) = snr_at(snrs, [b[i].mean() for b, i in zip(ey, idx)], n)
        g[r] = ux - uy if gx == gy == "ok" else np.nan
    lo, hi = np.nanpercentile(g, [5, 95])
    return float(lo), float(hi)


def recovery(cols, B=2000, seed=20260926):
    """cols = [(F_X, F_V1, F_genie) arrays per SNR]; one resampled index set per replicate shared by all SNRs and arms."""
    X, V, G = (sum(c[i].sum() for c in cols) for i in range(3))
    R = (X - V) / (X - G) if X - G > 0 else float("nan")
    rng = np.random.default_rng(seed); n = len(cols[0][0]); out = np.empty(B)
    for r in range(B):
        idx = rng.integers(0, n, n)
        xs = sum(c[0][idx].sum() for c in cols); vs = sum(c[1][idx].sum() for c in cols); gs = sum(c[2][idx].sum() for c in cols)
        out[r] = (xs - vs) / (xs - gs) if xs - gs > 0 else np.nan
    ok = np.isfinite(out)
    lo, hi = np.percentile(out[ok], [5, 95]) if ok.sum() else (np.nan, np.nan)
    return R, float(lo), float(hi), int((~ok).sum())


def main():
    out = {}
    print("=" * 100); print("A. TEST RAW raw_U28NR32SBL (448 chunks) -- plan, meta, genie replay")
    plan = [(40 * k, 40) for k in range(64)]
    META = ("run|git", "meta|sparse", "meta|bstar", "meta|kron_K", "meta|ll_val|kron", "meta|worker_gb", "meta|jobs", "run|iters",
            "run|seed", "meta|ntrain", "meta|stagec_ckpt_id", "run|dtype", "run|beta", "run|t_in", "meta|em_sec")
    sbl, metas, plans, fk, nonfin = load_raw(os.path.join(MAIN, "raw_U28NR32SBL"), want_plan=plan, meta_keys=META)
    print(f"  SNR points {sorted(sbl)} (grid {SNRS}): {'OK' if sorted(sbl) == SNRS else 'MISMATCH'}")
    cmp("A.grid", sorted(sbl), SNRS)
    print(f"  chunk plan per SNR = {{(40k, 40): k = 0..63}}: OK for all {len(plans)} SNRs (checked at load)")
    cmp("A.plan", all(plans[s] == plan for s in SNRS), True)
    print(f"  '|failed' keys: {len(fk)}; non-finite blk_err@16 (raised trials): {nonfin if nonfin else 0}")
    cmp("A.failed_keys", len(fk), 0); cmp("A.raised", len(nonfin), 0)
    for k in META:
        print(f"  {k:<22} value set = {sorted(metas[k])}")
    want = {"run|git": {"13f05fb1"}, "meta|sparse": {'{"L": 1, "n_em": 3, "rho_omp": 1, "rho_sbl": 4}'}, "meta|bstar": {"kron"},
            "meta|kron_K": {"4096"}, "meta|ll_val|kron": {"152.23176788511105"}, "meta|worker_gb": {"7.0"}, "meta|jobs": {"96"},
            "run|iters": {"16"}, "run|seed": {"20260926"}, "meta|ntrain": {"160000.0"}, "meta|stagec_ckpt_id": {"(absent)"}}
    for k, w in want.items():
        cmp(f"A.meta {k}", metas[k], w)
    arms_sbl = sorted(sbl[-3])
    print(f"  arms in the SBL raw: {arms_sbl}")
    cmp("A.arms", arms_sbl, [GENIE, SBL])
    cmp("A.sparse_json", json.dumps(dict(rho_sbl=4, n_em=3, rho_omp=1, L=1), sort_keys=True), next(iter(metas["meta|sparse"])))

    base, bm, _, bfk, bnf = load_raw(os.path.join(WTS, "raw_U28NR32B16e4"), want_plan=plan, meta_keys=("run|git", "meta|stagec_ckpt_id", "meta|ll_val|kron", "meta|kron_K", "meta|bstar"))
    pil, pm, _, pfk, pnf = load_raw(os.path.join(WTS, "raw_PILU28NR32"), want_plan=plan, meta_keys=("run|git",))
    ald, am, _, afk, anf = load_raw(os.path.join(WTS, "raw_ALDU28NR32"), want_plan=plan, meta_keys=("run|git",))
    print(f"  reference raws: base run|git {sorted(bm['run|git'])} ckpt {sorted(bm['meta|stagec_ckpt_id'])} ll_val|kron {sorted(bm['meta|ll_val|kron'])}; "
          f"PIL {sorted(pm['run|git'])}; ALD {sorted(am['run|git'])}; failed keys {len(bfk) + len(pfk) + len(afk)}; raised {bnf or 0} {pnf or 0} {anf or 0}")
    cmp("A.base git", bm["run|git"], {"b4433d3c"}); cmp("A.pil git", pm["run|git"], {"b4433d3c"}); cmp("A.ald git", am["run|git"], {"b4433d3c"})
    cmp("A.ref failed keys", len(bfk) + len(pfk) + len(afk), 0)
    # genie replay: every key, every SNR, every trial (NaN == NaN) -- SBL raw vs base, and PIL / ALD vs base
    nv = 0; diffs = []
    for s in SNRS:
        for name, other in (("SBL", sbl), ("PIL", pil), ("ALD", ald)):
            for q in KEYS_RAW + ("guardH",):
                a, b = base[s][GENIE][q], other[s][GENIE][q]
                nv += a.size
                if a.shape != b.shape or not np.array_equal(a, b, equal_nan=True):
                    diffs.append((name, s, q))
    print(f"  R5-genie replay (7 KEYS_RAW + guardH, 7 SNR x 2560 trials, SBL / PIL / ALD vs base): {nv} values, differing arrays {diffs if diffs else 0}")
    cmp("A.genie replay", len(diffs), 0)
    out["genie_values_compared"] = nv

    # merge the arms the way the registration's analysis does (base loop arms + PIL + ALD + extra SBL raw)
    dat = {s: {**base[s], "V1-pilot": pil[s]["V1-pilot"], "bstar-pilot": pil[s]["bstar-pilot"],
               "ALD-pilot": ald[s]["ALD-pilot"], "ALDv-pilot": ald[s]["ALDv-pilot"], SBL: sbl[s][SBL]} for s in SNRS}
    for s in SNRS:
        for arm in dat[s]:
            if len(dat[s][arm]["blk_err"]) != 2560:
                raise SystemExit(f"{s} {arm}: {len(dat[s][arm]['blk_err'])} trials")
    # pilot@1 identities (pair_baselines integrity items, recomputed here)
    for x, y in (("V1-pilot", V1), ("bstar-pilot", BSTAR)):
        ok = all(np.array_equal(pil[s][x]["nmse"][:, 0], base[s][y]["nmse"][:, 0], equal_nan=True) for s in SNRS)
        print(f"  {x}@1 nmse == {y}@1 nmse at all 7 SNR: {ok}"); cmp(f"A.{x}@1", ok, True)

    # ------------------------------------------------------------------------------------------------------------------------
    print("=" * 100); print("B. FAILURE COUNTS @16 per SNR (-12 .. +6 dB) vs pairB_U28NR32SBL.txt lines 107-122")
    rec = open(os.path.join(RN, "pairB_U28NR32SBL.txt")).read().splitlines()
    rec_b = open(os.path.join(RN, "pairB_U28NR32SBL_bstar.txt")).read().splitlines()
    tab = {}
    i0 = next(i for i, l in enumerate(rec) if l.startswith("BLER@16 failures"))
    for l in rec[i0 + 1:]:
        if not l.startswith("    "):
            break
        p = l.split(); tab[p[0]] = [int(v) for v in p[1:]]
    F = {arm: [int(fails(dat[s][arm]["blk_err"]).sum()) for s in SNRS] for arm in tab}
    for arm in tab:
        ok = F[arm] == tab[arm]
        for s, g, w in zip(SNRS, F[arm], tab[arm]):
            cmp(f"B.F {arm} {s:+d}", g, w)
        print(f"  {arm:<22} {' '.join(f'{v:5d}' for v in F[arm])}   {'OK' if ok else 'MISMATCH ' + str(tab[arm])}")
    out["F"] = F
    # §6.2 / §0 sums
    dp = [-3, 0, 3]
    sums = {arm: sum(F[arm][SNRS.index(s)] for s in dp) for arm in (BSTAR, V1, GENIE, SBL)}
    print(f"  decision-point (-3/0/+3) sums: b* {sums[BSTAR]} V1 {sums[V1]} genie {sums[GENIE]} SBL-loop {sums[SBL]}  (§0: 958 / 599 / 127)")
    cmp("B.sum b*", sums[BSTAR], 958); cmp("B.sum V1", sums[V1], 599); cmp("B.sum genie", sums[GENIE], 127)

    # ------------------------------------------------------------------------------------------------------------------------
    print("=" * 100); print("C. TABLE B X -> V1 for b* + 13 baselines (anchor rule, exact sign test, power guard, label, SNR@0.1 gap, R_X)")
    # parse the committed blocks
    blocks = {}
    for i, l in enumerate(rec):
        m = re.match(r"^(\S+) -> (\S+)  \[anchor (\S+)\]  decision SNRs (\[.*\])$", l)
        if m:
            blocks[(m[1], m[2])] = rec[i:i + 7]
    for i, l in enumerate(rec_b):
        m = re.match(r"^(\S+) -> (\S+)  \[anchor (\S+)\]  decision SNRs (\[.*\])$", l)
        if m:
            blocks[(m[1], m[2])] = rec_b[i:i + 5]
    labs = {}
    rows = []
    for x in (BSTAR,) + BASELINES:
        t = table_b(dat, x, V1, SNRS)
        g = gain(dat, x, V1, SNRS)
        A, Bn = sum(r[0] for r in t["res"]), sum(r[1] for r in t["res"])
        labs[x] = t["lab"]
        blk = blocks[(x, V1)]
        rc = eval(blk[0].split("decision SNRs ")[1])
        cmp(f"C.{x} decision SNRs", [f"{s:+.0f}" for s in t["cand"]], rc)
        st = "    sign test @16: " + "  ".join(f"{s:+.0f} dB {a}:{b} p={p:.2g}" for s, (a, b, p) in zip(t["cand"], t["res"])) + f"   pooled {A}:{Bn} p={sign_p(A, Bn):.2g}"
        cmp(f"C.{x} sign-test line", st, blk[1])
        pw = f"    POWERED={t['powered']}  second arm fewer at {t['wy']}/{len(t['cand'])}, first arm fewer at {t['wx']}/{len(t['cand'])}  -> {t['lab']}"
        cmp(f"C.{x} power/label line", pw, blk[2])
        gl = f"    SNR@0.1 gap ({x} minus V1): {g['text']}"
        cmp(f"C.{x} gap line", gl, blk[3])
        fx, fv, fg = (fails(dat[-3][arm]["blk_err"]) for arm in (x, V1, GENIE))
        ag = f"    absolute gap -3 dB: F_X - F_V1 = {int(fx.sum() - fv.sum())} blocks of {len(fx)}"
        cmp(f"C.{x} absolute gap line", ag, blk[4])
        bl = fx.mean()
        if not (0.005 <= bl <= 0.9) or fx.sum() <= fg.sum():
            r1 = "undefined (out of range: -3 dB BLER %.4f, F_X %d, F_genie %d)" % (bl, fx.sum(), fg.sum())
        else:
            R, lo, hi, nn = recovery([(fx, fv, fg)])
            r1 = f"{R:.3f} [90% {lo:.3f}, {hi:.3f}]" + (f" ({nn} undefined replicates)" if nn else "")
        cmp(f"C.{x} R_X -3 line", f"    R_X -3 dB (primary): {r1}", blk[5])
        cols2 = [tuple(fails(dat[s][arm]["blk_err"]) for arm in (x, V1, GENIE)) for s in t["cand"]]
        R2, lo2, hi2, nn2 = recovery(cols2)
        r2 = f"{R2:.3f} [90% {lo2:.3f}, {hi2:.3f}] over {len(t['cand'])} point(s)" + (f" ({nn2} undefined)" if nn2 else "")
        cmp(f"C.{x} R_X dp line", f"    R_X decision points (secondary): {r2}", blk[6])
        rows.append((x, int(fx.sum()), t["lab"]))
        print(f"  {x:<20} dp {[f'{s:+.0f}' for s in t['cand']]} " + " ".join(f"{a}:{b}(p={p:.2g})" for a, b, p in t["res"])
              + f" pooled {A}:{Bn} POWERED={t['powered']} wy {t['wy']} wx {t['wx']} -> {t['lab']} | gap {g['text'][:60]} | R-3 {r1[:28]}")
        if x == SBL:
            out["sbl_v1"] = dict(cand=t["cand"], res=t["res"], pooled=(A, Bn, sign_p(A, Bn)), lab=t["lab"], gap=g, r1=r1, r2=r2,
                                 bler=[float(fails(dat[s][SBL]["blk_err"]).mean()) for s in SNRS],
                                 logdist={s: abs(math.log10(t["bl"][s] / 0.1)) for s in SNRS})
            lo_o, hi_o = gain_other_seed(dat, x, V1, SNRS)
            print(f"    robustness (different seed/scheme, report only): SNR@0.1 gap 90% CI [{lo_o:+.2f}, {hi_o:+.2f}]")
            out["sbl_v1"]["gap_other_seed"] = (lo_o, hi_o)
            print(f"    anchor |log10(BLER/0.1)| per SNR: " + " ".join(f"{s:+d}:{abs(math.log10(t['bl'][s] / 0.1)):.3f}" for s in SNRS)
                  + f"  (BLER -12 dB {t['bl'][-12]:.4f} > 0.9 -> excluded)")
    k = sum(1 for x in labs if labs[x] == "(i)"); mm = sum(1 for x in labs if labs[x] == "(ii)")
    kB = k - (labs[BSTAR] == "(i)")
    s1 = f"SUMMARY-B (baselines without b*, {len(BASELINES)}): (i) {kB}, (ii) {mm - (labs[BSTAR] == '(ii)')}, not decided {len(BASELINES) - kB - (mm - (labs[BSTAR] == '(ii)'))}; b* -> V1 {labs[BSTAR]}"
    cmp("C.SUMMARY-B", s1, next(l for l in rec if l.startswith("SUMMARY-B")))
    s2 = f"SUMMARY registered baselines {len(labs)} (b* + 𝔅 {len(BASELINES)}): (i) {k}, (ii) {mm}, not decided {len(labs) - k - mm}"
    cmp("C.SUMMARY", s2, next(l for l in rec if l.startswith("SUMMARY registered")))
    xs = min(rows, key=lambda r: (r[1], r[0]))
    fx, fv, fg = (fails(dat[-3][arm]["blk_err"]) for arm in (xs[0], V1, GENIE))
    ok_range = 0.005 <= fx.mean() <= 0.9 and fx.sum() > fg.sum() and fg.sum() < fails(dat[-3][V1]["blk_err"]).sum()
    R, lo, hi, nn = recovery([(fx, fv, fg)])
    xl = f"X* (fewest -3 dB failures, ties by name) = {xs[0]} (F={xs[1]}); R_X* -3 dB = {R:.3f} [90% {lo:.3f}, {hi:.3f}]"
    cmp("C.X*", xl, next(l for l in rec if l.startswith("X* (fewest")))
    cond = k == len(labs) and mm == 0 and ok_range and lo > 0
    cl = f"'등록된 baseline 전부와 멀어진다' condition (k = {len(labs)}, (ii) = 0, R_X* CI lower > 0): {'MET' if cond else 'NOT met'}"
    cmp("C.condition", cl, next(l for l in rec if l.startswith("'등록된")))
    print(f"  {s1}\n  {s2}\n  {xl}\n  {cl}")
    out["labels"] = labs

    # ------------------------------------------------------------------------------------------------------------------------
    print("=" * 100); print("D. REPORT-ONLY b* -> SBL-loop (pairB_U28NR32SBL_bstar.txt)")
    t = table_b(dat, BSTAR, SBL, SNRS); g = gain(dat, BSTAR, SBL, SNRS)
    A, Bn = sum(r[0] for r in t["res"]), sum(r[1] for r in t["res"])
    blk = blocks[(BSTAR, SBL)]
    cmp("D.decision SNRs", [f"{s:+.0f}" for s in t["cand"]], eval(blk[0].split("decision SNRs ")[1]))
    st = "    sign test @16: " + "  ".join(f"{s:+.0f} dB {a}:{b} p={p:.2g}" for s, (a, b, p) in zip(t["cand"], t["res"])) + f"   pooled {A}:{Bn} p={sign_p(A, Bn):.2g}"
    cmp("D.sign-test line", st, blk[1])
    cmp("D.power line", f"    POWERED={t['powered']}  second arm fewer at {t['wy']}/{len(t['cand'])}, first arm fewer at {t['wx']}/{len(t['cand'])}  -> {t['lab']}", blk[2])
    cmp("D.gap line", f"    SNR@0.1 gap ({BSTAR} minus {SBL}): {g['text']}", blk[3])
    fl = "    failures@16 at the decision SNRs: " + "  ".join(f"{arm} " + "/".join(str(int(fails(dat[s][arm]["blk_err"]).sum())) for s in t["cand"]) for arm in (BSTAR, SBL))
    cmp("D.failures line", fl, blk[4])
    print(f"  dp {t['cand']} " + " ".join(f"{a}:{b}(p={p:.2g})" for a, b, p in t["res"]) + f" pooled {A}:{Bn}; b* fewer at {t['wx']}/3 points (mechanical label {t['lab']}, NOT attached per §1.3); gap {g['text']}")
    print(f"  {fl.strip()}")
    out["bstar_sbl"] = dict(cand=t["cand"], res=t["res"], pooled=(A, Bn), gap=g["text"])

    # ------------------------------------------------------------------------------------------------------------------------
    print("=" * 100); print("E. REPORT-ONLY median NMSE@16 (pairB lines 124-138)")
    i0 = next(i for i, l in enumerate(rec) if l.startswith("report-only, median NMSE"))
    for l in rec[i0 + 1:]:
        if not l.startswith("    "):
            break
        p = l.split(); arm = p[0]; want_v = p[1:]
        got = [f"{np.nanmedian(np.asarray(dat[s][arm]['nmse'])[:, -1]):.2e}" for s in SNRS]
        for s, gv, wv in zip(SNRS, got, want_v):
            cmp(f"E.nmse {arm} {s:+d}", gv, wv)
        print(f"  {arm:<20} {' '.join(got)}  {'OK' if got == want_v else 'MISMATCH'}")

    # ------------------------------------------------------------------------------------------------------------------------
    print("=" * 100); print("F. DEVELOPMENT SELECTION (worktree t2_wtE3 raw_U28NR32SBLd_*; §1.2 rules re-applied; vs select_dev_*.out and §5)")
    SEC = {(4, 3): 4.765, (4, 10): 12.398, (4, 25): 39.051, (8, 3): 33.897, (8, 10): 43.338, (8, 25): 122.003, (16, 3): 124.065, (16, 10): 295.339}
    # probe.out re-read: the SEC table must equal the probe file
    probe = {}
    for l in open(os.path.join(RN, "sbl32", "probe.out")):
        m = re.match(r"rho=(\d+) n_em=(\d+): ([\d.]+) s/block; 16 sites; ([\d.]+) MiB", l)
        if m:
            probe[(int(m[1]), int(m[2]))] = (float(m[3]), float(m[4]))
    for key, sec in SEC.items():
        cmp(f"F.probe {key}", probe[key][0], sec, 1e-9)
    cmp("F.probe (16,25) excluded by time", probe[(16, 25)][0] * 17920 / 96 > 30 * 3600, True)
    print(f"  probe.out: {len(probe)} rows; 30 h screen = block > {30 * 3600 * 96 / 17920:.1f} s -> excluded {[k for k, v in probe.items() if v[0] * 17920 / 96 > 30 * 3600]} "
          f"({probe[(16, 25)][0] * 17920 / 96 / 3600:.1f} h); max RSS range {min(v[1] for v in probe.values()):.1f}-{max(v[1] for v in probe.values()):.1f} MiB")
    dplan = [(3840 + 10 * k, 10) for k in range(32)]
    cands = [(r, e, w) for (r, e) in SEC for w in (False, True) if (not w) or (r, e) in ((4, 3), (8, 3))]
    drows, dgenie = [], None
    for r, e, w in cands:
        tag = f"U28NR32SBLd_r{r}e{e}" + ("w" if w else "")
        d, m, pl, fk2, nf2 = load_raw(os.path.join(WTE3, f"raw_{tag}"), want_plan=dplan, meta_keys=("run|git", "meta|sparse", "run|iters"))
        if sorted(d) != [-3, 0, 3]:
            raise SystemExit(f"{tag}: SNRs {sorted(d)}")
        want_sp = json.dumps(dict(rho_sbl=r, n_em=e, rho_omp=1, L=1, **({"warm": True} if w else {})), sort_keys=True)
        cmp(f"F.{tag} meta|sparse", m["meta|sparse"], {want_sp}); cmp(f"F.{tag} run|git one value", len(m["run|git"]), 1)
        cmp(f"F.{tag} run|iters", m["run|iters"], {"16"}); cmp(f"F.{tag} failed keys", len(fk2), 0)
        gcat = np.concatenate([np.r_[d[s][GENIE][q].ravel()] for s in (-3, 0, 3) for q in KEYS_RAW])
        if dgenie is None:
            dgenie = gcat
        cmp(f"F.{tag} genie identical to first candidate", bool(np.array_equal(gcat, dgenie, equal_nan=True)), True)
        Fs = [int(fails(d[s][SBL]["blk_err"]).sum()) for s in (-3, 0, 3)]
        raised = [int((~np.isfinite(d[s][SBL]["blk_err"][:, -1])).sum()) for s in (-3, 0, 3)]
        drows.append(dict(tag=tag, rho=r, n_em=e, warm=w, F=Fs, Fsum=sum(Fs), metric=sum(Fs) / 960, raised=raised, sec=SEC[(r, e)], git=next(iter(m["run|git"]))))
    key = lambda x: (x["Fsum"], x["sec"], x["warm"])
    cold = sorted((x for x in drows if not x["warm"]), key=key)
    top2 = [(x["rho"], x["n_em"]) for x in cold[:2]]
    final = sorted(drows, key=key); pick = final[0]
    edge = [ax for ax, hit in (("rho", pick["rho"] in (4, 16)), ("n_em", pick["n_em"] in (3, 25)), ("rho16-column max n_em (time screen)", (pick["rho"], pick["n_em"]) == (16, 10))) if hit]
    # compare with the committed outputs line by line (same print format as select_dev.py)
    fmt = lambda x: f"{x['tag']:<22} F(-3,0,+3) {x['F']!r} sum {x['Fsum']!r} metric {x['metric']!r} raised {x['raised']!r} probe_sec {x['sec']!r} git {x['git']}"
    rc_cold = open(os.path.join(RN, "sbl32", "select_dev_cold.out")).read().splitlines()
    rc_final = open(os.path.join(RN, "sbl32", "select_dev_final.out")).read().splitlines()
    for i, x in enumerate(cold):
        cmp(f"F.cold line {i}", fmt(x), rc_cold[i])
    cmp("F.TOP2 line", "TOP2 (cold, warm variants to run): " + " ".join(f"{r},{e}" for r, e in top2), rc_cold[8])
    for i, x in enumerate(final):
        cmp(f"F.final line {i}", fmt(x), rc_final[i])
    pl = f"PICK {pick['tag']} rho {pick['rho']} n_em {pick['n_em']} warm {pick['warm']} metric {pick['metric']!r} range_edge {edge if edge else 'none'}"
    cmp("F.PICK line", pl, rc_final[10])
    for x in final:
        print("  " + fmt(x))
    print(f"  TOP2 {top2}; {pl}")
    gits = {x["tag"]: x["git"] for x in drows}
    cmp("F.git cold 7 = d3993c8d", {g for t_, g in gits.items() if not t_.endswith("w") and t_ != "U28NR32SBLd_r16e10"}, {"d3993c8d"})
    cmp("F.git r16e10 = 79ea962c", gits["U28NR32SBLd_r16e10"], "79ea962c")
    cmp("F.git warm = fe7e911b", {gits["U28NR32SBLd_r4e3w"], gits["U28NR32SBLd_r8e3w"]}, {"fe7e911b"})
    # §3 prediction 1 (strict inequalities)
    Fcol = {(x["rho"], x["n_em"]): x["Fsum"] for x in cold}
    p1 = (Fcol[(4, 3)] > Fcol[(8, 3)] > Fcol[(16, 3)]) and (Fcol[(4, 10)] > Fcol[(8, 10)] > Fcol[(16, 10)]) and (Fcol[(4, 25)] > Fcol[(8, 25)])
    print(f"  prediction 1 (rho larger -> fewer dev failures, strict): n_em3 {Fcol[(4, 3)]},{Fcol[(8, 3)]},{Fcol[(16, 3)]}  n_em10 {Fcol[(4, 10)]},{Fcol[(8, 10)]},{Fcol[(16, 10)]}  "
          f"n_em25 {Fcol[(4, 25)]},{Fcol[(8, 25)]} -> {'적중' if p1 else '빗나감'}")
    cmp("F.prediction1 = 빗나감", p1, False)
    warm_best = min(x["Fsum"] for x in drows if x["warm"])
    print(f"  prediction 2 (pick is cold): pick warm={pick['warm']} (best warm sum {warm_best} vs cold best {cold[0]['Fsum']}) -> {'적중' if not pick['warm'] else '빗나감'}")
    cmp("F.prediction2 = 적중", pick["warm"], False)
    cmp("F.prediction3 = 적중 (i)", labs[SBL], "(i)")
    cmp("F.prediction4 = 적중 (b* fewer 3/3)", out["bstar_sbl"]["res"][0][0] < out["bstar_sbl"]["res"][0][1] and all(a < b for a, b, _ in out["bstar_sbl"]["res"]), True)
    out["dev"] = drows; out["top2"] = top2; out["pick"] = pick["tag"]; out["edge"] = edge
    # dev / test separation: every chunk of every dev / smoke / merge raw starts at >= 2560
    mins = {}
    for root in glob.glob(os.path.join(WTE3, "raw_U28NR32SBL*")) + [os.path.join(MAIN, "raw_U28NR32SBLmrg")]:
        sk = [int(PAT.search(f)[3]) for f in glob.glob(os.path.join(root, "D2_C9_*.npz"))]
        mins[os.path.basename(root)] = (min(sk), max(sk), len(sk))
    print("  dev / smoke / merge raws (min skip, max skip, chunks): " + ", ".join(f"{k} {v}" for k, v in sorted(mins.items())))
    cmp("F.all dev raws start >= 2560", all(v[0] >= 2560 for v in mins.values()), True)
    # any other C9 UMi28 32x4 raw holding an SBL arm?  (first and last chunk's key set of every C9 raw in the trees)
    holders = []
    for tree in (MAIN, WTS, WTE3, "/home/HTJ/t2_wtE5/conf"):
        for root in sorted(glob.glob(os.path.join(tree, "raw_*"))):
            fs = sorted(glob.glob(os.path.join(root, "D2_C9_UMi28_Nr32_*.npz")))
            if not fs:
                continue
            arms_ = set()
            for f in (fs[0], fs[-1]):
                with np.load(f, allow_pickle=False) as z:
                    arms_ |= {k.split("|")[0] for k in z.files if "|" in k and not k.startswith(("meta|", "run|"))}
            if SBL in arms_ or "SBL-pilot" in arms_ or "OMP-pilot" in arms_:
                sk = [int(PAT.search(f)[3]) for f in fs]
                holders.append((root.replace("/home/HTJ/", ""), min(sk), max(sk), len(fs)))
    print("  C9 raws holding an SBL/OMP arm (root, min skip, max skip, chunks):")
    for h in holders:
        print(f"    {h}")
    test_holders = [h for h in holders if h[1] < 2560]
    cmp("F.only the test run holds SBL arms at trials < 2560", [h[0] for h in test_holders], ["t2/conf/raw_U28NR32SBL"])
    out["sbl_holders"] = holders

    # ------------------------------------------------------------------------------------------------------------------------
    print("=" * 100); print("G. ARITHMETIC OF §5 / §1.2 (worker count, time screen, G)")
    cmp("G.G = ceil05(6.580*1.05)", math.ceil(6.580 * 1.05 / 0.5) * 0.5, 7.0, 1e-12)
    cmp("G.workers floor(0.8*MemAvail/G)", int(0.8 * (1003263876 / 1048576) / 7.0), 109)
    cmp("G.estimate 5 x 108 s", math.ceil(448 / 96) * 108, 540)
    print(f"  6.580 x 1.05 = {6.580 * 1.05:.3f} -> G 7.0; floor(0.8 x {1003263876 / 1048576:.1f} GiB / 7) = {int(0.8 * (1003263876 / 1048576) / 7.0)}; ceil(448/96) x 108 = {math.ceil(448 / 96) * 108} s")

    print("=" * 100)
    print(f"COMPARISONS: {N_OK} match, {N_BAD} mismatch")
    for b in BADS:
        print("  MISMATCH " + b)
    json.dump(out, open(os.path.join(HERE, "recompute_sbl32.json"), "w"), indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))


if __name__ == "__main__":
    main()
