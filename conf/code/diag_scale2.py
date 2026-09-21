"""conf/code/diag_scale2.py -- H3 follow-up.  Two things diag_scale.py left open:

  F  Is nu*J a valid conditional covariance?  The diffusion's Wirtinger Jacobian vs the GMM's EXACT one,
     on the SAME q at the SAME nu.  (GMMPriorB.denoise_full is a closed-form posterior covariance, so its
     nu*J is PSD by construction and is the right ruler.)
  E2 The live loop, de-duplicated (diag_scale.py's tap fired twice per iteration: once from denoise(),
     once from _matrix_site()->denoise_full()), 8 trials, and with the CONTROL arm that separates
     "the prior is wrong" from "the D-13/D-14 interface is wrong":

       M-ours-dscore   diffusion prior  THROUGH the score interface   (scal=belief, hsite=matrix)
       X-gmm-score     GMM b* prior     THROUGH THE SAME score interface   <-- control, diagnostic only
       M-ours-bstar    GMM b* prior     through the mixture-EP interface   (scal=site, hsite=scalar)

REPORT ONLY.  X-gmm-score is a DIAGNOSTIC arm: it is not pre-registered and appears in no BLER table.
"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import torch

import common as C
import arms as A
import score as S
import runner as R

torch.set_num_threads(4)
OUT = os.path.join(C.CONF, "results", "diag")
os.makedirs(OUT, exist_ok=True)
CK = os.path.join(C.CONF, "ckpt", "d2sx_N10000_a1.pt")
NR, NT, PRIOR, N = 8, 4, "S2", 32
REC = []


def say(*a):
    s = " ".join(str(x) for x in a)
    REC.append(s); print(s, flush=True)


def eigstats(M):
    M = 0.5 * (M + M.conj().T)
    return np.linalg.eigvalsh(M)


# ------------------------------------------------------------------ F: is nu*J a covariance?
def part_F(sp, gmm, H, E, nus, n=96):
    say("\n" + "=" * 108)
    say("F. IS  SigH = nu*J  A VALID CONDITIONAL COVARIANCE?   (D-14 inverts it; RouteAClip._matrix_site)")
    say("   Cov[h|q] must be Hermitian PSD.  The GMM's denoise_full returns the exact one -> the ruler.")
    say("=" * 108)
    say(f"   n = {n} draws of q = h + CN(0, nu I) ;  herm = max |SigH - SigH^H| / max|SigH| BEFORE symmetrising")
    say(f"\n   {'nu':>10} | {'src':>5} | {'herm':>9} {'eig_min':>11} {'eig_max':>11} {'cond':>10} | "
        f"{'frac neg-def':>12} {'frac lam<floor':>14} | {'|Lam|_2 med':>12}")
    rows = []
    for nu in nus:
        for src in ("diff", "gmm"):
            hm = []; emin = []; emax = []; cnd = []; nneg = 0; nclip = 0; l2 = []
            for i in range(n):
                q = H[i] + np.sqrt(nu) * E[i]
                if src == "diff":
                    # the RAW (unsymmetrised) J, exactly as ScorePrior._eval computes it before its own
                    # 0.5*(J+J^H); the herm number below is what that symmetrisation hides.
                    x = torch.as_tensor(S.np_pack(q), dtype=torch.float64)
                    sg = torch.as_tensor(float(S.NU_TO_SIGMA(nu)), dtype=torch.float64)
                    Jw = S.wirtinger(torch.func.jacrev(lambda v: S.tweedie_real(sp.model, v, sg))(x)).numpy()
                else:
                    _, Jw = gmm.denoise_full(q, nu)
                Sg = nu * Jw
                hm.append(np.max(np.abs(Sg - Sg.conj().T)) / max(np.max(np.abs(Sg)), 1e-300))
                w = eigstats(Sg)
                emin.append(w.min()); emax.append(w.max()); cnd.append(abs(w.max() / w.min()) if w.min() else np.inf)
                nneg += int(w.min() < 0)
                Lam = np.linalg.inv(0.5 * (Sg + Sg.conj().T)) - np.eye(N) / nu
                wl = eigstats(Lam)
                nclip += int(wl.min() < C.LAM_MIN)
                l2.append(np.max(np.abs(wl)))
            r = (nu, src, np.median(hm), np.median(emin), np.median(emax), np.median(cnd),
                 nneg / n, nclip / n, np.median(l2))
            say(f"   {nu:10.3e} | {src:>5} | {r[2]:9.3e} {r[3]:11.3e} {r[4]:11.3e} {r[5]:10.3e} | "
                f"{r[6]:12.3f} {r[7]:14.3f} | {r[8]:12.3e}")
            rows.append(r)
    say("   'frac neg-def'   = share of draws whose nu*J has a NEGATIVE eigenvalue (not a covariance).")
    say("   'frac lam<floor' = share of draws where D-14's site Lambda hits the lam_min = 1e-6 eigenvalue")
    say("                      clip, i.e. RouteAClip fabricates the site instead of using the model's.")
    return rows


# ------------------------------------------------------------------ E2: the live loop + control arm
def build_arms(snr):
    P = R.build_point("D2", "C2", PRIOR, snr, ckpt=CK)
    fits, llv, bstar, kron_K = A.gmm_selection("D2", PRIOR, NR)
    fam, K = ("kron", kron_K) if bstar == "kron" else ("full", int(bstar[3:]))
    gmm = C.GMMPriorB(NR, NT, fits[(fam, K)]["covs"], fits[(fam, K)]["pi"])
    a = (NR, NT, P["T"], P["Tp"], P["sigma2"])
    # CONTROL: the SAME GMM b* prior pushed through the SAME D-13 belief + D-14 matrix-site interface
    # the diffusion arm uses.  Diagnostic only -- not an arm, not in any table.
    P["arms"]["X-gmm-score"] = A.route_a(*a, gmm, P["code"], P["Xp"], "score", clip="eta")
    return P, gmm


def part_E2(snrs=(6.0, 0.0), n_tr=8, iters=16):
    say("\n" + "=" * 108)
    say("E2. THE LIVE LOOP at C2 (8x4, T=16, Tp=4) -- de-duplicated tap, one row per OUTER ITERATION")
    say("=" * 108)
    store = {}
    for snr in snrs:
        P, gmm = build_arms(snr)
        names = ["M-ours-dscore", "X-gmm-score", "M-ours-bstar", "R2-ours-G"]
        names = [n for n in names if n in P["arms"]]
        say(f"\n   --- snr {snr:g} dB, {n_tr} trials, sigma2 = {P['sigma2']:.4g}, arms: {names}")
        taps = {}
        for nm in ("M-ours-dscore", "X-gmm-score"):
            if nm not in P["arms"]:
                continue
            rx = P["arms"][nm]; pr = rx.prior; t = []; taps[nm] = t
            orig = pr.denoise_full

            def mk(_o, _t, _pr):
                def f(q, nu):
                    m, J = _o(q, nu)
                    Sg = nu * 0.5 * (J + J.conj().T)
                    w = np.linalg.eigvalsh(Sg)
                    _t.append((float(nu), float(np.sum(np.abs(q) ** 2) / N),
                               float(np.sum(np.abs(m) ** 2) / N), float(np.trace(J).real / N),
                               float(w.min()), float(w.max())))
                    return m, J
                return f
            pr.denoise_full = mk(orig, t, pr)      # only denoise_full is tapped: denoise() hits the cache

        gen, code = P["gen"], P["code"]
        rng = C.trial_rng("D2", PRIOR, NR, P["T"], P["Tp"], snr)
        first = P["arms"]["R5-genie"]
        nms = {nm: [] for nm in names}; bler = {nm: [] for nm in names}
        tp = {nm: [] for nm in taps}
        for tr in range(n_tr):
            Hc = gen.sample(rng); u = rng.integers(0, 2, code.K); perm = rng.permutation(code.Ns)
            X, Y = first.transmit(u, perm, Hc, rng)
            for nm in names:
                if nm in taps:
                    taps[nm].clear()
                lg = P["arms"][nm].run(Y, Hc, u, perm, iters)
                nms[nm].append(lg["nmse"]); bler[nm].append(lg["blk_err"])
                if nm in taps:
                    tp[nm].append(np.array(taps[nm][:iters]))
        say(f"   {'it':>3} | " + " | ".join(f"{nm[:13]:>13}" for nm in names) + "   (median NMSE over trials)")
        Nm = {nm: np.array(nms[nm]) for nm in names}
        for t in range(iters):
            say(f"   {t+1:>3} | " + " | ".join(f"{np.nanmedian(Nm[nm][:, t]):13.4e}" for nm in names))
        say(f"   {'BLER':>3} | " + " | ".join(f"{np.nanmean(np.array(bler[nm])[:, -1]):13.4f}" for nm in names))

        for nm, L in tp.items():
            L = [x for x in L if len(x) == iters]
            if not L:
                continue
            Q = np.stack(L)
            say(f"\n   {nm} denoiser tap (mean over {len(L)} trials)")
            say(f"   {'it':>3} {'nu_q':>11} {'|q|^2/N':>10} {'1+nu_q':>10} {'ratio':>7} {'|m|^2/N':>10} "
                f"{'alpha':>8} {'eig(nuJ)min':>12} {'eig(nuJ)max':>12}")
            for t in range(iters):
                v = np.nanmean(Q[:, t, :], 0)
                say(f"   {t+1:>3} {v[0]:11.4e} {v[1]:10.4e} {1+v[0]:10.4e} {v[1]/(1+v[0]):7.3f} "
                    f"{v[2]:10.4e} {v[3]:8.4f} {v[4]:12.4e} {v[5]:12.4e}")
            store[f"tap_{nm}_snr{int(snr)}"] = Q
        for nm in names:
            store[f"nmse_{nm}_snr{int(snr)}"] = Nm[nm]
    return store


def main():
    t0 = time.time()
    say(C.header("D2", extra=[
        "content     : H3 follow-up -- validity of SigH = nu*J, and the D-13/D-14 interface isolated",
        f"checkpoint  : {CK}",
        f"cell        : C2 (Nr={NR}, Nt={NT}, T=16, Tp=4), prior {PRIOR}",
        "status      : REPORT ONLY.  Nothing retrained, nothing tuned, no gate threshold touched.",
        "X-gmm-score : DIAGNOSTIC control arm (GMM b* through the score interface).  Not pre-registered."]))
    gen = C.make_gen("D2", PRIOR, NR, NT)
    fits, llv, bstar, kron_K = A.gmm_selection("D2", PRIOR, NR)
    fam, K = ("kron", kron_K) if bstar == "kron" else ("full", int(bstar[3:]))
    gmm = C.GMMPriorB(NR, NT, fits[(fam, K)]["covs"], fits[(fam, K)]["pi"])
    sp = S.ScorePrior(CK, NR, NT, fits[("full", 32)]["Chat"], device="cpu")
    say(f"# GMM b* = {bstar} ({fam} K={K})")

    n_eval = 96
    H = gen.sample_vecs(C.train_rng("D2", PRIOR, NR, 10), n_eval)
    nrng = np.random.default_rng(S.SEED_GATE)
    E = (nrng.standard_normal((n_eval, N)) + 1j * nrng.standard_normal((n_eval, N))) / np.sqrt(2)
    nus = [2.318e-03, 1.837e-02, 7.05e-02, 4.988e-01]
    F = part_F(sp, gmm, H, E, nus, n=n_eval)
    st = part_E2()

    say(f"\n# wall {time.time() - t0:.1f} s")
    with open(os.path.join(OUT, "scale-mismatch_D2_jacobian.txt"), "w") as f:
        f.write("\n".join(REC) + "\n")
    np.savez_compressed(os.path.join(OUT, "scale-mismatch_D2_jacobian.npz"),
                        F=np.array([[r[0]] + [np.nan if r[1] == "gmm" else 1.0] + list(r[2:]) for r in F]),
                        **st)
    print("\nwrote", os.path.join(OUT, "scale-mismatch_D2_jacobian.txt"))


if __name__ == "__main__":
    main()
