"""Scratch probe (channel statistics only, no receiver): Sionna RT, ONE fixed BS, UE positions varied; carrier and propagation
mechanisms varied on the SAME UE positions.  Reports the share of rank-1 links (largest singular value's energy share >= 0.95).
usage: CUDA_VISIBLE_DEVICES=<g> python -I srt_fixed_probe.py <scene> <bs_x> <bs_y> <bs_z> [n_ue] [r_max]"""
import sys
import time

import numpy as np

name, bs = sys.argv[1], [float(x) for x in sys.argv[2:5]]
N = int(sys.argv[5]) if len(sys.argv) > 5 else 2048
RMAX = float(sys.argv[6]) if len(sys.argv) > 6 else 400.0
NR, NT, H_UE, GROUND = 8, 4, 1.5, 1.0

import mitsuba as mi
import sionna.rt as rt
from sionna.rt import PathSolver, PlanarArray, Receiver, Transmitter, load_scene

scene = load_scene(getattr(rt.scene, name))
bb = scene.mi_scene.bbox(); top = float(np.array(bb.max).ravel()[2]) + 1.0


def on_ground(xy):                                               # srt_build.py's test: the surface seen from above is below GROUND
    o = mi.Point3f(mi.Float(xy[:, 0].astype(np.float32)), mi.Float(xy[:, 1].astype(np.float32)), top)
    s = scene.mi_scene.ray_intersect(mi.Ray3f(o, mi.Vector3f(0.0, 0.0, -1.0)))
    return np.asarray(s.is_valid()) & (np.asarray(s.p.z) < GROUND)


rng = np.random.default_rng(20260926)
r = np.sqrt(rng.uniform(10.0 ** 2, RMAX ** 2, 16 * N)); ph = rng.uniform(-np.pi, np.pi, 16 * N)
xy = np.array(bs[:2]) + np.stack([r * np.cos(ph), r * np.sin(ph)], 1)
xy = xy[on_ground(xy)][:N]
yaw = rng.uniform(-np.pi, np.pi, len(xy))
assert len(xy) == N, len(xy)
scene.add(Transmitter(name="bs", position=bs, orientation=[0.0, 0.0, 0.0]))
t0 = time.time()
for i in range(N):
    scene.add(Receiver(name=f"ue{i}", position=[float(xy[i, 0]), float(xy[i, 1]), H_UE], orientation=[float(yaw[i]), 0.0, 0.0]))
print(f"# {name}: BS fixed at {bs}, {N} outdoor UE positions within {RMAX:.0f} m (uniform in area), h_UE {H_UE} m; receivers added in {time.time() - t0:.0f} s", flush=True)
solver = PathSolver()
arr = lambda n: PlanarArray(num_rows=1, num_cols=n, vertical_spacing=0.5, horizontal_spacing=0.5, pattern="iso", polarization="V")
print(f"{'carrier':>8} {'depth':>5} {'mechanisms':<34} {'with-path':>9} {'LoS':>6} {'paths':>6} {'rank-1':>7} {'<0.80':>6} {'erank':>6} {'rank-1|LoS':>10} {'rank-1|NLoS':>11}")
for fc, depth, refr, diff, dif in [(28e9, 2, 0, 0, 0), (3.5e9, 2, 0, 0, 0), (28e9, 3, 0, 0, 0), (3.5e9, 3, 0, 0, 0), (28e9, 5, 0, 0, 0), (3.5e9, 5, 0, 0, 0),
                                   (28e9, 3, 1, 1, 0), (3.5e9, 3, 1, 1, 0), (28e9, 3, 0, 1, 0), (3.5e9, 3, 0, 1, 0), (3.5e9, 3, 1, 0, 0)]:
    scene.frequency = fc
    scene.tx_array, scene.rx_array = arr(NR), arr(NT)
    lab = "specular" + (" + refraction" if refr else "") + (" + diffraction" if diff else "") + (" + diffuse" if dif else "")
    try:
        p = solver(scene, max_depth=depth, los=True, specular_reflection=True, diffuse_reflection=bool(dif), refraction=bool(refr),
                   diffraction=bool(diff), samples_per_src=10 ** 7, synthetic_array=True, seed=1)
        h = p.cfr(frequencies=mi.Float([0.0]), normalize_delays=False, normalize=False, out_type="numpy")[:, :, 0, :, 0, 0]
        ar, ai = p.a
        a = (np.asarray(ar.numpy()) + 1j * np.asarray(ai.numpy()))[:, 0, 0, 0, :]
        v = np.asarray(p.valid.numpy()).reshape(N, -1)
        it = np.asarray(p.interactions.numpy())
    except Exception as e:                                       # a mechanism this build does not support: say so and go on
        print(f"{fc / 1e9:8.1f} {depth:5d} {lab:<34} FAILED: {type(e).__name__}: {str(e)[:120]}", flush=True)
        continue
    pw = (np.abs(a) ** 2 * v).sum(1); ok = v.any(1) & (pw > 0)
    H = h[ok].transpose(0, 2, 1) / np.sqrt(pw[ok])[:, None, None]
    s = np.linalg.svd(H, compute_uv=False) ** 2; q = s / s.sum(1, keepdims=True); sh = q[:, 0]
    er = np.exp(-(q * np.log(np.maximum(q, 1e-300))).sum(1))
    los = ((it[0, :, 0, :] == 0) & v).any(1)[ok]
    f = lambda m: f"{(sh[m] >= 0.95).mean():.3f}" if m.any() else "  -  "
    print(f"{fc / 1e9:8.1f} {depth:5d} {lab:<34} {ok.mean():9.3f} {los.mean():6.3f} {v.sum(1)[ok].mean():6.1f} {(sh >= 0.95).mean():7.3f} {(sh < 0.80).mean():6.3f} "
          f"{er.mean():6.2f} {f(los):>10} {f(~los):>11}", flush=True)
print(f"# done in {time.time() - t0:.0f} s")
