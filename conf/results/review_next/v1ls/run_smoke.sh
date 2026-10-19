#!/bin/bash
cd /home/HTJ/t2_wtLS/conf || exit 1
P=~/miniforge3/envs/torch/bin/python; export CUDA_VISIBLE_DEVICES=; D=results/review_next/v1ls
echo "[v1ls smoke $(TZ=America/Chicago date '+%m-%d %H:%M %Z') git $(git rev-parse --short HEAD)$([ -n "$(git status --porcelain code ../Demo)" ] && echo +dirty)] start" >> logs/v1ls_smoke.log
i=0; for j in "U28 qpsk" "U28 16qam" "D2 qpsk" "D2 16qam"; do
  nice -n 10 taskset -c $((140 + i)) $P $D/rss_smoke_v1ls.py $j > $D/log_smoke_$(echo $j | tr ' ' '_').txt 2>&1 &
  i=$((i + 1)); done
wait; echo "[v1ls smoke $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] SMOKE_DONE" >> logs/v1ls_smoke.log
