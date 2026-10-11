"""rank_probe_2026-10-11/srt_box_save.py -- save candidate channel sets of Sionna RT room scenes (ONE fixed BS by srt_box_probe.py's
rule, N UE positions, 28 GHz, LoS + specular, samples 1e8) for genie_screen.py: scene x wall material x max_depth.
usage: CUDA_VISIBLE_DEVICES=<g> python -I srt_box_save.py <out_dir> <N>"""
import os
import sys
import numpy as np
import mitsuba as mi
import sionna.rt as rt
from sionna.rt import ITURadioMaterial, PathSolver, PlanarArray, Receiver, Transmitter, load_scene
out, N = sys.argv[1], int(sys.argv[2])
arr = lambda n: PlanarArray(num_rows=1, num_cols=n, vertical_spacing=0.5, horizontal_spacing=0.5, pattern="iso", polarization="V")
for name, mats, depths in (("box", ("shipped", "concrete", "glass"), (1, 2, 5)), ("box_one_screen", ("shipped",), (1, 2)), ("box_two_screens", ("shipped",), (1, 2, 5))):
    scene = load_scene(getattr(rt.scene, name)); scene.frequency = 28e9
    bb = scene.mi_scene.bbox(); lo, hi = np.array(bb.min).ravel(), np.array(bb.max).ravel(); sz = hi - lo
    rng = np.random.default_rng(20260926)
    xy = lo[:2] + sz[:2] * rng.uniform(0.05, 0.95, (N, 2)); yaw = rng.uniform(-np.pi, np.pi, N)
    scene.tx_array, scene.rx_array = arr(8), arr(4)
    scene.add(Transmitter(name="bs", position=[float(lo[0] + 0.2 * sz[0]), float(lo[1] + 0.3 * sz[1]), float(lo[2] + 0.8 * sz[2])], orientation=[0.0, 0.0, 0.0]))
    for i in range(N):
        scene.add(Receiver(name=f"ue{i}", position=[float(xy[i, 0]), float(xy[i, 1]), float(lo[2] + 1.5)], orientation=[float(yaw[i]), 0.0, 0.0]))
    solver = PathSolver()
    for mat in mats:
        if mat != "shipped":
            m = ITURadioMaterial(f"w-{mat}", mat, thickness=0.1)
            for o in scene.objects.values():
                o.radio_material = m
        for depth in depths:
            p = solver(scene, max_depth=depth, max_num_paths_per_src=10 ** 7, los=True, specular_reflection=True, diffuse_reflection=False,
                       refraction=False, diffraction=False, samples_per_src=10 ** 8, synthetic_array=True, seed=1)
            h = p.cfr(frequencies=mi.Float([0.0]), normalize_delays=False, normalize=False, out_type="numpy")[:, :, 0, :, 0, 0]
            ar, ai = p.a                                         # per-pair normalisation of the pool recipe (srb_build.py): sum of path powers = 1
            a = (np.asarray(ar.numpy()) + 1j * np.asarray(ai.numpy()))[:, 0, 0, 0, :]
            v = np.asarray(p.valid.numpy()).reshape(N, -1)
            pw = (np.abs(a) ** 2 * v).sum(1); ok = pw > 0
            H = h[ok].transpose(0, 2, 1) / np.sqrt(pw[ok])[:, None, None]
            np.save(os.path.join(out, f"{name}_{mat}_d{depth}_norm.npy"), H.astype(np.complex64))
            print(f"SAVED {name}_{mat}_d{depth}_norm {len(H)} of {N}", flush=True)
