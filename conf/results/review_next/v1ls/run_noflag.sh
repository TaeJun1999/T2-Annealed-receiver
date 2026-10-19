#!/bin/bash
# Fable S5: the smoke chunks (+18 dB, QPSK 6320..6359 / 16-QAM 5520..5559) again WITHOUT --lowsig-arms / --wide-ckpt, arms V1 b* genie only;
# then V1 / b* / genie must be byte-identical (every key) to the flagged smoke chunk (raw_<cell>LSsm<mod>).
cd /home/HTJ/t2_wtLS/conf || exit 1
P=~/miniforge3/envs/torch/bin/python; export CUDA_VISIBLE_DEVICES=; D=results/review_next/v1ls
echo "[v1ls noflag $(TZ=America/Chicago date '+%m-%d %H:%M %Z') git $(git rev-parse --short HEAD)$([ -n "$(git status --porcelain code ../Demo)" ] && echo +dirty)] start" >> logs/v1ls_smoke.log
i=0
for j in "U28 qpsk UMi28 6320 d2sx_UMi28_N160000_a1_best.pt" "U28 16qam UMi28 5520 d2sx_UMi28_N160000_a1_best.pt" \
         "D2 qpsk S2 6320 d2sx_N160000_a1.pt" "D2 16qam S2 5520 d2sx_N160000_a1.pt"; do
  set -- $j; T=$1LSnf$2
  mkdir -p results/gmm_fits_D2_$T; cp -L results/gmm_fits_D2_$1LSsm$2/*.npz results/gmm_fits_D2_$T/
  nice -n 10 taskset -c $((33 + i)) $P code/runner.py run --testbed D2 --prior $3 --cell C2 --ntrain 160000 --stagec-ckpt /home/HTJ/t2/conf/ckpt/$5 \
    --chunk 40 --n 40 --skip0 $4 --snr 18 --arm M-ours-dscore-C-V1 M-ours-bstar R5-genie --tag $T $([ $2 = 16qam ] && echo --mod 16qam) \
    > $D/log_noflag_$1_$2.txt 2>&1 &
  i=$((i + 1))
done
wait
$P - >> logs/v1ls_smoke.log 2>&1 <<'PY'
import glob, os, numpy as np
for c in ("U28", "D2"):
    for m in ("qpsk", "16qam"):
        a, b = glob.glob(f"raw_{c}LSnf{m}/*.npz"), glob.glob(f"raw_{c}LSsm{m}/*.npz")
        if len(a) != 1 or len(b) != 1:
            print(c, m, "MISSING", a, b); continue
        za, zb = np.load(a[0]), np.load(b[0])
        keys = [k for k in za.files if k.split("|")[0] in ("M-ours-dscore-C-V1", "M-ours-bstar", "R5-genie")]
        diff = [k for k in keys if not np.array_equal(za[k], zb[k], equal_nan=True)]
        print(f"noflag vs flagged smoke {c} {m}: {len(keys)} arrays (V1 b* genie), differing {diff}")
PY
echo "[v1ls noflag $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] NOFLAG_DONE" >> logs/v1ls_smoke.log
