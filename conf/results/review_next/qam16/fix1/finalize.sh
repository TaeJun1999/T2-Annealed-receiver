#!/usr/bin/env bash
set -euo pipefail
set -C
cd /home/HTJ/t2_wtE5
export CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export PYTHONDONTWRITEBYTECODE=1 GIT_OPTIONAL_LOCKS=0
qdir=/home/HTJ/t2_wtE5/conf/results/review_next/qam16/fix1
export TMPDIR="$qdir/tmp" XDG_CACHE_HOME="$qdir/cache" MPLCONFIGDIR="$qdir/cache/matplotlib"
py=/home/HTJ/miniforge3/envs/torch/bin/python
taskset -c 64-65 "$py" -B "$qdir/preservation_audit.py" > "$qdir/preservation.audit.stdout.log" 2> "$qdir/preservation.audit.stderr.log"
taskset -c 64-65 "$py" -B "$qdir/static_checks.py" > "$qdir/static_checks.stdout.log" 2> "$qdir/static_checks.stderr.log"
taskset -c 64-65 "$py" -B "$qdir/record.py" > "$qdir/record.stdout.log" 2> "$qdir/record.stderr.log"
git diff --check -- conf/code/runner.py docs/EXPERIMENTS.md > "$qdir/diff_check.log" 2>&1
git diff -- conf/code/runner.py > "$qdir/implementation.diff"
{
  TZ=America/Chicago date '+%Y-%m-%d %H:%M:%S %Z'
  git diff --check -- conf/code/runner.py docs/EXPERIMENTS.md
  git status --short
  git diff --stat
  sha256sum conf/code/runner.py "$qdir/checks.py" "$qdir/run_checks.sh"
  cat "$qdir/static_checks.stdout.log" "$qdir/record.stdout.log"
  printf '%s\n' E5_FIX1_FINALIZED
} > "$qdir/final_status.log"
