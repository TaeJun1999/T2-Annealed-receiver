#!/bin/bash
# Nr=8 FIRST.  C1/C2/C5 (every cell the equal-budget tables use) are Nr=8; Nr=4 serves C3/C4 only.
# The previous lane script put Nr=4 first, which put work no planned table reads on the critical path.
# Within a lane: most expensive (kron, large K) first so the longest job starts at t=0.
cd /home/HTJ/t2/conf
P=~/miniforge3/envs/torch/bin/python; L=logs/fit_D2_n16e4_gpu.log; TAG=n16e4
lane () { G=$1; shift
  while [ $# -ge 3 ]; do
    CUDA_VISIBLE_DEVICES=$G $P code/fit_gpu.py $1 $2 $3 160000 $TAG >> $L 2>&1
    shift 3
  done
  echo "[gpu-fit] lane GPU$G done $(date '+%T')" >> $L
}
lane 2  8 kron 128  4 kron 256  &
lane 3  8 kron 64   8 full 16   8 full 64   4 kron 128  &
lane 4  8 kron 32   8 full 128  8 full 256  4 kron 64   &
lane 5  8 kron 16                                       &
wait
echo "[gpu-fit] Nr8-first relaunch finished $(date '+%T')" >> $L
