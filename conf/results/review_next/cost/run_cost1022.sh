#!/bin/bash
# E4 COST1022 measurement (PROMPT_SERVER_COST.md; user 10-19 CDT: keep the GPU dummies + --force, start now). CPU only, one core.
cd /home/HTJ/t2 || exit 1
export CUDA_VISIBLE_DEVICES=
P=/home/HTJ/miniforge3/envs/torch/bin/python
L=conf/logs/cost/measure_COST1022.log
stamp () { TZ=America/Chicago date '+%m-%d %H:%M:%S %Z'; }
echo "[cost1022 $(stamp) git $(git rev-parse --short HEAD) bench $(sha256sum conf/code/bench_cost.py | cut -c1-16) lock $(lock id /home/HTJ/t2/conf/code/bench_cost.py)] start" >> $L
for cell in D2 U32; do
  extra=; [ $cell = D2 ] && extra=--ms-arm
  taskset -c 24 $P -B conf/code/bench_cost.py --cell $cell --tag COST1022_$cell $extra --force >> $L 2>&1
  echo "[cost1022 $(stamp)] $cell rc=$?" >> $L
done
echo "COST1022_DONE $(stamp)" >> $L
