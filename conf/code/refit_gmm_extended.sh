#!/bin/bash
# (10_SPEC_stageC §6l) Re-run the equal-budget C2 table at one budget with the GMM grid EXTENDED
# (K=1024, and K=2048 where it was fitted), so b* is chosen from the full grid.  Only the GMM arms can
# change; the learned arms use the same checkpoint as before.  Selection is validation log-likelihood
# only.  Usage:  refit_gmm_extended.sh <ntrain> <base_fits_dir> <out_tag> <trigger_regex> <ckpt>
#   e.g.  refit_gmm_extended.sh 40000  gmm_fits_D2_n4e4  B4e4k  'N=40000 K=2048 MERGE EXIT|K512_STAYS' ckpt/d2sx_N40000_a1.pt
cd /home/HTJ/t2/conf
NT=$1; BASE=$2; TAG=$3; TRIG=$4; CKPT=$5
P=~/miniforge3/envs/torch/bin/python; L=logs/fit_k1024.log
log () { echo "[refit-$TAG $(TZ=Asia/Seoul date '+%H:%M')] $*" >> logs/queue.log; }

until grep -qE "$TRIG" $L 2>/dev/null; do sleep 120; done
log "trigger seen ($TRIG)"
D=results/gmm_fits_D2_$TAG; mkdir -p $D
for f in results/$BASE/fit_S2_Nr*_n${NT}.npz; do ln -sf "../$BASE/$(basename $f)" "$D/$(basename $f)"; done
for K in 1024 2048; do
  src=results/gmm_fits_D2_K${K}n${NT}/fit_S2_Nr8_kronK${K}_n${NT}.npz
  [ -f "$src" ] && ln -sf "../gmm_fits_D2_K${K}n${NT}/$(basename $src)" "$D/$(basename $src)" && log "linked K=$K"
done
log "grid in $D: $(ls $D | grep -c npz) files"
while pgrep -f "runner.py run --testbed D2" > /dev/null; do sleep 60; done
$P code/runner.py run --testbed D2 --cell C2 --prior S2 --n 2560 --chunk 40 --tag $TAG --ntrain $NT \
   --stagec-ckpt /home/HTJ/t2/conf/$CKPT >> logs/run_D2_$TAG.log 2>&1
$P code/runner.py analysis --testbed D2 --tag $TAG >> logs/run_D2_$TAG.log 2>&1
$P code/guard_report.py --raw /home/HTJ/t2/conf/raw_$TAG --testbed D2 > results/guard_D2_$TAG.txt 2>&1
log "$TAG done: b* = $(grep -m1 -oE 'b\* +: [a-z]+ \([^)]*\)' results/tables_D2_$TAG.txt)"
