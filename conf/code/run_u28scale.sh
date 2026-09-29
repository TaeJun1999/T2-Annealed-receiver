#!/bin/bash
# stage 0 (user 2026-09-30 CDT: spare GPUs): UMi28 GB' trend over the array, Nr = 16 (C6) and 32 (C9), N = 1e4, frozen recipe, no BLER.
# Per Nr (tag U28NR<Nr>): 12 GMM fits (the C6 1e4 grid) -> SNR-grid probe (genie / b* / R2, development trials, n = 160) ->
# sigma grid -> V1 training (train_nr16.py --prior UMi28) -> GB' vs the equal-budget b*.  Compare with UMi28 Nr = 8 (0.920 @1.6e5).
# End U28SCALE_DONE in logs/u28scale.log.
cd /home/HTJ/t2_wtS/conf; P=~/miniforge3/envs/torch/bin/python; L=logs/u28scale.log
log () { echo "[u28scale $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $*" >> $L; }
fits () { local G=$1 N=$2; shift 2
  while [ $# -ge 2 ]; do CUDA_VISIBLE_DEVICES=$G $P code/fit_gpu.py $N $1 $2 10000 U28NR$N --prior UMi28 >> logs/fit_u28scale.log 2>&1; shift 2; done; }
fits 2 16 full 512 kron 512 full 64 kron 64 full 16 kron 16 & fits 3 16 full 256 kron 256 full 128 kron 128 full 32 kron 32 &
fits 4 32 full 512 kron 512 full 64 kron 64 full 16 kron 16 & fits 5 32 full 256 kron 256 full 128 kron 128 full 32 kron 32 &
wait
pipe () { local N=$1 CELL=$2 G=$3 T=U28NR$1
  n=$(ls results/gmm_fits_D2_$T/*.npz 2>/dev/null | wc -l); log "Nr=$N fits $n/12"; [ "$n" -eq 12 ] || { log "Nr=$N ABORT fits"; return 1; }
  CUDA_VISIBLE_DEVICES= $P code/runner.py run --testbed D2 --prior UMi28 --cell $CELL --snr -15 -12 -9 -6 -3 0 3 6 9 12 15 --n 160 --chunk 40 \
    --skip0 2560 --ntrain 10000 --arm R2-ours-G R5-genie M-ours-bstar --tag $T > logs/u28probe_$CELL.log 2>&1; log "Nr=$N SNR probe rc=$?"
  CUDA_VISIBLE_DEVICES= $P code/runner.py sigma --testbed D2 --prior UMi28 --cell $CELL --tag $T > logs/sigma_$T.log 2>&1 || { log "Nr=$N ABORT sigma"; return 1; }
  log "Nr=$N sigma $(grep -o 'sigma_t in \[[^]]*\]' logs/sigma_$T.log | tail -1)"
  CUDA_VISIBLE_DEVICES=$G $P code/train_nr16.py --nr $N --prior UMi28 --ntrain 10000 --sigma-tag $T --fits-tag $T > logs/train_$T.log 2>&1
  log "Nr=$N train+GB' rc=$?: $(grep -E 'trained' logs/train_$T.log | tail -1) | $(grep -E 'GMM b\* =' logs/train_$T.log | tail -1)"; }
pipe 16 C6 2 & pipe 32 C9 3 & wait
log U28SCALE_DONE
