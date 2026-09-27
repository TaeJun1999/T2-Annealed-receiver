#!/bin/bash
# (NEXT_EXPERIMENTS_MISMATCH16e4 §1, after the freeze commit) train/test channel-model mismatch, eight pairs: the TRAIN prior's
# checkpoint + GMM fits + sample covariance (fits dir results/gmm_fits_D2_<TAG> = links renamed to the test prior) on the TEST
# prior's test trials.  Arms V1, b*, R2-ours-G, R5-genie; the matched arms are read from the test prior's base raw (paired
# by trial stream).  Per pair: run -> run_manifest -> eval_accept (meta = the TRAIN b*, ckpt id, genie replay vs the base
# raw) -> pair_mismatch ONLY if eval_accept passed.  GPUs hidden (38.901 test priors; DECISIONS 80bae849).  Log
# logs/run_mismatch16e4.log, end marker "MISMATCH_EVAL_DONE ok=<n> fail=<n>".  All eight are run and reported; arguments
# name a subset only to RESUME an interrupted pair.   Usage: run_mismatch16e4.sh [D2-D3 D3-D2 U28-MX MX-U28 D2-U28 U28-D2 D2-SV SV-D2]
cd /home/HTJ/t2/conf
export CUDA_VISIBLE_DEVICES=
P=~/miniforge3/envs/torch/bin/python
L=logs/run_mismatch16e4.log
log () { echo "[mismatch16e4 $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $*" | tee -a $L >> logs/queue.log; }
[ -n "$(git -C /home/HTJ/t2 status --porcelain conf/code Demo)" ] && { log "ABORT: conf/code or Demo dirty"; exit 1; }
# name  tag  train_prior test_prior base_raw  ckpt  sha  role  bstar kron_K|- ll_val   (b* = the TRAIN prior's)
DS="D2-D3  MMs2s2c S2    S2c   raw_D3B16e4  ckpt/d2sx_N160000_a1.pt            4443921ce8d5c4a1 legacy-last kron   1024 -11.459169831224418
D3-D2  MMs2cs2 S2c   S2    raw_B16e4k   ckpt/d2sx_S2c_N160000_a1_best.pt   7ebf4e6647d4413f best        kron   4096 0.08879931165293979
U28-MX MMu28mx UMi28 MIX3  raw_MXB16e4  ckpt/d2sx_UMi28_N160000_a1_best.pt 6f3a1b9490864af1 best        kron   4096 5.797910431000217
MX-U28 MMmxu28 MIX3  UMi28 raw_U28B16e4 ckpt/d2sx_MIX3_N160000_a1_best.pt  b591ae24ae3c5f31 best        kron   4096 33.7604873920761
D2-U28 MMs2u28 S2    UMi28 raw_U28B16e4 ckpt/d2sx_N160000_a1.pt            4443921ce8d5c4a1 legacy-last kron   1024 -11.459169831224418
U28-D2 MMu28s2 UMi28 S2    raw_B16e4k   ckpt/d2sx_UMi28_N160000_a1_best.pt 6f3a1b9490864af1 best        kron   4096 5.797910431000217
D2-SV  MMs2sv  S2    SV8e  raw_SVB16e4  ckpt/d2sx_N160000_a1.pt            4443921ce8d5c4a1 legacy-last kron   1024 -11.459169831224418
SV-D2  MMsvs2  SV8e  S2    raw_B16e4k   ckpt/d2sx_SV8e_N160000_a1_best.pt  d2d78962c2846364 best        gmm256 -    -47.80545576704972"
WANT="$*"
for w in $WANT; do echo "$DS" | grep -q "^$w " || { log "ABORT: unknown pair '$w'"; exit 1; }; done
log "start (git $(git rev-parse --short HEAD)) pairs: ${WANT:-all}"
OK=0; FAIL=0
while read NAME TAG PTR PTE BASE CK SHA ROLE BS KK LL; do
  [ -n "$WANT" ] && ! echo " $WANT " | grep -q " $NAME " && continue
  case $PTR in S2) TB=raw_B16e4k;; S2c) TB=raw_D3B16e4;; SV8e) TB=raw_SVB16e4;; UMi28) TB=raw_U28B16e4;; MIX3) TB=raw_MXB16e4;; esac
  [ -d $BASE ] && [ -d $TB ] || { log "$NAME ABORT: base raw $BASE or train base $TB missing"; FAIL=$((FAIL+1)); continue; }
  FD=results/gmm_fits_D2_$TAG; BADL=0; NL=0          # every link resolves to a TRAIN-prior fit file (review_MISMATCH16e4 #1a)
  for f in $FD/fit_${PTE}_Nr8_*K*_n160000.npz; do NL=$((NL+1)); r=$(readlink -e $f) && case $(basename $r) in fit_${PTR}_Nr8_*) ;; *) BADL=1;; esac || BADL=1; done
  [ $NL -ge 13 ] && [ $BADL -eq 0 ] || { log "$NAME ABORT: fits links in $FD ($NL) do not all resolve to fit_${PTR}_ files"; FAIL=$((FAIL+1)); continue; }
  [ "$(sha256sum $CK | cut -c1-16)" = "$SHA" ] || { log "$NAME ABORT: ckpt sha differs"; FAIL=$((FAIL+1)); continue; }
  $P code/runner.py run --testbed D2 --prior $PTE --cell C2 --n 2560 --chunk 40 --ntrain 160000 --stagec-ckpt /home/HTJ/t2/conf/$CK \
    --train-prior $PTR --arm M-ours-dscore-C-V1 M-ours-bstar R2-ours-G R5-genie --tag $TAG > logs/run_D2_$TAG.log 2>&1 \
    || { log "$NAME ABORT: run failed"; FAIL=$((FAIL+1)); continue; }
  $P code/run_manifest.py --tag $TAG >> $L 2>&1; log "$NAME run_manifest rc=$?"
  KARG=""; [ "$KK" != "-" ] && KARG="--kron-K $KK"
  $P code/eval_accept.py --prior $PTE --tag $TAG:$ROLE:$SHA:C2 --ntrain 160000 --bstar $BS $KARG --ll-val $LL --ref-raw $BASE \
    > results/review_next/${TAG}_accept.txt 2>&1
  RC=$?; log "$NAME acceptance rc=$RC ($(head -1 results/review_next/${TAG}_accept.txt))"
  [ $RC -ne 0 ] && { log "$NAME INVALID: acceptance failed, no pair_mismatch (registration §1)"; FAIL=$((FAIL+1)); continue; }
  $P code/pair_mismatch.py --base $BASE --mis raw_$TAG --train-base $TB --train-prior $PTR --cell C2 --prior $PTE > results/review_next/pair_$TAG.txt 2>&1
  RC=$?; log "$NAME pair_mismatch rc=$RC ($(head -1 results/review_next/pair_$TAG.txt | cut -c1-160))"
  [ $RC -eq 0 ] && OK=$((OK+1)) || { log "$NAME INVALID: integrity failed (registration §1)"; FAIL=$((FAIL+1)); }
done < <(echo "$DS")
log "MISMATCH_EVAL_DONE ok=$OK fail=$FAIL"
exit $FAIL
