"""exp_0919 runner — QPSK route (a), Gaussian Kronecker prior (rho = 0.7), 4x4, T = 28, (133,171)_8 nu=6 terminated, 8 iterations.
usage: python exp_0919_run.py <set> <Tp> <snr_db> <n_trials> <skip>
Trials of a (Tp, SNR) point come from one rng stream seeded SEED + 100 + int(snr)  (SEED = 20260919), so chunks (skip, n_trials)
concatenate into one reproducible sequence and every variant sees the same (H, u, perm, Y). Raw per-trial logs -> exp_0919_raw/*.npz."""
import os, sys, time, numpy as np
os.makedirs("./exp_0919_raw", exist_ok=True); os.makedirs("./exp_0920_raw", exist_ok=True)
sys.path.insert(0, ".")
from exp_0919_common import *
SETS = {
  # main grid: v0 scalar, D-11 (cinit1), belief scalarisation (n_inner 1 / 3), references; each with beta in {1, 0.7}
  "main": {f"{n}_b{b}": dict(c, beta=b) for b in (1.0, 0.7) for n, c in {
      "scalar":  dict(mode="scalar"),
      "cinit1":  dict(mode="scalar", init_colored=1),
      "belief1": dict(mode="scalar", scal="belief", n_inner=1),
      "belief3": dict(mode="scalar", scal="belief", n_inner=3),
      "colored": dict(mode="colored"),
      "pilot":   dict(mode="pilot_only"),
      "genie":   dict(mode="genie")}.items()},
}
SETS["core"] = {k: v for k, v in SETS["main"].items() if not k.startswith(("pilot", "genie"))}     # more trials at decision points
SETS["iter16"] = {k: v for k, v in SETS["main"].items() if k.startswith(("scalar", "belief1", "colored"))}   # run with n_iter = 16 (D-12 condition)
# ablations on the default receiver. In the Gaussian testbed D-13 + D-14 == mode 'colored' exactly (T6), so 'colored' stands for the default.
SETS["abl"] = {
    "base":        dict(mode="colored"),
    "post_fb":     dict(mode="colored", feedback="posterior"),                 # (ii) a-posteriori soft symbols into L_H, LOO kept
    "no_loo":      dict(mode="colored", loo=False),                            # (ii) extrinsic symbols, no LOO cavity (full channel posterior in L_X)
    "post_noloo":  dict(mode="colored", feedback="posterior", loo=False),      # (ii) classical a-posteriori code-aided re-estimation (T1 F2)
    "pmf":         dict(mode="colored", dec_ext="pmf"),                        # (iii) Q-04 divide-then-project decoder extrinsic
    "per_sym":     dict(mode="colored", alphaD="per_symbol"),                  # (iv) Q-04' per-symbol alpha^D
    "base_b0.7":   dict(mode="colored", beta=0.7),
    "pmf_b0.7":    dict(mode="colored", dec_ext="pmf", beta=0.7),
    "belief1":     dict(mode="scalar", scal="belief"),
    "belief1_pmf": dict(mode="scalar", scal="belief", dec_ext="pmf"),
    "pilot":       dict(mode="pilot_only"),
    "pilot_pmf":   dict(mode="pilot_only", dec_ext="pmf"),
    "genie_pmf":   dict(mode="genie", dec_ext="pmf"),
}
if __name__ == "__main__":
    sname, Tp, snr, n_trials, skip = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
    n_iter = int(sys.argv[6]) if len(sys.argv) > 6 else 8
    t0 = time.time()
    agg = run_trials(Tp, snr, SETS[sname], skip + n_trials, n_iter, SEED + 100 + int(snr), skip=skip)
    flat = {f"{n}|{k}": v for n, a in agg.items() for k, v in a.items()}
    np.savez_compressed(f"./exp_0919_raw/{sname}_Tp{Tp}_snr{int(snr)}_skip{skip}_n{n_trials}.npz", **flat)
    line = f"[{sname}] Tp={Tp} SNR={snr:.0f} dB trials {skip}..{skip + n_trials - 1} ({time.time() - t0:.0f} s) BLER(last): " + \
           " ".join(f"{n}={a['blk_err'][:, -1].mean():.3f}" for n, a in agg.items())
    print(line, flush=True)
