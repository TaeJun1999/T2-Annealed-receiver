#!/bin/bash
# (review_next A1 C5 follow-up, user decision 2026-09-23 09:40 CDT: "추가 학습 포함 등록") N=1.6e5 aug / ctrl attempts 2 and 3,
# same recipe as attempt 1 (train_ctrl.py; legacy siblings ckpt/d2sx_N160000_a{2,3}.pt cross-checked).  TRAINING ONLY:
# no BLER is computed here -- the development/confirmation evaluation is fixed by the new pre-registration, frozen
# before any of these checkpoints is evaluated.  One training per GPU (Exclusive_Process), GPUs 0-3.
cd /home/HTJ/t2
P=~/miniforge3/envs/torch/bin/python
L=conf/logs/review_next/run_a1c5_train.log
log () { echo "[a1c5 $(TZ=America/Chicago date '+%H:%M %Z')] $*" | tee -a $L >> conf/logs/queue.log; }
log "start (git $(git rev-parse --short HEAD))"
pids=(); names=(); g=0
for a in 2 3; do
  for kind in ctrl aug; do
    [ $kind = aug ] && F=--phase-aug || F=
    CUDA_VISIBLE_DEVICES=$g $P conf/code/train_ctrl.py --ntrain 160000 --attempt $a $F > conf/logs/review_next/stdout_${kind}_N160000_a$a.log 2>&1 &
    pids+=($!); names+=("${kind}_a$a@GPU$g"); g=$((g+1))
  done
done
for i in "${!pids[@]}"; do wait ${pids[$i]} && log "${names[$i]} done" || log "FAIL ${names[$i]}"; done
log "A1C5_TRAIN_DONE"
