# STATUS — conf 실험 (최종)

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
