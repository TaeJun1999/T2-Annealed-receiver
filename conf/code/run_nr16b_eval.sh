#!/bin/bash
# (NEXT_EXPERIMENTS_C6B16e4 v2 §1, after §5 is committed) C6 (Nr=16) equal-budget N'=1.6e5 evaluation on the TEST set,
# CPU receiver, all arms (= NR16run2 configuration):
#   ① measurement-judging  NR16B16e4      C6  _best.pt        ② report-only  NR16B16e4last  C6  last-EMA
# sequential (192 workers each, ~4.5 h each at b* kron K=4096), then analysis + run_manifest + guard_report per tag,
# eval_accept (chunk plan, meta, ckpt identity, R5-genie replay vs raw_NR16run2, grid completeness) and recovery_ci.
# Usage: run_nr16b_eval.sh <kron_K> <ll_val|kron> <best_sha> <last_sha> [ckpt_stem]
#   ckpt_stem = the §3d attempt that §5 records (default d2sx_NR16_N160000_a1; attempt 2 = d2sx_NR16_N160000_a1_fb2)
cd /home/HTJ/t2/conf
P=~/miniforge3/envs/torch/bin/python
L=logs/run_nr16b_eval.log
log () { echo "[nr16beval $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $*" | tee -a $L >> logs/queue.log; }
[ -n "$(git -C /home/HTJ/t2 status --porcelain conf/code)" ] && { log "ABORT: conf/code dirty"; exit 1; }
[ -L results/gmm_fits_D2_NR16B16e4last ] || { log "ABORT: fits link gmm_fits_D2_NR16B16e4last missing"; exit 1; }
CK=/home/HTJ/t2/conf/ckpt
ST=${5:-d2sx_NR16_N160000_a1}
[ -f $CK/${ST}_best.pt ] && [ -f $CK/$ST.pt ] || { log "ABORT: checkpoints $ST(.pt,_best.pt) missing"; exit 1; }
COMMON="--testbed D2 --prior S2 --n 2560 --chunk 40 --ntrain 160000 --cell C6"
log "start (git $(git rev-parse --short HEAD)) kron_K=$1 ll_val=$2 best=$3 last=$4 ckpt=$ST"
$P code/runner.py run $COMMON --stagec-ckpt $CK/${ST}_best.pt --tag NR16B16e4 > logs/run_D2_NR16B16e4.log 2>&1 \
  || { log "ABORT: run NR16B16e4 failed"; exit 1; }
log "run NR16B16e4 (measurement) done"
$P code/runner.py analysis --testbed D2 --tag NR16B16e4 > logs/analysis_NR16B16e4.log 2>&1; log "analysis NR16B16e4 rc=$?"
$P code/runner.py run $COMMON --stagec-ckpt $CK/$ST.pt --tag NR16B16e4last > logs/run_D2_NR16B16e4last.log 2>&1 \
  || { log "ABORT: run NR16B16e4last failed"; exit 1; }
$P code/runner.py analysis --testbed D2 --tag NR16B16e4last > logs/analysis_NR16B16e4last.log 2>&1; log "NR16B16e4last done"
for T in NR16B16e4 NR16B16e4last; do
  $P code/run_manifest.py --tag $T >> $L 2>&1
  $P code/guard_report.py --raw raw_$T --testbed D2 > results/guard_D2_$T.txt 2>&1
  $P code/recovery_ci.py --raw raw_$T --cell C6 --snrs -3 0 3 > results/review_next/recovery_$T.txt 2>&1
done
$P code/recovery_ci.py --raw raw_NR16run2 --cell C6 --snrs -3 0 3 > results/review_next/recovery_NR16run2.txt 2>&1
$P code/recovery_ci.py --raw raw_B16e4k --cell C2 --snrs -3 0 3 > results/review_next/recovery_B16e4k.txt 2>&1
$P code/eval_accept.py --tag NR16B16e4:best:$3:C6 --tag NR16B16e4last:last:$4:C6 --ntrain 160000 --kron-K $1 --ll-val $2 \
  --ref-raw raw_NR16run2 --fits-dir results/gmm_fits_D2_NR16B16e4 \
  --grid "full:16,32,64,128,256,512 kron:16,32,64,128,256,512,1024,2048,4096" > results/review_next/NR16B16e4_accept.txt 2>&1
log "acceptance rc=$? ($(head -1 results/review_next/NR16B16e4_accept.txt))"
log "NR16B_EVAL_DONE"
