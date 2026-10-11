#!/bin/bash
# After the DMC training stopped (stopped_by recorded) and b* is fixed (logs/tb2_post_DMC.log): the two GPU steps that precede §5.
#   lane A (GPU $GA): GB' of DMC16e4 §1 -- run_d2_sx.py resume (no training), vs the final b*          -> logs/gbprime_DMCB16e4.log
#   lane B (CPU, then GPU $GB): DMCBASE16e4 §1 "선행" -- ald.py regen (dev sites, trials 2560..3071) -> ald.py tune (--ckpt = the
#                               RELATIVE path, as run_dmc_base.sh passes it)                              -> logs/ald_tune_PILDMC.log
# NO BLER.  Usage: tmux new -d -s postdmc "bash code/run_dmc_post_gpu.sh <fallback k> <GPU A> <GPU B>"
cd /home/HTJ/t2/conf || exit 1
P=~/miniforge3/envs/torch/bin/python; FB=${1:-1}; GA=${2:-1}; GB=${3:-0}
ST=d2sx_DMC_N160000_a1$([ $FB -gt 1 ] && echo _fb$FB)
log () { echo "[post DMC $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $*" | tee -a logs/tb2_post_DMC.log; }
for g in $GA $GB; do
  [ "$(nvidia-smi -i $g --query-gpu=memory.used --format=csv,noheader,nounits | tr -d ' ')" -lt 100 ] || { log "GPU $g busy -> stop (no retry)"; exit 1; }
done
log "GB' resume on GPU $GA (ckpt $ST, git $(git rev-parse --short HEAD)); ALD dev regen + tune on GPU $GB"
( CUDA_VISIBLE_DEVICES=$GA $P code/run_d2_sx.py --prior DMC --ntrain 160000 --tag DMCB16e4 --fallback $FB > logs/gbprime_DMCB16e4.log 2>&1
  log "GB' rc=$? ($(grep -E 'GMM b\* =' logs/gbprime_DMCB16e4.log | tail -1 | cut -c1-160))" ) &
( CUDA_VISIBLE_DEVICES= $P code/ald.py regen --tag PILDMC --prior DMC --cell C2 --fits-tag DMCB16e4 --set dev > logs/ald_regen_PILDMC_dev.log 2>&1 \
    || { log "ALD regen dev FAILED"; exit 1; }
  CUDA_VISIBLE_DEVICES=$GB $P code/ald.py tune --tag PILDMC --ckpt ckpt/${ST}_best.pt > logs/ald_tune_PILDMC.log 2>&1
  log "ALD tune rc=$?" ) &
wait
log "POST_GPU_DONE"
