#!/bin/bash
# (10_SPEC_stageC §7, review_next S7-b) C6 (Nr=16) BLER re-run WITH the Stage C diffusion arms.
# The first run (tag NR16run) dropped every M-ours-dscore-C-* arm through the old `Nr != 8` guard
# (fixed in cd241b7e); raw_NR16run is kept as the record of that arm-less run.  Same configuration
# otherwise: equal budget N=1e4, n=2560, chunk 40, the SAME ungated d2sx_NR16_N10000_a1.pt
# (legacy last-EMA @1688, best @1668 -> BEST_WEIGHTS_UNAVAILABLE, written to meta|stagec_ckpt_id).
# Receiver = CPU complex128 for every arm (01_RULES §9.3).
cd /home/HTJ/t2/conf
P=~/miniforge3/envs/torch/bin/python
log () { echo "[nr16run2 $(TZ=Asia/Seoul date '+%H:%M')] $*" >> logs/queue.log; }

log "BLER C6 re-run with Stage C arms, tag NR16run2"
ln -sfn gmm_fits_D2_NR16 results/gmm_fits_D2_NR16run2
$P code/runner.py run --testbed D2 --cell C6 --prior S2 --n 2560 --chunk 40 --tag NR16run2 --ntrain 10000 \
   --stagec-ckpt /home/HTJ/t2/conf/ckpt/d2sx_NR16_N10000_a1.pt >> logs/run_D2_NR16run2.log 2>&1 \
   || { log "ABORT: runner run failed (logs/run_D2_NR16run2.log)"; exit 1; }
$P code/runner.py analysis --testbed D2 --tag NR16run2 >> logs/run_D2_NR16run2.log 2>&1
$P code/guard_report.py --raw /home/HTJ/t2/conf/raw_NR16run2 --testbed D2 > results/guard_D2_NR16run2.txt 2>&1
log "NR16RUN2_DONE"
