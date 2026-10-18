#!/usr/bin/env bash
set -euo pipefail
cd /home/HTJ/t2_wtE3
export CUDA_VISIBLE_DEVICES=
export PYTHONDONTWRITEBYTECODE=1
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 BLIS_NUM_THREADS=1
export TZ=America/Chicago PYTHONUNBUFFERED=1
PY=/home/HTJ/miniforge3/envs/torch/bin/python
OUT=conf/results/review_next/sbl32
while tmux has-session -t e3_sbl32_checks2 2>/dev/null; do
    sleep 5
done
test -f "$OUT/probe_U28NR32.json"
taskset -c 0-1 "$PY" "$OUT/verify_stream_sbl32.py" | tee "$OUT/verify_stream_sbl32.out"
taskset -c 0-1 "$PY" "$OUT/finalize_report.py"
