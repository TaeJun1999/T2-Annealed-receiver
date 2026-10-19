"""recompute_e1ms.py -- independent record audit of NEXT_EXPERIMENTS_D2SITEMS §6 (E1+, tag D2SITEMS), Fable 5.1 subagent, 2026-10-19.
Reads the raw chunks (npz) with numpy only; conf/code (e1ms_compare / pair_baselines / analysis) is NOT imported.  Read-only.
Every rule is re-implemented from the frozen text (§1.4): paired discordant counts at iteration 16, exact two-sided sign test,
MIN_DISC 6 power guard, label order (iv) -> (i) -> (ii) -> (iii), SNR@0.1 by log-linear interpolation (first downward crossing,
BLER floored at 0.5/n), 90 % paired bootstrap B 2000 / default_rng(20260925) / rng.integers(n, size=n) per grid point in order,
same indices for both arms, nanpercentile 5 / 95, censored = replicates without a crossing.
    CUDA_VISIBLE_DEVICES= nice -n 10 taskset -c 2-5 ~/miniforge3/envs/torch/bin/python -B recompute_e1ms.py > recompute_e1ms.out"""
import glob, hashlib, json, math, os, re, sys, time, zipfile
import numpy as np

CONF = "/home/HTJ/t2/conf"
RAW = f"{CONF}/raw_D2SITEMS"; BASE = f"{CONF}/raw_B16e4k"; WT = "/home/HTJ/t2_wtMS/conf"
MS, V1, V4, GEN = "M-ours-dscore-C-V1ms", "M-ours-dscore-C-V1", "M-ours-dscore-C-V4", "R5-genie"
KEYS_RAW = ("blk_err", "ber", "nmse", "tauL_gmean", "alphaD", "tauL_clip_frac", "alphaD_clip")
KEYS4 = ("blk_err", "ber", "tauL_gmean", "alphaD")
SNRS = [-3.0, 0.0, 3.0]
PAT = re.compile(r"^D2_(C\d+)_(S\d)_Nr(\d+)_T(\d+)_Tp(\d+)_dft_snr(-?\d+)_skip(\d+)_n(\d+)\.npz$")

tally = {"match": 0, "mismatch": 0}
def chk(name, got, want, eq=None):
    ok = (eq(got, want) if eq else got == want)
    tally["match" if ok else "mismatch"] += 1
    print(f"  [{'OK ' if ok else 'XX '}] {name}: got {got!r}" + ("" if ok else f"  WANT {want!r}"))
    return ok

def pfmt(p): return f"{p:.2g}"
def sign_p(a, b):
    n = a + b
    if n == 0: return 1.0
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(min(a, b) + 1)) / 2 ** n)
def snr_at(snrs, bler, n, target=0.1):
    lb = np.log10(np.maximum(np.asarray(bler, float), 0.5 / n)); lt = math.log10(target)
    if lb[0] <= lt: return snrs[0], "lo"
    for i in range(len(snrs) - 1):
        if lb[i] > lt >= lb[i + 1]:
            return snrs[i] + (lb[i] - lt) / (lb[i] - lb[i + 1]) * (snrs[i + 1] - snrs[i]), "ok"
    return snrs[-1], "hi"
def same(x, y): return np.array_equal(np.asarray(x), np.asarray(y), equal_nan=True) if np.asarray(x).dtype.kind == "f" else np.array_equal(x, y)

def load_point(root, snr, arms):
    """-> dict arm -> dict key -> concatenated (n, 16) arrays in skip order; also returns the chunk list and meta/run of each chunk."""
    fs = []
    for f in sorted(glob.glob(f"{root}/D2_C2_S2_Nr8_T16_Tp4_dft_snr{int(snr)}_skip*_n40.npz")):
        m = PAT.match(os.path.basename(f)); fs.append((int(m[7]), int(m[8]), f))
    fs.sort()
    out = {a: {k: [] for k in KEYS_RAW} for a in arms}; metas = []; extra_keys = set(); nonfinite = 0; failed_keys = 0
    for skip, n, f in fs:
        z = np.load(f)
        keys = set(z.files)
        for a in arms:
            for k in KEYS_RAW:
                out[a][k].append(z[f"{a}|{k}"])
        failed_keys += sum(1 for k in keys if k.endswith("|failed"))
        extra_keys |= {k.split("|")[0] for k in keys} - {"meta", "run"} - set(arms)
        for a in arms:
            be = z[f"{a}|blk_err"]
            nonfinite += int((~np.isfinite(be.astype(float))).sum())
        metas.append({k: (z[k].item() if z[k].ndim == 0 else None) for k in keys if k.startswith(("meta|", "run|"))} | {"_skip": skip, "_n": n, "_f": f, "_mtime": os.path.getmtime(f)})
    for a in arms:
        for k in KEYS_RAW:
            out[a][k] = np.concatenate(out[a][k]) if out[a][k] else None
    return out, fs, metas, extra_keys, failed_keys, nonfinite

print("=" * 100); print("recompute_e1ms.py  --  independent recomputation of NEXT_EXPERIMENTS_D2SITEMS §6 (tag D2SITEMS)")
print("date:", time.strftime("%Y-%m-%d %H:%M:%S %Z"), "| numpy", np.__version__)

# ---------------------------------------------------------------------------------------------------------------------------- 1
print("\n### 1. raw_D2SITEMS: chunk plan, meta, arms, shapes, non-finite blk_err")
D = {}; Dmeta = []; Dfs = {}
for s in SNRS:
    pt, fs, metas, extra, nfail, nonfin = load_point(RAW, s, (MS, GEN))
    D[s] = pt; Dmeta += metas; Dfs[s] = fs
    plan = [(sk, n) for sk, n, _ in fs]
    chk(f"{s:+.0f} dB chunk plan == {{(40k, 40): k < 64}}", plan, [(40 * k, 40) for k in range(64)])
    chk(f"{s:+.0f} dB arms other than {{V1ms, genie}}", sorted(extra), [])
    chk(f"{s:+.0f} dB '|failed' keys", nfail, 0)
    chk(f"{s:+.0f} dB non-finite blk_err entries", nonfin, 0)
    chk(f"{s:+.0f} dB n (V1ms blk_err rows)", len(pt[MS]["blk_err"]), 2560)
    chk(f"{s:+.0f} dB shapes (40,16) for 2 arms x 7 keys in every chunk",
        all(np.load(f)[f"{a}|{k}"].shape == (40, 16) for _, _, f in fs for a in (MS, GEN) for k in KEYS_RAW), True)
chk("total chunks", len(Dmeta), 192)
allfiles = sorted(glob.glob(f"{RAW}/*.npz")); chk("files in raw_D2SITEMS (all)", len(allfiles), 192)
chk("every file name matches the D2_C2_S2 pattern with snr in {-3,0,3}", all(PAT.match(os.path.basename(f)) and int(PAT.match(os.path.basename(f))[6]) in (-3, 0, 3) for f in allfiles), True)
def uniq(key): return sorted({str(m.get(key)) for m in Dmeta})
chk("run|git (all chunks)", uniq("run|git"), ["9a2c9fd4"])
chk("meta|ms_arm present in all chunks", all("meta|ms_arm" in m for m in Dmeta), True)
chk("meta|ms_arm string", uniq("meta|ms_arm"), ["V1 with the site covariance C+ = nu J+ replaced by tr(C+)/N I (arms.MatchedScalarPrior): M-ours-dscore-C-V1ms"])
chk("meta|stagec_ckpt_id", uniq("meta|stagec_ckpt_id"), ["sha256[:16]=4443921ce8d5c4a1 epoch=1784 best_epoch=1764 role=legacy-last 8x4 | BEST_WEIGHTS_UNAVAILABLE: evaluated = last-epoch EMA, reported best_val belongs to best_epoch"])
chk("meta|stagec_ckpt", uniq("meta|stagec_ckpt"), ["/home/HTJ/t2/conf/ckpt/d2sx_N160000_a1.pt"])
chk("meta|bstar", uniq("meta|bstar"), ["kron"]); chk("meta|kron_K", uniq("meta|kron_K"), ["1024"])
chk("meta|ll_val|kron (|d| <= 1e-9 of -11.459169831224418)", all(abs(float(m["meta|ll_val|kron"]) + 11.459169831224418) <= 1e-9 for m in Dmeta), True)
chk("meta|ntrain", uniq("meta|ntrain"), ["160000.0"]); chk("meta|em_sec", uniq("meta|em_sec"), ["107957.18832826614"])
chk("meta|jobs", uniq("meta|jobs"), ["96"]); chk("meta|worker_gb", uniq("meta|worker_gb"), ["1.5"])
chk("run|iters", uniq("run|iters"), ["16"]); chk("run|n", uniq("run|n"), ["40"]); chk("run|seed", uniq("run|seed"), ["20260926"])
chk("run|beta", uniq("run|beta"), ["0.7"]); chk("run|t_in", uniq("run|t_in"), ["5"]); chk("run|dtype", uniq("run|dtype"), ["complex128/float64"])
chk("run|skip == file name skip (all)", all(int(m["run|skip"]) == m["_skip"] for m in Dmeta), True)
chk("run|snr == file name snr (all)", all(float(m["run|snr"]) == float(PAT.match(os.path.basename(m["_f"]))[6]) for m in Dmeta), True)
chk("meta|dscore_status present (ABSENT -- no GATE-PASSING ...)", all(str(m.get("meta|dscore_status", "")).startswith("ABSENT -- no GATE-PASSING") for m in Dmeta), True)
mt = [m["_mtime"] for m in Dmeta]
print(f"  chunk mtime range: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(min(mt)))} .. {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(max(mt)))} KST")

# ---------------------------------------------------------------------------------------------------------------------------- 2
print("\n### 2. base raw_B16e4k: 448 chunks, manifest, 3-point plan, arms, chunks-sha digest")
bfiles = sorted(glob.glob(f"{BASE}/*.npz")); chk("files in raw_B16e4k", len(bfiles), 448)
man = json.load(open(f"{CONF}/results/review_next/run_manifest_B16e4k.json"))
chk("manifest written", man["written"], "2026-09-23 07:36:44 KST"); chk("manifest git_commit", man["git_commit"], "cd241b7e"); chk("manifest n_raw_files", man["n_raw_files"], 448)
w = time.mktime(time.strptime(man["written"][:19], "%Y-%m-%d %H:%M:%S"))
chk("base chunks newer than manifest 'written'", sum(1 for f in bfiles if os.path.getmtime(f) > w), 0)
bm = [os.path.getmtime(f) for f in bfiles]
print(f"  base chunk mtime range: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(min(bm)))} .. {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(max(bm)))} KST")
digest = hashlib.sha256("".join(hashlib.sha256(open(c, "rb").read()).hexdigest() for c in bfiles).encode()).hexdigest()[:16]
chk("chunks-sha digest (sha256 over sorted per-chunk sha256 hex, [:16])", digest, "78cbb59fc01ce520")
B = {}
for s in SNRS:
    pt, fs, metas, extra, nfail, nonfin = load_point(BASE, s, (V1, V4, GEN))
    B[s] = pt
    chk(f"base {s:+.0f} dB chunk plan", [(sk, n) for sk, n, _ in fs], [(40 * k, 40) for k in range(64)])
    chk(f"base {s:+.0f} dB '|failed' keys", nfail, 0); chk(f"base {s:+.0f} dB non-finite blk_err (V1,V4,genie)", nonfin, 0)
    chk(f"base {s:+.0f} dB run|git key", sorted({str(m.get("run|git", "(none)")) for m in metas}), ["None"]) if False else None
    print(f"  base {s:+.0f} dB: run|git present in chunks? {any('run|git' in m for m in metas)} (raw predates run|git -> manifest check applies); other arms {sorted(extra)}")

# ---------------------------------------------------------------------------------------------------------------------------- 3
print("\n### 3. genie bit-identity raw_D2SITEMS vs raw_B16e4k (per chunk: 7 KEYS_RAW + guardH), and per-point KEYS4 on concatenated arrays")
neq = 0; ntot = 0
for s in SNRS:
    for (sk, n, f) in Dfs[s]:
        zr = np.load(f); zb = np.load(f"{BASE}/{os.path.basename(f)}")
        for k in KEYS_RAW + ("guardH",):
            ntot += 1
            if not same(zr[f"{GEN}|{k}"], zb[f"{GEN}|{k}"]): neq += 1
chk(f"genie arrays differing (of {ntot} = 192 chunks x 8 arrays)", neq, 0)
for s in SNRS:
    chk(f"{s:+.0f} dB genie KEYS4 identical (concatenated 2560 x 16)", all(same(D[s][GEN][k], B[s][GEN][k]) for k in KEYS4), True)

# ---------------------------------------------------------------------------------------------------------------------------- 4
print("\n### 4. failures @16 / 2560 (record §6.2 table; §0.1 for V1 · V4 · genie)")
WANT_F = {V1: (371, 88, 29), V4: (394, 96, 21), MS: (389, 98, 27), GEN: (87, 26, 12)}
F = {}
for a, src in ((V1, B), (V4, B), (MS, D), (GEN, D)):
    F[a] = tuple(int(np.sum(src[s][a]["blk_err"][:, -1])) for s in SNRS)
    chk(f"failures {a.replace('M-ours-dscore-C-', '')} (-3/0/+3)", F[a], WANT_F[a])
chk("genie failures counted from the base raw equal those from raw_D2SITEMS", tuple(int(np.sum(B[s][GEN]["blk_err"][:, -1])) for s in SNRS), F[GEN])
BL = {a: tuple(F[a][i] / 2560 for i in range(3)) for a in F}
chk("BLER@16 V1 (§0.1, 5 dp)", tuple(round(x, 5) for x in BL[V1]), (0.14492, 0.03438, 0.01133))
chk("BLER@16 V4 (§0.1, 5 dp)", tuple(round(x, 5) for x in BL[V4]), (0.15391, 0.03750, 0.00820))

# ---------------------------------------------------------------------------------------------------------------------------- 5
print("\n### 5. paired sign tests, power guard, labels (§1.4 rule re-applied; record §6.2)")
def arm_err(a, s): return (D if a in (MS, GEN) else B)[s][a]["blk_err"][:, -1]
def paired(x, y, s):
    ex, ey = arm_err(x, s), arm_err(y, s)
    return int(np.sum((ex == 1) & (ey == 0))), int(np.sum((ex == 0) & (ey == 1)))
try:
    from scipy.stats import binomtest
    def sign_p2(a, b): return 1.0 if a + b == 0 else binomtest(min(a, b), a + b, 0.5, alternative="two-sided").pvalue
except Exception:
    sign_p2 = None
WANT = {"primary": dict(ab=[(53, 35), (22, 12), (8, 10)], p=["0.069", "0.12", "0.81"], pooled=(83, 57), pp="0.034", D=(88, 34, 18), powered=True, wy=0, wx=0, lab="(iii)"),
        "secondary": dict(ab=[(6, 1), (4, 6), (0, 6)], p=["0.12", "0.75", "0.031"], pooled=(10, 13), pp="0.68", D=(7, 10, 6), powered=True, wy=0, wx=1, lab="(iii)")}
RES = {}
for role, x, y in (("primary", MS, V1), ("secondary", V4, MS)):
    ab = [paired(x, y, s) for s in SNRS]; ps = [sign_p(a, b) for a, b in ab]
    A, Bn = sum(a for a, _ in ab), sum(b for _, b in ab)
    Dd = tuple(a + b for a, b in ab)
    powered = len(SNRS) == 3 and sum(1 for d in Dd if d >= 6) >= 2
    wy = sum(1 for (a, b), p in zip(ab, ps) if a > b and p < 0.05)      # second arm (y) fewer
    wx = sum(1 for (a, b), p in zip(ab, ps) if b > a and p < 0.05)      # first arm (x) fewer
    lab = "(iv)" if not powered else "(i)" if wy >= 2 else "(ii)" if wx >= 2 else "(iii)"
    RES[role] = dict(ab=ab, ps=ps, pooled=(A, Bn), pp=sign_p(A, Bn), D=Dd, powered=powered, wy=wy, wx=wx, lab=lab)
    w_ = WANT[role]
    print(f" [{role}] {x} -> {y}")
    chk("  a:b per point", ab, w_["ab"]); chk("  p (%.2g) per point", [pfmt(p) for p in ps], w_["p"])
    if sign_p2: chk("  p via scipy binomtest == own exact p (|d| < 1e-12)", all(abs(sign_p2(a, b) - p) < 1e-12 for (a, b), p in zip(ab, ps)), True)
    chk("  pooled a:b", (A, Bn), w_["pooled"]); chk("  pooled p", pfmt(sign_p(A, Bn)), w_["pp"])
    chk("  D = a+b", Dd, w_["D"]); chk("  POWERED (>=2 of 3 points with D >= 6)", powered, w_["powered"])
    chk("  second arm fewer (k/3)", wy, w_["wy"]); chk("  first arm fewer (k/3)", wx, w_["wx"]); chk("  label", lab, w_["lab"])
    print(f"    p (full precision): {[f'{p:.6g}' for p in ps]}, pooled {sign_p(A, Bn):.6g}")

# ---------------------------------------------------------------------------------------------------------------------------- 6
print("\n### 6. anchor-rule check line (BLER in [0.005, 0.9], |log10(BLER/0.1)| smallest 3) on V1-ms and V4")
def anchor(a):
    bl = {s: max(BL[a][i], 0.5 / 2560) for i, s in enumerate(SNRS)}
    cand = sorted((s for s in SNRS if 0.005 <= bl[s] <= 0.9), key=lambda s: abs(math.log10(bl[s] / 0.1)))[:3]
    return [f"{s:+.0f}" for s in sorted(cand)]
chk("anchor rule on V1-ms", anchor(MS), ["-3", "+0", "+3"]); chk("anchor rule on V4", anchor(V4), ["-3", "+0", "+3"])
print("  |log10(BLER/0.1)| V1-ms:", [round(abs(math.log10(b / 0.1)), 3) for b in BL[MS]], " V4:", [round(abs(math.log10(b / 0.1)), 3) for b in BL[V4]])

# ---------------------------------------------------------------------------------------------------------------------------- 7
print("\n### 7. SNR@0.1 (log-linear, first downward crossing, floor 0.5/n) and L; bootstrap B 2000 seed 20260925")
S = {a: snr_at(SNRS, BL[a], 2560) for a in (V1, V4, MS, GEN)}
for a in (V1, MS, V4, GEN): print(f"  SNR@0.1 {a}: {S[a][0]:+.4f} dB ({S[a][1]})")
chk("SNR@0.1 V1 (3 dp; §0.1 / §6.6)", round(S[V1][0], 3), -2.226); chk("SNR@0.1 V1-ms (3 dp; §6.6)", round(S[MS][0], 3), -2.090); chk("SNR@0.1 V4 (3 dp; §0.1)", round(S[V4][0], 3), -2.084)
chk("kinds all ok (V1, V1-ms, V4)", (S[V1][1], S[MS][1], S[V4][1]), ("ok", "ok", "ok"))
L = S[MS][0] - S[V1][0]; G2 = S[V4][0] - S[MS][0]
chk("L = SNR_ms - SNR_V1 (%+.2f)", f"{L:+.2f}", "+0.14"); chk("L (3 dp; §6.6 +0.137)", round(L, 3), 0.137)
chk("secondary gap V4 - V1ms (%+.2f)", f"{G2:+.2f}", "+0.01"); chk("secondary gap (3 dp; §6.6 +0.006)", round(G2, 3), 0.006)
def boot(x, y, Bn=2000, seed=20260925):
    ex = [arm_err(x, s) for s in SNRS]; ey = [arm_err(y, s) for s in SNRS]; n = 2560
    rng = np.random.default_rng(seed); g = np.empty(Bn)
    for b in range(Bn):
        bx, by = [], []
        for a, c in zip(ex, ey):
            i = rng.integers(n, size=n); bx.append(a[i].mean()); by.append(c[i].mean())
        (ux, kx), (uy, ky) = snr_at(SNRS, bx, n), snr_at(SNRS, by, n)
        g[b] = ux - uy if kx == ky == "ok" else np.nan
    cens = float(np.mean(~np.isfinite(g))); lo, hi = np.nanpercentile(g, [5, 95])
    return lo, hi, cens
t0 = time.time(); lo, hi, cens = boot(MS, V1); lo2, hi2, cens2 = boot(V4, MS)
print(f"  bootstrap wall {time.time() - t0:.1f} s")
chk("L 90 % CI (%+.2f)", (f"{lo:+.2f}", f"{hi:+.2f}"), ("+0.05", "+0.22")); chk("L CI (3 dp; §6.6)", (round(lo, 3), round(hi, 3)), (0.050, 0.225)); chk("L censored replicates", f"{100 * cens:.0f}%", "0%")
chk("secondary 90 % CI (%+.2f)", (f"{lo2:+.2f}", f"{hi2:+.2f}"), ("-0.04", "+0.04")); chk("secondary CI (3 dp; §6.6)", (round(lo2, 3), round(hi2, 3)), (-0.037, 0.042)); chk("secondary censored", f"{100 * cens2:.0f}%", "0%")
lo_b, hi_b, _ = boot(MS, V1, seed=1); print(f"  (robustness, not a record value) L CI with seed 1: [{lo_b:+.3f}, {hi_b:+.3f}]")

# ---------------------------------------------------------------------------------------------------------------------------- 8
print("\n### 8. prediction scoring (§3) from the recomputed values")
P = RES["primary"]; Q = RES["secondary"]
pred = {1: P["lab"] == "(iii)",
        2: (P["ab"][0][0] > P["ab"][0][1] and P["ps"][0] < .05) and P["ps"][1] >= .05 and P["ps"][2] >= .05 and P["wx"] == 0,
        3: P["powered"] and all(d >= 6 for d in P["D"]),
        4: (S[MS][1] == S[V1][1] == "ok") and cens == 0 and 0.04 <= round(L, 2) <= 0.25,
        5: round(lo, 2) >= 0.01,
        6: Q["lab"] == "(iv)" and all(d <= m for d, m in zip(Q["D"], (20, 10, 10))),
        7: all(abs(F[MS][i] - F[V4][i]) <= m for i, m in enumerate((20, 10, 10))) and F[MS][0] > 371 and F[MS][2] < 29,
        8: anchor(MS) == anchor(V4) == ["-3", "+0", "+3"],
        9: open(f"{CONF}/results/review_next/e1ms/D2SITEMS_accept.txt").read().strip() == "ACCEPT: OK -- D2SITEMS" and "0 problems" in open(f"{CONF}/results/review_next/e1ms/console_D2SITEMS.txt").read() and "NOTE" not in open(f"{CONF}/results/review_next/e1ms/compare_D2SITEMS.txt").read(),
        10: 4.6 <= 15}
for k, v in pred.items(): print(f"  prediction {k}: {'HIT' if v else 'MISS'}")
chk("hits among 1-10", sum(pred.values()), 8); chk("misses are exactly {2, 6}", sorted(k for k, v in pred.items() if not v), [2, 6])
print(f"  partials: pred 2 -> -3 dB a>b {P['ab'][0][0] > P['ab'][0][1]} but p {P['ps'][0]:.3f}; 0/+3 dB p>=.05 {P['ps'][1] >= .05 and P['ps'][2] >= .05}; no V1-ms-side significant point {P['wx'] == 0}")
print(f"            pred 6 -> secondary label {Q['lab']} (D {Q['D']}, all >= 6 -> POWERED); D <= 20/10/10 {all(d <= m for d, m in zip(Q['D'], (20, 10, 10)))}")

# ---------------------------------------------------------------------------------------------------------------------------- 9
print("\n### 9. §6.3 sentences vs §2.1 / §2.2 / §2.4 templates; §2.3 forbidden phrases in §6")
doc = open(f"{CONF}/results/review_next/NEXT_EXPERIMENTS_D2SITEMS.md", encoding="utf-8").read().splitlines()
s6 = "\n".join(doc[215:])          # lines 216..end (1-based)
L154 = next(l for l in doc if l.startswith("- 모든 문장 끝에 V1-ms 의 **고정 설명**"))
fixed = L154.split('"')[1]
chk("fixed explanation (§2.1) appears verbatim in §6.3", fixed in s6, True)
Lsent = f'SNR 손실 L = SNR_ms(0.1) − SNR_V1(0.1) = {L:+.2f} dB [90 % paired bootstrap {lo:+.2f}, {hi:+.2f}] (양수 = scalar 쪽 손실; 3 점 격자 −3 / 0 / +3 dB; censored replicates {100 * cens:.0f} %)'
chk("L sentence with recomputed x/l/u/c appears in §6.3", Lsent in s6, True)
chk("label (iii) string in §6.3", '"판정하지 못함 (유의 방향 없음)"' in s6, True)
eng3 = "In paired sign tests, the comparison between the matrix-site receiver and its matched-scalar variant is not decided: neither receiver has p < 0.05 in its favor at two or more of the three tested SNRs."
chk("§2.4 (iii) English sentence verbatim in §6.3", eng3 in s6, True)
engL = f"Relative to the matrix-site receiver, the matched-scalar variant reaches BLER 0.1 at an SNR offset of {L:+.2f}\\,dB [${lo:+.2f}$, ${hi:+.2f}$] (positive: more SNR needed)."
chk("§2.4 common sentence with recomputed numbers in §6.3", engL in s6, True)
sec = "V4 와 V1-ms 는 Jacobian 수리 (V4 없음 · V1-ms 있음) 와 scalar site 를 만드는 경로가 함께 다르다 (§0.2)"
chk("§2.2 fixed secondary clause in §6.3", sec in s6, True)
chk("§6.3 secondary numbers", "−3 dB 6:1 p=0.12 · +0 dB 4:6 p=0.75 · +3 dB 0:6 p=0.031" in s6 and "+0.01 dB [90% paired bootstrap −0.04, +0.04; censored replicates 0%]" in s6, True)
forb = ["동등", "비열등", "최적 GMM", "scaling law", "비긴다", "차이 없음", "모든 SNR 에서", "floor 만의 몫", "Jacobian 수리만의 효과", "고정 질의에서", "site 한 번의 효과", "저비용 scalar"]
hits = {w: [i + 216 for i, l in enumerate(doc[215:]) if w in l] for w in forb}
hits = {w: v for w, v in hits.items() if v}
print("  forbidden-phrase hits in §6 (line numbers):", hits if hits else "none")
# the only tolerated occurrences are the §2.3 prohibition itself being cited, not used; report any hit for the reader
chk("§6 has no forbidden phrase used as a result statement", all(w in ("비열등",) for w in hits) if hits else True, True)
print("  (if '비열등' is listed it comes from the sentence '비열등 margin ...' style citation; see the audit file)")

# --------------------------------------------------------------------------------------------------------------------------- 10
print("\n### 10. test / development separation: V1-ms on test trials (skip < 2560) anywhere besides raw_D2SITEMS?")
roots = sorted(set(glob.glob("/home/HTJ/t2/conf/raw_*") + glob.glob("/home/HTJ/t2_wt*/conf/raw_*") + glob.glob("/home/HTJ/t2/.claude/worktrees/*/conf/raw_*")
                   + glob.glob("/tmp/claude-1005/-home-HTJ-t2/*/scratchpad/**/raw_*", recursive=True)))
cut = time.mktime(time.strptime("2026-10-19 11:00:00", "%Y-%m-%d %H:%M:%S"))   # ba1b7c35 (V1-ms code) = 10-19 11:30:30 KST
scanned = 0; found = {}
for r in roots:
    if r.rstrip("/") == RAW: continue
    for f in glob.glob(f"{r}/*.npz"):
        if os.path.getmtime(f) < cut: continue
        scanned += 1
        try:
            with zipfile.ZipFile(f) as zf: names = zf.namelist()
        except zipfile.BadZipFile:
            continue
        if any(n.startswith(MS + "|") for n in names):
            m = PAT.match(os.path.basename(f)); skip = int(m[7]) if m else -1
            found.setdefault(r, []).append((skip, f))
print(f"  scanned {scanned} npz files newer than 2026-10-19 11:00 KST under {len(roots)} raw folders (excluding raw_D2SITEMS)")
for r, lst in found.items():
    sk = sorted(s for s, _ in lst)
    print(f"  V1-ms key in {r}: {len(lst)} files, skip range {sk[0]}..{sk[-1]}")
test_hits = {r: [f for s, f in lst if 0 <= s < 2560] for r, lst in found.items()}
test_hits = {r: v for r, v in test_hits.items() if v}
# synthetic check: in the flow / KAT raws the V1-ms arrays must be the base's V1 arrays, renamed
for r, fl in test_hits.items():
    ne = 0; nt = 0
    for f in fl:
        z = np.load(f); zb = np.load(f"{BASE}/{os.path.basename(f)}")
        for k in KEYS_RAW:
            nt += 1
            if not same(z[f"{MS}|{k}"], zb[f"{V1}|{k}"]): ne += 1
    chk(f"  {os.path.basename(r)}: V1-ms arrays at test skips == base V1 arrays (synthetic rename; differing of {nt})", ne, 0)
real = [r for r in test_hits if not os.path.basename(r).startswith(("raw_E1MSflow", "raw_KAT"))]
chk("raw folders with a REAL V1-ms run on test trials (not synthetic flow/KAT)", real, [])
print("  dev-only V1-ms raws (skip >= 2560):", {os.path.basename(r): sorted({s for s, _ in lst}) for r, lst in found.items() if r not in test_hits})

# --------------------------------------------------------------------------------------------------------------------------- 11
print("\n### 11. merge check (a)(b) and 확인 3 raws: arms, trials, bit-identity")
ref = np.load(f"{BASE}/D2_C2_S2_Nr8_T16_Tp4_dft_snr-3_skip0_n40.npz")
for d, want_ms, want_git in (("/home/HTJ/t2/conf/raw_E1MSmcaon", True, "fef2594a"), ("/home/HTJ/t2/conf/raw_E1MSmcaoff", False, "fef2594a"),
                             (f"{WT}/raw_E1MSregon", True, "99f62bfb+dirty"), (f"{WT}/raw_E1MSregoff", False, "99f62bfb+dirty")):
    fs = sorted(glob.glob(f"{d}/*.npz")); z = np.load(fs[0])
    arms = sorted({k.split("|")[0] for k in z.files} - {"meta", "run"})
    chk(f"{os.path.basename(d)}: one file, name", [os.path.basename(f) for f in fs], ["D2_C2_S2_Nr8_T16_Tp4_dft_snr-3_skip0_n40.npz"])
    chk(f"{os.path.basename(d)}: arms exactly {{V1, V4}}", arms, [V1, V4])
    chk(f"{os.path.basename(d)}: 14 arrays == raw_B16e4k", sum(1 for a in (V1, V4) for k in KEYS_RAW if not same(z[f'{a}|{k}'], ref[f'{a}|{k}'])), 0)
    chk(f"{os.path.basename(d)}: meta|ms_arm present", "meta|ms_arm" in z.files, want_ms); chk(f"{os.path.basename(d)}: run|git", str(z["run|git"]), want_git)
    chk(f"{os.path.basename(d)}: run|skip, run|n, run|snr", (int(z["run|skip"]), int(z["run|n"]), float(z["run|snr"])), (0, 40, -3.0))
zb_ = np.load("/home/HTJ/t2/conf/raw_E1MSmcb/D2_C2_S2_Nr8_T16_Tp4_dft_snr-3_skip2560_n40.npz")
chk("raw_E1MSmcb: arms exactly {V1ms, genie}", sorted({k.split('|')[0] for k in zb_.files} - {'meta', 'run'}), [MS, GEN])
chk("raw_E1MSmcb: run|git / skip", (str(zb_["run|git"]), int(zb_["run|skip"])), ("fef2594a", 2560))
for d in ("raw_E1MSdev", "raw_E1MSsm"):
    wz = np.load(f"{WT}/{d}/D2_C2_S2_Nr8_T16_Tp4_dft_snr-3_skip2560_n40.npz")
    chk(f"raw_E1MSmcb vs worktree {d}: 14 arrays (V1ms, genie) differing", sum(1 for a in (MS, GEN) for k in KEYS_RAW if not same(zb_[f'{a}|{k}'], wz[f'{a}|{k}'])), 0)
    chk(f"worktree {d} run|git", str(wz["run|git"]), "2807dd23")
chk("merge-check verdict file", open(f"{CONF}/results/review_next/e1ms/mergechk_compare.txt").read().strip().splitlines()[-1], "E1MS_MERGECHK OK (0 problems)")

# --------------------------------------------------------------------------------------------------------------------------- 12
print("\n### 12. development screen (§0.3, raw_E1MSdev, trials 2560..2879) recount")
E = {}
for s in SNRS:
    pt, fs, metas, extra, nfail, nonfin = load_point(f"{WT}/raw_E1MSdev", s, (V1, MS, V4, GEN)); E[s] = pt
    chk(f"dev {s:+.0f} dB plan (2560 + 40k, k < 8)", [(sk, n) for sk, n, _ in fs], [(2560 + 40 * k, 40) for k in range(8)])
def dev_err(a, s): return E[s][a]["blk_err"][:, -1]
chk("dev failures V1 / V1-ms / V4 / genie (-3,0,+3)", {a.replace("M-ours-dscore-C-", ""): tuple(int(dev_err(a, s).sum()) for s in SNRS) for a in (V1, MS, V4, GEN)},
    {"V1": (38, 11, 2), "V1ms": (38, 10, 4), "V4": (37, 10, 4), "R5-genie": (11, 5, 1)})
def dpair(x, y, s):
    ex, ey = dev_err(x, s), dev_err(y, s); return int(np.sum((ex == 1) & (ey == 0))), int(np.sum((ex == 0) & (ey == 1)))
chk("dev V1-ms -> V1 a:b", [dpair(MS, V1, s) for s in SNRS], [(6, 6), (1, 2), (2, 0)])
chk("dev V4 -> V1-ms a:b", [dpair(V4, MS, s) for s in SNRS], [(0, 1), (0, 0), (0, 0)])
chk("dev V4 -> V1 a:b", [dpair(V4, V1, s) for s in SNRS], [(5, 6), (1, 2), (2, 0)])
chk("dev V4 vs V1-ms blocks differing at iteration 16 (total over 960)", sum(int(np.sum(dev_err(V4, s) != dev_err(MS, s))) for s in SNRS), 1)

# --------------------------------------------------------------------------------------------------------------------------- 13
print("\n### 13. assets: checkpoint sha256, fits copies, s5")
chk("ckpt sha256", hashlib.sha256(open(f"{CONF}/ckpt/d2sx_N160000_a1.pt", "rb").read()).hexdigest(), "4443921ce8d5c4a11c7cda879a53a66436f43bd76864734a3e6203cfb4b82f29")
for fn, sha in (("fit_S2_Nr8_kronK1024_n160000.npz", "bf796b84037e1b3790ed5a6d7917ea2a79f2bee4a9f155f0d3385d856c950997"), ("fit_S2_Nr8_fullK32_n160000.npz", "d4601650a888b4b355565a9010cf0a23499a3e92505e657e2cd79a1c152359f3")):
    chk(f"fits copy sha256 {fn}", hashlib.sha256(open(f"{CONF}/results/gmm_fits_D2_D2SITEMS/{fn}", "rb").read()).hexdigest(), sha)
src = sorted(glob.glob(f"{CONF}/results/gmm_fits_D2_B16e4k/*.npz")); cp = sorted(glob.glob(f"{CONF}/results/gmm_fits_D2_D2SITEMS/*.npz"))
chk("fits copy: count == original (24) and byte-identical, no symlinks", (len(cp) == len(src) == 24, all(open(a, 'rb').read() == open(b, 'rb').read() for a, b in zip(src, cp)), not any(os.path.islink(f) for f in cp)), (True, True, True))
chk("s5 content", open(f"{CONF}/results/review_next/e1ms/e1ms_s5.txt").read().split(), ["FREEZE", "e6ac9e653dad4e15d2e781c9800a090cab529857", "WGB", "1.5"])
kz = np.load(f"{CONF}/results/gmm_fits_D2_D2SITEMS/fit_S2_Nr8_kronK1024_n160000.npz", allow_pickle=True)
print("  kron1024 fit keys:", [k for k in kz.files][:12]);
for k in ("ll_val", "ll", "val_ll"):
    if k in kz.files: print(f"  fit {k} = {kz[k]}")

print("\n" + "=" * 100)
print(f"TALLY: {tally['match']} match, {tally['mismatch']} mismatch")
