#!/bin/bash
# NEXT_EXPERIMENTS_SEEDSROOM16e4 (after its freeze commit): the four seed-repeat tags of the two Sionna RT room pools on the TEST
# set, one after the other -- SRBB16e4s2, SRBB16e4s3 (prior SRB), SRPB16e4s2, SRPB16e4s3 (prior SRP).  Each tag is ONE call of
# code/run_seeds16e4.sh (NEXT_EXPERIMENTS_SEEDS16e4 §1: same cell, fits, trials and arms as the a1 tag, only the diffusion
# checkpoint differs; analysis, manifest, guard, recovery_ci, eval_accept, --ref-arms all) with the arguments of §1 / §5.
# A tag counts as ok only with SEEDS_EVAL_DONE, 'ACCEPT: OK -- <TAG>' AND the --ref-arms all gate (every point shares 2560/2560 trials,
# no key missing, only Stage C arms {V0, V1, V4, V4b} differ from the a1 raw) -- review S1, as run_seedsnr16e4.sh's refok.
# CPU: the user limited the runner to about half of the 192 threads (2026-10-12 CDT) -- every call runs under
# `taskset -c 24-47,120-143,72-95,168-191` (NUMA nodes 1 and 3, 96 threads); runner.py still starts 192 workers (no --jobs flag by
# design), the receiver is CPU-deterministic, so only the wall time changes.  GPUs hidden.
# Usage: tmux new -d -s seedsroom "bash code/run_seedsroom16e4.sh"     log logs/run_seedsroom16e4.log, end "SEEDSROOM_DONE ok=<n> fail=<n>"
cd /home/HTJ/t2/conf; export CUDA_VISIBLE_DEVICES=
L=logs/run_seedsroom16e4.log; CPUS=24-47,120-143,72-95,168-191
log () { echo "[seedsroom $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $*" | tee -a $L; }
REG=results/review_next/NEXT_EXPERIMENTS_SEEDSROOM16e4.md
[ -z "$(git -C /home/HTJ/t2 status --porcelain conf/code Demo)" ] || { log "ABORT (precondition): conf/code or Demo dirty"; exit 1; }
for f in $REG DECISIONS.md; do [ -n "$(git ls-files $f)" ] && [ -z "$(git status --porcelain $f)" ] || { log "ABORT (precondition): $f not tracked+clean"; exit 1; }; done
pgrep -f 'code/runner[.]py run' > /dev/null && { log "ABORT (precondition): another runner.py run is alive"; exit 1; }
H=$(git rev-parse --short HEAD)
# TAG|PRIOR|CKPT (relative to conf/)|REF raw|BSTAR|KRON_K|LL_VAL|SHA16 of the _best checkpoint (§5)|GRID
ROWS='SRBB16e4s2|SRB|ckpt/d2sx_SRB_N160000_a2_best.pt|raw_SRBB16e4|gmm1024|2048|97.00871495382869|2d3e7eae6bb20008|full:16,32,64,128,256,512,1024 kron:16,32,64,128,256,512,1024,2048
SRBB16e4s3|SRB|ckpt/d2sx_SRB_N160000_a3_best.pt|raw_SRBB16e4|gmm1024|2048|97.00871495382869|9f6a9d5042587ae5|full:16,32,64,128,256,512,1024 kron:16,32,64,128,256,512,1024,2048
SRPB16e4s2|SRP|ckpt/d2sx_SRP_N160000_a2_best.pt|raw_SRPB16e4|kron|4096|244.1932863626755|bdc0f5e854d2abbd|full:16,32,64,128,256,512 kron:16,32,64,128,256,512,1024,2048,4096
SRPB16e4s3|SRP|ckpt/d2sx_SRP_N160000_a3_best.pt|raw_SRPB16e4|kron|4096|244.1932863626755|5db51008da6cc8df|full:16,32,64,128,256,512 kron:16,32,64,128,256,512,1024,2048,4096'
X=$(for t in $(cut -d'|' -f1 <<< "$ROWS"); do ls -d raw_$t 2>/dev/null; done | tr '\n' ' ')
[ -z "$X" ] || { log "ABORT (precondition): raw(s) exist: $X(a re-run of a tag needs user approval)"; exit 1; }
log "start (git $H) tags: $(cut -d'|' -f1 <<< "$ROWS" | tr '\n' ' ')cpus $CPUS"; OK=0; FAIL=0
while IFS='|' read -r TAG PR CK REF BS KK LL SHA GRID; do
  [ "$(git rev-parse --short HEAD)" = "$H" ] || { log "ABORT: HEAD moved from $H during the run"; exit 1; }
  log "$TAG: run_seeds16e4.sh $PR $TAG $CK $REF $BS $KK $LL $SHA best \"$GRID\""
  taskset -c $CPUS bash code/run_seeds16e4.sh $PR $TAG $CK $REF $BS $KK $LL $SHA best "$GRID" < /dev/null
  RA=results/review_next/${TAG}_refarms.txt   # gate (§1 수용): every point shares 2560/2560 trials, no key missing, only Stage C arms differ from the a1 raw
  refok () { [ "$(head -1 $RA 2>/dev/null)" = "ACCEPT: FAILED" ] && [ "$(sed 1d $RA | wc -l)" -ge 1 ] && ! sed 1d $RA | grep -v -E \
    "^  $TAG \('C2', -?[0-9]+\): replay vs $REF \(all\): shared 2560/2560, arms differing \[('M-ours-dscore-C-V(0|1|4|4b)'(, )?)+\] \(max \|diff\| [^)]*\)$" | grep -q .; }
  if grep -q 'SEEDS_EVAL_DONE' logs/run_seeds16e4_$TAG.log 2>/dev/null && [ "$(head -1 results/review_next/${TAG}_accept.txt 2>/dev/null)" = "ACCEPT: OK -- $TAG" ] && refok; then
    OK=$((OK+1)); log "$TAG done: $(head -1 results/review_next/${TAG}_accept.txt); ref-arms gate ok: $(grep -o 'arms differing \[[^]]*\]' $RA | sort -u | tr '\n' ' ')"
  else FAIL=$((FAIL+1)); log "$TAG NOT accepted (see logs/run_seeds16e4_$TAG.log, results/review_next/${TAG}_accept.txt, $RA) -- continuing with the next tag"; fi
done <<< "$ROWS"
log "SEEDSROOM_DONE ok=$OK fail=$FAIL"
