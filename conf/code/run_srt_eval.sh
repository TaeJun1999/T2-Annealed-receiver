#!/bin/bash
# NEXT_EXPERIMENTS_SRT16e4 §1 "실행" with the §5 arguments, verbatim -- run ONCE, after the §5 commit, GPUs hidden.
# Checkpoint = §3d ladder attempt 2 (gradient clipping 1.0; attempt 1 diverged), b* = kron K = 4096 (grid edge).
# Usage: tmux new -d -s srteval "bash code/run_srt_eval.sh"
cd /home/HTJ/t2/conf || exit 1
CUDA_VISIBLE_DEVICES= bash code/run_prior_eval.sh SRT SRTB16e4 d2sx_SRT_N160000_a1_fb2 kron 4096 208.1279194544014 \
  7c7354bef3bb1e40 918a424724fcb0ab "full:16,32,64,128,256,512 kron:16,32,64,128,256,512,1024,2048,4096"
