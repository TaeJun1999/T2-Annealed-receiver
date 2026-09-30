#!/bin/bash
# Fill idle GPUs from the generic fit queue (logs/fitq_queue.txt): every 60 s, a GPU with no compute process in TWO consecutive
# checks (so a lane between two jobs is not mistaken for idle) and no live fitqG<g> session gets `run_fitq.sh <g>`.
# Stops when the queue is empty and no fitq lane is alive.  Log logs/gpu_filler.log.
cd /home/HTJ/t2_wtS/conf; L=logs/gpu_filler.log
busy () { nvidia-smi --query-compute-apps=pid --format=csv,noheader | while read p; do tr '\0' '\n' < /proc/$p/environ 2>/dev/null | grep "^CUDA_VISIBLE_DEVICES="; done | cut -d= -f2; }
declare -A idle
while true; do
  B=" $(busy | tr '\n' ' ') "; left=$(wc -l < logs/fitq_queue.txt)
  alive=$(tmux ls 2>/dev/null | grep -c "^fitqG")
  [ "$left" -eq 0 ] && [ "$alive" -eq 0 ] && { echo "[filler $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] queue empty, no lanes -> stop" >> $L; break; }
  for g in 0 1 2 3 4 5; do
    if [[ "$B" == *" $g "* ]] || tmux has-session -t fitqG$g 2>/dev/null; then idle[$g]=0; continue; fi
    idle[$g]=$(( ${idle[$g]:-0} + 1 ))
    if [ "${idle[$g]}" -ge 2 ] && [ "$left" -gt 0 ]; then
      tmux new -d -s fitqG$g "bash code/run_fitq.sh $g"; idle[$g]=0
      echo "[filler $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] GPU $g idle -> lane fitqG$g" >> $L
    fi
  done
  sleep 60
done
