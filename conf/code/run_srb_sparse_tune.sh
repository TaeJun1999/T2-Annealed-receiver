#!/bin/bash
# Sionna RT room (prior SRB, cell C2) development tuning of the sparse baselines -- NEXT_EXPERIMENTS_SPARSE16e4 §1 rule, unchanged
# (v2b grid, n = 256 per SNR, pilot-only NMSE, NO BLER); 2 BLAS threads, CPU, GPUs hidden (run_sparse_tune.sh's settings).
# Development channels = SRB test pool (dmimo.py docstring).  Usage: tmux new -d -s sptsrb "bash code/run_srb_sparse_tune.sh"
cd /home/HTJ/t2/conf; P=~/miniforge3/envs/torch/bin/python
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 CUDA_VISIBLE_DEVICES=
[ -e results/sparse/tune_SRB_C2.json ] && { echo "tune_SRB_C2.json exists" >> logs/sparse_tune.log; exit 1; }
echo "[sparse_tune SRB $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] start (git $(git rev-parse --short HEAD))" >> logs/sparse_tune.log
$P code/sparse_tune.py --prior SRB --cell C2 --n 256 > logs/sparse_tune_SRB_C2.log 2>&1
echo "[sparse_tune SRB $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] SPARSE_TUNE_DONE rc=$?" >> logs/sparse_tune.log
