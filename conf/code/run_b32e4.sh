#!/bin/bash
# (larger-N re-run, user decisions 2026-09-23: N' = 3.2e5, GMM K grid extended until b* is interior (01_RULES:76))
# GPU job queue, NO BLER here: GMM EM fits with the frozen runner-fit protocol (fit_gpu.py: same kappa grid, 3 restarts,
# 500-iteration cap, validation early stopping, selection by validation log-likelihood only) into
# results/gmm_fits_D2_B32e4/, and the score trainings with the frozen recipe: D2 run_d2_sx.py --ntrain 320000 (its GB'
# step needs the fits and may fail now -- re-run later, training resumes as done) and the D1 sibling run_samplecx.py
# 320000 (+ D1 gate).  Six workers (one per GPU, Exclusive_Process) pull jobs in priority order; merges of the per-restart
# candidates and any K=4096 extension are added after the K=1024/2048 likelihoods are known.
# Measured cost (2026-09-23, GPU): kron K=1024 121 s/iter, K=2048 243 s/iter at N=3.2e5 (<= 500 iterations/restart).
cd /home/HTJ/t2/conf
P=~/miniforge3/envs/torch/bin/python
Q=logs/b32e4_queue.txt; L=logs/b32e4.log
TAG=B32e4; N=320000
log () { echo "[b32e4 $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $*" | tee -a $L >> logs/queue.log; }
if [ ! -f $Q ]; then
  { for K in 2048 1024; do for r in 0 1 2; do echo "code/fit_gpu.py 8 kron $K $N $TAG --restart $r"; done; done
    echo "code/run_d2_sx.py --ntrain $N"
    echo "code/run_samplecx.py $N"
    for fk in "kron 512" "kron 256" "full 512" "full 256" "kron 128" "full 128" "kron 64" "full 64" "kron 32" "full 32" \
              "kron 16" "full 16"; do echo "code/fit_gpu.py 8 $fk $N $TAG"; done; } > $Q
fi
worker () {
  local g=$1 job
  while true; do
    job=$(flock $Q.lock sh -c "head -n1 $Q; sed -i 1d $Q")
    [ -z "$job" ] && break
    log "GPU $g start: $job"
    CUDA_VISIBLE_DEVICES=$g $P $job >> logs/b32e4_gpu$g.log 2>&1
    log "GPU $g done rc=$?: $job"
  done
}
log "queue start (git $(git rev-parse --short HEAD)), $(wc -l < $Q) jobs"
for g in 0 1 2 3 4 5; do worker $g & done
wait
log "B32E4_QUEUE_DONE"
