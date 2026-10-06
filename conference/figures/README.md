# 논문 그림 (IEEE ICC 2027 원고용)

이 폴더의 `F*.pdf` / `F*.png` 가 **논문에 넣는 그림**이다. `paper_fXX.py` 는 `conf/code/figure_fXX.py` (git 3f7c09ab) 의 논문판 사본이며, 데이터·계산·색·마커는 원본과 같고 **표시 문구만** 바꿨다 (그림 제목 없음, 패널 표시 (a)… 만; 내부 용어 없음 — [`TERMS.md`](TERMS.md); PDF 글꼴 TrueType). 각 스크립트는 기록 텍스트를 표준 출력으로 내며, 원본 `conf/figs/F*.txt` 와 대조됐다 (F17 은 스크립트 줄 번호 한 곳, F21 은 0 실패 이름 목록만 다름). 원본 (기록판) 그림과 캡션 메모 `.txt` 는 `conf/conference_plot/`.

다시 그리기 (CPU, 수 분): `cd ~/t2/conf && for f in ~/t2/conference/figures/paper_f*.py; do CUDA_VISIBLE_DEVICES= ~/miniforge3/envs/torch/bin/python -B $f > /dev/null; done`

## 공통으로 캡션에 넣을 것
- BLER 은 바깥 반복 16 회 뒤. 모든 학습 prior 와 GMM 은 같은 학습 집합 (동일예산; 따로 적지 않으면 N_train = 1.6×10^5). GMM 의 성분 수 K 는 검증 우도로 고른다.
- Perfect CSI = 같은 검출기·루프에 참 채널을 준 참조 (bound 아님).
- BLER 오차 막대는 95% Wilson; SNR 이득·격차 비율의 구간은 90% paired bootstrap (따로 적은 곳 제외). 실패 0 점은 로그 축에서 뺀다.
- 데이터셋: Sparse specular 외에는 모두 8×4 (N_r = 8, N_t = 4, 파일럿 4) — "따로 적지 않으면 8×4".

## 그림별 패널과 캡션 메모
| 그림 | 패널 | 캡션에 꼭 |
|---|---|---|
| F16 | (a) Sparse specular 8×4, BLER vs SNR: Gaussian prior, GMM prior, Proposed, Perfect CSI + SBL (in loop), SBL (pilot-only), OMP (pilot-only); 상자 "GMM prior → Proposed: −3 dB BLER 0.243 → 0.145, +1.41 dB at BLER 0.1 [90% CI 1.22, 1.64]". (b) −3 dB BLER vs N_train (1e4·4e4·1.6e5·3.2e5), 점 옆 K | 희소 3 개는 오차 막대 없음; (b) 는 NSCALE (6.4e5·1.28e6) 결과 뒤 점 추가 예정 |
| F17 | (a) Sparse specular 8×4, (b) Sparse specular 16×4 BLER vs SNR (N_train 1.6e5); (c) −3 dB 격차 비율 vs N_train, 두 배열 | (b) 곡선은 best-validation 체크포인트 (등록 판정 태그), (c) 의 16×4·1.6e5 점은 마지막 EMA 가중치 (0.815) — 캡션에 밝히거나 하나로 맞출 것; 점 이동 −0.45/0/+0.45 dB |
| F18 | (a) 8×4·파일럿 2·−3 dB (채움 = test, 속 빈 = development), (b) 같은 점의 반복별 BLER 과 격자 위 질의 비율, (c) development 보고점 (8×4 파일럿 2·0 dB, 파일럿 3·−6 dB) | arXiv 확장판용. a:b = 첫 arm 만 실패 : 둘째만 실패 (양측 정확 부호검정), n.s. |
| F19 | (a) BLER: Proposed (Tp=4) vs GMM prior (Tp=4/6/8), Perfect CSI (Tp=4); (b) BLER 0.1 의 SNR vs 파일럿 비율 (y 축 반전, 위가 좋음) | 8×4, T = 16; (b) 90% unpaired 구간; 상자의 Tp=6 −0.40 dB [95%], Tp=8 +0.38 dB [90%] (Holm 순서) |
| F20 | (a) 채널 모델별 SNR 이득 at BLER 0.1, (b) 3GPP UMi 28 GHz BLER, (c) −3 dB 격차 비율 | 3GPP mixed 는 속 빈 마커 (보조 점); 38.901 은 캡션에서 인용 |
| F21 | (a) Sparse specular 8×4, (b) Sparse specular 16×4, (c) Sparse specular, CN gains, (d) Clustered SV, (e) 3GPP UMi 28 GHz, (f) 3GPP mixed — 전 기준선 + 희소 3 개 | BiG-AMP 는 i.i.d. prior; OMP (pilot-only) 는 L = N 점에서 파일럿 LS 와 같다 (8×4 +15 dB, Clustered SV·UMi 28 GHz +3..+15, mixed +6..+15) |
| F22 | F21 과 같은 패널: 파일럿 전용 대 루프 | |
| F23 | (a) 같은 불일치에서 SNR 이득 (채움 = 불일치, 속 빈 회색 = 정합), (b) 불일치에 따른 SNR 손실 (파랑 Proposed, 주황 GMM prior); 행 = 학습 → 평가 모델 | 90% paired bootstrap; "insuff." = 검정력 부족 |
| F24 | Sparse specular 8×4, 정적·0° 학습 prior: (a) Doppler ν = 0.005, (b) ν = 0.01, (c) 배열 회전 15°, (d) 30° | |
| F25 | 같은 네 조건 (a)–(d) 에서 데이터셋 6 개의 −3 dB BLER: Proposed, Best baseline, Perfect CSI | Best baseline = GMM prior 와 기준선 12 개 중 −3 dB 실패가 가장 적은 것 |
| F26 | (a) 표류 학습 prior, 회전 15° (Sparse specular 8×4), (b) 30°, (c) 공간 비정상 (Sparse specular 16×4) | |
| F27 | (a) SNR 이득 at BLER 0.1, (b) −3 dB 격차 비율 — Static / Doppler / 회전 × 데이터셋 6 개 | Hollow: n.s. 또는 insuff.; Doppler ν = 0.01 의 Sparse specular 두 배열은 Perfect CSI 가 기준이 못 되어 (b) 에서 빠짐 |
| F28 | Sparse specular 16×4: (a) Doppler 0.005, (b) 0.01, (c) 회전 15°, (d) 30° | |
| F29 | 24 조건 × 기준선 13 개 라벨 격자 | 범례 4 칸 (Proposed fails more 는 0/288) |
| F30 | (a) Sparse specular, (b) 3GPP UMi 28 GHz: 격차 비율 vs N_r (8·16·32); (c) Sparse specular 32×4, (d) 3GPP UMi 28 GHz 32×4 BLER | (a)(b) 90% paired CI, 판정점 3 개의 합 |
| F31 | (a) 데이터셋별 기준선→Perfect CSI 격차 비율 (GMM prior + 희소 3 개), (b) Sparse specular 8×4 BLER (Proposed, GMM prior, 희소 3 개, Perfect CSI) | 행 중 16×4 표시가 없는 것은 8×4 |
| F32 | +6..+15 dB: (a) Sparse specular 8×4, (b) 16×4 — 속 빈 왼쪽 = 원 시험 시행 (n = 2560), 채움 오른쪽 = 새 시행 (n = 20480) | 보고 전용 보강 |

본문 6 쪽 후보는 `../PAPER_PLAN.md` §2 (F16, F30, 표 I, 필요시 F31/F20/F27).
