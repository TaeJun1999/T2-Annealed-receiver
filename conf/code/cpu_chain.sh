#!/bin/bash
# CPU chain (work queue 2026-09-29 CDT; user: "Queue 에 있는거 잘 확인하고 계속 잘 진행"): wait for the array-scaling stage 1 to finish
# (STAGE1_C6_DONE in ~/t2_wtS/conf/logs/stage1.log), then run the frozen SEEDS3 BLER (run_seeds3_eval.sh), then HISNR16e4 if and
# only if its registration is frozen (tracked + clean) by then; otherwise stop.  One CPU job at a time.  Log logs/cpu_chain.log.
cd /home/HTJ/t2/conf; L=logs/cpu_chain.log
log () { echo "[chain $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $*" >> $L; }
log "waiting for stage 1"
until grep -q STAGE1_C6_DONE /home/HTJ/t2_wtS/conf/logs/stage1.log 2>/dev/null; do sleep 120; done
log "stage 1 done -> SEEDS3 BLER"; bash code/run_seeds3_eval.sh; log "SEEDS3 exit $?"
R=results/review_next/NEXT_EXPERIMENTS_HISNR16e4.md
if [ -n "$(git ls-files $R)" ] && [ -z "$(git status --porcelain $R)" ] && grep -q "동결 — HISNR16e4" DECISIONS.md; then
  log "HISNR registration frozen -> run"; bash code/run_hisnr16e4.sh; log "HISNR exit $?"
else log "HISNR not frozen -> chain stops (run by hand after the freeze)"; fi
log "CHAIN_DONE"
