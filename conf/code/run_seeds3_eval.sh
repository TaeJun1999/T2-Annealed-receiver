#!/bin/bash
# NEXT_EXPERIMENTS_SEEDS3_16e4 §1 (frozen 73a93547, §5 dbe0bdb3): the six seed-repeat tags on the TEST set, one at a time, with the
# SEEDS16e4 per-tag pipeline code/run_seeds16e4.sh.  All tags with GPUs hidden (MIX3 must; the others do not need a GPU).
# Log logs/run_seeds3_eval.log, end "SEEDS3_EVAL_DONE ok=<n> fail=<n>".  A failed tag is not re-run here (user approval).
cd /home/HTJ/t2/conf; L=logs/run_seeds3_eval.log; export CUDA_VISIBLE_DEVICES=
log () { echo "[seeds3 $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $*" | tee -a $L; }
REG=results/review_next/NEXT_EXPERIMENTS_SEEDS3_16e4.md
[ -n "$(git -C /home/HTJ/t2 status --porcelain conf/code Demo)" ] && { log "ABORT: conf/code or Demo dirty"; exit 1; }
[ -n "$(git ls-files $REG)" ] && [ -z "$(git status --porcelain $REG)" ] || { log "ABORT: registration not tracked+clean"; exit 1; }
G1="full:16,32,64,128,256,512 kron:16,32,64,128,256,512,1024,2048,4096"; G2="full:16,32,64,128,256,512 kron:16,32,64,128,256,512,1024,2048"
log "start (git $(git rev-parse --short HEAD))"; OK=0; FAIL=0
run () { bash code/run_seeds16e4.sh "$@" < /dev/null; local rc=$?
  log "$2 rc=$rc ($(grep -h 'acceptance rc' logs/run_seeds16e4_$2.log 2>/dev/null | tail -1 | cut -c1-100))"
  grep -q SEEDS_EVAL_DONE logs/run_seeds16e4_$2.log 2>/dev/null && [ $rc -eq 0 ] && OK=$((OK+1)) || FAIL=$((FAIL+1)); }
run S2c  D3B16e4s2 ckpt/d2sx_S2c_N160000_a2_best.pt  raw_D3B16e4 kron   4096 0.08879931165293979 4e9a6ca2c3197004 best "$G1"
run S2c  D3B16e4s3 ckpt/d2sx_S2c_N160000_a3_best.pt  raw_D3B16e4 kron   4096 0.08879931165293979 3e4e36945a9314c3 best "$G1"
run SV8e SVB16e4s2 ckpt/d2sx_SV8e_N160000_a2_best.pt raw_SVB16e4 gmm256 2048 -47.80545576704972  b05d92632e611494 best "$G2"
run SV8e SVB16e4s3 ckpt/d2sx_SV8e_N160000_a3_best.pt raw_SVB16e4 gmm256 2048 -47.80545576704972  5e1ff49f455f110a best "$G2"
run MIX3 MXB16e4s2 ckpt/d2sx_MIX3_N160000_a2_best.pt raw_MXB16e4 kron   4096 33.7604873920761    d7a6b1a199c51637 best "$G1"
run MIX3 MXB16e4s3 ckpt/d2sx_MIX3_N160000_a3_best.pt raw_MXB16e4 kron   4096 33.7604873920761    128b8090036332bc best "$G1"
log "SEEDS3_EVAL_DONE ok=$OK fail=$FAIL"
