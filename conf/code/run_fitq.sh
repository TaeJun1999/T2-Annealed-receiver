#!/bin/bash
# Generic GPU fit queue (array-scaling stage-2 preparation; user 2026-09-29 CDT "남는 컴퓨팅 자원에는 계속 작업을 할당").
# Queue file logs/fitq_queue.txt, one job per line:  <Nr> <fam> <K> <ntrain> <tag> [fit_gpu.py options...]
# A '--merge' job waits (re-queued at the end) until its three restart candidates .k0r{0,1,2}.npz exist.
# One lane per GPU given on the command line; jobs are taken under flock so lanes can be added at any time.
cd /home/HTJ/t2_wtS/conf; P=~/miniforge3/envs/torch/bin/python; Q=logs/fitq_queue.txt; L=logs/fitq.log
touch $Q
lane () { local G=$1 j
  while true; do j=$(flock $Q.lock sh -c "head -n1 $Q; sed -i 1d $Q"); [ -z "$j" ] && break
    set -- $j; Nr=$1; fam=$2; K=$3; n=$4; tag=$5; shift 5
    if [ "$*" != "${*/--merge/}" ]; then
      pr=$(echo "$*" | grep -oE -- '--prior [A-Za-z0-9]+' | cut -d' ' -f2); pr=${pr:-S2}
      c=$(ls results/gmm_fits_D2_$tag/fit_${pr}_Nr${Nr}_${fam}K${K}_n${n}.k0r[012].npz 2>/dev/null | wc -l)
      if [ "$c" -lt 3 ]; then flock $Q.lock sh -c "echo '$j' >> $Q"; sleep 300; continue; fi
    fi
    echo "[fitq $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] GPU $G start: $j" >> $L
    CUDA_VISIBLE_DEVICES=$G $P code/fit_gpu.py $Nr $fam $K $n $tag "$@" >> logs/fitq_gpu$G.log 2>&1
    echo "[fitq $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] GPU $G done rc=$?: $j" >> $L; done; }
for g in "$@"; do lane $g & done; wait
