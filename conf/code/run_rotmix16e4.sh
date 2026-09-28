#!/bin/bash
# (NEXT_EXPERIMENTS_ROTMIX16e4 §1, after the design freeze 389e23f4 + §5 + prerequisite code + merge into main)
# B': drift-TRAINED priors (S2d: S2 + per-block receive rotation U[0,30 deg]) on S2 channels at fixed rotation 0/15/30 deg -- the
# SAME trials as raw_B16e4k / raw_ROTaB16e4k / raw_ROTbB16e4k.  Per angle d, 5 tags (registration §1 태그):
#   RMX<d>     14 arms, S2d _best, b* kron 4096        RMX<d>PIL  --pilot-arms (V1-pilot bstar-pilot R5-genie)
#   RMX<d>ALD  ALD-pilot ALDv-pilot R5-genie           RMX<d>last V1 last-EMA + genie      RMX<d>k1  b* kron 1024 + genie
# Phase 0 (per angle): fits link dirs (S2d fits under S2 names; k1 = 13 links up to kron 1024) + readlink check (수용 (a));
#   ALD test pilots (CPU) -> ALD estimate (GPU, a free GPU per angle; ald.py guards: --train-prior S2d, rotation).
# Phase 1 (per angle, CPU, GPUs hidden): the 5 runs -> run_manifest; analysis on RMX<d> only; eval_accept (grid on the S2d
#   source dir, ckpt ids, genie replay vs the angle's ref raw) -> pair_rotmix (DT, DD, fingerprints) + pair_baselines (판정 1/3)
#   ONLY if eval_accept passed.  All 15 tags are run and reported; arguments name a subset of angles only to RESUME.
# Log logs/run_rotmix16e4.log, end marker "ROTMIX_EVAL_DONE ok=<n> fail=<n>" (n counts angles: 3 = all pairs written).
cd /home/HTJ/t2/conf
P=~/miniforge3/envs/torch/bin/python
L=logs/run_rotmix16e4.log
log () { echo "[rotmix $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $*" | tee -a $L >> logs/queue.log; }
[ -n "$(git -C /home/HTJ/t2 status --porcelain conf/code Demo)" ] && { log "ABORT: conf/code or Demo dirty"; exit 1; }
BEST=ckpt/d2sx_S2d_N160000_a1_best.pt; LAST=ckpt/d2sx_S2d_N160000_a1.pt; BSHA=ceec0222e0912a1c; LSHA=98bc88f7333f19ee
LL4096=-5.574511189627533; LL1024=-8.988496590420036; SRC=gmm_fits_D2_S2dB16e4
[ "$(sha256sum $BEST | cut -c1-16)" = $BSHA ] && [ "$(sha256sum $LAST | cut -c1-16)" = $LSHA ] || { log "ABORT: S2d ckpt sha differs from §5"; exit 1; }
GRID="full:16,32,64,128,256,512 kron:16,32,64,128,256,512,1024,2048,4096"
COMMON="--testbed D2 --prior S2 --cell C2 --train-prior S2d --n 2560 --chunk 40 --ntrain 160000"
ref () { case $1 in 0) echo raw_B16e4k;; 15) echo raw_ROTaB16e4k;; 30) echo raw_ROTbB16e4k;; esac; }
DEGS="${*:-0 15 30}"
log "start (git $(git rev-parse --short HEAD)) angles: $DEGS"
mklinks () {   # $1 dir  $2 max kron K
  local D=results/gmm_fits_D2_$1 f b K; mkdir -p $D
  for f in results/$SRC/fit_S2d_Nr8_*K*_n160000.npz; do
    b=$(basename $f); K=$(echo $b | sed -E 's/.*K([0-9]+)_n.*/\1/')
    case $b in *kron*) [ $K -gt $2 ] && continue;; esac
    ln -sfn ../$SRC/$b $D/${b/fit_S2d_/fit_S2_}
  done
  local n=0 badl=0
  for f in $D/fit_S2_Nr8_*K*_n160000.npz; do n=$((n+1)); r=$(readlink -e $f) && case $(basename $r) in fit_S2d_Nr8_*) ;; *) badl=1;; esac || badl=1; done
  [ $badl -eq 0 ] && [ $n -eq $3 ] && [ -z "$(ls $D | grep k0r)" ]
}
# ---- phase 0: links + ALD estimates
FREE=($(nvidia-smi --query-gpu=index,memory.used --format=csv,noheader,nounits | awk -F', ' '$2 < 100 {print $1}')); i=0
for d in $DEGS; do
  for t in RMX$d RMX${d}PIL RMX${d}ALD RMX${d}last; do mklinks $t 4096 15 || { log "d=$d ABORT: link dir $t (수용 (a))"; exit 1; }; done
  mklinks RMX${d}k1 1024 13 || { log "d=$d ABORT: link dir RMX${d}k1 (수용 (a))"; exit 1; }
  ET=RMX${d}ALD
  [ -f results/ald/pilots_${ET}_test.npz ] || CUDA_VISIBLE_DEVICES= $P code/ald.py regen --tag $ET --prior S2 --cell C2 --fits-tag RMXS2d \
    --train-prior S2d --rotation $d --set test >> $L 2>&1 || { log "d=$d ABORT: ALD test regen"; exit 1; }
  E=results/ald/ald_$ET.npz
  if [ ! -f $E ] || [ results/ald/tune_$ET.json -nt $E ]; then
    [ $i -lt ${#FREE[@]} ] || { log "d=$d ABORT: no free GPU for the ALD estimate (resume later, no approval needed)"; exit 1; }
    CUDA_VISIBLE_DEVICES=${FREE[$i]} $P code/ald.py estimate --tag $ET --ckpt $BEST --train-prior S2d --set test >> $L 2>&1 &
    i=$((i+1))
  fi
done; wait
log "phase 0 done: links + ALD estimates $(ls results/ald/ald_RMX*ALD.npz 2>/dev/null | wc -l)/3"
# ---- phase 1: runs (CPU, GPUs hidden)
export CUDA_VISIBLE_DEVICES=
OK=0; FAIL=0
for d in $DEGS; do
  R=$(ref $d); [ -d $R ] || { log "d=$d ABORT: ref raw $R missing"; FAIL=$((FAIL+1)); continue; }
  [ -f results/ald/ald_RMX${d}ALD.npz ] || { log "d=$d ABORT: no ALD estimate"; FAIL=$((FAIL+1)); continue; }
  run () { $P code/runner.py run $COMMON --rotation $d --tag $1 "${@:2}" > logs/run_D2_$1.log 2>&1 \
             && $P code/run_manifest.py --tag $1 >> $L 2>&1; local rc=$?; log "d=$d $1 run+manifest rc=$rc"; return $rc; }
  run RMX$d --stagec-ckpt /home/HTJ/t2/conf/$BEST || { log "d=$d ABORT: RMX$d failed -- the angle's other tags not started"; FAIL=$((FAIL+1)); continue; }
  $P code/runner.py analysis --testbed D2 --tag RMX$d > logs/analysis_RMX$d.log 2>&1; log "d=$d analysis rc=$?"
  run RMX${d}PIL --stagec-ckpt /home/HTJ/t2/conf/$BEST --pilot-arms --arm V1-pilot bstar-pilot R5-genie
  run RMX${d}ALD --stagec-ckpt /home/HTJ/t2/conf/$BEST --ald-file /home/HTJ/t2/conf/results/ald/ald_RMX${d}ALD.npz --arm ALD-pilot ALDv-pilot R5-genie
  run RMX${d}last --stagec-ckpt /home/HTJ/t2/conf/$LAST --arm M-ours-dscore-C-V1 R5-genie
  run RMX${d}k1 --stagec-ckpt /home/HTJ/t2/conf/$BEST --arm M-ours-bstar R5-genie
  A=results/review_next/RMX${d}_accept.txt
  $P code/eval_accept.py --prior S2d --ntrain 160000 --bstar kron --kron-K 4096 --ll-val $LL4096 --ref-raw $R \
    --tag RMX$d:best:$BSHA:C2 --tag RMX${d}PIL:best:$BSHA:C2 --tag RMX${d}ALD:best:$BSHA:C2 --tag RMX${d}last:last:$LSHA:C2 \
    --fits-dir results/$SRC --grid "$GRID" > $A 2>&1; RC1=$?
  $P code/eval_accept.py --prior S2 --ntrain 160000 --bstar kron --kron-K 1024 --ll-val $LL1024 --ref-raw $R \
    --tag RMX${d}k1:best:$BSHA:C2 >> $A 2>&1; RC2=$?
  log "d=$d acceptance rc=$RC1/$RC2 ($(grep ACCEPT $A | tr '\n' ' ' | cut -c1-160))"
  [ $RC1 -ne 0 ] || [ $RC2 -ne 0 ] && { log "d=$d INVALID: acceptance failed, no pair scripts"; FAIL=$((FAIL+1)); continue; }
  $P code/pair_rotmix.py --deg $d --ref $R --rmx raw_RMX$d --last raw_RMX${d}last --k1 raw_RMX${d}k1 > results/review_next/pair_RMX$d.txt 2>&1
  RC1=$?; log "d=$d pair_rotmix rc=$RC1 ($(head -1 results/review_next/pair_RMX$d.txt | cut -c1-150))"
  $P code/pair_baselines.py --base raw_RMX$d --pil raw_RMX${d}PIL --ald raw_RMX${d}ALD --est RMX${d}ALD --cell C2 --prior S2 --ref $R \
    > results/review_next/pairB_RMX$d.txt 2>&1
  RC2=$?; log "d=$d pair_baselines rc=$RC2 ($(head -1 results/review_next/pairB_RMX$d.txt | cut -c1-150))"
  [ $RC1 -eq 0 ] && [ $RC2 -eq 0 ] && OK=$((OK+1)) || { log "d=$d INVALID: integrity failed"; FAIL=$((FAIL+1)); }
done
log "ROTMIX_EVAL_DONE ok=$OK fail=$FAIL"
exit $FAIL
