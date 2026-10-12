"""rank_probe_2026-10-11/srt_box_material.py -- box scene, fixed BS (srt_box_probe.py's rule), max_depth 5, samples 1e8: the share of
rank-1 links with the walls as shipped ('box-mat': relative permittivity 1, conductivity 1e7 S/m = a metal box) and with ITU
materials put on the same walls.  Channel statistics only."""
import sys
import numpy as np
import mitsuba as mi
import sionna.rt as rt
from sionna.rt import ITURadioMaterial, PathSolver, PlanarArray, Receiver, Transmitter, load_scene
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
solver = PathSolver()
print(f"{'walls':<16} {'depth':>5} {'paths':>7} {'rank-1':>7} {'<0.80':>6} {'erank':>6}")
for mat in ("as shipped", "concrete", "plasterboard", "glass", "wood", "metal"):
    if mat != "as shipped":
        m = ITURadioMaterial(f"w-{mat}", mat, thickness=0.1)
        for o in scene.objects.values():
            o.radio_material = m
    for depth in (2, 5):
        p = solver(scene, max_depth=depth, max_num_paths_per_src=10 ** 7, los=True, specular_reflection=True, diffuse_reflection=False, refraction=False,
                   diffraction=False, samples_per_src=10 ** 8, synthetic_array=True, seed=1)
        h = p.cfr(frequencies=mi.Float([0.0]), normalize_delays=False, normalize=False, out_type="numpy")[:, :, 0, :, 0, 0]
        H = h.transpose(0, 2, 1)
        q = np.linalg.svd(H, compute_uv=False) ** 2; q /= q.sum(1, keepdims=True)
        er = np.exp(-(q * np.log(np.maximum(q, 1e-300))).sum(1))
        v = np.asarray(p.valid.numpy()).reshape(N, -1)
        print(f"{mat:<16} {depth:5d} {v.sum(1).mean():7.1f} {(q[:, 0] >= 0.95).mean():7.3f} {(q[:, 0] < 0.80).mean():6.3f} {er.mean():6.2f}", flush=True)
