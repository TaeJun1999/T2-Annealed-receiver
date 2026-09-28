"""conf/code/pair_rotmix.py -- drift-TRAINED priors vs static priors on the SAME rotated trials (NEXT_EXPERIMENTS_ROTMIX16e4 §1
판정 2·DD, 수용 (c)-(f)).  One rotation angle per call.

Raws: --ref = the static raw of these trials (0 deg raw_B16e4k, 15 deg raw_ROTaB16e4k, 30 deg raw_ROTbB16e4k; V1 = headline
legacy-last, b* = kron 1024); --rmx = RMX<d> (14 arms, S2d `_best`, b* kron 4096); --last = RMX<d>last (V1 S2d last-EMA);
--k1 = RMX<d>k1 (b* S2d kron 1024).  Labels (registration §2): DT-V1 = V1(static last) -> V1(S2d last); DT-b* = b*(static
kron 1024) -> b*(S2d kron 1024); DD = R_b*(S2d: b* 4096, V1 last, genie) - R_b*(static), -3 dB, the six arms resampled
together (B = 2000, default_rng(20260926)), 90% CI.  Integrity (any failure -> exit 1 BEFORE any label): point sets,
load_raw warnings, one clean commit across rmx/last/k1, meta|rotation == d, R5-genie 4 keys == the ref raw, fit fingerprint
(meta ll_val|gmm16..512, ll_val|kron, em_sec == the S2d fit files; k1: kron 1024 over 13 files), checkpoint ids, and at
d = 0: R3-bigamp (prior-free) identical to the ref raw in every stored field, b* / R2 nmse NOT identical (the S2d fits were
applied).
    python code/pair_rotmix.py --deg 15 --ref raw_ROTaB16e4k --rmx raw_RMX15 --last raw_RMX15last --k1 raw_RMX15k1
"""
import argparse
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import numpy as np
from analysis import load_raw, decision_points, paired, gain, sign_p, MIN_DISC
from pair_cross import same, failed
from pair_baselines import chunk_meta, fails, table_b, KEYS4

V1, BSTAR, GENIE = "M-ours-dscore-C-V1", "M-ours-bstar", "R5-genie"
FITS = "results/gmm_fits_D2_S2dB16e4"
B_BOOT, SEED = 2000, 20260926


def fit_ll(fam, K):
    with np.load(os.path.join(C.CONF, FITS, f"fit_S2d_Nr8_{fam}K{K}_n160000.npz")) as z:
        return float(z["ll_val"]), float(z["sec"])


def dd_boot(s2d, sta, guard_ok):
    """s2d / sta = lists (one per SNR) of (F_b*, F_V1, F_genie) over the SAME trials; one trial-index resample per replicate
    is applied to every SNR column and both sides (recovery_ci convention) -> (dR, lo, hi, n_undefined)."""
    def R(cols, idx=None):
        b, v, g = (sum((c[i] if idx is None else c[i][idx]).sum() for c in cols) for i in range(3))
        return (b - v) / (b - g) if b - g > 0 else np.nan
    d0 = R(s2d) - R(sta)
    if not guard_ok:
        return d0, np.nan, np.nan, 0
    rng = np.random.default_rng(SEED)
    n = len(s2d[0][0]); out = np.empty(B_BOOT)
    for i in range(B_BOOT):
        idx = rng.integers(0, n, n)
        out[i] = R(s2d, idx) - R(sta, idx)
    ok = np.isfinite(out)
    lo, hi = np.percentile(out[ok], [5, 95]) if ok.sum() else (np.nan, np.nan)
    return d0, lo, hi, int((~ok).sum())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--deg", type=float, required=True)
    for k in ("--ref", "--rmx", "--last", "--k1"):
        ap.add_argument(k, required=True)
    ap.add_argument("--cell", default="C2"); ap.add_argument("--prior", default="S2")
    ap.add_argument("--best-sha", default="ceec0222e0912a1c"); ap.add_argument("--last-sha", default="98bc88f7333f19ee")
    a = ap.parse_args()
    names = ("ref", "rmx", "last", "k1")
    roots = {n: os.path.join(C.CONF, getattr(a, n)) for n in names}
    raws = {n: load_raw("D2", root=roots[n]) for n in names}
    D = {n: raws[n][0] for n in names}; M = {n: raws[n][1].get((a.cell, a.prior), {}) for n in names}
    sel = lambda d: sorted((k for k in d if k[:2] == (a.cell, a.prior)), key=lambda k: k[2])
    keys = sel(D["rmx"]); grid = [float(s) for s in C.CELLS[a.cell]["snrs"]]
    bad = [f"{n}: point set != grid" for n in names if [k[2] for k in sel(D[n])] != grid]
    bad += [f"{n}: load_raw warning: {w.strip()}" for n in names for w in raws[n][2]]
    gits = set().union(*(chunk_meta(roots[n], a.cell, "run|git") for n in names[1:]))
    if len(gits) != 1 or any(g.endswith("+dirty") or g == "(none)" for g in gits):
        bad.append(f"code version across rmx/last/k1 chunks: {sorted(gits)} (one clean commit expected)")
    for n in names[1:]:
        r = chunk_meta(roots[n], a.cell, "meta|rotation")
        if len(r) != 1 or not next(iter(r)).startswith(f"deg={a.deg!r}:"):
            bad.append(f"{n}: meta|rotation {sorted(x[:20] for x in r)} != deg={a.deg!r}")
    # fit fingerprint (registration 수용 (c))
    full = {K: fit_ll("full", K) for K in (16, 32, 64, 128, 256, 512)}
    kron = {K: fit_ll("kron", K) for K in (16, 32, 64, 128, 256, 512, 1024, 2048, 4096)}
    sec15 = sum(v[1] for v in full.values()) + sum(v[1] for v in kron.values())
    sec13 = sum(v[1] for v in full.values()) + sum(kron[K][1] for K in (16, 32, 64, 128, 256, 512, 1024))
    for n, kk, sec in (("rmx", 4096, sec15), ("last", 4096, sec15), ("k1", 1024, sec13)):
        m = M[n]
        want = {f"ll_val|gmm{K}": full[K][0] for K in full} | {"ll_val|kron": kron[kk][0], "kron_K": float(kk), "em_sec": sec}
        diff = [f"{q} {m.get(q)} != {v}" for q, v in want.items() if m.get(q) is None or abs(float(m.get(q)) - v) > 1e-9 * max(1, abs(v))]
        if diff:
            bad.append(f"{n}: S2d fit fingerprint: " + "; ".join(diff[:4]))
    for n, sha, role in (("rmx", a.best_sha, "best"), ("last", a.last_sha, "last"), ("k1", a.best_sha, "best")):
        cid = str(M[n].get("stagec_ckpt_id", ""))
        if f"sha256[:16]={sha}" not in cid or f"role={role}" not in cid:
            bad.append(f"{n}: stagec_ckpt_id {cid[:70]!r} != {sha}/{role}")
    for k in keys if not bad else []:
        for n in names[1:]:
            for q in KEYS4:
                if not same(D["ref"][k][GENIE][q], D[n][k][GENIE][q]):
                    bad.append(f"{k[2]:+.0f} dB {n}: R5-genie|{q} differs from the ref raw (not the same trials / rotation)")
            if len(D[n][k][GENIE]["blk_err"]) != 2560:
                bad.append(f"{k[2]:+.0f} dB {n}: trial count != 2560")
        if a.deg == 0:
            r3 = D["rmx"][k].get("R3-bigamp", {})
            if not r3 or any(not same(r3[q], D["ref"][k]["R3-bigamp"][q]) for q in r3 if q in D["ref"][k]["R3-bigamp"]):
                bad.append(f"{k[2]:+.0f} dB: R3-bigamp (prior-free) not identical to the ref raw")
            for arm in (BSTAR, "R2-ours-G"):
                ok = ~(failed(D["rmx"][k], arm) | failed(D["ref"][k], arm))
                if same(np.asarray(D["rmx"][k][arm]["nmse"])[ok], np.asarray(D["ref"][k][arm]["nmse"])[ok]):
                    bad.append(f"{k[2]:+.0f} dB: {arm} nmse identical to the static raw (S2d fits not applied?)")
    print(f"# pair_rotmix deg={a.deg} ref {a.ref} rmx {a.rmx} last {a.last} k1 {a.k1}, cell {a.cell}, prior {a.prior}, "
          f"git {sorted(gits)}; integrity (point sets, one clean commit, meta angle, genie == ref, S2d fit fingerprint, ckpt ids"
          + (", R3 identical, S2d fits applied" if a.deg == 0 else "") + "): " + ("OK" if not bad else "FAILED: " + "; ".join(bad[:10])))
    if bad:
        sys.exit(1)
    ren = lambda n, arm, new: {k: {new: D[n][k][arm]} for k in keys}
    data = {k: {} for k in keys}
    for n, arm, new in (("ref", V1, "V1-static"), ("ref", BSTAR, "bstar-static"), ("ref", GENIE, "genie"), ("ref", "R2-ours-G", "R2-static"),
                        ("rmx", V1, "V1-drift-best"), ("rmx", BSTAR, "bstar-drift-4096"), ("rmx", "R2-ours-G", "R2-drift"),
                        ("last", V1, "V1-drift-last"), ("k1", BSTAR, "bstar-drift-1024")):
        for k in keys:
            data[k][new] = D[n][k][arm]
    snrs = [k[2] for k in keys]
    for x, y, name in (("V1-static", "V1-drift-last", f"DT-V1({a.deg:g}): V1 static (legacy-last) -> V1 drift-trained (last-EMA)"),
                       ("bstar-static", "bstar-drift-1024", f"DT-b*({a.deg:g}): b* static kron 1024 -> b* drift-trained kron 1024"),
                       ("V1-drift-best", "V1-drift-last", "report: V1 drift best -> V1 drift last"),
                       ("bstar-drift-1024", "bstar-drift-4096", "report: b* drift kron 1024 -> kron 4096"),
                       ("V1-static", "V1-drift-best", "report: V1 static (legacy-last) -> V1 drift best"),
                       ("bstar-static", "bstar-drift-4096", "report: b* static kron 1024 -> b* drift kron 4096"),
                       ("R2-static", "R2-drift", "report: R2 static -> R2 drift")):
        cand, res, powered, wy, wx, lab = table_b(data, a.cell, a.prior, snrs, x, y)
        A, Bn = sum(r[0] for r in res), sum(r[1] for r in res)
        print(f"{name}: {x} -> {y}  [anchor {x}]  decision SNRs {[f'{s:+.0f}' for s in cand]}")
        print("    sign test @16: " + "  ".join(f"{s:+.0f} dB {r[0]}:{r[1]} p={r[2]:.2g}" for s, r in zip(cand, res))
              + f"   pooled {A}:{Bn} p={sign_p(A, Bn):.2g}")
        print(f"    POWERED={powered}  second arm fewer at {wy}/{len(cand)}, first arm fewer at {wx}/{len(cand)}  -> {lab}")
        print(f"    SNR@0.1 gap ({x} minus {y}): {gain(data, a.cell, a.prior, snrs, x, y)['text']}")
    k3 = (a.cell, a.prior, -3.0)
    f = {arm: fails(data[k3], arm) for arm in data[k3]}
    for tag, bd in (("DD (registered: S2d b* kron 4096 + V1 last vs static b* 1024 + V1 legacy-last)", "bstar-drift-4096"),
                    ("report: same-K DD (S2d b* kron 1024)", "bstar-drift-1024")):
        s2d, sta = (f[bd], f["V1-drift-last"], f["genie"]), (f["bstar-static"], f["V1-static"], f["genie"])
        guard = all(0.005 <= x.mean() <= 0.9 and x.sum() > f["genie"].sum() for x in (f[bd], f["bstar-static"]))
        d0, lo, hi, nn = dd_boot([s2d], [sta], guard)
        Rs = lambda b, v, g: (b.sum() - v.sum()) / (b.sum() - g.sum())
        print(f"{tag} @ {a.deg:g} deg, -3 dB: R_S2d {Rs(*s2d):.3f} - R_static {Rs(*sta):.3f} = {d0:+.3f}"
              + (f"  [90% paired {lo:+.3f}, {hi:+.3f}]" + (f" ({nn} undefined replicates)" if nn else "")
                 + ("  -> CI > 0" if lo > 0 else "  -> CI < 0" if hi < 0 else "  -> CI contains 0") if guard else
                 "  -> undefined (out of range; secondary only)"))
        cand = decision_points(data, a.cell, a.prior, snrs, bd)
        cs = [tuple(fails(data[(a.cell, a.prior, s)], x) for x in (bd, "V1-drift-last", "genie")) for s in cand]
        ct = [tuple(fails(data[(a.cell, a.prior, s)], x) for x in ("bstar-static", "V1-static", "genie")) for s in cand]
        if cand:
            d2, lo2, hi2, _ = dd_boot(cs, ct, True)
            print(f"    secondary (decision points of {bd} {[f'{s:+.0f}' for s in cand]}, pooled): {d2:+.3f} [90% {lo2:+.3f}, {hi2:+.3f}]")
    print("BLER@16 failures / n per SNR " + " ".join(f"{s:+.0f}" for s in snrs) + " dB:")
    for arm in data[keys[0]]:
        print(f"    {arm:<20}" + " ".join(f"{int(fails(data[k], arm).sum()):5d}" for k in keys))


if __name__ == "__main__":
    main()
