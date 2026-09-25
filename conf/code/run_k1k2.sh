#!/bin/bash
# (NEXT_EXPERIMENTS_K1K2 v2 §3, after the freeze commit) K2 then K1, CPU only, in the registered order.
#   pre-checks (§2.1): (a) C1 -3 dB dev 2560..2599: driver V1 / b* / bstar-scalar blk_err@16 == p1_cavity <arm>|fail, 40/40
#                      (b) C2 -3 dB dev 2560..2599: V1-edge / V1-clamp bit-identical to V1 (n_oog 0) and the driver's
#                          V1 / b* / gmmB-scorew-eta / genie bit-identical to raw_review_next_A2
#   K2: C1 -3 dB 3200..4479 (primary), C1 0 dB 2560..3199, C5 -6 dB 2560..3199   -> raw_review_next_K2, K2_report.txt
#   K1: C2 -3 dB 3200..4479, C5 -3 dB 3200..3839 (BR-S + V1 + b* + genie)          -> raw_review_next_K1, K1_report.txt
# Refuses a dirty conf/code tree, an open C6 evaluation window (run_nr16b_eval.sh running), or existing K raw dirs.
set -o pipefail
cd /home/HTJ/t2/conf
export CUDA_VISIBLE_DEVICES=""
P=~/miniforge3/envs/torch/bin/python
L=logs/review_next/run_k1k2.log
log () { echo "[k1k2 $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $*" | tee -a $L >> logs/queue.log; }
abort () { log "ABORT: $*"; exit 1; }
[ -n "$(git -C /home/HTJ/t2 status --porcelain conf/code)" ] && abort "conf/code dirty"
pgrep -f run_nr16b_eval.sh > /dev/null && abort "C6 evaluation window (run_nr16b_eval.sh) is open"
{ [ -e raw_review_next_K2 ] || [ -e raw_review_next_K1 ]; } && abort "raw_review_next_K1/K2 already exist"
log "start (git $(git rev-parse --short HEAD))"
K2ARMS="M-ours-dscore-C-V1 V1-edge V1-clamp M-ours-bstar M-ours-bstar-scalar gmmB-scorew-eta R5-genie"
K1ARMS="BR-S M-ours-dscore-C-V1 M-ours-bstar R5-genie"
SHA=4443921ce8d5c4a1
nfiles () { ls $1/D2_$2_*_snr$3_skip*_n*.npz 2>/dev/null | wc -l; }
# ---- pre-checks (already-recorded trials only; outputs kept under conf/)
rm -rf raw_review_next_K2pre_c1 raw_review_next_K2pre_c2
$P code/diag_prior_swap.py run --cell C1 --snr -3 --skip0 2560 --n 40 --chunk 10 --jobs 4 --arms M-ours-dscore-C-V1 M-ours-bstar M-ours-bstar-scalar --out raw_review_next_K2pre_c1 > logs/review_next/k2_pre_c1.log 2>&1 || abort "pre-check (a) run failed"
$P code/diag_prior_swap.py check-cavity --out raw_review_next_K2pre_c1 --cell C1 --snr -3 >> logs/review_next/k2_pre_c1.log 2>&1 || abort "pre-check (a) failed"
$P code/diag_prior_swap.py run --cell C2 --snr -3 --skip0 2560 --n 40 --chunk 10 --jobs 4 --arms M-ours-dscore-C-V1 V1-edge V1-clamp M-ours-bstar gmmB-scorew-eta R5-genie --out raw_review_next_K2pre_c2 > logs/review_next/k2_pre_c2.log 2>&1 || abort "pre-check (b) run failed"
$P - <<EOF >> logs/review_next/k2_pre_c2.log 2>&1 || abort "pre-check (b) V1-edge/clamp identity failed"
import numpy as np, glob, sys
ok = True
for f in sorted(glob.glob("raw_review_next_K2pre_c2/*.npz")):
    d = np.load(f)
    for v in ("V1-clamp", "V1-edge"):
        same = all(np.array_equal(d[f"{v}|{q}"], d[f"M-ours-dscore-C-V1|{q}"], equal_nan=True) for q in ("blk_err", "ber", "nmse", "tauL_gmean", "alphaD"))
        ok &= bool(same) and d[f"{v}|n_oog"].sum() == 0
        print(f"pre-check (b) {f[-26:]} {v} == V1: {same}, n_oog {d[f'{v}|n_oog'].sum()}")
sys.exit(0 if ok else 1)
EOF
$P code/diag_prior_swap.py check --out raw_review_next_K2pre_c2 --ref raw_review_next_A2 --cell C2 --snr -3 >> logs/review_next/k2_pre_c2.log 2>&1 || abort "pre-check (b) A2 identity failed"
log "pre-checks (a)(b) PASS"
# ---- K2
$P code/diag_prior_swap.py run --cell C1 --snr -3 --skip0 3200 --n 1280 --chunk 10 --arms $K2ARMS --out raw_review_next_K2 2>&1 | tee logs/review_next/k2_C1_m3.log > /dev/null || abort "K2 C1 -3 dB run failed"
[ "$(nfiles raw_review_next_K2 C1 -3)" = 128 ] || abort "K2 C1 -3 dB: $(nfiles raw_review_next_K2 C1 -3) chunks, expected 128"
log "K2 C1 -3 dB done"
$P code/diag_prior_swap.py run --cell C1 --snr 0 --skip0 2560 --n 640 --chunk 10 --arms $K2ARMS --out raw_review_next_K2 2>&1 | tee logs/review_next/k2_C1_p0.log > /dev/null || abort "K2 C1 0 dB run failed"
$P code/diag_prior_swap.py run --cell C5 --snr -6 --skip0 2560 --n 640 --chunk 10 --arms $K2ARMS --out raw_review_next_K2 2>&1 | tee logs/review_next/k2_C5_m6.log > /dev/null || abort "K2 C5 -6 dB run failed"
[ "$(nfiles raw_review_next_K2 C1 0)" = 64 ] && [ "$(nfiles raw_review_next_K2 C5 -6)" = 64 ] || abort "K2 report points: chunk counts $(nfiles raw_review_next_K2 C1 0) / $(nfiles raw_review_next_K2 C5 -6), expected 64 / 64"
log "K2 report points done"
PAIRS="M-ours-bstar>V1-edge M-ours-dscore-C-V1>V1-edge gmmB-scorew-eta>V1-edge M-ours-bstar-scalar>V1-edge M-ours-bstar>V1-clamp M-ours-dscore-C-V1>V1-clamp gmmB-scorew-eta>V1-clamp M-ours-bstar-scalar>V1-clamp V1-clamp>V1-edge M-ours-bstar>M-ours-dscore-C-V1"
rm -f results/review_next/K2_report.txt
$P code/diag_prior_swap.py report --out raw_review_next_K2 --cell C1 --snr -3 --skip0 3200 --n 1280 --chunk 10 --ckpt-sha $SHA --pairs $PAIRS --save K2_report.txt >> $L 2>&1 || log "K2 C1 -3 dB report: acceptance FAILED (see K2_report.txt)"
$P code/diag_prior_swap.py report --out raw_review_next_K2 --cell C1 --snr 0 --skip0 2560 --n 640 --chunk 10 --ckpt-sha $SHA --pairs $PAIRS --save K2_report.txt >> $L 2>&1 || log "K2 C1 0 dB report: acceptance FAILED"
$P code/diag_prior_swap.py report --out raw_review_next_K2 --cell C5 --snr -6 --skip0 2560 --n 640 --chunk 10 --ckpt-sha $SHA --pairs $PAIRS --save K2_report.txt >> $L 2>&1 || log "K2 C5 -6 dB report: acceptance FAILED"
# ---- K1
$P code/diag_prior_swap.py run --cell C2 --snr -3 --skip0 3200 --n 1280 --chunk 20 --arms $K1ARMS --out raw_review_next_K1 2>&1 | tee logs/review_next/k1_C2_m3.log > /dev/null || abort "K1 C2 -3 dB run failed"
$P code/diag_prior_swap.py run --cell C5 --snr -3 --skip0 3200 --n 640 --chunk 20 --arms $K1ARMS --out raw_review_next_K1 2>&1 | tee logs/review_next/k1_C5_m3.log > /dev/null || abort "K1 C5 -3 dB run failed"
[ "$(nfiles raw_review_next_K1 C2 -3)" = 64 ] && [ "$(nfiles raw_review_next_K1 C5 -3)" = 32 ] || abort "K1: chunk counts $(nfiles raw_review_next_K1 C2 -3) / $(nfiles raw_review_next_K1 C5 -3), expected 64 / 32"
log "K1 done"
$P code/k1_report.py --save K1_report.txt >> $L 2>&1 || log "K1 report failed"
log "K1K2_DONE"
