"""recompute_e5_dev.py -- independent recomputation of NEXT_EXPERIMENTS_E5QAM16 §5 (development records) and of the §6.1
run statistics: the SNR-grid development runs (worktree raw_U28QAM16g / raw_D2QAM16g, b* only, trials 5120..5439), the
nu_q coverage files (qam16/coverage_*.npz; prediction 4), the smoke logs (RSS -> G), the worker estimate, and the per-chunk
times / counts of the two test runner logs.  numpy + stdlib only.

    CUDA_VISIBLE_DEVICES= nice -n 10 taskset -c 10-13 python -B recompute_e5_dev.py > recompute_e5_dev.out
"""
import glob
import math
import os
import re
import statistics
from collections import defaultdict

import numpy as np

WT = os.path.expanduser("~/t2_wtE5/conf")
CONF = "/home/HTJ/t2/conf"
QAM = os.path.join(CONF, "results/review_next/qam16")
BS = "M-ours-bstar"
G0 = [3, 6, 9, 12, 15, 18, 21]
N_OK = N_BAD = 0
BAD = []


def check(name, got, want):
    global N_OK, N_BAD
    ok = got == want
    N_OK += ok; N_BAD += (not ok)
    if not ok:
        BAD.append(f"{name}: got {got!r} want {want!r}")
    print(f"  [{'ok' if ok else 'MISMATCH'}] {name}: {got!r}" + ("" if ok else f"   (expected {want!r})"))


# ---------------------------------------------------------------- §5 SNR grid (b* only, development trials 5120..5439)
EXP_GRID = {"U28QAM16g": dict(F=(213, 129, 92, 68, 40, 23, 11), git="57eb1f22", kron_K=4096, ll=5.797910431000217, prior="UMi28"),
            "D2QAM16g": dict(F=(150, 78, 48, 42, 32, 22, 16), git="2e02fda0", kron_K=1024, ll=-11.459169831224418, prior="S2")}
PAT = re.compile(r"^D2_(C\d)_(\w+?)_Nr8_T16_Tp4_(dft|eig)_snr(-?\d+)_skip(\d+)_n(\d+)\.npz$")
for tag, E in EXP_GRID.items():
    files = sorted(glob.glob(os.path.join(WT, f"raw_{tag}", "D2_*.npz")))
    print(f"\n=== {tag}: {len(files)} chunks in {WT}/raw_{tag}")
    plan, vals, F, raised, shapes, arms = defaultdict(list), defaultdict(set), defaultdict(int), defaultdict(int), set(), set()
    for f in files:
        m = PAT.match(os.path.basename(f)); assert m, f
        snr, skip, n = int(m[4]), int(m[5]), int(m[6])
        plan[snr].append((skip, n)); vals["prior"].add(m[2]); vals["cell"].add(m[1])
        z = np.load(f)
        for k in ("run|git", "meta|modulation", "meta|payload_bits", "meta|protocol", "meta|bstar", "meta|kron_K", "meta|ll_val|kron", "run|iters", "run|n", "run|seed"):
            vals[k].add(z[k].item())
        vals["skip==name"].add(int(z["run|skip"]) == skip); vals["snr==name"].add(float(z["run|snr"]) == snr)
        arms.add(tuple(sorted(k.split("|")[0] for k in z.files if k.endswith("|blk_err"))))
        be = z[f"{BS}|blk_err"]; shapes.add(be.shape)
        v = be[:, -1].astype(float)
        F[snr] += int(np.sum(np.where(np.isfinite(v), v != 0, True))); raised[snr] += int((~np.isfinite(v)).sum())
        raised[snr] += sum(1 for k in z.files if k.endswith("|failed"))
    snrs = sorted(plan)
    check(f"{tag} SNRs present", snrs, G0)
    check(f"{tag} plan: 32 chunks of 10 at skips 5120..5430 per SNR", all(sorted(plan[s]) == [(5120 + 10 * k, 10) for k in range(32)] for s in snrs), True)
    check(f"{tag} arm set", arms, {(BS,)})
    check(f"{tag} blk_err shape", shapes, {(10, 16)})
    check(f"{tag} run|git", vals["run|git"], {E["git"]})
    check(f"{tag} meta modulation/payload/protocol", (vals["meta|modulation"], vals["meta|payload_bits"], vals["meta|protocol"]), ({"16qam"}, {90}, {"E5-qam16-v1"}))
    check(f"{tag} meta bstar/kron_K/ll_val", (vals["meta|bstar"], vals["meta|kron_K"], vals["meta|ll_val|kron"]), ({"kron"}, {E["kron_K"]}, {E["ll"]}))
    check(f"{tag} run iters/n/seed", (vals["run|iters"], vals["run|n"], vals["run|seed"]), ({16}, {10}, {20260926}))
    check(f"{tag} run|skip / run|snr == file name", (vals["skip==name"], vals["snr==name"]), ({True}, {True}))
    check(f"{tag} file-name prior / cell", (vals["prior"], vals["cell"]), ({E["prior"]}, {"C2"}))
    check(f"{tag} b* failures / 320 at +3..+21", tuple(F[s] for s in G0), E["F"])
    check(f"{tag} raised", sum(raised.values()), 0)
    lo, hi = F[3] / 320, F[21] / 320
    inside = lo > 0.1 and hi < 0.1
    print(f"  BLER(+3) = {lo!r}, BLER(+21) = {hi!r}; inside condition (BLER(+3) > 0.1 and BLER(+21) < 0.1) = {inside}")
    check(f"{tag} §1.2 rule -> G0 without shift", inside, True)
    print(f"  b* BLER per SNR: " + "  ".join(f"{s:+d}:{F[s] / 320:.6f}" for s in G0) + f"; monotone non-increasing = {all(F[G0[i + 1]] <= F[G0[i]] for i in range(6))}")

# ---------------------------------------------------------------- §1.3 / §5 nu_q coverage (prediction 4)
EXP_COV = {"coverage_U28QAM16_16qam": (0, 0, 0, 0, 7, 23, 40), "coverage_U28QAM16_qpsk": (0, 0, 0, 0, 8, 39, 40),
           "coverage_D2QAM16_16qam": (0, 0, 0, 0, 27, 26, 40), "coverage_D2QAM16_qpsk": (0, 0, 0, 0, 37, 37, 40)}
EXP_CKPT = {"U28": "sha256[:16]=6f3a1b9490864af1 epoch=379 best_epoch=379 role=best 8x4",
            "D2": "sha256[:16]=4443921ce8d5c4a1 epoch=1784 best_epoch=1764 role=legacy-last 8x4"}
pooled = {}
for name, want in EXP_COV.items():
    z = np.load(os.path.join(QAM, name + ".npz"), allow_pickle=True)
    print(f"\n=== {name}.npz")
    meta = {k.split("|", 1)[1]: z[k].item() for k in z.files if k.startswith("meta|")}
    cell = "U28" if "U28" in name else "D2"
    mod = "16qam" if name.endswith("16qam") else "qpsk"
    check(f"{name} meta skip/n", (meta.get("skip"), meta.get("n")), (5440, 40))
    check(f"{name} meta modulation/payload", (meta.get("modulation"), meta.get("payload_bits")), (mod, 90 if mod == "16qam" else 42))
    check(f"{name} meta checkpoint_id", meta.get("checkpoint_id"), EXP_CKPT[cell])
    print(f"  meta sigma_tag {meta.get('sigma_tag')!r} s_lo {meta.get('s_lo')!r} s_hi {meta.get('s_hi')!r} fit_tag {meta.get('fit_tag')!r} convention {meta.get('convention')!r}")
    s_lo, s_hi = float(meta["s_lo"]), float(meta["s_hi"])
    snrs = sorted({int(k.split("|")[0]) for k in z.files if k.endswith("|sigma")})
    check(f"{name} SNRs", snrs, G0)
    out16, fin16, stored_ok, conv_ok = [], [], True, True
    for s in snrs:
        sg, nu = z[f"{s}|sigma"], z[f"{s}|nu_q"]
        conv_ok &= bool(np.allclose(np.sqrt(nu / 2), sg, equal_nan=True))
        fin = np.isfinite(sg)
        below = ((sg < s_lo) & fin).sum(0); above = ((sg > s_hi) & fin).sum(0)
        stored_ok &= bool(np.array_equal(below, z[f"{s}|below"]) and np.array_equal(above, z[f"{s}|above"]) and np.array_equal(fin.sum(0), z[f"{s}|finite"]))
        out16.append(int(below[15] + above[15])); fin16.append(int(fin[:, 15].sum()))
        assert sg.shape == (40, 16)
    check(f"{name} sigma == sqrt(nu_q / 2) (stored convention)", conv_ok, True)
    check(f"{name} stored below/above/finite arrays == recomputed from sigma vs [s_lo, s_hi] (all 16 iterations)", stored_ok, True)
    check(f"{name} iteration-16 out-of-range per SNR", tuple(out16), want)
    check(f"{name} iteration-16 finite per SNR", tuple(fin16), (40,) * 7)
    pooled[(cell, mod)] = (sum(out16), sum(fin16))
    print(f"  pooled iteration 16: {sum(out16)}/{sum(fin16)} = {sum(out16) / sum(fin16):.3f}")
check("prediction 4 UMi28: 16-QAM out fraction <= QPSK", (pooled[("U28", "16qam")], pooled[("U28", "qpsk")], pooled[("U28", "16qam")][0] / 280 <= pooled[("U28", "qpsk")][0] / 280), ((70, 280), (87, 280), True))
check("prediction 4 D2: 16-QAM out fraction <= QPSK", (pooled[("D2", "16qam")], pooled[("D2", "qpsk")], pooled[("D2", "16qam")][0] / 280 <= pooled[("D2", "qpsk")][0] / 280), ((93, 280), (114, 280), True))
# the same sigma range for the two modulations of a cell
for cell in ("U28", "D2"):
    r = [tuple(float(np.load(os.path.join(QAM, f"coverage_{cell}QAM16_{m}.npz"))[f"meta|{k}"]) for k in ("s_lo", "s_hi")) for m in ("16qam", "qpsk")]
    check(f"{cell}: same [s_lo, s_hi] for 16-QAM and QPSK coverage", r[0] == r[1], True)

# ---------------------------------------------------------------- smoke logs -> G, worker estimate, times
print("\n=== smoke logs (RSS -> G = ceil(RSS * 1.05 / 0.5) * 0.5), worker estimate, time estimate")
for cell, want in (("U28", (245, 247, 1.203, 1.5)), ("D2", (128, 134, 0.877, 1.0))):
    txt = open(os.path.join(CONF, "logs", f"e5_smoke_{cell}.log")).read()
    t_chunk = int(re.search(r"\((\d+) s\)\s+modulation=16qam", txt)[1])
    m = re.search(r"wall (\d+) s\s+max RSS ([\d.]+) GB\s+-> G = ([\d.]+)", txt)
    wall, rss, g_log = int(m[1]), float(m[2]), float(m[3])
    g = math.ceil(rss * 1.05 / 0.5) * 0.5
    check(f"smoke {cell}: chunk s, wall s, RSS GB, G (recomputed)", (t_chunk, wall, rss, g), want)
    check(f"smoke {cell}: G printed in the log == recomputed", g_log, g)
    mem_gb = 1003263876 / 2 ** 20
    workers = math.floor(0.8 * mem_gb / g)
    print(f"  MemAvailable 1003263876 kB = {mem_gb:.1f} GiB -> floor(0.8 * {mem_gb:.1f} / {g}) = {workers} (registered {510 if cell == 'U28' else 765}); "
          f"estimate ceil(448/96) x {t_chunk} s = {5 * t_chunk / 60:.1f} min")
    check(f"smoke {cell}: worker bound", workers, 510 if cell == "U28" else 765)

# ---------------------------------------------------------------- §6.1 runner logs: per-chunk times, counts, line references
print("\n=== test runner logs")
for tag, want in (("U28QAM16", (388, 397, 252, 446, "32.5", 529)), ("D2QAM16", (213, 225, 121, 244, "17.7", 793))):
    lines = open(os.path.join(CONF, "logs", f"run_D2_{tag}.log")).read().splitlines()
    done = [l for l in lines if re.search(r"^\d+/448 done", l)]
    secs = [int(re.search(r"\((\d+) s\)", l)[1]) for l in done]
    exc0 = sum(1 for l in done if l.endswith("arm-trial exceptions=0"))
    mod = all("modulation=16qam K=90" in l for l in done)
    fin = re.search(r"finished in ([\d.]+) min", lines[-1])
    guard = re.search(r"memory guard allows (\d+) workers -> jobs = (\d+)", lines[5])
    check(f"{tag} log: 448 'done' lines, all 'arm-trial exceptions=0', all 'modulation=16qam K=90'", (len(done), exc0, mod), (448, 448, True))
    check(f"{tag} log: chunk s mean / median / min / max", (round(statistics.mean(secs)), round(statistics.median(secs)), min(secs), max(secs)), want[:4])
    check(f"{tag} log: 'finished in' min (line 456)", (fin[1], len(lines)), (want[4], 456))
    check(f"{tag} log line 6: memory guard -> jobs", (int(guard[1]), int(guard[2])), (want[5], 96))
    check(f"{tag} log line 7: '448 tasks on 96 workers'", "448 tasks on 96 workers" in lines[6], True)
    files = sorted(glob.glob(os.path.join(CONF, f"raw_{tag}", "D2_*.npz")), key=os.path.getmtime)
    import datetime as dt
    t0, t1 = (dt.datetime.fromtimestamp(os.path.getmtime(f)) for f in (files[0], files[-1]))
    print(f"  raw mtimes KST: first chunk {t0:%Y-%m-%d %H:%M:%S}, last chunk {t1:%Y-%m-%d %H:%M:%S}; span {(t1 - t0).total_seconds() / 60:.1f} min; mean {statistics.mean(secs):.1f} s median {statistics.median(secs)} s")

print(f"\nSUMMARY: {N_OK} comparisons match, {N_BAD} mismatch")
for b in BAD:
    print("  MISMATCH " + b)
