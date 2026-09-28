"""conf/code/pair_baselines.py -- "V1 against EVERY registered baseline" (NEXT_EXPERIMENTS_S2V16e4 §1 판정 1·2 / X*,
NEXT_EXPERIMENTS_ROTMIX16e4 §1 판정 1·3): table B `X -> V1` for X in {b*} + the baseline set (13), the genie-gap recovery
R_X = (F_X - F_V1)/(F_X - F_genie) per X with a paired bootstrap (the three arms resampled together), the closest baseline
X* (fewest -3 dB failures, ties by name) and the registered "all registered baselines" sentence condition.

The loop arms live in the base raw (14 arms), V1-pilot / bstar-pilot in the PIL raw, ALD-pilot / ALDv-pilot in the ALD raw,
all on the SAME trials (stream fixed by testbed, prior, Nr, T, Tp, SNR; rotation draws nothing).  Integrity (any failure ->
exit 1 BEFORE any label): same point set = the cell's grid in every raw, no load_raw warning, R5-genie 4 keys identical in
PIL / ALD (and --ref, when given) vs the base, 2560 trials, one clean code version per raw, the base's meta|rotation (if any)
equal in PIL / ALD, no raised trial in the pilot-only / ALD arms, V1-pilot@1 == V1@1 and bstar-pilot@1 == b*@1, the ALD
arms' estimate fixed over iterations and equal to the precomputed estimate (nmse@1 vs results/ald/, rtol 1e-9), the ALD
estimate's checkpoint sha == the base's V1 checkpoint and its rotation == the base's rotation.
    python code/pair_baselines.py --base raw_S2vB16e4 --pil raw_S2vPIL --ald raw_S2vALD --est S2vALD --cell C6 --prior S2v
    python code/pair_baselines.py --base raw_RMX15 --pil raw_RMX15PIL --ald raw_RMX15ALD --est RMX15ALD --cell C2 --prior S2 \
        --ref raw_ROTaB16e4k
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
from recovery_ci import boot

V1, BSTAR, GENIE = "M-ours-dscore-C-V1", "M-ours-bstar", "R5-genie"
BASELINES = ("M-ours-bstar-scalar", "M-ours-gmm32", "R0-pilot", "R1-turbo", "R2-ours-G", "R3-bigamp", "R4-llr", "R4-scvamp",
             "bstar-pilot", "V1-pilot", "ALD-pilot", "ALDv-pilot")        # 𝔅, fixed by the registrations (12)
PIL, ALD = ("V1-pilot", "bstar-pilot"), ("ALD-pilot", "ALDv-pilot")
KEYS4 = ("blk_err", "ber", "tauL_gmean", "alphaD")
B_BOOT, SEED = 2000, 20260926


def fails(d, arm):
    v = np.asarray(d[arm]["blk_err"])[:, -1]
    return np.where(np.isfinite(v), v, 1.0)                     # a raised block is a failure (01_RULES §4)


def chunk_meta(root, cell, key):
    vals = set()
    for f in glob.glob(os.path.join(root, f"D2_{cell}_*.npz")):
        with np.load(f) as z:
            vals.add(str(z[key]) if key in z.files else "(none)")
    return vals


def table_b(data, cell, prior, snrs, x, y):
    cand = decision_points(data, cell, prior, snrs, x)          # anchor = the first member (08_SPEC §2)
    res = [paired(data[(cell, prior, s)], x, y) for s in cand]
    powered = len(cand) == 3 and sum(1 for r in res if r[0] + r[1] >= MIN_DISC) >= 2
    wy = sum(1 for r in res if r[0] > r[1] and r[2] < 0.05); wx = sum(1 for r in res if r[1] > r[0] and r[2] < 0.05)
    lab = "(iv)" if not powered else "(i)" if wy >= 2 else "(ii)" if wx >= 2 else "(iii)"
    return cand, res, powered, wy, wx, lab


def recovery(cols):
    """cols = [(F_X, F_V1, F_genie) per SNR] -> (R, lo, hi, n_undefined_replicates)."""
    X, V, G = (sum(c[i].sum() for c in cols) for i in range(3))
    (lo, hi), nn = boot(cols, B_BOOT, SEED)
    return ((X - V) / (X - G) if X - G > 0 else np.nan), lo, hi, nn


def main():
    ap = argparse.ArgumentParser()
    for k in ("--base", "--pil", "--ald", "--est", "--cell", "--prior"):
        ap.add_argument(k, required=True)
    ap.add_argument("--ref", default=None, help="an external raw of the same trials whose R5-genie must match (ROTMIX)")
    ap.add_argument("--legacy", action="store_true", help="VALIDATION ONLY on raws older than run|git (DOP/ROT code): skip "
                    "the one-clean-commit check.  Never used for a registered tag.")
    a = ap.parse_args()
    roots = {k: os.path.join(C.CONF, getattr(a, k)) for k in ("base", "pil", "ald")}
    if a.ref:
        roots["ref"] = os.path.join(C.CONF, a.ref)
    raws = {k: load_raw("D2", root=r) for k, r in roots.items()}
    b, p, m = raws["base"][0], raws["pil"][0], raws["ald"][0]
    sel = lambda d: sorted((k for k in d if k[:2] == (a.cell, a.prior)), key=lambda k: k[2])
    keys = sel(b)
    grid = [float(s) for s in C.CELLS[a.cell]["snrs"]]
    bad = [f"{n}: point set {[k[2] for k in sel(raws[n][0])]} != grid {grid}" for n in raws if [k[2] for k in sel(raws[n][0])] != grid]
    bad += [f"{n}: load_raw warning: {w.strip()}" for n in raws for w in raws[n][2]]
    for n in ("base", "pil", "ald"):
        g = chunk_meta(roots[n], a.cell, "run|git")
        if not a.legacy and (len(g) != 1 or any(x.endswith("+dirty") or x == "(none)" for x in g)):
            bad.append(f"{n}: code version across chunks {sorted(g)} (one clean commit expected)")
    rot = {n: chunk_meta(roots[n], a.cell, "meta|rotation") for n in ("base", "pil", "ald")}
    if len(rot["base"]) != 1 or rot["pil"] != rot["base"] or rot["ald"] != rot["base"]:
        bad.append(f"meta|rotation differs across raws: {rot}")
    deg = next(iter(rot["base"]))
    est = np.load(os.path.join(C.CONF, "results", "ald", f"ald_{a.est}.npz"), allow_pickle=True)
    pil = np.load(os.path.join(C.CONF, "results", "ald", f"pilots_{a.est}_test.npz"), allow_pickle=True)
    bm = raws["base"][1].get((a.cell, a.prior), {})
    prov = str(est["prov"]) if "prov" in est.files else ""
    sha = str(bm.get("stagec_ckpt_id", "")).split()[0].replace("sha256[:16]=", "")
    if sha and sha not in prov + str(est["ckpt_sha"] if "ckpt_sha" in est.files else ""):
        bad.append(f"ALD estimate checkpoint (prov {prov[:80]!r}) is not the base's V1 checkpoint {sha}")
    erot = float(pil["rotation"]) if "rotation" in pil.files else -1.0
    brot = float(deg.split(":")[0].replace("deg=", "")) if deg.startswith("deg=") else -1.0
    if erot != brot:
        bad.append(f"ALD pilots rotation {erot} != base rotation {brot}")
    for k in keys if not bad else []:
        for q in KEYS4:
            for n in [x for x in ("pil", "ald", "ref") if x in raws]:
                if not same(b[k][GENIE][q], raws[n][0][k][GENIE][q]):
                    bad.append(f"{k[2]:+.0f} dB R5-genie|{q} differs ({n} vs base)")
        if not all(len(d[k][GENIE]["blk_err"]) == 2560 for d in (b, p, m)):
            bad.append(f"{k[2]:+.0f} dB: trial count != 2560")
        for arm, d in [(x, p) for x in PIL] + [(x, m) for x in ALD]:
            if failed(d[k], arm).any():
                bad.append(f"{k[2]:+.0f} dB {arm}: {int(failed(d[k], arm).sum())} raised trials")
        for x, y in (("V1-pilot", V1), ("bstar-pilot", BSTAR)):
            ok = ~(failed(p[k], x) | failed(b[k], y))
            if not same(np.asarray(p[k][x]["nmse"])[ok, 0], np.asarray(b[k][y]["nmse"])[ok, 0]):
                bad.append(f"{k[2]:+.0f} dB {x}@1 != {y}@1")
        j = int(np.flatnonzero(np.isclose(est["snrs"], k[2]))[0])
        H, hh = pil["H"][j], est["hhat"][j]
        ref = np.sum(np.abs(hh - H) ** 2, -1) / np.sum(np.abs(H) ** 2, -1)
        for arm in ALD:
            nm = np.asarray(m[k][arm]["nmse"])
            if not same(nm, np.repeat(nm[:, :1], nm.shape[1], axis=1)) or not np.allclose(nm[:, 0], ref, rtol=1e-9, atol=0):
                bad.append(f"{k[2]:+.0f} dB {arm}: channel estimate not the precomputed ALD estimate")
    print(f"# pair_baselines {a.base} + {a.pil} + {a.ald}" + (f" (genie ref {a.ref})" if a.ref else "")
          + f", cell {a.cell}, prior {a.prior}, rotation {deg}, git {sorted(chunk_meta(roots['base'], a.cell, 'run|git'))}; "
          f"integrity: " + ("OK" if not bad else "FAILED: " + "; ".join(bad[:10])))
    if bad:
        sys.exit(1)                                     # an invalid tag gets no label (registrations §1)
    data = {k: {**b[k], **{x: p[k][x] for x in PIL}, **{x: m[k][x] for x in ALD}} for k in keys}
    snrs = [k[2] for k in keys]
    k3 = (a.cell, a.prior, -3.0)
    rows, labs = [], {}
    for x in (BSTAR,) + BASELINES:
        cand, res, powered, wy, wx, lab = table_b(data, a.cell, a.prior, snrs, x, V1)
        labs[x] = lab
        A, Bn = sum(r[0] for r in res), sum(r[1] for r in res)
        print(f"{x} -> {V1}  [anchor {x}]  decision SNRs {[f'{s:+.0f}' for s in cand]}")
        print("    sign test @16: " + "  ".join(f"{s:+.0f} dB {r[0]}:{r[1]} p={r[2]:.2g}" for s, r in zip(cand, res))
              + f"   pooled {A}:{Bn} p={sign_p(A, Bn):.2g}")
        print(f"    POWERED={powered}  second arm fewer at {wy}/{len(cand)}, first arm fewer at {wx}/{len(cand)}  -> {lab}")
        print(f"    SNR@0.1 gap ({x} minus V1): {gain(data, a.cell, a.prior, snrs, x, V1)['text']}")
        fx, fv, fg = (fails(data[k3], arm) for arm in (x, V1, GENIE))
        bl = fx.mean()
        if not (0.005 <= bl <= 0.9) or fx.sum() <= fg.sum():
            r1 = "undefined (out of range: -3 dB BLER %.4f, F_X %d, F_genie %d)" % (bl, fx.sum(), fg.sum())
        else:
            R, lo, hi, nn = recovery([(fx, fv, fg)])
            r1 = (f"{R:.3f} [90% {lo:.3f}, {hi:.3f}]" + (f" ({nn} undefined replicates)" if nn else "")
                  + (" -> 정의 불가 (>5% undefined)" if nn > 0.05 * B_BOOT else ""))
        if cand:
            R2, lo2, hi2, nn2 = recovery([tuple(fails(data[(a.cell, a.prior, s)], arm) for arm in (x, V1, GENIE)) for s in cand])
            r2 = f"{R2:.3f} [90% {lo2:.3f}, {hi2:.3f}] over {len(cand)} point(s)" + (f" ({nn2} undefined)" if nn2 else "")
        else:
            r2 = "undefined (no decision point)"
        print(f"    R_X -3 dB (primary): {r1}")
        print(f"    R_X decision points (secondary): {r2}")
        rows.append((x, int(fx.sum()), lab, r1))
    k = sum(1 for x in labs if labs[x] == "(i)"); mm = sum(1 for x in labs if labs[x] == "(ii)")
    xs = min(rows, key=lambda r: (r[1], r[0]))
    fx, fv, fg = (fails(data[k3], arm) for arm in (xs[0], V1, GENIE))
    ok_range = 0.005 <= fx.mean() <= 0.9 and fx.sum() > fg.sum()
    R, lo, hi, nn = recovery([(fx, fv, fg)]) if ok_range else (np.nan, np.nan, np.nan, 0)
    print(f"\nSUMMARY registered baselines {len(labs)} (b* + 𝔅 {len(BASELINES)}): (i) {k}, (ii) {mm}, "
          f"not decided {len(labs) - k - mm}")
    print("    " + "  ".join(f"{x}={labs[x]}" for x in labs))
    print(f"X* (fewest -3 dB failures, ties by name) = {xs[0]} (F={xs[1]}); R_X* -3 dB = "
          + (f"{R:.3f} [90% {lo:.3f}, {hi:.3f}]" if ok_range else "undefined (out of range)"))
    cond = k == len(labs) and mm == 0 and ok_range and lo > 0
    print(f"'등록된 baseline 전부와 멀어진다' condition (k = {len(labs)}, (ii) = 0, R_X* CI lower > 0): {'MET' if cond else 'NOT met'}")
    print("BLER@16 failures / n per SNR " + " ".join(f"{s:+.0f}" for s in snrs) + " dB:")
    for arm in (GENIE, V1, BSTAR) + BASELINES + ("M-ours-dscore-C-V0", "M-ours-dscore-C-V4", "M-ours-dscore-C-V4b"):
        if arm in data[keys[0]]:
            print(f"    {arm:<20}" + " ".join(f"{int(fails(data[k], arm).sum()):5d}" for k in keys))
    print("report-only, median NMSE@16 of the channel estimate per SNR:")
    for arm in (V1, BSTAR) + BASELINES:
        if arm in data[keys[0]] and "nmse" in data[keys[0]][arm]:
            print(f"    {arm:<20}" + " ".join(f"{np.nanmedian(np.asarray(data[k][arm]['nmse'])[:, -1]):.2e}" for k in keys))


if __name__ == "__main__":
    main()
