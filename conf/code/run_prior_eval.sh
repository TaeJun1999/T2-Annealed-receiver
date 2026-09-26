#!/bin/bash
# Generic TEST-set evaluation of a D2-pipeline prior variant after its pre-registration §5 is committed
# (NEXT_EXPERIMENTS_D3B16e4 / _SVB16e4 / _38901 §1; generalises run_nr16b_eval.sh): CPU receiver, all arms, cell C2,
#   ① measurement tag <TAG>      = <ckpt_stem>_best.pt        ② report-only tag <TAG>last = <ckpt_stem>.pt (last-EMA)
# sequential, then analysis + run_manifest + guard_report + recovery_ci per tag, eval_accept (chunk plan, meta, ckpt
# identity, R5-genie replay of the last tag against the best tag, grid completeness) and the unpaired recovery
# difference against the D2 headline (frontier_ci.py --recovery).
# Usage: run_prior_eval.sh <prior> <TAG> <ckpt_stem> <bstar> <kron_K|-> <ll_val> <best_sha> <last_sha> [grid]
#   prior  S2c | SV8e | UMi28 | MIX3         bstar  kron | gmm<K>        kron_K  '-' when bstar is a full family
#   grid   default "full:16,32,64,128,256,512 kron:16,32,64,128,256,512,1024,2048" (append ,4096 when merged)
cd /home/HTJ/t2/conf
P=~/miniforge3/envs/torch/bin/python
PR=$1; TAG=$2; ST=$3; BS=$4; KK=$5; LL=$6; BSHA=$7; LSHA=$8
GRID=${9:-"full:16,32,64,128,256,512 kron:16,32,64,128,256,512,1024,2048"}
L=logs/run_prior_eval_$TAG.log
log () { echo "[prior_eval $TAG $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $*" | tee -a $L >> logs/queue.log; }
[ $# -ge 8 ] || { log "ABORT: usage"; exit 1; }
[ -n "$(git -C /home/HTJ/t2 status --porcelain conf/code)" ] && { log "ABORT: conf/code dirty"; exit 1; }
[ -L results/gmm_fits_D2_${TAG}last ] || { log "ABORT: fits link gmm_fits_D2_${TAG}last missing"; exit 1; }
CK=/home/HTJ/t2/conf/ckpt
[ -f $CK/${ST}_best.pt ] && [ -f $CK/$ST.pt ] || { log "ABORT: checkpoints $ST(.pt,_best.pt) missing"; exit 1; }
[ "$(sha256sum $CK/${ST}_best.pt | cut -c1-16)" = "$BSHA" ] || { log "ABORT: best sha differs from §5"; exit 1; }
[ "$(sha256sum $CK/$ST.pt | cut -c1-16)" = "$LSHA" ] || { log "ABORT: last sha differs from §5"; exit 1; }
KARG=""; [ "$KK" != "-" ] && KARG="--kron-K $KK"
COMMON="--testbed D2 --prior $PR --n 2560 --chunk 40 --ntrain 160000 --cell C2"
log "start (git $(git rev-parse --short HEAD)) prior=$PR bstar=$BS kron_K=$KK ll_val=$LL best=$BSHA last=$LSHA ckpt=$ST"
$P code/runner.py run $COMMON --stagec-ckpt $CK/${ST}_best.pt --tag $TAG > logs/run_D2_$TAG.log 2>&1 \
  || { log "ABORT: run $TAG failed"; exit 1; }
log "run $TAG (measurement) done"
$P code/runner.py analysis --testbed D2 --tag $TAG > logs/analysis_$TAG.log 2>&1; log "analysis $TAG rc=$?"
$P code/runner.py run $COMMON --stagec-ckpt $CK/$ST.pt --tag ${TAG}last > logs/run_D2_${TAG}last.log 2>&1 \
  || { log "ABORT: run ${TAG}last failed"; exit 1; }
$P code/runner.py analysis --testbed D2 --tag ${TAG}last > logs/analysis_${TAG}last.log 2>&1; log "${TAG}last done"
# decision SNRs of the registered pair (anchor b*) as analysis printed them for the measurement tag -- the recovery R is
# reported at -3 dB (primary) and at these points (secondary); never chosen by hand
DP=$($P - <<PY
import re
t = open("results/tables_D2_$TAG.txt").read()
m = re.search(r"M-ours-bstar -> M-ours-dscore-C-V1.*?\n\s*decision SNRs \[([^\]]*)\]", t, re.S)
print(" ".join(x.strip("' ") for x in m.group(1).split(",")) if m and m.group(1).strip() else "")
PY
)
log "decision SNRs (anchor b*, tag $TAG): ${DP:-none}"
for T in $TAG ${TAG}last; do
  $P code/run_manifest.py --tag $T >> $L 2>&1
  $P code/guard_report.py --raw raw_$T --testbed D2 > results/guard_D2_$T.txt 2>&1
  $P code/recovery_ci.py --raw raw_$T --cell C2 --snrs -3 > results/review_next/recovery_$T.txt 2>&1
  [ -n "$DP" ] && $P code/recovery_ci.py --raw raw_$T --cell C2 --snrs $DP >> results/review_next/recovery_$T.txt 2>&1
done
$P code/eval_accept.py --prior $PR --bstar $BS $KARG --tag $TAG:best:$BSHA:C2 --tag ${TAG}last:last:$LSHA:C2 --ntrain 160000 \
  --ll-val $LL --ref-raw raw_$TAG --fits-dir results/gmm_fits_D2_$TAG --grid "$GRID" > results/review_next/${TAG}_accept.txt 2>&1
log "acceptance rc=$? ($(head -1 results/review_next/${TAG}_accept.txt))"
$P code/frontier_ci.py --recovery "raw_$TAG:C2:-3" "raw_B16e4k:C2:-3" > results/review_next/recovery_diff_$TAG.txt 2>&1
$P code/frontier_ci.py --recovery "raw_${TAG}last:C2:-3" "raw_B16e4k:C2:-3" >> results/review_next/recovery_diff_$TAG.txt 2>&1
[ -n "$DP" ] && $P code/frontier_ci.py --recovery "raw_$TAG:C2:$(echo $DP | tr ' ' ',')" "raw_B16e4k:C2:-3,0,3" \
  >> results/review_next/recovery_diff_$TAG.txt 2>&1
log "recovery diff rc=$? (secondary at decision SNRs: ${DP:-none} vs D2 -3,0,3)"
log "PRIOR_EVAL_DONE"
