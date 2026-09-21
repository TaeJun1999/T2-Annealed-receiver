"""conf/code/diag_ep_probe.py -- mechanism probe for H4: what does the D-14 matrix site look like?

For each receiver iteration of a few real D2/C2 trials, record the spectrum of  nu*J  (the denoiser-stage
covariance) and of the UNCLIPPED site precision  Lambda = (nu J)^-1 - I/nu, for both Module-H denoisers.
A valid EP site needs 0 < nu*J <= nu*I  (i.e. Cov[h|q] PSD and <= the cavity covariance).  Read only.
"""
import os, sys, json
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
from diag_ep_site import build



def instrument(rx, rec):
    base = rx._matrix_site

    def wrapped(q, nu_q, G):
        hH, J = rx.prior.denoise_full(q, nu_q)
        SigH = 0.5 * (nu_q * J + (nu_q * J).conj().T)
        ev_sig = np.linalg.eigvalsh(SigH)
        Lam = np.linalg.inv(SigH) - np.eye(rx.N) / nu_q
        ev_lam = np.linalg.eigvalsh(0.5 * (Lam + Lam.conj().T))
        rec.append(dict(nu=float(nu_q), alpha=float(np.trace(J).real / rx.N),
                        sig_min=float(ev_sig.min() / nu_q), sig_max=float(ev_sig.max() / nu_q),
                        lam_min=float(ev_lam.min()), lam_max=float(ev_lam.max()),
                        n_neg=int((ev_lam < 1e-6).sum()), hH=float(np.linalg.norm(hH))))
        return base(q, nu_q, G)
    rx._matrix_site = wrapped


def main(cell="C2", snr=0.0, n=8, iters=C.N_ITER):
    rx, gen, code, Nr, Nt, T, Tp, meta = build(cell, snr, ckpt=CK)
    keep = {k: rx[k] for k in ("dscore|scorew", "gmmB|scorew")}
    rec = {k: [] for k in keep}
    for k, r in keep.items():
        instrument(r, rec[k])
    rng = C.trial_rng("D2", "S2", Nr, T, Tp, snr)
    first = rx["gauss|sitesc"]
    for tr in range(n):
        H = gen.sample(rng); u = rng.integers(0, 2, code.K); perm = rng.permutation(code.Ns)
        X, Y = first.transmit(u, perm, H, rng)
        for k, r in keep.items():
            r.run(Y, H, u, perm, iters)
    out = {}
    print(f"# D2 {cell} SNR {snr:+.0f} dB, {n} trials x {iters} iterations; a VALID D-14 site needs 0 < eig(nu J)/nu <= 1")
    print(f"{'arm':<16} {'iter':>4} {'nu_q':>10} {'alpha=trJ/N':>12} {'min eig(J)':>11} {'max eig(J)':>11} "
          f"{'min eig(Lam)':>13} {'#eig(Lam)<0':>12} {'|hH|':>9}")
    for k, L in rec.items():
        a = {q: np.array([d[q] for d in L]).reshape(n, iters) for q in L[0]}
        out.update({f"{k}|{q}": v for q, v in a.items()})
        for it in list(range(min(6, iters))) + [iters - 1]:
            print(f"{k:<16} {it+1:>4} {np.median(a['nu'][:,it]):10.3e} {np.median(a['alpha'][:,it]):12.4f} "
                  f"{np.median(a['sig_min'][:,it]):11.3e} {np.median(a['sig_max'][:,it]):11.4f} "
                  f"{np.median(a['lam_min'][:,it]):13.3e} {np.median(a['n_neg'][:,it]):12.1f} {np.median(a['hH'][:,it]):9.3f}")
        print()
    p = os.path.join(C.CONF, "results", "diag", f"ep-site-integration_probe_D2_{cell}_snr{int(snr):+d}_n{n}.npz")
    np.savez_compressed(p, **out, meta=np.array(json.dumps(meta)))
    print("# saved", p)


if __name__ == "__main__":
    CK = "/home/HTJ/t2/conf/ckpt/d2sx_N10000_a1.pt"
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument("--snr", type=float, default=0.0)
    ap.add_argument("--n", type=int, default=8); ap.add_argument("--cell", default="C2")
    a = ap.parse_args(); main(a.cell, a.snr, a.n)
