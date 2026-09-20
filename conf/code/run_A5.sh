#!/bin/bash
# conf/code/run_A5.sh -- Stage A5 driver (conf/04_SPEC_diffusion.md §4).
#
# The ladder is STRICTLY SEQUENTIAL and stops at the FIRST rung that clears GA-GD:
#   00_GOAL §3 A5 ends on "한 칸이 GA~GD PASS, 또는 전 칸 소진".
#   L3 needs L1 and L2's gate scores, L4 needs L3's, L5 needs L3/L4's -- so a later rung is only
#   ever reached because every earlier rung FAILED, and its inputs are therefore always available.
# Every attempt appends a row to conf/LADDER.md whether it passes or fails (01_RULES §5: the failed
# attempts are what show the model was not chosen by looking at the results).
# The judge is the pre-registered gate, never BLER.
set -u
PY=~/miniforge3/envs/torch/bin/python
cd /home/HTJ/t2/conf
TESTBED=${TESTBED:-D1}
GPU=${GPU:-0}
export CUDA_VISIBLE_DEVICES=$GPU

echo "=== A5 ladder | testbed $TESTBED | CUDA_VISIBLE_DEVICES=$GPU | $(date '+%F %T %Z') ==="
nvidia-smi --query-gpu=index,name,memory.used --format=csv,noheader

for RUNG in L1 L2 L3 L4 L5 L6; do
  for A in 1 2 3; do
    echo
    echo "################ $RUNG attempt $A | $(date '+%F %T') ################"
    $PY code/runner.py train --rung "$RUNG" --attempt "$A" --testbed "$TESTBED" --device cuda
    rc=$?
    if [ $rc -ne 0 ]; then echo "!!! train $RUNG a$A exited $rc -- recorded, moving to the next attempt"; continue; fi
    $PY code/runner.py gate --testbed "$TESTBED" --rung "$RUNG" --attempt "$A" --device cuda
    echo "--- gate verdict check ---"
    $PY - "$TESTBED" "$RUNG" "$A" <<'PYEOF'
import sys
sys.path.insert(0, "code")
import score
tb, rung, att = sys.argv[1], sys.argv[2], int(sys.argv[3])
p = score._passing_attempts(tb)
print(f"passing attempts on record for {tb}: {p if p else 'none'}")
sys.exit(0 if any(r == rung and a == att for r, a, *_ in p) else 3)
PYEOF
    if [ $? -eq 0 ]; then
      echo "=== $RUNG attempt $A PASSED the pre-registered gates -> ladder stops here (04_SPEC §4) ==="
      exit 0
    fi
    echo "--- $RUNG attempt $A did not clear the gates; next attempt ---"
  done
  echo "=== $RUNG exhausted its 3 attempts -> next rung ==="
done
echo "=== every rung exhausted without clearing the gates."
echo "    04_SPEC §4: this is reported as a FINDING, not a failure, and the gates are NOT lowered. ==="
exit 1
