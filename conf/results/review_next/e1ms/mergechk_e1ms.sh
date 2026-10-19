#!/bin/bash
# NEXT_EXPERIMENTS_D2SITEMS §5 병합 확인 (after the merge 7af288e6 and the user's approval, before the s5 commit), from the MAIN tree:
#  (a) V1 and V4 on ONE recorded chunk of raw_B16e4k (D2 C2 -3 dB, test trials 0..39 -- the approved regression; V1-ms is not run on test
#      trials: --arm keeps V1 and V4), --ms-arm ON and OFF: every KEYS_RAW array of the two arms bit-identical to the recorded chunk;
#  (b) the development smoke chunk (V1-ms + R5-genie, -3 dB, trials 2560..2599, --ms-arm): every KEYS_RAW array bit-identical to the
#      worktree's smoke raw (/home/HTJ/t2_wtMS/conf/raw_E1MSsm, e1-ms 2807dd23).
# Log logs/e1ms_mergechk.log, verdict "E1MS_MERGECHK OK|FAIL" in results/review_next/e1ms/mergechk_compare.txt.
cd /home/HTJ/t2/conf || exit 1
P=~/miniforge3/envs/torch/bin/python; export CUDA_VISIBLE_DEVICES=; L=logs/e1ms_mergechk.log; CK=/home/HTJ/t2/conf/ckpt/d2sx_N160000_a1.pt
echo "[e1ms-mergechk $(TZ=America/Chicago date '+%m-%d %H:%M %Z') git $(git rev-parse --short HEAD)$([ -n "$(git status --porcelain code ../Demo)" ] && echo +dirty)] start" >> $L
i=0
for spec in "E1MSmcaon -3 0 M-ours-dscore-C-V1,M-ours-dscore-C-V4 on" "E1MSmcaoff -3 0 M-ours-dscore-C-V1,M-ours-dscore-C-V4 off" \
            "E1MSmcb -3 2560 M-ours-dscore-C-V1ms,R5-genie on"; do
  set -- $spec; T=$1; SNR=$2; SK=$3; ARMS=$(echo $4 | tr ',' ' '); MS=$5
  [ -d results/gmm_fits_D2_$T ] || { mkdir -p results/gmm_fits_D2_$T && cp -L results/gmm_fits_D2_B16e4k/*.npz results/gmm_fits_D2_$T/; }
  nice -n 10 taskset -c $((24 + i)) $P code/runner.py run --testbed D2 --prior S2 --cell C2 --ntrain 160000 --stagec-ckpt $CK \
    --chunk 40 --n 40 --skip0 $SK --snr $SNR --arm $ARMS $([ $MS = on ] && echo --ms-arm) --tag $T > logs/e1ms_mergechk_$T.log 2>&1 &
  i=$((i + 1))
done
wait
$P - > results/review_next/e1ms/mergechk_compare.txt 2>&1 <<'PY'
import sys; sys.path.insert(0, "code"); import numpy as np, common as C
bad = 0
ref = np.load("raw_B16e4k/D2_C2_S2_Nr8_T16_Tp4_dft_snr-3_skip0_n40.npz")
for t in ("E1MSmcaon", "E1MSmcaoff"):
    z = np.load(f"raw_{t}/D2_C2_S2_Nr8_T16_Tp4_dft_snr-3_skip0_n40.npz")
    diff = [f"{a}|{k}" for a in ("M-ours-dscore-C-V1", "M-ours-dscore-C-V4") for k in C.KEYS_RAW
            if not np.array_equal(z[f"{a}|{k}"], ref[f"{a}|{k}"], equal_nan=True)]
    extra = sorted({k.split("|")[0] for k in z.files} - {"meta", "run", "M-ours-dscore-C-V1", "M-ours-dscore-C-V4"})
    print(f"(a) {t}: {2 * len(C.KEYS_RAW)} arrays vs raw_B16e4k, differing {diff}, other arms {extra}, meta|ms_arm {'present' if 'meta|ms_arm' in z.files else 'absent'}")
    bad += len(diff) + len(extra)
z = np.load("raw_E1MSmcb/D2_C2_S2_Nr8_T16_Tp4_dft_snr-3_skip2560_n40.npz")
for d in ("raw_E1MSdev", "raw_E1MSsm"):    # §5 (b) names the dev screen raw; the smoke raw is the same chunk
    w = np.load(f"/home/HTJ/t2_wtMS/conf/{d}/D2_C2_S2_Nr8_T16_Tp4_dft_snr-3_skip2560_n40.npz")
    diff = [f"{a}|{k}" for a in ("M-ours-dscore-C-V1ms", "R5-genie") for k in C.KEYS_RAW
            if not np.array_equal(z[f"{a}|{k}"], w[f"{a}|{k}"], equal_nan=True)]
    print(f"(b) E1MSmcb: {2 * len(C.KEYS_RAW)} arrays vs the worktree {d} (git {w['run|git']}), differing {diff}")
    bad += len(diff)
print(f"E1MS_MERGECHK {'OK' if bad == 0 else 'FAIL'} ({bad} problems)")
PY
echo "[e1ms-mergechk $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] MERGECHK_DONE" >> $L
