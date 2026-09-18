# T2 Scooping Log

> 월 1회(매월 1일) arXiv cs.IT / eess.SP / cs.LG 전수 확인. 키워드(핸드오프 §7 + 동반 노트 §7): `score-based VAMP`, `LDPC coded nonlinear channel score`, `diffusion joint channel estimation decoding`, `decoder as denoiser diffusion`, `generative receiver coded bilinear`, `Tweedie BCJR`, `plug-and-play decoder`, `trellis denoiser diffusion`, `annealed turbo`, `Onsager Fisher`, `score-to-Fisher bridge`.
> 감시 그룹: Wadayama–Takahashi, Segarra/Zilberstein, Schniter, Nachmani·Choukroun–Wolf, Utschick.
> 발견 시: 여기에 기록 → 24시간 안에 핸드오프 §4 시나리오 재판정 → 필요하면 보고.

---

## [2026-09-15] 착수 확인 (전수 sweep 아님)

**원문 판독.** arXiv:2604.19061v1 (Wadayama–Takahashi, "Three-Module SC-VAMP for LDPC-Coded Nonlinear Channels", 21 Apr 2026) 전문(6쪽) 판독 완료.
- 채널: known $\mathbf H$ (i.i.d. Gaussian, 실험은 block-diagonal $32\times32$) + known component-wise $f=\tanh$ [eq. (1)–(2), §II-B; eqs. (16)–(17), §III-C1].
- 학습 prior: 없음 (code prior만; unknown $f$용 learned score는 §III-C2·§V에서 가능성/future work로만 언급).
- Denoiser: LDPC BP만 [§III-C3, eqs. (23)–(24)]; trellis/BCJR 없음.
- **판정: 시나리오 1** — T2 novelty (i)+(ii)+(iii)+(iv) 유지, (ii) 문장 수정(D-02 참조).
- 그들의 future work(§V): state evolution, clipping/1-bit, unknown $f$ score learning. 채널 추정·bilinear 없음.
- 유의: 이 논문의 §III-A는 "general Markov chain $X_1\to\cdots\to X_L$"로 일반화를 선언. 채널을 latent로 넣는 확장은 그들에게 가까움. 단 bilinear는 단일 chain이 아님(Q-08).

**감시 그룹 빠른 확인(웹 검색 2건, 전수 아님).** Wadayama–Takahashi의 2604.19061 이후 wireless 관련 신규 게시물: 확인되지 않음. 2601.07095(SC-VAMP) v1만 재확인. 다른 감시 그룹은 미확인.
**판정.** 시나리오 1 유지. 다음 전수 sweep: **2026-10-01** (위 키워드 전부, 5개 그룹).

---

## [2026-09-17] 세션 3 메모 (sweep 아님)
새로 생긴 확인 대상: (a) D-14 관련 — "denoiser Jacobian = posterior covariance (2차 Tweedie)"를 역문제 likelihood 결합에 쓰는 diffusion 문헌 [M, 출처 미확인 → VERIFY]; (b) D-13 관련 — VAMP/EP형 JCESD에서 "LMMSE 단계의 belief 등방화 vs extrinsic 등방화" 비교나 $T_p<N_t$ 시동 문제 언급 여부; (c) D-15 관련 — EP-JCESD에서 bilinear factor의 tilted 모멘트를 APP로 근사하는 선행(고전 turbo 채널 추정의 "APP 기반 soft symbol" 관행 [M] 포함). 판정 변화 없음(시나리오 1 유지).

## [2026-09-18] 세션 5 메모 (sweep 아님; R-A 설계 중 웹 검색 2건)
- **SNIPS** — Kawar, Vaksman, Elad, "SNIPS: Solving Noisy Inverse Problems Stochastically", NeurIPS 2021, arXiv:2105.14951 [V: 초록·서론 발췌]. SVD로 측정을 분리하고 annealed Langevin의 annealing 잡음을 **측정 잡음의 일부로 구성**, MMSE Gaussian denoiser만 사용 → 우리 R-A의 noise-splitting·고유기저 clamp 구성의 **prior art**. 영상 역문제, 표본 생성 목적; EP 모멘트·통신 수신기 아님. 본문 식 대조는 미실시 [VERIFY].
- **MMPS** — arXiv:2405.13712 ("Learning Diffusion Priors from Observations by Expectation Maximization") §4.2 [V: 발췌]: $q(y|x_t)=\mathcal N(y|A\mathbb E[x|x_t],\Sigma_y+A\mathbb V[x|x_t]A^\top)$, Tweedie 공분산 사용, 선행 [22–25] 인용 → D-14 재료(2차 Tweedie 공분산을 역문제 likelihood 결합에 사용)의 prior art 확인(부분). 우리 것은 turbo 수신기의 행렬값 EP site로 쓰는 것·Gaussian 항등식·GMM 기준 측정.
- arXiv:2605.30330 ("When, why, and how do diffusion posterior samplers fail? A finite-sample lens", 2026-05) [V: 발췌] — moment-matching DPS 계열 정리. 무선·부호 없음. 위협 아님.
- 2204.07122(Arvinte–Tamir) Alg. 1 원문 확인 [V]: ALD 점추정, likelihood 분모에 annealing 항, 50표본 평균을 approximate MMSE로 사용. 보정된 공분산·turbo 결합 없음.
- **판정 변화 없음(시나리오 1 유지).** 기여 목록 영향: ③(F6 + R-A 처방)에서 표집기 자체는 prior art 조합임을 명시, 우리 것은 "EP site용 Rao-Blackwell 모멘트 + D-13/D-14와의 관계 + $\chi$ 전환 + turbo 통합".

## [2026-09-18] 세션 5 메모 2 (sweep 아님; 웹 검색 1건)
- **GMM 기반 CME** — Koller, Fesl, Turan, Utschick, "An Asymptotically MSE-Optimal Estimator Based on Gaussian Mixture Models", IEEE TSP 70:4109–4123 (2022), arXiv:2112.12499 [V: 초록]: 채널 표본에 GMM 적합 → 폐형식 CME. **감시 그룹(Utschick).** 우리 GMM testbed의 `exactEP` 기준과 같은 계산 구조 → Q-32(전략). 후속: structured covariances(arXiv:2205.03634), mixtures of factor analyzers(ACSSC 2023), **"Diffusion-based Generative Prior for Low-Complexity MIMO Channel Estimation"(arXiv:2403.03545) [V: dblp 제목만 — 원문 VERIFY]**.
- 판정 변화 없음(시나리오 1): 위 계열은 pilot-only 채널 추정이며 부호·bilinear 결합 없음[초록 수준 확인]. 단 기여 ③의 "prior 모듈" 서술은 GMM-CME를 baseline으로 명시해야 함.

## [2026-09-18] 세션 6 메모 (sweep 아님; 웹 검색 0건 — 코드 세션)
- 새로 생긴 [VERIFY] 대상(10-01 sweep에 추가): (a) **구조화 공분산 GMM 채널 추정** — Kronecker/matrix-normal 성분 GMM 적합의 선행. 후보 arXiv:2205.03634(Utschick 그룹, "structured covariances" [V: 제목만])와 mixtures of factor analyzers(ACSSC 2023 [M]) 본문 확인; 우리는 이것을 kill test의 baseline 강화(R3)로만 쓰므로 위협은 아니지만, GMM arm의 서술에 인용 필요. (b) **EP/moment-matching에서 site 정밀도 clip 시 평균 보존 규칙**의 선행(EP 문헌의 "moment matching with PSD projection" 관행 [M] — Minka, Seeger, power-EP 계열에서 표준일 가능성이 높음; 표준이면 우리 것으로 주장하지 않고 관행으로 인용). (c) 각도 규약(전기각 vs 물리각) 관련 없음.
- 추가 키워드: `Kronecker structured Gaussian mixture channel prior`, `matrix normal mixture channel estimation`, `expectation propagation site precision positive definite projection`, `moment matching mean preserving damping EP`.
- 판정 변화 없음(시나리오 1 유지). 감시 그룹 동일.

## 예정
- [ ] 10-01 sweep 추가 키워드: `second-order Tweedie posterior covariance inverse problem`, `denoiser Jacobian covariance diffusion`, `EP bilinear tilted moments channel estimation`, `semi-blind fewer pilots than antennas turbo`.
- [ ] 2026-10-01 전수 sweep. 특히 확인: 2604.19061 v2 여부, Wadayama–Takahashi "SC-VAMP + channel estimation / bilinear / MIMO", Segarra 그룹 coded diffusion JCESD, Choukroun–Wolf 2026 score decoder 후속.
- [ ] 동반 노트 Phase 0 항목: `plug-and-play decoder`, `code-aware denoiser`, `HMM denoiser diffusion`, `structured prior Tweedie` 검색 (미실시).
- [ ] 10-01 sweep 추가 키워드(세션 4): `pilot contamination-free semi-blind fewer pilots than transmit antennas turbo`, `score-based posterior sampling channel estimation turbo decoding`, `isotropic denoiser interface VAMP rank-deficient`, `eigen-aligned pilots correlated MIMO joint estimation decoding`.
- [ ] 10-01 sweep 추가 키워드(세션 5): `SNIPS channel estimation`, `diffusion posterior sampling expectation propagation moments`, `Rao-Blackwellized Tweedie posterior covariance`, `noisy inpainting diffusion MIMO channel pilots fewer than antennas`, `annealed Langevin joint channel estimation decoding coded`. 원문 확인: SNIPS 본문, 2405.13712의 [22–25], TMPD/ΠGDM [M].
- [ ] 10-01 sweep 추가(세션 5-2): `Gaussian mixture model channel estimator turbo / joint decoding / semi-blind`, `Utschick diffusion prior channel estimation` (2403.03545 원문·후속), `moment matching posterior sampling wireless`.
- [ ] 10-01 sweep 추가(세션 6): `Kronecker structured Gaussian mixture channel prior`, `matrix normal mixture channel estimation`, `expectation propagation site precision positive definite projection`, `moment matching mean preserving damping EP`. 원문 확인: 2205.03634.
- [ ] 10-01 sweep **최우선**(세션 5-3, Q-33): `Gaussian mixture model channel estimation turbo receiver`, `GMM prior joint channel estimation decoding`, `GMM semi-blind channel estimation data-aided Utschick`, `conditionally Gaussian channel prior expectation propagation bilinear`. 2112.12499 본문에서 "채널은 조건부 Gaussian → GMM이 자연스럽다"는 논거의 원문 확인 [M → VERIFY].

