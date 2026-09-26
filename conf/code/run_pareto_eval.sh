#!/bin/bash
# (NEXT_EXPERIMENTS_PARETO §1, after §5 is committed) Tp >= Nt Pareto cells on the TEST set with the HEADLINE checkpoint
# and the HEADLINE fits (link gmm_fits_D2_PARB16e4 -> gmm_fits_D2_B16e4k): CPU receiver, all arms,
#   C7 (Tp=6) and C8 (Tp=8) on the widened grid -9..15 (common.CELLS), then the single C2 -6 dB point (--snr -6),
# all under ONE tag PARB16e4; then analysis + run_manifest + guard_report, recovery_ci (C7, C8 at -3 0 3 -- the decision
# points are re-read from the analysis afterwards), eval_accept (C2 -6 replayed against raw_B1e4lo's R5-genie) and
# frontier_ci (registered unpaired comparisons P-a / P-b and the report-only goodput envelope).
cd /home/HTJ/t2/conf
P=~/miniforge3/envs/torch/bin/python
TAG=PARB16e4; L=logs/run_pareto_eval.log
log () { echo "[pareto $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $*" | tee -a $L >> logs/queue.log; }
[ -n "$(git -C /home/HTJ/t2 status --porcelain conf/code)" ] && { log "ABORT: conf/code dirty"; exit 1; }
[ -L results/gmm_fits_D2_$TAG ] || { log "ABORT: fits link gmm_fits_D2_$TAG missing"; exit 1; }
CK=/home/HTJ/t2/conf/ckpt/d2sx_N160000_a1.pt
[ "$(sha256sum $CK | cut -c1-16)" = "4443921ce8d5c4a1" ] || { log "ABORT: headline checkpoint sha differs"; exit 1; }
log "start (git $(git rev-parse --short HEAD))"
# (0) receiver regression check (NEXT_EXPERIMENTS_PARETO §1): C2 -3 dB chunk 0 (trials 0..39, already observed in
# raw_B16e4k) re-run under the CURRENT code with the headline checkpoint and fits, tag PARB16e4chk (link -> B16e4k);
# every arm x KEYS_RAW @1..16 must be bit-identical to raw_B16e4k, otherwise nothing else runs.
[ -L results/gmm_fits_D2_${TAG}chk ] || { log "ABORT: fits link gmm_fits_D2_${TAG}chk missing"; exit 1; }
$P code/runner.py run --testbed D2 --prior S2 --cell C2 --snr -3 --n 40 --chunk 40 --ntrain 160000 --stagec-ckpt $CK \
  --tag ${TAG}chk > logs/run_D2_${TAG}chk.log 2>&1 || { log "ABORT: regression run failed"; exit 1; }
$P code/eval_accept.py --tag ${TAG}chk:legacy-last:4443921ce8d5c4a1:C2 --points C2:-3 --n 40 --ntrain 160000 --kron-K 1024 \
  --ll-val -11.459169831224418 --ref-raw raw_B16e4k --ref-arms all > results/review_next/${TAG}chk_accept.txt 2>&1
RC=$?; log "regression check rc=$RC ($(head -1 results/review_next/${TAG}chk_accept.txt))"
[ $RC -eq 0 ] || { log "ABORT: receiver regression check FAILED -- no Pareto run (record the cause, decide before re-run)"; exit 1; }
COMMON="--testbed D2 --prior S2 --n 2560 --chunk 40 --ntrain 160000 --stagec-ckpt $CK --tag $TAG"
$P code/runner.py run $COMMON --cell C7 C8 > logs/run_D2_${TAG}.log 2>&1 || { log "ABORT: run C7 C8 failed"; exit 1; }
log "run C7 C8 done"
$P code/runner.py run $COMMON --cell C2 --snr -6 > logs/run_D2_${TAG}_C2m6.log 2>&1 || { log "ABORT: run C2 -6 failed"; exit 1; }
log "run C2 -6 done"
$P code/runner.py analysis --testbed D2 --tag $TAG > logs/analysis_$TAG.log 2>&1; log "analysis rc=$?"
$P code/run_manifest.py --tag $TAG >> $L 2>&1
$P code/guard_report.py --raw raw_$TAG --testbed D2 > results/guard_D2_$TAG.txt 2>&1
# recovery R at -3 dB (primary) and at the pair's decision SNRs as analysis printed them per cell (anchor b*; never by hand)
for CELL in C7 C8; do
  DP=$($P - <<PY
import re
t = open("results/tables_D2_$TAG.txt").read()
blk = t.split("--- cell $CELL  prior")[1] if "--- cell $CELL  prior" in t else ""
m = re.search(r"M-ours-bstar -> M-ours-dscore-C-V1.*?\n\s*decision SNRs \[([^\]]*)\]", blk, re.S)
print(" ".join(x.strip("' ") for x in m.group(1).split(",")) if m and m.group(1).strip() else "")
PY
)
  log "decision SNRs $CELL (anchor b*): ${DP:-none}"
  $P code/recovery_ci.py --raw raw_$TAG --cell $CELL --snrs -3 > results/review_next/recovery_${TAG}_$CELL.txt 2>&1
  [ -n "$DP" ] && $P code/recovery_ci.py --raw raw_$TAG --cell $CELL --snrs $DP >> results/review_next/recovery_${TAG}_$CELL.txt 2>&1
done
$P code/eval_accept.py --tag $TAG:legacy-last:4443921ce8d5c4a1:C2,C7,C8 --points C2:-6 --ntrain 160000 --kron-K 1024 \
  --ll-val -11.459169831224418 --ref-raw raw_B1e4lo --ref-cells C2 --fits-dir results/gmm_fits_D2_$TAG \
  --cand-dir results/gmm_fits_D2_K1024n160000 --grid "full:16,32,64,128,256,512 kron:16,32,64,128,256,512,1024" \
  > results/review_next/${TAG}_accept.txt 2>&1
log "acceptance rc=$? ($(head -1 results/review_next/${TAG}_accept.txt))"
$P code/frontier_ci.py \
  --pair "V1_C2=raw_B16e4k+raw_$TAG:C2:M-ours-dscore-C-V1" "bstar_C7=raw_$TAG:C7:M-ours-bstar" \
  --pair "V1_C2=raw_B16e4k+raw_$TAG:C2:M-ours-dscore-C-V1" "bstar_C8=raw_$TAG:C8:M-ours-bstar" \
  --pair "V1_C2=raw_B16e4k+raw_$TAG:C2:M-ours-dscore-C-V1" "V1_C7=raw_$TAG:C7:M-ours-dscore-C-V1" \
  --pair "V1_C2=raw_B16e4k+raw_$TAG:C2:M-ours-dscore-C-V1" "V1_C8=raw_$TAG:C8:M-ours-dscore-C-V1" \
  --pair "bstar_C2=raw_B16e4k+raw_$TAG:C2:M-ours-bstar" "bstar_C7=raw_$TAG:C7:M-ours-bstar" \
  --pair "bstar_C2=raw_B16e4k+raw_$TAG:C2:M-ours-bstar" "bstar_C8=raw_$TAG:C8:M-ours-bstar" \
  --pair "genie_C2=raw_B16e4k+raw_$TAG:C2:R5-genie" "genie_C7=raw_$TAG:C7:R5-genie" \
  --pair "genie_C2=raw_B16e4k+raw_$TAG:C2:R5-genie" "genie_C8=raw_$TAG:C8:R5-genie" \
  --goodput raw_B16e4k+raw_$TAG:C2 raw_$TAG:C7 raw_$TAG:C8 --arms M-ours-bstar M-ours-dscore-C-V1 R5-genie R2-ours-G \
  > results/review_next/frontier_$TAG.txt 2>&1
log "frontier rc=$?"
log "PARETO_EVAL_DONE"
