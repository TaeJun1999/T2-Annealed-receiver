#!/bin/bash
# The 4 configurations the CPU run has NOT finished (its remaining 10 EM tasks), most expensive first.
# One process per GPU, CUDA_VISIBLE_DEVICES pinned (Compute Mode = Exclusive_Process).
# GPUs 0 and 1 carry Stage C trainings and are never touched.
set -u
cd /home/HTJ/t2/conf
P=~/miniforge3/envs/torch/bin/python
L=logs/fit_D2_n16e4_gpu.log
echo "[gpu-fit] $(date '+%F %T %Z') start -- 4 configs the CPU run has not completed, expensive first" >> $L
# TAG must match the CPU run's --tag: it routes output to results/gmm_fits_D2_$TAG/.  Omitting it
# sent the fits to results/gmm_fits_D2/ (the ORIGINAL n=1e4 dir) -- see fit_gpu.py's docstring.
TAG=n16e4
nohup env CUDA_VISIBLE_DEVICES=2 $P code/fit_gpu.py 8 kron 512 160000 $TAG >> $L 2>&1 &
nohup env CUDA_VISIBLE_DEVICES=3 $P code/fit_gpu.py 8 kron 256 160000 $TAG >> $L 2>&1 &
nohup env CUDA_VISIBLE_DEVICES=4 $P code/fit_gpu.py 4 kron 512 160000 $TAG >> $L 2>&1 &
nohup env CUDA_VISIBLE_DEVICES=5 $P code/fit_gpu.py 8 full 512 160000 $TAG >> $L 2>&1 &
wait
echo "[gpu-fit] $(date '+%F %T %Z') all four finished" >> $L
