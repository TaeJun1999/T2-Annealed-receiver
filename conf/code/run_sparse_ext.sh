#!/bin/bash
# SPARSE16e4 tuning, FINAL edge extension (rule: an edge axis is extended step by step; this is the last step): after the v2b
# picks of the five C2 datasets exist, copy them to results/sparse/v2b/ and, for every dataset whose rho pick (SBL or OMP) sits
# at the v2b edge 16, evaluate rho = 32 only and pick over the union (sparse_tune.py --rhos 32 --merge-with).  2 BLAS threads each.
cd /home/HTJ/t2_wtSBL/conf; P=~/miniforge3/envs/torch/bin/python; L=logs/sparse_ext.log
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 CUDA_VISIBLE_DEVICES=
C2="MIX3 S2 S2c SV8e UMi28"
all_done () { for p in $C2; do [ -f results/sparse/pick_${p}_C2.json ] || return 1; done; }
until all_done; do sleep 120; done
mkdir -p results/sparse/v2b
for p in $C2; do
  cp results/sparse/tune_${p}_C2.json results/sparse/pick_${p}_C2.json results/sparse/v2b/
  e=$($P -c "import json; d=json.load(open('results/sparse/pick_${p}_C2.json')); print(int(d.get('edge_rho_sbl', False) or d.get('edge_rho_omp', False)))")
  if [ "$e" = "1" ]; then
    echo "[ext $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $p C2: rho 16 at edge -> rho 32" >> $L
    $P code/sparse_tune.py --prior $p --cell C2 --n 256 --rhos 32 --merge-with results/sparse/v2b/tune_${p}_C2.json > logs/sparse_ext_$p.log 2>&1 &
  else echo "[ext $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $p C2: interior -> keep v2b" >> $L; fi
done; wait; echo "SPARSE_EXT_C2_DONE" >> $L
