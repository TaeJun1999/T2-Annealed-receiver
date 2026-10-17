"""rss_smoke.py -- NEXT_EXPERIMENTS_U28NR32GCAP §1.3 memory guard / time: ONE development chunk (0 dB, trials 2560..2599,
never the test set) of the main run's arms (M-ours-bstar + R5-genie) with jobs = 1, under the fits of tag U28NR32GCAPdev
(= copies of the GCAPe fits).  Prints the largest resident set of the runner tree (getrusage(RUSAGE_CHILDREN).ru_maxrss,
GB = 2**30 B) and the wall time, and G = (RSS * 1.05) rounded UP to 0.5 GB (SCALE16e4 rule).
    cd ~/t2/conf && CUDA_VISIBLE_DEVICES= taskset -c 191 python results/review_next/gcap/rss_smoke.py"""
import math, os, resource, subprocess, sys, time

cmd = [sys.executable, "code/runner.py", "run", "--testbed", "D2", "--prior", "UMi28", "--cell", "C9", "--ntrain", "160000",
       "--stagec-ckpt", "/home/HTJ/t2/conf/ckpt/d2sx_UMi28NR32_N160000_a1_best.pt", "--chunk", "40", "--n", "40",
       "--skip0", "2560", "--snr", "0", "--arm", "M-ours-bstar", "R5-genie", "--tag", "U28NR32GCAPdev"]
import hashlib
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
dev, e = "results/gmm_fits_D2_U28NR32GCAPdev", "results/gmm_fits_D2_U28NR32GCAPe"   # dev must be byte copies of the e fits
if sorted(os.listdir(dev)) != sorted(os.listdir(e)) or len(os.listdir(dev)) != 2 or any(
        os.path.islink(os.path.join(d, f)) or sha(os.path.join(dev, f)) != sha(os.path.join(e, f)) for d in (dev, e) for f in os.listdir(dev)):
    sys.exit(f"rss_smoke: {dev} is not a 2-file byte copy of {e} -- refusing")
out = "raw_U28NR32GCAPdev/D2_C9_UMi28_Nr32_T16_Tp4_eig_snr0_skip2560_n40.npz"
if os.path.exists(out):                       # runner would skip an existing chunk and the RSS would not be a receiver's
    sys.exit(f"rss_smoke: {out} exists -- refusing (the measurement needs a freshly computed chunk)")
t = time.time()
rc = subprocess.run(cmd).returncode
dt = time.time() - t
rss = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / 2 ** 20          # kB -> GB (2**30 B)
if rc != 0 or not os.path.exists(out):
    sys.exit(f"rss_smoke: runner rc {rc}, chunk written {os.path.exists(out)} -- no G (measurement invalid)")
print(f"rss_smoke: rc {rc}  wall {dt:.0f} s  max RSS {rss:.3f} GB  -> G = {math.ceil(rss * 1.05 / 0.5) * 0.5:.1f}", flush=True)
