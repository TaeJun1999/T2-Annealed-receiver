#!/bin/bash
cd /home/HTJ/t2/conf; P=~/miniforge3/envs/torch/bin/python; export CUDA_VISIBLE_DEVICES=
$P /tmp/claude-1005/-home-HTJ-t2/ac4d3602-6d72-4574-8052-16040bb635a9/scratchpad/malloctest/run_variant.py U28NR32MTa 10 > /tmp/claude-1005/-home-HTJ-t2/ac4d3602-6d72-4574-8052-16040bb635a9/scratchpad/malloctest/a.log 2>&1 &
GLIBC_TUNABLES=glibc.malloc.mmap_max=0:glibc.malloc.trim_threshold=68719476736 MALLOC_MMAP_MAX_=0 MALLOC_TRIM_THRESHOLD_=68719476736 \
  $P /tmp/claude-1005/-home-HTJ-t2/ac4d3602-6d72-4574-8052-16040bb635a9/scratchpad/malloctest/run_variant.py U28NR32MTb 11 > /tmp/claude-1005/-home-HTJ-t2/ac4d3602-6d72-4574-8052-16040bb635a9/scratchpad/malloctest/b.log 2>&1 &
wait; echo "MALLOCTEST_DONE $(TZ=America/Chicago date '+%H:%M %Z')" >> /tmp/claude-1005/-home-HTJ-t2/ac4d3602-6d72-4574-8052-16040bb635a9/scratchpad/malloctest/done.log
