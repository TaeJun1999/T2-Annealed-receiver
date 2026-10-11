#!/bin/bash
# Sionna RT prior SRT, equal budget N' = 1.6e5, cell C2 (8x4): GPU queue = frozen-recipe score training (10_SPEC §3d ladder) + the GMM
# grid, the SAME job list and order as UMi28 (logs/tb2.log 09-26 CDT: @train, kron 1024 x3, full 512..16 / kron 512..16 interleaved,
# kron 2048 x3, kron 4096 x3).  kron = batched exact M-step (results/nr8b_batched_check_SRT_n160000.txt: PASS), full = exact path.
# NO BLER here (BLER only after the pre-registration is frozen).  Usage: tmux new -d -s tb2srt "GPUS='0 1 2' bash code/run_srt_gpu.sh"
cd /home/HTJ/t2/conf || exit 1
T=SRTB16e4; PR=SRT; Q=logs/tb2_queue.txt
[ -s $Q ] && { echo "queue $Q not empty"; exit 1; }
{
  echo "@train $PR $T"
  for r in 0 1 2; do echo "code/fit_gpu_batched.py 8 kron 1024 160000 $T --restart $r --prior $PR"; done
  echo "code/fit_gpu.py 8 full 512 160000 $T --prior $PR"
  echo "code/fit_gpu.py 8 full 256 160000 $T --prior $PR"
  echo "code/fit_gpu_batched.py 8 kron 512 160000 $T --prior $PR"
  echo "code/fit_gpu.py 8 full 128 160000 $T --prior $PR"
  echo "code/fit_gpu_batched.py 8 kron 256 160000 $T --prior $PR"
  echo "code/fit_gpu.py 8 full 64 160000 $T --prior $PR"
  echo "code/fit_gpu_batched.py 8 kron 128 160000 $T --prior $PR"
  echo "code/fit_gpu.py 8 full 32 160000 $T --prior $PR"
  echo "code/fit_gpu_batched.py 8 kron 64 160000 $T --prior $PR"
  echo "code/fit_gpu.py 8 full 16 160000 $T --prior $PR"
  echo "code/fit_gpu_batched.py 8 kron 32 160000 $T --prior $PR"
  echo "code/fit_gpu_batched.py 8 kron 16 160000 $T --prior $PR"
  for K in 2048 4096; do for r in 0 1 2; do echo "code/fit_gpu_batched.py 8 kron $K 160000 $T --restart $r --prior $PR"; done; done
} > $Q
rm -f $Q.stop
GPUS="${GPUS:-0 1 2}" exec bash code/run_tb2.sh     # the GPUs handed to us (override: GPUS="..." bash code/run_srt_gpu.sh)
