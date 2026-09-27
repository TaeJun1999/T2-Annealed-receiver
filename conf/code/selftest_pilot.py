"""conf/code/selftest_pilot.py RAWDIR -- the pilot-only arms' iteration-1 output must equal their loop arms' (PilotSitePrior
reproduces V1's iteration-0 Module H; bstar-pilot's ep_site call equals M-ours-bstar's iteration 0).  Exit 1 on any difference."""
import glob
import sys

import numpy as np

bad = 0
for f in sorted(glob.glob(f"{sys.argv[1]}/D2_*.npz")):
    z = np.load(f)
    for new, ref in (("V1-pilot", "M-ours-dscore-C-V1"), ("bstar-pilot", "M-ours-bstar")):
        for q in ("blk_err", "ber", "nmse"):
            x, y = z[f"{new}|{q}"][:, 0], z[f"{ref}|{q}"][:, 0]
            same = np.array_equal(np.nan_to_num(x, nan=1e300), np.nan_to_num(y, nan=1e300))
            bad += not same
            print(f"{f.split('/')[-1]} {new} vs {ref} @1 {q}: {'identical' if same else 'DIFFER'}")
sys.exit(1 if bad else 0)
