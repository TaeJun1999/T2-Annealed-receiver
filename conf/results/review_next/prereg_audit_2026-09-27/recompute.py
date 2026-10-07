"""Independent re-derivation of every number quoted in NEXT_EXPERIMENTS_PILOT16e4 §6.1 (+§0/§1a/§3), SEEDS16e4 §5/§6.2,
MISMATCH16e4 §6.1 (+§0/§1a/§3), the matching docs/EXPERIMENTS.md rows, DECISIONS entries, RESULTS §10.5 and figs/F22_pilot_only.txt
(record audit, 2026-09-27; precedent: prereg_audit_2026-09-26/recompute.py, whose functions are reused verbatim).

Reads ONLY raw npz files, checkpoints, fit files, logs and git.  Does NOT call pair_cross.py / pair_mismatch.py / analysis.gain /
recovery_ci.py: the statistics are re-implemented from their written definitions (08_SPEC §2 decision points anchored on the
first arm, exact two-sided sign test via scipy binomtest, POWERED = 3 points and >= 2 with a+b >= 6, 2/3 rule at p < .05;
exp_0925 snr_at log-linear interpolation with a paired bootstrap B = 2000 seed 20260925; recovery_ci paired bootstrap seed
20260926).  analysis.load_raw is imported for the raw reader only (file naming / chunk concatenation / meta).

    CUDA_VISIBLE_DEVICES= ~/miniforge3/envs/torch/bin/python conf/results/review_next/prereg_audit_2026-09-27/recompute.py > .../recompute.out
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
from analysis import load_raw  # noqa: E402  (raw reader only)

BSTAR, V1, GENIE, R2, V0, R0 = "M-ours-bstar", "M-ours-dscore-C-V1", "R5-genie", "R2-ours-G", "M-ours-dscore-C-V0", "R0-pilot"
VP, BP = "V1-pilot", "bstar-pilot"
KEYS_RAW = ("blk_err", "ber", "nmse", "tauL_gmean", "alphaD", "tauL_clip_frac", "alphaD_clip")
GEN4 = ("blk_err", "ber", "tauL_gmean", "alphaD")
B = 2000
_RAW = {}


def P(*a):
    print(*a, flush=True)


def sha16(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


def raw(tag):
    if tag not in _RAW:
        d, meta, warns = load_raw("D2", root=os.path.join(CONF, f"raw_{tag}"))
        for w in warns:
            P(f"  !! load_raw warning {tag}: {w}")
        _RAW[tag] = (d, meta)
    return _RAW[tag][0]


def meta(tag):
    raw(tag)
    return _RAW[tag][1]


def same(x, y):
    x, y = np.asarray(x), np.asarray(y)
    return x.shape == y.shape and np.array_equal(np.nan_to_num(x, nan=1e300), np.nan_to_num(y, nan=1e300))


def failed(v):
    return np.asarray(v.get("failed", np.zeros(len(v["blk_err"])))) > 0


def fails(d, key, arm, it=-1):
    v = np.asarray(d[key][arm]["blk_err"])[:, it]
    return np.where(np.isfinite(v), v, 1.0)


def bler(d, key, arm, it=-1):
    return float(fails(d, key, arm, it).mean())


def nfail(d, key, arm, it=-1):
    return int(fails(d, key, arm, it).sum())


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
    keys = points(d, cell); n = len(fails(d, keys[0], anchor))
    bl = {k[2]: max(bler(d, k, anchor), 0.5 / n) for k in keys}
    return sorted(sorted((s for s in bl if 0.005 <= bl[s] <= 0.9), key=lambda s: abs(np.log10(bl[s] / 0.1)))[:3])


def table_b(d, cell, x, y):
    """anchor = x (first arm).  -> (decision snrs, [(a, b, p)], (A, B, p), powered, wx, wy, label)"""
    cand = decision_points(d, cell, x); res = []
    for s in cand:
        k = [k for k in points(d, cell) if k[2] == s][0]
        fx, fy = fails(d, k, x), fails(d, k, y)
        a = int(((fx > 0) & (fy == 0)).sum()); b = int(((fx == 0) & (fy > 0)).sum()); res.append((a, b, sign_p(a, b)))
    A = sum(r[0] for r in res); Bt = sum(r[1] for r in res)
    powered = len(cand) == 3 and sum(1 for a, b, _ in res if a + b >= 6) >= 2
    wy = sum(1 for a, b, p in res if a > b and p < 0.05); wx = sum(1 for a, b, p in res if b > a and p < 0.05)
    label = "(iv) UNDECIDED" if not powered else "(i) second fewer" if wy >= 2 else "(ii) first fewer" if wx >= 2 else "(iii) no direction"
    return cand, res, (A, Bt, sign_p(A, Bt)), powered, wx, wy, label


def fmt_b(t):
    cand, res, pooled, powered, wx, wy, label = t
    return (f"decision {[f'{s:+.0f}' for s in cand]} a:b " + " · ".join(f"{a}:{b} (p {p:.2g})" for a, b, p in res)
            + f" pooled {pooled[0]}:{pooled[1]} (p {pooled[2]:.2g}) POWERED={powered} wy={wy} wx={wx} -> {label}")


def paired_gap(d, cell, x, y, seed=20260925, digits=2):
    keys = points(d, cell); snrs = [k[2] for k in keys]
    ex = [fails(d, k, x) for k in keys]; ey = [fails(d, k, y) for k in keys]; n = min(len(e) for e in ex)
    (vx, fx), (vy, fy) = snr_at(snrs, [e.mean() for e in ex], n), snr_at(snrs, [e.mean() for e in ey], n)
    if fx != "ok" or fy != "ok":
        return None, f"n/a ({vx:.2f} {fx} vs {vy:.2f} {fy})"
    rng = np.random.default_rng(seed); g = []
    for _ in range(B):
        bx, by = [], []
        for a, b in zip(ex, ey):
            i = rng.integers(len(a), size=len(a)); bx.append(a[i].mean()); by.append(b[i].mean())
        (ux, gx), (uy, gy) = snr_at(snrs, bx, n), snr_at(snrs, by, n); g.append(ux - uy if gx == gy == "ok" else np.nan)
    g = np.array(g); lo, hi = np.nanpercentile(g, [5, 95]); f = f"{{:+.{digits}f}}"
    return vx - vy, f"{f.format(vx - vy)} [{f.format(lo)}, {f.format(hi)}] censored {100 * np.mean(~np.isfinite(g)):.0f}%"


def recovery(d, cell, snrs, seed=20260926):
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
    return f"b*/V1/genie {int(b)}/{int(v)}/{int(g)} R={R:.3f} [90% {lo:.3f}, {hi:.3f}] undefined {int((~ok).sum())}"


def meta_line(tag, cell):
    """meta fields as eval_accept reads them (first raw file of each point, all points collapsed)."""
    seen = {}
    for f in sorted(glob.glob(os.path.join(CONF, f"raw_{tag}", f"D2_{cell}_*.npz"))):
        with np.load(f) as z:
            g = lambda k: (z[k].item() if z[k].shape == () else z[k]) if k in z.files else None
            bs = str(g("meta|bstar")); ll = g(f"meta|ll_val|{bs}")
            key = (str(g("meta|ntrain")), bs, str(g("meta|kron_K")), repr(ll), str(g("meta|stagec_ckpt_id"))[:60], str(g("run|iters")), repr(g("meta|em_sec")))
            seen[key] = seen.get(key, 0) + 1
    return "; ".join(f"{c} files: ntrain={k[0]} bstar={k[1]} K={k[2]} ll_val={k[3]} ckpt='{k[4]}' iters={k[5]} em_sec={k[6]}" for k, c in seen.items())


def n_per_arm(d, cell):
    return sorted({(arm, len(np.asarray(d[k][arm]["blk_err"]))) for k in points(d, cell) for arm in d[k] if "blk_err" in d[k][arm]})


def identity(da, db, cell):
    diff = set()
    for k in points(da, cell):
        for arm in da[k]:
            for q in KEYS_RAW:
                if q in da[k][arm] and arm in db.get(k, {}) and q in db[k][arm] and not same(da[k][arm][q], db[k][arm][q]):
                    diff.add(arm)
    return sorted(diff)


def git(*a):
    return subprocess.run(["git", "-C", CONF] + list(a), capture_output=True, text=True).stdout.strip()


# ----------------------------------------------------------------------------------------------------------------- main
def main():
    P("# recompute.py -- record audit 2026-09-27 (Fable 5.1); raw/ckpt/fits/logs/git only; git HEAD", git("rev-parse", "--short", "HEAD"))

    P("\n## 0. git claims")
    for desc, args in (("92d26757..bfe80c48 (all)", ["92d26757", "bfe80c48"]), ("92e31706..0b994cd2 -- conf/code Demo", ["92e31706", "0b994cd2", "--", "code", "../Demo"]),
                       ("d63b26be..7c6ebcda -- runner.py (numstat)", ["--numstat", "d63b26be", "7c6ebcda", "--", "code/runner.py"]),
                       ("c52bbdaf..92e31706 (all)", ["c52bbdaf", "92e31706"]), ("bfe80c48..92e31706 -- conf/code", ["bfe80c48", "92e31706", "--", "code"]),
                       ("5d9a9a1a..bfe80c48 -- conf/code", ["5d9a9a1a", "bfe80c48", "--", "code"]), ("5d9a9a1a..c52bbdaf -- conf/code", ["5d9a9a1a", "c52bbdaf", "--", "code"]),
                       ("5d9a9a1a..d04fb7c3 -- conf/code", ["5d9a9a1a", "d04fb7c3", "--", "code"]), ("92d26757..92e31706 -- conf/code Demo", ["92d26757", "92e31706", "--", "code", "../Demo"])):
        out = git("diff", "--stat" if "--numstat" not in args else "", *args) if "--numstat" not in args else git("diff", *args)
        P(f"  {desc}:\n    " + (out.replace("\n", "\n    ") or "(empty)"))
    for h in ("2b27ef6a", "92d26757", "bfe80c48", "d63b26be", "7c6ebcda", "c52bbdaf", "92e31706", "f408885f", "0b994cd2", "2e18e44a", "5d9a9a1a", "d04fb7c3", "fb768181"):
        P(f"  {h}: {git('show', '-s', '--format=%ci', h)}  (KST; CDT = KST - 14 h)")

    P("\n## 1. checkpoints sha256[:16] (+ stored fields for the UMi28 seeds)")
    import torch
    for f in ("d2sx_UMi28_N160000_a2_best.pt", "d2sx_UMi28_N160000_a2.pt", "d2sx_UMi28_N160000_a3_best.pt", "d2sx_UMi28_N160000_a3.pt"):
        z = torch.load(os.path.join(CONF, "ckpt", f), map_location="cpu", weights_only=False)
        P(f"  {f}: {sha16(os.path.join(CONF, 'ckpt', f))} epoch={z.get('epoch')} best_epoch={z.get('best_epoch')} best_val={z.get('best_val')!r} "
          f"stopped_by={z.get('stopped_by')} aborted={z.get('aborted')} prior={z.get('prior')} sigma_tag={z.get('sigma_tag')} rung={z.get('rung')} attempt={z.get('attempt')} split_hash={z.get('split_hash')}")
    for f in ("d2sx_N160000_a1.pt", "d2sx_NR16_N160000_a1_fb2_best.pt", "d2sx_S2c_N160000_a1_best.pt", "d2sx_SV8e_N160000_a1_best.pt", "d2sx_UMi28_N160000_a1_best.pt", "d2sx_MIX3_N160000_a1_best.pt"):
        P(f"  {f}: {sha16(os.path.join(CONF, 'ckpt', f))}")
    P("  training logs (UMi28 a2/a3): header time, done line, ckpt mtime - wall:")
    import datetime
    for s in ("2", "3"):
        lines = open(os.path.join(CONF, f"logs/train_d2sx_UMi28_N160000_a{s}.log")).read().splitlines()
        head = [l for l in lines if l.startswith("# =====")][0]; done = [l for l in lines if l.startswith("# done")][-1]
        wall = float(done.split("wall ")[1].split(" s")[0]); mt = os.path.getmtime(os.path.join(CONF, f"ckpt/d2sx_UMi28_N160000_a{s}.pt"))
        P(f"    a{s}: {head[:60]} | {done} | last ckpt mtime {datetime.datetime.fromtimestamp(mt):%H:%M:%S} KST, minus wall = {datetime.datetime.fromtimestamp(mt - wall):%H:%M:%S} KST")

    P("\n## 2. Chat trace / N of the training sample covariance (fit gmm32 npz of each base)")
    for pr, tag in (("S2", "B16e4k"), ("S2c", "D3B16e4"), ("SV8e", "SVB16e4"), ("UMi28", "U28B16e4"), ("MIX3", "MXB16e4")):
        with np.load(os.path.join(CONF, "results", f"gmm_fits_D2_{tag}", f"fit_{pr}_Nr8_fullK32_n160000.npz"), allow_pickle=True) as z:
            C = z["Chat"]; P(f"  {pr}: trace/N = {np.trace(C).real / C.shape[0]:.4f} (N={C.shape[0]}) em sec(gmm32)={float(z['sec']):.1f}")

    # ------------------------------------------------------------------------------------------------ PILOT16e4
    P("\n## 3. PILOT16e4 (6 datasets; pilot raw merged with the base raw)")
    SETS = (("D2C2", "PILB16e4k", "B16e4k", "C2"), ("D2C6", "PILNR16", "NR16B16e4", "C6"), ("D3", "PILD3", "D3B16e4", "C2"),
            ("SV8e", "PILSV", "SVB16e4", "C2"), ("UMi28", "PILU28", "U28B16e4", "C2"), ("MIX3", "PILMX", "MXB16e4", "C2"))
    PAIRS = ((VP, V1, "P1 V1-pilot->V1"), (BP, VP, "P2 bstar-pilot->V1-pilot"), (BP, BSTAR, "rep bstar-pilot->b*"), (VP, BSTAR, "rep V1-pilot->b*"))
    for name, ptag, btag, cell in SETS:
        P(f"\n### {name}: raw_{ptag} x raw_{btag} cell {cell}")
        p, b = raw(ptag), raw(btag)
        P(f"  meta pilot: {meta_line(ptag, cell)}"); P(f"  meta base : {meta_line(btag, cell)}")
        P(f"  n per arm pilot: {sorted({n for _, n in n_per_arm(p, cell)})}  base: {sorted({n for _, n in n_per_arm(b, cell)})}; arms pilot {sorted(a for a in p[points(p, cell)[0]] if a != 'run')}")
        kp, kb = points(p, cell), points(b, cell)
        P(f"  point set pilot {[k[2] for k in kp]} == base {[k[2] for k in kb]}: {[k[2] for k in kp] == [k[2] for k in kb]}")
        bad = []; nraise = {VP: 0, BP: 0}
        for k in kp:
            for q in GEN4:
                if not same(b[k][GENIE][q], p[k][GENIE][q]):
                    bad.append(f"{k[2]:+.0f} genie {q}")
            for new, ref in ((VP, V1), (BP, BSTAR)):
                ok = ~(failed(p[k][new]) | failed(b[k][ref])); nraise[new] += int(failed(p[k][new]).sum())
                for q in ("blk_err", "ber", "nmse"):
                    if not same(np.asarray(p[k][new][q])[ok, 0], np.asarray(b[k][ref][q])[ok, 0]):
                        bad.append(f"{k[2]:+.0f} {new}@1 {q}")
                nm = np.asarray(p[k][new]["nmse"])[~failed(p[k][new])]
                if not same(nm, np.repeat(nm[:, :1], nm.shape[1], axis=1)):
                    bad.append(f"{k[2]:+.0f} {new} nmse varies")
        P(f"  integrity: genie 4 keys identical, @1 equal (blk_err/ber/nmse), nmse fixed over 16 iterations -> {'OK' if not bad else bad}; raised trials {nraise}")
        k3 = [k for k in kp if k[2] == -3.0][0]
        P(f"  §0 -3 dB failures: V1@1 {nfail(b, k3, V1, 0)} V1@16 {nfail(b, k3, V1)} b*@1 {nfail(b, k3, BSTAR, 0)} b*@16 {nfail(b, k3, BSTAR)} "
          f"R0@1 {nfail(b, k3, R0, 0)} R0@16 {nfail(b, k3, R0)} genie@16 {nfail(b, k3, GENIE)} | R2@1 {nfail(b, k3, R2, 0)} (R0@1 == R2@1 blk_err: {same(np.asarray(b[k3][R0]['blk_err'])[:, 0], np.asarray(b[k3][R2]['blk_err'])[:, 0])}); b*@1 - V1@1 = {nfail(b, k3, BSTAR, 0) - nfail(b, k3, V1, 0)}")
        data = {k: {**b[k], VP: p[k][VP], BP: p[k][BP]} for k in kp}
        P(f"  base table B b*->V1: {fmt_b(table_b(data, cell, BSTAR, V1))}; gap {paired_gap(data, cell, BSTAR, V1)[1]}")
        for x, y, nm in PAIRS:
            P(f"  {nm}: {fmt_b(table_b(data, cell, x, y))}; gap {paired_gap(data, cell, x, y)[1]}")
        P("  -3 dB BLER@16: " + "  ".join(f"{a} {bler(data, k3, a):.3f}" for a in (R0, BSTAR, BP, V1, VP, GENIE)))
        P("  -3 dB median NMSE@16 (pilot arms == @1): " + "  ".join(f"{a} {np.nanmedian(np.asarray(data[k3][a]['nmse'])[:, -1]):.2e}" for a in (R0, BSTAR, BP, V1, VP))
          + " | @1: " + "  ".join(f"{a} {np.nanmedian(np.asarray(data[k3][a]['nmse'])[:, 0]):.2e}" for a in (R0, BSTAR, V1)))
        P("  F22 failures per SNR " + " ".join(f"{k[2]:+.0f}" for k in kp) + ":")
        zeros = []
        for a in (R0, BP, VP, BSTAR, V1, GENIE):
            c = [nfail(data, k, a) for k in kp]; zeros += [f"{a} {k[2]:+.0f}" for k, x in zip(kp, c) if x == 0]
            P(f"    {a:<20}" + " ".join(f"{x:5d}" for x in c))
        P(f"    zero-failure points: {'; '.join(zeros) if zeros else 'none'}")
        if name == "D2C2":
            P(f"  §3 pred 6: V1-pilot -3 dB BLER@16 {bler(data, k3, VP):.3f} in (0.145, 0.574): {0.145 < round(bler(data, k3, VP), 3) < 0.574}")

    # ------------------------------------------------------------------------------------------------ SEEDS16e4 UMi28
    P("\n## 4. SEEDS16e4 UMi28 a1 / a2 / a3 (raw_U28B16e4, raw_U28B16e4s2, raw_U28B16e4s3)")
    da = raw("U28B16e4")
    for s, tag in (("a1", "U28B16e4"), ("a2", "U28B16e4s2"), ("a3", "U28B16e4s3")):
        d = raw(tag); P(f"\n### {s} raw_{tag}: meta {meta_line(tag, 'C2')}")
        P(f"  n per arm: {sorted({n for _, n in n_per_arm(d, 'C2')})}; arms {len([a for a in d[points(d, 'C2')[0]] if a != 'run'])}")
        if s != "a1":
            P(f"  arms differing from a1 (all KEYS_RAW, 7 points): {identity(d, da, 'C2')}")
        P(f"  table B b*->V1: {fmt_b(table_b(d, 'C2', BSTAR, V1))}")
        P(f"  gap b*-V1 2dp {paired_gap(d, 'C2', BSTAR, V1)[1]} | 4dp {paired_gap(d, 'C2', BSTAR, V1, digits=4)[1]}")
        keys = points(d, "C2"); k3 = keys[0]
        P(f"  -3 dB: V1 {bler(d, k3, V1):.3f} ({nfail(d, k3, V1)})  V0 {bler(d, k3, V0):.3f} ({nfail(d, k3, V0)})  b* {bler(d, k3, BSTAR):.3f} ({nfail(d, k3, BSTAR)})  genie {bler(d, k3, GENIE):.3f} ({nfail(d, k3, GENIE)})"
          f"  V0->V1 reduction {100 * (1 - nfail(d, k3, V1) / nfail(d, k3, V0)):.1f}%")
        P(f"  V1 failures -3..+15: {' '.join(str(nfail(d, k, V1)) for k in keys)} | b*: {' '.join(str(nfail(d, k, BSTAR)) for k in keys)} | genie: {' '.join(str(nfail(d, k, GENIE)) for k in keys)}")
        cand = decision_points(d, "C2", BSTAR)
        P(f"  R(-3): {recovery(d, 'C2', (-3.0,))} | R(decision {cand}): {recovery(d, 'C2', tuple(float(c) for c in cand))}")
        nm = np.asarray(d[k3][V0]["nmse"]); P(f"  V0 guard fire rate -3 dB: {np.any(~np.isfinite(nm) | (nm > 10.0), axis=1).mean():.3f}")

    P("\n## 4b. SEEDS16e4 D2 a2 / a3 (RESULTS §10.5 rows; raw_B16e4s2, raw_B16e4s3 vs raw_B16e4k)")
    dk = raw("B16e4k")
    for s, tag in (("a2", "B16e4s2"), ("a3", "B16e4s3")):
        d = raw(tag); keys = points(d, "C2"); k3 = keys[0]
        P(f"  {s} raw_{tag}: meta {meta_line(tag, 'C2')}")
        P(f"    arms differing from a1: {identity(d, dk, 'C2')}; table B b*->V1: {fmt_b(table_b(d, 'C2', BSTAR, V1))}")
        P(f"    gap {paired_gap(d, 'C2', BSTAR, V1)[1]}; -3 dB V1 {bler(d, k3, V1):.3f} ({nfail(d, k3, V1)}) V0 {bler(d, k3, V0):.3f} ({nfail(d, k3, V0)}) b* {nfail(d, k3, BSTAR)} genie {nfail(d, k3, GENIE)} "
          f"V0->V1 reduction {100 * (1 - nfail(d, k3, V1) / nfail(d, k3, V0)):.1f}%; R(-3) {recovery(d, 'C2', (-3.0,))}; R(-3,0,3) {recovery(d, 'C2', (-3.0, 0.0, 3.0))}")

    # ------------------------------------------------------------------------------------------------ MISMATCH16e4
    P("\n## 5. MISMATCH16e4 §0: matched base raws (failures per SNR -3..+15; table B b*->V1; gap)")
    BASES = {"S2": "B16e4k", "S2c": "D3B16e4", "SV8e": "SVB16e4", "UMi28": "U28B16e4", "MIX3": "MXB16e4"}
    for pr, tag in BASES.items():
        d = raw(tag); keys = points(d, "C2")
        P(f"  {pr} ({tag}): " + " | ".join(f"{a} " + " ".join(str(nfail(d, k, a)) for k in keys) for a in (R2, BSTAR, V1, GENIE)))
        P(f"    table B b*->V1: {fmt_b(table_b(d, 'C2', BSTAR, V1))}; gap {paired_gap(d, 'C2', BSTAR, V1)[1]}")

    P("\n## 6. MISMATCH16e4 §6.1 (8 pairs; mismatch raw merged with the TEST prior's base raw; fingerprint vs the TRAIN prior's base raw)")
    MM = (("D2-D3", "MMs2s2c", "S2", "S2c"), ("D3-D2", "MMs2cs2", "S2c", "S2"), ("U28-MX", "MMu28mx", "UMi28", "MIX3"), ("MX-U28", "MMmxu28", "MIX3", "UMi28"),
          ("D2-U28", "MMs2u28", "S2", "UMi28"), ("U28-D2", "MMu28s2", "UMi28", "S2"), ("D2-SV", "MMs2sv", "S2", "SV8e"), ("SV-D2", "MMsvs2", "SV8e", "S2"))
    REN = {V1: "V1-mis", BSTAR: "bstar-mis", R2: "R2-mis"}
    MPAIRS = (("bstar-mis", "V1-mis", "MM bstar-mis->V1-mis"), ("V1-mis", V1, "rep V1-mis->V1"), ("bstar-mis", BSTAR, "rep bstar-mis->b*"),
              (BSTAR, "V1-mis", "rep b*->V1-mis"), ("R2-mis", "V1-mis", "rep R2-mis->V1-mis"), ("R2-mis", R2, "rep R2-mis->R2"))
    for name, mtag, ptr, pte in MM:
        P(f"\n### {name} ({ptr} -> {pte}): raw_{mtag} x raw_{BASES[pte]}; train base raw_{BASES[ptr]}")
        m, b = raw(mtag), raw(BASES[pte]); mm, tm = meta(mtag)[("C2", pte)], meta(BASES[ptr])[("C2", ptr)]
        P(f"  meta mis: {meta_line(mtag, 'C2')}")
        fk = ["em_sec"] + sorted(k for k in tm if k.startswith("ll_val|"))
        P(f"  fingerprint vs train base ({len(fk)} keys em_sec + ll_val|*): " + ("EQUAL" if all(str(mm.get(k)) == str(tm.get(k)) for k in fk) else "DIFF " + str([(k, mm.get(k), tm.get(k)) for k in fk if str(mm.get(k)) != str(tm.get(k))]))
          + f"; em_sec {mm.get('em_sec')!r}; ckpt id mis '{str(mm.get('stagec_ckpt_id'))[:50]}'")
        km, kb = points(m, "C2"), points(b, "C2"); bad = []; nraise = {}
        P(f"  point set {[k[2] for k in km] == [k[2] for k in kb]} n per arm {sorted({n for _, n in n_per_arm(m, 'C2')})} arms {sorted(a for a in m[km[0]] if a != 'run')}")
        for k in km:
            for q in GEN4:
                if not same(b[k][GENIE][q], m[k][GENIE][q]):
                    bad.append(f"{k[2]:+.0f} genie {q}")
            for arm in (BSTAR, R2):
                ok = ~(failed(b[k][arm]) | failed(m[k][arm]))
                if same(np.asarray(b[k][arm]["nmse"])[ok], np.asarray(m[k][arm]["nmse"])[ok]):
                    bad.append(f"{k[2]:+.0f} {arm} nmse identical (mismatch not applied)")
            for arm in REN:
                nraise[REN[arm]] = nraise.get(REN[arm], 0) + int(failed(m[k][arm]).sum())
        P(f"  integrity: genie identical, mismatch applied (b*/R2 nmse differ) -> {'OK' if not bad else bad}; raised {nraise}")
        data = {k: {**b[k], **{REN[a]: m[k][a] for a in REN}} for k in km}
        gaps = {}
        for x, y, nm in MPAIRS:
            est, txt = paired_gap(data, "C2", x, y); gaps[nm] = est
            P(f"  {nm}: {fmt_b(table_b(data, 'C2', x, y))}; gap {txt}")
        g0 = paired_gap(data, "C2", BSTAR, V1)[0]; g1 = gaps["MM bstar-mis->V1-mis"]
        P(f"  retention = {g1:+.2f} / {g0:+.2f} = {g1 / g0:.2f}" if g1 is not None and g0 else "  retention n/a")
        k3 = km[0]
        P(f"  -3 dB failures: mis R2/b*/V1 {nfail(data, k3, 'R2-mis')} · {nfail(data, k3, 'bstar-mis')} · {nfail(data, k3, 'V1-mis')} | matched R2/b*/V1/genie {nfail(data, k3, R2)} · {nfail(data, k3, BSTAR)} · {nfail(data, k3, V1)} · {nfail(data, k3, GENIE)}")
        P("  failures per SNR: " + " | ".join(f"{a} " + " ".join(str(nfail(data, k, a)) for k in km) for a in ("R2-mis", "bstar-mis", "V1-mis")))

    # ------------------------------------------------------------------------------------------------ logs / manifests
    P("\n## 7. driver logs, manifests, tables headers")
    for f in ("run_pilot16e4.log", "run_mismatch16e4.log", "run_seeds16e4_U28B16e4s2.log", "run_seeds16e4_U28B16e4s3.log"):
        P(f"  --- logs/{f}")
        for l in open(os.path.join(CONF, "logs", f)).read().splitlines():
            if l.startswith("[") and ("start" in l or "DONE" in l or "pair_" in l or "ref-arms" in l or "acceptance" in l):
                P("    " + l[:150])
    import json
    for t in ("PILB16e4k", "PILNR16", "PILD3", "PILSV", "PILU28", "PILMX", "MMs2s2c", "MMs2cs2", "MMu28mx", "MMmxu28", "MMs2u28", "MMu28s2", "MMs2sv", "MMsvs2", "U28B16e4s2", "U28B16e4s3"):
        j = json.load(open(os.path.join(CONF, "results/review_next", f"run_manifest_{t}.json")))
        P(f"  manifest {t}: git {j['git_commit']} config_hash {j['config_hash']} n_raw {j['n_raw_files']} ckpt {str(j.get('stagec_ckpt_id'))[:60]}")
    for t in ("U28B16e4s2", "U28B16e4s3"):
        P(f"  tables_D2_{t}.txt: " + " | ".join(l for l in open(os.path.join(CONF, "results", f"tables_D2_{t}.txt")).read().splitlines()[:2]))
    for pat in ("pair_PIL*.txt", "pair_MM*.txt"):
        for f in sorted(glob.glob(os.path.join(CONF, "results/review_next", pat))):
            h = open(f).readline(); P(f"  {os.path.basename(f)}: git {h.split('git ')[1].split(';')[0]}; {h.split('integrity')[1].strip()[:40]}")
    P("  fits link dirs mtime (KST): " + " ".join(f"{os.path.basename(d)} {datetime.datetime.fromtimestamp(os.lstat(d).st_mtime):%H:%M:%S}" for d in sorted(glob.glob(os.path.join(CONF, "results/gmm_fits_D2_MM*")) + glob.glob(os.path.join(CONF, "results/gmm_fits_D2_PIL*")) + glob.glob(os.path.join(CONF, "results/gmm_fits_D2_U28B16e4s*")))))
    P("  raw_PILchk exists:", os.path.isdir(os.path.join(CONF, "raw_PILchk")), "| PILchk accept file:", glob.glob(os.path.join(CONF, "results/review_next/PILchk*")))


if __name__ == "__main__":
    main()
