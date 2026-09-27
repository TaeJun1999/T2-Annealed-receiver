#!/bin/bash
# (NEXT_EXPERIMENTS_PILOT16e4 §1, after the freeze commit) pilot-only arms on the TEST set, six datasets, the SAME weights,
# fits and trials as each base tag; only V1-pilot, bstar-pilot and R5-genie are run (the loop arms are read from the base raw,
# paired by trial stream).  Per dataset: run -> run_manifest -> eval_accept (meta, ckpt id, genie replay vs the base raw) ->
# pair_cross (integrity + registered comparisons) ONLY if eval_accept passed.  runner.py analysis is NOT run: its table_A
# needs R2-ours-G, which a pilot-only raw does not hold.  GPUs hidden (38.901 datasets; DECISIONS 80bae849).  Log
# logs/run_pilot16e4.log, end marker "PILOT_EVAL_DONE ok=<n> fail=<n>".  All six are run and reported (registration §1);
# arguments name a subset only to RESUME an interrupted dataset (finished chunks are skipped by the runner).
#   Usage: run_pilot16e4.sh [D2C2 D2C6 D3 SV8e UMi28 MIX3]   (default: all six)
cd /home/HTJ/t2/conf
export CUDA_VISIBLE_DEVICES=
P=~/miniforge3/envs/torch/bin/python
L=logs/run_pilot16e4.log
log () { echo "[pilot16e4 $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $*" | tee -a $L >> logs/queue.log; }
[ -n "$(git -C /home/HTJ/t2 status --porcelain conf/code Demo)" ] && { log "ABORT: conf/code or Demo dirty"; exit 1; }
# name  tag  cell prior base_raw  ckpt  sha  role  bstar kron_K ll_val
DS="D2C2   PILB16e4k C2 S2    raw_B16e4k    ckpt/d2sx_N160000_a1.pt                4443921ce8d5c4a1 legacy-last kron   1024 -11.459169831224418
D2C6   PILNR16   C6 S2    raw_NR16B16e4 ckpt/d2sx_NR16_N160000_a1_fb2_best.pt  c050d611b2c714a6 best        kron   4096 63.1751571838059
D3     PILD3     C2 S2c   raw_D3B16e4   ckpt/d2sx_S2c_N160000_a1_best.pt       7ebf4e6647d4413f best        kron   4096 0.08879931165293979
SV8e   PILSV     C2 SV8e  raw_SVB16e4   ckpt/d2sx_SV8e_N160000_a1_best.pt      d2d78962c2846364 best        gmm256 -    -47.80545576704972
UMi28  PILU28    C2 UMi28 raw_U28B16e4  ckpt/d2sx_UMi28_N160000_a1_best.pt     6f3a1b9490864af1 best        kron   4096 5.797910431000217
MIX3   PILMX     C2 MIX3  raw_MXB16e4   ckpt/d2sx_MIX3_N160000_a1_best.pt      b591ae24ae3c5f31 best        kron   4096 33.7604873920761"
WANT="$*"
for w in $WANT; do echo "$DS" | grep -q "^$w " || { log "ABORT: unknown dataset '$w'"; exit 1; }; done
log "start (git $(git rev-parse --short HEAD)) datasets: ${WANT:-all}"
OK=0; FAIL=0
while read NAME TAG CELL PR BASE CK SHA ROLE BS KK LL; do
  [ -n "$WANT" ] && ! echo " $WANT " | grep -q " $NAME " && continue
  [ -L results/gmm_fits_D2_$TAG ] || { log "$NAME ABORT: fits link gmm_fits_D2_$TAG missing"; FAIL=$((FAIL+1)); continue; }
  [ "$(sha256sum $CK | cut -c1-16)" = "$SHA" ] || { log "$NAME ABORT: ckpt sha differs"; FAIL=$((FAIL+1)); continue; }
  $P code/runner.py run --testbed D2 --prior $PR --cell $CELL --n 2560 --chunk 40 --ntrain 160000 \
    --stagec-ckpt /home/HTJ/t2/conf/$CK --pilot-arms --arm V1-pilot bstar-pilot R5-genie --tag $TAG > logs/run_D2_$TAG.log 2>&1 \
    || { log "$NAME ABORT: run failed"; FAIL=$((FAIL+1)); continue; }
  $P code/run_manifest.py --tag $TAG >> $L 2>&1
  KARG=""; [ "$KK" != "-" ] && KARG="--kron-K $KK"
  $P code/eval_accept.py --prior $PR --tag $TAG:$ROLE:$SHA:$CELL --ntrain 160000 --bstar $BS $KARG --ll-val $LL --ref-raw $BASE \
    > results/review_next/${TAG}_accept.txt 2>&1
  RC=$?; log "$NAME acceptance rc=$RC ($(head -1 results/review_next/${TAG}_accept.txt))"
  [ $RC -ne 0 ] && { log "$NAME INVALID: acceptance failed, no pair_cross (registration §1)"; FAIL=$((FAIL+1)); continue; }
  $P code/pair_cross.py --base $BASE --pilot raw_$TAG --cell $CELL --prior $PR > results/review_next/pair_$TAG.txt 2>&1
  RC=$?; log "$NAME pair_cross rc=$RC ($(head -1 results/review_next/pair_$TAG.txt | cut -c1-160))"
  [ $RC -eq 0 ] && OK=$((OK+1)) || { log "$NAME INVALID: integrity failed (registration §1)"; FAIL=$((FAIL+1)); }
done < <(echo "$DS")
log "PILOT_EVAL_DONE ok=$OK fail=$FAIL"
exit $FAIL
