#!/bin/bash
# One-time build of the Sionna RT pool (prior SRT): the scenes of srt_build.SCENES one after another on ONE GPU, then the CPU
# merge (H.npy, split.npy, meta.npz in ~/data/sionna_rt/srt_Nr8).  A scene whose part file exists is skipped.
# Usage: run_srt_build.sh <gpu>          log: logs/srt_build.log, end marker SRT_BUILD_DONE
cd /home/HTJ/t2/conf || exit 1
P=~/miniforge3/envs/torch/bin/python; L=logs/srt_build.log; O=~/data/sionna_rt/srt_Nr8; G=$1
log () { echo "[srt_build $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $*" | tee -a $L; }
[ -n "$G" ] || { echo "usage: run_srt_build.sh <gpu>"; exit 1; }
mkdir -p $O
log "start (git $(git rev-parse --short HEAD)$([ -n "$(git status --porcelain code)" ] && echo +dirty)) GPU $G"
for s in $($P -c "import sys; sys.path.insert(0, 'code'); import srt_build; print(' '.join(srt_build.SCENES))"); do
  [ -f $O/part_$s.npz ] && { log "scene $s: part exists, skipped"; continue; }
  CUDA_VISIBLE_DEVICES=$G $P -I code/srt_build.py scene $s 8 2>&1 | grep -v -E 'Warning|warn' >> $L
  [ -f $O/part_$s.npz ] || { log "ABORT: scene $s wrote no part file"; exit 1; }
  log "scene $s done"
done
CUDA_VISIBLE_DEVICES= $P -I code/srt_build.py merge 8 >> $L 2>&1 || { log "ABORT: merge failed"; exit 1; }
log "SRT_BUILD_DONE"
