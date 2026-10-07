## draftNote
 초안 v1 파일을 만들었습니다: `/home/HTJ/t2_wtS/conf/results/review_next/NEXT_EXPERIMENTS_SCALE16e4.md`. 이 파일 외에는 아무것도 쓰지 않았고, 커밋·GPU·수신기 실행은 하지 않았습니다. SEEDS3·HISNR 출력도 열지 않았습니다. 형식은 SUPP16e4·C6B16e4 와 같게 제목, 머리 목록(작성·틀·작성 시점 공개), 목적, §0–§6 순서입니다. `{{NOW}}` 는 세 곳(작성 줄, §0.5, §4.1)에 넣었습니다.

**핵심 선택 (합성 설계 그대로)**
- **지위**: UNGATED "배열 규모 축 측정"입니다. 캠페인에서 추세 검정을 등록하는 것은 처음이라는 점과, C2 쪽 끝값은 이미 알려져 있다는 점을 공개했습니다.
- **재사용 3 셀**: B16e4k 0.509, NR16B16e4 0.823, U28B16e4 0.150 입니다. 셋 모두 recovery 파일과 대조해 맞는 것을 확인했습니다.
- **새 3 셀**: NR32B16e4, U28NR16B16e4, U28NR32B16e4.
- **1차 통계량**: 판정점 3 점 합으로 구한 R_dp 의 ΔR = R_C9 − R_C2 입니다. 비짝 부트스트랩(B 2000, seed 20260926)을 쓰고, Holm m = 2, FWER 0.10 입니다.
- **한정어 두 개** (1차 라벨은 바꾸지 않음):
  - Q-OP: R\*@0.05 로 운영점을 맞춘 값
  - Q-K: 시행별 외삽 e⁺ = 2·e(K) − e(K/2) 와 K/2 태그
- **SNR 격자**: C9 는 −12..+6 으로 CELLS 를 바꿉니다. UMi28 C6 는 C6 셀 격자 −3..+15 를 씁니다.
- **σ 격자**: 합격 조건은 σ_hi ≥ σ_t1(s_min) 이고, 측정 집합에 {s_min−3} guard 점이 들어가야 합니다. NR32 와 U28NR32 는 재사용하고, U28NR16g 는 새로 측정합니다.
- **arm**: 새 셀마다 11 arm + PIL + ALD + K2 + chk 입니다. V0/V4/V4b 는 뺍니다.
- **재사용 셀 추가 실행**: bridge 3 개, K2 2 개.
- **나머지**: 격자 끝 규칙은 kron 4096 에서 멈춥니다. 폴백은 fb2·fb3 병렬입니다. "모든 baseline" 문구는 SPARSE 전까지 쓰지 않습니다. 예측은 19 항목입니다.

**설계에 없던 것을 보탠 곳 (검토 때 확인 필요)**
1. CPU 순서에 "재사용 bridge ×3" 을 넣었습니다. 설계의 순서에는 bridge 가 빠져 있었습니다.
2. 수용 검사 (b) 에 "chk·bridge 는 청크 0 × 1 점" 을 적었습니다.
3. 셀 가드를 "그 셀을 쓰는 통계량"에만 걸리도록 좁혔습니다. C6 가드는 1차가 아니라 2차 단계에만 영향이 갑니다.
4. §4.2 에 3b 를 새로 두었습니다. UMi28 C6(Nr 16) 의 kron 2048·4096 을 어느 EM 경로로 돌릴지 설계가 정하지 않았습니다. 기존 Nr 16 검사는 S2 만 했으므로, `--nr 16 --prior UMi28` 로 검사해 PASS 일 때만 일괄 경로를 쓰자고 작성자 제안으로 적었습니다.

**파일에서 새로 확인한 적합 현황 (§0.5)**
- **UMi28 C6**: 기본 격자와 kron 1024 병합(53.880)이 끝났습니다. kron 1024 가 계열 최대라서 **격자 끝 규칙이 이미 발동**했고, 다음은 kron 2048 입니다. full 계열 최대는 256 으로 내부입니다.
- **D2 C9**: 기본 격자는 끝났고 kron 1024 병합이 큐에 있습니다. full 계열 최대는 256(121.174)으로 내부입니다.
- **UMi28 C9**: kron 128(116.396)과 kron 512(143.616)가 새로 끝났습니다. full 128(80.064)이 full 256·512 보다 크지만 여전히 내부입니다. 나머지 격자는 도는 중이거나 큐에 있습니다.

**열린 선행 조건 (§4.2, 항목마다 결정 규칙을 적음)**
1. D2 C9 kron 1024 병합과 2048/4096 — 격자 끝 규칙으로 정하고, 그 결과가 K2 와 Q-K 를 만들지를 정합니다.
2. UMi28 C9 기본 격자의 나머지.
3. Nr 32 일괄 EM 검사 PASS 여부 (3b 는 위의 Nr 16 경로 문제).
4. UMi28 Nr 16·32 testbed TMXa — FAIL 이면 등록 전에 멈추고 사용자에게 알립니다.
5. U28NR16g 의 실측 σ_hi — 불합격이면 공식대로 올립니다.
6. D2 C9 학습 발산 여부 — §3d 사다리를 따릅니다.
7. C9, K 4096 에서의 arm 별 비용 — 비용 스모크로 정하고, n·arm·K 는 줄이지 않습니다.
8. bridge 비트 동일 여부 — 실패하면 그 셀은 추세에서 빠지고 재실행은 사용자가 정합니다.
9. 1.6e5 에서의 자동 판정점.
10. UMi28 C9 의 R\* 정의 가능성.
11. ALD 조정 격자 끝.
12. SPARSE16e4 동결과 Nr 32 튜닝 규칙.

그 밖에 선행 코드 ①–⑩ 은 아직 구현하지 않았습니다. Fable 적대적 검토, 동결 커밋, §5 기록도 모두 대기 중입니다.


## review stats
 ## 적대적 검토 — NEXT_EXPERIMENTS_SCALE16e4 초안 v1 (통계·추론 렌즈)

대상: `/home/HTJ/t2_wtS/conf/results/review_next/NEXT_EXPERIMENTS_SCALE16e4.md` (전문 읽음). 대조: 01_RULES §5, 08_SPEC §2, C6B16e4·38901·PARETO·SUPP·STATIC·SEEDS·HISNR·B32e4 등록, STAGE0/1, `code/frontier_ci.py`·`recovery_ci.py`·`analysis.py:405-412`·`pair_baselines.py:91`·`ald.py:85`·`Demo/exp_0925_analysis.py:45`, σ 파일 4 개, `conf/raw_B16e4` 메타, 새 fits 디렉터리 3 개. 파일 수정 없음, GPU·BLER 없음, SEEDS3·HISNR 산출물 미열람.

### 반드시 (동결 전 고쳐야 함)

1. **§2.2 2차 라벨표 — D2 에 "증가" 라벨이 없다.** §2.2 첫 행은 "S1·S2 하한이 모두 > 0 → 단조 증가" 인데 D2 는 S1 을 채점하지 않으므로(§2.2 마지막 줄) D2 의 S2 하한 > 0 은 어느 행에도 해당하지 않는다(예측 13 은 "판정하지 못함" 을 기대하지만 반대 결과의 라벨이 비어 있다 = 결과 뒤 라벨을 만들게 됨). 수정 문안: 단계마다 독립 라벨로 바꾼다 — "S1 하한 > 0 → '<d> 8→16 증가'; S1 상한 < 0 → '<d> 8→16 감소'; 그 밖 → '<d> 8→16 판정하지 못함' (D2 는 S1 기록값 0.314 를 채점 없이 인용). S2 도 같은 세 갈래('16→32'). '<d> 단조 증가' 는 두 단계가 모두 '증가' 일 때만 붙이는 요약 문구(D2 는 S1 기록값 + S2 증가일 때)."

2. **§1 한정어 Q-K — ΔF_K < 0 이면 외삽이 '경계' 가 아니라 반대 방향이 된다.** e⁺ = 2e(K_max) − e(K_max/2) 는 K_max 가 K/2 보다 실패가 *많을* 때 b\*⁺ 를 b\* 보다 나쁘게 만들어 R⁺ > R → "[K 상한 강건]" 이 자동 성립한다(한정어의 목적인 GMM 유리 경계가 깨짐). 또 b\*⁺ 가 가드(ΣF ≤ ΣF_g 등)를 건드릴 때의 처리가 없다. 수정 문안: "ΔF_K := ΣF_b\*(K_max/2) − ΣF_b\*(K_max) (판정점 3 점 합, 같은 시행). ΔF_K ≤ 0 이면 b\*⁺ = b\* 로 두고 '[K 상한 강건 (K/2 가 더 낫지 않음, ΔF_K = …)]' 로 적는다. ΔF_K > 0 일 때만 ΣF_b\*⁺ = ΣF_b\*(K_max) − ΔF_K (복제마다 같은 인덱스로 같은 식). b\*⁺ 에서 §1 가드(분모 ≤ 0, 정의 불가 5 %)가 발동하면 '[K 상한 한정어 정의 불가]' 이고 1차 라벨은 그대로." (`--extrap` 구현·항등 검사 ⑤ 에 이 clamp 를 포함.)

3. **§1 한정어 Q-OP — B_V1(s\*)·B_g(s\*) 의 계산법이 없다.** s\* 는 정의됐지만 격자 밖 점 s\* 에서 V1·genie BLER 을 어떻게 얻는지(보간 방식·바닥값), 부트스트랩에서 s\* 를 복제마다 다시 구하는지가 적혀 있지 않다 → 구현자 자유. 수정 문안: "B_V1(s\*), B_g(s\*) 는 s\* 를 감싸는 두 격자점 사이에서 log10 max(BLER, 0.5/n) 을 선형 보간해 10^ 으로 되돌린 값(`snr_at` 과 같은 바닥 0.5/n). 부트스트랩 복제마다 (i) 그 셀의 전 격자점을 (raw, 셀, SNR) 단위로 재표본해 세 arm 에 같은 인덱스 적용, (ii) 재표본 b\* 곡선에서 s\* 를 다시 구하고, (iii) 같은 복제의 재표본 V1·genie 곡선에서 B_V1(s\*)·B_g(s\*) 를 계산. 점추정도 같은 식. 'lo' (첫 점에서 이미 < 0.05)·'hi' (교차 없음)·B_g(s\*) ≥ 0.05 는 정의 불가." 스모크 목표 0.610/0.806/0.218 은 raw 실패 수로 재계산하면 정확히 나온다(아래 확인 5) — "반올림 표값 재계산" 문구를 "raw 실패 수에서 계산" 으로 고치고 허용오차(소수 셋째 자리)를 적는다.

4. **§1 보고 전용·§3 예측 12·13 — Q(곡률)·ΔF_K·λ 가 정의 없이 예측에 쓰인다.** 예측 13 "Q_D2 < 0", 예측 12 "ΔF_K ≤ 0.15·(F_b\* − F_V1)" 는 정의가 없어 채점할 수 없다(사후 정의 = 사후 자유). 수정 문안: "Q_d := S2_d − S1_d = R_C9 − 2R_C6 + R_C2 (점추정, CI 없음, 보고 전용). ΔF_K 는 항목 2 의 정의. λ = ln(ρ_a/ρ_b), ρ = 1 − R 는 (a, b) = (C9, C2) 와 (C6, C2) 두 쌍만, 점추정만."

5. **§1 수용 검사 (b)·(d) — D2 C2 의 K/2 원천 `raw_B16e4` 에 (b) 를 그대로 적용하면 실패한다.** `conf/raw_B16e4` (results/ 아래가 아님) 는 C2 7 SNR × 64 청크, `meta|bstar kron`, `kron_K 512`, `ll_val|kron −14.636106156749378`, 그러나 `em_sec 49597.8` (fits 디렉터리 `gmm_fits_D2_B16e4` 12 파일) 로 `raw_B16e4k` (107957.2, 13 파일) 와 다르다 → (b) "한 셀의 모든 태그에서 fits 실체가 같다" 를 문자 그대로 적용하면 무효, 적용하지 않으면 사후 예외. 수정 문안: "(b) 의 fits 실체 동일 조건에서 `raw_B16e4` 는 제외하고 대신 `meta|kron_K = 512`, `meta|ll_val|kron = −14.636106156749378` (= `gmm_fits_D2_B16e4k` 의 kron 512 ll_val, PARETO §5) 을 확인한다; (d) 의 genie 4 키 비트 동일은 그대로." 경로도 `conf/raw_B16e4` 로 명기(`frontier_ci.raws` 는 `C.CONF/<raw>` 로 푼다).

6. **§4.2 항목 3b (UMi28 C6 kron 2048·4096 의 EM 경로) 가 "검토 항목·작성자 제안" 으로 열려 있다.** 동결 문서에 미결 항목이 있으면 안 된다(BLER 무관이라 위험은 낮지만 §5 기록·수용 (a) 와 연결됨). 수정 문안: 제안대로 확정 — "`em_batched_check_nr.py --nr 16 --prior UMi28` 원 기준 PASS → 일괄, 그 밖 → 정확 경로; 결과와 경로를 §5 에 파일별 기록." 로 §1 EM 경로 행에 넣고 4.2-3b 는 삭제.

### 권고

- **§3 예측 9·10 (D2) 범위 불일치**: R_C2 = 0.509 는 상수이므로 예측 10 의 ΔR_D2 ∈ [+0.18, +0.42] 는 R_C9 ∈ [0.689, 0.929] 인데 예측 9 는 [0.70, 0.92] → R_C9 = 0.695 면 9 빗나감·10 적중. 하나에서 다른 하나를 유도해 일치시킬 것(예: ΔR_D2 ∈ [+0.19, +0.41]).
- **§2.4 "단계 4"** → 채점되는 단계는 3 개(S2_D2, S1_U28, S2_U28); S1_D2 는 기록값. 개수 정정.
- **Holm 둘째의 자동 "판정하지 못함"** 라벨 문구를 "(T0-Holm) 판정하지 못함 (첫째 미판정)" 로 구분 — 둘째의 자체 CI 가 0 을 배제해도 '방향 없음' 으로 읽히지 않게.
- **Q-OP CI 수준**: L\* 를 항상 90 % 로 두면 첫째(95 %) 데이터셋의 한정어가 1차보다 느슨하다. "그 데이터셋의 Holm 수준(첫째 95 %, 둘째 90 %)과 같은 CI" 로 맞출 것.
- **R 은 상대 통계량**: R↑ 은 "b\* 격차 대비 V1 의 genie 격차 비율이 줄었다" 이지 V1 의 절대 genie 격차 감소가 아니다(b\* 가 나빠져도 R 은 오른다). S_d 문장의 "genie 쪽으로 이동" 옆에 "(b\* 대비 상대 격차)" 를 붙이고, 보고 전용에 절대 격차 F_V1 − F_g (판정점 합, 블록 수)와 그 90 % CI 를 추가.
- **재사용 R_dp "소수 셋째 자리 재현"** 은 점추정에 한정한다고 명시 — CI 는 도구별 난수 소비가 달라 `recovery_ci` [0.470, 0.545] vs `frontier_ci` [0.470, 0.544] 로 이미 셋째 자리가 다르다. 등록 CI 는 `frontier_ci --recovery` 것으로 고정.
- **미병합 kron 2048·4096 후보의 ll_val 은 보게 된다** → 38901 §1 문장("미병합 후보는 존재를 §5 에 적고 쓰지 않는다")을 §1 GMM 행에 복사.
- **bridge 실패 → 사용자 재실행 결정** 은 결과 뒤 분기다. 미리 적을 것: "재실행하면 새 태그가 그 셀의 유일한 값이 되고, 원 raw 와의 차이(실패 수·R_dp)를 §6 에 병기; 재실행 없으면 (T-iv) 유지."
- **σ 합격 조건의 등호 통과**는 σ_hi 와 σ_t1(−3) 이 같은 식(√(ν/2), ν = 10^(0.3)/4)으로 계산될 때만 부동소수 등호가 성립한다. 검사는 ν 로 하거나 허용오차(σ_hi ≥ σ_t1 − 1e-12)를 적을 것. U28NR16 표에서 −3 dB 반복 2 중앙값 0.161 이므로 −6 dB 반복 ≥ 2 가 0.4988 을 넘는 표본은 적을 것이고, 99 백분위는 질량점 안에 떨어질 가능성이 크다(등호). 어느 쪽이든 폴백 규칙이 결정론적이라 결과는 같다.
- **MDE 를 적을 것**: SE(R_dp) ≈ 0.023 (C2 D2) · 0.024 (C2 UMi28), C9 도 판정점 실패 수가 크면 ≈ 0.03 → SE(ΔR) ≈ 0.04, 95 % 반폭 ≈ 0.08. 예측 ΔR ≥ 0.18 이면 검정력은 충분; (T0) 가 나오면 "차이 ≤ 0.08 수준" 이 아니라 판정 불가임을 §2.4 에 유지.
- **UMi28 C6 격자 "아래로 한 점 여유"** 는 판정점이 0/+3/+6 일 때만 참이다. 1.6e5 에서 −3/0/+3 이 되면 여유 0 → 문장을 "판정점이 0/+3/+6 이면 한 점 여유, −3/0/+3 이면 여유 없음(격자 확장 없음)" 으로.
- **D2 C2 K=512 arm 의 회귀**: bridge 는 `raw_B16e4k` 만 덮는다. `raw_B16e4` 의 b\*(K 512) 청크 0 을 bridge 에 1 arm 추가(비용 무시 가능)하면 Q-K 의 D2 끝점이 현재 코드와 비트 동일함이 보장된다.
- 부트스트랩 p = 2·min(...) 은 1 로 캡.

### 확인 (근거와 함께 OK)

1. **Holm m = 2, FWER 0.10 양측 → 첫째 95 %, 둘째 90 %, 첫째 미판정 시 둘째 자동 미판정**: Holm 절차와 일치(PARETO §1·§6.2 선례와 동일 문구, `frontier_ci.py` 가 양측 p 를 찍음).
2. **비짝 부트스트랩이 셀 간 독립인 근거**: `common.trial_rng([20260926, 2, PID, Nr, T, Tp, snr+100])` 에 Nr·PID 가 들어가 C2/C9·D2/UMi28 스트림이 다르다(σ 파일 머리말 seed rule 동일). `frontier_ci.Resampler` 는 (raw, 셀, SNR) 마다 인덱스 1 회 → 셀 안 짝·셀 간 독립; 정의 불가 복제는 백분위에서 제외되고 개수가 출력된다 — §1 서술과 코드 일치.
3. **재사용 값**: `recovery_B16e4k.txt` 0.509 [0.470, 0.545] (864/488/125), `recovery_NR16B16e4.txt` 0.823 [0.771, 0.871] (277/82/40), `recovery_U28B16e4.txt` 0.150 [0.110, 0.189] (800/712/215), 판정점 −3/0/+3·−3/0/+3·+3/+6/+9 — §0.1 과 일치. 시드 산포 D2 0.011·UMi28 0.028 은 SEEDS16e4 §6 의 R(3 점 합) 범위(0.509–0.520, 0.150–0.178)와 일치.
4. **파일럿 R_dp 재계산** (STAGE1 실패 수): D2 C9 (695−152)/(695−40) = 0.829, UMi28 C6 (474−354)/(474−81) = 0.305, UMi28 C9 (573−341)/(573−68) = 0.459 — §0.2 일치.
5. **R\*@0.05 스모크 목표**: raw 실패 수로 `snr_at` 규칙(log10 max(BLER, 0.5/n) 선형 보간, 첫 하향 교차)을 적용하면 D2 C2 s\* = 0.93 dB → 0.610, D2 C6 s\* = −2.01 → 0.806, UMi28 C2 s\* = 8.93 → 0.218 (3 자리 일치). 단 UMi28 C2 는 b\*(+9) = 0.0492 가 0.05 바로 아래라 복제의 절반쯤은 교차가 +9..+12 구간으로 튄다 — §0.4 의 "SE 0.061" 과 정합.
6. **판정점 규칙**: `analysis.py:412` `0.005 <= bl <= 0.9`, `abs(log10(bl/0.1))` 최소 3 개, 앵커 = baseline arm — §1 서술 그대로.
7. **셀당 격자 하나**: `pair_baselines.py:91` 과 `ald.py:85` 가 `C.CELLS[cell]["snrs"]` 와 점 집합을 대조 — §0.4 사실 확인. C9 격자는 현재 −15..15 (`common.py:86`) 이고 `DEFAULT_CELLS` 에서 제외 — 동결 커밋에서 −12..+6 으로 바꿔야 한다는 §1 서술과 일치.
8. **σ 격자 수치**: NR32 99 백분위 σ_t 1.740, U28NR32 1.723 ≥ σ_t1(−12) = √(10^1.2/8) = 1.4075; NR16 99 백분위 0.4915 < 0.4994 (99.9 백분위 0.4994 = −3 dB 반복 1 질량점) — "소폭 불합격 공개" 정확; U28NR16 (−3..15) 0.4047 — STAGE1 붕괴 설명과 일치.
9. **새 fits 상태 §0.5**: `gmm_fits_D2_NR32B16e4` full 6 + kron 6 + kron 1024 후보 3(병합 파일 없음), `U28NR16B16e4` kron 1024 병합 완료, `U28NR32B16e4` 부분(full 128/256/512, kron 128/512, 1024 후보 3) + 큐 2 줄 — 문서와 디렉터리 일치.
10. **가드·예측의 반증 가능성**: 판정점 < 3, 분모 ≤ 0, genie ≥ V1, 정의 불가 5 %, 학습 실패, 수용 실패 → (T-iv) 로 닫혀 있고, "한쪽 정의 불가여도 m = 2" 는 보수적. §3 예측은 항목 1·2·4·6 을 제외한 전부가 수치 구간이라 이분 채점 가능(위 반드시 4 만 정의 보강 필요). "결과를 본 뒤 격자·K·arm·n 을 바꾸지 않는다" 가 §1 두 곳·§3-19 에 고정돼 있다.
11. **동일예산·정보 상태 공개**: 새 3 셀 테스트 시행은 Gaussian 수신기의 σ 측정(0..63)만 닿았고 BLER 은 기록하지 않았다는 서술이 38901 §0 관례와 같다; 파일럿 6 셀·재사용 수치·fit ll_val 을 본 뒤 R\*·0.05·Q-K 를 정했다는 공개가 §0·§1 무결성 행에 있다.


## review fair
 **검토 대상**: `/home/HTJ/t2_wtS/conf/results/review_next/NEXT_EXPERIMENTS_SCALE16e4.md` (초안 v1). 아래 근거는 전부 파일·raw·fits 에서 직접 읽은 것이며, SEEDS3·HISNR 산출물은 열지 않았다. 파일 수정 없음.

## 반드시 (must-fix)

1. **§1 「한정어 Q-K」 — 근거 문장 "기록된 모든 사다리에서 두 배당 ll 증분이 줄어든다 (r ≤ 0.46)" 은 사실이 아니다.** 기록된 kron 사다리: B32e4 (3.2e5) 1024→2048→4096 = +3.376 / +2.766 / +1.851 nat → r = 0.82, 0.67 (`NEXT_EXPERIMENTS_B32e4.md` §5); MIX3 +1.792 / +0.964 / +0.469 → r = 0.54, 0.49 (`_38901.md` §5); S2d +2.14 / +1.27 → r = 0.59 (`_ROTMIX16e4.md` §5). D2 C9 자신의 사다리 256→512→1024 = +27.0 / +12.3 → r = 0.46 (경계값; `results/gmm_fits_D2_NR32B16e4/*.npz`). 따라서 "한 번 더 두 배로 외삽한 값은 GMM 쪽에 유리한 경계" 는 성립하지 않는다 (r = 0.82 면 기하 꼬리 r/(1−r) = 4.6 배). 또 "시행별 e⁺ = 2·e_b\*(K_max) − e_b\*(K_max/2)" 는 시행 단위로 {−1,0,1,2} 값을 갖는다.
   **고칠 문장**: "Q-K 는 경계가 아니라 **민감도 분석**이다. 셀마다 r = Δll(K_max − K_max/2) / Δll(K_max/2 − K_max/4) 를 §5 의 ll_val 로 계산(BLER 무관)하고 c_K = max(1, r/(1−r)) 로 둔다. 판정점 3 점 합에서 ΣF⁺ = ΣF_b\*(K_max) − c_K·(ΣF_b\*(K_max/2) − ΣF_b\*(K_max)) (부트스트랩은 같은 시행 인덱스로 이 선형식을 복제마다 계산). r ≥ 1 이거나 ΣF⁺ ≤ ΣF_g 인 복제가 5 % 를 넘으면 Q-K 는 정의 불가이고 (T±) 에 '[K 상한 민감: 외삽 불가]' 를 강제로 붙인다. c_K 와 r 은 §5 에 셀별로 적는다."

2. **§2.1 라벨 문자열에 GMM 프로토콜 한정이 없다.** Nr 32 의 새 fits 는 읽히는 전부가 tol 규칙 정지(n_iter − it_best < patience 40: D2 C9 kron 512 196/190, kron 1024 169/160·재시드 34, UMi28 C6 kron 1024 62/60·재시드 2401, UMi28 C9 kron 512 59/50·재시드 267, full 512 42/40·재시드 14001)이고 K 상한 4096 의 미적합 잔여(1 번 항목의 r) 는 Nr 와 함께 커진다 — 추세 검정의 교란 변수가 축과 같이 움직인다. §5 의 캐비엇 행만으로는 부족하다.
   **고칠 문장**: §2.1 (T+)/(T−) 와 S_d 문장 끝에 고정 한정어를 붙인다: "(b\* = 등록 프로토콜의 GMM — kron K ≤ 4096, 재시작 3, 상한 500·tol 정지 — 이며 최적 GMM 이 아니다; 격자 끝·tol 정지 셀: <§5 목록>)". §5 에 셀별 "tol 정지 파일 수 / 전체" 행을 추가한다.

3. **§1 「수용 검사」(b) 가 K2 태그와 모순된다.** (b) "한 셀의 모든 태그에서 fits 실체가 같다", meta bstar·kron_K·ll_val 일치 — 그러나 K2 는 설계상 K_max/2 링크 집합이라 bstar K·ll_val·em_sec 이 다르고, `eval_accept.py:128` 은 태그 간 (bstar, kron_K, em_sec) 불일치를 FAIL 로 낸다.
   **고칠 문장**: "(b) 는 A·PIL·ALD·chk 에 적용. K2 는 별도 호출 `eval_accept --bstar kron --kron-K K_max/2 --ll-val <ll(K_max/2), 정확한 float> --fits-dir <K2 링크 dir> --grid <K_max 제외 격자> --ref-raw raw_<T>` 로 검사(genie 4 키는 A 와 대조). 재사용 K2 의 기대값: K2NR16B16e4 kron 2048 61.982…(§5 에 정확한 float), K2U28B16e4 kron 2048 5.539276756851168. D2 C2 의 K2 = `conf/raw_B16e4` (실체 확인: 청크 {(40k,40)}×7 SNR 448 파일, meta kron_K 512 · ll_val −14.636106156749378 · ntrain 160000 · 같은 ckpt `d2sx_N160000_a1.pt`, R5-genie 4 키 448 파일 전부 raw_B16e4k 와 비트 동일, b\* 실패 −3/0/+3 = 647/191/61 vs K=1024 623/184/57) — 이 값을 §5 에 미리 적는다."

4. **§1 「실행 위치」·수용 (f): "새 raw 의 run|git 을 동결 커밋 하나로 둔다" 는 불가능하다.** 동결 커밋 뒤에 ⑩ main→scale 병합(`git diff main scale -- conf/code` 는 23 파일; scale 에는 `eval_accept --skip0`·`HISNR_SKIP0`·`run_manifest` HISNR 표기가 없어 병합이 필수)과 §5 커밋이 온다.
   **고칠 문장**: "새 raw 의 run|git = **실행 커밋 하나**(동결 커밋 이후). §5 에 `git diff <동결> <실행> -- conf/code` 의 내용이 ⑩ 병합분과 선행 코드뿐임을 적는다 (38901 §6 선례: 실행 80bae849 = 동결 eee1d669 와 conf/code 동일)."

5. **§0.5·§5 — D2 C9 fits 3 개는 0단계 probeC9 파일의 복사본인데 공개가 없다.** `gmm_fits_D2_NR32B16e4/` 의 full K16, kron K64, kron K256 은 `gmm_fits_D2_probeC9/` 와 sha256 동일(3cef4eeb…, 718afe2d…, 60e1afc9…; 복사 mtime 09-30 06:47:23), `code/run_c9fits.sh` 머리말에만 적혀 있다.
   **고칠 문장**: §0.5 와 §5 격자 행에 "full 16 · kron 64 · kron 256 = 0단계 probeC9 적합 재사용 (같은 fit_gpu.py 프로토콜·시드 튜플, sha256 동일)" 을 적고 수용 (a) 가 sha 로 이를 받아들이게 한다. 같은 자리에서 §0.5 갱신: D2 C9 kron 1024 병합 완료 (240.836799, r2, 169/160, 재시드 34) → 계열 최대 → 2048 발동 확정.

6. **§4.2 항목 4 (testbed TMXa Nr 16·32) 의 순서가 열려 있다 — 동결 전제 조건으로 못 박아야 한다.** 이미 도는 U28NR16B16e4·U28NR32B16e4 적합, 재사용할 σ 격자 U28NR32, 1단계 파일럿이 모두 `mix3.py` 의 새 보정 상수(P_RAW (UMi28,16,4) 0.99051…, (UMi28,32,4))에 서 있다. TMXa 가 FAIL 이면 상수가 바뀌고 이 모두가 무효인데, 초안은 σ 재사용·적합 진행을 TMXa 앞에 둔다.
   **고칠 문장**: §1 「실행 순서」 첫 줄에 "④ 구현 → TMXa Nr 16·32 PASS (허용오차는 38901 §0 과 동일, 실행 전 고정) 가 **동결 커밋의 전제**; FAIL 이면 fits·σ·파일럿을 모두 폐기하고 사용자에게 알린다" 를 넣고 §5 testbed 행에 "PASS 시각 < 동결 커밋 시각" 을 요구한다.

## 권고 (should)

- **D2 1차는 사실상 결정돼 있다**: R_C2 = 0.509 [0.470, 0.545] 와 R_C6 = 0.823 [0.771, 0.871] 이 모두 기록값이고 파일럿 C9 = 0.83 이라, D2 의 새 정보는 R_C9 하나뿐이며 ΔR_D2 = R_C9 − R_C2 의 (T+) 는 C9 붕괴가 없는 한 예정된 결과다. §1 목적과 §2.1 에 "D2 의 (T+) 는 C6 등록값으로 이미 예상되는 결과이고 D2 의 새 정보는 2차 S2 (16→32) 에 있다" 를 명시하거나, D2 만 1차를 R_C9 − R_C6 로 두는 안을 검토(비대칭이 싫으면 전자).
- **역할 비대칭**: D2 추세의 두 끝이 legacy-last (C2) 대 `_best` (C9) 다. 기존 best/last 차(≤ 0.017)는 C6·UMi28 C2 값이지 C9 값이 아니다. 새 3 셀에 `--points` 3 점 · {V1, genie} 만의 last-EMA 태그(청크 192 개, V1 지배 → 셀당 ≈ 1–2 h CPU)를 보고 전용으로 두면 T4 를 뺀 비용 논리와 충돌하지 않는다.
- **UMi28 C6 격자 −3..+15**: 0단계 정보 구간 −9..+6 의 −9/−6 (파일럿에서 V1 이 붕괴한 점) 이 빠진 이유가 "셀당 격자 하나" 코드 제약임을 §1 에 문장으로 공개하고, 그래서 R(−9)/R(−6) 은 측정되지 않는다고 적는다.
- **σ 합격 조건의 등호**: U28NR16g 예상 σ_hi = 0.4994 는 8192 표본 중 상위 82 개가 −6 dB it1 64 개(ν 0.9953) + −3 dB it1 질량점(0.4988) 에 떨어진다는 계산이며 맞다(단 −6 dB it≥2 표본이 0.4988 을 넘으면 σ_hi 가 조금 더 크고 여전히 합격). 그러나 `np.percentile` 이 돌려주는 표본값과 공식 √(10^0.3/8) 은 ulp 수준에서 다를 수 있어 "≥" 가 헛FAIL 날 수 있다 → "σ_hi ≥ σ_t1(s_min)·(1 − 1e-9)" 로 쓰고 두 float 를 §5 에 적는다 (FAIL 분기의 격자는 PASS 분기와 수치적으로 같으므로 결과 영향 없음).
- **`runner.py:606`** 의 안내 문구 가드가 `(8, 16)` 그대로라 C9 실행 로그에 "M-ours-dscore → ABSENT" 가 찍힌다(build_point 가드 `:343` 은 (8,16,32) 로 고쳐져 V1 은 돈다). ⑩ 코드 목록에 넣어 정정.
- **보고 전용 추가**: C9 판정점(−9/−6/−3)에서 genie ≈ 0 이라 R ≈ 1 − F_V1/F_b\* 가 된다. "genie 쪽으로" 를 뒷받침하려면 판정점 합의 절대 격차 F_V1 − F_g 와 F_b\* − F_g 를 셀별로 함께 싣는다.
- §4.1 "kron 1024 병합 (D2 C9) 큐" → 완료로 갱신; §0.5 UMi28 C9 full 16·32·64 는 여전히 큐.

## 확인 (verified OK)

- **arm 집합 = 등록된 13 개**: A 태그(b\*-scalar, gmm32, R0, R1, R2, R3, R4-llr, R4-scvamp + b\*) + PIL(V1-pilot, bstar-pilot) + ALD(ALD-pilot, ALDv-pilot) = SUPP/STATIC 의 𝔅 12 + b\*. V0/V4/V4b 는 𝔅 밖(사용자 원칙 (2)). `runner.py --arm` 부분집합·`--pilot-arms`·`--ald-file` 존재; 1단계 `analysis_S1D2C9.log` 에서 축소 arm 집합의 표 B·power guard 가 정상 출력됨.
- **동일예산**: `train_nr16.py --nr 32 --prior UMi28 --sigma-tag --fits-tag --no-gbprime` 전부 존재; `score.train("D2SX{pre}NR{NR}{ntrain}", …, ntrain)` 이 GMM 과 같은 스트림 7 집합(fits 파일명 n160000), `--fits-tag` 는 GB′ 에만 영향. 새 fits 전부 `kron_batched = 0` (정확 경로), κ = 0, 재시작 3 — 초안 §0.4 와 일치.
- **테스트 시행 미사용**: worktree 의 C9·UMi28 C6 raw 전부 skip ≥ 2560 (`raw_snrC9`, `raw_S1*`, `raw_U28NR16/32` = b\*·R2·genie 탐침, `raw_pa*`, `raw_probeC9t`); `sigma.py measure/write` 는 nu_q 백분위만 기록하고 blk_err 를 쓰지 않는다 (`raw_NR32`, `raw_U28p16/32`, `raw_probeC9` 는 빈 디렉터리).
- **σ 격자 재사용 수치**: NR32 p99 σ 1.740 ≥ σ_t1(−12) 1.4075; U28NR32 1.723 ≥ 1.4075; NR16 0.4915 < 0.4994 (비 1.016, 초안이 공개); 학습은 [σ_lo, σ_hi] 연속 log-uniform 추출(`score.py:926`)이라 경계 질의도 학습 범위 안. U28NR16 원 격자 상단 0.4047 이 파일럿 붕괴 원인이라는 §0.2 진단과 파일이 일치.
- **부트스트랩·다중성**: `frontier_ci.Resampler` = (raw, 셀, SNR) 점당 인덱스 1 회, 점 간 독립 — §1 서술과 동일; B 2000·seed 20260926; Holm m = 2·FWER 0.10 (첫째 95 %, 둘째 90 %) 는 PARETO §1 선례와 같고 단계 논리가 맞다.
- **재사용 3 셀 값**: `recovery_{B16e4k,NR16B16e4,U28B16e4}.txt` 의 R_dp 0.509/0.823/0.150 과 CI, 판정점, ckpt sha·role, kron K·ll_val 이 §0.1·§1 과 일치; STATIC16e4 `chunks-sha` 3 개로 raw 가 고정돼 있다.
- **격자 끝 규칙·4096 멈춤**: DECISIONS 6b1de688 원칙 (1) 과 C6·38901·B32e4 선례 그대로; UMi28 C6 kron 1024 (53.880) > 512 (51.388) 로 2048 발동은 파일로 확인.
- **mix3 변경**: main 대비 diff 는 (UMi28,16,4)·(UMi28,32,4) 상수 추가와 docstring 뿐, Nr 8 경로 무변경 → bridge `BRU28` 가 비트 대조로 닫는다.
- **U28NR16g 예상 σ_hi 계산**: 8 점 × 16 × 64 = 8192, 상위 1 % = 82 개, −6 dB it1 64 개 뒤 −3 dB it1 질량점 → σ_hi = √(0.4988/2) = 0.4994 (위 권고의 ulp 캐비엇 외에는 맞음).


## review integ
 # 적대적 검토 — NEXT_EXPERIMENTS_SCALE16e4.md 초안 v1 (렌즈: 무결성·코드·비용)

검토 범위: 초안 전문, `~/t2_wtS`(scale, HEAD **742fd8ac** — 초안 작성 뒤 `edge_rule.sh` 가 커밋됨) 의 코드, main 의 규칙·선행 등록·raw 메타, 실행 중 프로세스(`ps`/`nvidia-smi`/`free`). 파일 수정 없음, GPU·수신기 실행 없음. SEEDS3·HISNR 의 raw/표/pair 는 열지 않았다(DECISIONS 의 SEEDS3 한 줄 요약과 `ps` 의 HISNR 명령줄·RSS 만 봤다). 시각: 09-30 10:20 CDT.

## 반드시 (must-fix)

**1. C9 수신기 메모리 — K = 4096 에서 192 워커는 OOM 이다 (비용 행·⑧ 스모크·선행 코드).**
- 근거: `Demo/t2_gmm.py:26-48 GMMPriorB` 는 `covs`·`U`(eigh)·`covinv` 를 각각 (K, N, N) complex128 로 들고, 반복마다 `A = covinv + G`, `Sig = inv(A)` 임시 2 개를 더 만든다. N = Nr·Nt = 128, K = 4096 → 배열 하나 1.07 GB, 워커당 ≈ 5–6 GB. **실측**: 지금 도는 HISNR C6 (N = 64, K = 4096) 이 193 워커 × **1.50 GB** = 290 GB (`ps` RSS 합). N 이 4 배 → 192 워커 ≈ 1.0–1.15 TB > 서버 RAM 1007 GB (`free -g`: 총 1007, 가용 745).
- `runner.py` 는 설계상 `--jobs` 가 없고(`runner.py:16`, `:636 jobs = min(cpu_count, len(tasks))`), `build_point` 는 arm 전부를 만든 뒤 `--arm` 으로 거른다(`runner.py:507`) → A·PIL·ALD·chk 등 **C9 의 모든 태그**가 K = 4096 GMM 을 워커마다 만든다(K2 @2048 ≈ 3 GB/워커, 192 × 3 ≈ 580 GB 로 경계). 초안의 ⑧("코어 4 이하, 시간만 출력")은 이를 잡지 못한다.
- 수정 문안: (a) ⑧ 에 "1 점·1 청크(`--n 40 --chunk 40` → jobs = 1)로 K = 4096 Nr 32 워커 RSS 를 `/usr/bin/time -v` 로 측정해 §5 에 적는다" 추가. (b) 선행 코드에 메모리 가드 추가: `jobs = min(os.cpu_count(), len(tasks), floor(0.8·MemAvailable / RSS_worker))` (RSS_worker 는 ⑧ 실측값을 인자·상수로; 실제 jobs 를 raw meta 와 로그에 기록). 01_RULES §4 "기본 = 전체 코어" 의 예외이므로 DECISIONS 동결 줄에 명시. (c) CPU 비용 행을 워커 ≈ 120–140 기준으로 재산정(벽시계 ≈ 1.4–1.6 배). (d) b\* 가 2048(내부)로 끝나면 192 유지.

**2. "새 raw 의 run|git = 동결 커밋 하나" 는 §5 커밋과 모순이고, ⑩ 병합 순서·커밋 금지 구간의 브랜치가 뒤섞여 있다 (§1 실행 위치 행, §1 선행 코드 ⑩, §4.1).**
- 초안 순서: 동결 커밋 → §5 채움·커밋 → CPU. 그러면 raw 의 `run|git` 은 §5 커밋이지 동결 커밋이 아니다. 또 ⑩ "main → scale 병합" 을 "main 커밋 금지 구간이 끝난 뒤" 로 미뤘는데, scale 로의 병합은 main 커밋이 아니며(금지 구간은 HISNR·SPARSE raw 가 main HEAD 를 기록하기 때문: WORK_QUEUE:18, `_git_head` 는 `code`·`../Demo` 만 본다 `runner.py:453-460`), 동결 뒤에 병합하면 동결된 코드 ≠ 실행 코드가 된다.
- 수정 문안: "⑩ main → scale 병합(코드 diff 확인)은 **동결 커밋 전**에 한다. 새 raw 의 `run|git` 은 **§5 커밋** 하나이며 `git diff <동결> <§5 커밋> -- code ../Demo` 가 비어 있어야 한다. §5 커밋부터 마지막 stage-2 raw 까지 **scale 브랜치 커밋 금지**(main 의 HISNR·SPARSE 구간과 별개). DECISIONS 동결 줄은 main 에 쓰려면 HISNR 종료(≈ 16:30 CDT 오늘)~SPARSE BLER 시작 틈에 쓰고, 아니면 scale 의 DECISIONS 에 쓰고 병합 충돌 해소 방침(ROTMIX 선례)을 적는다."

**3. 학습 실패 행: `aborted` 를 §3d 발동 조건으로 썼다 (§1 학습 실패 행).**
- `score.py:1031-1034`: `aborted` = KeyboardInterrupt(중단) 또는 min_epochs 미달 → 01_RULES §5 "시도가 아님" → 체크포인트 재개. 같은 행 끝의 "kill 이나 재부팅이면 재개" 와 모순.
- 수정 문안: "`stopped_by = diverged` 일 때만 §3d(fb2·fb3 병렬, 번호 최저 성공 시행, 나머지 미개봉 — 6953d595). `aborted = True`(중단·min_epochs 미달)는 시도가 아니며 같은 체크포인트에서 재개한다."

**4. GMM 격자 확장 서술이 실제로 도는 코드와 다르다 (§1 GMM b\* 행, EM 경로 행, §4.1).**
- 초안: "2048·4096 후보는 미리 병렬로 적합하고, 규칙이 발동할 때만 병합". 실제 `code/edge_rule.sh`(742fd8ac, 10 분마다): 병합된 최대 K 가 b\* 이면 **그때** 2K 재시작 0–2 + merge 를 큐에 넣고(merge 는 무조건), 4096 이면 정지. 4096 을 미리 적합하지 않는다. 또 EM 경로 행 "PASS 면 Nr 32 kron K ≥ 2048 은 일괄" 은 이미 틀렸다: `fitq_queue.txt` 에 NR32B16e4·U28NR16B16e4 의 kron 2048 재시작이 **정확 경로**로 들어가 있다(`run_fitq.sh` 는 `FIT_KRON_BATCHED` 를 안 켠다).
- 수정 문안: GMM 행을 edge_rule.sh 그대로 적는다("병합마다 `arms.gmm_selection`(ll_val)으로 재판정 → 계열 최대면 2K 큐 → 4096 정지, 로그 `logs/edge_rule.log`, 끝 표시 EDGE_RULE_DONE"). EM 행: "kron 2048 은 정확 경로(이미 큐); 일괄 검사 PASS 면 **4096 후보에만** 일괄 경로, 파일마다 `kron_batched` 기록". ③ 의 출력 파일명도 고정(`em_batched_check_nr.py:33` 의 OUT 이 `nr16b_batched_check.txt` 고정 → `results/nr{nr}b_batched_check_{prior}.txt`).

**5. 수용 검사 (b) "한 셀의 모든 태그에서 fits 실체가 같다" 는 K2 와 모순 (§1 수용 검사 (b), K2 정의).**
- `eval_accept.py:139` 는 한 호출의 모든 `--tag` 가 (bstar, kron_K, em_sec) 를 공유해야 통과한다. K2 는 kron_K = K/2 이고 fits 링크 집합이 다르다.
- 수정 문안: "(b) A·PIL·ALD·chk 는 한 호출(같은 fits 실체·em_sec). **K2 는 별도 호출**: `--kron-K K/2 --ll-val <ll(K/2)> --points <C>:<판정점 3> --fits-dir results/gmm_fits_D2_K2<T> --grid '<K_max 제외 격자>' --ref-raw raw_<T>`. K2 링크 집합은 full 파일을 남기므로(Chat 필요) kron K/2 의 ll_val 이 full 최대를 이기는지를 §5 에 적고, 아니면 K2 를 만들지 않고 Q-K 를 '정의 불가' 로 기록."

**6. pair_baselines `--est PIL<suf>` 와 ALD 명령 원문 (§1 2차 행, ALD 태그 행).**
- `pair_baselines.py:104-105` 는 `results/ald/ald_<est>.npz`·`pilots_<est>_test.npz` 를 읽는다 → `--est` 는 **ALD 추정 태그**다. ALD16e4 관례는 추정 태그 = PIL 이름(`run_ald16e4.sh` DS 표: `D2C6 PILNR16 ALDNR16 …`)이라 `--est PIL<suf>` 는 `ald.py … --tag PIL<suf>` 로 돌릴 때만 맞다. 초안엔 ald.py 명령이 없다.
- 수정 문안(원문 고정): `CUDA_VISIBLE_DEVICES= ald.py regen --tag PIL<suf> --prior <p> --cell <C> --fits-tag <T> --set dev` → `CUDA_VISIBLE_DEVICES=<g> ald.py tune --tag PIL<suf> --ckpt <best>` → `… regen --set test` → `… estimate --tag PIL<suf> --ckpt <best> --set test` → `runner.py run … --ald-file results/ald/ald_PIL<suf>.npz --arm ALD-pilot ALDv-pilot R5-genie --tag ALD<suf>`.

**7. `run_scale2.sh` ⑦ 의 필수 사양을 §1 에 적어야 한다 — `run_prior_eval.sh` 는 그대로 못 쓴다.**
- `run_prior_eval.sh` 는 `cd /home/HTJ/t2/conf`(main 트리), `--cell C2` 고정, `${TAG}last` 도 실행, `gmm_fits_D2_${TAG}last` 링크 요구, `CUDA_VISIBLE_DEVICES` 미설정, `--arm` 없음(14 arm).
- 수정 문안에 넣을 것: `cd ~/t2_wtS/conf`; **`export CUDA_VISIBLE_DEVICES=`** (38901 §4 :139 — UMi28 Sionna 워커가 GPU 0 을 잡아 청크 0 개로 정체한 선례; `run_stage1.sh`·`run_hisnr16e4.sh` 도 숨김); `--cell {C6,C9} --prior {S2,UMi28} --n 2560 --chunk 40 --ntrain 160000`; A: `--arm M-ours-dscore-C-V1 M-ours-bstar M-ours-bstar-scalar M-ours-gmm32 R0-pilot R1-turbo R2-ours-G R3-bigamp R4-llr R4-scvamp R5-genie --stagec-ckpt <best>`; PIL: `--pilot-arms --arm V1-pilot bstar-pilot R5-genie`; **K2·chk·bridge 도 `--stagec-ckpt` 를 넣는다**(안 넣으면 `meta|stagec_ckpt_id` 가 없어 eval_accept (c) 실패: `runner.py:382`, XL 선례 `run_supp16e4.sh:84`); chk/bridge: `--n 40 --chunk 40 --snr <첫 점>`; bridge BRB16e4k 의 role 문자열은 **`legacy-last`**(`run_pilot16e4.sh:17`); `last` 태그 없음; 전제: `git status --porcelain code ../Demo` 비어 있음, `_best.pt` sha 대조, fits 링크 전부(`gmm_fits_D2_{PIL<suf>,ALD<suf>,<T>chk,K2<T>,BRB16e4k,BRNR16,BRU28,K2NR16B16e4,K2U28B16e4}`), raw 링크(`raw_NR16B16e4`·`raw_U28B16e4` 는 git 미추적이라 main 링크 필요; `raw_B16e4k`·`raw_B16e4` 는 git 추적 사본이라 worktree 에 이미 있음 — "링크" 서술 정정).

**8. Q-K "같은 시행이라 같은 인덱스" 는 현 Resampler 로 보장되지 않는다 (§1 Q-K 행, ⑤).**
- `frontier_ci.py:60-75` 는 인덱스를 (raw spec, 점) 으로 키 잡는다 → K2 raw 는 base raw 와 다른 인덱스를 받는다.
- 수정 문안: "⑤ `--extrap RAW_K2` 는 K2 raw 의 b\* 열을 **base raw 의 키**로 재표본(`take(spec=base, …)`)하고, 항등 검사(K2 = base → 출력 동일)로 확인." 또 e⁺ 를 시행 단위(−1·2 가 나옴) 대신 합 단위 F⁺ = 2F(K_max) − F(K/2) 로 정의하고 F⁺ ≤ F_g 면 정의 불가로 둔다.

## 권고 (should)

- §0/§4.1 현황 갱신: SEEDS3 는 08:03 CDT 종료(체인 로그), HISNR 은 08:03 시작·C6 단계 실행 중(≈ 16:30 CDT 종료 추정); D2 C9 kron 1024 병합 완료(10:20 CDT, 240.837 → 2048 발동·큐); scale HEAD 742fd8ac; ⑩ diff 목록에 `edge_rule.sh` 포함.
- `runner.py:606` 의 안내 출력이 `Nr not in (8, 16)` 이라 C9 에서 "M-ours-dscore → ABSENT" 를 잘못 찍는다(빌드 가드 `:343` 은 32 포함). 로그 오해 방지용으로 (8, 16, 32) 로 맞추거나 §1 에 "무시" 를 적는다.
- full 계열 "512 가 끝일 때만 1024 를 한 번" 은 C6B16e4/B32e4 의 "어느 계열이든 2K 반복" 과 다르다. 세 셀 모두 full 이 내부라 실효는 없으나 규칙을 선례와 같게 두거나 이탈을 명시한다.
- ② `runner.py sigma --snr`: argparse 엔 `--snr` 가 있으나(`:1170`) `cmd_sigma`(`:763`)·`sigma.measure`(`:61`) 가 CELLS 격자를 쓴다 → 측정 집합을 파일 머리말에 찍게 하고 수용 (i) 와 연결.
- σ 공개 보강: NR32·U28NR32 는 탐침 격자(−15..15, 11 점)로 재서 20 점이 등록 격자(−12..6)보다 넓게 퍼진다; U28NR16g 만 등록 격자 ∪{−6} 로 잰다 — 비대칭을 §1 σ 행에 적는다.
- §0.4 "XL 14.1 분 / DOPaNR16 112.2 분" 의 출처 파일을 적는다(SUPP16e4 §1:42 는 DOPbNR16 111.5 분·XL 9.4–17.2 분을 인용; 14.1 은 못 찾았다).
- D2 C2 의 K/2 = `raw_B16e4`(legacy: `run|git`·ckpt id 없음, kron 512, ll −14.63610615674937) 에는 (c)(f) 를 적용할 수 없음을 명시하고 (d) genie 동일성만 검사한다고 적는다.
- ③ 의 (b) 케이스는 N = 1e4 집합에서 K = 512 를 새로 적합해 재시드 ≥ 1 을 요구한다(`em_batched_check_nr.py` 도큐스트링·`:48`) — 재시드가 0 이면 구성상 FAIL → 정확 경로(비용 300 h 쪽)임을 §4.2-3 에 적는다.
- CLAUDE.md 규칙대로 §6 뒤 `docs/EXPERIMENTS.md` 행 추가를 §4.1 에 넣는다.
- chk 의 "첫 등록 SNR"(C9 = −12 dB, b\* BLER ≈ 0.9)은 비트 동일 검사엔 충분하나 표 머리말·UMi28 배너 검사도 그 점에서 한다고 적는다.

## 확인 (verified OK)

- **셀·러너**: `common.py:86` C9 = Nr 32/Nt 4/T 16/Tp 4, 탐침 격자 −15..15; `:90` DEFAULT_CELLS 제외; `runner.py:343` Nr ∈ (8,16,32) 가드; PID S2 = 4, UMi28 = 8, TBID D2 = 2 (`common.py:95-104`) → 시행 스트림 서술 일치(`:212`).
- **학습**: `train_nr16.py` 인자 `--nr {16,32} --prior {S2,S2v,UMi28} --ntrain --sigma-tag --fits-tag --no-gbprime --fallback {1,2,3}`, ckpt 이름 `d2sx_[UMi28]NR{nr}_N160000_a1[_fb2]`; `conf/ckpt` 는 main 링크이고 NR32·UMi28NR16·UMi28NR32 의 1.6e5 ckpt 가 없다 → 우발 재개 없음. 레시피 HP 일치. NR32 1e4: 2342 ep patience, 1.414 s/ep → 1.6e5 ≈ 22.6 s/ep(≈ 21 s 추정 타당).
- **eval_accept (scale)**: `--grid --nr --prior --points --ref-arms all --cand-dir --bstar` 있음(`--skip0` 은 main 전용, 불필요); K ≥ 1024 후보 3 개 검사 `:151-157`.
- **pair_baselines (scale)**: `--base --pil --ald --est --cell --prior --r0 at1 --extra --ref --legacy`; `:91` 격자 = CELLS; 𝔅 12 = `:30-31`; V0/V4/V4b 없어도 통과(`:208` 필수 목록, `:274` `if arm in data`). `ald.py:85` 격자 = CELLS, `--set dev --n-dev 512` → 2560..3071.
- **frontier_ci**: `--recovery` 2 spec·90 % 만(p·95 % 는 ⑤ 신설 필요), Resampler 점별 인덱스, 양측 p 공식은 `cmd_pair :118-119` 에 있음. `raws()` 는 `conf/<raw>` 경로 → worktree 링크 전제 맞음.
- **fit_gpu/큐**: `--restart r | --merge` + `--prior` 파싱 `:147-164`, 후보 `.k0r{r}.npz`, merge 는 후보 3 개 없으면 거부; `run_fitq.sh` 가 후보 3 개를 기다림; `arms.D2_KS` 에 2048·4096·8192, 선택 = ll_val 최대(`arms.py:91-100`).
- **fits 현황**: NR32B16e4 full 16..512 + kron 16..1024 병합(10:20 CDT); U28NR16B16e4 전부 + kron 1024 병합 53.880 급; U28NR32B16e4 진행 중(kron 1024 r0 147.154·kron 512 r1 143.616·full 64 r1 75.728 로그 확인); 큐에 kron 2048 ×2 태그. 재사용 K2 용 fits 존재: NR16B16e4 kron 2048, U28B16e4 kron 2048; B16e4k 는 kron ≤ 1024(2048 미적합) → D2 C2 K/2 = raw_B16e4(kron 512) 타당.
- **σ**: NR32 [3.281e-2, 1.740] (git bafdf46a, C9 11 점), U28NR32 [3.296e-2, 1.723], U28NR16 [3.293e-2, 4.047e-1] (C6 7 점), NR16 σ_hi 0.4915; σ_t1(−12) = 1.4075, σ_t1(−3) = 0.4994, 비 1.016 — 모두 재계산 일치. `sigma.py:30-56` 은 `trial_rng` 시행 0..63, n = 64 → 테스트 시행 접촉 공개 정확. U28NR16 파일의 최대 ν = 0.4988(−3 dB it1 질량점) → 등호 통과 예측 타당.
- **재사용 셀 수치**: `recovery_{B16e4k,NR16B16e4,U28B16e4}.txt` 의 R_dp 0.509 [0.470,0.545] / 0.823 [0.771,0.871] / 0.150 [0.110,0.189], R(−3) 0.470/0.809/0.062, 실패 합 864/488/125 · 277/82/40 · 800/712/215; ckpt sha256 4443921ce8d5c4a1 / c050d611b2c714a6 / 6f3a1b9490864af1 (sha256sum); raw 메타 kron 1024(−11.45916983122441)/4096(63.1751571838059)/4096(5.797910431000217), 448 청크; STATIC16e4 §6:104-108 의 chunks-sha 존재; SEEDS16e4 산포 0.011(0.509/0.513/0.520)·0.028(0.150/0.162/0.178).
- **규칙·선례**: 01_RULES:76 = "GMM arm 을 약화시키지 않는다(K 전 범위)" 인용 타당; §9.3 ALD GPU 예외 선례(ALD16e4 §1); 10_SPEC §3d·§6l 존재; C6B16e4 §1 격자 끝 규칙("어느 계열이든 2K"), 4096 정지 = 사용자 결정; 6953d595 = 시행 3 대기 실행 규칙; 6b1de688 위임 원문; PARETO §1 Holm m = 2(첫째 95 %·둘째 90 %); 38901 §0 σ 관례(n = 64, 시행 0..63)·§4 CUDA 숨김 사유; 08_SPEC §2 power guard·`analysis.decision_points :405-413`([0.005, 0.9], |log10(BLER/0.1)|).
- **미구현 확인 (초안 ①–④ 주장과 일치)**: `em_batched_check_nr.py` 는 argparse 없이 NR = 16/S2 고정(`:31`), `testbed_mix3.py:23` NR = 8 고정, `cmd_sigma` 는 `--snr` 미사용, `nr16b_batched_check.txt` PASS(×15.4, K ≤ 512).
- **비용 기준**: STAGE0 수치(C9/C6 적합 4.8–17×, 청크 3512 s vs 386 s, V1 350 s/4 블록) 인용 정확; D2 C9 kron 1024 재시작 31,226–31,715 s(≈ 8.7 h) → 4096 ≈ 35 h/재시작 추정 정합; UMi28 Nr 32 kron 1024 ≈ 10,936 s.
- **자원 상태**: HISNR 193 워커 290 GB; GPU 1·2·3 적합 중, 0·4·5 유휴(lane 대기); scale 트리 `code` 청결(`edge_rule.sh` 커밋됨), 수정 추적 파일은 `results/gmm_fits_D2_B1e4` 링크·`d2_gbprime_UMi28.csv` 뿐(`_git_head` 는 code/Demo 만 보므로 raw 에 +dirty 안 붙음).
