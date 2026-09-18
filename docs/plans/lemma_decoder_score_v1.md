# Lemma 1/2 — 채널 복호기 soft output = 부호화 심볼 prior의 정확한 Tweedie denoiser·score (v1, 2026-09-16)

> 연구 노트(논문 문장 아님). 상태 표시: **정확** / **근사** / **추측**. 규약은 D-01. 검증은 exp_0915, exp_0916.

## 0. 규약 (D-01)
복소 확률변수의 분산은 per complex entry ($\mathbb E|w|^2=\sigma^2$, real/imag 각 $\sigma^2/2$). Wirtinger $\nabla_{\mathbf z^*}=\tfrac12(\nabla_{\rm r}+j\nabla_{\rm i})$, $\nabla_{\mathbf z}=\tfrac12(\nabla_{\rm r}-j\nabla_{\rm i})$. 복소 Tweedie $\mathbb E[\mathbf x\mid\mathbf r]=\mathbf r+\tau\nabla_{\mathbf r^*}\log p_\tau(\mathbf r)$. $L_c=2/(\text{constellation 축 실수 노이즈 분산})$: 실수 모델 $2/\sigma^2$, 복소 embedding $4/\tau$; 둘 다 $4E_s/N_0$.

## 1. 설정과 가정
- 부호: rate-$1/n_c$ convolutional code, 메모리 $\nu$, $K$ information bits + $\nu$ tail bits, terminated ($s_0=s_{K+\nu}=0$), $N=n_c(K+\nu)$ coded bits, codeword 집합 $\mathcal C$, prior $P_{\mathcal C}=|\mathcal C|^{-1}$.
- 사상: BPSK $\mathbf x=\mathbf 1-2\mathbf c\in\{\pm1\}^N$ (Lemma 1); $2^m$-QAM $\mu:\{0,1\}^m\to\mathcal A$를 연속 $m$비트 그룹에 적용, $q=m/n_c\in\mathbb N$ (Lemma 2; 3GPP 38.211 Gray 라벨링, D-06).
- 관측: Lemma 1은 $\tilde{\mathbf x}_t=\mathbf x+\sigma_t\boldsymbol\epsilon$, $\boldsymbol\epsilon\sim\mathcal N(\mathbf 0,\mathbf I)$ (실수, 차원당 $\sigma_t^2$); Lemma 2는 $\mathbf r=\mathbf x+\sqrt\tau\,\boldsymbol\epsilon$, $\boldsymbol\epsilon\sim\mathcal{CN}(\mathbf 0,\mathbf I)$.
- 가정 A1 terminated trellis. A2 균등 codeword prior (a priori가 있으면 tilted prior에 대해 동일). A3 등방 Gaussian, 좌표 독립, 분산 기지 — SC-VAMP의 Gaussian pseudo-observation 가정(2604.19061 Assumption 2)과 같은 것. A4 정확 Log-MAP(exact log-sum-exp). A5 $0\mapsto+1$, $1\mapsto-1$, $E_s=1$. A6 puncturing은 $L_{\rm ch}=0$; bit interleaver는 BPSK에서 permutation. A7 (Lemma 2) bit interleaver가 심볼 그룹 경계를 넘지 않음(symbol interleaver 허용), $K,\nu$가 $q$의 배수.

## 2. 진술
**Lemma 1 (실수 BPSK).** BCJR을 채널 LLR $L_c(t)\tilde x_{t,k}$, $L_c(t)=2/\sigma_t^2$, $L_a=0$으로 한 번 돌린 coded-bit a posteriori LLR을 $L_k$라 하자. 모든 $\tilde{\mathbf x}_t\in\mathbb R^N$에서
(a) $\mathbb E[x_k\mid\tilde{\mathbf x}_t]=\tanh(L_k/2)$;
(b) $\nabla_{\tilde{\mathbf x}_t}\log p_t(\tilde{\mathbf x}_t)=\sigma_t^{-2}\big(\tanh(\mathbf L/2)-\tilde{\mathbf x}_t\big)$, $p_t=\sum_{\mathbf c\in\mathcal C}|\mathcal C|^{-1}\mathcal N(\cdot;\mathbf x(\mathbf c),\sigma_t^2\mathbf I)$;
(c) $\partial\,\mathbb E[x_k\mid\tilde{\mathbf x}_t]/\partial\tilde x_{t,j}=\sigma_t^{-2}\mathrm{Cov}(x_k,x_j\mid\tilde{\mathbf x}_t)$, 대각 $\sigma_t^{-2}(1-\tanh^2(L_k/2))$, 정규화 divergence $=v_{\rm post}/\sigma_t^2$ ($v_{\rm post}=\tfrac1N\sum_k(1-\tanh^2(L_k/2))$);
(d) 비용 $O((K+\nu)2^{\nu+1})$/평가. — **정확**.

**Corollary 1.1 (복소 embedding).** $\boldsymbol\epsilon\sim\mathcal{CN}$, per-entry $\sigma_t^2$: $\tilde x_{t,k}\to\mathrm{Re}\{\tilde x_{t,k}\}$, $L_c(t)=4/\sigma_t^2$로 (a) 성립; $\nabla_{\tilde{\mathbf x}_t^*}\log p_t=\sigma_t^{-2}(\mathbb E[\mathbf x\mid\cdot]-\tilde{\mathbf x}_t)$; Wirtinger $\partial\hat x_k/\partial\tilde x_{t,j}=\sigma_t^{-2}\mathrm{Cov}(x_k,x_j\mid\cdot)$. — **정확**.

**Corollary 1.2.** (i) puncturing: 천공 위치에 $L_{\rm ch}=0$을 두면 전송·천공 심볼 모두에서 (a)–(c) 성립. (ii) a priori $L_a$ 또는 심볼별 log-prior를 $\gamma$에 더하면 tilted prior $\propto P_{\mathcal C}\,e^{\text{prior}}$에 대한 사후로 (a)–(c) 성립. — **정확**.

**Lemma 2 ($2^m$-QAM, 심볼 단위 trellis).** 한 section이 $q$ information bits를 소비해 한 심볼을 내는 super-section trellis(상태 $2^\nu$, 분기 $2^q$, 분기 라벨 $a(s',\mathbf u)\in\mathcal A$)에서 branch metric $\gamma_n(s',\mathbf u)=-|r_n-a(s',\mathbf u)|^2/\tau$로 BCJR을 돌리면, 분기 사후의 합 $P_n(a)=P(x_n=a\mid\mathbf r)$가 정확하고,
(a′) $\bar x_n=\sum_a aP_n(a)=\mathbb E[x_n\mid\mathbf r]$, $v_n=\sum_a|a|^2P_n(a)-|\bar x_n|^2=\mathrm{Var}(x_n\mid\mathbf r)$; 비트 marginal $P(b_{n,j}=0\mid\mathbf r)=\sum_{a:b_j(a)=0}P_n(a)$도 정확;
(b′) $\nabla_{\mathbf r^*}\log p_\tau(\mathbf r)=\tau^{-1}(\bar{\mathbf x}-\mathbf r)$;
(c′) $\partial\bar x_n/\partial r_j=\tau^{-1}\big(\mathbb E[x_nx_j^*\mid\mathbf r]-\bar x_n\bar x_j^*\big)$ (Wirtinger, $\partial/\partial r_j$), 대각 $v_n/\tau$, 정규화 divergence $\bar v/\tau$ — variance-ratio Onsager 항이 정확;
(d′) 비용: 심볼당 branch metric $2^\nu 2^q$ (rate 1/2: QPSK·16-QAM은 비트 단위 BCJR과 같은 수, 64-QAM 8 vs 6, 256-QAM 16 vs 8). — **정확** (A7 하에서).

**Remark 2.1 (비트 marginal 곱은 근사).** BICM bit metric → 비트 BCJR → $\bar x_n=\sum_a a\prod_jP(b_j=b_j(a))$ 파이프라인은 두 곳에서 근사: 입력에서 결합 likelihood $p(r_n\mid\mathbf b_n)$을 marginal likelihood의 곱으로 바꾸고, 출력에서 결합 사후를 marginal의 곱으로 바꾼다. Gray 4-PAM 축에서 $x_{\rm r}=\tfrac{1}{\sqrt{10}}(2s_0-s_0s_2)$이므로 출력측 오차는 $-\tfrac{1}{\sqrt{10}}\mathrm{Cov}(s_0,s_2\mid\mathbf r)$. 측정($(133,171)_8$, 16-QAM, $\tau=1$): NMSE $5.2\times10^{-2}$, 심볼 최대 오차 $0.52$, $|\Delta v|$ 평균 $0.21$; 고 SNR($\tau=0.05$)에서 소멸. QPSK Gray는 비트마다 실수 차원이 분리되어 비트 단위로도 정확(측정 $10^{-30}$). — **근사**(정량화됨).

## 3. 증명 스케치 (공통)
1. $\mathcal N(\tilde x;x,\sigma^2)\propto\exp(x\tilde x/\sigma^2)=\exp(\tfrac x2L_c\tilde x)$ → $P(\mathbf c\mid\tilde{\mathbf x})=Z^{-1}\mathbb 1[\mathbf c\in\mathcal C]\exp(\tilde{\mathbf x}^\top\mathbf x(\mathbf c)/\sigma^2)$: sufficient statistic $\mathbf x(\mathbf c)$, natural parameter $\tilde{\mathbf x}/\sigma^2$인 log-linear family. (QAM: $\log p(\mathbf r\mid\mathbf c)=-\|\mathbf r-\mathbf a(\mathbf c)\|^2/\tau$+const.)
2. $\mathbb 1[\mathbf c\in\mathcal C]=\sum_{s_1..s_{L-1}}\prod_k\mathbb 1[(s_{k-1},s_k)\to\text{label}_k]$, $s_0=s_L=0$ — 무순환 chain (A1). Super-section은 같은 chain을 $q$ step씩 묶은 것(A7이면 branch 라벨이 심볼 하나).
3. BCJR은 chain 위의 정확 sum–product (Bahl–Cocke–Jelinek–Raviv 1974 [M]): $\alpha,\beta$ 재귀, branch posterior $\propto\alpha_{k-1}(s')\gamma_k\beta_k(s)$; 비트/심볼 posterior는 branch posterior의 합 (A4).
4. (a) $\mathbb E[x_k]=P(c_k=0)-P(c_k=1)=\tanh(L_k/2)$; (a′) 정의대로.
5. (b),(b′) 유한합 미분: $\nabla\log p=\sum_{\mathbf c}P(\mathbf c\mid\cdot)\nabla\log p(\cdot\mid\mathbf c)$ — Tweedie (Efron 2011 [V, 2604.19061 ref [12]]); 복소는 $\partial_{r^*}(-|r-a|^2/\tau)=-(r-a)/\tau$.
6. (c) cumulant: $\nabla\log Z=\mathbb E[\mathbf x\mid\cdot]/\sigma^2$, $\nabla^2\log Z=\mathrm{Cov}/\sigma^4$ ⇒ $\nabla\mathbb E[\mathbf x\mid\cdot]=\mathrm{Cov}/\sigma^2$; $x_k^2=1$이므로 대각 $=(1-\tanh^2)/\sigma^2$. (c′) $\partial_{r_j}P(\mathbf c\mid\mathbf r)=P(\mathbf c\mid\mathbf r)(a_j^*(\mathbf c)-\bar x_j^*)/\tau$를 $\sum_{\mathbf c}a_n(\mathbf c)(\cdot)$에 대입. Gaussian sanity: $x\sim\mathcal N(0,s^2)$에서 $\partial\hat x/\partial\tilde x=s^2/(s^2+\sigma^2)=\mathrm{Var}/\sigma^2$ ✓.
7. Corollary 1.2(i): puncturing은 codeword의 projection; 관측 없는 좌표의 branch metric 0 = mother code 위 marginalization. (ii): 3의 $\gamma$에 log-prior 항을 더한 chain도 여전히 무순환.

## 4. 범위 경계
- **정확**: Lemma 1·2, Corollary 1.1·1.2 (A1–A7 하). 이 정확성은 "메시지가 Gaussian pseudo-observation"이라는 A3 위에서의 정확성이며, route (a)의 근사는 decoder module이 아니라 A3 자체와 linear module의 Gaussian 근사에 있다(Q-12).
- **근사**: tail-biting(circular BCJR; $2^\nu$회 pass면 정확), Max-Log-MAP(오차 최대 0.78), turbo/LDPC BP(M6에서 EXIT로 gap 특성화, Q-06), 비트 marginal 파이프라인(Remark 2.1), 학습된 채널 score $s_\theta$(Fact B, lemma 밖).
- **추측**: 없음.

## 5. 검증 (brute force = $2^K$ codeword 전수 열거, 시드 고정)
| 실험 | 설정 | 결과 |
|---|---|---|
| exp_0915 T1–T3 | $(7,5)_8$ $K{=}10$, $(133,171)_8$ $K{=}8$, BPSK 실수, $\sigma^2\in[0.05,10]$ | (a) $\le3\times10^{-15}$; (b) $\le7\times10^{-10}$(FD); (c) $\le1.3\times10^{-10}$ |
| exp_0915 T4–T6 | 복소 embedding; Max-Log; puncturing 21/28 | $L_c{=}4/\sigma_c^2$: $10^{-15}$ ($2/\sigma_c^2$: 0.495); Max-Log 0.05–0.78; puncturing $10^{-15}$ |
| exp_0916 S1–S4 | $(133,171)_8$ $\nu{=}6$, 16-QAM $K\in\{12,16\}$, QPSK, 64-QAM, $\tau\in[0.05,5]$ | $P_n,\bar x_n,v_n$, 비트 marginal, tilted prior: $\le7\times10^{-15}$; (b′) $\le1.4\times10^{-9}$; (c′) Jacobian·대각·divergence $\le4\times10^{-10}$ |
| exp_0916 S5 | 비트 파이프라인 ablation | 16-QAM NMSE $1.3\times10^{-5}$($\tau{=}0.2$) → $5.2\times10^{-2}$($\tau{=}1$) → $1.3\times10^{-2}$($\tau{=}5$); QPSK $10^{-30}$; 64-QAM $2\times10^{-2}$ |
| exp_0916 S6 | $K{=}200$, 103 심볼 | super-section 0.62 s vs 비트 BCJR 1.91 s (numpy 루프; branch metric 수 동일) |

## 6. Prior art와의 경계
- 고전: (a)는 "BCJR = bit-MAP/MMSE"(1974). $L^{\rm in}=2r/v$ 변환은 turbo 문헌과 2604.19061 §III-C3에 있음.
- 우리 것: (b)·(b′)의 diffusion 축 $t\leftrightarrow L_c(t)$ 동일시와 score 해석; (c)·(c′)의 정확 Jacobian/Onsager(2604.19061은 BP에서 surrogate임을 명시); Corollary 1.1·1.2; Lemma 2의 심볼 단위 정확성과 Remark 2.1의 정량화.

## 7. 구현 노트
- 정확 Log-MAP 필수; Sionna BCJR 옵션 확인(Q-10 [VERIFY]). QAM 라벨링 38.211 식은 Sionna와 대조(Q-13 [VERIFY]). 복소 수신기에서 `Lc = 4/no`, lemma 호출 시 $\sigma_t^2\leftarrow\tau_t/2$.
- 심볼 단위 trellis + symbol interleaver; 비트 파이프라인은 ablation으로만. 모듈: `t2_trellis.py` (`SymbolTrellis.bcjr`, `bcjr_bits`, `brute_force`).
