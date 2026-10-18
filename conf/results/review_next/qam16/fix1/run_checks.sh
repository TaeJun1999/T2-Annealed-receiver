#!/usr/bin/env bash
set -euo pipefail
set -C
cd /home/HTJ/t2_wtE5
export CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1 BLIS_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 GIT_OPTIONAL_LOCKS=0
qdir=/home/HTJ/t2_wtE5/conf/results/review_next/qam16/fix1
export TMPDIR="$qdir/tmp" XDG_CACHE_HOME="$qdir/cache" MPLCONFIGDIR="$qdir/cache/matplotlib"
mkdir -p "$TMPDIR" "$MPLCONFIGDIR"
py=/home/HTJ/miniforge3/envs/torch/bin/python
{
  TZ=America/Chicago date '+%Y-%m-%d %H:%M:%S %Z'
  git rev-parse HEAD
  git status --short
  "$py" -B /home/HTJ/.local/bin/lock id /home/HTJ/t2/Demo
  "$py" -B /home/HTJ/.local/bin/lock id /home/HTJ/t2_wtE5/Demo || true
  printf '%s\n' 'CPU=64-65; single BLAS/torch thread; GPU=disabled; seed=20260926; no test receiver evaluation'
  sha256sum conf/code/runner.py "$qdir/checks.py" "$qdir/runner_before.py"
} > "$qdir/execution_context.txt"
for check in defects regression B16e4k U28B16e4; do
  TZ=America/Chicago date '+%Y-%m-%d %H:%M:%S %Z'
  printf 'COMMAND: taskset -c 64-65 %s -B %s/checks.py %s\n' "$py" "$qdir" "$check"
  taskset -c 64-65 "$py" -B "$qdir/checks.py" "$check" > "$qdir/$check.stdout.log" 2> "$qdir/$check.stderr.log"
  cat "$qdir/$check.stdout.log"
done
taskset -c 64-65 "$py" -B "$qdir/preservation.py" after > "$qdir/preservation.after.stdout.log" 2> "$qdir/preservation.after.stderr.log"
git diff --check > "$qdir/diff_check.log" 2>&1
git diff -- conf/code/runner.py > "$qdir/implementation.diff"
TZ=America/Chicago date '+%Y-%m-%d %H:%M:%S %Z'
printf '%s\n' E5_FIX1_CHECKS_DONE
