# 05 — D2 testbed: sparse specular multipath (주장용)

> **왜 새 testbed가 필요한가.** 기존 D1은 참 prior를 $K_{\rm true}=32\times32$ **격자 GMM으로 정의**한 것이다. 즉 GMM arm이 **correctly specified**다 — 함수 형태가 정확히 맞는다. 거기서 GMM이 이겨도 "학습 prior가 무용하다"가 아니라 **"이 testbed가 GMM의 홈그라운드다"** 일 수 있다. 이 교란은 사전 등록된 kill test로도 통제되지 않는다.
>
> **선택 기준은 "GMM에 불리해서"가 아니라 "물리적으로 표준이라서"다.** 전자는 리뷰어가 정확히 그 지점을 친다. 아래 §1의 채널은 mmWave 희소 다중경로라는 표준 모델이고, 조건부 Gaussian 가정이 깨지는 것은 그 물리의 **귀결**이지 목적이 아니다.

---

## 1. 채널 모델

$$\mathbf H=\sqrt{\frac{N_rN_t}{L}}\sum_{\ell=1}^{L}\alpha_\ell\,\mathbf a_r(\theta_\ell)\,\mathbf a_t(\phi_\ell)^H$$

| 요소 | 규격 |
|---|---|
| 경로 수 $L$ | $\mathrm{Unif}\{3,\dots,8\}$, 블록마다 새로 뽑음 |
| AoA/AoD $\theta_\ell,\phi_\ell$ | **연속** 균등 (격자 없음). 전 범위 판 U2, 섹터 $\pm\pi/3$ 판 S2 |
| 경로 이득 $\alpha_\ell$ | $\alpha_\ell=\sqrt{p_\ell}\,e^{j\psi_\ell}$, $\psi_\ell\sim\mathrm{Unif}[0,2\pi)$ |
| 전력 프로파일 $p_\ell$ | **결정적** 지수 감쇠 $p_\ell\propto e^{-\ell/\tau}$, $\tau=2$, $\sum_\ell p_\ell=1$ |
| steering | ULA, 반파장 간격 |

### 이 모델이 D1과 다른 점 (핵심)

$|\alpha_\ell|$가 **결정적**이므로, **각도를 조건으로 줘도 $\mathbf H$가 Gaussian이 아니다.** 3GPP 계열 모델은 각도가 주어지면 $\alpha_\ell\sim\mathcal{CN}$ 이라 $\mathbf H\mid\text{angles}$가 Gaussian이고, 그래서 conditionally-Gaussian mixture(= GMM)가 correctly specified가 된다. 여기서는 그 성질이 깨진다. 이것이 D2의 존재 이유다.

> **주의 [추측, VERIFY].** "표준 채널이면 GMM에 불리하다"는 성립하지 않는다. Utschick 그룹의 GMM 채널추정 라인(arXiv:2112.12499, 2205.03634)이 존재하는 이유가 바로 3GPP 채널의 조건부 Gaussian 구조다. 따라서 CDL을 그냥 가져오면 **오히려 GMM에 유리할 수 있다.** D2의 차별점은 "실제 채널"이 아니라 **"조건부 Gaussian의 파괴"** 라는 것을 서술에서 흐리지 말 것.

---

## 2. 필수 검증 — BLER을 보기 전에 전부 끝낸다

testbed가 검증되지 않으면 그 위의 모든 숫자가 무효다. 세션 6에서 prior P가 "거의 백색이라 설계 전제가 성립하지 않았다"는 사고가 이미 한 번 났다. 같은 실수를 반복하지 않는다.

| id | 내용 | 기준 / 행동 |
|---|---|---|
| **T2a** | 정규화 $\mathbb E\|\mathbf H\|_F^2=N_rN_t$ | 상대 오차 $\le10^{-3}$ ($10^5$ 표본) |
| **T2b** | 앙상블 공분산 $\hat{\mathbf C}$의 **유효 rank**를 계산해 기록 | 백색에 가까우면(유효 rank $\gtrsim0.9\times$ 전차원) **eigen-aligned 파일럿이 무의미** → DFT 파일럿을 쓴다. 판정을 기록한다 |
| **T2c** | $T_p=2$ 첫 패스 $\mathrm{NMSE}_\infty$ 를 폐형식으로 계산 (세션 6의 논리 재적용) | $1-T_p/N_t$ 에 가까우면 같은 $T_p$의 (상한)−(하한) 비교가 공허해진다 → **교차-$T_p$ goodput으로 읽어야 한다.** 판정을 기록 |
| **T2d** | **조건부 Gaussian 파괴의 직접 증거.** 각도를 고정한 조건부 분포에서 $\mathbf H$ 성분의 4차 모멘트/kurtosis가 복소 Gaussian 값에서 벗어남을 수치로 제시 | 벗어나지 않으면 **모델이 의도대로 작동하지 않는 것** → BLOCKED로 올리고 사용자 판단을 기다린다 |
| **T2e** | 희소성 지표(참여 경로 수, 각도 도메인 에너지 집중도)를 기록 | 기록만 |

**T2d가 D2 전체의 정당성이다.** 통과 못 하면 D2에서 얻은 어떤 비교도 주장으로 쓸 수 없다.

## 3. testbed 교체에 따라 사라지는 것 (정직하게 기록)

| 잃는 것 | 대체 |
|---|---|
| `Hscore-exact` (참 prior 정확 score) | 없음. **D1에서만 존재** → 품질 게이트는 D1에서만 (`04_SPEC_diffusion.md` §5) |
| `exactEP-true` (oracle 상한) | 없음. 상한은 `R5-genie`만 남는다 |
| eigen-aligned 파일럿 정당성 | T2b의 판정에 따름 |
| 기존 GMM 적합·`b*` | **새 데이터로 전부 재적합.** 검증 우도만으로 재선택 |

## 4. GMM arm 재구성 (공정성)

D2에서 GMM이 약해 보이는 것이 **우리가 약하게 만들어서가 아님**을 보여야 한다. R3(세션 6의 arm 강화 규칙)를 그대로 적용한다:

- $K\in\{16,32,64,128\}$ 전부 적합. MAP shrinkage $\kappa$ + 검증 우도 early stopping.
- Kronecker 구조 성분도 시도(D2는 Kronecker가 아니므로 불리할 수 있으나, **시도했다는 기록이 필요**).
- **`b*` = 검증 우도 최대 arm.** BLER 미사용.
- 적합 표를 `conf/results/gmm_fit_D2.txt`에 남긴다: $K$별 train/val 우도, 과적합 격차, 적합 wall-clock.
- **GMM이 D1 대비 얼마나 나빠졌는지**를 명시적으로 표로 낸다. 이것이 "testbed가 실제로 조건부 Gaussian을 깼다"의 두 번째 증거다.

## 5. 실행 순서

D2는 **D1 작업이 전부 끝난 뒤**에 시작한다(`00_GOAL.md` Stage B). D1의 산출물 중 D2로 넘어가는 것:

- baseline R3·R4 구현 (그대로)
- 우리 모델 조립기 (그대로)
- score 학습 코드와 **게이트를 통과한 아키텍처·하이퍼파라미터** (§`04_SPEC_diffusion.md` §6 — D2에서 재탐색 금지)
- $\sigma_t$ 격자는 **D2에서 다시 측정한다**(수신기 질의 분포가 달라지므로)
