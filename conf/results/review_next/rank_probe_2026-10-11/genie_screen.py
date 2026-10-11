"""rank_probe_2026-10-11/genie_screen.py -- dataset screening by the PERFECT-CSI receiver only (R5-genie: same EP detector + BCJR, true H,
16 iterations): BLER of candidate channel sets, cell C2 (8x4), so that the pool whose BLER LEVEL is lowest can be chosen.
User, 2026-10-11 CDT: "모든 선택 기준은 bler가 낮게 나올거 같은 방향으로 해야해".  No prior-dependent arm (V1, GMM, baselines) is
run and no test-trial stream is used: the transmitter / decoder objects come from runner.build_point of an existing prior (the
genie ignores the prior and the pilots), the channels are the candidate's own, scaled to mean ||H||_F^2 = Nr Nt over the candidate
set, and bits / noise use a screening rng [20261011, candidate index, snr + 100].
usage (from conf/): CUDA_VISIBLE_DEVICES= python -B results/review_next/rank_probe_2026-10-11/genie_screen.py <n_trials> <name=H.npy> ...
  H.npy: (n, 8, 4) complex.  Output: one row per candidate, BLER@16 at -3 / +3 / +9 / +15 dB."""
import os
import sys
from multiprocessing import Pool

sys.path.insert(0, "code")
import common as C
import numpy as np
import runner

SNRS, CELL, REF_PRIOR, REF_TAG = tuple(float(x) for x in os.environ.get("SCREEN_SNRS", "-3,3,9,15").split(",")), "C2", "SRT", "SRTB16e4"
N = int(sys.argv[1]); CANDS = [a.split("=", 1) for a in sys.argv[2:]]
POINT = {}


def task(job):
    ci, snr = job
    if snr not in POINT:
        runner._init(REF_TAG)
        P = runner.build_point("D2", CELL, REF_PRIOR, snr, 160000)
        POINT[snr] = (P["code"], P["arms"]["R5-genie"])
    code, arm = POINT[snr]
    H = np.load(CANDS[ci][1], mmap_mode="r")
    rng = np.random.default_rng([20261011, ci, int(snr) + 100])
    idx = rng.choice(len(H), N, replace=len(H) < N)
    Hs = np.asarray(H[np.sort(idx)], dtype=complex)
    scale = np.sqrt(np.mean(np.sum(np.abs(np.asarray(H[:: max(1, len(H) // 20000)])) ** 2, (1, 2))) / (Hs.shape[1] * Hs.shape[2]))
    f = 0
    for k in range(N):
        h = Hs[k] / scale
        u = rng.integers(0, 2, code.K); perm = rng.permutation(code.Ns)
        _, Y = arm.transmit(u, perm, h, rng)
        f += int(np.asarray(arm.run(Y, h, u, perm, C.N_ITER)["blk_err"])[-1])
    return ci, snr, f


if __name__ == "__main__":
    jobs = [(ci, s) for ci in range(len(CANDS)) for s in SNRS]
    with Pool(min(len(jobs), 96)) as pool:
        R = {(ci, s): f for ci, s, f in pool.imap_unordered(task, jobs)}
    print(f"# genie_screen: R5-genie BLER@16, cell {CELL}, n = {N} per point; candidates scaled to mean ||H||^2 = Nr Nt")
    print(f"{'candidate':<34} " + " ".join(f"{s:+5.0f}dB" for s in SNRS) + "   pairs  rank-1  erank")
    for ci, (name, path) in enumerate(CANDS):
        H = np.load(path, mmap_mode="r"); Hq = np.asarray(H[:: max(1, len(H) // 20000)])
        q = np.linalg.svd(Hq, compute_uv=False) ** 2; q /= q.sum(1, keepdims=True)
        er = np.exp(-(q * np.log(np.maximum(q, 1e-300))).sum(1)).mean()
        print(f"{name:<34} " + " ".join(f"{R[(ci, s)] / N:7.3f}" for s in SNRS) + f"  {len(H):6d}  {(q[:, 0] >= 0.95).mean():.3f}  {er:.2f}", flush=True)
