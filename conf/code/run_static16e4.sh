#!/bin/bash
# NEXT_EXPERIMENTS_STATIC16e4 §1: table B `X -> V1` for the 13 registered baselines on the 6 static datasets, from EXISTING raws
# (no new BLER; a rule-fixed post-hoc computation).  CPU only.  Outputs results/review_next/pairB_ST<TAG>.txt (first line = this
# script's HEAD); log logs/run_static16e4.log, end STATIC_DONE ok= fail=.  Preconditions (review_STATIC16e4 반드시 6): conf/code and
# Demo clean; the registration and DECISIONS.md tracked and clean (= frozen); no earlier pairB_ST output (a re-run needs the user).
# The labels already recorded before this run (§0: b*, V1-pilot, ALD-pilot, ALDv-pilot, R2) are checked by pair_baselines --expect.
cd /home/HTJ/t2/conf; P=~/miniforge3/envs/torch/bin/python; L=logs/run_static16e4.log; export CUDA_VISIBLE_DEVICES=
log () { echo "[static $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $*" | tee -a $L; }
REG=results/review_next/NEXT_EXPERIMENTS_STATIC16e4.md
[ -n "$(git -C /home/HTJ/t2 status --porcelain conf/code Demo)" ] && { log "ABORT: conf/code or Demo dirty"; exit 1; }
for f in $REG DECISIONS.md; do
  [ -n "$(git ls-files $f)" ] && [ -z "$(git status --porcelain $f)" ] || { log "ABORT: $f not tracked+clean (freeze first)"; exit 1; }
done
ls results/review_next/pairB_ST*.txt >/dev/null 2>&1 && { log "ABORT: pairB_ST outputs exist (re-run needs user approval)"; exit 1; }
H=$(git rev-parse --short HEAD); log "start (git $H)"; OK=0; FAIL=0
while read TAG SUF CELL PR BS VP AL AV; do
  O=results/review_next/pairB_ST$TAG.txt
  echo "# run_static16e4 git $H $(TZ=America/Chicago date '+%Y-%m-%d %H:%M %Z')" > $O
  $P code/pair_baselines.py --base raw_$TAG --pil raw_PIL$SUF --ald raw_ALD$SUF --est PIL$SUF --cell $CELL --prior $PR --r0 at1 \
    --provenance manifest --expect-bstar "$BS" --expect "V1-pilot=$VP" --expect "ALD-pilot=$AL" --expect "ALDv-pilot=$AV" \
    --expect "R2-ours-G=(i)" >> $O 2>&1 < /dev/null
  rc=$?; log "$TAG rc=$rc ($(grep -E '^SUMMARY-B' $O | cut -c1-110))"
  [ $rc -eq 0 ] && OK=$((OK+1)) || FAIL=$((FAIL+1))
done <<'T'
B16e4k B16e4k C2 S2 (i) (i) (i) (i)
NR16B16e4 NR16 C6 S2 (i) (iv) (i) (i)
D3B16e4 D3 C2 S2c (i) (i) (i) (i)
SVB16e4 SV C2 SV8e (iv) (iv) (i) (i)
U28B16e4 U28 C2 UMi28 (i) (i) (i) (i)
MXB16e4 MX C2 MIX3 (i) (i) (i) (i)
T
log "STATIC_DONE ok=$OK fail=$FAIL"
