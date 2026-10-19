#!/bin/bash
# Pre-freeze development check (new C = d2sx_*_sgUMi28HSUd_best.pt / _sgHSUd.pt): the runner's M-ours-dscore-C-V1-wide arm on the first
# 40 trials of the development screens must be bit-identical (blk_err, nmse) to eval_c.py 'd' (screenCd_*), and V1 to diag_lowsig (screen_*);
# meta wide_ckpt_id / wide_sigma_tag must name the new C.  Development trials only (QPSK 6000..6039, 16-QAM 5120..5159), +18 dB.
cd /home/HTJ/t2_wtLS/conf || exit 1
P=~/miniforge3/envs/torch/bin/python; export CUDA_VISIBLE_DEVICES=; D=results/review_next/v1ls
echo "[v1ls widechk $(TZ=America/Chicago date '+%m-%d %H:%M %Z') git $(git rev-parse --short HEAD)$([ -n "$(git status --porcelain code ../Demo)" ] && echo +dirty)] start" >> logs/v1ls_smoke.log
i=0
for j in "U28 UMi28 qpsk 6000" "U28 UMi28 16qam 5120" "D2 S2 qpsk 6000" "D2 S2 16qam 5120"; do
  set -- $j; CELL=$1; PR=$2; MOD=$3; SK=$4; T=${CELL}LSwc$MOD
  case $CELL in
    U28) SRC=/home/HTJ/t2/conf/results/gmm_fits_D2_U28B16e4; CK=/home/HTJ/t2/conf/ckpt/d2sx_UMi28_N160000_a1_best.pt
         WK=/home/HTJ/t2/conf/ckpt/d2sx_UMi28_N160000_a1_sgUMi28HSUd_best.pt ;;
    D2)  SRC=/home/HTJ/t2/conf/results/gmm_fits_D2_B16e4k; CK=/home/HTJ/t2/conf/ckpt/d2sx_N160000_a1.pt
         WK=/home/HTJ/t2/conf/ckpt/d2sx_N160000_a1_sgHSUd.pt ;;
  esac
  [ -d results/gmm_fits_D2_$T ] || { mkdir -p results/gmm_fits_D2_$T && cp -L $SRC/*.npz results/gmm_fits_D2_$T/; }
  nice -n 10 taskset -c $((140 + i)) $P code/runner.py run --testbed D2 --prior $PR --cell C2 --ntrain 160000 --stagec-ckpt $CK \
    $([ $MOD = 16qam ] && echo --mod 16qam) --chunk 40 --n 40 --skip0 $SK --snr 18 --arm M-ours-dscore-C-V1 M-ours-dscore-C-V1-wide \
    --wide-ckpt $WK --tag $T > $D/log_widechk_${CELL}_$MOD.txt 2>&1 &
  i=$((i + 1))
done
wait
$P - >> $D/log_widechk_compare.txt 2>&1 <<'PY'
import glob, hashlib, numpy as np
L = "/home/HTJ/t2/conf/results/review_next/lowsig"
WK = {"U28": "/home/HTJ/t2/conf/ckpt/d2sx_UMi28_N160000_a1_sgUMi28HSUd_best.pt", "D2": "/home/HTJ/t2/conf/ckpt/d2sx_N160000_a1_sgHSUd.pt"}
TAG = {"U28": "UMi28HSUd", "D2": "HSUd"}
bad = 0
for cell, mod, sk in (("U28", "qpsk", 6000), ("U28", "16qam", 5120), ("D2", "qpsk", 6000), ("D2", "16qam", 5120)):
    fs = glob.glob(f"raw_{cell}LSwc{mod}/D2_*.npz")
    if len(fs) != 1:
        print(f"{cell} {mod}: {len(fs)} chunks -- FAIL"); bad += 1; continue
    z = np.load(fs[0]); zc = np.load(f"{L}/screenCd_{cell}_{mod}_{sk}_320_snr18.npz"); zs = np.load(f"{L}/screen_{cell}_{mod}_{sk}_320_snr18.npz")
    sha16 = hashlib.sha256(open(WK[cell], "rb").read()).hexdigest()[:16]
    chk = {"wide blk_err": np.array_equal(z["M-ours-dscore-C-V1-wide|blk_err"], zc["blk_err"][:40]),
           "wide nmse": np.array_equal(z["M-ours-dscore-C-V1-wide|nmse"], zc["nmse"][:40], equal_nan=True),
           "V1 blk_err": np.array_equal(z["M-ours-dscore-C-V1|blk_err"], zs["18|V1|blk_err"][:40]),
           "meta wide_ckpt_id": sha16 in str(z["meta|wide_ckpt_id"]),
           "meta wide_sigma_tag": str(z["meta|wide_sigma_tag"]) == TAG[cell]}
    if "18|V1|nmse" in zs.files:
        chk["V1 nmse"] = np.array_equal(z["M-ours-dscore-C-V1|nmse"], zs["18|V1|nmse"][:40], equal_nan=True)
    bad += sum(not v for v in chk.values())
    f = lambda a: int((np.asarray(a)[:, 15] != 0).sum())
    print(f"{cell} {mod} +18 dB trials {sk}..{sk + 39}: " + "  ".join(f"{k} {'OK' if v else 'DIFF'}" for k, v in chk.items())
          + f"   failures@16 V1 {f(z['M-ours-dscore-C-V1|blk_err'])} wide {f(z['M-ours-dscore-C-V1-wide|blk_err'])} / 40")
print(f"WIDECHK {'OK' if bad == 0 else 'FAIL'} ({bad} problems)")
PY
echo "[v1ls widechk $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] WIDECHK_DONE" >> logs/v1ls_smoke.log
