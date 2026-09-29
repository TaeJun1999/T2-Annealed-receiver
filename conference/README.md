# 학회 원고용 결과 모음

스냅샷 기준: SUPP16e4 결과·감사까지 (2026-09-29 CDT). 이 폴더는 **색인과 사본**만 담는다. 원본은 다음과 같다.
- 수치: `conf/results/`
- 실행 기록: `docs/EXPERIMENTS.md`
- 결정: `conf/DECISIONS.md`

수치와 라벨은 각 사전 등록 문서 §6과 DECISIONS의 결과 기록 줄에서 **그대로 옮겼다**. 해석은 넣지 않았다.

| 파일 | 내용 |
|---|---|
| [`conf/conference_plot/`](../conf/conference_plot/) | 학회용 그림 F16~F29 (pdf·png·txt). F24~F29 는 비정상 실험. `.txt` 에 수치 전부와 캡션용 캐비엇이 있다 |
| `RESULTS_snapshot.md` | `docs/RESULTS.md` 사본. §1~§10.7과 그림 목록 §11이 들어 있다. 09-27까지의 결과만 담는다 |

공통 조건 (따로 적은 곳 외):
- testbed D2 계열, 셀 C2 (8×4, T=16, Tp=4)
- 동일예산 N_train = 1.6e5, SNR당 n = 2560, BLER@16
- 짝지음 부호검정 `M-ours-bstar (GMM b*) → M-ours-dscore-C-V1 (V1)`
- 라벨 (i) = "V1이 적게 실패", (iii) = 유의 방향 없음, (iv) = 판정하지 못함 (검정력 미달)
- 격차는 SNR@0.1(b\*) − SNR@0.1(V1)이며 단위는 dB다

## 1. 헤드라인과 확장 (RESULTS_snapshot에 수록)

| 실험 | 등록 문서 | 기록된 결과 | 그림 | RESULTS 절 |
|---|---|---|---|---|
| 헤드라인 D2 C2, 동일예산 | Stage C (10_SPEC), [B32e4](../conf/results/review_next/NEXT_EXPERIMENTS_B32e4.md) | (i) 3/3, pooled 454:78, 격차 +1.41 [+1.22, +1.64], 회수율 R 0.470 | F16 | §1 |
| 여차원 C6 (Nr=16) | [C6B16e4](../conf/results/review_next/NEXT_EXPERIMENTS_C6B16e4.md) | 1e4 회수율 0.838 | F17 | §5, §7 |
| C1 격자 밖 질의 규칙 K2 | [K1K2](../conf/results/review_next/NEXT_EXPERIMENTS_K1K2.md) | C1 −3 dB 테스트 V1-edge 대 b\* 400:264 | F18 | §8 |
| 파일럿 오버헤드 Pareto | [PARETO](../conf/results/review_next/NEXT_EXPERIMENTS_PARETO.md) | (A) C7/C8 (i) | F19 | §9 |
| 채널 모델: D3 | [D3B16e4](../conf/results/review_next/NEXT_EXPERIMENTS_D3B16e4.md) | (i) 393:67, 격차 +1.41, R 0.367 | F20 | §10.1–10.2 |
| 채널 모델: 38.901 UMi28 (주) · MIX3 (부속) | [38901](../conf/results/review_next/NEXT_EXPERIMENTS_38901.md) | UMi28 (i) 161:73, +0.60, R 0.062 · MIX3 (i) 198:71, +0.98 (보고) | F20 | §10 |
| 채널 모델: SV8e | [SVB16e4](../conf/results/review_next/NEXT_EXPERIMENTS_SVB16e4.md) | (iv) 148:72, +0.25, R 0.143 | F20 | §10 |
| 전 baseline 곡선 (6 데이터셋) | — | R1 turbo, R2 Gaussian, R3 BiG-AMP, b\*, V1, genie | F21 | §11 |
| 시드 강건성 | [SEEDS16e4](../conf/results/review_next/NEXT_EXPERIMENTS_SEEDS16e4.md) | D2·UMi28 모두 "시드 강건 (3/3 (i))" | — | §10.5 |
| 파일럿 전용 prior (Arvinte–Tamir형 설정) | [PILOT16e4](../conf/results/review_next/NEXT_EXPERIMENTS_PILOT16e4.md) | P1 4/6 (i), P2 6/6 (i); D2 C2 P2 +1.07 | F22 | §10.6 |
| 학습/평가 채널 모델 불일치 | [MISMATCH16e4](../conf/results/review_next/NEXT_EXPERIMENTS_MISMATCH16e4.md) | MM 8 쌍 중 7 (i), D2→SV8e (iv) | F23 | §10.7 |

## 2. 09-27 이후 결과 (RESULTS.md 미반영, 등록 문서 §6.1과 DECISIONS가 원본)

| 실험 | 등록 문서 | 기록된 결과 (DECISIONS 결과 줄 그대로 요약) | 그림 |
|---|---|---|---|
| ALD (annealed Langevin, 같은 V1 가중치) | [ALD16e4](../conf/results/review_next/NEXT_EXPERIMENTS_ALD16e4.md) | D2 C2: A1 (i) +1.54 dB, A2 (i) +1.82 dB, "루프 V1 이 ALD 파일럿 추정(오차 인지·plug-in 모두)보다 적게 실패". A1·A2 5/5 (i), A3 6 중 5 (i)·SV8e (iii) | — |
| 블록 안 도플러 | [DOP16e4](../conf/results/review_next/NEXT_EXPERIMENTS_DOP16e4.md) | D2 C2: ν=0.005 (i), ν=0.01 (iii). 측정 ν=0.005 5/6 (i), ν=0.01 3/6 (i) | F24, F25, F27, F28, F29 |
| 수신 배열 회전 | [ROT16e4](../conf/results/review_next/NEXT_EXPERIMENTS_ROT16e4.md) | D2 C2: 15° (i) 448:80, 30° (i) 529:124, "수신 배열 회전 15°·30° 모두에서 V1 이 b* 보다 적게 실패". 측정 15° 5/6 (SV8e (iv)), 30° 6/6 | F24, F25, F27, F28, F29 |
| 표류 학습 prior (B′) | [ROTMIX16e4](../conf/results/review_next/NEXT_EXPERIMENTS_ROTMIX16e4.md) | RB 15° (i) 406:81, 30° (i) 450:122. DD-15·DD-30 판정하지 못함. 판정 3: 세 각도 모두 13/13 (i) | F26 (a)(b) |
| 공간 비정상 S2v (C) | [S2V16e4](../conf/results/review_next/NEXT_EXPERIMENTS_S2V16e4.md) | 판정 1 (i) 202:32, R_b\* 0.603, ΔR −0.205 (S2 C6보다 낮음). 판정 2: 13/13 (i) | F26 (c) |
| DOP·ROT 보충 (등록 baseline 전부) | [SUPP16e4](../conf/results/review_next/NEXT_EXPERIMENTS_SUPP16e4.md) | 24/24 수용·무결성 OK. D2 C2 네 조건 모두 (A) "V1 이 𝔅 12 개 전부보다 적게 실패" (DOP ν=0.01 은 원 b\* (iii)). (ii) 0/288, k𝔅 = 12 21/24, "등록된 baseline 전부와 멀어진다" 18/24 | F24, F25, F27, F28, F29 |

2절의 기록 감사(Fable)는 모두 완료됐다: ALD·DOP·ROT·ROTMIX·S2V (`5b5c8f4a`, 전부 재현), SUPP16e4 (§6.2, 정정 없음).

## 3. 인용 주의 (RESULTS_snapshot §6 요약)

- 헤드라인 체크포인트는 best가 아니라 **last-EMA**로 평가됐다 (BEST_WEIGHTS_UNAVAILABLE).
- D2 헤드라인의 게이트 표기는 **"D1 형제 게이트 PASS 레시피 + 동일예산"**으로 읽는다.
- D3·SV8e·38.901·S2v 체크포인트는 **UNGATED**다. 이 결과는 측정이며 arm 판정이 아니다.
- 쓰면 안 되는 행과 정정된 수치는 `RESULTS_snapshot.md` §6에 있다.
