#!/bin/bash
# Seed repeats a2 / a3 for D3 (S2c), SV8e, MIX3 (user decision 2026-09-29 CDT: "추천 순서로"; the SEEDS16e4 pattern, frozen recipe).
# Training only (no BLER): run_d2_sx.py --attempt 2|3 --fallback 1 --no-gbprime, one GPU each.  D3 a2 was started by hand on GPU 1
# at 16:4x CDT (same command); this script starts the other five.  The BLER evaluation follows its own registration.
cd /home/HTJ/t2/conf; P=~/miniforge3/envs/torch/bin/python
tr () { CUDA_VISIBLE_DEVICES=$1 $P code/run_d2_sx.py --prior $2 --ntrain 160000 --tag $3 --attempt $4 --fallback 1 --no-gbprime \
          > logs/seeds3_$2_a$4.log 2>&1; echo "rc=$?" >> logs/seeds3_$2_a$4.log; }
tr 2 S2c D3B16e4 3 & tr 3 SV8e SVB16e4 2 & tr 4 SV8e SVB16e4 3 & tr 5 MIX3 MXB16e4 2 &
wait
tr 2 MIX3 MXB16e4 3          # the sixth job, on the first lane to free up (GPU 2)
echo "SEEDS3_TRAIN_DONE" >> logs/seeds3_train.log
