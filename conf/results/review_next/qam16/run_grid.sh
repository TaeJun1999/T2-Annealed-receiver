#!/bin/bash
# NEXT_EXPERIMENTS_E5QAM16 §1.2 -- development runs of b* only (16-QAM) for the SNR grid of one cell: trials 5120..5439 (n 320,
# chunks of 10), SNRs given (G0 = 3 6 9 12 15 18 21, or the one shift point 0 / 24).  CPU only, on the CPU list given.
#   bash results/review_next/qam16/run_grid.sh U28|D2 <cpu-list> <snr> [<snr> ...]
# Log logs/e5_grid.log; end line "E5GRID_DONE <cell> rc=<rc>".
cd /home/HTJ/t2_wtE5/conf || exit 1
P=~/miniforge3/envs/torch/bin/python; export CUDA_VISIBLE_DEVICES=
L=logs/e5_grid.log
log () { echo "[e5grid $(TZ=America/Chicago date '+%m-%d %H:%M %Z') git $(git rev-parse --short HEAD)] $*" | tee -a $L; }
[ -z "$(git status --porcelain code ../Demo)" ] || { log "ABORT: code/ or Demo/ not clean"; exit 1; }
CELL=${1:-}
case "$CELL" in      # §1.1: b* file and R2's fullK32 (Chat), full sha256
  U28) PR=UMi28; T=U28QAM16g; SRC=/home/HTJ/t2/conf/results/gmm_fits_D2_U28B16e4
       SHA="74d22f332726203f512ddfb4289d59ad10bb3f4f67c9ef7cb275821a32aa01f8 fit_UMi28_Nr8_kronK4096_n160000.npz
c0261395e7238650a447cbbcc5a061c4161bd9fb23f118600dcd3541938f3194 fit_UMi28_Nr8_fullK32_n160000.npz" ;;
  D2)  PR=S2;    T=D2QAM16g;  SRC=/home/HTJ/t2/conf/results/gmm_fits_D2_B16e4k
       SHA="bf796b84037e1b3790ed5a6d7917ea2a79f2bee4a9f155f0d3385d856c950997 fit_S2_Nr8_kronK1024_n160000.npz
d4601650a888b4b355565a9010cf0a23499a3e92505e657e2cd79a1c152359f3 fit_S2_Nr8_fullK32_n160000.npz" ;;
  *) echo "usage: run_grid.sh U28|D2 <cpu-list> <snr> ..."; exit 1 ;;
esac
CPUS=$2; shift 2; SNRS="$*"
for s in $SNRS; do case " 0 3 6 9 12 15 18 21 24 " in *" $s "*) ;; *) echo "SNR $s not in G0 or a shift point"; exit 1 ;; esac; done
F=results/gmm_fits_D2_$T
if [ ! -d $F ]; then mkdir -p $F && cp -L $SRC/*.npz $F/; fi        # byte copies of the original fits folder (no links)
[ -z "$(find $F -type l)" ] && [ "$(ls $F/*.npz | wc -l)" = "$(ls $SRC/*.npz | wc -l)" ] || { log "ABORT: fits folder $F"; exit 1; }
for f in $SRC/*.npz; do cmp -s $f $F/$(basename $f) || { log "ABORT: $F/$(basename $f) differs from $SRC"; exit 1; }; done
(cd $F && echo "$SHA" | sha256sum -c --quiet) || { log "ABORT: sha256 of the b* / fullK32 copy in $F != §1.1"; exit 1; }
[ -d raw_$T ] && log "resume $T ($(ls raw_$T | wc -l) chunks present)"
log "start $T prior $PR SNR $SNRS on CPUs $CPUS"
taskset -c $CPUS $P code/runner.py run --testbed D2 --prior $PR --cell C2 --ntrain 160000 --mod 16qam --chunk 10 --n 320 \
  --skip0 5120 --snr $SNRS --arm M-ours-bstar --tag $T >> logs/run_D2_$T.log 2>&1
rc=$?; log "E5GRID_DONE $CELL rc=$rc"; exit $rc
