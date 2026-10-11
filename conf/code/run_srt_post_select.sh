#!/bin/bash
# NEXT_EXPERIMENTS_SRT16e4 §1 "순서 규칙" / "GMM 격자와 b*": AFTER the freeze commit and after the 21 fit jobs of the queue ended --
# merge kron 1024 / 2048, select b* by the validation likelihood (arms.gmm_selection; BLER is never consulted), apply the
# grid-edge rule (b* = kron 2048 -> merge kron 4096 and select again; STOP at 4096), list every fit file, and create the fits
# link of the report-only tag.  CPU only.  A full-512 b* is reported and left to the registered rule (full 1024 once, by hand).
# Usage: bash code/run_srt_post_select.sh <freeze commit>        log: logs/tb2_post_SRT.log, end marker POST_SELECT_DONE
cd /home/HTJ/t2/conf || exit 1
P=~/miniforge3/envs/torch/bin/python; T=SRTB16e4; PR=SRT; D=results/gmm_fits_D2_$T; L=logs/tb2_post_$PR.log; FZ=$1
export CUDA_VISIBLE_DEVICES=
log () { echo "[post $PR $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $*" | tee -a $L; }
[ -n "$FZ" ] && git cat-file -e "$FZ^{commit}" 2>/dev/null || { echo "usage: run_srt_post_select.sh <freeze commit>"; exit 1; }
git show "$FZ:conf/results/review_next/NEXT_EXPERIMENTS_SRT16e4.md" | head -1 | grep -q "사전 등록 v2" || { log "ABORT: $FZ is not the v2 freeze commit"; exit 1; }
n=$(ls $D/fit_${PR}_Nr8_*_n160000*.npz 2>/dev/null | wc -l)
[ "$(grep -c "done rc=0: code/fit_gpu.* $T .*--prior $PR" logs/tb2.log)" -ge 21 ] || { log "ABORT: the 21 fit jobs have not all ended with rc=0"; exit 1; }
log "freeze $FZ ($(TZ=America/Chicago git log -1 --format=%cd --date=format-local:'%m-%d %H:%M:%S CDT' $FZ)) done; $n fit files present -> merge kron 1024 / 2048 (registered base grid), select b*"
sel () { $P - <<PY 2>&1 | grep -v -i warn | tee -a $L
import sys; sys.path.insert(0, "code")
import arms as A, runner
runner._init("$T")
fits, llv, b, kK = A.gmm_selection("D2", "$PR", 8, 160000)
print("ll_val by arm:", {k: round(v, 4) for k, v in llv.items()}, "| kron ll_val by K:", {K: round(float(fits[("kron", K)]["ll_val"]), 4) for f, K in sorted(fits) if f == "kron"})
print("SELECT b* =", b, "kron_K =", kK, "ll_val =", repr(llv[b]), "| full best:", max((v, k) for k, v in llv.items() if k != "kron"))
open("logs/tb2_post_${PR}.sel", "w").write(f"{b} {kK if b == 'kron' else '-'} {llv[b]!r}\\n")       # the decision is passed by FILE, not by a printed string
PY
}
for K in 1024 2048; do $P code/fit_gpu.py 8 kron $K 160000 $T --merge --prior $PR 2>&1 | grep -v -i warn | tee -a $L; done
sel
if [ "$(cut -d' ' -f1,2 logs/tb2_post_$PR.sel)" = "kron 2048" ]; then
  log "b* = kron 2048 = base-grid edge -> merge kron 4096 (registered rule; STOP at 4096)"
  $P code/fit_gpu.py 8 kron 4096 160000 $T --merge --prior $PR 2>&1 | grep -v -i warn | tee -a $L
  sel
fi
$P - <<PY 2>&1 | tee -a $L
import glob, os, time, numpy as np
g = lambda z, k: (z[k].item() if k in z.files and z[k].ndim == 0 else "-")
for f in sorted(glob.glob("$D/fit_${PR}_Nr8_*_n160000*.npz")):
    z = np.load(f, allow_pickle=True)
    print(os.path.basename(f), repr(float(z["ll_val"])), "n_iter", g(z, "n_iter"), "it_best", g(z, "it_best"), "reseed", g(z, "n_reseed"), "kappa", g(z, "kappa"),
          "restart", g(z, "restart"), "mtime", time.strftime("%m-%d %H:%M:%S KST", time.localtime(os.path.getmtime(f))))
PY
ln -sfn gmm_fits_D2_$T results/gmm_fits_D2_${T}last
log "final b* (family kron_K ll_val) = $(cat logs/tb2_post_$PR.sel); link gmm_fits_D2_${T}last created; POST_SELECT_DONE"
