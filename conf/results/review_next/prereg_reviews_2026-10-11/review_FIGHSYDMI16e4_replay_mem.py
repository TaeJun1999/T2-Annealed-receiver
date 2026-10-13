"""review_FIGHSYDMI16e4: memory / time of eval_accept.py's --ref-raw 'rows' dict (lines 108-113, copied verbatim) on a chunk-400
reference (raw_ZQDRY: 2 files x 400 trials, the dry-run scratch raw) and on a chunk-40 reference (raw_FHDMIB16e4 +15 dB, 512 files).
Read-only."""
import glob, os, resource, sys, time
sys.path.insert(0, "/home/HTJ/t2/conf/code")
import numpy as np
REF_KEYS = ("blk_err", "ber", "tauL_gmean", "alphaD")
rk = [f"R5-genie|{q}" for q in REF_KEYS]
iters = 16
cut = lambda v, i: v[i, :iters] if v.ndim == 2 else v[i]
rss = lambda: int(open("/proc/self/statm").read().split()[1]) * 4096
def build(files, n, reps=1):
    rows = {}; r0 = rss(); t0 = time.time(); nt = 0
    for rep in range(reps):
        for j, f in enumerate(files):
            with np.load(f) as z:
                for i in range(n):
                    rows[(rep, j, i)] = {k: cut(z[k], i) for k in rk}; nt += 1
    dt = time.time() - t0; dr = rss() - r0
    x = rows[(0, 0, 0)][rk[0]]
    print(f"  {len(files)} files x {n} trials x reps {reps}: {nt} trials, {dt:.1f} s ({dt / nt * 1e6:.0f} us/trial), RSS +{dr / 2**20:.0f} MiB "
          f"({dr / nt / 1024:.1f} KiB/trial); row value shape {x.shape}, base shape {x.base.shape if x.base is not None else None}, base nbytes {x.base.nbytes if x.base is not None else 0}")
    return dt / nt, dr / nt
print("chunk-400 reference (raw_ZQDRY, the code path of FZALDDMI --ref-raw raw_FZDMIB16e4):")
f400 = sorted(glob.glob("/home/HTJ/t2/conf/raw_ZQDRY/D2_*_n400.npz"))
with np.load(f400[0]) as z: print("  keys shapes:", {k: z[k].shape for k in rk}, "dtype", z[rk[0]].dtype)
t4, m4 = build(f400, 400, reps=25)       # 20000 trials
print(f"  => extrapolated to n = 3,072,000 reference trials (7680 files): {t4 * 3072000 / 60:.0f} min, {m4 * 3072000 / 2**30:.0f} GiB")
print("chunk-40 reference (raw_FHDMIB16e4 +15 dB, the code path of FYALDDMI --ref-raw raw_FYDMIB16e4):")
f40 = sorted(glob.glob("/home/HTJ/t2/conf/raw_FHDMIB16e4/D2_*_snr15_*_n40.npz"))
t1, m1 = build(f40, 40)
print(f"  => extrapolated to n = 327,680 reference trials (8192 files): {t1 * 327680 / 60:.1f} min, {m1 * 327680 / 2**30:.1f} GiB")
