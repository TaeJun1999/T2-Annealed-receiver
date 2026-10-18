#!/usr/bin/env bash
set -euo pipefail
cd /home/HTJ/t2_wtE3
export CUDA_VISIBLE_DEVICES=
export PYTHONDONTWRITEBYTECODE=1
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 BLIS_NUM_THREADS=1
export TZ=America/Chicago
export PYTHONUNBUFFERED=1
PY=/home/HTJ/miniforge3/envs/torch/bin/python
OUT=conf/results/review_next/sbl32
date
if [[ ! -f "$OUT/input_manifest.json" ]]; then
    taskset -c 0-1 "$PY" "$OUT/prepare_inputs.py"
fi
taskset -c 0-1 "$PY" "$OUT/regression_sbl32.py" | tee "$OUT/regression.out"
taskset -c 0-1 "$PY" conf/code/sbl_probe.py | tee "$OUT/probe.out"
date
echo SBL32_CHECKS_DONE
