"""M6 -- the self-test of the Stage C V1 / (F1) symmetric-PSD projection of the D-14 site.

(F1), conf/10_SPEC_stageC.md §3b: under real Gaussian noise the TRUE posterior-mean denoiser has
    J = dm/dq = Cov(h|q)/nu   ->  Hermitian and PSD, necessarily.
score.project_psd() enforces exactly that -- Hermitian part, eigenvalues floored at common.LAM_MIN --
and NOTHING else (lmax is deliberately left alone: the exact GMM genuinely has lmax(J) > 1 on many D2
points, so clamping the top of the spectrum would be a bias the true prior does not have).

Three assertions, all run on CPU:
  1. IDENTITY ON THE EXACT PRIOR.  The fitted D2 GMM's Jacobian is already Hermitian PSD, so the SAME
     projection code path must be the identity on it -- both through GMMPriorB.denoise_full (closed form)
     and through the autodiff/Wirtinger path of ExactGMMTorch (what jacobian_psd.py measures).
  2. EFFECT ON THE LEARNED PRIOR.  jacobian_psd.jac_stats with and without the projection: the indefinite
     fraction must go to 0, and the belief-mean shift of RouteAClip._matrix_site is reported before/after.
  3. NO CHANGE WHEN OFF.  ScorePrior defaults to psd_project=False and then returns bit-for-bit what the
     pre-V1 code returned (Hermitian part of the Wirtinger Jacobian); the mean m is never touched.

Nothing here is tuned and nothing is retrained: a fixed checkpoint on the frozen D2 sigma grid.
"""
import argparse, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import torch

import common as C
import arms as A
import sigma as SG
import score
import jacobian_psd as JP

NR, NT = 8, 4
N = NR * NT
OUT = os.path.join(C.CONF, "results", "diag")


def _held_out(prior, n):
    """The same held-out stream 10 and noise draw jacobian_psd.py uses, so the numbers are comparable."""
    gen = C.make_gen("D2", prior, NR, NT)
    H = gen.sample_vecs(C.train_rng("D2", prior, NR, 10), n)
    rng = np.random.default_rng(score.SEED_GATE)
    E = (rng.standard_normal((n, N)) + 1j * rng.standard_normal((n, N))) / np.sqrt(2)
    return H, E


def _gmm(prior):
    fits, llv, bstar, kron_K = A.gmm_selection("D2", prior, NR, C.N_TRAIN)
    fam, K = ("kron", kron_K) if bstar == "kron" else ("full", int(bstar[3:]))
    return C.GMMPriorB(NR, NT, fits[(fam, K)]["covs"], fits[(fam, K)]["pi"]), f"{bstar}(K={K})"


# ----------------------------------------------------------------------------- 1. identity on the exact prior
def step1(prior, H, E, nu_grid, ks, log):
    gmm, name = _gmm(prior)
    worst, lmin = 0.0, np.inf
    for k in ks:
        nu = float(nu_grid[k])
        for q in H + np.sqrt(nu) * E:
            m, J = gmm.denoise_full(q, nu)
            Jp = score.project_psd(J)
            worst = max(worst, float(np.max(np.abs(Jp - J)) / max(np.max(np.abs(J)), 1e-300)))
            lmin = min(lmin, float(np.linalg.eigvalsh(0.5 * (J + J.conj().T))[0]))
    log(f"[1] exact GMM {name}: closed-form denoise_full over {len(ks)} sigma points x {len(H)} samples")
    log(f"    max relative change of the projection : {worst:.3e}   (must be < 1e-10)")
    log(f"    min eigenvalue of J seen              : {lmin:.3e}   (LAM_MIN = {C.LAM_MIN:.0e})")
    assert worst < 1e-10, f"projection is NOT the identity on the exact GMM: {worst:.3e}"
    assert lmin >= C.LAM_MIN, (f"the exact GMM itself has an eigenvalue {lmin:.3e} below LAM_MIN -- the floor "
                               f"would then be a real change, not a projection")
    return dict(gmm=name, rel_change=worst, lmin=lmin)


def step1b(prior, H, E, nu_grid, sig_grid, k, log):
    """The same statement through the AUTODIFF path: ExactGMMTorch pushed through jac_stats, with and
    without the projection, must give identical site statistics."""
    gmm, name = _gmm(prior)
    m = score.ExactGMMTorch(gmm)
    nu, sg = float(nu_grid[k]), float(sig_grid[k])
    Q = torch.as_tensor(score.np_pack(H + np.sqrt(nu) * E), dtype=torch.float64)
    r0 = JP.jac_stats(m, Q, sg, nu)
    r1 = JP.jac_stats(m, Q, sg, nu, project=score.project_psd)
    d = {f: float(np.max(np.abs(r1[f] - r0[f]))) for f in ("lmin_c", "lmax_c", "nclip", "shift")}
    log(f"[1b] exact GMM {name} through jacobian_psd.jac_stats, sigma grid k={k} ({sg:.4e}), "
        f"n={len(H)}: max |after - before| " + "  ".join(f"{f}={v:.3e}" for f, v in d.items()))
    for f, v in d.items():
        assert v < 1e-10, f"projection changed the exact GMM's {f} by {v:.3e}"
    return d


# ----------------------------------------------------------------------------- 2. effect on the learned prior
def step2(ckpt, H, E, nu_grid, sig_grid, ks, log):
    model = score._as_model(ckpt, NR, NT, "cpu")[0]
    rows = []
    log(f"[2] learned prior {os.path.basename(ckpt)}: jacobian_psd.jac_stats before / after the projection, "
        f"n={len(H)} held-out D2 samples per sigma point")
    log(f"    {'k':>3}{'sigma':>11} | {'f(lmin<0)':>10}{'clipfrac':>10}{'shift_med':>11}{'shift_max':>11}"
        f" || {'f(lmin<0)':>10}{'clipfrac':>10}{'shift_med':>11}{'shift_max':>11}")
    for k in ks:
        nu, sg = float(nu_grid[k]), float(sig_grid[k])
        Q = torch.as_tensor(score.np_pack(H + np.sqrt(nu) * E), dtype=torch.float64)
        r0 = JP.jac_stats(model, Q, sg, nu)
        r1 = JP.jac_stats(model, Q, sg, nu, project=score.project_psd)
        q = dict(k=k, sigma=sg, nu=nu,
                 neg0=float((r0["lmin_c"] < 0).mean()), neg1=float((r1["lmin_c"] < 0).mean()),
                 clip0=float(r0["nclip"].mean()), clip1=float(r1["nclip"].mean()),
                 smed0=float(np.median(r0["shift"])), smed1=float(np.median(r1["shift"])),
                 smax0=float(np.max(r0["shift"])), smax1=float(np.max(r1["shift"])),
                 lmin0=float(r0["lmin_c"].min()), lmin1=float(r1["lmin_c"].min()),
                 lmax0=float(r0["lmax_c"].max()), lmax1=float(r1["lmax_c"].max()))
        rows.append(q)
        log(f"    {k:>3}{sg:>11.4e} | {q['neg0']:>10.3f}{q['clip0']:>10.3f}{q['smed0']:>11.3e}"
            f"{q['smax0']:>11.3e} || {q['neg1']:>10.3f}{q['clip1']:>10.3f}{q['smed1']:>11.3e}"
            f"{q['smax1']:>11.3e}")
    bad = [q["k"] for q in rows if q["neg1"] > 0]
    assert not bad, f"indefinite Jacobians survive the projection at sigma points {bad}"
    return rows


# ----------------------------------------------------------------------------- 3. off = unchanged
def step3(ckpt, prior, H, E, nu_grid, ks, log):
    Chat = A.load_fits("D2", prior, NR)[("full", 32)]["Chat"]
    sp0 = score.ScorePrior(ckpt, NR, NT, Chat, device="cpu")
    sp1 = score.ScorePrior(ckpt, NR, NT, Chat, device="cpu", psd_project=True)
    assert sp0.psd_project is False, "ScorePrior must default to the PRE-V1 behaviour"
    dJ = dm = 0.0
    dal, lmin1 = [], np.inf
    for k in ks:
        nu = float(nu_grid[k])
        for q in H + np.sqrt(nu) * E:
            m0, J0 = sp0.denoise_full(q, nu)
            m1, J1 = sp1.denoise_full(q, nu)
            # the pre-V1 expression, written out here so the test does not trust the branch it is testing
            x = torch.as_tensor(score.np_pack(q), dtype=torch.float64)
            sgt = torch.as_tensor(float(score.NU_TO_SIGMA(nu)), dtype=torch.float64)
            f = lambda v: score.tweedie_real(sp0.model, v, sgt)
            Jr = torch.func.jacrev(f)(x)
            Jref = score.wirtinger(Jr).detach().numpy()
            Jref = 0.5 * (Jref + Jref.conj().T)
            mref = score.np_unpack(f(x).detach().numpy())
            dJ = max(dJ, float(np.max(np.abs(J0 - Jref))))
            dm = max(dm, float(np.max(np.abs(m0 - mref))), float(np.max(np.abs(m1 - m0))))
            dal.append(float(np.trace(J1).real - np.trace(J0).real) / N)
            lmin1 = min(lmin1, float(np.linalg.eigvalsh(J1)[0]))
    log(f"[3] ScorePrior(psd_project=False) vs the pre-V1 expression, {len(ks)} sigma points x {len(H)} samples")
    log(f"    max |J_off - J_pre_V1|                : {dJ:.3e}   (must be exactly 0)")
    log(f"    max |m - m_pre_V1|, both flags        : {dm:.3e}   (the projection never touches the mean)")
    log(f"    min eigenvalue with psd_project=True  : {lmin1:.3e}   (>= LAM_MIN = {C.LAM_MIN:.0e})")
    log(f"    alpha = tr(J)/N shift on, mean / max  : {np.mean(dal):.3e} / {np.max(np.abs(dal)):.3e}")
    assert dJ == 0.0, f"psd_project=False changed the existing output by {dJ:.3e}"
    assert dm == 0.0, f"the denoiser mean moved by {dm:.3e}"
    assert lmin1 >= C.LAM_MIN - 1e-12, f"projected J is still indefinite: {lmin1:.3e}"
    return dict(dJ=dJ, dm=dm, lmin_on=lmin1, dalpha_mean=float(np.mean(dal)),
                dalpha_absmax=float(np.max(np.abs(dal))))


def main(a):
    torch.set_default_dtype(torch.float64)
    torch.set_num_threads(a.threads)
    os.makedirs(OUT, exist_ok=True)
    nu_grid, sig_grid = SG.load("D2")
    ks = [int(k) for k in a.ks.split(",")]
    H, E = _held_out(a.prior, a.n)
    lines = []

    def log(s):
        print(s, flush=True)
        lines.append(s)

    t0 = time.time()
    log(f"# M6 -- Stage C V1 / (F1) symmetric-PSD projection of the D-14 site   {time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    log(f"# ckpt = {a.ckpt}   prior = {a.prior}   n = {a.n} held-out D2 samples/point   sigma grid k = {ks}")
    log(f"# projection = score.project_psd: Hermitian part, then eigenvalues floored at common.LAM_MIN "
        f"= {C.LAM_MIN:.0e}.  lmax is NOT touched.")
    log("")
    s1 = step1(a.prior, H[:a.n1], E[:a.n1], nu_grid, ks, log)
    s1b = step1b(a.prior, H[:a.n1], E[:a.n1], nu_grid, sig_grid, ks[len(ks) // 2], log)
    log("")
    rows = step2(a.ckpt, H, E, nu_grid, sig_grid, ks, log)
    log("")
    s3 = step3(a.ckpt, a.prior, H[:a.n1], E[:a.n1], nu_grid, ks, log)
    log("")
    log(f"# ALL M6 ASSERTIONS PASSED  ({time.time() - t0:.1f} s)")

    txt = os.path.join(OUT, f"V1_selftest_M6{a.out}.txt")
    with open(txt, "w") as f:
        f.write("\n".join(lines) + "\n")
    np.savez_compressed(os.path.join(OUT, f"V1_jacpsd_D2{a.out}.npz"),
                        ckpt=a.ckpt, n=a.n, lam_min=C.LAM_MIN, sigma=sig_grid, nu=nu_grid,
                        gmm_rel_change=s1["rel_change"], gmm_lmin=s1["lmin"],
                        **{f"gmm_autodiff|{k}": v for k, v in s1b.items()},
                        **{f"off|{k}": v for k, v in s3.items()},
                        **{f"learned|{f}": np.array([r[f] for r in rows]) for f in rows[0]})
    print(f"\n# saved -> {txt}\n#          {os.path.join(OUT, f'V1_jacpsd_D2{a.out}.npz')}", flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--ckpt", default=os.path.join(C.CONF, "ckpt", "d2sx_N10000_a1.pt"))
    p.add_argument("--prior", default="S2")
    p.add_argument("--n", type=int, default=64, help="samples per sigma point for step 2")
    p.add_argument("--n1", type=int, default=16, help="samples for the (slower, exact-GMM / ScorePrior) steps")
    p.add_argument("--ks", default="0,6,12,18", help="indices into the frozen D2 sigma grid")
    p.add_argument("--threads", type=int, default=2)
    # REVIEWER FIX: this was `default=None, help="unused"` and BOTH outputs were hard-coded, so a re-run
    # at a different --n/--n1/--ks silently overwrote the RECORDED V1_* artefacts with different-n numbers
    # (observed).  Now a suffix, like runner.py's --tag; default "" keeps the recorded paths byte-identical.
    p.add_argument("--out", default="", help="suffix on the output stem; '' = the recorded V1_* artefacts")
    main(p.parse_args())
