#!/bin/bash
# review_next: COPY (never move/overwrite) the C (S2v, ~/t2_wtC) and B' (S2d, ~/t2_wtB) worktree artefacts into main ~/t2/conf.
# Touches only ckpt/, results/, logs/ (never conf/code or Demo -> ROT16e4's cleanliness check is unaffected).  Re-runnable (cp -an).
# Verifies sha256 of every copied checkpoint / GMM fit / ALD file.  Log: ~/t2/conf/results/review_next/worktree_copy.log
M=~/t2/conf; LOG=$M/results/review_next/worktree_copy.log
log () { echo "[copy $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $*" | tee -a $LOG; }
copy () { local src=$1 dst=$2; [ -e "$src" ] || { log "skip (absent): $src"; return; }; mkdir -p "$(dirname "$dst")"; cp -an "$src" "$dst"; }
for W in ~/t2_wtC/conf ~/t2_wtB/conf; do
  log "from $W"
  for f in $W/ckpt/d2sx_S2vNR16_N160000_a1*.pt $W/ckpt/d2sx_S2d_N160000_a1*.pt; do copy $f $M/ckpt/$(basename $f); done
  for d in gmm_fits_D2_S2vB16e4 gmm_fits_D2_S2dB16e4 gmm_fits_D2_RMXS2d; do [ -d $W/results/$d ] && { mkdir -p $M/results/$d; cp -an $W/results/$d/. $M/results/$d/; }; done
  for f in $W/results/sigma_grid_D2_S2vNR16.* $W/results/sigma_grid_D2_S2d.* $W/results/d2_gbprime_S2vNR16* $W/results/d2_gbprime_S2d* $W/results/d2_gbprime_S2d.csv \
           $W/results/ald/*S2vALD* $W/results/ald/*RMX*; do copy $f $M/results/${f#$W/results/}; done
  for f in $W/logs/s2v*.log $W/logs/s2d*.log $W/logs/train_d2sx_S2vNR16*.log $W/logs/train_d2sx_S2d*.log $W/logs/ald_*S2vALD.log $W/logs/ald_*RMX*.log; do copy $f $M/logs/$(basename $f); done
done
# verify: every copied file in main hashes equal to its worktree source
bad=0; n=0
for W in ~/t2_wtC/conf ~/t2_wtB/conf; do
  for f in $W/ckpt/d2sx_S2vNR16_N160000_a1*.pt $W/ckpt/d2sx_S2d_N160000_a1*.pt $W/results/gmm_fits_D2_S2vB16e4/*.npz $W/results/gmm_fits_D2_S2dB16e4/*.npz \
           $W/results/ald/*S2vALD* $W/results/ald/*RMX* $W/results/d2_gbprime_S2vNR16* $W/results/d2_gbprime_S2d*; do
    [ -f "$f" ] || continue; n=$((n+1)); g=$M/${f#$W/}
    [ "$(sha256sum "$f" | cut -c1-16)" = "$(sha256sum "$g" | cut -c1-16)" ] || { log "SHA MISMATCH $g"; bad=$((bad+1)); }
  done
done
log "verified $n files, mismatches $bad; links in results/gmm_fits_D2_RMXS2d resolve: $(ls $M/results/gmm_fits_D2_RMXS2d 2>/dev/null | wc -l) links, broken $(find $M/results/gmm_fits_D2_RMXS2d -xtype l 2>/dev/null | wc -l)"
log "WORKTREE_COPY_DONE bad=$bad"
