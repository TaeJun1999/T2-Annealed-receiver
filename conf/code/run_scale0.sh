#!/bin/bash
# Array-scaling stage 0 (user decisions 2026-09-29/30 CDT): architecture DIAGNOSTIC at Nr = 32 (cell C9), no BLER.
#   1. the 12 equal-budget GMM fits at N = 1e4 (full + kron, K 16..512 = the C6 1e4 grid, fit_nr16.sh) on GPUs 0 1 3 4 5
#   2. sigma grid for the 32x4 array, tag NR32 (CPU; runner.cmd_sigma needs the fits, as in run_nr16.sh)
#   3. V1 training at N = 1e4 with the FROZEN recipe (train_nr16.py --nr 32 --no-gbprime) on GPU 5
#   4. GB' against the equal-budget b* once all 12 fits exist (train_nr16.py --nr 32: resumes the finished run, then GB')
# Read-outs (report-only diagnostic): training stability (stopped_by / aborted -> fallback needed?) and the GB' ratio
# diffusion/GMM vs C2 (1e4) and C6 (1e4, results/d2_gbprime_NR16_N10000_a1.npz).  End marker SCALE0_DONE in logs/scale0.log.
cd /home/HTJ/t2_wtS/conf
P=~/miniforge3/envs/torch/bin/python; L=logs/scale0.log
log () { echo "[scale0 $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $*" | tee -a $L; }
log "start (git $(git rev-parse --short HEAD), dirty: $(git status --porcelain code | wc -l) code files)"
lane () { G=$1; shift
  while [ $# -ge 2 ]; do CUDA_VISIBLE_DEVICES=$G $P code/fit_gpu.py 32 $1 $2 10000 NR32 >> logs/fit_D2_nr32.log 2>&1; shift 2; done; }
lane 0 full 512 full 16 & lane 1 kron 512 kron 16 & lane 3 full 256 full 32 kron 32 &
lane 4 kron 256 full 64 kron 64 & lane 5 full 128 kron 128 &
wait
n=$(ls results/gmm_fits_D2_NR32/*.npz 2>/dev/null | wc -l); log "GMM fits N=1e4: $n/12"
[ "$n" -eq 12 ] || { log "ABORT: $n/12 fits -- GB' would use a partial grid"; exit 1; }
CUDA_VISIBLE_DEVICES= $P code/runner.py sigma --testbed D2 --cell C9 --tag NR32 > logs/sigma_NR32.log 2>&1 \
  || { log "ABORT: sigma grid failed (logs/sigma_NR32.log)"; exit 1; }
log "sigma grid NR32: $(grep -o 'sigma_t in \[[^]]*\]' logs/sigma_NR32.log | tail -1)"
CUDA_VISIBLE_DEVICES=5 $P code/train_nr16.py --nr 32 --ntrain 10000 --no-gbprime > logs/train_nr32.log 2>&1
log "training rc=$?: $(grep -E '^\[nr16\] trained' logs/train_nr32.log | tail -1)"
CUDA_VISIBLE_DEVICES=5 $P code/train_nr16.py --nr 32 --ntrain 10000 >> logs/train_nr32.log 2>&1
log "GB' rc=$?: $(grep -E 'GMM b\* =' logs/train_nr32.log | tail -1)"
log "SCALE0_DONE"
