"""review_FIGHSX16e4_gpu_smoke.py -- OPTIONAL pre-commit smoke for NEXT_EXPERIMENTS_FIGHSX16e4 (review_FIGHSX16e4.md S-5).

Question: does ald.ald_run take ONE batch of B = 81920 blocks on this GPU (memory, kernel limits, same-seed bit-reproducibility)?
The registered `ald.py estimate --set hisnr4` makes that call for the first time about 3 h into an unattended run; phase C only
exercises B = 2560, and the n = 20480 supplements B = 20480.

SYNTHETIC input only: the SRB TEST pilots at +12 dB (trials 0..2559, already observed) tiled to B rows; 2 noise levels x 3 steps
instead of 200 x 3; nothing is written, no new trial is touched, no NMSE / BLER is computed.  It reads conf/code (common, score)
without writing bytecode.

  cd ~/t2/conf && CUDA_VISIBLE_DEVICES=<free GPU> ~/miniforge3/envs/torch/bin/python -B \\
      results/review_next/prereg_reviews_2026-10-11/review_FIGHSX16e4_gpu_smoke.py [ald.py path] [B = 81920] [cuda|cpu]
"""
import importlib.util
import json
import sys
import time

sys.dont_write_bytecode = True
CONF = "/home/HTJ/t2/conf"
path = sys.argv[1] if len(sys.argv) > 1 else CONF + "/code/ald.py"
B = int(sys.argv[2]) if len(sys.argv) > 2 else 81920
dev = sys.argv[3] if len(sys.argv) > 3 else "cuda"
sys.path.insert(0, CONF + "/code")
spec = importlib.util.spec_from_file_location("ald_smoke", path)
A = importlib.util.module_from_spec(spec)
spec.loader.exec_module(A)
import numpy as np
import torch

if dev == "cuda":
    A._det()
A.L_LEVELS = 2                                               # 2 x M_STEPS = 6 steps: the per-step memory is the full run's
rec = json.load(open(CONF + "/results/ald/tune_PILSRB.json"))
m, smin, smax, _ = A._model(CONF + "/" + rec["ckpt"], dev)
z = np.load(CONF + "/results/ald/pilots_PILSRB_test.npz")
k = int(np.flatnonzero(z["snrs"] == 12.0)[0])
b = np.tile(z["b"][k], (B // z["b"].shape[1] + 1, 1))[:B]
out = []
for rep in range(2):                                         # the same seed twice, as cmd_estimate's determinism check
    gen = torch.Generator(device=dev).manual_seed(A.SEED + 1000)
    t0 = time.time()
    _, kept = A.ald_run(m, b, z["G"][k], float(z["sigma2"][k]), smin, smax, rec["c"], rec["beta"], gen=gen, keep={A.L_LEVELS * A.M_STEPS})
    if dev == "cuda":
        torch.cuda.synchronize()
    out.append((kept[A.L_LEVELS * A.M_STEPS], time.time() - t0))
steps = A.L_LEVELS * A.M_STEPS
per = out[1][1] / steps
print(f"ald_run B = {B} on {dev}: OK, output {out[0][0].shape}, finite {bool(np.isfinite(out[0][0]).all())}, "
      f"same seed twice bit-identical {bool(np.array_equal(out[0][0], out[1][0]))}; {per:.3f} s/step (second call) -> "
      f"hisnr4 estimate ~ {per * 600 * 3 / 60:.1f} min (2 SNRs + the determinism repeat, 600 steps each)"
      + (f"; peak GPU memory {torch.cuda.max_memory_allocated() / 2**30:.1f} GiB allocated, {torch.cuda.max_memory_reserved() / 2**30:.1f} GiB reserved "
         f"of {torch.cuda.get_device_properties(0).total_memory / 2**30:.0f} GiB ({torch.cuda.get_device_name(0)})" if dev == "cuda" else ""))
