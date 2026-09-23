#!/bin/bash
# (review_next NEXT_EXPERIMENTS_P3 v2 §1, §5) P3 judging runs on the P3 judging set (trials 3200..): reference 16-iteration
# run review_next_P3ref (V1, b*, genie) and 32-iteration run review_next_P3 (V1, b*, 4 damping variants, + r_t).
# C2 -3 dB n=1280 (judging), C2 +6 dB and C5 -3 dB n=640 (report-only).  Headline configuration: N_train 1.6e5, GMM b*
# kron K=1024 (fits of tag B16e4k via symlink), Stage C ckpt d2sx_N160000_a1.pt (last-EMA).  Receiver CPU complex128.
# All six runner invocations run concurrently (64 + 64 workers).  Judged afterwards by code/p3_rules.py.
cd /home/HTJ/t2/conf
P=~/miniforge3/envs/torch/bin/python
L=logs/review_next/run_p3.log
CK=/home/HTJ/t2/conf/ckpt/d2sx_N160000_a1.pt
log () { echo "[p3 $(TZ=America/Chicago date '+%H:%M %Z')] $*" | tee -a $L >> logs/queue.log; }
for T in review_next_P3ref review_next_P3; do ln -sfn gmm_fits_D2_B16e4k results/gmm_fits_D2_$T; done
COMMON="--testbed D2 --prior S2 --skip0 3200 --chunk 40 --ntrain 160000 --stagec-ckpt $CK"
REF="--iters 16 --arm M-ours-dscore-C-V1 M-ours-bstar R5-genie --tag review_next_P3ref"
RUN="--iters 32 --p3-arms --extra-log r_t --arm M-ours-dscore-C-V1 M-ours-bstar V1-b05 bstar-b05 V1-fb05 bstar-fb05 --tag review_next_P3"
log "P3 start (git $(git rev-parse --short HEAD))"
pids=(); names=()
for spec in "C2 -3 1280" "C2 6 640" "C5 -3 640"; do
  set -- $spec
  for kind in ref run; do
    [ $kind = ref ] && A=$REF || A=$RUN
    $P code/runner.py run $COMMON --cell $1 --snr $2 --n $3 $A > logs/review_next/run_p3_${kind}_$1_$2.log 2>&1 &
    pids+=($!); names+=("${kind}_$1_$2")
  done
done
bad=0
for i in "${!pids[@]}"; do wait ${pids[$i]} || { log "ABORT: ${names[$i]} failed"; bad=1; }; done
[ $bad = 0 ] || exit 1
for T in review_next_P3ref review_next_P3; do $P code/run_manifest.py --tag $T >> $L 2>&1; done
log "P3_DONE"
