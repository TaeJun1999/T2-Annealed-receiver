"""exp_0919_tests.py — session-3 unit / regression tests, merged into one file (sources: exp_0919_t0_bcjr_vec.py, exp_0919_t1_sanity.py,
exp_0919_t5_scalarization_closedform.py, exp_0919_t6_matrix_site.py, exp_0919_t7_newparts.py; bodies unchanged, only indented).
usage:  python exp_0919_tests.py <t0|t1|t5|t6|t7|all>        (run with 2>/dev/null; needs t2_trellis.py, t2_route_a.py, exp_0919_common.py in .)
  t0  vectorised SymbolTrellis.bcjr vs brute force / bcjr_loop (QPSK, 16-QAM, 64-QAM; per-symbol tau; info LLRs; tilted prior)   ~10 s
  t1  QPSK sanity inside RouteA: rho = 0 -> H extrinsic == prior, scalar == colored; wall-clock per run                                ~25 s
  t5  L_H -> H scalarisation rules, Gaussian closed form (site vs belief; fixed-point mean == exact LMMSE)                              ~5 s
  t6  matrix H-site (full Jacobian, D-14) == mode 'colored' for a Gaussian prior                                                      ~10 s
  t7  exact extrinsic pmf vs brute force; GMMPrior denoiser / Tweedie / Jacobian / Monte-Carlo MMSE; ensemble covariance == I          ~45 s
Each section writes ./exp_0919_results_T<k>.txt as before."""
import sys
_WHICH = sys.argv[1] if len(sys.argv) > 1 else "all"
def _run(name): return _WHICH in (name, "all")

if _run("t0"):
    # ---------------- merged from exp_0919_t0_bcjr_vec.py
    """
    exp_0919 T0 — regression of the vectorised SymbolTrellis.bcjr (t2_trellis.py, exp_0919) against
     (a) brute force over all 2^K codewords (per-symbol tau, info-bit LLRs, tilted prior), QPSK / 16-QAM / 64-QAM, (133,171)_8 nu=6;
     (b) the original per-state loop implementation (bcjr_loop) on full-length blocks (Ns = 96/104 as in exp_0919, K = 90/98),
         including extreme per-symbol variances (tau in [1e-3, 1e8], the L_X clip value);
     (c) wall-clock. Seed 20260919.
    """
    import sys, time, numpy as np
    from scipy.special import logsumexp
    sys.path.insert(0, ".")
    from t2_trellis import SymbolTrellis, soft_symbols
    SEED, GENS, NU = 20260919, ("133", "171"), 6
    out = []
    def P_(*a):
        s = " ".join(str(x) for x in a); print(s, flush=True); out.append(s)
    rng = np.random.default_rng(SEED)

    P_("=== T0 (exp_0919): vectorised SymbolTrellis.bcjr ===")
    for m, K in ((2, 8), (4, 8), (6, 9)):
        st = SymbolTrellis(GENS, NU, m); Ns = st.n_symbols(K); A = 1 << m
        U = ((np.arange(1 << K)[:, None] >> np.arange(K)[None, :]) & 1)
        SYMIDX = np.array([st.encode_symbols(u)[0] for u in U]); SYM = st.CONST[SYMIDX]
        e = dict(P=0.0, Lu=0.0, xbar=0.0, v=0.0, Ptilt=0.0, loop=0.0)
        for trial in range(6):
            lo, hi = (0.1, 3.0) if trial < 4 else (0.02, 30.0)
            tau = np.exp(rng.uniform(np.log(lo), np.log(hi), Ns))
            r = SYM[rng.integers(1 << K)] + np.sqrt(tau / 2) * (rng.standard_normal(Ns) + 1j * rng.standard_normal(Ns))
            ll = -np.sum(np.abs(r[None, :] - SYM) ** 2 / tau[None, :], axis=1); w = np.exp(ll - logsumexp(ll))
            Pbf = np.zeros((Ns, A))
            for k in range(Ns): np.add.at(Pbf[k], SYMIDX[:, k], w)
            # info-bit LLRs: section k carries q bits msb-first -> info index k*q+i
            Lu_bf = np.array([logsumexp(ll[U[:, k] == 0]) - logsumexp(ll[U[:, k] == 1]) for k in range(K)])
            Pv, Lu = st.bcjr(r, tau, K, return_info=True)
            xb, v = soft_symbols(Pv, st.CONST); xb_bf, v_bf = soft_symbols(Pbf, st.CONST)
            e["P"] = max(e["P"], np.max(np.abs(Pv - Pbf))); e["Lu"] = max(e["Lu"], np.max(np.abs(Lu.reshape(-1) - Lu_bf)))
            e["xbar"] = max(e["xbar"], np.max(np.abs(xb - xb_bf))); e["v"] = max(e["v"], np.max(np.abs(v - v_bf)))
            # tilted prior (Cor. 1.2(ii)): random log-prior on symbols
            lp = rng.standard_normal((Ns, A))
            llt = ll + lp[np.arange(Ns)[None, :], SYMIDX].sum(1); wt = np.exp(llt - logsumexp(llt))
            Pt_bf = np.zeros((Ns, A))
            for k in range(Ns): np.add.at(Pt_bf[k], SYMIDX[:, k], wt)
            e["Ptilt"] = max(e["Ptilt"], np.max(np.abs(st.bcjr(r, tau, K, log_prior=lp) - Pt_bf)))
            Pl, Lul = st.bcjr_loop(r, tau, K, return_info=True)
            e["loop"] = max(e["loop"], np.max(np.abs(Pv - Pl)), np.max(np.abs(Lu - Lul)))
        P_(f"T0a m={m} K={K} (Ns={Ns}, {1 << K} codewords) vs brute force: max|dP| = {e['P']:.2e}, max|dLu| = {e['Lu']:.2e}, "
           f"max|dxbar| = {e['xbar']:.2e}, max|dv| = {e['v']:.2e}, tilted max|dP| = {e['Ptilt']:.2e}; vs bcjr_loop = {e['loop']:.2e}")

    P_("--- T0b full-length blocks vs bcjr_loop (no brute force possible) ---")
    for m, Ns in ((2, 96), (2, 104), (4, 48)):
        st = SymbolTrellis(GENS, NU, m); K = Ns * st.q - NU
        worst = [0.0, 0.0]; t_vec = t_loop = 0.0
        for trial in range(4):
            u = rng.integers(0, 2, K); x = st.encode_symbols(u)[1]
            if trial < 2:   tau = np.exp(rng.uniform(np.log(0.05), np.log(3.0), Ns))
            elif trial == 2: tau = np.exp(rng.uniform(np.log(1e-3), np.log(1e2), Ns))          # very confident ... very noisy
            else:
                tau = np.exp(rng.uniform(np.log(0.05), np.log(3.0), Ns)); tau[rng.integers(0, Ns, 6)] = 1e8   # L_X clip value (F4)
            r = x + np.sqrt(np.minimum(tau, 10) / 2) * (rng.standard_normal(Ns) + 1j * rng.standard_normal(Ns))
            t0 = time.time(); Pv, Lu = st.bcjr(r, tau, K, return_info=True); t_vec += time.time() - t0
            t0 = time.time(); Pl, Lul = st.bcjr_loop(r, tau, K, return_info=True); t_loop += time.time() - t0
            dl = np.abs(Lu - Lul) / (1 + np.abs(Lul)); assert not np.isnan(dl).any()
            worst[0] = max(worst[0], np.max(np.abs(Pv - Pl))); worst[1] = max(worst[1], np.max(dl))
            assert np.all(np.isfinite(Pv)) and np.all(np.isfinite(Lu)) and np.array_equal(Lu < 0, Lul < 0)   # finite, same hard decisions
        P_(f"T0b m={m} Ns={Ns} K={K}: max|dP| = {worst[0]:.2e}, max rel|dLu| = {worst[1]:.2e}; wall-clock/call: vectorised {t_vec / 4 * 1e3:.1f} ms vs loop {t_loop / 4 * 1e3:.0f} ms")
    with open("./exp_0919_results_T0.txt", "w") as f: f.write("\n".join(out) + "\n")

if _run("t1"):
    # ---------------- merged from exp_0919_t1_sanity.py
    """exp_0919 T1 — QPSK sanity inside RouteA (first execution of QAMCode in the loop).
    (1) rho = 0: Module H extrinsic must equal the prior (hE = 0, nuE = 1) at every iteration, and mode 'scalar' == mode 'colored'.
    (2) wall-clock per RouteA.run, per mode."""
    import sys, time, numpy as np
    sys.path.insert(0, ".")
    from exp_0919_common import *
    out = []
    def P(*a):
        s = " ".join(str(x) for x in a); print(s, flush=True); out.append(s)
    P("=== T1 (exp_0919) QPSK sanity: rho = 0 -> H extrinsic == prior; scalar == colored ===")
    modes = {"scalar": dict(mode="scalar"), "colored": dict(mode="colored")}
    for Tp in (4, 2):
        agg = run_trials(Tp, 6.0, modes, 10, 6, SEED + 1, rho=0.0)
        s, c = agg["scalar"], agg["colored"]
        P(f"Tp={Tp}: max||hE|| = {np.max(s['hE_norm']):.1e}, max|nuE-1| = {np.max(np.abs(s['nuE'] - 1)):.1e}, "
          f"max|NMSE_s - NMSE_c| = {np.max(np.abs(s['nmse'] - c['nmse'])):.1e}, "
          f"max|tauL_s - tauL_c|/tauL = {np.max(np.abs(s['tauL_gmean'] - c['tauL_gmean']) / c['tauL_gmean']):.1e}, BER_s == BER_c: {np.array_equal(s['ber'], c['ber'])}")
        P(f"      NMSE traj (scalar, mean): {fmt(s['nmse'].mean(0))};  nu_q traj: {fmt(s['nu_q'].mean(0))};  BLER: {fmt(s['blk_err'].mean(0), '{:.2f}')}")
    # same check with damping + colored-init options switched on (they must not break the identity)
    agg = run_trials(2, 6.0, {"scalar": dict(mode="scalar", beta=0.7, init_colored=1), "colored": dict(mode="colored", beta=0.7)}, 10, 6, SEED + 1, rho=0.0)
    s, c = agg["scalar"], agg["colored"]
    P(f"Tp=2, beta=0.7, init_colored=1: max||hE|| = {np.max(s['hE_norm']):.1e}, max|nuE-1| = {np.max(np.abs(s['nuE'] - 1)):.1e}, max|NMSE_s - NMSE_c| = {np.max(np.abs(s['nmse'] - c['nmse'])):.1e}")
    P("--- wall-clock per RouteA.run (8 iterations, rho = 0.7, Tp = 4, 6 dB), QPSK vs BPSK ---")
    for mod in ("qpsk", "bpsk"):
        for name in ("scalar", "colored", "pilot_only", "genie"):
            t0 = time.time(); run_trials(4, 6.0, {name: dict(mode=name)}, 5, 8, SEED + 2, mod=mod); P(f"  {mod:5s} {name:10s}: {(time.time() - t0) / 5:.3f} s/run")
    with open("./exp_0919_results_T1.txt", "w") as f: f.write("\n".join(out) + "\n")

if _run("t5"):
    # ---------------- merged from exp_0919_t5_scalarization_closedform.py
    """exp_0919 T5 — closed-form check of the two scalarisation rules for the L_H -> H message (Gaussian prior, no decoder in the loop).
    Setting: 4x4, rho = 0.7, pilots only (DFT, Tp in {2,4}) at 6 dB, i.e. the very first channel-side pass of RouteA (r^D = 0, tau^D = 1).
    Claim [exact, Gaussian prior]: with 'belief' scalarisation the fixed point of the inner L_H <-> H iteration has the exact LMMSE mean
      h* = (C^{-1} + G)^{-1} b   (only the covariance stays approximate), whereas 'site' scalarisation is a one-shot map that returns
      (hE, nuE) ~ isotropic prior when G is singular (F1)."""
    import sys, numpy as np
    sys.path.insert(0, ".")
    from t2_route_a import KronGaussianPrior, dft_pilots
    out = []
    def P_(*a):
        s = " ".join(str(x) for x in a); print(s, flush=True); out.append(s)
    rng = np.random.default_rng(20260919 + 5)
    Nr = Nt = 4; N = 16; rho = 0.7; sigma2 = 10 ** (-0.6); I = np.eye(N)
    prior = KronGaussianPrior(Nr, Nt, rho)
    P_("=== T5 (exp_0919): L_H -> H scalarisation, Gaussian closed form, pilots only, 6 dB, rho = 0.7 ===")
    for Tp in (2, 4):
        Xp = dft_pilots(Nt, Tp); res = {k: [] for k in ("site", "b1", "b2", "b3", "b5", "b10", "b30", "lmmse_iso")}; nuq = {}
        for trial in range(200):
            H = prior.sample(rng); h = H.reshape(-1, order="F")
            Y = H @ Xp + np.sqrt(sigma2 / 2) * (rng.standard_normal((Nr, Tp)) + 1j * rng.standard_normal((Nr, Tp)))
            G = sum(np.kron(np.outer(Xp[:, n].conj(), Xp[:, n]), np.eye(Nr)) for n in range(Tp)) / sigma2
            b = sum(np.kron(Xp[:, n].conj(), Y[:, n]) for n in range(Tp)) / sigma2
            h_star = np.linalg.solve(prior.Cinv + G, b)                                   # exact colored LMMSE mean
            nm = lambda e: np.sum(np.abs(e - h_star) ** 2) / np.sum(np.abs(h_star) ** 2)  # distance to the exact posterior mean
            # site scalarisation (v0)
            Cq = np.linalg.inv(G + I / 1e4); q = Cq @ b; nu_q = np.trace(Cq).real / N
            hH, a = prior.denoise(q, nu_q); hE = (hH - a * q) / (1 - a); nuE = a / (1 - a) * nu_q
            res["site"].append(nm(np.linalg.solve(I / nuE + G, hE / nuE + b))); nuq["site"] = nu_q
            res["lmmse_iso"].append(nm(np.linalg.solve(I / prior.cbar + G, b)))
            # belief scalarisation, n_inner passes
            hE = np.zeros(N, complex); nuE = prior.cbar
            for it in range(1, 31):
                SigL = np.linalg.inv(I / nuE + G); hL = SigL @ (hE / nuE + b)
                aL = np.trace(SigL).real / N / nuE; nu_q = aL / (1 - aL) * nuE; q = (hL - aL * hE) / (1 - aL)
                hH, a = prior.denoise(q, nu_q); hE = (hH - a * q) / (1 - a); nuE = a / (1 - a) * nu_q
                if it in (1, 2, 3, 5, 10, 30):
                    res[f"b{it}"].append(nm(np.linalg.solve(I / nuE + G, hE / nuE + b)))
                    if it == 1: nuq["b1"] = nu_q
                    if it == 30: nuq["b30"] = (nu_q, nuE)
        P_(f"Tp={Tp}: ||h_Lx - h*||^2/||h*||^2 (median over 200 draws; h_Lx = channel mean handed to L_X, h* = exact colored LMMSE)")
        P_("   " + " | ".join(f"{k}: {np.median(v):.2e}" for k, v in res.items()))
        P_(f"   nu_q: site {nuq['site']:.3g}, belief pass 1 {nuq['b1']:.3g}, belief pass 30 (nu_q, nuE) = ({nuq['b30'][0]:.3g}, {nuq['b30'][1]:.3g})")
    with open("./exp_0919_results_T5.txt", "w") as f: f.write("\n".join(out) + "\n")

if _run("t6"):
    # ---------------- merged from exp_0919_t6_matrix_site.py
    """exp_0919 T6 — unit test: matrix-valued H extrinsic (full Jacobian) == mode 'colored' for a Gaussian prior, for both scalarisation rules."""
    import sys, numpy as np
    sys.path.insert(0, ".")
    from exp_0919_common import *
    out = []
    def P(*a):
        s = " ".join(str(x) for x in a); print(s, flush=True); out.append(s)
    P("=== T6 (exp_0919): H -> L matrix site from the full Jacobian vs mode 'colored' (Gaussian prior, rho = 0.7, QPSK, 6 dB, 10 trials, 6 iter) ===")
    for Tp in (4, 2):
        agg = run_trials(Tp, 6.0, {"colored": dict(mode="colored"), "mat_site": dict(mode="scalar", hsite="matrix"),
                                   "mat_belief": dict(mode="scalar", hsite="matrix", scal="belief"), "scalar": dict(mode="scalar")}, 10, 6, SEED + 6)
        c = agg["colored"]
        for n in ("mat_site", "mat_belief", "scalar"):
            a = agg[n]
            P(f"Tp={Tp} {n:10s}: max|NMSE - NMSE_colored| = {np.max(np.abs(a['nmse'] - c['nmse'])):.1e}, max rel|tauL - tauL_colored| = "
              f"{np.max(np.abs(a['tauL_gmean'] - c['tauL_gmean']) / c['tauL_gmean']):.1e}, BER identical: {np.array_equal(a['ber'], c['ber'])}")
    with open("./exp_0919_results_T6.txt", "w") as f: f.write("\n".join(out) + "\n")

if _run("t7"):
    # ---------------- merged from exp_0919_t7_newparts.py
    """exp_0919 T7 — unit tests of the new parts. Seed 20260919+7.
    (a) exact extrinsic symbol pmf P(x_n = a | r_{\\n}) from SymbolTrellis.bcjr(return_ext=True) vs brute force (QPSK, 16-QAM; per-symbol tau);
        BPSK wrapper: L_ext = L_app - L_ch vs brute force.
    (b) GMMPrior: K=1 == KronGaussianPrior; complex Tweedie m = q + nu grad_{q*} log p_nu (finite differences); Wirtinger Jacobian dm/dq == Cov/nu (FD);
        alpha == tr(J)/N; Monte-Carlo MMSE == E tr Cov; ensemble covariance of the 4x4-direction steering mixture == I."""
    import sys, numpy as np
    from scipy.special import logsumexp
    sys.path.insert(0, ".")
    from t2_trellis import SymbolTrellis, soft_symbols, all_codewords
    from t2_route_a import KronGaussianPrior, GaussianPrior, GMMPrior, steer_corr, BPSKCode
    out = []
    def P_(*a):
        s = " ".join(str(x) for x in a); print(s, flush=True); out.append(s)
    rng = np.random.default_rng(20260919 + 7); GENS, NU = ("133", "171"), 6
    P_("=== T7a exact extrinsic pmf vs brute force ===")
    for m, K in ((2, 8), (4, 8)):
        st = SymbolTrellis(GENS, NU, m); Ns = st.n_symbols(K); A = 1 << m
        U = ((np.arange(1 << K)[:, None] >> np.arange(K)[None, :]) & 1)
        SYMIDX = np.array([st.encode_symbols(u)[0] for u in U]); SYM = st.CONST[SYMIDX]; worst = 0.0
        for trial in range(5):
            tau = np.exp(rng.uniform(np.log(0.05), np.log(3.0), Ns))
            r = SYM[rng.integers(1 << K)] + np.sqrt(tau / 2) * (rng.standard_normal(Ns) + 1j * rng.standard_normal(Ns))
            per = -np.abs(r[None, :] - SYM) ** 2 / tau[None, :]; tot = per.sum(1)
            Pe_bf = np.zeros((Ns, A))
            for n in range(Ns):
                l = tot - per[:, n]; w = np.exp(l - logsumexp(l)); np.add.at(Pe_bf[n], SYMIDX[:, n], w)
            P, Lu, Pe = st.bcjr(r, tau, K, return_info=True, return_ext=True)
            worst = max(worst, np.max(np.abs(Pe - Pe_bf)))
        P_(f"  m={m} K={K}: max|dP_ext| = {worst:.2e}")
    code = BPSKCode(GENS, NU, 28); CW = 1 - 2 * all_codewords(8, code.tr.nxt, code.tr.out, NU); worst = 0.0
    for trial in range(5):
        tau = np.exp(rng.uniform(np.log(0.1), np.log(3.0), 28)); x = CW[rng.integers(256)]
        r = x + np.sqrt(tau / 2) * (rng.standard_normal(28) + 1j * rng.standard_normal(28))
        per = -np.abs(r[None, :] - CW) ** 2 / tau[None, :]; tot = per.sum(1)
        xe_bf = np.array([np.sum(np.exp((tot - per[:, n]) - logsumexp(tot - per[:, n])) * CW[:, n]) for n in range(28)])
        worst = max(worst, np.max(np.abs(code.decode(r, tau, ext=True)[3].real - xe_bf)))
    P_(f"  BPSK K=8: max|d r_ext| = {worst:.2e}")

    P_("=== T7b GMMPrior (closed-form score / denoiser / Jacobian) ===")
    Nr = Nt = 4; N = 16
    kp = KronGaussianPrior(Nr, Nt, 0.7); g1 = GMMPrior(Nr, Nt, [kp.C])
    q = (rng.standard_normal(N) + 1j * rng.standard_normal(N)); e = []
    for nu in (0.01, 0.3, 5.0):
        m0, a0 = kp.denoise(q, nu); m1, a1 = g1.denoise(q, nu); J1 = g1.denoise_full(q, nu)[1]; J0 = kp.denoise_full(q, nu)[1]
        e.append(max(np.max(np.abs(m0 - m1)), abs(a0 - a1), np.max(np.abs(J0 - J1))))
    P_(f"  K=1 mixture vs KronGaussianPrior (mean, alpha, J): max err = {max(e):.2e}")
    psis = 2 * np.pi * (np.arange(4) + 0.5) / 4
    covs = [np.kron(steer_corr(Nt, 0.9, pt).T, steer_corr(Nr, 0.9, pr)) for pt in psis for pr in psis]
    gm = GMMPrior(Nr, Nt, covs)
    P_(f"  steering mixture: K = {gm.K}, ||C_hat - I||_max = {np.max(np.abs(gm.C - np.eye(N))):.1e}, per-component eig(R_exp(0.9)) = "
       f"{np.round(np.linalg.eigvalsh(steer_corr(4, 0.9, 0.3))[::-1], 3)}")
    for nu in (0.02, 0.3, 1.1):
        H = gm.sample(rng); h = H.reshape(-1, order="F")
        q = h + np.sqrt(nu / 2) * (rng.standard_normal(N) + 1j * rng.standard_normal(N))
        m, J = gm.denoise_full(q, nu); m_, a_ = gm.denoise(q, nu); d = 1e-6
        grad = np.zeros(N, complex); Jfd = np.zeros((N, N), complex)
        for i in range(N):
            ei = np.zeros(N, complex); ei[i] = d
            gr = (gm.log_pdf_noisy(q + ei, nu) - gm.log_pdf_noisy(q - ei, nu)) / (2 * d)
            gi = (gm.log_pdf_noisy(q + 1j * ei, nu) - gm.log_pdf_noisy(q - 1j * ei, nu)) / (2 * d)
            grad[i] = 0.5 * (gr + 1j * gi)
            dr = (gm.denoise(q + ei, nu)[0] - gm.denoise(q - ei, nu)[0]) / (2 * d); di = (gm.denoise(q + 1j * ei, nu)[0] - gm.denoise(q - 1j * ei, nu)[0]) / (2 * d)
            Jfd[:, i] = 0.5 * (dr - 1j * di)
        P_(f"  nu={nu}: Tweedie |m - (q + nu grad)|_max = {np.max(np.abs(m - (q + nu * grad))):.1e}; |J - J_FD|_max = {np.max(np.abs(J - Jfd)):.1e}; "
           f"|alpha - tr(J)/N| = {abs(a_ - np.trace(J).real / N):.1e}; min eig(J) = {np.linalg.eigvalsh(0.5 * (J + J.conj().T)).min():.3f}, max eig(J) = {np.linalg.eigvalsh(0.5 * (J + J.conj().T)).max():.3f}")
    for nu in (0.05, 1.1):
        se = trc = 0.0; n_mc = 4000; amax = 0.0
        for _ in range(n_mc):
            h = gm.sample(rng).reshape(-1, order="F"); q = h + np.sqrt(nu / 2) * (rng.standard_normal(N) + 1j * rng.standard_normal(N))
            m, a = gm.denoise(q, nu); se += np.sum(np.abs(h - m) ** 2); trc += a * N * nu; amax = max(amax, a)
        P_(f"  nu={nu}: Monte-Carlo MSE/N = {se / n_mc / N:.4f} vs E[tr Cov]/N = {trc / n_mc / N:.4f} (4000 draws); max alpha over draws = {amax:.3f}; "
           f"ensemble-Gaussian (C_hat = I) LMMSE MSE/N = {nu / (1 + nu):.4f}")
    with open("./exp_0919_results_T7.txt", "w") as f: f.write("\n".join(out) + "\n")

