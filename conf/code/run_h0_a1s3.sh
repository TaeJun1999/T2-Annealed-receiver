#!/bin/bash
# (review_next NEXT_EXPERIMENTS §2.5 H0 and §3.1 step 3) Unattended: wait for each N=1.6e5 training to finish,
# evaluate its checkpoints on the DEVELOPMENT set (V1 wiring, headline GMM fits B16e4k), then run the
# pre-registered paired tests with pair_tags.py.  Nothing here selects anything; the rules are those of v3.
#   H0      : ctrl_N160000_a1 _best.pt vs ctrl_N160000_a1.pt (last), C2 -3 dB.  Reference (report only): the
#             legacy last-EMA d2sx_N160000_a1 = review_next_A2:M-ours-dscore-C-V1 on the same trials.
#   A1 s3   : aug_N160000_a1 _best.pt vs ctrl_N160000_a1 _best.pt at C2 -3 dB (decision), C2 +6 and C5 -3 (report).
#             Step 4 (test-set confirmation) is NOT launched here: it needs the step-3 verdict first.
cd /home/HTJ/t2/conf
P=~/miniforge3/envs/torch/bin/python
L=logs/review_next/run_h0_a1s3.log
CK=/home/HTJ/t2/conf/ckpt_review_next
ARMS="M-ours-dscore-C-V1 M-ours-bstar R5-genie"
log () { echo "[h0a1s3 $(TZ=America/Chicago date '+%H:%M %Z')] $*" | tee -a $L >> logs/queue.log; }
done_train () { grep -q "^# done" logs/review_next/train_$1.log 2>/dev/null; }
evalrun () {   # $1 tag  $2 ckpt  $3.. "cell snr..." specs
  local TAG=$1 CKPT=$2; shift 2
  ln -sfn gmm_fits_D2_B16e4k results/gmm_fits_D2_$TAG
  for spec in "$@"; do set -- $spec; local cell=$1; shift
    $P code/runner.py run --testbed D2 --cell $cell --snr "$@" --prior S2 --skip0 2560 --n 640 --chunk 40 \
       --tag $TAG --ntrain 160000 --stagec-ckpt $CKPT --arm $ARMS >> logs/review_next/run_$TAG.log 2>&1 \
       || { log "FAIL runner $TAG $cell"; return 1; }
  done
  $P code/run_manifest.py --tag $TAG >> logs/review_next/run_$TAG.log 2>&1; log "evaluated $TAG ($CKPT)"
}
pt () { CUDA_VISIBLE_DEVICES="" $P code/pair_tags.py "$@" >> $L 2>&1; }

log "waiting for ctrl_N160000_a1 (H0) and aug_N160000_a1 (A1 step 3)"
until done_train ctrl_N160000_a1; do sleep 120; done
log "ctrl_N160000_a1 finished: $(grep '^# done' logs/review_next/train_ctrl_N160000_a1.log | tail -1)"
evalrun review_next_H0_ctrl_best $CK/ctrl_N160000_a1_best.pt "C2 -3 6" "C5 -3" &
evalrun review_next_H0_ctrl_last $CK/ctrl_N160000_a1.pt "C2 -3" &
wait
pt pair --cell C2 --snr -3 --x review_next_H0_ctrl_best:M-ours-dscore-C-V1 --y review_next_H0_ctrl_last:M-ours-dscore-C-V1 --out H0_best_vs_last_C2_m3
pt pair --cell C2 --snr -3 --x review_next_H0_ctrl_last:M-ours-dscore-C-V1 --y review_next_A2:M-ours-dscore-C-V1 --out H0_ref_ctrllast_vs_legacy_C2_m3
log "H0_DONE"

until done_train aug_N160000_a1; do sleep 300; done
log "aug_N160000_a1 finished: $(grep '^# done' logs/review_next/train_aug_N160000_a1.log | tail -1)"
evalrun review_next_A1s3_aug_best $CK/aug_N160000_a1_best.pt "C2 -3 6" "C5 -3"
pt pair --cell C2 --snr -3 --x review_next_A1s3_aug_best:M-ours-dscore-C-V1 --y review_next_H0_ctrl_best:M-ours-dscore-C-V1 --out A1s3_aug_vs_ctrl_C2_m3
pt pair --cell C2 --snr 6 --x review_next_A1s3_aug_best:M-ours-dscore-C-V1 --y review_next_H0_ctrl_best:M-ours-dscore-C-V1 --out A1s3_aug_vs_ctrl_C2_p6
pt pair --cell C5 --snr -3 --x review_next_A1s3_aug_best:M-ours-dscore-C-V1 --y review_next_H0_ctrl_best:M-ours-dscore-C-V1 --out A1s3_aug_vs_ctrl_C5_m3
log "A1S3_DONE"
