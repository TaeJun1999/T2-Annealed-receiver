#!/usr/bin/env bash
set -euo pipefail
cd /home/HTJ/t2_wtE5
export CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
qdir=conf/results/review_next/qam16
{
  TZ=America/Chicago date '+%Y-%m-%d %H:%M:%S %Z'
  git rev-parse HEAD
  git status --short
  lock id /home/HTJ/t2/Demo
  printf '%s\n' 'GPU=disabled; CPU affinity=4-5; single process and BLAS/torch thread'
  sha256sum conf/code/{common,arms,runner,diag_sigma_coverage}.py
} > "$qdir/execution_context.txt"
for check in unit regression smoke; do
  TZ=America/Chicago date '+%Y-%m-%d %H:%M:%S %Z'
  taskset -c 4-5 /home/HTJ/miniforge3/envs/torch/bin/python -B "$qdir/checks.py" "$check" > "$qdir/$check.stdout.log" 2> "$qdir/$check.stderr.log"
  cat "$qdir/$check.stdout.log"
done
TZ=America/Chicago date '+%Y-%m-%d %H:%M:%S %Z'
printf '%s\n' E5_CHECKS_DONE
