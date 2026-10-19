#!/bin/bash
# E4 control run (user 10-19 CDT "짧은 대조 실행"): does CPU / memory-node placement explain why the COST1022 UMi32 times
# (CPU 24) were 16-21 % slower than the 10-18 check run (CPU 66-67)?  Development trial 2561 (warm-up 2560), U32 V1 + K4096 + SBL.
cd /home/HTJ/t2 || exit 1
export CUDA_VISIBLE_DEVICES=
P=/home/HTJ/miniforge3/envs/torch/bin/python
O=conf/results/review_next/cost/numa_check; mkdir -p $O
L=conf/logs/cost/numa_check.log
stamp () { TZ=America/Chicago date '+%m-%d %H:%M:%S %Z'; }
nodes () { for n in /sys/devices/system/node/node[0-3]; do printf '%s free %.1fGB  ' ${n##*/} $(awk '/MemFree/{print $4/1048576}' $n/meminfo); done; }
echo "[numa_check $(stamp) git $(git rev-parse --short HEAD) bench $(sha256sum conf/code/bench_cost.py | cut -c1-16)] start; $(nodes)" >> $L
run () {   # tag, launcher ... (taskset / numactl exec python, so $! is the python pid)
  local tag=$1; shift
  "$@" $P -B conf/code/bench_cost.py --cell U32 --tag $tag --trials 1 --gmm k4096 --force --out-dir $O >> $L 2>&1 &
  local pid=$!
  while kill -0 $pid 2>/dev/null; do
    sleep 30
    [ -r /proc/$pid/numa_maps ] && echo "NUMA $tag $(stamp) $(awk '{for(i=1;i<=NF;i++) if($i ~ /^N[0-9]+=/){split($i,a,"=");s[a[1]]+=a[2]}} END{for(k in s) printf "%s=%d ", k, s[k]}' /proc/$pid/numa_maps 2>/dev/null) cpus=$(awk '/Cpus_allowed_list/{print $2}' /proc/$pid/status 2>/dev/null) mems=$(awk '/Mems_allowed_list/{print $2}' /proc/$pid/status 2>/dev/null)" >> $L
  done
  wait $pid; echo "[numa_check $(stamp)] $tag rc=$?; $(nodes)" >> $L
}
run NUMA_a24     taskset -c 24
run NUMA_b6667   taskset -c 66-67
run NUMA_c24m1   numactl --physcpubind=24 --membind=1
run NUMA_d6667m2 numactl --physcpubind=66,67 --membind=2
echo "NUMA_CHECK_DONE $(stamp)" >> $L
