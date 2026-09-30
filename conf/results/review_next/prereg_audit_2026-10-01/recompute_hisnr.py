"""prereg_audit_2026-10-01/recompute_hisnr.py -- Fable record audit of NEXT_EXPERIMENTS_HISNR16e4 §6.1 (+ EXPERIMENTS row,
DECISIONS line).  Read-only: raw npz (via analysis.load_raw), the report / genie_floor / accept / manifest files, the three
documents.  Everything is recomputed here (Wilson, discordant counts, exact sign p, genie L aggregation) and compared with
the document values that are PARSED from the markdown, not typed in.  CPU single process, no receiver.
    CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=2 ~/miniforge3/envs/torch/bin/python recompute_hisnr.py
"""
import glob
import json
import math
import os
import re
import sys

CONF = "/home/HTJ/t2/conf"
sys.path.insert(0, os.path.join(CONF, "code"))
import numpy as np                       # noqa: E402
from analysis import load_raw            # noqa: E402  (raw reading only)

RN = os.path.join(CONF, "results/review_next")
REG = os.path.join(RN, "NEXT_EXPERIMENTS_HISNR16e4.md")
EXP = "/home/HTJ/t2/docs/EXPERIMENTS.md"
DEC = os.path.join(CONF, "DECISIONS.md")
SNRS = (6, 9, 12, 15)
ARMS = ("M-ours-dscore-C-V1", "M-ours-bstar", "R2-ours-G", "R1-turbo", "R3-bigamp", "R5-genie")
TAGS = {"HSB16e4k": ("C2", "raw_B16e4k", 1024, -11.459169831224418, "4443921ce8d5c4a1", "legacy-last"),
        "HSNR16": ("C6", "raw_NR16B16e4", 4096, 63.1751571838059, "c050d611b2c714a6", "best")}
Z = 1.959963984540054
MIS = []


def chk(name, got, want):
    ok = got == want
    if not ok:
        MIS.append(f"{name}: got {got!r} want {want!r}")
    print(f"  [{'ok' if ok else 'MISMATCH'}] {name}: {got!r}" + ("" if ok else f"  (doc: {want!r})"))
    return ok


def wilson(k, n, z=Z):
    """Wilson score interval, written from the textbook form (not imported)."""
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = (z / den) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return centre - half, centre + half


def sign_exact_two_sided(a, b):
    """Exact two-sided binomial sign test, p0 = 0.5, statistic min(a, b)."""
    n = a + b
    if n == 0:
        return 1.0
    k = min(a, b)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / 2.0 ** n
    return min(1.0, 2 * tail)


def fails16(v):
    e = np.asarray(v, float)[:, -1]
    nonfin = int((~np.isfinite(e)).sum())
    return int(np.where(np.isfinite(e), e, 1.0).sum()), nonfin


# ----------------------------------------------------------------------------- 1. raw integrity (new tags)
print("=" * 100 + "\n1. RAW INTEGRITY (raw_HSB16e4k, raw_HSNR16)")
raw = {}
for tag, (cell, _, kK, ll, sha, role) in TAGS.items():
    root = os.path.join(CONF, "raw_" + tag)
    files = sorted(glob.glob(os.path.join(root, "D2_*.npz")))
    gits, iters, skips, failed_keys, nonfin_any, meta_bad = set(), set(), {}, 0, 0, []
    for f in files:
        z = np.load(f)
        gits.add(str(z["run|git"])); iters.add(int(z["run|iters"]))
        m = re.search(r"snr(-?\d+)_skip(\d+)_n(\d+)\.npz$", f)
        skips.setdefault(int(m[1]), []).append((int(m[2]), int(m[3])))
        failed_keys += sum(1 for k in z.files if k.endswith("|failed"))
        for k in z.files:
            if k.endswith("|blk_err") and k.split("|")[0] in ARMS:
                nonfin_any += int((~np.isfinite(np.asarray(z[k], float))).sum())
        g = lambda k: str(z[k].item() if z[k].shape == () else z[k])
        if (int(float(g("meta|ntrain"))) != 160000 or g("meta|bstar") != "kron" or int(float(g("meta|kron_K"))) != kK
                or abs(float(g("meta|ll_val|kron")) - ll) > 1e-9 or f"sha256[:16]={sha}" not in g("meta|stagec_ckpt_id")
                or f"role={role}" not in g("meta|stagec_ckpt_id") or int(z["run|seed"]) != 20260926):
            meta_bad.append(os.path.basename(f))
    print(f"{tag}: files {len(files)}, run|git {sorted(gits)}, run|iters {sorted(iters)}, '<arm>|failed' keys {failed_keys}, "
          f"non-finite blk_err (all 16 iters, 6 arms) {nonfin_any}, meta/ckpt/seed mismatches {len(meta_bad)}")
    chk(f"{tag} n files", len(files), 2048); chk(f"{tag} run|git", sorted(gits), ["6b1de688"]); chk(f"{tag} iters", sorted(iters), [16])
    chk(f"{tag} failed keys", failed_keys, 0); chk(f"{tag} nonfinite", nonfin_any, 0); chk(f"{tag} meta bad", len(meta_bad), 0)
    for s in SNRS:
        chk(f"{tag} snr{s} chunks", sorted(skips[s]), [(10000 + 40 * k, 40) for k in range(512)])
    d, meta, warns = load_raw("D2", root=root)
    chk(f"{tag} load_raw warnings", len(warns), 0)
    raw[tag] = d

# ----------------------------------------------------------------------------- 2. report tables recomputed
print("=" * 100 + "\n2. REPORT TABLES (failures / n, BLER, Wilson, paired discordant, exact sign p) vs hisnr_<TAG>.txt AND §6.1")
reg = open(REG, encoding="utf-8").read()
sec61 = reg[reg.index("### 6.1"):]
# parse the report txt
def parse_report(path):
    out, snr = {}, None
    for ln in open(path, encoding="utf-8"):
        m = re.match(r"SNR ([+-]\d+) dB, n = (\d+):", ln)
        if m:
            snr = int(m[1]); out[snr] = {"n": int(m[2])}; continue
        m = re.match(r"\s+(\S+)\s+(\d+) / (\d+)\s+BLER (\S+)\s+95% \[(\S+), (\S+)\]", ln)
        if m:
            out[snr][m[1]] = (int(m[2]), int(m[3]), m[4], m[5], m[6]); continue
        m = re.match(r"\s+paired b\* only : V1 only = (\d+):(\d+), exact two-sided sign p = (\S+) \(report\)", ln)
        if m:
            out[snr]["paired"] = (int(m[1]), int(m[2]), m[3])
    return out

# parse the §6.1 report table (markdown) for one cell block
def parse_md_report(block):
    out = {s: {} for s in SNRS}
    for ln in block.splitlines():
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) != 5:
            continue
        arm = cells[0].replace("\\*", "*")
        if arm in ARMS:
            for s, c in zip(SNRS, cells[1:]):
                m = re.match(r"(\d+) / (\d+) · (\S+) \[(\S+), (\S+)\]", c)
                out[s][arm] = (int(m[1]), int(m[2]), m[3], m[4], m[5])
        elif arm.startswith("짝지음"):
            for s, c in zip(SNRS, cells[1:]):
                m = re.match(r"(\d+):(\d+) · p = (\S+)", c)
                out[s]["paired"] = (int(m[1]), int(m[2]), m[3])
    return out

blocks = {"HSB16e4k": sec61[sec61.index("**D2 C2 (HSB16e4k)**"):sec61.index("**D2 C6 (HSNR16)**")],
          "HSNR16": sec61[sec61.index("**D2 C6 (HSNR16)**"):sec61.index("**원 태그 (n = 2560) 와 나란히")]}
computed = {}
for tag, (cell, *_) in TAGS.items():
    rep = parse_report(os.path.join(RN, f"hisnr_{tag}.txt")); md = parse_md_report(blocks[tag]); d = raw[tag]
    computed[tag] = {}
    for s in SNRS:
        pt = d[(cell, "S2", float(s))]; n = len(np.asarray(pt[ARMS[0]]["blk_err"]))
        chk(f"{tag} +{s} n", n, 20480)
        computed[tag][s] = {}
        for arm in ARMS:
            f, nf = fails16(pt[arm]["blk_err"]); lo, hi = wilson(f, n)
            mine = (f, n, f"{f / n:.2e}", f"{lo:.2e}", f"{hi:.2e}")
            computed[tag][s][arm] = f
            chk(f"{tag} +{s} {arm} vs txt", mine, rep[s][arm]); chk(f"{tag} +{s} {arm} vs §6.1", mine, md[s][arm])
        b = np.asarray(pt["M-ours-bstar"]["blk_err"], float)[:, -1]; v = np.asarray(pt["M-ours-dscore-C-V1"]["blk_err"], float)[:, -1]
        b = np.where(np.isfinite(b), b, 1.0) > 0; v = np.where(np.isfinite(v), v, 1.0) > 0
        a_, b_ = int((b & ~v).sum()), int((v & ~b).sum()); p = sign_exact_two_sided(a_, b_)
        mine = (a_, b_, f"{p:.2g}"); computed[tag][s]["paired"] = (a_, b_, p)
        chk(f"{tag} +{s} paired vs txt", mine, rep[s]["paired"]); chk(f"{tag} +{s} paired vs §6.1", mine, md[s]["paired"])
        try:
            from scipy.stats import binomtest
            chk(f"{tag} +{s} sign p (scipy)", f"{binomtest(min(a_, b_), a_ + b_, 0.5).pvalue:.2g}", f"{p:.2g}")
        except ImportError:
            print("  (scipy absent: math.comb only)")

# ----------------------------------------------------------------------------- 3. original tags (n = 2560) and prediction 3
print("=" * 100 + "\n3. ORIGINAL TAGS (raw_B16e4k / raw_NR16B16e4, n = 2560) + prediction 3 + registration header expected counts")
side = sec61[sec61.index("**원 태그 (n = 2560) 와 나란히"):sec61.index("**genie 바닥**")]
md_side = {}
for ln in side.splitlines():
    c = [x.strip() for x in ln.strip().strip("|").split("|")]
    if len(c) == 6 and c[0] in ("C2", "C6"):
        m1 = re.match(r"(\d+) · (\S+) \[(\S+), (\S+)\]", c[3]); m2 = re.match(r"(\d+) · (\S+) \[(\S+), (\S+)\]", c[4])
        md_side[(c[0], int(c[1]), c[2].replace("\\*", "*"))] = ((int(m1[1]), m1[2], m1[3], m1[4]), (int(m2[1]), m2[2], m2[3], m2[4]), c[5])
chk("side-by-side rows parsed", len(md_side), 16)
header_expect = {("C2", "V1"): (128, 56, 40, 24), ("C6", "V1"): (48, 16, 16, 16), ("C2", "b*"): (224, 136, 128, 64),
                 ("C6", "b*"): (176, 112, 80, 40), ("C2", "genie"): (72, 16, 16, 16), ("C6", "genie"): (48, 8, 16, 0)}
inside, mind = 0, []
orig = {}
for tag, (cell, oraw, *_) in TAGS.items():
    d0, _, w0 = load_raw("D2", root=os.path.join(CONF, oraw)); chk(f"{oraw} load_raw warnings", len(w0), 0)
    for lab, arm in (("V1", "M-ours-dscore-C-V1"), ("b*", "M-ours-bstar"), ("genie", "R5-genie")):
        fs = []
        for s in SNRS:
            pt = d0[(cell, "S2", float(s))]; n0 = len(np.asarray(pt[arm]["blk_err"])); chk(f"{oraw} +{s} n", n0, 2560)
            f0, nf0 = fails16(pt[arm]["blk_err"]); lo0, hi0 = wilson(f0, n0); fs.append(f0); orig[(cell, s, lab)] = (f0, n0, lo0, hi0, nf0)
            if lab != "genie":
                f1 = computed[tag][s][arm]; p1 = f1 / 20480; lo1, hi1 = wilson(f1, 20480)
                mine = ((f0, f"{f0 / n0:.2e}", f"{lo0:.2e}", f"{hi0:.2e}"), (f1, f"{p1:.2e}", f"{lo1:.2e}", f"{hi1:.2e}"), "예" if lo0 <= p1 <= hi0 else "아니오")
                chk(f"side {cell} +{s} {lab}", mine, md_side[(cell, s, lab)])
                inside += lo0 <= p1 <= hi0; mind.append((min(p1 - lo0, hi0 - p1), cell, s, lab, p1, lo0, hi0))
        chk(f"header expected failures {cell} {lab} (= orig x 8)", tuple(8 * x for x in fs), header_expect[(cell, lab)])
        print(f"    {oraw} {lab}: failures +6/+9/+12/+15 = {fs}, non-finite@16 = {[orig[(cell, s, lab)][4] for s in SNRS]}")
chk("prediction 3 inside count", inside, 16)
mind.sort(); m = mind[0]
print(f"    smallest distance to an original interval end: {m[1]} +{m[2]} {m[3]}: point {m[4]:.4e}, orig [{m[5]:.4e}, {m[6]:.4e}], dist {m[0]:.3e}")
chk("closest cell", (m[1], m[2], m[3], f"{m[4]:.3e}", f"{m[5]:.3e}"), ("C2", 12, "b*", "3.955e-03", "3.851e-03"))
print("    next three:", [(x[1], x[2], x[3], f"{x[0]:.2e}") for x in mind[1:4]])
# original-tag genie +9..+15 (registration header: 6 failures, all L = 3 -- L not recomputed here, count only)
chk("orig C2 genie +9..+15 failures (header: 6)", sum(orig[("C2", s, "genie")][0] for s in (9, 12, 15)), 6)

# ----------------------------------------------------------------------------- 4. genie floor files
print("=" * 100 + "\n4. GENIE FLOOR (genie_floor_raw_<TAG>.txt): fail list vs raw genie failures; per-SNR L aggregation vs §6.1; L table sums")
gblock = sec61[sec61.index("**genie 바닥**"):sec61.index("**§3 예측 채점**")]
gcol = {"HSB16e4k": 1, "HSNR16": 2}
grows = {}
for ln in gblock.splitlines():
    c = [x.strip() for x in ln.strip().strip("|").split("|")]
    if len(c) == 3:
        grows[c[0]] = c[1:]
for tag, (cell, *_) in TAGS.items():
    txt = open(os.path.join(RN, "genie_floor", f"genie_floor_raw_{tag}.txt"), encoding="utf-8").read().splitlines()
    head = re.match(r"# genie_floor raw_(\S+) S2 (C\d) SNR \[6, 9, 12, 15\]: trials (\d+), genie failures (\d+)", txt[0])
    chk(f"{tag} genie header", (head[1], head[2]), (tag, cell))
    fl = [re.match(r"\s+fail snr ([+-]\d+) trial (\d+) L=(\d) cond=(\S+) smin=(\S+) \|H\|\^2=(\S+)", l) for l in txt[11:]]
    assert all(fl), "unparsed fail line"
    fl = [(int(m[1]), int(m[2]), int(m[3])) for m in fl]
    chk(f"{tag} genie total failures (header)", int(head[4]), len(fl)); chk(f"{tag} trials (header)", int(head[3]), 81920)
    # fail list == raw genie failures at iteration 16 (trial index = 10000 + row)
    d = raw[tag]
    for s in SNRS:
        e = np.asarray(d[(cell, "S2", float(s))]["R5-genie"]["blk_err"], float)[:, -1]; e = np.where(np.isfinite(e), e, 1.0)
        chk(f"{tag} +{s} fail-list trials == raw genie failures", sorted(t for ss, t, _ in fl if ss == s), sorted(int(i) + 10000 for i in np.flatnonzero(e > 0)))
        chk(f"{tag} +{s} genie count list vs report", sum(1 for ss, _, _ in fl if ss == s), computed[tag][s]["R5-genie"])
    # per-SNR L aggregation -> §6.1 "SNR 별 실패 (L)" cell
    parts = []
    for s in SNRS:
        Ls = {}
        for ss, _, L in fl:
            if ss == s:
                Ls[L] = Ls.get(L, 0) + 1
        parts.append(f"+{s}: {sum(Ls.values())} (" + ", ".join(f"L{L} {Ls[L]}" for L in sorted(Ls)) + ")")
    chk(f"{tag} per-SNR L cell", "; ".join(parts), grows["SNR 별 실패 (L)"][gcol[tag] - 1])
    # L table lines 5-10 vs §6.1 rows and vs the fail-list totals per L
    Ltot = {}
    for _, _, L in fl:
        Ltot[L] = Ltot.get(L, 0) + 1
    trials_sum = 0
    for L in range(3, 9):
        m = re.match(rf"  L={L}: trials (\d+), genie failures\s+(\d+) \((\S+)\)", txt[L + 1]); assert m
        trials_sum += int(m[1])
        chk(f"{tag} L={L} failures file vs fail list", int(m[2]), Ltot.get(L, 0))
        chk(f"{tag} L={L} rate", m[3], f"{int(m[2]) / int(m[1]):.4f}")
        key = "L=3 시행 · 실패 (비율)" if L == 3 else f"L={L}"
        chk(f"{tag} L={L} §6.1 row", grows[key][gcol[tag] - 1], f"{m[1]} · {int(m[2])} ({m[3]})")
    chk(f"{tag} L trials sum", trials_sum, 81920)
    chk(f"{tag} §6.1 trials·failures row", grows["시행 · genie 실패 (4 SNR 합)"][gcol[tag] - 1], f"{head[3]} · {head[4]}")
    # cond / sigma_min / ||H||^2 / p95 rows: string transcription check against the file
    q = lambda l: re.match(r"  \S+\s+failed: median (\S+) \[p10 (\S+), p90 (\S+)\] \| ok: median (\S+) \[p10 (\S+), p90 (\S+)\]", l)
    for key, li in (("cond(H) 실패 / 성공: 중앙값 [p10, p90]", 1), ("sigma_min(H) 실패 / 성공", 2), ("‖H‖_F² 실패 / 성공", 3)):
        m = q(txt[li]); want = f"{m[1]} [{m[2]}, {m[3]}] / {m[4]} [{m[5]}, {m[6]}]"
        chk(f"{tag} {key}", grows[key][gcol[tag] - 1], want)
    m = re.match(r"  genie failure rate: cond\(H\) >= p95 \((\S+)\) (\S+) vs below (\S+)", txt[10])
    chk(f"{tag} p95 row", grows["genie 실패율 cond(H) ≥ p95 / 미만"][gcol[tag] - 1], f"{m[2]} / {m[3]} (p95 = {m[1]})")
    if tag == "HSB16e4k":
        l3 = {s: sum(1 for ss, _, L in fl if ss == s and L == 3) for s in SNRS}; tot = {s: sum(1 for ss, _, _ in fl if ss == s) for s in SNRS}
        print(f"    prediction 1: genie failures +9/+12/+15 = {tot[9]}/{tot[12]}/{tot[15]}; L=3 among them {l3[9]}/{tot[9]}, {l3[12]}/{tot[12]}, {l3[15]}/{tot[15]}; "
              f"pooled {l3[9] + l3[12] + l3[15]}/{tot[9] + tot[12] + tot[15]} = {100 * (l3[9] + l3[12] + l3[15]) / (tot[9] + tot[12] + tot[15]):.1f} %")
        chk("prediction 1 numbers", (tot[9], tot[12], tot[15], l3[9], l3[12], l3[15]), (36, 16, 13, 35, 16, 11))
        chk("prediction 1: all > 0 and majority L=3 per SNR and pooled", all(tot[s] > 0 and l3[s] * 2 > tot[s] for s in (9, 12, 15)) and (l3[9] + l3[12] + l3[15]) * 2 > (tot[9] + tot[12] + tot[15]), True)
        chk("L=3 total 114/131 (EXPERIMENTS/DECISIONS)", (Ltot.get(3, 0), len(fl)), (114, 131))
    else:
        chk("L=3 total 44/47 (EXPERIMENTS/DECISIONS)", (Ltot.get(3, 0), len(fl)), (44, 47))

# ----------------------------------------------------------------------------- 5. prediction 2, EXPERIMENTS row, DECISIONS line
print("=" * 100 + "\n5. PREDICTION 2 + EXPERIMENTS row + DECISIONS line number strings")
p2 = all(computed[t][s]["M-ours-dscore-C-V1"] <= computed[t][s]["M-ours-bstar"] for t in TAGS for s in SNRS)
chk("prediction 2 (V1 <= b*, 8/8)", p2, True)
vb = {t: ", ".join(f"{computed[t][s]['M-ours-dscore-C-V1']}:{computed[t][s]['M-ours-bstar']}" for s in SNRS) for t in TAGS}
pr = {t: ", ".join(f"{computed[t][s]['paired'][0]}:{computed[t][s]['paired'][1]}" for s in SNRS) for t in TAGS}
ge = {t: "/".join(str(computed[t][s]["R5-genie"]) for s in SNRS) for t in TAGS}
exp_row = [l for l in open(EXP, encoding="utf-8") if "run_hisnr16e4.sh" in l][-1]
dec_line = [l for l in open(DEC, encoding="utf-8") if "HISNR16e4 결과 기록" in l][-1]
chk("EXPERIMENTS C2 V1:b*", f"C2 {vb['HSB16e4k']} (짝지음 b\\* only : V1 only {pr['HSB16e4k']})" in exp_row, True)
chk("EXPERIMENTS C6 V1:b*", f"C6 {vb['HSNR16']} ({pr['HSNR16']})" in exp_row, True)
chk("EXPERIMENTS genie", f"genie 실패 C2 {ge['HSB16e4k']} (L=3 114/131), C6 {ge['HSNR16']} (L=3 44/47)" in exp_row, True)
chk("DECISIONS C2/C6 V1:b*", (f"C2 {vb['HSB16e4k'].replace(', ', '·')}, C6 {vb['HSNR16'].replace(', ', '·')}" in dec_line), True)
chk("DECISIONS genie L=3", "genie 실패 L=3 C2 114/131, C6 44/47" in dec_line, True)
chk("§6.1 prediction-2 string", f"C2 {vb['HSB16e4k']}; C6 {vb['HSNR16']} → 8/8" in sec61, True)
chk("§6.1 header expected-failure list", "V1 C2 16/7/5/3, C6 6/2/2/2; b\\* C2 28/17/16/8, C6 22/14/10/5; genie C2 9/2/2/2, C6 6/1/2/0" in sec61, True)
mine_hdr = "; ".join(f"{lab} C2 {'/'.join(str(orig[('C2', s, lab)][0]) for s in SNRS)}, C6 {'/'.join(str(orig[('C6', s, lab)][0]) for s in SNRS)}" for lab in ("V1", "b*", "genie"))
chk("recomputed original counts string", mine_hdr, "V1 C2 16/7/5/3, C6 6/2/2/2; b* C2 28/17/16/8, C6 22/14/10/5; genie C2 9/2/2/2, C6 6/1/2/0")

# ----------------------------------------------------------------------------- 6. manifests, accept files, log facts
print("=" * 100 + "\n6. MANIFESTS / ACCEPT / LOG FACTS")
for tag, (cell, oraw, kK, ll, sha, role) in TAGS.items():
    mf = json.load(open(os.path.join(RN, f"run_manifest_{tag}.json")))
    chk(f"{tag} manifest git", mf["git_commit"], "6b1de688"); chk(f"{tag} manifest n_raw_files", mf["n_raw_files"], 2048)
    chk(f"{tag} manifest kron_K", mf["gmm"]["kron_K"], str(kK)); chk(f"{tag} manifest ckpt sha", mf["stagec_checkpoint"]["sha256_16"], sha)
    chk(f"{tag} manifest role", mf["stagec_checkpoint"]["role"], role); chk(f"{tag} manifest skip", (mf["trial_stream"]["skip_min"], mf["trial_stream"]["skip_max_end"]), (10000, 30480))
    chk(f"{tag} manifest n_chunks", mf["run_params"]["n_chunks"], 2048); chk(f"{tag} manifest arms", mf["arms"], sorted(ARMS))
    chk(f"{tag} manifest fits_dir", mf["gmm"]["fits_dir"], f"{CONF}/results/gmm_fits_D2_{tag}")
    chk(f"{tag} fits link target", os.readlink(f"{CONF}/results/gmm_fits_D2_{tag}"), "gmm_fits_D2_" + oraw[4:])
    chk(f"{tag} manifest config_hash / written / stagec_gate", (mf["config_hash"], mf["written"], re.match(r"NO GATE RECORD mentions (\S+) -- UNVERIFIED here", mf["stagec_gate"])[1]),
        {"HSB16e4k": ("b66966335b0c172b", "2026-09-30 22:47:57 KST", "d2sx_N160000_a1.pt"), "HSNR16": ("7e8fe21e1c7fea42", "2026-10-01 07:09:00 KST", "d2sx_NR16_N160000_a1_fb2_best.pt")}[tag])
    om = json.load(open(os.path.join(RN, f"run_manifest_{oraw[4:]}.json")))
    chk(f"{tag} stagec_gate == original tag manifest", mf["stagec_gate"], om["stagec_gate"])
    chk(f"{tag} accept file", open(os.path.join(RN, f"{tag}_accept.txt")).read(), f"ACCEPT: OK -- {tag}\n")
    rl = open(os.path.join(CONF, "logs", f"run_D2_{tag}.log")).read().splitlines()
    chk(f"{tag} runner minutes", re.search(r"\[run\] finished in (\S+) min", rl[-1])[1], {"HSB16e4k": "44.4", "HSNR16": "500.3"}[tag])
    chk(f"{tag} runner done lines", sum(1 for l in rl if "/2048 done" in l), 2048)
log = open(os.path.join(CONF, "logs/run_hisnr16e4.log")).read().splitlines()
chk("run log start line", log[0], "[hisnr 09-30 08:03 CDT] start (git 6b1de688)"); chk("run log lines", len(log), 10)
chk("run log ABORT/INVALID/resume", any(("ABORT" in l or "INVALID" in l) for l in log), False)
chk("run log HISNR_DONE", log[-1], "[hisnr 09-30 17:09 CDT] HISNR_DONE ok=2 fail=0")
chk("run log accept/report lines", [log[3], log[4], log[7], log[8]],
    ["[hisnr 09-30 08:47 CDT] HSB16e4k acceptance rc=0 (ACCEPT: OK -- HSB16e4k)", "[hisnr 09-30 08:48 CDT] HSB16e4k report rc=0 genie_floor rc=0",
     "[hisnr 09-30 17:09 CDT] HSNR16 acceptance rc=0 (ACCEPT: OK -- HSNR16)", "[hisnr 09-30 17:09 CDT] HSNR16 report rc=0 genie_floor rc=0"])
ch = open(os.path.join(CONF, "logs/cpu_chain.log")).read().splitlines()
chk("chain log", ch[2:], ["[chain 09-30 08:03 CDT] SEEDS3 exit 0", "[chain 09-30 08:03 CDT] HISNR registration frozen -> run", "[chain 09-30 17:09 CDT] HISNR exit 0", "[chain 09-30 17:09 CDT] CHAIN_DONE"])
for tag in TAGS:
    h = open(os.path.join(RN, f"hisnr_{tag}.txt")).read().splitlines()
    chk(f"{tag} report header", (h[0], h[1]), (f"# run_hisnr16e4 git 6b1de688 2026-09-30 {'08:47' if tag == 'HSB16e4k' else '17:09'} CDT",
                                              f"# hisnr_report raw_{tag} {TAGS[tag][0]} S2; load_raw warnings: 0; REPORT-ONLY (HISNR16e4 §1)"))
# placeholders / forbidden wording in the three additions
add = sec61 + exp_row + dec_line
chk("placeholder 'x CDT'/TODO absent", bool(re.search(r"\bx CDT|TODO|xx:xx", add)), False)
chk("interpretive words absent", bool(re.search(r"유의하게|낫다|우수|개선|도달|여지|headroom|bound|최적|비긴다|significant", add)), False)

print("=" * 100)
print(f"mismatches: {len(MIS)}")
for m in MIS:
    print("  " + m)
