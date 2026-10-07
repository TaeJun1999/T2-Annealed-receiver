"""Independent re-derivation of every number quoted in the §6 sections of NEXT_EXPERIMENTS_{PARETO,D3B16e4,SVB16e4,38901}.md,
the matching docs/EXPERIMENTS.md rows and DECISIONS entries (record audit, 2026-09-26; precedent: k1k2c6_review_raw/recompute.py).

Reads ONLY raw npz files, checkpoints, fit files, GB' csv and git.  Re-implements the statistics from their written definitions
(08_SPEC §2 decision points / sign test / power guard, exp_0925 snr_at interpolation, paired and unpaired bootstraps with the
registered seeds and resampling order) instead of calling analysis.py / recovery_ci.py / frontier_ci.py, so an agreement is a
reproduction and a disagreement is a finding.  Prints everything; the comparison against the documents is done by the reviewers.

    CUDA_VISIBLE_DEVICES= ~/miniforge3/envs/torch/bin/python results/review_next/prereg_audit_2026-09-26/recompute.py > .../recompute.out
"""
import glob
import hashlib
import os
import subprocess
import sys

import numpy as np
from scipy.stats import binomtest

CONF = "/home/HTJ/t2/conf"
sys.path.insert(0, os.path.join(CONF, "code"))
from analysis import load_raw          # the raw reader only (file naming / chunk concatenation), no statistics  # noqa: E402

BSTAR, V1, GENIE, SCALAR, R2, V0 = "M-ours-bstar", "M-ours-dscore-C-V1", "R5-genie", "M-ours-bstar-scalar", "R2-ours-G", "M-ours-dscore-C-V0"
ARMS_REPORT = (R2, "M-ours-gmm32", BSTAR, V0, V1, "M-ours-dscore-C-V4", "M-ours-dscore-C-V4b", SCALAR, GENIE)
NONSTAGEC = (BSTAR, SCALAR, "M-ours-gmm32", "R0-pilot", "R1-turbo", R2, "R3-bigamp", "R4-scvamp", "R4-llr", GENIE)
KEYS_RAW = ("blk_err", "ber", "nmse", "tauL_gmean", "alphaD", "tauL_clip_frac", "alphaD_clip")
B = 2000


def P(*a):
    print(*a, flush=True)


def sha16(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


def raw(tag):
    d, _, warns = load_raw("D2", root=os.path.join(CONF, f"raw_{tag}"))
    for w in warns:
        P(f"  !! load_raw warning {tag}: {w}")
    return d


def fails(d, key, arm):
    v = np.asarray(d[key][arm]["blk_err"])[:, -1]
    return np.where(np.isfinite(v), v, 1.0)


def bler16(d, key, arm):
    return float(fails(d, key, arm).mean())


def sign_p(a, b):
    n = a + b
    return 1.0 if n == 0 else float(binomtest(min(a, b), n, 0.5, alternative="two-sided").pvalue)


def snr_at(snrs, bl, n, target=0.1):
    lb = np.log10(np.maximum(np.asarray(bl, float), 0.5 / n)); lt = np.log10(target)
    if lb[0] <= lt:
        return snrs[0], "lo"
    for i in range(len(snrs) - 1):
        if lb[i] > lt >= lb[i + 1]:
            return snrs[i] + (lb[i] - lt) / (lb[i] - lb[i + 1]) * (snrs[i + 1] - snrs[i]), "ok"
    return snrs[-1], "hi"


def points(d, cell):
    return sorted((k for k in d if k[0] == cell), key=lambda k: k[2])


def decision_points(d, cell, anchor):
    keys = points(d, cell)
    n = len(fails(d, keys[0], anchor))
    bl = {k[2]: max(bler16(d, k, anchor), 0.5 / n) for k in keys}
    cand = sorted((s for s in bl if 0.005 <= bl[s] <= 0.9), key=lambda s: abs(np.log10(bl[s] / 0.1)))[:3]
    return sorted(cand)


def table_b(d, cell, x, y, anchor):
    """Returns (decision snrs, [(a, b, p)], pooled (A, B, p), powered, wx, wy, label)."""
    cand = decision_points(d, cell, anchor)
    res = []
    for s in cand:
        k = [k for k in points(d, cell) if k[2] == s][0]
        fx, fy = fails(d, k, x), fails(d, k, y)
        a = int(((fx > 0) & (fy == 0)).sum()); b = int(((fx == 0) & (fy > 0)).sum())
        res.append((a, b, sign_p(a, b)))
    A = sum(r[0] for r in res); Bt = sum(r[1] for r in res)
    powered = len(cand) == 3 and sum(1 for a, b, _ in res if a + b >= 6) >= 2
    wy = sum(1 for a, b, p in res if a > b and p < 0.05)
    wx = sum(1 for a, b, p in res if b > a and p < 0.05)
    label = ("(iv) UNDECIDED" if not powered else "(i) second fewer" if wy >= 2 else "(ii) first fewer" if wx >= 2 else "(iii) no direction")
    return cand, res, (A, Bt, sign_p(A, Bt)), powered, wx, wy, label


def paired_gap(d, cell, x, y, seed=20260925):
    """exp_0925_analysis.gain: SNR@0.1(x) - SNR@0.1(y), paired bootstrap, same resampled indices for both arms at every SNR."""
    keys = points(d, cell); snrs = [k[2] for k in keys]
    ex = [fails(d, k, x) for k in keys]; ey = [fails(d, k, y) for k in keys]; n = min(len(e) for e in ex)
    (vx, fx), (vy, fy) = snr_at(snrs, [e.mean() for e in ex], n), snr_at(snrs, [e.mean() for e in ey], n)
    if fx != "ok" or fy != "ok":
        return f"n/a ({vx:.2f} {fx} vs {vy:.2f} {fy})"
    rng = np.random.default_rng(seed); g = []
    for _ in range(B):
        bx, by = [], []
        for a, b in zip(ex, ey):
            i = rng.integers(len(a), size=len(a)); bx.append(a[i].mean()); by.append(b[i].mean())
        (ux, gx), (uy, gy) = snr_at(snrs, bx, n), snr_at(snrs, by, n); g.append(ux - uy if gx == gy == "ok" else np.nan)
    g = np.array(g); lo, hi = np.nanpercentile(g, [5, 95])
    return f"{vx - vy:+.2f} dB [90% {lo:+.2f}, {hi:+.2f}] censored {100 * np.mean(~np.isfinite(g)):.0f}%"


def recovery(d, cell, snrs, seed=20260926):
    """recovery_ci.py: R = (b* - V1)/(b* - genie) on pooled failure counts, paired bootstrap of trial indices."""
    keys = [k for k in points(d, cell) if any(abs(k[2] - s) < 1e-9 for s in snrs)]
    cols = [(fails(d, k, BSTAR), fails(d, k, V1), fails(d, k, GENIE)) for k in keys]
    b = sum(c[0].sum() for c in cols); v = sum(c[1].sum() for c in cols); g = sum(c[2].sum() for c in cols)
    R = (b - v) / (b - g) if b - g > 0 else np.nan
    rng = np.random.default_rng(seed); n = len(cols[0][0]); out = np.empty(B)
    for i in range(B):
        idx = rng.integers(0, n, n)
        bs = sum(c[0][idx].sum() for c in cols); vs = sum(c[1][idx].sum() for c in cols); gs = sum(c[2][idx].sum() for c in cols)
        out[i] = (bs - vs) / (bs - gs) if bs - gs > 0 else np.nan
    ok = np.isfinite(out); lo, hi = np.percentile(out[ok], [5, 95])
    return R, (int(b), int(v), int(g)), (lo, hi), int((~ok).sum())


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


def recovery_diff(d1, s1, snr1, d2, s2, snr2, seed=20260926):
    """frontier_ci.py --recovery: the two raw sets resampled independently; within a set the three arms share indices."""
    sets = []
    for d, spec, snrs in ((d1, s1, snr1), (d2, s2, snr2)):
        keys = [k for k in points(d, "C2") if any(abs(k[2] - s) < 1e-9 for s in snrs)]
        sets.append((spec, keys, [tuple(fails(d, k, a) for a in (BSTAR, V1, GENIE)) for k in keys]))
    rs = Resampler(seed); bo = np.full((B, 2), np.nan)
    for i in range(B):
        rs.new()
        for j, (spec, keys, cols) in enumerate(sets):
            rc = [tuple(rs.take(spec, k, x) for x in c) for k, c in zip(keys, cols)]
            b = sum(c[0].sum() for c in rc); v = sum(c[1].sum() for c in rc); g = sum(c[2].sum() for c in rc)
            bo[i, j] = (b - v) / (b - g) if b - g > 0 else np.nan
    dd = bo[:, 0] - bo[:, 1]; lo, hi = np.percentile(dd[np.isfinite(dd)], [5, 95])
    R = []
    for spec, keys, cols in sets:
        b = sum(c[0].sum() for c in cols); v = sum(c[1].sum() for c in cols); g = sum(c[2].sum() for c in cols); R.append((b - v) / (b - g))
    return R[0] - R[1], (lo, hi), int((~np.isfinite(dd)).sum())


def frontier_pair(specA, specB, seed=20260926):
    """frontier_ci.py --pair: (name, raw-dict, cell, arm); unpaired across specs, paired within a (spec, point)."""
    rs = Resampler(seed); est = []; cols = []
    for name, d, cell, arm in (specA, specB):
        keys = points(d, cell); snrs = [k[2] for k in keys]; c = [fails(d, k, arm) for k in keys]; n = min(len(x) for x in c)
        est.append(snr_at(snrs, [x.mean() for x in c], n)); cols.append((name, keys, snrs, c, n))
    bo = np.full((B, 2), np.nan)
    for i in range(B):
        rs.new()
        for j, (name, keys, snrs, c, n) in enumerate(cols):
            m = [rs.take(name, k, x).mean() for k, x in zip(keys, c)]
            v, f = snr_at(snrs, m, n); bo[i, j] = v if f == "ok" else np.nan
    out = []
    for j in range(2):
        lo, hi = np.percentile(bo[np.isfinite(bo[:, j]), j], [5, 95])
        out.append(f"{cols[j][0]} SNR@0.1 {est[j][0]:.2f} ({est[j][1]}) [90% {lo:.2f}, {hi:.2f}]")
    dd = bo[:, 0] - bo[:, 1]; df = dd[np.isfinite(dd)]
    l90, h90 = np.percentile(df, [5, 95]); l95, h95 = np.percentile(df, [2.5, 97.5])
    pb = 2 * min(np.mean(df <= 0), np.mean(df >= 0))
    out.append(f"Delta {est[0][0] - est[1][0]:+.2f} dB [90% {l90:+.2f}, {h90:+.2f}] [95% {l95:+.2f}, {h95:+.2f}] p={pb:.4f} censored {100 * np.mean(~np.isfinite(dd)):.1f}%")
    return out


def meta_check(tag, d, cell):
    """First and last chunk of every point: meta fields as eval_accept reads them; chunk completeness = n per arm."""
    P(f"  [{tag}] meta per point (n, bstar, kron_K, ll_val|bstar, ntrain, ckpt id, iters, em_sec):")
    files = sorted(glob.glob(os.path.join(CONF, f"raw_{tag}", f"D2_{cell}_*.npz")))
    seen = {}
    for f in files:
        with np.load(f) as z:
            g = lambda k: (z[k].item() if z[k].shape == () else z[k]) if k in z.files else None
            bs = str(g("meta|bstar")); ll = g(f"meta|ll_val|{bs}")
            key = (str(g("meta|ntrain")), bs, str(g("meta|kron_K")), repr(ll), str(g("meta|stagec_ckpt_id"))[:70], str(g("run|iters")), str(g("meta|em_sec")))
            seen[key] = seen.get(key, 0) + 1
    for k, c in seen.items():
        P(f"    {c} files: ntrain={k[0]} bstar={k[1]} kron_K={k[2]} ll_val={k[3]} ckpt='{k[4]}' iters={k[5]} em_sec={k[6]}")
    for k in points(d, cell):
        ns = {len(np.asarray(d[k][a]["blk_err"])) for a in d[k] if "blk_err" in d[k][a]}
        if ns != {2560} and ns != {40}:
            P(f"    !! {k}: n per arm {ns}")


def identity(tag_a, tag_b, cell):
    """Every arm x KEYS_RAW bit-identical between two tags (expect only V0/V1/V4/V4b to differ)."""
    da, db = raw(tag_a), raw(tag_b); diff = set()
    for k in points(da, cell):
        for arm in da[k]:
            for q in KEYS_RAW:
                if q in da[k][arm] and q in db[k][arm]:
                    x, y = np.asarray(da[k][arm][q]), np.asarray(db[k][arm][q])
                    if x.shape != y.shape or not np.array_equal(np.nan_to_num(x, nan=1e300), np.nan_to_num(y, nan=1e300)):
                        diff.add(arm)
    return sorted(diff)


def v0_guard(d, cell):
    out = []
    for k in points(d, cell):
        nm = np.asarray(d[k][V0]["nmse"])
        fired = np.any(~np.isfinite(nm) | (nm > 10.0), axis=1) if nm.ndim == 2 else (~np.isfinite(nm) | (nm > 10.0))
        out.append(f"{k[2]:+.0f}:{fired.mean():.3f}")
    return " ".join(out)


def bler_table(d, cell, snrs, arms=ARMS_REPORT):
    for arm in arms:
        vals = []
        for s in snrs:
            kk = [k for k in points(d, cell) if abs(k[2] - s) < 1e-9]
            vals.append(f"{bler16(d, kk[0], arm):.3f}" if kk else "  -  ")
        P(f"    {arm:<20} " + " / ".join(vals))


def snr01_table(d, cell):
    keys = points(d, cell); snrs = [k[2] for k in keys]; n = 2560
    for arm in ARMS_REPORT:
        v, f = snr_at(snrs, [bler16(d, k, arm) for k in keys], n)
        P(f"    {arm:<20} SNR@0.1 {v:6.2f} ({f})")


def best_vs_last(db, dl, cell, snrs):
    A = Bt = 0; parts = []
    for s in snrs:
        k = [k for k in points(db, cell) if abs(k[2] - s) < 1e-9][0]
        x, y = fails(db, k, V1), fails(dl, k, V1)
        a = int(((x > 0) & (y == 0)).sum()); b = int(((x == 0) & (y > 0)).sum()); A += a; Bt += b; parts.append(f"{s:+.0f} {a}:{b}")
    return " · ".join(parts) + f" pooled {A}:{Bt} p={sign_p(A, Bt):.3g}"


def fit_ll(tag, prior, fam, K):
    f = os.path.join(CONF, "results", f"gmm_fits_D2_{tag}", f"fit_{prior}_Nr8_{fam}K{K}_n160000.npz")
    with np.load(f, allow_pickle=True) as z:
        return repr(float(z["ll_val"])), int(z["n_iter"]), int(z["it_best"]), (int(z["n_reseed"]) if "n_reseed" in z.files else None), (int(z["restart"]) if "restart" in z.files else None)


def git(*a):
    return subprocess.run(["git", "-C", CONF] + list(a), capture_output=True, text=True).stdout.strip()


def main():
    P("# recompute.py -- record audit 2026-09-26 (Fable 5.1); raw/ckpt/fits/csv/git only")
    P("# git HEAD", git("rev-parse", "--short", "HEAD"))
    P("\n## 0. code identity: conf/code diff vs the freeze eee1d669 (empty = identical)")
    for h in ("2b03df55", "07a8935a", "80bae849", "344d084c", "baa3c370", "4219fdfc"):
        P(f"  {h}: '{git('diff', '--stat', 'eee1d669', h, '--', 'code')}'")

    P("\n## 1. checkpoints sha256[:16]")
    for f in ("d2sx_N160000_a1.pt", "d2sx_S2c_N160000_a1_best.pt", "d2sx_S2c_N160000_a1.pt", "d2sx_SV8e_N160000_a1_best.pt", "d2sx_SV8e_N160000_a1.pt",
              "d2sx_UMi28_N160000_a1_best.pt", "d2sx_UMi28_N160000_a1.pt", "d2sx_MIX3_N160000_a1_best.pt", "d2sx_MIX3_N160000_a1.pt"):
        P(f"  {f}: {sha16(os.path.join(CONF, 'ckpt', f))}")

    P("\n## 2. b* fit files (ll_val repr, n_iter, it_best, n_reseed, restart)")
    for tag, prior, fam, K in (("B16e4k", "S2", "kron", 1024), ("D3B16e4", "S2c", "kron", 4096), ("SVB16e4", "SV8e", "full", 256),
                               ("U28B16e4", "UMi28", "kron", 4096), ("MXB16e4", "MIX3", "kron", 4096)):
        P(f"  {tag} {fam} K={K}: {fit_ll(tag, prior, fam, K)}")
    em = sum(float(np.load(f)["sec"]) for f in glob.glob(os.path.join(CONF, "results/gmm_fits_D2_B16e4k/fit_S2_Nr8_*_n160000.npz")))
    P(f"  B16e4k Nr8 em_sec sum over {len(glob.glob(os.path.join(CONF, 'results/gmm_fits_D2_B16e4k/fit_S2_Nr8_*_n160000.npz')))} files: {em!r}")

    P("\n## 3. GB' csv rows")
    for p in ("S2c", "SV8e", "UMi28", "MIX3"):
        P(f"  {p}: " + open(os.path.join(CONF, "results", f"d2_gbprime_{p}.csv")).read().strip().splitlines()[-1])
    z = np.load(os.path.join(CONF, "results/d2_gbprime_UMi28_N160000_a1.npz")); r = z["nmse_model"] / z["nmse_gmm"]
    P(f"  UMi28 per-sigma ratio max at sigma={float(z['sigma'][r.argmax()]):.4f}: {r.max():.4f}; n>1 = {int((r > 1).sum())}; neighbours {r[r.argmax() - 1]:.4f} / {r[r.argmax() + 1]:.4f}")

    # ---------------------------------------------------------------- Pareto
    P("\n## 4. PARETO (PARB16e4 + B16e4k)")
    dp = raw("PARB16e4"); dk = raw("B16e4k"); dchk = raw("PARB16e4chk")
    meta_check("PARB16e4", dp, "C7"); meta_check("PARB16e4chk", dchk, "C2")
    P("  points in PARB16e4:", sorted((k[0], k[2]) for k in dp))
    for cell in ("C7", "C8"):
        for x, y, anc, nm in ((BSTAR, V1, BSTAR, "b*->V1"), (BSTAR, SCALAR, BSTAR, "b*->scalar")):
            cand, res, pooled, powered, wx, wy, label = table_b(dp, cell, x, y, anc)
            P(f"  {cell} {nm}: decision {cand} a:b {[(a, b, f'{p:.2g}') for a, b, p in res]} pooled {pooled[0]}:{pooled[1]} p={pooled[2]:.2g} POWERED={powered} wx={wx} wy={wy} -> {label}")
        P(f"  {cell} paired gap b*-V1: {paired_gap(dp, cell, BSTAR, V1)};  b*-scalar: {paired_gap(dp, cell, BSTAR, SCALAR)}")
        for snrs in ((-3.0,), tuple(float(s) for s in decision_points(dp, cell, BSTAR))):
            R, cnt, ci, und = recovery(dp, cell, snrs)
            P(f"  {cell} recovery {snrs}: b*/V1/genie {cnt} R={R:.3f} [90% {ci[0]:.3f}, {ci[1]:.3f}] undefined {und}")
        P(f"  {cell} SNR@0.1:"); snr01_table(dp, cell)
        P(f"  {cell} BLER@16 (-9/-6/-3/0/+15):"); bler_table(dp, cell, (-9, -6, -3, 0, 15))
        P(f"  {cell} V0 guard fire rate: {v0_guard(dp, cell)}")
    # C2 curve = B16e4k (7) + PARB16e4 C2 -6
    dc2 = {k: v for k, v in dk.items() if k[0] == "C2"}; dc2.update({k: v for k, v in dp.items() if k[0] == "C2"})
    P("  C2 merged points:", sorted(k[2] for k in dc2))
    P("  C2 -6 dB BLER@16:"); bler_table(dp, "C2", (-6,))
    P("  C2 (8 pts) SNR@0.1:"); snr01_table(dc2, "C2")
    for nm, arm, cell in (("bstar_C7", BSTAR, "C7"), ("bstar_C8", BSTAR, "C8"), ("V1_C7", V1, "C7"), ("V1_C8", V1, "C8"), ("genie_C7", GENIE, "C7"), ("genie_C8", GENIE, "C8")):
        A = ("V1_C2" if arm == V1 or arm == BSTAR and False else nm.split("_")[0] + "_C2", dc2, "C2", V1 if nm.startswith("V1") or nm.startswith("bstar") and False else arm)
        # registered pairs: V1_C2 vs bstar_C7 / bstar_C8 (P-a, P-b); report pairs: same-arm across cells
        if nm.startswith("bstar"):
            for aname, aarm in (("V1_C2", V1), ("bstar_C2", BSTAR)):
                out = frontier_pair((aname, dc2, "C2", aarm), (nm, dp, cell, arm)); P(f"  pair {aname} vs {nm}: " + " | ".join(out))
        else:
            out = frontier_pair((nm.split("_")[0] + "_C2", dc2, "C2", arm), (nm, dp, cell, arm)); P(f"  pair {nm.split('_')[0]}_C2 vs {nm}: " + " | ".join(out))
    # regression check: all arms bit-identical between PARB16e4chk (trials 0..39) and B16e4k C2 -3 chunk 0
    k = [k for k in dchk if k[2] == -3.0][0]; kk = [k for k in dk if k[0] == "C2" and k[2] == -3.0][0]; bad = []
    for arm in dchk[k]:
        for q in KEYS_RAW:
            if q in dchk[k][arm] and q in dk[kk].get(arm, {}):
                x = np.asarray(dchk[k][arm][q]); y = np.asarray(dk[kk][arm][q])[:len(x)]
                if not np.array_equal(np.nan_to_num(x, nan=1e300), np.nan_to_num(y, nan=1e300)):
                    bad.append((arm, q))
    P(f"  regression check PARB16e4chk vs raw_B16e4k C2 -3 trials 0..{len(x) - 1}: arms in chk {len(dchk[k])}, differing {bad}")
    # C2 -6 genie vs raw_B1e4lo
    dlo = raw("B1e4lo"); k6 = [k for k in dp if k[0] == "C2"][0]; kl = [k for k in dlo if k[0] == "C2" and k[2] == -6.0][0]
    P("  C2 -6 genie blk_err/ber/tauL_gmean/alphaD identical to B1e4lo:", all(np.array_equal(np.nan_to_num(np.asarray(dp[k6][GENIE][q]), nan=1e300), np.nan_to_num(np.asarray(dlo[kl][GENIE][q]), nan=1e300)) for q in ("blk_err", "ber", "tauL_gmean", "alphaD")))

    # ---------------------------------------------------------------- prior variants
    for tag, prior, bfam, dec in (("D3B16e4", "S2c", "kron", None), ("SVB16e4", "SV8e", "gmm256", None), ("U28B16e4", "UMi28", "kron", None), ("MXB16e4", "MIX3", "kron", None)):
        P(f"\n## 5. {tag} ({prior})")
        db, dl = raw(tag), raw(tag + "last")
        meta_check(tag, db, "C2"); meta_check(tag + "last", dl, "C2")
        for nm, d in (("best", db), ("last", dl)):
            for x, y, anc, pn in ((BSTAR, V1, BSTAR, "b*->V1"), (BSTAR, SCALAR, BSTAR, "b*->scalar"), (R2, BSTAR, R2, "R2->b*")):
                cand, res, pooled, powered, wx, wy, label = table_b(d, "C2", x, y, anc)
                P(f"  {nm} {pn}: decision {cand} a:b {[(a, b, f'{p:.2g}') for a, b, p in res]} pooled {pooled[0]}:{pooled[1]} p={pooled[2]:.2g} POWERED={powered} wx={wx} wy={wy} -> {label}")
            P(f"  {nm} paired gap b*-V1: {paired_gap(d, 'C2', BSTAR, V1)};  b*-scalar: {paired_gap(d, 'C2', BSTAR, SCALAR)};  R2-b*: {paired_gap(d, 'C2', R2, BSTAR)}")
            cand = tuple(float(s) for s in decision_points(d, "C2", BSTAR))
            for snrs in ((-3.0,), cand):
                R, cnt, ci, und = recovery(d, "C2", snrs)
                P(f"  {nm} recovery {snrs}: b*/V1/genie {cnt} R={R:.3f} [90% {ci[0]:.3f}, {ci[1]:.3f}] undefined {und}")
            dR, ci, und = recovery_diff(d, f"raw_{tag}{'' if nm == 'best' else 'last'}", (-3.0,), dk, "raw_B16e4k", (-3.0,))
            P(f"  {nm} dR(-3 dB) vs D2: {dR:+.3f} [90% {ci[0]:+.3f}, {ci[1]:+.3f}] undefined {und}")
            if nm == "best":
                dR, ci, und = recovery_diff(d, f"raw_{tag}", cand, dk, "raw_B16e4k", (-3.0, 0.0, 3.0))
                P(f"  best dR(decision {cand}) vs D2(-3,0,3): {dR:+.3f} [90% {ci[0]:+.3f}, {ci[1]:+.3f}] undefined {und}")
                k3 = [k for k in points(d, 'C2') if k[2] == -3.0][0]
                P(f"  best anchor b* BLER@16 -3 dB = {bler16(d, k3, BSTAR):.3f} (saturation guard band [0.005, 0.9])")
        P("  best SNR@0.1:"); snr01_table(db, "C2")
        P("  last V1 SNR@0.1:"); snr01_table(dl, "C2") if False else None
        keys = points(dl, "C2"); v, f = snr_at([k[2] for k in keys], [bler16(dl, k, V1) for k in keys], 2560); P(f"    last V1 SNR@0.1 {v:.2f} ({f})")
        P("  best BLER@16 (-3/0/+3/+6):"); bler_table(db, "C2", (-3, 0, 3, 6))
        P(f"  best V0 guard fire rate: {v0_guard(db, 'C2')}")
        cand = decision_points(db, "C2", BSTAR)
        P(f"  best-vs-last V1 at decision {cand}: {best_vs_last(db, dl, 'C2', cand)};  at -3: {best_vs_last(db, dl, 'C2', [-3.0])}")
        P(f"  arms differing between {tag} and {tag}last: {identity(tag, tag + 'last', 'C2')}")


if __name__ == "__main__":
    main()
