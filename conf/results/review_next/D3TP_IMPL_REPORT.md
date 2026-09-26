# IMPL_REPORT — Tp > Nt cells (C7/C8) and the D3 control (prior S2c)

Written 2026-09-26 (KST, around 00:10 CDT). Nothing was committed and no long GPU job was launched. No BLER was run on
test trials (0..2559) or on any registered range. The only receiver runs were:
- the ν_q measurement on trials 6400..6463 (Gaussian receiver only; BLER was neither read nor written);
- smokes on trials 6400..6401 (n = 2).

Demo/ was not touched. Every existing testbed, prior and cell is bit-identical to HEAD `54d68a14` (§3).

---

## 1. Files changed (conf/code, `git diff --stat`: 9 files, +118 / −25) and new files

| file | change |
|---|---|
| `common.py` | **make_pilots**: new `Tp > Nt` branch placed *before* the existing code. It returns `("dft", exp(-2jπ·b·c/Tp))` for b = 0..Nt−1 and c = 0..Tp−1: unit modulus, `Xp Xp^H = Tp I`. The existing `Tp <= Nt` branches are unchanged. **CELLS**: C7 `(Nr 8, Nt 4, T 16, Tp 6)` and C8 `(… Tp 8)` are appended with C2's SNR grid. **DEFAULT_CELLS** = the cells with Tp ≤ Nt (C1..C6), so every no-`--cell` default keeps the old set. **PID** gets `"S2c": 5` (new value, nothing renumbered). **D3_WARNING** text is added. |
| `d2.py` | Prior **S2c** is registered: `ANGLE_RANGE["S2c"]` equals the S2 sector, and `CN_GAIN = ("S2c",)`. `D2Gen.cn` is set for S2c. In `_draw`, S2c returns `α = sqrt(p_l)·(N + jN)/√2` right after drawing (L, θ, φ); the S2 lines below are untouched. `sample_angles` gets the same branch. `ensemble_sides_d2("S2c")` is therefore identical to S2 (T2b gives DFT). The module docstring explains D3. |
| `runner.py` | `cmd_run` and `cmd_sigma` defaults use `C.DEFAULT_CELLS`, so C7/C8 run only when named. `--prior` / `--cell` choices pick up S2c, C7 and C8 automatically. |
| `sigma.py` | `CHAT_FROM_TRAIN = ("S2c",)`. For S2c there is no N=1e4 fit, so Chat is computed as `X^T X^*/n` of the stream-7 training set. This is exactly what `t2_gmm.fit_gmm_em` stores as Chat, and on S2 the computed Chat is **bit-equal** to `gmm_fits_D2/fit_S2_Nr8_fullK32_n10000.npz["Chat"]`. Every other prior reads the fit file exactly as before. |
| `analysis.py` | In `PAT`, the prior group changes from `[A-Z]\d?` to `[A-Z]\d?c?`. All 15,288 existing raw names parse to identical groups. The D2 header warning prints as before; the D3 warning prints when a group's prior is S2c. |
| `run_d2_sx.py` | Adds `--prior {S2,S2c}` (default S2 = unchanged; same call, names and stdout) and `--no-gbprime`. For S2c: rung `D2SXS2c<N>`, ckpt `ckpt/d2sx_S2c_N<N>_a<k>[_fb<j>].pt`, log `logs/train_d2sx_S2c_…`, `results/d2_gbprime_S2c_….npz`, CSV `results/d2_gbprime_S2c.csv`, `sigma_tag="S2c"` (stored in the ckpt), and a `stopped_by/aborted` print line. |
| `fit_gpu.py` | Optional `--prior P` (default `PRIOR_OF["D2"]` = unchanged). `fit_gpu_batched.py` passes it through without changes. |
| `run_manifest.py` | The prior is read from the raw names (`{"S2"}` for every existing tag, so output is unchanged). The S2c description says `alpha_l ~ CN(0,p_l)`. |
| `eval_accept.py` | `--prior` (default S2) for the grid-completeness glob. |
| **new** `selftest_d3tp.py` | Bit-identity against a git revision, plus property checks (§3). |
| **new** `testbed_d3.py` | D3 verification, writing `results/testbed_D3.txt` (§4). |
| **new** `nuq_coverage_tp.py` | ν_q coverage, writing `results/review_next/nuq_coverage_tp.txt` and `.npz` (§5). |
| **new** `run_d3.sh` | D3 GPU queue (§7). Not started. |

New outputs in conf/:
- `results/sigma_grid_D2_S2c.{txt,npz}` and `logs/sigma_S2c.log`
- `results/testbed_D3.txt`
- `results/review_next/nuq_coverage_tp.{txt,npz}`

Nothing else was written to conf/. The empty `raw_S2c/` that `runner.py` creates was removed, and no fits dir was created.

### Tp > Nt audit (Task A.1)

**No arm needed a change.**
- `route_a`, R3, R4-scvamp/-llr and pilot_only take `Xp` explicitly, and every consumer is generic in Tp. That covers `A[:Tp]`, `Y[:, :Tp]`, `Xp^* Xp^T`, the Tau/Xbar stacking and `QAMCode(Nt(T−Tp))`, which gives K = 34 / 26.
- **Demo `dft_pilots(Nt, Tp)`** returns only Nt columns when Tp > Nt. So `RouteA(Xp=None)` would fail its shape assert, but no conf arm calls it that way.
- The **eig branch** can supply only Nt eigenvectors. It is bypassed by the new branch, which also overrides the T2b decision for Tp > Nt; that is moot for S2/S2c, where T2b already says DFT.
- `d2._pilots` (T2c helper only) returns Nt columns for Tp > Nt. T2c's `Tp >= Nt` branch reports NMSE_inf = 0, which is correct because full-span pilots give 0.

**Still open:**
- **analysis table C** pairs only C1/C2. C7/C8 appear in tables A and B with the right K, but the Tp Pareto/goodput table needs its own pre-registered script.
- `tp_trend.py` and `figures_stagec2.py` have hard-coded cell lists; these are report scripts and were left unchanged.
- **`runner.py smoke` runs trials 0,1, which are test trials.** Do not use it for C7/C8/D3. The smokes here used `runner.run_task` with skip = 6400 (§6).

---

## 2. Decisions taken here (flagged for the Fable pre-registration)

1. **σ grid for D3.** I measured S2c's own grid with the headline procedure: `runner.py sigma` with cells C1+C2 (the headline grid's cells), n = 64, and the Gaussian Chat of the N=1e4 stream-7 set. The resulting S2c grid is [3.2831e-2, 8.6484e-1], against the frozen D2 grid [3.3062e-2, 8.4516e-1]: −0.7 % at the low end and +2.3 % at the high end. S2c training uses it (`sigma_tag="S2c"`, as C6 did with "NR16").
   *Alternative:* keep the frozen D2 grid as the ruler. To do that, drop `**({"sigma_tag": PT} …)` in `run_d2_sx.py`.
2. **Receiver for the ν_q measurement.** R2-ours-G itself (mode `colored`) never queries a denoiser and logs `nu_q = NaN`. I used sigma.py's receiver instead: the same Gaussian prior through the score interface, which the Demo T6 identity says follows the same trajectory. R2-ours-G was run on the same (H, Y) as a check. The max |NMSE_t difference| over all trials, iterations and points is **2.8e-8**.
3. **GB′ checkpoint.** `run_d2_sx.py` computes GB′ on the last-epoch file, as it always has for S2. The pre-registration must name which file the BLER run uses; S2c training writes `_best.pt` too.
4. **Batched kron M-step.** It was not re-checked on S2c data. It is an algebraic identity, already PASSED on S2 at Nr 8 and 16, including the reseed-active case. For a re-check, run `em_batched_check_nr.py` with `NR, PRIOR = 8, "S2c"` (one GPU, minutes).
5. **§3d standby** (DECISIONS 6953d595 style) is **not** automated. The ladder hook is sequential on one GPU. A standby fallback-2 run would need a rule registered before launch and would be started by hand, as in C6.

---

## 3. Bit-identity test (`python code/selftest_d3tp.py`, vs HEAD 54d68a14)

How it works: `git archive HEAD conf/code` is extracted into a temp dir (Demo symlinked). The same `dump()` runs on the old tree and on the working tree in separate processes, and every array is compared with `np.array_equal`. The dump covers:
- D2 `sample_vecs` (1000 draws, fixed rng) for priors S2/U2 at Nr 4/8/16, plus train streams 7/8/10/90;
- `sample_angles`, ensemble sides, and D1 `sample_vecs` for U/S/P;
- `make_pilots` for every existing (testbed, prior, cell);
- the first 3 trials (H, u, perm, Y) of every existing cell at its first and last SNR (D2/S2, and D1/S where it applies);
- code sizes, PID/TBID, and `analysis.PAT` groups for every raw file name under `conf/raw*/`.

Output:
```
bit-identity vs HEAD: 387 arrays, 337941 values, 15288 raw file names -> IDENTICAL
properties: C7/C8 pilots (unit modulus, Xp Xp^H = Tp I, K=34/26), S2c sides == S2, S2c path gains |alpha|^2/p_l mean 1.0031 (1), E[.^2] 2.0183 (2) -- OK
```
The properties block also asserts:
- S2c draws the same (L, θ, φ) as S2 from the same rng state (only the gains differ);
- S2c train streams differ from S2 and U2 streams;
- `DEFAULT_CELLS` = {C1..C6}.

Code-level identity checks, not covered by the dump:
- `run_d2_sx.py` with the default S2 makes the same `score.train` call (identical kwargs), uses the same names and CSV, and prints nothing extra.
- `fit_gpu.py` without `--prior` resolves to the same prior.
- `sigma.measure_point` for S2 runs the fit-file line verbatim.
- `run_manifest` still gives the prior `"S2"` and the same description.
- `d2.py`'s own self-check still passes (`python code/d2.py`).

---

## 4. D3 testbed validation (`python code/testbed_d3.py`, writes `results/testbed_D3.txt`, 25 s CPU)

| id | verdict | value |
|---|---|---|
| T2a (n = 1e5) | PASS | rel err 9.63e-4 ≤ 1e-3. **But the MC s.e. at n = 1e5 on S2c is 1.8e-3** (sd(‖H‖²/NrNt) = 0.57 vs 0.16 on S2), so this verdict is mostly chance. |
| **T3a** (T2a criterion at n = 4e6, stream 93) | **PASS** | E‖H‖²/(NrNt) = 1.000086, rel err 8.6e-5 = 0.31 s.e. (s.e. 2.8e-4) |
| T2b | RECORD | erank(Rt) = 3.8770/4 (0.969), so pilots are **DFT**, same as S2 (identical sides) |
| T2c | RECORD | C1 (Tp 2): NMSE_inf dft 0.4663. C2 (Tp 4): 0 |
| T2d / T2dm (D2 criterion) | FAIL(exp) | expected: D2's prediction 2 − Σp² no longer holds |
| **T3d** (restored conditional Gaussianity) | **PASS** | every 99.9 % CI contains 2; max \|meas − 2\| = **0.0071**. L=3: 2.0059 (1.9872, 2.0280); L=4: 1.9933; L=5: 2.0063; L=6: 2.0005; L=7: 2.0013; L=8: 1.9988 (plus 2 free L=5 sets) |
| T3dm | RECORD | the D2 prediction (1.614..1.746) is below every T3d CI; smallest margin 0.2375 |
| T2e | RECORD | effective #bins 5.895/32 |

T3a was added because T2a's own criterion is underpowered for CN gains. The 1e-3 value is kept; only n changes.

**σ grid:** `runner.py sigma --testbed D2 --prior S2c --cell C1 C2 --tag S2c` finished in 7 s and wrote `results/sigma_grid_D2_S2c.{txt,npz}` (log `logs/sigma_S2c.log`). The grid is 20 points over ν_q ∈ [2.1558e-3, 1.4959], i.e. σ_t ∈ [3.2831e-2, 8.6484e-1].

---

## 5. ν_q coverage (`python code/nuq_coverage_tp.py`, writes `results/review_next/nuq_coverage_tp.txt` and `.npz`)

Setup:
- Receiver: Gaussian Chat from `gmm_fits_D2_B16e4k` (full K = 32, N = 1.6e5) through the score interface.
- Trials 6400..6463, 16 iterations, 21 workers, 8 s wall.
- Grid: headline ckpt `d2sx_N160000_a1.pt` has `sigma_tag = ''`, so the frozen D2 grid applies: s_lo = 3.30622e-2, s_hi = 8.45156e-1.

Fraction of queries below / inside / above the grid:

| cell | pooled (7 SNR × 64 × 16) | +15 dB | every other SNR (−3..+12) | min σ_t |
|---|---|---|---|---|
| C2 (Tp 4) | 0.025 / 0.975 / 0.000 | 0.176 / 0.824 / 0 | 0 / 1 / 0 | 0.974 × s_lo |
| C7 (Tp 6) | 0.037 / 0.963 / 0.000 | 0.257 / 0.743 / 0 | 0 / 1 / 0 | 0.972 × s_lo |
| C8 (Tp 8) | 0.092 / 0.908 / 0.000 | 0.644 / 0.356 / 0 | 0 / 1 / 0 | 0.968 × s_lo |

At +15 dB, below-grid queries start at iteration 2 and stay flat through iteration 16 (C2 19 %, C7 27–28 %, C8 67–69 %). No query at any cell or SNR is above the grid. The per-iteration median σ_t is in the .txt.

---

## 6. Smokes (trials 6400..6401 only, n = 2; raw written to scratch, never to conf/raw*)

`scratch/d3tp/smoke_runner.py` calls `runner.run_task` (the real code path) with `d_raw` redirected.

- **C7/C8, S2**: B16e4k fits (N = 1.6e5) with `--stagec-ckpt ckpt/d2sx_N160000_a1.pt`. 14 arms: R0 R1 R2 R3 R4-scvamp R4-llr R5-genie M-ours-gmm32 M-ours-bstar M-ours-bstar-scalar V0 V1 V4 V4b. No exceptions, finite NMSE, b* = kron 1024. `analysis.main` on that raw prints `cell C7 (8x4, T=16, Tp=6, K=34)` and `C8 … K=26`. Output: `smoke_C7C8.txt`.
- **D3 (S2c), C2 and C7**: sandbox fits and ckpt (below). Same 14 arms, no exceptions. Analysis prints the D3 warning; `run_manifest` labels the prior S2c with the CN description, while S2 keeps its old description. Output: `smoke_D3.txt`.
- **`run_d3.sh` end-to-end, in a sandbox**: `scratch/d3tp/sandbox` (a copy of conf/code with Demo symlinked), run as `CONF=… N=10000 TAG=D3smoke GPUS="0 1 2 3"`, then `GPUS="0 1"`. It exercised:
  - all 19 queue jobs, rc = 0 (full exact, kron batched, kron 1024 and 2048 per restart);
  - the **crash path**: training killed, `stopped_by=None`, chain stops, no GB′;
  - `merge kron 1024` and the grid-completeness check;
  - the **edge rule**: b* = kron 1024 = family max, so "MANUAL … kron 2048 candidates ready: 3/3" and GB′ deferred;
  - then a manual 2048 merge, a forced `stopped_by=diverged` on attempt 1 and a 205-epoch cap in the sandbox copy only. Result: "§3d: fallback 1 DIVERGED → fallback 2 on GPU 1", then `max_epochs`, then b* interior, then **GB′ (fallback 2) rc = 0**.
  - Outputs: `d2_gbprime_S2c.csv`, `d2_gbprime_S2c_N10000_a1_fb2.npz`, ckpt `d2sx_S2c_N10000_a1_fb2{,_best}.pt` (rung D2SXS2c10000, sigma_tag S2c, grad_clip 1.0).
  - The sandbox numbers are smoke-only and meaningless.

---

## 7. Launch commands (main session, after review and commit)

The queue logs `git rev-parse` of HEAD, so commit conf/code first. Then:
```bash
cd /home/HTJ/t2/conf && tmux new-session -d -s d3 'GPUS="0 1 2 3 4" bash code/run_d3.sh'
# GPU 5 free as well:  GPUS="0 1 2 3 4 5".  A GPU with memory in use (>10 MiB) at launch or before a job is skipped, not retried.
tail -f logs/d3.log         # CDT stamps; per-GPU logs/d3_gpu<g>.log, post phase logs/d3_post.log, logs/d3_train_state.txt
```

**Queue** (19 jobs; files go to `results/gmm_fits_D2_D3B16e4/fit_S2c_Nr8_*_n160000*`):
1. `@train`: `run_d2_sx.py --prior S2c --ntrain 160000 --tag D3B16e4 --fallback k --no-gbprime`. k = 1, then 2 or 3 only after `stopped_by=diverged`, on the same GPU.
2. kron 1024, restarts 0, 1, 2 (batched).
3. full 512, 256, 128, 64, 32, 16 (exact, κ grid) interleaved with kron 512..16 (batched).
4. kron 2048, restarts 0..2, as candidates only (not merged).

**Post phase:**
- merge kron 1024;
- b* by ll_val;
- missing K → no GB′;
- b* = the largest K of its family → "MANUAL: extend K", GB′ deferred;
- otherwise GB′ for the attempt the ladder ended on.

**Expected duration.** Training should take about 10 h: D2 N = 1.6e5 attempt 1 ran 1784 epochs at 20 s each, 9.9 h. Fits should take about 1–2 h on the other GPUs, going by NR16B16e4 and B32e4 durations.

**Edge rule.** S2 at 1.6e5 had b* = kron 1024 (B16e4k), so the rule may fire here too. After the user decides:
```bash
CUDA_VISIBLE_DEVICES= ~/miniforge3/envs/torch/bin/python code/fit_gpu.py 8 kron 2048 160000 D3B16e4 --merge --prior S2c
bash code/run_d3.sh    # empty queue file -> workers exit at once -> post phase only (b* again, then GB')
```

**Resume after a kill.** Jobs are popped when they start, so a killed job is gone from the queue. Put its line back at the head of `logs/d3_queue.txt` (for training: `@train`; it resumes from the checkpoint) and relaunch. Re-running the post phase after GB′ has already been computed appends a second row to `results/d2_gbprime_S2c.csv`.

**After the Fable freeze only (BLER; not now):**
```bash
# D3 (cells per the registration, e.g. C2 [C1]); fits dir = raw tag = D3B16e4
python code/runner.py run --testbed D2 --prior S2c --cell C2 --n 2560 --chunk 40 --ntrain 160000 \
  --stagec-ckpt ckpt/d2sx_S2c_N160000_a1[_fb<k>]_best.pt --tag D3B16e4
python code/runner.py analysis --testbed D2 --tag D3B16e4; python code/run_manifest.py --tag D3B16e4
python code/eval_accept.py --prior S2c --fits-dir results/gmm_fits_D2_D3B16e4 ...
# C7/C8 (S2, same budget as B16e4k).  --tag routes the fits dir too, so link it first:
ln -s gmm_fits_D2_B16e4k results/gmm_fits_D2_<TAG>
python code/runner.py run --testbed D2 --prior S2 --cell C7 C8 --n 2560 --chunk 40 --ntrain 160000 \
  --stagec-ckpt ckpt/d2sx_N160000_a1.pt --tag <TAG>
```
