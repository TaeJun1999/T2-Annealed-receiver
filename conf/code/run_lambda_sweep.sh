#!/bin/bash
# §6e lambda sweep on D1.  One lambda per GPU as they free up.  Diagnostic only -- no arm comes out of this.
cd /home/HTJ/t2/conf
G=$1; LAM=$2
CUDA_VISIBLE_DEVICES=$G ~/miniforge3/envs/torch/bin/python -u code/run_d1_variant.py \
    --variant V3 --ntrain 160000 --attempt 1 --device cuda --tag L${LAM} --jac-reg $LAM \
    > logs/run_V3_D1_lam${LAM}.console.log 2>&1
echo "EXIT_lam${LAM}=$?" >> logs/lambda_sweep.log
