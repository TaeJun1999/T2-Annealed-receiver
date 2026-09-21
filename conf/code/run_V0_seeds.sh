#!/bin/bash
# Stage C V0: attempts 2 and 3 at N'=1.6e5 (10_SPEC_stageC.md §4 allows up to 3 attempts).
# Same frozen recipe, same budget; only the attempt seed differs.  No hyperparameter is touched.
cd /home/HTJ/t2/conf
G=$1; A=$2
CUDA_VISIBLE_DEVICES=$G ~/miniforge3/envs/torch/bin/python code/run_d2_sx.py \
    --ntrain 160000 --attempt $A --gmm-ntrain 10000 \
    > logs/d2sx_N160000_a$A.log 2>&1
echo "EXIT_a$A=$?" >> logs/d2sx_N160000_seeds.log
