#!/bin/bash
# NEXT_EXPERIMENTS_E5QAM16 §1.3 (D2): V1 query-noise coverage on development trials 5440..5479 at the chosen grid, 16-QAM and QPSK
# (same trial NUMBERS, different realisations).  nu_q only, no BLER.  One CPU each (118, 119 -- freed NUMA 0 slots).
cd /home/HTJ/t2_wtE5/conf; P=~/miniforge3/envs/torch/bin/python; export CUDA_VISIBLE_DEVICES=
G="3 6 9 12 15 18 21"; CK=/home/HTJ/t2/conf/ckpt/d2sx_N160000_a1.pt
for m in 16qam:118 qpsk:119; do
  mod=${m%:*}; cpu=${m#*:}
  taskset -c $cpu $P code/diag_sigma_coverage.py --mod $mod --cell C2 --prior S2 --tag D2QAM16g --ntrain 160000 --stagec-ckpt $CK \
    --snr $G --skip0 5440 --n 40 --out results/review_next/qam16/coverage_D2QAM16_$mod.npz > logs/nuq_D2QAM16_$mod.log 2>&1 &
done
wait; echo "NUQ_D2_DONE $(TZ=America/Chicago date '+%m-%d %H:%M %Z')" >> logs/e5_grid.log
