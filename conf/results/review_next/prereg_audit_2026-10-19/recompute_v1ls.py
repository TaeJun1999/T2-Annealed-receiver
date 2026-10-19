"""recompute_v1ls.py -- independent recomputation for audit_V1LS.md (NEXT_EXPERIMENTS_V1LS §6, four runs).

Reads the raw chunks (npz) with numpy only -- nothing under conf/code or Demo/ is imported; every rule of §1.4 (sign test,
decision points, power guard, labels, SNR@0.1 gap + 90 % paired bootstrap, sum F / R + bootstrap, MONOTONE, SUFFIX) is
re-implemented here from the registration text, and the exact two-sided sign-test p is cross-checked with scipy.binomtest.
The committed compare_<T>.txt is then parsed and every reproducible line is compared string-for-string (same formats).
Also: chunk plan / meta / raised-block checks (acceptance ②), the bit-identity check of V1 · b* · genie against the reference
raw over EVERY key with that arm prefix (acceptance ③, a superset of KEYS_RAW), the §6.5 predictions 4 · 5, and the
re-application of lowsig/SELECTION_RULE.md (M, no-harm, PRIMARY, M4, paired counts of §0) from the development screens.

    CUDA_VISIBLE_DEVICES= nice -n 10 taskset -c 14-17 ~/miniforge3/envs/torch/bin/python -B recompute_v1ls.py > recompute_v1ls.out
"""
import glob
import math
import os
import re
import sys

import numpy as np
from scipy.stats import binomtest

CONF = "/home/HTJ/t2/conf"
RN = os.path.join(CONF, "results", "review_next")
V1, BS, G = "M-ours-dscore-C-V1", "M-ours-bstar", "R5-genie"
A_, B_, C_ = "M-ours-dscore-C-V1-clamp", "M-ours-dscore-C-V1-gmmfb", "M-ours-dscore-C-V1-wide"
ARMS6 = (V1, BS, G, A_, B_, C_)
VARS = (C_, A_, B_)                       # primary first, then the two report-only variants
KEYS_RAW = ("blk_err", "ber", "nmse", "tauL_gmean", "alphaD", "tauL_clip_frac", "alphaD_clip")
N, CH, HIGH = 2560, 40, (18, 21)
RUN_GIT = "1d706648"
U28 = dict(prior="UMi28", pil="eig", v1sha="6f3a1b9490864af1", v1ep="epoch=379 best_epoch=379 role=best", wsha="03cc9005164fe31d",
           wep="epoch=493 best_epoch=493 role=best", wtag="UMi28HSUd", slo="0.032681101782796075", K=4096, ll=5.797910431000217)
D2 = dict(prior="S2", pil="dft", v1sha="4443921ce8d5c4a1", v1ep="epoch=1784 best_epoch=1764 role=legacy-last", wsha="bd48a8860ca2543e",
          wep="epoch=1028 best_epoch=1008 role=last", wtag="HSUd", slo="0.033062204571989696", K=1024, ll=-11.459169831224418)
QG, SG = [-3, 0, 3, 6, 9, 12, 15, 18, 21], [3, 6, 9, 12, 15, 18, 21]
RUNS = [("U28LSQ", dict(U28, mod="qpsk", grid=QG, ref="raw_U28B16e4")),
        ("U28LS16", dict(U28, mod="16qam", grid=SG, ref="raw_U28QAM16")),
        ("D2LSQ", dict(D2, mod="qpsk", grid=QG, ref="raw_B16e4k")),
        ("D2LS16", dict(D2, mod="16qam", grid=SG, ref="raw_D2QAM16"))]

TOT = {"match": 0, "mismatch": 0}
MIS = []


def tally(ok, what):
    TOT["match" if ok else "mismatch"] += 1
    if not ok:
        MIS.append(what)
    return ok


# ----------------------------------------------------------------------------- statistics (re-implemented from §1.4)
def sign_p(a, b):
    """exact two-sided sign test, integer arithmetic (min(1, 2 P[X <= min(a,b)]), X ~ Bin(a+b, 1/2))."""
    n, k = a + b, min(a, b)
    return 1.0 if n == 0 else min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def sign_p_scipy(a, b):
    n = a + b
    return 1.0 if n == 0 else binomtest(min(a, b), n, 0.5, alternative="two-sided").pvalue


def paired(ex, ey):
    a = int(np.sum((ex == 1) & (ey == 0)))
    b = int(np.sum((ex == 0) & (ey == 1)))
    return a, b, sign_p(a, b)


def decision_points(F_anchor, grid):
    bl = {s: max(F_anchor[s] / N, 0.5 / N) for s in grid}
    cand = sorted((s for s in grid if 0.005 <= bl[s] <= 0.9), key=lambda s: abs(math.log10(bl[s] / 0.1)))[:3]
    return sorted(cand)


def snr_at(snrs, bler, n, target=0.1):
    lb = np.log10(np.maximum(np.asarray(bler, float), 0.5 / n))
    lt = math.log10(target)
    if lb[0] <= lt:
        return snrs[0], "lo"
    for i in range(len(snrs) - 1):
        if lb[i] > lt >= lb[i + 1]:
            return snrs[i] + (lb[i] - lt) / (lb[i] - lb[i + 1]) * (snrs[i + 1] - snrs[i]), "ok"
    return snrs[-1], "hi"


def gap(ex, ey, snrs, B=2000, seed=20260925):
    """SNR@0.1(x) - SNR@0.1(y); paired bootstrap: at every SNR the same resampled trial indices for both arms, B replicates."""
    n = min(len(e) for e in ex)
    (vx, fx), (vy, fy) = snr_at(snrs, [e.mean() for e in ex], n), snr_at(snrs, [e.mean() for e in ey], n)
    if not (fx == "ok" and fy == "ok"):
        return dict(est=vx - vy, lo=np.nan, hi=np.nan, cens=np.nan, flags=(fx, fy))
    rng = np.random.default_rng(seed)
    g = np.empty(B)
    for r in range(B):
        bx, by = [], []
        for a, b in zip(ex, ey):
            i = rng.integers(len(a), size=len(a))
            bx.append(a[i].mean())
            by.append(b[i].mean())
        (ux, gx), (uy, gy) = snr_at(snrs, bx, n), snr_at(snrs, by, n)
        g[r] = ux - uy if gx == gy == "ok" else np.nan
    cens = float(np.mean(~np.isfinite(g)))
    lo, hi = np.nanpercentile(g, [5, 95])
    return dict(est=vx - vy, lo=lo, hi=hi, cens=cens, flags=(fx, fy))


def r_boot(cols, B=2000, seed=20260926):
    rng = np.random.default_rng(seed)
    n = len(cols[0][0])
    out = np.empty(B)
    for i in range(B):
        idx = rng.integers(0, n, n)
        bs = sum(b[idx].sum() for b, _, _ in cols)
        vs = sum(v[idx].sum() for _, v, _ in cols)
        gs = sum(g[idx].sum() for _, _, g in cols)
        out[i] = (bs - vs) / (bs - gs) if bs - gs > 0 else np.nan
    ok = np.isfinite(out)
    return (np.percentile(out[ok], [5, 95]) if ok.sum() else (np.nan, np.nan)), int((~ok).sum())


# ----------------------------------------------------------------------------- loading + acceptance ② / ③
def load_run(T, cfg):
    pat = re.compile(rf"^D2_C2_{cfg['prior']}_Nr8_T16_Tp4_{cfg['pil']}_snr(-?\d+)_skip(\d+)_n(\d+)\.npz$")
    files = sorted(glob.glob(f"{CONF}/raw_{T}/D2_*.npz"))
    allfiles = sorted(os.listdir(f"{CONF}/raw_{T}"))
    plan, issues = {}, []
    for f in files:
        m = pat.match(os.path.basename(f))
        if not m:
            issues.append(f"unexpected file name {os.path.basename(f)}")
            continue
        plan.setdefault(int(m[1]), []).append((int(m[2]), int(m[3]), f))
    print(f"  files in raw_{T}: {len(allfiles)} (npz matching the run pattern: {len(files)})")
    if sorted(plan) != cfg["grid"]:
        issues.append(f"SNR set {sorted(plan)} != registered {cfg['grid']}")
    for s, ch in plan.items():
        sk = sorted(k for k, _, _ in ch)
        if sk != list(range(0, N, CH)) or any(n != CH for _, n, _ in ch) or len(ch) != N // CH:
            issues.append(f"snr {s}: chunk plan broken: {len(ch)} chunks, skips {sk[:4]}.., n {sorted({n for _, n, _ in ch})}")
    be = {}                                   # snr -> arm -> (2560, 16) blk_err
    meta = {}                                 # key -> {value: count}
    failed_keys, nonfinite, bad_shape, vals = 0, 0, [], set()
    ref_chunks, ref_arrays, ref_diff, ref_only = 0, 0, [], {}
    ref_keys_seen = set()
    for s in sorted(plan):
        parts = {a: [] for a in ARMS6}
        for skip, n, f in sorted(plan[s]):
            z = np.load(f)
            keys = set(z.files)
            failed_keys += sum(1 for k in keys if k.endswith("|failed"))
            for a in ARMS6:
                for k in KEYS_RAW:
                    v = z[f"{a}|{k}"]
                    if v.shape != (CH, 16):
                        bad_shape.append(f"{os.path.basename(f)} {a}|{k} {v.shape}")
                v = z[f"{a}|blk_err"]
                nonfinite += int((~np.isfinite(v.astype(float))).sum())
                vals |= set(np.unique(v).tolist())
                parts[a].append(v)
            for k in keys:
                if k.startswith("meta|") or k.startswith("run|"):
                    v = z[k]
                    if v.ndim == 0:
                        meta.setdefault(k, {})
                        sv = repr(v.item()) if v.dtype.kind in "iufb" else str(v)
                        meta[k][sv] = meta[k].get(sv, 0) + 1
            # acceptance ③ (superset: every key with the arm prefix, both files' key sets)
            r = os.path.join(CONF, cfg["ref"], os.path.basename(f))
            if os.path.exists(r):
                y = np.load(r)
                ref_chunks += 1
                for a in (V1, BS, G):
                    kz = {k for k in z.files if k.startswith(a + "|")}
                    ky = {k for k in y.files if k.startswith(a + "|")}
                    for k in kz ^ ky:
                        ref_only[k] = ref_only.get(k, 0) + 1
                    for k in kz & ky:
                        ref_keys_seen.add(k.split("|", 1)[1])
                        ref_arrays += 1
                        if not np.array_equal(z[k], y[k], equal_nan=True):
                            ref_diff.append(f"{os.path.basename(f)} {k}")
        for a in ARMS6:
            be[s] = be.get(s, {})
            be[s][a] = np.concatenate(parts[a])
            if len(be[s][a]) != N:
                issues.append(f"snr {s} {a}: n = {len(be[s][a])}")
    print(f"  chunk plan: {len(files)} chunks = {len(plan)} SNR x {N // CH}; issues: {issues if issues else 'none'}")
    tally(not issues, f"{T} chunk plan")
    print(f"  '|failed' keys: {failed_keys}; non-finite blk_err entries: {nonfinite}; blk_err values: {sorted(vals)}; bad shapes: {len(bad_shape)}")
    tally(failed_keys == 0 and nonfinite == 0 and not bad_shape and vals <= {0, 1}, f"{T} raised/shape/values")
    # acceptance ② meta
    def one(k):
        d = meta.get(k, {})
        return (next(iter(d)) if len(d) == 1 else f"MULTIPLE {d}") if d else "ABSENT"
    chunks = len(files)
    checks = {
        "run|git": (one("run|git"), RUN_GIT, sum(meta.get("run|git", {}).values()) == chunks),
        "meta|modulation": (one("meta|modulation"), cfg["mod"], None),
        "meta|lowsig_arms present": (str(sum(meta.get("meta|lowsig_arms", {}).values())), str(chunks), None),
        "meta|lowsig_s_lo": (one("meta|lowsig_s_lo"), cfg["slo"], None),
        "meta|wide_sigma_tag": (one("meta|wide_sigma_tag"), cfg["wtag"], None),
        "meta|wide_ckpt_id (prefix)": (one("meta|wide_ckpt_id")[:len(f"sha256[:16]={cfg['wsha']} {cfg['wep']} 8x4")],
                                       f"sha256[:16]={cfg['wsha']} {cfg['wep']} 8x4", None),
        "meta|wide_ckpt_id (full, distinct)": (one("meta|wide_ckpt_id"), one("meta|wide_ckpt_id"), None),
        "meta|stagec_ckpt_id (prefix)": (one("meta|stagec_ckpt_id")[:len(f"sha256[:16]={cfg['v1sha']} {cfg['v1ep']} 8x4")],
                                         f"sha256[:16]={cfg['v1sha']} {cfg['v1ep']} 8x4", None),
        "meta|kron_K": (one("meta|kron_K"), repr(cfg["K"]), None),
        "meta|bstar": (one("meta|bstar"), "kron", None),
        "meta|ntrain": (one("meta|ntrain"), repr(160000.0), None),
        "meta|jobs": (one("meta|jobs"), "96", None),
        "meta|worker_gb": (one("meta|worker_gb"), "1.5", None),
        "run|n": (one("run|n"), "40", None), "run|iters": (one("run|iters"), "16", None),
        "run|seed": (one("run|seed"), "20260926", None), "run|dtype": (one("run|dtype"), "complex128/float64", None),
    }
    llk = meta.get("meta|ll_val|kron", {})
    llok = len(llk) == 1 and abs(float(next(iter(llk))) - cfg["ll"]) <= 1e-9
    checks["meta|ll_val|kron (|d|<=1e-9)"] = (one("meta|ll_val|kron"), repr(cfg["ll"]), llok)
    if cfg["mod"] == "16qam":
        checks["meta|payload_bits"] = (one("meta|payload_bits"), "90", None)
        checks["meta|protocol"] = (one("meta|protocol"), "E5-qam16-v1", None)
    else:
        checks["meta|modulation"] = (one("meta|modulation"), "qpsk", None)       # absent would be read as qpsk; here it is present?
    print("  acceptance ② (every chunk, distinct values):")
    for k, (got, want, ok) in checks.items():
        ok = (got == want) if ok is None else (ok and got == want)
        if k == "meta|modulation" and cfg["mod"] == "qpsk" and got == "ABSENT":
            ok = True                                              # §1.3: absent = qpsk
        tally(ok, f"{T} {k}: got {got!r} want {want!r}")
        print(f"    {'OK ' if ok else 'BAD'} {k}: {got}" + ("" if ok else f"   (want {want})"))
    print(f"  acceptance ③ vs {cfg['ref']}: {ref_chunks} chunks (want 448), {ref_arrays} arrays of V1/b*/genie compared over keys "
          f"{sorted(ref_keys_seen)}, differing {len(ref_diff)}, keys present in only one file: {ref_only if ref_only else 'none'}")
    for d in ref_diff[:10]:
        print("     DIFF", d)
    tally(ref_chunks == 448 and not ref_diff, f"{T} acceptance ③")
    return be


# ----------------------------------------------------------------------------- compare_<T>.txt parsing
def blocks(txt):
    """split the committed compare file into named blocks (header line -> list of lines)."""
    out, cur = {}, None
    for line in txt.splitlines():
        m = re.match(r"^######## (.*) ########$", line)
        if m:
            cur = m[1]
            out[cur] = []
        elif cur is not None:
            out[cur].append(line)
    return out


def check_line(blines, line, what):
    ok = line in blines
    tally(ok, what + " :: " + line.strip())
    return ok


def fmt_p(p):
    return f"{p:.2g}"


def analyse(T, cfg, be):
    grid = cfg["grid"]
    F = {a: {s: int((be[s][a][:, -1] != 0).sum()) for s in grid} for a in ARMS6}
    last = {s: {a: be[s][a][:, -1] for a in ARMS6} for s in grid}
    txt = open(f"{RN}/v1ls/compare_{T}.txt").read()
    bl = blocks(txt)
    primary_lines = bl[f"PRIMARY ({C_})"]
    print(f"  failures @16 / 2560 per SNR (recomputed):")
    print("    SNR  " + "".join(f"{a.replace('M-ours-dscore-C-', ''):>14}" for a in ARMS6))
    table_block = [l for l in txt.splitlines()]
    for s in grid:
        row = f"  {s:+3.0f}   " + "".join(f"{F[a][s]:>14d}" for a in ARMS6)
        print("  " + row.strip() if False else "    " + f"{s:+3d}  " + "".join(f"{F[a][s]:>14d}" for a in ARMS6))
        check_line(table_block, row, f"{T} BLER table {s:+d} dB")
    res_all = {}
    for X in VARS:
        lines = primary_lines if X == C_ else bl[f"report only: {X}"]
        name = "PRIMARY" if X == C_ else "report-only"
        # ---- L1
        r = {s: paired(last[s][V1], last[s][X]) for s in HIGH}
        xf = [r[s][0] > r[s][1] and r[s][2] < 0.05 for s in HIGH]
        vf = [r[s][1] > r[s][0] and r[s][2] < 0.05 for s in HIGH]
        l1 = "(a) X fewer at both points" if all(xf) else "(c) V1 fewer at a point" if any(vf) else "(b) not decided"
        l1_line = "    " + "  ".join(f"{s:+.0f} dB {r[s][0]}:{r[s][1]} p={fmt_p(r[s][2])}" for s in HIGH) + f"   -> {l1}"
        f3 = {s: F[X][s] for s in (15,) + HIGH}
        mono = f3[18] <= f3[15] and f3[21] <= f3[18]
        mono_line = (f"    MONOTONE (failures of {X} at +15 / +18 / +21 dB = {f3[15]} / {f3[18]} / {f3[21]} of 2560): "
                     + ("yes" if mono else "no"))
        for s in HIGH:                                      # scipy cross-check of the exact p
            tally(abs(sign_p_scipy(*r[s][:2]) - r[s][2]) <= 1e-9 * max(r[s][2], 1e-300) or (r[s][2] == 0 and sign_p_scipy(*r[s][:2]) == 0),
                  f"{T} {X} L1 p scipy cross-check {s}")
        # ---- L2
        cand = decision_points(F[BS], grid)
        rr = [paired(last[s][BS], last[s][X]) for s in cand]
        A, B = sum(x[0] for x in rr), sum(x[1] for x in rr)
        powered = len(cand) == 3 and sum(1 for a, b, _ in rr if a + b >= 6) >= 2
        wy = sum(1 for a, b, p in rr if a > b and p < 0.05)
        wx = sum(1 for a, b, p in rr if b > a and p < 0.05)
        l2 = ("(i)" if wy >= 2 else "(ii)" if wx >= 2 else "(iii)") if powered else "(iv)"
        dec_line = f"    decision SNRs {[f'{s:+.0f}' for s in cand]}"
        st_line = ("    sign test @16: " + "  ".join(f"{s:+.0f} dB {a}:{b} p={fmt_p(p)}" for (a, b, p), s in zip(rr, cand))
                   + f"   pooled {A}:{B} p={fmt_p(sign_p(A, B))}")
        pg_line = (f"    power guard: POWERED; second arm fewer failures at {wy}/{len(cand)} points, first arm fewer failures at "
                   f"{wx}/{len(cand)} points -> " + ("significant" if max(wx, wy) >= 2 else "not significant")) if powered else \
                  f"    power guard: {len(cand)} decision points (needs 3), discordant-pair counts {[a + b for a, b, _ in rr]} -> UNDECIDED"
        for (a, b, p), s in zip(rr, cand):
            tally(abs(sign_p_scipy(a, b) - p) <= 1e-9 * max(p, 1e-300), f"{T} {X} L2 p scipy cross-check {s}")
        gp = gap([last[s][BS] for s in grid], [last[s][X] for s in grid], grid)
        gap_line = (f"    SNR@0.1 gap ({BS} minus {X}): {gp['est']:+.2f} dB  [90% paired bootstrap {gp['lo']:+.2f}, {gp['hi']:+.2f}; "
                    f"censored replicates {100 * gp['cens']:.0f}%]   -> label {l2}")
        cols = [tuple(np.where(np.isfinite(last[s][a].astype(float)), last[s][a], 1.0).astype(float) for a in (BS, X, G)) for s in cand]
        Fs = [int(sum(c[i].sum() for c in cols)) for i in range(3)]
        (lo, hi), nn = r_boot(cols)
        R = (Fs[0] - Fs[1]) / (Fs[0] - Fs[2]) if Fs[0] > Fs[2] else float("nan")
        sf_line = (f"    decision points: sum F  b* {Fs[0]}  X {Fs[1]}  genie {Fs[2]}   R = {R:.6f}  [90% paired bootstrap B=2000 seed 20260926: "
                   f"{lo:.3f}, {hi:.3f}]" + (f"  ({nn} replicates undefined)" if nn else ""))
        # ---- SUFFIX
        suf, seen = [], set()
        if l2 == "(i)":
            for (a, b, p), s in zip(rr, cand):
                if b > a and p < 0.05:
                    suf.append(f"{s:+.0f} dB 에서는 {BS} 가 적게 실패: {a}:{b}, p = {fmt_p(p)}")
                    seen.add(s)
        elif l2 == "(ii)":
            suf += [f"{s:+.0f} dB 에서는 {X} 가 적게 실패: {a}:{b}, p = {fmt_p(p)}" for (a, b, p), s in zip(rr, cand) if a > b and p < 0.05]
        hi_bx = {}
        for s in HIGH:
            a, b, p = paired(last[s][BS], last[s][X])
            hi_bx[s] = (a, b, p)
            if b > a and p < 0.05 and l2 != "(ii)" and s not in seen:
                suf.append(f"{s:+.0f} dB 에서는 {BS} 가 적게 실패: {a}:{b}, p = {fmt_p(p)}")
        suf_line = "    SUFFIX (§2.1 M3): " + ("; ".join(f"(단 {t})" for t in suf) if suf else "none")
        print(f"  [{name}] {X}")
        print("    L1 " + l1_line.strip())
        print("    " + mono_line.strip())
        print("    L2 " + dec_line.strip() + " | " + st_line.strip())
        print("    " + pg_line.strip())
        print("    " + gap_line.strip() + f"   (flags {gp['flags']})")
        print("    " + sf_line.strip())
        print("    " + suf_line.strip())
        for line, what in ((l1_line, "L1"), (mono_line, "MONOTONE"), (dec_line, "decision SNRs"), (st_line, "sign test"),
                           (pg_line, "power guard"), (gap_line, "gap"), (sf_line, "sum F / R"), (suf_line, "SUFFIX")):
            check_line(lines, line, f"{T} {X} {what}")
        if X == C_:
            pl = f"  PRIMARY LABELS: L1 {l1} (monotone {'yes' if mono else 'no'})   L2 {l2} (suffixes {len(suf)})"
            check_line(lines, pl, f"{T} PRIMARY LABELS")
            print("    " + pl.strip())
        res_all[X] = dict(l1=l1, mono=mono, l2=l2, cand=cand, gap=gp, F=Fs, R=R, ci=(lo, hi), suf=suf, hi_bx=hi_bx, r=r, rr=rr, AB=(A, B))
    # ---- report only: V1 -> C at the other grid points, pooled <= +15
    low = [s for s in grid if s not in HIGH]
    ob = bl[f"report only: V1 -> {C_} at the other grid points (a = only V1 fails : b = only X fails)"]
    rl = [paired(last[s][V1], last[s][C_]) for s in low]
    for (a, b, p), s in zip(rl, low):
        check_line(ob, f"  {s:+3.0f} dB  {a}:{b}  p={fmt_p(p)}", f"{T} V1->C other point {s:+d}")
    A15, B15 = sum(x[0] for x in rl), sum(x[1] for x in rl)
    check_line(ob, f"  pooled over the points <= +15 dB: {A15}:{B15}  p={fmt_p(sign_p(A15, B15))}", f"{T} V1->C pooled <=15")
    print(f"  V1 -> C other points: " + "  ".join(f"{s:+d} {a}:{b} p={fmt_p(p)}" for (a, b, p), s in zip(rl, low))
          + f"; pooled <= +15 dB {A15}:{B15} p={fmt_p(sign_p(A15, B15))}")
    hb = bl[f"report only: {BS} -> {C_} at +18 / +21 dB"]
    for s in HIGH:
        a, b, p = res_all[C_]["hi_bx"][s]
        check_line(hb, f"  {s:+3.0f} dB  {a}:{b}  p={fmt_p(p)}", f"{T} b*->C {s:+d}")
    print(f"  b* -> C at +18 / +21: " + "  ".join(f"{s:+d} {res_all[C_]['hi_bx'][s][0]}:{res_all[C_]['hi_bx'][s][1]} p={fmt_p(res_all[C_]['hi_bx'][s][2])}" for s in HIGH))
    # ---- §6.5 predictions 4 and 5 (and §6.2 note on the largest decision-point p)
    v1le = sum(F[V1][s] for s in grid if s <= 15)
    cle = sum(F[C_][s] for s in grid if s <= 15)
    lim = v1le + 2 * math.sqrt(v1le)
    print(f"  prediction 5: C <= +15 dB sum {cle} vs V1 {v1le} (limit {lim:.1f}) -> {'ok' if cle <= lim else 'VIOLATED'}")
    if cfg["mod"] == "qpsk":
        print(f"  prediction 4: V1 vs b* at +18 / +21: {F[V1][18]} vs {F[BS][18]}, {F[V1][21]} vs {F[BS][21]} -> "
              f"{'ok' if F[V1][18] > F[BS][18] and F[V1][21] > F[BS][21] else 'VIOLATED'}")
    pmax = max(p for _, _, p in res_all[C_]["rr"])
    print(f"  largest decision-point p (PRIMARY): {pmax:.4g}; sign_p(53,27) = {sign_p(53, 27):.4g}")
    return F, res_all, dict(cle=cle, v1le=v1le, lim=lim)


# ----------------------------------------------------------------------------- lowsig selection rule re-applied
def selection():
    L = os.path.join(RN, "lowsig")
    PTS = [(c, m, s) for c in ("U28", "D2") for m in ("qpsk", "16qam") for s in (15, 18, 21)]
    SK = {"16qam": 5120, "qpsk": 6000}
    Fc = lambda be: int((np.asarray(be)[:, 15] != 0).sum())
    print("\n==== lowsig/SELECTION_RULE.md re-applied from the development screens (npz) ====")
    for cset, out in (("", "select_lowsig.out"), ("d", "select_lowsig_d.out")):
        M = {k: 0 for k in ("V1", "b*", "A", "B", "C")}
        M15 = {k: 0 for k in ("V1", "A", "B", "C")}
        per = {}
        pair = {k: [0, 0] for k in ("A:C", "B:C", "b*:C", "V1:C")}
        pair15 = {k: [0, 0] for k in pair}
        pairhi = {k: [0, 0] for k in pair}
        p7 = {}
        for c, m, s in PTS:
            z = np.load(f"{L}/screen_{c}_{m}_{SK[m]}_320_snr{s}.npz")
            zc = np.load(f"{L}/screenC{cset}_{c}_{m}_{SK[m]}_320_snr{s}.npz")
            arr = {"V1": z[f"{s}|V1|blk_err"], "b*": z[f"{s}|b*|blk_err"], "A": z[f"{s}|V1-clamp|blk_err"], "B": z[f"{s}|V1-gmmfb|blk_err"],
                   "C": zc["blk_err"]}
            assert all(len(v) == 320 for v in arr.values())
            f = {k: Fc(v) for k, v in arr.items()}
            per[(c, m, s)] = f
            for k, v in f.items():
                M[k] += v
                if s == 15 and k in M15:
                    M15[k] += v
            for k in pair:
                x = arr[k.split(":")[0]][:, 15]
                y = arr["C"][:, 15]
                a, b = int(np.sum((x != 0) & (y == 0))), int(np.sum((x == 0) & (y != 0)))
                for dct, cond in ((pair, True), (pair15, s == 15), (pairhi, s in (18, 21))):
                    if cond:
                        dct[k][0] += a
                        dct[k][1] += b
                if k == "b*:C":
                    p7[(c, m, s)] = (a, b, sign_p(a, b))
        lim = M15["V1"] + 2 * math.sqrt(M15["V1"])
        ok = [k for k in ("A", "B", "C") if M15[k] <= lim]
        best = min(ok, key=lambda k: (M[k], "ABC".index(k)))
        rows = [f"{c} {m} {s:+d}: " + " ".join(f"{k} {v}" for k, v in f.items()) for (c, m, s), f in per.items()]
        print(f"  [{out}] per point: " + " | ".join(rows))
        print(f"  [{out}] M: " + "  ".join(f"{k} {v}" for k, v in M.items()) + f";  no-harm +15: V1 {M15['V1']} limit {lim:.2f}: "
              + "  ".join(f"{k} {M15[k]} {'pass' if k in ok else 'FAIL'}" for k in ("A", "B", "C")) + f"  -> PRIMARY = {best}")
        # compare with the committed .out file
        committed = open(f"{L}/{out}").read()
        mline = "M (12 points / 3840 blocks): " + "  ".join(f"{k} {v}" for k, v in M.items())
        nline = f"no-harm at +15 dB: V1 {M15['V1']}, limit {lim:.2f}; " + "  ".join(f"{k} {M15[k]} {'pass' if k in ok else 'FAIL'}" for k in ("A", "B", "C"))
        tally(mline in committed, f"{out} M line :: {mline}")
        tally(nline in committed, f"{out} no-harm line :: {nline}")
        tally(f"PRIMARY = {best}" in committed, f"{out} PRIMARY")
        for (c, m, s), f in per.items():
            row = f"{c:3s} {m:5s} {s:+3d} dB  " + "  ".join(f"{k} {v:3d}" for k, v in f.items())
            tally(row in committed, f"{out} row {c} {m} {s}")
        print(f"  [{out}] paired a:b (a = first arm only fails : b = C only fails), 12 points: "
              + "  ".join(f"{k} {v[0]}:{v[1]} (p {fmt_p(sign_p(*v))})" for k, v in pair.items())
              + " | +15 only: " + "  ".join(f"{k} {v[0]}:{v[1]}" for k, v in pair15.items())
              + " | +18/+21 only: " + "  ".join(f"{k} {v[0]}:{v[1]} (p {fmt_p(sign_p(*v))})" for k, v in pairhi.items()))
        if cset == "d":
            print("  prediction-7 table (b*:C per point, p): " + "  ".join(f"{c} {m} {s:+d} {a}:{b} (p {fmt_p(p)})" for (c, m, s), (a, b, p) in p7.items()))
            print("  C +15/+18/+21 failures per run: " + "  ".join(f"{c} {m} {per[(c, m, 15)]['C']}/{per[(c, m, 18)]['C']}/{per[(c, m, 21)]['C']}"
                                                                    for c in ("U28", "D2") for m in ("qpsk", "16qam")))
            # M4
            M4 = {("U28", "qpsk"): (3, 6, 9), ("D2", "qpsk"): (-3, 0, 3), ("U28", "16qam"): (12,), ("D2", "16qam"): (9, 12)}
            for (c, m), ss in M4.items():
                tot = {k: 0 for k in ("V1", "b*", "A", "B", "C")}
                pv = [0, 0]
                pb = [0, 0]
                for s in ss:
                    z = np.load(f"{L}/screen_{c}_{m}_{SK[m]}_320_snr{s:g}.npz")
                    zc = np.load(f"{L}/screenCd_{c}_{m}_{SK[m]}_320_snr{s:g}.npz")
                    arr = {"V1": z[f"{float(s):g}|V1|blk_err"], "b*": z[f"{float(s):g}|b*|blk_err"], "A": z[f"{float(s):g}|V1-clamp|blk_err"],
                           "B": z[f"{float(s):g}|V1-gmmfb|blk_err"], "C": zc["blk_err"]}
                    assert all(len(v) == 320 for v in arr.values())
                    for k, v in arr.items():
                        tot[k] += Fc(v)
                    y = arr["C"][:, 15]
                    for key, dst in (("V1", pv), ("b*", pb)):
                        x = arr[key][:, 15]
                        dst[0] += int(np.sum((x != 0) & (y == 0)))
                        dst[1] += int(np.sum((x == 0) & (y != 0)))
                lim4 = tot["V1"] + 2 * math.sqrt(tot["V1"])
                line = (f"  {c:3s} {m:5s} SNR {ss}: " + "  ".join(f"{k} {v}" for k, v in tot.items())
                        + f"   PRIMARY {best} {tot[best]} vs limit {lim4:.2f} -> " + ("ok" if tot[best] <= lim4 else "VIOLATION (to the user)"))
                tally(line in committed, f"{out} M4 {c} {m} :: {line.strip()}")
                print("  M4 " + line.strip() + f"   paired V1:C {pv[0]}:{pv[1]}  b*:C {pb[0]}:{pb[1]}")
    # grid keys of the new-C screens
    gs = {}
    for f in sorted(glob.glob(f"{L}/screenCd_*_snr18.npz")):
        gs[os.path.basename(f)] = np.load(f)["grid"].tolist()
    print("  screenCd grid key (s_lo, s_hi) at +18 dB: " + "; ".join(f"{k}: {v}" for k, v in gs.items()))


def main():
    print(f"# recompute_v1ls.py -- numpy {np.__version__}; raw read from {CONF}/raw_<T>; compare files from {RN}/v1ls")
    summary = {}
    for T, cfg in RUNS:
        print(f"\n==== {T} ({cfg['prior']} {cfg['mod']}, grid {cfg['grid']}, reference {cfg['ref']}) ====")
        be = load_run(T, cfg)
        F, res, p5 = analyse(T, cfg, be)
        summary[T] = (F, res, p5)
    selection()
    print("\n==== §6.2 table, recomputed (PRIMARY = C) ====")
    for T, (F, res, p5) in summary.items():
        r = res[C_]
        print(f"  {T}: L1 {' · '.join(f'{r['r'][s][0]}:{r['r'][s][1]}' for s in HIGH)} {r['l1'][:3]} | MONOTONE {'yes' if r['mono'] else 'no'} "
              f"({F[C_][15]} / {F[C_][18]} / {F[C_][21]}) | decision {r['cand']} | b*->C "
              f"{' · '.join(f'{a}:{b}' for a, b, _ in r['rr'])}; {r['AB'][0]}:{r['AB'][1]} | L2 {r['l2']} | gap {r['gap']['est']:+.2f} "
              f"[{r['gap']['lo']:+.2f}, {r['gap']['hi']:+.2f}] | sum F {r['F'][0]} / {r['F'][1]} / {r['F'][2]} | R {r['R']:.3f} "
              f"[{r['ci'][0]:.3f}, {r['ci'][1]:.3f}] | SUFFIX {'none' if not r['suf'] else r['suf']} | pred5 {p5['cle']} vs {p5['v1le']} ({p5['lim']:.1f})")
    print("\n==== §6.4 / §6.7 report-only (A, B) ====")
    for T, (F, res, p5) in summary.items():
        for X in (A_, B_):
            r = res[X]
            print(f"  {T} {X.replace('M-ours-dscore-C-', '')}: L1 {r['l1'][:3]} MONOTONE {'yes' if r['mono'] else 'no'} "
                  f"({F[X][15]} / {F[X][18]} / {F[X][21]}) | L2 {r['l2']} gap {r['gap']['est']:+.2f} [{r['gap']['lo']:+.2f}, {r['gap']['hi']:+.2f}] "
                  f"| sum F {r['F'][0]} / {r['F'][1]} / {r['F'][2]} R {r['R']:.3f} [{r['ci'][0]:.3f}, {r['ci'][1]:.3f}] | SUFFIX {'none' if not r['suf'] else r['suf']}")
    print(f"\n==== TALLY: {TOT['match']} checks matched, {TOT['mismatch']} mismatched ====")
    for m in MIS:
        print("  MISMATCH:", m)


if __name__ == "__main__":
    main()
