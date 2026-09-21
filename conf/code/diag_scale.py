"""conf/code/diag_scale.py -- H3 diagnostic: normalisation / scale mismatch between the data the
diffusion model was TRAINED on and what the RouteA receiver feeds it at inference.

REPORT ONLY.  Nothing here retrains, tunes or re-gates anything; the checkpoint is fixed.
Writes conf/results/diag/scale-mismatch_D2_C2.txt (+ .npz).

Parts
  A  normalisation + vec-convention audit  (training set vs receiver path vs model's internal reshape)
  B  sigma-argument sweep: noise added at a KNOWN nu, denoiser evaluated at c*sqrt(nu/2) -- the sqrt(2) test
  C  vec-permutation test: what a column-major/row-major mix-up would cost
  D  receiver-convention denoiser + Wirtinger site at the MEASURED C2 operating nu_q
  E  the live loop: what q, nu_q and ||q||^2/N actually are inside M-ours-dscore at C2 6 dB
"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import torch

import common as C
import arms as A
import score as S
import sigma as SG

torch.set_num_threads(4)
OUT = os.path.join(C.CONF, "results", "diag")
os.makedirs(OUT, exist_ok=True)
CK = os.path.join(C.CONF, "ckpt", "d2sx_N10000_a1.pt")
NR, NT, PRIOR, N = 8, 4, "S2", 32
REC = []                                          # report lines


def say(*a):
    s = " ".join(str(x) for x in a)
    REC.append(s)
    print(s, flush=True)


# --------------------------------------------------------------------------------- A: normalisation audit
def part_A(gen, Xtr):
    say("\n" + "=" * 100)
    say("A. NORMALISATION + VEC CONVENTION AUDIT")
    say("=" * 100)
    p_tr = float(np.mean(np.sum(np.abs(Xtr) ** 2, 1))) / N
    say(f"  training set (arms.training_set -> score.training_split), n={len(Xtr)}")
    say(f"    E||h||^2 / N                 = {p_tr:.6f}     (training_split ASSERTS |.-1| < 0.05)")
    say(f"    E|h_i|^2 per-entry min/max   = {np.mean(np.abs(Xtr)**2,0).min():.4f} / "
        f"{np.mean(np.abs(Xtr)**2,0).max():.4f}")

    # the receiver's own path: runner._run_point does H = gen.sample(rng), RouteA.run does reshape(order='F')
    rng = C.trial_rng("D2", PRIOR, NR, 16, 4, 6.0)
    Hs = np.stack([gen.sample(rng) for _ in range(2000)])
    hv = Hs.reshape(len(Hs), -1, order="C")                       # NOT the receiver's convention
    hF = Hs.transpose(0, 2, 1).reshape(len(Hs), N)                # == H.reshape(-1, order='F'), receiver
    p_rx = float(np.mean(np.sum(np.abs(hF) ** 2, 1))) / N
    say(f"  receiver path (runner: H = gen.sample(rng); RouteA.run: h = H.reshape(-1, order='F')), n=2000")
    say(f"    E||h||^2 / N                 = {p_rx:.6f}")
    say(f"    ratio receiver/training      = {p_rx / p_tr:.6f}      <-- 1.0 means NO scale mismatch")

    # same rng stream, element-for-element: does sample_vecs equal vec(sample) column-major?
    r1 = C.train_rng("D2", PRIOR, NR, 7); r2 = C.train_rng("D2", PRIOR, NR, 7)
    v = gen.sample_vecs(r1, 1)[0]
    # sample_vecs draws n at once, sample draws 1 -- same _draw call shape for n=1, so streams agree
    h1 = gen.sample(r2).reshape(-1, order="F")
    say(f"    max|sample_vecs - vec(sample,'F')| = {np.max(np.abs(v - h1)):.3e}   "
        f"(vs row-major: {np.max(np.abs(v - gen.sample(C.train_rng('D2', PRIOR, NR, 7)).reshape(-1))):.3e})")

    # model's internal reshape: push a one-hot through the (2,Nt,Nr)->transpose path of arch_dit / _Conv
    z = np.zeros(N, complex); z[1 + NR * 2] = 1.0                 # h[i+Nr*j] with i=1, j=2  ->  H[1,2]
    x = torch.as_tensor(S.np_pack(z), dtype=torch.float64)
    y = x.reshape(-1, 2, NT, NR).transpose(-1, -2)                # what DiT.forward does
    ij = np.argwhere(y[0, 0].numpy() != 0)
    say(f"    model internal reshape of h[1+Nr*2] lands at (i,j) = {tuple(ij[0])}   (must be (1, 2))")
    return p_tr, p_rx


# --------------------------------------------------------------------------------- B: the sqrt(2) test
CS = np.array([0.5, 1 / np.sqrt(2), 0.85, 1.0, 1.18, np.sqrt(2), 2.0])


def _tweedie(model, Q, sig):
    X = torch.as_tensor(S.np_pack(Q), dtype=torch.float64)
    with torch.no_grad():
        m = S.tweedie_real(model, X, torch.full((len(X),), float(sig), dtype=X.dtype))
    return S.np_unpack(m.numpy())


def part_B(model, gmm, H, E, nus):
    say("\n" + "=" * 100)
    say("B. SIGMA-ARGUMENT SWEEP -- noise added at a KNOWN nu, denoiser asked for c*sqrt(nu/2)")
    say("   c = 1.0 is the project convention sigma_t = sqrt(nu/2).  A sqrt(2) bug shows as argmin c != 1.")
    say("=" * 100)
    p_h = float(np.mean(np.sum(np.abs(H) ** 2, 1)))
    say(f"   n_eval = {len(H)}   NMSE = E||m - h||^2 / E||h||^2 ;  c* = argmin over the c grid")
    say("   c grid: " + "  ".join(f"{c:.4f}" for c in CS))
    out = {}
    say(f"\n   {'nu':>10} {'sigma_t':>10} | " + " ".join(f"{'c=' + f'{c:.3f}':>10}" for c in CS)
        + f" | {'c*_diff':>8} {'c*_gmm':>8}")
    for nu in nus:
        Q = H + np.sqrt(nu) * E
        nm_d, nm_g = [], []
        for c in CS:
            sg = c * np.sqrt(nu / 2.0)
            m = _tweedie(model, Q, sg)
            nm_d.append(float(np.mean(np.sum(np.abs(m - H) ** 2, 1))) / p_h)
            nu_a = 2.0 * sg ** 2                                   # the GMM takes nu directly
            mg = np.stack([gmm.denoise(Q[i], nu_a)[0] for i in range(len(Q))])
            nm_g.append(float(np.mean(np.sum(np.abs(mg - H) ** 2, 1))) / p_h)
        nm_d, nm_g = np.array(nm_d), np.array(nm_g)
        out[float(nu)] = (nm_d, nm_g)
        say(f"   {nu:10.3e} {np.sqrt(nu/2):10.3e} | " + " ".join(f"{v:10.4e}" for v in nm_d)
            + f" | {CS[nm_d.argmin()]:8.4f} {CS[nm_g.argmin()]:8.4f}")
        say(f"   {'(gmm)':>10} {'':>10} | " + " ".join(f"{v:10.4e}" for v in nm_g))
    return out


# --------------------------------------------------------------------------------- C: vec permutation
def part_C(model, gmm, H, E, nus):
    say("\n" + "=" * 100)
    say("C. VEC-CONVENTION TEST -- h[i + Nr*j] (column-major, correct) vs h[j + Nt*i] (row-major)")
    say("=" * 100)
    P = np.arange(N).reshape(NR, NT).T.reshape(-1)                 # row-major reader's index order
    p_h = float(np.mean(np.sum(np.abs(H) ** 2, 1)))
    say(f"   {'nu':>10} | {'NMSE colmajor':>14} {'NMSE rowmajor':>14} {'ratio':>8} | "
        f"{'gmm colmaj':>11} {'gmm rowmaj':>11}")
    rows = []
    for nu in nus:
        Q = H + np.sqrt(nu) * E
        sg = np.sqrt(nu / 2)
        a = float(np.mean(np.sum(np.abs(_tweedie(model, Q, sg) - H) ** 2, 1))) / p_h
        b = float(np.mean(np.sum(np.abs(_tweedie(model, Q[:, P], sg)[:, np.argsort(P)] - H) ** 2, 1))) / p_h
        ga = float(np.mean([np.sum(np.abs(gmm.denoise(Q[i], nu)[0] - H[i]) ** 2) for i in range(len(Q))])) / p_h
        gb = float(np.mean([np.sum(np.abs(gmm.denoise(Q[i][P], nu)[0][np.argsort(P)] - H[i]) ** 2)
                            for i in range(len(Q))])) / p_h
        say(f"   {nu:10.3e} | {a:14.5e} {b:14.5e} {b/a:8.3f} | {ga:11.4e} {gb:11.4e}")
        rows.append((nu, a, b, ga, gb))
    return np.array(rows)


# --------------------------------------------------------------------------------- D: receiver-side site
def part_D(sp, gmm, H, E, nus):
    say("\n" + "=" * 100)
    say("D. RECEIVER CONVENTION -- ScorePrior.denoise / denoise_full at the MEASURED C2 operating nu_q,")
    say("   on q = h + CN(0, nu I) (the ideal cavity the loop's SC-VAMP step pretends to produce).")
    say("=" * 100)
    n = min(len(H), 128)
    say(f"   n = {n} ;  alpha = tr(J)/N (the scalar the loop uses) ;  SigH = nu*J is what D-14 INVERTS")
    say(f"   {'nu':>10} | {'nmse_d':>9} {'nmse_g':>9} | {'alpha_d':>8} {'alpha_g':>8} {'alpha_id':>8} | "
        f"{'eig(SigH)min':>12} {'eig(SigH)max':>12} | {'clipfrac':>8} {'lam_min_eig':>12}")
    rows = []
    for nu in nus:
        nmd = nmg = ad = ag = 0.0
        emin, emax, nclip, lmin = np.inf, -np.inf, 0, np.inf
        for i in range(n):
            q = H[i] + np.sqrt(nu) * E[i]
            m, J = sp.denoise_full(q, nu)
            nmd += np.sum(np.abs(m - H[i]) ** 2); ad += float(np.trace(J).real / N)
            mg, agi = gmm.denoise(q, nu)
            nmg += np.sum(np.abs(mg - H[i]) ** 2); ag += agi
            SigH = nu * J; SigH = 0.5 * (SigH + SigH.conj().T)
            w = np.linalg.eigvalsh(SigH)
            emin, emax = min(emin, w.min()), max(emax, w.max())
            Lam = np.linalg.inv(SigH) - np.eye(N) / nu
            wl = np.linalg.eigvalsh(0.5 * (Lam + Lam.conj().T))
            lmin = min(lmin, wl.min()); nclip += int(wl.min() < C.LAM_MIN)
        ph = float(np.sum(np.abs(H[:n]) ** 2))
        r = (nu, nmd / ph, nmg / ph, ad / n, ag / n, nu / (nu + 1.0), emin, emax, nclip / n, lmin)
        say(f"   {nu:10.3e} | {r[1]:9.3e} {r[2]:9.3e} | {r[3]:8.4f} {r[4]:8.4f} {r[5]:8.4f} | "
            f"{emin:12.4e} {emax:12.4e} | {nclip/n:8.3f} {lmin:12.4e}")
        rows.append(r)
    say("   alpha_id = nu/(nu+1) is the alpha a WHITE UNIT-POWER Gaussian prior would give -- a scale ruler,")
    say("   not a target.  alpha << that means a much more confident prior; alpha > 1 or < 0 is nonsense.")
    return np.array(rows)


# --------------------------------------------------------------------------------- E: the live loop
def part_E(snrs=(6.0,), n_tr=4, iters=16):
    say("\n" + "=" * 100)
    say("E. THE LIVE LOOP -- what M-ours-dscore actually hands the network at C2 (8x4, T=16, Tp=4)")
    say("=" * 100)
    import runner as R
    out = {}
    for snr in snrs:
        P = R.build_point("D2", "C2", PRIOR, snr, ckpt=CK)
        rx = P["arms"].get("M-ours-dscore")
        if rx is None:
            say(f"   snr {snr}: M-ours-dscore ABSENT ({P['dscore']})"); continue
        gen, code = P["gen"], P["code"]
        sp = rx.prior
        tap = []
        orig = sp.denoise_full

        def patched(q, nu, _o=orig, _t=tap):
            m, J = _o(q, nu)
            _t.append((float(nu), float(np.sum(np.abs(q) ** 2) / N), float(np.sum(np.abs(m) ** 2) / N),
                       float(np.trace(J).real / N)))
            return m, J
        sp.denoise_full = patched
        sp.denoise = lambda q, nu, _p=patched: (lambda mj: (mj[0], float(np.trace(mj[1]).real / N)))(_p(q, nu))

        rng = C.trial_rng("D2", PRIOR, P["Nr"], P["T"], P["Tp"], snr)
        first = P["arms"]["R5-genie"]
        nms, qn = [], []
        for tr in range(n_tr):
            Hc = gen.sample(rng); u = rng.integers(0, 2, code.K); perm = rng.permutation(code.Ns)
            X, Y = first.transmit(u, perm, Hc, rng)
            tap.clear()
            lg = rx.run(Y, Hc, u, perm, iters)
            nms.append(lg["nmse"]); qn.append(np.array(tap))
        nms = np.array(nms); Q = np.stack([q[:iters] for q in qn if len(q) >= iters])
        say(f"\n   snr {snr:g} dB, {n_tr} trials, E|h_i|^2 = 1 by construction")
        say(f"   {'it':>3} {'nu_q':>11} {'|q|^2/N':>11} {'1+nu_q':>11} {'ratio':>7} "
            f"{'|m|^2/N':>11} {'alpha':>8} {'nmse':>10}")
        for t in range(iters):
            nu = np.nanmean(Q[:, t, 0]); q2 = np.nanmean(Q[:, t, 1]); m2 = np.nanmean(Q[:, t, 2])
            al = np.nanmean(Q[:, t, 3]); nm = np.nanmean(nms[:, t])
            say(f"   {t+1:>3} {nu:11.4e} {q2:11.4e} {1+nu:11.4e} {q2/(1+nu):7.3f} "
                f"{m2:11.4e} {al:8.4f} {nm:10.4e}")
        say(f"   query stats: {sp.query_stats()}")
        out[snr] = Q
    return out


def main():
    t0 = time.time()
    say(C.header("D2", extra=[
        "content     : H3 diagnostic -- training/inference normalisation + sigma convention + vec order",
        f"checkpoint  : {CK}",
        f"cell        : C2 (Nr={NR}, Nt={NT}, T=16, Tp=4), prior {PRIOR}",
        "status      : REPORT ONLY.  Nothing retrained, nothing tuned, no gate threshold touched."]))

    gen = C.make_gen("D2", PRIOR, NR, NT)
    Xtr = A.training_set("D2", PRIOR, NR, NT)
    p_tr, p_rx = part_A(gen, Xtr)

    model, st = S.load_model(CK, NR, NT, device="cpu")
    say(f"\n  checkpoint hp = {st['hp']}\n  trained on testbed={st['testbed']} prior={st['prior']} "
        f"Nr={st['Nr']} Nt={st['Nt']} split_hash={st['split_hash']}")

    fits, llv, bstar, kron_K = A.gmm_selection("D2", PRIOR, NR)
    fam, K = ("kron", kron_K) if bstar == "kron" else ("full", int(bstar[3:]))
    gmm = C.GMMPriorB(NR, NT, fits[(fam, K)]["covs"], fits[(fam, K)]["pi"])
    say(f"  GMM b* = {bstar} ({fam} K={K})")

    # HELD-OUT samples: stream 10 is the one gb_prime uses, and it is not the training stream (7).
    n_eval = 512
    H = gen.sample_vecs(C.train_rng("D2", PRIOR, NR, 10), n_eval)
    nrng = np.random.default_rng(S.SEED_GATE)
    E = (nrng.standard_normal((n_eval, N)) + 1j * nrng.standard_normal((n_eval, N))) / np.sqrt(2)

    # the nu the receiver ACTUALLY queries at C2 (results/sigma_grid_D2.txt, median nu_q per iteration)
    nus = [2.318e-03, 9.0e-03, 1.837e-02, 3.585e-02, 7.05e-02, 1.46e-01, 4.988e-01]
    B = part_B(model, gmm, H, E, nus)
    Cc = part_C(model, gmm, H, E, nus)
    sp = S.ScorePrior(CK, NR, NT, fits[("full", 32)]["Chat"], device="cpu")
    D = part_D(sp, gmm, H[:128], E[:128], nus)
    Ee = part_E()

    say(f"\n# wall {time.time() - t0:.1f} s")
    with open(os.path.join(OUT, "scale-mismatch_D2_C2.txt"), "w") as f:
        f.write("\n".join(REC) + "\n")
    np.savez_compressed(os.path.join(OUT, "scale-mismatch_D2_C2.npz"),
                        c_grid=CS, nus=np.array(nus), p_train=p_tr, p_rx=p_rx,
                        B_diff=np.stack([B[n][0] for n in B]), B_gmm=np.stack([B[n][1] for n in B]),
                        C_perm=Cc, D_site=D,
                        **{f"E_snr{int(k)}": v for k, v in Ee.items()})
    print("\nwrote", os.path.join(OUT, "scale-mismatch_D2_C2.txt"))


if __name__ == "__main__":
    main()
