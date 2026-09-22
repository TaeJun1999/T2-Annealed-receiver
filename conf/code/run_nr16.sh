#!/bin/bash
# (10_SPEC_stageC §7) The whole C6 (Nr=16) pipeline, unattended.
#   1. wait for the 12 GMM fits  (code/fit_nr16.sh, GPUs 0-5)
#   2. measure the sigma grid for THIS array, tagged NR16 -- the frozen D2 grid is a different ruler
#      and is never touched (04_SPEC §3; sigma.load now takes a tag)
#   3. train the score at Nr=16 with the FROZEN recipe, reading the NR16 grid
#   4. BLER on C6, equal budget N=1e4, n=2560, same arms as §6d
# Every step appends to logs/queue.log so the 30-minute briefing can read one file.
cd /home/HTJ/t2/conf
P=~/miniforge3/envs/torch/bin/python
log () { echo "[nr16 $(TZ=Asia/Seoul date '+%H:%M')] $*" >> logs/queue.log; }

until grep -q "ALL 12 CONFIGS DONE" logs/fit_D2_nr16.log 2>/dev/null; do sleep 120; done
n=$(ls results/gmm_fits_D2_NR16/*.npz 2>/dev/null | wc -l)
log "GMM fits done: $n/12 files"
[ "$n" -eq 12 ] || { log "ABORT: expected 12 fit files, found $n -- b* would be chosen from a subset"; exit 1; }

log "step 2/4: sigma grid (tag NR16)"
$P code/runner.py sigma --testbed D2 --cell C6 --tag NR16 >> logs/sigma_NR16.log 2>&1
log "sigma grid: $(grep -o 'sigma_t in \[[^]]*\]' logs/sigma_NR16.log | tail -1)"

log "step 3/4: score training, Nr=16, N=1e4, frozen recipe"
CUDA_VISIBLE_DEVICES=0 $P code/train_nr16.py --ntrain 10000 --attempt 1 >> logs/train_nr16.log 2>&1 \
  || { log "ABORT: train_nr16.py failed (see logs/train_nr16.log) -- BLER not started"; exit 1; }
log "training: $(grep -oE 'stopped_by=[a-z_]+|best [0-9.e+-]+ @[0-9]+' logs/train_nr16.log | tail -2 | tr '\n' ' ')"

log "step 4/4: BLER C6, n=2560, equal budget N=1e4"
ln -sfn gmm_fits_D2_NR16 results/gmm_fits_D2_NR16run
$P code/runner.py run --testbed D2 --cell C6 --prior S2 --n 2560 --chunk 40 --tag NR16run --ntrain 10000 \
   --stagec-ckpt /home/HTJ/t2/conf/ckpt/d2sx_NR16_N10000_a1.pt >> logs/run_D2_NR16.log 2>&1
$P code/runner.py analysis --testbed D2 --tag NR16run >> logs/run_D2_NR16.log 2>&1
$P code/guard_report.py --raw /home/HTJ/t2/conf/raw_NR16run --testbed D2 > results/guard_D2_NR16run.txt 2>&1
log "NR16_PIPELINE_DONE"
