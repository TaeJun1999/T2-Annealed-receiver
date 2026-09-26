#!/bin/bash
# (user decisions 2026-09-25 CDT: "(B) the D3 mechanism control", pre-registered (Fable) before any BLER; training and
# fitting may start before the freeze)  D3 = D2 prior S2c (alpha_l ~ CN(0, p_l), code/d2.py; testbed results/testbed_D3.txt),
# Nr=8, equal budget N' = 1.6e5, tag D3B16e4.  GPU job queue modelled on run_nr16b.sh / run_b32e4.sh.  NO BLER here.
#  - @train: score training with the frozen recipe (run_d2_sx.py --prior S2c: rung D2SXS2c<N>, ckpt/d2sx_S2c_N<N>_a1*.pt,
#    sigma grid results/sigma_grid_D2_S2c.npz), attempt 1, with the 10_SPEC §3d ladder as a hook ON THE SAME GPU: attempt
#    --fallback k+1 (2 = grad-norm clip 1.0, 3 = + lr/3) starts only when attempt k's checkpoint says stopped_by=diverged.
#    Anything else that is not patience/max_epochs (a crash / kill: no stopped_by) stops the chain -> manual decision, no
#    automatic retry.  --no-gbprime: GB' is computed in the post phase against the COMPLETE grid, never a partial one.
#  - GMM grid for S2c, Nr=8, N': runner.cmd_fit protocol through fit_gpu.py --prior S2c (kappa grid for full, 3 restarts,
#    500-iteration cap, validation early stopping, selection by validation log-likelihood only) into
#    results/gmm_fits_D2_D3B16e4/fit_S2c_Nr8_*: full K 512..16 exact path; kron K 512..16 with the batched exact kron
#    M-step (fit_gpu_batched.py; em_batched_check / _check2 / _check_nr PASSED on S2 at Nr 8/16, incl. reseeds); kron
#    K=1024 batched per restart (3 jobs) and --merge in the post phase.
#  - LAST in the queue, for GPUs that would otherwise idle while training runs (~10 h vs ~2 h of fits): kron K=2048 per-
#    restart CANDIDATES only (fit_gpu.py --restart r writes fit_...kronK2048_....k0r<r>.npz; arms.load_fits reads only the
#    merged file, so the grid and b* are untouched).  They are merged ONLY if the edge rule below fires and the user decides.
#  - post phase (after every worker is done): merge kron 1024, b* by validation log-likelihood, the grid-edge rule
#    (01_RULES:76, 10_SPEC §6l): b* = the LARGEST K of its family -> "MANUAL: extend K" (user decision, as C6/B32e4), GB'
#    deferred; otherwise GB' (run_d2_sx.py resume -> no epoch trained) for the attempt the ladder ended on.
# Usage:  bash code/run_d3.sh                      GPUS="0 1 2 3 4 5" by default (user: use every free resource)
#         GPUS="0 1 2" bash code/run_d3.sh         a GPU whose memory is in use at launch or before a job is skipped
# Resumable: the queue file persists (only un-started jobs), fits skip existing files, training resumes its checkpoint.
CONF=${CONF:-/home/HTJ/t2/conf}
cd $CONF || exit 1
P=${P:-~/miniforge3/envs/torch/bin/python}
N=${N:-160000}; TAG=${TAG:-D3B16e4}; GPUS=${GPUS:-"0 1 2 3 4 5"}
Q=logs/d3_queue.txt; L=logs/d3.log
log () { echo "[d3 $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $*" | tee -a $L >> logs/queue.log; }
busy () { local m; m=$(nvidia-smi -i $1 --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | tr -d ' ')
          [ -z "$m" ] || [ "$m" -gt 10 ]; }                  # nvidia-smi failure counts as busy
if [ ! -f $Q ]; then
  { echo "@train"
    for r in 0 1 2; do echo "code/fit_gpu_batched.py 8 kron 1024 $N $TAG --restart $r --prior S2c"; done
    for fk in "full 512" "full 256" "kron 512" "full 128" "kron 256" "full 64" "kron 128" "full 32" "kron 64" \
              "full 16" "kron 32" "kron 16"; do
      set -- $fk
      [ $1 = full ] && echo "code/fit_gpu.py 8 $fk $N $TAG --prior S2c" || echo "code/fit_gpu_batched.py 8 $fk $N $TAG --prior S2c"
    done
    for r in 0 1 2; do echo "code/fit_gpu_batched.py 8 kron 2048 $N $TAG --restart $r --prior S2c"; done
    for r in 0 1 2; do echo "code/fit_gpu_batched.py 8 kron 4096 $N $TAG --restart $r --prior S2c"; done; } > $Q   # review R2: idle-GPU candidates, never merged unless the edge rule + user decide
fi

train_chain () {                       # 10_SPEC §3d ladder on ONE GPU; writes "<fallback> <stopped_by>" for the post phase
  local g=$1 fb ck s
  for fb in 1 2 3; do
    ck=ckpt/d2sx_S2c_N${N}_a1$([ $fb -gt 1 ] && echo _fb$fb).pt
    CUDA_VISIBLE_DEVICES=$g $P code/run_d2_sx.py --prior S2c --ntrain $N --tag $TAG --fallback $fb --no-gbprime \
      >> logs/d3_gpu$g.log 2>&1
    s=$(CUDA_VISIBLE_DEVICES= $P -c "import torch; print(torch.load('$ck', map_location='cpu', weights_only=False).get('stopped_by'))" 2>/dev/null)
    log "train fallback $fb: stopped_by=${s:-NO_CHECKPOINT} ($ck)"
    [ "$s" = diverged ] && [ $fb -lt 3 ] && { log "§3d: fallback $fb DIVERGED -> fallback $((fb + 1)) on GPU $g"; continue; }
    break
  done
  echo "$fb ${s:-NO_CHECKPOINT}" > logs/d3_train_state.txt
}

worker () {
  local g=$1 job
  while true; do
    busy $g && { log "GPU $g in use by another process -> worker $g stops (no retry)"; break; }
    job=$(flock $Q.lock sh -c "head -n1 $Q; sed -i 1d $Q")
    [ -z "$job" ] && break
    log "GPU $g start: $job"
    if [ "$job" = "@train" ]; then train_chain $g; rc="(train: see d3_train_state.txt)"; else CUDA_VISIBLE_DEVICES=$g $P $job >> logs/d3_gpu$g.log 2>&1; rc=$?; fi
    log "GPU $g done rc=$rc: $job"
  done
}

free=""
for g in $GPUS; do busy $g && log "GPU $g in use at launch -> not used" || free="$free $g"; done
[ -z "$free" ] && { log "ABORT: no free GPU in '$GPUS'"; exit 1; }
git diff --quiet -- code 2>/dev/null || log "WARNING: conf/code has uncommitted changes -- the logged git hash does not describe the code"
log "queue start (git $(git rev-parse --short HEAD 2>/dev/null)), N=$N tag=$TAG GPUs:$free, $(wc -l < $Q) jobs"
for g in $free; do worker $g & done
wait
log "workers done; queue left: $(wc -l < $Q) jobs"

# ---- post phase
CUDA_VISIBLE_DEVICES= $P code/fit_gpu.py 8 kron 1024 $N $TAG --merge --prior S2c >> logs/d3_post.log 2>&1
log "merge kron 1024 rc=$?"
CUDA_VISIBLE_DEVICES= $P - $N $TAG >> logs/d3_post.log 2>&1 <<'EOF'
import sys
sys.path.insert(0, "code")
import runner, arms as A
N, TAG = int(sys.argv[1]), sys.argv[2]
runner._init(TAG)
fits, llv, bstar, kK = A.gmm_selection("D2", "S2c", 8, N)
fam = {f: sorted(K for g, K in fits if g == f) for f in ("full", "kron")}
miss = [f"{f} {K}" for f, Ks in (("full", (16, 32, 64, 128, 256, 512)), ("kron", (16, 32, 64, 128, 256, 512, 1024)))
        for K in Ks if K not in fam[f]]
edge = (kK == max(fam["kron"])) if bstar == "kron" else (int(bstar[3:]) == max(fam["full"]))
print(f"[d3-post] b* = {bstar}" + (f" (kron K={kK})" if bstar == "kron" else "") + f" ll_val {llv[bstar]:.6f}; "
      f"full K {fam['full']} kron K {fam['kron']}; missing {miss or 'none'}; b* at grid edge: {edge}")
sys.exit(4 if miss else 3 if edge else 0)
EOF
rc=$?
log "$(grep '\[d3-post\] b\*' logs/d3_post.log | tail -1 | cut -c11-)"
read fb st < logs/d3_train_state.txt 2>/dev/null
if [ $rc -eq 4 ]; then log "GRID INCOMPLETE -> GB' not run (see logs/d3_post.log)"
elif [ $rc -eq 3 ]; then log "MANUAL: b* is the largest K of its family -> extend K (user decision, 01_RULES:76); GB' deferred;" \
  "kron 2048 candidates ready: $(ls results/gmm_fits_D2_$TAG/fit_S2c_Nr8_kronK2048_n$N.k0r*.npz 2>/dev/null | wc -l)/3" \
  "(merge: code/fit_gpu.py 8 kron 2048 $N $TAG --merge --prior S2c)"
elif [ $rc -ne 0 ]; then log "b* check failed rc=$rc -> GB' not run"
elif [ "$st" != patience ] && [ "$st" != max_epochs ]; then log "training state '$fb $st' -> no GB' (manual: §3d / resume)"
else
  g=$(for x in $free; do busy $x || { echo $x; break; }; done)
  [ -z "$g" ] && { log "no free GPU for GB' -> skipped (run manually)"; log "D3_QUEUE_DONE"; exit 0; }
  CUDA_VISIBLE_DEVICES=$g $P code/run_d2_sx.py --prior S2c --ntrain $N --tag $TAG --fallback $fb >> logs/d3_post.log 2>&1
  log "GB' (fallback $fb, GPU $g) rc=$?: $(grep '\[d2sx\] GMM b\*' logs/d3_post.log | tail -1)"
fi
log "D3_QUEUE_DONE"
