#!/bin/bash
# Seed repeats a2 / a3 of the V1 score network on Sionna RT (prior SRT), then the resume of the DeepMIMO seeds a2 / a3 that
# run_dmc_seeds_train.sh left at epoch 394: the SEEDS16e4 / run_seeds3_train.sh pattern, frozen recipe, ONE GPU, one training at a
# time.  Training only (no BLER): the BLER evaluation of these seeds needs its own registration.  §3d ladder as run_tb2.sh
# train_chain: a diverged attempt is followed by the next fallback.  Every trainer is STARTED under taskset on one hyper-thread
# pair of the GPU's NUMA node, so a chained process keeps the pin (result-neutral; GPU 0-3 = node0).
# User instruction 2026-10-10 CDT: the GPUs handed to us keep running project work, Sionna first.
# Usage: run_srt_seeds_train.sh <gpu> [cpu pair, default 22,118]
cd /home/HTJ/t2/conf || exit 1
P=~/miniforge3/envs/torch/bin/python; G=$1; PIN=${2:-22,118}; L=logs/seeds_SRT_train.log
log () { echo "[seeds $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $*" >> $L; }
chain () {   # <prior> <tag> <attempt>
  local fb ck s
  for fb in 1 2 3; do
    ck=ckpt/d2sx_$1_N160000_a$3$([ $fb -gt 1 ] && echo _fb$fb).pt
    CUDA_VISIBLE_DEVICES=$G taskset -c $PIN $P code/run_d2_sx.py --prior $1 --ntrain 160000 --tag $2 --attempt $3 --fallback $fb \
      --no-gbprime >> logs/seeds_$1_a$3.log 2>&1 || { log "$1 a$3 fallback $fb: trainer rc != 0 -> stop (no retry)"; exit 1; }
    s=$(CUDA_VISIBLE_DEVICES= $P -c "import torch; print(torch.load('$ck', map_location='cpu', weights_only=False).get('stopped_by'))" 2>/dev/null)
    log "$1 a$3 fallback $fb: stopped_by=${s:-NO_CHECKPOINT} ($ck)"
    [ "$s" = diverged ] && [ $fb -lt 3 ] && continue
    break
  done
}
[ -n "$G" ] || { echo "usage: run_srt_seeds_train.sh <gpu> [cpu pair]"; exit 1; }
log "start (git $(git rev-parse --short HEAD)) GPU $G pin $PIN"
chain SRT SRTB16e4 2; chain SRT SRTB16e4 3; chain DMC DMCB16e4 2; chain DMC DMCB16e4 3
log "SEEDS_TRAIN_DONE"
