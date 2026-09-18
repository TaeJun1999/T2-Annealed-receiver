"""
exp_0918b — F1/F3 cause isolation (route (a) v0, Gaussian Kronecker prior, rho = 0.7, 4x4, BPSK (133,171)_8).
T4a per-trial inspection of the late NMSE jump (F3, Tp=4, 6 dB, same trials as exp_0918 T2).
T4b colored-init: exact colored prior for the first k in {1,2} iterations, scalar EP afterwards (Tp=2, 6/9 dB).
T4c damping beta and clip eps (Tp=4, 6 dB). Seed 20260918 (+ offsets as in exp_0918).
"""
import sys, time, numpy as np
sys.path.insert(0, "/home/claude/t2")
from t2_route_a import KronGaussianPrior, BPSKCode, RouteA
GENS, NU, SEED = ("133", "171"), 6, 20260918
out = []
def P(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); out.append(s)
def fmt(v, f="{:.3g}"): return " ".join(f.format(x) for x in v)
def run_trials(Tp, snr_db, modes, n_trials, n_iter, seed, Nr=4, Nt=4, T=28, rho=0.7):
    prior = KronGaussianPrior(Nr, Nt, rho); code = BPSKCode(GENS, NU, Nt * (T - Tp)); sigma2 = 10 ** (-snr_db / 10)
    rxs = {n: RouteA(Nr, Nt, T, Tp, sigma2, prior, code, **c) for n, c in modes.items()}
    logs = {n: [] for n in modes}; rng = np.random.default_rng(seed)
    for _ in range(n_trials):
        H = prior.sample(rng); u = rng.integers(0, 2, code.K); perm = rng.permutation(code.Ns)
        X, Y = rxs[next(iter(modes))].transmit(u, perm, H, rng)
        for n, rx in rxs.items(): logs[n].append(rx.run(Y, H, u, perm, n_iter))
    return {n: {k: np.array([l[k] for l in L]) for k in L[0]} for n, L in logs.items()}
def report(name, a):
    P(f"   [{name}] NMSE mean: {fmt(a['nmse'].mean(0), '{:.4f}')} | median: {fmt(np.median(a['nmse'], 0), '{:.4f}')}")
    P(f"   [{name}] BLER: {fmt(a['blk_err'].mean(0), '{:.3f}')} | BER: {fmt(a['ber'].mean(0), '{:.4f}')}")

which = sys.argv[1] if len(sys.argv) > 1 else "ac"
if "a" in which:
    P("=== T4a per-trial: F3 late NMSE jump (Tp=4, 6 dB, seed as exp_0918 T2) ===")
    t0 = time.time()
    agg = run_trials(4, 6.0, {"scalar": dict(mode="scalar"), "colored": dict(mode="colored")}, 80, 8, SEED + 106)
    s, c = agg["scalar"], agg["colored"]
    nm = s["nmse"]; run_min = np.minimum.accumulate(nm, axis=1)
    jump = np.any(nm[:, 2:] > 1.5 * run_min[:, 1:-1], axis=1)
    P(f"trials with a late jump (NMSE > 1.5 x running min, t>=3): {jump.sum()} / 80 ; colored same criterion: "
      f"{np.any(c['nmse'][:, 2:] > 1.5 * np.minimum.accumulate(c['nmse'], 1)[:, 1:-1], axis=1).sum()} / 80")
    for i in np.where(jump)[0]:
        P(f" trial {i}: NMSE_s {fmt(nm[i], '{:.4f}')} | NMSE_c {fmt(c['nmse'][i], '{:.4f}')}")
        P(f"           BER_s {fmt(s['ber'][i], '{:.3f}')} | BER_c {fmt(c['ber'][i], '{:.3f}')} | blk_s {s['blk_err'][i]} blk_c {c['blk_err'][i]}")
        P(f"           alphaD_s {fmt(s['alphaD'][i], '{:.1e}')} | nu_q {fmt(s['nu_q'][i], '{:.3g}')} | nuE {fmt(s['nuE'][i], '{:.3g}')} | tauL_g {fmt(s['tauL_gmean'][i], '{:.3g}')}")
    ok = ~jump
    P(f"non-jump trials: mean NMSE_s last = {nm[ok, -1].mean():.4f}, NMSE_c last = {c['nmse'][ok, -1].mean():.4f}; "
      f"blocks in error at t=8: scalar {s['blk_err'][:, -1].sum()}, colored {c['blk_err'][:, -1].sum()}; "
      f"decoded-OK-then-failed (scalar): {np.sum((s['blk_err'][:, 1] == 0) & (s['blk_err'][:, -1] == 1))}, colored: {np.sum((c['blk_err'][:, 1] == 0) & (c['blk_err'][:, -1] == 1))}")
    # F2: period-2 oscillation vs alphaD clip
    d = np.diff(nm[ok][:, 2:], axis=1); sgn_alt = np.mean(np.sign(d[:, :-1]) * np.sign(d[:, 1:]) < 0)
    P(f"F2: fraction of sign alternations in consecutive NMSE steps (t>=3, non-jump trials): {sgn_alt:.2f}; "
      f"fraction of iterations with alphaD at clip eps: {np.mean(s['alphaD'][ok] <= 1.1e-6):.2f}")
    P(f"(T4a {time.time() - t0:.0f} s)\n")
if "c" in which:
    P("=== T4c damping / eps (Tp=4, 6 dB, scalar mode, same trials) ===")
    t0 = time.time()
    modes = {"b1.0_e1e-6": dict(mode="scalar"), "b0.7_e1e-6": dict(mode="scalar", beta=0.7),
             "b1.0_e1e-3": dict(mode="scalar", eps=1e-3), "b0.7_e1e-3": dict(mode="scalar", beta=0.7, eps=1e-3)}
    agg = run_trials(4, 6.0, modes, 80, 8, SEED + 106)
    for n, a in agg.items():
        nm = a["nmse"]; jump = np.any(nm[:, 2:] > 1.5 * np.minimum.accumulate(nm, 1)[:, 1:-1], axis=1).sum()
        P(f" {n}: jumps {jump}/80 | NMSE mean {fmt(nm.mean(0), '{:.4f}')} | BLER last {a['blk_err'].mean(0)[-1]:.3f} | alphaD clip frac {np.mean(a['alphaD'] <= 1.1 * float(n.split('_e')[1])):.2f}")
    P(f"(T4c {time.time() - t0:.0f} s)\n")
if "b" in which:
    P("=== T4b colored-init (Tp=2): is the scalar loss the start (isotropised prior) or the site throughout? ===")
    t0 = time.time()
    modes = {"scalar": dict(mode="scalar"), "cinit1": dict(mode="scalar", init_colored=1),
             "cinit2": dict(mode="scalar", init_colored=2), "colored": dict(mode="colored")}
    for snr in (6.0, 9.0):
        agg = run_trials(2, snr, modes, 80, 8, SEED + 100 + int(snr))
        P(f"--- Tp=2, SNR {snr:.0f} dB ---")
        for n, a in agg.items(): report(n, a)
        P(f"   scalar nu_q: {fmt(agg['scalar']['nu_q'].mean(0))} | cinit1 nu_q: {fmt(agg['cinit1']['nu_q'].mean(0))}")
    P(f"(T4b {time.time() - t0:.0f} s)")
with open(f"/home/claude/t2/exp_0918b_results_{which}.txt", "w") as f: f.write("\n".join(out) + "\n")
