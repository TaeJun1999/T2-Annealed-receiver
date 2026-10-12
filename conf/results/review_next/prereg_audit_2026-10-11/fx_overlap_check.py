#!/usr/bin/env python
"""fx_overlap_check.py -- NEXT_EXPERIMENTS_FIGHSX16e4 §3 prediction 8 (the author's own check; the record audit repeats it
independently): the first 20480 trials (chunks skip 10000..30440) of every n = 81920 raw raw_FX<tag> at +12 / +15 dB against the
same-named chunk of the n = 20480 raw raw_FH<tag> -- every array of every arm except ALD-pilot (a new posterior sample by
construction: registration header '시행'), bit for bit (NaN == NaN).  Reads raws only.
usage (from conf/): CUDA_VISIBLE_DEVICES= python -B results/review_next/prereg_audit_2026-10-11/fx_overlap_check.py [SRB SRP]
"""
import glob, os, re, sys

import numpy as np

bad_total = 0
for P in (sys.argv[1:] or ["SRB", "SRP"]):
    for t in (f"{P}B16e4", f"SP{P}", f"ALD{P}"):
        fx = sorted(f for f in glob.glob(f"raw_FX{t}/D2_*.npz") if 10000 <= int(re.search(r"_skip(\d+)_", f)[1]) <= 30440)
        n, bad, arms, ald = 0, [], set(), [0, 0]
        for f in fx:
            g = os.path.join(f"raw_FH{t}", os.path.basename(f))
            if not os.path.exists(g):
                bad.append(f"{os.path.basename(f)}: no twin in raw_FH{t}")
                continue
            with np.load(f) as a, np.load(g) as b:
                for k in a.files:
                    arm = k.split("|")[0]
                    if arm in ("meta", "run"):
                        continue
                    if arm == "ALD-pilot":                      # reported, not required
                        ald[0] += 1
                        ald[1] += int(k not in b.files or not np.array_equal(a[k], b[k], equal_nan=True))
                        continue
                    arms.add(arm); n += 1
                    if k not in b.files or a[k].shape != b[k].shape or not np.array_equal(a[k], b[k], equal_nan=True):
                        bad.append(f"{os.path.basename(f)} {k}")
                for k in ("run|skip", "run|snr", "run|n", "run|seed", "run|iters"):
                    n += 1
                    if str(a[k]) != str(b[k]):
                        bad.append(f"{os.path.basename(f)} {k}")
        bad_total += len(bad) + (len(fx) != 1024)
        print(f"raw_FX{t} vs raw_FH{t}: {len(fx)} chunk files (expected 1024 = 512 x 2 SNR), arms {sorted(arms)}, {n} array comparisons, "
              f"{len(bad)} differ" + (f"; ALD-pilot (not required): {ald[1]} of {ald[0]} arrays differ" if ald[0] else ""))
        for x in bad[:10]:
            print("   ", x)
print("OVERLAP: " + ("OK" if bad_total == 0 else "FAILED"))
