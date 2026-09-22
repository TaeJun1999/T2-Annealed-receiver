#!/bin/bash
# §6f cell generalisation at equal budget N=1e4 (C5 Tp=3, C1 Tp=2).
# Same run as §6d's B1e4 with --cell changed.  Pre-registered in 10_SPEC_stageC.md §6f (commit 8880d33).
cd /home/HTJ/t2/conf
P=~/miniforge3/envs/torch/bin/python
$P code/runner.py run --testbed D2 --cell C5 C1 --prior S2 --n 2560 --chunk 40 \
   --tag B1e4x --ntrain 10000 \
   --stagec-ckpt /home/HTJ/t2/conf/ckpt/d2sx_N10000_a1.pt 2>&1 | tee logs/run_D2_B1e4x.log
$P code/runner.py analysis --testbed D2 --tag B1e4x 2>&1 | tee -a logs/run_D2_B1e4x.log
echo "EXIT=$?"
