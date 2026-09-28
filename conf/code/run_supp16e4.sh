#!/bin/bash
# NEXT_EXPERIMENTS_SUPP16e4 (DOP16e4 + ROT16e4 supplement, user decision 2026-09-29: "DOP·ROT 보충: baseline 전부"): the
# registered baselines missing from the DOP / ROT tags, on the SAME trials as each of the 24 condition tags
# (DOP{a,b}<suf>: nu 0.005 / 0.01; ROT{a,b}<suf>: 15 / 30 deg; 6 datasets).  Per condition <T> (= the original tag):
#   XL<T>  loop arms M-ours-bstar-scalar M-ours-gmm32 R0-pilot R1-turbo R3-bigamp R4-llr R4-scvamp + R5-genie
#   XP<T>  --pilot-arms: V1-pilot bstar-pilot R5-genie          XA<T>  --ald-file: ALD-pilot ALDv-pilot R5-genie
# The original raw raw_<T> keeps V1 / b* / R2 / genie; every new genie must equal it bit for bit.
#   bash code/run_supp16e4.sh tune [cond ...]   ALD development tuning per condition (dev trials under the SAME Doppler /
#                                               rotation; ald.py regen --set dev -> tune; GPU queue, one job per free GPU)
#   bash code/run_supp16e4.sh eval [cond ...]   ALD test pilots + estimates (GPU) -> XL / XP / XA runs (CPU, GPUs hidden)
#                                               -> run_manifest -> eval_accept (genie replay vs raw_<T>) -> pair_baselines
# cond = original tag (e.g. DOPaB16e4k); arguments name a subset only to RESUME.  Log logs/run_supp16e4.log,
# end markers SUPP_TUNE_DONE / "SUPP_EVAL_DONE ok=<n> fail=<n>".
cd /home/HTJ/t2/conf
P=~/miniforge3/envs/torch/bin/python
L=logs/run_supp16e4.log
log () { echo "[supp $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $*" | tee -a $L >> logs/queue.log; }
MODE=$1; shift
[ -n "$(git -C /home/HTJ/t2 status --porcelain conf/code Demo)" ] && [ "$MODE" = eval ] && { log "ABORT: conf/code or Demo dirty"; exit 1; }
# name suffix cell prior base_fits ckpt sha role bstar kron_K|- ll_val   (= run_dop16e4.sh / run_rot16e4.sh)
DS="D2C2  B16e4k C2 S2    B16e4k    ckpt/d2sx_N160000_a1.pt               4443921ce8d5c4a1 legacy-last kron   1024 -11.459169831224418
D3    D3     C2 S2c   D3B16e4   ckpt/d2sx_S2c_N160000_a1_best.pt      7ebf4e6647d4413f best        kron   4096 0.08879931165293979
SV8e  SV     C2 SV8e  SVB16e4   ckpt/d2sx_SV8e_N160000_a1_best.pt     d2d78962c2846364 best        gmm256 -    -47.80545576704972
UMi28 U28    C2 UMi28 U28B16e4  ckpt/d2sx_UMi28_N160000_a1_best.pt    6f3a1b9490864af1 best        kron   4096 5.797910431000217
MIX3  MX     C2 MIX3  MXB16e4   ckpt/d2sx_MIX3_N160000_a1_best.pt     b591ae24ae3c5f31 best        kron   4096 33.7604873920761
D2C6  NR16   C6 S2    NR16B16e4 ckpt/d2sx_NR16_N160000_a1_fb2_best.pt c050d611b2c714a6 best        kron   4096 63.1751571838059"
CONDS () {   # prints: TAG FLAG VALUE NAME SUF CELL PR BF CK SHA ROLE BS KK LL   (C2 datasets first, C6 last: heavy)
  while read NAME SUF CELL PR BF CK SHA ROLE BS KK LL; do
    for c in "DOPa --doppler 0.005" "DOPb --doppler 0.01" "ROTa --rotation 15" "ROTb --rotation 30"; do
      set -- $c; echo "$1$SUF $2 $3 $NAME $SUF $CELL $PR $BF $CK $SHA $ROLE $BS $KK $LL"
    done
  done < <(echo "$DS")
}
WANT=" $* "
sel () { CONDS | while read T REST; do [ "$WANT" = "  " ] || echo "$WANT" | grep -q " $T " && echo "$T $REST"; done; }
FREE=($(nvidia-smi --query-gpu=index,memory.used --format=csv,noheader,nounits | awk -F', ' '$2 < 100 {print $1}'))
if [ "$MODE" = tune ]; then
  log "tune start (git $(git rev-parse --short HEAD)) free GPUs: ${FREE[*]}"
  Q=logs/supp_tune_queue.txt; sel > $Q
  worker () { local g=$1 line
    while true; do
      line=$(flock $Q.lock sh -c "head -n1 $Q; sed -i 1d $Q"); [ -z "$line" ] && break
      set -- $line; local T=$1 FL=$2 V=$3 PR=$7 CELL=$6 BF=$8 CK=$9
      CUDA_VISIBLE_DEVICES= $P code/ald.py regen --tag XA$T --prior $PR --cell $CELL --fits-tag $BF $FL $V --set dev >> logs/supp_tune_gpu$g.log 2>&1 \
        && CUDA_VISIBLE_DEVICES=$g $P code/ald.py tune --tag XA$T --ckpt $CK >> logs/supp_tune_gpu$g.log 2>&1
      log "GPU $g tune XA$T rc=$? ($(grep -h '"c":' logs/supp_tune_gpu$g.log | tail -1 | cut -c1-90))"
    done; }
  for g in "${FREE[@]}"; do worker $g & done; wait
  log "SUPP_TUNE_DONE $(ls results/ald/tune_XA*.json 2>/dev/null | wc -l)/24 tune records"
  exit 0
fi
[ "$MODE" = eval ] || { echo "usage: run_supp16e4.sh tune|eval [cond ...]"; exit 1; }
log "eval start (git $(git rev-parse --short HEAD))"
# phase 0: fits links, ALD test pilots (CPU) and estimates (GPU, parallel over free GPUs)
i=0
while read T FL V NAME SUF CELL PR BF CK SHA ROLE BS KK LL; do
  for x in XL XP XA; do ln -sfn gmm_fits_D2_$BF results/gmm_fits_D2_$x$T; done
  [ -f results/ald/tune_XA$T.json ] || { log "$T ABORT: no ALD tuning record"; continue; }
  [ -f results/ald/pilots_XA${T}_test.npz ] || CUDA_VISIBLE_DEVICES= $P code/ald.py regen --tag XA$T --prior $PR --cell $CELL \
    --fits-tag $BF $FL $V --set test >> $L 2>&1
  E=results/ald/ald_XA$T.npz
  if [ ! -f $E ] || [ results/ald/tune_XA$T.json -nt $E ]; then
    g=${FREE[$((i % ${#FREE[@]}))]}; i=$((i+1))
    CUDA_VISIBLE_DEVICES=$g $P code/ald.py estimate --tag XA$T --ckpt $CK --set test >> $L 2>&1 &
    [ $((i % ${#FREE[@]})) -eq 0 ] && wait
  fi
done < <(sel); wait
log "phase 0 done: ALD estimates $(ls results/ald/ald_XA*.npz 2>/dev/null | wc -l)"
export CUDA_VISIBLE_DEVICES=
OK=0; FAIL=0
while read T FL V NAME SUF CELL PR BF CK SHA ROLE BS KK LL; do
  R=raw_$T; KARG=""; [ "$KK" != "-" ] && KARG="--kron-K $KK"
  [ -d $R ] || { log "$T ABORT: original raw missing"; FAIL=$((FAIL+1)); continue; }
  [ -f results/ald/ald_XA$T.npz ] || { log "$T ABORT: no ALD estimate"; FAIL=$((FAIL+1)); continue; }
  B="--testbed D2 --prior $PR --cell $CELL --n 2560 --chunk 40 --ntrain 160000 $FL $V --stagec-ckpt /home/HTJ/t2/conf/$CK"
  rc=0
  $P code/runner.py run $B --arm M-ours-bstar-scalar M-ours-gmm32 R0-pilot R1-turbo R3-bigamp R4-llr R4-scvamp R5-genie --tag XL$T \
    > logs/run_D2_XL$T.log 2>&1 || rc=1
  $P code/runner.py run $B --pilot-arms --arm V1-pilot bstar-pilot R5-genie --tag XP$T > logs/run_D2_XP$T.log 2>&1 || rc=1
  $P code/runner.py run $B --ald-file /home/HTJ/t2/conf/results/ald/ald_XA$T.npz --arm ALD-pilot ALDv-pilot R5-genie --tag XA$T \
    > logs/run_D2_XA$T.log 2>&1 || rc=1
  for x in XL XP XA; do $P code/run_manifest.py --tag $x$T >> $L 2>&1; done
  [ $rc -ne 0 ] && { log "$T ABORT: a run failed"; FAIL=$((FAIL+1)); continue; }
  A=results/review_next/X${T}_accept.txt
  $P code/eval_accept.py --prior $PR --ntrain 160000 --bstar $BS $KARG --ll-val $LL --ref-raw $R \
    --tag XL$T:$ROLE:$SHA:$CELL --tag XP$T:$ROLE:$SHA:$CELL --tag XA$T:$ROLE:$SHA:$CELL > $A 2>&1
  RC=$?; log "$T acceptance rc=$RC ($(head -1 $A | cut -c1-90))"
  [ $RC -ne 0 ] && { log "$T INVALID: acceptance failed, no pair_baselines"; FAIL=$((FAIL+1)); continue; }
  $P code/pair_baselines.py --base $R --extra raw_XL$T --pil raw_XP$T --ald raw_XA$T --est XA$T --cell $CELL --prior $PR \
    > results/review_next/pairB_X$T.txt 2>&1
  RC=$?; log "$T pair_baselines rc=$RC ($(grep -E '^SUMMARY|condition' results/review_next/pairB_X$T.txt | tr '\n' ' ' | cut -c1-40))"
  [ $RC -eq 0 ] && OK=$((OK+1)) || { log "$T INVALID: integrity failed"; FAIL=$((FAIL+1)); }
done < <(sel)
log "SUPP_EVAL_DONE ok=$OK fail=$FAIL"
exit $FAIL
