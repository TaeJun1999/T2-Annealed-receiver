"""synth_fine.py -- diag_v1 (development only): the synthetic denoiser check of diag_v1_collapse.py `synth` on a FINE sigma grid
around the training floor (sigma / s_lo = 0.52 ... 1.05, which covers the iteration-2 query sigma at +15 / +18 / +21 dB), 100
channels from the generator (seed 20261019, no trial stream).  Prints MSE / nu (mean and median over channels) of the V1 denoiser and
of the GMM b* posterior mean, and the share of channels with V1 MSE / nu > 2.
    cd ~/t2/conf && CUDA_VISIBLE_DEVICES= nice -n 10 taskset -c <cpu> python results/review_next/qam16/diag_v1/synth_fine.py U28|D2"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import diag_v1_collapse as DG

cell = sys.argv[1]
path = os.path.join(DG.OUT, f"synth_fine_{cell}.txt")
if os.path.exists(path):
    sys.exit(f"{path} exists -- refusing")
p = DG.point(cell, "qpsk", 15.0)
v1, gw = p["arms"][DG.V1].prior, p["arms"][DG.GW].prior
s_lo = v1.s_lo
rng = np.random.default_rng(20261019)
hs = [p["gen"].sample(rng).reshape(-1, order="F") for _ in range(100)]
rows = [f"# synth_fine {cell}: 100 channels (seed 20261019), q = h + CN(0, nu I), s_lo {s_lo:.5g}; MSE/nu mean | median; share V1 MSE/nu > 2"]
for f in (0.52, 0.62, 0.72, 0.80, 0.85, 0.90, 0.95, 1.00, 1.05):
    s = f * s_lo; nu = 2 * s * s
    r = []
    for h in hs:
        q = h + np.sqrt(nu / 2) * (rng.standard_normal(h.shape) + 1j * rng.standard_normal(h.shape))
        m, _ = v1.denoise_full(q, nu); mg, _ = gw.denoise(q, nu)
        r.append((np.mean(np.abs(m - h) ** 2) / nu, np.mean(np.abs(mg - h) ** 2) / nu))
    r = np.asarray(r)
    rows.append(f"sigma/s_lo {f:.2f}  V1 {r[:, 0].mean():.3g} | {np.median(r[:, 0]):.3g}  share>2 {np.mean(r[:, 0] > 2):.2f}   "
                f"GMM b* {r[:, 1].mean():.3g} | {np.median(r[:, 1]):.3g}")
open(path, "w").write("\n".join(rows) + "\n")
print("\n".join(rows), flush=True)
