#!/bin/bash
# (NEXT_EXPERIMENTS_SEEDS16e4 §1, after the freeze commit) one seed-repeat tag on the TEST set: same cell, fits, trials and
# arms as the a1 tag, only the diffusion checkpoint differs.  CPU receiver, all arms; then analysis + run_manifest +
# guard_report + recovery_ci (-3 dB and the analysis table's decision SNRs), eval_accept (chunk plan, meta, ckpt identity,
# R5-genie replay against the a1 raw, grid completeness) and the `--ref-arms all` report (expected: only V0/V1/V4/V4b differ).
# Usage: run_seeds16e4.sh <prior> <TAG> <ckpt_path> <ref_raw> <bstar> <kron_K> <ll_val> <sha> <role> <grid> [cand_dir]
#   ckpt_path is RELATIVE to conf/ (the script prefixes /home/HTJ/t2/conf/).
#   e.g. run_seeds16e4.sh S2 B16e4s2 ckpt/d2sx_N160000_a2.pt raw_B16e4k kron 1024 -11.459169831224418 9465fbec56cbf834 legacy-last \
#          "full:16,32,64,128,256,512 kron:16,32,64,128,256,512,1024" results/gmm_fits_D2_K1024n160000
# For UMi28 / MIX3 tags run with CUDA_VISIBLE_DEVICES= in the environment (GPUs hidden; DECISIONS 80bae849).
cd /home/HTJ/t2/conf
P=~/miniforge3/envs/torch/bin/python
PR=$1; TAG=$2; CK=$3; REF=$4; BS=$5; KK=$6; LL=$7; SHA=$8; ROLE=$9; GRID=${10}; CAND=${11}
L=logs/run_seeds16e4_$TAG.log
log () { echo "[seeds16e4 $TAG $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $*" | tee -a $L >> logs/queue.log; }
[ $# -ge 10 ] || { log "ABORT: usage (10-11 arguments)"; exit 1; }
[ -n "$(git -C /home/HTJ/t2 status --porcelain conf/code)" ] && { log "ABORT: conf/code dirty"; exit 1; }
[ -L results/gmm_fits_D2_$TAG ] || { log "ABORT: fits link gmm_fits_D2_$TAG missing"; exit 1; }
[ -f $CK ] || { log "ABORT: checkpoint $CK missing"; exit 1; }
[ "$(sha256sum $CK | cut -c1-16)" = "$SHA" ] || { log "ABORT: checkpoint sha differs from §5"; exit 1; }
CANDARG=""; [ -n "$CAND" ] && CANDARG="--cand-dir $CAND"
log "start (git $(git rev-parse --short HEAD)) prior=$PR ckpt=$CK sha=$SHA role=$ROLE bstar=$BS kron_K=$KK ll_val=$LL ref=$REF CUDA_VISIBLE_DEVICES='${CUDA_VISIBLE_DEVICES-unset}'"
$P code/runner.py run --testbed D2 --prior $PR --cell C2 --n 2560 --chunk 40 --ntrain 160000 --stagec-ckpt /home/HTJ/t2/conf/$CK \
  --tag $TAG > logs/run_D2_$TAG.log 2>&1 || { log "ABORT: run $TAG failed"; exit 1; }
log "run $TAG done"
$P code/runner.py analysis --testbed D2 --tag $TAG > logs/analysis_$TAG.log 2>&1; log "analysis rc=$?"
DP=$($P - <<PY
import re
t = open("results/tables_D2_$TAG.txt").read()
m = re.search(r"M-ours-bstar -> M-ours-dscore-C-V1.*?\n\s*decision SNRs \[([^\]]*)\]", t, re.S)
print(" ".join(x.strip("' ") for x in m.group(1).split(",")) if m and m.group(1).strip() else "")
PY
)
log "decision SNRs (anchor b*): ${DP:-none}"
$P code/run_manifest.py --tag $TAG >> $L 2>&1
$P code/guard_report.py --raw raw_$TAG --testbed D2 > results/guard_D2_$TAG.txt 2>&1
$P code/recovery_ci.py --raw raw_$TAG --cell C2 --snrs -3 > results/review_next/recovery_$TAG.txt 2>&1
[ -n "$DP" ] && $P code/recovery_ci.py --raw raw_$TAG --cell C2 --snrs $DP >> results/review_next/recovery_$TAG.txt 2>&1
$P code/eval_accept.py --prior $PR --tag $TAG:$ROLE:$SHA:C2 --ntrain 160000 --bstar $BS --kron-K $KK --ll-val $LL --ref-raw $REF \
  --fits-dir results/gmm_fits_D2_$TAG --grid "$GRID" $CANDARG > results/review_next/${TAG}_accept.txt 2>&1
log "acceptance rc=$? ($(head -1 results/review_next/${TAG}_accept.txt))"
$P code/eval_accept.py --prior $PR --tag $TAG:$ROLE:$SHA:C2 --ntrain 160000 --bstar $BS --kron-K $KK --ll-val $LL --ref-raw $REF \
  --ref-arms all > results/review_next/${TAG}_refarms.txt 2>&1
log "ref-arms all report: $(grep -o 'arms differing \[[^]]*\]' results/review_next/${TAG}_refarms.txt | sort -u | tr '\n' ' ')"
log "SEEDS_EVAL_DONE"
