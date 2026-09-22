#!/bin/bash
# (10_SPEC_stageC §6l, second half) K=1024 at the LARGER budgets.
#
# The N=1e4 result does NOT generalise.  Nr=8 kron ll_val, K=256 -> K=512 gain by budget:
#   N=1e4   -23.936 -> -23.473   (+0.46, and K=1024 is WORSE at -23.573 -> b* interior)
#   N=4e4   -19.699 -> -17.344   (+2.36, still climbing)
#   N=1.6e5 -18.417 -> -14.636   (+3.78, climbing FASTER)
# So at the larger budgets b* = K=512 sits on a grid edge with the likelihood still rising steeply,
# and K=1024 is likely to win there.  If it does, the GMM arm in tables_D2_B4e4 / B16e4 is fitted on
# a truncated grid -- i.e. an unfairly weak baseline at exactly the budget of the gate-passing table.
# 01_RULES:76 forbids that.  Selection stays validation-log-likelihood only; BLER is never consulted.
cd /home/HTJ/t2/conf
P=~/miniforge3/envs/torch/bin/python
L=logs/fit_k1024.log

free_gpu () {
  for g in 5 4 3 2 0 1; do
    if [ -z "$(nvidia-smi -i $g --query-compute-apps=pid --format=csv,noheader 2>/dev/null)" ]; then
      echo $g; return
    fi
  done
}

# N=4e4 first: cheaper, and it decides whether the already-published B4e4 table needs a re-run.
for NT in 40000 160000; do
  until [ -n "$(free_gpu)" ]; do sleep 120; done
  G=$(free_gpu)
  TAG=K1024n$NT
  echo "[k1024] $(date '+%T') GPU $G -> kron K=1024, Nr=8, N=$NT (tag $TAG)" >> $L
  CUDA_VISIBLE_DEVICES=$G $P code/fit_gpu.py 8 kron 1024 $NT $TAG >> $L 2>&1
  echo "[k1024] $(date '+%T') N=$NT EXIT=$?" >> $L
done
echo "[k1024] $(date '+%T') K1024_BIG_DONE" >> $L
