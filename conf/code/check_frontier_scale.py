"""conf/code/check_frontier_scale.py -- self-check of the frontier_ci.py additions for NEXT_EXPERIMENTS_SCALE16e4 §1 (⑤).
Reads recorded raws only (no receiver, no GPU).  Asserts:
  (1) the pre-existing --recovery lines stay bit-identical to results/review_next/recovery_diff_U28B16e4.txt (last block);
  (2) recorded R_dp points 0.509 (raw_B16e4k C2), 0.823 (raw_NR16B16e4 C6), 0.150 (raw_U28B16e4 C2);
  (3) Q-K identity: K/2 raw = base raw -> R+ replicates / point identical to R, the other lines identical to no --extrap;
  (4) Q-OP R*@0.05 from raw failure counts: 0.610 / 0.806 / 0.218 (tol 1e-3);
  (5) arithmetic of _Rplus (clamp, c_K, SigmaF+ <= SigmaF_g) and ci_p (p capped at 1);
  (6) cross-raw Q-K (the path the primary uses): --extrap - raw_B16e4 --ck - 5.2637007373767215 on spec 2 = raw_B16e4k ->
      R draws / R1 / R2 / R1 - R2 / gaps lines unchanged, b*(K/2) 899, dF +35, R2+ = the _Rplus float formula, genie assert.
    CUDA_VISIBLE_DEVICES= ~/miniforge3/envs/torch/bin/python code/check_frontier_scale.py
"""
import contextlib
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import frontier_ci as F

B16, NR16, U28 = "raw_B16e4k:C2:-3,0,3", "raw_NR16B16e4:C6:-3,0,3", "raw_U28B16e4:C2:3,6,9"


def run(*a, **k):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        out = F.cmd_recovery(*a, **k)
    return buf.getvalue().splitlines(), out


# (5) arithmetic, no data
assert F._Rplus(100, 50, 10, 90, 2.0)[0] == (100 - 50) / (100 - 10)          # dF <= 0 -> b*+ = b*
assert abs(F._Rplus(100, 50, 10, 110, 2.0)[0] - 30 / 70) < 1e-15             # SigmaF+ = 100 - 2*10 = 80
assert np.isnan(F._Rplus(100, 50, 10, 150, 2.0)[0])                          # SigmaF+ = 0 <= SigmaF_g
assert F.ci_p(np.zeros(10), 0.9)[2] == 1.0 and F.ci_p(np.ones(10), 0.9)[2] == 0.0

# (1) + (2)
lines, out = run(U28, B16, F.B, F.SEED)
rec = open(os.path.join(F.C.CONF, "results/review_next/recovery_diff_U28B16e4.txt")).read().splitlines()[-4:]
assert lines[:4] == rec, (lines[:4], rec)
r_nr = F._R(F._rec_cols(NR16)[3])[0]
assert (round(out["r"][1], 3), round(r_nr, 3), round(out["r"][0], 3)) == (0.509, 0.823, 0.150), (out["r"], r_nr)

# (3) identity on raw_B16e4k
plain, o0 = run(B16, U28, F.B, F.SEED, 0.95)
ext, o1 = run(B16, U28, F.B, F.SEED, 0.95, ("raw_B16e4k", "-"), ("2", "-"))
assert np.array_equal(o0["bo"], o1["bo"], equal_nan=True) and np.array_equal(o1["bp"], o1["bo"], equal_nan=True)
assert tuple(o1["rp"]) == tuple(o1["r"])
qk = [l for l in ext if l.startswith(("# Q-K", "  R1+", "  R2+"))]
assert [l for l in ext if l not in qk] == plain and len(qk) == 3
r1 = next(l for l in plain if l.startswith("  R1:")); r1p = next(l for l in ext if l.startswith("  R1+:"))
assert r1.split("R = ")[1] in r1p                                             # same point and 90% CI text
d95 = next(l for l in plain if "(--level" in l); dp = next(l for l in ext if l.startswith("  R1+ - R2+"))
assert d95.split(" = ", 1)[1].split("  (--level")[0] in dp                    # same Delta, CI at level, p

# (4) R*@0.05 smoke from raw failure counts
for spec, want in ((B16, 0.610), (NR16, 0.806), (U28, 0.218)):
    raw, cell = spec.split(":")[:2]
    d = F.raws(raw); ks = F.points(d, cell)
    cols = [tuple(F.fails(d, k, a) for a in F.REC_ARMS) for k in ks]
    r = F._rstar([k[2] for k in ks], cols, min(len(c[0]) for c in cols), 0.05)
    assert r[1] == "ok" and abs(r[0] - want) < 1e-3, (spec, r)
    print(f"R*@0.05 {raw} {cell}: s* = {r[2]:+.4f} dB  R* = {r[0]:.6f}  (target {want})")

# (6) cross-raw Q-K on the path the primary uses: D2 C2's K/2 raw (raw_B16e4, kron 512) vs the base raw_B16e4k
plain2, o2 = run(NR16, B16, F.B, F.SEED, 0.95)
ext2, o3 = run(NR16, B16, F.B, F.SEED, 0.95, ("-", "raw_B16e4"), ("-", "5.2637007373767215"))
assert np.array_equal(o2["bo"], o3["bo"], equal_nan=True) and o3["rp"][0] == o3["r"][0]   # R draws untouched, R1+ = R1
fp = 864 - 5.2637007373767215 * 35                                                       # same float ops as _Rplus
assert abs(o3["rp"][1] - (fp - 488) / (fp - 125)) < 1e-12, o3["rp"]
r2p = next(l for l in ext2 if l.startswith("  R2+:"))
assert "b*(K/2) 899  dF = +35" in r2p and "SigmaF+ <= SigmaF_g in 0.0%" in r2p, r2p
assert [l for l in ext2 if not l.startswith(("# Q-K", "  R2+", "  R1+ - R2+"))] == plain2
print(f"cross-raw Q-K raw_B16e4 -> raw_B16e4k: {r2p.strip()[:120]}")
print("  " + r2p.split("R+ = ")[1][:60] + " | " + next(l for l in ext2 if l.startswith("  R1+ - R2+")).strip()[:80])
print("  plain: " + next(l for l in plain2 if "(--level" in l).strip()[:80])
print(f"R_dp points: B16e4k {out['r'][1]:.6f}  NR16B16e4 {r_nr:.6f}  U28B16e4 {out['r'][0]:.6f}")
print("check_frontier_scale: ALL PASS")
