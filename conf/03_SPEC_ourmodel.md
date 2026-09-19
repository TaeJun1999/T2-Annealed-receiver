# 03 — 우리 모델 설계 지침 (M-ours)

> **착수 시점: baseline R3·R4의 단위 테스트가 전부 PASS한 뒤.** 이 순서를 바꾸지 마라.
> 이유는 편의가 아니라 무결성이다. baseline을 먼저 고정해 두면, 나중에 우리 모델의 숫자가 기대에 못 미칠 때 baseline을 약화시키는 쪽으로 손이 가는 경로가 구조적으로 막힌다.

---

## 0. 이 모델의 diffusion 성분 — 무엇이 들어 있고 무엇을 주장하지 않는가

| | 내용 | 이 실험에서 |
|---|---|---|
| **A** | **Decoder 소프트 출력 = 부호심볼 prior의 정확 Tweedie score**, $L_c(t)=2/\sigma_t^2$. annealing 축 = 반복 인덱스 | **들어 있다.** BCJR을 쓰는 모든 arm의 기반. `exp_0915`가 기계 정밀도로 검증 완료 → §6에서 그림으로 |
| **B** | **채널 score prior (oracle 형)** = `M-ours-score` (참 prior 정확 score + D-13 + D-14) | **들어 있다, 단 D1에서만.** 학습 score의 **상한이자 품질 게이트의 기준**(`04_SPEC_diffusion.md` §5) |
| **C** | **학습된 diffusion / score 네트워크** = `M-ours-dscore` | **들어 있다.** 사다리 L1~L6로 학습하고 사전 등록 게이트로 심판한다(`04_SPEC_diffusion.md`) |
| **D** | **다단계 annealed sampling** (R-A) | **넣지 않는다.** D-17 철회로 이미 기각(exp_0923 기준 미달, exp_0924는 one-shot보다 나쁨). 인터페이스는 one-shot + D-13 + D-14로 고정 |

### 주장의 경계 (결과 파일 헤더에 적을 것)

- `M-ours-score`는 **oracle arm**이다. 학습된 prior가 아니다. **계측기이지 주장이 아니다.**
- **D1(격자 GMM testbed)의 결과로는 "학습 prior가 이득을 준다"를 주장할 수 없다.** 참 prior가 GMM으로 *정의*되어 있어 GMM arm이 correctly specified이기 때문이다. D1 결과 헤더에 이 경고를 반드시 넣는다.
- **주장은 D2(sparse specular)에서만 한다**(`05_SPEC_testbed_D2.md`).
- 인터페이스(one-shot + D-13 + D-14)는 oracle arm과 학습 arm이 **동일**하다. 그래야 둘의 차이가 score 자체의 차이가 된다.

---

## 1. 우리 모델의 정의 (conference 버전)

**우리 모델 = R2의 루프 + Module H.** R2와의 차이는 **Module H 하나뿐이어야 한다.** 다른 것이 하나라도 달라지면 논문의 headline 격차가 무엇의 몫인지 말할 수 없게 된다.

### 1.1 루프 (R2와 완전히 동일 — 바꾸지 말 것)

| 항목 | 값 | 출처 |
|---|---|---|
| 채널 추정 입력 $L_H$ | decoder **a-posteriori** $(\bar x_n, v_n)$ 소비 | D-15 |
| 검출 출력 $L_X$ | **extrinsic + LOO** (leave-one-out) | D-15 |
| posterior 경로 damping | **없음** (`beta_fb=None`) | D-15, Q-24 닫힘 |
| damping $\beta$ | 0.7 | v1 기본 구성 |
| `n_inner` | 1 | v1 기본 구성 |
| 외부 반복 | 16 | 전 arm 공통 |
| site clip 규칙 | 기존 기본값 그대로 | Q-34 미결이므로 바꾸지 않는다 |

### 1.2 Module H 후보 (셋 다 만든다)

| arm | Module H | 비고 |
|---|---|---|
| `M-ours-gmm32` | 채널 dataset에 GMM 적합(EM) → **정확 mixture EP site**, $K=32$ | D-18 |
| `M-ours-bstar` | 같은 것, **검증 우도 최대** arm (`b*`) | 선택은 **검증 우도만**. BLER 미사용 |
| `M-ours-score` | 참 prior 정확 score + D-13(belief) + D-14(matrix site) | **D1 전용.** oracle 상한 = 게이트 기준 |
| `M-ours-dscore` | **학습된 diffusion score** + D-13 + D-14 (인터페이스 동일) | `04_SPEC_diffusion.md`의 게이트를 통과한 모델 |

> **어느 것이 논문의 "우리 모델"인지는 이번 실험이 정하지 않는다.** 별도의 사전 등록 실험(exp_0925)이 정한다. 셋 다 돌리고, **이번 BLER을 보고 고르지 않는다.** (`01_RULES.md` §5)

---

## 2. 무엇을 만드는가 — 얇은 조립기 + 동등성 증명

`Demo/`에 이 구성요소들이 **이미 있다**(`t2_route_a.py`의 `RouteA`/`RouteAClip`, `t2_gmm.py`의 `GMMPriorB.ep_site`·`denoise_full`·`fit_gmm_em`, score denoiser 경로). **재구현하지 마라.** `conf/code/`에 만드는 것은 그 위의 얇은 층이다:

| 단위 | 책임 | 불변식 |
|---|---|---|
| **config 객체** | §1.1의 설정을 **명시적 필드**로 보유. 하드코딩 금지 | 결과 파일에 전체 덤프 |
| **조립기** | config → `Demo/`의 수신기·Module H를 조립해 반환 | 기존 클래스의 기본값에 의존하지 않고 **전부 명시적으로 전달** |
| **GMM 적합 단계** | 채널 dataset($N_{\rm train}=10^4$) 생성 → `fit_gmm_em` → `b*` 선택 | 선택 기준 = **검증 우도만**. 적합 wall-clock 기록 |

> **GPU 참고.** GMM EM 적합과 1024성분 batched EP site가 이 실험에서 GPU 이득이 가장 큰 지점이다(`01_RULES.md` §9.2 순위 1·2). 다만 CPU 실측이 3분 25초였으므로 **먼저 CPU로 재어 보고** 예산을 넘길 때만 옮긴다. 옮기면 §9.3의 5개 조건과 테스트 G1·G2를 전부 지켜야 한다.
| **동등성 검사** | 조립기 출력이 `Demo/`의 기존 arm과 동일한지 | §4의 M1~M3 |

**하드코딩 금지의 이유.** `RouteA` 생성자 기본값은 회귀 테스트 t0/t6이 의존하고 있어 D-15 설정과 다르다(핸드오프 #4). 기본값에 기대면 조용히 다른 수신기를 돌리게 된다. 전부 명시적으로 넘겨라.

---

## 3. `Demo/`에서 못 찾았을 때의 fallback

먼저 `Demo/t2_route_a.py`, `t2_gmm.py`, `Demo/exp_0925_run.py`를 끝까지 읽어라. exp_0925가 이 arm들을 실제로 돌렸으므로 그 러너에 조립 방법이 적혀 있다.

그래도 없으면: §1의 정의대로 만들고 **DECISIONS.md에 다음을 반드시 적어라** — "기존 arm을 찾지 못해 정의로부터 구성했다. exp_0925 결과와 교차 확인 불가." 이 경우 §4의 M1~M3는 SKIP이 아니라 **`UNVERIFIED`** 로 기록한다. 검증 없는 숫자임을 표에 남긴다.

---

## 4. 동등성·정합성 테스트 (M1~M4)

`07_SPEC_tests.md`에도 같은 목록이 있다. 둘 중 하나가 틀리면 `07_SPEC_tests.md`가 정본이다.

| id | 내용 | 기준 |
|---|---|---|
| **M1** | 조립기의 `M-ours-gmm32`가 **`Demo/`의 기존 동일 arm과 동일 시드에서 로그 차이 0.0** | 정확히 0 |
| **M2** | 조립기의 Module H를 Gaussian(표본 공분산)으로 바꾸면 **`R2-ours-G`와 로그 차이 0.0** — 즉 R2와의 차이가 Module H 하나뿐임을 증명 | 정확히 0 |
| **M3** | GMM 적합의 항등식: $\sum_k\pi_k\mathbf C_k$ = 표본 공분산 | $\le10^{-12}$ |
| **M4** | config 덤프가 §1.1의 표와 **필드 단위로 일치**(자동 대조) | 전 항목 일치 |

**M2가 이 문서에서 가장 중요한 테스트다.** 논문의 headline 격차가 Module H의 몫이라는 주장의 유일한 증거다. M2가 FAIL이면 우리 모델 arm 전체를 `FAILED-VERIFICATION`으로 표시하고 baseline만 가지고 마무리한다 — 억지로 맞추지 마라.

---

## 5. 하이퍼파라미터에 손대지 않는다

$\beta$, 반복 수, clip 규칙, $K$, `n_inner`, LOO on/off는 **전부 기존 사전 등록 값**이다. 이번 실행의 결과를 보고 조정하지 마라. 새로 정해야 하는 값이 생기면 보수적인 쪽(우리 주장에 불리한 쪽)으로 정하고 DECISIONS.md에 적어라.

GMM 적합의 $K$, shrinkage $\kappa$, early stopping은 **검증 우도만으로** 정한다. BLER을 한 번도 보지 않은 상태에서 `b*`를 확정하고, 확정 시각을 DECISIONS.md에 기록해라.

---

## 6. Lemma 검증 (F2) — 값싸고 claim-independent

§0의 성분 **A**를 보이는 한 장짜리 그림. 논문의 이론 앵커이자, K1/K2/K3 어느 판정이 나와도 살아남는 유일한 결과다.

**이미 다 되어 있다.** `Demo/exp_0915_bcjr_score_check.py`가 종단 convolutional 부호의 전 codeword 열거로 다음을 기계 정밀도로 확인해 두었다 [측정]:
- $\tanh(L_k/2)$ [BCJR, $L_c=2/\sigma^2$] $= \mathbb E[x_k\mid\tilde{\mathbf x}]$ — $(133,171)_8$에서 오차 $\le2.3\times10^{-15}$
- Tweedie: $\nabla\log p_t(\tilde{\mathbf x}) = (\mathbb E[\mathbf x\mid\tilde{\mathbf x}]-\tilde{\mathbf x})/\sigma^2$ — 유한차분 오차 $\le6.9\times10^{-10}$
- Jacobian ↔ 조건부 공분산, Max-Log-MAP은 정확성을 깨뜨림, puncturing은 유지
- **복소 규약: $L_c=4/\sigma_c^2$가 정확하고 $2/\sigma_c^2$는 틀림** (이 폴더의 복소 구현 전반에 해당하는 경고)

**할 일은 재현 + 그림뿐이다.** 새 실험이 아니다. 예산 10분.

1. `conf/code/`에서 `Demo/exp_0915_bcjr_score_check.py`를 **수정 없이** 호출해 출력을 `conf/results/lemma.txt`로 남긴다.
2. $\sigma^2$(= annealing 수준) 축에 대해 BCJR 조건부 평균과 brute-force 값을 겹쳐 그리고, 오차를 로그 축 두 번째 패널로 그린다 → `conf/figs/F2_lemma.png`.
3. 재현 불가(파일 없음·의존성 오류)면 `BLOCKED`로 표시하고 넘어간다. **다시 구현하지 않는다.**
