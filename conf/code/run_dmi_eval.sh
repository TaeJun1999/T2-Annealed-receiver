#!/bin/bash
# NEXT_EXPERIMENTS_ROOM16e4 §1 "실행" with the §5 arguments, verbatim -- run ONCE, after the §5 commit, GPUs hidden.
# The arguments are filled in by the §5 commit (checkpoint stem, b* family / kron K / ll_val, best / last sha, grid).
# Usage: tmux new -d -s dmieval "bash code/run_dmi_eval.sh"
cd /home/HTJ/t2/conf || exit 1
CUDA_VISIBLE_DEVICES= bash code/run_prior_eval.sh DMI DMIB16e4 d2sx_DMI_N160000_a1 gmm1024 - 112.04253042212595 \
  dc784649f1e9b890 20d28bf06e317ca5 "full:16,32,64,128,256,512,1024 kron:16,32,64,128,256,512,1024,2048"
