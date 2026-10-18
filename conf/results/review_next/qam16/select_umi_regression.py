"""Read-only selection of the least-cost SNR by old per-SNR median chunk wall time."""
from pathlib import Path
import json,re,statistics
p=Path('/home/HTJ/t2/conf/logs/run_D2_U28B16e4.log')
values={}
for line in p.read_text().splitlines():
    m=re.search(r'snr(-?\d+)_skip\d+_n40.npz\s+\((\d+) s\)',line)
    if m:values.setdefault(int(m[1]),[]).append(int(m[2]))
costs={s:dict(n=len(v),median=statistics.median(v),minimum=min(v)) for s,v in sorted(values.items())}
selected=min(costs,key=lambda s:costs[s]['median'])
print(json.dumps(dict(source=str(p),selected_snr=selected,rule='minimum median of all old n40 chunk times per SNR',costs=costs),indent=2))
