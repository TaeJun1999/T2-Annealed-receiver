#!/bin/bash
# Second-testbed GPU queue (user decisions 2026-09-26: SV8e + 38.901 MIX3 "boundary-both-sides" test; DECISIONS 15:03 KST).
# NO BLER here (BLER only after the Fable pre-registration is frozen).  Generalises run_d3.sh to several priors:
#  - "@train <prior> <tag>": frozen recipe, run_d2_sx.py --no-gbprime, with the 10_SPEC §3d ladder on ONE GPU (fallback k+1
#    only when attempt k's checkpoint says stopped_by=diverged; anything else stops the chain for a manual decision);
#  - any other line: a plain command (fit_gpu.py / fit_gpu_batched.py ... --prior <prior>), CUDA_VISIBLE_DEVICES=<gpu>.
# One worker per GPU in $GPUS.  A worker WAITS (60 s polls of nvidia-smi, never touching the GPU) while its GPU is busy with
# THIS user's processes (e.g. the D3 queue), and STOPS -- no retry -- if another user's process holds it or nvidia-smi fails.
# An empty queue is polled every 120 s so jobs can be appended (38.901 later); `touch logs/tb2_queue.txt.stop` ends it.
# Post steps (merge kron 1024 / grid-edge rule / GB') are run by hand per prior, as for C6.
CONF=${CONF:-/home/HTJ/t2/conf}; cd $CONF || exit 1
P=${P:-~/miniforge3/envs/torch/bin/python}; N=${N:-160000}; GPUS=${GPUS:-"0 1 2 3 4"}
Q=logs/tb2_queue.txt; L=logs/tb2.log
log () { echo "[tb2 $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $*" | tee -a $L >> logs/queue.log; }
mem () { nvidia-smi -i $1 --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | tr -d ' '; }
foreign () {                                   # 0 (true) if a process of another user holds GPU $1
  local uuid p; uuid=$(nvidia-smi -i $1 --query-gpu=uuid --format=csv,noheader 2>/dev/null)
  for p in $(nvidia-smi --query-compute-apps=gpu_uuid,pid --format=csv,noheader 2>/dev/null | awk -F', ' -v u="$uuid" '$1==u{print $2}'); do
    [ "$(ps -o user= -p $p 2>/dev/null | tr -d ' ')" != "$USER" ] && return 0
  done; return 1; }
train_chain () {
  local g=$1 prior=$2 tag=$3 fb ck s
  for fb in 1 2 3; do
    ck=ckpt/d2sx_${prior}_N${N}_a1$([ $fb -gt 1 ] && echo _fb$fb).pt
    CUDA_VISIBLE_DEVICES=$g $P code/run_d2_sx.py --prior $prior --ntrain $N --tag $tag --fallback $fb --no-gbprime \
      >> logs/tb2_gpu$g.log 2>&1
    s=$(CUDA_VISIBLE_DEVICES= $P -c "import torch; print(torch.load('$ck', map_location='cpu', weights_only=False).get('stopped_by'))" 2>/dev/null)
    log "train $prior fallback $fb: stopped_by=${s:-NO_CHECKPOINT} ($ck)"
    [ "$s" = diverged ] && [ $fb -lt 3 ] && { log "§3d: $prior fallback $fb DIVERGED -> fallback $((fb + 1)) on GPU $g"; continue; }
    break
  done
  echo "$fb ${s:-NO_CHECKPOINT}" > logs/tb2_train_state_$prior.txt
}
worker () {
  local g=$1 job m rc
  while true; do
    [ -f $Q.stop ] && break
    m=$(mem $g)
    [ -z "$m" ] && { log "GPU $g: nvidia-smi failed -> worker $g stops"; break; }
    if [ "$m" -gt 10 ]; then
      foreign $g && { log "GPU $g held by another user -> worker $g stops (no retry)"; break; }
      sleep 60; continue                       # our own job (e.g. the D3 queue) still running
    fi
    job=$(flock $Q.lock sh -c "head -n1 $Q; sed -i 1d $Q")
    [ -z "$job" ] && { sleep 120; continue; }
    log "GPU $g start: $job"
    case "$job" in
      @train*) set -- $job; train_chain $g $2 $3; rc="(train: logs/tb2_train_state_$2.txt)";;
      *) CUDA_VISIBLE_DEVICES=$g $P $job >> logs/tb2_gpu$g.log 2>&1; rc=$?;;
    esac
    log "GPU $g done rc=$rc: $job"
  done
}
git diff --quiet -- code 2>/dev/null || log "WARNING: conf/code has uncommitted changes -- the logged git hash does not describe the code"
log "queue start (git $(git rev-parse --short HEAD 2>/dev/null)), N=$N GPUs: $GPUS, $(grep -c . $Q) jobs"
for g in $GPUS; do worker $g & done
wait
log "TB2_QUEUE_DONE"
