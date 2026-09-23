#!/bin/bash
# (review_next NEXT_EXPERIMENTS §3.1 step 2) A1 1st-stage ablation, DEVELOPMENT set C2 -3 dB (n=640):
# {aug, ctrl} x attempt 1..3 at N_train = 1e4, each evaluated with its _best.pt in the V1 wiring
# (M-ours-dscore-C-V1 = psd_project) -- only after the D1 sibling gate PASSED (gate_aug_D1_N160000_a1.txt).
# GMM fits: the N=1e4 set (conf/results/gmm_fits_D2, kron K=512), as every N=1e4 table.  Receiver CPU.
# Judged with: pair_tags.py group --aug <3 aug tags> --ctrl <3 ctrl tags> --cell C2 --snr -3
cd /home/HTJ/t2/conf
P=~/miniforge3/envs/torch/bin/python
L=logs/review_next/run_a1s2.log
log () { echo "[a1s2 $(TZ=America/Chicago date '+%H:%M %Z')] $*" | tee -a $L >> logs/queue.log; }
grep -q "VERDICT   PASS" results/review_next/gate_aug_D1_N160000_a1.txt \
  || { log "ABORT: D1 sibling gate is not PASS -- §3.1 step 1 ends A1, no BLER is computed"; exit 1; }
log "start: 6 checkpoints x C2 -3 dB dev (skip 2560..3199)"
for v in aug ctrl; do for k in 1 2 3; do
  TAG=review_next_A1s2_${v}_a$k
  ln -sfn gmm_fits_D2 results/gmm_fits_D2_$TAG
  ( $P code/runner.py run --testbed D2 --cell C2 --snr -3 --prior S2 --skip0 2560 --n 640 --chunk 40 \
      --tag $TAG --ntrain 10000 --stagec-ckpt /home/HTJ/t2/conf/ckpt_review_next/${v}_N10000_a${k}_best.pt \
      --arm M-ours-dscore-C-V1 M-ours-bstar R5-genie >> logs/review_next/run_$TAG.log 2>&1 \
    && $P code/run_manifest.py --tag $TAG >> logs/review_next/run_$TAG.log 2>&1 \
    && log "done $TAG" || log "FAIL $TAG" ) &
done; done
wait
log "A1S2_DONE"
