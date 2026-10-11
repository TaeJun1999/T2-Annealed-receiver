"""rank_probe_2026-10-11/dm_scan_summary.py <dm_scan_raw.log> -- per scenario: BS count, pairs, and the per-BS rank-1 share (min / median / max), the BS with the lowest share and its row."""
import re
import sys
from collections import defaultdict

R = defaultdict(list)
for l in open(sys.argv[1], errors="replace"):
    m = re.match(r"^(\S+)\s+(\d+)\s+(\d+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", l)
    if m:
        R[m.group(1)].append([float(x) for x in m.groups()[1:]])
    elif "FAILED" in l or "not available" in l or "Error" in l:
        print("  !", l.strip()[:160])
print(f"{'scenario':<28} {'BS':>4} {'pairs':>9} {'LoS':>5} {'rank-1 min/med/max':>20}   lowest BS: idx pairs rank-1 <0.80 erank")
for s, rows in R.items():
    r = sorted(rows, key=lambda x: x[4]); a = [x[4] for x in r]; n = sum(x[1] for x in rows)
    print(f"{s:<28} {len(rows):4d} {int(n):9d} {sum(x[2] * x[1] for x in rows) / n:5.2f} {a[0]:6.3f}/{a[len(a) // 2]:5.3f}/{a[-1]:5.3f}   "
          f"{int(r[0][0]):4d} {int(r[0][1]):7d} {r[0][4]:.3f} {r[0][5]:.3f} {r[0][6]:.2f}")
