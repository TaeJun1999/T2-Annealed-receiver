"""probe_gcap.py (U28NR32GCAP step 1 + step 3 timing probe; development only, no BLER, no test trials).
(a) regenerate the frozen UMi28 Nr32 train (stream 7, 160000) / val (stream 8, 5000) sets exactly as runner._sets;
(b) re-evaluate the selected K4096 fit's state on them: train ll must equal ll[it_best] = 188.2857805090495 and
    val ll must equal ll_val = 152.23176788511105 (recorded) up to round-off;
(c) time K = 8192 kron batched EM for n_iter = 3 (2 M-steps) and record peak GPU memory.
Run: CUDA_VISIBLE_DEVICES=k taskset -c c,c+96 python probe_gcap.py <src_fit.npz>"""
import os, sys, time
sys.path.insert(0, os.path.expanduser("~/t2/conf/code"))
import numpy as np, torch
import common as C
from runner import _sets
from gmm_em_gpu import fit_gmm_em_gpu, _loglik_t

src = sys.argv[1]
t0 = time.time()
gen, (X, Xv, Xt) = _sets("UMi28", 32, 4, 160000)
print(f"data: X {X.shape} Xv {Xv.shape} Xt {Xt.shape}  gen {time.time() - t0:.0f} s", flush=True)
d = np.load(src)
dev = torch.device("cuda")
pi, covs = d["pi"], d["covs"]
logpi = torch.as_tensor(np.log(pi), device=dev); cv = torch.as_tensor(covs, device=dev)
for name, Y, ref in (("train", X, float(d["ll"][int(d["it_best"])])), ("val", Xv, float(d["ll_val"]))):
    Yt = torch.as_tensor(Y, device=dev)
    v = float(torch.logsumexp(_loglik_t(Yt, logpi, cv, 128), 1).mean())
    print(f"state-0 {name}: recomputed {v!r}  recorded {ref!r}  rel diff {abs(v - ref) / abs(ref):.3e}", flush=True)
del cv, logpi, Yt; torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats()
rng = np.random.default_rng([C.SEED, C.TBID["D2"], 9, C.PID["UMi28"], 32, 1, 8192, 0, 99])   # probe-only stream (r=99)
t1 = time.time()
f = fit_gmm_em_gpu(X, 8192, rng, n_iter=3, kappa=0.0, struct="kron", dims=(32, 4), Xval=Xv, batched=True)
dt = time.time() - t1
print(f"K8192 probe: n_iter {f['n_iter']} ll {np.round(f['ll'], 3).tolist()} reseeds {f['n_reseed']}  "
      f"{dt:.0f} s total, {dt / 3:.0f} s/iter (incl. init)  peak GPU mem {torch.cuda.max_memory_allocated() / 2**30:.1f} GiB",
      flush=True)
