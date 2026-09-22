#!/bin/bash
# §6g seed robustness: repeat the §6d N=1e4 equal-budget C2 run with seeds a2 and a3.
# a1 stays the reported arm (selected by validation loss, never by BLER).  Pre-reg: 10_SPEC_stageC §6g.
cd /home/HTJ/t2/conf
P=~/miniforge3/envs/torch/bin/python
# wait for the §6f run to release the 192 cores
while pgrep -f "runner.py run --testbed D2 --cell C5 C1" > /dev/null; do sleep 60; done
for S in 2 3; do
  TAG=B1e4s$S
  $P code/runner.py run --testbed D2 --cell C2 --prior S2 --n 2560 --chunk 40 \
     --tag $TAG --ntrain 10000 \
     --stagec-ckpt /home/HTJ/t2/conf/ckpt/d2sx_N10000_a$S.pt 2>&1 | tee logs/run_D2_$TAG.log
  $P code/runner.py analysis --testbed D2 --tag $TAG 2>&1 | tee -a logs/run_D2_$TAG.log
done
echo "SEEDS_EXIT=$?"
