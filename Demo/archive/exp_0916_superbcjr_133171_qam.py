#!/usr/bin/env python3
"""
exp_0916_superbcjr_133171_qam.py  (T2, M1: symbol-level BCJR module check, code (133,171)_8, nu=6)

Checks against brute-force enumeration of all 2^K codewords (complex noise CN(0,tau) per entry, D-01):
  S1  symbol posteriors P(x_n=a|r), soft symbols (x_bar, v), exact bit marginals: super-section BCJR == brute force
  S2  complex Tweedie: grad_{r*} log p_tau(r) == (x_bar - r)/tau   (finite differences, d/dz* = (d/dRe + j d/dIm)/2)
  S3  Wirtinger Jacobian: d x_bar_n / d r_j == (E[x_n x_j^*] - x_bar_n x_bar_j^*)/tau ; diag == v_n/tau ;
      normalized divergence == mean(v)/tau   (finite differences, d/dz = (d/dRe - j d/dIm)/2)
  S4  tilted prior (a-priori symbol weights) keeps exactness
  S5  BICM bit pipeline (demapper metrics -> bit BCJR -> product of marginals) error vs exact  [ablation]
  S6  branch-metric counts and wall-clock per BCJR call
Seeds fixed.
"""
import time
import numpy as np
from scipy.special import logsumexp
from t2_trellis import (SymbolTrellis, soft_symbols, bit_marginals, bcjr_bits, demap_bit_llrs,
                        product_assembly, brute_force, all_codewords)

rng = np.random.default_rng(20260916)

def fd_complex(f, r, h=1e-5):
    """Returns (dRe f, dIm f) as arrays over coordinates of r for scalar/vector-valued f."""
    Ns = r.size
    dr = []; di = []
    for j in range(Ns):
        e = np.zeros(Ns, complex); e[j] = h
        dr.append((f(r + e) - f(r - e)) / (2 * h))
        di.append((f(r + 1j * e) - f(r - 1j * e)) / (2 * h))
    return np.array(dr), np.array(di)

def codeword_symbol_table(T, K):
    C = all_codewords(K, T.nxt, T.out, T.nu)
    return (C.reshape(C.shape[0], -1, T.m) << (T.m - 1 - np.arange(T.m))[None, None, :]).sum(2), C

def run(gens, nu, m, K, tau_list, trials=4, do_fd=True, label=""):
    T = SymbolTrellis(gens, nu, m); Ns = T.n_symbols(K)
    SYMIDX, C = codeword_symbol_table(T, K)
    print(f"\n[{label}] code {gens}_8 nu={nu}, 2^{m}-QAM, K={K}: {Ns} symbols/block, {SYMIDX.shape[0]} codewords, "
          f"branches/section = {T.S}x{T.U} = {T.S*T.U}")
    hdr = f"{'tau':>6} {'max|dP|':>9} {'max|dxbar|':>11} {'max|dv|':>9} {'bitmarg':>9}"
    if do_fd: hdr += f" {'Tweedie':>9} {'Jac':>9} {'diag=v/tau':>11} {'div':>9}"
    hdr += f" {'tilted':>9} {'pipe NMSE':>10} {'pipe max':>9} {'pipe|dv|':>9}"
    print(hdr)
    for tau in tau_list:
        e = dict(P=0, x=0, v=0, b=0, tw=0, jac=0, dg=0, dv=0, tl=0); num = den = 0.0; pmax = 0.0; pdv = 0.0
        for _ in range(trials):
            idx = SYMIDX[rng.integers(SYMIDX.shape[0])]; x = T.CONST[idx]
            r = x + np.sqrt(tau / 2) * (rng.standard_normal(Ns) + 1j * rng.standard_normal(Ns))
            P_bf, logp, w = brute_force(r, tau, SYMIDX, T.CONST)
            P = T.bcjr(r, tau, K)
            xb, v = soft_symbols(P, T.CONST); xb_bf, v_bf = soft_symbols(P_bf, T.CONST)
            e['P'] = max(e['P'], np.abs(P - P_bf).max()); e['x'] = max(e['x'], np.abs(xb - xb_bf).max())
            e['v'] = max(e['v'], np.abs(v - v_bf).max())
            e['b'] = max(e['b'], np.abs(bit_marginals(P, T.CBITS) - bit_marginals(P_bf, T.CBITS)).max())
            if do_fd:
                gr, gi = fd_complex(lambda z: brute_force(z, tau, SYMIDX, T.CONST)[1], r)
                score_conj = 0.5 * (gr + 1j * gi)                                # d/dr* of log p
                e['tw'] = max(e['tw'], np.abs(r + tau * score_conj - xb).max())
                jr, ji = fd_complex(lambda z: soft_symbols(brute_force(z, tau, SYMIDX, T.CONST)[0], T.CONST)[0], r)
                J = 0.5 * (jr - 1j * ji)                                          # J[j, n] = d xbar_n / d r_j
                SYM = T.CONST[SYMIDX]
                Exx = (w[:, None, None] * SYM[:, :, None] * np.conj(SYM[:, None, :])).sum(0)   # E[x_n x_j^*]
                Cov = Exx - np.outer(xb_bf, np.conj(xb_bf))
                e['jac'] = max(e['jac'], np.abs(J.T - Cov / tau).max())
                e['dg'] = max(e['dg'], np.abs(np.diag(J) - v / tau).max())
                e['dv'] = max(e['dv'], abs(np.trace(J) / Ns - v.mean() / tau))
            # tilted prior: random a-priori symbol weights, brute force with same weights
            lp = rng.standard_normal((Ns, 1 << m)) * 0.7
            P_t = T.bcjr(r, tau, K, log_prior=lp)
            ll = -np.sum(np.abs(r[None, :] - T.CONST[SYMIDX]) ** 2, axis=1) / tau + lp[np.arange(Ns)[None, :], SYMIDX].sum(1)
            wt = np.exp(ll - logsumexp(ll)); P_tb = np.zeros_like(P_t)
            for k in range(Ns): np.add.at(P_tb[k], SYMIDX[:, k], wt)
            e['tl'] = max(e['tl'], np.abs(P_t - P_tb).max())
            # BICM bit pipeline (ablation)
            Lch = np.concatenate([demap_bit_llrs(r[i], tau, T.CONST, T.CBITS) for i in range(Ns)]).reshape(-1, T.nc)
            Lapp = bcjr_bits(Lch, T.nxt, T.out, nu, K).reshape(-1)
            xp = np.zeros(Ns, complex); vp = np.zeros(Ns)
            for i in range(Ns):
                xp[i], vp[i] = product_assembly(Lapp[m * i:m * (i + 1)], T.CONST, T.CBITS)
            num += np.sum(np.abs(xp - xb_bf) ** 2); den += np.sum(np.abs(x) ** 2)
            pmax = max(pmax, np.abs(xp - xb_bf).max()); pdv += np.mean(np.abs(vp - v_bf)) / trials
        row = f"{tau:6.2f} {e['P']:9.1e} {e['x']:11.1e} {e['v']:9.1e} {e['b']:9.1e}"
        if do_fd: row += f" {e['tw']:9.1e} {e['jac']:9.1e} {e['dg']:11.1e} {e['dv']:9.1e}"
        row += f" {e['tl']:9.1e} {num/den:10.1e} {pmax:9.3f} {pdv:9.3f}"
        print(row)
    return T, Ns

if __name__ == "__main__":
    TAUS = [0.05, 0.2, 0.5, 1.0, 2.0, 5.0]
    T16, Ns = run(("133", "171"), 6, 4, 12, TAUS, trials=4, label="main 16-QAM")
    run(("133", "171"), 6, 4, 16, [1.0], trials=2, do_fd=False, label="K=16 16-QAM (65536 codewords)")
    run(("133", "171"), 6, 2, 12, [0.5, 2.0], trials=2, label="QPSK")
    run(("133", "171"), 6, 6, 12, [0.5, 2.0], trials=2, label="64-QAM")
    # S6: cost accounting / wall-clock for the main configuration
    Kbig = 200; Tt = SymbolTrellis(("133", "171"), 6, 4); Nsb = Tt.n_symbols(Kbig)
    idx, x = Tt.encode_symbols(rng.integers(0, 2, Kbig))
    r = x + np.sqrt(0.5) * (rng.standard_normal(Nsb) + 1j * rng.standard_normal(Nsb))
    t0 = time.perf_counter(); P = Tt.bcjr(r, 1.0, Kbig); t1 = time.perf_counter()
    Lch = np.concatenate([demap_bit_llrs(r[i], 1.0, Tt.CONST, Tt.CBITS) for i in range(Nsb)]).reshape(-1, 2)
    t2 = time.perf_counter(); Lapp = bcjr_bits(Lch, Tt.nxt, Tt.out, 6, Kbig); t3 = time.perf_counter()
    print(f"\n[cost] K={Kbig}, {Nsb} 16-QAM symbols: super-section BCJR {t1-t0:.2f}s "
          f"({Tt.S*Tt.U} branch metrics/symbol) vs bit-level BCJR {t3-t2:.2f}s ({2*Tt.S*2} branch metrics/symbol); numpy loops, no vectorization")
    print("[cost] branch metrics per symbol, rate-1/2 code, 2^nu states: QPSK 2^nu*2 vs 2^nu*2 ; 16-QAM 2^nu*4 vs 2^nu*4 ; "
          "64-QAM 2^nu*8 vs 2^nu*6 ; 256-QAM 2^nu*16 vs 2^nu*8   (super-section vs bit-level)")
