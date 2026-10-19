"""rss_smoke_e1ms.py -- NEXT_EXPERIMENTS_D2SITEMS §5 (E1+): memory guard / time for the run: ONE development chunk (-3 dB, the slowest
point; trials 2560..2599) of the run's two arms (M-ours-dscore-C-V1ms, R5-genie; --ms-arm) with jobs = 1, fits = byte copy of the run's
fits folder.  Prints the largest resident set of the runner tree (RUSAGE_CHILDREN, GB = 2**30 B), the wall time and
G = RSS * 1.05 rounded UP to 0.5 GB.  BLER is not read.   cd ~/t2_wtMS/conf && CUDA_VISIBLE_DEVICES= nice -n 10 taskset -c <cpu> python
results/review_next/e1ms/rss_smoke_e1ms.py  (rss_smoke_v1ls.py's method)"""
import glob, math, os, resource, shutil, subprocess, sys, time
SRC, CK, T = "/home/HTJ/t2/conf/results/gmm_fits_D2_B16e4k", "/home/HTJ/t2/conf/ckpt/d2sx_N160000_a1.pt", "E1MSsm"
F = f"results/gmm_fits_D2_{T}"
if not os.path.isdir(F):
    os.makedirs(F)
    for f in glob.glob(f"{SRC}/*.npz"):
        shutil.copyfile(os.path.realpath(f), os.path.join(F, os.path.basename(f)))
if glob.glob(f"raw_{T}/*"):
    sys.exit(f"raw_{T} not empty -- refusing (the RSS must be a fresh receiver's)")
cmd = [sys.executable, "code/runner.py", "run", "--testbed", "D2", "--prior", "S2", "--cell", "C2", "--ntrain", "160000", "--stagec-ckpt", CK,
       "--chunk", "40", "--n", "40", "--skip0", "2560", "--snr", "-3", "--arm", "M-ours-dscore-C-V1ms", "R5-genie", "--ms-arm", "--tag", T]
t = time.time(); rc = subprocess.run(cmd).returncode; dt = time.time() - t
rss = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / 2 ** 20
ok = rc == 0 and len(glob.glob(f"raw_{T}/*.npz")) == 1
if not ok:
    sys.exit(f"rss_smoke_e1ms: runner rc {rc}, chunk written {ok} -- no G (measurement invalid)")
print(f"rss_smoke_e1ms: rc {rc}  wall {dt:.0f} s  max RSS {rss:.3f} GB  -> G = {math.ceil(rss * 1.05 / 0.5) * 0.5:.1f}", flush=True)
