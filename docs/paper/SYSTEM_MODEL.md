# 시스템 모델과 수학적 정식화: 코드에 구현된 그대로

**범위.** 이 문서는 D2 testbed의 두 셀을 다룹니다. 헤드라인 셀 C2(8×4)와 공차원 축 셀 C6(16×4)에서 실제로 돌아간 다음 요소를 식으로 적었습니다.
- 신호 모델
- 채널
- 반복 수신기
- prior 네 종
- 평가 규칙

**경로 표기.**
- `Demo/…`와 `conf/code/…`는 저장소 루트 기준 경로입니다.
- 기록 파일(`results/…`, `logs/…`, `raw_…`, `ckpt/…`)과 스펙 문서(`10_SPEC_stageC.md` 등)는 `conf/` 기준 경로입니다.

**기준 코드.**
- 기준 커밋은 `54d68a14`입니다.
- 모든 기록 헤더에 적힌 수신기 해시는 `t2_route_a.py=95a5408901ec125c  t2_trellis.py=31cd0ee9c68e972b  t2_gmm.py=d064e58c7510c769`입니다(`results/guard_D2_B16e4k.txt:8`, `results/nr16b_batched_check.txt:8`).

**태그.**
- **[코드]**: 코드에서 직접 읽은 것
- **[유도]**: 코드의 식에서 우리가 유도한 것. 코드 안에는 없습니다.
- **[가정]**: 원고에 모델링 가정으로 밝혀야 하는 것
- **[기록]**: 결과 기록(표, 로그, raw meta, fit 파일, checkpoint 필드)에서 가져온 것
- **[가설]**: 기록이 시사하지만 증명되지 않은 해석. 원고에서는 가설로만 씁니다.

**용어 규칙.**
- genie(R5)는 **같은 루프에 참 $\mathbf H$를 넣은 known-channel 참조 수신기**입니다. bound가 아닙니다(§3.6).
- $p\ge0.05$이거나 검정력 가드를 넘지 못한 비교는 "차이 없음"이 아니라 **판정하지 못함**입니다.

**원고용 arm 이름 대응.**

| 원고 이름 | 코드 arm |
|---|---|
| Gaussian | `R2-ours-G` |
| b\* | `M-ours-bstar` |
| V0 | `M-ours-dscore-C-V0` |
| V1 | `M-ours-dscore-C-V1` |
| V1-edge | `V1-edge` (K2) |
| genie | `R5-genie` |

---

## 요지: 원고 순서대로 (어디서, 얼마나, 왜 → 범위는 §6.2)

1. **비교가 분리하는 것.** 모든 arm은 같은 3-모듈 루프를 공유합니다. 검출기, BCJR, 감쇠, 16회 반복이 같고, prior는 Module H 한 곳에만 들어갑니다(§3.2).
   - [코드] `conf/code/arms.py:18-38`
   - [기록] `results/tests.txt:35`: M2, 차이 0.0. M2가 확인하는 것은 Gaussian 경우 하나입니다. b\*와 score arm이 Module H 필드만 다르다는 근거는 위 코드입니다(§3.2).
2. **어디서, 얼마나.**
   - **C2 헤드라인 (N′=1.6e5)** [기록]
     - b\*→V1 짝지은 부호검정은 판정점 3/3에서 유의했고, pooled 454:78, $p=1.7\times10^{-65}$입니다.
     - SNR@0.1 격차는 **+1.41 dB** [90% paired bootstrap 1.22, 1.64]입니다(`results/tables_D2_B16e4k.txt:368-372`).
     - −3 dB 실패 수(n=2560)는 b\* 623, V1 371, genie 87입니다. 회수율은 $\mathcal R=0.470$ [0.427, 0.512]입니다(`results/review_next/recovery_B16e4k.txt:2`).
   - **C6 (Nr=16, 공차원 축)** [기록]
     - 지위: UNGATED이므로 arm 판정이 아니라 "기하·예산 축 측정"입니다.
     - b\*→V1은 213:18, 3/3입니다(`results/tables_D2_NR16B16e4.txt:370-372`).
     - −3 dB 실패 수는 b\* 184, V1 53, genie 22이고, $\mathcal R=0.809$ [0.747, 0.870]입니다(`results/review_next/recovery_NR16B16e4.txt:2`).
     - 이 수치는 회수율 대역 문장과 반드시 함께 씁니다(`results/review_next/NEXT_EXPERIMENTS_C6B16e4.md:28,44`).
     - GMM 쪽 캐비엇 두 가지(b\*가 격자 끝, b\*가 덜 수렴했을 수 있음)도 함께 붙입니다. 둘 다 V1에 유리한 방향입니다(§6.2 3항, `:135`).
3. **왜: 정식화 수준에서 말할 수 있는 것.**
   - 학습 denoiser의 Jacobian을 EP 행렬 site로 쓸 때, $\mathrm{Herm}(\mathbf J)$에 음의 고유값이 있으면 site 평균이 폭주할 수 있습니다 [유도, 근사; §4.4]. 참 MMSE denoiser라면 Jacobian이 PSD입니다(§4.3 (e)).
   - V1은 PSD 투영으로 이 조건을 강제합니다. 투영이 없는 V0에서는 다음 결과가 나왔습니다 [기록, §4.4].
     - C2: 블록의 53–93%에서 발산 가드가 발동했습니다.
     - C2 −3 dB에서 Gaussian 대비 166:844로 더 나빴습니다.
   - "학습 prior가 GMM보다 나은 이유가 D2의 저차원 지지 집합 때문"이라는 설명은 **[가설]**입니다(§4.4, §6.2).
4. **범위와 한계**는 §6.2에 전부 모았습니다. 등록된 캐비엇은 하나도 빼지 않았습니다.

---

## 0. 표기

| 기호 | 의미 | 코드 이름 / 출처 |
|---|---|---|
| $N_r,\,N_t,\,N=N_rN_t$ | 수신·송신 안테나 수($N_t=4$ 고정), 채널 벡터 차원 | `Nr, NT` (`conf/code/common.py:41`) |
| $T,\;T_p,\;T_d=T-T_p$ | 블록의 RE(열) 수, 파일럿 열 수, 데이터 열 수 | `T, Tp, Td` (`Demo/t2_route_a.py:253`) |
| $t$ | 블록 안의 열(RE) 번호. $\mathcal P$=파일럿 열, $\mathcal D$=데이터 열 | `n`, `c` |
| $a,\;b$ | 수신 안테나 번호, 송신 안테나(=layer) 번호 | |
| $\mathbf h=\mathrm{vec}(\mathbf H)$ | 열 우선 벡터화, $h_{a+N_rb}=H_{ab}$ (0-based) | `H.reshape(-1, order="F")` (`Demo/t2_route_a.py:8,323`) |
| $\sigma^2$ | 수신 안테나당·RE당 복소 잡음 분산 | `sigma2` |
| $j=1,\dots,16$ | 외부(turbo) 반복 번호 | `t` in `RouteA.run` |
| $\ell,\;L$ | D2의 경로 번호, 경로 수 | `L` (`conf/code/d2.py:65`) |
| $k$ | GMM 성분 번호 | |
| $i=1,\dots,N_s$ | 부호 심볼 번호, $N_s=N_tT_d$ | |
| $\pi$ | 심볼 인터리버 순열 | `perm` |
| $(\mathbf G,\mathbf b)$ | 채널 likelihood site: 정밀도 행렬, 선형항 | `G, b` |
| $d_t,\;e_b$ | 열 $t$의 유효 잡음 정밀도, 송신 안테나 $b$의 채널 에너지 추정 | `d`, `eh2` |
| $(\boldsymbol\Lambda,\boldsymbol\eta)$ | Module H의 prior site: 정밀도, 선형항 | 코드의 `P`는 $\boldsymbol\Lambda+\mathbf G$이고 `site_vec`이 $\boldsymbol\eta$ (`Demo/t2_route_a.py:318,374,376`) |
| $(\hat{\mathbf h},\boldsymbol\Sigma)$ | 채널 belief의 평균과 공분산 | `hpost, Sigma` |
| $(\mathbf h_E,\nu_E)$ | 등방 extrinsic (score arm에서만 쓰임) | `hE, nuE` |
| $(\mathbf q,\nu_q)$ | denoiser 질의: $\mathbf q\approx\mathbf h+\mathcal{CN}(\mathbf 0,\nu_q\mathbf I)$ | `q, nu_q` |
| $\mathbf m(\mathbf q,\nu),\;\mathbf J$ | denoiser 출력, 그 Wirtinger Jacobian $\partial\mathbf m/\partial\mathbf q$ | `hH, J` |
| $\varsigma=\sqrt{\nu/2}$ | 네트워크 입력의 실수 차원당 잡음 표준편차 | `sigma_t`, `NU_TO_SIGMA` (`conf/code/score.py:63-64`) |
| $\nu_{\rm lo},\nu_{\rm hi}$ | 측정 $\sigma$ 격자의 양 끝 ($\nu=2\varsigma^2$) | `s_lo, s_hi` (`conf/code/score.py:1100`) |
| $(\bar{\mathbf x},\mathbf v)$ | 복호기 a-posteriori 심볼 평균·분산 | `xbar_grid, v_grid` |
| $(\mathbf r^D,\boldsymbol\tau^D)$ | 복호기 extrinsic (감쇠 적용 후) | `rD, tauD` |
| $(\mathbf r^L,\boldsymbol\tau^L)$ | 검출기 extrinsic | `rL, tauL` |
| $\boldsymbol\Xi_t$ | 검출기의 유효 잡음 공분산 (채널 불확실성 포함) | `R` (`Demo/t2_route_a.py:398`) |
| $\hat{\mathbf C}$ | 학습 채널 집합의 표본 공분산 $\frac1{N'}\sum\mathbf h\mathbf h^H$ | `Chat` (`Demo/t2_gmm.py:145`) |
| $\mathbf R_{\rm t},\mathbf R_{\rm r}$ | D2 앙상블 공분산의 송신·수신 인자 | `Rt, Rr` (`conf/code/d2.py:105-117`) |
| $\lambda_{\min}=10^{-6}$ | 고유값 하한 | `LAM_MIN` (`conf/code/common.py:51`) |
| $N'$ | 채널 학습 예산(표본 수). 헤드라인은 $1.6\times10^5$ | `ntrain` |

---

## 1. 신호 모델

### 1.1 블록 페이딩 MIMO `[코드]`

$$
\mathbf Y=\mathbf H\mathbf X+\mathbf W,\qquad
\mathbf X=[\mathbf X_p\;\mathbf X_d]\in\mathbb C^{N_t\times T},\qquad
W_{at}\overset{\rm iid}{\sim}\mathcal{CN}(0,\sigma^2).
$$

- 식의 출처는 `Demo/t2_route_a.py:287-293`이고, 잡음은 `:292`에서 만듭니다.
- $\mathbf H$는 블록마다 한 번 뽑고, 블록의 $T$개 열 전체에서 같습니다.
- 한 블록에서 뽑는 순서는 $\mathbf H\to\mathbf u\to\pi\to\mathbf W$이고, 블록끼리는 독립입니다(`conf/code/runner.py:453-459`).
- 한 점의 모든 arm은 같은 $\mathbf Y$를 받습니다(`conf/code/runner.py:459,464-469`).

열 단위로 쓰면 다음과 같습니다 `[유도]`.

$$
\mathbf y_t=\mathbf H\mathbf x_t+\mathbf w_t=(\mathbf x_t^{T}\otimes\mathbf I_{N_r})\,\mathbf h+\mathbf w_t .
$$

**파일럿 위치는 결과에 영향이 없습니다.** `[유도]`
- 채널 쪽은 열들의 합 $\mathbf G=\sum_t\mathbf A_t$, $\mathbf b=\sum_t\mathbf b_t$만 씁니다(`Demo/t2_route_a.py:344-345`).
- 검출기는 데이터 열마다 따로 돌고, 자기 열의 $(\mathbf A_t,\mathbf b_t)$만 뺍니다(`:386-408`).
- 따라서 $T$개 열의 순서를 바꾸고 $\pi$와 $\mathbf X_p$의 열 번호만 맞춰 주면 같은 알고리즘이 됩니다. 달라지는 것은 부동소수점 합산 순서뿐입니다.

수치 점검 [기록] (`conf/code/pilot_position_check.py` → `results/review_next/pilot_position_check.txt`, 기록 `DECISIONS.md:205`)
- 조건: C2 기하, 0 dB, 해석적 $\mathbf C_{\rm ens}$ Gaussian prior (`conf/code/pilot_position_check.py:17`), D2 블록 30개, 16반복 (`results/review_next/pilot_position_check.txt:1`)
- (a) 데이터 열끼리, 파일럿 열끼리 순서를 무작위로 바꾸고 $\pi$와 $\mathbf X_p$의 열 번호를 맞췄을 때, 블록 오류 궤적(16회)이 같았던 블록 수 (`:2-4`):

  | 수신기 | 궤적 일치 | 최대 NMSE 차이 |
  |---|---|---|
  | RouteA-Gaussian | 30/30 | $2.73\times10^{-15}$ |
  | R3-BiG-AMP | 30/30 | $7.40\times10^{-9}$ |
  | R4-SC-VAMP | 30/30 | $1.71\times10^{-9}$ |

- (b) 파일럿을 $t\in\{0,4,8,12\}$로 흩어 놓았을 때 $(\mathbf G,\mathbf b)$의 상대 차이는 $4.79\times10^{-16}$입니다(`:5`). 이 항목은 채널 쪽 합만 비교했고, 수신기 전체 궤적은 돌리지 않았습니다.
- score arm과 b\*는 점검 대상에 넣지 않았습니다. 다만 같은 구조 논증이 적용됩니다.

### 1.2 OFDM 해석 `[가정]`

블록 하나를 **하나의 coherence 영역 안에 있는 RE $T=16$개**로 읽습니다. 예를 들면 부반송파 4개 × OFDM 심볼 4개입니다. 코드와 스펙에는 이 해석이 없으므로(§6.1 F19), 원고에서 다음 다섯 가지를 가정으로 밝혀야 합니다.

- **(A1)** CP가 지연 확산보다 깁니다. 그래서 RE마다 $\mathbf y_t=\mathbf H\mathbf x_t+\mathbf w_t$가 성립합니다(ISI·ICI 없음).
- **(A2)** 16개 RE 전체에서 주파수 영역 채널 행렬 $\mathbf H$가 정확히 같습니다(RE 영역의 block fading). 영역끼리는 독립입니다. 이 가정 아래에서 §1.1의 파일럿 위치 불변성이 성립합니다.
- **(A3)** 파일럿 RE는 $T_p$개이고, C2와 C6에서 다음 두 조건을 만족합니다.
  - $\mathbf X_p\mathbf X_p^H=N_t\mathbf I$
  - 파일럿 RE 하나의 총 에너지는 $N_t$로, 데이터 RE 하나의 총 에너지(포트당 1)와 같습니다.
  - 코드의 DFT 파일럿(§1.4)은 여기에 더해 각 파일럿 RE에서 $N_t$개 포트를 모두 보냅니다. 아래의 분포 동치에는 이 성질이 필요하지 않습니다.
- **(A4)** 부호어 하나($K$ 정보 비트)가 영역 하나 안에 갇힙니다. 여러 PRB에 걸친 주파수 다이버시티가 없으므로, 보고하는 BLER은 **영역당 부호어 BLER**입니다.
- **(A5)** D2의 경로 위상 $\psi_\ell$(§2.1)은 그 영역 위치에서의 위상입니다. 지연에 따른 위상 $e^{-j2\pi f\tau_\ell}$를 흡수한 값입니다. 코드는 지연, Doppler, 영역 간 상관을 **모델링하지 않습니다**(`conf/code/d2.py:143-155`).

**NR DM-RS와의 대응 `[유도]` (코드로 검증하지 않음).**

(A2) 아래에서 파일럿 열의 로그 likelihood는 $h$에 대해 다음 두 양에만 의존합니다.

$$
\sum_{t\in\mathcal P}\frac{\|\mathbf y_t-\mathbf H\mathbf x_t\|^2}{\sigma^2}
=\text{const}-\frac{2}{\sigma^2}\Re\,\mathrm{tr}\!\big(\mathbf H^H\mathbf Y_p\mathbf X_p^H\big)+\frac1{\sigma^2}\mathrm{tr}\!\big(\mathbf H\mathbf X_p\mathbf X_p^H\mathbf H^H\big),
$$

즉 $(\mathbf Y_p\mathbf X_p^H,\ \mathbf X_p\mathbf X_p^H)$입니다. 코드로 쓰면 $\mathbf G_{\rm pilot}=\sigma^{-2}(\mathbf X_p\mathbf X_p^H)^*\otimes\mathbf I_{N_r}$, $\mathbf b_{\rm pilot}=\sigma^{-2}\mathrm{vec}(\mathbf Y_p\mathbf X_p^H)$입니다(§3.1).

$\mathbf X_p\mathbf X_p^H=N_t\mathbf I$이면 $\mathbf b_{\rm pilot}=\sigma^{-2}(N_t\mathbf h+\mathbf w')$, $\mathbf w'\sim\mathcal{CN}(\mathbf 0,N_t\sigma^2\mathbf I)$입니다. 따라서 이 조건을 만족하는 직교 cover라면 무엇이든 "$\mathbf H$와 수신기 입력"의 결합 분포가 같고, **BLER의 분포가 같습니다**. 블록별 실현은 다릅니다.

NR에서 이 조건을 만족하는 구성은 둘입니다. 원고에서는 **하나를 정해 명시해야** 합니다.
- **(a) double-symbol type-1 DM-RS의 한 CDM 그룹**
  - 포트 {1000, 1001, 1004, 1005}가 FD-OCC $[+1,\pm1]$ × TD-OCC $[+1,\pm1]$로 부반송파 2개 × 심볼 2개에 실립니다(TS 38.211 V19.5.0 Table 7.4.1.1.2-1).
  - 수열 $r(m)$의 크기가 1이면 $\mathbf X_p=\mathbf W\,\mathrm{diag}(\mathbf r)$이므로 $\mathbf X_p\mathbf X_p^H=\mathbf W\mathbf W^H=4\mathbf I$입니다.
  - "데이터 없는 CDM 그룹 1개"의 PDSCH/DM-RS EPRE 비는 0 dB입니다(TS 38.214 V19.5.0 Table 4.1-1). 따라서 (A3)와 일치합니다.
- **(b) single-symbol type-1, 4 포트**
  - CDM 그룹 2개({1000,1001}과 {1002,1003})가 FDM으로 나뉩니다. 같은 EPRE라면 파일럿 RE 4개에서 $\mathbf X_p\mathbf X_p^H=2\mathbf I$입니다.
  - "데이터 없는 CDM 그룹 2개"의 EPRE 비는 −3 dB이고(같은 표), 이 3 dB DM-RS boost를 넣어야 $4\mathbf I$가 됩니다. 이때 RE당 총 에너지도 $N_t$가 됩니다.
  - 즉 (b)는 이 boost를 포함할 때에만 (A3)를 만족합니다. 이때도 RE마다 포트가 2개뿐이라 코드의 DFT 파일럿과 모양이 다릅니다. (b)는 $\mathbf X_p\mathbf X_p^H=4\mathbf I$를 통해 위 분포 동치 부류에 들 뿐입니다.

추가로, 파일럿 비율은 $T_p/T=0.25$입니다. 이 값이 NR 슬롯의 DM-RS 밀도와 같다고 주장하지 않습니다.

### 1.3 SNR 정의 `[코드]`

$$
\sigma^2=10^{-\mathsf{SNR}_{\rm dB}/10}\qquad(\texttt{conf/code/runner.py:314},\ \texttt{conf/code/sigma.py:29}).
$$

- 심볼 에너지는 $\mathbb E|x_{bt}|^2=1$입니다. QPSK와 DFT 파일럿이 모두 단위 에너지입니다.
- D2에서는 **모든 원소가** $\mathbb E|H_{ab}|^2=1$입니다(§2.2).
- 따라서 $\mathsf{SNR}=\mathbb E|H_{ab}x_{bt}|^2/\sigma^2$는 **layer 하나가 수신 안테나 하나에서 갖는 평균 SNR**입니다.
- 송신 전력은 $N_t$로 나누지 않으므로 $\mathbb E\|\mathbf x_t\|^2=N_t$입니다.
- 이것은 앙상블 평균이며, $\|\mathbf H\|_F^2$는 블록마다 다릅니다.

여기서 다음이 따라 나옵니다 `[유도]`.
- **수신 안테나당 총 수신 SNR**은 $N_t\cdot\mathsf{SNR}$, 즉 $+6.02$ dB입니다. 헤드라인 −3 dB는 안테나당 총 수신 SNR +3.02 dB에 해당합니다.
- **$E_b/N_0$ (수신 안테나 하나 기준, 파일럿 에너지 포함, $T_p=N_t$)**
  - 파일럿의 평균 수신 에너지는 $\mathrm{tr}(\mathbf R_{\rm t}^T\mathbf X_p\mathbf X_p^H)$입니다.
  - $T_p=N_t$이면 이 값이 $N_t\,\mathrm{tr}\,\mathbf R_{\rm t}=N_t^2$이고, 블록 전체 에너지는 $N_tT$입니다.
  - 따라서 $E_b/N_0=\mathsf{SNR}+10\log_{10}(N_tT/K)$이고, C2와 C6에서는 **$\mathsf{SNR}+1.83$ dB**입니다. 이것은 차이값이며, 헤드라인 −3 dB에서는 **$E_b/N_0=-1.17$ dB**입니다.
  - 데이터 에너지만 세면 $\mathsf{SNR}+10\log_{10}(N_tT_d/K)=\mathsf{SNR}+0.58$ dB입니다.
  - $T_p<N_t$(C1, C5)에서는 $\mathbf R_{\rm t}\ne\mathbf I$(고유값 1.2103/1.0857/0.9776/0.7264, `results/testbed_D2.txt:15`)이므로 파일럿 에너지가 $N_tT_p$가 아닙니다. 위 식을 그대로 쓰지 않습니다.
- 어느 스펙에도 SNR 정의가 문장으로 적혀 있지 않습니다(§6.1 F10).

### 1.4 파일럿 `[코드]`

$$
[\mathbf F_{N_t}]_{bc}=e^{-j2\pi bc/N_t}\ (b,c=0..N_t-1),\qquad \mathbf X_p=[\mathbf F_{N_t}]_{:,\,0:T_p-1}
\qquad(\texttt{Demo/t2_route_a.py:242-244}).
$$

- 원소의 크기는 모두 1입니다.
- $T_p=N_t$(C2, C6)이면 $\mathbf X_p\mathbf X_p^H=N_t\mathbf I$입니다.
- **DFT를 쓰는 이유는 T2b 판정입니다.** 송신 측 앙상블 공분산 $\mathbf R_{\rm t}$의 유효 rank가 $0.9N_t$ 이상이면 DFT를 씁니다(`conf/code/common.py:125-137`, `conf/code/d2.py:105-117`). 기록값은 erank $=3.877\ge3.6$입니다 [기록] (`results/testbed_D2.txt:15`).
- C1($T_p=2$)과 C5($T_p=3$)는 앞쪽 $T_p$개 열만 쓰므로 $\mathbf X_p\mathbf X_p^H\ne N_t\mathbf I$입니다.

### 1.5 부호, 변조, 인터리버 `[코드]`

- **부호.** rate-1/2 feed-forward 컨볼루션 부호입니다.
  - 생성다항식은 $(133,171)_8$, 메모리 $\nu=6$(64 상태)입니다.
  - 0 꼬리 비트 6개로 종단합니다(`conf/code/common.py:39`, `Demo/t2_trellis.py:23-43`).
- **변조.** 트렐리스 한 섹션의 출력 비트 두 개가 QPSK 심볼 하나가 됩니다(`Demo/t2_trellis.py:50-59,106-109`).
$$
s_i=\tfrac{1}{\sqrt2}\big[(1-2c_{2i-1})+j(1-2c_{2i})\big],\qquad i=1..N_s,\quad N_s=N_tT_d .
$$
- **정보 비트 수.** $K=N_s-6$, 즉 $K=N_t(T-T_p)-6$입니다(`Demo/t2_route_a.py:224`, `conf/code/analysis.py:270`).
- **인터리버.** 심볼 단위이고, 블록마다 균등 랜덤 순열 $\pi$를 새로 뽑습니다(`conf/code/runner.py:458`). 수신기는 $\pi$를 압니다.
  - 배치 규칙: $[\mathbf X_d]_{b,n}=s_i\iff\pi(i)=nN_t+b$ (0-based, `Demo/t2_route_a.py:289-290`)
  - 비트 인터리빙이 없으므로 BICM이 아닙니다. 복호는 심볼 단위의 정확한 BCJR입니다(§3.4).

### 1.6 셀 `[코드]`

| 셀 | $N_r\times N_t$ | $T$ | $T_p$ | $N_s$ | $K$ | $K/2N_s$ | SNR 격자 (dB) | 지위 |
|---|---|---|---|---|---|---|---|---|
| C1 | 8×4 | 16 | 2 | 56 | 50 | 0.446 | −3:3:15 | 파일럿 예산 축. K2(V1-edge) 셀 |
| **C2** | 8×4 | 16 | 4 | 48 | 42 | 0.4375 | −3:3:15 | **헤드라인** (D1 형제 게이트를 통과한 레시피) |
| C5 | 8×4 | 16 | 3 | 52 | 46 | 0.442 | −3:3:15 | 파일럿 예산 축 |
| C6 | 16×4 | 16 | 4 | 48 | 42 | 0.4375 | −3:3:15 | 공차원 축. **UNGATED 측정** |

- 셀 정의: `conf/code/common.py:55-71`
- C6가 C2와 다른 점은 $N_r$ 하나뿐입니다(`:64-70`).
- 지위의 근거: `conf/code/arms.py:158-162`, `LADDER_C.md:1`, `results/review_next/NEXT_EXPERIMENTS_C6B16e4.md:28`

---

## 2. 채널 모델

### 2.1 D2: 희소 정반사 다중경로 (주장용 testbed) `[코드]`

$$
\mathbf H=\sqrt{N_rN_t}\sum_{\ell=1}^{L}\alpha_\ell\,\mathbf a_{N_r}(\theta_\ell)\,\mathbf a_{N_t}(\phi_\ell)^H,\qquad
\mathbf a_{N}(\theta)=\tfrac{1}{\sqrt N}\big[e^{j\pi n\sin\theta}\big]_{n=0}^{N-1}
\qquad(\texttt{conf/code/d2.py:140,151-155}).
$$

- **경로 수.** $L\sim\mathcal U\{3,\dots,8\}$이고 블록마다 새로 뽑습니다(`conf/code/d2.py:65,145`).
- **각도.** $\theta_\ell$(AoA)와 $\phi_\ell$(AoD)는 **물리 각도**입니다.
  - $\mathcal U[-\pi/3,\pi/3]$에서 연속 균등하게, 서로 독립으로 뽑습니다.
  - 격자는 없습니다(`conf/code/d2.py:67-68,146-147`).
- **경로 이득.** $\alpha_\ell=\sqrt{p_\ell}\,e^{j\psi_\ell}$, $\psi_\ell\sim\mathcal U[0,2\pi)$이고, **크기 $|\alpha_\ell|$는 결정적**입니다(`:148-149`).
- **경로 전력.** $p_\ell=e^{-\ell/2}\big/\sum_{\ell'=1}^{L}e^{-\ell'/2}$입니다(`:66,71-75`).
  - 지연을 모델링하지 않으므로 원고에서는 "power-delay profile"이 아니라 **경로 전력 프로파일**이라고 씁니다(§6.1 F15).
- **스케일.** $\sqrt{N_rN_t}$는 스펙 문구($\sqrt{N_rN_t/L}$)와 다릅니다(§6.1 F1).
- **이 모델의 위치.** D2는 조건부 Gaussian성의 붕괴를 분리하려고 만든 **통제된** 희소 정반사 모델입니다. 표준 채널이나 현실적인 mmWave 채널로 제시하지 않습니다(`conf/code/d2.py:24-29`).

### 2.2 D2의 성질

1. **정규화** `[코드]`
   - 모든 $(a,b)$에서 $\mathbb E|H_{ab}|^2=N_rN_t\sum_\ell p_\ell\frac1{N_r}\frac1{N_t}=1$이고, $\mathbb E\|\mathbf H\|_F^2=N_rN_t$입니다(`conf/code/d2.py:38-39`).
   - [기록] T2a: 표본 $10^5$개에서 31.997845 vs 32 (`results/testbed_D2.txt:14`)
   - 이 정규화는 앙상블 평균에서만 성립하고, 블록마다 정규화하지는 않습니다.
2. **2차 모멘트** `[코드]`
   - $\mathbf C_{\rm ens}=\mathbb E[\mathbf h\mathbf h^H]=\mathbf R_{\rm t}^T\otimes\mathbf R_{\rm r}$입니다.
   - $[\mathbf R]_{mn}=\mathbb E[e^{j\pi(m-n)\sin\theta}]$는 실수 Toeplitz 행렬이고, 적분으로 정확히 계산합니다(`conf/code/d2.py:41-53,86-99`).
   - **Kronecker 구조는 2차 모멘트에만 해당합니다.**
3. **조건부 Gaussian성이 깨짐** (T2d) `[코드/기록]`
   - $(L,\theta,\phi)$를 고정하고 위상만 무작위로 두면 다음이 성립합니다(`conf/code/d2.py:295-302`).
$$
\frac{\mathbb E|h_{ab}|^4}{(\mathbb E|h_{ab}|^2)^2}=2-\sum_\ell p_\ell^2<2\qquad(\mathcal{CN}\text{이면 정확히 }2).
$$
   - 측정값과 예측값의 최대 차이는 $5.01\times10^{-3}$이고, 모든 CI가 2를 배제합니다(`results/testbed_D2.txt:17-18`).
   - GMM은 성분마다 조건부 Gaussian을 가정하는데, D2는 그 가정을 깨도록 만든 모델입니다.
4. **저차원 지지 집합** `[유도]`
   - $N_r\ge8\ge L$이고 각도가 서로 다르면(확률 1), 조향 행렬이 Vandermonde라서 $\mathrm{rank}\,\mathbf H=\min(L,N_t)$입니다.
   - 한 $L$에서 $\mathbf h$는 매개변수 $3L$개(각도 $2L$개, 위상 $L$개)의 매끈한 상이므로, 지지 집합은 실수 차원 $\le3L$인 manifold들의 합집합입니다.
   - 여차원 $2N-3L$은 C2에서 40–55, C6에서 104–119입니다(`conf/code/common.py:64-69` 주석과 일치).

### 2.3 D1: 격자 GMM (맥락용, 순환 testbed) `[코드]`

$$
p(\mathbf h)=\tfrac{1}{32^2}\sum_{a_t,a_r}\mathcal{CN}\big(\mathbf 0,\ \mathbf R(\psi_{a_t})^{T}\otimes\mathbf R(\psi_{a_r})\big),\qquad
\mathbf R(\psi)=\mathbf D(\psi)\mathbf R_{\exp}(0.7)\mathbf D(\psi)^H,\quad \mathbf D(\psi)=\mathrm{diag}(e^{j\psi n})
$$

- 출처: `Demo/t2_gmm.py:198-213`, `Demo/t2_route_a.py:30-32,78-81`, `conf/code/common.py:43`
- $\psi$는 **전기 각도**이고, $[-\pi/3,\pi/3]$ 안의 32개 중점 격자에서 고릅니다.
- **모델 부류는 맞지만 $K$가 부족합니다.**
  - 참 prior는 $32^2=1024$ 성분입니다.
  - D1의 GMM arm은 $K\le64$입니다(`conf/code/arms.py:57`의 `D1_KS`).
  - 코드도 "not representable by a K ≤ 64 mixture"라고 적어 두었습니다(`Demo/t2_gmm.py:8-9`).
  - 참 prior를 그대로 쓰는 arm은 R6-exactEP뿐입니다(`conf/code/arms.py:120-121`).
- D1은 **품질 게이트(GA–GD) 측정 도구**로만 쓰고, 주장에는 쓰지 않습니다(`conf/code/common.py:222-227`).
- D2의 S2는 **물리** 각도 ±60°이고, D1의 S는 **전기** 각도 ±60°(물리 ±19.5°)입니다. 두 모델은 서로 다릅니다.

---

## 3. 수신기: RouteA 3-모듈 turbo 루프

### 3.0 반복 일정과 초기화 `[코드]`

반복 $j=1..16$마다 $[\,L_H+\text{Module H}\,]\to[\,L_X\,]\to[\,D\,]$ 순서로 돌고, 반복마다 BLER을 기록합니다(`Demo/t2_route_a.py:339-434`). 모든 arm에 공통인 루프 설정은 `conf/code/arms.py:18-33`에 있습니다.

초기값은 다음과 같습니다(`Demo/t2_route_a.py:324-327`).

$$
\mathbf r^D=\mathbf 0,\ \boldsymbol\tau^D=\mathbf 1,\ \bar{\mathbf x}=\mathbf 0,\ \mathbf v=\mathbf 1,\ \mathbf h_E=\mathbf 0,\ \nu_E=\bar c,\ e_b=\tfrac1{N_r}\textstyle\sum_a[\mathbf C_{\rm pr}]_{(a,b),(a,b)},\qquad \bar c=\tfrac1N\mathrm{tr}\,\mathbf C_{\rm pr}.
$$

**$\mathbf C_{\rm pr}$는 prior 객체의 공분산이고, arm마다 다릅니다.**
- Gaussian과 score arm: $\mathbf C_{\rm pr}=\hat{\mathbf C}$ (`conf/code/score.py:1091-1095`). 같은 클래스의 docstring(`:1072-1074`)은 이것이 "GMM arm이 받는 것과 같은 표본 공분산"이라고 적지만, 아래와 같이 b\*에는 맞지 않습니다(§6.1 F20).
- b\*: $\mathbf C_{\rm pr}=\sum_k\pi_k\mathbf C_k$ (`Demo/t2_gmm.py:35-37`)
  - kron M-step과 floor 때문에 이 값은 일반적으로 $\hat{\mathbf C}$와 같지 않습니다.
  - 항등식 `Demo/t2_gmm.py:13`은 floor가 0인 full EM에서만 성립합니다.

**그래도 결과에는 영향이 없습니다** `[유도]`.
- (i) 첫 반복의 데이터 열은 $\bar{\mathbf x}=\mathbf 0$이므로 $d_t$와 무관하게 $\mathbf A_t=\mathbf 0$, $\mathbf b_t=\mathbf 0$입니다. 파일럿 열은 $\mathbf v=\mathbf 0$이어서 $d_t=\sigma^{-2}$입니다. 따라서 초기 $e_b$는 어디에도 들어가지 않고, 그 뒤에는 posterior로 다시 계산됩니다(`:379`).
- (ii) $\nu_E$는 score arm의 D-13 단계에서만 쓰입니다. $T_p=N_t$에서는 첫 반복의 $(\mathbf q,\nu_q)$가 $\nu_E$와 무관합니다(§4.3 (c) 보조정리. 첫 반복의 $\alpha_L$이 clip에 걸리지 않는 격자 SNR에서).
- 따라서 **C2와 C6에서는 arm들의 첫 반복이 Module H에서만 다릅니다.** $T_p<N_t$인 C1과 C5에서는 $\nu_E=\bar c(\hat{\mathbf C})$가 score arm에 영향을 줍니다.

### 3.1 채널 likelihood site $L_H$ (form A, posterior 피드백) `[코드]`

열 $t$의 soft 심볼은 다음과 같습니다(`feedback="posterior"`, `conf/code/arms.py:21`, `Demo/t2_route_a.py:342-343`).
- 파일럿 열: $(\mathbf x_{p,t},\mathbf 0)$
- 데이터 열: 복호기 **a-posteriori** 모멘트 $(\bar{\mathbf x}_t,\mathbf v_t)$

$$
d_t=\Big(\sigma^2+\sum_b v_{bt}\,e_b\Big)^{-1},\quad
\mathbf A_t=d_t\,(\bar{\mathbf x}_t^{*}\bar{\mathbf x}_t^{T})\otimes\mathbf I_{N_r},\quad
\mathbf b_t=d_t\,\bar{\mathbf x}_t^{*}\otimes\mathbf y_t,\quad
\mathbf G=\sum_{t=1}^{T}\mathbf A_t,\ \ \mathbf b=\sum_t\mathbf b_t
$$

- 출처: `Demo/t2_route_a.py:296-306,344-345`
- 이 site는 $\prod_t\mathcal{CN}(\mathbf y_t;\mathbf H\bar{\mathbf x}_t,d_t^{-1}\mathbf I)$이고, $\ell(\mathbf h)\propto\exp(-\mathbf h^H\mathbf G\mathbf h+2\Re\,\mathbf b^H\mathbf h)$로 쓸 수 있습니다. 심볼 불확실성은 열마다 스칼라 잡음으로 흡수합니다.

posterior를 구한 뒤 다음과 같이 갱신합니다(`:379`).

$$
e_b\leftarrow\tfrac1{N_r}\textstyle\sum_a\big(|\hat h_{ab}|^2+\Sigma_{(a,b),(a,b)}\big)
$$

**$T_p=N_t$에서 첫 반복** `[유도]`
- $\bar{\mathbf x}_{\mathcal D}=\mathbf 0$이므로 $\mathbf G=(N_t/\sigma^2)\mathbf I$, $\mathbf b=\sigma^{-2}\mathrm{vec}(\mathbf Y_p\mathbf X_p^H)$입니다.
- $\mathbf G^{-1}\mathbf b=\mathrm{vec}(\mathbf Y_p\mathbf X_p^H)/N_t$는 파일럿 LS 추정입니다.

### 3.2 Module H: prior가 들어가는 유일한 자리 `[코드]`

prior마다 site $(\boldsymbol\Lambda,\boldsymbol\eta)$를 만들고(§4), 채널 belief는 공통으로 다음 식입니다(`Demo/t2_route_a.py:378`).

$$
\boldsymbol\Sigma=(\boldsymbol\Lambda+\mathbf G)^{-1},\qquad \hat{\mathbf h}=\boldsymbol\Sigma(\boldsymbol\eta+\mathbf b)
$$

- Gaussian, b\*, score arm이 다른 곳은 Module H 필드뿐입니다 [코드] (`conf/code/arms.py:34-38`).
- 테스트 M2(차이 0.0)가 확인하는 것은 Gaussian 경우 하나입니다. Module H를 Gaussian으로 둔 M-ours 조립 경로가 `R2-ours-G`와 같다는 것입니다 [기록] (`results/tests.txt:35`). b\*와 score arm에 대한 근거는 위 코드뿐입니다.
- G-1 guard $\nu_{\max}=10^4$(`conf/code/arms.py:27`)는 이 문서의 어느 arm에서도 쓰이지 않습니다. `scal="site"` 경로에서만 쓰이기 때문입니다(`Demo/t2_route_a.py:347-349`).

### 3.3 Site를 고정한 LOO cavity와 검출기 $L_X$ `[코드]`

데이터 열 $t$에 대해 채널 belief에서 **열 $t$ 자신의 likelihood 항만** 뺍니다. prior site $(\boldsymbol\Lambda,\boldsymbol\eta)$는 열 $t$를 포함해 계산한 값을 그대로 둡니다(`Demo/t2_route_a.py:391-392`).

$$
\boldsymbol\Sigma_{\setminus t}=(\boldsymbol\Lambda+\mathbf G-\mathbf A_t)^{-1},\qquad
\hat{\mathbf h}_{\setminus t}=\boldsymbol\Sigma_{\setminus t}(\boldsymbol\eta+\mathbf b-\mathbf b_t),\qquad \hat{\mathbf H}_{\setminus t}=\mathrm{unvec}(\hat{\mathbf h}_{\setminus t})
$$

심볼 prior는 **복호기 extrinsic**입니다: $\mathbf x_t\sim\mathcal{CN}(\mathbf r,\mathbf D_\tau)$, $\mathbf r=\mathbf r^D_{:,t}$, $\mathbf D_\tau=\mathrm{diag}(\boldsymbol\tau^D_{:,t})$. 채널 불확실성은 잡음 공분산에 흡수합니다(`:396-399`).

$$
\boldsymbol\Xi_t=\sigma^2\mathbf I_{N_r}+\sum_{b,b'}M_{bb'}\,\boldsymbol\Sigma_{\setminus t}^{[b,b']},\qquad \mathbf M=\mathbf r\mathbf r^H+\mathbf D_\tau,\qquad
\big[\boldsymbol\Sigma^{[b,b']}\big]_{aa'}=\mathrm{Cov}(h_{ab},h_{a'b'}).
$$

열 단위 LMMSE는 다음과 같습니다(`:400-404`).

$$
\mathbf K_t=\mathbf D_\tau\hat{\mathbf H}_{\setminus t}^H\big(\hat{\mathbf H}_{\setminus t}\mathbf D_\tau\hat{\mathbf H}_{\setminus t}^H+\boldsymbol\Xi_t\big)^{-1},\quad
\hat{\mathbf x}=\mathbf r+\mathbf K_t(\mathbf y_t-\hat{\mathbf H}_{\setminus t}\mathbf r),\quad
\boldsymbol\omega=\mathrm{diag}(\mathbf D_\tau-\mathbf K_t\hat{\mathbf H}_{\setminus t}\mathbf D_\tau)
$$

심볼별 Gaussian 나눗셈으로 extrinsic을 만듭니다(`:405-408`).

$$
\frac1{\tau^L_b}=\max\!\Big(\frac1{\omega_b}-\frac1{\tau_b},\;p_{\min}\Big),\qquad r^L_b=\tau^L_b\Big(\frac{\hat x_b}{\omega_b}-\frac{r_b}{\tau_b}\Big),\qquad p_{\min}=10^{-8}.
$$

$p_{\min}$은 extrinsic **정밀도의 하한**이므로, $\tau^L$에는 **상한 $10^{8}$**으로 작용합니다.

### 3.4 복호기 $D$: 정확한 심볼 BCJR과 moment extrinsic `[코드]`

- **역인터리빙.** 격자 인덱스 $g=nN_t+b$로 펼친 뒤 $\tilde r_i=r^L_{\pi(i)}$, $\tilde\tau_i=\tau^L_{\pi(i)}$로 되돌립니다(`Demo/t2_route_a.py:411`).
- **Log-MAP.** super-section 트렐리스를 씁니다(섹션 하나 = QPSK 심볼 하나). 가지 metric은 $\gamma_i=-|\tilde r_i-s(\text{branch})|^2/\tilde\tau_i$이고, 꼬리는 0으로 강제합니다(`Demo/t2_trellis.py:111-153`, `:123,126`).
- **APP 모멘트.** 심볼 APP $P_i(\cdot)$에서 $\bar x_i=\sum_s sP_i(s)$, $v_i=\sum_s|s|^2P_i(s)-|\bar x_i|^2$를 구합니다(`Demo/t2_trellis.py:190-193`).
- **경판정.** 정보 비트 APP LLR로 $\hat u=\mathbb 1[L^u<0]$를 정합니다(`Demo/t2_route_a.py:431`).
- **Extrinsic.** SC-VAMP 형태이고, Onsager 계수는 스칼라입니다(`:417-423`, $\epsilon=10^{-6}$).

$$
\alpha^D=\mathrm{clip}_{[\epsilon,1-\epsilon]}\Big(\tfrac1{N_s}\textstyle\sum_i v_i/\tilde\tau_i\Big),\quad
r^{D}_i=\frac{\bar x_i-\alpha^D\tilde r_i}{1-\alpha^D},\quad \tau^{D}_i=\frac{\alpha^D}{1-\alpha^D}\tilde\tau_i
$$

### 3.5 감쇠와 피드백 경로 `[코드]`

재인터리빙한 뒤 **extrinsic 쌍에만** 감쇠를 겁니다(`Demo/t2_route_a.py:427`, $\beta=0.7$, `conf/code/common.py:49`).

$$
(\mathbf r^D,\boldsymbol\tau^D)\leftarrow\beta\,(\cdot)^{\rm new}+(1-\beta)\,(\cdot)^{\rm old}
$$

- APP $(\bar{\mathbf x},\mathbf v)$는 **감쇠 없이** 다음 반복의 $L_H$로 갑니다(`beta_fb=None`, `conf/code/arms.py:24`, `Demo/t2_route_a.py:429`).
- 정리하면 검출기에는 extrinsic이, 채널 추정에는 APP가 들어갑니다(D-15).

### 3.6 Genie: known-channel 참조 수신기 `[코드]`

- 채널 쪽을 건너뛰고 $\hat{\mathbf H}_{\setminus t}=\mathbf H$, $\boldsymbol\Xi_t=\sigma^2\mathbf I$로 둡니다.
- 검출기, 복호기, 감쇠, 16회 반복은 그대로입니다(`Demo/t2_route_a.py:388-389`, `conf/code/arms.py:119`).
- 따라서 genie는 **bound가 아니라 참조**입니다.
  - C2 −3 dB에서 V1은 성공하고 genie는 실패한 블록이 15개입니다 [기록] (`08_SPEC_analysis.md:12`).
  - 그러므로 블록 단위의 하한도 아닙니다.

### 3.7 루프 상수

| 상수 | 값 | 출처 |
|---|---|---|
| 외부 반복 | 16 (모든 arm) | `conf/code/common.py:42` |
| $\beta$ (extrinsic 감쇠) | 0.7 | `conf/code/common.py:49`, `conf/code/arms.py:23` |
| posterior 피드백 감쇠 | 없음 | `conf/code/arms.py:24` |
| `n_inner` (L_H↔H 안쪽 반복) | 1 | `conf/code/arms.py:25` |
| $\alpha$ clip $\epsilon$ ($\alpha^D,\alpha_L,\alpha_H$) | $10^{-6}$ | `conf/code/arms.py:26` |
| $p_{\min}$ (extrinsic 정밀도 하한 = $\tau^L$ 상한 $10^8$) | $10^{-8}$ | `conf/code/arms.py:28` |
| $\lambda_{\min}$ (site·Jacobian 고유값 하한) | $10^{-6}$ | `conf/code/common.py:51` |
| $\nu_{\max}$ (G-1 guard) | $10^{4}$, 이 문서의 arm에서는 쓰이지 않음 | `conf/code/arms.py:27` |
| 수신기 정밀도·장치 | complex128/float64, CPU (모든 arm) | `conf/code/runner.py:24-26` |

---

## 4. Prior

### 4.1 Gaussian (`R2-ours-G`) `[코드]`

- 식: $\boldsymbol\Lambda=\hat{\mathbf C}^{-1}$, $\boldsymbol\eta=\mathbf 0$ (`Demo/t2_route_a.py:376`)
- 즉 주어진 $(\mathbf G,\mathbf b)$에서 LMMSE posterior를 정확히 계산합니다.
- $\hat{\mathbf C}=\frac1{N'}\sum\mathbf h\mathbf h^H$는 학습 집합(stream 7, $N'$개)의 표본 공분산입니다(`Demo/t2_gmm.py:145`). full $K=32$ fit 파일에 저장된 값을 읽습니다(`conf/code/arms.py:108`).

### 4.2 GMM b\*: 정확한 mixture EP site `[코드]`

**모형.** $p(\mathbf h)=\sum_{k=1}^{K}\pi_k\,\mathcal{CN}(\mathbf 0,\mathbf C_k)$이고, 성분은 두 종류입니다.
- full 공분산
- Kronecker 공분산 $\mathbf C_k=\mathbf C^{\rm t}_k\otimes\mathbf C^{\rm r}_k$

**EM** (`Demo/t2_gmm.py:136-187`)
- **seed 초기화**(`:151-154`): $\mathbf C_k^{(0)}=\tfrac12\hat{\mathbf C}+\tfrac12\frac{N\bar c}{\|\mathbf h_s\|^2}\mathbf h_s\mathbf h_s^H$이고, $\mathbf h_s$는 학습 표본에서 무작위로 고릅니다.
- **full M-step**(`:172-174`): $\mathbf C_k=\frac{n_k\mathbf S_k+\kappa\hat{\mathbf C}}{n_k+\kappa}+10^{-4}\bar c\,\mathbf I$
- **Kronecker M-step**(`:175-183`)
  - flip-flop을 3회 돌립니다.
  - 정규화는 $\mathrm{tr}\,\mathbf C^{\rm t}_k=N_t(1+10^{-4})$입니다(`:182`, floor 포함).
  - 두 인자 모두에 floor가 들어갑니다.
- **재seed**: $n_k$가 부족한 성분(full은 $n_k<N$, kron은 $n_k<4$)은 다시 seed합니다. 이 때문에 단조 증가가 깨질 수 있습니다(`:167-170`).
- **종료 조건** (먼저 걸리는 것)
  - (i) **patience**: 검증 로그우도를 10반복마다 재고, 40반복 동안 개선이 없으면 멈춥니다(`:159-162`).
  - (ii) **train-ll 조건**: 20반복 뒤 $\ell\ell_j-\ell\ell_{j-1}<10^{-6}|\ell\ell_j|$이면 멈춥니다. **감소도 이 조건을 만족합니다**(`:164`).
  - (iii) **상한**: 500반복입니다(`conf/code/runner.py:62`).
  - 어느 경우든 **검증 로그우도가 최대였던 반복의 파라미터**를 돌려줍니다(`:186`).
- **GPU 포트.** `conf/code/gmm_em_gpu.py:78-79`는 같은 종료 규칙을 씁니다(`:133,137`). batched kron M-step은 정확한 경로와 비교해 동치임을 확인했습니다 [기록] (`results/nr16b_batched_check.txt:10-14`).

**데이터** (`conf/code/runner.py:57,916-921`)

| 용도 | stream | 크기 |
|---|---|---|
| 학습 | 7 | $N'$ |
| 검증 | 8 | 5000 |
| 시험 | 10 | 5000 (보고용 ll_test) |

**선택** (`conf/code/runner.py:979`, `conf/code/arms.py:91-100`)
- 각 (family, $K$) 안에서 검증 로그우도가 가장 높은 $(\kappa,\text{restart})$를 고릅니다.
- 전체 후보는 $\{$full의 각 $K\}\cup\{$검증 우도가 가장 높은 kron $K\}$이고, 이 중 argmax가 $b^*$입니다.
- BLER은 한 번도 보지 않습니다.
- 격자 목록 $K\in\{16..8192\}$(`conf/code/arms.py:57`)는 등록부일 뿐입니다. `load_fits`는 **파일이 있는 $K$만** 읽습니다(`:72-82`).

**실제로 적합한 격자** [기록: 각 `.npz`의 `ll_val, n_iter, it_best, n_reseed, kappa, restart`; 종료 사유는 `[유도]`]

종료 사유 표기:
- P = patience
- C = 500 상한
- T± = train-ll 조건(부호는 마지막 $\Delta\ell\ell$)

선택된 $\kappa$는 두 셀의 모든 full $K$에서 0입니다.

*C2* (`results/gmm_fits_D2_B16e4k/fit_S2_Nr8_*_n160000.npz`, $N'=1.6\times10^5$; full은 $\kappa\in\{0,16,64,256\}$ × 재시작 3회, kron은 $\kappa=0$ × 재시작 3회)

| $K$ | full: $\ell\ell_{\rm val}$ (종료) | kron: $\ell\ell_{\rm val}$ (종료) |
|---|---|---|
| 16 | −38.152 (T+) | −39.018 (T+) |
| 32 | −31.460 (P) | −33.023 (P) |
| 64 | −25.344 (**C**, it_best 490) | −27.475 (T+) |
| 128 | −20.206 (**C**, it_best 490) | −22.573 (P) |
| 256 | −16.552 (**C**, it_best 490) | −18.417 (P) |
| 512 | −16.316 (P) | −14.636 (P) |
| 1024 | 적합 안 함 | **−11.459 (P; n_iter 331, it_best 290) = b\*** |

*C6* (`results/gmm_fits_D2_NR16B16e4/fit_S2_Nr16_*_n160000.npz`)

| $K$ | full: $\ell\ell_{\rm val}$ (종료) | kron: $\ell\ell_{\rm val}$ (종료) |
|---|---|---|
| 16 / 32 / 64 | −29.634 (T−) / −10.900 (T−) / 4.249 (P) | −28.834 (T+) / −8.699 (T−) / 7.710 (T−) |
| 128 / 256 | 14.735 (T+) / 16.611 (**C**) | 24.365 (T−) / 38.407 (T−) |
| 512 | 13.507 (T−; n_iter 51, 재seed 2,392) | 50.185 (T−) |
| 1024 / 2048 | 적합 안 함 | 58.857 (T+; 재seed 477) / 61.982 (T−; 재seed 23,279) |
| 4096 | 적합 안 함 | **63.175 (T−; n_iter 163, it_best 160, 재seed 85,594) = b\*** |

**캐비엇** `[기록/유도]`
- **C2**
  - b\*(kron $K=1024$)와 full 최선($K=512$)은 모두 **적합한 격자의 끝**입니다. kron 검증 우도는 $K=512\to1024$에서 +3.18 nat로 아직 오르는 중입니다.
  - $K=2048$은 적합하지 않았습니다. 근거는 4e4에서 $K$를 2배로 늘렸을 때 BLER 변화가 −1%였다는 것입니다(`DECISIONS.md:100`).
  - full $K=64/128/256$은 500반복 상한에서 멈췄고, 최대 검증 우도는 반복 490에 있었습니다. 즉 **수렴 전에 멈춘 후보**입니다.
  - 반면 b\*는 patience로 끝났습니다.
- **C6**
  - b\* = kron $K=4096$은 사용자 결정으로 멈춘 **격자의 끝**입니다(`DECISIONS.md:183`). $K=2048\to4096$에서 +1.19 nat입니다.
  - C6의 적합은 대부분 **train-ll 조건**으로 끝났습니다. b\*도 n_iter 163에서 train ll이 떨어진 순간 멈췄습니다($\Delta\ell\ell=-1.75\times10^{-3}$, 재seed 85,594회). **patience로 끝나지 않았습니다.**
  - **b\*가 덜 수렴했을 수 있습니다** [기록] (`results/review_next/NEXT_EXPERIMENTS_C6B16e4.md:135`, `DECISIONS.md:205`)
    - kron $K=4096$의 재시작 셋(b\* = 재시작 2 포함)이 모두 train-ll 조건으로 멈췄습니다. 재seed 때문에 $\Delta\ell\ell<0$이 된 순간입니다. n_iter/it_best는 재시작 0/1/2에서 169/160, 223/220, 163/160입니다(`results/review_next/NEXT_EXPERIMENTS_C6B16e4.md:79`, 각 `.k0r*.npz`).
    - 셋 모두 검증 우도가 마지막 평가(10반복 간격)에서 최고였습니다. 즉 검증 우도가 아직 오르던 중이었을 수 있습니다.
    - $K=2048$은 셋 중 둘, $K=1024$는 셋 중 하나가 같은 방식으로 멈췄습니다.
    - 이 규칙은 모든 적합에 같은 동결 EM 프로토콜이므로 규칙 위반은 아니고, 수치와 판정은 그대로입니다. 반면 C2 b\*는 patience로 멈췄습니다(n_iter 331, it_best 290).
    - 따라서 C6 b\*는 C2 b\*보다 덜 수렴한 상태에서 선택됐을 수 있고, 이 방향은 V1에 유리합니다.
    - `NEXT_EXPERIMENTS_C6B16e4.md:135` 는 처음에 이 규칙을 `Demo/t2_gmm.py:162`로 적었다가 커밋 전에 `:164` 로 고쳤습니다(`:162` 는 patience 분기). train-ll 규칙은 `:164`이고, GPU 포트에서는 `conf/code/gmm_em_gpu.py:137`입니다.
  - C6 full $K=512$는 반복 51에서 멈췄습니다.

**Site: 비등방 cavity $(\mathbf G,\mathbf b)$에 대한 정확한 tilted moment** (`Demo/t2_gmm.py:44-52`)

$$
\boldsymbol\Sigma_k=(\mathbf C_k^{-1}+\mathbf G)^{-1},\quad \boldsymbol\mu_k=\boldsymbol\Sigma_k\mathbf b,\quad
\log w_k=\log\pi_k-\log\det(\mathbf I+\mathbf C_k\mathbf G)+\mathbf b^H\boldsymbol\Sigma_k\mathbf b\quad(\text{정규화 후}),
$$

$$
\mathbf m_\pi=\sum_k w_k\boldsymbol\mu_k,\qquad \mathbf V_\pi=\sum_k w_k(\boldsymbol\Sigma_k+\boldsymbol\mu_k\boldsymbol\mu_k^H)-\mathbf m_\pi\mathbf m_\pi^H,
$$

$$
\boldsymbol\Lambda=\Pi_{\ge\lambda_{\min}}\!\big(\mathbf V_\pi^{-1}-\mathbf G\big),\qquad \boldsymbol\eta=\mathbf V_\pi^{-1}\mathbf m_\pi-\mathbf b\qquad(\texttt{Demo/t2_gmm.py:54-66}).
$$

- $\Pi_{\ge\lambda_{\min}}$는 고유값을 아래에서 자릅니다.
- clip 규칙은 `eta`입니다(`conf/code/arms.py:185`의 `.view("eta")`). $\boldsymbol\Lambda$를 잘라도 $\boldsymbol\eta$는 그대로 둡니다.
- 자르지 않으면 $\hat{\mathbf h}=\mathbf m_\pi$, $\boldsymbol\Sigma=\mathbf V_\pi$가 정확히 성립합니다.
- b\* 경로는 `mode="colored", exact_prior=True`입니다(`conf/code/arms.py:36`). 이 경로에서는 $\hat{\mathbf C}$를 쓰지 않습니다.

### 4.3 학습 score prior (V0, V1): D-13 belief와 D-14 행렬 site `[코드]`

배선은 `mode="scalar", scal="belief", hsite="matrix", clip="eta"`입니다(`conf/code/arms.py:37,191,198`). 클래스는 `RouteAClip`이고 `Demo/t2_gmm.py:101-122`에 있습니다.

**(a) 네트워크와 학습** [코드/기록]

| 항목 | C2 (헤드라인) | C6 |
|---|---|---|
| checkpoint | `ckpt/d2sx_N160000_a1.pt`, sha256[:16] `4443921ce8d5c4a1` | `ckpt/d2sx_NR16_N160000_a1_fb2_best.pt`, `c050d611b2c714a6` |
| **평가 가중치** | **마지막 epoch(1784)의 EMA.** 검증 손실 최소 epoch는 1764였지만 그 가중치는 저장되지 않음 | **검증 손실 최소 epoch(1684)의 EMA** (raw meta `stagec_ckpt_id … role=best`). 마지막 epoch(1704) 가중치(`bf688d605691c7f7`)도 별도로 평가함 |
| 학습 레시피 | 기본 레시피, grad clip 없음 (checkpoint에 `grad_clip` 필드가 없고, 코드 기본값은 0.0 = 끔, `conf/code/score.py:983-984`) | **§3d 폴백 시행 2: `grad_clip=1.0`** (checkpoint 필드). 시행 1은 발산했고, 시행 3은 규칙대로 열어 보지 않음 |
| 파라미터 수 | 479,426 (`logs/train_d2sx_N160000_a1.log:6`) | 481,474 (`logs/train_d2sx_NR16_N160000_a1_fb2.log:6`) |
| 학습/검증 분할 | 144,000 / 16,000 (`…_a1.log:4`) | 144,000 / 16,000 (`…_fb2.log:4`) |
| $\varsigma$ 추출 범위 | $[0.033062,\,0.84516]$ (`…_a1.log:5`) | $[0.032832,\,0.49152]$ (`…_fb2.log:5`) |
| 종료 | 1784 epoch, patience, wall-clock 35,774.6 s (`…_a1.log:1792`) | 1704 epoch, patience, wall-clock 36,743.4 s (`…_fb2.log` 마지막 줄) |
| 게이트 지위 | D2 checkpoint 자체는 게이트 기록이 없음(raw meta `UNVERIFIED`). 레시피가 D1 형제 `sx_N160000_D1.pt`의 게이트를 통과함(`LADDER_C.md:1`) | **UNGATED**: D1 형제가 없음(`results/review_next/NEXT_EXPERIMENTS_C6B16e4.md:28`) |

- C6 레시피 이력의 근거: `DECISIONS.md:185,195`, `results/review_next/HANDOFF_2026-09-25.md:21`
- 공통 설정
  - **도메인.** 각도 도메인입니다. $\mathbf H_a=\mathbf F_{N_r}^H\mathbf H\mathbf F_{N_t}$(unitary DFT)이고, 실수 직교 embedding $\mathbf M$을 씁니다(`conf/code/score.py:341-350`). 네트워크는 $\boldsymbol\epsilon_\theta(\mathbf u,\varsigma)=\mathbf M^T\,\mathrm{DiT}_\theta(\mathbf M\mathbf u,\log\varsigma)$입니다(`:382-385`).
  - **구조.** DiT, adaLN-Zero, 토큰 = 안테나 쌍 bin($N_rN_t$개, patch 1), 폭 64, 깊이 6, 8 heads, 학습되는 위치 embedding(0 초기화), $\log\varsigma$ Fourier embedding(emb 256)입니다(`conf/code/arch_dit.py:111-160`, 로그 `hp` 줄).
  - **옵티마이저.** Adam, lr $2.238\times10^{-3}$, EMA 0.999, batch 256입니다(`conf/code/score.py:896`, 로그 `hp` 줄).
  - **종료.** 검증 손실(EMA 가중치 기준)의 patience 20, 최소 200 epoch, 최대 3000 epoch입니다(`conf/code/score.py:836`).
  - **정밀도.** 학습은 GPU float32로 하고, 수신기 안의 추론은 CPU float64로 합니다(`conf/code/score.py:1052-1057`).
- **목적 함수: VP $\epsilon$-prediction DSM** (`conf/code/score.py:441-444`)
  - $\bar\alpha=1/(1+\varsigma^2)$로 두면, VE 잡음 $\mathbf x+\varsigma\boldsymbol\xi$를 $\sqrt{\bar\alpha}$배한 것과 같습니다.

$$
\mathcal L(\theta)=\mathbb E_{\mathbf x,\varsigma,\boldsymbol\xi}\big\|\boldsymbol\epsilon_\theta(\sqrt{\bar\alpha}\,\mathbf x+\sqrt{1-\bar\alpha}\,\boldsymbol\xi,\ \varsigma)-\boldsymbol\xi\big\|^2,\qquad
\log\varsigma\sim\mathcal U[\log\varsigma_{\rm lo},\log\varsigma_{\rm hi}]\ \ (\texttt{:968-969}).
$$

  - 여기서 $\mathbf x=[\Re\mathbf h;\Im\mathbf h]$입니다(`conf/code/score.py:170-176`).
  - 이로부터 score와 denoiser가 정해집니다(`:411-413,427-429`).

$$
\mathbf s_\theta(\mathbf x,\varsigma)=-\hat{\boldsymbol\epsilon}/\varsigma,\qquad D_\theta(\mathbf x,\varsigma)=\mathbf x-\varsigma\hat{\boldsymbol\epsilon},\qquad \hat{\boldsymbol\epsilon}=\boldsymbol\epsilon_\theta(\sqrt{\bar\alpha}\,\mathbf x,\varsigma)
$$

**(b) $\sigma$ 격자와 측정 조건** [코드/기록]

학습 범위 $[\varsigma_{\rm lo},\varsigma_{\rm hi}]$는 **수신기가 실제로 보내는 질의 $\nu_q$** 분포의 1–99 백분위입니다(`conf/code/sigma.py:20-22,58-63`).

측정 수신기: score 배선(D-13 belief + D-14 행렬 site)에 **Gaussian prior $\hat{\mathbf C}$ (N=1e4 fit 파일)**을 넣었습니다(`conf/code/sigma.py:33-35`). `load_fits`의 기본 ntrain은 1e4입니다(`conf/code/common.py:47`).

| | C2 격자 (`results/sigma_grid_D2.txt`) | C6 격자 (`results/sigma_grid_D2_NR16.txt`) |
|---|---|---|
| 측정 셀 | C1과 C2, 14점, 점당 64블록 × 16반복 = 14,336 표본 (`:12`) | C6만, 7점, 7,168 표본 (`:12`) |
| $\nu$ 범위 | $[2.1862\times10^{-3},\ 1.4286]$ (`:37`) | $[2.1559\times10^{-3},\ \mathbf{0.48318}]$ (`:30`) |
| $\varsigma$ 범위 | $[0.033062,\ 0.84516]$ (`:39,58`) | $[0.032832,\ 0.49152]$ (`:32,51`) |
| $\hat{\mathbf C}$ 출처 | `results/gmm_fits_D2` (n10000) | `results/gmm_fits_D2_NR16` (n10000, `conf/code/run_nr16.sh:19`의 `--tag NR16`) |

- checkpoint의 `sigma_tag`가 $\varsigma_{\rm hi}$를 정합니다(`conf/code/score.py:1096-1100`). C6 checkpoint의 `sigma_tag`는 `NR16`입니다.
- 격자 밖 질의는 **clamp하지 않고 외삽합니다**(`conf/code/score.py:1076-1078`).
- 측정에 쓴 64블록은 각 점 **테스트 스트림의 trial 0..63과 같은 실현**입니다(`conf/code/sigma.py:36-42`의 `trial_rng`). 측정에는 Gaussian 수신기의 $\nu_q$만 쓰고 BLER은 쓰지 않았습니다(§6.1 F18).

**(c) D-13 belief 스칼라화 (VAMP의 LMMSE 단계)** (`Demo/t2_route_a.py:360-364`)

$$
\boldsymbol\Sigma_L=(\mathbf I/\nu_E+\mathbf G)^{-1},\quad \mathbf h_L=\boldsymbol\Sigma_L(\mathbf h_E/\nu_E+\mathbf b),\quad
\alpha_L=\mathrm{clip}_{[\epsilon,1-\epsilon]}\Big(\tfrac{\mathrm{tr}\boldsymbol\Sigma_L}{N\nu_E}\Big),\quad
\nu_q=\tfrac{\alpha_L}{1-\alpha_L}\nu_E,\quad \mathbf q=\tfrac{\mathbf h_L-\alpha_L\mathbf h_E}{1-\alpha_L}
$$

**보조정리 ($T_p=N_t$에서 질의 분산 부등식)** `[유도]`

C2와 C6처럼 $\mathbf X_p\mathbf X_p^H=N_t\mathbf I$이고 첫 반복의 $\alpha_L$이 clip에 걸리지 않으면, 즉 $\epsilon/(1-\epsilon)<\bar cN_t/\sigma^2<(1-\epsilon)/\epsilon\approx10^{6}$이면, 모든 반복 $j$와 모든 블록에서 다음이 성립합니다. 등호는 $j=1$에서입니다.

$$
\nu_q^{(j)}\le\sigma^2/N_t .
$$

- 이 조건은 격자 SNR(−3..15 dB)에서 성립합니다. $\bar c\approx1$(§2.2의 정규화)이고 $\sigma^2\in[10^{-1.5},10^{0.3}]$이므로 $\bar cN_t/\sigma^2\approx2.0$–$126.5$입니다.

증명:
1. 파일럿 열은 $d_t=\sigma^{-2}$이므로 합이 $(N_t/\sigma^2)\mathbf I$입니다. 데이터 열의 $\mathbf A_t\succeq0$입니다. 따라서 $\mathbf G\succeq(N_t/\sigma^2)\mathbf I$입니다.
2. 그러면 $\boldsymbol\Sigma_L\preceq(1/\nu_E+N_t/\sigma^2)^{-1}\mathbf I$이고, clip하기 전의 $\alpha_L\le1/(1+c)$입니다. 여기서 $c=\nu_EN_t/\sigma^2$입니다.
3. $f(\alpha)=\alpha/(1-\alpha)$는 증가 함수이므로 $\nu_q=f(\alpha_L)\nu_E\le\nu_E/c=\sigma^2/N_t$입니다. 위쪽 clip은 $\alpha_L$을 줄이기만 합니다.
4. 아래쪽 clip($\alpha_L=\epsilon$)이 걸리는 경우를 따로 봅니다.
   - 이때는 $\nu_q=\frac{\epsilon}{1-\epsilon}\nu_E$입니다.
   - $j\ge2$이면 직전 반복의 $\nu_E=f(\alpha_H)\nu_q^{(j-1)}\le\frac{1-\epsilon}{\epsilon}\nu_q^{(j-1)}$입니다($\alpha_H\le1-\epsilon$).
   - 따라서 귀납적으로 $\nu_q^{(j)}\le\nu_q^{(j-1)}\le\sigma^2/N_t$입니다.
5. $j=1$에서는 $\mathbf G=(N_t/\sigma^2)\mathbf I$, $\mathbf h_E=\mathbf 0$, $\nu_E=\bar c$이므로 clip 전 $\alpha_L=1/(1+\bar cN_t/\sigma^2)$입니다. 위 조건에서는 clip이 걸리지 않으므로 $\nu_q=\sigma^2/N_t$이고, $\mathbf q=\mathbf G^{-1}\mathbf b$(파일럿 LS)입니다. 둘 다 $\nu_E$와 무관합니다. 이것이 4의 귀납 시작점입니다.

측정값과도 맞습니다 [기록].
- C2 −3 dB 첫 반복의 중앙값은 $4.988\times10^{-1}=\sigma^2/4$입니다.
- 이후 반복의 중앙값은 단조 감소합니다(`results/sigma_grid_D2.txt:29-35`, `results/sigma_grid_D2_NR16.txt:22-28`).

**(d) One-shot Tweedie denoiser** (`conf/code/score.py:1107-1122,589-592`)

$$
\mathbf m(\mathbf q,\nu_q)=\mathbf q+\nu_q\,\hat{\mathbf s}(\mathbf q,\nu_q),\qquad \hat{\mathbf s}\approx\nabla_{\mathbf q^*}\log p_{\nu_q}(\mathbf q),\qquad \varsigma=\sqrt{\nu_q/2}.
$$

실수 영역에서는 $D_\theta(\mathbf x,\varsigma)=\mathbf x+\varsigma^2\mathbf s_\theta$입니다. $\mathbf s_{\mathbb R}=2[\Re\hat{\mathbf s};\Im\hat{\mathbf s}]$이고 $2\varsigma^2=\nu$이므로 두 표현은 같습니다.

**(e) Wirtinger Jacobian과 V0/V1** (`conf/code/score.py:595-600,603-619,1120-1129`)

실수 Jacobian $\mathbf J_{\mathbb R}=\begin{bmatrix}\mathbf J_{11}&\mathbf J_{12}\\ \mathbf J_{21}&\mathbf J_{22}\end{bmatrix}$를 `jacrev`로 한 번에 구합니다(VJP $2N$회). 이로부터 다음을 만듭니다.

$$
\mathbf J=\tfrac12\big[(\mathbf J_{11}+\mathbf J_{22})+j(\mathbf J_{21}-\mathbf J_{12})\big]=\partial\mathbf m/\partial\mathbf q\quad(\mathbf q^*\text{ 고정}).
$$

- 참 MMSE denoiser라면 $\mathbf J=\mathrm{Cov}[\mathbf h\mid\mathbf q]/\nu_q\succeq0$입니다(2차 Tweedie, `Demo/t2_route_a.py:60-61` 주석).
- $\partial\mathbf m/\partial\mathbf q^*$(pseudo-covariance)는 버립니다(§6.1 F16).
- **V0**: $\mathbf J\leftarrow\mathrm{Herm}(\mathbf J)=\frac12(\mathbf J+\mathbf J^H)$
- **V1**: $\mathbf J\leftarrow\Pi_{\rm PSD}(\mathbf J)=\mathbf U\max(\boldsymbol\Lambda_J,\lambda_{\min})\mathbf U^H$
  - $\mathrm{Herm}(\mathbf J)$의 고유값을 아래에서 $10^{-6}$으로 자릅니다. 위쪽은 건드리지 않습니다(`:610-611`).
  - V1 arm은 `psd_project=True`로 만듭니다(`conf/code/runner.py:345`).
- $\alpha_H=\mathrm{tr}\,\mathbf J/N$은 **투영한 뒤의** $\mathbf J$로 계산합니다(`conf/code/score.py:1133-1135`). 따라서 V1은 (f)의 등방 extrinsic에도 영향을 줍니다.

**(f) 등방 extrinsic (다음 반복의 (c) 입력)** (`Demo/t2_route_a.py:365-367`)

$$
\mathbf h_E=\frac{\mathbf m-\alpha_H\mathbf q}{1-\alpha_H},\qquad \nu_E=\frac{\alpha_H}{1-\alpha_H}\nu_q,\qquad \alpha_H\in[\epsilon,1-\epsilon]
$$

**(g) D-14 행렬 site** (`Demo/t2_gmm.py:112-122`)

검출기와 채널 belief는 이 site를 씁니다. 등방 site는 denoiser 입력에만 쓰입니다(`Demo/t2_route_a.py:368-370`).

$$
\boldsymbol\Sigma_H=\nu_q\mathbf J,\qquad \boldsymbol\Lambda=\Pi_{\ge\lambda_{\min}}\big(\boldsymbol\Sigma_H^{-1}-\mathbf I/\nu_q\big),\qquad \boldsymbol\eta=\boldsymbol\Sigma_H^{-1}\mathbf m-\mathbf q/\nu_q
$$

- 이 식은 "denoiser belief $\mathcal{CN}(\mathbf m,\boldsymbol\Sigma_H)$ ÷ 등방 cavity $\mathcal{CN}(\mathbf q,\nu_q\mathbf I)$"입니다. 이렇게 얻은 site를 **비등방 likelihood $(\mathbf G,\mathbf b)$ 전체**와 곱합니다(§3.2).
- $\lambda_{\min}$을 두 번 적용하는 것에 주의해야 합니다. V1은 $\mathbf J$와 $\boldsymbol\Lambda$ 양쪽을 자르고, V0는 $\boldsymbol\Lambda$만 자릅니다(§6.1 F17).
- **인터페이스가 비대칭입니다** (§6.1 F14).
  - b\*는 비등방 cavity에 대한 정확한 tilted moment를 받습니다.
  - 학습 prior는 등방 cavity만 봅니다.
  - 그래서 비교는 "prior + 인터페이스" 묶음끼리의 비교입니다. b\*를 V1 배선에 넣은 대조군 `gmmB-scorew-eta`가 있습니다(`conf/code/arms.py:216-218`, 보고 전용).

### 4.4 V0 발산과 V1 투영: 고유값 부호

**식에서 직접 나오는 것** `[유도]`

(e)를 거친 $\mathbf J$의 고유쌍을 $(\lambda_i,\mathbf u_i)$라 하겠습니다. 그러면 (g)의 site는 다음과 같습니다.

$$
\Lambda_i=\frac{1-\lambda_i}{\nu_q\lambda_i},\qquad \mathbf u_i^H\boldsymbol\eta=\frac{\mathbf u_i^H\mathbf m}{\nu_q\lambda_i}-\frac{\mathbf u_i^H\mathbf q}{\nu_q}.
$$

- **$0<\lambda_i\le1$**: $\Lambda_i\ge0$입니다. $\lambda_i$가 $1$에 아주 가까우면 $\lambda_{\min}$으로 잘립니다.
- **$\lambda_i>1$**: $\Lambda_i\in(-1/\nu_q,0)$이므로 $\lambda_{\min}$으로 잘립니다. `eta` 규칙이라 $\boldsymbol\eta$는 그대로입니다.
  - 정확한 GMM denoiser에서도 이 경우가 흔합니다 [기록]. `logs/jacpsd_D2_final.log:31-50`에서 kron $K=512$ GMM의 $f(\lambda_{\max}>1)$은 0.43–0.94입니다(헤드라인 b\*가 아닌 $K=512$ 적합). 같은 표에서 clip이 만드는 denoiser 단계 belief 평균의 상대 이동은 중앙값 $\le5.7\times10^{-3}$입니다.
  - 이 clip이 BLER에 미치는 영향은 따로 측정하지 않았습니다.
  - V1 자체의 clip 통계는 raw의 `M-ours-dscore-C-V1|clip` 필드에 있지만, 아직 기록 파일로 뽑지 않았습니다. 기록 파일이 생기면 위 GMM 대리 측정 대신 그 값을 인용합니다.
- **$\lambda_i<0$ (V0에서만 가능)**
  - $\Lambda_i<-1/\nu_q$이고, $\lambda_i\to0^-$이면 크기가 커집니다. $\Lambda_i$는 $\lambda_{\min}$으로 잘리지만, $\boldsymbol\eta$의 $\mathbf u_i^H\mathbf m/(\nu_q\lambda_i)$ 항은 그대로 남습니다.
  - 그 방향이 $\mathbf G$의 고유벡터와 가깝다고 근사하면, 채널 belief 평균의 그 성분은 대략 $(\mathbf u_i^H\boldsymbol\eta+\ldots)/(\lambda_{\min}+g_i)$가 되어 폭주합니다.
- **V1**: $\lambda_i\ge\lambda_{\min}$이므로 $\Lambda_i\le(1-\lambda_{\min})/(\nu_q\lambda_{\min})$입니다. $\lambda_i\to\lambda_{\min}$인 방향에서는 $\Lambda_i^{-1}\mathbf u_i^H\boldsymbol\eta\to\mathbf u_i^H\mathbf m$이므로, belief가 denoiser 출력에 고정됩니다.

**평가 checkpoint에서 측정한 스펙트럼** [기록] (`logs/jacpsd_D2_final.log:8-27`)
- 조건: `ckpt/d2sx_N160000_a1.pt`(C2 평가 가중치), 점당 held-out D2 표본 128개, $\mathbf q=\mathbf h+$ 격자 $\varsigma$의 잡음
- V0/V1이 실제로 쓰는 $\mathrm{Herm}(\mathbf J)$ 기준입니다.

| $\varsigma$ | 0.033 | 0.039 | 0.047–0.092 | 0.109, 0.129 | 0.153 | 0.182 | 0.216 | 0.256 | 0.304 | 0.360 | 0.427 | 0.507–0.845 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| $f(\lambda_{\min}(\mathrm{Herm}\,\mathbf J)<0)$ | 0.812 | 0.992 | 1.000 | 0.992 | 0.961 | 0.922 | 0.836 | 0.477 | 0.492 | 0.195 | 0.180 | 0.031–0.086 |

- 같은 checkpoint에서 실수 Jacobian $\mathbf J_{\mathbb R}$ 기준으로는 $\varsigma\le0.182$에서 0.992–1.000입니다(같은 로그의 첫 번째 `f<0` 열).
- D1 checkpoint `sx_N160000_D1.pt`에서는 20개 격자점 모두 0.000입니다(`logs/jacpsd_D1_N160000.log:8-27`).
- C6 checkpoint의 스펙트럼은 **측정 기록이 없습니다.**

**발산 가드 기록** [기록]
- 가드는 "16반복 중 한 번이라도 NMSE > 10이거나 비유한"이면 발동합니다. 판정과 분류에만 쓰고, 궤적은 바꾸지 않습니다(`conf/code/runner.py:495-504`).
- **C2 V0**: SNR별로 블록의 **53–93%**에서 발동했고, 최악 NMSE는 $5.3\times10^{7}$–$2.6\times10^{10}$입니다. NMSE로 7.7–10.4 자릿수입니다(`results/guard_D2_B16e4k.txt:18-24`).
- **C6 V0**: 99.3–100%에서 발동했고, 최악 NMSE는 $7.0\times10^{8}$–$1.2\times10^{11}$입니다(`results/guard_D2_NR16B16e4.txt:18-24`).
- V1, b\*, Gaussian에서는 두 셀 모두 한 번도 발동하지 않았습니다(각 파일 `:26`).
- C2에서 V0는 Gaussian보다도 나쁩니다. 판정점 3/3에서 V0의 실패가 더 많았고, −3 dB에서 166:844입니다(`results/tables_D2_B16e4k.txt:331-335`).

**해석** `[가설]`
- "음의 고유값은 D2의 참 posterior 공분산이 여차원 방향에서 거의 특이해서, 0 근처의 작은 추정 오차가 부호를 뒤집기 때문"이라는 설명이 있습니다(`PAPER_MATERIALS.md:455-470`의 "margin" 설명).
- 이 설명은 코드 식에서 유도된 것이 아닙니다. D2에는 닫힌 형식의 참 posterior가 없으므로 검증되지 않았습니다.
- 사전 등록 근거는 (F1)입니다(`10_SPEC_stageC.md:86-91`).

### 4.5 V1-edge (K2): 격자 위쪽 질의에 대한 규칙 `[코드]`

V1은 $\varsigma>\varsigma_{\rm hi}$여도 네트워크를 그대로 외삽합니다(`conf/code/score.py:1076-1078`). V1-edge는 **$\nu_q>\nu_{\rm hi}=2\varsigma_{\rm hi}^2$일 때만** 다르게 동작하고, 그 밖에서는 `ScorePrior._eval`을 그대로 호출합니다. 따라서 V1과 비트 단위로 같습니다(`conf/code/prior_variants.py:60-62`).

위쪽 질의에서는 잡음을 정확히 둘로 나눕니다.
- $\mathbf q=\mathbf z+\mathbf e_2$, $\mathbf z=\mathbf h+\mathbf e_1$
- $\mathbf e_1\sim\mathcal{CN}(\mathbf 0,\nu_{\rm hi}\mathbf I)$, $\mathbf e_2\sim\mathcal{CN}(\mathbf 0,(\nu_q-\nu_{\rm hi})\mathbf I)$

$$
p(\mathbf z\mid\mathbf q)\propto p_{\nu_{\rm hi}}(\mathbf z)\,e^{-\|\mathbf q-\mathbf z\|^2/(\nu_q-\nu_{\rm hi})}
$$

- 이 분포를 **격자 안 학습 score만 써서** ULA로 샘플링합니다.
  - 체인 16개, burn 100, keep 100
  - 스텝 $\epsilon_{\rm ULA}=0.05\min(\nu_{\rm hi}/2,\,(\nu_q-\nu_{\rm hi})/2)$ (실수 차원당 분산 기준)
  - 출처: `conf/code/prior_variants.py:73-88`. 설정은 raw meta로 확인했습니다(`results/review_next/K2_report.txt:3`).
- 그다음 다음 식으로 계산합니다(`:89-95`). Jacobian 평균은 마지막 16개 상태로 냅니다.

$$
\mathbf m=\mathbb E_{\mathbf z\mid\mathbf q}[D(\mathbf z,\nu_{\rm hi})],\quad
\mathrm{Cov}=\nu_{\rm hi}\,\mathbb E_{\mathbf z\mid\mathbf q}[\mathbf J(\mathbf z,\nu_{\rm hi})]+\mathrm{Cov}_{\mathbf z\mid\mathbf q}[D],\quad
\mathbf J\leftarrow\Pi_{\rm PSD}(\mathrm{Cov}/\nu_q)
$$

- 대조군 V1-clamp는 $\mathbf m=D(\mathbf q,\nu_{\rm hi})$, $\mathrm{Cov}=\nu_{\rm hi}\mathbf J(\mathbf q,\nu_{\rm hi})$입니다.

**어느 셀에서 V1-edge가 V1과 달라지는가** `[유도]`
- 보조정리(§4.3 (c))에 따라 $T_p=N_t$이면 모든 반복에서 $\nu_q\le\sigma^2/4$입니다. SNR ≥ −3 dB이면 $\le0.4988$입니다.
- **C2**: $0.4988<\nu_{\rm hi}=1.4286$입니다. 따라서 **모든 블록, 모든 반복에서 위쪽 질의가 0개**이고, V1-edge ≡ V1(비트 단위)입니다.
  - [기록] 개발 집합 40블록(2560..2599, 16반복 전체)에서 `n_oog 0`이고 비트 단위로 같았습니다(`logs/review_next/k2_pre_c2.log`의 `pre-check (b)` 줄).
- **C6**: NR16 격자의 $\nu_{\rm hi}=0.48318<0.4988$입니다.
  - 따라서 **−3 dB에서는 모든 블록의 첫 반복 질의가 격자 위쪽**입니다. $\varsigma=0.4994>\varsigma_{\rm hi}=0.4915$이고, V1은 여기서 외삽합니다.
  - 이후 반복은 $\le0.4988$이지만 위쪽일 수 있습니다. C6 raw에는 질의별 기록이 없습니다.
  - 0 dB 이상에서는 $\sigma^2/4\le0.25<\nu_{\rm hi}$입니다.
  - C6에서 V1-edge는 **돌리지 않았습니다.**
- **C1, C5** ($T_p<N_t$): 보조정리가 적용되지 않습니다. 실제로 C1 −3 dB에서 V1은 ν_q 가 기록된 블록(2246/2560)이 전부 첫 반복에서 격자 위쪽을 질의했고(ν_q = 1.998), 전 블록에서 발산 가드가 발동했습니다(`results/review_next/K2test_report.txt:7`). 보고서의 0.88 은 예외로 끝난 314 블록(ν_q 없음)을 '위쪽 아님'으로 센 값입니다(`code/diag_prior_swap.py:243`; `NEXT_EXPERIMENTS_K1K2.md` §5.3 항목 5).
  - V1-edge 결과: C1 −3 dB 테스트 집합에서 b\*→V1-edge 400:264, $p=1.5\times10^{-7}$ [기록] (`results/review_next/K2test_report.txt:12`). 그 전의 1차 판정은 등록 판정 집합(trial 3200..4479, n=1280)에서 198:134, $p=5.3\times10^{-4}$입니다(`results/review_next/K2_report.txt:1,12`).
  - 개발 집합 점(trial 2560..3199, n=640, 판정에 쓰지 않음)에서는 셀과 SNR마다 결과가 다릅니다 [기록] (`results/review_next/K2_report.txt:22-51`).
    - C1 0 dB: V1의 첫 반복 질의가 전부 격자 위쪽(1.00)이었는데도 발산 가드는 0회였고, V1 실패 306은 b\* 344보다 적었습니다(`:26,28`).
    - C5 −6 dB (K2 보고 전용, 셀 C5 의 등록 SNR 격자 밖 점; `NEXT_EXPERIMENTS_K1K2.md:67`): V1은 첫 반복 질의가 전부 위쪽이었고, 전 블록(640)에서 가드가 발동했습니다(`:49`). V1-edge는 가드 0회, 실패 505였고 b\*는 579였습니다(`:47,52`).

### 4.6 그 밖의 참조 수신기 (보고 전용, bound 아님) `[코드]`

- **genie**: §3.6
- **LO (P4-LO)**: 참 기하 $(L,\theta,\phi)$를 아는 조건부 2차 모멘트 $\mathbf C_z=\mathbf V\mathrm{diag}(\mathbf p)\mathbf V^H$에 ridge를 더한 Gaussian prior입니다. LO-S는 V1 배선을 씁니다(`conf/code/diag_latent_oracle.py:6-17`).
- **BR-S (K1, Bayes-G)**
  - 경로 이득을 $\mathcal{CN}(0,p_\ell)$로 완화한 생성기 posterior입니다.
  - 잠재변수는 $\mathbf q$에서 griddy Gibbs로 추론합니다: 각도 격자 96×48, 체인 4개, burn 25, keep 75.
  - V1 배선을 씁니다(`conf/code/prior_variants.py:16-19,104-107`).

---

## 5. 평가

1. **BLER@16** `[코드]`
   - 식: $\widehat{\rm BLER}=\frac1n\sum_{s}\mathbb 1[\hat{\mathbf u}^{(16)}_s\ne\mathbf u_s]$ (`Demo/t2_route_a.py:434`)
   - 예외를 던진 블록은 NaN 행으로 남기고(`conf/code/runner.py:468-473`) **실패로 셉니다**(`conf/code/analysis.py:172-180`, `conf/code/recovery_ci.py:21-24`).
   - 신뢰구간은 95% Wilson입니다(`Demo/exp_0921_analysis.py:38-41`).
2. **표본과 짝** `[코드]`
   - 점마다 스트림 하나를 씁니다: `default_rng([20260926, 2, 4, Nr, T, Tp, SNR+100])` (`conf/code/common.py:168-169`)
   - 테스트 집합은 trial 0..2559($n=2560$)입니다.
   - 개발 집합은 2560..부터, P3 판정용은 3200..부터입니다(`conf/code/common.py:44-45`).
   - 한 셀 안에서는 모든 arm이 같은 $(\mathbf H,\mathbf u,\pi,\mathbf W)$를 봅니다.
3. **짝지은 정확 부호검정** `[코드]`
   - $a=\#\{x\text{만 실패}\}$, $b=\#\{y\text{만 실패}\}$로 둡니다(`Demo/exp_0921_analysis.py:44-51`).
$$
p=\min\!\Big(1,\ 2\sum_{i=0}^{\min(a,b)}\tbinom{a+b}{i}2^{-(a+b)}\Big)
$$
4. **판정점, 검정력 가드, 유의 규칙** `[코드]` (`conf/code/analysis.py:403-451`)
   - **판정점**: anchor arm의 BLER@16(하한 $0.5/n$)이 $[0.005,0.9]$ 안에 있는 격자 SNR 가운데, $|\log_{10}(\mathrm{BLER}/0.1)|$이 가장 작은 3점입니다.
   - **anchor**: 비교 쌍의 baseline 쪽입니다. b\*→V1이면 b\*, Gaussian→\*이면 Gaussian입니다(`:375-400`).
   - **검정력 가드**: 판정점이 3개이고, 그중 2점 이상에서 불일치 쌍이 6개 이상이어야 합니다(`MIN_DISC=6`, `Demo/exp_0925_analysis.py:94`). 못 채우면 **UNDECIDED(판정하지 못함)**입니다.
   - **유의 규칙**: 한 방향으로 $p<0.05$인 판정점이 2개 이상이면 유의합니다. "3/3"은 세 점 모두 유의하다는 뜻입니다.
   - 가드를 넘지 못했거나 유의하지 않은 비교는 **판정하지 못함**으로 적습니다. 차이가 없다는 뜻이 아닙니다.
5. **SNR@0.1과 격차** `[코드]` (`Demo/exp_0925_analysis.py:45-71`)
   - $\log_{10}\max(\mathrm{BLER},0.5/n)$를 SNR(dB)에 대해 선형 보간하고, **처음으로 0.1 아래로 내려가는 SNR**을 씁니다.
   - 격차는 $\Delta=\mathrm{SNR}_{0.1}(x)-\mathrm{SNR}_{0.1}(y)$입니다.
   - 90% 짝지은 bootstrap: $B=2000$, seed 20260925입니다. SNR마다 trial을 다시 뽑되, 두 arm에 같은 인덱스를 씁니다.
   - 두 arm이 모두 최저 격자점에서 이미 0.1 아래이면 "n/a"입니다(C6: `results/tables_D2_NR16B16e4.txt:373`).
6. **동일 예산** `[코드/기록]`
   - **데이터**
     - 두 prior는 모두 stream 7의 같은 채널 $N'=1.6\times10^5$개를 씁니다(`conf/code/runner.py:916-921`, `conf/code/arms.py:85-88`).
     - GMM은 $N'$ 전부로 EM을 돌리고, **추가로 독립 검증 집합 5000개**(stream 8)를 조기 종료와 $(\kappa,\text{restart},K,\text{family})$ 선택에 씁니다.
     - score 네트워크는 같은 $N'$을 9:1(144,000/16,000)로 나눠 씁니다(`conf/code/score.py:653-664`).
     - 이 비대칭은 baseline 쪽에 유리합니다(`DECISIONS.md:10`).
   - **$\hat{\mathbf C}$의 쓰임**
     - Gaussian arm은 $\hat{\mathbf C}$를 prior로 씁니다.
     - score arm은 초기 $\nu_E$와 $e_b$ bookkeeping에만 씁니다(§3.0).
     - **b\*는 $\hat{\mathbf C}$를 쓰지 않습니다** (§4.2).
   - **계산량은 맞추지 않았고, 두 숫자는 같은 척도도 아닙니다.**

     | 셀 | GMM EM | DiT 학습 |
     |---|---|---|
     | C2 | 107,957 s = Nr=8 fit 파일 13개의 `sec` 합. 각 파일은 κ × 재시작 EM 실행 시간의 합이고, 병렬로 실행했으므로 **wall-clock이 아님** (raw meta `em_sec_note`) | 35,775 s = **GPU 1장의 wall-clock** (raw meta `fit_sec`) |
     | C6 | 46,650 s (fit 파일 15개의 `sec` 합. GPU, kron은 batched 경로: 아래 참고) | 36,743 s |

     - C6 적합 15개는 모두 GPU에서 돌았고(`logs/nr16b_gpu*.log`의 `[gpu-fit]` 줄), kron 적합은 batched M-step 경로를 썼습니다(`results/review_next/NEXT_EXPERIMENTS_C6B16e4.md:79`).
     - 이 경로는 $K=512$에서 정확 경로보다 15.4배 빨랐습니다(`results/nr16b_batched_check.txt:10`). batched 경로는 C2 적합이 끝난 뒤에 추가됐습니다(커밋 `96ca6581`, 2026-09-25).
     - 따라서 EM 초는 C2와 C6 사이에서도 같은 척도가 아닙니다.

7. **Genie-gap 회수율** `[코드]` (`conf/code/recovery_ci.py:1-4,27-42`)
   - $F$는 나열한 SNR에서 @16 실패 수의 합입니다.
$$
\mathcal R=\frac{F_{b^*}-F_{\rm V1}}{F_{b^*}-F_{\rm genie}}
$$
   - 90% 짝지은 bootstrap: $B=2000$, seed 20260926입니다. 세 arm을 **같은 trial 인덱스로 함께** 다시 뽑고, 합산할 때는 모든 SNR에 같은 인덱스를 씁니다.
   - **보고 전용입니다.** 판정 통계로 등록되지 않았습니다.

**이 정식화에서 기록된 헤드라인 수치** [기록]

| | C2 (N′=1.6e5, 헤드라인) | C6 (N′=1.6e5, UNGATED 측정) |
|---|---|---|
| 판정점 (anchor b\*) | −3, 0, +3 dB (`tables_D2_B16e4k.txt:368`) | −3, 0, +3 dB (`tables_D2_NR16B16e4.txt:369`) |
| b\*→V1 부호검정 | −3/0/+3 dB: 302:50, 117:21, 35:7. pooled 454:78, 3/3 (`:369-371`) | 142:11, 45:4, 26:3. pooled 213:18, 3/3 (`:370-372`) |
| SNR@0.1 격차 (b\* − V1) | **+1.41 dB** [1.22, 1.64] (`:372`) | n/a: 두 arm 모두 −3 dB에서 이미 0.1 아래 (`:373`) |
| −3 dB 실패 수 b\* / V1 / genie (n=2560) | 623 / 371 / 87 | 184 / 53 / 22 |
| $\mathcal R$ at −3 dB | 0.470 [0.427, 0.512] (`review_next/recovery_B16e4k.txt:2`) | 0.809 [0.747, 0.870] (`review_next/recovery_NR16B16e4.txt:2`) |
| 마지막 epoch 가중치로 평가한 경우 | 해당 없음 (평가 자체가 마지막 epoch) | 208:17, $\mathcal R=0.815$ [0.756, 0.872] (`review_next/NEXT_EXPERIMENTS_C6B16e4.md:102`) |

위 표의 파일 경로는 모두 `results/` 아래입니다.

---

## 6. 스펙과 코드가 어긋나는 곳, 범위와 캐비엇

### 6.1 스펙–코드 불일치 (갱신판)

| # | 항목 | 스펙 | 코드(실제) | 원고 처리 |
|---|---|---|---|---|
| F1 | D2 스케일 | $\sqrt{N_rN_t/L}$, $\sum p_\ell=1$ (`05_SPEC_testbed_D2.md:13,20`) | $\sqrt{N_rN_t}$ (`conf/code/d2.py:34-39,140`), `DECISIONS.md:13` | 코드 식을 씁니다 |
| F2 | $\sigma$ 격자 측정 | D1에서 R2로 측정, 양은 "$\mathbf G$의 유효 잡음" (`04_SPEC_diffusion.md:50-52`) | D2에서 Gaussian $\hat{\mathbf C}$(N=1e4)를 **score 배선**에 넣고 D-13의 $\nu_q$를 기록(`conf/code/sigma.py:4-7,33-35`, `DECISIONS.md:12`). C2 격자는 C1과 C2의 14점, C6 격자는 C6의 7점 | "수신기가 실제로 보내는 $\nu_q$의 1–99 백분위"로 쓰고, 측정 조건을 적습니다(§4.3 (b)) |
| F3 | 학습 표본 수 | $N_{\rm train}=10^4$ (`04_SPEC_diffusion.md:30`) | Stage C에서 $N'=1.6\times10^5$ (`10_SPEC_stageC.md:38,107`) | 예산 곡선의 한 점으로 명시합니다 |
| F4 | "같은 split" | `10_SPEC_stageC.md:38-39` | GMM: $N'$ 전부 + **추가 검증 5000개**. score: $N'$을 9:1로 분할. $\hat{\mathbf C}$는 Gaussian arm(prior)과 score arm(bookkeeping)만 쓰고, b\*는 쓰지 않음 | 예산 정의에 비대칭을 적습니다. baseline에 유리한 쪽입니다 |
| F5 | $K$ 격자 | {16..128} (`05_SPEC_testbed_D2.md:66`), {16..512} (`10_SPEC_stageC.md:115`) | 실제 적합 격자는 §4.2 표와 같습니다. C2는 full 16..512, kron 16..1024이고, **b\*는 격자 끝**입니다. full 64/128/256은 **500반복 상한**에서 멈췄습니다. C6는 kron 4096이 격자 끝(사용자 결정)이고, 적합 대부분과 b\*가 train-ll 조건으로 멈췄습니다. b\*를 포함한 kron 4096 재시작 셋은 검증 우도가 마지막 평가에서 최고인 채 멈춰, 덜 수렴했을 수 있습니다(V1에 유리한 방향, `results/review_next/NEXT_EXPERIMENTS_C6B16e4.md:135`) | 두 캐비엇을 모두 붙입니다 |
| F6 | 게이트와 가중치 | D2 checkpoint는 D1 형제 모델의 게이트 통과로 자격을 얻음 (`10_SPEC_stageC.md` §5) | C2: 게이트 행 없음(UNVERIFIED), 레시피는 D1 형제가 통과, **마지막 epoch EMA로 평가**(검증 손실 최소 epoch 가중치는 미저장). C6: **UNGATED, 검증 손실 최소 epoch EMA로 평가, grad_clip 1.0 레시피**, 481,474 파라미터 | 두 셀의 가중치 규칙과 레시피가 다르다는 점을 표로 밝힙니다(§4.3 (a)) |
| F7 | 파일럿 규칙 | "prior S → eigen-aligned" (`06_SPEC_runner.md:56`) | D2/S2는 T2b 판정으로 **DFT** (`conf/code/common.py:133-137`) | DFT로 씁니다 |
| F8 | 헤드라인 셀 | C1 (`00_GOAL.md` §5, `06_SPEC_runner.md:65`, 주석 `conf/code/common.py:56`) | Stage C가 BLER을 보기 전에 C2를 주 셀로 고정 (`10_SPEC_stageC.md` §6) | 헤드라인은 C2입니다. 코드 주석은 옛 내용입니다 |
| F9 | 모듈 설명 | `Demo/t2_route_a.py:15` docstring은 `scal='site'`를 설명 | score arm은 `scal='belief'` (`conf/code/arms.py:37`) | §4.3 (c)의 식을 씁니다 |
| F10 | SNR 정의 | 어느 스펙에도 없음 | $\sigma^2=10^{-\mathsf{SNR}/10}$, layer당·수신 안테나당 SNR | 정의, +6.02 dB 환산, $E_b/N_0$ 차이(+1.83 dB)를 적습니다(§1.3) |
| F11 | (F1) 표기 | $\mathbf J=\mathrm{Cov}/\sigma^2$ (`10_SPEC_stageC.md:87`) | $\mathbf J=\mathrm{Cov}/\nu_q$ ($\nu$는 복소 원소당 분산) | $\nu_q$로 통일합니다 |
| F12 | "반복 1은 항상 격자 위쪽" | 코드 주석 `conf/code/score.py:1143-1144`, `DECISIONS.md:22` | $T_p=N_t$이면 $\nu_q\le\sigma^2/N_t$ (§4.3 보조정리). **C2는 모든 반복이 격자 안이거나 아래**입니다. **C6 −3 dB는 첫 반복이 모든 블록에서 위쪽**입니다. C1은 −3 dB 첫 반복이 위쪽(1.997)이고 15 dB에서는 안쪽(1.015)입니다(`results/sigma_grid_D2.txt:22,28`) | 주석을 인용하지 않습니다. 셀별 사실을 적습니다 |
| F13 | Stage C 판정점 anchor | "앵커 arm은 R2-ours-G" (`10_SPEC_stageC.md:144`) | b\*→V1 쌍의 anchor는 b\* (`conf/code/analysis.py:398`) | C2와 C6 모두 두 anchor가 {−3, 0, +3}이라 실질적 영향이 없습니다(`results/tables_D2_B16e4k.txt:332,368`, `results/tables_D2_NR16B16e4.txt:339,369`) |
| F14 | 인터페이스 비대칭 | 스펙 위반은 아님 | b\*는 비등방 cavity에 대한 정확한 EP, 학습 prior는 등방 cavity와 행렬 site | 비교가 "prior + 인터페이스" 묶음끼리임을 밝히고, 대조군 `gmmB-scorew-eta`를 언급합니다 |
| F15 | "PDP" 용어 | `conf/code/d2.py:66` 주석 | 지연을 모델링하지 않음 | "경로 전력 프로파일"로 씁니다 |
| F16 | Jacobian 근사 | 없음 | $\partial\mathbf m/\partial\mathbf q^*$를 버리고 proper Gaussian site를 가정 | 근사라고 명시합니다 |
| F17 | 하한을 두 번 적용 | 없음 | V1은 $\mathbf J$와 $\boldsymbol\Lambda$ 양쪽에 $\lambda_{\min}$, V0는 $\boldsymbol\Lambda$에만 | §4.3 (e)(g)의 식으로 보입니다 |
| F18 (신규) | 격자 측정 표본 | 없음 | $\sigma$ 격자를 각 점 테스트 스트림 trial 0..63의 실현에서 측정(Gaussian 수신기의 $\nu_q$만, BLER은 쓰지 않음; `conf/code/sigma.py:36-42`) | 원고의 재현성 절에 한 줄 적습니다 |
| F19 (신규) | OFDM 해석 | 없음 | 코드는 추상 블록 모델뿐 | (A1)–(A5)를 가정으로 명시하고, NR 대응은 분포 동치로만, 구성 하나를 정해서 씁니다(§1.2) |
| F20 (신규) | 공분산 bookkeeping 주석 | 없음 | docstring `conf/code/score.py:1072-1074`는 score arm의 $\hat{\mathbf C}$가 "GMM arm이 받는 것과 같은 표본 공분산"이라고 적음. 실제로 b\*의 $\mathbf C_{\rm pr}$는 $\sum_k\pi_k\mathbf C_k$이고, b\*는 $\hat{\mathbf C}$를 쓰지 않음(§3.0, §4.2) | 주석을 인용하지 않습니다. arm별 $\mathbf C_{\rm pr}$와, C2·C6에서 결과에 영향이 없다는 논증(§3.0)을 씁니다. 코드 주석은 옛 내용입니다 |

### 6.2 범위와 캐비엇 (원고의 scope 절: 마지막에 두지만 빼지 않음)

1. **testbed**
   - 주장은 D2 한 모델에서 나온 것입니다. D2는 통제된 모델이며, 표준이나 현실 채널로 제시하지 않습니다(`conf/code/d2.py:24-29`).
   - D1은 게이트 측정 도구입니다.
   - 두 번째 testbed는 계획 문서만 있고 결과는 없습니다(`docs/plans/2026-09-25_sionna_deepmimo_gmm_vs_dm.md`).
2. **C6의 지위**
   - UNGATED이므로 "기하·예산 축 측정"이고, arm 판정이 아닙니다.
   - 회수율 대역 문장과 반드시 함께 씁니다.
   - C6는 어느 결과에서도 헤드라인이 되지 않습니다(`results/review_next/NEXT_EXPERIMENTS_C6B16e4.md:28,44`).
3. **GMM 격자의 끝**
   - C2 b\*는 kron 1024, C6 b\*는 kron 4096이고 둘 다 격자 끝입니다. $K$를 늘릴 때 검증 우도가 아직 오르는 중입니다.
   - C2 full 64/128/256은 반복 상한에서 멈췄습니다.
   - C6 적합 대부분과 b\*는 train-ll 조건으로 멈췄습니다(§4.2).
   - C6 b\*를 포함한 kron $K=4096$ 재시작 셋은 검증 우도가 마지막 평가에서 최고인 채 멈췄습니다. 따라서 C6 b\*는 덜 수렴한 GMM일 수 있고, 이 방향은 V1에 유리합니다. C2 b\*는 patience로 멈췄습니다(`results/review_next/NEXT_EXPERIMENTS_C6B16e4.md:135`).
   - C6의 측정 판정(213:18)과 회수율 대역 문장($\mathcal R=0.809$)을 인용할 때는 격자 끝 캐비엇과 이 캐비엇을 함께 붙입니다(같은 곳).
4. **가중치와 레시피 차이**
   - C2는 마지막 epoch EMA로, C6는 검증 손실 최소 epoch EMA와 grad clip 레시피로 평가했습니다.
   - C6는 마지막 epoch 가중치로도 평가했습니다. b\*→V1은 검증 손실 최소 가중치에서 213:18, 마지막 epoch 가중치에서 208:17입니다. $\mathcal R$은 각각 0.809 [0.747, 0.870], 0.815 [0.756, 0.872]입니다(`results/review_next/NEXT_EXPERIMENTS_C6B16e4.md:102-103`, §5 표).
5. **격자 밖 외삽**
   - C6 −3 dB에서는 모든 블록의 첫 반복 V1 질의가 NR16 격자 위쪽 외삽입니다.
   - C2에는 위쪽 질의가 없습니다.
   - $T_p<N_t$에서는 셀과 SNR마다 다릅니다(§4.5).
     - C1 −3 dB(테스트 집합)와 C5 −6 dB(개발 집합, 등록 SNR 격자 밖 보고 점)에서는 V1의 발산 가드가 전 블록에서 발동했습니다(`results/review_next/K2test_report.txt:7`, `results/review_next/K2_report.txt:49`).
     - 격자 위쪽 규칙만 바꾼 등록 변형 V1-edge는 두 점에서 가드가 0회였고, 실패가 b\*보다 적었습니다. C1 −3 dB에서 b\*→V1-edge 400:264(`K2test_report.txt:12`), C5 −6 dB에서 86:12(`K2_report.txt:54`)입니다.
     - C1 0 dB(개발 집합)에서는 V1의 첫 반복 질의가 전부 격자 위쪽이었는데도 가드가 0회였고, V1 실패(306)가 b\*(344)보다 적었습니다(`K2_report.txt:26,28`).
     - 따라서 "격자 위쪽 질의가 있으면 V1이 무너진다"로 일반화하지 않습니다.
6. **인터페이스 비대칭과 Jacobian 근사**: F14, F16, F17
7. **계산량**: 맞추지 않았습니다. GMM EM 초 합계와 DiT wall-clock은 같은 척도가 아닙니다. C6 kron 적합의 EM 초는 batched 경로(×15.4)에서 나와 C2 (GPU 정확 경로) EM 초와도 같은 척도가 아닙니다; C6 full 적합은 정확 경로입니다(§5.6, `NEXT_EXPERIMENTS_C6B16e4.md:79`).
8. **OFDM과 NR 해석**: 전부 가정입니다. NR 대응은 BLER 분포 동치로만 성립하고, 파일럿 구성 하나에 대해서만 성립합니다(§1.2).
9. **음의 Jacobian 고유값의 기하 설명**: [가설]입니다(§4.4). C6 checkpoint의 스펙트럼은 측정하지 않았습니다.
10. **파일럿 위치 불변성의 수치 확인**: 저장소 기록입니다(`results/review_next/pilot_position_check.txt`, §1.1). 점검한 수신기는 RouteA-Gaussian, R3, R4입니다. score arm과 b\*에는 구조 논증만 적용됩니다. 흩어 놓은 파일럿 배치는 채널 쪽 합 $(\mathbf G,\mathbf b)$만 비교했습니다.
