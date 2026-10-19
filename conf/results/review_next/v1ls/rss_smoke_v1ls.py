"""rss_smoke_v1ls.py -- NEXT_EXPERIMENTS_V1LS §5: memory guard / time for ONE run: one DEVELOPMENT chunk (+18 dB; QPSK trials 6320..6359,
16-QAM 5520..5559 -- neither used before) of the six arms with jobs = 1, fits = byte copy of the run's fits folder.  Prints the
largest resident set of the runner tree (RUSAGE_CHILDREN, GB = 2**30 B), the wall time and G = RSS * 1.05 rounded UP to 0.5 GB.
BLER is not read.   cd ~/t2_wtLS/conf && CUDA_VISIBLE_DEVICES= nice -n 10 taskset -c <cpu> python results/review_next/v1ls/rss_smoke_v1ls.py U28|D2 qpsk|16qam"""
import glob, math, os, resource, shutil, subprocess, sys, time
CELL, MOD = sys.argv[1], sys.argv[2]
PR, SRC, CK, WK = {"U28": ("UMi28", "/home/HTJ/t2/conf/results/gmm_fits_D2_U28B16e4", "/home/HTJ/t2/conf/ckpt/d2sx_UMi28_N160000_a1_best.pt",
                           "/home/HTJ/t2/conf/ckpt/d2sx_UMi28_N160000_a1_sgUMi28HSU_best.pt"),
                   "D2": ("S2", "/home/HTJ/t2/conf/results/gmm_fits_D2_B16e4k", "/home/HTJ/t2/conf/ckpt/d2sx_N160000_a1.pt",
                          "/home/HTJ/t2/conf/ckpt/d2sx_N160000_a1_sgHSU.pt")}[CELL]
SK = {"qpsk": 6320, "16qam": 5520}[MOD]
T = f"{CELL}LSsm{MOD}"
F = f"results/gmm_fits_D2_{T}"
if not os.path.isdir(F):
    os.makedirs(F)
    for f in glob.glob(f"{SRC}/*.npz"):
        shutil.copyfile(os.path.realpath(f), os.path.join(F, os.path.basename(f)))
if glob.glob(f"raw_{T}/*"):
    sys.exit(f"raw_{T} not empty -- refusing (the RSS must be a fresh receiver's)")
cmd = [sys.executable, "code/runner.py", "run", "--testbed", "D2", "--prior", PR, "--cell", "C2", "--ntrain", "160000", "--stagec-ckpt", CK,
       "--chunk", "40", "--n", "40", "--skip0", str(SK), "--snr", "18", "--arm", "M-ours-dscore-C-V1", "M-ours-bstar", "R5-genie",
       "M-ours-dscore-C-V1-clamp", "M-ours-dscore-C-V1-gmmfb", "M-ours-dscore-C-V1-wide", "--lowsig-arms", "--wide-ckpt", WK, "--tag", T] \
      + (["--mod", "16qam"] if MOD == "16qam" else [])
t = time.time(); rc = subprocess.run(cmd).returncode; dt = time.time() - t
rss = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / 2 ** 20
ok = rc == 0 and len(glob.glob(f"raw_{T}/*.npz")) == 1
if not ok:
    sys.exit(f"rss_smoke_v1ls: runner rc {rc}, chunk written {ok} -- no G (measurement invalid)")
print(f"rss_smoke_v1ls {CELL} {MOD}: rc {rc}  wall {dt:.0f} s  max RSS {rss:.3f} GB  -> G = {math.ceil(rss * 1.05 / 0.5) * 0.5:.1f}", flush=True)
