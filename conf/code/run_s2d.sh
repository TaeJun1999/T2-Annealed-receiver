#!/bin/bash
# B' (user decision 2026-09-27 CDT, "B' 도 추가해"): DRIFT-TRAINED priors.  S2d = S2 + per-block receive-array rotation
# delta ~ U[0, 30 deg] (d2.DRIFT; selftest_s2d), Nr=8 C2 budget N' = 1.6e5, tag S2dB16e4.  Verbatim copy of run_d3.sh (the D3
# queue: @train with the §3d ladder, GMM grid full/kron 16..512 + kron 1024 per restart, kron 2048/4096 candidates, post phase
# = merge kron 1024, b* by validation ll, grid-edge rule, GB') with S2c -> S2d, d3 -> s2d.  Differences:
#  - runs in the worktree ~/t2_wtB (branch c-rotmix) while the S2v queue (~/t2_wtC) and DOP (main) run;
#  - GPUs "0 2 3 4 5" (GPU 1 = S2v training, then its GB');  a worker WAITS until the S2v queue file is empty (no S2v job can
#    still start -> no exclusive-process race) and its GPU is free, instead of stopping.  NO BLER here.
CONF=${CONF:-/home/HTJ/t2_wtB/conf}
cd $CONF || exit 1
P=${P:-~/miniforge3/envs/torch/bin/python}
N=${N:-160000}; TAG=${TAG:-S2dB16e4}; GPUS=${GPUS:-"0 2 3 4 5"}
Q=logs/s2d_queue.txt; L=logs/s2d.log
log () { echo "[s2d $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $*" | tee -a $L >> logs/queue.log; }
busy () { local m; m=$(nvidia-smi -i $1 --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | tr -d ' ')
          [ -z "$m" ] || [ "$m" -gt 10 ]; }                  # nvidia-smi failure counts as busy
if [ ! -f $Q ]; then
  { echo "@train"
    for r in 0 1 2; do echo "code/fit_gpu_batched.py 8 kron 1024 $N $TAG --restart $r --prior S2d"; done
    for fk in "full 512" "full 256" "kron 512" "full 128" "kron 256" "full 64" "kron 128" "full 32" "kron 64" \
              "full 16" "kron 32" "kron 16"; do
      set -- $fk
      [ $1 = full ] && echo "code/fit_gpu.py 8 $fk $N $TAG --prior S2d" || echo "code/fit_gpu_batched.py 8 $fk $N $TAG --prior S2d"
    done
    for r in 0 1 2; do echo "code/fit_gpu_batched.py 8 kron 2048 $N $TAG --restart $r --prior S2d"; done
    for r in 0 1 2; do echo "code/fit_gpu_batched.py 8 kron 4096 $N $TAG --restart $r --prior S2d"; done; } > $Q   # review R2: idle-GPU candidates, never merged unless the edge rule + user decide
fi

train_chain () {                       # 10_SPEC §3d ladder on ONE GPU; writes "<fallback> <stopped_by>" for the post phase
  local g=$1 fb ck s
  for fb in 1 2 3; do
    ck=ckpt/d2sx_S2d_N${N}_a1$([ $fb -gt 1 ] && echo _fb$fb).pt
    CUDA_VISIBLE_DEVICES=$g $P code/run_d2_sx.py --prior S2d --ntrain $N --tag $TAG --fallback $fb --no-gbprime \
      >> logs/s2d_gpu$g.log 2>&1
    s=$(CUDA_VISIBLE_DEVICES= $P -c "import torch; print(torch.load('$ck', map_location='cpu', weights_only=False).get('stopped_by'))" 2>/dev/null)
    log "train fallback $fb: stopped_by=${s:-NO_CHECKPOINT} ($ck)"
    [ "$s" = diverged ] && [ $fb -lt 3 ] && { log "§3d: fallback $fb DIVERGED -> fallback $((fb + 1)) on GPU $g"; continue; }
    break
  done
  echo "$fb ${s:-NO_CHECKPOINT}" > logs/s2d_train_state.txt
}

worker () {
  local g=$1 job
  while true; do
    while [ -s $S2VQ ] || busy $g; do sleep 60; done              # wait: S2v queue drained and this GPU free
    job=$(flock $Q.lock sh -c "head -n1 $Q; sed -i 1d $Q")
    [ -z "$job" ] && break
    log "GPU $g start: $job"
    if [ "$job" = "@train" ]; then train_chain $g; rc="(train: see s2d_train_state.txt)"; else CUDA_VISIBLE_DEVICES=$g $P $job >> logs/s2d_gpu$g.log 2>&1; rc=$?; fi
    log "GPU $g done rc=$rc: $job"
  done
}

S2VQ=/home/HTJ/t2_wtC/conf/logs/s2v_queue.txt
free=" $GPUS"
git diff --quiet -- code 2>/dev/null || log "WARNING: conf/code has uncommitted changes -- the logged git hash does not describe the code"
log "queue start (git $(git rev-parse --short HEAD 2>/dev/null)), N=$N tag=$TAG GPUs:$free, $(wc -l < $Q) jobs"
for g in $free; do worker $g & done
wait
log "workers done; queue left: $(wc -l < $Q) jobs"

# ---- post phase
CUDA_VISIBLE_DEVICES= $P code/fit_gpu.py 8 kron 1024 $N $TAG --merge --prior S2d >> logs/s2d_post.log 2>&1
log "merge kron 1024 rc=$?"
CUDA_VISIBLE_DEVICES= $P - $N $TAG >> logs/s2d_post.log 2>&1 <<'EOF'
import sys
sys.path.insert(0, "code")
import runner, arms as A
N, TAG = int(sys.argv[1]), sys.argv[2]
runner._init(TAG)
fits, llv, bstar, kK = A.gmm_selection("D2", "S2d", 8, N)
fam = {f: sorted(K for g, K in fits if g == f) for f in ("full", "kron")}
miss = [f"{f} {K}" for f, Ks in (("full", (16, 32, 64, 128, 256, 512)), ("kron", (16, 32, 64, 128, 256, 512, 1024)))
        for K in Ks if K not in fam[f]]
edge = (kK == max(fam["kron"])) if bstar == "kron" else (int(bstar[3:]) == max(fam["full"]))
print(f"[s2d-post] b* = {bstar}" + (f" (kron K={kK})" if bstar == "kron" else "") + f" ll_val {llv[bstar]:.6f}; "
      f"full K {fam['full']} kron K {fam['kron']}; missing {miss or 'none'}; b* at grid edge: {edge}")
sys.exit(4 if miss else 3 if edge else 0)
EOF
rc=$?
log "$(grep '\[s2d-post\] b\*' logs/s2d_post.log | tail -1 | cut -c11-)"
read fb st < logs/s2d_train_state.txt 2>/dev/null
if [ $rc -eq 4 ]; then log "GRID INCOMPLETE -> GB' not run (see logs/s2d_post.log)"
elif [ $rc -eq 3 ]; then log "MANUAL: b* is the largest K of its family -> extend K (user decision, 01_RULES:76); GB' deferred;" \
  "kron 2048 candidates ready: $(ls results/gmm_fits_D2_$TAG/fit_S2d_Nr8_kronK2048_n$N.k0r*.npz 2>/dev/null | wc -l)/3" \
  "(merge: code/fit_gpu.py 8 kron 2048 $N $TAG --merge --prior S2d)"
elif [ $rc -ne 0 ]; then log "b* check failed rc=$rc -> GB' not run"
elif [ "$st" != patience ] && [ "$st" != max_epochs ]; then log "training state '$fb $st' -> no GB' (manual: §3d / resume)"
else
  g=$(for x in $free; do busy $x || { echo $x; break; }; done)
  [ -z "$g" ] && { log "no free GPU for GB' -> skipped (run manually)"; log "S2D_QUEUE_DONE"; exit 0; }
  CUDA_VISIBLE_DEVICES=$g $P code/run_d2_sx.py --prior S2d --ntrain $N --tag $TAG --fallback $fb >> logs/s2d_post.log 2>&1
  log "GB' (fallback $fb, GPU $g) rc=$?: $(grep '\[d2sx\] GMM b\*' logs/s2d_post.log | tail -1)"
fi
log "S2D_QUEUE_DONE"
