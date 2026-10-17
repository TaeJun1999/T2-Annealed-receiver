#!/bin/bash
# U28NR32GCAP probe (step 1 state re-evaluation + step 3 K8192 timing); GPU 0, its NUMA hyperthread pair
cd ~/t2/conf
CUDA_VISIBLE_DEVICES=0 taskset -c 0,96 ~/miniforge3/envs/torch/bin/python results/review_next/gcap/probe_gcap.py \
  ~/t2_wtS/conf/results/gmm_fits_D2_U28NR32B16e4/fit_UMi28_Nr32_kronK4096_n160000.npz > logs/gcap_probe.log 2>&1
echo "exit $? $(TZ=America/Chicago date)" >> logs/gcap_probe.log
