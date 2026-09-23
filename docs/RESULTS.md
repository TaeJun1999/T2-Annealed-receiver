# 결과 정리 (논문용)

웹에서 해석할 때 가져가는 파일. 표와 수치는 반드시 EXPERIMENTS.md의 행(커밋·설정)을 가리킨다. 해석과 결론은 여기 쓰지 않는다.

- 갱신: 2026-09-23 17:59 CDT (커밋 8cf4b954; 처음에 18:05 CDT 로 잘못 적었던 것을 정정), 기준 커밋 6d56404a. 절마다 초안 작성자와 별도 검증자가 원 결과 파일·EXPERIMENTS.md 행과 대조했다(워크플로 wf_6422f535-670; 검증 메모 원문 `conf/results/review_next/results_md_raw/sections_wf_6422f535.json`).
- 판정 문구는 사전 등록 라벨(지지 / 판정 불가 / UNDECIDED / 기각 / PASS 등) 그대로다. 수치를 인용하기 전에 **§6 인용 주의**를 먼저 읽는다.
- 목차: §1 헤드라인(Stage C, 동일예산) · §2 review_next 진단·ablation · §3 A1 위상 augmentation · §4 P3 반복 루프 규칙 · §5 C6 (Nr=16) · §6 인용 주의

---

## 1. 헤드라인: Stage C, D2 셀 C2 동일예산 비교 (N_train 1e4 / 4e4 / 1.6e5)

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

