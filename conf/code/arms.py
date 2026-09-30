"""conf/code/arms.py -- arm registry (conf/06_SPEC_runner.md §1).

Every RouteA-based arm is built from an EXPLICIT, fully-populated config dict: no reliance on the
constructor defaults of t2_route_a.RouteA, because those defaults are pinned by the regression tests
t0/t6 and differ from the D-15 configuration (conf/03_SPEC_ourmodel.md §2, test C5).
The config of every arm is dumped into the result header (tests C5, M4).
"""
import os
import numpy as np

import common as C
from common import (BETA, LAM_MIN, N_TRAIN, DEMO, GaussianPrior, GMMPriorB, RouteA, RouteAClip)
from bigamp import R3BiGAMP
from scvamp import R4SCVAMP

# ----------------------------------------------------------------------------- the D-15 / v1 loop, spelled out
# conf/03_SPEC_ourmodel.md §1.1.  Fields marked (H) are the only ones an arm may change: they select Module H.
LOOP = dict(
    lh_form="A",            # likelihood site form A (marginalisation / LMMSE)
    alphaD="mean",          # scalar Onsager alpha^D
    feedback="posterior",   # D-15: channel estimator consumes the decoder A-POSTERIORI moments
    loo=True,               # D-15: detector uses the leave-one-out cavity
    beta=BETA,              # 0.7, v1
    beta_fb=None,           # D-15 / Q-24 closed: NO damping on the posterior feedback path
    n_inner=1,              # v1
    eps=1e-6,
    nu_max=1e4,
    p_min=1e-8,
    init_colored=0,
    nu_sw=None,
    dec_ext="moment",
    tauD_min=1e-8,
)
MODULE_H = {                                            # (H) -- the ONLY difference between R2-ours-G and M-ours-*
    "gaussian":  dict(mode="colored", scal="site",   hsite="scalar", lam_min=0.0,     exact_prior=False),
    "gmm_site":  dict(mode="colored", scal="site",   hsite="scalar", lam_min=LAM_MIN, exact_prior=True),
    "score":     dict(mode="scalar",  scal="belief", hsite="matrix", lam_min=LAM_MIN, exact_prior=False),
}


def route_a(Nr, Nt, T, Tp, sigma2, prior, code, Xp, moduleH, clip=None, **over):
    cfg = dict(LOOP, **MODULE_H[moduleH], Xp=Xp)
    cfg.update(over)
    cls = RouteA if clip is None else RouteAClip
    kw = dict(cfg) if clip is None else dict(cfg, clip=clip)
    rx = cls(Nr, Nt, T, Tp, sigma2, prior, code, **kw)
    # The site clip rule lives on RouteAClip for the score arms and on the GMM prior object (.view("eta"))
    # for the mixture-EP arms; record the EFFECTIVE rule either way (test M4).
    rx.cfg_dump = dict(cfg, module_H=moduleH, class_=cls.__name__,
                       clip=(clip if clip is not None else getattr(prior, "clip", "n/a")))
    return rx


# ----------------------------------------------------------------------------- GMM fits
D1_FITS = os.path.join(DEMO, "exp_0925_fits")            # reused verbatim (see DECISIONS)
D2_FITS = os.path.join(C.CONF, "results", "gmm_fits_D2")
D1_KS, D2_KS = (16, 32, 64), (16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192)   # 256/512: b* kept hitting the grid edge
# 4096/8192 added 2026-09-23 (NEXT_EXPERIMENTS_B32e4 §1, before any K=4096 fit exists): the §6l extension rule at
# N'=3.2e5.  load_fits() only loads files that exist, so every existing fits directory selects exactly as before.
# (DECISIONS); 1024/2048 added 2026-09-22 15:30 under 10_SPEC_stageC §6l -- at N=4e4 kron K=1024 beat K=512 on
# validation log-likelihood, so the grid must extend until b* is interior (01_RULES:76).  load_fits() only loads
# files that exist, so a directory without a K=1024 fit selects exactly as before; `runner.py fit` will now
# enumerate the two new K for every family/Nr.


def fit_path(testbed, prior, Nr, fam, K, ntrain=N_TRAIN):
    if testbed == "D1":
        return os.path.join(D1_FITS, f"fit_{prior}_Nr{Nr}_{fam}K{K}_n{ntrain}.npz")
    return os.path.join(D2_FITS, f"fit_{prior}_Nr{Nr}_{fam}K{K}_n{ntrain}.npz")


def load_fits(testbed, prior, Nr, ntrain=N_TRAIN):
    Ks = D1_KS if testbed == "D1" else D2_KS
    out = {}
    for fam in ("full", "kron"):
        for K in Ks:
            p = fit_path(testbed, prior, Nr, fam, K, ntrain)
            if os.path.exists(p):
                out[(fam, K)] = np.load(p)
    if not out:
        raise FileNotFoundError(f"no GMM fits for {testbed}/{prior}/Nr={Nr} -- run `runner.py fit --testbed {testbed}`")
    return out


def training_set(testbed, prior, Nr, Nt, ntrain=N_TRAIN):
    """The ONE channel dataset that both the GMM fit and the diffusion training use (04_SPEC §2, test D2t)."""
    gen = C.make_gen(testbed, prior, Nr, Nt)
    return gen.sample_vecs(C.train_rng(testbed, prior, Nr, 7), ntrain)


def gmm_selection(testbed, prior, Nr, ntrain=N_TRAIN):
    """b* = the Hgmm arm with the best VALIDATION log-likelihood.  BLER is never consulted (01_RULES §5)."""
    fits = load_fits(testbed, prior, Nr, ntrain)
    Ks = sorted({K for fam, K in fits if fam == "full"})
    llv = {f"gmm{K}": float(fits[("full", K)]["ll_val"]) for K in Ks}
    kron = [(K, float(fits[("kron", K)]["ll_val"])) for fam, K in fits if fam == "kron"]
    kron_K = max(kron, key=lambda t: t[1])[0] if kron else None
    if kron_K is not None:
        llv["kron"] = float(fits[("kron", kron_K)]["ll_val"])
    return fits, llv, max(llv, key=llv.get), kron_K


# ----------------------------------------------------------------------------- arm construction
def build_baseline_arms(testbed, prior, Nr, Nt, T, Tp, sigma2, code, Xp, ntrain=N_TRAIN, true_prior=None):
    """R0..R6.  All share the same pilot matrix, the same 16 outer iterations and (inside a cell) the same
    channel/noise realisations.  R6-exactEP exists only where the true prior has an exact EP site (D1)."""
    fits = load_fits(testbed, prior, Nr, ntrain)
    Chat = fits[("full", 32)]["Chat"]                       # sample covariance of the SAME training set
    Cs = GaussianPrior(Nr, Nt, Chat)
    a = (Nr, Nt, T, Tp, sigma2)
    arms, cfgs = {}, {}

    arms["R0-pilot"] = route_a(*a, Cs, code, Xp, "gaussian", mode="pilot_only")
    arms["R1-turbo"] = route_a(*a, Cs, code, Xp, "gaussian", loo=False)
    arms["R2-ours-G"] = route_a(*a, Cs, code, Xp, "gaussian")
    arms["R3-bigamp"] = R3BiGAMP(*a, code, Xp, beta=BETA, t_in=C.T_IN)
    arms["R4-scvamp"] = R4SCVAMP(*a, Cs, code, Xp, mode="onsager")
    arms["R4-llr"] = R4SCVAMP(*a, Cs, code, Xp, mode="llr")
    arms["R5-genie"] = route_a(*a, Cs, code, Xp, "gaussian", mode="genie")
    if testbed == "D1" and true_prior is not None:
        arms["R6-exactEP"] = route_a(*a, true_prior.view("eta"), code, Xp, "gmm_site")

    for k, v in arms.items():
        cfgs[k] = dict(v.cfg_dump)                       # every arm carries a complete, explicit dump (test C5)
        cfgs[k]["arm"] = k
    return arms, cfgs, Cs, fits


P3_BETA = 0.5                       # NEXT_EXPERIMENTS_P3 §2.2: the one value of beta / beta_fb the P3 variants use

# ----------------------------------------------------------------------------- our model (conf/03_SPEC_ourmodel.md)
# M-ours-* differs from R2-ours-G in MODULE H AND NOTHING ELSE.  Test M2 is the proof of that sentence and is
# the single most important test in this experiment (03_SPEC §4).
def module_h_priors(testbed, prior, Nr, Nt, ntrain=N_TRAIN, true_prior=None):
    fits, llv, bstar, kron_K = gmm_selection(testbed, prior, Nr, ntrain)
    Ks = sorted({K for fam, K in fits if fam == "full"})
    gm = {K: GMMPriorB(Nr, Nt, fits[("full", K)]["covs"], fits[("full", K)]["pi"]) for K in Ks}
    out = {f"gmm{K}": gm[K] for K in Ks}
    if kron_K is not None:
        out["kron"] = GMMPriorB(Nr, Nt, fits[("kron", kron_K)]["covs"], fits[("kron", kron_K)]["pi"])
    return out, fits, llv, bstar, kron_K


class PilotSitePrior:
    """Learned prior used ONCE, on the pilots only -- the pilot-only (no data-aided re-estimation) setting of score-based
    channel estimation (Arvinte & Tamir, IEEE TWC 2023), rebuilt inside this receiver with the SAME V1 weights, data and
    trials (review_next 2026-09-26, NEXT_EXPERIMENTS_PILOT16e4).  It is handed to RouteA's mode='pilot_only' with
    exact_prior=True, which computes the pilot-only likelihood site (G, b), calls ep_site(G, b, lam_min) ONCE, freezes the
    channel belief (P = Lam + G, h = P^-1 (eta + b)) and then iterates detection <-> decoding with that belief.
    ep_site reproduces V1's iteration-0 Module H VERBATIM (MODULE_H['score']: scal='belief', n_inner=1, starting from
    RouteA.run's nuE = cbar, hE = 0; then RouteAClip._matrix_site with clip='eta'), so the arm's iteration-1 output is
    bit-identical to M-ours-dscore-C-V1's iteration-1 output (at iteration 0 the data columns carry xbar = 0 and add
    nothing to (G, b)) -- checked by selftest_pilot.py.  Every other attribute (cbar, eh2_prior, C, ...) is the wrapped
    ScorePrior's."""

    def __init__(self, sp, eps):
        self.sp, self.eps = sp, eps

    def __getattr__(self, k):
        return getattr(self.sp, k)

    def ep_site(self, G, b, lam_min):
        N = G.shape[0]; I = np.eye(N)
        nuE = self.sp.cbar; hE = np.zeros(N, complex)                                    # RouteA.run initial state
        SigL = np.linalg.inv(I / nuE + G); hL = SigL @ (hE / nuE + b)                     # scal='belief', n_inner=1
        aL = float(np.clip(np.trace(SigL).real / N / nuE, self.eps, 1 - self.eps))
        nu_q = aL / (1 - aL) * nuE; q = (hL - aL * hE) / (1 - aL)
        self.sp.denoise(q, nu_q)                                                          # V1 calls it here too (query stats)
        hH, J = self.sp.denoise_full(q, nu_q)                                             # RouteAClip._matrix_site, clip='eta'
        SigH = nu_q * J; SigH = 0.5 * (SigH + SigH.conj().T)
        SigHinv = np.linalg.inv(SigH)
        Lam = SigHinv - I / nu_q; Lam = 0.5 * (Lam + Lam.conj().T)
        w, V = np.linalg.eigh(Lam); eta = SigHinv @ hH - q / nu_q
        if w.min() < lam_min:
            Lam = (V * np.maximum(w, lam_min)) @ V.conj().T
        return Lam, eta


CURRENT_TRIAL = None                # runner.run_task sets the trial index before every trial (ALDSitePrior lookup)


class ALDSitePrior:
    """Arvinte & Tamir (IEEE TWC 2023) pilot-only estimate by annealed Langevin posterior sampling with the V1 network,
    PRECOMPUTED by code/ald.py (GPU; NEXT_EXPERIMENTS_ALD16e4) and handed to RouteA's mode='pilot_only' (exact_prior=True)
    as a frozen channel belief N(hhat, v I): ep_site returns Lam = I/v - G, eta = hhat/v - b, so P = Lam + G = I/v and
    hpost = hhat.  v = V_PLUGIN (the authors' plug-in use of the estimate) or the dev-set MSE per entry (error-aware
    variant).  The trial is found by CURRENT_TRIAL and CHECKED: the stored pilot site b must equal the receiver's b."""
    V_PLUGIN = 1e-8

    def __init__(self, sp, table, k, v):
        self.sp, self.hhat, self.b, self.v = sp, table["hhat"][k], table["b"][k], float(v)
        self.skip = int(table["skip"])                  # the table's first trial (0 = test set)

    def __getattr__(self, k):
        return getattr(self.sp, k)

    def ep_site(self, G, b, lam_min):
        tr = CURRENT_TRIAL - self.skip
        ref = self.b[tr]
        if not np.allclose(b, ref, rtol=1e-9, atol=1e-12 * np.max(np.abs(ref))):
            raise RuntimeError(f"ALDSitePrior: pilot site of trial {tr} differs from the precomputed one")
        N = G.shape[0]
        return np.eye(N) / self.v - G, self.hhat[tr] / self.v - b


def dft_dict(Nr, Nt, rho):
    """Oversampled 2-D DFT (virtual-channel) dictionary for h = vec(H), column-major: H = F_r X F_t^T <=> h = (F_t kron F_r) vec(X);
    F_n[k, g] = exp(2 pi j k g / (rho n)) / sqrt(n), g = 0..rho n - 1 (half-wavelength ULA spatial frequencies on a rho-times grid)."""
    F = lambda n: np.exp(2j * np.pi * np.arange(n)[:, None] * np.arange(int(rho * n))[None, :] / (rho * n)) / np.sqrt(n)
    return np.kron(F(Nt), F(Nr))


class SparsePrior:
    """Sparse Bayesian learning (SBL; Tipping 2001, Wipf & Rao 2004) as the channel prior of the SAME EP receiver as b* (MODULE_H
    'gmm_site', exact_prior): h = A x, x_i ~ CN(0, gamma_i), A = dft_dict(Nr, Nt, rho).  At every call the hyper-parameters gamma
    are re-learned by n_em EM steps on the CURRENT Gaussian likelihood exp(-h^H G h + 2 Re b^H h) (pilots only in the pilot-only
    mode; pilots + data-aided columns in the loop), started from the flat level cbar N / M, then the prior site of the Gaussian
    prior CN(0, A diag(gamma) A^H + eps I) is returned: Lam = C^-1, eta = 0 (exact for a Gaussian prior; PSD, no clipping).
    Needs no training data (a model-based baseline, NEXT_EXPERIMENTS_SPARSE16e4).  Every other attribute (C, Cinv, cbar,
    eh2_prior, ...) is the wrapped sample-covariance GaussianPrior's, so the receiver's initial state equals R2's / b*'s."""

    def __init__(self, base, Nr, Nt, rho, n_em, eps=1e-6):
        self.base, self.A, self.n_em, self.eps = base, dft_dict(Nr, Nt, rho), int(n_em), float(eps)
        self.clip = "n/a"

    def __getattr__(self, k):
        return getattr(self.base, k)

    def gamma(self, G, b):
        """EM on gamma in the N x N (Woodbury) form: with B = A Gamma, K = (I + G A Gamma A^H)^-1,
        mu_x = Gamma A^H K b,  diag Sigma_x = gamma - gamma^2 * diag(A^H K G A)  (= (Gamma^-1 + A^H G A)^-1, never forming M x M)."""
        A = self.A; M = A.shape[1]; N = G.shape[0]; I = np.eye(N)
        g = np.full(M, self.base.cbar * self.base.N / M)
        for _ in range(self.n_em):
            B = A * g
            K = np.linalg.inv(I + G @ (B @ A.conj().T))
            mx = g * (A.conj().T @ (K @ b))
            d = np.real(np.einsum("ij,ij->j", A.conj(), K @ (G @ A)))
            g = np.maximum(np.abs(mx) ** 2 + g - g ** 2 * d, 1e-12)
        return g

    def ep_site(self, G, b, lam_min):
        N = G.shape[0]; g = self.gamma(G, b)
        Cx = (self.A * g) @ self.A.conj().T + self.eps * np.eye(N)
        Ci = np.linalg.inv(0.5 * (Cx + Cx.conj().T))
        return 0.5 * (Ci + Ci.conj().T), np.zeros(N, complex)


class OMPSitePrior:
    """Orthogonal matching pursuit (Pati et al. 1993; Tropp & Gilbert 2007) channel estimate from the pilots on dft_dict(Nr, Nt, rho),
    handed to RouteA's mode='pilot_only' (exact_prior) as a frozen belief N(hhat, v I) exactly like ALDSitePrior (plug-in v).
    Greedy on the Gaussian likelihood (G, b): pick the atom maximising |a_i^H (b - G h)|^2 / (a_i^H G a_i), re-solve the
    least-squares coefficients on the support (A_S^H G A_S) x_S = A_S^H b, stop after L atoms."""
    V_PLUGIN = 1e-8

    def __init__(self, base, Nr, Nt, rho, L):
        self.base, self.A, self.L = base, dft_dict(Nr, Nt, rho), int(L)
        self.clip = "n/a"

    def __getattr__(self, k):
        return getattr(self.base, k)

    def hhat(self, G, b):
        A = self.A; AGA = A.conj().T @ G @ A; Ab = A.conj().T @ b
        dg = np.maximum(np.real(np.diag(AGA)), 1e-30); S = []; h = np.zeros(G.shape[0], complex)
        for _ in range(self.L):
            c = np.abs(A.conj().T @ (b - G @ h)) ** 2 / dg
            c[S] = -1.0; S.append(int(np.argmax(c)))
            xs = np.linalg.solve(AGA[np.ix_(S, S)], Ab[S]); h = A[:, S] @ xs
        return h

    def ep_site(self, G, b, lam_min):
        N = G.shape[0]; h = self.hhat(G, b)
        return np.eye(N) / self.V_PLUGIN - G, h / self.V_PLUGIN - b


def build_our_arms(testbed, prior, Nr, Nt, T, Tp, sigma2, code, Xp, ntrain=N_TRAIN,
                   true_prior=None, score_prior=None, with_G=False, score_prior_v1=None,
                   score_prior_c=None, bstar_scalar=False, mean_arms=False,
                   score_prior_v1_floor=None, p3_arms=False, pilot_arms=False, ald=None, sparse=None):
    """M-ours-gmm32 / M-ours-bstar / M-ours-score (D1 only) / M-ours-dscore / M-ours-G (test M2 only).

    score_prior_v1: a SECOND score.ScorePrior built with psd_project=True (Stage C V1, spec 10 §3b / (F1)).
    It becomes the separate arm M-ours-dscore-C-V1; every other arm, M-ours-dscore included, is untouched.

    Stage C, OPT-IN (spec 10 §3b / §3c).  Every argument below defaults to "not built", so a caller that
    does not ask for Stage C gets exactly the pre-registered arm set, bit for bit:
      score_prior_c : the Stage C checkpoint (--stagec-ckpt) -> M-ours-dscore-C-V0 (D-14 MATRIX site, the
                      pre-registered score wiring) and M-ours-dscore-C-V4 (D-14 REPLACED by the D-13
                      belief scalarisation).  ONE ScorePrior drives both, exactly as code/diag_ep_site.py
                      drives its dscore|scorew and dscore|belsc cells from one object.  Gate status is not
                      enforced (the runner records it in meta|stagec_gate): D1 sx_N160000_D1.pt passes; a D2
                      checkpoint has no gate row and is qualified through its D1 sibling, which passes only at
                      N_train=1.6e5.  [record correction 2026-09-23, review_next G-1.2: previously 'the
                      gate-passing Stage C checkpoint'.]
      bstar_scalar  : M-ours-bstar-scalar, the b* GMM through V4's wiring.  §3c makes this arm MANDATORY
                      in the same run as V4: if scalarisation also helps the GMM, the gain belongs to the
                      site, not to the learned prior.

    review_next A2, OPT-IN (NEXT_EXPERIMENTS v3 §3.2; development set only, report-only):
      mean_arms     : the clip='mean' symmetric ablation.  M-ours-dscore-C-V1-mean = V1 with RouteAClip
                      clip='mean' (needs score_prior_v1); gmmB-scorew-eta / -mean = b* in V1's wiring, the
                      adapter control; M-ours-bstar-mean = b*.view('mean') on the gmm_site path (a different
                      mean is preserved there -> report-only row, audit M3).  Existing arms are untouched.

    review_next P3, OPT-IN (NEXT_EXPERIMENTS_P3 §2.2; judging set skip >= 3200):
      p3_arms       : the loop-constant ablation.  V1-b05 / bstar-b05 = V1 / M-ours-bstar with beta = P3_BETA (damping
                      of the extrinsic pair (rD, tauD); v1 value 0.7), V1-fb05 / bstar-fb05 = the same with beta_fb =
                      P3_BETA (damping of the posterior feedback (xbar, v); D-15 value None).  Everything else is the
                      base arm's route_a() call verbatim; each bstar variant gets its OWN .view("eta") (own clip
                      counters, and a per-arm object for instance hooks).  Existing arms are untouched.

    review_next pilot-only, OPT-IN (NEXT_EXPERIMENTS_PILOT16e4, 2026-09-26):
      pilot_arms    : V1-pilot = the V1 weights used once on the pilots (PilotSitePrior) with the channel belief frozen,
                      then detection <-> decoding only (RouteA mode='pilot_only'); bstar-pilot = the same for the b* GMM
                      (its own .view("eta"); exact mixture EP site on the pilots only).  Existing arms are untouched."""
    hp, fits, llv, bstar, kron_K = module_h_priors(testbed, prior, Nr, Nt, ntrain)
    Cs = GaussianPrior(Nr, Nt, fits[("full", 32)]["Chat"])
    a = (Nr, Nt, T, Tp, sigma2)
    arms, cfgs = {}, {}

    arms["M-ours-gmm32"] = route_a(*a, hp["gmm32"].view("eta"), code, Xp, "gmm_site")
    arms["M-ours-bstar"] = route_a(*a, hp[bstar].view("eta"), code, Xp, "gmm_site")
    if testbed == "D1" and true_prior is not None:
        arms["M-ours-score"] = route_a(*a, true_prior, code, Xp, "score", clip="eta")
    if score_prior is not None:
        arms["M-ours-dscore"] = route_a(*a, score_prior, code, Xp, "score", clip="eta")
    if score_prior_v1 is not None:
        arms["M-ours-dscore-C-V1"] = route_a(*a, score_prior_v1, code, Xp, "score", clip="eta")
    # --- Stage C.  The three route_a() calls below are LIFTED VERBATIM from code/diag_ep_site.py, so the
    # production arms and the diagnostic cells that measured the mechanism are provably one configuration:
    #   diag  dscore|scorew = route_a(..., sp, "score", clip="eta")                   -> V0
    #   diag  dscore|belsc  = route_a(..., sp, "score", clip="eta", hsite="scalar")   -> V4
    #   diag  gmmB|belsc    = the same on hp[bstar] (raw prior, NOT .view("eta"))     -> M-ours-bstar-scalar
    if score_prior_c is not None:
        arms["M-ours-dscore-C-V0"] = route_a(*a, score_prior_c, code, Xp, "score", clip="eta")
        arms["M-ours-dscore-C-V4"] = route_a(*a, score_prior_c, code, Xp, "score", clip="eta", hsite="scalar")
        # V4b (§3c: "동일하되 scal=site. 부수 보고용").  Registered with V4 and then not wired until the
        # 2026-09-21 18:20 audit noted it had been silently dropped.  §3b's standard for this document is
        # "넷을 다 돌린 사실과 그 결과를 전부 보고한다", so it is carried, not quietly left out.
        #   diag dscore|sitesc = route_a(..., sp, "score", clip="eta", hsite="scalar", scal="site")
        arms["M-ours-dscore-C-V4b"] = route_a(*a, score_prior_c, code, Xp, "score", clip="eta",
                                              hsite="scalar", scal="site")
    if bstar_scalar:
        arms["M-ours-bstar-scalar"] = route_a(*a, hp[bstar], code, Xp, "score", clip="eta", hsite="scalar")
    # --- review_next A2 (§3.2).  The gmmB-scorew pair is LIFTED VERBATIM from code/diag_ep_site.py:
    #   diag  gmmB|scorew = route_a(..., hp[bstar] (raw prior, NOT .view()), "score", clip="eta")
    # MODULE_H["score"] has exact_prior=False, and RouteA keeps exact_prior only when it is asked for AND the
    # prior has ep_site -- so the raw GMMPriorB goes through the scalar belief + RouteAClip._matrix_site path,
    # exactly like V1, never through ep_site.  The assert makes that a build-time fact.
    if mean_arms:
        if score_prior_v1 is not None:
            arms["M-ours-dscore-C-V1-mean"] = route_a(*a, score_prior_v1, code, Xp, "score", clip="mean")
        for cl in ("eta", "mean"):
            arms[f"gmmB-scorew-{cl}"] = route_a(*a, hp[bstar], code, Xp, "score", clip=cl)
            assert not arms[f"gmmB-scorew-{cl}"].exact_prior, "gmmB-scorew must not take the ep_site path"
        arms["M-ours-bstar-mean"] = route_a(*a, hp[bstar].view("mean"), code, Xp, "gmm_site")
        if score_prior_v1_floor is not None:   # §2.6 C-calib report-only row: V1 with eigenvalue floor 1e-2
            arms["M-ours-dscore-C-V1-floor1e-2"] = route_a(*a, score_prior_v1_floor, code, Xp, "score", clip="eta")
    if p3_arms:                     # review_next P3 §2.2 -- same call as the base arm, ONE loop constant changed
        for sfx, over in (("b05", dict(beta=P3_BETA)), ("fb05", dict(beta_fb=P3_BETA))):
            if score_prior_v1 is not None:
                arms[f"V1-{sfx}"] = route_a(*a, score_prior_v1, code, Xp, "score", clip="eta", **over)
            arms[f"bstar-{sfx}"] = route_a(*a, hp[bstar].view("eta"), code, Xp, "gmm_site", **over)
    if pilot_arms:                  # pilot-only estimate, frozen channel belief (no data-aided re-estimation)
        if score_prior_v1 is not None:
            arms["V1-pilot"] = route_a(*a, PilotSitePrior(score_prior_v1, LOOP["eps"]), code, Xp, "score", clip="eta",
                                       mode="pilot_only", exact_prior=True)
            assert arms["V1-pilot"].exact_prior and arms["V1-pilot"].mode == "pilot_only"
        arms["bstar-pilot"] = route_a(*a, hp[bstar].view("eta"), code, Xp, "gmm_site", mode="pilot_only")
        assert arms["bstar-pilot"].exact_prior and arms["bstar-pilot"].mode == "pilot_only"
    if ald is not None and score_prior_v1 is not None:     # (table, SNR index k): NEXT_EXPERIMENTS_ALD16e4
        tab, k = ald
        for name, v in (("ALD-pilot", ALDSitePrior.V_PLUGIN), ("ALDv-pilot", tab["v"][k])):
            arms[name] = route_a(*a, ALDSitePrior(score_prior_v1, tab, k, v), code, Xp, "score", clip="eta",
                                 mode="pilot_only", exact_prior=True)
            assert arms[name].exact_prior and arms[name].mode == "pilot_only"
    if sparse is not None:          # NEXT_EXPERIMENTS_SPARSE16e4: model-based sparse baselines, same EP receiver as b* ('gmm_site')
        rs, n_em, ro, L = sparse["rho_sbl"], sparse["n_em"], sparse["rho_omp"], sparse["L"]
        arms["SBL-loop"] = route_a(*a, SparsePrior(Cs, Nr, Nt, rs, n_em), code, Xp, "gmm_site")
        arms["SBL-pilot"] = route_a(*a, SparsePrior(Cs, Nr, Nt, rs, n_em), code, Xp, "gmm_site", mode="pilot_only")
        arms["OMP-pilot"] = route_a(*a, OMPSitePrior(Cs, Nr, Nt, ro, L), code, Xp, "gmm_site", mode="pilot_only")
        for k in ("SBL-loop", "SBL-pilot", "OMP-pilot"):
            assert arms[k].exact_prior
    if with_G:
        arms["M-ours-G"] = route_a(*a, Cs, code, Xp, "gaussian")

    meta = dict(bstar=bstar, kron_K=(kron_K if kron_K is not None else -1),
                **{f"ll_val|{k}": v for k, v in llv.items()})
    for k, v in arms.items():
        cfgs[k] = dict(v.cfg_dump)
        cfgs[k]["arm"] = k
        cfgs[k]["moduleH_object"] = type(v.prior).__name__ + (f" K={v.prior.K}" if hasattr(v.prior, "K") else "")
    return arms, cfgs, meta, hp, fits


# conf/03_SPEC_ourmodel.md §1.1, verbatim -- test M4 compares the dump against this field by field.
SPEC_TABLE_11 = {
    "feedback": "posterior",     # channel estimator consumes the decoder A-POSTERIORI (x_bar, v)   [D-15]
    "loo": True,                 # detector output = extrinsic + leave-one-out                      [D-15]
    "beta_fb": None,             # NO damping on the posterior feedback path                        [D-15, Q-24 closed]
    "beta": 0.7,                 # damping                                                          [v1]
    "n_inner": 1,                # inner L_H <-> H repetitions                                      [v1]
    "iters": 16,                 # outer iterations, all arms
    "clip": "eta",               # site clip rule: existing default, unchanged                      [Q-34 open -> do not touch]
}
