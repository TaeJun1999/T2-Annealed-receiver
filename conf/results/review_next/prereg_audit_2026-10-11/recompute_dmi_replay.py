"""recompute_dmi_replay.py -- RECORD AUDIT of NEXT_EXPERIMENTS_ROOM16e4.md §7 (prior DMI): in-memory REPLAY of stored raw chunks
under a DIFFERENT CPU affinity (taskset -c 0-15 = NUMA node 0; the registered run used nodes 1 + 3, 192 workers on 96 threads).
Calls runner.run_task for one chunk with the task tuple cmd_run builds, but
  * runner.raw_file is replaced so that the "exists" short-cut does not fire (the path is never written), and
  * numpy.savez_compressed is replaced by an in-memory capture -- NOTHING is written to disk (no raw directory is touched).
Then every key of the captured chunk is compared with the stored chunk file (arrays bit for bit, equal_nan; strings exactly).
Expected differences: run|git only (HEAD is cde35a4e now and conf/code holds an untracked follow-up script).

usage (cwd = ~/t2/conf):  CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=<1|8> ... taskset -c 0-15 ~/miniforge3/envs/torch/bin/python -B \
    results/review_next/prereg_audit_2026-10-11/recompute_dmi_replay.py <tag: DMIB16e4|DMIB16e4last|PILDMI|ALDDMI|SPDMI> <snr> <skip>
(the three main-run replays recompute_dmi_replay_{best_m3_t1,last_0_t1,best_p3_t8}.out were made with the first version of this file,
 which knew only the two main tags; the baseline branches were added afterwards and change nothing for the main tags)
"""
import os
import sys
import time

CONF = "/home/HTJ/t2/conf"
sys.path.insert(0, os.path.join(CONF, "code"))
import numpy as np  # noqa: E402

import common as C  # noqa: E402
import runner  # noqa: E402


def main():
    tag, snr, skip = sys.argv[1], float(sys.argv[2]), int(sys.argv[3])
    ck = os.path.join(CONF, "ckpt", "d2sx_DMI_N160000_a1.pt" if tag == "DMIB16e4last" else "d2sx_DMI_N160000_a1_best.pt")
    # baseline raws (run_dmi_base.sh): PILDMI = --stagec-ckpt best --pilot-arms --arm V1-pilot bstar-pilot R5-genie; ALDDMI = --stagec-ckpt best
    # --ald-file ald_PILDMI.npz --arm ALD-pilot ALDv-pilot R5-genie; SPDMI = --sparse-file pick_DMI_C2.json --arm SBL-loop SBL-pilot OMP-pilot R5-genie
    arm_sel, pilot_arms, ald_file = None, False, None
    if tag == "PILDMI":
        arm_sel, pilot_arms = ["V1-pilot", "bstar-pilot", "R5-genie"], True
    elif tag == "ALDDMI":
        arm_sel, ald_file = ["ALD-pilot", "ALDv-pilot", "R5-genie"], os.path.join(CONF, "results/ald/ald_PILDMI.npz")
    elif tag == "SPDMI":
        import json
        sp = json.load(open(os.path.join(CONF, "results/sparse/pick_DMI_C2.json")))
        runner.SPARSE = {k: sp[k] for k in ("rho_sbl", "rho_omp", "per_snr")}          # what runner.main does for --sparse-file
        arm_sel, ck = ["SBL-loop", "SBL-pilot", "OMP-pilot", "R5-genie"], None
    print(f"# replay {tag} snr {snr:g} skip {skip} n 40; affinity {sorted(os.sched_getaffinity(0))[:3]}..{max(os.sched_getaffinity(0))} "
          f"({len(os.sched_getaffinity(0))} cpus); OMP_NUM_THREADS={os.environ.get('OMP_NUM_THREADS')} MKL={os.environ.get('MKL_NUM_THREADS')} "
          f"OPENBLAS={os.environ.get('OPENBLAS_NUM_THREADS')}", flush=True)
    runner._init(tag)
    stored_name = runner.raw_file("D2", "C2", "DMI", C.make_pilots("D2", "DMI", 4, 4, 8)[0], snr, skip, 40)
    assert os.path.exists(stored_name), stored_name
    cap = {}
    real_raw_file, real_savez = runner.raw_file, np.savez_compressed
    runner.raw_file = lambda *a: os.path.join(CONF, "results/review_next/prereg_audit_2026-10-11", "__replay_never_written__.npz")

    def capture(out, **flat):
        cap.update(flat)

    np.savez_compressed = capture
    task = ("D2", "C2", "DMI", snr, skip, 40, 160000, C.BETA, C.T_IN, C.N_ITER, arm_sel, None, ck, False, False, None, pilot_arms, ald_file, None, None, None)
    t0 = time.time()
    try:
        msg = runner.run_task(task)
    finally:
        runner.raw_file, np.savez_compressed = real_raw_file, real_savez
    print(f"  run_task: {msg}  [{time.time() - t0:.0f} s]", flush=True)
    try:
        import torch
        print(f"  torch threads {torch.get_num_threads()}")
    except Exception as e:  # pragma: no cover
        print("  torch not imported:", e)
    z = np.load(stored_name)
    ks, kc = set(z.files), set(cap)
    print(f"  stored {os.path.relpath(stored_name, CONF)}: {len(ks)} keys; replay: {len(kc)} keys; only stored {sorted(ks - kc)}; only replay {sorted(kc - ks)}")
    diff, same_arr, same_meta = [], 0, 0
    for k in sorted(ks & kc):
        a, b = z[k], np.asarray(cap[k])
        if a.dtype.kind in "US" or b.dtype.kind in "US":
            if str(a) == str(b):
                same_meta += 1
            else:
                diff.append((k, str(a)[:90], str(b)[:90]))
        else:
            if a.shape == b.shape and np.array_equal(a, b, equal_nan=True):
                same_arr += 1
            else:
                d = float(np.nanmax(np.abs(a.astype(float) - b.astype(float)))) if a.shape == b.shape else None
                diff.append((k, f"shape {a.shape}", f"shape {b.shape} max|d| {d}"))
    print(f"  identical numeric keys {same_arr}, identical string keys {same_meta}, differing keys {len(diff)}")
    for d in diff:
        print("    DIFF", d)
    arms = sorted({k.split("|")[0] for k in ks if k.endswith("|blk_err")})
    print(f"  arms with blk_err: {len(arms)}; failures @16 in this chunk (stored == replay): "
          + ", ".join(f"{a} {int(np.nansum(z[a + '|blk_err'][:, -1]))}" for a in arms))
    only_git = all(d[0] == "run|git" for d in diff)
    print(f"  VERDICT: {'BIT-IDENTICAL except run|git' if only_git and not (ks ^ kc) else 'NOT identical'}")


if __name__ == "__main__":
    main()
