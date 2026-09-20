"""conf/code/param_edm.py -- the EDM parameterisation (Karras et al. 2022, "Elucidating the Design Space
of Diffusion-Based Generative Models") as PURE FUNCTIONS, ready to be wired into score.py::ScoreModel as
a fourth `param` value "edm" alongside 've' / 'vp' / 'rf'.

WHY THIS RUNG EXISTS
  The binding gate of this project is GC, the relative score error  E||s_hat - s*|| / E||s*||  over the
  FROZEN measured sigma_t grid (04_SPEC_diffusion.md §5), and GC is worst at SMALL sigma.  That is exactly
  the conditioning problem EDM preconditioning is designed for: at small sigma the eps-parameterisations
  ask the network to supply a quantity that is then divided by sigma (s = -eps_hat/sigma), so a fixed
  relative error in eps_hat becomes a 1/sigma-amplified error in the score.  EDM instead makes the network
  predict a quantity whose target has UNIT variance at every sigma, and folds the sigma-dependence into
  closed-form coefficients.  Nothing else about the ladder changes.

WHAT IS AND IS NOT IN THIS FILE
  There is NO architecture here.  EDM is a parameterisation + a loss weighting, so this file only ever
  receives a `raw(x_scaled, c_noise) -> F_theta` callable -- in production that is the bound method
  score.py::ScoreModel.raw, which already carries the backbone (_MLP / _Conv / _UNet), the zero-initialised
  output projection and, for the angle domain, the orthogonal DFT wrapper.  Consequences:
    * The COLUMN-MAJOR layout  h[i + Nr*j] = H[i,j]  is inherited from the backbone (score.py::_Conv.forward
      is the reference).  This file never reshapes x; it only scales it along the last axis, so whatever
      leading dims `raw` supports, these functions support unchanged -- including the bare (2N,) shape that
      torch.func.vmap hands the Jacobian code in score.py::jac_batch.
    * The required final-layer zero-init is the BACKBONE's (score.py zero-inits every `out` layer).  Its
      EDM consequence is checked in the self-test below: with F_theta == 0 the denoiser collapses to
      D = c_skip * x exactly, which as sigma -> 0 is the identity denoiser D = x.  Same guarantee as ve/vp/rf,
      reached through c_skip rather than through "predict eps = 0".

THE EQUATIONS (Karras et al. 2022, Table 1, "ours" column -- transcribed, not improvised)
  D(x; sigma) = c_skip(sigma) * x + c_out(sigma) * F_theta(c_in(sigma) * x, c_noise(sigma))
  c_skip  = sd^2 / (sigma^2 + sd^2)          sd := sigma_data
  c_out   = sigma * sd / sqrt(sigma^2 + sd^2)
  c_in    = 1 / sqrt(sigma^2 + sd^2)
  c_noise = log(sigma) / 4
  loss    = lambda(sigma) * || D(x0 + sigma*eps; sigma) - x0 ||^2,
            lambda(sigma) = (sigma^2 + sd^2) / (sigma*sd)^2 = 1 / c_out^2.
  score   = (D - x) / sigma^2                (Tweedie; the same identity ve/vp/rf use)

  LOSS EQUIVALENCE (this is why edm_loss never forms lambda).  Substituting D and using lambda = 1/c_out^2,
      lambda * ||D - x0||^2 = || F_theta(c_in*x, c_noise) - (x0 - c_skip*x)/c_out ||^2,
  and the target (x0 - c_skip*x)/c_out, with x = x0 + sigma*eps, simplifies EXACTLY to
      target = (sigma*x0 - sd^2*eps) / (sd * sqrt(sigma^2 + sd^2))                       [edm_target]
  which is finite and well conditioned at every sigma -- in particular target -> -eps as sigma -> 0 and
  target -> x0/sd as sigma -> inf, where the literal form 1/c_out^2 * ||...||^2 is 0/0 in float32.
  So the weighted loss IS a plain unweighted MSE on a unit-variance target; edm_loss computes that form,
  and the self-test checks the two agree numerically where the literal form is still computable.
  (Unit variance: with x0 having per-real-dimension variance sd^2 and eps ~ N(0,I),
   E[target^2] = (sigma^2*sd^2 + sd^4) / (sd^2*(sigma^2+sd^2)) = 1 for EVERY sigma.  That equality is the
   whole point of the EDM weighting, and it is asserted in the self-test.)

SIGMA_DATA
  sigma_data is the per-REAL-dimension standard deviation of the data.  The project normalisation is
  E||H||_F^2 = Nr*Nt (04_SPEC §2), i.e. unit variance per COMPLEX entry, i.e. 1/2 per real dimension, so
      sigma_data = 1/sqrt(2) = 0.70710678...                                       [SIGMA_DATA_DEFAULT]
  estimate_sigma_data(X) measures it from an actual training array so the caller can VERIFY rather than
  assume; score.py::training_split already asserts E||H||_F^2/(Nr*Nt) = 1 to 5%, and the two checks are
  the same statement seen from the two conventions.

WHY THE SIGMA DRAW DEFAULTS TO LOG-UNIFORM
  Every other rung of this ladder draws sigma LOG-UNIFORMLY over the frozen measured grid range
  [sigma.min(), sigma.max()] of conf/results/sigma_grid.txt (04_SPEC §2-3; score.py::train, the identical
  expression torch.exp(U*(log smax - log smin) + log smin)).  Keeping that draw bit-for-bit identical is
  what isolates EDM's ACTUAL contribution -- the preconditioning and the loss weighting -- instead of
  confounding it with a different emphasis over noise levels.  mode="lognormal" reproduces EDM's own
  P_mean=-1.2 / P_std=1.2 training distribution and exists so the orchestrator can run it as a SEPARATE
  attempt; it is CLAMPED to the frozen [lo, hi] because the grid range is pre-registered and may not widen
  (04_SPEC §3 "이후 바꾸지 않는다").

GATE GA
  D is the NATIVE denoiser head here and the score is defined as (D - x)/sigma^2, so x + sigma^2*score_real
  and denoise_real are the same expression and GA reads ~0 exactly as it does for ve/vp/rf.  That is
  expected and already documented in score.py::GA_NOTE; a PASS rests on GB/GC/GD.  Do not try to make GA bite.

WIRING (for the orchestrator; this file changes nothing on its own)
  score.py::ScoreModel.__init__ asserts param in ("ve","vp","rf") and make_model asserts
  param in ("ve","vp","rf","vae") -- both need "edm" added.  Then:
      score_real   -> param_edm.edm_score(self.raw, x, sigma, self.sigma_data)
      denoise_real -> param_edm.edm_denoise(self.raw, x, sigma, self.sigma_data)
      loss         -> param_edm.edm_loss(self.raw, x0, sigma, eps, self.sigma_data)
  sigma_data belongs in the checkpoint's hp so a reload cannot silently change the parameterisation.
"""
import math

import numpy as np
import torch

SIGMA_DATA_DEFAULT = 2 ** -0.5          # E||H||_F^2 = Nr*Nt  =>  1/2 per real dimension


def estimate_sigma_data(X):
    """Per-real-dimension standard deviation of the data, measured.

    Accepts the real packed form x = [Re(h), Im(h)] of shape (..., 2N) OR the complex h of shape (..., N)
    (score.py::training_split hands out the complex one, np_pack turns it into the real one), numpy or torch.
    Taken about ZERO, not about the sample mean: this prior is circularly symmetric and therefore zero-mean
    by construction, and the EDM coefficients are derived for a zero-mean x.  For the complex form the
    per-real-dimension variance is half the per-complex-entry variance."""
    A = X.detach().cpu().numpy() if torch.is_tensor(X) else np.asarray(X)
    if np.iscomplexobj(A):
        return float(np.sqrt(np.mean(np.abs(A) ** 2) / 2.0))
    return float(np.sqrt(np.mean(np.asarray(A, float) ** 2)))


def edm_coeffs(sigma, sigma_data=SIGMA_DATA_DEFAULT):
    """(c_skip, c_out, c_in, c_noise) for sigma of shape (...,).

    SHAPES -- the three MULTIPLICATIVE coefficients come back with shape (..., 1) so they broadcast against
    x of shape (..., 2N); c_noise comes back with shape (...) = sigma's own shape, because it goes into the
    `logsig` slot of raw(), and score.py::_TimeEmb.forward does the unsqueeze(-1) itself."""
    s = torch.as_tensor(sigma)
    sd = torch.as_tensor(sigma_data, dtype=s.dtype, device=s.device)
    v = s * s + sd * sd                                   # sigma^2 + sigma_data^2
    r = torch.sqrt(v)
    return (sd * sd / v).unsqueeze(-1), (s * sd / r).unsqueeze(-1), (1.0 / r).unsqueeze(-1), torch.log(s) / 4.0


def edm_denoise(raw, x, sigma, sigma_data=SIGMA_DATA_DEFAULT):
    """D(x; sigma) = c_skip*x + c_out*F_theta(c_in*x, c_noise).  `raw(x_scaled, c_noise) -> F_theta output`,
    i.e. exactly score.py::ScoreModel.raw.  Layout- and leading-dim-agnostic: x passes through untouched
    except for a scalar scale on the last axis."""
    c_skip, c_out, c_in, c_noise = edm_coeffs(sigma, sigma_data)
    return c_skip * x + c_out * raw(c_in * x, c_noise)


def edm_score(raw, x, sigma, sigma_data=SIGMA_DATA_DEFAULT):
    """grad_x log p_sigma(x) = (D(x;sigma) - x) / sigma^2  (Tweedie, exact)."""
    s = torch.as_tensor(sigma)
    return (edm_denoise(raw, x, sigma, sigma_data) - x) / (s * s).unsqueeze(-1)


def edm_target(x0, sigma, eps, sigma_data=SIGMA_DATA_DEFAULT):
    """The unit-variance regression target (x0 - c_skip*x)/c_out with x = x0 + sigma*eps, in the closed
    form that never divides by c_out.  See the LOSS EQUIVALENCE paragraph of the module docstring."""
    s = torch.as_tensor(sigma).unsqueeze(-1)
    sd = torch.as_tensor(sigma_data, dtype=s.dtype, device=s.device)
    return (s * x0 - sd * sd * eps) / (sd * torch.sqrt(s * s + sd * sd))


def edm_loss(raw, x0, sigma, eps, sigma_data=SIGMA_DATA_DEFAULT):
    """lambda(sigma) * ||D(x0 + sigma*eps; sigma) - x0||^2, computed as the algebraically identical and
    numerically stable ||F_theta(c_in*x, c_noise) - edm_target||^2.  Reduction is .mean() over batch AND
    dimensions, matching score.py::ScoreModel.loss, so validation losses stay on a comparable scale and the
    existing patience-20 early stopping needs no change."""
    c_skip, c_out, c_in, c_noise = edm_coeffs(sigma, sigma_data)
    x = x0 + torch.as_tensor(sigma).unsqueeze(-1) * eps
    return ((raw(c_in * x, c_noise) - edm_target(x0, sigma, eps, sigma_data)) ** 2).mean()


def edm_sigma_sample(n, lo, hi, generator=None, mode="loguniform", p_mean=-1.2, p_std=1.2):
    """Draw n noise levels in [lo, hi].  lo/hi are the FROZEN measured grid endpoints
    (score.py::_sigma_range -> sigma.load(testbed)); this function never widens them.

    mode="loguniform"  THE DEFAULT.  Bit-for-bit the draw score.py::train already makes for every other
                       rung, so switching a rung to EDM changes the parameterisation and nothing else.
    mode="lognormal"   EDM's own log-normal(p_mean, p_std) emphasis, CLAMPED into [lo, hi].  Clamping (not
                       rejection sampling) keeps the sample count deterministic; the price is a point mass
                       at each endpoint, which is visible and acceptable because the endpoints are where the
                       receiver actually queries least.  Run it as a separate attempt, never as the default.

    Returns a tensor on the generator's device (CPU by default), like the existing training loop, which
    does the .to(dev) itself."""
    dev = generator.device if generator is not None else None
    if mode == "loguniform":
        u = torch.rand(n, generator=generator, device=dev)
        return torch.exp(u * (math.log(hi) - math.log(lo)) + math.log(lo))
    if mode == "lognormal":
        z = torch.randn(n, generator=generator, device=dev)
        return torch.exp(p_mean + p_std * z).clamp(lo, hi)
    raise ValueError(f"unknown mode {mode!r} (expected 'loguniform' or 'lognormal')")


# ----------------------------------------------------------------------------- self-test
def _corr_channels(rng, n, Nr, Nt, rho_r=0.9, rho_t=0.6):
    """n correlated MIMO channels, packed real column-major exactly like score.py::np_pack(vec(H)).
    Exponential (unit-diagonal) correlation each side => E||H||_F^2 = tr(R_r)*tr(R_t)/... = Nr*Nt in
    POPULATION, so estimate_sigma_data has something real to measure rather than something pre-normalised.
    The spread eigen-spectrum is what makes the denoising task learnable at all: for an ISOTROPIC prior the
    EDM-optimal F_theta is identically 0 and no network can reduce the loss below 1."""
    half = lambda R: np.linalg.cholesky(R)
    ex = lambda m, r: r ** np.abs(np.subtract.outer(np.arange(m), np.arange(m)))
    Ar, At = half(ex(Nr, rho_r)), half(ex(Nt, rho_t))
    G = (rng.standard_normal((n, Nr, Nt)) + 1j * rng.standard_normal((n, Nr, Nt))) / np.sqrt(2)
    H = Ar @ G @ At.T
    h = H.transpose(0, 2, 1).reshape(n, Nr * Nt)          # column-major vec: h[i + Nr*j] = H[i,j]
    return np.concatenate([h.real, h.imag], -1)


def _mk_raw(Nr, Nt, arch="mlp", width=256, depth=4, emb=128, domain="pixel", seed=0):
    """The production `raw` slot: a real score.py ScoreModel, used only for its .raw (param is a placeholder
    -- score.py's assert does not know "edm" yet, which is one line the orchestrator adds)."""
    import score
    torch.manual_seed(seed)
    hp = dict(arch=arch, param="ve", domain=domain, width=width, depth=depth, emb=emb)
    m = score.make_model("L1", hp, Nr, Nt).eval()
    return m


def selftest(verbose=True):
    """Runs the whole battery.  Wrapper only: it restores the process-global autograd flag that the body
    toggles, so importing this module and calling selftest() inside a larger harness (score.py's __main__
    runs three self-tests back to back in one process) cannot leave grad disabled for whatever runs next."""
    g0 = torch.is_grad_enabled()
    try:
        return _selftest_impl(verbose)
    finally:
        torch.set_grad_enabled(g0)


def _selftest_impl(verbose=True):
    import score
    P = print if verbose else (lambda *a, **k: None)
    torch.set_grad_enabled(False)          # re-enabled for the trainability block only; restored by selftest()
    ok = lambda name, cond, extra="": (P(f"  [{'ok' if cond else 'FAIL'}] {name}{'  ' + extra if extra else ''}"),
                                       (_ for _ in ()).throw(AssertionError(name)) if not cond else None)[0]

    P("=" * 100)
    P("param_edm.py self-test")
    P(f"  torch {torch.__version__} | SIGMA_DATA_DEFAULT = {SIGMA_DATA_DEFAULT!r}")
    P("=" * 100)

    # --- sigma_data: default vs measured on a synthetic unit-variance-per-complex set -------------------
    P("\n[0] sigma_data")
    rng = np.random.default_rng(20260920)
    for (Nr, Nt) in ((8, 4), (4, 4)):
        Xr = _corr_channels(rng, 20000, Nr, Nt)
        hc = Xr[:, :Nr * Nt] + 1j * Xr[:, Nr * Nt:]
        est_r, est_c = estimate_sigma_data(Xr), estimate_sigma_data(hc)
        pw = float(np.mean(np.sum(np.abs(hc) ** 2, 1))) / (Nr * Nt)
        rel = abs(est_r - SIGMA_DATA_DEFAULT) / SIGMA_DATA_DEFAULT
        P(f"  {Nr}x{Nt}: E||H||_F^2/(Nr*Nt) = {pw:.6f} | estimate_sigma_data(real) = {est_r:.8f} | "
          f"(complex) = {est_c:.8f} | default = {SIGMA_DATA_DEFAULT:.8f} | rel.dev {100 * rel:.3f}%")
        ok(f"{Nr}x{Nt} measured sigma_data agrees with the default to a few percent", rel < 0.03)
        ok(f"{Nr}x{Nt} real and complex input give the same estimate", abs(est_r - est_c) < 1e-12)

    # --- coefficient limits ---------------------------------------------------------------------------
    P("\n[1] coefficient limits and the zero-init collapse")
    s = torch.tensor([1e-8, 1e-4, 1e-2, 0.0329357, 0.1, 0.7908, 1.0, 1e3, 1e8], dtype=torch.float64)
    cs, co, ci, cn = edm_coeffs(s)
    P("      sigma      c_skip       c_out        c_in       c_noise")
    for i in range(len(s)):
        P(f"   {float(s[i]):9.3e}  {float(cs[i,0]):10.7f}  {float(co[i,0]):10.3e}  {float(ci[i,0]):10.3e}  "
          f"{float(cn[i]):10.4f}")
    ok("sigma -> 0: c_skip -> 1 (identity denoiser)", abs(float(cs[0, 0]) - 1.0) < 1e-14)
    ok("sigma -> 0: c_out  -> 0", float(co[0, 0]) < 1e-7)
    ok("sigma -> inf: c_skip -> 0 (prior mean)", float(cs[-1, 0]) < 1e-14)
    ok("c_noise == log(sigma)/4", bool(torch.allclose(cn, torch.log(s) / 4, atol=0, rtol=0)))
    ok("c_out^2 == sigma^2*sd^2/(sigma^2+sd^2) (lambda = 1/c_out^2)",
       bool(torch.allclose(co[:, 0] ** 2, s ** 2 * 0.5 / (s ** 2 + 0.5), rtol=1e-12, atol=0)))

    # --- per-cell tests -------------------------------------------------------------------------------
    for (Nr, Nt) in ((8, 4), (4, 4)):
        dim = 2 * Nr * Nt
        P(f"\n{'=' * 100}\n(Nr, Nt) = ({Nr}, {Nt})   dim = 2*Nr*Nt = {dim}\n{'=' * 100}")

        # [2] shapes, arbitrary leading dims
        P("\n[2] output shape == input shape, arbitrary leading dims")
        mlp = _mk_raw(Nr, Nt, "mlp", 256, 4, 128)
        cnv = _mk_raw(Nr, Nt, "conv", 64, 4, 128)
        ang = _mk_raw(Nr, Nt, "mlp", 128, 2, 64, domain="angle")
        lin = lambda u, c: u * 0.0                                     # lead-agnostic reference raw
        for tag, raw, leads in (("mlp", mlp.raw, [(7,), (7, 3)]), ("conv", cnv.raw, [(7,)]),
                                ("mlp/angle", ang.raw, [(7,), (7, 3)]), ("pure-fn", lin, [(), (7,), (7, 3), (2, 3, 5)])):
            for lead in leads:
                x = torch.randn(*lead, dim)
                sg = torch.full(lead, 0.1) if lead else torch.tensor(0.1)
                d, sc = edm_denoise(raw, x, sg), edm_score(raw, x, sg)
                ok(f"{tag:10s} lead={str(lead):10s} denoise {tuple(d.shape)} score {tuple(sc.shape)}",
                   d.shape == x.shape and sc.shape == x.shape)
        P("   NOTE: lead=(B,K) is run on the MLP and on a pure-function raw.  score.py::_Conv/_UNet reshape to"
          "\n         (*lead, 2, Nt, Nr) and nn.Conv2d accepts only 3D/4D, so a conv backbone supports lead=()"
          "\n         and lead=(B,) -- exactly what jac_batch's vmap and the trainer need.  That is a property"
          "\n         of score.py, which this task forbids editing; param_edm itself is lead-agnostic, which is"
          "\n         what the pure-fn rows prove.")

        # [3] zero-init
        P("\n[3] zero-init: F_theta == 0 exactly  =>  D == c_skip * x  exactly")
        x = torch.randn(64, dim)
        sg = edm_sigma_sample(64, 3.293572e-02, 7.908e-01, torch.Generator().manual_seed(1))
        for tag, m in (("mlp", mlp), ("conv", cnv), ("mlp/angle", ang)):
            f0 = m.raw(x, torch.log(sg))
            cs_, co_, ci_, cn_ = edm_coeffs(sg)
            d = edm_denoise(m.raw, x, sg)
            ok(f"{tag:10s} F_theta == 0", bool(torch.equal(f0, torch.zeros_like(f0))))
            ok(f"{tag:10s} D == c_skip*x (bitwise)", bool(torch.equal(d, cs_ * x)))
        d_small = edm_denoise(mlp.raw, x, torch.full((64,), 1e-6))
        ok("at sigma = 1e-6 the zero-init denoiser is the identity to 1e-11",
           float((d_small - x).abs().max()) < 1e-11, f"max|D-x| = {float((d_small - x).abs().max()):.3e}")

        # [4] determinism
        P("\n[4] determinism in eval mode")
        for tag, m in (("mlp", mlp), ("conv", cnv), ("mlp/angle", ang)):
            m.eval()
            with torch.no_grad():
                a = edm_score(m.raw, x, sg)
                b = edm_score(m.raw, x, sg)
            ok(f"{tag:10s} two forwards bitwise identical", bool(torch.equal(a, b)))

        # [5] loss equivalence: weighted form == ||F - target||^2
        P("\n[5] loss equivalence  lambda*||D - x0||^2  ==  ||F_theta - target||^2")
        torch.manual_seed(7)
        trained = _mk_raw(Nr, Nt, "mlp", 64, 2, 32, seed=11)
        for p in trained.parameters():                                  # break the zero-init: F_theta != 0
            with torch.no_grad():
                p.add_(0.05 * torch.randn_like(p))
        trained = trained.double()
        x0 = torch.as_tensor(_corr_channels(rng, 256, Nr, Nt), dtype=torch.float64)
        eps = torch.randn(256, dim, dtype=torch.float64)
        for sv in (3.293572e-02, 0.1, 0.7908):
            sg2 = torch.full((256,), sv, dtype=torch.float64)
            cs_, co_, ci_, cn_ = edm_coeffs(sg2)
            xt = x0 + sg2.unsqueeze(-1) * eps
            D = edm_denoise(trained.raw, xt, sg2)
            lam = (sg2 ** 2 + 0.5) / (sg2 * SIGMA_DATA_DEFAULT) ** 2
            literal = (lam.unsqueeze(-1) * (D - x0) ** 2).mean()
            stable = edm_loss(trained.raw, x0, sg2, eps)
            rel = float((literal - stable).abs() / stable)
            ok(f"sigma={sv:.6f}  literal {float(literal):.12f}  stable {float(stable):.12f}  rel {rel:.3e}",
               rel < 1e-12)
        # unit-variance property of the target
        sg3 = edm_sigma_sample(4096, 3.293572e-02, 7.908e-01, torch.Generator().manual_seed(3)).double()
        x0b = torch.as_tensor(_corr_channels(rng, 4096, Nr, Nt), dtype=torch.float64)
        tg = edm_target(x0b, sg3, torch.randn(4096, dim, dtype=torch.float64))
        ok(f"E[target^2] == 1 (EDM unit-variance weighting): {float((tg ** 2).mean()):.6f}",
           abs(float((tg ** 2).mean()) - 1.0) < 0.05)

        # [6] THE TEST THAT MATTERS: analytic Gaussian prior, exact + finite-difference Tweedie
        P("\n[6] Tweedie / preconditioning algebra against the analytic Gaussian prior p = N(0, sd^2 I)")
        sd = SIGMA_DATA_DEFAULT
        # (a) D* = c_skip*x is reached with F_theta == 0, which is EDM's design statement: for an isotropic
        #     prior the optimal residual is exactly zero.  s* = (D*-x)/sigma^2 = -x/(sigma^2+sd^2).
        zero_raw = lambda u, c: torch.zeros_like(u)
        xg = torch.randn(512, dim, dtype=torch.float64)
        sg4 = edm_sigma_sample(512, 3.293572e-02, 7.908e-01, torch.Generator().manual_seed(5)).double()
        Dstar = (sd ** 2 / (sg4 ** 2 + sd ** 2)).unsqueeze(-1) * xg
        got_D = edm_denoise(zero_raw, xg, sg4, sd)
        got_s = edm_score(zero_raw, xg, sg4, sd)
        want_s = (Dstar - xg) / (sg4 ** 2).unsqueeze(-1)
        exact_s = -xg / (sg4 ** 2 + sd ** 2).unsqueeze(-1)              # grad log N(0,(sigma^2+sd^2)I)
        P(f"   max|D - D*|            = {float((got_D - Dstar).abs().max()):.3e}")
        P(f"   max|score - (D*-x)/s^2| = {float((got_s - want_s).abs().max()):.3e}")
        P(f"   max|score - exact|      = {float((got_s - exact_s).abs().max()):.3e}")
        ok("D == D* exactly", float((got_D - Dstar).abs().max()) < 1e-15)
        ok("edm_score == (D*-x)/sigma^2 to 1e-10", float((got_s - want_s).abs().max()) < 1e-10)
        ok("edm_score == -x/(sigma^2+sd^2) to 1e-10", float((got_s - exact_s).abs().max()) < 1e-10)
        # (b) a NON-TRIVIAL raw, so c_in and c_out placement is tested, not just c_skip.
        torch.manual_seed(13)
        W = torch.randn(dim, dim, dtype=torch.float64) / math.sqrt(dim)
        bvec = torch.randn(dim, dtype=torch.float64) * 0.1
        aff = lambda u, c: u @ W.T + bvec + c.unsqueeze(-1)
        cs_, co_, ci_, cn_ = edm_coeffs(sg4, sd)
        ref_D = cs_ * xg + co_ * ((ci_ * xg) @ W.T + bvec + cn_.unsqueeze(-1))
        ok("non-trivial raw: edm_denoise matches the hand-written c_skip/c_out/c_in composition",
           float((edm_denoise(aff, xg, sg4, sd) - ref_D).abs().max()) < 1e-15)
        ok("non-trivial raw: edm_score == (D - x)/sigma^2",
           float((edm_score(aff, xg, sg4, sd) - (ref_D - xg) / (sg4 ** 2).unsqueeze(-1)).abs().max()) < 1e-15)
        # (c) FINITE-DIFFERENCE Tweedie: central difference of log p_sigma against edm_score.
        xfd = torch.randn(8, dim, dtype=torch.float64)
        sfd = torch.tensor([0.05] * 8, dtype=torch.float64)
        var = float(sfd[0] ** 2 + sd ** 2)
        logp = lambda z: -0.5 * (z ** 2).sum(-1) / var
        h = 1e-5
        fd = torch.stack([(logp(xfd + h * torch.eye(dim, dtype=torch.float64)[k])
                           - logp(xfd - h * torch.eye(dim, dtype=torch.float64)[k])) / (2 * h)
                          for k in range(dim)], -1)
        fd_err = float((edm_score(zero_raw, xfd, sfd, sd) - fd).abs().max())
        P(f"   max|edm_score - central-difference grad log p_sigma| = {fd_err:.3e}  (h = {h})")
        ok("edm_score matches a finite-difference of log p_sigma", fd_err < 1e-6)

        # [7] trainability
        P("\n[7] trainability: 200 Adam steps on a fixed synthetic denoising task")
        torch.manual_seed(101)
        net = _mk_raw(Nr, Nt, "mlp", 256, 4, 128, seed=101).train()
        g = torch.Generator().manual_seed(202)
        x0t = torch.as_tensor(_corr_channels(np.random.default_rng(303), 256, Nr, Nt), dtype=torch.float32)
        sgt = edm_sigma_sample(256, 3.293572e-02, 7.908e-01, g)
        epst = torch.randn(256, dim, generator=g)
        opt = torch.optim.Adam(net.parameters(), lr=1e-3)
        torch.set_grad_enabled(True)
        l0 = float(edm_loss(net.raw, x0t, sgt, epst).detach())
        for _ in range(200):
            loss = edm_loss(net.raw, x0t, sgt, epst)
            opt.zero_grad(set_to_none=True); loss.backward(); opt.step()
        l1 = float(edm_loss(net.raw, x0t, sgt, epst).detach())
        torch.set_grad_enabled(False)
        P(f"   loss[0] = {l0:.6f}  (= E[target^2] ~ 1 at zero-init, as the docstring predicts)")
        P(f"   loss[200] = {l1:.6f}   reduction = {100 * (1 - l1 / l0):.2f}%")
        P("   (fixed 256-sample batch, so this is memorisation, not generalisation -- it is a TRAINABILITY"
          "\n    check: it fails if a gradient is detached, a coefficient is mis-shaped, or c_out kills the"
          "\n    signal.  Generalisation is the ladder's job, under the 9000/1000 split and the frozen gates.)")
        ok("200 Adam steps reduce the loss by >= 30%", (1 - l1 / l0) >= 0.30)

        # [8] parameter counts
        P("\n[8] parameter count per configured width (score.py DEFAULT_HP / ATTEMPT_HP widths)")
        for tag, a, w, dp, em in (("mlp", "mlp", 256, 4, 128), ("mlp", "mlp", 512, 6, 128),
                                  ("conv", "conv", 64, 4, 128), ("conv", "conv", 96, 6, 128),
                                  ("unet", "unet", 64, 4, 128), ("unet", "unet", 32, 4, 128)):
            m = _mk_raw(Nr, Nt, a, w, dp, em)
            P(f"   {tag:5s} width={w:<4d} depth={dp} emb={em} : {score.n_params(m):>10,d} params")

    # --- sigma draw -----------------------------------------------------------------------------------
    P(f"\n{'=' * 100}\n[9] edm_sigma_sample\n{'=' * 100}")
    lo, hi = 3.293572e-02, 7.908e-01
    g = torch.Generator().manual_seed(20260920)
    su = edm_sigma_sample(200000, lo, hi, g)
    ok(f"loguniform stays inside the frozen [lo, hi] = [{lo:.6e}, {hi:.6e}]",
       bool((su >= lo).all() and (su <= hi).all()), f"min {float(su.min()):.6e} max {float(su.max()):.6e}")
    lu = torch.log(su)
    ok(f"loguniform: mean log sigma {float(lu.mean()):.5f} vs uniform {0.5*(math.log(lo)+math.log(hi)):.5f}",
       abs(float(lu.mean()) - 0.5 * (math.log(lo) + math.log(hi))) < 0.01)
    # identical to score.py::train's own draw, given the same generator state
    g1, g2 = torch.Generator().manual_seed(9), torch.Generator().manual_seed(9)
    mine = edm_sigma_sample(1000, lo, hi, g1)
    theirs = torch.exp(torch.rand(1000, generator=g2) * (math.log(hi) - math.log(lo)) + math.log(lo))
    ok("loguniform draw is bit-for-bit score.py::train's draw", bool(torch.equal(mine, theirs)))
    sn = edm_sigma_sample(200000, lo, hi, torch.Generator().manual_seed(4), mode="lognormal")
    at_lo, at_hi = float((sn <= lo).float().mean()), float((sn >= hi).float().mean())
    ok(f"lognormal is clamped into the frozen range (mass at lo {100*at_lo:.2f}%, at hi {100*at_hi:.2f}%)",
       bool((sn >= lo).all() and (sn <= hi).all()))
    P(f"   lognormal(p_mean=-1.2, p_std=1.2) clamped: median {float(sn.median()):.6f}  "
      f"unclamped median would be {math.exp(-1.2):.6f}")
    try:
        edm_sigma_sample(4, lo, hi, g, mode="uniform"); ok("unknown mode raises", False)
    except ValueError:
        ok("unknown mode raises ValueError", True)

    P("\n" + "=" * 100)
    P("ALL CHECKS PASSED")
    P("=" * 100)
    return True


if __name__ == "__main__":
    # CPU-only by construction: 2N <= 64 reals, and the determinism assertions are bitwise.  The env var is
    # set BEFORE any CUDA call (torch initialises CUDA lazily) because torch 2.14's Adam.step() runs
    # torch.accelerator.current_stream() even for CPU parameters, which fails outright on a machine whose
    # GPUs are all Compute Mode Exclusive_Process and occupied.
    import os
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    print("param_edm self-test: CPU only (CUDA_VISIBLE_DEVICES forced empty)")
    selftest()
