"""Independent re-derivation of every number quoted in NEXT_EXPERIMENTS_SCALE16e4.md §6.1 (lines 418-741), the matching
docs/EXPERIMENTS.md row and the DECISIONS line (record audit 2026-10-03, Fable 5.1; precedent prereg_audit_2026-10-01/
sparse_recompute.py, prereg_audit_2026-09-28/recompute.py whose own raw reader / table-B / bootstrap code is reused here).

Reads ONLY raw npz chunks, checkpoints, fit files, results/ald/*, logs, the result text files (to COMPARE against) and git.
The raw reader, decision points, sign test (house exact formula), SNR@0.1 gap (paired bootstrap, seed 20260925), genie-gap
recovery R (paired bootstrap, seed 20260926, recovery_ci draw order), the UNPAIRED frontier ΔR / Q-K R+ / Q-OP R* (frontier_ci
draw order: one index draw per (raw, cell, SNR) per replicate, own Resampler for R*) are re-implemented from the registration's
written definitions -- analysis.py / recovery_ci.py / frontier_ci.py / pair_baselines.py / eval_accept.py are NOT called.

    OMP_NUM_THREADS=2 CUDA_VISIBLE_DEVICES= ~/miniforge3/envs/torch/bin/python \
        results/review_next/prereg_audit_2026-10-03/scale_recompute.py > .../scale_recompute.out 2> .../scale_recompute.err
"""
import glob
import hashlib
import json
import os
import re
import subprocess
import sys
from math import comb

import numpy as np

CONF = "/home/HTJ/t2_wtS/conf"
T2W = "/home/HTJ/t2_wtS"
RN = os.path.join(CONF, "results/review_next")
V1, BSTAR, GENIE = "M-ours-dscore-C-V1", "M-ours-bstar", "R5-genie"
KEYS_RAW = ("blk_err", "ber", "nmse", "tauL_gmean", "alphaD", "tauL_clip_frac", "alphaD_clip")
KEYS4 = ("blk_err", "ber", "tauL_gmean", "alphaD")
B = 2000
SEED = 20260926
PAT = re.compile(r"^D2_(C\d)_([A-Za-z0-9]+)_Nr(\d+)_T(\d+)_Tp(\d+)_(dft|eig)_snr(-?\d+)_skip(\d+)_n(\d+)\.npz$")
BASELINES = ("M-ours-bstar-scalar", "M-ours-gmm32", "R0-pilot", "R1-turbo", "R2-ours-G", "R3-bigamp", "R4-llr", "R4-scvamp",
             "bstar-pilot", "V1-pilot", "ALD-pilot", "ALDv-pilot")
AARMS = ("M-ours-dscore-C-V1", "M-ours-bstar", "M-ours-bstar-scalar", "M-ours-gmm32", "R0-pilot", "R1-turbo", "R2-ours-G",
         "R3-bigamp", "R4-llr", "R4-scvamp", "R5-genie")
CHECKS = [0, 0]           # [n, mismatches]
MIS = []


def P(*a):
    print(*a, flush=True)


def chk(name, got, exp, show=True):
    CHECKS[0] += 1
    ok = (got == exp)
    if not ok:
        CHECKS[1] += 1
        MIS.append(name)
    if show or not ok:
        P(f"    [{'ok' if ok else 'MISMATCH'}] {name}: {got!r}" + ("" if ok else f"  (expected {exp!r})"))
    return ok


def sha16(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


def git(*a):
    return subprocess.run(["git", "-C", T2W] + list(a), capture_output=True, text=True).stdout.strip()


def same(x, y):
    x, y = np.asarray(x), np.asarray(y)
    return x.shape == y.shape and np.array_equal(np.nan_to_num(x, nan=1e300), np.nan_to_num(y, nan=1e300))


def cdt(kst):
    """'2026-10-02 08:43:39' KST -> 'MM-DD HH:MM' CDT (-14 h) via date."""
    return subprocess.run(["date", "-d", f"{kst} KST -14 hours", "+%m-%d %H:%M"], capture_output=True, text=True).stdout.strip()


# ----------------------------------------------------------------------------------------------- own raw reader
class Raw:
    def __init__(self, tag, only=None):
        self.tag = tag
        root = os.path.join(CONF, f"raw_{tag}")
        pts = {}
        for f in sorted(glob.glob(os.path.join(root, "D2_*.npz"))):
            m = PAT.match(os.path.basename(f))
            if m:
                pts.setdefault((m[1], m[2], float(m[7])), []).append((int(m[8]), int(m[9]), f))
        self.nfiles = sum(len(v) for v in pts.values())
        self.plan = {}
        self.data, self.meta, self.scal, self.holes, self.fill, self.raised = {}, {}, {}, [], [], {}
        for key, chunks in sorted(pts.items()):
            chunks.sort()
            self.plan[key] = [(s, n) for s, n, _ in chunks]
            pos = 0
            for s, n, _ in chunks:
                if s != pos:
                    self.holes.append((key, s, pos))
                pos = s + n
            zs = [np.load(f) for _, _, f in chunks]
            ns = [n for _, n, _ in chunks]
            keys = sorted({k for z in zs for k in z.files})
            d = {}
            for k in keys:
                a0 = next(z[k] for z in zs if k in z.files)
                if k.startswith("meta|") or k.startswith("run|"):
                    v = a0.item() if a0.shape == () else a0
                    self.meta.setdefault(key[:2], {}).setdefault(k, v)
                    for z in zs:
                        self.scal.setdefault(k, set()).add(str(z[k].item() if k in z.files and z[k].shape == () else (z[k] if k in z.files else "(none)")))
                    continue
                if "|" not in k or a0.ndim == 0:
                    continue
                arm, q = k.split("|", 1)
                if only is not None and arm not in only:
                    continue
                parts = []
                for z, nz in zip(zs, ns):
                    if k in z.files:
                        parts.append(z[k])
                    elif q == "failed":
                        parts.append(np.zeros((nz,) + a0.shape[1:]))
                    else:
                        parts.append(np.full((nz,) + a0.shape[1:], np.nan)); self.fill.append((key, k, nz))
                d.setdefault(arm, {})[q] = np.concatenate(parts)
            for z in zs:
                z.close()
            for arm, vv in d.items():
                be = vv.get("blk_err")
                if getattr(be, "ndim", 0) == 2:
                    bad = ~np.isfinite(be)
                    self.raised[(key, arm)] = int(bad[:, -1].sum())
                    if bad.any():
                        vv["blk_err"] = np.where(bad, 1.0, be)
            if "R0-pilot" in d:
                d["R0-pilot@1"] = {q: a[:, :1] for q, a in d["R0-pilot"].items() if getattr(a, "ndim", 0) == 2}
            self.data[key] = d
        self.cp = sorted({k[:2] for k in self.data})

    def snrs(self, cp):
        return sorted(k[2] for k in self.data if k[:2] == cp)

    def d(self, cp, s):
        return self.data[(cp[0], cp[1], float(s))]

    def m(self, cp):
        return self.meta.get(cp, {})

    def meta1(self, k):
        v = self.scal.get(k, {"(none)"})
        return next(iter(v)) if len(v) == 1 else sorted(v)


def fails(d, arm, it=-1):
    v = np.asarray(d[arm]["blk_err"])[:, it]
    return np.where(np.isfinite(v), v, 1.0)


def sign_p(a, b):
    n = a + b
    return 1.0 if n == 0 else min(1.0, 2 * sum(comb(n, i) for i in range(min(a, b) + 1)) / 2 ** n)


def dpoints(D, anchor):
    snrs = sorted(D)
    n = len(D[snrs[0]][anchor]["blk_err"])
    bl = {s: max(fails(D[s], anchor).mean(), 0.5 / n) for s in snrs}
    return sorted(sorted((s for s in snrs if 0.005 <= bl[s] <= 0.9), key=lambda s: abs(np.log10(bl[s] / 0.1)))[:3])


def table_b(D, x, y):
    cand = dpoints(D, x)
    res = []
    for s in cand:
        fx, fy = fails(D[s], x), fails(D[s], y)
        a = int(((fx == 1) & (fy == 0)).sum()); b = int(((fx == 0) & (fy == 1)).sum())
        res.append((a, b, sign_p(a, b)))
    A = sum(r[0] for r in res); Bn = sum(r[1] for r in res)
    powered = len(cand) == 3 and sum(1 for a, b, _ in res if a + b >= 6) >= 2
    wy = sum(1 for a, b, p in res if a > b and p < 0.05); wx = sum(1 for a, b, p in res if b > a and p < 0.05)
    lab = "(iv)" if not powered else "(i)" if wy >= 2 else "(ii)" if wx >= 2 else "(iii)"
    return dict(cand=cand, res=res, A=A, B=Bn, pp=sign_p(A, Bn), powered=powered, wx=wx, wy=wy, lab=lab)


def snr_at(snrs, bl, n, target=0.1):
    lb = np.log10(np.maximum(np.asarray(bl, float), 0.5 / n)); lt = np.log10(target)
    if lb[0] <= lt:
        return snrs[0], "lo"
    for i in range(len(snrs) - 1):
        if lb[i] > lt >= lb[i + 1]:
            return snrs[i] + (lb[i] - lt) / (lb[i] - lb[i + 1]) * (snrs[i + 1] - snrs[i]), "ok"
    return snrs[-1], "hi"


def fmt_at(v, f):
    return {"ok": f"{v:6.2f}", "lo": f"<={v:4.0f}", "hi": f" >{v:4.0f}"}[f]


def gap_text(D, x, y, seed=20260925):
    """house gain(): SNR@0.1(x) - SNR@0.1(y), paired bootstrap, one index draw per SNR per replicate, both arms."""
    snrs = sorted(D); ex = [fails(D[s], x) for s in snrs]; ey = [fails(D[s], y) for s in snrs]; n = min(len(e) for e in ex)
    (vx, fx), (vy, fy) = snr_at(snrs, [e.mean() for e in ex], n), snr_at(snrs, [e.mean() for e in ey], n)
    if fx == "hi" and fy == "ok":
        return f">= {vx - vy:+.2f} dB ({x} never reaches 0.1 on the grid)"
    if fx == "ok" and fy == "lo":
        return f">= {vx - vy:+.2f} dB ({y} is already below 0.1 at the lowest grid SNR)"
    if fx != "ok" or fy != "ok":
        return f"n/a ({fmt_at(vx, fx).strip()} vs {fmt_at(vy, fy).strip()}) — extend the SNR grid"
    rng = np.random.default_rng(seed); g = []
    for _ in range(B):
        bx, by = [], []
        for a, b in zip(ex, ey):
            i = rng.integers(len(a), size=len(a)); bx.append(a[i].mean()); by.append(b[i].mean())
        (ux, gx), (uy, gy) = snr_at(snrs, bx, n), snr_at(snrs, by, n); g.append(ux - uy if gx == gy == "ok" else np.nan)
    g = np.array(g); cens = np.mean(~np.isfinite(g)); lo, hi = np.nanpercentile(g, [5, 95])
    return f"{vx - vy:+.2f} dB  [90% paired bootstrap {lo:+.2f}, {hi:+.2f}; censored replicates {100 * cens:.0f}%]"


def boot_rec(cols, seed=SEED):
    """recovery_ci.boot: ONE index draw per replicate applied to every SNR column and all three arms."""
    rng = np.random.default_rng(seed); n = len(cols[0][0]); out = np.empty(B)
    for i in range(B):
        idx = rng.integers(0, n, n)
        bs = sum(b[idx].sum() for b, _, _ in cols); vs = sum(v[idx].sum() for _, v, _ in cols); gs = sum(g[idx].sum() for _, _, g in cols)
        out[i] = (bs - vs) / (bs - gs) if bs - gs > 0 else np.nan
    ok = np.isfinite(out)
    return (np.percentile(out[ok], [5, 95]) if ok.sum() else (np.nan, np.nan)), int((~ok).sum())


def recovery(cols):
    X, Vv, G = (sum(c[i].sum() for c in cols) for i in range(3))
    (lo, hi), nn = boot_rec(cols)
    return ((X - Vv) / (X - G) if X - G > 0 else np.nan), lo, hi, nn, (int(X), int(Vv), int(G))


# ----------------------------------------------------------------------------------------------- frontier_ci mirror
class Resampler:
    def __init__(self, seed):
        self.rng = np.random.default_rng(seed); self.idx = {}

    def new(self):
        self.idx = {}

    def take(self, spec, key, x):
        k = (spec, key)
        if k not in self.idx:
            self.idx[k] = self.rng.integers(0, len(x), len(x))
        return x[self.idx[k]]


def pct(v, q):
    v = v[np.isfinite(v)]
    return np.percentile(v, q) if len(v) else [np.nan] * len(q)


def ci_p(d, level):
    q = round(50 * (1 - level), 9)
    lo, hi = pct(d, [q, 100 - q])
    df = d[np.isfinite(d)]
    return lo, hi, (min(1.0, 2 * min(np.mean(df <= 0), np.mean(df >= 0))) if len(df) else np.nan)


def _R(cols):
    b = sum(c[0].sum() for c in cols); v = sum(c[1].sum() for c in cols); g = sum(c[2].sum() for c in cols)
    return (b - v) / (b - g) if b - g > 0 else np.nan, (int(b), int(v), int(g))


def _Rplus(b, v, g, bk2, ck):
    dF = bk2 - b
    fp = b - ck * max(0.0, dF)
    return ((fp - v) / (fp - g) if fp - g > 0 else np.nan), fp, dF


def _rstar(snrs, cols, n, t):
    bl = [np.array([c[a].mean() for c in cols]) for a in range(3)]
    s, f = snr_at(snrs, bl[0], n, target=t)
    if f != "ok":
        return np.nan, f, s, np.nan, np.nan
    bv, bg = (10 ** np.interp(s, snrs, np.log10(np.maximum(x, 0.5 / n))) for x in bl[1:])
    return ((t - bv) / (t - bg) if bg < t else np.nan), ("ok" if bg < t else "g"), s, bv, bg


RAWS = {}


def raw(tag, only=None):
    if tag not in RAWS:
        RAWS[tag] = Raw(tag, only)
    return RAWS[tag]


def frontier(s1, s2, level=0.90, extrap=("-", "-"), ck=("-", "-"), rstar=None):
    """-> list of output lines in frontier_ci's format (the lines after the '# run_scale2' header / NOTE line)."""
    out = []
    out.append(f"# recovery R = (b* - V1)/(b* - genie) @16; paired bootstrap per raw set (three arms together), the two raw sets "
               f"resampled independently (UNPAIRED difference); B={B}, seed={SEED}, 90% CI")
    sets = []
    for spec in (s1, s2):
        rtag, cell, snrs = spec.split(":")
        r = raw(rtag[4:], only=(BSTAR, V1, GENIE))
        keys = [k for k in sorted(r.data, key=lambda k: k[2]) if k[0] == cell and any(abs(k[2] - float(s)) < 1e-9 for s in snrs.split(","))]
        assert len(keys) == len(snrs.split(","))
        sets.append((rtag, cell, keys, [tuple(fails(r.data[k], a) for a in (BSTAR, V1, GENIE)) for k in keys]))
    k2 = []
    for e, st in zip(extrap, sets):
        if e == "-":
            k2.append(None); continue
        r2 = raw(e[4:], only=(BSTAR, GENIE)); rtag, cell, keys, cols = st
        for k, c in zip(keys, cols):
            assert k in r2.data and np.array_equal(fails(r2.data[k], GENIE), c[2]), f"{e} {k}: genie differs"
        k2.append([fails(r2.data[k], BSTAR) for k in keys])
    ckv = [None if e == "-" else float(c) for e, c in zip(extrap, ck)]
    rs = Resampler(SEED)
    bo, bp, fpg = (np.full((B, 2), np.nan) for _ in range(3)); ga = np.full((B, 2, 2), np.nan)
    for i in range(B):
        rs.new()
        for j, (rtag, cell, keys, cols) in enumerate(sets):
            rc = [tuple(rs.take(rtag, k, x) for x in c) for k, c in zip(keys, cols)]
            bo[i, j], (b, v, g) = _R(rc)
            ga[i, j] = v - g, b - g
            if k2[j] is None:
                bp[i, j] = bo[i, j]
            elif np.isfinite(ckv[j]):
                bk2 = sum(rs.take(rtag, k, x).sum() for k, x in zip(keys, k2[j]))
                bp[i, j], fp, _ = _Rplus(b, v, g, bk2, ckv[j]); fpg[i, j] = fp - g
    for j, (rtag, cell, keys, cols) in enumerate(sets):
        r, (b, v, g) = _R(cols); lo, hi = pct(bo[:, j], [5, 95])
        out.append(f"  R{j + 1}: {rtag} {cell} SNR {[f'{k[2]:+.0f}' for k in keys]}  b* {b} V1 {v} genie {g}  R = {r:.3f}  [90% {lo:.3f}, {hi:.3f}]"
                   + (f"  ({int((~np.isfinite(bo[:, j])).sum())} replicates undefined)" if (~np.isfinite(bo[:, j])).any() else ""))
    d = bo[:, 0] - bo[:, 1]; r1, r2 = _R(sets[0][3])[0], _R(sets[1][3])[0]
    lo, hi = pct(d, [5, 95])
    out.append(f"  R1 - R2 = {r1 - r2:+.3f}  [90% unpaired {lo:+.3f}, {hi:+.3f}]  undefined replicates {int((~np.isfinite(d)).sum())}")
    L = f"{100 * level:g}%"; lo, hi, p = ci_p(d, level)
    out.append(f"  R1 - R2 = {r1 - r2:+.3f}  [{L} unpaired {lo:+.3f}, {hi:+.3f}]  bootstrap two-sided p = {p:.4f}  (--level {level:g})")
    for j, (rtag, cell, keys, cols) in enumerate(sets):
        _, (b, v, g) = _R(cols); (l1, h1), (l2, h2) = pct(ga[:, j, 0], [5, 95]), pct(ga[:, j, 1], [5, 95])
        out.append(f"  gaps R{j + 1}: SigmaF_V1 - SigmaF_g = {v - g}  [90% {l1:.0f}, {h1:.0f}]   SigmaF_b* - SigmaF_g = {b - g}  [90% {l2:.0f}, {h2:.0f}]"
                   f"   (blocks, summed over SNR {[f'{k[2]:+.0f}' for k in keys]})")
    rp = [r1, r2]
    if any(x is not None for x in k2):
        out.append("# Q-K (K upper-limit SENSITIVITY, not a bound): dF = SigmaF_b*(K/2) - SigmaF_b*(K_max), SigmaF+ = SigmaF_b*(K_max) - "
                   "c_K max(0, dF), R+ = (SigmaF+ - SigmaF_V1)/(SigmaF+ - SigmaF_g); the K/2 b* column resampled with the BASE raw's indices")
    for j, (rtag, cell, keys, cols) in enumerate(sets):
        if k2[j] is None:
            continue
        _, (b, v, g) = _R(cols); bk2 = int(sum(x.sum() for x in k2[j]))
        K = [raw(rtag[4:]).m((cell, keys[0][1])).get("meta|kron_K"), raw(extrap[j][4:]).m((cell, keys[0][1])).get("meta|kron_K")]
        head = f"  R{j + 1}+: {rtag} {cell} kron_K {K[0]}  K/2 raw {extrap[j]} kron_K {K[1]}  b*(K/2) {bk2}  dF = {bk2 - b:+d}  c_K = {ckv[j]:g}"
        if not np.isfinite(ckv[j]):
            rp[j] = np.nan; out.append(head + "  (r >= 1)  [K 상한 민감: 외삽 불가]"); continue
        rp[j], fp, dF = _Rplus(b, v, g, bk2, ckv[j]); lo, hi = pct(bp[:, j], [5, 95]); und = np.mean(~(fpg[:, j] > 0))
        q = ("[K 상한 민감: 외삽 불가]" if und > 0.05 or not np.isfinite(rp[j]) else
             f"[K 상한 강건 (K/2 가 더 낫지 않음, ΔF_K = {dF:+.0f})]" if dF <= 0 else "")
        out.append(head + f"  SigmaF+ = {fp:g}  R+ = {rp[j]:.3f}  [90% {lo:.3f}, {hi:.3f}]  SigmaF+ <= SigmaF_g in {100 * und:.1f}% of replicates  {q}")
    if any(x is not None for x in k2):
        dp = bp[:, 0] - bp[:, 1]
        if np.isfinite(rp[0] - rp[1]):
            lo, hi, p = ci_p(dp, level)
            out.append(f"  R1+ - R2+ = {rp[0] - rp[1]:+.3f}  [{L} unpaired {lo:+.3f}, {hi:+.3f}]  bootstrap two-sided p = {p:.4f}  undefined replicates {int((~np.isfinite(dp)).sum())}")
        else:
            out.append("  R1+ - R2+: n/a (Q-K undefined)")
    if rstar is not None:
        t = rstar
        out.append(f"# Q-OP R*@{t:g} = ({t:g} - B_V1(s*))/({t:g} - B_g(s*)); s* = first downward crossing of {t:g} by b* (log10 max(BLER, 0.5/n) "
                   f"linear interpolation, snr_at); all grid points of the cell resampled (three arms together), s* recomputed per replicate; "
                   f"B={B}, seed={SEED} (own draw), {100 * level:g}% CI; undefined = lo / hi / B_g(s*) >= {t:g}")
        cur = []
        for rtag, cell, keys, _ in sets:
            r = raw(rtag[4:]); ks = sorted((k for k in r.data if k[0] == cell), key=lambda k: k[2])
            cols = [tuple(fails(r.data[k], a) for a in (BSTAR, V1, GENIE)) for k in ks]
            cur.append((rtag, cell, [k[2] for k in ks], ks, cols, min(len(c[0]) for c in cols)))
        rs = Resampler(SEED); bo2, fl = np.full((B, 2), np.nan), np.empty((B, 2), dtype=object)
        for i in range(B):
            rs.new()
            for j, (rtag, cell, snrs, ks, cols, n) in enumerate(cur):
                bo2[i, j], fl[i, j] = _rstar(snrs, [tuple(rs.take(rtag, k, x) for x in c) for k, c in zip(ks, cols)], n, t)[:2]
        q = round(50 * (1 - level), 9); est = []
        for j, (rtag, cell, snrs, ks, cols, n) in enumerate(cur):
            r, f, s, bv, bg = _rstar(snrs, cols, n, t); est.append(r)
            lo, hi = pct(bo2[:, j], [q, 100 - q]); und = np.mean(~np.isfinite(bo2[:, j]))
            cnt = {x: int((fl[:, j] == x).sum()) for x in ("lo", "hi", "g")}
            pt = f"s* = {s:+.2f} dB  B_V1(s*) = {bv:.4f}  B_g(s*) = {bg:.4f}  R* = {r:.3f}" if f == "ok" else \
                f"R* undefined ({'B_g(s*) >= t' if f == 'g' else fmt_at(s, f).strip() + ' dB'})"
            out.append(f"  R*{j + 1}: {rtag} {cell} grid {[f'{x:+.0f}' for x in snrs]} n={n}  {pt}  [{100 * level:g}% {lo:.3f}, {hi:.3f}]  "
                       f"undefined replicates {100 * und:.1f}% (lo {cnt['lo']}, hi {cnt['hi']}, B_g>=t {cnt['g']})"
                       + ("  [운영점 한정어 정의 불가]" if und > 0.05 or f != "ok" else ""))
        d = bo2[:, 0] - bo2[:, 1]
        if np.isfinite(est[0] - est[1]):
            lo, hi, p = ci_p(d, level)
            out.append(f"  R*1 - R*2 = {est[0] - est[1]:+.3f}  [{100 * level:g}% unpaired {lo:+.3f}, {hi:+.3f}]  bootstrap two-sided p = {p:.4f}  "
                       f"undefined replicates {int((~np.isfinite(d)).sum())}")
        else:
            out.append("  R*1 - R*2: n/a (R* undefined at the point estimate)")
    return out


def cmp_file(name, lines, skip_prefix=("# run_scale2", "# REPORT-ONLY")):
    f = os.path.join(RN, name + ".txt")
    have = [l.rstrip("\n") for l in open(f) if not l.startswith(skip_prefix)]
    ok = have == lines
    chk(f"{name}.txt body == own recompute ({len(lines)} lines)", ok, True, show=True)
    if not ok:
        for a, b in zip(have, lines):
            if a != b:
                P("      file: " + a); P("      own : " + b)
        if len(have) != len(lines):
            P(f"      line counts {len(have)} vs {len(lines)}")


# ----------------------------------------------------------------------------------------------- sections
def sec_git():
    P("\n## G. git / documents / logs / manifests / acceptance files")
    REG = "conf/results/review_next/NEXT_EXPERIMENTS_SCALE16e4.md"
    chk("HEAD", git("rev-parse", "--short", "HEAD"), "b4433d3c")
    chk("branch", git("branch", "--show-current"), "scale")
    chk("commits after b4433d3c on scale", git("log", "--oneline", "b4433d3c..HEAD"), "")
    chk("conf/code Demo clean", git("status", "--porcelain", "conf/code", "Demo"), "")
    chk("b4433d3c commit time (KST)", git("log", "-1", "--format=%ci", "b4433d3c"), "2026-10-02 03:52:11 +0900")
    chk("16a9dff6 commit time (KST)", git("log", "-1", "--format=%ci", "16a9dff6"), "2026-10-01 04:06:44 +0900")
    chk("diff 16a9dff6..b4433d3c -- conf/code Demo", git("diff", "16a9dff6", "b4433d3c", "--stat", "--", "conf/code", "Demo"), "")
    chk("files changed 16a9dff6..b4433d3c", git("diff", "16a9dff6", "b4433d3c", "--name-only").splitlines(), [REG, "conf/results/scale/scale2_s5.txt"])
    chk("numstat (working tree)", git("diff", "--numstat").splitlines(),
        ["2\t0\tconf/DECISIONS.md", f"324\t0\t{REG}", "1\t0\tdocs/EXPERIMENTS.md"])
    dl = git("diff", "--", REG).splitlines()
    chk("REG hunks", [l for l in dl if l.startswith("@@")], ["@@ -415,3 +415,327 @@ CELL NR32B16e4 d2sx_NR32_N160000_a1 3cf5d3eff96f0341 1f782042a5ad06b8 kron 2048"])
    chk("REG removed lines", len([l for l in dl if l.startswith("-") and not l.startswith("---")]), 0)
    txt = open(os.path.join(T2W, REG)).read().splitlines()
    head = git("show", f"HEAD:{REG}").splitlines()
    chk("REG lines 1-417 == HEAD (append-only)", txt[:417] == head and len(head) == 417, True)
    chk("REG line 417 is '## 6.'", txt[416].startswith("## 6. 결과"), True)
    chk("REG line 419 is '### 6.1'", txt[418].startswith("### 6.1 결과 (기록 2026-10-03 12:06 CDT (= 10-04 02:06 KST)"), True)
    chk("REG total lines", len(txt), 741)
    body = "\n".join(txt[418:741])
    chk("§6.1 bytes (lines 418-741)", len(("\n".join(txt[417:741]) + "\n").encode()), 47183)
    chk("scale2_s5.txt sha256 (HEAD == working)", git("show", "b4433d3c:conf/results/scale/scale2_s5.txt") == open(os.path.join(CONF, "results/scale/scale2_s5.txt")).read().rstrip("\n"), True)
    for pat in ("x CDT", "x KST", "xx:xx", "TODO"):
        chk(f"placeholder '{pat}' in §6.1 / EXPERIMENTS row / DECISIONS line", pat in body or pat in LAST_EXP or pat in LAST_DEC, False)
    chk("'TBD' in §6.1 only as the §5 reference '(§5 의 TBD)'", (body.count("TBD"), body.count("(§5 의 TBD)"), "TBD" in LAST_EXP + LAST_DEC), (1, 1, False))
    # §6.1.5 duration sums (runner 'finished in' minutes)
    chk("§6.1.5 sums UMi28 C9 / D2 C9 / UMi28 C6 / reuse", (round(820.0 + 50.6 + 4.6 + 73.6 + 120.5 + 325.1, 1), round(661.9 + 40.8 + 1.9 + 92.2 + 266.7, 1), round(120.8 + 8.8 + 2.5 + 12.1 + 18.8 + 44.2, 1), round(10.9 + 3.7 + 3.4 + 35.0 + 4.9, 1)), (1394.4, 1063.5, 207.2, 57.9))
    for w in ("유의하게", "우수", "개선", "여지", "headroom", "최적의", "비긴다", "동등", "significant", "입증", "확인됐다"):
        chk(f"interpretive word '{w}' absent", w in body + LAST_EXP + LAST_DEC, False)
    # ---- main log
    L = open(os.path.join(CONF, "logs/run_scale2.log")).read().splitlines()
    chk("run_scale2.log lines", len(L), 180)
    chk("L:1 start tune", L[0].startswith("[scale2 10-01 11:35 CDT] start tune (git 16a9dff6") and "GPU '1'" in L[0], True)
    chk("L:11 TUNE_DONE", L[10], "[scale2 10-01 12:57 CDT] SCALE2_TUNE_DONE ok=6 fail=0")
    chk("L:12 start estimate", L[11], "[scale2 10-01 14:03 CDT] start estimate (git b4433d3c, freeze 16a9dff651c8406927400da6353eb5b17022c73f, resume 0, WGB 8.0 (run 8.0), GPU '0')")
    chk("L:25 ESTIMATE_DONE", L[24], "[scale2 10-01 14:16 CDT] SCALE2_ESTIMATE_DONE ok=6 fail=0")
    chk("L:26 start eval", L[25], "[scale2 10-01 14:16 CDT] start eval (git b4433d3c, freeze 16a9dff651c8406927400da6353eb5b17022c73f, resume 0, WGB 8.0 (run 8.0), GPU '')")
    chk("L:179 DONE", L[178], "[scale2 10-03 11:49 CDT] SCALE2_DONE ok=101 fail=0")
    chk("L:180 EXIT", L[179], "SCALE2_EXIT=0")
    ev = L[25:179]
    chk("eval rc=0 lines", sum(1 for l in ev if l.endswith(" rc=0")), 101)
    chk("eval rc!=0 lines", sum(1 for l in ev if re.search(r" rc=[1-9]\d*$", l)), 0)
    chk("ABORT/SKIPPED/skip:/resume lines", sum(1 for l in L if re.search(r"ABORT|SKIPPED|skip:|--resume", l)), 0)
    chk("start lines", [i + 1 for i, l in enumerate(L) if " start " in l], [1, 12, 26])
    chk("frontier lines L:160-175", [i + 1 for i, l in enumerate(L) if "] frontier " in l], list(range(160, 176)))
    chk("pair_baselines lines L:176-178", [i + 1 for i, l in enumerate(L) if "] pair_baselines " in l], [176, 177, 178])
    chk("L:57", L[56], "[scale2 10-01 17:17 CDT] U28NR16B16e4 decision SNRs (anchor b*, never by hand): 0 3 6")
    chk("L:94", L[93], "[scale2 10-02 08:25 CDT] U28NR32B16e4 decision SNRs (anchor b*, never by hand): -3 0 3")
    chk("L:131", L[130], "[scale2 10-03 05:03 CDT] NR32B16e4 decision SNRs (anchor b*, never by hand): -9 -6 -3")
    chk("L:52", L[51], "raw_B16e4 (D2 C2 K/2 = kron 512 -14.636106156749378): 0 bad of 448 C2 files")
    chk("L:53", L[52], "[scale2 10-01 15:15 CDT] check raw_B16e4 (D2 C2 K/2) rc=0")
    acc_lines = {i + 1: l for i, l in enumerate(L) if "] accept " in l}
    chk("accept line numbers", sorted(acc_lines), [35, 42, 43, 50, 51, 86, 87, 88, 89, 90, 123, 124, 125, 126, 127, 156, 157, 158, 159])
    chk("all accept lines say ACCEPT: OK and rc=0", all("(ACCEPT: OK --" in l and l.endswith("rc=0") for l in acc_lines.values()), True)
    chk("(k) OK on C9 accept lines", [i for i, l in acc_lines.items() if "ACCEPT (k): OK" in l], [123, 124, 125, 126, 127, 156, 157, 158, 159])
    chk("manifest JSON lines", sum(1 for l in L if l.startswith('{"git_commit": "b4433d3c"')), 22)
    chk("b* last == A lines rc=0", [i + 1 for i, l in enumerate(L) if "b* " in l and "last ==" in l and l.endswith("rc=0")], [85, 122, 155])
    chk("guard_report lines rc=0", [i + 1 for i, l in enumerate(L) if "guard_report" in l and l.endswith("rc=0")], [81, 118, 151])
    t0 = int(subprocess.run(["date", "-d", "2026-10-01 14:16 CDT", "+%s"], capture_output=True, text=True).stdout)
    t1 = int(subprocess.run(["date", "-d", "2026-10-03 11:49 CDT", "+%s"], capture_output=True, text=True).stdout)
    chk("eval elapsed minutes", (t1 - t0) // 60, 2733)
    chk("45 h 33 min", divmod((t1 - t0) // 60, 60), (45, 33))
    for kst, cdtexp in (("2026-10-04 02:06", "10-03 12:06"), ("2026-10-02 04:16", "10-01 14:16"), ("2026-10-04 01:49", "10-03 11:49"), ("2026-10-02 03:52:11", "10-01 13:52")):
        chk(f"KST {kst} -> CDT", cdt(kst), cdtexp)
    for f, exp in ((REG, "2026-10-04 02:06"), ("conf/DECISIONS.md", "2026-10-04 02:06"), ("docs/EXPERIMENTS.md", "2026-10-04 02:06")):
        mt = subprocess.run(["stat", "-c", "%y", os.path.join(T2W, f)], capture_output=True, text=True).stdout[:16]
        chk(f"mtime {f} (KST)", mt, exp)
    chk("rss mentions in run_scale2.sh (lines)", [i + 1 for i, l in enumerate(open(os.path.join(CONF, "code/run_scale2.sh"))) if "rss" in l.lower()], [22, 35])
    chk("RSS / ps lines in run_scale2.log", sum(1 for l in L if re.search(r"RSS|\bps\b|VmRSS", l)), 0)
    chk("2nd-stage frontier lines carry no --level", all("--level" not in L[i] for i in (171, 172, 173)), True)
    chk("forced Q-K header absent in primary U28 files", all(not any(l.startswith("# Q-K: [K") for l in open(os.path.join(RN, f"scale2_primary_U28_{v}.txt"))) for v in ("L95", "L90")), True)
    # ---- runner logs (22)
    P("  runner logs (tag: header lines/resume, workers, first done s, finished min, warn/err lines, '/N done' count):")
    EXP6 = {}
    for row in re.findall(r"^\| (\S+) (?:\(A\) )?\| [^|]+ \| (\d+) \([^)]*\) \| (\d+) s \(:\d+\) \| ([\d.]+) min \(:\d+\) \| (?:10-0\d )?(\d\d:\d\d) \(:(\d+)\) \|$", "\n".join(txt[435:457]), re.M):
        EXP6[row[0]] = row[1:]
    chk("§6.1 runner table rows parsed", len(EXP6), 22)
    for t in TAGS:
        f = os.path.join(CONF, f"logs/run_D2_{t}.log"); ls = open(f).read().splitlines()
        hdr = [l for l in ls if l.startswith("# run_scale2 git b4433d3c")]
        wk = re.search(r"-> (\d+) tasks on (\d+) workers", "\n".join(ls)); jobs = re.search(r"jobs = (\d+)", "\n".join(ls))
        first = next((re.search(r"\((\d+) s\)", l)[1] for l in ls if re.search(r"^\s*1/\d+ done", l)), None)
        fin = next((re.search(r"finished in ([\d.]+) min", l)[1] for l in ls if "finished in" in l), None)
        ndone = sum(1 for l in ls if re.search(r"^\s*\d+/\d+ done", l))
        werr = sum(1 for l in ls if re.search(r"warn|error|traceback|exception", l, re.I))
        exp = EXP6.get(t)
        logline = next((i + 1, l) for i, l in enumerate(L) if re.search(rf"\] run {t} \(", l))
        got = (wk[2], first, fin, logline[1][14:19], str(logline[0]))
        chk(f"runner {t}: hdr {len(hdr)} resume=0 {all('resume=0' in h for h in hdr)} ndone {ndone} werr {werr} | workers/first/finished/time/L", got, tuple(exp), show=True)
        chk(f"runner {t}: one header, resume=0, no warn/err, all chunks done", (len(hdr), all("resume=0" in h for h in hdr), werr, ndone == int(wk[1])), (1, True, 0, True), show=False)
    # ---- manifests
    P("  run_manifest JSON (git, n_raw_files, config_hash, arms, written KST -> CDT == log time):")
    for t in TAGS:
        m = json.load(open(os.path.join(RN, f"run_manifest_{t}.json")))
        logline = next((i + 1, l) for i, l in enumerate(L) if re.search(rf"\] run_manifest {t} rc=0", l))
        chk(f"manifest {t}", (m["git_commit"], m["n_raw_files"], m["config_hash"], len(m["arms"]), cdt(m["written"][:19]) == logline[1][8:19]),
            ("b4433d3c", NFILES[t], CFG[t], NARMS[t], True), show=True)
    # ---- acceptance files
    for t in ACC:
        chk(f"{t}_accept.txt", open(os.path.join(RN, f"{t}_accept.txt")).read().rstrip("\n").splitlines(), ACC[t], show=False)
    P(f"  acceptance files: {len(ACC)} compared")


TAGS = ["K2NR16B16e4", "K2U28B16e4", "BRB16e4k", "BRNR16", "BRU28",
        "U28NR16B16e4", "PILU28NR16", "ALDU28NR16", "K2U28NR16B16e4", "U28NR16B16e4chk", "U28NR16B16e4last",
        "U28NR32B16e4", "PILU28NR32", "ALDU28NR32", "K2U28NR32B16e4", "U28NR32B16e4chk", "U28NR32B16e4last",
        "NR32B16e4", "PILNR32", "ALDNR32", "NR32B16e4chk", "NR32B16e4last"]
NFILES = {t: (448 if (t.startswith(("PIL", "ALD")) or t in ("U28NR16B16e4", "U28NR32B16e4", "NR32B16e4")) else 1 if (t.startswith("BR") or t.endswith("chk")) else 192) for t in TAGS}
NARMS = {t: (14 if t.startswith("BR") else 2 if t.startswith("K2") else 3 if t.startswith(("PIL", "ALD")) or t.endswith("last") else 11) for t in TAGS}
CFG = dict(BRB16e4k="116f9f39fdff840f", K2NR16B16e4="5f18c69f99ce4d34", BRNR16="df23c83552a360b4", K2U28B16e4="af426876fd7d9a24", BRU28="5f69f58ab3f09779",
           U28NR16B16e4="a6690fc805e18f7e", PILU28NR16="a6690fc805e18f7e", ALDU28NR16="a6690fc805e18f7e", K2U28NR16B16e4="7742fd0201dd4a3f",
           U28NR16B16e4chk="df23c83552a360b4", U28NR16B16e4last="7742fd0201dd4a3f", U28NR32B16e4="8058a740f0282d38", PILU28NR32="8058a740f0282d38",
           ALDU28NR32="8058a740f0282d38", K2U28NR32B16e4="00d5c3a2d97766a3", U28NR32B16e4chk="e153aa498f11669e", U28NR32B16e4last="00d5c3a2d97766a3",
           NR32B16e4="8058a740f0282d38", PILNR32="8058a740f0282d38", ALDNR32="8058a740f0282d38", NR32B16e4chk="e153aa498f11669e", NR32B16e4last="96c82d63940fa78e")
K8 = "  (k) raw_{r}: meta|worker_gb ['8.0']  meta|jobs ['{j}']"
ACC = {"BRB16e4k": ["ACCEPT: OK -- BRB16e4k"], "BRNR16": ["ACCEPT: OK -- BRNR16"], "BRU28": ["ACCEPT: OK -- BRU28"],
       "K2NR16B16e4": ["ACCEPT: OK -- K2NR16B16e4"], "K2U28B16e4": ["ACCEPT: OK -- K2U28B16e4"],
       "U28NR16B16e4": ["ACCEPT: OK -- U28NR16B16e4"], "U28NR16B16e4pa": ["ACCEPT: OK -- U28NR16B16e4, PILU28NR16, ALDU28NR16"],
       "U28NR16B16e4chk": ["ACCEPT: OK -- U28NR16B16e4chk"], "K2U28NR16B16e4": ["ACCEPT: OK -- K2U28NR16B16e4"], "U28NR16B16e4last": ["ACCEPT: OK -- U28NR16B16e4last"],
       "U28NR32B16e4": ["ACCEPT: OK -- U28NR32B16e4", K8.format(r="U28NR32B16e4", j=99), "ACCEPT (k): OK"],
       "U28NR32B16e4pa": ["ACCEPT: OK -- U28NR32B16e4, PILU28NR32, ALDU28NR32", K8.format(r="U28NR32B16e4", j=99), K8.format(r="PILU28NR32", j=99), K8.format(r="ALDU28NR32", j=99), "ACCEPT (k): OK"],
       "U28NR32B16e4chk": ["ACCEPT: OK -- U28NR32B16e4chk", K8.format(r="U28NR32B16e4chk", j=1), "ACCEPT (k): OK"],
       "K2U28NR32B16e4": ["ACCEPT: OK -- K2U28NR32B16e4", K8.format(r="K2U28NR32B16e4", j=99), "ACCEPT (k): OK"],
       "U28NR32B16e4last": ["ACCEPT: OK -- U28NR32B16e4last", K8.format(r="U28NR32B16e4last", j=99), "ACCEPT (k): OK"],
       "NR32B16e4": ["ACCEPT: OK -- NR32B16e4", K8.format(r="NR32B16e4", j=99), "ACCEPT (k): OK"],
       "NR32B16e4pa": ["ACCEPT: OK -- NR32B16e4, PILNR32, ALDNR32", K8.format(r="NR32B16e4", j=99), K8.format(r="PILNR32", j=99), K8.format(r="ALDNR32", j=99), "ACCEPT (k): OK"],
       "NR32B16e4chk": ["ACCEPT: OK -- NR32B16e4chk", K8.format(r="NR32B16e4chk", j=1), "ACCEPT (k): OK"],
       "NR32B16e4last": ["ACCEPT: OK -- NR32B16e4last", K8.format(r="NR32B16e4last", j=99), "ACCEPT (k): OK"]}
LAST_EXP = open(os.path.join(T2W, "docs/EXPERIMENTS.md")).read().rstrip("\n").splitlines()[-1]
LAST_DEC = open(os.path.join(CONF, "DECISIONS.md")).read().rstrip("\n").splitlines()[-1]

# cells: tag -> (cell, prior, suffix, ckpt stem, best sha, last sha, kron_K, ll_val, decision points, grid)
NEW = {"U28NR16B16e4": ("C6", "UMi28", "U28NR16", "d2sx_UMi28NR16_N160000_a1", "34136808b1e367ac", "ee3818febe902e99", 4096, 56.5879534445348, (0, 3, 6), (-3, 0, 3, 6, 9, 12, 15), 642, 662),
       "U28NR32B16e4": ("C9", "UMi28", "U28NR32", "d2sx_UMi28NR32_N160000_a1", "463da87aa8dbfb61", "347a1e5b6c270222", 4096, 152.23176788511105, (-3, 0, 3), (-12, -9, -6, -3, 0, 3, 6), 232, 252),
       "NR32B16e4": ("C9", "S2", "NR32", "d2sx_NR32_N160000_a1", "3cf5d3eff96f0341", "1f782042a5ad06b8", 2048, 242.7371088214899, (-9, -6, -3), (-12, -9, -6, -3, 0, 3, 6), 230, 250)}
REUSE = {"B16e4k": ("C2", "S2", "d2sx_N160000_a1.pt", "4443921ce8d5c4a1", "legacy-last", 1024, -11.459169831224418, (-3, 0, 3), "BRB16e4k", -3, None, None, "78cbb59fc01ce520"),
         "NR16B16e4": ("C6", "S2", "d2sx_NR16_N160000_a1_fb2_best.pt", "c050d611b2c714a6", "best", 4096, 63.1751571838059, (-3, 0, 3), "BRNR16", -3, "K2NR16B16e4", 61.982398757574266, "279cdea5c7a4f054"),
         "U28B16e4": ("C2", "UMi28", "d2sx_UMi28_N160000_a1_best.pt", "6f3a1b9490864af1", "best", 4096, 5.797910431000217, (3, 6, 9), "BRU28", 3, "K2U28B16e4", 5.539276756851168, "213dd3a3a3226fa6")}


def chunks_sha(root):
    chunks = sorted(glob.glob(os.path.join(root, "*.npz")))
    return hashlib.sha256("".join(hashlib.sha256(open(c, "rb").read()).hexdigest() for c in chunks).encode()).hexdigest()[:16], len(chunks)


def sec_raw():
    P("\n## 1. raw integrity (22 tags): files, chunk plan, run|git, meta, ckpt id, jobs/worker_gb, em_sec, genie (d), chk/bridge replay (e), K/2, last == A")
    total = 0
    for t in TAGS:
        r = raw(t); total += r.nfiles
        cp = r.cp[0]; snrs = r.snrs(cp)
        n = {len(r.d(cp, s)[a]["blk_err"]) for s in snrs for a in r.d(cp, s)}
        plan_ok = all(p == [(40 * k, 40) for k in range(len(p))] for p in r.plan.values())
        arms = sorted(a for a in r.d(cp, snrs[0]) if a != "R0-pilot@1")
        info = (r.nfiles, r.meta1("run|git"), r.meta1("meta|ntrain"), r.meta1("meta|bstar"), r.meta1("meta|kron_K"), r.meta1("meta|ll_val|kron"),
                r.meta1("meta|jobs"), r.meta1("meta|worker_gb"), sorted(n), plan_ok, not r.holes, not r.fill, len(arms), sum(r.raised.values()))
        P(f"  {t}: files {info[0]} git {info[1]} ntrain {info[2]} bstar {info[3]} kron_K {info[4]} ll {info[5]} jobs {info[6]} worker_gb {info[7]} n {info[8]} plan {info[9]} holes0 {info[10]} nanfill0 {info[11]} arms {info[12]} raised {info[13]} points {[f'{s:+.0f}' for s in snrs]}")
        P(f"      ckpt id {r.meta1('meta|stagec_ckpt_id')!r}  em_sec {r.meta1('meta|em_sec')}  fit_sec|V1 {r.meta1('meta|fit_sec|M-ours-dscore-C-V1')}")
        chk(f"{t} basics", (info[0], info[1], info[2], info[3], info[8], info[9], info[10], info[11], info[13]), (NFILES[t], "b4433d3c", "160000.0", "kron", [2560 if NFILES[t] > 1 else 40], True, True, True, 0), show=False)
    chk("npz total over 22 tags", total, 5382)
    # per new cell: meta, ckpt id, jobs, genie identity, chk replay, last == A, K2
    for T, (cell, prior, suf, stem, bsha, lsha, kk, ll, dp, grid, bep, lep) in NEW.items():
        cp = (cell, prior)
        A = raw(T); fam = {"A": T, "PIL": "PIL" + suf, "ALD": "ALD" + suf, "chk": T + "chk", "last": T + "last"}
        if kk == 4096:
            fam["K2"] = "K2" + T
        P(f"  [{T}] family {sorted(fam.values())}")
        for role, tg in fam.items():
            r = raw(tg); cpx = r.cp[0]
            kexp = 2048 if role == "K2" else kk; lexp = {"K2U28NR16B16e4": 55.61013440427408, "K2U28NR32B16e4": 150.38770163027337}.get(tg, ll)
            idexp = f"sha256[:16]={lsha} epoch={lep} best_epoch={bep} role=last" if role == "last" else f"sha256[:16]={bsha} epoch={bep} best_epoch={bep} role=best"
            chk(f"{tg}: cell/prior, kron_K, ll_val, ckpt id prefix", (cpx, r.meta1("meta|kron_K"), r.meta1("meta|ll_val|kron"), str(r.meta1("meta|stagec_ckpt_id")).startswith(idexp)),
                (cp, str(kexp), repr(lexp), True), show=False)
            jexp = ("99" if NFILES[tg] > 1 else "1", "8.0") if cell == "C9" else ("(none)", "(none)")
            chk(f"{tg}: meta|jobs, meta|worker_gb", (r.meta1("meta|jobs"), r.meta1("meta|worker_gb")), jexp, show=False)
            chk(f"{tg}: point set", tuple(int(s) for s in r.snrs(cpx)), tuple(dp) if role in ("K2", "last") else (grid[0],) if role == "chk" else tuple(grid), show=False)
            chk(f"{tg}: em_sec == A", r.meta1("meta|em_sec"), A.meta1("meta|em_sec") if role != "K2" else r.meta1("meta|em_sec"), show=False)
            # (d) genie 4 keys bit-identical to A at shared trials
            bad = 0
            for s in r.snrs(cpx):
                for q in KEYS4:
                    x = np.asarray(r.d(cpx, s)[GENIE][q]); y = np.asarray(A.d(cp, s)[GENIE][q])[:len(x)]
                    bad += not same(x, y)
            chk(f"{tg}: (d) genie 4 keys == A ({len(r.snrs(cpx))} points)", bad, 0, show=False)
        # (c) manual epoch cross-check
        chk(f"{T}: (c) A epoch == last best_epoch", (re.search(r"epoch=(\d+)", str(A.meta1("meta|stagec_ckpt_id")))[1], re.search(r"best_epoch=(\d+)", str(raw(T + "last").meta1("meta|stagec_ckpt_id")))[1]), (str(bep), str(bep)))
        # (e) chk replay: all 11 arms x KEYS_RAW at chunk 0 of the first grid SNR
        c = raw(T + "chk"); s0 = float(grid[0]); diff = []
        for a in AARMS:
            for q in KEYS_RAW:
                if q in c.d(cp, s0)[a]:
                    if not same(c.d(cp, s0)[a][q], np.asarray(A.d(cp, s0)[a][q])[:40]):
                        diff.append((a, q))
        chk(f"{T}chk: (e) 11 arms x KEYS_RAW == A chunk 0 at {s0:+.0f} dB", diff, [])
        # last == A: b* 7 keys over 192 chunks
        last = raw(T + "last"); nb = nn = 0
        for s in dp:
            for q in KEYS_RAW:
                x, y = np.asarray(last.d(cp, s)[BSTAR][q]), np.asarray(A.d(cp, s)[BSTAR][q])
                for k in range(64):
                    nn += 1; nb += not same(x[40 * k:40 * k + 40], y[40 * k:40 * k + 40])
        chk(f"{T}last: b* last == A (chunk, key) pairs differing / total", (nb, nn), (0, 1344))
        # K2: b* kron 2048 raw at decision points
        if "K2" in fam:
            k2 = raw(fam["K2"]); chk(f"K2{T}: kron_K / points", (k2.meta1("meta|kron_K"), tuple(int(s) for s in k2.snrs(cp))), ("2048", tuple(dp)))
        # ckpt sha
        chk(f"{T}: ckpt sha best/last", (sha16(os.path.join(CONF, "ckpt", stem + "_best.pt")), sha16(os.path.join(CONF, "ckpt", stem + ".pt"))), (bsha, lsha))
        # fits grid completeness (a)
        fd = os.path.join(CONF, f"results/gmm_fits_D2_{T}"); nr = {"C6": 16, "C9": 32}[cell]
        miss = [f"{fam_}K{K}" for fam_, Ks in (("full", (16, 32, 64, 128, 256, 512)), ("kron", (16, 32, 64, 128, 256, 512, 1024, 2048, 4096))) for K in Ks
                if not os.path.exists(os.path.join(fd, f"fit_{prior}_Nr{nr}_{fam_}K{K}_n160000.npz"))]
        cands = [K for K in (1024, 2048, 4096) if len(glob.glob(os.path.join(fd, f"fit_{prior}_Nr{nr}_kronK{K}_n160000.k0r*.npz"))) != 3]
        chk(f"{T}: (a) fits grid 15 merged + 3 candidates x 3", (miss, cands), ([], []))
        with np.load(os.path.join(fd, f"fit_{prior}_Nr{nr}_kronK{kk}_n160000.npz")) as z:
            chk(f"{T}: fits kron{kk} ll_val == raw meta", repr(float(z["ll_val"])), A.meta1("meta|ll_val|kron"))
        if "K2" in fam:
            with np.load(os.path.join(fd, f"fit_{prior}_Nr{nr}_kronK2048_n160000.npz")) as z:
                chk(f"{T}: fits kron2048 ll_val == K2 raw meta", repr(float(z["ll_val"])), raw(fam["K2"]).meta1("meta|ll_val|kron"))
    # reuse cells: bridge replay (14 arms), K2 genie, chunks-sha, ckpt sha, raw_B16e4
    for Rt, (cell, prior, ckf, sha, role, kk, ll, dp, br, s0, k2, k2ll, csha) in REUSE.items():
        cp = (cell, prior); base = raw(Rt)
        chk(f"raw_{Rt}: files, kron_K, ll_val, run|git key", (base.nfiles, base.meta1("meta|kron_K"), base.meta1("meta|ll_val|kron"), base.meta1("run|git")), (448, str(kk), repr(ll), "(none)"))
        chk(f"raw_{Rt}: chunks-sha", chunks_sha(os.path.join(CONF, f"raw_{Rt}")), (csha, 448))
        chk(f"{ckf} sha256[:16]", sha16(os.path.join(CONF, "ckpt", ckf)), sha)
        b = raw(br); d0 = b.d(cp, float(s0)); diff = []
        for a in sorted(d0):
            if a == "R0-pilot@1":
                continue
            for q in KEYS_RAW:
                if q in d0[a] and q in base.d(cp, float(s0)).get(a, {}):
                    if not same(d0[a][q], np.asarray(base.d(cp, float(s0))[a][q])[:40]):
                        diff.append((a, q))
        chk(f"{br}: bridge replay {len([a for a in d0 if a != 'R0-pilot@1'])} arms x KEYS_RAW vs raw_{Rt} chunk 0 at {s0:+d} dB", diff, [])
        chk(f"{br}: ckpt id role/sha", (f"sha256[:16]={sha}" in str(b.meta1("meta|stagec_ckpt_id")), f"role={role}" in str(b.meta1("meta|stagec_ckpt_id"))), (True, True))
        if k2:
            r2 = raw(k2); bad = sum(not same(r2.d(cp, s)[GENIE][q], base.d(cp, s)[GENIE][q]) for s in dp for q in KEYS4)
            chk(f"{k2}: kron_K 2048, ll, genie == raw_{Rt} at {dp}", (r2.meta1("meta|kron_K"), r2.meta1("meta|ll_val|kron"), bad), ("2048", repr(k2ll), 0))
    # raw_B16e4 (D2 C2 K/2)
    bk = raw("B16e4k"); cp = ("C2", "S2"); bad = 0; nfs = 0
    for f in sorted(glob.glob(os.path.join(CONF, "raw_B16e4/D2_C2_*.npz"))):
        nfs += 1
        with np.load(f) as z, np.load(os.path.join(CONF, "raw_B16e4k", os.path.basename(f))) as y:
            bad += int(float(z["meta|kron_K"])) != 512 or abs(float(z["meta|ll_val|kron"]) + 14.636106156749378) > 1e-9
            bad += any(not same(z[k], y[k]) for k in ("R5-genie|blk_err", "R5-genie|ber", "R5-genie|tauL_gmean", "R5-genie|alphaD"))
    chk("raw_B16e4 (D2 C2 K/2): C2 files, bad", (nfs, bad), (448, 0))
    chk("raw_B16e4k / raw_B16e4 git-tracked and clean", (len(git("ls-files", "conf/raw_B16e4k", "conf/raw_B16e4").splitlines()), git("status", "--porcelain", "conf/raw_B16e4k", "conf/raw_B16e4")), (1792, ""))
    for lk, tgt in (("raw_NR16B16e4", "/home/HTJ/t2/conf/raw_NR16B16e4"), ("raw_U28B16e4", "/home/HTJ/t2/conf/raw_U28B16e4"), ("results/gmm_fits_D2_NR16B16e4", "/home/HTJ/t2/conf/results/gmm_fits_D2_NR16B16e4")):
        chk(f"link {lk}", os.path.realpath(os.path.join(CONF, lk)), tgt, show=False)


def pairb_lines(T):
    """Re-generate pair_baselines' 13-arm block + summaries + failure / NMSE tables for a new cell (own implementation)."""
    cell, prior, suf = NEW[T][:3]; cp = (cell, prior)
    base, pil, ald = raw(T), raw("PIL" + suf), raw("ALD" + suf)
    snrs = base.snrs(cp)
    D = {s: {**base.d(cp, s), **{x: pil.d(cp, s)[x] for x in ("V1-pilot", "bstar-pilot")}, **{x: ald.d(cp, s)[x] for x in ("ALD-pilot", "ALDv-pilot")}} for s in snrs}
    BL = tuple("R0-pilot@1" if x == "R0-pilot" else x for x in BASELINES)
    out = ["# R0-pilot read at @1 (1-pass, 08_SPEC §1; load_raw alias 'R0-pilot@1'), SUPP16e4 §1"]
    labs, rows = {}, []
    fv3, fg3 = fails(D[-3.0], V1), fails(D[-3.0], GENIE); vg = fg3.sum() >= fv3.sum()
    for x in (BSTAR,) + BL:
        t = table_b(D, x, V1); labs[x] = t["lab"]
        out.append(f"{x} -> {V1}  [anchor {x}]  decision SNRs {[f'{s:+.0f}' for s in t['cand']]}")
        out.append("    sign test @16: " + "  ".join(f"{s:+.0f} dB {r[0]}:{r[1]} p={r[2]:.2g}" for s, r in zip(t["cand"], t["res"])) + f"   pooled {t['A']}:{t['B']} p={t['pp']:.2g}")
        out.append(f"    POWERED={t['powered']}  second arm fewer at {t['wy']}/{len(t['cand'])}, first arm fewer at {t['wx']}/{len(t['cand'])}  -> {t['lab']}")
        out.append(f"    SNR@0.1 gap ({x} minus V1): {gap_text(D, x, V1)}")
        fx, fv, fg = (fails(D[-3.0], a) for a in (x, V1, GENIE)); bl = fx.mean()
        if vg:
            r1 = "undefined (the genie fails at least as often as V1 at -3 dB)"
        elif not (0.005 <= bl <= 0.9) or fx.sum() <= fg.sum():
            r1 = "undefined (out of range: -3 dB BLER %.4f, F_X %d, F_genie %d)" % (bl, fx.sum(), fg.sum())
        else:
            R, lo, hi, nn, _ = recovery([(fx, fv, fg)])
            r1 = f"{R:.3f} [90% {lo:.3f}, {hi:.3f}]" + (f" ({nn} undefined replicates)" if nn else "") + (" -> 정의 불가 (>5% undefined)" if nn > 0.05 * B else "")
        cols2 = [tuple(fails(D[s], a) for a in (x, V1, GENIE)) for s in t["cand"]]
        if t["cand"] and sum(c[2].sum() for c in cols2) >= sum(c[1].sum() for c in cols2):
            r2 = "undefined (the genie fails at least as often as V1 over the decision points)"
        elif t["cand"]:
            R2, lo2, hi2, nn2, _ = recovery(cols2)
            r2 = f"{R2:.3f} [90% {lo2:.3f}, {hi2:.3f}] over {len(t['cand'])} point(s)" + (f" ({nn2} undefined)" if nn2 else "")
        else:
            r2 = "undefined (no decision point)"
        out.append(f"    absolute gap -3 dB: F_X - F_V1 = {int(fx.sum() - fv.sum())} blocks of {len(fx)}")
        out.append(f"    R_X -3 dB (primary): {r1}")
        out.append(f"    R_X decision points (secondary): {r2}")
        rows.append((x, int(fx.sum()), t["lab"], r1))
    k = sum(1 for x in labs if labs[x] == "(i)"); mm = sum(1 for x in labs if labs[x] == "(ii)")
    kB = k - (labs[BSTAR] == "(i)"); mB = mm - (labs[BSTAR] == "(ii)")
    out.append(f"SUMMARY-B (baselines without b*, {len(BL)}): (i) {kB}, (ii) {mB}, not decided {len(BL) - kB - mB}; b* -> V1 {labs[BSTAR]}")
    xs = min(rows, key=lambda r: (r[1], r[0]))
    fx, fv, fg = (fails(D[-3.0], a) for a in (xs[0], V1, GENIE))
    ok_range = 0.005 <= fx.mean() <= 0.9 and fx.sum() > fg.sum() and not vg
    R, lo, hi, nn, _ = recovery([(fx, fv, fg)]) if ok_range else (np.nan, np.nan, np.nan, 0, None)
    out.append("")
    out.append(f"SUMMARY registered baselines {len(labs)} (b* + 𝔅 {len(BASELINES)}): (i) {k}, (ii) {mm}, not decided {len(labs) - k - mm}")
    out.append("    " + "  ".join(f"{x}={labs[x]}" for x in labs))
    out.append(f"X* (fewest -3 dB failures, ties by name) = {xs[0]} (F={xs[1]}); R_X* -3 dB = " + (f"{R:.3f} [90% {lo:.3f}, {hi:.3f}]" if ok_range else "undefined (out of range)"))
    cond = k == len(labs) and mm == 0 and ok_range and lo > 0
    out.append(f"'등록된 baseline 전부와 멀어진다' condition (k = {len(labs)}, (ii) = 0, R_X* CI lower > 0): {'MET' if cond else 'NOT met'}")
    out.append("BLER@16 failures / n per SNR " + " ".join(f"{s:+.0f}" for s in snrs) + " dB:")
    for arm in dict.fromkeys((GENIE, V1, BSTAR) + BL + ("R0-pilot", "M-ours-dscore-C-V0", "M-ours-dscore-C-V4", "M-ours-dscore-C-V4b")):
        if arm in D[snrs[0]]:
            out.append(f"    {arm:<20}" + " ".join(f"{int(fails(D[s], arm).sum()):5d}" for s in snrs))
    out.append("report-only, median NMSE@16 of the channel estimate per SNR:")
    for arm in (V1, BSTAR) + BL:
        if arm in D[snrs[0]] and "nmse" in D[snrs[0]][arm]:
            out.append(f"    {arm:<20}" + " ".join(f"{np.nanmedian(np.asarray(D[s][arm]['nmse'])[:, -1]):.2e}" for s in snrs))
    return out, D, labs, rows, xs, (R, lo, hi, ok_range, cond)


def sec_pair():
    P("\n## 2. decision points, table B (13 X -> V1), 𝔅, X*, sentence condition, failures / NMSE tables -- vs pairB_<T>.txt and §6.1.3")
    txt = open(os.path.join(T2W, "conf/results/review_next/NEXT_EXPERIMENTS_SCALE16e4.md")).read().splitlines()
    sec = "\n".join(txt[417:741])
    res = {}
    for T in NEW:
        out, D, labs, rows, xs, cond = pairb_lines(T)
        have = [l.rstrip("\n") for l in open(os.path.join(RN, f"pairB_{T}.txt"))][2:]
        chk(f"pairB_{T}.txt lines 3-132 == own recompute ({len(out)} lines)", have == out, True)
        if have != out:
            for a, b in zip(have, out):
                if a != b:
                    P("      file: " + a); P("      own : " + b)
        dp = dpoints(D, BSTAR)
        chk(f"{T}: decision points (anchor b*)", tuple(int(s) for s in dp), NEW[T][8])
        res[T] = (out, D, labs, rows, xs, cond)
        # §6.1.3 𝔅 table rows: parse the markdown rows of this cell and compare each cell with the pairB-derived strings
        blk = {}
        for i in range(0, len(out)):
            m = re.match(r"^(\S+) -> M-ours-dscore-C-V1  \[anchor \S+\]  decision SNRs \[(.*)\]$", out[i])
            if m:
                x = m[1]; cand = m[2].replace("'", "").replace(", ", "/")
                pooled = re.search(r"pooled (\d+:\d+)", out[i + 1])[1]
                lab = re.search(r"-> (\(\w+\))$", out[i + 2])[1]; k3 = re.search(r"second arm fewer at (\d/\d)", out[i + 2])[1]
                g = out[i + 3].split(": ", 1)[1]
                g = re.sub(r"  \[90% paired bootstrap [^\]]*\]", "", g).replace(" dB", " dB")
                g = re.sub(r"^>= (\+[\d.]+) dB \(.*never reaches 0.1 on the grid\)$", r"≥ \1 dB (격자에서 0.1 미도달)", g)
                ag = re.search(r"= (-?\d+) blocks", out[i + 4])[1]
                r1 = out[i + 5].split(": ", 1)[1]; r2 = out[i + 6].split(": ", 1)[1].replace(" over 3 point(s)", "")
                blk[x] = (cand, pooled, lab, k3, r1, r2, ag, g)
        name = {"NR32B16e4": "D2 C9 (`pairB_NR32B16e4.txt`):", "U28NR16B16e4": "UMi28 C6 (`pairB_U28NR16B16e4.txt`):", "U28NR32B16e4": "UMi28 C9 (`pairB_U28NR32B16e4.txt`):"}[T]
        i0 = txt.index(name); rows_md = [l for l in txt[i0 + 4: i0 + 17] if l.startswith("| ")]
        nrow = 0
        for l in rows_md:
            c = [x.strip() for x in l.strip("|").split("|")]
            x = c[0].replace("\\", ""); x = {"b* (M-ours-bstar)": BSTAR, "b*": BSTAR}.get(x, x)
            exp = blk[x]
            got = (c[1].replace("−", "-"), c[2], re.sub(r"\*\*|\s*\d/3$", "", c[3]).strip(), re.search(r"(\d/3)", c[3])[1], c[4].replace("−", "-"), c[5], c[6], c[7].replace("−", "-"))
            expc = (exp[0], exp[1], exp[2], exp[3], exp[4].replace("[90% ", "["), exp[5].replace("[90% ", "["), exp[6], exp[7])
            nrow += 1
            chk(f"§6.1.3 {T} row {x}", got, expc, show=False)
        chk(f"§6.1.3 {T}: 13 rows parsed", nrow, 13)
    # §6.1.3 summary table and sentences
    for T, xexp, rexp, cexp in (("NR32B16e4", "V1-pilot (F = 12)", "undefined (out of range)", "NOT met"), ("U28NR16B16e4", "M-ours-bstar (F = 752)", "0.228 [0.190, 0.266]", "MET"), ("U28NR32B16e4", "V1-pilot (F = 440)", "0.259 [0.216, 0.301]", "MET")):
        out, D, labs, rows, xs, (R, lo, hi, okr, cond) = res[T]
        chk(f"{T}: X*, R_X*, condition", (f"{xs[0]} (F = {xs[1]})", f"{R:.3f} [{lo:.3f}, {hi:.3f}]" if okr else "undefined (out of range)", "MET" if cond else "NOT met"), (xexp, rexp, cexp))
        chk(f"{T}: labels (i) 13, (ii) 0", (sum(v == "(i)" for v in labs.values()), sum(v == "(ii)" for v in labs.values()), len(labs)), (13, 0, 13))
    chk("§6.1.3 count sentence", "표 B 3 ((i) 3) + 𝔅 36 ((i) 36, (ii) 0, 판정 못함 0)" in sec, True)
    # (b) failures table in §6.1.4 vs own
    for T, key in (("NR32B16e4", "| D2 C9 | −12/−9/−6/−3/+0/+3/+6 |"), ("U28NR16B16e4", "| UMi28 C6 | −3/+0/+3/+6/+9/+12/+15 |"), ("U28NR32B16e4", "| UMi28 C9 | −12/−9/−6/−3/+0/+3/+6 |")):
        out, D = res[T][:2]; snrs = sorted(D)
        row = key + "".join(" " + " · ".join(str(int(fails(D[s], a).sum())) for s in snrs) + " |" for a in (GENIE, V1, BSTAR, "M-ours-bstar-scalar"))
        chk(f"§6.1.4 (b) row {T}", row in sec, True)
    return res


def sec_recovery(res):
    P("\n## 3. recovery_ci files (per-SNR + pooled paired bootstrap) and R_dp(last) -- own recompute vs recovery_<T>{,last}.txt")
    for T, (cell, prior, suf, stem, bsha, lsha, kk, ll, dp, grid, bep, lep) in NEW.items():
        cp = (cell, prior)
        for tg, snr_sets in ((T, ((-3,), dp)), (T + "last", (dp,))):
            r = raw(tg); lines = []
            for snrs in snr_sets:
                lines.append(f"# recovery R = (b* - V1)/(b* - genie) @16, raw_{tg} {cell}, paired bootstrap B={B} seed={SEED}, 90% CI")
                cols = []
                for s in snrs:
                    b, v, g = (fails(r.d(cp, s), a) for a in (BSTAR, V1, GENIE)); cols.append((b, v, g))
                    (lo, hi), nn = boot_rec([(b, v, g)])
                    rr = (b.sum() - v.sum()) / (b.sum() - g.sum())
                    lines.append(f"  {s:+.0f} dB  b* {int(b.sum())}  V1 {int(v.sum())}  genie {int(g.sum())}  n={len(b)}  R = {rr:.3f}  [90% {lo:.3f}, {hi:.3f}]" + (f"  ({nn} replicates undefined)" if nn else ""))
                (lo, hi), nn = boot_rec(cols); B_, V_, G_ = (sum(c[i].sum() for c in cols) for i in range(3))
                lines.append(f"  pooled {len(cols)} SNRs  b* {int(B_)}  V1 {int(V_)}  genie {int(G_)}  R = {(B_ - V_) / (B_ - G_):.3f}  [90% {lo:.3f}, {hi:.3f}]" + (f"  ({nn} replicates undefined)" if nn else ""))
            have = [l.rstrip("\n") for l in open(os.path.join(RN, f"recovery_{tg}.txt")) if not l.startswith("b* last == A")]
            chk(f"recovery_{tg}.txt == own ({len(lines)} lines)", have == lines, True)
            if have != lines:
                for a, b in zip(have, lines):
                    if a != b:
                        P("      file: " + a); P("      own : " + b)
            if tg.endswith("last"):
                bl = [l for l in open(os.path.join(RN, f"recovery_{tg}.txt")) if l.startswith("b* last == A")]
                chk(f"recovery_{tg}.txt integrity line", bl[0].rstrip("\n"), f"b* last == A (report-only integrity, not a gate; raw_{tg} vs raw_{T}): 0 of 1344 (chunk, key) pairs differ -> OK")


def sec_frontier():
    P("\n## 4. frontier_ci: 12 primary (+Q-K runs b/c) + 3 step + C6 report files -- own recompute (frontier draw order) vs files")
    D2 = ("raw_NR32B16e4:C9:-9,-6,-3", "raw_B16e4k:C2:-3,0,3"); U28 = ("raw_U28NR32B16e4:C9:-3,0,3", "raw_U28B16e4:C2:3,6,9")
    CK = "5.2637007373767215"
    jobs = [("scale2_primary_D2_L95", D2, 0.95, ("-", "raw_B16e4"), ("-", CK), 0.05),
            ("scale2_primary_D2_L90", D2, 0.90, ("-", "raw_B16e4"), ("-", CK), 0.05),
            ("scale2_primary_D2_L95_qkC9", D2, 0.95, ("-", "-"), ("-", "-"), None),
            ("scale2_primary_D2_L95_qkC2", D2, 0.95, ("-", "raw_B16e4"), ("-", CK), None),
            ("scale2_primary_D2_L90_qkC9", D2, 0.90, ("-", "-"), ("-", "-"), None),
            ("scale2_primary_D2_L90_qkC2", D2, 0.90, ("-", "raw_B16e4"), ("-", CK), None),
            ("scale2_primary_U28_L95", U28, 0.95, ("raw_K2U28NR32B16e4", "raw_K2U28B16e4"), ("inf", "1"), 0.05),
            ("scale2_primary_U28_L90", U28, 0.90, ("raw_K2U28NR32B16e4", "raw_K2U28B16e4"), ("inf", "1"), 0.05),
            ("scale2_primary_U28_L95_qkC9", U28, 0.95, ("raw_K2U28NR32B16e4", "-"), ("inf", "-"), None),
            ("scale2_primary_U28_L95_qkC2", U28, 0.95, ("-", "raw_K2U28B16e4"), ("-", "1"), None),
            ("scale2_primary_U28_L90_qkC9", U28, 0.90, ("raw_K2U28NR32B16e4", "-"), ("inf", "-"), None),
            ("scale2_primary_U28_L90_qkC2", U28, 0.90, ("-", "raw_K2U28B16e4"), ("-", "1"), None),
            ("scale2_step_D2_S2", ("raw_NR32B16e4:C9:-9,-6,-3", "raw_NR16B16e4:C6:-3,0,3"), 0.90, ("-", "-"), ("-", "-"), 0.05),
            ("scale2_step_U28_S1", ("raw_U28NR16B16e4:C6:0,3,6", "raw_U28B16e4:C2:3,6,9"), 0.90, ("-", "-"), ("-", "-"), 0.05),
            ("scale2_step_U28_S2", ("raw_U28NR32B16e4:C9:-3,0,3", "raw_U28NR16B16e4:C6:0,3,6"), 0.90, ("-", "-"), ("-", "-"), 0.05),
            ("scale2_report_C6_dFK", ("raw_U28NR16B16e4:C6:0,3,6", "raw_NR16B16e4:C6:-3,0,3"), 0.90, ("raw_K2U28NR16B16e4", "raw_K2NR16B16e4"), ("1.3001064598543197", "1"), None)]
    L = open(os.path.join(CONF, "logs/run_scale2.log")).read().splitlines()
    for name, specs, level, ex, ck, rs in jobs:
        lines = frontier(specs[0], specs[1], level, ex, ck, rs)
        cmp_file(name, lines)
        hdr = open(os.path.join(RN, name + ".txt")).readline().rstrip("\n")
        args = f"--recovery {specs[0]} {specs[1]}" + (f" --extrap {ex[0]} {ex[1]} --ck {ck[0]} {ck[1]}" if ex != ("-", "-") or name.endswith("qkC9") and "D2" in name else "")
        logl = next(l for l in L if f"] frontier {name} (" in l)
        chk(f"{name}: header args == log line args", hdr.split(": frontier_ci.py ")[1] == logl.split(f"frontier {name} (")[1].rsplit(") rc=0", 1)[0], True, show=False)
        chk(f"{name}: header git/time", hdr.startswith("# run_scale2 git b4433d3c 2026-10-03 11:4") and (" --level" in hdr) == (name.startswith("scale2_primary")), True, show=False)


def sec_report(res):
    P("\n## 5. report-only arithmetic, SNR@0.1, ALD NMSE, Δll, predictions -- vs §6.1.4 / §6.1.6 / §6.1.1")
    txt = open(os.path.join(T2W, "conf/results/review_next/NEXT_EXPERIMENTS_SCALE16e4.md")).read().splitlines(); sec = "\n".join(txt[417:741])
    F = {"D2C9": (1161, 276, 70), "D2C6": (277, 82, 40), "D2C2": (864, 488, 125), "U28C9": (958, 599, 127), "U28C6": (824, 636, 170), "U28C2": (800, 712, 215)}
    # the counts themselves from raws
    got = {}
    for key, (tg, cell, prior, dp) in {"D2C9": ("NR32B16e4", "C9", "S2", (-9, -6, -3)), "D2C6": ("NR16B16e4", "C6", "S2", (-3, 0, 3)), "D2C2": ("B16e4k", "C2", "S2", (-3, 0, 3)),
                                       "U28C9": ("U28NR32B16e4", "C9", "UMi28", (-3, 0, 3)), "U28C6": ("U28NR16B16e4", "C6", "UMi28", (0, 3, 6)), "U28C2": ("U28B16e4", "C2", "UMi28", (3, 6, 9))}.items():
        r = raw(tg); got[key] = tuple(int(sum(fails(r.d((cell, prior), s), a).sum() for s in dp)) for a in (BSTAR, V1, GENIE))
    chk("decision-point failure sums (b*, V1, genie) x 6 cells", got, F)
    R = {k: (b - v) / (b - g) for k, (b, v, g) in F.items()}
    chk("R point values", {k: repr(v) for k, v in R.items()}, {"D2C9": "0.8111824014665444", "D2C6": "0.8227848101265823", "D2C2": "0.5087956698240866", "U28C9": "0.43200962695547535", "U28C6": "0.2874617737003058", "U28C2": "0.15042735042735042"})
    chk("Q_D2", repr(R["D2C9"] - 2 * R["D2C6"] + R["D2C2"]), "-0.3255915489625336")
    chk("Q_UMi28", repr(R["U28C9"] - 2 * R["U28C6"] + R["U28C2"]), "0.007513429982214187")
    lam = lambda a, b: float(np.log((1 - R[a]) / (1 - R[b])))
    chk("λ D2 (C9,C2), (C6,C2)", (repr(lam("D2C9", "D2C2")), repr(lam("D2C6", "D2C2"))), ("-0.9560787303601385", "-1.019495436168412"))
    chk("λ UMi28 (C9,C2), (C6,C2)", (repr(lam("U28C9", "U28C2")), repr(lam("U28C6", "U28C2"))), ("-0.4026289881346652", "-0.17589989619632507"))
    chk("F_b*/F_V1", tuple(f"{F[k][0] / F[k][1]:.4f}" for k in ("D2C9", "D2C6", "D2C2", "U28C9", "U28C6", "U28C2")), ("4.2065", "3.3780", "1.7705", "1.5993", "1.2956", "1.1236"))
    chk("Δll D2 C6 / D2 C2 / UMi28 C2", (repr(63.1751571838059 - 61.982398757574266), repr(-11.459169831224418 - (-14.636106156749378)), repr(5.797910431000217 - 5.539276756851168)),
        ("1.1927584262316344", "3.1769363255249594", "0.25863367414904914"))
    chk("Δll UMi28 C6 / C9 (§5 ll_val)", (repr(56.5879534445348 - 55.61013440427408), repr(152.23176788511105 - 150.38770163027337), repr(237.47394470961802 - 242.7371088214899)),
        ("0.9778190402607194", "1.844066254837685", "-5.263164111871873"))
    r6 = 0.9778190402607194 / (55.61013440427408 - 53.88020846319057); r9 = 1.844066254837685 / (150.38770163027337 - 148.94696809521847)
    chk("r UMi28 C6 -> c_K, r UMi28 C9 >= 1", (repr(r6), repr(max(1, r6 / (1 - r6))), repr(r9), r9 >= 1), ("0.5652375151090457", "1.3001064598543197", "1.2799495603934918", True))
    rD2 = (-11.459169831224418 - (-14.636106156749378)) / ((-14.636106156749378) - (-18.416598133332922))
    chk("r D2 C2 -> c_K", (repr(rD2), repr(rD2 / (1 - rD2))), ("0.8403499716975932", "5.2637007373767215"))
    chk("ΣF+ D2 C2 = 864 - c_K*35 (§1 '= 679.7704741918', file 'SigmaF+ = 679.77')", (f"{864 - 5.2637007373767215 * 35:.10f}", f"{864 - 5.2637007373767215 * 35:g}"), ("679.7704741918", "679.77"))
    # prediction 12 thresholds 0.15 (ΣF_b* - ΣF_V1)
    chk("pred 12 thresholds D2C6/U28C2/U28C6/U28C9", tuple(f"{0.15 * (F[k][0] - F[k][1]):g}" for k in ("D2C6", "U28C2", "U28C6", "U28C9")), ("29.25", "13.2", "28.2", "53.85"))
    chk("pred 12 ΔF_K values within (−5, +9, +27, +2)", all(d <= t for d, t in ((-5, 29.25), (9, 13.2), (27, 28.2), (2, 53.85))), True)
    # SNR@0.1 of b*, V1, genie per new cell (grid, n = 2560)
    for T, exp, ln in (("NR32B16e4", ("-6.24", "-9.22", "-11.54"), (175, 176, 178)), ("U28NR16B16e4", ("3.01", "1.60", "-2.82"), (178, 179, 181)), ("U28NR32B16e4", ("0.70", "-1.60", "-6.58"), (178, 179, 181))):
        D = res[T][1]; snrs = sorted(D)
        v = tuple(f"{snr_at(snrs, [fails(D[s], a).mean() for s in snrs], 2560)[0]:.2f}" for a in (BSTAR, V1, GENIE))
        chk(f"{T}: SNR@0.1 b*/V1/genie", v, exp)
        tl = open(os.path.join(CONF, f"results/tables_D2_{T}.txt")).read().splitlines()
        chk(f"{T}: tables lines {ln} are b*/V1/genie SNR@0.1 rows", tuple(tl[i - 1].split()[1] for i in ln), exp, show=False)
        chk(f"{T}: tables line {305 if T == 'NR32B16e4' else 308} is the b* -> V1 table-B head", tl[(305 if T == "NR32B16e4" else 308) - 1].startswith("  M-ours-bstar -> M-ours-dscore-C-V1        [decision-point anchor arm: M-ours-bstar]"), True, show=False)
        gl = open(os.path.join(CONF, f"results/guard_D2_{T}.txt")).read().splitlines()
        chk(f"{T}: guard line 16", gl[15], "NO GUARD FIRINGS in this raw set.  Every arm kept NMSE <= 10.0 and finite at every iteration of every trial.", show=False)
    # ALD test NMSE
    for suf, exp, shaexp in (("NR32", "-1.66 / -4.16 / -6.63 / -9.46 / -13.13 / -16.87 / -20.48", "3cf5d3eff96f0341"), ("U28NR16", "-6.60 / -8.81 / -11.43 / -14.22 / -17.05 / -19.82 / -22.61", "34136808b1e367ac"), ("U28NR32", "-2.26 / -3.84 / -5.52 / -7.37 / -9.58 / -12.23 / -14.83", "463da87aa8dbfb61")):
        z = np.load(os.path.join(CONF, f"results/ald/ald_PIL{suf}.npz"), allow_pickle=True)
        pl = np.load(os.path.join(CONF, f"results/ald/pilots_PIL{suf}_test.npz"), allow_pickle=True)
        own = []
        for j in range(len(z["snrs"])):
            H, hh = pl["H"][j], z["hhat"][j]
            own.append(10 * np.log10(np.mean(np.sum(np.abs(hh - H) ** 2, -1) / np.sum(np.abs(H) ** 2, -1))))
        chk(f"ald_PIL{suf}: nmse field dB", " / ".join(f"{10 * np.log10(x):.2f}" for x in z["nmse"]), exp.replace("−", "-"))
        chk(f"ald_PIL{suf}: recomputed from hhat/H (2560 trials) dB", " / ".join(f"{x:.2f}" for x in own), exp.replace("−", "-"))
        prov = json.loads(str(z["prov"]))
        chk(f"ald_PIL{suf}: ckpt_sha, prov git, ald_py_sha, n trials", (str(z["ckpt_sha"]), prov["git"], prov["ald_py_sha"], z["hhat"].shape[1]), (shaexp, "b4433d3c", "f1da04d1e91e0baf", 2560))
    # em_sec / fit_sec quoted in §6.1
    for tg, es, fs in (("NR32B16e4", "421169.2490725517", "2904.2433154582977"), ("U28NR16B16e4", "75912.80111646652", "9013.529504776001"), ("U28NR32B16e4", "128781.03982377052", "4895.238476037979"),
                       ("K2U28NR16B16e4", "72578.62030720711", None), ("K2U28NR32B16e4", "118360.95772218704", None), ("K2NR16B16e4", "33201.76065135002", None), ("K2U28B16e4", "7482.270877122879", None),
                       ("BRB16e4k", "107957.18832826614", None), ("BRNR16", "46649.95333504677", None), ("BRU28", "9133.61854147911", None)):
        r = raw(tg)
        chk(f"{tg}: meta|em_sec (and fit_sec|V1)", (r.meta1("meta|em_sec"), r.meta1("meta|fit_sec|M-ours-dscore-C-V1") if fs else None), (es, fs), show=False)
    P("  em_sec / fit_sec: 10 tags compared")
    # §6.1.1 / 6.1.2 / 6.1.4 key strings present (values from the recomputed frontier / recovery files which matched above)
    S = ["**0.811** [0.790, 0.832]", "**0.509** [0.470, 0.544]", "**+0.302 [+0.254, +0.355]**", "+0.302 [+0.262, +0.345]",
         "**0.432** [0.401, 0.463]", "**0.150** [0.108, 0.190]", "**+0.282 [+0.232, +0.335]**", "+0.282 [+0.221, +0.345]",
         "0.909 [95% 0.851, 0.968] (s\\* −4.31 dB, B_V1 0.0073, B_g 0.0030", "0.610 [95% 0.518, 0.699] (s\\* +0.93 dB, 0.0244, 0.0080", "+0.299 [95% +0.190, +0.413], p 0.0000",
         "0.558 [90% 0.486, 0.625] (s\\* +3.44 dB, 0.0238, 0.0030", "0.218 [90% 0.120, 0.322] (s\\* +8.93 dB, 0.0413, 0.0104", "+0.339 [90% +0.210, +0.460], p 0.0010",
         "+0.466 [95% +0.294, +0.770], p 0.0000", "+0.466 [90% +0.315, +0.710]", "b*(K/2) 899  dF = +35  c_K = 5.2637  SigmaF+ = 679.77  R+ = 0.346  [90% 0.106, 0.492]",
         "b*(K/2) 960  dF = +2  c_K = inf  (r >= 1)  [K 상한 민감: 외삽 불가]", "b*(K/2) 809  dF = +9  c_K = 1  SigmaF+ = 791  R+ = 0.137  [90% 0.071, 0.185]",
         "PILNR32 (D2 C9, −12..+6) −1.66 / −4.16 / −6.63 / −9.46 / −13.13 / −16.87 / −20.48 dB", "PILU28NR16 (UMi28 C6, −3..+15) −6.60 / −8.81 / −11.43 / −14.22 / −17.05 / −19.82 / −22.61 dB",
         "PILU28NR32 (UMi28 C9, −12..+6) −2.26 / −3.84 / −5.52 / −7.37 / −9.58 / −12.23 / −14.83 dB",
         "| 0.811 · 0.287 · 0.432 |", "둘 다 강건; +0.299, +0.339", "0.190461 · 0.880615 · 0.836979, 0.837 < 0.881", "| +2.99, +2.29 |", "642 < 752", "6/6 (i) (1276:25, 1244:27, 434:33, 348:41, 369:25, 348:31)",
         "D2 C6 −5 ≤ 29.25, UMi28 C2 +9 ≤ 13.2, UMi28 C6 +27 ≤ 28.2, UMi28 C9 +2 ≤ 53.85", "UMi28 C6 662 ✓, UMi28 C9 252 ✗ (§5); D2 C9 250 ✗",
         "BRB16e4k 116f9f39fdff840f (:32), K2NR16B16e4 5f18c69f99ce4d34 (:36), BRNR16 df23c83552a360b4 (:39), K2U28B16e4 af426876fd7d9a24 (:44), BRU28 5f69f58ab3f09779 (:47)",
         "NR32B16e4last 96c82d63940fa78e (:148)", "UMi28 C9 계열 1394.4 min", "D2 C9 계열 1063.5 min", "UMi28 C6 계열 207.2 min", "재사용 K2·bridge 57.9 min",
         "D2 C9 421169.2490725517 / 2904.2433154582977, UMi28 C6 75912.80111646652 / 9013.529504776001, UMi28 C9 128781.03982377052 / 4895.238476037979",
         "BRB16e4k 107957.18832826614, BRNR16 46649.95333504677, BRU28 9133.61854147911", "경과 2733 분 (45 h 33 min",
         "+0.295 [95% +0.226, +0.384]", "[90% +0.238, +0.369]",
         "−0.012 [−0.067, +0.041] · p 0.7200", "+0.137 [+0.085, +0.193] · p 0.0000", "+0.145 [+0.099, +0.193] · p 0.0000", "0.823 [0.774, 0.874]", "0.287 [0.252, 0.322]", "0.287 [0.252, 0.323]",
         "+0.102 [90% +0.030, +0.175], p 0.0180", "0.909 [0.860, 0.959]", "0.806 [0.752, 0.860]", "+0.087 [90% −0.042, +0.216], p 0.2910", "0.305 [0.226, 0.386], s\\* +5.52 dB", "+0.252 [90% +0.140, +0.352], p 0.0000",
         "206 [182, 231] / 1091 [1045, 1135]", "363 [332, 396] / 739 [697, 781]", "42 [29, 54] / 237 [213, 263]", "472 [437, 505] / 831 [786, 871]", "497 [461, 532] / 585 [547, 623]", "466 [432, 501] / 654 [616, 696]", "[433, 502] / [614, 696]",
         "**0.808 [0.786, 0.829]** (1161 · 280 · 70)", "−9 0.782 · −6 0.883 · −3 0.870", "**0.278 [0.243, 0.313]** (824 · 642 · 170)", "+0 0.259 · +3 0.306 · +6 0.283", "**0.439 [0.409, 0.469]** (958 · 593 · 127)", "−3 0.366 · +0 0.496 · +3 0.551",
         "0.922 [0.851, 0.986] (b\\* 81 · V1 10 · genie 4", "0.780 [0.754, 0.806] / 0.887 [0.840, 0.930]", "0.228 [0.190, 0.266] (752 · 642 · 269", "0.262 [0.211, 0.310] / 0.320 [0.260, 0.378] / 0.303 [0.206, 0.396], 합 0.287 [0.253, 0.322]",
         "0.380 [0.339, 0.421] (509 · 349 · 88), +0/+3 0.453 [0.398, 0.506] / 0.551 [0.479, 0.628], 합 0.432 [0.402, 0.462]",
         "851 · **+27** (ΣF⁺ 788.897, R⁺ 0.247 [90% 0.186, 0.302], 0.0 %)", "272 · **−5** (`[K 상한 강건 (K/2 가 더 낫지 않음, ΔF_K = -5)]`, R⁺ 0.823 [90% 0.767, 0.872])",
         "+2.99 dB [+2.72, +3.25]", "+1.41 dB [+1.08, +1.67]", "+2.29 dB [+1.98, +2.61]", "914:29 (3.7e-229)", "232:44 (5.1e-32)", "391:32 (1.3e-79)",
         "D2 C9 b\\* −6.24 · V1 −9.22 · genie −11.54", "UMi28 C6 3.01 · 1.60 · −2.82", "UMi28 C9 0.70 · −1.60 · −6.58",
         "**Q_D2 = R_C9 − 2R_C6 + R_C2 = −0.3255915489625336**", "**Q_UMi28 = +0.007513429982214187**",
         "적중 13 (1, 2, 6, 7, 8, 9, 10, 11, 13, 15, 16, 17, 18), 빗나감 5 (3, 4, 5, 12, 14)"]
    miss = [s for s in S if s not in sec]
    chk(f"§6.1 key value strings present ({len(S)})", miss, [])
    # EXPERIMENTS row / DECISIONS line
    E = ["| 2026-10-02 04:16 ~ 10-04 01:49 KST (텍사스 10-01 14:16 ~ 10-03 11:49 CDT) |", "| b4433d3c (= §5 커밋; 동결 16a9dff6 과 conf/code·Demo 동일) |", "SCALE2_DONE ok=101 fail=0",
         "D2 ΔR = R_C9 − R_C2 = 0.811 − 0.509 = +0.302 [95% +0.254, +0.355] (T+) [운영점 정합 강건][K 상한 강건]", "UMi28 0.432 − 0.150 = +0.282 [90% +0.232, +0.335] (T+) [운영점 정합 강건][K 상한 민감: 외삽 불가] (r ≥ 1 강제)",
         "2차 D2 S2 −0.012 [90% −0.067, +0.041] 판정하지 못함, UMi28 S1 +0.137·S2 +0.145 증가 (단조 증가)", "표 B b\\* → V1 3/3 (i); 𝔅 36 (i) 36·(ii) 0", "§3 예측 적중 13·빗나감 5 (3, 4, 5, 12, 14)", "eval 45 h 33 min",
         "R_dp(last) 0.808 / 0.278 / 0.439, `b* last == A` 3/3 OK", "`frontier_ci` 16", "`pair_baselines` 3"]
    chk(f"EXPERIMENTS row strings ({len(E)})", [s for s in E if s not in LAST_EXP], [])
    chk("EXPERIMENTS row has 8 cells", len(LAST_EXP.strip().strip("|").split("|")), 8)
    Dd = ["[2026-10-04 02:06 KST] SCALE16e4 결과 기록 (Opus 5.5; 텍사스 10-03 12:06 CDT)", "estimate 10-01 14:03~14:16 CDT (GPU 0) → eval 10-01 14:16 ~ 10-03 11:49 CDT, SCALE2_DONE ok=101 fail=0, 재개 없음",
          "실행 커밋 b4433d3c (= §5 커밋, 동결 16a9dff6 과 conf/code·Demo 동일, raw run|git 22 태그 전부 b4433d3c)", "판정점 D2 C9 −9/−6/−3, UMi28 C6 0/+3/+6, UMi28 C9 −3/0/+3",
          "D2 ΔR +0.302 [95% +0.254, +0.355] (T+)", "UMi28 ΔR +0.282 [90% +0.232, +0.335] (T+)", "D2 S2 판정하지 못함 (−0.012), UMi28 S1·S2 증가 → UMi28 단조 증가",
          "표 B 3/3 (i); 𝔅 36 (i) 36·(ii) 0", "§3 예측 적중 13·빗나감 5 (3·4·5·12·14)", "(k) worker_gb {8.0}·jobs 99"]
    chk(f"DECISIONS line strings ({len(Dd)})", [s for s in Dd if s not in LAST_DEC], [])


def main():
    P("# scale_recompute.py -- SCALE16e4 §6.1 record audit, own recomputation (no project analysis code called)")
    P("# python", sys.version.split()[0], "numpy", np.__version__, "| CUDA_VISIBLE_DEVICES =", repr(os.environ.get("CUDA_VISIBLE_DEVICES")))
    sec_git()
    sec_raw()
    res = sec_pair()
    sec_recovery(res)
    sec_frontier()
    sec_report(res)
    P(f"\n## SUMMARY: checks {CHECKS[0]}, mismatches {CHECKS[1]}")
    for m in MIS:
        P("  MISMATCH:", m)


if __name__ == "__main__":
    main()
