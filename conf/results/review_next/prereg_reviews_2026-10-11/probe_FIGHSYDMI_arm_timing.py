"""In-memory timing probe (nothing written): one chunk (trials 10000..10039, +15 dB) of prior DMI with an arm subset."""
import os, sys, time
CONF = "/home/HTJ/t2/conf"
sys.path.insert(0, os.path.join(CONF, "code"))
import numpy as np
import common as C
import runner

arms = sys.argv[1].split(",")
snr, skip = float(sys.argv[2]), int(sys.argv[3])
ck = os.path.join(CONF, "ckpt", "d2sx_DMI_N160000_a1_best.pt")
runner._init("FHDMIB16e4")
stored = runner.raw_file("D2", "C2", "DMI", C.make_pilots("D2", "DMI", 4, 4, 8)[0], snr, skip, 40)
cap = {}
runner.raw_file = lambda *a: "/nonexistent/__probe_never_written__.npz"
np.savez_compressed = lambda out, **flat: cap.update(flat)
task = ("D2", "C2", "DMI", snr, skip, 40, 160000, C.BETA, C.T_IN, C.N_ITER, arms, None, ck, False, False, None, False, None, None, None, None)
t0 = time.time()
runner.run_task(task)
dt = time.time() - t0
z = np.load(stored) if os.path.exists(stored) else None
same = "n/a" if z is None else all(np.array_equal(z[a + "|blk_err"], cap[a + "|blk_err"]) for a in arms)
print(f"arms {','.join(arms)}  snr {snr:g} skip {skip}: {dt:.0f} s for 40 trials; blk_err == stored chunk: {same}", flush=True)
