#!/usr/bin/env bash
# Sequential development checks. No receiver worker pool, no test raw access.
set -euo pipefail
cd /home/HTJ/t2_wtCost
export CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
stamp=20261018_222512_CDT
phase=${1:-all}
[[ "$phase" == all || "$phase" == guards || "$phase" == measure ]] || exit 2
out=conf/results/review_next/cost
log=conf/logs/cost/verify_${stamp}_${phase}.log
err=conf/logs/cost/verify_${stamp}_${phase}.err
if [[ -e "$log" || -e "$err" ]]; then
    echo "Refusing existing log" >&2
    exit 2
fi
exec > >(tee "$log") 2> >(tee "$err" >&2)
py=/home/HTJ/miniforge3/envs/torch/bin/python
runpy() { taskset -c 66-67 "$py" -B "$@"; }
TZ=America/Chicago date '+%Y-%m-%d %H:%M:%S %Z'
git rev-parse HEAD
git status --short
runpy "$out/check_cost_${stamp}.py"

if [[ "$phase" != measure ]]; then
# Use a small, deliberately truncated copy, never modify the source checkpoint.
runpy - <<'PY'
from pathlib import Path
src = Path('/home/HTJ/t2/conf/ckpt/d2sx_N160000_a1.pt')
dst = Path('conf/results/review_next/cost/bad_checkpoint_20261018_222512_CDT.pt')
with src.open('rb') as f, dst.open('xb') as g:
    g.write(f.read(128))
print('CORRUPTION_FIXTURE', dst, dst.stat().st_size)
PY
set +e
runpy conf/code/bench_cost.py --cell D2 --tag bad_${stamp} --check-assets-only \
    --checkpoint "$out/bad_checkpoint_${stamp}.pt"
rc=$?
set -e
[[ "$rc" == 2 ]] || { echo "Hash guard did not reject: $rc"; exit 1; }
echo "HASH_MISMATCH_REJECTION rc=$rc PASS"

set +e
runpy conf/code/bench_cost.py --cell D2 --tag busy_${stamp} --trials 1
rc=$?
set -e
[[ "$rc" == 2 ]] || { echo "Concurrent-load guard was not exercised: $rc"; exit 1; }
echo "BUSY_WITHOUT_FORCE_REJECTION rc=$rc PASS"
fi
if [[ "$phase" == guards ]]; then
    TZ=America/Chicago date '+%Y-%m-%d %H:%M:%S %Z'
    echo "COST_GUARDS_DONE"
    exit 0
fi

runpy conf/code/bench_cost.py --cell D2 --tag D2_${stamp} --trials 1 --ms-arm --force --verify-tap
runpy conf/code/bench_cost.py --cell U32 --tag U32_${stamp} --trials 1 --gmm both --force --verify-tap
runpy "$out/check_cost_${stamp}.py" "$out/cost_D2_${stamp}.npz" "$out/cost_U32_${stamp}.npz"

set +e
runpy conf/code/bench_cost.py --cell D2 --tag D2_${stamp} --trials 1 --force
rc=$?
set -e
[[ "$rc" == 2 ]] || { echo "Overwrite guard did not reject: $rc"; exit 1; }
echo "EXISTING_OUTPUT_REJECTION rc=$rc PASS"
TZ=America/Chicago date '+%Y-%m-%d %H:%M:%S %Z'
echo "COST_CHECKS_DONE"
