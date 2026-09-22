"""conf/code/diag_p1_heldout.py -- P1-2 / P1-3 / P1-4 on HELD-OUT AWGN queries: the held-out halves of
NEXT_EXPERIMENTS v3 §2.2 (calibration), §2.3 (global-phase equivariance) and §2.4 (pseudo-covariance).  The
real-query halves belong to the §2.1 cavity dump.  Diagnostic P1-x, NOT a gate (§0).  Nothing is trained, tuned
or selected: the headline checkpoint and the headline GMM b* are measured on the frozen D2 sigma grid.

Per frozen grid point k = 0..19 (0-based; tiers low k0-6 / mid k7-14 / high k15-19, §0):
  queries  q = h + CN(0, nu_k I),  h = gen.sample_vecs(C.train_rng(D2, S2, 8, 10), n_calib)  (held-out stream 10,
           §0, = GB'); noise E from default_rng(score.SEED_GATE), shared by every k (common random numbers, as
           in score.gb_prime).  §2.3 uses the first n_phase of the same queries.
  network  m = score.tweedie_real, Jr = dm/dx (real 2N x 2N, float64 autodiff on `--device`, score.jac_batch),
           J = score.wirtinger(Jr) = 0.5[(A+D) + j(C-B)],  K = 0.5[(A-D) + j(C+B)]  (§2.4).
  §2.2     V1: Sigma = nu project_psd(J).  V0: Sigma = nu Herm(J).  GMM b*: Sigma = exact posterior Cov.
           rho_tr = E||h-m||^2 / E tr Sigma, both on the full space and on the unfloored subspace.
           Unfloored subspace = eigen-directions of Herm(J) (GMM: Cov/nu) with eigenvalue > 10*floor, where
           floor = C.LAM_MIN is the project_psd floor.  On that subspace V0 and V1 have the same eigenpairs, so
           rho_sub, d^2 and coverage are one number for both.  d^2 = sum_S |v_i^H(h-m)|^2 / (nu lam_i), reported
           as d^2/dim.  Nominal 50/90% coverage uses the PROPER complex-Gaussian reference 2 d^2 ~ chi2(2 dim).
           Also: floored error mass and floored |eigen| mass (fractions) with mean counts; the eigen-direction
           calibration slope (rank quintiles of the Sigma eigenvalues x mean actual projected variance, OLS slope
           in log-log over the 5 bins); PSD floor hit ratio (lam_min(Herm J) < floor).
           V0 gets rho_tr (full space), plus coverage on its PSD subset (lam_min(Herm J) >= 0) with that fraction.
  §2.3     eps_phi = ||e^{-j phi} D(e^{j phi} q) - D(q)|| / ||D(q)||,   eps_J = ||J(e^{j phi} q) - J(q)||_F / ||J(q)||_F
           (raw Wirtinger J), phi = 2 pi k'/8 for k' = 0..7.  D(q) and J(q) come from the §2.2 pass.  So k' = 0
           re-evaluates the same input (a determinism check, 0 by construction -- at n_phase = 4*chunk even the
           batch composition is identical), and the PRIMARY equivariance statistics pool k' = 1..7; the literal
           k' = 0..7 pooling and the ratio of medians are reported next to it and the rule line says whether the
           C-phase verdict depends on the reading.  ratio = eps_phi / (||D(q)-h||/||h||) per (sample, k');
           tier value = median over the tier's grid points of the per-point medians (§2.3).
  §2.4     r_P = ||nu K||_F / max(||nu J||_F, eps) with J in {V1 = project_psd(J), V0 = Herm(J), raw J}.
           GMM: r_P = ||P||_F / ||Cov||_F, P = sum_k w_k mu_k mu_k^T - m m^T (the component posteriors are proper,
           so they carry no pseudo-covariance of their own).  This runs FIRST: an improper linear-Gaussian toy
           (exact posterior) must reproduce Cov and P through the same autodiff + (J, K) transform to 1e-12
           relative, or the script stops.
  checks   GMM GPU batch vs CPU GMMPriorB.denoise_full (1e-10, 01_RULES §9.4 G1); GMM closed-form (Cov, P) vs the
           autodiff (J, K) of score.ExactGMMTorch (1e-10; the K error is scaled by ||Cov||, the r_P denominator);
           V1 eigen-floor == score.project_psd (1e-12).
Rules evaluated here: §2.6 C-phase / §1 H3(a) (tier ratios), and §1 H2 / §2.6 C-calib (count of grid points where
V1 has rho_tr in [0.8, 1.25] and cov90 in [0.85, 0.95], both on the unfloored subspace).  H4 / C-pseudo use r_P
at receiver ITERATION 4 (real queries) and are NOT decided here: the held-out r_P is report-only.
"""
import argparse, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, torch
from scipy.stats import chi2
import common as C, score, arms as A, sigma as SG, runner as R

NR, NT = 8, 4
N = NR * NT
TESTBED, PRIOR = "D2", "S2"
OUT = os.path.join(C.CONF, "results", "review_next")
# ---- fixed by NEXT_EXPERIMENTS v3 -- pre-registered, not hyper-parameters
TIERS = {"low": range(0, 7), "mid": range(7, 15), "high": range(15, 20)}   # §0, 0-based k
FLOOR, SUB = C.LAM_MIN, 10.0                   # §2.2: unfloored subspace = eigenvalue > SUB * FLOOR
N_PHI = 8                                      # §2.3: phi = 2 pi k'/8, k' = 0..7
RHO_BAND, COV90_BAND, H2_MIN, CCALIB_MIN = (0.8, 1.25), (0.85, 0.95), 14, 7   # §1 H2, §2.6 C-calib
CPHASE = 0.10                                  # §2.6 C-phase / §1 H3(a)
TOY_TOL, GMM_TOL, PSD_TOL = 1e-12, 1e-10, 1e-12
EPS = 1e-300
REGISTERED = dict(ckpt=os.path.join(C.CONF, "ckpt", "d2sx_N160000_a1.pt"), gmm_tag="B16e4k", gmm_ntrain=160000,
                  n_calib=2048, n_phase=512)


def pseudo_K(Jr):
    """(..., 2N, 2N) real Jacobian -> K = dm/dq* = 0.5[(A-D) + j(C+B)] (§2.4).  For an exact MMSE denoiser
    nu K = E[(h-m)(h-m)^T | q], just as nu * score.wirtinger(Jr) = E[(h-m)(h-m)^H | q]."""
    n = Jr.shape[-1] // 2
    a, b, c, d = Jr[..., :n, :n], Jr[..., :n, n:], Jr[..., n:, :n], Jr[..., n:, n:]
    return 0.5 * torch.complex(a - d, c + b)


def net_eval(model, Q, sg, dev, chunk):
    """(m, J, K) of the one-shot Tweedie denoiser at complex queries Q (n, N): float64 autodiff on `dev`,
    `chunk` samples per vmap(jacrev) call (the memory knob)."""
    X = torch.as_tensor(score.np_pack(Q), dtype=torch.float64, device=dev)
    f = lambda v, u: score.tweedie_real(model, v, u)
    M, J, K = [], [], []
    for i in range(0, len(X), chunk):
        x = X[i:i + chunk]
        s = torch.full((len(x),), float(sg), dtype=x.dtype, device=dev)
        Jr = score.jac_batch(f, x, s)
        with torch.no_grad():
            M.append(score._unpack(f(x, s)))
        J.append(score.wirtinger(Jr))
        K.append(pseudo_K(Jr))
    return torch.cat(M), torch.cat(J), torch.cat(K)


def gmm_eval(G, Q, nu, dev, chunk):
    """Exact GMM b* posterior (m, Cov, P) for a batch.  These are score.gmm_denoise_batch's formulas plus both
    second moments: Cov = sum_k w_k S_k + sum_k w_k mu_k mu_k^H - m m^H (= nu * GMMPriorB.denoise_full's J),
    P = sum_k w_k mu_k mu_k^T - m m^T."""
    U, lam, logpi = G
    g = lam / (lam + nu)
    base = logpi - torch.log(lam + nu).sum(1)
    S = ((U * (nu * g).to(U.dtype)[:, None, :]) @ U.conj().transpose(1, 2)).reshape(len(U), -1)  # (K, N*N)
    M, Cv, P = [], [], []
    for i in range(0, len(Q), chunk):
        q = torch.as_tensor(Q[i:i + chunk], dtype=torch.complex128, device=dev)
        z = torch.einsum("kji,bj->bki", U.conj(), q)                                  # U_k^H q
        w = torch.softmax(base - (z.abs() ** 2 / (lam + nu)).sum(2), dim=1).to(z.dtype)
        mk = torch.einsum("kij,bkj->bki", U, g * z)                                   # component means
        m = torch.einsum("bk,bki->bi", w, mk)
        wm = (mk * w[..., None]).transpose(1, 2)                                      # (B, N, K)
        Cv.append((w @ S).reshape(-1, N, N) + wm @ mk.conj() - m[:, :, None] * m.conj()[:, None, :])
        P.append(wm @ mk - m[:, :, None] * m[:, None, :])
        M.append(m)
    return torch.cat(M), torch.cat(Cv), torch.cat(P)


def rel(a, b):
    return float(np.linalg.norm(a - b) / max(np.linalg.norm(b), EPS))


class _LinGauss(torch.nn.Module):
    """Exact posterior-mean denoiser of an IMPROPER Gaussian prior x ~ N(0, S) in the real 2N domain.  S is
    generic (S_rr != S_ii, S_ri != -S_ir^T), so the posterior pseudo-covariance is non-zero.
    score_real = -(S + s^2 I)^{-1} x."""

    def __init__(self, S):
        super().__init__()
        self.register_buffer("S", S)

    def score_real(self, x, sigma):
        I = torch.eye(len(self.S), dtype=self.S.dtype, device=self.S.device)
        return -torch.linalg.solve(self.S + (sigma ** 2)[..., None, None] * I, x.unsqueeze(-1)).squeeze(-1)


def toy_check(sgs, dev, chunk, n=4):
    """§2.4: the (J, K) transform must reproduce the exact complex covariance and pseudo-covariance, from a
    DIFFERENT closed form (Sigma_post = (S^-1 + I/s^2)^-1), to TOY_TOL relative.  Raises otherwise."""
    rng = np.random.default_rng(score.SEED_GATE)
    W = rng.standard_normal((2 * N, 2 * N))
    S = W @ W.T / (2 * N) + 0.05 * np.eye(2 * N)
    model = _LinGauss(torch.as_tensor(S, dtype=torch.float64, device=dev))
    worst = dict(J=0.0, K=0.0, rP=0.0, P_over_Cov_min=np.inf)
    for sg in sgs:
        nu = 2.0 * sg ** 2
        Sp = np.linalg.inv(np.linalg.inv(S) + np.eye(2 * N) / sg ** 2)
        rr, ri, ir, ii = Sp[:N, :N], Sp[:N, N:], Sp[N:, :N], Sp[N:, N:]
        Cov, P = rr + ii + 1j * (ir - ri), rr - ii + 1j * (ir + ri)
        Q = (rng.standard_normal((n, N)) + 1j * rng.standard_normal((n, N))) / np.sqrt(2)
        _, J, K = net_eval(model, Q, sg, dev, chunk)
        J, K = J.cpu().numpy(), K.cpu().numpy()
        rp = np.linalg.norm(P) / np.linalg.norm(Cov)
        worst["P_over_Cov_min"] = min(worst["P_over_Cov_min"], rp)
        for j in range(n):
            worst["J"] = max(worst["J"], rel(nu * J[j], Cov))
            worst["K"] = max(worst["K"], rel(nu * K[j], P))
            worst["rP"] = max(worst["rP"], abs(np.linalg.norm(K[j]) / np.linalg.norm(J[j]) - rp) / rp)
    if max(worst["J"], worst["K"], worst["rP"]) > TOY_TOL:
        raise SystemExit(f"TOY CHECK FAILED (tol {TOY_TOL:g}): {worst} -- the (J, K) transform is wrong; nothing written")
    return worst


def calib_stats(lam, proj, err2, nu):
    """Per-sample §2.2 quantities.  lam (n, N) = ascending spectrum of the dimensionless Herm J (GMM: Cov/nu);
    proj (n, N) = |v_i^H (h - m)|^2 along its eigenvectors; err2 = ||h - m||^2."""
    S = lam > SUB * FLOOR
    dim = S.sum(1)
    d2 = np.where(S, proj / (nu * np.where(S, lam, 1.0)), 0.0).sum(1)
    ok = dim > 0
    in50, in90 = np.full(len(lam), np.nan), np.full(len(lam), np.nan)
    in50[ok] = 2 * d2[ok] <= chi2.ppf(0.5, 2 * dim[ok])
    in90[ok] = 2 * d2[ok] <= chi2.ppf(0.9, 2 * dim[ok])
    return dict(dim=dim, d2=d2, d2_dim=np.where(ok, d2 / np.maximum(dim, 1), np.nan), in50=in50, in90=in90,
                err_sub=np.where(S, proj, 0.0).sum(1), tr_sub=nu * np.where(S, lam, 0.0).sum(1),
                err_excl=err2 - np.where(S, proj, 0.0).sum(1),
                eig_excl=np.where(S, 0.0, np.abs(lam)).sum(1), eig_abs=np.abs(lam).sum(1),
                tr_v0=nu * lam.sum(1), tr_v1=nu * np.maximum(lam, FLOOR).sum(1),
                n_excl=N - dim, n_floor=(lam < FLOOR).sum(1), lmin=lam[:, 0])


def calib_slope(lam, proj, nu):
    """Eigen-direction calibration: pool (sample, direction) pairs of the unfloored subspace, split by the RANK of
    the predicted variance nu*lam into 5 quintiles, and fit the OLS slope of log(mean actual) on log(mean predicted).
    A slope of 1 with a zero offset means calibrated.  Returns (slope, bins (5, 2) = [mean predicted, mean actual])."""
    S = lam > SUB * FLOOR
    s, p = nu * lam[S], proj[S]
    if len(s) < 5:
        return np.nan, np.full((5, 2), np.nan)
    bins = np.array([[s[i].mean(), p[i].mean()] for i in np.array_split(np.argsort(s), 5)])
    return float(np.polyfit(np.log(bins[:, 0]), np.log(bins[:, 1]), 1)[0]), bins


def point_calib(cs, err2, full_tr):
    lmin, psd = cs["lmin"], cs["lmin"] >= 0.0
    return dict(rho_full=float(err2.sum() / cs[full_tr].sum()), rho_sub=float(cs["err_sub"].sum() / cs["tr_sub"].sum()),
                d2dim_med=float(np.nanmedian(cs["d2_dim"])), cov50=float(np.nanmean(cs["in50"])),
                cov90=float(np.nanmean(cs["in90"])), floor_hit=float(np.mean(lmin < FLOOR)),
                n_floor=float(cs["n_floor"].mean()), n_excl=float(cs["n_excl"].mean()),
                fl_err=float(cs["err_excl"].sum() / err2.sum()), fl_eig=float(cs["eig_excl"].sum() / cs["eig_abs"].sum()),
                psd_frac=float(psd.mean()),
                cov50_psd=float(np.nanmean(cs["in50"][psd])) if psd.any() else np.nan,
                cov90_psd=float(np.nanmean(cs["in90"][psd])) if psd.any() else np.nan)


def tier_median(vals, ks):
    """§2.3 tier rule, used for every tier summary: median over the tier's evaluated grid points of the per-point value."""
    return {t: (float(np.median([vals[ks.index(k)] for k in r if k in ks])) if any(k in ks for k in r) else np.nan)
            for t, r in TIERS.items()}


def in_band(x, band):
    return band[0] <= x <= band[1]


def main(a):
    torch.set_default_dtype(torch.float64)
    torch.set_num_threads(a.threads)
    dev = torch.device(a.device)
    if dev.type == "cuda" and not torch.cuda.is_available():
        raise SystemExit("--device cuda requested but CUDA is unavailable (set CUDA_VISIBLE_DEVICES to a free GPU)")
    if a.smoke:
        a.n_calib, a.n_phase, a.ks = 32, 32, a.ks or [0, 10, 19]
    ks = sorted(a.ks) if a.ks else list(range(20))
    assert a.n_phase <= a.n_calib and all(0 <= k < 20 for k in ks)
    sfx = "_smoke" if a.smoke else ""
    out = os.path.abspath(a.out or os.path.join(OUT, f"p1_heldout{sfx}"))
    if os.path.commonpath([out, OUT]) != OUT or (a.smoke and not os.path.basename(out).endswith("_smoke")):
        raise SystemExit(f"--out must stay under {OUT} (§0 result preservation) and end in _smoke for --smoke")
    if not a.smoke and not a.overwrite and (os.path.exists(out + ".npz") or os.path.exists(out + ".txt")):
        raise SystemExit(f"{out}.npz/.txt exists -- results are never overwritten silently (pass --overwrite)")
    registered = (ks == list(range(20)) and a.n_calib == REGISTERED["n_calib"] and a.n_phase == REGISTERED["n_phase"]
                  and os.path.abspath(a.ckpt) == REGISTERED["ckpt"] and a.gmm_tag == REGISTERED["gmm_tag"]
                  and a.gmm_ntrain == REGISTERED["gmm_ntrain"])
    t_start = time.time()

    # ---- the GMM b* of the headline (§0): runner routes arms.D2_FITS to gmm_fits_D2_<tag>
    R._init(a.gmm_tag)
    fits, llv, bstar, kron_K = A.gmm_selection(TESTBED, PRIOR, NR, a.gmm_ntrain)
    fam, KK = ("kron", kron_K) if bstar == "kron" else ("full", int(bstar[3:]))
    if (a.gmm_tag, a.gmm_ntrain) == (REGISTERED["gmm_tag"], REGISTERED["gmm_ntrain"]):
        assert (fam, KK) == ("kron", 1024), f"§0 fixes b* = kron K=1024, fits dir gives {fam} K={KK}"
    gmm = C.GMMPriorB(NR, NT, fits[(fam, KK)]["covs"], fits[(fam, KK)]["pi"])
    G = (torch.as_tensor(gmm.U, dtype=torch.complex128, device=dev),
         torch.as_tensor(gmm.lam, dtype=torch.float64, device=dev),
         torch.as_tensor(np.log(gmm.pi), dtype=torch.float64, device=dev))
    gmm_ad = score.ExactGMMTorch(gmm).to(dev)

    model = score._as_model(a.ckpt, NR, NT, dev)[0]
    cid = score.ckpt_identity(a.ckpt)
    nu_grid, sig_grid = SG.load(TESTBED)            # the FROZEN D2 grid (checkpoint carries no sigma_tag)
    gen = C.make_gen(TESTBED, PRIOR, NR, NT)
    H = gen.sample_vecs(C.train_rng(TESTBED, PRIOR, NR, 10), a.n_calib)
    nrng = np.random.default_rng(score.SEED_GATE)
    E = (nrng.standard_normal((a.n_calib, N)) + 1j * nrng.standard_normal((a.n_calib, N))) / np.sqrt(2)
    Ht = torch.as_tensor(H, dtype=torch.complex128, device=dev)
    h2 = np.sum(np.abs(H) ** 2, 1)
    phis = 2 * np.pi * np.arange(N_PHI) / N_PHI
    urot = torch.as_tensor(np.exp(-1j * phis), dtype=torch.complex128, device=dev)

    gpu = torch.cuda.get_device_name(dev) if dev.type == "cuda" else "cpu"
    hdr = C.header(TESTBED, extra=[
        "content     : NEXT_EXPERIMENTS v3 §2.2 / §2.3 / §2.4, HELD-OUT AWGN halves (P1-2, P1-3, P1-4). P1-x diagnostic, NOT a gate",
        f"script      : conf/code/diag_p1_heldout.py sha256[:16]={C.file_sha(os.path.abspath(__file__))}",
        f"this script : network Jacobians + GMM control on {dev} ({gpu}), CUDA_VISIBLE_DEVICES="
        f"{os.environ.get('CUDA_VISIBLE_DEVICES', '<unset>')}, float64/complex128; the receiver is NOT run",
        f"ckpt        : {os.path.abspath(a.ckpt)}",
        f"ckpt id     : {R.stagec_id_str(a.ckpt)}",
        f"GMM b*      : tag {a.gmm_tag}, fits {A.D2_FITS}, N_train {a.gmm_ntrain}, bstar={bstar} -> {fam} K={KK}",
        f"queries     : h = gen.sample_vecs(C.train_rng('{TESTBED}','{PRIOR}',{NR},10), n)  noise E ~ default_rng(score.SEED_GATE={score.SEED_GATE}) (shared over k)",
        f"n           : n_calib = {a.n_calib} (§2.2, §2.4)   n_phase = {a.n_phase} (§2.3, first n_phase of the same queries)"
        + ("   ** SMOKE **" if a.smoke else "") + ("" if registered else "   ** NOT the registered n/grid/ckpt: no verdict **"),
        f"grid        : frozen D2 (sigma_grid_D2.npz), ks = {ks}; tiers low k0-6 / mid k7-14 / high k15-19",
        f"registered  : floor = C.LAM_MIN = {FLOOR:g}, unfloored subspace = eig > {SUB:g}*floor; phi = 2 pi k'/{N_PHI}; "
        f"bands rho {RHO_BAND} cov90 {COV90_BAND}; H2 >= {H2_MIN}/20 satisfying; C-calib >= {CCALIB_MIN}/20 violating; C-phase >= {CPHASE}",
        f"seeds       : h = C.train_rng stream 10 (above); noise E and the toy S each from a fresh default_rng(SEED_GATE); no other randomness",
    ])
    print(hdr, flush=True)

    # ---- §2.4: the transform check runs FIRST and stops the script on failure
    toy = toy_check([float(sig_grid[k]) for k in ks], dev, a.chunk)
    print(f"# toy (improper linear-Gaussian, exact posterior) max rel err: nu*J vs Cov {toy['J']:.2e}   "
          f"nu*K vs P {toy['K']:.2e}   r_P {toy['rP']:.2e}   (tol {TOY_TOL:g}; min |P|/|Cov| = {toy['P_over_Cov_min']:.3f}) PASS",
          flush=True)

    keep = {}                                   # per-sample arrays, stacked over ks
    rows = []                                   # per-point summaries
    chk = dict(gmm_cpu=0.0, gmm_ad_J=0.0, gmm_ad_K=0.0, v1_psd=0.0)

    def push(name, v):
        keep.setdefault(name, []).append(np.asarray(v))

    for k in ks:
        t0 = time.time()
        nu, sg = float(nu_grid[k]), float(sig_grid[k])
        Q = H + np.sqrt(nu) * E
        # ---- network, §2.2 / §2.4 pass
        m, J, Kp = net_eval(model, Q, sg, dev, a.chunk)
        HJ = 0.5 * (J + J.conj().transpose(1, 2))
        lam, V = torch.linalg.eigh(HJ)
        e = Ht - m
        proj = ((V.conj().transpose(1, 2) @ e[..., None]).squeeze(-1).abs() ** 2).cpu().numpy()
        lam_n, err2 = lam.cpu().numpy(), (e.abs() ** 2).sum(1).cpu().numpy()
        Kf = torch.linalg.norm(Kp, dim=(-2, -1)).cpu().numpy()
        Jf = torch.linalg.norm(J, dim=(-2, -1)).cpu().numpy()
        Jnp = J[:a.n_check].cpu().numpy()
        Vn = V[:a.n_check].cpu().numpy()
        for j in range(len(Jnp)):               # V1 (eigen floor on HJ) is exactly what the receiver's V1 consumes
            ref = nu * score.project_psd(Jnp[j])
            chk["v1_psd"] = max(chk["v1_psd"], rel(nu * (Vn[j] * np.maximum(lam_n[j], FLOOR)) @ Vn[j].conj().T, ref))
        # ---- GMM b* control
        mg, Cg, Pg = gmm_eval(G, Q, nu, dev, a.gmm_chunk)
        lamg, Vg = torch.linalg.eigh(0.5 * (Cg + Cg.conj().transpose(1, 2)) / nu)
        eg = Ht - mg
        projg = ((Vg.conj().transpose(1, 2) @ eg[..., None]).squeeze(-1).abs() ** 2).cpu().numpy()
        lamg_n, err2g = lamg.cpu().numpy(), (eg.abs() ** 2).sum(1).cpu().numpy()
        Pf = torch.linalg.norm(Pg, dim=(-2, -1)).cpu().numpy()
        Cf = torch.linalg.norm(Cg, dim=(-2, -1)).cpu().numpy()
        nc = min(a.n_check, a.n_calib)
        mgc, Cgc, Pgc = mg[:nc].cpu().numpy(), Cg[:nc].cpu().numpy(), Pg[:nc].cpu().numpy()
        _, Jad, Kad = net_eval(gmm_ad, Q[:nc], sg, dev, a.chunk)
        Jad, Kad = Jad.cpu().numpy(), Kad.cpu().numpy()
        for j in range(nc):
            mc, Jc = gmm.denoise_full(Q[j], nu)
            chk["gmm_cpu"] = max(chk["gmm_cpu"], rel(mgc[j], mc), rel(Cgc[j], nu * Jc))
            chk["gmm_ad_J"] = max(chk["gmm_ad_J"], rel(nu * Jad[j], Cgc[j]))
            # scaled by ||Cov|| = the r_P denominator: at low sigma P ~ 1e-5 ||Cov|| is a cancellation residue of
            # sum_k w_k mu_k mu_k^T - m m^T (||m||^2 ~ 4e3 ||Cov||), so a relative-to-||P|| test measures round-off
            chk["gmm_ad_K"] = max(chk["gmm_ad_K"], float(np.linalg.norm(nu * Kad[j] - Pgc[j]) / np.linalg.norm(Cgc[j])))
        # ---- §2.3 phase pass on the first n_phase queries, k' = 0..7 in one batch
        npf = a.n_phase
        Qp = (np.exp(1j * phis)[:, None, None] * Q[None, :npf]).reshape(-1, N)
        mp, Jp, _ = net_eval(model, Qp, sg, dev, a.chunk)
        mp, Jp = mp.reshape(N_PHI, npf, N), Jp.reshape(N_PHI, npf, N, N)
        eps = ((urot[:, None, None] * mp - m[:npf]).norm(dim=-1) / m[:npf].norm(dim=-1)).cpu().numpy()
        epsJ = (torch.linalg.norm(Jp - J[:npf], dim=(-2, -1)) / torch.linalg.norm(J[:npf], dim=(-2, -1))).cpu().numpy()
        delta = ((m[:npf] - Ht[:npf]).norm(dim=-1) / Ht[:npf].norm(dim=-1)).cpu().numpy()
        mgp, Cgp, _ = gmm_eval(G, Qp, nu, dev, a.gmm_chunk)
        mgp, Cgp = mgp.reshape(N_PHI, npf, N), Cgp.reshape(N_PHI, npf, N, N)
        epsg = ((urot[:, None, None] * mgp - mg[:npf]).norm(dim=-1) / mg[:npf].norm(dim=-1)).cpu().numpy()
        epsJg = (torch.linalg.norm(Cgp - Cg[:npf], dim=(-2, -1)) / torch.linalg.norm(Cg[:npf], dim=(-2, -1))).cpu().numpy()
        deltag = ((mg[:npf] - Ht[:npf]).norm(dim=-1) / Ht[:npf].norm(dim=-1)).cpu().numpy()

        # ---- per-sample derived quantities
        cs, csg = calib_stats(lam_n, proj, err2, nu), calib_stats(lamg_n, projg, err2g, nu)
        slope, sbins = calib_slope(lam_n, proj, nu)
        slopeg, sbinsg = calib_slope(lamg_n, projg, nu)
        rP_V1 = Kf / np.maximum(np.sqrt((np.maximum(lam_n, FLOOR) ** 2).sum(1)), EPS)
        rP_V0 = Kf / np.maximum(np.sqrt((lam_n ** 2).sum(1)), EPS)
        rP_raw = Kf / np.maximum(Jf, EPS)
        rP_g = Pf / np.maximum(Cf, EPS)
        ratio, ratiog = eps / delta[None], epsg / deltag[None]

        for nm, v in (("calib|net_lam", lam_n), ("calib|net_proj", proj), ("calib|net_err2", err2), ("calib|h2", h2),
                      ("calib|gmm_lam", lamg_n), ("calib|gmm_proj", projg), ("calib|gmm_err2", err2g),
                      ("calib|net_slope_bins", sbins), ("calib|gmm_slope_bins", sbinsg),
                      ("pseudo|net_Kf", Kf), ("pseudo|net_Jf_raw", Jf), ("pseudo|net_rP_V1", rP_V1),
                      ("pseudo|net_rP_V0", rP_V0), ("pseudo|net_rP_raw", rP_raw),
                      ("pseudo|gmm_Pf", Pf), ("pseudo|gmm_Covf", Cf), ("pseudo|gmm_rP", rP_g),
                      ("phase|net_eps", eps), ("phase|net_epsJ", epsJ), ("phase|net_delta", delta),
                      ("phase|gmm_eps", epsg), ("phase|gmm_epsJ", epsJg), ("phase|gmm_delta", deltag)):
            push(nm, v)
        for q in ("d2", "dim", "in50", "in90", "lmin"):
            push(f"calib|net_{q}", cs[q]); push(f"calib|gmm_{q}", csg[q])

        r = dict(k=k, nu=nu, sigma=sg)
        r.update({f"v_{q}": v for q, v in point_calib(cs, err2, "tr_v1").items()})
        r["v0_rho_full"] = float(err2.sum() / cs["tr_v0"].sum())
        r["v_slope"] = slope
        r.update({f"g_{q}": v for q, v in point_calib(csg, err2g, "tr_v0").items()})
        r["g_slope"] = slopeg
        r.update(nmse_net=float(err2.sum() / h2.sum()), nmse_gmm=float(err2g.sum() / h2.sum()))
        r.update(rP_V1_med=float(np.median(rP_V1)), rP_V1_max=float(rP_V1.max()),
                 rP_V0_med=float(np.median(rP_V0)), rP_V0_max=float(rP_V0.max()),
                 rP_raw_med=float(np.median(rP_raw)), rP_raw_max=float(rP_raw.max()),
                 rP_g_med=float(np.median(rP_g)), rP_g_max=float(rP_g.max()))
        r.update(eps_med=float(np.median(eps[1:])), eps_max=float(eps[1:].max()),
                 epsJ_med=float(np.median(epsJ[1:])), epsJ_max=float(epsJ[1:].max()),
                 delta_med=float(np.median(delta)), ratio_med=float(np.median(ratio[1:])),
                 ratio_med_k0incl=float(np.median(ratio)), ratio_of_meds=float(np.median(eps[1:]) / np.median(delta)),
                 eps0_max=float(eps[0].max()), epsJ0_max=float(epsJ[0].max()),
                 g_eps_med=float(np.median(epsg[1:])), g_eps_max=float(epsg[1:].max()),
                 g_epsJ_max=float(epsJg[1:].max()), g_delta_med=float(np.median(deltag)),
                 g_ratio_med=float(np.median(ratiog[1:])))
        r["h2_ok"] = bool(in_band(r["v_rho_sub"], RHO_BAND) and in_band(r["v_cov90"], COV90_BAND))
        r["h2_ok_fullrho"] = bool(in_band(r["v_rho_full"], RHO_BAND) and in_band(r["v_cov90"], COV90_BAND))
        rows.append(r)
        mem = f"  peak GPU mem {torch.cuda.max_memory_allocated(dev) / 2**30:.2f} GiB" if dev.type == "cuda" else ""
        print(f"# k={k:2d} sigma={sg:.4f} done in {time.time() - t0:.1f} s{mem}", flush=True)

    # ---- checks
    bad = [f"{q}={v:.2e}" for q, v in chk.items() if v > (PSD_TOL if q == "v1_psd" else GMM_TOL)]
    if bad:
        raise SystemExit("CONSISTENCY CHECK FAILED: " + ", ".join(bad) + " -- nothing written")

    # ---- summary text
    L = [hdr, f"# toy check: nu*J vs Cov {toy['J']:.2e}, nu*K vs P {toy['K']:.2e}, r_P {toy['rP']:.2e} (tol {TOY_TOL:g}) PASS",
         f"# checks  : GMM GPU vs CPU denoise_full {chk['gmm_cpu']:.2e}; GMM closed-form vs ExactGMMTorch autodiff "
         f"J {chk['gmm_ad_J']:.2e} K(pseudo, /||Cov||) {chk['gmm_ad_K']:.2e} (tol {GMM_TOL:g}); V1 eigen-floor vs score.project_psd "
         f"{chk['v1_psd']:.2e} (tol {PSD_TOL:g}); first {a.n_check} samples per point"]
    L.append("\n## §2.2 calibration (held-out).  V1 = nu*project_psd(J); rho_sub/d2/cov on the unfloored subspace "
             "(identical for V0 and V1); cov50/90 = nominal coverage, proper-CN reference")
    L.append(f"{'k':>2} {'sigma':>7} | {'rhoV1':>7} {'rhoV0':>7} {'rho_sub':>7} {'d2/dim':>7} {'cov50':>6} {'cov90':>6} "
             f"{'slope':>6} {'fhit':>5} {'n<fl':>5} {'nexcl':>5} {'flErr':>6} {'flEig':>6} | {'V0psd':>5} {'c90psd':>6} "
             f"| {'H2':>2} | GMM {'rho':>6} {'rho_sub':>7} {'d2/dim':>6} {'cov50':>6} {'cov90':>6} {'slope':>6} | {'nmseN':>7} {'nmseG':>7}")
    for r in rows:
        L.append(f"{r['k']:>2} {r['sigma']:7.4f} | {r['v_rho_full']:7.3f} {r['v0_rho_full']:7.3f} {r['v_rho_sub']:7.3f} "
                 f"{r['v_d2dim_med']:7.3f} {r['v_cov50']:6.3f} {r['v_cov90']:6.3f} {r['v_slope']:6.3f} {r['v_floor_hit']:5.2f} "
                 f"{r['v_n_floor']:5.1f} {r['v_n_excl']:5.1f} {r['v_fl_err']:6.3f} {r['v_fl_eig']:6.3f} | {r['v_psd_frac']:5.2f} "
                 f"{r['v_cov90_psd']:6.3f} | {'Y' if r['h2_ok'] else 'n':>2} |     {r['g_rho_full']:6.3f} {r['g_rho_sub']:7.3f} "
                 f"{r['g_d2dim_med']:6.3f} {r['g_cov50']:6.3f} {r['g_cov90']:6.3f} {r['g_slope']:6.3f} | "
                 f"{r['nmse_net']:7.4f} {r['nmse_gmm']:7.4f}")
    L.append("\n## §2.3 global-phase equivariance (held-out).  eps/epsJ pooled over k'=1..7; ratio = eps_phi/delta, "
             "delta = ||D(q)-h||/||h||; eps0 = k'=0 re-evaluation (numerical floor)")
    L.append(f"{'k':>2} {'sigma':>7} | {'eps_med':>9} {'eps_max':>9} {'epsJ_med':>9} {'epsJ_max':>9} {'delta_med':>9} "
             f"{'RATIO_med':>9} {'r(k0incl)':>9} {'r_of_meds':>9} {'eps0_max':>9} | GMM {'eps_med':>9} {'eps_max':>9} "
             f"{'epsJ_max':>9} {'ratio_med':>9}")
    for r in rows:
        L.append(f"{r['k']:>2} {r['sigma']:7.4f} | {r['eps_med']:9.3e} {r['eps_max']:9.3e} {r['epsJ_med']:9.3e} "
                 f"{r['epsJ_max']:9.3e} {r['delta_med']:9.3e} {r['ratio_med']:9.4f} {r['ratio_med_k0incl']:9.4f} "
                 f"{r['ratio_of_meds']:9.4f} {r['eps0_max']:9.2e} |     {r['g_eps_med']:9.2e} {r['g_eps_max']:9.2e} "
                 f"{r['g_epsJ_max']:9.2e} {r['g_ratio_med']:9.2e}")
    L.append("\n## §2.4 pseudo-covariance (held-out, REPORT-ONLY; H4 is judged at receiver iteration 4 on real queries)")
    L.append(f"{'k':>2} {'sigma':>7} | {'rP_V1_med':>9} {'rP_V1_max':>9} {'rP_V0_med':>9} {'rP_V0_max':>9} "
             f"{'rP_raw_med':>10} | GMM {'rP_med':>9} {'rP_max':>9}")
    for r in rows:
        L.append(f"{r['k']:>2} {r['sigma']:7.4f} | {r['rP_V1_med']:9.4f} {r['rP_V1_max']:9.4f} {r['rP_V0_med']:9.4f} "
                 f"{r['rP_V0_max']:9.4f} {r['rP_raw_med']:10.4f} |     {r['rP_g_med']:9.4f} {r['rP_g_max']:9.4f}")

    col = lambda f: [r[f] for r in rows]
    L.append("\n## tiers (median over the tier's evaluated grid points of the per-point value; §2.3 rule applied to every row)")
    L.append(f"{'quantity':<34} {'low k0-6':>10} {'mid k7-14':>10} {'high k15-19':>12}")
    for lab, f in (("phase ratio (PRIMARY, k'=1..7)", "ratio_med"), ("phase ratio (k'=0..7 literal)", "ratio_med_k0incl"),
                   ("phase ratio-of-medians", "ratio_of_meds"), ("eps_phi median", "eps_med"), ("eps_J median", "epsJ_med"),
                   ("GMM phase ratio", "g_ratio_med"), ("V1 rho_sub", "v_rho_sub"), ("V1 rho_full", "v_rho_full"),
                   ("V0 rho_full", "v0_rho_full"), ("V1 cov90", "v_cov90"), ("V1 d2/dim median", "v_d2dim_med"),
                   ("V1 floored error mass", "v_fl_err"), ("GMM rho_full", "g_rho_full"), ("GMM cov90", "g_cov90"),
                   ("r_P V1 median", "rP_V1_med"), ("r_P V0 median", "rP_V0_med"), ("GMM r_P median", "rP_g_med")):
        t = tier_median(col(f), ks)
        L.append(f"{lab:<34} {t['low']:10.4f} {t['mid']:10.4f} {t['high']:12.4f}")

    verdict = "" if registered else "  [NOT A VERDICT: n/grid/ckpt differ from the registered run]"
    robust = lambda same: "reading-robust" if same else "** READING-DEPENDENT: the verdict needs a user decision (DECISIONS.md) **"

    def cphase(f):
        t = tier_median(col(f), ks)
        return t, [q for q, v in t.items() if np.isfinite(v) and v >= CPHASE]
    tr, over = cphase("ratio_med")
    alt = {lab: bool(cphase(f)[1]) for lab, f in (("k'=0..7 literal", "ratio_med_k0incl"), ("ratio-of-medians", "ratio_of_meds"))}
    L.append("\n## rules")
    L.append(f"C-phase (§2.6) / H3(a) (§1): tier ratios low {tr['low']:.4f} mid {tr['mid']:.4f} high {tr['high']:.4f}; "
             f"tiers >= {CPHASE}: {over or 'none'} -> "
             + ("C-phase SATISFIED (A1)" if over else "C-phase NOT satisfied = H3(a) rejects: no augmentation") + verdict)
    L.append("   (alternative readings: " + ", ".join(f"{lab} -> {'SATISFIED' if v else 'not satisfied'}" for lab, v in alt.items())
             + f"; {robust(all(v == bool(over) for v in alt.values()))})")

    def h2_verdict(nok):
        return ("H2 REJECTED, C-calib not satisfied" if nok >= H2_MIN else
                "H2 NOT rejected, C-calib SATISFIED" if len(rows) - nok >= CCALIB_MIN else "undetermined")
    n_ok = sum(r["h2_ok"] for r in rows)
    n_ok_full = sum(r["h2_ok_fullrho"] for r in rows)
    per_t = {t: sum(r["h2_ok"] for r in rows if r["k"] in rg) for t, rg in TIERS.items()}
    L.append(f"H2 (§1) / C-calib (§2.6): V1 grid points with rho_sub in {list(RHO_BAND)} AND cov90 in {list(COV90_BAND)}: "
             f"{n_ok}/{len(rows)} (low {per_t['low']}, mid {per_t['mid']}, high {per_t['high']}); violating {len(rows) - n_ok}. "
             f"H2 rejected iff >= {H2_MIN}/20 satisfy; C-calib satisfied iff >= {CCALIB_MIN}/20 violate -> "
             + h2_verdict(n_ok) + verdict)
    L.append(f"   (alternative reading, full-space rho_tr instead of rho_sub: {n_ok_full}/{len(rows)} satisfy -> "
             f"{h2_verdict(n_ok_full)}; {robust(h2_verdict(n_ok_full) == h2_verdict(n_ok))})")
    L.append("H4 / C-pseudo: NOT decided here (registered on r_P at receiver iteration 4, real queries). Held-out r_P above is report-only.")
    L.append(f"\n# wall {time.time() - t_start:.0f} s")
    txt = "\n".join(L)
    print("\n".join(L[1:]))

    os.makedirs(os.path.dirname(out), exist_ok=True)
    arrs = {q: np.stack(v) for q, v in keep.items()}
    arrs.update({f"summary|{f}": np.array(col(f)) for f in rows[0]})
    arrs.update({f"check|toy_{q}": v for q, v in toy.items()})
    arrs.update({f"check|{q}": v for q, v in chk.items()})
    arrs.update({"meta|ks": np.array(ks), "meta|nu": nu_grid[ks], "meta|sigma": sig_grid[ks], "meta|phis": phis,
                 "meta|n_calib": a.n_calib, "meta|n_phase": a.n_phase, "meta|header": np.array(hdr),
                 "meta|ckpt": np.array(os.path.abspath(a.ckpt)), "meta|ckpt_identity": np.array(json.dumps(cid)),
                 "meta|gmm": np.array(json.dumps(dict(tag=a.gmm_tag, fits=A.D2_FITS, ntrain=a.gmm_ntrain, bstar=bstar,
                                                      family=fam, K=int(KK)))),
                 "meta|smoke": a.smoke, "meta|registered": registered, "meta|device": np.array(f"{dev} {gpu}")})
    np.savez_compressed(out + ".npz", **arrs)
    with open(out + ".txt", "w") as f:
        f.write(txt + "\n")
    print(f"# saved -> {out}.npz / .txt")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--ckpt", default=REGISTERED["ckpt"])
    p.add_argument("--gmm-tag", default=REGISTERED["gmm_tag"], help="runner tag of the GMM fits dir (b* of §0)")
    p.add_argument("--gmm-ntrain", type=int, default=REGISTERED["gmm_ntrain"])
    p.add_argument("--device", default="cuda")
    p.add_argument("--n-calib", type=int, default=REGISTERED["n_calib"], help="§0: n_eval for §2.2 / §2.4")
    p.add_argument("--n-phase", type=int, default=REGISTERED["n_phase"], help="§0: n for §2.3")
    p.add_argument("--ks", type=int, nargs="+", default=None, help="grid points (default all 20)")
    p.add_argument("--chunk", type=int, default=128, help="samples per vmap(jacrev) call (GPU memory knob)")
    p.add_argument("--gmm-chunk", type=int, default=256)
    p.add_argument("--n-check", type=int, default=4, help="samples per point for the GMM / project_psd consistency checks")
    p.add_argument("--threads", type=int, default=1)
    p.add_argument("--smoke", action="store_true", help="n_calib = n_phase = 32, ks = 0 10 19, *_smoke.* outputs")
    p.add_argument("--out", default=None, help="output stem (default results/review_next/p1_heldout[_smoke])")
    p.add_argument("--overwrite", action="store_true")
    main(p.parse_args())
