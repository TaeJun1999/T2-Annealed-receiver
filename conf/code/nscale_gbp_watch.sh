#!/bin/bash
# NSCALE GB' watcher (tmux nsgbp; replaces the first version logs/nscale/gbp_watch.sh, 2026-10-04 CDT).  Queues each tag's GB'
# re-run on gpuq ONCE, at priority 90, when ALL of:
#   (a) the tag's grid has its 15 final fits (full 6 + kron 9; .k0r* candidates excluded by the glob);
#   (b) the LAST '# done' line of the V1 training log has aborted=False and is not stopped_by=diverged (training finished;
#       an interrupted run (aborted=True, still rc=0) is NOT queued -- the main session resumes it with ONE --no-gbprime job
#       and this watcher queues GB' after that job's own '# done ... aborted=False');
#   (c) no job of that stem is queued in gpuq.txt or running (pgrep -f) -- a GB' job resumes the same checkpoint, so it must
#       never overlap a training / resume / earlier GB' job of the stem; and (d) logs/nscale/gbp_<T>.log does not exist yet
#       (GB' queued at most once, also across watcher restarts).
# diverged -> ALERT, tag dropped (§3d ladder by the main session); training rc != 0 in gpu_sched.log -> ALERT, tag dropped.
# Log: logs/nscale/gbp_watch.log.  M / S / ONESHOT=1 (one pass) / PGREP=false (tests only) may be set in the environment.
M=${M:-/home/HTJ/t2/conf}; S=${S:-/home/HTJ/t2_wtS/conf/logs}; P=/home/HTJ/miniforge3/envs/torch/bin/python
L=$M/logs/nscale/gbp_watch.log
declare -A CMD=( [B64e4]="run_d2_sx.py --ntrain 640000 --tag B64e4" [B128e4]="run_d2_sx.py --ntrain 1280000 --tag B128e4"
                 [NR16B64e4]="train_nr16.py --nr 16 --ntrain 640000 --fits-tag NR16B64e4" )
declare -A GL=( [B64e4]="fit_S2_Nr8_*_n640000.npz" [B128e4]="fit_S2_Nr8_*_n1280000.npz" [NR16B64e4]="fit_S2_Nr16_*_n640000.npz" )
declare -A TL=( [B64e4]=train_d2sx_N640000_a1.log [B128e4]=train_d2sx_N1280000_a1.log [NR16B64e4]=train_d2sx_NR16_N640000_a1.log )
declare -A TR=( [B64e4]="run_d2_sx.py --ntrain 640000 --no-gbprime" [B128e4]="run_d2_sx.py --ntrain 1280000 --no-gbprime"
                [NR16B64e4]="train_nr16.py --nr 16 --ntrain 640000 --no-gbprime" )
declare -A STEM=( [B64e4]="run_d2_sx.py --ntrain 640000 " [B128e4]="run_d2_sx.py --ntrain 1280000 "
                  [NR16B64e4]="train_nr16.py --nr 16 --ntrain 640000 " )   # matches the training, its resume and the GB' job
log () { echo "[gbp $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $*" >> $L; }
drop () { left=$(echo $left | tr ' ' '\n' | grep -vx $1 | tr '\n' ' '); }
declare -A said; log "start (v2: aborted / stem guards)"; left="B64e4 B128e4 NR16B64e4"
while [ -n "$left" ]; do
  for t in $left; do
    n=$(ls $M/results/gmm_fits_D2_$t/${GL[$t]} 2>/dev/null | wc -l)
    last=$(grep "^# done" $M/logs/${TL[$t]} 2>/dev/null | tail -1)
    busy=$({ grep -F "${STEM[$t]}" $S/gpuq.txt; ${PGREP:-pgrep} -f "${STEM[$t]}"; } 2>/dev/null | head -1)
    if [[ $last == *stopped_by=diverged* ]]; then log "ALERT $t training DIVERGED -> not queued (§3d ladder: main session)"; drop $t
    elif grep -q "done rc=[^0].*${TR[$t]}" $S/gpu_sched.log; then log "ALERT training rc!=0 for $t -> not queued (main session)"; drop $t
    elif [[ $last == *aborted=True* ]]; then
      [ "${said[$t]}" = int ] || log "NOTE $t training interrupted (aborted=True) -> waiting for ONE --no-gbprime resume by the main session"
      said[$t]=int
    elif [ -e $M/logs/nscale/gbp_$t.log ]; then log "$t: gbp_$t.log exists (GB' already queued once) -> skip"; drop $t
    elif [ "$n" -ge 15 ] && [[ $last == *aborted=False* ]] && [ -z "$busy" ]; then
      line="90 GPU gbp$t env -C $M $P code/${CMD[$t]} > $M/logs/nscale/gbp_$t.log 2>&1"
      flock $S/gpuq.txt.lock sh -c "echo '$line' >> $S/gpuq.txt"; log "queued: $line"; drop $t
    fi
  done
  [ "$ONESHOT" = 1 ] && break; sleep 120
done; [ -z "$left" ] && log "GBP_WATCH_DONE"
