#!/bin/bash
# U28NR32GCAP fits (fit_manifest_U28NR32GCAP.json).  One process per call, run in its own tmux session:
#   bash run_gcap_fits.sh cont <gpu>           continuation 50 of the selected K4096 fit
#   bash run_gcap_fits.sh k8192 <gpu> <r>...   K8192 restarts r (in order; a restart whose candidate or marker exists is skipped)
#   bash run_gcap_fits.sh merge                K8192 merge on CPU (all three candidates must exist)
# GPU g gets its NUMA hyperthread pair (GPU 0-3 -> c = g, GPU 4-5 -> c = 44 + g); merge runs on CPU 24,120 with no GPU.
set -u
cd ~/t2/conf
PY=~/miniforge3/envs/torch/bin/python
SRC=/home/HTJ/t2_wtS/conf/results/gmm_fits_D2_U28NR32B16e4/fit_UMi28_Nr32_kronK4096_n160000.npz
SHA=2d72a4349e2700e79aec72b48bebed29e59b0f336091b9a6706dbd70d29ef569
FITS=results/gmm_fits_D2_U28NR32GCAP
LOG=logs/gcap_fits.log
stamp() { echo "[gcap $(TZ=America/Chicago date '+%m-%d %H:%M:%S CDT') git $(git rev-parse --short HEAD)$(git diff --quiet HEAD -- code || echo '+dirty')] $*" >> $LOG; }
pair() { local g=$1; local c=$(( g < 4 ? g : 44 + g )); echo "$c,$((c + 96))"; }
mkdir -p $FITS
case $1 in
  cont)
    g=$2; stamp "start cont GPU $g"
    CUDA_VISIBLE_DEVICES=$g taskset -c $(pair $g) $PY code/fit_gcap_cont.py $SRC $SHA 50 U28NR32GCAP 32 --prior UMi28 >> logs/gcap_cont.log 2>&1
    stamp "end cont rc=$?";;
  k8192)
    g=$2; shift 2
    for r in "$@"; do
      cand=$FITS/fit_UMi28_Nr32_kronK8192_n160000.k0r$r.npz; mark=$FITS/.started_k8192_r$r
      if [ -e $cand ] || [ -e $mark ]; then stamp "skip K8192 r$r (candidate or marker exists)"; continue; fi
      touch $mark; stamp "start K8192 r$r GPU $g"
      FIT_KRON_BATCHED=1 FIT_STOP_RULE=gcap CUDA_VISIBLE_DEVICES=$g taskset -c $(pair $g) \
        $PY code/fit_gpu.py 32 kron 8192 160000 U28NR32GCAP --restart $r --prior UMi28 >> logs/gcap_k8192.log 2>&1
      stamp "end K8192 r$r rc=$?"
    done;;
  merge)
    stamp "start K8192 merge (CPU)"
    CUDA_VISIBLE_DEVICES= taskset -c 24,120 $PY code/fit_gpu.py 32 kron 8192 160000 U28NR32GCAP --merge --prior UMi28 >> logs/gcap_k8192.log 2>&1
    stamp "end K8192 merge rc=$?";;
  *) echo "usage: see header"; exit 2;;
esac
