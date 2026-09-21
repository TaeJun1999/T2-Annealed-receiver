"""conf/code/diag_ep_site.py -- H4 diagnosis: is the COLLAPSE of M-ours-dscore in the wiring or the model?

Factorial: {Module-H denoiser} x {EP-site wiring}, everything else identical (same pilots, same
trial stream, same 16 iterations, same beta/loo/feedback).  Diagnostic only: nothing is retrained,
no threshold is touched, no pre-registered file is written.

  denoiser  gmmB   = the fitted D2 GMM b* (GMMPriorB): EXACT posterior mean + EXACT Wirtinger Jacobian
            dscore = the frozen checkpoint ckpt/d2sx_N10000_a1.pt (ScorePrior, one-shot Tweedie)
  wiring    epsite = mode='colored' + prior.ep_site  (the M-ours-bstar path; anisotropic-cavity mixture EP)
            scorew = mode='scalar', scal='belief', hsite='matrix', RouteAClip(clip='eta')   (the M-ours-dscore path)
            belsc  = mode='scalar', scal='belief', hsite='scalar'   (D-13 only, no D-14 matrix site)
            sitesc = mode='scalar', scal='site',   hsite='scalar'   (v0 SC-VAMP scalar path)

  gmmB x scorew  is the DECISIVE cell: exact denoiser, score wiring.
"""
import os, sys, time, json
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import arms as A
import runner as R

OUT = os.path.join(C.CONF, "results", "diag")
TAG = "ep-site-integration"


def build(cell, snr, testbed="D2", prior="S2", ckpt=None):
    c = C.CELLS[cell]
    Nr, Nt, T, Tp = c["Nr"], c["Nt"], c["T"], c["Tp"]
    sigma2 = 10 ** (-snr / 10)
    code = C.QAMCode(C.GENS, C.NU, C.M_QAM, Nt * (T - Tp))
    pil, Xp = C.make_pilots(testbed, prior, Nt, Tp, Nr)
    gen = C.make_gen(testbed, prior, Nr, Nt)
    hp, fits, llv, bstar, kron_K = A.module_h_priors(testbed, prior, Nr, Nt)
    Cs = C.GaussianPrior(Nr, Nt, fits[("full", 32)]["Chat"])
    sp, why = R.score_prior(testbed, prior, Nr, Nt, ckpt)
    assert sp is not None, why
    a = (Nr, Nt, T, Tp, sigma2)
    gm = hp[bstar]                                    # b* = the GMM the pre-registered M-ours-bstar uses

    rx = {}
    # --- controls: exactly the two pre-registered arms
    rx["gmmB|epsite"]   = A.route_a(*a, gm.view("eta"), code, Xp, "gmm_site")          # == M-ours-bstar
    rx["dscore|scorew"] = A.route_a(*a, sp,             code, Xp, "score", clip="eta") # == M-ours-dscore
    # --- THE HYBRID: exact GMM denoiser pushed through the score wiring
    rx["gmmB|scorew"]   = A.route_a(*a, gm,             code, Xp, "score", clip="eta")
    # --- wiring decomposition (D-13 alone, and the v0 scalar path) for both denoisers
    for nm, pr in (("gmmB", gm), ("dscore", sp)):
        rx[f"{nm}|belsc"]  = A.route_a(*a, pr, code, Xp, "score", clip="eta", hsite="scalar")
        rx[f"{nm}|sitesc"] = A.route_a(*a, pr, code, Xp, "score", clip="eta", scal="site", hsite="scalar")
    # --- anchor
    rx["gauss|sitesc"] = A.route_a(*a, Cs, code, Xp, "gaussian")                        # == R2-ours-G
    meta = dict(bstar=bstar, pil=pil, ckpt=str(getattr(sp, "ckpt", "?")), why=why,
                cfg={k: {q: (str(v.cfg_dump.get(q))) for q in
                         ("mode", "scal", "hsite", "lam_min", "exact_prior", "clip", "class_", "beta", "loo", "feedback")}
                     for k, v in rx.items()})
    return rx, gen, code, Nr, Nt, T, Tp, meta


def run_point(cell, snr, n, iters=C.N_ITER, testbed="D2", prior="S2", ckpt=None):
    rx, gen, code, Nr, Nt, T, Tp, meta = build(cell, snr, testbed, prior, ckpt)
    first = rx["gauss|sitesc"]
    logs = {k: [] for k in rx}
    fail = {k: 0 for k in rx}
    clip = {k: [] for k in rx}
    rng = C.trial_rng(testbed, prior, Nr, T, Tp, snr)
    t0 = time.time()
    for tr in range(n):
        H = gen.sample(rng)
        u = rng.integers(0, 2, code.K)
        perm = rng.permutation(code.Ns)
        X, Y = first.transmit(u, perm, H, rng)
        for k, r in rx.items():
            so = R.stats_obj(r)
            if so is not None:
                so.reset_stats()
            try:
                logs[k].append(r.run(Y, H, u, perm, iters))
            except Exception as ex:                         # classify, never drop
                fail[k] += 1
                logs[k].append({q: np.full(iters, np.nan) for q in C.KEYS_LOG})
            if so is not None:
                clip[k].append((so.n_clip / max(so.n_site, 1), so.shift / max(so.n_clip, 1)))
    out = {}
    for k, L in logs.items():
        for q in ("blk_err", "ber", "nmse", "nuE", "nu_q", "alphaH", "hE_norm", "tauL_gmean"):
            out[f"{k}|{q}"] = np.array([l[q] for l in L])
        out[f"{k}|failed"] = np.array([fail[k]])
        if clip[k]:
            out[f"{k}|clip"] = np.array(clip[k])
    out["meta|json"] = np.array(json.dumps(meta))
    out["run|snr"] = snr; out["run|n"] = n; out["run|iters"] = iters; out["run|cell"] = cell
    p = os.path.join(OUT, f"{TAG}_{testbed}_{cell}_snr{int(snr):+d}_n{n}.npz")
    np.savez_compressed(p, **out)
    print(f"# saved {p}   ({time.time()-t0:.0f} s)")
    return out, meta


def table(out, snr, n):
    ks = [k for k in out if k.endswith("|blk_err")]
    print(f"\n--- SNR {snr:+.0f} dB, n={n} ---")
    print(f"{'arm (denoiser|wiring)':<22} {'BLER@1':>7} {'BLER@2':>7} {'BLER@16':>8} {'BER@16':>8} "
          f"{'NMSE med@1':>11} {'NMSE med@16':>12} {'NMSE mean@16':>13} {'frac NMSE>1':>12} {'nuE@16 med':>11} {'clip%':>6} {'clipshift':>10} {'raised':>7}")
    for kk in ks:
        k = kk[:-len("|blk_err")]
        be = out[f"{k}|blk_err"]; nm = out[f"{k}|nmse"]; nu = out[f"{k}|nuE"]
        cl = out.get(f"{k}|clip")
        print(f"{k:<22} {np.nanmean(be[:,0]):7.3f} {np.nanmean(be[:,1]):7.3f} {np.nanmean(be[:,-1]):8.3f} "
              f"{np.nanmean(out[f'{k}|ber'][:,-1]):8.3f} {np.nanmedian(nm[:,0]):11.4f} {np.nanmedian(nm[:,-1]):12.4f} "
              f"{np.nanmean(nm[:,-1]):13.4f} {np.nanmean(nm[:,-1] > 1.0):12.3f} {np.nanmedian(nu[:,-1]):11.3e} "
              f"{(100*np.mean([c[0] for c in cl]) if cl is not None else float('nan')):6.1f} "
              f"{(np.nanmean([c[1] for c in cl]) if cl is not None else float('nan')):10.3e} {int(out[f'{k}|failed'][0]):7d}")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", default="C2"); ap.add_argument("--snrs", type=float, nargs="+", default=[0.0])
    ap.add_argument("--n", type=int, default=128); ap.add_argument("--iters", type=int, default=C.N_ITER)
    ap.add_argument("--ckpt", default=None)
    a = ap.parse_args()
    print(C.header("D2", [f"DIAGNOSTIC {TAG}: Module-H denoiser x EP-site wiring factorial (H4). No retraining, no tuning."]))
    for s in a.snrs:
        out, meta = run_point(a.cell, s, a.n, a.iters, ckpt=a.ckpt)
        print("# b* =", meta["bstar"], " pilots =", meta["pil"], " ckpt =", meta["ckpt"])
        table(out, s, a.n)
