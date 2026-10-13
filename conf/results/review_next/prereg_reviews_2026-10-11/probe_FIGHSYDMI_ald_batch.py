"""Sizing probe (nothing written): time and peak GPU memory of ald.ald_run for one +15 dB batch of B trials (tiled real pilots)."""
import json, sys, time
sys.path.insert(0, "/home/HTJ/t2/conf/code")
import numpy as np, torch
import ald

ald._det()
rec = json.load(open("results/ald/tune_PILDMI.json"))
m, smin, smax, st = ald._model(rec["ckpt"], "cuda")
z = np.load("results/ald/pilots_PILDMI_hisnr.npz")
k = list(z["snrs"]).index(15.0)
stop = int(rec["stop"]["15.0"])
print("levels", ald.L_LEVELS, "steps/level", ald.M_STEPS, "stop step", stop, "b", z["b"][k].shape, flush=True)
for B in [int(x) for x in sys.argv[1:]]:
    b = np.tile(z["b"][k], (B // 20480, 1))
    torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize()
    gen = torch.Generator(device="cuda").manual_seed(1)
    t0 = time.time()
    try:
        _, kept = ald.ald_run(m, b, z["G"][k], float(z["sigma2"][k]), smin, smax, rec["c"], rec["beta"], gen=gen, keep={stop})
        torch.cuda.synchronize()
        print(f"B {B}: {time.time() - t0:.0f} s, peak GPU memory {torch.cuda.max_memory_allocated() / 2**30:.1f} GiB, out {kept[stop].shape}", flush=True)
    except torch.OutOfMemoryError as e:
        print(f"B {B}: OOM after {time.time() - t0:.0f} s ({str(e)[:80]})", flush=True)
    del b; torch.cuda.empty_cache()
