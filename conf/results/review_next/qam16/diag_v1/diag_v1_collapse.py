"""diag_v1_collapse.py -- E5QAM16 §6.5 / WORK_QUEUE 11 (user 2026-10-18 CDT): DEVELOPMENT-ONLY diagnosis of the V1 collapse at
+18 / +21 dB (16-QAM).  Not a registered analysis; no label; the E5 test raws are not read.  Nothing under Demo/ or conf/code
is modified -- the receiver objects are only wrapped at instance level to OBSERVE what Module H is asked and returns.

  traj  <U28|D2> <qpsk|16qam> <snr> [<snr> ...]   development trials 5440..5479 (n 40, the §1.3 diagnostic trials), arms
        V1 (M-ours-dscore-C-V1), b* (M-ours-bstar) and gmmB-scorew-eta (b*'s GMM in V1's score wiring); per outer iteration:
        failures, NMSE, and for the two score-wired arms the query (q, nu_q) of the matrix site with
        err_q = mean|q - h|^2 (the actual query error) / nu_q, err_m = mean|m - h|^2 (denoiser output error),
        pred_m = nu_q tr(J)/N (its claimed variance), sigma = sqrt(nu_q/2) vs the checkpoint's frozen grid, J and Lambda
        eigen-extremes and whether the site's Lambda was floored.
  synth <U28|D2>   synthetic queries q = h + CN(0, nu I) with h from the training-distribution generator (own seed
        20261018, no trial stream), sigma from 0.25 s_lo to 2 s_hi: input MSE (= nu), V1 denoiser MSE and claimed
        variance, the GMM b* posterior-mean MSE (exact for the GMM, the reference).

    cd ~/t2/conf && CUDA_VISIBLE_DEVICES= nice -n 10 taskset -c <cpu> python results/review_next/qam16/diag_v1/diag_v1_collapse.py ...
Outputs next to this file: traj_<cell>_<mod>.npz/.txt, synth_<cell>.npz/.txt (refuses to overwrite).
"""
import os, sys
sys.path.insert(0, "code")
import numpy as np
import common as C
import runner as R

CELLS = {"U28": ("UMi28", "U28QAM16mrg", "/home/HTJ/t2/conf/ckpt/d2sx_UMi28_N160000_a1_best.pt"),
         "D2": ("S2", "D2QAM16mrg", "/home/HTJ/t2/conf/ckpt/d2sx_N160000_a1.pt")}
OUT = os.path.dirname(os.path.abspath(__file__))
SKIP0, N = 5440, 40
V1, BS, GW = "M-ours-dscore-C-V1", "M-ours-bstar", "gmmB-scorew-eta"


def point(cell, mod, snr):
    prior, tag, ck = CELLS[cell]
    R._init(tag)
    return R.build_point("D2", "C2", prior, snr, ntrain=160000, stagec_ckpt=ck, mod=mod, mean_arms=True)


def hook(rx, rec, h_true):
    """Record what the matrix site is asked (q, nu_q) and what Module H returns (m, J) -- the cached evaluation the
    receiver itself uses, so the receiver's numbers are unchanged."""
    f = rx._matrix_site

    def g(q, nu_q, G):
        out = f(q, nu_q, G)
        m, J = rx.prior.denoise_full(q, nu_q)
        Jh = 0.5 * (J + J.conj().T); wj = np.linalg.eigvalsh(Jh)
        SigH = nu_q * Jh; Lam = np.linalg.inv(SigH) - np.eye(len(q)) / nu_q; wl = np.linalg.eigvalsh(0.5 * (Lam + Lam.conj().T))
        h = h_true[0]
        rec.append((nu_q, np.mean(np.abs(q - h) ** 2), np.mean(np.abs(m - h) ** 2), nu_q * np.trace(J).real / len(q),
                    wj.min(), wj.max(), wl.min(), float(wl.min() < rx.lam_min)))
        return out
    rx._matrix_site = g


def traj(cell, mod, snrs):
    path = os.path.join(OUT, f"traj_{cell}_{mod}")
    if os.path.exists(path + ".npz"):
        sys.exit(f"{path}.npz exists -- refusing")
    vals, lines = {}, []
    for snr in snrs:
        p = point(cell, mod, snr)
        arms = {a: p["arms"][a] for a in (V1, BS, GW)}
        s_lo, s_hi = arms[V1].prior.s_lo, arms[V1].prior.s_hi
        rng = C.trial_rng("D2", CELLS[cell][0], p["Nr"], p["T"], p["Tp"], snr)
        h_true = [None]; recs = {V1: [], GW: []}
        for a in recs:
            hook(arms[a], recs[a], h_true)
        logs = {a: {"blk_err": [], "nmse": []} for a in arms}
        site = {a: [] for a in recs}
        for tr in range(SKIP0 + N):
            H = p["gen"].sample(rng); u = rng.integers(0, 2, p["code"].K); perm = rng.permutation(p["code"].Ns)
            _, Y = arms[V1].transmit(u, perm, H, rng)
            if tr < SKIP0:
                continue
            h_true[0] = H.reshape(-1, order="F")
            for a, rx in arms.items():
                n0 = len(recs[a]) if a in recs else 0
                lg = rx.run(Y, H, u, perm, C.N_ITER)
                logs[a]["blk_err"].append(lg["blk_err"]); logs[a]["nmse"].append(lg["nmse"])
                if a in recs:
                    r = np.asarray(recs[a][n0:], float)
                    assert len(r) == C.N_ITER, (a, len(r))      # one matrix site per outer iteration
                    site[a].append(r)
        k = f"{snr:g}"
        for a in arms:
            vals[f"{k}|{a}|blk_err"] = be = np.asarray(logs[a]["blk_err"], float)
            vals[f"{k}|{a}|nmse"] = nm = np.asarray(logs[a]["nmse"], float)
            lines.append(f"{snr:+3.0f} dB {mod:5s} {a:<20} failures/iter " + " ".join(f"{int((be[:, i] != 0).sum()):2d}" for i in range(C.N_ITER))
                         + f"   median NMSE it1 {np.nanmedian(nm[:, 0]):.2e} it2 {np.nanmedian(nm[:, 1]):.2e} it16 {np.nanmedian(nm[:, 15]):.2e}")
        for a in recs:
            S = np.asarray(site[a])                          # (N trials, 16 iters, 8 fields)
            vals[f"{k}|{a}|site"] = S
            nu, eq, em, pm = S[..., 0], S[..., 1], S[..., 2], S[..., 3]
            sig = np.sqrt(nu / 2)
            med = lambda x: " ".join(f"{v:.2g}" for v in np.median(x, 0)[[0, 1, 2, 3, 7, 15]])
            lines.append(f"      {a:<20} it 1,2,3,4,8,16: err_q/nu_q {med(eq / nu)} | err_m/nu_q {med(em / nu)} | err_m/pred_m {med(em / pm)}")
            lines.append(f"      {'':<20} sigma<s_lo count/40 " + " ".join(str(int(v)) for v in (sig < s_lo).sum(0)[[0, 1, 2, 3, 7, 15]])
                         + f" | Lambda floored count/40 " + " ".join(str(int(v)) for v in S[..., 7].sum(0)[[0, 1, 2, 3, 7, 15]])
                         + f" | min eig J median " + " ".join(f"{v:.2g}" for v in np.median(S[..., 4], 0)[[0, 1, 2, 3, 7, 15]]))
        vals[f"{k}|grid"] = np.array([s_lo, s_hi])
    txt = (f"# diag_v1_collapse traj {cell} {mod}: development trials {SKIP0}..{SKIP0 + N - 1}, SNR {snrs}; site fields "
           "(nu_q, err_q, err_m, pred_m, minEigJ, maxEigJ, minEigLam, floored)\n" + "\n".join(lines) + "\n")
    np.savez_compressed(path + ".npz", **vals)
    open(path + ".txt", "w").write(txt)
    print(txt, flush=True)


def synth(cell):
    path = os.path.join(OUT, f"synth_{cell}")
    if os.path.exists(path + ".npz"):
        sys.exit(f"{path}.npz exists -- refusing")
    p = point(cell, "qpsk", 15.0)
    v1, gw = p["arms"][V1].prior, p["arms"][GW].prior
    s_lo, s_hi = v1.s_lo, v1.s_hi
    rng = np.random.default_rng(20261018)
    hs = [p["gen"].sample(rng).reshape(-1, order="F") for _ in range(200)]
    sig = np.geomspace(0.25 * s_lo, 2 * s_hi, 13)
    rows, vals = [], {"sigma": sig, "grid": np.array([s_lo, s_hi])}
    for s in sig:
        nu = 2 * s * s
        r = []
        for h in hs:
            q = h + np.sqrt(nu / 2) * (rng.standard_normal(h.shape) + 1j * rng.standard_normal(h.shape))
            m, J = v1.denoise_full(q, nu); mg, _ = gw.denoise(q, nu)
            r.append((np.mean(np.abs(q - h) ** 2), np.mean(np.abs(m - h) ** 2), nu * np.trace(J).real / len(h),
                      np.mean(np.abs(mg - h) ** 2)))
        r = np.asarray(r); vals[f"{s:.6g}"] = r
        rows.append(f"sigma {s:.4g} ({'below' if s < s_lo else 'above' if s > s_hi else 'inside'} grid)  nu {nu:.3e}  "
                    f"input MSE/nu {r[:, 0].mean() / nu:.3f}  V1 MSE/nu {r[:, 1].mean() / nu:.3f}  V1 claimed/nu {r[:, 2].mean() / nu:.3f}  "
                    f"GMM b* MSE/nu {r[:, 3].mean() / nu:.3f}")
    txt = (f"# diag_v1_collapse synth {cell}: 200 channels from the generator (seed 20261018), q = h + CN(0, nu I), "
           f"frozen grid [{s_lo:.4g}, {s_hi:.4g}]; MSE are means over the 200 channels\n" + "\n".join(rows) + "\n")
    np.savez_compressed(path + ".npz", **vals)
    open(path + ".txt", "w").write(txt)
    print(txt, flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "traj":
        traj(sys.argv[2], sys.argv[3], [float(s) for s in sys.argv[4:]])
    else:
        synth(sys.argv[2])
