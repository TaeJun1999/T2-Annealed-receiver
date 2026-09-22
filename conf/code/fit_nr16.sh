#!/bin/bash
# (10_SPEC_stageC §7) GMM fit grid for the co-dimension cell C6 (Nr=16, Nt=4) at the equal budget
# N_train = 1e4.  Base grid K <= 512, both families, same kappa grid / restarts / selection rule as
# every other fit; §6l's rule then applies -- extend to K=1024 only if b* lands on the boundary.
# Six lanes, expensive-first within each lane so the longest job starts at t=0.
cd /home/HTJ/t2/conf
P=~/miniforge3/envs/torch/bin/python; L=logs/fit_D2_nr16.log; TAG=NR16
lane () { G=$1; shift
  while [ $# -ge 2 ]; do
    CUDA_VISIBLE_DEVICES=$G $P code/fit_gpu.py 16 $1 $2 10000 $TAG >> $L 2>&1
    shift 2
  done
  echo "[nr16] lane GPU$G done $(date '+%T')" >> $L
}
echo "[nr16] $(date '+%T') start: Nr=16 Nt=4 N=1e4, K<=512, full+kron" >> $L
lane 0  full 512  full 64   &
lane 1  kron 512  kron 64   &
lane 2  full 256  full 32   &
lane 3  kron 256  kron 32   &
lane 4  full 128  full 16   &
lane 5  kron 128  kron 16   &
wait
echo "[nr16] $(date '+%T') ALL 12 CONFIGS DONE" >> $L
ls results/gmm_fits_D2_NR16/ >> $L 2>&1
