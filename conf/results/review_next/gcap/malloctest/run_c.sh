#!/bin/bash
cd /home/HTJ/t2/conf; export CUDA_VISIBLE_DEVICES=
GLIBC_TUNABLES=glibc.malloc.mmap_max=0:glibc.malloc.trim_threshold=68719476736 MALLOC_MMAP_MAX_=0 MALLOC_TRIM_THRESHOLD_=68719476736 \
  taskset -c 12 nice -n 10 ~/miniforge3/envs/torch/bin/python code/runner.py run --testbed D2 --prior UMi28 --cell C9 --ntrain 160000 \
  --stagec-ckpt /home/HTJ/t2/conf/ckpt/d2sx_UMi28NR32_N160000_a1_best.pt --chunk 3 --n 3 --skip0 2560 --snr 0 --arm M-ours-bstar R5-genie \
  --tag U28NR32MTc > /tmp/claude-1005/-home-HTJ-t2/ac4d3602-6d72-4574-8052-16040bb635a9/scratchpad/malloctest/c.log 2>&1
~/miniforge3/envs/torch/bin/python -c "
import glob, numpy as np
c = np.load(glob.glob('raw_U28NR32MTc/*.npz')[0]); r = np.load('raw_U28NR32GCAPdev/D2_C9_UMi28_Nr32_T16_Tp4_eig_snr0_skip2560_n40.npz')
ks = [k for k in c.files if '|' in k and not k.startswith(('meta', 'run'))]
bad = [k for k in ks if not np.array_equal(c[k], r[k][:3], equal_nan=True)]
print('MTc vs GCAPdev rows 0..2:', len(ks), 'arrays compared; differing:', bad)" >> /tmp/claude-1005/-home-HTJ-t2/ac4d3602-6d72-4574-8052-16040bb635a9/scratchpad/malloctest/c.log 2>&1
echo "MTC_DONE $(TZ=America/Chicago date '+%H:%M %Z')" >> /tmp/claude-1005/-home-HTJ-t2/ac4d3602-6d72-4574-8052-16040bb635a9/scratchpad/malloctest/c.log
