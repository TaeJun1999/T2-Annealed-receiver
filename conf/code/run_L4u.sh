#!/bin/bash
# conf/code/run_L4u.sh -- the U-Net variant of L4 (04_SPEC §4 names "2D conv / 소형 U-Net" for L4).
# Same frozen gates, same data, same split.  L4's original three attempts are untouched.
set -u
PY=~/miniforge3/envs/torch/bin/python
cd /home/HTJ/t2/conf
export CUDA_VISIBLE_DEVICES=${GPU:-1}
echo "=== L4u (small U-Net) | CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES | $(date '+%F %T %Z') ==="
for A in 1 2 3; do
  echo; echo "################ L4u attempt $A | $(date '+%F %T') ################"
  $PY code/runner.py train --rung L4u --attempt "$A" --testbed D1 --device cuda || { echo "!!! train L4u a$A failed"; continue; }
  $PY code/runner.py gate --testbed D1 --rung L4u --attempt "$A" --device cuda
done
echo "=== L4u done ==="
