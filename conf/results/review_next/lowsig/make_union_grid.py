"""make_union_grid.py -- WORK_QUEUE 13 variant (C): the TRAINING grid for the retrained V1 = the frozen grid's range extended DOWNWARD
only: sigma_t from min(lo_wide, lo_frozen) to max(hi_wide, hi_frozen), N_GRID log-equispaced points (sigma.N_GRID; the same rule as
sigma.build_grid).  lo_wide / hi_wide come from measure_grid_hs.py (-3 ... +24 dB); taking the frozen top keeps every sigma the frozen
model was trained on (the wider pooling lowers the 99th percentile).  Writes results/sigma_grid_D2_<out>.{npz,txt}; refuses to overwrite.
    python results/review_next/lowsig/make_union_grid.py <frozen tag or ''> <wide tag> <out tag>"""
import os, sys
sys.path.insert(0, "code")
import numpy as np
import common as C, sigma as SG

frozen, wide, out = sys.argv[1], sys.argv[2], sys.argv[3]
path = os.path.join(C.CONF, "results", f"sigma_grid_D2_{out}")
if os.path.exists(path + ".npz"):
    sys.exit(f"{path}.npz exists -- refusing")
nf, sf = SG.load("D2", frozen); nw, sw = SG.load("D2", wide)
lo, hi = min(nf.min(), nw.min()), max(nf.max(), nw.max())          # nu (per complex entry)
nu = np.exp(np.linspace(np.log(lo), np.log(hi), SG.N_GRID)); sig = np.sqrt(nu / 2)
np.savez(path + ".npz", nu=nu, sigma=sig, lo=lo, hi=hi, samples=np.array([]))
with open(path + ".txt", "w") as f:
    f.write(C.header("D2", extra=[f"content     : WORK_QUEUE 13 variant (C) TRAINING grid = range union of the frozen grid "
                                  f"'{frozen or '(untagged D2)'}' and the wide grid '{wide}' (-3 ... +24 dB), {SG.N_GRID} log-equispaced points",
                                  f"frozen sigma_t [{sf.min():.4e}, {sf.max():.4e}]  wide [{sw.min():.4e}, {sw.max():.4e}]  "
                                  f"-> union [{sig.min():.4e}, {sig.max():.4e}]"]) + "\n\n  k    nu_q          sigma_t\n")
    for i, (a, b) in enumerate(zip(nu, sig)):
        f.write(f"  {i:<4} {a:.6e}  {b:.6e}\n")
print(f"[union] {out}: sigma_t [{sig.min():.4e}, {sig.max():.4e}]", flush=True)
