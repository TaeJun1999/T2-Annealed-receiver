#!/bin/bash
# E1+ development screen (registration §0 / predictions; development trials 2560..2879, n 320 per point): V1, V1-ms, V4, genie at
# D2 C2 -3 / 0 / +3 dB, one runner run under tag E1MSdev.  CPU 4-15 (NUMA 0, user's cap 168), nice 10.
cd /home/HTJ/t2_wtMS/conf || exit 1
P=~/miniforge3/envs/torch/bin/python; export CUDA_VISIBLE_DEVICES=; L=logs/e1ms_dev.log; T=E1MSdev
echo "[e1ms-dev $(TZ=America/Chicago date '+%m-%d %H:%M %Z') git $(git rev-parse --short HEAD)$([ -n "$(git status --porcelain code ../Demo)" ] && echo +dirty)] start" >> $L
[ -d results/gmm_fits_D2_$T ] || { mkdir -p results/gmm_fits_D2_$T && cp -L /home/HTJ/t2/conf/results/gmm_fits_D2_B16e4k/*.npz results/gmm_fits_D2_$T/; }
nice -n 10 taskset -c 4-15 $P code/runner.py run --testbed D2 --prior S2 --cell C2 --ntrain 160000 \
  --stagec-ckpt /home/HTJ/t2/conf/ckpt/d2sx_N160000_a1.pt --chunk 40 --skip0 2560 --n 320 --snr -3 0 3 \
  --arm M-ours-dscore-C-V1 M-ours-dscore-C-V1ms M-ours-dscore-C-V4 R5-genie --ms-arm --tag $T > logs/run_D2_$T.log 2>&1
echo "[e1ms-dev $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] runner exit $? DEV_DONE" >> $L
