#!/bin/bash
# CPU pipeline, revision 2.  The box went idle (load 113) waiting for the N=1.6e5 GMM fits, so the
# 6g seed run -- which needs only the N=1e4 fits that already exist -- is pulled forward into that
# window.  B16e4 (the only table that is both gate-passing AND equal-budget) still runs the moment
# the Nr=8 fit set is complete and the box is free.
cd /home/HTJ/t2/conf
P=~/miniforge3/envs/torch/bin/python
log () { echo "[queue2 $(TZ=Asia/Seoul date '+%H:%M')] $*" >> logs/queue.log; }

seed_run () {   # $1 = seed index
  TAG=B1e4s$1
  $P code/runner.py run --testbed D2 --cell C2 --prior S2 --n 2560 --chunk 40 \
     --tag $TAG --ntrain 10000 \
     --stagec-ckpt /home/HTJ/t2/conf/ckpt/d2sx_N10000_a$1.pt >> logs/run_D2_$TAG.log 2>&1
  $P code/runner.py analysis --testbed D2 --tag $TAG >> logs/run_D2_$TAG.log 2>&1
  $P code/guard_report.py --raw /home/HTJ/t2/conf/raw_$TAG --testbed D2 > results/guard_D2_$TAG.txt 2>&1
  log "seed a$1 done"
}

b16_run () {    # $@ = cells
  $P code/runner.py run --testbed D2 --cell "$@" --prior S2 --n 2560 --chunk 40 \
     --tag B16e4 --ntrain 160000 \
     --stagec-ckpt /home/HTJ/t2/conf/ckpt/d2sx_N160000_a1.pt >> logs/run_D2_B16e4.log 2>&1
  $P code/runner.py analysis --testbed D2 --tag B16e4 >> logs/run_D2_B16e4.log 2>&1
  $P code/guard_report.py --raw /home/HTJ/t2/conf/raw_B16e4 --testbed D2 > results/guard_D2_B16e4.txt 2>&1
  log "B16e4 $* done"
}

log "queue2 start -- seed a2 pulled into the fit-wait window"
seed_run 2

until ./code/check_fits_n16e4.sh > /dev/null 2>&1; do sleep 120; done
log "Nr=8 fit set complete -> B16e4"
b16_run C2                 # the headline point first
b16_run C5 C1              # 6f at the gate-passing budget

seed_run 3
log "QUEUE2_DONE"
