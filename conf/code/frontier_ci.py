"""conf/code/frontier_ci.py -- UNPAIRED bootstrap CIs across raw sets / cells (NEXT_EXPERIMENTS_PARETO §1, _D3B16e4 §1,
_SVB16e4 §1, _38901 §1).  Report-only arithmetic on raw files; nothing here selects, judges or stops anything.

Within ONE cell of ONE raw set the arms share their trial streams, so a replicate resamples the trial indices of a
(raw set, cell, SNR) point ONCE and applies them to every arm read from that point (paired within a cell, exactly as
analysis.gain).  Two different cells, or two different raw sets (a different prior or tag = different streams), are
resampled independently -- an UNPAIRED comparison.  B = 2000, numpy.random.default_rng(20260926), percentiles 5/95 (90%)
and 2.5/97.5 (95%; the Holm m=2 level of the Pareto registration); the Holm order is the bootstrap two-sided
p = 2 min(P[D* <= 0], P[D* >= 0]) printed with each Delta.  A replicate whose SNR@0.1 is off the grid ('lo'/'hi'
of exp_0925_analysis.snr_at) is censored and counted, never clamped.

    --pair "A=raw_B16e4k+raw_PARB16e4:C2:M-ours-dscore-C-V1" "B=raw_PARB16e4:C7:M-ours-bstar"   (repeatable)
        SNR@0.1 of A and of B (each with its CI) and Delta = A - B.  RAW1+RAW2 merges disjoint SNR points of one cell
        (same weights, fits and trial rule -- the Pareto C2 curve = raw_B16e4k -3..15 plus the -6 dB point of the tag).
    --recovery "raw_D3B16e4:C2:-3" "raw_B16e4k:C2:-3"
        recovery R = (b* - V1)/(b* - genie) @16 of each (paired bootstrap, as recovery_ci.py) and R1 - R2 unpaired.
        SNRs after the cell are comma-separated and pooled (failure counts summed) before the ratio.
        Added lines (NEXT_EXPERIMENTS_SCALE16e4 §1; the lines above stay bit-identical, their draws are untouched):
        R1 - R2 at --level (0.90 default; 0.95 = the Holm first test) with the bootstrap two-sided p = min(1, 2 min(
        P[D* <= 0], P[D* >= 0])), and per spec the absolute gaps SigmaF_V1 - SigmaF_g, SigmaF_b* - SigmaF_g (90%).
      --extrap K2_1 K2_2 --ck C1 C2   (Q-K, a SENSITIVITY analysis, not a bound; '-' = K_max interior, b*+ = b*)
        the K/2 raw's b* column at the spec's points, resampled with the BASE raw's indices (same trials; genie must be
        bit-identical); dF = SigmaF_b*(K/2) - SigmaF_b*(K_max), SigmaF+ = SigmaF_b*(K_max) - c_K max(0, dF) per replicate
        and at the point; R+ uses SigmaF+ for SigmaF_b*.  c_K = max(1, r/(1-r)) from the section-5 ll_val; 'inf' = r >= 1.
      --rstar 0.05   (Q-OP) R* = (t - B_V1(s*))/(t - B_g(s*)), s* = first downward crossing of t by b* (snr_at rule),
        B_V1 / B_g = 10^ of the linear interpolation of log10 max(BLER, 0.5/n) between the grid points bracketing s*;
        every grid point of the cell is resampled (its OWN Resampler: the R lines keep their draws), s* recomputed per
        replicate; undefined = 'lo' / 'hi' / B_g(s*) >= t.  R*1 - R*2 at --level with p.
    --goodput raw_B16e4k+raw_PARB16e4:C2 raw_PARB16e4:C7 raw_PARB16e4:C8 --arms M-ours-bstar M-ours-dscore-C-V1 R5-genie
        per SNR and arm: K (1 - BLER@16) / T per cell and the envelope max over cells (08_SPEC §3 table C definition,
        K = Nt (T - Tp) - 6).  No CI, report only.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import numpy as np
from analysis import load_raw, snr_at, fmt_at

SEED, B = 20260926, 2000
REC_ARMS = ("M-ours-bstar", "M-ours-dscore-C-V1", "R5-genie")
_CACHE, _META = {}, {}


def raws(spec):
    """'raw_A+raw_B' -> merged {(cell, prior, snr): {arm: {...}}}; overlapping points are an error (not a silent choice)."""
    if spec not in _CACHE:
        data = {}
        for r in spec.split("+"):
            d, m, _ = load_raw("D2", root=os.path.join(C.CONF, r))
            _META.update({(spec, k): v for k, v in m.items()})
            dup = set(d) & set(data)
            assert not dup, f"{spec}: point(s) {sorted(dup)} appear in more than one raw set"
            data.update(d)
        _CACHE[spec] = data
    return _CACHE[spec]


def points(data, cell):
    keys = sorted((k for k in data if k[0] == cell), key=lambda k: k[2])
    assert keys, f"no points of cell {cell}"
    return keys


def fails(data, key, arm):
    v = np.asarray(data[key][arm]["blk_err"])[:, -1]
    return np.where(np.isfinite(v), v, 1.0)                         # a raised block is a failure (01_RULES §4)


class Resampler:
    """One index draw per (raw spec, cell, snr) per replicate: paired within a point, independent across points.
    take(BASE spec, key, x) on another raw's column of the same trials reuses the base draw (Q-K's K/2 b* column)."""

    def __init__(self, seed):
        self.rng = np.random.default_rng(seed)
        self.idx = {}

    def new_replicate(self):
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
    """-> (lo, hi, p): percentile CI at `level` and the bootstrap two-sided p = min(1, 2 min(P[D*<=0], P[D*>=0])), defined replicates."""
    q = round(50 * (1 - level), 9)                                  # 0.90 -> exactly 5 / 95, 0.95 -> 2.5 / 97.5
    lo, hi = pct(d, [q, 100 - q])
    df = d[np.isfinite(d)]
    return lo, hi, (min(1.0, 2 * min(np.mean(df <= 0), np.mean(df >= 0))) if len(df) else np.nan)


def cmd_pair(pairs, nb, seed):
    print(f"# SNR@0.1 (log-linear interpolation of log10 max(BLER@16, 0.5/n), first downward crossing; exp_0925_analysis.snr_at)")
    print(f"# UNPAIRED bootstrap across cells / raw sets, paired within a (raw, cell, SNR) point; B={nb}, seed={seed}; "
          f"censored = replicate off the grid ('lo' / 'hi'), never clamped")
    for pa, pb in pairs:
        specs = []
        for s in (pa, pb):
            name, rest = s.split("=", 1)
            raw, cell, arm = rest.split(":")
            d = raws(raw)
            keys = points(d, cell)
            specs.append((name, raw, cell, arm, keys, [fails(d, k, arm) for k in keys]))
        rs = Resampler(seed)
        est, boots = [], []
        for name, raw, cell, arm, keys, cols in specs:
            snrs = [k[2] for k in keys]
            n = min(len(c) for c in cols)
            v, f = snr_at(snrs, [c.mean() for c in cols], n)
            est.append((v, f, snrs, n))
        bo = np.full((nb, 2), np.nan)
        for i in range(nb):
            rs.new_replicate()
            for j, (name, raw, cell, arm, keys, cols) in enumerate(specs):
                snrs = [k[2] for k in keys]
                m = [rs.take(raw, k, c).mean() for k, c in zip(keys, cols)]
                v, f = snr_at(snrs, m, est[j][3])
                bo[i, j] = v if f == "ok" else np.nan
        for j, (name, raw, cell, arm, keys, cols) in enumerate(specs):
            v, f, snrs, n = est[j]
            lo, hi = pct(bo[:, j], [5, 95])
            print(f"  {name}: {raw} {cell} {arm}  grid {[f'{s:+.0f}' for s in snrs]} n={n}  SNR@0.1 = {fmt_at(v, f).strip()} dB"
                  f"  [90% {lo:+.2f}, {hi:+.2f}; censored {100 * np.mean(~np.isfinite(bo[:, j])):.1f}%]")
        d = bo[:, 0] - bo[:, 1]
        (fa, fb) = est[0][1], est[1][1]
        if fa == fb == "ok":
            l90, h90 = pct(d, [5, 95]); l95, h95 = pct(d, [2.5, 97.5])
            df = d[np.isfinite(d)]                         # bootstrap two-sided p (Holm ordering, NEXT_EXPERIMENTS_PARETO §1)
            pb = 2 * min(np.mean(df <= 0), np.mean(df >= 0)) if len(df) else np.nan
            print(f"  Delta = {specs[0][0]} - {specs[1][0]} = {est[0][0] - est[1][0]:+.2f} dB  [90% {l90:+.2f}, {h90:+.2f}]  "
                  f"[95% {l95:+.2f}, {h95:+.2f}]  bootstrap two-sided p = {pb:.4f}  censored replicates {100 * np.mean(~np.isfinite(d)):.1f}%")
        else:
            print(f"  Delta = {specs[0][0]} - {specs[1][0]}: n/a (point estimate off the grid: {fmt_at(*est[0][:2]).strip()} vs "
                  f"{fmt_at(*est[1][:2]).strip()}) -- no CI is formed")
        print()


def _rec_cols(spec):
    raw, cell, snrs = spec.split(":")
    d = raws(raw)
    keys = [k for k in points(d, cell) if any(abs(k[2] - float(s)) < 1e-9 for s in snrs.split(","))]
    assert len(keys) == len(snrs.split(",")), f"{spec}: SNR(s) missing in {raw} {cell}"
    return raw, cell, keys, [tuple(fails(d, k, a) for a in REC_ARMS) for k in keys]


def _R(cols):
    b = sum(c[0].sum() for c in cols); v = sum(c[1].sum() for c in cols); g = sum(c[2].sum() for c in cols)
    return (b - v) / (b - g) if b - g > 0 else np.nan, (int(b), int(v), int(g))


def _k2_cols(k2, st):
    """K/2 raw's b* failure columns at the base spec's points; the trials must be the base's (genie bit-identical)."""
    raw, cell, keys, cols = st
    d = raws(k2)
    for k, c in zip(keys, cols):
        assert k in d, f"{k2}: point {k} missing"
        assert np.array_equal(fails(d, k, REC_ARMS[2]), c[2]), f"{k2} {k}: genie differs from {raw} -- not the same trials"
    return [fails(d, k, REC_ARMS[0]) for k in keys]


def _Rplus(b, v, g, bk2, ck):
    """Q-K: SigmaF+ = SigmaF_b*(K_max) - c_K max(0, dF), dF = SigmaF_b*(K/2) - SigmaF_b*(K_max) -> (R+, SigmaF+, dF)."""
    dF = bk2 - b
    fp = b - ck * max(0.0, dF)
    return ((fp - v) / (fp - g) if fp - g > 0 else np.nan), fp, dF


def _rstar(snrs, cols, n, t):
    """Q-OP R*@t at one (raw, cell) curve: cols = per grid point (b*, V1, genie) failure columns -> (R*, flag, s*, B_V1, B_g)."""
    bl = [np.array([c[a].mean() for c in cols]) for a in range(3)]
    s, f = snr_at(snrs, bl[0], n, target=t)
    if f != "ok":
        return np.nan, f, s, np.nan, np.nan
    bv, bg = (10 ** np.interp(s, snrs, np.log10(np.maximum(x, 0.5 / n))) for x in bl[1:])   # bracketing grid points
    return ((t - bv) / (t - bg) if bg < t else np.nan), ("ok" if bg < t else "g"), s, bv, bg


def cmd_recovery(s1, s2, nb, seed, level=0.90, extrap=None, ck=None, rstar=None):
    print(f"# recovery R = (b* - V1)/(b* - genie) @16; paired bootstrap per raw set (three arms together), the two raw sets "
          f"resampled independently (UNPAIRED difference); B={nb}, seed={seed}, 90% CI")
    sets = [_rec_cols(s1), _rec_cols(s2)]
    extrap, ck = extrap or ("-", "-"), ck or ("-", "-")
    k2 = [None if e == "-" else _k2_cols(e, st) for e, st in zip(extrap, sets)]
    ck = [None if e == "-" else float(c) for e, c in zip(extrap, ck)]
    rs = Resampler(seed)
    bo, bp, fpg = (np.full((nb, 2), np.nan) for _ in range(3))     # R, R+, SigmaF+ - SigmaF_g
    ga = np.full((nb, 2, 2), np.nan)                               # SigmaF_V1 - SigmaF_g, SigmaF_b* - SigmaF_g
    for i in range(nb):
        rs.new_replicate()
        for j, (raw, cell, keys, cols) in enumerate(sets):
            rc = [tuple(rs.take(raw, k, x) for x in c) for k, c in zip(keys, cols)]
            bo[i, j], (b, v, g) = _R(rc)
            ga[i, j] = v - g, b - g
            if k2[j] is None:
                bp[i, j] = bo[i, j]
            elif np.isfinite(ck[j]):
                bk2 = sum(rs.take(raw, k, x).sum() for k, x in zip(keys, k2[j]))     # BASE raw's keys = same trial indices
                bp[i, j], fp, _ = _Rplus(b, v, g, bk2, ck[j])
                fpg[i, j] = fp - g
    for j, (raw, cell, keys, cols) in enumerate(sets):
        r, (b, v, g) = _R(cols)
        lo, hi = pct(bo[:, j], [5, 95])
        print(f"  R{j + 1}: {raw} {cell} SNR {[f'{k[2]:+.0f}' for k in keys]}  b* {b} V1 {v} genie {g}  R = {r:.3f}  [90% {lo:.3f}, {hi:.3f}]"
              + (f"  ({int((~np.isfinite(bo[:, j])).sum())} replicates undefined)" if (~np.isfinite(bo[:, j])).any() else ""))
    d = bo[:, 0] - bo[:, 1]
    r1, r2 = _R(sets[0][3])[0], _R(sets[1][3])[0]
    lo, hi = pct(d, [5, 95])
    print(f"  R1 - R2 = {r1 - r2:+.3f}  [90% unpaired {lo:+.3f}, {hi:+.3f}]  undefined replicates {int((~np.isfinite(d)).sum())}")
    L = f"{100 * level:g}%"
    lo, hi, p = ci_p(d, level)
    print(f"  R1 - R2 = {r1 - r2:+.3f}  [{L} unpaired {lo:+.3f}, {hi:+.3f}]  bootstrap two-sided p = {p:.4f}  (--level {level:g})")
    for j, (raw, cell, keys, cols) in enumerate(sets):
        _, (b, v, g) = _R(cols)
        (l1, h1), (l2, h2) = pct(ga[:, j, 0], [5, 95]), pct(ga[:, j, 1], [5, 95])
        print(f"  gaps R{j + 1}: SigmaF_V1 - SigmaF_g = {v - g}  [90% {l1:.0f}, {h1:.0f}]   SigmaF_b* - SigmaF_g = {b - g}  [90% {l2:.0f}, {h2:.0f}]"
              f"   (blocks, summed over SNR {[f'{k[2]:+.0f}' for k in keys]})")
    rp = [r1, r2]
    if any(x is not None for x in k2):
        print(f"# Q-K (K upper-limit SENSITIVITY, not a bound): dF = SigmaF_b*(K/2) - SigmaF_b*(K_max), SigmaF+ = SigmaF_b*(K_max) - "
              f"c_K max(0, dF), R+ = (SigmaF+ - SigmaF_V1)/(SigmaF+ - SigmaF_g); the K/2 b* column resampled with the BASE raw's indices")
    for j, (raw, cell, keys, cols) in enumerate(sets):
        if k2[j] is None:
            continue
        _, (b, v, g) = _R(cols)
        bk2 = int(sum(x.sum() for x in k2[j]))
        K = [_META.get((sp, (cell, keys[0][1])), {}).get("kron_K") for sp in (raw, extrap[j])]
        head = f"  R{j + 1}+: {raw} {cell} kron_K {K[0]}  K/2 raw {extrap[j]} kron_K {K[1]}  b*(K/2) {bk2}  dF = {bk2 - b:+d}  c_K = {ck[j]:g}"
        if not np.isfinite(ck[j]):
            rp[j] = np.nan
            print(head + "  (r >= 1)  [K 상한 민감: 외삽 불가]")
            continue
        rp[j], fp, dF = _Rplus(b, v, g, bk2, ck[j])
        lo, hi = pct(bp[:, j], [5, 95])
        und = np.mean(~(fpg[:, j] > 0))
        q = ("[K 상한 민감: 외삽 불가]" if und > 0.05 or not np.isfinite(rp[j]) else
             f"[K 상한 강건 (K/2 가 더 낫지 않음, ΔF_K = {dF:+.0f})]" if dF <= 0 else "")
        print(head + f"  SigmaF+ = {fp:g}  R+ = {rp[j]:.3f}  [90% {lo:.3f}, {hi:.3f}]  SigmaF+ <= SigmaF_g in {100 * und:.1f}% of replicates  {q}")
    if any(x is not None for x in k2):
        dp = bp[:, 0] - bp[:, 1]
        if np.isfinite(rp[0] - rp[1]):
            lo, hi, p = ci_p(dp, level)
            print(f"  R1+ - R2+ = {rp[0] - rp[1]:+.3f}  [{L} unpaired {lo:+.3f}, {hi:+.3f}]  bootstrap two-sided p = {p:.4f}  "
                  f"undefined replicates {int((~np.isfinite(dp)).sum())}")
        else:
            print("  R1+ - R2+: n/a (Q-K undefined)")
    if rstar is not None:
        cmd_rstar(sets, nb, seed, level, rstar)
    return dict(bo=bo, bp=bp, r=(r1, r2), rp=rp)


def cmd_rstar(sets, nb, seed, level, t):
    """Q-OP: R*@t per spec over the cell's WHOLE grid, own Resampler (the R_dp draws above stay bit-identical)."""
    print(f"# Q-OP R*@{t:g} = ({t:g} - B_V1(s*))/({t:g} - B_g(s*)); s* = first downward crossing of {t:g} by b* (log10 max(BLER, 0.5/n) "
          f"linear interpolation, snr_at); all grid points of the cell resampled (three arms together), s* recomputed per replicate; "
          f"B={nb}, seed={seed} (own draw), {100 * level:g}% CI; undefined = lo / hi / B_g(s*) >= {t:g}")
    cur = []
    for raw, cell, keys, _ in sets:
        d = raws(raw)
        ks = points(d, cell)
        cols = [tuple(fails(d, k, a) for a in REC_ARMS) for k in ks]
        cur.append((raw, cell, [k[2] for k in ks], ks, cols, min(len(c[0]) for c in cols)))
    rs = Resampler(seed)
    bo, fl = np.full((nb, 2), np.nan), np.empty((nb, 2), dtype=object)
    for i in range(nb):
        rs.new_replicate()
        for j, (raw, cell, snrs, ks, cols, n) in enumerate(cur):
            bo[i, j], fl[i, j] = _rstar(snrs, [tuple(rs.take(raw, k, x) for x in c) for k, c in zip(ks, cols)], n, t)[:2]
    q = round(50 * (1 - level), 9)
    est = []
    for j, (raw, cell, snrs, ks, cols, n) in enumerate(cur):
        r, f, s, bv, bg = _rstar(snrs, cols, n, t)
        est.append(r)
        lo, hi = pct(bo[:, j], [q, 100 - q])
        und = np.mean(~np.isfinite(bo[:, j]))
        cnt = {x: int((fl[:, j] == x).sum()) for x in ("lo", "hi", "g")}
        pt = f"s* = {s:+.2f} dB  B_V1(s*) = {bv:.4f}  B_g(s*) = {bg:.4f}  R* = {r:.3f}" if f == "ok" else \
            f"R* undefined ({'B_g(s*) >= t' if f == 'g' else fmt_at(s, f).strip() + ' dB'})"
        print(f"  R*{j + 1}: {raw} {cell} grid {[f'{x:+.0f}' for x in snrs]} n={n}  {pt}  [{100 * level:g}% {lo:.3f}, {hi:.3f}]  "
              f"undefined replicates {100 * und:.1f}% (lo {cnt['lo']}, hi {cnt['hi']}, B_g>=t {cnt['g']})"
              + ("  [운영점 한정어 정의 불가]" if und > 0.05 or f != "ok" else ""))
    d = bo[:, 0] - bo[:, 1]
    if np.isfinite(est[0] - est[1]):
        lo, hi, p = ci_p(d, level)
        print(f"  R*1 - R*2 = {est[0] - est[1]:+.3f}  [{100 * level:g}% unpaired {lo:+.3f}, {hi:+.3f}]  bootstrap two-sided p = {p:.4f}  "
              f"undefined replicates {int((~np.isfinite(d)).sum())}")
    else:
        print("  R*1 - R*2: n/a (R* undefined at the point estimate)")
    return est


def cmd_goodput(specs, arms):
    print("# goodput K (1 - BLER@16) / T per cell and the envelope (max over cells) per SNR and arm; K = Nt (T - Tp) - 6; report only")
    cells = []
    for s in specs:
        raw, cell = s.split(":")
        c = C.CELLS[cell]
        cells.append((raw, cell, c["Nt"] * (c["T"] - c["Tp"]) - 6, c["T"], raws(raw)))
    snrs = sorted({k[2] for _, _, _, _, d in cells for k in d})
    hdr = "  ".join(f"{cell}(Tp={C.CELLS[cell]['Tp']},K={K})" for _, cell, K, _, _ in cells)
    for arm in arms:
        print(f"\n  arm {arm}:  SNR | {hdr} | envelope (cell)")
        for s in snrs:
            vals = []
            for raw, cell, K, T, d in cells:
                keys = [k for k in d if k[0] == cell and abs(k[2] - s) < 1e-9]
                vals.append((K * (1 - fails(d, keys[0], arm).mean()) / T, cell) if keys else (np.nan, cell))
            best = max((v for v in vals if np.isfinite(v[0])), default=(np.nan, "-"))
            print(f"  {s:+5.0f} | " + "  ".join(f"{v:.3f}" if np.isfinite(v) else "  -  " for v, _ in vals)
                  + f" | {best[0]:.3f} ({best[1]})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pair", nargs=2, action="append", metavar=("A=RAWS:CELL:ARM", "B=RAWS:CELL:ARM"))
    ap.add_argument("--recovery", nargs=2, metavar=("RAW:CELL:SNRS", "RAW:CELL:SNRS"))
    ap.add_argument("--goodput", nargs="+", metavar="RAWS:CELL")
    ap.add_argument("--level", type=float, default=0.90, help="CI level of the --recovery difference lines (0.95 = Holm first test)")
    ap.add_argument("--extrap", nargs=2, metavar=("K2_OF_1", "K2_OF_2"), help="Q-K: K/2 raw of each --recovery spec, '-' = interior")
    ap.add_argument("--ck", nargs=2, metavar=("C1", "C2"), help="Q-K c_K = max(1, r/(1-r)) per spec ('inf' = r >= 1, '-' = interior)")
    ap.add_argument("--rstar", type=float, metavar="T", help="Q-OP R*@T (0.05) for both --recovery specs")
    ap.add_argument("--arms", nargs="+", default=list(REC_ARMS))
    ap.add_argument("--B", type=int, default=B)
    ap.add_argument("--seed", type=int, default=SEED)
    a = ap.parse_args()
    if (a.extrap or a.ck or a.rstar is not None) and not a.recovery:
        ap.error("--extrap / --ck / --rstar need --recovery")
    if bool(a.extrap) != bool(a.ck) or (a.extrap and any((e == "-") != (c == "-") for e, c in zip(a.extrap, a.ck))):
        ap.error("--extrap and --ck go together, '-' in the same positions")
    if a.ck and any(c != "-" and not float(c) >= 1 for c in a.ck):
        ap.error("c_K = max(1, r/(1-r)) >= 1 ('inf' when r >= 1)")
    if a.pair:
        cmd_pair(a.pair, a.B, a.seed)
    if a.recovery:
        cmd_recovery(*a.recovery, a.B, a.seed, a.level, a.extrap, a.ck, a.rstar)
    if a.goodput:
        cmd_goodput(a.goodput, a.arms)


if __name__ == "__main__":
    main()
