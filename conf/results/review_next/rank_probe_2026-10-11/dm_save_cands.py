"""rank_probe_2026-10-11/dm_save_cands.py -- save candidate channel sets (the pool recipe of dmimo_build.py, one random UE yaw per
position, up to N random positions per dataset) for genie_screen.py.
usage (cwd = ~/data/deepmimo): python -I dm_save_cands.py <out_dir> <N> <scenario>[:i,j,...] ..."""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.expanduser("~/data/deepmimo/site"))
import deepmimo as dm

out, N = sys.argv[1], int(sys.argv[2])
rng = np.random.default_rng(20261011)
for spec in sys.argv[3:]:
    s, _, sel = spec.partition(":")
    L = list(dm.load(s, max_paths=25)) if type(dm.load(s, max_paths=25)).__name__ == "MacroDataset" else [dm.load(s, max_paths=25)]
    for bi in ([int(x) for x in sel.split(",")] if sel else range(len(L))):
        d = L[bi]; n_ue = len(d.rx_pos); ok = np.asarray(d.num_paths) > 0
        cen = np.asarray(d.rx_pos)[ok].mean(0) - np.asarray(d.tx_pos).reshape(-1, 3)[0]
        p = dm.ChannelParameters()
        p.bs_antenna.shape = np.array([8, 1]); p.bs_antenna.rotation = np.array([0.0, 0.0, float(np.degrees(np.arctan2(cen[1], cen[0])))])
        p.ue_antenna.shape = np.array([4, 1])
        p.ue_antenna.rotation = np.column_stack([np.zeros(n_ue), np.zeros(n_ue), rng.uniform(-180.0, 180.0, n_ue)])
        p.num_paths = 25; p.freq_domain = True; p.ofdm.selected_subcarriers = np.array([0])
        H = np.asarray(d.compute_channels(p))[ok, :, :, 0].transpose(0, 2, 1)
        H = H / np.sqrt(np.nansum(np.asarray(d.power_linear)[ok], 1))[:, None, None]
        H = H[np.isfinite(H).all((1, 2))]
        H = H[np.sort(rng.choice(len(H), min(N, len(H)), replace=False))].astype(np.complex64)
        np.save(os.path.join(out, f"{s}_bs{bi}.npy"), H)
        print(f"SAVED {s}_bs{bi} {len(H)} of {int(ok.sum())}", flush=True)
