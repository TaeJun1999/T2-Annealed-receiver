#!/bin/bash
# WORK_QUEUE 11 (user 2026-10-18 CDT): development-only V1 collapse diagnosis; six single-thread processes, nice 10.
cd /home/HTJ/t2/conf || exit 1
P=~/miniforge3/envs/torch/bin/python; export CUDA_VISIBLE_DEVICES=; D=results/review_next/qam16/diag_v1; L=logs/diag_v1_collapse.log
echo "[diag_v1 $(TZ=America/Chicago date '+%m-%d %H:%M %Z') git $(git rev-parse --short HEAD)$([ -n "$(git status --porcelain code ../Demo)" ] && echo +dirty)] start" >> $L
i=0
for job in "synth U28" "synth D2" "traj U28 16qam 15 18 21" "traj U28 qpsk 15 18 21" "traj D2 16qam 15 18 21" "traj D2 qpsk 15 18 21"; do
  cpu=$((184 + i)); i=$((i + 1)); name=$(echo $job | tr ' ' '_')
  nice -n 10 taskset -c $cpu $P $D/diag_v1_collapse.py $job > $D/log_$name.txt 2>&1 &
done
wait
echo "[diag_v1 $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] DIAG_DONE" >> $L
