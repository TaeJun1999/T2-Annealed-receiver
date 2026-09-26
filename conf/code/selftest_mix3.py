"""conf/code/selftest_mix3.py -- bit-identity of every EXISTING testbed / prior / cell after the 38.901 MIX3 prior (code/mix3.py,
2026-09-26; the standard-model side of the boundary-both-sides second testbed), plus the defining properties of the addition.
Adapted from selftest_sv.py; the existing set now includes SV8e (sample_vecs, train streams, sides, pilots, trial streams).

  python selftest_mix3.py [REV]        REV = git revision to compare against (default HEAD; the MIX3 commit's parent is 9e182607)

REV:conf/code is extracted into a temp dir (Demo/ is symlinked, never copied or edited).  The SAME dump() runs once on the old
code and once on the working tree, each in its own subprocess, and every array must be np.array_equal:
  D2 priors S2 / U2 / S2c: sample_vecs (1000 draws, fixed rng), train streams 7/8/10/90, sample_angles, ensemble sides, Nr 4/8/16;
  D1 priors U / S / P: sample_vecs, Nr 4/8;
  cells C1..C8: CELLS entries, DEFAULT_CELLS, code sizes, make_pilots for every existing (testbed, prior), and the trial streams
  (first 3 trials: H, u, perm, Y at the first and last SNR) for D2/S2, D2/S2c and D1/S (D1 not at Nr=16);
  PID / TBID / PRIOR_OF of the existing keys; sigma.CHAT_FROM_TRAIN membership of the existing priors;
  analysis.PAT on every raw file name under conf/raw*/ AND on synthetic names of every (testbed, cell, existing prior, pilot, SNR);
  analysis.main tables text (D1 and D2 from conf/raw, D2 from conf/raw_B16e4; the date / git-commit header lines stripped).
Generating trial draws is not a receiver run: no BLER is computed anywhere here (analysis only re-reads existing raw files).
"""
import os
import subprocess
import sys
import tempfile
import warnings

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
CELLS8 = ("C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8")
D2_OLD = ("S2", "U2", "S2c")
OLD_PID = ("U", "S", "P", "U2", "S2", "S2c", "SV8e")
TABLES = (("D1", ""), ("D2", ""), ("D2", "B16e4"))


def dump(code_dir, out, tmp):
    sys.path = [code_dir] + [p for p in sys.path if os.path.abspath(p or ".") != HERE]
    import glob
    import common as C
    import d2
    import analysis
    import sigma
    assert os.path.dirname(os.path.abspath(C.__file__)) == os.path.abspath(code_dir), C.__file__
    D = {}
    for prior in D2_OLD:
        for Nr in (4, 8, 16):
            g = C.make_gen("D2", prior, Nr, 4)
            D[f"vecs|{prior}|{Nr}"] = g.sample_vecs(np.random.default_rng(20260926), 1000)
            for w in (7, 8, 10, 90):
                D[f"train|{prior}|{Nr}|{w}"] = g.sample_vecs(C.train_rng("D2", prior, Nr, w), 64)
            H, ang = g.sample_angles(np.random.default_rng(3), 50)
            D[f"angles|{prior}|{Nr}"] = np.concatenate([H.reshape(-1)] + [np.asarray(a, complex) for a in ang])
            Rt, Rr, inf = d2.ensemble_sides_d2(prior, Nr, 4)
            D[f"sides|{prior}|{Nr}"] = np.concatenate([Rt.reshape(-1), Rr.reshape(-1), [float(inf)]])
    import sv
    for Nr in (4, 8, 16):                                            # SV8e (existing since 9e182607)
        g = C.make_gen("D2", "SV8e", Nr, 4)
        D[f"vecs|SV8e|{Nr}"] = g.sample_vecs(np.random.default_rng(20260926), 1000)
        for w in (7, 8, 10, 90):
            D[f"train|SV8e|{Nr}|{w}"] = g.sample_vecs(C.train_rng("D2", "SV8e", Nr, w), 64)
        Rt, Rr, inf = sv.ensemble_sides_sv("SV8e", Nr, 4)
        D[f"sides|SV8e|{Nr}"] = np.concatenate([Rt.reshape(-1), Rr.reshape(-1), [float(inf)]])
    for prior in ("U", "S", "P"):
        for Nr in (4, 8):
            D[f"d1vecs|{prior}|{Nr}"] = C.make_gen("D1", prior, Nr, 4).sample_vecs(np.random.default_rng(5), 64)
    for cell in CELLS8:
        c = C.CELLS[cell]
        D[f"cell|{cell}"] = np.array([c["Nr"], c["Nt"], c["T"], c["Tp"]] + list(c["snrs"]), float)
        for tb, prior in (("D1", "U"), ("D1", "S"), ("D1", "P")) + tuple(("D2", p) for p in D2_OLD + ("SV8e",)):
            pil, Xp = C.make_pilots(tb, prior, c["Nt"], c["Tp"], c["Nr"])
            D[f"pilots|{tb}|{prior}|{cell}"] = Xp
            D[f"pil|{tb}|{prior}|{cell}"] = np.array([pil == "dft", pil == "eig"])
        code = C.QAMCode(C.GENS, C.NU, C.M_QAM, c["Nt"] * (c["T"] - c["Tp"]))
        D[f"code|{cell}"] = np.array([code.K, code.Ns])
        for tb, prior in (("D2", "S2"), ("D2", "S2c"), ("D2", "SV8e")) + ((("D1", "S"),) if c["Nr"] != 16 else ()):
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
    D["pid"] = np.array([C.PID[k] for k in OLD_PID])
    D["tbid"] = np.array([C.TBID["D1"], C.TBID["D2"]])
    D["prior_of"] = np.array([C.PRIOR_OF["D1"], C.PRIOR_OF["D2"]])
    D["default_cells"] = np.array(list(C.DEFAULT_CELLS))
    D["chat_from_train"] = np.array([p in sigma.CHAT_FROM_TRAIN for p in OLD_PID])
    names = sorted(os.path.basename(f) for f in glob.glob(os.path.join(REPO, "conf", "raw*", "*.npz")))
    names += [f"{tb}_{cell}_{p}_Nr{C.CELLS[cell]['Nr']}_T{C.CELLS[cell]['T']}_Tp{C.CELLS[cell]['Tp']}_{pil}_snr{int(s)}"
              f"_skip{sk}_n{n}.npz" for tb in ("D1", "D2") for cell in CELLS8 for p in OLD_PID for pil in ("dft", "eig")
              for s in C.CELLS[cell]["snrs"] for sk, n in ((0, 40), (2560, 64))]
    D["pat"] = np.array(["|".join(m.groups()) if m else "NOMATCH" for m in map(analysis.PAT.match, names)])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for tb, tag in TABLES:
            root = os.path.join(REPO, "conf", "raw" + (f"_{tag}" if tag else ""))
            txt = analysis.main(tb, tag, root, os.path.join(tmp, f"tables_{os.getpid()}"),
                                os.path.join(REPO, "conf", "results"))
            D[f"tables|{tb}|{tag}"] = np.array([l for l in txt.splitlines()
                                                if not l.startswith(("# date", "# git commit"))])
    np.savez(out, **D)


def _mix3_det(out):
    """Subprocess helper: MIX3 draws that must be identical across processes."""
    import common as C
    g = C.make_gen("D2", "MIX3", 8, 4)
    np.savez(out, vecs=g.sample_vecs(np.random.default_rng(5), 10), one=g.sample(np.random.default_rng(6)),
             train=g.sample_vecs(C.train_rng("D2", "MIX3", 8, 7), 8))


def properties():
    """The MIX3 addition itself (working tree only)."""
    import torch
    import common as C
    import analysis
    import runner
    import score
    import sigma
    import mix3
    assert C.PID["MIX3"] == 7 and C.PID["UMi28"] == 8 and sorted(C.PID.values()) == list(range(len(C.PID))), C.PID
    assert C.MIX3_PRIORS == mix3.PRIORS == ("MIX3", "UMi28") and {"MIX3", "UMi28"} <= set(sigma.CHAT_FROM_TRAIN)
    assert all((p, 8, 4) in mix3.P_RAW and (p, 8, 4) in mix3.RT for p in mix3.PRIORS), "calibration constants missing"
    g = C.make_gen("D2", "MIX3", 8, 4)
    assert isinstance(g, mix3.MIX3Gen) and g.prior is None and g.N == 32
    nt = torch.get_num_threads()
    H = g._draw(np.random.default_rng(0), 3)
    X = g.sample_vecs(np.random.default_rng(0), 3)
    assert torch.get_num_threads() == nt, "thread count not restored"
    assert np.array_equal(X, np.array([h.reshape(-1, order="F") for h in H])), "MIX3 vec is not column-major"
    assert np.array_equal(g.sample(np.random.default_rng(1)).reshape(-1, order="F"), g.sample_vecs(np.random.default_rng(1), 1)[0])
    with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as tmp:          # determinism across processes
        outs = []
        for k in range(2):
            o = os.path.join(tmp, f"det{k}.npz")
            subprocess.run([sys.executable, os.path.abspath(__file__), "--mix3det", o], check=True,
                           env=dict(os.environ, CUDA_VISIBLE_DEVICES=""))
            outs.append(np.load(o))
        assert all(np.array_equal(outs[0][k], outs[1][k]) for k in ("vecs", "one", "train")), "MIX3 not deterministic"
        assert np.array_equal(outs[0]["vecs"], g.sample_vecs(np.random.default_rng(5), 10)), "MIX3 differs in-process"
    Xn = g.sample_vecs(C.train_rng("D2", "MIX3", 8, 8), 4096)                        # validation stream: normalisation
    pw = float(np.mean(np.sum(np.abs(Xn) ** 2, 1))) / 32
    assert 0.9 < pw < 1.1, pw
    for s in ("S2", "U2", "S2c", "SV8e"):                            # MIX3 streams are NEW streams
        assert not np.array_equal(C.train_rng("D2", "MIX3", 8, 7).random(4), C.train_rng("D2", s, 8, 7).random(4))
        assert not np.array_equal(C.trial_rng("D2", "MIX3", 8, 16, 4, -3).random(4), C.trial_rng("D2", s, 8, 16, 4, -3).random(4))
    Rt, _, inf = mix3.ensemble_sides_mix3("MIX3", 8, 4)
    for cell in ("C1", "C2", "C5", "C7", "C8"):
        c = C.CELLS[cell]
        pil, Xp = C.make_pilots("D2", "MIX3", c["Nt"], c["Tp"], c["Nr"])
        if c["Tp"] > c["Nt"]:
            assert pil == "dft" and np.allclose(Xp @ Xp.conj().T, c["Tp"] * np.eye(c["Nt"]), atol=1e-12)
        else:
            assert pil == ("eig" if inf else "dft") and Xp.shape == (c["Nt"], c["Tp"])
    for p in ("S2", "U2", "S2c"):
        assert C.banner("D2", p) == C.D2_WARNING
    assert C.banner("D2", "SV8e") == C.SV_WARNING and C.banner("D2", "MIX3") == C.MIX3_WARNING and C.banner("D2", "UMi28") == C.UMI28_WARNING
    runner.TAG = None
    for cell in CELLS8:
        f = os.path.basename(runner.raw_file("D2", cell, "MIX3", "dft", -3.0, 2560, 40))
        m = analysis.PAT.match(f)
        c = C.CELLS[cell]
        assert m and m.groups() == ("D2", cell, "MIX3", str(c["Nr"]), str(c["T"]), str(c["Tp"]), "dft", "-3", "2560", "40"), f
    out = []
    analysis.table_D("D2", out, os.path.join(REPO, "conf", "results"), priors={"MIX3"})
    assert "gate_D2.txt / gmm_fit_D2.txt describe the D2 (S2) testbed" in "\n".join(out)
    ix = {score._rung_ix(f"D2SX{p}{n}") for p in ("", "S2c", "SV8e", "MIX3", "UMi28") for n in (10000, 40000, 160000, 320000)}
    assert len(ix) == 20, "rung seed collision"
    print(f"properties: PID MIX3=7, MIX3Gen column-major / deterministic across processes / new streams / threads restored, "
          f"normalisation {pw:.4f} (val stream, n=4096), pilots {'eig' if inf else 'dft'} (T2b rule; Tp>Nt DFT branch), banners, "
          "raw_file<->PAT, table_D note, rung seeds distinct -- OK")


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
            subprocess.run([sys.executable, os.path.abspath(__file__), "--dump", d, o, tmp], check=True)
            outs.append(o)
        a, b = (np.load(o) for o in outs)
        assert set(a.files) == set(b.files), set(a.files) ^ set(b.files)
        bad = [k for k in a.files if a[k].dtype != b[k].dtype or not np.array_equal(a[k], b[k])]
        n = sum(a[k].size for k in a.files)
        nt = sum(a[k].size for k in a.files if k.startswith("tables|"))
        print(f"bit-identity vs {rev}: {len(a.files)} arrays, {n} values ({nt} table lines), {len(a['pat'])} raw / synthetic "
              f"file names ({int((a['pat'] != 'NOMATCH').sum())} parsed) -> "
              + ("IDENTICAL" if not bad else "DIFFER: " + ", ".join(bad[:10])))
        assert not bad
    properties()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--dump":
        dump(sys.argv[2], sys.argv[3], sys.argv[4])
    elif len(sys.argv) > 1 and sys.argv[1] == "--mix3det":
        sys.path.insert(0, HERE)
        _mix3_det(sys.argv[2])
    else:
        main(*sys.argv[1:2])
