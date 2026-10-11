#!/bin/bash
# NEXT_EXPERIMENTS_ROOM16e4 §1 "실행" with the §5 arguments, verbatim -- run ONCE, after the §5 commit, GPUs hidden.
# Checkpoint = attempt 1 (patience stop at epoch 1680), b* = FULL-family K = 1024 (full 512 was the grid edge; the registered
# rule added full 1024 once).
# Usage: tmux new -d -s srbeval "bash code/run_srb_eval.sh"
cd /home/HTJ/t2/conf || exit 1
CUDA_VISIBLE_DEVICES= bash code/run_prior_eval.sh SRB SRBB16e4 d2sx_SRB_N160000_a1 gmm1024 - 97.00871495382869 \
  ed437f21af15c305 b5f74923f2bd2920 "full:16,32,64,128,256,512,1024 kron:16,32,64,128,256,512,1024,2048"
