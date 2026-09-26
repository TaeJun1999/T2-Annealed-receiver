"""conf/code/testbed_d3.py -- verification of D3 = D2 prior 'S2c' (alpha_l ~ CN(0, p_l); d2.py) before any BLER.

Mirrors the D2 verification (05_SPEC §2, d2.tests_T2) where it is meaningful, on the S2c streams:
  T2a  normalisation E||H||_F^2 = Nr Nt (+ analytic C_ens = kron(Rt^T, Rr) vs samples)   -- same criterion as D2
  T3a  the T2a criterion (rel err <= 1e-3) at n = 4e6: with CN gains sd(||H||_F^2/NrNt) = 0.57 (S2: 0.16), so at T2a's
       n = 1e5 the MC s.e. (1.8e-3) EXCEEDS the 1e-3 criterion and a T2a PASS/FAIL there is mostly chance.  At 4e6 the s.e.
       is 2.8e-4 (criterion = 3.5 s.e.).  Same criterion value, enough samples to mean something.
  T2b  effective rank / pilot decision (same sides as S2 -> same decision)                  -- record
  T2c  first-pass NMSE_inf at the cell's Tp                                                 -- record
  T2e  sparsity                                                                             -- record
  T2d/T2dm (D2's criterion "every CI EXCLUDES 2", prediction 2 - sum p_l^2) are printed as run: on D3 they MUST fail.
  T3d  THE DEFINING PROPERTY of D3: conditional Gaussianity RESTORED.  Given (L, angles), h = sum_l u_l alpha_l with
       alpha_l ~ CN(0, p_l) is complex Gaussian, so E|h|^4 / (E|h|^2)^2 = 2 EXACTLY.  Same design as T2d (same stream
       index 91, one forced angle set per L in 3..8 + free sets, 20000 gain draws per set, 99.9% bootstrap CI over
       realisations).  PASS = every CI contains 2 (criterion fixed here, before the run).
  T3dm D2 contrast: the D2 prediction 2 - sum_l p_l^2 lies BELOW every T3d CI (the two testbeds are distinguishable
       at every L).  RECORD.

  python testbed_d3.py [--cell C1 C2]   -> conf/results/testbed_D3.txt      (CPU, ~1 min, no BLER)
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C                      # FIRST: sets OMP/OPENBLAS/MKL_NUM_THREADS=1 before numpy loads the BLAS
import numpy as np
import d2
import tests as TS

PRIOR = "S2c"


def t3d(Nr, Nt, n_sets=8, n_phase=20000, n_boot=1000):
    gen = d2.D2Gen(PRIOR, Nr, Nt)
    rng = C.train_rng("D2", PRIOR, Nr, 91)
    forced = list(range(d2.L_MIN, d2.L_MAX + 1))
    rows = []
    for i in range(max(n_sets, len(forced))):
        if i < len(forced):
            Lf = forced[i]
            ang0 = (gen.lo + (gen.hi - gen.lo) * rng.random(Lf), gen.lo + (gen.hi - gen.lo) * rng.random(Lf),
                    d2._P[Lf - d2.L_MIN, :Lf].copy())
            Hs, ang = gen.sample_angles(rng, n_phase, angles=ang0)
        else:
            Hs, ang = gen.sample_angles(rng, n_phase)
        p = ang[2]
        a2 = (Hs.real ** 2 + Hs.imag ** 2).reshape(n_phase, -1)
        s2, s4 = a2.sum(1), (a2 ** 2).sum(1)
        meas = gen.N * s4.mean() / s2.mean() ** 2
        bs = np.empty(n_boot)
        for b in range(n_boot):
            j = rng.integers(0, n_phase, n_phase)
            bs[b] = gen.N * s4[j].mean() / s2[j].mean() ** 2
        lo, hi = np.percentile(bs, [0.05, 99.95])
        rows.append((len(p), meas, lo, hi, 2.0 - float(np.sum(p ** 2) / np.sum(p) ** 2)))
    ok = all(lo <= 2.0 <= hi for _, _, lo, hi, _ in rows)
    sep = all(pd < lo for _, _, lo, _, pd in rows)
    worst = max(abs(m - 2.0) for _, m, _, _, _ in rows)
    per = " | ".join(f"L={L}: meas {m:.4f} (CI {lo:.4f},{hi:.4f}) D2-pred {pd:.4f}" for L, m, lo, hi, pd in rows)
    return [
        ("T3d", "PASS" if ok else "FAIL", worst, "every CI contains 2",
         f"D3 conditional Gaussianity: {len(rows)} angle sets x {n_phase} path-gain draws (L and angles FIXED, "
         f"alpha_l ~ CN(0, p_l) free), 99.9% bootstrap CI ({n_boot} resamples over realisations). Complex Gaussian "
         f"value = 2 EXACTLY. " + per + f" -> max |meas - 2| = {worst:.4f}; "
         + ("every CI contains 2: conditional Gaussianity is RESTORED." if ok else
            "*** a CI EXCLUDES 2: the S2c generator is NOT conditionally Gaussian -- do not use D3. ***")),
        ("T3dm", "RECORD", min(lo - pd for _, _, lo, _, pd in rows), "D2-pred < CI_lo at every L",
         "D2 contrast: the D2 (|alpha_l| deterministic) prediction 2 - sum_l p_l^2 is "
         + ("BELOW every T3d CI (smallest margin CI_lo - pred printed as residual): D3 and D2 differ at every L."
            if sep else "NOT excluded by every T3d CI -- D3 and D2 are not distinguishable at some L.")),
    ]


def t3a(Nr, Nt, n=4_000_000, chunk=200_000):
    gen = d2.D2Gen(PRIOR, Nr, Nt)
    rng = C.train_rng("D2", PRIOR, Nr, 93)
    e = np.concatenate([(np.abs(gen.sample_vecs(rng, chunk)) ** 2).sum(1) for _ in range(n // chunk)]) / (Nr * Nt)
    rel, se = abs(e.mean() - 1.0), e.std() / np.sqrt(len(e))
    return [("T3a", "PASS" if rel <= 1e-3 else "FAIL", rel, "rel err <= 1e-3",
             f"E||H||_F^2/(Nr Nt) = {e.mean():.6f} over n={len(e)} (stream 93); MC s.e. {se:.2e} -> |rel err| = "
             f"{rel / se:.2f} s.e.; sd(||H||_F^2/NrNt) = {e.std():.4f}. (T2a above uses n=1e5, s.e. "
             f"{e.std() / np.sqrt(1e5):.2e} > its 1e-3 criterion.)")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", nargs="+", default=["C1", "C2"])
    a = ap.parse_args()
    rows = []
    for cell in a.cell:
        c = C.CELLS[cell]
        for tid, v, r, cr, d in d2.tests_T2(PRIOR, c["Nr"], c["Nt"], c["Tp"]):
            if cell != a.cell[0] and tid != "T2c":             # only T2c depends on Tp
                continue
            if tid in ("T2d", "T2dm"):                         # D2's own criterion: on D3 it must NOT hold
                v, d = {"FAIL": "FAIL(exp)", "PASS": "PASS(!)"}.get(v, v), "[D2 criterion applied to D3 -- " \
                    "expected to FAIL, since the D2 prediction 2 - sum p_l^2 no longer holds] " + d
            rows.append((f"{cell}:{tid}" if len(a.cell) > 1 else tid, v, r, cr, d))
    Nrs = sorted({C.CELLS[c]["Nr"] for c in a.cell})
    for Nr in Nrs:
        rows += [((f"Nr{Nr}:" if len(Nrs) > 1 else "") + r[0],) + r[1:] for r in t3a(Nr, C.NT) + t3d(Nr, C.NT)]
    txt = TS.fmt(rows)
    out = os.path.join(C.CONF, "results", "testbed_D3.txt")
    with open(out, "w") as f:
        f.write(C.header("D2", extra=[
            f"content     : D3 = D2 prior {PRIOR} (alpha_l ~ CN(0, p_l)) -- T2a/T2b/T2c/T2e as 05_SPEC §2, D2's T2d "
            f"shown failing, T3d = restored conditional Gaussianity (cells {a.cell})",
            "gate        : T3a or T3d FAIL => D3 is not the intended control; no D3 BLER.",
        ]) + "\n" + C.D3_WARNING + "\n\n" + txt + "\n")
    print(txt, flush=True)
    print(f"[testbed_d3] -> {out}", flush=True)
    t3 = [v for t, v, *_ in rows if t.endswith(("T3a", "T3d"))]
    return 0 if t3 and all(v == "PASS" for v in t3) else 1


if __name__ == "__main__":
    sys.exit(main())
