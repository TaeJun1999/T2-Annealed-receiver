#!/bin/bash
# (NEXT_EXPERIMENTS_B32e4 v2 §1, after §5 is committed) evaluation runs on the TEST set, CPU receiver, all arms:
#  ① judging  B32e4     C2      _best.pt   ③ report B32e4last C2 last-EMA   ② report B32e4x C5 C1 _best.pt
# sequential (192 workers each), then analysis + run_manifest per tag and the §1 acceptance check.
# Usage: run_b32e4_eval.sh <kron_K> <ll_val|kron> <best_sha> <last_sha>
cd /home/HTJ/t2/conf
P=~/miniforge3/envs/torch/bin/python
L=logs/run_b32e4_eval.log
log () { echo "[b32e4eval $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $*" | tee -a $L >> logs/queue.log; }
[ -n "$(git -C /home/HTJ/t2 status --porcelain conf/code)" ] && { log "ABORT: conf/code dirty"; exit 1; }
CK=/home/HTJ/t2/conf/ckpt
COMMON="--testbed D2 --prior S2 --n 2560 --chunk 40 --ntrain 320000"
log "start (git $(git rev-parse --short HEAD))"
$P code/runner.py run $COMMON --cell C2 --stagec-ckpt $CK/d2sx_N320000_a1_best.pt --tag B32e4 > logs/run_D2_B32e4.log 2>&1 \
  || { log "ABORT: run B32e4 failed"; exit 1; }
log "run B32e4 (judging) done"
$P code/runner.py analysis --testbed D2 --tag B32e4 > logs/analysis_B32e4.log 2>&1; log "analysis B32e4 rc=$?"
$P code/runner.py run $COMMON --cell C2 --stagec-ckpt $CK/d2sx_N320000_a1.pt --tag B32e4last > logs/run_D2_B32e4last.log 2>&1 \
  || { log "ABORT: run B32e4last failed"; exit 1; }
$P code/runner.py analysis --testbed D2 --tag B32e4last > logs/analysis_B32e4last.log 2>&1; log "B32e4last done"
$P code/runner.py run $COMMON --cell C5 C1 --stagec-ckpt $CK/d2sx_N320000_a1_best.pt --tag B32e4x > logs/run_D2_B32e4x.log 2>&1 \
  || { log "ABORT: run B32e4x failed"; exit 1; }
$P code/runner.py analysis --testbed D2 --tag B32e4x > logs/analysis_B32e4x.log 2>&1; log "B32e4x done"
for T in B32e4 B32e4last B32e4x; do $P code/run_manifest.py --tag $T >> $L 2>&1; done
$P code/b32e4_accept.py --kron-K $1 --ll-val $2 --best-sha $3 --last-sha $4 >> $L 2>&1; log "acceptance rc=$?"
log "B32E4_EVAL_DONE"
