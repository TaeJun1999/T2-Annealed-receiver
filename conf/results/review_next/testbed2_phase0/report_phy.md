None of the 38.901 configurations I tried is favourable. At K=64 and −3 dB, the EM-GMM closes 0.62–0.74 of the K1→LO gap in every 38.901 config, against 0.24–0.26 on D2 at the same sizes. No knob I tried moved a 38.901 case toward D2: carrier (28→100 GHz), forcing LoS, UMi/UMa/RMa, a UMi+UMa+RMa mix, Nr 8/16/32, and 38.901 §7.6.4 blockage model A. A favourable second testbed therefore cannot be a standard 38.901 PHY configuration. It would have to come from RT or DeepMIMO, or from a non-standard sparse model.

**Checks**
- The GPU torch port of `fit_gmm_em` matches the CPU `Demo/t2_gmm.fit_gmm_em` to about 1e-12 in covariances, with identical `it_best`, re-seeds and val log-likelihood (D2 8x4, K=16/64).
- D2 8x4 closes 0.26 at K=64 (−3 dB), 0.25 with a second seed.
- UMi-28 8x4 yaw-only closes 0.68 at K=64 (0.69 with seed 2).

**Setup**
- Uplink, narrowband: paths summed at t=0.
- BS ULA with Nr elements, UE ULA with Nt=4, half-wavelength spacing, single V polarisation, omni patterns.
- UE orientation: yaw uniform on [−π, π), pitch and roll 0. BS uses the `gen_single_sector_topology` default (sector-centred yaw, scenario downtilt).
- Outdoor UEs only; RMa has in_car=False. Pathloss and shadowing off.
- Normalised so E‖H‖²=Nr·Nt on the train set; h = vec column-major.
- Sizes: 40,000 train (36,000 fit + 4,000 val early stop, n_iter=200, patience 40), 1,000 test, R=400 conditional draws.
- Pilots: Tp=Nt, nu=σ²/Nt.
- For LO, the ray sampler output is captured and replayed, so only ray phases are redrawn.

**Primary metric** (closed fraction for K=16/64/256; gap = K1−LO in NMSE):

| config | −3 dB gap | closed 16/64/256 (−3 dB) | +3 dB gap | closed 16/64/256 (+3 dB) |
|---|---|---|---|---|
| D2 8x4 (s1 / s2) | 0.249 / 0.249 | 0.19/0.26/0.29 · 0.20/0.25/0.29 | 0.089 | 0.18/0.25/0.24 |
| D2 16x4 | 0.273 | 0.21/0.26/0.24 | 0.094 | 0.21/0.25/0.21 |
| D2 32x4 | 0.285 | 0.21/0.24/0.23 | 0.097 | 0.22/0.20/0.24 |
| UMi28 mix 8x4 (s1 / s2) | 0.173 / 0.178 | 0.57/0.68/0.71 · 0.58/0.69/0.71 | 0.055 | 0.54/0.63/0.64 |
| UMi28 mix, LoS part / NLoS part | 0.259 / 0.117 | 0.55/0.68/0.74 · 0.61/0.68/0.66 | – | – |
| UMi100 mix 8x4 | 0.178 | 0.59/0.70/0.72 | 0.056 | 0.57/0.66/0.66 |
| UMi100 LoS-only 8x4 | 0.250 | 0.59/0.72/0.77 | 0.081 | 0.53/0.62/0.64 |
| UMa28 LoS-only 8x4 | 0.254 | 0.63/0.73/0.78 | 0.082 | 0.57/0.65/0.68 |
| RMa 3.5 GHz LoS-only 8x4 | 0.260 | 0.60/0.68/0.73 | 0.086 | 0.55/0.62/0.65 |
| RMa 3.5 GHz mix 8x4 | 0.231 | 0.58/0.66/0.68 | 0.078 | 0.58/0.66/0.66 |
| MIX3 (UMi28+UMa28+RMa, 1/3 each) 8x4 | 0.195 | 0.58/0.66/0.66 | 0.065 | 0.57/0.65/0.65 |
| UMi28 mix + blockage A 8x4 | 0.189 | 0.61/0.69/0.71 | 0.061 | 0.56/0.64/0.65 |
| UMi28 LoS + blockage A 8x4 | 0.250 | 0.65/0.74/0.78 | 0.080 | 0.56/0.65/0.67 |
| UMi100 mix + blockage A 8x4 | 0.192 | 0.62/0.71/0.72 | 0.062 | 0.59/0.68/0.68 |
| UMi28 mix 16x4 | 0.186 | 0.58/0.68/0.69 | 0.060 | 0.54/0.61/0.59 |
| UMi28 mix + blockage A 16x4 | 0.202 | 0.60/0.69/0.68 | 0.066 | 0.56/0.62/0.61 |
| UMi100 LoS 16x4 | 0.260 | 0.62/0.72/0.75 | 0.085 | 0.54/0.61/0.58 |
| RMa LoS 16x4 | 0.268 | 0.61/0.69/0.71 | 0.090 | 0.56/0.61/0.62 |
| MIX3 16x4 | 0.215 | 0.58/0.65/0.65 | 0.071 | 0.57/0.61/0.62 |
| UMi28 mix 32x4 | 0.195 | 0.58/0.62/0.61 | 0.064 | 0.54/0.54/0.53 |
| UMi100 LoS 32x4 | 0.267 | 0.62/0.71/0.73 | 0.087 | 0.54/0.55/0.50 |
| CDL-C control 8x4 | −0.002 | undefined | −0.001 | undefined |

The CDL-C control has no gap: K1, LO and GMM all sit at about 0.174 at −3 dB, so there is nothing for any prior to gain. Its LO uses independent draws, because the random coupling in CDL is redrawn on every call.

**Why it happens (extra diagnostic, beyond the brief)**
- **Low rank is not the reason.** 38.901 LoS-only configs have a lower conditional effective rank (1.3–1.5) than D2 (3.2). Their absolute LO gap is the same as D2's (about 0.25), yet the GMM closes about 0.7 of it.
- **The dimension of the latent is the difference.** I added an "LSP oracle": topology and LSPs fixed, all rays (cluster powers and angles) redrawn.
  - In 38.901 it alone closes 0.92/0.89 (UMi28 8x4, −3/+3 dB), 0.96/0.92 (UMi100 LoS), 0.93/0.90 (RMa LoS), 0.88/0.87 (MIX3) and 0.90/0.87 (UMi28 16x4).
  - So about 90% of the per-drop covariance is set by a few-dimensional latent (LoS state, LoS directions, spreads, K-factor, UE yaw), which K=64 can cover. 38.901 cluster angles are close to deterministic given those LSPs: offsets scale with √(−ln Pₙ), with a random sign and σ/7 jitter.
  - The D2 counterpart (L and the strongest path's angles fixed, everything else redrawn) closes only 0.22/0.09 at 8x4, because D2's latent has 2L independent continuous angles.

**Secondary metrics** (8x4 unless stated)

| config | LoS fraction | clusters / paths per sample | ens. eff. rank | cond. eff. rank | beamspace top-4 / top-8 | outage at −3 dB | median MI (bit) |
|---|---|---|---|---|---|---|---|
| D2 | – | 5.4 paths | 28.5 | 3.17 | 0.67 / 0.84 | 0.003 | 6.9 |
| UMi28 mix | 0.40 | 15.7 | 27.9 | 6.6 | 0.70 / 0.85 | 0.015 | 6.05 |
| UMi100 mix | 0.40 | 15.7 | 27.6 | 6.2 | 0.71 / 0.86 | 0.018 | 5.93 |
| UMi100 LoS | 1 | 11.1 | 26.0 | 1.37 | 0.83 / 0.92 | 0.029 | 4.86 |
| UMa28 LoS | 1 | 11.6 | 26.0 | 1.29 | 0.84 / 0.93 | 0.026 | 4.90 |
| RMa LoS | 1 | 9.5 | 25.4 | 1.38 | 0.84 / 0.93 | 0.092 | 4.86 |
| RMa mix | 0.22 | 9.9 | 26.6 | 3.24 | 0.78 / 0.90 | 0.119 | 5.36 |
| MIX3 | 0.27 | 14.5 | 27.5 | 4.9 | 0.73 / 0.87 | 0.061 | 5.70 |
| CDL-C | – | – | 7.7 | 7.6 | 0.61 / 0.80 | 0.001 | 7.33 |

- **Blockage A** gives high outage: 0.25 (UMi28 mix), 0.26 (UMi100 mix), 0.40 (UMi28 LoS), 0.17 (UMi28 mix 16x4). Those regimes are prior-insensitive.
- **Other array sizes:** 16x4 and 32x4 outage is about 0.00 for UMi and D2. Conditional effective rank for UMi28 is 10.9 at 16x4 and 18.4 at 32x4; D2 stays at 3.3.
- **Beamspace sparsity** does not separate the two families: the 38.901 LoS configs are sparser than D2 and still GMM-friendly.
- **Leakage:** the fraction of test samples with nearest-neighbour normalised distance < 0.1 is 0.000 in every config (0.001 for UMi28+blockage i.i.d.), both i.i.d. and under the spatial-block split (azimuth halves).
  - Median NN distance, i.i.d.: 0.38–0.42 for LoS-only, 0.65–0.74 for the mixes, 0.82 for D2.
  - Under the block split: 0.77–1.13.
  - Each 38.901 drop is an independent topology with no cross-drop spatial consistency, so these configs are i.i.d. by construction.
- **Throughput** on one GPU: 0.004–0.04 ms per sample, so 1.6e5 + 5,000 + 7×2,560 = 182,920 samples take under 0.15 min in every config.

**Caveats**
- At K=256 (and at K=64 for 32x4) the EM runs out of data per component. There are thousands of re-seeds and the tolerance stop fires early (about 20–70 iterations), exactly as the CPU code behaves. K=64 at 8x4 and 16x4 is the clean number.
- Per-drop power variation comes from K-factor, O2I and blockage only, because normalisation is ensemble-wide.
- Blockage A uses landscape self-blocking and 4 non-self blockers.
- The LSP-oracle and D2 strongest-path oracle are diagnostics I added beyond the brief.
- The NMSE standard error at 1,000 test samples is roughly ±0.01–0.02 in the closed fraction (seed 1 vs seed 2 differ by ≤0.03).

All files are in `/tmp/claude-1005/-home-HTJ-t2/47f1f727-1d40-4c8f-a798-01f8d9d886c3/scratchpad/tb2/sionna_phy/`:
- `tb.py` – generators, GPU EM port, metrics
- `chk_em.py` – GPU-vs-CPU EM check
- `d2_coarse.py` – D2 strongest-path oracle
- `table.py` – builds the results table
- `results/*.json` – 28 files, one per config and seed; `*_lspo.json` are the LSP-oracle runs
- `logs/*.log` – run logs