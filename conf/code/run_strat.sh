#!/bin/bash
# Equal-n, random-sampled architecture comparison. One GPU works through its assigned architectures.
set -u
cd /home/HTJ/t2/conf
G=${G:?}; N=${N:-30}
for A in $ARCHS; do
  echo "=== strat $A on gpu $G ($N trials) | $(date '+%F %T') ==="
  ~/miniforge3/envs/torch/bin/python code/hpo.py strat --arch "$A" --trials "$N" --gpu "$G"
done
echo "=== gpu $G strat done ==="
