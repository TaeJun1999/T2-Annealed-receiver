#!/bin/bash
# (10_SPEC_stageC §6l) b* sits at the K grid EDGE: gmm_fit_D2.txt:66 reads "b* = kron K=512" and the
# kron likelihood is still climbing (K=128 -26.116 -> K=256 -23.936 -> K=512 -23.473).  01_RULES:76
# forbids weakening the GMM arm, so the grid must be extended until b* is interior.
#
# Output goes to results/gmm_fits_D2_K1024/, which is the pre-registered N=1e4 set (symlinked,
# unchanged) PLUS the new K=1024 file.  The pre-registered directory itself is never written to.
# Selection stays validation-log-likelihood only; BLER is never consulted.
cd /home/HTJ/t2/conf
P=~/miniforge3/envs/torch/bin/python
L=logs/fit_k1024.log

free_gpu () {   # echo the index of a GPU with no compute process, else nothing
  for g in 2 3 4 5 0 1; do
    if [ -z "$(nvidia-smi -i $g --query-compute-apps=pid --format=csv,noheader 2>/dev/null)" ]; then
      echo $g; return
    fi
  done
}

mkdir -p results/gmm_fits_D2_K1024
for f in results/gmm_fits_D2/*n10000*.npz; do
  ln -sf "../gmm_fits_D2/$(basename "$f")" "results/gmm_fits_D2_K1024/$(basename "$f")"
done
echo "[k1024] $(date '+%T') linked $(ls results/gmm_fits_D2_K1024 | wc -l) pre-registered N=1e4 fits" >> $L

until [ -n "$(free_gpu)" ]; do sleep 120; done
G=$(free_gpu)
echo "[k1024] $(date '+%T') GPU $G free -> kron K=1024, Nr=8, N=1e4" >> $L
CUDA_VISIBLE_DEVICES=$G $P code/fit_gpu.py 8 kron 1024 10000 K1024 >> $L 2>&1
echo "[k1024] $(date '+%T') EXIT=$?" >> $L
grep -E "b\*|K=1024" $L | tail -5 >> $L
