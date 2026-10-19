#!/bin/bash
# wait for the S2 retraining (variant C) to end, re-hold GPU 1 (user instruction: keep GPUs held), then evaluate C on D2.
until grep -q TRAIN_C_DONE /home/HTJ/t2/conf/logs/diag_lowsig.log; do sleep 60; done
tmux new-session -d -s gpuhold1 "bash /home/HTJ/t2/conf/results/review_next/gpuhold/run_hold.sh 1 22,118"
bash /home/HTJ/t2/conf/results/review_next/lowsig/run_eval_c.sh D2 126
