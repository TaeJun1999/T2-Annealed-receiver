#!/bin/bash
cd /home/HTJ/t2/conf
G=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null | wc -l)
D=$( [ -f results/d2_gbprime.csv ] && echo $(( $(wc -l < results/d2_gbprime.csv) - 1 )) || echo 0 )
F=$(grep -c "^  " logs/fit_D2_n4e4.log 2>/dev/null || echo 0)
FD=$(grep -q "EXIT=" logs/fit_D2_n4e4.log 2>/dev/null && echo "완료" || echo "진행중")
echo "[브리핑 $(date '+%m-%d %H:%M')] GPU $G/6 | D2 GB' 완료 $D/6 | GMM N=4e4 적합 $F/180 ($FD)"
[ "$D" -gt 0 ] && tail -n +2 results/d2_gbprime.csv | awk -F, '{printf "   N=%s a%s gmm@%s eq=%s ratio %.3f~%.3f (med %.3f)\n", $1,$2,$3,$4,$10,$11,$12}'
