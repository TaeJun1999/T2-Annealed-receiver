# PAPER_MATERIALS — extended abstract 작성용 자료 색인

> 이 파일은 **논문 원고가 아니다.** 인용 가능한 모든 수치와 그 출처 파일을 매핑한 색인이다.
> 모든 수치는 `conf/results/` 의 파일에서 그대로 복사한 것이고, 각 항목에 출처를 적었다.
> 실행 재현: `conf/code/runner.py` 의 서브커맨드 (tests/run/lemma/sigma/train/gate/testbed/fit/analysis).

---

## 0. 한 문단 요약 (사실만)

미지의 bilinear MIMO 채널에서 검출·복호·채널추정을 함께 도는 EP/VAMP 형 수신기에, 채널 prior 를
모듈(Module H)로 갈아끼울 수 있게 만들었다. 데이터로 적합한 Kronecker 구조 GMM 을 Module H 로 쓰면
2차 모멘트(표본공분산 Gaussian) prior 대비 **+0.49 dB** (SNR@BLER 0.1, 90% CI [0.30, 0.72], 3/3 결정점
유의, pooled p = 1.4e-29) 를 얻는다. 같은 인터페이스에 **학습된 diffusion score** 를 넣는 분기는 사전
등록 품질 게이트를 **959 시도 전부 미달**했고, 부족분은 아키텍처가 아니라 **표본 수** 로 정량화된다
(GC ~ N^-0.474, 기준 교차 N ~ 5.3e4, GMM 과 동일한 예산 N = 1e4 에서는 1.62배 부족).

---

## 1. 시스템 설정 — 출처 `results/tables_D2.txt` 헤더

```
# date        : 2026-09-21 10:08:20 KST
# git commit  : 5e2e77a
# versions    : python 3.12.14  numpy 2.5.2  scipy 1.18.1  torch 2.14.0+cu130 (cuda_available=True)
# device      : CPU (192 cores) | dtype: complex128 / float64 | deterministic: yes (fixed seeds, no GPU in the receiver)
# testbed     : D2
# seed rule   : default_rng([20260926, TBID[testbed], PID[prior], Nr, T, Tp, int(snr)+100])  (trials of a point = ONE stream)
# code        : rate-1/2 conv (133,171)_8 nu=6 terminated, QPSK, outer iterations = 16 for EVERY arm
# Demo/ hashes: t2_route_a.py=95a5408901ec125c  t2_trellis.py=31cd0ee9c68e972b  t2_gmm.py=d064e58c7510c769
# arm list with per-arm notes (06_SPEC §5):
```

- 셀 C2 (headline): 8x4, T = 16, Tp = 4, K = 42 정보비트, SNR -3..+15 dB 7점
- 전 arm 동일: 외부 반복 16, 동일 파일럿 행렬, **셀 안에서 동일 채널·잡음 실현 (paired)**
- 수신기 전 arm CPU complex128 — GPU 미사용이므로 테스트 G1/G2 는 N/A

## 2. Testbed

| | D1 (계측기) | D2 (주장) |
|---|---|---|
| 채널 prior | 32x32 격자 GMM 으로 **정의** (참 score 폐형식 존재) | sparse specular mmWave 다중경로 |
| 용도 | 품질 게이트 GA~GD 측정 | **논문의 주장** |
| 경고 | 순환 testbed — GMM 이 correctly specified. 학습 prior 주장 불가 | 조건부 Gaussian 파괴 (T2d) |

D2 채널 (`conf/code/d2.py`, 사양 `conf/05_SPEC_testbed_D2.md`):
경로 수 L ~ Unif{3..8}, 지수 전력분포 tau = 2, **경로 이득 크기 |alpha_l| 결정적**, 위상만 균등,
AoA/AoD 연속 균등 (S2 = 물리각 +-60도 표준 섹터), 반파장 ULA, E||H||_F^2 = Nr*Nt.

## 3. 검증 — 출처 `results/tests.txt`, `results/testbed_D2.txt`, `results/lemma.txt`

```
PASS 35/35, FAILED: []   (N/A: ['S4'], RECORD: ['S5', 'S7', 'T2b', 'T2c', 'T2e'])
```

인용할 핵심 잔차:

- `M1    | PASS        |     0.000e+00 | exactly 0               | assembler M-ours-gmm32 == Demo/exp_0925 'Hgmm-K32' (b* = kron, legacy b* = Hgmm-kron)`
- `M2    | PASS        |     0.000e+00 | exactly 0               | M-ours-G (Module H -> Gaussian) == R2-ours-G: the headline gap is Module H's alone`
- `L1    | PASS        |     6.890e-15 | tanh <= 1e-14 and FD <= 1e-9 | (133,171)_8: max|tanh(L/2) - E[x|x~]| = 2.33e-15, max Tweedie FD error = 6.89e-10 (recorded in 03_SPEC §6: 2.3e-15 / 6.9e`
- `L2    | PASS        |     2.550e-15 | Lc=4 <= 1e-12 and Lc=2 > 1e-3 | L_c = 4/sigma_c^2 error 2.55e-15 (exact); L_c = 2/sigma_c^2 error up to 4.95e-01 (wrong)`
- `T2a   | PASS        |     6.735e-05 | rel err <= 1e-3         | E||H||_F^2 = 31.997845 vs Nr*Nt = 32 over n=100000; analytic C_ens=kron(Rt^T,Rr) vs MC: max|dC|/cbar = 7.265e-03 = 2.3 MC s.e.`
- `T2d   | PASS        |    -2.518e-01 | max CI_hi - 2 < 0       | 8 angle sets x 20000 phase draws, 99.9% bootstrap CI (1000 resamples over realisations). Gaussian value = 2 EXACTLY. L=3: meas`
- `T2dm  | PASS        |     5.010e-03 | |meas - pred| <= 1e-2   | T2d MECHANISM: measured fourth-moment ratio vs the analytic 2 - sum_l |u_l|^4/(sum_l |u_l|^2)^2 = 2 - sum_l p_l^2 (unit-norm s`

**M2 = 정확히 0.0 이 이 논문의 귀속 논증이다** — Module H 만 Gaussian 으로 되돌리면 R2-ours-G 와
로그가 비트 단위로 같다. 따라서 아래 모든 격차는 Module H 하나의 몫이다.

## 4. 주 결과 — D2 셀 C2 (headline), 출처 `results/tables_D2.txt` TABLE B

```
R1-turbo -> R2-ours-G        [decision-point anchor arm: R1-turbo]
    sign test @16: +0 dB 291:1 p=7.4e-86  +3 dB 32:0 p=4.7e-10  +6 dB 11:1 p=0.0063   pooled 334:2 p=8.1e-97
    power guard: 3 decision points, 3 with >= 6 discordant pairs -> POWERED
    two-sided sign test at p < .05: second arm fewer failures at 3/3 points, first arm fewer failures at 0/3 points -> significant
    SNR@0.1 gap (R1-turbo minus R2-ours-G): +2.77 dB  [90% paired bootstrap +2.13, +3.42; censored replicates 0%]

R2-ours-G -> M-ours-bstar        [decision-point anchor arm: R2-ours-G]
    sign test @16: -3 dB 274:79 p=2.5e-26  +0 dB 86:44 p=0.00029  +3 dB 14:3 p=0.013   pooled 374:126 p=1.4e-29
    power guard: 3 decision points, 3 with >= 6 discordant pairs -> POWERED
    two-sided sign test at p < .05: second arm fewer failures at 3/3 points, first arm fewer failures at 0/3 points -> significant
    SNR@0.1 gap (R2-ours-G minus M-ours-bstar): +0.49 dB  [90% paired bootstrap +0.30, +0.72; censored replicates 0%]

R2-ours-G -> M-ours-gmm32        [decision-point anchor arm: R2-ours-G]
    sign test @16: -3 dB 218:84 p=7e-15  +0 dB 83:50 p=0.0053  +3 dB 8:5 p=0.58   pooled 309:139 p=6.3e-16
    power guard: 3 decision points, 3 with >= 6 discordant pairs -> POWERED
    two-sided sign test at p < .05: second arm fewer failures at 2/3 points, first arm fewer failures at 0/3 points -> significant
    SNR@0.1 gap (R2-ours-G minus M-ours-gmm32): +0.36 dB  [90% paired bootstrap +0.18, +0.58; censored replicates 0%]

R2-ours-G -> R4-scvamp        [decision-point anchor arm: R2-ours-G]
    sign test @16: -3 dB 5:733 p=2.5e-210  +0 dB 5:521 p=3e-147  +3 dB 1:81 p=3.4e-23   pooled 11:1335 p=0
    power guard: 3 decision points, 3 with >= 6 discordant pairs -> POWERED
    two-sided sign test at p < .05: second arm fewer failures at 0/3 points, first arm fewer failures at 3/3 points -> significant
    SNR@0.1 gap (R2-ours-G minus R4-scvamp): -5.61 dB  [90% paired bootstrap -6.76, -4.81; censored replicates 0%]

R4-llr -> R4-scvamp        [decision-point anchor arm: R4-llr]
    sign test @16: +9 dB 141:8 p=1.5e-32  +12 dB 102:9 p=4.3e-21  +15 dB 92:2 p=4.5e-25   pooled 335:19 p=7.8e-76
    power guard: 3 decision points, 3 with >= 6 discordant pairs -> POWERED
    two-sided sign test at p < .05: second arm fewer failures at 3/3 points, first arm fewer failures at 0/3 points -> significant
    SNR@0.1 gap (R4-llr minus R4-scvamp): >= +9.40 dB (R4-llr never reaches 0.1 on the grid)

R2-ours-G -> R3-bigamp        [decision-point anchor arm: R2-ours-G]
    sign test @16: -3 dB 59:609 p=4.3e-116  +0 dB 30:314 p=7.9e-61  +3 dB 3:33 p=2.3e-07   pooled 92:956 p=7.2e-182
    power guard: 3 decision points, 3 with >= 6 discordant pairs -> POWERED
    two-sided sign test at p < .05: second arm fewer failures at 0/3 points, first arm fewer failures at 3/3 points -> significant
    SNR@0.1 gap (R2-ours-G minus R3-bigamp): -2.66 dB  [90% paired bootstrap -3.37, -2.06; censored replicates 0%]

```

- b* = **kron K=512**, 선택은 **검증 우도만** (BLER 미사용). 출처 `results/gmm_fit_D2.txt`
- headline 2점 (-3, 0 dB) 은 **n = 2560**, 나머지 n = 640. 출처: 위 표 `n per SNR` 행

## 5. 이득이 나타나는 조건 — 출처 `results/tables_D2.txt` 셀 C1 / C5 / C2

Tp = 2 / 3 / 4 에 대해 BLER@16 (SNR -3 ... +15 dB):

```
--- C1 (Tp=2)
  R2-ours-G        0.789 3.5e-01 6.36e-01  0.572 2.6e-01 4.19e-01  0.472 2.2e-01 5.85e-02  0.418 2.0e-01 2.52e-02  0.412 2.0e-01 1.26e-02  0.405 1.9e-01 6.30e-03  0.408 1.9e-01 3.06e-03
  M-ours-bstar     0.778 3.6e-01 6.43e-01  0.534 2.5e-01 2.68e-01  0.442 2.1e-01 4.27e-02  0.404 1.9e-01 2.15e-02  0.409 1.9e-01 1.14e-02  0.414 2.0e-01 5.75e-03  0.388 1.9e-01 2.91e-03
  R5-genie           0.039 1.0e-02 nan       0.013 4.7e-03 nan       0.005 1.8e-03 nan       0.002 8.7e-04 nan       0.002 5.8e-04 nan       0.000 0.0e+00 nan      0.000 0.0e+00 nan
--- C5 (Tp=3)
  R2-ours-G        0.623 2.7e-01 3.67e-01  0.341 1.5e-01 8.16e-02  0.214 9.6e-02 3.98e-02  0.206 9.7e-02 2.04e-02  0.144 6.5e-02 9.60e-03  0.150 7.3e-02 5.00e-03  0.116 5.3e-02 2.41e-03
  M-ours-bstar     0.559 2.4e-01 2.10e-01  0.283 1.2e-01 6.36e-02  0.183 8.4e-02 3.28e-02  0.184 8.7e-02 1.74e-02  0.148 6.6e-02 8.72e-03  0.147 6.8e-02 4.49e-03  0.159 7.4e-02 2.28e-03
  R5-genie           0.034 1.1e-02 nan       0.014 3.5e-03 nan       0.006 1.8e-03 nan       0.006 2.5e-03 nan       0.000 0.0e+00 nan      0.000 0.0e+00 nan      0.000 0.0e+00 nan
--- C2 (Tp=4)
  R2-ours-G        0.329 1.2e-01 1.37e-01  0.100 3.8e-02 6.81e-02  0.044 1.7e-02 3.48e-02  0.027 1.1e-02 1.84e-02  0.009 4.5e-03 9.09e-03  0.009 3.6e-03 4.47e-03  0.006 2.6e-03 2.31e-03
  M-ours-bstar     0.252 9.6e-02 1.04e-01  0.083 3.1e-02 5.33e-02  0.027 8.5e-03 2.85e-02  0.013 4.5e-03 1.56e-02  0.006 2.2e-03 7.84e-03  0.009 4.3e-03 4.02e-03  0.003 1.7e-03 2.10e-03
  R5-genie           0.034 1.1e-02 nan       0.010 3.8e-03 nan       0.005 1.7e-03 nan       0.003 7.4e-04 nan       0.002 8.9e-04 nan       0.000 0.0e+00 nan      0.002 6.3e-04 nan
```

읽는 법: Module H 이득은 **채널 추정이 부정확한 저SNR 에서 나타나고 고SNR 에서 사라지거나 역전**된다
(C5 +15 dB: R2 0.116 vs bstar 0.159, sign 36:64, p = 0.0066 으로 R2 우세).
C1 (Tp=2) 에서 어떤 prior 도 작동하지 않는 것은 사전 등록 진단 **T2c** 가 예측한 대로 첫 패스가
무정보이기 때문이다 (NMSE_inf = 0.466 vs 1 - Tp/Nt = 0.500). 출처 `results/testbed_D2.txt` T2c 행.

## 6. D1 결과 (맥락용, 주장 불가) — 출처 `results/tables_D1.txt`

```
R1-turbo -> R2-ours-G        [decision-point anchor arm: R1-turbo]
    sign test @16: +9 dB 52:0 p=4.4e-16  +12 dB 28:1 p=1.1e-07  +15 dB 24:1 p=1.5e-06   pooled 104:2 p=1.4e-28
    power guard: 3 decision points, 3 with >= 6 discordant pairs -> POWERED
    two-sided sign test at p < .05: second arm fewer failures at 3/3 points, first arm fewer failures at 0/3 points -> significant
    SNR@0.1 gap (R1-turbo minus R2-ours-G): +5.03 dB  [90% paired bootstrap +3.74, +7.38; censored replicates 8%]

R2-ours-G -> M-ours-bstar        [decision-point anchor arm: R2-ours-G]
    sign test @16: +6 dB 48:14 p=1.7e-05  +9 dB 37:11 p=0.00022  +15 dB 36:8 p=2.5e-05   pooled 121:33 p=5.3e-13
    power guard: 3 decision points, 3 with >= 6 discordant pairs -> POWERED
    two-sided sign test at p < .05: second arm fewer failures at 3/3 points, first arm fewer failures at 0/3 points -> significant
    SNR@0.1 gap (R2-ours-G minus M-ours-bstar): +2.62 dB  [90% paired bootstrap +1.57, +3.64; censored replicates 0%]

M-ours-score -> R6-exactEP        [decision-point anchor arm: R6-exactEP]
    sign test @16: +0 dB 18:33 p=0.049  +3 dB 16:21 p=0.51  +6 dB 10:6 p=0.45   pooled 44:60 p=0.14
    power guard: 3 decision points, 3 with >= 6 discordant pairs -> POWERED
    two-sided sign test at p < .05: second arm fewer failures at 0/3 points, first arm fewer failures at 1/3 points -> not significant
    SNR@0.1 gap (M-ours-score minus R6-exactEP): -0.07 dB  [90% paired bootstrap -0.55, +0.39; censored replicates 0%]

```

**이 표의 숫자로 학습 prior 주장을 하면 안 된다** — 참 prior 가 격자 GMM 으로 정의되어 GMM arm 이
correctly specified 이다. 표 헤더에 경고가 박혀 있다.

`M-ours-score -> R6-exactEP` 가 유의하지 않다는 것 (p = 0.14, -0.07 dB [-0.55, +0.39]) 은 별도로 쓸모가
있다: **one-shot Tweedie + D-13 + D-14 인터페이스가 정확 mixture-EP site 대비 측정 가능한 손실이 없다**
는 뜻이고, 따라서 학습 분기의 실패는 인터페이스 탓이 아니다.

## 7. 학습 diffusion prior — 음성 결과, 출처 `results/gate_D1.txt`, `hpo_D1.txt`, `hpo_strat_D1.txt`

사전 등록 게이트 (`conf/04_SPEC_diffusion.md` §5, 어떤 모델이 생기기 전에 동결):
GA <= 1e-6 (Tweedie 자기무결성) · GB <= +5% (denoising NMSE 초과) · GC <= 0.15 (score 상대오차)
· GD <= 0.20 (D-14 가 쓰는 Wirtinger Jacobian 의 상대 Frobenius 오차).

총 **959 시도** 전부 미달: 사전 등록 사다리 L1~L6 x 3 = 18, 확장칸(U-Net/EDM/DiT/U-ViT/ADM) 15,
Optuna TPE 724, 균등표본 196, 최종 재게이트 6.

동일 예산 N = 1e4 에서의 최선 (보고용 held-out stream 10):
**GB 0.0117 <= 0.05 통과 · GD 0.161 <= 0.20 통과 · GC 0.243 vs 0.15 미달 (1.62배)**

아키텍처 균등표본 비교 (n = 30 씩, 무작위 표집) — 출처 `results/hpo_strat_D1.txt`:

```
  arch      n     best      p25   median    worst
  --------------------------------------------------
  unet     30    1.572    2.145    3.356   10.877
  uvit     30    1.814    2.746    3.889   16.608
  dit      30    1.865    2.734    3.302   20.483
  adm      30    1.872    2.958    6.757   48.885
  conv     30    1.902    2.455    2.654 1770.612
  mlp      30    4.540    5.202    6.100   19.628
```

-> **mlp 만 명확히 열등, 나머지 5종은 구분 불가.** 즉 부족분은 아키텍처 탐색 부족이 아니다.
(주의: `hpo_D1.txt` 의 TPE 결과는 아키텍처별 시도 수가 불균등하므로 **아키텍처 우열 근거로 쓰면 안 된다**.)

## 8. 표본 복잡도 — 출처 `results/samplecx_D1.txt`

```
  N_train  epochs    val_loss         GB         GC         GD  gate_score  verdict
  ----------------------------------------------------------------------------------
     2,500     357  7.4618e-01    0.05523    0.78537    0.32425      5.2358  FAIL
    10,000     200  7.2817e-01    0.01174    0.24333    0.16081      1.6222  FAIL   <- the arm budget (01_RULES §5)
    40,000     200  7.3615e-01    0.00453    0.16651    0.10099      1.1101  FAIL
   160,000     200  7.3984e-01    0.00266    0.09986    0.07183      0.6657  PASS   <- clears all four gates

  GC scaling: a log-log fit over these four budgets gives GC ~ N^(-0.474) (R^2 = 0.9342).
  Extrapolating that fit, GC crosses the pre-registered 0.15 at N ~ 52,731; it is bracketed by
  the measured points N = 40,000 (GC 0.1665, fail) and N = 160,000 (GC 0.0999, pass), so the
  crossing is MEASURED, not only extrapolated.
```

arm 비교는 **동일 1e4 예산 고정** (01_RULES §5) 이고, 이 곡선은 GB' 와 같은 **보고 전용** 이다.
어떤 BLER 표에도 arm 으로 들어가지 않는다.

## 9. GMM 적합 — 출처 `results/gmm_fit_D2.txt`

K in {16,32,64,128,256,512} x {full, kron} x MAP shrinkage kappa x restarts, **검증 우도로만 선택**.
b* 가 격자 경계에 놓일 때마다 128 -> 256 -> 512 로 확장했다 (GMM 을 강하게 만드는 = 우리 주장에
불리한 방향). D1 대비 과적합 격차가 7~10배 증가하는 것이 testbed 가 실제로 어려워졌다는 2차 증거다.

## 10. 쓰면 안 되는 것

- **"학습된 diffusion prior 가 GMM 을 이긴다"** — 게이트 통과 arm 이 없다. `M-ours-dscore` 는 D1/D2
  양쪽 표에서 BLOCKED 로 표기돼 있다.
- **D1 표의 숫자로 prior 에 대한 주장** — 순환 testbed.
- **D2 C1 (Tp=2) 을 실패로 서술** — T2c 가 사전 진단한 무정보 영역이고, 그 자체가 체제 결과다.
- **TPE 결과로 아키텍처 우열** — 시도 수 불균등. 균등표본 표를 쓸 것.
- **testbed 선택 근거를 "GMM 에 불리해서"로 서술** — `01_RULES §5` 가 금지. 근거는 "물리적으로 표준"이고
  조건부 Gaussian 파괴는 그 물리의 귀결이며 T2d 가 직접 증거다.

## 11. 그림 — `conf/figs/` (PDF + PNG, 생성은 `code/figures.py`)

| 파일 | 내용 | 쓸 곳 |
|---|---|---|
| `F2_lemma.pdf/png` | 복호기 soft output = 정확 Tweedie score. (좌) 산점, (우) 오차 vs sigma^2 | 이론 앵커 |
| `F3_bler_D2.pdf/png` | **BLER vs SNR, D2. (a) Tp=4 headline, (b) Tp=2.** 두 패널 대비가 체제 결과를 한 장에 담는다 | **메인 그림** |
| `F3_bler_D1.pdf/png` | 같은 그림의 D1 판 (순환 testbed, 맥락용) | 부록 |
| `F4_regime_D2.pdf/png` | Module H 이득 vs SNR, Tp = 2/3/4. **90% paired bootstrap CI**, 블록오류 15개 미만 점은 축에 눈금으로 표시하고 값은 그리지 않음 | 체제 주장 |
| `F5_samplecx.pdf/png` | GB/GC/GD vs 학습 표본수 N, 게이트 선 점선. `GC ~ N^-0.47` 적합선 | **음성 결과 그림** |
| `F6_arch.pdf/png` | 아키텍처 균등표본 비교 (30회씩). 빨강 = best-of-30, 검정 = median, 초록 파선 = 전 게이트 통과선 | 아키텍처 주장 |

그림 주의사항:
- `F4` 의 고SNR 구간은 **블록 오류가 적어 비율이 추정 불가**다. 눈금만 찍힌 점을 "이득 0"으로 읽으면 안 된다.
- `F6` 에서 **초록선(1.0)에 닿은 아키텍처가 하나도 없다** — 이것이 음성 결과의 시각적 요약이다.
- `F3(b)` 의 평탄한 곡선은 실패가 아니라 T2c 가 예측한 무정보 영역이다.

## 12. 파일 지도

| 파일 | 내용 |
|---|---|
| `results/tables_D2.txt` | **주 결과.** 표 A/B/C/D, 셀 C1~C5 |
| `results/tables_D1.txt` | 계측기 결과 (순환 경고 포함) |
| `results/samplecx_D1.txt` | 표본 복잡도 곡선 |
| `results/hpo_strat_D1.txt` | 아키텍처 균등표본 비교 (**인용용**) |
| `results/hpo_D1.txt` | TPE 탐색 724 시도 (맥락용) |
| `results/gate_D1.txt` / `gate_D2.txt` | 게이트 GA~GD 수치 / GB' |
| `results/testbed_D2.txt` | T2a~T2e (+T2dm) |
| `results/gmm_fit_D2.txt` | GMM 적합표 + D1 대비 악화 |
| `results/lemma.txt` + `figs/F2_lemma.*` | F2 lemma |
| `figs/F3..F6` | 결과 그림 (PDF + PNG). 생성: `code/figures.py` |
| `results/tests.txt` | 사전 등록 테스트 35/35 |
| `LADDER.md` | 사다리 전 시도 (82행, append-only) |
| `DECISIONS.md` | 자율 판단 34건 + 근거 + 되돌리는 법 |
| `STATUS.md` | 최종 상태 · DoD 점검 |
| `raw/` | npz 1056개 (블록별 성공/실패 플래그 포함, paired 재분석 가능) |
| `code/` | 전 구현. `runner.py --help` 로 재현 |
