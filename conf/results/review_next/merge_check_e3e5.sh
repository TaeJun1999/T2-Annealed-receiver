#!/bin/bash
# merge_check_e3e5.sh -- after merging e3-sbl32 and e5-qam16 into main (auto-merged conf/code/arms.py and runner.py), re-run the
# three development smoke chunks with the MERGED code and compare every data array with the chunk each branch wrote:
#   SBL-loop (4,3,1,1) + genie, UMi28 C9, 0 dB, trials 4160..4199   vs ~/t2_wtE3/conf/raw_U28NR32SBLdev
#   16-QAM five arms, UMi28 C2, +12 dB, trials 5480..5519           vs ~/t2_wtE5/conf/raw_U28QAM16dev
#   16-QAM five arms, D2 (S2) C2, +12 dB, trials 5480..5519          vs ~/t2_wtE5/conf/raw_D2QAM16dev
# Development trials only; no BLER is printed.  Fits folders = byte copies of the branch smoke folders.  Ends "MERGECHECK_DONE".
#   cd ~/t2/conf && bash results/review_next/merge_check_e3e5.sh      (tmux; nice 10, CPUs 189-191)
cd /home/HTJ/t2/conf || exit 1
P=~/miniforge3/envs/torch/bin/python; export CUDA_VISIBLE_DEVICES=; L=logs/merge_check_e3e5.log
echo "[mergecheck $(TZ=America/Chicago date '+%m-%d %H:%M %Z') git $(git rev-parse --short HEAD)$([ -n "$(git status --porcelain code ../Demo)" ] && echo +dirty)] start" | tee -a $L
cp_fits () { mkdir -p results/gmm_fits_D2_$2 && for f in $1/*.npz; do cp -L $f results/gmm_fits_D2_$2/; done; }
cp_fits /home/HTJ/t2_wtE3/conf/results/gmm_fits_D2_U28NR32SBLdev U28NR32SBLmrg
cp_fits /home/HTJ/t2_wtE5/conf/results/gmm_fits_D2_U28QAM16dev U28QAM16mrg
cp_fits /home/HTJ/t2_wtE5/conf/results/gmm_fits_D2_D2QAM16dev D2QAM16mrg
nice -n 10 taskset -c 191 $P code/runner.py run --testbed D2 --prior UMi28 --cell C9 --ntrain 160000 --chunk 40 --n 40 --skip0 4160 \
  --snr 0 --arm SBL-loop R5-genie --sparse-arms 4,3,1,1 --tag U28NR32SBLmrg >> $L 2>&1 &
nice -n 10 taskset -c 190 $P code/runner.py run --testbed D2 --prior UMi28 --cell C2 --ntrain 160000 \
  --stagec-ckpt /home/HTJ/t2/conf/ckpt/d2sx_UMi28_N160000_a1_best.pt --pilot-arms --mod 16qam --chunk 40 --n 40 --skip0 5480 --snr 12 \
  --arm M-ours-dscore-C-V1 M-ours-bstar R2-ours-G R5-genie V1-pilot --tag U28QAM16mrg >> $L 2>&1 &
nice -n 10 taskset -c 189 $P code/runner.py run --testbed D2 --prior S2 --cell C2 --ntrain 160000 \
  --stagec-ckpt /home/HTJ/t2/conf/ckpt/d2sx_N160000_a1.pt --pilot-arms --mod 16qam --chunk 40 --n 40 --skip0 5480 --snr 12 \
  --arm M-ours-dscore-C-V1 M-ours-bstar R2-ours-G R5-genie V1-pilot --tag D2QAM16mrg >> $L 2>&1 &
wait
$P - >> $L 2>&1 <<'PY'
import glob, numpy as np
pairs = [("raw_U28NR32SBLmrg", "/home/HTJ/t2_wtE3/conf/raw_U28NR32SBLdev"), ("raw_U28QAM16mrg", "/home/HTJ/t2_wtE5/conf/raw_U28QAM16dev"),
         ("raw_D2QAM16mrg", "/home/HTJ/t2_wtE5/conf/raw_D2QAM16dev")]
for new, old in pairs:
    fn, fo = sorted(glob.glob(f"{new}/*.npz")), sorted(glob.glob(f"{old}/*.npz"))
    if len(fn) != 1 or len(fo) != 1 or fn[0].split("/")[-1] != fo[0].split("/")[-1]:
        print(f"{new}: chunk files {fn} vs {fo} -- MISMATCH"); continue
    a, b = np.load(fn[0]), np.load(fo[0])
    ka = sorted(k for k in a.files if not k.startswith(("meta|", "run|")))
    kb = sorted(k for k in b.files if not k.startswith(("meta|", "run|")))
    diff = [k for k in ka if k not in kb or not np.array_equal(a[k], b[k], equal_nan=True)]
    meta = [k for k in a.files if k.startswith("meta|") and k in b.files and "em_sec" not in k and "fits" not in k
            and str(a[k]) != str(b[k])]
    print(f"{new} vs {old}: {len(ka)} data arrays (old {len(kb)}), differing {diff}; run|git {a['run|git']} vs {b['run|git']}; "
          f"meta keys differing (excl. em_sec / paths): {meta}")
PY
echo "MERGECHECK_DONE $(TZ=America/Chicago date '+%m-%d %H:%M %Z')" | tee -a $L
