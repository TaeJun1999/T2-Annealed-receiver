"""prereg_audit_2026-10-11/los_strata.py -- POST HOC, REPORT-ONLY (no label, no test, no CI; not registered): BLER@16 of Perfect
CSI, V1 and b* on raw_SRTB16e4 split by the LoS flag of the trial's pool pair (meta.npz `los`, descriptive metadata of
srt_build.py) crossed with the rank-1 share (largest singular value's energy share >= 0.95, the rank_strata.py definition).
Made after the results, on the user's question (2026-10-11 CDT) "Bler가 높은 원인이 los야?".  Trials are replayed exactly as
code/rank_strata.py does (raws only read); the pool index of each trial is recorded by wrapping the generator's draw.
Alignment check: R5-genie on the first 40 replayed trials must equal the raw bit for bit.
usage (from conf/): CUDA_VISIBLE_DEVICES= python -B results/review_next/prereg_audit_2026-10-11/los_strata.py
"""
import os
import sys

sys.path.insert(0, "code")
import common as C
import dmimo
import numpy as np
import runner
from analysis import load_raw
from rank_strata import ARMS, N_CHECK, decision_snrs, fails

TAG, PRIOR, CELL, NTRAIN = "SRTB16e4", "SRT", "C2", 160000
runner._init(TAG)
c = C.CELLS[CELL]
meta = np.load(os.path.join(dmimo.pool_dir(PRIOR, c["Nr"]), "meta.npz"))
data, _, _ = load_raw("D2", root=os.path.join(C.CONF, f"raw_{TAG}"))
L = [C.header("D2", extra=[f"content     : los_strata.py -- BLER@16 of raw_{TAG} (prior {PRIOR}, cell {CELL}) by the LoS flag of the trial's "
                           "pool pair x rank-1 share (>= 0.95), POST HOC, REPORT-ONLY"]), ""]
ok = True
for snr in sorted({-3.0, *decision_snrs(TAG)}):
    P = runner.build_point("D2", CELL, PRIOR, snr, NTRAIN)
    code, gen, first = P["code"], P["gen"], P["arms"]["R5-genie"]
    b, v, g = (fails(data, CELL, snr, arm) for arm in ARMS)
    ref = np.asarray(data[[k for k in data if k[0] == CELL and k[2] == snr][0]]["R5-genie"]["blk_err"])
    rng = C.trial_rng("D2", PRIOR, c["Nr"], c["T"], c["Tp"], snr)
    rec = []

    def draw(rng, n, G=gen):                                   # DMGen._draw with the drawn pool index recorded
        w = dmimo._which(rng, G.kind, G.Nr)
        assert w == "test" and n == 1, (w, n)
        i = G.idx[w][rng.integers(0, len(G.idx[w]), n)]
        rec.append(int(i[0]))
        return np.asarray(G.H[i], dtype=complex) / G.s
    gen._draw = draw
    share, same = np.empty(len(g)), True
    for tr in range(len(g)):
        H = gen.sample(rng)
        u = rng.integers(0, 2, code.K)
        perm = rng.permutation(code.Ns)
        _, Y = first.transmit(u, perm, H, rng)
        s = np.linalg.svd(H, compute_uv=False) ** 2
        share[tr] = s[0] / s.sum()
        if tr < N_CHECK:
            same &= np.array_equal(np.asarray(first.run(Y, H, u, perm, C.N_ITER)["blk_err"]), ref[tr], equal_nan=True)
    ok &= same
    i = np.array(rec)
    los, npath, r1 = meta["los"][i], meta["npath"][i], share >= 0.95
    row = lambda name, m: (f"    {name:<26} n={m.sum():5d} ({m.mean():.3f})  BLER genie {g[m].mean():.3f}  V1 {v[m].mean():.3f}  b* {b[m].mean():.3f}   "
                           f"failures {int(g[m].sum())} / {int(v[m].sum())} / {int(b[m].sum())}" if m.any() else f"    {name:<26} (empty)")
    L += [f"{snr:+.0f} dB  n={len(g)}  alignment (R5-genie, first {N_CHECK} replayed trials vs raw): {'OK' if same else 'MISMATCH'};  LoS share "
          f"{los.mean():.3f};  rank-1 share (>= 0.95): all {r1.mean():.3f}, among LoS {r1[los].mean():.3f}, among NLoS {r1[~los].mean():.3f};  "
          f"mean path count LoS {npath[los].mean():.2f} / NLoS {npath[~los].mean():.2f}",
          row("LoS", los), row("NLoS", ~los), row("LoS  & rank-1 (>= 0.95)", los & r1), row("LoS  & not rank-1", los & ~r1),
          row("NLoS & rank-1 (>= 0.95)", ~los & r1), row("NLoS & not rank-1", ~los & ~r1),
          row("NLoS, 1 path", ~los & (npath == 1)), row("NLoS, >= 2 paths", ~los & (npath >= 2)),
          row("LoS, 1 path (LoS only)", los & (npath == 1)), row("LoS, >= 2 paths", los & (npath >= 2))]
L += ["", f"alignment {'OK at every SNR' if ok else 'MISMATCH -- do not use'}", "post hoc, report-only: no label, no test, no CI; interpretation is the user's."]
open(os.path.join(C.CONF, "results", "review_next", f"{TAG}_los_strata.txt"), "w").write("\n".join(L) + "\n")
print("\n".join(L))
