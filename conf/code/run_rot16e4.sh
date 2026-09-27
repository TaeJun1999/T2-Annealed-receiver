#!/bin/bash
# (NEXT_EXPERIMENTS_ROT16e4 §1, after the freeze commit) receive-array rotation (distribution drift, runner --rotation),
# six datasets x rotation in {15, 30} deg; arms V1, b*, R2-ours-G, R5-genie; static arms read from the base raw (same trials).
# Per dataset: (0) 0-deg CONTROL -- C2/C6 -3 dB chunk 0 (trials 0..39, already observed) through the rotation code path,
# every arm x KEYS_RAW bit-identical to the base raw (eval_accept --ref-arms all); a failing control skips the dataset.
# (1) for each angle: run -> run_manifest -> eval_accept (chunk plan, meta, ckpt id) -> pair_rot ONLY if eval_accept passed.
# CPU, GPUs hidden.  All twelve tags are run and reported; arguments name a subset of DATASETS only to RESUME.
# Log logs/run_rot16e4.log, end marker "ROT_EVAL_DONE ok=<n> fail=<n>".
cd /home/HTJ/t2/conf
export CUDA_VISIBLE_DEVICES=
P=~/miniforge3/envs/torch/bin/python
L=logs/run_rot16e4.log
log () { echo "[rot16e4 $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $*" | tee -a $L >> logs/queue.log; }
[ -n "$(git -C /home/HTJ/t2 status --porcelain conf/code Demo)" ] && { log "ABORT: conf/code or Demo dirty"; exit 1; }
ARMS="M-ours-dscore-C-V1 M-ours-bstar R2-ours-G R5-genie"
DEGS="a:15 b:30"
# name  suffix  cell prior base_fits  base_raw  ckpt  sha  role  bstar kron_K|- ll_val
DS="D2C2  B16e4k C2 S2    B16e4k    raw_B16e4k    ckpt/d2sx_N160000_a1.pt               4443921ce8d5c4a1 legacy-last kron   1024 -11.459169831224418
D2C6  NR16   C6 S2    NR16B16e4 raw_NR16B16e4 ckpt/d2sx_NR16_N160000_a1_fb2_best.pt c050d611b2c714a6 best        kron   4096 63.1751571838059
D3    D3     C2 S2c   D3B16e4   raw_D3B16e4   ckpt/d2sx_S2c_N160000_a1_best.pt      7ebf4e6647d4413f best        kron   4096 0.08879931165293979
SV8e  SV     C2 SV8e  SVB16e4   raw_SVB16e4   ckpt/d2sx_SV8e_N160000_a1_best.pt     d2d78962c2846364 best        gmm256 -    -47.80545576704972
UMi28 U28    C2 UMi28 U28B16e4  raw_U28B16e4  ckpt/d2sx_UMi28_N160000_a1_best.pt    6f3a1b9490864af1 best        kron   4096 5.797910431000217
MIX3  MX     C2 MIX3  MXB16e4   raw_MXB16e4   ckpt/d2sx_MIX3_N160000_a1_best.pt     b591ae24ae3c5f31 best        kron   4096 33.7604873920761"
WANT="$*"
for w in $WANT; do echo "$DS" | grep -q "^$w " || { log "ABORT: unknown dataset '$w'"; exit 1; }; done
log "start (git $(git rev-parse --short HEAD)) datasets: ${WANT:-all}"
OK=0; FAIL=0
while read NAME SUF CELL PR BF BASE CK SHA ROLE BS KK LL; do
  [ -n "$WANT" ] && ! echo " $WANT " | grep -q " $NAME " && continue
  [ "$(sha256sum $CK | cut -c1-16)" = "$SHA" ] || { log "$NAME ABORT: ckpt sha differs"; FAIL=$((FAIL+2)); continue; }
  [ -d $BASE ] || { log "$NAME ABORT: base raw $BASE missing"; FAIL=$((FAIL+2)); continue; }
  KARG=""; [ "$KK" != "-" ] && KARG="--kron-K $KK"
  CT=ROT0$SUF; ln -sfn gmm_fits_D2_$BF results/gmm_fits_D2_$CT
  $P code/runner.py run --testbed D2 --prior $PR --cell $CELL --snr -3 --n 40 --chunk 40 --ntrain 160000 --rotation 0 \
    --stagec-ckpt /home/HTJ/t2/conf/$CK --tag $CT > logs/run_D2_$CT.log 2>&1
  $P code/eval_accept.py --prior $PR --tag $CT:$ROLE:$SHA:$CELL --points $CELL:-3 --n 40 --ntrain 160000 --bstar $BS $KARG \
    --ll-val $LL --ref-raw $BASE --ref-arms all > results/review_next/${CT}_accept.txt 2>&1
  RC=$?; log "$NAME control 0 deg rc=$RC ($(head -1 results/review_next/${CT}_accept.txt))"
  [ $RC -ne 0 ] && { log "$NAME INVALID: 0-deg control not bit-identical to $BASE -- no rotation runs"; FAIL=$((FAIL+2)); continue; }
  for DG in $DEGS; do
    TAG=ROT${DG%%:*}$SUF; V=${DG#*:}; ln -sfn gmm_fits_D2_$BF results/gmm_fits_D2_$TAG
    $P code/runner.py run --testbed D2 --prior $PR --cell $CELL --n 2560 --chunk 40 --ntrain 160000 --rotation $V \
      --stagec-ckpt /home/HTJ/t2/conf/$CK --arm $ARMS --tag $TAG > logs/run_D2_$TAG.log 2>&1 \
      || { log "$NAME deg=$V ABORT: run failed"; FAIL=$((FAIL+1)); continue; }
    $P code/run_manifest.py --tag $TAG >> $L 2>&1; log "$NAME deg=$V run_manifest rc=$?"
    $P code/eval_accept.py --prior $PR --tag $TAG:$ROLE:$SHA:$CELL --ntrain 160000 --bstar $BS $KARG --ll-val $LL \
      > results/review_next/${TAG}_accept.txt 2>&1
    RC=$?; log "$NAME deg=$V acceptance rc=$RC ($(head -1 results/review_next/${TAG}_accept.txt))"
    [ $RC -ne 0 ] && { log "$NAME deg=$V INVALID: acceptance failed, no pair_rot"; FAIL=$((FAIL+1)); continue; }
    $P code/pair_rot.py --base $BASE --rot raw_$TAG --deg $V --cell $CELL --prior $PR > results/review_next/pair_$TAG.txt 2>&1
    RC=$?; log "$NAME deg=$V pair_rot rc=$RC ($(head -1 results/review_next/pair_$TAG.txt | cut -c1-150))"
    [ $RC -eq 0 ] && OK=$((OK+1)) || { log "$NAME deg=$V INVALID: integrity failed"; FAIL=$((FAIL+1)); }
  done
done < <(echo "$DS")
log "ROT_EVAL_DONE ok=$OK fail=$FAIL"
exit $FAIL
