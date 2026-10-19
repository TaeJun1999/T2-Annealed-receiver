#!/bin/bash
# NEXT_EXPERIMENTS_D2SITEMS §1.3 (E1+, PROMPT_SERVER_E1MS) -- test evaluation of the matched-scalar arm on the headline cell:
#   E1MS_CPUS=<cpu-list> bash code/run_e1ms.sh [--resume]     (tmux, from the main tree after the merge -- the merge only after the V1LS test)
# M-ours-dscore-C-V1ms + R5-genie, D2 C2 (S2), -3 / 0 / +3 dB x test trials 0..2559 = 192 chunks under tag D2SITEMS; V1 and V4 are
# the recorded raw_B16e4k (not re-run).  Then acceptance ① eval_accept (checkpoint id, b*, fits, plan; R5-genie bit-identical to
# raw_B16e4k, every chunk and trial) ② every chunk: run|git = HEAD, meta|ms_arm, the two arms x KEYS_RAW shape (40, 16), 192 chunks;
# only if both are OK: code/e1ms_compare.py.  Log logs/run_e1ms.log, end "E1MS_DONE ok=<n> fail=<n>" (exit = fail count).
# e1ms_s5.txt (§5; tracked; HEAD = the last commit touching it): "FREEZE <commit>" / "WGB <G>" (2 lines).
cd /home/HTJ/t2_wtMS/conf || exit 1
P=~/miniforge3/envs/torch/bin/python; export CUDA_VISIBLE_DEVICES=
L=logs/e1ms_flow.log; REG=results/review_next/NEXT_EXPERIMENTS_D2SITEMS.md; S5=results/review_next/e1ms/e1ms_s5.txt
log () { echo "[e1ms $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $*" | tee -a $L; }
die () { log "ABORT (precondition): $*"; exit 1; }
RESUME=0; [ "${1:-}" = --resume ] && RESUME=1
T=E1MSflow; BASE=/home/HTJ/t2/conf/raw_B16e4k; SRC=results/gmm_fits_D2_B16e4k
CK=/home/HTJ/t2/conf/ckpt/d2sx_N160000_a1.pt; CKSHA=4443921ce8d5c4a11c7cda879a53a66436f43bd76864734a3e6203cfb4b82f29
SHA="bf796b84037e1b3790ed5a6d7917ea2a79f2bee4a9f155f0d3385d856c950997 fit_S2_Nr8_kronK1024_n160000.npz
d4601650a888b4b355565a9010cf0a23499a3e92505e657e2cd79a1c152359f3 fit_S2_Nr8_fullK32_n160000.npz"
H=$(git rev-parse --short HEAD)
RM=0; log "flow test: preconditions and runner skipped"
ok=0; fail=0; [ $RM = 0 ] || fail=$((fail + 1))
step () { local name=$1; shift; if "$@"; then log "$name: OK"; ok=$((ok + 1)); else log "$name: FAILED"; fail=$((fail + 1)); return 1; fi; }
GATE=1
step accept_eval sh -c "$P code/eval_accept.py --tag $T:legacy-last:${CKSHA:0:16}:C2 --prior S2 --ntrain 160000 --kron-K 1024 \
  --ll-val -11.459169831224418 --points C2:-3,0,3 --chunk 40 --n 2560 --ref-raw $BASE > results/review_next/e1ms/${T}_accept.txt 2>&1" || GATE=0
step accept_raw $P -c "
import glob, sys; sys.path.insert(0, 'code'); import numpy as np, common as C
fs = sorted(glob.glob('raw_$T/D2_*.npz')); bad = []
for f in fs:
    z = np.load(f)
    if str(z['run|git']) != '$H': bad.append(f'{f}: run|git {z[\"run|git\"]}')
    if 'meta|ms_arm' not in z.files: bad.append(f'{f}: meta|ms_arm missing')
    arms = sorted({k.split('|')[0] for k in z.files} - {'meta', 'run'})
    if arms != ['M-ours-dscore-C-V1ms', 'R5-genie']: bad.append(f'{f}: arms {arms}')
    for a in ('M-ours-dscore-C-V1ms', 'R5-genie'):
        for k in C.KEYS_RAW:
            if z[f'{a}|{k}'].shape != (40, 16): bad.append(f'{f}: {a}|{k} shape {z[f\"{a}|{k}\"].shape}')
print(f'{len(fs)} chunks (want 192), {len(bad)} problems'); print('\n'.join(bad[:20])); sys.exit(0 if len(fs) == 192 and not bad else 1)" || GATE=0
if [ $GATE = 1 ]; then
  step compare sh -c "$P code/e1ms_compare.py --raw raw_$T --base $BASE --out results/review_next/e1ms/compare_$T.txt >> $L 2>&1"
else log "compare: NOT RUN (acceptance failed -- §1.5: report to the user)"; fail=$((fail + 1)); fi
log "E1MS_DONE ok=$ok fail=$fail"
exit $fail
