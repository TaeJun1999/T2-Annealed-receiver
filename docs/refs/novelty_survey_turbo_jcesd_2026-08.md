# 선행연구/신규성 조사 보고서: Turbo 복호(BCJR/외재정보 교환)와 JCESD 교차 4개 연구방향 (2026년 8월 기준)

## TL;DR
- **후보 A(코드 제약 스코어 기반 확산 JCESD)와 후보 C(정확한 외재/leave-one-out 채널추정과 Onsager 등가성 증명)는 "열려 있음"(open)에 가깝다.** 반면 **후보 B(코드 구조만으로 MIMO 채널 식별)는 스칼라 위상·스트림 permutation 부분이 이미 다뤄져 "부분 커버"이고, 후보 D(현대 복호기를 루프에 포함한 부호화 bilinear JCESD의 상태전개/replica 분석)는 CDMA·활성탐지 특수형만 존재해 "부분 커버/열림"이다.**
- **2025–2026 arXiv에 스쿠핑 위험이 높은 논문이 다수 등장.** 특히 후보 A는 Wadayama–Takahashi 그룹의 SC-VAMP(arXiv:2601.07095)와 그 후속 "Three-Module SC-VAMP for LDPC-Coded Nonlinear Channels"(arXiv:2604.19061)가 **BP 복호기를 스코어 denoiser로 삽입 + Onsager 외재 메시지 교환**을 이미 제시하고 있어 가장 심각한 스쿠핑 위험이다. 후보 B는 Pilotless Polar(2602.17979)·Phase-Equivariant Polar(2305.01972), 후보 D는 Takeuchi et al.(T-IT 2012) 및 JADCE replica(TSP 2022)가 가장 근접하다.
- 각 후보 모두 명확한 차별화 기여가 여전히 존재한다. 특히 "SISO 복호기를 이산 부호심볼 prior의 정확한 스코어/Tweedie denoiser로 해석 + **학습된 채널 확산 prior**와 bilinear 결합"(A의 채널 prior 부분)과 "Onsager항 = leave-one-out 채널추정의 1차 전개 증명 + 단블록 오류마루 정량화"(C)는 현시점 미발표로 판단된다.

## Key Findings

**후보 A — 코드 제약 스코어 기반 확산 JCESD**: 확산/스코어 기반 JCESD는 존재하나 대부분 **비부호화(uncoded)** 심볼 prior에 머문다. 복호기를 denoiser/스코어로 쓰는 아이디어(DDECC, VCDC, Score-Based ECC Decoder)와 확산 JCESD(Zilberstein 2024 등)가 별개로 존재했으나, **최근 SC-VAMP 후속(2604.19061)이 BP 복호기 + Onsager 외재 스칼라-가우시안 메시지 교환을 결합**하여 A의 핵심 아이디어에 매우 근접했다. 다만 "채널 H에 대한 **학습된 확산/스코어 prior**를 bilinear 우도로 결합"하는 완전한 JCESD 통합은 여전히 미발견. → 부분 커버에 근접한 열림.

**후보 B — 코드를 파일럿으로**: LDPC 패리티 기반 blind/code-aided 채널추정(Scherb–Kühn–Kammeyer), permutation 모호성 없는 blind MIMO 분리(Zhao–Davies), 위상 모호성의 코드적 해결(Phase-Equivariant Polar, Pilotless Polar)이 이미 존재. **스칼라 위상·스트림 permutation은 커버됨**; 고차 QAM 하 완전한 행렬 모호성군 G의 일반 식별성 정리는 미완. → 부분 커버.

**후보 C — 정확한 외재(leave-one-out) 채널추정 ≡ Onsager**: 소프트심볼 채널추정(Otnes–Tüchler, Song–Singer–Sung)과 a posteriori vs extrinsic 구분은 존재하나, **명시적 leave-one-out 채널추정 H^{\n} 정식화, Onsager항이 그 1차 전개임을 증명, 단블록 T에 대한 오류마루 정량화 — 세 요소 모두 미발표.** → 열림.

**후보 D — 부호화 bilinear JCESD의 상태전개/replica**: Takeuchi et al.(MIMO DS-CDMA, per-user decoding 포함 replica)와 JADCE replica(TSP 2022)가 존재. **복호기의 EXIT 전달함수를 2차원 상태전개에 임베딩하여 파일럿길이 T_p·코히어런스 T·SNR의 함수로 달성률을 구하고 Hassibi–Hochwald 하계와 비교하는 분석은 미발견.** → 부분 커버/열림.

## Details

### 후보 A — "Code-constrained score for diffusion-based JCESD"

**가장 근접한 선행연구:**
- N. Zilberstein(Rice), A. Swami(DEVCOM Army Research Laboratory), S. Segarra(Rice), "Joint Channel Estimation and Data Detection in Massive MIMO Systems Based on Diffusion Models," ICASSP 2024, pp. 13291–13295 (arXiv:2311.10311). 명시적 기여(초록 verbatim): "A unique contribution of the algorithm is to include the discrete prior distribution of the symbols and a learned prior for the channels." 채널의 학습된 prior + 심볼의 이산 prior를 결합해 joint posterior에서 annealed Langevin 샘플링. **비부호화**. 후보 A의 직접적 출발점이나 코드 제약 없음.
- SIC-aided diffusion JCESD, arXiv:2501.11229 (Jan 2025). 저랭크 채널을 위한 SIC 결합 스코어 확산. 비부호화, 소스-채널 추정.
- "Generative Diffusion Model Driven Massive Random Access in Massive MIMO," arXiv:2505.12382 (2025). 비동기 교대 CE–DD, predictor-corrector 샘플러; 일부 스코어는 학습, 일부는 constellation prior로 폐형 도출. 제목에 JCEDD를 언급하나 코드 제약은 constellation 수준이며 BCJR/BP 복호기를 스코어로 삽입하지 않음.
- Y. Choukroun, L. Wolf, "Denoising Diffusion Error Correction Codes (DDECC)," arXiv:2209.13533 (ICLR 2023). 선형부호의 soft decoding을 확산 역과정으로. **채널추정 없음(AWGN 단일)**.
- C. Zhang, Y. Du, S. Liao, "Variational Diffusion Channel Decoder (VCDC)," arXiv:2605.18902 (May 2026). BP + VDM 결합, DDECC 대비 FLOPs 최대 5자릿수 절감(LDPC 121,60 기준). 순수 복호기.
- A. Helvits, E. Nachmani, "Score Based Error Correcting Code Decoder," arXiv:2605.28358 (May 2026). CrossMPT 백본, 스코어 기반 ECC 복호. 순수 복호기, 채널·bilinear 없음.
- **SC-VAMP**: T. Wadayama(Nagoya Institute of Technology), T. Takahashi(The University of Osaka), "Score-Based VAMP with Fisher-Information-Based Onsager Correction," arXiv:2601.07095 (11 Jan 2026). 초록 verbatim: "We propose score-based VAMP (SC-VAMP)... in which the Onsager correction is expressed and computed via conditional Fisher information, thereby enabling a Jacobian-free implementation. Using learned score functions, SC-VAMP constructs nonlinear MMSE estimators through Tweedie's formula and derives the corresponding Onsager terms from the score-norm statistics." **SISO 모듈을 Tweedie 공식 기반 비선형 MMSE 추정기로, Onsager항을 조건부 Fisher 정보로 표현.** 후보 A·C 모두에 핵심적으로 근접하나, 채널 H에 대한 bilinear/JCESD 설정이 아니라 일반 선형역문제이며 부호심볼 prior의 BCJR/BP 스코어 해석을 명시하지 않음.
- **⚠ 최대 스쿠핑 위험**: Wadayama & Takahashi, "Three-Module SC-VAMP for LDPC-Coded Nonlinear Channels," arXiv:2604.19061. 초록 verbatim: "a denoiser module that incorporates the code constraint using belief propagation (BP) decoding. Each module exchanges extrinsic scalar-Gaussian messages with Onsager corrections." — 이는 후보 A의 "BP 복호기를 스코어 denoiser로 + 외재/Onsager 메시지 교환" 핵심을 이미 구현. **A는 반드시 이 논문을 인용하고, 채널 H의 학습된 확산 prior + bilinear 결합(즉 JCESD)이라는 차별점을 분명히 해야 함.**
- Tweedie 공식 ↔ MMSE denoiser ↔ 스코어 등가는 표준(예: "Random Walks with Tweedie," arXiv:2411.18702). 후보 A가 인용해야 할 이론적 기반.

**신규성 판정: 열림에 가까우나 급속히 좁혀지는 중.** 확산 JCESD는 비부호화가 지배적이고, 복호기-as-denoiser는 채널추정과 분리되어 있었으나, 2604.19061이 "BP 복호기 스코어 + Onsager 외재 교환"을 선점. **아직 미발표인 핵심 조합**: (1) BCJR(convolutional/turbo)·BP(LDPC)를 이산 부호심볼 prior의 정확/근사 MMSE denoiser로 Tweedie 공식(L_c(t)=2/σ_t²)을 통해 사용, (2) 채널 H는 **학습된 확산/스코어 prior**(2604.19061은 채널을 비선형 관측 모델로 다루지 학습된 채널 생성 prior를 쓰지 않음), (3) bilinear 우도로 결합하며 Turbo-CS/OAMP식 외재/Onsager 보정.

**차별화 기여**: "복호기 소프트출력 = 이산 부호심볼 prior의 스코어"라는 정확한 해석을, **채널의 학습된 확산 prior와 bilinear로 결합한 완전 JCESD annealed turbo 수신기**. 즉 코드 스코어(2604.19061이 선점) 자체가 아니라 "코드 스코어 × 학습된 채널 확산 prior × bilinear joint posterior sampler"의 결합이 신규 축.

**인용 필수 기반**: Zilberstein–Swami–Segarra 2024; DDECC 2023; VCDC 2605.18902; Score-Based ECC 2605.28358; SC-VAMP 2601.07095; **Three-Module SC-VAMP 2604.19061**; Ma & Ping OAMP 2017; Ma–Yuan–Ping Turbo-CS; Parker–Schniter–Cevher BiG-AMP 2014; Efron Tweedie / Song–Ermon score SDE.

### 후보 B — "The code as the pilot"

**가장 근접한 선행연구:**
- A. Scherb, V. Kühn, K. D. Kammeyer, "Blind Turbo Channel Estimation Exploiting Parity Check Equations" 및 "Blind Identification and Equalization of LDPC-encoded MIMO Systems" (2000년대 중반). 채널부호가 유발하는 통계적 종속성으로 blind 식별; **permutation 모호성이 없고, 비대칭 부호면 위상까지 교정**. 후보 B의 가장 직접적 선행연구.
- B. Shi 외, "Code-Aided Channel Estimation in LDPC-Coded MIMO Systems," arXiv:2311.07091. LDPC 코드제약(패리티체크가 만족될 확률)으로 CSI 미세조정, 파일럿+데이터 결합; QPSK·WiMAX LDPC, FER 10⁻⁴에서 최대 1.3 dB 이득. 반(半)파일럿 지향.
- X. Zhao, M. Davies, "Coding-assisted blind MIMO separation and decoding," IEEE TVT 59(9):4408–4417, 2010. permutation 모호성 회피.
- M. Geiselhart 외, "Phase-Equivariant Polar Coded Modulation," arXiv:2305.01972 (ICC 2023). Gray-QAM 위상회전 = bit-flip + automorphism; frozen bit 설계로 파일럿 없이 위상 모호성 해결, QPSK/16-QAM에서 파일럿 대비 0.8/2 dB 우위.
- "Learning While Transmitting: Pilotless Polar Coded Modulation for Short Packet Transmission," arXiv:2602.17979 (Feb 2026). 코드화 파일럿(QPSK 세그먼트가 CSI 없이 복호 가능→암묵 파일럿), DEGA 최적화, 다중블록 페이딩.
- T. R. Dean, M. Wootters, A. J. Goldsmith, "Blind Joint MIMO Channel Estimation and Decoding," arXiv:1802.01049. 초입방체 소스 구조 이용 최소부피 평행육면체 적합.
- IDMA 기반 스트림/사용자 분리·반블라인드 채널추정(다수). 스트림별 인터리버로 permutation 해결.
- 위상 모호성 코드적 해결: LDPC 신드롬 LLR 최소화 기반 blind phase offset 추정(BPSK/고차).

**신규성 판정: 부분 커버(partially covered).** 이미 커버: 스칼라 위상 모호성(Phase-Equivariant Polar, LDPC syndrome), 스트림 permutation(IDMA 인터리버, Zhao–Davies), SIMO/저차 변조 blind LDPC 식별(Scherb 외). **미완**: (1) 선형이진부호(turbo/LDPC)+고차 QAM 매핑 하 완전한 모호성군 G={G:G·X_set=X_set}의 일반 식별성 정리, (2) MIMO 완전 행렬 모호성(스칼라 위상을 넘는 unitary/행렬 모호성)의 코드 기반 해소 조건, (3) 이를 BiG-AMP/EP+복호기로 실현하는 near-pilot-free 수신기의 식별성-성능 동시 특성화. 대부분 polar 중심이며 LDPC/turbo의 near-pilotless는 상대적으로 빈약.

**차별화 기여**: 부호+유한알파벳 결합 하 G의 대수적 특성화(automorphism/frozen bit/all-ones 코드워드/미분부호화 포함)와 고차 QAM·MIMO 행렬 모호성까지 확장한 식별성 정리, IDMA식 스트림별 인터리버로 permutation을 명시적으로 해소. **스쿠핑 위험**: Pilotless Polar(2602.17979)는 polar에 국한 → B는 LDPC/turbo와 일반 행렬 모호성으로 차별화 가능.

**인용 필수 기반**: Marzetta–Hochwald 1999; Zheng–Tse 2002; Hassibi–Hochwald(training) 2003; Scherb–Kühn–Kammeyer; Zhao–Davies 2010; Phase-Equivariant Polar 2023; Pilotless Polar 2026; Dean–Wootters–Goldsmith; IDMA(Ping 외).

### 후보 C — "정확한 외재(leave-one-out) 채널추정과 Onsager 등가성"

**가장 근접한 선행연구:**
- R. Otnes, M. Tüchler, "Iterative Channel Estimation for Turbo Equalization of Time-Varying Frequency-Selective Channels," IEEE TWC 3(6):1918–1923, Nov. 2004 (DOI 10.1109/TWC.2004.837421). 초록 verbatim: "the concept of soft iterative channel estimation, which is to improve the channel estimate over the iterations by using soft information fed back from the decoder... to generate 'extended training sequences' between the actual transmitted training sequences." **명시적 leave-one-out 아님, Onsager 등가 없음, 오류마루-T 특성화 없음.**
- S. Song, A. C. Singer, K.-M. Sung, "Soft Input Channel Estimation for Turbo Equalization," IEEE TSP 52(10):2885–2894, Oct. 2004 (DOI 10.1109/TSP.2004.833857). 소프트정보 소비 MMSE 채널추정 + soft-input RLS; **정상(stationary) 채널의 MSIE 분석**(단블록 오류마루 아님).
- M. Tüchler, R. Otnes, A. Schmidbauer, "Performance of soft iterative channel estimation in turbo equalization," ICC 2002, vol.3, pp.1858–1862.
- M. Sandell, C. Luschi, P. Strauch, R. Yan, "Iterative channel estimation using soft decision feedback," GLOBECOM 1998, pp.3728–3733. 초기 소프트피드백 반복 채널추정.
- Z. Bao, Q. Han, X. Xu, "A leave-one-out approach to approximate message passing," arXiv:2312.05911 (2023). **AMP 반복의 leave-one-out 표현 + Onsager 벡터 명시**. 그러나 일반 AMP 이론(가우시안 설계행렬)이며 **채널추정에 적용 안 됨.**
- M. Bayati, A. Montanari, "The dynamics of message passing on dense graphs...," IEEE T-IT 57(2):764–785, 2011. cavity/BP 1차 근사로 Onsager 유도, self-feedback 상쇄.
- "Joint Channel and Data Estimation for Multiuser Extremely Large-Scale MIMO," arXiv:2406.19289. 안테나별 **외재값**으로 **self-noise feedback 억제**(BP 규칙). 메시지패싱형 외재 채널/데이터 추정에 가장 근접하나 leave-one-out H^{\n} 정식화·Onsager 등가 증명은 없음.
- "Data-Aided LS Channel Estimation in Massive MIMO Turbo-Receiver," arXiv:2003.09317. 소프트심볼 분산이 유발하는 **바이어스**를 모델링해 보정(경험적 상수). 바이어스 메커니즘에 직접 관련하나 T-의존 오류마루 폐형은 아님.
- Sun 외, "Trainable Joint Channel Estimation, Detection and Decoding for MIMO URLLC Systems," TWC 2024 (arXiv:2404.07721). 단 LDPC에서 **positive feedback/error propagation**(Tanner 그래프 단주기 기인)을 정성적으로 기술하며, 이를 회피하려 non-iterative JCDD를 제안. **정량적 오류마루-T 법칙·a posteriori vs extrinsic 채널피드백 비교는 없음.**

**신규성 판정: 열림(appears open).** 서브에이전트 심층조사 결과 세 하위요소 모두 미발표로 확인: (a) 명시적 leave-one-out/jackknife 채널추정 H^{\n} 정식화(채널추정용, 심볼검출용이 아님) — 관련 용어("leave-one-out"/"jackknife")를 채널추정에 쓴 논문 없음; (b) Onsager항 = leave-one-out 채널추정의 1차 Taylor 전개임을 증명 — 재료(Bao–Han–Xu의 leave-one-out AMP, Bayati–Montanari의 cavity Onsager, BiG-AMP의 CLT+Taylor 유도)는 각각 존재하나 채널추정용으로 결합·증명된 적 없음; (c) a posteriori vs extrinsic 채널피드백의 positive-feedback 바이어스/BER 오류마루를 블록길이 T의 함수로 정량화 — 정성적 서술과 경험적 바이어스 모델만 존재.

**차별화 기여**: rank-1 downdate 기반 leave-one-out 소프트심볼 채널추정 H^{\n}의 정식화 및 BiG-AMP Onsager항과의 1차 등가 증명, 그리고 단패킷(URLLC) 오류마루의 T·SNR 의존 특성화. **4개 후보 중 신규성이 가장 명확하고 방어 가능.**

**인용 필수 기반**: Otnes–Tüchler TWC 2004; Song–Singer–Sung TSP 2004; Sandell 외 1998; Valenti–Woerner 2001; Kobayashi–Boutros–Caire 2001; Bayati–Montanari 2011; Donoho–Maleki–Montanari 2009; Bao–Han–Xu 2023; Parker–Schniter–Cevher BiG-AMP 2014; SC-VAMP 2601.07095; Sun 외 TWC 2024.

### 후보 D — "부호화 bilinear JCESD의 상태전개/replica 분석"

**가장 근접한 선행연구:**
- K. Takeuchi, M. Vehkaperä, T. Tanaka, R. R. Müller, "Large-System Analysis of Joint Channel and Data Estimation for MIMO DS-CDMA Systems," IEEE T-IT 58(3):1385–1412, Mar. 2012 (DOI 10.1109/TIT.2011.2177757; arXiv:1002.4470). 초록 verbatim: "Joint CE-MUDD is found to significantly reduce the rate loss caused by transmission of pilot signals when compared to the receivers based on one-shot channel estimation, particularly for multiple-antenna systems." replica 기반 대규모 극한에서 CE–MUDD(per-user decoding 포함) 분석. **후보 D의 가장 직접적 선행연구**이나 DS-CDMA·successive decoding + LMMSE CE에 국한, 현대 복호기의 EXIT 임베딩·파일럿오버헤드-달성률 곡선은 없음.
- J.-C. Jiang, H.-M. Wang, H. V. Poor, "Performance Analysis of Joint Active User Detection and Channel Estimation for Massive Connectivity," IEEE TSP 70:3647–3662, 2022 (DOI 10.1109/TSP.2022.3185844; arXiv:2206.12541). Bayes-optimal replica로 AMP JADCE 상전이·최적성 분석. **데이터복호 미포함.**
- C.-K. Wen, C.-J. Wang, S. Jin, K.-K. Wong, P. Ting, "Bayes-Optimal Joint Channel-and-Data Estimation for Massive MIMO With Low-Precision ADCs," IEEE TSP 64(10):2541–2556, May 2016. replica로 저해상도 ADC JCESD.
- SC-VAMP(2601.07095): 상태전개·Onsager·decoupling을 스코어 관점에서, EXIT/turbo 원리와의 연결을 명시(그러나 부호화 bilinear JCESD 달성률 분석은 아님).
- "A Joint Symbol-Detection, Channel-Estimation and Decoding Scheme under Few-Bit ADCs" (Sensors 2020, PBiGAMP + doping factor로 extrinsic/posterior 혼합). 알고리즘적 결합이나 상태전개 달성률 분석은 없음.
- Hassibi–Hochwald "How much training is needed?" (IEEE T-IT 2003), Marzetta–Hochwald 1999, Zheng–Tse 2002: 파일럿 하계·비간섭 용량의 기준.

**신규성 판정: 부분 커버/열림.** 이미: CDMA·활성탐지·저해상도 ADC의 replica/상태전개. **미완**: (1) 채널 MSE와 심볼 MSE를 결합한 2차원 상태전개에 복호기 EXIT 전달함수를 임베딩, (2) 그 고정점으로부터 T_p·T·SNR 함수의 달성률 도출, (3) Hassibi–Hochwald 훈련 하계와 Marzetta–Hochwald/Zheng–Tse 비간섭 용량 사이 격차를 JCESD가 얼마나 회수하는지 정량화 — 이 통합 분석은 미발견.

**차별화 기여**: 복호기 EXIT를 내장한 2D 상태전개 + 달성률-파일럿오버헤드 곡선 + 훈련 하계 대비 회수율 정량화(massive MIMO/OFDM/저해상도 ADC 확장).

**인용 필수 기반**: Takeuchi 외 T-IT 2012(1002.4470); Jiang–Wang–Poor TSP 2022; Wen 외 TSP 2016; Hassibi–Hochwald 2003; Marzetta–Hochwald 1999; Zheng–Tse 2002; ten Brink EXIT; Ma–Ping OAMP; Parker–Schniter–Cevher BiG-AMP; SC-VAMP 2601.07095.

## Recommendations

1. **즉시 착수 권장(가장 열림, 신규성 최강): 후보 C.** 서브에이전트 심층조사로 세 하위요소 모두 미발표 확인. 실행 순서: (i) Bao–Han–Xu(2312.05911)의 leave-one-out AMP 표현을 bilinear 채널추정으로 이식 → (ii) BiG-AMP Onsager항과의 1차 등가를 증명 → (iii) 단블록 오류마루를 상태전개로 정량화(후보 D와 자연 결합). **판단 변경 트리거**: SC-VAMP(2601.07095) 계열이 "채널추정 + leave-one-out + Onsager 증명"으로 확장되면 즉시 재평가.

2. **차선 착수(속도가 관건): 후보 A.** SC-VAMP(2601.07095)와 특히 후속 2604.19061이 "BP 복호기 스코어 + Onsager 외재 교환"을 이미 선점 → **A는 "학습된 채널 확산 prior + bilinear 완전 JCESD"로 축을 재정의**하고 최소예제(convolutional 또는 LDPC + 2×2 MIMO, 학습된 채널 스코어 prior)로 신속 실증. **트리거**: 2604.19061 후속이 학습된 채널 생성 prior를 결합하면 A의 잔여 신규성이 소멸하므로 월 단위 추적 필수.

3. **정리(theory) 논문으로 후보 B 재구성.** 응용은 포화(polar 위주)이므로 순수 알고리즘보다 **식별성 정리**(고차 QAM·MIMO 행렬 모호성군 G의 대수적 특성화)로 포지셔닝. Scherb·Zhao–Davies·Phase-Equivariant Polar·Pilotless Polar를 반드시 차별화하고, LDPC/turbo + 일반 행렬 모호성을 핵심 기여로.

4. **후보 D는 후보 C와 묶어서.** 2D 상태전개(D)는 C의 Onsager 등가 결과를 분석 엔진으로 재사용 가능. Takeuchi 프레임을 현대 복호기 EXIT로 확장하되 **Hassibi–Hochwald 대비 회수율**을 핵심 신규 지표로. 단독 D는 Takeuchi와의 증분이 작을 위험.

5. **공통 모니터링**: 모든 후보는 SC-VAMP(2601.07095) 및 2604.19061을 인용·차별화해야 하며, 2025–2026 arXiv를 월 단위 추적(특히 Wadayama–Takahashi 그룹[A·C·D 전반], Nachmani/Choukroun–Wolf 그룹[A], Schniter 그룹[A·C·D], Segarra/Zilberstein 그룹[A]).

## Caveats
- **검증 상태**: 대부분 논문은 arXiv landing/PDF 또는 다중 인용 교차확인으로 저자·제목·연도를 검증. 일부 IEEE 유료 PDF는 직접 열람하지 못해 권/호/페이지는 교차인용에 의존. Otnes–Tüchler TWC 2004(3(6):1918–1923, DOI 10.1109/TWC.2004.837421), Song–Singer–Sung TSP 2004(52(10):2885–2894, DOI 10.1109/TSP.2004.833857), Takeuchi 외 T-IT 2012(58(3):1385–1412, DOI 10.1109/TIT.2011.2177757), Jiang–Wang–Poor TSP 2022(70:3647–3662), Wen 외 TSP 2016(64(10):2541–2556)은 서지 검증 완료.
- **arXiv:2604.19061(Three-Module SC-VAMP for LDPC-Coded Nonlinear Channels)**은 enricher가 반환한 후보 A 최대 스쿠핑 위험 논문이나, 필자가 직접 원문을 열람하지 못했으므로 초록 문구 외 세부(채널 prior의 성격, JCESD 여부)는 착수 전 반드시 직접 확인 요망. 이 확인 결과에 따라 A의 신규성 판정("열림")이 "부분 커버"로 하향될 수 있음.
- Song–Singer–Sung 페이지는 TSP 2004 52(10):2885–2894가 정확하며, 일부 인용의 "III-2805–2808"은 별개 ICASSP 2002 논문(“Turbo equalization with an unknown channel,” Orlando)임(혼동 주의).
- arXiv 2605.18902(VCDC), 2605.28358(Score-Based ECC), 2601.07095(SC-VAMP), 2602.17979(Pilotless Polar), 2604.19061 등 2026년 프리프린트는 아직 피어리뷰 전일 수 있어 최종 게재 여부 재확인 필요.
- "부분 커버/열림" 판정은 부재 증명(proving a negative)의 한계를 가짐 — 검색범위(arXiv, IEEE Xplore, 주요 학회) 밖 또는 매우 최근(2026년 하반기) 논문 존재 가능성을 배제할 수 없음. Onsager⇔leave-one-out 채널추정 등가에 대한 단일 명시적 증명 논문을 찾지 못했다는 점이 후보 C "열림" 판정을 강화하나 100% 확정은 아님.