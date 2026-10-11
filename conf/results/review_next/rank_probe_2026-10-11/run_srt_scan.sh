#!/bin/bash
# Site scan on ONE GPU: three scenes at the pool's BS height (10 m), then munich at 25 m and 5 m.  Log scan.log, end marker SCAN_DONE.
cd /home/HTJ/t2/conf/results/review_next/rank_probe_2026-10-11 || exit 1
P=~/miniforge3/envs/torch/bin/python; O=~/data/sionna_rt/rank_probe; G=$1
for job in "munich 600 10" "etoile 600 10" "florence 600 10" "munich 200 25" "munich 200 5"; do
  set -- $job; d=$O/${1}_h$3
  echo "[scan $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $job -> $d" >> scan.log
  CUDA_VISIBLE_DEVICES=$G $P -I srt_site_scan.py $1 $2 $3 $d 2>&1 | grep -v -E 'Warning|warn' >> scan.log
  CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=8 $P -I srt_site_rank.py $d/part_$1.npz > rank_${1}_h$3.txt 2>&1
done
echo "[scan $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] SCAN_DONE" >> scan.log
