"""Determinism probe for the ALD batch of FIGHSYDMI16e4 (review S-9; nothing written): the same seed twice at B = 327680 must
give bit-identical iterates (ald.py estimate asserts exactly this for the first SNR)."""
import json, sys, time
sys.path.insert(0, "/home/HTJ/t2/conf/code")
import numpy as np, torch
import ald

ald._det()
rec = json.load(open("results/ald/tune_PILDMI.json"))
m, smin, smax, st = ald._model(rec["ckpt"], "cuda")
z = np.load("results/ald/pilots_PILDMI_hisnr.npz")
k = list(z["snrs"]).index(12.0)
stop = int(rec["stop"]["12.0"]); B = 327680
b = np.tile(z["b"][k], (B // 20480, 1))
out = []
for r in range(2):
    gen = torch.Generator(device="cuda").manual_seed(ald.SEED + 1000)
    t0 = time.time()
    _, kept = ald.ald_run(m, b, z["G"][k], float(z["sigma2"][k]), smin, smax, rec["c"], rec["beta"], gen=gen, keep={stop})
    out.append(kept[stop]); print(f"run {r}: {time.time() - t0:.0f} s, peak {torch.cuda.max_memory_allocated() / 2**30:.1f} GiB", flush=True)
print("same seed twice, B", B, "bit-identical:", bool(np.array_equal(out[0], out[1])), flush=True)
