#!/bin/bash
# (10_SPEC_stageC §6l) "extend until b* is interior".  Waits for the N=4e4 kron K=1024 fit; if it beats
# K=512 on validation log-likelihood, fits K=2048 at N=4e4 with the three restarts spread over whichever
# GPUs free up (fit_gpu.py --restart, protocol-faithful), then merges.  Selection is ll_val only.
cd /home/HTJ/t2/conf
P=~/miniforge3/envs/torch/bin/python; L=logs/fit_k1024.log
F1024=results/gmm_fits_D2_K1024n40000/fit_S2_Nr8_kronK1024_n40000.npz
F512=results/gmm_fits_D2_n4e4/fit_S2_Nr8_kronK512_n40000.npz
until [ -f "$F1024" ]; do sleep 120; done
WIN=$($P - <<'EOF'
import numpy as np
a=float(np.load("results/gmm_fits_D2_K1024n40000/fit_S2_Nr8_kronK1024_n40000.npz")["ll_val"])
b=float(np.load("results/gmm_fits_D2_n4e4/fit_S2_Nr8_kronK512_n40000.npz")["ll_val"])
print(f"K1024 {a:.4f} vs K512 {b:.4f} ->", "K1024_WINS" if a > b else "K512_STAYS")
EOF
)
echo "[k2048] $(date '+%T') N=4e4: $WIN" >> $L
case "$WIN" in *K512_STAYS*) exit 0;; esac

free () { [ -z "$(nvidia-smi -i $1 --query-compute-apps=pid --format=csv,noheader 2>/dev/null)" ]; }
next_free () { while true; do for g in 5 2 3 4; do free $g && { echo $g; return; }; done; sleep 60; done; }
TAG=K2048n40000
for r in 0 1 2; do
  G=$(next_free)
  echo "[k2048] $(date '+%T') GPU $G -> kron K=2048 Nr=8 N=40000 restart $r" >> $L
  CUDA_VISIBLE_DEVICES=$G $P code/fit_gpu.py 8 kron 2048 40000 $TAG --restart $r >> $L 2>&1 &
  sleep 25
done
wait
$P code/fit_gpu.py 8 kron 2048 40000 $TAG --merge >> $L 2>&1
echo "[k2048] $(date '+%T') N=40000 K=2048 MERGE EXIT=$?" >> $L
