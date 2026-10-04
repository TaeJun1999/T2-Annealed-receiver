#!/bin/bash
# N-scaling (NSCALE; user decisions 2026-10-04 CDT: "A2 + C6 6.4e5" + report-only kron 8192 at D2 C2 6.4e5, long training approved).
# GPU work only, NO BLER: appends jobs to the unified scheduler queue (~/t2_wtS/conf/code/gpu_sched.sh, tmux gpusched).  That
# scheduler cds into ~/t2_wtS/conf, so every command here runs in THIS tree via env -C and logs to absolute paths.
#   GMM grids (frozen runner-fit protocol, fit_gpu.py): D2 C2 (Nr 8) N' = 6.4e5 (B64e4) and 1.28e6 (B128e4), D2 C6 (Nr 16)
#   N' = 6.4e5 (NR16B64e4): full 16..512 (4 kappa x 3 restarts, one job each), kron 16..512 (one job each), kron 1024/2048/4096
#   per restart + CPU merge.  kron fits use the batched exact M-step (FIT_KRON_BATCHED=1) only after em_batched_check_nr.py PASSES
#   for that (Nr, N') -- the WAIT file exists only on exit 0.  Grid cap 4096 (no edge rule: b* is expected at the cap -> Q-K).
#   Report-only kron 8192 at Nr 8 N' 6.4e5 goes to its own dir (tag K8B64e4) so it never enters the B64e4 b* selection
#   (arms.D2_KS contains 8192).
#   Trainings (frozen recipes, attempt 1, GB' later with the final grid): V1 D2 6.4e5 / 1.28e6 (run_d2_sx.py), V1 C6 6.4e5
#   (train_nr16.py), D1 siblings 6.4e5 / 1.28e6 (run_samplecx.py, + D1 gate).
# Priorities: checks 95 > V1 90 > kron 4096 restarts 85 > D1 70 > rest of the grid 50 > 8192 40 (longest jobs first).
DRY=$1; M=/home/HTJ/t2/conf; P=/home/HTJ/miniforge3/envs/torch/bin/python; Q=/home/HTJ/t2_wtS/conf/logs/gpuq.txt
R=$M/results; LG=$M/logs/nscale; mkdir -p $LG
J=$(mktemp)
job () { echo "$*" >> $J; }                                         # <prio> <kind> <label> <command...>
run () { echo "env -C $M $P code/$1 > $LG/$2.log 2>&1"; }          # $1 = script + args, $2 = log name
brun () { echo "env -C $M FIT_KRON_BATCHED=1 $P code/$1 > $LG/$2.log 2>&1"; }

for cfg in "8 640000" "8 1280000" "16 640000"; do set -- $cfg
  job 95 GPU chk${1}_$2 "$(run "em_batched_check_nr.py --nr $1 --ntrain $2" chk_nr$1_n$2) && touch $LG/bpass_nr$1_n$2"; done
job 90 GPU v1d2n128e4 "$(run "run_d2_sx.py --ntrain 1280000 --no-gbprime" v1_d2_n1280000)"
job 90 GPU v1d2n64e4  "$(run "run_d2_sx.py --ntrain 640000 --no-gbprime" v1_d2_n640000)"
job 90 GPU v1c6n64e4  "$(run "train_nr16.py --nr 16 --ntrain 640000 --no-gbprime" v1_c6_n640000)"
job 70 GPU d1n128e4   "$(run "run_samplecx.py 1280000" d1_n1280000)"
job 70 GPU d1n64e4    "$(run "run_samplecx.py 640000" d1_n640000)"

grid () {  # $1 Nr, $2 N', $3 tag
  local nr=$1 n=$2 t=$3 W="WAIT:$LG/bpass_nr$1_n$2:1"
  for K in 4096 2048 1024; do local pr=$([ $K = 4096 ] && echo 85 || echo 50)
    for r in 0 1 2; do job $pr $W:GPU $t$K$r "$(brun "fit_gpu.py $nr kron $K $n $t --restart $r" fit_${t}_kron${K}_r$r)"; done
    job 50 "WAIT:$R/gmm_fits_D2_$t/fit_S2_Nr${nr}_kronK${K}_n$n.k0r[012].npz:3:CPU" m$t$K \
        "$(run "fit_gpu.py $nr kron $K $n $t --merge" fit_${t}_kron${K}_merge)"; done
  for K in 512 256 128 64 32 16; do
    job 50 GPU ${t}f$K "$(run "fit_gpu.py $nr full $K $n $t" fit_${t}_full$K)"
    job 50 $W:GPU ${t}k$K "$(brun "fit_gpu.py $nr kron $K $n $t" fit_${t}_kron$K)"; done; }
grid 8 1280000 B128e4
grid 16 640000 NR16B64e4
grid 8 640000 B64e4
for r in 0 1 2; do job 40 WAIT:$LG/bpass_nr8_n640000:1:GPU K8B64e4$r \
  "$(brun "fit_gpu.py 8 kron 8192 640000 K8B64e4 --restart $r" fit_K8B64e4_kron8192_r$r)"; done
job 40 "WAIT:$R/gmm_fits_D2_K8B64e4/fit_S2_Nr8_kronK8192_n640000.k0r[012].npz:3:CPU" mK8B64e4 \
    "$(run "fit_gpu.py 8 kron 8192 640000 K8B64e4 --merge" fit_K8B64e4_kron8192_merge)"

[ "$DRY" = "--dry" ] && { cat $J; rm $J; exit 0; }
flock $Q.lock sh -c "cat $J >> $Q"; echo "[nscale $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] queued $(wc -l < $J) jobs on gpuq (git $(git -C $M rev-parse --short HEAD))" | tee -a $M/logs/queue.log
rm $J
