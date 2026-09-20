#!/bin/bash
# 한 줄 상태 요약 (30분 브리핑용)
cd /home/HTJ/t2/conf
TPE=$(( $(wc -l < results/hpo_trials.csv 2>/dev/null || echo 1) - 1 ))
ST=$(( $(wc -l < results/hpo_strat_trials.csv 2>/dev/null || echo 1) - 1 ))
NGPU=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null | wc -l)
~/miniforge3/envs/torch/bin/python - "$TPE" "$ST" "$NGPU" <<'PY'
import csv, math, sys, collections
import numpy as np
tpe, st, ngpu = sys.argv[1], sys.argv[2], sys.argv[3]
def load(p):
    try:
        return [r for r in csv.DictReader(open(p)) if r['gate_score'] and math.isfinite(float(r['gate_score']))]
    except Exception:
        return []
best = ''
t = load('results/hpo_trials.csv')
if t:
    b = min(t, key=lambda r: float(r['gate_score']))
    best = f"TPE최고 {float(b['gate_score']):.3f} ({b['arch']}/{b['param']}/{b['domain']}, GC={float(b['GC']):.4f})"
s = load('results/hpo_strat_trials.csv')
o = collections.defaultdict(list)
for r in s:
    o[r['arch']].append((int(r['trial']), float(r['gate_score'])))
neq = min((len(v) for v in o.values()), default=0)
rank = ''
if neq >= 5:
    by = {k: [g for _, g in sorted(v)[:neq]] for k, v in o.items()}
    rank = ' | 균등n=%d: ' % neq + ', '.join(
        f"{k} {min(v):.2f}/{np.median(v):.2f}" for k, v in sorted(by.items(), key=lambda kv: min(kv[1])))
print(f"[브리핑] GPU {ngpu}/6 가동 | TPE {tpe}/720 | 균등표본 {st}/180 ({dict(sorted((k, len(v)) for k, v in o.items()))}) | {best}{rank}")
PY
