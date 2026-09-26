"""conf/code/selftest_d3tp.py -- bit-identity of every EXISTING testbed / prior / cell after the D3 (prior 'S2c') and
Tp > Nt (cells C7/C8) additions of 2026-09-25/26, plus the defining properties of the two additions.

  python selftest_d3tp.py [REV]          REV = git revision to compare against (default HEAD)

REV:conf/code is extracted into a temp dir (Demo/ is symlinked, never copied or edited).  The SAME dump() runs once
on the old code and once on the working tree, each in its own subprocess, and every array must be np.array_equal:
  D2 sample_vecs (1000 draws, fixed rng) and train streams 7/8/10/90, priors S2/U2, Nr 4/8/16; sample_angles;
  ensemble sides; D1 sample_vecs (U/S/P, Nr 4/8); make_pilots for every existing (testbed, prior, cell);
  the trial streams of every existing cell (first 3 trials: H, u, perm, Y at the first and last SNR, D2/S2 and D1/S);
  code sizes; CELLS / PID of the existing keys; analysis.PAT on every raw file name under conf/raw*/.
Generating trial draws is not a receiver run: no BLER is computed anywhere here.
"""
import os
import subprocess
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
OLD_CELLS = ("C1", "C2", "C3", "C4", "C5", "C6")


def dump(code_dir, out):
    sys.path = [code_dir] + [p for p in sys.path if os.path.abspath(p or ".") != HERE]
    import glob
    import common as C
    import d2
    import analysis
    assert os.path.dirname(os.path.abspath(C.__file__)) == os.path.abspath(code_dir), C.__file__
    D = {}
    for prior in ("S2", "U2"):
        for Nr in (4, 8, 16):
            g = C.make_gen("D2", prior, Nr, 4)
            D[f"vecs|{prior}|{Nr}"] = g.sample_vecs(np.random.default_rng(20260926), 1000)
            for w in (7, 8, 10, 90):
                D[f"train|{prior}|{Nr}|{w}"] = g.sample_vecs(C.train_rng("D2", prior, Nr, w), 64)
            H, ang = g.sample_angles(np.random.default_rng(3), 50)
            D[f"angles|{prior}|{Nr}"] = np.concatenate([H.reshape(-1)] + [np.asarray(a, complex) for a in ang])
            Rt, Rr, inf = d2.ensemble_sides_d2(prior, Nr, 4)
            D[f"sides|{prior}|{Nr}"] = np.concatenate([Rt.reshape(-1), Rr.reshape(-1), [float(inf)]])
    for prior in ("U", "S", "P"):
        for Nr in (4, 8):
            D[f"d1vecs|{prior}|{Nr}"] = C.make_gen("D1", prior, Nr, 4).sample_vecs(np.random.default_rng(5), 64)
    for cell in OLD_CELLS:
        c = C.CELLS[cell]
        D[f"cell|{cell}"] = np.array([c["Nr"], c["Nt"], c["T"], c["Tp"]] + list(c["snrs"]), float)
        for tb, prior in (("D1", "U"), ("D1", "S"), ("D1", "P"), ("D2", "U2"), ("D2", "S2")):
            pil, Xp = C.make_pilots(tb, prior, c["Nt"], c["Tp"], c["Nr"])
            D[f"pilots|{tb}|{prior}|{cell}"] = Xp
            D[f"pil|{tb}|{prior}|{cell}"] = np.array([pil == "dft", pil == "eig"])
        code = C.QAMCode(C.GENS, C.NU, C.M_QAM, c["Nt"] * (c["T"] - c["Tp"]))
        D[f"code|{cell}"] = np.array([code.K, code.Ns])
        for tb, prior in (("D2", "S2"),) + ((("D1", "S"),) if c["Nr"] != 16 else ()):
            _, Xp = C.make_pilots(tb, prior, c["Nt"], c["Tp"], c["Nr"])
            gen = C.make_gen(tb, prior, c["Nr"], c["Nt"])
            for snr in (c["snrs"][0], c["snrs"][-1]):
                rx = C.RouteA(c["Nr"], c["Nt"], c["T"], c["Tp"], 10 ** (-snr / 10),
                              C.GaussianPrior(c["Nr"], c["Nt"], np.eye(c["Nr"] * c["Nt"])), code, Xp=Xp)
                rng = C.trial_rng(tb, prior, c["Nr"], c["T"], c["Tp"], snr)
                for tr in range(3):
                    H = gen.sample(rng)
                    u = rng.integers(0, 2, code.K)
                    perm = rng.permutation(code.Ns)
                    _, Y = rx.transmit(u, perm, H, rng)
                    for k, v in (("H", H), ("u", u), ("perm", perm), ("Y", Y)):
                        D[f"trial|{tb}|{prior}|{cell}|{snr:g}|{tr}|{k}"] = v
    D["pid"] = np.array([C.PID[k] for k in ("U", "S", "P", "U2", "S2")])
    D["tbid"] = np.array([C.TBID["D1"], C.TBID["D2"]])
    names = sorted(os.path.basename(f) for f in glob.glob(os.path.join(REPO, "conf", "raw*", "*.npz")))
    D["pat"] = np.array(["|".join(m.groups()) if m else "NOMATCH" for m in map(analysis.PAT.match, names)])
    np.savez(out, **D)


def properties():
    """The additions themselves (working tree only)."""
    import common as C
    import d2
    for cell, Tp in (("C7", 6), ("C8", 8)):
        c = C.CELLS[cell]
        assert (c["Nr"], c["Nt"], c["T"], c["Tp"]) == (8, 4, 16, Tp) and c["snrs"] == C.CELLS["C2"]["snrs"]
        code = C.QAMCode(C.GENS, C.NU, C.M_QAM, c["Nt"] * (c["T"] - c["Tp"]))
        assert code.K == c["Nt"] * (c["T"] - c["Tp"]) - 6 == {6: 34, 8: 26}[Tp], code.K
        for tb, prior in (("D2", "S2"), ("D2", "S2c"), ("D2", "U2"), ("D1", "S")):
            pil, Xp = C.make_pilots(tb, prior, 4, Tp, 8)
            assert pil == "dft" and Xp.shape == (4, Tp)
            assert np.allclose(np.abs(Xp), 1.0, atol=0, rtol=1e-15)
            assert np.allclose(Xp @ Xp.conj().T, Tp * np.eye(4), atol=1e-12)
            assert np.array_equal(Xp, np.exp(-2j * np.pi * np.outer(np.arange(4), np.arange(Tp)) / Tp))
    assert C.PID["S2c"] not in [C.PID[k] for k in C.PID if k != "S2c"]
    assert set(C.DEFAULT_CELLS) == set(OLD_CELLS)
    g, g0 = C.make_gen("D2", "S2c", 8, 4), C.make_gen("D2", "S2", 8, 4)
    assert (g.lo, g.hi, g.scale) == (g0.lo, g0.hi, g0.scale) and g.cn and not g0.cn
    for k, a, b in zip(("Rt", "Rr", "inf"), d2.ensemble_sides_d2("S2c", 8, 4), d2.ensemble_sides_d2("S2", 8, 4)):
        assert np.array_equal(a, b), k
    for s in ("S2", "U2"):                                     # S2c streams are NEW streams, never an S2 stream
        assert not np.array_equal(C.train_rng("D2", "S2c", 8, 7).random(4), C.train_rng("D2", s, 8, 7).random(4))
    # same (L, angles) draw as S2 given the same rng state; only the path gains differ -> |alpha_l| now random
    th, ph, al, L = g._draw(np.random.default_rng(1), 4000)
    th0, ph0, al0, L0 = g0._draw(np.random.default_rng(1), 4000)
    assert np.array_equal(L, L0) and np.array_equal(th, th0) and np.array_equal(ph, ph0)
    amp = np.sqrt(d2._P[L - d2.L_MIN])
    assert np.allclose(np.abs(al0), amp) and not np.allclose(np.abs(al), amp)
    r = np.abs(al[amp > 0]) ** 2 / amp[amp > 0] ** 2          # |CN(0,1)|^2 ~ Exp(1): mean 1, E x^2 = 2
    assert abs(r.mean() - 1) < 0.02 and abs((r ** 2).mean() - 2) < 0.08, (r.mean(), (r ** 2).mean())
    print("properties: C7/C8 pilots (unit modulus, Xp Xp^H = Tp I, K=34/26), S2c sides == S2, S2c path gains "
          f"|alpha|^2/p_l mean {r.mean():.4f} (1), E[.^2] {(r ** 2).mean():.4f} (2) -- OK")


def main(rev="HEAD"):
    with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as tmp:
        old = os.path.join(tmp, "conf", "code")
        os.makedirs(old)
        os.symlink(os.path.join(REPO, "Demo"), os.path.join(tmp, "Demo"))
        tar = subprocess.run(["git", "-C", REPO, "archive", rev, "conf/code"], check=True, capture_output=True).stdout
        subprocess.run(["tar", "-x", "-C", tmp], input=tar, check=True)
        outs = []
        for d in (old, HERE):
            o = os.path.join(tmp, f"dump{len(outs)}.npz")
            subprocess.run([sys.executable, os.path.abspath(__file__), "--dump", d, o], check=True)
            outs.append(o)
        a, b = (np.load(o) for o in outs)
        assert set(a.files) == set(b.files), set(a.files) ^ set(b.files)
        bad = [k for k in a.files if a[k].dtype != b[k].dtype or not np.array_equal(a[k], b[k])]
        n = sum(a[k].size for k in a.files)
        print(f"bit-identity vs {rev}: {len(a.files)} arrays, {n} values, "
              f"{len(a['pat'])} raw file names -> {'IDENTICAL' if not bad else 'DIFFER: ' + ', '.join(bad[:10])}")
        assert not bad
    properties()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--dump":
        dump(sys.argv[2], sys.argv[3])
    else:
        main(*sys.argv[1:2])
