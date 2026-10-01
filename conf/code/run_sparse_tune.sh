#!/bin/bash
# SPARSE16e4 development tuning (pilot-only NMSE, no BLER) on the six static datasets; 2 BLAS threads per job, CPU, GPUs hidden.
cd /home/HTJ/t2_wtSBL/conf; P=~/miniforge3/envs/torch/bin/python
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 CUDA_VISIBLE_DEVICES=
for c in "S2 C2" "S2 C6" "S2c C2" "SV8e C2" "UMi28 C2" "MIX3 C2"; do set -- $c
  $P code/sparse_tune.py --prior $1 --cell $2 --n 256 > logs/sparse_tune_$1_$2.log 2>&1 &
done; wait; echo SPARSE_TUNE_DONE >> logs/sparse_tune.log
