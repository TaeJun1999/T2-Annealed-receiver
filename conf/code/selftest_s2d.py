"""B' (S2d, per-block receive rotation U[0, 30 deg]) self-check: old D2 priors bit-identical to the pre-B' commit's generator,
S2d = S2 draws + one extra last draw per block, rotation law, new streams.  Run: python code/selftest_s2d.py"""
import os, subprocess, sys, importlib.util, tempfile
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C, d2

# 1) old priors: same output as the pre-B' d2.py (git show 9c0ca1f4)
src = subprocess.run(["git", "show", "9c0ca1f4:conf/code/d2.py"], capture_output=True, text=True, check=True,
                     cwd=os.path.dirname(os.path.abspath(__file__))).stdout
with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
    f.write(src)
spec = importlib.util.spec_from_file_location("d2_old", f.name); old = importlib.util.module_from_spec(spec); spec.loader.exec_module(old)
for prior in ("S2", "U2", "S2c"):
    for Nr, Nt in ((8, 4), (16, 4)):
        a, b = d2.D2Gen(prior, Nr, Nt), old.D2Gen(prior, Nr, Nt)
        r1, r2 = np.random.default_rng(5), np.random.default_rng(5)
        assert np.array_equal(a.sample_vecs(r1, 300), b.sample_vecs(r2, 300)), prior
        assert np.array_equal(a.sample(r1), b.sample(r2)) and r1.random() == r2.random(), prior
        H1, P1 = a.sample_paths(r1); H2, P2 = b.sample_paths(r2); assert np.array_equal(H1, H2) and np.array_equal(P1, P2)
# 2) S2d = S2 draws, then delta ~ U[0, 30deg] per block added to every AoA
g, s = d2.D2Gen("S2d", 8, 4), d2.D2Gen("S2", 8, 4)
r1, r2 = np.random.default_rng(9), np.random.default_rng(9)
th, ph, al, L = g._draw(r1, 1000); th0, ph0, al0, L0 = s._draw(r2, 1000)
dl = r2.random((1000, 1)) * np.deg2rad(30.0)
assert np.array_equal(ph, ph0) and np.array_equal(al, al0) and np.array_equal(L, L0) and np.allclose(th, th0 + dl, atol=1e-15)
d = (th - th0)[:, 0]
assert np.allclose(th - th0, d[:, None]) and d.min() >= 0 and d.max() < np.deg2rad(30) and abs(d.mean() - np.deg2rad(15)) < 0.02
# 3) rotation ROT is still additive on top; power; new PID / streams
assert C.PID["S2d"] not in [C.PID[k] for k in C.PID if k != "S2d"]
X = g.sample_vecs(np.random.default_rng(1), 20000); assert abs(np.mean(np.sum(abs(X) ** 2, 1)) / 32 - 1) < 0.02
assert not np.array_equal(C.train_rng("D2", "S2d", 8, 7).random(4), C.train_rng("D2", "S2", 8, 7).random(4))
print("selftest_s2d OK")
