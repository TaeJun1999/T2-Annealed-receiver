#!/bin/bash
# Stage C: is the Jacobian a valid covariance as the training budget grows?
# Fixed checkpoints, frozen sigma grid, nothing retrained or tuned.
cd /home/HTJ/t2/conf
SNAP="$1"
run () {   # $1 = tag, $2 = ckpt path
  OMP_NUM_THREADS=2 ~/miniforge3/envs/torch/bin/python code/jacobian_psd.py \
      --ckpt "$2" --n 128 --threads 2 \
      --out "results/diag/jacobian-psd_D2_$1.npz" > "logs/jacpsd_$1.log" 2>&1
  echo "EXIT_$1=$?" >> logs/jacpsd_budget.log
}
run N10000_a1  ckpt/d2sx_N10000_a1.pt
run N40000_a1  ckpt/d2sx_N40000_a1.pt
run N160000    "$SNAP"
echo DONE >> logs/jacpsd_budget.log
