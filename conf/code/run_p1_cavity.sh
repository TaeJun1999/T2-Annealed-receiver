#!/bin/bash
# (review_next NEXT_EXPERIMENTS §2.1) P1-1 real-query diagnostics on the DEVELOPMENT set (trials 2560..3199):
# 4 points x 16 chunks, one CPU process per chunk (receiver = CPU complex128, one thread), then merge per point.
# Waits for the C6 re-run to release the CPUs.  Chunks that already exist are skipped by diag_p1_cavity.py.
cd /home/HTJ/t2/conf
P=~/miniforge3/envs/torch/bin/python
L=logs/review_next/p1_cavity.log
log () { echo "[p1cav $(TZ=America/Chicago date '+%H:%M %Z')] $*" | tee -a $L >> logs/queue.log; }

until grep -qE "NR16RUN2_DONE|nr16run2.*ABORT" logs/queue.log; do sleep 60; done
log "start: C2 -3 (decision), C2 +6, C5 -3, C1 -3 (report-only); 64 chunks"
for pt in "C2 -3" "C2 6" "C5 -3" "C1 -3"; do
  for s in $(seq 2560 40 3160); do echo "$pt $s"; done
done | CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=1 xargs -P 64 -L 1 bash -c \
  "$P code/diag_p1_cavity.py --cell \$0 --snr \$1 --skip \$2 >> $L 2>&1 || echo \"[p1cav] FAIL \$0 \$1 \$2\" >> $L"
for pt in "C2 -3" "C2 6" "C5 -3" "C1 -3"; do
  set -- $pt
  CUDA_VISIBLE_DEVICES="" $P code/diag_p1_cavity.py --cell $1 --snr $2 --merge >> $L 2>&1 \
    && log "merged $1 $2" || log "MERGE FAILED $1 $2"
done
log "P1_CAVITY_DONE"
