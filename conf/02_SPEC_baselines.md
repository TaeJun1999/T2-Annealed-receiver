# 02 — Baseline 설계 지침 (R3, R4)

> 표기: bit $0\mapsto+1,\ 1\mapsto-1$; $L_c=2/\sigma^2$; $\mathbf Y=\mathbf H\mathbf X+\mathbf W$, $\mathbf H\in\mathbb C^{N_r\times N_t}$, $\mathbf X=[\mathbf X_p\ \mathbf X_d]\in\mathbb C^{N_t\times T}$; soft symbol $\bar x_n, v_n$. 태그 **정확 / 근사 / 추측 / 측정**.
>
> **이 문서에는 코드가 없다.** 구조와 식만 있다. 구현은 Claude Code가 한다.

---

## 0. 공통 — 복소 규약 (가장 흔한 버그)

두 원문 모두 **실수** 모델이다(BiG-AMP은 복소 일반형을 병기하지만 서술은 실수 기준, SC-VAMP 3-module은 BPSK 실수 전용). 우리는 복소다.

- 이 프로젝트의 확정 규약(Q-03, 닫힘): **복소 차원당 잡음 분산 $\sigma^2$.**
- 전치는 전부 Hermitian $(\cdot)^H$로 바꾼다.
- LLR ↔ pseudo-observation 변환의 factor 2는 **직접 유도하지 말고** `Demo/`의 기존 헬퍼를 쓴다. 기존 헬퍼를 못 찾으면 직접 만들되 `07_SPEC_tests.md` S6(왕복 항등)으로 잠근다.
- QPSK Gray: $x=(b_1+jb_2)/\sqrt2$, $b_k=\pm1$이면 $\mathbb E[x]=(\bar b_1+j\bar b_2)/\sqrt2$, $\operatorname{Var}(x)=\tfrac12[(1-\bar b_1^2)+(1-\bar b_2^2)]$. **이미 구현돼 있으면 재구현하지 말 것.**

---

## 1. R3 — BiG-AMP + BCJR

### 1.1 모듈 구조 (스켈레톤)

`conf/code/`에 다음 책임을 갖는 단위를 만든다. 이름은 자유.

| 단위 | 책임 | 입력 | 출력 | 불변식 |
|---|---|---|---|---|
| BiG-AMP 코어 | Table III 한 반복 | 현재 상태 $(\hat{\mathbf H},\nu^h,\hat{\mathbf X},\nu^x,\hat{\mathbf S})$, $\mathbf Y$, $\sigma^2$, 심볼 prior, 채널 prior | 갱신된 상태 | 모든 분산 $>0$, 유한 |
| 심볼 prior 어댑터 | decoder extrinsic LLR → (R13)(R14)의 $p_{x_{nl}}$ | LLR, 파일럿 마스크 | $(\hat x_{nl},\nu^x_{nl})$ | 파일럿 열은 $\nu^x=0$ |
| 외부 turbo 루프 | BiG-AMP $T_{\rm in}$회 → 심볼 LLR 추출 → BCJR → extrinsic → prior 갱신 | | 반복별 지표 | 외부 반복 = 16 |
| 진단 | 발산·clip·정지조건 집계 | | 카운터 | 기록만, 숨기지 않음 |

### 1.2 원문 알고리즘 [V: arXiv:1310.2632v3 Table III 본문 확인]

원문 표기 $\mathbf Z=\mathbf A\mathbf X$, $\mathbf A\in\mathbb C^{M\times N}$, $\mathbf X\in\mathbb C^{N\times L}$. **우리 사상:** $\mathbf A\to\mathbf H$, $M\to N_r$, $N\to N_t$, $L\to T$, $\nu^w\to\sigma^2$. 단계 번호는 원문 유지.

초기화: $\hat s_{ml}(0)=0$; $\nu^x_{nl}(1),\hat x_{nl}(1),\nu^h_{mn}(1),\hat h_{mn}(1)$ 선택.

$t=1,\dots,T_{\max}$:

$$\bar\nu^p_{ml}(t)=\sum_{n=1}^{N_t}\Big(|\hat h_{mn}(t)|^2\nu^x_{nl}(t)+\nu^h_{mn}(t)|\hat x_{nl}(t)|^2\Big)\tag{R1}$$
$$\bar p_{ml}(t)=\sum_{n=1}^{N_t}\hat h_{mn}(t)\hat x_{nl}(t)\tag{R2}$$
$$\nu^p_{ml}(t)=\bar\nu^p_{ml}(t)+\sum_{n=1}^{N_t}\nu^h_{mn}(t)\nu^x_{nl}(t)\tag{R3}$$
$$\hat p_{ml}(t)=\bar p_{ml}(t)-\hat s_{ml}(t-1)\,\bar\nu^p_{ml}(t)\tag{R4}$$
$$\nu^z_{ml}(t)=\operatorname{var}\{z_{ml}\mid p_{ml}=\hat p_{ml}(t);\nu^p_{ml}(t)\}\tag{R5}$$
$$\hat z_{ml}(t)=\mathbb E\{z_{ml}\mid p_{ml}=\hat p_{ml}(t);\nu^p_{ml}(t)\}\tag{R6}$$
$$\nu^s_{ml}(t)=\big(1-\nu^z_{ml}(t)/\nu^p_{ml}(t)\big)/\nu^p_{ml}(t)\tag{R7}$$
$$\hat s_{ml}(t)=\big(\hat z_{ml}(t)-\hat p_{ml}(t)\big)/\nu^p_{ml}(t)\tag{R8}$$
$$\nu^r_{nl}(t)=\Big(\sum_{m=1}^{N_r}|\hat h_{mn}(t)|^2\nu^s_{ml}(t)\Big)^{-1}\tag{R9}$$
$$\hat r_{nl}(t)=\hat x_{nl}(t)\Big(1-\nu^r_{nl}(t)\sum_{m}\nu^h_{mn}(t)\nu^s_{ml}(t)\Big)+\nu^r_{nl}(t)\sum_{m}\hat h^{*}_{mn}(t)\hat s_{ml}(t)\tag{R10}$$
$$\nu^q_{mn}(t)=\Big(\sum_{l=1}^{T}|\hat x_{nl}(t)|^2\nu^s_{ml}(t)\Big)^{-1}\tag{R11}$$
$$\hat q_{mn}(t)=\hat h_{mn}(t)\Big(1-\nu^q_{mn}(t)\sum_{l}\nu^x_{nl}(t)\nu^s_{ml}(t)\Big)+\nu^q_{mn}(t)\sum_{l}\hat x^{*}_{nl}(t)\hat s_{ml}(t)\tag{R12}$$
$$\nu^x_{nl}(t{+}1)=\operatorname{var}\{x_{nl}\mid r_{nl}=\hat r_{nl}(t);\nu^r_{nl}(t)\},\qquad \hat x_{nl}(t{+}1)=\mathbb E\{\cdot\}\tag{R13, R14}$$
$$\nu^h_{mn}(t{+}1)=\operatorname{var}\{h_{mn}\mid q_{mn}=\hat q_{mn}(t);\nu^q_{mn}(t)\},\qquad \hat h_{mn}(t{+}1)=\mathbb E\{\cdot\}\tag{R15, R16}$$
$$\text{정지: }\sum_{m,l}|\bar p_{ml}(t)-\bar p_{ml}(t{-}1)|^2\le\tau\sum_{m,l}|\bar p_{ml}(t)|^2\tag{R17}$$

**AWGN 특수화** [정확, 원문 식 71–72]. (R5)–(R8)은 적분하지 말고 이 폐형식으로 직접 구현한다:
$$\nu^s_{ml}=\frac{1}{\nu^p_{ml}+\sigma^2},\quad \hat s_{ml}=\frac{y_{ml}-\hat p_{ml}}{\nu^p_{ml}+\sigma^2},\quad \nu^z_{ml}=\frac{\nu^p_{ml}\sigma^2}{\nu^p_{ml}+\sigma^2},\quad \hat z_{ml}=\frac{\sigma^2\hat p_{ml}+\nu^p_{ml}y_{ml}}{\nu^p_{ml}+\sigma^2}$$

**Damping** [원문 §IV-A 식 93–98]. $\beta(t)\in(0,1]$를 $\bar\nu^p,\nu^p,\nu^s,\hat s,\hat x,\hat h$에 적용. 감쇠된 $\bar x_{nl}(t{+}1),\bar h_{mn}(t{+}1)$은 **(R9)–(R12)에만** 쓰고 **(R1)–(R2)에는 쓰지 않는다.** $\beta=1$이면 무감쇠 Table III와 동일해야 한다(테스트 B1).

> ### ⚠ 원문 오타 — 반드시 읽을 것 [정확, 폐형식 확인]
> 원문 damping 식 (95)는 $\nu^s\leftarrow\beta\big((\nu^z/\nu^p-1)/\nu^p\big)+\cdots$로 인쇄되어 있어 **(R7)과 부호가 반대다.**
> (R7)이 맞다: AWGN에서 $\nu^z=\nu^p\sigma^2/(\nu^p+\sigma^2)<\nu^p$이므로 $(1-\nu^z/\nu^p)/\nu^p = 1/(\nu^p+\sigma^2)>0$이고 이것이 원문 식 (72)와 일치한다.
> **(R7)의 부호를 쓰고, (95)는 따르지 않는다.** 코드에 이 주석을 남긴다.

### 1.3 우리 설정에서의 구체화

- **파일럿 열** $l\le T_p$: $p_{x_{nl}}$은 파일럿 심볼의 점질량. (R13)(R14)에서 $\nu^x_{nl}=0$, $\hat x_{nl}=x^{\rm pilot}_{nl}$ 고정.
- **데이터 열 심볼 prior**: decoder extrinsic LLR로 만든 QPSK prior. 외부 루프 = [BiG-AMP $T_{\rm in}{=}5$회] → 심볼 LLR 추출 → BCJR → extrinsic LLR → prior 갱신, **총 외부 16회**.
- **채널 prior**: Table III는 **element-wise 분리형 prior만** 받는다. 우리 testbed의 채널은 Kronecker 상관이라 상관 prior를 넣을 수 없다. → **i.i.d. $\mathcal{CN}(0,1/N_r)$** 로 두고, 결과 파일 헤더에 한 줄로 명시한다:
  `BiG-AMP prior: i.i.d. CN(0,1/Nr) — correlated prior not supported by Table III (structural limitation)`
  이는 BiG-AMP의 구조적 한계이지 우리가 불리하게 만든 것이 아니다. 논문에서도 그렇게 서술한다.
- **초기화 (I2)**: 파일럿 기반 LS/LMMSE로 $\hat h_{mn}(1),\nu^h_{mn}(1)$ (다른 arm과 동일한 첫 패스). 데이터 열은 $\hat x_{nl}(1)=0$, $\nu^x_{nl}(1)=1$.
- **damping** 기본 $\beta=0.7$. adaptive damping은 구현하지 않는다.
- **수치 안정화**: $\nu^p,\nu^r,\nu^q$ 하한 $10^{-12}$; 매 반복 `isfinite` 점검; 발산 시 `diverged` 분류 후 마지막 유효 반복 반환.
- **구현 형태**: Table III의 전 단계를 **블록 방향으로 배치 가능한 형태**(시행 $n$개를 선행 축으로)로 쓴다. 행렬 자체는 작으므로 CPU 멀티프로세스로 충분하지만, 배치형으로 써 두면 병목이 측정됐을 때 GPU 이식이 쉽다(`01_RULES.md` §9.2 순위 3). **추측으로 미리 GPU 포팅하지 말 것.**

---

## 2. R4 — 3-module SC-VAMP형

### 2.1 먼저 — 원문과 우리 설정의 차이 (서술에서 흐리지 말 것)

[V: arXiv:2604.19061v1 본문 전체 확인, 2026-09-19]

| | 원문 | 우리 |
|---|---|---|
| 관측 | $\mathbf Y=f(\mathbf H\mathbf X)+\mathbf Z$, $f=\tanh$ 등 | $\mathbf Y=\mathbf H\mathbf X+\mathbf W$ ($f=\mathrm{id}$) |
| 채널 $\mathbf H$ | **기지**, i.i.d. 실수 $\mathcal N(0,1/M)$ | **미지**, 상관, 추정 대상 |
| 채널 추정 | **없음** | 있어야 함 |
| prior | LDPC 부호 제약 $p_X$ 하나 | 부호 + 채널 |
| denoiser | **BP만** | BCJR (convolutional) |
| 신호 | BPSK 실수 | QPSK 복소 |

⇒ **R4는 저 논문의 알고리즘이 아니다. 저 논문의 *인터페이스*를 우리 설정에 적응시킨 것이다.** 결과 파일과 논문 서술에서 이 구분을 유지한다.

### 2.2 가져오는 것 — 인터페이스 [V, 원문 식 3–5, 12–13, 16–18, 23–24]

**(a) 범용 extrinsic 규칙.** 모듈 입력 $(r_{\rm in},v_{\rm in})$, 사후 $(\hat x_{\rm post},v_{\rm post})$에 대해
$$\alpha=\frac{v_{\rm post}}{v_{\rm in}},\qquad r_{\rm out}=\frac{\hat x_{\rm post}-\alpha\,r_{\rm in}}{1-\alpha},\qquad v_{\rm out}=\frac{\alpha}{1-\alpha}\,v_{\rm in}$$
Fisher 형 $\alpha=1-(v_{\rm in}/N)J_{R\mid Y}$와 등가. 모든 $\alpha$를 $[\epsilon,1-\epsilon]$, $\epsilon=10^{-6}$로 clip한다(원문 명시).

**(b) Module A (likelihood).** 우리는 $f=\mathrm{id}$이므로 원문이 명시하듯 Module A는 매 반복 $(\mathbf y,\sigma^2)$를 **상수로** 돌려주고 3-module이 2-module로 정확히 환원된다. 별도 구현 불필요 — 단, 테스트 S1으로 이 상수성을 확인한다.

**(c) Module C (coupling) = SISO-LMMSE** [정확, 원문 식 16–18]. 데이터 열 $l$마다
$$\boldsymbol\Sigma^C=\Big(\tfrac{1}{v_x}\mathbf I_{N_t}+\tfrac{1}{\sigma^2}\hat{\mathbf H}^H\hat{\mathbf H}\Big)^{-1},\qquad
\hat{\mathbf x}^C_{{\rm post},l}=\boldsymbol\Sigma^C\Big(\tfrac{\mathbf r_{x,l}}{v_x}+\tfrac{\hat{\mathbf H}^H\mathbf y_l}{\sigma^2}\Big)$$
$$v^C_{{\rm post},x}=\tfrac1{N_t}\operatorname{Tr}\boldsymbol\Sigma^C,\qquad
\alpha^C_x=\frac{v^C_{{\rm post},x}}{v_x}=\frac1{N_t}\sum_{n=1}^{N_t}\frac{\sigma^2}{\sigma^2+v_x\lambda_n}$$
$\lambda_n$ = $\hat{\mathbf H}^H\hat{\mathbf H}$의 고유값. 고유분해는 블록당 1회 계산해 재사용.

**(d) Module B (prior/denoiser) = BCJR.** pseudo-observation → LLR → BCJR → a-posteriori LLR → soft symbol $(\bar x_n, v_n)$ (기존 헬퍼 사용) → $v^B_{\rm post}=\frac1{N}\sum_n v_n$ → $\alpha^B=v^B_{\rm post}/v^{\rm in}_x$ → (a)의 extrinsic 규칙.
  - **두 모드를 반드시 둘 다 구현한다.** `onsager`: 위. `llr`: 고전 $L^{\rm ext}=L^{\rm app}-L^{\rm in}$. 원문의 "LLR Turbo" ablation이 이 스위치다.
  - 코드 주석으로 남길 것 [원문 §III-C3, 근사]: variance-ratio $\alpha^B$는 **정확한 MMSE denoiser일 때만** 이론적 Onsager 보정과 일치하고, 근사 복호기에서는 대용품이다.

**(e) 초기화·일정.** $(r_x,v_x)=(0,1)$. 한 반복 = Module C가 extrinsic 출력 → Module B 갱신 → (Module A는 상수).

### 2.3 우리가 추가하는 것 — 원문에 없는 부분

원문에 채널 추정 모듈이 없으므로 하나를 붙여야 한다. **가장 고전적인 것**을 붙인다:

- 파일럿 + **a-posteriori** soft symbol 기반 LMMSE 재추정. **LOO 없음. damping 없음.**

이렇게 두면 R4가 분리하는 것이 정확히 하나가 된다: **우리 D-15+LOO 이득이 저들의 variance-ratio Onsager 인터페이스만으로 얻어지는가.** R2와 R4의 격차가 작게 나올 가능성은 실재한다(원문은 기지 채널·$f=\mathrm{id}$에서 Onsager 인터페이스가 고전 LLR 차감 대비 BER $10^{-2}$에서 ≈3 dB 유리하다고 보고). **그 결과가 나와도 설정을 바꾸지 않는다.**

결과 파일 헤더에 명시:
`R4: channel estimation = classical APP-LMMSE (no LOO); only the Onsager extrinsic interface follows arXiv:2604.19061`

### 2.4 모듈 구조 (스켈레톤)

| 단위 | 책임 | 불변식 |
|---|---|---|
| extrinsic 연산자 | (a)의 세 식 + clip | $v_{\rm out}>0$, clip 발동 횟수 집계 |
| Module C | (c)의 LMMSE + $\alpha^C_x$ | $\alpha^C_x\in(0,1)$; 고유분해 재사용 |
| Module B | (d), 모드 스위치 | `llr` 모드는 기존 고전 turbo arm과 로그 동일 (테스트 S4) |
| 채널 추정기 | (2.3) | LOO 미사용을 명시적 플래그로 |
| 루프 | 16회, 반복별 지표 기록 | |
