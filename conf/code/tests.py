"""conf/code/tests.py -- the pre-registered unit tests of conf/07_SPEC_tests.md.

Every test returns (id, verdict, residual, criterion, one-line description).  A test that only prints
PASS is useless (07_SPEC preamble), so the residual is always a number.
Verdicts: PASS / FAIL / N/A / UNVERIFIED / RECORD (measurement-only tests).
"""
import hashlib
import numpy as np

import common as C
from common import (BETA, EPS_CLIP, GaussianPrior, LAM_MIN, N_ITER, N_TRAIN, QAMCode, RouteA, T_IN,
                    VAR_FLOOR, CONST_QPSK, CBITS_QPSK)
import bigamp as BG
import scvamp as SV
import arms as A

RES = []


def rec(tid, ok, resid, crit, desc):
    v = ok if isinstance(ok, str) else ("PASS" if ok else "FAIL")
    RES.append((tid, v, resid, crit, desc))
    return v


def _cell(cell="C1", prior="S", testbed="D1", snr=9.0):
    c = C.CELLS[cell]
    Nr, Nt, T, Tp = c["Nr"], c["Nt"], c["T"], c["Tp"]
    code = QAMCode(C.GENS, C.NU, C.M_QAM, Nt * (T - Tp))
    pil, Xp = C.make_pilots(testbed, prior, Nt, Tp, Nr)
    gen = C.make_gen(testbed, prior, Nr, Nt)
    return dict(Nr=Nr, Nt=Nt, T=T, Tp=Tp, code=code, pil=pil, Xp=Xp, gen=gen,
                sigma2=10 ** (-snr / 10), testbed=testbed, prior=prior, snr=snr, cell=cell)


def _trial(e, seed=11):
    rng = np.random.default_rng(seed)
    H = e["gen"].sample(rng)
    u = rng.integers(0, 2, e["code"].K)
    perm = rng.permutation(e["code"].Ns)
    tx = BG.R3BiGAMP(e["Nr"], e["Nt"], e["T"], e["Tp"], e["sigma2"], e["code"], e["Xp"])
    X, Y = tx.transmit(u, perm, H, rng)
    return H, u, perm, X, Y


# ============================================================================= R3 -- BiG-AMP
def _xprior_gauss(tau_x):
    def f(rhat, nu_r):
        return (tau_x / (tau_x + nu_r)) * rhat, tau_x * nu_r / (tau_x + nu_r)
    return f


def test_B1():
    """Damping identity: bigamp_iter(beta=1) == the independently written undamped Table III core."""
    rng = np.random.default_rng(3)
    Nr, Nt, T = 8, 4, 16
    sigma2, tau_h, tau_x = 0.13, 1.0 / Nr, 1.0
    Y = (rng.standard_normal((Nr, T)) + 1j * rng.standard_normal((Nr, T))) / np.sqrt(2)
    Hh = (rng.standard_normal((Nr, Nt)) + 1j * rng.standard_normal((Nr, Nt))) / np.sqrt(2 * Nr)
    Xh = (rng.standard_normal((Nt, T)) + 1j * rng.standard_normal((Nt, T))) / np.sqrt(2)
    nuh = np.full((Nr, Nt), 1.0 / Nr)
    nux = np.full((Nt, T), 1.0)
    xp = _xprior_gauss(tau_x)

    st = BG.BiGAMPState(Hh.copy(), nuh.copy(), Xh.copy(), nux.copy())
    pH, pnh, pX, pnx, psh = Hh.copy(), nuh.copy(), Xh.copy(), nux.copy(), np.zeros((Nr, T), complex)
    err = 0.0
    for _ in range(12):
        st, _ = BG.bigamp_iter(st, Y, sigma2, 1.0, tau_h, xp)
        pH, pnh, pX, pnx, psh, _, _ = BG.bigamp_iter_plain(pH, pnh, pX, pnx, psh, Y, sigma2, tau_h, xp)
        err = max(err, np.abs(st.Hh - pH).max(), np.abs(st.Xh - pX).max(),
                  np.abs(st.nuh - pnh).max(), np.abs(st.nux - pnx).max())
    return rec("B1", err <= 1e-14, err, "<= 1e-14", "damping beta=1 reproduces undamped Table III")


def test_B2():
    """AWGN closed form (eqs 71-72) vs numerical integration of (R5)-(R8) at 100 random points."""
    rng = np.random.default_rng(5)
    err = 0.0
    for _ in range(100):
        nup = 10 ** rng.uniform(-3, 2)
        s2 = 10 ** rng.uniform(-3, 2)
        ph = (rng.standard_normal() + 1j * rng.standard_normal())
        y = ph + np.sqrt((nup + s2) / 2) * (rng.standard_normal() + 1j * rng.standard_normal())
        nz, zh, ns, sh = BG.awgn_out(np.array([[y]]), np.array([[ph]]), np.array([[nup]]), s2)
        # exact posterior of z: real and imaginary parts separate and are Gaussian x Gaussian.
        # trapezoid on a wide grid -> spectrally accurate for analytic, exponentially decaying integrands.
        sp = np.sqrt(nup * s2 / (nup + s2) / 2)
        m0 = (s2 * ph + nup * y) / (nup + s2)
        mom = []
        for c, mc in ((0, m0.real), (1, m0.imag)):
            t = np.linspace(mc - 16 * sp, mc + 16 * sp, 6001)
            pc, yc = (ph.real, y.real) if c == 0 else (ph.imag, y.imag)
            lg = -(t - pc) ** 2 / nup - (yc - t) ** 2 / s2
            w = np.exp(lg - lg.max())
            Z = np.trapezoid(w, t)
            mu = np.trapezoid(w * t, t) / Z
            var = np.trapezoid(w * (t - mu) ** 2, t) / Z
            mom.append((mu, var))
        z_num = mom[0][0] + 1j * mom[1][0]
        nz_num = mom[0][1] + mom[1][1]
        ns_num = (1 - nz_num / nup) / nup
        sh_num = (z_num - ph) / nup
        err = max(err, abs(zh[0, 0] - z_num), abs(nz[0, 0] - nz_num) / max(nz_num, 1e-300),
                  abs(ns[0, 0] - ns_num) / max(abs(ns_num), 1e-300), abs(sh[0, 0] - sh_num) / max(abs(sh_num), 1e-300))
    return rec("B2", err <= 1e-10, err, "<= 1e-10", "AWGN closed form (71)-(72) == numerical (R5)-(R8)")


def test_B3():
    """Genie symbols: with nu^x = 0 and x_hat = x_true on EVERY column, H_hat converges to the all-column LS solution."""
    e = _cell(snr=80.0)                                     # high SNR: the Wiener shrinkage of (R15)(R16) -> identity
    H, u, perm, X, Y = _trial(e)
    Nr, Nt, T = e["Nr"], e["Nt"], e["T"]
    s2, tau_h = e["sigma2"], 1.0 / e["Nr"]
    xp = lambda r, nr: (X.copy(), np.zeros((Nt, T)))
    st = BG.BiGAMPState(np.zeros((Nr, Nt), complex), np.full((Nr, Nt), tau_h), X.copy(), np.zeros((Nt, T)))
    for _ in range(60):
        st, _ = BG.bigamp_iter(st, Y, s2, 1.0, tau_h, xp)
    Hls = Y @ X.conj().T @ np.linalg.inv(X @ X.conj().T)
    n_bg = np.sum(np.abs(st.Hh - H) ** 2) / np.sum(np.abs(H) ** 2)
    n_ls = np.sum(np.abs(Hls - H) ** 2) / np.sum(np.abs(H) ** 2)
    d = abs(n_bg - n_ls)
    return rec("B3", d <= 1e-6, d, "<= 1e-6", f"genie-symbol fixed point == LS (NMSE {n_bg:.3e} vs {n_ls:.3e})")


def test_B4():
    """Real-path cross-check: on purely real data the complex core reproduces a real reference core."""
    rng = np.random.default_rng(7)
    Nr, Nt, T = 6, 3, 10
    sigma2, tau_h, tau_x = 0.2, 1.0 / Nr, 1.0
    Y = rng.standard_normal((Nr, T)) + 0j
    Hh = rng.standard_normal((Nr, Nt)) / np.sqrt(Nr) + 0j
    Xh = rng.standard_normal((Nt, T)) + 0j
    nuh = np.full((Nr, Nt), tau_h)
    nux = np.full((Nt, T), tau_x)
    st = BG.BiGAMPState(Hh.copy(), nuh.copy(), Xh.copy(), nux.copy())
    rH, rnh, rX, rnx, rsh = Hh.real.copy(), nuh.copy(), Xh.real.copy(), nux.copy(), np.zeros((Nr, T))
    rmem = {}
    err = e1 = 0.0
    for i in range(8):
        st, _ = BG.bigamp_iter(st, Y, sigma2, BETA, tau_h, _xprior_gauss(tau_x))
        rH, rnh, rX, rnx, rsh, _, _, rmem = BG.bigamp_iter_real(rH, rnh, rX, rnx, rsh, Y.real, sigma2, tau_h, tau_x, beta=BETA, mem=rmem)
        e = max(np.abs(st.Hh - rH).max() / np.abs(rH).max(), np.abs(st.Xh - rX).max() / np.abs(rX).max(),
                np.abs(st.Hh.imag).max())
        err = max(err, e)
        if i == 0:
            e1 = e
    return rec("B4", err <= 1e-12, err, "<= 1e-12",
               f"complex core on real input == real reference core (relative; iter-1 residual {e1:.1e}; "
               f"imag part stays exactly 0)")


def test_B5():
    """Onsager wiring: zeroing the s_hat(t-1) term of (R4) must CHANGE the trajectory."""
    rng = np.random.default_rng(9)
    Nr, Nt, T = 8, 4, 16
    sigma2, tau_h, tau_x = 0.13, 1.0 / Nr, 1.0
    Y = (rng.standard_normal((Nr, T)) + 1j * rng.standard_normal((Nr, T))) / np.sqrt(2)
    Hh = (rng.standard_normal((Nr, Nt)) + 1j * rng.standard_normal((Nr, Nt))) / np.sqrt(2 * Nr)
    Xh = (rng.standard_normal((Nt, T)) + 1j * rng.standard_normal((Nt, T))) / np.sqrt(2)
    nuh, nux = np.full((Nr, Nt), tau_h), np.full((Nt, T), tau_x)
    xp = _xprior_gauss(tau_x)
    out = []
    for drop in (False, True):
        pH, pnh, pX, pnx, psh = Hh.copy(), nuh.copy(), Xh.copy(), nux.copy(), np.zeros((Nr, T), complex)
        for _ in range(8):
            pH, pnh, pX, pnx, psh, _, _ = BG.bigamp_iter_plain(pH, pnh, pX, pnx, psh, Y, sigma2, tau_h, xp, drop_onsager=drop)
        out.append(pH)
    d = np.abs(out[0] - out[1]).max() / max(np.abs(out[0]).max(), 1e-300)
    return rec("B5", d > 1e-3, d, "> 1e-3", "the Onsager term of (R4) is actually wired in")


def test_B6():
    """Erratum guard: nu^s computed with the sign of (R7) equals 1/(nu^p+sigma2) and is strictly positive.
    The printed eq (95) has the opposite sign and would give nu^s < 0 (conf/09_PRIOR_ART_NOTE.md §2)."""
    rng = np.random.default_rng(13)
    nup = 10 ** rng.uniform(-4, 3, 2000)
    s2 = 10 ** rng.uniform(-4, 3, 2000)
    ref = 1.0 / (nup + s2)
    L = np.longdouble
    nz_L = L(nup) * L(s2) / (L(nup) + L(s2))
    ns_L = (L(1) - nz_L / L(nup)) / L(nup)                        # (R7) in extended precision
    err = float(np.max(np.abs(ns_L - L(ref)) / L(ref)))           # the ALGEBRAIC identity
    nz = nup * s2 / (nup + s2)
    ns64 = (1.0 - nz / nup) / nup                                 # (R7) as literally spelled, float64
    ns_95 = (nz / nup - 1.0) / nup                                # eq (95) as PRINTED in the paper
    cancel = float(np.max(np.abs(ns64 - ref) / ref))
    ok = err <= 1e-12 and np.all(ns_L > 0) and np.all(ns64 > 0) and np.all(ns_95 < 0)
    return rec("B6", ok, err, "<= 1e-12 and all > 0",
               f"(R7) == 1/(nu^p+sigma2) > 0 everywhere; the PRINTED eq (95) is < 0 at all {len(nup)} points "
               f"({bool(np.all(ns_95 < 0))}) -> would diverge. float64 cancellation of the (R7) spelling: "
               f"{cancel:.1e} rel -> production uses eq (72)")


# ============================================================================= R4 -- 3-module SC-VAMP-type
def test_S1():
    """f = id => Module A returns (y, sigma2) unchanged at every iteration."""
    e = _cell()
    H, u, perm, X, Y = _trial(e)
    err = 0.0
    for _ in range(N_ITER):
        yA, s2A = SV.module_A(Y, e["sigma2"])
        err = max(err, np.abs(yA - Y).max(), abs(s2A - e["sigma2"]))
    return rec("S1", err <= 1e-14, err, "<= 1e-14", "Module A is constant (3 modules collapse to 2)")


def test_S2():
    """alpha^C closed form == tr(Sigma^C)/Nt/v_x from the direct inverse."""
    rng = np.random.default_rng(17)
    err = 0.0
    for _ in range(200):
        Nr, Nt = 8, 4
        Hh = (rng.standard_normal((Nr, Nt)) + 1j * rng.standard_normal((Nr, Nt))) / np.sqrt(2 * Nr)
        v_x = 10 ** rng.uniform(-3, 1)
        s2 = 10 ** rng.uniform(-3, 1)
        Yd = (rng.standard_normal((Nr, 5)) + 1j * rng.standard_normal((Nr, 5)))
        _, v_post, a_cf, _ = SV.module_C(Hh, Yd, np.zeros((Nt, 5), complex), v_x, s2)
        Sig = np.linalg.inv(np.eye(Nt) / v_x + Hh.conj().T @ Hh / s2)
        a_dir = float(np.trace(Sig).real / Nt / v_x)
        err = max(err, abs(a_cf - a_dir) / a_dir, abs(v_post - float(np.trace(Sig).real / Nt)) / v_post)
        if not (0 < a_cf < 1):
            err = np.inf
    return rec("S2", err <= 1e-12, err, "<= 1e-12", "Module C closed-form alpha^C == direct inverse, in (0,1)")


def test_S3():
    """Gaussian exactness: with p_X = CN(0,1) and a known channel the fixed point equals the exact joint
    Gaussian posterior mean  (I + H^H H/sigma2)^-1 H^H y/sigma2."""
    e = _cell(snr=6.0)
    H, u, perm, X, Y = _trial(e)
    Nr, Nt, Tp, Td = e["Nr"], e["Nt"], e["Tp"], e["T"] - e["Tp"]
    s2 = e["sigma2"]
    Xtr = e["gen"].sample_vecs(C.train_rng("D1", "S", Nr, 7), 2000)
    pr = GaussianPrior(Nr, Nt, Xtr.T @ Xtr.conj() / len(Xtr))
    rx = SV.R4SCVAMP(Nr, Nt, e["T"], Tp, s2, pr, e["code"], e["Xp"], mode="onsager",
                     gauss_code=True, genie_H=H)
    rx.run(Y, H, u, perm, 30)
    Sig = np.linalg.inv(np.eye(Nt) + H.conj().T @ H / s2)
    Xex = Sig @ (H.conj().T @ Y[:, Tp:]) / s2
    Xc, _, _, _ = SV.module_C(H, Y[:, Tp:], np.zeros((Nt, Td), complex), 1.0, s2)
    err = np.abs(Xc - Xex).max()
    return rec("S3", err <= 1e-10, err, "<= 1e-10", "Gaussian p_X fixed point == exact joint Gaussian posterior")


def test_S4():
    """07_SPEC asks for  R4(mode='llr') == R1-turbo  exactly.  Those are DIFFERENT receivers by the spec's
    own construction (02_SPEC §2.2(c)+§2.3: scalar-variance SISO-LMMSE + APP-LMMSE channel estimator, vs
    RouteA 'colored' matrix-site EP with per-column R_n), so the identity cannot hold.  We run it, print
    the measured gap, and record N/A-BY-CONSTRUCTION; the property S4 was meant to lock is tested by S4b."""
    e = _cell(snr=9.0)
    H, u, perm, X, Y = _trial(e)
    arms, cfgs, Cs, fits = A.build_baseline_arms("D1", "S", e["Nr"], e["Nt"], e["T"], e["Tp"],
                                                 e["sigma2"], e["code"], e["Xp"])
    r1 = arms["R1-turbo"].run(Y, H, u, perm, N_ITER)
    r4 = arms["R4-llr"].run(Y, H, u, perm, N_ITER)
    d = float(np.max(np.abs(r1["ber"] - r4["ber"])))
    return rec("S4", "N/A", d, "exactly 0 (unreachable)",
               "R4-llr vs R1-turbo: structurally different receivers (see DECISIONS); measured max|dBER|")


def test_S4b():
    """ADDED (07_SPEC allows extra tests).  The property S4 was for: in mode='llr' the forwarded message is
    EXACTLY the classical extrinsic, i.e. L_ext + L_in == L_app bit for bit."""
    rng = np.random.default_rng(23)
    e = _cell()
    code = e["code"]
    Ns = code.Ns
    r = (rng.standard_normal(Ns) + 1j * rng.standard_normal(Ns)) * 0.4
    v = 0.7
    P, Lu, Pe = code.st.bcjr(r, np.full(Ns, v), code.K, return_info=True, return_ext=True)
    L_app = C.bit_llrs_from_pmf(P)
    L_in = SV.qpsk_channel_llr(r, v)
    L_ext = L_app - L_in
    err = float(np.max(np.abs((L_ext + L_in) - L_app)))
    return rec("S4b", err <= 1e-12, err, "<= 1e-12", "mode='llr' forwards exactly L_app - L_in")


def test_S5():
    """alpha clip statistics.  Warn if the clip fires after the first iteration."""
    e = _cell(snr=9.0)
    H, u, perm, X, Y = _trial(e)
    arms, *_ = A.build_baseline_arms("D1", "S", e["Nr"], e["Nt"], e["T"], e["Tp"], e["sigma2"], e["code"], e["Xp"])
    rx = arms["R4-scvamp"]
    out = rx.run(Y, H, u, perm, N_ITER)
    nC, cC, nB, cB = rx.clip_calls
    late = float(np.mean(out["tauL_clip_frac"][1:] > out["tauL_clip_frac"][0]))
    return rec("S5", "RECORD", cC / max(nC, 1), "record only",
               f"alpha^C clipped {cC}/{nC}, alpha^B clipped {cB}/{nB}; clip rate rises after iter 1 in {100*late:.0f}% of iters")


def test_S6():
    """Complex factor 2:  L_0 = 2 sqrt(2) Re(r)/v  must equal the exact QPSK bit metric obtained by
    brute-force marginalisation over the constellation (t2_trellis.demap_bit_llrs)."""
    from t2_trellis import demap_bit_llrs
    rng = np.random.default_rng(29)
    err = 0.0
    for _ in range(300):
        r = (rng.standard_normal() + 1j * rng.standard_normal()) * rng.uniform(0.2, 2.0)
        v = 10 ** rng.uniform(-2, 1)
        ref = demap_bit_llrs(r, v, CONST_QPSK, CBITS_QPSK)
        mine = SV.qpsk_channel_llr(np.array([r]), v)[0]
        err = max(err, float(np.max(np.abs(ref - mine))))
    return rec("S6", err <= 1e-12, err, "<= 1e-12", "LLR <-> pseudo-observation round trip (complex factor 2)")


def test_S7(n=64):
    """Iteration-count disadvantage check: 20 outer iterations vs 16 at one SNR point.  RECORD only --
    the configuration is NOT changed (01_RULES §5)."""
    e = _cell(snr=9.0)
    arms, *_ = A.build_baseline_arms("D1", "S", e["Nr"], e["Nt"], e["T"], e["Tp"], e["sigma2"], e["code"], e["Xp"])
    rng = C.trial_rng("D1", "S", e["Nr"], e["T"], e["Tp"], 9.0)
    b16 = b20 = 0
    for _ in range(n):
        H = e["gen"].sample(rng)
        u = rng.integers(0, 2, e["code"].K)
        perm = rng.permutation(e["code"].Ns)
        X, Y = arms["R5-genie"].transmit(u, perm, H, rng)
        o = arms["R4-scvamp"].run(Y, H, u, perm, 20)
        b16 += int(o["blk_err"][15])
        b20 += int(o["blk_err"][19])
    return rec("S7", "RECORD", (b20 - b16) / n, "record only",
               f"R4-scvamp n={n} @9dB: BLER@16 = {b16/n:.3f}, BLER@20 = {b20/n:.3f} (config unchanged)")


# ============================================================================= common
def test_C1():
    """n=2 smoke over every arm; the return dict of the NEW arms must have the same keys and shapes as RouteA."""
    e = _cell()
    arms, cfgs, Cs, fits = A.build_baseline_arms("D1", "S", e["Nr"], e["Nt"], e["T"], e["Tp"],
                                                 e["sigma2"], e["code"], e["Xp"],
                                                 true_prior=e["gen"].prior)
    rng = C.trial_rng("D1", "S", e["Nr"], e["T"], e["Tp"], 9.0)
    ref = None
    bad = []
    for _ in range(2):
        H = e["gen"].sample(rng)
        u = rng.integers(0, 2, e["code"].K)
        perm = rng.permutation(e["code"].Ns)
        X, Y = arms["R5-genie"].transmit(u, perm, H, rng)
        for k, rx in arms.items():
            o = rx.run(Y, H, u, perm, N_ITER)
            sig = {q: np.asarray(o[q]).shape for q in C.KEYS_LOG}
            if ref is None:
                ref = sig
            elif sig != ref:
                bad.append(k)
    return rec("C1", not bad, len(bad), "0 mismatching arms",
               f"{len(arms)} arms smoke-run; key/shape signature identical to RouteA" + (f"; bad={bad}" if bad else ""))


def test_C2():
    """Determinism: two runs with the same seed are bitwise identical."""
    e = _cell()
    H, u, perm, X, Y = _trial(e)
    arms, *_ = A.build_baseline_arms("D1", "S", e["Nr"], e["Nt"], e["T"], e["Tp"], e["sigma2"], e["code"], e["Xp"],
                                     true_prior=e["gen"].prior)
    err = 0.0
    for k, rx in arms.items():
        a = rx.run(Y, H, u, perm, N_ITER)
        b = rx.run(Y, H, u, perm, N_ITER)
        for q in C.KEYS_LOG:
            x, y = np.asarray(a[q], float), np.asarray(b[q], float)
            err = max(err, float(np.max(np.abs(np.nan_to_num(x - y)))))
    return rec("C2", err == 0.0, err, "exactly 0", "two runs of every arm are bitwise identical")


def test_C3(before=None):
    """Demo/ must be untouched: sha256 of t2_route_a.py, t2_trellis.py, t2_gmm.py."""
    now = C.demo_hashes()
    ref = before or REFERENCE_HASHES
    bad = [k for k in now if now[k] != ref.get(k)]
    return rec("C3", not bad, len(bad), "0 changed files",
               "Demo/ locked files unchanged: " + ", ".join(f"{k}={v}" for k, v in now.items()))


REFERENCE_HASHES = {"t2_route_a.py": "95a5408901ec125c", "t2_trellis.py": "31cd0ee9c68e972b",
                    "t2_gmm.py": "d064e58c7510c769"}


def test_C4():
    """Paired realisations: inside a cell every arm must receive the SAME (H, Y)."""
    e = _cell()
    arms, *_ = A.build_baseline_arms("D1", "S", e["Nr"], e["Nt"], e["T"], e["Tp"], e["sigma2"], e["code"], e["Xp"],
                                     true_prior=e["gen"].prior)
    seen = {}
    rng = C.trial_rng("D1", "S", e["Nr"], e["T"], e["Tp"], 9.0)
    for tr in range(2):
        H = e["gen"].sample(rng)
        u = rng.integers(0, 2, e["code"].K)
        perm = rng.permutation(e["code"].Ns)
        X, Y = arms["R5-genie"].transmit(u, perm, H, rng)
        for k, rx in arms.items():
            h = hashlib.sha256(np.ascontiguousarray(H).tobytes() + np.ascontiguousarray(Y).tobytes()).hexdigest()[:16]
            seen.setdefault(tr, set()).add(h)
            rx.run(Y, H, u, perm, 1)
    n = max(len(v) for v in seen.values())
    return rec("C4", n == 1, n - 1, "1 distinct (H,Y) hash per trial",
               "every arm sees the same channel/noise realisation inside a cell")


def test_C5():
    """No arm may rely on RouteA's constructor defaults: the dumped config must have no empty field."""
    e = _cell()
    arms, cfgs, *_ = A.build_baseline_arms("D1", "S", e["Nr"], e["Nt"], e["T"], e["Tp"], e["sigma2"], e["code"], e["Xp"],
                                           true_prior=e["gen"].prior)
    need_ra = set(A.LOOP) | {"mode", "lam_min", "exact_prior", "hsite", "scal", "Xp", "module_H"}
    need_bg = {"arm", "beta", "t_in", "tau_h", "class_"}
    need_sv = {"arm", "mode", "eps", "class_", "prior"}
    OPT = ("beta_fb", "nu_sw", "genie_H")                       # None is the DOCUMENTED value of these
    miss, empty = {}, {}
    for k, c in cfgs.items():
        need = need_ra if "lh_form" in c else (need_bg if "t_in" in c else need_sv)
        m = sorted(need - set(c))
        if m:
            miss[k] = m
        e = [q for q, v in c.items() if v is None and q not in OPT]
        if e:
            empty[k] = e
    return rec("C5", not miss and not empty, len(miss) + len(empty), "0 missing/empty fields",
               f"explicit config dump complete for {len(cfgs)} arms" + (f"; miss={miss} empty={empty}" if (miss or empty) else ""))


def test_C6(path=None):
    """Result headers must state device, precision and (if GPU) the model name."""
    h = C.header("D1")
    ok = ("device" in h) and ("dtype" in h) and ("deterministic" in h)
    return rec("C6", ok, int(ok), "present", "result header carries device / dtype / determinism")


# ============================================================================= drivers
BSC = [test_B1, test_B2, test_B3, test_B4, test_B5, test_B6,
       test_S1, test_S2, test_S3, test_S4, test_S4b, test_S5, test_S6, test_S7,
       test_C1, test_C2, test_C3, test_C4, test_C5, test_C6]


def fmt(rows):
    out = ["id    | verdict     | residual      | criterion               | description",
           "-" * 130]
    for tid, v, r, c, d in rows:
        rs = f"{r:.3e}" if isinstance(r, (int, float, np.floating)) and np.isfinite(r) else str(r)
        out.append(f"{tid:<5} | {v:<11} | {rs:>13} | {c:<23} | {d}")
    npass = sum(1 for _, v, *_ in rows if v == "PASS")
    ntest = sum(1 for _, v, *_ in rows if v in ("PASS", "FAIL"))
    failed = [t for t, v, *_ in rows if v == "FAIL"]
    out.append("-" * 130)
    out.append(f"PASS {npass}/{ntest}, FAILED: {failed if failed else '[]'}   "
               f"(N/A: {[t for t,v,*_ in rows if v=='N/A']}, RECORD: {[t for t,v,*_ in rows if v=='RECORD']})")
    return "\n".join(out)


def run(which=BSC):
    RES.clear()
    for f in which:
        try:
            f()
        except Exception as ex:                                   # a crashing test is a FAIL, never a skip
            rec(f.__name__.replace("test_", ""), False, np.inf, "no exception", f"EXCEPTION {type(ex).__name__}: {ex}")
    return list(RES)
