# NEXT_EXPERIMENTS_DMC16e4 — DeepMIMO v4 (6 개 도시 28 GHz, ray-traced, block split) 수신기 BLER: **DMC 측정** (셀 C2, 동일예산 N′ = 1.6e5, 태그 DMCB16e4) — 사전 등록 v1 (초안)

- 작성: 2026-10-10 17:51 CDT (= 10-11 07:51 KST), Claude Code (Opus 5.5), 초안 v1. 적대적 검토(Fable 서브에이전트) 반영 뒤 v2 로 동결한다. 동결 시각 = 동결 커밋 시각(`DECISIONS.md` 같은 줄). **결과 관측 전**: DMC 의 어떤 체크포인트·적합도 BLER 로 평가된 적이 없다(학습·GMM 격자는 GPU 큐에서 진행 중, §4). 커밋 뒤에는 §1~§3 을 바꾸지 않는다; 바꿔야 하면 사용자 승인 + `DECISIONS.md`.
- 사용자 결정(2026-10-10 CDT, 이 세션; `conf/DECISIONS.md` 같은 날 줄): (1) "우리 실험 Sionna와 Deep MIMO 로 진행한 내역 있나 확인해보고 없으면 진행하자" → 확인 결과 Sionna PHY(38.901) 는 수신기 BLER 까지 있고 Sionna RT·DeepMIMO 는 0단계 채널 통계만 있음 → 선택지 가운데 **"DeepMIMO 만"**; (2) "Deepmimo 자체에 채널 생성하는 게 있지?" → 채널은 **DeepMIMO 자체 생성기 `dataset.compute_channels`** 로 만든다(우리 배열 코드가 아님); (3) "Deepmimo 로 실험할때도 **기존 실험과 같은 사이즈**로 해야해".
- 틀: `NEXT_EXPERIMENTS_38901.md` v2 (§0~§6; UNGATED 측정·§3d 사다리·격자 반복 규칙·수용 검사 (a)~(e)·회수율 CI·ΔR) 를 그대로 따른다. 다른 곳은 채널 생성(§1 "생성 모델")과 DMC 고유 공개 사항(§1 "DMC 고유 사항")뿐이다. 재료: `results/review_next/testbed2_phase0/{report_deepmimo.md, selection.md, json/res_city_0_newyork_28+…_8_block_centroid.json}`, `code/{dmimo.py, dmimo_build.py, testbed_dm.py}` 머리말, `results/testbed_DMC.txt`, `results/sigma_grid_D2_DMC.txt`, `results/nr8b_batched_check_DMC_n160000.txt`.
- 목적: **사이트 특정 ray-traced 채널(DeepMIMO)에서 같은 파이프라인·같은 크기·같은 규칙으로 b\* 대 V1 을 잰다.** 0단계 채널 통계(수신기 BLER 미사용)는 DeepMIMO 를 "GMM 친화" 로 분류했고(6 개 도시 block split: K = 64 GMM 이 파일럿 단계 K1 → 잠재 오라클 격차의 0.68 을 메움; D2 0.26) 그래서 2026-09-26 에 두 번째 testbed 에서 뺐다. 같은 통계(0.68)였던 38.901 UMi28 은 등록 예측("V1 우위 없음")이 빗나가 (i) 가 나왔다(`NEXT_EXPERIMENTS_38901.md` §6; RESULTS §10). 따라서 0단계 통계만으로 DeepMIMO 의 BLER 방향을 말할 수 없다 — 그것을 잰다. 결과가 어느 쪽이든 보고한다. 헤드라인(C2 1.6e5 B16e4k)·D2 판정은 어느 결과에서도 바뀌지 않는다.
- 선택 경위(공개): DeepMIMO 구성은 0단계가 잰 것 가운데 **공통 크기를 감당하는 유일한 구성**을 그대로 쓴다 — 필요한 쌍 수는 학습 160000 + 검증 5000 + (테스트 쪽) 이고, boston5g_28 은 105,842 쌍, New York + Miami 는 130,969 쌍, 6 개 도시는 342,597 쌍이다(`report_deepmimo.md`). BS·UE 배열 규약, block split 규칙(20 m 타일, 15 %)도 0단계 것이다. 0단계의 닫힌 비율은 6 개 도시 block 0.68, NY+MIA 0.69, boston5g 0.75–0.77 (K = 64, −3 dB) 로 6 개 도시가 DeepMIMO 구성 가운데 가장 덜 GMM 친화였다 — 크기 조건이 그것을 고르게 했고, BLER 을 보고 고른 것이 아니다(어떤 DeepMIMO 구성도 수신기에 넣은 적이 없다). O1 계열은 0단계에서 재지 못했고(다운로드 쿼터) 이번에도 쓰지 않는다. Sionna RT 는 이번 결정에서 빠졌다(실행하지 않는다).

---

## 0. 출발점 (판정에 쓰지 않는다)

**0단계 채널 통계** (`testbed2_phase0/report_deepmimo.md`, JSON `res_city_0_newyork_28+city_6_miami_28+city_1_losangeles_28+city_2_chicago_28+city_3_houston_28+city_4_phoenix_28_8_block_centroid.json`; 수신기 BLER 미사용; 지표 = 파일럿 단계 디노이징(Tp = Nt, ν = σ²/Nt)에서 EM-GMM 이 K = 1 Gaussian → 잠재 오라클(LO) 격차를 메운 비율 closed; 학습 36000 / 검증 4000 / 테스트 2000, 0단계 자체 RNG·자체 split — 파이프라인 스트림이 아님):

| 구성 (8×4) | −3 dB 격차 K1−LO (NMSE) | closed 16/64/256 (−3 dB) | +3 dB 격차 | closed 16/64/256 (+3 dB) |
|---|---|---|---|---|
| **DeepMIMO 6 개 도시, block split** (전체) | 0.274 | **0.56/0.68/0.71** | 0.094 | 0.52/0.63/0.66 |
| 같은 구성, LoS 부분 (n 583) / NLoS 부분 (n 1417) | 0.290 / 0.267 | 0.63/0.75/0.79 · 0.53/0.64/0.67 | 0.099 / 0.092 | 0.63/0.74/0.77 · 0.47/0.58/0.61 |
| 38.901 UMi28 (문맥; `NEXT_EXPERIMENTS_38901.md` §0) | 0.173 | 0.57/0.68/0.71 | 0.055 | 0.54/0.63/0.64 |
| D2 S2 (기준값) | 0.249 | 0.19/0.26/0.29 | 0.089 | 0.18/0.25/0.24 |

- 0단계의 다른 값(같은 JSON): LoS 비율 0.281, 사용자당 경로 수 중앙값 22 (최강 경로 20 dB 안 4), 유효 경로 수 1/Σp² 중앙값 1.72, 앙상블 유효 랭크 25.1/32, 빔공간 top-4 에너지 0.844, −3 dB outage P(MI < 4 bit) 0.236, 누수(정규화 최근접 제곱거리 < 0.1 인 테스트 비율) 0.411, TwoNN 내재 차원 3.4 (D2 12.2).
- 0단계 캐비엇(공개): 0단계 선택 기준 (2)(공정성)에서 DeepMIMO 는 **누수·outage 로 "실패"** 로 적혔다(`selection.md` 8행). 이 등록은 그 두 성질을 고치지 않고 그대로 공개한 채 잰다(§1 "DMC 고유 사항").

**비교 대상 (짝 없음; 문맥용)** — D2 C2 1.6e5 헤드라인 `raw_B16e4k`: −3 dB 실패 b\* 623 (0.243) / V1 371 (0.145) / genie 87 (0.034); 표 B `b* → V1` 판정점 −3/0/+3, pooled 454:78; 회수율 R(−3 dB) 0.470 [90% 0.427, 0.512]; SNR@0.1 격차 +1.41 dB [1.22, 1.64]. 38.901 UMi28 `raw_U28B16e4` (RESULTS §10): 판정점 +3/+6/+9, 76:38 · 50:22 · 35:13, pooled 161:73, 라벨 (i), SNR@0.1 격차 +0.60 dB [+0.33, +0.87], R(−3 dB) 0.062 [0.033, 0.089], ΔR −0.408 [−0.458, −0.358], b\* = kron 4096 (격자 끝), GB′ median 0.920.

**testbed 검증** (`results/testbed_DMC.txt` @25f74c0a, 2026-10-11 07:39 KST = 10-10 17:39 CDT; `code/testbed_dm.py`, 허용오차는 실행 전 고정, BLER 없음):

| 검사 | DMC |
|---|---|
| TDMa 정규화(검증 스트림 8, n = 20000; 상수는 학습 스트림 7 에서 보정 → 같은 타일의 다른 쌍에 대한 표본 외 검사; 4 s.e. 대역) | mean ‖H‖²/(NrNt) = 1.00214 (s.e. 0.00281) **PASS**; 블록 전력 CV 0.396 |
| TDMb 원소별 E\|H_ab\|² (보고) | 0.9960–1.0110 |
| TDMc 풀이 0단계 프로브와 같은가 | 쌍 342597 = 342597; BS yaw 18 개 최대 차 0.10°; LoS 비율 0.281290 = 0.281290 **PASS** |
| TDMd 파일럿 단계 K = 1 Gaussian NMSE @ −3 dB vs 프로브(\|diff\| ≤ 0.02) | 0.3161 vs 0.3218 **PASS** |
| TDMe T2b 파일럿 결정 / erank(C_ens) / 빔공간 top-4 | erank(Rt) 3.422/4 < 3.6 → **eigen 정렬** / 25.27/32 (프로브 25.14) / 중앙값 0.872, 평균 0.854 (프로브 평균 0.844) |
| TDMf block split | 세 풀 서로소·전체, 20 m 타일 564 개 중 88 개가 테스트, 양쪽에 걸친 타일 없음, 테스트 비중 0.1523 **PASS** |
| TDMg split 이동(보고) | LoS 비율 학습 쪽 0.2819 / 테스트 쪽 0.2780; outage @ −3 dB 검증 0.2170 / 테스트 0.1905 (프로브 0.2362); K = 1 NMSE @ −3 dB 검증 0.3161 / 테스트 0.3164; 테스트 쪽 mean ‖H‖²/(NrNt) 1.0017 |
| TDMh 누수(보고) | 테스트 2000 표본의 최근접 학습 채널(N′ = 160000): 정규화 제곱거리 중앙값 0.1261, < 0.1 비율 **0.433** (프로브 0.411) |
| TDMi 생성 비용 | sample() 0.01 ms/호출, 160000 표본 0.1 s |
| 종합 | **ALL PASS** (4 s CPU) |

**σ 격자** (`runner.py sigma --testbed D2 --prior DMC --cell C1 C2 --tag DMC`, 다른 prior 와 같은 절차: Gaussian 수신기(M-ours-G 인터페이스), n = 64, 시행 0..63, 7 SNR, ν_q 만 기록; `sigma_grid_D2_DMC.{txt,npz}` @25f74c0a, 10-10 17:39 CDT 무렵): 20 점, ν_q [2.239e-03, 1.501e+00] → σ_t [3.346e-02, 8.664e-01] (헤드라인 D2 [3.3062e-02, 8.4516e-01] 대비 +1.2 % / +2.5 %). **공개: 이 측정으로 DMC 의 테스트 시행 0..63 (C1·C2, 7 SNR) 이 Gaussian 수신기로 한 번 실행됐다** (BLER 은 읽지도 쓰지도 않음; 헤드라인·D3·SV·38.901 관례와 같음).

**일괄 kron EM 검사** (`results/nr8b_batched_check_DMC_n160000.txt` @25f74c0a 작업 트리 + 선택지 한 줄, 커밋 08a3e81d): (a) N′ = 160000 K = 512 6 반복, (b) 재시드 활성 N = 10000 K = 512 15 반복(재시드 2358/2358) 둘 다 PASS(max\|Δll\| 3.9e-09, 공분산 상대 차 2.9e-08) → kron 계열은 일괄 경로(UMi28 C2 와 같음), full 계열은 정확 경로.

---

## 1. 고정되는 것

| 항목 | 값 |
|---|---|
| **셀·예산·시행 (기존 실험과 같은 크기 — 사용자 지시)** | C2 = 8×4, T 16, Tp 4, K = 42 정보 비트, rate-1/2 conv (133,171)_8, QPSK, 16 반복, 7 SNR (−3, 0, 3, 6, 9, 12, 15 dB; **결과 뒤 격자를 늘리지 않는다**), n = 2560, 테스트 시행 **0..2559** (chunk 40 → {(40k, 40): k = 0..63}), 수신기 CPU complex128. 시행 시드 `default_rng([20260926, 2, PID, 8, 16, 4, snr+100])` (`common.trial_rng`), **PID DMC = 11** → 다른 모든 prior 와 다른 스트림 → **D2 와의 비교는 짝 없음(unpaired)**. 동일예산 N′ = 160000: 채널 집합 하나 = `arms.training_set("D2", "DMC", 8, 4, 160000)` (스트림 7) 을 GMM 적합(`runner._sets`)과 score 학습(`score.train`; 자체 9:1 = 144000/16000)이 함께 쓴다; GMM 검증 5000 = 스트림 8; Gaussian arm 의 Chat 도 같은 집합 |
| **지위** | **UNGATED** (38.901·SV8e·D3 와 같음; D1 형제 규칙을 새 prior 로 넓히지 않는다) → 결과는 **"prior·기전 축 측정"** 이며 arm 판정이 아니다. 헤드라인(C2 1.6e5 B16e4k) 불변; DMC 는 어느 결과에서도 헤드라인이 되지 않는다 |
| **생성 모델** (`code/dmimo.py`·`code/dmimo_build.py` 머리말; 동결 — 바꾸려면 새 결정 + 새 prior id) | **DeepMIMO v4.0.5** (`pip --no-deps --target ~/data/deepmimo/site`; numpy 2.5.2 — 패키지 메타데이터는 numpy < 2.3 을 요구하나 동작함, torch 환경 불변). 시나리오(Wireless InSite 3.3, 28 GHz): `city_0_newyork_28`, `city_6_miami_28`, `city_1_losangeles_28`, `city_2_chicago_28`, `city_3_houston_28`, `city_4_phoenix_28`, `dm.load(s, max_paths=25)`, 도시마다 BS 3 개 × 사용자 격자. **쌍** = 경로가 하나라도 있는 (시나리오, BS, 격자 사용자) = **342,597 개**(경로 없는 사용자는 버림). **채널 = DeepMIMO 자체 생성기** `dataset.compute_channels(ChannelParameters)`: `freq_domain`, `selected_subcarriers [0]` (지연 위상 항 exp(0) = 1 → 반송파에서의 협대역 채널), `num_paths 25`, 등방성 소자, 반파장; BS = 8×1 패널(국소 y 축 수평 ULA), 회전 [0, 0, yaw_BS], yaw_BS = BS 에서 그 BS 의 쌍들 중심으로 향하는 방위각(사용자를 향한 섹터; 0단계 규칙); UE = 4×1 패널, 회전 [0, 0, yaw_UE], **yaw_UE ~ U[−180°, 180°) 를 쌍마다 한 번 뽑아 동결**; 상향링크는 상반성으로 H[a, b] = BS 안테나 a, UE 안테나 b = `compute_channels(...)[user, b, a, 0]`; **쌍별 정규화** H/√(그 쌍의 선형 경로 전력 합) (pathloss·shadowing 제거; 0단계와 같음); DeepMIMO 가 내는 complex64 → complex128. **앙상블 정규화** E‖H‖_F² = NrNt: H = H_pool/√P_RAW, P_RAW 는 학습 스트림 7 의 N_CAL = 160000 표본에서 한 번 재고 상수로 동결 — **P_RAW 0.0019541542355243444** (≈ 1/512 = DeepMIMO 의 1/부반송파 수 진폭 인자), **TRAIN_SHA e6ddafc27367f975**; vec 열 우선. **풀은 고정 파일**(git 밖, `~/data/deepmimo/dmc_Nr8/`): `H.npy` sha256[:16] **709a6346b0ea763b**, `split.npy` **9f3237f1997d6b91** (`dmimo.POOL_SHA` 가 고정; 다르면 생성기가 거부). 두 번 다시 빌드해 같은 sha. zip sha256[:16]: newyork 664b8cbff925386c, losangeles 3eb62ebc424a4008, chicago 781eeac4cd56f2f6, houston eb4d105a1798a560, phoenix 831c2bc43d27f4f4, miami 994b30a4d4fcc036. 빌드 시드 `default_rng([20260926, 2, 12, 11])` (yaw·타일·검증 풀). **상수는 8×4 만**(다른 배열은 오류) |
| **block split 과 스트림** (`dmimo.py` 머리말) | 시나리오별 20 m 위치 타일(`floor(xy/20)`) 564 개를 섞어 쌍의 15 % 이상을 담을 때까지 취한 88 개 = **테스트 타일**(52,172 쌍; 한 타일은 그것을 보는 모든 BS 에 대해 같은 쪽); 나머지 타일의 쌍 가운데 동결된 무작위 20,000 쌍 = **검증 풀**, 나머지 270,425 쌍 = **학습 풀**. 스트림 → 풀(생성기 API 에 스트림 번호가 없어 `rng.bit_generator.seed_seq` 의 시드 배치로 읽는다): 학습 스트림 7 → 학습 풀에서 **서로 다른 n 쌍**(순열 앞 n 개; N′ = 160000); 스트림 8 → 검증 풀에서 서로 다른 n 쌍(GMM 검증 5000; 학습 풀과 같은 타일·다른 쌍); 스트림 10 과 **모든 시행 스트림 → 테스트 풀에서 복원 추출 i.i.d.**(시행마다 색인 하나). 다른 시드 배치는 오류(split 을 조용히 어기지 않는다). `sample(rng) == sample_vecs(rng, 1)[0]` |
| **DMC 고유 사항 (공개; 고치지 않고 그대로 잰다)** | (1) **유한 풀**: 생성 모델이 아니다 — 테스트 시행은 52,172 쌍에서 복원 추출이므로 한 점의 2560 시행 안에 같은 쌍이 되풀이될 수 있다(기대 중복 약 2560²/(2·52172) ≈ 63 쌍; 채널은 같고 데이터·잡음은 독립). 부호검정의 독립 단위는 시행이며 채널 모집단은 "이 풀의 테스트 타일" 이다 — 다른 도시·다른 타일로의 일반화는 주장하지 않는다. (2) **누수**: 테스트 쪽 채널의 0.433 이 학습 집합에 정규화 제곱거리 0.1 안의 이웃을 갖는다(TDMh; 20 m block split 으로도 줄지 않는다 — 0단계 보고서: 저차원 기하라 다른 곳에 닮은 채널이 있다). GMM 과 score 모델이 같은 학습 집합을 쓰므로 조건은 두 arm 에 같다. (3) **outage**: 테스트 쪽 −3 dB P(MI < 4 bit) 0.1905 — 낮은 SNR 에서는 prior 와 무관하게 실패하는 블록이 많다; 판정점은 규칙이 자동으로 고른다(BLER 이 0.1 에 가까운 3 점). (4) **모집단 가중**: 쌍에 균등(도시·BS 는 경로 있는 쌍 수에 비례); UE yaw 는 쌍마다 고정. (5) **split 이동**: 테스트 타일은 다른 장소라 학습 쪽과 통계가 조금 다르다(TDMg). (6) 블록 전력 CV 0.396 (쌍별 경로 전력 합은 1 이지만 경로 간 간섭으로 ‖H‖² 가 변한다) |
| **파일럿** | D2 의 T2b 규칙(`common.make_pilots`) 을 학습 집합에서 잰 Rt = E[HᴴH]/Nr (동결 상수 `dmimo.RT`) 에 적용: erank(Rt) 3.422 < 0.9·Nt = 3.6 → **eigen 정렬 파일럿** (U2·SV8e·38.901 과 같은 처리; 규칙 적용이며 새 판단 아님). C2 (Tp = Nt = 4) 에서는 X_p X_pᴴ = 4I 로 DFT 와 같은 충분통계 |
| **GMM 격자와 b\*** | 38.901 §1 과 같다. 기본 격자 full K ∈ {16, 32, 64, 128, 256, 512} (정확 경로 + κ 격자), kron K ∈ {16, …, 512} (일괄 경로) + kron 1024·2048·4096 은 재시작 후보 3 개(`.k0r{0,1,2}.npz`) → CPU 병합(`fit_gpu.py 8 kron K 160000 DMCB16e4 --merge --prior DMC`); 선택 = 검증 우도 최대(`arms.gmm_selection`, 스트림 8). **반복 규칙**: kron 1024·2048 을 병합해 b\* 를 고르고, b\* 가 kron 2048(기본 격자 끝)이면 kron 4096 을 병합해 다시 고른다; **kron 4096 에서 멈춘다(K = 8192 없음) → 그때는 b\* = 격자 끝 + 캐비엇**. b\* 가 full 512 이면 full 1024 를 같은 프로토콜로 한 번 적합해 다시 고르고 1024 에서 멈춘다 + 캐비엇. 후보 파일 누락 시 같은 시드의 그 재시작만 재실행(결정적)하고 §5 에 적는다. 상한 500 정지·재시드 수·구현 경로·수렴 규칙은 §5 에 파일별로. **BLER 은 선택에 쓰지 않는다.** 미병합 후보는 존재를 §5 에 적고 쓰지 않는다. 큐: `code/run_dmc_gpu.sh` (UMi28 와 같은 22 작업·같은 순서) |
| **체크포인트·평가 가중치** | 동결 레시피 `run_d2_sx.py --prior DMC --ntrain 160000 --tag DMCB16e4 --fallback 1 --no-gbprime` (hp: dit / vp / angle, lr 2.238046e-3, ema 0.999, batch 256, emb 256, width 64, depth 6, heads 8, patch 1, **479,426 params**; patience 20, 최소 200, 최대 3000 epoch; float32 학습), rung **D2SXDMC160000** (`score._rung_ix` 1694; 기존 rung 과 충돌 없음), attempt 1 → `ckpt/d2sx_DMC_N160000_a1.pt` (last-EMA) + `_best.pt`. **측정 판정 태그 `DMCB16e4` = `_best.pt`**; **`DMCB16e4last` = last-EMA, 보고 전용**. "시도했다" = patience 종료 또는 ≥ 200 epoch |
| **학습 실패 처리** | `stopped_by=diverged` 또는 `aborted` → 10_SPEC §3d 사다리(`run_tb2.sh train_chain` 이 같은 GPU 에서 자동 연쇄): 시행 2 = 기울기 클리핑 1.0 (`_fb2.pt`), 시행 3 = + lr/3 (`_fb3.pt`); 같은 rung·attempt = 같은 데이터 스트림; 시행 간 선택은 val loss 만, 발산 체크포인트로 평가하지 않는다; 시행 3 도 실패 → "학습 실패", BLER 없음. stopped_by 가 patience/max_epochs/diverged 가 아니면 사슬을 멈추고 수동 결정(§4 에 기록). `max_epochs` 정지는 유효 |
| **σ 격자** | 학습·GB′ 모두 prior 자체 격자 `sigma_tag = "DMC"` (§0; 체크포인트에 저장; 학습 로그 머리말 `sigma grid MEASURED … [3.3459e-02, 8.6642e-01]` 로 확인). 재측정하지 않는다 |
| **실행 (테스트 집합, 전 arm = D2·D3·SV·38.901 과 같은 14 arm 구성)** | 격자 확정·§5 채움·커밋 뒤에만. `CUDA_VISIBLE_DEVICES= code/run_prior_eval.sh DMC DMCB16e4 d2sx_DMC_N160000_a1[_fb<k>] <bstar> <kronK\|-> <ll_val> <best_sha> <last_sha> "<grid>"` = ① `runner.py run --testbed D2 --prior DMC --cell C2 --n 2560 --chunk 40 --ntrain 160000 --stagec-ckpt ckpt/<stem>_best.pt --tag DMCB16e4` → `runner.py analysis`; ② 보고 전용: 같은 명령을 `ckpt/<stem>.pt --tag DMCB16e4last`; ③ 태그마다 `run_manifest.py`, `guard_report.py`, `recovery_ci.py` 를 −3 dB 로 한 번, 그리고 스크립트가 `results/tables_D2_DMCB16e4.txt` 의 앵커 b\* 판정점을 읽어 한 번; ④ `eval_accept.py`; ⑤ `frontier_ci.py --recovery "raw_DMCB16e4:C2:-3" "raw_B16e4k:C2:-3"` (+ 2차: 판정점 합 대 D2 −3,0,3 합). 선행: `ln -s gmm_fits_D2_DMCB16e4 results/gmm_fits_D2_DMCB16e4last`. 로그 `logs/run_prior_eval_DMCB16e4.log`, 끝 표시 `PRIOR_EVAL_DONE`. 스크립트 인자 값은 §5 가 기록한 것만 넘긴다. 실행은 한 번 |
| **수용 검사** | 38.901 §1 의 (a)~(e) 그대로, prior = DMC: (a) 격자 완전성(full 6 + kron {16..512} 6 + kron 1024·2048(격자 끝이면 4096) 병합 파일, K ≥ 1024 는 후보 3 개); (b) 태그마다 점마다 raw 청크 정확히 {(40k, 40): k = 0..63}, meta `ntrain=160000`, `bstar`·`kron_K`·`ll_val\|<bstar>` 이 §5 와 일치(\|Δll\| ≤ 1e-9), 두 태그의 `bstar`·`kron_K`·`em_sec` 동일, 같은 fits 디렉터리; (c) `stagec_ckpt_id` sha·epoch·best_epoch·role 이 §5 와 일치, 저장된 prior·sigma_tag = DMC, Demo 해시 동일, raw 이름에 `DMC`, analysis 머리말에 `DM_WARNING` 배너("sparse specular" 문구 없음); (d) genie 재현: `--ref-raw raw_DMCB16e4` 로 last 태그의 R5-genie 가 best 태그와 7 SNR 전 시행 비트 동일; (e) GB′ 로그의 `GMM b* = (계열, K)` 가 §5 최종 b\* 와 같고 npz 가 격자 확정 뒤에 쓰였을 것(GB′ 는 격자 확정 뒤 `run_d2_sx.py --prior DMC --ntrain 160000 --tag DMCB16e4 --fallback <k>` 재개(학습 없음)로 한 번 계산; held-out = 스트림 10 = **테스트 풀**). 명령: `eval_accept.py --prior DMC --bstar <kron\|gmmK> [--kron-K <K>] --ll-val <정확한 float> --tag DMCB16e4:best:<sha>:C2 --tag DMCB16e4last:last:<sha>:C2 --ntrain 160000 --ref-raw raw_DMCB16e4 --fits-dir results/gmm_fits_D2_DMCB16e4 --grid "<§5 격자>"`. 어긋나면 그 실행 무효 → 원인 기록, 새 태그 재실행 |
| **측정 판정 (태그 DMCB16e4)** | `08_SPEC` §2 표 B `M-ours-bstar → M-ours-dscore-C-V1`, 판정점 = 앵커 b\* 의 BLER@16 이 [0.005, 0.9] 안에서 \|log10(BLER/0.1)\| 최소 3 SNR(자동), 점마다 exact 양측 부호검정. **`power guard … -> POWERED` 이고 `second arm fewer failures at k/3 points` 의 k ≥ 2 → (i); `first arm fewer failures at k/3` 의 k ≥ 2 → (ii)**; `significant` 토큰은 판정 기준이 아니다. 대조군 `M-ours-bstar → M-ours-bstar-scalar` 도 같은 형식으로 보고 |
| **기전 판독 (`_best` 로 계산, last 도 나란히)** | 38.901 §1 과 같다. 회수율 R = (b\*−V1)/(b\*−genie) 를 실패 수로 −3 dB(1차) 와 판정점 3 점 합(2차) 에서 계산, paired bootstrap 90% CI (B = 2000, `default_rng(20260926)`, 5/95 백분위; `recovery_ci.py`). R < 0 은 그대로 보고. D2 와의 비교는 **비짝 차이 CI** ΔR = R(DMC) − R(D2 B16e4k) (`frontier_ci.py --recovery`) 로 세 갈래: CI < 0 → "DeepMIMO 에서 회수율이 D2 보다 낮다"; CI > 0 → "높다"; 0 을 걸침 → "판정하지 못함". **포화 가드(1차)**: −3 dB 에서 앵커 b\* 의 BLER@16 이 [0.005, 0.9] 밖이거나 b\* 실패 수 ≤ genie 실패 수이면 1차 ΔR 은 "판정하지 못함(범위 밖)" 으로 고정하고 2차만 보고. **정의 불가 규칙**: undefined 복제가 5 % 를 넘거나 점추정이 정의되지 않으면 "판정하지 못함(정의 불가)". ΔR 라벨은 1차에서만, 2차는 보고만. 동등성은 주장하지 않는다 |
| 보고 전용 | V0·V4·V4b, F3 가드 발동률(전 arm); best 대 last V1 짝 부호검정; 동일예산 GB′ (격자 확정 뒤 재계산본; D3 0.559·SV8e 0.918·UMi28 0.920 과 나란히); 격자 표(재시작별 ll_val·n_iter·it_best·재시드·구현 경로); SNR@0.1 격차(격자 밖이면 "n/a" 그대로). **누수 층화(보고 전용, 라벨·검정·CI 없음)**: 태그 DMCB16e4 의 판정점 3 SNR 에서 시행마다 d = min_학습(N′ = 160000, 스트림 7) ‖h − h_학습‖²/‖h‖² (TDMh 의 정의)를 계산해 **d < 0.1 / d ≥ 0.1** 두 층으로 나누고, 층마다 n 과 b\*·V1·genie 의 BLER@16 실패 수, 점추정 R 을 적는다(시행의 채널은 시행 스트림을 runner 와 같은 순서로 다시 뽑아 얻는다; raw 는 건드리지 않는다; 구현 `code/dmc_leak_strata.py` 는 본 실행 뒤, 수치 해석은 사용자). **LoS/NLoS·도시별·BS 별 조건부 BLER 은 계산하지 않는다**(등록하지 않음; 사후 분할 금지). **다중성**: 이 문서의 라벨 검정은 표 B 하나 + ΔR 1차 하나뿐이다. 추세 검정 없음; 결과를 보고 셀·SNR·시나리오·split 을 더하거나 바꾸려면 별도 등록 |
| 비용·일정 [추정] | GPU: 학습 6.5 s/epoch(§4 실측) × patience 정지 시점(D3 514, SV8e 260, UMi28 399 epoch) → 0.4–1 h; GMM 격자 22 작업 ≈ 2–3 h 벽시계(GPU 6 장; UMi28 실측 10:30–13:12 CDT). CPU: BLER 태그당 C2 7 SNR ≈ 35 분(D2 K = 4096 실측 34.4 분) → 2 태그 ≈ 1.2 h (채널 생성 부담 없음) |

## 2. 라벨 (여기서 고정; "측정" 이지 arm 판정이 아니다. UNDECIDED / 비유의는 "판정하지 못함" 이며 어느 쪽의 증거도 아니다)

표 B `b* → V1` (C2, DMCB16e4):

| 결과 | 기록 |
|---|---|
| (i) POWERED 이고 second arm fewer ≥ 2/3 | "DeepMIMO (6 개 도시 28 GHz, block split) 에서 V1 이 b\* 보다 적게 실패 (prior·기전 축 측정, UNGATED)" — §1 회수율·ΔR 문장과 함께 |
| (ii) POWERED 이고 first arm fewer ≥ 2/3 | "DeepMIMO (6 개 도시 28 GHz, block split) 에서 b\* 가 V1 보다 적게 실패" — 회수율(음수 포함)·ΔR 과 함께 |
| (iii) POWERED 이고 어느 쪽도 ≥ 2/3 아님 | "판정하지 못함 (유의 방향 없음)" — 검정력은 있으나 방향이 없다; 동등성의 증거가 아니다 |
| (iv) UNDECIDED (판정점 < 3 이거나 불일치 쌍 ≥ 6 인 판정점이 2 개 미만) | "판정하지 못함 (검정력 미달)"; SNR 격자를 결과 뒤 늘리지 않는다 |
| 학습 실패 (§3d 시행 3 까지) | BLER 미실행, "학습 실패" |

- (ii)(iii)(iv) 어디에서도 "비긴다"·"동등" 문구를 만들지 않는다. 어느 결과도 헤드라인·C2 판정·D2 기록·38.901 기록을 바꾸지 않는다. 문장 범위: DMC 결과로 셀·prior·데이터셋 한정 없는 주장("ray-traced 채널에서", "실측 채널에서")을 쓰지 않는다 — 이 풀·이 split·이 크기 한정이다. 모든 라벨 문장에는 §1 "DMC 고유 사항" 의 (1)(2)(3) 을 붙인다(유한 풀·누수 0.433·outage).

## 3. 미리 적는 예측 (빗나가면 그대로 쓴다; 0단계 채널 통계와 38.901 결과를 본 뒤의 약한 예측이며, DMC 의 BLER 은 본 적이 없다)

1. **표 B: (i)** — V1 이 b\* 보다 적게 실패. 확신 낮음. 근거: 0단계 닫힌 비율이 같은(0.68) 38.901 UMi28 에서 같은 파이프라인이 (i) 였다. 반대 근거(같이 적는다): DeepMIMO 는 내재 차원이 더 낮고(TwoNN 3.4) 채널이 거의 rank-1 이라 kron GMM(성분 = AoA 셀 ⊗ AoD 셀)이 잘 맞는 구조이며 누수 0.433 이 큰 K 의 GMM 을 돕는다. 채점: (i) = 적중; (ii)·(iii) = 빗나감; (iv) = 채점 불가.
2. **크기는 UMi28 보다 작다**: SNR@0.1 격차(b\* − V1) 점추정 < +0.60 dB; 회수율 2차(판정점 합) R ≤ 0.15 (UMi28 0.150). ΔR 1차는 **포화 가드 또는 "D2 보다 낮다"** (CI < 0).
3. `R2-ours-G → b*`: b\* 우세(first arm fewer ≥ 2/3). 확신 높음(0단계 K = 1 NMSE 0.322 → GMM64 0.137).
4. **genie 가 높다**: genie BLER(−3 dB) ≥ 0.10 (테스트 쪽 outage 0.19; D2 0.034). 판정점 3 개는 모두 0 dB 이상.
5. **GB′ 비(확산/GMM b\*, held-out 디노이징 NMSE, σ 격자 20 점) median ≥ 0.9** (D3 0.559, SV8e 0.918, UMi28 0.920).
6. 학습: 발산 없음, patience 정지, **epoch 200–600**. [2026-10-10 17:51 CDT 에 이 줄을 쓸 때 본 것: `logs/train_d2sx_DMC_N160000_a1.log` epoch 51 에서 best val 2.625866e-01 @51 — 학습 곡선이지 판정량이 아니다.]
7. GMM: **b\* = kron, 격자 끝 4096** (D3·UMi28·MIX3 선례; rank-1 에 가까운 채널에 kron 구조가 맞음). 확신 중간.
8. V0: 가드 발동(낮은 SNR 에서 BLER ≥ 0.9). V4·V4b 는 V1 과 비슷하거나 나쁨. best 대 last V1: 판정하지 못함(pooled p > 0.05).
9. 대조군 `b* → b*-scalar`: b\* 우세(first arm fewer ≥ 2/3).
10. 누수 층화(보고 전용): 예측하지 않는다.
11. 빗나갈 경로: (a) (ii) 또는 (iii) → 그대로 기록, 레시피 탐색 없음, 사후 설명은 사용자; (b) R 이 음수 → 그대로 기록; (c) (iv) → 그대로 기록, 격자 확장 없음; (d) 발산 → §3d; (e) full 512 격자 끝 → full 1024 한 번 적합 후 멈춤 + 캐비엇(§1).

## 4. 선행 작업과 실행 현황 (갱신한다; 시각은 `date` 로 읽음)

| 항목 | 상태 · 담당 |
|---|---|
| DeepMIMO 설치·다운로드·풀 빌드(`dmimo_build.py 8`), DMC 연결(`dmimo.py`, PID 11, 보정 상수, `testbed_dm.py`), 기존 경로 비트 동일(`selftest_sv.py` 742 배열·`selftest_mix3.py` 968 배열 IDENTICAL vs 6cf9d698) | **완료·커밋 25f74c0a** (10-10 17:39 CDT 무렵) |
| σ 격자 · 일괄 kron EM 검사 · GPU 큐 스크립트 `run_dmc_gpu.sh` | **완료·커밋 08a3e81d** |
| 학습 DMC (`@train DMC DMCB16e4`, tmux `tb2dmc`, GPU 1) | 진행 중: 큐 시작 10-10 17:44 CDT, 학습 루프 머리말 2026-10-11 07:44:57 KST (= 10-10 17:44 CDT), split_hash 6fc8339a144a6d55, E‖H‖² 1.000000, σ 격자 [3.3459e-02, 8.6642e-01]; 17:46 CDT 에 `taskset -a -p -c 20,116` 으로 HT 쌍 하나에 고정(결과 중립; epoch 22.9 s → 6.5 s) |
| GMM 격자 DMC (21 작업, `logs/tb2_queue.txt`, GPU 0·2–5 → 학습 뒤 GPU 1 도) | 진행 중 → `results/gmm_fits_D2_DMCB16e4/` |
| 병합·격자 끝 규칙·GB′ (수동, C6·D3·38.901 관례) | 대기: kron 1024·2048 병합 → b\* 선택 → 격자 끝이면 4096 병합 → 멈춤 → GB′ 재개 실행 → §5 |
| 적대적 검토(Fable) → v2 → 동결 커밋 | 대기 |
| §5 채우기 → 커밋 → 실행 ①~⑤ → §6 (+ 누수 층화) → 기록 감사(Fable) | 대기 |

## 5. 평가 전 고정 기록 (실행 전에 채우고 커밋한다; 갱신 시각을 적는다)

(격자·학습 완료 뒤 채운다: PID·rung·σ 격자, 보정 상수, testbed 검증, 파일럿, 격자 표(K 별 ll_val·n_iter·it_best·재시드·구현 경로·수렴 규칙), 확장 결정과 시각, 최종 b\*(정확한 float)·격자 끝 캐비엇, 체크포인트 sha·epoch·best_epoch·stopped_by, §3d 적용 여부, GB′, 선행 코드 커밋·fits 링크·평가 스크립트 인자 원문.)

## 6. 결과 (실행 뒤 전사; 생성기와 기록 감사)

(실행 뒤 채운다.)
