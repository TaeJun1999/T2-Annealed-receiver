"""rss_smoke_e5.py -- NEXT_EXPERIMENTS_E5QAM16 §1.4 memory guard / time for ONE cell: one development chunk (trials 5480..5519,
the grid's 4th SNR, the five arms, 16-QAM) with jobs = 1 under tag <T>dev whose fits folder is a byte copy of the original
folder (= the test folder's content).  Prints the largest resident set of the runner tree (RUSAGE_CHILDREN, GB = 2**30 B), the
wall time, and G = RSS * 1.05 rounded UP to 0.5 GB (SCALE16e4 rule).  The chunk's BLER is not printed (runner prints none for
16-QAM) and is not read here.
    cd ~/t2_wtE5/conf && CUDA_VISIBLE_DEVICES= taskset -c <cpu> python results/review_next/qam16/rss_smoke_e5.py U28|D2 <snr>
"""
import filecmp, glob, math, os, resource, shutil, subprocess, sys, time

CELL, SNR = sys.argv[1], sys.argv[2]
PR, T, SRC, CK = {"U28": ("UMi28", "U28QAM16dev", "/home/HTJ/t2/conf/results/gmm_fits_D2_U28B16e4",
                          "/home/HTJ/t2/conf/ckpt/d2sx_UMi28_N160000_a1_best.pt"),
                  "D2": ("S2", "D2QAM16dev", "/home/HTJ/t2/conf/results/gmm_fits_D2_B16e4k",
                         "/home/HTJ/t2/conf/ckpt/d2sx_N160000_a1.pt")}[CELL]
F = f"results/gmm_fits_D2_{T}"
if not os.path.isdir(F):
    os.makedirs(F)
    for f in glob.glob(f"{SRC}/*.npz"):
        shutil.copyfile(os.path.realpath(f), os.path.join(F, os.path.basename(f)))     # cp -L: real bytes, no links
src = sorted(os.path.basename(f) for f in glob.glob(f"{SRC}/*.npz"))
if sorted(os.listdir(F)) != src or any(os.path.islink(os.path.join(F, f)) or not filecmp.cmp(os.path.join(SRC, f), os.path.join(F, f), shallow=False) for f in src):
    sys.exit(f"rss_smoke_e5: {F} is not a byte copy of {SRC} -- refusing")
if glob.glob(f"raw_{T}/*snr{SNR}_skip5480_n40.npz"):
    sys.exit(f"rss_smoke_e5: the development chunk already exists in raw_{T} -- refusing (the RSS must be a fresh receiver's)")
cmd = [sys.executable, "code/runner.py", "run", "--testbed", "D2", "--prior", PR, "--cell", "C2", "--ntrain", "160000",
       "--stagec-ckpt", CK, "--pilot-arms", "--mod", "16qam", "--chunk", "40", "--n", "40", "--skip0", "5480", "--snr", SNR,
       "--arm", "M-ours-dscore-C-V1", "M-ours-bstar", "R2-ours-G", "R5-genie", "V1-pilot", "--tag", T]
t = time.time()
rc = subprocess.run(cmd).returncode
dt = time.time() - t
rss = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / 2 ** 20
ok = rc == 0 and bool(glob.glob(f"raw_{T}/*snr{SNR}_skip5480_n40.npz"))
if not ok:
    sys.exit(f"rss_smoke_e5: runner rc {rc}, chunk written {ok} -- no G (measurement invalid)")
print(f"rss_smoke_e5 {CELL}: rc {rc}  wall {dt:.0f} s  max RSS {rss:.3f} GB  -> G = {math.ceil(rss * 1.05 / 0.5) * 0.5:.1f}", flush=True)
