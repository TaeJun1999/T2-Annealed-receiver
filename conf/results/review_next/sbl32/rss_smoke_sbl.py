"""rss_smoke_sbl.py -- NEXT_EXPERIMENTS_U28NR32SBL §1.3 'CPU · 메모리' row: ONE development chunk (0 dB, trials 4160..4199,
never the test set) of the main run's arms (SBL-loop with the §1.2 pick + R5-genie) with jobs = 1, under the fits of tag
U28NR32SBLdev = a 2-file byte copy (no links) of the test fits (fullK32 + the recorded kronK4096).  Prints the largest
resident set of the runner tree (getrusage(RUSAGE_CHILDREN).ru_maxrss, GB = 2**30 B), the wall time, and
G = (RSS * 1.05) rounded UP to 0.5 GB (SCALE16e4 rule).  The chunk's BLER is not printed or read here.
    cd ~/t2_wtE3/conf && CUDA_VISIBLE_DEVICES= nice -n 10 taskset -c 191 python results/review_next/sbl32/rss_smoke_sbl.py 4,3,1,1"""
import hashlib, math, os, resource, shutil, subprocess, sys, time

SPARSE = sys.argv[1]                                   # the §1.2 pick as --sparse-arms (rho,n_em,1,1[,1])
SRC = "/home/HTJ/t2_wtS/conf/results/gmm_fits_D2_U28NR32B16e4"
SHA = {"fit_UMi28_Nr32_fullK32_n160000.npz": "d572e0ac63013a96042a148aa1fceaa6662710ddfdbcfb4a4dd051271704e215",
       "fit_UMi28_Nr32_kronK4096_n160000.npz": "2d72a4349e2700e79aec72b48bebed29e59b0f336091b9a6706dbd70d29ef569"}
T = "U28NR32SBLdev"
dev = f"results/gmm_fits_D2_{T}"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
if not os.path.isdir(dev):
    os.makedirs(dev)
    for f in SHA:
        shutil.copyfile(os.path.join(SRC, f), os.path.join(dev, f))
if sorted(os.listdir(dev)) != sorted(SHA) or any(os.path.islink(os.path.join(dev, f)) or sha(os.path.join(dev, f)) != h
                                                 for f, h in SHA.items()):
    sys.exit(f"rss_smoke_sbl: {dev} is not the 2-file byte copy (fullK32 + kronK4096, recorded sha256) -- refusing")
out = f"raw_{T}/D2_C9_UMi28_Nr32_T16_Tp4_eig_snr0_skip4160_n40.npz"
if os.path.exists(out):                       # runner would skip an existing chunk and the RSS would not be a receiver's
    sys.exit(f"rss_smoke_sbl: {out} exists -- refusing (the measurement needs a freshly computed chunk)")
cmd = [sys.executable, "code/runner.py", "run", "--testbed", "D2", "--prior", "UMi28", "--cell", "C9", "--ntrain", "160000",
       "--chunk", "40", "--n", "40", "--skip0", "4160", "--snr", "0", "--arm", "SBL-loop", "R5-genie",
       "--sparse-arms", SPARSE, "--tag", T]
t = time.time()
rc = subprocess.run(cmd).returncode
dt = time.time() - t
rss = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / 2 ** 20          # kB -> GB (2**30 B)
if rc != 0 or not os.path.exists(out):
    sys.exit(f"rss_smoke_sbl: runner rc {rc}, chunk written {os.path.exists(out)} -- no G (measurement invalid)")
print(f"rss_smoke_sbl {SPARSE}: rc {rc}  wall {dt:.0f} s  max RSS {rss:.3f} GB  -> G = {math.ceil(rss * 1.05 / 0.5) * 0.5:.1f}",
      flush=True)
