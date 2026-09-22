#!/bin/bash
# CPU priority queue.  ORDER MATTERS: B16e4 is the ONLY table that is both gate-passing AND
# equal-budget, so it runs before the seed-robustness repeats (which harden a claim that
# already has two budgets).  One 192-worker pool at a time -- the box cannot hold two.
cd /home/HTJ/t2/conf
P=~/miniforge3/envs/torch/bin/python
log () { echo "[queue $(TZ=Asia/Seoul date '+%H:%M')] $*" >> logs/queue.log; }

while pgrep -f "runner.py run --testbed D2 --cell C5 C1" > /dev/null; do sleep 60; done
log "B1e4x done"
$P code/guard_report.py --raw /home/HTJ/t2/conf/raw_B1e4x --testbed D2 > results/guard_D2_B1e4x.txt 2>&1

# --- 1. B16e4: equal budget N=1.6e5 with the GATE-PASSING checkpoint.  Blocked on the Nr=8 fit set.
until ./code/check_fits_n16e4.sh > /dev/null 2>&1; do sleep 120; done
log "Nr=8 fit set complete -> B16e4 C2"
$P code/runner.py run --testbed D2 --cell C2 --prior S2 --n 2560 --chunk 40 \
   --tag B16e4 --ntrain 160000 \
   --stagec-ckpt /home/HTJ/t2/conf/ckpt/d2sx_N160000_a1.pt >> logs/run_D2_B16e4.log 2>&1
$P code/runner.py analysis --testbed D2 --tag B16e4 >> logs/run_D2_B16e4.log 2>&1
$P code/guard_report.py --raw /home/HTJ/t2/conf/raw_B16e4 --testbed D2 > results/guard_D2_B16e4.txt 2>&1
log "B16e4 C2 done"

# --- 2. B16e4 cell generalisation (6f at the gate-passing budget)
$P code/runner.py run --testbed D2 --cell C5 C1 --prior S2 --n 2560 --chunk 40 \
   --tag B16e4 --ntrain 160000 \
   --stagec-ckpt /home/HTJ/t2/conf/ckpt/d2sx_N160000_a1.pt >> logs/run_D2_B16e4.log 2>&1
$P code/runner.py analysis --testbed D2 --tag B16e4 >> logs/run_D2_B16e4.log 2>&1
$P code/guard_report.py --raw /home/HTJ/t2/conf/raw_B16e4 --testbed D2 > results/guard_D2_B16e4.txt 2>&1
log "B16e4 C5+C1 done"

# --- 3. 6g seed robustness (a2, a3) at N=1e4
for S in 2 3; do
  TAG=B1e4s$S
  $P code/runner.py run --testbed D2 --cell C2 --prior S2 --n 2560 --chunk 40 \
     --tag $TAG --ntrain 10000 \
     --stagec-ckpt /home/HTJ/t2/conf/ckpt/d2sx_N10000_a$S.pt >> logs/run_D2_$TAG.log 2>&1
  $P code/runner.py analysis --testbed D2 --tag $TAG >> logs/run_D2_$TAG.log 2>&1
  $P code/guard_report.py --raw /home/HTJ/t2/conf/raw_$TAG --testbed D2 > results/guard_D2_$TAG.txt 2>&1
  log "seed a$S done"
done
log "QUEUE_DONE"
