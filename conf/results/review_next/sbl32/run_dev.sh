#!/bin/bash
# NEXT_EXPERIMENTS_U28NR32SBL §1.2 -- development tuning of SBL-loop in UMi28 C9 (32x4): trials 3840..4159 (n 320) at -3 / 0 / +3 dB,
# arms SBL-loop + R5-genie, every candidate on the SAME trials.  CPU only, NUMA 0 (48 threads, user 2026-10-17 CDT), run from the
# e3-sbl32 worktree.  Candidates run side by side, each on a CPU slice sized by its probe block time (results do not depend on it).
#   bash results/review_next/sbl32/run_dev.sh cold                      (the 8 cold candidates of §1.2 step 2)
#   bash results/review_next/sbl32/run_dev.sh warm <r>,<e> <r>,<e>      (§1.2 step 4: warm variants of the top two cold candidates)
# Log logs/sbl32_dev.log; end line "SBL32DEV_DONE <phase> ok=<n> fail=<n>".
cd /home/HTJ/t2_wtE3/conf || exit 1
P=~/miniforge3/envs/torch/bin/python; export CUDA_VISIBLE_DEVICES=
L=logs/sbl32_dev.log; FULL32=d572e0ac63013a96042a148aa1fceaa6662710ddfdbcfb4a4dd051271704e215
SRC=/home/HTJ/t2/conf/results/gmm_fits_D2_U28NR32GCAPchk/fit_UMi28_Nr32_fullK32_n160000.npz
CPUS=($(seq 0 23) $(seq 96 119))                                   # NUMA 0, 48 threads
declare -A SEC=([4,3]=4.765 [4,10]=12.398 [4,25]=39.051 [8,3]=33.897 [8,10]=43.338 [8,25]=122.003 [16,3]=124.065 [16,10]=295.339)
log () { echo "[sbl32dev $(TZ=America/Chicago date '+%m-%d %H:%M %Z') git $(git rev-parse --short HEAD)] $*" | tee -a $L; }
[ -z "$(git status --porcelain code ../Demo)" ] || { log "ABORT: code/ or Demo/ not clean"; exit 1; }
PHASE=${1:-}
case "$PHASE" in
  cold) W=0; CANDS=("16,10" "16,3" "8,25" "8,10" "8,3" "4,25" "4,10" "4,3") ;;
  warm) W=1; shift; CANDS=("$@"); [ ${#CANDS[@]} = 2 ] || { echo "warm needs two <r>,<e>"; exit 1; } ;;
  *) echo "usage: run_dev.sh cold | warm <r>,<e> <r>,<e>"; exit 1 ;;
esac
for c in "${CANDS[@]}"; do [ -n "${SEC[$c]:-}" ] || { echo "unknown or excluded candidate $c (§1.2 2)"; exit 1; }; done
if [ $W = 1 ]; then                                              # §1.2 4: the warm pair = the cold top two of select_dev_cold.out
  top=$(grep '^TOP2' results/review_next/sbl32/select_dev_cold.out 2>/dev/null | sed 's/.*: //')
  [ "$(echo $top | tr ' ' '\n' | sort | tr '\n' ' ')" = "$(printf '%s\n' "${CANDS[@]}" | sort | tr '\n' ' ')" ] || { echo "warm args (${CANDS[*]}) != TOP2 of select_dev_cold.out ($top)"; exit 1; }
fi
pgrep -af "[r]unner.py run .*--mod" > /dev/null && { log "ABORT: an E5 (QAM16) runner is active -- ask the user for the order"; exit 1; }
# threads per candidate proportional to the probe block time (at least 1), largest first; the slices partition the 48 CPUs
tot=$(for c in "${CANDS[@]}"; do echo ${SEC[$c]}; done | awk '{s += $1} END {print s}')
declare -A NT; used=0
for c in "${CANDS[@]}"; do n=$(awk -v s=${SEC[$c]} -v t=$tot 'BEGIN {n = int(48 * s / t + 0.5); print (n < 1 ? 1 : n)}'); NT[$c]=$n; used=$((used + n)); done
NT[${CANDS[0]}]=$(( ${NT[${CANDS[0]}]} - used + 48 ))              # the most expensive candidate absorbs the rounding
off=0; pids=()
for c in "${CANDS[@]}"; do
  r=${c%,*}; e=${c#*,}; t=U28NR32SBLd_r${r}e${e}$([ $W = 1 ] && echo w)
  set_cpus=$(IFS=,; echo "${CPUS[*]:$off:${NT[$c]}}"); off=$((off + NT[$c]))
  mkdir -p results/gmm_fits_D2_$t
  [ -f results/gmm_fits_D2_$t/fit_UMi28_Nr32_fullK32_n160000.npz ] || cp $SRC results/gmm_fits_D2_$t/
  [ "$(sha256sum results/gmm_fits_D2_$t/fit_UMi28_Nr32_fullK32_n160000.npz | cut -d' ' -f1)" = $FULL32 ] || { log "ABORT: fullK32 sha ($t)"; exit 1; }
  [ "$(ls results/gmm_fits_D2_$t | wc -l)" = 1 ] && [ -z "$(find results/gmm_fits_D2_$t -type l)" ] || { log "ABORT: fits folder of $t"; exit 1; }
  [ -d raw_$t ] && log "resume $t ($(ls raw_$t | wc -l) chunks present)"
  log "start $t on ${NT[$c]} CPUs ($set_cpus)"
  taskset -c $set_cpus $P code/runner.py run --testbed D2 --prior UMi28 --cell C9 --ntrain 160000 --chunk 10 --n 320 --skip0 3840 \
    --snr -3 0 3 --arm SBL-loop R5-genie --sparse-arms $r,$e,1,1,$W --tag $t >> logs/run_D2_$t.log 2>&1 &
  pids+=("$!:$t")
done
ok=0; fail=0
for pt in "${pids[@]}"; do
  wait ${pt%%:*}; rc=$?; log "end ${pt#*:} rc=$rc"; [ $rc = 0 ] && ok=$((ok + 1)) || fail=$((fail + 1)); done
log "SBL32DEV_DONE $PHASE ok=$ok fail=$fail"
exit $fail
