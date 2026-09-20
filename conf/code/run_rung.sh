#!/bin/bash
# conf/code/run_rung.sh -- run ONE rung's <=3 attempts (train + gate) on one GPU.
# Same frozen gates as the pre-registered ladder; every attempt appends to LADDER.md.
set -u
PY=~/miniforge3/envs/torch/bin/python
cd /home/HTJ/t2/conf
R=${RUNG:?}; export CUDA_VISIBLE_DEVICES=${GPU:-0}
echo "=== $R | GPU $CUDA_VISIBLE_DEVICES | $(date '+%F %T %Z') ==="
for A in 1 2 3; do
  echo; echo "################ $R attempt $A | $(date '+%F %T') ################"
  $PY code/runner.py train --rung "$R" --attempt "$A" --testbed D1 --device cuda || { echo "!!! train $R a$A rc=$?"; continue; }
  $PY code/runner.py gate --testbed D1 --rung "$R" --attempt "$A" --device cuda || echo "!!! gate $R a$A rc=$?"
done
echo "=== $R done ==="
