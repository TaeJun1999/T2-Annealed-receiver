"""conf/code/selftest_dop.py -- NEXT_EXPERIMENTS_DOP16e4 code checks (review_DOP16e4 #3); exit 1 on any failure.  GPUs hidden.
  (1) every generator: sample_paths(rng) gives H bit-identical to sample(rng) and leaves the stream at the same state;
      sum_l P_l = H (rel <= 1e-12; 38.901 <= 1e-6, Sionna float32 paths)
  (2) runner.doppler_rx with nu = 0 returns Y bit for bit
  (3) nu > 0: doppler_rx equals a naive per-symbol loop Y_t = H_t X_t + W_t (rel <= 1e-12)
  (4) E<H_0, H_15>/E||H_0||^2 matches Clarke J0(2 pi nu 15) within 0.03 (300 blocks, a separate stream)
  (5) the Doppler stream is separate: two calls with different (SNR, trial) keys give different phases, same key the same
    CUDA_VISIBLE_DEVICES= python code/selftest_dop.py
"""
import os
import sys

os.environ["CUDA_VISIBLE_DEVICES"] = ""
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import numpy as np
from scipy.special import j0
import runner

bad = []
code = C.QAMCode(C.GENS, C.NU, C.M_QAM, 4 * 12)
for prior, Nr in (("S2", 8), ("S2", 16), ("S2c", 8), ("SV8e", 8), ("UMi28", 8), ("MIX3", 8)):
    g = C.make_gen("D2", prior, Nr, 4)
    tol = 1e-6 if prior in ("UMi28", "MIX3") else 1e-12
    r1, r2 = np.random.default_rng(11), np.random.default_rng(11)
    for _ in range(3):
        H1 = g.sample(r1); H, P = g.sample_paths(r2)
        if not np.array_equal(H1, H):
            bad.append(f"{prior}/{Nr}: sample_paths H != sample H")
        if np.max(np.abs(P.sum(0) - H)) > tol * np.max(np.abs(H)):
            bad.append(f"{prior}/{Nr}: sum P != H")
    if r1.integers(0, 2 ** 62) != r2.integers(0, 2 ** 62):
        bad.append(f"{prior}/{Nr}: stream state differs")
    # (2)(3) on one block with random symbols
    X = (np.random.default_rng(5).standard_normal((4, 16)) + 1j * np.random.default_rng(6).standard_normal((4, 16))) / np.sqrt(2)
    W = 0.1 * (np.random.default_rng(7).standard_normal((Nr, 16)) + 1j * np.random.default_rng(8).standard_normal((Nr, 16)))
    Y = H @ X + W
    if not np.array_equal(runner.doppler_rx(H, P, X, Y, 0.0, C.PID[prior], -3.0, 0), Y):
        bad.append(f"{prior}/{Nr}: nu = 0 does not return Y bit for bit")
    nu = 0.01
    drng = np.random.default_rng([runner.DOP_SEED, int(C.PID[prior]), 970, 0])
    w = 2 * np.pi * nu * np.cos(2 * np.pi * drng.random(P.shape[0]))
    naive = np.stack([(H + sum(P[l] * (np.exp(1j * w[l] * t) - 1) for l in range(P.shape[0]))) @ X[:, t] for t in range(16)], 1) + (Y - H @ X)
    got = runner.doppler_rx(H, P, X, Y, nu, C.PID[prior], -3.0, 0)
    if np.max(np.abs(got - naive)) > 1e-12 * np.max(np.abs(naive)):
        bad.append(f"{prior}/{Nr}: doppler_rx != naive loop")
    # (5) key separation
    a = runner.doppler_rx(H, P, X, Y, nu, C.PID[prior], -3.0, 1); b = runner.doppler_rx(H, P, X, Y, nu, C.PID[prior], -3.0, 2)
    if np.array_equal(a, b) or not np.array_equal(a, runner.doppler_rx(H, P, X, Y, nu, C.PID[prior], -3.0, 1)):
        bad.append(f"{prior}/{Nr}: Doppler stream keys not separate / not reproducible")
# (4) Clarke correlation
for prior in ("S2", "SV8e", "UMi28"):
    g = C.make_gen("D2", prior, 8, 4); rng = np.random.default_rng(7)
    for nu in (0.005, 0.01):
        num = den = 0.0
        for tr in range(300):
            H, P = g.sample_paths(rng)
            w = 2 * np.pi * nu * np.cos(2 * np.pi * np.random.default_rng([99, tr]).random(P.shape[0]))
            Ht = H + np.einsum("l,lij->ij", np.exp(1j * w * 15) - 1, P)
            num += np.real(np.vdot(H, Ht)); den += np.vdot(H, H).real
        r, ref = num / den, j0(2 * np.pi * nu * 15)
        print(f"  {prior} nu={nu}: corr(H0,H15) {r:.3f}  J0 {ref:.3f}")
        if abs(r - ref) > 0.03:
            bad.append(f"{prior} nu={nu}: correlation {r:.3f} vs J0 {ref:.3f}")
print("selftest_dop: " + ("OK" if not bad else "FAILED: " + "; ".join(bad)))
sys.exit(1 if bad else 0)
