#!/bin/bash
# stage 1 re-run of S1D2C6 (first attempt: missing worktree link results/gmm_fits_D2_NR16 -> FileNotFoundError, no chunk written).
# Waits for STAGE1_DONE so the CPU pool is not shared, then runs the same pilot command as run_stage1.sh.
cd /home/HTJ/t2_wtS/conf; P=~/miniforge3/envs/torch/bin/python; L=logs/stage1.log
until grep -q STAGE1_DONE $L; do sleep 120; done
CUDA_VISIBLE_DEVICES= $P code/runner.py run --testbed D2 --prior S2 --cell C6 --snr -3 0 3 6 9 12 15 --n 1280 --chunk 40 --skip0 2560 \
  --ntrain 10000 --stagec-ckpt /home/HTJ/t2/conf/ckpt/d2sx_NR16_N10000_a1.pt \
  --arm M-ours-dscore-C-V1 M-ours-bstar R2-ours-G R1-turbo R3-bigamp R0-pilot R5-genie --tag S1D2C6 > logs/run_S1D2C6.log 2>&1
rc=$?; $P code/runner.py analysis --testbed D2 --tag S1D2C6 > logs/analysis_S1D2C6.log 2>&1
echo "[stage1 $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] B: S1D2C6 re-run rc=$rc analysis rc=$?" >> $L
echo "[stage1 $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] STAGE1_C6_DONE" >> $L
