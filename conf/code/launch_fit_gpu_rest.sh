#!/bin/bash
# The 20 configurations the GPU launcher did not cover (it ran only the 4 the CPU had not finished).
# Round-robin over GPUs 2-5, cheap-to-expensive within each lane.  TAG routes output to gmm_fits_D2_n16e4.
cd /home/HTJ/t2/conf
P=~/miniforge3/envs/torch/bin/python; L=logs/fit_D2_n16e4_gpu.log; TAG=n16e4
lane () {  # $1 = GPU, rest = "Nr fam K" triples
  G=$1; shift
  while [ $# -ge 3 ]; do
    CUDA_VISIBLE_DEVICES=$G $P code/fit_gpu.py $1 $2 $3 160000 $TAG >> $L 2>&1
    shift 3
  done
  echo "[gpu-fit] lane GPU$G done $(date '+%T')" >> $L
}
lane 2  4 full 16   4 full 64   4 full 256   4 kron 32   8 full 32   &
lane 3  4 full 32   4 full 128  4 full 512   4 kron 64   8 full 128  &
lane 4  4 kron 16   4 kron 128  8 full 16    8 kron 16   8 kron 64   &
lane 5  4 kron 256  8 full 64   8 full 256   8 kron 32   8 kron 128  &
wait
echo "[gpu-fit] all 20 remaining configs finished $(date '+%T')" >> $L
