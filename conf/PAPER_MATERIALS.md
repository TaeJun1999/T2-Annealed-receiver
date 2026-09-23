# PAPER_MATERIALS — extended abstract 작성용 자료 색인

> 이 파일은 **논문 원고가 아니다.** 인용 가능한 모든 수치와 그 출처 파일을 매핑한 색인이다.
> 모든 수치는 `conf/results/` 의 파일에서 그대로 복사한 것이고, 각 항목에 출처를 적었다.
> 실행 재현: `conf/code/runner.py` 의 서브커맨드 (tests/run/lemma/sigma/train/gate/testbed/fit/analysis).
>
> **갱신 2026-09-22 00:40 KST — Stage C 를 포함하도록 확장했다.**
> §0~§9 는 Stage A/B (동결). §10~§16 은 Stage C (`10_SPEC_stageC.md` + 증보 §3b §3c §3d §6b §6c §9).
> §17 은 **쓰면 안 되는 것** 이며 Stage C 분을 추가했다 — **인용 전에 §17 을 먼저 읽을 것.**
> §20 은 출처를 특정하지 못한 항목이다 (누락 대신 명시).

---

## 0. 한 문단 요약 (사실만)

미지의 bilinear MIMO 채널에서 검출·복호·채널추정을 함께 도는 EP/VAMP 형 수신기에, 채널 prior 를
모듈(Module H)로 갈아끼울 수 있게 만들었다. 데이터로 적합한 Kronecker 구조 GMM 을 Module H 로 쓰면
2차 모멘트(표본공분산 Gaussian) prior 대비 **+0.49 dB** (SNR@BLER 0.1, 90% CI [0.30, 0.72], 3/3 결정점
유의, pooled p = 1.4e-29) 를 얻는다. 같은 인터페이스에 **학습된 diffusion score** 를 넣는 분기는 사전
등록 품질 게이트를 **959 시도 전부 미달**했고, 부족분은 아키텍처가 아니라 **표본 수** 로 정량화된다
(GC ~ N^-0.474, 기준 교차 N ~ 5.3e4, GMM 과 동일한 예산 N = 1e4 에서는 1.62배 부족).

**Stage C (2026-09-21 14:00 개시).** 예산을 N' = 1.6e5 로 올린 학습 score 가 D1 게이트를 **통과**했고
(GB 0.0027 · GC 0.0999 · GD 0.0718; GA 는 이 모델 계열에서 구조적 0 이므로 실질 3개 게이트),
그 체크포인트로 두 testbed 의 확증 BLER 을 n = 2560 으로 돌렸다. 결과: **사전 등록 배선(V0)은 주장
testbed D2 에서 붕괴한다** (C2 −3 dB BLER 0.593 으로 고전 터보 0.537 보다 나쁘다). 같은 체크포인트·같은
예산에서 **D-14 행렬 site 를 수리하면(V1, 대칭-PSD 투영) BLER 0.145 로 최고 arm 이 된다.** 기전은 학습
야코비안의 **고유값 부호**이고, D1 과 D2 를 가르는 것은 추정기 품질이 아니라 **참 스펙트럼의 여유
(margin)** 다. 게이트 통과가 수신기 사용 가능성을 보증하지 않는다는 것이 이 실행의 실측 결과다.

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

인용할 정확한 양:

| 양 | 값 | 출처 행 |
|---|---|---|
| GC 스케일링 지수 | `GC ~ N^(-0.474)`, log-log 적합 R^2 = 0.9342, 4개 예산 | `samplecx_D1.txt` "GC scaling" 문단 |
| 외삽 교차점 | GC 가 사전 등록 0.15 를 지나는 지점 **N ~ 52,731** | 같은 문단 |
| 실측 괄호 | N = 40,000 GC 0.1665 FAIL · N = 160,000 GC 0.0999 PASS → **교차는 실측으로 괄호가 쳐져 있다 (외삽 전용이 아니다)** | 같은 문단 |
| 1e4 예산에서 부족한 것 | GB 0.0117 (기준 0.05) 통과, GD 0.161 (기준 0.20) 통과, **GC 만 1.62배 부족** | `samplecx_D1.txt` READING |

arm 비교는 **동일 1e4 예산 고정** (01_RULES §5) 이고, 이 곡선은 GB' 와 같은 **보고 전용** 이다.
어떤 BLER 표에도 arm 으로 들어가지 않는다. `samplecx_D1.txt` 스스로 그렇게 못박고 있다:
"This does NOT license a learned-prior arm at any budget: M-ours-dscore stays BLOCKED on both testbeds."

**Stage C 와의 연결 (§11).** 위 표의 `N_train = 160,000  PASS` 행이 바로 Stage C 가 arm 으로 올린
D1 체크포인트 `ckpt/sx_N160000_D1.pt` 이다. 즉 Stage C 는 "GC 는 N ~ 5e4 에서 넘는다"는 이 곡선의
예측을 실제로 집행한 것이고, `LADDER_C.md` 의 PASS 행이 그 집행 기록이다.

## 9. GMM 적합 — 출처 `results/gmm_fit_D2.txt`

K in {16,32,64,128,256,512} x {full, kron} x MAP shrinkage kappa x restarts, **검증 우도로만 선택**.
b* 가 격자 경계에 놓일 때마다 128 -> 256 -> 512 로 확장했다 (GMM 을 강하게 만드는 = 우리 주장에
불리한 방향). D1 대비 과적합 격차가 7~10배 증가하는 것이 testbed 가 실제로 어려워졌다는 2차 증거다.

---

# Stage C (§10 ~ §16) — `10_SPEC_stageC.md` + 증보 §3b §3c §3d §6b §6c §9

## 10. Stage C 범위와 동결 상태 — 출처 `STATUS.md` "■ Stage C 요약", `DECISIONS.md`

- **Stage A/B 의 사전 등록 판정은 전부 동결이다.** `tables_D1.txt`, `tables_D2.txt`, `gate_D1.txt`,
  `LADDER.md` 는 내용 기준 불변이며, 사전 등록 arm `M-ours-dscore` 는 **양 testbed 본 표에서 BLOCKED
  유지**다. Stage C 산출물은 전부 `*_C` 접미사 파일이고 본 표와 합치지 않는다.
- Stage C arm 정의 (출처: `results/tables_D2_C.txt` 헤더, 10_SPEC §3b/§3c):

| arm | 정의 |
|---|---|
| `M-ours-dscore-C-V0` | **PRIMARY.** 학습 prior @ N', 사전 등록 D-14 **행렬** site, 배선 무변경 |
| `M-ours-dscore-C-V1` | V0 + (F1) D-14 site 의 **대칭-PSD 투영** (`ScorePrior(psd_project=True)`) |
| `M-ours-dscore-C-V4` | D-14 행렬 site 를 D-13 **belief 스칼라화**로 교체 (`hsite=scalar, scal=belief`). POST-HOC 등록 (10_SPEC §3c) |
| `M-ours-dscore-C-V4b` | V4 와 같되 `scal=site`. §3c 에 등록됐다가 누락, 감사 지적 후 2026-09-21 배선 |
| `M-ours-bstar-scalar` | **MANDATORY 대조군** (§3c) — b* GMM 을 V4 의 **동일 배선**에 통과. 스칼라화 이득이 prior 가 아니라 site 의 몫인지 가른다 |
| `M-ours-score` | D1 전용 **ORACLE** — 참 prior 의 정확 score. 학습 prior 가 아니며 이 arm 에서 학습 prior 주장 불가 |

- **감사 이력.** 2026-09-21 18:20 적대적 감사(5인 + 심판)에서 실제 결함 **29건 (BLOCKER 3건)** 이
  나왔고 STATUS 요약이 전면 재작성됐다. 철회된 주장 목록은 **§17.2** 에 있으며, 인용 전에 반드시
  읽어야 한다. 감사가 깨끗하다고 확인한 것: 절대 규칙 위반 0건, 사전 등록 4개 파일 내용 불변,
  게이트 임계 불변, `LADDER_C.md` append-only, BLER 로 선택한 것 없음, 전사 수치는 정확.
- **내 구현 결함 2건** (감사가 찾아 같은 시각 수정, `STATUS.md` 감사 정정 절):
  (a) `DIVERGE_TRAIN` 이 NaN 을 못 잡았다 — `vl > 3*best` 는 NaN 에서 항상 False. `(vl != vl) or (...)` 로 수정.
  (b) (F3) Module H 발산 가드가 §3 에 등록됐으나 미구현. `code/guard_report.py` 로 구현 (탐지·분류 전용,
      `DIVERGE_NMSE = 10.0` 을 `code/bigamp.py` 에서 재사용, 어떤 arm 의 궤적도 바꾸지 않음).

## 11. Stage C 게이트 — 출처 `results/gate_D1_C.txt`, `LADDER_C.md`

게이트 임계는 Stage A/B 와 **동일하고 변경되지 않았다** (§7 참조): GA <= 1e-6, GB <= 0.05,
GC <= 0.15, GD <= 0.20. GD 는 **full Wirtinger matrix 의 상대 Frobenius 오차**이고 `GD_trace`
(tr(J)/N 의 상대오차) 는 **보고만 하고 게이트가 아니다** (`DECISIONS.md` 2026-09-20 12:35,
어떤 체크포인트가 게이트를 받기 **전에** 고정).

### 11.1 GA 는 구조적 0 — PASS 는 **네 게이트가 아니라 세 게이트**에 달려 있다

`results/gate_D1_C.txt` 가 표 위에 직접 적고 있는 문장 (그대로 인용):

```
GA -- STRUCTURAL ZERO.  READ THIS BEFORE READING ANY GA NUMBER BELOW.
GA is identically zero by construction for this model family; it guards score-path vs x0-path
inconsistency only, and PASS therefore rests on GB/GC/GD.
```

같은 문장이 `LADDER_C.md` 의 PASS 행 끝에도 붙어 있다. **따라서 "네 게이트를 전부 통과했다" 로 쓰면
안 되고, "실질 세 게이트(GB·GC·GD)를 통과했다 · GA 는 구조상 0" 으로 쓴다.**
(이것은 감사 정정 8번 항목이다 — §17.2)

### 11.2 Stage C 가 arm 으로 올린 체크포인트 — PASS

출처 `LADDER_C.md` `[2026-09-21 14:12 KST] SX160000 | a1`, 체크포인트 `ckpt/sx_N160000_D1.pt`:

| 게이트 | 값 | 기준 | 판정 |
|---|---|---|---|
| GA | 9.879e-16 | <= 1e-6 | PASS (**구조적 0**) |
| GB | 2.659e-03 (= +0.27%) | <= 0.05 | PASS |
| GC | 9.986e-02 | <= 0.15 | PASS |
| GD (full-matrix `J_rel_fro`) | 7.183e-02 | <= 0.20 | PASS |
| `GD_trace` | 7.462e-03 | — | **보고만, 게이트 아님** |
| **판정** | | | **PASS** |

측정 조건: `n_eval = 512` held-out (`common.train_rng` stream 10), `n_jac = 64`, 8x4, prior S,
D1 val loss 7.398444e-01. GB/GC/GD 는 `results/samplecx_D1.txt` 의 `N_train = 160,000` 행과 같은 값이다 (§8).

### 11.3 V2 (에너지 매개화) — 게이트 FAIL, **arm 이 아니다**

출처 `results/gate_D1_C.txt` (이 파일이 담고 있는 체크포인트는 **이것 하나**다:
`# checkpoints : 1 found under /home/HTJ/t2/conf/ckpt_C (filter: ckpt=ckpt/sx_V2_N160000_D1_a3.pt)`)
및 `LADDER_C.md` `[2026-09-21 22:24 KST] D1V2160000 | a3`:

| 게이트 | V0 `sx_N160000_D1` | **V2 `sx_V2_N160000_D1_a3`** |
|---|---|---|
| D1 val loss | 7.398444e-01 | 7.398676e-01 |
| GA | 9.879e-16 PASS | 9.71161e-16 PASS |
| GB | 2.659e-03 PASS | 4.54217e-03 PASS |
| **GC (<= 0.15)** | **9.986e-02 PASS** | **1.67378e-01 FAIL** (11.6% 초과) |
| GD | 7.183e-02 PASS | 8.14335e-02 PASS |
| `GD_trace` | 7.462e-03 | 1.59462e-02 |
| **판정** | **PASS** | **FAIL** |

V2 hp: `{'arch':'dit','param':'vp','domain':'angle','lr':7.46015350530356e-04,'ema':0.999,'batch':256,
'emb':256,'width':64,'depth':6,'heads':8,'patch':1,'head':'energy'}`.

이 대비에서 인용 가능한 **두 가지**:

1. **DSM 검증손실은 GC 를 예측하지 못한다.** D1 val loss 는 7.398444e-01 대 7.398676e-01 (**0.003% 차**)
   인데 GC 는 0.0999 대 0.1674 (**68% 차**)다. 사전 등록 게이트를 검증손실로 대체할 수 없다는 직접 근거.
2. **매개화와 학습률이 교란돼 있다 — V2 의 결론으로 확정하지 않는다.** V2 의 D1 쌍둥이는 동결 lr 에서
   두 번 발산해 §3d 폴백의 **lr/3** 으로 학습됐다. GC 실패가 에너지 매개화 탓인지 낮아진 lr 탓인지
   이 실험은 가르지 못한다. **동결 lr 로 완주한 V2 D1 실행은 존재하지 않는다.** 사다리 3시행이
   소진돼(a1 DIVERGED, a2 DIVERGED, a3 완료 후 FAIL) 교란된 채로 보고한다.

### 11.4 V3 (야코비안 정칙화 λ=1.0) — 게이트 없음

`LADDER_C.md`: D2 a1 DIVERGED (`STOPPED BY DIVERGE_TRAIN` @35, best val 6.919234e-01 @27),
D1 a1 (`[2026-09-22 00:22 KST] D1V3160000 | a1`) DIVERGED (train 2.010e+00 / val 7.658e-01, UNGATED).
D2 a2 (`[2026-09-21 20:08 KST] D2SX160000 | a1 | V3 lambda=1.0`) 는 200 ep 완주했으나
**D2 에는 참 score 가 없어 UNGATED** 다. λ = 1.0 은 §3b 가 튜닝을 금지했고 바꾸지 않았다.
**어떤 V3 행도 게이트 PASS 가 아니고 어떤 BLER 표에도 arm 으로 들어가 있지 않다.**

## 12. 야코비안 스펙트럼 — 출처 `results/jac_spectrum.txt` (본표 + 증보 3건)

측정: `code/jac_spectrum.py`, 격자점당 held-out n = 48, 샘플당 고유값 64개, `sym(J_r)` 기준.
`J_r = dm_real/dx` 는 참 사후평균 denoiser 에 대해 `Cov(h|q)/sigma^2` 이므로 **대칭 PSD 여야 한다.**

### 12.1 본표 (2026-09-21 16:55) — 두 개의 라벨 정정을 달고 읽어야 한다

```
                    |         k=0  sigma .033        |         k=6  sigma .092        |         k=12 sigma .256        |         k=18 sigma .713
model               |   n_neg  n<0.01   25%tl   lmin |   n_neg  n<0.01   25%tl   lmin |   n_neg  n<0.01   25%tl   lmin |   n_neg  n<0.01   25%tl   lmin
D1 N=1.6e5  learned |     0.0     0.0   0.979  +0.94 |     0.0     0.0   0.866  +0.68 |     0.0     0.0   0.470  +0.22 |     0.0     0.0   0.118 +0.031
D1 N=1.6e5  EXACT   |     0.0     0.0   0.980  +0.92 |     0.0     0.0   0.867  +0.62 |     0.0     0.0   0.471  +0.21 |     0.0     0.0   0.117 +0.039
D2 N=1e4    learned |     8.0     9.3   0.069  -0.20 |    10.6    12.4   0.028  -0.25 |    11.2    13.7   0.018  -0.27 |     7.8    10.9   0.022  -0.12
D2 N=1.6e5  learned |    10.3    12.5   0.028  -0.20 |    17.0    19.8  -0.003  -0.28 |    14.1    17.6   0.005  -0.63 |     0.7     1.6   0.051 -0.045
D2 both     FITTED  |     0.0     0.1   0.948 +4e-03 |     0.0     2.5   0.665 +6e-04 |     0.0     4.5   0.203 +8e-05 |     0.0     0.6   0.092 +5e-03
```

본표에 파일 스스로 박아 둔 정정 **2건** (둘 다 인용 시 함께 옮겨야 한다):

- `[CORRECTED 18:40]` 컬럼 라벨이 `n<0.1` 이었으나 실제로는 로그의 **`n<0.01`** 이다. 진짜 `n<0.1`
  값은 훨씬 크다 — 예: D2 N=1.6e5 k=18 은 1.6 이 아니라 **38.08 / 64**.
- `[CORRECTED 18:40]` D1 의 `EXACT` 행은 **참 prior 가 아니다.** `arms.gmm_selection()` 이 돌려준
  **N_TRAIN=10000 EM 적합본(K=32 kron)** 이었다. D1 의 참 prior 는
  `t2_gmm.angle_grid_prior(S, 8, 4, rho_c=0.7, KG=32)`, 32x32 = **1024 성분** 격자 혼합이며 여기서
  쓰이지 않았다. → 재측정이 §12.2.
- D2 의 `FITTED` 행도 정답이 아니다 — D2 에 적합한 512 성분 Kronecker GMM 이며,
  **D2 에는 폐형식 참 score 가 없다** (`05_SPEC §3`).
- **D2 N=1.6e5 행은 세션 임시 디렉토리 스냅샷** (epoch 240) 이고 18:20 감사가 재현 불가로 표시했다.
  재현 가능한 판은 §12.3.

### 12.2 ADDENDUM 2026-09-21 21:55 — D1 을 **참 prior** 기준으로 재측정 (철회의 대체물)

**철회된 주장:** "D1 에서 학습 야코비안이 정확값과 **세 자리 유효숫자까지** 일치한다."
철회 이유: 기준선이 참 prior 가 아니라 EM 적합본이었다. (감사 정정 4번 — §17.2)

재측정 (`logs/jacspec_D1_true.log`, 참 prior + 적합본을 **둘 다** 놓고, n = 48, 고유값 64개):

```
  model                      k=0 s=.0329        k=6 s=.0899        k=12 s=.2452       k=18 s=.6690
  learned  lmin / 25%tl / lmax   .9407/.9789/1.012  .6765/.8664/1.073  .2232/.4702/1.190  .0308/.1184/1.317
  TRUE     lmin / 25%tl / lmax   .9450/.9798/1.019  .6978/.8670/1.096  .2369/.4699/1.162  .0403/.1163/1.350
  FITTED   lmin / 25%tl / lmax   .9209/.9797/1.051  .6195/.8666/1.219  .2142/.4714/1.406  .0392/.1172/1.290

  n_neg = 0 for ALL THREE at ALL FOUR grid points.
```

참 prior 대비 상대오차 (%), learned / fitted:

```
  quantity   sigma .0329      .0899       .2452       .6690      learned closer at
  lmin       0.46 / 2.55   3.05 /11.22   5.78 / 9.58  23.47/ 2.63    3 of 4 (5.6x, 3.7x, 1.7x)
  25%tile    0.09 / 0.01   0.07 / 0.05   0.06 / 0.32   1.81/ 0.77    1 of 4 (both < 2% throughout)
  lmax       0.69 / 3.14   2.10 /11.22   2.41 /21.00   2.44/ 4.44    **4 of 4** (1.8x .. 8.7x)
```

**철회된 문장 자리에 쓸 수 있는 문장 (파일이 직접 적은 그대로):** D1 에서 학습 score 의 야코비안은
**어디서나 PSD** 이고, 스펙트럼 **몸통**(25th percentile)에서는 적합 혼합과 비슷하게 참값을 따라가며
(둘 다 전 격자 2% 이내), **극단값**에서는 더 낫다 — lmax 는 4개 sigma 전부, lmin 은 작은 sigma 3개.
적합 혼합이 lmin 에서 더 가까운 것은 가장 큰 sigma (0.669) 한 곳뿐이고 거기서 학습 모델은 23% 낮다.
극단값이 `RouteAClip._matrix_site` 가 실제로 소비하는 양이다 (`nu*Herm(J)` 를 역행렬 하므로).

한계 (파일이 명시): 격자점 4개 · n = 48 이라 전 격자 주장이 아니며, "D1 에서 적합 GMM 보다 낫다" 는
**D2 로 전이되지 않고**, 수신기에 대해서는 아무 말도 하지 않는다.

### 12.3 ADDENDUM 2026-09-21 23:50 — D2 를 **최종 체크포인트**로 재측정 (재현성 복구)

체크포인트 `conf/ckpt/d2sx_N160000_a1.pt` (sha256 `4443921ce8d5c4a1…`, `stopped_by=patience`,
**1784 epoch**, best val **3.519379e-01 @1764**). `logs/jacspec_D2_final.log`, n = 48.

> **정정 (2026-09-23, review_next P0-1b)**: §12.3 의 스펙트럼은 이 파일의 **마지막 epoch(1784) EMA** 로 측정됐다. `jac_spectrum.py:42` → `score._as_model` → `load_model` 경로가 `st["ema"]` 를 읽는다(ema sha256[:16] a43f1105eb27a29b, 이 가중치의 val 3.519602e-01). 파일 mtime 09-21 22:37 이 측정(로그 23:47)보다 앞선다. "best val 3.519379e-01 @1764" 는 저장되지 않은 @1764 가중치의 값이다(BEST_WEIGHTS_UNAVAILABLE). 표 수치는 바뀌지 않는다. 원고에 "best 체크포인트에서 측정" 으로 쓰지 말 것. 620 행 뒤 정정을 볼 것.

```
  model                k=0 s=.0331          k=6 s=.0920          k=12 s=.2561        k=18 s=.7126
  learned  n_neg          6.71                19.79                13.50               0.69
           n<0.1         26.52                37.58                41.10              35.50
           25%tile       0.0381              -0.0104               0.0063              0.0565
           lmin         -0.140               -0.298               -0.451              -0.033
  FITTED   n_neg          0.00                 0.00                 0.00                0.00
           n<0.1          3.44                 6.54                11.19               16.94
           25%tile       0.9476               0.6654               0.2028              0.0916
```

- **데이터를 늘려도 나아지지 않는다.** N=1e4 의 8.0 / 10.6 / 11.2 / 7.8 대비 N=1.6e5 완주본은
  6.71 / 19.79 / 13.50 / 0.69 — 방향이 유리하지 않다. sigma = 0.092 에서는 **25th percentile 자체가
  음수(-0.0104)** 다 (64개 중 1/4 이상이 0 미만).
- **manifold 예측은 절반만 맞았다.** D2 의 support 는 3L 차원 집합들의 합집합(L ~ U{3..8}) 이라
  R^64 안의 9~24 차원, 여차원 **40~55**. 학습 모델은 **0.1 미만 고유값을 26.5 / 37.6 / 41.1 / 35.5** 개
  놓고, sigma=0.256 의 41.1 은 예측 대역 40~55 안이다. 적합 혼합은 3.4 / 6.5 / 11.2 / 16.9 개뿐이다.
  **과대예측된 것은 0 을 건너는 개수** (예측 ~여차원의 절반, 실측 7~20).
- **재현 명령:** `OMP_NUM_THREADS=2 python code/jac_spectrum.py --testbed D2 --ckpt ckpt/d2sx_N160000_a1.pt --n 48`

여전히 미확립: D2 에는 폐형식 prior 가 없으므로 "학습 모델의 0 근처 스펙트럼이 적합 혼합보다 참에
가깝다" 는 **미증명**이다. 정답 없는 진단 둘(GB', Hyvarinen)이 학습 모델 편이라 **개연적**일 뿐이다.

### 12.4 ADDENDUM 2026-09-22 00:15 — 기전 정정: **비대칭이 판별자가 아니다**

`logs/jacpsd_D1_N160000.log` (게이트를 통과한 바로 그 모델):

```
  sigma      0.033      0.090      0.245      0.669
  D1 asym    1.88e-3    1.08e-2    3.74e-2    8.39e-2     f(lmin<0) = 0.000 at all 20 grid points
  D2 asym    1.8e-1     2.6e-1     2.6e-1     1.6e-1      f(lmin<0) = 1.000 for sigma <= 0.2
```

격자 상단에서 D1 의 비대칭 0.084 대 D2 의 0.16~0.28 — **약 3배, 같은 자릿수**인데 D1 은 음의 고유값이
하나도 없고 D2 는 64개 중 7~20개다. 따라서 **"DSM 이 비보존장을 만든다" 는 참이지만 두 testbed 를
가르는 것이 아니다** (양쪽 모두에 있는 추정기의 성질이다).

**가르는 것은 여유(margin)다.** D1 의 참 스펙트럼은 0 에서 떨어져 있고 (lmin 0.938 → 0.025,
25th percentile 0.980 → 0.116) 같은 크기의 섭동이 부호를 못 바꾼다. D2 는 manifold 구조 때문에
64개 중 **26~41개가 0.1 미만**(여차원 40~55)이라 같은 섭동이 7~20개를 뒤집는다.
D2 **내부의 sigma 의존성**도 같은 문장으로 설명된다: sigma > 0.2 에서 잡음이 참 스펙트럼을 0 에서
들어올려 여유가 생기므로 f(lmin<0) 가 1.000 → 0.36 으로 떨어진다.

**주장으로 쓸 수 있는 형태 (파일이 적은 그대로):** 학습 score 를 EP 행렬 site 에 꽂을 수 있는 조건은
**대상 밀도의 사후공분산이 수신기가 방문하는 잡음 수준에서 특이에서 떨어져 있는가**이며, 이것은
(i) 학습 전에 생성모형의 내재 차원으로, (ii) 학습 후에 정답 없이 held-out 에서 `f(lmin(Herm J) < 0)`
를 세어서 확인 가능하다. **둘 다 GA~GD 에 없다.**

### 12.5 CAVEAT §5 — V1 의 항등성 주장

`selftest_M6` 는 PSD 투영이 정확 prior 위에서 항등이라고 주장하며 근거로 "lmin 이 `LAM_MIN=1e-6`
보다 **780배** 위" 를 들었다. 전 sigma 격자에서 재면 그 여유는 더 작다 — 적합 GMM 의 lmin 은
k=12 에서 **7.6e-5**, 즉 **76배**. 항등은 성립하되 여유는 **3자릿수가 아니라 2자릿수**다.
(→ 780배로 인용 금지, §17.3)

## 13. 붕괴 진단과 정산(settling) 실험 — **둘 다 미게이트 체크포인트의 진단 탐침**

> **두 절의 모든 수치는 `ckpt/d2sx_N10000_a1.pt` 에서 나왔고, 이 체크포인트는 사전 등록 게이트를
> 통과하지 못했다** (D1 재게이트 `results/hpo_final_r2.txt`: GA 1.03540e-15 PASS, GB 7.71573e-03 PASS,
> **GC 2.24111e-01 FAIL** (기준 0.15), GD 1.49894e-01 PASS, `GD_trace` 2.96603e-02 보고용).
> 두 소스 파일 모두 머리에 "DIAGNOSTIC PROBES, NOT ARMS … may NOT enter any result table and do NOT
> license a claim" 을 박아 두었다. **§17.4 를 반드시 함께 읽을 것.**

### 13.1 발산 진단 — 출처 `results/diag/SUMMARY.md`

체크포인트 `ckpt/d2sx_N10000_a1.pt` (sha256 `d94aa99bdc5689067f90895b28d6394e7c61a296ed58ada3f041eb4ad8fdf01a`,
HPO trial 386), D2 셀 C2.

> **정정 (2026-09-23, review_next P0-1b)**: 이 파일(sha256 `d94aa99b…`)의 가중치는 **마지막 epoch(673) EMA** 다(ema sha256[:16] 62432fd33f0c9378, 이 가중치의 val 3.986240e-01, `logs/train_d2sx_N10000_a1.log:680-681`). best val 3.985658e-01 @653 의 가중치는 저장되지 않았다(BEST_WEIGHTS_UNAVAILABLE). 두 시점 사이 EMA 갱신은 36×20 = 720회다(0.999^720 ≈ 0.49). 그래서 두 가중치는 일부 겹치지만 같지 않다. 평가 경로 `score.load_model` 은 `st["ema"]` 를 읽는다. 따라서 §13 에서 이 파일을 읽은 수치(표 3번 BLER 포함)는 이 @673 EMA 의 값이다. 표 1번 GB'(`results/gate_D2.txt`, 09-21 07:49)는 이 파일이 아니라 형제 시드 `ckpt/B3_dscore_D2.pt` 에서 나왔다(`results/diag/checkpoint-provenance_SUMMARY.md:26-38`). 표 3번 BLER 의 출처는 `raw_supp` 112파일(전부 `meta|dscore_ckpt` = `ckpt/d2sx_N10000_a1.pt`, arm `M-ours-dscore`)이며, ckpt mtime 09-21 12:51:59 가 raw_supp 13:19–13:20 보다 앞선다. H5 "체크포인트 출처 REFUTED" 는 파일 동일성에 대한 판정이므로 그대로 둔다.

세 진단이 서로 어긋나는 것이 출발점이다:

| # | 진단 | 결과 | 출처 |
|---|---|---|---|
| 1 | GB' (one-shot denoising NMSE vs GMM, 동결 20점 sigma 격자) | **학습 prior 가 전 sigma 에서 GMM 보다 낫다**, diff/gmm 0.5204 → 0.8781, `worst_excess` -0.1219 | `results/gate_D2.txt` |
| 2 | Hyvarinen score matching (정답 불필요) | 학습 score 가 3~4배 정확. k=0 (sigma 3.3062e-2): GMM -3198.69 ± 81.18 vs diffusion -14016.64 ± 118.96 (**약 91 s.e.**) | `results/hyvarinen_D2_n1e4.npz` |
| 3 | 16반복 RouteA 수신기의 BLER (C2) | **붕괴.** BLER 0.805/0.898/0.883/0.795/0.686/0.523/0.312 (-3..15 dB), NMSE 비단조이며 6 dB 에서 **1.110 > 1** | `results/tables_D2_supp.txt` |

가설 5개의 판정: **H1 (학습 denoiser 의 야코비안이 유효 공분산이 아니다) = CAUSAL**,
H2 (sigma 범위 외삽) REFUTED, H3 (정규화/스케일/vec 순서) REFUTED, H5 (체크포인트 출처) REFUTED,
H4 (EP 배선) = **CONTRIBUTING, 단독 원인 아님**.

인과 확정의 핵심 — 양방향 do() 개입 (**n = 64** 짝지음, 0 dB / +6 dB):

| arm | Herm(J) 에 가한 개입 | BLER@16 0 dB | +6 dB |
|---|---|---|---|
| `dscore\|eta` | 없음 (= 사전 등록 배선) | 0.922 (.066) | 0.719 (.110) |
| `dscore\|psd1e-2` | 고유값을 [1e-2, 1] 로 투영 | **0.031 (.043)** | **0.000** |
| `dscore\|mean` | 없음. `clip='mean'` 으로만 변경 | **0.047 (.052)** | **0.000** |
| `dscore\|abs1e-2` | \|eig\| 를 1e-2 로 바닥, **부호 유지** | 0.922 (.066) | 0.578 (.121) |
| `gmmB\|eta` | 없음 (정확 GMM, score 배선) | 0.109 (.076) | 0.031 (.043) |
| `g\|scorew+dJ` | 정확 GMM 에 **학습 J 만 주입** | **0.953 ± 0.026** | **0.922 ± 0.034** |

짝지음 McNemar (불일치쌍, 0 dB / +6 dB), 단측, 각각 p < 1e-13: `g|scorew → +dJ` 54:0 / 57:0,
`d|scorew → +gmmJ` 0:55 / 0:46, `→ +psd` 0:57 / 0:46, `→ +clipmean` 0:56 / 0:46.
가로챈 야코비안의 94.8% (0 dB) / 98.6% (+6 dB) 가 수리 전에 부정부호였다.
**조건수가 아니라 부호가 원인이다** (부호를 남긴 `abs1e-2` 는 회복 없음; PD 를 유지한 채 GMM 에
근특이성만 주입한 `tiny4` 는 무손상).

기전 (SUMMARY §5): DSM 은 score 의 **값**만 구속하고 **도함수**는 구속하지 않는다 → 학습장은
비보존적 → Hermitian 대칭화 후에도 `Herm(J)` 가 동작 nu 에서 held-out q 의 **70~100% 에서 부정부호**
→ `RouteAClip._matrix_site` (`Demo/t2_gmm.py:114-122`) 가 **PSD 검사도 정칙화도 없이** `nu*Herm(J)` 를
역행렬 하고 `clip='eta'` 에서 부정부호 역행렬로 만든 eta 를 유지 → 반환된 (precision, mean) 쌍이
어떤 가우시안도 기술하지 않게 되고, RouteA 에는 Module H 경로에 **발산 가드가 없어** 16회를 그대로 돈다.

**SUMMARY §4 가 스스로 철회/약화한 것 5건** (인용 시 반드시 함께, §17.3):
`[C1]` 비대칭은 인과 사슬의 고리가 아니다 (`score.py:959` 가 먼저 대칭화한다; **부정부호만 인과**).
`[C2]` 수신기측 belief-mean shift 는 **용량이 아니라 표지**다.
`[C3]` 클립 발동률은 판별자가 아니다 (GMM 도 lmax>1 클립을 51~79% 에서 친다).
`[C4]` "단일 인과 요소" 는 한 요소 부족 — 독립 수복책이 둘이므로 **결합(conjunction)** 이다.
`[C5]` "실패한 게이트가 곧 야코비안 게이트(GD)였다" 는 **이 구성에서 거짓** — trial 386 은
GD 0.1499 **PASS**, GC 0.2241 **FAIL** 이다.

### 13.2 정산 실험 (7 SNR 개입) — 출처 `results/settling_D2.txt`

D2 셀 C2, **SNR 7점 전부**, SNR 당 **n = 256 짝지음**, `code/diag_psd_cf.py` (`--snrs` 만 변경).

```
BLER@16                    -3 dB    0 dB   +3 dB   +6 dB   +9 dB  +12 dB  +15 dB
gauss|sitesc (= R2-ours-G)  0.375   0.117   0.027   0.027   0.008   0.012   0.004
gmmB|epsite  (= M-ours-b*)  0.324   0.094   0.020   0.012   0.000   0.016   0.000
dscore|eta   (= the arm)    0.824   0.902   0.895   0.777   0.664   0.500   0.332
dscore|abs1e-2              0.793   0.875   0.773   0.613   0.422   0.238   0.098
dscore|psd1e-2              0.176   0.043   0.012   0.004   0.004   0.000   0.000
dscore|mean                 0.184   0.039   0.004   0.004   0.004   0.000   0.000
dscore|belsc                0.168   0.039   0.016   0.008   0.000   0.000   0.000

fraction of trials with NMSE > 1 after 16 iterations
dscore|eta                  0.332   0.488   0.492   0.523   0.344   0.242   0.082
dscore|abs1e-2              0.273   0.398   0.371   0.301   0.160   0.082   0.023
dscore|psd1e-2              0.000   0.000   0.000   0.000   0.000   0.000   0.000
dscore|belsc                0.000   0.000   0.000   0.000   0.000   0.000   0.000
```

1. **sigma 대역 예측이 맞았다.** `jac_spectrum.txt` 가 sigma ~ 0.09~0.26 에 손상 정점, 0.71 에서 소멸을
   예측했고, 수신기의 nu 는 SNR 이 오르면 줄어든다. 발산율이 정확히 그 모양이다:
   0.332 → 0.488 → 0.492 → **0.523 (+6 dB 정점)** → 0.344 → 0.242 → 0.082.
2. **전 SNR 에서 원인은 부호다.** 크기만 바닥 치고 부호를 남긴 `abs1e-2` 는 어디서도 회복하지 않는다.
3. **모든 수리가 발산을 완전히 제거한다** — 7 SNR 전부 NMSE>1 비율 **0.000** (감소가 아니라 0).
4. **수리한 학습 prior 는 적합 GMM 을 7 중 5 SNR 에서 이긴다.**
   `[CORRECTED 18:40 after audit — 원래 제목이 "AT EVERY SNR" 이었고 같은 파일 24행이 그것을 반박한다:
   +9 dB 는 적합 GMM 이 엄격히 낫고(0.000 vs 0.004), +15 dB 는 전 arm 0.000 동률이다.]`
   -3 dB 0.168~0.184 vs 0.324 (~1.9x), 0 dB 0.039~0.043 vs 0.094 (~2.3x), +3 dB 0.004~0.016 vs 0.020.

파일이 직접 적은 한계: arm 결과가 아니다 · 유의성 검정이 아니다 (짝지음 주변비율일 뿐).
예산 관점으로는 이 비교만큼은 동일예산이다 (학습 N=1e4 = GMM 적합 N=1e4). **확증 실행은 §15.**

## 14. D1 확증 실행 (Stage C) — 출처 `results/tables_D1_C.txt`, `results/guard_D1_C.txt`

- 실행 조건: **전 격자점 n = 2560**, 셀 C1(Tp=2)/C2(Tp=4)/C5(Tp=3) x SNR 7점, `raw_C` 1344 파일.
  체크포인트 `ckpt/sx_N160000_D1.pt` (**게이트 PASS**, §11.2).
  **power guard 주의: 전 비교가 POWERED 인 것이 아니다.** `tables_D1_C.txt` 의 **11쌍이 UNDECIDED**
  이고 전부 C2 에 있으며 `M-ours-bstar → V0/V1/V4` 와 `→ M-ours-bstar-scalar` 를 포함한다. 따라서
  **C2 에서 학습 arm 대 GMM 진술은 검정 근거가 없다.** 인용한 C1·C5 비교는 POWERED 다.
  (2026-09-22 01:00 감사 BLOCKER 1 정정.)
  n = 640 중간본을 먼저 보았음이 표 머리말과 `DECISIONS.md` 17:55 에 기록돼 있다.

  > **정정 (2026-09-23, review_next P0-1b·ckpt/M2)**: `sx_N160000_D1.pt` 가 담은 가중치는 마지막 epoch(200) EMA 다(ema sha256[:16] ae04fefa33998484, 이 가중치의 val 7.398687e-01). best val 7.398444e-01 @136 의 가중치는 저장되지 않았다(BEST_WEIGHTS_UNAVAILABLE). §14 의 학습 arm(V0/V1/V4, `raw_C` D1 1344파일)과 §11.2 의 게이트 PASS 는 둘 다 이 같은 @200 EMA 에서 측정됐다. 원고에 "best 체크포인트" 로 쓰지 말 것.

- `M-ours-dscore-C-V4b` 는 **D1 에서 실행하지 않았다** — arm 추가가 1344 태스크 전량 재계산이라,
  누락이 아니라 기록된 결정이다 (`DECISIONS.md` 2026-09-21 21:45).

**앵커 `R2-ours-G` 기준 짝지음 부호검정 (pooled, 판정점 3개 규칙)** — `tables_D1_C.txt` TABLE B:

| 셀 | `→ M-ours-score` (정확 score oracle) | `→ V0` (학습, 행렬 site) | `→ V4` (학습, 스칼라 site) |
|---|---|---|---|
| C1 (Tp=2) | 449:132 p=2.3e-41, 3/3 유의 | **449:227 p=9.7e-18, 3/3 유의** | 429:327 p=0.00023, 1/3 **무의미** |
| C2 (Tp=4) | 321:95 p=9.2e-30, 2/3 유의 | **307:94 p=1.8e-27, 2/3 유의** | 306:134 p=1.5e-16, 2/3 유의 |
| C5 (Tp=3) | 365:148 p=3.5e-22, 3/3 유의 | **374:159 p=5.4e-21, 2/3 유의** | 312:252 p=0.013, 1/3 **무의미** |

학습 prior 의 승수(449 · 307 · 374)가 정확 score oracle 의 것(449 · 321 · 365)과 사실상 같다.

**상한 대비 (C5):** `M-ours-dscore-C-V0 → R6-exactEP` 88:91 **p=0.88, POWERED**,
SNR@0.1 gap -0.00 dB [90% paired bootstrap -0.08, +0.07]. 검정력을 갖춘 상태의 동률이다.

> **정정 (2026-09-23, review_next M-10.3a)**: "상한 대비 (C5)" → "exact-prior EP reference 대비 (C5)". `R6-exactEP` 는 참 prior GMM site 를 쓰는 같은 route_a EP/터보 루프(`code/arms.py:119`)이며 bound 가 아니다: 88:91 의 91 = V0 성공·R6 실패 블록(C5 −3/+0/+3 dB 합, `results/tables_D1_C.txt:1139`, 규약 :754). 수치·판정 불변. DECISIONS [2026-09-23 11:47] 명칭 정정 참조.

**GMM 대비 (C5):** `M-ours-bstar → V0` 103:102 **p=1**, SNR@0.1 +0.03 dB [-0.04, +0.11].
C1 은 299:354 p=0.035 0/3 무의미, C2 는 UNDECIDED.
→ **동일 예산이 아니다** (학습 N'=1.6e5 vs D1 GMM 적합 N=1e4). §6b 에 따라 1차 비교로 쓰지 않는다 (§17.5).

**스칼라 site 는 D1 에서 손해이며 그것은 site 효과다:** GMM 대조군
`M-ours-bstar → M-ours-bstar-scalar` 가 C1 268:443 p=5.5e-11 (3/3), C5 129:270 p=1.4e-12 (2/3)
로 **첫 arm(비스칼라) 우세**. 학습 prior 의 V4 도 같은 방향으로 약해진다.

**(F3) 발산 가드 — 출처 `results/guard_D1_C.txt` (전문 4행이 전부다):**

```
cell    SNR arm                        fired     of    rate  worst NMSE seen
C1       -3 M-ours-dscore-C-V0          2560   2560   1.000  4.535e+18
C1       -3 M-ours-dscore-C-V1          2560   2560   1.000  1.654e+20
C1       -3 M-ours-dscore-C-V4          2560   2560   1.000  1.411e+84
C1       +3 M-ours-dscore-C-V0            11   2560   0.004  3.625e+05
```

가드를 **한 번도 발동하지 않은 arm 11개**: `M-ours-bstar, M-ours-bstar-scalar, M-ours-gmm32,
M-ours-score, R0-pilot, R1-turbo, R2-ours-G, R3-bigamp, R4-llr, R4-scvamp, R6-exactEP`.
`R5-genie` 는 채널 추정이 없어 N/A. 규칙: 16반복 중 **어느 한 반복에서라도** NMSE > 10.0 또는 비유한.
→ **C1 (Tp=2) −3 dB 에서는 수리를 포함한 모든 학습 arm 이 사용 불가다.**

**이 표의 상시 경고:** D1 은 **순환 testbed** 다 (참 prior 가 격자 GMM 으로 정의 → GMM arm 이
correctly specified). 학습 prior 에 대한 어떤 주장도 이 표에서 D2 로 전이되지 않는다.

## 15. D2 확증 실행 (Stage C) — **주장 testbed** — 출처 `results/tables_D2_C.txt`, `results/guard_D2_C.txt`

- 실행 조건: **전 격자점 n = 2560**, 셀 C1/C2/C5 x SNR 7점, `raw_C` 1344 파일,
  기록 시각 2026-09-22 00:22 KST, git `f6062a0`. **전 비교가 POWERED 인 것이 아니다** — `tables_D1_C.txt` 11쌍, `tables_D2_C.txt` 8쌍이 UNDECIDED 이며 §17.3·§17.5 에 목록이 있다. 인용 전 반드시 확인할 것.
- 체크포인트 `ckpt/d2sx_N160000_a1.pt` (sha256 `4443921ce8d5c4a1…`, patience 로 1784 epoch 종료,
  best val **3.519379e-01 @1764**). **검증손실로 3시드 중 선택, BLER 미사용**
  (a1 3.519379e-01 / a2 3.547692e-01 / a3 3.525231e-01 — 시드 간 0.8%, `DECISIONS.md` 23:00).

  > **정정 (2026-09-23, review_next P0-1b)**: 이 파일의 가중치는 마지막 epoch(1784) EMA 다(ema sha256[:16] a43f1105eb27a29b, 이 가중치의 val 3.519602e-01). best val 3.519379e-01 @1764 는 선택 기준값일 뿐이고, 그 epoch 의 가중치는 저장되지 않았다(BEST_WEIGHTS_UNAVAILABLE). §15 와 이후 표의 V0/V1/V4/V4b 는 전부 last-EMA 로 낸 값이다. 원고에 "best 체크포인트" 로 쓰지 말 것. 977 행 표의 같은 서술에도 적용된다. 마지막 epoch val 로 비교해도 시드 순서는 같다(a1 3.519602e-01 < a3 3.525437e-01 < a2 3.548169e-01).

- **게이트 상태 — 정확히 쓸 것.** 표 헤더가 그대로 적고 있다:
  `gate: NO GATE RECORD mentions d2sx_N160000_a1.pt -- UNVERIFIED here. (GA-GD are measurable on D1
  only, 10_SPEC §5: a D2 re-train is qualified by its D1 sibling's gate row, which this string cannot prove.)`
  즉 **D2 체크포인트 자체에는 게이트 행이 없다** (D2 에는 참 score 가 없어 원리적으로 잴 수 없다).
  자격은 **같은 레시피의 D1 쌍둥이 `sx_N160000_D1.pt` 의 PASS 행**(§11.2)이 부여한다.

### 15.1 셀 C2 (8x4, T=16, **Tp=4**, K=42), −3 dB, n = 2560 — TABLE A

| arm | BLER@16 | 95% Wilson CI |
|---|---|---|
| R1-turbo (고전 터보) | 0.537 | [0.517, 0.556] |
| **M-ours-dscore-C-V0** (사전 등록 배선) | **0.593** | [0.573, 0.611] |
| R2-ours-G (가우시안 prior) | 0.329 | [0.311, 0.347] |
| M-ours-bstar (GMM, N=1e4) | 0.252 | [0.236, 0.270] |
| M-ours-bstar-scalar (대조군) | 0.261 | [0.244, 0.278] |
| **M-ours-dscore-C-V1** (PSD 투영) | **0.145** | **[0.132, 0.159]** |
| M-ours-dscore-C-V4 (스칼라 site) | 0.154 | [0.140, 0.168] |
| M-ours-dscore-C-V4b (`scal=site`) | 0.161 | [0.148, 0.176] |
| R5-genie (상한) | 0.034 | [0.028, 0.042] |

> **정정 (2026-09-23, review_next R-10.3)**: `R5-genie (상한)` → `R5-genie` (known-channel receiver reference: 동일 EP detector + BCJR, 참 H). 같은 route_a 반복 루프에 참 H 를 넣은 것이며(`code/arms.py:117`, `Demo/t2_route_a.py:388-389`) bound 가 아니다: 같은 C2 −3 dB 에서 V1 성공·genie 실패 15 블록(`raw_C` `blk_err[:,15]`, n=2560). 0.034 [0.028, 0.042] 불변. DECISIONS [2026-09-23 11:47] 명칭 정정 참조.

### 15.2 사전 등록 짝지음 검정 (pooled, 판정점 3개 규칙) — TABLE B

| 비교 | C2 (Tp=4) | C5 (Tp=3) | C1 (Tp=2) |
|---|---|---|---|
| `R2-ours-G → V0` | **187:5114 p=0, 첫 arm 3/3** | 57:5482 p=0, 첫 arm 3/3 | 65:4326 p=0, 첫 arm 3/3 |
| `R2-ours-G → V1` | **772:67 p=8.5e-153, 3/3 유의** | 665:664 p=1.0, 무의미 | 1125:1425, 첫 arm 2/3 |
| `R2-ours-G → V4` | 762:80 p=2.3e-140, 3/3 유의 | 578:776, 첫 arm 2/3 | 1179:1085 p=0.051, 2/3 유의 |
| `M-ours-bstar → V0` | 111:5310 p=0, 첫 arm 3/3 | 107:5386 p=0, 첫 arm 3/3 | 110:4321 p=0, 첫 arm 3/3 |
| **`M-ours-bstar → V1`** | **511:78 p=5.8e-79, 3/3 유의** | **821:674 p=1.6e-4, 2/3 유의** | 1402:1602, 첫 arm 1/3, 무의미 |
| `M-ours-bstar → V4` | 501:91 p=1.4e-69, 3/3 유의 | 753:805 p=0.2, 무의미 | 1469:1342 p=0.017, 1/3, 무의미 |
| `M-ours-bstar → V4b` | 474:92 p=6e-63, 3/3 유의 | **140:5118 p=0, 첫 arm 3/3** | 125:4278 p=0, 첫 arm 3/3 |
| 대조군 `bstar → bstar-scalar` | 125:149 p=0.16, **무의미** | 588:969, 첫 arm 3/3 | 1117:1485, 첫 arm 3/3 |

C2 의 SNR@0.1 격차 (판정점 -3 / +0 / +3 dB, 90% paired bootstrap, censored 0%):

- `R2-ours-G → V1` : **+2.22 dB** [+1.98, +2.49]   (점별 511:41 / 183:16 / 78:10)
- `M-ours-bstar → V1` : **+1.73 dB** [+1.50, +1.98]   (점별 332:57 / 137:12 / 42:9)
- `M-ours-bstar → V0` : **n/a (-0.50 vs > 15) — SNR 격자를 늘려야 함** (점별 104:975 / 7:1956 / 0:2379)
- 대조군 `M-ours-bstar → M-ours-bstar-scalar` : +0.04 dB [-0.12, +0.19], p=0.16 **무의미**

### 15.3 §6c 사전 등록 예측 대조 — 예측 커밋 `9e0023c` (실행 **전**)

| # | 예측 | 실제 |
|---|---|---|
| 1 | V0 는 게이트 통과에도 D2 에서 붕괴한다 | **맞음.** 세 셀 전부 파국적 (111:5310 / 107:5386 / 110:4321). C2 에서 BLER 0.593 으로 **고전 터보 0.537 보다 나쁘다** |
| 2 | V1·V4 는 정상이고 V0 대비 큰 차이로 낫다 | **C2 에서 맞음** (V1 0.145 vs V0 0.593). C5·C1 에서는 부분적 — C5 의 V4 는 가우시안보다 나쁘고, C1 의 V1 은 GMM 보다 나쁘다 |
| 3 | D1 과 D2 에서 V1·V4 순서가 뒤집힌다 | **틀림.** 뒤집힌 것은 **V0 의 위치**다 (D1 최상위 → D2 최하위). V1 과 V4 의 상대 순서는 양쪽 다 V1 ≳ V4 |
| 4 | GMM 스칼라 대조군은 차이가 없을 것 | **부분적으로 틀림.** C2 에서는 맞지만(p=0.16) C1·C5 에서는 스칼라화가 GMM 을 **유의하게 악화**시킨다 (3/3) |

> **정정 (2026-09-23, review_next G-1.2)**: 예측 1 의 "게이트 통과에도" 는 "D1 형제 게이트 PASS 레시피로 학습한 D2 체크포인트(`d2sx_N160000_a1.pt`)에서도" 로 읽는다. 등록 원문(`10_SPEC_stageC.md:385-386`, 예측 커밋 `9e0023c`)은 사전 등록 텍스트라 고치지 않는다. 채점(맞음)과 수치는 불변.

**→ 2 맞음 / 2 틀림.** 예측을 실행 전에 커밋했고 채점은 그대로 보고한다.

### 15.4 (F3) 발산 가드 — 출처 `results/guard_D2_C.txt`

발동률이 높은 행만 (전문은 파일에 64행):

- **C1 (Tp=2) −3 dB**: V0 / V1 / V4 / V4b 가 전부 **2560/2560 (1.000)**,
  최악 NMSE 7.406e21 / 3.518e24 / 6.72e35 / 1.125e21.
- **V0 는 전 셀·전 SNR 에서 상시 발동**: C2 0.529~0.932 (최악 2.942e9 ~ 2.588e10),
  C5 0.623~0.932, C1 0.786~1.000.
- **V4b (`scal=site`) 는 C1·C5 의 전 SNR 에서 1.000** (최악 NMSE ~1e21). C2 에서만 발동 0.
- **V1 은 C2 에서 발동 0**, C1 에서 0.000~0.179, C5 에서 0.005~0.034.
- GMM·베이스라인: `M-ours-bstar` 가 C1/C5 에서 2~3/2560 (rate 0.001, 최악 NMSE 10.67~60.48),
  `M-ours-bstar-scalar` 1~6/2560. 가드를 **한 번도 발동하지 않은 arm 5개**:
  `R0-pilot, R1-turbo, R2-ours-G, R4-llr, R4-scvamp`. `R5-genie` 는 N/A.
- TABLE A 머리말의 비유한 블록 기록 (전부 **KEPT, 블록 오류로 계수**, 버린 것 없음):
  C1 −3 dB 에서 V0 1077/2560, V1 294/2560, V4 126/2560 이 `blk_err@16` 비유한.

### 15.5 이 실행에서 읽을 수 있는 것 (네 문장, STATUS "읽기" 절)

1. **사전 등록 배선이 수신기를 고전 터보보다 나쁘게 만든다.** V0 는 실질 세 게이트를 통과한
   체크포인트를 사전 등록 D-14 행렬 site 에 그대로 넣은 것이고 결과는 BLER 0.593 대 0.537.
   → **게이트 통과가 수신기 사용 가능성을 보증하지 않는다** 가 실측 확정됐다.

   > **정정 (2026-09-23, review_next G-1.2)**: 690-691행 "V0 는 실질 세 게이트를 통과한 체크포인트를" 은 §17.3 규칙(819-820)대로 "V0 는 D1 형제 `sx_N160000_D1.pt` 가 실질 세 게이트(GB·GC·GD. GA 는 이 모델 계열에서 구조적 0)를 통과한 레시피로 D2 에 학습한 체크포인트(`d2sx_N160000_a1.pt`)를" 로 읽는다. 그 D2 체크포인트에는 게이트 행이 없다(`results/tables_D2_C.txt:45`). 692행은 "D1 형제의 게이트 PASS 가 D2 수신기 사용 가능성을 보증하지 않는다" 로 읽는다(STATUS:390 과 같은 뜻). 수치(BLER 0.593 대 0.537)는 불변이다.

2. **site 를 고치면 같은 모델이 최고 arm 이 된다.** V1 은 C2 −3 dB 에서 0.145, GMM 0.252 대비
   **42% 감소** 한다 — 그러나 **이 두 수는 GMM(N=1e4) 기준이고 학습 arm 은 N'=1.6e5 다. 동일 예산이
   아니므로 인용하지 말 것.** 공정한 것은 **같은 체크포인트** 기준의 site ablation 이다:
   V0 0.593 → V1 0.145 = **75.5% 감소**, genie 까지 격차의 80.1%. 후자만 "같은 체크포인트·같은
   예산·같은 수신기" 라고 말할 수 있다. (2026-09-22 01:00 감사 BLOCKER 3 정정; STATUS 의 이전 판에서
   복사된 문장이었다.)
   **이 site ablation (V0/V1/V4/V4b) 이 Stage C 의 1차 주장이다.**
3. **스칼라화는 학습 prior 전용 이득이 아니며 해가 되기도 한다.** 손익을 정하는 것은 prior 종류가
   아니라 **야코비안 유효성**이다 — D1(유효)에서는 손해, D2 C2(무효)에서는 이득.
4. **V4b (`scal=site`) 는 깨진다.** C2 에서는 다른 수리와 같지만 C1·C5 에서 가드 1.000, 최악 NMSE ~1e21.
   등록해 놓고 빠뜨렸다가 감사 지적으로 넣은 변형이며, 넣지 않았으면 "스칼라화는 안전하다"로
   잘못 결론냈을 것이다.

### 15.6 이 실행의 범위 — **반드시 함께 인용**

- **`M-ours-bstar → V1` 은 동일 예산이 아니다** (학습 N'=1.6e5 vs GMM 적합 N=1e4). §6b·A3 에 따라
  **1차 비교로 쓰지 않는다.** 동일예산 GMM (N'=1.6e5) 적합은 **아직 실행 중**이고 (§20 참조)
  완료되면 `M-ours-bstar-C` 로 다시 잰다. 그때까지 위 GMM 대비 행은 **부수 결과**다.
- **Tp=2 (C1) 에서는 어떤 학습 arm 도 GMM 을 이기지 못한다** (V1 1402:1602 로 오히려 뒤진다).
  이득은 Tp=4 에 집중되며 Stage A/B 의 Tp 의존성(§16)과 같은 방향이다.
- 사전 등록 arm `M-ours-dscore` 는 본 표(`tables_D2.txt`)에서 **BLOCKED 유지**이고 이 실행이 그것을
  바꾸지 않는다. 위는 전부 별도 파일 `tables_D2_C.txt` 의 Stage C arm 이다.

## 16. Tp 교차 셀 읽기 — **EXPLORATORY** — 출처 `results/tp_trend_D2.txt`

**이 파일은 사전 등록 검정이 아니다.** 파일 스스로 "EXPLORATORY, NOT A PRE-REGISTERED TEST" 를 적고,
7개 SNR 에 대한 다중성 보정이 없으며 **검정으로 인용하면 안 된다**고 명시한다. 새 실행이 아니라
동결된 `conf/raw/*.npz` 의 재독이다 (`code/tp_trend.py`).

측정 대상: 구조화 prior 이득 `R2-ours-G → M-ours-bstar` 를, 각 셀의 자체 판정점이 아니라
**모든 SNR 에서 짝지어** 본 것 (Tp 를 움직이고 SNR 을 고정).

```
--- 8x4 array
  SNR | C1(Tp=2)  win:loss        p | C5(Tp=3)  win:loss        p | C2(Tp=4)  win:loss        p
   -3 |    60:53    5.7e-01  |    88:47    5.3e-04* |   274:79    2.5e-26*
   +0 |    83:59    5.3e-02  |    80:43    1.1e-03* |    86:44    2.9e-04*
   +3 |    94:75    1.7e-01  |    62:42    6.2e-02  |    14:3     1.3e-02*
   +6 |   396:362   2.3e-01  |    66:52    2.3e-01  |    10:1     1.2e-02*
   +9 |   413:405   8.1e-01  |    57:60    8.5e-01  |     3:1     6.2e-01
  +12 |    92:98    7.2e-01  |    53:51    9.2e-01  |     3:3     1.0e+00
  +15 |   118:105   4.2e-01  |    36:64    6.6e-03* |     2:0     5.0e-01
 pool |  1256:1157  4.6e-02* |   442:359   3.7e-03* |   392:131   3.1e-31*

--- 4x4 array
  SNR | C3(Tp=2)  win:loss        p | C4(Tp=4)  win:loss        p
   +9 |    77:139   3.0e-05* |     7:1     7.0e-02
  +15 |    88:132   3.6e-03* |
 pool |   269:392   2.0e-06* |    47:5     1.3e-09*
```

인용 가능한 정확한 양 (모두 "탐색적" 꼬리표와 함께):

- 8x4 배열의 pooled 불일치비가 파일럿 예산에 따라 단조 증가: Tp=2 **1.09** (1256:1157),
  Tp=3 **1.23** (442:359), Tp=4 **2.99** (392:131).
- 모든 셀에서 이득이 저SNR 에 몰리고 고SNR 에서 사라지거나 음이 된다:
  C5 (Tp=3) −3 dB 88:47 → +15 dB **36:64 (prior 가 해롭다, p=6.6e-03)**.
- 기하·배열·T 를 고정하고 **Tp 만 다른** +9 dB 에서 부호가 뒤집힌다:
  Tp=2 **77:139** (p=3.0e-05, 해롭다) vs Tp=4 **7:1** (p=7.0e-02, 돕는다).
- **사전 등록 판정은 바뀌지 않는다**: `tables_D2.txt` 의 결정점 분석이 그대로 선다
  (C2 pooled 374:126 p=1.4e-29 유의, C4 47:5 p=1.3e-09 유의, C1 p=0.69 · C5 p=0.12 무의미,
  C3 는 **역전** p=2e-06). 이 파일은 C1/C5 를 양성 결과로 바꾸지 않는다.

---

## 17. 쓰면 안 되는 것

> **이 절이 이 색인의 규율이다. 어떤 수치를 인용하기 전에 여기서 그 수치를 찾아볼 것.**

### 17.1 Stage A/B (기존)

- **"학습된 diffusion prior 가 GMM 을 이긴다"** (Stage A/B 문맥) — 게이트 통과 arm 이 없다.
  `M-ours-dscore` 는 D1/D2 양쪽 본 표에서 BLOCKED 로 표기돼 있다.
- **D1 표의 숫자로 prior 에 대한 주장** — 순환 testbed.
- **D2 C1 (Tp=2) 을 실패로 서술** — T2c 가 사전 진단한 무정보 영역이고, 그 자체가 체제 결과다.
- **TPE 결과로 아키텍처 우열** — 시도 수 불균등. 균등표본 표(`hpo_strat_D1.txt`)를 쓸 것.
- **testbed 선택 근거를 "GMM 에 불리해서"로 서술** — `01_RULES §5` 가 금지. 근거는 "물리적으로 표준"이고
  조건부 Gaussian 파괴는 그 물리의 귀결이며 T2d 가 직접 증거다.

  > **정정 (2026-09-23, review_next M-5.2a)**: 앞 절의 금지("GMM 에 불리해서" 로 서술하지 않는다)는 유지한다. 뒤따르는 "근거는 "물리적으로 표준"이고 조건부 Gaussian 파괴는 그 물리의 귀결" 은 같은 기록의 철회와 충돌한다. `results/NUMBERS_PACKAGE_2026-09-22.md:695`(철회 56)는 "D2 is a standard mmWave channel, so the result transfers to real deployments." 를 인용 금지로 두고, `05_SPEC_testbed_D2.md:25` 는 "D2의 차별점은 "실제 채널"이 아니라 "조건부 Gaussian의 파괴"" 라 적는다. D2 는 고정 |α_ℓ|·연속 균등 각도·고정 지수 PDP(τ=2)로 정의된 통제 모델 하나다(`05_SPEC_testbed_D2.md:16-18`).
  > 인용할 때는 이렇게 쓴다: "근거는 조건부 Gaussian 가정의 파괴를 분리해 보는 통제된 희소 정반사 모델이라는 것이고, T2d 가 그 파괴의 직접 증거다." `01_RULES:77` 의 같은 근거 문구는 사용자 결정을 기다린다(review_next M-5.2a 노트).

### 17.2 Stage C 가 **철회한** 주장 — 인용 금지 (출처 `STATUS.md` "감사 정정", 2026-09-21 18:20 감사)

아래는 내가 한 번 적었다가 감사에서 틀린 것으로 확인돼 **철회한** 문장들이다. **어느 것도 인용해선 안 된다.**

| # | 쓰면 안 되는 문장 | 실제 |
|---|---|---|
| 1 | "학습 diffusion prior 는 쓸 수 있다" (무조건 헤드라인) | D2 BLER 이 없는 상태의 과대주장이었다. 지금은 §15 가 있으나 **배선·셀·예산 범위를 반드시 붙인다** |
| 2 | "V0 는 발산하지 않았다 / 비-genie 최고 성능" | **틀림.** D1 C1 −3 dB 에서 BLER 1.000, 가드 2560/2560, 전 arm 중 최악 |
| 3 | "V1·V4 는 정상 동작" (무조건) | **틀림.** 같은 점에서 V1 0.979, V4 0.953 이고 최악 NMSE 1.654e20 / 1.411e84 |
| 4 | **"D1 학습 야코비안이 정확값과 세 자리 유효숫자까지 일치한다"** | **철회.** 기준선이 참 prior 가 아니라 적합 GMM(K=32, N=1e4)이었다. 대체물은 §12.2 의 참-prior 재측정 |
| 5 | **"GA~GD 어느 것도 PSD 를 시험하지 않는다"** | **철회.** Weyl 로 `GD < λmin(J*)/‖J*‖_F` 이면 PSD 가 **증명된다**. D1 k=0 에서 그 기준은 ≈0.11 이고 실측 GD 는 1.6e-3 이라 68배 안쪽 — **GD 는 거기서 실제로 PSD 를 증명했다** |
| 6 | "수리한 학습 prior 가 7 SNR **전부**에서 GMM 을 이긴다" | **틀림. 5/7 이다.** +9 dB 는 GMM 이 낫고 +15 dB 는 동률 (§13.2) |
| 7 | do() 표를 "n=128" 로 인용 | 실제 **n=64** (§13.1) |
| 8 | **"네 게이트 전부 PASS"** | GA 는 구조적 0 이므로 **실질 3개 (GB·GC·GD)** (§11.1) |
| 9 | "V2 best 3.577178e-01 @81, 계속 개선 중" | **틀림.** 실제 3.569986e-01 @85 이고 그 시점에 이미 NaN 으로 죽어 있었다 |
| 10 | "부정부호는 σ≲0.2 에서만" | 부정부호는 더 큰 σ 에서도 남는다 (σ=0.845 에서 36%). 집중되는 것은 그 **결과**(belief 이탈)다 |
| 11 | D1 확증 결과를 **n=640** 판으로 인용 | 사전 등록 요건 미달. 보고본은 **n=2560** (`tables_D1_C.txt`, `guard_D1_C.txt`) |
| 12 | "gnorm ≈ 2.0 이라 클리핑이 매 스텝 작동" | 실제 **0.2**, 클리핑은 폭발 전까지 거의 발동하지 않았다 |
| 13 | **"학습 arm 이 정확 score oracle 과 동률"** (짝지음 검정으로) | **철회.** 그런 짝지음 검정은 존재하지 않았다 — 두 arm 을 공통 제3자(R2-ours-G)에 각각 붙여 눈으로 비교한 것이었다. (D1 에는 별도로 `V0 → R6-exactEP` C5 88:91 p=0.88 POWERED 가 있고 **그것은 인용 가능하다**, §14) |
| 14 | "V3 의 asym_reg 가 줄고 있다" | **철회.** 인접 두 점을 고른 것이었고 실제로는 4 자릿수를 오르내린다 |
| 15 | "단일 인과 요소는 D-14 행렬 site 다" | 한 요소 부족. 독립 수복책이 둘이므로 **부정부호 J 와 `clip='eta'` 의 결합**이다 (SUMMARY `[C4]`) |
| 16 | "실패한 게이트가 곧 문제의 게이트(GD)였다" | **거짓.** 평가된 구성(trial 386)은 GD 0.1499 **PASS** / GC 0.2241 FAIL (SUMMARY `[C5]`) |
| 17 | "비대칭이 두 testbed 를 가른다" | **정정됨.** D1 에서도 비대칭은 같은 자릿수(0.084 vs 0.16~0.28)인데 음의 고유값은 0 이다. 가르는 것은 **여유(margin)** 다 (§12.4) |
| 18 | `jac_spectrum.txt` 본표의 `n<0.1` 컬럼 | **라벨 오류.** 그 값은 `n<0.01` 이다. 진짜 `n<0.1` 은 훨씬 크다 (§12.1) |
| 19 | "belief-mean shift 가 손상의 용량(dose)" | **표지(marker)일 뿐** (SUMMARY `[C2]`) |
| 20 | "클립 발동률이 학습/GMM 판별자" | **아니다.** GMM 도 lmax>1 클립을 51~79% 에서 친다 (SUMMARY `[C3]`) |
| 21 | "비대칭이 인과 사슬의 고리" | **아니다.** `score.py:959` 가 먼저 Hermitian 대칭화한다. **부정부호만 인과** (SUMMARY `[C1]`) |
| 22 | V1 의 PSD 투영 항등성을 "**780배** 여유" 로 | 전 격자에서는 **76배** (적합 GMM lmin 7.6e-5 @ k=12). 3자릿수가 아니라 2자릿수 (§12.5) |

### 17.3 **미게이트(UN-GATED) 체크포인트에서 나온 수치** — arm 결과로 인용 금지

게이트를 통과하지 못했거나 게이트 자체가 없는 체크포인트에서 나온 수치는 **진단 탐침**이며,
어떤 결과 표에도 들어갈 수 없고 어떤 주장도 허가하지 않는다. 해당 항목:

| 출처 | 체크포인트 | 게이트 상태 |
|---|---|---|
| `results/diag/SUMMARY.md` 전체 (§13.1) | `ckpt/d2sx_N10000_a1.pt` | **FAIL** — D1 재게이트 GC 0.2241 vs 0.15 (`hpo_final_r2.txt`) |
| `results/settling_D2.txt` 전체 (§13.2) | 동일 | **FAIL** — 파일 머리에 "DIAGNOSTIC PROBES, NOT ARMS" |
| `figs/F9` 전 행 | 동일 | **FAIL** — 캡션에 명시 |
| `figs/F8` 의 D2 곡선 4개 | `d2sx_N10000_a1` + N=1.6e5 스냅샷 2개 | **미게이트**. 스냅샷 2개는 **임시 디렉토리 파일이라 재현 불가** (18:20 감사) |
| `figs/F7` 패널 (b) | `ckpt/d2sx_N160000_a1.pt` | **게이트 불가** — D2 에 참 score 가 없다 (`04_SPEC §5`, `LADDER_C.md`) |
| `jac_spectrum.txt` 본표의 D2 N=1.6e5 행 | 임시 디렉토리 epoch-240 스냅샷 | **재현 불가**. 재현 가능한 판은 §12.3 |
| §11.3 / §11.4 의 V2·V3 수치 | `sx_V2_N160000_D1_a3.pt` 외 | **FAIL / UNGATED** — §17.5 |

또한 **`results/tables_D2_C.txt` 의 Stage C arm 이 쓰는 D2 체크포인트 자체에는 게이트 행이 없다.**
표 헤더가 `NO GATE RECORD mentions d2sx_N160000_a1.pt -- UNVERIFIED here` 라고 적는다. 자격은
같은 레시피의 **D1 쌍둥이** `sx_N160000_D1.pt` 의 PASS 행이 부여한다 (§11.2). 인용할 때
"게이트를 통과한 D2 모델" 이라고 쓰면 안 되고, **"D1 에서 게이트를 통과한 레시피로 D2 에 학습한
체크포인트"** 라고 쓴다.

### 17.4 **동일 예산이 아닌 학습 vs GMM 비교** — 1차 비교로 인용 금지

`01_RULES §5` / `10_SPEC A3` / `§6b`: arm 간 공정 비교는 **동일 N_train** 에서만 성립한다.
현재 상태:

- 학습 arm (V0/V1/V4/V4b): **N_train = 160,000**
- `M-ours-bstar`, `M-ours-bstar-scalar`, `M-ours-gmm32`: **N_train = 10,000**
- → **`M-ours-bstar → V1`, `M-ours-bstar → V4`, `M-ours-bstar → V0` 등 모든 GMM 대비 행은 동일
  예산이 아니다.** §15.2 의 표, §14 의 GMM 대비 행이 전부 여기 해당한다.
- 동일예산 GMM (N' = 1.6e5, arm 명 `M-ours-bstar-C`) 적합은 **아직 끝나지 않았다** (§20).
  끝나기 전에는 **GMM head-to-head 를 1차 주장으로 보고하지 않는다** (`DECISIONS.md` 14:40 · 22:30 · 23:00).
- **1차 주장으로 쓸 수 있는 것:** (i) **site ablation V0/V1/V4/V4b** — 같은 체크포인트·같은 예산·같은
  수신기라 완전히 공정, (ii) `R2-ours-G` 대비 (Gaussian prior 는 N_train=10000 의 표본공분산이지만
  `M2` 테스트가 Module H 이외의 모든 차이를 0 으로 확인했다).
- 예외적으로 **동일 예산인 학습-GMM 비교 하나**: `results/settling_D2.txt` 는 학습 N=1e4 = GMM 적합
  N=1e4 라 예산은 같다. **그러나 미게이트 체크포인트이므로 §17.3 에 의해 여전히 arm 이 아니다.**

### 17.5 **V2 / V3 의 어떤 수치도 arm 결과가 아니다** — 게이트를 통과하지 못했다

- **V2 (에너지 매개화)**: D1 게이트 **FAIL** (GC 0.167378 vs 0.15, 11.6% 초과 — §11.3).
  §3b ("arm 으로 승격할 변형은 D1 게이트 통과 여부로만 정한다") 에 따라 **V2 는 arm 이 아니다.**
  §3d 사다리 3시행 소진 (a1 DIVERGED, a2 DIVERGED, a3 FAIL).
- **V3 (야코비안 정칙화 λ=1.0)**: 게이트 행이 **없다**. D1 a1 DIVERGED, D2 a1 DIVERGED,
  D2 a2 는 완주했으나 **D2 에는 참 score 가 없어 UNGATED**.
- **`train_V2_D2_N160000_a3` 의 best val 3.492148e-01 @285** 은 **D2 DSM 검증손실 관측 사실로만**
  인용할 수 있다. 비교 상대인 V0 a1 의 최선은 **3.519379e-01 @1764** 이다
  (`logs/train_d2sx_N160000_a1.log` 마지막 행: `stopped_by=patience, best val 3.519379e-01 @ epoch 1764,
  wall 35774.6 s`). **`STATUS.md` 22:25 절의 "3.519459e-01 @1756" 은 실행이 끝나기 전 중간값이며
  인용하지 말 것** (§20.9). §11.3 의 (1) 이 보여주듯
  검증손실은 GC 도 수신기 성능도 함의하지 않으며, **V2 의 D2 모델은 어떤 BLER 표에도 arm 으로
  들어가 있지 않다.**
- V2 의 GC 실패를 "에너지 매개화의 결과" 로 단정해서도 안 된다 — **매개화와 학습률(lr/3)이 교란돼
  있고**, 동결 lr 로 완주한 V2 D1 실행은 존재하지 않는다 (§11.3 의 (2)).

### 17.6 그 밖의 Stage C 금지

- **`figs/F7` 의 D2 패널로 "학습 모델이 틀렸다"** — 적합 혼합은 **정답이 아니다.** 전랭크 성분
  공분산은 저차원 집합 근처의 밀도를 표현할 수 없어 야코비안이 항등 근처에 머물고 **공짜로 PSD** 다.
  PSD 라는 사실은 학습 모델이 틀렸다는 증거가 아니다 (`jac_spectrum.txt` READING 3, F7/F8 캡션).
- **D2 C2 에서 "genie 상한과 유의하게 다르다 / 가깝다" 는 검정 진술** — `R5-genie` 를 앵커로 한
  **모든 쌍이 사전 등록 power guard 에서 UNDECIDED** 다 (판정 SNR 이 −3, +0 dB 두 개뿐 — genie 가
  +3 dB 부터 앵커 창 `BLER in [0.005, 0.9]` 밖). §15.5 의 "남은 격차의 49%" 는 TABLE A 값의
  **기술적 서술**일 뿐 검정이 아니다. 출처: `figs/F11_bler_D2_confirmatory.txt`.
- **`M-ours-dscore-C-V0` 의 BLER 을 보통의 오류율로 읽기** — C2 의 V0 곡선은 **전 SNR 에서 (F3) 가드가
  52.9~93.2% 발동**한다 (`guard_D2_C.txt`). 발산 중인 수신기의 값이므로 다른 arm 과 오류율로서
  비교되지 않는다. 같은 이유로 C5·C1 의 V4b 곡선(전 SNR 2560/2560)도 그렇다.
- **`figs/F4` 의 고SNR 눈금을 "이득 0" 으로 읽기** — 블록 오류가 적어 비율 추정 불가 구간이다.
- **`tp_trend_D2.txt` 를 검정으로 인용** — 다중성 보정이 없는 탐색적 재독이다 (§16).
- **`results/diag/SUMMARY.md` 의 수리 arm** (`dscore|psd1e-2`, `dscore|mean`, `dscore|belsc`,
  `d|scorew+gmmJ`, `g|scorew+dJ`, `X-gmm-score`) — 사전 등록 전에 BLER 을 본 arm 이며,
  **이 수치의 힘으로 어떤 표에도 들어갈 수 없다** (SUMMARY §8 무결성 선언).
- **`runner.py analysis` 를 `--tag` 없이 실행** — 사전 등록 파일을 덮어쓴다. 2026-09-21 21:45 에
  실제로 `tables_D1.txt` 헤더 3줄을 건드려 `git checkout` 으로 복원한 사고가 있다 (`DECISIONS.md`).

## 18. 그림 — `conf/figs/` (PDF + PNG)

### 18.1 Stage A/B — 생성 `code/figures.py`

| 파일 | 내용 | 쓸 곳 |
|---|---|---|
| `F2_lemma.png` | 복호기 soft output = 정확 Tweedie score. (좌) 산점, (우) 오차 vs sigma^2 | 이론 앵커 |
| `F3_bler_D2.pdf/png` | **BLER vs SNR, D2. (a) Tp=4 headline, (b) Tp=2.** 두 패널 대비가 체제 결과를 한 장에 담는다 | **메인 그림** |
| `F3_bler_D1.pdf/png` | 같은 그림의 D1 판 (순환 testbed, 맥락용) | 부록 |
| `F4_regime_D2.pdf/png` | Module H 이득 vs SNR, Tp = 2/3/4. **90% paired bootstrap CI**, 블록오류 15개 미만 점은 축에 눈금만 | 체제 주장 |
| `F5_samplecx.pdf/png` | GB/GC/GD vs 학습 표본수 N, 게이트 선 점선. `GC ~ N^-0.47` 적합선 | **음성 결과 그림** |
| `F6_arch.pdf/png` | 아키텍처 균등표본 비교 (30회씩). 빨강 = best-of-30, 검정 = median, 초록 파선 = 전 게이트 통과선 | 아키텍처 주장 |

주의: `F4` 고SNR 눈금을 "이득 0"으로 읽지 말 것 · `F6` 에서 **초록선(1.0)에 닿은 아키텍처가 없다**
(음성 결과의 시각적 요약) · `F3(b)` 의 평탄한 곡선은 T2c 가 예측한 무정보 영역이다.

### 18.2 Stage C — 생성 `code/figures_stagec.py` (house style 은 `figures.py` 에서 import)

각 그림에 같은 이름의 `.txt` 가 **캡션 + 출처 + 게이트 상태**를 담고 있다. **그 파일을 함께 읽을 것.**

| 파일 | 내용 | 게이트 상태 | 쓸 곳 |
|---|---|---|---|
| `F7_jacspectrum_D1_D2.*` | `sym(J_r)` 고유값 스펙트럼, sigma 격자 4점 (k=0,6,12,18). **(a) D1**: 학습 / **참 prior** (1024 성분 격자 GMM) / 적합 GMM(K=32) — **셋 다 n_neg = 0**. **(b) D2**: 학습 N=1.6e5 최종 체크포인트 / 적합 GMM(K=512) — 학습 스펙트럼이 4점 전부에서 0 을 건넌다 (n_neg 6.7 / 19.8 / 13.5 / 0.7). n=48, 샘플당 64 고유값, y 는 symlog | (a) **PASS** (`sx_N160000_D1.pt`) · (b) **게이트 불가 = 진단 탐침** | **기전 그림** |
| `F8_budget_psd_asym.*` | 20점 sigma 격자 전체에서 (상) `f(λmin(J_r) < 0)`, (하, log) `asym(J_r)`. 예산별 1선. **σ ≤ 0.26 에서 D2 곡선 4개가 f = 0.95~1.00 에 겹친다 — 16배 데이터가 둘 다 못 움직인다.** D1 학습 모델은 **같은 아키텍처·레시피·예산으로 f = 0**. n=128/격자점 | D2 전 곡선 **미게이트**, D1 곡선 **PASS** | 예산 배제 |
| `F9_sigma_band_vs_snr.*` | (a) `shift_med` vs sigma 격자 + 위험대 음영 (코드가 적용한 규칙: 최대의 2배 이내), (b) 7 SNR 의 발산율(NMSE>1 비율). 두 x 축은 **다른 물리량이고 서로 매핑하지 않는다** — 유일한 연결은 (a) 위의 `sigma_t(SNR)` 눈금자 (별도 측정, **n=12**) | **전 행 미게이트** (`d2sx_N10000_a1.pt`) | σ 대역 ↔ SNR 모양 |
| `F10_bler_D1_confirmatory.*` | D1 확증 BLER, **n=2560**, 셀 C5/C2/C1. arm: R1-turbo, R2-ours-G, M-ours-bstar, M-ours-score(oracle), V0, V4, R5-genie. **회색 띠** = power guard 가 UNDECIDED 로 남긴 쌍의 판정 SNR (쌍 수준 판정이며 BLER 값이 불확실하다는 뜻이 아니다). **빨간 고리** = (F3) 가드가 2560 전부 발동한 점 (C1/−3 dB 의 V0·V4). BLER 0 은 0.5/n = 1.95e-4 에 그린다 | **PASS** (`sx_N160000_D1.pt`) — 탐침이 아니라 확증 | D1 확증 |
| `F11_bler_D2_confirmatory.*` | **D2 확증 BLER = 주장 testbed.** n=2560, C2(Tp=4) 주 패널 + C5/C1. arm 9종 (R1-turbo, R2-ours-G, M-ours-bstar, M-ours-bstar-scalar, V0, V1, V4, V4b, R5-genie). **빨간 큰 고리 + 후광** = (F3) 가드가 2560 중 50% 초과 발동한 점 (= 발산 중인 수신기이므로 그 BLER 은 보통의 오류율이 아니다), **작은 고리** = 일부 발동. 회색 띠 = power guard UNDECIDED 쌍의 판정 SNR. BLER 0 은 0.5/n = 1.95e-4 에 그린다 | 체크포인트 `d2sx_N160000_a1.pt` — **D2 게이트 행 없음** (§15), 캡션이 `NO GATE RECORD … UNVERIFIED here` 를 그대로 인용 | **주장 그림** |

| `F12_tp_envelope.*` | **Tp 동작 범위, 게이트 통과 예산 N=1.6e5** (run `B16e4`), n=2560, C1/C5/C2 BLER (위) + 사전 등록 판정점 부호검정을 불일치쌍 마진 (a−b)/(a+b) 로 (아래 좌축) + 폐형식 바닥·**측정** ν_q·격자 상한 (아래 우축). C5 는 곡선이 −3~+6 dB 에서 V1 우세이나 앵커 규칙이 판정점을 +6/+12/+15 에 두어 **동률**(623:640) — 캡션이 그 이유를 적는다. 생성 `code/figures_stagec2.py` | `d2sx_N160000_a1` — D1 형제 `sx_N160000_D1` **PASS** | **범위 그림** (§6f) |
| `F14_headline_C2_m3dB.*` | **헤드라인 지점, 최종.** run `B16e4k` = 게이트 통과 + 동일예산 + **확장 K=1024 격자**. C2 −3 dB: GMM 0.243 / V1 0.145 / V0 0.593 / genie 0.034. §6q 고정 메뉴 A1~A8. **(d) 패널만 다른 체크포인트(N=1e4 진단)** 이며 캡션·패널 안에 명시 | 게이트 통과 (형제) | **헤드라인 그림** |
| `F15_gap_robustness.*` | **격차가 데이터·성분수·시드로 설명되지 않는다.** (a) C2 11 SNR 등예산, V1 이 11/11 우세·가드 0, 절대차 최대 −6 dB·비 최대 +6 dB 둘 다 표시 (b) 예산축 1e4/4e4/1.6e5 격차 0.107/0.105/0.108 (c) 성분축 K=512/1024/2048, 우도 +2.16~3.18 nat 에 BLER 불변 (d) 시드축 a1/a2/a3, V1 산포 0.0043 대 V0 0.0926. 생성 `code/figures_stagec3.py` | 패널별 혼재 — 캡션·푸터가 어느 패널이 게이트 실패분인지 명시 | **방어 그림** (§6d·§6l·§6g·§6p) |
| `F14b_C2_m6dB_max_absolute_gap.*` | 같은 메뉴, C2 −6 dB (N=1e4): **절대 감소 최대** 0.791→0.601. **사후 선택**, 캡션 첫 줄 명시 | 게이트 실패 (N=1e4) | 보조 |
| `F14c_C2_p6dB_max_ratio.*` | 같은 메뉴, C2 +6 dB (B16e4k): **비 최대** (게이트 통과 예산 1.7×, N=1e4 에서 3.2×). **사후 선택**, 명시 | 게이트 통과 | 보조 |

`F12`/`F13` 는 2026-09-22 14:55 에 독립 검증(wf_49dc79b9-4cf, 확인 결함 38건)을 반영해 인쇄 폭 7.16 in 으로 다시 그렸고,
`F12`·`F14` 는 22:00 에 **실험 마감본**(F12 → 게이트 통과 `B16e4`, F14 → 확장 격자 `B16e4k`)으로 다시 그렸다. `F15` 는 그때 신규.

> **정정 (2026-09-23, review_next G-1.2)**: §17.3 규칙(819-820: "게이트를 통과한 D2 모델" 이라고 쓰지 않고 "D1 에서 게이트를 통과한 레시피로 D2 에 학습한 체크포인트" 라고 쓴다)을 위 표가 스스로 어긴 곳이 있다. 읽는 법 — 905 설명: "run `B16e4k` = D1 형제 게이트 PASS 레시피 + 동일예산 + 확장 K=1024 격자"(게이트 열 "게이트 통과 (형제)" 는 이미 한정됨). 908 게이트 열: "D1 형제 게이트 PASS". 907 게이트 열: "D1 형제 게이트 FAIL (N=1e4)". 911: "F12 → D1 형제 게이트 PASS 예산 `B16e4`". 906 게이트 열 '어느 패널이 게이트 실패분인지' 는 '어느 패널이 D1 형제 게이트 FAIL 분인지' 로 읽는다. F15 캡션과 푸터 원문은 이미 'checkpoints whose D1 siblings FAIL GC' 로 한정한다(`code/figures_stagec3.py:192-193`, `:237-238`). 근거: D2 체크포인트 게이트 행 없음(`tables_D2_B16e4.txt:45`, `tables_D2_B16e4k.txt:45`, `tables_D2_B1e4.txt:45`), 형제 행 `LADDER_C.md:1` PASS(GB +0.27% / GC 0.0999 / GD 0.0718), `samplecx_D1.txt:28` GC 0.24333 FAIL. 904·908 괄호 안의 "게이트 통과 예산" 은 예산 표현이라 그대로 둔다. 그림 파일과 캡션은 재생성하지 않는다. 수치 불변.

`F8` 의 알려진 한계 (캡션이 직접 적음): N=1.6e5 곡선 2개는 **임시 디렉토리 체크포인트**라 다시 돌릴 수
없고, 재측정 로그(`logs/jacpsd_D2_final.log`)는 그릴 때 20점 중 7점만 있어 **그리지 않았다**
(그 7점은 f = 0.992, 1.000 × 6 으로 그려진 곡선과 겹친다). 20행이 차면 **다시 그릴 것.**

`F11` 이 그리도록 만들어진 세 가지 (전부 `tables_D2_C.txt` TABLE A):
(a) C2 에서 **V0 가 전 SNR 에서 고전 터보 위에 있다** (0.593 / 0.845 / 0.954 / 0.950 / 0.909 / 0.818 /
0.446 대 R1-turbo 0.537 / 0.213 / 0.079 / 0.041 / 0.025 / 0.019 / 0.009). 그림 전체에서 예외는 단 한 점,
**C5 / −3 dB** 뿐이다 (V0 0.769 대 R1-turbo 0.795).
(b) C2 에서 V1·V4·V4b 가 **전 SNR 에서 비-genie 최하위 3자리**를 차지한다. **셋 중 누가 최저인지는 이
그림이 가리지 않는다** — V1 이 7점 중 5점, V4 가 +3 dB, +6 dB 에서는 셋 다 0.006 이다.
(c) **C1 에서는 그 순서가 성립하지 않는다** (−3 dB 에서 V1 0.979 · V4 0.953 대 bstar 0.778).
C1 의 `bstar → V1` · `bstar → V4` 는 **둘 다 무의미**이고, C2 의 같은 두 쌍은 3/3 유의다.

**`F11` 이 드러낸 판정 사실 하나 — C2 에서 genie 대비 비교는 전부 UNDECIDED 다.** `R5-genie` 가 앵커일 때
판정 SNR 이 2개(−3, +0 dB)밖에 나오지 않아 (genie 가 +3 dB 부터 0.005 이하로 앵커 창 [0.005, 0.9] 밖)
사전 등록 power guard 가 판정을 내리지 않는다. → **C2 에서 어떤 arm 도 genie 상한과 다르다고 주장할 수
없다.** §15.5 의 "genie 까지 남은 격차의 49% 를 메운다" 는 TABLE A 값의 **기술적 서술**이며 검정이 아니다.

`F10` 의 정직 주석: C1/−3 dB 에서 "모든 학습 arm 이 BLER 1.0" 은 **V0 에만 맞다** — V1 0.996(미도시),
V4 0.945 이고 V4 의 2560 블록 중 3개가 비유한 BLER@16 (KEPT, 블록 오류로 계수).

**F11 은 작성 도중(2026-09-22 00:45 KST) 형제 에이전트가 생성했고** 위 표에 넣었다. 캡션 전문은
`figs/F11_bler_D2_confirmatory.txt` 이며 가드 발동 전량(>50% 37행, ≤50% 26행)과 예산표가 거기 있다.

## 19. 파일 지도

### 19.1 Stage A/B (동결)

| 파일 | 내용 |
|---|---|
| `results/tables_D2.txt` | **주 결과.** 표 A/B/C/D, 셀 C1~C5 |
| `results/tables_D1.txt` | 계측기 결과 (순환 경고 포함) |
| `results/samplecx_D1.txt` | 표본 복잡도 곡선 (§8) |
| `results/hpo_strat_D1.txt` | 아키텍처 균등표본 비교 (**인용용**) |
| `results/hpo_D1.txt` | TPE 탐색 724 시도 (맥락용) |
| `results/gate_D1.txt` / `gate_D2.txt` | 게이트 GA~GD 수치 / GB' |
| `results/testbed_D2.txt` | T2a~T2e (+T2dm) |
| `results/gmm_fit_D2.txt` | GMM 적합표 + D1 대비 악화 |
| `results/lemma.txt` + `figs/F2_lemma.*` | F2 lemma |
| `results/hyvarinen_D2_n1e4.npz` | Hyvarinen score matching 진단 (정답 불필요) |
| `results/tables_D2_supp.txt` + `raw_supp/` | 보조 BLER 실행 (미게이트 체크포인트, arm 아님) |
| `figs/F3..F6` | 결과 그림. 생성 `code/figures.py` |
| `results/tests.txt` | 사전 등록 테스트 35/35 |
| `LADDER.md` | 사다리 전 시도 (82행, append-only) |
| `raw/` | npz 1056개 (블록별 성공/실패 플래그 포함, paired 재분석 가능) |

### 19.2 Stage C

| 파일 | 내용 | 절 |
|---|---|---|
| `10_SPEC_stageC.md` | Stage C 사전 등록 (+ 증보 §3b §3c §3d §6b §6c §9) | §10 |
| `LADDER_C.md` | Stage C 사다리 (append-only). **PASS 행 = `sx_N160000_D1.pt`** | §11.2 |
| `results/gate_D1_C.txt` | Stage C 게이트 측정. 담고 있는 체크포인트는 **V2 a3 하나** (FAIL). **GA 구조적 0 선언이 표 위에 있다** | §11.1, §11.3 |
| `results/jac_spectrum.txt` | 야코비안 스펙트럼 본표 + 증보 3건 (21:55 참-prior 재측정 / 23:50 D2 최종 체크포인트 / 00:15 여유 기전) | §12 |
| `results/diag/SUMMARY.md` | 붕괴 진단 407행, 가설 H1~H5, do() 개입, 정정 [C1]~[C5]. **미게이트 탐침** | §13.1 |
| `results/diag/*.npz`, `*.txt`, `*_SUMMARY.md` | 진단 산출물 (야코비안 PSD, EP site, H4 J-swap, 체크포인트 출처) | §13.1 |
| `results/settling_D2.txt` | 7 SNR 개입 실험, n=256 짝지음. **미게이트 탐침** | §13.2 |
| `results/tables_D1_C.txt` | **D1 확증** n=2560, 3셀 x 7 SNR. TABLE A/B/C/D | §14 |
| `results/guard_D1_C.txt` | (F3) D1 발산 가드 발동 (전문 4행) | §14 |
| `results/tables_D2_C.txt` | **D2 확증 = 주장 testbed.** n=2560, 1344 raw | §15 |
| `results/guard_D2_C.txt` | (F3) D2 발산 가드 발동 (64행) | §15.4 |
| `results/tp_trend_D2.txt` | Tp 교차 셀 읽기. **EXPLORATORY** | §16 |
| `raw_C/` | Stage C raw npz 1344개 (D1 + D2, paired 재분석 가능) | §14, §15 |
| `ckpt/sx_N160000_D1.pt` | D1 게이트 **PASS** 체크포인트 (Stage C arm 의 자격 근거) | §11.2 |
| `ckpt/d2sx_N160000_a1.pt` | D2 확증 체크포인트. sha256 `4443921ce8d5c4a1…`, 1784 ep, best val 3.519379e-01 @1764 | §15 |
| `figs/F7..F10` (+ 동명 `.txt` 캡션) | Stage C 그림. 생성 `code/figures_stagec.py` | §18.2 |
| `code/guard_report.py` | (F3) 가드. `DIVERGE_NMSE=10.0` 재사용, **탐지·분류 전용** | §10 |
| `code/jac_spectrum.py` | 스펙트럼 측정 | §12 |
| `code/diag_psd_cf.py` | do() 개입 / 정산 실험 | §13 |
| `code/selftest_M6.py` / `selftest_V2.py` / `selftest_V3.py` | V1 / V2 / V3 구현 자체검증 | §11~§12 |
| `STATUS.md` | 실행 기록. 상단 "■ Stage C 요약" 과 "감사 정정", 하단 "■■ D2 확증 실행 결과" | 전반 |
| `DECISIONS.md` | 자율 판단 1행/건 + 근거 + 되돌리는 법 (Stage C 분 포함) | 전반 |

## 20. 출처를 찾지 못한 것 / 아직 존재하지 않는 것

누락 대신 여기에 적는다. **아래 항목은 인용할 수 없다.**

1. **`M-ours-dscore-C-V4b` 의 학습 예산이 표 헤더에서 해소되지 않는다.** `tables_D2_C.txt` 는
   V0/V1/V4 를 `N_train=160000  ckpt=d2sx_N160000_a1.pt` 로 적으면서 **V4b 만
   `N_train=10000 -- unclassified arm, quoting the point's channel-set size`** 로 적는다.
   V4b 는 §3c 정의상 V4 와 같은 체크포인트를 쓰는 변형이므로 이 10000 은 arm 분류기가 붙이지 못한
   자리표시값으로 보이지만, **파일이 그렇게 적고 있으므로 여기서 해소하지 않는다.**
   `F11` 캡션도 같은 문장을 그대로 옮기며 "this figure does not resolve it" 이라고 적는다.
   → **V4b 를 "학습 N'=1.6e5 arm" 으로 단정해 인용하지 말 것.**
2. **동일예산 GMM `M-ours-bstar-C` (N' = 1.6e5)** — **아직 존재하지 않는다.**
   적합이 실행 중이며 (`logs/fit_D2_n16e4.log` 마지막 행 **164/180**, 누적 31,381 s),
   출력 디렉토리 `results/gmm_fits_D2_n16e4/` 는 **비어 있고** `gmm_fit_D2_n16e4.txt` 요약도 없다.
   → 학습 vs GMM 의 **동일예산 head-to-head 수치는 어디에도 없다** (§17.4).
3. **`STATUS.md` "■ Stage C 요약" 항목 9 의 가드 수치 (`1400/1400`, 최악 NMSE 4.5e+18 / 6.6e+17 / 1.4e+84)**
   — 이것은 **n=640 중간 실행의 값**이고 보고본이 아니다. 보고본은 `results/guard_D1_C.txt` 의
   **2560/2560**, 최악 NMSE **4.535e+18 / 1.654e+20 / 1.411e+84** 이다 (§14). **`6.6e+17` 은 현행
   가드 파일 어디에도 없다.** 요약 절의 그 행을 인용하지 말고 가드 파일을 인용할 것.
4. **`V4b` 의 D1 BLER** — 실행하지 않았다 (arm 추가가 1344 태스크 전량 재계산이라
   `DECISIONS.md` 2026-09-21 21:45 에 기록된 결정). D2 확증에는 포함돼 있다 (§15).
5. **`V2` / `V3` 의 D2 BLER** — 존재하지 않는다. 게이트를 통과하지 못했으므로 arm 이 아니다 (§17.5).
6. **D2 의 폐형식 참 prior / 참 score** — 원리적으로 없다 (`05_SPEC §3`). 따라서 D2 의
   "학습 스펙트럼이 참에 더 가깝다" 는 **증명 불가**이며 정답 없는 진단 2종(GB', Hyvarinen)이
   지지하는 **개연적** 진술로만 쓸 수 있다 (§12.3).
7. **`jac_spectrum.txt` 본표 D2 N=1.6e5 행의 epoch 라벨** — 임시 디렉토리 스냅샷이라 정확한 epoch 기록이
   없다. `F8` 캡션은 `STATUS.md` 489행이 가리키는 epoch 816 을 유일한 단서로 들며 그래서 숫자 대신
   "later snap." 이라고 쓴다.
8. **D2 확증 실행에서 SNR 격자를 벗어난 SNR@0.1 격차** — `M-ours-bstar → V0` 는
   `n/a (-0.50 vs > 15) — extend the SNR grid` 로 기록돼 있다. **수치가 없다** (§15.2).
9. **V0 D2 a1 의 best val 에 기록이 두 가지 있다.** `STATUS.md` 22:25 절은 `3.519459e-01 @1756`,
   `DECISIONS.md` 23:00 · `jac_spectrum.txt` 23:50 증보 · 학습 로그 마지막 행은 `3.519379e-01 @1764`.
   학습 로그가 종결값이므로 **`3.519379e-01 @1764` 를 쓴다** — STATUS 의 값은 실행 도중(1784 ep 완주 전)
   에 적힌 중간 best 다. 확인 명령:
   `tail -1 conf/logs/train_d2sx_N160000_a1.log`
