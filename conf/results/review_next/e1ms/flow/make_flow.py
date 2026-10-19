"""S2 (Fable review of D2SITEMS v1): end-to-end flow test of run_e1ms.sh after the runner (accept_eval -> accept_raw -> compare ->
E1MS_DONE).  Builds raw_<tag> = the 192 raw_B16e4k chunks at -3 / 0 / +3 dB with V1 renamed V1-ms (+ R5-genie, the base's run| / meta|
keys, the smoke chunk's extra meta keys, run|git = HEAD); with 'missing', the same minus one chunk (failure path).  Then writes
flow_run.sh = run_e1ms.sh with the preconditions and the runner call replaced by RM=0 (paths: worktree, base absolute).
    cd ~/t2_wtMS/conf && python results/review_next/e1ms/flow/make_flow.py <tag> [missing]"""
import glob, os, re, shutil, subprocess, sys
import numpy as np
tag, missing = sys.argv[1], len(sys.argv) > 2 and sys.argv[2] == "missing"
H = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
sm = np.load(glob.glob("raw_E1MSsm/*.npz")[0])
extra = {k: sm[k] for k in ("meta|budget|M-ours-dscore-C-V1ms", "meta|fit_sec|M-ours-dscore-C-V1ms", "meta|ms_arm", "meta|stagec_ckpt_id")}
out = f"raw_{tag}"; os.makedirs(out, exist_ok=False)
fs = [f for f in sorted(glob.glob("/home/HTJ/t2/conf/raw_B16e4k/D2_C2_S2_*_n40.npz"))
      if float(re.search(r"_snr(-?\d+)_", f).group(1)) in (-3.0, 0.0, 3.0)]
for i, f in enumerate(fs):
    if missing and i == 0:
        continue
    z = np.load(f); d = {k: z[k] for k in z.files if k.startswith(("run|", "meta|", "R5-genie|"))}
    d.update({k.replace("M-ours-dscore-C-V1|", "M-ours-dscore-C-V1ms|"): z[k] for k in z.files if k.startswith("M-ours-dscore-C-V1|")})
    d.update(extra); d["run|git"] = np.array(H)
    np.savez(os.path.join(out, os.path.basename(f)), **d)
F = f"results/gmm_fits_D2_{tag}"
if not os.path.isdir(F):
    os.makedirs(F)
    for g in glob.glob("/home/HTJ/t2/conf/results/gmm_fits_D2_B16e4k/*.npz"):
        shutil.copyfile(os.path.realpath(g), os.path.join(F, os.path.basename(g)))
s = open("code/run_e1ms.sh").read()
s = s.replace("cd /home/HTJ/t2/conf || exit 1", "cd /home/HTJ/t2_wtMS/conf || exit 1")
s = s.replace("L=logs/run_e1ms.log", "L=logs/e1ms_flow.log")
s = s.replace("T=D2SITEMS; BASE=raw_B16e4k", f"T={tag}; BASE=/home/HTJ/t2/conf/raw_B16e4k")
a, b = s.index('[ -n "${E1MS_CPUS:-}" ]'), s.index('RM=$?; log "runner exit $RM"')
s = s[:a] + 'H=$(git rev-parse --short HEAD)\n' + s[b:].replace('RM=$?; log "runner exit $RM"', 'RM=0; log "flow test: preconditions and runner skipped"', 1)
open(f"results/review_next/e1ms/flow/flow_run_{tag}.sh", "w").write(s)
print(f"{len(glob.glob(out + '/*.npz'))} chunks in {out}, run|git {H}; wrote results/review_next/e1ms/flow/flow_run_{tag}.sh")
