"""conf/code/frontier_ci.py -- UNPAIRED bootstrap CIs across raw sets / cells (NEXT_EXPERIMENTS_PARETO §1, _D3B16e4 §1,
_SVB16e4 §1, _38901 §1).  Report-only arithmetic on raw files; nothing here selects, judges or stops anything.

Within ONE cell of ONE raw set the arms share their trial streams, so a replicate resamples the trial indices of a
(raw set, cell, SNR) point ONCE and applies them to every arm read from that point (paired within a cell, exactly as
analysis.gain).  Two different cells, or two different raw sets (a different prior or tag = different streams), are
resampled independently -- an UNPAIRED comparison.  B = 2000, numpy.random.default_rng(20260926), percentiles 5/95 (90%)
and 2.5/97.5 (95%; the Holm m=2 level of the Pareto registration).  A replicate whose SNR@0.1 is off the grid ('lo'/'hi'
of exp_0925_analysis.snr_at) is censored and counted, never clamped.

    --pair "A=raw_B16e4k+raw_PARB16e4:C2:M-ours-dscore-C-V1" "B=raw_PARB16e4:C7:M-ours-bstar"   (repeatable)
        SNR@0.1 of A and of B (each with its CI) and Delta = A - B.  RAW1+RAW2 merges disjoint SNR points of one cell
        (same weights, fits and trial rule -- the Pareto C2 curve = raw_B16e4k -3..15 plus the -6 dB point of the tag).
    --recovery "raw_D3B16e4:C2:-3" "raw_B16e4k:C2:-3"
        recovery R = (b* - V1)/(b* - genie) @16 of each (paired bootstrap, as recovery_ci.py) and R1 - R2 unpaired.
        SNRs after the cell are comma-separated and pooled (failure counts summed) before the ratio.
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
_CACHE = {}


def raws(spec):
    """'raw_A+raw_B' -> merged {(cell, prior, snr): {arm: {...}}}; overlapping points are an error (not a silent choice)."""
    if spec not in _CACHE:
        data = {}
        for r in spec.split("+"):
            d, _, _ = load_raw("D2", root=os.path.join(C.CONF, r))
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
    """One index draw per (raw spec, cell, snr) per replicate: paired within a point, independent across points."""

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
            print(f"  Delta = {specs[0][0]} - {specs[1][0]} = {est[0][0] - est[1][0]:+.2f} dB  [90% {l90:+.2f}, {h90:+.2f}]  "
                  f"[95% {l95:+.2f}, {h95:+.2f}]  censored replicates {100 * np.mean(~np.isfinite(d)):.1f}%")
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


def cmd_recovery(s1, s2, nb, seed):
    print(f"# recovery R = (b* - V1)/(b* - genie) @16; paired bootstrap per raw set (three arms together), the two raw sets "
          f"resampled independently (UNPAIRED difference); B={nb}, seed={seed}, 90% CI")
    sets = [_rec_cols(s1), _rec_cols(s2)]
    rs = Resampler(seed)
    bo = np.full((nb, 2), np.nan)
    for i in range(nb):
        rs.new_replicate()
        for j, (raw, cell, keys, cols) in enumerate(sets):
            rc = [tuple(rs.take(raw, k, x) for x in c) for k, c in zip(keys, cols)]
            bo[i, j] = _R(rc)[0]
    for j, (raw, cell, keys, cols) in enumerate(sets):
        r, (b, v, g) = _R(cols)
        lo, hi = pct(bo[:, j], [5, 95])
        print(f"  R{j + 1}: {raw} {cell} SNR {[f'{k[2]:+.0f}' for k in keys]}  b* {b} V1 {v} genie {g}  R = {r:.3f}  [90% {lo:.3f}, {hi:.3f}]"
              + (f"  ({int((~np.isfinite(bo[:, j])).sum())} replicates undefined)" if (~np.isfinite(bo[:, j])).any() else ""))
    d = bo[:, 0] - bo[:, 1]
    r1, r2 = _R(sets[0][3])[0], _R(sets[1][3])[0]
    lo, hi = pct(d, [5, 95])
    print(f"  R1 - R2 = {r1 - r2:+.3f}  [90% unpaired {lo:+.3f}, {hi:+.3f}]  undefined replicates {int((~np.isfinite(d)).sum())}")


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
    ap.add_argument("--arms", nargs="+", default=list(REC_ARMS))
    ap.add_argument("--B", type=int, default=B)
    ap.add_argument("--seed", type=int, default=SEED)
    a = ap.parse_args()
    if a.pair:
        cmd_pair(a.pair, a.B, a.seed)
    if a.recovery:
        cmd_recovery(*a.recovery, a.B, a.seed)
    if a.goodput:
        cmd_goodput(a.goodput, a.arms)


if __name__ == "__main__":
    main()
