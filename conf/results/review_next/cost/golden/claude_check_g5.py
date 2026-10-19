"""Golden G5 (S1-S7) against bench_cost.quantiles / write_results (E4 cost bench, e4-cost worktree; development check, no receiver)."""
import math, sys, tempfile
from pathlib import Path
sys.path.insert(0, "/home/HTJ/t2_wtCost/conf/code")
import bench_cost as B

def rec(run_s, h_call_s, exception="", early=False, nonfinite=False):
    return dict(trial=0, order=0, run_s=run_s, h_s=float(sum(h_call_s)) if h_call_s else float("nan"), h_calls=len(h_call_s),
                forward=0, vjp=0, vjp_batches=0, em_steps=0, iterations=16, exception=exception, early=early, nonfinite=nonfinite,
                h_call_s=list(h_call_s), denoise_s=[], site_s=[], vjp_widths=[])

def table(records):
    d = Path(tempfile.mkdtemp(dir="/tmp/claude-1005/-home-HTJ-t2/ac4d3602-6d72-4574-8052-16040bb635a9/scratchpad/golden_cost/check"))
    B.write_results(None, {}, [("D2", -3, "X", "gmm", 1024, records)], {}, d / "c.txt", d / "c.npz")
    line = [l for l in (d / "c.txt").read_text().splitlines() if l.startswith("D2 | -3 | X |")][0]
    return line

ok = True
def check(name, got, want, tol=1e-9):
    global ok
    g = all((math.isnan(x) and math.isnan(y)) or abs(x - y) <= tol for x, y in zip(got, want)) and len(got) == len(want)
    ok &= g
    print(f"{name}: got {['%.6g' % x for x in got]} want {['%.6g' % x for x in want]} -> {'OK' if g else 'DIFF'}")

# S1: quantiles (returns p25, p50, p75, p90)
check("S1", B.quantiles([3, 1, 4, 1, 5, 9, 2, 6]), [1.75, 3.5, 5.25, 6.9])
# S2: paired per-call sums (the bench's tap pairs denoise_i + site_i; here we feed the paired sums, as h_call_s holds)
check("S2", B.quantiles([2.0 + 0.5, 3.0 + 0.4, 2.5 + 0.6, 4.0 + 0.5]), [2.95, 3.25, 3.675, 4.17])
# S3: two blocks, calls pooled; rx.run median/IQR; share = median of block ratios (table is in ms -> inputs in s * 1e3)
l = table([rec(0.040, [0.001, 0.002, 0.009]), rec(0.030, [0.003, 0.004, 0.005])]); print("  S3 row:", l)
f = l.split(" | ")
rx = [float(x) for x in f[3].replace("[", " ").replace("]", " ").replace(",", " ").split()]
hc = [float(x) for x in f[5].replace("[", " ").replace("]", " ").replace(",", " ").replace(";", " ").split()]
check("S3 rx median/IQR (ms)", rx, [35.0, 32.5, 37.5]); check("S3 H/call median, IQR, p90 (ms)", hc, [3.5, 2.25, 4.75, 7.0])
check("S3 share", [float(f[4].rstrip("%")) / 100], [0.35], 1e-5); check("S3 H/block median (ms)", [float(f[6])], [12.0])
# S4: share = median of block ratios
l = table([rec(1.00, [0.20]), rec(1.20, [0.60]), rec(0.90, [0.30])]); f = l.split(" | ")
check("S4 share (median of block ratios)", [float(f[4].rstrip("%")) / 100], [1 / 3], 1e-5)
rx = [float(x) for x in f[3].replace("[", " ").replace("]", " ").replace(",", " ").split()]
check("S4 rx median/IQR (ms)", rx, [1000.0, 950.0, 1100.0])
# S5: one value
l = table([rec(7.0, [2.1])]); f = l.split(" | ")
rx = [float(x) for x in f[3].replace("[", " ").replace("]", " ").replace(",", " ").split()]
check("S5 rx (ms)", rx, [7000.0, 7000.0, 7000.0]); check("S5 share", [float(f[4].rstrip("%")) / 100], [0.3], 1e-5)
# S6: all blocks raise -> NaN statistics, row kept, exceptions 24
l = table([rec(float("nan"), [], exception="RuntimeError: x") for _ in range(24)]); print("  S6 row:", l)
s6 = "nan" in l.split(" | ")[3] and l.rstrip().endswith("0/24/0/0"); ok &= s6; print(f"S6 row kept, NaN stats, 0 ok / 24 exceptions -> {'OK' if s6 else 'DIFF'}")
# S7: block 2 raised after 5 calls -> excluded; pooled calls only from blocks 1 and 3 (32 values); H calls set {16}
r1, r3 = rec(1.0, [0.01] * 16), rec(1.0, [0.02] * 16)
r2 = rec(float("nan"), [0.5] * 5, exception="RuntimeError: y"); r2["h_calls"] = 5
l = table([r1, r2, r3]); f = l.split(" | "); print("  S7 row:", l)
hc = [float(x) for x in f[5].replace("[", " ").replace("]", " ").replace(",", " ").replace(";", " ").split()]
check("S7 H/call median, IQR, p90 (ms; 32 values)", hc, [15.0, 10.0, 20.0, 20.0]); s7 = f[7].strip() == "16" and l.rstrip().endswith("2/1/0/0")
ok &= s7; print(f"S7 H calls '16' and 2 ok / 1 exception -> {'OK' if s7 else 'DIFF'}")
print("G5", "OK" if ok else "FAIL")
