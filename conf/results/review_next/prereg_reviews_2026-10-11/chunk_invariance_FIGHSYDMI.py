"""chunk_invariance_FIGHSYDMI.py -- pre-registration check for NEXT_EXPERIMENTS_FIGHSYDMI16e4 (nothing is written to any raw directory).
The +15 dB row of that registration runs with --chunk 400 instead of 40 (every chunk regenerates the skipped trials of its point's
stream, so with chunk 40 and n = 3072000 the regeneration alone would cost about as much as the receivers).  Claim checked here:
the per-trial results do not depend on the chunk partition.  One in-memory chunk (trials 10000..10399, +15 dB, the seven main arms,
runner.run_task with the task tuple cmd_run builds; raw_file / savez replaced so nothing is written) is compared, trial by trial and
for every KEYS_RAW key of every arm, with the ten stored chunk-40 files of raw_FHDMIB16e4 holding the same trials.
usage (cwd = ~/t2/conf): CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=1 ... taskset -c <cpu> ~/miniforge3/envs/torch/bin/python -B <this file>
"""
import os, sys, time
CONF = "/home/HTJ/t2/conf"
sys.path.insert(0, os.path.join(CONF, "code"))
import numpy as np
import common as C
import runner

ARMS = ["R0-pilot", "R1-turbo", "R2-ours-G", "R3-bigamp", "M-ours-bstar", "M-ours-dscore-C-V1", "R5-genie"]
SNR, SKIP, N = 15.0, 10000, 400
ck = os.path.join(CONF, "ckpt", "d2sx_DMI_N160000_a1_best.pt")
runner._init("FHDMIB16e4")
pil = C.make_pilots("D2", "DMI", 4, 4, 8)[0]
stored = [runner.raw_file("D2", "C2", "DMI", pil, SNR, s, 40) for s in range(SKIP, SKIP + N, 40)]
assert all(os.path.exists(f) for f in stored)
cap = {}
runner.raw_file = lambda *a: "/nonexistent/__probe_never_written__.npz"
np.savez_compressed = lambda out, **flat: cap.update(flat)
task = ("D2", "C2", "DMI", SNR, SKIP, N, 160000, C.BETA, C.T_IN, C.N_ITER, ARMS, None, ck, False, False, None, False, None, None, None, None)
t0 = time.time()
runner.run_task(task)
print(f"# one chunk skip {SKIP} n {N} at {SNR:+.0f} dB, arms {ARMS}: {time.time() - t0:.0f} s (affinity {sorted(os.sched_getaffinity(0))})")
zs = [np.load(f) for f in stored]
keys = [f"{a}|{q}" for a in ARMS + ["R0-pilot@1"] for q in C.KEYS_RAW if f"{a}|{q}" in zs[0].files]
ncmp, bad, skipped = 0, [], []
for k in keys:
    if k not in cap:
        bad.append(k + " (absent from the n = 400 chunk)"); continue
    big = np.asarray(cap[k])
    parts = [np.asarray(z[k]) for z in zs]
    if parts[0].ndim == 0 or parts[0].shape[0] != 40:
        skipped.append(k); continue
    ref = np.concatenate(parts, 0)
    ncmp += 1
    if big.shape != ref.shape or not np.array_equal(np.nan_to_num(big, nan=1e300), np.nan_to_num(ref, nan=1e300)):
        bad.append(k)
print(f"per-trial keys compared {ncmp} (arms x KEYS_RAW present in the stored chunks; not per-trial, skipped: {skipped or 'none'}); differing: {bad or 'none'}")
print("failures@16 in these 400 trials: " + ", ".join(f"{a} {int(np.nansum(np.asarray(cap[a + '|blk_err'])[:, -1]))}" for a in ARMS))
print("CHUNK-INVARIANCE: " + ("OK" if ncmp and not bad else "FAILED"))
