"""conf/code/dmi_build.py -- ONE-TIME builder of the DeepMIMO INDOOR pool (prior 'DMI'); dmimo.py reads the result.

User instructions 2026-10-11 CDT (conf/DECISIONS.md): "기지국은 고정하고 위치를 비꿔서 채널을 수집하는게 좋을 거 같은데",
"Deepmimo, Sionna 모두 rank1이 적게 나오는 채널로 찾아봐", "뭐가 됬던 rank 1 가장 낮은가로 해보자", "기지국하나에 연속적으로
위치를 바꿔서 보는거 맞지?".  The configuration is the (scenario, BS) with the lowest share of rank-1 links (largest singular
value's energy share >= 0.95) in the channel-statistics scan conf/results/review_next/rank_probe_2026-10-11/dm_scan.txt (no
receiver, no BLER): scenario i1_2p4 (indoor, 2.4 GHz, Wireless InSite, 2 reflections), dataset 120 = the TX at
(-20.89, 12.60, 5.00) m with the 7 m x 1 m user grid (701 x 101 positions, 1 cm spacing, z = 1 m): rank-1 share 0.023, tied at
three decimals with datasets 68 and 119; the tie goes to the higher mean effective rank (1.64 / 1.63 / 1.61).

ONE fixed BS.  Its grid has 70801 positions, fewer than the training set (160000), so every grid position is used with NYAW = 5
independent UE yaws: 354005 (position, yaw) pairs (the scale of the DeepMIMO city pool, 342597).  Channels by the LIBRARY'S OWN
generator, exactly the recipe of dmimo_build.py: dm.load(max_paths=25), compute_channels(ChannelParameters): freq_domain,
subcarrier 0 (narrowband at the carrier), num_paths 25, isotropic elements, half-wavelength ULAs, BS ULA Nr x 1 with its yaw
toward the centroid of its users, UE ULA 4 x 1 with yaw ~ U[-180, 180) deg; per pair divided by sqrt(sum of the path powers).
Block split on the USER POSITION (all yaws of a position are on the same side): tiles floor(xy / TILE), TILE = 0.5 m (4
wavelengths; the grid is 7 m x 1 m, so the 20 m tiles of the city pools would be one tile); tiles are shuffled and taken as TEST
until they hold >= 15 % of the pairs; of the other pairs a frozen random N_VAL_POOL = 20000 are the validation pool, the rest
the fit pool.  rng = default_rng([SEED, TBID["D2"], 12, PID["DMI"]]).

usage (CPU; cwd = ~/data/deepmimo, where deepmimo_scenarios/ lives):  python -I <conf>/code/dmi_build.py [Nr]
  -> ~/data/deepmimo/dmi_Nr<Nr>/{H.npy, split.npy, meta.npz};  H.npy / split.npy are pinned by dmimo.POOL_SHA.
"""
import hashlib
import os
import sys
import time

import numpy as np

SITE = os.path.expanduser("~/data/deepmimo/site")
SCEN, DS, TX_POS, N_GRID, NYAW = "i1_2p4", 120, (-20.89, 12.60, 5.00), 70801, 5
MAX_PATHS, TILE, TEST_SHARE, N_VAL_POOL, NT = 25, 0.5, 0.15, 20000, 4


def out_dir(Nr):
    return os.path.expanduser(f"~/data/deepmimo/dmi_Nr{Nr}")


def sha16(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()[:16]


def build(Nr):
    sys.path.insert(0, SITE)
    import deepmimo as dm
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import common as C
    rng = np.random.default_rng([C.SEED, C.TBID["D2"], 12, C.PID["DMI"]])
    d = list(dm.load(SCEN, max_paths=MAX_PATHS))[DS]
    tx = np.asarray(d.tx_pos).reshape(-1, 3)[0]
    rx = np.asarray(d.rx_pos)
    n_ue = len(rx)
    assert np.allclose(tx, TX_POS, atol=0.01) and n_ue == N_GRID, (tx, n_ue)        # the dataset the scan ranked
    ok = np.asarray(d.num_paths) > 0
    assert ok.all(), "a grid position without a path"
    cen = rx.mean(0) - tx
    by = float(np.degrees(np.arctan2(cen[1], cen[0])))
    pw = np.nansum(np.asarray(d.power_linear), 1)
    Hs, yaw = [], []
    for j in range(NYAW):
        uy = rng.uniform(-180.0, 180.0, n_ue)                              # one draw per grid position and yaw index (fixed order)
        p = dm.ChannelParameters()
        p.bs_antenna.shape = np.array([Nr, 1]); p.bs_antenna.rotation = np.array([0.0, 0.0, by])
        p.ue_antenna.shape = np.array([NT, 1])
        p.ue_antenna.rotation = np.column_stack([np.zeros(n_ue), np.zeros(n_ue), uy])
        p.num_paths = MAX_PATHS
        p.freq_domain = True
        p.ofdm.selected_subcarriers = np.array([0])
        H = np.asarray(d.compute_channels(p))[:, :, :, 0]                  # (pairs, UE Nt, BS Nr)
        H = H.transpose(0, 2, 1) / np.sqrt(pw)[:, None, None]              # uplink (pairs, Nr, Nt), sum of path powers = 1
        assert H.shape[1:] == (Nr, NT) and np.isfinite(H).all(), (j, H.shape)
        Hs.append(H.astype(np.complex64)); yaw.append(uy)
        print(f"  {SCEN} dataset {DS} yaw draw {j}: {n_ue} pairs, BS yaw {by:+.1f} deg", flush=True)
    H = np.concatenate(Hs); yaw = np.concatenate(yaw); n = len(H)
    pos = np.tile(rx, (NYAW, 1)); posi = np.tile(np.arange(n_ue), NYAW)
    los = np.tile(np.asarray(d.los), NYAW); npath = np.tile(np.asarray(d.num_paths), NYAW)
    tile = np.floor(pos[:, :2] / TILE).astype(np.int64)                    # block split on the user position only
    key = tile[:, 0] * 100003 + tile[:, 1]
    uk, inv = np.unique(key, return_inverse=True)
    order = rng.permutation(len(uk)); cnt = np.bincount(inv)
    tsel = order[: np.searchsorted(np.cumsum(cnt[order]), TEST_SHARE * n) + 1]
    istest = np.isin(inv, tsel)
    idx_test = np.where(istest)[0]; tr = np.where(~istest)[0]
    v = np.zeros(len(tr), bool); v[rng.permutation(len(tr))[:N_VAL_POOL]] = True
    idx_val, idx_fit = tr[v], tr[~v]
    assert not set(key[idx_test]) & set(key[tr]), "a tile is on both sides of the split"
    assert not set(posi[idx_test]) & set(posi[tr]), "a grid position is on both sides of the split"
    o = out_dir(Nr); os.makedirs(o, exist_ok=True)
    split = np.zeros(n, np.int8); split[idx_val] = 1; split[idx_test] = 2      # 0 fit / 1 validation / 2 test
    np.save(os.path.join(o, "H.npy"), H)
    np.save(os.path.join(o, "split.npy"), split)                             # .npy is byte-deterministic (an .npz is not)
    np.savez(os.path.join(o, "meta.npz"), scen=np.zeros(n, np.int64), bs=np.zeros(n, np.int64), pos=pos, posi=posi, los=los, npath=npath, yaw=yaw,
             bsyaw=np.full(n, by), key=key, tx=tx, scenarios=np.array([SCEN]))    # descriptive only, not pinned
    return o, n, len(idx_fit), len(idx_val), len(idx_test), len(uk), len(tsel)


if __name__ == "__main__":
    Nr = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    t0 = time.time()
    o, n, nf, nv, nt, nk, nts = build(Nr)
    print(f"# dmi_build Nr={Nr} x Nt={NT}: {n} pairs = fit {nf} + val {nv} + test {nt} (test share {nt / n:.4f}); tiles {nk} ({nts} test); {time.time() - t0:.0f} s")
    print(f"POOL_SHA[('DMI', {Nr})] = ({sha16(os.path.join(o, 'H.npy'))!r}, {sha16(os.path.join(o, 'split.npy'))!r})")
