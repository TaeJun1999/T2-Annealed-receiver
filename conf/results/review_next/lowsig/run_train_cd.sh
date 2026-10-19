#!/bin/bash
# SELECTION_RULE.md addendum (Fable M1): re-train C on the development-trial grids (UMi28HSUd / HSUd), GPU 0 / 1 (dummy holds taken down
# first, re-held after), then evaluate the new C ('d') on the 12 screen points and the 9 decision-point SNRs (development trials, n 320).
cd /home/HTJ/t2/conf || exit 1
P=~/miniforge3/envs/torch/bin/python; L=logs/diag_lowsig.log; D=results/review_next/lowsig
echo "[lowsig $(TZ=America/Chicago date '+%m-%d %H:%M %Z') git $(git rev-parse --short HEAD)$([ -n "$(git status --porcelain code ../Demo)" ] && echo +dirty)] start train Cd" >> $L
CUDA_VISIBLE_DEVICES=0 taskset -c 0,96 $P code/run_d2_sx.py --prior UMi28 --ntrain 160000 --attempt 1 --sigma-tag UMi28HSUd --no-gbprime > logs/run_train_cd_UMi28.log 2>&1 &
CUDA_VISIBLE_DEVICES=1 taskset -c 22,118 $P code/run_d2_sx.py --prior S2 --ntrain 160000 --attempt 1 --sigma-tag HSUd --no-gbprime > logs/run_train_cd_S2.log 2>&1 &
wait
echo "[lowsig $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] TRAIN_CD_DONE" >> $L
tmux new-session -d -s gpuhold0 "bash /home/HTJ/t2/conf/results/review_next/gpuhold/run_hold.sh 0 0,96"
tmux new-session -d -s gpuhold1 "bash /home/HTJ/t2/conf/results/review_next/gpuhold/run_hold.sh 1 22,118"
export CUDA_VISIBLE_DEVICES=
cpu=120
for job in "U28 qpsk 6000 15" "U28 qpsk 6000 18" "U28 qpsk 6000 21" "U28 16qam 5120 15" "U28 16qam 5120 18" "U28 16qam 5120 21" \
           "D2 qpsk 6000 15" "D2 qpsk 6000 18" "D2 qpsk 6000 21" "D2 16qam 5120 15" "D2 16qam 5120 18" "D2 16qam 5120 21" \
           "U28 qpsk 6000 3" "U28 qpsk 6000 6" "U28 qpsk 6000 9" "D2 qpsk 6000 -3" "D2 qpsk 6000 0" "D2 qpsk 6000 3" \
           "U28 16qam 5120 12" "D2 16qam 5120 9" "D2 16qam 5120 12"; do
  set -- $job
  nice -n 10 taskset -c $cpu $P $D/eval_c.py $1 $2 $3 320 $4 d > $D/log_evalcd_$1_$2_$4.txt 2>&1 &
  cpu=$((cpu + 1))
done
wait
echo "[lowsig $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] EVAL_CD_DONE" >> $L
