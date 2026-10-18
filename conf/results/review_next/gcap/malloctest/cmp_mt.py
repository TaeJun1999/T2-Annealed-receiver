"""cmp_mt.py -- U28NR32GCAP §6.4: the allocator settings change no result (development trials only).
MTa (default allocator) vs MTb (GLIBC_TUNABLES / MALLOC_* settings), trials 4300..4302, 0 dB, every data array;
MTc (allocator settings) vs the GCAP development smoke chunk (default allocator) rows 0..2, every data array.
    cd ~/t2/conf && python results/review_next/gcap/malloctest/cmp_mt.py"""
import glob, numpy as np
f = lambda t: np.load(glob.glob(f"raw_{t}/*.npz")[0])
a, b, c = f("U28NR32MTa"), f("U28NR32MTb"), f("U28NR32MTc")
r = np.load("raw_U28NR32GCAPdev/D2_C9_UMi28_Nr32_T16_Tp4_eig_snr0_skip2560_n40.npz")
ks = [k for k in a.files if "|" in k and not k.startswith(("meta", "run"))]
assert ks == [k for k in b.files if "|" in k and not k.startswith(("meta", "run"))]
print("MTa vs MTb:", len(ks), "arrays compared; differing:", [k for k in ks if not np.array_equal(a[k], b[k], equal_nan=True)])
kc = [k for k in c.files if "|" in k and not k.startswith(("meta", "run"))]
print("MTc vs GCAPdev rows 0..2:", len(kc), "arrays compared; differing:", [k for k in kc if not np.array_equal(c[k], r[k][:3], equal_nan=True)])
