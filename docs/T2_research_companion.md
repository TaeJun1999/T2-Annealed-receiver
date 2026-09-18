# T2 연구 동반 노트 — 물어야 할 질문, 함정, 읽을 논문, 기록 템플릿

> 용도: T2(annealed turbo receiver) 프로젝트 안에서 연구를 진행하며 수시로 펼쳐 보는 개인 참고 문서. 핸드오프 문서가 "무엇을 할 것인가"라면, 이 문서는 "무엇을 물어야 하는가"와 "무엇에 걸려 넘어지는가"의 목록이다.
> 표기: 기술 용어는 영어, 설명은 한국어. 참고문헌의 **[V]** 는 2026-08 조사에서 서지 확인됨, **[M]** 은 기억 기반이라 인용 전 재확인 필요.
> 상태 기준일: 2026-08-25.

---

## 0. 이 문서를 쓰는 법

- 매 세션 시작: §2의 해당 phase 질문 중 아직 답이 없는 것을 하나 고른다.
- 매 세션 끝: §9 템플릿으로 decision log와 open questions를 갱신한다.
- 매월 1일: §7 감시 키워드로 arXiv를 훑고 scooping log를 쓴다.
- 교수님 미팅 전: §4에서 해당 마일스톤의 질문을 고르고, §5의 예상 질문에 대한 답을 한 줄씩 준비한다.
- 어떤 결과든 "정확 / 근사 / 추측" 중 하나로 표시하기 전에는 확정으로 취급하지 않는다.

---

## 1. 연구 질문의 위계

**주 질문.** 부호화된 심볼과 미지의 채널을 함께 다루는 생성 수신기를, 표준 복호기를 심볼 denoiser로 그대로 쓰고 학습된 diffusion prior를 채널에만 붙여서 만들 수 있는가. 그렇게 하면 짧은 블록에서 파일럿을 얼마나 줄일 수 있는가.

**하위 질문 1 — 정확성.** 어떤 조건에서 decoder의 soft output이 부호화 심볼 prior의 정확한 Tweedie denoiser(score)인가. 조건이 깨지는 경우(QAM, tail-biting, puncturing, turbo/LDPC)의 오차는 얼마인가.

**하위 질문 2 — 결합.** 두 denoiser(BCJR, channel score model)를 bilinear 우도로 결합할 때 extrinsic/Onsager 보정을 어떻게 정확히 하는가. 채널 오차 공분산이 등방성이 아닐 때 diffusion denoiser를 어떻게 쓰는가.

**하위 질문 3 — 스케줄.** turbo 반복의 신뢰도 증가를 annealing schedule로 볼 때, 노이즈 레벨을 메시지 분산에서 유도하는 것이 고정 스케줄보다 실제로 나은가.

**하위 질문 4 — 이득의 출처.** 파일럿 절감 이득 중 얼마가 채널 prior에서, 얼마가 부호 인식 denoiser에서, 얼마가 extrinsic 채널 추정(T1)에서 오는가.

**하위 질문 5 — 강건성.** 학습 분포와 운용 분포가 다를 때 이득이 얼마나 남는가. Gaussian/GMM 같은 싼 prior와 비교해 diffusion prior가 값어치를 하는가.

---

## 2. 단계별로 반드시 물어야 할 질문

### Phase 0 — 착수 전 (문헌·스쿠핑)

- [ ] arXiv:2604.19061 (Three-Module SC-VAMP) 원문에서 세 가지를 확인했는가: (i) 채널이 미지수(bilinear)인가 아니면 알려진 비선형인가, (ii) 학습된 채널 prior가 있는가, (iii) BCJR/trellis denoiser가 있는가. → 답에 따라 §3.4의 잔여 novelty 시나리오를 확정한다.
- [ ] arXiv:2601.07095 (SC-VAMP)의 Onsager 항 계산법(Fisher information)이 우리 채널 denoiser에 그대로 적용되는가, 아니면 Monte-Carlo divergence가 필요한가.
- [ ] Zilberstein 2024가 쓴 채널 prior의 형태(픽셀 vs 변환 도메인, 크기)와 우리 설정의 차이는 무엇인가.
- [ ] "decoder as denoiser"를 다른 이름으로 이미 쓴 논문이 있는가: `plug-and-play decoder`, `code-aware denoiser`, `HMM denoiser diffusion`, `structured prior Tweedie` 로 검색했는가.
- [ ] Utschick 그룹의 GMM/VAE 기반 채널 추정기를 베이스라인 목록에 넣었는가 (diffusion보다 싼 학습 prior — 리뷰어가 반드시 묻는다).
- [ ] T1(leave-one-out 채널 추정)이 어디까지 진행됐는가. T2의 3단계가 그 결과를 쓴다.

### Phase 1 — Lemma: decoder = score

- [ ] 실수 BPSK: $\tilde x=x+\sigma\epsilon$, $\epsilon\sim\mathcal N(0,1)$에서 LLR $=2\tilde x/\sigma^2$, 즉 $L_c=2/\sigma^2$. 복소 관측일 때 $\sigma^2$가 복소 차원당인지 실수 차원당인지 어느 쪽으로 고정했는가. 두 규약을 섞으면 factor 2 오류가 난다.
- [ ] Tweedie를 복소 형태로 쓸 때 Wirtinger 미분 규약을 한 번 정하고 코드와 수식이 일치하는가.
- [ ] 종료된(terminated) 트렐리스에서 BCJR a posteriori 소프트 심볼이 $\mathbb E[x_k\mid\tilde{\mathbf x}]$와 같음을 짧은 블록($K\le 20$)에서 brute force로 확인했는가.
- [ ] tail-biting 부호에서는 정확성이 깨지는가(순환 BCJR은 근사). 어느 부호를 쓸지 결정했는가.
- [ ] puncturing/rate matching: 천공 위치는 관측 없음(erasure)으로 넣으면 정확성이 유지되는가.
- [ ] **QAM에서의 함정**: 심볼 사후 평균 $\sum_a a\,P(x=a\mid\cdot)$은 한 심볼의 $m$비트에 대한 **결합** 사후를 요구한다. BCJR의 비트별 marginal LLR을 곱으로 조합하면 근사다. 정확히 하려면 심볼 단위 트렐리스(한 섹션에 $m$비트)로 돌려야 한다. 어느 쪽으로 갈지, 근사 오차는 얼마인지 측정했는가.
- [ ] divergence: BPSK에서 $\partial\mathbb E[x_k\mid\tilde{\mathbf x}]/\partial\tilde x_k=\mathrm{Var}(x_k\mid\tilde{\mathbf x})/\sigma^2=(1-\tanh^2(L_k/2))/\sigma^2$. QAM에서는 심볼 사후 분산으로 일반화되는가. off-diagonal Jacobian(다른 심볼 간 상관)은 Onsager 항에 필요한가, 아니면 trace만 필요한가.
- [ ] 정확한 사후 샘플링: forward filtering–backward sampling으로 코드워드를 샘플링하는 구현이 있는가. 샘플 평균이 BCJR 소프트 출력과 일치하는가(검증).
- [ ] turbo/LDPC 근사 오차: 같은 브루트포스 비교를 짧은 turbo/LDPC에서 하고, 오차를 입력 $L_c$의 함수로 그렸는가(낮은 $L_c$와 높은 $L_c$에서 작고 중간에서 큰지).
- [ ] lemma의 진술을 "정리 + 증명 + 가정"으로 한 페이지에 썼는가. 가정: 종료 트렐리스, 등방성 가우시안 노이즈, 심볼 단위 사후.

### Phase 2 — Channel score model

- [ ] 학습 데이터 출처를 정했는가: CDL-B/C(Sionna), DeepMIMO, 실측. 각각 몇 개의 실현값인가(권장 $10^4\sim10^5$).
- [ ] 표현 도메인: 픽셀($N_r\times N_t$ 실수부/허수부) vs angle-delay. 어느 쪽이 학습이 쉽고 denoising MSE가 낮은가. 두 도메인 모두 시도했는가.
- [ ] 정규화: 채널 에너지를 어떻게 맞췄는가(entry당 단위 분산). 수신기에서 SNR 정의와 일치하는가.
- [ ] 아키텍처: 작은 행렬($8\times4$)에 U-Net이 맞는가. MLP/DiT형이 나은가. 파라미터 수와 추론 시간은.
- [ ] 노이즈 스케줄: 수신기에서 실제로 만나는 채널 오차 크기 범위(파일럿-only 초기의 큰 값부터 후반 반복의 작은 값까지)를 학습 스케줄이 덮는가. 범위 밖이면 denoiser가 외삽한다.
- [ ] 위상 불변성: 채널 분포가 global phase 회전에 불변이면 데이터 증강으로 넣었는가. 안테나 순서/공액 대칭 같은 다른 불변성은.
- [ ] Gaussian sanity: $\mathcal{CN}(0,\mathbf R)$로 학습한 모델의 denoiser가 LMMSE 폐형과 일치하는가. 이게 안 맞으면 다음 단계로 가지 않는다.
- [ ] denoising MSE vs $\sigma$ 곡선을 그렸는가. 이 곡선이 §T5의 mismatch spectrum과 같은 물건이다.
- [ ] **비등방 오차 공분산**: 3단계의 $\mathbf C_{\mathrm{LS}}$는 일반적으로 등방성이 아니다. (a) whitening 후 denoise, (b) $\sigma^2=\mathrm{tr}(\mathbf C)/d$ 스칼라 근사, (c) VAMP식으로 LMMSE 단계가 오차를 근사 등방화한다는 논리 — 셋 중 무엇을 쓰고 손실은 얼마인가.
- [ ] mismatch: CDL-B 학습 → CDL-C 운용, DeepMIMO 시나리오 A → B. 성능 감소량을 측정했는가.
- [ ] 베이스라인 prior: Gaussian(Kronecker), GMM(Utschick), VAE. 같은 데이터로 학습해 비교했는가.

### Phase 3 — 결합 알고리즘

- [ ] route (a) 결정적 메시지 패싱과 route (b) 샘플링 중 무엇이 주인가. 둘 다 구현했는가(ablation용).
- [ ] extrinsic 메시지 공식을 분산 도메인에서 정확히 썼는가: $1/v^{\mathrm{ext}}=1/v^{\mathrm{post}}-1/\tau$, $\bar x^{\mathrm{ext}}=v^{\mathrm{ext}}(\hat x/v^{\mathrm{post}}-r/\tau)$. 음의 분산이 나올 때의 guard는.
- [ ] 채널 쪽 Onsager: Monte-Carlo divergence(Hutchinson)의 분산과 비용, 또는 Fisher trick. 어느 쪽을 쓰고 오차는 얼마인가.
- [ ] 3단계가 T1의 leave-one-out 추정을 쓰는가, 아니면 임시로 a-posteriori 되먹임을 쓰는가. 후자면 positive feedback이 결과를 오염시킨다.
- [ ] 초기화: $T_p<N_t$(미결정)일 때 파일럿-only 초기치가 나쁘다. prior가 얼마나 메우는가. 다중 초기화가 필요한가.
- [ ] 스케줄: 메시지 분산에서 유도한 스케줄 vs 고정 기하 스케줄. 둘 다 돌렸는가. 발산·진동이 있으면 damping 계수는.
- [ ] 반복 횟수와 종료: 5, 10, 15회에서 BLER 포화 지점은. CRC 조기 종료는 넣었는가.
- [ ] 실패 모드 점검: 분산 붕괴(과신), 진동, 낮은 SNR에서 발산. 각각을 유발하는 설정을 찾아 기록했는가.
- [ ] 복잡도 회계: 반복당 BCJR 1회 + score net 1회 + 선형대수. FLOPs와 wall-clock을 분리했는가. 학습 비용은 제외했고 그 이유를 적었는가.

### Phase 4 — 실험

- [ ] 설정 고정: $N_t\times N_r\in\{4\times4,\ 8\times4,\ 8\times8\}$, 16-QAM, $T\in\{14,28,56\}$, $T_p/T\in\{1/14,\dots,4/14\}$, 채널 CDL-B/C·DeepMIMO. 시드와 버전이 기록됐는가.
- [ ] 베이스라인 그룹: (i) pilot-only LMMSE + turbo 수신기(a-posteriori / T1-extrinsic), (ii) BiG-AMP + decoder, (iii) 학습형: Sun 2024 JCDD, GMM/VAE prior 수신기, (iv) 생성형: Zilberstein 2024(비부호화), 2604.19061 구조 재현(Gaussian prior), (v) genie CSI.
- [ ] 공정성: 같은 채널 실현값, 같은 decoder 반복 수, 같은 파일럿 패턴. 베이스라인도 튜닝했는가.
- [ ] 지표 정의: NMSE 식, BLER, "파일럿 절감량 at target BLER"의 정의와 SNR 범위. 평균을 취했다면 무엇에 대해.
- [ ] Ablation 다섯 개를 다 돌렸는가: (1) diffusion prior → Gaussian prior, (2) BCJR → 비부호화 constellation denoiser, (3) extrinsic → a-posteriori 채널 되먹임, (4) 유도 스케줄 → 고정 스케줄, (5) route (a) → route (b).
- [ ] 이득의 귀속: 각 베이스라인 그룹 대비 이득을 하나의 원인에 귀속했을 때, 그 원인을 가진 다른 베이스라인도 이기는가. 그렇다면 진짜 차별점은 무엇인가.
- [ ] 통계: BLER $10^{-3}$ 점에 오류 블록 100개 이상인가. 신뢰구간을 그렸는가.
- [ ] 강건성: mismatch 실험, SNR 추정 오차, 파일럿 패턴 변화.
- [ ] 수렴 그림: 반복별 NMSE와 심볼 분산 궤적을 그렸는가(T3의 2D SE와 비교할 재료).

### Phase 5 — 분석 연결 (T3)과 주장 범위

- [ ] T3의 2D state evolution 예측과 시뮬레이션 궤적이 맞는가. 안 맞으면 어느 가정이 깨졌는가.
- [ ] 파일럿 절감 주장의 범위를 SNR·$T$·부호율로 명시했는가.
- [ ] "optimal"이라는 단어가 어디에도 없는가(증명된 것 외).

---

## 3. 함정 목록 (한 번씩은 걸리는 것들)

1. **factor 2**: $L_c=2/\sigma^2$의 $\sigma^2$가 실수 차원당인지 복소 차원당인지. 코드의 noise 생성과 LLR 계산을 같은 규약으로.
2. **a-posteriori를 extrinsic 자리에**: 3단계의 채널 추정에 decoder의 a-posteriori 소프트 심볼을 쓰면 positive feedback. T1의 leave-one-out 또는 최소한 extrinsic 소프트 심볼.
3. **Tweedie의 부호**: $\mathbb E[x\mid\tilde x]=\tilde x+\sigma^2\nabla\log p$. 네트워크가 $\epsilon$을 예측하면 $\nabla\log p=-\epsilon_\theta/\sigma$. 부호 실수는 denoiser가 노이즈를 더하는 결과를 낸다.
4. **QAM 심볼 사후 평균**: 비트 marginal의 곱은 근사(§2 Phase 1).
5. **비등방 오차에 등방 denoiser**: 3단계 오차 공분산을 스칼라로 뭉개면 손실. 최소한 손실을 측정.
6. **스케줄 범위 밖 외삽**: 학습한 $\sigma$ 범위 밖의 노이즈 레벨에서 denoiser를 호출하면 무의미한 출력.
7. **Onsager 누락**: 채널 denoiser의 divergence를 빼먹으면 반복이 과신으로 붕괴. 증상: 반복 2~3회 만에 분산이 0으로.
8. **불공정 베이스라인**: turbo 수신기 베이스라인에 decoder 반복을 덜 주거나, 파일럿 패턴을 다르게 주는 실수.
9. **학습 비용 은닉**: 복잡도 표에서 학습을 제외했으면 명시. 리뷰어는 반드시 묻는다.
10. **CDL 과적합**: CDL 한 종류로만 학습·평가하면 "합성 채널에 과적합"이라는 공격. mismatch 실험 필수.
11. **정확·근사 경계 흐림**: lemma는 컨볼루션에서 정확, turbo/LDPC에서 근사. 문장마다 어느 쪽인지.
12. **단위 시험 없는 유도**: 모든 항등식은 Gaussian 특수 경우로 수치 검증. 검증 안 된 유도는 노트에 [UNVERIFIED].
13. **스쿠핑 로그 누락**: 월 1회 확인을 건너뛰면 몇 달 뒤 논문을 접는다.

---

## 4. 교수님께 물어볼 질문 (마일스톤별)

**착수 시**
- 트렐리스 우선(정확성) + LDPC 확장 순서를 승인하시는가.
- 목표 venue: ICASSP/GLOBECOM 선행 후 TWC/JSAC인지, 바로 저널인지.
- 2604.19061 판정이 나쁠 때 T4(파일럿 설계)로 전환하는 조건을 미리 정해도 되는가.
- 실측 채널 데이터에 접근할 수 있는가(없으면 DeepMIMO로 site-specific 대체).

**Lemma 완료 시**
- QAM 심볼 단위 트렐리스로 갈지, 비트 marginal 근사로 가고 오차를 보고할지.
- lemma를 별도 짧은 논문(ISIT/Comm. Lett.)으로 낼 가치가 있는지, 아니면 본 논문에 넣을지.

**첫 결과 시**
- 파일럿 절감량의 headline 숫자와 그 SNR 범위가 설득력이 있는지.
- 이득 귀속 설명(prior vs 부호 denoiser vs extrinsic)이 납득되는지.
- 어느 베이스라인이 빠졌다고 보시는지(특히 GMM/VAE prior).

**논문 준비 전**
- 그림 1(구조도)과 그림 2(정확성 검증)를 먼저 그려서 보여 드리고 의견을 받는다.
- 주장 범위와 "하지 않을 주장" 목록을 확인받는다.

---

## 5. 예상 리뷰어/청중 질문과 준비할 답

| 질문 | 준비할 답의 골자 |
|---|---|
| 왜 5G LDPC가 아니라 컨볼루션인가 | 정확성 결과가 트렐리스에서만 성립; 짧은 블록에서 컨볼루션은 약하지 않음; LDPC는 확장 장에서 근사 오차와 함께 제시 |
| Wadayama–Takahashi와 무엇이 다른가 | 미지 채널(bilinear), 학습된 채널 prior, 트렐리스 정확 score, 메시지 분산에서 유도한 스케줄. 원문 확인 후 확정된 문장으로 |
| BCJR이 MMSE denoiser라는 건 고전 아닌가 | 맞다. 새로운 것은 확산 시간축과의 동일시, bilinear 수신기 안에서의 결합, 정확한 divergence와 샘플링의 활용 |
| QAM에서도 정확한가 | 심볼 단위 트렐리스면 정확, 비트 marginal 곱이면 근사. 측정치 제시 |
| 채널 prior 학습 데이터는 어디서 오나, 실용적인가 | 시뮬레이터/ray-tracing/기지국 과거 추정치. 실측 접근 여부 명시. mismatch 실험으로 한계 제시 |
| GMM/VAE prior로도 되지 않나 | 같은 데이터로 학습한 GMM/VAE 베이스라인 결과로 답. diffusion의 추가 이득이 작으면 그렇게 보고 |
| 복잡도는 turbo 수신기 대비 얼마나 늘었나 | 반복당 score net 1회 추가. FLOPs/시간 표. 학습 제외 명시 |
| 반복이 수렴한다는 보장이 있나 | 없음(T3에서 SE로 다룸). 실험적 수렴 곡선과 실패 모드 제시 |
| 파일럿 절감이 어느 레짐에서 성립하나 | 짧은 블록·중저 SNR. 범위를 표로 |
| diffusion 샘플링은 느리지 않나 | 주 방식은 결정적 메시지 패싱(5~15회). 샘플링 버전은 ablation |
| 채널 오차가 가우시안이라는 가정은 | leave-one-out으로 독립성 확보, 가우시안은 근사. 잔차 분포를 측정해 제시 |
| 실측 채널에서도 되나 | 접근 가능 여부에 따라 답. 없으면 명시적 한계로 |

---

## 6. 읽을 논문 (우선순위 · 무엇을 뽑아낼지)

### Tier 1 — 착수 전에 읽을 것
1. T. Wadayama, T. Takahashi, "Three-Module SC-VAMP for LDPC-Coded Nonlinear Channels," arXiv:2604.19061 [V, 초록만 확인됨]. → 채널 모델, prior 유무, denoiser 종류, Onsager 계산법. 잔여 novelty 판정의 근거.
2. T. Wadayama, T. Takahashi, "Score-Based VAMP with Fisher-Information-Based Onsager Correction," arXiv:2601.07095 [V]. → Onsager를 Fisher 정보로 쓰는 방법, 우리 채널 denoiser에 적용 가능한지.
3. N. Zilberstein, A. Swami, S. Segarra, "Joint Channel Estimation and Data Detection in Massive MIMO Systems Based on Diffusion Models," ICASSP 2024, arXiv:2311.10311 [V]. → 채널 prior 형태, annealing 설정, 비부호화 심볼 score.
4. M. Arvinte, J. I. Tamir, "MIMO Channel Estimation Using Score-Based Generative Models," IEEE TWC 22(6), 2023 [M]. → 채널 score 모델의 아키텍처·도메인·학습 설정.
5. X. Kong, R. Brekelmans, G. Ver Steeg, "Information-Theoretic Diffusion," ICLR 2023, arXiv:2302.03792 [V]. → Tweedie/I-MMSE 관계, 노이즈 레벨-SNR 대응.

### Tier 2 — Lemma와 결합 구조
6. L. R. Bahl, J. Cocke, F. Jelinek, J. Raviv, "Optimal decoding of linear codes for minimizing symbol error rate," IEEE T-IT 1974 [M]. → BCJR 원문; 사후 marginal의 정확성.
7. J. Ma, L. Ping, "Orthogonal AMP," IEEE Access 2017 [M]; J. Ma, X. Yuan, L. Ping, "Turbo compressed sensing with partial DFT sensing matrix," IEEE SPL 2015 [M]. → 선형 모듈 ↔ denoiser의 extrinsic 교환 공식.
8. S. Rangan, P. Schniter, A. K. Fletcher, "Vector Approximate Message Passing," IEEE T-IT 65(10), 2019 [M]. → 분산 도메인 extrinsic 공식, divergence 항.
9. J. T. Parker, P. Schniter, V. Cevher, "Bilinear Generalized Approximate Message Passing — Part I," IEEE TSP 2014 [V]. → bilinear 결합의 뼈대, Onsager 항 형태.
10. S. Sarkar, A. K. Fletcher, S. Rangan, P. Schniter, "Bilinear Recovery Using Adaptive Vector-AMP," IEEE TSP 67(13), 2019 [M]. → 회전불변 채널용 bilinear VAMP.
11. M. Bayati, A. Montanari, "The dynamics of message passing on dense graphs, with applications to compressed sensing," IEEE T-IT 57(2), 2011 [V]. → Onsager 항의 유래.
12. "Random Walks with Tweedie," arXiv:2411.18702 [V]. → Tweedie ↔ MMSE ↔ score 배경.

### Tier 3 — 베이스라인과 비교 대상
13. Y. Sun et al., "Trainable Joint Channel Estimation, Detection and Decoding for MIMO URLLC Systems," IEEE TWC 23(9), 2024, arXiv:2404.07721 [V]. → 학습형 JCDD 베이스라인, positive feedback 논의.
14. M. Koller, B. Fesl, N. Turan, W. Utschick, "An asymptotically MSE-optimal estimator based on Gaussian mixture models," IEEE TSP 2022 [M]. → GMM prior 채널 추정 베이스라인.
15. M. Baur, B. Fesl, W. Utschick, VAE 기반 채널 추정 (IEEE TWC 2024 근방) [M, 제목 재확인]. → VAE prior 베이스라인.
16. R. Otnes, M. Tüchler, "Iterative Channel Estimation for Turbo Equalization of Time-Varying Frequency-Selective Channels," IEEE TWC 3(6), 2004 [V]. → 고전 code-aided 채널 추정 베이스라인.
17. Y. Choukroun, L. Wolf, "Denoising Diffusion Error Correction Codes," ICLR 2023, arXiv:2209.13533 [V]. → 확산 복호기 계열과의 구분.
18. N. Zilberstein et al., "Annealed Langevin Dynamics for Massive MIMO Detection," IEEE TWC 2023 (DOI 10.1109/TWC.2022.3221057) [V]. → route (b)의 원형.

### Tier 4 — 배경·분석
19. S. ten Brink, "Convergence behavior of iteratively decoded parallel concatenated codes," IEEE TCOM 49(10), 2001 [M]. → EXIT; turbo/LDPC 근사 오차 특성화.
20. B. Hassibi, B. M. Hochwald, "How much training is needed in multiple-antenna wireless links?," IEEE T-IT 49(4), 2003 [M]. → 파일럿 절감 주장의 기준 하한.
21. H.-A. Loeliger et al., "The factor graph approach to model-based signal processing," Proc. IEEE 2007 [M]. → 전체를 하나의 팩터 그래프로 쓰는 언어.
22. H. Cui, Z. Yu, J. Liu, "Sampling from the Random Linear Model via Stochastic Localization Up to the AMP Threshold," AISTATS 2025, arXiv:2407.10763 [V]. → route (b)의 이론적 배경(T3와 공유).
23. J. Hoydis et al., "Sionna," arXiv:2203.11854 [V]. → 시뮬레이션 도구, 5G LDPC/BCJR 구현.
24. T. Karras et al., "Elucidating the Design Space of Diffusion-Based Generative Models," NeurIPS 2022 [M]. → 노이즈 스케줄·전처리 설계.

---

## 7. 감시 키워드와 주기

월 1회, arXiv(cs.IT, eess.SP, cs.LG):
`score-based VAMP`, `LDPC coded nonlinear channel score`, `diffusion joint channel estimation decoding`, `decoder as denoiser diffusion`, `generative receiver coded`, `Tweedie BCJR`, `plug-and-play decoder`, `trellis denoiser diffusion`, `annealed turbo`.
감시 그룹: Wadayama–Takahashi, Segarra/Zilberstein, Schniter, Nachmani·Choukroun–Wolf, Utschick.
발견 시: scooping log에 기록 → 24시간 안에 §3.4(핸드오프) 시나리오 재판정 → 필요하면 교수님께 보고.

---

## 8. 마일스톤별 "완료"의 정의

| 마일스톤 | 완료 조건 |
|---|---|
| M1 문헌·판정 | 2604.19061의 세 답이 기록되고 잔여 novelty 시나리오가 확정됨 |
| M1 lemma | 정리·증명·가정이 한 페이지로 쓰이고, $K\le20$ 브루트포스 검증 통과 |
| M2 채널 score | Gaussian sanity 통과, denoising MSE 곡선 확보, 두 도메인 비교 완료 |
| M3 결합 | route (a) 동작, Onsager 포함, 반복별 NMSE 궤적이 단조 개선 |
| M4 첫 결과 | 4×4·16-QAM·컨볼루션에서 베이스라인 (i)(ii)(v) 대비 BLER 곡선 확보 |
| M5 ablation | §2 Phase 4의 다섯 ablation 완료, 이득 귀속 표 작성 |
| M6 확장 | LTE turbo·5G LDPC 결과, 근사 오차 그림 |
| M7 강건성 | mismatch·SNR 오차·파일럿 패턴 변화 결과 |
| M8 학회 원고 | 그림 1·2·3 확정, 주장 범위 확정 |

---

## 9. 기록 템플릿

**Decision log**
```
[2026-09-03] 결정: QAM은 심볼 단위 트렐리스로 간다.
이유: 비트 marginal 곱의 오차가 16-QAM에서 x dB 손실.
대안: 비트 marginal 근사(기각), 근거 실험: exp_0912.
```

**Scooping log**
```
[2026-09-01] arXiv 확인. 신규: 없음. 재확인: 2604.19061 v2 (변경 없음).
판정: 시나리오 A 유지.
```

**Open questions**
```
Q-07 (열림, Phase 2): 비등방 C_LS에 whitening vs 스칼라 근사 손실? 담당: 실험 exp_0915.
Q-03 (닫힘 2026-09-05): factor 2 규약 → 복소 차원당 σ²로 통일.
```

**Experiment log**
```
exp_0915 | 목적: 비등방 오차 처리 방식 비교 | 설정: 8×4, CDL-B, T=28, Tp=4, 16-QAM, conv ν=6
결과: whitening NMSE −x dB vs 스칼라 | 시드: 0–9 | 코드: commit abc123 | 결론/후속: Q-07 닫힘 후보
```

---

## 10. Claude에게 요청할 때 효과가 좋은 형식

- "이 항등식을 Gaussian prior 특수 경우로 환원해서 폐형과 비교하는 파이썬 검증 코드를 써 줘."
- "이 유도에서 깨질 수 있는 가정을 셋 꼽고, 각각을 깨는 반례를 만들어 줘."
- "이 결과를 '정확 / 근사 / 추측'으로 분류하고 근거를 한 줄씩 붙여 줘."
- "BiG-AMP Part I의 H-update 식을 원문 그대로 인용한 뒤 우리 표기로 번역해 줘. 기억으로 재구성하지 마."
- "이 실험 설계에서 리뷰어가 불공정하다고 지적할 부분을 찾아 줘."
- "이 주장이 틀렸다면 어떤 실험 결과가 그것을 보여 줄지 말해 줘."
- "지난 decision log를 읽고 오늘 결정이 그것과 모순되는지 확인해 줘."
