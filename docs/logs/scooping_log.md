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

## 예정
- [ ] 10-01 sweep 추가 키워드: `second-order Tweedie posterior covariance inverse problem`, `denoiser Jacobian covariance diffusion`, `EP bilinear tilted moments channel estimation`, `semi-blind fewer pilots than antennas turbo`.
- [ ] 2026-10-01 전수 sweep. 특히 확인: 2604.19061 v2 여부, Wadayama–Takahashi "SC-VAMP + channel estimation / bilinear / MIMO", Segarra 그룹 coded diffusion JCESD, Choukroun–Wolf 2026 score decoder 후속.
- [ ] 동반 노트 Phase 0 항목: `plug-and-play decoder`, `code-aware denoiser`, `HMM denoiser diffusion`, `structured prior Tweedie` 검색 (미실시).
