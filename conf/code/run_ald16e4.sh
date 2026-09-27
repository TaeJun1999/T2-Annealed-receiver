#!/bin/bash
# (NEXT_EXPERIMENTS_ALD16e4 §1, after the freeze commit) Arvinte-Tamir annealed-Langevin pilot-only estimation with the V1
# network, six datasets.  Phase 1 (CPU, GPUs hidden): regenerate the TEST pilot sites (code/ald.py regen).  Phase 2 (GPU
# 0..5, one dataset per GPU, the only GPU step): the frozen-hyper-parameter ALD estimates (code/ald.py estimate).  Phase 3
# (CPU, GPUs hidden, sequential): runner with --ald-file, arms ALD-pilot / ALDv-pilot / R5-genie -> run_manifest ->
# eval_accept (genie replay vs the base raw) -> pair_ald ONLY if eval_accept passed.  All six are run and reported; arguments
# name a subset only to RESUME.  Log logs/run_ald16e4.log, end marker "ALD_EVAL_DONE ok=<n> fail=<n>".
cd /home/HTJ/t2/conf
P=~/miniforge3/envs/torch/bin/python
L=logs/run_ald16e4.log
log () { echo "[ald16e4 $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $*" | tee -a $L >> logs/queue.log; }
[ -n "$(git -C /home/HTJ/t2 status --porcelain conf/code Demo)" ] && { log "ABORT: conf/code or Demo dirty"; exit 1; }
# name  est_tag  run_tag  cell prior base_fits  base_raw  pil_raw  ckpt  sha  role  bstar kron_K|- ll_val
DS="D2C2  PILB16e4k ALDB16e4k C2 S2    B16e4k    raw_B16e4k    raw_PILB16e4k ckpt/d2sx_N160000_a1.pt               4443921ce8d5c4a1 legacy-last kron   1024 -11.459169831224418
D2C6  PILNR16   ALDNR16   C6 S2    NR16B16e4 raw_NR16B16e4 raw_PILNR16   ckpt/d2sx_NR16_N160000_a1_fb2_best.pt c050d611b2c714a6 best        kron   4096 63.1751571838059
D3    PILD3     ALDD3     C2 S2c   D3B16e4   raw_D3B16e4   raw_PILD3     ckpt/d2sx_S2c_N160000_a1_best.pt      7ebf4e6647d4413f best        kron   4096 0.08879931165293979
SV8e  PILSV     ALDSV     C2 SV8e  SVB16e4   raw_SVB16e4   raw_PILSV     ckpt/d2sx_SV8e_N160000_a1_best.pt     d2d78962c2846364 best        gmm256 -    -47.80545576704972
UMi28 PILU28    ALDU28    C2 UMi28 U28B16e4  raw_U28B16e4  raw_PILU28    ckpt/d2sx_UMi28_N160000_a1_best.pt    6f3a1b9490864af1 best        kron   4096 5.797910431000217
MIX3  PILMX     ALDMX     C2 MIX3  MXB16e4   raw_MXB16e4   raw_PILMX     ckpt/d2sx_MIX3_N160000_a1_best.pt     b591ae24ae3c5f31 best        kron   4096 33.7604873920761"
WANT="$*"
for w in $WANT; do echo "$DS" | grep -q "^$w " || { log "ABORT: unknown dataset '$w'"; exit 1; }; done
sel () { echo "$DS" | while read NAME REST; do [ -z "$WANT" ] || echo " $WANT " | grep -q " $NAME " && echo "$NAME $REST"; done; }
log "start (git $(git rev-parse --short HEAD)) datasets: ${WANT:-all}"
# phase 1: test pilot sites (CPU)
while read NAME ET RT CELL PR BF BASE PIL CK SHA ROLE BS KK LL; do
  [ -f results/ald/pilots_${ET}_test.npz ] || CUDA_VISIBLE_DEVICES= $P code/ald.py regen --tag $ET --prior $PR --cell $CELL \
    --fits-tag $BF --set test >> $L 2>&1 &
done < <(sel); wait
# phase 2: ALD estimates, one dataset per FREE GPU (memory.used < 100 MiB now; exclusive-process GPUs).  A dataset with no
# free GPU is logged and left without an estimate (phase 3 then ABORTs it; resuming it later needs no approval).  An
# estimate older than its tune record is recomputed (never reused silently); runner also checks the checkpoint sha.
FREE=($(nvidia-smi --query-gpu=index,memory.used --format=csv,noheader,nounits | awk -F', ' '$2 < 100 {print $1}'))
i=0
while read NAME ET RT CELL PR BF BASE PIL CK SHA ROLE BS KK LL; do
  E=results/ald/ald_${ET}.npz; TJ=results/ald/tune_${ET}.json
  [ -f $E ] && [ $E -nt $TJ ] && continue
  [ $i -lt ${#FREE[@]} ] || { log "$NAME: no free GPU for the ALD estimate (deferred)"; continue; }
  CUDA_VISIBLE_DEVICES=${FREE[$i]} $P code/ald.py estimate --tag $ET --ckpt $CK --set test >> $L 2>&1 &
  i=$((i+1))
done < <(sel); wait
log "phases 1-2 done: $(ls results/ald/ald_PIL*.npz 2>/dev/null | grep -vc _dev) estimate files"
# phase 3: receiver (CPU) per dataset
OK=0; FAIL=0
while read NAME ET RT CELL PR BF BASE PIL CK SHA ROLE BS KK LL; do
  [ -f results/ald/ald_${ET}.npz ] || { log "$NAME ABORT: no ALD estimate file"; FAIL=$((FAIL+1)); continue; }
  [ "$(sha256sum $CK | cut -c1-16)" = "$SHA" ] || { log "$NAME ABORT: ckpt sha differs"; FAIL=$((FAIL+1)); continue; }
  ln -sfn gmm_fits_D2_$BF results/gmm_fits_D2_$RT
  CUDA_VISIBLE_DEVICES= $P code/runner.py run --testbed D2 --prior $PR --cell $CELL --n 2560 --chunk 40 --ntrain 160000 \
    --stagec-ckpt /home/HTJ/t2/conf/$CK --ald-file /home/HTJ/t2/conf/results/ald/ald_${ET}.npz \
    --arm ALD-pilot ALDv-pilot R5-genie --tag $RT > logs/run_D2_$RT.log 2>&1 || { log "$NAME ABORT: run failed"; FAIL=$((FAIL+1)); continue; }
  CUDA_VISIBLE_DEVICES= $P code/run_manifest.py --tag $RT >> $L 2>&1; log "$NAME run_manifest rc=$?"
  KARG=""; [ "$KK" != "-" ] && KARG="--kron-K $KK"
  CUDA_VISIBLE_DEVICES= $P code/eval_accept.py --prior $PR --tag $RT:$ROLE:$SHA:$CELL --ntrain 160000 --bstar $BS $KARG --ll-val $LL \
    --ref-raw $BASE > results/review_next/${RT}_accept.txt 2>&1
  RC=$?; log "$NAME acceptance rc=$RC ($(head -1 results/review_next/${RT}_accept.txt))"
  [ $RC -ne 0 ] && { log "$NAME INVALID: acceptance failed, no pair_ald (registration §1)"; FAIL=$((FAIL+1)); continue; }
  CUDA_VISIBLE_DEVICES= $P code/pair_ald.py --base $BASE --pil $PIL --ald raw_$RT --est $ET --cell $CELL --prior $PR \
    > results/review_next/pair_$RT.txt 2>&1
  RC=$?; log "$NAME pair_ald rc=$RC ($(head -1 results/review_next/pair_$RT.txt | cut -c1-160))"
  [ $RC -eq 0 ] && OK=$((OK+1)) || { log "$NAME INVALID: integrity failed (registration §1)"; FAIL=$((FAIL+1)); }
done < <(sel)
log "ALD_EVAL_DONE ok=$OK fail=$FAIL"
exit $FAIL
