#!/bin/bash
# NEXT_EXPERIMENTS_PATH16e4 §1 "실행" with the §5 arguments, verbatim -- run ONCE, after the §5 commit, GPUs hidden.
# Checkpoint = attempt 1 (patience stop, no divergence), b* = kron K = 4096 (grid edge).
# Usage: tmux new -d -s srpeval "bash code/run_srp_eval.sh"
cd /home/HTJ/t2/conf || exit 1
CUDA_VISIBLE_DEVICES= bash code/run_prior_eval.sh SRP SRPB16e4 d2sx_SRP_N160000_a1 kron 4096 244.1932863626755 \
  ac4699c78b3e2d80 f82762a7002308db "full:16,32,64,128,256,512 kron:16,32,64,128,256,512,1024,2048,4096"
