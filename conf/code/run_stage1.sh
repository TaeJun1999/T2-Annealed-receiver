#!/bin/bash
# Array-scaling STAGE 1 (user decision 2026-09-29 CDT: "1단계 먼저"): N = 1e4 equal-budget BLER PILOT, report-only, no registration.
# Datasets D2 (prior S2) and UMi28, arrays Nr = 8 (C2) / 16 (C6) / 32 (C9).  DEVELOPMENT trials 2560.. (n = 1280) so the test trials
# 0..2559 stay untouched for the stage-2 registration.  Arms: V1 (Stage C, last-EMA weights -- the only ones the 1e4 C2/C6 runs
# kept), b*, R2, R1, R3, R0-pilot, genie; the score ablations V0/V4/V4b are dropped (V1 dominates the cost at Nr = 32).
# Phase A (GPU 0-5): UMi28 Nr = 8 N = 1e4 (12 fits, tag U28NR8) -> frozen-recipe training (run_d2_sx.py) -> GB'.
# Phase B (CPU, GPUs hidden): the 6 pilot runs, light cells first.  Per-cell SNR grids from the stage-0 probes (STAGE0.md).
# End STAGE1_DONE in logs/stage1.log.
cd /home/HTJ/t2_wtS/conf
P=~/miniforge3/envs/torch/bin/python; L=logs/stage1.log; CK=/home/HTJ/t2/conf/ckpt
log () { echo "[stage1 $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $*" | tee -a $L; }
log "start (git $(git rev-parse --short HEAD), dirty code files: $(git status --porcelain code | wc -l))"
ln -sfn /home/HTJ/t2/conf/results/gmm_fits_D2_B1e4 results/gmm_fits_D2_B1e4
# ---- phase A: UMi28 Nr 8, N = 1e4
fits () { local G=$1; shift
  while [ $# -ge 2 ]; do CUDA_VISIBLE_DEVICES=$G $P code/fit_gpu.py 8 $1 $2 10000 U28NR8 --prior UMi28 >> logs/fit_u28nr8.log 2>&1; shift 2; done; }
( fits 0 full 512 kron 16 & fits 1 kron 512 full 16 & fits 2 full 256 kron 32 & fits 3 kron 256 full 32 &
  fits 4 full 128 kron 64 & fits 5 kron 128 full 64 & wait
  n=$(ls results/gmm_fits_D2_U28NR8/*.npz 2>/dev/null | wc -l); log "A: UMi28 Nr8 1e4 fits $n/12"
  CUDA_VISIBLE_DEVICES=0 $P code/run_d2_sx.py --prior UMi28 --ntrain 10000 --tag U28NR8 > logs/train_u28nr8.log 2>&1
  log "A: UMi28 Nr8 1e4 train+GB' rc=$?: $(grep -E 'GMM b\* =' logs/train_u28nr8.log | tail -1)" ) &
APID=$!
# ---- phase B: pilots (tag, prior, cell, fits dir, ckpt, snrs)
pilot () { local T=$1 PR=$2 CELL=$3 FD=$4 CKF=$5; shift 5
  ln -sfn $FD results/gmm_fits_D2_$T
  CUDA_VISIBLE_DEVICES= $P code/runner.py run --testbed D2 --prior $PR --cell $CELL --snr "$@" --n 1280 --chunk 40 --skip0 2560 \
    --ntrain 10000 --stagec-ckpt $CK/$CKF \
    --arm M-ours-dscore-C-V1 M-ours-bstar R2-ours-G R1-turbo R3-bigamp R0-pilot R5-genie --tag $T > logs/run_$T.log 2>&1
  local rc=$?
  $P code/runner.py analysis --testbed D2 --tag $T > logs/analysis_$T.log 2>&1
  log "B: $T ($PR $CELL) rc=$rc analysis rc=$?"; }
pilot S1D2C2  S2    C2 gmm_fits_D2_B1e4 d2sx_N10000_a1.pt        -3 0 3 6 9 12 15
pilot S1D2C6  S2    C6 gmm_fits_D2_NR16 d2sx_NR16_N10000_a1.pt   -3 0 3 6 9 12 15
pilot S1D2C9  S2    C9 gmm_fits_D2_NR32 d2sx_NR32_N10000_a1.pt   -15 -12 -9 -6 -3 0 3
pilot S1U28C6 UMi28 C6 gmm_fits_D2_U28NR16 d2sx_UMi28NR16_N10000_a1.pt -9 -6 -3 0 3 6 9
pilot S1U28C9 UMi28 C9 gmm_fits_D2_U28NR32 d2sx_UMi28NR32_N10000_a1.pt -12 -9 -6 -3 0 3 6
wait $APID
[ -f $CK/d2sx_UMi28_N10000_a1.pt ] && pilot S1U28C2 UMi28 C2 gmm_fits_D2_U28NR8 d2sx_UMi28_N10000_a1.pt -3 0 3 6 9 12 15 \
  || log "B: S1U28C2 SKIPPED (no UMi28 Nr8 1e4 checkpoint)"
log "STAGE1_DONE"
