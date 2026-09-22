#!/bin/bash
# Provisional §6l refit at N=4e4 with K=1024 in the grid (K=2048 still fitting; if it wins, the waiter
# produces B4e4k and this table is superseded).  Uses the idle CPU now instead of waiting.
cd /home/HTJ/t2/conf; P=~/miniforge3/envs/torch/bin/python
echo "[B4e4k1 $(TZ=Asia/Seoul date '+%H:%M') start]" >> logs/queue.log
$P code/runner.py run --testbed D2 --cell C2 --prior S2 --n 2560 --chunk 40 --tag B4e4k1 --ntrain 40000 \
   --stagec-ckpt /home/HTJ/t2/conf/ckpt/d2sx_N40000_a1.pt >> logs/run_D2_B4e4k1.log 2>&1
$P code/runner.py analysis --testbed D2 --tag B4e4k1 >> logs/run_D2_B4e4k1.log 2>&1
$P code/guard_report.py --raw /home/HTJ/t2/conf/raw_B4e4k1 --testbed D2 > results/guard_D2_B4e4k1.txt 2>&1
echo "[B4e4k1 $(TZ=Asia/Seoul date '+%H:%M') done: $(grep -m1 -oE 'GMM b\* +: [^,]*' results/tables_D2_B4e4k1.txt)]" >> logs/queue.log
