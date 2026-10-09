"""recompute_site.py -- independent recomputation of SITE16e4 (M-ours-dscore-C-V4 -> M-ours-dscore-C-V1, D2 C2 S2, raw_B16e4k)
straight from the raw .npz chunks.  Own loader, own exact sign test (math.comb), own power guard / label, own anchor rule,
own SNR@0.1 interpolation and paired bootstrap.  pair_baselines.py / analysis.py / Demo/*.py are NOT imported.
Read-only: nothing is written except stdout.  Run: CUDA_VISIBLE_DEVICES= ~/miniforge3/envs/torch/bin/python recompute_site.py"""
import glob, hashlib, json, os, re
from math import comb
import numpy as np

RAW = "/home/HTJ/t2/conf/raw_B16e4k"
MANIFEST = "/home/HTJ/t2/conf/results/review_next/run_manifest_B16e4k.json"
CKPT = "/home/HTJ/t2/conf/ckpt/d2sx_N160000_a1.pt"
V4, V1, BS = "M-ours-dscore-C-V4", "M-ours-dscore-C-V1", "M-ours-bstar"
PAT = re.compile(r"^D2_C2_S2_Nr8_T16_Tp4_dft_snr(-?\d+)_skip(\d+)_n(\d+)\.npz$")
FIXED = [-3.0, 0.0, 3.0]
N_TRIALS, N_IT, MIN_DISC = 2560, 16, 6


# ------------------------------------------------------------------ 1. load the raw myself, checking the pairing structure
def load():
    files = sorted(glob.glob(os.path.join(RAW, "*.npz")))
    pts, problems = {}, []
    for f in files:
        m = PAT.match(os.path.basename(f))
        if not m:
            problems.append(f"unmatched file name {os.path.basename(f)}"); continue
        pts.setdefault(float(m[1]), []).append((int(m[2]), int(m[3]), f))
    data = {}                                   # snr -> arm -> blk_err (2560, 16)
    raised = {}                                 # snr -> arm -> raised blocks
    for snr, chunks in sorted(pts.items()):
        chunks.sort()
        pos = 0
        for skip, n, _ in chunks:
            if skip != pos: problems.append(f"{snr:+.0f} dB: chunk gap/overlap at skip {skip} (expected {pos})")
            pos = skip + n
        if pos != N_TRIALS: problems.append(f"{snr:+.0f} dB: {pos} trials, expected {N_TRIALS}")
        arrs = {a: [] for a in (V4, V1, BS)}
        rs = {a: 0 for a in (V4, V1, BS)}
        seeds = set()
        for skip, n, f in chunks:
            with np.load(f) as z:
                seeds.add((int(z["run|seed"]), float(z["run|snr"]), int(z["run|iters"])))
                if int(z["run|skip"]) != skip or int(z["run|n"]) != n:
                    problems.append(f"{os.path.basename(f)}: run|skip/run|n != file name")
                for a in arrs:
                    be = z[f"{a}|blk_err"]
                    if be.shape != (n, N_IT): problems.append(f"{os.path.basename(f)} {a}: shape {be.shape}")
                    if f"{a}|failed" in z.files:            # runner writes it only when some trial raised
                        rs[a] += int(np.asarray(z[f"{a}|failed"]).sum())
                    if not np.all(np.isfinite(be)) or not np.all(np.isin(be, (0, 1))):
                        problems.append(f"{os.path.basename(f)} {a}: blk_err not all in {{0,1}}")
                    arrs[a].append(np.asarray(be, dtype=float))
        if len(seeds) != 1: problems.append(f"{snr:+.0f} dB: run|seed/snr/iters not constant across chunks: {seeds}")
        data[snr] = {a: np.concatenate(v) for a, v in arrs.items()}
        raised[snr] = rs
    return data, raised, problems, files


# ------------------------------------------------------------------ 2. own statistics
def sign_p(a, b):
    """exact two-sided sign test: P(X <= min(a,b)) doubled, X ~ Bin(a+b, 1/2); 1 if a+b == 0."""
    n = a + b
    return 1.0 if n == 0 else min(1.0, 2 * sum(comb(n, i) for i in range(min(a, b) + 1)) / 2 ** n)


def discordant(d, x, y):
    ex, ey = d[x][:, -1], d[y][:, -1]
    a = int(np.sum((ex == 1) & (ey == 0)))      # only x fails
    b = int(np.sum((ex == 0) & (ey == 1)))      # only y fails
    c = int(np.sum((ex == 1) & (ey == 1)))      # both fail
    return a, b, c


def label(res):
    """res = [(a, b, p)] at 3 decision SNRs; registration §1 / table_b order (iv) -> (i) -> (ii) -> (iii)."""
    powered = len(res) == 3 and sum(1 for a, b, _ in res if a + b >= MIN_DISC) >= 2
    wy = sum(1 for a, b, p in res if a > b and p < 0.05)    # second arm (y) fewer failures, significant
    wx = sum(1 for a, b, p in res if b > a and p < 0.05)    # first arm (x) fewer failures, significant
    lab = "(iv)" if not powered else "(i)" if wy >= 2 else "(ii)" if wx >= 2 else "(iii)"
    return powered, wy, wx, lab


def anchor(data, snrs, ref):
    n = N_TRIALS
    bl = {s: max(data[s][ref][:, -1].mean(), 0.5 / n) for s in snrs}
    cand = sorted((s for s in snrs if 0.005 <= bl[s] <= 0.9), key=lambda s: abs(np.log10(bl[s] / 0.1)))[:3]
    return sorted(cand), bl


def snr_at(snrs, bler, n, target=0.1):
    """first downward crossing of target on a log10(BLER)-linear-in-SNR line (floor 0.5/n). -> (value, kind)"""
    lb = np.log10(np.maximum(np.asarray(bler, float), 0.5 / n)); lt = np.log10(target)
    if lb[0] <= lt: return snrs[0], "lo"
    for i in range(len(snrs) - 1):
        if lb[i] > lt >= lb[i + 1]:
            return snrs[i] + (lb[i] - lt) / (lb[i] - lb[i + 1]) * (snrs[i + 1] - snrs[i]), "ok"
    return snrs[-1], "hi"


def gap_boot(data, snrs, x, y, B=2000, seed=20260925):
    """SNR@0.1(x) - SNR@0.1(y), paired bootstrap over trials: ONE index draw per SNR per replicate, applied to both arms.
    Same seed / B / draw order / interpolation / percentile as the registered `gain` (Demo/exp_0925_analysis.py) so an exact
    match is expected; the code itself is mine."""
    ex = [data[s][x][:, -1] for s in snrs]; ey = [data[s][y][:, -1] for s in snrs]; n = N_TRIALS
    (vx, kx), (vy, ky) = snr_at(snrs, [e.mean() for e in ex], n), snr_at(snrs, [e.mean() for e in ey], n)
    rng = np.random.default_rng(seed); g = np.full(B, np.nan)
    for r in range(B):
        bx, by = [], []
        for a, b in zip(ex, ey):
            i = rng.integers(len(a), size=len(a)); bx.append(a[i].mean()); by.append(b[i].mean())
        (ux, gx), (uy, gy) = snr_at(snrs, bx, n), snr_at(snrs, by, n)
        if gx == gy == "ok": g[r] = ux - uy
    cens = float(np.mean(~np.isfinite(g))); lo, hi = np.nanpercentile(g, [5, 95])
    return dict(est=vx - vy, kx=kx, ky=ky, vx=vx, vy=vy, lo=lo, hi=hi, cens=cens)


def main():
    data, raised, problems, files = load()
    snrs = sorted(data)
    print("== 1. raw structure (own loader) ==")
    print(f"files {len(files)}; SNR grid {[f'{s:+.0f}' for s in snrs]}; trials/SNR {[len(data[s][V1]) for s in snrs]}")
    print(f"raised blocks (<arm>|failed) V4/V1/b* per SNR: {[(f'{s:+.0f}', raised[s][V4], raised[s][V1], raised[s][BS]) for s in snrs]}")
    print("structural problems:", problems if problems else "none")
    print("pairing: V1 and V4 are columns of the SAME chunk files (same run|seed/skip/n per chunk; runner.run_task draws one"
          " (H, u, perm, Y) per trial for every arm) -> paired by construction; no separate seed per arm exists in the raw.")

    print("\n== 2. provenance hashes (own code) ==")
    digest = hashlib.sha256("".join(hashlib.sha256(open(c, "rb").read()).hexdigest() for c in files).encode()).hexdigest()[:16]
    m = json.load(open(MANIFEST))
    print(f"chunks-sha (sha256 of concatenated per-chunk sha256 hex, files sorted by name) = {digest}")
    print(f"manifest git_commit={m['git_commit']} n_raw_files={m['n_raw_files']} written={m['written']} "
          f"stagec sha256_16={m['stagec_checkpoint']['sha256_16']} stored_epoch={m['stagec_checkpoint']['stored_epoch']}")
    print(f"checkpoint file sha256[:16] = {hashlib.sha256(open(CKPT, 'rb').read()).hexdigest()[:16]}  ({os.path.basename(CKPT)})")
    import datetime
    w = datetime.datetime.strptime(m["written"][:19], "%Y-%m-%d %H:%M:%S").timestamp()
    mt = [os.path.getmtime(c) for c in files]
    print(f"chunk mtimes (KST): min {datetime.datetime.fromtimestamp(min(mt))}  max {datetime.datetime.fromtimestamp(max(mt))}; "
          f"newer than manifest: {sum(t > w for t in mt)}")
    with np.load(files[0]) as z:
        for a in (V1, V4):
            print(f"raw meta|budget|{a}: ckpt= ...{str(z[f'meta|budget|{a}']).split('ckpt=')[1].split()[0][-24:]}")

    print("\n== 3. the registered pair V4 -> V1 at the FIXED decision SNRs -3 / 0 / +3 dB ==")
    print("orientation: a = blocks where ONLY V4 fails, b = blocks where ONLY V1 fails (x = V4 first, y = V1 second)")
    res, rows = [], []
    for s in FIXED:
        a, b, c = discordant(data[s], V4, V1)
        p = sign_p(a, b)
        fV4, fV1 = int(data[s][V4][:, -1].sum()), int(data[s][V1][:, -1].sum())
        assert a - b == fV4 - fV1 and a + c == fV4 and b + c == fV1
        res.append((a, b, p)); rows.append((s, a, b, c, p, fV4, fV1))
        print(f"  {s:+.0f} dB: F_V4={fV4} F_V1={fV1}  a:b={a}:{b}  both={c}  D=a+b={a + b}  a-b={a - b:+d}  "
              f"p={p:.2g} (={p:.6f})  direction={'V1 fewer' if a > b else 'V4 fewer' if b > a else 'tie'}  sig={'yes' if p < 0.05 else 'no'}")
    A, Bn = sum(r[0] for r in res), sum(r[1] for r in res)
    pp = sign_p(A, Bn)
    print(f"  pooled (report-only): {A}:{Bn}  D={A + Bn}  a-b={A - Bn:+d}  p={pp:.2g} (={pp:.6f})  sig={'yes' if pp < 0.05 else 'no'}")
    powered, wy, wx, lab = label(res)
    print(f"  power guard: 3 points, {sum(1 for a, b, _ in res if a + b >= MIN_DISC)} with D >= {MIN_DISC} -> POWERED={powered}")
    print(f"  V1-side significant (a>b, p<.05): {wy}/3; V4-side significant (b>a, p<.05): {wx}/3  -> label {lab}")
    mixed = any(b > a and p < 0.05 for a, b, p in res) and any(a > b and p < 0.05 for a, b, p in res)
    print(f"  mixed result (opposite-direction significant points): {mixed}")
    try:
        from scipy.stats import binomtest
        print("  cross-check scipy.stats.binomtest two-sided p: " + "  ".join(
            f"{r[0]:+.0f} dB {binomtest(min(r[1], r[2]), r[1] + r[2], 0.5).pvalue:.6f}" for r in rows)
              + f"  pooled {binomtest(min(A, Bn), A + Bn, 0.5).pvalue:.6f}")
    except Exception as e:
        print("  scipy cross-check skipped:", e)

    auto, bl = anchor(data, snrs, V4)
    print(f"\n  anchor rule on V4 (BLER in [0.005, 0.9], 3 smallest |log10(BLER/0.1)|): {[f'{s:+.0f}' for s in auto]}  "
          f"(V4 BLER@16: {', '.join(f'{s:+.0f}:{bl[s]:.4f}' for s in snrs)})")
    autob, _ = anchor(data, snrs, BS)
    print(f"  anchor rule on b* (drift pairs): {[f'{s:+.0f}' for s in autob]}")

    print("\n== 4. SNR@0.1 gap (V4 minus V1), 90% paired bootstrap ==")
    g = gap_boot(data, snrs, V4, V1)
    print(f"  SNR@0.1: V4 {g['vx']:.4f} ({g['kx']})  V1 {g['vy']:.4f} ({g['ky']})  gap {g['est']:+.4f} dB -> {g['est']:+.2f}")
    print(f"  90% paired bootstrap (B=2000, default_rng(20260925), 5/95 nanpercentile): [{g['lo']:+.4f}, {g['hi']:+.4f}] "
          f"-> [{g['lo']:+.2f}, {g['hi']:+.2f}]; censored {100 * g['cens']:.0f}%")
    print(f"  formatted as `gain` would: {g['est']:+.2f} dB  [90% paired bootstrap {g['lo']:+.2f}, {g['hi']:+.2f}; censored replicates {100 * g['cens']:.0f}%]")
    print(f"  sign: gap > 0 <=> V4 needs a HIGHER SNR for BLER 0.1 <=> V1 reaches 0.1 at a lower SNR (gain of V1 over V4 = +gap)")
    g2 = gap_boot(data, snrs, V4, V1, seed=1)
    print(f"  robustness (NOT the registered setting; seed=1, B=2000): [{g2['lo']:+.2f}, {g2['hi']:+.2f}]")

    print("\n== 5. drift pairs b* -> V1, b* -> V4 (anchor rule on b*), own code ==")
    for y in (V1, V4):
        rr = [discordant(data[s], BS, y) for s in autob]
        ps = [sign_p(a, b) for a, b, _ in rr]
        A2, B2 = sum(r[0] for r in rr), sum(r[1] for r in rr)
        pw, wy2, wx2, lab2 = label([(a, b, p) for (a, b, _), p in zip(rr, ps)])
        gg = gap_boot(data, snrs, BS, y)
        print(f"  {BS} -> {y}: " + "  ".join(f"{s:+.0f} dB {a}:{b} p={p:.2g}" for s, (a, b, _), p in zip(autob, rr, ps))
              + f"   pooled {A2}:{B2} p={sign_p(A2, B2):.2g}  POWERED={pw} wy={wy2} wx={wx2} -> {lab2}")
        print(f"      SNR@0.1 gap: {gg['est']:+.2f} dB  [90% paired bootstrap {gg['lo']:+.2f}, {gg['hi']:+.2f}; censored replicates {100 * gg['cens']:.0f}%]"
              f"   failures@16 {BS} {'/'.join(str(int(data[s][BS][:, -1].sum())) for s in autob)}  {y} {'/'.join(str(int(data[s][y][:, -1].sum())) for s in autob)}")

    print("\n== 6. registration-header arithmetic ((c)(d)(e)) checked with the own sign test ==")
    for a, b in ((10, 2), (11, 3), (74, 51), (75, 52)):
        print(f"  {a}:{b} p={sign_p(a, b):.4f}")
    for diff in (23, 8):
        dmax = max(D for D in range(diff, 400, 2) if sign_p((D + diff) // 2, (D - diff) // 2) < 0.05)
        print(f"  a-b={diff}: largest D with p<.05 = {dmax}")
    c3 = {s: discordant(data[s], V4, V1)[2] for s in FIXED}
    print(f"  overlap c (both fail) at -3/0/+3: {c3[-3.0]}/{c3[0.0]}/{c3[3.0]}  (thresholds 320/86/19; pooled Σc={sum(c3.values())} vs 437)")
    bv1 = discordant(data[-3.0], BS, V1); bv4 = discordant(data[-3.0], BS, V4)
    print(f"  (e) -3 dB: b*∩V1={bv1[2]} b*∩V4={bv4[2]} F_b*={int(data[-3.0][BS][:, -1].sum())} -> c(-3) >= {bv1[2] + bv4[2] - int(data[-3.0][BS][:, -1].sum())}")


if __name__ == "__main__":
    main()
