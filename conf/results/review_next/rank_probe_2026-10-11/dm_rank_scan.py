"""rank_probe_2026-10-11/dm_rank_scan.py -- channel statistics only (no receiver, no BLER): DeepMIMO scenarios, per BS, the share of rank-1 links at 8x4 with the pool's channel
recipe (dmimo_build.py: max_paths 25, isotropic half-wavelength ULAs, BS yaw toward the grid centre, random UE yaw, narrowband).
usage (cwd = ~/data/deepmimo): python -I dm_freq_probe.py <scenario> [<scenario> ...]"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.expanduser("~/data/deepmimo/site"))
import deepmimo as dm

NR, NT, MAXP = 8, 4, 25
rng = np.random.default_rng(20260926)
print(f"{'scenario':<26} {'BS':>2} {'pairs':>7} {'LoS':>6} {'paths':>6} {'rank-1':>7} {'<0.80':>6} {'erank':>6} {'rank-1|LoS':>10} {'rank-1|NLoS':>11}")
for s in sys.argv[1:]:
    if not os.path.isdir(os.path.join("deepmimo_scenarios", s)):
        try:
            dm.download(s)
        except Exception as e:
            print(f"{s:<26} DOWNLOAD FAILED: {type(e).__name__}: {str(e)[:120]}"); continue
    if not os.path.isdir(os.path.join("deepmimo_scenarios", s)):
        print(f"{s:<26} not available after download"); continue
    ds = dm.load(s, max_paths=MAXP)
    for bi, d in enumerate(ds if type(ds).__name__ == "MacroDataset" else [ds]):
        n_ue = len(d.rx_pos); ok = np.asarray(d.num_paths) > 0
        cen = np.asarray(d.rx_pos)[ok].mean(0) - np.asarray(d.tx_pos).reshape(-1, 3)[0]
        p = dm.ChannelParameters()
        p.bs_antenna.shape = np.array([NR, 1]); p.bs_antenna.rotation = np.array([0.0, 0.0, float(np.degrees(np.arctan2(cen[1], cen[0])))])
        p.ue_antenna.shape = np.array([NT, 1])
        p.ue_antenna.rotation = np.column_stack([np.zeros(n_ue), np.zeros(n_ue), rng.uniform(-180.0, 180.0, n_ue)])
        p.num_paths = MAXP; p.freq_domain = True; p.ofdm.selected_subcarriers = np.array([0])
        H = np.asarray(d.compute_channels(p))[ok, :, :, 0].transpose(0, 2, 1)
        m = np.isfinite(H).all((1, 2)) & (np.abs(H).sum((1, 2)) > 0)   # drop pairs without a finite, non-zero channel
        H, los = H[m], (np.asarray(d.los)[ok] == 1)[m]
        q = np.linalg.svd(H, compute_uv=False) ** 2; q = q / q.sum(1, keepdims=True); sh = q[:, 0]
        er = np.exp(-(q * np.log(np.maximum(q, 1e-300))).sum(1))
        f = lambda m: f"{(sh[m] >= 0.95).mean():.3f}" if m.any() else "  -  "
        print(f"{s:<26} {bi:2d} {len(sh):7d} {los.mean():6.3f} {np.asarray(d.num_paths)[ok][m].mean():6.1f} {(sh >= 0.95).mean():7.3f} {(sh < 0.80).mean():6.3f} "
              f"{er.mean():6.2f} {f(los):>10} {f(~los):>11}", flush=True)
