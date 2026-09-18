# Route (a) 설계 노트 v0 — SC-VAMP·BiG-AMP 원문 복사, 우리 표기 번역, 의사코드 (2026-09-17)

> 연구 노트. 모든 식에 출처 태그: **[복사: 논문 식번호]** (원문 그대로, 원 표기), **[번역]** (우리 표기, D-01), **[우리]** (새 유도). 상태: **정확 / 근사 / 추측**. 규약 D-01: 복소 per-entry 분산, Wirtinger, $L_c=2/\sigma^2$(real)$=4/\tau$(complex).

---

## 1. SC-VAMP (arXiv:2601.07095, Wadayama–Takahashi) — 원문 식

### 1.1 SISO 모듈의 score 표현 [복사: (1)–(7)]
$$\mathbf x_{\rm post}=\mathbf x_{\rm in}+v_{\rm in}\,s(\mathbf x_{\rm in}|\mathbf y)\ (1),\qquad \mathbf x_{\rm out}=\frac{\mathbf x_{\rm post}-\alpha(v_{\rm in})\mathbf x_{\rm in}}{1-\alpha(v_{\rm in})}\ (2),\qquad v_{\rm out}=\frac{\alpha(v_{\rm in})}{1-\alpha(v_{\rm in})}v_{\rm in}\ (3),$$
$$\alpha(v_{\rm in})=1-\frac{v_{\rm in}}{N}J_{X_{\rm in}|Y}\ (4),\qquad s(\mathbf x_{\rm in}|\mathbf y)\equiv\nabla_{\mathbf x_{\rm in}}\log p_{X_{\rm in}|Y}(\mathbf x_{\rm in}|\mathbf y)\ (5),\qquad J_{X_{\rm in}|Y}\equiv\mathbb E[\|s(\mathbf x_{\rm in}|\mathbf y)\|^2]\ (6),\qquad v_{\rm post}=v_{\rm in}\alpha(v_{\rm in})\ (7).$$
Denoiser module(관측 $\mathbf y$ 없음)은 무조건 score $s(\mathbf x_{\rm in})\equiv\nabla\log p_{X_{\rm in}}(\mathbf x_{\rm in})$ 사용. 입력 모델 $\mathbf X_{\rm in}=\mathbf X+\mathbf Z$, $\mathbf Z\sim\mathcal N(\mathbf 0,v_{\rm in}\mathbf I_N)$ (16), 실수.

### 1.2 2-module 알고리즘 [복사: (8)–(15)]
Module A(observation): $\mathbf x_{{\rm out},A}=\dfrac{v_{{\rm in},A}s(\mathbf x_{{\rm in},A}|\mathbf y)+(1-\alpha_A)\mathbf x_{{\rm in},A}}{1-\alpha_A}$ (8), $v_{{\rm out},A}=\dfrac{\alpha_A}{1-\alpha_A}v_{{\rm in},A}$ (9), $\alpha_A=1-\dfrac{v_{{\rm in},A}}{N}J_{X_{{\rm in},A}|Y}$ (10), $\mathbf x_{{\rm in},A}=\mathbf x_{{\rm out},B}$, $v_{{\rm in},A}=v_{{\rm out},B}$ (11). Module B(denoiser): (12)–(14) 동일 구조에 $s(\mathbf x_{\rm in})$, $J_{X_{\rm in}}$; (15) $\mathbf x_{{\rm in},B}=\mathbf x_{{\rm out},A}$, $v_{{\rm in},B}=v_{{\rm out},A}$. 초기화 $\mathbf x^{(0)}_{{\rm out},B}=\mathbf 0$, $v^{(0)}_{{\rm out},B}=v_{\rm init}$(prior 분산 또는 큰 값).

### 1.3 extrinsic의 유도 [복사: (24)–(26), (30)]
$$\frac1{v_{\rm post}}=\frac1{v_{\rm in}}+\frac1{v_{\rm out}}\ (24),\qquad \frac{\mathbf x_{\rm post}}{v_{\rm post}}=\frac{\mathbf x_{\rm in}}{v_{\rm in}}+\frac{\mathbf x_{\rm out}}{v_{\rm out}}\ (25),\qquad v_{\rm post}=v_{\rm in}\alpha(v_{\rm in})\ (26),\qquad \mathbf x_{\rm post}=\alpha\mathbf x_{\rm in}+(1-\alpha)\mathbf x_{\rm out}\ (30).$$
(Gaussian 사후 근사 + precision 합; EP projection과 동일.)

### 1.4 Onsager 계수의 두 유도 [복사: (31)–(33), (36)–(39)]
$$\alpha(v_{\rm in})\equiv\frac1N\mathbb E[\nabla_{\mathbf x_{\rm in}}\!\cdot\eta(\mathbf x_{\rm in})]=1+\frac{v_{\rm in}}{N}\mathbb E[\nabla\!\cdot s(\mathbf x_{\rm in}|\mathbf y)]\ (31)\ \xrightarrow{\text{Stein }\mathbb E[\nabla\cdot s]=-\mathbb E\|s\|^2}\ \alpha=1-\frac{v_{\rm in}}{N}J_{X_{\rm in}|Y}\ (33);$$
$$\mathrm{mmse}(v_{\rm in})=Nv_{\rm in}-v_{\rm in}^2J_{X_{\rm in}|Y}\ (36),\qquad v_{\rm post}=\frac1N\mathrm{mmse}=v_{\rm in}\Big(1-\frac{v_{\rm in}}{N}J\Big)=v_{\rm in}\alpha\ (37)\text{–}(39)$$
(conditional de Bruijn + I-MMSE). 주의: (31)–(33)은 **기대값** 항등식. VAMP의 표준 정의는 (43) $\alpha_{\rm VAMP}=\frac1N\mathrm{Tr}(\partial\eta/\partial\mathbf x_{\rm in})$(포인트별 divergence); 선형 Gaussian에서 두 정의 일치 (46).

### 1.5 선형 관측에서의 회복 [복사: (41), (44)–(45)]
$$\hat{\mathbf x}_{\rm LMMSE}=\Big(\tfrac1{v_{\rm in}}\mathbf I+\tfrac1{\sigma_w^2}\mathbf A^\top\mathbf A\Big)^{-1}\Big(\tfrac1{v_{\rm in}}\mathbf x_{\rm in}+\tfrac1{\sigma_w^2}\mathbf A^\top\mathbf y\Big)\ (41),\qquad \boldsymbol\Sigma_{\rm post}=(v_{\rm in}^{-1}\mathbf I+\sigma_w^{-2}\mathbf A^\top\mathbf A)^{-1},\quad \alpha_{\rm VAMP}=\frac1{Nv_{\rm in}}\mathrm{Tr}(\boldsymbol\Sigma_{\rm post})\ (45).$$

### 1.6 실무 추정 [복사: (47)–(48), (64)–(70)]
미니배치 $B$: $\hat J_\theta=\frac1B\sum_{i=1}^B\|s_\theta(\mathbf x^{(i)}_{\rm in}|\mathbf y^{(i)})\|^2$ (47), $\hat\alpha=1-\frac{v_{\rm in}}{N}\hat J_\theta$ (48). DSM 손실 $\mathcal L(\theta)=\mathbb E\big\|s_\theta(\mathbf x+\mathbf z)+\mathbf z/v_{\rm in}\big\|^2$ (66). 학습 후 $\mathbf x_{\rm post}=\mathbf x_{\rm in}+v_{\rm in}s_\theta(\mathbf x_{\rm in}|\mathbf y)$ (67), $J_\theta\simeq\frac1B\sum\|s_\theta\|^2$ (68)–(69), "실무에서는 VAMP 반복 중 네트워크 출력의 평균 제곱 노름으로 추정" (§V-B). 사전학습 denoiser에서 $\hat s=(\eta_{\rm opt}(\mathbf x_{\rm in})-\mathbf x_{\rm in})/v_{\rm in}$ (49).

### 1.7 Decoupling 가정 [§VI-A, D 요약]
SE·Onsager는 $\mathbf x_{\rm in}^{(t)}=\mathbf x+\mathbf e^{(t)}$, $\mathbf e^{(t)}\sim\mathcal N(\mathbf 0,v^{(t)}\mathbf I)$(i.i.d. 등방)를 전제. 성립 조건: (i) 좌표 간 통계적 대칭, (ii) 단거리 상관 억제(locally tree-like 또는 고차원 random mixing: RRI 행렬, random interleaver, random unitary modulation). 우리 채널 side는 $N=N_rN_t=32$로 작고 $\mathbf C_{\rm LS}$가 비등방 → 이 가정이 약함(§3.5, Q-07).

### 1.8 우리 표기로 번역 [번역] + 복소 Fisher 공식 [우리]
| SC-VAMP | 우리 (심볼 side) | 우리 (채널 side) |
|---|---|---|
| $\mathbf x_{\rm in},v_{\rm in}$ | $\mathbf r^{D}\in\mathbb C^{N}$, $\tau^{D}$ (pseudo-observation of $\mathbf x=\mathrm{vec}(\mathbf X_d)$) | $\hat{\mathbf Q}\in\mathbb C^{N_r\times N_t}$, $\nu^{q}$ |
| $\eta=\mathbf x_{\rm in}+v_{\rm in}s$ | Lemma 2: $\bar{\mathbf x}=\mathbb E[\mathbf x\mid\mathbf r^D]$ (BCJR) | $\hat{\mathbf H}^{\rm post}=\hat{\mathbf Q}+\nu^q\,s_\theta(\hat{\mathbf Q},\nu^q)$, $s_\theta\approx\nabla_{\mathbf Q^*}\log p_{\nu^q}$ |
| $\alpha$ | $\alpha^D=\bar v/\tau^D$ (**정확**, Lemma 2(c′)) | $\alpha^H=\frac1{N_rN_t}\mathrm{tr}\,\partial\hat{\mathbf H}^{\rm post}/\partial\hat{\mathbf Q}$ (Wirtinger $\partial/\partial q$) |
| (2)–(3) | $r^{D\to L}_n=\frac{\bar x_n-\alpha^D r^D_n}{1-\alpha^D}$, $\tau^{D\to L}=\frac{\alpha^D}{1-\alpha^D}\tau^D$ | 동일 형태로 $\hat{\mathbf H}^{H\to L}$, $\nu^{H\to L}$ |

**복소 Fisher 형 Onsager [우리, 정확].** 실수 stacking($2N$차원, 실수 분산 $\nu/2$)에 (31)–(33)을 적용하고 $\mathbf s_c=\nabla_{\mathbf q^*}\log p=\tfrac12(\mathbf s_{\rm r}+j\mathbf s_{\rm i})$, $\|\mathbf s_{\mathbb R}\|^2=4\|\mathbf s_c\|^2$, gradient field에서 curl 항 소멸을 쓰면
$$\alpha=\frac1{2N}\nabla_{\mathbb R}\!\cdot\eta_{\mathbb R}=1+\frac{\nu}{N}\mathrm{tr}\frac{\partial\mathbf s_c}{\partial\mathbf q}\quad\Rightarrow\quad \mathbb E[\alpha]=1-\frac{\nu}{N}J_c,\qquad J_c\equiv\mathbb E\|\nabla_{\mathbf q^*}\log p_\nu(\mathbf q)\|^2,\ N=\text{복소 entry 수}.$$
검증(exp_0917, Gaussian prior 폐형): $\mathbb E[\hat\alpha_{F1}]=\alpha_{\rm exact}=\frac1N\mathrm{tr}(\mathbf C(\mathbf C+\nu\mathbf I)^{-1})$ (0.9423 vs 0.9426 등). 부수 관찰 [우리, remark]: 학습된 $s_\theta$가 gradient field가 아니면 curl 항이 남아 Fisher 형과 divergence 형이 달라진다 — score 모델 품질 진단에 쓸 수 있음(**추측**, 측정 필요).

**소규모 $N$에서의 추정 분산 [우리, exp_0917].** $8\times4$($N=32$), 단일 표본 Fisher: $\mathrm{std}(\hat\alpha)=0.015\sim0.13$ → $v_{\rm ext}=\frac{\alpha}{1-\alpha}\nu$ 상대오차 $28\sim63\%$; Hutchinson $K=16$: $8\sim25\%$($\nu=0.01$에서는 $1-\alpha$가 작아 발산); $8\times8$: 각각 $20\sim45\%$, $6\sim10\%$; $32\times32$($N=1024$): $6\sim13\%$, $1\sim3\%$. 정확 trace: $2N$회 방향미분(64/128회) 또는 autodiff Jacobian trace 1회, 분산 0.

---

## 2. BiG-AMP Part I (arXiv:1310.2632v3, Parker–Schniter–Cevher) — 원문 식

### 2.1 모델과 가정 [복사: (1)–(3)]
$\mathbf A\in\mathbb R^{M\times N}$, $\mathbf X\in\mathbb R^{N\times L}$, $\mathbf Z\triangleq\mathbf A\mathbf X$, 관측 $\mathbf Y\in\mathbb R^{M\times L}$. **separable** prior/likelihood: $p_{\mathsf A}(\mathbf A)=\prod_m\prod_np_{\mathsf a_{mn}}(a_{mn})$ (1), $p_{\mathsf X}(\mathbf X)=\prod_n\prod_lp_{\mathsf x_{nl}}(x_{nl})$ (2), $p_{\mathsf Y|\mathsf Z}(\mathbf Y|\mathbf Z)=\prod_m\prod_lp_{\mathsf y_{ml}|\mathsf z_{ml}}(y_{ml}|z_{ml})$ (3). 복소도 허용(Table III 주석: (R10),(R12)의 conjugate; $\mathcal N$은 circular complex Gaussian).

### 2.2 Table III — The BiG-AMP Algorithm [복사, 전문]
정의: (D1) $p_{\mathsf z_{ml}|\mathsf p_{ml}}(z|\hat p;\nu^p)\triangleq\dfrac{p_{\mathsf y_{ml}|\mathsf z_{ml}}(y_{ml}|z)\mathcal N(z;\hat p,\nu^p)}{\int_{z'}p_{\mathsf y_{ml}|\mathsf z_{ml}}(y_{ml}|z')\mathcal N(z';\hat p,\nu^p)}$; (D2) $p_{\mathsf x_{nl}|\mathsf r_{nl}}(x|\hat r;\nu^r)\triangleq\dfrac{p_{\mathsf x_{nl}}(x)\mathcal N(x;\hat r,\nu^r)}{\int_{x'}p_{\mathsf x_{nl}}(x')\mathcal N(x';\hat r,\nu^r)}$; (D3) $p_{\mathsf a_{mn}|\mathsf q_{mn}}(a|\hat q;\nu^q)\triangleq\dfrac{p_{\mathsf a_{mn}}(a)\mathcal N(a;\hat q,\nu^q)}{\int_{a'}p_{\mathsf a_{mn}}(a')\mathcal N(a';\hat q,\nu^q)}$.
초기화: (I1) $\forall m,l:\hat s_{ml}(0)=0$; (I2) $\forall m,n,l$: choose $\nu^x_{nl}(1),\hat x_{nl}(1),\nu^a_{mn}(1),\hat a_{mn}(1)$.
for $t=1,\dots,T_{\max}$:
- (R1) $\forall m,l:\ \bar\nu^p_{ml}(t)=\sum_{n=1}^N|\hat a_{mn}(t)|^2\nu^x_{nl}(t)+\nu^a_{mn}(t)|\hat x_{nl}(t)|^2$
- (R2) $\forall m,l:\ \bar p_{ml}(t)=\sum_{n=1}^N\hat a_{mn}(t)\hat x_{nl}(t)$
- (R3) $\forall m,l:\ \nu^p_{ml}(t)=\bar\nu^p_{ml}(t)+\sum_{n=1}^N\nu^a_{mn}(t)\nu^x_{nl}(t)$
- (R4) $\forall m,l:\ \hat p_{ml}(t)=\bar p_{ml}(t)-\hat s_{ml}(t-1)\bar\nu^p_{ml}(t)$
- (R5) $\forall m,l:\ \nu^z_{ml}(t)=\mathrm{var}\{\mathsf z_{ml}\mid\mathsf p_{ml}=\hat p_{ml}(t);\nu^p_{ml}(t)\}$
- (R6) $\forall m,l:\ \hat z_{ml}(t)=\mathrm E\{\mathsf z_{ml}\mid\mathsf p_{ml}=\hat p_{ml}(t);\nu^p_{ml}(t)\}$
- (R7) $\forall m,l:\ \nu^s_{ml}(t)=(1-\nu^z_{ml}(t)/\nu^p_{ml}(t))/\nu^p_{ml}(t)$
- (R8) $\forall m,l:\ \hat s_{ml}(t)=(\hat z_{ml}(t)-\hat p_{ml}(t))/\nu^p_{ml}(t)$
- (R9) $\forall n,l:\ \nu^r_{nl}(t)=\big(\sum_{m=1}^M|\hat a_{mn}(t)|^2\nu^s_{ml}(t)\big)^{-1}$
- (R10) $\forall n,l:\ \hat r_{nl}(t)=\hat x_{nl}(t)\big(1-\nu^r_{nl}(t)\sum_{m=1}^M\nu^a_{mn}(t)\nu^s_{ml}(t)\big)+\nu^r_{nl}(t)\sum_{m=1}^M\hat a^*_{mn}(t)\hat s_{ml}(t)$
- (R11) $\forall m,n:\ \nu^q_{mn}(t)=\big(\sum_{l=1}^L|\hat x_{nl}(t)|^2\nu^s_{ml}(t)\big)^{-1}$
- (R12) $\forall m,n:\ \hat q_{mn}(t)=\hat a_{mn}(t)\big(1-\nu^q_{mn}(t)\sum_{l=1}^L\nu^x_{nl}(t)\nu^s_{ml}(t)\big)+\nu^q_{mn}(t)\sum_{l=1}^L\hat x^*_{nl}(t)\hat s_{ml}(t)$
- (R13) $\forall n,l:\ \nu^x_{nl}(t+1)=\mathrm{var}\{\mathsf x_{nl}\mid\mathsf r_{nl}=\hat r_{nl}(t);\nu^r_{nl}(t)\}$
- (R14) $\forall n,l:\ \hat x_{nl}(t+1)=\mathrm E\{\mathsf x_{nl}\mid\mathsf r_{nl}=\hat r_{nl}(t);\nu^r_{nl}(t)\}$
- (R15) $\forall m,n:\ \nu^a_{mn}(t+1)=\mathrm{var}\{\mathsf a_{mn}\mid\mathsf q_{mn}=\hat q_{mn}(t);\nu^q_{mn}(t)\}$
- (R16) $\forall m,n:\ \hat a_{mn}(t+1)=\mathrm E\{\mathsf a_{mn}\mid\mathsf q_{mn}=\hat q_{mn}(t);\nu^q_{mn}(t)\}$
- (R17) if $\sum_{m,l}|\bar p_{ml}(t)-\bar p_{ml}(t-1)|^2\le\tau_{\rm BiG\text{-}AMP}\sum_{m,l}|\bar p_{ml}(t)|^2$, stop.

AWGN 관측 $p_{\mathsf y_{ml}|\mathsf z_{ml}}=\mathcal N(y_{ml};z_{ml},\nu^w)$ (71)에서 $\nu^s_{ml}=\dfrac{1}{\nu^p_{ml}+\nu^w}$, $\hat s_{ml}=\dfrac{y_{ml}-\hat p_{ml}}{\nu^p_{ml}+\nu^w}$ (72). Scalar-variance: $\nu^r(t)\approx\dfrac{N}{\nu^s(t)\|\hat{\mathbf A}(t)\|_F^2}$ (76), $\nu^q(t)\approx\dfrac{N}{\nu^s(t)\|\hat{\mathbf X}(t)\|_F^2}$ (77). Damping $\beta(t)\in(0,1]$: (R1),(R3),(R7),(R8)을 (93)–(96) $\nu^p,\nu^s,\hat s$의 convex 혼합으로 대체하고, (97) $\underline x_{nl}(t{+}1)=\beta\hat x_{nl}(t{+}1)+(1-\beta)\underline x_{nl}(t)$, (98) $\underline a_{mn}(t{+}1)=\beta\hat a_{mn}(t{+}1)+(1-\beta)\underline a_{mn}(t)$을 (R9)–(R12)에서 사용[(R1)–(R2)에는 미사용]. 해석(§II-H): (R1)–(R2) plug-in $\mathbf P$, (R3)–(R4) Onsager 보정, (R5)–(R8) 잔차 $\hat{\mathbf S}$, (R9)–(R10) $\hat r_{nl}$은 "$\nu^r_{nl}$-분산 AWGN으로 손상된 $x_{nl}$의 관측", (R11)–(R12) $\hat q_{mn}$도 같은 해석.

### 2.3 우리 표기로 번역 [번역]
$\mathbf A\to\mathbf H$ ($M\to N_r$, $N\to N_t$), $\mathbf X\to\mathbf X=[\mathbf X_p\ \mathbf X_d]$ ($L\to T$), $\nu^w\to\sigma^2$, 첨자 $(m,n,l)\to(i,j,n)$ [수신 안테나 $i$, 송신 스트림 $j$, 심볼 시간 $n$]. 파일럿 열 $n\le T_p$: $\hat x_{jn}=x_{jn}$, $\nu^x_{jn}=0$ (prior가 점질량; (R13)–(R14)가 상수를 돌려줌). AWGN (72): $\nu^s_{in}=1/(\nu^p_{in}+\sigma^2)$, $\hat s_{in}=(y_{in}-\hat p_{in})/(\nu^p_{in}+\sigma^2)$.
- **채널 update = (R11),(R12),(R15),(R16)**: $\nu^q_{ij}=\big(\sum_n|\hat x_{jn}|^2\nu^s_{in}\big)^{-1}$, $\hat q_{ij}=\hat h_{ij}\big(1-\nu^q_{ij}\sum_n\nu^x_{jn}\nu^s_{in}\big)+\nu^q_{ij}\sum_n\hat x^*_{jn}\hat s_{in}$. 이것이 T1 §3.4의 비교 대상(Onsager 항 = 첫째 괄호의 감쇠 + 잔차 항; LOO의 1차 전개 주장은 T1의 일).
- **심볼 update = (R9),(R10),(R13),(R14)**: $\hat r_{jn}$, $\nu^r_{jn}$이 decoder module의 pseudo-observation. 우리는 (R13)–(R14)의 separable MMSE를 **Lemma 2 BCJR(비분리 code prior)**로 교체: 심볼별 $\tau_{jn}=\nu^r_{jn}$을 branch metric에 넣으면 Lemma 2는 그대로 성립(**정확**; 대각 공분산 Gaussian). 교체 시의 근사: BiG-AMP의 Onsager는 denoiser의 **대각** Jacobian(=$\nu^x_{jn}$, Lemma 2(c′)로 정확)만 사용하고 trellis가 만드는 비대각 상관은 무시 — AMP의 large-system 논리에 의존(**근사**, T1 LOO가 유한 $T$ 대안).
- **채널 denoiser (R15)–(R16)**: separable prior 대신 학습 score: $\hat{\mathbf H}(t{+}1)=\hat{\mathbf Q}+\nu^q s_\theta(\hat{\mathbf Q},\nu^q)$, $\nu^a=\nu^q\alpha^H$ (entry별 분산 대신 스칼라; scalar-variance (76)–(77)와 정합).
- 이렇게 얻는 "BiG-AMP + BCJR + score prior"는 **baseline group (ii)/(iv)의 AMP형 구현**이며 route (a)의 주 방식은 아래 §3의 EP/VAMP형.

---

## 3. Route (a) v0 — EP/VAMP형 3-module annealed turbo receiver [우리]

### 3.0 왜 AMP형이 아니라 EP형인가 (D-08 제안)
(1) $N_r\times N_t=8\times4$, $T\le56$: AMP Onsager는 large-system 근사, 소규모에서 진동·발산이 잦아 damping 의존(BiG-AMP §IV). (2) T1의 LOO는 EP cavity와 동일한 대상: 심볼 $n$ 검출에 쓰는 채널 belief = 다른 모든 factor의 site 곱 = $\hat{\mathbf H}^{\setminus n}$; 유한 $T$에서 정확. (3) 2604.19061의 3-module SC-VAMP도 EP형(extrinsic mean–variance)이며 그들의 Module C(LMMSE, known $\mathbf H$)를 "채널 불확실성을 marginalize한 LMMSE"로 일반화하는 것이 자연스럽다. BiG-AMP형은 baseline (ii).

### 3.1 Factor graph
변수: $\mathbf H$, $\{\mathbf x_n\}_{n>T_p}$. Factor: $f_n(\mathbf H,\mathbf x_n)=\mathcal{CN}(\mathbf y_n;\mathbf H\mathbf x_n,\sigma^2\mathbf I)$ ($n=1..T$; 파일럿 열은 $\mathbf x_n$ 기지), $p(\mathbf H)$ [학습 score], $P_{\mathcal C}(\mathbf X_d)$ [부호, 한 factor]. 이는 단일 latent Markov chain이 아니다(bilinear) → 2604.19061 §III-A의 chain 일반화로는 덮이지 않음(Q-08 닫힘 근거).

### 3.2 메시지와 모듈 (한 반복 $t$)
표기: 심볼 side pseudo-observation $(r^{L}_{jn},\tau^{L}_{jn})$ [linear→decoder], decoder extrinsic $(r^{D}_{jn},\tau^{D}_{jn})$ [decoder→linear]; 채널 side $(\hat{\mathbf Q},\nu^{q})$ [linear→score], $(\hat{\mathbf H}^{E},\nu^{E})$ [score→linear].

**Module D (심볼 denoiser, Lemma 2) — 정확.** 입력 $(r^L_{jn},\tau^L_{jn})$ 전체(파일럿 제외)를 symbol interleaver 역순으로 super-section trellis에 넣어 branch metric $-|r^L_{jn}-a|^2/\tau^L_{jn}$로 BCJR → $\bar x_{jn}$, $v_{jn}$ (정확 사후). Onsager $\alpha^D=\frac{1}{N}\sum_{jn}v_{jn}/\tau^L_{jn}$ (또는 심볼별 $\alpha^D_{jn}=v_{jn}/\tau^L_{jn}$ — Q-04′). Extrinsic [복사 (2)–(3)]: $r^D_{jn}=\frac{\bar x_{jn}-\alpha^D r^L_{jn}}{1-\alpha^D}$, $\tau^D=\frac{\alpha^D}{1-\alpha^D}\tau^L$. 대안(Q-04): LLR-domain extrinsic(정확 cavity marginal)에서 $(r^D,\tau^D)$를 재구성. Clip $\alpha\in[\epsilon,1-\epsilon]$ [2604.19061 §III-C3].

**Module H (채널 denoiser) — 근사(학습 score).** 입력 $(\hat{\mathbf Q},\nu^q)$. $\hat{\mathbf H}^{\rm post}=\hat{\mathbf Q}+\nu^q s_\theta(\hat{\mathbf Q},\nu^q)$ [복사 (1), 복소형 D-01]. $\alpha^H=\frac1{N_rN_t}\mathrm{tr}\,\partial\hat{\mathbf H}^{\rm post}/\partial\hat{\mathbf Q}$: **정확 autodiff trace(기본값, D-09 제안)**; Fisher 형 $1-\frac{\nu^q}{N}\|s_\theta\|^2$는 진단용/대규모용(exp_0917). Extrinsic [복사 (2)–(3)]: $\hat{\mathbf H}^{E}=\frac{\hat{\mathbf H}^{\rm post}-\alpha^H\hat{\mathbf Q}}{1-\alpha^H}$, $\nu^E=\frac{\alpha^H}{1-\alpha^H}\nu^q$. 학습 범위 밖 $\nu^q$는 clamp(동반 노트 함정 6).

**Module L_H (채널 side 선형) — 근사(soft-symbol linearization).** Gaussian belief $\mathbf H\sim\mathcal{CN}(\hat{\mathbf H}^E,\nu^E\mathbf I)$와 심볼 belief $x_{jn}\sim\mathcal{CN}(r^D_{jn},\tau^D_{jn})$(파일럿: 점질량) 아래 $\mathbf y_n\approx\mathbf H\mathbf r^D_n+\tilde{\mathbf w}_n$, $\tilde{\mathbf w}_n$의 분산 $\sigma^2+\sum_j\tau^D_{jn}\,\mathbb E|h_{ij}|^2$ [BiG-AMP (R1)/(R3)와 같은 moment 근사]. 행별 LMMSE:
$$\hat{\mathbf H}^{\rm post}_{L}=\big(\hat{\mathbf H}^E/\nu^E+\mathbf Y\mathbf D\bar{\mathbf X}^H\big)\big(\mathbf I/\nu^E+\bar{\mathbf X}\mathbf D\bar{\mathbf X}^H+\textstyle\sum_n d_n\mathrm{diag}(\boldsymbol\tau^D_n)\big)^{-1},\quad d_n=(\sigma^2+\textstyle\sum_j\tau^D_{jn}\mathbb E|h_{ij}|^2)^{-1},\ \mathbf D=\mathrm{diag}(d_n),$$
여기서 $\mathbb E|h_{ij}|^2=|\hat h^E_{ij}|^2+\nu^E$(belief의 2차 모멘트), $\mathbf G\triangleq\bar{\mathbf X}\mathbf D\bar{\mathbf X}^H+\sum_nd_n\mathrm{diag}(\boldsymbol\tau^D_n)$, 사후 행 공분산 $\mathbf C_{\rm post}=(\mathbf I/\nu^E+\mathbf G)^{-1}$ (비등방). Extrinsic to Module H [복사 (24)–(25), 행렬형]: $\mathbf C^{-1}_{q}=\mathbf C_{\rm post}^{-1}-\mathbf I/\nu^E=\mathbf G$, $\hat{\mathbf Q}=(\hat{\mathbf H}^{\rm post}_L\mathbf C_{\rm post}^{-1}-\hat{\mathbf H}^E/\nu^E)\mathbf C_q=\mathbf Y\mathbf D\bar{\mathbf X}^H\mathbf G^{-1}$.
**환원 [우리, 정확(linearization 안에서)]:** likelihood factor가 $\mathbf H$에 대해 Gaussian(선형화 후)이므로 EP site는 prior site와 무관 — Module L_H가 Module H에 보내는 pseudo-observation은 **가중 soft-symbol LS** $\hat{\mathbf Q}=\mathbf Y\mathbf D\bar{\mathbf X}^H\mathbf G^{-1}$, 오차 행 공분산 $\mathbf C_q=\mathbf G^{-1}$이며($d_n$을 통해서만 $\nu^E$에 약하게 의존), $d_n$ 상수이면 T1의 $\hat{\mathbf H}=\mathbf Y\bar{\mathbf X}^H\boldsymbol\Sigma^{-1}$, $\boldsymbol\Sigma=\bar{\mathbf X}\bar{\mathbf X}^H+\sum_n\mathrm{diag}(\mathbf v_n)$와 일치. Prior site $(\hat{\mathbf H}^E,\nu^E)$는 L_X가 쓰는 사후·LOO belief에만 들어간다. 등방화(Q-07): v0는 $\nu^q=\mathrm{tr}(\mathbf C_q)/N_t$ 스칼라 근사; 대안 whitening / colored-noise 학습.

**Module L_X (심볼 side 선형) — 근사(EP-LMMSE).** 심볼 $n$ 검출용 채널 belief는 cavity = LOO [T1 §3.2, **정확**]: $\hat{\mathbf H}^{\setminus n}$, $\mathbf C^{\setminus n}$ (Sherman–Morrison, $O(N_t^2)$/심볼; prior site $\hat{\mathbf H}^E,\nu^E$를 $\boldsymbol\Sigma$에 포함). T1 §3.3: $p(\mathbf y_n|\mathbf x_n)=\mathcal{CN}(\hat{\mathbf H}^{\setminus n}\mathbf x_n,(\sigma^2+\mathbf x_n^H\mathbf C^{\setminus n}\mathbf x_n)\mathbf I)$. EP-LMMSE(분산을 $\sigma_n^2=\sigma^2+\mathrm{tr}(\mathbf C^{\setminus n}(\mathbf r^D_n\mathbf r^{DH}_n+\mathrm{diag}(\boldsymbol\tau^D_n)))$로 상수화 — **근사**, PSK·등방에서 정확):
$$\hat{\mathbf x}^{\rm post}_n=\mathbf r^D_n+\mathbf T_n\hat{\mathbf H}^{\setminus nH}\big(\hat{\mathbf H}^{\setminus n}\mathbf T_n\hat{\mathbf H}^{\setminus nH}+\sigma_n^2\mathbf I\big)^{-1}(\mathbf y_n-\hat{\mathbf H}^{\setminus n}\mathbf r^D_n),\qquad \boldsymbol\Sigma^{\rm post}_n=\mathbf T_n-\mathbf T_n\hat{\mathbf H}^{\setminus nH}(\cdots)^{-1}\hat{\mathbf H}^{\setminus n}\mathbf T_n,\ \mathbf T_n=\mathrm{diag}(\boldsymbol\tau^D_n).$$
Extrinsic to Module D [복사 (24)–(25), entry별]: $1/\tau^L_{jn}=1/[\boldsymbol\Sigma^{\rm post}_n]_{jj}-1/\tau^D_{jn}$, $r^L_{jn}=\tau^L_{jn}\big(\hat x^{\rm post}_{jn}/[\boldsymbol\Sigma^{\rm post}_n]_{jj}-r^D_{jn}/\tau^D_{jn}\big)$. 음의 분산 guard: $\tau^L\leftarrow\max(\tau^L,\epsilon)$ 또는 스칼라화 $\tau^L_n=\frac1{N_t}\sum_j$.
2604.19061 (16)–(17)과의 관계: $\mathbf C^{\setminus n}=\mathbf 0$(known $\mathbf H$), $\mathbf T_n=\tau\mathbf I$이면 그들의 Module C와 일치(**정확한 환원**).

### 3.3 스케줄 = 메시지 분산 (핸드오프 §3.3)
Module D가 보는 노이즈 레벨은 $\sigma_t^2\equiv\tau^L$(복소 per-entry; Lemma 1 호출 시 $\tau^L/2$), $L_c(t)=4/\tau^L$. 즉 annealing 스케줄은 설계 변수가 아니라 L_X가 내는 $\tau^L(t)$의 궤적이다. 고정 기하 스케줄은 ablation (5).

### 3.4 반복 골격 (의사코드)
```
입력: Y, X_p, σ², s_θ, 코드/trellis, interleaver π, T_max, damping β, ε
초기화: r^D=0, τ^D=1 (데이터; 비정보 prior, 2604.19061 §III-C와 동일), 파일럿 점질량;
        ν^E=ν_init(큰 값, SC-VAMP §III-B), Ĥ^E=0
for t = 1..T_max:
  [L_H]  (Ĥ_post, C_post) ← LMMSE(Y, r^D, τ^D, Ĥ^E, ν^E, σ²);  (Q̂, C_q) ← extrinsic;  ν^q ← tr(C_q)/N_t   (Q-07)
  [H]    Ĥ_post ← Q̂ + ν^q s_θ(Q̂, ν^q);  α^H ← (1/N) tr ∂Ĥ_post/∂Q̂ (autodiff);  (Ĥ^E, ν^E) ← extrinsic (2)-(3)
  [L_X]  for n > T_p: (Ĥ^{\n}, C^{\n}) ← LOO downdate (T1);  (x̂_post_n, Σ_post_n) ← EP-LMMSE;  (r^L_n, τ^L_n) ← extrinsic (24)-(25)
  [D]    (x̄, v) ← super-section BCJR(π^{-1}(r^L), τ^L)  [Lemma 2];  α^D ← mean(v/τ^L);  (r^D, τ^D) ← extrinsic (2)-(3)
  damping: r^D ← β r^D + (1-β) r^D_prev (τ^D 동일);  CRC 통과 또는 |Δ x̄| < tol 이면 stop
출력: 경판정 x̂ = argmax_a P_n(a) (또는 정보 비트 LLR), Ĥ_post, 분산 궤적 {τ^L(t), ν^q(t)} (T3·스케줄 그림용)
```
복잡도/반복: L_H $O(N_rN_t^2+N_t^3)$, L_X $O(T(N_t^3+N_rN_t^2))$, D: BCJR 1회 $O(T_dN_t\,2^{\nu}2^{q}/q)$, H: score net 1회 + trace($2N_rN_t$ JVP 또는 Jacobian 1회). 학습 비용 제외(명시).

### 3.5 정확/근사 경계 (route (a) v0)
정확: Module D(Lemma 2), LOO cavity(T1), extrinsic 대수 (24)–(25), 환원 특수경우(known $\mathbf H$ → 2604.19061 Module C; $\nu^E\to\infty$ → soft-symbol LS). 근사: Gaussian message 가정(A3), L_H의 soft-symbol linearization, L_X의 분산 상수화, Module H의 학습 score와 스칼라 $\nu^q$(비등방 무시), damping. 추측: 반복 수렴(T3), 스케줄 이점(하위 질문 3).

---

## 4. 제안 결정 (승인 대기) 및 열린 질문 갱신
- **D-08** route (a) = EP/VAMP형(§3); BiG-AMP형(§2.3)은 baseline (ii). 근거: §3.0.
- **D-09** 채널 denoiser Onsager = 정확 autodiff Jacobian trace(소규모 $N$); Fisher 형은 진단/대규모/배치용. 근거: exp_0917.
- **Q-08 닫힘 제안**: bilinear는 chain이 아님; 2604.19061 Module C는 known $\mathbf H$ 전제(eq. (16)–(17)).
- **Q-05**: 절반 닫힘(방법 선택 D-09); 남은 것 = 학습 score의 curl 진단(추측).
- **Q-04′(신규)**: Module D의 $\alpha^D$를 블록 평균으로 할지 심볼별로 할지(EP 정확도 vs 안정성).
- **Q-15(신규)**: L_H의 extrinsic 행 공분산 $\mathbf C_q$가 비정정(negative definite 방향)이 될 때의 guard.

## 5. 다음 실험 제안
- **exp_0918**: Gaussian 채널 prior(폐형 score, Kronecker $\mathbf C$)로 route (a) v0를 numpy 구현, $4\times4$, BPSK/QPSK, $(133,171)_8$, $T=28$, $T_p\in\{2,4\}$: (i) 반복별 NMSE·$\tau^L$ 궤적 단조 개선 여부(M3 완료 조건), (ii) ablation (3) extrinsic→a-posteriori 채널 되먹임의 floor(T1 F2 재현), (iii) Q-04 두 extrinsic 도메인 비교, (iv) Q-07 스칼라 vs whitening. 학습 없이 결합 버그를 격리하는 것이 목적; baseline (iv) "2604.19061 구조 + Gaussian prior"도 동시에 확보.
