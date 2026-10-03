#!/bin/bash
# Stage-2 preparation (user 2026-09-29 CDT: "남는 컴퓨팅 자원에는 계속 작업을 할당"): D2 C9 (Nr 32) GMM fits at N = 1.6e5, tag NR32B16e4,
# the part needed whatever kron-K cap stage 2 registers (full 16..512, kron 16..1024).  full K16 / kron K64 / K256 are copies of
# the stage-0 probe fits (tag probeC9, same fit_gpu.py protocol and seed tuple).  One lane per GPU given on the command line;
# jobs are taken from logs/c9fits_queue.txt under flock, so lanes can be added later.  Existing fit files are skipped by fit_gpu.py.
cd /home/HTJ/t2_wtS/conf; P=~/miniforge3/envs/torch/bin/python; Q=logs/c9fits_queue.txt
lane () { local G=$1 j
  while true; do j=$(flock $Q.lock sh -c "head -n1 $Q; sed -i 1d $Q"); [ -z "$j" ] && break
    echo "[c9fits $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] GPU $G start: $j" >> logs/c9fits.log
    set -- $j; CUDA_VISIBLE_DEVICES=$G $P code/fit_gpu.py 32 $1 $2 160000 NR32B16e4 ${@:3} >> logs/c9fits_gpu$G.log 2>&1
    echo "[c9fits $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] GPU $G done rc=$?: $j" >> logs/c9fits.log; done; }
for g in "$@"; do lane $g & done; wait   # kron 1024 restarts are merged by hand afterwards (fit_gpu.py ... --merge)
