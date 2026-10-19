#!/bin/bash
# WORK_QUEUE 13: larger development screen (n 320 per point) of V1-clamp / V1-gmmfb; one process per (cell, modulation, SNR), nice 10.
#   16-QAM: trials 5120..5439 (E5 grid trials; only b*'s BLER was ever read there);  QPSK: trials 6000..6319 (development range).
cd /home/HTJ/t2/conf || exit 1
P=~/miniforge3/envs/torch/bin/python; export CUDA_VISIBLE_DEVICES=; D=results/review_next/lowsig; L=logs/diag_lowsig.log
echo "[lowsig $(TZ=America/Chicago date '+%m-%d %H:%M %Z') git $(git rev-parse --short HEAD)$([ -n "$(git status --porcelain code ../Demo)" ] && echo +dirty)] start screen2" >> $L
cpu=176
for cell in U28 D2; do for ms in "16qam 5120" "qpsk 6000"; do set -- $ms; for snr in 15 18 21; do
  nice -n 10 taskset -c $cpu $P $D/diag_lowsig.py $cell $1 $2 320 $snr > $D/log_screen2_${cell}_$1_$snr.txt 2>&1 &
  cpu=$((cpu + 1))
done; done; done
wait
echo "[lowsig $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] SCREEN2_DONE" >> $L
