# 논문 그림 용어집 (내부 용어 → 논문 용어)

논문 그림에는 이 프로젝트 안에서만 쓰는 이름(arm 코드, 셀·testbed 코드, 등록 판정 문구)을 넣지 않는다 (사용자 지시 2026-10-05 CDT). 원고 본문도 같은 이름을 쓰면 그림과 맞는다. 기록(`docs/RESULTS.md`, 등록 문서, 그림 `.txt`)은 내부 이름을 그대로 쓴다 — 이 표가 둘을 잇는다.

## 방법 (arm)

| 내부 | 그림 (영문) | 비고 |
|---|---|---|
| V1, M-ours-dscore-C-V1, "diffusion prior V1 (proposed)" | **Proposed (diffusion prior)**; 좁은 곳은 **Proposed** | 학습 diffusion prior + PSD 수리 행렬 site |
| V0 | Diffusion prior, unrepaired | 수리 없는 학습 야코비안 site |
| V4 / V4b | Diffusion prior, scalar site / Diffusion prior, scalar site (b) | |
| b\*, M-ours-bstar, "GMM prior b\*" | **GMM prior** | 동일예산, 검증 우도로 K 선택 (캡션에) |
| M-ours-bstar-scalar | GMM prior, scalar site | |
| M-ours-gmm32 | GMM prior (K = 32) | |
| R2, R2-ours-G | Gaussian prior | 같은 EP 수신기 |
| R0, R0-pilot | Pilot-only LMMSE | 판독 시점이 둘이다: 첫 반복 뒤 (`R0-pilot@1`; 원고 IV-A 정의, 등록 baseline) = `F16deep_wide`·`F21sel_wide`·`F2a_snr`·`F2b_budget` 의 곡선과 F29 의 행, 16 회 뒤 = F22 의 곡선 — 캡션에 적는다 |
| R1 | Turbo LMMSE receiver | |
| R3 | BiG-AMP | |
| R4 | SC-VAMP (LLR 판이면 SC-VAMP (LLR)) | |
| bstar-pilot / b\* pilot-only | GMM prior, pilot-only | |
| V1-pilot | Proposed prior, pilot-only | |
| ALDv-pilot / ALD-pilot | Annealed Langevin (error-aware) / Annealed Langevin (plug-in) | |
| SBL-loop / SBL-pilot / OMP-pilot | SBL (in loop) / SBL (pilot-only) / OMP (pilot-only) | |
| V1-edge / V1-clamp | Proposed, out-of-grid rule / Proposed, clamped queries | |
| R5, R5-genie, genie, "known-channel reference" | **Perfect CSI** | 같은 검출기·루프에 참 H. bound 아님 (캡션에) |

## 데이터셋 (testbed)·셀

| 내부 | 그림 |
|---|---|
| D2 | Sparse specular |
| D3 | Sparse specular, CN gains |
| SV8e | Clustered SV (Saleh–Valenzuela) — 좁은 곳은 Clustered SV |
| UMi28 | 3GPP UMi 28 GHz |
| MIX3 | 3GPP mixed |
| C2 / C6 / C9 | 8×4 / 16×4 / 32×4 (N_r = 8 / 16 / 32, N_t = 4, 4 pilots) |
| C1 / C5 / C7 / C8 | 8×4, 2 pilots / 3 pilots / 6 pilots / 8 pilots |
| "D2 C2" (헤드라인) | Sparse specular, 8×4 |
| DOP ν / ROT θ | Doppler ν = … / Array rotation θ |
| S2d (표류 학습), S2v (공간 비정상) | Drift-trained prior / Spatially non-stationary |

## 축·통계량

| 내부 | 그림 |
|---|---|
| BLER@16, "BLER (16 outer iterations)" | BLER (반복 수는 캡션에) |
| SNR@0.1 격차 b\* − V1 | SNR gain at BLER 0.1 [dB] (> 0: proposed better) |
| R, R_dp, R_X, "recovery … over the decision points", "b\*→genie gap closed by V1" | Fraction of the GMM-to-perfect-CSI gap closed (기준선이 GMM 이 아니면 "baseline-to-perfect-CSI gap") |
| N_train, "equal training budget" | Training set size N_train (channels) — 동일예산은 캡션에 |
| N_train — 원고 Fig. 2 용 판 (한 단 판 `F16b_col`, 두 단 판 `F16deep_wide` (b), subfigure 판 `F2b_budget`) 의 x 축 | Training set size N′ (channels) — 원고 Fig. 2 용 판의 x 축은 원고 표기 N′ 를 쓴다 (`$\mathit{N}$` + U+2032; 이 표의 N_train 에 대한 예외) |
| kron K=… | K = … (GMM components) |

## 그림에서 지우는 것 (캡션이나 본문으로)

- 등록 판정 문구와 표기: (i)·(ii)·(iii)·(iv), "3/3", "POWERED", "UNGATED", "(T+)", "Holm", "S1:", "S2:", "not decided", "recorded value, not scored", "[operating-point robust]", "[K-cap …]", "report-only", "decision points", "primary ΔR …", "monotone increase".
  - 꼭 필요한 유의성 표시는 기호로: (iii) → "n.s.", (iv) → "insuff." (캡션에서 정의).
- 내부 공정 표시: "gate-FAIL recipe" 음영, "best-val weights" 계열 (같은 예산 점이 둘이 되지 않게 last-EMA 점만), "cited, STATIC16e4" 같은 출처 꼬리표.
- 그림 제목 (패널 표시 (a), (b), … 만 남김).

## 그림 작업 중 추가된 이름 (2026-10-05 CDT, 논문 그림 에이전트 보고)

| 내부 | 그림 | 쓰인 곳 |
|---|---|---|
| failures / 2560 | Block errors (예: 623/2560) | F17 숫자 상자 |
| X\* (closest baseline: −3 dB 실패가 가장 적은 기준선, GMM + 12 개 중) | Best baseline | F25 |
| b\* in V1's wiring | GMM prior, proposed wiring | F18 |
| 불일치 비용 (SNR@0.1) | SNR loss from mismatch at BLER 0.1 [dB] | F23 (b) |
| recorded blocks | non-aborted blocks | F18 (b) |
| static (조건) | Static | F27 |
| V1-edge / V1-clamp (좁은 곳) | Out-of-grid rule / Clamped queries | F18 |
| 라벨 격자 색 | Proposed fails less / n.s. / insuff. / Proposed fails more (none) | F29 범례 |
| hollow = (iii)/(iv) | Hollow: n.s. or insuff. | F27 |
