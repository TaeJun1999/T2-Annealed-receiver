"""One malloc variant of the GCAP receiver config on development trials 4300..4302 (0 dB), 1 worker; prints wall and max RSS."""
import os, resource, subprocess, sys, time
tag, cpu = sys.argv[1], sys.argv[2]
cmd = ["taskset", "-c", cpu, "nice", "-n", "10", sys.executable, "code/runner.py", "run", "--testbed", "D2", "--prior", "UMi28",
       "--cell", "C9", "--ntrain", "160000", "--stagec-ckpt", "/home/HTJ/t2/conf/ckpt/d2sx_UMi28NR32_N160000_a1_best.pt",
       "--chunk", "3", "--n", "3", "--skip0", "4300", "--snr", "0", "--arm", "M-ours-bstar", "R5-genie", "--tag", tag]
t = time.time(); rc = subprocess.run(cmd, cwd="/home/HTJ/t2/conf").returncode; dt = time.time() - t
ru = resource.getrusage(resource.RUSAGE_CHILDREN)
print(f"{tag}: rc {rc} wall {dt:.0f} s  maxRSS {ru.ru_maxrss / 2**20:.2f} GB  utime {ru.ru_utime:.0f} s  stime {ru.ru_stime:.0f} s  "
      f"minflt {ru.ru_minflt}  majflt {ru.ru_majflt}  env GLIBC_TUNABLES={os.environ.get('GLIBC_TUNABLES', '')}", flush=True)
