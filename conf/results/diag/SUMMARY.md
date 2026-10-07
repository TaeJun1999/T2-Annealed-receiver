# M-ours-dscore BLER collapse on D2 — reconciled diagnosis

date: 2026-09-21 15:00 KST | testbed D2 (sparse specular, prior S2) | cell C2 (8x4, T=16, Tp=4)
checkpoint under diagnosis: `ckpt/d2sx_N10000_a1.pt` (frozen; sha256 d94aa99bdc5689067f90895b28d6394e7c61a296ed58ada3f041eb4ad8fdf01a)
hp: `{'arch':'dit','param':'vp','domain':'angle','lr':0.002238046051591068,'ema':0.999,'batch':256,'emb':256,'width':64,'depth':6,'heads':8,'patch':1}` (= HPO trial 386)

**Status of this document.** Diagnostic only. Nothing was retrained, no hyperparameter tuned, no gate
threshold changed. No pre-registered file (`results/tables_D2.txt`, `results/tables_D1.txt`,
`results/gate_D1.txt`, `LADDER.md`) and nothing under `Demo/` or `docs/` was modified. **M-ours-dscore
remains BLOCKED in the pre-registered tables regardless of everything below.**

---

## 1. The question

Three diagnostics on the same frozen checkpoint disagree:

| # | diagnostic | result | source |
|---|---|---|---|
| 1 | GB' — one-shot denoising NMSE vs the GMM prior, frozen 20-point sigma grid | learned prior BEATS the GMM at every sigma, ratio diff/gmm 0.5204 -> 0.8781, worst_excess -0.1219 | `results/gate_D2.txt` |
| 2 | Hyvarinen score-matching, no ground truth needed | learned score 3-4x more accurate; k=0 (sigma 3.3062e-2): GMM -3198.69 +- 81.18 vs diffusion -14016.64 +- 118.96 (~91 s.e.) | `results/hyvarinen_D2_n1e4.npz` |
| 3 | BLER in the full 16-iteration RouteA receiver, cell C2 | COLLAPSE: BLER 0.805/0.898/0.883/0.795/0.686/0.523/0.312 at -3..15 dB, NMSE non-monotone and **> 1** at 6 dB (1.110) | `results/tables_D2_supp.txt` |

NMSE > 1 means the channel estimate is worse than the all-zero estimator: a diverging iteration, not
a merely inaccurate prior.

---

## 2. The five hypotheses and their outcomes

| H | hypothesis | verdict | decided by |
|---|---|---|---|
| H1 | The learned denoiser's Jacobian is not a valid covariance, so the D-14 matrix site is a mismatched (precision, mean) pair and the loop diverges | **CAUSAL** (confirmed by do()-intervention in both directions) | §3.1, §3.6 |
| H2 | The loop's nu trajectory leaves the trained/gated sigma range | **REFUTED** | §3.2 |
| H3 | Normalisation / scale / vec-order mismatch between training and inference | **REFUTED** | §3.3 |
| H4 | The score prior is wired into the EP loop differently, and the wiring — not the prior — is the cause | **CONTRIBUTING, not sufficient** (wiring alone exonerated; wiring is a necessary co-factor) | §3.4, §3.7 |
| H5 | The supplementary BLER run evaluated a different checkpoint/configuration than believed | **REFUTED** (one documentation defect found, no conclusion moves) | §3.5 |

---

## 3. What was measured

### 3.1 H1 — Jacobian validity (CAUSAL)

For a true posterior-mean denoiser under real Gaussian noise, `Jr = dm_real/dx = Cov_real(h|q)/sigma^2`
is symmetric PSD, and the complex Wirtinger `J` the receiver consumes satisfies `nu*Herm(J) = Cov[h|q] >= 0`.

Measured over the frozen 20-point D2 sigma grid, 64 held-out samples per point, CPU/float64:

- diffusion: `||Jr - Jr^T||_F / ||Jr||_F = 0.177-0.288` at every grid point; `frac lambda_min(sym Jr) < 0 = 0.547-1.000`
  (= 1.000 for k=0..11, i.e. nu 2.2e-3 to 9.3e-2); most negative lambda_min = -0.322; on the complex Hermitian J
  the receiver actually consumes, `frac lambda_min < 0 = 0.172-1.000`, min -0.172, `frac lambda_max > 1 = 0.781-1.000` (max 2.74).
- exact GMM reference (b* = kron K=512, same machinery): asymmetry 2.2e-16 to 2.3e-15, `lambda_min(sym Jr) >= +6.5e-4`,
  `frac < 0 = 0.000` at **every** one of the 20 points.

Isolation at the receiver's operating noise level (k=6, nu=1.6932e-2; C2 median nu_q = 1.837e-2 at 6 dB),
n=256, replaying `Demo/t2_gmm.py:112-122` verbatim: **255/256** diffusion samples give an INDEFINITE
`SigH = nu*Herm(J)`; belief-mean shift `||mu-hH||^2/||hH||^2` median 1.87, p90 59.4, max 1.53e6;
`||eta||/||q/nu|| = 2.56`. GMM: 0/256 indefinite (133 clip on lambda_max>1 with shift median 3.5e-4, max 9.3e-3;
123 need no clip). **The lambda_max clip is benign; the negative eigenvalue is what blows up.**

Receiver-side, read out of the pre-registered raw npz only (`raw_supp/`, 640 trials/SNR, nothing re-run):
M-ours-dscore clip fraction 0.9904/0.9979/1.0000/1.0000/1.0000/1.0000/1.0000 at -3..15 dB; per-iteration
median NMSE at 6 dB = 5.10, 0.75, 0.94, 1.15, 1.11, 1.37, 1.56, 1.50, 1.64, 1.23, 1.20, 1.10, 1.06, 1.01,
1.11, 1.11 (90th pct 1.1e2 down to 3.6e1, never below 27). M-ours-bstar and M-ours-gmm32, identical except
Module H, record belief-mean shift 1.38e-4..5.45e-3 and 7.1e-5..3.4e-3. (The dscore shift column
4.28e3..1.11e5 is a **marker, not a dose** — see §4, correction [C2].)

commands
```
export OMP_NUM_THREADS=4 MKL_NUM_THREADS=4
cd /home/HTJ/t2/conf/code && ~/miniforge3/envs/torch/bin/python jacobian_psd.py --n 64 2>&1 | tee /home/HTJ/t2/conf/logs/jacobian_psd_D2.log
cd /home/HTJ/t2/conf/code && ~/miniforge3/envs/torch/bin/python jacobian_psd_split.py 2>&1 | tee /home/HTJ/t2/conf/results/diag/jacobian-psd_split_D2_k6.txt
```
artifacts `results/diag/jacobian-psd_D2.txt`, `jacobian-psd_D2.npz`, `jacobian-psd_split_D2_k6.txt`,
`jacobian-psd_receiver_clip_C2.txt`; code `code/jacobian_psd.py`, `code/jacobian_psd_split.py`;
log `logs/jacobian_psd_D2.log`.

### 3.2 H2 — sigma-range extrapolation (REFUTED)

Trained range == gated range == frozen measured grid, exactly: `sigma_t` log-uniform on
[3.306220e-02, 8.451555e-01] (`score.py:665,775-777`; `logs/train_d2sx_N10000_a1.log:5`).
Instrumented run (cell C2, n=12 trials x 16 iterations x 6 SNRs, four arms on identical (H,u,perm,Y);
wrapping `prior.denoise*` confirms `log["nu_q"]` IS the queried nu, max |queried - logged| = 0.0):

| SNR | queries out of [s_lo,s_hi] (of 192) | frac trials NMSE>1 at **iteration 1** |
|---|---|---|
| -3 dB | 0/192 | 42% |
| 0 dB | 0/192 | 58% |
| +3 dB | 0/192 | 75% |
| +6 dB | 0/192 | 83% |
| +9 dB | 0/192 | 75% |
| +15 dB | 73/192 (38%, all below the floor; min/lo = 0.970) | 33% |

At -3..+9 dB coverage is 100% and the estimate is already diverged, so extrapolation cannot be the cause.
At +15 dB, where the only excursion occurs, NMSE>1 came strictly FIRST in 5 of the 6 trials where both
events occur. Controls through the same interface: `ctrl-bstar-sIF` (GMM through the score interface) goes
out of range at +15 dB too (14.6%) with NMSE>1 in 0 of 192x6 iterations; `ctrl-G-sIF` never leaves the grid;
both reach BLER 0.000 from +3 dB up. Population cross-check on the pre-registered raw (640/point):
M-ours-dscore median NMSE at **iteration 1** = 0.22/0.93/2.20/5.10/2.91/1.85/1.13 at -3..+15 dB vs
M-ours-bstar 0.236/0.145/0.083/0.046/0.025/0.013/0.0068.

command
```
cd /home/HTJ/t2/conf && OMP_NUM_THREADS=4 ~/miniforge3/envs/torch/bin/python code/diag_sigma_coverage.py --cell C2 --snr -3 0 3 6 9 15 --n 12 2>&1 | tee logs/diag_sigma_coverage.log
```
artifacts `results/diag/sigma-coverage_D2_C2_n12.txt`, `sigma-coverage_D2_C2_n12.npz`;
code `code/diag_sigma_coverage.py`; log `logs/diag_sigma_coverage.log`.

### 3.3 H3 — normalisation / scale / vec order (REFUTED)

Four candidate mismatches, none exists.
(a) channel power `E||h||^2/N` = 0.999400 (training set, n=10000) vs 0.997442 (receiver path, n=2000), ratio 0.998.
(b) sigma convention: sweeping the sigma argument over `c*sqrt(nu/2)`, argmin c = 1.000 at 5 of 7 nu and 0.85
at the other two (c=1.0 within 0.007% and 0.5% of the minimum); `c=sqrt(2)` costs +11..+21%, `c=0.707` +15..+343%.
No factor of sqrt(2). The GMM reference sweeps identically.
(c) vec order: `max|sample_vecs - vec(sample,'F')| = 0.000e+00` (row-major reading of the same draw differs by 1.775);
forcing the row-major permutation costs 1.43x-1.79x NMSE.
(d) denoising in the receiver's own convention, at the seven measured C2 operating nu_q (2.318e-3 .. 4.988e-1, n=128):
diffusion NMSE 1.190e-3 .. 1.687e-1 vs GMM b* 2.051e-3 .. 2.363e-1 — **1.4x-1.7x better at every nu**, matching GB'.
Live loop tap (6 dB, 8 trials): at iteration 1 `|q|^2/N = 1.0681` vs expected `1+nu_q = 1.0628`, ratio 1.005.
Control: the GMM b* pushed through the IDENTICAL D-13 + D-14 interface (`X-gmm-score`) converges normally
(median NMSE 1.583e-2, BLER 0.000 at 6 dB) while M-ours-dscore on the same trials oscillates 5.2e-1 .. 6.6e0, BLER 1.000.
Same measurement pass also recorded: `SigH = nu*J` from the diffusion has a negative eigenvalue in
91.7%/99.0%/92.7%/28.1% of draws at nu = 2.318e-3/1.837e-2/7.050e-2/4.988e-1 (GMM 0.000 everywhere), and
`tr(nu J)/N` tracks the diffusion's own realised per-entry MSE to within 0.3-5.3% — **a shape defect, not a scale defect**.

command
```
cd /home/HTJ/t2/conf && export OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 && ~/miniforge3/envs/torch/bin/python code/diag_scale.py && ~/miniforge3/envs/torch/bin/python code/diag_scale2.py
```
artifacts `results/diag/scale-mismatch_D2_C2.txt`, `scale-mismatch_D2_C2.npz`,
`scale-mismatch_D2_jacobian.txt`, `scale-mismatch_D2_jacobian.npz`.

### 3.4 H4 — EP wiring (CONTRIBUTING; wiring alone exonerated)

Harness validated first: the diagnostic arms reproduce the pre-registered ones bit-exactly on 40 paired
trials (`dscore|scorew == M-ours-dscore`, `gmmB|epsite == M-ours-bstar`, blk_err identical, max|dNMSE| = 0.000e+00).

Factorial, n=128 paired trials, BLER@16 at -3/0/+6 dB, NMSE_H median@16:

| arm | denoiser | wiring | BLER@16 (-3/0/+6) | NMSE med@16 |
|---|---|---|---|---|
| gmmB\|epsite (= M-ours-bstar) | GMM | GMM | 0.320 / 0.117 / 0.016 | 0.1081 / 0.0536 / 0.0156 |
| gmmB\|scorew (hybrid) | GMM | SCORE | 0.297 / 0.109 / 0.023 | 0.1062 / 0.0532 / 0.0156 |
| dscore\|scorew (= M-ours-dscore) | learned | SCORE | 0.852 / 0.914 / 0.773 | 0.2773 / 1.3474 / 1.2851 |
| dscore\|belsc (D-14 site removed) | learned | SCORE, hsite='scalar' | 0.203 / 0.055 / 0.008 | 0.0605 / 0.0280 / 0.0078 |
| dscore\|sitesc (v0 SC-VAMP scalar site) | learned | scalar site | 0.203 / 0.055 / 0.000 | 0.0622 / 0.0288 / 0.0079 |
| gauss\|sitesc (= R2-ours-G) | Gaussian | scalar site | 0.344 / 0.117 / 0.031 | 0.1469 / 0.0678 / 0.0182 |

The hybrid does not collapse -> the score wiring as a whole is exonerated as a standalone cause. The same
frozen checkpoint with only `hsite` flipped 'matrix' -> 'scalar' goes from BLER 0.914 to 0.055 at 0 dB.
NMSE mean@16 at 0 dB: `dscore|scorew` 16673 with 53.9% of blocks above NMSE 1; every other arm 0.03-0.08
with 0.0% above 1. Along the receiver trajectory (0 dB, iter 2, medians): `dscore` min eig(Lambda) = -2.28e3
with 7.0/32 eigenvalues below `lam_min`, vs `gmmB` -4.37e-1 with 0.5/32. Held-out min eig of Herm(J):
nu=2.5e-1 dscore med +5.0e-4 / worst -9.4e-2 / 50% not PSD; nu=8.0e-2 med -3.4e-2 / 90.6% not PSD;
nu=3.0e-2 med -7.5e-2 / 100% not PSD; GMM 0% not PSD at all three. `frac_out_of_grid = 0.0`.
Also verified by inspection: **RouteA has no divergence guard on the Module-H path** — no NMSE test, no
`diverged` flag, no state freeze (cf. `code/bigamp.py` `DIVERGE_NMSE = 10.0`, `code/scvamp.py` diverged flag).
The `nu_max=1e4` guard sits inside `if use_scalar and (scal == 'site' or nu_sw is not None)` and is never
executed for the score arm. `runner.run_task` therefore writes NaN in `<arm>|diverged` for every RouteA arm.

commands
```
cd /home/HTJ/t2/conf && export OMP_NUM_THREADS=1
for s in -3 0 6; do ~/miniforge3/envs/torch/bin/python code/diag_ep_site.py --cell C2 --snrs $s --n 128 \
  --ckpt /home/HTJ/t2/conf/ckpt/d2sx_N10000_a1.pt > logs/diag_ep_site_snr${s}.log 2>&1 & done; wait
~/miniforge3/envs/torch/bin/python code/diag_ep_probe.py --snr 0 --n 8
```
artifacts `results/diag/ep-site-integration_summary.txt`, `ep-site-integration_D2_C2_snr{-3,+0,+6}_n128.npz`,
`ep-site-integration_probe_D2_C2_snr+0_n8.npz`, `ep-site-integration_jacobian_psd_D2.npz`;
code `code/diag_ep_site.py`, `code/diag_ep_probe.py`; logs `logs/diag_ep_site_snr{-3,0,6}.log`.

### 3.5 H5 — checkpoint / configuration provenance (REFUTED)

All 112 `raw_supp/` point files record `meta|dscore_ckpt = 'ckpt/d2sx_N10000_a1.pt'` and
`meta|fit_sec|M-ours-dscore = 672.41867852`, equal to that checkpoint's internal `wall_sec = 672.41867852211`
— unique among the 7 D2 checkpoints (B3 443.61, a2 556.85, a3 649.61, N2500 178.46, N4e4 3982.23, N1.6e5 4414.70).
Replaying `score.load_prior("D2","S2",8,4,ckpt=...)` reproduces `meta|dscore_status` character-for-character.
Geometry matches (`testbed=D2 prior=S2 Nr=8 Nt=4 split_hash=5340d785c2ad3eb6`; `CELLS["C2"]` = Nr8 Nt4 T16 Tp4 S2).
The `gmm_fits_D2_supp` symlink is harmless: over 10528 (file,key) pairs across 112 files the only differing
keys are two provenance STRINGS; everything else is bitwise identical, including `meta|em_sec`,
`meta|ll_val|kron`, `meta|bstar`, `meta|kron_K`. Demo/ hashes identical across `gate_D2.txt`,
`tables_D2.txt`, `tables_D2_supp.txt`; `git diff 5e2e77a..85f6339` over `conf/code/{score,arms,common,runner}.py`
and `Demo/` is empty.

One real defect found, documentation only: **the GB' table in `results/gate_D2.txt` was computed with
`ckpt/B3_dscore_D2.pt`, a sibling seed, not with the evaluated `d2sx_N10000_a1.pt`** (recomputed GB' vs the
recorded `nmse_diff` column: B3 max rel dev 3.7e-06 = match; a1 1.2e-02; a2 1.3e-02; a3 2.1e-02; N2500 1.8e-01;
N4e4 1.5e-01). The claim survives: measured directly for the checkpoint actually run,
`d2sx_N10000_a1` gives `worst_excess = -0.122702`, ratio 0.5157 -> 0.8773 (gate_D2.txt records -0.121905,
0.5204 -> 0.8781), and `results/d2_gbprime.csv` independently has N=1e4 a1 `worst_excess = -0.126715` at n_eval=4096.
Hyvarinen reproduced exactly: recomputed SM = -14016.6442 vs stored -14016.6442, rel dev 0.000e+00.

artifacts `results/diag/checkpoint-provenance_SUMMARY.md`, `checkpoint-provenance_gbprime.json`,
`checkpoint-provenance_hyvarinen.json`, `checkpoint-provenance_loadpath.json`, `checkpoint-provenance_table_compare.json`;
code `code/diag_prov_gbprime.py`, `code/diag_prov_hyv.py`; logs `logs/diag_prov_gbprime.log`, `logs/diag_prov_hyv.log`.

### 3.6 Adversarial test of H1 — receiver-level do()-interventions

n=64 paired trials per point, 16 iterations, `prior.denoise` (D-13, `alphaH = tr(J)/N`) delegated UNTOUCHED
so only the Jacobian entering `_matrix_site` changes:

| arm | intervention on Herm(J) | BLER@16 0 dB | 6 dB | NMSE med 0 dB | frac NMSE>1 0 dB |
|---|---|---|---|---|---|
| dscore\|eta | none (= M-ours-dscore) | 0.922 (.066) | 0.719 (.110) | 1.3284 | 0.531 |
| dscore\|psd1e-2 | eig clipped into [1e-2, 1] | **0.031 (.043)** | **0.000** | 0.0241 | 0.000 |
| dscore\|mean | none; `clip='mean'` instead of `'eta'` | **0.047 (.052)** | **0.000** | 0.0241 | 0.000 |
| dscore\|abs1e-2 | \|eig\| floored at 1e-2, **sign kept** | 0.922 (.066) | 0.578 (.121) | 0.5596 | 0.375 |
| dscore\|belsc | D-14 site removed entirely | 0.047 (.052) | 0.016 (.030) | 0.0241 | 0.000 |
| gmmB\|eta | none (exact GMM, score wiring) | 0.109 (.076) | 0.031 (.043) | 0.0519 | 0.000 |
| gmmB\|flip4 | sign of 4 smallest \|eig\| flipped | 0.141 (.085) | 0.016 (.030) | 0.0680 | 0.000 |
| gmmB\|tiny4 | 4 smallest \|eig\| set to +1e-4 (PD) | 0.109 (.076) | 0.031 (.043) | 0.0526 | 0.000 |
| gmmB\|epsite | none (= M-ours-bstar) | 0.125 (.081) | 0.016 (.030) | 0.0533 | 0.000 |
| gauss\|sitesc | none (= R2-ours-G) | 0.078 (.066) | 0.016 (.030) | 0.0668 | 0.000 |

94.8% (0 dB) / 98.6% (6 dB) of intercepted Jacobians were indefinite before repair.
Remove the negative eigenvalues -> collapse gone. Keep the sign and remove only the near-singularity
(`abs1e-2`) -> no recovery. Inject near-singularity into the healthy GMM arm while keeping it PD (`tiny4`)
-> no damage. **Ill-conditioning is not the cause; the sign is.** Independent re-derivation at k=6
(nu=1.6932e-2, n=128, seed 987654321, NOT `score.SEED_GATE`): diffusion `frac lmin<0 = 1.000`, med lmin
-6.558e-2, med |lmin| 2.882e-3, med cond 391, site shift median 1.857; GMM `frac lmin<0 = 0.000`,
med lmin +9.941e-2, shift 8.969e-10.

commands
```
export OMP_NUM_THREADS=4 MKL_NUM_THREADS=4
cd /home/HTJ/t2/conf/code && ~/miniforge3/envs/torch/bin/python -u diag_psd_cf.py --cell C2 --snrs 0 6 --n 64 --ckpt /home/HTJ/t2/conf/ckpt/d2sx_N10000_a1.pt > /home/HTJ/t2/conf/logs/jacpsd_counterfactual_D2.log 2>&1
cd /home/HTJ/t2/conf/code && OMP_NUM_THREADS=2 ~/miniforge3/envs/torch/bin/python -u diag_psd_align.py 2>&1 | tee /home/HTJ/t2/conf/results/diag/jacpsd-alignment_D2_k6.txt
```
artifacts `results/diag/jacpsd-counterfactual_SUMMARY.txt`,
`jacpsd-counterfactual_D2_C2_snr{+0,+6}_n64.npz`, `jacpsd-alignment_D2_k6.txt`;
code `code/diag_psd_cf.py`, `code/diag_psd_align.py`; log `logs/jacpsd_counterfactual_D2.log`.

### 3.7 Adversarial test of H4 — single-factor Jacobian swap

The H4 factorial swapped the WHOLE denoiser (mean AND Jacobian). Moving one factor at a time inside the
frozen score wiring (n=64 paired trials; harness bit-exact against the published npz: `d|scorew ==
dscore|scorew`, max|dNMSE| = 0.000e+00):

| arm | mean | J in `_matrix_site` | clip | BLER@16 0 dB | +6 dB |
|---|---|---|---|---|---|
| d\|scorew | learned | learned | eta | 0.922 +- 0.034 | 0.719 +- 0.056 |
| d\|scorew+gmmJ | learned | EXACT GMM | eta | 0.062 +- 0.030 | 0.000 |
| d\|scorew+psd | learned | learned, eig in (0,1] | eta | 0.031 +- 0.022 | 0.000 |
| d\|scorew+clipmean | learned | learned | mean | 0.047 +- 0.026 | 0.000 |
| g\|scorew | EXACT GMM | EXACT GMM | eta | 0.109 +- 0.039 | 0.031 +- 0.022 |
| g\|scorew+dJ | EXACT GMM | **learned** | eta | **0.953 +- 0.026** | **0.922 +- 0.034** |

Paired McNemar (discordant pairs, 0 dB / +6 dB), one-sided, p < 1e-13 each: `g|scorew -> +dJ` 54:0 / 57:0;
`d|scorew -> +gmmJ` 0:55 / 0:46; `-> +psd` 0:57 / 0:46; `-> +clipmean` 0:56 / 0:46.
Injecting only the learned Jacobian into an otherwise exact arm reproduces the collapse (0.109 -> 0.953):
**the learned Jacobian is sufficient, given the D-14 site and `clip='eta'`.**
Cause, not symptom: at iteration 1 the cavity is arm-independent (`nu_q@1`, `alphaH@1` bit-identical across
each swapped pair), and the median NMSE of the FIRST channel estimate goes 0.152 -> 5.004 (0 dB) and
0.049 -> 26.25 (+6 dB) when only J is swapped in, 1.568 -> 0.093 and 4.774 -> 0.026 when only J is swapped out.
Independent PSD re-check (held-out stream 11, noise seed 20260921, `score.ExactGMMTorch` rather than
`t2_gmm.GMMPriorB`, n=96 q per nu, all in-grid): `frac lmin(J)<0` diffusion 0.698/0.958/1.000/0.990 at
nu = 2.60e-1/9.32e-2/3.35e-2/1.69e-2 vs GMM 0.000/0.000/0.000/0.000; med `|J-J^H|/|J|` diffusion 0.098-0.112
vs GMM ~1e-16.

commands
```
cd /home/HTJ/t2/conf && export OMP_NUM_THREADS=3
nohup ~/miniforge3/envs/torch/bin/python code/diag_h4_jswap.py --snrs 0 --n 64 > logs/h4_jswap_snr0.log 2>&1 &
nohup ~/miniforge3/envs/torch/bin/python code/diag_h4_jswap.py --snrs 6 --n 64 > logs/h4_jswap_snr6.log 2>&1 &
OMP_NUM_THREADS=2 ~/miniforge3/envs/torch/bin/python code/diag_h4_psd_indep.py > logs/h4_psd_indep.log 2>&1
```
artifacts `results/diag/h4-jswap_summary.txt`, `h4-jswap_D2_C2_snr{+0,+6}_n64.npz`,
`h4-jswap_D2_C2_snr+0_n4.npz`, `h4-jswap_psd_independent.npz`;
code `code/diag_h4_jswap.py`, `code/diag_h4_psd_indep.py`; logs `logs/h4_jswap_snr{0,6}.log`, `logs/h4_psd_indep.log`.

---

## 4. Corrections to the individual reports (the verdicts survive; these claims do not)

- **[C1] Asymmetry is not a link in the causal chain.** `ScorePrior._eval` (`code/score.py:959`) Hermitian-
  symmetrises J before the receiver sees it, and every intervention above acts on the symmetrised `Herm(J)`.
  The measured asymmetry (`herm_res` 0.17-0.20) is a co-symptom of the same non-conservative score field.
  Only **indefiniteness** is causal. H1's phrase "not symmetric, not PSD" overstates.
- **[C2] The receiver-side belief-mean shift is a marker, not a dose.** `RouteAClip` records the shift from
  the pre-recompute eta regardless of clip mode (`Demo/t2_gmm.py:120` precedes `:121`), so `dscore|mean`
  records shift 1.146e+03 at 0 dB while achieving BLER 0.047. H1's "shift peaks at 6 dB, NMSE peaks at 6 dB"
  correspondence is weaker than presented, and its own table already breaks it (shift is minimum at 12 dB,
  1.61e3, where BLER is still 0.523). Along-trajectory shift figures (6.96e3 / 2.88e3 / 8.70e2) are partly
  symptom; measured on held-out q the clean figure is 2.0-4.4 (still 3-6 orders above the GMM's 2.7e-3 .. 2.1e-8).
- **[C3] Clip firing rate is not the discriminator.** The GMM's J has `lmax > 1` on 51-79% of held-out q, which
  also drives Lambda negative and trips the `lam_min` floor. H4's "6 orders of magnitude" comparison of firing
  rates conflates the benign `lmax` clip with the harmful indefiniteness.
- **[C4] "The single causal component is the D-14 matrix site fed by the learned Jacobian" is one factor short.**
  Two independently sufficient repairs exist — replace/repair J, or set `clip='mean'` (a pre-existing option,
  one word, same indefinite J). The collapse is a **conjunction**: an indefinite learned Jacobian AND a site
  rule that keeps `eta` computed from the indefinite inverse while flooring the precision.
- **[C5] "The gate that failed is exactly the Jacobian gate (GD)" is FALSE for this configuration.** See §6.

---

## 5. The mechanism (reconciled)

1. Denoising score matching constrains the score **value**; nothing in the objective constrains its
   **derivative**. The learned field is not conservative: `|J - J^H| / |J|` = 0.10-0.20 on held-out q.
2. The receiver's D-14 matrix site does not consume the value. It consumes `J = dm/dq`, which for a true
   posterior-mean denoiser equals `Cov[h|q]/nu` and must be Hermitian PSD. After the forced Hermitian
   symmetrisation, the learned `Herm(J)` is **indefinite on 70-100% of held-out q** at the operating nu
   (`frac lmin<0 = 1.000` for k=0..11), with `|lmin|` median ~2.9e-3. The exact GMM is PSD to machine
   precision at every point.
3. `RouteAClip._matrix_site` (`Demo/t2_gmm.py:114-122`) inverts `SigH = nu*Herm(J)` with **no PSD check and
   no regularisation**, forms `eta = SigH^-1 hH - q/nu` (a negative eigenvalue of magnitude 1e-3 turns into a
   site precision of magnitude 1e3 with the wrong sign), floors the eigenvalues of `Lam` at `LAM_MIN=1e-6`,
   and under `clip='eta'` — the setting `arms.MODULE_H['score']` selects — **keeps the eta built from the
   indefinite inverse**. The returned (precision, mean) pair no longer describes any Gaussian, so
   `hpost = (Lam+G)^-1 (eta+b)` is pulled arbitrarily far from `hH`.
4. The damage is injected at the **first** site formation, before any decoder feedback (median NMSE of the
   first estimate 0.152 -> 5.004 at 0 dB when only J is swapped in), and RouteA has no divergence guard on
   the Module-H path, so the iteration is free to run 16 times with no flag raised.
5. This reconciles all three observations. GB' and Hyvarinen measure the score **value** / posterior mean —
   and on those the learned prior really is better, confirmed independently here: with an exact Jacobian the
   learned mean beats the GMM arm (`d|scorew+gmmJ` 0.062 vs `g|scorew` 0.109 at 0 dB). The BLER collapse is
   a property of the **derivative**, which neither passing diagnostic measures.
6. The collapse is specific to the learned prior (the exact GMM through the same wiring is healthy) and
   requires the wiring as a co-factor (`clip='mean'` repairs it with the same indefinite J).

---

## 6. What this does and does not say about the pre-registered gates

The gates GA-GD are computable only on D1, where the exact score is known; the D2 checkpoint was never gated.
Its configuration is HPO trial 386, whose D1 re-gate on the reported stream 10 (`results/hpo_final_r2.txt`) is:

```
GA 1.03540e-15 <= 1e-06  PASS
GB 7.71573e-03 <= 0.05   PASS
GC 2.24111e-01 <= 0.15   FAIL
GD 1.49894e-01 <= 0.20   PASS      GD_trace 2.96603e-02 (reported, not gated)
```

So for the configuration actually evaluated here, **GD — the full-Wirtinger-matrix relative Frobenius error —
PASSED, and the gate that failed is GC, the score's relative L2 error.** The "GD 0.27-0.32" figure quoted in
both adversarial reports is a family-wide range over other ladder members (LADDER.md: L4u_a3 GD 0.3198,
L5_a3 0.3859; final re-gate trials 400 and 88 at 0.2764 and 0.3056) and does not apply to trial 386.
Four of the six finally re-gated trials PASS GD (0.1499, 0.1623, 0.1644, 0.1657); all six FAIL GC (0.2241-0.3503).

Consequence: **the diagnosis does NOT show that "the gate that failed is the one that mattered".** It shows
something narrower and more useful — GD is a norm-relative error and cannot constrain the **sign** of the
smallest eigenvalue when `|lmin| ~ 3e-3` while `||J||` is O(1): a 15% relative Frobenius error is more than an
order of magnitude larger than the eigenvalue whose sign decides whether the site is a Gaussian at all. No gate
in GA-GD tests PSD-ness. The pre-registered battery blocked this arm for a different reason (GC), and the
property that actually broke the receiver was never measured by any gate.
That the sign statistic **is measurable on D2 without ground truth** (it is a property of the model's own
Jacobian) is the practical opening this diagnosis leaves.

---

## 7. What remains unexplained

**(a) The non-monotonic SNR shape is only PARTIALLY explained.** The decomposition below reproduces the
observed BLER exactly, but it is a re-partition of the same n=128 trials, not an independent prediction, and
it exists at only 3 of the 7 SNRs:

| SNR | blow-up rate | BLER \| blew up | BLER \| clean | product | observed BLER@16 |
|---|---|---|---|---|---|
| -3 dB | 0.836 | 0.953 | 0.333 | 0.852 | 0.852 |
| 0 dB | 0.984 | 0.929 | 0.000 | 0.914 | 0.914 |
| +6 dB | 0.969 | 0.798 | 0.000 | 0.773 | 0.773 |

The blow-up rate rises with SNR (the Jacobian is more often indefinite as nu shrinks) while the conditional
BLER falls (the likelihood recovers more of the block), and the product peaks at 0 dB. Open points:
- The do()-interventions were run at **0 and +6 dB only**. Five of the seven SNRs have no counterfactual.
- The "damage is monotone in SNR, the absolute BLER merely saturates" argument is not exactly true: the
  normalised damage ratios are themselves non-monotone at 12 dB — `dscore/pilot_C` = 1.7, 6.1, 17.7, 26.8,
  54.9, **47.9**, 66.7 and `dscore/M-ours-bstar` = 3.1, 9.7, 33.2, 63.6, 109.7, **55.8**, 100.0. The 12 dB dip
  is unexplained by anything measured here.
- The **NMSE** shape (0.265, 0.903, 0.963, 1.110, 0.549, 0.324, 0.104) peaks at 6 dB and then falls steeply;
  no counterfactual exists at 9, 12 or 15 dB to show that repairing the Jacobian flattens it.

**The experiment that would settle it.** Run `code/diag_psd_cf.py` at all seven SNRs (-3, 0, 3, 6, 9, 12, 15),
cell C2, n >= 256 paired trials on the pre-registered trial stream, arms
`{dscore|eta, dscore|psd1e-2, dscore|mean, gmmB|epsite}`, recording per SNR and per iteration:
(i) the realised `nu_q` distribution, (ii) `frac lmin(Herm J) < 0` evaluated at those realised `nu_q`
(not on the frozen grid), (iii) the blow-up rate and the conditional BLER. Pre-register the prediction
`BLER(SNR) = p_blow(SNR) * BLER|blow(SNR) + (1 - p_blow(SNR)) * BLER|clean(SNR)` with `p_blow` predicted from
the realised-nu indefiniteness fraction alone, and require the repaired arms to be monotone in SNR at all seven
points. Cost: CPU only, roughly 7 x 25 min single-process at n=256.

**(b) Generality is untested.** Only `ckpt/d2sx_N10000_a1.pt`, only cell C2. Seeds a2/a3, budgets
N=2500/4e4/1.6e5, and cells C1 (Tp=2) / C5 (Tp=3) were not measured, so "the learned Jacobian is indefinite"
is established for this checkpoint, not for the architecture family.

**(c) The origin of the non-conservative Jacobian is not determined** — training objective (DSM does not
constrain Jacobian symmetry) versus the DiT backbone. Untested here; this is what the pre-registered Stage C
variants V2 (energy parameterisation) and V3 (Jacobian regularisation) exist to separate.

**(d) Off-manifold behaviour.** All Jacobian statistics are measured on-manifold (`q = h + sqrt(nu)*eps` from
the true D2 prior). The receiver's cavity `q` is off-manifold. The receiver-level interventions (§3.6, §3.7)
run at the true operating points, so the causal conclusion does not depend on this — but the off-manifold
Jacobian spectrum itself is unmeasured.

**(e) Whether a divergence guard would rescue the arm** was not tested; only that no such guard exists.

---

## 8. Integrity statement

The repaired arms (`dscore|psd1e-2`, `dscore|mean`, `dscore|belsc`, `d|scorew+gmmJ`, `g|scorew+dJ`,
`X-gmm-score`) are **diagnostic probes**. Their BLER was seen before any pre-registration; none of them may
enter any table on the strength of these numbers. Everything in this document is a measurement of a frozen
checkpoint. Pre-registered files untouched; **M-ours-dscore remains BLOCKED on both testbeds.**
