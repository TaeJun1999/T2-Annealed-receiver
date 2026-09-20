#!/bin/bash
# Add an HPO search worker on GPU $G as soon as the rung currently holding it finishes.
set -u
cd /home/HTJ/t2/conf
G=${G:?}; R=${R:?}
until grep -q "done ===" "logs/$R.log" 2>/dev/null; do sleep 30; done
exec ~/miniforge3/envs/torch/bin/python code/hpo.py search --trials 120 --gpu "$G" > "logs/hpo_g$G.log" 2> "logs/hpo_g$G.stderr"
