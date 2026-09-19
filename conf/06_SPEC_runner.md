# 06 — 러너 사양

## 1. arm 목록 (testbed에 따라 다름)

같은 러너에서 같은 인터페이스로 돌아야 한다.

### baseline (먼저 만든다)

| tag | 구성 | 출처 |
|---|---|---|
| `R0-pilot` | pilot-only LMMSE + 1-pass 검출·복호 (turbo 루프 없음) | 기존 `Demo/` 래핑 |
| `R1-turbo` | 고전 turbo: 양 경로 APP feedback, **LOO 없음**, 표본 공분산 LMMSE 재추정 | 기존 (exp_0921 A의 LOO 제거 조건) |
| `R2-ours-G` | D-15 + LOO + $\beta=0.7$ + Gaussian(표본 공분산) prior | 기존 (`lmmseC_pf`). **우리 모델의 기준선** |
| `R3-bigamp` | BiG-AMP + BCJR | **신규** — `02_SPEC_baselines.md` §1 |
| `R4-scvamp` | 3-module SC-VAMP형, Module B `mode='onsager'` | **신규** — `02_SPEC_baselines.md` §2 |
| `R4-llr` | 같은 구조, `mode='llr'` (원문 ablation 재현) | **신규** |
| `R5-genie` | genie CSI | 기존 |
| `R6-exactEP` | `exactEP-true` (참 prior 정확 EP, oracle 상한) | 기존 |

### 우리 모델 (baseline 테스트 통과 후에 만든다)

| tag | Module H | 출처 |
|---|---|---|
| `M-ours-gmm32` | GMM 적합(EM) + 정확 mixture EP site, $K=32$ | `03_SPEC_ourmodel.md` — `conf/code/` 조립기 경유 |
| `M-ours-bstar` | 같은 것, 검증 우도 최대 arm (`b*`) | 〃 |
| `M-ours-score` | 참 prior 정확 score + D-13 + D-14 | 〃. **D1 전용**(D2에는 정확 score가 없다) |
| `M-ours-dscore` | **학습된 diffusion score** + D-13 + D-14 | `04_SPEC_diffusion.md` 게이트 통과 모델. **D1·D2 양쪽** |
| `M-ours-G` | Module H를 Gaussian으로 되돌린 것 — **테스트 M2 전용**, 결과 표에는 넣지 않는다 | 〃 |

> **모든 `M-ours-*`는 `R2-ours-G`와 Module H **하나만** 달라야 한다.** 테스트 M2가 이를 증명한다(`07_SPEC_tests.md`).
> 셋 중 무엇이 논문의 "우리 모델"인지는 **이번 결과로 정하지 않는다**(`00_GOAL.md` §6, `01_RULES.md` §5).

### testbed별 arm 집합 — 같지 않다

| | D1 (격자 GMM) | D2 (sparse specular) |
|---|---|---|
| R0, R1, R2, R3, R4-scvamp, R4-llr, R5-genie | ○ | ○ |
| `R6-exactEP` | ○ | **✕** (참 prior 정확 EP 불가) |
| `M-ours-gmm32`, `M-ours-bstar` | ○ | ○ (D2 데이터로 **재적합**) |
| `M-ours-score` (oracle) | ○ | **✕** (정확 score 없음) |
| `M-ours-dscore` (학습) | ○ | ○ (D2 데이터로 **재학습**, 아키텍처는 D1 통과본 고정) |
| `M-ours-G` (M2 테스트 전용) | ○ | ○ |

**두 표는 arm 집합이 다르다.** 합쳐서 한 표로 만들지 않는다.

## 2. 고정 설정

| 항목 | 값 |
|---|---|
| 부호 | rate-1/2 convolutional $(133,171)_8$, $\nu=6$, BCJR |
| 변조 | QPSK |
| 외부 반복 | **16, 전 arm 공통** |
| testbed | **D1** = 기존 격자 GMM(prior S 우선) / **D2** = sparse specular(`05_SPEC_testbed_D2.md`, S2 우선) |
| 파일럿 | prior S → eigen-aligned, U → DFT. **셀 안에서 전 arm 동일 행렬** |
| 채널·잡음 실현 | **셀 안에서 전 arm paired** (동일 시드, 동일 실현) |
| $n$ | sweep 640, C1 headline 2점 2560 |
| 시드 | 고정, 결과 파일에 기록 |

## 3. 셀 (우선순위 순)

| id | $N_r\times N_t$ | $T$ | $T_p$ | 비고 |
|---|---|---|---|---|
| C1 | 8×4 | 16 | 2 | **headline** |
| C2 | 8×4 | 16 | 4 | 교차-$T_p$ goodput 포락선용 |
| C3 | 4×4 | 28 | 2 | sanity |
| C4 | 4×4 | 28 | 4 | sanity |

SNR 격자: `Demo/exp_0925_run.py`의 것을 읽어 그대로 쓴다. 읽을 수 없으면 `01_RULES.md` §4의 fallback.

## 4. 서브커맨드

| 이름 | 동작 |
|---|---|
| `tests` | `07_SPEC_tests.md` 전 항목. 잔차 수치 출력. **하나라도 FAIL이면 그 arm은 본 실행에서 제외** |
| `smoke` | $n=2$, 전 arm, 수치는 폐기. 예외·형상 점검만 |
| `run` | 본 실행. 셀·SNR·arm 지정 가능. chunk 재개 지원 |
| `lemma` | `Demo/exp_0915_bcjr_score_check.py`를 수정 없이 호출 → `conf/results/lemma.txt` + F2 그림 |
| `sigma` | $\sigma_t$ 격자 측정 (`04_SPEC_diffusion.md` §3) → `sigma_grid.txt` |
| `train` | **score model 학습.** `--rung L1..L6 --attempt k --device cuda`. 체크포인트 → `conf/ckpt/`, 시도 로그 → `LADDER.md`. 재개 가능 |
| `gate` | 학습된 체크포인트에 GA~GD 평가 (D1) 또는 GB′ (D2) → `gate_D1.txt` / `gate_D2.txt` |
| `testbed` | D2 생성기 검증 T2a~T2e (`05_SPEC_testbed_D2.md` §2) |
| `analysis` | `08_SPEC_analysis.md`의 표 생성 |

인자: `--cell --snr --n --arm --iters --beta --tin --seed --prior --testbed --device --dtype --rung --attempt --ckpt`.

`--device`: **`run`·`tests`의 기본값은 `cpu`**(추론은 전 arm 동일해야 하므로). **`train`·`gate`의 기본값은 `cuda`**(학습은 GPU가 정답이고 arm 간 paired 비교 대상이 아니다). `run`에서 GPU는 `01_RULES.md` §9의 조건을 만족할 때만 쓰고, **전 arm에 동일하게** 적용한다. **`--jobs`는 두지 않는다**(기본 = 전체 코어).

## 5. 출력

### `conf/results/*.txt`
사람이 읽는 표. 맨 위에 **재현 헤더** 필수:

```
date / git commit / python & numpy (& torch) version
device: CPU(cores) or GPU(model) | dtype: complex128 / complex64 | deterministic: yes/no
cell, prior, pilot type, SNR grid, n per point, outer iterations, seed rule
arm list with per-arm notes:
  R3-bigamp : prior i.i.d. CN(0,1/Nr) — correlated prior not supported (structural), beta=<used>, T_in=<used>
  R4-scvamp : channel estimation = classical APP-LMMSE (no LOO); Onsager interface only
  M-ours-score : ORACLE arm — exact score of the TRUE prior, NOT a learned diffusion prior.
                 No claim of "learned channel prior gain" can be made from this run.
  M-ours-*  : full config dump (D-15 loop, LOO, beta, n_inner, iters, clip rule, Module H, K, kappa)
              + equivalence test M1/M2 result (PASS / UNVERIFIED / FAILED)
fit/training cost column (GMM EM wall-clock) — 숨기지 않는다
```

### `conf/raw/*.npz`
chunk 재개 가능. 파일당 최소한 다음을 담는다:

- 반복별 NMSE($\mathbb E\|\hat{\mathbf H}-\mathbf H\|_F^2/\mathbb E\|\mathbf H\|_F^2$), 반복별 BLER/BER
- 블록별 성공/실패 플래그 (paired 분석용)
- 실패 분류: `stuck` / `cyc2` / `diverged` / `other`
- clip 발동 카운트 ($\alpha$ clip, 분산 하한 clip)
- 사용한 $\beta$, $T_{\rm in}$, 시드, 반복 수

**실패·발산 블록을 raw에서 빼지 않는다.** 집계에서 어떻게 다루는지는 분석 단계에서 정한다.

### `conf/logs/`
모든 stdout/stderr tee. stderr는 별도 파일.
