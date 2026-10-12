"""prereg_audit_2026-10-11/highsnr_fail_SRB.py [TAG PRIOR] -- POST HOC, REPORT-ONLY diagnostic (user question 2026-10-11 CDT: the proposed curve
has MORE failures at +9 dB than at +6 dB -- is something wrong?).  For every high-SNR point, each trial where V1 fails at iteration
16: the trial's channel (replayed from the trial stream exactly as code/rank_strata.py does; raws only read) -- largest singular
value's energy share, smallest singular value, ||H||^2/(Nr Nt) -- V1's channel-estimate NMSE at iteration 16, at which iteration
its block error last changed, and which other arms fail on the same trial.  No label, no test.
usage (from conf/): CUDA_VISIBLE_DEVICES= python -B results/review_next/prereg_audit_2026-10-11/highsnr_fail_SRB.py [SRBB16e4 SRB [SKIP0]]
SKIP0 (e.g. FHSRBB16e4 SRB 10000: the n = 20480 raw of FIGHSROOM16e4, user question "15dB에서 왜 위로 튀지?"): the raw holds trials
SKIP0.. of the stream; the SNRs and comparison arms are those the raw has, and each failing trial also prints a fingerprint of its
channel (a pool prior draws with replacement, so the same pool channel can fail more than once).  Without SKIP0: unchanged."""
import hashlib
import os
import sys

sys.path.insert(0, "code")
import common as C
import numpy as np
import runner
from analysis import load_raw

TAG, PRIOR = (sys.argv[1], sys.argv[2]) if len(sys.argv) > 2 else ("SRBB16e4", "SRB")
SK = int(sys.argv[3]) if len(sys.argv) > 3 else 0
CELL, V1, OTH = "C2", "M-ours-dscore-C-V1", ("M-ours-bstar", "R5-genie", "R2-ours-G", "M-ours-dscore-C-V4")
runner._init(TAG)
c = C.CELLS[CELL]
data, _, _ = load_raw("D2", root=os.path.join(C.CONF, f"raw_{TAG}"))
print(f"# highsnr_fail: raw_{TAG} (prior {PRIOR}, cell {CELL}); POST HOC, REPORT-ONLY")
for snr in (sorted(k[2] for k in data if k[0] == CELL) if SK else (3.0, 6.0, 9.0, 12.0, 15.0)):
    key = [k for k in data if k[0] == CELL and k[2] == snr][0]
    if SK:
        OTH = tuple(a for a in OTH if a in data[key])
    e = {a: np.asarray(data[key][a]["blk_err"], float) for a in (V1,) + OTH}
    nm = np.asarray(data[key][V1]["nmse"], float)
    n = len(e[V1])
    P = runner.build_point("D2", CELL, PRIOR, snr, 160000)
    code, gen, first = P["code"], P["gen"], P["arms"]["R5-genie"]
    rng = C.trial_rng("D2", PRIOR, c["Nr"], c["T"], c["Tp"], snr)
    sv = np.empty((n, c["Nt"])); ok = True; fp = {}
    for tr in range(-SK, n):                               # trials before SKIP0 are regenerated and dropped, as runner.py does
        H = gen.sample(rng); u = rng.integers(0, 2, code.K); perm = rng.permutation(code.Ns)
        _, Y = first.transmit(u, perm, H, rng)
        if tr < 0:
            continue
        fp[tr] = hashlib.sha1(np.ascontiguousarray(H).tobytes()).hexdigest()[:8]
        sv[tr] = np.linalg.svd(H, compute_uv=False) ** 2
        if tr < 20:
            ok &= np.array_equal(np.asarray(first.run(Y, H, u, perm, C.N_ITER)["blk_err"]), np.asarray(data[key]["R5-genie"]["blk_err"])[tr], equal_nan=True)
    share, pw = sv[:, 0] / sv.sum(1), sv.sum(1) / (c["Nr"] * c["Nt"])
    f = np.where(e[V1][:, -1] > 0)[0]
    print(f"\n{snr:+.0f} dB  n={n}  alignment (genie, first 20 trials) {'OK' if ok else 'MISMATCH'};  failures@16: V1 {len(f)}  " + "  ".join(f"{a.replace('M-ours-', '').replace('dscore-C-', '')} {int(e[a][:, -1].sum())}" for a in OTH)
          + (f";  distinct channels among the {n} trials {len(set(fp.values()))}" if SK else "") + f";  all trials: share median {np.median(share):.3f}, share>=0.95 {np.mean(share >= 0.95):.3f}, smallest sv^2 median {np.median(sv[:, -1]):.2e}, power median {np.median(pw):.2f}")
    print(f"    V1 failures by iteration (1, 2, 4, 8, 16): {[int(e[V1][:, i - 1].sum()) for i in (1, 2, 4, 8, 16)]};  V1 NMSE@16 [dB] median over all trials {10 * np.log10(np.median(nm[:, -1])):.1f}")
    for t in (f if SK else f[:30]):
        last = int(np.max(np.where(np.diff(e[V1][t]) != 0)[0]) + 2) if np.any(np.diff(e[V1][t]) != 0) else 1
        print(f"    trial {t + SK:4d}: share {share[t]:.3f}  2nd/1st sv^2 {sv[t, 1] / sv[t, 0]:.3f}  smallest sv^2 {sv[t, -1]:.2e}  power {pw[t]:.2f}  V1 NMSE@16 {10 * np.log10(nm[t, -1]):6.1f} dB (max over iters {10 * np.log10(np.nanmax(nm[t])):6.1f})"
              f"  err last changed at it {last:2d}  also fail: " + (", ".join(a.replace('M-ours-', '').replace('dscore-C-', '') for a in OTH if e[a][t, -1] > 0) or "none")
              + (f"  channel {fp[t]} (drawn {sum(v == fp[t] for v in fp.values())}x at this SNR; V1 fails on {sum(e[V1][i, -1] > 0 for i, v in fp.items() if v == fp[t])} of them)" if SK else ""))
