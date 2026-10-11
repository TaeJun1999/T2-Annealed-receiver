# NEXT_EXPERIMENTS_ROOM16e4 — 고정 기지국 한 곳·방(실내) ray-traced 풀 두 개의 수신기 BLER: **Sionna RT `box` (prior SRB) 와 DeepMIMO `i1_2p4` (prior DMI), 각각 주 실행 + 등록된 baseline 전부** (셀 C2, 동일예산 N′ = 1.6e5, 태그 SRBB16e4 / PILSRB / ALDSRB / SPSRB · DMIB16e4 / PILDMI / ALDDMI / SPDMI) — 사전 등록 초안 v1

- 작성: 2026-10-11 11:10 CDT (= 10-12 01:10 KST), Claude Code (Opus 5.5), 초안 v1. 적대적 검토(Fable) 뒤 v2 로 동결한다; 동결 시각 = 동결 커밋 시각(`DECISIONS.md` 같은 줄). **결과 관측 전**: SRB·DMI 의 어떤 체크포인트·적합도 BLER 로 평가된 적이 없고, prior 에 의존하는 arm(V1·GMM·baseline)은 이 두 풀에서 한 번도 돌지 않았다(아래 "선택 경위" 의 Perfect CSI 선별은 prior 를 쓰지 않는 arm 하나뿐). 커밋 뒤에는 §1~§3 을 바꾸지 않는다; 바꿔야 하면 사용자 승인 + `DECISIONS.md`.
- 사용자 지시(2026-10-11 CDT, 이 세션; 원문): "Deepmimo랑 Sionna기 Rank 1이 안되도록 할 수 있어?" · "꼭 28GHz 로 해야해? 이정도면 당연히 los도 많도 rank 1도 많겠는데" · "그리고 기지국은 고정하고 위치를 비꿔서 채널을 수집하는게 좋을 거 같은데" · "Deepmimo, Sionna 모두 rank1이 적게 나오는 채널로 찾아봐" · "뭐가 됬던 rank 1 가장 낮은가로 해보자" · "기지국하나에 연속적으로 위치를 바꿔서 보는거 맞지?" · "모든 선택 기준은 bler가 낮게 나올거 같은 방향으로 해야해". 앞선 지시가 그대로 적용된다: 채널은 **라이브러리 자체 생성기**로; "기존 실험과 같은 사이즈로 해야해"; "우리 conference에 넣는 11개 그래프 모두 찍어야 해".
- 배경: 도시 ray-traced 풀 두 개(DeepMIMO 6 개 도시 `NEXT_EXPERIMENTS_DMC16e4.md`, Sionna RT 3 개 장면 `NEXT_EXPERIMENTS_SRT16e4.md`)는 둘 다 라벨 (i) 였지만 **모든 arm 의 BLER 이 높았다**(Perfect CSI 의 +15 dB BLER 0.239 · 0.499): 테스트 채널의 0.66 · 0.80 이 사실상 rank-1 이고 실패가 그 층에 몰린다(SRT16e4 §6.2 · §6.9). 사용자는 BLER 이 낮게 나오는 ray-traced 풀을 원한다.
- **한 문서에 두 prior 의 주 실행과 baseline 확장을 함께 등록한다.** 틀(새 판정 규칙 없음) = `NEXT_EXPERIMENTS_SRT16e4.md` v2 §1~§2 (= DMC16e4 · DMCBASE16e4 의 틀). 아래 §1 에 **다른 곳과 고정 값**을 적고, 긴 규칙 문장(라벨·수용 검사 (a)~(e)·회수율 CI·ΔR 세 갈래·포화 가드·X\*·R_X·"전부"/"멀어진다" 문장·§3d 사다리·격자 반복 규칙)은 SRT16e4 v2 의 문장을 prior SRB / DMI · 해당 태그로 읽는다. 두 prior 는 서로 독립이다: 라벨·수용·예측 채점을 prior 마다 따로 하고, 한쪽이 멈춰도 다른 쪽은 등록대로 간다.
- 목적: 고정 기지국 한 곳의 방 안 채널(다중경로가 풍부해 rank-1 이 드문 ray-traced 채널)에서 같은 파이프라인·같은 크기·같은 규칙으로 b\* 대 V1 과 등록된 baseline 전부를 잰다. 결과가 어느 쪽이든 보고한다. 헤드라인(C2 1.6e5 B16e4k)·D2·38.901·DeepMIMO 도시·Sionna RT 도시 기록은 어느 결과에서도 바뀌지 않는다.

**선택 경위(공개 — 이 풀들은 "BLER 수준이 낮게 나오도록" 채널 통계와 Perfect CSI 선별로 골랐다; 기록 `rank_probe_2026-10-11/`)**

1. **무엇을 보고 골랐나.** (a) 채널 통계: rank-1 비율(최대 특이값 에너지 비중 ≥ 0.95)·유효 랭크·LoS 비율. (b) **Perfect CSI 수신기 하나(R5-genie: 같은 EP 검출기 + BCJR, 참 H)의 BLER** (`genie_screen.py`): 후보 채널 묶음에서 뽑은 채널(풀 전체 또는 탐색 표본; **시행 스트림이 아닌 별도 rng** `[20261011, 후보 번호, snr + 100]`)로 2048–4096 블록. R5-genie 는 채널 prior·파일럿을 쓰지 않는다 — **V1·b\*·그 밖의 prior 의존 arm 은 어느 후보에서도 돌리지 않았고, 두 arm 의 비교는 본 적이 없다.** 이 선별 때문에 아래 §3 에서 Perfect CSI 의 BLER 수준은 예측이 아니라 "관측됨(채점 제외)" 이다.
2. **생성 설정으로는 안 됐다.** 고정 기지국 1 곳(Munich)에서 28 → 3.5 GHz 는 rank-1 을 줄이지 않았고(0.74 → 0.89), 굴절·회절을 켜도 0.91–0.94 였다(`srt_fixed_probe.py` 의 콘솔 출력 — 파일로 남기지 않은 로그 외 사실). DeepMIMO 의 3.5 GHz 도시판은 28 GHz 판과 통계가 같았다(Miami 0.61 / 0.69 / 0.62). 도시 장면 셋의 기지국 위치 2,896 곳(쌍 400 개 이상인 1,929 곳 가운데)을 훑어도 기지국별 최저 0.26 (`rank_*.txt`; 높이 10 m, Munich 은 25 m · 5 m 도), DeepMIMO 실외 시나리오는 기지국별 최저 0.54 (`dm_scan_summary.txt`; 28 GHz 도시 14 곳 중 6 곳은 다운로드 한도(HTTP 429)로 받지 못해 재지 못했다).
3. **방(실내) 시나리오가 가장 낮았다.** Sionna RT 내장 `box` (10 × 10 × 5 m 빈 방, **벽 재질은 기본 제공 그대로 `box-mat`: 비유전율 1, 전도도 1e7 S/m = 금속**) 와 DeepMIMO 실내 `i1_2p4` (2.4 GHz, Wireless InSite, 반사 2 회, 기지국 위치 64 곳 × 단말 격자 2 개). 재질을 바꾼 `box` 는 유리 0.07 · 콘크리트 0.11 · 석고보드 0.51 · 목재 0.88 (rank-1 비율, 깊이 5; `box_probe.txt` 뒤의 `srt_box_material.py` 콘솔 출력 — 로그 외 사실) — **사용자에게 금속 벽임을 알렸고(10-11 CDT), 사용자 지시("bler가 낮게 나올거 같은 방향")에 따라 기본 제공 그대로 쓴다.**
4. **BLER 을 가장 낮추는 설정을 그대로 쓰지 않은 이유(작성자 판단, 공개).** SNR 격자는 다른 실험과 같은 −3 … 15 dB 로 고정이고(§1), 판정점은 앵커 b\* 의 BLER 이 [0.005, 0.9] 안인 SNR 3 개가 필요하다. `box` 깊이 2 · 5 는 Perfect CSI BLER 이 0 dB 에서 0.002 · 0.000 이라(`genie_screen_final.txt`) 폭포가 격자 아래쪽 끝에 붙어 판정점이 3 개에 못 미칠 위험이 크다. 그래서 **"Perfect CSI BLER(−3 dB) 가 가장 낮되, Perfect CSI BLER(+2 dB) ≥ 0.005 인 것"** 을 기준으로 삼았다(Perfect CSI 보다 1 dB 나쁜 arm 도 +3 dB 에서 판정 범위에 들도록; D2 기준 채널의 같은 선별값은 0.007). 이 기준은 결과를 보기 전에 작성자가 정한 휴리스틱이며 검정이 아니다.
   - Sionna RT: `box` 기본 제공 그대로, **깊이 1** (LoS + 여섯 벽의 1 차 반사) — 풀 자체의 선별값 −6 / −3 / 0 / +2 / +3 / +6 dB = 0.452 / 0.102 / 0.017 / 0.007 / 0.003 / 0.000. 탈락: 깊이 2 (+2 dB 0.000), 깊이 5 (0.000); 기준을 넘지만 더 높은 것: 유리 깊이 5 (−3 dB 0.133), 콘크리트 깊이 5 (0.191).
   - DeepMIMO: `i1_2p4` 데이터셋 120 (기지국 (−20.89, 12.60, 5.00) m × 7 m × 1 m 격자) — 선별값 0.546 / 0.127 / 0.019 / **0.003** / 0.002 / 0.000. **+2 dB 값이 기준(0.005)에 못 미친다**: 이 풀은 기준을 세우기 전에 "rank-1 비율 최저(0.023; 동률 셋 중 유효 랭크가 높은 것)" 로 이미 만들었고, −3 dB BLER 이 후보 가운데 최저권(`genie_screen_deepmimo.txt`: 같은 격자의 기지국 10 곳이 0.120–0.157, 이 데이터셋 0.122)이라 **사용자 지시(낮은 BLER)를 우선해 그대로 둔다 — 판정점이 3 개에 못 미쳐 (iv) 가 될 위험을 안고 간다**(§3 예측 2). 더 안전한 후보(데이터셋 65: 0.197 / +2 dB 0.014, `i2_28b`: 0.294 / 0.076)는 BLER 이 더 높다.
5. **기지국 한 곳(사용자 지시).** Sionna: 장면 경계 상자에서 규칙으로 정한 한 점(x 20 % · y 30 % · z 80 % = (−3, −2, 4) m; 탐색 스크립트의 규칙 그대로, 다른 위치는 재지 않았다). DeepMIMO: 데이터셋 하나(기지국 1 곳 × 격자 1 개)는 위치가 70,801 개뿐이라 학습 160,000 에 못 미친다 → **같은 위치에서 단말 yaw 를 5 번 독립 추첨**해 354,005 쌍(도시 풀 342,597 과 같은 규모). 처음에는 기지국 5 곳을 쓰려 했으나 사용자 지시("기지국하나에…")로 바꿨다.
6. 어느 선택도 V1·b\* 의 BLER 을 보고 하지 않았다. **그러나 이 등록은 "도시 풀 두 개의 결과를 본 뒤, BLER 수준이 낮은 채널을 골라 다시 재는" 것이다** — 모집단은 "이 방·이 기지국 한 곳" 이며 다른 장소·다른 재질로의 일반화는 주장하지 않는다. 도시 풀 두 개의 기록은 그대로 남고, 무엇을 원고에 쓸지는 사용자가 정한다.

---

## 0. 출발점 (판정에 쓰지 않는다)

**풀** (BLER 없음; 빌드 시점의 코드 = git 36e0a264 + 미커밋 작업 트리 = 커밋 44d3ab5e 의 빌더, 빌드 뒤 그 파일들을 바꾸지 않았다):

| | SRB (Sionna RT 2.1 `box`) | DMI (DeepMIMO v4.0.5 `i1_2p4`) |
|---|---|---|
| 빌더 · 로그 | `code/srb_build.py build 8` (GPU 0, 10-11 10:31 → 10:44 CDT; `logs/srb_build.log`) | `code/dmi_build.py 8` (CPU, 10-11 10:20 → 10:21 CDT; `logs/dmi_build.log`) |
| 채널 | 28 GHz, `PathSolver` max_depth 1 (LoS + 정반사; 난반사·굴절·회절 off), samples_per_src 1e8, `PlanarArray` 1×8 / 1×4 등방성 V, `Paths.cfr` (반송파), 링크당 경로 7 개 | 2.4 GHz, `dm.load(max_paths=25)` + `compute_channels` (반송파, 등방성 반파장 ULA 8×1 / 4×1, BS yaw = 단말 격자 중심 방향 +88.2°), 링크당 평균 경로 11.06 개 |
| 기지국 · 단말 | BS 1 곳 (−3, −2, 4) m; 단말 345,600 위치 = 바닥 평면 [−4.5, 4.5]² 균등, 높이 1.5 m, yaw ~ U[−π, π) | BS 1 곳 (−20.89, 12.60, 5.00) m; 단말 격자 701 × 101 = 70,801 위치(1 cm 간격, 높이 1 m) × yaw 5 회 ~ U[−180°, 180°) |
| 쌍 = 학습 풀 + 검증 풀 + 테스트 풀 | 345,600 = 273,247 + 20,000 + 52,353 (테스트 0.1515) | 354,005 = 273,305 + 20,000 + 60,700 (테스트 0.1715) |
| block split | 1 m 타일 100 개 중 16 개가 테스트 | 위치 기준 0.5 m 타일 45 개 중 8 개가 테스트(한 위치의 yaw 5 개는 같은 쪽) |
| sha256[:16] `H.npy` / `split.npy` (`dmimo.POOL_SHA`) | ae1c023605d002b4 / 24c202836d56b34e | dec5e7a1ea1e4605 / f0f716718f1c15d1 |
| 보정 (학습 스트림 7, n = 160000) | P_RAW 1.0005289046575756, TRAIN_SHA 2544c37a719436e2 | P_RAW 0.0019453481377247777, TRAIN_SHA 3380177f4c38cf57 (DeepMIMO 의 전력 단위 상수; 도시 풀 DMC 도 0.00195) |

- SRB 의 배열 packing 은 `srt_build.py` 와 같은 방식(수신기를 배열로 넘김): `srb_build.py selfcheck` — 위치·방향 차 0, 소자 오프셋 차 9.3e-10 m, 유효 경로 마스크 동일, 채널 상대 오차 5.9e-07 (결정적 solver, 수신기 64 개; 세션 콘솔 출력 — 로그 외 사실, 재실행 명령은 같은 것). 처음에 깊이 5 로 시작한 빌드는 출력 파일을 쓰기 전에 멈췄다(`logs/srb_build.log`).

**testbed 검증** (`results/testbed_{SRB,DMI}.txt`, `code/testbed_dm.py`, BLER 없음):

| 검사 | SRB | DMI | (문맥) SRT / DMC |
|---|---|---|---|
| TDMa 정규화(검증 스트림 8, n = 20000) | 0.99984 (s.e. 0.00311) **PASS**; 블록 전력 CV 0.440 | 1.00422 (s.e. 0.00189) **PASS**; CV 0.266 | CV 0.354 / 0.396 |
| TDMc 풀 정체 | 345,600 쌍, 장면 box, BS 1 곳, LoS 1.000, 평균 경로 7.00 **PASS** | 354,005 = 70,801 × 5, 데이터셋 120, LoS 1.000, 평균 경로 11.06 **PASS** | LoS 0.848 / 0.281 |
| TDMd 파일럿 단계 K = 1 Gaussian NMSE @ −3 dB (보고) | 0.3134 | 0.2847 | 0.3191 / 0.3161 |
| TDMe T2b 파일럿 결정 / erank(C_ens) | erank(Rt) 3.991/4 ≥ 3.6 → **DFT 파일럿** / 25.95/32 | 3.839/4 → **DFT 파일럿** / 20.47/32 | 3.392 → eigen / 3.422 → eigen |
| TDMf block split | 서로소·전체, 양쪽에 걸친 타일 없음 **PASS** | **PASS** | PASS |
| TDMg split 이동(보고): outage P(MI < 4 bit) @ −3 dB 검증 / 테스트; K = 1 NMSE 검증 / 테스트 | 0.0231 / 0.0304; 0.3134 / 0.3371 | 0.0019 / 0.0018; 0.2847 / 0.2918 | 0.1399 / 0.1349 (SRT) |
| TDMh 누수(보고): 테스트 2000 표본의 최근접 학습 채널, 정규화 제곱거리 중앙값 · < 0.1 비율 | 0.3509 · **0.004** | 0.1789 · **0.058** | 0.0500 · 0.634 / 0.1261 · 0.433 |
| 종합 | **ALL PASS** | **ALL PASS** | |

- 채널 랭크(풀에서 직접; `genie_screen_pools.txt` 의 표본): rank-1 비율 SRB 0.026 / DMI 0.023, 평균 유효 랭크 1.84 / 1.64 (SRT 0.808 · 1.12, DMC 0.677 · 1.23, D2 S2 0.013 · 2.20).
- **Perfect CSI 선별값**(R5-genie BLER@16, n = 4096, 별도 rng, 풀 전체에서 추출; `genie_screen_final.txt`): SRB −6 / −3 / 0 / +2 / +3 / +6 dB = 0.452 / 0.102 / 0.017 / 0.007 / 0.003 / 0.000; DMI 0.546 / 0.127 / 0.019 / 0.003 / 0.002 / 0.000; D2 S2 기준 0.199 / 0.042 / 0.011 / 0.007 / 0.008 / 0.003. (선별 도구의 검증 `genie_screen_validation.txt`: 같은 도구로 SRT 풀 −3 / +15 dB 0.813 / 0.496, DMC 풀 0.722 / 0.244 — 등록 실행(테스트 풀)의 Perfect CSI 0.817 / 0.499, 0.686 / 0.239 와 같은 수준.)

**σ 격자** (`runner.py sigma --testbed D2 --prior <P> --cell C1 C2 --tag <P>`; `sigma_grid_D2_{SRB,DMI}.{txt,npz}`): SRB 20 점 ν_q [2.142e-03, 1.461e+00] → σ_t [3.273e-02, 8.548e-01]; DMI ν_q [2.162e-03, 1.437e+00] → σ_t [3.288e-02, 8.477e-01]. **공개: 이 측정으로 두 prior 의 테스트 시행 0..63 (C1·C2, 7 SNR) 이 Gaussian 수신기로 한 번 실행됐다**(BLER 은 읽지도 쓰지도 않음; 모든 prior 의 관례).

**일괄 kron EM 검사** (`results/nr8b_batched_check_{SRB,DMI}_n160000.txt`, GPU 1): SRB (a) N′ = 160000 K = 512 PASS (max\|Δll\| 4.8e-11, 재시드 600/600), (b) N = 10000 PASS (재시드 2725/2725); DMI (a) PASS (1.3e-10, 재시드 113/113), (b) PASS (1418/1418) → kron 계열은 일괄 경로, full 계열은 정확 경로.

**기존 경로 불변**: `selftest_sv.py` 742 배열 · `selftest_mix3.py` 968 배열 IDENTICAL; `dmimo.py selfcheck 8 DMC` · `SRT` train sha 불변(e6ddafc27367f975 · d15b033bc915cf88); `paper_f21dmc.py` (DMC · SRT) · `paper_f33cdf.py SRT` 의 그림·기록 바이트 동일.

---

## 1. 고정되는 것

| 항목 | 값 |
|---|---|
| **셀·예산·시행 (기존 실험과 같은 크기 — 사용자 지시)** | SRT16e4 §1 첫 행 그대로: C2 = 8×4, T 16, Tp 4, K = 42, rate-1/2 conv (133,171)_8, QPSK, 16 반복, **7 SNR (−3 … 15 dB; 결과 전에도 뒤에도 격자를 바꾸지 않는다)**, n = 2560, 테스트 시행 0..2559 (chunk 40), 수신기 CPU complex128, 시행 시드 `common.trial_rng` 에 **PID SRB = 13 · DMI = 14** (다른 모든 prior 와 다른 스트림 → 다른 데이터셋과의 비교는 짝 없음). N′ = 160000 = `arms.training_set("D2", <P>, 8, 4, 160000)` (스트림 7) 을 GMM 적합과 score 학습(자체 9:1)이 함께 쓴다; GMM 검증 5000 = 스트림 8 |
| **지위** | **UNGATED** → "prior·기전 축 측정" 이며 arm 판정이 아니다. SRB·DMI 는 어느 결과에서도 헤드라인이 되지 않는다 |
| **생성 모델** | §0 의 표와 빌더 머리말(`code/srb_build.py`, `code/dmi_build.py` @44d3ab5e = 원문; 동결 — 바꾸려면 새 결정 + 새 prior id). 풀 파일 `~/data/sionna_rt/srb_Nr8/` · `~/data/deepmimo/dmi_Nr8/` 의 `{H.npy, split.npy}` 는 git 밖, sha 로 고정 |
| **block split 과 스트림** (`dmimo.py`; 도시 풀과 같은 코드) | 타일을 섞어 쌍의 15 % 이상을 담을 때까지 = 테스트 타일; 나머지의 동결된 무작위 20,000 = 검증 풀, 나머지 = 학습 풀. 타일: SRB floor(xy / 1 m), DMI floor(위치 xy / 0.5 m) — 방이 작아 도시 풀의 20 m 타일은 쓸 수 없다. 스트림 → 풀: 학습 스트림 7 → 학습 풀에서 서로 다른 n 쌍; 스트림 8 → 검증 풀; 스트림 10·모든 시행 스트림·`sparse_tune` 개발 스트림 → 테스트 풀 복원 추출 |
| **고유 사항 (공개; 고치지 않고 그대로 잰다)** | (1) **유한 풀·한 장소**: 테스트 시행은 테스트 풀(SRB 52,353 · DMI 60,700 쌍)에서 복원 추출; 채널 모집단은 "이 방·이 기지국 한 곳의 테스트 타일". (2) **가까운 이웃**: 타일이 1 m · 0.5 m 라 테스트 위치가 학습 위치와 가깝다(SRB 는 28 GHz 에서 약 93 λ, DMI 는 2.4 GHz 에서 4 λ 타일) — 채널 거리로 본 누수는 §0 TDMh (0.004 · 0.058); DMI 는 같은 위치를 yaw 만 바꿔 5 번 쓴다(한 위치의 yaw 5 개는 split 의 같은 쪽). (3) **Sionna `box` 는 금속 벽**(기본 제공 재질)이고 반사는 1 차까지만 넣었다 — 현실의 방이라기보다 "LoS + 무손실 1 차 반사 6 개" 인 기하 채널이다. (4) **선택 편향**: 이 두 풀은 BLER 수준이 낮도록 고른 것이다(선택 경위). (5) 모든 링크가 LoS 다(1.000). (6) V1·b\* 의 학습·모델 선택은 학습 타일 안에서만 한다; baseline 조정용 개발 채널은 테스트 풀에서 나온다(DMCBASE16e4 "DMC 고유 1" 과 같음 — baseline 에 유리한 방향). (7) σ 격자 측정은 테스트 시행 0..63 을 Gaussian 수신기로 한 번 실행한다(§0). (8) SRB 의 `PathSolver` 는 기본(비결정적 후보 생성)으로 돌렸다 — 재생성이 같은 sha 를 낸다는 보장이 없다 |
| **파일럿** | D2 의 T2b 규칙을 학습 집합의 Rt 에 적용(`dmimo.RT`) → 두 prior 모두 **DFT 파일럿**(§0 TDMe; 도시 풀은 eigen 정렬이었다) |
| **GMM 격자와 b\*** | SRT16e4 §1 과 같다: full K ∈ {16 … 512} (정확 경로) + kron K ∈ {16 … 512} + kron 1024·2048·4096 재시작 후보 3 개씩(일괄 경로), 선택 = 검증 우도 최대(스트림 8). 반복 규칙: b\* 가 kron 2048 이면 4096 병합, **4096 에서 멈춘다** + 캐비엇; b\* 가 full 512 이면 full 1024 한 번 + 캐비엇. **BLER 은 선택에 쓰지 않는다.** 큐 `code/run_room_gpu.sh` (두 prior 한 큐: 학습 2 + 적합 42 작업, GPU 0·1·2). 병합·선택·끝 규칙·fits 링크는 `code/run_{srb,dmi}_post_select.sh <동결 커밋>` (동결 커밋이 v2 인지와 그 prior 의 적합 21 작업의 rc=0 을 확인; 선택 결과는 `logs/tb2_post_<P>.sel`) |
| **체크포인트·평가 가중치·학습 실패 처리·σ 격자** | SRT16e4 §1 과 같다: 동결 레시피 `run_d2_sx.py --prior <P> --ntrain 160000 --tag <P>B16e4 --fallback 1 --no-gbprime` (479,426 params; patience 20, 최소 200, 최대 3000 epoch), rung **D2SXSRB160000 · D2SXDMI160000**, attempt 1 → `ckpt/d2sx_<P>_N160000_a1{,_best}.pt`; 판정 태그 `<P>B16e4` = `_best`, `<P>B16e4last` = last-EMA 보고 전용; §3d 사다리(발산 → 시행 2 = 기울기 클리핑 1.0 → 시행 3; `run_tb2.sh train_chain` 이 자동으로 이어 돌린다 — 44d3ab5e 부터 학습을 시작부터 `taskset` 으로 HT 쌍 하나에 고정, 결과 중립); σ 격자 = prior 자체 격자 `sigma_tag = <P>` (§0) |
| **순서 규칙** | 동결 커밋 → prior 마다 kron 1024·2048 병합·b\* 선택(→ 4096) → ALD 개발 재생성·조정 → §5 채움·커밋(두 prior 를 한 커밋 또는 prior 마다; 각 prior 의 실행 커밋 = 그 prior 의 §5 를 담은 커밋) → 주 실행 → 수용 → baseline 단계 → §6. **주 실행은 한 번에 하나만 돈다**(192 워커): SRB 먼저, 이어서 DMI — 순서는 결과와 무관하게 여기서 고정. 한 prior 의 주 실행·baseline 이 끝난 뒤 다른 prior 의 runner 가 돌기 전에는 커밋할 수 있다(runner 가 도는 동안 main 커밋 금지; raw 마다 깨끗한 커밋 하나). **작성자는 동결 전에 다음을 읽지 않는다**: `results/gmm_fits_D2_{SRB,DMI}B16e4/*.npz` 와 `logs/tb2_gpu{0,1,2}.log` (ll_val 이 찍힌다), `logs/tb2_post_{SRB,DMI}.{log,sel}`, `results/sparse/{tune,pick}_{SRB,DMI}_C2.json` 과 `logs/sparse_tune_{SRB,DMI}_C2.log`, `results/ald/tune_PIL{SRB,DMI}.json` 과 `logs/ald_tune_PIL{SRB,DMI}.log`, `results/d2_gbprime_{SRB,DMI}*`·`logs/gbprime_{SRB,DMI}B16e4.log` (읽는 것은 `logs/tb2.log` 의 작업 시작·종료 줄, 파일 개수, 학습 로그의 epoch 줄뿐). 병합 파일 `fit_<P>_Nr8_kronK{1024,2048,4096}_n160000.npz`·`tb2_post_<P>.sel` 의 mtime 은 동결 커밋 시각보다 뒤여야 한다(§5). 희소 baseline 조정(`sparse_tune.py --prior <P> --cell C2 --n 256`, CPU 2 스레드, BLER 없음)은 풀이 고정되는 대로 시작해 다른 단계와 겹쳐 돈다. **GB′ 는 보고 전용이고 그 prior 의 §5 커밋 뒤에 계산한다**(`run_{srb,dmi}_post_gpu.sh <k> GBP <GPU>`; 주 실행과 겹쳐도 된다) |
| **실행 — 주 실행** | `CUDA_VISIBLE_DEVICES= code/run_prior_eval.sh <P> <P>B16e4 d2sx_<P>_N160000_a1[_fb<k>] <bstar> <kronK\|-> <ll_val> <best_sha> <last_sha> "<grid>"` (인자는 §5 가 기록한 것만; `code/run_{srb,dmi}_eval.sh` 에 원문 — §5 커밋에서 채운다). prior 마다 한 번 |
| **실행 — baseline** | SRT16e4 §1 "실행 — baseline" 그대로, prior 마다: 선행 `ald.py regen --tag PIL<P> --prior <P> --cell C2 --fits-tag <P>B16e4 --set dev` → `ald.py tune --tag PIL<P> --ckpt ckpt/<stem>_best.pt` (`run_{srb,dmi}_post_gpu.sh <k> ALD <GPU>`); 본 실행 `code/run_{srb,dmi}_base.sh <ckpt_stem> <best_sha16> <pick_sha16> <tune_ald_sha16> <bstar> <kron_K\|-> <ll_val>` — 순서 PIL → ALD → SP → `pair_baselines`. 빈 GPU 가 없으면 `DEFER_ALD=1` (SRT16e4 §1 의 조건 그대로). SPARSE 격자는 한 판으로 끝낸다(끝값이면 끝값 + 캐비엇) |
| **수용 검사** | SRT16e4 §1 (a)~(e) 그대로, prior = SRB / DMI. (c) 의 글자 조건: 두 태그의 `results/tables_D2_<tag>.txt` 에 문자열 `SITE-SPECIFIC RAY-TRACED TESTBED (prior <P>)` 가 있고 문자열 `CLAIM TESTBED -- sparse specular` 가 없다; `eval_accept.py` 가 검사하지 않는 항목(배너·raw 이름·`N_train` 줄·저장된 prior / sigma_tag·Demo 해시)은 읽어 확인하고 §6 에 적는다. (e) GB′ 로그의 `GMM b* =` 줄 = §5 최종 b\* 이고 `d2_gbprime_<P>_*.npz` 의 mtime 이 병합 파일 뒤 — 어긋나면 GB′ 수치만 무효. baseline: 태그마다 `eval_accept.py`, R5-genie 가 `raw_<P>B16e4` 와 비트 동일, `pair_cross`·`pair_ald` 무결성, pick 재현·`meta\|sparse` |
| **측정 판정** | 주: 표 B `M-ours-bstar → M-ours-dscore-C-V1` (판정점 = 앵커 b\* 의 BLER@16 이 [0.005, 0.9] 안에서 \|log10(BLER/0.1)\| 최소 3 SNR, 점마다 exact 양측 부호검정; POWERED 이고 second arm fewer ≥ 2/3 → (i); first arm fewer ≥ 2/3 → (ii); 둘 다 아님 → (iii); UNDECIDED(범위 안 SNR 이 3 개 미만이거나 불일치 쌍 부족) → (iv)). baseline: `pair_baselines.py --base raw_<P>B16e4 --pil raw_PIL<P> --ald raw_ALD<P> --est PIL<P> --extra raw_SP<P> --add-baselines SBL-loop SBL-pilot OMP-pilot --cell C2 --prior <P> --r0 at1 --provenance manifest` → 표 B `X → V1`, X ∈ 𝔅 15 → prior 마다 새 라벨 15 개 + 주 라벨 1 개; 출력 `results/review_next/pairB_SP<P>.txt` |
| **기전 판독** | SRT16e4 §1 그대로: R = (b\*−V1)/(b\*−genie) 를 −3 dB(1차)와 판정점 합(2차)에서, paired bootstrap 90 % (B 2000, `default_rng(20260926)`); ΔR = R(<P>) − R(D2 B16e4k) 비짝 CI 세 갈래 "회수율이 D2 보다 낮다 / 높다 / 판정하지 못함"; 포화 가드(−3 dB 에서 앵커 b\* 의 BLER@16 이 [0.005, 0.9] 밖이거나 b\* 실패 ≤ genie 실패 → 1차 "판정하지 못함(범위 밖)", 2차만 보고; **가드가 발동하면 −3 dB 의 R 값은 §6 에 옮기지 않는다** — SRT16e4 감사 S1); 정의 불가 규칙 |
| **보고 전용** | V0·V4·V4b, F3 가드, best 대 last V1, GB′, 격자 표, SNR@0.1 (이번에는 격자 안일 수 있다 — 표 B 의 SNR@0.1 격차 줄을 그대로 옮긴다; 판정에는 쓰지 않는다); **누수 층화** `code/dmc_leak_strata.py --tag <P>B16e4 --prior <P>`; **랭크 층화** `code/rank_strata.py --tag <P>B16e4 --prior <P>` (rank-1 층이 거의 비어 있을 것 — 그대로 적는다); **채널 추정 NMSE 의 CDF** `conference/figures/paper_f33cdf.py <P>` — 패널 넷 = −3 dB 와 판정점 3 SNR, **−3 dB 가 판정점이면 넷째 패널 = 판정점 바로 위의 격자 SNR**(이 커밋의 스크립트 원문); ALD·SPARSE 조정 표, `pair_cross`·`pair_ald` 의 등록 비교 |
| **그림** | 11 곡선(`paper_f16deep.SHOW`)을 전 SNR n = 2560 으로: `conference/figures/paper_f21dmc.py <P>` → `F21srb_col` · `F21dmi_col`. y 축은 원고 주 그림 F16deep_wide (a) 의 규칙(이 커밋의 `ROOM` 분기 원문): 0 실패 점이 없고 모든 점·막대 끝이 2e-4 위면 (2e-4, 1.2), 아니면 (3e-5, 1.2); 0 실패 점에서는 곡선이 끊기고 Perfect CSI 에만 Wilson 상한 화살표(`paper_f16deep.draw`). n = 20480 보강은 하지 않는다 |
| **다중성** | prior 마다 주 라벨 1 + baseline 새 라벨 15; 등록 사이·prior 사이 보정 없음(다른 데이터셋과 같은 관례) |
| 비용·일정 [추정] | 학습 2 개 5 s/epoch × 300–1200 epoch ≈ 0.5–1.7 h; GMM 격자 42 작업 GPU 3 장 ≈ 3–4 h; SPARSE 조정 ≈ 2–3 h; 주 실행 prior 당 2 태그 ≈ 1.7 h (합 3.4 h, 순차); baseline prior 당 ≈ 15 분 |

## 2. 라벨 (여기서 고정; "측정" 이지 arm 판정이 아니다)

표 B `b* → V1` (C2), prior 마다. 이름: SRB = "Sionna RT 방 (내장 `box` 장면 28 GHz, 고정 기지국 한 곳, block split)", DMI = "DeepMIMO 실내 (`i1_2p4` 2.4 GHz, 고정 기지국 한 곳, block split)".

| 결과 | 기록 |
|---|---|
| (i) | "<이름> 에서 V1 이 b\* 보다 적게 실패 (prior·기전 축 측정, UNGATED)" — 회수율·ΔR 문장과 함께 |
| (ii) | "<이름> 에서 b\* 가 V1 보다 적게 실패" — 회수율(음수 포함)·ΔR 과 함께 |
| (iii) | "판정하지 못함 (유의 방향 없음)" |
| (iv) | "판정하지 못함 (검정력 미달)"; SNR 격자를 결과 뒤 늘리지 않는다 |
| 학습 실패 | BLER 미실행, "학습 실패" |

- baseline: (i)~(iv) 는 같은 규칙을 X → V1 에 적용. **"전부" 문장**: 그 prior 의 주 라벨이 (i) 이고 15 개가 모두 (i) 일 때만 "<이름> 에서 V1 이 등록된 baseline 전부(16 개, 희소 baseline 포함)보다 적게 실패 (UNGATED 측정)"; 여기에 R_{X\*}(−3 dB) 90 % CI 하한 > 0 (`pair_baselines` 의 condition 줄 MET) 이면 "…전부와 멀어진다"; 아니면 (i) 의 수와 (i) 가 아닌 arm 의 이름·라벨을 그대로 적는다.
- 어디에서도 동치 문구를 만들지 않는다. 모든 라벨 문장에 §1 "고유 사항" 의 (1) 유한 풀·한 장소 · (2) 가까운 이웃 · (3) 금속 벽·1 차 반사(SRB 에만) · (4) 선택 편향 · (6) 개발 채널(baseline 라벨에만) 을 붙인다. 범위: 이 방·이 기지국·이 split·이 크기 한정.

## 3. 미리 적는 예측 (빗나가면 그대로 쓴다; 도시 풀 두 개의 결과와 §0 의 통계·Perfect CSI 선별값을 본 뒤의 예측이며, 두 풀에서 prior 의존 arm 의 BLER 은 본 적이 없다)

prior 마다 따로 채점한다(문장마다 SRB / DMI).

1. **표 B: (i)** — V1 이 b\* 보다 적게 실패. 확신 중간 이하. 근거: D2 (B16e4k) · 38.901 UMi28 · DeepMIMO 도시 · Sionna RT 도시가 (i) 였다. 반대 근거: 방 하나의 채널은 (위치, yaw) 3 차원 다양체라 큰 K 의 kron GMM 이 잘 덮을 수 있다; 판정점이 3 개에 못 미치면 (iv). 채점: (i) = 적중; (ii)·(iii) = 빗나감; (iv) = 채점 불가.
2. **판정점 = −3 / 0 / +3 dB 이고 POWERED** (앵커 b\*). SRB 확신 중간, **DMI 확신 낮음**(선택 경위 4: +2 dB 선별값 0.003). 채점: 세 점이 −3 / 0 / +3 이고 POWERED = 적중; 범위 안 SNR 이 3 개 미만이거나 다른 세 점 = 빗나감.
3. Perfect CSI 의 BLER 수준: **관측됨(채점 제외)** — 선별에서 봤다(§0).
4. **1차 ΔR 의 포화 가드는 발동하지 않는다**(−3 dB 에서 b\* 의 BLER@16 ∈ [0.005, 0.9] 이고 b\* 실패 > genie 실패). 채점: 미발동 = 적중. ΔR 의 방향은 예측하지 않는다.
5. 회수율 R(−3 dB) 의 90 % CI 하한 > 0 (가드가 발동하면 채점 불가).
6. `R2-ours-G → b*`: b\* (second arm) 가 ≥ 2/3 점에서 적게 실패. 확신 높음.
7. **SNR@0.1 이 격자 안**: 표 A 에서 V1·b\*·genie 의 SNR@0.1 이 모두 "> 15" 가 아니다(세 arm 따로 채점하지 않고 한 문장). 그리고 표 B `b* → V1` 의 SNR@0.1 격차(b\* − V1) > 0 dB (격차가 n/a 면 채점 불가).
8. GB′ median ≤ 0.90.
9. 학습: 최종 시행이 patience 정지이고 epoch ∈ [300, 1500] (발산 여부는 예측하지 않는다 — SRT 는 시행 1 이 발산했다). [이 줄을 쓸 때 본 것: 두 학습 로그의 epoch 30 부근 줄 — 학습 곡선이지 판정량이 아니다]
10. GMM: **b\* = kron 계열**이고 K ≥ 1024 (도시 풀·UMi28·MIX3 선례는 4096 = 격자 끝). 두 문장 따로 채점하지 않는다.
11. V0: 가드 발동률이 −3 dB 에서 ≥ 0.5 이고 −3 dB BLER ≥ 0.9. best 대 last V1: 판정하지 못함(pooled p > 0.05).
12. 대조군 `b* → b*-scalar`: (iii). 채점: (iii) = 적중; (i)·(ii) = 빗나감; (iv) = 채점 불가.
13. baseline 15 개: **(ii) 0 이고 (i) ≥ 12**; `pair_ALD<P>.txt` 의 A3 (`ALDv-pilot → V1-pilot`) = (i); `pairB_SP<P>.txt` 의 실패 수 표에서 −3 dB 에 `SBL-pilot` < `R0-pilot@1`. 세 문장을 따로 채점한다. (`V1-pilot` 의 라벨은 예측하지 않는다 — 도시 풀에서는 (iii) 였지만 랭크가 높은 채널에서는 루프 이득이 있을 수 있다.)
14. 랭크 층화: 판정점 시행에서 비중 ≥ 0.95 층의 비율 ≤ 0.05 (세 판정점 모두).
15. 누수 층화·NMSE CDF: 예측하지 않는다.
16. 빗나갈 경로: (a) (ii) 또는 (iii) → 그대로 기록, 레시피 탐색 없음, 사후 설명은 사용자; (b) R 이 음수 → 그대로; (c) (iv) → 그대로, **SNR 격자 확장도 다른 풀로의 교체도 이 등록 안에서는 하지 않는다**(새 풀은 새 등록 + 사용자 결정); (d) 발산 → §3d; (e) b\* 가 full 512 → full 1024 한 번 + 캐비엇; (f) baseline 에 (ii) 가 하나라도 → 그대로, 재조정 없음.

## 4. 선행 작업과 실행 현황 (갱신한다; 시각은 `date` 로 읽음)

| 항목 | 상태 |
|---|---|
| rank-1 탐색·Perfect CSI 선별 (`rank_probe_2026-10-11/`: Sionna 기지국 위치 탐색, DeepMIMO 시나리오 탐색, 방 장면·재질·깊이, 선별 도구) | **완료·커밋 44d3ab5e** (10-11 09:59 → 11:00 CDT) |
| 풀 빌더·연결(`srb_build.py`, `dmi_build.py`, `common`·`dmimo`·`analysis` 등, `run_{srb,dmi}_*.sh`, `run_room_gpu.sh`) + sha 고정·보정·testbed·σ 격자·일괄 EM 검사 + 기존 경로 비트 동일 검사 | **완료·커밋 44d3ab5e** (§0) |
| 그림 스크립트의 방 풀 분기(`paper_f21dmc.py` `ROOM`, `paper_f33cdf.py` 넷째 패널 규칙) | 이 문서의 v1 커밋에 포함(DMC · SRT 의 그림·기록 바이트 동일 확인) |
| 학습 SRB · DMI (`@train`, tmux `tb2room`, GPU 1 · GPU 0, 시작부터 HT 쌍 고정) | 진행 중: 큐 시작 10-11 11:03 CDT (git 44d3ab5e); split_hash c009329584978bd9 (SRB) · fecf46b30175b5c8 (DMI), E‖H‖² 1.000000 |
| GMM 격자 SRB · DMI (42 작업, `logs/tb2_queue.txt`, GPU 2 → 학습 뒤 GPU 0·1 도) | 진행 중: 10-11 11:03 CDT 부터 (`logs/tb2.log`) |
| SPARSE 조정 SRB · DMI (`run_{srb,dmi}_sparse_tune.sh`, tmux `sptsrb` · `sptdmi`, CPU 2 스레드씩) | 진행 중: 10-11 11:03 CDT 시작 (git 44d3ab5e; 동결 전에 읽지 않는다) |
| 이 문서 초안 v1 → 적대적 검토(Fable) → v2 → 동결 커밋 | 초안 2026-10-11 11:10 CDT |
| prior 마다: 병합·b\* 선택 → ALD 조정 → §5 → 주 실행 (+ GB′) → 수용 → baseline → §6 → 기록 감사(Fable) → 그림 | 대기 |
| 공개: GPU 2 에서 돌던 시드 학습(`run_srt_seeds_train.sh`: SRT a2 · a3, DMC a2 는 patience 로 끝남, DMC a3 는 epoch 675 에서 멈춤 — 이 등록과 무관)을 10-11 09:53 CDT 에 멈추고 GPU 를 탐색·이 등록에 넘겼다(`logs/seeds_SRT_train.log`) | — |

## 5. 평가 전 고정 기록 (실행 전에 채우고 커밋한다)

(동결 뒤 prior 마다 채운다.)

## 6. 결과 (실행 뒤 전사; 생성기와 기록 감사)

(실행 뒤 채운다.)
