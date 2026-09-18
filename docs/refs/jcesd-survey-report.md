# Joint Channel Estimation and Symbol Detection (JCESD) 연구 조사 보고서

> 작성일: 2026-08-06 · 용도: 연구 보고서 작성을 위한 기초 조사 자료
> 용어 주의: 문헌에 따라 symbol detection / data detection / signal detection이 혼용되며, 본 보고서에서는 동일한 문제로 취급한다. 약어로 JCESD(Joint Channel Estimation and Symbol/Data Detection)를 사용한다.

---

## 목차

1. 문제 정의와 시스템 모델
2. 역사적 전개 (주요 이정표와 핵심 수식)
3. 한눈에 보는 타임라인
4. 방법론 분류 (Taxonomy)와 통일적 관점
5. 이론적 한계와 성능 지표
6. 열린 문제와 연구 기회
7. 연구 보고서 구성 제안
8. 참고문헌
9. 표기법

---

## 1. 문제 정의와 시스템 모델

### 1.1 왜 "조인트"인가 — 닭과 달걀 문제

수신기는 두 가지를 동시에 알지 못한다. 심볼을 검출하려면 채널을 알아야 하고, 채널을 추정하려면 송신 심볼을 알아야 한다. 전통적 해법은 이 순환을 **파일럿(training sequence)** 으로 끊는 것이다. 송수신기가 약속한 기지(known) 심볼로 채널을 먼저 추정하고, 그 추정치를 참값처럼 취급해 데이터를 검출한다. 이 "분리형(separate/decoupled)" 구조는 구현이 단순하지만 세 가지 근본적 비용을 치른다.

1. **파일럿 오버헤드**: 파일럿이 차지한 자원만큼 유효 전송률이 줄어든다. 고이동성(짧은 코히어런스 시간), 대규모 안테나(추정할 계수 증가), 짧은 패킷(URLLC) 환경에서 오버헤드 비중이 급격히 커진다.
2. **추정 오차의 전파**: 채널 추정 오차는 검출 단계에서 잡음처럼 작용하며, 특히 저SNR에서 성능 열화가 크다. 검출기는 추정치를 참값으로 가정하는 mismatched receiver가 된다.
3. **정보의 낭비**: 데이터 심볼이 실린 수신 신호에도 채널 정보가 들어 있다. 분리형 수신기는 이 정보를 버린다.

JCESD는 데이터 구간의 수신 신호까지 채널 추정에 활용하고(반대로 정제된 채널 추정치를 다시 검출에 활용하여), 파일럿 오버헤드를 줄이면서 분리형 대비 검출·추정 성능을 동시에 끌어올리려는 문제이다. 이 문제의식은 1970년대 적응 등화에서 싹텄고, EM·터보·메시지 패싱·딥러닝으로 도구를 바꿔가며 50년 넘게 이어져 왔다.

### 1.2 신호 모델

가장 널리 쓰이는 블록 페이딩(block-fading) MIMO 모델을 기준으로 한다. $N_t$개 송신 안테나, $N_r$개 수신 안테나, 코히어런스 블록 길이 $T$에서

$$
\mathbf{Y} = \mathbf{H}\mathbf{X} + \mathbf{W}, \qquad \mathbf{W}[:,n] \sim \mathcal{CN}(\mathbf{0}, \sigma^2\mathbf{I}_{N_r})
$$

여기서 $\mathbf{Y}\in\mathbb{C}^{N_r\times T}$는 수신 행렬, $\mathbf{H}\in\mathbb{C}^{N_r\times N_t}$는 블록 내에서 일정한 채널, $\mathbf{X}=[\mathbf{X}_p\ \mathbf{X}_d]\in\mathbb{C}^{N_t\times T}$는 파일럿 $\mathbf{X}_p$ ($T_p$ 심볼)와 데이터 $\mathbf{X}_d$ ($T_d = T-T_p$ 심볼, 각 원소는 성상 $\mathcal{A}$에서 선택)로 구성된 송신 행렬이다.

같은 뼈대가 다른 파형에도 그대로 적용된다.

- **주파수 선택적 SISO/ISI 채널**: $y[n] = \sum_{l=0}^{L-1} h[l]\,x[n-l] + w[n]$ — 트렐리스 기반 기법(MLSE, PSP, BCJR)의 무대.
- **OFDM**: 부반송파별로 $Y[k] = H[k]X[k] + W[k]$ — 파일럿 배치·보간과 결합된 JCESD의 무대.
- **시변(doubly-selective) 채널·OTFS**: 채널이 블록 내에서도 변해 기저 전개(BEM)나 지연-도플러 표현이 필요한 무대.

### 1.3 분리형 수신기 기준선 (baseline)

파일럿 구간 $\mathbf{Y}_p = \mathbf{H}\mathbf{X}_p + \mathbf{W}_p$에서의 고전적 추정기는 다음과 같다.

$$
\hat{\mathbf{H}}_{\mathrm{LS}} = \mathbf{Y}_p\mathbf{X}_p^{H}\big(\mathbf{X}_p\mathbf{X}_p^{H}\big)^{-1}
$$

$$
\hat{\mathbf{h}}_{\mathrm{LMMSE}} = \mathbf{R_h}\tilde{\mathbf{X}}_p^{H}\big(\tilde{\mathbf{X}}_p\mathbf{R_h}\tilde{\mathbf{X}}_p^{H} + \sigma^2\mathbf{I}\big)^{-1}\mathbf{y}_p
$$

(두 번째 식은 $\mathbf{h}=\mathrm{vec}(\mathbf{H})$, $\mathbf{y}_p=\mathrm{vec}(\mathbf{Y}_p)$, $\tilde{\mathbf{X}}_p = \mathbf{X}_p^{T}\otimes\mathbf{I}_{N_r}$로 벡터화한 표현이며, $\mathbf{R_h}$는 채널 공분산.)

추정치 $\hat{\mathbf{H}}$가 주어지면 검출은

$$
\hat{\mathbf{x}}_{\mathrm{ML}} = \arg\min_{\mathbf{x}\in\mathcal{A}^{N_t}} \big\|\mathbf{y} - \hat{\mathbf{H}}\mathbf{x}\big\|^2
\qquad\text{(선형 대안: ZF, LMMSE } \hat{\mathbf{x}} = (\hat{\mathbf{H}}^{H}\hat{\mathbf{H}} + \sigma^2\mathbf{I})^{-1}\hat{\mathbf{H}}^{H}\mathbf{y}\text{)}
$$

이 구조의 성능은 $\hat{\mathbf{H}}$의 품질에 종속되며, 추정 오차를 고려하지 않는 한 최적이 아니다.

### 1.4 조인트 문제의 정식화

**(a) 조인트 ML (deterministic 관점).** 채널을 미지의 결정적 파라미터로 보면

$$
(\hat{\mathbf{H}},\hat{\mathbf{X}}_d) = \arg\max_{\mathbf{H},\ \mathbf{X}_d\in\mathcal{A}^{N_t\times T_d}} p(\mathbf{Y}\mid\mathbf{H},\mathbf{X})
= \arg\min_{\mathbf{H},\ \mathbf{X}_d} \big\|\mathbf{Y}-\mathbf{H}\mathbf{X}\big\|_F^2 .
$$

주어진 $\mathbf{X}$에 대해 $\mathbf{H}$의 최적해는 LS 해 $\hat{\mathbf{H}}(\mathbf{X}) = \mathbf{Y}\mathbf{X}^{H}(\mathbf{X}\mathbf{X}^{H})^{-1}$이므로, 이를 대입해 채널을 소거한 **농축(concentrated) 우도 / GLRT** 형태를 얻는다.

$$
\hat{\mathbf{X}} = \arg\max_{\mathbf{X}} \operatorname{tr}\!\big(\mathbf{Y}\,\mathbf{P}_{\mathbf{X}}\,\mathbf{Y}^{H}\big),
\qquad \mathbf{P}_{\mathbf{X}} := \mathbf{X}^{H}(\mathbf{X}\mathbf{X}^{H})^{-1}\mathbf{X}.
$$

즉 조인트 ML 검출은 "수신 신호 에너지를 가장 잘 설명하는 부호어 부분공간 찾기"이며, 탐색 공간이 $|\mathcal{A}|^{N_t T_d}$로 지수적이라 일반적으로 NP-hard이다. 특수 구조(직교 STBC, 상수 포락선 성상 등)에서는 반한정 완화(SDR)나 격자 기반 기법으로 최적해 또는 준최적해를 다항 복잡도로 얻는 연구가 이어졌다.

**(b) 베이지안 최적 (stochastic 관점).** 채널에 사전분포 $p(\mathbf{H})$를 부여하면, 비트/심볼 오류 최소화 관점의 최적 검출은 채널을 **주변화(marginalize)** 한 사후확률을 요구한다.

$$
\hat{x}_{n}^{\mathrm{MAP}} = \arg\max_{a\in\mathcal{A}}\ p(x_n = a \mid \mathbf{Y})
= \arg\max_{a} \sum_{\mathbf{X}_d:\,x_n=a} \int p(\mathbf{Y}\mid\mathbf{H},\mathbf{X})\,p(\mathbf{H})\,P(\mathbf{X}_d)\,d\mathbf{H}.
$$

적분(채널 주변화)과 이산 합(심볼 주변화)이 얽혀 정확한 계산은 불가능하고, 이 난제를 어떻게 근사하느냐가 곧 JCESD 방법론의 역사다: EM(점추정+소프트 심볼), 터보(스케줄링된 소프트 정보 교환), 메시지 패싱/변분 추론(분포 근사), 딥러닝(근사 사후분포 또는 반복 알고리즘 자체를 학습).

**(c) 쌍선형(bilinear) 역문제 관점.** $\mathbf{Y} \approx \mathbf{H}\mathbf{X}$에서 두 인자를 모두 복원하는 문제는 행렬 분해(matrix factorization)·사전 학습(dictionary learning)과 같은 구조의 **blind/bilinear inverse problem**이다. 이 관점은 2010년대 BiG-AMP 계열과 2020년대 생성모델(확산모델) 기반 접근의 출발점이 된다.

### 1.5 식별 가능성(identifiability)과 모호성

파일럿이 전혀 없으면 $\mathbf{H}\mathbf{X} = (\mathbf{H}\mathbf{G})(\mathbf{G}^{-1}\mathbf{X})$인 임의의 가역 $\mathbf{G}$에 대해 우도가 동일하므로 해가 유일하지 않다. 유한 알파벳 제약은 $\mathbf{G}$를 (일반화된) 순열·위상 모호성으로 줄여 주지만, 스트림별 위상/순열 모호성은 남는다. 실무적 결론은 다음과 같다.

- **완전 블라인드**는 잔여 모호성 해소 장치(차동 부호화, 성상 비대칭 등)가 필요하다.
- **준블라인드(semi-blind)** — 소수의 파일럿 + 데이터 통계의 결합 — 가 모호성을 없애면서 오버헤드를 최소화하는 현실적 절충이며, JCESD의 표준 설정이다. 준블라인드 CRB 분석(de Carvalho & Slock, 1997)은 소량의 파일럿과 데이터 정보의 결합이 순수 파일럿 기반 대비 얼마나 이득인지 정량화했다.

---

## 2. 역사적 전개 — 주요 이정표와 핵심 수식

### 2.1 태동기: 적응 등화와 결정지향 적응 (1960s–1970s)

JCESD의 씨앗은 **결정지향(decision-directed) 적응**이다. Lucky(1965)의 zero-forcing 적응 등화기는 훈련 구간이 끝난 뒤 자신의 검출 결과를 참값처럼 사용해 등화기 계수를 계속 갱신했다. "검출 결과로 채널 지식을 갱신하고, 갱신된 지식으로 다시 검출한다"는 순환 구조가 여기서 처음 등장한다. LMS(Widrow–Hoff, 1960)는 이 적응의 표준 도구가 되었다.

명시적인 "채널 추정 + 시퀀스 검출"의 결합은 **Magee & Proakis(1973)** 의 adaptive MLSE에서 나타난다. Viterbi 알고리즘(1967)과 Forney의 MLSE 정식화(1972)를 배경으로, 이들은 미지 ISI 채널에서 채널 추정기(적응 필터)와 Viterbi 검출기를 결합한 수신기를 제안했다. 다만 채널 갱신에 쓰이는 검출 결정이 트렐리스 결정 지연만큼 늦어, 시변 채널에서 추정치가 낡는(stale) 문제를 안고 있었다 — 이 약점이 20여 년 뒤 PSP(2.5절)의 탄생 배경이 된다.

이 시기의 유산은 실무에도 깊이 남았다. GSM은 짧은 버스트 중앙의 midamble로 채널을 추정하고 MLSE로 검출하는 구조를 채택했는데, 짧은 블록에서 파일럿 효율과 추정 품질의 긴장이라는 JCESD의 문제의식을 상용 시스템 차원에서 보여 준 사례다.

### 2.2 블라인드 등화: 파일럿 없이 (1975–1990)

Sato(1975)는 파일럿 없이 출력 신호의 통계적 성질만으로 등화기를 적응시키는 self-recovering equalization을 제안했고, Godard(1980)의 **CMA(Constant Modulus Algorithm)** 가 이 계열의 대표가 되었다. CMA는 성상의 상수 포락선 성질을 비용함수로 삼는다.

$$
J_{\mathrm{CMA}}(\mathbf{f}) = \mathbb{E}\Big[\big(|\mathbf{f}^{H}\mathbf{y}[n]|^{2} - R_2\big)^{2}\Big],
\qquad R_2 = \frac{\mathbb{E}[|x|^4]}{\mathbb{E}[|x|^2]}.
$$

고차 통계 기반 판별 기준의 이론화는 Shalvi & Weinstein(1990)으로 이어졌다. 블라인드 등화는 채널을 명시적으로 추정하지 않는다는 점에서 JCESD와 구별되지만, "데이터 자체가 채널 지식의 원천"이라는 핵심 통찰을 확립했고, 수렴 속도·국소 최소·위상 모호성이라는 블라인드 계열 공통의 한계도 드러냈다.

### 2.3 EM 알고리즘: 확률적 조인트의 원형 (1977, 1988–1999)

Dempster–Laird–Rubin(1977)의 **EM 알고리즘**(HMM 맥락의 Baum–Welch(1970)가 선행)은 JCESD에 처음으로 원리적인 통계적 틀을 제공했다. 채널 $\mathbf{H}$를 추정 대상 파라미터, 데이터 심볼 $\mathbf{X}_d$를 잠재변수로 두면

$$
\text{E-step:}\quad Q\big(\mathbf{H}\mid\mathbf{H}^{(t)}\big)
= \mathbb{E}_{\mathbf{X}_d\mid\mathbf{Y},\mathbf{H}^{(t)}}\Big[\ln p(\mathbf{Y},\mathbf{X}_d\mid\mathbf{H})\Big],
\qquad
\text{M-step:}\quad \mathbf{H}^{(t+1)} = \arg\max_{\mathbf{H}} Q .
$$

가우시안 잡음에서는 M-step이 소프트 심볼의 1·2차 모멘트만으로 닫힌 형태를 갖는다.

$$
\mathbf{H}^{(t+1)} = \mathbf{Y}\,\mathbb{E}[\mathbf{X}]^{H}\Big(\mathbb{E}\big[\mathbf{X}\mathbf{X}^{H}\big]\Big)^{-1}.
$$

E-step의 심볼 사후확률은 ISI 채널에서는 BCJR(forward–backward)로 정확히 계산할 수 있다. EM은 우도의 단조 증가를 보장하지만 국소 최대에 갇힐 수 있어, 소량의 파일럿으로 초기화하는 준블라인드 운용이 표준이 되었다.

주요 이정표: Feder & Weinstein(1988)이 중첩 신호 파라미터 추정에 EM을 도입했고, **Kaleh & Vallet(1994)** 은 미지(비선형 포함) 채널에서 Baum–Welch/EM 기반의 조인트 파라미터 추정·심볼 검출을 정식화했다 — 논문 제목("Joint parameter estimation and symbol detection…") 자체가 이 분야의 명명에 가깝다. Georghiades & Han(1997)은 랜덤 파라미터 하 시퀀스 추정에 EM을 체계화했다. 갱신 순서를 유연화해 수렴을 개선한 **SAGE**(Fessler & Hero, 1994)는 채널 파라미터 추정(Fleury et al., 1999)과 이후 고이동성 OFDM의 조인트 추정·검출(예: ICI 소거를 포함한 SAGE 수신기)로 확장되었다.

한편 EM의 "하드 결정" 버전에 해당하는 **교대 최적화**도 같은 시기에 정립되었다(2.4절의 ILSP/ILSE). EM(소프트) vs. 교대 LS(하드)의 대비는 이후 모든 반복형 JCESD의 기본 설계 축이 된다.

### 2.4 2차 통계 블라인드 식별과 유한 알파벳 조인트 (1991–1996)

1990년대 전반 신호처리 커뮤니티는 블라인드 문제를 두 갈래로 돌파했다.

**(i) 2차 통계(SOS) 기반 식별.** Tong–Xu–Kailath(1991/1994)는 과표본화(oversampling)로 생기는 순환정상성(cyclostationarity) 덕분에 SIMO 채널이 2차 통계만으로 식별 가능함을 보였고, Moulines et al.(1995)의 부분공간(subspace) 방법이 뒤따랐다. 고차 통계가 필요하던 기존 블라인드 대비 필요한 데이터 양을 크게 줄인 돌파구였다. 이 계열은 채널을 먼저 (블라인드로) 추정한 뒤 검출하는 구조라 엄밀히는 JCESD가 아니지만, "파일럿 최소화"라는 목표를 공유하며 준블라인드 CRB 분석(de Carvalho & Slock, 1997)으로 이론적 토대를 제공했다.

**(ii) 유한 알파벳(finite-alphabet) 성질을 이용한 조인트.** Seshadri(1994)는 블라인드 트렐리스 탐색으로 채널과 데이터 시퀀스를 동시에 추정했고, **Talwar–Viberg–Paulraj(1996)** 의 **ILSP/ILSE**는 조인트 ML의 교대 최적화 구조를 명료하게 정식화했다.

$$
\mathbf{X}^{(t+1)} = \Pi_{\mathcal{A}}\Big(\big(\mathbf{H}^{(t)}\big)^{\dagger}\mathbf{Y}\Big),
\qquad
\mathbf{H}^{(t+1)} = \mathbf{Y}\big(\mathbf{X}^{(t+1)}\big)^{\dagger}.
$$

($\Pi_{\mathcal{A}}$: 성상으로의 성분별 사영. ILSE는 사영 대신 열거로 정확한 조건부 최적을 취한다.) 각 스텝이 비용 $\|\mathbf{Y}-\mathbf{H}\mathbf{X}\|_F^2$를 단조 감소시키지만 국소 최소가 많다는 점, 위상/순열 모호성이 남는다는 점이 명확히 인식되었다. 상수 포락선 성상에 대한 해석적 해(ACMA, van der Veen & Paulraj, 1996)도 이 시기의 성과다.

### 2.5 Per-Survivor Processing: 트렐리스 안으로 들어간 채널 추정 (1995)

**Raheli–Polydoros–Tzou(1995)** 의 **PSP**는 "미지 파라미터 하 MLSE"의 일반 원리로서, 조인트 추정·검출을 트렐리스 탐색 자체에 내장했다. 핵심은 전역 채널 추정치 하나를 유지하는 대신 **생존 경로(survivor)마다 그 경로의 심볼 가설로 갱신한 채널 추정치를 따로 유지**하는 것이다.

$$
\hat{\mathbf{h}}_{n+1}(s) = \hat{\mathbf{h}}_{n}(\check{s}) + \mu\, e_{n}(\check{s})\,\mathbf{x}_{n}^{*}(\check{s}),
\qquad e_{n}(\check{s}) = y_n - \hat{\mathbf{h}}_{n}^{H}(\check{s})\,\mathbf{x}_{n}(\check{s}),
$$

($\check{s}$: 상태 $s$로 들어오는 생존 경로, $\mathbf{x}_n(\check{s})$: 그 경로의 심볼 가설.) 각 가지 메트릭이 자기 경로의 추정치로 계산되므로 결정 지연에 따른 추정치 낡음이 사라진다. Magee–Proakis(1973)의 약점을 정면으로 해결한 것으로, 채널뿐 아니라 위상·주파수 오프셋 등 임의의 미지 파라미터에 적용되는 범용 원리라는 점에서 "굵직한" 이정표다. 상태 수만큼 추정기를 유지하는 복잡도 증가가 대가다.

### 2.6 터보 원리: 반복 수신기와 code-aided 추정 (1995–2005)

터보 부호(Berrou et al., 1993)의 **외재 정보(extrinsic information) 교환** 원리는 수신기 설계 전반을 바꿨다. Douillard et al.(1995)의 **터보 등화**는 등화기와 복호기가 소프트 정보를 반복 교환하게 했고, Wang & Poor(1999)는 이를 다중 사용자 검출·복호에 확장했다. Tüchler–Koetter–Singer(2002)의 저복잡도 LMMSE 터보 등화는 실용화의 결정판이었다.

채널 추정이 이 루프에 편입된 것이 **code-aided / iterative channel estimation**(예: Valenti & Woerner, 2001)이다. 복호기가 내놓는 LLR로 **소프트 심볼**을 만들고,

$$
\bar{x}_n = \sum_{a\in\mathcal{A}} a\,P\big(x_n=a\mid\mathcal{L}^{\mathrm{ext}}\big),
\qquad
v_n = \sum_{a\in\mathcal{A}} |a|^2 P\big(x_n=a\mid\mathcal{L}^{\mathrm{ext}}\big) - |\bar{x}_n|^2,
$$

이를 "가상의 파일럿"으로 삼아 LMMSE 채널 재추정을 수행한다(잔차 불확실성 $v_n$은 유효 잡음으로 처리). 반복 구조는 [채널 추정기 ↔ 검출기 ↔ 복호기]의 3자 소프트 정보 교환으로 일반화되며, 수렴 거동은 EXIT 차트(ten Brink, 2001)로 분석되었다. 파일럿을 데이터에 겹쳐 보내는 superimposed pilot(Hoeher & Tufvesson, 1999)도 오버헤드 없는 추정이라는 같은 문제의식에서 나왔다. 이 시대의 핵심 교훈 — **하드 결정 대신 소프트 정보를, 일회성 대신 반복을** — 은 이후 메시지 패싱과 딥러닝 시대까지 관통한다.

### 2.7 정보이론적 토대: 비코히어런트 용량과 훈련의 가치 (1990–2003)

"조인트가 얼마나 이득인가"에 대한 이론적 답이 이 시기에 나왔다.

- **Divsalar & Simon(1990)** 의 다중 심볼 차동 검출(MSDD)은 채널 추정 없이 블록 단위 검출만으로 코히어런트 성능에 접근할 수 있음을 보여, 명시적 추정이 목적이 아니라 수단임을 일깨웠다.
- **Marzetta & Hochwald(1999)** 는 송수신 모두 CSI가 없는 블록 페이딩 채널의 용량 구조를 규명했고(유니터리 시공간 변조, Hochwald & Marzetta, 2000), **Zheng & Tse(2002)** 는 고SNR 자유도(DoF)가

$$
N^{*}\Big(1 - \frac{N^{*}}{T}\Big)\ \log \mathrm{SNR} + O(1), \qquad N^{*} = \min\big(N_t, N_r, \lfloor T/2 \rfloor\big)
$$

임을 보이며 최적 시그널링이 Grassmann 다양체 위의 부호화임을 밝혔다. $1 - N^{*}/T$라는 인자는 "채널을 알아내는 데 불가피하게 지불하는 자원"의 정보이론적 표현으로, 1.4절의 GLRT(부분공간 검출)와 정확히 조응한다.
- **Hassibi & Hochwald(2003)** 는 파일럿 기반 시스템의 용량 하한을 최적화해, 전력 최적화 시 최적 파일럿 길이가 $T_p = N_t$임을 보였다. 고SNR·저이동성에서는 파일럿 기반의 손실이 작지만, 저SNR·고이동성(짧은 $T$)에서는 손실이 커진다 — 즉 **JCESD가 가장 값진 영역이 어디인지**를 이 결과가 정량적으로 지목한다.

### 2.8 팩터 그래프와 메시지 패싱: 통합 언어의 등장 (2001–2016)

Kschischang–Frey–Loeliger(2001)의 sum-product 알고리즘 정식화와 함께, **Worthen & Stark(2001)** 는 채널 추정·검출·복호를 하나의 팩터 그래프 위 반복 수신기로 통합 설계하는 틀을 제시했다. 결합 사후분포를

$$
p(\mathbf{X}_d,\mathbf{H}\mid\mathbf{Y}) \ \propto\ p(\mathbf{H})\ \prod_{n} p\big(\mathbf{y}_n \mid \mathbf{H},\mathbf{x}_n\big)\ \prod_{n} P(\mathbf{x}_n)
$$

로 인수분해하고, 변수(심볼, 채널)와 인자(우도, 사전, 부호 제약) 사이에 메시지를 교환한다. 이 관점의 힘은 **기존 기법들이 전부 특수한 메시지 패싱 스케줄로 재해석**된다는 데 있다: 터보 반복은 그래프 상의 스케줄이고, EM은 채널 메시지를 점질량으로 제한한 경우다(Loeliger et al., 2007).

연속 변수(채널) 메시지의 처리에서 갈래가 나뉜다. 평균장(mean-field) 근사를 쓰는 **변분 메시지 패싱(VMP)** 기반 조인트 수신기(Kirkelund et al., 2010, MIMO-OFDM), BP와 MF를 자유에너지 관점에서 최적 결합한 **BP–MF 하이브리드**(Riegler et al., 2013), 모멘트 매칭으로 가우시안 근사를 정제하는 **EP(expectation propagation)** 검출(Céspedes et al., 2014)이 대표적이다. 다중 사용자 MIMO-OFDM 상향링크의 조인트 검출·추정을 팩터 그래프로 설계한 Novak–Matz–Hlawatsch(2013), 3D massive MIMO-OFDM의 조인트 추정·복호 메시지 패싱 수신기(Wu et al., 2016)가 이 흐름의 성숙을 보여 준다. 변분 관점의 일반형은 다음과 같다.

$$
q^{\star} = \arg\min_{q(\mathbf{X}_d)q(\mathbf{H})} \mathrm{KL}\Big(q(\mathbf{X}_d)\,q(\mathbf{H})\ \Big\|\ p(\mathbf{X}_d,\mathbf{H}\mid\mathbf{Y})\Big),
\qquad
\ln q^{\star}(\mathbf{H}) = \mathbb{E}_{q(\mathbf{X}_d)}\big[\ln p(\mathbf{Y},\mathbf{X}_d,\mathbf{H})\big] + \mathrm{const}.
$$

### 2.9 압축 센싱, AMP, 그리고 쌍선형 추론 (2008–2016)

무선 채널의 (지연·각도 영역) 희소성이 주목받으며 **compressed channel sensing**(Bajwa–Haupt–Sayeed–Nowak, 2010)이 파일럿 수를 채널의 자유도 수준으로 끌어내렸다. 알고리즘 측면에서는 **AMP**(Donoho–Maleki–Montanari, 2009)와 **GAMP**(Rangan, 2011)가 대규모 선형 역문제의 근사 베이지안 추론을 사실상 표준화했고, Schniter(2011)는 미지 희소 채널 위 BICM-OFDM의 조인트 추정·복호 메시지 패싱 수신기를 설계했다.

결정적 도약은 **BiG-AMP**(Parker–Schniter–Cevher, 2014)다. $\mathbf{Y}=\mathbf{H}\mathbf{X}+\mathbf{W}$에서 $\mathbf{H}$와 $\mathbf{X}$를 **모두** 확률변수로 두는 쌍선형 일반화 AMP를 유도해, JCESD를 행렬 분해·사전 학습과 같은 부류의 문제로 통일했다. 채널에는 연속 사전분포, 심볼에는 이산(성상) 사전분포를 넣으면 그대로 준블라인드 JCESD가 되며, 대규모 시스템 극한에서 state evolution으로 성능 예측이 가능하다. 응용의 대표가 저해상도 ADC massive MIMO의 **Bayes-optimal joint channel-and-data estimation**(Wen et al., 2016)이다. 인접 문제로, grant-free 대규모 접속의 조인트 활동 감지·채널 추정(JADCE)도 AMP로 정식화되었다(Liu & Yu, 2018).

### 2.10 Massive MIMO 시대: 파일럿 오염과 준블라인드의 재부상 (2010–2018)

Marzetta(2010)의 massive MIMO는 JCESD의 동기를 재점화했다. 안테나가 늘수록 추정할 계수와 파일럿 부담이 커지고, 셀 간 파일럿 재사용이 **파일럿 오염(pilot contamination)** 이라는 근본 한계를 만들기 때문이다. 대응으로 수신 신호의 부분공간 구조를 이용한 EVD 기반 블라인드 추정(Ngo & Larsson, 2012), 대규모 안테나 극한에서 신호·간섭 부분공간이 분리되는 성질을 이용한 **blind pilot decontamination**(Müller et al., 2014), 다중 사용자 준블라인드 추정(Nayebi & Rao, 2018) 등이 나왔다. 요지는 명확하다: **안테나가 많을수록 데이터로부터 공짜로 얻는 채널 정보가 많아져, 조인트/준블라인드의 이득이 커진다.**

### 2.11 딥러닝 수신기 (2017–2022)

O'Shea & Hoydis(2017)의 물리계층 딥러닝 개관과 함께 JCESD는 학습의 언어로 다시 쓰였다. 세 갈래로 정리된다.

**(i) 순수 데이터 구동(암묵적 조인트).** Ye–Li–Juang(2018)은 OFDM에서 DNN이 파일럿+데이터 수신 신호로부터 비트를 직접 복원하게 하여 — 명시적 채널 추정 단계 없이 — 추정과 검출이 하나의 학습된 사상 $\hat{\mathbf{x}} = f_{\theta}(\mathbf{Y}, \mathbf{X}_p)$으로 융합될 수 있음을 보였다. 학습은 통상 교차 엔트로피 손실

$$
\mathcal{L}(\theta) = \mathbb{E}\Big[\textstyle\sum_{n} \mathrm{CE}\big(\mathbf{x}_n,\ f_{\theta}(\mathbf{Y},\mathbf{X}_p)_n\big)\Big]
$$

로 이뤄진다. 산업계 스케일의 정점이 **DeepRx**(Honkala et al., 2021, Nokia)로, 전체 시간-주파수 그리드를 입력받는 완전 컨볼루션 수신기가 5G 파일럿 패턴 하에서 추정·등화·복조를 통합 수행했다.

**(ii) 모델 구동(model-driven) / 알고리즘 언폴딩.** 반복 알고리즘의 각 반복을 학습 가능한 층으로 펼친다. 일반형은

$$
\mathbf{r}^{(t)} = \mathbf{x}^{(t)} + \gamma_t\,\mathbf{W}_t\big(\mathbf{y}-\mathbf{H}\mathbf{x}^{(t)}\big),
\qquad
\mathbf{x}^{(t+1)} = \eta_{t}\big(\mathbf{r}^{(t)};\theta_t\big)
$$

(선형 정정 + 학습된 잡음 제거기). DetNet(Samuel–Diskin–Wiesel, 2019)이 사영 경사 언폴딩으로 포문을 열었고, **OAMP-Net/OAMP-Net2**(He–Wen–Jin–Li, 2018/2020)는 OAMP를 언폴딩하며 채널 추정 오차를 명시적으로 고려한 JCESD 구성을 다뤘다. ComNet(Gao et al., 2018)은 추정 서브넷과 검출 서브넷을 전문가 지식으로 결합한 OFDM 수신기, Yi & Zhong(2020)의 CENet+CCRNet은 추정 네트워크의 출력에 조건화된 복원 네트워크로 조인트를 구성했다. ViterbiNet, DeepSIC(Shlezinger et al., 2020/2021)은 각각 Viterbi·소프트 간섭 소거의 학습판으로, 채널 지식 없이 데이터로 메트릭을 학습한다. 터보 수신기의 언폴딩(모델 구동 turbo-MIMO, Zhang et al., 2020)과 EM 반복 자체의 심층화(deep EM 기반 조인트 MIMO 추정·검출, Zhang et al., 2022)도 이 계열이다.

**(iii) 적응성 문제와 메타 학습.** 학습 수신기의 약점인 분포 이동(채널 통계 변화)에 대해, 소수 파일럿만으로 빠르게 적응하는 오프라인/온라인 메타 학습(Park–Simeone–Kang, 2021)이 제시되었다.

### 2.12 생성모델·파일럿리스·파운데이션 모델과 표준화 (2021–2026)

**생성모델 사전분포.** score 기반 생성모델을 채널 사전분포로 쓰는 채널 추정(Arvinte & Tamir, 2023)을 거쳐, **확산모델 기반 JCESD**(Zilberstein–Swami–Segarra, 2024)가 등장했다. 채널·심볼의 결합 사후분포에서 직접 샘플링하는 역확산 과정을 구성하되, 심볼에는 이산 성상 사전을, 채널에는 학습된 사전을 결합해 blind inverse problem을 푼다 — 1.4(c)의 쌍선형 관점이 생성모델의 언어로 재구현된 것으로, 파일럿 오버헤드 절감이 보고되었다. 재밍 환경용 Brownian bridge 확산 기반 조인트 추정·검출(2026) 등 변형이 빠르게 늘고 있다.

**파일럿리스를 향한 종단 학습.** Aoudia & Hoydis(2021)는 넓은 시간-주파수 창을 보는 신경 수신기가 직교 파일럿 수를 크게 줄일 수 있고, 나아가 superimposed pilot 또는 성상 자체를 수신기와 공동 학습하면 직교 파일럿을 완전히 제거하고도 BER 손실이 없음을 보였다 — 2.7절의 비코히어런트 이론이 예고했던 방향의 학습 기반 실현이다. 오픈소스 도구(Sionna, 2022)와 5G NR 규격 준수 다중 사용자 MIMO 신경 수신기의 실시간 구현(NVIDIA neural_rx)이 재현 연구의 기반을 넓혔다.

**표준화와 산업 동향.** 3GPP는 Rel-18에서 AI/ML 기반 무선 인터페이스 연구(CSI 피드백·빔 관리·측위)를 진행했고, 6G 연구 항목에서 물리계층 AI가 본격 검토되고 있다. 장비사들은 파일럿 외 자원 요소 전체를 활용해 채널 추정·등화를 수행하는 AI 수신기가 저SNR·고이동성 영역에서 가장 큰 이득을 낸다고 보고한다 — 고전 이론(2.7절)이 지목한 "조인트가 값진 영역"과 일치하는 관찰이다.

**파운데이션 모델.** 과제별 소형 모델의 일반화 한계를 넘기 위해, 대규모 무선 데이터로 사전학습한 물리계층 파운데이션 모델·대형 AI 모델 연구(예: Large AI Models for Wireless Physical Layer, 2025; LLM 기반 채널 예측 LLM4CP, 2024)가 2024년 이후 급증했다. JCESD 관점에서는 "추정·검출·복호를 포괄하는 범용 수신 표현 학습"이라는 새 질문이 열린 상태다.

### 2.13 새로운 파형·환경: OTFS, RIS, 고이동성 (2017–현재)

**OTFS**(Hadani et al., 2017)는 지연-도플러(DD) 영역에서 심볼을 싣는 파형으로, 고이동성에서 채널이 희소·준정적이 되는 성질 덕에 JCESD의 좋은 무대가 되었다. 메시지 패싱 검출(Raviteja et al., 2018)과 embedded pilot 기반 DD 채널 추정(Raviteja et al., 2019)이 표준 구성 요소가 되었고, 검출된 데이터를 파일럿으로 재활용해 추정을 정제하는 조인트 기법(ZP-OTFS 저PAPR 조인트, 2023 등), 하이브리드 RIS 결합 mmWave OTFS의 조인트 추정·검출(Li et al., 2022) 등이 이어진다. **RIS** 환경에서는 캐스케이드 채널의 차원 폭증이 파일럿 부담을 키워 조인트 접근(예: 저해상도 ADC RIS-massive MIMO의 BiG-AMP 기반 조인트, 2023)이 자연스러운 해법이 되며, 고이동성 시변 OFDM에서는 기저 전개 모델(BEM)과 SAGE/변분 추론을 결합한 조인트 추정·등화·검출 계열이 오래전부터 이어져 왔다(예: 2010년대 doubly-selective OFDM SAGE 수신기).

---

## 3. 한눈에 보는 타임라인

| 시기 | 이정표 | 대표 문헌 |
|---|---|---|
| 1965 | 결정지향 적응 등화 — 검출 결과로 수신기 갱신 | Lucky (BSTJ 1965) |
| 1973 | Adaptive MLSE — 채널 추정기 + Viterbi 검출의 최초 명시적 결합 | Magee & Proakis (IEEE T-IT 1973) |
| 1975–1980 | 블라인드 등화 (Sato, CMA) — 데이터 통계가 채널 지식의 원천 | Sato 1975; Godard 1980 |
| 1977 | EM 알고리즘 — 확률적 조인트의 수학적 틀 | Dempster–Laird–Rubin 1977 |
| 1988–1997 | EM/Baum–Welch 기반 조인트 추정·검출 정식화 | Feder & Weinstein 1988; Kaleh & Vallet 1994; Georghiades & Han 1997 |
| 1991–1995 | 2차 통계 블라인드 식별 (SIMO/부분공간) | Tong–Xu–Kailath 1994; Moulines et al. 1995 |
| 1994–1996 | 유한 알파벳 조인트 ML, 교대 최적화 (ILSP/ILSE) | Seshadri 1994; Talwar–Viberg–Paulraj 1996 |
| 1995 | Per-Survivor Processing — 트렐리스 내장형 조인트 | Raheli–Polydoros–Tzou 1995 |
| 1995–2002 | 터보 등화·반복 수신기·code-aided 채널 추정 | Douillard 1995; Wang & Poor 1999; Valenti & Woerner 2001; Tüchler 2002 |
| 1999–2003 | 비코히어런트 용량, Grassmann 시그널링, 훈련 최적화 | Marzetta & Hochwald 1999; Zheng & Tse 2002; Hassibi & Hochwald 2003 |
| 2001–2013 | 팩터 그래프 통합 설계, VMP/BP–MF/EP 수신기 | Worthen & Stark 2001; Kirkelund 2010; Riegler 2013 |
| 2009–2014 | AMP → GAMP → BiG-AMP (쌍선형 추론으로서의 JCESD) | Donoho 2009; Rangan 2011; Parker–Schniter–Cevher 2014 |
| 2010–2018 | Massive MIMO·파일럿 오염 → 준블라인드 재부상, JADCE | Marzetta 2010; Müller 2014; Wen 2016; Liu & Yu 2018 |
| 2017–2021 | 딥러닝 수신기: 암묵적 조인트, 언폴딩, 산업 실증 | Ye–Li–Juang 2018; He 2020 (OAMP-Net2); Honkala 2021 (DeepRx) |
| 2021–2022 | 파일럿리스 종단 학습, 오픈소스 생태계 | Aoudia & Hoydis 2021; Sionna 2022 |
| 2023–2026 | 확산모델 기반 JCESD, OTFS/RIS 조인트, 파운데이션 모델, 3GPP AI-PHY | Arvinte & Tamir 2023; Zilberstein 2024; Guo et al. 2025 |

---

## 4. 방법론 분류 (Taxonomy)와 통일적 관점

| 계열 | 대표 기법 | 채널 취급 | 심볼 취급 | 최적성/보장 | 복잡도 경향 |
|---|---|---|---|---|---|
| 교대 최적화 | ILSP/ILSE, alternating LS | 점추정 (LS) | 하드 결정 | 비용 단조 감소, 국소 최소 다수 | 낮음 |
| 트렐리스 내장 | adaptive MLSE, PSP | 생존 경로별 점추정 | 시퀀스 가설 | 근사 조인트 MLSE | 상태 수 비례 |
| EM/SAGE | Baum–Welch 조인트, SAGE 수신기 | 점추정 (M-step) | 소프트 사후 (E-step) | 우도 단조 증가, 국소 최대 | 중간 |
| 터보/code-aided | 터보 등화 + 반복 채널 추정 | 소프트 심볼 기반 LMMSE | 소프트 (LLR) | EXIT로 수렴 분석 | 중간 |
| 메시지 패싱/변분 | BP, VMP, BP–MF, EP, BiG-AMP | 근사 사후분포 | 근사 사후분포 | 특정 극한에서 Bayes-최적 접근 (state evolution) | 중간–낮음 |
| 최적화/완화 | GLRT + SDR, 격자 기법 | 소거 (농축 우도) | 완화 후 반올림 | 특수 구조에서 (준)최적 | 문제 의존 |
| 학습: 데이터 구동 | FC-DNN (Ye 2018), DeepRx | 암묵적 (내재 표현) | 신경망 출력 | 경험적 | 추론 낮음, 학습 비용 큼 |
| 학습: 모델 구동 | ComNet, OAMP-Net2, DeepSIC, deep EM | 구조는 고전, 파라미터 학습 | 반복층의 소프트 추정 | 고전 구조의 해석성 일부 유지 | 낮음–중간 |
| 학습: 생성모델 | 확산모델 JCESD | 학습된 사전 + 사후 샘플링 | 이산 사전 + 샘플링 | 사후 샘플링 근사 | 높음 (샘플링 스텝) |

**통일적 관점 (보고서의 서사로 추천).** 표의 대부분은 1.4(b)의 다루기 힘든 결합 사후분포 $p(\mathbf{X}_d,\mathbf{H}\mid\mathbf{Y})$를 서로 다른 방식으로 근사하는 한 가족이다. EM은 채널 쪽 분포를 점질량으로 제한한 평균장의 특수형이고, 교대 최적화는 양쪽 모두 점질량으로 제한한 극단이며, 터보 반복은 팩터 그래프 위 특정 메시지 스케줄이고, 언폴딩 네트워크는 그 반복을 유한 층으로 자르고 파라미터를 데이터로 보정한 것이다. 확산모델 JCESD는 같은 사후분포를 근사 최적화 대신 **샘플링**으로 공략한다. "근사 추론의 진화사"라는 축으로 50년을 꿰면 보고서의 이야기가 하나로 정리된다.

---

## 5. 이론적 한계와 성능 지표

**지표.** 추정 품질은 (N)MSE, 검출 품질은 SER/BER(부호화 없는 경우 — 이때는 "심볼 검출 성능"이라 부르는 것이 정확하다), 부호화 시스템은 BLER, 시스템 관점은 유효 전송률(파일럿 오버헤드 반영 achievable rate)로 측정한다. 시뮬레이션에는 완전 CSI(genie-aided) 검출과 파일럿-온리 추정이라는 두 기준선을 함께 그리는 것이 관례다 — 조인트 기법의 이득이 그 사이 어디까지 도달했는지가 핵심 축이기 때문이다.

**추정 하한.** 데이터 심볼이 랜덤 뉘슨스 파라미터로 끼어드는 상황의 추정 하한으로는 표준 CRB 대신 **modified CRB**(D'Andrea–Mengali–Reggiannini, 1994)가 널리 쓰인다. MCRB는 뉘슨스에 대한 기대를 피셔 정보 계산 안으로 넣어

$$
\mathrm{MCRB}(\boldsymbol{\theta}) = \Big(\mathbb{E}_{\mathbf{X}_d}\big[\mathbf{J}(\boldsymbol{\theta};\mathbf{X}_d)\big]\Big)^{-1}
\ \preceq\ \mathrm{CRB}(\boldsymbol{\theta})
$$

형태의 (일반적으로 더 낙관적인) 하한을 준다. 파일럿-온리/준블라인드/블라인드 각각의 CRB 비교(de Carvalho & Slock, 1997)는 데이터가 추정에 기여하는 정보량을 정량화하는 표준 도구다.

**시스템 수준 한계.** 2.7절의 세 결과가 기둥이다: (i) 비코히어런트 용량과 DoF 인자 $1-N^{*}/T$ (채널 획득의 불가피한 비용), (ii) 파일럿 기반 하한과 최적 훈련 설계 $T_p=N_t$ (전력 최적화 시), (iii) 그 하한과 비코히어런트 용량의 간극 — 이 간극이 곧 JCESD가 회수할 수 있는 이론적 상한이다. 대규모 시스템 극한에서는 (BiG-)AMP의 state evolution이 반복 수신기의 도달 성능을 예측하는 해석 도구가 된다.

---

## 6. 열린 문제와 연구 기회

1. **성능–복잡도–지연의 3자 절충.** 확산모델 JCESD는 성능이 좋지만 샘플링 비용이 크고, 언폴딩은 가볍지만 도달 성능에 한계가 있다. 실시간(슬롯 단위) 제약 하의 파레토 경계는 아직 정리되지 않았다.
2. **학습 수신기의 일반화·강건성.** 분포 이동(채널 통계, SNR, 파일럿 패턴 변화)과 적대적 교란에 대한 학습 기반 JCESD의 취약성은 반복형 고전 기법과의 체계적 비교가 진행 중인 주제다(예: DL vs. 반복 알고리즘 비교 연구, arXiv:2303.03678). 온라인 적응·메타 학습·모델 구동 구조가 완충 장치로 연구된다.
3. **이론 보증.** 학습된 JCESD의 수렴·최적성 보장은 거의 없다. 언폴딩과 state evolution, 자유에너지 관점을 잇는 해석이 열려 있다.
4. **고이동성·이중 분산 채널.** OTFS를 포함한 DD 영역 JCESD에서 파일럿 오버헤드(guard 영역)와 PAPR, 프레임 구조의 공동 설계가 활발하다.
5. **하드웨어 제약 결합.** 저해상도 ADC, 위상 잡음, 비선형 PA와의 결합 조인트 문제는 쌍선형을 넘어 다중선형/비선형 역문제가 된다.
6. **파일럿 설계의 공동 최적화.** superimposed pilot·성상·수신기의 종단 공동 학습(파일럿리스)과 표준 호환성(기존 DM-RS 패턴과의 공존) 사이의 간극.
7. **확장 환경.** cell-free/XL-MIMO(근접장), RIS 캐스케이드 채널, ISAC(감지 보조 추정)에서의 조인트 정식화.
8. **파운데이션 모델 시대의 질문.** 과제별 모델을 넘어, 추정·검출·복호를 아우르는 범용 수신 표현의 사전학습이 JCESD의 이득 구조를 바꾸는지 — 2024년 이후 막 열린 물음이다.

---

## 7. 연구 보고서 구성 제안

조사 내용을 보고서로 옮길 때 다음 구성이 자연스럽다. (1) 서론: 닭-달걀 문제와 분리형의 세 가지 비용(1.1절), (2) 문제 정식화: 조인트 ML → GLRT → 베이지안 주변화의 위계(1.4절), (3) 역사: "근사 추론의 진화"라는 축으로 2절의 이정표를 배치하고 타임라인 표(3절)로 요약, (4) 방법론 비교: 4절 표 + 각 계열의 핵심 수식 1–2개, (5) 이론 한계: 5절의 세 기둥, (6) 동향과 열린 문제: 6절, (7) 결론. 분량 제약이 있으면 2.2(블라인드 등화)와 2.4(i)(SOS 식별)는 배경으로 압축해도 본류(EM→터보→메시지 패싱→학습)의 서사는 유지된다.

---

## 8. 참고문헌 (시대순, 검증된 항목 위주)

**고전·태동기**
1. R. W. Lucky, "Automatic equalization for digital communication," Bell Syst. Tech. J., 1965.
2. F. R. Magee and J. G. Proakis, "Adaptive maximum-likelihood sequence estimation for digital signaling in the presence of intersymbol interference," IEEE Trans. Inf. Theory, 1973.
3. Y. Sato, "A method of self-recovering equalization for multilevel amplitude-modulation systems," IEEE Trans. Commun., 1975.
4. A. P. Dempster, N. M. Laird, and D. B. Rubin, "Maximum likelihood from incomplete data via the EM algorithm," J. Roy. Statist. Soc. B, 1977.
5. D. N. Godard, "Self-recovering equalization and carrier tracking in two-dimensional data communication systems," IEEE Trans. Commun., 1980.

**EM·블라인드·유한 알파벳 (1988–1999)**
6. M. Feder and E. Weinstein, "Parameter estimation of superimposed signals using the EM algorithm," IEEE Trans. Acoust., Speech, Signal Process., 1988.
7. O. Shalvi and E. Weinstein, "New criteria for blind deconvolution of nonminimum phase systems (channels)," IEEE Trans. Inf. Theory, 1990.
8. D. Divsalar and M. K. Simon, "Multiple-symbol differential detection of MPSK," IEEE Trans. Commun., 1990.
9. L. Tong, G. Xu, and T. Kailath, "Blind identification and equalization based on second-order statistics: A time domain approach," IEEE Trans. Inf. Theory, 1994.
10. N. Seshadri, "Joint data and channel estimation using blind trellis search techniques," IEEE Trans. Commun., 1994.
11. G. K. Kaleh and R. Vallet, "Joint parameter estimation and symbol detection for linear or nonlinear unknown channels," IEEE Trans. Commun., 1994.
12. A. N. D'Andrea, U. Mengali, and R. Reggiannini, "The modified Cramer–Rao bound and its application to synchronization problems," IEEE Trans. Commun., 1994.
13. J. A. Fessler and A. O. Hero, "Space-alternating generalized expectation-maximization algorithm," IEEE Trans. Signal Process., 1994.
14. E. Moulines, P. Duhamel, J.-F. Cardoso, and S. Mayrargue, "Subspace methods for the blind identification of multichannel FIR filters," IEEE Trans. Signal Process., 1995.
15. R. Raheli, A. Polydoros, and C.-K. Tzou, "Per-survivor processing: A general approach to MLSE in uncertain environments," IEEE Trans. Commun., 1995.
16. S. Talwar, M. Viberg, and A. Paulraj, "Blind separation of synchronous co-channel digital signals using an antenna array — Part I: Algorithms," IEEE Trans. Signal Process., 1996.
17. E. de Carvalho and D. T. M. Slock, "Cramer–Rao bounds for semi-blind, blind and training sequence based channel estimation," Proc. IEEE SPAWC, 1997.
18. C. N. Georghiades and J. C. Han, "Sequence estimation in the presence of random parameters via the EM algorithm," IEEE Trans. Commun., 1997.
19. B. H. Fleury et al., "Channel parameter estimation in mobile radio environments using the SAGE algorithm," IEEE J. Sel. Areas Commun., 1999.
20. P. Hoeher and F. Tufvesson, "Channel estimation with superimposed pilot sequence," Proc. IEEE GLOBECOM, 1999.

**터보·반복 수신기 (1993–2002)**
21. C. Berrou, A. Glavieux, and P. Thitimajshima, "Near Shannon limit error-correcting coding and decoding: Turbo-codes," Proc. IEEE ICC, 1993.
22. C. Douillard et al., "Iterative correction of intersymbol interference: Turbo-equalization," Eur. Trans. Telecommun., 1995.
23. X. Wang and H. V. Poor, "Iterative (turbo) soft interference cancellation and decoding for coded CDMA," IEEE Trans. Commun., 1999.
24. S. ten Brink, "Convergence behavior of iteratively decoded parallel concatenated codes," IEEE Trans. Commun., 2001.
25. M. C. Valenti and B. D. Woerner, "Iterative channel estimation and decoding of pilot symbol assisted turbo codes over flat-fading channels," IEEE J. Sel. Areas Commun., 2001.
26. M. Tüchler, R. Koetter, and A. C. Singer, "Turbo equalization: Principles and new results," IEEE Trans. Commun., 2002.

**정보이론 (1999–2003)**
27. T. L. Marzetta and B. M. Hochwald, "Capacity of a mobile multiple-antenna communication link in Rayleigh flat fading," IEEE Trans. Inf. Theory, 1999.
28. L. Zheng and D. N. C. Tse, "Communication on the Grassmann manifold: A geometric approach to the noncoherent multiple-antenna channel," IEEE Trans. Inf. Theory, 2002.
29. B. Hassibi and B. M. Hochwald, "How much training is needed in multiple-antenna wireless links?," IEEE Trans. Inf. Theory, 2003.

**팩터 그래프·메시지 패싱·AMP (2001–2018)**
30. F. R. Kschischang, B. J. Frey, and H.-A. Loeliger, "Factor graphs and the sum-product algorithm," IEEE Trans. Inf. Theory, 2001.
31. A. P. Worthen and W. E. Stark, "Unified design of iterative receivers using factor graphs," IEEE Trans. Inf. Theory, 2001.
32. H.-A. Loeliger et al., "The factor graph approach to model-based signal processing," Proc. IEEE, 2007.
33. D. L. Donoho, A. Maleki, and A. Montanari, "Message-passing algorithms for compressed sensing," Proc. Nat. Acad. Sci., 2009.
34. W. U. Bajwa, J. Haupt, A. M. Sayeed, and R. Nowak, "Compressed channel sensing: A new approach to estimating sparse multipath channels," Proc. IEEE, 2010.
35. G. E. Kirkelund, C. N. Manchón, L. P. B. Christensen, E. Riegler, and B. H. Fleury, "Variational message-passing for joint channel estimation and decoding in MIMO-OFDM," Proc. IEEE GLOBECOM, 2010.
36. S. Rangan, "Generalized approximate message passing for estimation with random linear mixing," Proc. IEEE ISIT, 2011.
37. P. Schniter, "A message-passing receiver for BICM-OFDM over unknown clustered-sparse channels," IEEE J. Sel. Topics Signal Process., 2011.
38. E. Riegler, G. E. Kirkelund, C. N. Manchón, M.-A. Badiu, and B. H. Fleury, "Merging belief propagation and the mean field approximation: A free energy approach," IEEE Trans. Inf. Theory, 2013.
39. C. Novak, G. Matz, and F. Hlawatsch, "IDMA for the multiuser MIMO-OFDM uplink: A factor graph framework for joint data detection and channel estimation," IEEE Trans. Signal Process., 2013.
40. J. T. Parker, P. Schniter, and V. Cevher, "Bilinear generalized approximate message passing — Parts I & II," IEEE Trans. Signal Process., 2014.
41. J. Céspedes, P. M. Olmos, M. Sánchez-Fernández, and F. Pérez-Cruz, "Expectation propagation detection for high-order high-dimensional MIMO systems," IEEE Trans. Commun., 2014.
42. S. Wu, L. Kuang, Z. Ni, D. Huang, Q. Guo, and J. Lu, "Message-passing receiver for joint channel estimation and decoding in 3D massive MIMO-OFDM systems," IEEE Trans. Wireless Commun., 2016.

**Massive MIMO (2010–2018)**
43. T. L. Marzetta, "Noncooperative cellular wireless with unlimited numbers of base station antennas," IEEE Trans. Wireless Commun., 2010.
44. H. Q. Ngo and E. G. Larsson, "EVD-based channel estimation in multicell multiuser MIMO systems with very large antenna arrays," Proc. IEEE ICASSP, 2012.
45. R. R. Müller, L. Cottatellucci, and M. Vehkaperä, "Blind pilot decontamination," IEEE J. Sel. Topics Signal Process., 2014.
46. C.-K. Wen et al., "Bayes-optimal joint channel-and-data estimation for massive MIMO with low-precision ADCs," IEEE Trans. Signal Process., 2016.
47. E. Nayebi and B. D. Rao, "Semi-blind channel estimation for multiuser massive MIMO systems," IEEE Trans. Signal Process., 2018.
48. L. Liu and W. Yu, "Massive connectivity with massive MIMO — Part I: Device activity detection and channel estimation," IEEE Trans. Signal Process., 2018.

**딥러닝·생성모델 (2017–2026)**
49. T. J. O'Shea and J. Hoydis, "An introduction to deep learning for the physical layer," IEEE Trans. Cogn. Commun. Netw., 2017.
50. H. Ye, G. Y. Li, and B.-H. Juang, "Power of deep learning for channel estimation and signal detection in OFDM systems," IEEE Wireless Commun. Lett., 2018.
51. X. Gao, S. Jin, C.-K. Wen, and G. Y. Li, "ComNet: Combination of deep learning and expert knowledge in OFDM receivers," IEEE Commun. Lett., 2018.
52. N. Samuel, T. Diskin, and A. Wiesel, "Learning to detect," IEEE Trans. Signal Process., 2019.
53. M. Soltani, V. Pourahmadi, A. Mirzaei, and H. Sheikhzadeh, "Deep learning-based channel estimation," IEEE Commun. Lett., 2019.
54. H. He, C.-K. Wen, S. Jin, and G. Y. Li, "Model-driven deep learning for MIMO detection," IEEE Trans. Signal Process., 2020. (OAMP-Net2)
55. X. Yi and C. Zhong, "Deep learning for joint channel estimation and signal detection in OFDM systems," IEEE Commun. Lett., 2020.
56. N. Shlezinger, N. Farsad, Y. C. Eldar, and A. J. Goldsmith, "ViterbiNet: A deep learning based Viterbi algorithm for symbol detection," IEEE Trans. Wireless Commun., 2020.
57. N. Shlezinger, R. Fu, and Y. C. Eldar, "DeepSIC: Deep soft interference cancellation for multiuser MIMO detection," IEEE Trans. Wireless Commun., 2021.
58. M. Honkala, D. Korpi, and J. M. J. Huttunen, "DeepRx: Fully convolutional deep learning receiver," IEEE Trans. Wireless Commun., 2021.
59. S. Park, O. Simeone, and J. Kang, "Learning to demodulate from few pilots via offline and online meta-learning," IEEE Trans. Signal Process., 2021.
60. F. Ait Aoudia and J. Hoydis, "End-to-end learning for OFDM: From neural receivers to pilotless communication," IEEE Trans. Wireless Commun., 2021. (arXiv:2009.05261)
61. J. Hoydis et al., "Sionna: An open-source library for next-generation physical layer research," arXiv:2203.11854, 2022.
62. Y. Zhang, J. Sun, J. Xue, G. Y. Li, and Z. Xu, "Deep expectation-maximization for joint MIMO channel estimation and signal detection," IEEE Trans. Signal Process., 2022.
63. M. Arvinte and J. I. Tamir, "MIMO channel estimation using score-based generative models," IEEE Trans. Wireless Commun., 2023.
64. N. Zilberstein, A. Swami, and S. Segarra, "Joint channel estimation and data detection in massive MIMO systems based on diffusion models," Proc. IEEE ICASSP, 2024. (arXiv:2311.10311)
65. J. Guo, Y. Cui, S. Jin, and J. Zhang, "Large AI models for wireless physical layer," arXiv:2508.02314, 2025.

**OTFS·RIS·비교 연구**
66. R. Hadani et al., "Orthogonal time frequency space modulation," Proc. IEEE WCNC, 2017.
67. P. Raviteja, K. T. Phan, Y. Hong, and E. Viterbo, "Interference cancellation and iterative detection for orthogonal time frequency space modulation," IEEE Trans. Wireless Commun., 2018.
68. P. Raviteja, K. T. Phan, and Y. Hong, "Embedded pilot-aided channel estimation for OTFS in delay–Doppler channels," IEEE Trans. Veh. Technol., 2019.
69. M. Li, S. Zhang, Y. Ge, F. Gao, and P. Fan, "Joint channel estimation and data detection for hybrid RIS aided millimeter wave OTFS systems," IEEE Trans. Commun., 2022.
70. "A comparative study of deep learning and iterative algorithms for joint channel estimation and signal detection in OFDM systems," arXiv:2303.03678, 2023.

> 표기 주의: 위 목록은 조사 시점에서 저자·연도·게재지를 확인한 항목들이다. 보고서에 인용할 때는 각 항목의 권·호·쪽수를 원문에서 최종 확인할 것.

---

## 9. 표기법

굵은 소문자($\mathbf{x}$)는 벡터, 굵은 대문자($\mathbf{X}$)는 행렬, $(\cdot)^{H}$는 켤레 전치, $(\cdot)^{\dagger}$는 의사역행렬, $\|\cdot\|_F$는 Frobenius 노름, $\mathcal{A}$는 심볼 성상, $\mathcal{CN}$은 순환 대칭 복소 가우시안, $\Pi_{\mathcal{A}}(\cdot)$는 성상으로의 성분별 사영, $\mathrm{CE}$는 교차 엔트로피, $\mathcal{L}^{\mathrm{ext}}$는 외재 LLR을 뜻한다.
