"""(10_SPEC_stageC §6q, item A8) Module H cost per call: fitted GMM vs learned score.

The receiver calls Module H ONCE per outer iteration (16 per trial), through the identical entry point
`prior.denoise_full(q, nu) -> (m, J)`.  Everything else in the loop is shared by every arm, so this
single call IS the complexity difference between the arms.  Nothing else here is claimed.

Fairness conditions, all enforced below:
  - same q, same nu, same process, float64, ONE thread (the receiver runs one thread per worker)
  - the ScorePrior caches on (q, nu), so every call gets a FRESH q -- otherwise the learned arm would
    be timed on a cache hit and look free
  - the GMM is b* selected by validation log-likelihood, exactly the arm in the BLER tables
  - both are timed on the same nu grid the receiver actually queries

Report-only.  Selects nothing, changes no arm, and is not a BLER measurement.
"""
import os
import sys
import time

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import common as C
import arms as A
import score as S

TESTBED, PRIOR, NR, NT = "D2", "S2", 8, C.NT
NTRAIN = 10000
CKPT = os.path.join(C.CONF, "ckpt", "d2sx_N10000_a1.pt")
OUT = os.path.join(C.CONF, "results", "complexity_moduleH.txt")
# the nu values the receiver actually queries in C2 (from results/sigma_grid_D2.txt and §6j):
# iteration 1 at -3 dB is nu ~ 0.50; later iterations fall towards ~0.008 at +15 dB.
NUS = (0.50, 0.25, 0.05, 0.008)
REPS = 40


def timed(fn, q_list, nu):
    fn(q_list[0], nu)                                   # warm-up, not timed
    t0 = time.perf_counter()
    for q in q_list:
        fn(q, nu)
    return (time.perf_counter() - t0) / len(q_list)


def main():
    rng = np.random.default_rng(20260922)
    gm, fits, llv, bstar, kron_K = A.module_h_priors(TESTBED, PRIOR, NR, NT, NTRAIN)
    gmm = gm[bstar]
    K = int(np.atleast_1d(fits[("kron", kron_K)]["pi"]).size) if bstar == "kron" else \
        int(np.atleast_1d(fits[("full", int(bstar[3:]))]["pi"]).size)
    Chat = np.cov(A.training_set(TESTBED, PRIOR, NR, NT, NTRAIN).T, bias=True) \
        if False else gmm.C                              # ScorePrior only uses Chat for bookkeeping
    sp = S.ScorePrior(CKPT, NR, NT, Chat, device="cpu", psd_project=False)
    sp1 = S.ScorePrior(CKPT, NR, NT, Chat, device="cpu", psd_project=True)
    npar = sum(p.numel() for p in sp.model.parameters())

    N = NR * NT
    lines = []
    w = lines.append
    w("# (10_SPEC_stageC §6q A8) Module H cost per call -- fitted GMM vs learned score")
    w(f"# date        : {time.strftime('%Y-%m-%d %H:%M:%S')} KST")
    w(f"# host        : CPU, float64, ONE thread (OMP_NUM_THREADS={os.environ['OMP_NUM_THREADS']}); "
      f"the receiver runs one thread per worker process")
    w(f"# entry point : prior.denoise_full(q, nu) -> (m, J).  Called ONCE per outer iteration, 16 per trial.")
    w(f"# GMM arm     : b* = {bstar}  (K = {K} components, selected by validation log-likelihood)")
    w(f"# learned arm : {os.path.basename(CKPT)}  ({npar:,} parameters)")
    w(f"# fresh q per call (the ScorePrior caches on (q, nu); a repeated q would time a cache hit)")
    w(f"# reps        : {REPS} calls per (arm, nu)")
    w("")
    w(f"{'nu':>8}  {'sigma_t':>8} | {'GMM b* (ms)':>13} {'score V0 (ms)':>14} {'score V1 (ms)':>14} | "
      f"{'V0/GMM':>8} {'V1/GMM':>8}")
    rows = []
    for nu in NUS:
        qs = [(rng.standard_normal(N) + 1j * rng.standard_normal(N)) / np.sqrt(2) for _ in range(REPS)]
        tg = timed(gmm.denoise_full, qs, nu)
        t0 = timed(sp.denoise_full, qs, nu)
        t1 = timed(sp1.denoise_full, qs, nu)
        s = float(S.NU_TO_SIGMA(nu))
        w(f"{nu:>8.3f}  {s:>8.4f} | {tg*1e3:>13.3f} {t0*1e3:>14.3f} {t1*1e3:>14.3f} | "
          f"{t0/tg:>8.1f} {t1/tg:>8.1f}")
        rows.append((nu, tg, t0, t1))
    w("")
    g = np.mean([r[1] for r in rows]); a0 = np.mean([r[2] for r in rows]); a1 = np.mean([r[3] for r in rows])
    w(f"mean over the four nu: GMM {g*1e3:.3f} ms, score V0 {a0*1e3:.3f} ms, score V1 {a1*1e3:.3f} ms")
    w(f"  -> the learned prior costs {a0/g:.1f}x the GMM per Module H call (V1: {a1/g:.1f}x).")
    w(f"  -> per trial (16 outer iterations): GMM {16*g*1e3:.1f} ms, score V0 {16*a0*1e3:.1f} ms, "
      f"V1 {16*a1*1e3:.1f} ms.")
    w(f"  -> V1 minus V0 = the PSD projection (one {N}x{N} Hermitian eigendecomposition): "
      f"{(a1-a0)*1e3:.3f} ms, {100*(a1-a0)/a0:.1f}% of the V0 call.")
    w("")
    w("WHAT THIS DOES AND DOES NOT SAY")
    w("  - It is INFERENCE cost only.  Training / fitting cost is separate and is already a column of")
    w("    TABLE A in every results table (GMM EM wall-clock); the score model's training wall-clock is")
    w("    in LADDER_C.md.  Neither is included here.")
    w("  - It is ONE implementation on ONE machine: numpy/BLAS for the GMM, torch.func.jacrev for the")
    w("    network, both float64 single-thread.  A different Jacobian implementation (forward-mode,")
    w("    batched, or an analytic head) would change the learned arm's number and not the GMM's.")
    w("  - The GMM cost scales with K; the learned cost does not.  At b* = K above, that is the")
    w("    comparison the BLER tables actually used.")
    w("  - If the learned arm is the more expensive one, then the equal-budget claim in this work is")
    w("    'same training data', NOT 'same inference complexity', and must be written that way.")
    with open(OUT, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\n-> {OUT}")


if __name__ == "__main__":
    main()
