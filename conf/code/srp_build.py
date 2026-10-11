"""conf/code/srp_build.py -- ONE-TIME builder of the Sionna RT ROOM PATH pool (prior 'SRP'); dmimo.py reads the result.

User instruction 2026-10-11 CDT (conf/DECISIONS.md): the channels should be collected CONTINUOUSLY IN TIME by a UE that moves, with
the receiver unchanged ("난 시간적으로 이어지는 데이터를 말한거긴 해", "일단 1번으로 하고 ... 범위(넓이)를 더 크게해서 중복이
없개하면 될거 같아").  Everything except the UE positions / orientations and the split is the room pool SRB (srb_build.py): the
built-in `box` scene as shipped (metal walls), 28 GHz, PathSolver max_depth 1 (LoS + first-order specular), samples_per_src 1e8,
PlanarArray 1 x Nr / 1 x 4 isotropic V half-wavelength ULAs, ONE fixed BS at the same rule-placed point, Paths.cfr at the carrier,
per-pair normalisation by the sum of the path powers.

The path (fixed before any SRP BLER):
  UE          one UE moves along a boustrophedon (lawn-mower) route over the floor at height 1.5 m: NY = 576 rows 1.5 cm apart,
              NX = 600 snapshots 1.5 cm apart on each row, alternate rows walked in opposite directions -- 345600 snapshots in
              time order, no position is visited twice (1.5 cm = 1.4 wavelengths at 28 GHz: neighbouring snapshots are already
              different channels).  The lattice is centred in the room (x in [-4.4925, 4.4925], y in [-4.3125, 4.3125] m).
  yaw         the UE array keeps its orientation relative to the direction of travel: yaw = heading = 0 on the rows walked in
              +x, pi on the rows walked in -x (no random orientation)
  split       BY TIME: the LAST 87 rows of the route (the smallest number of final rows holding >= 15 % of the snapshots: 52200
              = an area the UE has not entered before) are the TEST pool; of the earlier snapshots a frozen random
              N_VAL_POOL = 20000 are the validation pool, the rest the fit pool (dmimo.py's stream -> pool map).  The tile key
              of dmimo's self-check is the row index.
  rng         default_rng([SEED, TBID["D2"], 12, PID["SRP"], 1]) for the validation draw only (the route is deterministic);
              solver seed = chunk index.  The solver's candidate generator is not deterministic: a rebuild need not reproduce
              the sha.
Receivers are packed as arrays exactly as in srb_build.py (`selfcheck` compares with the stock packing on 64 receivers).

usage (GPU):  CUDA_VISIBLE_DEVICES=<g> python -I code/srp_build.py build [Nr]      -> ~/data/sionna_rt/srp_Nr<Nr>/{H.npy, split.npy, meta.npz}
              CUDA_VISIBLE_DEVICES=<g> python -I code/srp_build.py selfcheck
H.npy / split.npy are pinned by dmimo.POOL_SHA; meta.npz (position, yaw, time index, row, LoS, path count) is descriptive only.
"""
import hashlib
import os
import sys
import time

import numpy as np

SCENE, NT, FC, DEPTH, SAMPLES, MAXPATHS = "box", 4, 28e9, 1, 10 ** 8, 10 ** 7
BS_FRAC, H_UE = (0.2, 0.3, 0.8), 1.5
NX, NY, STEP = 600, 576, 0.015                                   # snapshots per row, rows, spacing [m] along and across the rows
TARGET, CHUNK, TEST_SHARE, N_VAL_POOL = NX * NY, 7200, 0.15, 20000


def out_dir(Nr):
    return os.path.expanduser(f"~/data/sionna_rt/srp_Nr{Nr}")


def sha16(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()[:16]


def _rng(*tail):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import common as C
    return np.random.default_rng([C.SEED, C.TBID["D2"], 12, C.PID["SRP"], *tail])


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
    cen = 0.5 * (lo[:2] + hi[:2])
    row = np.repeat(np.arange(NY), NX)                           # the route in time order: row j is walked in +x (j even) or -x (j odd)
    col = np.tile(np.arange(NX), NY)
    col = np.where(row % 2 == 0, col, NX - 1 - col)
    xy = cen + STEP * np.stack([col - (NX - 1) / 2, row - (NY - 1) / 2], 1)
    yaw = np.where(row % 2 == 0, 0.0, np.pi)                     # the UE array keeps its orientation relative to the direction of travel
    assert (np.abs(xy - cen) < 0.5 * sz[:2] - 0.05).all() and len(np.unique(np.round(xy / STEP * 2).astype(np.int64), axis=0)) == TARGET   # inside the room; no position twice
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
    print(f"# srp_build {SCENE}: bbox {lo.round(3)} .. {hi.round(3)}, BS {bs.round(3)}, objects / materials "
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
    n_test_rows = int(np.ceil(TEST_SHARE * NY))                  # split BY TIME: the last rows of the route are the test pool
    istest = row >= NY - n_test_rows
    key = row.astype(np.int64)                                   # the "tile" of dmimo's self-check = the row
    idx_test = np.where(istest)[0]; tr = np.where(~istest)[0]
    v = np.zeros(len(tr), bool); v[rng.permutation(len(tr))[:N_VAL_POOL]] = True
    idx_val, idx_fit = tr[v], tr[~v]
    assert idx_test.min() > tr.max() and not set(key[idx_test]) & set(key[tr]), "the test pool must be the end of the route"
    o = out_dir(Nr); os.makedirs(o, exist_ok=True)
    split = np.zeros(n, np.int8); split[idx_val] = 1; split[idx_test] = 2      # 0 fit / 1 validation / 2 test
    np.save(os.path.join(o, "H.npy"), H)
    np.save(os.path.join(o, "split.npy"), split)                             # .npy is byte-deterministic (an .npz is not)
    np.savez(os.path.join(o, "meta.npz"), pos=xy, yaw=yaw, t=np.arange(n), row=row, los=np.concatenate(los), npath=np.concatenate(npath), key=key, bs=bs,
             bbox=np.stack([lo, hi]), scen=np.zeros(n, np.int64), scenes=np.array([SCENE]))   # descriptive only, not pinned
    print(f"# srp_build Nr={Nr} x Nt={NT}: {n} snapshots = fit {len(idx_fit)} + val {len(idx_val)} + test {len(idx_test)} "
          f"(test share {len(idx_test) / n:.4f}); rows {NY} (the last {n_test_rows} are the test pool, y >= {xy[idx_test, 1].min():.4f} m); {time.time() - t0:.0f} s")
    print(f"POOL_SHA[('SRP', {Nr})] = ({sha16(os.path.join(o, 'H.npy'))!r}, {sha16(os.path.join(o, 'split.npy'))!r})")
    return o


if __name__ == "__main__":
    mode = sys.argv[1]
    assert mode in ("build", "selfcheck"), mode
    build(int(sys.argv[2]) if len(sys.argv) > 2 else 8, check=mode == "selfcheck")
