#!/bin/bash
# Unified GPU scheduler for the array-scaling stage-2 preparation (replaces gpu_filler.sh + run_fitq.sh lanes; 2026-09-30 CDT).
# Queue logs/gpuq.txt, one job per line:   <prio> <kind> <label> <command ...>
#   prio : integer, larger runs first (training 90, GMM restarts 50, fits 40 ...); ties keep file order
#   kind : GPU  -> needs one free GPU; launched as  CUDA_VISIBLE_DEVICES=<g> <command>  in tmux job_g<g>
#          CPU  -> no GPU (merges); launched as    CUDA_VISIBLE_DEVICES= <command>     in tmux cpu_<label> (label: no . or :)
#          WAIT:<glob>:<count> prefix on kind (e.g. WAIT:results/x/*.k0r[012].npz:3:CPU) -> runnable only when <count> files match
# A GPU is FREE when it has no compute process in two consecutive 60-s checks AND no live job_g<g> session (a job that is still
# starting, e.g. generating channels before CUDA init, keeps its GPU reserved).  Every launch / finish is logged to logs/gpu_sched.log
# with the command's exit code.  The scheduler runs until stopped; add jobs at any time
# (append under `flock logs/gpuq.txt.lock`).  Stop: touch logs/gpu_sched.stop.
cd /home/HTJ/t2_wtS/conf; Q=logs/gpuq.txt; L=logs/gpu_sched.log; touch $Q
log () { echo "[sched $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $*" >> $L; }
busy () {  # GPU index of every compute process (by uuid, so other users' processes count too)
  nvidia-smi --query-compute-apps=gpu_uuid --format=csv,noheader | sort -u | while read u; do
    nvidia-smi --query-gpu=index,uuid --format=csv,noheader | awk -F', ' -v u="$u" '$2==u{print $1}'; done; }
declare -A idle
launch () {  # $1 = session name, $2 = CUDA value, rest = command line
  local s=$1 cv=$2; shift 2; local cmd="$*"
  tmux new -d -s $s "cd /home/HTJ/t2_wtS/conf; CUDA_VISIBLE_DEVICES=$cv $cmd; rc=\$?; echo \"[sched \$(TZ=America/Chicago date '+%m-%d %H:%M %Z')] done rc=\$rc $s: $cmd\" >> $L"
  log "launch $s (CUDA_VISIBLE_DEVICES='$cv'): $cmd"; }
runnable () {  # prints "lineno kind rest" of the best runnable job for the given class (GPU|CPU)
  local want=$1; awk '{print NR" "$0}' $Q | sort -k2,2nr -k1,1n -s | while read ln prio kind label rest; do
    k=$kind
    if [[ $k == WAIT:* ]]; then IFS=: read _ g c k <<< "$kind"; [ "$(ls $g 2>/dev/null | wc -l)" -ge "$c" ] || continue; fi
    [ "$k" = "$want" ] && { echo "$ln $label $rest"; break; }
  done; }
take () { flock $Q.lock sed -i "${1}d" $Q; }
while [ ! -f logs/gpu_sched.stop ]; do
  B=" $(busy | tr '\n' ' ') "
  # CPU jobs (merges): run as soon as their dependencies exist
  while true; do r=$(runnable CPU); [ -z "$r" ] && break
    read ln label rest <<< "$r"; take $ln; launch cpu_$label "" "$rest"; done
  for g in 0 1 2 3 4 5; do
    if [[ "$B" == *" $g "* ]] || tmux has-session -t job_g$g 2>/dev/null; then idle[$g]=0; continue; fi
    idle[$g]=$(( ${idle[$g]:-0} + 1 )); [ "${idle[$g]}" -lt 2 ] && continue
    r=$(runnable GPU); [ -z "$r" ] && continue
    read ln label rest <<< "$r"; take $ln; launch job_g$g $g "$rest"; idle[$g]=0
  done
  sleep 60
done
log "stopped (gpu_sched.stop)"
