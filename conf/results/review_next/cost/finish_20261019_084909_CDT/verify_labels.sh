#!/usr/bin/env bash
# Saved development arrays only; sequential, no receiver or GPU work.
set -euo pipefail
cd /home/HTJ/t2_wtCost
export CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
out=conf/results/review_next/cost/finish_20261019_084909_CDT
log=conf/logs/cost/labels_20261019_084909_CDT_r2.log
err=conf/logs/cost/labels_20261019_084909_CDT_r2.err
[[ ! -e "$log" && ! -e "$err" ]] || exit 2
exec > >(tee "$log") 2> >(tee "$err" >&2)
TZ=America/Chicago date '+%Y-%m-%d %H:%M:%S %Z'
git rev-parse HEAD
git status --short
lock id conf/code || true
lock id Demo || true
taskset -c 1,97 /home/HTJ/miniforge3/envs/torch/bin/python -B "$out/check_labels.py"
sha256sum --check --quiet "$out/protected.sha256"
echo PROTECTED_FILES_SHA256_UNCHANGED_PASS
git diff --exit-code HEAD -- conf/code/arms.py conf/code/score.py conf/code/runner.py conf/code/common.py conf/code/bench_moduleH_ep.py Demo
echo SHARED_CODE_GIT_DIFF_EMPTY_PASS
TZ=America/Chicago date '+%Y-%m-%d %H:%M:%S %Z'
echo COST_FINISH_CHECKS_DONE
