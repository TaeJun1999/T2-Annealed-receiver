#!/usr/bin/env bash
set -euo pipefail
cd /home/HTJ/t2_wtE5
export CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
qdir=conf/results/review_next/qam16
{
 TZ=America/Chicago date '+%Y-%m-%d %H:%M:%S %Z'
 printf '%s\n' 'Original run interrupted during D2 explicit QPSK after omitted QPSK passed. No UMi trial evaluated yet. UMi input corrected to +12 dB: smallest median chunk time in existing original log. Completed omitted raw reused; all original logs preserved.'
 sha256sum conf/code/{common,arms,runner,diag_sigma_coverage}.py
} > "$qdir/continuation_context.txt"
for check in regression smoke; do
 TZ=America/Chicago date '+%Y-%m-%d %H:%M:%S %Z'
 taskset -c 4-5 /home/HTJ/miniforge3/envs/torch/bin/python -B "$qdir/checks.py" "$check" > "$qdir/$check.continued.stdout.log" 2> "$qdir/$check.continued.stderr.log"
 cat "$qdir/$check.continued.stdout.log"
done
TZ=America/Chicago date '+%Y-%m-%d %H:%M:%S %Z'
printf '%s\n' E5_CHECKS_DONE
