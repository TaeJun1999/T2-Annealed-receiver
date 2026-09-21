# STATUS — conf 실험 (Stage A/B 완료 · Stage C 진행 중)

## 세션 설정
- 모델 : **Opus 5 (1M context)** (`claude-opus-5[1m]`). effort/thinking 은 세션 내부에서 확인·변경 불가한
  클라이언트 설정이라 모델이 검증할 수 없음.
- 기간 : 2026-09-20 00:22 KST ~ 2026-09-21 10:10 KST (약 34시간)
- 자원 : NVIDIA RTX PRO 6000 Blackwell x 6 (각 97887 MiB, Exclusive_Process), CPU 192코어.
  수신기 실행 = **CPU 전용 complex128** (전 arm 동일) / score 학습·게이트 = GPU float32.
  -> 테스트 **G1·G2 는 N/A** (수신기에 GPU 를 쓰지 않았으므로).

---

# 완료 : DoD 9항목 전부 충족

| # | DoD 항목 | 상태 |
|---|---|---|
| 1 | 테스트 B·S·C·M·L 전 항목 PASS | **35/35 PASS** (S4 N/A, S5·S7·T2b·T2c·T2e RECORD) |
| 2 | `results/sigma_grid.txt` | 있음 (측정 20점, D2 판 별도) |
| 3 | 학습 증거 | ckpt **38개 1517 MB**, LADDER **82행**, `gate_D1.txt`, train 로그 38개, **ABORTED 0건** |
| 4 | D1 전 arm 표 + 순환 testbed 경고 | `tables_D1.txt` (경고 삽입 확인) |
| 5 | T2a~T2e | `testbed_D2.txt`, **T2d PASS** |
| 6 | `gmm_fit_D2.txt` | 있음 (K 16~512 x full/kron x kappa x restart) |
| 7 | D2 전 arm 표 (headline) | `tables_D2.txt` (claim testbed 경고 삽입 확인) |
| 8 | 표 A/B/C/D, n>=640, headline 2점 n>=2560 | 전부 있음. C1 +6/+9 dB, C2 -3/0 dB 에서 n=2560 |
| 9 | STATUS 최종 + push | 이 파일 |

**셀 9개 x SNR 격자, raw 1056개.** D1: C1~C5 / D2: C1~C5.

---

# 핵심 결과

## 1. 수신기 — D-15 + LOO 루프 (양 testbed 유의)

| 비교 | D2 C2 | p |
|---|---|---|
| R1-turbo -> R2-ours-G | **+2.77 dB** [2.13, 3.42] | 8.1e-97 |
| R2-ours-G -> R4-scvamp (최근접 선행의 Onsager 인터페이스) | R2 가 **+5.61 dB** 우세 | 2.2e-236 |
| R4-llr -> R4-scvamp (원문 ablation 재현) | Onsager 우세 | 1.2e-07 |
| R2-ours-G -> R3-bigamp | R2 압도 | 매우 유의 |

`09_PRIOR_ART_NOTE` 가 지목한 스쿠핑 위험(arXiv:2604.19061)에 대한 직접 답 — **저들의 인터페이스만으로는
우리 설정(미지 bilinear 채널)에서 작동하지 않는다.**

## 2. Module H (구조화 GMM) — **headline**

**D2 C2, n=2560 (결정점):  R2-ours-G -> M-ours-bstar  = +0.49 dB [0.30, 0.72],
3/3 점 전부 유의, pooled 374:126, p=1.4e-29**

- **M2 = 정확히 0.0** 이 이 격차가 **Module H 단독의 몫**임을 증명 (다른 모든 설정 동일)
- b* = kron K=256, **검증 우도만으로 선택** (BLER 미사용). K 격자는 b* 가 경계에 놓일 때마다
  128 -> 256 -> 512 로 확장했다 — GMM 을 강하게 만드는 = **우리 주장에 불리한** 방향

## 3. 이득이 나타나는 조건 (체제 특성)

Tp 2/3/4 x SNR 7점 x 2 testbed 에서 일관된 패턴: **Module H 는 채널 추정이 부정확한 저SNR 에서 이득을
주고, 고SNR 에서는 이득이 사라지거나 역전된다** (D2 C5 +15dB: R2 0.116 vs bstar 0.159, 36:64 p=0.0066).
D2 C1(Tp=2)에서 이득이 없는 것은 T2c 가 사전에 진단한 대로 **첫 패스가 무정보**(NMSE_inf 0.466 ~ 1-Tp/Nt 0.5)
이기 때문이고, 그 셀은 표에서 빼지 않고 진단 결과로 보고한다.

## 4. 학습 diffusion prior — BLOCKED, 그러나 정량화된 음성 결과

**총 959 시도** (사전 등록 사다리 18 + 확장칸 15 + TPE 724 + 균등표본 196 + 최종 재게이트 6) **전부 게이트 미달.**

동일 1e4 예산에서 **GB(0.0117<=0.05) 와 GD(0.161<=0.20) 는 충족, GC 만 0.243 vs 0.15 로 1.62배 부족.**

**표본복잡도 (보고 전용, arm 비교는 1e4 고정):**

| N_train | GB | GC | GD | 판정 |
|---|---|---|---|---|
| 2,500 | 0.0552 | 0.785 | 0.324 | FAIL |
| **10,000** (arm 예산) | 0.0117 | 0.243 | 0.161 | FAIL |
| 40,000 | 0.0045 | 0.167 | 0.101 | FAIL |
| **160,000** | 0.0027 | **0.0999** | 0.0718 | **PASS** |

`GC ~ N^(-0.474)` (R^2 0.934), 0.15 교차점 **N ~ 5.3e4** — 40k/160k 사이로 **측정된** 교차.
-> 결론은 "해봤는데 안 됨"이 아니라 **"동일 예산에서 GC 만 1.62배 부족하고 기준 도달에 ~1e5 필요"** 이다.

부족분이 아키텍처나 인터페이스 탓이 아님도 확인했다:
- 아키텍처: 959시도 + **균등표본 n=30씩 6종** 비교에서 mlp 만 명확히 열등(4.540), 나머지 5종
  (unet 1.572 / uvit 1.814 / dit 1.865 / adm 1.872 / conv 1.902) 은 **통계적으로 구분 불가**
- 인터페이스: 정확 score 를 one-shot D-13+D-14 로 넣은 것과 정확 mixture-EP site 의 차이가
  **유의하지 않음** (p=0.14, -0.07 dB [-0.55, +0.39])

## 5. 이론·검증 앵커

- **F2 lemma** : 복호기 soft output = 부호심볼 prior 의 정확 Tweedie score. `max|tanh-E| = 2.33e-15`,
  Tweedie 유한차분 `6.89e-10`. 복소 규약 `L_c = 4/sigma_c^2` 확인 (`2/sigma_c^2` 는 오차 0.495)
- **T2d** : 조건부 Gaussian 파괴를 **메커니즘까지** 검증. L in {3..8} 전 구간 층화, 측정 vs 해석해
  `2 - sum p^2` 편차 **5.0e-3**, 99.9% CI 전부 Gaussian 값 2 를 배제 (worst CI_hi-2 = -0.2518)
- **M2 = 0.0**, M1 = 0.0 (기존 exp_0925 arm 과 비트 동일)

---

# BLOCKED
- `M-ours-dscore` : 게이트 통과 체크포인트 없음 -> D1·D2 양쪽 표에서 BLOCKED/FAILED-VERIFICATION 표기.
  **게이트를 낮추지 않았다.**

# DECISIONS
- 34건 (`conf/DECISIONS.md`)

# 주요 산출물
`results/` : tables_D1.txt, tables_D2.txt, gate_D1.txt, gate_D2.txt, samplecx_D1.txt, hpo_D1.txt,
hpo_strat_D1.txt, testbed_D2.txt, gmm_fit_D2.txt, lemma.txt, sigma_grid.txt, sigma_grid_D2.txt,
tests.txt, ckpt_inventory.txt / `figs/F2_lemma.png` / `LADDER.md` (82행) / `raw/` (1056)

---

# Stage C — 학습 prior 예산 교정 재시도 (2026-09-21 14:00 KST 개시, 진행 중)

사전 등록: `10_SPEC_stageC.md` (커밋 bce4e62, **결과 관측 전**에 커밋됨).
**Stage A/B 판정은 전부 동결.** `tables_D1/D2.txt`, `gate_D1.txt`, `LADDER.md` 불변이며
`M-ours-dscore` 는 본 표에서 BLOCKED 유지. Stage C 산출물은 전부 별도 파일(`*_C.*`, `LADDER_C.md`).

## C0 — 왜 재시도하는가 (전부 Stage C 착수 이전에 측정된 사실)

`results/samplecx_D1.txt` / `samplecx.csv` — 게이트 vs 훈련 표본 수:

| N_train | GA | GB (≤0.05) | GC (≤0.15) | GD (≤0.20) | gate_score | 판정 |
|---|---|---|---|---|---|---|
| 2,500 | 1.5e-15 | 0.0552 | 0.785 | 0.324 | 5.24 | FAIL |
| **10,000** (등록 예산) | 1.1e-15 | **0.0117 ✅** | 0.243 ❌ | **0.1608 ✅** | 1.62 | FAIL |
| 40,000 | 1.0e-15 | 0.0045 ✅ | 0.167 ❌ | 0.1010 ✅ | 1.11 | FAIL |
| **160,000** | 9.9e-16 | **0.0027 ✅** | **0.0999 ✅** | **0.0718 ✅** | **0.666** | **PASS** |

등록 예산에서 이미 **GA·GB·GD 통과**, 놓친 것은 GC 하나(배율 1.62). GC ~ N^(-0.474) (R² 0.934),
임계 통과가 4e4(FAIL)–1.6e5(PASS) 사이에서 **실측으로** 괄호됨. 즉 등록된 부정 결과는
"방법 부적합"이 아니라 **"예산 부족"**이다.

## C1 — 붕괴 메커니즘 진단 (완료분)

보조 BLER 실행(`tables_D2_supp.txt`)에서 N=1e4 모델은 BLER 0.31~0.90 으로 붕괴했고
**NMSE 가 SNR 상승과 함께 1 을 넘었다**(6 dB 에서 1.11) — 부정확이 아니라 **발산**.

원인 확정 (`results/diag/jacobian-psd_*`), D2 σ 격자 k=6, n=256:

| 모델 | site 공분산 indefinite | belief 평균 이탈 shift(중앙값) |
|---|---|---|
| **diffusion (N=1e4)** | **255 / 256** | **1.87** (p90 59.4, max 1.5e6) |
| GMM-exact (kron K=512) | **0 / 256** | 3.5e-4 (max 9.3e-3) |

수신기 실측 (`jacobian-psd_receiver_clip_C2.txt`, raw_supp 640 trial/SNR):

| arm | 클리핑 비율 | shift 평균 | shift 최대 |
|---|---|---|---|
| **M-ours-dscore** | **0.99 ~ 1.00** | **4.3e3 ~ 1.1e5** | **5.5e7** |
| M-ours-bstar | 0.44 ~ 0.74 | 1.4e-4 ~ 5.5e-3 | 6.5e-2 |
| M-ours-gmm32 | 0.30 ~ 0.57 | 7.1e-5 ~ 3.4e-3 | 3.1e-2 |

**메커니즘**: 참 posterior-mean 디노이저는 J = Cov(h|q)/σ² 이므로 대칭 PSD 가 강제되지만
신경망 야코비안은 그렇지 않다 → D-14 행렬 site 가 부정부호 → LAM_MIN 바닥치기 →
site 의 평균 η 와 정밀도 Λ 가 상호 모순 → belief 평균이 6~8 자릿수 이탈 → 루프 발산.

**이것이 GB′(posterior 평균)와 Hyvarinen(score)이 둘 다 학습 prior 우세를 보고하면서도
BLER 이 붕괴한 이유다. 깨진 것은 평균도 score 도 아니고 오직 미분이며, 그것이 GD 가 재는 양이다.**
GD 는 등록 예산에서 0.161 (통과) 이었으나 D2 에서의 유효성은 D1 게이트가 보증하지 않는다 — §C3 참조.

## C2/C3 — 진행 중

| 작업 | 상태 |
|---|---|
| D1 N=1.6e5 게이트 정식 기록 → `gate_D1_C.txt`, `LADDER_C.md` | 실행 중 |
| D2 score N=1.6e5 학습 (dit/vp/angle, HPO 최적 구성 그대로) | 실행 중 (epoch 259, val 3.678e-1) |
| GMM D2 N=1.6e5 재적합 (동일 예산, K≤512, 180 EM) | 실행 중 (~6h 예상) |
| GMM D2 N=4e4 재적합 | 167/180 |

## 미해결 / 다음

- N=1.6e5 모델(GD 0.072)의 야코비안도 부정부호인가? **이것이 Stage C 의 분기점.**
  아니면 예산만으로 해결, 맞으면 사전 등록된 수정 (F1) 대칭 PSD 투영을 적용한다.
- (F1)(F2)(F3) 적용 여부는 `10_SPEC_stageC.md` §3 의 사전 정당화에 따르며 BLER 을 보고 정하지 않는다.
