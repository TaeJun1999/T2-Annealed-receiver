**Verdict: none of the Sionna RT configurations is favourable to the diffusion prior. Drop this family.** In every non-degenerate config, EM-GMM with K=64 closes 0.65–0.77 of the pilot-stage gap between K=1 and the latent oracle at −3 dB. That matches the known GMM-friendly UMi value (0.68). D2, run with the same code and sizes, closes 0.26. The least unfavourable config is `et28_d2_rs` (etoile scene, 28 GHz, depth 2, random BS sites): 0.65 at −3 dB and 0.61 at +3 dB. It is still UMi-like.

## Calibration (D2 S2, same code and sizes)
- **8x4:** K=16/64/256 close 0.19 / 0.26 / 0.29 at −3 dB. K=64 closes 0.25 at +3 dB. K1−LO gap 0.250 (6.6 dB). Outage 0.003.
- **16x4:** 0.21 / 0.26 / 0.24; K=64 closes 0.25 at +3 dB. Gap 0.273 (9.1 dB).

## Setup (to register)
- **Solver:** Sionna RT 2.1, `PathSolver`. Specular only, LOS on, refraction and diffraction off, `samples_per_src` 1e7. The BS is the ray source (uplink by reciprocity).
- **Antennas:** single V-polarised iso element at both ends. The ULAs are built afterwards from each path's directions.
  - BS ULA is horizontal and perpendicular to the site boresight. Downtilt has no effect on a horizontal iso ULA.
  - UE ULA is horizontal with yaw ~ U[−π, π) and no tilt or slant. Half-wavelength spacing on both sides.
- **Placement:** BS at 10 m. UEs at 1.5 m, uniform over a 120° sector annulus of 10–200 m (120 m in the canyon scene).
- **Normalisation and conventions:** per-sample Σ|a_l|² = 1 (pathloss and shadowing removed), ensemble normalised on the train set, no-path samples dropped, column-major vec.
- **Sizes:** train 36000, validation 4000 (early stop, patience 40, n_iter 200), test 2000, R = 400. The reference script used 500 test samples; 2000 cuts the noise and D2 still reproduces 0.26.
- **LO oracle:** directions and |a| fixed, path phases redrawn, as in the reference script. I also computed it exactly (`LOx`); it matches the Monte Carlo version.
- **Site selection:**
  - `s1`: the best of 60 random munich candidates by sector coverage.
  - `m4`: 4 such fixed sites, at least 150 m apart.
  - `rs`: a new uniform random site with a uniform random boresight for every batch of 1000 UEs (129–1215 sites per config).

## Results
cl = fraction closed at −3 dB unless marked; vsLOm = K=64 against the sensitivity oracle described under Caveats.

| config | cl64 | cl16 / cl256 | cl64 @+3 dB | cl64 vsLOm | cl64 NLOS | gap (dB) | LOS | eff. paths | cond. erank | P(rank90≥3) | erank(C) | top4 / top8 | leak iid / block | outage −3 dB | gen h for 1.84e5 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D2 8x4 | 0.26 | 0.19 / 0.29 | 0.25 | – | – | 6.6 | 0 | 3.43 | 3.17 | 0.98 | 28.5 | 0.67 / 0.84 | 0.00 / – | 0.003 | – |
| et28_d2_rs | 0.65 | 0.55 / 0.70 | 0.61 | 0.64 | 0.69 | 9.2 | 0.75 | 2.47 | 1.46 | 0.14 | 26.5 | 0.85 / 0.94 | 0.06 / 0.05 | 0.57 | 0.07 |
| fl28_d2_rs | 0.66 | 0.55 / 0.70 | 0.63 | 0.65 | 0.66 | 9.2 | 0.87 | 2.19 | 1.40 | 0.13 | 27.1 | 0.85 / 0.94 | 0.06 / 0.05 | 0.57 | 0.31 |
| mu28_d2_rs 16x4 | 0.67 | 0.58 / 0.69 | 0.65 | 0.67 | 0.73 | 12.2 | 0.83 | 2.30 | 1.39 | 0.13 | 54.0 | 0.84 / 0.92 | 0.07 / 0.06 | 0.44 | 0.15 |
| mu28_d2_rs | 0.68 | 0.58 / 0.73 | 0.66 | 0.67 | 0.72 | 9.5 | 0.83 | 2.30 | 1.35 | 0.11 | 27.4 | 0.86 / 0.94 | 0.13 / 0.10 | 0.59 | 0.15 |
| mu28_d1_s1 | 0.68 | 0.53 / 0.79 | 0.67 | 0.68 | 0.73 | 8.1 | 0.77 | 2.65 | 1.62 | 0.18 | 9.9 | 0.83 / 0.93 | 0.38 / 0.23 | 0.27 | 0.03 |
| mu28_d3_rs NLOS-only | 0.69 | 0.58 / 0.73 | 0.67 | 0.68 | – | 9.9 | 0 | 2.61 | 1.43 | 0.15 | 23.0 | 0.86 / 0.94 | 0.13 / 0.13 | 0.49 | 1.10 |
| mu28_d2_s1 | 0.69 | 0.55 / 0.77 | 0.66 | 0.66 | 0.60 | 6.7 | 0.71 | 3.56 | 1.86 | 0.34 | 12.0 | 0.81 / 0.92 | 0.15 / 0.11 | 0.37 | 0.04 |
| mu28_d3_rs | 0.69 | 0.58 / 0.72 | 0.67 | 0.67 | 0.68 | 9.2 | 0.80 | 2.43 | 1.42 | 0.13 | 27.8 | 0.86 / 0.94 | 0.06 / 0.06 | 0.63 | 0.22 |
| mu28_d3_s1 16x4 | 0.69 | 0.57 / 0.75 | 0.66 | 0.67 | 0.65 | 8.2 | 0.65 | 3.71 | 2.00 | 0.45 | 16.4 | 0.78 / 0.89 | 0.06 / 0.04 | 0.19 | 0.06 |
| mu28_d1_m4 | 0.70 | 0.56 / 0.76 | 0.69 | 0.69 | 0.77 | 9.9 | 0.76 | 1.90 | 1.25 | 0.07 | 16.0 | 0.85 / 0.94 | 0.28 / 0.22 | 0.37 | 0.02 |
| mu28_d3_s1 | 0.70 | 0.56 / 0.76 | 0.66 | 0.65 | 0.62 | 6.4 | 0.65 | 3.71 | 1.93 | 0.41 | 10.7 | 0.82 / 0.92 | 0.08 / 0.05 | 0.44 | 0.06 |
| mu28_d2_m4 | 0.74 | 0.62 / 0.78 | 0.68 | 0.72 | 0.70 | 9.1 | 0.71 | 2.38 | 1.41 | 0.16 | 25.9 | 0.85 / 0.94 | 0.15 / 0.15 | 0.42 | 0.03 |
| mu35_d2_s1 (3.5 GHz) | 0.75 | 0.63 / 0.82 | 0.70 | 0.72 | 0.66 | 7.3 | 0.71 | 2.76 | 1.50 | 0.15 | 14.1 | 0.82 / 0.92 | 0.15 / 0.09 | 0.47 | 0.04 |
| cy28_d4_s1 (street canyon, BS in street) | 0.77 | 0.64 / 0.83 | 0.76 | 0.77 | 0.79 | 9.7 | 0.27 | 2.09 | 1.52 | 0.24 | 23.6 | 0.84 / 0.93 | 0.52 / 0.44 | 0.39 | 0.07 |
| cy28_d4_s0 (**degenerate**, open-area site) | 0.87 | 0.76 / 0.92 | 0.88 | 0.87 | – | 13.0 | 1.00 | 1.01 | 1.01 | 0.00 | 24.9 | 0.90 / 0.96 | 0.93 / 0.92 | 0.06 | 0.05 |
| mu28_d1_s1_diff (**invalid**, see below) | −2.24 | – | – | – | – | LO worse than K1 | 0.56 | 66.8 | – | – | 11.1 | 0.81 / 0.91 | 0.24 / 0.16 | 0.79 | 0.37 |

Labels: mu = munich, et = etoile, fl = florence, cy = simple_street_canyon; 28/35 = GHz; d = max_depth. 8x4 unless marked.

## Why RT is GMM-friendly
- **Near-rank-1 channels.** The effective rank of each sample's conditional (LO) covariance is 1.25–2.0 in RT versus 3.2 in D2. The share of samples with 90%-energy rank ≥ 3 is 0.07–0.45 in RT versus 0.98 in D2.
- **Paths the arrays cannot separate.** LOS and its ground bounce share the same steering vector, and reflections along one street fall inside the 8x4 beam resolution. So the channel is roughly one steering vector over a 2-D (s_r, s_t) manifold. K=64 components tile the 32 beam cells.
- **Few latent dimensions.** Per site the latent is only (x, y, yaw). In D2 it is 2L = 6–16 independent angles.
- **Nothing I varied moved it.** Depth 1→4, fixed or random multi-BS, 28 vs 3.5 GHz, four scenes, NLOS-only and Nr=16 all stay at 0.65–0.77.
- **Beamspace sparsity misleads here.** RT is sparser than D2 (top-4 energy 0.78–0.86 vs 0.67), but because it is nearly rank-1, which is exactly what the GMM tiles well.
- **High outage.** −3 dB outage is 0.27–0.63 (D2: 0.003), because rank-1 channels cap mutual information near 4 bit. That regime is also insensitive to the prior.

## Caveats and checks
- **Diffuse control is invalid.** Sionna's diffuse micro-paths add coherently: actual ‖h‖² / (N·Σ|a|²) has mean 56 and p90 214 (0.94 for specular depth 1). Redrawing their phases is therefore not an oracle (LO comes out worse than K1), and energy becomes heavy-tailed (outage 0.79). Scattering coefficient 0.3, samples_per_src 4e6, strongest 512 paths kept (94% of energy).
- **Coherent-merge oracle (LOm).** At depth ≥ 2, the coherence ratio above has mean 0.49 (depth 3), so the specified LO is loose. LOm is a sensitivity variant: paths whose steering coordinates differ by less than 0.005 on both sides are summed coherently before the phase redraw. It lowers the closed fraction by at most 0.05; the verdict does not change.
- **EM iteration cap.** Raising n_iter from 200 to 600 on `et28_d2_rs` changes nothing (0.65 / 0.61; it converges near iteration 250).
- **NLOS-only split.** `mu28_d3_rs` NLOS-only had 39,348 NLOS samples, so validation was cut to 1,348 to keep the 36,000 training samples.
- **Leakage** is dense coverage of the channel manifold, not repeated positions: the median nearest-neighbour position gap is 0.3 m, about 28 wavelengths. The spatial-block split gives similar numbers.
- **Throughput** is 0.4–7 ms per valid sample on one GPU, so the full 1.84e5-sample set takes 0.02–0.37 h (1.1 h for NLOS-only).

## Implementation notes
- **GPU EM:** a complex128 torch port of `fit_gmm_em` (`emt.py`). Checked against the numpy original: covariance difference 3e-13, same best iteration.
- **Sionna speed-up:** the stock endpoint builder bakes each receiver position into the compiled kernel, which forced a ~20 s recompile per batch. I patched `Scene._endpoints` to pass all receiver positions as one array. Path gains are unchanged (max difference 2e-10 on amplitudes around 2e-5).

Files are in `/tmp/claude-1005/-home-HTJ-t2/47f1f727-1d40-4c8f-a798-01f8d9d886c3/scratchpad/tb2/rt/`:
- Scripts: `gen_rt.py`, `ana.py`, `emt.py`, `crank.py`, `coh.py`, `table.py`
- Results: `res_*.json`, `crank_*.json`
- Logs: `log_b_*.txt` (final RT runs), `log_D2_*.txt`, `log_a_mu28_d1_s1_diff.txt`, `log_c_et28_iter600.txt`
- Data: `g_*.npz`