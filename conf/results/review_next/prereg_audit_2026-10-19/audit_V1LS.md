# 기록 감사 — NEXT_EXPERIMENTS_V1LS.md §6 (V1 저 σ 변형 test; 태그 U28LSQ · U28LS16 · D2LSQ · D2LS16)

- 감사자: Claude Code (Fable 5.1 서브에이전트, 독립 기록 감사; `gcap/PROMPT_SERVER_COMMON.md` §3 의 "기록 감사 1회"). 감사 시각 2026-10-19 22:48 ~ 23:08 KST (= 10-19 08:48 ~ 09:08 CDT; `date` · `TZ=America/Chicago date` 로 읽음).
- 감사 대상 판: 작업 트리 = HEAD **9a2c9fd4** (10-19 22:42:42 KST; E1+ 실행 커밋). 등록 문서 · `v1ls/` · `lowsig/` 는 작업 트리와 HEAD 동일 (`git diff --stat HEAD` 비어 있음). 동결 §0–§5 는 FREEZE **2a9b4d14** (= `v1-lowsig` 병합; 문서는 브랜치 tip 4fbf093a 와 diff 0) → 실행 커밋 1d706648 → §6 전사 1659a0e4 → §6.7 보충 fef2594a → HEAD 에서 **삭제된 줄 0, 추가는 188 행 (`## 6.`) 뒤뿐** (`git diff -U0 2a9b4d14 HEAD -- NEXT_EXPERIMENTS_V1LS.md`: hunk `@@ -188,0 +189,51 @@` 하나).
- 방식: 읽기 전용. 새 파일은 이 폴더에만 (이름 V1LS): `recompute_v1ls.py` → `recompute_v1ls.out` (raw 청크 npz 를 numpy 로 직접 읽음; `conf/code` · `Demo` 미import; 부호검정 · 판정점 · power guard · 라벨 · SNR@0.1 격차와 90 % paired bootstrap (B 2000, seed 20260925) · ΣF · R 과 bootstrap (B 2000, seed 20260926) · MONOTONE · SUFFIX 를 등록 문구대로 따로 구현, exact p 는 scipy `binomtest` 로 교차 확인; 커밋된 `compare_<T>.txt` 의 줄을 같은 서식으로 만들어 문자열 대조), `rerun_compare_V1LS_<T>.txt` ×4 + `rerun_compare_V1LS_diff.txt` (등록 도구 `code/v1ls_compare.py` 를 `--out` 만 이 폴더로 바꿔 재실행, 커밋본과 `cmp`), `rerun_accept_V1LS.txt` (`code/eval_accept.py` ×4 재실행). CPU `nice -n 10 taskset -c 14-17`, GPU 미사용 (`CUDA_VISIBLE_DEVICES=`). 수신기 시뮬레이터 · `run_*.sh` 미실행. git 상태 · 기존 파일 변경 없음. (같은 폴더의 `*gcap*` · `*sbl*` · `*e5*` 파일은 같은 시각에 돈 다른 감사의 것이다.)

## 1. 재계산한 것과 재현 여부

| 항목 | 방법 | 검사 값 수 | 결과 |
|---|---|---|---|
| raw 청크 계획: 네 run 각각 SNR 집합 = 등록 격자 (QPSK 9 점 −3…+21, 16-QAM 7 점 +3…+21), 점마다 {(40k, 40): k = 0..63}, 파일명 패턴 (UMi28·eig / S2·dft), 구멍 · 중복 없음; `\|failed` 키 0, 비유한 blk_err 0, blk_err ∈ {0, 1}, 여섯 arm × KEYS_RAW 7 키 모양 (40, 16) | 파일명 파싱 · numpy | 4 × 2 | **재현** (576 · 448 · 576 · 448 청크; raise 된 블록 0 = §6.1 "NOTE 0") |
| 수용 ② meta (전 청크 2048 개의 서로 다른 값): `run\|git` 1d706648, `meta\|modulation` (16qam / QPSK 는 키 없음 = qpsk), 16-QAM `payload_bits` 90 · `protocol` E5-qam16-v1, `lowsig_arms` 있음, `lowsig_s_lo` 0.032681101782796075 · 0.033062204571989696 (= 동결 격자 UMi28 · D2 의 하한 3.2681e-02 · 3.3062e-02), `wide_ckpt_id` sha16 03cc9005164fe31d epoch 493 best 493 role best · bd48a8860ca2543e epoch 1028 best 1008 role last, `wide_sigma_tag` UMi28HSUd · HSUd, `stagec_ckpt_id` 6f3a1b9490864af1 epoch 379 role best · 4443921ce8d5c4a1 epoch 1784 best 1764 role legacy-last, `kron_K` 4096 · 1024, `ll_val\|kron` 5.797910431000217 · −11.459169831224418 (\|Δ\| ≤ 1e-9), `jobs` 96, `worker_gb` 1.5, `run\|n` 40 · `iters` 16 · `seed` 20260926 · `dtype` complex128/float64 | 전 청크 비교 | 76 | **재현** |
| 수용 ③ (같은 시행): 기준 raw (`raw_U28B16e4` · `raw_U28QAM16` · `raw_B16e4k` · `raw_D2QAM16`) 와 같은 이름의 청크 448 개 ×4 에서 V1 · b\* · genie 의 **arm 접두가 붙은 모든 키** (KEYS_RAW 7 + `guardH` + `clip` = 9 키; 등록 범위보다 넓음) | `array_equal(equal_nan)` | 4 × 11648 배열 | **재현** (다른 배열 0, 한쪽에만 있는 키 0 — §6.1 · `accept_ref_recheck.txt` 의 "448 청크 · 0 differing" 과 일치) |
| 실패 수 / 2560 (= BLER@16 분자) 여섯 arm × SNR | numpy 직접 | 32 행 (192 값) | **재현** (`compare_<T>.txt` 끝 표와 행 단위 문자열 동일) |
| L1: V1 → X 의 +18 · +21 dB a:b · exact 양측 p (`.2g`) · 판정 순서 (a)→(c)→(b) · MONOTONE 세 실패 수와 yes/no — X = C (PRIMARY) · A · B | 직접 | 12 × 2 줄 | **재현** (PRIMARY (a) ×4, MONOTONE yes ×4; A yes·yes·no·yes, B no·yes·no·no) |
| L2: 판정점 (b\* 앵커, BLER ∈ [0.005, 0.9], \|log10(BLER/0.1)\| 최소 3 점) · 점별 a:b · p · pooled · power guard (3 점, 불일치 ≥ 6 인 점 ≥ 2) · 2/3 규칙 · 라벨 — 12 쌍 | 직접 | 12 × 3 줄 | **재현** ((i) ×12; QPSK 의 +18 · +21 dB 는 b\* BLER 7/2560 · 6/2560 · 4/2560 < 0.005 라 후보에서 빠짐) |
| SNR@0.1 격차 (b\* − X) 점추정 · 90 % paired bootstrap 구간 · censored % | 자체 구현 (log-linear 첫 교차, `default_rng(20260925)`, SNR 마다 같은 재표집 index 를 두 arm 에) | 12 줄 | **재현** (PRIMARY +0.58 [+0.30, +0.86] · +0.69 [+0.43, +1.02] · +1.40 [+1.21, +1.63] · +3.33 [+2.51, +4.28]; A · B 도 `.2f` 까지 동일) |
| 판정점 ΣF (b\*, X, genie) · R · 90 % paired bootstrap (undefined 수 포함) | 자체 구현 (`default_rng(20260926)`, 판정점에 걸쳐 같은 index) | 12 줄 | **재현** (PRIMARY R 0.162393 [0.121, 0.202] · 0.197880 [0.159, 0.236] · 0.502030 [0.464, 0.538] · 0.678337 [0.631, 0.729]; undefined 0) |
| SUFFIX 규칙 ((i) 의 판정점에서 b\* 유의 우세, (ii) 가 아닐 때 +18 · +21 dB 의 b\* 유의 우세, 같은 SNR 한 번) | 직접 | 12 | **재현** (none ×12) |
| `PRIMARY LABELS` 줄, 보고 전용 V1 → C 다른 격자점 점별 a:b · p 와 ≤ +15 dB pooled (123:128 p .8 · 95:74 p .12 · 82:87 p .76 · 173:185 p .56), b\* → C +18 · +21 dB (4:2 · 6:1, 44:16 · 35:8, 3:1 · 4:0, 68:11 · 64:7) | 직접 | 4 + 24 + 4 + 8 | **재현** |
| exact p 교차 확인: 정수식 min(1, 2·ΣC(n,i)/2ⁿ) 대 scipy `binomtest` (L1 2 점 + 판정점 3 점, 12 쌍) | 두 구현 | 60 | **일치** (상대 1e-9 이내; 0 은 둘 다 0) |
| §6.2 각주 "판정점의 점별 p 는 모두 < .005 (최대 U28LSQ +6 dB 53:27, p = .0049)" | 직접 | 1 | **재현** (p = 0.004868; 12 판정점 가운데 최대) |
| 예측 4 (QPSK +18 · +21 dB 의 V1 > b\*: 934 > 7, 2556 > 6, 2258 > 4, 2559 > 6) · 예측 5 (≤ +15 dB 합 C ≤ V1 + 2√V1: 2669 ≤ 2767.2 (V1 2664), 4006 ≤ 4153.9 (4027), 524 ≤ 564.6 (519), 1917 ≤ 1992.3 (1905)) | 직접 | 4 + 12 | **재현** |
| 등록 도구 재실행: `v1ls_compare.py` ×4 (HEAD 9a2c9fd4 의 `code/` 는 깨끗하고 `v1ls_compare.py` · `analysis.py` · `recovery_ci.py` · `common.py` · `eval_accept.py` · `Demo/` 는 FREEZE 이후 변경 없음) | `cmp` 커밋본 | 4 파일 | **바이트 동일** (`rerun_compare_V1LS_diff.txt`) |
| `eval_accept.py` (§1.3 인자 그대로: tag:role:sha16:C2, prior, ntrain, kron-K, ll-val, points, chunk 40, n 2560) | 재실행 | 4 | `ACCEPT: OK` ×4, rc 0 (`rerun_accept_V1LS.txt`) |
| **개발 선택 규칙 재적용** (`lowsig/SELECTION_RULE.md` 규칙 1–5): 12 점 × 5 arm 실패 수, M (옛 C: V1 2279 · b\* 148 · A 114 · B 122 · C 104; 새 C: C 110), +15 dB 해 없음 (V1 55, 한계 69.83; A 55 · B 55 · C 53 / 56 통과), PRIMARY = C (두 번 다); M4 4 run (92 / 111.18, 60 / 70.97, 60 / 74.36, 67 / 85.61 ok) | `screen_*_320_snr*.npz` · `screenC_*` · `screenCd_*` 를 직접 읽음 | 2 × 15 + 4 | **재현** (`select_lowsig.out` · `select_lowsig_d.out` 의 줄과 문자열 동일) |
| §0 S1 paired (새 C: A:C 14:10 p .54 · +15 만 5:6 · +18/+21 만 9:4 p .27; B:C 20:8 p .036 · 15:2; b\*:C 45:7 p 7e-8; V1:C 2175:6 · 2170:0; 옛 C: A:C 15:5 p .041, B:C 23:5, b\*:C 49:5), M4 paired (V1:C 8:8 · 9:13 · 1:2 · 8:6, b\*:C 20:5 · 58:11 · 8:0 · 34:11), 예측 6 의 개발 수 (3/0/0, 33/21/9, 0/0/0, 20/15/9), 예측 7 표 (b\*:C 12 점과 p) | 직접 | ≈ 60 | **재현** |
| 새 C 의 "21 개 개발 점 격자 밖 질의 0" | `screenCd_*.txt` 21 파일 | 21 | **재현** ("out-of-grid queries 0/…" 21 건; screenCd npz 의 `grid` 키 = [0.011747, 0.83725] · [0.011709, 0.84516]) |
| 체크포인트: sha256 (V1 6f3a1b94…3d1c · 4443921c…2f29, C 03cc9005…f245 · bd48a886…a29b = 문서 `WIDE_U28` · `WIDE_D2` 줄, 문서에 각 1 줄), `torch.load` 의 epoch/best_epoch/role/sigma_tag/split_hash/rung/attempt (U28 C 493/493/best/UMi28HSUd/98cc168731eb922c; D2 C 1028/1008/last/HSUd/a00951cf75b852a6, stopped_by patience; V1 379/379/best, 1784/1764), 학습 로그 (σ 범위 "log-uniform draw over [1.1747e-02, 8.3725e-01]" · "[1.1709e-02, 8.4516e-01]", 513 · 1028 epoch patience 정지, 시작 10-18 19:01 · 18:57 CDT, 끝 19:46 · 20:28 CDT; V1 로그 399 · 1784 epoch 정지) | `sha256sum`, `torch.load(cpu)`, 로그 | ≈ 30 | **재현** |
| git · 동결: FREEZE 2a9b4d14 가 1d706648 의 부모; `git log -1 -- v1ls_s5.txt` = 1d706648 (HEAD = s5 마지막 커밋 조건); `git diff 2a9b4d14 1d706648 -- conf/code Demo` 비어 있음 (실행 커밋은 s5 · DECISIONS · WORK_QUEUE · 병합 확인 기록 · `logs/v1ls_smoke.log` 만); s5 = `FREEZE 2a9b4d14… / PRIMARY M-ours-dscore-C-V1-wide / WGB_* 1.5 ×4`; 실행 창 (10-18 22:13 – 10-19 03:13 CDT) 안 main first-parent 커밋 **없음** (1d706648 22:13:24 CDT 는 체인 시작 로그 `git 1d706648` 보다 앞, 1659a0e4 는 03:17:38 CDT) — 그 창의 커밋 7 개 (7326010c … e6ac9e65) 는 모두 `e1-ms` 브랜치 (worktree `~/t2_wtMS`) 이고 1659a0e4 의 조상이 아님 | `git log/diff/merge-base`, `git worktree list` | — | **재현** |
| 시각 (로그 · 커밋 · mtime, KST→CDT): 규칙 커밋 1f4c5c4c 17:21:28 < 큰 선별 첫 출력 17:41 (`log_screen2_D2_qpsk_21.txt` 07:41 KST); 추가 절 08e47ec2 18:51:00 < grid_dev · m4 시작 18:51 (`diag_lowsig.log`, git 08e47ec2) < C 재학습 18:57 < 5af1b147 18:58:23 < M4_DONE 19:26 · TRAIN_CD_DONE 20:28 · EVAL_CD_DONE 20:38; `select_lowsig_d.out` 9fe40517 20:40:38; WIDECHK 20:43–20:46; v2.2 4fbf093a 10-19 11:46:41 KST = 10-18 21:46 CDT; FREEZE 21:56:49 CDT; MERGECHK 21:56–22:04 (`v1ls_smoke.log`); 실행 커밋 22:13:24; run 1 22:13 → 23:49 runner exit (96.2 min) → 23:50 DONE; run 2 23:50 → 01:07 (77.2); run 3 01:07 → 02:18 (70.5); run 4 02:18 → 03:13 (55.1); CHAIN_DONE 03:13; `accept_ref_recheck.txt` 03:15:47; §6 커밋 03:17:38; 기록 커밋 03:18:21; §6.7 · `v1ls_guard_incident.txt` 03:29:27 CDT; Codex 중단 `cost_bench.out` mtime 22:48:57 CDT | `git log`, 로그, `ls --time-style=full-iso` | ≈ 30 | **일치** |
| 기록 줄: DECISIONS 465 (실행 커밋 · 승인 · MERGECHK · s_lo 두 값 · 명령) · 467 (결과 전부 — a:b 8 쌍, 격차 4, R 4, pooled 4, V1 붕괴 4, 예측 7/7, §6 1659a0e4) · 469 (사건); EXPERIMENTS 91 (시각 · 명령 · 시행 · arm · 커밋 · 자원 · 결과 · 로그 · raw · Demo 잠금 3b5c0a375509 = `LOCKED.md` 7 행); WORK_QUEUE 3 · 16 · 65 | 읽어 대조 | ≈ 80 | **일치** |
| §6.3 문장: 여덟 문장이 §2.1 틀 (L1 (a) 문장 + MONOTONE yes 괄호 + V1-wide 설명; L2 (i) 문장 + U28 에만 "[K 상한 민감: 외삽 불가]" + SUFFIX 없음 + 설명) 과 **문자열 동일** (프로그램 대조; V1-wide 설명 8 회) | 프로그램 | 8 | **일치** |
| §2.2 금지 문구 ("동등" · "비열등" · "완전히 해결" · "모든 SNR 에서" · "원인을 증명" · "σ 범위만의 효과"), 네 run 을 합친 라벨 문장 | grep · 읽기 | — | 없음 (§6.3 끝의 "쓰지 않는다" 열거만) |
| 예측 3 의 기준 기록: `tables_D2_U28B16e4.txt` 371–372 행 `b* → V1` 판정점 +3 · +6 · +9, `tables_D2_B16e4k.txt` 367–368 행 −3 · 0 · +3, E5 §6 UMi28 +12 · +15 · +18 (133 행) · D2 +9 · +12 · +15 (140 행) | 읽기 | 4 | **일치** (수용 ③ 통과로 b\* 실패 수가 같아 기계적; §6.5 도 그렇게 적음) |
| 교차 기록 일관성 (수용 ③ 의 귀결; 등록 항목은 아님): V1LS 의 b\* → A (A ≡ V1 at ≤ +15 dB) 가 옛 기록과 같음 — U28LSQ 76:38 · 50:22 · 35:13, pooled 161:73 = `tables_D2_U28B16e4` `b* → V1`; D2LSQ 302:50 · 117:21 · 35:7, 454:78 = `tables_D2_B16e4k`; D2LS16 157:23 · 121:17 · 93:16, +3.44 [+2.62, +4.33], ΣF 922/607/465 R 0.689278 [0.642, 0.736] = E5 §6 D2; U28LS16 +12 72:17 · +15 49:20 = E5 UMi28; V1 의 16-QAM +18 · +21 실패 1844 · 2543 · 2485 · 2557 = §0 의 E5 기록 | 읽기 | 20 | **일치** |

합계: 자동 대조 **350 값 중 0 불일치** (`recompute_v1ls.out` 끝 TALLY), 등록 도구 재실행 4 파일 바이트 동일 + 수용 ① 4 OK, 수동 대조 약 300 값 (§6.1–6.7 · §0 · §1.1 · DECISIONS · EXPERIMENTS · WORK_QUEUE 의 수치 · 시각 · 커밋) 중 **0 불일치**.

## 2. 규칙 재적용 (동결 §1–§2 → 재계산 값)

- **PRIMARY**: `SELECTION_RULE.md` 규칙 1–3 을 `screen_*` · `screenCd_*` 에서 다시 적용 → +15 dB 해 없음 통과 A · B · C, M 최소 C (110 < A 114 < B 122) → **C**. 옛 C 로도 C (104). 추가 절 (C 재정의 · M4) 은 그 평가 결과 (M4_DONE 19:26, EVAL_CD_DONE 20:38 CDT) 보다 앞선 08e47ec2 (18:51:00 CDT). s5 의 `PRIMARY M-ours-dscore-C-V1-wide` 와 일치.
- **L1** (순서 (a)→(c)→(b)): 네 run 모두 두 점에서 a > b 이고 p < .05 → **(a)**; (c) 조건 (어느 점에서든 b > a, p < .05) 해당 없음. MONOTONE: C 의 실패 24/5/1 · 273/154/80 · 3/2/2 · 132/90/66 → +18 ≤ +15, +21 ≤ +18 → **yes** ×4 → §2.1 의 "(V1 의 고 SNR 붕괴가 이 격자에서는 나타나지 않음)" 괄호가 맞다.
- **L2**: 판정점 (b\* 앵커) +3·+6·+9 / +12·+15·+18 / −3·0·+3 / +9·+12·+15; 모두 3 점 · 불일치 쌍 ≥ 6 인 점 3 → POWERED; "second arm fewer failures" (a > b, p < .05) 3/3 ×4 ≥ 2/3 → **(i)** ×4; (ii)·(iii)·(iv) 해당 없음. U28 두 run 에만 "[K 상한 민감: 외삽 불가]" (§2.1). SUFFIX: (i) 의 판정점에서 b\* 가 유의하게 적게 실패한 점 없음, +18 · +21 dB 의 b\* → C 는 네 run 모두 a ≥ b (b\* 가 더 많이 실패) → **none** ×4 → 문장에 붙는 접미 없음.
- **보고 전용** (라벨 문장 없음): A · B 의 L1 (a) · L2 (i) ×4, MONOTONE · 격차 · ΣF · R · SUFFIX 는 §6.4 · §6.7 과 같다.
- **다중성 · 단독 문장**: §6.3 은 run 마다 L1 · L2 문장 하나씩 (8 문장), 합친 문장 없음; "4/4" 는 §6.5 채점에만.
- **예측 채점 (§3 → §6.5)**: 1 (a) ×4 적중; 2 (i) ×4 적중; 3 판정점 = 기록 — 적중이나 "기계적 · 증거로 세지 않음" 으로 적힘 (§3 N4 그대로); 4 네 점 모두 V1 > b\* 적중; 5 네 run 모두 한계 안 적중 (수치 재현); 6 MONOTONE yes ×4 적중 (`PRIMARY LABELS` 줄 기준); 7 `(suffixes 0)` ×4 적중. **관대한 채점 없음** — 모든 예측이 사전에 수치 기준을 가졌고 그 기준대로 채점됐다.
- **test / 개발 분리**: 변형 선별 (`diag_lowsig.py` · `eval_c.py` 는 `skip0 >= DEV_SKIP0 = 2560` 을 assert; 파일명 6000_320 · 5120_320 · 5440_40), M4 (같은 개발 시행), σ 격자 재측정 (`measure_grid_dev.py` SKIP = 2560 → `log_grid_*d.txt` "trials 2560..2623"), C 학습 (train 144000 / val 16000, split_hash = V1 과 동일), 스모크 · 플래그 없음 확인 (6320.. · 5520..), WIDECHK · 병합 확인 (6000.. · 5120..) — 모두 개발 시행 또는 train/validation. test 번호 시행을 쓴 것은 DECISIONS 4c08302d (461 행) 가 적은 대로 **σ 격자 측정** 뿐: `code/sigma.py` `measure_point` 는 첫 커밋 de46d6ec 부터 지금까지 14 개 버전 모두 skip 없이 `range(n)` (n = N_MEAS = 64) 을 돈다 (이 감사에서 전 버전 grep) → 동결 격자 (`sigma_grid_D2.txt` 09-20, `_UMi28.txt` 09-27, n = 64) 와 옛 HS · UMi28HS (10-18 17:00 CDT, −3…+24 dB) 는 시행 0..63 의 라벨 없는 질의 통계다. 그 공개는 사실과 맞고, C 의 학습 σ 범위 **상한** 이 그 동결 격자에서 왔다는 정정 (DECISIONS 463 행, 등록 §0 · §1.1 · §2.1 · §6.3 의 모든 문장) 도 격자 파일 (`sigma_grid_D2_HSUd.txt`: "frozen [3.3062e-02, 8.4516e-01] wide [1.1709e-02, 7.9057e-01] → union [1.1709e-02, 8.4516e-01]") 과 맞는다. 옛 C (HSU · UMi28HSU; test 번호 시행으로 잰 하한) 는 test 에 쓰이지 않았다 (전 청크 `wide_ckpt_id` = 새 C sha16).
- **실행 중 사건** (E4 Codex 중단): `v1ls_guard_incident.txt` 의 래퍼 출력 (시작 22:17 CDT, rc 1, "turn interrupted") 과 scratchpad `cost_bench.out` · `codex.log` 의 mtime 22:48:54–57 CDT 가 DECISIONS 469 의 "22:48 CDT 중단" 과 맞는다. 결과 무관의 근거: 가드 (`pgrep -f "[r]unner.py run"`) 는 run 의 **시작 조건** 에서만 평가되고, 뒤의 세 run (23:50 · 01:07 · 02:18 CDT) 은 ABORT 없이 시작해 `V1LS_DONE ok=4 fail=0` 으로 끝났다 (`run_v1ls.log`); Codex 는 별도 worktree (`~/t2_wtCost`) 에서 돌았고 main 의 `code/` · `Demo/` 청결은 run 마다 다시 검사됐다; 수신기는 CPU complex128 결정적 경로라 동시 부하는 시간에만 영향을 준다.

## 3. 발견

### MUST-FIX
없음 — §6 의 판정 · 라벨 · 인용 수치 · 채점 가운데 틀린 것을 찾지 못했다.

### SHOULD-FIX
없음 — DECISIONS · EXPERIMENTS · WORK_QUEUE · §6 의 기록 사실 (수치 · 시각 · 커밋 · 수용 범위 · 사건) 가운데 원자료 · 로그 · git 과 어긋나는 것을 찾지 못했다.

### NIT
없음.

### 사실 메모 (지적 아님; 판정 · 수치 · 기록 사실에 영향 없음)
- 등록 §0 · §5 는 WIDECHK 를 "(7052e5f2; 10-18 20:43–20:46 CDT)" 로, EXPERIMENTS 90 행은 "0d179feb (widechk)" 로 적는다. `logs/v1ls_smoke.log` 의 "[v1ls widechk 10-18 20:43 CDT git 0d179feb] start" 대로 실행 시 HEAD 는 0d179feb (main → v1-lowsig 병합, 20:43:15 CDT) 이고 7052e5f2 (20:46:16 CDT) 는 그 결과 파일을 담은 커밋이다. 두 기록 모두 참이다 (하나는 실행 HEAD, 하나는 결과 커밋).
- §5 추정 시간 "2–4 h" 에 대해 실제 체인은 5 h 00 min (22:13 → 03:13 CDT). 추정치라 기록 오류가 아니다.
- `v1ls_guard_incident.txt` 가 옮긴 래퍼 출력의 `output /home/HTJ/t2/reviews/20261019-121729-codex_write_cost_bench.md` 는 존재하지 않는다 (중단된 turn 이라 보고 파일이 만들어지지 않은 것으로 보인다; 래퍼 줄을 그대로 옮긴 것이고 기록의 주장이 아니다).
- 수용 ③ 의 대조 수는 `run_v1ls.sh` 가 로그에 남기지 않아 (step 의 stdout 은 화면) `accept_ref_recheck.txt` 로 다시 셌다 — §6.1 에 공개돼 있고, 이 감사의 독립 대조 (9 키 11648 배열 ×4, 차이 0) 가 그 값을 확인한다.

## 4. 검증하지 못한 것
- tmux 세션 이름 `v1ls`, 체인 화면의 원래 accept_ref 출력 (남아 있지 않음), 사건 메모의 pid (3018532 · 3018539) 와 tmux `codex_cost`: 지금 확인할 파일 없음. Codex 중단 시각은 scratchpad 파일 mtime (22:48:54–57 CDT) 으로만 뒷받침된다.
- §6.7 의 verifier 자신의 재실행 주장 (compare 바이트 동일, 독립 구현, 수용 ① · ③ 재확인) 은 다시 검증하지 않았다 — 이 감사가 같은 항목을 따로 했고 결과가 같다.
- run 시작 사이 (실행 중) 에 main 작업 트리의 `code/` · `Demo/` 가 계속 깨끗했는지는 네 번의 시작 검사 (통과) 와 `git diff FREEZE HEAD -- code ../Demo` 비어 있음 외에 기록이 없다. 같은 시각 다른 CPU 작업 (GCAP 적합 등) 과의 자원 공유는 이 감사 범위 밖 (결정적 CPU 경로라 수치에 영향 없음).
- E5 개발 시행 (16-QAM 5120..5439) 에서 "b\* 의 BLER 만 열람된 적 있음" (SELECTION_RULE.md) 과 "작성자가 test 를 보기 전에 §0–§5 를 고정했다" 는 파일로 증명할 수 없는 진술이다 (커밋 순서 — FREEZE 21:56 < 실행 22:13 CDT — 만 확인).
- 격자 밖 질의 0 (`screenCd_*.txt`) 은 개발 래퍼 `eval_c.py` 의 집계를 읽은 것이고 다시 세지 않았다.
- `lowsig/` 의 작은 선별 (5440..5479, n 40) 은 규칙 커밋 전에 본 결과라고 SELECTION_RULE.md 가 적는다; 그 수치 자체는 이 감사 범위 밖.
- SNR@0.1 격차 · R 의 bootstrap 은 자체 구현으로 재현했고 (seed · 재표집 순서를 등록 서술대로), 등록 도구 재실행과도 일치한다 — 다른 재표집 규약 (예: SNR 마다 다른 index 대신 같은 index) 으로 구간이 얼마나 움직이는지는 보지 않았다 (등록 밖).

## 5. 결론
- **§6.2 의 라벨 L1 (a) ×4 · L2 (i) ×4 는 §1.4 · §2.1 의 동결 규칙을 raw 에서 다시 적용해 재현된다** (판정점 · power guard · 2/3 규칙 · MONOTONE yes · SUFFIX none 포함); §6.3 의 여덟 문장은 §2.1 틀과 문자열까지 같다.
- §6.4 · §6.5 · §6.7 의 수치 · 채점 (7/7, 3 은 기계적) 과 DECISIONS 465 · 467 · 469, EXPERIMENTS 91, WORK_QUEUE 3 · 16 · 65 의 수치 · 시각 · 커밋은 원자료 · 로그 · git 과 일치한다.
- PRIMARY = C 는 결과 전에 커밋된 선택 규칙의 재적용 결과와 같고, 변형 선별 · σ 격자 재측정 · C 학습은 개발 시행 · train/validation 만 썼다; test 번호 시행 (0..63, 라벨 없는 질의 통계) 의 사용은 σ 격자 (동결 격자 상한 · 옛 HS 격자) 에 한하며 기록된 공개와 코드 이력이 맞는다.
- 고칠 것을 찾지 못했다 (MUST 0 · SHOULD 0 · NIT 0).
