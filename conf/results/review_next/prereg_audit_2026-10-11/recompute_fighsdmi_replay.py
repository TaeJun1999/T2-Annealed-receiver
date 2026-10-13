"""recompute_fighsdmi_replay.py -- RECORD AUDIT of NEXT_EXPERIMENTS_FIGHSDMI16e4.md §6: in-memory REPLAY of ONE stored chunk of a new
raw (raw_FHDMIB16e4 / raw_FHSPDMI / raw_FHALDDMI), modelled on recompute_dmi_replay.py (same folder; that file is not modified).
runner.run_task is called with the task tuple cmd_run builds for the row's flags (run_fighsdmi16e4.sh ROWS), but
  * runner.raw_file is replaced after the stored file name was taken, so the "exists" short-cut does not fire and no path in a
    raw_* directory is ever opened for writing, and
  * numpy.savez_compressed is replaced by an in-memory capture -- NOTHING is written to disk.
Every key of the captured chunk is then compared with the stored chunk (arrays bit for bit, NaN == NaN; strings exactly).
Expected difference: run|git only (stored e5caaccb; HEAD is 42fd4e03 now).  CPU only, different cores than the run (NUMA node 0).

usage (cwd anywhere):  CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 taskset -c 0-15 \
    ~/miniforge3/envs/torch/bin/python -B recompute_fighsdmi_replay.py <FHDMIB16e4|FHSPDMI|FHALDDMI> <snr> <skip>
"""
import json
import os
import sys
import time

CONF = "/home/HTJ/t2/conf"
os.chdir(CONF)
sys.path.insert(0, os.path.join(CONF, "code"))
sys.dont_write_bytecode = True
import numpy as np  # noqa: E402

import common as C  # noqa: E402
import runner  # noqa: E402

CK = os.path.join(CONF, "ckpt/d2sx_DMI_N160000_a1_best.pt")
ROWS = {  # tag -> (--arm list, --stagec-ckpt, --ald-file, --sparse-file)   [run_fighsdmi16e4.sh ROWS / args()]
    "FHDMIB16e4": ("R0-pilot R1-turbo R2-ours-G R3-bigamp M-ours-bstar M-ours-dscore-C-V1 R5-genie".split(), CK, None, None),
    "FHSPDMI": ("SBL-loop SBL-pilot OMP-pilot R5-genie".split(), None, None, "results/sparse/pick_DMI_C2.json"),
    "FHALDDMI": ("ALD-pilot R5-genie".split(), CK, os.path.join(CONF, "results/ald/ald_PILDMI_hisnr.npz"), None),
}


def main():
    tag, snr, skip = sys.argv[1], float(sys.argv[2]), int(sys.argv[3])
    arm_sel, ck, ald_file, sparse = ROWS[tag]
    if sparse:                                                       # what runner.main does for --sparse-file
        sp = json.load(open(os.path.join(CONF, sparse)))
        runner.SPARSE = {k: sp[k] for k in ("rho_sbl", "rho_omp", "per_snr")}
    aff = sorted(os.sched_getaffinity(0))
    print(f"# replay {tag} snr {snr:g} skip {skip} n 40; affinity {aff[0]}..{aff[-1]} ({len(aff)} cpus); OMP={os.environ.get('OMP_NUM_THREADS')} "
          f"MKL={os.environ.get('MKL_NUM_THREADS')} OPENBLAS={os.environ.get('OPENBLAS_NUM_THREADS')} CUDA_VISIBLE_DEVICES={os.environ.get('CUDA_VISIBLE_DEVICES')!r}", flush=True)
    assert os.path.islink(os.path.join(CONF, f"results/gmm_fits_D2_{tag}")), "fits link of the tag missing (a replay must not fit anything)"
    runner._init(tag)
    stored = runner.raw_file("D2", "C2", "DMI", C.make_pilots("D2", "DMI", 4, 4, 8)[0], snr, skip, 40)
    assert os.path.exists(stored), stored
    cap = {}
    real_raw_file, real_savez = runner.raw_file, np.savez_compressed
    runner.raw_file = lambda *a: os.path.join("/nonexistent_dir_for_replay", "__replay_never_written__.npz")

    def capture(out, **flat):
        cap.update(flat)

    np.savez_compressed = capture
    task = ("D2", "C2", "DMI", snr, skip, 40, 160000, C.BETA, C.T_IN, C.N_ITER, arm_sel, None, ck, False, False, None, False, ald_file, None, None, None)
    t0 = time.time()
    try:
        msg = runner.run_task(task)
    finally:
        runner.raw_file, np.savez_compressed = real_raw_file, real_savez
    print(f"  run_task: {msg}  [{time.time() - t0:.0f} s]", flush=True)
    z = np.load(stored)
    ks, kc = set(z.files), set(cap)
    print(f"  stored {os.path.relpath(stored, CONF)}: {len(ks)} keys; replay: {len(kc)} keys; only stored {sorted(ks - kc)}; only replay {sorted(kc - ks)}")
    diff, same_arr, same_str = [], 0, 0
    for k in sorted(ks & kc):
        a, b = z[k], np.asarray(cap[k])
        if a.dtype.kind in "US" or b.dtype.kind in "US":
            if str(a) == str(b):
                same_str += 1
            else:
                diff.append((k, str(a)[:90], str(b)[:90]))
        elif a.shape == b.shape and a.dtype == b.dtype and np.array_equal(a, b, equal_nan=True):
            same_arr += 1
        else:
            diff.append((k, f"{a.dtype} {a.shape}", f"{b.dtype} {b.shape}"))
    print(f"  identical numeric keys {same_arr}, identical string keys {same_str}, differing keys {len(diff)}")
    for d in diff:
        print("    DIFF", d)
    arms = sorted({k.split("|")[0] for k in ks if k.endswith("|blk_err")})
    print("  failures @16 in this chunk (stored): " + ", ".join(f"{a} {int(np.nansum(z[a + '|blk_err'][:, -1]))} (rows {np.flatnonzero(z[a + '|blk_err'][:, -1] > 0).tolist()})" for a in arms))
    ok = all(d[0] == "run|git" for d in diff) and not (ks ^ kc)
    print(f"  VERDICT: {'BIT-IDENTICAL except run|git' if ok else 'NOT identical'}")


if __name__ == "__main__":
    main()
