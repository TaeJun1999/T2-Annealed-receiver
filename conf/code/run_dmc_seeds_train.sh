#!/bin/bash
# Seed repeats a2 / a3 of the V1 score network on DeepMIMO (prior DMC): the SEEDS16e4 / run_seeds3_train.sh pattern, frozen recipe.
# Training only (no BLER): run_d2_sx.py --attempt 2|3 --fallback 1 --no-gbprime, one GPU each, each pinned from the start to one
# hyper-thread pair on the GPU's NUMA node (result-neutral; GPU 0-3 = node0).  User instruction 2026-10-10 CDT: the GPUs handed
# back to us run project work.  The BLER evaluation of these seeds needs its own registration.
# Usage: run_dmc_seeds_train.sh <gpu_a2> <gpu_a3>
cd /home/HTJ/t2/conf; P=~/miniforge3/envs/torch/bin/python
tr () { CUDA_VISIBLE_DEVICES=$1 taskset -c $3 $P code/run_d2_sx.py --prior DMC --ntrain 160000 --tag DMCB16e4 --attempt $2 --fallback 1 \
          --no-gbprime > logs/seeds_DMC_a$2.log 2>&1; echo "rc=$?" >> logs/seeds_DMC_a$2.log; }
tr $1 2 20,116 & tr $2 3 21,117 &
wait
echo "DMC_SEEDS_TRAIN_DONE $(TZ=America/Chicago date '+%m-%d %H:%M %Z')" >> logs/seeds_DMC_train.log
