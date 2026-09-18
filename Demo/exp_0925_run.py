"""exp_0925 runner — D-19 kill test (pre-registration: docs/logs/decision_log.md, entries D-19 and "D-19 보정" of 2026-09-17/18).
QPSK, (133,171)_8 nu = 6 terminated, Nt = 4, 16 iterations, every joint arm = D-15 + LOO + beta 0.7 (v1 configuration).

  python exp_0925_run.py prior                 closed-form report on the 'true' priors U / S / P (ensemble spectra, pilots)                    (< 5 s)
  python exp_0925_run.py fit                   EM fits: family {full, kron} x K {16,32,64} x kappa {0,16,64,256} (full only) x restarts, per prior x Nr in {4,8};
                                               selection by VALIDATION log-likelihood only (never by BLER) -> exp_0925_fits/*.npz + KL gaps on an independent test set
  python exp_0925_run.py time                  seconds per RouteA.run for every arm, both cells (2 trials, prior S)                            (needs the fits)
  python exp_0925_run.py K                     the kill-test run: cells x priors x SNR grid, n = 640 per point -> exp_0925_raw/*.npz            (needs the fits)
  options: --n 640  --chunk 40  --cells H R  --priors U S P  --snr ...  --ntrain 10000  --restarts 4  --fit-iters 300  --jobs J (default: all cores)  --tag X
           (--tag X: fits / raw go to exp_0925_fits_X / exp_0925_raw_X; used for smoke tests so that they never mix with the real run)

True priors (t2_gmm.angle_grid_prior; dense 32 x 32 angle grid = 1024 components DEFINES the continuous-angle prior; per-component rho_c = 0.7):
  U  psi_t, psi_r uniform on [0, 2pi)                 ensemble covariance = I exactly            pilots: DFT
  S  psi_t, psi_r uniform on [-pi/3, pi/3]            informative ensemble covariance (D-19 literal "+-60 deg" in the electrical angle)   pilots: eig of R_t,ens
  P  psi_t full, psi_r = pi sin(theta), |theta| <= 60 deg   lambda/2 ULA, standard 120-deg sector; ensemble covariance nearly white        pilots: DFT
Cells:  H (headline) = 8x4, T = 16, Tp = 2, SNR -3..15 dB;   H4 = same with Tp = 4 = Nt (cross-Tp goodput baseline: what the second-moment method needs when
  R_t,ens = I, where its Tp = 2 first pass has NMSE_inf = 0.5 [exact]);   R (reference, comparable with exp_0921 C) = 4x4, T = 28, Tp = 2, SNR 9/12/15 dB.
Arms (pre-registered):  (a) lmmseC_pf  Gaussian prior with the SAMPLE covariance of the training set;  (b) Hgmm-K{16,32,64}  EM-fitted full-covariance GMM (MAP shrinkage kappa and
  stopping iteration chosen by validation log-lik) + exact mixture-EP site;  Hgmm-kron  Kronecker-structured components, K chosen by validation log-lik;
  (b*) := the Hgmm arm with the best validation log-lik (recorded in every raw file as meta|bstar; selection never sees BLER);
  (c) Hscore-exact  exact score of the TRUE prior + one-shot interface D-13 + D-14;  (d) exactEP-true  exact site of the true prior;  pilot_C, pilot_Hgmm-K32, genie.
Diagnostic arms (not part of K1-K3):  Hscore-K32 (fitted prior through the one-shot interface: 2x2 factorial prior{true,fit} x interface{exact site, one-shot}),
  oracle_pf (true component known),  *-mp = mean-preserving clip (t2_gmm.GMMPriorB.ep_site / RouteAClip) for (b,K=32), (c), (d).

Reproducibility: SEED = 20260925. Trials of a point come from ONE stream  default_rng([SEED, prior_id, Nr, T, int(snr) + 100]); a task = (point, skip, chunk) regenerates
the skipped trials, so chunks concatenate and every arm at a point sees the same (H, u, perm, Y). Training set: default_rng([SEED, 7, prior_id, Nr]); validation set
(n_val = 5000): [SEED, 8, prior_id, Nr]; test set (reporting only): [SEED, 10, prior_id, Nr]; EM restart: [SEED, 9, prior_id, Nr, fam_id, K, kappa, r].
Finished fits / chunks are skipped on re-run."""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"): os.environ.setdefault(_v, "1")   # one BLAS thread per worker
import sys, time, argparse, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from t2_route_a import GaussianPrior, QAMCode, RouteA, dft_pilots
from t2_gmm import GMMPriorB, RouteAClip, fit_gmm_em, angle_grid_prior, ensemble_sides, PRIOR_DOC

GENS, NU, SEED, NT, N_ITER, RHO_C, KG, N_VAL = ("133", "171"), 6, 20260925, 4, 16, 0.7, 32, 5000
CELLS = {"H": dict(Nr=8, T=16, Tp=2, snrs=(-3, 0, 3, 6, 9, 12, 15)), "H4": dict(Nr=8, T=16, Tp=4, snrs=(-3, 0, 3, 6, 9, 12, 15)), "R": dict(Nr=4, T=28, Tp=2, snrs=(9, 12, 15))}
PID = {"U": 0, "S": 1, "P": 2}; KS = (16, 32, 64); KAPPAS = (0, 16, 64, 256); FAM = {"full": 0, "kron": 1}; LAM = 1e-6
KEYS = ("blk_err", "ber", "nmse", "tauL_gmean", "alphaD")
TAG = ""


def _init(tag):
    global TAG; TAG = tag                                                                          # worker initialiser (robust to spawn / forkserver start methods)


def d_fits(): return os.path.join(HERE, "exp_0925_fits" + (f"_{TAG}" if TAG else ""))
def d_raw(): return os.path.join(HERE, "exp_0925_raw" + (f"_{TAG}" if TAG else ""))
def fit_file(prior, Nr, fam, K, ntrain): return os.path.join(d_fits(), f"fit_{prior}_Nr{Nr}_{fam}K{K}_n{ntrain}.npz")


def make_pilots(prior, Tp):
    """DFT unless the transmit-side ensemble covariance is informative (prior S): then sqrt(Nt) * top-Tp eigenvectors of R_t,ens (same rule as exp_0921 'eig')."""
    if prior != "S": return "dft", dft_pilots(NT, Tp)
    Rt, _ = ensemble_sides(prior, 4, NT, RHO_C, KG); w, U = np.linalg.eigh(Rt); U = U[:, ::-1]
    U = U * np.exp(-1j * np.angle(U[np.argmax(np.abs(U), 0), np.arange(NT)]))                      # fix the eigenvector phase (platform independent)
    return "eig", np.sqrt(NT) * U[:, :Tp]


# ----------------------------------------------------------------------------- prior report (closed form)
def cmd_prior():
    """Second-moment facts [exact]: the LMMSE error of ANY linear method depends on the prior only through C_ens = kron(R_t,ens^T, R_r,ens). High-SNR first pass (exp_0921 F5):
    NMSE_inf = tr S / tr R_t,  S = R_t - R_t Xp (Xp^H R_t Xp)^-1 Xp^H R_t  -> what arm (a) starts from; 'captured' = tr(P_Xp R_t) / tr R_t."""
    np.set_printoptions(precision=3, suppress=True, linewidth=170)
    for kind in PID:
        print(f"prior {kind}: {PRIOR_DOC[kind]}")
        for Nr in (4, 8):
            Rt, Rr = ensemble_sides(kind, Nr, NT, RHO_C, KG); et, er = np.linalg.eigvalsh(Rt)[::-1], np.linalg.eigvalsh(Rr)[::-1]
            print(f"  {Nr}x{NT}: eig R_t,ens {et}   eig R_r,ens {er}   eff.rank(C_ens) = {(et.sum() ** 2 / (et ** 2).sum()) * (er.sum() ** 2 / (er ** 2).sum()):.1f}/{Nr * NT}")
        for name, Xp in (("dft", dft_pilots(NT, 2)),) + (((("eig",) + make_pilots(kind, 2)[1:]),) if kind == "S" else ()):
            Pj = Xp @ np.linalg.inv(Xp.conj().T @ Xp) @ Xp.conj().T; S = Rt - Rt @ Xp @ np.linalg.inv(Xp.conj().T @ Rt @ Xp) @ Xp.conj().T @ Rt
            print(f"  pilots {name} (Tp=2): captured transmit power {np.trace(Pj @ Rt).real / np.trace(Rt).real:.3f},  second-moment first pass NMSE_inf = {np.trace(S).real / np.trace(Rt).real:.3f}"
                  + ("   <- used" if name == make_pilots(kind, 2)[0] else ""))


# ----------------------------------------------------------------------------- fit stage
def _sets(prior, Nr, ntrain):
    true = angle_grid_prior(prior, Nr, NT, RHO_C, KG)
    return (true,) + tuple(true.sample_vecs(np.random.default_rng([SEED, sid, PID[prior], Nr]), n)[0] for sid, n in ((7, ntrain), (8, N_VAL), (10, N_VAL)))


def fit_task(task):
    prior, Nr, fam, K, kappa, r, ntrain, iters = task; t0 = time.time(); true, X, Xv, Xt = _sets(prior, Nr, ntrain)
    f = fit_gmm_em(X, K, np.random.default_rng([SEED, 9, PID[prior], Nr, FAM[fam], K, kappa, r]), n_iter=iters, kappa=float(kappa), struct=fam, dims=(Nr, NT), Xval=Xv)
    f["ll_test"] = float(GMMPriorB(Nr, NT, f["covs"], f["pi"]).log_pdf(Xt).mean()); f["ll_train"] = float(f["ll"][f["it_best"]]); f["sec"] = time.time() - t0
    return task[:6], f


def ref_task(task):
    prior, Nr, ntrain = task; true, X, Xv, Xt = _sets(prior, Nr, ntrain); Chat = X.T @ X.conj() / len(X); g = GMMPriorB(Nr, NT, Chat[None])
    return (prior, Nr), dict(true_val=float(true.log_pdf(Xv).mean()), true_test=float(true.log_pdf(Xt).mean()), gauss_val=float(g.log_pdf(Xv).mean()), gauss_test=float(g.log_pdf(Xt).mean()))


def cmd_fit(a):
    import multiprocessing as mp
    os.makedirs(d_fits(), exist_ok=True); Nrs = sorted({CELLS[c]["Nr"] for c in a.cells})
    todo = [(p, Nr, fam, K) for p in a.priors for Nr in Nrs for fam in FAM for K in KS if not os.path.exists(fit_file(p, Nr, fam, K, a.ntrain))]
    tasks = [t + (kap, r, a.ntrain, a.fit_iters) for t in todo for kap in (KAPPAS if t[2] == "full" else (0,)) for r in range(a.restarts)]; tasks.sort(key=lambda t: -t[1] * t[3])
    print(f"[fit] {len(todo)} fits -> {len(tasks)} EM runs on {a.jobs} workers (ntrain = {a.ntrain}, n_val = n_test = {N_VAL}, kappa grid {KAPPAS}, restarts {a.restarts})", flush=True)
    t0 = time.time(); res = {}
    with mp.Pool(min(a.jobs, max(len(tasks), 1)), initializer=_init, initargs=(TAG,)) as pool:
        refs = dict(pool.imap_unordered(ref_task, sorted({(t[0], t[1], a.ntrain) for t in todo})))
        for i, (key, f) in enumerate(pool.imap_unordered(fit_task, tasks)):
            res.setdefault(key[:4], {})[key[4:]] = f
            print(f"  {i + 1}/{len(tasks)} {key}: iters {f['n_iter']} best@{f['it_best']} reseeds {f['n_reseed']} ll_train {f['ll_train']:.3f} ll_val {f['ll_val']:.3f} ({f['sec']:.0f} s)", flush=True)
    for (p, Nr, fam, K), rs in sorted(res.items()):
        kb = max(rs, key=lambda k: rs[k]["ll_val"]); f = rs[kb]; ref = refs[(p, Nr)]; cand = sorted(rs)
        np.savez_compressed(fit_file(p, Nr, fam, K, a.ntrain), pi=f["pi"], covs=f["covs"], Chat=f["Chat"], ll=f["ll"], kappa=kb[0], restart=kb[1], it_best=f["it_best"], n_iter=f["n_iter"],
                            n_reseed=f["n_reseed"], ll_train=f["ll_train"], ll_val=f["ll_val"], ll_test=f["ll_test"], kl_test=ref["true_test"] - f["ll_test"], kl_test_gauss=ref["true_test"] - ref["gauss_test"],
                            cand=np.array(cand), cand_ll_val=np.array([rs[c]["ll_val"] for c in cand]), cand_ll_test=np.array([rs[c]["ll_test"] for c in cand]), ntrain=a.ntrain, n_val=N_VAL)
        print(f"[fit] {p} Nr={Nr} {fam:<4} K={K:<2}: kappa {kb[0]:>3} restart {kb[1]} best@{f['it_best']:<3} train-val gap {f['ll_train'] - f['ll_val']:6.3f}   KL(true||fit) on the test set = "
              f"{ref['true_test'] - f['ll_test']:6.3f} nat   (Gaussian sample-cov prior: {ref['true_test'] - ref['gauss_test']:.3f});  pi_min = {f['pi'].min():.4f}", flush=True)
    print(f"[fit] finished in {(time.time() - t0) / 60:.1f} min -> {d_fits()}   (the analysis script prints the full table)")


def load_fits(prior, Nr, ntrain):
    out = {}
    for fam in FAM:
        for K in KS:
            fn = fit_file(prior, Nr, fam, K, ntrain)
            if not os.path.exists(fn): sys.exit(f"missing {fn}: run  python exp_0925_run.py fit  first")
            out[(fam, K)] = np.load(fn)
    return out


# ----------------------------------------------------------------------------- receivers
def make_arms(prior, Nr, T, Tp, sigma2, code, ntrain):
    true = angle_grid_prior(prior, Nr, NT, RHO_C, KG); fits = load_fits(prior, Nr, ntrain)
    gm = {K: GMMPriorB(Nr, NT, fits[("full", K)]["covs"], fits[("full", K)]["pi"]) for K in KS}; Cs = GaussianPrior(Nr, NT, fits[("full", 32)]["Chat"])   # same training set for every fit
    Kk = max(KS, key=lambda K: float(fits[("kron", K)]["ll_val"])); gk = GMMPriorB(Nr, NT, fits[("kron", Kk)]["covs"], fits[("kron", Kk)]["pi"])
    llv = {f"Hgmm-K{K}": float(fits[("full", K)]["ll_val"]) for K in KS}; llv["Hgmm-kron"] = float(fits[("kron", Kk)]["ll_val"])
    meta = dict(bstar=max(llv, key=llv.get), kron_K=Kk, **{f"ll_val|{k}": v for k, v in llv.items()})
    pil, Xp = make_pilots(prior, Tp); a = (Nr, NT, T, Tp, sigma2); v1 = dict(beta=0.7, feedback="posterior", Xp=Xp)
    site = dict(mode="colored", exact_prior=True, lam_min=LAM, **v1); shot = dict(mode="scalar", scal="belief", hsite="matrix", lam_min=LAM, **v1)
    arms = {"lmmseC_pf": RouteA(*a, Cs, code, mode="colored", **v1)}
    for K in KS: arms[f"Hgmm-K{K}"] = RouteA(*a, gm[K].view("eta"), code, **site)
    arms["Hgmm-kron"] = RouteA(*a, gk.view("eta"), code, **site)
    arms["Hscore-exact"] = RouteAClip(*a, true, code, clip="eta", **shot)
    arms["exactEP-true"] = RouteA(*a, true.view("eta"), code, **site)
    arms["Hscore-K32"] = RouteAClip(*a, gm[32], code, clip="eta", **shot)
    arms["Hgmm-K32-mp"] = RouteA(*a, gm[32].view("mean"), code, **site)
    arms["Hscore-exact-mp"] = RouteAClip(*a, true, code, clip="mean", **shot)
    arms["exactEP-true-mp"] = RouteA(*a, true.view("mean"), code, **site)
    arms["pilot_C"] = RouteA(*a, Cs, code, mode="pilot_only", beta=0.7, Xp=Xp)
    arms["pilot_Hgmm-K32"] = RouteA(*a, gm[32].view("eta"), code, mode="pilot_only", exact_prior=True, lam_min=LAM, beta=0.7, Xp=Xp)
    arms["genie"] = RouteA(*a, true, code, mode="genie", Xp=Xp)
    return true, arms, pil, v1, meta


def stats_obj(rx):
    return rx if isinstance(rx, RouteAClip) else rx.prior if (getattr(rx, "exact_prior", False) and hasattr(rx.prior, "reset_stats")) else None


def raw_file(cell, prior, pil, snr, skip, n):
    c = CELLS[cell]; return os.path.join(d_raw(), f"K_{cell}_{prior}_Nr{c['Nr']}_T{c['T']}_Tp{c['Tp']}_{pil}_snr{int(snr)}_skip{skip}_n{n}.npz")


def run_task(task):
    cell, prior, snr, skip, n, ntrain = task; c = CELLS[cell]; Nr, T, Tp = c["Nr"], c["T"], c["Tp"]
    out = raw_file(cell, prior, make_pilots(prior, Tp)[0], snr, skip, n)
    if os.path.exists(out): return f"exists  {os.path.basename(out)}"
    t0 = time.time(); code = QAMCode(GENS, NU, 2, NT * (T - Tp)); sigma2 = 10 ** (-snr / 10)
    true, arms, pil, v1, meta = make_arms(prior, Nr, T, Tp, sigma2, code, ntrain); first = arms["genie"]
    logs = {k: [] for k in list(arms) + ["oracle_pf"]}; clip = {k: [] for k, rx in arms.items() if stats_obj(rx) is not None}; comp = []
    rng = np.random.default_rng([SEED, PID[prior], Nr, T, int(snr) + 100])
    for tr in range(skip + n):
        H = true.sample(rng); k = true.last_k; u = rng.integers(0, 2, code.K); perm = rng.permutation(code.Ns)
        X, Y = first.transmit(u, perm, H, rng)
        if tr < skip: continue
        comp.append(k)
        for name, rx in arms.items():
            so = stats_obj(rx)
            if so is not None: so.reset_stats()
            logs[name].append(rx.run(Y, H, u, perm, N_ITER))
            if so is not None: clip[name].append((so.n_clip / max(so.n_site, 1), so.shift / max(so.n_clip, 1)))
        logs["oracle_pf"].append(RouteA(Nr, NT, T, Tp, sigma2, GaussianPrior(Nr, NT, true.covs[k]), code, mode="colored", **v1).run(Y, H, u, perm, N_ITER))
    flat = {f"{k}|{key}": np.array([l[key] for l in L]) for k, L in logs.items() for key in KEYS}
    flat.update({f"{k}|clip": np.array(v) for k, v in clip.items()}); flat["comp"] = np.array(comp); flat.update({f"meta|{k}": np.array(v) for k, v in meta.items()})
    os.makedirs(d_raw(), exist_ok=True); np.savez_compressed(out, **flat)
    bl = " ".join(f"{k}={np.mean([l['blk_err'][-1] for l in logs[k]]):.2f}" for k in ("lmmseC_pf", "Hgmm-K32", "Hgmm-kron", "Hscore-exact", "exactEP-true", "genie"))
    return f"done    {os.path.basename(out)}  ({time.time() - t0:.0f} s)  BLER16: {bl}"


def cmd_time(a):
    for cell in a.cells:
        c = CELLS[cell]; Nr, T, Tp = c["Nr"], c["T"], c["Tp"]; code = QAMCode(GENS, NU, 2, NT * (T - Tp)); rng = np.random.default_rng(1)
        t0 = time.time(); true, arms, pil, v1, meta = make_arms("S", Nr, T, Tp, 10 ** -0.6, code, a.ntrain); print(f"[{cell}] {Nr}x{NT} T={T} Tp={Tp}: build {time.time() - t0:.1f} s  meta {meta}"); tot = 0.0
        trials = []
        for _ in range(2):
            H = true.sample(rng); u = rng.integers(0, 2, code.K); perm = rng.permutation(code.Ns); trials.append((H, u, perm, arms["genie"].transmit(u, perm, H, rng)[1]))
        for name, rx in arms.items():
            t0 = time.time()
            for H, u, perm, Y in trials: rx.run(Y, H, u, perm, N_ITER)
            dt = (time.time() - t0) / 2; tot += dt; print(f"  [{cell}] {name:<18} {dt:6.2f} s/run")
        print(f"  [{cell}] total {tot:.1f} s/trial (+ oracle_pf ~ lmmseC_pf)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["prior", "fit", "time", "K"])
    ap.add_argument("--n", type=int, default=640); ap.add_argument("--chunk", type=int, default=40); ap.add_argument("--jobs", type=int, default=os.cpu_count())
    ap.add_argument("--cells", nargs="+", default=list(CELLS), choices=list(CELLS)); ap.add_argument("--priors", nargs="+", default=list(PID), choices=list(PID))
    ap.add_argument("--snr", type=float, nargs="+", default=None); ap.add_argument("--ntrain", type=int, default=10000)
    ap.add_argument("--restarts", type=int, default=3); ap.add_argument("--fit-iters", type=int, default=500); ap.add_argument("--tag", default="")
    a = ap.parse_args(); TAG = a.tag
    if a.cmd == "prior": cmd_prior(); sys.exit()
    if a.cmd == "fit": cmd_fit(a); sys.exit()
    if a.cmd == "time": cmd_time(a); sys.exit()
    pts = [(cell, p, float(s)) for cell in a.cells for p in a.priors for s in (a.snr or CELLS[cell]["snrs"])]
    for cell, p, _ in pts: load_fits(p, CELLS[cell]["Nr"], a.ntrain)                               # fail early if a fit is missing
    tasks = [pt + (s, min(a.chunk, a.n - s), a.ntrain) for pt in pts for s in range(0, a.n, a.chunk)]
    tasks.sort(key=lambda t: (t[3], -CELLS[t[0]]["Nr"]))                                           # first chunks of every point early; expensive cell first
    print(f"[K] {len(pts)} points x n={a.n} -> {len(tasks)} tasks on {a.jobs} workers", flush=True); t0 = time.time()
    if a.jobs <= 1:
        for i, t in enumerate(tasks): print(f"{i + 1}/{len(tasks)} {run_task(t)}", flush=True)
    else:
        import multiprocessing as mp
        with mp.Pool(a.jobs, initializer=_init, initargs=(TAG,)) as pool:
            for i, msg in enumerate(pool.imap_unordered(run_task, tasks)): print(f"{i + 1}/{len(tasks)} {msg}", flush=True)
    print(f"[K] finished in {(time.time() - t0) / 60:.1f} min -> now run: python exp_0925_analysis.py" + (f" --tag {TAG}" if TAG else ""))
