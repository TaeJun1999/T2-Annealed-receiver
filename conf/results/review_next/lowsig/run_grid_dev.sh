#!/bin/bash
cd /home/HTJ/t2/conf || exit 1
P=~/miniforge3/envs/torch/bin/python; export CUDA_VISIBLE_DEVICES=; D=results/review_next/lowsig; L=logs/diag_lowsig.log
echo "[lowsig $(TZ=America/Chicago date '+%m-%d %H:%M %Z') git $(git rev-parse --short HEAD)] start grid_dev (trials 2560..2623)" >> $L
nice -n 10 taskset -c 168-175 $P $D/measure_grid_dev.py UMi28 UMi28HSd 8 > $D/log_grid_UMi28HSd.txt 2>&1 &
nice -n 10 taskset -c 176-183 $P $D/measure_grid_dev.py S2 HSd 8 > $D/log_grid_HSd.txt 2>&1 &
wait
CUDA_VISIBLE_DEVICES= taskset -c 168 $P $D/make_union_grid.py UMi28 UMi28HSd UMi28HSUd >> $D/log_grid_UMi28HSd.txt 2>&1
CUDA_VISIBLE_DEVICES= taskset -c 168 $P $D/make_union_grid.py "" HSd HSUd >> $D/log_grid_HSd.txt 2>&1
echo "[lowsig $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] GRID_DEV_DONE" >> $L
