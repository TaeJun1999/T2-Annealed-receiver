"""nuq_summary.py -- NEXT_EXPERIMENTS_E5QAM16 §1.3 (report only): out-of-training-range fraction of V1's query noise, per SNR at
outer iteration 16 (index 15) and pooled over the 7 SNRs, 16-QAM vs QPSK (same development trial NUMBERS, different realisations).
Prediction 4's quantity: pooled (below + above) / finite at iteration 16.
    python results/review_next/qam16/nuq_summary.py <coverage_..._16qam.npz> <coverage_..._qpsk.npz>"""
import sys
import numpy as np
z = {m: np.load(p) for m, p in zip(("16qam", "qpsk"), sys.argv[1:3])}
snrs = sorted({int(float(k.split("|")[0])) for k in z["16qam"].files if k.endswith("|finite")})
for m in ("16qam", "qpsk"):
    out = [(int(z[m][f"{s}|below"][15] + z[m][f"{s}|above"][15]), int(z[m][f"{s}|finite"][15])) for s in snrs]
    o, f = sum(a for a, _ in out), sum(b for _, b in out)
    print(f"{m:<6} iter16 out/finite per SNR " + "  ".join(f"{s:+d}:{a}/{b}" for s, (a, b) in zip(snrs, out))
          + f"   pooled {o}/{f} = {o / f!r}")
    print(f"{m:<6} pooled out fraction per iteration " + " ".join(f"{sum(int(z[m][f'{s}|below'][i] + z[m][f'{s}|above'][i]) for s in snrs) / max(1, sum(int(z[m][f'{s}|finite'][i]) for s in snrs)):.3f}" for i in range(16)))
