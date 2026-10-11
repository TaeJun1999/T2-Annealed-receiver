"""conf/code/srb_build.py -- ONE-TIME builder of the Sionna RT ROOM pool (prior 'SRB'); dmimo.py reads the result.

User instructions 2026-10-11 CDT (conf/DECISIONS.md): "기지국은 고정하고 위치를 비꿔서 채널을 수집하는게 좋을 거 같은데",
"Deepmimo, Sionna 모두 rank1이 적게 나오는 채널로 찾아봐", "뭐가 됬던 rank 1 가장 낮은가로 해보자", "모든 선택 기준은 bler가
낮게 나올거 같은 방향으로 해야해".  Selection (conf/results/review_next/rank_probe_2026-10-11/; no prior-dependent arm, no test
trial): the room scene `box` (an empty 10 x 10 x 5 m box, walls AS SHIPPED = material 'box-mat', relative permittivity 1,
conductivity 1e7 S/m, i.e. metal) has the fewest rank-1 links of everything scanned; among its settings the one with the lowest
PERFECT-CSI BLER (genie_screen.py: R5-genie only) that keeps the waterfall on the fixed SNR grid -- guard: Perfect-CSI
BLER(0 dB) >= that of the D2 reference (0.011), so that an estimated-channel arm has three SNR points in the decision range --
is max_depth 1 (LoS + the six first-order wall reflections): Perfect-CSI BLER 0.199 at -3 dB, 0.037 at 0 dB (depth 2 / 3 / 5:
0.006 / 0.000 / 0.000 at 0 dB, below the guard; glass / concrete walls at depth 5: 0.281 / 0.332 at -3 dB).  Same sizes as
every other testbed; channels by the LIBRARY'S OWN generator: Sionna RT 2.1 PathSolver + PlanarArray + Paths.cfr.

Every choice (fixed before any SRB BLER):
  scene       rt.scene.box, 28 GHz
  solver      PathSolver(): max_depth 1, LoS on, specular reflection on, diffuse reflection / refraction / diffraction off,
              samples_per_src 1e8 and max_num_paths_per_src 1e7 (the screened setting; all 7 paths of a link are found),
              synthetic arrays; the BS is the ray source (uplink by reciprocity: H_ul = H_dl^T)
  arrays      PlanarArray 1 x Nr (BS) and 1 x 4 (UE), isotropic, V polarisation, half-wavelength: horizontal ULAs
  BS          ONE fixed BS, placed by rule from the scene's bounding box: x at 20 %, y at 30 % of the footprint, z at 80 % of the
              height (the rule of the scan), orientation [0, 0, 0]
  UEs         TARGET positions uniform over the footprint with a 5 % margin on every side, height 1.5 m, yaw ~ U[-pi, pi)
  channel     Paths.cfr at frequency offset 0 (narrowband at the carrier), per pair divided by sqrt(sum of the path powers
              |a_l|^2 of the reference element pair) -- pathloss removed, multipath interference kept; dmimo.py then applies
              the ensemble normalisation
  split       tiles floor(xy / TILE) with TILE = 1 m (the room is 10 m wide: the 20 m tiles of the city pools would be one tile);
              tiles are shuffled and taken as TEST until they hold >= 15 % of the pairs; of the other pairs a frozen random
              N_VAL_POOL = 20000 are the validation pool, the rest the fit pool (dmimo.py's stream -> pool map)
  rng         default_rng([SEED, TBID["D2"], 12, PID["SRB"], 0]) for positions and yaws, [.., 1] for the split; solver seed =
              chunk index.  The solver's candidate generator is not deterministic: a rebuild need not reproduce the sha.
The receivers are packed as arrays (Scene.targets is overridden for the solve; a stock Scene.targets call packs them one by one):
same positions, orientations and element offsets -- `selfcheck` compares the two on 64 receivers with a deterministic solver.

usage (GPU):  CUDA_VISIBLE_DEVICES=<g> python -I code/srb_build.py build [Nr]      -> ~/data/sionna_rt/srb_Nr<Nr>/{H.npy, split.npy, meta.npz}
              CUDA_VISIBLE_DEVICES=<g> python -I code/srb_build.py selfcheck
H.npy / split.npy are pinned by dmimo.POOL_SHA; meta.npz (position, yaw, LoS, path count, tile key) is descriptive only.
"""
import hashlib
import os
import sys
import time

import numpy as np

SCENE, NT, FC, DEPTH, SAMPLES, MAXPATHS = "box", 4, 28e9, 1, 10 ** 8, 10 ** 7
BS_FRAC, MARGIN, H_UE = (0.2, 0.3, 0.8), 0.05, 1.5
TARGET, CHUNK, TILE, TEST_SHARE, N_VAL_POOL = 345600, 7200, 1.0, 0.15, 20000


def out_dir(Nr):
    return os.path.expanduser(f"~/data/sionna_rt/srb_Nr{Nr}")


def sha16(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()[:16]


def _rng(*tail):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import common as C
    return np.random.default_rng([C.SEED, C.TBID["D2"], 12, C.PID["SRB"], *tail])


def build(Nr, check=False):
    import drjit as dr
    import mitsuba as mi
    import sionna.rt as rt
    from sionna.rt import PathSolver, PlanarArray, Receiver, Transmitter, load_scene
    scene = load_scene(getattr(rt.scene, SCENE))
    scene.frequency = FC
    arr = lambda n: PlanarArray(num_rows=1, num_cols=n, vertical_spacing=0.5, horizontal_spacing=0.5, pattern="iso", polarization="V")
    scene.tx_array, scene.rx_array = arr(Nr), arr(NT)
    bb = scene.mi_scene.bbox()
    lo, hi = np.array(bb.min).ravel().astype(float), np.array(bb.max).ravel().astype(float)
    sz = hi - lo
    bs = lo + np.array(BS_FRAC) * sz
    rng = _rng(0)
    xy = lo[:2] + sz[:2] * rng.uniform(MARGIN, 1 - MARGIN, (TARGET, 2))      # every position and yaw is drawn up front (fixed order)
    yaw = rng.uniform(-np.pi, np.pi, TARGET)
    n_rx = 64 if check else CHUNK
    scene.add(Transmitter(name="bs", position=[float(x) for x in bs], orientation=[0.0, 0.0, 0.0]))
    for i in range(n_rx):                                        # the solver only needs their COUNT (Paths.num_rx); see fast_targets
        scene.add(Receiver(name=f"ue{i}", position=[1.0 + 0.01 * i, 0.0, H_UE], orientation=[0.0, 0.0, 0.0]))
    el = np.asarray(scene.rx_array.positions(scene.wavelength).numpy(), np.float64).reshape(3, -1).T   # (NT, 3) element offsets
    cur = {}

    def fast_targets(synthetic_array, return_velocities):       # == Scene.targets for orientation [yaw, 0, 0] (srt_build.py)
        assert synthetic_array and return_velocities
        p, y = cur["xy"], cur["yaw"]
        cy, sy = np.cos(y)[:, None], np.sin(y)[:, None]
        rel = np.stack([cy * el[None, :, 0] - sy * el[None, :, 1], sy * el[None, :, 0] + cy * el[None, :, 1],
                        np.broadcast_to(el[None, :, 2], (len(p), NT))], -1).reshape(-1, 3).astype(np.float32)
        f = lambda x: mi.Float(np.ascontiguousarray(x, np.float32))
        z = np.zeros(len(p), np.float32)
        return (mi.Point3f(f(p[:, 0]), f(p[:, 1]), f(z + H_UE)), mi.Point3f(f(y), f(z), f(z)),
                mi.Point3f(f(rel[:, 0]), f(rel[:, 1]), f(rel[:, 2])), dr.zeros(mi.Vector3f, len(p)))

    stock_targets = scene.targets
    solver = PathSolver(deterministic=check)                     # selfcheck: deterministic candidates (1e6 samples: its hash table is samples x receivers x depth)

    def solve(p, y, seed, fast=True):
        cur.update(xy=p, yaw=y)
        if fast:
            scene.targets = fast_targets
        else:
            scene.targets = stock_targets
            for i in range(len(p)):
                u = scene.get(f"ue{i}")
                u.position = mi.Point3f(float(p[i, 0]), float(p[i, 1]), H_UE)
                u.orientation = mi.Point3f(float(y[i]), 0.0, 0.0)
        paths = solver(scene, max_depth=DEPTH, max_num_paths_per_src=MAXPATHS, los=True, specular_reflection=True, diffuse_reflection=False,
                       refraction=False, diffraction=False, samples_per_src=10 ** 6 if check else SAMPLES, synthetic_array=True, seed=seed)
        h = paths.cfr(frequencies=mi.Float([0.0]), normalize_delays=False, normalize=False, out_type="numpy")[:, :, 0, :, 0, 0]
        ar, ai = paths.a
        a = (np.asarray(ar.numpy()) + 1j * np.asarray(ai.numpy()))[:, 0, 0, 0, :]            # (UE, paths): reference element pair
        v = np.asarray(paths.valid.numpy()).reshape(len(p), -1)
        it = np.asarray(paths.interactions.numpy())                                          # (depth, UE, 1, paths)
        return h, a, v, it

    mat = {o: scene.objects[o].radio_material for o in scene.objects}
    print(f"# srb_build {SCENE}: bbox {lo.round(3)} .. {hi.round(3)}, BS {bs.round(3)}, objects / materials "
          f"{ {o: (str(m.name), float(np.asarray(m.relative_permittivity).ravel()[0]), float(np.asarray(m.conductivity).ravel()[0])) for o, m in mat.items()} } "
          "(name, relative permittivity, conductivity S/m)", flush=True)
    if check:
        p, y = xy[:64], yaw[:64]
        h, a, v, _ = solve(p, y, 0)
        h2, a2, v2, _ = solve(p, y, 0, fast=False)               # (this also sets the stock receivers)
        cur.update(xy=p, yaw=y)
        for q, (x, z) in zip(("positions", "orientations", "element offsets"), zip(fast_targets(True, True)[:3], stock_targets(True, True)[:3])):
            d = max(float(np.abs(np.asarray(getattr(x, k)) - np.asarray(getattr(z, k))).max()) for k in "xyz")
            print(f"  selfcheck: {q} max |array-packed - stock| = {d:.2e}")
        print(f"  selfcheck: valid equal {np.array_equal(v, v2) if v.shape == v2.shape else (v.shape, v2.shape)}, paths per link "
              f"{v.sum(1).mean():.1f} / {v2.sum(1).mean():.1f}, max |h - h_stock| / max |h_stock| = "
              f"{(np.abs(h - h2).max() / max(np.abs(h2).max(), 1e-30)) if h.shape == h2.shape else -1:.2e}", flush=True)
        return None
    Hs, los, npath, t0 = [], [], [], time.time()
    for k, s in enumerate(range(0, TARGET, CHUNK)):
        h, a, v, it = solve(xy[s:s + CHUNK], yaw[s:s + CHUNK], k)
        pw = (np.abs(a) ** 2 * v).sum(1)
        assert v.any(1).all() and (pw > 0).all(), f"chunk {k}: a link without a path in a closed room"
        H = h.transpose(0, 2, 1) / np.sqrt(pw)[:, None, None]                                # uplink (pairs, Nr, Nt)
        assert H.shape[1:] == (Nr, NT) and np.isfinite(H).all(), (k, H.shape)
        Hs.append(H.astype(np.complex64)); los.append(((it[0, :, 0, :] == 0) & v).any(1)); npath.append(v.sum(1))
        if k % 6 == 0 or s + CHUNK >= TARGET:
            print(f"  chunk {k + 1}/{TARGET // CHUNK}: {s + CHUNK} pairs, LoS {np.concatenate(los).mean():.3f}, mean paths {np.concatenate(npath).mean():.1f}, "
                  f"|H|_F^2 mean {(np.abs(H) ** 2).sum((1, 2)).mean():.2f}, {time.time() - t0:.0f} s", flush=True)
    H = np.concatenate(Hs); n = len(H)
    assert n == TARGET
    rng = _rng(1)
    tile = np.floor(xy / TILE).astype(np.int64)                  # block split: tiles keyed by floor(xy / TILE)
    key = tile[:, 0] * 100003 + tile[:, 1]
    uk, inv = np.unique(key, return_inverse=True)
    order = rng.permutation(len(uk)); cnt = np.bincount(inv)
    tsel = order[: np.searchsorted(np.cumsum(cnt[order]), TEST_SHARE * n) + 1]
    istest = np.isin(inv, tsel)
    idx_test = np.where(istest)[0]; tr = np.where(~istest)[0]
    v = np.zeros(len(tr), bool); v[rng.permutation(len(tr))[:N_VAL_POOL]] = True
    idx_val, idx_fit = tr[v], tr[~v]
    assert not set(key[idx_test]) & set(key[tr]), "a tile is on both sides of the split"
    o = out_dir(Nr); os.makedirs(o, exist_ok=True)
    split = np.zeros(n, np.int8); split[idx_val] = 1; split[idx_test] = 2      # 0 fit / 1 validation / 2 test
    np.save(os.path.join(o, "H.npy"), H)
    np.save(os.path.join(o, "split.npy"), split)                             # .npy is byte-deterministic (an .npz is not)
    np.savez(os.path.join(o, "meta.npz"), pos=xy, yaw=yaw, los=np.concatenate(los), npath=np.concatenate(npath), key=key, bs=bs,
             bbox=np.stack([lo, hi]), scen=np.zeros(n, np.int64), scenes=np.array([SCENE]))   # descriptive only, not pinned
    print(f"# srb_build Nr={Nr} x Nt={NT}: {n} pairs = fit {len(idx_fit)} + val {len(idx_val)} + test {len(idx_test)} "
          f"(test share {len(idx_test) / n:.4f}); tiles {len(uk)} ({len(tsel)} test); {time.time() - t0:.0f} s")
    print(f"POOL_SHA[('SRB', {Nr})] = ({sha16(os.path.join(o, 'H.npy'))!r}, {sha16(os.path.join(o, 'split.npy'))!r})")
    return o


if __name__ == "__main__":
    mode = sys.argv[1]
    assert mode in ("build", "selfcheck"), mode
    build(int(sys.argv[2]) if len(sys.argv) > 2 else 8, check=mode == "selfcheck")
