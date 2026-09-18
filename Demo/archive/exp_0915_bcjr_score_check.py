#!/usr/bin/env python3
"""
exp_0915_bcjr_score_check.py  (T2, milestone M1: "BCJR-score check")

Checks, on a terminated rate-1/2 convolutional code with brute-force enumeration of all 2^K codewords:
  T1  real BPSK, x~ = x + sigma*eps, eps~N(0,1):  tanh(L_k/2) [BCJR, L_c = 2/sigma^2]  ==  E[x_k | x~]
  T2  Tweedie:  grad log p_t(x~)  ==  (E[x|x~] - x~)/sigma^2            (finite differences)
  T3  Jacobian: d E[x_k|x~]/d x~_j == Cov(x_k,x_j|x~)/sigma^2 ; diag == (1-tanh^2(L_k/2))/sigma^2
  T4  complex embedding (per-complex-entry variance sigma_c^2): L_c = 4/sigma_c^2 exact, 2/sigma_c^2 wrong;
      complex Tweedie with Wirtinger d/dz* = (d/dRe + j d/dIm)/2
  T5  Max-Log-MAP breaks exactness
  T6  puncturing handled as erasure (L_ch = 0) keeps exactness
  T7  16-QAM (Gray): bit-level pipeline (bit metrics -> BCJR -> product of marginals) vs exact
      vs symbol-level super-section BCJR
Conventions: bits 0->+1, 1->-1; L = log P(c=0)/P(c=1).  Seeds fixed.
"""
import numpy as np
from scipy.special import logsumexp

rng = np.random.default_rng(20260915)

# ---------------------------------------------------------------- trellis / encoder
def make_trellis(gens_oct, nu):
    """Feed-forward rate-1/n code. State = last nu inputs (msb = most recent).
    Generator octal string, msb tap = current input (standard convention, e.g. 133 = 1+D^2+D^3+D^5+D^6)."""
    gens = [int(g, 8) for g in gens_oct]
    S = 1 << nu
    nxt = np.zeros((S, 2), int)
    out = np.zeros((S, 2, len(gens)), int)
    for s in range(S):
        for u in range(2):
            reg = (u << nu) | s
            for i, g in enumerate(gens):
                out[s, u, i] = bin(reg & g).count("1") & 1
            nxt[s, u] = reg >> 1
    return nxt, out

def encode(u_info, nxt, out, nu):
    u = np.concatenate([u_info, np.zeros(nu, int)])
    s, c = 0, []
    for uk in u:
        c.append(out[s, uk]); s = nxt[s, uk]
    assert s == 0, "trellis not terminated"
    return np.concatenate(c)            # section-major order, length n*(K+nu)

def all_codewords(K, nxt, out, nu):
    U = ((np.arange(1 << K)[:, None] >> np.arange(K)[None, :]) & 1).astype(int)
    C = np.array([encode(u, nxt, out, nu) for u in U])
    return C, 1 - 2 * C                  # bits, BPSK symbols

# ---------------------------------------------------------------- BCJR (log domain, exact)
def bcjr(Lch, nxt, out, nu, K, maxlog=False):
    """Lch: (K+nu, n) channel LLRs of coded bits (a priori = 0 on info bits, tail forced to 0).
    Returns coded-bit a posteriori LLRs (K+nu, n)."""
    S = 1 << nu; Ksec, n = Lch.shape
    lse = (lambda a: np.max(a)) if maxlog else (lambda a: logsumexp(a))
    xs = 1 - 2 * out                                     # (S,2,n) in {+-1}
    gamma = 0.5 * np.einsum("sui,ki->ksu", xs, Lch)      # (Ksec,S,2): sum_i (x_i/2) Lch_i
    gamma[K:, :, 1] = -np.inf                            # known zero tail
    alpha = np.full((Ksec + 1, S), -np.inf); alpha[0, 0] = 0.0
    for k in range(Ksec):
        cand = alpha[k][:, None] + gamma[k]              # (S,2) indexed by (s',u)
        for s2 in range(S):
            v = cand[nxt == s2]
            alpha[k + 1, s2] = lse(v) if v.size else -np.inf
    beta = np.full((Ksec + 1, S), -np.inf); beta[Ksec, 0] = 0.0
    for k in range(Ksec - 1, -1, -1):
        b = gamma[k] + beta[k + 1][nxt]                  # (S,2)
        beta[k] = np.array([lse(b[s]) for s in range(S)])
    Lapp = np.zeros((Ksec, n))
    for k in range(Ksec):
        bp = alpha[k][:, None] + gamma[k] + beta[k + 1][nxt]   # branch log-posteriors (S,2)
        for i in range(n):
            Lapp[k, i] = lse(bp[out[:, :, i] == 0]) - lse(bp[out[:, :, i] == 1])
    return Lapp

# ---------------------------------------------------------------- brute force
def brute_real(xt, sigma2, X):
    ll = -np.sum((xt[None, :] - X) ** 2, axis=1) / (2 * sigma2)
    lZ = logsumexp(ll); w = np.exp(ll - lZ)
    m = w @ X
    cov = (X - m).T @ (w[:, None] * (X - m))
    logp = lZ - np.log(X.shape[0]) - 0.5 * X.shape[1] * np.log(2 * np.pi * sigma2)
    return m, cov, logp

def brute_complex(xt, sigma2c, X):
    ll = -np.sum(np.abs(xt[None, :] - X) ** 2, axis=1) / sigma2c
    lZ = logsumexp(ll); w = np.exp(ll - lZ)
    m = w @ X
    logp = lZ - np.log(X.shape[0]) - X.shape[1] * np.log(np.pi * sigma2c)
    return m, logp

def fd_grad(f, x, h=1e-5):
    g = np.zeros_like(x, dtype=float)
    for j in range(x.size):
        e = np.zeros_like(x, dtype=float); e[j] = h
        g[j] = (f(x + e) - f(x - e)) / (2 * h)
    return g

# ================================================================= T1-T3, T5: real BPSK
def run_real(gens, nu, K, sig2_list, trials=3):
    nxt, out = make_trellis(gens, nu); n = out.shape[2]; Ksec = K + nu
    C, X = all_codewords(K, nxt, out, nu); N = X.shape[1]
    print(f"\n[real BPSK] code {gens}_8, nu={nu}, K={K}: N={N} coded bits, {X.shape[0]} codewords")
    print(f"{'sigma^2':>8} {'max|tanh-E|':>12} {'score(FD)':>12} {'Jac(FD)':>12} {'diag vs BCJR':>13} {'div vs v/s2':>12} {'MaxLog err':>11}")
    for sig2 in sig2_list:
        e1 = e2 = e3 = e4 = e5 = e6 = 0.0
        for _ in range(trials):
            x = X[rng.integers(X.shape[0])]
            xt = x + np.sqrt(sig2) * rng.standard_normal(N)
            Lch = (2.0 / sig2) * xt.reshape(Ksec, n)                     # L_c = 2/sigma^2 (real)
            xb = np.tanh(bcjr(Lch, nxt, out, nu, K) / 2).reshape(-1)
            m, cov, _ = brute_real(xt, sig2, X)
            e1 = max(e1, np.abs(xb - m).max())
            score_fd = fd_grad(lambda z: brute_real(z, sig2, X)[2], xt)
            e2 = max(e2, np.abs(score_fd - (xb - xt) / sig2).max())
            jac_fd = np.array([fd_grad(lambda z: brute_real(z, sig2, X)[0][k], xt) for k in range(N)])
            e3 = max(e3, np.abs(jac_fd - cov / sig2).max())
            e4 = max(e4, np.abs(np.diag(jac_fd) - (1 - xb ** 2) / sig2).max())
            e5 = max(e5, abs(np.trace(jac_fd) / N - np.mean(1 - xb ** 2) / sig2))
            xml = np.tanh(bcjr(Lch, nxt, out, nu, K, maxlog=True) / 2).reshape(-1)
            e6 = max(e6, np.abs(xml - m).max())
        print(f"{sig2:8.3f} {e1:12.2e} {e2:12.2e} {e3:12.2e} {e4:13.2e} {e5:12.2e} {e6:11.2e}")
    return nxt, out, C, X

# ================================================================= T4: complex embedding
def run_complex(gens, nu, K, sig2c_list, trials=3):
    nxt, out = make_trellis(gens, nu); n = out.shape[2]; Ksec = K + nu
    C, X = all_codewords(K, nxt, out, nu); N = X.shape[1]
    print(f"\n[complex embedding] noise CN(0, sigma_c^2) per entry; BPSK on real axis")
    print(f"{'sigma_c^2':>9} {'Lc=4/s2 err':>12} {'Lc=2/s2 err':>12} {'cplx Tweedie':>13}")
    for sig2c in sig2c_list:
        e_ok = e_bad = e_tw = 0.0
        for _ in range(trials):
            x = X[rng.integers(X.shape[0])].astype(complex)
            xt = x + np.sqrt(sig2c / 2) * (rng.standard_normal(N) + 1j * rng.standard_normal(N))
            m, _ = brute_complex(xt, sig2c, X.astype(complex))
            xb_ok = np.tanh(bcjr((4.0 / sig2c) * xt.real.reshape(Ksec, n), nxt, out, nu, K) / 2).reshape(-1)
            xb_bad = np.tanh(bcjr((2.0 / sig2c) * xt.real.reshape(Ksec, n), nxt, out, nu, K) / 2).reshape(-1)
            e_ok = max(e_ok, np.abs(xb_ok - m.real).max()); e_bad = max(e_bad, np.abs(xb_bad - m.real).max())
            # complex Tweedie: E[x|xt] = xt + sigma_c^2 * d/dxt* log p,  d/dz* = (d/dRe + j d/dIm)/2
            f = lambda z: brute_complex(z, sig2c, X.astype(complex))[1]
            gr = fd_grad(lambda v: f(v + 1j * xt.imag), xt.real.copy())
            gi = fd_grad(lambda v: f(xt.real + 1j * v), xt.imag.copy())
            score_c = 0.5 * (gr + 1j * gi)
            e_tw = max(e_tw, np.abs(xt + sig2c * score_c - m).max())
        print(f"{sig2c:9.3f} {e_ok:12.2e} {e_bad:12.2e} {e_tw:13.2e}")

# ================================================================= T6: puncturing as erasure
def run_puncture(gens, nu, K, sig2_list, trials=3):
    nxt, out = make_trellis(gens, nu); n = out.shape[2]; Ksec = K + nu
    C, X = all_codewords(K, nxt, out, nu); N = X.shape[1]
    keep = np.ones((Ksec, n), bool); keep[1::2, 1] = False       # puncture 2nd output on odd sections (rate ~2/3)
    keep = keep.reshape(-1)
    print(f"\n[puncturing] {keep.sum()}/{N} bits transmitted; punctured positions get L_ch = 0")
    print(f"{'sigma^2':>8} {'tx symbols err':>15} {'punct. symbols err':>19}")
    for sig2 in sig2_list:
        e_tx = e_pn = 0.0
        for _ in range(trials):
            x = X[rng.integers(X.shape[0])]
            xt = x + np.sqrt(sig2) * rng.standard_normal(N)
            Lch = np.where(keep, (2.0 / sig2) * xt, 0.0).reshape(Ksec, n)
            xb = np.tanh(bcjr(Lch, nxt, out, nu, K) / 2).reshape(-1)
            # brute force with observations only at transmitted coordinates
            ll = -np.sum((xt[None, keep] - X[:, keep]) ** 2, axis=1) / (2 * sig2)
            w = np.exp(ll - logsumexp(ll)); m = w @ X
            e_tx = max(e_tx, np.abs(xb[keep] - m[keep]).max()); e_pn = max(e_pn, np.abs(xb[~keep] - m[~keep]).max())
        print(f"{sig2:8.3f} {e_tx:15.2e} {e_pn:19.2e}")

# ================================================================= T7: 16-QAM
PAM = np.array([-3, -1, 1, 3]) / np.sqrt(10)        # Gray: 00->-3, 01->-1, 11->+1, 10->+3
GRAY_IDX = {(0, 0): 0, (0, 1): 1, (1, 1): 2, (1, 0): 3}
def map16(bits4):                                    # bits (b0,b1)->I, (b2,b3)->Q
    return PAM[GRAY_IDX[(bits4[0], bits4[1])]] + 1j * PAM[GRAY_IDX[(bits4[2], bits4[3])]]
CONST = np.array([map16(((a >> 3) & 1, (a >> 2) & 1, (a >> 1) & 1, a & 1)) for a in range(16)])
CBITS = np.array([[(a >> 3) & 1, (a >> 2) & 1, (a >> 1) & 1, a & 1] for a in range(16)])

def demap_bit_llrs(r, tau):
    """BICM bit metrics without a priori: L_j = log sum_{a:b_j=0} e^{-|r-a|^2/tau} - log sum_{a:b_j=1} ..."""
    ll = -np.abs(r - CONST) ** 2 / tau
    return np.array([logsumexp(ll[CBITS[:, j] == 0]) - logsumexp(ll[CBITS[:, j] == 1]) for j in range(4)])

def soft_symbol_from_bit_llrs(L4):
    P0 = 1 / (1 + np.exp(-L4))
    Pa = np.prod(np.where(CBITS == 0, P0[None, :], 1 - P0[None, :]), axis=1)   # product of marginals
    xb = np.sum(Pa * CONST); v = np.sum(Pa * np.abs(CONST) ** 2) - abs(xb) ** 2
    return xb, v

def bcjr_symbol_level(r, tau, nxt, out, nu, K):
    """Super-section BCJR: one section = 2 info bits = 4 coded bits = one 16-QAM symbol (rate-1/2 code).
    Branch metric = exact symbol likelihood. Returns exact symbol posteriors P(x_n = a | r)."""
    assert K % 2 == 0 and nu % 2 == 0
    S = 1 << nu; Ksec2 = (K + nu) // 2
    nxt2 = np.zeros((S, 4), int); sym2 = np.zeros((S, 4), int)
    for s in range(S):
        for u in range(4):
            u1, u2 = u >> 1, u & 1
            s1 = nxt[s, u1]; s2 = nxt[s1, u2]
            b = np.concatenate([out[s, u1], out[s1, u2]])
            nxt2[s, u] = s2; sym2[s, u] = (b[0] << 3) | (b[1] << 2) | (b[2] << 1) | b[3]
    gamma = np.zeros((Ksec2, S, 4))
    for k in range(Ksec2):
        gamma[k] = -np.abs(r[k] - CONST[sym2]) ** 2 / tau
    gamma[K // 2:, :, 1:] = -np.inf                                   # tail forces u=(0,0)
    alpha = np.full((Ksec2 + 1, S), -np.inf); alpha[0, 0] = 0.0
    for k in range(Ksec2):
        cand = alpha[k][:, None] + gamma[k]
        for s2 in range(S):
            v = cand[nxt2 == s2]; alpha[k + 1, s2] = logsumexp(v) if v.size else -np.inf
    beta = np.full((Ksec2 + 1, S), -np.inf); beta[Ksec2, 0] = 0.0
    for k in range(Ksec2 - 1, -1, -1):
        b = gamma[k] + beta[k + 1][nxt2]; beta[k] = logsumexp(b, axis=1)
    P = np.zeros((Ksec2, 16))
    for k in range(Ksec2):
        bp = alpha[k][:, None] + gamma[k] + beta[k + 1][nxt2]
        for a in range(16):
            m = sym2 == a
            P[k, a] = logsumexp(bp[m]) if m.any() else -np.inf
        P[k] = np.exp(P[k] - logsumexp(P[k]))
    return P

def run_qam(gens, nu, K, tau_list, trials=20):
    nxt, out = make_trellis(gens, nu); n = out.shape[2]; Ksec = K + nu
    C, X = all_codewords(K, nxt, out, nu); N = X.shape[1]; Ns = N // 4
    SYM = np.array([[map16(c[4 * i:4 * i + 4]) for i in range(Ns)] for c in C])   # (2^K, Ns)
    print(f"\n[16-QAM Gray, no interleaver] code {gens}_8, nu={nu}, K={K}: {Ns} symbols/block, {trials} trials")
    print(f"{'tau':>6} {'symbol-BCJR err':>16} {'bit-pipeline NMSE':>18} {'max|dx|':>9} {'|dv| mean':>10} {'input-side NMSE':>16} {'output-side NMSE':>17}")
    for tau in tau_list:
        e_sym = 0.0; num = num_in = num_out = 0.0; den = 0.0; emax = 0.0; dv = 0.0
        for _ in range(trials):
            idx = rng.integers(SYM.shape[0]); x = SYM[idx]
            r = x + np.sqrt(tau / 2) * (rng.standard_normal(Ns) + 1j * rng.standard_normal(Ns))
            # exact (brute force)
            ll = -np.sum(np.abs(r[None, :] - SYM) ** 2, axis=1) / tau
            w = np.exp(ll - logsumexp(ll)); m_ex = w @ SYM; v_ex = w @ np.abs(SYM) ** 2 - np.abs(m_ex) ** 2
            # exact bit marginals (for isolating the two error sources)
            Pb0_ex = w @ (C == 0)                                           # (N,)
            # symbol-level BCJR
            P = bcjr_symbol_level(r, tau, nxt, out, nu, K); m_sb = P @ CONST
            e_sym = max(e_sym, np.abs(m_sb - m_ex).max())
            # bit-level pipeline: demapper bit metrics -> BCJR -> product of marginals
            Lch = np.concatenate([demap_bit_llrs(r[i], tau) for i in range(Ns)]).reshape(Ksec, n)
            Lapp = bcjr(Lch, nxt, out, nu, K).reshape(-1)
            m_bp = np.zeros(Ns, complex); v_bp = np.zeros(Ns)
            for i in range(Ns):
                m_bp[i], v_bp[i] = soft_symbol_from_bit_llrs(Lapp[4 * i:4 * i + 4])
            # (a) input-side only: compare bit marginals from pipeline vs exact marginals, as soft bits
            sb_pipe = np.tanh(Lapp / 2); sb_ex = 2 * Pb0_ex - 1
            # (b) output-side only: exact marginals -> product assembly
            Lex = np.log(np.clip(Pb0_ex, 1e-300, 1)) - np.log(np.clip(1 - Pb0_ex, 1e-300, 1))
            m_po = np.array([soft_symbol_from_bit_llrs(Lex[4 * i:4 * i + 4])[0] for i in range(Ns)])
            num += np.sum(np.abs(m_bp - m_ex) ** 2); den += np.sum(np.abs(x) ** 2)
            num_in += np.sum((sb_pipe - sb_ex) ** 2) / 4.0     # per-symbol scale (4 bits)
            num_out += np.sum(np.abs(m_po - m_ex) ** 2)
            emax = max(emax, np.abs(m_bp - m_ex).max()); dv += np.mean(np.abs(v_bp - v_ex))
        print(f"{tau:6.2f} {e_sym:16.2e} {num / den:18.2e} {emax:9.3f} {dv / trials:10.3f} {num_in / den:16.2e} {num_out / den:17.2e}")

if __name__ == "__main__":
    # Gaussian-prior closed-form sanity of the Jacobian identity: x~N(0,s2), xt=x+sigma*eps
    s2, sig2 = 0.7, 0.4
    print(f"[Gaussian sanity] E[x|xt]=s2/(s2+sig2) xt -> Jacobian {s2/(s2+sig2):.6f}; Var/sig2 = {(s2*sig2/(s2+sig2))/sig2:.6f}")
    SIG2 = [0.05, 0.3, 1.0, 3.0, 10.0]
    run_real(("7", "5"), 2, 10, SIG2)
    run_real(("133", "171"), 6, 8, SIG2, trials=2)
    run_complex(("133", "171"), 6, 8, [0.3, 1.0, 3.0], trials=2)
    run_puncture(("133", "171"), 6, 8, [0.3, 1.0, 3.0], trials=2)
    run_qam(("7", "5"), 2, 10, [0.05, 0.2, 0.5, 1.0, 2.0], trials=20)
