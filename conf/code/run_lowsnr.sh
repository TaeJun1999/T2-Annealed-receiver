#!/bin/bash
# (10_SPEC_stageC §6p) Extend the SNR axis downward for C2 and C5 at equal budget N=1e4.
# No new GMM fit and no new training: arms.fit_path keys on (prior, Nr, fam, K, ntrain) only, so the
# pre-registered N=1e4 fits serve every SNR and every Tp.  Waits for the box to be free first --
# one 192-worker pool at a time.
cd /home/HTJ/t2/conf
P=~/miniforge3/envs/torch/bin/python
log () { echo "[lowsnr $(TZ=Asia/Seoul date '+%H:%M')] $*" >> logs/queue.log; }

while pgrep -f "runner.py run --testbed D2" > /dev/null; do sleep 60; done
log "box free -> §6p low-SNR extension"
$P code/runner.py run --testbed D2 --cell C2 C5 --prior S2 --snr -9 -7 -6 -5 \
   --n 2560 --chunk 40 --tag B1e4lo --ntrain 10000 \
   --stagec-ckpt /home/HTJ/t2/conf/ckpt/d2sx_N10000_a1.pt >> logs/run_D2_B1e4lo.log 2>&1
$P code/runner.py analysis --testbed D2 --tag B1e4lo >> logs/run_D2_B1e4lo.log 2>&1
$P code/guard_report.py --raw /home/HTJ/t2/conf/raw_B1e4lo --testbed D2 > results/guard_D2_B1e4lo.txt 2>&1
log "§6p low-SNR extension done"
