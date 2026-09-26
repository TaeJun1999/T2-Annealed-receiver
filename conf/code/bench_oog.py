"""conf/code/bench_oog.py -- single-thread cost of ONE above-grid prior query for the K2 arms (NEXT_EXPERIMENTS_K1K2 §2.3:
the manuscript "out-of-grid rule" table carries V1-edge with V1-clamp next to it, with cost columns: network
calls and seconds per above-grid query, :83).

Priors are built exactly as the K2 runs built them: diag_prior_swap.build(C1, -3 dB, fits B16e4k, ntrain 1.6e5, headline
checkpoint d2sx_N160000_a1.pt, registered edge_kw) and the arm's .prior is queried directly (prior._eval(q, nu), the one
network(+Jacobian) evaluation the receiver makes per outer iteration).
  (1) network work per query, COUNTED by instrumenting model.raw (every network forward, with its batch size) and
      torch.func.jacrev (reverse-mode Jacobians of the 2N = 64-dim real denoiser) for one query per arm;
  (2) seconds per query, torch.set_num_threads(1) (one CPU thread per K2 worker), at nu = the median iteration-1 nu_q of
      V1-edge in raw_review_next_K2test (above the sigma grid, nu_hi = 1.4285757), plus one in-grid V1 reference at the
      median iteration-2..16 nu_q.  The prior caches an identical (q, nu), so every repetition uses a NEW random
      q = h + CN(0, nu I) with h from the D2 S2 generator (synthetic queries at the recorded nu; the receiver's own q is
      not stored in raw).  One untimed warm-up call per arm.
  (3) per-block network time from the measured above-grid queries per block (<arm>|n_oog in raw_review_next_K2test).
Writes results/review_next/oog_cost.txt.  Read-only on raw.  CPU only.
"""
import os
import socket
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C                          # FIRST: BLAS threads = 1
import numpy as np
import torch
from analysis import load_raw
import diag_prior_swap as DPS

NU_HI = 1.4285757304853552
CKPT = os.path.join(C.CONF, "ckpt", "d2sx_N160000_a1.pt")
EDGE_KW = dict(M=16, burn=100, keep=100, n_jac=16)      # registered (meta|edge_kw of every K2 chunk; eps_frac 0.05 default)
ARMS = ("M-ours-dscore-C-V1", "V1-clamp", "V1-edge")
REPS = {"M-ours-dscore-C-V1": 40, "V1-clamp": 40, "V1-edge": 10}
OUT = os.path.join(C.CONF, "results", "review_next", "oog_cost.txt")
sh = lambda *c: subprocess.run(c, capture_output=True, text=True, cwd=C.CONF).stdout.strip()


def queries(gen, rng, nu, n):
    h = gen.sample_vecs(rng, n)
    return h + np.sqrt(nu / 2) * (rng.standard_normal(h.shape) + 1j * rng.standard_normal(h.shape))


def count_calls(prior, q, nu):
    """(forward batch sizes, #jacrev) of one query.  model.raw is the network (score_real -> raw, once per call)."""
    fw, nj = [], [0]
    raw0, jr0 = prior.model.raw, torch.func.jacrev

    def raw(x, logsig):
        fw.append(1 if x.ndim == 1 else int(x.shape[0])); return raw0(x, logsig)

    def jacrev(*a, **k):
        nj[0] += 1; return jr0(*a, **k)
    prior.model.raw, torch.func.jacrev = raw, jacrev
    try:
        prior._eval(q, nu)
    finally:
        del prior.model.raw; torch.func.jacrev = jr0
    return fw, nj[0]


def fmt_calls(fw, nj):
    b = {}
    for x in fw:
        b[x] = b.get(x, 0) + 1
    fwd = " + ".join(f"{c} x batch {k}" for k, c in sorted(b.items()))
    return f"{len(fw)} network forwards ({fwd}; {sum(fw)} sample-forwards), {nj} jacrev (each = 1 of those forwards + 64 VJPs, vmapped)"


def main():
    torch.set_num_threads(1)
    t_start = time.time()
    x = load_raw("D2", root=os.path.join(C.CONF, "raw_review_next_K2test"))[0][("C1", "S2", -3.0)]
    e = np.asarray(x["V1-edge"]["nu_q"], float)
    nu_out, nu_in = float(np.median(e[:, 0])), float(np.nanmedian(e[:, 1:]))
    assert nu_out > NU_HI > nu_in, (nu_out, nu_in)
    n_blk = len(e)
    oog = {k: float(np.mean(x[k]["n_oog"])) for k in ("V1-edge", "V1-clamp")}
    v1 = np.asarray(x["M-ours-dscore-C-V1"]["nu_q"], float); rec = np.isfinite(v1).all(1)
    oog["M-ours-dscore-C-V1"] = float(np.mean((v1[rec] > NU_HI).sum(1)))           # recorded (non-raised) blocks only

    rxs = DPS.build("C1", -3.0, list(ARMS), "B16e4k", 160000, CKPT, EDGE_KW, {})[0]
    pri = {k: rxs[k].prior for k in ARMS}
    gen = C.make_gen("D2", "S2", 8, 4)
    rng = np.random.default_rng(20260926)
    L = []
    calls = {}
    for k in ARMS:
        fw, nj = count_calls(pri[k], queries(gen, rng, nu_out, 1)[0], nu_out)
        calls[k] = (fw, nj)
    fw_in, nj_in = count_calls(pri["M-ours-dscore-C-V1"], queries(gen, rng, nu_in, 1)[0], nu_in)

    T = {}
    for k, nu in [(a, nu_out) for a in ARMS] + [("V1 in-grid", nu_in)]:
        p = pri["M-ours-dscore-C-V1" if k == "V1 in-grid" else k]
        n0 = getattr(p, "n_oog", 0); ts, bad = [], 0
        for i, q in enumerate(queries(gen, rng, nu, REPS.get(k, 40) + 1)):
            t0 = time.perf_counter(); m, J = p._eval(q, nu); dt = time.perf_counter() - t0
            bad += int(not (np.all(np.isfinite(m)) and np.all(np.isfinite(J))))
            if i:                                                                      # call 0 = warm-up
                ts.append(dt)
        T[k] = (np.array(ts), bad, getattr(p, "n_oog", 0) - n0)
        print(f"[bench] {k:<20} nu {nu:.4f}: median {np.median(ts):.4f} s ({len(ts)} reps)", flush=True)

    t_in = float(np.median(T["V1 in-grid"][0]))
    L += ["oog_cost -- single-thread cost of one ABOVE-grid prior query, K2 arms (code/bench_oog.py)", "",
          f"date      : {sh('date')}",
          f"git       : HEAD {sh('git', 'rev-parse', '--short', 'HEAD')} (bench_oog.py itself is a new, uncommitted file; "
          f"prior_variants.py / diag_prior_swap.py / score.py {'unchanged vs HEAD' if not sh('git', 'status', '--porcelain', 'code/prior_variants.py', 'code/diag_prior_swap.py', 'code/score.py') else 'MODIFIED vs HEAD'})",
          f"host      : {socket.gethostname()}  CPU {sh('sh', '-c', 'grep -m1 \"model name\" /proc/cpuinfo | cut -d: -f2').strip()}  "
          f"load average at end {os.getloadavg()[0]:.2f} / {os.cpu_count()} cores",           # 1-min, read once after the timings
          f"threads   : torch.get_num_threads() = {torch.get_num_threads()}, OMP/MKL/OPENBLAS_NUM_THREADS = "
          f"{os.environ.get('OMP_NUM_THREADS')}/{os.environ.get('MKL_NUM_THREADS')}/{os.environ.get('OPENBLAS_NUM_THREADS')}",
          f"torch     : {torch.__version__}  numpy {np.__version__}  dtype float64  device cpu",
          f"checkpoint: {os.path.relpath(CKPT, C.CONF)} (DiT, vp)  fits B16e4k  ntrain 160000  edge_kw {EDGE_KW} + eps_frac 0.05",
          "",
          "Method: priors built by diag_prior_swap.build('C1', -3, ...) exactly as the K2 runs; prior._eval(q, nu) timed with "
          "time.perf_counter.  nu_above = median iteration-1 nu_q of V1-edge in raw_review_next_K2test (C1 -3 dB, n="
          f"{n_blk}; the value is the same in every block), nu_in = median iteration-2..16 nu_q of V1-edge (in-grid).  Each repetition "
          "uses a new synthetic q = h + CN(0, nu I), h ~ D2 S2 generator (the prior caches an identical (q, nu)); one untimed "
          "warm-up call per arm.  Network work counted by instrumenting model.raw and torch.func.jacrev on one query.",
          f"nu_above = {nu_out:.6f} (> nu_hi {NU_HI:.7f})   nu_in = {nu_in:.6f}", "",
          "Network work per ABOVE-grid query (counted; matches the code: ScorePrior._eval = jacrev(tweedie) + tweedie forward; "
          "clamp = _net(q, s_hi) + _jac(q, s_hi); edge = (burn+keep)=200 Langevin score calls on M=16 chains + keep=100 "
          "denoiser calls on the same batch + n_jac=16 jacrev):"]
    for k in ARMS:
        L.append(f"  {k:<20} {fmt_calls(*calls[k])}")
    L.append(f"  {'V1 in-grid (ref.)':<20} {fmt_calls(fw_in, nj_in)}")
    L += ["", "Seconds per query (single thread):"]
    for k in ARMS + ("V1 in-grid",):
        ts, bad, dn = T[k]
        L.append(f"  {k:<20} median {np.median(ts):.4f} s  min {ts.min():.4f}  max {ts.max():.4f}  reps {len(ts)}  "
                 f"non-finite outputs {bad}" + (f"  above-grid path taken {dn}/{len(ts) + 1}" if k in ("V1-edge", "V1-clamp") else ""))
    L += ["", f"Per-block prior-network time at C1 -3 dB TEST (16 outer iterations = 16 queries per block; raw_review_next_K2test, "
          f"n={n_blk}):"]
    for k in ARMS:
        a, t_out = oog[k], float(np.median(T[k][0]))
        blk = a * t_out + (16 - a) * t_in
        L.append(f"  {k:<20} above-grid queries/block {a:.4f}  -> {blk:.3f} s/block = {blk / (16 * t_in):.2f} x (16 in-grid "
                 f"V1 queries = {16 * t_in:.3f} s);  if all 16 were above-grid: {16 * t_out:.2f} s/block")
    L += [f"  (V1-edge: {int(round(oog['V1-edge'] * n_blk))} above-grid queries in {n_blk} blocks = every block at iteration 1 "
          f"+ 1 block at iteration 2; V1-clamp {int(round(oog['V1-clamp'] * n_blk))}, all at iteration 1.  The frozen V1's count "
          f"is over its {int(rec.sum())} recorded blocks; its {n_blk - int(rec.sum())} raised blocks carry no nu_q record.  "
          "The frozen V1's network work per query is the same above and in the grid (2 forwards + 1 jacrev); its per-block "
          "line uses its own measured above-grid time.)",
          "  Receiver work outside the prior (LMMSE-PIC, BCJR) is not included; timings are on this host at the load above, "
          "not under the multi-worker contention of the K2 runs (128 workers dev 3200..4479, 192 test 0..2559, 64 per report "
          "point; logs/review_next/k2_C1_m3.log, k2test_C1_m3.log, k2_C1_p0.log, k2_C5_m6.log, line 1).",
          f"", f"wall time of this benchmark: {time.time() - t_start:.0f} s"]
    open(OUT, "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
