"""conf/code/diag_p1_cavity.py -- P1-1 of NEXT_EXPERIMENTS v3 (§2.1): the ACTUAL denoiser input (cavity) the
receiver forms, measured with real receiver runs on the DEVELOPMENT set, plus the real-query halves of §2.2
(covariance calibration) and §2.4 (pseudo-covariance r_P).  A P1-x diagnostic, not a gate (§0).

One task = one (cell, snr) point x one development chunk (skip, n) of runner.chunk_plan(C.DEV_SKIP0, 640, 40).
The point is built by runner.build_point exactly as the B16e4k headline (tag B16e4k -> the Nr=8, N=1.6e5 fits,
b* = kron K=1024 asserted; Stage C checkpoint d2sx_N160000_a1.pt = last-EMA, BEST_WEIGHTS_UNAVAILABLE), and the
trial stream is regenerated as runner.run_task does (trials < skip regenerated and dropped), so all arms see the
same (H, u, perm, Y).  Arms (§2.1): V1 = M-ours-dscore-C-V1, V0 = M-ours-dscore-C-V0, M-ours-bstar-scalar (b*
through the belief-scalar wiring: it really forms a scalar cavity), M-ours-bstar (colored ep_site: no (q, nu_q)
exists, G-based quantities only).

Instance-level hooks (Demo/ untouched).  Each wrapper calls the original bound method and COPIES what it returned;
nothing the receiver holds is modified, so the trajectory is unchanged (--smoke re-runs every arm unhooked and
asserts every log key bit-identical):
  rx._sites                               -> G = sum_n A_n, b = sum_n B_n  (the receiver's own sums)
  rx.prior.denoise                        -> q, nu_q, h_H, alpha_H          (belief arms: V1, V0, bstar-scalar)
  rx.prior.denoise_full, rx._matrix_site  -> (m, J) the D-14 site consumed, (P, eta), RouteAClip n_clip/shift deltas
  rx.prior.ep_site, .tilted_moments       -> (P = Lam + G, eta), GMMPriorB n_clip/shift deltas, tilted mean m
Per block x iteration (§2.1): nu_q; grid exit (sigma = sqrt(nu_q/2) outside the frozen D2 grid [s_lo, s_hi]);
alpha_H (denoiser's tr(J)/N, unclipped; the receiver's clipped one is log_alphaH); clip flag and shift =
sqrt(per-call increment of the shift sum) = |mu_clip - h_H|/|h_H| (V0/V1; bstar: the ep_site analogue);
h_H; h_post (P^-1 (eta + b) for the matrix / ep sites, the SC-VAMP scalar site for bstar-scalar; checked against
the receiver's logged nmse); e_t = |q - h|^2 / (N nu_q); a_t = mean over the top-8 / mean over the bottom-8 of
|v_i^H (q - h)|^2, v_i = eigenvectors of SigL = (I/nu_E + G)^-1 ranked by EIGENVALUE (iteration >= 2; iteration 1
stored NaN), nu_E = the receiver's (checked: this SigL reproduces the receiver's nu_q); |h_post - h_H|/|h_H|
(§2.2 "which mean is preserved"); bstar: eig(G), |V_G^H (h_post - h)|^2, tilted mean m.
Per block: fail = blk_err[-1] (1 if the arm raised), guardH divergence (runner's rule, bigamp.DIVERGE_NMSE), time.
§2.2 real queries: V1/V0's own (m, J) as consumed (V1: project_psd(J), V0: Herm(J)) and the counterfactual exact
GMM b* posterior GMMPriorB.denoise_full at the SAME (q, nu_q): eig(J) and |v_i^H (h - m)|^2 per eigen-direction
(Sigma = nu J).  rho_tr, the unfloored-subspace Mahalanobis / coverage (floor = common.LAM_MIN, unfloored =
eig(J) > 10 floor), floored mass / count, eigen-direction calibration and floor hits are functions of these.
§2.4 real queries: r_P = |nu K|_F / max(|nu J|_F, eps), K = 0.5[(A-D) + j(C+B)], J = wirtinger(Jr) (raw), Jr =
real Jacobian of tweedie_real at V1's recorded (q, nu_q), every iteration (H4 reads iteration 4).  POST-PASS after
the chunk (score.jac_batch on V1's model object; ScorePrior's cache/counters untouched), checked against the J the
receiver consumed (eig(project_psd(J_post)) vs the hooked eig(J)).  The K formula is checked first on a widely-
linear toy map (relative error <= 1e-12, §2.4).

CPU only (CUDA_VISIBLE_DEVICES=""), complex128/float64; h_true is diagnostic only, never given to a receiver.
Outputs (results/review_next/ only):
  p1_cavity/p1_cavity_<point>_skip<s>_n<n>.npz/.txt   one per chunk (finished chunks skipped; parallelisable)
  p1_cavity_<point>.npz/.txt                          --merge: refused unless the chunk set is exactly
                                                      {(2560 + 40k, 40) : k = 0..15} (§0 acceptance check)
    ~/miniforge3/envs/torch/bin/python conf/code/diag_p1_cavity.py --cell C2 --snr -3 --skip 2560
    ~/miniforge3/envs/torch/bin/python conf/code/diag_p1_cavity.py --cell C2 --snr -3 --merge
    ~/miniforge3/envs/torch/bin/python conf/code/diag_p1_cavity.py --smoke        (1 trial -> *_smoke.*)
"""
import argparse
import collections
import glob
import os
import re
import sys
import time
import warnings

os.environ["CUDA_VISIBLE_DEVICES"] = ""                # §0: the receiver path is CPU complex128
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import common as C                                     # first: one BLAS thread (env set before numpy)
import numpy as np
import torch
from scipy.stats import gamma
import arms as A
import bigamp
import runner as R
import score as S

TESTBED, PRIOR = "D2", "S2"
V1, V0, BS, BSTAR = "M-ours-dscore-C-V1", "M-ours-dscore-C-V0", "M-ours-bstar-scalar", "M-ours-bstar"
ARMS = (V1, V0, BS, BSTAR)
DEV_N, CHUNK = 640, 40             # §0 development set: skip 2560..3199 in 16 chunks of 40
A_TOP = 8                          # §2.1 a_t: top-8 vs bottom-8 SigL eigen-directions (null F(16,16))
FLOOR_MULT = 10.0                  # §2.2 unfloored eigen-subspace: eig(J) > 10 * LAM_MIN
EPS_RP = 1e-300                    # §2.4 eps in max(|nu J|_F, eps): value not registered, only guards 0/0
REPORT_ITERS = (1, 2, 4, 8, 16)    # §2.1 metric iterations
IT_H1, IT_H4 = 8, 4                # §1 H1 (iteration 8) and H4 (iteration 4), 1-based
OUTD = os.path.join(C.CONF, "results", "review_next")
CHD = os.path.join(OUTD, "p1_cavity")


# ----------------------------------------------------------------------------- hooks
class Tap:
    """Instance-level hooks on ONE receiver arm; r[field] gets one entry per outer iteration."""

    def __init__(self, rx):
        self.rx, self.hooks = rx, []
        pr = rx.prior
        self._hook(rx, "_sites", self._sites)
        if rx.mode == "scalar":
            self._hook(pr, "denoise", self._denoise)
            if rx.hsite == "matrix":
                self._hook(pr, "denoise_full", self._dfull)
                self._hook(rx, "_matrix_site", self._msite)
        if rx.exact_prior:
            self._hook(pr, "ep_site", self._ep)
            self._hook(pr, "tilted_moments", self._tilt)
        self.reset()

    def _hook(self, obj, name, wrap):
        f = getattr(obj, name)
        w = lambda *a: wrap(f, *a)
        setattr(obj, name, w)
        self.hooks.append((obj, name, w))

    def off(self):                  # instance attribute removed -> the class method is back
        for obj, name, _ in self.hooks:
            delattr(obj, name)

    def on(self):
        for obj, name, w in self.hooks:
            setattr(obj, name, w)

    def reset(self):
        self.r = collections.defaultdict(list)

    def _sites(self, f, Y, Xbar, Tau, eh2):
        d, A_, B = f(Y, Xbar, Tau, eh2)
        self.r["G"].append(A_.sum(0)); self.r["b"].append(B.sum(0))
        return d, A_, B

    def _denoise(self, f, q, nu):
        hH, a = f(q, nu)
        r = self.r
        r["q"].append(q.copy()); r["nu_q"].append(float(nu)); r["hH"].append(np.array(hH)); r["alphaH"].append(float(a))
        return hH, a

    def _dfull(self, f, q, nu):
        m, J = f(q, nu)
        self.r["mJ"].append((np.array(m), np.array(J)))
        return m, J

    def _site(self, P, eta, dclip, dshift):
        self.r["P"].append(P); self.r["eta"].append(np.array(eta))
        self.r["clip"].append(float(dclip)); self.r["shift"].append(float(np.sqrt(max(dshift, 0.0))))

    def _msite(self, f, q, nu, G):
        rx = self.rx
        n0, s0 = rx.n_clip, rx.shift
        P, eta = f(q, nu, G)
        self._site(P, eta, rx.n_clip - n0, rx.shift - s0)
        return P, eta

    def _ep(self, f, G, b, lam_min=0.0):
        pr = self.rx.prior
        n0, s0 = pr.n_clip, pr.shift
        Lam, eta = f(G, b, lam_min)
        self._site(Lam + G, eta, pr.n_clip - n0, pr.shift - s0)      # the receiver's P = Lam + G
        return Lam, eta

    def _tilt(self, f, G, b):
        w, m, Cov = f(G, b)
        self.r["m_tilt"].append(m.copy())
        return w, m, Cov


def calib(m, J, h):
    """§2.2 per-query ingredients: ascending eig of Herm(J) and |v_i^H (h - m)|^2 (Sigma = nu J)."""
    w, V = np.linalg.eigh(0.5 * (J + J.conj().T))
    return w, np.abs(V.conj().T @ (h - m)) ** 2


def post(tap, rx, log, h, iters, gm):
    """One trial of one arm -> {field: (iters,) or (iters, N)}; NaN where the run did not reach an iteration."""
    r, N, I, eps = tap.r, rx.N, np.eye(rx.N), rx.eps
    belief = rx.mode == "scalar"
    score = belief and rx.hsite == "matrix"
    ep = rx.exact_prior
    spec = dict(hpost="c", nmse_post="s", nmse_dev="s")
    if belief:
        spec.update(q="c", nu_q="s", hH="c", alphaH="s", e_t="s", a_t="s", nu_dev="s", post_vs_H="s")
    if score or ep:
        spec.update(clip="s", shift="s")
    if score:
        spec.update(cal_eigJ="r", cal_proj="r", cf_m="c", cf_eigJ="r", cf_proj="r")
    if ep:
        spec.update(G_eig="r", G_proj="r", m_tilt="c")
    o = {f: np.full((iters,) if s == "s" else (iters, N), np.nan, complex if s == "c" else float)
         for f, s in spec.items()}
    if belief:
        nuE = rx.prior.cbar                                   # RouteA.run: nuE before iteration 1
        for t in range(len(r["hH"])):
            q, nu, hH, aH, G, b = r["q"][t], r["nu_q"][t], r["hH"][t], r["alphaH"][t], r["G"][t], r["b"][t]
            SigL = np.linalg.inv(I / nuE + G)                 # RouteA.run belief branch, n_inner = 1
            aL = float(np.clip(np.trace(SigL).real / N / nuE, eps, 1 - eps))
            o["nu_dev"][t] = abs(aL / (1 - aL) * nuE - nu) / nu      # 0 <=> this SigL is the receiver's
            w, V = np.linalg.eigh(SigL)                       # ascending: top-8 = last 8 (by EIGENVALUE)
            err = q - h
            p = np.abs(V.conj().T @ err) ** 2
            if t >= 1:
                o["a_t"][t] = p[-A_TOP:].mean() / p[:A_TOP].mean()
            o["e_t"][t] = np.sum(np.abs(err) ** 2) / (N * nu)
            o["q"][t], o["nu_q"][t], o["hH"][t], o["alphaH"][t] = q, nu, hH, aH
            a = float(np.clip(aH, eps, 1 - eps))
            nuE = a / (1 - a) * nu                            # SC-VAMP (2)-(3), the receiver's expression
            if not score:                                     # hsite='scalar': P = I/nuE + G, site = hE/nuE
                hE = (hH - a * q) / (1 - a)
                o["hpost"][t] = np.linalg.inv(I / nuE + G) @ (hE / nuE + b)
    if score or ep:
        for t in range(len(r["P"])):
            o["hpost"][t] = np.linalg.inv(r["P"][t]) @ (r["eta"][t] + r["b"][t])
            o["clip"][t], o["shift"][t] = r["clip"][t], r["shift"][t]
    if score:
        for t, (m, J) in enumerate(r["mJ"]):
            o["cal_eigJ"][t], o["cal_proj"][t] = calib(m, J, h)
            mc, Jc = gm.denoise_full(r["q"][t], r["nu_q"][t])  # counterfactual: exact b* at the SAME (q, nu_q)
            o["cf_m"][t] = mc
            o["cf_eigJ"][t], o["cf_proj"][t] = calib(mc, Jc, h)
    if ep:
        for t in range(len(r["P"])):
            wG, VG = np.linalg.eigh(r["G"][t])
            o["G_eig"][t], o["G_proj"][t] = wG, np.abs(VG.conj().T @ (o["hpost"][t] - h)) ** 2
            o["m_tilt"][t] = r["m_tilt"][t]
    o["nmse_post"] = np.sum(np.abs(o["hpost"] - h) ** 2, 1) / np.sum(np.abs(h) ** 2)
    if belief:
        o["post_vs_H"] = np.linalg.norm(o["hpost"] - o["hH"], axis=1) / np.linalg.norm(o["hH"], axis=1)
    for k in C.KEYS_LOG:
        o["log_" + k] = np.asarray(log[k], float) if log is not None else np.full(iters, np.nan)
    o["nmse_dev"] = np.abs(o["nmse_post"] - o["log_nmse"]) / o["log_nmse"]
    o["raised"] = float(log is None)
    o["fail"] = 1.0 if log is None else float(log["blk_err"][-1])
    with np.errstate(invalid="ignore"):
        o["diverged"] = float(np.any(~np.isfinite(o["log_nmse"]) | (o["log_nmse"] > bigamp.DIVERGE_NMSE)))
    return o


# ----------------------------------------------------------------------------- §2.4 real-Jacobian post-pass
def k_and_j(Jr):
    """(..., 2N, 2N) real Jacobian [[A, B], [C, D]] -> K = dm/dq* = 0.5[(A-D) + j(C+B)], J = dm/dq = wirtinger."""
    n = Jr.shape[-1] // 2
    a, b, c, d = Jr[..., :n, :n], Jr[..., :n, n:], Jr[..., n:, :n], Jr[..., n:, n:]
    return 0.5 * torch.complex(a - d, c + b), S.wirtinger(Jr)


def check_k(N=8, seed=0):
    """§2.4 transform check: for the widely-linear m = M q + W q* the jacrev path must give K = W, J = M."""
    g = np.random.default_rng(seed)
    M, W = g.standard_normal((2, N, N)) + 1j * g.standard_normal((2, N, N))
    # the same map on [Re q, Im q] (vmap has no batching rule for complex conj views)
    Rm = torch.as_tensor(np.block([[M.real + W.real, W.imag - M.imag], [M.imag + W.imag, M.real - W.real]]))
    f = lambda v, s: Rm @ v
    K, J = k_and_j(S.jac_batch(f, torch.as_tensor(g.standard_normal((3, 2 * N))), torch.ones(3, dtype=torch.float64)))
    rel = lambda X, Y: float(np.abs(X.numpy() - Y).max() / np.abs(Y).max())
    return max(rel(K, W), rel(J, M))


def rp_real(model, Q, nu, chunk=64):
    """|K|_F, |J|_F (raw Wirtinger) and eig(project_psd(J)) of tweedie_real at the queries (Q, nu)."""
    f = lambda v, s: S.tweedie_real(model, v, s)
    nK, nJ, ev = [], [], []
    for i in range(0, len(Q), chunk):
        x = torch.as_tensor(S.np_pack(Q[i:i + chunk]), dtype=torch.float64)
        s = torch.as_tensor(S.NU_TO_SIGMA(nu[i:i + chunk]), dtype=torch.float64)
        K, J = (t.numpy() for t in k_and_j(S.jac_batch(f, x, s)))
        nK.append(np.linalg.norm(K, axis=(1, 2))); nJ.append(np.linalg.norm(J, axis=(1, 2)))
        ev.append(np.linalg.eigvalsh(np.stack([S.project_psd(j) for j in J])))
    return np.concatenate(nK), np.concatenate(nJ), np.concatenate(ev)


# ----------------------------------------------------------------------------- one chunk
def point_name(cell, snr):
    c = C.CELLS[cell]
    pil = C.make_pilots(TESTBED, PRIOR, c["Nt"], c["Tp"], c["Nr"])[0]
    return f"{TESTBED}_{cell}_{PRIOR}_Nr{c['Nr']}_T{c['T']}_Tp{c['Tp']}_{pil}_snr{int(snr)}"


def run_chunk(a):
    pt = point_name(a.cell, a.snr)
    base = os.path.join(CHD, f"p1_cavity_{pt}_skip{a.skip}_n{a.n}" + ("_smoke" if a.smoke else ""))
    if os.path.exists(base + ".npz") and not a.smoke:
        print(f"exists  {base}.npz"); return
    t00 = time.time()
    k_toy = check_k()
    assert k_toy <= 1e-12, f"K/J transform check failed: {k_toy:.3e}"
    R._init(a.tag)                                            # -> A.D2_FITS = gmm_fits_D2_<tag>
    P = R.build_point(TESTBED, a.cell, PRIOR, a.snr, a.ntrain, stagec_ckpt=a.ckpt)
    meta = P["meta"]
    miss = [k for k in ARMS if k not in P["arms"]]
    if miss:
        sys.exit(f"arms not built: {miss} -- {P['stagec']}")
    assert meta["bstar"] == "kron" and int(meta["kron_K"]) == 1024, (meta["bstar"], meta["kron_K"])   # §0
    s_lo, s_hi = S._sigma_range(TESTBED)[:2]                  # the FROZEN D2 grid (tag "")
    for k in (V1, V0):
        assert (P["arms"][k].prior.s_lo, P["arms"][k].prior.s_hi) == (s_lo, s_hi), "ScorePrior grid != frozen D2 grid"
    arms = {k: P["arms"][k] for k in ARMS}
    taps = {k: Tap(rx) for k, rx in arms.items()}
    gm = arms[BS].prior                  # the raw b* object (kron K=1024); its denoise_full is not hooked
    code, gen, first = P["code"], P["gen"], P["arms"]["R5-genie"]
    rng = C.trial_rng(TESTBED, PRIOR, P["Nr"], P["T"], P["Tp"], a.snr)
    rows, trials, hs = {k: [] for k in ARMS}, [], []
    for tr in range(a.skip + a.n):                            # runner.run_task's stream, verbatim
        H = gen.sample(rng)
        u = rng.integers(0, 2, code.K)
        perm = rng.permutation(code.Ns)
        X, Y = first.transmit(u, perm, H, rng)
        if tr < a.skip:
            continue
        h = H.reshape(-1, order="F")
        for k, rx in arms.items():
            so = R.stats_obj(rx)
            if so is not None:
                so.reset_stats()
            taps[k].reset()
            t0 = time.perf_counter()
            try:
                log = rx.run(Y, H, u, perm, a.iters)
            except Exception as ex:                           # classified, never dropped
                log = None
                print(f"[p1] trial {tr} {k}: raised {type(ex).__name__}: {ex}", flush=True)
            sec = time.perf_counter() - t0
            o = post(taps[k], rx, log, h, a.iters, gm)
            o["sec"] = sec
            if a.smoke:                                       # hooks must not change the trajectory
                taps[k].off()
                lg = rx.run(Y, H, u, perm, a.iters)
                taps[k].on()
                assert log is not None and set(lg) == set(log) and all(
                    np.array_equal(lg[q], log[q], equal_nan=True) for q in lg), f"{k}: hooked run differs"
            rows[k].append(o)
        trials.append(tr); hs.append(h)
        print(f"[p1] trial {tr} done ({time.time() - t00:.0f} s)", flush=True)

    out = {f"{k}|{f}": np.stack([o[f] for o in rows[k]]) for k in ARMS for f in rows[k][0]}
    for k in (V1, V0, BS):
        sg = np.sqrt(out[f"{k}|nu_q"] / 2)
        with np.errstate(invalid="ignore"):
            out[f"{k}|grid_exit"] = np.where(np.isfinite(sg), (sg < s_lo) | (sg > s_hi), np.nan)
    nuV = out[f"{V1}|nu_q"]; ok = np.isfinite(nuV)
    nK, nJ, evp = rp_real(arms[V1].prior.model, out[f"{V1}|q"][ok], nuV[ok])
    for f, v in (("rp_normK", nK), ("rp_normJ", nJ)):
        out[f"{V1}|{f}"] = np.full(nuV.shape, np.nan); out[f"{V1}|{f}"][ok] = v
    out[f"{V1}|r_P"] = nuV * out[f"{V1}|rp_normK"] / np.maximum(nuV * out[f"{V1}|rp_normJ"], EPS_RP)
    jdev = float(np.abs(evp - out[f"{V1}|cal_eigJ"][ok]).max()) if ok.any() else np.nan
    out["trial"], out["h_true"] = np.array(trials), np.array(hs)
    cid = S.ckpt_identity(a.ckpt)
    m = dict(point=pt, cell=a.cell, snr=a.snr, skip=a.skip, n=a.n, iters=a.iters, smoke=a.smoke, tag=a.tag,
             fits=A.D2_FITS, ntrain=a.ntrain, bstar=meta["bstar"], kron_K=int(meta["kron_K"]), ckpt=a.ckpt,
             ckpt_id=R.stagec_id_str(a.ckpt), ckpt_sha=cid["sha256_16"], s_lo=s_lo, s_hi=s_hi, git=C.git_commit(),
             k_toy=k_toy, jdev=jdev, wall=time.time() - t00)
    out.update({f"meta|{k}": np.array(v) for k, v in m.items()})
    os.makedirs(CHD, exist_ok=True)
    np.savez_compressed(base + ".tmp.npz", **out)             # atomic: a killed run leaves no "exists" chunk
    os.replace(base + ".tmp.npz", base + ".npz")
    txt = summary(out)
    with open(base + ".txt", "w") as f:
        f.write(txt + "\n")
    print(txt + f"\n# saved {base}.npz / .txt", flush=True)


# ----------------------------------------------------------------------------- merge (tiny)
def merge(cell, snr):
    """The 16 development chunks of one point -> p1_cavity_<point>.npz.  §0 acceptance: exactly the plan."""
    pt = point_name(cell, snr)
    plan = R.chunk_plan(C.DEV_SKIP0, DEV_N, CHUNK)
    have = sorted((int(s), int(n)) for s, n in (re.search(r"_skip(\d+)_n(\d+)\.npz$", p).groups()
                  for p in glob.glob(os.path.join(CHD, f"p1_cavity_{pt}_skip*_n*.npz")) if not p.endswith("_smoke.npz")))
    if have != sorted(plan):
        sys.exit(f"refused: chunk set {have} != the development plan {plan} (NEXT_EXPERIMENTS §0)")
    Zs = [dict(np.load(os.path.join(CHD, f"p1_cavity_{pt}_skip{s}_n{n}.npz"))) for s, n in plan]
    per_chunk = ("meta|skip", "meta|n", "meta|wall", "meta|jdev", "meta|k_toy", "meta|git")
    for k in Zs[0]:                                          # same point / arms / fits / ckpt / iters in every chunk
        if k.startswith("meta|") and k not in per_chunk and len({str(z[k]) for z in Zs}) != 1:
            sys.exit(f"refused: chunks differ in {k}: {sorted({str(z[k]) for z in Zs})}")
    if any(set(z) != set(Zs[0]) for z in Zs):
        sys.exit("refused: chunks carry different field sets")
    out = {k: (Zs[0][k] if k.startswith("meta|") else np.concatenate([z[k] for z in Zs])) for k in Zs[0]}
    out.update({"meta|skip": np.array(C.DEV_SKIP0), "meta|n": np.array(DEV_N),
                "meta|wall": np.array(sum(float(z["meta|wall"]) for z in Zs)),
                "meta|jdev": np.array(max(float(z["meta|jdev"]) for z in Zs)),
                "meta|k_toy": np.array(max(float(z["meta|k_toy"]) for z in Zs)),
                "meta|git": np.array(" ".join(sorted({str(z["meta|git"]) for z in Zs})))})
    base = os.path.join(OUTD, f"p1_cavity_{pt}")
    np.savez_compressed(base + ".npz", **out)
    txt = summary(out)
    with open(base + ".txt", "w") as f:
        f.write(txt + "\n")
    print(txt + f"\n# saved {base}.npz / .txt", flush=True)


# ----------------------------------------------------------------------------- summary
def _mq(x):
    x = np.asarray(x, float).ravel(); x = x[np.isfinite(x)]
    return f"{np.median(x):.3g} [{np.percentile(x, 25):.3g},{np.percentile(x, 75):.3g}]" if len(x) else "-"


def _g(x, f="{:.3g}"):
    return f.format(x) if np.isfinite(x) else "-"


def _nanmean(x):
    x = np.asarray(x, float); x = x[np.isfinite(x)]
    return float(x.mean()) if len(x) else np.nan


def cal_stats(eigJ, proj, nu):
    """§2.2 at one iteration over blocks: Sigma = nu J; unfloored = eig(J) > FLOOR_MULT * LAM_MIN.
    rho = the full-space rho_tr (all blocks, V0's indefinite trace included); every subspace / Mahalanobis /
    floor quantity (rho_unf = rho_tr on the unfloored subspace, the H2 / C-calib form; d2/dim; coverage;
    floored count, error share mfl and eigen-mass share mfe) is over the PSD subset only (§2.2: V0 -> "rho_tr
    only, coverage on the PSD subset with its fraction"; V1 and the GMM are PSD by construction).  hit = an
    eigenvalue AT the project_psd floor (not merely <= it: V0's negative eigenvalues are no floor hits)."""
    ok = np.isfinite(nu)
    if not ok.any():
        return dict(rho=np.nan, rho_unf=np.nan, d2dim=np.nan, c50=np.nan, c90=np.nan, nfl=np.nan, mfl=np.nan,
                    mfe=np.nan, hit=np.nan, psd=np.nan)
    eigJ, proj, nu = eigJ[ok], proj[ok], nu[ok]
    err2 = proj.sum(1)
    rho = err2.sum() / np.sum(nu * eigJ.sum(1))
    hit = float(np.mean(np.any(np.abs(eigJ - C.LAM_MIN) <= 1e-6 * C.LAM_MIN, 1)))
    psd = eigJ.min(1) > 0
    out = dict(rho=rho, hit=hit, psd=float(psd.mean()))
    if not psd.any():
        return dict(out, rho_unf=np.nan, d2dim=np.nan, c50=np.nan, c90=np.nan, nfl=np.nan, mfl=np.nan, mfe=np.nan)
    eigJ, proj, nu, err2 = eigJ[psd], proj[psd], nu[psd], err2[psd]
    unf = eigJ > FLOOR_MULT * C.LAM_MIN
    S_ = nu[:, None] * eigJ
    d2 = np.sum(np.where(unf, proj / np.where(unf, S_, 1.0), 0.0), 1)
    dim = unf.sum(1)
    with np.errstate(invalid="ignore", divide="ignore"):
        c50, c90 = d2 <= gamma.ppf(0.5, dim), d2 <= gamma.ppf(0.9, dim)   # complex: d2 ~ Gamma(dim, 1)
        return dict(out, rho_unf=np.sum(np.where(unf, proj, 0)) / np.sum(np.where(unf, S_, 0)),
                    d2dim=float(np.nanmedian(d2 / dim)), c50=_nanmean(c50), c90=_nanmean(c90),
                    nfl=float(np.mean(eigJ.shape[1] - dim)), mfl=float(np.nanmedian(np.sum(np.where(unf, 0, proj), 1) / err2)),
                    mfe=float(np.nanmedian(np.sum(np.where(unf, 0, eigJ), 1) / eigJ.sum(1))))


def summary(Z):
    with warnings.catch_warnings():                       # all-NaN slices (iteration 1 a_t, tiny n) -> "-"
        warnings.simplefilter("ignore", RuntimeWarning)
        return _summary(Z)


def _summary(Z):
    m = lambda k: Z["meta|" + k][()]
    n, iters = len(Z["trial"]), int(m("iters"))
    its = [t for t in REPORT_ITERS if t <= iters]
    L = [C.header(TESTBED, extra=[
        "content     : P1-1 cavity (NEXT_EXPERIMENTS v3 §2.1) + real-query parts of §2.2 / §2.4; DEVELOPMENT set; "
        "diagnostic P1-x, not a gate; h_true diagnostic only",
        f"point       : {m('point')}  trials {m('skip')}..{m('skip') + n - 1}  n = {n}" + ("  [SMOKE]" if m("smoke") else ""),
        f"arms        : {', '.join(ARMS)}  (paired: same H, u, perm, Y)",
        f"GMM b*      : {m('bstar')} K={m('kron_K')}  fits {m('fits')}  N_train {m('ntrain')}",
        f"checkpoint  : {m('ckpt')}  {m('ckpt_id')}",
        f"grid        : frozen D2 sigma grid (20 pts) [s_lo, s_hi] = [{m('s_lo'):.4f}, {m('s_hi'):.4f}]; "
        f"unfloored = eig(J) > {FLOOR_MULT:g} x LAM_MIN = {FLOOR_MULT * C.LAM_MIN:g}",
        f"seeds       : trial stream only (common.trial_rng, SEED {C.SEED}); no other randomness",
        f"run device  : CPU only (CUDA_VISIBLE_DEVICES=''), 1 thread, complex128/float64 (receiver and r_P post-pass)",
        f"run         : git {m('git')}  wall {float(m('wall')):.0f} s  outer iterations {iters}"])]
    L += ["", f"## §2.1 cavity -- block median [IQR]; exit = sigma(nu_q) outside the grid; shift = median over clipped calls",
          f"{'arm':<20}{'it':>3} {'e_t':>24} {'a_t':>24} {'exit':>6} {'alpha_H':>8} {'clip':>6} {'shift':>9} "
          f"{'NMSE h_post':>12} {'|hp-hH|/|hH|':>13} {'BLER':>6}"]
    for k in (V1, V0, BS):
        for t in its:
            i = t - 1
            cl = Z.get(f"{k}|clip")
            clip = _nanmean(cl[:, i]) if cl is not None else np.nan
            sh = Z[f"{k}|shift"][:, i][cl[:, i] > 0] if cl is not None else []
            L.append(f"{k:<20}{t:>3} {_mq(Z[f'{k}|e_t'][:, i]):>24} {_mq(Z[f'{k}|a_t'][:, i]):>24} "
                     f"{_g(_nanmean(Z[f'{k}|grid_exit'][:, i]), '{:.3f}'):>6} {_g(np.nanmedian(Z[f'{k}|alphaH'][:, i])):>8} "
                     f"{_g(clip, '{:.3f}'):>6} {_g(np.median(sh) if len(sh) else np.nan):>9} "
                     f"{_g(np.nanmedian(Z[f'{k}|nmse_post'][:, i])):>12} {_g(np.nanmedian(Z[f'{k}|post_vs_H'][:, i])):>13} "
                     f"{_g(_nanmean(Z[f'{k}|log_blk_err'][:, i]), '{:.3f}'):>6}")
    L += ["", f"## §2.1 {BSTAR} (colored ep_site; G-based only)",
          f"{'it':>3} {'clip':>6} {'shift':>9} {'NMSE h_post':>12} {'NMSE m_tilt':>12} {'eig G min':>10} {'eig G max':>10} {'BLER':>6}"]
    h2 = np.sum(np.abs(Z["h_true"]) ** 2, 1)
    for t in its:
        i = t - 1
        cl = Z[f"{BSTAR}|clip"][:, i]; sh = Z[f"{BSTAR}|shift"][:, i][cl > 0]
        nm_t = np.sum(np.abs(Z[f"{BSTAR}|m_tilt"][:, i] - Z["h_true"]) ** 2, 1) / h2
        L.append(f"{t:>3} {_g(_nanmean(cl), '{:.3f}'):>6} {_g(np.median(sh) if len(sh) else np.nan):>9} "
                 f"{_g(np.nanmedian(Z[f'{BSTAR}|nmse_post'][:, i])):>12} {_g(np.nanmedian(nm_t)):>12} "
                 f"{_g(np.nanmedian(Z[f'{BSTAR}|G_eig'][:, i, 0])):>10} {_g(np.nanmedian(Z[f'{BSTAR}|G_eig'][:, i, -1])):>10} "
                 f"{_g(_nanmean(Z[f'{BSTAR}|log_blk_err'][:, i]), '{:.3f}'):>6}")
    L += ["", "## §2.2 real-query calibration (Sigma = nu J); rho_tr = sum|h-m|^2 / sum tr Sigma (all blocks); "
          "on the PSD subset (psd = its fraction): rho_unf = rho_tr on the unfloored subspace (H2 / C-calib form), d2/dim, "
          "coverage, #fl = mean count outside it, mfl / mfe = median floored share of |h-m|^2 / of tr Sigma; "
          "hit = frac with an eigenvalue at the LAM_MIN floor",
          f"{'source':<22}{'it':>3} {'rho_tr':>8} {'rho_unf':>8} {'d2/dim':>8} {'cov50':>6} {'cov90':>6} {'#fl':>6} "
          f"{'mfl':>8} {'mfe':>8} {'hit':>6} {'psd':>6}"]
    for lab, k, pre in (("V1 own (J_psd)", V1, "cal"), ("V0 own (Herm J)", V0, "cal"),
                        ("GMM b* cf @ V1 (q,nu)", V1, "cf"), ("GMM b* cf @ V0 (q,nu)", V0, "cf")):
        for t in its:
            i = t - 1
            c = cal_stats(Z[f"{k}|{pre}_eigJ"][:, i], Z[f"{k}|{pre}_proj"][:, i], Z[f"{k}|nu_q"][:, i])
            L.append(f"{lab:<22}{t:>3} {_g(c['rho']):>8} {_g(c['rho_unf']):>8} {_g(c['d2dim']):>8} {_g(c['c50'], '{:.3f}'):>6} "
                     f"{_g(c['c90'], '{:.3f}'):>6} {_g(c['nfl'], '{:.2f}'):>6} {_g(c['mfl']):>8} {_g(c['mfe']):>8} "
                     f"{_g(c['hit'], '{:.3f}'):>6} {_g(c['psd'], '{:.3f}'):>6}")
    rp = Z[f"{V1}|r_P"]
    L += ["", "## §2.4 real-query r_P (V1) = |nu K|_F / max(|nu J|_F, eps), J = raw Wirtinger",
          "  it " + " ".join(f"{t:>9}" for t in its),
          "  med" + " ".join(f"{_g(np.nanmedian(rp[:, t - 1])):>9}" for t in its),
          "  max" + " ".join(f"{_g(np.nanmax(rp[:, t - 1]) if np.isfinite(rp[:, t - 1]).any() else np.nan):>9}" for t in its)]
    if iters >= IT_H1:
        L += ["", f"## inputs of the registered rules (the verdicts belong to the full C2 -3 dB development point, n = {DEV_N})",
              f"H1: V1 iteration {IT_H1} block medians  e_{IT_H1} = {_g(np.nanmedian(Z[f'{V1}|e_t'][:, IT_H1 - 1]), '{:.4g}')}  "
              f"a_{IT_H1} = {_g(np.nanmedian(Z[f'{V1}|a_t'][:, IT_H1 - 1]), '{:.4g}')}   (rule: reject H1 iff e in [0.7, 1.4] AND a <= 3)",
              f"H4: V1 iteration {IT_H4} block r_P median = {_g(np.nanmedian(rp[:, IT_H4 - 1]), '{:.4g}')}   "
              f"(rule: reject H4 iff median < 0.2 OR LR p >= 0.05 in the NMSE + nu_q logistic model -- LR test not computed here)"]
    L += ["", "## per block"]
    for k in ARMS:
        L.append(f"{k:<20} fail@{iters} {int(np.sum(Z[f'{k}|fail']))}/{n}  raised {int(np.sum(Z[f'{k}|raised']))}  "
                 f"diverged(guardH) {int(np.sum(Z[f'{k}|diverged']))}  sec/block {np.mean(Z[f'{k}|sec']):.1f}")
    nud = max(float(np.nanmax(Z[f"{k}|nu_dev"])) if np.isfinite(Z[f"{k}|nu_dev"]).any() else np.nan for k in (V1, V0, BS))
    nmd = max(float(np.nanmax(Z[f"{k}|nmse_dev"])) if np.isfinite(Z[f"{k}|nmse_dev"]).any() else np.nan for k in ARMS)
    L += ["", f"## consistency: max rel |nu_q(SigL) - nu_q| = {nud:.2e}  max rel |NMSE(h_post) - logged nmse| = {nmd:.2e}  "
              f"max |eig project_psd(J_post) - eig J_hooked| = {float(m('jdev')):.2e}  K/J toy rel err = {float(m('k_toy')):.2e}"]
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--cell", default="C2", choices=("C1", "C2", "C5"))
    ap.add_argument("--snr", type=float, default=-3.0)
    ap.add_argument("--skip", type=int, default=C.DEV_SKIP0, help="chunk start (one of runner.chunk_plan(2560, 640, 40))")
    ap.add_argument("--n", type=int, default=CHUNK)
    ap.add_argument("--iters", type=int, default=C.N_ITER)
    ap.add_argument("--tag", default="B16e4k", help="GMM fit directory tag (§0 headline)")
    ap.add_argument("--ntrain", type=int, default=160000)
    ap.add_argument("--ckpt", default=os.path.join(C.CONF, "ckpt", "d2sx_N160000_a1.pt"))
    ap.add_argument("--smoke", action="store_true", help="1 trial of the first development chunk -> *_smoke.*")
    ap.add_argument("--merge", action="store_true", help="merge the 16 chunks of (cell, snr)")
    a = ap.parse_args()
    torch.set_num_threads(1)
    if a.merge:
        return merge(a.cell, a.snr)
    if a.smoke:
        a.skip, a.n = C.DEV_SKIP0, 1
    elif (a.skip, a.n) not in R.chunk_plan(C.DEV_SKIP0, DEV_N, CHUNK):
        sys.exit(f"(skip, n) = ({a.skip}, {a.n}) is not a development chunk {R.chunk_plan(C.DEV_SKIP0, DEV_N, CHUNK)}")
    run_chunk(a)


if __name__ == "__main__":
    main()
