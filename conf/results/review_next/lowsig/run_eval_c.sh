#!/bin/bash
# WORK_QUEUE 13 variant (C) on the SELECTION_RULE.md development points: run_eval_c.sh <U28|D2> <first cpu>  (6 processes, nice 10).
# After the S2 training ends this script is also what re-holds GPU 1 (user: keep GPUs held) -- see run_after_train_s2.sh.
cd /home/HTJ/t2/conf || exit 1
P=~/miniforge3/envs/torch/bin/python; export CUDA_VISIBLE_DEVICES=; D=results/review_next/lowsig; L=logs/diag_lowsig.log
cell=$1; cpu=$2
echo "[lowsig $(TZ=America/Chicago date '+%m-%d %H:%M %Z') git $(git rev-parse --short HEAD)$([ -n "$(git status --porcelain code ../Demo)" ] && echo +dirty)] start eval_c $cell" >> $L
for ms in "16qam 5120" "qpsk 6000"; do set -- $ms; for snr in 15 18 21; do
  nice -n 10 taskset -c $cpu $P $D/eval_c.py $cell $1 $2 320 $snr > $D/log_evalc_${cell}_$1_$snr.txt 2>&1 &
  cpu=$((cpu + 1))
done; done
wait
echo "[lowsig $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] EVAL_C_DONE $cell" >> $L
