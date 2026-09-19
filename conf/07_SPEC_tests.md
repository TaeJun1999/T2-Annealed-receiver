# 07 — 단위 테스트 (사전 등록)

> **원칙: 검증되지 않은 숫자는 결과 표에 넣지 않는다.** 테스트가 FAIL인 arm은 본 실행에서 제외하고, 표의 그 자리에 `FAILED-VERIFICATION`을 남긴다.
>
> 각 테스트는 PASS/FAIL과 **함께 잔차 수치를 출력**한다. "PASS"만 찍는 테스트는 쓸모가 없다.
>
> 아래 목록은 **최소**다. 구현 중 위험하다고 느낀 지점이 있으면 테스트를 **추가**한다(추가는 자율 판단, DECISIONS에 기록).

---

## R3 (BiG-AMP)

| id | 내용 | 기준 |
|---|---|---|
| **B1** | **Damping 항등식.** $\beta=1$이 무감쇠 Table III와 일치 | $\le10^{-14}$ |
| **B2** | **AWGN 폐형식.** (R5)–(R8)의 폐형식(원문 식 71–72)이 수치 적분과 일치. 무작위 $(\hat p,\nu^p,y)$ 100점 | $\le10^{-10}$ |
| **B3** | **Genie 심볼.** 전 열에서 $\nu^x_{nl}=0,\ \hat x_{nl}=x_{nl}$(참값)로 고정하면 $\hat{\mathbf H}$가 전 열 LS 해에 수렴 | NMSE 차 $\le10^{-6}$ |
| **B4** | **실수 경로 대조.** 허수부 0 입력에서 복소 구현이 실수 참조 구현과 일치 | $\le10^{-12}$ |
| **B5** | **Onsager 배선.** (R4)의 $\hat s(t{-}1)$ 항을 0으로 두면 결과가 **달라진다**(항이 실제로 연결돼 있는지) | 상대차 $>10^{-3}$ |
| **B6** | **오타 방어.** (R7) 부호로 계산한 $\nu^s$가 AWGN 폐형식 $1/(\nu^p+\sigma^2)$와 일치하고 **양수**임 | $\le10^{-12}$, 전부 $>0$ |

## R4 (3-module SC-VAMP형)

| id | 내용 | 기준 |
|---|---|---|
| **S1** | **$f=\mathrm{id}$ 환원** [원문 명시]. Module A 출력이 매 반복 $(\mathbf y,\sigma^2)$로 상수 | $\le10^{-14}$ |
| **S2** | **Module C 폐형식** [원문 명시]. $\alpha^C_x=\frac1{N_t}\sum_n\frac{\sigma^2}{\sigma^2+v_x\lambda_n}$가 직접 역행렬의 $\frac1{N_t}\operatorname{Tr}\boldsymbol\Sigma^C/v_x$와 일치 | $\le10^{-12}$ |
| **S3** | **Gaussian 전구간 정확성.** $p_X$를 Gaussian으로 바꾸면 전체 반복의 고정점이 정확한 결합 Gaussian posterior 평균과 일치 | $\le10^{-10}$ |
| **S4** | **`mode='llr'` 회귀.** `mode='llr'` + 고전 채널 추정이 **기존 고전 turbo arm(R1)과 로그 차이 0.0** | 정확히 0 |
| **S5** | **clip 집계.** $\alpha$ clip 발동 횟수를 센다. 첫 반복 외에 발동이 있으면 경고 출력 | 기록만 |
| **S6** | **복소 factor 2.** LLR → pseudo-observation → LLR 왕복이 항등 | $\le10^{-12}$ |
| **S7** | **반복 수 불리 점검.** 외부 20회 변형을 C1의 한 SNR 점, $n=64$로 돌려 16회와 비교. 20회가 뚜렷이 좋으면 **결과 파일에 기록**(설정은 바꾸지 않는다) | 기록만 |

## M — 우리 모델 (P5, `03_SPEC_ourmodel.md` §4)

> baseline 테스트가 전부 PASS한 뒤에 실행한다.

| id | 내용 | 기준 |
|---|---|---|
| **M1** | **기존 arm 동등성.** 조립기의 `M-ours-gmm32`가 `Demo/`의 기존 동일 arm과 동일 시드에서 **로그 차이 0.0** | 정확히 0 |
| **M2** | **Module H 단독 차이 증명.** `M-ours-G`(Module H만 Gaussian으로 되돌린 것)가 **`R2-ours-G`와 로그 차이 0.0** | 정확히 0 |
| **M3** | **GMM 적합 항등식.** $\sum_k\pi_k\mathbf C_k$ = 표본 공분산 | $\le10^{-12}$ |
| **M4** | **config 정합.** config 덤프가 `03_SPEC_ourmodel.md` §1.1 표와 필드 단위로 일치(자동 대조) | 전 항목 일치 |

**M2가 이 실험 전체에서 가장 중요한 테스트다.** 논문 headline 격차가 Module H의 몫이라는 주장의 유일한 증거다.
- **M2 FAIL** → 우리 모델 arm 전체를 `FAILED-VERIFICATION`으로 표시하고 **baseline만으로 마무리한다.** 억지로 맞추지 않는다.
- `Demo/`에서 기존 arm을 못 찾아 정의로부터 구성한 경우(`03_SPEC_ourmodel.md` §3) → M1은 `UNVERIFIED`로 기록한다. SKIP이 아니다.

## 공통

| id | 내용 |
|---|---|
| **C1** | 두 신규 arm이 $n=2$ 스모크에서 예외 없이 돌고, 반환 필드의 **키·형상이 기존 arm과 동일** |
| **C2** | 시드 고정 시 두 번 실행 결과가 비트 단위로 동일 |
| **C3** | `Demo/t2_route_a.py`, `t2_trellis.py`, `t2_gmm.py`의 **파일 해시가 작업 전후로 변하지 않았음** (git status로도 확인) |
| **C6** | 결과 파일 헤더에 device(CPU/GPU)·정밀도·(GPU면) 모델명이 적혀 있는지 |
| **C5** | 우리 모델 arm이 **기존 클래스 기본값에 의존하지 않고** 전 설정을 명시적으로 받았는지 (config 덤프에 빈 필드 없음) |
| **C4** | 셀 안에서 전 arm이 **동일한 채널·잡음 실현**을 받는지 확인(paired 보장). 서로 다른 arm의 $\mathbf H$ 해시가 같아야 함 |

---

## L — Lemma 재현 (P4, `03_SPEC_ourmodel.md` §6)

| id | 내용 | 기준 |
|---|---|---|
| **L1** | `Demo/exp_0915_bcjr_score_check.py`를 **수정 없이** 재실행했을 때 $(133,171)_8$의 `max|tanh−E|`와 Tweedie 유한차분 오차가 기록값과 같은 자릿수 | $\le10^{-14}$ / $\le10^{-9}$ |
| **L2** | 복소 규약 확인: $L_c=4/\sigma_c^2$가 정확하고 $2/\sigma_c^2$는 틀린다는 출력이 재현됨 | 재현 |

L2는 이 폴더의 복소 구현 전반(특히 `02_SPEC_baselines.md` §0)에 대한 경고 역할을 한다. 어긋나면 복소 규약 구현을 먼저 의심해라.

## D — Diffusion 품질 게이트 (A5, `04_SPEC_diffusion.md` §5)

GA·GB·GC·GD는 그 문서가 정본이다. 여기서는 러너가 지켜야 할 것만 적는다.

| id | 내용 | 기준 |
|---|---|---|
| **D0** | $\sigma_t$ 격자가 **측정으로** 정해졌는지(`sigma_grid.txt` 존재, 근거 분포 포함) | 존재 |
| **D1t** | 학습·검증 분할이 전 사다리 칸에서 **동일**한지(해시 대조) | 일치 |
| **D2t** | 학습 데이터가 GMM이 받은 것과 **동일 $N_{\rm train}$·동일 표본**인지 | 일치 |
| **D3t** | `LADDER.md`에 모든 시도가 기록돼 있는지(시도 수 = 로그 행 수) | 일치 |
| **D4t** | **학습이 실제로 실행됐는지.** `conf/ckpt/`에 L1·L2·L3 체크포인트 파일이 실재하고, 각각 로드해서 forward가 도는지 | 파일 존재 + 로드 성공 |
| **D5t** | **device 기록.** `torch.cuda.is_available()` 결과, 학습에 쓴 device, epoch당 시간, 총 학습 wall-clock이 STATUS와 `LADDER.md`에 있는지 | 존재 |
| **D6t** | **학습이 충분했는지.** 각 칸이 조기 종료 조건 또는 최소 200 epoch에 도달했는지(`ABORTED`가 아닌지) | 전 칸 확인 |

## T — D2 testbed 검증 (B1, `05_SPEC_testbed_D2.md` §2)

T2a~T2e는 그 문서가 정본이다. **T2d(조건부 Gaussian 파괴의 직접 증거)가 FAIL이면 Stage B를 진행하지 않는다.**

## G — GPU 경로 (GPU를 실제로 쓸 때만, `01_RULES.md` §9)

| id | 내용 | 기준 |
|---|---|---|
| **G1** | **CPU 동등성.** 같은 시드에서 GPU 경로와 CPU 경로의 출력이 일치 | `complex128` → $\le10^{-10}$ / `complex64` → $\le10^{-5}$ **이고** 블록별 성공·실패 판정 100% 일치 |
| **G2** | **결정론.** GPU 경로에서 두 번 실행이 비트 단위로 동일 (테스트 C2의 GPU판) | 정확히 일치 |

**G1의 판정 일치가 깨지면 GPU 경로를 폐기하고 CPU로 돌아간다.** 속도를 위해 판정을 바꾸지 않는다.
GPU를 쓰지 않았으면 이 두 항목은 `N/A`로 기록한다(SKIP이 아니라 N/A).

## 테스트 출력 형식

`conf/results/tests.txt`에 다음 형식으로:

```
id | PASS/FAIL | 잔차 | 기준 | 한 줄 설명
```

맨 아래에 요약 한 줄: `PASS n/m, FAILED: [id...]`.
FAIL이 있으면 `conf/STATUS.md`와 `conf/BLOCKERS.md`에도 반영한다.
