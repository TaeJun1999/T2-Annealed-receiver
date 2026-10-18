#!/bin/bash
# run_e3e5_chain.sh -- the two registered test runs one after the other from the run commit (each script refuses to start while
# another runner.py run is active, so they cannot overlap): E3' SBL32, then E5 UMi28, then E5 D2 (E5 §1.5: D2 regardless of the
# UMi result; start rule (UMi end + D2 estimate 11 min <= 2026-10-24 06:00 CDT) checked below).  Log logs/run_e3e5_chain.log.
#   cd ~/t2/conf && bash results/review_next/run_e3e5_chain.sh        (tmux)
cd /home/HTJ/t2/conf || exit 1
L=logs/run_e3e5_chain.log; C=24-47,120-143,72-95,168-191
log () { echo "[chain $(TZ=America/Chicago date '+%m-%d %H:%M %Z') git $(git rev-parse --short HEAD)] $*" | tee -a $L; }
log "start SBL32"; bash code/run_sbl32.sh; log "SBL32 exit $?"
log "start E5 U28"; E5_CPUS=$C bash code/run_e5.sh U28; log "E5 U28 exit $?"
if [ $(( $(date +%s) + 11 * 60 )) -le $(TZ=America/Chicago date -d '2026-10-24 06:00' +%s) ]; then
  log "D2 start rule OK (now + 11 min <= 2026-10-24 06:00 CDT)"; log "start E5 D2"; E5_CPUS=$C bash code/run_e5.sh D2; log "E5 D2 exit $?"
else log "D2 start rule NOT met -- D2 not started (E5 §1.5)"; fi
log "CHAIN_DONE"
