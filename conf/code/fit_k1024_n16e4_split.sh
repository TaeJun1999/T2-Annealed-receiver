#!/bin/bash
# (10_SPEC_stageC §6l) kron K=1024 at N=1.6e5, Nr=8 -- the fit that decides whether B16e4's GMM arm sits
# on a truncated grid.  At N=4e4 one restart took 2532 s; at N=1.6e5 each is ~4x that, so the three
# restarts run on THREE GPUs in parallel via fit_gpu.py --restart r (the original CPU protocol treats
# every (kappa, restart) as an independent pool task with its own seed tuple, so this changes no RNG
# draw), then --merge selects by validation log-likelihood only and writes the ordinary fit file.
cd /home/HTJ/t2/conf
P=~/miniforge3/envs/torch/bin/python; L=logs/fit_k1024.log; TAG=K1024n160000
GPUS=(2 3 4)

free () { [ -z "$(nvidia-smi -i $1 --query-compute-apps=pid --format=csv,noheader 2>/dev/null)" ]; }

for r in 0 1 2; do
  G=${GPUS[$r]}
  until free $G; do sleep 30; done
  echo "[k1024] $(date '+%T') GPU $G -> kron K=1024 Nr=8 N=160000 restart $r (tag $TAG)" >> $L
  CUDA_VISIBLE_DEVICES=$G $P code/fit_gpu.py 8 kron 1024 160000 $TAG --restart $r >> $L 2>&1 &
  sleep 20                      # let the CUDA context come up before the next GPU is probed
done
wait
echo "[k1024] $(date '+%T') all 3 restarts done -> merge" >> $L
$P code/fit_gpu.py 8 kron 1024 160000 $TAG --merge >> $L 2>&1
echo "[k1024] $(date '+%T') N=160000 K=1024 MERGE EXIT=$?" >> $L
