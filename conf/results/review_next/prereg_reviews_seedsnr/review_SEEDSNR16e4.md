# SEEDSNR16e4 사전 등록 — 적대적 검토 원문 (Fable 5.1 서브에이전트; 워크플로 wf_cf5580d4-5ec, 앞선 wf_a992325c-df0 은 초안 작성자의 삭제 명령 권한 대기로 멈춰 중지)

## 1회차

### 검토 대상을 만든 작성자 보고 (원문)

The registration draft and the fixed run script are both written. Neither is committed and nothing has been run. The script passes `bash -n`, its flags all match the tools' argparse, and its helper functions pass small tests on scratch data.

**Files**
- `/home/HTJ/t2_wtS/conf/results/review_next/NEXT_EXPERIMENTS_SEEDSNR16e4.md` (new, untracked). It has §0–§5 and an empty §6, with `{{NOW}}` placeholders and one `[주 세션 기입: …]` slot for the user's quote.
- `/home/HTJ/t2_wtS/conf/code/run_seedsnr16e4.sh` (the previous drafter's script, reused and fixed, untracked).
- Scratch: `/tmp/claude-1005/-home-HTJ-t2/6cbef450-8bb7-430d-b07a-4c32854f5588/scratchpad/seedsnr/`

**Design decisions and why**
1. **Arms: the A tag's 11 arms, not V1 + b\* + genie.**
   - Table B and R_dp need b\*, V1 and genie in the same raw; no tool can borrow b\* from the a1 raw, and I wrote no new code.
   - On a 3-arm raw (`raw_U28NR16B16e4last`), `analysis.main` stops with `KeyError: 'R2-ours-G'` (table A's reference arm), so a 3-arm run would break the pipeline.
   - The 8 extra arms cost 6–17 % more (SCALE16e4 last tags vs A × 3/7). In return, all 10 non-V1 arms are replayed against the a1 raw, as in the precedent's `--ref-arms all`.
2. **SNR: only the 3 a1 decision points** (UMi28 C6 0/3/6, UMi28 C9 −3/0/3, D2 C9 −9/−6/−3).
   - The label, R_dp and the trend statements use only these points. They are set by b\*, and b\* must be bit-identical to a1 to pass acceptance.
   - I checked on the a1 raws restricted to these 3 points (symlinked chunks):
     - Table B: same decision points and same counts (232:44, 391:32, 914:29).
     - `frontier_ci`: reproduces the SCALE16e4 R1 and ΔR/S1 lines exactly.
   - Cost: about 22.9 h instead of 53.4 h for all 7 points.
   - Lost (report-only): V1 SNR@0.1 for D2 C9 (V1 is already below 0.1 at −9 dB), R(−3 dB) for UMi28 C6, R\*/Q-OP.
3. **Labels: exactly the SEEDS16e4 form.** Per seed, table B b\*→V1 is (i), (ii)/(iii) or (iv)/training failure. Per cell, the aggregate is "시드 강건 (3/3 (i))", "시드 의존" or "판정하지 못함", counted over 3 seeds including a1.
4. **Statement conditions (fixed in the draft, not labels):**
   - (S1) Each cell's statement either gets "(확산 시드 3/3)" or the caveat "단일 시드 한정".
   - (S2) For each C9 seed: dR(s) = R_C9(seed s) − R_C2(registered a1 raw). The SCALE16e4 (T+) counts as held only if the CI lower bound is > 0 for both seeds, at the level used in SCALE16e4 §6.1.1 (D2 95 %, UMi28 90 %).
   - (S3) The same check for the UMi28 C6 step S1 at 90 %.
   - All conditions must hold together, so no multiplicity correction is needed. The C9 − C6 step is excluded because pairing seeds across cells would be arbitrary.
5. **D2 C9 a3 handling: §3d ladder.** fb2 is used if it does not diverge, otherwise fb3; if both fail, the seed is "학습 실패". Once fb2 succeeds, fb3 is stopped and never opened; the original a3 `_best.pt` is kept but never evaluated.
   - **This departs from the precedent:** SEEDS16e4 and SEEDS3 counted a diverged seed as a failure, with no ladder.
   - Justification: the D2 C6 a1 in the same trend is itself an fb2 checkpoint, made after the same late divergence. fb2 keeps a3's seed and only adds gradient clipping, and the choice between fb2 and fb3 follows a fixed number rule, not val loss or BLER.
   - The precedent-rule label is also recorded for D2 C9, as report-only.
6. **Batches.**
   - Batch 1 runs at run commit 1 with 5 seeds; `NR32B16e4s3` has no SEED line yet, so it is skipped as PENDING. Estimate about 18.5 h.
   - Once the ladder resolves, a §5 addendum becomes run commit 2 and batch 2 runs with `--resume` (about 4.7 h).
   - If the ladder resolves before run commit 1, a single batch is enough.
7. **Regression check `U28NR16B16e4chkS`, about 19 min.** It reruns the SCALE16e4 chk command and must be bit-identical, otherwise the whole run aborts. It is needed because the seed tags' replay check cannot catch drift in the V1 path.
8. **Acceptance:**
   - per-tag eval_accept checks: chunk plan, meta, ckpt sha/role, genie replay, grid;
   - the `--ref-arms all` gate: only V1 may differ, 2560/2560 shared;
   - decision points equal to a1's; memory-guard check (k) for C9;
   - one clean commit per raw;
   - code identical to the freeze commit and to b4433d3c except this script.
   C9 runs use `--worker-gb 8.0`.
9. **§5 values are pre-filled** (sha, epoch, best val, σ tag and split hash identical to a1) for the 5 seeds that are ready. A `seedsnr_s5.txt` draft is in §5.
10. **Script changes from the previous draft:**
    - added S1(s) for UMi28 C6;
    - changed `frontier_ci --level 0.90` to `0.95`, which prints both the 90 % and 95 % lines;
    - the main loop now reads its input on fd 3, so no command inside it can consume stdin.

**Open items**
1. Applying §3d against the SEEDS16e4/SEEDS3 "no ladder" rule is a research call. I recommend the main session either gets the user's confirmation or records the reasoning in DECISIONS.
2. Fill in the user's quote and time, the `{{NOW}}` placeholders, and the DECISIONS freeze line (§5 lists what it should contain).
3. **Do not merge main into scale before the freeze.** The script requires that the only code change since b4433d3c is this script, so main's figure scripts would make it abort.
4. Before run commit 1, create the 7 fits links: 6 seed tags plus chkS.
5. When fb2 finishes successfully, stop fb3 with SIGINT and do not open it.
6. The Fable adversarial review still needs to run, followed by v2.

### 렌즈 stats-fair

#### 반드시
- **[M1]** §1 시드 강건성 라벨 행 · 문장 조건 (S1)(S2) · §2 표 · §6 전사 규칙 (D2 C9 사다리 한정어)
  - 문제: D2 C9 의 a3 가 등록 규칙(§3d)으로 fb2/fb3 체크포인트가 되면 그 시드는 a1·a2 와, 그리고 SEEDS16e4·SEEDS3 의 모든 시드와 레시피가 다르다(클리핑 1.0, fb3 는 + lr/3; ckpt 메타 a1·a2 grad_clip 0.0 확인). 그런데 §1 의 집계 라벨 문자열 "시드 강건 (3/3 (i))" 과 (S1) 의 접미 "(확산 시드 3/3)", (S2) 의 "유지 (2/2)" 는 선례 문자열과 글자가 같아, §6·EXPERIMENTS·RESULTS 를 읽는 사람은 세 시드 중 하나가 수리된 시행임을 알 수 없다 — 같은 자료가 선례 규칙(SEEDS16e4 §1 "사다리 없음")이면 "판정하지 못함 (2/3 (i), 1 판정 못함)" 으로 읽혔을 것이다. 선례 규칙 라벨 병기는 '보고 전용' 이라 라벨 자체에는 남지 않는다. 또 (S1) 의 "붙일 수 있다" 는 재량을 남긴다. 결과가 라벨을 고르는 문제는 아니지만, 라벨·문장이 선례와 같은 주장으로 읽히는 불공정한 표현이다.
  - 수정: §1 라벨 행 끝에 추가: "**사다리 한정어 (라벨 문자열의 일부; 보고 전용 아님)**: 어느 셀의 시드가 §3d 시행 2·3 의 체크포인트이면 그 시드의 §2 라벨과 그 셀의 집계 라벨에 `; a<s> = §3d fb<k>` 를 붙인다 — 예: D2 C9 \"시드 강건 (3/3 (i); a3 = §3d fb2)\". 한정어 없는 \"시드 강건 (3/3 (i))\" 은 세 시드가 모두 시행 1 일 때만 쓴다(SEEDS16e4·SEEDS3 문자열과 같은 뜻을 유지). §6 표·EXPERIMENTS 행·RESULTS 인용은 모두 이 문자열을 그대로 쓴다. §6 에서 D2 C9 는 등록 라벨(사다리)과 선례 규칙 라벨을 같은 표의 두 열로 나란히 적는다." (S1) 문장을 다음으로 교체: "셀 라벨이 \"시드 강건 (3/3 (i))\" 이면 SCALE16e4 §6.1.3 의 그 셀 표 B 문장에 \"(확산 시드 3/3)\" 을 **붙인다**; 라벨에 사다리 한정어가 있으면 \"(확산 시드 3/3; a<s> = §3d fb<k> 클리핑)\" 으로 붙인다. 아니면 …(이하 그대로)". (S2) 문장을 "SCALE16e4 1차 (T+) 는 C9 확산 시드 a2·a3 에서도 유지된다 (2/2[; a3 = §3d fb<k>])" 로. §2 표의 "학습 실패" 행 위에 한 행 추가: "(i)–(iv) 가 §3d 시행 2·3 의 체크포인트에서 나온 경우 | 같은 문자열 + \"; a<s> = §3d fb<k>\"".
- **[M2]** §3 예측 4–8 (채점 가능성)
  - 문제: 예측 4·5·6 "두 시드 모두", 7 "여섯 시드 태그 모두", 8 "셀마다 세 시드" 는 NR32B16e4s3 가 "학습 실패"(fb2·fb3 모두 실패) 이거나 어느 태그가 수용 실패일 때 적중·빗나감 어느 쪽도 아니게 되고, 그때 채점자가 사후에 범위를 정하게 된다(13(c) 는 경로만 적고 채점 규칙이 없다). SEEDS3 §3 은 채점 제외 항목을 미리 표시했다.
  - 수정: §3 머리말 끝에 추가: "**채점 규칙(미리 고정)**: 예측 4–8 은 라벨 대상 태그(학습 성공·수용 통과)에 대해서만 채점한다. 학습 실패·수용 실패 태그가 있으면 그 태그를 뺀 나머지로 적중/빗나감을 정하고 \"(n/6 태그 채점)\" 을 옆에 적는다; 어느 셀의 라벨 대상 태그가 하나도 없으면 그 셀의 항목은 \"채점 불가 (사유)\" 로 적고 적중·빗나감 합계에 넣지 않는다. 예측 1–3·10–12 는 그대로 이분 채점한다(학습 실패는 1–3·10·11 의 빗나감)." 예측 7 의 "여섯 시드 태그 모두" → "라벨 대상 시드 태그 모두", 예측 8 의 "세 시드 R_dp" → "라벨 대상 시드(a1 포함)의 R_dp".

#### 권고
- §1 학습 실패 행: fb3 처리에 "fb3 가 fb2 보다 먼저 끝나더라도 그 로그·ckpt·`# done` 줄을 읽지 않으며, SIGINT 뒤 gpuq 재큐·재개를 하지 않는다(gpu_sched.sh:20 은 rc 만 기록하고 자동 재큐가 없다 — 재큐는 사람이 한다)" 를 덧붙일 것. 선택은 번호 규칙이라 결과 선택 여지는 없지만 '열지 않음' 이 지금 문구로는 fb3 가 먼저 끝난 경우를 덮지 못한다.
- §1 학습 실패 행의 인용 정리: `aborted` → 재개 규칙의 출처는 01_RULES §4 Fallback 표 '학습 도중 중단·재시작'(:59) + score.py:1034 (KeyboardInterrupt → aborted=True, '01_RULES §5: not an attempt') + SCALE16e4 §1 학습 실패 행(integ-3 "`diverged` 만 §3d, `aborted` 는 재개") 이다. DECISIONS 6953d595 와 C6B16e4 §1 은 'aborted=True → fb3/사다리' 로 적혀 있어 이 등록과 다르므로, "SCALE16e4 §1 이 6953d595 의 aborted 조항을 대신한다" 를 한 줄 명시할 것.
- §1 묶음 행·§5: 실행 커밋 2 가 "§5 의 그 칸만" 이라고 하지만 §4.1 표(fb2/fb3 종료·쓴 시행)와 §4.3 현황도 그때 갱신해야 한다(§4 는 '갱신한다' 절). 스크립트는 REG 가 추적·청결이기만 요구하므로 "실행 커밋 2 = §5 칸 + `seedsnr_s5.txt` 줄 + §4 갱신 (§1~§3 불변)" 으로 고칠 것.
- 2 묶음의 회귀 검사: `--resume` 에서 chkS raw 가 완전하면 `run` 이 건너뛰어 2 묶음(며칠 뒤)의 V1 경로 drift 는 검사되지 않는다(비-V1 10 arm 은 시드 태그의 (b) 게이트가 잡는다). 비용 ≈ 19 분이므로 2 묶음용 태그(예: `U28NR16B16e4chkS2`, 같은 명령·같은 fits 링크)를 두거나, 1 묶음으로 끝나지 않으면 chkS 를 새로 돈다고 적는 것을 권한다. Nr 32 V1 경로(모델 차원 256)는 chkS 가 덮지 않는다 — `raw_NR32B16e4chk`(D2 C9 −12 dB 청크 0) 재생을 더하면 덮인다(선택).
- 스크립트 후처리 파일(`seedsnr_dR_<X>.txt`·`<X>_accept.txt`·`_refarms.txt`·`recovery_<X>.txt`)은 2 묶음에서 1 묶음 태그에 대해 다시 써지고 머리말의 `git $H` 는 실행 커밋 2 가 된다. §1 실행 스크립트 행에 "머리말 git 은 후처리 시점 커밋이며 raw 의 `run|git` 이 실행 커밋이다" 를 적거나, 머리말에 raw 의 `run|git` 을 함께 찍을 것(misrecord 예방).
- (S2)(S3) 문장에 SCALE16e4 의 G_d·Q-K·Q-OP 한정어를 '그대로' 붙이는데 Q-OP(R*@0.05)는 a1 V1 에서 계산된 값이다. "a1 의 한정어를 인용으로 붙인다(시드별 재계산 없음)" 로 표현을 바꿀 것.
- §0 R_dp 출처 `recovery_<T>.txt:8` 은 세 파일 모두 pooled 줄로 확인됐으나, NR32 파일은 −3 dB 줄이 두 번(첫 호출 `--snrs -3` + 둘째 호출) 있어 줄 번호 인용이 깨지기 쉽다 — "pooled 3 SNRs 줄" 로 인용할 것.
- §1 회귀 검사 행의 chkS 와 §4.3 fits 링크 7 개는 실행 커밋 1 전에 만들어야 하며(스크립트 :57·:68 이 die), 링크는 미추적이라 동결 커밋에는 들어가지 않는다 — §4.3 에 "생성 시각은 `ls -la --time-style` 로 적는다" 를 더하면 감사가 쉽다.

#### 확인
- 스크립트 전제·형식 (읽기만, 실행 없음): eval_accept.py:125-127 의 replay 줄 형식 `  <tag> ('C', s): replay vs raw_<T> (all): shared n/n, arms differing [...] (max |diff| x)` 가 `refok` 정규식과 일치(실례 `results/review_next/U28B16e4s2_refarms.txt`·main `D3B16e4s2_refarms.txt`); 머리말은 `ACCEPT: OK -- <tags>` / `ACCEPT: FAILED` (:144). `dp` 정규식을 작성자 scratch 3 점 표 3 개와 a1 7 점 표 3 개에 돌려 블록 1 개·'-9 -6 -3'/'0 3 6'/'-3 0 3' 확인. frontier_ci.py:219-222 는 `--level 0.95` 에서 90 %·95 % 줄을 함께 찍고(scratch `frontier3_*.txt` 가 SCALE16e4 D2 +0.302 [95% +0.254, +0.355]·UMi28 S1 +0.137 [90% +0.085, +0.193] 재현), `--recovery RAW:CELL:SNRS` 형식은 run_scale2.sh 의 SD2/SU6/C2 spec 과 같다. argparse: eval_accept `--nr --points --ref-arms --fits-dir --grid --n`, runner `--worker-gb --snr(nargs+ float) --arm --stagec-ckpt --tag`, recovery_ci `--snrs(nargs+ float)` 모두 존재.
- git 전제: `git diff --name-status` 는 cwd conf/ 에서도 저장소 루트 상대 경로(`conf/...`)를 찍고 `diff.relative` 미설정 → 동결 뒤 정확히 `A\tconf/code/run_seedsnr16e4.sh` 한 줄이 된다; 현재 `git diff --name-status b4433d3c HEAD -- code ../Demo` 는 비어 있고 `git status --porcelain code ../Demo` 는 `?? conf/code/run_seedsnr16e4.sh` 만. `../Demo` 디렉터리 존재. raw 의 `run|git` 은 짧은 해시(`b4433d3c`) → `gitok` 의 `startswith` 동작; a1 C9 raw 에 `meta|jobs 99`·`meta|worker_gb 8.0` 존재(수용 (d)).
- a1 자료: raw_U28NR16B16e4·raw_U28NR32B16e4·raw_NR32B16e4·raw_U28B16e4·raw_B16e4k 각 448 파일, raw_U28NR16B16e4chk 1 파일; `scale2_s5.txt` CELL 줄 11 필드(ST BSHA LSHA BS KK LL FK KR K2K K2LL CKK)와 `s2c` 의 read 순서 일치; a1 `_best.pt` sha16 3 개가 CELL 줄과 일치(34136808b1e367ac·463da87aa8dbfb61·3cf5d3eff96f0341).
- §5 값: 시드 5 개의 `_best.pt`/last `.pt` sha16 10 개가 §5·s5 초안과 모두 일치(sha256sum). torch.load(CPU) 메타: epoch/best_epoch/best_val/sigma_tag/split_hash/grad_clip 0.0/lr 0.002238046051591068 이 §5 표의 모든 칸과 일치(UMi28 C6 a2 847/847/0.5221701264381409 U28NR16g 83e08c3911e52fc3; a3 615/615; UMi28 C9 a2 446/446, a3 917/917 U28NR32 01735b4ef4b87ff8; D2 C9 a2 318/318 NR32 3669354ecf3a9f00); a1 셋도 §0 best val 과 일치(0.5224766·0.3923236·0.0988171). last `.pt` 의 stopped_by 는 모두 patience.
- §4.1 표: gpu_sched.log:53-56,58,60,67,68,70-74,90,91 의 명령·시각과 일치(a2·a3 10-01 00:52–03:34 CDT 투입; U28NR16 a3 SIGINT 06:25, 재개 06:34, 종료 07:37; NR32 a3 종료 08:33; fb2·fb3 10-03 18:12 CDT GPU 0·1). 학습 로그: U28NR16 a3 `491 epochs, stopped_by=interrupted, aborted=True` → 재개 머리말 `2026-10-01 20:41:30 KST`(= 06:41:30 CDT) → `635 epochs, stopped_by=patience`; NR32 a3 `1240 epochs, stopped_by=diverged, best 9.599885e-02 @1235`. fb2·fb3 프로세스는 지금 실행 중(pgrep; ckpt mtime 10-04 12:16 KST) — fb3 로그는 열지 않았다.
- §3d 같은 시드 주장: train_nr16.py:54-65 는 `--fallback` 으로 `grad_clip`·`lr` 만 바꾸고 같은 rung·attempt 를 score.train 에 넘긴다; score.py:900-905 의 생성기 시드 = SEED_TRAIN + rung_ix·17 + attempt (+7919/+104729) 로 fallback 무관; GRAD_CLIP_LADDER (0.0, 1.0, 1.0)·LR_DIV_LADDER (1.0, 1.0, 3.0) (score.py:821-822). 사다리 선택 규칙 '번호가 가장 낮은 성공 시행·나머지는 열지 않음' 은 SCALE16e4 §1 학습 실패 행(:149)·DECISIONS 6953d595 와 일치; 주 세션 결정은 main WORK_QUEUE.md:25 "NR32 a3 diverged → 시드 등록 시 §3d fb2".
- §0·§1 수치: 표 B 계수 914:29 / 232:44 / 391:32 와 판정점이 a1 표(`tables_D2_<T>.txt`)·3 점 scratch 표 모두에서 같다; R_dp pooled 줄 0.811 [0.790, 0.832] / 0.287 [0.253, 0.322] / 0.432 [0.402, 0.462] 가 `recovery_<T>.txt` 와 일치. 비용 산술: A 태그 120.8/820.0/661.9 분·last 44.2/325.1/266.7·chk 18.8 분이 SCALE16e4 §6.1 runner 표와 일치; 2×(51.8+351.4+283.7) = 22.9 h, 1 묶음 ≈ 18.5 h, 2 묶음 ≈ 4.7 h.
- 선례 정합: 라벨 (i)–(iv)·집계 문자열·분모 3·'단일 시드 한정' 캐비엇은 SEEDS3 §1·§2 / SEEDS16e4 §1 과 같다; (S2) 의 데이터셋별 수준(D2 95 %, UMi28 90 %)은 SCALE16e4 §1 다중성 행(Holm m=2, 동률이면 D2 첫째 95 %)과 일치; analysis._present(analysis.py:200-205)는 raw 에 있는 SNR 점만 격자로 쓰므로 3 점 raw 에서 arm 결손이 없고, load_raw 경고는 청크 구멍·키 결손에만 난다(:138,167) — 작성자 3 점 표에 경고 없음; run_manifest 는 파일 수를 세기만 한다(448 기대 없음). 선례 run_scale2.sh 의 K2·last 수용이 3 점 raw 를 7 점 a1 raw 와 `--points` 로 대조해 통과한 바 있다(eval_accept 는 태그 raw 의 점만 순회, :74-95).

### 렌즈 integ

#### 반드시
- **[integ-1]** run_seedsnr16e4.sh:37, :57, :82–87, :138–144 · 등록 §1 회귀 검사 행 · §1 수용 (e) · §1 비용 행 · §4.3 fits 링크 행
  - 문제: 회귀 검사 chkS 가 2 묶음(실행 커밋 2, `--resume`)에서는 돌지 않는다. `raw_U28NR16B16e4chkS` 는 1 묶음에서 완성(1 파일, `run|git` = 실행 커밋 1)되므로 `run()` 이 "skip: raw complete" 로 건너뛰고 `acc $CHK` 는 묵은 raw 를 다시 수용해 `accept chkS OK` 를 2 묶음 로그에 남긴다 — 실행 커밋 2 의 코드·환경에서 V1 경로를 재현한 적이 없는데 게이트 (e) 가 통과한 것으로 기록된다(misrecord). 등록 §1 회귀 검사 행의 근거("시드 태그의 `--ref-arms all` 은 V1 경로 drift 를 잡지 못한다")가 NR32B16e4s3 의 실행에는 적용되지 않아 다른 다섯 시드와 검사 수준이 다르다. 코드는 (f) 로 동일하지만 환경(torch·numpy)은 묶음 사이 며칠 동안 바뀔 수 있고, 그것이 chk 를 두는 이유다.
  - 수정: 스크립트 — :57 의 링크 검사 줄을 지우고, gitok 정의 끝(:81 `}` 다음, :82 `for X in $CHK $TAGS` 앞)에 다음 세 줄을 넣는다:
```
# one fresh chk per run commit: a complete raw_$CHK whose run|git is another commit (= a batch-1 raw) means batch 2 -> tag ${CHK}2 (own fits link)
[ "$(nraw $CHK)" -eq 1 ] && ! gitok $CHK && CHK=${CHK}2
[ "$(readlink -f results/gmm_fits_D2_$CHK)" = "$(readlink -f results/gmm_fits_D2_U28NR16B16e4)" ] || die "fits link gmm_fits_D2_$CHK -> gmm_fits_D2_U28NR16B16e4 missing"
```
:89 의 start 로그에 `chk $CHK` 를 추가: `log "start (git $H, freeze $FREEZE, resume $RESUME, chk $CHK, WGB $WGB (run $WGBR), CUDA_VISIBLE_DEVICES='$CUDA_VISIBLE_DEVICES')"`. 머리말 :6 에 `(batch 2 = run commit 2 uses U28NR16B16e4chkS2)` 를 덧붙인다.
등록 §1 회귀 검사 행 끝에 추가: "**실행 커밋(묶음)마다 1 회**: 2 묶음에서는 `raw_U28NR16B16e4chkS` 의 `run|git` 이 HEAD 가 아니므로 스크립트가 태그 `U28NR16B16e4chkS2` 로 같은 명령을 다시 돌린다(링크 `gmm_fits_D2_U28NR16B16e4chkS2` → `gmm_fits_D2_U28NR16B16e4`; 비용 ≈ 19 분 추가). 사다리가 실행 커밋 1 전에 닫혀 한 묶음이면 chkS2 는 없다." §1 수용 (e) 를 "회귀 검사 chkS(2 묶음은 chkS2) 비트 동일(실패 = 전체 ABORT)" 로, §1 비용 행의 "chkS ≈ 0.3 h" 를 "chkS 묶음마다 ≈ 0.3 h", "2 묶음 ≈ 4.7 h" 를 "2 묶음 ≈ 5.0 h" 로, §4.3 "fits 링크 7 개 (`gmm_fits_D2_<T>s{2,3}` 6 + `gmm_fits_D2_U28NR16B16e4chkS`)" 를 "fits 링크 8 개 (… 6 + `gmm_fits_D2_U28NR16B16e4chkS` + `gmm_fits_D2_U28NR16B16e4chkS2`)" 로 고친다. §1 묶음 행의 2 묶음 설명에 "(chkS2 포함)" 을 넣는다.

#### 권고
- §1 실행 위치·커밋 행의 "**동결 전** main → scale 병합 금지" 는 범위가 짧다. 스크립트는 시작마다(1·2 묶음 모두) `git diff --name-status b4433d3c HEAD -- code ../Demo` = 이 스크립트 한 줄을 요구하고, 현재 main 은 scale 과 `conf/code` 가 11 파일 다르다(arms.py·eval_accept.py·runner.py·pair_baselines.py 수정 + figure_f30/31/32.py·run_sparse*.sh·sparse_tune.py 추가: `git diff --name-status HEAD main -- conf/code`). → "**마지막 묶음의 `SEEDSNR_DONE` 까지** main → scale 병합 금지(병합하면 ABORT → 새 동결)" 로 바꾸고 §4.2 열린 항목 3 에도 같은 범위를 적을 것.
- 2 묶음 `--resume` 는 1 묶음에서 끝난 다섯 태그의 뒤 단계(analysis·manifest·guard·recovery·accept·refarms·dR)를 다시 돌려 결과 파일을 덮어쓴다. 값은 결정적이지만 머리말이 바뀐다: `seedsnr_dR_<X>.txt` 의 `git $H` 와 `run_manifest_<X>.json` 의 `git_commit`(= 뒤 단계 시점 HEAD = 실행 커밋 2)·`written` 이 raw 의 `run|git`(실행 커밋 1) 과 달라진다. → :169 머리말을 `git $H (raw run|git: $(…첫 청크의 run|git…))` 로 하거나, 더 간단히 등록 §1 묶음 행에 "뒤 단계 산출물의 git 은 그 단계를 돌린 커밋이고 raw 의 실행 커밋은 manifest `run.git` 과 §6 raw 표에서 읽는다" 를 한 줄 적어 §6 전사 때 혼동을 막을 것.
- §3d 사다리를 선례(SEEDS16e4·SEEDS3 "사다리 없음")와 다르게 쓰는 것은 §4.2 #1 대로 동결 전 사용자 확인 또는 DECISIONS 근거가 필요하다(연구 판단; 이 검토는 판정하지 않음). 그와 별개로 D2 C9 의 집계 라벨 문자열 자체에 레시피 차이가 보이게 할 것: §1 시드 강건성 라벨 행에 "D2 C9 의 a3 가 fb2/fb3 이면 집계 라벨에 `; a3 = §3d fb<k>` 를 붙인다 (예: "시드 강건 (3/3 (i); a3 = §3d fb2)")" 를 추가. 선례 규칙 병기(보고 전용)만으로는 라벨만 인용될 때 fb2 가 숨는다.
- frontier dR 의 C2 끝 raw(`raw_B16e4k` 448, `raw_U28B16e4` → main 링크 448)를 전제 검사에 넣을 것 — 지금은 링크가 깨지면 실행 도중 `frontier dR <X> rc≠0` 으로만 드러나 FAIL 로 세어진다. :57 근처에 `for r in raw_B16e4k raw_U28B16e4; do [ "$(ls $r/D2_C2_*.npz 2>/dev/null | wc -l)" -eq 448 ] || die "$r: not 448 C2 chunk files (C2 end of dR)"; done`.
- (선택) chk 는 UMi28 C6(Nr 16) 한 셀만 재현한다. Nr 32 V1 경로(입력 256 차원)는 코드가 같아 drift 를 대체로 공유하지만, 완전한 재현을 원하면 `NR32B16e4chk` 재실행(SCALE16e4 실측 92.2 분, 워커 1·가드 8.0)을 추가할 수 있다. 비용 대비 가치가 작아 선택.
- :157 `st` 메시지는 실패해도 "'…' == a1 '…'" 로 찍힌다(rc 로만 구분). 전사 혼동을 줄이려면 `[ "$D" = "${DP//,/ }" ]; rc=$?; st $rc "decision SNRs $X (anchor b*, never by hand): '${D:-none}' vs a1 '${DP//,/ }'"; DOK=$rc` 로.

#### 확인
- 플래그: 스크립트가 쓰는 플래그 전부가 scale 의 argparse 에 있다 — eval_accept.py:45–62 (--tag --ntrain --kron-K --ll-val --n --points --ref-raw --fits-dir --grid --nr --ref-arms --prior --bstar), runner.py:1187–1254 (run/analysis, --testbed --cell --snr --prior --n --chunk --arm --ntrain --stagec-ckpt --worker-gb --tag), frontier_ci.py:326–328 (--recovery --level), recovery_ci.py:47–49, run_manifest.py:37, guard_report.py:81–82. `bash -n` 통과(이 검토가 실행).
- §5 값: 다섯 시드 `_best.pt` sha256[:16] (f956a85c82ed4fb3 · 9c38545ab009f307 · c11bb951ff7be4d4 · 7f72480c42fcd6c9 · 0c887ee786ff9dfa) 와 last sha (e26ed7c3… 0a4592e3… a6331677… ac384d5f… 8d9c5f0c…) 가 `sha256sum` 과 일치; `torch.load`(CPU) 로 epoch/best_epoch/best_val/stopped_by/sigma_tag/split_hash/grad_clip 0.0/lr 0.002238046051591068/role 이 §5 표와 전부 일치; a1 세 `_best` sha = scale2_s5.txt CELL 줄(34136808b1e367ac · 463da87aa8dbfb61 · 3cf5d3eff96f0341), a1 best @642/@232/@230 = §0.
- §4.1: `logs/gpu_sched.log:53–58,60–61,67–68,70–74,90–91` 의 명령(--attempt 2|3 --fallback 1 --no-gbprime; fb2 --fallback 2, fb3 --fallback 3)·시각이 표와 같다; 학습 로그 `# done` 줄 — NR32 a2 338/@318 patience, a3 1240/@1235 diverged, U28NR16 a2 867/@847, a3 491 interrupted aborted=True → 재개 머리말 `2026-10-01 20:41:30 KST`(= 06:41:30 CDT) → 635/@615 patience, U28NR32 a2 466/@446, a3 937/@917. 재개: 첫 구간은 epoch 490 까지만 기록되고 `epoch  491` 줄은 로그 전체에 한 번(506 행) — 공개 내용과 일치.
- 수용·게이트 코드: eval_accept 는 `--points` 로 want 집합을 바꾸고(3 점 raw 와 7 점 ref raw 비교 가능), `run|git` 을 HEAD 와 대조하지 않으므로 새 커밋의 chkS 가 비트 동일이면 `ACCEPT: OK` 가 된다; `--ref-arms all` 출력 줄 형식(`B16e4s2_refarms.txt`)이 `refok` 정규식과 맞는다 — 실제 형식에서 만든 scratch 입력으로 V1 만 다름 rc 0, b* 포함/shared 2559/여분 줄 rc 1, `ACCEPT: OK` rc 0 (`scratchpad/seedsnr/rev/`). `dp` 정규식은 a1 7 점 표와 초안 작성자의 3 점 표 모두에서 블록 1 개·`-9 -6 -3` / `0 3 6`.
- 3 점 부분집합 재현: 작성자 scratch `an/tables3_*` 의 판정점·표 B 계수(232:44 · 391:32 · 914:29, POWERED 3/3)가 7 점 표(tables_D2_*:308–311/305–308)와 같다; `frontier3_NR32.txt` 가 `scale2_primary_D2_L95.txt:3–6` 과 숫자까지 같고 `frontier3_U28NR16.txt` 90 % 줄이 `scale2_step_U28_S1.txt:3–5` 와 같다; frontier_ci 는 90 % 줄(:219)을 항상 찍고 `--level` 줄(:222)을 더 찍는다 → (S2)(S3) 가 읽을 수준이 모두 출력된다. R_dp §0 값 = `recovery_<T>.txt:8` (0.287 [0.253, 0.322] · 0.432 · 0.811).
- (S2) 수준: SCALE16e4 §6.1.1 (:509–511) 동률 → D2 첫째 95 %, UMi28 둘째 90 % — 초안의 D2 95 %·UMi28 90 % 가 맞다. C2 끝·명령형은 run_scale2.sh 1차·S1 줄과 같다(raw_B16e4k:C2:-3,0,3 · raw_U28B16e4:C2:3,6,9).
- 실행 위치·커밋: ~/t2_wtS 브랜치 scale HEAD 8992254c; `git diff --name-status b4433d3c HEAD -- conf/code Demo` 가 비어 있어 동결 커밋 뒤 정확히 `A conf/code/run_seedsnr16e4.sh` 가 된다; a1 raw 3 개 448 파일, raw_B16e4k(실디렉터리 448)·raw_U28B16e4(→ main 링크 448) 존재; `raw_*s2/s3`·`raw_*chkS` 는 두 트리 어디에도 없음; scale2_s5.txt 의 CELL 11 필드·WGB 8.0·FREEZE 16a9dff6… 가 `s2c` 필드 순서와 맞는다; 필요한 fits 링크 8 개(위 integ-1 포함)는 아직 없고 스크립트가 대상 일치를 검사한다.
- 시드·사다리: score.py:900 시드 = SEED_TRAIN + _rung_ix(rung)·17 + attempt (fallback 무관 → fb2 = a3 시드), GRAD_CLIP_LADDER (0,1,1)·LR_DIV_LADDER (1,1,3) (:821–822), train_nr16.py 체크포인트 이름 `_a3_fb<k>{,_best}.pt`; 규칙 원문 — SCALE16e4 §1 학습 실패 행(:149) "fb2·fb3 병렬, 번호가 가장 낮은 성공 시행, 나머지 열지 않음, aborted=True 는 시도가 아니며 재개", DECISIONS 6953d595 "fb3 는 시행 2 가 diverged/aborted 일 때만, val 비교 없음", WORK_QUEUE.md:25 "NR32 a3 diverged → 시드 등록 시 §3d fb2". 초안은 SCALE16e4 문구(aborted → 재개)를 따르며 그 차이를 공개했다. fb2·fb3 체크포인트는 계속 쓰이고 있고(mtime 10-04 12:19 KST) gpuq.txt 는 비어 있다(둘 다 이미 launch, gpu_sched.log:90–91); 이 검토는 fb3 의 로그·sha 를 열지 않았다.
- chkS 명령 = SCALE16e4 chk 명령 원문(`logs/run_D2_U28NR16B16e4chk.log:1`: --prior UMi28 --cell C6 --stagec-ckpt …a1_best.pt --n 40 --chunk 40 --snr -3 --arm <11 arm 같은 순서>), 1 태스크·1 워커, 18.8 분(:9); 수용 호출도 SCALE16e4 §1 수용 (b) chk 형식과 같다.
- 비용·메모리: SCALE16e4 runner 표(:441/:447/:453 A 120.8/820.0/661.9 분, :446/:452/:457 last 44.2/325.1/266.7 분) → ×3/7 = 51.8/351.4/283.7 분, 1 묶음 ≈ 18.5 h·총 ≈ 22.9 h 산술 맞음; `--worker-gb` → `meta|jobs`·`meta|worker_gb` (runner.py:649–655), `kchk`·`acc`·`dp`·`run` 은 run_scale2.sh 와 같은 본문; common.CELLS C9 = (−12..6), C6 = (−3..15), KEYS_RAW 7 키.
- 스크립트 흐름: 본 루프 입력 fd 3, `read -u 3`; PENDING(SEED 줄 없음)·`-`(학습 실패) 분기와 끝 줄 `SEEDSNR_DONE … pending= trainfail=` 이 등록 §1 묶음·실행 스크립트 행과 일치; `--resume` 없이 기존 raw 가 있으면 ABORT, 부분 raw 는 `gitok`(모든 청크 `run|git` 이 HEAD 접두)일 때만 이어 감; `run()` 이 HEAD 이동 시 ABORT; 음수 SNR(`--snr -9 -6 -3`, `--points C9:-9,-6,-3`)은 argparse 음수 처리와 SCALE16e4 실측(NR32B16e4last)으로 문제 없음.

## 2회차

### 검토 대상을 만든 작성자 보고 (원문)

Round 2 is applied: all three must items (M1, M2, integ-1) are in the registration doc and the run script, and a review-round summary bullet is now line 4 of the doc header. Everything else is unchanged and the `{{NOW}}` placeholders are kept. `bash -n` passes on the script. I tested the new chk-selection lines in a scratch git repo (exact lines copied out of the script) but did not run the script itself. Nothing was committed and no GPU was used.

Files:
- /home/HTJ/t2_wtS/conf/results/review_next/NEXT_EXPERIMENTS_SEEDSNR16e4.md
- /home/HTJ/t2_wtS/conf/code/run_seedsnr16e4.sh (still untracked)
- Copy of the doc before this round: /tmp/claude-1005/-home-HTJ-t2/6cbef450-8bb7-430d-b07a-4c32854f5588/scratchpad/seedsnr/NEXT_EXPERIMENTS_SEEDSNR16e4.before_round2.md
- Scratch test: /tmp/claude-1005/-home-HTJ-t2/6cbef450-8bb7-430d-b07a-4c32854f5588/scratchpad/seedsnr/chk2test/

**M1 (doc)**
- The §1 label row now ends with the ladder-qualifier rule, as drafted.
- (S1): "붙일 수 있다" became "**붙인다**", plus the qualified form `"(확산 시드 3/3; a<s> = §3d fb<k> 클리핑)"`.
- (S2): the string is now `(2/2[; a3 = §3d fb<k>])`.
- §2 table: a new row "(i)–(iv) 가 §3d 시행 2·3 의 체크포인트에서 나온 경우" sits above the 학습 실패 row.

**M2 (doc)**
- The scoring rule, fixed in advance, is a paragraph right after the §3 heading.
- Prediction 7 now reads "라벨 대상 시드 태그 모두" and prediction 8 reads "라벨 대상 시드(a1 포함)의 R_dp 의 산포".

**integ-1 (script)**
- I removed the old link check at line 57.
- After `gitok` I added the three lines from the review: the comment, `[ "$(nraw $CHK)" -eq 1 ] && ! gitok $CHK && CHK=${CHK}2`, and the fits-link check on `$CHK`.
- The start log now includes `chk $CHK`, and header line 6 now mentions batch 2 using `U28NR16B16e4chkS2`.

**integ-1 (doc)**
- The §1 regression-check row now says chk runs once per run commit (chkS2 in batch 2, link, +19 min).
- The batch row says "(chkS2 포함)", and acceptance (e) says "chkS(2 묶음은 chkS2)".
- Cost row: chkS is ≈ 0.3 h per batch, and batch 2 goes from ≈ 4.7 h to ≈ 5.0 h (283.7 + ~19 min).
- §4.3 now lists 8 fits links.

Scratch test results:

| Situation | Result |
|---|---|
| No chkS raw | chkS |
| chkS raw written by HEAD (batch-1 resume) | chkS |
| chkS raw from another commit, no chkS2 link | ABORT (precondition) |
| chkS raw from another commit, chkS2 link present | chkS2 |

Formatting choice: new strings containing `<s>`/`<k>` outside the label-row qualifier are in backticks. Raw `<s>` is an HTML strikethrough tag in markdown and `<k>` would be dropped. The words are exactly the review's. Pipe counts in every table row are consistent.

Gaps I left alone because they are outside the must list:
1. Prediction 3 still points to "시드 강건 (3/3 (i))" with no ladder qualifier. If a3 = fb2, the real D2 C9 label will be "시드 강건 (3/3 (i); a3 = §3d fb2)", so the arrow text won't match it.
2. Prediction 9 (D2 C9 a2 R_dp) is not covered by M2's rule, which names only 4–8 and 1–3·10–12. If a2 fails acceptance, how to score it is not decided.
3. The script row's flow text "(0) chkS run" and its precondition "fits 링크(시드 태그·chkS)" don't mention chkS2.

The main session still needs to create the `gmm_fits_D2_U28NR16B16e4chkS2` link before batch 2. The script will ABORT without it, and can be fixed and resumed without approval.

### 렌즈 stats-fair

#### 반드시
- (없음)

#### 권고
- §3 예측 3 화살표: `→ "시드 강건 (3/3 (i))"` → `→ "시드 강건 (3/3 (i)[; a3 = §3d fb<k>])"` (굵은 본문 "D2 C9 a2·a3 표 B 모두 (i)" 로 채점하면 이분은 되지만, a3 = fb2 일 때 실제 라벨 문자열과 화살표가 어긋남).
- §3 채점 규칙에 9·12 추가: "예측 9 는 D2 C9 a2 가 라벨 대상일 때만 채점(아니면 '채점 불가 (사유)'); 예측 12 의 '여섯 태그 모두' 는 라벨 대상 태그 모두로 읽고 학습 실패 태그는 제외" — 지금은 4–8·1–3·10–12 만 정해져 a2 수용 실패 / a3 학습 실패 때 9·12 채점이 미정.
- §1 실행 스크립트 행: 흐름 "(0) chkS run" → "(0) chkS(2 묶음은 chkS2) run", 전제 "fits 링크(시드 태그·chkS)" → "fits 링크(시드 태그·chkS·2 묶음은 chkS2)" (스크립트 83–84 행과 일치시키기).
- (S1) 한정어 판 `"(확산 시드 3/3; a<s> = §3d fb<k> 클리핑)"` → `"(확산 시드 3/3; a<s> = §3d fb<k>)"` — fb3 은 클리핑 + lr/3 이라 '클리핑' 만 적으면 fb3 일 때 틀린 문장이 됨.
- §1 수용 검사 행 머리 "재실행은 사용자 승인; 재실행하면 새 태그가 그 시드의 유일한 값" 뒤에 한 문장: "재실행 여부는 그 태그의 표 B·R_dp 를 보지 않고 원인만으로 정한다(자원·순서 문제 → 재실행, 그 밖 → '수용 실패 (시드 s)' 로 끝)" — 스크립트가 analysis(표 B)를 수용 검사보다 먼저 돌리므로(159 → 164 행) 무효 태그의 라벨을 본 뒤 재실행을 고를 통로가 열려 있음. 선례(SCALE16e4 §1 수용 행)도 같은 문구라 must 로 올리지 않음.
- §1 묶음 행에 "2 묶음은 1 묶음 결과와 무관하게 사다리가 닫히면 실행한다(실행하지 않는 선택은 없다)" 한 줄 — 지금은 절차로만 적혀 있어 1 묶음 결과를 본 뒤 2 묶음을 미루는 길이 문면상 막혀 있지 않음.
- §3 예측 10 은 세 부분(S2 D2·S2 UMi28·S3)이라 "셋 모두 성립해야 적중" 을 명시하거나 10a–c 로 나누기.
- §1 묶음 행에 공개 한 줄: `--resume` 2 묶음은 1 묶음 태그의 뒤 단계(analysis·accept·refarms·recovery·dR)를 다시 돌려 같은 파일을 실행 커밋 2 의 git 머리말로 덮어쓴다(코드 동일·결정적; raw 의 `run|git` 은 1 그대로) — 전사자가 머리말 해시만 보고 혼동하지 않게.
- 표기만: 끝 줄 `pending=${PEND:- none}` 은 " NR32B16e4s3" 앞에 공백이 붙음(PEND="$PEND $X"); 채점 규칙의 "(n/6 태그 채점)" 은 셀별 항목 4–6 에서는 n/2 가 자연스러움.

#### 확인
- §5 sha256[:16] 10 개(5 `_best.pt` + 5 last `.pt`) 와 a1 `_best` 3 개 = `sha256sum /home/HTJ/t2/conf/ckpt/…` 출력과 전부 일치(f956a85c…, 9c38545a…, c11bb951…, 7f72480c…, 0c887ee7…, e26ed7c3…, 0a4592e3…, a6331677…, ac384d5f…, 8d9c5f0c…; a1 34136808…/463da87a…/3cf5d3ef… = scale2_s5.txt CELL 줄).
- §4.1 표 = `logs/gpu_sched.log` :53–56,58,60,67,68,70–74,90,91 (투입·done·SIGINT 문구·시각) 및 각 `logs/train_d2sx_*.log` 의 `# done` 줄(867/847 patience, 491 interrupted aborted=True → 635/615 patience, 466/446, 937/917, 338/318, 1240 diverged best@1235) 과 일치. 재개: 첫 구간 마지막 epoch 줄 490, `# =====` 2026-10-01 20:41:30 KST(= 06:41:30 CDT) 뒤 506 행이 epoch 491 — '491 을 저장 RNG 로 다시 돈다' 서술 그대로.
- §1 학습 실패 행 '같은 rung·attempt = 같은 시드': `code/score.py:900` `SEED_TRAIN + _rung_ix(rung)*17 + attempt` (902·905 도 같은 식), fallback 항 없음; grad_clip 은 별도 인자(835–837) → fb2·fb3 은 a3 의 초기화·데이터 스트림 그대로. 선택 규칙 = SCALE16e4 §1:149 ('번호가 가장 낮은 성공 시행, 나머지는 열지 않음', DECISIONS 6953d595) 와 동일.
- §0 전사: `results/review_next/recovery_{U28NR16B16e4,U28NR32B16e4,NR32B16e4}.txt` 8 행 R_dp 0.287 [0.253,0.322] / 0.432 [0.402,0.462] / 0.811 [0.790,0.832] 와 점별 b*·V1·genie 실패 수; `tables_D2_<T>.txt` 표 B 232:44 / 391:32 / 914:29 (3/3 POWERED); SCALE16e4 §6.1.1 Holm 순서 '동률 → D2 첫째 95 %, UMi28 둘째 90 %' 와 §6.1.3 세 셀 (i) — (S2) 수준·a1 라벨 인용 모두 일치.
- 3 점 부분집합 동치(작성자 확인 (1)(2)): scratch `an/tables3_{NR32B16e4,U28NR16B16e4,U28NR32B16e4}.txt` 의 판정점·부호검정 수가 7 점 표와 동일; `frontier3_*.txt` 의 R1−R2 줄이 `scale2_primary_D2_L95.txt:5–6`·`scale2_step_U28_S1.txt:5` 와 동일. `analysis.decision_points` (analysis.py:405–413) 는 [0.005,0.9] 안 점 중 |log10(BLER/0.1)| 최소 3 개 → 수용 (b) 의 b* 비트 동일이면 판정점이 a1 과 같음은 구조적으로 보장.
- 스크립트 `dp` 정규식을 실제 a1 7 점 표 3 개에 적용 → 블록 정확히 1, '0 3 6' / '-3 0 3' / '-9 -6 -3'. `refok` 정규식 vs `eval_accept.py:125–127` 출력 형식(키 `('C9', -9)` 는 `load_points` 의 int(m[2]) 로 정수) 및 scratch `rev/{ok_real,bad_bstar,bad_shared,bad_extra,ok_all}.txt` 사례 일치.
- `frontier_ci.py`: `--recovery` 스펙 `raw:cell:s1,s2,…` 파싱(149–154), 219 행 90 % 줄 + 222 행 `--level` 줄을 항상 함께 출력 → `--level 0.95` 로 D2 95 %·UMi28 90 % 모두 읽을 수 있음(scale2_primary_D2_L95.txt:5–6 실례). `recovery_ci --snrs` nargs='+' float.
- `eval_accept.py` 인자 `--nr --points --ref-arms --fits-dir --grid --n` 존재; `--points C:s1,s2` 정수 파싱(66), 재생 검사는 태그 raw 의 점만 순회(80) → 3 점 raw 를 7 점 a1 raw 와 비교 가능; chk 호출은 run_scale2.sh:238·253 (ONE='--n 40 --chunk 40', C6 S0=-3, AARMS 11 arm 동일) 과 같은 플래그.
- 실행 커밋 전제: worktree 에서 `git diff --name-status b4433d3c HEAD -- conf/code Demo` 가 지금 비어 있음(HEAD 8992254c) → 스크립트 추가 뒤 정확히 `A\tconf/code/run_seedsnr16e4.sh` 한 줄; `git status --porcelain conf/code` 는 미추적 스크립트만. a1 raw 3 개 각 448 파일, `run|git` = 'b4433d3c'(짧은 해시; `gitok` 의 startswith 와 호환); `raw_U28NR16B16e4chk` 1 파일 `run|git` b4433d3c. `common.CELLS['C9']['snrs']` = (−12,…,6).
- fits 링크: 시드 6 개·chkS·chkS2 는 아직 없음(§4.3 '[실행 커밋 1 전] 생성' 과 일치); 기존 `gmm_fits_D2_<T>{chk,last}` 등은 상대 링크. `conf/ckpt` 는 worktree 에서 `/home/HTJ/t2/conf/ckpt` 로의 심볼릭 링크 → 스크립트의 절대 CK 경로와 같은 파일.
- ROUND 2 적용 범위: before_round2 사본과 현재 문서 diff = 머리말 4 행 추가, §1 회귀·묶음·수용·라벨·문장 조건·비용 행, §2 사다리 행, §3 채점 규칙·예측 7·8, §4.3 링크 8 개 — 보고된 M1·M2·integ-1 외 변경 없음; `{{NOW}}` 유지; `bash -n` 통과.
- fb2·fb3 학습 프로세스 진행 중(pid 2969660 GPU 0 `--fallback 2`, 2969673 GPU 1 `--fallback 3`, worktree conf 에서 실행). 검토자는 fb2 로그 꼬리 2 줄만 봤고(값 인용 안 함) fb3 의 로그·체크포인트는 열지 않았음. GPU·수신기 실행·삭제·커밋 없음.

### 렌즈 integ

#### 반드시
- (없음)

#### 권고
- (스크립트 83행 뒤, 1줄) 세 번째 실행 커밋이 생기면 `raw_U28NR16B16e4chkS2`(커밋 2)가 완성돼 있어 `run` 이 건너뛰고 회귀 검사가 그 커밋에서 돌지 않은 채 통과로 기록된다(등록은 2 묶음만이라 확률 낮음). 추가: `[ "$(nraw $CHK)" -eq 1 ] && ! gitok $CHK && die "raw_$CHK is another commit's chk too: a third run commit is not registered (§1 묶음 행)"`
- (스크립트 147행) chk 실패 ABORT 경로가 `SEEDSNR_DONE ok=0 fail=1 …` 를 찍는다 — §1 묶음 행의 "1 묶음 `SEEDSNR_DONE` 뒤에만 실행 커밋 2" 를 grep 으로 보면 오인한다. `log "SEEDSNR_ABORT chk=$CHK ok=$OK fail=$FAIL"` 로 바꾸고 §1 실행 스크립트 행 끝 줄 설명에 "(chk ABORT 는 `SEEDSNR_ABORT`)" 를 덧붙인다
- (스크립트 전제, 1줄) dR/S1 의 C2 끝 raw 를 전제에서 검사하지 않는다 — 지금은 둘 다 448 파일(raw_B16e4k 실제 디렉터리, raw_U28B16e4 → /home/HTJ/t2/conf 링크)이지만 없으면 18 h 뒤 frontier 단계에서만 실패한다. 71행 뒤: `for r in raw_B16e4k raw_U28B16e4; do [ "$(ls $r/D2_C2_*.npz 2>/dev/null | wc -l)" -eq 448 ] || die "$r: not 448 C2 chunk files (dR/S1 C2 end)"; done`
- (문서 §1 실행 스크립트 행) 전제 "fits 링크(시드 태그·chkS) 대상 일치" → "fits 링크(시드 태그·chkS, 2 묶음은 chkS2) 대상 일치"; 흐름 "(0) chkS run" → "(0) chkS(2 묶음은 chkS2) run"; 예측 12 "chkS 비트 동일" → "chkS(2 묶음은 chkS2) 비트 동일" (스크립트 머리말 6–7행·§1 회귀 검사 행과 맞춤)
- (문서 §1 묶음 행 또는 §6 전사 규칙) 2 묶음 `--resume` 은 1 묶음 태그의 뒤 단계를 다시 돌려 `seedsnr_dR_<T>s<s>.txt`·`_accept.txt` 머리말의 git 이 실행 커밋 2 가 된다(값은 결정적으로 같음). §6 은 raw 의 `run|git`(run_manifest) 을 실행 커밋으로 적고 머리말 해시는 "계산 시점 커밋" 으로만 적는다고 한 줄 못 박는다
- (문서 §1 학습 실패 행, 인용 정합) DECISIONS 6953d595 원문은 "fb3 는 시행 2 가 diverged 또는 aborted=True 로 끝날 때만" 인데 이 행은 aborted=True 를 재개로 처리한다(SCALE16e4 §1 학습 실패 행과 같음). "(aborted 처리는 SCALE16e4 §1 을 따르며 6953d595 의 aborted 문구를 대체한다)" 를 괄호로 덧붙이면 감사 때 충돌로 잡히지 않는다
- (통계 렌즈 밖, 작성자가 남긴 틈 2) 예측 9(D2 C9 a2 R_dp < 0.811)의 채점 조건이 M2 규칙(4–8, 1–3·10–12)에 없다 — "a2 가 라벨 대상 태그일 때만 채점, 아니면 채점 불가" 한 구를 채점 규칙에 더한다

#### 확인
- 플래그 전부 존재(argparse grep): runner.py `--testbed --ntrain --prior --cell --worker-gb --stagec-ckpt --n --chunk --snr(nargs+, float) --arm --tag`, `analysis` cmd; eval_accept.py `--ntrain --prior --nr --bstar --kron-K --ll-val --n --points(CELL:s1,s2 반복) --ref-raw --ref-arms --fits-dir --grid --tag`; recovery_ci.py `--raw --cell --snrs`; frontier_ci.py `--recovery(nargs 2) --level(기본 0.90)`; guard_report.py `--raw --testbed`; run_manifest.py `--tag`
- eval_accept 재생 검사는 태그 raw 의 점(3 점)을 돌며 참조 raw(7 점)에서 찾는다(eval_accept.py:73–97) → 3 점 태그 vs 7 점 a1 raw 가 성립; 실증 `NR32B16e4last_accept.txt` = ACCEPT OK + (k) 줄. `--ref-arms all` 출력 형식 `  <tag> ('C2', -3): replay vs raw_X (all): shared 2560/2560, arms differing [...] (max |diff| 1e+08)` (D3B16e4s2_refarms.txt) 가 `refok` 정규식과 일치; 비교 키는 참조 raw 의 arm×KEYS_RAW 라 11 arm chk/시드 raw 와 구성상 맞음
- 체크포인트 sha256[:16] 10 개 전부 §5 와 일치(f956a85c82ed4fb3·9c38545ab009f307·c11bb951ff7be4d4·7f72480c42fcd6c9·0c887ee786ff9dfa best; e26ed7c3…·0a4592e3…·a6331677…·ac384d5f…·8d9c5f0c… last), a1 best sha 3 개 = scale2_s5.txt CELL 줄. `~/t2_wtS/conf/ckpt` → `/home/HTJ/t2/conf/ckpt` 심볼릭 링크라 스크립트 `CK` 와 fb2/fb3 저장 위치가 같다(`d2sx_NR32_N160000_a3_fb{2,3}{,_best}.pt` 존재, 갱신 중; fb3 로그·ckpt 내용은 열지 않았다)
- 학습 로그 `# done` 줄 = §4.1·§5: UMi28NR16 a2 867/847 5.221701e-01 patience; a3 491 interrupted aborted=True best@486 → 재개 머리말 20:41:30 KST(=06:41:30 CDT) → 635/615 5.224268e-01 patience; UMi28NR32 a2 466/446, a3 937/917; NR32 a2 338/318; NR32 a3 1240 diverged best@1235 9.599885e-02. gpu_sched.log :53–56 (00:52 투입), :58 (02:58), :60 (03:34), :67–:68 (06:24/06:25 SIGINT 문구 그대로), :71–:72 (06:34→07:37), :73 (07:54), :74 (08:33), :90–:91 (10-03 18:12 fb2 GPU 0·fb3 GPU 1) 모두 일치
- git 전제: `git diff --name-status b4433d3c HEAD -- code ../Demo` 가 현재 빈 출력(8992254c 는 code 미변경) → 동결 뒤 `A conf/code/run_seedsnr16e4.sh` 한 줄이 됨; `git diff --quiet 16a9dff6 HEAD -- code ../Demo` rc 0; `../Demo` 존재; 스크립트 미추적(`?? conf/code/run_seedsnr16e4.sh`)이라 커밋 전엔 45행에서 die(의도). `run|git` 는 짧은 해시('b4433d3c', `_git_head` 는 dirty 면 '+dirty' 접미) 라 `gitok` 의 `h.startswith(x)` 가 맞다; 동결·§5 커밋 시각 09-30 14:06 / 10-01 13:52 CDT = 문서 9행
- a1 raw 448 파일 × 3 셀; `raw_U28NR16B16e4chk` 1 파일(`D2_C6_UMi28_Nr16_T16_Tp4_eig_snr-3_skip0_n40.npz`, run|git b4433d3c) → chk 명령(C6 −3, n 40, 11 arm) = SCALE `run ${T}chk 1 $B $BEST $ONE --snr $S0 --arm $CHKARMS`(S0 = C6 격자 첫 점 −3; `common.CELLS` C6 (−3..15), C9 (−12..6) 확인); SCALE chk 18.8 분(§6.1 표 :445), chk 수용 OK(`U28NR16B16e4chk_accept.txt`). chkS 링크는 아직 없음(§4.3 대로 실행 커밋 1 전 생성 필요)
- frontier_ci `--level 0.95` 는 90 % 줄과 `(--level 0.95)` 95 % 줄을 함께 찍는다(frontier_ci.py:219–222, scale2_primary_D2_L95.txt); `--rstar` 없으면 Q-OP 생략(:257); 작성자 scratch `frontier3_NR32.txt`·`frontier3_U28NR16.txt` 가 3 점 부분집합으로 SCALE 값을 그대로 재현(D2 +0.302 [95% +0.254, +0.355], UMi28 +0.137 [90% +0.085, +0.193]) → `--extrap`·`--rstar` 생략이 dR 줄을 바꾸지 않음. C2 끝 raw 둘 다 worktree 에 448 C2 파일
- §0 수치 대조: recovery_<T>.txt:8 R_dp 0.287 [0.253, 0.322] / 0.432 [0.402, 0.462] / 0.811 [0.790, 0.832]; 판정점 실패 수 합 = frontier R1 줄(b* 824/958/1161, V1 636/599/276, genie 170/127/70); 표 B 앵커 블록이 세 a1 표에 정확히 1 개(`dp` 정규식 `len(m)==1` 충족), 판정점 '+0 +3 +6' / '-3 +0 +3' / '-9 -6 -3'. 비용 출처 숫자(120.8·820.0·661.9·44.2·325.1·266.7 분, 99/192 워커) = SCALE §6.1 :441–:457; 산술 51.8/351.4/283.7 → 22.9 h, 1 묶음 18.5 h, 2 묶음 5.0 h 재계산 일치
- 재개 안전: runner `run_task` 가 기존 청크 파일을 건너뜀(runner.py:489 'FINISHED CHUNKS ARE SKIPPED'); 부분 raw 는 `gitok`(청크 전부 run|git == HEAD) 통과 때만 이어 감; 완성 raw 는 `run` 이 skip 하고 뒤 단계만 재실행; chkS/chkS2 선택 83행은 작성자 scratch 표(없음→chkS, HEAD→chkS, 다른 커밋→chkS2, 링크 없으면 ABORT) 와 코드 읽기가 일치; `SEEDSNR_WGB` 인상은 S5·HEAD 불변, `kchk` 는 worker_gb ≥ WGB 집합 허용. eval_accept 는 git/HEAD 를 보지 않아 2 묶음에서 1 묶음 raw 의 수용 재실행이 FAILED 로 바뀌지 않음
- 메모리 가드: `--worker-gb $WGBR` 가 C9 호출에만 붙고(152행) chk·C6 는 없음 = SCALE 결정 5; runner.py:649–655 가 `[run] --worker-gb G: memory guard allows M workers -> jobs = J` 를 찍고 `meta|jobs`·`meta|worker_gb` 를 남김; `kchk` 는 run_scale2.sh 와 글자 동일. `bash -n` 통과(작성자 보고와 같음; 스크립트는 실행하지 않았다, GPU·수신기 실행 없음, 삭제 명령 없음)
- 인용: DECISIONS 6953d595 커밋 존재("C6 1.6e5 — §3d 시행 3 대기 실행 규칙"); `train_nr16.py:54–65` 에서 fb 는 태그 접미·grad_clip·lr 만 바꾸고 `score.train(rung, attempt)` 의 시드(`score.py:900` SEED_TRAIN + rung_ix·17 + attempt)는 같음 → "같은 rung·attempt = 같은 시드" 맞음; SEEDS16e4·SEEDS3 §1 의 "발산 시드 = 사다리 없이 학습 실패" 문구와 SCALE16e4 §1 학습 실패 행(§3d·가장 낮은 번호·aborted 재개) 둘 다 원문 확인 → 문서의 '선례와 다른 규칙 공개·병기' 는 사실에 맞음
