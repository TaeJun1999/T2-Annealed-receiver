#!/bin/bash
# NEXT_EXPERIMENTS_PATH16e4 §1 "실행" with the §5 arguments, verbatim -- run ONCE, after the §5 commit, GPUs hidden.
# The arguments are filled in by the §5 commit (checkpoint stem, b* family / kron K / ll_val, best / last sha, grid).
# Usage: tmux new -d -s srpeval "bash code/run_srp_eval.sh"
cd /home/HTJ/t2/conf || exit 1
echo "run_srp_eval.sh: the §5 arguments are not filled in yet"; exit 1
