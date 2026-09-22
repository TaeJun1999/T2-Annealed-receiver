#!/bin/bash
# (10_SPEC_stageC §6e) gate each finished lambda-sweep checkpoint on D1 as soon as its training stops.
# Runs on GPU 0 (freed when the lambda=0.1 run exits); results -> results/gate_D1_L<lam>.txt, LADDER_L<lam>.md.
cd /home/HTJ/t2/conf; P=~/miniforge3/envs/torch/bin/python
gate_one () {  # $1 = lambda, $2 = log, $3 = ckpt, $4 = gpu
  until grep -qE "stopped_by=" "$2"; do sleep 120; done
  echo "[gate-L$1 $(TZ=Asia/Seoul date '+%H:%M') training stopped: $(grep -oE 'stopped_by=[a-z_]+' $2 | tail -1) -> gate on GPU $4]" >> logs/queue.log
  CUDA_VISIBLE_DEVICES=$4 $P code/runner.py gate --testbed D1 --ckpt /home/HTJ/t2/conf/$3 --tag L$1 >> logs/gate_L$1.log 2>&1
  echo "[gate-L$1 $(TZ=Asia/Seoul date '+%H:%M') done: $(grep -oE 'VERDICT.*' results/gate_D1_L$1.txt | tail -1)]" >> logs/queue.log
}
gate_one 0.1  logs/train_V3_D1_N160000_a2_lam0.1.log  ckpt/sx_V3_N160000_D1_a2_lam0.1.pt 0 &
gate_one 0.01 logs/train_V3_D1_N160000_a1_lam0.01.log ckpt/sx_V3_N160000_D1_a1_lam0.01.pt 1 &
wait
