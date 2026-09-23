#!/bin/bash
# (review_next NEXT_EXPERIMENTS_P3 v2 §3) ONE-SHOT test-set confirmation of the adopted rule R-adapt (user decision
# 2026-09-23 10:15 CDT): test set trials 0..2559, C2 all SNRs (-3/0/+3 dB decision, rest report-only), new tag, --iters 32,
# the same arm configuration as review_next_P3 (+ r_t).  R16 reference = iteration 16 of THIS run, which must be
# bit-identical to raw_B16e4k (checked by p3_rules.py --confirm).  Headline unchanged whatever the outcome.
cd /home/HTJ/t2/conf
P=~/miniforge3/envs/torch/bin/python
L=logs/review_next/run_p3test.log
T=review_next_P3test
log () { echo "[p3test $(TZ=America/Chicago date '+%H:%M %Z')] $*" | tee -a $L >> logs/queue.log; }
ln -sfn gmm_fits_D2_B16e4k results/gmm_fits_D2_$T
log "P3 test confirmation start (git $(git rev-parse --short HEAD))"
$P code/runner.py run --testbed D2 --cell C2 --prior S2 --skip0 0 --n 2560 --chunk 40 --iters 32 --ntrain 160000 \
   --stagec-ckpt /home/HTJ/t2/conf/ckpt/d2sx_N160000_a1.pt --p3-arms --extra-log r_t \
   --arm M-ours-dscore-C-V1 M-ours-bstar V1-b05 bstar-b05 V1-fb05 bstar-fb05 --tag $T >> $L 2>&1 \
   || { log "ABORT: runner failed"; exit 1; }
$P code/run_manifest.py --tag $T >> $L 2>&1
log "P3TEST_DONE"
