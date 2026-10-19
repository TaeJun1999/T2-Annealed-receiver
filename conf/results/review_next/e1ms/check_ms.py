"""E1+ V1-ms checks (prompt 확인 1 · 2; development trials only).  cd ~/t2_wtMS/conf && python results/review_next/e1ms/check_ms.py"""
import sys; sys.path.insert(0, "code")
import numpy as np
import common as C, arms as A, runner as R

def site(prior, q, nu, G, lam_min):
    """RouteAClip._matrix_site (clip='eta') on a bare object -- the receiver's own method."""
    rx = type("Rx", (), {})(); rx.prior, rx.I_N, rx.lam_min, rx.clip = prior, np.eye(len(q)), lam_min, "eta"
    rx.n_site = rx.n_clip = 0; rx.shift = 0.0
    return C.RouteAClip._matrix_site(rx, q, nu, G)

# 확인 2: isotropic J (= c I) and no eigenvalue clipping -> V1 and V1-ms give the same site
rng = np.random.default_rng(1); N = 32
q = rng.normal(size=N) + 1j * rng.normal(size=N); m = 0.7 * q; G = np.diag(rng.uniform(0.1, 1, N)).astype(complex)
for c in (0.3, 0.7):
    iso = type("P", (), {"denoise_full": lambda self, q, nu, c=c: (0.7 * q, c * np.eye(len(q)))})()
    P1, e1 = site(iso, q, 0.05, G, C.LAM_MIN); P2, e2 = site(A.MatchedScalarPrior(iso), q, 0.05, G, C.LAM_MIN)
    print(f"isotropic c={c}: max|dP| {np.abs(P1 - P2).max():.2e}  max|deta| {np.abs(e1 - e2).max():.2e}")
    assert np.allclose(P1, P2, rtol=1e-12, atol=1e-12) and np.allclose(e1, e2, rtol=1e-12, atol=1e-12)

# 확인 1: real network, D2 C2 -3 dB, development trials 2560..2561 -- every V1-ms site = the definition
R._init("E1MSchk")
p = R.build_point("D2", "C2", "S2", -3.0, ntrain=160000, stagec_ckpt="/home/HTJ/t2/conf/ckpt/d2sx_N160000_a1.pt", ms_arm=True)
rx, rv1 = p["arms"]["M-ours-dscore-C-V1ms"], p["arms"]["M-ours-dscore-C-V1"]
sp = rx.prior.sp
assert type(rx.prior).__name__ == "MatchedScalarPrior" and sp is not rv1.prior          # fresh prior, own counters
assert rx.prior.denoise.__self__ is sp                                                    # scalar feedback = the wrapped prior's
print("meta ms_arm:", p["meta"].get("ms_arm"))
calls, base = [], type(rx)._matrix_site
def tap(q, nu, G):
    out = base(rx, q, nu, G); calls.append((q.copy(), nu, G.copy(), out)); return out
rx._matrix_site = tap
r = C.trial_rng("D2", "S2", p["Nr"], p["T"], p["Tp"], -3.0); worst = 0.0; nclip = 0
for tr in range(2562):
    H = p["gen"].sample(r); u = r.integers(0, 2, p["code"].K); perm = r.permutation(p["code"].Ns)
    _, Y = rx.transmit(u, perm, H, r)
    if tr < 2560:
        continue
    rx.run(Y, H, u, perm, C.N_ITER)
for q, nu, G, (P, eta) in calls:
    mm, J = sp.denoise_full(q, nu)                         # the cached (m, J+) of that very query
    S = nu * 0.5 * (J + J.conj().T); s = np.trace(S).real / len(q)
    lam = 1 / s - 1 / nu; nclip += lam < rx.lam_min
    Pd = max(lam, rx.lam_min) * np.eye(len(q)) + G; ed = mm / s - q / nu
    worst = max(worst, np.abs(P - Pd).max() / np.abs(Pd).max(), np.abs(eta - ed).max() / max(np.abs(ed).max(), 1e-300))
print(f"fixed-query sites: {len(calls)} calls on trials 2560..2561, max rel. deviation from the definition {worst:.2e}, floored {nclip}")
assert worst < 1e-10
print("CHECK_MS OK")
