"""conf/code/testbed_sv.py -- verification of the second testbed SV (prior 'SV8e', code/sv.py) before any training or BLER.

  python testbed_sv.py      -> conf/results/testbed_SV.txt        (CPU, a few minutes, no BLER, no GPU)

Rows (tests.fmt format; criteria fixed here before the run):
  TSV0 construction identity: SVGen's channel == the probe's formula (testbed2_phase0/code/sv_probe.py: un-normalised
       steering, H = sum alpha a_r a_t^T) evaluated at the SAME draws with phi -> -phi.  a_t^H(phi) = a_t^T(-phi) and
       U[-pi,pi) + Laplace is invariant under phi -> -phi, so this identity + equal angle/gain laws = the same model.  PASS
       = max relative difference <= 1e-12.
  TSVa normalisation E||H||_F^2 = Nr Nt at n = N_NORM (stream 93; T2a/T3a criterion rel err <= 1e-3), every entry
       E|H_ab|^2 = 1 (max |dev| in s.e. <= 5), analytic C_ens = kron(Rt^T, Rr) vs the Monte-Carlo covariance (reported,
       as in D2's T2a).
  TSVb effective ranks + the T2b pilot decision (d2.T2B_ERANK_FRAC on Rt, exactly the D2 rule in common.make_pilots). RECORD
  TSVc first-pass NMSE_inf (d2.nmse_inf) of eig and DFT pilots at the cells' Tp.                                    RECORD
  TSVd conditional law GIVEN all 80 ray angles: fourth-moment ratio E|h|^4/(E|h|^2)^2, 8 angle sets x N_PHASE gain draws
       (stream 91), 99.9% bootstrap CI over realisations (as D2 T2d / D3 T3d).  Exact prediction with the per-block
       normalisation alpha = g/||g|| (uniform on the unit sphere of C^P, P = 80): 2P/(P+1) = 160/81, angle-invariant;
       without it (alpha = g ~ CN) the channel would be exactly complex Gaussian (ratio 2).  PASS = every CI contains 160/81.
       Whether the CIs exclude 2 is recorded in the row (near-Gaussian, not exactly Gaussian).
  TSVe beamspace sparsity (unitary 2-D DFT bins, as D2 T2e).                                                        RECORD
  TSVp probe reproduction (selection.md / json/res_SV8e.json, seed 1): ensemble erank of the sample covariance (n=40000),
       conditional-covariance erank (probe definition: sum_l |alpha_l|^2 v_l v_l^H, realised gains), top-4 / top-8 beamspace
       energy.  PASS = every |mine - probe| <= 4 combined Monte-Carlo s.e. (mine's s.e. scaled to the probe's n).
       paths_eff, clusters_eff, outage(-3 dB), angle-only conditional erank are printed beside it (not judged).
Gate: TSV0, TSVa, TSVd or TSVp FAIL => SV8e is not the selected model; no SV training or BLER.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C                      # FIRST: sets OMP/OPENBLAS/MKL_NUM_THREADS=1 before numpy loads the BLAS
import numpy as np
import d2
import sv
import tests as TS

PRIOR, NR, NT = "SV8e", 8, C.NT
CELLS = ("C1", "C2")
N_NORM, NORM_CHUNK = 2_000_000, 100_000
N_PHASE, N_SETS, N_BOOT = 100_000, 8, 1000
N_PROBE_C, N_COND = 40_000, 10_000
PROBE_JSON = os.path.join(C.CONF, "results", "review_next", "testbed2_phase0", "json", "res_SV8e.json")
rec = lambda tid, ok, r, cr, d: (tid, ok if isinstance(ok, str) else ("PASS" if ok else "FAIL"), r, cr, d)
erank = lambda lam: lam.sum(-1) ** 2 / (lam ** 2).sum(-1)


def tsv0(g, rng):
    th, ph, al = g._draw(rng, 2000)
    h = g._channels(th, ph, al).transpose(0, 2, 1).reshape(len(al), -1)
    steer = lambda s, M: np.exp(1j * np.pi * s[..., None] * np.arange(M))                       # sv_probe.py verbatim
    V = (steer(-np.sin(ph), NT)[..., :, None] * steer(np.sin(th), NR)[..., None, :]).reshape(*th.shape, NR * NT)
    hp = np.einsum("nl,nlk->nk", al, V)
    d = float(np.max(np.abs(h - hp)) / np.max(np.abs(hp)))
    return rec("TSV0", d <= 1e-12, d, "max rel diff <= 1e-12",
               f"SVGen channel vs sv_probe.py formula (Vof, un-normalised steering, a_t^T at -phi) on the same 2000 draws: "
               f"max|dh|/max|h| = {d:.2e}. Probe differences are conventions only: a_t^H(phi) = a_t^T(-phi) (the AoD law "
               "U[-pi,pi) + Laplace is symmetric), and the probe's empirical power rescale s is 1 analytically here "
               "(unit-norm steering x SCALE = sqrt(Nr Nt)). Angle/gain laws: cluster-mean AoA U[-60,60] deg, AoD U[-180,180) "
               "deg, Laplace offsets b = 7.5/sqrt2 deg, g ~ CN(0,1/80), alpha = g/||g|| -- identical to the probe.")


def tsva(g, Rt, Rr):
    rng = C.train_rng("D2", PRIOR, NR, 93)
    s1 = s2 = 0.0
    e1 = np.zeros(NR * NT)
    e2 = np.zeros(NR * NT)
    Cmc = np.zeros((NR * NT, NR * NT), complex)
    for _ in range(N_NORM // NORM_CHUNK):
        X = g.sample_vecs(rng, NORM_CHUNK)
        P = X.real ** 2 + X.imag ** 2
        f = P.sum(1) / (NR * NT)
        s1 += f.sum(); s2 += (f ** 2).sum(); e1 += P.sum(0); e2 += (P ** 2).sum(0)
        Cmc += X.T @ X.conj()
    n = N_NORM
    m, sd = s1 / n, np.sqrt(s2 / n - (s1 / n) ** 2)
    em = e1 / n
    ese = np.sqrt(e2 / n - em ** 2) / np.sqrt(n)
    ez = float(np.max(np.abs(em - 1.0) / ese))
    Cmc /= n
    Cens = np.kron(Rt.T, Rr)
    cerr = float(np.max(np.abs(Cmc - Cens)) / (np.trace(Cens).real / (NR * NT)))
    rel, se = abs(m - 1.0), sd / np.sqrt(n)
    ok = rel <= 1e-3 and ez <= 5.0
    return rec("TSVa", ok, rel, "rel err <= 1e-3; E|H_ab|^2 <= 5 s.e.",
               f"E||H||_F^2/(Nr Nt) = {m:.6f} over n={n} (stream 93), MC s.e. {se:.2e} -> |rel err| = {rel / se:.2f} s.e.; "
               f"sd(||H||_F^2/NrNt) = {sd:.4f}. Per entry E|H_ab|^2 in [{em.min():.5f}, {em.max():.5f}], worst |dev| = "
               f"{ez:.2f} s.e. (analytic value 1 for every entry). Analytic C_ens = kron(Rt^T, Rr) vs MC: max|dC|/cbar = "
               f"{cerr:.2e} = {cerr * np.sqrt(n):.1f} MC s.e. (per-entry s.e. ~ 1/sqrt(n)) -- "
               + ("the closed form AGREES with samples it was never fitted to." if cerr * np.sqrt(n) <= 6 else
                  "*** DISAGREES: Rt/Rr do not describe these samples -- the pilot decision below is built from them. ***")), Cmc


def tsvb(Rt, Rr, inf, Cmc):
    lt, lr = np.linalg.eigvalsh(Rt), np.linalg.eigvalsh(Rr)
    et, er_, ec = d2._erank(lt), d2._erank(lr), d2._erank(np.kron(lt, lr))
    emc = float(erank(np.linalg.eigvalsh(Cmc)))
    Ru = d2.ensemble_sides_d2("U2", NR, NT)[0]
    full = ec < d2.T2B_ERANK_FRAC * NR * NT
    return rec("TSVb", "RECORD", et, f"erank(Rt) < {d2.T2B_ERANK_FRAC}*Nt ?",
               f"erank(Rt) = {et:.4f}/{NT} ({et / NT:.3f}), erank(Rr) = {er_:.4f}/{NR} ({er_ / NR:.3f}), erank(C_ens) = "
               f"{ec:.4f}/{NR * NT} ({ec / (NR * NT):.3f}) [MC n={N_NORM}: {emc:.4f}]; Rt eigenvalues = "
               f"[{', '.join(f'{v:.4f}' for v in lt[::-1])}]. DECISION (the D2 T2b rule of common.make_pilots): pilots = "
               + ("EIGEN-ALIGNED (Rt informative)" if inf else "DFT (transmit side near-white)")
               + f". Why not near-white although the AoD spans the full circle: phi mod 2pi is uniform, so sin(phi) has the "
               f"arcsine law (mass piles up at endfire) and the lags are r_t(k) = J_0(pi k) = "
               f"[{', '.join(f'{v:.4f}' for v in Rt[0])}] -- Rt is IDENTICAL to D2 prior U2's (max diff "
               f"{np.max(np.abs(Rt - Ru)):.1e}; U2 also gets eig pilots). The full-covariance reading ({ec:.4f} "
               f"{'<' if full else '>='} {d2.T2B_ERANK_FRAC * NR * NT:.1f}) "
               + ("agrees." if full == inf else "DIFFERS from the decision in force."))


def tsvc(Rt):
    out = []
    for cell in CELLS:
        Tp = C.CELLS[cell]["Tp"]
        pil, Xp = C.make_pilots("D2", PRIOR, NT, Tp, NR)
        nm = {k: d2.nmse_inf(Rt, d2._pilots(k, Rt, NT, Tp)) for k in ("eig", "dft")}
        out.append(rec(f"{cell}:TSVc", "RECORD", nm[pil], f"vs 1-Tp/Nt = {1 - Tp / NT:.4f}",
                       f"NMSE_inf(Tp={Tp}): eig = {nm['eig']:.6f}, dft = {nm['dft']:.6f}; 1-Tp/Nt = {1 - Tp / NT:.4f}; pilots IN "
                       f"USE (make_pilots) = {pil}, |Xp| in [{np.abs(Xp).min():.3f}, {np.abs(Xp).max():.3f}], Xp Xp^H = "
                       f"{'Tp I' if np.allclose(Xp @ Xp.conj().T, Tp * np.eye(NT)) else 'not a multiple of I'}"
                       + (" -- Tp = Nt: eig and DFT pilots both span the whole transmit side with Xp Xp^H = Nt I, so the "
                          "pilot observation Y Xp^H / Nt = H + white noise is the same sufficient statistic (same law; the "
                          "trial streams still differ)." if Tp == NT else "")))
    return out


def tsvd(g):
    rng = C.train_rng("D2", PRIOR, NR, 91)
    P = sv.P_RAYS
    pred = 2.0 * P / (P + 1.0)
    rows = []
    for _ in range(N_SETS):
        Hs, _ = g.sample_angles(rng, N_PHASE)
        a2 = (Hs.real ** 2 + Hs.imag ** 2).reshape(N_PHASE, -1)
        s2, s4 = a2.sum(1), (a2 ** 2).sum(1)
        meas = g.N * s4.mean() / s2.mean() ** 2
        bs = np.empty(N_BOOT)
        for b in range(N_BOOT):
            j = rng.integers(0, N_PHASE, N_PHASE)
            bs[b] = g.N * s4[j].mean() / s2[j].mean() ** 2
        lo, hi = np.percentile(bs, [0.05, 99.95])
        rows.append((meas, lo, hi))
    ok = all(lo <= pred <= hi for _, lo, hi in rows)
    n_ex2 = sum(hi < 2.0 for _, _, hi in rows)
    worst = max(abs(m - pred) for m, _, _ in rows)
    return rec("TSVd", ok, worst, "every CI contains 160/81",
               f"conditional law given ALL {P} ray angles (theta, phi fixed; alpha = g/||g||, g ~ CN(0, I/{P}) free): "
               f"{N_SETS} angle sets x {N_PHASE} gain draws (stream 91), 99.9% bootstrap CI ({N_BOOT} resamples over "
               f"realisations). Exact prediction 2P/(P+1) = {pred:.5f} (uniform-sphere gains; complex Gaussian = 2 exactly, "
               "D2 S2 = 2 - sum p_l^2 in [1.61, 1.75], D3 S2c = 2). "
               + " | ".join(f"set {i}: {m:.4f} (CI {lo:.4f},{hi:.4f})" for i, (m, lo, hi) in enumerate(rows))
               + f" -> max |meas - {pred:.4f}| = {worst:.4f}; {n_ex2}/{N_SETS} CIs exclude 2. STATEMENT: given the cluster "
               "angles and ray offsets, h = V alpha is the projection of a uniform unit-sphere vector -- CONDITIONALLY "
               "GAUSSIAN UP TO THE PER-BLOCK POWER NORMALISATION (elliptical, covariance V V^H/80, fourth-moment deficit "
               f"2/(P+1) = {2 / (P + 1):.4f}); without the normalisation (the CN draw itself) exactly Gaussian. The angles "
               "are continuous, so the ensemble is a continuous (near-)Gaussian mixture and a finite-K GMM is an approximation.")


def beams(Hm):
    Fr = np.fft.fft(np.eye(NR)) / np.sqrt(NR)
    Ft = np.fft.fft(np.eye(NT)) / np.sqrt(NT)
    B = np.abs(np.einsum("ab,nbc,cd->nad", Fr.conj(), Hm, Ft, optimize=True)).reshape(len(Hm), -1) ** 2
    return np.sort(B / B.sum(1, keepdims=True), 1)[:, ::-1]


def tsve(f):
    topk = {k: float(f[:, :k].sum(1).mean()) for k in (1, 2, 4, 8)}
    part = float((1.0 / np.sum(f ** 2, 1)).mean())
    return rec("TSVe", "RECORD", part, "record only",
               f"{sv.N_CL} clusters x {sv.N_RAY} rays per block, Laplacian spread {np.rad2deg(sv.SPREAD):.1f} deg; 2D-DFT "
               f"angular energy over {NR * NT} bins (n={len(f)}, stream 90): "
               + ", ".join(f"top-{k} = {v:.4f}" for k, v in topk.items())
               + f"; effective #bins (1/sum f_b^2) = {part:.3f}/{NR * NT} ({part / (NR * NT):.3f} of the aperture). "
               "D2 S2 for comparison (testbed_D2 T2e): top-4 0.7117, effective #bins 5.895.")


def tsvp(g, f):
    pr = json.load(open(PROBE_JSON))
    rng = C.train_rng("D2", PRIOR, NR, 90)
    # (1) ensemble erank of the sample covariance, n = 40000 (the probe's training size); s.e. by bootstrap over rows
    X = g.sample_vecs(rng, N_PROBE_C)
    ec = float(erank(np.linalg.eigvalsh(X.T @ X.conj() / len(X))))
    rb = np.random.default_rng(5)
    bse = np.std([erank(np.linalg.eigvalsh((lambda Y: Y.T @ Y.conj() / len(Y))(X[rb.integers(0, len(X), len(X))])))
                  for _ in range(100)])
    # (2) conditional covariance erank, probe definition (realised gains), and the angle-only version (weights 1/P)
    th, ph, al = g._draw(rng, N_COND)
    ar = np.exp(1j * np.pi * np.sin(th)[..., None] * np.arange(NR)) / np.sqrt(NR)
    at = np.exp(1j * np.pi * np.sin(ph)[..., None] * np.arange(NT)) / np.sqrt(NT)
    V = g.scale * (at.conj()[..., :, None] * ar[..., None, :]).reshape(N_COND, sv.P_RAYS, NR * NT)   # column-major vec
    p = np.abs(al) ** 2
    ce = erank(np.linalg.eigvalsh(np.swapaxes(V * p[..., None], 1, 2) @ V.conj()))      # sum_l p_l v_l v_l^H
    ca = erank(np.linalg.eigvalsh(np.swapaxes(V, 1, 2) @ V.conj()))                     # sum_l v_l v_l^H
    pc = p.reshape(N_COND, sv.N_CL, sv.N_RAY).sum(2)
    Hm = g._channels(th[:20000], ph[:20000], al[:20000])
    mi = np.log2(1 + np.linalg.svd(Hm, compute_uv=False) ** 2 / 10 ** (3 / 10)).sum(1)
    # (3) judged comparisons: (name, mine, se_mine, n_mine, probe, n_probe)
    t4, t8 = f[:, :4].sum(1), f[:, :8].sum(1)
    cmp_ = [("erank_C", ec, bse, N_PROBE_C, pr["erank_C"], pr["ntr"]),
            ("cond_erank", float(ce.mean()), float(ce.std() / np.sqrt(N_COND)), N_COND, pr["cond_erank"], pr["nte"]),
            ("top4", float(t4.mean()), float(t4.std() / np.sqrt(len(f))), len(f), pr["top4"], pr["ntr"]),
            ("top8", float(t8.mean()), float(t8.std() / np.sqrt(len(f))), len(f), pr["top8"], pr["ntr"])]
    zs = [abs(m - q) / (s * np.sqrt(1 + n / nq)) for _, m, s, n, q, nq in cmp_]
    ok = max(zs) <= 4.0
    rec_ = dict(paths_eff=(float((1 / (p ** 2).sum(1)).mean()), pr["paths_eff"]),
                clusters_eff=(float((1 / (pc ** 2).sum(1)).mean()), pr["clusters_eff"]),
                outage_m3dB=(float(np.mean(mi < 4)), pr["outage_-3dB"]))
    return rec("TSVp", ok, max(zs), "max |d| <= 4 comb. s.e.",
               "probe reproduction vs json/res_SV8e.json (seed 1): "
               + "; ".join(f"{k} mine {m:.4f} (s.e. {s:.4f}, n={n}) vs probe {q:.4f} (n={nq}): {z:.2f} s.e."
                           for (k, m, s, n, q, nq), z in zip(cmp_, zs))
               + ". Not judged: " + ", ".join(f"{k} {a:.4f} vs probe {b:.4f}" for k, (a, b) in rec_.items())
               + f"; angle-only conditional covariance (E over gains given the 80 angles = V V^H/{sv.P_RAYS}, the covariance "
               f"of the TSVd law) erank = {float(ca.mean()):.3f}. selection.md table: erank_c 9.0, top4 0.58 -- "
               + ("REPRODUCED: same model." if ok else "*** NOT REPRODUCED -- this generator is not the selected SV8e. ***"))


def main():
    t0 = time.time()
    g = C.make_gen("D2", PRIOR, NR, NT)
    Rt, Rr, inf = sv.ensemble_sides_sv(PRIOR, NR, NT)
    Xv = g.sample_vecs(C.train_rng("D2", PRIOR, NR, 90), N_PROBE_C)
    f = beams(Xv.reshape(len(Xv), NT, NR).transpose(0, 2, 1))
    rows = [tsv0(g, np.random.default_rng(0))]
    ra, Cmc = tsva(g, Rt, Rr)
    rows += [ra, tsvb(Rt, Rr, inf, Cmc)] + tsvc(Rt) + [tsvd(g), tsve(f), tsvp(g, f)]
    txt = TS.fmt(rows)
    out = os.path.join(C.CONF, "results", "testbed_SV.txt")
    with open(out, "w") as fo:
        fo.write(C.header("D2", extra=[
            f"content     : second testbed SV = D2-pipeline prior {PRIOR} (code/sv.py; user decision 2026-09-26 00:06 CDT) -- "
            f"construction vs probe, normalisation, pilot decision, NMSE_inf, conditional law, sparsity, probe statistics",
            f"arrays      : Nr={NR} x Nt={NT} (cells {list(CELLS)}); CPU {time.time() - t0:.0f} s",
            "gate        : TSV0, TSVa, TSVd or TSVp FAIL => not the selected SV8e model; no SV training or BLER.",
        ]) + "\n" + C.SV_WARNING + "\n\n" + txt + "\n")
    print(txt, flush=True)
    print(f"[testbed_sv] -> {out}  ({time.time() - t0:.0f} s)", flush=True)
    judged = [v for t, v, *_ in rows if v in ("PASS", "FAIL")]
    return 0 if judged and all(v == "PASS" for v in judged) else 1


if __name__ == "__main__":
    sys.exit(main())
