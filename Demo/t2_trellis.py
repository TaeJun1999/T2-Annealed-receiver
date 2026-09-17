"""
t2_trellis.py — T2 decoder-as-denoiser modules (numpy reference implementation).

Conventions (D-01): bits 0->+1, 1->-1 ; L = log P(c=0)/P(c=1) ; complex variances are per complex entry,
so a complex pseudo-observation r = x + sqrt(tau) eps, eps ~ CN(0,1), has real/imag noise variance tau/2 each.
Real BPSK model: L_c = 2/sigma^2 (sigma^2 per real dimension). Complex embedding of BPSK: L_c = 4/tau on Re{r}.

Contents
  make_trellis / encode / all_codewords      rate-1/n_c feed-forward convolutional code, terminated
  qam_constellation(m)                        3GPP TS 38.211 §5.1.4 Gray labeling for m in {1,2,4,6}  [VERIFY vs Sionna]
  SymbolTrellis(gens, nu, m).bcjr(r, tau, K)  exact symbol posteriors P(x_n = a | r) on the super-section trellis
                                              (one section = q = m/n_c info bits = one 2^m-QAM symbol), log-domain, exact log-sum-exp;
                                              vectorised since exp_0919 (.bcjr_loop = original per-state loop, kept as regression reference)
  soft_symbols / bit_marginals                 (x_bar, v) and exact bit marginals from P
  bcjr_bits(Lch, ...)                          bit-level BCJR (coded-bit a-posteriori LLRs) — used by the BICM ablation
  demap_bit_llrs / product_assembly            BICM bit metrics and product-of-marginals soft symbol (approximate pipeline)
  brute_force(r, tau, SYMIDX, CONST)           exact reference by enumeration of all 2^K codewords
"""
import numpy as np
from scipy.special import logsumexp

# ----------------------------------------------------------------------------- convolutional code
def make_trellis(gens_oct, nu):
    """State = last nu inputs (msb = most recent). Octal generator, msb tap = current input (e.g. 133 = 1+D^2+D^3+D^5+D^6)."""
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
    u = np.concatenate([np.asarray(u_info, int), np.zeros(nu, int)])
    s, c = 0, []
    for uk in u:
        c.append(out[s, uk]); s = nxt[s, uk]
    assert s == 0
    return np.concatenate(c)

def all_codewords(K, nxt, out, nu):
    U = ((np.arange(1 << K)[:, None] >> np.arange(K)[None, :]) & 1).astype(int)
    return np.array([encode(u, nxt, out, nu) for u in U])          # (2^K, n_c (K+nu)) bits

# ----------------------------------------------------------------------------- QAM labeling (3GPP TS 38.211 §5.1.4)
def qam_constellation(m):
    """Returns CONST (2^m,) complex (unit average energy) and CBITS (2^m, m); label index a = sum_i b_i 2^(m-1-i).
    m=1 BPSK on the real axis; m=2 QPSK; m=4 16QAM; m=6 64QAM.  Formulas as in TS 38.211 [M — VERIFY against Sionna]."""
    A = 1 << m
    CBITS = ((np.arange(A)[:, None] >> (m - 1 - np.arange(m))[None, :]) & 1).astype(int)
    s = 1 - 2 * CBITS                                                  # (A, m) in {+1,-1}
    if m == 1:
        x = s[:, 0].astype(complex)
    elif m == 2:
        x = (s[:, 0] + 1j * s[:, 1]) / np.sqrt(2)
    elif m == 4:
        x = (s[:, 0] * (2 - s[:, 2]) + 1j * s[:, 1] * (2 - s[:, 3])) / np.sqrt(10)
    elif m == 6:
        x = (s[:, 0] * (4 - s[:, 2] * (2 - s[:, 4])) + 1j * s[:, 1] * (4 - s[:, 3] * (2 - s[:, 5]))) / np.sqrt(42)
    else:
        raise ValueError("m in {1,2,4,6}")
    return x, CBITS

# ----------------------------------------------------------------------------- symbol-level (super-section) trellis
class SymbolTrellis:
    """Super-section trellis for a rate-1/n_c terminated convolutional code followed (without interleaver) by a 2^m-QAM
    mapper acting on consecutive groups of m coded bits. One section consumes q = m/n_c information bits and emits one symbol.
    Requires K % q == 0 and nu % q == 0 (tail sections carry forced zero inputs)."""
    def __init__(self, gens_oct, nu, m):
        self.nxt, self.out = make_trellis(gens_oct, nu)
        self.nu, self.m, self.nc = nu, m, self.out.shape[2]
        assert m % self.nc == 0
        self.q = m // self.nc
        S, U = 1 << nu, 1 << self.q
        self.CONST, self.CBITS = qam_constellation(m)
        self.nxt_q = np.zeros((S, U), int)
        self.sym_q = np.zeros((S, U), int)
        for s in range(S):
            for u in range(U):
                st, bits = s, []
                for i in range(self.q):                                 # msb-first input order
                    ui = (u >> (self.q - 1 - i)) & 1
                    bits.extend(self.out[st, ui]); st = self.nxt[st, ui]
                self.nxt_q[s, u] = st
                self.sym_q[s, u] = int(sum(b << (m - 1 - i) for i, b in enumerate(bits)))
        self.S, self.U = S, U
        self.pred = [np.argwhere(self.nxt_q == s2) for s2 in range(S)]  # predecessor (s,u) pairs
        self.sym_masks = [self.sym_q == a for a in range(1 << m)]
        # exp_0919: index arrays for the vectorised recursion. In the feed-forward shift-register trellis every state
        # has exactly U = 2^q predecessor branches (asserted, not assumed).
        assert all(len(p) == U for p in self.pred)
        self.pS = np.array([p[:, 0] for p in self.pred])                # (S,U) predecessor states
        self.pU = np.array([p[:, 1] for p in self.pred])                # (S,U) inputs on those branches
        self.sym_onehot = np.zeros((S * U, 1 << m))                     # branch (s,u) -> emitted symbol (one-hot)
        self.sym_onehot[np.arange(S * U), self.sym_q.reshape(-1)] = 1.0
        self.ubit = ((np.arange(U)[:, None] >> (self.q - 1 - np.arange(self.q))[None, :]) & 1)   # (U,q) msb-first

    def n_symbols(self, K):
        assert K % self.q == 0 and self.nu % self.q == 0
        return (K + self.nu) // self.q

    def encode_symbols(self, u_info):
        c = encode(u_info, self.nxt, self.out, self.nu)
        idx = (c.reshape(-1, self.m) << (self.m - 1 - np.arange(self.m))[None, :]).sum(1)
        return idx, self.CONST[idx]

    def bcjr(self, r, tau, K, log_prior=None, return_info=False, return_ext=False):
        """Vectorised exact Log-MAP on the super-section trellis (exp_0919; same interface and semantics as bcjr_loop).
        r: (Ns,) complex pseudo-observations, noise CN(0, tau_n) per entry; tau scalar or (Ns,) per-symbol (diagonal
        covariance, Lemma 2 unchanged). log_prior: optional (Ns, 2^m) log a-priori symbol weights (tilted prior).
        Returns P: (Ns, 2^m) exact symbol posteriors (and, if return_info, info-bit APP LLRs Lu: (K//q, q), msb-first).
        Recursions use exact pairwise log-add-exp over the U predecessors / successors of each state; the symbol
        posterior is a max-shifted exp-sum grouped by emitted symbol (identical to log-sum-exp up to rounding; terms
        more than ~745 nats below the section maximum underflow to 0, as they would after exp() anyway);
        info-bit LLRs stay in the log domain (per-group log-sum-exp) so that confident LLRs remain finite."""
        Ns = self.n_symbols(K); Kq = K // self.q
        S, U = self.S, self.U
        tau_n = np.broadcast_to(np.asarray(tau, float), (Ns,))[:, None, None]
        gamma = -np.abs(r[:, None, None] - self.CONST[self.sym_q][None]) ** 2 / tau_n    # (Ns,S,U) exact symbol likelihood
        if log_prior is not None:
            gamma = gamma + log_prior[np.arange(Ns)[:, None, None], self.sym_q[None]]
        gamma[Kq:, :, 1:] = -np.inf                                                      # forced zero tail
        alpha = np.full((Ns + 1, S), -np.inf); alpha[0, 0] = 0.0
        beta = np.full((Ns + 1, S), -np.inf); beta[Ns, 0] = 0.0
        with np.errstate(invalid="ignore", divide="ignore"):
            for k in range(Ns):
                cand = alpha[k][:, None] + gamma[k]
                alpha[k + 1] = np.logaddexp.reduce(cand[self.pS, self.pU], axis=1)
            for k in range(Ns - 1, -1, -1):
                beta[k] = np.logaddexp.reduce(gamma[k] + beta[k + 1][self.nxt_q], axis=1)
            bp = alpha[:-1, :, None] + gamma + beta[1:][:, self.nxt_q]                   # (Ns,S,U) branch log-posteriors (unnormalised)
            flat = bp.reshape(Ns, S * U)
            E = np.exp(flat - flat.max(axis=1, keepdims=True)) @ self.sym_onehot         # (Ns, 2^m)
            P = E / E.sum(axis=1, keepdims=True)
            res = [P]
            if return_info:
                Lu = np.empty((Kq, self.q))
                for i in range(self.q):
                    m0 = self.ubit[:, i] == 0
                    Lu[:, i] = logsumexp(bp[:Kq][:, :, m0], axis=(1, 2)) - logsumexp(bp[:Kq][:, :, ~m0], axis=(1, 2))
                res.append(Lu)
            if return_ext:
                # exp_0919b (Q-04): exact extrinsic pmf P(x_n = a | r_{\n}) — branch posterior WITHOUT the channel metric of section n
                # (code structure, tail constraint and optional log_prior kept). Computed from alpha/beta directly: no subtraction of large logs.
                gs = gamma + np.abs(r[:, None, None] - self.CONST[self.sym_q][None]) ** 2 / tau_n      # = structural part (0 / -inf / log_prior)
                fe = (alpha[:-1, :, None] + gs + beta[1:][:, self.nxt_q]).reshape(Ns, S * U)
                Ee = np.exp(fe - fe.max(axis=1, keepdims=True)) @ self.sym_onehot
                res.append(Ee / Ee.sum(axis=1, keepdims=True))
        return res[0] if len(res) == 1 else tuple(res)

    def bcjr_loop(self, r, tau, K, log_prior=None, return_info=False):
        """r: (Ns,) complex pseudo-observations, noise CN(0, tau_n) per entry; tau scalar or (Ns,) per-symbol
        (exp_0918 extension: diagonal covariance, Lemma 2 unchanged). log_prior: optional (Ns, 2^m) log a-priori
        weights on symbols (tilted prior; default uniform). Returns P: (Ns, 2^m) exact symbol posteriors
        (and, if return_info, the info-bit APP LLRs Lu: (K//q, q), msb-first within a section)."""
        Ns = self.n_symbols(K); Kq = K // self.q
        S, U = self.S, self.U
        tau_n = np.broadcast_to(np.asarray(tau, float), (Ns,))[:, None, None]
        gamma = -np.abs(r[:, None, None] - self.CONST[self.sym_q][None]) ** 2 / tau_n    # (Ns,S,U) exact symbol likelihood
        if log_prior is not None:
            gamma = gamma + log_prior[np.arange(Ns)[:, None, None], self.sym_q[None]]
        gamma[Kq:, :, 1:] = -np.inf                                                      # forced zero tail
        alpha = np.full((Ns + 1, S), -np.inf); alpha[0, 0] = 0.0
        for k in range(Ns):
            cand = alpha[k][:, None] + gamma[k]
            for s2 in range(S):
                p = self.pred[s2]
                alpha[k + 1, s2] = logsumexp(cand[p[:, 0], p[:, 1]]) if len(p) else -np.inf
        beta = np.full((Ns + 1, S), -np.inf); beta[Ns, 0] = 0.0
        for k in range(Ns - 1, -1, -1):
            beta[k] = logsumexp(gamma[k] + beta[k + 1][self.nxt_q], axis=1)
        P = np.full((Ns, 1 << self.m), -np.inf)
        Lu = np.zeros((Kq, self.q))
        ubit = ((np.arange(U)[:, None] >> (self.q - 1 - np.arange(self.q))[None, :]) & 1)   # (U, q) input bits, msb-first
        for k in range(Ns):
            bp = alpha[k][:, None] + gamma[k] + beta[k + 1][self.nxt_q]
            for a, msk in enumerate(self.sym_masks):
                if msk.any():
                    P[k, a] = logsumexp(bp[msk])
            P[k] -= logsumexp(P[k])
            if return_info and k < Kq:
                for i in range(self.q):
                    Lu[k, i] = logsumexp(bp[:, ubit[:, i] == 0]) - logsumexp(bp[:, ubit[:, i] == 1])
        return (np.exp(P), Lu) if return_info else np.exp(P)

def soft_symbols(P, CONST):
    xbar = P @ CONST
    v = P @ (np.abs(CONST) ** 2) - np.abs(xbar) ** 2
    return xbar, v

def bit_marginals(P, CBITS):
    """P(b_j = 0 | r) for each symbol and bit position: (Ns, m)."""
    return P @ (CBITS == 0)

# ----------------------------------------------------------------------------- bit-level BCJR (ablation / BPSK)
def bcjr_bits(Lch, nxt, out, nu, K, La=None, maxlog=False):
    """Lch: (K+nu, n_c) channel LLRs of coded bits; La: optional (K,) a-priori LLRs of info bits.
    Returns coded-bit a-posteriori LLRs (K+nu, n_c). Exact log-sum-exp unless maxlog."""
    S = 1 << nu; Ksec, n = Lch.shape
    lse = (lambda a: np.max(a)) if maxlog else (lambda a: logsumexp(a))
    xs = 1 - 2 * out
    gamma = 0.5 * np.einsum("sui,ki->ksu", xs, Lch)
    if La is not None:
        gamma[:K] += 0.5 * (np.array([1.0, -1.0])[None, None, :] * La[:, None, None])
    gamma[K:, :, 1] = -np.inf
    alpha = np.full((Ksec + 1, S), -np.inf); alpha[0, 0] = 0.0
    for k in range(Ksec):
        cand = alpha[k][:, None] + gamma[k]
        for s2 in range(S):
            v = cand[nxt == s2]; alpha[k + 1, s2] = lse(v) if v.size else -np.inf
    beta = np.full((Ksec + 1, S), -np.inf); beta[Ksec, 0] = 0.0
    for k in range(Ksec - 1, -1, -1):
        b = gamma[k] + beta[k + 1][nxt]; beta[k] = np.array([lse(b[s]) for s in range(S)])
    Lapp = np.zeros((Ksec, n))
    for k in range(Ksec):
        bp = alpha[k][:, None] + gamma[k] + beta[k + 1][nxt]
        for i in range(n):
            Lapp[k, i] = lse(bp[out[:, :, i] == 0]) - lse(bp[out[:, :, i] == 1])
    return Lapp

def demap_bit_llrs(r, tau, CONST, CBITS):
    """BICM bit metrics without a priori (exact marginalization over the constellation)."""
    ll = -np.abs(r - CONST) ** 2 / tau
    return np.array([logsumexp(ll[CBITS[:, j] == 0]) - logsumexp(ll[CBITS[:, j] == 1]) for j in range(CBITS.shape[1])])

def product_assembly(L, CONST, CBITS):
    """Soft symbol from bit LLRs under the product-of-marginals approximation."""
    P0 = 1 / (1 + np.exp(-L))
    Pa = np.prod(np.where(CBITS == 0, P0[None, :], 1 - P0[None, :]), axis=1)
    xbar = Pa @ CONST; v = Pa @ (np.abs(CONST) ** 2) - abs(xbar) ** 2
    return xbar, v

# ----------------------------------------------------------------------------- brute-force reference
def brute_force(r, tau, SYMIDX, CONST):
    """SYMIDX: (2^K, Ns) constellation indices of every codeword. Returns exact P (Ns, 2^m), log p_tau(r), and weights."""
    SYM = CONST[SYMIDX]
    ll = -np.sum(np.abs(r[None, :] - SYM) ** 2, axis=1) / tau
    lZ = logsumexp(ll); w = np.exp(ll - lZ)
    Ns, A = SYMIDX.shape[1], CONST.size
    P = np.zeros((Ns, A))
    for k in range(Ns):
        np.add.at(P[k], SYMIDX[:, k], w)
    logp = lZ - np.log(SYMIDX.shape[0]) - Ns * np.log(np.pi * tau)
    return P, logp, w
