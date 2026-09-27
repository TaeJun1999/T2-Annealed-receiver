#!/bin/bash
# review_next C (user decision 2026-09-27: spatially non-stationary testbed, 16x4 visibility windows; "GPU 적극 사용"):
# GPU job queue for prior S2v at Nr=16 (cell C6), equal budget N' = 160000, fits tag S2vB16e4.  NO BLER here (BLER only after
# a frozen pre-registration).  Same recipe as the C6 point (run_nr16b.sh): training with the frozen hyper-parameters
# (train_nr16.py --prior S2v --sigma-tag S2vNR16), full grid 16..512 (fit_gpu.py), kron 16..512 (fit_gpu.py) and kron
# 1024/2048/4096 per restart (fit_gpu_batched.py; the batched kron M-step was verified at Nr=16 by em_batched_check_nr.py)
# followed by --merge (CPU).  Workers take the next job; a GPU busy with a foreign process makes its job fail (logged, not
# retried).  Log logs/s2v.log; end marker S2V_QUEUE_DONE.
cd "$(dirname "$0")/.."
P=~/miniforge3/envs/torch/bin/python
Q=logs/s2v_queue.txt; L=logs/s2v.log
TAG=S2vB16e4; N=160000
log () { echo "[s2v $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $*" | tee -a $L; }
mkdir -p logs ckpt
if [ ! -f $Q ]; then
  { echo "code/train_nr16.py --prior S2v --sigma-tag S2vNR16 --ntrain $N --no-gbprime"
    for K in 4096 2048 1024; do for r in 0 1 2; do echo "code/fit_gpu_batched.py 16 kron $K $N $TAG --restart $r --prior S2v"; done; done
    for K in 512 256 128 64 32 16; do echo "code/fit_gpu.py 16 full $K $N $TAG --prior S2v"; echo "code/fit_gpu.py 16 kron $K $N $TAG --prior S2v"; done
  } > $Q
fi
worker () {
  local g=$1 job
  while true; do
    job=$(flock $Q.lock sh -c "head -n1 $Q; sed -i 1d $Q")
    [ -z "$job" ] && break
    log "GPU $g start: $job"
    CUDA_VISIBLE_DEVICES=$g $P $job >> logs/s2v_gpu$g.log 2>&1
    log "GPU $g done rc=$?: $job"
  done
}
log "queue start (git $(git rev-parse --short HEAD)), $(wc -l < $Q) jobs"
FREE=($(nvidia-smi --query-gpu=index,memory.used --format=csv,noheader,nounits | awk -F', ' '$2 < 100 {print $1}'))
log "free GPUs: ${FREE[*]}"
for g in "${FREE[@]}"; do worker $g & done
wait
for K in 1024 2048 4096; do CUDA_VISIBLE_DEVICES= $P code/fit_gpu.py 16 kron $K $N $TAG --merge --prior S2v >> $L 2>&1; log "merge kron $K rc=$?"; done
log "S2V_QUEUE_DONE"
