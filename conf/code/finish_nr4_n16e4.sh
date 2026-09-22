#!/bin/bash
# Record-completeness only: the three Nr=4 configs at N=1.6e5 that were stopped at 15:10 to free GPUs for
# §6l.  Nr=4 serves C3/C4 (sanity cells) and no planned table reads them.  Runs on GPU 5 when it is free.
cd /home/HTJ/t2/conf; P=~/miniforge3/envs/torch/bin/python; L=logs/fit_D2_n16e4_gpu.log
free () { [ -z "$(nvidia-smi -i $1 --query-compute-apps=pid --format=csv,noheader 2>/dev/null)" ]; }
for cfg in "4 kron 64" "4 kron 128" "4 kron 256"; do
  until free 5; do sleep 60; done
  echo "[gpu-fit] $(date '+%T') GPU 5 -> Nr=4 leftover: $cfg (record completeness)" >> $L
  CUDA_VISIBLE_DEVICES=5 $P code/fit_gpu.py $cfg 160000 n16e4 >> $L 2>&1
done
echo "[gpu-fit] $(date '+%T') Nr=4 leftovers finished" >> $L
