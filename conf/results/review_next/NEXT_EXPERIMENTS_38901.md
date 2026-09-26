# NEXT_EXPERIMENTS_38901 — 3GPP TR 38.901 두 번째 testbed(표준 모델 쪽): **UMi28 주 실험(등록 판정) + MIX3 보고 전용 부속 점** (셀 C2, 동일예산 N′ = 1.6e5, 태그 U28B16e4 / MXB16e4) — 사전 등록 v2

- 작성: 2026-09-26 10:22 CDT (= 09-27 00:22 KST), Claude Code (Fable 5.1), 초안 v1 → 적대적 검토 2건(A 설계·통계 12건, B 실행 가능성·코드·사실 6건; `prereg_reviews_2026-09-26/review_{A,B}_PARETO_38901.md`) 반영 v2 2026-09-26 10:41 CDT. 동결 시각 = 동결 커밋 시각(`DECISIONS.md` 같은 줄). **결과 관측 전**: UMi28·MIX3 의 어떤 체크포인트·적합도 BLER 로 평가된 적이 없다(학습·GMM 격자는 GPU 큐 `tb2` 에서 진행 중, §4). 커밋 뒤에는 §1~§3 을 바꾸지 않는다; 바꿔야 하면 사용자 승인 + `DECISIONS.md`.
- 사용자 결정(원문 `conf/DECISIONS.md`): **[2026-09-27 00:07 KST = 09-26 10:07 CDT] UMi 28 GHz 단일 = 주 실험(등록 판정), MIX3 = 보고 전용 부속 점** (아침 목록 `MORNING_QUESTIONS_2026-09-26.md` 1번의 선택지 (c)); [2026-09-26 15:03 KST = 01:03 CDT] (1) 경계 양쪽 검증(SV8e 와 38.901 을 둘 다 등록·실행·보고), (2) UNGATED, (3) GMM K 는 kron 4096 에서 멈춤·헤드라인 불변; [15:07 KST] (2) 표준 모델 쪽 = MIX3 — 이 항목은 00:07 KST 결정으로 **"MIX3 주" 에서 "UMi28 주 + MIX3 부속" 으로 바뀌었다**(기록은 둘 다 남긴다).
- 틀: `NEXT_EXPERIMENTS_C6B16e4.md` v2 (§0~§6; UNGATED 측정·§3d 사다리·격자 반복 규칙·수용 검사 (a)~(e)·회수율 CI), `NEXT_EXPERIMENTS_B32e4.md` §1, `10_SPEC_stageC.md` §3d·§6d·§6l, `01_RULES.md` §4·§5·:76·:77, `08_SPEC_analysis.md` §2(판정점 3개·power guard·앵커 = baseline), review_next v3 §0(테스트 0..2559, `_best.pt`, CPU 수신기, "p ≥ 0.05 는 판정하지 못함이지 차이 없음이 아니다"). 재료: `PREREG_FACTS_2026-09-26.md` §0·§C(공통 사실·SV 쪽) + `_CHECK.md` 정정, `results/review_next/testbed2_phase0/{report_phy.md, selection.md}`, `code/mix3.py` 머리말, `results/testbed_{UMi28,MIX3}.txt`, `results/sigma_grid_D2_{UMi28,MIX3}.txt`.
- 목적: **경계 양쪽 검증의 "잠재 차원이 낮은 쪽"**. 0단계 채널 통계(수신기 BLER 미사용)는 3GPP 38.901 채널에서 유한 K GMM 이 파일럿 단계의 K=1 Gaussian → 잠재 오라클 격차를 0.62–0.74 메운다고 쟀다(D2 0.26). 위치·방향 등 소수 잠재 변수로 정해지는 표준 채널에서는 **학습 prior(V1) 의 우위가 없다** 는 예측을 세우고, 같은 파이프라인·같은 규칙으로 잰다. 반대쪽(SV8e: 독립 연속 잠재 각도가 많음 → V1 우위 예측) 은 `NEXT_EXPERIMENTS_SVB16e4.md` 에 따로 등록한다. **두 결과의 공동 판독표는 이 문서 §2.3 에 둔다.** 결과가 어느 쪽이든 둘 다 보고한다. 헤드라인(C2 1.6e5 B16e4k)·D2 판정은 어느 결과에서도 바뀌지 않는다.
- 선택 경위(공개; `01_RULES.md:77` "testbed 선택 근거는 물리적으로 표준이라서" 에 부합): 38.901 은 채널 통계만 보고 미리 "GMM 친화" 로 분류된 표준 모델이다. 0단계의 선택 문서(`selection.md:61`) 는 표준 계열 가운데 MIX3 가 "가장 덜 불리" 하다고 적었고 15:07 KST 결정이 MIX3 를 골랐다. 이후 사용자가 UMi 28 GHz 단일을 주 실험으로 바꿨다 — 이유(사실만): 단일 시나리오라 설명이 단순하고 사후 선택 의심이 없다; 0단계 메움 UMi28 0.68 vs MIX3 0.66 (K=64, −3 dB) 은 결과를 바꿀 차이가 아니다; MIX3 는 이미 학습 중이라 부속 점으로 보존한다. MIX3 학습(09:37 CDT)·GMM 격자는 UMi28 결정(10:07 CDT) 전에 시작됐다 — BLER 은 둘 다 관측된 적이 없으므로 결과를 본 뒤의 선택이 아니다(전환 시점에 MIX3 의 학습 곡선 — epoch ~94, val 0.485 — 은 보였으나 판정량이 아니다).

---

## 0. 출발점 (판정에 쓰지 않는다)

**0단계 채널 통계** (`testbed2_phase0/report_phy.md` 표 "Primary metric", `selection.md` 표 5·9행; 수신기 BLER 미사용; 지표 = 파일럿 단계 디노이징(Tp=Nt, ν=σ²/Nt) 에서 EM-GMM 이 K=1 Gaussian → 잠재 오라클(LO) 격차를 메운 비율 closed, K ∈ {16, 64, 256}; 0단계 자체 RNG(seed 1/2), 파이프라인 스트림 7/8/10 이 아님):

| 구성 (8×4) | −3 dB 격차 K1−LO (NMSE) | closed 16/64/256 (−3 dB) | +3 dB 격차 | closed 16/64/256 (+3 dB) |
|---|---|---|---|---|
| **UMi28 mix** (seed 1 / seed 2) | 0.173 / 0.178 | **0.57/0.68/0.71 · 0.58/0.69/0.71** | 0.055 | 0.54/0.63/0.64 |
| UMi28 mix, LoS 부분 / NLoS 부분 | 0.259 / 0.117 | 0.55/0.68/0.74 · 0.61/0.68/0.66 | – | – |
| **MIX3** (UMi28+UMa28+RMa3.5, 1/3 씩) | 0.195 | **0.58/0.66/0.66** | 0.065 | 0.57/0.65/0.65 |
| D2 S2 (기준값; seed 1 / 2) | 0.249 / 0.249 | 0.19/0.26/0.29 · 0.20/0.25/0.29 | 0.089 | 0.18/0.25/0.24 |
| SV8e (반대쪽; `selection.md` 1행) | 0.133 | 0.17/0.22/0.19 | – | 0.24/0.16 |

- 읽기(0단계 보고서의 기전 해석, 보조): 표준·RT 채널은 위치·방향 등 소수 잠재 변수로 정해져(내재 차원 ~3, D2 ~12) 유한 K GMM 이 덮는다; 이득 조건은 "독립적인 연속 잠재 각도의 수" (SV 군집 8 → 0.22, 3–8 → 0.37, 3 → 0.44). **이 해석이 §3 예측의 근거이며, 이 실험이 검정하는 가설이다.**
- 0단계 캐비엇(공개): 38.901 의 LO 는 실현된 경로 이득을 고정한 오라클이라 격차 자체가 D2 보다 작다(0.173–0.195 vs 0.249); UMi28 은 LoS 부분(격차 0.259)과 NLoS 부분(0.117)이 다르고 LoS 비율은 0.40 이다; 0단계 적합은 full 공분산·K ≤ 256 만 봤다.

**비교 대상 (짝 없음; 문맥용)** — D2 C2 1.6e5 헤드라인 `raw_B16e4k` (`tables_D2_B16e4k.txt`, legacy-last): −3 dB 실패 b\* 623 (0.243) / V1 371 (0.145) / genie 87 (0.034); 표 B `b* → V1` 판정점 −3/0/+3, pooled 454:78, POWERED 3/3; 회수율 R(−3 dB) 0.470 [90% 0.427, 0.512]; SNR@0.1 격차 +1.41 dB [1.22, 1.64]. 같은 캠페인의 다른 두 prior 변형(BLER 전): D3 (S2c) GB′ median 0.559 (b\* kron 4096), SV8e GB′ median 0.918 (b\* full 256) — `DECISIONS.md` [2026-09-26 18:50 KST].

**testbed 검증** (`results/testbed_UMi28.txt` @0a3bb946, 09-26 23:59 KST = 09:59 CDT; `results/testbed_MIX3.txt` @598b6de6, 23:35 KST = 09:35 CDT; `code/testbed_mix3.py`, 허용오차는 실행 전 고정, BLER 없음):

| 검사 | UMi28 | MIX3 |
|---|---|---|
| TMXa 정규화(검증 스트림 8, n=20000; 상수는 학습 스트림 7 에서 보정 → 표본 외 검사; 4 s.e. 대역) | mean ‖H‖²/(NrNt) = 0.99875 (s.e. 0.00204) **PASS**; 블록 전력 CV 0.289 | 0.99880 (s.e. 0.00288) **PASS**; CV 0.407 |
| TMXb 원소별 E\|H_ab\|² (보고) | 0.9858–1.0088 | 0.9877–1.0101 |
| TMXc LoS 비율·시나리오 비중 vs 0단계 프로브(4 s.e.) | LoS 0.4094 vs 0.400 (4 s.e. 0.064); umi@28 GHz 비중 1.000 **PASS** | LoS 0.2712 vs 0.273 (0.058); 비중 0.333/0.334/0.333, LoS 0.407/0.196/0.211 **PASS** |
| TMXd 파일럿 단계 K=1 Gaussian NMSE @ −3 dB (ν=σ²/Nt) vs 프로브(\|diff\| ≤ 0.02) | 0.3230 vs 0.3228 **PASS** | 0.3229 vs 0.3150 **PASS** |
| TMXe T2b 파일럿 결정(erank Rt < 0.9·Nt = 3.6) / erank(C_ens) / 빔공간 top-4 에너지 중앙값 | erank(Rt) 3.494/4 → **eigen 정렬** / 27.74/32 / 0.699 | 3.483/4 → eigen / 27.54/32 / 0.744 |
| TMXf 생성 비용 | sample() 9.1 ms/호출, 4096 표본 5.4 s, 20000 표본 30.4 s | 10.4 ms, 4.2 s, 24.0 s |
| 종합 | **ALL PASS** (88 s CPU) | **ALL PASS** (70 s CPU) |

**σ 격자** (`runner.py sigma --testbed D2 --prior <p> --cell C1 C2 --tag <p>`, 헤드라인·S2c·SV8e 와 같은 절차: Gaussian 수신기(M-ours-G 인터페이스), n=64, 시행 0..63, 7 SNR, ν_q 만 기록): UMi28 (`sigma_grid_D2_UMi28.{txt,npz}` @0a3bb946, 09-27 00:03 KST = 09-26 10:03 CDT) 20 점, ν_q 1–99 백분위 [2.1361e-03, 1.4020e+00] → σ_t [3.268110e-02, 8.372515e-01]; MIX3 (`sigma_grid_D2_MIX3.{txt,npz}` @598b6de6) [2.1282e-03, 1.4452e+00] → σ_t [3.262043e-02, 8.500441e-01]. 헤드라인 D2 격자 [3.3062e-02, 8.4516e-01] 대비 양끝 −1.2 % / −0.9 % (UMi28), −1.3 % / +0.6 % (MIX3). **공개: 이 측정으로 UMi28·MIX3 의 테스트 시행 0..63 (C1·C2, 7 SNR) 이 Gaussian 수신기(R2-ours-G 와 같은 궤적)로 한 번 실행됐다** (BLER 은 읽지도 쓰지도 않음, 헤드라인·D3·SV 관례와 같음). C2 에서 반복 1 의 ν_q = σ²/Tp 는 결정적이므로 −3..15 dB 의 반복 1 질의는 두 격자 모두 안에 있다(UMi28 ν_hi 1.402 > σ²(−3 dB)/4 = 0.499).

---

## 1. 고정되는 것

| 항목 | 값 |
|---|---|
| **셀·예산·시행** | C2 = 8×4, T 16, Tp 4, K = 42 정보 비트, rate-1/2 conv (133,171)_8, QPSK, 16 반복, 7 SNR (−3, 0, 3, 6, 9, 12, 15 dB; **결과 뒤 격자를 늘리지 않는다**), n = 2560, 테스트 시행 **0..2559** (chunk 40 → {(40k, 40): k = 0..63}), 수신기 CPU complex128. 시행 시드 `default_rng([20260926, 2, PID, 8, 16, 4, snr+100])` (`common.trial_rng`), **PID UMi28 = 8, MIX3 = 7** → 두 prior 의 시행은 서로도, D2(PID 4)·D3(5)·SV8e(6) 와도 다른 스트림 → **모든 비교는 짝 없음(unpaired)**. 동일예산 N′ = 160000: 채널 집합 하나 = `arms.training_set("D2", <prior>, 8, 4, 160000)` (스트림 7) 을 GMM 적합(`runner._sets`)과 score 학습(`score.train`; 자체 9:1 = 144000/16000)이 함께 쓴다; GMM 검증 5000 = 스트림 8; Gaussian arm 의 Chat 도 같은 집합 |
| **지위** | **UNGATED** (사용자 결정 15:03 KST (2); D1 형제 규칙을 새 prior 로 넓히지 않는다) → 결과는 **"prior·기전 축 측정"** 이며 arm 판정이 아니다. 헤드라인(C2 1.6e5 B16e4k) 불변; 38.901 은 어느 결과에서도 헤드라인이 되지 않는다. **UMi28 = 주 실험(등록 판정·§2 라벨·§2.3 공동 판독)**, **MIX3 = 보고 전용 부속 점**(같은 규칙·같은 세 갈래 문자열로 실행·보고하되 판정·공동 판독표에 들어가지 않는다) |
| **생성 모델** (`code/mix3.py` 머리말; 동결 — 바꾸려면 새 결정 + 새 prior id) | Sionna 2.1 (`sionna-no-rt` 2.1.0) `sionna.phy.channel.tr38901`: 블록마다 시나리오 ~ Unif{UMi @ 28 GHz, UMa @ 28 GHz, RMa @ 3.5 GHz} (MIX3, 코드 0/1/2 각 1/3) — **UMi28 은 추첨을 코드 0(UMi 28 GHz) 으로 제한**(`mix3.NSCEN["UMi28"] = 1`; 나머지 경로는 MIX3 와 동일); 배열 PanelArray 1 행 × N 열(단일 열 ULA), 반파장, 단일 편파 'V', 안테나 패턴 omni; BS Nr = 8, UE Nt = 4, direction 'uplink'; UMi/UMa(o2i_model 'low')/RMa, `enable_pathloss=False`, `enable_shadow_fading=False`, 나머지 Sionna 기본값(spec 19.2, 공간 일관성·blockage 없음, LSP 는 set_topology 에서); 토폴로지 `gen_single_sector_topology(B, 1, scenario, indoor_probability=0.0)` (드롭당 UE 1, 실외, BS 는 섹터 중심 yaw·시나리오 downtilt) 뒤 **UE 방향을 yaw ~ U[−π, π), pitch = roll = 0 으로 덮어씀**, RMa in_car = False, los = None (38.901 LoS 확률); 스냅샷 = 협대역 블록 페이딩, 첫 시간 표본에서 CIR 경로 합(H[a, b] = BS 안테나 a, UE 안테나 b), precision 'single' → complex128; **앙상블 정규화** E‖H‖_F² = NrNt: H = H_raw/√P_RAW, P_RAW 는 학습 스트림 7 의 N_CAL = 160000 표본에서 한 번 재고 상수로 동결 — **UMi28 P_RAW 0.9901769449816289, TRAIN_SHA a2f617f3111ea64e; MIX3 P_RAW 0.9953569092328413, TRAIN_SHA 9f595676e0d1a032** (드롭별 전력은 모델의 K-factor·O2I 변동을 유지); vec 열 우선. 결정성: numpy 스트림이 유일한 난수원 — 청크(4096 블록)마다 (시나리오 코드, 64 비트 시드) 를 뽑아 Sionna 의 CPU torch 생성기를 그 시드로 두고 시나리오별 새 모델로 생성, 상태 복원; torch 단일 스레드; `sample(rng) == sample_vecs(rng, 1)[0]`; 프로세스 간 비트 동일(`selftest_mix3.py`). **상수는 8×4 만 보정**(다른 배열은 오류). 프로브(0단계 `phy_tb.py`) 와의 관례 차이(법칙은 같음): 시나리오를 집합별 정확한 1/3 이 아니라 블록별로 추첨; UE yaw 를 torch 전역 생성기가 아니라 시드된 Sionna 생성기에서 뽑음 |
| **파일럿** | D2 의 T2b 규칙(`common.make_pilots`) 을 학습 집합에서 잰 Rt = E[HᴴH]/Nr (동결 상수 `mix3.RT`) 에 적용: erank(Rt) UMi28 3.494 / MIX3 3.483 < 0.9·Nt = 3.6 → **eigen 정렬 파일럿** (U2·SV8e 와 같은 처리; 규칙 적용이며 새 판단 아님). **C2 (Tp = Nt = 4) 에서는 X_p X_pᴴ = 4I 로 DFT 와 같은 충분통계** — 파일럿 관측 Y X_pᴴ/4 = H + 백색잡음의 법칙이 같다(시행 스트림은 다름). raw 파일 이름의 `_eig_` 는 이 결정의 흔적이다 |
| **GMM 격자와 b\*** | 기본 격자 full K ∈ {16, 32, 64, 128, 256, 512} (정확 경로 + κ 격자), kron K ∈ {16, …, 512} (일괄 경로) + kron 1024·2048 은 재시작 후보 3 개(`.k0r{0,1,2}.npz`) → CPU 병합(`fit_gpu.py 8 kron K 160000 <tag> --merge --prior <p>`); 선택 = 검증 우도 최대(`arms.gmm_selection`, 스트림 8; `arms.D2_KS` 에 4096·8192 포함, `load_fits` 는 병합 파일만 적재). **반복 규칙(B32e4 §1·C6 §1)**: b\* 가 그 계열의 최대 K 이면 2K 를 같은 프로토콜(재시작 3·상한 500·검증 조기 종료)로 적합해 다시 선택 → kron 은 4096 후보 3 개가 큐에 미리 있으므로 병합만 한다; **kron 4096 에서 멈춘다(K = 8192 없음; 사용자 결정 15:03 KST (3)) → 그때는 b\* = 격자 끝 + 캐비엇**. full 계열 끝(b\* = full 512) 이면 같은 반복 규칙을 full 에 적용한다: **full 1024 를 같은 프로토콜(κ 격자 × 재시작 3, 상한 500, 검증 조기 종료; `fit_gpu.py 8 full 1024 160000 <tag> --prior <p>`, 정확 경로)로 한 번 적합해 다시 선택하고 1024 에서 멈춘다 + 격자 끝 캐비엇** — 결정 (3) 의 구조(기본 격자 최대 K 의 2 배에서 멈춤)를 full 계열에 옮긴 것이며 full 2048 은 적합하지 않는다(비용 [추정]: K=512 의 4 배 ≈ 2.7 GPU-h). 후보 파일 누락 시 같은 시드의 그 재시작만 재실행(결정적)하고 §5 에 적는다. 상한 500 정지·재시드 수·구현 경로(정확/일괄)·수렴 규칙(학습 우도 증가량 < tol 로 멈춘 경우 C6 §6.5 형태의 캐비엇) 은 §5 에 파일별로. BLER 은 선택에 쓰지 않는다. 미병합 후보(예: 규칙이 발동하지 않은 kron 4096) 는 존재를 §5 에 적고 쓰지 않는다 |
| **체크포인트·평가 가중치** | 동결 레시피 `run_d2_sx.py --prior <p> --ntrain 160000 --tag <TAG> --fallback 1 --no-gbprime` (hp: dit / vp / angle, lr 2.238046e-3, ema 0.999, batch 256, emb 256, width 64, depth 6, heads 8, patch 1, 479,426 params; patience 20, 최소 200, 최대 3000 epoch; float32 학습), rung **D2SXUMi28160000** (`score._rung_ix` 1665) / **D2SXMIX3160000** (1276), attempt 1 → `ckpt/d2sx_<p>_N160000_a1.pt` (last-EMA) + `_best.pt`. **측정 판정 태그 `U28B16e4` = `_best.pt`** (v3 §0); **`U28B16e4last` = last-EMA, 보고 전용**; MIX3 도 같은 형식(`MXB16e4` = `_best`, `MXB16e4last` = last). "시도했다" = patience 종료 또는 ≥ 200 epoch (01_RULES §5) |
| **학습 실패 처리** | `stopped_by=diverged` 또는 `aborted` → 10_SPEC §3d 사다리(`run_tb2.sh train_chain` 이 같은 GPU 에서 자동 연쇄): 시행 2 = 기울기 클리핑 1.0 (`--fallback 2`, `_fb2.pt`), 시행 3 = + lr/3 (`--fallback 3`, `_fb3.pt`); 같은 rung·attempt = 같은 데이터 스트림; 시행 간 선택은 val loss 만, 발산 체크포인트로 평가하지 않는다; 시행 3 도 실패 → "학습 실패", BLER 없음. stopped_by 가 patience/max_epochs/diverged 가 아니면(kill 등) 사슬을 멈추고 수동 결정(§4 에 기록). `max_epochs` 정지는 유효 |
| **σ 격자** | 학습·GB′ 모두 prior 자체 격자 `sigma_tag = "UMi28"` / `"MIX3"` (§0; 체크포인트에 저장; 학습 로그 머리말 `sigma grid MEASURED … [3.2681e-02, 8.3725e-01]` / `[3.2620e-02, 8.5004e-01]` 로 확인). 재측정하지 않는다 |
| **실행 (테스트 집합, 전 arm = D2·D3·SV 와 같은 14 arm 구성)** | 격자 확정·§5 채움·커밋 뒤에만. 범용 평가 스크립트(db038a10·33719007·2f6b6497) `code/run_prior_eval.sh <prior> <TAG> <ckpt_stem> <bstar> <kronK\|-> <ll_val> <best_sha> <last_sha> <grid>` (9번째 인자 = 수용 검사 격자 문자열, **필수**; kron 4096 까지 병합했으면 `,4096`, full 1024 까지 적합했으면 `full:…,1024` 포함) = ① `runner.py run --testbed D2 --prior <p> --cell C2 --n 2560 --chunk 40 --ntrain 160000 --stagec-ckpt ckpt/<stem>_best.pt --tag <TAG>` → `runner.py analysis --tag <TAG>`; ② 보고 전용: 같은 명령을 `ckpt/<stem>.pt --tag <TAG>last` → analysis; ③ 태그마다 `run_manifest.py`, `guard_report.py`, `recovery_ci.py` 를 −3 dB 로 한 번, 그리고 스크립트가 `results/tables_D2_<TAG>.txt` 의 앵커 b\* 판정점을 정규식으로 읽어 한 번; ④ `eval_accept.py`(아래); ⑤ `frontier_ci.py --recovery "raw_<TAG>:C2:-3" "raw_B16e4k:C2:-3"` (비짝 차이 CI; 2차 = 판정점 합 대 D2 −3,0,3 합). 선행: `ln -s gmm_fits_D2_<TAG> results/gmm_fits_D2_<TAG>last`. 로그 `logs/run_prior_eval_<TAG>.log`, 끝 표시 `PRIOR_EVAL_DONE`. **UMi28 명령**: `code/run_prior_eval.sh UMi28 U28B16e4 d2sx_UMi28_N160000_a1[_fb<k>] <bstar> <kronK\|-> <ll_val> <best_sha> <last_sha> "<grid>"`; **MIX3 명령**: `code/run_prior_eval.sh MIX3 MXB16e4 d2sx_MIX3_N160000_a1[_fb<k>] …`. 두 prior 의 BLER 은 CPU 192 워커로 **순차**(runner 에 워커 수 인자가 없고 01_RULES §4 가 지정을 금지한다) — 스크립트 인자 값은 §5 가 기록한 것만 넘긴다. 출력: `results/review_next/<TAG>_accept.txt`, `recovery_<TAG>{,last}.txt`, `recovery_diff_<TAG>.txt` |
| **수용 검사** | (a) 격자 완전성(§5 채우기 전): `gmm_fits_D2_<TAG>/fit_<p>_Nr8_*_n160000.npz` 에 full 6 개 + kron {16..512} 6 개 + kron 1024·2048(격자 끝이면 4096) 병합 파일, K ≥ 1024 는 후보 `.k0r{0,1,2}.npz` 3 개; (b) 태그마다 점마다 raw 청크 정확히 {(40k, 40): k = 0..63}, meta `ntrain=160000`, `bstar`·`kron_K`·`ll_val|<bstar>` 이 §5 최종 선택과 일치(\|Δll\| ≤ 1e-9), 두 태그의 `bstar`·`kron_K`·`em_sec` 동일, 같은 fits 디렉터리; (c) `stagec_ckpt_id` sha·epoch·best_epoch·role 이 §5 와 일치(best: epoch == last.best_epoch), 저장된 prior·sigma_tag = 해당 prior(runner 는 prior 불일치만 거부, `runner.py:1201-1206`; sigma_tag 는 §5 에서 확인), Demo 해시 동일, 표 머리말 N_train = 160000, raw 이름에 `UMi28`/`MIX3`, analysis 머리말에 해당 배너(`UMI28_WARNING` / `MIX3_WARNING`; "sparse specular" 문구 없음); (d) genie 재현: 외부 참조 raw 가 없다(새 스트림; σ 격자 측정은 BLER 을 기록하지 않았다) → `--ref-raw raw_<TAG>` 로 **last 태그의 `R5-genie|blk_err·ber·tauL_gmean·alphaD @1..16 이 best 태그와 7 SNR 전 시행 비트 동일**(genie 는 학습·적합 무관; 자기 비교인 best 쪽은 자명하게 통과); (e) GB′ 로그의 `GMM b* = (계열, K)` 가 §5 최종 b\* 와 같고 npz 가 격자 확정 뒤에 쓰였을 것 — 학습 종료 시 자동으로 도는 GB′ 는 큐 설계상 없고(`--no-gbprime`), GB′ 는 격자 확정 뒤 `run_d2_sx.py --prior <p> --ntrain 160000 --tag <TAG> --fallback <k>` 재개(학습 없음, last 파일 기준) 로 한 번 계산한다(산출 `results/d2_gbprime_<p>.csv`, `d2_gbprime_<p>_N160000_a1[_fb<k>].npz`); npz mtime 과 격자 확정 시각(마지막 병합 파일 mtime) 을 §5·§6 에 나란히 적는다; 잘못된 순서로 만들어진 GB′ 는 폐기. 명령: `eval_accept.py --prior <p> --bstar <kron\|gmmK> [--kron-K <K>] --ll-val <정확한 float> --tag <TAG>:best:<sha>:C2 --tag <TAG>last:last:<sha>:C2 --ntrain 160000 --ref-raw raw_<TAG> --fits-dir results/gmm_fits_D2_<TAG> --grid "full:16,32,64,128,256,512 kron:16,…,<최종 K>"`. 어긋나면 그 실행 무효 → 원인 기록, 새 태그 재실행 |
| **측정 판정 (UMi28, 태그 U28B16e4)** | `08_SPEC` §2 표 B `M-ours-bstar → M-ours-dscore-C-V1`, 판정점 = 앵커 b\* 의 BLER@16 이 [0.005, 0.9] 안에서 \|log10(BLER/0.1)\| 최소 3 SNR(자동), 점마다 exact 양측 부호검정. **`power guard … -> POWERED` 이고 `second arm fewer failures at k/3 points` 의 k ≥ 2 → (i); `first arm fewer failures at k/3` 의 k ≥ 2 → (ii)**; `significant` 토큰은 판정 기준이 아니다. 대조군 `M-ours-bstar → M-ours-bstar-scalar` 도 같은 형식으로 보고. MIX3 (MXB16e4) 는 같은 문자열을 **보고 전용** 으로 찍는다 |
| **기전 판독 (목적 질문의 규칙; `_best` 로 계산, last 도 나란히)** | 회수율 R = (b\*−V1)/(b\*−genie) 를 실패 수로 −3 dB(1차) 와 판정점 3 점 합(2차) 에서 계산하고 paired bootstrap 90% CI (B = 2000, `default_rng(20260926)`, 5/95 백분위; `recovery_ci.py`). **R < 0 (V1 이 b\* 보다 많이 실패) 은 그대로 보고한다**(정의역 제한 없음; 분모 b\*−genie ≤ 0 인 복제는 "undefined" 로 셈). D2 와의 비교는 **비짝 차이 CI** ΔR = R(UMi28) − R(D2 B16e4k) (두 raw 를 독립 복원추출, 같은 B·시드; `frontier_ci.py --recovery`) 로 세 갈래: CI < 0 → "38.901 에서 회수율이 D2 보다 낮다"; CI > 0 → "높다"; 0 을 걸침 → "판정하지 못함". **포화 가드(1차)**: −3 dB 에서 앵커 b\* 의 BLER@16 이 [0.005, 0.9] 밖이거나 b\* 실패 수 ≤ genie 실패 수이면 1차 ΔR 은 "판정하지 못함(범위 밖)" 으로 고정하고 2차(판정점 합 = 운영점을 맞춘 비교)만 보고한다. **정의 불가 규칙**: undefined 복제가 5% 를 넘거나 점추정이 정의되지 않으면 "판정하지 못함(정의 불가)". **ΔR 라벨은 1차에서만**, 2차는 보고만(엇갈려도 조정하지 않음). 대안 b\* 를 BLER 로 평가하지 않는다. 동등성은 주장하지 않는다. 이 문장은 prior 축 측정이며 arm 주장이 아니다 |
| 보고 전용 | MIX3 의 표 B·R·ΔR(같은 형식); V0·V4·V4b, F3 가드 발동률(전 arm); best 대 last V1 짝 부호검정(C2); 동일예산 GB′ (격자 확정 뒤 재계산본; D3 0.559·SV8e 0.918 과 나란히); 격자 표(재시작별 ll_val·n_iter·it_best·재시드·구현 경로); LoS/NLoS 조건부 BLER 은 **계산하지 않는다**(raw 에 LoS 플래그가 없다; 사후 분할 금지); SNR@0.1 격차(격자 밖이면 "n/a" 그대로). **다중성**: 이 문서의 라벨 검정은 UMi28 표 B 하나 + ΔR 1차 하나뿐이다; 이번 배치(Pareto·D3·SV8e·38.901 UMi28)의 등록 1차 검정 수는 원고에서 밝히고, 등록 사이의 보정은 하지 않는다(서로 다른 가설). 추세 검정 없음; 결과를 보고 셀·SNR·시나리오를 더하려면 별도 등록 |
| 비용·일정 [추정] | GPU: 학습 ≈ 20.1–21.4 s/epoch(§4 실측) × patience 정지 시점(D3 514, SV8e 260 epoch) → 1.5–3 h/prior (MIX3 09:37 CDT, UMi28 10:07 CDT 시작); GMM 격자 UMi28 21 작업(MIX3 격자 뒤; D3 실측 em_sec: kron 4096 3378 s, kron 2048 2776 s, full 512 2467 s) ≈ 1.5–2 h 벽시계(GPU 4–5 장). CPU: BLER 태그당 C2 7 SNR ≈ 35 분(D2 K=4096 실측 34.4 분; b\* K 가 작으면 덜) + 채널 생성 부담(§4) → 4 태그 ≈ 2.5 h |

## 2. 라벨 (여기서 고정; "측정" 이지 arm 판정이 아니다. UNDECIDED / 비유의는 "판정하지 못함" 이며 어느 쪽의 증거도 아니다)

### 2.1 UMi28 표 B `b* → V1` (C2, U28B16e4)

| 결과 | 기록 |
|---|---|
| (i) POWERED 이고 second arm fewer ≥ 2/3 | "38.901 UMi 28 GHz 에서 V1 이 b\* 보다 적게 실패 (prior·기전 축 측정, UNGATED; **§3 예측 빗나감**)" — §1 회수율·ΔR 문장과 함께 |
| (ii) POWERED 이고 first arm fewer ≥ 2/3 | "38.901 UMi 28 GHz 에서 b\* 가 V1 보다 적게 실패" — 회수율(음수 포함)·ΔR 과 함께 |
| (iii) POWERED 이고 어느 쪽도 ≥ 2/3 아님 | "판정하지 못함 (유의 방향 없음)" — 검정력은 있으나 방향이 없다; 동등성의 증거가 아니다 |
| (iv) UNDECIDED (판정점 < 3 이거나 불일치 쌍 ≥ 6 인 판정점이 2 개 미만) | "판정하지 못함 (검정력 미달)"; SNR 격자를 결과 뒤 늘리지 않는다 |
| 학습 실패 (§3d 시행 3 까지) | BLER 미실행, "학습 실패" |

- (ii)(iii)(iv) 어디에서도 "비긴다"·"동등" 문구를 만들지 않는다. 어느 결과도 헤드라인·C2 판정·D2 기록을 바꾸지 않는다. 문장 범위(§6f): 38.901 UMi28 결과로 셀·prior 한정 없는 주장을 쓰지 않는다.

### 2.2 MIX3 (MXB16e4, 보고 전용)

같은 (i)~(iv) 문자열을 "38.901 MIX3(UMi28+UMa28+RMa3.5) 부속 점" 으로 찍는다. **§2.1 판정·§2.3 공동 판독·§3 채점에 쓰지 않는다**(MIX3 방향은 §3 의 보조 예측 10 으로만 채점). UMi28 과 MIX3 가 다른 방향이면 그대로 두 줄로 보고한다(설명은 사용자). **MIX3 결과가 UMi28 과 다르더라도 판정·공동 판독·§3 채점에 쓰지 않으며, 두 prior 의 역할(주/부속)을 결과 뒤에 바꾸지 않는다 — 바꾸려면 새 등록.**

### 2.3 경계 양쪽 공동 판독표 (SV8e 표 B × UMi28 표 B; 두 등록이 모두 §6 을 채운 뒤 한 번만 적용)

§3 예측 채점 규칙(UMi28): (ii) 또는 (iii) = **"우위 없음 예측 적중(약)"** ((iii) 은 검정력 있는 무방향이지 동등성이 아니다); (iv) = "판정하지 못함(채점 불가)"; (i) = **"예측 빗나감(38.901 에서도 V1 우위)"**. 표 B 채점과 §3 예측 2(R·ΔR)의 채점은 따로 적고 합산하지 않는다.

| SV8e (`NEXT_EXPERIMENTS_SVB16e4.md` §2, 예측 = V1 우위) | UMi28 ∈ {(ii), (iii)} | UMi28 = (i) | 어느 쪽이든 (iv) 또는 학습 실패 |
|---|---|---|---|
| **SV8e = (i)** | **"경계 양쪽 예측 모두 적중"** — 채널 통계로 미리 그은 경계(독립 연속 잠재 각도의 수)의 양쪽에서 예측 방향대로 | "기전 경계 예측 빗나감: 양쪽 모두 우위" — 경계 가설은 이 자료로 지지되지 않음(우위의 원인은 다른 것) | "판정하지 못함" |
| **SV8e ∉ (i)** ((ii) 또는 (iii)) | "한쪽만(38.901) 적중; 기전 가설은 지지되지 않음" — SV 쪽 예측 빗나감 | "양쪽 모두 빗나감(방향 반대)" | "판정하지 못함" |
| **SV8e = (iv)** | "판정하지 못함" | "판정하지 못함" | "판정하지 못함" |

- 어떤 칸도 헤드라인(C2 D2)·D2 판정을 바꾸지 않는다. 두 표 B 는 서로 다른 가설(각각 방향 예측 하나)이므로 다중성 보정은 하지 않고, 두 결과를 합쳐 하나의 p 로 만들지 않는다. 공동 문장은 셀 C2·두 prior 한정이다.

## 3. 미리 적는 예측 (빗나가면 그대로 쓴다; 0단계 채널 통계를 본 뒤의 약한 예측이며, 1.6e5 BLER 은 본 적이 없다)

1. **표 B (UMi28): (ii) 또는 (iii)** — 학습 prior 우위 없음. 확신 중간(0단계 closed 0.68 vs D2 0.26 에 기댐).
2. **회수율 R(−3 dB) ≤ 0.2** (음수 가능; 90% CI 상한 < 0.47). ΔR = R(UMi28) − R(D2) 의 90% CI < 0 ("D2 보다 낮다").
3. `R2-ours-G → b*`: b\* 우세(first arm fewer ≥ 2/3) — GMM 이 Gaussian 을 이기는 폭은 D2 보다 작을 수 있다(0단계 GMM−Gaussian NMSE 폭이 작음).
4. genie 격차: −3 dB 에서 b\*−genie 실패 수 차이가 D2 의 536 (623−87) 보다 작다; genie(−3 dB) BLER ≤ 0.05 (D2 0.034; LoS 40 %).
5. **GB′ 비(확산/GMM b\*, held-out 디노이징 NMSE, σ 격자 20 점) median ≥ 0.9** (D3 0.559, SV8e 0.918); worst excess 는 −0.1 이상.
6. 학습: 발산 없음, patience 정지, **epoch 200–600** (D3 514, SV8e 260), best val < 0.5 [10:21 CDT 관측 뒤 쓴 값: UMi28 epoch 27 에서 0.562, MIX3 epoch 118 에서 0.485 — 학습 곡선이지 판정량이 아니다].
7. GMM: b\* 계열은 예측하지 않는다. full 계열이 이길 가능성을 열어 둔다(SV8e 선례 full 256; 38.901 은 소수 잠재 변수 → full 이 유리할 수 있음). kron 이면 격자 끝(4096)까지 갈 가능성이 있다(D3 선례).
8. V0: 가드 발동(−3~+3 dB BLER ≥ 0.9). V4·V4b 는 V1 과 비슷하거나 나쁨. best 대 last V1: 판정하지 못함(pooled p > 0.05).
9. 대조군 `b* → b*-scalar`: b\* 우세(first arm fewer ≥ 2/3).
10. **MIX3 는 UMi28 과 같은 방향**((ii)/(iii) 이고 R(−3) ≤ 0.2); MIX3 의 b\*·genie BLER 은 UMi28 보다 높다(RMa·UMa NLoS 비중, 블록 전력 CV 0.41 vs 0.29).
11. 빗나갈 경로: (a) **(i) 가 나오면 §2.3 의 "빗나감" 칸으로 가고 기전 가설(잠재 차원) 은 수정이 필요하다 — 그대로 기록, 사후 설명은 사용자**; (b) R 이 크게 음수(V1 이 b\* 보다 훨씬 나쁨) → 그대로 기록, 레시피 탐색 없음; (c) (iv) → 그대로 기록, 격자 확장 없음; (d) 발산 → §3d; (e) full 512 격자 끝 → full 1024 한 번 적합 후 멈춤 + 캐비엇(§1); (f) 두 prior 가 서로 다른 방향 → 두 줄로 보고.

## 4. 선행 작업과 실행 현황 (갱신한다; 시각은 `date` 로 읽음)

| 항목 | 상태 · 담당 |
|---|---|
| UMi28 연결(`mix3.py` NSCEN, PID 8, 보정 상수, `testbed_mix3.py [prior]`, σ 격자, `selftest_mix3.py` 968 배열 IDENTICAL vs 0a3bb946) | **완료·커밋 67a5523b** (09-26 10:07 CDT 무렵; DECISIONS 00:07 KST). MIX3 연결은 598b6de6 (09:37 CDT), 독립 검토 PASS + 문서 수정 22c45e53 |
| 학습 UMi28 (`@train UMi28 U28B16e4`, tmux `tb2` 창 `gpu5`, GPU 5) | 진행 중: 큐 시작 10:07 CDT, 학습 루프 머리말 09-27 00:11:44 KST (= 10:11 CDT), split_hash 98cc168731eb922c, E‖H‖² 1.000000, σ 격자 [3.2681e-02, 8.3725e-01]; **10:21 CDT 기준 epoch 27, 20.3–21.4 s/epoch, best val 5.618699e-01 @27** (`logs/train_d2sx_UMi28_N160000_a1.log`, 프로세스 RSS 1.77 GB) |
| 학습 MIX3 (`@train MIX3 MXB16e4`, tmux `tb2`, GPU 0) | 진행 중: 09:37 CDT 시작, 머리말 09-26 23:40:36 KST (= 09:40 CDT), split_hash 16f67ba3d3f59660, σ 격자 [3.2620e-02, 8.5004e-01]; **10:21 CDT 기준 epoch 118, best val 4.845191e-01 @118** (RSS 1.77 GB) |
| GMM 격자 MIX3 (`logs/tb2_queue.txt`, GPU 1–4) | 10:21 CDT: full 16..512 6 개 완료, kron 16..512 완료, kron 1024 후보 3 개 완료(`gmm_fits_D2_MXB16e4/`), **kron 2048 r0/r1/r2 실행 중**(GPU 1/4/2, 10:15/10:17/10:19 시작), kron 4096 r0 실행 중(GPU 3, 10:20); 큐에 kron 4096 r1·r2 대기 |
| GMM 격자 UMi28 (21 작업, MIX3 격자 뒤) | 큐 대기(10:21 CDT 큐 23 줄 = MIX3 2 + UMi28 21) → `results/gmm_fits_D2_U28B16e4/` (아직 없음) |
| 병합·격자 끝 규칙·GB′ (prior 마다; 수동, C6·D3 관례) | 대기: kron 1024·2048 병합 → b\* 선택 → 격자 끝이면 4096 병합 → 멈춤 → GB′ 재개 실행 → §5 |
| 선행 코드: `run_prior_eval.sh`(범용), `frontier_ci.py --recovery`(비짝 ΔR CI), `eval_accept.py` 의 `--kron-K` 선택화(full b\*)·`--ref-cells`, fits 링크 `gmm_fits_D2_{U28B16e4,MXB16e4}last` | **완료** db038a10 (`run_prior_eval.sh`, `frontier_ci.py`, `eval_accept.py` 인자), 33719007 (판정점 자동 읽기), 2f6b6497 (`--ref-arms all`); `…last` 링크는 fits 디렉터리가 생긴 뒤 §5 시점에 만든다(스크립트는 링크가 없으면 ABORT) |
| BLER 실행 메모리 [추정] | 서버 RAM 총 1007 GB, 사용 20 GB, 가용 986 GB (10:21 CDT `free -g`). `runner.py run` 은 `mp.Pool` 기본 컨텍스트(**fork**; `set_start_method` 없음) 192 워커이고 워커마다 `build_point` → `make_gen` → 첫 `sample()` 에서 **Sionna + torch 를 워커 프로세스 안에서 import** 한다(`mix3._sionna` 는 CUDA 를 가리고 CPU 로만 import). **실측(검토 B, CPU ru_maxrss)**: torch import 0.52 GB → + sionna 0.85 GB → 첫 sample 뒤 0.87 GB, 9.3 ms/sample → 상한 192 × 0.87 ≈ 167 GB (가용 986 GB 안; fork 의 COW 로 실제는 더 적을 수 있음). 청크 (skip, 40) 는 시행 0..skip+39 를 다시 생성하므로(`runner.py:454-460`) 점당 Σ(skip+40) ≈ 83,200 회 `sample()` ≈ 12.9 CPU-분(192 워커에 분산; 태그당 7 점 → 수 분 벽시계 [추정]); D2 대비 추가 비용은 이것뿐. 첫 태그 실행 초반에 `free -g` 와 워커 RSS 를 실측해 §6 에 적는다 |
| §5 채우기 → 커밋 → 실행 ①~⑤ → §6 | 대기(격자·학습 완료 뒤) |

## 5. 평가 전 고정 기록 (실행 전에 채우고 커밋한다; 갱신 시각을 적는다)

| 항목 | UMi28 (U28B16e4) | MIX3 (MXB16e4) |
|---|---|---|
| PID · rung · σ 격자 태그 | 8 · D2SXUMi28160000 (ix 1665) · `UMi28` [3.268110e-02, 8.372515e-01] (20 점, @0a3bb946) | 7 · D2SXMIX3160000 (ix 1276) · `MIX3` [3.262043e-02, 8.500441e-01] (@598b6de6) |
| 보정 상수(학습 스트림 7, n=160000) | P_RAW 0.9901769449816289, TRAIN_SHA a2f617f3111ea64e (212 s) | P_RAW 0.9953569092328413, TRAIN_SHA 9f595676e0d1a032 (170 s) |
| testbed 검증 | ALL PASS @0a3bb946 (§0 표) | ALL PASS @598b6de6 (§0 표) |
| 파일럿 | eigen 정렬 (erank Rt 3.494) | eigen 정렬 (3.483) |
| 격자: K 별(계열별) ll_val · n_iter · it_best(상한 500 정지) · 재시드 · 구현 경로 · 수렴 규칙, 병합 ll_val · 마지막 병합 파일 mtime | **full** (정확 경로, κ 격자 × 재시작 3, 전부 κ=0 선택): 16 −18.613 (r1, 143/140) / 32 −12.029 (r1, 364/340) / 64 −7.205 (r1, 248/240) / 128 −3.506 (r0, 431/390) / 256 −1.700 (r0, **500/490 상한 정지**) / 512 −1.331 (r1, 136/110, 재시드 2,243). **kron** (일괄 경로, κ=0, 재시작 3): 16 −18.353 / 32 −11.024 / 64 −6.355 / 128 −1.999 / 256 1.308 / 512 3.622 / **1024 4.943874136038161** (r2, 246/210, rs 236; r0 4.936 214/210 rs 214, r1 4.891 208/200 rs 106) / **2048 5.539276756851168** (r2, 217/210, rs 16,650; r0 5.465 157/150 rs 11,609, r1 5.529 166/150 rs 11,683) / **4096 5.797910431000217** (r0, 88/80, rs 71,589; r1 5.759 81/80 rs 68,522, r2 5.435 59/50 rs 48,754). 병합 파일 합 em_sec 9133.6 s. 마지막 병합(kron 4096) mtime 09-27 03:12 KST = 13:12 CDT. kron 4096 후보의 정지 사유(npz 필드 없음, n_iter/it_best 에서 추론): r0 88/80·r1 81/80·r2 59/50 모두 patience(40)·상한(500) 미만 → 학습 우도 tol 규칙 정지(재시드 다수) | **full**: 16 4.577 (r2, 183/180) / 32 11.943 (r0, 141/100) / 64 17.777 (r0, 366/360) / 128 21.634 (r1, 321/280) / 256 23.513 (r2, 302/270, rs 297) / 512 23.930 (r1, 137/130, rs 5,030). **kron**: 16 5.441 / 32 13.486 / 64 19.875 / 128 24.244 / 256 27.639 / 512 30.535 / **1024 32.32734842265888** (r0, 93/90, rs 1,265; r1 32.049, r2 32.275) / **2048 33.291262657749414** (r0, 73/70, rs 15,371; r1 33.003, r2 33.074) / **4096 33.7604873920761** (r2, 67/60, rs 86,904; r0 33.621 69/50 rs 88,612, r1 33.678 66/60 rs 84,380). 병합 파일 합 em_sec 6242.1 s. 마지막 병합 mtime 09-27 01:21 KST = 11:21 CDT. kron 4096 후보 모두 tol 규칙 정지(추론) |
| 확장 결정(kron 2048 / 4096 병합)과 시각 | 12:35 CDT kron 1024·2048 병합 → 13:04 b\* = kron 2048 (5.5393, 기본 격자 끝) → 규칙대로 kron 4096 병합 → 13:12 b\* = kron 4096 → **4096 에서 멈춤**(결정 (3)); full 계열 끝 규칙은 발동하지 않음(b\* 가 kron; full 512 −1.331 < kron 4096) (`logs/tb2_post_UMi28.log`) | 10:45 CDT 병합 → b\* = kron 2048 (33.2913, 기본 격자 끝) → 11:08 kron 4096 병합 → 11:21 b\* = kron 4096 → 멈춤 (`logs/tb2_post_MIX3.log`; DECISIONS 2b03df55) |
| 최종 b\*: 계열·K·ll_val(정확한 float), 내부 여부 / 격자 끝 캐비엇 / 미병합 후보 | **b\* = kron K=4096, ll_val 5.797910431000217** (재시작 0). **격자 끝**(2048 대비 +0.259 nat, 오르는 중) + **수렴 캐비엇**(tol 정지, 재시드 7.2만; 덜 수렴된 GMM 일 수 있고 방향은 V1 유리). 미병합 후보 없음. 수용 검사 `--bstar kron --kron-K 4096 --ll-val 5.797910431000217` | **b\* = kron K=4096, ll_val 33.7604873920761** (재시작 2). 격자 끝(+0.469 nat) + 수렴 캐비엇(재시드 8.7만). `--kron-K 4096 --ll-val 33.7604873920761` |
| 체크포인트: last / best 의 sha256[:16]·epoch·best_epoch·stopped_by·aborted; best.epoch == last.best_epoch; 학습 시각·초 | best `ckpt/d2sx_UMi28_N160000_a1_best.pt` **6f3a1b9490864af1** (epoch 379, role best, best val 0.5533451437950134); last `…_a1.pt` **1fc8c7766507b823** (epoch 399, best_epoch 379 = best.epoch ✓, stopped_by patience, aborted 필드 None(로그 done 줄 aborted=False), role last, grad_clip 0.0); prior UMi28, sigma_tag UMi28, rung D2SXUMi28160000, attempt 1. 학습 10:11~12:18 CDT, 7,828.4 s, 19.62 s/epoch; split_hash 98cc168731eb922c | best **b591ae24ae3c5f31** (epoch 464, best val 0.4814744293689728); last **10c3fb112c685d1b** (epoch 484, best_epoch 464 ✓, patience, aborted None, grad_clip 0.0); prior·sigma_tag MIX3, rung D2SXMIX3160000. 학습 09:40~12:19 CDT, 9,672.3 s, 19.98 s/epoch; split_hash 16f67ba3d3f59660 |
| §3d 사다리 적용 여부 | 미발동(시행 1 patience; `logs/tb2_train_state_UMi28.txt` = `1 patience`) | 미발동(`1 patience`) |
| GB′ (격자 확정 뒤 재개본; 기준 b\*, 비 min/max/median, worst excess, npz 경로) | [채워질 것 — 13:30 CDT GPU 1 에서 재개 실행 중] | 12:36 CDT GPU 0 재개 실행(학습 없음, last 파일) → 14:15 CDT rc=0: `GMM b* = kron (kron K=4096)` = §5 최종 b\* ✓, 확산/GMM 디노이징 NMSE 비 **min 0.8795 · max 0.9410 · median 0.8941**, worst excess **−0.0590** (σ 격자 MIX3 20 점 전부에서 확산이 낮음); `results/d2_gbprime_MIX3.csv`, `d2_gbprime_MIX3_N160000_a1.npz` (mtime 14:15 CDT, 격자 확정 11:21 CDT 뒤 → 수용 (e) 충족; `logs/gbprime_MXB16e4.log`) |
| 선행 코드 커밋 해시, fits 링크 생성 시각, 평가 스크립트 인자 원문(9 인자) | 코드 db038a10·33719007·2f6b6497 + 동결 eee1d669; 링크 `gmm_fits_D2_U28B16e4last` 09-26 13:32 CDT; 인자 [채워질 것 — GB′ 뒤] | 코드 동일; 링크 `gmm_fits_D2_MXB16e4last` 09-26 13:32 CDT; 인자 `code/run_prior_eval.sh MIX3 MXB16e4 d2sx_MIX3_N160000_a1 kron 4096 33.7604873920761 b591ae24ae3c5f31 10c3fb112c685d1b "full:16,32,64,128,256,512 kron:16,32,64,128,256,512,1024,2048,4096"` |

## 6. 결과 (이 절은 추가만 한다)

(비어 있음 — 실행 뒤 §6.1 측정 판정(UMi28) · §6.2 보고 전용(MIX3 포함) · §6.3 §3 예측 채점 · §6.4 공동 판독(§2.3; SV8e §6 이 채워진 뒤) · §6.5 기록 감사 순으로 채운다.)
