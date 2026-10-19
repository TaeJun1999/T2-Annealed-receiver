"""golden helper (NOT the bench): count Module H / network calls per block on the real receiver code, my own instrumentation.

usage: python -I -B g_count.py D2|U32 SNR[,SNR...] [n_measured=1]
  D2 : C2 8x4, prior S2,    arms V1, V1-ms, b* (kron K1024; fits = gmm_fits_D2_B16e4k, read only)
  U32: C9 32x4, prior UMi28, arms V1, SBL-loop (rho 4, n_em 3, cold)   (GMM K4096/8192 skipped: memory; same code path as b*)
Trials: common.trial_rng stream, trials 0..2559 regenerated and dropped, 2560 = warm-up, 2561.. measured (dev set).
Counters per arm and block: H-method calls, ScorePrior n_query delta, torch.func.jacrev calls and Jacobian rows,
forward hooks on the backbone (sp.model.net), SBL EM steps (np.einsum calls made from arms.py; one per EM step).
"""
import hashlib, os, sys, time, types
os.environ["CUDA_VISIBLE_DEVICES"] = ""
sys.path.insert(0, "/home/HTJ/t2/conf/code")
import numpy as np
import common as C
import torch
torch.set_num_threads(1)
import arms as A
import score as S

which = sys.argv[1]
snrs = [float(s) for s in sys.argv[2].split(",")]
n_meas = int(sys.argv[3]) if len(sys.argv) > 3 else 1
NTRAIN = 160000
if which == "D2":
    prior, cell, ckpt = "S2", "C2", "/home/HTJ/t2/conf/ckpt/d2sx_N160000_a1.pt"
    A.D2_FITS = "/home/HTJ/t2/conf/results/gmm_fits_D2_B16e4k"
else:
    prior, cell, ckpt = "UMi28", "C9", "/home/HTJ/t2/conf/ckpt/d2sx_UMi28NR32_N160000_a1_best.pt"
    A.D2_FITS = "/home/HTJ/t2_wtS/conf/results/gmm_fits_D2_U28NR32B16e4"


class MatchedScalarPrior:            # verbatim from git 9dd8b5fe:conf/code/arms.py (E1+ V1-ms); absent from main's arms.py
    def __init__(self, sp):
        self.__dict__["sp"] = sp

    def __getattr__(self, k):
        return getattr(self.sp, k)

    def denoise_full(self, q, nu):
        m, J = self.sp.denoise_full(q, nu)
        return m, (np.trace(J).real / len(q)) * np.eye(len(q))


CUR = [None]
CNT = {}
_jr = torch.func.jacrev


def jacrev_counting(f, *a, **k):     # score.py looks torch.func.jacrev up at call time
    g = _jr(f, *a, **k)

    def h(*args):
        out = g(*args)
        c = CNT[CUR[0]]; c["jacrev"] += 1; c["jac_rows"] += int(out.shape[0]); c["jac_shape"] = tuple(out.shape)
        return out
    return h


torch.func.jacrev = jacrev_counting


class NpProxy(types.ModuleType):     # only arms.py's own `np.` lookups go through this
    def __getattr__(self, k):
        v = getattr(np, k)
        if k == "einsum":
            def e(*a, **kw):
                CNT[CUR[0]]["em_steps"] += 1
                return v(*a, **kw)
            return e
        return v


def wrap(obj, name, key):
    f = getattr(obj, name)

    def w(*a, **k):
        CNT[CUR[0]][key] += 1
        return f(*a, **k)
    setattr(obj, name, w)


c = C.CELLS[cell]; Nr, Nt, T, Tp = c["Nr"], c["Nt"], c["T"], c["Tp"]
for snr in snrs:
    sigma2 = 10 ** (-snr / 10)
    code = C.QAMCode(C.GENS, C.NU, C.MOD_BITS["qpsk"], Nt * (T - Tp))
    pil, Xp = C.make_pilots("D2", prior, Nt, Tp, Nr)
    gen = C.make_gen("D2", prior, Nr, Nt)
    fits = A.load_fits("D2", prior, Nr, NTRAIN)
    Cs = A.GaussianPrior(Nr, Nt, fits[("full", 32)]["Chat"])
    a = (Nr, Nt, T, Tp, sigma2)
    rxs, sps = {}, {}
    sp1 = S.load_prior("D2", prior, Nr, Nt, ckpt=ckpt, device="cpu", psd_project=True, ntrain=NTRAIN)
    assert sp1 is not None, S.last_reason
    rxs["V1"] = A.route_a(*a, sp1, code, Xp, "score", clip="eta"); sps["V1"] = sp1
    if which == "D2":
        spm = S.load_prior("D2", prior, Nr, Nt, ckpt=ckpt, device="cpu", psd_project=True, ntrain=NTRAIN)
        rxs["V1-ms"] = A.route_a(*a, MatchedScalarPrior(spm), code, Xp, "score", clip="eta"); sps["V1-ms"] = spm
        hp, _, llv, bstar, kron_K = A.module_h_priors("D2", prior, Nr, Nt, NTRAIN)
        rxs["bstar"] = A.route_a(*a, hp[bstar].view("eta"), code, Xp, "gmm_site")
        print(f"[{snr:+.0f} dB] b* = {bstar} kron_K = {kron_K} K = {rxs['bstar'].prior.K}  (folder {A.D2_FITS})")
    else:
        A.np = NpProxy("np")
        rxs["SBL"] = A.route_a(*a, A.SparsePrior(Cs, Nr, Nt, 4, 3, warm=False), code, Xp, "gmm_site")
        print(f"[{snr:+.0f} dB] SBL dictionary A {rxs['SBL'].prior.A.shape}, n_em {rxs['SBL'].prior.n_em}, warm {rxs['SBL'].prior.warm}")
    for k, rx in rxs.items():
        CNT[k] = dict(jacrev=0, jac_rows=0, fwd=0, H_denoise=0, H_msite=0, denoise_full=0, H_ep=0, gamma=0, em_steps=0)
        print(f"   {k:<6} class {type(rx).__name__:<10} mode {rx.mode:<8} scal {rx.scal:<6} hsite {rx.hsite:<6} exact_prior {rx.exact_prior}"
              f" n_inner {rx.n_inner} init_colored {rx.init_colored} nu_sw {rx.nu_sw}")
        if k in sps:
            sps[k].model.net.register_forward_hook(lambda m, i, o, k=k: CNT[k].__setitem__("fwd", CNT[k]["fwd"] + 1))
            wrap(rx.prior, "denoise", "H_denoise"); wrap(rx, "_matrix_site", "H_msite")
            wrap(sps[k], "denoise_full", "denoise_full")
        else:
            wrap(rx.prior, "ep_site", "H_ep")
            if k == "SBL":
                wrap(rx.prior, "gamma", "gamma")
    rng = C.trial_rng("D2", prior, Nr, T, Tp, snr)
    t0 = time.time()
    first = rxs["V1"]
    for tr in range(2560 + 1 + n_meas):
        H = gen.sample(rng); u = rng.integers(0, 2, code.K); perm = rng.permutation(code.Ns)
        X, Y = first.transmit(u, perm, H, rng)
        if tr < 2560:
            continue
        fp = hashlib.sha256(H.tobytes() + u.tobytes() + perm.tobytes() + Y.tobytes()).hexdigest()[:16]
        print(f"[{snr:+.0f} dB] trial {tr} ({'warm-up' if tr == 2560 else 'measured'}) block fingerprint {fp}  (stream regenerated in {time.time() - t0:.1f} s)")
        for k, rx in rxs.items():
            for f in CNT[k]:
                if f != "jac_shape":
                    CNT[k][f] = 0
            nq0 = sps[k].n_query if k in sps else 0
            CUR[0] = k
            t1 = time.time()
            out = rx.run(Y, H, u, perm, C.N_ITER)
            dt = time.time() - t1
            nq = (sps[k].n_query - nq0) if k in sps else None
            cc = dict(CNT[k]); cc["n_query_delta"] = nq
            print(f"   {k:<6} trial {tr}: iters logged {len(out['blk_err'])}  blk_err[-1] {int(out['blk_err'][-1])}  nmse[-1] {out['nmse'][-1]:.6e}  "
                  f"rx.run {dt:.2f} s  counts {cc}")
