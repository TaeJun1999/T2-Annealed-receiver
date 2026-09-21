#!/bin/bash
# 잔여 실행: D2 sanity 셀, D1 체제 셀, headline n>=2560 (00_GOAL §4 DoD 8)
set -u
PY=~/miniforge3/envs/torch/bin/python
cd /home/HTJ/t2/conf
echo "### 1/4 D2 C3/C4 (4x4 sanity) $(date '+%T')"
$PY code/runner.py run --testbed D2 --cell C3 C4 --n 640 --chunk 40
echo "### 2/4 D1 C5 (Tp=3, 체제 곡선을 두 testbed 모두에) $(date '+%T')"
$PY code/runner.py run --testbed D1 --cell C5 --n 640 --chunk 40
echo "### 3/4 D2 C1 headline 2점 n=2560 $(date '+%T')"
$PY code/runner.py run --testbed D2 --cell C1 --snr 6 9 --n 2560 --chunk 40
echo "### 4/4 D2 C2 headline 2점 n=2560 $(date '+%T')"
$PY code/runner.py run --testbed D2 --cell C2 --snr -3 0 --n 2560 --chunk 40
echo "### 완료 $(date '+%T')"
