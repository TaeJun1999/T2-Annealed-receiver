"""rank_probe_2026-10-11/srt_box_probe.py -- channel statistics only: Sionna RT built-in closed / canyon scenes, ONE fixed BS placed by
rule from the bounding box (x at 20 %, y at 30 % of the footprint, z at 80 % of the height), UEs uniform over the footprint
(5 % margin) at z = min(1.5 m, 30 % of the height) with random yaw; 28 GHz, LoS + specular, 8x4 half-wavelength ULAs.
Reports the share of rank-1 links (largest singular value's energy share >= 0.95) per max_depth.
usage: CUDA_VISIBLE_DEVICES=<g> python -I srt_box_probe.py <scene> [n_ue]"""
import sys

import numpy as np

name = sys.argv[1]; N = int(sys.argv[2]) if len(sys.argv) > 2 else 1024
import mitsuba as mi
import sionna.rt as rt
from sionna.rt import PathSolver, PlanarArray, Receiver, Transmitter, load_scene

scene = load_scene(getattr(rt.scene, name)); scene.frequency = 28e9
bb = scene.mi_scene.bbox(); lo, hi = np.array(bb.min).ravel(), np.array(bb.max).ravel(); sz = hi - lo
bs = [float(lo[0] + 0.2 * sz[0]), float(lo[1] + 0.3 * sz[1]), float(lo[2] + 0.8 * sz[2])]
zu = float(lo[2] + min(1.5, 0.3 * sz[2]))
rng = np.random.default_rng(20260926)
xy = lo[:2] + sz[:2] * rng.uniform(0.05, 0.95, (N, 2)); yaw = rng.uniform(-np.pi, np.pi, N)
arr = lambda n: PlanarArray(num_rows=1, num_cols=n, vertical_spacing=0.5, horizontal_spacing=0.5, pattern="iso", polarization="V")
scene.tx_array, scene.rx_array = arr(8), arr(4)
scene.add(Transmitter(name="bs", position=bs, orientation=[0.0, 0.0, 0.0]))
for i in range(N):
    scene.add(Receiver(name=f"ue{i}", position=[float(xy[i, 0]), float(xy[i, 1]), zu], orientation=[float(yaw[i]), 0.0, 0.0]))
print(f"# {name}: bbox {lo.round(2)} .. {hi.round(2)}, objects {list(scene.objects)[:8]}, BS {np.round(bs, 2)}, UE z {zu:.2f}, {N} UEs")
solver = PathSolver()
print(f"{'depth':>5} {'with-path':>9} {'LoS':>6} {'paths':>6} {'rank-1':>7} {'<0.80':>6} {'erank':>6}")
for depth in (1, 2, 3, 5):
    p = solver(scene, max_depth=depth, los=True, specular_reflection=True, diffuse_reflection=False, refraction=False, diffraction=False,
               samples_per_src=10 ** 7, synthetic_array=True, seed=1)
    h = p.cfr(frequencies=mi.Float([0.0]), normalize_delays=False, normalize=False, out_type="numpy")[:, :, 0, :, 0, 0]
    ar, ai = p.a
    a = (np.asarray(ar.numpy()) + 1j * np.asarray(ai.numpy()))[:, 0, 0, 0, :]
    v = np.asarray(p.valid.numpy()).reshape(N, -1); it = np.asarray(p.interactions.numpy())
    pw = (np.abs(a) ** 2 * v).sum(1); ok = v.any(1) & (pw > 0)
    H = h[ok].transpose(0, 2, 1) / np.sqrt(pw[ok])[:, None, None]
    q = np.linalg.svd(H, compute_uv=False) ** 2; q /= q.sum(1, keepdims=True); sh = q[:, 0]
    er = np.exp(-(q * np.log(np.maximum(q, 1e-300))).sum(1)); los = ((it[0, :, 0, :] == 0) & v).any(1)[ok]
    print(f"{depth:5d} {ok.mean():9.3f} {los.mean():6.3f} {v.sum(1)[ok].mean():6.1f} {(sh >= 0.95).mean():7.3f} {(sh < 0.80).mean():6.3f} {er.mean():6.2f}", flush=True)
