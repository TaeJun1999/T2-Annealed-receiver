"""
exp_0918 — route (a) v0 with a Gaussian (Kronecker) channel prior: coupling-bug isolation, trajectories, references.
Seed 20260918. Settings: Nr x Nt = 4x4, T = 28, Tp in {2,4}, BPSK, (133,171)_8 nu=6 terminated, one codeword per block
(Ns = Nt*Td coded bits, K = Ns/2 - 6), symbol interleaver (random permutation, fixed per trial), DFT pilots (unit modulus).
SNR := 1/sigma2 (per receive antenna per stream, E_s = 1, E|h_ij|^2 = 1).
T0 regression: BitTrellis vs bcjr_bits; per-symbol tau BCJR (bit-level and symbol-level) + info LLRs vs brute force.
T1 sanity 1 (rho = 0): Module H extrinsic == prior (hE = 0, nuE = 1) and mode 'scalar' == mode 'colored' trajectories.
T2 main (rho = 0.7): scalar / colored / pilot_only / genie, SNR sweep, per-iteration NMSE, tauL, nu_q, alpha, BER, BLER.
T3 ablation D-10: L_H form A (LMMSE) vs form B (v0 hybrid with the diag(tau) precision term).
"""
import sys, time
import numpy as np
from scipy.special import logsumexp
sys.path.insert(0, "/home/claude/t2")
from t2_trellis import make_trellis, encode, all_codewords, bcjr_bits, SymbolTrellis, qam_constellation
from t2_route_a import KronGaussianPrior, BitTrellis, BPSKCode, RouteA

SEED = 20260918
GENS, NU = ("133", "171"), 6
out = []
def P(*a):
    s = " ".join(str(x) for x in a); print(s); out.append(s)

# ============================================================================ T0 regression
P("=== T0 regression: extended BCJR vs t2_trellis / brute force ===")
rng = np.random.default_rng(SEED)
bt = BitTrellis(GENS, NU)
K = 20; Lch = rng.standard_normal((K + NU, 2)) * 3
Lapp_fast, Lu_fast = bt.bcjr(Lch, K)
Lapp_ref = bcjr_bits(Lch, bt.nxt, bt.out, NU, K)
P(f"T0a BitTrellis vs bcjr_bits (K={K}): max|dLapp| = {np.max(np.abs(Lapp_fast - Lapp_ref)):.2e}")

# T0b bit-level, complex embedding, per-bit tau vs brute force (K=8 -> 28 coded bits, 256 codewords)
K = 8; CW = all_codewords(K, bt.nxt, bt.out, NU); XC = 1 - 2 * CW                    # (256, 28)
U = ((np.arange(1 << K)[:, None] >> np.arange(K)[None, :]) & 1)
errs = []
for trial in range(5):
    tau = np.exp(rng.uniform(np.log(0.1), np.log(3.0), XC.shape[1]))
    x = XC[rng.integers(256)]
    r = x + np.sqrt(tau / 2) * (rng.standard_normal(x.size) + 1j * rng.standard_normal(x.size))
    ll = -np.sum(np.abs(r[None, :] - XC) ** 2 / tau[None, :], axis=1); w = np.exp(ll - logsumexp(ll))
    xbar_bf = w @ XC; Lu_bf = np.array([logsumexp(ll[U[:, k] == 0]) - logsumexp(ll[U[:, k] == 1]) for k in range(K)])
    Lapp, Lu = bt.bcjr((4 * r.real / tau).reshape(-1, 2), K)
    errs.append((np.max(np.abs(np.tanh(Lapp / 2).reshape(-1) - xbar_bf)), np.max(np.abs(Lu - Lu_bf))))
P(f"T0b bit BCJR per-bit tau vs brute force: max|dxbar| = {max(e[0] for e in errs):.2e}, max|dLu| = {max(e[1] for e in errs):.2e}")

# T0c symbol-level QPSK, per-symbol tau vs brute force
st = SymbolTrellis(GENS, NU, 2); K = 8; Ns = st.n_symbols(K)
SYMIDX = np.array([st.encode_symbols(u)[0] for u in U]); SYM = st.CONST[SYMIDX]
errs = []
for trial in range(5):
    tau = np.exp(rng.uniform(np.log(0.1), np.log(3.0), Ns))
    r = SYM[rng.integers(256)] + np.sqrt(tau / 2) * (rng.standard_normal(Ns) + 1j * rng.standard_normal(Ns))
    ll = -np.sum(np.abs(r[None, :] - SYM) ** 2 / tau[None, :], axis=1); w = np.exp(ll - logsumexp(ll))
    Pbf = np.zeros((Ns, 4))
    for k in range(Ns): np.add.at(Pbf[k], SYMIDX[:, k], w)
    Lu_bf = np.array([logsumexp(ll[U[:, k] == 0]) - logsumexp(ll[U[:, k] == 1]) for k in range(K)])
    Pb, Lu = st.bcjr(r, tau, K, return_info=True)
    Ps = st.bcjr(r, tau, K)                                                            # backward-compatible call
    errs.append((np.max(np.abs(Pb - Pbf)), np.max(np.abs(Lu.reshape(-1) - Lu_bf)), np.max(np.abs(Ps - Pb))))
P(f"T0c symbol BCJR per-symbol tau vs brute force (QPSK): max|dP| = {max(e[0] for e in errs):.2e}, "
  f"max|dLu| = {max(e[1] for e in errs):.2e}, compat = {max(e[2] for e in errs):.1e}")
P("")

# ============================================================================ helpers
def make_setup(Nr, Nt, T, Tp, rho):
    prior = KronGaussianPrior(Nr, Nt, rho)
    code = BPSKCode(GENS, NU, Nt * (T - Tp))
    return prior, code

def run_trials(Nr, Nt, T, Tp, rho, snr_db, modes, n_trials, n_iter, seed, **kw):
    prior, code = make_setup(Nr, Nt, T, Tp, rho)
    sigma2 = 10 ** (-snr_db / 10)
    rxs = {name: RouteA(Nr, Nt, T, Tp, sigma2, prior, code, **dict(cfg, **kw)) for name, cfg in modes.items()}
    logs = {name: [] for name in modes}
    rng = np.random.default_rng(seed)
    for tr in range(n_trials):
        H = prior.sample(rng); u = rng.integers(0, 2, code.K); perm = rng.permutation(code.Ns)
        X, Y = rxs[next(iter(modes))].transmit(u, perm, H, rng)
        for name, rx in rxs.items():
            logs[name].append(rx.run(Y, H, u, perm, n_iter))
    agg = {}
    for name in modes:
        L = logs[name]
        agg[name] = {k: np.array([l[k] for l in L]) for k in L[0]}
    return agg

def fmt_traj(v, f="{:.3g}"):
    return " ".join(f.format(x) for x in v)

# ============================================================================ T1 sanity 1 (rho = 0)
P("=== T1 sanity 1: rho = 0 (C = I). Module H extrinsic must equal the prior; scalar == colored ===")
modes = {"scalar": dict(mode="scalar"), "colored": dict(mode="colored")}
t0 = time.time()
for Tp in (4, 2):
    agg = run_trials(4, 4, 28, Tp, 0.0, 6.0, modes, n_trials=10, n_iter=6, seed=SEED + 1)
    s, c = agg["scalar"], agg["colored"]
    P(f"Tp={Tp}: max||hE|| = {np.max(s['hE_norm']):.1e}, max|nuE-1| = {np.max(np.abs(s['nuE'] - 1)):.1e}, "
      f"max|NMSE_s - NMSE_c| = {np.max(np.abs(s['nmse'] - c['nmse'])):.1e}, "
      f"max|tauL_s - tauL_c|/tauL = {np.max(np.abs(s['tauL_gmean'] - c['tauL_gmean']) / c['tauL_gmean']):.1e}, "
      f"BER_s == BER_c: {np.array_equal(s['ber'], c['ber'])}")
    P(f"      NMSE traj (scalar): {fmt_traj(s['nmse'].mean(0))};  nu_q traj: {fmt_traj(s['nu_q'].mean(0))}")
P(f"(T1 wall-clock {time.time() - t0:.1f} s)")
P("")

# ============================================================================ T2 main (rho = 0.7)
P("=== T2 main: rho = 0.7, 4x4, T = 28, BPSK (133,171)_8, 8 iterations ===")
modes = {"scalar": dict(mode="scalar"), "colored": dict(mode="colored"),
         "pilot_only": dict(mode="pilot_only"), "genie": dict(mode="genie")}
N_TRIALS, N_ITER = 80, 8
snrs = [0.0, 3.0, 6.0, 9.0, 12.0]
t0 = time.time()
summary = {}
for Tp in (4, 2):
    P(f"--- Tp = {Tp} (Td = {28 - Tp}, K = {4 * (28 - Tp) // 2 - 6} info bits) ---")
    for snr in snrs:
        agg = run_trials(4, 4, 28, Tp, 0.7, snr, modes, N_TRIALS, N_ITER, SEED + 100 + int(snr))
        summary[(Tp, snr)] = agg
        line = f"SNR {snr:4.1f} dB | "
        for name in modes:
            a = agg[name]
            bler = a["blk_err"].mean(0); nm = a["nmse"].mean(0)
            line += f"{name}: BLER {bler[0]:.2f}->{bler[-1]:.2f}"
            if name in ("scalar", "colored", "pilot_only"):
                line += f", NMSE {nm[0]:.3f}->{nm[-1]:.3f}"
            line += " | "
        P(line)
        if snr == 6.0:
            for name in ("scalar", "colored"):
                a = agg[name]
                P(f"   [{name}] NMSE  : {fmt_traj(a['nmse'].mean(0), '{:.4f}')}")
                P(f"   [{name}] tauL_g: {fmt_traj(a['tauL_gmean'].mean(0))}   (L_c = 4/tauL)")
                P(f"   [{name}] BLER  : {fmt_traj(a['blk_err'].mean(0), '{:.2f}')}   BER: {fmt_traj(a['ber'].mean(0), '{:.3f}')}")
                P(f"   [{name}] alphaD: {fmt_traj(a['alphaD'].mean(0))}  tauL clip frac: {fmt_traj(a['tauL_clip_frac'].mean(0), '{:.3f}')}")
                if name == "scalar":
                    P(f"   [{name}] nu_q  : {fmt_traj(a['nu_q'].mean(0))}   alphaH: {fmt_traj(a['alphaH'].mean(0))}   nuE: {fmt_traj(a['nuE'].mean(0))}")
                # monotonicity of NMSE per trial
                dn = np.diff(a["nmse"], axis=1)
                P(f"   [{name}] NMSE non-monotone steps: {np.mean(dn > 1e-3 * a['nmse'][:, :-1]):.3f} of steps; trials with any increase >1%: {np.mean(np.any(dn > 0.01 * a['nmse'][:, :-1], axis=1)):.2f}")
            for name in ("pilot_only", "genie"):
                a = agg[name]
                P(f"   [{name}] BLER  : {fmt_traj(a['blk_err'].mean(0), '{:.2f}')}   tauL_g: {fmt_traj(a['tauL_gmean'].mean(0))}")
P(f"(T2 wall-clock {time.time() - t0:.1f} s)")
P("")

# ============================================================================ T3 D-10 ablation: L_H form A vs B (rho = 0.7, Tp = 2, 6 dB)
P("=== T3 D-10 ablation: L_H form A (LMMSE, marginalisation) vs form B (v0 hybrid with diag(tau) precision) ===")
modes = {"scalar_A": dict(mode="scalar", lh_form="A"), "scalar_B": dict(mode="scalar", lh_form="B"),
         "colored_A": dict(mode="colored", lh_form="A"), "colored_B": dict(mode="colored", lh_form="B")}
t0 = time.time()
for Tp in (4, 2):
    for snr in (3.0, 6.0):
        agg = run_trials(4, 4, 28, Tp, 0.7, snr, modes, 60, 8, SEED + 300 + Tp + int(snr))
        line = f"Tp={Tp} SNR {snr:.0f} dB | "
        for name in modes:
            a = agg[name]
            line += f"{name}: NMSE {a['nmse'].mean(0)[-1]:.4f} BLER {a['blk_err'].mean(0)[-1]:.2f} | "
        P(line)
        a, bb = agg["scalar_A"], agg["scalar_B"]
        P(f"   NMSE traj A: {fmt_traj(a['nmse'].mean(0), '{:.4f}')}")
        P(f"   NMSE traj B: {fmt_traj(bb['nmse'].mean(0), '{:.4f}')}")
P(f"(T3 wall-clock {time.time() - t0:.1f} s)")

with open("/home/claude/t2/exp_0918_results.txt", "w") as f:
    f.write("\n".join(out) + "\n")
