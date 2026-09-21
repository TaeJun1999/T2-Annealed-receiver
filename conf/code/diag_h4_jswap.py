"""conf/code/diag_h4_jswap.py -- ADVERSARIAL re-test of H4 (wiring vs prior).

The published H4 factorial swapped the WHOLE denoiser (mean + Jacobian) between the GMM and the
checkpoint.  That cannot separate "the learned mean is bad" from "the learned Jacobian is bad", and it
cannot show that the non-PSD Jacobian is SUFFICIENT.  Here only ONE factor moves at a time inside the
frozen M-ours-dscore wiring (mode='scalar', scal='belief', hsite='matrix', RouteAClip(clip='eta')):

  d|scorew          control                     == M-ours-dscore                    (mean d, J d)
  d|scorew+gmmJ     learned mean, EXACT GMM J   -> does replacing ONLY J rescue it? (mean d, J g)
  d|scorew+psd      learned mean, learned J with eig clamped into the EP-valid box (0,1]  (no knob:
                    the box is the definition of a valid site, eig(nu J) in (0, nu])
  d|scorew+clipmean RouteAClip(clip='mean'): identical site arithmetic, but eta is recomputed so the
                    denoiser-stage belief mean stays hH -> isolates the eta/Lambda INCONSISTENCY of the
                    clip rule (a WIRING property) from the Jacobian itself
  g|scorew          exact GMM denoiser in the score wiring (their decisive hybrid, reproduced)
  g|scorew+dJ       EXACT GMM mean, LEARNED J   -> is the learned J SUFFICIENT to cause the collapse?

Diagnostic only: frozen checkpoint, no retraining, no tuning, no threshold changed, nothing written
outside conf/results/diag/.
"""
import os, sys, time, json
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import arms as A
import runner as R
from diag_ep_site import build as _build_ref   # reuse the VALIDATED harness (bit-exact vs raw_supp)

OUT = os.path.join(C.CONF, "results", "diag")
TAG = "h4-jswap"


class JSwap:
    """Delegates everything to `base`; only the Jacobian handed to the D-14 matrix site is altered.
    denoise() (the D-13 scalar/alpha path) is ALWAYS the base prior's, so the arm differs from its
    control in exactly one place: the J inside RouteAClip._matrix_site."""

    def __init__(self, base, jac=None, psd=False):
        self.base, self.jac, self.psd = base, jac, psd

    def __getattr__(self, k):
        if k in ("base", "jac", "psd"):
            raise AttributeError(k)
        return getattr(self.base, k)

    def denoise(self, q, nu):
        return self.base.denoise(q, nu)

    def denoise_full(self, q, nu):
        m, J = self.base.denoise_full(q, nu)
        if self.jac is not None:
            _, J = self.jac.denoise_full(q, nu)
        if self.psd:
            Jh = 0.5 * (J + J.conj().T)
            w, V = np.linalg.eigh(Jh)
            J = (V * np.clip(w, 1e-6, 1.0)) @ V.conj().T     # the EP-valid box, not a tuned knob
        return m, J


def build(cell, snr, ckpt):
    c = C.CELLS[cell]
    Nr, Nt, T, Tp = c["Nr"], c["Nt"], c["T"], c["Tp"]
    sigma2 = 10 ** (-snr / 10)
    code = C.QAMCode(C.GENS, C.NU, C.M_QAM, Nt * (T - c["Tp"]))
    pil, Xp = C.make_pilots("D2", "S2", Nt, Tp, Nr)
    gen = C.make_gen("D2", "S2", Nr, Nt)
    hp, fits, llv, bstar, kron_K = A.module_h_priors("D2", "S2", Nr, Nt)
    Cs = C.GaussianPrior(Nr, Nt, fits[("full", 32)]["Chat"])
    sp, why = R.score_prior("D2", "S2", Nr, Nt, ckpt)
    assert sp is not None, why
    gm = hp[bstar]
    a = (Nr, Nt, T, Tp, sigma2)
    rx = {}
    rx["d|scorew"]          = A.route_a(*a, sp, code, Xp, "score", clip="eta")
    rx["d|scorew+gmmJ"]     = A.route_a(*a, JSwap(sp, jac=gm), code, Xp, "score", clip="eta")
    rx["d|scorew+psd"]      = A.route_a(*a, JSwap(sp, psd=True), code, Xp, "score", clip="eta")
    rx["d|scorew+clipmean"] = A.route_a(*a, sp, code, Xp, "score", clip="mean")
    rx["g|scorew"]          = A.route_a(*a, gm, code, Xp, "score", clip="eta")
    rx["g|scorew+dJ"]       = A.route_a(*a, JSwap(gm, jac=sp), code, Xp, "score", clip="eta")
    rx["gauss|sitesc"]      = A.route_a(*a, Cs, code, Xp, "gaussian")      # transmitter + anchor
    meta = dict(bstar=bstar, pil=pil, ckpt=str(getattr(sp, "ckpt", "?")), why=why)
    return rx, gen, code, Nr, Nt, T, Tp, meta


def run_point(cell, snr, n, ckpt, iters=C.N_ITER):
    rx, gen, code, Nr, Nt, T, Tp, meta = build(cell, snr, ckpt)
    first = rx["gauss|sitesc"]
    logs = {k: [] for k in rx}; fail = {k: 0 for k in rx}; clip = {k: [] for k in rx}
    rng = C.trial_rng("D2", "S2", Nr, T, Tp, snr)          # SAME trial stream as the published run
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
    out = {}
    for k, L in logs.items():
        for q in ("blk_err", "ber", "nmse", "nuE", "nu_q", "alphaH", "hE_norm"):
            out[f"{k}|{q}"] = np.array([l[q] for l in L])
        out[f"{k}|failed"] = np.array([fail[k]])
        if clip[k]:
            out[f"{k}|clip"] = np.array(clip[k])
    out["meta|json"] = np.array(json.dumps(meta)); out["run|snr"] = snr; out["run|n"] = n
    p = os.path.join(OUT, f"{TAG}_D2_{cell}_snr{int(snr):+d}_n{n}.npz")
    np.savez_compressed(p, **out)
    print(f"# saved {p}  ({time.time()-t0:.0f} s)")
    return out


def table(out, snr, n):
    print(f"\n--- D2 C2  SNR {snr:+.0f} dB  n={n}  (paired trials; se = binomial) ---")
    print(f"{'arm':<20} {'BLER@16':>9} {'+-se':>6} {'NMSEmed@1':>10} {'NMSEmed@16':>11} "
          f"{'NMSEmean@16':>12} {'ever>1':>7} {'>1@it1':>7} {'clip%':>6} {'clipshift':>10} {'raised':>7}")
    for kk in [k for k in out if k.endswith("|blk_err")]:
        k = kk[:-len("|blk_err")]
        be = out[f"{k}|blk_err"][:, -1]; nm = out[f"{k}|nmse"]; cl = out.get(f"{k}|clip")
        p = float(np.nanmean(be))
        print(f"{k:<20} {p:9.3f} {np.sqrt(p*(1-p)/n):6.3f} {np.nanmedian(nm[:,0]):10.4f} "
              f"{np.nanmedian(nm[:,-1]):11.4f} {np.nanmean(nm[:,-1]):12.4g} "
              f"{np.nanmean(np.nanmax(nm,1)>1.0):7.3f} {np.nanmean(nm[:,0]>1.0):7.3f} "
              f"{(100*np.mean([c[0] for c in cl]) if cl is not None else float('nan')):6.1f} "
              f"{(np.nanmean([c[1] for c in cl]) if cl is not None else float('nan')):10.3e} "
              f"{int(out[f'{k}|failed'][0]):7d}")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", default="C2"); ap.add_argument("--snrs", type=float, nargs="+", default=[0.0])
    ap.add_argument("--n", type=int, default=128)
    ap.add_argument("--ckpt", default="/home/HTJ/t2/conf/ckpt/d2sx_N10000_a1.pt")
    a = ap.parse_args()
    print(C.header("D2", [f"DIAGNOSTIC {TAG}: single-factor Jacobian swap inside the frozen score wiring."]))
    for s in a.snrs:
        table(run_point(a.cell, s, a.n, a.ckpt), s, a.n)
