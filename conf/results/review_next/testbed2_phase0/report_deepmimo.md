DeepMIMO v4 works without the numpy downgrade, but none of the DeepMIMO outdoor 28 GHz scenarios is a favourable second testbed. The EM-GMM closes 0.63–0.80 of the K1→LO gap on every one I tested, which is the same as UMi (0.68) or friendlier to the GMM. D2, run with the same code, closes 0.26. My recommendation is not to pre-register DeepMIMO under these conventions.

**Install.** `pip install --no-deps --target .../tb2/deepmimo/site deepmimo` gave v4.0.5. It runs on the torch env's numpy 2.5.2, scipy 1.18.1, matplotlib, tqdm and requests, even though its metadata asks for numpy<2.3. Nothing extra was installed and nothing went into the torch or base envs. My own array code matches DeepMIMO's `compute_channels` exactly (|corr| = 1.000000 on 300 users, UE yaw 0° and 37°).
- `dm.load()` on a scenario that isn't downloaded yet waits for keyboard input and crashes in a script, so call `dm.download()` first.
- **Download quota:** deepmimo.net has a daily download limit, and asking the API for a file's size spends quota. I used about 250 MB of downloads. About 7 MB was left today, so `o1_28`, `o1b_28` and `o1_60` could not be downloaded or measured.

**Licence** (from deepmimo.net/license): "In order to use the DeepMIMO dataset/scripts or any (modified) part of them, please cite: 1. the DeepMIMO paper (Alkhateeb, ITA 2019, arXiv:1902.06435); 2. the Remcom Wireless InSite ray-tracer (Sionna for Sionna scenarios); 3. the scenario's associated publication, if one is listed." The page states no separate data licence. The pip package is inconsistent: its LICENSE file is Apache-2.0 but its metadata says GPL-2.0-or-later. All scenarios used are Wireless InSite v3.3.

**Conventions I registered** (stated here so they can be disclosed):
- BS: horizontal ULA, half-wavelength, omni, single V polarisation, on the local y axis. BS yaw is set so boresight points at the centroid of that BS's users (a sector facing its users). Downtilt has no effect for a horizontal ULA with omni elements.
- UE: 4-element ULA, yaw-only random orientation U[−180°, 180°), no tilt or slant.
- Path gains: at the carrier, per-user path powers normalised to sum to 1, ensemble normalised from the train stream, users with no path dropped.
- Split: "block" means 20 m position tiles, 15% of them held out for test.
- Oracle: the LO uses the exact closed-form covariance sum_l p_l v_l v_l^H. On the first 500 test samples it matches the script's Monte-Carlo LO (R=400) to 3 decimals in every case.
- GMM fits: GPU port of `fit_gmm_em`, identical to the CPU version (covariance relative error 7e-13, same iterations), trained on 36000 samples with 4000 for validation. The test set is 2000 samples, with 95% bootstrap intervals.

**Primary metric: GMM headroom closed, 8x4, all test samples (lower is more favourable to the diffusion prior)**

| Case | Split | −3 dB K16/64/256 | +3 dB K16/64/256 | K1−LO gap (−3 dB) | NLOS K64 (−3/+3 dB) |
|---|---|---|---|---|---|
| D2-S2 (calibration) | iid | 0.19 / **0.26** [0.25, 0.27] / 0.29 | 0.19 / 0.25 / 0.24 | 0.250 | – |
| boston5g_28 (1 BS, 105,842 users) | iid | 0.65 / **0.75** / 0.80 | 0.63 / 0.73 / 0.78 | 0.258 | 0.77 / 0.76 |
| boston5g_28 | block | 0.67 / **0.77** / 0.80 | 0.64 / 0.74 / 0.78 | 0.262 | 0.77 / 0.75 |
| boston5g_28, DeepMIMO default BS rotation | iid | 0.70 / 0.79 / 0.83 | 0.70 / 0.79 / 0.83 | 0.220 | 0.79 / 0.79 |
| city New York + Miami (6 BS, 130,969 pairs) | iid | 0.58 / **0.69** / 0.73 | 0.56 / 0.67 / 0.70 | 0.272 | 0.67 / 0.65 |
| same | block | 0.58 / 0.69 / 0.73 | 0.58 / 0.69 / 0.71 | 0.267 | 0.68 / 0.67 |
| 6 cities: NY, MIA, LA, CHI, HOU, PHX (18 BS, 342,597 pairs) | block | 0.56 / **0.68** / 0.71 | 0.52 / 0.63 / 0.66 | 0.274 | 0.64 / 0.58 |

At 16x4 the picture is the same: D2 0.26 / 0.25, boston5g 0.76 / 0.74, two-city mix 0.70 / 0.68 (K64, −3/+3 dB). The GMM's share of the gap does not depend on Nr or on the split.

**Why RT loses the advantage.** In these scenarios path angles and powers are functions of UE position and yaw, so the family of conditional covariances is only about 3-dimensional, and 64–256 components cover it. D2 draws each path's angles independently, which makes that family about 12-dimensional. TwoNN intrinsic-dimension estimates (20,000 samples, 8x4): D2 12.2, boston5g 2.7, 6-city mix 3.4. Sparsity is not what separates them: DeepMIMO is actually sparser than D2. Adding more sites adds modes, not dimensions, so it moved K64 only from 0.75 to 0.68. NLOS is the least GMM-friendly subset, but even 6-city NLOS at +3 dB (0.58) is far above D2.

**Secondary metrics (8x4)**

| Metric | D2 | boston5g (iid / block) | 6-city (block) |
|---|---|---|---|
| LOS fraction | 0 | 0.38 | 0.28 |
| Paths per user, median | 3–8 by design | 4 | 22 (4 within 20 dB of strongest) |
| Effective paths 1/Σp², median | 3.46 | 1.87 | 1.72 |
| Ensemble effective rank | 28.5/32 | 20.7/32 (16.5 with default rotation) | 25.1/32 |
| Beamspace top-4 / top-8 energy | 0.67 / 0.84 | 0.84 / 0.93 | 0.84 / 0.93 |
| Outage P(MI<4 bit) at −3 dB | 0.003 | 0.25 / 0.30 | 0.24 |

So 20–30% of DeepMIMO blocks at 8x4 are in outage at −3 dB, where the prior barely matters (8% for boston5g and 4% for the two-city mix at 16x4).

**Leakage (the D6 concern).** Numbers are the fraction of test samples whose nearest training sample is within a normalised distance of 0.1. The grids are dense: 0.37 m spacing in boston5g, 1 m in the cities.

| Case | Channel, random yaw | Channel, fixed yaw | Latent covariance |
|---|---|---|---|
| D2 (for reference) | 0.00 (median distance 0.60) | – | – |
| boston5g iid | 0.48 | 0.70 | 0.98 |
| boston5g block | 0.38 | 0.64 | 0.93 |
| 6-city block | 0.41 | 0.45 | 0.80 |

The 20 m block split barely reduces it, because the low-dimensional geometry means a near-twin exists elsewhere in the map. Random yaw only partly hides this.

**Data volume and speed.** Building channels takes about 3 s per 1.83e5 samples at 8x4 (6 s at 16x4), plus 3–10 s to load. boston5g has only 105,842 user pairs (89,782 in the block-split train pool), which is fewer than 1.6e5 train + 5000 val + 7×2560 test. The 6-city mix has enough: 291k train pool and 51k test pool.

**Not tested:** O1 (quota). It is the same Wireless InSite street geometry with reflections only and 18 BS, so I would expect it to behave like the city mixes. An RT testbed would only become favourable if each sample's geometry were independently randomised (for example, scene or scatterer placement redrawn per sample) to raise the latent dimension. That would need its own mechanism-based pre-registration.

Everything is in `/tmp/claude-1005/-home-HTJ-t2/47f1f727-1d40-4c8f-a798-01f8d9d886c3/scratchpad/tb2/deepmimo/`:
- run.py
- gmm_t.py
- dmimo.py
- idim.py
- freegpu.sh
- logs/*.log
- res_*.json
- deepmimo_scenarios/ (about 3.1 GB)