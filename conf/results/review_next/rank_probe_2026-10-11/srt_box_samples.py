"""rank_probe_2026-10-11/srt_box_samples.py -- box scene, fixed BS (srt_box_probe.py's rule): how complete is the specular path set
at a given max_depth as samples_per_src grows (image-source count of a rectangular room: 1 + sum_{n<=d} (4 n^2 + 2))."""
import sys, time
import numpy as np
import mitsuba as mi
import sionna.rt as rt
from sionna.rt import PathSolver, PlanarArray, Receiver, Transmitter, load_scene
N = int(sys.argv[1]) if len(sys.argv) > 1 else 1024
scene = load_scene(rt.scene.box); scene.frequency = 28e9
bb = scene.mi_scene.bbox(); lo, hi = np.array(bb.min).ravel(), np.array(bb.max).ravel(); sz = hi - lo
rng = np.random.default_rng(20260926)
xy = lo[:2] + sz[:2] * rng.uniform(0.05, 0.95, (N, 2)); yaw = rng.uniform(-np.pi, np.pi, N)
arr = lambda n: PlanarArray(num_rows=1, num_cols=n, vertical_spacing=0.5, horizontal_spacing=0.5, pattern="iso", polarization="V")
scene.tx_array, scene.rx_array = arr(8), arr(4)
scene.add(Transmitter(name="bs", position=[float(lo[0] + 0.2 * sz[0]), float(lo[1] + 0.3 * sz[1]), float(lo[2] + 0.8 * sz[2])], orientation=[0.0, 0.0, 0.0]))
for i in range(N):
    scene.add(Receiver(name=f"ue{i}", position=[float(xy[i, 0]), float(xy[i, 1]), 1.5], orientation=[float(yaw[i]), 0.0, 0.0]))
print("materials:", {o: str(scene.objects[o].radio_material.name) for o in scene.objects})
solver = PathSolver()
print(f"{'depth':>5} {'samples':>8} {'maxpaths':>9} {'paths':>7} {'of':>4} {'rank-1':>7} {'<0.80':>6} {'erank':>6} {'pw kept':>8} {'sec':>5}")
ref = {}
for depth, smp, mx in [(3, 10 ** 7, 10 ** 6), (3, 10 ** 8, 10 ** 7), (5, 10 ** 7, 10 ** 6), (5, 10 ** 8, 10 ** 7), (5, 3 * 10 ** 8, 10 ** 7)]:
    t0 = time.time()
    try:
        p = solver(scene, max_depth=depth, max_num_paths_per_src=mx, los=True, specular_reflection=True, diffuse_reflection=False, refraction=False,
                   diffraction=False, samples_per_src=smp, synthetic_array=True, seed=1)
        h = p.cfr(frequencies=mi.Float([0.0]), normalize_delays=False, normalize=False, out_type="numpy")[:, :, 0, :, 0, 0]
        ar, ai = p.a
        a = (np.asarray(ar.numpy()) + 1j * np.asarray(ai.numpy()))[:, 0, 0, 0, :]
        v = np.asarray(p.valid.numpy()).reshape(N, -1)
    except Exception as e:
        print(f"{depth:5d} {smp:8.0e} {mx:9.0e} FAILED {type(e).__name__}: {str(e)[:100]}", flush=True); continue
    pw = (np.abs(a) ** 2 * v).sum(1); H = h.transpose(0, 2, 1) / np.sqrt(pw)[:, None, None]
    q = np.linalg.svd(H, compute_uv=False) ** 2; q /= q.sum(1, keepdims=True)
    er = np.exp(-(q * np.log(np.maximum(q, 1e-300))).sum(1))
    ref.setdefault(depth, pw)                                    # path power relative to the first (smallest) sample count of this depth
    print(f"{depth:5d} {smp:8.0e} {mx:9.0e} {v.sum(1).mean():7.1f} {1 + sum(4 * n * n + 2 for n in range(1, depth + 1)):4d} {(q[:, 0] >= 0.95).mean():7.3f} {(q[:, 0] < 0.80).mean():6.3f} "
          f"{er.mean():6.2f} {np.mean(ref[depth] / pw):8.3f} {time.time() - t0:5.0f}", flush=True)
