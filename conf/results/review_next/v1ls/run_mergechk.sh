#!/bin/bash
# NEXT_EXPERIMENTS_V1LS §5 병합 확인 (after FREEZE, before the s5 commit): from the MAIN tree at FREEZE, one +18 dB DEVELOPMENT chunk per
# (cell, modulation) -- QPSK trials 6000..6039, 16-QAM 5120..5159 -- with the six registered arms (--lowsig-arms --wide-ckpt), compared
# bit for bit (blk_err, nmse) with the development screens: V1 / b* / A / B with lowsig/screen_*_snr18 rows 0..39, C with screenCd_* rows
# 0..39; meta lowsig_s_lo = repr(ScorePrior.s_lo) of the V1 checkpoint (the arms.py s_lo assert and this meta never ran in a recorded
# runner run before); meta wide_ckpt_id / wide_sigma_tag = the new C.  Log logs/v1ls_smoke.log, end MERGECHK_DONE; verdict line
# "MERGECHK OK|FAIL" in results/review_next/v1ls/log_mergechk_compare.txt.
cd /home/HTJ/t2/conf || exit 1
P=~/miniforge3/envs/torch/bin/python; export CUDA_VISIBLE_DEVICES=; D=results/review_next/v1ls
echo "[v1ls mergechk $(TZ=America/Chicago date '+%m-%d %H:%M %Z') git $(git rev-parse --short HEAD)$([ -n "$(git status --porcelain code ../Demo)" ] && echo +dirty)] start" >> logs/v1ls_smoke.log
ARMS="M-ours-dscore-C-V1 M-ours-bstar R5-genie M-ours-dscore-C-V1-clamp M-ours-dscore-C-V1-gmmfb M-ours-dscore-C-V1-wide"
i=0
for j in "U28 UMi28 qpsk 6000" "U28 UMi28 16qam 5120" "D2 S2 qpsk 6000" "D2 S2 16qam 5120"; do
  set -- $j; CELL=$1; PR=$2; MOD=$3; SK=$4; T=${CELL}LSmc$MOD
  case $CELL in
    U28) SRC=results/gmm_fits_D2_U28B16e4; CK=/home/HTJ/t2/conf/ckpt/d2sx_UMi28_N160000_a1_best.pt
         WK=/home/HTJ/t2/conf/ckpt/d2sx_UMi28_N160000_a1_sgUMi28HSUd_best.pt ;;
    D2)  SRC=results/gmm_fits_D2_B16e4k; CK=/home/HTJ/t2/conf/ckpt/d2sx_N160000_a1.pt
         WK=/home/HTJ/t2/conf/ckpt/d2sx_N160000_a1_sgHSUd.pt ;;
  esac
  [ -d results/gmm_fits_D2_$T ] || { mkdir -p results/gmm_fits_D2_$T && cp -L $SRC/*.npz results/gmm_fits_D2_$T/; }
  nice -n 10 taskset -c $((140 + i)) $P code/runner.py run --testbed D2 --prior $PR --cell C2 --ntrain 160000 --stagec-ckpt $CK \
    $([ $MOD = 16qam ] && echo --mod 16qam) --chunk 40 --n 40 --skip0 $SK --snr 18 --arm $ARMS --lowsig-arms --wide-ckpt $WK \
    --tag $T > $D/log_mergechk_${CELL}_$MOD.txt 2>&1 &
  i=$((i + 1))
done
wait
$P - > $D/log_mergechk_compare.txt 2>&1 <<'PY'
import glob, hashlib, numpy as np
L = "results/review_next/lowsig"
WK = {"U28": "/home/HTJ/t2/conf/ckpt/d2sx_UMi28_N160000_a1_sgUMi28HSUd_best.pt", "D2": "/home/HTJ/t2/conf/ckpt/d2sx_N160000_a1_sgHSUd.pt"}
TAG = {"U28": "UMi28HSUd", "D2": "HSUd"}
SLO = {"U28": "0.032681101782796075", "D2": "0.033062204571989696"}      # repr(ScorePrior.s_lo) of the registered V1 (verifier, v2.1 review)
SCR = {"M-ours-dscore-C-V1": "V1", "M-ours-bstar": "b*", "M-ours-dscore-C-V1-clamp": "V1-clamp", "M-ours-dscore-C-V1-gmmfb": "V1-gmmfb"}
bad = 0
for cell, mod, sk in (("U28", "qpsk", 6000), ("U28", "16qam", 5120), ("D2", "qpsk", 6000), ("D2", "16qam", 5120)):
    fs = glob.glob(f"raw_{cell}LSmc{mod}/D2_*.npz")
    if len(fs) != 1:
        print(f"{cell} {mod}: {len(fs)} chunks -- FAIL"); bad += 1; continue
    z = np.load(fs[0]); zs = np.load(f"{L}/screen_{cell}_{mod}_{sk}_320_snr18.npz"); zc = np.load(f"{L}/screenCd_{cell}_{mod}_{sk}_320_snr18.npz")
    chk = {}
    for arm, s in SCR.items():
        for k in ("blk_err", "nmse"):
            chk[f"{s} {k}"] = np.array_equal(z[f"{arm}|{k}"], zs[f"18|{s}|{k}"][:40], equal_nan=True)
    for k in ("blk_err", "nmse"):
        chk[f"C {k}"] = np.array_equal(z[f"M-ours-dscore-C-V1-wide|{k}"], zc[k][:40], equal_nan=True)
    chk["meta lowsig_s_lo"] = str(z["meta|lowsig_s_lo"]) == SLO[cell]
    chk["meta wide_ckpt_id"] = hashlib.sha256(open(WK[cell], "rb").read()).hexdigest()[:16] in str(z["meta|wide_ckpt_id"])
    chk["meta wide_sigma_tag"] = str(z["meta|wide_sigma_tag"]) == TAG[cell]
    bad += sum(not v for v in chk.values())
    print(f"{cell} {mod} +18 dB trials {sk}..{sk + 39}: " + "  ".join(f"{k} {'OK' if v else 'DIFF'}" for k, v in chk.items())
          + f"   (lowsig_s_lo {z['meta|lowsig_s_lo']})")
print(f"MERGECHK {'OK' if bad == 0 else 'FAIL'} ({bad} problems)")
PY
echo "[v1ls mergechk $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] MERGECHK_DONE" >> logs/v1ls_smoke.log
