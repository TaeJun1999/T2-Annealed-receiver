#!/bin/bash
# (NEXT_EXPERIMENTS_S2V16e4 §1, after the design freeze 389e23f4 + §5 + prerequisite code + merge into main)
# C: spatially non-stationary S2v (receive visibility windows), cell C6 16x4, N' = 1.6e5.  Four tags on the SAME trials,
# order ① S2vB16e4 (14 arms, _best) -> ③ S2vPIL (--pilot-arms) -> ④ S2vALD (ALD arms) -> ② S2vB16e4last (14 arms, last-EMA,
# report only).  ① ABORT -> nothing else starts (no genie reference).  Phase 0: fits links for ②③④ -> the S2vB16e4 fits;
# ALD test pilots (CPU) + estimate (GPU, one free GPU).  Then per registration §1 (명령 원문): analysis ①② only,
# run_manifest, guard_report ①②, eval_accept (grid, ckpt ids, genie replay vs ①; ② also --ref-arms all), recovery_ci,
# frontier_ci --recovery vs raw_NR16B16e4, pair_baselines (판정 1·2, X*).  CPU, GPUs hidden.
# Log logs/run_s2v16e4_eval.log, end marker "S2V_EVAL_DONE ok=<n> fail=<n>" (ok=1: every step and integrity passed).
cd /home/HTJ/t2/conf
P=~/miniforge3/envs/torch/bin/python
L=logs/run_s2v16e4_eval.log
log () { echo "[s2veval $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $*" | tee -a $L >> logs/queue.log; }
[ -n "$(git -C /home/HTJ/t2 status --porcelain conf/code Demo)" ] && { log "ABORT: conf/code or Demo dirty"; exit 1; }
BEST=ckpt/d2sx_S2vNR16_N160000_a1_best.pt; LAST=ckpt/d2sx_S2vNR16_N160000_a1.pt; BSHA=fef34e13133004fc; LSHA=9940812e5f7ab689
LL=-58.45384925132457; FD=gmm_fits_D2_S2vB16e4
GRID="full:16,32,64,128,256,512 kron:16,32,64,128,256,512,1024,2048,4096"
[ "$(sha256sum $BEST | cut -c1-16)" = $BSHA ] && [ "$(sha256sum $LAST | cut -c1-16)" = $LSHA ] || { log "ABORT: S2v ckpt sha differs from §5"; exit 1; }
COMMON="--testbed D2 --prior S2v --cell C6 --n 2560 --chunk 40 --ntrain 160000"
log "start (git $(git rev-parse --short HEAD))"
# ---- phase 0
for t in S2vB16e4last S2vPIL S2vALD; do ln -sfn $FD results/gmm_fits_D2_$t; done
[ -f results/ald/pilots_S2vALD_test.npz ] || CUDA_VISIBLE_DEVICES= $P code/ald.py regen --tag S2vALD --prior S2v --cell C6 \
  --fits-tag S2vB16e4 --set test >> $L 2>&1 || { log "ABORT: ALD test regen"; exit 1; }
E=results/ald/ald_S2vALD.npz
if [ ! -f $E ] || [ results/ald/tune_S2vALD.json -nt $E ]; then
  G=$(nvidia-smi --query-gpu=index,memory.used --format=csv,noheader,nounits | awk -F', ' '$2 < 100 {print $1; exit}')
  [ -n "$G" ] || { log "ABORT: no free GPU for the ALD estimate (resume later, no approval needed)"; exit 1; }
  CUDA_VISIBLE_DEVICES=$G $P code/ald.py estimate --tag S2vALD --ckpt $BEST --set test >> $L 2>&1 || { log "ABORT: ALD estimate"; exit 1; }
fi
log "phase 0 done (links, ALD estimate)"
# ---- phase 1 (CPU)
export CUDA_VISIBLE_DEVICES=
run () { $P code/runner.py run $COMMON --tag $1 "${@:2}" > logs/run_D2_$1.log 2>&1 && $P code/run_manifest.py --tag $1 >> $L 2>&1
         local rc=$?; log "$1 run+manifest rc=$rc"; return $rc; }
run S2vB16e4 --stagec-ckpt /home/HTJ/t2/conf/$BEST || { log "ABORT: ① S2vB16e4 failed -- ②③④ not started"; log "S2V_EVAL_DONE ok=0 fail=1"; exit 1; }
$P code/runner.py analysis --testbed D2 --tag S2vB16e4 > logs/analysis_S2vB16e4.log 2>&1; log "analysis ① rc=$?"
run S2vPIL --stagec-ckpt /home/HTJ/t2/conf/$BEST --pilot-arms --arm V1-pilot bstar-pilot R5-genie; R3=$?
run S2vALD --stagec-ckpt /home/HTJ/t2/conf/$BEST --ald-file /home/HTJ/t2/conf/$E --arm ALD-pilot ALDv-pilot R5-genie; R4=$?
run S2vB16e4last --stagec-ckpt /home/HTJ/t2/conf/$LAST; R2=$?
$P code/runner.py analysis --testbed D2 --tag S2vB16e4last > logs/analysis_S2vB16e4last.log 2>&1; log "analysis ② rc=$?"
DP=$($P - <<PY
import re
t = open("results/tables_D2_S2vB16e4.txt").read()
m = re.search(r"M-ours-bstar -> M-ours-dscore-C-V1.*?\n\s*decision SNRs \[([^\]]*)\]", t, re.S)
print(" ".join(x.strip("' ") for x in m.group(1).split(",")) if m and m.group(1).strip() else "")
PY
)
log "decision SNRs (anchor b*, ①): ${DP:-none}"
for T in S2vB16e4 S2vB16e4last; do
  $P code/guard_report.py --raw raw_$T --testbed D2 > results/guard_D2_$T.txt 2>&1
  $P code/recovery_ci.py --raw raw_$T --cell C6 --snrs -3 > results/review_next/recovery_$T.txt 2>&1
  [ -n "$DP" ] && $P code/recovery_ci.py --raw raw_$T --cell C6 --snrs $DP >> results/review_next/recovery_$T.txt 2>&1
done
A=results/review_next/S2vB16e4_accept.txt
$P code/eval_accept.py --prior S2v --nr 16 --bstar kron --kron-K 4096 --ntrain 160000 --ll-val $LL \
  --tag S2vB16e4:best:$BSHA:C6 --tag S2vB16e4last:last:$LSHA:C6 --tag S2vPIL:best:$BSHA:C6 --tag S2vALD:best:$BSHA:C6 \
  --ref-raw raw_S2vB16e4 --fits-dir results/$FD --grid "$GRID" > $A 2>&1; RA=$?
$P code/eval_accept.py --prior S2v --nr 16 --bstar kron --kron-K 4096 --ntrain 160000 --ll-val $LL \
  --tag S2vB16e4last:last:$LSHA:C6 --ref-raw raw_S2vB16e4 --ref-arms all >> $A 2>&1; RB=$?
DIFF=$(grep -o "arms differing \[[^]]*\]" $A | tr -d "'" | sort -u | tr '\n' ' ')
OTHER=$(echo "$DIFF" | tr ' ,[]' '\n' | grep -E "^(M-|R[0-9])" | grep -vE "^M-ours-dscore-C-V(0|1|4|4b)$" | sort -u | tr '\n' ' ')
log "acceptance rc=$RA (all tags, genie replay vs ①) / ② vs ① all arms: $DIFF-> non-Stage-C arms differing: ${OTHER:-none}"
[ -n "$OTHER" ] && { log "INVALID: ② non-Stage-C arms not identical to ①"; RA=1; }
$P code/frontier_ci.py --recovery "raw_S2vB16e4:C6:-3" "raw_NR16B16e4:C6:-3" > results/review_next/recovery_diff_S2vB16e4.txt 2>&1
$P code/frontier_ci.py --recovery "raw_S2vB16e4last:C6:-3" "raw_NR16B16e4:C6:-3" >> results/review_next/recovery_diff_S2vB16e4.txt 2>&1
log "ΔR vs S2 C6 rc=$?"
RP=1
if [ $RA -eq 0 ]; then
  $P code/pair_baselines.py --base raw_S2vB16e4 --pil raw_S2vPIL --ald raw_S2vALD --est S2vALD --cell C6 --prior S2v \
    > results/review_next/pairB_S2vB16e4.txt 2>&1; RP=$?
  log "pair_baselines rc=$RP ($(head -1 results/review_next/pairB_S2vB16e4.txt | cut -c1-150))"
else
  log "INVALID: acceptance failed -> no pair_baselines (registration §1)"
fi
[ $RA -eq 0 ] && [ $RP -eq 0 ] && [ $R2 -eq 0 ] && [ $R3 -eq 0 ] && [ $R4 -eq 0 ] && log "S2V_EVAL_DONE ok=1 fail=0" || log "S2V_EVAL_DONE ok=0 fail=1"
