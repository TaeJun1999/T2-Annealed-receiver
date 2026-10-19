"""measure_grid_hs.py -- WORK_QUEUE 13 variant (C): the sigma_t grid measured EXACTLY as the frozen grids were (sigma.measure / sigma.write:
M-ours-G queries, cells C1 C2, n = 64, 1-99 percentile, 20 log-equispaced points) but over the SNR set -3 ... +24 dB (the frozen grids used
the cells' -3 ... +15 dB).  Written under a NEW tag (never the frozen grid):  results/sigma_grid_D2_<tag>.{txt,npz}.
    cd ~/t2/conf && CUDA_VISIBLE_DEVICES= nice -n 10 taskset -c <cpus> python results/review_next/lowsig/measure_grid_hs.py <prior> <tag> <jobs>"""
import os, sys
sys.path.insert(0, "code")
import sigma as SG

prior, tag, jobs = sys.argv[1], sys.argv[2], int(sys.argv[3])
out = os.path.join(SG.C.CONF, "results", f"sigma_grid_D2_{tag}.npz")
if os.path.exists(out):
    sys.exit(f"{out} exists -- refusing")
snrs = [-3.0, 0.0, 3.0, 6.0, 9.0, 12.0, 15.0, 18.0, 21.0, 24.0]
res, pr = SG.measure("D2", ["C1", "C2"], prior=prior, n=SG.N_MEAS, jobs=jobs, snrs=snrs)
nu, sig, path = SG.write("D2", res, pr, tag=tag, snrs=snrs)
print(f"[grid_hs] prior {pr} tag {tag}: sigma_t in [{sig[0]:.4e}, {sig[-1]:.4e}] -> {path}", flush=True)
