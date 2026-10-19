#!/bin/bash
# WORK_QUEUE 13: development screen of V1-clamp / V1-gmmfb (diag_lowsig.py), four single-thread processes, nice 10.
cd /home/HTJ/t2/conf || exit 1
P=~/miniforge3/envs/torch/bin/python; export CUDA_VISIBLE_DEVICES=; D=results/review_next/lowsig; L=logs/diag_lowsig.log
echo "[lowsig $(TZ=America/Chicago date '+%m-%d %H:%M %Z') git $(git rev-parse --short HEAD)$([ -n "$(git status --porcelain code ../Demo)" ] && echo +dirty)] start screen" >> $L
i=0
for job in "U28 16qam" "U28 qpsk" "D2 16qam" "D2 qpsk"; do
  cpu=$((184 + i)); i=$((i + 1)); name=$(echo $job | tr ' ' '_')
  nice -n 10 taskset -c $cpu $P $D/diag_lowsig.py $job 5440 40 9 15 18 21 > $D/log_screen_$name.txt 2>&1 &
done
wait
echo "[lowsig $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] SCREEN_DONE" >> $L
