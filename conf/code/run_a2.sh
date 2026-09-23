#!/bin/bash
# (review_next NEXT_EXPERIMENTS §3.2 A2) clip='mean' symmetric ablation + §2.6 C-calib report-only floor row,
# DEVELOPMENT set only (trials 2560..3199): C2 -3 dB (decision), C2 +6 dB and C5 -3 dB (report-only).
# Headline configuration: N_train 1.6e5, GMM b* kron K=1024 (fits of tag B16e4k via symlink), Stage C ckpt
# d2sx_N160000_a1.pt (legacy last-EMA).  Receiver CPU complex128.  Judged with code/pair_tags.py afterwards.
cd /home/HTJ/t2/conf
P=~/miniforge3/envs/torch/bin/python
L=logs/review_next/run_a2.log
TAG=review_next_A2
ARMS="M-ours-dscore-C-V1 M-ours-dscore-C-V1-mean M-ours-dscore-C-V1-floor1e-2 gmmB-scorew-eta gmmB-scorew-mean M-ours-bstar M-ours-bstar-mean R5-genie"
log () { echo "[a2 $(TZ=America/Chicago date '+%H:%M %Z')] $*" | tee -a $L >> logs/queue.log; }
ln -sfn gmm_fits_D2_B16e4k results/gmm_fits_D2_$TAG
log "A2 start, tag $TAG"
for spec in "C2 -3 6" "C5 -3"; do
  set -- $spec; cell=$1; shift
  $P code/runner.py run --testbed D2 --cell $cell --snr "$@" --prior S2 --skip0 2560 --n 640 --chunk 40 \
     --tag $TAG --ntrain 160000 --stagec-ckpt /home/HTJ/t2/conf/ckpt/d2sx_N160000_a1.pt --mean-arms \
     --arm $ARMS >> $L 2>&1 || { log "ABORT: runner failed for $cell"; exit 1; }
done
$P code/run_manifest.py --tag $TAG >> $L 2>&1
log "A2_DONE"
