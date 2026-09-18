"""exp_0925 analysis (measurement convention M-1).   usage: python exp_0925_analysis.py [--tag X] [--ntrain 10000]   -> stdout + exp_0925_results[_X].txt (overwritten)
Sections: 1 fit table (validation-selected fits, KL gaps on the independent test set)   2 per point: rows, clip statistics, paired sign tests (@16 and @8)
          3 per cell x prior: BLER@16 table, SNR@BLER 0.1 (log-linear interpolation), paired bootstrap of SNR gains   4 cross-Tp goodput (H vs H4)
          5 PRE-REGISTERED criteria evaluated mechanically (decision_log D-19 + "D-19 보정"); the printed verdict is an aid — the reading is done by a human afterwards.
Pre-registered rules coded here (fixed BEFORE any BLER was seen):
  K1  decision cell = (H, prior S):  gain := SNR@0.1(lmmseC_pf) - SNR@0.1(exactEP-true).  gain < 0.5 dB -> K1 fires;  90% paired-bootstrap CI straddles 0.5 -> UNDECIDED (raise n).
      K1 fired AND the cross-Tp goodput-envelope gain of exactEP-true over lmmseC_pf in prior P is >= 5% at >= 3 consecutive SNR points -> 'scope restriction', not 'stop'.
  K2  decision cell = (H, prior S); decision points = the 3 grid SNRs whose Hgmm-K32 BLER@16 is closest to 0.1 in |log10| among those with BLER in [0.005, 0.9].
      Hscore-exact must beat the GMM arm (only-GMM-fails > only-score-fails, two-sided sign test p < .05) at >= 2 of the 3 points -> K3 (go to M2); otherwise K2 fires.
      Evaluated against the literal arm Hgmm-K32 AND against b* (best validation log-lik Hgmm arm); K3 needs BOTH. The -mp (mean-preserving clip) pair must agree, else UNDECIDED.
  R6/R7 (power guard, pre-registered with the rest): K2 may only FIRE if the test could have detected the opposite — 3 decision points must exist on the grid and at least
      2 of them must have >= 6 discordant pairs (below that a two-sided sign test cannot reach p < .05). Otherwise the verdict is UNDECIDED: raise n or extend the SNR grid."""
import os, re, sys, glob, argparse, itertools, warnings
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from exp_0921_analysis import wilson, sign_p, paired, row
NT = 4; CELLS = {"H": (8, 16, 2), "H4": (8, 16, 4), "R": (4, 28, 2)}
PAT = re.compile(r"K_(H4|H|R)_([USP])_Nr(\d+)_T(\d+)_Tp(\d+)_(dft|eig)_snr(-?\d+)_skip(\d+)_n(\d+)\.npz$")
_out = []


def P(*a):
    s = " ".join(str(x) for x in a); print(s); _out.append(s)


def load(raw):
    pts = {}
    for f in glob.glob(os.path.join(raw, "K_*.npz")):
        m = PAT.search(os.path.basename(f))
        if m: pts.setdefault((m[1], m[2], float(m[7])), []).append((int(m[8]), int(m[9]), f))
    data, meta = {}, {}
    for key, chunks in pts.items():
        chunks.sort(); pos = 0; ok = True
        for skip, n, _ in chunks: ok &= skip == pos; pos = skip + n
        if not ok: P(f"  WARNING {key}: chunk sequence has holes/overlaps: {[(s, n) for s, n, _ in chunks]}")
        zs = [np.load(f) for _, _, f in chunks]; d = {}
        for k in zs[0].files:
            if k.startswith("meta|"): meta.setdefault(key[:2], {})[k[5:]] = zs[0][k].item(); continue
            if "|" not in k: continue
            v, q = k.split("|"); d.setdefault(v, {})[q] = np.concatenate([z[k] for z in zs])
        data[key] = d
    return data, meta


def snr_at(snrs, bler, n, target=0.1):
    """first downward crossing of the target, log-linear interpolation -> (value, flag); flag 'lo' = already below at the first point, 'hi' = never reached (value = grid edge)."""
    lb = np.log10(np.maximum(bler, 0.5 / n)); lt = np.log10(target)
    if lb[0] <= lt: return snrs[0], "lo"
    for i in range(len(snrs) - 1):
        if lb[i] > lt >= lb[i + 1]: return snrs[i] + (lb[i] - lt) / (lb[i] - lb[i + 1]) * (snrs[i + 1] - snrs[i]), "ok"
    return snrs[-1], "hi"


def fmt_at(v, f): return {"ok": f"{v:6.2f}", "lo": f"<={v:4.0f}", "hi": f" >{v:4.0f}"}[f]


def gain(data, cell, prior, snrs, x, y, B=2000):
    """SNR@0.1(x) - SNR@0.1(y) with a paired bootstrap over trials (same resampled trial indices for both arms at every SNR). -> dict(text, est, lo, hi, kind)"""
    ex = [data[(cell, prior, s)][x]["blk_err"][:, -1] for s in snrs]; ey = [data[(cell, prior, s)][y]["blk_err"][:, -1] for s in snrs]; n = min(len(e) for e in ex)
    (vx, fx), (vy, fy) = snr_at(snrs, [e.mean() for e in ex], n), snr_at(snrs, [e.mean() for e in ey], n)
    if fx == "hi" and fy == "ok": return dict(text=f">= {vx - vy:+.2f} dB ({x} never reaches 0.1 on the grid)", est=vx - vy, lo=vx - vy, hi=np.inf, kind="lower")
    if fx == "ok" and fy == "lo": return dict(text=f">= {vx - vy:+.2f} dB ({y} is already below 0.1 at the lowest grid SNR)", est=vx - vy, lo=vx - vy, hi=np.inf, kind="lower")
    if fx != "ok" or fy != "ok": return dict(text=f"n/a ({fmt_at(vx, fx).strip()} vs {fmt_at(vy, fy).strip()}) — extend the SNR grid", est=np.nan, lo=np.nan, hi=np.nan, kind="na")
    rng = np.random.default_rng(20260925); g = []
    for _ in range(B):
        bx, by = [], []
        for a, b in zip(ex, ey):
            i = rng.integers(len(a), size=len(a)); bx.append(a[i].mean()); by.append(b[i].mean())
        (ux, gx), (uy, gy) = snr_at(snrs, bx, n), snr_at(snrs, by, n); g.append(ux - uy if gx == gy == "ok" else np.nan)
    g = np.array(g); cens = np.mean(~np.isfinite(g)); lo, hi = np.nanpercentile(g, [5, 95])
    return dict(text=f"{vx - vy:+.2f} dB  [90% paired bootstrap {lo:+.2f}, {hi:+.2f}; censored replicates {100 * cens:.0f}%]", est=vx - vy, lo=lo, hi=hi, kind="ok")


def fit_table(fits, ntrain):
    P("=" * 20, "1. EM fits (selection by validation log-lik; KL(true||fit) = E_true[log p_true - log p_fit] on an independent test set, nat per channel vector)", "=" * 20)
    pat = re.compile(rf"fit_([USP])_Nr(\d+)_(full|kron)K(\d+)_n{ntrain}\.npz$"); rows = {}
    for f in glob.glob(os.path.join(fits, "fit_*.npz")):
        m = pat.search(os.path.basename(f))
        if m: rows[(m[1], int(m[2]), m[3], int(m[4]))] = np.load(f)
    for (p, Nr) in sorted({k[:2] for k in rows}):
        sub = {k: v for k, v in rows.items() if k[:2] == (p, Nr)}; best = max(sub, key=lambda k: float(sub[k]["ll_val"])); g = next(iter(sub.values()))
        P(f"  prior {p}  {Nr}x{NT} (N = {Nr * NT}):  Gaussian sample-covariance prior KL = {float(g['kl_test_gauss']):.3f}")
        for k in sorted(sub):
            z = sub[k]; P(f"    {k[2]:<4} K={k[3]:<2} kappa={int(z['kappa']):<3} best@{int(z['it_best']):<3}/{int(z['n_iter']):<3} train-val gap {float(z['ll_train']) - float(z['ll_val']):6.3f}  ll_val {float(z['ll_val']):9.3f}"
                          f"  KL_test {float(z['kl_test']):6.3f}  pi_min {z['pi'].min():.4f}" + ("   <- best validation log-lik" if k == best else ""))


PAIRS = [("Hgmm-K32", "Hscore-exact"), ("BSTAR", "Hscore-exact"), ("Hgmm-K32-mp", "Hscore-exact-mp"), ("lmmseC_pf", "exactEP-true"), ("lmmseC_pf", "BSTAR"), ("lmmseC_pf", "Hscore-exact"),
         ("BSTAR", "exactEP-true"), ("Hscore-exact", "exactEP-true"), ("Hgmm-K16", "Hgmm-K32"), ("Hgmm-K32", "Hgmm-K64"), ("Hgmm-K32", "Hgmm-kron"),
         ("Hscore-K32", "Hgmm-K32"), ("Hscore-K32", "Hscore-exact"), ("Hgmm-K32", "Hgmm-K32-mp"), ("Hscore-exact", "Hscore-exact-mp"), ("exactEP-true", "exactEP-true-mp"),
         ("exactEP-true", "oracle_pf"), ("pilot_Hgmm-K32", "Hgmm-K32"), ("pilot_C", "lmmseC_pf")]


MIN_DISC = 6                    # R6: a two-sided sign test cannot reach p < .05 with fewer than 6 discordant pairs (2 / 2^6 = .031) -> the point carries no power


def k2_eval(data, cell, prior, snrs, gmm, score):
    """-> (decision SNRs, per-point (a, b, p), wins_score, wins_gmm, pooled (a, b, p), powered);  a = only the GMM arm fails, b = only the score arm fails.
    Decision points: the (up to) 3 grid SNRs whose Hgmm-K32 BLER@16 is closest to 0.1 in |log10| among those in [0.005, 0.9].
    powered (R6/R7): 3 decision points exist AND at least 2 of them have >= MIN_DISC discordant pairs. Not powered -> the verdict is UNDECIDED, not K2."""
    n = len(data[(cell, prior, snrs[0])]["Hgmm-K32"]["blk_err"]); bl = {s: max(data[(cell, prior, s)]["Hgmm-K32"]["blk_err"][:, -1].mean(), 0.5 / n) for s in snrs}
    cand = sorted((s for s in snrs if 0.005 <= bl[s] <= 0.9), key=lambda s: abs(np.log10(bl[s] / 0.1)))[:3]; cand.sort()
    res = [paired(data[(cell, prior, s)], gmm, score) for s in cand]; A = sum(r[0] for r in res); Bv = sum(r[1] for r in res)
    powered = len(cand) == 3 and sum(1 for a, b, _ in res if a + b >= MIN_DISC) >= 2
    return cand, res, sum(1 for a, b, p in res if a > b and p < 0.05), sum(1 for a, b, p in res if b > a and p < 0.05), (A, Bv, sign_p(A, Bv)), powered


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--tag", default=""); ap.add_argument("--ntrain", type=int, default=10000); a = ap.parse_args(); sfx = f"_{a.tag}" if a.tag else ""
    data, meta = load(os.path.join(HERE, "exp_0925_raw" + sfx))
    P("exp_0925 — D-19 kill test.  QPSK (133,171)_8, Nt=4, 16 iterations, joint arms = D-15 + LOO + beta 0.7; seed 20260925.  '@16' = last iteration.")
    fit_table(os.path.join(HERE, "exp_0925_fits" + sfx), a.ntrain)
    groups = sorted({k[:2] for k in data}, key=lambda g: (list(CELLS).index(g[0]), "SPU".index(g[1]))); summ = {}
    P("\n" + "=" * 20, "2. per point", "=" * 20)
    for cell, prior in groups:
        Nr, T, Tp = CELLS[cell]; snrs = sorted(k[2] for k in data if k[:2] == (cell, prior)); bs = meta[(cell, prior)]["bstar"]
        for s in snrs:
            d = data[(cell, prior, s)]; d["BSTAR"] = d[bs]
            P(f"\n--- cell {cell} ({Nr}x{NT}, T={T}, Tp={Tp})  prior {prior}  SNR {s:.0f} dB   b* = {bs} (kron K = {meta[(cell, prior)]['kron_K']})")
            for name, v in d.items():
                if name != "BSTAR": P(row(name, v))
            P("    clip [fraction of site updates clipped | mean |mu_legacy - m|^2/|m|^2 over clipped updates], trial means: " +
              "  ".join(f"{k}: {v['clip'][:, 0].mean():.2f}|{v['clip'][:, 1].mean():.1e}" for k, v in d.items() if "clip" in v and k != "BSTAR"))
            for x, y in PAIRS:
                if x in d and y in d:
                    a8, b8, p8 = paired(d, x, y, 7); a16, b16, p16 = paired(d, x, y)
                    P(f"    paired {x.replace('BSTAR', 'b*')} vs {y}: @16 only-first-fails {a16}, only-second-fails {b16}, p={p16:.2g}   (@8: {a8}:{b8}, p={p8:.2g})")
    P("\n" + "=" * 20, "3. BLER@16 tables, SNR@BLER 0.1, SNR gains", "=" * 20)
    for cell, prior in groups:
        Nr, T, Tp = CELLS[cell]; snrs = sorted(k[2] for k in data if k[:2] == (cell, prior)); ns = [len(data[(cell, prior, s)]["genie"]["blk_err"]) for s in snrs]
        P(f"\n--- cell {cell} ({Nr}x{NT}, T={T}, Tp={Tp}, K={NT * (T - Tp) - 6})  prior {prior}   n per SNR: {ns}   b* = {meta[(cell, prior)]['bstar']}")
        P(f"  {'SNR [dB]':<20}" + " ".join(f"{s:>6.0f}" for s in snrs) + "   SNR@0.1")
        for name in data[(cell, prior, snrs[0])]:
            if name == "BSTAR": continue
            bl = np.array([data[(cell, prior, s)][name]["blk_err"][:, -1].mean() for s in snrs]); summ[(cell, prior, name)] = (np.array(snrs), bl)
            P(f"  {name:<20}" + " ".join(f"{x:6.3f}" for x in bl) + "   " + fmt_at(*snr_at(snrs, bl, min(ns))))
        if len(snrs) >= 3:
            for x, y in (("lmmseC_pf", "exactEP-true"), ("lmmseC_pf", "BSTAR"), ("lmmseC_pf", "Hscore-exact"), ("BSTAR", "exactEP-true"), ("Hscore-exact", "exactEP-true"), ("Hgmm-K32", "Hscore-exact")):
                P(f"  SNR@0.1 gain {x.replace('BSTAR', 'b*')} -> {y.replace('BSTAR', 'b*')}: " + gain(data, cell, prior, snrs, x, y)["text"])
    P("\n" + "=" * 20, "4. cross-Tp goodput K(1-BLER@16)/T, cells H (Tp=2) and H4 (Tp=4); envelope = best Tp per SNR", "=" * 20)
    env_gain = {}
    for prior in "SPU":
        if ("H", prior, "genie") not in summ or ("H4", prior, "genie") not in summ: continue
        snrs = [s for s in summ[("H", prior, "genie")][0] if s in summ[("H4", prior, "genie")][0]]; P(f"\n--- prior {prior}   (upper bounds K/T: Tp=2 {50 / 16:.3f}, Tp=4 {42 / 16:.3f})")
        P(f"  {'SNR [dB]':<26}" + " ".join(f"{s:>7.0f}" for s in snrs)); env = {}
        for name in ("lmmseC_pf", "pilot_C", meta[("H", prior)]["bstar"], "Hscore-exact", "exactEP-true", "genie"):
            g = {}
            for cell, K in (("H", 50), ("H4", 42)):
                sn, bl = summ[(cell, prior, name)]; g[cell] = np.array([K * (1 - bl[list(sn).index(s)]) / 16 for s in snrs])
                P(f"  {name:<18} Tp={CELLS[cell][2]}    " + " ".join(f"{x:7.3f}" for x in g[cell]))
            env[name] = np.maximum(g["H"], g["H4"])
        base = np.maximum(env["lmmseC_pf"], env["pilot_C"])
        for name in (meta[("H", prior)]["bstar"], "Hscore-exact", "exactEP-true"):
            r = 100 * (env[name] / np.maximum(base, 1e-9) - 1); env_gain[(prior, name)] = r
            P(f"  envelope gain over the second-moment envelope (lmmseC_pf / pilot_C, best Tp): {name:<14}" + " ".join(f"{x:+6.1f}%" for x in r))
    P("\n" + "=" * 20, "5. pre-registered criteria, evaluated mechanically (aid only; the reading follows)", "=" * 20)
    for prior in "SPU":
        if ("H", prior) not in meta: continue
        snrs = sorted(k[2] for k in data if k[:2] == ("H", prior)); tagp = "DECISION CELL" if prior == "S" else "context"
        if len(snrs) < 3: continue
        g1 = gain(data, "H", prior, snrs, "lmmseC_pf", "exactEP-true"); gb = gain(data, "H", prior, snrs, "lmmseC_pf", "BSTAR")
        v1 = "n/a" if g1["kind"] == "na" else "NOT fired" if g1["lo"] >= 0.5 else "FIRES" if g1["hi"] < 0.5 else ("UNDECIDED (CI straddles 0.5 dB) — point estimate " + ("< 0.5" if g1["est"] < 0.5 else ">= 0.5"))
        P(f"\n[{tagp}] (H, prior {prior})   K1: gain(d over a) = {g1['text']}  ->  {v1}.    achievable with b*: {gb['text']}")
        if prior == "S" and ("P", "exactEP-true") in env_gain:
            r = env_gain[("P", "exactEP-true")] >= 5.0; run = max((sum(1 for _ in grp) for val, grp in itertools.groupby(r) if val), default=0)
            P(f"    scope branch: cross-Tp envelope gain of exactEP-true in prior P >= 5% at {run} consecutive SNR points (needs >= 3)")
        out = {}; powered = True
        for gmm, score, lab in (("Hgmm-K32", "Hscore-exact", "literal"), ("BSTAR", "Hscore-exact", "b*"), ("Hgmm-K32-mp", "Hscore-exact-mp", "mp-clip")):
            cand, res, ws, wg, pool, pw = k2_eval(data, "H", prior, snrs, gmm, score); out[lab] = ws >= 2; powered &= pw
            P(f"    K2 [{lab:<7}] decision SNRs {cand}: (only-GMM-fails : only-score-fails, p) = " + ", ".join(f"{x}:{y} p={p:.2g}" for x, y, p in res) +
              f"   score wins {ws}/{len(cand)}, GMM wins {wg}/{len(cand)}, pooled {pool[0]}:{pool[1]} p={pool[2]:.2g}" + ("" if pw else "   [UNDERPOWERED]"))
        base = out["literal"] and out["b*"]                                                # the score arm must beat the literal AND the validation-best GMM arm
        verdict = ("K3 (score branch survives -> M2)" if base and out["mp-clip"] else "K2 FIRES (score branch stops)" if not base and not out["mp-clip"] else "UNDECIDED (the clip rule changes the answer)")
        if not powered and "K3" not in verdict: verdict = "UNDECIDED — the test had no power (R6/R7: need 3 decision points on the grid and >= 6 discordant pairs at >= 2 of them); raise n or extend the SNR grid"
        P(f"    K2/K3 mechanical verdict: {verdict}")
    with open(os.path.join(HERE, f"exp_0925_results{sfx}.txt"), "w") as f: f.write("\n".join(_out) + "\n")


if __name__ == "__main__":
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning); main()
