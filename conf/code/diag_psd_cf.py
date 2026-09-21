"""conf/code/diag_psd_cf.py -- INTERVENTIONAL test of the claim
    "the learned denoiser's Jacobian is not a valid covariance (indefinite), the D-14 site
     RouteAClip builds from it is therefore a mismatched (precision, mean) pair, and the loop diverges."

The claim was supported by CORRELATION only (bad Jacobian upstream + bad BLER downstream).  This script
runs the two do()-interventions that separate cause from correlate, both on the FROZEN checkpoint, with
the D-13 scalarisation left EXACTLY as the pre-registered arm sees it (prior.denoise untouched), so the
ONLY thing that changes is the Wirtinger Jacobian that feeds _matrix_site (D-14):

  (a) REMOVE the defect from the broken arm.  dscore|psd*: eigenvalues of Herm(J) clipped into
      [delta, 1], which makes SigH = nu J PD *and* Lam = SigH^-1 - I/nu PSD by construction, so the
      lam_min floor never fires and (Lam, eta) describe the same Gaussian.  If the claim is right,
      BLER must recover.
      dscore|mean: clip='mean' (already in Demo/t2_gmm.py, no new knob) -- repairs ONLY the
      (precision, mean) mismatch the claim names, leaving the indefinite inverse inside Lam's magnitude.
  (b) INJECT the defect into the working arm.  gmmB|flipM: the EXACT GMM denoiser (whose J is PSD to
      machine precision) pushed through the same score wiring, with the sign of its M smallest
      eigenvalues flipped.  tr(J) -- hence alphaH -- barely moves, so this adds indefiniteness and
      nothing else.  If indefiniteness is SUFFICIENT, the GMM arm must now collapse too.

Diagnostic only: nothing retrained, no pre-registered file written, no arm's own configuration changed.
"""
import os, sys, time, json
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import arms as A
import runner as R

OUT = os.path.join(C.CONF, "results", "diag")
TAG = "jacpsd-counterfactual"


class JFix:
    """Wraps a Module-H prior and rewrites ONLY the Jacobian returned by denoise_full (the D-14 path).
    denoise() -- the D-13 belief scalarisation alphaH = tr(J)/N -- is delegated untouched, so any BLER
    change is attributable to the matrix site alone."""

    def __init__(self, inner, mode, delta=1e-2, mflip=1):
        self.inner, self.mode, self.delta, self.mflip = inner, mode, float(delta), int(mflip)
        self.n_neg_in = self.n_call = 0

    def __getattr__(self, k):                      # cbar, eh2_prior, C, Cinv, ep_site, view, ckpt, ...
        return getattr(self.__dict__["inner"], k)

    def denoise(self, q, nu):
        return self.inner.denoise(q, nu)

    def denoise_full(self, q, nu):
        m, J = self.inner.denoise_full(q, nu)
        Jh = 0.5 * (J + J.conj().T)
        w, V = np.linalg.eigh(Jh)
        self.n_call += 1
        self.n_neg_in += int(w.min() < 0)
        if self.mode == "psd":                     # valid covariance AND valid EP site: 0 < eig(J) <= 1
            w = np.clip(w, self.delta, 1.0)        #   removes BOTH the negative sign and the near-zero magnitude
        elif self.mode == "absmin":                # KEEP the sign (still indefinite), remove only the
            w = np.sign(w) * np.minimum(np.maximum(np.abs(w), self.delta), 1.0)   # near-singular magnitude
        elif self.mode == "flip":                  # inject the SIGN defect only: |eig| unchanged, tr(J) ~ fixed
            w = w.copy(); ix = np.argsort(np.abs(w))[: self.mflip]
            w[ix] = -np.abs(w[ix])
        elif self.mode == "tiny":                  # inject the CONDITIONING defect only: still strictly PD
            w = w.copy(); ix = np.argsort(np.abs(w))[: self.mflip]
            w[ix] = self.delta
        else:
            raise ValueError(self.mode)
        return m, (V * w) @ V.conj().T


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
    gm = hp[bstar]

    rx, wrap = {}, {}
    # --- anchors (pre-registered wiring, untouched)
    rx["gmmB|epsite"]    = A.route_a(*a, gm.view("eta"), code, Xp, "gmm_site")            # == M-ours-bstar
    rx["dscore|eta"]     = A.route_a(*a, sp, code, Xp, "score", clip="eta")               # == M-ours-dscore
    rx["gmmB|eta"]       = A.route_a(*a, gm, code, Xp, "score", clip="eta")               # GMM through score wiring
    # --- (a) repair the broken arm
    rx["dscore|mean"]    = A.route_a(*a, sp, code, Xp, "score", clip="mean")
    for nm, md in (("psd", "psd"), ("abs", "absmin")):
        w = JFix(sp, md, delta=1e-2); wrap[f"dscore|{nm}1e-2"] = w
        rx[f"dscore|{nm}1e-2"] = A.route_a(*a, w, code, Xp, "score", clip="eta")
    # --- (b) break the working arm: SIGN defect alone, then CONDITIONING defect alone
    for nm, md, kw in (("flip4", "flip", dict(mflip=4)), ("tiny4", "tiny", dict(mflip=4, delta=1e-4))):
        w = JFix(gm, md, **kw); wrap[f"gmmB|{nm}"] = w
        rx[f"gmmB|{nm}"] = A.route_a(*a, w, code, Xp, "score", clip="eta")
    # --- reference: same denoiser, D-14 site removed entirely
    rx["dscore|belsc"]   = A.route_a(*a, sp, code, Xp, "score", clip="eta", hsite="scalar")
    rx["gauss|sitesc"]   = A.route_a(*a, Cs, code, Xp, "gaussian")                        # == R2-ours-G

    meta = dict(bstar=bstar, pil=pil, ckpt=str(getattr(sp, "ckpt", "?")), why=why,
                cfg={k: {q: str(v.cfg_dump.get(q)) for q in
                         ("mode", "scal", "hsite", "lam_min", "exact_prior", "clip", "class_", "beta")}
                     for k, v in rx.items()})
    return rx, wrap, gen, code, meta


def run_point(cell, snr, n, iters=C.N_ITER, testbed="D2", prior="S2", ckpt=None):
    rx, wrap, gen, code, meta = build(cell, snr, testbed, prior, ckpt)
    first = rx["gauss|sitesc"]
    logs = {k: [] for k in rx}; fail = {k: 0 for k in rx}; clip = {k: [] for k in rx}
    rng = C.trial_rng(testbed, prior, gen.Nr if hasattr(gen, "Nr") else C.CELLS[cell]["Nr"],
                      C.CELLS[cell]["T"], C.CELLS[cell]["Tp"], snr)
    t0 = time.time()
    for tr in range(n):
        H = gen.sample(rng); u = rng.integers(0, 2, code.K); perm = rng.permutation(code.Ns)
        X, Y = first.transmit(u, perm, H, rng)
        for k, r in rx.items():
            so = R.stats_obj(r)
            if so is not None:
                so.reset_stats()
            try:
                logs[k].append(r.run(Y, H, u, perm, iters))
            except Exception:
                fail[k] += 1
                logs[k].append({q: np.full(iters, np.nan) for q in C.KEYS_LOG})
            if so is not None:
                clip[k].append((so.n_clip / max(so.n_site, 1), so.shift / max(so.n_clip, 1)))
        if (tr + 1) % 16 == 0:
            print(f"#   trial {tr+1}/{n}  {time.time()-t0:.0f} s", flush=True)
    out = {}
    for k, L in logs.items():
        for q in ("blk_err", "ber", "nmse", "nuE", "nu_q", "alphaH"):
            out[f"{k}|{q}"] = np.array([l[q] for l in L])
        out[f"{k}|failed"] = np.array([fail[k]])
        if clip[k]:
            out[f"{k}|clip"] = np.array(clip[k])
    for k, w in wrap.items():
        out[f"{k}|jfix"] = np.array([w.n_neg_in, w.n_call])
    out["meta|json"] = np.array(json.dumps(meta))
    out["run|snr"] = snr; out["run|n"] = n; out["run|iters"] = iters
    p = os.path.join(OUT, f"{TAG}_{testbed}_{cell}_snr{int(snr):+d}_n{n}.npz")
    np.savez_compressed(p, **out)
    print(f"# saved {p}   ({time.time()-t0:.0f} s)", flush=True)
    return out, meta


def table(out, snr, n):
    print(f"\n--- D2 C2  SNR {snr:+.0f} dB,  n={n} paired trials,  16 iterations ---")
    print(f"{'arm':<16} {'BLER@1':>7} {'BLER@2':>7} {'BLER@16':>8} {'+-95%':>7} {'BER@16':>8} "
          f"{'NMSEmed@16':>11} {'NMSEmean':>10} {'fr>1':>6} {'clip%':>6} {'clipshift':>10} {'Jneg%':>6}")
    for kk in [k for k in out if k.endswith("|blk_err")]:
        k = kk[:-len("|blk_err")]
        be = out[kk]; nm = out[f"{k}|nmse"]; cl = out.get(f"{k}|clip"); jf = out.get(f"{k}|jfix")
        p = float(np.nanmean(be[:, -1])); ci = 1.96 * np.sqrt(max(p * (1 - p), 1e-12) / n)
        print(f"{k:<16} {np.nanmean(be[:,0]):7.3f} {np.nanmean(be[:,1]):7.3f} {p:8.3f} {ci:7.3f} "
              f"{np.nanmean(out[f'{k}|ber'][:,-1]):8.3f} {np.nanmedian(nm[:,-1]):11.4f} "
              f"{np.nanmean(nm[:,-1]):10.3e} {np.nanmean(nm[:,-1]>1.0):6.3f} "
              f"{(100*np.mean([c[0] for c in cl]) if cl is not None else np.nan):6.1f} "
              f"{(np.nanmean([c[1] for c in cl]) if cl is not None else np.nan):10.3e} "
              f"{(100*jf[0]/max(jf[1],1) if jf is not None else np.nan):6.1f}")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", default="C2"); ap.add_argument("--snrs", type=float, nargs="+", default=[0.0])
    ap.add_argument("--n", type=int, default=96); ap.add_argument("--iters", type=int, default=C.N_ITER)
    ap.add_argument("--ckpt", default=None)
    a = ap.parse_args()
    print(C.header("D2", [f"DIAGNOSTIC {TAG}: do()-interventions on the D-14 Jacobian site. "
                          "No retraining, no tuning of any pre-registered arm."]))
    for s in a.snrs:
        out, meta = run_point(a.cell, s, a.n, a.iters, ckpt=a.ckpt)
        print("# b* =", meta["bstar"], " pilots =", meta["pil"], " ckpt =", meta["ckpt"])
        table(out, s, a.n)
