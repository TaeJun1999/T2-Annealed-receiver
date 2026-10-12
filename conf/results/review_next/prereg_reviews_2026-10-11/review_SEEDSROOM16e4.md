# Adversarial pre-run review — NEXT_EXPERIMENTS_SEEDSROOM16e4 (draft v1) + `code/run_seedsroom16e4.sh`

- Reviewer: Fable 5.1 subagent. Report written 2026-10-12 09:22 CDT (review started 2026-10-12 09:07 CDT, read by `date`).
- Reviewed objects (sha256[:16], read at 09:07:14 CDT and again at 09:19:42 CDT, unchanged): registration `9dfba89cd7ec5e0d`, driver `2608f224c3d0b538`; HEAD `2cf68d5c`.
- Nothing under `conf/code` / `Demo` was created or modified; no `runner.py run`, no GPU. Read-only runs: `eval_accept.py` (a1 raws, through the new links), `arms.gmm_selection`, `torch.load(map_location="cpu")`.

## Verdict

**Runnable as is: YES.** No script bug found — all four calls trace to an accepted run (arguments, sha, links, b\* selection, grids, acceptance line format, loop/stdin handling all verified). **One MUST on the record** (the "what is running / what has been seen" disclosure went stale between 09:06 and 09:15 CDT: a GB′ value of an evaluated seed now exists before the freeze, and the a4 · a5 trainings were stopped). **4 SHOULD** (one is a driver gate, code given), **6 NIT**.

---

## MUST

### M1. Disclosure is stale at freeze: an SRB a2 GB′ value exists before the freeze, and a4 · a5 trainings are no longer running
- **Where**: header "작성 시점 공개" last bullet ("지금 GPU 에서 도는 것"), §1 row "보고 전용" (the GB′ sentence), §1 row "CPU 절반" (last sentence), §5 (addendum line promised by the draft).
- **What is wrong**: v1 (file mtime 09:06:34 CDT) says the GB′ values "may come out before the BLER" and that four a4 · a5 trainings are running. Both are now false or incomplete:
  - `logs/gbprime_SRBB16e4_a2.log` / `results/d2_gbprime_SRB.csv` / `results/d2_gbprime_SRB_N160000_a2.npz` (all mtime **09:13:00 CDT**): `GMM b* = gmm1024 (full K=1024) @N=160000 | diff/gmm min 0.5673 max 1.0104 median 0.6158` (csv row `160000,2,…,1357,…,0.567277,1.010419,0.615774,0.010419`; a1 row: min 0.594906, max 5.104649, median 0.647227). A denoising-quality number of an evaluated seed that is *better* than a1's is information bearing on predictions 1–3. SRB a3 GB′ started 09:13:04 CDT (SRB takes ~9 min, not the 1 h 45 min of SRP a1) so it will also be out before any realistic freeze; SRP a2 running since 09:04:02 CDT; SRP a3 not started.
  - `logs/seeds_SRB_train.log` / `logs/seeds_SRP_train.log`, 09:15 CDT: `NOTE: SR{B,P} a4 / a5 stopped by SIGINT on purpose (… the registered seed set is a1..a3); checkpoints kept, resumable`. Partial `ckpt/d2sx_SR{B,P}_N160000_a{4,5}*.pt` exist.
- **Why MUST**: "report-only, no label" is airtight for the *label* (table B is mechanical; GB′ never enters `analysis.py` / `eval_accept.py`), but the only leak path is §3 (predictions) or a §1 design choice changed between v1 and v2 after the GB′ value became visible. The record must say what existed at freeze and that §3 was not touched. Evidence that §3 predates the value: this review read v1's sha (`9dfba89cd7ec5e0d`) at 09:07:14 CDT, 6 min before the first GB′ value.
- **Replacement text** (header bullet; replace the whole "- **지금 GPU 에서 도는 것(이 등록 밖)**: …" bullet):

  > - **등록 밖에서 돈 것·도는 것 (동결 시점 기준)**: 시드 a4 · a5 의 학습 네 개(SRB · SRP; GPU 0–3)는 10-12 09:03 CDT 에 시작했다가 **09:15 CDT 에 SIGINT 로 멈췄다**(등록 시드는 a1..a3; `logs/seeds_SR{B,P}_train.log` 의 NOTE 줄). 부분 체크포인트 `ckpt/d2sx_SR{B,P}_N160000_a{4,5}*.pt` 는 남아 있고 이 등록은 평가하지 않는다(분모 3 고정; 쓰려면 새 등록). a2 · a3 의 동일예산 GB′ (GPU 4 · 5, 09:03 CDT ~, a2 다음 a3; 보고 전용, BLER 이 아니다 — §1 보고 전용 행): **v1 (sha256[:16] 9dfba89cd7ec5e0d, 09:06 CDT) 의 §1–§3 은 a2 · a3 의 GB′ 값이 하나도 없을 때 썼고, v2 는 §3 예측을 바꾸지 않았다**(검토가 v1 해시를 09:07 CDT 에 읽었다 — `prereg_reviews_2026-10-11/review_SEEDSROOM16e4.md`; v2 의 §1 변경은 그 검토의 S1 · S2 · N1 뿐). **동결 전에 나온 GB′ 값은 §5 추가 줄에 있다**(SRB a2 는 09:13 CDT); 나머지는 BLER 중·뒤에 나온다.

  §1 "보고 전용" row — replace `이 등록의 동결 전에 시작됐고 값이 BLER 보다 먼저 나올 수 있다(나온 값은 §5 추가 줄에 적는다)` with:

  > 이 등록의 동결 전에 시작됐고 **일부 값은 동결 전에 나왔다**(§5 추가 줄; §3 예측은 그 전에 썼고 바꾸지 않았다 — 머리말 공개). 나머지는 BLER 중·뒤에 나온다(나오는 대로 §5 추가 줄에 적되 **커밋은 `SEEDSROOM_DONE` 뒤**)

  §1 "CPU 절반" row — replace the last sentence (`같은 시간대의 GPU 학습(등록 밖)은 … 나누지 않는다`) with:

  > 같은 시간대의 등록 밖 GPU 작업(a2 · a3 의 GB′; CPU 쌍 68,164 · 69,165 = 노드 2)은 마스크 밖 스레드에 고정돼 있어 runner 와 코어를 나누지 않는다(a4 · a5 학습은 09:15 CDT 에 멈췄다)

  §5 — add under the table (values for SRB a3 / SRP must be **read at freeze**, not typed from this review):

  > **추가 줄 — 동결 전에 나온 GB′ (보고 전용; 라벨·예측에 쓰지 않는다; `results/d2_gbprime_SRB.csv` · `logs/gbprime_SRBB16e4_a<s>.log` 원문; last `.pt`, n_eval 4096, b\* gmm1024)**: SRB a2 — diff/gmm median **0.6158** (min 0.5673 · max 1.0104), 10-12 09:13 CDT; 나란히 a1 0.6472 (min 0.5949 · max 5.1046; ROOM16e4 §6.9). SRB a3 — `<동결 시점에 tail -1 logs/gbprime_SRBB16e4_a3.log 로 읽어 적는다; 줄이 없으면 "아직 없음">`. SRP a2 · a3 — `<ls results/d2_gbprime_SRP_N160000_a{2,3}.npz 로 확인; 없으면 "동결 시점에 아직 없음">`.

---

## SHOULD

### S1. Driver: `ok` does not gate on the `--ref-arms all` report although §1 makes a non-Stage-C difference invalidating
- **Where**: `code/run_seedsroom16e4.sh` lines 30–32; registration §1 "태그·실행" (driver description) and prediction 7.
- **What**: `ok` = `SEEDS_EVAL_DONE` + first line `ACCEPT: OK -- <TAG>`. The acceptance call only replays R5-genie; a b\* / R-arm difference from the a1 raw (the thing §1 calls "실행 무효", and the thing that guarantees the decision points equal a1's) shows up only in `<TAG>_refarms.txt`, which the driver merely echoes. An unattended `SEEDSROOM_DONE ok=4 fail=0` would then read as "accepted" while one tag is invalid. `run_seedsnr16e4.sh` already has this gate (`refok`).
- **Evidence**: the gate below was run on a real pool report (`eval_accept.py … --tag SRBB16e4last:last:… --ref-raw raw_SRBB16e4 --ref-arms all`, 7 lines, 221 s) → PASS; on five tampered copies (b\* added to the list / `shared 2520/2560` / `keys missing` / `ACCEPT: OK` first line / file absent) → FAIL each; on the precedent files `{D3B16e4s2,SVB16e4s3,U28B16e4s2,B16e4s3,MXB16e4s2}_refarms.txt` → PASS each.
- **Replacement code** (replace lines 30–32; `bash -n` clean):

```bash
  RA=results/review_next/${TAG}_refarms.txt   # gate (§1 수용): every point shares 2560/2560 trials, no key missing, only Stage C arms differ from the a1 raw
  refok () { [ "$(head -1 $RA 2>/dev/null)" = "ACCEPT: FAILED" ] && [ "$(sed 1d $RA | wc -l)" -ge 1 ] && ! sed 1d $RA | grep -v -E \
    "^  $TAG \('C2', -?[0-9]+\): replay vs $REF \(all\): shared 2560/2560, arms differing \[('M-ours-dscore-C-V(0|1|4|4b)'(, )?)+\] \(max \|diff\| [^)]*\)$" | grep -q .; }
  if grep -q 'SEEDS_EVAL_DONE' logs/run_seeds16e4_$TAG.log 2>/dev/null && [ "$(head -1 results/review_next/${TAG}_accept.txt 2>/dev/null)" = "ACCEPT: OK -- $TAG" ] && refok; then
    OK=$((OK+1)); log "$TAG done: $(head -1 results/review_next/${TAG}_accept.txt); ref-arms gate ok: $(grep -o 'arms differing \[[^]]*\]' $RA | sort -u | tr '\n' ' ')"
  else FAIL=$((FAIL+1)); log "$TAG NOT accepted (see logs/run_seeds16e4_$TAG.log, results/review_next/${TAG}_accept.txt, $RA) -- continuing with the next tag"; fi
```
- **Registration text** (§1 "태그·실행", replace `` `SEEDS_EVAL_DONE` 과 `ACCEPT: OK` 확인 `` with):

  > `SEEDS_EVAL_DONE` · `ACCEPT: OK -- <TAG>` · `--ref-arms all` 관문(모든 점 shared 2560/2560, 빠진 키 없음, 다른 arm ⊆ {V0, V1, V4, V4b}) 확인 — 셋 다여야 ok

  (The driver sha changes with this edit; lazier alternative if the driver is left untouched: keep the script and add to §1 that `ok=4` alone is not acceptance and the transcriber must read the four `_refarms.txt` — works, but an unattended run then needs a human step.)

### S2. No commit and no new file under `conf/code` until `SEEDSROOM_DONE` — say so in §1
- **Where**: §1 "태그·실행" (end) or §4.
- **What**: the driver exits (`ABORT: HEAD moved`, no `SEEDSROOM_DONE`) before the next tag if any commit lands during the ~5 h run, and `run_seeds16e4.sh` aborts each later tag if anything untracked appears in `conf/code`. The draft itself plans mid-run record writes (GB′ addendum lines), and the FIGHSX16e4 resume was aborted by exactly this kind of mid-run edit (DECISIONS 2026-10-12 19:03 KST line). After an abort the remaining tags can only be started by hand, and a half-written raw needs user approval.
- **Replacement text** (append to §1 "태그·실행"):

  > **실행 중 규칙**: `SEEDSROOM_DONE` 이 찍힐 때까지 main 에 커밋하지 않고 `conf/code` · `Demo` 에 파일을 만들지 않는다(HEAD 가 움직이면 드라이버가 다음 태그 앞에서 멈추고, `conf/code` 가 더러우면 `run_seeds16e4.sh` 가 그 태그를 중단한다). 실행 중에 생기는 기록(GB′ 값 등)은 작업 트리에만 쓰고 끝난 뒤 커밋한다.

### S3. §5 row header attributes `stopped_by` to `_best.pt` — the field there is `None`
- **Where**: §5 table, first row header `sha256[:16] · epoch · best_epoch · stopped_by (`_best.pt`; last 의 epoch)`.
- **Evidence**: `torch.load` of the four `_best.pt`: `stopped_by = None`; `patience` is the last `.pt`'s value (and the log's `# done` line). The SEEDS3_16e4 audit already had to correct this exact header (its §6 correction 4).
- **Replacement text**:

  > `sha256[:16] · epoch · best_epoch (`_best.pt`) · stopped_by (last `.pt` · 로그 done 줄; 괄호 = last 의 epoch · sha)`

### S4. Cost row: keep the band, but state what it rests on
- **Where**: §1 "비용 [추정]".
- **What**: the 53.2 min of SRP a1 was measured with other CPU load on the machine (PATH16e4 §6 운영 기록) and the `last` tag of the same pool took 41.2 min; "뒤 단계 몇 분씩" is ≈ 5 min per tag (`--ref-arms all` alone measured 221 s here; SEEDS3 D3B16e4s2: 04:48 → 04:53 CDT).
- **Replacement text**:

  > CPU: 192 스레드 실측 SRB 28.3 분(best) · 24.8 분(last), SRP 53.2 분(best; 다른 CPU 부하와 겹침) · 41.2 분(last) → 96 스레드(물리 코어 절반)에서 약 2 배: SRB 태그 ≈ 50–57 분, SRP 태그 ≈ 82–106 분, 뒤 단계 ≈ 5 분/태그 → **네 태그 ≈ 4.7–5.8 시간**(시분할 손실 10 % 를 더하면 ≈ 6.3 시간까지) 순차. GPU: 없음(BLER). RAM: a1 실행과 같다(워커 192 개 그대로)

---

## NIT

- **N1. SRP qualifier only shown for the "시드 강건" string.** §1 label row: after the example add `; 다른 두 집계에도 괄호 안 끝에 같은 꼴로 붙인다 — "시드 의존 (k/3 (i), m 다름; b* = 씨앗 초기화 GMM)" · "판정하지 못함 (k/3 (i), j 판정 못함; b* = 씨앗 초기화 GMM)"`. (Form is consistent with SEEDSNR16e4's `; a<s> = §3d fb<k>` qualifier — inside the parenthesis, part of the label string.)
- **N2. §3 item 8 is not a prediction** ("빗나갈 경로"), yet the header says every item is scored. Prefix it with `(채점 제외 — 경로 설명)`; items 1–7 are scoreable as written (1 · 4 mechanical from table B; 2 · 5 three-digit BLER in the closed Wilson interval — verified 704/2560 → [0.2581, 0.2926], 812/2560 → [0.2994, 0.3355]; 3 · 6 CI overlap from the table-B gap line; 7 from the driver log + `_refarms.txt`).
- **N3. "앞선 시드 등록 다섯"** — the parenthesis lists datasets, not registrations, so the count cannot be checked. Suggested: `앞선 시드 등록(SEEDS16e4: D2 · UMi28; SEEDS3_16e4: D3 · SV8e · MIX3; SEEDSNR16e4: Nr 16/32 세 셀; "시드 강건 3/3" 이 다수)`. Optional half-sentence: DMC · SRT 의 a2 · a3 체크포인트는 있으나 평가된 적 없다(WORK_QUEUE 결정 대기 5) — so no pool was picked after seeing its seed BLER.
- **N4. Training-log header sentence** ("검토가 확인할 것") — confirmed, can be stated as fact: header counts now 2 / 2 / 2 / 1 (SRB a2, SRB a3, SRP a2, SRP a3); the second header is the GB′ no-op resume (`# resume : checkpoint already meets stopped_by=patience … no epoch trained, … left untouched`) at 09:04:02 CDT (a2 logs) and 09:13:04 CDT (SRB a3); SRP a3 gets its own when its GB′ starts. Each log: epoch lines = last epoch (1357 / 1519 / 764 / 783), first line `epoch 1`, no other `# resume` line; checkpoint mtimes are the training-end times and all eight sha values still equal §5.
- **N5. §4 link time**: the four links' mtime is 09:05:10 CDT (doc: 09:06). Harmless.
- **N6. Launch directory**: `tmux new -d -s seedsroom "bash code/run_seedsroom16e4.sh"` resolves the script path relative to the directory tmux is started from; started outside `conf/` the session dies at once with no log. Either launch from `/home/HTJ/t2/conf` or use `tmux new -d -s seedsroom -c /home/HTJ/t2/conf "bash code/run_seedsroom16e4.sh"`; after launch check that `logs/run_seedsroom16e4.log` has its `start` line.

---

## Verified (how)

**A. The four calls**
- `bash -n code/run_seedsroom16e4.sh` clean. Dry parse of `ROWS` with the driver's own `while IFS='|' read` → 4 rows, each 10 arguments, GRID kept as one argument with its space; no trailing whitespace (`cat -A`).
- Per row: checkpoint exists, `sha256sum | cut -c1-16` = row sha = §5 (2d3e7eae6bb20008 / 9f6a9d5042587ae5 / bdc0f5e854d2abbd / 5db51008da6cc8df). `torch.load(cpu)`: epoch = best_epoch = 1337 / 1499 / 744 / 763, role `best`, best_val = §5 to the last digit, rung D2SXSRB160000 / D2SXSRP160000, attempt 2 / 3, split_hash c009329584978bd9 (SRB) / 27af93705c6dc289 (SRP) = a1's, prior = sigma_tag = SRB / SRP, grad_clip 0.0, same hp as a1. Last `.pt`: epoch 1357 / 1519 / 764 / 783, best_epoch as above, stopped_by patience, sha = §5.
- Links `results/gmm_fits_D2_{SRBB16e4,SRPB16e4}s{2,3}` are symlinks to the a1 dirs. Reference raws: 448 files each, 14 arms each (R0, R1, R2, R3, R4-scvamp, R4-llr, R5-genie, gmm32, b\*, b\*-scalar, V0, V1, V4, V4b; M-ours-dscore ABSENT in both, same reason string) — "14 arm" holds. `meta|bstar / kron_K / ll_val` identical in all 448 files: SRB gmm1024 / 2048 / 97.00871495382869, SRP kron / 4096 / 244.1932863626755. No `raw_SR{B,P}B16e4s*`, no `logs/run_seeds16e4_SR*`, no `results/review_next/SR?B16e4s*`.
- Flags: `run_prior_eval.sh` (a1) used `--testbed D2 --prior $PR --n 2560 --chunk 40 --ntrain 160000 --cell C2 --stagec-ckpt … --tag` — the same set as `run_seeds16e4.sh`; nothing pool-specific is missing. `runner.py` read: prior check (ckpt prior == run prior) passes; `_init(tag)` routes fits to the link; `load_fits` opens only exact merged names, so the unmerged `fit_SRB_Nr8_kronK4096_n160000.k0r{0,1,2}.npz` in the SRB dir (no merged K4096 file there) and all `.k0r*` in the SRP dir are invisible to selection.
- `arms.gmm_selection` run through each link (CPU): same b\*, kron_K and ll_val as the a1 raws for all four tags (15 fits each).
- `eval_accept.py` run read-only on the a1 raws with the **seed-call argument form and `--fits-dir` = each new link**: SRB `--bstar gmm1024 --kron-K 2048` + SRB grid → `ACCEPT: OK -- SRBB16e4` (rc 0, both links); SRP `--bstar kron --kron-K 4096` + SRP grid → `ACCEPT: OK -- SRPB16e4` (rc 0, both links). So: kron_K is ignored for a full-family b\* (code lines 85–86, and in practice), the grid strings (identical to `run_srb_eval.sh` / `run_srp_eval.sh`) are complete incl. 3 candidates for every kron K ≥ 1024, and the single-tag first line is exactly `ACCEPT: OK -- <TAG>` — the string the driver compares.
- Decision-SNR regex of `run_seeds16e4.sh` on `tables_D2_{SRBB16e4,SRPB16e4}.txt`: one pair header each, result `-3 +0 +3` (what a1 passed to `recovery_ci.py`).
- `analysis.py` / `run_manifest.py` / `guard_report.py` / `recovery_ci.py`: keyed on the prior in the raw file names, not on the tag string (`PAT` lists SRB · SRP; banners via `C.DM_PRIORS`); the `…last` tags of both pools went through the same tools under another tag name.
- Code drift since the a1 runs (99039ef5 / 9ad4caa0 → HEAD): only `ald.py` (regen `hisnr4` set), three `run_fighs*.sh`, `run_srb_eval.sh` — no receiver file. Site-packages of the `torch` env: newest entry 2026-09-27.
- Preconditions after the freeze commit: `git status --porcelain conf/code Demo` shows only `?? conf/code/run_seedsroom16e4.sh`; `DECISIONS.md` tracked + clean now; `__pycache__/` ignored; no `runner.py run` alive.
- GB′ cannot disturb the run: `run_d2_sx.py` resume writes no checkpoint (log line "left untouched"; mtimes unchanged) and writes only `results/d2_gbprime_*` + a log.

**B. The driver / CPU**
- Loop: with a stdin-eating command in the body the here-string loop stops after row 1; with `< /dev/null` it reads 4 rows — the driver has `< /dev/null` on the only stdin-capable command. `exit` inside the loop leaves the script (no subshell).
- `taskset -c 24-47,120-143,72-95,168-191`: `nproc` → 96, Python `os.cpu_count()` → 192, `len(os.sched_getaffinity(0))` → 96; siblings 24↔120, 72↔168, 95↔191 → the mask is NUMA nodes 1 + 3 = 48 whole cores. `runner.py`: `jobs = min(os.cpu_count(), len(tasks))` = 192, fork start method (Python 3.12.14), BLAS threads pinned to 1 by `common.py`, no affinity call anywhere in `conf/code/*.py`. 192 single-thread workers time-share 96 threads: no correctness effect (each chunk regenerates its own stream; the a1 `last` tags replayed genie bit-identically under a different scheduling). Memory is the same as in the a1 runs (192 workers then too); 985 GB available.
- Other load: GB′ processes on CPU 68 / 165 (pairs 68,164 · 69,165, node 2), outside the mask; a4 · a5 trainings stopped 09:15 CDT.

**C. Registration facts**
- §0 against ROOM16e4 §6.1 / 6.2 and PATH16e4 §6.1 / 6.2: table B counts, pooled, POWERED 3/3, V1 −3 dB (704, 812), Wilson intervals (recomputed), b\* / genie −3 dB (827, 299 → 0.323, 0.117; 1356, 428 → 0.530, 0.167), SNR@0.1 gap and CI, R(−3 dB) and CI, a1 best val / epoch (from the checkpoints) — all equal. "baseline 16 개 전부 (i)" = both records' §6.3 "전부" sentences. b\* BLER at −3 / 0 / +3 inside [0.005, 0.9] for both pools; SRB 0 dB 65:38 p 0.01.
- Training times: `logs/seeds_SRP_train.log` 14:20 → 16:47 · 19:20 CDT (GPU 0), `logs/seeds_SRB_train.log` 19:26 → 00:55 · 01:33 CDT (GPU 0 · 2); consistent with checkpoint `wall_sec` (8840 / 9165 / 19760 / 22041 s).
- "Never evaluated by any receiver": no `SR[BP]_N160000_a[2-5]` in any `logs/run_D2_*.log`; the stems appear only in training / GB′ logs.
- Label rule = SEEDSNR16e4 §1 wording (which is SEEDS16e4 §1 in SEEDS3's absolute form, incl. "수용 실패 = 판정 못함").
- 7 SNRs under half the CPU: not a problem. The unmodified `run_seeds16e4.sh` and its acceptance call (no `--points`) require the full C2 grid anyway; cost is the ≈ 5 h above.

## Not verified
- The user quotes in the header; the cites "01_RULES §4" (`--jobs`) and "ROOM16e4 감사 N3".
- The 2× wall-time scaling (no run was made) and per-worker RSS (not logged in the a1 runs).
- Bit-identity of the non-Stage-C arms under the taskset mask — argued from per-chunk determinism and precedent only; the run's own `--ref-arms all` is the test (hence S1).
- SEEDS16e4 beyond its label / acceptance rows; results of the earlier seed registrations as quoted in §0 "선례".
- Whether the session will launch from `conf/` (N6).

## Duration estimate (96 threads, 192 workers)

| tag | a1-pool basis (192 threads) | runner at ½ CPU | + post steps | per tag |
|---|---|---|---|---|
| SRBB16e4s2, s3 | 28.3 min (best), 24.8 min (last); Σ chunk-seconds / 192 = 25.5 / 22.4 min | 50–57 min | ≈ 5 min | **≈ 55–62 min** |
| SRPB16e4s2, s3 | 53.2 min (best, other CPU load present), 41.2 min (last); Σ / 192 = 48.8 / 37.1 min | 82–106 min | ≈ 5 min | **≈ 87–111 min** |

Total sequential **≈ 4.7–5.8 h** (central ≈ 5.2 h; allow ≈ 6.3 h with 10 % time-slicing loss). The draft's 5.5–6.5 h is on the conservative side of the same arithmetic. First chunk lines appear only after ≈ 11–13 min (SRB) / ≈ 11–25 min (SRP) — silence until then is normal.
