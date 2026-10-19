"""diag_lowsig.py -- WORK_QUEUE 13 (user 2026-10-18 CDT "제안대로 진행"): DEVELOPMENT-ONLY screen of two V1 variants for queries
below the checkpoint's frozen sigma grid (sigma = sqrt(nu/2) < s_lo), against V1 and b*.  Not a registered analysis; nothing under
conf/code or Demo is modified -- the variants wrap V1's ScorePrior at instance level:

  V1-clamp : nu < nu_lo = 2 s_lo^2  ->  evaluate the network at nu_lo, form the prior site there
             (Lam_c = (nu_lo J_c)^-1 - I/nu_lo, eta_c = (nu_lo J_c)^-1 m_c - q/nu_lo) and return the (m', J') for which the
             receiver's matrix site at the ACTUAL nu reproduces that site exactly: J' = (nu Lam_c + I)^-1, m' = J'(nu eta_c + q).
  V1-gmmfb : nu < nu_lo  ->  b*'s GMM denoiser (the same GMMPriorB object as gmmB-scorew-eta) instead of the network.
Above s_lo both are V1 bit for bit (same object, same cache).

    cd ~/t2/conf && CUDA_VISIBLE_DEVICES= nice -n 10 taskset -c <cpu> python results/review_next/lowsig/diag_lowsig.py \
        <U28|D2> <qpsk|16qam> <skip0> <n> <snr> [<snr> ...]
Output next to this file: screen_<cell>_<mod>_<skip0>_<n>.{txt,npz} (refuses to overwrite).  Failures are counted at every iteration;
no test trial is used (skip0 >= 2560 enforced).
"""
import copy, os, sys
sys.path.insert(0, "code")
import numpy as np
import common as C
import runner as R

CELLS = {"U28": ("UMi28", "U28QAM16mrg", "/home/HTJ/t2/conf/ckpt/d2sx_UMi28_N160000_a1_best.pt"),
         "D2": ("S2", "D2QAM16mrg", "/home/HTJ/t2/conf/ckpt/d2sx_N160000_a1.pt")}
OUT = os.path.dirname(os.path.abspath(__file__))
V1, BS, GW = "M-ours-dscore-C-V1", "M-ours-bstar", "gmmB-scorew-eta"


class LowSig:
    """Delegates everything to the wrapped ScorePrior except denoise / denoise_full below nu_lo."""
    def __init__(self, sp, mode, gmm=None):
        self.__dict__["_sp"], self.__dict__["_mode"], self.__dict__["_gmm"] = sp, mode, gmm
        self.__dict__["_nu_lo"] = 2 * sp.s_lo ** 2
        self.__dict__["n_low"] = 0

    def __getattr__(self, k):
        return getattr(self._sp, k)

    def denoise_full(self, q, nu):
        if nu >= self._nu_lo:
            return self._sp.denoise_full(q, nu)
        self.__dict__["n_low"] += 1
        if self._mode == "gmmfb":
            return self._gmm.denoise_full(q, nu)
        nl = self._nu_lo
        mc, Jc = self._sp.denoise_full(q, nl)
        I = np.eye(len(q))
        Sinv = np.linalg.inv(nl * 0.5 * (Jc + Jc.conj().T))
        Lc = Sinv - I / nl; ec = Sinv @ mc - q / nl
        Jp = np.linalg.inv(nu * Lc + I)
        return Jp @ (nu * ec + q), Jp

    def denoise(self, q, nu):
        m, J = self.denoise_full(q, nu)
        return m, float(np.trace(J).real / len(q))


def main(cell, mod, skip0, n, snrs):
    assert skip0 >= C.DEV_SKIP0, "development trials only"
    path = os.path.join(OUT, f"screen_{cell}_{mod}_{skip0}_{n}" + ("" if len(snrs) > 1 else f"_snr{snrs[0]:g}"))   # one-SNR runs (screen2) get the SNR in the name
    if os.path.exists(path + ".npz"):
        sys.exit(f"{path}.npz exists -- refusing")
    prior, tag, ck = CELLS[cell]
    R._init(tag)
    vals, lines = {}, []
    for snr in snrs:
        p = R.build_point("D2", "C2", prior, snr, ntrain=160000, stagec_ckpt=ck, mod=mod, mean_arms=True)
        v1 = p["arms"][V1]
        arms = {"V1": v1, "b*": p["arms"][BS]}
        for mode in ("clamp", "gmmfb"):
            rx = copy.copy(v1); rx.prior = LowSig(v1.prior, mode, p["arms"][GW].prior); arms[f"V1-{mode}"] = rx
        rng = C.trial_rng("D2", prior, p["Nr"], p["T"], p["Tp"], snr)
        logs = {a: {"blk_err": [], "nmse": []} for a in arms}
        for tr in range(skip0 + n):
            H = p["gen"].sample(rng); u = rng.integers(0, 2, p["code"].K); perm = rng.permutation(p["code"].Ns)
            _, Y = v1.transmit(u, perm, H, rng)
            if tr < skip0:
                continue
            for a, rx in arms.items():
                lg = rx.run(Y, H, u, perm, C.N_ITER)
                logs[a]["blk_err"].append(lg["blk_err"]); logs[a]["nmse"].append(lg["nmse"])
        for a in arms:
            be = np.asarray(logs[a]["blk_err"], float); nm = np.asarray(logs[a]["nmse"], float)
            vals[f"{snr:g}|{a}|blk_err"], vals[f"{snr:g}|{a}|nmse"] = be, nm
            f = lambda i: int((be[:, i] != 0).sum())
            lines.append(f"{snr:+3.0f} dB {mod:5s} {a:<9} failures @1 {f(0):4d} @2 {f(1):4d} @4 {f(3):4d} @16 {f(15):4d} / {n}   "
                         f"median NMSE @1 {np.nanmedian(nm[:, 0]):.2e} @16 {np.nanmedian(nm[:, 15]):.2e}"
                         + (f"   low-sigma queries {arms[a].prior.n_low}" if a.startswith("V1-") else ""))
    txt = f"# diag_lowsig {cell} {mod}: development trials {skip0}..{skip0 + n - 1}, SNR {snrs}\n" + "\n".join(lines) + "\n"
    np.savez_compressed(path + ".npz", **vals)
    open(path + ".txt", "w").write(txt)
    print(txt, flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    main(a[0], a[1], int(a[2]), int(a[3]), [float(s) for s in a[4:]])
