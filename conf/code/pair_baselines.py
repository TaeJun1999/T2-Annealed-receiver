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


MAN = {}                                               # raw role -> manifest git_commit (--provenance manifest only)


def manifest_check(root, bad, role):
    """--provenance manifest (STATIC16e4 §1): for a raw written before run|git.  The manifest's git_commit is the HEAD when the
    MANIFEST was written (run_manifest.py), not the run commit -- printed as 'manifest-head:' only.  Checks: manifest exists, is
    git-tracked and clean; n_raw_files == chunks; its point list == the raw's point set; every chunk mtime <= manifest 'written';
    a git-tracked raw dir must be clean.  Returns the header string incl. sha256 over the sorted per-chunk sha256 list."""
    import hashlib, json, subprocess, datetime
    tag = os.path.basename(os.path.normpath(root))[len("raw_"):]
    f = os.path.join(C.CONF, "results", "review_next", f"run_manifest_{tag}.json")
    git = lambda *x: subprocess.run(["git", "-C", C.CONF, *x], capture_output=True, text=True).stdout.strip()
    if not os.path.exists(f):
        bad.append(f"{role}: no run manifest {os.path.basename(f)} (--provenance manifest)")
        return "(none)"
    if not git("ls-files", f) or git("status", "--porcelain", f):
        bad.append(f"{role}: manifest {os.path.basename(f)} not tracked / not clean")
    m = json.load(open(f)); chunks = sorted(glob.glob(os.path.join(root, "*.npz")))
    if m.get("n_raw_files") != len(chunks) or not m.get("git_commit"):
        bad.append(f"{role}: manifest n_raw_files {m.get('n_raw_files')} vs {len(chunks)} chunks, git {m.get('git_commit')}")
    pts = {os.path.basename(c).rsplit("_skip", 1)[0] for c in chunks}
    if set(m.get("points", [])) != pts:
        bad.append(f"{role}: manifest point list != raw point set ({len(m.get('points', []))} vs {len(pts)})")
    w = datetime.datetime.strptime(m["written"][:19], "%Y-%m-%d %H:%M:%S").timestamp()   # KST = the container clock (TZ=Asia/Seoul)
    late = [c for c in chunks if os.path.getmtime(c) > w]
    if late:
        bad.append(f"{role}: {len(late)} chunks newer than the manifest ({os.path.basename(late[0])})")
    if git("ls-files", root) and git("status", "--porcelain", root):
        bad.append(f"{role}: git-tracked raw dir has uncommitted changes")
    digest = hashlib.sha256("".join(hashlib.sha256(open(c, "rb").read()).hexdigest() for c in chunks).encode()).hexdigest()[:16]
    MANI[role] = m
    return f"manifest-head:{m.get('git_commit')}/chunks-sha:{digest}"


MANI = {}                                              # raw role -> manifest dict (--provenance manifest only)


def table_b(data, cell, prior, snrs, x, y, cand=None):
    if cand is None:                                            # default; cand given = decision SNRs fixed by a registration (--pairs)
        cand = decision_points(data, cell, prior, snrs, x)      # anchor = the first member (08_SPEC §2)
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
    ap.add_argument("--r0", choices=("at16", "at1"), default="at16", help="R0-pilot reading: at16 = the 16-iteration trajectory "
                    "(S2V16e4 / ROTMIX16e4 records); at1 = the 1-pass reading 08_SPEC §1 calls R0-pilot (SUPP16e4, load_raw alias "
                    "'R0-pilot@1')")
    ap.add_argument("--add-baselines", nargs="*", default=[], help="SPARSE16e4: extra baseline arms (from --extra raws) appended to the baseline set; default none = the 12 of SUPP16e4 §1, unchanged")
    ap.add_argument("--expect", action="append", default=[], help="STATIC16e4: ARM=LABEL recorded before this run, e.g. "
                    "'V1-pilot=(i)'; a different recomputed label is code drift -> exit 1 (repeatable)")
    ap.add_argument("--expect-bstar", default=None, help="SUPP16e4: the b* -> V1 label the original registration recorded "
                    "('(i)', '(iii)', ...); a different recomputed label is code drift -> exit 1")
    ap.add_argument("--extra", action="append", default=[], help="SUPP16e4: further raws of the SAME trials holding more loop "
                    "arms (merged into the base after the genie / meta / commit checks; an arm may not appear twice)")
    ap.add_argument("--provenance", choices=("run-git", "manifest"), default="run-git",
                    help="run-git (default, unchanged) = one clean run|git commit per raw.  manifest (STATIC16e4, user decision "
                         "2026-09-29 CDT) = for raws written BEFORE run|git existed (no chunk carries the key): each raw must have "
                         "results/review_next/run_manifest_<tag>.json with n_raw_files == its chunk count and a git_commit, printed "
                         "in the header; a raw that DOES carry run|git is still held to the one-clean-commit rule")
    ap.add_argument("--pairs", nargs="+", default=None, metavar="X>Y[@S1,S2,S3]",
                    help="SITE16e4: after the integrity checks, table B for exactly these pairs `X -> Y` (a = only X fails) and "
                         "nothing else (no baseline loop, no summary); '@S1,S2,S3' fixes the decision SNRs (the anchor rule on X is "
                         "then printed as a check only), without it the anchor rule on X applies.  Default: unchanged behaviour")
    ap.add_argument("--legacy", action="store_true", help="VALIDATION ONLY on raws older than run|git (DOP/ROT code): skip "
                    "the one-clean-commit check.  Never used for a registered tag.")
    a = ap.parse_args()
    roots = {k: os.path.join(C.CONF, getattr(a, k)) for k in ("base", "pil", "ald")}
    if a.ref:
        roots["ref"] = os.path.join(C.CONF, a.ref)
    for i, e in enumerate(a.extra):
        roots[f"extra{i}"] = os.path.join(C.CONF, e)
    EXTRA = [f"extra{i}" for i in range(len(a.extra))]
    raws = {k: load_raw("D2", root=r) for k, r in roots.items()}
    b, p, m = raws["base"][0], raws["pil"][0], raws["ald"][0]
    sel = lambda d: sorted((k for k in d if k[:2] == (a.cell, a.prior)), key=lambda k: k[2])
    keys = sel(b)
    grid = [float(s) for s in C.CELLS[a.cell]["snrs"]]
    bad = [f"{n}: point set {[k[2] for k in sel(raws[n][0])]} != grid {grid}" for n in raws if [k[2] for k in sel(raws[n][0])] != grid]
    bad += [f"{n}: load_raw warning: {w.strip()}" for n in raws for w in raws[n][2]]
    for n in ["base", "pil", "ald"] + EXTRA:
        g = chunk_meta(roots[n], a.cell, "run|git")
        if a.provenance == "manifest" and g == {"(none)"}:
            MAN[n] = manifest_check(roots[n], bad, n)
        elif not a.legacy and (len(g) != 1 or any(x.endswith("+dirty") or x == "(none)" for x in g)):
            bad.append(f"{n}: code version across chunks {sorted(g)} (one clean commit expected)")
    for mk in ("meta|rotation", "meta|doppler"):
        mv = {n: chunk_meta(roots[n], a.cell, mk) for n in ["base", "pil", "ald"] + EXTRA}
        if len(mv["base"]) != 1 or any(mv[n] != mv["base"] for n in mv):
            bad.append(f"{mk} differs across raws: {mv}")
    deg = next(iter(chunk_meta(roots["base"], a.cell, "meta|rotation")))
    dop = next(iter(chunk_meta(roots["base"], a.cell, "meta|doppler")))
    est = np.load(os.path.join(C.CONF, "results", "ald", f"ald_{a.est}.npz"), allow_pickle=True)
    pil = np.load(os.path.join(C.CONF, "results", "ald", f"pilots_{a.est}_test.npz"), allow_pickle=True)
    bm = raws["base"][1].get((a.cell, a.prior), {})
    prov = str(est["prov"]) if "prov" in est.files else ""
    sid = str(bm.get("stagec_ckpt_id", "")).split()
    sha = sid[0].replace("sha256[:16]=", "") if sid else ""
    if not sha and a.provenance == "manifest" and bm.get("stagec_ckpt"):   # raws older than meta|stagec_ckpt_id
        import hashlib
        fsha = hashlib.sha256(open(str(bm["stagec_ckpt"]), "rb").read()).hexdigest()[:16]
        msid = str(MANI.get("base", {}).get("stagec_ckpt_id", "")).split()
        msha = msid[0].replace("sha256[:16]=", "") if msid and msid[0] != "(none)" else ""
        if msha and msha != fsha:
            bad.append(f"base V1 checkpoint: manifest id {msha} != file {os.path.basename(str(bm['stagec_ckpt']))} sha {fsha}")
        sha = msha or fsha
        print(f"# base V1 checkpoint id: manifest {msha or '(none)'}, file {os.path.basename(str(bm['stagec_ckpt']))} {fsha}")
    if sha and sha not in prov + str(est["ckpt_sha"] if "ckpt_sha" in est.files else ""):
        bad.append(f"ALD estimate checkpoint (prov {prov[:80]!r}) is not the base's V1 checkpoint {sha}")
    erot = float(pil["rotation"]) if "rotation" in pil.files else -1.0
    brot = float(deg.split(":")[0].replace("deg=", "")) if deg.startswith("deg=") else -1.0
    if erot != brot:
        bad.append(f"ALD pilots rotation {erot} != base rotation {brot}")
    edop = float(pil["doppler"]) if "doppler" in pil.files else -1.0
    bdop = float(dop.split(" ")[0].replace("nu=", "")) if dop.startswith("nu=") else -1.0
    if edop != bdop:
        bad.append(f"ALD pilots doppler {edop} != base doppler {bdop}")
    for k in keys if not bad else []:
        for q in KEYS4:
            for n in [x for x in ["pil", "ald", "ref"] + EXTRA if x in raws]:
                if not same(b[k][GENIE][q], raws[n][0][k][GENIE][q]):
                    bad.append(f"{k[2]:+.0f} dB R5-genie|{q} differs ({n} vs base)")
        if not all(len(d[k][GENIE]["blk_err"]) == 2560 for d in [b, p, m] + [raws[n][0] for n in EXTRA]):
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
    print(f"# pair_baselines {a.base} + {a.pil} + {a.ald}" + "".join(f" + {e}" for e in a.extra) + (f" (genie ref {a.ref})" if a.ref else "")
          + f", cell {a.cell}, prior {a.prior}, rotation {deg[:12]}, doppler {dop[:12]}, git "
          + " ".join(f"{n}={MAN.get(n) or ','.join(sorted(chunk_meta(roots[n], a.cell, 'run|git')))}" for n in ["base"] + EXTRA + ["pil", "ald"]) + "; "
          f"integrity: " + ("OK" if not bad else "FAILED: " + "; ".join(bad[:10])))
    if bad:
        sys.exit(1)                                     # an invalid tag gets no label (registrations §1)
    for n in EXTRA:                                   # SUPP16e4: more loop arms of the same trials; never overwrite an arm
        dup = sorted((set(raws[n][0][keys[0]]) & set(b[keys[0]])) - {GENIE, "run", "meta"})
        if dup:
            print(f"# extra raw {n} repeats arms {dup} -- refusing"); sys.exit(1)
        for k in keys:
            b[k] = {**b[k], **{x: v for x, v in raws[n][0][k].items() if x not in (GENIE, "run", "meta")}}
    miss = [x for x in (BSTAR, V1) + BASELINES + tuple(a.add_baselines) if x not in b[keys[0]] and x not in PIL + ALD]
    if miss:
        print(f"# arms missing after the merge: {miss} -- refusing"); sys.exit(1)
    data = {k: {**b[k], **{x: p[k][x] for x in PIL}, **{x: m[k][x] for x in ALD}} for k in keys}
    BL = tuple("R0-pilot@1" if (x == "R0-pilot" and a.r0 == "at1") else x for x in BASELINES) + tuple(a.add_baselines)
    if a.r0 == "at1":
        print("# R0-pilot read at @1 (1-pass, 08_SPEC §1; load_raw alias 'R0-pilot@1'), SUPP16e4 §1")
    snrs = [k[2] for k in keys]
    if a.pairs:                                         # SITE16e4: only the listed pairs, same table_b / paired / gain as below
        for spec in a.pairs:
            xy, _, pts = spec.partition("@"); x, y = xy.split(">")
            fixed = sorted(float(s) for s in pts.split(",")) if pts else None
            if x not in data[keys[0]] or y not in data[keys[0]] or (fixed and not set(fixed) <= set(snrs)):
                print(f"# --pairs {spec}: arm missing or a fixed decision SNR off the grid {snrs} -- refusing"); sys.exit(1)
            cand, res, powered, wy, wx, lab = table_b(data, a.cell, a.prior, snrs, x, y, fixed)
            A, Bn = sum(r[0] for r in res), sum(r[1] for r in res)
            auto = [f"{s:+.0f}" for s in decision_points(data, a.cell, a.prior, snrs, x)]
            print(f"{x} -> {y}  [" + (f"decision SNRs FIXED; check: the anchor rule on {x} gives {auto}" if fixed else f"anchor {x}")
                  + f"]  decision SNRs {[f'{s:+.0f}' for s in cand]}")
            print("    sign test @16: " + "  ".join(f"{s:+.0f} dB {r[0]}:{r[1]} p={r[2]:.2g}" for s, r in zip(cand, res))
                  + f"   pooled {A}:{Bn} p={sign_p(A, Bn):.2g}")
            print(f"    POWERED={powered}  second arm fewer at {wy}/{len(cand)}, first arm fewer at {wx}/{len(cand)}  -> {lab}")
            print(f"    SNR@0.1 gap ({x} minus {y}): {gain(data, a.cell, a.prior, snrs, x, y)['text']}")
            print("    failures@16 at the decision SNRs: " + "  ".join(
                f"{arm} " + "/".join(str(int(fails(data[(a.cell, a.prior, s)], arm).sum())) for s in cand) for arm in (x, y)))
        return
    k3 = (a.cell, a.prior, -3.0)
    rows, labs = [], {}
    fv3, fg3 = (fails(data[k3], arm) for arm in (V1, GENIE))
    vg = fg3.sum() >= fv3.sum()                         # SUPP16e4 §1: the genie fails at least as often as V1 (DOP nu = 0.01)
    if vg:
        print(f"# genie -3 dB failures {int(fg3.sum())} >= V1 {int(fv3.sum())}: R_X undefined for every X at -3 dB (SUPP16e4 §1 guard)")
    for x in (BSTAR,) + BL:
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
        if vg:
            r1 = "undefined (the genie fails at least as often as V1 at -3 dB)"
        elif not (0.005 <= bl <= 0.9) or fx.sum() <= fg.sum():
            r1 = "undefined (out of range: -3 dB BLER %.4f, F_X %d, F_genie %d)" % (bl, fx.sum(), fg.sum())
        else:
            R, lo, hi, nn = recovery([(fx, fv, fg)])
            r1 = (f"{R:.3f} [90% {lo:.3f}, {hi:.3f}]" + (f" ({nn} undefined replicates)" if nn else "")
                  + (" -> 정의 불가 (>5% undefined)" if nn > 0.05 * B_BOOT else ""))
        cols2 = [tuple(fails(data[(a.cell, a.prior, s)], arm) for arm in (x, V1, GENIE)) for s in cand]
        if cand and sum(c[2].sum() for c in cols2) >= sum(c[1].sum() for c in cols2):
            r2 = "undefined (the genie fails at least as often as V1 over the decision points)"
        elif cand:
            R2, lo2, hi2, nn2 = recovery(cols2)
            r2 = f"{R2:.3f} [90% {lo2:.3f}, {hi2:.3f}] over {len(cand)} point(s)" + (f" ({nn2} undefined)" if nn2 else "")
        else:
            r2 = "undefined (no decision point)"
        print(f"    absolute gap -3 dB: F_X - F_V1 = {int(fx.sum() - fv.sum())} blocks of {len(fx)}")
        print(f"    R_X -3 dB (primary): {r1}")
        print(f"    R_X decision points (secondary): {r2}")
        rows.append((x, int(fx.sum()), lab, r1))
    k = sum(1 for x in labs if labs[x] == "(i)"); mm = sum(1 for x in labs if labs[x] == "(ii)")
    kB = k - (labs[BSTAR] == "(i)"); mB = mm - (labs[BSTAR] == "(ii)")
    print(f"SUMMARY-B (baselines without b*, {len(BL)}): (i) {kB}, (ii) {mB}, not decided {len(BL) - kB - mB}; b* -> V1 {labs[BSTAR]}")
    if a.expect_bstar and labs[BSTAR] != a.expect_bstar:
        print(f"# b* -> V1 recomputed {labs[BSTAR]} != recorded {a.expect_bstar}: code drift -- no summary sentence"); sys.exit(1)
    for e in a.expect:
        arm, lab = e.split("=", 1)
        if labs.get(arm) != lab:
            print(f"# {arm} -> V1 recomputed {labs.get(arm)} != recorded {lab}: code drift -- no summary sentence"); sys.exit(1)
    xs = min(rows, key=lambda r: (r[1], r[0]))
    fx, fv, fg = (fails(data[k3], arm) for arm in (xs[0], V1, GENIE))
    ok_range = 0.005 <= fx.mean() <= 0.9 and fx.sum() > fg.sum() and not vg
    R, lo, hi, nn = recovery([(fx, fv, fg)]) if ok_range else (np.nan, np.nan, np.nan, 0)
    print(f"\nSUMMARY registered baselines {len(labs)} (b* + 𝔅 {len(BL)}): (i) {k}, (ii) {mm}, "
          f"not decided {len(labs) - k - mm}")
    print("    " + "  ".join(f"{x}={labs[x]}" for x in labs))
    print(f"X* (fewest -3 dB failures, ties by name) = {xs[0]} (F={xs[1]}); R_X* -3 dB = "
          + (f"{R:.3f} [90% {lo:.3f}, {hi:.3f}]" if ok_range else "undefined (out of range)"))
    cond = k == len(labs) and mm == 0 and ok_range and lo > 0
    print(f"'등록된 baseline 전부와 멀어진다' condition (k = {len(labs)}, (ii) = 0, R_X* CI lower > 0): {'MET' if cond else 'NOT met'}")
    print("BLER@16 failures / n per SNR " + " ".join(f"{s:+.0f}" for s in snrs) + " dB:")
    for arm in dict.fromkeys((GENIE, V1, BSTAR) + BL + ("R0-pilot", "M-ours-dscore-C-V0", "M-ours-dscore-C-V4", "M-ours-dscore-C-V4b")):
        if arm in data[keys[0]]:
            print(f"    {arm:<20}" + " ".join(f"{int(fails(data[k], arm).sum()):5d}" for k in keys))
    print("report-only, median NMSE@16 of the channel estimate per SNR:")
    for arm in (V1, BSTAR) + BL:
        if arm in data[keys[0]] and "nmse" in data[keys[0]][arm]:
            print(f"    {arm:<20}" + " ".join(f"{np.nanmedian(np.asarray(data[k][arm]['nmse'])[:, -1]):.2e}" for k in keys))


if __name__ == "__main__":
    main()
