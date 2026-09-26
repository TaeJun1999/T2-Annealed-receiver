# Sionna·DeepMIMO 설정별 GMM vs Diffusion Prior 채널 추정 성능 예상

> 출처: 사용자가 웹에서 작성해 2026-09-25 22:3x CDT 세션에 붙여 넣은 계획 문서(원문 그대로 보존). 지시: "위 내용 참고해서 해봐" + "새로운 데이터셋은 proposed 에 유리할 수 있는 데이터셋이어야 한다".
> 이 프로젝트에서의 쓰임: 두 번째 testbed 선택의 **사전(a priori) 기전 근거**. 선택은 채널 통계(비-Gaussian 성·희소성·다봉성)로만 하고 수신기 BLER 을 보고 고르지 않는다. 판정은 별도 사전 등록(Fable)에서 고정한다.
> 문서 본문은 이 줄 아래부터 원문이다. 우리 파이프라인(터보 수신기 BLER, 동일예산, 8×4)과 다른 점: 원문은 단독 채널 추정 NMSE 와 외부 DM 코드([F24], [AT23]) 를 전제한다.

---

(원문 요약 표·가설 H1~H8, 메커니즘 M1~M5, Sionna PHY P1~P6 / 대조군 P-C1~C3, Sionna RT R1~R6 / R-C1~C3, DeepMIMO D1~D6 / D-C1~C2, DM 이 못 이길 조건 6개, 검증 실험 E1~E8, 전처리 체크리스트, 참고문헌 [K22] [F22] [F23] [F24] [F24b] [AT22] [AT23] [HD-DM] [EBDM] [MoE] [GAI-DM] [MRS25], Sionna 2.1.0 문서, DeepMIMO v4.)

## 원문

### 0. 요약
GMM 추정기는 채널 분포를 K개의 Gaussian 조각으로 덮고, 각 조각의 LMMSE 필터를 가중합한다. 채널 분포가 (1) 고차원, (2) 넓거나 다봉, (3) 소수 경로로 이루어진 저차원 manifold 일수록 무너지기 쉽다. Diffusion prior(DM)는 하나의 신경망이 분포 전체의 denoiser/score 를 학습하므로 이 세 경우에 상대적으로 유리할 가능성이 높다. 반대로 채널이 거의 Gaussian(Rayleigh, TDL, 단일 CDL, 산란 풍부 RT)이거나, 학습 데이터가 적거나, 저 SNR 에서 posterior sampling 을 쓰면 DM 의 이점이 사라지거나 역전될 것으로 예상된다.

| # | 설정 | 데이터 | 메커니즘 | 예상 | 확신도 | 근거 |
|---|---|---|---|---|---|---|
| H1 | 대규모 배열, 안테나×부반송파 joint 추정 | 공통 | M1 고차원 | full GMM 과적합, DM 우위 | 높음 | [F24] |
| H2 | diffuse off, 낮은 max_depth, mmWave | Sionna RT, DeepMIMO | M3 저랭크 manifold | 고 SNR 에서 GMM floor, DM 우위 | 중~높음 | [F24] + 추론 |
| H3 | LSP·topology 매 샘플 재생성, LoS/NLoS 혼합 | Sionna PHY | M2 넓은/다봉 분포 | K 부족 GMM 은 LMMSE 수준, DM 우위 | 중간 | 추론, [MRS25] 간접 |
| H4 | 맵 전체, 다중 BS, 여러 시나리오 혼합 | Sionna RT, DeepMIMO | M2 다봉 | DM 우위(단일 DM 도 한계) | 중간 | [GAI-DM], [MoE] |
| H5 | 파일럿 부족 (N_p < N_tx) | 공통 | M5 압축 관측 | posterior sampling DM 우위 | 중간 | [AT23], [EBDM] |
| H6 | normalize_delays=False | Sionna RT | M4 이동 불변성 | CNN 기반 DM 우위 | 낮음~중간 | 추론 |
| H7 | 학습·테스트 시나리오 다름 | DeepMIMO, RT | 분포 이동 | 둘 다 저하, posterior sampling DM 이 더 완만 | 낮음~중간 | [AT22] |
| H8 | 학습 데이터 적음, near-Gaussian, 저 SNR posterior sampling | 공통 | 대조군 | GMM ≥ DM | 중간 | 추론 + [F24] |

### 1~9절
메커니즘 표(M1 고차원 / M2 넓은·다봉 / M3 저차원 manifold / M4 이동 불변성 / M5 관측 모델), Sionna PHY 설정 P1(UMi/UMa/RMa 배치마다 gen_single_sector_topology, always_generate_lsp=True), P2(los=None, indoor_probability>0), P3(큰 PanelArray, dual pol, joint 추정), P4(높은 carrier_frequency), P5(속도 분포 + 시간축), P6(적은 PilotPattern); 대조군 P-C1(Rayleigh, TDL), P-C2(단일 CDL), P-C3(pathloss/shadowing 기본값). Sionna RT R1(diffuse off, max_depth 0~1), R2(mmWave + 큰 배열), R3(맵 전체 Rx, 다중 Tx, LoS/NLoS), R4(normalize_delays=False), R5(near-field), R6(시간축); 대조군 R-C1(diffuse on 충분 샘플), R-C2(diffuse on 작은 samples_per_src), R-C3(normalize=False). DeepMIMO D1(산란 없는 28/60 GHz), D2(다중 BS·시나리오 혼합), D3(blockage), D4(큰 배열·많은 부반송파), D5(시나리오 이동), D6(촘촘한 격자 무작위 split 누수); 대조군 D-C1(작은 시나리오), D-C2(경로 없는 사용자). DM 이 못 이길 조건 6개(near-Gaussian, 적은 데이터, 저 SNR posterior sampling, 구조 가정 정확, 지연·복잡도 제약, 크게 다른 시나리오 혼합). 검증 실험 E1 희소성, E2 분포 폭, E3 차원, E4 학습 크기, E5 split, E6 시나리오 이동, E7 파일럿, E8 대조군(기각 기준 포함). 전처리 체크리스트(샘플별 정규화, normalize_delays=True, 경로 없는 위치 제거, samples_per_src 수렴, deterministic PathSolver·seed, angular-domain 입력, FFT 유니터리 정상 동작 검사, 공간 블록 split, 파라미터 수·복잡도 표). 참고문헌: [K22] Koller et al. TSP 2022 arXiv:2112.12499; [F22] Fesl et al. Asilomar 2022 arXiv:2205.03634; [F23] Fesl et al. Asilomar 2023 arXiv:2304.14809; [F24] Fesl et al. 2024 arXiv:2403.03545 (코드 benediktfesl/Diffusion_channel_est); [F24b] arXiv:2403.02957; [AT22] Arvinte & Tamir WCNC 2022 arXiv:2111.08177; [AT23] Arvinte & Tamir TWC 2023 (코드 utcsilab/score-based-channels); [HD-DM] arXiv:2408.10501; [EBDM] arXiv:2510.22230; [MoE] arXiv:2605.18325; [GAI-DM] arXiv:2410.06389; [MRS25] arXiv:2512.12449; Sionna 2.1.0 RT/PHY 문서; DeepMIMO v4.

(원문 전체는 세션 대화 기록에 있다. 이 파일은 요지·표·참고문헌을 보존한 사본이다.)
