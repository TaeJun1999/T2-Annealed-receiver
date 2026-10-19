"""measure_grid_dev.py -- SELECTION_RULE.md addendum (Fable M1): the wide sigma grid of variant (C) re-measured on DEVELOPMENT trials.
sigma.measure_point's receiver, code, pilots, Chat and per-trial draw order (H -> u -> perm -> transmit) VERBATIM, except that the first
SKIP = 2560 trials of each point's stream are drawn and discarded (no receiver run), so the measured trials are 2560 .. 2560+n-1
(sigma.measure_point itself uses 0 .. n-1 = test numbers).  Cells C1 C2, n = sigma.N_MEAS (64), SNR -3 ... +24 dB, then sigma.write (the
same 1-99 percentile / 20-point grid) under a NEW tag.  Nothing under conf/code is changed.
    cd ~/t2/conf && CUDA_VISIBLE_DEVICES= nice -n 10 taskset -c <cpus> python results/review_next/lowsig/measure_grid_dev.py <prior> <tag> <jobs>"""
import multiprocessing as mp, os, sys
sys.path.insert(0, "code")
import numpy as np
import common as C, arms as A, sigma as SG

SKIP = C.DEV_SKIP0
SNRS = [-3.0, 0.0, 3.0, 6.0, 9.0, 12.0, 15.0, 18.0, 21.0, 24.0]


def point(task):
    testbed, prior, cell, snr, n = task
    c = C.CELLS[cell]
    Nr, Nt, T, Tp = c["Nr"], c["Nt"], c["T"], c["Tp"]
    sigma2 = 10 ** (-snr / 10)
    code = C.QAMCode(C.GENS, C.NU, C.M_QAM, Nt * (T - Tp))
    pil, Xp = C.make_pilots(testbed, prior, Nt, Tp, Nr)
    gen = C.make_gen(testbed, prior, Nr, Nt)
    if prior in SG.CHAT_FROM_TRAIN:
        X = A.training_set(testbed, prior, Nr, Nt)
        Chat = X.T @ X.conj() / len(X)
    else:
        Chat = A.load_fits(testbed, prior, Nr)[("full", 32)]["Chat"]
    Cs = C.GaussianPrior(Nr, Nt, Chat)
    rx = A.route_a(Nr, Nt, T, Tp, sigma2, Cs, code, Xp, "score", clip="eta")     # == M-ours-G in the score interface
    rng = C.trial_rng(testbed, prior, Nr, T, Tp, snr)
    vals = []
    for tr in range(SKIP + n):
        H = gen.sample(rng)
        u = rng.integers(0, 2, code.K)
        perm = rng.permutation(code.Ns)
        X, Y = rx.transmit(u, perm, H, rng)
        if tr < SKIP:
            continue
        vals.append(rx.run(Y, H, u, perm, C.N_ITER)["nu_q"])
    return (cell, snr), np.asarray(vals, float)


if __name__ == "__main__":
    prior, tag, jobs = sys.argv[1], sys.argv[2], int(sys.argv[3])
    out = os.path.join(C.CONF, "results", f"sigma_grid_D2_{tag}.npz")
    if os.path.exists(out):
        sys.exit(f"{out} exists -- refusing")
    tasks = [("D2", prior, cell, s, SG.N_MEAS) for cell in ("C1", "C2") for s in SNRS]
    with mp.Pool(min(jobs, len(tasks))) as pool:
        res = dict(pool.map(point, tasks))
    nu, sig, path = SG.write("D2", res, prior, tag=tag, snrs=SNRS)
    print(f"[grid_dev] prior {prior} tag {tag} (trials {SKIP}..{SKIP + SG.N_MEAS - 1}): sigma_t in [{sig[0]:.4e}, {sig[-1]:.4e}] -> {path}", flush=True)
