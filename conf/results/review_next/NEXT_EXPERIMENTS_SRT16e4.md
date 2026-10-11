# NEXT_EXPERIMENTS_SRT16e4 — Sionna RT 2.1 (내장 도시 장면 3 개 28 GHz, ray-traced, block split) 수신기 BLER: **SRT 측정 + 등록된 baseline 전부** (셀 C2, 동일예산 N′ = 1.6e5, 태그 SRTB16e4 / PILSRT / ALDSRT / SPSRT) — 사전 등록 v2

- 작성: 2026-10-10 23:33 CDT (= 10-11 13:33 KST), Claude Code (Opus 5.5), 초안 v1 (커밋 c9b09731) → 적대적 검토 1 건(Fable 5.1 서브에이전트, 10-10 23:51 CDT 보고; `prereg_reviews_2026-10-10/review_SRT16e4.md`: MUST 2 · SHOULD 10 · NIT 6 — 전부 반영, §4) → **v2 2026-10-10 23:55 CDT (= 10-11 13:55 KST)**. 동결 시각 = 동결 커밋 시각(`DECISIONS.md` 같은 줄). **결과 관측 전**: SRT 의 어떤 체크포인트·적합도 BLER 로 평가된 적이 없다. 커밋 뒤에는 §1~§3 을 바꾸지 않는다; 바꿔야 하면 사용자 승인 + `DECISIONS.md`.
- 사용자 지시(2026-10-10 CDT, 이 세션; `conf/DECISIONS.md` 10-11 KST 줄): "그래 좋다. 그럼 할거 다 하면 Sionna에서도 진행하자" · "오케이. 얼른 해서 sionna 도 돌리자". 앞선 지시가 그대로 적용된다: "Deepmimo 자체에 채널 생성하는 게 있지?" → 채널은 **라이브러리 자체 생성기**로; "기존 실험과 같은 사이즈로 해야해"; "우리 conference에 넣는 11개 그래프 모두 찍어야 해".
- **Sionna = Sionna RT.** Sionna 계열 가운데 3GPP 38.901 (Sionna PHY; prior UMi28 · MIX3) 은 수신기 BLER·baseline·그림까지 이미 있고(RESULTS §10), Sionna RT (광선 추적) 는 0단계 채널 통계뿐이었다(`testbed2_phase0/report_rt.md`: "GMM 친화, 이 계열은 뺀다" — 같은 판정을 받은 DeepMIMO 는 오늘 (i) 가 나왔다, `NEXT_EXPERIMENTS_DMC16e4.md` §6).
- **한 문서에 주 실행과 baseline 확장을 함께 등록한다**(DeepMIMO 는 두 문서였다). 틀(새 규칙 없음): 주 실행 = `NEXT_EXPERIMENTS_DMC16e4.md` v2 §1~§2 (= `NEXT_EXPERIMENTS_38901.md` v2 의 틀), baseline = `NEXT_EXPERIMENTS_DMCBASE16e4.md` v2 §1. 아래 §1 에 **다른 곳과 고정 값**을 적고, 긴 규칙 문장(라벨·수용 검사 (a)~(e)·회수율 CI·ΔR 세 갈래·포화 가드·X\*·R_X·"전부"/"멀어진다" 문장·§3d 사다리·격자 반복 규칙)은 그 두 문서의 문장을 prior SRT · 태그 SRTB16e4 / PILSRT / ALDSRT / SPSRT 로 읽는다.
- 목적: 사이트 특정 ray-traced 채널의 두 번째 출처(Sionna RT)에서 같은 파이프라인·같은 크기·같은 규칙으로 b\* 대 V1 과 등록된 baseline 전부를 잰다. 결과가 어느 쪽이든 보고한다. 헤드라인(C2 1.6e5 B16e4k)·D2·38.901·DeepMIMO 기록은 어느 결과에서도 바뀌지 않는다.
- **작성 시점 공개**: 작성자는 오늘 DeepMIMO 의 결과(주 실행 (i), baseline 16 개 중 15 개 (i), 채널 랭크별 사후 분할)를 모두 본 뒤에 이 문서를 쓴다. SRT 구성(아래 "선택 경위")은 SRT 의 어떤 수신기 실행보다 먼저 정했다. 풀 생성(`srt_build.py`)·σ 격자·학습·GMM 격자는 이 문서의 동결 전에 GPU 에서 시작됐을 수 있다(§4 에 시각) — BLER 은 동결·§5 커밋 뒤에만 돈다.
- **선택 경위(공개)**: (1) 장면 = Sionna RT 2.1 에 들어 있는 실외 도시 장면 가운데 지면이 평평한 것 전부 = **munich · etoile · florence** (0단계가 잰 세 도시). `san_francisco` 는 뺀다: 지형이 평평하지 않아 "위에서 본 표면이 1 m 아래면 지상" 이라는 판정 규칙이 맞지 않고(탐침: 2413 번 추첨에서 3 곳만 통과, 모두 개활지 LoS 1.000 — 세션 콘솔 출력, 파일로 남기지 않은 로그 외 사실), 0단계가 재지 않았다. `simple_street_canyon` 은 도시 장면이 아니고 0단계에서 퇴화·GMM 최친화(0.77–0.87)였다. (2) 깊이 2 · 무작위 BS("rs") = 0단계가 **세 장면 모두에서** 잰 유일한 조합(`et28_d2_rs` 0.65 · `fl28_d2_rs` 0.66 · `mu28_d2_rs` 0.68; K = 64, −3 dB closed). 무작위 사이트라 사이트를 고르는 자유도가 없다. (3) 풀 크기 = 장면당 115,200 쌍, 합 345,600 (DeepMIMO 풀 342,597 과 같은 규모; 공통 크기 = 학습 160000 + 검증 풀 20000 + 테스트 쪽 15 %). 어느 것도 BLER 을 보고 고르지 않았다(어떤 Sionna RT 구성도 수신기에 넣은 적이 없다).

---

## 0. 출발점 (판정에 쓰지 않는다)

**0단계 채널 통계** (`testbed2_phase0/report_rt.md`; 수신기 BLER 미사용; closed = 파일럿 단계 디노이징에서 EM-GMM 이 K = 1 → 잠재 오라클 격차를 메운 비율; 학습 36000 / 검증 4000 / 테스트 2000, 0단계 자체 RNG — 파이프라인 스트림이 아님; **0단계는 경로 방향으로 ULA 를 직접 만들었고 생성 스크립트는 남아 있지 않다 — 이 등록의 풀은 Sionna 자체 배열로 새로 만든 것이라 아래 값과 같은 표본이 아니다**):

| 구성 (8×4, 28 GHz, 깊이 2, rs) | closed 16/64/256 (−3 dB) | closed 64 (+3 dB) | 격차 K1−LO (dB) | LoS | 유효 경로 | 조건부 erank | −3 dB outage | 누수 iid / block |
|---|---|---|---|---|---|---|---|---|
| etoile `et28_d2_rs` | 0.55 / 0.65 / 0.70 | 0.61 | 9.2 | 0.75 | 2.47 | 1.46 | 0.57 | 0.06 / 0.05 |
| florence `fl28_d2_rs` | 0.55 / 0.66 / 0.70 | 0.63 | 9.2 | 0.87 | 2.19 | 1.40 | 0.57 | 0.06 / 0.05 |
| munich `mu28_d2_rs` | 0.58 / 0.68 / 0.73 | 0.66 | 9.5 | 0.83 | 2.30 | 1.35 | 0.59 | 0.13 / 0.10 |
| DeepMIMO 6 개 도시 block (문맥) | 0.56 / 0.68 / 0.71 | 0.63 | — | 0.28 | 1.72 (중앙값) | — | 0.24 | 0.41 (block) |
| D2 S2 (기준값) | 0.19 / 0.26 / 0.29 | 0.25 | 6.6 | 0 | 3.43 | 3.17 | 0.003 | 0.00 |

- 0단계 캐비엇(공개): Sionna RT 는 선택 기준 (1)(GMM 이 메우는 비율)과 (2)(outage)에서 "실패" 로 적혔다(`selection.md` 7·11 행). 이 등록은 그 성질을 고치지 않고 그대로 공개한 채 잰다(§1 "SRT 고유 사항").

**비교 대상 (짝 없음; 문맥용)** — D2 C2 1.6e5 `raw_B16e4k`: −3 dB 실패 b\* 623 / V1 371 / genie 87, 표 B (i) pooled 454:78, R(−3 dB) 0.470 [0.427, 0.512]. 38.901 UMi28: (i) 161:73, R(−3 dB) 0.062. **DeepMIMO `raw_DMCB16e4` (오늘)**: 판정점 +9/+12/+15, 127:46 · 111:42 · 119:36, pooled 357:124, (i); −3 dB 실패 b\* 2232 / V1 2136 / genie 1756 (BLER 0.872 / 0.834 / 0.686); R(−3 dB) 0.202 [0.166, 0.240], 판정점 합 0.279; ΔR −0.268 [−0.325, −0.209]; SNR@0.1 전 arm 격자 밖; b\* kron 4096 (격자 끝); GB′ median 0.715; baseline 16 개 중 (i) 15, V1-pilot (iii); Perfect CSI 실패는 최대 특이값 에너지 비중 ≥ 0.95 인 시행(시행의 0.665–0.672; `DMCB16e4_genie_rank.txt`, 보고 전용)에 몰림.

**풀** (`code/srt_build.py` → `code/run_srt_build.sh 2`, GPU 2, 10-10 23:07 → 23:24 CDT; `logs/srt_build.log`): munich 115200 쌍 / 139 사이트(210 추첨, 333 s) · etoile 115200 / 126 (190, 313 s) · florence 115200 / 145 (282, 356 s) → **345,600 쌍 = 학습 풀 273,748 + 검증 풀 20,000 + 테스트 풀 51,852** (테스트 비중 0.1500), 20 m 타일 5,982 개 중 911 개가 테스트. sha256[:16]: `H.npy` **b9f47f1c7c10a014** · `split.npy` **bd7019926eb03e6f** (= `dmimo.POOL_SHA[('SRT', 8)]`); part 파일 munich e3de2857fba8986b · etoile b5c927eed23b0527 · florence d9c04a5449711167 (보존용, 고정 대상 아님). 빌드 시점의 코드: git 89cde8a8 + 미커밋 작업 트리(= 커밋 d1fd0227 의 `srt_build.py`; 빌드 뒤 그 파일을 바꾸지 않았다). 보정(학습 스트림 7, n = 160000; `dmimo.py calibrate 8 SRT`): P_RAW 1.027118787916483, TRAIN_SHA d15b033bc915cf88 (커밋 f379258f).

**testbed 검증** (`results/testbed_SRT.txt` @d1fd0227 + 보정 상수, 2026-10-11 13:25 KST = 10-10 23:25 CDT; `code/testbed_dm.py SRT`, BLER 없음; 이 풀 구성의 0단계 프로브가 없어 TDMc·TDMd 의 프로브 대조는 없다 — 보고만):

| 검사 | SRT | (문맥) DMC |
|---|---|---|
| TDMa 정규화(검증 스트림 8, n = 20000; 4 s.e. 대역) | mean ‖H‖²/(NrNt) = 0.99564 (s.e. 0.00249) **PASS**; 블록 전력 CV 0.354 | 1.00214; CV 0.396 |
| TDMb 원소별 E\|H_ab\|² (보고) | 0.9912–1.0021 | 0.9960–1.0110 |
| TDMc 풀 정체 | 장면당 115200 쌍(= TARGET), 사이트 139 / 124 / 139 (쌍을 낸 사이트), **LoS 비율 0.848**, 평균 경로 수 2.95 **PASS** | LoS 0.281 |
| TDMd 파일럿 단계 K = 1 Gaussian NMSE @ −3 dB (보고) | 0.3191 | 0.3161 |
| TDMe T2b 파일럿 결정 / erank(C_ens) / 빔공간 top-4 | erank(Rt) 3.392/4 < 3.6 → **eigen 정렬** / 26.03/32 / 중앙값 0.892, 평균 0.871 | 3.422 → eigen / 25.27 / 0.872, 0.854 |
| TDMf block split | 세 풀 서로소·전체, 양쪽에 걸친 타일 없음 **PASS** | PASS |
| TDMg split 이동(보고) | LoS 학습 쪽 0.8476 / 테스트 쪽 0.8482; **outage P(MI < 4 bit) @ −3 dB 검증 0.1399 / 테스트 0.1349**; K = 1 NMSE 검증 0.3191 / 테스트 0.3207; 테스트 쪽 mean ‖H‖²/(NrNt) 0.9917 | outage 0.2170 / 0.1905 |
| TDMh 누수(보고) | 테스트 2000 표본의 최근접 학습 채널(N′ = 160000): 정규화 제곱거리 중앙값 0.0500, **< 0.1 비율 0.634** | 0.1261, 0.433 |
| 종합 | **ALL PASS** (3 s CPU) | ALL PASS |

- **채널 랭크(채널 통계; 풀에서 직접 계산, BLER 아님)**: 최대 특이값의 에너지 비중 s₁²/Σs² ≥ 0.95 인 쌍의 비율 — 풀의 쌍 전부에서 — SRT 학습 풀 0.815 / **테스트 풀 0.796** (0.80–0.95: 0.159, < 0.80: 0.045; 중앙값 0.9997), DeepMIMO 학습 풀 0.682 / 테스트 풀 0.658 (중앙값 0.988). 즉 SRT 테스트 채널의 약 0.80 이 사실상 rank-1 이다(LoS + 지면 반사가 같은 steering 벡터). 0단계 표의 outage 0.57–0.59 는 이 풀에서 재현되지 않는다(0.135; 0단계는 배열·표본 추출이 달랐다).

**σ 격자** (`runner.py sigma --testbed D2 --prior SRT --cell C1 C2 --tag SRT`, 다른 prior 와 같은 절차; `sigma_grid_D2_SRT.{txt,npz}` @d1fd0227, 10-10 23:25 CDT): 20 점, ν_q [2.269e-03, 1.463e+00] → σ_t [3.368e-02, 8.551e-01]. **공개: 이 측정으로 SRT 의 테스트 시행 0..63 (C1·C2, 7 SNR) 이 Gaussian 수신기로 한 번 실행됐다**(BLER 은 읽지도 쓰지도 않음; 모든 prior 의 관례).

**일괄 kron EM 검사** (`results/nr8b_batched_check_SRT_n160000.txt` @d1fd0227, GPU 2): (a) N′ = 160000 K = 512 6 반복 PASS (max\|Δll\| 2.6e-08, 공분산 상대 차 2.1e-07), (b) 재시드 활성 N = 10000 K = 512 15 반복 PASS (재시드 2329/2329) → kron 계열은 일괄 경로, full 계열은 정확 경로.

**기존 경로 불변**: `selftest_sv.py` 742 배열 · `selftest_mix3.py` 968 배열 IDENTICAL vs 63cbb295; DMC `analysis` 표가 git 줄을 빼고 동일; `dmimo.py selfcheck 8 DMC` train sha e6ddafc27367f975 (불변).

---

## 1. 고정되는 것

| 항목 | 값 |
|---|---|
| **셀·예산·시행 (기존 실험과 같은 크기 — 사용자 지시)** | DMC16e4 §1 첫 행 그대로: C2 = 8×4, T 16, Tp 4, K = 42, rate-1/2 conv (133,171)_8, QPSK, 16 반복, 7 SNR (−3 … 15 dB; **결과 뒤 격자를 늘리지 않는다**), n = 2560, 테스트 시행 0..2559 (chunk 40), 수신기 CPU complex128, 시행 시드 `common.trial_rng` 에 **PID SRT = 12** (다른 모든 prior 와 다른 스트림 → D2·DeepMIMO 와의 비교는 짝 없음). N′ = 160000 = `arms.training_set("D2", "SRT", 8, 4, 160000)` (스트림 7) 을 GMM 적합과 score 학습(자체 9:1)이 함께 쓴다; GMM 검증 5000 = 스트림 8 |
| **지위** | **UNGATED** → "prior·기전 축 측정" 이며 arm 판정이 아니다. SRT 는 어느 결과에서도 헤드라인이 되지 않는다 |
| **생성 모델** (`code/srt_build.py` 머리말 = 원문; 동결 — 바꾸려면 새 결정 + 새 prior id) | **Sionna RT 2.1** (`sionna-rt` 2.1.0, mitsuba 3.9.1, drjit 1.5.0; torch 환경에 이미 있음). 장면 `munich` · `etoile` · `florence`, 28 GHz. **채널 = Sionna 자체 생성기**: `PathSolver()` (max_depth 2, LoS on, 정반사 on, 난반사·굴절·회절 off, samples_per_src 1e7, synthetic_array) + `PlanarArray` (BS 1×8, UE 1×4, 등방성 V 편파, 반파장 — 장치 boresight 에 수직인 수평 ULA) + `Paths.cfr` (주파수 오프셋 0 → 반송파에서의 협대역 채널). BS 가 광선 원천(상향링크는 상반성: H_ul = H_dlᵀ). **사이트 "rs"**: 사이트마다 새 BS — 장면 xy 경계 상자에서 균등, 지상(위에서 내려 본 표면이 1 m 아래)일 때만 채택, 높이 10 m, boresight ~ U[−π, π); 사이트마다 후보 UE 8192 개 — boresight 둘레 120° 섹터·반경 10–200 m 고리의 **실외(같은 지상 판정)** 부분에서 면적 균등, 높이 1.5 m, yaw ~ U[−π, π). 후보 8192 개 = 균등 추첨 4 × 8192 개 가운데 실외인 것의 앞 8192 개이며, **실외 점이 8192 개에 못 미치는 사이트(섹터 고리의 실외 비율이 약 25 % 미만)는 통째로 건너뛴다** — 건물이 빽빽한 곳의 사이트가 덜 대표된다(검토 S1). 지상 판정은 위에서만 본다: 벽으로 둘러싸인 마당 같은 자리도 통과하며 그런 BS 는 거의 어떤 UE 에도 닿지 않는다(빌드 로그의 munich 사이트 둘이 그랬다 — 쌍 1 개·7 개; 검토 S2). **쌍** = 경로가 하나라도 있는 후보, 사이트당 후보 순서대로 최대 1000 개; 장면당 115,200 쌍에서 멈춘다(마지막 사이트는 잘림). 난수: 장면 i 의 추첨 `default_rng([20260926, 2, 12, 12, i])`, split `default_rng([20260926, 2, 12, 12, 3])` (`srt_build._rng`); solver 시드 = 사이트 번호. **쌍별 정규화** H/√(기준 소자 쌍의 Σ\|a_l\|²) (pathloss 제거, 다중경로 간섭은 남음) 뒤 앙상블 정규화(`dmimo.py` `P_RAW`, 학습 스트림 7 로 보정). 수신기 packing 만 배열로 넘긴다(기본 `Scene.targets` 는 수신기를 하나씩 넣어 느리다): 위치·방향 동일, 소자 오프셋 차 ≤ 1.4e-9 m, 유효 경로 마스크 동일, 채널 상대 오차 ≤ 3.7e-07 (`srt_build.py selfcheck munich`, 결정적 solver, 사이트 3 곳 × 수신기 64 개; **이 수치는 세션 콘솔 출력이며 파일로 남기지 않았다 — 로그 외 사실**, 재실행 명령은 같은 것; float32 위치의 위상 분해능 수준) — 경로 추적·전계·배열 합성·주파수 응답은 Sionna 것 그대로 |
| **block split 과 스트림** (`dmimo.py` 머리말; DeepMIMO 와 같은 코드) | (장면, floor(xy/20 m)) 타일을 섞어 쌍의 15 % 이상을 담을 때까지 = 테스트 타일; 나머지 타일의 쌍 가운데 동결된 무작위 20,000 = 검증 풀, 나머지 = 학습 풀. 스트림 → 풀: 학습 스트림 7 → 학습 풀에서 서로 다른 n 쌍; 스트림 8 → 검증 풀; 스트림 10·모든 시행 스트림·`sparse_tune` 개발 스트림 → 테스트 풀 복원 추출. 다른 시드 배치는 오류. 풀 파일 `~/data/sionna_rt/srt_Nr8/{H.npy, split.npy}` 는 git 밖, sha 로 고정(`dmimo.POOL_SHA[('SRT', 8)]`; §0) |
| **SRT 고유 사항 (공개; 고치지 않고 그대로 잰다)** | (1) **유한 풀**: 테스트 시행은 테스트 풀 51,852 쌍에서 복원 추출(한 점의 2560 시행 안의 기대 중복 약 2560²/(2·51852) ≈ 63 쌍; 채널은 같고 데이터·잡음은 독립) — 채널 모집단은 "이 풀의 테스트 타일" 이며 다른 장면·다른 사이트로의 일반화는 주장하지 않는다. (2) **누수**: §0 TDMh 의 값(테스트 채널 가운데 학습 집합에 정규화 제곱거리 0.1 안의 이웃이 있는 비율); 두 arm 에 같은 조건. (3) **outage·랭크**: §0 TDMg 의 값; 0단계에서 Sionna RT 는 DeepMIMO 보다 LoS 가 많고(0.75–0.87 대 0.28) 조건부 유효 랭크가 낮았다 → **Perfect CSI 를 포함한 모든 arm 의 BLER 이 DeepMIMO 보다 높을 수 있고 SNR@0.1 은 격자 밖일 수 있다**(사용자에게 미리 알림, 10-10 CDT). 판정점은 규칙이 자동으로 고른다. (4) **모집단 가중**: 장면당 같은 쌍 수; 사이트당 최대 1000 쌍(가시 영역이 넓은 사이트가 덜 대표됨); 실외 비율이 낮은 사이트는 건너뜀(생성 모델 칸); UE 는 실외만. (5) **split 이동**: 테스트 타일은 다른 장소(§0 TDMg); 장면 비중이 학습 풀 munich / etoile / florence = 0.329 / 0.336 / 0.335 → 테스트 풀 0.356 / 0.319 / 0.325 (타일 추첨의 결과). (6) **재생성**: `PathSolver` 는 기본(비결정적 후보 생성) 으로 돌렸다 — 같은 시드로 다시 만들면 수치적으로 같은 풀이 나오더라도 sha 가 같다는 보장이 없다. 풀은 sha 로 고정하고 장면별 part 파일을 보존한다. (7) V1·b\* 의 학습·모델 선택은 학습 타일 안에서만 한다; baseline 조정용 개발 채널은 테스트 풀에서 나온다(DMCBASE16e4 "DMC 고유 1" 과 같음 — baseline 에 유리한 방향). (8) σ 격자 측정은 테스트 시행 0..63 을 Gaussian 수신기로 한 번 실행한다(ν_q 만 기록; 모든 prior 의 관례) |
| **파일럿** | D2 의 T2b 규칙을 학습 집합의 Rt 에 적용(`dmimo.RT`; §0 TDMe 의 결정) |
| **GMM 격자와 b\*** | DMC16e4 §1 과 같다: full K ∈ {16 … 512} (정확 경로) + kron K ∈ {16 … 512} + kron 1024·2048·4096 재시작 후보 3 개씩(일괄 경로; §0 의 일괄 EM 검사 PASS 가 전제), 선택 = 검증 우도 최대(스트림 8). 반복 규칙: b\* 가 kron 2048 이면 4096 병합, **4096 에서 멈춘다** + 캐비엇; b\* 가 full 512 이면 full 1024 한 번 + 캐비엇. **BLER 은 선택에 쓰지 않는다.** 큐 `code/run_srt_gpu.sh` (22 작업, GPU 0·1·2). 병합·선택·끝 규칙·fits 링크는 `code/run_srt_post_select.sh <동결 커밋>` 이 한다(동결 커밋이 v2 인지와 적합 21 작업의 rc=0 을 확인; 선택 결과는 `logs/tb2_post_SRT.sel` 파일로 넘김; 로그 `logs/tb2_post_SRT.log`; full 512 분기는 손으로 — 등록 규칙 그대로) |
| **체크포인트·평가 가중치·학습 실패 처리·σ 격자** | DMC16e4 §1 과 같다: 동결 레시피 `run_d2_sx.py --prior SRT --ntrain 160000 --tag SRTB16e4 --fallback 1 --no-gbprime` (479,426 params; patience 20, 최소 200, 최대 3000 epoch), rung **D2SXSRT160000**, attempt 1 → `ckpt/d2sx_SRT_N160000_a1{,_best}.pt`; 판정 태그 `SRTB16e4` = `_best`, `SRTB16e4last` = last-EMA 보고 전용; §3d 사다리; σ 격자 = prior 자체 격자 `sigma_tag = "SRT"` (§0) |
| **순서 규칙** | 동결 커밋 → kron 1024·2048 병합·b\* 선택(→ 4096) → §5 채움·커밋 → 주 실행 → 수용 → baseline 단계 → §6. 동결 전에 끝난 적합·학습이 있어도 **작성자는 동결 전에 다음을 읽지 않는다**: `results/gmm_fits_D2_SRTB16e4/*.npz` 와 `logs/tb2_gpu{0,1,2}.log` (ll_val 이 찍힌다), `logs/tb2_post_SRT.{log,sel}`, `results/sparse/{tune,pick}_SRT_C2.json` 과 `logs/sparse_tune_SRT_C2.log`, `results/ald/tune_PILSRT.json` 과 `logs/ald_tune_PILSRT.log`, `results/d2_gbprime_SRT*`·`logs/gbprime_SRTB16e4.log` (읽는 것은 `logs/tb2.log` 의 작업 시작·종료 줄, 파일 개수, 학습 로그의 epoch 줄뿐; 읽었다면 해당 예측을 "관측됨(채점 제외)" 로 바꾼다). 동결 줄(`DECISIONS.md`)에 그때 무엇이 존재했는지 적는다. **병합 파일 `fit_SRT_Nr8_kronK{1024,2048,4096}_n160000.npz`·`tb2_post_SRT.sel` 의 mtime 은 동결 커밋 시각보다 뒤여야 한다**(§5 에 나란히 적는다). 희소 baseline 조정(`sparse_tune.py --prior SRT --cell C2 --n 256`, CPU 2 스레드, BLER 없음)은 풀이 고정되는 대로 시작해 다른 단계와 겹쳐 돈다. **GB′ 는 보고 전용이고 §5 커밋 뒤에 계산한다**(`run_srt_post_gpu.sh <k> GBP <GPU>`; 주 실행과 겹쳐도 된다; 값은 §6 에만 — 작성자는 §5 를 쓸 때 GB′ 를 보지 않는다; DMC16e4 는 §5 전에 계산했다 — 여기서는 대기 시간을 줄이려고 바꾼다; 재개 실행은 정지한 체크포인트를 다시 쓰지 않는다). ALD 개발 재생성·조정(`run_srt_post_gpu.sh <k> ALD <GPU>`)은 §5 전에 한다(그 sha 가 §5 에 들어간다) |
| **실행 — 주 실행** | DMC16e4 §1 "실행" 그대로: `CUDA_VISIBLE_DEVICES= code/run_prior_eval.sh SRT SRTB16e4 d2sx_SRT_N160000_a1[_fb<k>] <bstar> <kronK\|-> <ll_val> <best_sha> <last_sha> "<grid>"` (인자는 §5 가 기록한 것만; `code/run_srt_eval.sh` 에 원문). 실행은 한 번; 실행 중 main 커밋 금지 |
| **실행 — baseline** | DMCBASE16e4 §1 "실행" 그대로, prior SRT: 선행 `ald.py regen --tag PILSRT --prior SRT --cell C2 --fits-tag SRTB16e4 --set dev` → `ald.py tune --tag PILSRT --ckpt ckpt/<stem>_best.pt` (`code/run_srt_post_gpu.sh`); 본 실행 `code/run_srt_base.sh <ckpt_stem> <best_sha16> <pick_sha16> <tune_ald_sha16> <bstar: kron\|gmm<K>> <kron_K\|-> <ll_val>` (b\* 가 full 계열이어도 같은 스크립트; 검토 M2) — 순서 PIL → ALD → SP → `pair_baselines`. **ALD 추정에 쓸 빈 GPU 가 없으면 `DEFER_ALD=1` 로 SP 를 먼저 돌리고 GPU 가 비면 같은 스크립트를 다시 돌린다**(단계는 서로의 출력을 읽지 않는다 — DMCBASE16e4 §6 감사에서 확인; 썼으면 §6 에 적는다; 그 경우 ALD 단계 전에 PIL·SP 의 부분 결과가 디스크에 생기며 작성자가 볼 수 있다 — 조정값·규칙·명령은 §5 에서 이미 고정이라 바꿀 것이 없다). raw 마다 깨끗한 커밋 하나; runner 가 도는 동안 main 커밋 금지. SPARSE 격자는 한 판으로 끝낸다(끝값이면 끝값 + 캐비엇) |
| **수용 검사** | 주 실행: DMC16e4 §1 (a)~(e) 그대로, prior = SRT — 단 (c) 의 배너 조건은 글자로: **두 태그의 `results/tables_D2_<tag>.txt` 에 문자열 `SITE-SPECIFIC RAY-TRACED TESTBED (prior SRT)` 가 있고 문자열 `CLAIM TESTBED -- sparse specular` 가 없다**(DMC16e4 감사 N4 의 문구 문제를 고침); (c) 가운데 `eval_accept.py` 가 검사하지 않는 항목(배너·raw 이름·`N_train` 줄·저장된 prior / sigma_tag·Demo 해시)은 표·manifest·체크포인트를 읽어 확인하고 §6 에 그렇게 적는다. (e) 는 "GB′ 로그의 `GMM b* =` 줄이 §5 최종 b\* 와 같고 `d2_gbprime_SRT_*.npz` 의 mtime 이 격자 확정(병합 파일 mtime) 뒤" 를 §6 에서 확인하며, **어긋나면 GB′ 수치만 무효(보고하지 않음)이고 주 실행의 유효성과는 무관하다**. baseline: DMCBASE16e4 §1 "수용 검사" 그대로(태그마다 `eval_accept.py`, R5-genie 가 `raw_SRTB16e4` 와 비트 동일, `pair_cross`·`pair_ald` 무결성, pick 재현·`meta\|sparse`) |
| **측정 판정** | 주: 표 B `M-ours-bstar → M-ours-dscore-C-V1` (판정점 = 앵커 b\* 의 BLER@16 이 [0.005, 0.9] 안에서 \|log10(BLER/0.1)\| 최소 3 SNR, 점마다 exact 양측 부호검정; POWERED 이고 second arm fewer ≥ 2/3 → (i); first arm fewer ≥ 2/3 → (ii); 둘 다 아님 → (iii); UNDECIDED → (iv)). baseline: `pair_baselines.py --base raw_SRTB16e4 --pil raw_PILSRT --ald raw_ALDSRT --est PILSRT --extra raw_SPSRT --add-baselines SBL-loop SBL-pilot OMP-pilot --cell C2 --prior SRT --r0 at1 --provenance manifest` → 표 B `X → V1`, X ∈ 𝔅 15 → 새 라벨 15 개 + 인용 1 개; 출력 `results/review_next/pairB_SPSRT.txt` |
| **기전 판독** | DMC16e4 §1 그대로: R = (b\*−V1)/(b\*−genie) 를 −3 dB(1차)와 판정점 합(2차)에서, paired bootstrap 90 % (B 2000, `default_rng(20260926)`); ΔR = R(SRT) − R(D2 B16e4k) 비짝 CI 세 갈래 "Sionna RT 에서 회수율이 D2 보다 낮다 / 높다 / 판정하지 못함"; 포화 가드(−3 dB 에서 앵커 b\* 의 BLER@16 이 [0.005, 0.9] 밖이거나 b\* 실패 ≤ genie 실패 → 1차 ΔR "판정하지 못함(범위 밖)", 2차만 보고); 정의 불가 규칙 |
| **보고 전용** | V0·V4·V4b, F3 가드, best 대 last V1, GB′, 격자 표, SNR@0.1; **누수 층화** `code/dmc_leak_strata.py --tag SRTB16e4 --prior SRT` (DMC16e4 §1 의 정의 그대로); **랭크 층화**(라벨·검정·CI 없음): `code/rank_strata.py --tag SRTB16e4 --prior SRT` — −3 dB 와 판정점 3 SNR 에서 시행의 채널을 시행 스트림 재생으로 얻어 최대 특이값의 에너지 비중 {≥ 0.95, 0.80–0.95, 0.60–0.80, < 0.60} 네 층으로 나누고 층마다 n 과 b\*·V1·genie 의 BLER@16 을 적는다(DeepMIMO 의 사후 분할 `DMCB16e4_genie_rank.txt` 와 같은 정의; 여기서는 미리 등록); **채널 추정 NMSE 의 CDF**(사용자 제안 10-10 CDT "아니면 CDF를 그려볼까?"; 라벨·검정·CI 없음): `conference/figures/paper_f33cdf.py SRT` (@331dba15; 머리말이 규칙 원문) — 패널 넷 = −3 dB 와 판정점 3 SNR(`tables_D2_SRTB16e4.txt` 에서 읽음), 곡선 = 범례 가운데 추정이 있는 10 개(Perfect CSI 제외), 값 = raw 의 `nmse` 마지막 열(@16; Pilot-only LMMSE 는 별칭 `R0-pilot@1` 의 한 열), 2560 시행 전부(비유한·비양수는 +∞ 로 세고 개수를 기록), x 범위는 그리기에만 적용, 기록에 중앙값·90 백분위 표 — DeepMIMO 에는 결과를 본 뒤 같은 스크립트로 그렸다(`F33cdf_DMC_wide`), 여기서는 미리 고정한다; ALD·SPARSE 조정 표, `pair_cross`·`pair_ald` 의 등록 비교 |
| **그림** | 11 곡선(`paper_f16deep.SHOW`)을 전 SNR n = 2560 으로: `conference/figures/paper_f21dmc.py SRT` (@f379258f 에서 prior 인자로 일반화함; `SETS["SRT"]`) → `F21srt_col` (모양·범례·검사 동일; y 아래 끝 = 사다리 {0.5, 0.3, 0.2, 0.1, …} 가운데 모든 점과 Wilson 막대 아래 끝보다 작은 가장 큰 값 — 눈으로 정하지 않는다). n = 20480 보강은 하지 않는다 |
| **다중성** | 주 라벨 1 + baseline 새 라벨 15; 등록 사이 보정 없음(다른 데이터셋과 같은 관례) |
| 비용·일정 [추정] | 풀 생성 GPU 한 장 ≈ 20 분(munich 실측 333 s); 학습 6 s/epoch × 300–900 epoch ≈ 0.5–1.5 h; GMM 격자 22 작업 GPU 3 장 ≈ 1.5–2.5 h (DeepMIMO: 6 장 48 분); SPARSE 조정 ≈ 3 h (DeepMIMO 2 h 53 분); 주 실행 2 태그 ≈ 1.8 h (DeepMIMO 56 + 52 분); baseline ≈ 10 분 |

## 2. 라벨 (여기서 고정; "측정" 이지 arm 판정이 아니다)

표 B `b* → V1` (C2, SRTB16e4):

| 결과 | 기록 |
|---|---|
| (i) | "Sionna RT (내장 도시 장면 3 개 28 GHz, block split) 에서 V1 이 b\* 보다 적게 실패 (prior·기전 축 측정, UNGATED)" — 회수율·ΔR 문장과 함께 |
| (ii) | "Sionna RT (내장 도시 장면 3 개 28 GHz, block split) 에서 b\* 가 V1 보다 적게 실패" — 회수율(음수 포함)·ΔR 과 함께 |
| (iii) | "판정하지 못함 (유의 방향 없음)" |
| (iv) | "판정하지 못함 (검정력 미달)"; SNR 격자를 결과 뒤 늘리지 않는다 |
| 학습 실패 | BLER 미실행, "학습 실패" |

- baseline: (i)~(iv) 는 같은 규칙을 X → V1 에 적용. **"전부" 문장**: 주 라벨이 (i) 이고 15 개가 모두 (i) 일 때만 "Sionna RT (…) 에서 V1 이 등록된 baseline 전부(16 개, 희소 baseline 포함)보다 적게 실패 (UNGATED 측정)"; 여기에 R_{X\*}(−3 dB) 90 % CI 하한 > 0 (`pair_baselines` 의 condition 줄 MET) 이면 "…전부와 멀어진다"; 아니면 (i) 의 수와 (i) 가 아닌 arm 의 이름·라벨을 그대로 적는다.
- 어디에서도 동치 문구를 만들지 않는다. 모든 라벨 문장에 §1 "SRT 고유 사항" 의 (1) 유한 풀 · (2) 누수 · (3) outage·랭크 · (7) 개발 채널(baseline 라벨에만) 을 붙인다. 범위: 이 풀·이 split·이 크기 한정 — 데이터셋·풀·split·크기 한정이 없는 일반화 문장은 쓰지 않는다.

## 3. 미리 적는 예측 (빗나가면 그대로 쓴다; DeepMIMO 결과와 §0 의 SRT 채널 통계를 본 뒤의 예측이며, SRT 의 BLER 은 본 적이 없다)

**동결 시각에 이미 관측된 항목은 예측이 아니라 관측이다.** 작성 시점: 학습은 돌고 있고(아래 7 의 대괄호), GMM 격자는 시작됐으며, 작성자는 SRT 의 ll_val·GB′·pick·ALD 점수를 하나도 읽지 않았다.

1. **표 B: (i)** — V1 이 b\* 보다 적게 실패. 확신 중간. 근거: 같은 파이프라인이 38.901 UMi28 과 DeepMIMO 에서 (i). 반대 근거: 테스트 채널의 0.79 가 사실상 rank-1 이고 누수가 0.634 라 큰 K 의 kron GMM 이 잘 맞는 구조다; rank-1 층에서는 prior 와 무관하게 실패하는 블록이 많아 불일치 쌍이 줄 수 있다. 채점: (i) = 적중; (ii)·(iii) = 빗나감; (iv) = 채점 불가.
2. **Perfect CSI 가 DeepMIMO 보다 높다** — 네 문장을 따로 채점한다: (a) genie BLER(−3 dB) ≥ 0.70 (DeepMIMO 0.686); (b) genie BLER(+15 dB) ≥ 0.25 (DeepMIMO 0.239); (c) `b* → V1` 의 판정점 = +9 / +12 / +15; (d) 표 A 의 14 arm 모두 SNR@0.1 이 "> 15".
3. **1차 ΔR 의 포화 가드가 "−3 dB 에서 b\* 의 BLER@16 > 0.9" 조건으로 발동한다** → "판정하지 못함(범위 밖)" (DeepMIMO 는 0.872 로 아슬아슬하게 안쪽이었다). 채점: 그 조건으로 발동 = 적중; 발동하지 않거나 다른 조건(b\* 실패 ≤ genie 실패)으로만 발동 = 빗나감. 발동하지 않을 때의 ΔR 방향은 예측하지 않는다.
4. 회수율 2차(판정점 합) R ∈ [0.10, 0.40] (DeepMIMO 0.279, UMi28 0.150).
5. `R2-ours-G → b*`: b\* (second arm) 가 ≥ 2/3 점에서 적게 실패. 확신 높음.
6. **GB′ median ≤ 0.90** (DeepMIMO 0.715, UMi28 0.920).
7. 학습: 발산 없음 **이고** patience 정지 **이고** epoch ∈ [300, 1200] (DeepMIMO 832) — 셋 다 맞아야 적중. [2026-10-10 23:34 CDT 에 이 줄을 쓸 때 본 것: `logs/train_d2sx_SRT_N160000_a1.log` epoch 30, best val 1.585689e-01 @30 — 학습 곡선이지 판정량이 아니다; 정지 시점·stopped_by 미관측]
8. GMM: **b\* = kron, 격자 끝 4096** (D3·UMi28·MIX3·DeepMIMO 선례).
9. V0: 가드 발동이고 −3·0 dB 에서 BLER ≥ 0.9. best 대 last V1: 판정하지 못함(pooled p > 0.05). (V4·V4b 는 예측하지 않는다 — DeepMIMO 감사 N3: 문턱 없는 예측은 채점할 수 없다.)
10. 대조군 `b* → b*-scalar`: 라벨 규칙으로 (iii) — POWERED 이고 second·first arm fewer 가 모두 2/3 미만 (UMi28·DeepMIMO 선례). 채점: (iii) = 적중; (i)·(ii) = 빗나감; (iv) = 채점 불가.
11. baseline 15 개: **(ii) 0 이고 (i) ≥ 13**; `V1-pilot` 은 (i) 가 아니다((iii) 또는 (iv)); `pair_ALDSRT.txt` 의 A3 (`ALDv-pilot → V1-pilot`) = (i); `pairB_SPSRT.txt` 의 실패 수 표에서 −3·0 dB 모두 `OMP-pilot` < `R0-pilot@1` 이고 `SBL-pilot` < `R0-pilot@1`. 네 문장을 따로 채점한다.
12. 랭크 층화(보고 전용 수치로 채점; `SRTB16e4_rank_strata.txt` 의 +15 dB 블록 — `rank_strata.py` 는 −3 dB 와 판정점만 찍으므로 **+15 dB 가 판정점이 아니면 채점 불가**): Perfect CSI 의 BLER 이 비중 ≥ 0.95 층에서 ≥ 0.25 이고, 비중 < 0.80 인 두 층을 합쳐(두 층의 genie 실패 수 합 / n 합) ≤ 0.02 — 두 문장을 따로 채점.
13. 누수 층화·NMSE CDF: 예측하지 않는다.
14. 빗나갈 경로: (a) (ii) 또는 (iii) → 그대로 기록, 레시피 탐색 없음, 사후 설명은 사용자; (b) R 이 음수 → 그대로; (c) (iv) → 그대로, 격자 확장 없음; (d) 발산 → §3d; (e) b\* 가 full 512 → full 1024 한 번 + 캐비엇; (f) baseline 에 (ii) 가 하나라도 → 그대로, 재조정 없음.

## 4. 선행 작업과 실행 현황 (갱신한다; 시각은 `date` 로 읽음)

| 항목 | 상태 |
|---|---|
| Sionna RT 풀 빌더·연결(`srt_build.py`, `dmimo.py` 일반화, PID 12, 접점, `run_srt_*.sh`, `rank_strata.py`) + 기존 경로 비트 동일 검사 | **완료·커밋 d1fd0227** |
| 풀 생성(GPU 2) → sha 고정·보정·testbed·σ 격자·일괄 EM 검사 | **완료·커밋 f379258f** (10-10 23:07 → 23:27 CDT; §0) |
| 학습 SRT (`@train SRT SRTB16e4`, tmux `tb2srt`, GPU 2) | 진행 중: 큐 시작 10-10 23:29 CDT (git f379258f), 학습 머리말 2026-10-11 13:30:02 KST, split_hash 5ef5dca3dca07cf3, E‖H‖² 1.000000, σ 격자 [3.3679e-02, 8.5515e-01]; 23:30 CDT 에 `taskset -a -p -c 22,118` 로 HT 쌍 하나에 고정(결과 중립) |
| GMM 격자 SRT (21 작업, `logs/tb2_queue.txt`, GPU 0·1 → 학습 뒤 GPU 2 도) | 진행 중: 10-10 23:32 CDT 부터 (`logs/tb2.log`) → `results/gmm_fits_D2_SRTB16e4/` |
| SPARSE 조정 (`run_srt_sparse_tune.sh`, tmux `sptsrt`, CPU 2 스레드) | 진행 중: 10-10 23:29 CDT 시작 (git f379258f) → `results/sparse/{tune,pick}_SRT_C2.json` (동결 전에 읽지 않는다) |
| 이 문서 초안 v1 → 적대적 검토(Fable) → v2 → 동결 커밋 | 검토 끝(10-10 23:51 CDT 보고; MUST 2 · SHOULD 10 · NIT 6). 반영: M1 GB′ 는 §5 뒤(`run_srt_post_gpu.sh` 를 lane 하나씩 `ALD` / `GBP` 로 나눔; §1·§4 일치), M2 `run_srt_base.sh` 7 인자(full 계열 b\* 도 실행 가능), S1 사이트 건너뜀 규칙·S2 둘러싸인 자리 공개(`srt_build.py` 머리말에도 — 문구만, 동작 줄 불변), S3 장면 비중, S4·S5 예측 2·3·10·12 의 채점 규칙, S6 열람 금지 파일 목록·병합 mtime 규칙, S7 `DEFER_ALD` 의 부분 결과, S8 NMSE CDF 스크립트 인용, S9 수용 (c) 의 글자 조건, S10 `run_srt_post_select.sh` 를 동결 커밋에 포함(선택은 파일로 전달), N1 랭크 비중을 풀 전체로 재계산(0.794 → 0.796 등), N2·N6 로그 외 사실 표시, N3 기대 중복·시드 배치·"0.67" 출처, N4 `dmc_leak_strata.py` 머리말, N5 문구. 검토가 실행으로 확인한 것: 풀 sha·크기·타일·P_RAW·TRAIN_SHA·§0 수치 재계산 일치, 스트림 → 풀 매핑, `analysis.PAT`·배너·rung 색인(1753, 충돌 없음), `bash -n`. **동결 시점의 관측 상태는 `DECISIONS.md` 동결 줄에.** 초안 2026-10-10 23:33 CDT |
| 병합·b\* 선택(`run_srt_post_select.sh`) → ALD 개발 재생성·조정(`run_srt_post_gpu.sh <k> ALD <GPU>`) → §5 채움·커밋 → 주 실행 (+ 겹쳐서 GB′: `run_srt_post_gpu.sh <k> GBP <GPU>`) → 수용 → baseline (`run_srt_base.sh`) → §6 → 기록 감사(Fable) → 그림 | 동결 2e50f269 (10-10 23:56:31 CDT) → 학습 시행 1 발산(00:25 CDT) → 시행 2 patience(04:16 CDT), 적합 21 작업 끝(01:27 CDT), SPARSE 조정 끝(01:18 CDT) → 병합·선택 04:18 CDT (b\* kron 4096) → ALD 조정 04:18–04:28 CDT → §5 채움(2026-10-11 04:29 CDT) → 이 커밋 뒤 주 실행 |
| 공개: GPU 0·1 에서 돌던 DeepMIMO 시드 a2·a3 학습(이 등록과 무관)을 10-10 23:31 CDT 에 epoch 394 에서 멈추고 GPU 를 SRT 격자에 넘겼다(`logs/seeds_DMC_train.log`) | — |

## 5. 평가 전 고정 기록 (실행 전에 채우고 커밋한다)

갱신 2026-10-11 04:29 CDT (Opus 5.5). 값은 파일에서 읽었다(생성기 `prereg_audit_2026-10-11/s5_gen.py SRT SRTB16e4 d2sx_SRT_N160000_a1 d2sx_SRT_N160000_a1_fb2` — fit 파일·mtime·`torch.load`·`sha256`; `logs/tb2.log`, `logs/tb2_post_SRT.{log,sel}`, `results/sparse/pick_SRT_C2.json`, `results/ald/tune_PILSRT.json`). **모두 동결(2e50f269, 10-10 23:56:31 CDT) 뒤에 읽었다.**

| 항목 | SRT (SRTB16e4) |
|---|---|
| PID · rung · σ 격자 태그 | 12 · D2SXSRT160000 (ix 1753) · `SRT` σ_t [3.367917786039236e-02, 8.551482095651048e-01] (20 점) |
| 풀·보정 | `H.npy` b9f47f1c7c10a014 / `split.npy` bd7019926eb03e6f; P_RAW 1.027118787916483, TRAIN_SHA d15b033bc915cf88; testbed ALL PASS (§0); 파일럿 eigen 정렬 (erank Rt 3.392) |
| 격자: K 별 ll_val (재시작, n_iter/it_best, 재시드) · 구현 경로 | **full** (정확 경로, 전부 κ = 0): 16 66.788 (r2, 102/90, 0) / 32 85.908 (r1, 227/200, 0) / 64 100.122 (r1, 396/370, 0) / 128 110.845 (r2, 257/250, 2) / 256 119.968 (r2, 235/230, 17) / 512 124.780 (r2, 120/110, 5,163). **kron** (일괄 경로, κ = 0): 16 76.149 (r2, 69/60, 0) / 32 103.787 (r1, 93/90, 0) / 64 130.962 (r1, 154/150, 0) / 128 152.849 (r1, 115/110, 0) / 256 172.906 (r0, 193/190, 0) / 512 188.662 (r0, 231/230, 0) / **1024 199.61260681203092** (r0, 195/190, rs 147; r1 198.662 147/140 rs 45, r2 199.299 162/160 rs 35) / **2048 206.7566280497025** (r0, 259/250, rs 51,196; r1 206.294 270/260 rs 58,610, r2 205.834 208/190 rs 42,715) / **4096 208.1279194544014** (r2, 266/260, rs 481,555; r0 207.608 233/230 rs 413,092, r1 207.551 299/290 rs 532,037). 상한 500 정지 없음(전 파일 최대 396 반복). 파일 24 개 = full 6 + kron 16..512 6 + 후보 9 + 병합 3. 적합 21 작업 10-10 23:32 → 10-11 01:27 CDT, 모두 rc=0 (`logs/tb2.log`; GPU 0·1) |
| 확장 결정과 시각 (`code/run_srt_post_select.sh 2e50f269`, `logs/tb2_post_SRT.log`; **순서 규칙**: 동결 10-10 23:56:31 CDT 가 먼저) | 병합 파일 mtime: kron 1024 10-11 04:18:18 CDT · 2048 04:18:22 CDT → b\* = kron 2048 (206.7566, 기본 격자 끝) → 규칙대로 kron 4096 (후보 mtime 00:56:11 / 01:16:02 / 01:27:33 CDT) 병합 04:18:28 CDT → b\* = kron 4096 → **4096 에서 멈춤**. full 계열 끝 규칙 미발동(b\* 가 kron; full 512 124.780). `tb2_post_SRT.sel` = `kron 4096 208.1279194544014`. 모두 동결 뒤 ✓ (적합 21 작업 가운데 5 개는 동결 전에, 16 개는 동결 뒤에 끝났다 — 작성자는 동결 전 어떤 ll_val 도 읽지 않았다) |
| 최종 b\*: 계열·K·ll_val, 격자 끝 캐비엇 | **b\* = kron K = 4096, ll_val 208.1279194544014** (재시작 2). **격자 끝**(2048 대비 +1.371 nat, 오르는 중) + **수렴 캐비엇**(재시드 48.2 만; 4096 후보 셋 207.55–208.13). 미병합 후보 없음. 수용 검사 `--bstar kron --kron-K 4096 --ll-val 208.1279194544014` |
| **학습 — §3d 사다리 발동** | **시행 1 (클리핑 없음) 발산**: `ckpt/d2sx_SRT_N160000_a1.pt` epoch 498, stopped_by **diverged** (best val 0.14295178651809692 @489; 10-10 23:30 → 10-11 00:25 CDT, 3,346.9 s, 6.72 s/epoch; 23:30 CDT 에 `taskset -a -p -c 22,118` 고정) → 규칙대로 같은 GPU 2 에서 **시행 2 = 기울기 클리핑 1.0** 이 자동으로 이어 돎(`run_tb2.sh train_chain`; 같은 rung·attempt = 같은 데이터 스트림, split_hash 5ef5dca3dca07cf3): `ckpt/d2sx_SRT_N160000_a1_fb2.pt` epoch 617, stopped_by **patience** (best val 0.14180772006511688 @597; 00:25 → 04:16 CDT, 13,862.3 s, 22.47 s/epoch — **이 프로세스는 고정하지 않아 느렸다**(실행 사실, 결과 중립)). `logs/tb2_train_state_SRT.txt` = `2 patience`. 발산한 시행 1 의 체크포인트로는 평가하지 않는다(§1) |
| 체크포인트 (평가에 쓰는 것 = 시행 2) | best `ckpt/d2sx_SRT_N160000_a1_fb2_best.pt` **7c7354bef3bb1e40** (epoch 597, role best, grad_clip 1.0); last `…_fb2.pt` **918a424724fcb0ab** (epoch 617, best_epoch 597, stopped_by patience, role last); prior SRT, sigma_tag SRT, rung D2SXSRT160000, attempt 1. (시행 1: best 4400a75e008483e5 @489 / last 0d9b77e0a5d4f1ea — 쓰지 않음) |
| SPARSE 조정 (`run_srt_sparse_tune.sh`, CPU 2 스레드) | 10-10 23:29 → 10-11 01:18 CDT (`SPARSE_TUNE_DONE rc=0`; wall_sec 6539.4; git f379258f). `pick_SRT_C2.json` sha256[:16] **d7fac04ee4e601fe**, `tune_SRT_C2.json` **43df40e773c2a643** (mtime 01:18:59 CDT — 동결 뒤 생성). 고른 값: **SBL ρ = 16 = 격자 끝**(`edge_rho_sbl` true; 점수 −16.147 dB), n_em −3 dB 3 · 0…15 dB 5 (끝값 없음); **OMP ρ = 16 = 격자 끝**(`edge_rho_omp` true; −15.528 dB), L −3…15 dB = 1 / 2 / 2 / 3 / 4 / 4 / 6 (끝값 없음). **두 ρ 모두 끝값 + 캐비엇, §1 대로 확장하지 않는다** |
| ALD 조정 (`run_srt_post_gpu.sh 2 ALD 2`, GPU 2) | 10-11 04:18 → 04:28 CDT rc=0. `results/ald/tune_PILSRT.json` sha256[:16] **42d51362230f5e25** (git 2e50f269, ckpt `ckpt/d2sx_SRT_N160000_a1_fb2_best.pt`, ckpt_sha 7c7354bef3bb1e40, n_dev 512, dev_skip 2560), `tune_PILSRT_curves.npz` 015e04645fa76df9. 고른 값: **c = 0.01, β = 0.005** (개발 최적 c 0.01 · β 1e-05 −17.827 dB; 저자 기본값 β 0.005 가 −17.801 dB 로 0.1 dB 안 → 유지; β 축 두 번 확장, 확장 뒤 끝값 없음); 멈춤 단계 −3…15 dB = 425 / 476 / 543 / 600 / 600 / 600 / 600; 개발 NMSE −9.34 / −11.72 / −15.35 / −18.15 / −20.97 / −23.47 / −25.61 dB |
| GB′ | **아직 계산하지 않았다**(§1: §5 커밋 뒤, 보고 전용) — 이 커밋 뒤 `run_srt_post_gpu.sh 2 GBP <GPU>` |
| §3 예측 가운데 BLER 전에 채점되는 것 | **7 (발산 없음 · patience · epoch ∈ [300, 1200]): 빗나감** — 시행 1 이 발산했다(부분: 최종 시행은 patience 정지 ✓, epoch 617 ∈ [300, 1200] ✓). **8 (b\* = kron 4096): 적중**. 나머지는 실행 뒤 |
| 실행 사실(공개) | (1) 큐가 도는 10-11 00:00 ~ 04:17 CDT 동안 이 세션은 대기했다(알림 조건 = 22 작업 종료). (2) GMM 적합이 끝난 뒤(01:27 CDT) GPU 0·1 은 컨테이너 밖 프로세스가 다시 잡았다(04:17 CDT 에 장당 42,063 MiB) — 이후 GPU 작업은 GPU 2 한 장. (3) 예전 큐 실행기(`tb2dmc`)는 10-10 23:19 CDT 에 정지 파일로 끝냈고 SRT 큐는 `GPUS='2 0 1'` 로 새로 띄웠다 |
| 스크립트 인자 원문 | 주 실행: `CUDA_VISIBLE_DEVICES= code/run_prior_eval.sh SRT SRTB16e4 d2sx_SRT_N160000_a1_fb2 kron 4096 208.1279194544014 7c7354bef3bb1e40 918a424724fcb0ab "full:16,32,64,128,256,512 kron:16,32,64,128,256,512,1024,2048,4096"` (= `code/run_srt_eval.sh`, 이 커밋에서 채움). baseline: `bash code/run_srt_base.sh d2sx_SRT_N160000_a1_fb2 7c7354bef3bb1e40 d7fac04ee4e601fe 42d51362230f5e25 kron 4096 208.1279194544014`. 실행 커밋 = 이 §5 커밋; fits 링크 `gmm_fits_D2_SRTB16e4last` 는 `run_srt_post_select.sh` 가 10-11 04:18 CDT 에 만듦 |

## 6. 결과 (주 실행 2026-10-11 04:30~06:11 CDT, `run_prior_eval.sh` @28f38d55 = §5 커밋; baseline 06:13~06:27 CDT, `run_srt_base.sh` @6cbf9a5e; 이 절은 추가만 한다; 기록 2026-10-11 06:30 CDT, Opus 5.5 — 전사만, 해석 없음)

수치의 출처: 생성기 `prereg_audit_2026-10-11/s6_gen.py SRTB16e4` (표 B 줄은 `results/tables_D2_SRTB16e4{,last}.txt` 원문, 실패 수·BLER 은 `raw_SRTB16e4{,last}` 를 `analysis.load_raw` 로 읽음, 회수율·ΔR·수용·가드는 각 파일 원문) — `s6_gen.py DMCB16e4` 가 DeepMIMO 의 §6 초안(`prereg_audit_2026-10-10/s6_draft_raw.md`)을 재현하는 것을 SRT 의 BLER 전에 확인한 생성기다(커밋 28f38d55 = 실행 커밋에 들어 있음; 그 확인은 세션 콘솔 출력 — 로그 외 사실).

**실행·운영 기록**: `code/run_srt_eval.sh` (= §5 의 인자 원문) 한 번, tmux `srteval`, 10-11 04:30 CDT 시작(git 28f38d55 = §5 커밋, `conf/code` clean). 측정 태그 `SRTB16e4` (`_fb2_best`) 04:30 → 05:20 CDT (runner 50.7 분), 보고 태그 `SRTB16e4last` 05:20 → 06:10 CDT (49.0 분), 각각 448 작업 · 192 워커; 수용 검사 06:10 CDT, `PRIOR_EVAL_DONE` 06:11 CDT. manifest `run_manifest_SRTB16e4{,last}.json` 둘 다 git 28f38d55 · config_hash 8a027a73c8dbe626. 실행 중 main 커밋 없음(다음 커밋 6cbf9a5e 는 `PRIOR_EVAL_DONE` 뒤). 함께 돈 것(§1 순서 규칙에 등록): 보고 전용 GB′ (`run_srt_post_gpu.sh 2 GBP 2`, GPU 2 + CPU 여러 스레드) 가 04:30 → 06:12 CDT 에 겹쳤다. 비용: §1 추정 2 태그 ≈ 1.8 h → 실측 50.7 + 49.0 분.

**수용 검사**: **`ACCEPT: OK -- SRTB16e4, SRTB16e4last`** (`results/review_next/SRTB16e4_accept.txt`; `eval_accept.py` rc 0 — §1 (a)~(d): 격자 full 6 + kron 9 · K ≥ 1024 후보 3 개, 청크 {(40k, 40)} × 7 SNR, meta ntrain 160000 / bstar kron / kron_K 4096 / ll_val = §5, 체크포인트 sha·role, last 의 R5-genie 가 best 와 비트 동일). §1 (c) 의 글자 조건: 두 태그의 `results/tables_D2_<tag>.txt` 에 `SITE-SPECIFIC RAY-TRACED TESTBED (prior SRT)` 가 한 번씩 있고 `CLAIM TESTBED -- sparse specular` 는 0 번(`grep -c`). `eval_accept.py` 가 검사하지 않는 항목은 표·manifest·체크포인트를 읽어 확인했다: raw 이름에 `SRT` (`D2_C2_SRT_Nr8_T16_Tp4_eig_snr…`, 태그당 448 파일), 학습 예산 줄 `N_train=160000`, 저장된 prior·sigma_tag = SRT (§5; GB′ 로그 머리말도 `prior=SRT … sigma_tag=SRT`), 두 태그의 Demo 해시(t2_route_a 95a5408901ec125c · t2_trellis 31cd0ee9c68e972b · t2_gmm d064e58c7510c769)·manifest config_hash 동일. (e) GB′: 로그의 `GMM b* = kron (kron K=4096) @N=160000` = §5 최종 b\* ✓, `d2_gbprime_SRT_N160000_a1_fb2.npz` mtime 10-11 06:12:38 CDT > 병합 파일(kron 4096) mtime 04:18:28 CDT ✓ → GB′ 수치 유효. 판정점(앵커 b\*, 자동): **+9 / +12 / +15 dB** (SNR 격자의 위쪽 끝 3 점).

### 6.1 측정 판정 — 표 B `b* → V1` (C2, 태그 SRTB16e4 = `_fb2_best`, UNGATED)

| 태그 | 판정점 | a:b (부호검정 p) | pooled | 가드 | 라벨 | SNR@0.1 격차 b\*−V1 |
|---|---|---|---|---|---|---|
| **SRTB16e4 (판정)** | +9 / +12 / +15 | 145:38 (6.3e-16) · 126:22 (6.5e-19) · 132:33 (3.2e-15) | 403:93 (5.2e-47) | POWERED, second arm fewer 3/3 | **(i) "Sionna RT (내장 도시 장면 3 개 28 GHz, block split) 에서 V1 이 b\* 보다 적게 실패 (prior·기전 축 측정, UNGATED)"** | n/a (둘 다 > 15 dB) |
| SRTB16e4last (보고) | +9 / +12 / +15 | 148:40 (9e-16) · 128:24 (2.4e-18) · 130:36 (1.1e-13) | 406:100 (9.7e-45) | POWERED, 3/3 | (같은 문자열, 보고 전용) | n/a |

라벨 문장에 붙는 것(§2): **(1) 유한 풀** — 테스트 시행은 테스트 타일 51,852 쌍에서 복원 추출, 채널 모집단은 "이 풀의 테스트 타일"; **(2) 누수** — 테스트 쪽 채널의 0.634 가 학습 집합에 정규화 제곱거리 0.1 안의 이웃을 가짐(TDMh; 판정점 시행에서는 0.597 / 0.607 / 0.620 — 6.2); **(3) outage·랭크** — 테스트 쪽 −3 dB P(MI < 4 bit) 0.1349, 테스트 풀의 0.796 이 최대 특이값 에너지 비중 ≥ 0.95 (판정점 시행에서는 0.787 / 0.790 / 0.803 — 6.2), genie BLER@16 은 −3 dB 0.817 · +15 dB 0.499. 범위: 이 풀·이 split·이 크기 한정. 헤드라인·D2·38.901·DeepMIMO 기록 불변.

대조군 `b* → b*-scalar` (+9 / +12 / +15): 29:35 (0.53) · 37:39 (0.91) · 33:42 (0.36), pooled 99:116 (p 0.28), POWERED, 0/3 · 0/3 → (iii) 유의 방향 없음(판정하지 못함). `R2-ours-G → b*` (앵커 R2, +9 / +12 / +15): 265:54 · 237:40 · 219:42, pooled 721:136, POWERED, b\* (second arm) 가 3/3 에서 적게 실패. SNR@0.1 격차는 모든 쌍에서 n/a.

**기전 판독**: 회수율 R (best, paired 90 %): −3 dB 0.268 [0.221, 0.315] (b\* 2404 / V1 2320 / genie 2091); 판정점 +9 / +12 / +15 0.549 [0.463, 0.628] / 0.619 [0.535, 0.708] / 0.647 [0.554, 0.738], 합 **0.601 [0.553, 0.650]** (b\* 4536 / V1 4226 / genie 4020). last: −3 dB 0.275 [0.226, 0.323], 판정점 합 0.593 [0.542, 0.643]. **1차 ΔR (−3 dB)**: **포화 가드 발동** — 앵커 b\* 의 BLER@16 이 −3 dB 에서 0.939 로 [0.005, 0.9] 밖(b\* 2404 > genie 2091 이라 다른 조건은 해당 없음) → **등록 라벨 "판정하지 못함(범위 밖)"**. `recovery_diff_SRTB16e4.txt` 에는 도구가 −3 dB 줄도 찍었으나 가드에 따라 판독하지 않고 여기에 옮기지 않는다. **2차(보고)**: 판정점 합 0.601 vs D2 B16e4k (−3, 0, +3 합) 0.509 [0.470, 0.544] → ΔR = +0.092 [90 % 비짝 +0.030, +0.157], undefined 0 (last 태그는 2차 줄을 계산하지 않았다 — `run_prior_eval.sh` 가 best 태그에만 돌린다). 실패 수 격차(판정점 3 점 합; `recovery_diff_SRTB16e4.txt`): V1 − genie 206 [176, 236], b\* − genie 516 [477, 558] (D2 −3·0·+3 합: 363 [332, 396], 739 [697, 781]).

### 6.2 보고 전용

**BLER@16 (괄호 = 실패 수 / 2560; best 태그; R0-pilot 은 @1)**

| arm | −3 dB | 0 dB | +3 dB | +6 dB | +9 dB | +12 dB | +15 dB |
|---|---|---|---|---|---|---|---|
| **V1** | 0.906 (2320) | 0.803 (2056) | 0.696 (1781) | 0.649 (1661) | 0.588 (1504) | 0.543 (1391) | 0.520 (1331) |
| V1 (last 태그) | 0.905 (2318) | 0.805 (2061) | 0.698 (1788) | 0.650 (1663) | 0.587 (1503) | 0.543 (1391) | 0.522 (1336) |
| V4 | 0.910 (2329) | 0.802 (2054) | 0.690 (1767) | 0.649 (1662) | 0.584 (1496) | 0.545 (1396) | 0.516 (1321) |
| V4b | 0.907 (2323) | 0.801 (2051) | 0.692 (1772) | 0.649 (1662) | 0.586 (1501) | 0.547 (1400) | 0.519 (1328) |
| **b\*** | 0.939 (2404) | 0.847 (2169) | 0.758 (1941) | 0.693 (1774) | 0.629 (1611) | 0.584 (1495) | 0.559 (1430) |
| b\*-scalar | 0.941 (2408) | 0.848 (2171) | 0.758 (1940) | 0.693 (1774) | 0.632 (1617) | 0.585 (1497) | 0.562 (1439) |
| gmm32 | 0.952 (2438) | 0.865 (2214) | 0.789 (2019) | 0.714 (1828) | 0.654 (1673) | 0.606 (1551) | 0.584 (1495) |
| R2-ours-G | 0.961 (2461) | 0.895 (2291) | 0.818 (2093) | 0.752 (1924) | 0.712 (1822) | 0.661 (1692) | 0.628 (1607) |
| R1-turbo | 0.979 (2507) | 0.936 (2396) | 0.861 (2205) | 0.800 (2047) | 0.745 (1906) | 0.685 (1754) | 0.655 (1676) |
| R0-pilot (@1) | 0.995 (2547) | 0.977 (2500) | 0.933 (2389) | 0.894 (2289) | 0.860 (2202) | 0.817 (2092) | 0.793 (2029) |
| pilot_C (@16; 문맥) | 0.973 (2491) | 0.909 (2326) | 0.829 (2121) | 0.761 (1948) | 0.716 (1832) | 0.662 (1696) | 0.635 (1626) |
| R4-scvamp | 0.987 (2526) | 0.953 (2440) | 0.904 (2313) | 0.862 (2206) | 0.824 (2109) | 0.799 (2045) | 0.772 (1977) |
| R3-bigamp | 0.977 (2502) | 0.937 (2399) | 0.892 (2284) | 0.856 (2191) | 0.854 (2187) | 0.865 (2214) | 0.872 (2232) |
| R4-llr | 0.994 (2544) | 0.975 (2496) | 0.960 (2458) | 0.930 (2381) | 0.907 (2322) | 0.873 (2234) | 0.837 (2143) |
| V0 | 0.989 (2531) | 0.975 (2495) | 0.966 (2473) | 0.961 (2460) | 0.961 (2460) | 0.949 (2429) | 0.873 (2236) |
| **genie** | 0.817 (2091) | 0.731 (1871) | 0.635 (1626) | 0.604 (1546) | 0.553 (1416) | 0.518 (1327) | 0.499 (1277) |

- **SNR@0.1**: 14 arm(genie 포함; R0-pilot 은 @1 · @16 두 읽기) 모두 "> 15" (격자 안에서 BLER 0.1 에 닿지 않음) → 격차는 전부 n/a. §1 대로 격자를 늘리지 않았다.
- **V4 · V4b · V0 (앵커 b\*, +9 / +12 / +15)**: `b* → V4` 156:41 · 120:21 · 140:31, pooled 416:93, second arm fewer 3/3; `b* → V4b` 154:44 · 118:23 · 135:33, pooled 407:100, 3/3; `b* → V0` 0:849 · 1:935 · 2:808, pooled 3:2592, first arm (b\*) fewer 3/3. 판정점 3 점 실패 수 합: V1 4226 / V4 4213 / V4b 4229; 7 SNR 합: V1 12044 / V4 12025 / V4b 12037 (검정 없음).
- **`V1 → genie`** (앵커 genie, +9 / +12 / +15): 111:23 · 89:25 · 73:19, pooled 273:67, genie 가 3/3 에서 적게 실패. `b* → genie`: 223:28 · 181:13 · 172:19, pooled 576:60.
- **best 대 last V1 짝 부호검정** (+9 / +12 / +15; a = best 만 실패, b = last 만 실패): 11:10 (p 1) · 12:12 (1) · 11:16 (0.442), pooled 34:38 (p 0.724) → 판정하지 못함.
- **F3 가드 발동률** (`results/guard_D2_SRTB16e4{,last}.txt`; NMSE > 10 또는 비유한): V0 만 대량 — best −3 … +15 dB 0.965 / 0.960 / 0.927 / 0.923 / 0.904 / 0.881 / 0.790, last 0.968 / 0.964 / 0.936 / 0.920 / 0.913 / 0.885 / 0.789. 그 밖: +3 dB 에서 gmm32 · R0-pilot · R1-turbo · R2-ours-G · R4-llr · R4-scvamp 각 1 시행(두 태그 같음). b\* · b\*-scalar · V1 · V4 · V4b · R3-bigamp 는 발동 없음.
- **동일예산 GB′** (`logs/gbprime_SRTB16e4.log`, last 파일 `d2sx_SRT_N160000_a1_fb2.pt`; 10-11 04:30 → 06:12 CDT, GPU 2, rc 0): median **0.5425** (min 0.4535 · max 0.8722; D3 0.559 · DeepMIMO 0.715 · SV8e 0.918 · UMi28 0.920 과 나란히). 수용 (e) 통과(위).
- **누수 층화** (보고 전용 — 라벨·검정·CI 없음; `code/dmc_leak_strata.py --tag SRTB16e4 --prior SRT` @2e50f269 (스크립트의 마지막 커밋), 10-11 06:12 CDT 실행(실행 시 HEAD 28f38d55) → `results/review_next/SRTB16e4_leak_strata.txt`; 정렬 검사(R5-genie 처음 40 시행, raw 와 비트 동일) 세 SNR 모두 OK). 칸 = n: b\* / V1 / genie 실패 수 → 점추정 R:

| SNR | d 중앙값 | d < 0.1 비율 | d < 0.1 | d ≥ 0.1 |
|---|---|---|---|---|
| +9 dB | 0.0545 | 0.597 | 1529: 1294 / 1231 / 1188 → 0.594 | 1031: 317 / 273 / 228 → 0.494 |
| +12 dB | 0.0577 | 0.607 | 1553: 1241 / 1189 / 1143 → 0.531 | 1007: 254 / 202 / 184 → 0.743 |
| +15 dB | 0.0520 | 0.620 | 1587: 1243 / 1169 / 1145 → 0.755 | 973: 187 / 162 / 132 → 0.455 |
| 판정점 3 점 합 | — | — | 4669: 3778 / 3589 / 3476 → 0.626 | 3011: 758 / 637 / 544 → 0.565 |

- **랭크 층화** (보고 전용 — 라벨·검정·CI 없음; `code/rank_strata.py --tag SRTB16e4 --prior SRT` @d1fd0227, 10-11 06:12 CDT 실행(HEAD 28f38d55) → `results/review_next/SRTB16e4_rank_strata.txt`; 정렬 검사 네 SNR 모두 OK). 층 = 시행 채널의 최대 특이값 에너지 비중; 칸 = n (비율): genie / V1 / b\* 의 BLER@16 (실패 수):

| SNR | ≥ 0.95 | 0.80–0.95 | 0.60–0.80 | < 0.60 |
|---|---|---|---|---|
| −3 dB | 2063 (0.806): 0.948 / 0.984 / 0.990 (1955 / 2029 / 2043) | 386 (0.151): 0.313 / 0.661 / 0.785 (121 / 255 / 303) | 107 (0.042): 0.131 / 0.318 / 0.523 (14 / 34 / 56) | 4 (0.002): 0.250 / 0.500 / 0.500 (1 / 2 / 2) |
| +9 dB | 2014 (0.787): 0.700 / 0.738 / 0.788 (1410 / 1487 / 1587) | 422 (0.165): 0.014 / 0.031 / 0.055 (6 / 13 / 23) | 117 (0.046): 0.000 / 0.026 / 0.009 (0 / 3 / 1) | 7 (0.003): 0.000 / 0.143 / 0.000 (0 / 1 / 0) |
| +12 dB | 2022 (0.790): 0.654 / 0.686 / 0.728 (1322 / 1387 / 1473) | 410 (0.160): 0.007 / 0.005 / 0.037 (3 / 2 / 15) | 120 (0.047): 0.017 / 0.017 / 0.058 (2 / 2 / 7) | 8 (0.003): 0.000 / 0.000 / 0.000 (0 / 0 / 0) |
| +15 dB | 2055 (0.803): 0.620 / 0.645 / 0.691 (1274 / 1326 / 1419) | 401 (0.157): 0.007 / 0.010 / 0.025 (3 / 4 / 10) | 99 (0.039): 0.000 / 0.010 / 0.010 (0 / 1 / 1) | 5 (0.002): 0.000 / 0.000 / 0.000 (0 / 0 / 0) |

### 6.3 baseline — 표 B `X → V1`: 새 라벨 15 개 + 주 라벨 1 개 (C2, prior SRT, UNGATED; 앵커 = X, R0-pilot 은 @1)

수치의 출처: `results/review_next/pairB_SPSRT.txt` (생성기 `prereg_audit_2026-10-11/s6_base_gen.py` 가 표·요약 줄을 정규식으로 읽어 옮김 — `pairB_SPDMC.txt` 에 돌리면 DMCBASE16e4 §6.1 의 16 행을 글자 그대로 재현한다), `pair_PILSRT.txt`, `pair_ALDSRT.txt`, `{PILSRT,ALDSRT,SPSRT}_accept.txt`, `logs/run_srt_base.log`, `logs/run_D2_{PILSRT,ALDSRT,SPSRT}.log`.

**실행·운영 기록**: `bash code/run_srt_base.sh d2sx_SRT_N160000_a1_fb2 7c7354bef3bb1e40 d7fac04ee4e601fe 42d51362230f5e25 kron 4096 208.1279194544014` (= §5 의 인자 원문) **한 번**, tmux `srtbase`, 10-11 06:13 CDT 시작(git 6cbf9a5e; `DEFER_ALD` 스위치 없이 — 등록 순서 PIL → ALD → SP 그대로). PIL runner 2.0 분 → 06:16 CDT `ACCEPT: OK -- PILSRT`, `pair_cross` 무결성 OK(raised 0 / 0) → ALD 시험 사이트 재생성(CPU) → ALD 추정 GPU 2 (06:16 CDT; `results/ald/ald_PILSRT.npz` sha256[:16] 2c3de1268dc25017) → ALD runner 0.4 분 → 06:17 CDT `ACCEPT: OK -- ALDSRT`, `pair_ald` 무결성 OK(raised ALD 시행 없음) → pick 규칙 재현(`rule-reproduced=True`, 메모리 필요 ≈ 264 GB / 가용 1020 GB) → SP runner 10.0 분 → `meta|sparse` 불일치 0, raised 0 / 0 / 0 → 06:27 CDT `ACCEPT: OK -- SPSRT` → `pair_baselines` rc 0 → 06:27 CDT `SRT_BASE_DONE rc=0`. raw 마다 깨끗한 커밋 하나: `pair_baselines` 머리말 `git base=28f38d55 extra0=6cbf9a5e pil=6cbf9a5e ald=6cbf9a5e; integrity: OK` (manifest 세 개 모두 git 6cbf9a5e). 커밋 6cbf9a5e 는 `PRIOR_EVAL_DONE` 뒤·baseline 시작 전에(runner 가 돌지 않을 때) 주 실행의 결과 파일만 더한 것이다(`git diff 28f38d55 6cbf9a5e -- conf/code Demo` 비어 있음). 비용: §1 추정 ≈ 10 분 → 실측 06:13 → 06:27 CDT.

| X | 판정점 [dB] | a:b (X 만 실패 : V1 만 실패) | pooled (p) | 가드 · 유의 점 수 | 라벨 | F_X − F_V1 (−3 dB) | R_X (−3 dB) [90 %] | R_X (판정점 합) [90 %] |
|---|---|---|---|---|---|---|---|---|
| b\* (주 라벨, 6.1) | +9 / +12 / +15 | 145:38 · 126:22 · 132:33 | 403:93 (5.2e-47) | POWERED, V1 3/3 · X 0/3 | **(i)** | 84 | 정의 안 됨 (범위 밖: 0.9391) | 0.601 [0.553, 0.650] |
| b\*-scalar | +9 / +12 / +15 | 147:34 · 135:29 · 137:29 | 419:92 (7.4e-51) | POWERED, V1 3/3 · X 0/3 | **(i)** | 88 | 정의 안 됨 (범위 밖: 0.9406) | 0.614 [0.566, 0.661] |
| gmm32 | +9 / +12 / +15 | 208:39 · 189:29 · 186:22 | 583:90 (2.6e-89) | POWERED, V1 3/3 · X 0/3 | **(i)** | 118 | 정의 안 됨 (범위 밖: 0.9523) | 0.705 [0.668, 0.742] |
| R0-pilot@1 | +9 / +12 / +15 | 698:0 · 703:2 · 698:0 | 2099:2 (0) | POWERED, V1 3/3 · X 0/3 | **(i)** | 227 | 정의 안 됨 (범위 밖: 0.9949) | 0.911 [0.899, 0.923] |
| R1-turbo | +9 / +12 / +15 | 419:17 · 378:15 · 362:17 | 1159:49 (3e-276) | POWERED, V1 3/3 · X 0/3 | **(i)** | 187 | 정의 안 됨 (범위 밖: 0.9793) | 0.843 [0.823, 0.864] |
| R2-ours-G | +9 / +12 / +15 | 341:23 · 319:18 · 298:22 | 958:63 (2.5e-206) | POWERED, V1 3/3 · X 0/3 | **(i)** | 141 | 정의 안 됨 (범위 밖: 0.9613) | 0.813 [0.789, 0.838] |
| R3-bigamp | +6 / +9 / +12 | 541:11 · 687:4 · 825:2 | 2053:17 (0) | POWERED, V1 3/3 · X 0/3 | **(i)** | 182 | 정의 안 됨 (범위 밖: 0.9773) | 0.884 [0.871, 0.898] |
| R4-llr | +12 / +15 | 846:3 · 815:3 | 1661:6 (0) | UNDECIDED, V1 2/2 · X 0/2 | **(iv)** | 224 | 정의 안 됨 (범위 밖: 0.9938) | 0.933 [0.921, 0.947] |
| R4-scvamp | +9 / +12 / +15 | 611:6 · 658:4 · 649:3 | 1918:13 (0) | POWERED, V1 3/3 · X 0/3 | **(i)** | 206 | 정의 안 됨 (범위 밖: 0.9867) | 0.902 [0.890, 0.916] |
| bstar-pilot | +9 / +12 / +15 | 155:43 · 135:24 · 140:28 | 430:95 (6.8e-52) | POWERED, V1 3/3 · X 0/3 | **(i)** | 110 | 정의 안 됨 (범위 밖: 0.9492) | 0.619 [0.572, 0.668] |
| V1-pilot | +9 / +12 / +15 | 26:23 · 18:15 · 7:7 | 51:45 (0.61) | POWERED, V1 0/3 · X 0/3 | **(iii)** | 59 | 정의 안 됨 (범위 밖: 0.9293) | 0.028 [-0.047, 0.102] |
| ALD-pilot | +9 / +12 / +15 | 103:49 · 151:46 · 207:24 | 461:119 (1.9e-48) | POWERED, V1 3/3 · X 0/3 | **(i)** | 121 | 정의 안 됨 (범위 밖: 0.9535) | 0.624 [0.579, 0.670] |
| ALDv-pilot | +9 / +12 / +15 | 90:48 · 132:43 · 179:30 | 401:121 (4.8e-36) | POWERED, V1 3/3 · X 0/3 | **(i)** | 129 | 정의 안 됨 (범위 밖: 0.9566) | 0.576 [0.524, 0.629] |
| SBL-loop | +9 / +12 / +15 | 215:35 · 222:28 · 229:25 | 666:88 (1.1e-110) | POWERED, V1 3/3 · X 0/3 | **(i)** | 103 | 정의 안 됨 (범위 밖: 0.9465) | 0.737 [0.705, 0.771] |
| SBL-pilot | +9 / +12 / +15 | 244:30 · 239:31 · 228:31 | 711:92 (2.6e-119) | POWERED, V1 3/3 · X 0/3 | **(i)** | 136 | 정의 안 됨 (범위 밖: 0.9594) | 0.750 [0.719, 0.783] |
| OMP-pilot | +9 / +12 / +15 | 279:24 · 286:22 · 336:20 | 901:66 (3.6e-188) | POWERED, V1 3/3 · X 0/3 | **(i)** | 215 | 정의 안 됨 (범위 밖: 0.9902) | 0.802 [0.777, 0.828] |

- **요약 줄(원문)**: `SUMMARY-B (baselines without b*, 15): (i) 13, (ii) 0, not decided 2; b* -> V1 (i)` · `SUMMARY registered baselines 16 (b* + 𝔅 15): (i) 14, (ii) 0, not decided 2`.
- **"전부" 문장: 쓰지 않는다**(§2 조건 불충족). 그대로 적는 것: **(i) 13 / 15 (b\* 포함 14 / 16), (ii) 0; (i) 가 아닌 arm 둘 = `V1-pilot` (iii) "판정하지 못함 (유의 방향 없음)"** — 26:23 (p 0.78) · 18:15 (0.73) · 7:7 (1), pooled 51:45 (p 0.61), POWERED, 유의한 점 0/3 — **과 `R4-llr` (iv) "판정하지 못함 (검정력 미달)"** — 앵커 R4-llr 의 BLER@16 이 [0.005, 0.9] 안인 SNR 이 +12 · +15 dB 둘뿐(+9 dB 0.907)이라 판정점이 2 개 → `POWERED=False`; 그 두 점에서는 846:3 · 815:3 (pooled 1661:6). SNR 격자는 늘리지 않는다(§1). 동치 문구는 쓰지 않는다.
- **"멀어진다" 문장: 쓰지 않는다** — `'등록된 baseline 전부와 멀어진다' condition (k = 16, (ii) = 0, R_X* CI lower > 0): NOT met` (`X* (fewest -3 dB failures, ties by name) = V1-pilot (F=2379); R_X* -3 dB = undefined (out of range)`; (i) 도 16 개 중 14 개).
- **드리프트 검사**: `b* → V1` 을 `pair_baselines` 가 다시 낸 값(145:38 · 126:22 · 132:33, pooled 403:93, (i), 판정점 합 0.601 [0.553, 0.650]) = 6.1 → 드리프트 없음. −3 dB 의 R 은 `pair_baselines` 규칙으로 "정의 안 됨 (범위 밖: 0.9391)" 이다 — 6.1 에 적은 0.268 [0.221, 0.315] 는 `recovery_ci` 가 가드 없이 찍은 파일 값이며 1차 판독에 쓰지 않았다.
- SNR@0.1 격차는 16 쌍 모두 n/a (두 arm 모두 > 15 dB). **R_X(−3 dB) 는 16 개 전부에서 정의되지 않는다**(모든 X 의 −3 dB BLER 이 0.9 를 넘는다 — 가장 낮은 `V1-pilot` 이 0.9293; 포화 가드).
- 라벨에 붙는 것(§2): §1 "SRT 고유 사항" (1) 유한 풀(테스트 51,852 쌍 복원 추출) · (2) 누수 0.634 · (3) outage·랭크(테스트 풀의 0.796 이 비중 ≥ 0.95; genie BLER −3 dB 0.817 · +15 dB 0.499) · (7) baseline 조정용 개발 채널이 테스트 풀에서 나옴(baseline 에 유리한 방향). 범위: 이 풀·이 split·이 크기 한정.

### 6.4 원고 범례 11 곡선 — BLER@16 실패 수 / 2560 (`pairB_SPSRT.txt` 의 표; 전 SNR n = 2560)

| 곡선 | −3 | 0 | +3 | +6 | +9 | +12 | +15 dB |
|---|---|---|---|---|---|---|---|
| Proposed (V1) | 2320 | 2056 | 1781 | 1661 | 1504 | 1391 | 1331 |
| Annealed Langevin (plug-in) = ALD-pilot | 2441 | 2188 | 1907 | 1738 | 1558 | 1496 | 1514 |
| GMM prior = b\* | 2404 | 2169 | 1941 | 1774 | 1611 | 1495 | 1430 |
| Gaussian prior = R2-ours-G | 2461 | 2291 | 2093 | 1924 | 1822 | 1692 | 1607 |
| Turbo LMMSE = R1-turbo | 2507 | 2396 | 2205 | 2047 | 1906 | 1754 | 1676 |
| BiG-AMP = R3-bigamp | 2502 | 2399 | 2284 | 2191 | 2187 | 2214 | 2232 |
| Pilot-only LMMSE = R0-pilot@1 | 2547 | 2500 | 2389 | 2289 | 2202 | 2092 | 2029 |
| SBL (in loop) | 2423 | 2212 | 2001 | 1846 | 1684 | 1585 | 1535 |
| SBL (pilot-only) | 2456 | 2253 | 2028 | 1854 | 1718 | 1599 | 1528 |
| OMP (pilot-only) | 2535 | 2211 | 1974 | 1878 | 1759 | 1655 | 1647 |
| Perfect CSI = genie | 2091 | 1871 | 1626 | 1546 | 1416 | 1327 | 1277 |

- 11 곡선에 없는 등록 arm (같은 순서): V1-pilot 2379 / 2118 / 1825 / 1687 / 1507 / 1394 / 1331; bstar-pilot 2430 / 2205 / 1977 / 1784 / 1616 / 1502 / 1443; ALDv-pilot 2449 / 2207 / 1916 / 1741 / 1546 / 1480 / 1480; M-ours-bstar-scalar 2408 / 2171 / 1940 / 1774 / 1617 / 1497 / 1439; M-ours-gmm32 2438 / 2214 / 2019 / 1828 / 1673 / 1551 / 1495; R4-scvamp 2526 / 2440 / 2313 / 2206 / 2109 / 2045 / 1977; R4-llr 2544 / 2496 / 2458 / 2381 / 2322 / 2234 / 2143.
- 그림: `conference/figures/F21srt_col.{pdf,png}` (`paper_f21dmc.py SRT`, 기록 `records/paper_f21srt.txt`): 실패 수 = 위 표(assert), 세 raw 의 Perfect CSI 오류 배열 동일(assert), y 범위는 사다리 규칙으로 (0.3, 1.05) (눈금 0.3 / 0.5 / 0.7 / 1.0), 그려진 baseline 9 개의 라벨 모두 (i), 제안 곡선 이하인 그려진 **baseline** 곡선 없음(Perfect CSI 제외; 점추정). (i) 가 아닌 두 arm(`V1-pilot` · `R4-llr`)은 범례 11 곡선에 없다.
- **NMSE CDF** (보고 전용 — 라벨·검정·CI 없음): `conference/figures/F33cdf_SRT_wide.{pdf,png}` (`paper_f33cdf.py SRT`, 기록 `records/paper_f33cdf_SRT.txt`): 패널 −3 · +9 · +12 · +15 dB, 곡선 10 개, 2560 시행 전부(비유한·비양수 0 건). 중앙값 10 log10 NMSE [dB] (−3 / +9 / +12 / +15): Proposed −14.76 / −26.88 / −29.90 / −32.53; GMM prior −12.76 / −23.23 / −25.90 / −28.86; Annealed Langevin (plug-in) −11.14 / −23.46 / −25.71 / −27.66; Gaussian prior −5.70 / −15.42 / −18.51 / −21.72 (나머지와 90 백분위는 기록 파일). 그리기 범위 (−35, 5) dB 는 결과 전에 스크립트에 고정된 값이라 +9 dB 이상 패널에서 일부 곡선의 왼쪽 꼬리가 −35 dB 에서 잘려 그려진다(기록의 수치는 잘리지 않은 값).

### 6.5 baseline 보고 전용

- `pair_PILSRT.txt` (PILOT16e4 형식): P1 `V1-pilot → V1` (iii) (위와 같은 계수); P2 `bstar-pilot → V1-pilot` 153:44 · 130:22 · 141:29, pooled 424:95 → (i); `bstar-pilot → b*` 30:25 · 20:13 · 24:11, pooled 74:49 → (iii) (1/3 · 0/3); `V1-pilot → b*` 40:144 · 24:125 · 32:131, pooled 96:400 → (ii) (V1-pilot 이 3/3 에서 적게 실패).
- `pair_ALDSRT.txt` (ALD16e4 형식): A1 `ALDv-pilot → V1` 90:48 · 132:43 · 179:30 → (i); A2 `ALD-pilot → V1` 103:49 · 151:46 · 207:24 → (i); A3 `ALDv-pilot → V1-pilot` 85:46 · 122:36 · 177:28, pooled 384:110 → (i); `ALDv-pilot → b*` 60:125 · 77:92 · 119:69, pooled 256:286 → (iii) (1/3 · 1/3); `bstar-pilot → ALDv-pilot` 134:64 · 103:81 · 74:111, pooled 311:256 → (iii) (1/3 · 1/3); `ALD-pilot → ALDv-pilot` 26:14 · 33:17 · 45:11, pooled 104:42 → (i) (2/3). 시험 ALD NMSE(추정 파일 평균) −9.30 / −12.46 / −14.94 / −18.26 / −21.05 / −23.55 / −25.83 dB.
- 조정 표: §5 (SBL ρ 16 · OMP ρ 16 — 둘 다 격자 끝 + 캐비엇; ALD c 0.01 · β 0.005).
- raised trials: PIL 0 / 0, ALD 0, SP 0 / 0 / 0.

### 6.6 §3 예측 채점 (적중 / 빗나감; 범위 밖은 채점 불가)

1. 표 B (i) → 결과 (i) → **적중**.
2. (a) genie BLER(−3 dB) ≥ 0.70 → **적중** (0.817); (b) genie BLER(+15 dB) ≥ 0.25 → **적중** (0.499); (c) 판정점 +9 / +12 / +15 → **적중**; (d) 표 A 의 arm 모두 SNR@0.1 "> 15" → **적중** (표 A 의 15 줄 — 14 arm, R0-pilot 은 @1 · @16 두 읽기 — 모두 "> 15").
3. 1차 ΔR 의 포화 가드가 "−3 dB 에서 b\* 의 BLER@16 > 0.9" 로 발동 → **적중** (0.939).
4. 회수율 2차(판정점 합) R ∈ [0.10, 0.40] → **빗나감** (0.601 [0.553, 0.650] — 구간 위).
5. `R2-ours-G → b*` b\* 가 ≥ 2/3 점에서 적게 실패 → **적중** (3/3).
6. GB′ median ≤ 0.90 → **적중** (0.5425).
7. 학습(발산 없음 · patience · epoch ∈ [300, 1200]) → **빗나감** (§5: 시행 1 발산).
8. b\* = kron 4096 → **적중** (§5).
9. V0 가드 발동 ✓ (발동률 0.965 … 0.790) 이고 −3 · 0 dB BLER ≥ 0.9 ✓ (0.989 · 0.975); best 대 last V1 판정하지 못함 ✓ (pooled 34:38, p 0.724) → **적중**.
10. 대조군 `b* → b*-scalar` (iii) → **적중** (POWERED, 0/3 · 0/3, pooled 99:116).
11. baseline — 네 문장: "(ii) 0 이고 (i) ≥ 13" → **적중** ((ii) 0, (i) 13 / 15); `V1-pilot` 은 (i) 가 아니다 → **적중** ((iii)); `pair_ALDSRT.txt` A3 = (i) → **적중**; −3 · 0 dB 모두 `OMP-pilot` < `R0-pilot@1` (2535 < 2547, 2211 < 2500) 이고 `SBL-pilot` < `R0-pilot@1` (2456 < 2547, 2253 < 2500) → **적중**.
12. 랭크 층화(+15 dB 는 판정점 → 채점 가능): Perfect CSI BLER 이 비중 ≥ 0.95 층에서 ≥ 0.25 → **적중** (0.620, 1274 / 2055); 비중 < 0.80 인 두 층을 합쳐 ≤ 0.02 → **적중** ((0 + 0) / (99 + 5) = 0).
13. 누수 층화·NMSE CDF: 예측 없음(수치는 6.2 · 6.4).
14. 빗나갈 경로: (d) 발산 → §3d 발동(§5; 시행 2 로 평가). (a)(b)(c)(e)(f) 미발동((i); R > 0; 주 라벨 POWERED; b\* 는 kron; baseline 에 (ii) 없음). baseline `R4-llr` 의 (iv) 는 격자 확장 없이 그대로 적었다.

### 6.7 등록 대비 공개 사항 (수치·판정 불변)

- 동결(2e50f269) 뒤·BLER 전의 `conf/code`·`Demo` 변경은 `run_srt_eval.sh` 한 파일(+3 −2 줄: §5 의 인자를 채움)뿐이다(`git diff 2e50f269 28f38d55 -- conf/code Demo`). `conf/code` 는 실행 커밋 28f38d55 와 6cbf9a5e 에서 clean.
- 주 실행과 baseline 실행은 각각 한 번 돌았고 재실행·중단·재개가 없다(`logs/run_D2_SRTB16e4{,last}.log` 각 448 done, exists 줄 없음; `run_srt_base.log` 의 시작 줄 하나).
- 판정점이 SNR 격자의 위쪽 끝 3 점이고 모든 arm 의 SNR@0.1 이 격자 밖이다 — §1 "결과 뒤 격자를 늘리지 않는다" 를 그대로 지켰다.
- 학습 시행 1 발산 → 시행 2 (클리핑 1.0), 고정하지 않은 시행 2 의 속도, b\*·SPARSE ρ 의 격자 끝, GPU 0·1 재점유는 §5 에 적은 그대로다.
- 보고 전용 층화 둘(누수·랭크)은 `PRIOR_EVAL_DONE` (06:11 CDT) 뒤·baseline 시작(06:13 CDT) 전인 06:12 CDT 에 돌렸다(출력 머리말 git 28f38d55).
- **작성 순서**: 6.1·6.2 초안은 baseline runner 가 도는 동안(baseline 결과를 보기 전) 스크래치 파일에 썼고, 이 문서에는 `SRT_BASE_DONE` 뒤에 한 번에 옮겼다(runner 가 도는 동안 이 문서·`conf/code` 를 건드리지 않았다). 6.1·6.2 의 수치는 모두 주 실행의 파일에서 나온다.
- baseline 시작 시 빈 GPU 는 2 와 4 였고(`nvidia-smi`, 06:13 CDT — 로그 외 사실) 스크립트가 규칙대로 번호가 가장 작은 GPU 2 를 잡았다. GPU 0·1·3·5 는 컨테이너 밖 프로세스가 쓰고 있었다.
- 그림 두 종은 `SRT_BASE_DONE` 뒤 등록된 명령 그대로 한 번씩 만들었다(스크립트의 마지막 커밋: `paper_f21dmc.py` f379258f · `paper_f33cdf.py` 331dba15, 작업 트리 변경 없음).
