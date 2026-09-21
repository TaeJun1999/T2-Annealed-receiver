"""REVIEW probe for Stage C V1 (F1): does the floor-only PSD projection survive the RECEIVER LOOP?

Written by the V1 REVIEWER, not the implementer.  It closes the implementer's own risk (1): M6 measures
ONE denoiser call in isolation, so nothing in it says the 16-iteration EP loop converges.

The existing evidence (results/diag/h4-jswap_summary.txt, arm `d|scorew+psd`) clamps the eigenvalues into
the box (1e-6, 1.0].  V1's score.project_psd FLOORS at 1e-6 and deliberately does NOT cap lmax, so
Lam = (nu J)^-1 - I/nu is still driven negative whenever lmax(J) > 1 and RouteAClip still clips it while
keeping the unclipped eta.  The box arm therefore does NOT cover V1.  This probe runs V1 itself.

  V0-d|scorew      ScorePrior(psd_project=False)  -- the diverging control, must reproduce h4-jswap
  V1-d|scorew+psdf ScorePrior(psd_project=True)   -- THE CODE UNDER REVIEW, unmodified
  ref-d|scorew+box JSwap(psd=True)                -- the (0,1] box already measured, cross-check
  g|scorew         exact GMM in the same wiring   -- anchor

Same cell/SNR/trial stream as diag_h4_jswap.py so `V0-d|scorew` is pairable with the recorded npz.
DIAGNOSTIC ONLY: frozen checkpoint, nothing retrained, no threshold touched, NOT A RESULT, may not
enter any table.  Writes only conf/results/diag/review-V1-receiver_*.
"""
import argparse, json, os, sys, time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import arms as A
import runner as R
import score
from diag_h4_jswap import JSwap

OUT = os.path.join(C.CONF, "results", "diag")


def build(cell, snr, ckpt):
    c = C.CELLS[cell]
    Nr, Nt, T, Tp = c["Nr"], c["Nt"], c["T"], c["Tp"]
    sigma2 = 10 ** (-snr / 10)
    code = C.QAMCode(C.GENS, C.NU, C.M_QAM, Nt * (T - c["Tp"]))
    pil, Xp = C.make_pilots("D2", "S2", Nt, Tp, Nr)
    gen = C.make_gen("D2", "S2", Nr, Nt)
    hp, fits, llv, bstar, kron_K = A.module_h_priors("D2", "S2", Nr, Nt)
    sp0 = score.load_prior("D2", "S2", Nr, Nt, ckpt=ckpt)                      # V0 / current default
    sp1 = score.load_prior("D2", "S2", Nr, Nt, ckpt=ckpt, psd_project=True)    # V1, the code under review
    assert sp0 is not None and sp1 is not None, score.last_reason
    assert sp0.psd_project is False and sp1.psd_project is True
    gm = hp[bstar]
    a = (Nr, Nt, T, Tp, sigma2)
    rx = {"V0-d|scorew":      A.route_a(*a, sp0, code, Xp, "score", clip="eta"),
          "V1-d|scorew+psdf": A.route_a(*a, sp1, code, Xp, "score", clip="eta"),
          "ref-d|scorew+box": A.route_a(*a, JSwap(sp0, psd=True), code, Xp, "score", clip="eta"),
          "g|scorew":         A.route_a(*a, gm, code, Xp, "score", clip="eta")}
    # the transmitter/anchor, so the trial stream matches diag_h4_jswap exactly
    first = A.route_a(*a, C.GaussianPrior(Nr, Nt, fits[("full", 32)]["Chat"]), code, Xp, "gaussian")
    return rx, first, gen, code, Nr, T, Tp, dict(bstar=bstar, pil=pil, ckpt=str(ckpt))


def main(a):
    print(C.header("D2", ["REVIEW probe review-V1-receiver: does V1's floor-only PSD projection converge "
                          "in the 16-iteration loop?  DIAGNOSTIC ONLY, NOT A RESULT."]), flush=True)
    rx, first, gen, code, Nr, T, Tp, meta = build(a.cell, a.snr, a.ckpt)
    rng = C.trial_rng("D2", "S2", Nr, T, Tp, a.snr)          # SAME stream as diag_h4_jswap
    logs = {k: [] for k in rx}; clip = {k: [] for k in rx}; fail = {k: 0 for k in rx}
    t0 = time.time()
    for tr in range(a.n):
        H = gen.sample(rng); u = rng.integers(0, 2, code.K); perm = rng.permutation(code.Ns)
        X, Y = first.transmit(u, perm, H, rng)
        for k, r in rx.items():
            so = R.stats_obj(r)
            if so is not None:
                so.reset_stats()
            try:
                logs[k].append(r.run(Y, H, u, perm, a.iters))
            except Exception as ex:
                fail[k] += 1; logs[k].append({q: np.full(a.iters, np.nan) for q in C.KEYS_LOG})
            if so is not None:
                clip[k].append((so.n_clip / max(so.n_site, 1), so.shift / max(so.n_clip, 1)))
        if (tr + 1) % 8 == 0:
            print(f"#   trial {tr+1}/{a.n}  ({time.time()-t0:.0f} s)", flush=True)

    out = {}
    print(f"\n--- D2 {a.cell}  SNR {a.snr:+.0f} dB  n={a.n}  {a.iters} iters  (paired) ---")
    print(f"{'arm':<18}{'BLER@last':>10}{'+-se':>7}{'NMSEmed@1':>11}{'NMSEmed@last':>13}"
          f"{'NMSEmean@last':>14}{'ever>1':>8}{'clip%':>7}{'clipshift':>11}{'raised':>7}")
    for k, L in logs.items():
        for q in ("blk_err", "nmse", "nu_q", "alphaH"):
            out[f"{k}|{q}"] = np.array([l[q] for l in L])
        out[f"{k}|failed"] = np.array([fail[k]])
        if clip[k]:
            out[f"{k}|clip"] = np.array(clip[k])
        be = out[f"{k}|blk_err"][:, -1]; nm = out[f"{k}|nmse"]; cl = clip[k]
        p = float(np.nanmean(be))
        print(f"{k:<18}{p:10.3f}{np.sqrt(p*(1-p)/a.n):7.3f}{np.nanmedian(nm[:,0]):11.4f}"
              f"{np.nanmedian(nm[:,-1]):13.4f}{np.nanmean(nm[:,-1]):14.4g}"
              f"{np.nanmean(np.nanmax(nm,1)>1.0):8.3f}"
              f"{(100*np.mean([c[0] for c in cl]) if cl else float('nan')):7.1f}"
              f"{(np.nanmean([c[1] for c in cl]) if cl else float('nan')):11.3e}{fail[k]:7d}")

    # cross-check: the V0 control must reproduce the recorded h4-jswap run trial for trial
    ref = os.path.join(OUT, f"h4-jswap_D2_{a.cell}_snr{int(a.snr):+d}_n64.npz")
    if os.path.exists(ref):
        z = np.load(ref, allow_pickle=True); m = min(a.n, len(z["d|scorew|blk_err"]))
        d = float(np.nanmax(np.abs(z["d|scorew|nmse"][:m] - out["V0-d|scorew|nmse"][:m])))
        e = int(np.sum(z["d|scorew|blk_err"][:m] != out["V0-d|scorew|blk_err"][:m]))
        print(f"\n# harness cross-check vs {os.path.basename(ref)} (first {m} paired trials): "
              f"max|dNMSE| = {d:.3e}, blk_err mismatches = {e}")
        d2 = float(np.nanmax(np.abs(z["d|scorew+psd|nmse"][:m] - out["ref-d|scorew+box|nmse"][:m])))
        print(f"# box arm cross-check: max|dNMSE| = {d2:.3e}")

    out["meta|json"] = np.array(json.dumps(meta)); out["run|snr"] = a.snr; out["run|n"] = a.n
    p = os.path.join(OUT, f"review-V1-receiver_D2_{a.cell}_snr{int(a.snr):+d}_n{a.n}.npz")
    np.savez_compressed(p, **out)
    print(f"# saved {p}  ({time.time()-t0:.0f} s)", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", default="C2"); ap.add_argument("--snr", type=float, default=0.0)
    ap.add_argument("--n", type=int, default=48); ap.add_argument("--iters", type=int, default=C.N_ITER)
    ap.add_argument("--ckpt", default="/home/HTJ/t2/conf/ckpt/d2sx_N10000_a1.pt")
    main(ap.parse_args())
