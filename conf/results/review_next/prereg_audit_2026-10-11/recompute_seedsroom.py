"""Independent re-derivation for the SEEDSROOM16e4 record audit (Fable 5.1 subagent): NEXT_EXPERIMENTS_SEEDSROOM16e4.md
§0 (a1 rows), §5 (checkpoints, GB' addendum lines), §6.1 (four seed tags + the two a1 rows).

Reads ONLY raw npz chunks (own numpy reader -- no analysis.load_raw, no table code, no recovery_ci.py, no eval_accept.py),
checkpoints, GB' npz files.  Statistics re-implemented from their written definitions:
  decision points  : anchor b*, BLER@16 in [0.005, 0.9], three smallest |log10(BLER/0.1)|            (08_SPEC §2)
  sign test        : exact two-sided, min(1, 2 * sum_{i<=min(a,b)} C(n,i) / 2^n); scipy binomtest as a second opinion
  POWERED          : 3 decision points and >= 6 discordant pairs at >= 2 of them; (i) = V1 significantly fewer at >= 2/3
  SNR@0.1 gap      : log-linear first downward crossing; paired bootstrap B = 2000, default_rng(20260925), 5 / 95 percentiles
  recovery R       : (b* - V1)/(b* - genie); paired bootstrap B = 2000, default_rng(20260926)
The bootstraps use the registered seeds, so digit-level agreement is a reproduction, not an independent sample.
Every expected value below (EXP) was retyped from the record under audit.  With --xcheck the own reader is also compared with
analysis.load_raw (cross-check only).

    CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=8 ~/miniforge3/envs/torch/bin/python -B recompute_seedsroom.py [--xcheck] > recompute_seedsroom.out
"""
import glob
import hashlib
import math
import os
import re
import sys

import numpy as np
from scipy.stats import binomtest

CONF = "/home/HTJ/t2/conf"
KEYS_RAW = ("blk_err", "ber", "nmse", "tauL_gmean", "alphaD", "tauL_clip_frac", "alphaD_clip")
BSTAR, V1, V0, GENIE = "M-ours-bstar", "M-ours-dscore-C-V1", "M-ours-dscore-C-V0", "R5-genie"
STAGEC = {"M-ours-dscore-C-V0", "M-ours-dscore-C-V1", "M-ours-dscore-C-V4", "M-ours-dscore-C-V4b"}
PAT = re.compile(r"^D2_C2_(SRB|SRP)_Nr8_T16_Tp4_dft_snr(-?\d+)_skip(\d+)_n(\d+)\.npz$")
SNRS = [-3, 0, 3, 6, 9, 12, 15]
RUN_GIT = "62c24e7e"
NB = 2000
MIS = []
NCHK = [0]


def P(*a):
    print(*a, flush=True)


def chk(what, got, exp):
    NCHK[0] += 1
    ok = got == exp
    if not ok:
        MIS.append((what, got, exp))
    return "ok" if ok else f"MISMATCH (record {exp!r})"


def sha16(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()[:16]


def read(tag):
    """-> {snr: {"plan": [(skip, n)], "arr": {"arm|field": array}}, "meta": {key: set(values)}, "nfiles": n}"""
    pts, meta, nf = {}, {}, 0
    for f in sorted(glob.glob(f"{CONF}/raw_{tag}/*")):
        m = PAT.match(os.path.basename(f))
        assert m, f
        nf += 1
        with np.load(f) as z:
            d = {k: z[k] for k in z.files}
        assert int(d["run|skip"]) == int(m[3]) and int(d["run|n"]) == int(m[4]) and float(d["run|snr"]) == float(m[2]), f
        bs = str(d["meta|bstar"])
        for k in ("run|git", "run|iters", "run|seed", "run|dtype", "run|beta", "run|t_in", "meta|ntrain", "meta|bstar", "meta|kron_K",
                  f"meta|ll_val|{bs}", "meta|stagec_ckpt", "meta|stagec_ckpt_id"):
            meta.setdefault(k.replace(f"|{bs}", "|<bstar>") if k.startswith("meta|ll_val") else k, set()).add(d[k].item() if k in d else None)
        pts.setdefault(int(m[2]), []).append((int(m[3]), int(m[4]), {k: v for k, v in d.items() if not k.startswith(("meta|", "run|"))}))
    out = {"meta": meta, "nfiles": nf}
    for s, ch in pts.items():
        ch.sort(key=lambda c: c[0])
        keys = list(ch[0][2])
        assert all(list(c[2]) == keys for c in ch), (tag, s, "key sets differ between chunks")
        out[s] = {"plan": [(c[0], c[1]) for c in ch], "arr": {k: np.concatenate([c[2][k] for c in ch], axis=0) for k in keys}}
    return out


def fails(d, s, arm):
    v = d[s]["arr"][f"{arm}|blk_err"][:, -1].astype(float)
    return np.where(np.isfinite(v), v, 1.0)


def sign_p(a, b):
    n = a + b
    return 1.0 if n == 0 else min(1.0, 2 * sum(math.comb(n, i) for i in range(min(a, b) + 1)) / 2 ** n)


def snr_at(snrs, bl, n, target=0.1):
    lb = np.log10(np.maximum(np.asarray(bl, float), 0.5 / n)); lt = np.log10(target)
    if lb[0] <= lt:
        return snrs[0], "lo"
    for i in range(len(snrs) - 1):
        if lb[i] > lt >= lb[i + 1]:
            return snrs[i] + (lb[i] - lt) / (lb[i] - lb[i + 1]) * (snrs[i + 1] - snrs[i]), "ok"
    return snrs[-1], "hi"


def gap(d, x, y, seed=20260925):
    ex = [fails(d, s, x) for s in SNRS]; ey = [fails(d, s, y) for s in SNRS]; n = min(len(e) for e in ex)
    (vx, fx), (vy, fy) = snr_at(SNRS, [e.mean() for e in ex], n), snr_at(SNRS, [e.mean() for e in ey], n)
    assert fx == fy == "ok", (fx, fy)
    rng = np.random.default_rng(seed); g = []
    for _ in range(NB):
        bx, by = [], []
        for a, b in zip(ex, ey):
            i = rng.integers(len(a), size=len(a)); bx.append(a[i].mean()); by.append(b[i].mean())
        (ux, gx), (uy, gy) = snr_at(SNRS, bx, n), snr_at(SNRS, by, n); g.append(ux - uy if gx == gy == "ok" else np.nan)
    g = np.array(g); lo, hi = np.nanpercentile(g, [5, 95])
    return vx - vy, lo, hi, float(np.mean(~np.isfinite(g))), vx, vy


def recov(d, snrs, seed=20260926):
    cols = [(fails(d, s, BSTAR), fails(d, s, V1), fails(d, s, GENIE)) for s in snrs]
    b, v, g = (sum(c[i].sum() for c in cols) for i in range(3))
    rng = np.random.default_rng(seed); n = len(cols[0][0]); out = np.empty(NB)
    for i in range(NB):
        idx = rng.integers(0, n, n)
        bs, vs, gs = (sum(c[j][idx].sum() for c in cols) for j in range(3))
        out[i] = (bs - vs) / (bs - gs) if bs - gs > 0 else np.nan
    ok = np.isfinite(out); lo, hi = np.percentile(out[ok], [5, 95])
    return int(b), int(v), int(g), (b - v) / (b - g), lo, hi, int((~ok).sum())


def wilson(k, n, z):
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def eq(x, y):
    x, y = np.asarray(x), np.asarray(y)
    return x.shape == y.shape and x.dtype == y.dtype and (np.array_equal(x, y, equal_nan=True) if x.dtype.kind == "f" else np.array_equal(x, y))


# ------------------------------------------------------------------ expected values, retyped from the record (§0, §5, §6.1)
EXP = {
    "SRBB16e4":   dict(tb="209:86 (5.6e-13) · 65:38 (0.01) · 28:5 (6.6e-05) · 302:129 (4.5e-17)", gap="+0.32 [+0.18, +0.45]", v1="0.275 (0.258, 0.293), 704/2560",
                       bg="827 · 299", r3="0.233 [0.187, 0.279]", rd="0.256 [0.212, 0.299]", bgbler="0.323 / 0.117"),
    "SRBB16e4s2": dict(tb="211:95 (2.9e-11) · 62:30 (0.0011) · 26:5 (0.00019) · 299:130 (2e-16)", gap="+0.35 [+0.22, +0.48]", v1="0.278 (0.261, 0.295), 711/2560",
                       bg="827 · 299", r3="0.220 [0.174, 0.268]", rd="0.250 [0.208, 0.293]", guard="2560   2560   1.000  8.632e+08"),
    "SRBB16e4s3": dict(tb="207:106 (1.2e-08) · 66:30 (0.00031) · 24:9 (0.014) · 297:145 (4e-13)", gap="+0.37 [+0.24, +0.51]", v1="0.284 (0.266, 0.301), 726/2560",
                       bg="827 · 299", r3="0.191 [0.141, 0.241]", rd="0.225 [0.178, 0.270]", guard="2559   2560   1.000  3.461e+10"),
    "SRPB16e4":   dict(tb="606:62 (4.3e-113) · 321:27 (5.2e-65) · 117:8 (5.9e-26) · 1044:97 (4.1e-201)", gap="+2.01 [+1.78, +2.24]", v1="0.317 (0.299, 0.335), 812/2560",
                       bg="1356 · 428", r3="0.586 [0.554, 0.618]", rd="0.644 [0.620, 0.667]", bgbler="0.530 / 0.167"),
    "SRPB16e4s2": dict(tb="591:64 (8.5e-108) · 307:18 (4.9e-69) · 112:6 (2.1e-26) · 1010:88 (3.6e-199)", gap="+1.95 [+1.73, +2.18]", v1="0.324 (0.306, 0.342), 829/2560",
                       bg="1356 · 428", r3="0.568 [0.536, 0.597]", rd="0.627 [0.603, 0.649]", guard="2560   2560   1.000  7.113e+10"),
    "SRPB16e4s3": dict(tb="603:67 (9.2e-109) · 325:18 (5.1e-74) · 115:8 (2.1e-25) · 1043:93 (6e-204)", gap="+2.12 [+1.90, +2.35]", v1="0.320 (0.303, 0.339), 820/2560",
                       bg="1356 · 428", r3="0.578 [0.544, 0.607]", rd="0.646 [0.622, 0.668]", guard="2560   2560   1.000  1.273e+11"),
}
META = {"SRB": dict(bstar="gmm1024", ll=97.00871495382869, kron_K=2048), "SRP": dict(bstar="kron", ll=244.1932863626755, kron_K=4096)}
CK = {  # §5: tag -> (ckpt stem, best sha, epoch, best_epoch, last epoch, last sha, best_val, rung, attempt, split_hash)
    "SRBB16e4s2": ("d2sx_SRB_N160000_a2", "2d3e7eae6bb20008", 1337, 1337, 1357, "acb7a0852e306929", 0.24751384556293488, "D2SXSRB160000", 2, "c009329584978bd9"),
    "SRBB16e4s3": ("d2sx_SRB_N160000_a3", "9f6a9d5042587ae5", 1499, 1499, 1519, "e4d44ff042e936df", 0.24783873558044434, "D2SXSRB160000", 3, "c009329584978bd9"),
    "SRPB16e4s2": ("d2sx_SRP_N160000_a2", "bdc0f5e854d2abbd", 744, 744, 764, "19b7aa5915c7d196", 0.14912495017051697, "D2SXSRP160000", 2, "27af93705c6dc289"),
    "SRPB16e4s3": ("d2sx_SRP_N160000_a3", "5db51008da6cc8df", 763, 763, 783, "0698a00b93de9ca5", 0.14876320958137512, "D2SXSRP160000", 3, "27af93705c6dc289"),
}
A1 = {"SRB": ("d2sx_SRB_N160000_a1", "ed437f21af15c305", 1660, 0.24769899249076843, "c009329584978bd9"),
      "SRP": ("d2sx_SRP_N160000_a1", "ac4699c78b3e2d80", 694, 0.1495504230260849, "27af93705c6dc289")}
GBP = {  # §5 addendum lines / §6.1: (median, min, max)
    ("SRB", 1): ("0.6472", "0.5949", "5.1046"), ("SRB", 2): ("0.6158", "0.5673", "1.0104"), ("SRB", 3): ("0.6174", "0.5698", "0.9967"),
    ("SRP", 1): ("0.5836", "0.4954", "0.9130"), ("SRP", 2): ("0.5860", "0.5008", "0.9740"), ("SRP", 3): ("0.5840", "0.4943", "0.9938"),
}


def main():
    P("# recompute_seedsroom.py -- SEEDSROOM16e4 record audit (own numpy reader; raw / ckpt / GB' npz only)")
    D, LAB, SUM = {}, {}, {}
    for pr in ("SRB", "SRP"):
        for t in (f"{pr}B16e4", f"{pr}B16e4s2", f"{pr}B16e4s3"):
            d = D[t] = read(t); seed_tag = t.endswith(("s2", "s3"))
            P(f"\n## raw_{t}: {d['nfiles']} files")
            # ---- chunk plan, arms, meta (acceptance)
            plan_ok = all(d[s]["plan"] == [(40 * k, 40) for k in range(64)] for s in SNRS) and sorted(k for k in d if isinstance(k, int)) == SNRS
            arms = sorted({k.split("|")[0] for k in d[-3]["arr"] if k.split("|")[1] in KEYS_RAW})
            shapes = {d[s]["arr"][f"{a}|{q}"].shape for s in SNRS for a in arms for q in KEYS_RAW}
            P(f"  chunk plan {{(40k, 40)}} k = 0..63 at each of 7 SNRs: {plan_ok} [{chk(t + ' plan', plan_ok, True)}]; arms {len(arms)} [{chk(t + ' arms', len(arms), 14)}]; "
              f"KEYS_RAW array shapes {shapes} [{chk(t + ' shapes', shapes, {(2560, 16)})}]; '|failed' keys: {sorted(k for k in d[-3]['arr'] if k.endswith('|failed')) or 'none'}")
            m = d["meta"]
            P("  meta (distinct values over all files): " + "; ".join(f"{k}={sorted(map(str, v))}" for k, v in m.items()))
            P(f"    ntrain 160000 [{chk(t + ' ntrain', m['meta|ntrain'], {160000.0})}] bstar [{chk(t + ' bstar', m['meta|bstar'], {META[pr]['bstar']})}] "
              f"ll_val [{chk(t + ' ll_val', m['meta|ll_val|<bstar>'], {META[pr]['ll']})}] kron_K [{chk(t + ' kron_K', m['meta|kron_K'], {META[pr]['kron_K']})}] "
              f"iters 16 [{chk(t + ' iters', m['run|iters'], {16})}]")
            if seed_tag:
                stem, sha, ep, bep = CK[t][:4]
                P(f"    run|git == {RUN_GIT} on every chunk, no +dirty [{chk(t + ' git', m['run|git'], {RUN_GIT})}]; stagec_ckpt_id "
                  f"[{chk(t + ' ckpt_id', m['meta|stagec_ckpt_id'], {f'sha256[:16]={sha} epoch={ep} best_epoch={bep} role=best 8x4'})}]; "
                  f"stagec_ckpt [{chk(t + ' ckpt path', m['meta|stagec_ckpt'], {f'{CONF}/ckpt/{stem}_best.pt'})}]")
                # ---- identity against the a1 raw: every key (KEYS_RAW and the extra per-arm keys), every point
                a1 = D[f"{pr}B16e4"]; diff_raw, diff_extra, miss = set(), set(), set()
                for s in SNRS:
                    ka, kb = set(d[s]["arr"]), set(a1[s]["arr"]); miss |= ka ^ kb
                    for k in ka & kb:
                        if not eq(d[s]["arr"][k], a1[s]["arr"][k]):
                            (diff_raw if k.split("|")[1] in KEYS_RAW else diff_extra).add(k.split("|")[0])
                per = {s: sorted({k.split("|")[0] for k in d[s]["arr"] if k in a1[s]["arr"] and k.split("|")[1] in KEYS_RAW and not eq(d[s]["arr"][k], a1[s]["arr"][k])}) for s in SNRS}
                nid = sum(1 for s in SNRS for a in arms if a not in STAGEC for q in KEYS_RAW if eq(d[s]["arr"][f"{a}|{q}"], a1[s]["arr"][f"{a}|{q}"]))
                P(f"  vs raw_{pr}B16e4: keys missing on one side {sorted(miss) or 'none'}; arms differing in any KEYS_RAW array: {sorted(diff_raw)} "
                  f"[{chk(t + ' differing == StageC', diff_raw, STAGEC)}]; same set at every point: {all(set(v) == STAGEC for v in per.values())}; "
                  f"non-Stage-C arrays bit-identical {nid}/{7 * 10 * 7} [{chk(t + ' identical arrays', nid, 490)}]; extra keys (guardH / clip / diverged / ...) differing arms: {sorted(diff_extra)} "
                  f"[{chk(t + ' extra keys subset StageC', diff_extra <= STAGEC, True)}]")
                v1d = [int((fails(d, s, V1) != fails(a1, s, V1)).sum()) for s in SNRS]
                P(f"    V1 @16 block outcomes differing from a1 per SNR (trials): {v1d} (V1 actually different [{chk(t + ' V1 differs', sum(v1d) > 0, True)}])")
            # ---- table B
            n = 2560
            bl = {s: max(fails(d, s, BSTAR).mean(), 0.5 / n) for s in SNRS}
            cand = sorted(sorted((s for s in SNRS if 0.005 <= bl[s] <= 0.9), key=lambda s: abs(np.log10(bl[s] / 0.1)))[:3])
            res = []
            for s in cand:
                fx, fy = fails(d, s, BSTAR), fails(d, s, V1)
                a, b = int(((fx == 1) & (fy == 0)).sum()), int(((fx == 0) & (fy == 1)).sum())
                p = sign_p(a, b); p2 = binomtest(min(a, b), a + b, 0.5).pvalue
                assert f"{p:.2g}" == f"{p2:.2g}", (p, p2)
                res.append((a, b, p))
            A, B = sum(r[0] for r in res), sum(r[1] for r in res); pp = sign_p(A, B)
            ndisc = sum(1 for a, b, _ in res if a + b >= 6); powered = len(cand) == 3 and ndisc >= 2
            wy = sum(1 for a, b, p in res if a > b and p < 0.05); wx = sum(1 for a, b, p in res if b > a and p < 0.05)
            lab = "(iv)" if not powered else "(i)" if wy >= 2 else "(ii)" if wx >= 2 else "(iii)"
            LAB[t] = lab
            tb = " · ".join(f"{a}:{b} ({p:.2g})" for a, b, p in res) + f" · {A}:{B} ({pp:.2g})"
            P("  b* BLER@16 per SNR: " + " ".join(f"{s:+d}:{fails(d, s, BSTAR).mean():.4f}" for s in SNRS))
            P(f"  decision SNRs {cand} [{chk(t + ' decision', cand, [-3, 0, 3])}]")
            P(f"  table B b*->V1: {tb} [{chk(t + ' tableB', tb, EXP[t]['tb'])}]")
            P(f"  power guard: {ndisc}/3 points with >= 6 discordant -> {'POWERED' if powered else 'UNDECIDED'}; V1 fewer at {wy}/3, b* fewer at {wx}/3 -> label {lab} "
              f"[{chk(t + ' guard/direction/label', (powered, ndisc, wy, wx, lab), (True, 3, 3, 0, '(i)'))}]")
            g, lo, hi, cens, vx, vy = gap(d, BSTAR, V1)
            gs = f"{g:+.2f} [{lo:+.2f}, {hi:+.2f}]"
            P(f"  SNR@0.1 gap b*-V1: {gs} [{chk(t + ' gap', gs, EXP[t]['gap'])}]  (4 dp {g:+.4f} [{lo:+.4f}, {hi:+.4f}]; SNR@0.1 b* {vx:.3f} V1 {vy:.3f}; censored {100 * cens:.0f}%)")
            SUM[t] = dict(gap=g, lo=lo, hi=hi)
            kv, kb, k0, kg = (int(fails(d, -3, a).sum()) for a in (V1, BSTAR, V0, GENIE))
            w = wilson(kv, n, 1.959963984540054); w2 = wilson(kv, n, 1.96)
            vs = f"{kv / n:.3f} ({w[0]:.3f}, {w[1]:.3f}), {kv}/{n}"
            P(f"  -3 dB failures: V1 {kv} b* {kb} V0 {k0} genie {kg}; V1 {vs} [{chk(t + ' V1 -3dB', vs, EXP[t]['v1'])}] (z = 1.96: ({w2[0]:.3f}, {w2[1]:.3f})); "
              f"b* · genie {kb} · {kg} [{chk(t + ' b*/genie', f'{kb} · {kg}', EXP[t]['bg'])}]; V0 BLER {k0 / n:.3f}")
            if "bgbler" in EXP[t]:
                P(f"    §0 b* / genie -3 dB BLER: {kb / n:.3f} / {kg / n:.3f} [{chk(t + ' §0 b*/genie BLER', f'{kb / n:.3f} / {kg / n:.3f}', EXP[t]['bgbler'])}]")
            SUM[t].update(v1=kv, v0=k0)
            P("  failures -3..+15: " + " | ".join(f"{nm} {' '.join(str(int(fails(d, s, a).sum())) for s in SNRS)}" for nm, a in (("V1", V1), ("b*", BSTAR), ("genie", GENIE), ("V0", V0))))
            b3, v3, g3, r3, l3, h3, u3 = recov(d, [-3]); bd, vd, gd, rd, ld, hd, ud = recov(d, cand)
            r3s, rds = f"{r3:.3f} [{l3:.3f}, {h3:.3f}]", f"{rd:.3f} [{ld:.3f}, {hd:.3f}]"
            P(f"  R(-3 dB) {r3s} [{chk(t + ' R(-3)', r3s, EXP[t]['r3'])}] (b*/V1/genie {b3}/{v3}/{g3}, undefined {u3}); R(decision {cand}) {rds} "
              f"[{chk(t + ' R(dp)', rds, EXP[t]['rd'])}] (b*/V1/genie {bd}/{vd}/{gd}, undefined {ud})")
            SUM[t]["r3"] = r3
            for s in cand[1:]:
                bb, vv, gg, rr, ll, hh, _ = recov(d, [s]); P(f"    R({s:+d} dB) {rr:.3f} [{ll:.3f}, {hh:.3f}] b*/V1/genie {bb}/{vv}/{gg}")
            nm = d[-3]["arr"][f"{V0}|nmse"]; fired = (~np.isfinite(nm) | (nm > 10.0)).any(axis=1); worst = np.nanmax(nm[np.isfinite(nm)])
            gl = f"{int(fired.sum()):>4}   {len(fired):>4}   {fired.mean():.3f}  {worst:.4g}"
            P(f"  V0 guard -3 dB: fired {int(fired.sum())} of {len(fired)} rate {fired.mean():.3f} worst {worst:.4g}" + (f" [{chk(t + ' V0 guard', gl, EXP[t]['guard'])}]" if "guard" in EXP[t] else "")
              + "; V1 guard fired at -3 dB: " + str(int((~np.isfinite(d[-3]['arr'][f'{V1}|nmse']) | (d[-3]['arr'][f'{V1}|nmse'] > 10.0)).any(axis=1).sum())))

    P("\n## aggregate labels and spreads (§6.1)")
    for pr, exp_sp in (("SRB", "SNR@0.1 격차 +0.32 / +0.35 / +0.37 dB (0.05); V1 −3 dB 실패 수 704 / 711 / 726 (22); R(−3 dB) 0.233 / 0.220 / 0.191 (0.042)"),
                       ("SRP", "SNR@0.1 격차 +2.01 / +1.95 / +2.12 dB (0.17); V1 −3 dB 실패 수 812 / 829 / 820 (17); R(−3 dB) 0.586 / 0.568 / 0.578 (0.018)")):
        ts = (f"{pr}B16e4", f"{pr}B16e4s2", f"{pr}B16e4s3"); labs = [LAB[t] for t in ts]
        P(f"  {pr}: seed labels {labs} -> {'시드 강건 (3/3 (i))' if labs == ['(i)'] * 3 else 'NOT 3/3 (i)'} [{chk(pr + ' aggregate', labs, ['(i)'] * 3)}]")
        # the record forms the spreads from the PRINTED (rounded) values -- do the same, and also give the unrounded spreads
        gp = [float(f"{SUM[t]['gap']:+.2f}") for t in ts]; vv = [SUM[t]["v1"] for t in ts]; rr = [float(f"{SUM[t]['r3']:.3f}") for t in ts]
        sp = (f"SNR@0.1 격차 {' / '.join(f'{x:+.2f}' for x in gp)} dB ({max(gp) - min(gp):.2f}); V1 −3 dB 실패 수 {' / '.join(map(str, vv))} ({max(vv) - min(vv)}); "
              f"R(−3 dB) {' / '.join(f'{x:.3f}' for x in rr)} ({max(rr) - min(rr):.3f})")
        ug = [SUM[t]["gap"] for t in ts]; ur = [SUM[t]["r3"] for t in ts]
        P(f"    spread: {sp} [{chk(pr + ' spread', sp, exp_sp)}]; unrounded gap spread {max(ug) - min(ug):.4f} dB, unrounded R spread {max(ur) - min(ur):.4f}; "
          f"V0 -3 dB failures {[SUM[t]['v0'] for t in ts]}")
    P("  §3 scoring (strict, from recomputed values):")
    for pr, w, gc, i in (("SRB", (0.258, 0.293), (0.18, 0.45), 1), ("SRP", (0.299, 0.335), (1.78, 2.24), 4)):
        ts = (f"{pr}B16e4s2", f"{pr}B16e4s3")
        P(f"    {i}. both (i): {all(LAB[t] == '(i)' for t in ts)}; {i + 1}. V1 -3 dB BLER (3 dp) in [{w[0]}, {w[1]}]: "
          f"{[(round(SUM[t]['v1'] / 2560, 3), w[0] <= round(SUM[t]['v1'] / 2560, 3) <= w[1], f'unrounded {SUM[t]['v1'] / 2560:.5f}') for t in ts]}; "
          f"{i + 2}. gap CI overlaps [{gc[0]:+.2f}, {gc[1]:+.2f}]: {[(f'[{SUM[t]['lo']:+.4f}, {SUM[t]['hi']:+.4f}]', SUM[t]['lo'] <= gc[1] and SUM[t]['hi'] >= gc[0]) for t in ts]}")

    P("\n## §5 checkpoints (torch.load map_location=cpu weights_only=False; sha256[:16] of the files)")
    import torch
    def ld(f):
        z = torch.load(f"{CONF}/ckpt/{f}", map_location="cpu", weights_only=False)
        return {k: z.get(k) for k in ("epoch", "best_epoch", "best_val", "stopped_by", "role", "rung", "attempt", "split_hash", "prior", "sigma_tag", "aborted")}
    for t, (stem, sha, ep, bep, lep, lsha, bv, rung, att, sh) in CK.items():
        b, l = ld(f"{stem}_best.pt"), ld(f"{stem}.pt"); sb, sl = sha16(f"{CONF}/ckpt/{stem}_best.pt"), sha16(f"{CONF}/ckpt/{stem}.pt")
        P(f"  {stem}_best.pt sha {sb} {b}\n  {stem}.pt      sha {sl} {l}")
        got = (sb, b["epoch"], b["best_epoch"], l["stopped_by"], l["epoch"], sl, l["best_epoch"], b["best_val"], b["rung"], b["attempt"], b["split_hash"])
        P(f"    §5 [{chk(t + ' §5', got, (sha, ep, bep, 'patience', lep, lsha, ep, bv, rung, att, sh))}]; best.best_val == last.best_val: {b['best_val'] == l['best_val']}; "
          f"mtime best {os.path.getmtime(f'{CONF}/ckpt/{stem}_best.pt'):.0f} last {os.path.getmtime(f'{CONF}/ckpt/{stem}.pt'):.0f}")
    for pr, (stem, sha, ep, bv, sh) in A1.items():
        b = ld(f"{stem}_best.pt"); sb = sha16(f"{CONF}/ckpt/{stem}_best.pt")
        P(f"  {stem}_best.pt sha {sb} {b}  [{chk(pr + ' a1 ckpt', (sb, b['epoch'], b['best_val'], b['split_hash']), (sha, ep, bv, sh))}]; "
          f"a1 raw ckpt id {sorted(D[pr + 'B16e4']['meta']['meta|stagec_ckpt_id'])} run|git {sorted(D[pr + 'B16e4']['meta']['run|git'])}")
    P("  partial checkpoints (registered as NOT evaluated): " + ", ".join(sorted(os.path.basename(f) for f in glob.glob(f"{CONF}/ckpt/d2sx_SR[BP]_N160000_a[45]*.pt"))))

    P("\n## GB' npz (results/d2_gbprime_{SRB,SRP}_N160000_a{1,2,3}.npz): ratio nmse_model / nmse_gmm")
    for (pr, a), (med, mn, mx) in GBP.items():
        f = f"{CONF}/results/d2_gbprime_{pr}_N160000_a{a}.npz"
        with np.load(f, allow_pickle=True) as z:
            r = np.asarray(z["nmse_model"], float) / np.asarray(z["nmse_gmm"], float)
            extra = {k: (z[k].item() if z[k].shape == () else z[k].shape) for k in z.files if k not in ("nmse_model", "nmse_gmm")}
        got = (f"{np.median(r):.4f}", f"{r.min():.4f}", f"{r.max():.4f}")
        P(f"  {pr} a{a}: median {got[0]} min {got[1]} max {got[2]} over {r.size} points [{chk(f'GBP {pr} a{a}', got, (med, mn, mx))}]  other keys {extra}")

    if "--xcheck" in sys.argv:
        P("\n## cross-check of the own reader against analysis.load_raw (all arms x KEYS_RAW x 7 SNRs)")
        sys.path.insert(0, f"{CONF}/code")
        from analysis import load_raw
        for t in D:
            d2, _, warns = load_raw("D2", root=f"{CONF}/raw_{t}"); bad = 0; tot = 0; derived = set()
            for key in d2:
                if not isinstance(key, tuple):
                    continue
                for arm in d2[key]:
                    for q in KEYS_RAW:
                        if isinstance(d2[key][arm], dict) and q in d2[key][arm]:
                            if f"{arm}|{q}" not in D[t][int(key[2])]["arr"]:      # an arm load_raw derives (not a raw key), e.g. R0-pilot@1
                                derived.add(arm); continue
                            tot += 1; bad += not np.array_equal(np.asarray(d2[key][arm][q], float), D[t][int(key[2])]["arr"][f"{arm}|{q}"].astype(float), equal_nan=True)
            P(f"  {t}: {tot} arrays compared, {bad} differ, load_raw warnings {len(warns)}, arms only in load_raw (derived, skipped) {sorted(derived)} "
              f"[{chk(t + ' xcheck', (tot, bad, len(warns)), (686, 0, 0))}]")

    P(f"\n## summary: {NCHK[0]} programmatic comparisons (each may cover several record values), mismatches: {len(MIS)}")
    for m in MIS:
        P("  MISMATCH", m)


if __name__ == "__main__":
    main()
