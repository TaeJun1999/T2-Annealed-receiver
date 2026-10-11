"""scratch diagnostic (report-only, not registered): is the high Perfect-CSI BLER on DMC a channel-rank effect?
Replays the trial stream (as code/dmc_leak_strata.py does) to get each test trial's channel H, then tabulates the R5-genie
BLER@16 of raw_DMCB16e4 by (a) the energy share of the largest singular value and (b) the testbed's Gaussian MI
sum log2(1 + sv * snr) (code/testbed_dm.py outage()).  Rate needed: 42 info bits / 12 data uses = 3.5 bit per use."""
import os, sys
sys.path.insert(0, "/home/HTJ/t2/conf/code")
import common as C
import numpy as np
import runner
from analysis import load_raw
from recovery_ci import fails

runner._init("DMCB16e4")
c = C.CELLS["C2"]
data, _, _ = load_raw("D2", root=os.path.join(C.CONF, "raw_DMCB16e4"))
for snr in (-3.0, 9.0, 15.0):
    P = runner.build_point("D2", "C2", "DMC", snr, 160000)
    code, gen, first = P["code"], P["gen"], P["arms"]["R5-genie"]
    g = fails(data, "C2", snr, "R5-genie"); v = fails(data, "C2", snr, "M-ours-dscore-C-V1"); b = fails(data, "C2", snr, "M-ours-bstar")
    rng = C.trial_rng("D2", "DMC", c["Nr"], c["T"], c["Tp"], snr)
    sv = np.empty((len(g), c["Nt"]))
    for tr in range(len(g)):
        H = gen.sample(rng); u = rng.integers(0, 2, code.K); perm = rng.permutation(code.Ns); first.transmit(u, perm, H, rng)
        sv[tr] = np.linalg.svd(H, compute_uv=False) ** 2
    share = sv[:, 0] / sv.sum(1)
    mi = np.log2(1 + sv * 10 ** (snr / 10)).sum(1)
    print(f"\n=== {snr:+.0f} dB  n={len(g)}  genie BLER {g.mean():.3f}   ||H||_F^2 mean {sv.sum(1).mean():.2f} (min {sv.sum(1).min():.2f}, max {sv.sum(1).max():.2f})")
    print("  by energy share of the largest singular value:")
    for lo, hi in ((0.95, 1.01), (0.8, 0.95), (0.6, 0.8), (0.0, 0.6)):
        m = (share >= lo) & (share < hi)
        print(f"    share [{lo:.2f}, {min(hi,1):.2f})  n={m.sum():5d} ({m.mean():.3f})  BLER genie {g[m].mean():.3f}  V1 {v[m].mean():.3f}  b* {b[m].mean():.3f}")
    print("  by Gaussian MI [bit/use] (testbed_dm.outage convention):")
    for lo, hi in ((0, 3.5), (3.5, 5), (5, 7), (7, 10), (10, 99)):
        m = (mi >= lo) & (mi < hi)
        if m.sum():
            print(f"    MI [{lo:4.1f}, {hi:4.1f})  n={m.sum():5d} ({m.mean():.3f})  BLER genie {g[m].mean():.3f}  V1 {v[m].mean():.3f}  b* {b[m].mean():.3f}")
