"""conf/code/srt_build.py -- ONE-TIME builder of the Sionna RT channel pool (prior 'SRT'); dmimo.py reads the result.

User instruction 2026-10-10 CDT (conf/DECISIONS.md): after DeepMIMO, run the receiver BLER on Sionna as well -- Sionna RT (ray
tracing) is the Sionna family without a receiver BLER (3GPP 38.901 through Sionna PHY is UMi28 / MIX3).  Same sizes as every
other testbed; the channels come from the LIBRARY'S OWN generator (the user's DeepMIMO instruction, applied here too):
Sionna RT 2.1 PathSolver + its PlanarArray antenna arrays (synthetic_array=True) + Paths.cfr -- no array code of ours.

Every choice (fixed before any SRT BLER; the phase-0 "rs" configuration of
conf/results/review_next/testbed2_phase0/report_rt.md, pooled over the built-in city scenes like DeepMIMO's 6 cities):
  scenes      SCENES = the outdoor city scenes shipped with Sionna RT 2.1, 28 GHz
  solver      PathSolver(): max_depth 2, LoS on, specular reflection on, diffuse reflection / refraction / diffraction off,
              samples_per_src 1e7, synthetic arrays; the BS is the ray source (uplink by reciprocity: H_ul = H_dl^T)
  arrays      BS = PlanarArray 1 x Nr, UE = PlanarArray 1 x 4, isotropic V-polarised elements, half-wavelength spacing (a
              horizontal ULA perpendicular to the device's boresight); BS orientation = [boresight yaw, 0, 0],
              UE orientation = [yaw, 0, 0] with yaw ~ U[-pi, pi) per UE
  sites       "rs": for every batch a NEW BS site, uniform over the scene's xy bounding box and kept only if it stands on the
              ground (the surface seen from above at (x, y) is below GROUND m: not on / in a building), height H_BS above z = 0,
              boresight ~ U[-pi, pi); NC candidate UEs per site, uniform over the OUTDOOR part (same ground test) of the
              120 deg sector annulus R0..R1 m around the boresight, height H_UE.  The NC candidates are the first NC outdoor
              points among 4 NC uniform draws; a site with fewer than NC outdoor points among them (outdoor share of its
              sector annulus below about 25 %) is SKIPPED -- sites in densely built places are under-represented.  The
              ground test looks only from above: a courtyard-like spot enclosed by walls passes it, and such a BS site then
              reaches almost no UE (the pair rule drops the UEs without a path)
  pairs       the candidates with at least one path, at most NB per site in candidate order (phase 0: "a new site for every
              batch of 1000 UEs"; the cap keeps one open-area site from dominating); the scene loop stops at TARGET pairs per
              scene (the last site is truncated)
  speed       the stock Scene.targets packs the receivers one by one (a Python loop of scatters: seconds per thousand UEs);
              here the SAME quantities (positions, orientations, rotated element offsets = PlanarArray.positions rotated about
              z by the UE yaw) are handed to the solver as whole arrays -- `selfcheck` compares them with the stock builder.
              Path tracing, fields, array synthesis and the frequency response are Sionna's, unchanged
  channel     Paths.cfr at the carrier (frequency offset 0 -> narrowband), per-pair normalisation by sqrt(sum of the path
              powers |a_l|^2 of the reference element pair) -- pathloss removed, multipath interference kept; dmimo.py then
              normalises the ensemble
  split       20 m position tiles keyed by (scene, floor(xy / 20)); a seeded shuffle of the tiles, test tiles until they hold
              >= 15 % of the pairs; of the remaining pairs a seeded random 20000 = validation pool, the rest = fit pool
              (the DeepMIMO rule, dmimo_build.py)
Output  ~/data/sionna_rt/srt_Nr<Nr>/{part_<scene>.npz, H.npy, split.npy, meta.npz}; H.npy (pairs, Nr, 4) complex64 and split.npy
are pinned by dmimo.POOL_SHA; meta.npz (scene, site, position, LoS, path count, yaw) is descriptive only.
Usage (GPU; Dr.Jit kernels are compiled on the visible GPU):
  CUDA_VISIBLE_DEVICES=<g> python -I srt_build.py scene <name> [Nr]     one scene -> part_<name>.npz  (scenes can run in parallel)
  CUDA_VISIBLE_DEVICES=<g> python -I srt_build.py probe <name>          3 batches, statistics only, nothing written
  CUDA_VISIBLE_DEVICES=<g> python -I srt_build.py selfcheck <name>      the array-packed targets == Scene.targets; channels equal
  CUDA_VISIBLE_DEVICES=     python -I srt_build.py merge [Nr]           parts -> H.npy, split.npy, meta.npz (CPU)
"""
import hashlib
import os
import sys
import time

import numpy as np

SCENES = ("munich", "etoile", "florence")       # san_francisco is left out: its ground is not flat (the z-threshold ground test
#                                                 finds almost no site: 3 of 2413 draws, all on open ground) and phase 0 did not probe it
NT, FC, DEPTH, SAMPLES = 4, 28e9, 2, 10 ** 7
NC, NB, H_BS, H_UE, R0, R1, SECTOR, GROUND = 8192, 1000, 10.0, 1.5, 10.0, 200.0, np.pi / 3, 1.0
TARGET, TILE, TEST_SHARE, N_VAL_POOL = 115200, 20.0, 0.15, 20000


def out_dir(Nr):
    return os.path.expanduser(f"~/data/sionna_rt/srt_Nr{Nr}")


def sha16(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()[:16]


def _rng(*tail):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import common as C
    return np.random.default_rng([C.SEED, C.TBID["D2"], 12, C.PID["SRT"], *tail])


def build_scene(name, Nr, probe=False, check=False):
    import drjit as dr
    import mitsuba as mi
    import sionna.rt as rt
    from sionna.rt import PathSolver, PlanarArray, Receiver, Transmitter, load_scene
    si_ = SCENES.index(name)
    rng = _rng(si_)
    scene = load_scene(getattr(rt.scene, name))
    scene.frequency = FC
    arr = lambda n: PlanarArray(num_rows=1, num_cols=n, vertical_spacing=0.5, horizontal_spacing=0.5, pattern="iso", polarization="V")
    scene.tx_array, scene.rx_array = arr(Nr), arr(NT)
    bb = scene.mi_scene.bbox()
    lo, hi = np.array(bb.min).ravel(), np.array(bb.max).ravel()

    def on_ground(xy):                                           # the surface seen from above at (x, y) is below GROUND
        o = mi.Point3f(mi.Float(xy[:, 0].astype(np.float32)), mi.Float(xy[:, 1].astype(np.float32)), float(hi[2] + 1.0))
        s = scene.mi_scene.ray_intersect(mi.Ray3f(o, mi.Vector3f(0.0, 0.0, -1.0)))
        z = np.asarray(s.p.z); ok = np.asarray(s.is_valid())
        return ok & (z < GROUND)

    scene.add(Transmitter(name="bs", position=[0.0, 0.0, H_BS], orientation=[0.0, 0.0, 0.0]))
    n_rx = 64 if check else NC
    for i in range(n_rx):                                        # the solver only needs their COUNT (Paths.num_rx); see fast_targets
        scene.add(Receiver(name=f"ue{i}", position=[1.0 + i, 0.0, H_UE], orientation=[0.0, 0.0, 0.0]))
    el = np.asarray(scene.rx_array.positions(scene.wavelength).numpy(), np.float64).reshape(3, -1).T   # (NT, 3) element offsets
    cur = {}

    def fast_targets(synthetic_array, return_velocities):       # == Scene.targets for orientation [yaw, 0, 0] (rotation about z)
        assert synthetic_array and return_velocities
        xy, yaw = cur["xy"], cur["yaw"]
        cy, sy = np.cos(yaw)[:, None], np.sin(yaw)[:, None]
        rel = np.stack([cy * el[None, :, 0] - sy * el[None, :, 1], sy * el[None, :, 0] + cy * el[None, :, 1],
                        np.broadcast_to(el[None, :, 2], (len(xy), NT))], -1).reshape(-1, 3).astype(np.float32)
        f = lambda x: mi.Float(np.ascontiguousarray(x, np.float32))
        z = np.zeros(len(xy), np.float32)
        return (mi.Point3f(f(xy[:, 0]), f(xy[:, 1]), f(z + H_UE)), mi.Point3f(f(yaw), f(z), f(z)),
                mi.Point3f(f(rel[:, 0]), f(rel[:, 1]), f(rel[:, 2])), dr.zeros(mi.Vector3f, len(xy)))

    stock_targets = scene.targets
    solver = PathSolver(deterministic=check)                     # selfcheck: deterministic candidates, so the two runs are comparable

    def solve(c, bore, xy, yaw, seed, fast=True):
        scene.get("bs").position = mi.Point3f(float(c[0]), float(c[1]), H_BS)
        scene.get("bs").orientation = mi.Point3f(float(bore), 0.0, 0.0)
        cur.update(xy=xy, yaw=yaw)
        if fast:
            scene.targets = fast_targets
        else:
            scene.targets = stock_targets
            for i in range(len(xy)):
                u = scene.get(f"ue{i}")
                u.position = mi.Point3f(float(xy[i, 0]), float(xy[i, 1]), H_UE)
                u.orientation = mi.Point3f(float(yaw[i]), 0.0, 0.0)
        paths = solver(scene, max_depth=DEPTH, los=True, specular_reflection=True, diffuse_reflection=False, refraction=False,
                       diffraction=False, samples_per_src=SAMPLES, synthetic_array=True, seed=seed)
        h = paths.cfr(frequencies=mi.Float([0.0]), normalize_delays=False, normalize=False, out_type="numpy")[:, :, 0, :, 0, 0]
        ar, ai = paths.a
        a = (np.asarray(ar.numpy()) + 1j * np.asarray(ai.numpy()))[:, 0, 0, 0, :]            # (UE, paths): reference element pair
        v = np.asarray(paths.valid.numpy()).reshape(len(xy), -1)
        it = np.asarray(paths.interactions.numpy())                                          # (depth, UE, 1, paths)
        return h, a, v, it

    Hs, pos, los, npath, yaws, site, sxy, sbore = [], [], [], [], [], [], [], []
    n, b, tries, t0 = 0, 0, 0, time.time()
    while n < TARGET and not ((probe or check) and b >= 3):
        tries += 1
        c = lo[:2] + (hi[:2] - lo[:2]) * rng.random(2)
        bore = rng.uniform(-np.pi, np.pi)
        if not on_ground(c[None])[0]:
            continue
        r = np.sqrt(rng.uniform(R0 ** 2, R1 ** 2, 4 * NC)); ph = bore + rng.uniform(-SECTOR, SECTOR, 4 * NC)
        xy = c + np.stack([r * np.cos(ph), r * np.sin(ph)], 1)
        xy = xy[on_ground(xy)][:n_rx]
        yaw = rng.uniform(-np.pi, np.pi, NC)[:n_rx]              # drawn for every site, used or not (fixed order)
        if len(xy) < n_rx:                                       # fewer than NC outdoor points among 4 NC candidates: skip the site
            continue
        h, a, v, it = solve(c, bore, xy, yaw, b)
        if check:                                                # the array-packed targets against the stock builder
            h2, a2, v2, _ = solve(c, bore, xy, yaw, b, fast=False)                           # (this also sets the stock receivers)
            cur.update(xy=xy, yaw=yaw)
            for q, (x, y) in zip(("positions", "orientations", "element offsets"), zip(fast_targets(True, True)[:3], stock_targets(True, True)[:3])):
                d = max(float(np.abs(np.asarray(getattr(x, k)) - np.asarray(getattr(y, k))).max()) for k in "xyz")
                print(f"  selfcheck site {b}: {q} max |array-packed - stock| = {d:.2e}")
            print(f"  selfcheck site {b}: valid equal {np.array_equal(v, v2) if v.shape == v2.shape else (v.shape, v2.shape)}, with-path "
                  f"{v.any(1).mean():.3f} / {v2.any(1).mean():.3f}, max |h - h_stock| / max |h_stock| = "
                  f"{(np.abs(h - h2).max() / max(np.abs(h2).max(), 1e-30)) if h.shape == h2.shape else -1:.2e}", flush=True)
        pw = (np.abs(a) ** 2 * v).sum(1)
        ok = v.any(1) & (pw > 0)
        ok &= np.cumsum(ok) <= NB                                # at most NB pairs per site, in candidate order
        H = h[ok].transpose(0, 2, 1) / np.sqrt(pw[ok])[:, None, None]                        # uplink (pairs, Nr, Nt)
        assert H.shape[1:] == (Nr, NT) and np.isfinite(H).all(), (name, b, H.shape)
        Hs.append(H.astype(np.complex64)); pos.append(xy[ok]); yaws.append(yaw[ok]); site.append(np.full(ok.sum(), b))
        los.append(((it[0, :, 0, :] == 0) & v).any(1)[ok] if v.shape[1] else np.zeros(0, bool)); npath.append(v.sum(1)[ok])
        sxy.append(c); sbore.append(bore)
        n += int(ok.sum()); b += 1
        if b % 10 == 0 or probe or check:
            print(f"  {name} site {b} ({tries} drawn): {n} pairs, with-path {v.any(1).mean():.3f} (kept {int(ok.sum())}), LoS {np.concatenate(los).mean():.3f}, "
                  f"mean paths {np.concatenate(npath).mean():.2f}, |H|_F^2 mean {(np.abs(H) ** 2).sum((1, 2)).mean() if len(H) else 0:.2f}, "
                  f"{(time.time() - t0) / max(n, 1) * 1e3:.2f} ms/pair, {time.time() - t0:.0f} s", flush=True)
    H = np.concatenate(Hs)[:TARGET]
    cut = lambda x: np.concatenate(x)[:TARGET]
    print(f"# srt_build scene {name}: {len(H)} pairs from {b} sites ({tries} drawn), bbox {lo.round(1)} .. {hi.round(1)}, {time.time() - t0:.0f} s")
    if probe or check:
        return None
    o = out_dir(Nr); os.makedirs(o, exist_ok=True)
    f = os.path.join(o, f"part_{name}.npz")
    np.savez(f, H=H, pos=cut(pos), los=cut(los), npath=cut(npath), yaw=cut(yaws), site=cut(site), sxy=np.array(sxy), sbore=np.array(sbore))
    return f


def merge(Nr):
    o = out_dir(Nr)
    P = [np.load(os.path.join(o, f"part_{s}.npz")) for s in SCENES]
    assert all(len(p["H"]) == TARGET for p in P), [len(p["H"]) for p in P]
    H = np.concatenate([p["H"] for p in P]); n = len(H)
    scen = np.repeat(np.arange(len(SCENES)), TARGET); pos = np.concatenate([p["pos"] for p in P])
    rng = _rng(len(SCENES))
    tile = np.floor(pos / TILE).astype(np.int64)                 # block split (the DeepMIMO rule): tiles keyed by (scene, floor(xy / TILE))
    key = tile[:, 0] * 100003 + tile[:, 1] + 10 ** 12 * scen
    uk, inv = np.unique(key, return_inverse=True)
    order = rng.permutation(len(uk)); cnt = np.bincount(inv)
    tsel = order[: np.searchsorted(np.cumsum(cnt[order]), TEST_SHARE * n) + 1]
    istest = np.isin(inv, tsel)
    idx_test = np.where(istest)[0]; tr = np.where(~istest)[0]
    v = np.zeros(len(tr), bool); v[rng.permutation(len(tr))[:N_VAL_POOL]] = True
    idx_val, idx_fit = tr[v], tr[~v]
    assert not set(key[idx_test]) & set(key[tr]), "a tile is on both sides of the split"
    split = np.zeros(n, np.int8); split[idx_val] = 1; split[idx_test] = 2      # 0 fit / 1 validation / 2 test
    np.save(os.path.join(o, "H.npy"), H)
    np.save(os.path.join(o, "split.npy"), split)                             # .npy is byte-deterministic (an .npz is not)
    np.savez(os.path.join(o, "meta.npz"), scen=scen, pos=pos, key=key, scenes=np.array(SCENES),
             **{k: np.concatenate([p[k] for p in P]) for k in ("los", "npath", "yaw", "site")})   # descriptive only, not pinned
    print(f"# srt_build merge Nr={Nr} x Nt={NT}: {n} pairs = fit {len(idx_fit)} + val {len(idx_val)} + test {len(idx_test)} "
          f"(test share {len(idx_test) / n:.4f}); tiles {len(uk)} ({len(tsel)} test)")
    print(f"POOL_SHA[('SRT', {Nr})] = ({sha16(os.path.join(o, 'H.npy'))!r}, {sha16(os.path.join(o, 'split.npy'))!r})")
    for s in SCENES:
        print(f"# part_{s}.npz sha256[:16] {sha16(os.path.join(o, f'part_{s}.npz'))}")


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "merge":
        merge(int(sys.argv[2]) if len(sys.argv) > 2 else 8)
    else:
        f = build_scene(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 8, probe=mode == "probe", check=mode == "selfcheck")
        if f:
            print(f"# wrote {f} sha256[:16] {sha16(f)}")
