# 학회 원고용 결과 모음

색인 기준: SEEDSNR16e4 결과·감사까지 (scale c689a935 의 결과·문서 파일을 main 에 사본; 갱신 2026-10-05 18:39 CDT). NSCALE (N-스케일링) 은 실행 중 — 결과는 10-06 CDT 예정. **원고 목표와 배치 계획은 [`PAPER_PLAN.md`](PAPER_PLAN.md)** (IEEE ICC 2027, 투고 마감 2026-10-16, 6 쪽; 저널판 없음). 이 폴더는 **색인과 사본**만 담는다. 원본은 다음과 같다.
- 수치: `conf/results/`
- 실행 기록: `docs/EXPERIMENTS.md`
- 결정: `conf/DECISIONS.md`
- 기여·리뷰어 질문 정리: `docs/paper/CONTRIBUTIONS.md` (개정 2, 같은 날)

수치와 라벨은 각 사전 등록 문서 §6과 DECISIONS의 결과 기록 줄에서 **그대로 옮겼다**. 해석은 넣지 않았다.

| 파일 | 내용 |
|---|---|
| [`conf/conference_plot/`](../conf/conference_plot/) | 학회용 그림 F16~F32 (pdf·png·txt)와 그림 색인 README. F24~F29 는 비정상 실험, F30~F32 는 10-03 추가분이다. `.txt` 에 수치 전부와 캡션용 캐비엇이 있다 |
| [`tables/`](tables/) | **표 I 초안** (본문용 한 단 `table1_compact.tex`, 전체판 `table1.tex`, 출처 `table1_sources.md`) — 상태는 `tables/README.md` |
| [`figures/`](figures/) | **논문 그림** (내부 용어 없음, 제목 없음, TrueType): F16–F32 와 F30top (F30 위 두 칸의 IEEE 크기판 — 두 단 7.16 in, 한 단 3.5 in); 용어집 `TERMS.md`, 캡션 메모 `README.md` |
| `RESULTS_snapshot.md` | `docs/RESULTS.md` 사본 (2026-10-05 18:39 CDT 판: §1~§22 전부 — §22 SEEDSNR16e4 포함). 사본은 RESULTS 갱신을 커밋할 때 다시 만든다 |

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

## 2. 09-27 이후 결과 (RESULTS.md §12~§17 에 반영; 원본은 등록 문서 §6.1 과 DECISIONS)

| 실험 | 등록 문서 | 기록된 결과 (DECISIONS 결과 줄 그대로 요약) | 그림 |
|---|---|---|---|
| ALD (annealed Langevin, 같은 V1 가중치) | [ALD16e4](../conf/results/review_next/NEXT_EXPERIMENTS_ALD16e4.md) | D2 C2: A1 (i) +1.54 dB, A2 (i) +1.82 dB, "루프 V1 이 ALD 파일럿 추정(오차 인지·plug-in 모두)보다 적게 실패". A1·A2 5/5 (i), A3 6 중 5 (i)·SV8e (iii) | — |
| 블록 안 도플러 | [DOP16e4](../conf/results/review_next/NEXT_EXPERIMENTS_DOP16e4.md) | D2 C2: ν=0.005 (i), ν=0.01 (iii). 측정 ν=0.005 5/6 (i), ν=0.01 3/6 (i) | F24, F25, F27, F28, F29 |
| 수신 배열 회전 | [ROT16e4](../conf/results/review_next/NEXT_EXPERIMENTS_ROT16e4.md) | D2 C2: 15° (i) 448:80, 30° (i) 529:124, "수신 배열 회전 15°·30° 모두에서 V1 이 b* 보다 적게 실패". 측정 15° 5/6 (SV8e (iv)), 30° 6/6 | F24, F25, F27, F28, F29 |
| 표류 학습 prior (B′) | [ROTMIX16e4](../conf/results/review_next/NEXT_EXPERIMENTS_ROTMIX16e4.md) | RB 15° (i) 406:81, 30° (i) 450:122. DD-15·DD-30 판정하지 못함. 판정 3: 세 각도 모두 13/13 (i) | F26 (a)(b) |
| 공간 비정상 S2v (C) | [S2V16e4](../conf/results/review_next/NEXT_EXPERIMENTS_S2V16e4.md) | 판정 1 (i) 202:32, R_b\* 0.603, ΔR −0.205 (S2 C6보다 낮음). 판정 2: 13/13 (i) | F26 (c) |
| DOP·ROT 보충 (등록 baseline 전부) | [SUPP16e4](../conf/results/review_next/NEXT_EXPERIMENTS_SUPP16e4.md) | 24/24 수용·무결성 OK. D2 C2 네 조건 모두 (A) "V1 이 𝔅 12 개 전부보다 적게 실패" (DOP ν=0.01 은 원 b\* (iii)). (ii) 0/288, k𝔅 = 12 21/24, "등록된 baseline 전부와 멀어진다" 18/24 | F24, F25, F27, F28, F29 |
| 정적 × 등록 baseline 13 개 (규칙 고정 사후 계산) | [STATIC16e4](../conf/results/review_next/NEXT_EXPERIMENTS_STATIC16e4.md) | D2 C2 (A) + "등록 baseline 전부(13 개)와 멀어진다"; k𝔅 = 12: D2 C2·D3·UMi28·MIX3; 새 48 라벨 (ii) 0; 감사 정정 없음 | RESULTS §16 |

2절의 기록 감사(Fable)는 모두 완료됐다: ALD·DOP·ROT·ROTMIX·S2V (`5b5c8f4a`, 전부 재현), SUPP16e4 (§6.2, 정정 없음), STATIC16e4 (§6.2, 정정 없음).

## 3. 09-30 이후 결과 (RESULTS.md §18~§21 에 반영; 원본은 등록 문서 §6.1 과 DECISIONS)

| 실험 | 등록 문서 | 기록된 결과 (등록 §6.1 라벨 그대로 요약) | 그림 | RESULTS 절 |
|---|---|---|---|---|
| 시드 강건성 2 (D3·SV8e·MIX3, a2·a3) | [SEEDS3_16e4](../conf/results/review_next/NEXT_EXPERIMENTS_SEEDS3_16e4.md) | D3 "시드 강건 (3/3 (i))"; MIX3 "시드 강건 (3/3 (i))" (보고 전용 부속 점); SV8e "판정하지 못함 (0/3 (i), 3 판정 못함)" (판정점 2 개라 결과 전에 정해짐). 예측 8/8 | — | §18 |
| 고SNR 보강 (D2 C2·C6, +6..+15 dB, 새 시행 n = 20480; **보고 전용**) | [HISNR16e4](../conf/results/review_next/NEXT_EXPERIMENTS_HISNR16e4.md) | 라벨 없음. V1 실패 C2 111/59/39/23, C6 29/24/20/13 (/20480), 8 칸 모두 b\* 보다 적다. 점추정 16/16 이 원 태그 95% Wilson 안. genie 실패의 대부분은 L = 3 블록이다 | F32 | §19 |
| 정적 6 데이터셋 × 희소 baseline 3 개 (SBL-loop, SBL-pilot, OMP-pilot) | [SPARSE16e4](../conf/results/review_next/NEXT_EXPERIMENTS_SPARSE16e4.md) | D2 C2 (A) "V1 이 희소 baseline 3 개(SBL-loop, SBL-pilot, OMP-pilot) 전부보다 적게 실패" (SBL-loop 588:72). 새 18 라벨 (i) 17·(iv) 1 (SV8e SBL-loop)·(ii) 0. "등록된 baseline 전부(16 개, 희소 baseline 포함)와 멀어진다": D2 C2·D3·UMi28·MIX3. 예측 6/6 (1 채점 안 함) | F31 | §20 |
| 배열 규모 축 Nr 8 → 16 → 32 (D2·UMi28; UNGATED 배열 규모 축 측정) | [SCALE16e4](../conf/results/review_next/NEXT_EXPERIMENTS_SCALE16e4.md) | 1차 (Holm m = 2): D2 (T+) ΔR +0.302 [95% +0.254, +0.355] + G_D2 + "[운영점 정합 강건]" "[K 상한 강건]"; UMi28 (T+) ΔR +0.282 [90% +0.232, +0.335] + G_UMi28 + "[운영점 정합 강건]" "[K 상한 민감: 외삽 불가]". 2차: "D2 16→32 판정하지 못함", "UMi28 단조 증가". 새 3 셀 표 B (i) 3/3, 𝔅 36 (i); "전부(13 개)" UMi28 C6·C9 (D2 C9 불충족). 예측 적중 13·빗나감 5 | F30 | §21 |
| 시드 강건성 3 (Nr 16/32: UMi28 C6·C9, D2 C9; a2·a3) | [SEEDSNR16e4](../conf/results/review_next/NEXT_EXPERIMENTS_SEEDSNR16e4.md) | 6 시드 태그 표 B 6/6 (i); UMi28 C6 "시드 강건 (3/3 (i))", UMi28 C9 "시드 강건 (3/3 (i))", D2 C9 "시드 강건 (3/3 (i); a3 = §3d fb2)" (선례 규칙 병기 "판정하지 못함 (2/3 (i), 1 판정 못함)", 보고 전용); (S2) SCALE16e4 1차 (T+) 가 C9 시드 교체에서 유지 2/2 (D2·UMi28), (S3) UMi28 S1 유지 2/2; R_dp 산포 0.023 / 0.014 / 0.017 | — (F30 에 시드 미표시) | §22 |

3절의 기록 감사(Fable)도 모두 완료됐다. 수치·라벨·예측 채점 오류는 모두 0 이다: SEEDS3 (§6.2, 위생 정정 6), HISNR (§6.2, 327 검사, 위생 정정 3), SPARSE (§6.2, 2153 검사, 위생 정정 3), SEEDSNR (§6.2, 540 + 99 검사, 위생 정정 3 + 주 세션 결정 1; 폴더 `prereg_audit_2026-10-04/`), SCALE (§6.2, 474 검사, 위생 정정 3 + 주 세션 결정 1). 감사 폴더는 `conf/results/review_next/prereg_audit_2026-09-30/`, `_2026-10-01/`, `_2026-10-03/` 이다.

## 4. 인용 주의 (RESULTS_snapshot §6 요약 + 3절 등록의 캐비엇)

- 헤드라인 체크포인트는 best가 아니라 **last-EMA**로 평가됐다 (BEST_WEIGHTS_UNAVAILABLE).
- D2 헤드라인의 게이트 표기는 **"D1 형제 게이트 PASS 레시피 + 동일예산"**으로 읽는다.
- D3·SV8e·38.901·S2v 체크포인트는 **UNGATED**다. SCALE16e4 의 새 셀(D2 C9, UMi28 C6·C9)도 UNGATED 다. 이 결과는 측정이며 arm 판정이 아니다.
- 쓰면 안 되는 행과 정정된 수치는 `RESULTS_snapshot.md` §6에 있다.
- STATIC16e4 는 **"규칙 고정 사후 계산"**이다. 사전 등록이라 부르지 않는다. SPARSE16e4 의 "16 개" 문장에 든 정적 라벨 8 개가 여기서 왔다.
- SPARSE16e4: ρ 는 격자 끝 16 이다(확장 규칙 2 회째를 비용으로 중단). OMP-pilot 은 L = N 점에서 파일럿 LS 와 같아, 그 점은 "희소 복원"이라 부르지 않는다. SBL-loop 의 n_em 은 파일럿 개발 NMSE 로 골랐다. 사전은 on-grid DFT 다.
- SCALE16e4: R 은 b\* 대비 **상대 통계량**이다. 절대 격차를 함께 인용한다. (T±) 문장에는 G_d 와 한정어를 반드시 붙인다. "모든 baseline"은 쓰지 않고 "등록된 13 개"로만 쓴다 (희소 arm 없음). D2 의 (T+) 는 등록 때 이미 예상된 결과였다. 설계 선택은 사용자 위임 아래 했고 항목별 승인이 아니다.
- HISNR16e4 는 **보고 전용**이다. 원 태그와 합치지 않고, 등록 판정을 대신하지 않는다.
- SEEDS3 의 SV8e 라벨은 결과 전에 정해진 사실이다. MIX3 는 보고 전용 부속 점이다.
- SEEDSNR16e4: D2 C9 a3 는 원 시행 발산 → 등록 §3d fb2 (클리핑) 가중치; 라벨에 한정어가 붙고 선례 규칙 라벨은 보고 전용으로 병기. 봉인된 fb3 학습 로그 열람 공개 (선택 영향 없음) 는 등록 §5 부록·§6.1.7.
- 캐비엇 전부의 목록은 `docs/paper/CONTRIBUTIONS.md` §6 항목 11–17 과 각 등록 §6.1 끝 "편차·캐비엇"에 있다.
