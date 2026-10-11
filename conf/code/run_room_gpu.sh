#!/bin/bash
# Room pools SRB (Sionna RT `box`, one fixed BS) and DMI (DeepMIMO i1_2p4, one fixed BS), equal budget N' = 1.6e5, cell C2 (8x4):
# ONE GPU queue = the two frozen-recipe score trainings (10_SPEC §3d ladder) + the two GMM grids, per prior the SAME job list and
# order as run_srt_gpu.sh (kron 1024 x3, full 512..16 / kron 512..16 interleaved, kron 2048 x3, kron 4096 x3).  kron = batched exact
# M-step (results/nr8b_batched_check_{SRB,DMI}_n160000.txt must say PASS), full = exact path.  NO BLER here.
# Usage: tmux new -d -s tb2room "GPUS='0 1 2' bash code/run_room_gpu.sh"
cd /home/HTJ/t2/conf || exit 1
Q=logs/tb2_queue.txt
[ -s $Q ] && { echo "queue $Q not empty"; exit 1; }
for PR in SRB DMI; do grep -q PASS results/nr8b_batched_check_${PR}_n160000.txt || { echo "batched EM check of $PR missing / not PASS"; exit 1; }; done
{
  for PR in SRB DMI; do echo "@train $PR ${PR}B16e4"; done
  for PR in SRB DMI; do T=${PR}B16e4
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
  done
} > $Q
rm -f $Q.stop
GPUS="${GPUS:-0 1 2}" exec bash code/run_tb2.sh
