"""conf/code/selftest_rot.py -- NEXT_EXPERIMENTS_ROT16e4 code checks; exit 1 on any failure.  GPUs hidden.
  (1) every generator: an explicit .rot = 0.0 gives the same H and stream state as the class default (both run the rotation
      arithmetic -- theta + 0.0 / yaw + 0.0 are exact); bit-identity with the PRE-rotation code is the run script's 0-deg control
      and the review's hash comparison against main 063f3bcb;
  (2) .rot > 0 changes H but leaves the stream state unchanged (every random draw is the same, only the AoA moves);
  (3) D2 and SV8e: the rotated H equals the generator's own steering applied to the unrotated latents with theta + rot;
  (4) ensemble power E||H||^2 / (Nr Nt) stays within 5% under rotation for every generator incl. 38.901 (1000 blocks; for
      38.901 the yaw change also changes the polarisation coupling, so power is not preserved by construction).
The bit-identity of a 0-deg run with the static raw through the whole receiver is the run script's control (ROT0<suf>).
    CUDA_VISIBLE_DEVICES= python code/selftest_rot.py
"""
import os
import sys

os.environ["CUDA_VISIBLE_DEVICES"] = ""
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import numpy as np

bad = []
ROT = np.deg2rad(15.0)
for prior, Nr in (("S2", 8), ("S2", 16), ("S2c", 8), ("S2v", 16), ("SV8e", 8), ("UMi28", 8), ("MIX3", 8)):
    g0, g1, g2 = (C.make_gen("D2", prior, Nr, 4) for _ in range(3))
    g1.rot = 0.0; g2.rot = ROT
    r0, r1, r2 = (np.random.default_rng(21) for _ in range(3))
    H0 = [g0.sample(r0) for _ in range(3)]; H1 = [g1.sample(r1) for _ in range(3)]; H2 = [g2.sample(r2) for _ in range(3)]
    if not all(np.array_equal(a, b) for a, b in zip(H0, H1)):
        bad.append(f"{prior}/{Nr}: rot = 0 changes H")
    if not all(not np.allclose(a, c) for a, c in zip(H0, H2)):
        bad.append(f"{prior}/{Nr}: rot > 0 leaves H unchanged")
    s = [r.integers(1 << 30) for r in (r0, r1, r2)]
    if len(set(s)) != 1:
        bad.append(f"{prior}/{Nr}: stream state differs under rotation")
    if prior in ("S2", "SV8e") and Nr == 8:                                    # (3) the generator's own steering, theta + rot
        g = C.make_gen("D2", prior, Nr, 4)
        lat = g._draw(np.random.default_rng(4), 1)                             # rot = 0 latents of the same stream
        gr = C.make_gen("D2", prior, Nr, 4); gr.rot = ROT
        got = gr.sample(np.random.default_rng(4))
        ref = g._channels(lat[0] + ROT, lat[1], lat[2])[0]
        if not np.allclose(got, ref, rtol=1e-12, atol=1e-12):
            bad.append(f"{prior}: rotated H != own steering with theta + rot")
    if True:
        rr0, rr2 = np.random.default_rng(9), np.random.default_rng(9)
        p0 = np.mean([np.sum(np.abs(g0.sample(rr0)) ** 2) for _ in range(1000)]) / (Nr * 4)
        p2 = np.mean([np.sum(np.abs(g2.sample(rr2)) ** 2) for _ in range(1000)]) / (Nr * 4)
        print(f"  {prior}/{Nr}: E||H||^2/(Nr Nt) {p0:.3f} -> rotated {p2:.3f}")
        if abs(p2 / p0 - 1) > 0.05:
            bad.append(f"{prior}/{Nr}: power changes {p0:.3f} -> {p2:.3f}")
print("selftest_rot: " + ("OK" if not bad else "FAILED: " + "; ".join(bad)))
sys.exit(1 if bad else 0)
