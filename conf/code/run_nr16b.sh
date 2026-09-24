#!/bin/bash
# (user decision 2026-09-24 17:45 CDT 무렵: "C6(Nr=16) 1.6e5 동일예산") C6 equal-budget point N' = 160000, tag NR16B16e4.
# GPU job queue, NO BLER here (BLER only after the C6-1.6e5 pre-registration is frozen and committed):
#  - score training with the frozen recipe (train_nr16.py --ntrain 160000 --fits-tag NR16B16e4; its final equal-budget GB'
#    step needs the fits and fails if they are not done yet -> re-run later, training resumes as done)
#  - em_batched_check_nr.py (batched vs exact kron M-step at Nr=16, incl. a reseed-active case) -- the kron fits
#    (fit_gpu_batched.py, per-restart for K >= 1024 + --merge) are PREPENDED to the queue only after it PASSES
#  - full-covariance grid 512..16 with fit_gpu.py (exact; the batched switch touches only the kron M-step)
# Same fit protocol as runner.cmd_fit / B32e4 (kappa grid, 3 restarts, 500-iteration cap, validation early stopping,
# selection by validation log-likelihood only), output results/gmm_fits_D2_NR16B16e4/.
cd /home/HTJ/t2/conf
P=~/miniforge3/envs/torch/bin/python
Q=logs/nr16b_queue.txt; L=logs/nr16b.log
TAG=NR16B16e4; N=160000
log () { echo "[nr16b $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $*" | tee -a $L >> logs/queue.log; }
if [ ! -f $Q ]; then
  { echo "code/train_nr16.py --ntrain $N --fits-tag $TAG"
    echo "code/em_batched_check_nr.py"
    for K in 512 256 128 64 32 16; do echo "code/fit_gpu.py 16 full $K $N $TAG"; done; } > $Q
fi
worker () {
  local g=$1 job
  while true; do
    job=$(flock $Q.lock sh -c "head -n1 $Q; sed -i 1d $Q")
    [ -z "$job" ] && { sleep 60; [ -f $Q.stop ] && break; continue; }
    log "GPU $g start: $job"
    CUDA_VISIBLE_DEVICES=$g $P $job >> logs/nr16b_gpu$g.log 2>&1
    log "GPU $g done rc=$?: $job"
  done
}
log "queue start (git $(git rev-parse --short HEAD)), $(wc -l < $Q) jobs"
for g in 0 1 2 3 4 5; do worker $g & done
wait
log "NR16B_QUEUE_DONE"
