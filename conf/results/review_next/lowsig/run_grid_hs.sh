#!/bin/bash
cd /home/HTJ/t2/conf || exit 1
P=~/miniforge3/envs/torch/bin/python; export CUDA_VISIBLE_DEVICES=; D=results/review_next/lowsig; L=logs/diag_lowsig.log
echo "[lowsig $(TZ=America/Chicago date '+%m-%d %H:%M %Z') git $(git rev-parse --short HEAD)] start grid_hs" >> $L
nice -n 10 taskset -c 160-167 $P $D/measure_grid_hs.py UMi28 UMi28HS 8 > $D/log_grid_UMi28HS.txt 2>&1 &
nice -n 10 taskset -c 168-175 $P $D/measure_grid_hs.py S2 HS 8 > $D/log_grid_HS.txt 2>&1 &
wait
echo "[lowsig $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] GRID_HS_DONE" >> $L
