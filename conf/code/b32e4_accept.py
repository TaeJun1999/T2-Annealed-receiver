"""conf/code/b32e4_accept.py -- NEXT_EXPERIMENTS_B32e4 §1 acceptance check of the three evaluation tags (B32e4, B32e4x,
B32e4last): per point exactly the chunks {(40k, 40): k=0..63}; raw meta ntrain = 320000; bstar / kron_K / ll_val|kron equal
to the values frozen in §5 (passed on the command line); the three tags agree on bstar / kron_K / em_sec; the Stage C
checkpoint identity (sha256[:16], role) equals the expected one per tag; run|iters = 16.  Prints OK or the first failure
(exit 1).  Read-only.
    python conf/code/b32e4_accept.py --kron-K 4096 --ll-val -5.94... --best-sha 035744cbe955984d --last-sha f2f1eebc9894c773
"""
import argparse
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--kron-K", type=int, required=True)
ap.add_argument("--ll-val", type=float, required=True)
ap.add_argument("--best-sha", required=True)
ap.add_argument("--last-sha", required=True)
a = ap.parse_args()
TAGS = {"B32e4": ("best", a.best_sha, ["C2"]), "B32e4x": ("best", a.best_sha, ["C5", "C1"]),
        "B32e4last": ("last", a.last_sha, ["C2"])}
plan = [(40 * k, 40) for k in range(64)]
common_meta, bad = {}, []
for tag, (role, sha, cells) in TAGS.items():
    files = glob.glob(os.path.join(C.CONF, f"raw_{tag}", "D2_*.npz"))
    pts = {}
    for f in files:
        m = re.search(r"D2_(C\d)_.*_snr(-?\d+)_skip(\d+)_n(\d+)\.npz$", f)
        pts.setdefault((m[1], int(m[2])), []).append((int(m[3]), int(m[4]), f))
    want = {(c, s) for c in cells for s in C.CELLS[c]["snrs"]}
    if set(pts) != want:
        bad.append(f"{tag}: points {sorted(set(pts) ^ want)} missing/extra")
    for key, ch in pts.items():
        if sorted((s, n) for s, n, _ in ch) != plan:
            bad.append(f"{tag} {key}: chunk plan differs")
        for _, _, f in ch[:1] + ch[-1:]:
            with np.load(f) as z:
                g = lambda k: str(z[k].item() if z[k].shape == () else z[k])
                if int(float(g("meta|ntrain"))) != 320000 or g("meta|bstar") != "kron" or int(float(g("meta|kron_K"))) != a.kron_K:
                    bad.append(f"{os.path.basename(f)}: ntrain/bstar/kron_K = {g('meta|ntrain')}/{g('meta|bstar')}/{g('meta|kron_K')}")
                if abs(float(g("meta|ll_val|kron")) - a.ll_val) > 1e-9:
                    bad.append(f"{os.path.basename(f)}: ll_val|kron {g('meta|ll_val|kron')} != {a.ll_val}")
                ids = g("meta|stagec_ckpt_id")
                if f"sha256[:16]={sha}" not in ids or f"role={role}" not in ids:
                    bad.append(f"{os.path.basename(f)}: ckpt id {ids[:80]} != sha {sha} role {role}")
                if int(z["run|iters"]) != 16:
                    bad.append(f"{os.path.basename(f)}: run|iters {int(z['run|iters'])}")
                common_meta.setdefault((g("meta|bstar"), g("meta|kron_K"), g("meta|em_sec")), set()).add(tag)
if len(common_meta) != 1:
    bad.append(f"tags disagree on (bstar, kron_K, em_sec): {common_meta}")
print("ACCEPT: OK -- " + ", ".join(TAGS) if not bad else "ACCEPT: FAILED\n  " + "\n  ".join(bad[:20]))
sys.exit(1 if bad else 0)
