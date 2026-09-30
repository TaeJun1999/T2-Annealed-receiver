#!/bin/bash
# NEXT_EXPERIMENTS_HISNR16e4 (REPORT-ONLY): high-SNR supplement, D2 C2 (headline weights) and D2 C6, SNR +6..+15 dB, n = 20480 per
# SNR on NEW trials common.HISNR_SKIP0 = 10000.. (disjoint from the test / development / judging sets), arms V1 b* R2 R1 R3 genie.
# CPU, GPUs hidden.  run -> run_manifest -> eval_accept (--skip0, --n) -> hisnr_report.  Log logs/run_hisnr16e4.log, end HISNR_DONE.
cd /home/HTJ/t2/conf; P=~/miniforge3/envs/torch/bin/python; L=logs/run_hisnr16e4.log; export CUDA_VISIBLE_DEVICES=
log () { echo "[hisnr $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $*" | tee -a $L; }
REG=results/review_next/NEXT_EXPERIMENTS_HISNR16e4.md
[ -n "$(git -C /home/HTJ/t2 status --porcelain conf/code Demo)" ] && { log "ABORT: conf/code or Demo dirty"; exit 1; }
for f in $REG DECISIONS.md; do
  [ -n "$(git ls-files $f)" ] && [ -z "$(git status --porcelain $f)" ] || { log "ABORT: $f not tracked+clean (freeze first)"; exit 1; }
done
ls -d raw_HS* >/dev/null 2>&1 && { log "ABORT: raw_HS* exists (re-run needs user approval)"; exit 1; }
H=$(git rev-parse --short HEAD); log "start (git $H)"; OK=0; FAIL=0
# TAG CELL PR BF CKPT(rel. to conf) SHA ROLE BS KK LL
while read TAG CELL PR BF CK SHA ROLE BS KK LL; do
  ln -sfn gmm_fits_D2_$BF results/gmm_fits_D2_$TAG
  $P code/runner.py run --testbed D2 --prior $PR --cell $CELL --snr 6 9 12 15 --n 20480 --chunk 40 --skip0 10000 --ntrain 160000 \
    --stagec-ckpt /home/HTJ/t2/conf/$CK --arm M-ours-dscore-C-V1 M-ours-bstar R2-ours-G R1-turbo R3-bigamp R5-genie --tag $TAG \
    > logs/run_D2_$TAG.log 2>&1 < /dev/null || { log "$TAG ABORT: run failed"; FAIL=$((FAIL+1)); continue; }
  $P code/run_manifest.py --tag $TAG >> $L 2>&1
  $P code/eval_accept.py --prior $PR --ntrain 160000 --bstar $BS --kron-K $KK --ll-val $LL --n 20480 --skip0 10000 \
    --tag $TAG:$ROLE:$SHA:$CELL > results/review_next/${TAG}_accept.txt 2>&1; RC=$?
  log "$TAG acceptance rc=$RC ($(head -1 results/review_next/${TAG}_accept.txt | cut -c1-80))"
  [ $RC -ne 0 ] && { log "$TAG INVALID: acceptance failed"; FAIL=$((FAIL+1)); continue; }
  $P code/hisnr_report.py --raw raw_$TAG --cell $CELL --prior $PR > results/review_next/hisnr_$TAG.txt 2>&1
  log "$TAG report rc=$?"; OK=$((OK+1))
done <<'T'
HSB16e4k C2 S2 B16e4k ckpt/d2sx_N160000_a1.pt 4443921ce8d5c4a1 legacy-last kron 1024 -11.459169831224418
HSNR16 C6 S2 NR16B16e4 ckpt/d2sx_NR16_N160000_a1_fb2_best.pt c050d611b2c714a6 best kron 4096 63.1751571838059
T
log "HISNR_DONE ok=$OK fail=$FAIL"
