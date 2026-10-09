# 결과 정리 (논문용)

웹에서 해석할 때 가져가는 파일. 표와 수치는 반드시 EXPERIMENTS.md의 행(커밋·설정)을 가리킨다. 해석과 결론은 여기 쓰지 않는다.

- 갱신: 2026-09-23 17:59 CDT (커밋 8cf4b954; 처음에 18:05 CDT 로 잘못 적었던 것을 정정), 기준 커밋 6d56404a. 절마다 초안 작성자와 별도 검증자가 원 결과 파일·EXPERIMENTS.md 행과 대조했다(워크플로 wf_6422f535-670; 검증 메모 원문 `conf/results/review_next/results_md_raw/sections_wf_6422f535.json`).
- 추가: 2026-09-24 18:31 CDT — §1.9 N′ = 3.2e5 (B32e4) 추가(Opus). 수치는 결과 파일·raw 에서 직접 옮김; 이 절은 아직 별도 검증자 대조를 거치지 않았다.
- 추가: 2026-09-26 21:20 CDT — §7 C6 1.6e5, §8 K1·K2, §9 Tp≥Nt Pareto, §10 채널 모델 확장(D3·SV8e·38.901), §11 그림 목록 추가(Opus 5.5). 수치는 등록 문서 §6(기록 감사 5819db19 정정 반영)·결과 파일에서 옮김; **별도 검증자 대조 완료(`conf/results/review_next/results_md_raw/verify_sections7_11_2026-09-26.md`: 수치 오류 0, 위생 정정 5건 반영)**.
- 추가: 2026-10-03 17:03 CDT — §18 SEEDS3_16e4 · §19 HISNR16e4 · §20 SPARSE16e4 · §21 SCALE16e4 추가, §11 에 F30~F32 행 추가(Opus 5.5 서브에이전트, 기준 커밋 9253a0b5). 수치·라벨·캐비엇은 각 등록 §6.1 (기록 감사 §6.2 정정 반영)·결과 파일에서 옮김; **별도 검증자 대조 완료**(Fable 5.1 서브에이전트; 오류 0·규칙 위반 0, 위생 정정 3 반영; `conf/results/review_next/prereg_audit_2026-10-03/audit_RESULTS_update.md`).
- 추가: 2026-10-05 18:37 CDT — §22 SEEDSNR16e4 추가 (Opus 5.5). 수치·라벨·캐비엇은 등록 §6.1 (기록 감사 §6.2 정정 반영; scale c689a935, 결과·문서 파일은 main 에 사본) 에서 옮김; 별도 검증자 대조는 아래 §22 머리에 적는다.
- 추가: 2026-10-08 23:23 CDT — §24 SITE16e4 추가 (Opus 5.5). 수치·라벨은 등록 §6.1 (기록 감사 §6.2: raw 에서 독립 재계산, 수치 정정 없음)·원본 출력에서 스크립트로 옮김.
- 판정 문구는 사전 등록 라벨(지지 / 판정 불가 / UNDECIDED / 기각 / PASS 등) 그대로다. 수치를 인용하기 전에 **§6 인용 주의**를 먼저 읽는다.
- 목차: §1 헤드라인(Stage C, 동일예산) · §2 review_next 진단·ablation · §3 A1 위상 augmentation · §4 P3 반복 루프 규칙 · §5 C6 (Nr=16) · §6 인용 주의 · §7 C6 동일예산 1.6e5 · §8 K1·K2 · §9 파일럿 오버헤드(Tp≥Nt) · §10 채널 모델 확장 · §11 그림 목록 · §12 ALD · §13 비정상 A·B (DOP·ROT) · §14 비정상 B′·C (ROTMIX·S2v) · §15 DOP·ROT 보충 (SUPP) · §16 정적 13 baseline (STATIC) · §17 genie 고SNR 바닥 진단 · §18 시드 강건성 2 (SEEDS3) · §19 고SNR 보강 (HISNR) · §20 희소 baseline (SPARSE) · §21 배열 규모 확장 (SCALE) · §22 시드 강건성 3: Nr 16/32 (SEEDSNR)

---

## 1. 헤드라인: Stage C, D2 셀 C2 동일예산 비교 (N_train 1e4 / 4e4 / 1.6e5; 3.2e5 는 §1.9)

**EXPERIMENTS.md 행**: `2026-09-21 14:00 ~ 09-22 21:45` (Stage C). 이 행에 적힌 커밋은 `8fb27f5 (마감 시점)`이다. 각 표에 붙인 커밋은 해당 결과 파일 머리말의 `git commit` 값이다.

공통 조건은 다음과 같다.
- testbed D2, prior S2, 셀 C2 (8x4, T=16, **Tp=4**, K=42)
- SNR당 **n=2560**, BLER@16 (outer 16회), 수신기는 CPU complex128
- 짝지음 검정은 사전 등록된 판정점 3개 규칙을 따른다. 앵커는 `M-ours-bstar`, 창은 BLER ∈ [0.005, 0.9]이다.

> **이 절에 적용한 정정**
> - **(평가 가중치)** 학습 arm(V0/V1/V4/V4b)은 best가 아니라 **마지막 epoch EMA**로 평가됐다.
>   - 헤드라인 체크포인트 `ckpt/d2sx_N160000_a1.pt`: 평가 가중치는 last-EMA @1784 (ema `a43f1105eb27a29b`, val 3.519602e-01)이다. best val 3.519379e-01 @1764의 가중치는 저장되지 않았다(**BEST_WEIGHTS_UNAVAILABLE**).
>   - N=1e4 a1/a2/a3: epoch 673/657/662 (best 653/637/642)
>   - N=4e4 a1: epoch 1051 (best 1031)
>   - 출처: DECISIONS `[2026-09-23 11:47 KST] 정정 — Stage C 학습 arm 은 best 가 아니라 마지막 epoch EMA 로 평가됐다 (review_next P0-1b)`, `[2026-09-23 12:54 KST] 정정 — docs/EXPERIMENTS.md:21(…)의 읽는 법` (2)항
> - **(게이트 표기)** EXPERIMENTS 행의 "헤드라인: 게이트 통과 + 동일예산"은 **"D1 형제 게이트 PASS 레시피 + 동일예산"**으로 읽는다.
>   - D2 체크포인트에는 게이트 행이 없다. `tables_D2_B16e4k.txt:45`에 `NO GATE RECORD mentions d2sx_N160000_a1.pt -- UNVERIFIED here`로 적혀 있다.
>   - PASS 판정은 `LADDER_C.md:1`의 `sx_N160000_D1.pt` 행이다: GA 9.879e-16 / GB +0.27% / GC 0.0999 / GD 0.0718.
>   - 이 값은 @200 EMA에서 측정됐고, best @136 가중치는 저장되지 않았다.
>   - GA는 구조적으로 0이므로 PASS는 GB·GC·GD에 근거한다(`gate_D1_C.txt:20`).
>   - 출처: DECISIONS `[2026-09-23 11:47 KST] 정정 — D2 체크포인트를 "게이트 통과/실패" 로 직접 부른 줄임말 (review_next G-1.2)`, 12:54 EXPERIMENTS:21 읽는 법 (3)(4)항
> - **(GMM 적합 파일)** 헤드라인 표(B16e4/B16e4k)가 쓴 N=1.6e5 적합 파일은 커밋본(cc3d40ab, GPU EM)이다. b*(kron K=1024, `gmm_fits_D2_K1024n160000/`)는 "영향 없음, ll_val 선택 동일"로 기록돼 있다.
>   - 출처: DECISIONS `[2026-09-23 12:55 KST] 이전 세션 CPU EM 작업이 …` 줄
>   - 이 줄의 실제 기록 시각은 12:27이다(같은 파일 `[2026-09-23 12:57 KST] 정정` 줄).

### 1.1 예산별 인용 필드

| N_train | 결과 파일 (머리말 commit) | 학습 ckpt (평가 가중치) | 게이트 (D1 형제 행) | 동일예산 |
|---|---|---|---|---|
| 1e4 | `tables_D2_B1e4.txt` (2fd1a43) | `d2sx_N10000_a1.pt` (last-EMA @673) | D1 형제 게이트 FAIL: GC 0.24333, 기준 GC ≤ 0.15 (`samplecx_D1.txt:28`) | 예. 전 arm N_train=10000 (`:29-42`) |
| 4e4 | `tables_D2_B4e4.txt` (4a92200), `tables_D2_B4e4k1.txt` (4e06d15), `tables_D2_B4e4k.txt` (e1be3b3) | `d2sx_N40000_a1.pt` (last-EMA @1051) | D1 형제 게이트 FAIL: GC 0.16651 (`samplecx_D1.txt:29`) | 예. 전 arm N_train=40000 (`:29-42`) |
| 1.6e5 | `tables_D2_B16e4.txt` (89ee7db), **`tables_D2_B16e4k.txt` (98e22f8, 헤드라인)** | `d2sx_N160000_a1.pt` (last-EMA @1784) | D1 형제 게이트 PASS 레시피 (`LADDER_C.md:1`, GC 0.0999) | 예. 전 arm N_train=160000 (`tables_D2_B16e4k.txt:29-42`) |

- N=1e4와 4e4 표는 §6d에서 "예산축 측정, arm 결과 아님"으로 재등록됐다(NUMBERS_PACKAGE §E1).
- 이 두 예산의 D2 체크포인트에는 게이트 행이 없다. D1 형제는 GC에서 FAIL이다(0.24333 / 0.16651). 출처는 NUMBERS_PACKAGE §E4의 G-1.2 정정 노트다.
- N=1e4 레시피에는 D1 재게이트 행도 따로 있다: GC 0.224111, FAIL (`hpo_final_r2.txt` trial 386). 이 행은 DECISIONS G-1.2 줄과 PAPER_MATERIALS §17.3에 인용돼 있다.

### 1.2 TABLE A: C2 BLER@16 (95% Wilson CI). 점추정이며 검정이 아니다

| N_train | GMM 격자 상한 → b* | M-ours-bstar −3 / +0 / +3 dB | **V1** −3 / +0 / +3 dB | V0 −3 dB (F3 가드 발동률) | 출처 |
|---|---|---|---|---|---|
| 1e4 | kron K=512 | 0.252 (0.236,0.270) / 0.083 / 0.024 | **0.145** (0.132,0.159) / 0.037 / 0.009 | 0.789 (0.712) | `B1e4.txt:69-71`, `guard_D2_B1e4.txt:18` |
| 4e4 | K=512 | 0.250 (0.234,0.268) / 0.072 / 0.023 | 0.145 (0.131,0.159) / 0.033 / 0.009 | 0.741 (0.702) | `B4e4.txt:69-71`, `guard_D2_B4e4.txt:18` |
| 4e4 | K=1024 | 0.250 (0.234,0.267) / 0.073 / 0.021 | 위와 같은 값 | 위와 같은 값 | `B4e4k1.txt:69-71` |
| 4e4 | **K=2048 (b\*)** | 0.248 (0.232,0.265) / 0.067 / 0.021 | 위와 같은 값 | 위와 같은 값 | `B4e4k.txt:69-71` |
| 1.6e5 | K=512 | 0.253 (0.236,0.270) / 0.075 / 0.024 | 0.145 (0.132,0.159) / 0.034 / 0.011 | 0.593 (0.529) | `B16e4.txt:292-294`, `guard_D2_B16e4.txt:44` |
| 1.6e5 | **K=1024 (b\*, 헤드라인)** | **0.243** (0.227,0.260) / 0.072 / 0.022 | **0.145** (0.132,0.159) / 0.034 / 0.011 | 0.593 (0.529) | `B16e4k.txt:69-71`, `guard_D2_B16e4k.txt:18` |

- 4자리 값은 NUMBERS_PACKAGE ADDENDUM P13에 있다. 헤드라인 −3 dB는 GMM 0.2434 → V1 0.1449이다(−40.5%, 점추정 비). V1 0.1449 = 371/2560이다(DECISIONS 12:54 EXPERIMENTS:21 (2)항).
- P2와 P2′는 **함께 인용**해야 한다(NUMBERS_PACKAGE ADDENDUM).
  - K를 512로 고정하면: GMM 0.252/0.250/0.253, 격차 0.107/0.106/0.108
  - 예산별 b*를 쓰면: GMM 0.252/0.248/0.243, 격차 0.107/0.104/0.098
- V1은 C2 전 SNR에서 F3 가드가 한 번도 발동하지 않았다. 근거는 `guard_D2_B16e4k.txt:26`의 never-fired 목록(12 arm)이며, `guard_D2_B1e4.txt:26`과 `guard_D2_B4e4.txt:26`도 같다.
- V0의 BLER에는 발산 시행이 포함돼 있다. 그래서 V0 BLER은 가드 발동률과 함께 인용한다(NUMBERS_PACKAGE §A2).
- R5-genie는 known-channel receiver reference이며 bound가 아니다(DECISIONS 11:47 명칭 정정).
  - C2 −3 dB 값: 0.034 (0.028,0.042) (`B16e4k.txt:75`)
  - C2의 arm→R5-genie 쌍은 판정점이 2개뿐이다. 그래서 모든 표에서 **UNDECIDED**다(NUMBERS_PACKAGE §D6). 각 표에서 다시 확인했으며, B16e4k·B4e4k·B4e4k1·B1e4s3 모두 C2 genie 쌍 7개가 UNDECIDED다.

### 1.3 TABLE B: `M-ours-bstar → M-ours-dscore-C-V1` 부호검정 @16 (판정점 −3/+0/+3 dB)

| N_train / GMM K | −3 dB a:b (p) | +0 dB | +3 dB | pooled | power | 판정 (원문) | SNR@0.1 격차 [90% paired bootstrap] | 출처 |
|---|---|---|---|---|---|---|---|---|
| 1e4 / 512 | 323:49 (1.3e-50) | 134:16 (2.2e-24) | 45:7 (7e-08) | 502:72 p=2.6e-80 | POWERED | `second arm fewer failures at 3/3 points, first arm fewer failures at 0/3 points -> significant` | +1.68 dB [+1.47, +1.94] | `B1e4.txt:367-372` |
| 4e4 / 512 | 323:52 (6.6e-49) | 112:13 (8.1e-21) | 40:5 (7.9e-08) | 475:70 p=5.8e-75 | POWERED | 위와 같은 문자열 (3/3) | +1.45 dB [+1.27, +1.67] | `B4e4.txt:367-372` |
| 4e4 / 1024 | 325:55 (9.8e-48) | 116:14 (3.6e-21) | 36:7 (9e-06) | 477:76 p=5.4e-72 | POWERED | 위와 같은 문자열 (3/3) | +1.48 dB [+1.29, +1.70] | `B4e4k1.txt:367-372` |
| 4e4 / 2048 | 318:53 (3.5e-47) | 104:18 (6.8e-16) | 37:8 (1.5e-05) | 459:79 p=3.9e-66 | POWERED | 위와 같은 문자열 (3/3) | +1.33 dB [+1.14, +1.53] | `B4e4k.txt:367-372` |
| 1.6e5 / 512 | 325:49 (4.4e-51) | 122:19 (1.3e-19) | 42:10 (9.1e-06) | 489:78 p=1e-73 | POWERED | 위와 같은 문자열 (3/3) | +1.51 dB [+1.30, +1.73] | `B16e4.txt:946-951` |
| **1.6e5 / 1024** | **302:50 (4.7e-45)** | **117:21 (2.4e-17)** | **35:7 (1.5e-05)** | **454:78 p=1.7e-65** | **POWERED** | `second arm fewer failures at 3/3 points, first arm fewer failures at 0/3 points -> significant` | **+1.41 dB [+1.22, +1.64]** | `B16e4k.txt:367-372` |

- a:b에서 a는 GMM만 실패한 블록 수, b는 V1만 실패한 블록 수다. censored replicates는 모든 행에서 0%다.
- V0→V1 짝지음 검정은 어느 표에도 없다(NUMBERS_PACKAGE §E3).
- V0 대비 비율(1e4 81.6% / 4e4 80.4% / 1.6e5 75.5%)은 TABLE A 점추정 비이며 검정 결과가 아니다. 1.6e5의 75.5%는 NUMBERS_PACKAGE §E3에 `tables_D2_C.txt`(비동일예산) 출처로 적혀 있다. B16e4·B16e4k의 V0 0.593 / V1 0.145도 같은 값이다.

### 1.4 필수 대조군 `M-ours-bstar → M-ours-bstar-scalar` (GMM끼리 비교, 게이트 해당 없음)

| N_train / K | −3 / +0 / +3 dB a:b | pooled | power | 판정 (원문) | SNR@0.1 격차 | 출처 |
|---|---|---|---|---|---|---|
| 1e4 / 512 | 63:85 · 45:40 · 17:24 | 125:149 p=0.16 | POWERED | `second arm fewer failures at 0/3 points, first arm fewer failures at 0/3 points -> not significant` | +0.04 [−0.12, +0.19] | `B1e4.txt:385-390` |
| 4e4 / 512 | 67:86 · 22:43 · 5:25 | 94:154 p=0.00017 | POWERED | `… first arm fewer failures at 2/3 points -> significant` | −0.22 [−0.37, −0.09] | `B4e4.txt:385-390` |
| 4e4 / 1024 | 59:86 · 37:37 · 10:19 | 106:142 p=0.026 | POWERED | `… first arm fewer failures at 1/3 points -> not significant` | −0.02 [−0.17, +0.11] | `B4e4k1.txt:385-390` |
| 4e4 / 2048 | 67:95 · 26:53 · 8:22 | 101:170 p=3.3e-05 | POWERED | `… first arm fewer failures at 3/3 points -> significant` | −0.28 [−0.45, −0.15] | `B4e4k.txt:385-390` |
| 1.6e5 / 512 | 51:100 · 33:45 · 9:17 | 93:162 p=1.8e-05 | POWERED | `… first arm fewer failures at 1/3 points -> not significant` | −0.16 [−0.30, −0.02] | `B16e4.txt:964-969` |
| 1.6e5 / 1024 | 61:95 · 30:44 · 9:10 | 100:149 p=0.0023 | POWERED | `second arm fewer failures at 0/3 points, first arm fewer failures at 1/3 points -> not significant` | −0.17 [−0.31, −0.03] | `B16e4k.txt:385-390` |

### 1.5 시드 반복 (N=1e4, C2, D1 형제 게이트 FAIL 레시피, 동일예산)

| score 시드 | 표 (commit) | V1 −3 dB | V0 −3 dB | bstar→V1 −3 / +0 / +3 | pooled | power / 판정 | SNR@0.1 격차 |
|---|---|---|---|---|---|---|---|
| a1 | `B1e4.txt` (2fd1a43) | 0.145 (0.132,0.159) | 0.789 | 323:49 · 134:16 · 45:7 | 502:72 p=2.6e-80 | POWERED / 3/3 `significant` | +1.68 [+1.47, +1.94] |
| a2 | `B1e4s2.txt` (ee510ed) | 0.150 (0.136,0.164) | 0.881 | 317:54 · 142:17 · 42:8 | 501:79 p=5.2e-76 | POWERED / 3/3 `significant` | +1.68 [+1.46, +1.94] |
| a3 | `B1e4s3.txt` (89ee7db) | 0.148 (0.134,0.162) | 0.812 | 317:49 · 136:10 · 42:5 | 495:64 p=1.5e-83 | POWERED / 3/3 `significant` | +1.71 [+1.49, +1.96] |

- 행 번호는 BLER이 `:69-71`, 검정이 `:367-372`다. 4자리 V1 값은 0.1453 / 0.1496 / 0.1477이다(ADDENDUM P5).
- 시드가 바꾸는 것은 확산 체크포인트뿐이다. 다음 행들은 세 표에서 값이 같다: M-ours-bstar(0.252), bstar-scalar, R2-ours-G, 대조군(125:149 p=0.16). 출처는 NUMBERS_PACKAGE §B3이며, a3는 표에서 다시 확인했다.
- N=4e4와 1.6e5의 시드 반복 BLER 표는 이 EXPERIMENTS 행의 결과 파일 목록에 없다.

### 1.6 GMM b* 선택 (K 격자): Nr=8 kron, validation ll (nat/표본)

- 선택 규칙(원문): `VALIDATION log-likelihood only.  BLER is never consulted (01_RULES §5).` (`gmm_fit_D2.txt:10`, `gmm_fit_D2_n4e4.txt:10`)
- n_val = n_test = 5000이다(`gmm_fit_D2.txt:9`). 구성당 restart는 3회다.

| K | N=1e4 | N=4e4 | N=1.6e5 |
|---|---|---|---|
| 256 | −23.9360 | −19.6991 | −18.4166 |
| 512 | **−23.4734 (b\*)** | −17.3438 | −14.6361 |
| 1024 | −23.5726 | −15.8823 | **−11.4592 (b\*)** |
| 2048 | 적합 없음 | **−15.1863 (b\*)** | 적합 없음 |

- 출처는 다음 파일들의 `ll_val`이다. 모두 npz로 다시 확인했다.
  - `gmm_fit_D2.txt:66`, `gmm_fit_D2_n4e4.txt:66`
  - `gmm_fits_D2_K1024/`, `gmm_fits_D2_K1024n40000/`, `gmm_fits_D2_K2048n40000/`, `gmm_fits_D2_K1024n160000/`, `gmm_fits_D2_n16e4/`의 `.npz`
  - N=1.6e5 K≤512에는 저자가 쓴 요약 파일이 없다. 이 값들은 npz에서 읽었고 NUMBERS_PACKAGE §D1의 계산값과 같다.
- N=1e4의 K1024 − K512 차이는 −0.0992 nat이다. 검증 집합 1개에서 나온 값이고 오차막대가 없다. 같은 K 안의 restart 범위는 0.4325(K1024), 0.5925(K512)다(NUMBERS_PACKAGE §D1).
- restart별 ll_val (`.k0r*.npz`):
  - N=1.6e5 K1024: −11.776 / −11.459 / −11.674
  - N=4e4 K2048: −15.223 / −15.379 / −15.186
- N=4e4의 b*(K=2048)와 N=1.6e5의 b*(K=1024)는 모두 실행된 격자의 최댓값이다. N=1.6e5 K=2048은 적합되지 않았다(ADDENDUM P14 캐비엇).
- Nr=4는 어느 예산에서도 K=1024로 확장되지 않았다(NUMBERS_PACKAGE §D1).
- `05_SPEC_testbed_D2.md:66`에 등록된 격자는 K ∈ {16,32,64,128}이고, 실제 실행 격자는 이와 다르다. NUMBERS_PACKAGE §E2는 이 줄을 `:56`으로 적었다.

### 1.7 셀 C5 (Tp=3), C1 (Tp=2): 표가 있는 예산만

- 표가 있는 두 예산(1e4, 1.6e5)은 모두 동일예산이며 n=2560이다.
- N=1.6e5 셀 표의 GMM은 **K=512**이다. K=1024로는 다시 실행되지 않았다. `B16e4k`는 C2만 담고 있다.
- D1 형제 게이트는 1e4가 FAIL 레시피, 1.6e5가 PASS 레시피다.
- N=4e4 셀 표는 없다(`tables_D2_B4e4x.txt` 파일 없음).

| 셀 / N | BLER −3 dB: GMM → V1 | 판정점 | bstar→V1 a:b (p) | pooled | power | 판정 (원문) | 출처 |
|---|---|---|---|---|---|---|---|
| C5 / 1e4 | 0.544 → 0.394 | +9/+12/+15 | 282:170 (1.5e-07) · 268:221 (0.037) · 243:276 (0.16) | 793:667 p=0.0011 | POWERED | `second arm fewer failures at 2/3 points, first arm fewer failures at 0/3 points -> significant` | `B1e4x.txt:290-292, :728-733` (db945a9) |
| C5 / 1.6e5 | 0.517 → 0.400 | +6/+12/+15 | 232:156 (0.00013) · 206:213 (0.77) · 185:271 (6.6e-05) | 623:640 p=0.65 | POWERED | `second arm fewer failures at 1/3 points, first arm fewer failures at 1/3 points -> not significant` | `B16e4.txt:508-510, :1086-1091` |
| C1 / 1e4 | 0.778 → 1.000 | +6/+12/+15 | 462:473 (0.74) · 453:530 (0.015) · 457:629 (2e-07) | 1372:1632 p=2.3e-06 | POWERED | `second arm fewer failures at 0/3 points, first arm fewer failures at 2/3 points -> significant` | `B1e4x.txt:74-76, :588-593` |
| C1 / 1.6e5 | 0.760 → 0.982 | +6/+12/+15 | 353:518 (2.5e-08) · 386:546 (1.8e-07) · 370:627 (3.6e-16) | 1109:1691 p=3.1e-28 | POWERED | `second arm fewer failures at 0/3 points, first arm fewer failures at 3/3 points -> significant` | `B16e4.txt:76-78, :806-811` |

C5 전 SNR의 BLER@16 (GMM / V1). SNR은 −3, +0, +3, +6, +9, +12, +15 dB 순이다.

| N | GMM | V1 | 출처 |
|---|---|---|---|
| 1.6e5 (K=512) | 0.517 / 0.256 / 0.164 / 0.132 / 0.134 / 0.125 / 0.121 | 0.400 / 0.185 / 0.121 / 0.103 / 0.119 / 0.128 / 0.155 | `B16e4.txt:508,510` |
| 1e4 | 0.544 / 0.276 / 0.187 / 0.172 / 0.162 / 0.155 / 0.146 | 0.394 / 0.176 / 0.126 / 0.120 / 0.118 / 0.136 / 0.159 | `B1e4x.txt:290,292` |

- −3 dB는 C5·C1 쌍의 판정점이 아니다. 따라서 −3 dB의 BLER 비는 검정되지 않은 점추정이다(NUMBERS_PACKAGE §E6).
- 판정 SNR은 셀마다 다르다. 사전 등록된 교차 Tp 포락선(TABLE C)은 계산되지 않았다(NUMBERS_PACKAGE §E4).
- V1 F3 가드 발동률:
  - C1 −3 dB: 2560/2560 (1.6e5, `guard_D2_B16e4.txt:19`)
  - C1 +15 dB: 0.191 (1.6e5, `:42`) / 0.204 (1e4, `guard_D2_B1e4x.txt:47`)
  - C5, 1.6e5: +3~+15 dB에서 0.005~0.033 (`guard_D2_B16e4.txt:56-71`). −3/+0 dB에서는 발동 기록이 없다.
- C1 −3 dB에서 V1의 비유한 블록은 314/2560(1.6e5), 804/2560(1e4)이며, 블록 오류로 계수됐다(`B16e4.txt:57`, `B1e4x.txt:55`).
- STATUS의 동작 범위 문장("Tp=4 전 SNR / Tp=3 ≤ +6 dB / Tp=2 열세", ADDENDUM P4)의 power 열은 "—"로 적혀 있다. 이 절에는 위 수치만 옮긴다.

### 1.8 저SNR 연장 §6p (N=1e4, D1 형제 게이트 FAIL 레시피, 동일예산)

출처 파일은 `tables_D2_B1e4lo.txt` (6a4822e), `guard_D2_B1e4lo.txt`, `lowsnr_6p_score.txt`다.

| 셀 | SNR | GMM | V1 | V1 가드 (`lowsnr_6p_score.txt`) | bstar→V1 (앵커 규칙) |
|---|---|---|---|---|---|
| C2 | −9 / −7 / −6 / −5 | 0.996 / 0.906 / 0.791 / 0.580 | 0.981 / 0.796 / 0.601 / 0.395 | 0.000 / 0.000 / 0.000 / 0.000 | 판정점 −6/−5만: 544:56 · 567:94, pooled 1111:150 p=1.3e-181 → **UNDECIDED** (`2 decision points (needs 3)`, `:504-509`) |
| C5 | −9 / −7 / −6 / −5 | 0.998 / 0.964 / 0.904 / 0.793 | 1.000 / 0.998 / 0.993 / 0.655 | 0.865 / 0.836 / 0.779 / 0.000 | 판정점 −5 1개: 477:122 p=1.6e-50 → **UNDECIDED** (`:644-649`) |

- 가드 값은 두 파일의 정의가 다르다.
  - `lowsnr_6p_score.txt`: NMSE@16 > 10 또는 비유한 (`score_6p.py:44-46`)
  - `guard_D2_B1e4lo.txt`: 16회 반복 중 어느 회든 발동
  - 후자 기준 V1 값: C5 −9/−7/−6 = 2560/2560, 2559/2560, 2550/2560 (`:27,32,37`). C2 −9 = 1/2560 (`:19`). 나머지 점은 발동 기록이 없다.
- §6p 규칙(4 SNR 전부, raw에서 직접 계산)에 따른 SNR별 검정:
  - C2: −9 41:3 (1.6e-09), −7 312:30 (2.6e-60)
  - C5: −9 0:5, −7 4:92 (8.8e-23), −6 9:238 (7.5e-59), −5 477:122 (1.6e-50)
  - 출처는 STATUS §6p 표(`STATUS.md:1416-1417`, `:1436-1439`)와 NUMBERS_PACKAGE ADDENDUM P6이다. 이 값들은 `tables_D2_B1e4lo.txt`와 `lowsnr_6p_score.txt`에는 없다.
- §6p 예측 채점(원문): 1 빗나감, 2 빗나감, 3 맞음, 4 반만 맞음 (`STATUS.md:1446-1450`, 예측 커밋 279512b).

### 1.9 N′ = 3.2e5 동일예산 재실행 (B32e4; NEXT_EXPERIMENTS_B32e4 v2 사전 등록)

**EXPERIMENTS.md 행**: `2026-09-24 09:38 ~ 09-25 05:33 KST` (GPU 적합·학습, `run_b32e4.sh`), `2026-09-25 06:01 ~ 08:26 KST` (BLER, `run_b32e4_eval.sh`, 커밋 36b12bf6). 결과 파일 머리말 `git commit` = 36b12bf6. 판정·예측 채점 원문은 `conf/results/review_next/NEXT_EXPERIMENTS_B32e4.md` §6.

- **인용 필드**: 전 arm N_train=320000 (동일예산). b\* = kron K=4096, ll_val −5.942083265612076, **격자 끝**(K=2048 대비 +1.851 nat; 사용자 결정으로 K=8192 미적합). 평가 가중치: 판정 태그 B32e4 = `d2sx_N320000_a1_best.pt` (sha256[:16] 035744cbe955984d, epoch 966 = best), 보고 태그 B32e4last = `d2sx_N320000_a1.pt` (last-EMA @986, f2f1eebc9894c773). D1 형제 게이트 (`sx_N320000_D1.pt` last): GA 9.52e-16, GB 0.00325, GC 0.0937, GD 0.0715 → PASS (`samplecx.csv` 행 320000); best 파일 GC 0.0907 PASS (보고 전용, `B32e4_D1best_gate.txt`). 수용 검사 `ACCEPT: OK -- B32e4, B32e4x, B32e4last` (`B32e4_accept.txt`).
- **판정 (사전 등록 §2)**: `M-ours-bstar → M-ours-dscore-C-V1`, 태그 B32e4 → `power guard … -> POWERED`, `second arm fewer failures at 3/3 points, first arm fewer failures at 0/3 points -> significant` → 등록 문구 "동일예산 우위가 N′ = 3.2e5 에서도 유지". 헤드라인은 1.6e5 (§1.1~§1.3) 그대로.

**TABLE A (C2 BLER@16, 95% Wilson CI)**

| 태그 | M-ours-bstar −3 / +0 / +3 dB | V1 −3 / +0 / +3 dB | V0 −3 dB (F3 가드 발동률) | R5-genie −3 dB | 출처 |
|---|---|---|---|---|---|
| B32e4 (`_best`) | 0.238 (0.222,0.255) / 0.068 / 0.021 | 0.146 (0.133,0.160) / 0.032 / 0.012 | 0.595 (0.542) | 0.034 (0.028,0.042) | `tables_D2_B32e4.txt:70-76`, `guard_D2_B32e4.txt:18` |
| B32e4last (last-EMA) | 같은 값 (b\* 실패 벡터 동일) | 0.144 (0.131,0.158) / 0.034 / 0.014 | 0.750 (0.715) | 같은 값 | `tables_D2_B32e4last.txt:70-76`, `guard_D2_B32e4last.txt:18` |

**TABLE B (`M-ours-bstar → M-ours-dscore-C-V1` @16, 판정점 −3/+0/+3 dB)**

| 태그 | −3 dB | +0 dB | +3 dB | pooled | power | 판정 (원문) | SNR@0.1 격차 [90%] | 출처 |
|---|---|---|---|---|---|---|---|---|
| **B32e4** | 285:48 (3.8e-42) | 109:17 (1.3e-17) | 27:4 (3.4e-05) | 421:69 p=1.2e-62 | POWERED | `second arm fewer failures at 3/3 points, first arm fewer failures at 0/3 points -> significant` | +1.33 dB [+1.14, +1.53] | `tables_D2_B32e4.txt:368-373` |
| B32e4last | 290:48 (2.5e-43) | 101:14 (2e-17) | 27:9 (0.0039) | 418:71 p=7.4e-61 | POWERED | 같은 문자열 | +1.32 dB [+1.13, +1.52] | `tables_D2_B32e4last.txt:368-373` |

- 필수 대조군 `M-ours-bstar → M-ours-bstar-scalar` (B32e4): 72:90 (0.18) · 23:38 (0.072) · 12:13 (1), pooled 107:141 p=0.036, POWERED, `second arm fewer failures at 0/3 points, first arm fewer failures at 0/3 points -> not significant` (`tables_D2_B32e4.txt:386-391`).
- 실패 수 (n=2560, B32e4): b\* 610 / 173 / 53, V1 373 / 81 / 30, R5-genie 87 / 26 / 12. 격차 회수율 (b\*−V1)/(b\*−genie) = 0.453 / 0.626 / 0.561 (3점 합 0.495). 같은 셈을 헤드라인 B16e4k 에 적용: 623/184/57, 371/88/29, 87/26/12 → 0.470 / 0.608 / 0.622 (합 0.509). B32e4last: 0.463 / 0.592 / 0.439. (회수율은 사전 등록 판정 지표가 아닌 계산 수치; raw 에서 직접 셈.)
- best 대 last V1 짝 부호검정 (C2, a = best 실패·last 성공): −3 dB 21:16 (0.51), +0 8:13 (0.38), +3 2:7 (0.18); 3점 합 31:36 p=0.63.

**예산 곡선 (C2 −3 dB, last-EMA 규약; 사전 등록상 보고 전용, 추세 검정 없음)**

| N_train | b\* | GMM b\* | V1 | b\*→V1 pooled | SNR@0.1 격차 [90%] | D1 형제 게이트 |
|---|---|---|---|---|---|---|
| 1e4 | kron 512 | 0.252 | 0.145 | 502:72 | +1.68 [+1.47, +1.94] | FAIL |
| 4e4 | kron 2048 (끝) | 0.248 | 0.145 | 459:79 | +1.33 [+1.14, +1.53] | FAIL |
| 1.6e5 | kron 1024 (K=2048 미적합) | 0.243 | 0.145 | 454:78 | +1.41 [+1.22, +1.64] | PASS 레시피 |
| 3.2e5 | kron 4096 (끝) | 0.238 | 0.144 | 418:71 | +1.32 [+1.13, +1.52] | PASS |
| 3.2e5 `_best` (별도 열) | 같음 | 0.238 | 0.146 | 421:69 | +1.33 [+1.14, +1.53] | PASS |

(출처: `tables_D2_B1e4.txt:369-372`, `B4e4k.txt:369-372`, `B16e4k.txt:369-372`, `B32e4last.txt:370-373`, `B32e4.txt:370-373`.)

**셀 C5 (Tp=3), C1 (Tp=2), B32e4x (`_best`, 보고 전용; 앵커 규칙 자동)**

| 셀 | 판정점 | bstar→V1 a:b (p) | pooled | power | 판정 (원문) | 출처 |
|---|---|---|---|---|---|---|
| C5 | +6/+12/+15 | 230:157 (0.00024) · 228:225 (0.93) · 204:258 (0.014) | 662:640 p=0.56 | POWERED | `second arm fewer failures at 1/3 points, first arm fewer failures at 1/3 points -> not significant` | `tables_D2_B32e4x.txt:731-736` |
| C1 | +6/+9/+15 | 402:505 (0.0007) · 394:583 (1.6e-09) · 372:673 (9.2e-21) | 1168:1761 p=5e-28 | POWERED | `second arm fewer failures at 0/3 points, first arm fewer failures at 3/3 points -> significant` | `tables_D2_B32e4x.txt:591-596` |

- C5 BLER@16 (−3…+15 dB): GMM 0.497 / 0.255 / 0.155 / 0.141 / 0.141 / 0.138 / 0.123, V1 0.394 / 0.186 / 0.116 / 0.112 / 0.120 / 0.137 / 0.144. C1: GMM 0.749 / 0.512 / 0.399 / 0.362 / 0.355 / 0.364 / 0.355, V1 0.995 / 0.541 / 0.434 / 0.403 / 0.429 / 0.429 / 0.473. V0 F3 가드 −3 dB: C5 0.677, C1 1.000 (`guard_D2_B32e4x.txt:49,19`). V1 F3 가드: C1 −3 dB 2560/2560 (1.000), +0…+15 dB 0.066 / 0.018 / 0.079 / 0.137 / 0.175 / 0.193 (`guard_D2_B32e4x.txt:20,25,30,34,38,42,47`); C5 +0…+15 dB 0.002 / 0.005 / 0.011 / 0.023 / 0.033 / 0.032 (`:52-73`); C1 −3 dB V1 비유한 blk_err@16 80/2560 (`tables_D2_B32e4x.txt:56`). V4b: C5·C1 전 SNR 1.000. C2 (B32e4·B32e4last): V1·V4·V4b·b\* 발동 없음 (`guard_D2_B32e4.txt:26`).
- 동일예산 GB′ (b\* = kron 4096 기준, 보고 전용): 확산/GMM 디노이징 NMSE 비 0.453~0.879 (median 0.513), worst excess −0.121 (`results/d2_gbprime.csv` 행 320000).
- GMM 격자 전체 (kron 16~4096, full 16~512, 재시작별 ll_val·재시드·구현 경로): NEXT_EXPERIMENTS_B32e4 §5.

---

## 2. review_next 진단·ablation: P0-2 실경로 비용, P1 (cavity·calibration·phase·pseudo), A2 (clip=mean), H0 (best vs last)

**이 절 공통 인용 필드** (따로 적지 않으면 모든 표에 적용)

| 필드 | 값 | 출처 |
|---|---|---|
| testbed·prior | D2 / S2, 헤드라인 셀 C2 (8×4, T=16, Tp=4) | `conf/results/review_next/NEXT_EXPERIMENTS.md` §0 |
| 시행 집합 | 개발 집합: `common.trial_rng` skip 2560..3199, 점당 n=640. 테스트 집합 skip 0..2559 는 쓰지 않았다 | 같은 곳 §0 |
| 판정점 | C2 −3 dB 하나. C2 +6 dB·C5 −3 dB·C1 −3 dB 는 **보고 전용** | 같은 곳 §0 |
| 검정 (house test) | 같은 시행에서 짝지은 실패 지표(`blk_err[:, -1]`)의 불일치 쌍에 exact 양측 부호검정을 한다. p < 0.05 가 기준이다. n_d < 6 이면 UNDECIDED 다. MDD 는 보고용이다. p ≥ 0.05 는 "이 설계로 판정하지 못함"으로 읽고 "차이 없음"으로 읽지 않는다 | 같은 곳 §0 |
| power guard | 이 절의 부호검정은 모두 n_d ≥ 6 이라 UNDECIDED 조건(n_d < 6)에 해당하지 않는다. 결과 파일은 POWERED 라벨을 출력하지 않는다. 08_SPEC §2 의 3점 power guard 는 NEXT_EXPERIMENTS 에서 §3.1 4단계(테스트 확증)에만 규정돼 있다 | 각 결과 파일의 `house test` 줄, NEXT_EXPERIMENTS §3.1 |
| 헤드라인 체크포인트 | `d2sx_N160000_a1.pt` = **last-EMA@1784이고, best@1764 는 저장되지 않았다 (BEST_WEIGHTS_UNAVAILABLE)**. sha256[:16] 4443921ce8d5c4a1 | DECISIONS `[2026-09-23 11:47 KST] 정정 — Stage C 학습 arm 은 best 가 아니라 마지막 epoch EMA 로 평가됐다 (review_next P0-1b)` |
| 게이트 | D2 체크포인트에는 게이트 행이 없다. **"D1 형제 게이트 PASS 레시피"**로 읽는다(LADDER_C.md:1 `sx_N160000_D1.pt`). 그 D1 게이트도 last-EMA@200 에서 측정됐다 | DECISIONS `[2026-09-23 11:47 KST] 정정 — D2 체크포인트를 "게이트 통과/실패" 로 직접 부른 줄임말 (review_next G-1.2)`, `[2026-09-23 11:47 KST] 정정 — D1 게이트 판정은 best 가 아니라 마지막 epoch EMA 에 대해 측정됐다 (review_next ckpt/M2)` |
| 예산 | GMM b\* 는 kron K=1024 적합(`gmm_fits_D2_B16e4k`, N_train 160000)이다. score 체크포인트도 N_train 160000 이다. 학습 집합과 N_train 이 같다 | NEXT_EXPERIMENTS §0 "학습 데이터 예산", 각 결과 파일 헤더 |
| R5-genie 명칭 | "known-channel receiver reference (동일 EP detector + BCJR, 참 H)". 상한(bound)으로 부르지 않는다 | DECISIONS `[2026-09-23 11:47 KST] 정정 — R5-genie·R6-exactEP 를 "상한/upper bound/lower bound/headroom" 으로 부른 명칭 (review_next R-10.3 표 헤더, M-10.3a)` |

### 2.0 사전 등록 가설·진행 조건 판정 (기록된 라벨 그대로)

| id | 기록된 판정 | 판정값 | 규칙 (NEXT_EXPERIMENTS §1·§2.6) | EXPERIMENTS 행 |
|---|---|---|---|---|
| C-phase (= H3(a)의 여집합) | **만족** → A1 진행 | 구간별 비: 하 0.2460 / 중 0.1482 / 상 0.0830 | ≥ 0.10 인 구간이 하나 이상이면 만족 | `2026-09-23 08:05 (텍사스 09-22 18:05 CDT)` |
| H2 | **기각 안 됨** | 20점 중 두 대역을 모두 충족한 점 1개 (하 1·중 0·상 0) | 14/20 이상 충족하면 기각 | 같음 |
| C-calib | **만족** → A2 에 floor 1e-2 보고 전용 행 추가 | 대역을 벗어난 점 19/20 | 7/20 이상 벗어나면 만족 | 같음 |
| H1 | **H1 기각** | e_8 = 1.025, a_8 = 0.7532 | e_8 ∈ [0.7, 1.4] 이고 a_8 ≤ 3 이면 기각 | **출처 없음**. P1 cavity 실행에는 EXPERIMENTS 행이 없다. 기록 위치는 NEXT_EXPERIMENTS §6 "§2.1 P1-1 cavity" 줄과 커밋 d9085247 이다 |
| C-cavity | **불만족** → P2-B 보류 | (H1 기각) | H1 이 기각되지 않으면 만족 | 같음 (출처 없음) |
| H4 | **H4 기각** | 반복 4 r_P 중앙값 0.4816, 우도비 p = 0.69 | 중앙값 < 0.2 이거나 LR p ≥ 0.05 이면 기각 | 같음 (출처 없음) |
| C-pseudo | **불만족** → P2-A 보류 | (H4 기각) | H4 가 기각되지 않으면 만족 | 같음 (출처 없음) |
| H5 | **H5 기각** | V1-mean vs V1-eta 4:4, p=1 | p ≥ 0.05 이거나 V1-mean 의 실패가 더 많으면 기각 | `2026-09-23 09:30 ~ 09:52 (텍사스 09-22 19:30 ~ 19:52 CDT)` |
| A2 귀속 | **귀속 조건 불충족** ("adapter 일반 효과 또는 판정 불가") | 상호작용 9:19, p=0.0872 | p < 0.05 이고 V1 쪽 개선이 더 크면 "prior 에 특이적인 adapter 효과" | 같음 |
| H0 | **기각 안 됨** | best vs last 85 vs 85, 6:6, p=1 | p < 0.05 이면 기각 | `2026-09-23 07:14 ~ 13:39 (텍사스 09-22 17:14 ~ 23:39 CDT)` |

아래 표는 §7 사전 예측과 관측값을 나란히 적은 것이다. 예측 문구는 NEXT_EXPERIMENTS §7 원문을 따른다. "빗나감"은 기록에 적힌 경우에만 옮겼다.

| 항목 | 예측 | 관측 |
|---|---|---|
| C-phase | 만족 (예비값 0.29/0.16 @하·중; 상 0.07) | 0.246 / 0.148 / 0.083, 만족 |
| C-cavity | e_8 ∈ [0.7, 1.4] 이지만 a_8 > 3 → 만족 | e_8 1.025, a_8 0.753 → 불만족 |
| C-pseudo | 반복 4 r_P 중앙값 ≈ 0.4, NMSE·ν_q 통제 후 추가 설명력 없음 → 불만족 | 0.482, p 0.69 → 불만족 |
| C-calib | 하 구간에서 ρ_tr < 0.8 이 7점 이상 → 만족 | 만족. ρ_sub 는 대역 안에 있고 cov90 이 대역 밖에 있다. EXPERIMENTS 08:05 행은 이를 "사전 예측 중 … **빗나감**(ρ 는 대역 안, 만족은 coverage 때문)"으로 기록했다 |
| H0 | 기각 안 됨 (p ≥ 0.05) | p = 1, 기각 안 됨 |

### 2.1 P0-2: Module H 실경로 비용 (추론만)

EXPERIMENTS 행은 `2026-09-23 11:16 ~ 11:25 (텍사스 09-22 21:16 ~ 21:25 CDT)`이다.
- 결과 파일: `conf/results/review_next/complexity_moduleH_ep.{txt,npz}`
- 커밋: 실행 d217283d, 결과 3ceae3ab
- 설정: CPU float64, 1 스레드, SNR 당 24 시행(워밍업 1 제외), 16 반복, arm 순서 교대
- 검정: 해당 없음 (비용 측정)

| SNR | arm | Module H 호출당 중앙값 [IQR] | 블록 중앙값 | 블록 중 Module H 비중 | 호출당 비 (학습/GMM b\*) | 블록 비 |
|---|---|---|---|---|---|---|
| −3 dB | M-ours-bstar (kron K=1024, `ep_site`) | 44.528 ms [44.18, 44.87] | 754 ms | 94.5% | — | — |
| −3 dB | M-ours-dscore-C-V1 | 60.304 ms [60.03, 60.61] | 1006 ms | 95.9% | **1.35×** | **1.33×** |
| −3 dB | M-ours-dscore-C-V0 | 60.186 ms [59.91, 60.44] | 1005 ms | 95.9% | 1.35× | 1.33× |
| +6 dB | M-ours-bstar | 45.858 ms [45.21, 46.36] | 773 ms | 94.6% | — | — |
| +6 dB | M-ours-dscore-C-V1 | 63.849 ms [62.69, 64.95] | 1068 ms | 96.0% | **1.39×** | **1.38×** |
| +6 dB | M-ours-dscore-C-V0 | 63.621 ms [62.55, 65.01] | 1062 ms | 96.1% | 1.39× | 1.37× |

- **정정 적용.** 기존 A8 "학습 prior 4.6×"(`complexity_moduleH.txt`)는 arm 간 수신기 비용비가 아니다. A8 은 등방 `denoise_full` 마이크로벤치마크이고, K=512 와 N=1e4 체크포인트로 쟀다. arm 간 비용 진술은 위 표로 대체한다. A8 파일은 기록으로 남는다.
  - 근거: DECISIONS `[2026-09-23 11:47 KST] 정정 — §6q A8 "학습 prior 4.6배" 는 arm 간 수신기 비용비가 아니다 (review_next P0-2b·cost/M1·cost/M2)`, `[2026-09-23 12:54 KST] 정정 — §6q A8 4.6× 정정(11:47 P0-2b 줄) 보충: 대체 문장의 실경로 수치와 나머지 위치 (review_next P0-2b·cost/M2)`.
  - 보충 줄은 npz 에서 중앙값 비를 다시 계산해 호출 1.354·1.392, 블록 1.334·1.381 을 확인했다.
- 부하 평균은 시작 26.5, 끝 5.2 였다. 측정 중에 학습 2개가 동시에 돌았다. 학습·EM 적합 비용은 포함하지 않는다.

### 2.2 P1 held-out AWGN 진단: phase (P1-3), calibration (P1-2), pseudo (P1-4, 보고 전용)

EXPERIMENTS 행은 `2026-09-23 08:05 (텍사스 09-22 18:05 CDT)`이다.
- 결과 파일: `conf/results/review_next/p1_heldout.{npz,txt}`
- 커밋: 실행 1022fff0, 결과 d2bab1d6
- 질의 표본: h 는 `train_rng(D2,S2,8,10)`, 잡음은 SEED_GATE
- n: n_calib 2048, n_phase 512
- 격자: 동결 D2 격자 20점. 하 k0–6 / 중 k7–14 / 상 k15–19
- 체크포인트: 헤드라인 last-EMA
- 게이트: 진단 P1-x 이며 게이트가 아니다
- 검정: 부호검정이 아니다

| 양 (구간별: 격자점 값의 중앙값) | 하 | 중 | 상 |
|---|---|---|---|
| 위상 비 ε_φ/δ (1차 해석, k′=1..7) | 0.2460 | 0.1482 | 0.0830 |
| 위상 비 (k′=0..7 문자 그대로) / 중앙값끼리의 비 | 0.2343 / 0.2450 | 0.1412 / 0.1478 | 0.0793 / 0.0821 |
| GMM b\* 위상 비 | 0.0000 | 0.0000 | 0.0000 |
| V1 ρ_sub (floor 제외 부분공간) | 0.9791 | 0.9878 | 1.0046 |
| V1 cov90 (명목 0.90) | 0.7803 | 0.7988 | 0.7114 |
| GMM b\* ρ_full / cov90 | 1.0114 / 0.8813 | 1.0170 / 0.7915 | 0.9668 / 0.8013 |
| r_P 중앙값 V1 / V0 / GMM b\* (보고 전용) | 0.4094 / 0.4091 / 0.0092 | 0.4785 / 0.4784 / 0.1790 | 0.4809 / 0.4809 / 0.3191 |

- 격자점별 범위(파일 §2.2 표):
  - V1 ρ_sub 0.975–1.008, cov90 0.680–0.860
  - GMM b\* cov90 0.753–0.898
  - 두 대역을 모두 충족한 점은 k=0 (σ 0.0331) 하나다
- 해석 의존성은 파일에 이미 판정돼 있다. C-phase 와 H2/C-calib 는 대안 해석(k′=0..7, 중앙값끼리의 비, 전체 공간 ρ_tr)에서도 판정이 같다. 파일은 둘 다 `reading-robust` 로 표시했다. 해석 규정은 NEXT_EXPERIMENTS §6.1 항목 1–5 를 따른다.
- 파일 내 검사:
  - toy check 는 PASS 다(ν·J 대 Cov 4.83e-16, r_P 2.76e-15, tol 1e-12).
  - GMM GPU 대 CPU 차이는 2.91e-12 다.
  - 실행 시간(wall)은 251 s 다.

### 2.3 P1 cavity 실제 질의 (P1-1, P1-2·P1-4 의 실제 질의 부분): H1, H4

EXPERIMENTS 행은 **출처 없음**이다. 이 실행에는 행이 없다. 기록 위치는 NEXT_EXPERIMENTS §6 "§2.1 P1-1 cavity" 줄(완료 18:25 CDT = 09-23 08:25 KST)과 판정 커밋 d9085247 이다.
- 결과 파일: `conf/results/review_next/p1_cavity_D2_{C2_…_Tp4_dft_snr-3, C2_…_snr6, C5_…_Tp3_dft_snr-3, C1_…_Tp2_dft_snr-3}.{npz,txt}`
- 실행: git b7fca4b1, CPU 1 스레드, 점당 wall 5789 s (C2 −3 dB)
- 체크포인트: 헤드라인 last-EMA
- 게이트: 진단 P1-x 이며 게이트가 아니다
- 예산: 헤드라인과 같다 (kron K=1024, N_train 160000)
- 시행: 2560..3199, 점당 n=640

| 점 | e_8 (V1 블록 중앙값) | a_8 | r_P 반복 4 중앙값 | 실패@16: V1 / V0 / bstar-scalar / bstar | V0 guardH 발산 | 지위 |
|---|---|---|---|---|---|---|
| C2 −3 dB | **1.025** | **0.7532** | **0.4816** | 88 / 375 / 135 / 132 | 358 | 판정 |
| C2 +6 dB | 1.013 | 0.7223 | 0.4648 | 3 / 603 / 10 / 9 | 592 | 보고 전용 |
| C5 −3 dB | 1.159 | 0.9272 | 0.4795 | 257 / 488 / 346 / 314 | 386 | 보고 전용 |
| C1 −3 dB | 6.639e+04 | 0.9275 | 0.007969 | 623 / 640 / 511 / 483 | 640 (V0 raised 265, V1 은 guardH 640·raised 64) | 보고 전용 |

- **H4 우도비 p.**
  - 기록값은 0.69 (로그 변환 0.54)다. 출처는 NEXT_EXPERIMENTS §6 과 커밋 d9085247 메시지다. 결과 txt 에는 "LR test not computed here"라고 적혀 있다.
  - 검증을 위해 npz 로 다시 계산했다(기록이 아니라 검증 재계산이다). 사용한 키는 `M-ours-dscore-C-V1|fail`, 반복 4 의 `nmse_post`·`nu_q`·`r_P` 다.
    - 공변량이 모두 선형이면 p = 0.691 이다.
    - NMSE·ν_q 만 로그 변환하고 r_P 는 선형이면 p = 0.537 이다.
    - 세 공변량을 모두 로그 변환하면 p = 0.513 이다.
  - 기록값 0.54 가 어떤 변환 정의에서 나왔는지는 기록에 없다(**출처 없음**).
- H1 의 보고 전용 항목(반복 4 NMSE 를 통제한 e_4 의 추가 설명력)은 결과 파일에 없다. **출처 없음**.
- C2 −3 dB 실제 질의 calibration (보고 전용, 반복 8, Σ = νJ, coverage 는 PSD 부분집합에서 계산):

| source | ρ_tr | cov90 | PSD 비율 |
|---|---|---|---|
| V1 own (J_psd) | 1.24 | 0.708 | 1.000 |
| V0 own (Herm J) | 1.5 | 0.696 | 0.844 |
| GMM b\* 반사실 @ V1 (q, ν) | 1.08 | 0.736 | 1.000 |

### 2.4 A2: clip='mean' 대칭 ablation (H5; 개발 집합 전용·보고 전용)

EXPERIMENTS 행은 `2026-09-23 09:30 ~ 09:52 (텍사스 09-22 19:30 ~ 19:52 CDT)`이다.
- 결과 파일: `conf/results/review_next/A2_interaction_C2_m3.txt`, `run_manifest_review_next_A2.json`, raw `conf/raw_review_next_A2`
- 커밋: 실행 d9085247, 결과 73e53af4
- 체크포인트: 헤드라인 last-EMA
- 예산: GMM b\* kron K=1024 와 N_train 이 같다
- 지위: H5 는 테스트 raw 의 clip 통계에서 나온 가설이다. 그래서 개발 집합 전용·보고 전용이다 (NEXT_EXPERIMENTS §1)

| C2 −3 dB (n=640) | 실패 (X / Y) | a:b | n_d | p | MDD@n_d | 기록 |
|---|---|---|---|---|---|---|
| **H5**: V1-mean vs V1-eta | 88 / 88 | 4:4 | 8 | 1 | 8 | **H5 기각** |
| gmmB-scorew-mean vs gmmB-scorew-eta | 134 / 124 | 15:5 | 20 | 0.0414 | 10 | p < 0.05, gmmB-eta 의 실패가 더 적음 |
| 상호작용 d = (V1mean−V1eta) − (gmmBmean−gmmBeta) | — | 9:19 | 28 | 0.0872 | 12 | **귀속 조건 불충족** |

아래 표는 보고 전용 실패 수다. 행에 적힌 값과, raw `blk_err[:, -1]` 을 다시 집계한 값을 함께 실었다.

| 점 | V1-eta | V1-mean | V1-floor1e-2 | gmmB-eta | gmmB-mean | bstar | bstar-mean | R5-genie |
|---|---|---|---|---|---|---|---|---|
| C2 −3 dB | 88 | 88 | 88 | 124 | 134 | 132 | 135 | 28 |
| C2 +6 dB | 3 | 3 | 3 | 7 | 8 | 9 | 7 | 2 |
| C5 −3 dB | 257 | 252 (15:20, p=0.5) | 257 | 344 | 346 (21:19, p=0.88) | 314 | 319 | 25 |

- V1-floor1e-2 는 C-calib 만족에 따라 추가한 보고 전용 행이다. NMSE 는 V1 과 다르다(중앙값 상대차 1e-5).
- NMSE@16 중앙값은 V1-mean 0.0495, V1-eta 0.0525 다(행 메모).
- bstar-mean(`GMMPriorB.view('mean')`)은 의미가 다른 보고 전용 행이다 (§3.2, 감사 M3).

### 2.5 H0: best vs last (통제 재학습 `ctrl_N160000_a1`)

EXPERIMENTS 행은 `2026-09-23 07:14 ~ 13:39 (텍사스 09-22 17:14 ~ 23:39 CDT)`이다.
- 결과 파일: `conf/results/review_next/H0_best_vs_last_C2_m3.txt`, `H0_ref_ctrllast_vs_legacy_C2_m3.txt`, manifest 2개
- 커밋: 행 기재 115d391f (평가 시 코드 fe278087 이후). 결과 파일 헤더 6bbd487d, 결과 커밋 b7943e1c
- 학습:
  - GPU 1, 22,979 s, 1267 epoch, best @1247
  - 헤드라인 레시피·rung 라벨·seed·split 이 같다
  - 초기값은 고정하지 않았다(N1, init sha256[:16] 4252cef8d58e34f1)
- 게이트: 게이트 행이 없다. D1 형제 게이트 PASS 레시피로 읽는다 (G-1.2 정정)
- 예산: N_train 160000 으로 같다

| 비교 (C2 −3 dB, n=640, V1 wiring) | 체크포인트 | 실패 X / Y | a:b | n_d | p | MDD@n_d | 기록 |
|---|---|---|---|---|---|---|---|
| **H0 판정**: 재학습 best vs 재학습 last (같은 run) | e2b22673ac91ed8f (@1247, role=best) / 9eeb5c783e32fe9e (@1267, role=last) | 85 / 85 | 6:6 | 12 | 1 | 8 | **기각 안 됨** |
| 참조 (판정 아님): 재학습 last vs 기존 last-EMA | 9eeb5c783e32fe9e / 4443921ce8d5c4a1 (@1784, BEST_WEIGHTS_UNAVAILABLE) | 85 / 88 | 8:11 | 19 | 0.648 | 11 | p ≥ 0.05 (이 설계로 판정하지 못함) |

같은 시행에서 GMM b\* 실패는 132, R5-genie 는 28 이다. 재학습 best 의 보고 전용 값은 raw 재집계로 확인했다.

| 점 | V1 | b\* | R5-genie |
|---|---|---|---|
| C2 +6 dB | 4 | 9 | 2 |
| C5 −3 dB | 260 | 314 | 25 |

### 2.6 P3 기초 자료: 루프 동역학 (서술 전용, 새 실행 없음)

EXPERIMENTS 행은 `2026-09-23 13:20 (텍사스 09-22 23:20 CDT)`이다.
- 결과 파일: `conf/results/review_next/p3_loop_groundwork.txt`
- 커밋: 행 기재 b04db838 (결과 파일 헤더 git 도 같다), 결과 커밋 6bbd487d
- 원자료: §2.3 cavity npz (개발 시행 2560..3199, n=640)
- 검정·판정: 없다. 이 시행은 P3 규칙 판정에 재사용하지 않는다(skip ≥ 3200)
- 정정 적용: 분류 이름은 파일 원문(settled / 2-cycle / slow / moving)대로 쓰고 "고정점"이라는 표현은 쓰지 않는다. 근거는 DECISIONS `[2026-09-23 11:47 KST] 정정 — genie 격차 해부의 "꼬리 NMSE 가 반복 8→16 에서 평탄 → 루프가 나쁜 고정점에 갇힘, 반복은 측정으로 배제" 는 진단 없는 과해석이다 (review_next R-10.2)`

C2 −3 dB 결과는 다음과 같다.

| arm | 실패 | settled (실패) | 2-cycle (실패) | slow (실패) | moving (실패) | lost 8→16 | rescued | AUC(실패): r16 / alphaD / tauL |
|---|---|---|---|---|---|---|---|---|
| M-ours-dscore-C-V1 | 88 | 537 (14) | 3 (1) | 32 (13) | 68 (60) | 0 | 11 | 0.98 / 0.99 / 0.98 |
| M-ours-bstar | 132 | 521 (21) | 3 (3) | 22 (21) | 94 (87) | 1 | 13 | 1.00 / 0.99 / 0.97 |

- 분류 기준:
  - settled: max r_13..16 < 1e-3
  - 2-cycle: max c_15..16 < 1e-3 이고 min r_15..16 > 1e-2
  - slow: max r < 1e-2
  - moving: 나머지
- AUC 는 실패 블록에서 신호가 더 클 확률이다. 수신기에서 관측 가능한 신호만 쓴다.
- C2 +6 dB·C5 −3 dB·C1 −3 dB 행과 V0·bstar-scalar arm 은 같은 파일에 있다.

---

## 3. A1: 위상 augmentation (1~3단계 + A1-C5 후속)

**범위와 표기.** testbed는 D2, prior는 S2, V1 = `M-ours-dscore-C-V1`이다. 이 절의 BLER 비교는 모두 aug 체크포인트와 ctrl 체크포인트를 짝지은 것이다. 어느 비교에도 헤드라인 체크포인트 `d2sx_N160000_a1.pt`는 들어가지 않는다. 실패 지표는 `blk_err[:, -1]`(BLER@16)이다. 검정은 house test로, 불일치 쌍에 대한 exact 양측 부호검정이며 기준은 p < 0.05이고 n_d < 6이면 UNDECIDED이다. a:b에서 a는 aug만 실패한 시행 수, b는 ctrl만 실패한 시행 수다. 단계 번호는 EXPERIMENTS 행과 NEXT_EXPERIMENTS §6 A1 행의 표기를 따른다(1단계 = D1 형제 게이트, 2단계 = N=1e4, 3단계 = N=1.6e5). NEXT_EXPERIMENTS §3.1 목록 본문에서는 N=1e4가 "1단계 ablation", N=1.6e5가 "2단계"로 적혀 있다. 테스트 확증과 헤드라인 교체는 같은 목록의 4번과 5번 항목이다.

**모든 표에 공통으로 적용되는 인용 필드와 정정**

| 필드 | 내용 | 출처 |
|---|---|---|
| 평가 가중치 | 새로 학습한 aug/ctrl은 모두 `_best.pt`로 평가했다. 결과 파일 헤더에는 전부 `role=best`, `epoch == best_epoch`로 찍혀 있다 | NEXT_EXPERIMENTS §0 "평가 가중치", 각 결과 파일의 `stage C ckpt` 줄 |
| 헤드라인 체크포인트 | 이 절의 비교에는 쓰이지 않았다. 헤드라인 체크포인트에서 온 값은 P1 위상 비 참조값 0.246 / 0.148 / 0.083뿐이고, 이 값은 **last-EMA@1784(BEST_WEIGHTS_UNAVAILABLE)**로 잰 것이다 | EXPERIMENTS `2026-09-23 08:05 (텍사스 09-22 18:05 CDT)` 행, DECISIONS.md:124 `[2026-09-23 11:47 KST] 정정` (P0-1b) |
| 게이트 상태 표기 | D2 체크포인트에는 게이트 행이 없다. "게이트 통과"는 **"D1 형제 게이트 PASS 레시피"**로 읽는다 | DECISIONS.md:120 `[2026-09-23 11:47 KST] 정정` (G-1.2) |
| ctrl 레시피(N=1.6e5)의 D1 형제 게이트 | `sx_N160000_D1.pt` PASS(LADDER_C.md:1). 이 게이트는 **last-EMA로 측정됐고 best 가중치로는 측정되지 않았다** | DECISIONS.md:120 (G-1.2), DECISIONS.md:126 `[2026-09-23 11:47 KST] 정정` (ckpt/M2) |
| 초기 가중치 | 고정하지 않았다. 모든 aug/ctrl 비교와 attempt 간 비교는 "초기값 차이 포함"이다 | CHANGELOG_REVIEW.md:105 정정 N1, 그 아래의 사용자 결정(2026-09-22 17:45 CDT) |
| 동일 예산 | 학습 데이터 집합, N_train, 레시피, patience 규칙이 같다. 위상 aug는 "같은 학습 데이터이지 같은 정보는 아님"으로 표기한다. epoch 수는 다르다(각 표 참조). aug 체크포인트의 추론 비용 벤치: 출처 없음 | NEXT_EXPERIMENTS §0 "학습 데이터 예산", "계산 예산 (추론)" |
| power 판정 | house test의 조건(n_d ≥ 6)은 C2 +6 dB(n_d 0, **UNDECIDED**)를 뺀 모든 검정에서 충족된다. 08_SPEC §2의 3점 power guard는 테스트 확증에만 쓰이는데, 테스트 확증을 실행하지 않았으므로 해당 없음 | 각 결과 파일 `house test` 줄, NEXT_EXPERIMENTS §3.1 목록 4, NEXT_EXPERIMENTS_A1C5 §2 |

### 3.1 1단계: D1 형제 게이트 (aug 레시피, N=1.6e5)

| 체크포인트 | GA | GB | GC | GD | VERDICT |
|---|---|---|---|---|---|
| `ckpt_review_next/aug_D1_N160000_a1_best.pt` (sha256[:16] a68263d9d388b1fd, role best, epoch 164 = best_epoch) | 9.53939e-16 | 4.80318e-04 | 8.14252e-02 | 6.60872e-02 | **PASS** |

- 결과 파일: `conf/results/review_next/gate_aug_D1_N160000_a1.txt`(2026-09-23 09:15:57 KST, 헤더 commit 240394b9). 게이트 호출은 testbed D1, n_eval 512, n_jac 64였다. 파일에는 "GA is identically zero by construction … PASS therefore rests on GB/GC/GD"라고 적혀 있다.
- EXPERIMENTS 전용 행: 출처 없음. A1s2 행 `2026-09-23 11:12 ~ 11:14 (텍사스 09-22 21:12 ~ 21:14 CDT)`와 A1s3 행 `2026-09-23 08:40 ~ 14:23 (텍사스 09-22 18:40 ~ 00:23 CDT)`가 "D1 형제 게이트 PASS"를 참조한다. 같은 수치가 NEXT_EXPERIMENTS §6 A1 행에도 있다. 판정 커밋은 d217283d(git log)다.
- 이 게이트는 `_best.pt`로 측정했으므로 ckpt/M2 정정(last-EMA 게이트)의 대상이 아니다.

### 3.2 2단계: N_train = 1e4, attempt 1·2·3, 개발 집합 C2 −3 dB (판정점)

EXPERIMENTS 행 `2026-09-23 11:12 ~ 11:14 (텍사스 09-22 21:12 ~ 21:14 CDT)`, commit 73e53af4, 결과 파일 `conf/results/review_next/A1s2_group_C2_m3.txt`

| 항목 | 값 |
|---|---|
| 점, n | D2 C2 (8×4, Tp=4) −3 dB, 개발 집합 skip 2560..3199, **n = 640** |
| V1 실패 aug a1/a2/a3 (best epoch) | 85 (1315) / 82 (1437) / 83 (1384), 평균 83.33 |
| V1 실패 ctrl a1/a2/a3 (best epoch) | 85 (652) / 85 (651) / 88 (661), 평균 86.00 |
| 1차 검정 (3쌍 평균 group) | a:b = 15:19, net −4, **n_d = 34**, p = 0.608, MDD 14 → **판정 불가** |
| 쌍별 (부차) | a1 8:8 p=1 / a2 7:10 p=0.629 / a3 8:13 p=0.383. aug 실패가 더 적은 쌍 2/3, p < 0.05인 쌍 0/3 |
| 맥락 (EXPERIMENTS 행) | GMM b\*(kron K=512) 139, genie 28 |
| 게이트 상태 | N=1e4 aug 레시피의 D1 형제 게이트 행: 출처 없음(1단계 PASS는 N=1.6e5 레시피에 대한 것이다). 비-aug N=1e4 D1 형제는 GC 0.24333으로 FAIL이다(DECISIONS.md:120 G-1.2 줄이 인용한 samplecx_D1.txt:28-30) |
| 보고 전용 지표 (NEXT_EXPERIMENTS §3.1 목록 2: GB′, ε_φ) | 출처 없음 |

### 3.3 3단계: N_train = 1.6e5, attempt 1 한 쌍, 개발 집합

EXPERIMENTS 행은 `2026-09-23 08:40 ~ 14:23 (텍사스 09-22 18:40 ~ 00:23 CDT)`이고, 이 행의 commit은 "240394b9 (평가 시 코드 fe278087 이후)"이다. 결과 파일 헤더의 commit은 b7943e1c, 판정 커밋은 091bf9d5(git log)다. ctrl은 H0 통제 재학습의 best이며, 그 행은 EXPERIMENTS `2026-09-23 07:14 ~ 13:39 (텍사스 09-22 17:14 ~ 23:39 CDT)`(commit 115d391f)이다.

| 체크포인트 | sha256[:16] | best epoch / 총 epoch | 게이트 상태 |
|---|---|---|---|
| aug `aug_N160000_a1_best.pt` | 40c55cb294340594 | 1082 / 1102 | D1 형제 게이트 PASS 레시피(이 절 3.1) |
| ctrl `ctrl_N160000_a1_best.pt` | e2b22673ac91ed8f | 1247 / 1267 | D1 형제 게이트 PASS 레시피(last-EMA 게이트, ckpt/M2) |

| 점 (n = 640, skip 2560..3199) | 등록상 지위 | aug | ctrl | a:b | n_d | p | MDD | 라벨 | b\* / genie | 결과 파일 |
|---|---|---|---|---|---|---|---|---|---|---|
| C2 −3 dB | **판정점** | 84 | 85 | 9:10 | 19 | 1 | 11 | **판정 불가** | 132 / 28 | `A1s3_aug_vs_ctrl_C2_m3.txt` |
| C2 +6 dB | 보고 전용 | 4 | 4 | 0:0 | 0 | 1 | n/a | **UNDECIDED** (n_d < 6) | 9 / 2 | `A1s3_aug_vs_ctrl_C2_p6.txt` |
| C5 −3 dB (Tp=3) | 보고 전용 | 238 | 260 | 16:38 | 54 | 0.00384 | 16 | p < 0.05, aug 실패가 더 적음(보고 전용, 판정 아님) | 314 / 25 | `A1s3_aug_vs_ctrl_C5_m3.txt` |

- 판정점이 판정 불가였으므로 NEXT_EXPERIMENTS §3.1 목록 4(테스트 집합 확증)의 조건이 충족되지 않았고, 테스트 확증은 실행하지 않았다(EXPERIMENTS 행). 목록 5(헤드라인 교체)도 발동하지 않았다(NEXT_EXPERIMENTS_A1C5 머리말 "v3 §3.1 과의 관계").
- EXPERIMENTS 행의 기록: "C5 신호는 사전 등록상 보고 전용 — 확인하려면 C5 를 판정점으로 한 새 사전 등록 필요(사용자 결정)". 이 신호는 보고 전용 2점 중 하나에서 나온 것이다(사후 선택, NEXT_EXPERIMENTS_A1C5 §0).

### 3.4 A1-C5 후속: 별도 사전 등록 (v2, ad32f48b 동결)

- 등록 문서는 `conf/results/review_next/NEXT_EXPERIMENTS_A1C5.md`, 동결 기록은 DECISIONS `[2026-09-24 01:30 KST]`이다. §1~§3은 ad32f48b 이후 바뀌지 않았다(git diff 결과, 변경은 §5 이후뿐이다). 이 등록은 사용자 결정(2026-09-23 09:40 CDT)에 따른 **별도 추가 등록**이다. 통과해도 v3 5단계를 되살리지 않고(머리말), 헤드라인도 바꾸지 않는다(§1).
- 1차 검정 H9는 **새 쌍 a2·a3만** 쓴 2쌍 평균 부호검정이다. 점은 C5 −3 dB, 판정 집합은 skip 4480..5759(n = 1280), 검정 수는 1, α = 0.05다. a1 쌍은 보고 전용이다.
- 학습 행: EXPERIMENTS `2026-09-23 23:38 ~ 09-24 07:14 KST (텍사스 09-23 09:38 ~ 17:14 CDT)`, commit f5856204. 학습은 등록(ad32f48b)보다 먼저 시작했고, 평가는 identity 커밋 57709965 이후에만 했다.
- 평가 행: EXPERIMENTS `2026-09-24 07:15 ~ 07:25 KST (텍사스 09-23 17:15 ~ 17:25 CDT)`. 이 행의 commit은 710a5a3f(identity 커밋 57709965)다. 결과 파일 헤더의 commit은 57709965, 판정 커밋은 495a8ff4(git log)다. §6.2의 "2026-09-23 17:45 CDT 추가" 문단은 커밋 6d56404a(git log 시각 09-24 07:36 KST = 09-23 17:36 CDT)에 들어 있다.

**체크포인트 자격과 identity** (`a1c5_ckpts.json`, DECISIONS `[2026-09-24 07:15 KST]`): 6개 모두 자격이 있고, 전부 `stopped_by=patience`, `aborted=False`다.

| | a1 | a2 | a3 |
|---|---|---|---|
| aug sha256[:16] (best / last epoch) | 40c55cb294340594 (1082 / 1102) | 3f3639584bc626e7 (1444 / 1464) | 646926eb5f77b25d (1320 / 1340) |
| ctrl sha256[:16] (best / last epoch) | e2b22673ac91ed8f (1247 / 1267) | a45fdf61281dfcc6 (1037 / 1057) | 23ed9e6db8d865f7 (1426 / 1446) |

게이트 상태: aug는 D1 형제 게이트 PASS 레시피다. a2·a3에는 D1 형제가 없으므로 레시피 단위 자격이다(§1 "자격 (레시피)"). ctrl은 D1 형제 게이트 PASS 레시피이고, 그 게이트는 last-EMA로 측정됐다(ckpt/M2).

**수용 검사: ACCEPT OK** (`A1C5_accept_C5.txt`, `A1C5_accept_C2.txt`, commit 57709965). 청크 계획은 32 / 16 / 16이다. 태그마다 sha 일치와 role=best, epoch == best_epoch를 확인했다. `M-ours-bstar`·`R5-genie`는 6개 태그 사이에서 비트 동일이다.

**판정점 C5 −3 dB (n = 1280, skip 4480..5759)**, V1 실패 수. 맥락: b\* 642, genie 59.

| 비교 | aug | ctrl | a:b | n_d | p | MDD | 라벨 | 결과 파일 |
|---|---|---|---|---|---|---|---|---|
| **H9 (a2·a3 2쌍 평균, 1차)** | 517.5 | 521.5 | 70:71 | 141 | 1 | 25 | **판정 불가** | `A1C5_H9_C5_m3.txt` |
| a1 쌍 (보고: 개발 신호 16:38의 재현 검사) | 528 | 526 | 47:45 | 92 | 0.917 | 20 | p ≥ 0.05 (보고) | `A1C5_rep_pair_a1_C5_m3.txt` |
| a2 쌍 (보고) | 517 | 524 | 42:49 | 91 | 0.53 | 21 | p ≥ 0.05 (보고) | `A1C5_rep_pair_a2_C5_m3.txt` |
| a3 쌍 (보고) | 518 | 519 | 50:51 | 101 | 1 | 21 | p ≥ 0.05 (보고) | `A1C5_rep_pair_a3_C5_m3.txt` |
| 3쌍 group (보고) | 521.00 | 523.00 | 78:77 | 155 | 1 | 27 | p ≥ 0.05 (보고) | `A1C5_rep_group3_C5_m3.txt` |

**보고 전용 점 (n = 640, skip 4480..5119; 판정 아님)**

| 점 | V1 aug a1/a2/a3 | V1 ctrl a1/a2/a3 | 2쌍 group | 3쌍 group | 쌍별 a1 / a2 / a3 | b\* / genie |
|---|---|---|---|---|---|---|
| C5 0 dB | 94 / 97 / 85 | 104 / 92 / 92 | 24:24, n_d 48, p=1 | 28:34, n_d 62, p=0.526 | 14:24 p=0.143 / 19:14 p=0.487 / 11:18 p=0.265 | 133 / 9 |
| C2 −3 dB | 103 / 100 / 98 | 100 / 100 / 99 | 13:13, n_d 26, p=1 | 18:17, n_d 35, p=1 | 11:8 p=0.648 / 8:8 p=1 / 8:9 p=1 | 170 / 27 |

결과 파일은 `A1C5_rep_group{2,3}_{C5_0,C2_m3}.txt`와 `A1C5_rep_pair_a{1,2,3}_{C5_0,C2_m3}.txt`다. a2·a3 쌍별 값은 NEXT_EXPERIMENTS_A1C5 §6.2의 "2026-09-23 17:45 CDT 추가" 문단에도 있다.

**보고 전용 지표 (GPU; 판정에 쓰지 않음)**

| 체크포인트 | GB′ worst excess (학습 prior 대 b\* kron K=1024 @ N_train 1.6e5, n_eval 512) | ε_φ 위상 비 low / mid / high (held-out, k′=1..7, n_phase 512) |
|---|---|---|
| aug a1 / a2 / a3 | −12.3687% / −12.3201% / −12.4046% | 0.2299/0.1406/0.0758 · 0.2335/0.1396/0.0768 · 0.2283/0.1382/0.0745 |
| ctrl a1 / a2 / a3 | −12.1866% / −12.4614% / −12.3518% | 0.2486/0.1509/0.0824 · 0.2432/0.1494/0.0812 · 0.2428/0.1469/0.0789 |
| 참조: 헤드라인 `d2sx_N160000_a1.pt` (**last-EMA@1784, BEST_WEIGHTS_UNAVAILABLE**) | — | 0.2460/0.1482/0.0830 (`p1_heldout.txt`, commit 1022fff0, EXPERIMENTS `2026-09-23 08:05 (텍사스 09-22 18:05 CDT)` 행) |

결과 파일은 `gbprime_review_next_A1C5_{aug,ctrl}_a{1,2,3}.txt`(commit 57709965, 헤더 "NOT used for any judgement")와 `p1_heldout_review_next_A1C5_{aug,ctrl}_a{1,2,3}.{txt,npz}`(commit 57709965, 헤더 "NOT the registered n/grid/ckpt: no verdict", 본문 "NOT A VERDICT")다.

**등록 규칙에 따른 처리** (NEXT_EXPERIMENTS_A1C5 §2, §6.4, DECISIONS `[2026-09-24 07:30 KST]`): H9가 판정 불가이므로 A1은 등록된 라벨 "개발 집합 보고 전용 신호, 새 학습 쌍의 새 시행에서 재현되지 않음(판정 불가)"으로 닫혔다. 테스트 집합 확증은 발동하지 않았다. 헤드라인과 v3 2·3단계 판정은 바뀌지 않았다.

**사전 예측 대조** (NEXT_EXPERIMENTS_A1C5 §6.5 표의 라벨을 그대로 옮김)

| §3 예측 | §6.5 기록 |
|---|---|
| H9: 지지, net(a−b) = −30 ~ −90 | 빗나감 (net −1, 판정 불가) |
| a1 쌍 재현 net −20 ~ −60, p < 0.05 | 빗나감 (net +2, p = 0.92) |
| 새 2쌍 각각 aug가 적음(2/2), p < 0.05인 쌍 1~2 | 방향 2/2 적중(−7, −1), p < 0.05인 쌍 0으로 빗나감 |
| 3쌍 group 지지 | 빗나감 (78:77) |
| C5 0 dB: aug가 적지만 판정 불가 | 2쌍 group 24:24에서 "aug가 적음"은 빗나감, 판정 불가는 적중. 3쌍 group 28:34 |
| C2 −3 dB: 판정 불가 | 적중 (13:13, 18:17) |
| GB′: aug ≈ ctrl (1%p 이내) | 적중 (−12.19 ~ −12.46%) |
| ε_φ: aug < ctrl | 적중 (세 쌍·세 구간 모두) |

---

## 4. P3: 반복 루프 규칙 (판정 집합 + 테스트 집합 확증)

**출처 행 (`docs/EXPERIMENTS.md`, 첫 열 원문 그대로)**
- [E-P3] `2026-09-23 23:35 ~ 23:46 KST (텍사스 09:35 ~ 09:46 CDT), 판정 23:58 KST`: 실행 커밋 f5856204, 판정 코드 커밋 39e13126
- [E-P3test] `2026-09-24 00:12 ~ 01:02 KST (텍사스 09-23 10:12 ~ 11:02 CDT), 판정 01:05 KST`: 실행 커밋 d00bb877, 판정 코드 커밋 2b599c14 (행 원문: "결과 관측 전 커밋")

**사전 등록**: `conf/results/review_next/NEXT_EXPERIMENTS_P3.md` v2. §1~§3·§6은 d7e404ff에서 동결됐다(`p3_rules_C2_m3.txt:9` "frozen d7e404ff"). 구현 시 해석 명확화 §5.1 1~4는 `conf/DECISIONS.md` `[2026-09-23 23:58 KST]` 항목과 같은 내용이다. 둘 다 판정 데이터를 열기 전에 기록됐다. §5.1 5는 나중에 추가된 항목이다(2026-09-23 11:30 CDT, 기록 감사).

**공통 인용 필드** (`conf/STATUS.md` "인용 규칙" (i)~(v))

| 필드 | 값 | 출처 |
|---|---|---|
| (i) n | 판정 집합 1280 (C2 −3 dB), 보고 전용 640, 테스트 2560/SNR | 각 결과 파일 헤더 |
| (ii) testbed·셀·SNR | D2, prior S2. C2 (Nr8 Nt4 T16 Tp4), C5 (Nr8 Nt4 T16 Tp3). SNR은 각 절에 적는다 | `run_manifest_review_next_P3{,ref,test}.json` `.cells` |
| 체크포인트 | `conf/ckpt/d2sx_N160000_a1.pt`. 평가된 것은 **last-EMA @1784**이며 best @1764의 가중치는 저장되지 않았다(`BEST_WEIGHTS_UNAVAILABLE`). sha256[:16] 4443921ce8d5c4a1, role legacy-last | manifest `.stagec_checkpoint`. 정정: `conf/DECISIONS.md` `[2026-09-23 11:47 KST] 정정 — Stage C 학습 arm 은 best 가 아니라 마지막 epoch EMA 로 평가됐다 (review_next P0-1b)` |
| (iii) 게이트 | manifest 원문 `NO GATE RECORD mentions d2sx_N160000_a1.pt -- UNVERIFIED here`. 읽는 법은 **D1 형제 게이트 PASS 레시피**다(`sx_N160000_D1.pt`, `LADDER_C.md:1` PASS) | manifest `.stagec_gate` (세 manifest 동일). 정정: `conf/DECISIONS.md` `[2026-09-23 11:47 KST] 정정 — D2 체크포인트를 "게이트 통과/실패" 로 직접 부른 줄임말 (review_next G-1.2)` |
| (iv) 학습 예산 | V1 N_train 160000 / b\* kron K=1024 ntrain 160000 (`gmm_fits_D2_review_next_P3*` → `gmm_fits_D2_B16e4k` 심볼릭 링크). 읽는 법: "D1 형제 게이트 PASS 레시피 + 동일예산" | manifest `.gmm`, `.sample_counts`. `RECORD_CORRECTIONS_DRAFT.md:1242` (G-1.2, 적용 기록은 위 DECISIONS 줄) |
| 반복 예산 | 규칙마다 다르다. R16 = 16회, R32 = 32회, R-adapt = 멈춘 t, S-res = 3 × 32회 (비용 표 참조) | NEXT_EXPERIMENTS_P3 §2.1, §4 |
| 수신기 | CPU complex128, 모든 arm이 같은 시행(paired), seed 20260926 | manifest `.receiver`, `.run_params`, §1 |
| (v) power guard | 판정 집합: 출처 없음. §1에는 "n_d < 6 → UNDECIDED"만 있다. 테스트 확증: "power guard OK" (V1·b\* 모두) | §1, `p3_confirm_C2.txt:24,35` |
| 검정·라벨 | exact 양측 부호검정, p < 0.05, n_d < 6 → UNDECIDED. 라벨은 지지 / 판정 불가 / UNDECIDED / `반대 방향 (p < 0.05, 실패 많음) -> 지지 아님`. 테스트 확증 라벨은 PASS | §1, §3, §5.1 5 |

### 4.1 판정 집합: C2 −3 dB, n = 1280, 시행 3200..4479 [E-P3]

- 결과 파일: `conf/results/review_next/p3_rules_C2_m3.txt` (헤더 2026-09-23 23:58:43 KST, 커밋 39e13126)
- raw: `conf/raw_review_next_P3ref` (16회), `conf/raw_review_next_P3` (32회 + r_t)
- 수용 검사: PASSED
- 예외(raised) 0. 발산은 모든 규칙에서 0
- R5-genie @16 실패: 53/1280

실패 블록 수:

| prior | R16 | R32 | R-adapt (평균 반복, 최대) | b05 R16 / R32 | fb05 R16 / R32 | S-res | S-conf (보고) | 오라클 (보고, 참 비트) |
|---|---|---|---|---|---|---|---|---|
| V1 | 173 | 154 | 154 (17.80, 32) | 175 / 154 | 183 / 169 | 144 | 139 | 135 |
| b\* | 307 | 290 | 290 (18.75, 32) | 319 / 299 | 326 / 307 | 273 | 265 | 262 |

사전 등록 검정. a는 앞쪽 규칙만 실패한 블록 수, b는 뒤쪽 규칙만 실패한 블록 수다.

| 가설 | V1: a:b, p, MDD@n_d → 라벨 | b\*: a:b, p, MDD@n_d → 라벨 |
|---|---|---|
| H6a R32 vs R16 | 0:19, 3.81e-06, 11 → **지지** | 1:18, 7.63e-05, 11 → **지지** |
| H6b R-adapt vs R16 | 0:19, 3.81e-06, 11 → **지지** | 1:18, 7.63e-05, 11 → **지지** |
| H7-b05 (변형 R16 vs 기본 R16) | 13:11, 0.839, 12 → 판정 불가 | 20:8, 0.0357, 12 → 반대 방향 (p < 0.05, 실패 많음) → 지지 아님 |
| H7-fb05 | 26:16, 0.164, 14 → 판정 불가 | 37:18, 0.0145, 17 → 반대 방향 (p < 0.05, 실패 많음) → 지지 아님 |
| H8 S-res vs 기본 / b05 / fb05 R32 | 2:12 p=0.0129 / 4:14 p=0.0309 / 5:30 p=2.24e-05 → **지지** | 3:20 p=0.000488 / 3:29 p=2.56e-06 / 7:41 p=6.24e-07 → **지지** |

- **§2.4 prior 이득 분리**: d = (V1^규칙 − V1^R16) − (b\*^규칙 − b\*^R16)이다. 결과는 #d>0 : #d<0로 적는다.
  - R32: 17:19, p=0.868 → **판정 불가**
  - R-adapt: 17:19, p=0.868 → **판정 불가**
  - S-res: 36:30, p=0.539 → **판정 불가**
  - 결과 파일에는 MDD가 없다. §7.1은 `pair_tags.mdd`로 14 / 14 / 18을 계산했다.
- **V1 대 b\* 격차 (보고 전용)**: §2.4 판정을 대신하지 않는다(`p3_rules_C2_m3.txt:77-81`).
  - R16: 24:158, p=2.21e-25
  - R32: 18:154, p=4.07e-28
  - R-adapt: 18:154, p=4.07e-28
  - S-res: 14:143, p=4.23e-28
  - **정정**: [E-P3]의 "p ≤ 2e-25"는 "**p ≤ 2.3e-25**"로 읽는다. 판정은 바뀌지 않는다. 근거: `conf/DECISIONS.md` `[2026-09-24 01:21 KST] 정정 — review_next P3 기록의 감사 결과 4건` (1).
- **§3 채택**: H6b가 두 prior 모두에서 지지됐다. net(R-adapt − R32)는 V1 +0, b\* +0이다(기준 ≤ +3). 결과 파일은 "test-set confirmation candidate: R-adapt"로 출력한다.
  - 감쇠 변형과 S-res는 §3에 따라 확증 후보가 아니다.
  - S-res는 별도 사전 등록을 하지 않고 보고 전용으로만 기록한다(`conf/DECISIONS.md` `[2026-09-24 00:15 KST]` (2)).
- **정정 (H7 라벨)**: [E-P3]의 "반대 방향(변형이 나쁨)"은 "변형 R16의 실패가 많음(p < 0.05), H7 지지 아님"으로 읽는다. 품질 주장이 아니다. 근거: NEXT_EXPERIMENTS_P3 §5.1 5 (2026-09-23 11:30 CDT 추가), `[2026-09-24 01:21 KST]` 정정 줄.
- **동률 해석 (§5.1 1)**
  - S-res: 1차 해석과 문자 해석(`S-res|literal`)의 선택이 다른 블록은 0이다. 두 해석에서 H8과 §2.4 결과가 같다(파일 표기 "same verdict as PRIMARY").
  - S-conf: 2블록이 다르다. 문자 해석 값은 V1 141, b\* 267이다.
  - b05 = fb05 < 기본인 블록은 0이다.
- **R-adapt = R32 블록별 일치의 범위** (§7.1, 2026-09-23 11:30 CDT 한정 추가): 기본 V1·b\*와 V1 변형에서만 성립한다. bstar-b05는 C2 +6 dB에서 1블록이 다르다(R-adapt 7, R32 6, `p3_rules_C2_p6.txt:29`).
- **판정 집합 노출 기록 (§5.1 3)**: 동결 전 검토가 시행 3200~3202에서 V1·b\*·b05·fb05의 r_32와 ΔNMSE를 관측했다. 실패 여부는 보지 않았다. 이 시행들은 판정에서 빼지 않았다.

선택 빈도 (§2.3 필수 보고, §7.1 2026-09-23 11:30 CDT 추가). 각 규칙이 고른 실행의 반복 32 결과를 실패/성공으로 나눴다(`p3_rules_C2_m3.txt:88-94`, 1차 해석).

| prior | 규칙 | 기본 (실패/성공) | b05 | fb05 |
|---|---|---|---|---|
| V1 | S-res | 579 (42/537) | 562 (43/519) | 139 (59/80) |
| V1 | S-conf (보고) | 1161 (64/1097) | 51 (37/14) | 68 (38/30) |
| b\* | S-res | 1006 (98/908) | 148 (61/87) | 126 (114/12) |
| b\* | S-conf (보고) | 1034 (102/932) | 108 (82/26) | 138 (81/57) |

비용 (보고 전용): `complexity_moduleH_ep.txt`의 16회 블록 시간을 반복 수에 비례해 환산한 값이다(`p3_rules_C2_m3.txt:97-99`).

| prior | R16 | R-adapt | R32 | S-res / S-conf |
|---|---|---|---|---|
| V1 | 1006 ms | 1119 ms | 2012 ms | 6036 ms |
| b\* | 754 ms | 884 ms | 1508 ms | 4524 ms |

### 4.2 보고 전용 점: n = 640, 시행 3200..3839 [E-P3]

결과 파일은 `p3_rules_C2_p6.txt`와 `p3_rules_C5_m3.txt`다(커밋 39e13126). 두 파일 머리말에 "REPORT-ONLY point (no verdict is a judgement here)"라고 적혀 있다. 아래 라벨은 파일에 출력된 그대로이며 판정이 아니다.

| 점 | prior | R16 | R32 = R-adapt (평균 반복) | S-res | 오라클 | H6a a:b, p → 라벨 | H8 (기본 / b05 / fb05) | §2.4 (#d>0:#d<0) |
|---|---|---|---|---|---|---|---|---|
| C2 +6 dB | V1 | 1 | 1 (16.08) | 1 | 1 | 0:0, p=1 → UNDECIDED | 비교 3개 모두 UNDECIDED → 지지 아님 | R32 0:0, R-adapt 0:0, S-res 1:0 → UNDECIDED (n_d < 6) → 판정 불가 |
| C2 +6 dB | b\* | 6 | 6 (16.12) | 5 | 5 | 0:0, p=1 → UNDECIDED | 비교 3개 모두 UNDECIDED → 지지 아님 | (위와 같음) |
| C5 −3 dB | V1 | 230 | 209 (21.05) | 185 | 178 | 0:21, 9.54e-07 → 지지 | 4:28 p=1.93e-05 / 1:21 p=1.1e-05 / 4:41 p=9.33e-09 → 지지 | R32·R-adapt 15:19 p=0.608, S-res 36:43 p=0.5 → 판정 불가 |
| C5 −3 dB | b\* | 298 | 281 (22.41) | 260 | 254 | 1:18, 7.63e-05 → 지지 | 1:22 p=5.72e-06 / 1:27 p=2.16e-07 / 5:41 p=4.41e-08 → 지지 | (위와 같음) |

- genie 실패: C2 +6 dB 1/640, C5 −3 dB 30/640
- C5 −3 dB의 H7 네 검정은 모두 판정 불가다. V1은 b05 14:18, fb05 28:20이고, b\*는 b05 12:10, fb05 32:25다.
- 발산: 모든 점과 규칙에서 0이다. 예외는 C5 −3 dB의 bstar-fb05로, div16·div32·divAd가 각각 2다(`p3_rules_C5_m3.txt:30`).

### 4.3 테스트 집합 확증: C2, 시행 0..2559, n = 2560/SNR, 1회 실행 [E-P3test]

- 결과 파일: `conf/results/review_next/p3_confirm_C2.txt` (헤더 2026-09-24 01:02:57 KST, 커밋 2b599c14)
- manifest: `run_manifest_review_next_P3test.json`
- raw: `conf/raw_review_next_P3test` (448 파일)
- R16 기준은 이 실행의 반복 16이다. V1·b\*의 모든 KEYS_RAW 필드가 7개 SNR 모두에서 `conf/raw_B16e4k`와 비트 동일하다. Demo 해시도 같다.
- 예외 0, 발산 0
- **정정 (판정 시각)**: [E-P3test]의 "판정 01:05 KST"는 **01:03 KST**로 읽는다. 근거는 p3_confirm_C2.txt 헤더 01:02:57과 커밋 13d353b5 01:03:43이다.
- **정정 (사용자 결정 시각)**: 사용자 결정 시각 "10:15 CDT"는 결정을 기록한 시각이다. 실제 결정은 10:12 CDT 실행 시작보다 앞선다.
- 두 정정의 근거: `conf/DECISIONS.md` `[2026-09-24 01:21 KST]` 정정 (2), (4)

| SNR | V1 R16 → R-adapt (R32) | a:b, n_d, p → 라벨 | b\* R16 → R-adapt (R32) | a:b, n_d, p → 라벨 |
|---|---|---|---|---|
| −3 dB (판정) | 371 → 342 (341) | 2:31, 33, 1.31e-07 → 지지 | 623 → 589 (589) | 1:35, 36, 1.08e-09 → 지지 |
| 0 dB (판정) | 88 → 79 (79) | 0:9, 9, 0.00391 → 지지 | 184 → 162 (159) | 0:22, 22, 4.77e-07 → 지지 |
| +3 dB (판정) | 29 → 25 (24) | 0:4, 4, 0.125 → UNDECIDED | 57 → 49 (49) | 0:8, 8, 0.00781 → 지지 |
| +6 / +9 / +12 / +15 dB (보고) | 16→15 / 7→7 / 5→4 / 3→3 | 전부 UNDECIDED | 28→28 / 17→13 / 16→16 / 8→7 | 전부 UNDECIDED |

- **3점 규칙**
  - V1: wins 2/3, power guard OK → **PASS**
  - b\*: wins 3/3, power guard OK → **PASS**
- 세 점 합산 (보고 전용): V1 2:44 p=3.08e-11, b\* 1:65 p=1.82e-18
- 평균 반복 (−3/0/+3 dB, 보고): V1 17.90 / 16.55 / 16.20, b\* 18.72 / 16.77 / 16.18
- 보고 전용 값 (확증 후보 아님)
  - S-res: V1 303 / 58 / 19, b\* 548 / 131 / 34
  - 오라클: V1 287 / 55 / 15, b\* 529 / 115 / 30
- MDD는 결과 파일에 없다. §3은 MDD 보고를 요구하지 않는다. §7.1의 `pair_tags.mdd` 값은 V1 13 / 7 / n/a, b\* 14 / 12 / 8이다.
- 헤드라인 표는 바꾸지 않는다(§3). 이 결과는 "루프 규칙을 R-adapt 로 바꾼 별도 표"로 기록된다(§7.4).
- R16 실패율은 V1 371/2560 = 0.1449, b\* 623/2560 = 0.2434다. `tables_D2_B16e4k.txt`에는 반올림 값 V1 0.145(:71)와 b\* 0.243(:69)가 인쇄돼 있고, §7.4는 두 값이 "같다"고 기록한다.

### 4.4 §6 사전 예측 대조 (NEXT_EXPERIMENTS_P3 §7.3 기록 그대로)

| 예측 | 기록된 채점 |
|---|---|
| H6a 두 prior 지지 (순 15~25) | 적중 (순 19 / 17) |
| H6b 두 prior 지지, net ≤ +3, 평균 반복 ≈ 18~20 → R-adapt | 적중 (net 0 / 0). V1 17.80은 예측 범위 하한보다 약간 낮고, b\* 18.75는 범위 안에 있다. 이 표기에 대한 감사 지적은 기각됐고 "적중" 표기는 유지된다(`[2026-09-24 01:21 KST]` 줄) |
| H7-b05 판정 불가 | V1 적중, b\* 빗나감 (p = 0.036) |
| H7-fb05 실패 많음 또는 판정 불가 | 적중 (V1 판정 불가, b\* 많음 p = 0.015) |
| H8 지지 아님 | 빗나감 |
| 오라클 실패 30% 이상 감소 | 빗나감. 기본 R32 대비 V1 −12% (154→135), b\* −10% (290→262). R16 대비 −22% / −15% |
| §2.4 세 규칙 판정 불가, V1 < b\* 격차 유지 | 적중 |

---

## 5. C6 (Nr = 16): 여차원 축 (10_SPEC §7)

**출처 행**: `docs/EXPERIMENTS.md` 행 "2026-09-23 05:28 ~ 08:17 (텍사스 09-22 15:28 ~ 18:17 CDT)". 이 절의 수치는 이 행 또는 아래에 적은 결과 파일에서 가져왔다. 비교에 쓴 Nr=8 수치만 행 "2026-09-21 14:00 ~ 09-22 21:45"에서 왔다.

### 5.1 인용 필드

| 필드 | 값 | 출처 |
|---|---|---|
| 실행 | `conf/code/run_nr16run2.sh` = `runner.py run --testbed D2 --cell C6 --prior S2 --n 2560 --chunk 40 --tag NR16run2 --ntrain 10000 --stagec-ckpt ckpt/d2sx_NR16_N10000_a1.pt` | EXPERIMENTS 행 |
| 커밋 | 행: 274cb6fe ("실행 시작 시점 코드 cd241b7e 이후"). 표·guard·manifest 머리말: `git commit d2bab1d6` | EXPERIMENTS 행, `conf/results/tables_D2_NR16run2.txt:2`, `conf/results/guard_D2_NR16run2.txt:2`, `conf/results/review_next/run_manifest_NR16run2.json` |
| testbed / 셀 | D2, prior S2, C6 = 16×4, T=16, Tp=4. C2와 Tp·T·code·SNR이 같고 Nr만 다르다 | 표 머리말, 10_SPEC §7 "설계" |
| SNR 격자 | −3, 0, +3, +6, +9, +12, +15 dB | 표 머리말 |
| n | SNR마다 2560 (raw 448개, `conf/raw_NR16run2`) | manifest `points`, `n_raw_files` |
| seed | 20260926 (행 표기: "trial rng 동일". 규칙은 `default_rng([20260926, TBID, PID, Nr, T, Tp, int(snr)+100])`) | EXPERIMENTS 행, manifest `trial_stream` |
| GMM b\* | kron K=128. Nr=16 K 격자 {16…512}×{full, kron} 12개 적합에서 검증 우도로 선택했다. EM 2123.5 s | 표 머리말, manifest `gmm`, `conf/results/gmm_fits_D2_NR16run2/` (→ `gmm_fits_D2_NR16`) |
| 체크포인트 | `d2sx_NR16_N10000_a1.pt`, sha256[:16]=d7b1af69091e33b8. **평가한 가중치는 last-EMA @1688이다. best @1668 가중치는 저장되지 않았다 (BEST_WEIGHTS_UNAVAILABLE)** | manifest `stagec_ckpt_id`·`stagec_checkpoint`, EXPERIMENTS 행 메모. 정정 근거: `conf/results/review_next/REVIEW_AUDIT.md:20` (P0-1b, "NR16(1688 vs 1668)") |
| 게이트 | **UNGATED** (D1 형제 없음, §7에 사전 등록). 머리말 문자열: "NO GATE RECORD mentions d2sx_NR16_N10000_a1.pt -- UNVERIFIED here" | 10_SPEC §7 "게이트", 표 머리말 |
| 게이트 정정 | §7의 "게이트 통과 주장은 C2(Nr=8)에만 쓴다"는 "D1 형제 게이트 PASS 주장"으로 읽는다 | 10_SPEC §7 인라인 정정 "(2026-09-23, review_next G-1.2)", DECISIONS `[2026-09-23 11:47 KST] 정정 — … (review_next G-1.2)` |
| §7의 지위 | "§6d 와 같은 지위(예산·기하 축 측정, arm 판정 아님)" | 10_SPEC §7 "게이트" |
| 동일 예산 | 설계는 동일 예산 N_train=1e4, 전 arm 같은 채널 집합이다 (10_SPEC §7). GMM은 N_train=10000이다. score는 학습 로그 `ntrain=10000`, manifest `train_channels 10000` (`score_train 9000`, `score_val 1000`)이다. **표 머리말은 V0/V1/V4를 `N_train=1610000  rung=D2SXNR1610000`으로, V4b를 "N_train=10000 -- unclassified arm"으로 적는다. 이 표기를 다룬 정정 기록은 출처 없음** | 10_SPEC §7, `conf/logs/train_nr16.log:1`, manifest, `tables_D2_NR16run2.txt` 머리말 |
| 수신기 | CPU complex128, 192 워커, outer iterations 16 | EXPERIMENTS 행, 표 머리말 |
| 첫 실행 | `NR16run`은 score arm 없이 끝났다 (runner.py:298 가드, raw 448/448개가 stagec_status ABSENT). 행 메모: "arm 없는 기록으로 보존" | EXPERIMENTS 행 메모, `REVIEW_AUDIT.md:26` (S7-b), `conf/results/tables_D2_NR16run.txt` |

### 5.2 BLER@16 (C6, n=2560)

출처: `conf/results/tables_D2_NR16run2.txt` 표 A. 괄호 안은 95% Wilson CI다. +6/+9/+12 dB 열은 같은 파일에 있다.

| arm | −3 dB | 0 dB | +3 dB | +15 dB |
|---|---|---|---|---|
| R1-turbo | 0.262 (0.245,0.279) | 0.104 (0.092,0.116) | 0.053 (0.045,0.063) | 0.005 (0.003,0.009) |
| R2-ours-G | 0.113 (0.102,0.126) | 0.046 (0.038,0.054) | 0.025 (0.019,0.031) | 0.002 (0.001,0.005) |
| M-ours-bstar (kron K=128) | 0.081 (0.071,0.092) | 0.032 (0.026,0.039) | 0.018 (0.014,0.024) | 0.004 (0.002,0.007) |
| M-ours-bstar-scalar | 0.102 (0.091,0.114) | 0.043 (0.035,0.051) | 0.024 (0.019,0.030) | 0.005 (0.003,0.008) |
| M-ours-dscore-C-V0 | 1.000 (0.999,1.000) | 1.000 (0.998,1.000) | 0.999 (0.997,1.000) | 0.710 (0.692,0.727) |
| M-ours-dscore-C-V1 | 0.020 (0.016,0.027) | 0.007 (0.004,0.011) | 0.005 (0.003,0.008) | 0.001 (0.000,0.003) |
| M-ours-dscore-C-V4 | 0.027 (0.021,0.034) | 0.012 (0.009,0.017) | 0.004 (0.002,0.008) | 0.002 (0.001,0.004) |
| M-ours-dscore-C-V4b | 0.029 (0.023,0.037) | 0.011 (0.008,0.016) | 0.004 (0.002,0.007) | 0.002 (0.001,0.004) |
| R5-genie | 0.009 (0.006,0.013) | 0.004 (0.002,0.007) | 0.003 (0.002,0.006) | 0.000 (−0.000,0.001) |

실패 수 (n=2560). 굵게 표시하지 않은 값은 EXPERIMENTS 행의 값이다. † 표시는 행에 없는 값으로, `conf/raw_NR16run2`의 `|blk_err` @16을 다시 집계했거나 행의 수치로 계산했다.

| SNR | b\* | V1 | genie | bstar-scalar | V4 | b\*/V1 | genie 격차 회수 (b\*−V1)/(b\*−genie) |
|---|---|---|---|---|---|---|---|
| −3 dB | 207 | 52 | 22 | 261 | 68 | 3.98 | 0.838 |
| 0 dB | 81 | 18 | 10 | 109 † | 31 † | 4.50 † | 0.887 |
| +3 dB | 47 | 12 | 8 | 61 † | 11 † | 3.92 † | 0.897 |

**발산 가드** (`conf/results/guard_D2_NR16run2.txt`, 규칙: 16회 반복 중 한 번이라도 NMSE > 10.0이거나 비유한이면 발동): V0는 모든 SNR에서 발동했다. 발동 수는 −3 dB 2560/2560, 0 dB 2560/2560, +3 dB 2558/2560, +6 dB 2553/2560, +9 dB 2529/2560, +12 dB 2447/2560, +15 dB 2186/2560이다. 나머지 12개 arm은 한 번도 발동하지 않았다. R5-genie에는 가드가 적용되지 않는다 ("not applicable").

### 5.3 짝지음 부호검정 (표 B, @16. 'a:b' = 첫 arm만 실패 : 둘째 arm만 실패)

출처: `tables_D2_NR16run2.txt` 표 B. 판정 열은 파일 출력 문자열을 그대로 옮겼다. §7 실행은 "arm 판정 아님"이다 (5.1 참고).

| 쌍 (anchor) | 판정 SNR | −3 dB | 0 dB | +3 dB | pooled | power guard | 파일의 판정 문자열 |
|---|---|---|---|---|---|---|---|
| bstar → V1 (bstar) | −3, 0, +3 | 163:8 p=1.1e-38 | 66:3 p=1.9e-16 | 37:2 p=2.8e-09 | 266:13 p=1.6e-62 | POWERED | second arm fewer failures at 3/3 points, first arm fewer failures at 0/3 points -> significant |
| bstar → V4 (bstar) | −3, 0, +3 | 156:17 p=2.6e-29 | 58:8 p=1.8e-10 | 37:1 p=2.8e-10 | 251:26 p=2.2e-47 | POWERED | second arm fewer failures at 3/3 points, first arm fewer failures at 0/3 points -> significant |
| bstar → V4b (bstar) | −3, 0, +3 | 157:25 p=1.4e-24 | 60:8 p=5.7e-11 | 38:1 p=1.5e-10 | 255:34 p=4.9e-43 | POWERED | second arm fewer failures at 3/3 points, first arm fewer failures at 0/3 points -> significant |
| bstar → bstar-scalar (bstar) | −3, 0, +3 | 35:89 p=1.3e-06 | 17:45 p=0.0005 | 10:24 p=0.024 | 62:158 p=7.6e-11 | POWERED | second arm fewer failures at 0/3 points, first arm fewer failures at 3/3 points -> significant |
| bstar → V0 (bstar) | −3, 0, +3 | 0:2353 p=0 | 0:2478 p=0 | 0:2511 p=0 | 0:7342 p=0 | POWERED | second arm fewer failures at 0/3 points, first arm fewer failures at 3/3 points -> significant |
| R2-ours-G → bstar-scalar (R2-ours-G) | −3, 0, +3 | 103:74 p=0.035 | 50:42 p=0.47 | 28:26 p=0.89 | 181:142 p=0.034 | POWERED | second arm fewer failures at 1/3 points, first arm fewer failures at 0/3 points -> not significant |
| bstar → genie (R5-genie) | −3 | 189:4 p=9.1e-51 | — | — | 189:4 p=9.1e-51 | UNDECIDED (판정점 1개, 3개 필요) | UNDECIDED -- no significance call is made |
| V1 → genie (R5-genie) | −3 | 36:6 p=2.8e-06 | — | — | 36:6 p=2.8e-06 | UNDECIDED | UNDECIDED -- no significance call is made |
| V4 → genie (R5-genie) | −3 | 51:5 p=1.2e-10 | — | — | 51:5 p=1.2e-10 | UNDECIDED | UNDECIDED -- no significance call is made |
| V4b → genie (R5-genie) | −3 | 60:7 p=1.3e-11 | — | — | 60:7 p=1.3e-11 | UNDECIDED | UNDECIDED -- no significance call is made |

### 5.4 같은 예산(N_train=1e4)의 Nr=8(C2)과 나란히 본 값, −3 dB

| 항목 | Nr=8 C2 (`raw_B1e4`) | Nr=16 C6 (`raw_NR16run2`) |
|---|---|---|
| 출처 행 | "2026-09-21 14:00 ~ 09-22 21:45" (커밋 열 "8fb27f5 (마감 시점)". 표 머리말 `git commit 2fd1a43`) | "2026-09-23 05:28 ~ 08:17 (텍사스 09-22 15:28 ~ 18:17 CDT)" |
| 결과 파일 | `conf/results/tables_D2_B1e4.txt` | `conf/results/tables_D2_NR16run2.txt` |
| 표 머리말의 예산 표기 | V0/V1/V4 `N_train=10000 rung=D2SX10000`, GMM arm N_train=10000 | V0/V1/V4 `N_train=1610000 rung=D2SXNR1610000`, GMM arm N_train=10000, manifest `train_channels 10000` (5.1 참고) |
| GMM b\* | kron K=512 (raw meta `meta\|kron_K`) | kron K=128 |
| score ckpt | `d2sx_N10000_a1.pt`, last-EMA 673 (best 653) (DECISIONS `[2026-09-23 11:47 KST] 정정 … (review_next P0-1b)`) | `d2sx_NR16_N10000_a1.pt`, last-EMA @1688 (best @1668) |
| 게이트 | D2 자체 게이트 행 없음. "D1 형제(N=1e4)가 게이트에 실패한 레시피·예산의 D2 체크포인트" (D1 GC 0.24333 FAIL) (`conf/STATUS.md:996` 정정 G-1.2) | UNGATED (D1 형제 없음) |
| 실패 수 b\* / V1 / genie (n=2560) | 646 / 372 / 87 | 207 / 52 / 22 |
| b\*/V1 | 1.74 | 3.98 |
| genie 격차 회수 | 0.490 | 0.838 |
| bstar → V1 부호검정 −3 dB | 323:49 p=1.3e-50, POWERED (`tables_D2_B1e4.txt:369-370`) | 163:8 p=1.1e-38, POWERED |

행 메모: "같은 예산 Nr 8→16 에서 GMM 실패 646→207(1/3.1), V1 372→52(1/7.2)".

### 5.5 §7 사전 등록 예측과 기록된 대조

§7에 등록된 것은 예측 문구와 "빗나갈 경로"이다. 지지/기각 같은 판정 라벨을 등록한 기록은 **출처 없음**이다. 아래 대조 열은 EXPERIMENTS 행의 문구를 그대로 옮겼다.

| # | 10_SPEC §7 예측 (문구 그대로) | 기준값 (§7 본문) | EXPERIMENTS 행의 대조 (인용) |
|---|---|---|---|
| 1 | "V1 이 메운 genie 격차가 Nr=16 에서 60% 를 넘는다" | Nr=8 전체 실측 47% | "회수 >60% — 0.838" |
| 2 | "GMM/V1 의 BLER 비가 Nr=8 의 1.68 (C2 −3 dB, K=1024 격자)보다 커진다" | 1.68 | "비 >1.68 — 3.98" |
| 3 | "GMM 쪽이 더 나빠져서 그렇게 된다" | — | "같은 예산 Nr 8→16 에서 GMM 실패 646→207(1/3.1), V1 372→52(1/7.2): 비 상승은 V1 의 감소폭이 더 커서이고 예측 문구와 다름" |
| 4 | "대조군 `bstar → bstar-scalar` 는 Nr=16 에서도 무의미하거나 행렬 site 우세" | — | "bstar < bstar-scalar(207<261) — 행렬 site 우세" (표 B: pooled 62:158, POWERED, 5.3 참고) |

§7 예측의 기준값(47%, 1.68, K=1024 격자)과 5.4의 같은 예산 Nr=8 비교값(0.490, 1.74, `raw_B1e4` K=512)은 출처가 다르다.

### 5.6 GB′ (보고 전용): held-out denoising NMSE, GMM 대 diffusion, Nr=16

- 출처 파일: `conf/results/d2_gbprime_NR16_N10000_a1.npz` (배열 `sigma`, `nu`, `nmse_gmm`, `nmse_model`, 각 20점).
- 상태 기록: `conf/results/review_next/NEXT_EXPERIMENTS.md:157` "완료 (GPU, CPU 대조 7.4e-15)".
- 이 파일을 추가한 커밋: 28717307 (git log). EXPERIMENTS 행, 실행 커밋, n_eval, 사용한 체크포인트·GMM의 식별자: **출처 없음**. npz에는 메타데이터가 없다.
- σ 격자: `conf/results/sigma_grid_D2_NR16` [3.2832e-02, 4.9152e-01], 20점 (`train_nr16.log:1`). Nr=8의 동결 D2 격자(`gate_D2.txt`, 3.3062e-02 ~ 8.4516e-01)와 다르다.
- 비 = nmse_model / nmse_gmm. npz의 두 배열에서 계산했다.

| k | σ | nmse_gmm | nmse_model | 비 |
|---|---|---|---|---|
| 0 | 3.2832e-02 | 1.73491e-03 | 6.72419e-04 | 0.3876 |
| 9 (비 최소) | 1.1830e-01 | 2.02018e-02 | 6.34561e-03 | 0.3141 |
| 19 (비 최대) | 4.9152e-01 | 2.22805e-01 | 1.05627e-01 | 0.4741 |

`tables_D2_NR16run2.txt` 표 D에 인쇄된 GB′는 `gate_D2.txt`에서 가져온 값이다 (summary `'Nr': 8`, n_eval 512, 비 0.5204–0.8781). **Nr=16 값이 아니다.**

---

## 6. 인용 주의: 쓰면 안 되는 것, 정정된 수치, 보고 전용·사후 선택 신호

> 이 절은 목록만 담는다. 해석과 결론은 넣지 않았다. 판정 라벨은 출처 파일에 적힌 문자열을 그대로 옮겼다. 경로는 `conf/`를 기준으로 적었고, `docs/`만 예외다. "EXP 행"은 `docs/EXPERIMENTS.md`의 첫 열(날짜) 문자열이다. 정정은 모두 append 줄이나 인라인 노트로만 있고 원문 행은 고치지 않았다(각 DECISIONS 정정 줄의 "원문 불변"). `RECORD_CORRECTIONS_DRAFT.md`는 머리에 "초안 (미적용)"이라고 적혀 있다. 실제로 적용된 것은 DECISIONS 줄이 "적용"이라고 적은 STATUS·PAPER_MATERIALS·DECISIONS·NUMBERS_PACKAGE 노트다. 아래 "정정 줄" 열은 이 적용분만 가리킨다. DECISIONS 정정 줄 본문에 적힌 줄 번호는 cd241b7e 기준이라 현재 파일과 다를 수 있다. 아래 표의 위치는 현재 파일에서 확인한 줄 번호다. 현재 파일에서 확인하지 못한 번호에는 "(cd241b7e)"를 붙였다.

### 6.1 정정된 읽기: 원 표기 대신 이 읽기로 인용한다

| # | 원 표기 (위치) | 정정된 읽기 | 정정 줄 | EXP 행 · 커밋 · 결과 파일 |
|---|---|---|---|---|
| 1 | 헤드라인 평가 체크포인트를 "best val 3.519379e-01 @1764"로 소개 (STATUS:669, PAPER_MATERIALS:426·640·1022, NUMBERS_PACKAGE:198) | 평가 = `d2sx_N160000_a1.pt` **last-EMA @1784** (ema sha256[:16] a43f1105eb27a29b, 이 가중치의 val 3.519602e-01). 선택 기준 best val은 3.519379e-01 @1764이고, 이 가중치는 저장되지 않았다(**BEST_WEIGHTS_UNAVAILABLE**). 대상은 raw_C D2·raw_B16e4·raw_B16e4k의 V0/V1/V4/V4b 헤드라인 전부다(V1 C2 −3 dB는 세 곳 모두 371/2560) | DECISIONS.md:124, :141, :145 (2); STATUS.md:671; PAPER_MATERIALS.md:428, :643, :1071; NUMBERS_PACKAGE:200; `results/review_next/REVIEW_AUDIT.md:20` (P0-1b) | `2026-09-21 14:00 ~ 09-22 21:45` · 8fb27f5 · `results/tables_D2_B16e4k.txt` |
| 2 | D1 게이트 PASS (GB 2.66e-3 / GC 0.0999 / GD 0.0718)를 best 가중치의 값으로 읽음. "0.003 % 차" | 게이트 = `sx_N160000_D1.pt` **@200 EMA**다(best @136 가중치 미저장). λ=0.01 PASS도 @200 EMA다(best @142). 출처 문장은 "best 가중치에서 판정이 달라지는지는 확인되지 않았다"이다. 0.003 %는 best val끼리의 차다. 게이트된 @200 EMA끼리는 7.398687e-01 대 7.409458e-01로 0.146 %다. LADDER_C 2·3·4·6행 "holds the best-val EMA"는 거짓이다. `results/gate_D1_C.txt` HEAD 판에는 `sx_V3_N160000_D1_a3.pt` FAIL만 남아 있다. V0 PASS의 원 파일은 커밋 7f5f5a21 판이고, PASS 행은 `LADDER_C.md:1`에 있다 | DECISIONS.md:126, :128, :141, :143 (a)(d), :145 (3); PAPER_MATERIALS.md:349, :858; NUMBERS_PACKAGE:435, :767 | 같은 행 · 8fb27f5 · `LADDER_C.md:1` |
| 3 | D2 체크포인트에 "게이트 통과 + 동일예산"을 직접 붙인 표기 (EXP 행 결과 열, NUMBERS_PACKAGE:3·P1·P13, PAPER_MATERIALS:945-952 (cd241b7e 905-911)). PAPER_MATERIALS:23-25 "그 체크포인트로 두 testbed의 확증" | **"D1 형제 게이트 PASS 레시피 + 동일예산"**으로 읽는다. D2 체크포인트에는 게이트 행이 없다(`tables_D2_B16e4k.txt:45` "NO GATE RECORD mentions d2sx_N160000_a1.pt -- UNVERIFIED here"). PASS 판정은 `LADDER_C.md:1` `sx_N160000_D1.pt`에서 나왔다. N=1e4·4e4 D2 체크포인트는 "D1 형제 게이트 FAIL"이다(GC 0.24333 / 0.16651, `samplecx_D1.txt:28-29`). D2 확증은 `sx_N160000_D1.pt`가 아니라 `d2sx_N160000_a1.pt`로 돌렸다. "게이트 통과 예산"은 예산을 가리키는 표현이라 원문 그대로 둔다 | DECISIONS.md:120, :135, :137, :145 (4); PAPER_MATERIALS.md:31, :853-856, :954; NUMBERS_PACKAGE:4, :558, :700 | 같은 행 · 8fb27f5 |
| 4 | A8 "학습 prior 4.6× GMM(K=512)" (EXP 행 결과 열, NUMBERS_PACKAGE P12, `complexity_moduleH.txt:16-17`, F14 캡션) | A8은 등방 `denoise_full` 마이크로벤치마크다(K=512, `d2sx_N10000_a1.pt`). arm 간 수신기 비용비가 아니다. 같은 코드로 다시 돌렸을 때 4.6×는 재현되지 않았고, 그 수치는 저장되지 않았다. **실경로 V1/b\* = Module H 호출당 1.35× (−3 dB) · 1.39× (+6 dB), 블록 전체 1.33× · 1.38×** (kron K=1024 + `d2sx_N160000_a1.pt`, SNR당 24 시행 중앙값) | DECISIONS.md:122, :139, :145 (1); NUMBERS_PACKAGE:765 | `2026-09-23 11:16 ~ 11:25 (텍사스 09-22 21:16 ~ 21:25 CDT)` · d217283d · `results/review_next/complexity_moduleH_ep.txt:21-24` |
| 5 | R5-genie / R6-exactEP / M-ours-score를 "상한·bound·headroom"으로 부름 (NUMBERS_PACKAGE (F)5, PAPER_MATERIALS §17.6, 그림 범례 "genie CSI (lower bound)") | R5-genie = known-channel receiver reference(동일 EP detector + BCJR, 참 H). R6-exactEP = exact-prior EP reference. M-ours-score = oracle/exact-score reference receiver. 차이는 "reference까지의 격차"로 적는다. 출처가 든 근거: C2 −3 dB에서 V1 성공·genie 실패 15 블록(n=2560). UNDECIDED여서 검정 진술을 금지한 판정은 그대로다 | DECISIONS.md:114, :131, :133; PAPER_MATERIALS.md:904; NUMBERS_PACKAGE:650 | `raw_B16e4k`·`raw_C` `blk_err[:,15]` |
| 6 | genie 격차 해부 [2026-09-23 00:10]: "0.0281은 prior로 못 줄인다 / 0.1168 채널추정 귀속", "87 % 겹침 → prior 문제 아님", "나쁜 고정점, 반복 배제" (DECISIONS:104, STATUS:1756 (cd241b7e 1675-1676), 커밋 6ed06139) | 쌍별 계수만 적는다. genie 실패 87, V1 실패 371, 동시 실패 72 (0.0281), V1만 실패 299 (0.1168), genie만 실패 15. 겹침 250은 V1 꼬리(289)의 86.5 %다. GMM 꼬리의 69.2 %(563/813)는 V1에서 꼬리가 아니다. "고정점"은 진단 자료가 생길 때까지 쓰지 않는다. V1 전체 실패는 it8 433, it16 371이다 | DECISIONS.md:108, :110, :112; STATUS.md:1758 | `raw_B16e4k` C2 −3 dB n=2560 |
| 7 | D2를 "물리적으로 표준인 mmWave 모델"로, "α_ℓ∼CN → GMM correctly specified"로 서술 | "조건부 Gaussian 파괴를 분리하는 통제된 희소 정반사 모델"로 적고, "유한 K GMM은 근사"로 적는다 | DECISIONS.md:116, :118; PAPER_MATERIALS.md:805; NUMBERS_PACKAGE:716 ((F)56) | — |
| 8 | STATUS 요약의 수치: C1 −3 dB BLER `nan`, D1 가드 "1400/1400"·V1 "6.6e+17", V4 가드 2560/2560, 재시딩 9372, §6d "ALL POWERED" | 출처 판정은 "Source wins"다. BLER 1.000/1.000/0.996 (X1), V4 2552/2560 (X6), D1 가드 2560/2560·V1 최악 NMSE 1.654e+20 (X7), 재시딩 9144 (X10). §6d 표에는 UNDECIDED 7쌍이 있다(`tables_D2_B1e4.txt:391-414`) | DECISIONS.md:90; NUMBERS_PACKAGE:21, :26, :27, :30, :606 (E6 :583-610) | `tables_D2_B1e4x.txt:74-76`, `guard_D2_B1e4x.txt:18-22`, `guard_D1_C.txt:18-21` |
| 9 | V0 D2 a1 best val "3.519459e-01 @1756" (STATUS:652, 22:25 절) | 3.519379e-01 @1764를 쓴다. 3.519459e-01은 실행 도중에 적힌 중간값이었다. 평가 가중치는 행 1과 같다 | PAPER_MATERIALS.md:887, :1065-1071; STATUS.md:799 | `logs/train_d2sx_N160000_a1.log` 마지막 행 |
| 10 | P3 기록: "p ≤ 2e-25", "판정 01:05 KST", "변형이 나쁨", "R-adapt == R32" | "p ≤ 2.3e-25"(R16 p 2.21e-25), 판정 01:03 KST로 읽는다. "변형이 나쁨"은 "변형 R16의 실패가 많음(p < 0.05), H7 지지 아님"으로 읽으며 품질 주장이 아니다. R-adapt와 R32의 일치는 판정 집합의 기본 실행 V1·b\*과 V1 변형에만 해당한다. bstar-b05는 C2 +6 dB에서 1블록 다르다. 테스트 집합에서도 V1 −3 dB 342 vs 341, +3 dB 25 vs 24, b\* 0 dB 162 vs 159로 다르다 | DECISIONS.md:153; `results/review_next/NEXT_EXPERIMENTS_P3.md:115` (§5.1-5), :139, :206 | `2026-09-23 23:35 ~ 23:46 KST (텍사스 09:35 ~ 09:46 CDT), 판정 23:58 KST` · f5856204 / 39e13126; `2026-09-24 00:12 ~ 01:02 KST (텍사스 09-23 10:12 ~ 11:02 CDT), 판정 01:05 KST` · d00bb877 / 2b599c14 |
| 11 | "한 프로세스 한 run이면 초기값이 torch 기본 seed로 재현된다" (N1, REVIEW_AUDIT:727) | 초기 가중치는 어떤 wrapper에서도 재현되지 않는다. 기존 모든 체크포인트의 초기값은 기록되지 않은 난수다. 사용자 결정은 "기록만"이며, A1 비교에는 "초기값 차이 포함"이라고 표기한다 | `results/review_next/REVIEW_AUDIT.md:731`, :733 | — |

행 1과 함께 기록된 검정이 하나 있다.
- 출처: EXP 행 `2026-09-23 07:14 ~ 13:39 (텍사스 09-22 17:14 ~ 23:39 CDT)` · 115d391f · `results/review_next/H0_best_vs_last_C2_m3.txt:24-25`
- 결과: **H0: best vs last (같은 run) C2 −3 dB 85 vs 85 실패, 불일치 6:6, p=1 → 기각 안 됨**
- 조건: n=640 개발 집합. 비교 대상 둘 다 같은 run이라 동일예산이다. MDD 8 @ n_d 12. 사전 등록 규칙은 `NEXT_EXPERIMENTS.md:36`이다.
- 이 run은 재학습본이고 헤드라인 파일 자체가 아니다.
- 참조 비교(판정 아님): 재학습 last 85 vs 기존 last-EMA 88, 8:11, p=0.648.
- 재학습 체크포인트 자체의 게이트 행: 출처 없음.

### 6.2 쓰면 안 되는 것: 목록 위치와 NOT QUOTABLE 행

| 목록 | 위치 | 비고 |
|---|---|---|
| Stage C가 철회한 문장 22개 | PAPER_MATERIALS.md:808-835 (§17.2) | 18:20 감사 |
| 미게이트 체크포인트 수치 (진단 탐침, arm 아님) | PAPER_MATERIALS.md:837-858 (§17.3) | NUMBERS_PACKAGE:700의 G-1.2 읽기로 "UN-GATED D2 checkpoint" |
| 철회 R1–R11 | NUMBERS_PACKAGE:567-581 (E5) | R10: n=640 D1 수치 대신 C5 88:91 p=0.88 POWERED, C2 56:42 p=0.19 UNDECIDED |
| DO NOT WRITE 1–59 | NUMBERS_PACKAGE:639-721 (F) | 5·44번에 정정 노트 (:650, :700) |
| 사전 등록 이탈 공개 | NUMBERS_PACKAGE:553-566 (E4) | V0 단독 1차를 V0→V1로 바꿈, V4 사후 등록, V4b 누락 후 추가(D1 미실행), §6f 예측 비맹검("WEAK predictions"), §6h는 읽기 전·실행 후 등록, TABLE C 미계산. G-1.2 노트 :558 |
| 출처 없음 / 존재하지 않음 | PAPER_MATERIALS.md:1035-1071 (§20) | V4b 예산 미해소, 동일예산 GMM "아직 존재하지 않는다", STATUS 요약 가드 수치, V4b D1 BLER 미실행, V2/V3 D2 BLER 없음, D2 참 prior 없음, `jac_spectrum.txt` D2 행 epoch 라벨, `bstar→V0` SNR@0.1 "n/a (-0.50 vs > 15)", V0 best val 두 기록 |

| NOT QUOTABLE 항목 | 사유 (출처 문자열) | 출처 |
|---|---|---|
| p = 2.2e-236 (R2-ours-G → R4-scvamp) | 어느 결과 파일에도 없다. "Write p < 1e-300" | NUMBERS_PACKAGE:727, :604, :715 |
| `jac_spectrum.txt:173` "D2 asym" 행, `:22` D2 N=1.6e5 행, `logs/jacpsd_N160000.log` 수치 | 예산 라벨이 없다. 임시 디렉토리 epoch-240 스냅샷이라 재현할 수 없다 | NUMBERS_PACKAGE:728-730 |
| GB′ report 0.5204 – 0.8297 | 점별 n 기록 없음 | :731 |
| "959 configurations" | `hpo_D1.txt:16`은 724. 959는 재구성할 수 없다 | :732 |
| "gate GD 0.27–0.32 is the gate this checkpoint family failed" | 1차 기록: GD 0.1499 PASS, GC 0.2241 FAIL | :733 |
| n=640 D1 확증 (C2 "7:8 p=1.0", C1 "92:72 p=0.14") | n ≥ 2560 규정에 미달 | :737 |
| `tables_D2_C.txt:41` V4b `N_train=10000` | 코드상 1.6e5 (X5) | :736 |
| Test M6 | 결과 없음 | :738 |
| "b* at N=1.6e5" (자체 결과로서) | `results/gmm_fit_D2_n16e4.txt` 요약 파일 없음, `.npz` 불완전 | :740 |
| V2 D2 a3 best val | DSM 검증손실 관측으로만 인용할 수 있다. 어떤 BLER 표에도 arm으로 없다. 종결값은 3.361999e-01 @1262다(학습 로그 `done` 행, NUMBERS_PACKAGE:432, STATUS:968). PAPER_MATERIALS:884·STATUS:652의 3.492148e-01 @285는 로그 epoch 285 행의 실행 중 값이며, 정정 줄은 없다 | PAPER_MATERIALS.md §17.5; `logs/train_V2_D2_N160000_a3.log` |

기록 상태 메모 (정정 노트 없음): PAPER_MATERIALS §17.4 (:869)와 §20.2 (:1046)는 여전히 동일예산 GMM이 "아직 존재하지 않는다"고 적고 있다. 후속 기록은 NUMBERS_PACKAGE:776-779 (P13, "PENDING 없음 (21:45)")과 DECISIONS.md:100 ("헤드라인 표는 확장 격자 B16e4k 로")이다. `tables_D2_C.txt`는 16× 비대칭이라 동일예산이 아니다(NUMBERS_PACKAGE (F)21, :671).

### 6.3 보고 전용·사후 선택 신호와 UNGATED 체크포인트 결과

| 신호 | 수치 (출처 그대로) | n · 집합 | testbed·셀·SNR | 게이트 | 동일예산 | 기록된 라벨 | 후속 기록 | 출처 (EXP 행 · 커밋 · 파일) |
|---|---|---|---|---|---|---|---|---|
| A1 3단계 C5 (aug vs ctrl) | 238/640 vs 260/640, a:b=16:38, p=0.00384, MDD 16 | 640 · 개발 skip [2560, 3200) | D2 C5 −3 dB | EXP 행 "D1 형제 게이트 PASS 후 평가" (aug 레시피) | 예 (둘 다 N_train 1.6e5). 초기값 차이 포함 (N1) | **보고 전용**. 판정점 C2 −3 dB는 84 vs 85, 9:10, p=1 → **판정 불가** | A1-C5에서 a1 쌍(같은 sha 40c55cb294340594 / e2b22673ac91ed8f)을 새 시행으로 돌린 결과: 528 vs 526/1280, 47:45, p=0.917 ("개발 신호 16:38 재현 안 됨"). H9(a2·a3) 517.5 vs 521.5, 70:71, p=1, MDD 25 → **판정 불가** → A1 닫음, 테스트 확증 없음 (DECISIONS.md:159) | `2026-09-23 08:40 ~ 14:23 (텍사스 09-22 18:40 ~ 00:23 CDT)` · 240394b9 · `results/review_next/A1s3_aug_vs_ctrl_C5_m3.txt:24-25`; `2026-09-24 07:15 ~ 07:25 KST (텍사스 09-23 17:15 ~ 17:25 CDT)` · 710a5a3f (identity 57709965) · `A1C5_rep_pair_a1_C5_m3.txt:26-27`, `A1C5_H9_C5_m3.txt:36-38` |
| P3 S-res (H8) | 판정점 V1 S-res 144 vs 기본/b05/fb05 R32 154/154/169: 2:12 p=0.0129 / 4:14 p=0.0309 / 5:30 p=2.24e-05 → 지지. b\* 273 vs 290/299/307: 3:20 p=0.000488 / 3:29 p=2.56e-06 / 7:41 p=6.24e-07 → 지지. §5.1 두 동률 해석(1차·literal)의 S-res 선택 차이는 0 블록 | 1280 · 판정 집합 3200..4479 | D2 C2 −3 dB | `d2sx_N160000_a1.pt` = D1 형제 게이트 PASS 레시피, last-EMA | 예 (N_train 1.6e5, b\* kron K=1024) | H8 **지지**. 다만 §3에 따라 확증 후보가 아니다(NEXT_EXPERIMENTS_P3.md:153). 사용자 결정: "S-res(H8 지지)는 별도 사전 등록을 하지 않는다 — 보고 전용 결과로만 기록" | 테스트 집합(n=2560, 보고 전용·확증 후보 아님): S-res V1 303 / 58 / 19, b\* 548 / 131 / 34 (−3/0/+3 dB). 비용은 실행 3개 | `2026-09-23 23:35 ~ 23:46 KST …` · f5856204 / 39e13126 · `results/review_next/p3_rules_C2_m3.txt:55-70`; DECISIONS.md:151 (2); `2026-09-24 00:12 ~ 01:02 KST …` · d00bb877 / 2b599c14 · `p3_confirm_C2.txt:17-19, :28-30` |
| P3 오라클 | V1 135, b\* 262 (판정점) | 1280 | D2 C2 −3 dB | 위와 같음 | 위와 같음 | "배치 불가 상한 참조, arm 아님"(참 비트 사용). 출처 문자열 그대로 | — | NEXT_EXPERIMENTS_P3.md:61, :136-137 |
| P3 보고 전용 점 | C5 −3 dB: H6a V1 0:21 p=9.5e-7, b\* 1:18 p=7.6e-5, H8은 모두 p < 1e-4 / < 1e-5. C2 +6 dB: 전부 UNDECIDED. 테스트 +6~+15 dB: 전부 UNDECIDED | 640 · 3200..3839 / 2560 · 테스트 | D2 C5 −3, C2 +6…+15 | 위와 같음 | 위와 같음 | 판정 아님 | — | NEXT_EXPERIMENTS_P3.md §7.2 (:170-179), `p3_confirm_C2.txt:20-23, :31-34` |
| A2 H5 (clip eta/mean) | V1-eta 88, V1-mean 88, 4:4 p=1 → **H5 기각**. gmmB-scorew-mean 134 vs -eta 124, 15:5 p=0.0414. 상호작용 9:19 p=0.0872 → 귀속 조건 불충족 | 640 · 개발 | D2 C2 −3 dB | 헤드라인 체크포인트 (D1 형제 게이트 PASS 레시피), last-EMA | N_train 1.6e5 (설정 열). arm별 예산은 출처 없음 | "§3.2 는 개발 집합 전용·보고 전용" (H5는 테스트 raw의 clip 통계에서 나온 가설) | — | `2026-09-23 09:30 ~ 09:52 (텍사스 09-22 19:30 ~ 19:52 CDT)` · d9085247 · `results/review_next/A2_interaction_C2_m3.txt`; NEXT_EXPERIMENTS.md:41 |
| A1 2단계 부차 | aug가 3쌍 중 2쌍에서 실패 적음, p<0.05는 0/3. 1차 15:19, p=0.608 → **판정 불가** (MDD 14) | 640 · 개발 | D2 C2 −3 dB | EXP 행 "D1 형제 게이트 PASS 확인 후" | N_train 1e4 (aug·ctrl) | 부차 = 보고 | — | `2026-09-23 11:12 ~ 11:14 (텍사스 09-22 21:12 ~ 21:14 CDT)` · 73e53af4 · `results/review_next/A1s2_group_C2_m3.txt` |
| F14b·F14c gap 최대점 | 절대차 −6 dB 0.791→0.601 (0.190), 비 +6 dB 0.0125→0.0039 (3.2×). 판정점 −3 dB는 1.74× | 2560 | D2 C2 | P8 게이트 열 "FAIL (N=1e4)". 6.1 행 3에 따라 "D1 형제 게이트 FAIL"로 읽는다 | 예 | "b·c 는 **사후 선택** (캡션 명시)". "−3 만 3점 POWERED". §6p 예측 1·2 빗나감 | — | DECISIONS.md:96; NUMBERS_PACKAGE:759 (P8); `2026-09-21 14:00 ~ 09-22 21:45` · 8fb27f5 · `figs/F14{a,b,c}_*.txt` |
| C6 (Nr=16) NR16run2 | bstar→V1 −3 dB 163:8 p=1.1e-38, pooled 266:13 p=1.6e-62 | 2560 | D2 C6 −3/+0/+3 | EXP 행 메모 "체크포인트 UNGATED(D1 형제 없음, §7 사전 등록)". 표 :45 "NO GATE RECORD". last-EMA@1688, best@1668 미저장 | 설정 `--ntrain 10000`. 표 머리(:37-38)는 학습 arm을 `N_train=1610000 rung=D2SXNR1610000`, GMM b\*를 10000으로 적는다. 동일예산 판정은 출처 없음 | POWERED (`tables_D2_NR16run2.txt:370-371`) | 첫 실행 NR16run은 arm 없이 끝났고 그 기록으로 보존됐다 (REVIEW_AUDIT S7-b :26) | `2026-09-23 05:28 ~ 08:17 (텍사스 09-22 15:28 ~ 18:17 CDT)` · 274cb6fe · `results/tables_D2_NR16run2.txt` |

"판정 불가"는 출처 파일의 문자열 "not decided by this design"(p ≥ 0.05)을 옮긴 것이다. "효과 없음"으로 바꿔 쓰지 않는다.


---

## 7. C6 (Nr=16) 동일예산 N′ = 1.6e5 (NEXT_EXPERIMENTS_C6B16e4 v2)

**EXPERIMENTS.md 행**: `2026-09-26 00:07 ~ 08:27 KST (텍사스 09-25 10:07 ~ 18:27 CDT)` (`run_nr16b_eval.sh`, 커밋 2a36737c). 지위: **UNGATED** (D1 형제 없음) → 기하·예산 축 측정이며 arm 판정이 아니다 (C6B16e4 §1). 출처: `conf/results/review_next/NEXT_EXPERIMENTS_C6B16e4.md` §6 (6.1~6.5), `conf/results/tables_D2_NR16B16e4.txt`, `conf/results/review_next/recovery_NR16B16e4.txt`.

### 7.1 측정 판정 (C6, 태그 NR16B16e4 = `_best`, §3d 사다리 시행 2 가중치)

| 표 B `b* → V1` | 판정점 | a:b (p) | pooled | 가드 | 라벨 |
|---|---|---|---|---|---|
| NR16B16e4 (판정) | −3 / +0 / +3 | 142:11 (3.5e-30) · 45:4 (8.2e-10) · 26:3 (1.5e-05) | 213:18 (p=1.8e-43) | POWERED, second arm fewer 3/3 | **(i) "C6 동일예산 우위가 N′ = 1.6e5 에서도 유지 (기하 축 측정, UNGATED)"** |
| NR16B16e4last (보고) | −3 / +0 / +3 | 142:10 · 41:4 · 25:3 | 208:17 | POWERED 3/3 | (보고 전용) |

- SNR@0.1 격차: `n/a (<= -3 vs <= -3)` (두 arm 모두 격자 최저 SNR 에서 이미 0.1 아래; 격자는 늘리지 않는다) (C6B16e4 §6.1).
- **회수율 대역** (`recovery_NR16B16e4.txt`, paired bootstrap B=2000 seed 20260926): −3 dB **R = 0.809 [90% 0.747, 0.870]** → 대역 **"기하 효과 대부분 유지"** (R ≥ 0.70). 0 dB 0.804 [0.694, 0.903], +3 dB 0.958 [0.750, 1.188], 3 점 합 0.823 [0.771, 0.871]. 나란히: C6 1e4 0.838 [0.781, 0.892], C2 1.6e5 헤드라인 0.470 [0.427, 0.512] (C6B16e4 §6.1). 대역 문장은 셀·예산 한정이며 arm 주장이 아니다.

| C6 −3 dB 실패 수 (n=2560) | b\* | V1 | genie | pooled (3점) | R(−3 dB) |
|---|---|---|---|---|---|
| 1e4 (NR16run2, last-EMA; b\* kron 128) | 207 | 52 | 22 | 266:13 | 0.838 |
| 1.6e5 last-EMA (NR16B16e4last; b\* kron 4096) | 184 | 52 | 22 | 208:17 | 0.815 [0.756, 0.872] |
| **1.6e5 `_best` (NR16B16e4, 판정 태그)** | 184 | 53 | 22 | 213:18 | 0.809 [0.747, 0.870] |

### 7.2 보고 전용
- BLER@16 −3 dB: V1 0.021, V4 0.025, V4b 0.030, b\* 0.072, bstar-scalar 0.081, genie 0.009. V4·V4b 도 b\* 를 3/3 에서 이긴다 (209:32, 195:35) (C6B16e4 §6.2).
- 대조군 `b* → b*-scalar`: 42:65 · 11:45 · 9:15, pooled 62:125, POWERED, first arm fewer 2/3 → significant (b\* 행렬 site 우세).
- V0: −3~+9 dB BLER 1.000, +12 0.979, +15 0.911; F3 가드는 V0 에서만 발동.
- best 대 last V1: 3 점 합 12:16 (p=0.57) → 판정하지 못함.
- 동일예산 GB′: 비 0.261~0.508, median 0.283, worst excess −0.492 (1e4: median 0.343).
- 수용 검사 **ACCEPT: OK -- NR16B16e4, NR16B16e4last** (genie 가 raw_NR16run2 와 7 SNR 전 시행 비트 동일; C6B16e4 §6, §6.4 기록 감사로 독립 재계산).

### 7.3 캐비엇 (등록 기록 그대로)
- 학습 §3d 시행 1 은 epoch 1064 에서 발산했고, 모든 1.6e5 C6 수치는 시행 2 (기울기 클리핑 1.0) 가중치다 (C6B16e4 §6.2).
- b\* = kron K=4096 은 격자 끝이고(K=8192 는 사용자 결정으로 미적합), K=4096 재시작 셋 모두 학습 우도 tol 규칙으로 정지했으며 검증 우도가 마지막 평가 시점에서 최고였다 — 덜 수렴된 GMM 일 수 있고 방향은 V1 유리 (C6B16e4 §6.5).
- §3 예측 채점: 발산 없음 **빗나감**, b\* 100~170 **빗나감** (184), GB′ median 0.35~0.55 **빗나감** (0.283), 회수율 0.65~0.80 **빗나감(근소, 더 높음)**; 나머지 적중 (C6B16e4 §6.3).

---

## 8. K1·K2: 생성 모형을 아는 참조(K1, 보고 전용)와 C1 격자 밖 질의 규칙(K2) (NEXT_EXPERIMENTS_K1K2 v2)

**EXPERIMENTS.md 행**: `2026-09-25 23:01 ~ 09-26 00:03 KST (텍사스 09-25 09:01 ~ 10:03 CDT)` (K1·K2 개발·판정 집합), `2026-09-25 (시작 타임스탬프 미기록; 첫 raw 파일 23:35:02 KST) ~ 23:41 KST` (K2 테스트 확증). 코드 a7398611. 출처: `conf/results/review_next/NEXT_EXPERIMENTS_K1K2.md` §5.1~§5.3, `K2_report.txt`, `K2test_report.txt`, `K1_report.txt`. 그림 **F18** (`conf/figs/F18_oog_rule_K2.*`), 표 `conf/figs/T_K2_oog_rule.tex`.

### 8.1 K2 테스트 확증 (C1 −3 dB, 테스트 0..2559, n=2560; 사용자 결정 DECISIONS 7552826a)

| arm | 실패 (BLER) | 격차 위치 | F3 가드 | 예외 |
|---|---|---|---|---|
| **V1-edge** (등록 1차 변형, 별도 arm) | **1770 (0.691)** | +0.075 | 0 | 0 |
| V1-clamp (2차 변형) | 1783 (0.696) | +0.068 | 0 | 0 |
| M-ours-bstar (kron K=1024) | 1906 (0.745) | 0 | 3 | 0 |
| M-ours-bstar-scalar | 2071 (0.809) | −0.091 | 0 | 0 |
| gmmB-scorew-eta | 2027 (0.792) | −0.067 | 0 | 0 |
| M-ours-dscore-C-V1 (동결) | 2515 (0.982) | −0.336 | 2560 | 314 |
| R5-genie | 95 (0.037) | 1 | — | 0 |

- **판정 `M-ours-bstar → V1-edge` 400:264, p = 1.5e-07 (a > b) → 확증 통과.** 기전 `V1 → V1-edge` 758:13 (p=8.1e-205). `V1-clamp ↔ V1-edge` 75:62 (p=0.31) → 판정하지 못함 (n_d 137, MDD 25, |Δ| 13) (K1K2 §5.1, §5.3 정정 1·4).
- 개발·판정 집합 1차 검정 (C1 −3 dB, 3200..4479, n=1280): `b* → V1-edge` 198:134, p = 0.00053 → 갈래 (i); Holm m=3 에서도 유지 (K1K2 §5.1).
- **범위(등록 그대로)**: 셀 C1 의 등록 판정(표 B, 3.2e5: GMM 우세 3/3, 판정점 +6/+9/+15 dB)과 헤드라인은 불변. V1-edge 는 별도 arm 으로만 싣는다 (K1K2 §5.1). 이 계열의 등록 1차 검정 수는 3 (K1K2 §5.1: Holm m=3) 이다.
- 보고 점(라벨 없음, n=640): C1 0 dB b\*→V1-edge 112:73 (0.0051), V1→V1-edge 27:26 (1); C5 −6 dB 86:12 (5.9e-15), 134:0 (9.2e-41) (K1K2 §5.1).

### 8.2 K1 (보고 전용; C2 −3 dB, 3200..4479, n=1280)

| arm | 실패 (BLER) | 격차 위치 |
|---|---|---|
| M-ours-dscore-C-V1 | 173 (0.135) | 0.528 |
| BR-S (생성 모형을 아는 q-측정 참조) | 167 (0.130) | 0.551 |
| M-ours-bstar | 307 (0.240) | 0 |
| LO-S-d0.001 (잠재를 아는 참조) | 80 (0.063) | 0.894 |
| R5-genie | 53 (0.041) | 1 |

- R1' `V1 → BR-S` 26:20, p = 0.46 → 갈래 (ii) **"V1→BR 격차를 판정하지 못함"** (n_d 46, MDD 16). R2' `BR-S → LO-S` 95:8, p = 5.1e-20 → 갈래 (i) "잠재 정보 몫이 유의하게 남음" (크기 87 블록). C5 −3 dB (n=640): R1' 26:25 (p=1) → (ii), R2' 170:4 → (i) (K1K2 §5.2).
- 해석 한계(등록 §1.2 그대로): R1'(ii) 는 "구분되지 않는다" 까지만 말한다. BR 은 완화 모형 + 유한 MCMC 다.

---

## 9. 파일럿 오버헤드: Tp ≥ Nt Pareto (NEXT_EXPERIMENTS_PARETO v2, 태그 PARB16e4)

**EXPERIMENTS.md 행**: `2026-09-27 00:42 ~ 01:58 KST (텍사스 09-26 10:42 ~ 11:58 CDT)` (`run_pareto_eval.sh`, 실행 커밋 2b03df55 = 동결 eee1d669 와 `conf/code` 동일). 헤드라인 가중치(`d2sx_N160000_a1.pt`, legacy-last, sha 4443921ce8d5c4a1)와 헤드라인 적합(b\* kron K=1024)을 그대로 쓰고 셀만 바꿨다. 출처: `conf/results/review_next/NEXT_EXPERIMENTS_PARETO.md` §6 (6.1~6.5), `frontier_PARB16e4.txt`, `conf/results/tables_D2_PARB16e4.txt`. 그림 **F19** (`conf/figs/F19_pilot_pareto.*`; 스크립트가 P-a·P-b 를 기록값과 assert).

### 9.1 (B) 셀 간 등록 비교 — 비짝 부트스트랩 (B=2000, rng 20260926), Holm m=2 α=0.10

| 비교 | SNR@0.1 (V1, C2 8 점) | SNR@0.1 (b\*, 셀) | Δ | 90% CI | 95% CI | 부트스트랩 p | 등록 라벨 |
|---|---|---|---|---|---|---|---|
| **P-a** (Holm 첫째) | −2.23 [−2.38, −2.07] | C7 (Tp=6) −1.83 [−2.00, −1.65] | **−0.40 dB** | [−0.64, −0.17] | [−0.67, −0.13] | 0.0040 | **"V1(Tp=4)의 SNR@0.1 이 b\*(Tp=6)보다 낮다 (등록 비교 P-a)"** |
| **P-b** (둘째) | −2.23 | C8 (Tp=8) −2.60 [−2.81, −2.42] | **+0.38 dB** | [+0.14, +0.63] | [+0.09, +0.69] | 0.0070 | **"b\*(Tp=8)의 SNR@0.1 이 V1(Tp=4)보다 낮다 (P-b, 반대 유의)"** |

censored 0% (PARETO §6.2). P-c (Eb/N0, 보고): Δ₆ − 0.918 = −1.32 dB, Δ₈ − 2.083 = −1.70 dB.

### 9.2 (A) 셀 안 판정 — 표 B `b* → V1`

| 셀 | 판정점 | a:b (p) | pooled | 라벨 | SNR@0.1 짝 격차 b\*−V1 |
|---|---|---|---|---|---|
| C7 (Tp=6) | −3 / +0 / +3 | 195:41 (3.3e-25) · 61:10 (4.6e-10) · 31:9 (6.8e-4) | 287:60 (1.2e-36) | **(i)**, POWERED 3/3 | +1.09 dB [90% +0.90, +1.28] |
| C8 (Tp=8) | −6 / −3 / +0 | 422:68 (2e-63) · 142:31 (3.5e-18) · 43:14 (1.5e-4) | 607:113 (1.4e-82) | **(i)**, POWERED 3/3 | +0.97 dB [+0.79, +1.14] |

대조군 `b* → b*-scalar`: C7 pooled 87:101, 유의 방향 없음; C8 pooled 102:146, b\* 가 b\*-scalar 보다 적게 실패 2/3. 회수율(보고): C7 −3 dB 0.477 [0.417, 0.531], C8 0.519 [0.445, 0.587] (PARETO §6.1).

### 9.3 보고 전용
- **SNR@0.1 frontier (dB)**, 열 = Tp/T 0.25 (C2) / 0.375 (C7) / 0.50 (C8): R2 +0.06 / −0.89 / −1.59; b\* −0.81 / −1.83 / −2.60; **V1 −2.23 / −2.92 / −3.57**; genie −4.81 / −4.84 / −5.26 (C2 genie 는 −6 dB 점을 더한 8 점 곡선에서) (PARETO §6.3; F19 `.txt` 와 같음).
- goodput 포락선 K(1−BLER@16)/T: −3 dB 이상은 두 arm 모두 C2 가 포락선; −6 dB 에서 V1 은 C7 (1.150), b\* 는 C8 (0.836); −9 dB 는 C8 (PARETO §6.3).
- C2 −6 dB (1.6e5, 새 관측): V1 0.599, b\* 0.773, R2 0.840, genie 0.203 (1e4 실행과 genie 비트 동일).
- 수용 검사: **ACCEPT: OK -- PARB16e4**, 사전 수신기 회귀 검사 **ACCEPT: OK -- PARB16e4chk** (C2 −3 dB 청크 0 에서 14 arm 이 raw_B16e4k 와 비트 동일) (PARETO §6).

### 9.4 캐비엇 (등록 기록 그대로)
- 헤드라인 가중치는 legacy last-EMA (best 가중치 미저장); b\* kron 1024 는 격자 끝 (K=2048 미적합, 사용자 결정으로 헤드라인 불변).
- C2 −6 dB 시행은 1e4 arm 으로 이미 관측된 시행이다. 셀 간 비교는 짝이 없다. Tp>Nt 에서 측정된 게이트는 없다 — (A) 는 셀 한정 arm 결과로만 쓴다 (PARETO §1).
- +15 dB 의 C8 V1 0/2560 은 반복 ≥ 2 질의의 67–69% 가 학습 σ 범위 아래로 외삽하는 점이다(Gaussian 궤적 기준).
- §3 예측 채점: P-a "0 포함" **빗나감**(V1 쪽 유의), P-b 반대 유의 **적중**, Holm 첫째 = P-b **빗나감**, V1 교차점 이동 범위 **빗나감**(C7 −2.92, C8 −3.57 가 예측보다 작은 이동), genie 범위 **빗나감** (PARETO §6.4).

---

## 10. 채널 모델 확장: D3 · SV8e · 3GPP 38.901 (UMi28 주 + MIX3 부속)

**EXPERIMENTS.md 행**: D3 `2026-09-27 01:58 ~ 03:10 KST (텍사스 09-26 11:58 ~ 13:10 CDT)`; SV8e `2026-09-27 03:10 ~ 03:59 KST (텍사스 09-26 13:10 ~ 13:59 CDT)`; UMi28 `2026-09-27 06:37 ~ 08:48 KST (텍사스 09-26 16:37 ~ 18:48 CDT)`; MIX3 `2026-09-27 06:18 ~ 08:44 KST (텍사스 09-26 16:18 ~ 18:44 CDT; 16:37 재개)`. 등록 동결 eee1d669, 기록 감사 5819db19. 셀은 모두 C2 (8×4, T=16, Tp=4), 동일예산 1.6e5, 테스트 0..2559. 지위: 세 testbed 의 체크포인트는 모두 **UNGATED** (측정, arm 판정 아님); 헤드라인 불변; D2 와 짝 없음. 출처: `conf/results/review_next/NEXT_EXPERIMENTS_{D3B16e4,SVB16e4,38901}.md` §6, `recovery_diff_<TAG>.txt`. 그림 **F20** (`conf/figs/F20_channel_models.*`; 스크립트가 격차·회수율을 기록값과 assert).

### 10.1 표 B `b* → V1` (판정 태그 = `_best`) 와 SNR@0.1 격차

| testbed (태그) | 판정점 | a:b | pooled | 등록 라벨 | SNR@0.1 짝 격차 b\*−V1 (90%) |
|---|---|---|---|---|---|
| D2 헤드라인 (B16e4k, 문맥) | −3 / 0 / +3 | 302:50 · 117:21 · 35:7 | 454:78 | (i) 3/3 (D1 형제 게이트 PASS) | +1.41 [+1.22, +1.64] |
| **D3** = D2 기하 + CN 경로 이득 (D3B16e4) | +0 / +3 / +6 | 221:39 · 116:19 · 56:9 | 393:67 (3.6e-57) | **(i) "D3 (조건부 Gaussian 경로 이득) 에서도 V1 이 b\* 보다 적게 실패 (prior·기전 축 측정, UNGATED)"** | +1.41 [+1.19, +1.67] |
| **38.901 UMi 28 GHz** (U28B16e4, 주 실험) | +3 / +6 / +9 | 76:38 · 50:22 · 35:13 | 161:73 (8.7e-9) | **(i) "38.901 UMi 28 GHz 에서 V1 이 b\* 보다 적게 실패 (prior·기전 축 측정, UNGATED; §3 예측 빗나감)"** | +0.60 [+0.33, +0.87] |
| 38.901 MIX3 (MXB16e4, 보고 전용 부속) | +3 / +6 / +9 | 85:39 · 71:21 · 42:11 | 198:71 | (i) 문자열, 보고 전용 | +0.98 [+0.68, +1.31] |
| SV8e 군집 Saleh–Valenzuela (SVB16e4) | −3 / +0 (2 점) | 124:62 · 24:10 | 148:72 | **(iv) "판정하지 못함 (검정력 미달)"** (+3 dB b\* BLER 0.003 < 0.005; 격자 확장 없음) | +0.25 [+0.16, +0.33] |

- last 태그(보고): D3 400:70, UMi28 160:71, MIX3 198:80 (모두 POWERED 3/3), SV8e 151:68 (UNDECIDED).
- 대조군 `b* → b*-scalar`: D3·UMi28·MIX3 유의 방향 없음, SV8e UNDECIDED. `R2 → b*`: 네 testbed 모두 b\* 우세 3/3.
- SNR@0.1 (dB; best) — D3: b\* 2.61, V1 1.20, genie −1.38; UMi28: b\* 5.73, V1 5.13, genie 0.59; MIX3: b\* 5.72, V1 4.74, genie 1.10; SV8e: b\* −2.13, V1 −2.38, genie ≤ −3.
- BLER@16 −3 dB (best): D3 b\* 0.507 / V1 0.391 / genie 0.189; UMi28 0.496 / 0.480 / 0.232; MIX3 0.555 / 0.529 / 0.265; SV8e 0.181 / 0.157 / 0.012.
- 수용 검사: 네 prior 모두 **ACCEPT: OK** (best·last 두 태그); 비-Stage-C 10 arm 은 두 태그 간 비트 동일 (각 §6).

### 10.2 회수율 R 과 D2 와의 비짝 차이 ΔR (1차 = −3 dB, 등록 라벨은 1차에서만)

| testbed | R(−3 dB) [90% paired] | ΔR = R − R_D2(0.470) [90% 비짝] | 등록 라벨 | 2차(판정점 합, 보고) |
|---|---|---|---|---|
| D3 | 0.367 [0.335, 0.399] | −0.104 [−0.156, −0.049] | "D3 의 회수율이 D2 보다 낮다" | −0.038 [−0.089, +0.016] |
| UMi28 | 0.062 [0.033, 0.089] | −0.408 [−0.458, −0.358] | "38.901 에서 회수율이 D2 보다 낮다" | −0.358 [−0.411, −0.305] |
| SV8e | 0.143 [0.095, 0.188] | −0.327 [−0.392, −0.262] | "SV8e 의 genie 격차 회수율이 D2 보다 낮다" | −0.354 [−0.413, −0.295] |
| MIX3 (보고) | 0.090 [0.062, 0.117] | −0.380 [−0.430, −0.328] | (보고 전용) | −0.281 [−0.335, −0.224] |

포화 가드는 네 prior 모두 미발동 (−3 dB b\* BLER 0.507 / 0.496 / 0.181 / 0.555 ∈ [0.005, 0.9]; b\* 실패 > genie 실패), undefined 복제 0 (각 §6).

### 10.3 판독표·공동 판독·예측 채점 (등록 문자열 그대로)
- D3 판독표 칸: (i) & Δ < 0 → "우위는 남되 회수율은 낮다: 조건부 비-Gaussian 성이 우위의 일부에 기여했을 수 있다(단정 아님)" [E2 적중 · E1 빗나감]; 교란 요인(페이딩 깊이 sd 0.57 vs 0.16, 판정점 이동, 짝 없음, b\* 격자 끝·수렴 캐비엇) 병기 (D3B16e4 §6.2).
- **경계 양쪽 공동 판독 (38901 §2.3)**: SV8e = (iv) × UMi28 = (i) → **"판정하지 못함"** (38901 §6.5).
- 38.901 §3 예측 1 "(ii) 또는 (iii) — 학습 prior 우위 없음" → **"예측 빗나감(38.901 에서도 V1 우위)"**; 빗나갈 경로 (a) 발동 — 기전 가설(잠재 차원) 수정 필요, 사후 설명은 사용자 (38901 §6.4).
- SV8e 예측 1 (i) → 결과 (iv) → 채점 없음 (SVB16e4 §6.4).

### 10.4 캐비엇 (등록 기록 그대로)
- 세 testbed 모두 UNGATED, 확산 시드 하나 (시드 반복은 §10.5).
- b\*: D3·UMi28·MIX3 은 kron K=4096 격자 끝(4096 에서 멈춤, 사용자 결정) + 수렴 캐비엇(학습 우도 tol 규칙 정지); SV8e 는 full K=256 격자 내부.
- 동일예산 GB′ (보고): D3 median 0.559, SV8e 0.918, UMi28 0.920 (σ = 0.595 한 점만 비 2.37), MIX3 0.894.
- 운영: 38.901 첫 실행(14:16 CDT)은 GPU 가 보이는 셸에서 워커 하나가 GPU 0 을 독점해 Sionna 채널 생성이 막혀 청크 0 개로 정체 → 15:21 CDT 중지(raw 0 개), GPU 숨김(`CUDA_VISIBLE_DEVICES=`)으로 재실행; MIX3·UMi28 은 사용자 결정으로 병렬 실행 (DECISIONS 80bae849·344d084c; 38901 §6).
- SV8e 선택 경위와 `01_RULES.md:77` 충돌, 0단계 예측 1 일관성 검사 미채택·미실행 (SVB16e4 §0, §1).

- σ 격자 측정 공개(네 prior 모두): 각 prior 자체 σ 격자를 헤드라인과 같은 절차로 재면서 테스트 시행 0..63 (C1·C2) 이 Gaussian 수신기로 한 번 실행됐다(ν_q 만 기록, BLER 없음) — 각 등록 §0/§1.
- 38.901 주 실험 전환 경위: MIX3 학습이 09-26 09:37 CDT 에 시작된 뒤 사용자가 10:07 CDT 에 UMi28 단일을 주 실험으로 바꿨다(MIX3 는 보고 전용 부속 점); 어느 쪽도 BLER 관측 전 (DECISIONS [2026-09-27 00:07 KST], 38901 머리말).
- 운영 기록(수치 영향 없음): 38.901 병렬 전환 중 MIX3 runner 가 한 번 종료돼 완료 청크 192 개부터 재개했다 (DECISIONS 344d084c, 38901 §6).

### 10.5 시드 강건성 (동일예산 1.6e5)
- 등록 `conf/results/review_next/NEXT_EXPERIMENTS_SEEDS16e4.md` (동결 5d9a9a1a), 결과 §6.1 (D2) · §6.2 (UMi28). 규칙: a1 이 보고용 arm, BLER 을 본 뒤 시드를 고르지 않는다. 표 B `b* → V1`, BLER@16, n = 2560, 테스트 시행 0..2559.

| prior · 시드 | 체크포인트 (sha256[:16]) | 표 B 판정점 a:b | pooled | 라벨 | SNR@0.1 격차 b\*−V1 (90%) | V1 −3 dB BLER | 출처 (EXPERIMENTS 행) |
|---|---|---|---|---|---|---|---|
| D2 C2 a1 (헤드라인) | 4443921ce8d5c4a1 | −3/0/+3: 302:50 · 117:21 · 35:7 | 454:78 | (i) | +1.41 [+1.22, +1.64] | 0.145 | `2026-09-21 14:00 ~ 09-22 21:45` |
| D2 C2 a2 | 9465fbec56cbf834 | 303:47 · 117:20 · 34:8 | 454:75 | (i) | +1.44 [+1.24, +1.67] | 0.143 | `2026-09-27 10:55 ~ 11:54 KST` |
| D2 C2 a3 | b3d3376ce0796540 | 304:56 · 125:16 · 32:5 | 461:77 | (i) | +1.48 [+1.28, +1.71] | 0.146 | 같은 행 |
| UMi28 a1 | 6f3a1b9490864af1 | +3/+6/+9: 76:38 · 50:22 · 35:13 | 161:73 | (i) | +0.60 [+0.33, +0.87] | 0.480 | `2026-09-27 06:37 ~ 08:48 KST` |
| UMi28 a2 | 0ec0973b7892d0c2 | 77:39 · 54:17 · 32:12 | 163:68 | (i) | +0.74 [+0.46, +1.03] | 0.480 | `2026-09-27 12:39 ~ 14:28 KST` |
| UMi28 a3 | cc48b203ab114b92 | 81:35 · 55:20 · 36:13 | 172:68 | (i) | +0.74 [+0.46, +1.03] | 0.487 | 같은 행 |

- 등록 라벨: D2 **"시드 강건 (3/3 (i))"**, UMi28 **"시드 강건 (3/3 (i))"**. UMi28 a2·a3 격차는 네 자리로 +0.7364 / +0.7389 (두 자리 일치는 반올림).
- b\* 와 genie 는 시드와 무관하게 같은 값이다(같은 적합·시행): D2 −3 dB 623 / 87, UMi28 −3 dB 1270 / 594 실패.

---

### 10.6 파일럿 전용 학습 prior 와 GMM (Arvinte–Tamir 형 설정; NEXT_EXPERIMENTS_PILOT16e4 v2)
- 등록 `conf/results/review_next/NEXT_EXPERIMENTS_PILOT16e4.md` (동결 92d26757), 결과 §6.1, 감사 정정 문단(10393e2b). 출처: EXPERIMENTS 행 `2026-09-27 12:29 ~ 13:07 KST`. 같은 V1 가중치·GMM 적합·테스트 시행으로, prior 를 파일럿에 **한 번** 적용하고 채널 추정을 고정한 arm(V1-pilot, bstar-pilot)을 루프 arm 과 짝지었다. 원 방법(annealed Langevin)의 재현이 아니다. 표 B, BLER@16, n = 2560.

| 데이터셋 | P1 `V1-pilot → V1 루프` 라벨 · 격차 (90%) | P2 `bstar-pilot → V1-pilot` 라벨 · 격차 (90%) | 보고 `V1-pilot → b* 루프` 라벨 · 격차 |
|---|---|---|---|
| D2 C2 (주) | (i) 2/3 · +0.92 [+0.77, +1.07] | (i) 3/3 · +1.07 [+0.90, +1.25] | (ii) · −0.50 [−0.69, −0.32] |
| D2 C6 | (iv) 판정하지 못함 (검정력 미달) · n/a | (i) 3/3 · n/a | (iv) · n/a |
| D3 | (i) 3/3 · +0.83 [+0.67, +1.01] | (i) 3/3 · +1.28 [+0.99, +1.53] | (ii) · −0.58 [−0.82, −0.36] |
| SV8e | (iv) 판정하지 못함 (검정력 미달) · +1.04 [+0.92, +1.17] | (i) 2/3 · +0.17 [+0.08, +0.25] | (iv) · +0.79 [+0.67, +0.92] |
| UMi28 | (i) 2/3 · +0.37 [+0.18, +0.57] | (i) 3/3 · +0.63 [+0.33, +0.86] | (iii) · −0.22 [−0.49, +0.06] |
| MIX3 | (i) 2/3 · +0.57 [+0.40, +0.77] | (i) 3/3 · +0.88 [+0.58, +1.12] | (ii) · −0.41 [−0.71, −0.12] |

- 격차 = SNR@0.1(첫째) − SNR@0.1(둘째). P1 (i) = "루프 V1 이 파일럿 전용 V1 보다 적게 실패", P2 (i) = "파일럿 전용에서 V1 이 b\* 보다 적게 실패", 보고 (ii) = "파일럿 전용 V1 이 루프 b\* 보다 적게 실패". 측정 라벨 개수: P1 6 중 4 (i), P2 6 중 6 (i).
- 등록 캐비엇: P1 은 Module H 16 회 대 1 회라 데이터 보조 재추정의 몫과 반복 정련의 몫을 가르지 못한다. 그림 F22.

### 10.7 학습/평가 채널 모델 불일치 (NEXT_EXPERIMENTS_MISMATCH16e4 v2)
- 등록 `conf/results/review_next/NEXT_EXPERIMENTS_MISMATCH16e4.md` (동결 92e31706, 코드 7c6ebcda), 결과 §6.1, 감사 정정 문단(10393e2b). 출처: EXPERIMENTS 행 `2026-09-27 13:18 ~ 15:46 KST`. 학습 prior 의 체크포인트·GMM 적합·표본 공분산을 평가 prior 의 테스트 시행에 적용; 정합 arm 은 평가 prior 의 base raw. C2, BLER@16, n = 2560. 측정 라벨(1차 검정 없음).

| 학습 → 평가 | MM `bstar-mis → V1-mis` 라벨 · 격차 (90%) | 정합 격차 b\*−V1 | V1 불일치 비용 | b\* 불일치 비용 | 보고 `b*(정합) → V1-mis` |
|---|---|---|---|---|---|
| D2 → D3 | (i) 3/3 · +1.33 [+1.11, +1.61] | +1.41 | +0.25 [+0.13, +0.38] | +0.17 [−0.04, +0.40] | (i) +1.16 |
| D3 → D2 | (i) 3/3 · +1.18 [+1.00, +1.39] | +1.41 | +0.06 [−0.04, +0.16] | −0.17 [−0.32, −0.02] | (i) +1.35 |
| UMi28 → MIX3 | (i) 2/3 · +0.61 [+0.33, +0.92] | +0.98 | +0.28 [+0.12, +0.46] | −0.09 [−0.35, +0.19] | (i) +0.70 |
| MIX3 → UMi28 | (i) 3/3 · +1.04 [+0.73, +1.30] | +0.60 | −0.05 [−0.22, +0.10] | +0.40 [+0.12, +0.63] | (i) +0.65 |
| D2 → UMi28 | (i) 2/3 · +0.35 [+0.12, +0.61] | +0.60 | +1.51 [+1.19, +1.81] | +1.26 [+0.90, +1.61] | (ii) −0.92 |
| UMi28 → D2 | (i) 3/3 · +0.82 [+0.66, +0.99] | +1.41 | +0.93 [+0.76, +1.12] | +0.33 [+0.16, +0.50] | (i) +0.49 |
| D2 → SV8e | (iv) 판정하지 못함 (검정력 미달) · −0.11 [−0.23, +0.01] | +0.25 | +0.64 [+0.53, +0.77] | +0.28 [+0.19, +0.39] | (iv) −0.40 |
| SV8e → D2 | (i) 3/3 · +1.00 [+0.82, +1.19] | +1.41 | +0.85 [+0.68, +1.04] | +0.43 [+0.25, +0.61] | (i) +0.57 |

- MM (i) = "학습 P_tr → 평가 P_te 불일치 아래 V1 이 b\* 보다 적게 실패"; 집계: 8 조합 중 7 에서 (i). 불일치 비용 = SNR@0.1(불일치) − SNR@0.1(정합). 보고 `b*(정합) → V1-mis` 의 (ii) = "정합 b\* 가 불일치 V1 보다 적게 실패". 불일치는 prior 쪽뿐(파일럿·σ²·수신기는 평가 prior 의 것). 그림 F23.

---

## 11. 그림 목록 (학회 원고용, F16~F32; 사본 `conf/conference_plot/`)

| 그림 | 내용 | 스크립트 | 원자료 |
|---|---|---|---|
| F16 `conf/figs/F16_headline_budget.*` | (a) D2 C2 헤드라인 1.6e5 BLER@16 곡선 (R2, b\*, V1, genie), (b) C2 −3 dB BLER vs 동일예산 N_train | `conf/code/figure_f16.py` | raw_B16e4k 및 예산 태그 raw_{B1e4, B4e4k, B32e4, B32e4last} |
| F17 `conf/figs/F17_codim_C6.*` | 여차원: (a) C2 / (b) C6 1.6e5 BLER 곡선, (c) 회수율 R vs 예산 | `conf/code/figure_f17.py` | raw_B16e4k, raw_NR16B16e4{,last}, raw_NR16run2 등 |
| F18 `conf/figs/F18_oog_rule_K2.*` + `T_K2_oog_rule.tex` | K2 격자 밖 규칙: C1 −3 dB 테스트 BLER(속 빈 점 = 개발 시행), 반복별 BLER, 격자 밖 질의 비율, 보고 점; 비용(`oog_cost.txt`) | `conf/code/figure_f18.py`, `conf/code/bench_oog.py` | raw_review_next_K2test, raw_review_next_K2 |
| F19 `conf/figs/F19_pilot_pareto.*` | 파일럿 오버헤드: (a) V1(Tp=4) vs b\*(Tp=4/6/8) BLER, (b) SNR@0.1 vs Tp/T, P-a·P-b | `conf/code/figure_f19.py` | raw_B16e4k + raw_PARB16e4 |
| F20 `conf/figs/F20_channel_models.*` | 채널 모델별: (a) SNR@0.1 격차 b\*−V1, (b) UMi28 BLER 곡선, (c) 회수율 R | `conf/code/figure_f20.py` | raw_{B16e4k, D3B16e4, SVB16e4, U28B16e4, MXB16e4} |
| F21 `conf/figs/F21_all_baselines.*` | 6 데이터셋 × 핵심 기준선(BiG-AMP R3, turbo R1, Gaussian R2, GMM b\*) + V1 + genie, BLER vs SNR (나머지 arm 은 .txt) | `conf/code/figure_f21.py` | raw_{B16e4k, NR16B16e4, D3B16e4, SVB16e4, U28B16e4, MXB16e4} |
| F22 `conf/figs/F22_pilot_only.*` | 파일럿 전용 R0·b\*·V1 대 루프 b\*·V1 + genie, 6 데이터셋 BLER vs SNR (§10.6) | `conf/code/figure_f22.py` | 위 base raw + raw_PIL{B16e4k, NR16, D3, SV, U28, MX} |
| F23 `conf/figs/F23_mismatch.*` | 불일치 8 쌍: (a) 같은 불일치 아래 b\*−V1 격차 + 정합 격차, (b) V1·b\* 불일치 비용 (§10.7) | `conf/code/figure_f23.py` | raw_MM* + 평가 prior base raw |
| F24 `conf/figs/F24_nonstationary_D2C2.*` | D2 C2 도플러 ν 0.005/0.01 · 회전 15°/30° — 등록 baseline(ALD plug-in·V1-pilot 포함) 곡선 (§13, §15) | `conf/code/figure_f24.py` | raw_{DOP,ROT}{a,b}B16e4k + raw_X{L,P,A}… |
| F25 `conf/figs/F25_nonstationary_all.*` | 24 조건 −3 dB BLER: V1 · 가장 가까운 baseline X\* · genie (§15) | `conf/code/figure_f24.py` | SUPP16e4 raw |
| F26 `conf/figs/F26_drift_spatial.*` | 표류 학습 prior B′ (15°/30°) · 공간 비정상 S2v C6 곡선 (§14) | `conf/code/figure_f24.py` | raw_RMX{15,30}{,PIL,ALD}, raw_S2v{B16e4,PIL,ALD} |
| F27 `conf/figs/F27_nonstationary_gap_recovery.*` | 6 데이터셋 × {정적, 도플러 2, 회전 2}: SNR@0.1 격차 · 회수율 R (90% CI; 기록 파일 전사) (§10, §13) | `conf/code/figure_f27.py` | F20·F17 .txt, pairB_X*.txt |
| F28 `conf/figs/F28_nonstationary_C6.*` | D2 C6 도플러·회전 곡선 (§13, §15) | `conf/code/figure_f27.py` | raw_{DOP,ROT}{a,b}NR16 + raw_X… |
| F29 `conf/figs/F29_label_grid.*` | SUPP16e4 라벨 격자 24 × 13 (§15) | `conf/code/figure_f27.py` | pairB_X*.txt |
| F30 `conf/figs/F30_scale_trend.*` | 배열 규모 Nr 8/16/32 (C2/C6/C9): (a)(b) D2·UMi28 판정점 회수율 R_dp vs Nr (90% paired CI; 셀별 등록 CI = 그 셀을 등록한 frontier 파일 줄), 1차 ΔR·한정어·단계 라벨 주석 (그림은 영문 풀이, 등록 원문은 .txt); (c)(d) C9 두 셀 BLER@16 (b\*·V1·R2·genie, 95% Wilson) (§21; 등록 NEXT_EXPERIMENTS_SCALE16e4 v3) | `conf/code/figure_f30.py` | scale2_primary_*·scale2_step_*·recovery_*.txt + pairB_<T>.txt (R2) + raw_{B16e4k, NR16B16e4, U28B16e4} 및 scale 워크트리 raw_{NR32B16e4, U28NR16B16e4, U28NR32B16e4} (미추적) |
| F31 `conf/figs/F31_sparse_baselines.*` | 희소 baseline 3 개 (SBL-loop, SBL-pilot, OMP-pilot): (a) 6 데이터셋 판정점 R_X (90% CI; b\* 는 STATIC16e4 인용 병기, (iv) 표기, 나머지 (i)); (b) D2 C2 BLER@16 곡선 (V1·b\*·희소 3·genie) (§20; 등록 NEXT_EXPERIMENTS_SPARSE16e4 v2) | `conf/code/figure_f31.py` | pairB_SP*.txt + raw_SP{B16e4k, D3, SV, U28, MX, NR16} + base raw |
| F32 `conf/figs/F32_hisnr_highsnr.*` | 고SNR 보강 +6..+15 dB: 새 시행 n = 20480 BLER (95% Wilson) 과 원 태그 n = 2560 을 나란히 (합치지 않음), D2 C2·C6, V1·b\*·R2·genie (R1·R3 는 .txt 만; genie C6 +15 dB n = 2560 의 실패 0 점은 로그축에서 생략); 보고 전용, 등록 곡선 대체 아님 (§19; 등록 NEXT_EXPERIMENTS_HISNR16e4 v2) | `conf/code/figure_f32.py` | raw_HS{B16e4k, NR16} + raw_{B16e4k, NR16B16e4}; hisnr_HS*.txt; 원 태그 R2 실패 수 = pairB_SP{B16e4k, NR16}.txt |

각 그림의 `.txt` 에 수치 전부와 캡션용 캐비엇이 있다.

## 12. ALD: Arvinte–Tamir 형 annealed Langevin 파일럿 추정 (NEXT_EXPERIMENTS_ALD16e4 v2)

**EXPERIMENTS.md 행**: `2026-09-28 00:43 ~ 00:54 KST (텍사스 09-27 10:43 ~ 10:54 CDT)`. 같은 V1 가중치로 ALD 파일럿 추정을 GPU 에서 미리 계산하고(§9.3 GPU 예외, 추정기만) 수신기는 CPU. 원 방법(저자 네트워크)의 재현이 아니다. 표 B, BLER@16, n = 2560, 테스트 시행. 출처 `NEXT_EXPERIMENTS_ALD16e4.md` §6.1, 기록 감사 5b5c8f4a.

| 데이터셋 | A1 `ALDv-pilot → V1 루프` 라벨 · 격차 (90%) | A2 `ALD-pilot → V1 루프` | A3 `ALDv-pilot → V1-pilot` |
|---|---|---|---|
| **D2 C2 (주)** | **(i)** 3/3 · +1.54 [+1.37, +1.74] | **(i)** 3/3 · +1.82 [+1.62, +2.05] | (i) 3/3 · +0.62 [+0.49, +0.75] |
| D2 C6 | (i) 3/3 · n/a (≤ −3 dB) | (i) 3/3 · n/a | (i) 3/3 · n/a |
| D3 | (i) 3/3 · +1.31 [+1.10, +1.56] | (i) 3/3 · +1.52 [+1.29, +1.81] | (i) 3/3 · +0.48 [+0.32, +0.66] |
| SV8e | (i) 3/3 · +1.08 [+0.96, +1.22] | (i) 3/3 · +1.27 [+1.13, +1.41] | (iii) · +0.05 [−0.04, +0.13] |
| UMi28 | (i) 3/3 · +0.80 [+0.53, +1.02] | (i) 3/3 · +0.76 [+0.50, +1.00] | (i) 2/3 · +0.42 [+0.21, +0.60] |
| MIX3 | (i) 2/3 · +1.04 [+0.80, +1.32] | (i) 3/3 · +1.38 [+1.08, +1.66] | (i) 2/3 · +0.47 [+0.26, +0.68] |

- 주 라벨 문장(등록): "루프 V1 이 ALD 파일럿 추정(오차 인지·plug-in 모두)보다 적게 실패". 격차 = SNR@0.1(첫째) − SNR@0.1(V1 쪽). ALD-pilot = plug-in (v = 1e-8), ALDv-pilot = 오차 인지 (`arms.py`).


## 13. 비정상 조건 A·B: 블록 안 도플러 (DOP16e4) · 수신 배열 회전 (ROT16e4)

**EXPERIMENTS.md 행**: DOP `2026-09-28 01:26 ~ 08:32 KST (텍사스 09-27 11:26 ~ 18:32 CDT)`; ROT `2026-09-28 08:35 ~ 16:07 KST (텍사스 09-27 18:35 ~ 09-28 02:07 CDT; …)`. 정적/0° 학습 prior 를 비정상 시행에 그대로 적용. 표 B `b* → V1`, n = 2560, 테스트 시행. 출처 각 등록 §6.1 (그리고 SUPP16e4 §0 전사), 감사 5b5c8f4a.

| 데이터셋 | DOP ν = 0.005 | DOP ν = 0.01 | ROT 15° | ROT 30° |
|---|---|---|---|---|
| D2 C2 | (i) 540:103 | (iii) 288:188 | (i) 448:80 | (i) 529:124 |
| D2 C6 | (i) 258:25 | (iii) 320:190 | (i) 282:20 | (i) 518:18 |
| D3 | (i) 446:77 | (i) 299:151 | (i) 417:90 | (i) 445:85 |
| SV8e | (iv) 152:73 | (i) 274:149 | (iv) 154:68 | (i) 179:83 |
| UMi28 | (i) 161:74 | (iii) 192:147 | (i) 184:59 | (i) 245:74 |
| MIX3 | (i) 233:90 | (i) 261:164 | (i) 204:67 | (i) 196:57 |

- 주 라벨 (D2 C2): DOP ν = 0.005 (i), ν = 0.01 (iii) — 등록 문장 "ν = 0.005 에서 V1 이 적게 실패; ν = 0.01 에서는 판정하지 못함 (유의 방향 없음)"; ROT 15°·30° (i) — "수신 배열 회전 15°·30° 모두에서 V1 이 b* 보다 적게 실패". 측정 라벨 (i) 수: ν = 0.005 5/6, ν = 0.01 3/6, 15° 5/6, 30° 6/6. 그림 F24 (D2 C2 곡선), F25, F27, F28 (C6 곡선).


## 14. 비정상 조건 B′·C: 표류 학습 prior (ROTMIX16e4) · 공간 비정상 S2v (S2V16e4)

**EXPERIMENTS.md 행**: B′ `2026-09-28 16:08 ~ 18:34 KST (텍사스 09-28 02:08 ~ 04:34 CDT; …)`; C `2026-09-28 18:34 KST ~ 09-29 03:48 KST (텍사스 09-28 04:34 ~ 13:48 CDT; …)`. UNGATED 측정. 출처 각 등록 §6.1, 감사 5b5c8f4a.

| 실험 | 판정 | 기록 |
|---|---|---|
| B′ (S2d = 0°–30° 표류로 학습한 prior, D2 C2) | 판정 1 RB `b* → V1` | 15° (i) 406:81, 30° (i) 450:122 — "표류(0°~30°)로 학습한 prior 끼리 비교하면, 회전 15°·30° 모두에서 V1 이 b* 보다 적게 실패" |
| | DT (표류 학습 vs 정적 학습, 같은 arm) | DT-V1: 30° (i), 0°·15° (iii); DT-b\*: 30° (i), 0°·15° (iii) |
| | DD (차이의 차이) | DD-15 +0.001, DD-30 +0.029 — 판정하지 못함 (CI 0 포함) |
| | 판정 3 (등록 baseline 13 개) | 세 각도 모두 13/13 (i) |
| C (S2v 가시 창, D2 C6) | 판정 1 `b* → V1` | (i) 202:32 — "공간 비정상(가시 창) S2v 에서 V1 이 b* 보다 적게 실패 (측정, UNGATED)"; R_b\* (−3 dB) 0.603 [0.523, 0.675]; ΔR vs S2 C6 −0.205 [−0.303, −0.110] "S2v 의 genie 격차 회수율이 S2 C6 보다 낮다" |
| | 판정 2 (13 개) | 13/13 (i); X\* = V1-pilot, R 0.450 [0.356, 0.536] → "등록된 baseline 전부와 멀어진다" 조건 충족 |

그림 F26.


## 15. DOP·ROT 보충: 24 조건 × 등록 baseline 13 개 (SUPP16e4)

**EXPERIMENTS.md 행**: `2026-09-29 07:14 ~ 09:47 KST + 12:45 ~ 14:32 KST (텍사스 09-28 17:14 ~ 19:47 CDT + 22:45 ~ 09-29 00:32 CDT; …)`. 동결 e7c9f4a7, 24/24 수용·무결성 OK, 기록 감사 (Fable, 정정 없음; `NEXT_EXPERIMENTS_SUPP16e4.md` §6.2). 표 B `X → V1`, X ∈ b\* + 𝔅 12 (R0-pilot @1).

| 조건 | D2 C2 | D2 C6 | D3 | SV8e | UMi28 | MIX3 |
|---|---|---|---|---|---|---|
| DOP ν = 0.005 | k𝔅 12, (ii) 0, 문장 ✓ | k𝔅 12, (ii) 0, 문장 ✓ | k𝔅 12, (ii) 0, 문장 ✓ | k𝔅 12, (ii) 0, 문장 — | k𝔅 12, (ii) 0, 문장 ✓ | k𝔅 12, (ii) 0, 문장 ✓ |
| DOP ν = 0.01 | k𝔅 12, (ii) 0, 문장 — | k𝔅 11, (ii) 0, 문장 — | k𝔅 12, (ii) 0, 문장 ✓ | k𝔅 12, (ii) 0, 문장 ✓ | k𝔅 12, (ii) 0, 문장 — | k𝔅 12, (ii) 0, 문장 ✓ |
| ROT 15° | k𝔅 12, (ii) 0, 문장 ✓ | k𝔅 11, (ii) 0, 문장 — | k𝔅 12, (ii) 0, 문장 ✓ | k𝔅 8, (ii) 0, 문장 — | k𝔅 12, (ii) 0, 문장 ✓ | k𝔅 12, (ii) 0, 문장 ✓ |
| ROT 30° | k𝔅 12, (ii) 0, 문장 ✓ | k𝔅 12, (ii) 0, 문장 ✓ | k𝔅 12, (ii) 0, 문장 ✓ | k𝔅 12, (ii) 0, 문장 ✓ | k𝔅 12, (ii) 0, 문장 ✓ | k𝔅 12, (ii) 0, 문장 ✓ |

- k𝔅 = 𝔅 12 중 (i) 수, 문장 = "등록된 baseline 전부와 멀어진다" 조건 (원 b\* (i) + k𝔅 = 12 + (ii) 0 + R_{X\*} 하한 > 0). 집계: (ii) 0/288; k𝔅 = 12 21/24; 문장 18/24 (가능 19 중 18). D2 C2 주 라벨 네 조건 모두 (A) "V1 이 𝔅 12 개 전부보다 적게 실패". genie ≥ V1 가드: DOPb D2 C2·C6. 그림 F25, F29.


## 16. 정적 6 데이터셋 × 등록 baseline 13 개 (STATIC16e4, 규칙 고정 사후 계산)

**EXPERIMENTS.md 행**: `2026-09-30 07:31 ~ 07:33 KST (텍사스 09-29 17:31 ~ 17:33 CDT)`. 새 BLER 없음 — 기존 raw 위의 계산이며 작성자가 곡선·표를 먼저 봤다 (**"규칙 고정 사후 계산"**, 사용자 결정; 사전 등록이라 부르지 않는다). 동결 2139f082, 기록 감사 정정 없음 (§6.2).

| 데이터셋 | 원 b\* | k𝔅 · m𝔅 · 판정 못함 | (i) 아닌 X (𝔅) | X\* (F −3 dB) · R_{X\*} [90%] | "전부" 문장 조건 |
|---|---|---|---|---|---|
| D2 C2 (헤드라인) | (i) | 12 · 0 · 0 | — | M-ours-bstar (623) · 0.470 [0.427, 0.512] | 충족 |
| D2 C6 | (i) | 11 · 0 · 1 | V1-pilot (iv) | V1-pilot (83) · 0.492 [0.355, 0.630] | 불충족 |
| D3 | (i) | 12 · 0 · 0 | — | M-ours-bstar (1298) · 0.367 [0.335, 0.399] | 충족 |
| SV8e | (iv) | 9 · 0 · 3 | M-ours-bstar-scalar (iv), M-ours-gmm32 (iv), V1-pilot (iv) | M-ours-bstar (464) · 0.143 [0.095, 0.188] | 불충족 |
| UMi28 | (i) | 12 · 0 · 0 | — | M-ours-bstar (1270) · 0.062 [0.033, 0.089] | 충족 |
| MIX3 (보고 전용) | (i) | 12 · 0 · 0 | — | M-ours-bstar (1421) · 0.090 [0.062, 0.117] | 충족 |

- 새로 계산된 라벨 48 개 (8 arm × 6) 중 (i) 46, (iv) 2 (SV8e b\*-scalar·gmm32), (ii) 0. 문장 4/6 (가능하던 4 곳 전부). §3 예측 8/8.


## 17. 진단 (보고 전용): genie 고SNR 바닥

출처 DECISIONS `진단 (보고 전용) — genie 고SNR 바닥의 원인` 줄, `conf/results/review_next/genie_floor/`. D2 C2 +9..+15 dB 의 genie 실패 6 건 전부 L = 3 (< Nt = 4, cond(H) ≈ 1e16, 랭크 3); D3 27 건 중 L = 3 21 건, L = 4 5 건 (cond ≈ 1e4). SNR 점마다 채널·잡음을 독립으로 뽑으므로 실패 수 10 건 안팎의 점에서 곡선이 한 점 오르내리는 것은 표본 잡음이다.


## 18. 시드 강건성 2: D3 · SV8e · MIX3 (SEEDS3_16e4; 동일예산 1.6e5)

**EXPERIMENTS.md 행**: `2026-09-30 18:11 ~ 22:03 KST (텍사스 09-30 04:11 ~ 08:03 CDT)`. 등록 `conf/results/review_next/NEXT_EXPERIMENTS_SEEDS3_16e4.md` v2 (동결 73a93547, §5 dbe0bdb3), 결과 §6.1 (:72–112), 기록 감사 §6.2 (:114–123; `prereg_audit_2026-09-30/audit_SEEDS3_16e4.md` — 수치·라벨·채점 오류 0, 규칙 위반 0, 위생 정정 6 건 반영). 선례 §10.5 (D2·UMi28). 규칙 (등록 §1): a1 이 보고용 arm, 시드는 BLER 을 본 뒤 고르지 않는다; 같은 레시피·예산·GMM b\*·테스트 시행 0..2559 에서 확산 체크포인트 (`_best.pt`) 만 바꾼다. 표 B `b* → V1`, BLER@16, n = 2560, C2. 실행 커밋 6b1de688 — conf/code 가 동결 73a93547 과 12 파일 다르다 (HISNR·STATIC·체인 스크립트 추가 등); Stage C·수신기·runner 코드 (score.py·arms.py·runner.py) 는 동일하고 `--ref-arms all` 의 차이 = {V0, V1, V4, V4b} 가 이를 확인한다 (§6.1 :74).

| prior · 시드 (태그) | 체크포인트 `_best` sha256[:16] · best_epoch (§5) | 표 B 판정점 a:b · pooled | 라벨 | SNR@0.1 격차 b\*−V1 [90%] | V1 −3 dB BLER (95% Wilson) | R (−3 dB) [90%] |
|---|---|---|---|---|---|---|
| D3 a1 (D3B16e4; §0 인용) | @494 | +0/+3/+6: 221:39 · 116:19 · 56:9 · 393:67 | (i) 3/3 | +1.41 [+1.19, +1.67] | 0.391 (0.372, 0.410) | 0.367 [0.335, 0.399] |
| D3 a2 (D3B16e4s2) | 4e9a6ca2c3197004 · 386 | 223:31 · 117:23 · 57:12 · 397:66 | **(i)** 3/3 | +1.42 [+1.20, +1.69] | 0.400 (1024/2560) | 0.337 [0.306, 0.370] |
| D3 a3 (D3B16e4s3) | 3e4e36945a9314c3 · 449 | 224:34 · 118:18 · 59:10 · 401:62 | **(i)** 3/3 | +1.46 [+1.24, +1.74] | 0.398 (1019/2560) | 0.343 [0.312, 0.375] |
| SV8e a1 (SVB16e4; §0) | @240 | −3/+0: 124:62 · 24:10 · 148:72 | (iv) | +0.25 [+0.16, +0.33] | 0.157 (0.143, 0.172) | 0.143 [0.095, 0.188] |
| SV8e a2 (SVB16e4s2) | b05d92632e611494 · 236 | 120:65 · 27:12 · 147:77 | **(iv)** "판정하지 못함 (검정력 미달)" (판정점 2) | +0.24 [+0.15, +0.32] | 0.160 (409/2560) | 0.127 [0.079, 0.175] |
| SV8e a3 (SVB16e4s3) | 5e1ff49f455f110a · 299 | 126:62 · 28:6 · 154:68 | **(iv)** "판정하지 못함 (검정력 미달)" (판정점 2) | +0.30 [+0.22, +0.39] | 0.156 (400/2560) | 0.148 [0.098, 0.192] |
| MIX3 a1 (MXB16e4; §0, 보고 전용) | @464 | +3/+6/+9: 85:39 · 71:21 · 42:11 · 198:71 | (i) 3/3 | +0.98 [+0.68, +1.31] | 0.529 (0.510, 0.548) | 0.090 [0.062, 0.117] |
| MIX3 a2 (MXB16e4s2) | d7a6b1a199c51637 · 433 | 79:38 · 62:28 · 41:15 · 182:81 | **(i)** 3/3 | +0.72 [+0.44, +1.03] | 0.532 (1363/2560) | 0.078 [0.052, 0.106] |
| MIX3 a3 (MXB16e4s3) | 128b8090036332bc · 351 | 79:40 · 66:24 · 41:12 · 186:76 | **(i)** 3/3 | +0.83 [+0.54, +1.15] | 0.530 (1358/2560) | 0.085 [0.058, 0.112] |

(표는 §6.1 :76–86 그대로, 체크포인트 칸만 §5 :65 에서. 원본 `results/tables_D2_<TAG>.txt`, `results/review_next/recovery_<TAG>.txt`.)

- **등록 라벨 (§1, 분모 3 = a1·a2·a3; §6.1 :88–91)**: D3 **"시드 강건 (3/3 (i))"**; SV8e **"판정하지 못함 (0/3 (i), 3 판정 못함)"** — §0 에서 이미 정해진 사실 (b\* 비트 동일 → 판정점 2 개; `tables_D2_SVB16e4.txt` 372–374 의 +3 dB b\* 0.003 ∉ [0.005, 0.9]), 보고 전용; MIX3 **"시드 강건 (3/3 (i))"** (보고 전용 부속 점; 역할 불변).
- 수용: 6/6 **ACCEPT: OK**, `--ref-arms all` 의 "arms differing" = {V0, V1, V4, V4b} 6/6, 판정점 = a1 과 같음. b\*·genie −3 dB 실패 수는 세 시드에서 같다 (D3 1298·485, SV8e 464·31, MIX3 1421·679) (§6.1 :74, :93).
- 학습: 여섯 모두 발산 없음, patience 정지 (§5; §6.2 위생 정정 4 — §5 표제 "stopped_by (`_best.pt`)" 는 "best_epoch (`_best.pt`) · stopped_by (last `.pt`·로그 done 줄)" 로 읽는다).
- 보고 전용: 시드 간 산포 (V1 −3 dB) D3 0.391–0.400, SV8e 0.156–0.160, MIX3 0.529–0.532; V0 −3 dB·가드 발동률·NMSE → `tables_D2_<TAG>.txt`, `guard_D2_<TAG>.txt` (§6.1 :110).
- §3 예측: 적중 8, 빗나감 0 (§6.1 :95–108; 항목 9 는 경로 서술이라 채점하지 않음 — §6.2 메모).
- 캐비엇·공개 (등록 기록 그대로): 등록은 세 데이터셋 a1 의 BLER 결과와 D2·UMi28 시드 결과를 본 뒤 작성됐다; a2·a3 학습은 초안보다 먼저 시작했고 (MIX3 a3 는 동결 17:00 CDT 뒤 시작 — §4, §6.2 위생 정정 2), 학습 초기에 세션 조작 실수로 중단됐다가 같은 명령으로 재개됐다 (모두 epoch ≤ 32; 표본 스트림은 중단 없는 실행과 같고 GPU 부동소수 비트 동일은 보장되지 않는다 — 머리말·§4). a1 판정 (D3 (i), SV8e (iv), MIX3 (i) 보고 전용) 은 어느 결과에서도 바뀌지 않는다; 동등성 주장 없음; 다중성: 태그 6 개의 표 B 는 각각 보고, 집계 라벨만 새로 만든다 (§1). 학습 GPU 번호는 로그에 장치 색인이 없어 확인하지 못했다 (§6.2 메모).


## 19. 고SNR 보강 (보고 전용): D2 C2·C6, +6..+15 dB, 새 시행 n = 20480 (HISNR16e4)

**EXPERIMENTS.md 행**: `2026-09-30 22:03 ~ 10-01 07:09 KST (텍사스 09-30 08:03 ~ 17:09 CDT)`. 등록 `conf/results/review_next/NEXT_EXPERIMENTS_HISNR16e4.md` v2 (동결 32444c91), 결과 §6.1 (:41–143), 기록 감사 §6.2 (:145–151; `prereg_audit_2026-10-01/audit_HISNR16e4.md` — 327 검사 오류 0, 규칙 위반 0, 위생 정정 3 건 반영). **보고 전용 — 새 판정 라벨을 만들지 않는다**; 등록된 판정점·라벨·"전부" 문장은 원 태그 (n = 2560) 의 것이다 (등록 머리말·§2). 셀·가중치·적합은 원 태그와 같다: D2 C2 (HSB16e4k = B16e4k 의 헤드라인 가중치 `ckpt/d2sx_N160000_a1.pt` 4443921ce8d5c4a1 legacy-last, b\* kron 1024) · D2 C6 (HSNR16 = NR16B16e4 의 `ckpt/d2sx_NR16_N160000_a1_fb2_best.pt` c050d611b2c714a6 best, b\* kron 4096). 시행 10000..30479 (`common.HISNR_SKIP0`; 테스트 0..2559·개발 2560..·P3 3200..·A1C5 4480.. 와 겹치지 않음), 6 arm (V1, b\*, R2-ours-G, R1-turbo, R3-bigamp, R5-genie), BLER@16 (반복 16), 95% Wilson. 실행 커밋 6b1de688, 2/2 **ACCEPT: OK** (§6.1 :43–48).

**D2 C2 (HSB16e4k)** — 실패 / n · BLER [95% Wilson] (§6.1 :61–71 = `results/review_next/hisnr_HSB16e4k.txt`)

| arm | +6 dB | +9 dB | +12 dB | +15 dB |
|---|---|---|---|---|
| M-ours-dscore-C-V1 | 111 / 20480 · 5.42e-03 [4.50e-03, 6.52e-03] | 59 / 20480 · 2.88e-03 [2.23e-03, 3.71e-03] | 39 / 20480 · 1.90e-03 [1.39e-03, 2.60e-03] | 23 / 20480 · 1.12e-03 [7.48e-04, 1.68e-03] |
| M-ours-bstar | 235 / 20480 · 1.15e-02 [1.01e-02, 1.30e-02] | 149 / 20480 · 7.28e-03 [6.20e-03, 8.54e-03] | 81 / 20480 · 3.96e-03 [3.18e-03, 4.91e-03] | 72 / 20480 · 3.52e-03 [2.79e-03, 4.42e-03] |
| R2-ours-G | 467 / 20480 · 2.28e-02 [2.08e-02, 2.49e-02] | 292 / 20480 · 1.43e-02 [1.27e-02, 1.60e-02] | 182 / 20480 · 8.89e-03 [7.69e-03, 1.03e-02] | 133 / 20480 · 6.49e-03 [5.48e-03, 7.69e-03] |
| R1-turbo | 903 / 20480 · 4.41e-02 [4.14e-02, 4.70e-02] | 521 / 20480 · 2.54e-02 [2.34e-02, 2.77e-02] | 291 / 20480 · 1.42e-02 [1.27e-02, 1.59e-02] | 204 / 20480 · 9.96e-03 [8.69e-03, 1.14e-02] |
| R3-bigamp | 1083 / 20480 · 5.29e-02 [4.99e-02, 5.60e-02] | 1033 / 20480 · 5.04e-02 [4.75e-02, 5.35e-02] | 1116 / 20480 · 5.45e-02 [5.15e-02, 5.77e-02] | 1100 / 20480 · 5.37e-02 [5.07e-02, 5.69e-02] |
| R5-genie | 66 / 20480 · 3.22e-03 [2.53e-03, 4.10e-03] | 36 / 20480 · 1.76e-03 [1.27e-03, 2.43e-03] | 16 / 20480 · 7.81e-04 [4.81e-04, 1.27e-03] | 13 / 20480 · 6.35e-04 [3.71e-04, 1.09e-03] |
| 짝지음 b\* only : V1 only · exact 양측 부호검정 p (보고 전용) | 158:34 · p = 2.6e-20 | 106:16 · p = 1.8e-17 | 61:19 · p = 2.7e-06 | 57:8 · p = 3.2e-10 |

**D2 C6 (HSNR16)** — 실패 / n · BLER [95% Wilson] (§6.1 :73–83 = `hisnr_HSNR16.txt`)

| arm | +6 dB | +9 dB | +12 dB | +15 dB |
|---|---|---|---|---|
| M-ours-dscore-C-V1 | 29 / 20480 · 1.42e-03 [9.86e-04, 2.03e-03] | 24 / 20480 · 1.17e-03 [7.88e-04, 1.74e-03] | 20 / 20480 · 9.77e-04 [6.32e-04, 1.51e-03] | 13 / 20480 · 6.35e-04 [3.71e-04, 1.09e-03] |
| M-ours-bstar | 178 / 20480 · 8.69e-03 [7.51e-03, 1.01e-02] | 130 / 20480 · 6.35e-03 [5.35e-03, 7.53e-03] | 72 / 20480 · 3.52e-03 [2.79e-03, 4.42e-03] | 46 / 20480 · 2.25e-03 [1.68e-03, 2.99e-03] |
| R2-ours-G | 309 / 20480 · 1.51e-02 [1.35e-02, 1.69e-02] | 213 / 20480 · 1.04e-02 [9.10e-03, 1.19e-02] | 125 / 20480 · 6.10e-03 [5.13e-03, 7.27e-03] | 80 / 20480 · 3.91e-03 [3.14e-03, 4.86e-03] |
| R1-turbo | 621 / 20480 · 3.03e-02 [2.81e-02, 3.28e-02] | 433 / 20480 · 2.11e-02 [1.93e-02, 2.32e-02] | 264 / 20480 · 1.29e-02 [1.14e-02, 1.45e-02] | 157 / 20480 · 7.67e-03 [6.56e-03, 8.96e-03] |
| R3-bigamp | 1090 / 20480 · 5.32e-02 [5.02e-02, 5.64e-02] | 1265 / 20480 · 6.18e-02 [5.86e-02, 6.51e-02] | 1418 / 20480 · 6.92e-02 [6.58e-02, 7.28e-02] | 1099 / 20480 · 5.37e-02 [5.07e-02, 5.68e-02] |
| R5-genie | 17 / 20480 · 8.30e-04 [5.18e-04, 1.33e-03] | 16 / 20480 · 7.81e-04 [4.81e-04, 1.27e-03] | 7 / 20480 · 3.42e-04 [1.66e-04, 7.05e-04] | 7 / 20480 · 3.42e-04 [1.66e-04, 7.05e-04] |
| 짝지음 b\* only : V1 only · exact 양측 부호검정 p (보고 전용) | 156:7 · p = 9.5e-38 | 111:5 · p = 4e-27 | 63:11 · p = 5.3e-10 | 38:5 · p = 2.5e-07 |

**원 태그 (n = 2560) 와 나란히 (합치지 않음)** (§6.1 :85–104; 원 태그 수치는 `raw_B16e4k`·`raw_NR16B16e4` 에서 같은 Wilson 식으로 기록자가 계산 — 재현 `prereg_audit_2026-10-01/recompute_hisnr.out` §3)

| 셀 | SNR | arm | 원 태그 (n = 2560) 실패 · BLER [95% Wilson] | 이 실행 (n = 20480) 실패 · BLER [95% Wilson] | 이 실행 점추정 ∈ 원 구간 |
|---|---|---|---|---|---|
| C2 | +6 | V1 | 16 · 6.25e-03 [3.85e-03, 1.01e-02] | 111 · 5.42e-03 [4.50e-03, 6.52e-03] | 예 |
| C2 | +6 | b\* | 28 · 1.09e-02 [7.58e-03, 1.58e-02] | 235 · 1.15e-02 [1.01e-02, 1.30e-02] | 예 |
| C2 | +9 | V1 | 7 · 2.73e-03 [1.33e-03, 5.63e-03] | 59 · 2.88e-03 [2.23e-03, 3.71e-03] | 예 |
| C2 | +9 | b\* | 17 · 6.64e-03 [4.15e-03, 1.06e-02] | 149 · 7.28e-03 [6.20e-03, 8.54e-03] | 예 |
| C2 | +12 | V1 | 5 · 1.95e-03 [8.35e-04, 4.56e-03] | 39 · 1.90e-03 [1.39e-03, 2.60e-03] | 예 |
| C2 | +12 | b\* | 16 · 6.25e-03 [3.85e-03, 1.01e-02] | 81 · 3.96e-03 [3.18e-03, 4.91e-03] | 예 |
| C2 | +15 | V1 | 3 · 1.17e-03 [3.99e-04, 3.44e-03] | 23 · 1.12e-03 [7.48e-04, 1.68e-03] | 예 |
| C2 | +15 | b\* | 8 · 3.13e-03 [1.58e-03, 6.15e-03] | 72 · 3.52e-03 [2.79e-03, 4.42e-03] | 예 |
| C6 | +6 | V1 | 6 · 2.34e-03 [1.07e-03, 5.10e-03] | 29 · 1.42e-03 [9.86e-04, 2.03e-03] | 예 |
| C6 | +6 | b\* | 22 · 8.59e-03 [5.68e-03, 1.30e-02] | 178 · 8.69e-03 [7.51e-03, 1.01e-02] | 예 |
| C6 | +9 | V1 | 2 · 7.81e-04 [2.14e-04, 2.84e-03] | 24 · 1.17e-03 [7.88e-04, 1.74e-03] | 예 |
| C6 | +9 | b\* | 14 · 5.47e-03 [3.26e-03, 9.16e-03] | 130 · 6.35e-03 [5.35e-03, 7.53e-03] | 예 |
| C6 | +12 | V1 | 2 · 7.81e-04 [2.14e-04, 2.84e-03] | 20 · 9.77e-04 [6.32e-04, 1.51e-03] | 예 |
| C6 | +12 | b\* | 10 · 3.91e-03 [2.12e-03, 7.18e-03] | 72 · 3.52e-03 [2.79e-03, 4.42e-03] | 예 |
| C6 | +15 | V1 | 2 · 7.81e-04 [2.14e-04, 2.84e-03] | 13 · 6.35e-04 [3.71e-04, 1.09e-03] | 예 |
| C6 | +15 | b\* | 5 · 1.95e-03 [8.35e-04, 4.56e-03] | 46 · 2.25e-03 [1.68e-03, 2.99e-03] | 예 |

**genie 바닥** (`genie_floor.py --skip0 10000`, 두 태그 무조건; §6.1 :106–121 = `genie_floor/genie_floor_raw_<TAG>.txt`; §17 과 같은 진단의 새 시행판)

| 항목 | HSB16e4k (C2) | HSNR16 (C6) |
|---|---|---|
| 시행 · genie 실패 (4 SNR 합) | 81920 · 131 | 81920 · 47 |
| L=3 시행 · 실패 (비율) | 13711 · 114 (0.0083) | 13766 · 44 (0.0032) |
| L=4 | 13718 · 10 (0.0007) | 13503 · 1 (0.0001) |
| L=5 | 13717 · 4 (0.0003) | 13847 · 2 (0.0001) |
| L=6 | 13542 · 3 (0.0002) | 13591 · 0 (0.0000) |
| L=7 | 13684 · 0 (0.0000) | 13628 · 0 (0.0000) |
| L=8 | 13548 · 0 (0.0000) | 13585 · 0 (0.0000) |
| SNR 별 실패 (L) | +6: 66 (L3 52, L4 7, L5 4, L6 3); +9: 36 (L3 35, L4 1); +12: 16 (L3 16); +15: 13 (L3 11, L4 2) | +6: 17 (L3 15, L5 2); +9: 16 (L3 16); +12: 7 (L3 7); +15: 7 (L3 6, L4 1) |
| cond(H) 실패 / 성공: 중앙값 [p10, p90] | 1.51e+16 [4.78e+03, 2.43e+16] / 15.6 [4.78, 1.12e+16] | 1.42e+16 [7.85e+15, 1.85e+16] / 11 [3.83, 9.59e+15] |
| sigma_min(H) 실패 / 성공 | 3.5e-16 [2.12e-16, 0.00104] / 0.297 [4.2e-16, 0.909] | 5.51e-16 [4.28e-16, 8.24e-16] / 0.578 [6.78e-16, 1.56] |
| ‖H‖_F² 실패 / 성공 | 32.4 [19.8, 44.4] / 32 [26.5, 37.5] | 64.7 [55.6, 83.8] / 64 [57.2, 70.7] |
| genie 실패율 cond(H) ≥ p95 / 미만 | 0.0164 / 0.0008 (p95 = 1.49e+16) | 0.0076 / 0.0002 (p95 = 1.24e+16) |

- §3 예측 (보고 전용; §6.1 :123–131): 적중 3, 빗나감 0 — 1 (C2 +9..+15 dB genie 실패 36 / 16 / 13 > 0, 그중 L = 3 이 35/36, 16/16, 11/13, 합 62/65 = 95.4 %), 2 (V1 실패 ≤ b\* 실패 8/8), 3 (이 실행 점추정 ∈ 원 태그 95% Wilson 16/16; 원 구간 끝에 가장 가까운 칸 C2 +12 dB b\* 3.955e-03 대 원 하한 3.851e-03).
- 원고 문장 범위 (등록 §2): "고SNR 구간의 BLER 은 추가 n = 20480 시행에서 …" 처럼 **보고 전용 보강**으로만 쓴다. 그림은 등록 곡선을 대체하지 않고 별도 패널·표기로 싣는다 (§1). p 값은 서술용 (라벨 없음 → 다중성 해당 없음).
- 편차·주의 (§6.1 :133–143 그대로 요약):
  - 실행 HEAD 6b1de688 은 동결 32444c91 이 아니다 (차이 = `conf/DECISIONS.md`·`WORK_QUEUE.md` 두 문서; conf/code·Demo 차이 없음). raw `run|git`·매니페스트 git 은 6b1de688 하나.
  - 소요: C2 runner 44.4 min, C6 runner 500.3 min (합 544.7 min ≈ 9.1 h), 스크립트 전체 09-30 08:03–17:09 CDT (9 h 06 min). §1 추정 C2 ≈ 0.5 h, C6 ≈ 7.5 h, 합계 ≈ 8.2 h.
  - **§1 "실행 중 다른 CPU 작업 없음" 불충족** (감사 정정 §6.2): (a) SEEDS3 기록 감사의 raw 재계산 스크립트 두 개 (09:38–09:45 CDT); (b) SPARSE 재튜닝 `code/sparse_tune.py --prior S2 --cell C6 --n 256` (`~/t2_wtSBL`, CPU, 구간 전체와 겹침); (c) 2단계 GPU 적합 `code/fit_gpu.py 32 kron 2048 160000 {NR32B16e4, U28NR32B16e4} --restart 0/1/2` 6 개 (`~/t2_wtS`, GPU 0–5, 코어 1 개씩, 모두 C6 runner 구간 안) 와 bash 루프 gpu_sched.sh·edge_rule.sh·batched_prefix.sh. 근거 `prereg_audit_2026-10-01/concurrent_processes.txt` (구간 안에서 끝난 프로세스는 보이지 않으므로 하한). 수신기 실행·raw 쓰기 아님; 결과 값에 대한 영향은 판단하지 않는다 (§6.2 메모). §1 문장은 동결 문장이라 §6 편차로만 남긴다.
  - 매니페스트 fits_dir 는 실행 스크립트가 만든 미추적 링크 이름 (대상 = §1 적합); 수용이 meta·ckpt sha·role 을 대조해 OK. `stagec_gate` = "NO GATE RECORD mentions … -- UNVERIFIED here" (원 태그 매니페스트와 같은 문구).
  - genie 재현 대조 없음 (§1 대로; 새 시행). 원 태그 실패 수는 등록 머리말의 "기대 실패 수" (원 태그 실패 × 8) 와 맞는다.


## 20. 정적 6 데이터셋 × 희소 baseline 3 개 (SPARSE16e4; 등록 baseline 16 개)

**EXPERIMENTS.md 행**: `2026-10-01 09:04 ~ 10:22 KST (텍사스 09-30 19:04 ~ 20:22 CDT)`. 등록 `conf/results/review_next/NEXT_EXPERIMENTS_SPARSE16e4.md` v2 (동결 = 실행 커밋 02dafa1c = sbl → main 병합), 결과 §6.1 (:138–301), 기록 감사 §6.2 (:303–309; `prereg_audit_2026-10-01/audit_SPARSE16e4.md` — 2153 검사 오류 0, 규칙 위반 0, 위생 정정 3 건 반영). 선례 §16 (STATIC16e4). 새 arm 3 개를 정적 6 데이터셋의 테스트 시행 0..2559 (n = 2560, 7 SNR; 기존 raw 와 같은 시행) 에서 돌리고, `pair_baselines.py --extra raw_SP<suf> --add-baselines SBL-loop SBL-pilot OMP-pilot --r0 at1 --provenance manifest --expect …` 로 표 B `X → V1` 18 개를 새로 계산했다. b\* + 𝔅 12 의 13 라벨은 STATIC16e4 (규칙 고정 사후 계산) 인용 — `--expect` 대조 6 × 13 일치, 13 arm 블록이 `pairB_ST<TAG>.txt` 와 바이트 동일 6/6 (§6.1 :195). 새 arm (등록 §1): `SBL-loop` = 오버샘플 2-D DFT 사전 위 희소 분산 Gaussian prior (γ 갱신 MacKay 고정점, n_em 단계) 를 b\* 와 **같은 EP 수신기** 루프에; `SBL-pilot` = 같은 prior, 파일럿 전용 (채널 믿음 고정); `OMP-pilot` = 고정 L OMP 파일럿 전용, plug-in v = 1e-8. 하이퍼파라미터 (ρ, SNR 별 n_em·L) 는 개발 NMSE 로 고른 pick (§5; sha 고정, 6 행 모두 규칙 재현 True). 6/6 **ACCEPT: OK**, `meta|sparse` 불일치 청크 0, 새 arm 예외 시행 0, `--expect` 드리프트 없음 (§6.1 :140–153).

**표 B — 새 arm `X → V1`** (§6.1 :159–182 = `results/review_next/pairB_SP<suf>.txt`; R_X·절대 격차 (F_X − F_V1, −3 dB, /2560)·SNR@0.1 격차 X − V1 [90%] 는 보고 전용)

| 데이터셋 | X | 판정점 | 점별 a:b | pooled | 라벨 | R_X −3 dB [90%] | R_X 판정점 [90%] | 절대 격차 | SNR@0.1 격차 | 출처 줄 |
|---|---|---|---|---|---|---|---|---|---|---|
| D2 C2 | SBL-loop | −3/+0/+3 | 381:47 · 148:14 · 59:11 | 588:72 | **(i)** 3/3 | 0.540 [0.503, 0.579] | 0.587 [0.554, 0.618] | 334 | +1.86 [+1.64, +2.10] | SPB16e4k:96–102 |
| D2 C2 | SBL-pilot | −3/+0/+3 | 589:26 · 171:15 · 51:11 | 811:52 | **(i)** 3/3 | 0.665 [0.635, 0.694] | 0.676 [0.651, 0.702] | 563 | +2.12 [+1.90, +2.35] | :103–109 |
| D2 C2 | OMP-pilot | +0/+3/+6 | 263:9 · 124:8 · 64:3 | 451:20 | **(i)** 3/3 | 0.697 [0.669, 0.723] | 0.834 [0.802, 0.863] | 652 | +3.24 [+2.99, +3.51] | :110–116 |
| D3 | SBL-loop | +0/+3/+6 | 252:39 · 137:24 · 85:6 | 474:69 | **(i)** 3/3 | 0.406 [0.375, 0.438] | 0.525 [0.491, 0.560] | 352 | +1.62 [+1.35, +1.97] | SPD3:95–101 |
| D3 | SBL-pilot | +0/+3/+6 | 358:27 · 176:18 · 100:10 | 634:55 | **(i)** 3/3 | 0.506 [0.479, 0.534] | 0.613 [0.583, 0.641] | 528 | +2.35 [+1.97, +2.68] | :102–108 |
| D3 | OMP-pilot | +3/+6/+9 | 253:12 · 159:2 · 94:5 | 506:19 | **(i)** 3/3 | 0.528 [0.500, 0.555] | 0.792 [0.760, 0.823] | 575 | +3.95 [+3.52, +4.51] | :109–115 |
| SV8e | SBL-loop | −3/+0 | 209:37 · 47:5 | 256:42 | **(iv)** (POWERED=False, 판정점 2; V1 쪽 적음 2/2) | 0.317 [0.276, 0.355] | 0.341 [0.303, 0.377] (2 점) | 172 | +0.67 [+0.56, +0.78] | SPSV:95–101 |
| SV8e | SBL-pilot | −3/+0/+3 | 543:19 · 101:4 · 19:0 | 663:23 | **(i)** 3/3 | 0.585 [0.557, 0.614] | 0.604 [0.579, 0.630] | 524 | +1.44 [+1.31, +1.59] | :102–108 |
| SV8e | OMP-pilot | −3/+0/+3 | 1102:11 · 336:3 · 60:1 | 1498:15 | **(i)** 3/3 | 0.746 [0.727, 0.765] | 0.780 [0.764, 0.795] | 1091 | +3.04 [+2.89, +3.20] | :109–115 |
| UMi28 | SBL-loop | +3/+6/+9 | 154:25 · 97:21 · 56:10 | 307:56 | **(i)** 3/3 | 0.262 [0.230, 0.292] | 0.336 [0.299, 0.370] | 225 | +1.45 [+1.11, +1.76] | SPU28:95–101 |
| UMi28 | SBL-pilot | +3/+6/+9 | 201:16 · 113:21 · 74:12 | 388:49 | **(i)** 3/3 | 0.447 [0.421, 0.471] | 0.406 [0.373, 0.437] | 512 | +1.75 [+1.39, +2.09] | :102–108 |
| UMi28 | OMP-pilot | +6/+9/+12 | 282:5 · 177:3 · 110:2 | 569:10 | **(i)** 3/3 | 0.629 [0.609, 0.648] | 0.673 [0.645, 0.700] | 1076 | +4.28 [+3.65, +4.80] | :109–115 |
| MIX3 | SBL-loop | +3/+6/+9 | 190:33 · 136:12 · 90:11 | 416:56 | **(i)** 3/3 | 0.245 [0.216, 0.273] | 0.456 [0.421, 0.490] | 219 | +2.42 [+2.06, +2.80] | SPMX:95–101 |
| MIX3 | SBL-pilot | +3/+6/+9 | 256:29 · 169:11 · 98:9 | 523:49 | **(i)** 3/3 | 0.404 [0.378, 0.428] | 0.524 [0.493, 0.555] | 457 | +2.84 [+2.45, +3.28] | :102–108 |
| MIX3 | OMP-pilot | +6/+9/+12 | 408:0 · 257:3 · 171:5 | 836:8 | **(i)** 3/3 | 0.561 [0.539, 0.582] | 0.789 [0.766, 0.812] | 861 | +6.09 [+5.60, +6.65] | :109–115 |
| D2 C6 | SBL-loop | −3/+0/+3 | 203:5 · 83:4 · 44:2 | 330:11 | **(i)** 3/3 | 0.865 [0.820, 0.906] | 0.884 [0.847, 0.916] | 198 | n/a (<= −3 vs <= −3) — extend the SNR grid | SPNR16:95–101 |
| D2 C6 | SBL-pilot | −3/+0/+3 | 245:7 · 92:5 · 46:2 | 383:14 | **(i)** 3/3 | 0.885 [0.847, 0.920] | 0.898 [0.867, 0.926] | 238 | >= +0.38 dB (M-ours-dscore-C-V1 is already below 0.1 at the lowest grid SNR) | :102–108 |
| D2 C6 | OMP-pilot | −3/+0/+3 | 163:9 · 102:2 · 57:1 | 322:12 | **(i)** 3/3 | 0.832 [0.777, 0.884] | 0.881 [0.845, 0.914] | 154 | n/a (<= −3 vs <= −3) — extend the SNR grid | :109–115 |

(라벨의 "3/3" = `second arm fewer at 3/3, first arm fewer at 0/3`, 모두 POWERED=True.)

**데이터셋별 요약 — 등록 baseline 16 개 (b\* + 𝔅 12 + 새 3)** (§6.1 :184–193; `pairB_SP<suf>.txt` 의 SUMMARY-B·X\*·문장 조건 줄)

| 데이터셋 | 원 b\* (`--expect-bstar` 일치) | SUMMARY-B (15) (i) · (ii) · 판정 못함 | 16 개 (b\* + 𝔅 15) | (i) 아닌 X | X\* (F −3 dB) · R_{X\*} [90%] | "전부" 문장 조건 |
|---|---|---|---|---|---|---|
| D2 C2 (헤드라인) | (i) | 15 · 0 · 0 | 16 · 0 · 0 | — | M-ours-bstar (623) · 0.470 [0.427, 0.512] | MET |
| D3 | (i) | 15 · 0 · 0 | 16 · 0 · 0 | — | M-ours-bstar (1298) · 0.367 [0.335, 0.399] | MET |
| SV8e | (iv) | 11 · 0 · 4 | 11 · 0 · 5 | b\* (iv), M-ours-bstar-scalar (iv), M-ours-gmm32 (iv), V1-pilot (iv), SBL-loop (iv) | M-ours-bstar (464) · 0.143 [0.095, 0.188] | NOT met |
| UMi28 | (i) | 15 · 0 · 0 | 16 · 0 · 0 | — | M-ours-bstar (1270) · 0.062 [0.033, 0.089] | MET |
| MIX3 | (i) | 15 · 0 · 0 | 16 · 0 · 0 | — | M-ours-bstar (1421) · 0.090 [0.062, 0.117] | MET |
| D2 C6 | (i) | 14 · 0 · 1 | 15 · 0 · 1 | V1-pilot (iv) | V1-pilot (83) · 0.492 [0.355, 0.630] | NOT met |

- **주 라벨 (D2 C2; §6.1 :197)**: SBL-loop·SBL-pilot·OMP-pilot 모두 (i) → **(A) "V1 이 희소 baseline 3 개(SBL-loop, SBL-pilot, OMP-pilot) 전부보다 적게 실패"** (A1 = `SBL-loop → V1` (i) 588:72). 나머지 5 데이터셋은 측정 라벨 (§1).
- **"전부" 문장 (16 개; §6.1 :199)**: 조건 = 원 b\* (i) ∧ 등록 baseline 15 개 (𝔅 12 + 새 3) 모두 (i) ∧ (ii) 0 ∧ R_{X\*} CI 하한 > 0 (X\* 는 새 arm 포함 16 개 중 −3 dB 실패 최소) → **D2 C2·D3·UMi28·MIX3 충족** → "데이터셋 d 에서 등록된 baseline 전부(16 개, 희소 baseline 포함)와 멀어진다" (d = D2 C2, D3, UMi28, MIX3). C6·SV8e 불충족 (§1: STATIC16e4 의 (iv) 로 결과와 무관하게 불가능). X\*·R_{X\*} 는 6 데이터셋 모두 STATIC16e4 §6.1 값 (§16) 과 같다.
- **집계 (개수 서술만, 보정 없음; §6.1 :201)**: 새 18 라벨 중 (i) 17, (iv) 1 (SV8e SBL-loop), (ii) 0. 인용 78 라벨 (b\* 6 + 𝔅 72) 재계산·대조 일치. "전부" 문장 4/6 (가능하던 4 곳 모두). 다중성: 새 라벨 18 개, 개별 (i) 을 독립 주장으로 쓰지 않는다 (§1).
- §3 예측 (§6.1 :203–216): 적중 6, 빗나감 0, 채점 안 함 1 (예측 6 = 보고 전용 `b* → SBL-loop`, 등록 명령이 이 쌍을 내지 않아 계산하지 않음).

**보고 전용 (판정 아님)**

(b) −3 dB 실패 수 /2560 (§6.1 :222–231; `pairB_SP<suf>.txt` 의 `BLER@16 failures` 줄):

| 데이터셋 | R5-genie | V1 | b\* | SBL-loop | SBL-pilot | OMP-pilot |
|---|---|---|---|---|---|---|
| D2 C2 | 87 | 371 | 623 | 705 | 934 | 1023 |
| D3 | 485 | 1000 | 1298 | 1352 | 1528 | 1575 |
| SV8e | 31 | 402 | 464 | 574 | 926 | 1493 |
| UMi28 | 594 | 1228 | 1270 | 1453 | 1740 | 2304 |
| MIX3 | 679 | 1354 | 1421 | 1573 | 1811 | 2215 |
| D2 C6 | 22 | 53 | 184 | 251 | 291 | 207 |

(d) **SBL-loop NMSE@16 − SBL-pilot NMSE** (dB, SNR 별 = 10·log10 (SBL-loop 중앙값 / SBL-pilot 중앙값); §6.1 :256–265; 입력은 유효숫자 3 자리 출력값이라 반올림 오차 있음 — 감사 재계산 최대 |차| 0.018 dB; §2 의 n_em 문장과 함께 읽는다):

| 데이터셋 | −3 dB | 0 dB | +3 dB | +6 dB | +9 dB | +12 dB | +15 dB |
|---|---|---|---|---|---|---|---|
| D2 C2 | −4.56 | −5.14 | −5.30 | −5.40 | −5.52 | −5.47 | −5.52 |
| D3 | −2.56 | −4.75 | −5.11 | −5.32 | −5.43 | −5.43 | −5.45 |
| SV8e | −4.21 | −4.71 | −4.92 | −5.09 | −5.14 | −5.19 | −5.26 |
| UMi28 | −2.06 | −3.33 | −3.99 | −4.53 | −4.88 | −5.03 | −5.06 |
| MIX3 | −1.80 | −3.25 | −4.06 | −4.51 | −4.86 | −4.96 | −5.15 |
| D2 C6 | −5.10 | −5.52 | −5.53 | −5.55 | −5.51 | −5.60 | −5.62 |

- 새 arm 의 NMSE@16 중앙값 (c) 는 §6.1 :233–254, 테스트 파일럿 전용 NMSE@1 과 §5 개발 NMSE 의 차 (e; 정의가 달라 채점하지 않음) 는 §6.1 :267–284. 튜닝 pick (ρ, SNR 별 n_em·L, 개발 NMSE) 은 등록 §5.1 (:80–108)·§5.2 (:110–127).

**캐비엇 (§2·§5.3 이 적으라고 정한 것; §6.1 :288–292)**:
- **ρ 는 격자 끝 16 (확장 규칙 2 회째를 비용으로 중단)** (§5.3). pick 의 `edge_rho_*`: SBL 은 D2 C2·D3·SV8e·MIX3·C6 에서 ρ 16 끝 (UMi28 은 ρ_SBL 8 내부), OMP 는 6 데이터셋 모두 ρ 16 끝; SNR 별 끝 플래그는 모두 false. ρ 32 확장은 09-30 09:28 CDT 에 비용으로 중단, ρ 32 의 NMSE 는 저장·열람되지 않았다; ρ 8 → 16 의 SNR 평균 개선은 SBL ≤ 0.05 dB, OMP ≤ 0.20 dB 이나 ρ 32 가 더 낫지 않다는 증거는 아니다; OMP ρ 32 는 M × M `AᴴGA` 메모리 (192 워커 ≈ 3.3 TB) 로 테스트 실행 자체가 불가능하다 (§5.3).
- **OMP-pilot = 파일럿 LS 인 점 (L = N = 32, §2)**: D2 C2 +15 dB; SV8e +3..+15 dB; UMi28 +3..+15 dB; MIX3 +6..+15 dB — 15 점; D3 없음; C6 없음 (L ≤ 12 < N = 64). OMP-pilot 판정점 중 이 점: SV8e +3 dB, UMi28 (+6/+9/+12) 셋 모두, MIX3 (+6/+9/+12) 셋 모두. 이 점의 OMP-pilot 결과는 원고에서 "희소 복원" 으로 부르지 않는다.
- **새 arm 예외 시행**: 6 행 × 3 arm 모두 0 → "개수를 라벨 문장에 함께 적는다" 규칙이 적용되는 라벨 없음.
- **SBL-loop 의 n_em 은 파일럿 개발 NMSE 로 SNR 별로 고른 값을 루프 안에서도 그대로 쓴다** (루프 전용 튜닝 없음). 튜닝 표 기준 가능한 손해 (SNR 중 최대): D2 C2 0.28 dB, D3 0.85 dB, SV8e 0.15 dB, UMi28 0.05 dB, MIX3 0.09 dB — 방향은 SBL-loop 에 불리 (= V1 쪽으로 기운다) (§2).
- 원고 문장 범위 (§2): 이 셀·예산·prior, **on-grid 오버샘플 2-D DFT 사전**과 §1 튜닝 규칙의 SBL·OMP — SBL = MacKay 고정점 n_em 단계 (SNR 별 튜닝; 블록·외부 반복마다 평탄 초기값에서 재시작, 웜스타트 없음), OMP = 고정 L (SNR 별 튜닝), 잡음 기반 정지 없음, 채널 믿음 plug-in (v = 1e-8, 오차 비인지). off-grid 방법 (NOMP 등) 은 범위 밖. ρ 16 격자 끝을 원고에 적는다.
- 편차·주의 (§6.1 :294–301): §1 "실행 중 다른 CPU 작업 없음 (예외 …)" 대조 — 2단계 GPU 적합 6 개·bash 루프는 §1 예외 목록 안; 상시 도구 프로세스 (Claude Code 세션, claude-mem worker·chroma-mcp) 는 실험 작업이 아니며 §1 예외 목록에 이름이 없다; 근거 `prereg_audit_2026-10-01/sparse_ps_snapshot_transcriber_2027CDT.txt`·`sparse_concurrent_processes.txt` (하한; 결과 값에 대한 영향은 판단하지 않는다). 소요 runner C2 9.5·9.2·6.2·4.8·7.6 min, C6 37.6 min, 스크립트 전체 1 h 18 min (§1 추정 C2 ≈ 10 분 안팎, C6 ≈ 15 분–1.5 h). runner 는 `tables_D2_SP*`·`guard_D2_SP*` 를 만들지 않았다 (등록 출력은 pairB·accept·manifest). p 값은 서술용.


## 21. 배열 규모 확장: Nr 8 → 16 → 32, D2 · UMi28 (SCALE16e4; 동일예산 1.6e5)

**EXPERIMENTS.md 행**: `2026-10-02 04:16 ~ 10-04 01:49 KST (텍사스 10-01 14:16 ~ 10-03 11:49 CDT)`. 등록 `conf/results/review_next/NEXT_EXPERIMENTS_SCALE16e4.md` v3 (동결 16a9dff6, 브랜치 scale; 실행 커밋 = §5 커밋 b4433d3c; main 병합 29391104), 결과 §6.1 (:419–741), 기록 감사 §6.2 (:743–750; `prereg_audit_2026-10-03/audit_SCALE16e4.md` — 474 검사 오류 0, 규칙 위반 0, 위생 정정 3 건 + §4.1 상태 칸 반영). **UNGATED "배열 규모 축 측정"** 이며 arm 판정이 아니다; 헤드라인 (C2 B16e4k) 과 기존 등록의 §6 은 어떤 결과로도 바뀌지 않는다 (등록 §1). Nr 8 → 16 → 32 (Nt 4, T 16, Tp 4 고정), D2 (prior S2) · 3GPP 38.901 UMi 28 GHz (UMi28), 테스트 시행 0..2559, n = 2560, BLER@16. 재사용 3 셀 (D2 C2 `raw_B16e4k` legacy-last, D2 C6 `raw_NR16B16e4` fb2 `_best`, UMi28 C2 `raw_U28B16e4` `_best`; 재실행 없음, bridge 비트 대조 3/3) + 새 3 셀 (D2 C9 `NR32B16e4`, UMi28 C6 `U28NR16B16e4`, UMi28 C9 `U28NR32B16e4`; `_best.pt`, raw 는 scale 워크트리 `~/t2_wtS/conf`). 1차 통계량 **R = (ΣF_b\* − ΣF_V1)/(ΣF_b\* − ΣF_g)** 를 판정점 (앵커 b\* 자동) 3 점 합에서 (R_dp). R 은 **상대 통계량**이다 (b\* 가 나빠져도 오른다) — 절대 격차는 보고 전용으로 함께 싣는다 (등록 목적 문단). 실행: `SCALE2_DONE ok=101 fail=0`, 재개 없음, 수용 전부 OK — 추세 게이트 3/3, pair 게이트 3/3, bridge 3/3, K2 4/4 + `raw_B16e4` 0/448, last 3/3 (§6.1 :421–496). 판정점 (자동): UMi28 C6 0/+3/+6, UMi28 C9 −3/0/+3, D2 C9 −9/−6/−3.

### 21.1 1차: 데이터셋별 ΔR = R_C9 − R_C2, Holm m = 2 (§6.1.1 :498–548)

| 데이터셋 | R_C9 (spec 1) [90%] · 판정점 합 b\* · V1 · genie | R_C2 (spec 2) [90%] · 판정점 합 | ΔR [90%] | ΔR [95%] | 부트스트랩 p | Holm 순서 · 수준 | 라벨 | 출처 |
|---|---|---|---|---|---|---|---|---|
| D2 | **0.811** [0.790, 0.832] · −9/−6/−3: 1161 · 276 · 70 | **0.509** [0.470, 0.544] · −3/0/+3: 864 · 488 · 125 | +0.302 [+0.262, +0.345] | **+0.302 [+0.254, +0.355]** | 0.0000 | 첫째 · 95 % | **(T+)** | `scale2_primary_D2_L95:3–6`, `_L90:3–6` |
| UMi28 | **0.432** [0.401, 0.463] · −3/0/+3: 958 · 599 · 127 | **0.150** [0.108, 0.190] · +3/+6/+9: 800 · 712 · 215 | **+0.282 [+0.232, +0.335]** | +0.282 [+0.221, +0.345] | 0.0000 | 둘째 · 90 % | **(T+)** | `scale2_primary_U28_L95:3–6`, `_L90:3–6` |

- Holm 순서 (§1 다중성): p_D2 = p_UMi28 = 0.0000 (B = 2000 이라 p < 0.001 로 읽음) → **동률 → D2 첫째 (95 % CI), UMi28 둘째 (90 % CI)** (§1 의 "동률 가능성 높음 → 순서는 동률 규칙이 정한다" 공개 그대로 실현). UMi28 은 첫째가 (T0) 가 아니므로 (T0-Holm) 아님.
- 가드 점검 (네 셀): 판정점 3 개; ΣF_b\* > ΣF_g; ΣF_g < ΣF_V1; 정의 불가 복제 0 %; 학습·수용 실패 없음 → **(T-iv) 없음**, p := 1 대체 없음.
- 재사용 셀의 등록 CI = 이 `_L90` 파일의 R2 줄 (등록 §0.1 표 [0.470, 0.545]·[0.110, 0.189] 와 셋째 자리가 다르며 §0.1 규칙대로 파일 값이 등록값). 점추정 0.509 / 0.150 = §1 재현 요구 (0.508796 / 0.150427).

**GMM 프로토콜 한정어 G_d** (§2 첫 줄; (T±)·S_d 문장 끝에 항상 붙임 — §6.1 :513–516 그대로):
- G_D2 = "(b\* = 등록 프로토콜의 GMM — kron K ≤ 4096, 재시작 3, EM 상한 500 반복·tol/patience 정지 — 이며 최적 GMM 이 아니다; 격자 끝·tol 정지 셀: D2 C9 `NR32B16e4` tol 정지 24/24 (b\* kron 2048 은 적합 격자 내부, 격자 끝 아님), D2 C2 `B16e4k` 격자 끝 kron 1024 (2048 미적합))"
- G_UMi28 = "(b\* = 등록 프로토콜의 GMM — kron K ≤ 4096, 재시작 3, EM 상한 500 반복·tol/patience 정지 — 이며 최적 GMM 이 아니다; 격자 끝·tol 정지 셀: UMi28 C9 `U28NR32B16e4` 격자 끝 kron 4096 (4096 멈춤)·tol 정지 24/24, UMi28 C2 `U28B16e4` 격자 끝 kron 4096 (4096 멈춤))"
- (재사용 셀 적합 파일의 tol 정지 수는 등록 문서에 기록이 없어 목록에 넣지 않았다 — §6.1.7.)

**한정어 Q-OP** (R\*@0.05, CI = 그 데이터셋의 Holm 수준; §6.1 :518–525)

| 데이터셋 (수준) | R\*_C9 | R\*_C2 | L\* = R\*_C9 − R\*_C2 | 한정어 |
|---|---|---|---|---|
| D2 (95 %) | 0.909 [95% 0.851, 0.968] (s\* −4.31 dB, B_V1 0.0073, B_g 0.0030) | 0.610 [95% 0.518, 0.699] (s\* +0.93 dB, 0.0244, 0.0080) | +0.299 [95% +0.190, +0.413], p 0.0000 (`primary_D2_L95:13–15`) | **"[운영점 정합 강건]"** |
| UMi28 (90 %) | 0.558 [90% 0.486, 0.625] (s\* +3.44 dB, 0.0238, 0.0030) | 0.218 [90% 0.120, 0.322] (s\* +8.93 dB, 0.0413, 0.0104) | +0.339 [90% +0.210, +0.460], p 0.0010 (`primary_U28_L90:14–16`) | **"[운영점 정합 강건]"** |

**한정어 Q-K** (§6.1 :527–539)
- **D2**: C9 는 K_max 내부 (b\* kron 2048 < 적합 최대 4096) → '-'. C2 끝: r 0.8403499716975932, c_K 5.2637007373767215, K/2 = `raw_B16e4` (kron 512), b\*(K/2) 899, ΔF = +35, ΣF⁺ = 679.77, R⁺ = 0.346 [90% 0.106, 0.492] (`primary_D2_L95:10`); 강제 조건 해당 없음 → 세 실행 (Holm 수준 95 %):

| 실행 | 읽은 줄 | 값 | L⁺ |
|---|---|---|---|
| (a) 두 끝 | R1⁺ − R2⁺ (`primary_D2_L95:11`) | +0.466 [95% +0.294, +0.770], p 0.0000 | (T+) |
| (b) C9 끝만 | 외삽 없음 → R1 − R2 (`primary_D2_L95_qkC9:6`) | +0.302 [95% +0.254, +0.355], p 0.0000 | (T+) |
| (c) C2 끝만 | R1⁺ − R2⁺ (`primary_D2_L95_qkC2:11`) | +0.466 [95% +0.294, +0.770], p 0.0000 | (T+) |

  셋 모두 1차 라벨 (T+) 과 같다 → **"[K 상한 강건]"**. 90 % 파일 값 (보고): (a)·(c) +0.466 [90% +0.315, +0.710].
- **등록 공개의 재게시 (§2.1 Q-K, §6.1 :538 그대로)**: D2 에서는 C2 끝의 c_K = 5.264 로 R⁺_C2 가 크게 내려가 (0.509 → 0.346 [90% 0.106, 0.492]) 실행 (a)·(c) 가 '강건' 쪽으로 기울고, 그래서 실행 (b) 가 (T+) 의 실제 검사다; 미확장 D2 C2 b\* 자체는 반대로 ΔR_D2 에 보수적이다.
- **UMi28 — 강제 한정어**: UMi28 C9 의 r = 1.2799495603934918 ≥ 1 → c_K = inf (§5, BLER 전에 정해짐) → 셀 한정어 "[K 상한 민감: 외삽 불가]" → §2.1 Q-K (1) 로 **1차 라벨에 "[K 상한 민감: 외삽 불가]" 를 강제로 붙인다** (`primary_U28_L90:10,12`: `R1+ - R2+: n/a (Q-K undefined)`). C2 끝 (보고): b\*(K/2) 809, ΔF +9, c_K 1, ΣF⁺ 791, R⁺ 0.137 [90% 0.071, 0.185]. `primary_U28_L{95,90}_qk{C9,C2}` 4 파일은 라벨·강건 판단에 쓰지 않는다 (보고만: qkC2 R1⁺ − R2⁺ = +0.295 [95% +0.226, +0.384] / [90% +0.238, +0.369]).

**1차 라벨 (§2.1 문구 그대로; §6.1 :541–543)**:
- **D2 — (T+)**: "Nr 8→32 에서 V1 의 genie 격차 회수율(b\* 대비 상대 격차)이 커진다 (D2, 동일예산 1.6e5, b\* 판정점 운영점, UNGATED 배열 규모 축 측정)" + G_D2 + **"[운영점 정합 강건]" "[K 상한 강건]"**.
- **UMi28 — (T+)**: "Nr 8→32 에서 V1 의 genie 격차 회수율(b\* 대비 상대 격차)이 커진다 (UMi28, 동일예산 1.6e5, b\* 판정점 운영점, UNGATED 배열 규모 축 측정)" + G_UMi28 + **"[운영점 정합 강건]" "[K 상한 민감: 외삽 불가]"**.

**문장 조건 (§2.1; §6.1 :545–548)**:
- **S_D2 성립** ((T+) ∧ `NR32B16e4` 표 B (i)): "D2 에서 배열이 8→32 로 커질 때 V1 이 (b\* 대비 상대 격차로) genie 쪽으로 이동하고 b\* 와 멀어진다 (측정, UNGATED, 셀·예산·prior 한정)" + G_D2 + "[운영점 정합 강건]" "[K 상한 강건]". 병기 (보고 전용) 절대 격차 ΣF_V1 − ΣF_g: C2 363 [90% 332, 396] → C9 206 [90% 182, 231] (`primary_D2_L90:8,7`).
- **S_UMi28 성립** ((T+) ∧ `U28NR32B16e4` 표 B (i)): "UMi28 에서 배열이 8→32 로 커질 때 V1 이 (b\* 대비 상대 격차로) genie 쪽으로 이동하고 b\* 와 멀어진다 (측정, UNGATED, 셀·예산·prior 한정)" + G_UMi28 + "[운영점 정합 강건]" "[K 상한 민감: 외삽 불가]". 병기 절대 격차: C2 497 [90% 461, 532] → C9 472 [90% 437, 505] (`primary_U28_L90:8,7`).
- **공동 문장 (S_D2 ∧ S_UMi28 — 조건 충족)**: "두 데이터셋(D2·UMi28) 모두에서 배열이 8→32 로 커질 때 V1 이 (b\* 대비 상대 격차로) genie 쪽으로 이동하고 b\* 와 멀어진다 (측정, UNGATED, 셀·예산·prior 한정)" + G_D2 + G_UMi28 + 데이터셋별 한정어 (D2 "[운영점 정합 강건]" "[K 상한 강건]"; UMi28 "[운영점 정합 강건]" "[K 상한 민감: 외삽 불가]"). 등록은 "두 데이터셋 모두 …" 까지만 고정 — 나머지 문구는 S_d 문구를 그대로 합친 것. "적어도 하나" 문장은 쓰지 않는다; 데이터셋을 합치지 않는다.

### 21.2 2차 단계 (90 %, 보정 없음, 단계마다 독립; 큰 Nr 셀이 spec 1; §6.1.2 :550–561)

| 단계 | R1 [90%] | R2 [90%] | 차 [90%] · p | 라벨 | 출처 |
|---|---|---|---|---|---|
| D2 S1 (8→16) | — | — | 기록값 +0.314 [90% +0.251, +0.381] | **"D2 8→16 (기록값, 채점 없음)"** | 등록 §0.1·§2.2 |
| D2 S2 (16→32) | C9 0.811 [0.790, 0.832] | `raw_NR16B16e4` C6 −3/0/+3 (277 · 82 · 40) 0.823 [0.774, 0.874] | −0.012 [−0.067, +0.041] · p 0.7200 | **"D2 16→32 판정하지 못함"** | `scale2_step_D2_S2:3–6` |
| UMi28 S1 (8→16) | C6 0/+3/+6 (824 · 636 · 170) 0.287 [0.252, 0.322] | C2 0.150 [0.108, 0.190] | +0.137 [+0.085, +0.193] · p 0.0000 | **"UMi28 8→16 증가"** | `scale2_step_U28_S1:3–6` |
| UMi28 S2 (16→32) | C9 0.432 [0.401, 0.463] | C6 0.287 [0.252, 0.323] | +0.145 [+0.099, +0.193] · p 0.0000 | **"UMi28 16→32 증가"** | `scale2_step_U28_S2:3–6` |

- 요약 문구 (§2.2): UMi28 은 두 단계 모두 "증가" → **"UMi28 단조 증가"**. D2 는 S2 가 "판정하지 못함" 이라 "D2 단조 증가" 를 붙이지 않는다. 단계가 쓰는 셀의 가드 발동 없음.
- D2 C6 의 등록 CI = `step_D2_S2:4` 의 R2 줄 0.823 [90% 0.774, 0.874] (등록 §0.1 표 [0.771, 0.871] 와 셋째 자리 다름; 파일 값이 등록값).
- R\* 단계 (보고, 라벨 없음): D2 S2 R\*1 − R\*2 = +0.102 [90% +0.030, +0.175], p 0.0180 (R\* C9 0.909 [0.860, 0.959], D2 C6 0.806 [0.752, 0.860]); UMi28 S1 +0.087 [90% −0.042, +0.216], p 0.2910; UMi28 S2 +0.252 [90% +0.140, +0.352], p 0.0000 (`step_*:10–12`).

### 21.3 셀별: 표 B `b* → V1` · 𝔅 12 · "전부" 문장 (새 3 셀; §6.1.3 :563–644)

| 셀 | 판정점 | 점별 a:b (부호검정 p) | pooled | 라벨 (§2.3 문자열) | SNR@0.1 짝 격차 b\* − V1 [90%] | 출처 |
|---|---|---|---|---|---|---|
| D2 C9 (Nr 32) | −9/−6/−3 | 641:16 (1.6e-166) · 198:9 (1.6e-47) · 75:4 (5.2e-18) | 914:29 (3.7e-229) | **(i) "D2 C9 (Nr 32) 에서 V1 이 b\* 보다 적게 실패 (배열 규모 축 측정, UNGATED)"** | +2.99 dB [+2.72, +3.25] | `tables_D2_NR32B16e4:305–310` |
| UMi28 C6 (Nr 16) | +0/+3/+6 | 114:26 (2.4e-14) · 81:11 (2.5e-14) · 37:7 (5.3e-06) | 232:44 (5.1e-32) | **(i) "UMi28 C6 (Nr 16) 에서 V1 이 b\* 보다 적게 실패 (배열 규모 축 측정, UNGATED)"** | +1.41 dB [+1.08, +1.67] | `tables_D2_U28NR16B16e4:308–313` |
| UMi28 C9 (Nr 32) | −3/+0/+3 | 173:13 (7.3e-37) · 136:12 (9e-28) · 82:7 (2.4e-17) | 391:32 (1.3e-79) | **(i) "UMi28 C9 (Nr 32) 에서 V1 이 b\* 보다 적게 실패 (배열 규모 축 측정, UNGATED)"** | +2.29 dB [+1.98, +2.61] | `tables_D2_U28NR32B16e4:308–313` |

(모두 POWERED, second arm fewer 3/3.)

**b\* + 𝔅 12, 표 B `X → V1`** — 칸 = pooled a:b · 라벨 · R_X 판정점 [90%] (`pairB_<T>.txt:4–94` = §6.1 :575–629; 판정점·R_X −3 dB·절대 격차·SNR@0.1 격차는 거기에)

| X | D2 C9 (`pairB_NR32B16e4`) | UMi28 C6 (`pairB_U28NR16B16e4`) | UMi28 C9 (`pairB_U28NR32B16e4`) |
|---|---|---|---|
| b\* (M-ours-bstar) | 914:29 · (i) · 0.811 [0.790, 0.832] | 232:44 · (i) · 0.287 [0.253, 0.322] | 391:32 · (i) · 0.432 [0.402, 0.462] |
| M-ours-bstar-scalar | 1071:25 · (i) · 0.835 [0.817, 0.853] | 282:33 · (i) · 0.348 [0.314, 0.381] | 424:21 · (i) · 0.461 [0.432, 0.489] |
| M-ours-gmm32 | 422:8 · (i) · 0.924 [0.898, 0.949] | 375:33 · (i) · 0.423 [0.390, 0.455] | 574:22 · (i) · 0.539 [0.512, 0.565] |
| R0-pilot@1 | 823:0 · (i) · 0.986 [0.977, 0.994] | 869:0 · (i) · 0.781 [0.760, 0.801] | 903:0 · (i) · 0.793 [0.774, 0.813] |
| R1-turbo | 579:1 · (i) · 0.980 [0.967, 0.992] | 577:3 · (i) · 0.702 [0.675, 0.728] | 743:4 · (i) · 0.759 [0.736, 0.781] |
| R2-ours-G | 543:5 · (i) · 0.941 [0.920, 0.960] | 559:20 · (i) · 0.536 [0.508, 0.564] | 507:8 · (i) · 0.680 [0.651, 0.710] |
| R3-bigamp | 1107:0 · (i) · 0.993 [0.988, 0.998] | 2110:0 · (i) · 0.962 [0.955, 0.969] | 2612:0 · (i) · 0.917 [0.909, 0.926] |
| R4-llr | 1246:2 · (i) · 0.994 [0.989, 0.998] | 936:0 · (i) · 0.959 [0.948, 0.970] | 1584:2 · (i) · 0.871 [0.857, 0.883] |
| R4-scvamp | 730:1 · (i) · 0.984 [0.974, 0.993] | 807:1 · (i) · 0.768 [0.746, 0.789] | 812:3 · (i) · 0.775 [0.753, 0.795] |
| bstar-pilot | 430:12 · (i) · 0.925 [0.898, 0.949] | 332:31 · (i) · 0.392 [0.360, 0.424] | 509:20 · (i) · 0.509 [0.481, 0.535] |
| V1-pilot | 1222:41 · (i) · 0.496 [0.480, 0.513] (R_X −3 dB undefined: out of range, −3 dB BLER 0.0047) | 154:22 · (i) · 0.221 [0.188, 0.254] | 199:28 · (i) · 0.266 [0.233, 0.300] |
| ALD-pilot | 1276:25 · (i) · 0.859 [0.842, 0.874] | 434:33 · (i) · 0.463 [0.431, 0.493] | 369:25 · (i) · 0.422 [0.391, 0.451] |
| ALDv-pilot | 1244:27 · (i) · 0.855 [0.838, 0.871] | 348:41 · (i) · 0.397 [0.364, 0.430] | 348:31 · (i) · 0.402 [0.371, 0.432] |

(모든 줄 (i) 3/3, POWERED=True, first arm fewer 0/3.)

| 셀 | SUMMARY-B (𝔅 12) (i) · (ii) · 판정 못함 | 13 개 (b\* + 𝔅 12) | X\* (−3 dB 실패 최소) · R_X\* −3 dB [90%] | "전부와 멀어진다" 조건 (k = 13, (ii) = 0, R_X\* CI 하한 > 0) |
|---|---|---|---|---|
| D2 C9 | 12 · 0 · 0; b\* → V1 (i) | 13 · 0 · 0 | V1-pilot (F = 12) · undefined (out of range) | **NOT met** |
| UMi28 C6 | 12 · 0 · 0; (i) | 13 · 0 · 0 | M-ours-bstar (F = 752) · 0.228 [0.190, 0.266] | **MET** |
| UMi28 C9 | 12 · 0 · 0; (i) | 13 · 0 · 0 | V1-pilot (F = 440) · 0.259 [0.216, 0.301] | **MET** |

(§6.1 :631–637 = `pairB_<T>.txt:95–100`.)

- **§2.3 문장 (§6.1 :639–642)**: 𝔅 — 세 셀 모두 k𝔅 = 12, m𝔅 = 0 → **"V1 이 𝔅 12 개 전부보다 적게 실패"** (D2 C9, UMi28 C6, UMi28 C9). **"등록된 baseline 전부(13 개)와 멀어진다"**: **UMi28 C6** "UMi28 C6 에서 등록된 baseline 전부(13 개)와 멀어진다 (이 셀·예산·prior 한정)" + G (UMi28 C6 `U28NR16B16e4` 격자 끝 kron 4096 (4096 멈춤)·tol 정지 22/24); **UMi28 C9** "UMi28 C9 에서 등록된 baseline 전부(13 개)와 멀어진다 (이 셀·예산·prior 한정)" + G (UMi28 C9 `U28NR32B16e4` 격자 끝 kron 4096 (4096 멈춤)·tol 정지 24/24) (G 의 앞부분 문구는 G_d 와 같다). **D2 C9 불충족** — X\* = V1-pilot 의 R_X\* (−3 dB) 가 포화 가드로 정의되지 않음 (−3 dB BLER 0.0047 < 0.005; `pairB_NR32B16e4:79,99,100`).
- **집계 (개수 서술만; §2.4 다중성 문장, §6.1 :644)**: 등록 1차 검정 2 개 (Holm) — D2 (T+), UMi28 (T+). 한정어 2 × 2 는 새 가설이 아니라 캐비엇 규칙. 측정 라벨: 채점 단계 3 (D2 S2 판정하지 못함, UMi28 S1 증가, UMi28 S2 증가) + 표 B 3 ((i) 3) + 𝔅 36 ((i) 36, (ii) 0, 판정 못함 0). 등록 사이 보정 없음.

### 21.4 보고 전용 (라벨에 쓰지 않음; §6.1.4 :646–693)

(b) 실패 수 /2560 (genie · V1 · b\* · b\*-scalar; `pairB_<T>.txt:101–105`; 전 arm·전 SNR 과 NMSE@16 중앙값은 각 `pairB_<T>.txt:101–132`):

| 셀 | 격자 | R5-genie | V1 | b\* | b\*-scalar |
|---|---|---|---|---|---|
| D2 C9 | −12/−9/−6/−3/+0/+3/+6 | 347 · 48 · 18 · 4 · 3 · 2 · 0 | 1347 · 224 · 42 · 10 · 7 · 4 · 2 | 2243 · 849 · 231 · 81 · 47 · 23 · 20 | 2303 · 925 · 288 · 109 · 69 · 47 · 31 |
| UMi28 C6 | −3/+0/+3/+6/+9/+12/+15 | 269 · 119 · 38 · 13 · 7 · 3 · 0 | 642 · 367 · 187 · 82 · 33 · 14 · 3 | 752 · 455 · 257 · 112 · 61 · 30 · 13 | 778 · 468 · 293 · 124 · 64 · 33 · 15 |
| UMi28 C9 | −12/−9/−6/−3/+0/+3/+6 | 846 · 423 · 227 · 88 · 30 · 9 · 3 | 2219 · 1068 · 595 · 349 · 180 · 70 · 27 | 2280 · 1207 · 761 · 509 · 304 · 145 · 62 | 2339 · 1255 · 797 · 526 · 326 · 150 · 73 |

(a) R(−3 dB) [90% paired] (`recovery_<T>.txt`): D2 C9 0.922 [0.851, 0.986] (b\* 81 · V1 10 · genie 4); UMi28 C6 0.228 [0.190, 0.266] (752 · 642 · 269); UMi28 C9 0.380 [0.339, 0.421] (509 · 349 · 88). 재사용 셀 기록값: D2 C2 0.470, D2 C6 0.809, UMi28 C2 0.062. SNR 별 R 은 §6.1 :648. (`recovery_<T>.txt` 의 합 CI 와 frontier 의 R1 CI 는 난수 흐름이 달라 셋째 자리가 다를 수 있다 — 예 UMi28 C6 [0.253, 0.322] vs `step_U28_S1:3` [0.252, 0.322]; §6.1.4 (a).)

(c) 절대 격차 (판정점 합, 블록 수, 90 %; frontier `gaps` 줄) ΣF_V1 − ΣF_g / ΣF_b\* − ΣF_g: D2 C9 206 [182, 231] / 1091 [1045, 1135]; D2 C2 363 [332, 396] / 739 [697, 781]; D2 C6 42 [29, 54] / 237 [213, 263]; UMi28 C9 472 [437, 505] / 831 [786, 871]; UMi28 C2 497 [461, 532] / 585 [547, 623]; UMi28 C6 466 [432, 501] / 654 [616, 696] (`step_U28_S2:8` 는 [433, 502] / [614, 696]).

(d) 곡률·λ·F 비 (점추정만; 기록자 산술): **Q_D2 = R_C9 − 2R_C6 + R_C2 = −0.3255915489625336**, **Q_UMi28 = +0.007513429982214187**. λ = ln(ρ_a/ρ_b), ρ = 1 − R: D2 (C9, C2) −0.9560787303601385, (C6, C2) −1.019495436168412; UMi28 (C9, C2) −0.4026289881346652, (C6, C2) −0.17589989619632507. F_b\*/F_V1 (판정점 합): D2 C9 4.2065, C6 3.3780, C2 1.7705; UMi28 C9 1.5993, C6 1.2956, C2 1.1236.

(e) 셀별 ΔF_K · r · c_K (ΔF_K = ΣF_b\*(K/2) − ΣF_b\*(K_max), 판정점 합; §6.1 :664–675):

| 셀 | K_max (b\*) | ΣF_b\*(K/2) · ΔF_K | r | c_K | Δll(K_max − K_max/2) |
|---|---|---|---|---|---|
| D2 C9 | 4096 적합, b\* = kron 2048 (내부) | — (K2 없음) | (참고 −2.7696344624856746, Q-K 미사용) | '-' | (참고 −5.263164111871873) |
| UMi28 C9 | 4096 (격자 끝) | 960 · **+2** | 1.2799495603934918 | inf | 1.844066254837685 |
| UMi28 C6 | 4096 (격자 끝) | 851 · **+27** (ΣF⁺ 788.897, R⁺ 0.247 [90% 0.186, 0.302]) | 0.5652375151090457 | 1.3001064598543197 | 0.9778190402607194 |
| D2 C6 | 4096 (격자 끝) | 272 · **−5** (`[K 상한 강건 (K/2 가 더 낫지 않음, ΔF_K = -5)]`, R⁺ 0.823 [90% 0.767, 0.872]) | 0.3816292958923848 | 1 | 1.1927584262316344 |
| D2 C2 | 1024 (격자 끝, 2048 미적합) | 899 · **+35** | 0.8403499716975932 | 5.2637007373767215 | 3.1769363255249594 |
| UMi28 C2 | 4096 (격자 끝) | 809 · **+9** | 0.43438450740423645 | 1 | 0.25863367414904914 |

(f) last-EMA 태그 (결정 2·13; 판정점 3 점, n = 2560; §6.1 :677–685):

| 셀 | best R_dp [90%] | R_dp(last) [90% paired] (b\* · V1(last) · genie) | 점별 R(last) | `b* last == A` 무결성 줄 |
|---|---|---|---|---|
| D2 C9 | 0.811 [0.790, 0.832] | **0.808 [0.786, 0.829]** (1161 · 280 · 70) | −9 0.782 · −6 0.883 · −3 0.870 | `0 of 1344 (chunk, key) pairs differ -> OK` |
| UMi28 C6 | 0.287 [0.253, 0.322] | **0.278 [0.243, 0.313]** (824 · 642 · 170) | +0 0.259 · +3 0.306 · +6 0.283 | `0 of 1344 … -> OK` |
| UMi28 C9 | 0.432 [0.402, 0.462] | **0.439 [0.409, 0.469]** (958 · 593 · 127) | −3 0.366 · +0 0.496 · +3 0.551 | `0 of 1344 … -> OK` |

(기존 쌍의 역할 민감도: C6 R_dp best/last 0.823/0.806, UMi28 C2 0.150/0.152; D2 C2 는 legacy-last 뿐.)

(g) SNR@0.1 (dB; b\* · V1 · genie): D2 C9 −6.24 · −9.22 · −11.54; UMi28 C6 3.01 · 1.60 · −2.82; UMi28 C9 0.70 · −1.60 · −6.58 (`tables_D2_<T>.txt` SNR@0.1 표).

(h)·(i) ALD 테스트 NMSE (§6.1 :689), GB′ 중앙값 추세 D2 0.464 (C2) / 0.283 (C6) / 0.190461 (C9), UMi28 0.920 (C2) / 0.880615 (C6) / 0.836979 (C9), em_sec·학습 초, 가드 발동률 0 (세 A raw), 시드 산포 캐비엇 (SEEDS16e4) D2 0.011, UMi28 0.028 (§6.1 :691). 계산하지 않은 보고 전용 항목: R\*@0.02, 판정점 합 기준 X\*, σ 범위 밖 질의 비율 (§6.1 :693).

### 21.5 §3 예측 채점 (§6.1.6 :700–724)

적중 13 (1, 2, 6, 7, 8, 9, 10, 11, 13, 15, 16, 17, 18), 빗나감 5 (3, 4, 5, 12, 14); 19 는 경로 기록. 빗나감의 결정하는 수:

| # | 예측 (요지) | 결정하는 수 |
|---|---|---|
| 3 | U28NR16g σ_hi = 0.4994 질량점 | 0.546964149299485 (동결 전 관측, 기채점) |
| 4 | 새 3 셀 b\* = kron 4096 격자 끝; D2 C9 Δll(4096−2048) ∈ [+1.5, +4]; UMi28 C6·C9 ≤ +1.0; full 내부 | D2 C9 b\* = kron 2048 내부 ✗, Δll −5.263164111871873 ✗; UMi28 C6 0.9778 ✓, C9 1.8441 ✗; full 내부 256/256/128 ✓ |
| 5 | UMi28 C6·C9 시행 1 patience, epoch 300–1500; D2 C9 900–3000 epoch | UMi28 C6 662 ✓, UMi28 C9 252 ✗; D2 C9 250 ✗ |
| 12 | Q-K 두 데이터셋 "[K 상한 강건]"; 격자 끝 셀마다 ΔF_K ≤ 0.15·(ΣF_b\* − ΣF_V1) | UMi28 = "[K 상한 민감: 외삽 불가]" (강제) ✗; ΔF_K 부분 (나머지 격자 끝 4 셀) ✓ |
| 14 | 새 36 라벨 (ii) 0; UMi28 C6·C9 "전부" 문장 성립; D2 C9 는 X\* = V1-pilot 이고 V1-pilot → V1 이 (iii)/(iv) 라서 불성립 | (ii) 0 ✓; UMi28 C6·C9 MET ✓; D2 C9 X\* = V1-pilot ✓·불성립 ✓ 이나 V1-pilot → V1 = (i) 1222:41 ✗ (불성립 사유는 R_X\* 정의 불가) |

- 경로 19: (b) 발동 — UMi28 Q-K 강제 (r ≥ 1, BLER 전 확정); (a)(c)(d) 미발동; (e) 이 등록 밖 (SPARSE-scale 결과 없음). 격자·K 를 늘리지 않았다.

### 21.6 캐비엇·공개 (등록 기록 그대로)

- **작성 시점 공개 (등록 머리말)**: 이 등록의 선택은 모두 사용자 위임 (`DECISIONS.md` [2026-09-30 15:09 KST], 커밋 6b1de688: "2단계는 그냥 진행하도록 해") 아래 작성자·주 세션이 한 것이고 (결정 1–15), 사용자가 항목별로 승인한 것이 아니다. 작성자는 0단계 탐침·1단계 파일럿 6 셀 (V1 포함, 개발 시행)·재사용 3 셀의 모든 수치를 본 뒤 썼다; **한정어 Q-OP 의 R\*·기준값 0.05 와 한정어 Q-K 의 형태 (c_K, 우선순위) 는 그 수치를 본 뒤 정했고, D2 C2 끝의 큰 c_K (= 5.264) 가 D2 의 Q-K 를 '강건' 쪽으로 기울인다** (라벨 문구는 바꾸지 않음). **D2 의 (T+) 는 이미 예상되는 결과였다** (R_C2 0.509, R_C6 0.823 기록값, 파일럿 C9 0.829; 결정 1) — D2 의 새 정보는 2차 S2 (16→32) 에 있다. 추세 검정 등록은 캠페인 최초이고 1차의 한쪽 끝 (C2 두 셀) 은 이미 알려진 값이다. 새 3 셀의 테스트 시행은 BLER 로 쓰인 적이 없다 (σ 격자 측정이 테스트 시행 0..63 을 Gaussian 수신기로 돌림 — BLER 미기록, 38901 §0 관례).
- **격자 끝·수렴 캐비엇 (§6.1.7)**: UMi28 C6·C9 의 b\* = kron 4096 (4096 멈춤); 재사용 UMi28 C2·D2 C6 kron 4096 (4096 멈춤), D2 C2 kron 1024 (2048 미적합; B32e4 §0). D2 C9 는 내부 (적합 최대 kron 4096 의 병합 ll_val 237.47394470961802 < kron 2048 242.7371088214899) → K2 태그 없음, Q-K 의 C9 자리 '-'. 수렴 캐비엇 (C6 §6.5 형): 새 3 셀 tol 정지 24/24 · 22/24 (patience 2) · 24/24.
- UMi28 C6 판정점 0/+3/+6 → 아래로 한 점 (−3 dB) 여유; −9/−6 dB 는 격자 밖이라 측정되지 않음.
- UMi28 Q-K 강제 처리: 스크립트는 강제 머리말 줄 `# Q-K: … (forced …)` 을 쓰지 않았다; 강제 표시는 frontier 의 R1⁺ 줄과 `n/a (Q-K undefined)` 줄에 있다. `--ck inf` 분기는 이 실행에서 처음 쓰였다. D2 Q-K 의 "(K/2 가 더 낫지 않음, ΔF_K = …)" 병기는 C9 가 K_max 내부라 붙이지 않았다 (감사: §1 정의에 따른 것, 오류 아님).
- 2차 frontier 명령에 `--level 0.90` 이 없다 (출력의 `(--level 0.9)` = 기본값, 등록 수준과 같음). 재사용 셀 등록 CI 는 이 실행 파일 값이며 §0.1 표와 셋째 자리가 다르다 (예고된 난수 소비 차이). 첫 K = 4096 청크의 워커 RSS 는 기록되지 않았다 (§1 이 요구한 측정 미수행, 복구 불가; G = 8.0 인상·OOM 없음). run_manifest 의 config_hash 는 prior·arm·ckpt 를 담지 않아 데이터셋이 다른 태그끼리 같은 경우가 있다 (`run_manifest.py:83`).
- 재사용 σ `NR32`·`U28NR32` 는 옛 C9 격자 (−15..+15) 에서 쟀다 (§5 기록 노트 7). a1 학습 로그 세 개의 첫 머리줄이 `gpu_sched.sh` 의 stdout 두 줄로 덮였다 (§5 기록 노트 3; `# sigma grid`·`# data`·`# done` 줄은 온전, 수치 영향 없음). 같은 셀의 `_a2`/`_a3` 체크포인트는 이 등록 밖 (§5 기록 노트 9).
- **금지 문구 (등록 §2.4 그대로)**: "모든 baseline" 은 SPARSE-scale 부속 결과 전까지 쓰지 않는다 ("등록된 13 개" 로만); (T0)·(T0-Holm)·(iii)·(iv) 에서 "비긴다"·"동등" 을 쓰지 않는다; 빗나간 결과에 해석 문구를 붙이지 않는다; 셀·예산·prior 한정 없는 문장, G_d 없는 (T±)·S_d 문장을 쓰지 않는다; "genie 쪽으로" 는 R 이 상대 통계량임을 붙여 쓴다. p 값은 서술용; 1차는 Holm 규칙, 2차·𝔅 는 보정 없음.
- 선행 탐색 (판정 없음): 0단계 탐침 EXPERIMENTS 행 `2026-09-30 00:40 ~ 01:55 KST (텍사스 09-29 10:40 ~ 11:55 CDT)`·`2026-09-30 02:44 ~ 05:57 KST (텍사스 09-29 12:44 ~ 15:57 CDT)` (탐색 전용, `results/scale/STAGE0.md`); 1단계 파일럿 (N = 1e4, 개발 시행 2560..3839, 보고 전용; `results/scale/STAGE1.md`, 등록 §0.2).
- §4.1 이관분 (첫 청크 시간·RSS·메모리 가드) 은 §0–§5 편집 금지 규칙에 따라 §6.1.5 에 적혔다; eval 전체 45 h 33 min (§1 추정 상한 ≈ 60–200 h).

## 22. 시드 강건성 3: Nr 16/32 (SEEDSNR16e4; SCALE16e4 새 3 셀, 동일예산 1.6e5)

**EXPERIMENTS.md 행**: `2026-10-04 13:03 ~ 10-05 12:53 KST (텍사스 10-03 23:03 ~ 10-04 22:53 CDT)`. 등록 `conf/results/review_next/NEXT_EXPERIMENTS_SEEDSNR16e4.md` v2 (동결 cd85bef1, 브랜치 scale), 실행 커밋 1 d59b4c6c (1 묶음: chkS + 5 시드) · 실행 커밋 2 b53a8529 (2 묶음 `--resume`: chkS2 + NR32B16e4s3), 결과 §6.1 (:159–339), 기록 감사 §6.2 (:341–348; `prereg_audit_2026-10-04/audit_SEEDSNR16e4.md` — 540 + 99 검사 불일치 0, 규칙 위반 0, 위생 정정 3 + §0–§5 상태 칸 4 반영). 결과·문서 파일은 scale c689a935 에서 main 으로 사본 (코드 `run_seedsnr16e4.sh` 는 NSCALE 동결 때문에 NSCALE 끝난 뒤 병합).

공통: a1 = SCALE16e4 §21 의 판정 태그 (인용), a2·a3 = 확산 시드 (등록 전 학습, BLER 미평가); 각 시드 태그는 a1 판정점 3 점·A 의 11 arm, 테스트 시행 0..2559, n = 2560/점; 비-V1 10 arm 은 a1 과 비트 동일 (수용 `--ref-arms all`, 6/6). D2 C9 a3 는 원 시행 발산 → 등록 §3d 사다리 시행 2 (fb2, 클리핑 1.0) 사용, fb3 미사용.

**시드별 표 B `b* → V1` 과 R_dp [90% paired]** (§6.1.2 :221–235, 표 :223–233; R_dp = `recovery_ci` 판정점 합, B 2000 seed 20260926)

| 셀 · 시드 | 판정점 | pooled a:b | 라벨 | R_dp [90%] |
|---|---|---|---|---|
| UMi28 C6 (Nr 16) a1 (인용) | +0/+3/+6 | 232:44 | (i) | 0.287 [0.253, 0.322] |
| UMi28 C6 a2 | 〃 | 230:54 | **(i)** | 0.269 [0.231, 0.305] |
| UMi28 C6 a3 | 〃 | 238:47 | **(i)** | 0.292 [0.255, 0.328] |
| UMi28 C9 (Nr 32) a1 (인용) | −3/+0/+3 | 391:32 | (i) | 0.432 [0.402, 0.462] |
| UMi28 C9 a2 | 〃 | 403:35 | **(i)** | 0.443 [0.412, 0.474] |
| UMi28 C9 a3 | 〃 | 398:27 | **(i)** | 0.446 [0.416, 0.476] |
| D2 C9 (Nr 32) a1 (인용) | −9/−6/−3 | 914:29 | (i) | 0.811 [0.790, 0.832] |
| D2 C9 a2 | 〃 | 909:22 | **(i)** | 0.813 [0.790, 0.834] |
| D2 C9 a3 (§3d fb2) | 〃 | 899:31 | **(i)** | 0.796 [0.774, 0.816] |

(모두 POWERED, second arm fewer 3/3, first arm fewer 0/3. 셀마다 R_dp 산포 (a1 포함): 0.023 / 0.014 / 0.017 (§6.1.5 (e) :297).)

**시드 강건성 라벨** (§6.1.3 :237–245; 분모 3 = a1·a2·a3)

| 셀 | 등록 라벨 (문자열 그대로) | 선례 규칙 라벨 (보고 전용, 라벨로 쓰지 않음) |
|---|---|---|
| UMi28 C6 (Nr 16) | **"시드 강건 (3/3 (i))"** | 같음 |
| UMi28 C9 (Nr 32) | **"시드 강건 (3/3 (i))"** | 같음 |
| D2 C9 (Nr 32) | **"시드 강건 (3/3 (i); a3 = §3d fb2)"** | "판정하지 못함 (2/3 (i), 1 판정 못함)" (선례 SEEDS16e4·SEEDS3 는 사다리 없이 원 시행 발산 = 판정 못함) |

**문장 조건** (§6.1.4 :247–275; 라벨 아님)
- (S1) 세 셀의 SCALE16e4 표 B 문장에 "(확산 시드 3/3)" (D2 C9 는 "(확산 시드 3/3; a3 = §3d fb2 클리핑)") 이 붙는다.
- (S2) SCALE16e4 1차 (T+) 의 C9 시드 교체 (dR = R_C9(시드) − R_C2(a1)): D2 a2 +0.304 [95% +0.256, +0.357], a3 +0.287 [95% +0.239, +0.341] → "유지 2/2 (a3 = §3d fb2)"; UMi28 a2 +0.292 [90% +0.243, +0.344], a3 +0.296 [90% +0.247, +0.347] → "유지 2/2".
- (S3) UMi28 S1 "증가" 의 C6 시드 교체: a2 +0.119 [90% +0.064, +0.175], a3 +0.142 [90% +0.085, +0.197] → "유지 2/2".

**§3 예측** (§6.1.6 :305–323): 적중 10, 빗나감 2 — 3 (예측 문자열에 사다리 한정어 없음; 굵은 조건 "a2·a3 모두 (i)" 은 성립), 9 (D2 C9 a2 R_dp 0.813 ≥ a1 0.811).

**캐비엇·공개** (§6.1.7 :325–339, 등록 기록 그대로 요약)
- 두 묶음 구조; 2 묶음 `--resume` 이 1 묶음 5 태그의 뒤 단계 (tables·accept·recovery 등) 를 다시 돌려 그 파일 머리말 git 은 b53a8529 (raw `run|git` 은 d59b4c6c). 같은 raw 의 결정적 재계산이며 로그 50 줄 쌍·config_hash 동일.
- §3d 적용은 등록 규칙이며 선례 (사다리 없음) 와 다르다 — 라벨 문자열의 한정어와 선례 규칙 병기가 그 표시다.
- 공개: 봉인된 fb3 학습 로그의 마지막 학습 줄을 주 세션 브리핑이 14 회 (동결 전 10 · 뒤 4) 출력했고, 설계 서브에이전트가 1 회 (fb2 사용 결정 뒤) 읽었다. 시행 선택은 번호 규칙 (fb2 가 발산하지 않으면 fb2) 이라 영향 없음; fb3 체크포인트·sha·BLER 은 보지 않았다.
- D2 C9 두 시드 태그의 메모리 가드 jobs = 98 (a1 99). 판정점 밖 점·V1 SNR@0.1 은 측정하지 않음.


## 23. 동일예산 N 확장: C2 6.4e5·1.28e6, C6 6.4e5 (NSCALE; 보고 전용 kron 8192)

**EXPERIMENTS.md 행**: `2026-10-06 22:11 ~ 10-07 05:06 KST (텍사스 10-06 08:11 ~ 15:06 CDT)`. 등록 `conf/results/review_next/NEXT_EXPERIMENTS_NSCALE.md` v7 (동결 2d50dab5, main), §5 = 실행 커밋 68d4d353, 결과 §6.1 (:330–650), 기록 감사 §6.2 (:652–; `prereg_audit_2026-10-06/audit_NSCALE.md`, MUST 0 · SHOULD 4 · NIT 5 반영). `NSCALE_DONE ok=89 fail=0`, 수용 16/16 OK.

공통: D2, 테스트 시행 0..2559 (n = 2560/SNR, 이전 모든 예산과 같은 시행), BLER@16, 동일예산 (GMM 적합과 확산 prior 학습이 같은 N′ 채널 집합). 새 점의 V1 은 attempt 1 (`_best` 가 판정 태그, last-EMA 는 보고 전용), b\* 는 세 점 모두 kron 4096 = K 격자 끝 (상한) — 등록된 Q-K 한정어 대상 (§6.1.2). C2 새 점의 D1 형제 게이트 PASS, C6 는 UNGATED (게이트 없음).

**P1 — 새 예산 점별 표 B `b* → V1`** (§6.1.1 :433–448; 판정점 −3/+0/+3 dB)

| 셀 · N′ (태그) | 게이트 | pooled a:b | 라벨 | SNR@0.1 격차 b\* − V1 [90% paired] |
|---|---|---|---|---|
| C2 6.4e5 (`B64e4`) | PASS | 394:70 | **통과** (POWERED, 3/3) | +1.24 dB [+1.06, +1.44] |
| C2 1.28e6 (`B128e4`) | PASS | 391:90 | **통과** (POWERED, 3/3) | +1.10 dB [+0.92, +1.30] |
| C6 6.4e5 (`NR16B64e4`) | UNGATED | 189:23 | **(i)** — R(−3 dB) 0.779 [0.707, 0.850] → "기하 효과 대부분 유지" | n/a (두 arm 모두 −3 dB 에서 0.1 아래; 격자 밖) |

**예산 곡선 (C2 −3 dB BLER 와 R = (ΣF_b\* − ΣF_V1)/(ΣF_b\* − ΣF_genie), −3/0/+3 합; §6.1.5 (a) :510–528, 기준점 행은 등록 §0.1·§0.2 그대로)**

| 셀 · N′ (raw, 가중치) | b\* | b\* −3 dB | V1 −3 dB | 표 B pooled | R [90% paired] |
|---|---|---|---|---|---|
| C2 1e4 (`raw_B1e4`, last-EMA; 게이트 FAIL = 예산 축 측정) | kron 512 | 0.252 | 0.145 | 502:72 | 0.540 [0.506, 0.576] |
| C2 4e4 (`raw_B4e4k`, last-EMA; 게이트 FAIL) | kron 2048 (끝) | 0.248 | 0.145 | 459:79 | 0.518 [0.481, 0.554] |
| C2 1.6e5 (`raw_B16e4k`, 헤드라인 legacy-last) | kron 1024 | 0.243 | 0.145 | 454:78 | 0.509 [0.470, 0.544] |
| C2 3.2e5 (`raw_B32e4`, `_best`) | kron 4096 (끝) | 0.238 | 0.146 | 421:69 | 0.495 [0.457, 0.532] |
| **C2 6.4e5 (`raw_B64e4`, `_best`)** | kron 4096 (끝) | 0.231 | 0.145 | 394:70 | 0.477 [0.439, 0.515] |
| **C2 1.28e6 (`raw_B128e4`, `_best`)** | kron 4096 (끝) | 0.228 | 0.145 | 391:90 | 0.453 [0.413, 0.493] |
| C6 1e4 (`raw_NR16run2`, last-EMA) | kron 128 | — | — | 266:13 (i) | 0.858 [0.818, 0.899] |
| C6 1.6e5 (`raw_NR16B16e4`, §3d fb2 `_best`) | kron 4096 (끝) | — | — | 213:18 (i) | 0.823 [0.772, 0.874] |
| **C6 6.4e5 (`raw_NR16B64e4`, `_best`)** | kron 4096 (끝) | 0.062 | 0.020 | 189:23 (i) | 0.779 [0.722, 0.836] |

(새 점의 last-EMA 판 (보고 전용): C2 6.4e5 R 0.486, 1.28e6 R 0.470, C6 6.4e5 R 0.793 — §6.1.5 (i) :566–576. 그림: 논문판 `conference/figures/F16_headline_budget.*` (b) 는 모든 예산을 last-EMA 로 그린다.)

**P2 — 짝 추세 ΔR (1차, Holm m = 2)** (§6.1.2 :449–492; 고정 SNR −3/0/+3, `frontier_ci --paired`, B 2000)

| 셀 | 대비 | ΔR | Holm 순서 · CI | 라벨 |
|---|---|---|---|---|
| C2 | R(1.28e6) 0.453 − R(3.2e5) 0.495 | −0.042 | 첫째 (p 0.044) · 95% [−0.082, −0.001] | **(T−)** + Q-OP·Q-K **'[한정어 판정 불가: 비짝 CI 폭 (L⁰ = (T0))]'** |
| C6 | R(6.4e5) 0.779 − R(1.6e5) 0.823 | −0.043 | 둘째 (p 0.183) · 90% [−0.098, +0.010] | **(T0)** "판정하지 못함 (방향 없음)" |

- C2 (T−) 의 등록 문구 (§2.2 그대로): "N′ 를 3.2e5 → 1.28e6 (4 배) 로 늘릴 때 V1 의 genie 격차 회수율 (b\* 대비 상대 격차) 이 작아진다 (C2, 같은 테스트 시행 짝 비교, b\* 판정점 −3/0/+3 dB, attempt 1 · 학습 집합 1 개 (공개 3·5), D1 형제 게이트 기준 PASS / 새 PASS)" + G_N (b\* = 등록 프로토콜의 GMM, K 격자 끝) + 한정어 두 개 (위 표). 한정어의 L⁰ (비짝) = −0.042 [95% −0.107, +0.024] → (T0) 이라 '판정 불가' (공개 9 가 미리 적어 둔 예상 경로).
- 절대 격차 (ΣF, −3/0/+3 합; §6.1.5 (h) :560–564): C2 ΣF_V1 − ΣF_genie 359 (3.2e5) → 363 (1.28e6), ΣF_b\* − ΣF_genie 711 → 664.

**2차·합성 문장** (§6.1.3–6.1.4 :493–506)
- S1 (3.2e5→6.4e5) ΔR −0.018 [90% −0.050, +0.016], S2 (6.4e5→1.28e6) −0.024 [90% −0.060, +0.011] — 둘 다 "판정하지 못함".
- (E) 데이터 효율: N′ = 1.6e5 로 학습한 V1 (헤드라인 legacy-last) 의 SNR@0.1 이 N′ = 1.28e6 (8 배) 로 적합한 b\* 보다 1.11 dB 낮다 [90% +0.86, +1.36] (raw 사이 비짝). E128 (V1 @ 1e4, 게이트 FAIL) 대 b\* @ 1.28e6: +1.06 dB [90% +0.81, +1.32] (보고 전용).
- **S_N 성립 (C2·C6)**: "D2 C2 에서 동일예산 표 B `b* → V1` 이 N′ = 1e4 … 1.28e6 (128 배) 의 등록된 모든 예산 점에서 '통과'" (1e4·4e4 는 게이트 FAIL = 예산 축 측정); "D2 C6 에서 N′ = 1e4 … 6.4e5 (64 배) 의 모든 예산 점에서 (i) (UNGATED 측정)" — 둘 다 G_N 한정어 (b\* = 등록 프로토콜의 GMM, 격자 끝·tol 정지 점 목록) 와 함께.

**보고 전용 kron 8192** (§6.1.5 (j) :577–585; 어떤 등록 b\* 에도 들어가지 않음)
- B64e4 격자 + kron 8192: 검증 ll Δll(8192 − 4096) = +1.808 → b\* = kron 8192 (`K8 8192 -2.4856244669792424 1`).
- 같은 시행 짝 비교 (V1·genie 는 비트 동일): ΣF_b\*(8192) 816 vs ΣF_b\*(4096) 804, ΔR +0.009 [90% −0.010, +0.028].

**§3 예측** (§6.1.8 :604–627): 적중 13, 빗나감 3 — 2 (C6 Δll(4096−2048) 6.82 ∉ [+0.8, +3.0]), 11 (C2 라벨 (T−), 예측 (T0)), 17 (K8: ΣF_b\*(8192) 816 > 804), 제외 1 (동결 전 확인).

**캐비엇·공개** (§6.1.9–6.1.10 :629–650, 등록 기록 그대로 요약)
- 세 새 점 모두 b\* = kron 4096 = 격자 끝, C6 6.4e5 의 kron 4096 은 tol 정지 (274/260); N′/K (상한 4096): C2 3.2e5 78 → 1.28e6 312, C6 1.6e5 39 → 6.4e5 156 (공개 11).
- 새 학습 집합은 기존 집합을 포함하지 않는 독립 추출 (공개 5); 기준 C6 1.6e5 는 §3d fb2 가중치 (공개 7); 시드 분산은 부트스트랩에 없음 (공개 3); Q-K·Q-OP·(E) 는 비짝 (공개 9).
- 첫 청크 RSS 는 기록되지 않음 (편차). §5 채움 02:06 CDT → §5 커밋 08:11 CDT (사이 S5 불변).

## 24. 헤드라인 셀 V4 → V1 짝 검정 (SITE16e4, 규칙 고정 사후 계산)

**EXPERIMENTS.md 행**: `2026-10-09 13:08 ~ 13:09 KST (텍사스 10-08 23:08 ~ 23:09 CDT)`. 새 BLER 없음 — 기존 raw (`raw_B16e4k`) 위의 계산이며 작성자가 두 arm 의 BLER 표·실패 수를 먼저 봤다 (**"규칙 고정 사후 계산"**, 사용자 결정 2026-10-08 22:21 CDT; 사전 등록이라 부르지 않는다). 등록 `conf/results/review_next/NEXT_EXPERIMENTS_SITE16e4.md` v2 (동결 = 실행 커밋 9c4b6fe7), 결과 §6.1, 기록 감사 §6.2 (`prereg_audit_2026-10-08/audit_SITE16e4.md`, MUST 0 · SHOULD 1 · NIT 5 반영, 수치 정정 없음). 원본 `conf/results/review_next/pairB_SITEB16e4k.txt`.

공통: D2 C2 (8×4), prior S2, N′ = 1.6e5, 테스트 시행 0..2559 (n = 2560/SNR), BLER@16. 두 arm 은 같은 블록에서 같은 가중치 (`d2sx_N160000_a1.pt`, last-EMA) 를 쓰고 site 만 다르다 — V1 = `M-ours-dscore-C-V1` (행렬 site), V4 = `M-ours-dscore-C-V4` (스칼라 site). 판정점 −3 / 0 / +3 dB 고정 (같은 셀의 b\* 판정점; V4 기준 자동 규칙도 같은 셋). 검정 = 08_SPEC §2 표 B 의 exact 양측 부호검정 (p < .05)·power guard; 이 쌍은 08_SPEC §2 의 쌍 목록 밖이며 이 등록이 더한 것이다.

| 판정점 | 실패 수 V4 · V1 (/2560) | a:b (a = V4 만 실패, b = V1 만 실패) | p | 방향 · p < .05 |
|---|---|---|---|---|
| −3 dB | 394 · 371 | 56:33 | 0.019 | V1 쪽 유의 |
| 0 dB | 96 · 88 | 23:15 | 0.26 | V1 쪽, 유의 아님 |
| +3 dB | 21 · 29 | 6:14 | 0.12 | V4 쪽, 유의 아님 |
| pooled (보고 전용; 라벨에 쓰이지 않음) | — | 85:62 | 0.069 | V1 쪽, 유의 아님 |

- power guard: POWERED (판정점 3 개, 불일치 쌍 89 / 38 / 20, 모두 ≥ 6). V1 쪽 유의 1/3, V4 쪽 유의 0/3.
- **라벨 (iii) "판정하지 못함 (유의 방향 없음)"** (등록 §2 의 문자열 그대로).
- SNR@0.1 격차 (V4 − V1): +0.14 dB [90% paired bootstrap +0.06, +0.23], censored replicates 0%.
- 드리프트 검사 (V4 → V1 계산 전): 같은 코드로 다시 계산한 `b* → V1`·`b* → V4` 의 8 줄이 기록과 글자 단위로 같음 (부호검정·SNR@0.1 4 줄 = `conf/results/tables_D2_B16e4k.txt` :369·:372·:375·:378); 무결성 OK.
- 등록 §2 의 원고 문장 (채운 꼴): `In paired sign tests, the comparison between the \ours{} and the \scdiff{} is not decided.` `The SNR gain $\Delta_{0.1}$ of the \ours{} over the \scdiff{} is 0.14\,dB [$+0.06$, $+0.23$].`
- §3 예측 6/6. 실행 전에 주변 실패 수로 이미 정해져 있던 것 (등록 머리말 공개): a − b = +23 / +8 / −8, SNR@0.1 점추정 +0.14 dB. 이 실행이 새로 정한 것 = 불일치 쌍 수 (p·라벨) 와 bootstrap 구간.
- 범위 = 이 셀·예산·판정점 하나 (C6·다른 예산·다른 쌍은 계산하지 않음). 이 결과는 헤드라인·기존 등록의 판정·라벨을 바꾸지 않는다.
