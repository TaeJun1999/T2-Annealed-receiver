#!/bin/bash
# WORK_QUEUE 13 variant (C): retrain the two V1 checkpoints on the downward-extended sigma grids (run_d2_sx.py --sigma-tag), same rung /
# seed / data / recipe; GPU 0 (UMi28) and GPU 1 (S2) on their NUMA-0 hyperthread pairs (the dummy holds were taken down first).
cd /home/HTJ/t2/conf || exit 1
P=~/miniforge3/envs/torch/bin/python; L=logs/diag_lowsig.log
echo "[lowsig $(TZ=America/Chicago date '+%m-%d %H:%M %Z') git $(git rev-parse --short HEAD)$([ -n "$(git status --porcelain code ../Demo)" ] && echo +dirty)] start train C" >> $L
CUDA_VISIBLE_DEVICES=0 taskset -c 0,96 $P code/run_d2_sx.py --prior UMi28 --ntrain 160000 --attempt 1 --sigma-tag UMi28HSU --no-gbprime > logs/run_train_c_UMi28.log 2>&1 &
CUDA_VISIBLE_DEVICES=1 taskset -c 22,118 $P code/run_d2_sx.py --prior S2 --ntrain 160000 --attempt 1 --sigma-tag HSU --no-gbprime > logs/run_train_c_S2.log 2>&1 &
wait
echo "[lowsig $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] TRAIN_C_DONE" >> $L
