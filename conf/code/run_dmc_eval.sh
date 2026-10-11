#!/bin/bash
# NEXT_EXPERIMENTS_DMC16e4 §1 "실행" with the §5 arguments, verbatim -- run ONCE, after the §5 commit, GPUs hidden.
# Usage: tmux new -d -s dmceval "bash code/run_dmc_eval.sh"
cd /home/HTJ/t2/conf || exit 1
CUDA_VISIBLE_DEVICES= bash code/run_prior_eval.sh DMC DMCB16e4 d2sx_DMC_N160000_a1 kron 4096 122.37953759128766 \
  65b26ddd4f6437f4 92dc9f53c31af875 "full:16,32,64,128,256,512 kron:16,32,64,128,256,512,1024,2048,4096"
