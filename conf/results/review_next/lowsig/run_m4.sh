#!/bin/bash
# SELECTION_RULE.md addendum (Fable M4): V1, b*, A, B at the expected L2 decision-point SNRs not among the 12 screen points (n 320 each).
cd /home/HTJ/t2/conf || exit 1
P=~/miniforge3/envs/torch/bin/python; export CUDA_VISIBLE_DEVICES=; D=results/review_next/lowsig; L=logs/diag_lowsig.log
echo "[lowsig $(TZ=America/Chicago date '+%m-%d %H:%M %Z') git $(git rev-parse --short HEAD)] start m4 (V1 b* A B)" >> $L
cpu=24
for job in "U28 qpsk 6000 3" "U28 qpsk 6000 6" "U28 qpsk 6000 9" "D2 qpsk 6000 -3" "D2 qpsk 6000 0" "D2 qpsk 6000 3" \
           "U28 16qam 5120 12" "D2 16qam 5120 9" "D2 16qam 5120 12"; do
  set -- $job
  nice -n 10 taskset -c $cpu $P $D/diag_lowsig.py $1 $2 $3 320 $4 > $D/log_m4_$1_$2_$4.txt 2>&1 &
  cpu=$((cpu + 1))
done
wait
echo "[lowsig $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] M4_DONE" >> $L
