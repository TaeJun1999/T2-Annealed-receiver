#!/bin/bash
# Pre-registered settling experiment (results/diag/SUMMARY.md §gap): the interventional
# counterfactuals at ALL SEVEN SNRs of cell C2, so the non-monotonic BLER(SNR) shape can be
# tested against  BLER = p_blow*BLER|blow + (1-p_blow)*BLER|clean  with p_blow predicted from
# the realised-nu indefiniteness alone.  Nothing is retuned; only --snrs changes.
cd /home/HTJ/t2/conf
CK=ckpt/d2sx_N10000_a1.pt
for S in -3 0 3 6 9 12 15; do
  nice -n 10 env OMP_NUM_THREADS=1 ~/miniforge3/envs/torch/bin/python code/diag_psd_cf.py \
      --cell C2 --snrs $S --n 256 --ckpt $CK > logs/psd_cf_snr${S}.log 2>&1
  echo "EXIT_snr${S}=$?" >> logs/psd_cf.log
done
echo DONE >> logs/psd_cf.log
