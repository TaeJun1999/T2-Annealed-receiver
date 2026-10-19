# 기록 감사 — NEXT_EXPERIMENTS_D2SITEMS.md §6 (E1+ matched-scalar 대조; D2 C2 8×4 S2, 태그 D2SITEMS; 주 `V1-ms → V1`, 보조 `V4 → V1-ms`)

- 감사자: Claude Code (Fable 5.1 서브에이전트, 독립 기록 감사; 공통 절차 `gcap/PROMPT_SERVER_COMMON.md` §3 의 "기록 감사 1회"). 감사 시각 2026-10-19 23:08 ~ 23:22 KST (= 10-19 09:08 ~ 09:22 CDT; `date` · `TZ=America/Chicago date` 로 읽음).
- 감사 대상 판: 시작 때 HEAD **8b5322ca**, 끝날 때 **e6619eb2** (감사 중 부모 세션이 다른 감사 기록 · WORK_QUEUE 커밋 29985146 · e6619eb2 를 더함; 이 등록 문서 · `e1ms/` · DECISIONS · EXPERIMENTS 는 두 HEAD 에서 같고 작업 트리 = HEAD). §6 는 **ba03f1dc** (10-19 09:02:59 CDT) 에 들어갔다. 실행 커밋 **9a2c9fd4** (08:42:42 CDT; `e1ms_s5.txt` 를 만진 main 의 유일한 커밋), FREEZE **e6ac9e65** (`e1-ms`, 10-18 23:29:10 CDT), 병합 **7af288e6** (10-19 03:18:56 CDT; 부모 44691de0 + e6ac9e65).
- 방식: 읽기 전용. 새 파일은 이 폴더에만: `recompute_e1ms.py` → `recompute_e1ms.out` (numpy 로 청크 직접 읽기; `conf/code` 의 `e1ms_compare` · `pair_baselines` · `analysis` 미사용 — 부호검정 · 2/3 규칙 · power guard · 라벨 순서 · 앵커 규칙 · SNR@0.1 보간 · 90 % paired bootstrap (B 2000, `default_rng(20260925)`, 격자 점 순서대로 `integers(n, size=n)`, 두 arm 같은 index, `nanpercentile` 5 · 95) 을 §1.4 문구대로 따로 구현; p 는 `scipy.stats.binomtest` 와도 대조), `rerun_E1MS_compare.txt` (+ `.stdout` · `.err` · `_diff.txt`; 등록 도구 `code/e1ms_compare.py` 를 `--out` 만 이 폴더로 바꿔 재실행), `rerun_E1MS_accept.txt` (`code/eval_accept.py` 를 §1.3 인자 그대로 재실행). CPU `nice -n 10 taskset -c 2-5`, GPU 미사용 (`CUDA_VISIBLE_DEVICES=`). runner 실행 · `run_*.sh` 실행 · git 상태 변경 · 기존 파일 수정 없음.
- 이미 거친 검토 (§6.6 의 verifier 결함 0) 는 믿지 않고 전부 따로 셌다.

## 1. 재계산한 것과 재현 여부

| 항목 | 방법 | 검사 값 수 | 결과 |
|---|---|---|---|
| `raw_D2SITEMS` 청크 계획 {(40k, 40): k < 64} × 3 SNR = 192; 파일명 패턴; 구멍 · 중복 없음; `\|failed` 키 0; 비유한 blk_err 0; arm 집합 = 정확히 {V1-ms, genie}; 2 arm × 7 KEYS_RAW 모양 (40, 16) | 파일명 파싱 · npz 직접 | 3 × 6 + 3 | **재현** |
| `raw_D2SITEMS` meta (192 청크 전부 동일): `run\|git` 9a2c9fd4 (`+dirty` 없음), `meta\|ms_arm` 문자열, `stagec_ckpt_id` (sha256[:16] 4443921ce8d5c4a1 · epoch 1784 · best 1764 · legacy-last), `stagec_ckpt` 경로, bstar kron, kron_K 1024, `ll_val\|kron` = −11.459169831224418 (\|Δ\| ≤ 1e-9), ntrain 160000, em_sec 107957.18832826614 (= manifest), jobs 96, worker_gb 1.5, run\|iters 16 · n 40 · seed 20260926 · beta 0.7 · t_in 5 · dtype complex128/float64, run\|skip · run\|snr = 파일명 | 전 청크 비교 | 21 | **재현** (청크 mtime 10-19 22:44:08–22:47:29 KST = 08:44–08:47 CDT) |
| base `raw_B16e4k`: 448 청크, manifest written 2026-09-23 07:36:44 KST · git_commit cd241b7e · n_raw_files 448, manifest 보다 새 청크 0 (mtime 2026-09-22 21:23:28–21:39:55 KST), **chunks-sha 78cbb59fc01ce520 을 정렬 청크 sha256 연결의 sha256[:16] 으로 독립 재현**, 3 점 계획 · `\|failed` 0 · 비유한 0 | 직접 | 15 | **재현** (compare 머리말의 `manifest-head:cd241b7e/chunks-sha:78cbb59fc01ce520` 과 일치) |
| genie 비트 동일: 192 청크 × (7 KEYS_RAW + guardH) = 1536 배열, 점별 KEYS4 연결 배열 (NaN = NaN) | `array_equal(equal_nan)` | 1536 + 3 | **재현** (다른 배열 0) |
| 실패 수 / 2560 (−3 / 0 / +3): V1 371 · 88 · 29, V4 394 · 96 · 21, V1-ms 389 · 98 · 27, genie 87 · 26 · 12 (§6.2 표 · §0.1); genie 는 두 raw 에서 같은 수; BLER@16 §0.1 의 V1 · V4 소수 5 자리 | numpy 직접 | 12 + 3 + 6 | **재현** |
| 주 비교 `V1-ms → V1`: a:b 53:35 · 22:12 · 8:10, p (`%.2g`) 0.069 · 0.12 · 0.81 (전정밀 0.069346 · 0.121449 · 0.814529), pooled 83:57 p 0.034 (0.0342357), D 88 · 34 · 18, POWERED True, second arm fewer 0/3 · first arm fewer 0/3 → **(iii)** | `math.comb` 직접 + scipy 대조 | 17 | **재현** |
| 보조 `V4 → V1-ms`: 6:1 · 4:6 · 0:6, p 0.12 · 0.75 · 0.031 (0.125 · 0.753906 · 0.03125), pooled 10:13 p 0.68, D 7 · 10 · 6, POWERED True, second 0/3 · first 1/3 (+3 dB, V4 쪽) → **(iii)** | 직접 | 17 | **재현** |
| 앵커 규칙 확인 줄 (BLER ∈ [0.005, 0.9], \|log10(BLER/0.1)\| 최소 3 점) — V1-ms · V4 모두 `['-3', '+0', '+3']` | 직접 | 2 | **재현** (\|log10\| V1-ms 0.182 · 0.417 · 0.977, V4 0.187 · 0.426 · 1.086 — 세 점이 전부라 자동 선택도 같다) |
| SNR@0.1 (로그 선형, 첫 하향 교차, floor 0.5/n): V1 −2.2264, V1-ms −2.0895, V4 −2.0839 dB (모두 ok; genie 는 'lo') → **L = +0.137 → +0.14 dB**, 보조 +0.006 → +0.01 dB | 직접 | 3 + 2 + 2 | **재현** (§0.1 −2.226, §6.6 −2.090 · −2.084 · +0.137 · +0.006) |
| 90 % paired bootstrap (B 2000, seed 20260925): L **[+0.050, +0.225] → [+0.05, +0.22]**, censored 0/2000; 보조 **[−0.037, +0.042] → [−0.04, +0.04]**, censored 0 | 독립 구현 (RNG 소비 순서는 §1.4 · §0.1 Codex 3 의 서술대로) | 6 | **재현** (소수 3 자리까지 §6.6 과 같음; 참고로 seed 1 이면 L [+0.047, +0.227]) |
| 등록 도구 재실행 `e1ms_compare.py --raw raw_D2SITEMS --base raw_B16e4k` | `--out` 만 이 폴더 | 1 파일 | **커밋본 `compare_D2SITEMS.txt` 와 바이트 동일** (`cmp` · `diff` 빈 출력) |
| 수용 ① 재실행 `eval_accept.py --tag D2SITEMS:legacy-last:4443921ce8d5c4a1:C2 … --ref-raw raw_B16e4k` | 재실행 | 1 | rc 0, `ACCEPT: OK -- D2SITEMS` (커밋본과 동일) |
| §6.3 문장 = 틀: §2.1 고정 설명 (글자 단위), L 문장 (재계산 x · l · u · c 를 넣은 문자열이 §6.3 에 있음), (iii) 라벨 문자열, §2.4 (iii) 영어 문장 · 공통 문장 (재계산 수치), §2.2 고정 절, 보조 수치 | 문자열 포함 검사 | 7 | **통과** |
| §2.3 금지 문구 ("동등" · "비열등" · "최적 GMM" · "scaling law" · "비긴다" · "차이 없음" · "모든 SNR 에서" · "floor 만의 몫" · "Jacobian 수리만의 효과" · "고정 질의에서" · "site 한 번의 효과" · "저비용 scalar") 가 §6 (216 행 이후) 에 있는지 | grep | 12 | **0 건** |
| 예측 채점 (§3 1–10) 을 재계산 값으로 | 규칙대로 | 10 + 2 | **8 적중 · 빗나감 {2, 6}** — §6.4 와 같음 (관대한 채점 없음; 아래 §3) |
| test / 개발 분리: 2026-10-19 11:00 KST (V1-ms 코드 ba1b7c35 = 11:30 KST) 이후 쓰인 npz **23,001 개** (862 raw 폴더: `~/t2/conf/raw_*`, `~/t2_wt*/conf/raw_*`, `.claude/worktrees/*/conf/raw_*`, 세션 스크래치패드 `**/raw_*`; `raw_D2SITEMS` 제외) 에서 `M-ours-dscore-C-V1ms\|` 키를 찾음 | zip 목록 + npz | 23,001 | V1-ms 키가 있는 곳: `raw_E1MSdev` (skip 2560..2840) · `raw_E1MSsm` (2560) · `raw_E1MSmcb` (2560) — 모두 개발 시행; test skip (0..2520) 에 있는 것은 `raw_E1MSflow` (192) · `raw_E1MSflowm` (191) · 스크래치 `raw_KAT` (192) 뿐이고 **그 V1-ms 배열 1344 · 1337 · 1344 개가 전부 `raw_B16e4k` 의 V1 배열과 비트 동일** (= 이름만 바꾼 합성 raw, §4 흐름 시험 · 정답 사례). **test 시행에서 실제로 돈 V1-ms 는 `raw_D2SITEMS` 뿐** |
| 확인 3 (`raw_E1MSregon` · `regoff`, 99f62bfb+dirty) · 병합 확인 (a) (`raw_E1MSmcaon` · `mcaoff`, fef2594a): 파일 하나 (−3 dB skip 0 n 40), arm 집합 = 정확히 {V1, V4} (V1-ms 없음), 14 배열 = `raw_B16e4k`, `meta\|ms_arm` on 에만 | 직접 | 4 × 6 | **재현** |
| 병합 확인 (b) `raw_E1MSmcb` (fef2594a, skip 2560): arm {V1-ms, genie}; 14 배열 = worktree `raw_E1MSdev` 와 `raw_E1MSsm` (둘 다 2807dd23); 판정 파일 `E1MS_MERGECHK OK (0 problems)` | 직접 | 7 | **재현** |
| 개발 스크린 (§0.3, `raw_E1MSdev` 2560..2879): 계획, 실패 V1 38/11/2 · V1-ms 38/10/4 · V4 37/10/4 · genie 11/5/1, a:b 세 쌍 (6:6 · 1:2 · 2:0, 0:1 · 0:0 · 0:0, 5:6 · 1:2 · 2:0), V4 ↔ V1-ms 반복 16 불일치 블록 1/960 | 직접 | 3 + 4 + 3 + 1 | **재현** |
| 자산: 체크포인트 sha256 4443921c…82f29; fits 복사본 24 개 바이트 동일 · 링크 없음, b\* kron1024 bf796b84… · fullK32 d4601650… ; fit 파일의 `ll_val` −11.459169831224418; s5 = `FREEZE e6ac9e653dad4e15d2e781c9800a090cab529857` · `WGB 1.5` | sha256sum · npz | 6 | **재현** |
| §5 코드 sha256[:16] 6 개 (arms 145f9b568e83a681 · runner 9967a6b96a7f6fc2 · run_e1ms e99f2483951d274c · e1ms_compare 9f19154555ccf3bc · eval_accept d05b660c07e899fe · pair_baselines f11cea47e8c9c83c) 가 FREEZE e6ac9e65 와 실행 커밋 9a2c9fd4 에서 같음 | `git show \| sha256sum` | 12 | **재현** |
| FREEZE 뒤 §0–§5 불변: `git diff -U0 e6ac9e65 HEAD -- <등록>` 은 hunk 하나 `@@ -216,0 +217,51 @@` (§6 추가) 뿐; e6ac9e65 ↔ 7af288e6 ↔ 9a2c9fd4 에서 문서 차이 없음; `git diff e6ac9e65 9a2c9fd4 -- conf/code Demo` 비어 있음 (HEAD 까지의 차이는 E1+ 뒤 병합한 `bench_cost.py` 뿐) | git | 4 | **재현** |
| 순서 · 창: V1LS 기록 커밋 44691de0 (03:18:21 CDT) < 병합 7af288e6 (03:18:56) < fef2594a (03:29:27; code · Demo 불변) < 병합 확인 08:40–08:41 (tmux `e1msmc` 생성 08:40:14) < s5 파일 08:41:28 < 실행 커밋 9a2c9fd4 08:42:42 < tmux `e1ms` 생성 08:42:50 · 로그 start 08:42 < 청크 08:44:08–08:47:29 < `E1MS_DONE` 08:47 (로그 mtime 08:47:38) < §6 기록 08:49 (console 파일 mtime 08:49:05) < §6 커밋 ba03f1dc 09:02:59; **실행 창 08:42:00–08:48:00 CDT 안의 커밋은 (모든 ref 에서) 실행 커밋 9a2c9fd4 뿐**; 실행 커밋은 s5 + 실행 시작 DECISIONS 줄 (473 행) + 병합 확인 산출물 · WORK_QUEUE 만 (code · Demo · 등록 문서 없음); `e4-cost` 병합 1051c9b6 은 09:06:55 CDT (E1+ 뒤, §5 병합 순서) | `git log` · `date -r` · tmux | 14 | **재현** |
| 같은 시각의 다른 작업 (§6.1): Codex 두 건의 파일 `reviews/20261019-224612-prompt_s6_v1ls.md` · `20261019-224612-codex_write_cost_report.md` (= 08:46:12 CDT 시작), 프롬프트 · 명세의 `taskset -c 66-67` · `1,97`; Fable 감사 넷의 머리말 시작 08:47 · 08:47 · 08:48 · 08:48 CDT, `taskset -c 2-5 / 6-9 / 10-13 / 14-17` (= 2–17), nice 10; 96 + 2 + 2 + 16 = 96 + 20 | 파일 | 8 | **재현** (단 N2 — GPU 점유 더미 3 개 미기재) |
| 기록 줄: DECISIONS 471 (동결, 44691de0) · 473 (실행 시작, 9a2c9fd4) · 475 (결과, ba03f1dc) 와 EXPERIMENTS 92–94 행 · WORK_QUEUE 3 · 16 행의 수치 (실패 수 · a:b · p · D · 라벨 · L · 구간 · 예측 8/10) · 시각 (08:40–08:41 · 08:42–08:47 · 09:02 CDT; KST 병기) · 커밋 (9a2c9fd4 · e6ac9e65 · 7af288e6 · fef2594a · 99f62bfb+dirty · ba1b7c35 · 2807dd23 · 9dd8b5fe · 1de35f0c) · CPU (24 · 25 · 26; 96) · 승인 인용 ("다 진행하자", 08:39 CDT 이전 — 병합 확인 시작 08:40:14 와 일관; 네 파일에서 같은 인용) | 읽기 대조 | ≈ 90 | **1 건 불일치** → N1 (DECISIONS 471 의 FREEZE 시각) |
| `docs/RESULTS.md` | grep | — | D2SITEMS · V1-ms 절 없음 (§6.5 "사용자 요청 때" 와 일관) |

합계: 자동 비교 **162 값 중 0 불일치** (`recompute_e1ms.out` TALLY) + test / 개발 분리 스캔 23,001 파일 (실제 V1-ms test 실행 0), 도구 재실행 2 (compare 바이트 동일 · accept 동일), 수동 대조 약 120 값 중 **시각 1 건 · 누락 1 건**.

## 2. 규칙 재적용 (동결 §1.4 · §2 → §6.2 · §6.3)

- 판정점 −3 / 0 / +3 고정 (앵커 자동 선택도 같음) ✓. 검정: 점별 exact 양측 부호검정 p < .05 — 주 비교는 세 점 모두 p ≥ .05 (유의점 0), 보조는 +3 dB 0:6 p .031 (V4 쪽) 하나 ✓.
- power guard: D ≥ 6 인 판정점이 2 개 이상 — 주 88 · 34 · 18 (3/3), 보조 7 · 10 · 6 (3/3) → 둘 다 POWERED, (iv) 아님 ✓.
- 라벨 순서 (iv) → (i) → (ii) → (iii): 주 wy 0 · wx 0 → **(iii)**; 보조 wy 0 · wx 1 (< 2) → **(iii)** ✓. (iii) 의 뜻 (2 개 이상에서 자기 쪽 p < .05 없음) 과 "개별 유의점은 있을 수 있다 — 그 점의 방향과 p 를 §6 에 적는다" → §6.3 보조 문장 끝 "+3 dB 0:6 p .031 — V4 가 적게 실패" ✓. 혼합 결과 정의 (서로 다른 방향의 유의점) 에는 해당하지 않음 ✓.
- L 문장: kind ok (V1 · V1-ms 모두 −3 → 0 dB 사이 교차) → "SNR 손실 L = … = +0.14 dB [90 % paired bootstrap +0.05, +0.22] (양수 = scalar 쪽 손실; 3 점 격자 −3 / 0 / +3 dB; censored replicates 0 %)" — `gain` 문자열의 네 수 그대로 ✓; censored 분기 미사용 ✓.
- 고정 설명 (§2.1) 글자 단위 동일 ✓; 허용 꼴 · 허용 목록 밖의 해석 문장 없음 (§6.3 은 라벨 · L · 고정 설명 · 범위 · 보조 고정 문장 · 영어 틀만) ✓; pooled 83:57 p .034 는 "보고 전용 … 라벨 · 문장에 쓰지 않는다" 로만 등장 ✓.
- 보조 비교 문장 (§2.2 틀): 라벨 · 점별 a:b · p (출력 그대로) · gain 문자열 · 고정 절 ✓; "floor 만의 몫" 류 없음 ✓.
- 범위 문장 (이 셀 · 예산 · prior, 판정점, test 0..2559) ✓. 영어 틀 (iii) · 공통 문장 (+0.14, +0.05, +0.22) ✓.

## 3. 예측 채점 재확인 (§3 ↔ §6.4)

| # | 동결 예측 | 재계산 사실 | 채점 |
|---|---|---|---|
| 1 | 주 라벨 (iii) | (iii) | 적중 ✓ |
| 2 | −3 dB V1 쪽 유의 (a > b, p < .05); 0 · +3 유의 아님; 혼합 아님 | 53:35 a > b 이나 p .069; .12 · .81; V1-ms 쪽 유의 0 | **빗나감** (접속 예측의 한 절 ✗) — §6.4 와 같음 |
| 3 | POWERED, 세 점 D ≥ 6 | 88 · 34 · 18 | 적중 ✓ |
| 4 | kind ok, censored 0 %, L ∈ [+0.04, +0.25] | ok, 0 %, +0.137 | 적중 ✓ |
| 5 | 구간 출력 하한 ≥ +0.01 | +0.05 (+0.050) | 적중 ✓ |
| 6 | 보조 (iv) (D ≥ 6 인 점 < 2; 대안 (iii)); D ≤ 20 / 10 / 10 | (iii) (D 7 · 10 · 6, 3/3 ≥ 6); 7 · 10 · 6 ≤ 20 / 10 / 10 | **빗나감** — §6.4 와 같음 (대안을 적중으로 치지 않음) |
| 7 | \|F_ms − F_V4\| ≤ 20 / 10 / 10; F_ms(−3) > 371; F_ms(+3) < 29 | 5 · 2 · 6; 389; 27 | 적중 ✓ |
| 8 | 앵커 확인 줄 둘 다 ['-3', '+0', '+3'] | 둘 다 | 적중 ✓ |
| 9 | 수용 ① · ② OK, NOTE 0 | OK · 192 chunks 0 problems · NOTE 0 (재실행도 OK) | 적중 ✓ |
| 10 | runner ≤ 15 분 | 4.6 분 | 적중 ✓ |
| 11 | 빗나갈 경로 | 해당 없음 | — |

→ 8 / 10, 빗나감 {2, 6}: §6.4 · DECISIONS 475 · EXPERIMENTS 94 · WORK_QUEUE 와 같다. 관대한 채점 없음 (2 · 6 의 부분 ✓ 는 병기만 하고 점수에 넣지 않았다).

## 4. 발견

### MUST-FIX
없음 — §6 의 수치 · 라벨 · 판정 · 문장 · 채점 가운데 틀린 것을 찾지 못했다.

### SHOULD-FIX
없음.

### NIT

**N1 · `conf/DECISIONS.md` 471 행 (E1+ 등록 동결 줄, 44691de0) "FREEZE = e1-ms e6ac9e65 (10-18 **23:3x** CDT, 한 작업일 안)"** — FREEZE 커밋 e6ac9e65 의 시각은 2026-10-19 13:29:10 KST = **10-18 23:29:10 CDT** 다 (`git log -1 --date=iso e6ac9e65`; 등록 머리말의 "v2.3 작성 23:27 CDT" 와도 일관). "23:3x" 는 1 분 뒤 자리수로 적혔다. 판정 · 수치와 무관한 시각 표기. 교체 제안: `(10-18 23:29 CDT, 한 작업일 안)`.

**N2 · 등록 §6.1 224 행 "같은 시각의 다른 작업 … 08:46–08:47 CDT 에는 선언상 이 계정의 CPU 합이 96 + 20 스레드였다"** — 실행 창 내내 GPU 0 · 1 · 2 점유 더미 `gpuhold/gpu_hold.py` 세 프로세스 (pid 2432767 10-18 08:13 KST 시작, 2945815 · 2945838 10-19 10:28 KST 시작; 지금도 돌고 있고 `nvidia-smi` 에 596 MiB 씩; psr 23 · 0 · 118 = WORK_QUEUE 의 CPU 0·96 / 22·118 / 23·119, nice 10) 도 이 계정의 프로세스였다 (WORK_QUEUE "진행 중" 표의 사용자 지시 일회 예외; 256×256 matmul 5 s 마다 — 부하는 무시할 만하다). §6.1 의 열거와 "96 + 20" 에는 들어 있지 않다. 결과와 무관하고 §6.1 자체가 "(결과 무관)" 으로 적은 문장이지만, 같은 시각 프로세스 목록으로서는 누락이다. 덧붙임 제안: `(그 밖에 사용자 지시의 GPU 0 · 1 · 2 점유 더미 셋 — CPU 0·96 / 22·118 / 23·119, nice 10, WORK_QUEUE — 이 실행 전부터 돌고 있었다; 5 s 마다 작은 matmul 하나)`. DECISIONS 475 의 "(Codex 두 건, Fable 감사 넷 — 다른 CPU, runner 없음, 시작 가드 뒤)" 도 같은 범위.

### 그 밖에 확인한 것 (변경 불필요)
- §0.4 · DECISIONS 471 · 473 의 "`--arm` 필터 (runner.py:623) 가 시행 루프 (:643) 앞" — 실행 커밋의 `runner.py` 623 행 `arms = {k: v … if (not arm_sel or k in arm_sel)}`, 643 행 `for tr in range(skip + n)` 과 일치하고, 확인 3 · 병합 확인 (a) 의 raw 네 개에 V1-ms 키가 없다 (위 표).
- §5 "병합 확인 … main 의 병합 커밋에서" 는 7af288e6 자체가 아니라 그 다음 main 커밋 fef2594a (V1LS §6.7 문서만) 에서 돌았다 — code · Demo 는 FREEZE 와 같고 DECISIONS 473 · EXPERIMENTS 93 이 fef2594a 를 적고 있어 기록상 문제 없음.
- 공통 규칙 §3 의 "동결 커밋 = 실행 커밋" 과 달리 FREEZE (`e1-ms`) 와 실행 커밋 (main) 이 분리돼 있으나, 적대적 검토 M1 로 등록에 명시된 절차이고 `run_e1ms.sh` 가 FREEZE 조상 · 문서 불변 · code/Demo 불변을 검사한 것이 로그 · diff 로 확인된다.
- §6.4 의 채점 11 ("해당 없음") 과 §6.5 · §6.6 의 서술은 파일 사실과 모순이 없다. `e4-cost` 는 E1+ 뒤에 병합됐다 (1051c9b6 09:06:55 CDT).

## 5. 검증하지 못한 것
- 사용자 승인 "다 진행하자" 의 원문 · 시각 (세션 기록) — 파일 간 (DECISIONS 473 · 등록 §6.1 · §6.5 · EXPERIMENTS 93 · 94 · WORK_QUEUE · 다른 감사 넷) 인용이 같고, "08:39 CDT 이전" 이 병합 확인 시작 08:40:14 CDT 와 일관한 것까지만.
- 같은 시각 Codex · Fable 프로세스의 **실제** CPU 사용 (affinity · 부하) — 지나간 일이라 수단 없음 (§6.6 도 같은 말); 파일에 적힌 `taskset` 인자와 시작 시각만 확인.
- `run_e1ms.sh` 의 시작 전 전제 검사 (`raw_D2SITEMS` 비어 있음 · 다른 runner 없음 · V1LS 스크립트 없음) 는 ABORT 가 없었다는 로그와 결과 raw 로만 간접 확인.
- 부트스트랩은 §1.4 의 서술 (RNG 소비 순서) 대로 독립 구현해 소수 3 자리까지 같았고 등록 도구 재실행도 바이트 동일했다; 다른 RNG 소비 순서 (예: 재표본마다 arm 별 index) 를 쓰면 구간이 조금 달라질 수 있으나 그 선택은 동결된 것이다.
- §0.2 의 대수 성질 · §0.4 확인 1 · 2 (site 정의 편차 3.94e-16, 등방 입력 차 0) 는 `check_ms.out` 을 읽었을 뿐 다시 돌리지 않았다 (동결 전 개발 확인; 이번 감사 범위는 §6).

## 6. 결론
- **§6.2 의 주 라벨 (iii) 과 보조 라벨 (iii), 점별 a:b · p, pooled, D, POWERED, 실패 수 표, L = +0.14 dB [+0.05, +0.22] (censored 0 %), 보조 +0.01 dB [−0.04, +0.04] 는 raw 에서 §1.4 규칙을 다시 적용해 전부 재현된다** (자동 162 / 162 일치; 도구 재실행 바이트 동일).
- **§6.3 의 문장은 §2.1 · §2.2 · §2.4 의 틀과 글자 단위로 같고 §2.3 금지 문구가 없다. §6.4 의 채점 8 / 10 (빗나감 2 · 6) 은 관대하지 않다.**
- 출처 · 무결성: 192 청크 계획 · meta · 실행 커밋 9a2c9fd4 · genie 비트 동일 · FREEZE 뒤 §0–§5 불변 · 실행 창 안 main 커밋 없음 · s5 / FREEZE / 병합 / 실행 커밋의 관계 · 병합 확인 (a)(b) 의 사실 · V1-ms 가 test 시행에서 이 실행 전에 돈 적 없음 (23,001 파일 스캔; test skip 의 V1-ms 키는 전부 V1 의 이름 바꾼 합성 raw) — 모두 확인.
- 고칠 것은 DECISIONS 동결 줄의 FREEZE 시각 1 건 (N1) 과 §6.1 의 같은 시각 프로세스 목록 누락 1 건 (N2) 뿐이며 둘 다 판정 · 라벨 · 인용 수치를 바꾸지 않는다.
