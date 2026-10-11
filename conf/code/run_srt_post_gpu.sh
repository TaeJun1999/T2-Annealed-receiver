#!/bin/bash
# NEXT_EXPERIMENTS_SRT16e4 §1 "순서 규칙": the two GPU steps around §5, ONE lane per call (review M1: they must not be coupled).
#   lane ALD (BEFORE §5; after the training stopped and b* is fixed): ald.py regen (dev sites, trials 2560..3071, CPU) -> ald.py tune
#            (--ckpt = the RELATIVE path, as run_srt_base.sh passes it)                         -> logs/ald_tune_PILSRT.log
#   lane GBP (AFTER the §5 commit; may overlap the main BLER run -- report-only): GB' = run_d2_sx.py resume (no training; the
#            stopped checkpoint is not rewritten), vs the final b*                              -> logs/gbprime_SRTB16e4.log
# NO BLER.  Usage: tmux new -d -s postsrt "bash code/run_srt_post_gpu.sh <fallback k> <ALD|GBP> <GPU>"
cd /home/HTJ/t2/conf || exit 1
P=~/miniforge3/envs/torch/bin/python; FB=${1:-1}; LANE=$2; G=$3
ST=d2sx_SRT_N160000_a1$([ $FB -gt 1 ] && echo _fb$FB)
log () { echo "[post SRT $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $*" | tee -a logs/tb2_post_SRT.log; }
case "$LANE" in ALD|GBP) ;; *) echo "usage: run_srt_post_gpu.sh <fallback k> <ALD|GBP> <GPU>"; exit 1;; esac
[ "$(nvidia-smi -i $G --query-gpu=memory.used --format=csv,noheader,nounits | tr -d ' ')" -lt 100 ] || { log "GPU $G busy -> stop (no retry)"; exit 1; }
if [ $LANE = GBP ]; then
  log "GB' resume on GPU $G (ckpt $ST, git $(git rev-parse --short HEAD))"
  CUDA_VISIBLE_DEVICES=$G $P code/run_d2_sx.py --prior SRT --ntrain 160000 --tag SRTB16e4 --fallback $FB > logs/gbprime_SRTB16e4.log 2>&1
  log "GB' rc=$? ($(grep -E 'GMM b\* =' logs/gbprime_SRTB16e4.log | tail -1 | cut -c1-160)); POST_GBP_DONE"
else
  log "ALD dev regen (CPU) + tune on GPU $G (ckpt $ST, git $(git rev-parse --short HEAD))"
  CUDA_VISIBLE_DEVICES= $P code/ald.py regen --tag PILSRT --prior SRT --cell C2 --fits-tag SRTB16e4 --set dev > logs/ald_regen_PILSRT_dev.log 2>&1 \
    || { log "ALD regen dev FAILED"; exit 1; }
  CUDA_VISIBLE_DEVICES=$G $P code/ald.py tune --tag PILSRT --ckpt ckpt/${ST}_best.pt > logs/ald_tune_PILSRT.log 2>&1
  log "ALD tune rc=$?; POST_ALD_DONE"
fi
