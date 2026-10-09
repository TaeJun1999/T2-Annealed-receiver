#!/bin/bash
# NEXT_EXPERIMENTS_SITE16e4 §1: table B `M-ours-dscore-C-V4 -> M-ours-dscore-C-V1` on the headline cell (D2 C2, raw_B16e4k) at the
# FIXED decision SNRs -3 / 0 / +3 dB, from the EXISTING raw (no new BLER; a rule-fixed post-hoc computation).  CPU only.
#   1  drift check: `M-ours-bstar -> V1` and `M-ours-bstar -> V4` recomputed with the same code; their sign-test line and SNR@0.1
#      line must be the recorded lines of results/tables_D2_B16e4k.txt (:369 :372 :375 :378) character for character, and the
#      failure counts, decision SNRs and labels must be the registration's §0 values.  Any difference -> ABORT, V4 -> V1 is NOT computed.
#   2  V4 -> V1 (once).
# Output results/review_next/pairB_SITEB16e4k.txt (first line = this script's HEAD + this script's own sha256[:16] and path, so a
# record audit can tell a modified copy); log logs/run_site16e4.log, end SITE_DONE rc=.
# Preconditions: conf/code and Demo clean; the registration, DECISIONS.md and the recorded table tracked and clean (= frozen);
# HEAD = the freeze commit (the last commit touching the registration); no earlier output.  After any ABORT the partial output
# stays where it is and blocks a re-run: a re-run needs the user (who has the file moved aside first).
cd /home/HTJ/t2/conf; P=~/miniforge3/envs/torch/bin/python; L=logs/run_site16e4.log; export CUDA_VISIBLE_DEVICES=
log () { echo "[site $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $*" | tee -a $L; }
REG=results/review_next/NEXT_EXPERIMENTS_SITE16e4.md; O=results/review_next/pairB_SITEB16e4k.txt; T=results/tables_D2_B16e4k.txt
BS=M-ours-bstar; V1=M-ours-dscore-C-V1; V4=M-ours-dscore-C-V4
ARGS="--base raw_B16e4k --pil raw_PILB16e4k --ald raw_ALDB16e4k --est PILB16e4k --cell C2 --prior S2 --provenance manifest"
[ -n "$(git -C /home/HTJ/t2 status --porcelain conf/code Demo)" ] && { log "ABORT: conf/code or Demo dirty"; exit 1; }  # PRE
for f in $REG DECISIONS.md $T; do  # PRE
  [ -n "$(git ls-files $f)" ] && [ -z "$(git status --porcelain $f)" ] || { log "ABORT: $f not tracked+clean (freeze first)"; exit 1; }  # PRE
done  # PRE
[ "$(git log -1 --format=%H -- $REG)" = "$(git rev-parse HEAD)" ] || { log "ABORT: HEAD is not the freeze commit (the last commit touching $REG)"; exit 1; }  # PRE
[ -e $O ] && { log "ABORT: $O exists (a re-run needs user approval)"; exit 1; }  # PRE
H=$(git rev-parse --short HEAD); log "start (git $H)"
echo "# run_site16e4 git $H $(TZ=America/Chicago date '+%Y-%m-%d %H:%M %Z')  script sha256[:16] $(sha256sum "$0" | cut -c1-16)  ($0)" > $O
echo "# step 1 -- drift check: the two recorded pairs, recomputed (anchor rule)" >> $O
$P code/pair_baselines.py $ARGS --pairs "$BS>$V1" "$BS>$V4" >> $O 2>&1 < /dev/null \
  || { log "ABORT: the drift-check run itself failed (integrity? see $O)"; echo "# STEP 1 FAILED -- V4 -> V1 not computed" >> $O; exit 1; }
# the recorded values (registration §0): sign-test and SNR@0.1 lines as printed in $T, failure counts, decision SNRs, labels
EXP=(
"$BS -> $V1  [anchor $BS]  decision SNRs ['-3', '+0', '+3']"
"    sign test @16: -3 dB 302:50 p=4.7e-45  +0 dB 117:21 p=2.4e-17  +3 dB 35:7 p=1.5e-05   pooled 454:78 p=1.7e-65"
"    SNR@0.1 gap ($BS minus $V1): +1.41 dB  [90% paired bootstrap +1.22, +1.64; censored replicates 0%]"
"    failures@16 at the decision SNRs: $BS 623/184/57  $V1 371/88/29"
"$BS -> $V4  [anchor $BS]  decision SNRs ['-3', '+0', '+3']"
"    sign test @16: -3 dB 285:56 p=4.5e-38  +0 dB 111:23 p=5e-15  +3 dB 42:6 p=1e-07   pooled 438:85 p=2.8e-58"
"    SNR@0.1 gap ($BS minus $V4): +1.27 dB  [90% paired bootstrap +1.08, +1.50; censored replicates 0%]"
"    failures@16 at the decision SNRs: $BS 623/184/57  $V4 394/96/21"
)
for e in "${EXP[@]}"; do
  [ "$(grep -cxF -- "$e" $O)" = 1 ] || { log "ABORT (drift): not exactly once in the recomputation: $e"; echo "# DRIFT CHECK: FAILED -- V4 -> V1 not computed" >> $O; exit 1; }
done
for i in 1 2 5 6; do     # the sign-test / SNR@0.1 lines above are the record's own lines (the COMMITTED table)
  git -C /home/HTJ/t2 show HEAD:conf/$T | grep -qxF -- "${EXP[$i]}" \
    || { log "ABORT (drift): not a line of HEAD:conf/$T: ${EXP[$i]}"; echo "# DRIFT CHECK: FAILED -- V4 -> V1 not computed" >> $O; exit 1; }
done
[ "$(grep -cxF -- "    POWERED=True  second arm fewer at 3/3, first arm fewer at 0/3  -> (i)" $O)" = 2 ] \
  || { log "ABORT (drift): the two recorded labels are not both (i) 3/3"; echo "# DRIFT CHECK: FAILED -- V4 -> V1 not computed" >> $O; exit 1; }
# exactly 2 pair headers + 2 label lines so far: any extra line with ' -> ' (another pair, a load_raw NOTE) aborts -- deliberately conservative
[ "$(grep -c -- " -> " $O)" = 4 ] || { log "ABORT (drift): unexpected pair blocks in the drift step"; echo "# DRIFT CHECK: FAILED -- V4 -> V1 not computed" >> $O; exit 1; }
echo "# DRIFT CHECK: OK -- 8 recorded lines reproduced character for character (4 of them = lines of HEAD:conf/$T), both labels (i) 3/3" >> $O
log "drift check OK"
echo "# step 2 -- the registered pair, decision SNRs fixed at -3 / 0 / +3 dB (NEXT_EXPERIMENTS_SITE16e4 §1)" >> $O
$P code/pair_baselines.py $ARGS --pairs "$V4>$V1@-3,0,3" >> $O 2>&1 < /dev/null; rc=$?   # RUN
log "SITE_DONE rc=$rc ($(grep -E '^    POWERED' $O | tail -1 | cut -c1-110))"
exit $rc
