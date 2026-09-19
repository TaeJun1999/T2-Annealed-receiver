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
    rx.cfg_dump = dict(cfg, module_H=moduleH, clip=clip or "n/a", class_=cls.__name__)
    return rx


# ----------------------------------------------------------------------------- GMM fits
D1_FITS = os.path.join(DEMO, "exp_0925_fits")            # reused verbatim (see DECISIONS)
D2_FITS = os.path.join(C.CONF, "results", "gmm_fits_D2")
D1_KS, D2_KS = (16, 32, 64), (16, 32, 64, 128)


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
