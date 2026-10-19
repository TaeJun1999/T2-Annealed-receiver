#!/bin/bash
# E1+ (PROMPT_SERVER_E1MS 확인 3): V1 and V4 re-run on ONE recorded chunk of raw_B16e4k (D2 C2 -3 dB, test trials 0..39 -- the prompt's
# regression; V1-ms is NOT run on test trials: --arm keeps V1 and V4 only) with --ms-arm ON and OFF; every KEYS_RAW array of the two
# arms must be bit-identical to the recorded chunk.
cd /home/HTJ/t2_wtMS/conf || exit 1
P=~/miniforge3/envs/torch/bin/python; export CUDA_VISIBLE_DEVICES=; L=logs/e1ms_regress.log
echo "[e1ms-regress $(TZ=America/Chicago date '+%m-%d %H:%M %Z') git $(git rev-parse --short HEAD)$([ -n "$(git status --porcelain code ../Demo)" ] && echo +dirty)] start" >> $L
i=0
for f in on off; do
  T=E1MSreg$f
  [ -d results/gmm_fits_D2_$T ] || { mkdir -p results/gmm_fits_D2_$T && cp -L /home/HTJ/t2/conf/results/gmm_fits_D2_B16e4k/*.npz results/gmm_fits_D2_$T/; }
  nice -n 10 taskset -c $((3 + i)) $P code/runner.py run --testbed D2 --prior S2 --cell C2 --ntrain 160000 \
    --stagec-ckpt /home/HTJ/t2/conf/ckpt/d2sx_N160000_a1.pt --chunk 40 --n 40 --snr -3 \
    --arm M-ours-dscore-C-V1 M-ours-dscore-C-V4 $([ $f = on ] && echo --ms-arm) --tag $T > logs/e1ms_regress_$f.log 2>&1 &
  i=$((i + 1))
done
wait
$P - >> $L 2>&1 <<'PY'
import sys; sys.path.insert(0, "code"); import numpy as np, common as C
ref = np.load("/home/HTJ/t2/conf/raw_B16e4k/D2_C2_S2_Nr8_T16_Tp4_dft_snr-3_skip0_n40.npz")
bad = 0
for f in ("on", "off"):
    z = np.load(f"raw_E1MSreg{f}/D2_C2_S2_Nr8_T16_Tp4_dft_snr-3_skip0_n40.npz")
    diff = [f"{a}|{k}" for a in ("M-ours-dscore-C-V1", "M-ours-dscore-C-V4") for k in C.KEYS_RAW
            if not np.array_equal(z[f"{a}|{k}"], ref[f"{a}|{k}"], equal_nan=True)]
    extra = sorted({k.split("|")[0] for k in z.files if not k.startswith(("meta|", "run|"))} - {"M-ours-dscore-C-V1", "M-ours-dscore-C-V4"})
    print(f"--ms-arm {f}: {2 * len(C.KEYS_RAW)} arrays, differing {diff}, other arms in the chunk {extra}, meta ms_arm "
          f"{'present' if 'meta|ms_arm' in z.files else 'absent'}")
    bad += len(diff) + len(extra)
print(f"E1MS_REGRESS {'OK' if bad == 0 else 'FAIL'}")
PY
echo "[e1ms-regress $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] REGRESS_DONE" >> $L
