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


# ============================================================================= M -- our model (03_SPEC §4)
def _our(e, with_G=True, score_prior=None):
    return A.build_our_arms("D1", "S", e["Nr"], e["Nt"], e["T"], e["Tp"], e["sigma2"], e["code"], e["Xp"],
                            true_prior=e["gen"].prior, with_G=with_G, score_prior=score_prior)


def _maxdiff(a, b):
    m = 0.0
    for q in C.KEYS_LOG:
        x, y = np.asarray(a[q], float), np.asarray(b[q], float)
        d = np.abs(x - y)
        d = d[np.isfinite(d)]
        if d.size:
            m = max(m, float(d.max()))
    return m


def _legacy_0925(e):
    """The EXISTING exp_0925 arms, built by exp_0925_run.make_arms itself (Demo/ is imported, not copied)."""
    import exp_0925_run as L
    c = dict(Nr=e["Nr"], T=e["T"], Tp=e["Tp"])
    true, arms, pil, v1, meta = L.make_arms("S", c["Nr"], c["T"], c["Tp"], e["sigma2"], e["code"], N_TRAIN)
    return true, arms, pil, meta


def test_M1():
    """The assembler's M-ours-gmm32 must reproduce the EXISTING exp_0925 'Hgmm-K32' arm bit for bit."""
    e = _cell(snr=9.0)
    H, u, perm, X, Y = _trial(e)
    true, legacy, pil, meta = _legacy_0925(e)
    assert pil == e["pil"], f"pilot type differs: {pil} vs {e['pil']}"
    arms, cfgs, m2, hp, fits = _our(e)
    d = _maxdiff(arms["M-ours-gmm32"].run(Y, H, u, perm, N_ITER), legacy["Hgmm-K32"].run(Y, H, u, perm, N_ITER))
    return rec("M1", d == 0.0, d, "exactly 0",
               f"assembler M-ours-gmm32 == Demo/exp_0925 'Hgmm-K32' (b* = {m2['bstar']}, legacy b* = {meta['bstar']})")


def test_M1b():
    """ADDED: the same identity for the oracle score arm (M-ours-score == exp_0925 'Hscore-exact')."""
    e = _cell(snr=9.0)
    H, u, perm, X, Y = _trial(e)
    true, legacy, pil, meta = _legacy_0925(e)
    arms, *_ = _our(e)
    d = _maxdiff(arms["M-ours-score"].run(Y, H, u, perm, N_ITER), legacy["Hscore-exact"].run(Y, H, u, perm, N_ITER))
    return rec("M1b", d == 0.0, d, "exactly 0", "assembler M-ours-score == Demo/exp_0925 'Hscore-exact'")


def test_M2():
    """*** THE test.  Turn Module H back into a Gaussian (sample covariance) and the assembler must
    reproduce R2-ours-G exactly -- i.e. the ONLY difference between R2 and M-ours-* is Module H."""
    e = _cell(snr=9.0)
    H, u, perm, X, Y = _trial(e)
    base, *_ = A.build_baseline_arms("D1", "S", e["Nr"], e["Nt"], e["T"], e["Tp"], e["sigma2"], e["code"], e["Xp"],
                                     true_prior=e["gen"].prior)
    arms, *_ = _our(e)
    d = _maxdiff(arms["M-ours-G"].run(Y, H, u, perm, N_ITER), base["R2-ours-G"].run(Y, H, u, perm, N_ITER))
    return rec("M2", d == 0.0, d, "exactly 0",
               "M-ours-G (Module H -> Gaussian) == R2-ours-G: the headline gap is Module H's alone")


def test_M2b():
    """ADDED: the same statement through the MIXTURE code path -- a K=1 GMM prior driving the exact
    mixture-EP site must also reduce to R2-ours-G.  This exercises ep_site(), which M2 bypasses."""
    e = _cell(snr=9.0)
    H, u, perm, X, Y = _trial(e)
    base, _, Cs, fits = A.build_baseline_arms("D1", "S", e["Nr"], e["Nt"], e["T"], e["Tp"], e["sigma2"], e["code"], e["Xp"])
    g1 = C.GMMPriorB(e["Nr"], e["Nt"], np.asarray(fits[("full", 32)]["Chat"])[None], np.array([1.0]))
    rx = A.route_a(e["Nr"], e["Nt"], e["T"], e["Tp"], e["sigma2"], g1.view("eta"), e["code"], e["Xp"], "gmm_site")
    d = _maxdiff(rx.run(Y, H, u, perm, N_ITER), base["R2-ours-G"].run(Y, H, u, perm, N_ITER))
    return rec("M2b", d <= 1e-10, d, "<= 1e-10", "K=1 mixture-EP site reduces to the Gaussian arm (ep_site path)")


def test_M3():
    """EM identity  sum_k pi_k C_k = sample covariance.  Exact only for floor = 0 and kappa = 0 (t2_gmm
    docstring), so it is tested there; the deviation of the SHIPPED fits (floor 1e-4, MAP shrinkage) is
    measured and reported, not hidden."""
    from t2_gmm import fit_gmm_em
    e = _cell()
    X = e["gen"].sample_vecs(C.train_rng("D1", "S", e["Nr"], 7), 2000)
    Chat = X.T @ X.conj() / len(X)
    f = fit_gmm_em(X, 8, np.random.default_rng(31), n_iter=12, floor=0.0, kappa=0.0)
    S = np.einsum("k,kij->ij", f["pi"], f["covs"])
    err = float(np.max(np.abs(S - Chat)) / np.max(np.abs(Chat)))
    _, fits, llv, bstar, kron_K = A.module_h_priors("D1", "S", e["Nr"], e["Nt"])
    z = fits[("full", 32)]
    Sd = np.einsum("k,kij->ij", z["pi"], z["covs"])
    dev = float(np.max(np.abs(Sd - z["Chat"])) / np.max(np.abs(z["Chat"])))
    ok = err <= 1e-12 and f["n_reseed"] == 0
    return rec("M3", ok, err, "<= 1e-12",
               f"sum_k pi_k C_k == sample covariance for floor=0,kappa=0 (reseeds {f['n_reseed']}); "
               f"shipped K=32 fit (floor 1e-4, kappa {int(z['kappa'])}) deviates by {dev:.2e} rel -- by design")


def test_M4():
    """The dumped config must agree with the conf/03_SPEC_ourmodel.md §1.1 table field by field."""
    e = _cell()
    arms, cfgs, *_ = _our(e)
    bad = {}
    for k, c in cfgs.items():
        for q, want in A.SPEC_TABLE_11.items():
            got = N_ITER if q == "iters" else c.get(q, "<missing>")
            if q == "clip" and c.get("module_H") == "gaussian":
                continue                                       # the Gaussian arm has no site clip
            if got != want:
                bad.setdefault(k, []).append(f"{q}: {got!r} != {want!r}")
    return rec("M4", not bad, len(bad), "0 mismatching arms",
               f"config dump of {len(cfgs)} M-ours arms matches 03_SPEC §1.1" + (f"; {bad}" if bad else ""))


M_TESTS = [test_M1, test_M1b, test_M2, test_M2b, test_M3, test_M4]


# ============================================================================= L -- lemma reproduction (A3)
def test_L1():
    """Re-running Demo/archive/exp_0915_bcjr_score_check.py UNMODIFIED reproduces the recorded magnitudes
    for (133,171)_8:  max|tanh - E| <= 1e-14  and  Tweedie finite-difference error <= 1e-9."""
    import lemma as LM
    import os
    txt = open(os.path.join(C.CONF, "logs", "lemma.log")).read()
    t, tw, lc4, lc2, rows, crows = LM.parse(txt)
    ok = t <= 1e-14 and tw <= 1e-9
    return rec("L1", ok, max(t, tw / 1e5), "tanh <= 1e-14 and FD <= 1e-9",
               f"(133,171)_8: max|tanh(L/2) - E[x|x~]| = {t:.2e}, max Tweedie FD error = {tw:.2e} "
               f"(recorded in 03_SPEC §6: 2.3e-15 / 6.9e-10)")


def test_L2():
    """Complex convention: L_c = 4/sigma_c^2 is exact and 2/sigma_c^2 is wrong -- the guard for every
    complex implementation in conf/ (02_SPEC §0)."""
    import lemma as LM
    import os
    txt = open(os.path.join(C.CONF, "logs", "lemma.log")).read()
    t, tw, lc4, lc2, rows, crows = LM.parse(txt)
    ok = lc4 <= 1e-12 and lc2 > 1e-3
    return rec("L2", ok, lc4, "Lc=4 <= 1e-12 and Lc=2 > 1e-3",
               f"L_c = 4/sigma_c^2 error {lc4:.2e} (exact); L_c = 2/sigma_c^2 error up to {lc2:.2e} (wrong)")


L_TESTS = [test_L1, test_L2]


# ============================================================================= D -- diffusion training evidence (A5)
# conf/07_SPEC_tests.md section D.  These do NOT judge the score model -- GA-GD do that.  They judge whether
# TRAINING ACTUALLY HAPPENED, which is what makes "no rung reached the gates" an admissible conclusion rather
# than an excuse (conf/00_GOAL.md §4 item 3, conf/01_RULES.md §5).
import glob
import os
import re

LADDER_ROW = re.compile(
    r"^\[(?P<ts>[^\]]+)\]\s*(?P<rung>L\d)\s*\|\s*a(?P<att>\d+)\s*\|(?P<cfg>[^|]*)\|"
    r"\s*train\s*(?P<tr>[^/]+)/\s*val\s*(?P<va>[^|]*)\|(?P<gates>.*?)\|\s*(?P<verdict>[A-Z/-]+)\s*\|(?P<note>.*)$")


def _is_gate_row(r):
    """A gate row records GA-GD for an already-trained attempt; it has no epochs, device or wall-clock
    because nothing was trained when it was written.  Only TRAIN rows are training evidence."""
    return "GATED from" in r.get("note", "")


def _ladder_rows(path=None):
    path = path or os.path.join(C.CONF, "LADDER.md")
    if not os.path.exists(path):
        return []
    out = []
    for line in open(path):
        m = LADDER_ROW.match(line.strip())
        if m:
            out.append(m.groupdict())
    return out


def test_D0():
    """The sigma_t grid was MEASURED, not chosen: sigma_grid.txt exists and carries its basis distribution."""
    p = os.path.join(C.CONF, "results", "sigma_grid.txt")
    if not os.path.exists(p):
        return rec("D0", False, np.inf, "file exists", "conf/results/sigma_grid.txt absent -- A4 not run")
    t = open(p).read()
    need = ("empirical distribution of nu_q", "CHOSEN GRID", "percentile", "per cell x SNR")
    miss = [k for k in need if k not in t]
    npz = os.path.join(C.CONF, "results", "sigma_grid_D1.npz")
    n = int(np.load(npz)["nu"].size) if os.path.exists(npz) else 0
    return rec("D0", not miss and n >= 10, len(miss), "0 missing sections, >= 10 points",
               f"sigma_grid.txt present with the measured basis distribution; {n} grid points"
               + (f"; MISSING {miss}" if miss else ""))


def test_D1t():
    """Train/validation split identical across EVERY ladder attempt (split_hash compared, not assumed)."""
    rows = _ladder_rows()
    hs = sorted({m.group(1) for r in rows for m in [re.search(r"split ([0-9a-f]{8,})", r["note"])] if m})
    import score
    live = score.training_split("D1", "S", 8, 4)[2]
    ok = len(hs) <= 1 and (not hs or hs[0] == live)
    return rec("D1t", ok, len(hs) if len(hs) != 1 else 0, "exactly 1 distinct split hash",
               f"{len(rows)} ladder rows, split hashes {hs or '[]'}; live training_split hash {live}")


def test_D2t():
    """The diffusion saw the SAME N_train samples the GMM fit received (element-wise, not just the same count)."""
    import arms
    import score
    X = arms.training_set("D1", "S", 8, 4)
    Xtr, Xva, h, _ = score.training_split("D1", "S", 8, 4)
    n = len(Xtr) + len(Xva)
    pack = np.concatenate([Xtr, Xva], 0) if Xva.ndim == Xtr.ndim else Xtr
    same_n = (n == len(X) == C.N_TRAIN)
    # the split is a permutation of the one dataset: compare multisets by sorted flat magnitude+phase
    a = np.sort_complex(np.asarray(X).reshape(-1))
    b = np.sort_complex(np.asarray(pack).reshape(-1))
    d = float(np.max(np.abs(a - b))) if a.shape == b.shape else np.inf
    return rec("D2t", same_n and d <= 1e-12, d, "same N_train and identical samples",
               f"GMM training set n={len(X)}; diffusion train {len(Xtr)} + val {len(Xva)} = {n} "
               f"(N_train={C.N_TRAIN}); max element difference {d:.1e}")


def test_D3t():
    """Every attempt that ran is in LADDER.md: one row per checkpoint, ABORTED rows included."""
    rows = _ladder_rows()
    cks = sorted(glob.glob(os.path.join(C.CONF, "ckpt", "*_D1.pt")))
    keys_log = {(r["rung"], int(r["att"])) for r in rows}
    keys_ck = set()
    for p in cks:
        m = re.search(r"(L\d)_a(\d+)_D1\.pt$", os.path.basename(p))
        if m:
            keys_ck.add((m.group(1), int(m.group(2))))
    missing = sorted(keys_ck - keys_log)
    return rec("D3t", not missing, len(missing), "0 checkpoints without a ladder row",
               f"{len(rows)} ladder rows, {len(cks)} checkpoints; every checkpoint has a row"
               + (f"; MISSING {missing}" if missing else ""))


def test_D4t():
    """TRAINING REALLY HAPPENED: the L1, L2, L3 checkpoints exist, load, and run a forward pass.
    conf/00_GOAL.md §4 item 3 names this test as the evidence."""
    import score
    import torch
    need = ("L1", "L2", "L3")
    got, sizes, errs = [], [], []
    for r in need:
        hit = sorted(glob.glob(os.path.join(C.CONF, "ckpt", f"{r}_a*_D1.pt")))
        if not hit:
            errs.append(f"{r}: no checkpoint")
            continue
        p = hit[0]
        try:
            st = torch.load(p, map_location="cpu", weights_only=False)
            m = score.make_model(r, st["hp"], 8, 4)
            m.load_state_dict(st["model"])
            m.eval()
            x = torch.zeros(2, 2 * 8 * 4, dtype=torch.get_default_dtype())
            s = torch.full((2,), 0.1, dtype=torch.get_default_dtype())
            with torch.no_grad():
                y = m.score_real(x, s) if hasattr(m, "score_real") else m.score(x, s)
            assert y.shape == x.shape, f"{r}: forward shape {tuple(y.shape)} != {tuple(x.shape)}"
            got.append(r)
            sizes.append(f"{r}={os.path.getsize(p) / 1e6:.1f}MB")
        except Exception as ex:
            errs.append(f"{r}: {type(ex).__name__}: {ex}")
    return rec("D4t", len(got) == 3, 3 - len(got), "L1, L2, L3 load + forward",
               f"loaded and ran {got}; {' '.join(sizes)}" + (f"; ERRORS {errs}" if errs else ""))


def test_D5t():
    """device, per-epoch wall-clock and total wall-clock are on record (LADDER row AND the training log)."""
    rows = [r for r in _ladder_rows() if not _is_gate_row(r)]      # gate rows carry no training fields
    bad = [f"{r['rung']}a{r['att']}" for r in rows
           if not (re.search(r"device \S", r["note"]) and re.search(r"s/ep", r["note"])
                   and re.search(r"\d+ ep", r["note"]))]
    logs = sorted(glob.glob(os.path.join(C.CONF, "logs", "train_L*_D1.log")))
    nolog = []
    for p in logs:
        t = open(p).read()
        # the header line is "# DEVICE : cuda | ..." and each epoch line carries its own wall-clock
        has_dev = re.search(r"device\s*:", t, re.I)
        has_ep = re.search(r"epoch\s+\d+\s*\|.*\|\s*[\d.]+\s*s", t)
        if not (has_dev and has_ep):
            nolog.append(os.path.basename(p) + ("(no device)" if not has_dev else "(no per-epoch time)"))
    try:
        import torch
        avail = torch.cuda.is_available()
    except Exception:
        avail = "n/a"
    return rec("D5t", not bad and not nolog and bool(rows), len(bad) + len(nolog),
               "every TRAIN row has device / s-per-epoch / epochs",
               f"torch.cuda.is_available()={avail}; {len(rows)} train rows "
               f"({len(_ladder_rows()) - len(rows)} gate rows excluded), {len(logs)} training logs"
               + (f"; ROWS MISSING FIELDS {bad}" if bad else "") + (f"; LOGS MISSING FIELDS {nolog}" if nolog else ""))


def test_D6t():
    """Every attempt was TRAINED ENOUGH to count: early-stopped on validation loss, or >= 200 epochs.
    Anything less is ABORTED and must not be counted as one of the 3 attempts (01_RULES §5)."""
    rows = [r for r in _ladder_rows() if not _is_gate_row(r)]      # gate rows are not training attempts
    short = []
    for r in rows:
        m = re.search(r"(\d+) ep", r["note"])
        ep = int(m.group(1)) if m else 0
        stopped = "stop: patience" in r["note"] or "patience" in r["note"]
        if not (stopped or ep >= 200) and "ABORTED" not in r["verdict"]:
            short.append(f"{r['rung']}a{r['att']}({ep} ep)")
    aborted = [f"{r['rung']}a{r['att']}" for r in rows if "ABORTED" in r["verdict"]]
    return rec("D6t", not short and bool(rows), len(short),
               "every non-ABORTED TRAIN row >= 200 ep or early-stopped",
               f"{len(rows)} train rows; ABORTED (not counted as attempts): {aborted or 'none'}"
               + (f"; UNDER-TRAINED BUT COUNTED {short}" if short else ""))


D_TESTS = [test_D0, test_D1t, test_D2t, test_D3t, test_D4t, test_D5t, test_D6t]
