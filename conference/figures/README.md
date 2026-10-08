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
| F16 | (a) Sparse specular 8×4, BLER vs SNR: Gaussian prior, GMM prior, Proposed, Perfect CSI + SBL (in loop), SBL (pilot-only), OMP (pilot-only); 상자 "GMM prior → Proposed: −3 dB BLER 0.243 → 0.145, +1.41 dB at BLER 0.1 [90% CI 1.22, 1.64]". (b) −3 dB BLER vs N_train (1e4·4e4·1.6e5·3.2e5·6.4e5·1.28e6; 모두 last-EMA 가중치), GMM 점 옆 K (K = 4096 한 표시가 3.2e5–1.28e6 을 덮음) | 희소 3 개는 오차 막대 없음. (b) 의 6.4e5·1.28e6 = NSCALE (사전 등록, 실행 커밋 68d4d353; GMM K = 4096 = 격자 끝, D1 형제 게이트 PASS) — 판정용 `_best` 가중치 수는 그리지 않고 기록 출력에만 (3.2e5 와 같음). 1e4·4e4 는 게이트 FAIL 레시피 (예산 축 측정) — 캡션에 |
| F16a_col · F16b_col | **F16 의 한 단 판** (`paper_f16col.py`; 원고 Fig. 2 — 패널별 PDF 두 개를 `\subfloat` 로 쌓고 (a)·(b) 표시는 LaTeX 가 붙인다; 3.5 in = `\columnwidth` 를 1 배로). `F16a_col` 3.5×2.70 in = F16 (a) 의 일곱 곡선 + 위 0.62 in 띠에 그림 전체의 범례 (2 열, 틀 없음, 선+마커 손잡이). `F16b_col` 3.5×1.42 in = F16 (b). **F16 과 다른 점**: 수치 상자 없음 (같은 수치가 원고 IV-B 본문·표 I 첫 행); (a) y 아래 한계 2e-4 — FIGHS16e4 §1 의 3e-5 규칙의 예외, 실패 0 점이 없고 모든 점·막대 아래 끝이 2e-4 위일 때만 (지금 최저 점 6.348e-04, 막대 끝 3.710e-04: Perfect CSI, +15 dB; 조건이 깨지면 스크립트가 3e-5 로 두고 기록에 적는다); 글꼴 STIXGeneral (원고 본문·Fig. 1 이 Times); 패널 제목 없음; (a) x 눈금 = SNR 점; (b) Perfect CSI 는 일점쇄선 수평선 하나 (여섯 예산의 값·막대가 같음을 assert; 0.033984), GMM 점마다 K ("K = 512", 그 뒤 숫자만), x 축 이름은 원고 표기 N′ ([`TERMS.md`](TERMS.md) 의 한 단 판 예외), y 0–0.33; 선·마커 가늘게, x 눈금·축 이름 간격 좁힘 (아래 여백 0.36 in 고정), 두 파일의 y 축 이름을 같은 x 에. **수치는 다시 계산하지 않는다** — `paper_f16.main()` 을 저장만 막고 돌려 그 artist 의 x·y·막대 끝·색·마커·선 모양으로만 그린다. **assert**: 그 실행의 기록 출력 = `records/paper_f16.txt` (바이트 동일; 다르면 멈춤), K 여섯 개 = 기록의 `b*=kron` 줄, 다시 그린 x·y·막대 끝 = 참조 artist (rtol 1e-12), 두 파일의 축 왼쪽·오른쪽 끝이 같음 (36.00 / 247.68 pt), 글자 ≥ 7 pt, 모든 artist 가 캔버스 안, 범례가 띠 안, K 표시가 서로 안 겹침. 저장은 figsize 그대로 (tight 아님), PNG 300 dpi, TrueType. 기록 `records/paper_f16col.txt` | F16 과 같은 것 전부 (희소 3 개는 막대 없음, +6..+15 dB 는 20480 시행, 1e4·4e4 는 게이트 FAIL 레시피, 6.4e5·1.28e6 = NSCALE) + **범례는 (a) 파일에만 있고 (b) 에도 적용된다** — (b) 의 일점쇄선 수평선 = Perfect CSI (여섯 예산에서 같은 값), (b) 점 위 수 = GMM 성분 수 K; 상자를 뺐으므로 "−3 dB BLER 0.243 → 0.145, +1.41 dB at BLER 0.1 [90% CI 1.22, 1.64]" 는 본문·표 I 에서 |
| F17 | (a) Sparse specular 8×4, (b) Sparse specular 16×4 BLER vs SNR (N_train 1.6e5); (c) −3 dB 격차 비율 vs N_train, 두 배열 | (b) 곡선은 best-validation 체크포인트 (등록 판정 태그), (c) 의 16×4·1.6e5 점은 마지막 EMA 가중치 (0.815) — **사용자 결정 (2026-10-06 15:50 CDT): 그림은 그대로, 캡션에 밝힌다**. 캡션 예: "(b) best-validation checkpoint (registered decision run); (c) last-epoch EMA weights at every budget, as in Fig. 2(b)." F17 은 6 쪽 본문 계획 밖 — arXiv 확장판에 쓰면 (c) 에 NSCALE 점 추가; 점 이동 −0.45/0/+0.45 dB |
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
| F30top | F30 의 윗줄 (a)(b) 만, 같은 데이터·CI·그리기 (`paper_f30top.py`; 기록 텍스트 = F30 의 것에서 (c)(d) BLER 블록만 뺀 것, 같은 실행의 `paper_f30.main()` 출력과 assert): (a) Sparse specular, (b) 3GPP UMi 28 GHz — 격차 비율 vs N_r (8·16·32). `F30top_wide` = `figure*` 용 7.16×2.5 in, (a)·(b) 나란히; `F30top_col` = 한 단 3.5×4.3 in, (a) 위·(b) 아래 | F30 (a)(b) 와 같음: 90% paired CI, 판정점 3 개의 합; 데이터셋 이름은 그림에 없으니 캡션에. 32×4 BLER 곡선 (F30 (c)(d)) 은 없음. Sparse specular N_r = 32 의 CI [0.790, 0.832] 는 마커 지름 정도라 막대가 마커에 가려 끝 막대만 보임 (한 단 판에서 더 심함) — 필요하면 구간을 캡션·본문에 수치로 |
| F30one_col | **F30 윗줄의 한 단·한 패널 판** (`paper_f30one.py`; 원고 Fig. 3): 3.5×2.0 in, 한 축에 Sparse specular (채운 원·실선) 과 3GPP UMi 28 GHz (속 빈 네모·점선), 색은 둘 다 ink, 범례 오른쪽 아래 (틀 없음). **F30 (a)(b)·F30top 과 다른 점**: 축 하나 (패널 표시 없음 — 데이터셋은 범례로), 마커·선 작게, 글꼴 STIXGeneral; 점 위 수치는 위치·크기·색 그대로. **수치는 다시 계산하지 않는다** — `paper_f30.main()` 을 저장만 막고 돌려 (a)(b) 의 artist 에서 점·90% 막대·점 위 수치를 읽는다. **assert**: 읽은 값 = 그 실행 기록 텍스트의 R_dp 여섯 셀 = 기대값 (소수 셋째 자리; 다르면 멈춤), 다시 그린 점·막대 끝 = 참조 (rtol 1e-12), Sparse specular N_r = 32 의 막대 ([0.790, 0.832]) 가 마커 밖으로 보임 (막대 반 길이 2.28 pt ≥ 마커 반지름 + 테두리 반 + 0.3 = 2.20 pt; 안 되면 높이를 0.05 in 씩 2.2 in 까지), 점 위 수치·범례가 서로 안 겹침, 글자 ≥ 7 pt, 모든 artist 가 캔버스 안. 기록 출력은 `conf/figs/F30_scale_trend.txt` 와 대조 (동일). 저장은 figsize 그대로 (constrained, tight 아님), PNG 300 dpi, TrueType. 기록 `records/paper_f30one.txt` | F30 (a)(b) 와 같음: 90% paired CI, 판정점 3 개의 합. 데이터셋 이름이 범례에 있으므로 캡션은 패널로 부르지 않는다 (원고는 "Fig. 3" 으로만). 32×4 BLER 곡선 (F30 (c)(d)) 은 없음 |
| F31 | (a) 데이터셋별 기준선→Perfect CSI 격차 비율 (GMM prior + 희소 3 개), (b) Sparse specular 8×4 BLER (Proposed, GMM prior, 희소 3 개, Perfect CSI) | 행 중 16×4 표시가 없는 것은 8×4 |
| F32 | +6..+15 dB: (a) Sparse specular 8×4, (b) 16×4 — 속 빈 왼쪽 = 원 시험 시행 (n = 2560), 채움 오른쪽 = 새 시행 (n = 20480) | 보고 전용 보강 |

본문 6 쪽 후보는 `../PAPER_PLAN.md` §2 (F16, F30, 표 I, 필요시 F31/F20/F27).

## 실패 0 점 표기 (Perfect CSI 곡선이 끊겨 보이던 문제, 2026-10-06 16:44 CDT)

- 원인: 어떤 SNR 에서 한 블록도 실패하지 않으면 (0/2560) BLER 0 은 로그 축에 그릴 수 없어, 스크립트가 그 점을 빼고 이웃 점을 이었다 → F21 (b)(d), F22 (b)(d), F30 (c), F32 (b) 에서 Perfect CSI 곡선이 일찍 끝나거나 점을 건너뛰었다 (F17 은 이미 화살표 표기). 수치·기록 (.txt 의 'not drawn' 목록) 은 그대로다.
- 고침 (논문판 `paper_f21/f22/f30/f32.py`): 실패 0 점에서 곡선을 끊고 (이웃 점을 잇지 않음), Perfect CSI 의 실패 0 점은 95% Wilson 상한 (0/2560 → 1.5×10⁻³) 에서 아래로 향하는 짧은 화살표로 그린다 (F17 과 같은 표기; 추정값을 만들지 않음). 다른 방법의 실패 0 점은 곡선이 거기서 끝나거나 끊긴다.
- 캡션 문구 예: "Downward arrows: no block failure observed for perfect CSI (0/2560); the arrow starts at the 95% upper confidence bound (1.5×10⁻³). Other curves end or break at SNRs with no failed block."
- 기록판 그림 (`conf/conference_plot/`, `conf/figs/`) 은 아직 옛 표기 (점 생략) 다.

## Perfect CSI 곡선의 비단조 (재점검, 2026-10-06 16:59 CDT)

- 논문 그림 10 개의 Perfect CSI 곡선 32 개에서 BLER 이 SNR 과 함께 올라가는 칸을 모두 단측 Fisher 검정 (SNR 점마다 독립 시행 — `common.trial_rng` 의 시드에 SNR 이 들어간다).
- **정적 조건**: 올라가는 칸은 실패 수 1→2, 0→1, 2→3, 3→4, 2→4, 10→14 뿐이고 모두 p ≥ 0.27 — 이항 잡음 (2026-09-25 점검 "버그 없음" 과 같은 결론: 참 H·참 σ², 재생 비트 동일, rank-3 블록의 천천히 줄어드는 꼬리). 시행 8 배 (n = 20480) 인 F32 의 채운 점은 단조 (C2 66/36/16/13, C6 17/16/7/7) 다.
- **도플러 조건 (F24 (a) ν = 0.005, (b) ν = 0.01)**: 고SNR 에서 실제로 올라간다 (9 → 15 dB 실패 22 → 41, p = 0.011; 356 → 413, p = 0.014). 원인: 이 실험의 genie 는 블록 첫 심볼의 채널 H_0 만 안다 (runner meta "genie knows H_0 only") — 심볼마다 변하는 채널과의 차이가 잡음보다 커지는 고SNR 에서 오차가 바닥을 치고 늘어난다. 버그가 아니라 기준의 정의이며 등록 캐비엇 (ν = 0.01 의 genie ≥ V1 가드) 과 같은 사정.
- 캡션 문구 예 (F24): "Under Doppler, the perfect-CSI reference knows only the channel at the start of each block, so its BLER floors and rises at high SNR."
- **도플러 증가의 정량 근거 (2026-10-06 17:15 CDT, 작성자 계산 — 채널 생성기 `common.make_gen("D2","S2",8,4).sample_paths` 3000 개, `runner.doppler_rx` 와 같은 경로별 위상 회전, 블록 16 심볼 평균)**: genie 가 H_0 만 알 때 블록 안 채널 변화의 오차 전력 (안테나당, 단위 에너지 스트림) 은 ν = 0.005 에서 0.152 → 잡음 σ² 와 같아지는 SNR 8.2 dB (15 dB 에서 잡음의 4.8 배), ν = 0.01 에서 0.591 → 2.3 dB (15 dB 에서 18.7 배). 관측과 맞는다: ν = 0.005 의 genie 실패는 9 dB (22) 까지 줄다가 12·15 dB 에서 31·41 로 늘고, ν = 0.01 은 3–6 dB 부터 약 380–410 에 머문다. 수신기는 이 오차를 모른 채 잡음 σ² 만 가정하므로 SNR 이 높을수록 LLR 이 실제보다 확신에 차 (잡음 분산 불일치) 바닥 뒤 증가가 생긴다 — 모든 수신기 공통 (블록 고정 채널 가정), genie 만의 문제가 아니다.
- 캡션 문구 예 (F24, 정량 포함): "All receivers assume a block-constant channel; under Doppler the in-block channel change is an unmodelled error whose power exceeds the noise above about 8 dB (ν = 0.005) and 2 dB (ν = 0.01). The perfect-CSI reference knows only the channel at the block start, so its BLER floors and then rises with SNR."
- **D2 (sparse specular) 의 고SNR 평탄화**: 잔여 실패는 경로 3 개 블록 (rank H = 3 < N_t = 4) 이 대부분 — 천천히 줄어드는 꼬리이며 평평한 바닥이 아니다 (2026-09-25 점검, DECISIONS). 캡션 문구 예: "In the sparse-specular channel the residual high-SNR failures come mostly from three-path blocks (rank 3 < 4 streams), so all curves decay slowly there."
- 정적 그림의 표본 잡음은 고SNR 보강 (FIGHS16e4, n = 20480; 아래 절) 으로 다시 그렸다 — 범위 안 그림의 +6..+15 dB 점은 20480 시행이다. 범위 밖 그림 (F19, F30 (c)(d) 등, n = 2560) 에는 필요하면: "High-SNR perfect-CSI points rest on a few failures out of 2560 (independent trials per SNR); small non-monotone steps are within binomial noise."

## FIGHS16e4 merge (고SNR 점 n = 20480; 실행 끝 — 24 행 수용, 범위 안 그림 7 개 다시 그림)

- 등록 `conf/results/review_next/NEXT_EXPERIMENTS_FIGHS16e4.md` (v2; §0.1 출처, §1 그림 규칙; 보고 전용). 범위: F16 (a), F17 (a)(b), F20 (b), F21 (a)–(f), F22 (a)–(f), F24 (c)(d), F31 (b). 나머지 패널·그림은 그대로다 (F24 는 y 축을 공유하므로 (a)(b) 도 3×10⁻⁵ 부터, 데이터는 불변).
- 규칙 (공통 코드 `fighs_merge.py`): 곡선마다 −3/0/+3 dB = 원 raw (시험 시행 0..2559, n = 2560, 수 불변), +6/+9/+12/+15 dB = 새 시행 10000..30479 의 n = 20480 raw — `raw_FH<원 태그>`, 단 D2 8×4·16×4 의 V1·GMM·Gaussian·Turbo·BiG-AMP·Perfect CSI 는 HISNR `raw_HSB16e4k`·`raw_HSNR16`. 한 점 = 한 raw (합치지 않음); BLER = k/n 과 Wilson 막대는 점마다 자기 n; 막대는 원래 막대가 있던 곡선에만 (F16 (a) 네 곡선, F17 (a)(b), F20 (b)). 새 raw 의 수는 집계표 (`results/review_next/fighs_<TAG>.txt` — 수용된 태그에만 생김; HISNR 은 `hisnr_<TAG>.txt`) 와 assert.
- 실패 0 점: 곡선은 그 점에서 끊기고, Perfect CSI 는 그 점 n 의 95% Wilson 상한에서 아래 화살표 (n = 2560 → 1.5×10⁻³, n = 20480 → 1.9×10⁻⁴). y 축 아래 한계는 §1 대로 3×10⁻⁵ (n = 20480 점을 받는 패널; 1/20480 = 4.9×10⁻⁵ 가 보이게), F17 은 4×10⁻⁵ 그대로. F16 (a) 의 상자는 OMP 곡선을 비키도록 오른쪽으로 (축 비율 x 0.38 → 0.44).
- 기록 출력: 원래 기록 텍스트는 그대로 (원 raw 의 수) 두고, 끝에 "FIGHS16e4 merge" 블록 — 곡선마다 +6..+15 dB 의 k/n, 출처 raw, 그리고 BLER 이 SNR 과 함께 오르는 칸이 있으면 그 칸의 단측 Fisher p (§1; 평활·재실행·점 빼기 없음).
- 빠진 데이터: 필요한 새 raw·집계표·arm·SNR 이 없거나 n ≠ 20480 이면 스크립트는 그림을 저장하기 전에 멈춘다 (SystemExit, 어느 raw 가 빠졌는지 표시). `FIGHS_ALLOW_MISSING=1` 은 그 곡선만 원 raw 점으로 두고 stderr 에 WARNING, 기록 줄에 "FALLBACK … TEST RENDER ONLY" — 시험용이며 논문 그림이 아니다. `FIG_OUTDIR=<dir>` 은 pdf/png 저장 위치를 바꾼다 (시험 렌더가 이 폴더의 그림을 덮지 않게). F17 은 HISNR raw 로 이미 다 덮여 지금도 끝까지 돈다.
- 무효·미실행 태그 (§1 v2 S-4; 실행 로그의 `INVALID`·`SKIP`·`ABORT`): `FIGHS_N2560="<TAG> …"` 로 밝히면 그 태그에서 오는 곡선은 원 raw (n = 2560) 점을 전 구간 그대로 두고, 기록 줄에 "this curve is n = 2560 over the whole range", stderr 에 NOTE — **캡션에도 그 곡선을 적는다**. 수용된 태그 (집계표 있음) 를 넣으면 멈춘다. 재실행은 사용자 승인 뒤.
- 실행이 끝나고 24 태그가 수용된 뒤 (`logs/run_fighs16e4.log` 의 `FIGHS_DONE`): `cd ~/t2/conf && for f in 16 17 20 21 22 24 31; do CUDA_VISIBLE_DEVICES= ~/miniforge3/envs/torch/bin/python -B ~/t2/conference/figures/paper_f$f.py; done` (환경 변수 없이 — 무효·미실행 태그가 있으면 위의 `FIGHS_N2560` 만; `paper_f24.py` 는 F25·F26 도 같은 내용으로 다시 쓴다).
- 캡션 문장: "+6 to +15 dB points use 20 480 new trials per SNR (−3 to +3 dB: the original 2 560)". 실패 0 점이 n = 20480 점에 생기면 화살표 문구의 수를 바꾼다: "(0/20 480; the arrow starts at the 95% upper confidence bound, 1.9×10⁻⁴)". `FIGHS_N2560` 곡선이 있으면 덧붙인다 (예): "<curve>: original 2 560 trials at every SNR".
- **실행 결과** (등록 §6.1; `FIGHS_DONE ok=24 fail=0` 10-07 16:12 CDT, 중단·재개 1 회): 다시 그린 그림 F16 (a), F17 (a)(b), F20 (b), F21, F22, F24 (c)(d), F31 (b) (`paper_f24.py` 가 함께 다시 쓰는 F25·F26 은 PNG 바이트 동일). 기록 텍스트 = `records/paper_f<NN>.txt` (끝의 'FIGHS16e4 merge' 블록: 곡선별 +6..+15 dB 의 k/n, 출처 raw, 오르는 칸의 단측 Fisher p). 다시 그릴 때: `… paper_f$f.py > ~/t2/conference/figures/records/paper_f$f.txt`.
- 등록 §3 예측 (보고 전용; §6.1 의 채점표 그대로): 새 점추정이 원 raw (n = 2560) 의 95% Wilson 구간 안 — 281/304 = 0.9243 (✓); BiG-AMP 를 뺀 곡선 중 +6..+15 dB 에 오르는 칸이 있는 곡선 — 새 raw 0/70 (원 raw 재계산 9/70) (✓); Proposed 실패 ≤ GMM prior 실패 — 23/24 칸 (✓).
- **오르는 칸** (BLER 이 바로 아래 SNR 점보다 큰 칸; 기록 텍스트의 `rising:` 줄 그대로 — 실패 수는 +6/+9/+12/+15 dB, 각 20480 시행 중):
    - `paper_f21.txt`: R3-bigamp @16 1083/20480 1033/20480 1116/20480 1100/20480 (raw_HSB16e4k) rising: +9->+12 dB p=0.035
    - `paper_f21.txt`: R3-bigamp @16 1090/20480 1265/20480 1418/20480 1099/20480 (raw_HSNR16) rising: +6->+9 dB p=0.00011; +9->+12 dB p=0.0012
    - `paper_f21.txt`: R3-bigamp @16 2991/20480 2656/20480 2882/20480 2720/20480 (raw_FHD3B16e4) rising: +9->+12 dB p=0.00057
    - `paper_f21.txt`: R3-bigamp @16 181/20480 155/20480 120/20480 132/20480 (raw_FHSVB16e4) rising: +12->+15 dB p=0.24
    - `paper_f21.txt`: R5-genie @16 1/20480 0/20480 0/20480 0/20480 (raw_FHSVB16e4) rising: +3->+6 dB p=0.89
    - `paper_f21.txt`: R3-bigamp @16 6021/20480 5791/20480 6126/20480 6030/20480 (raw_FHU28B16e4) rising: +9->+12 dB p=0.00014
    - `paper_f21.txt`: R3-bigamp @16 6258/20480 5952/20480 6266/20480 6284/20480 (raw_FHMXB16e4) rising: +9->+12 dB p=0.00036; +12->+15 dB p=0.43
    - `paper_f22.txt`: R5-genie @16 1/20480 0/20480 0/20480 0/20480 (raw_FHSVB16e4) rising: +3->+6 dB p=0.89
    - `paper_f24.txt`: R3-bigamp @16 1159/20480 1047/20480 1205/20480 1146/20480 (raw_FHROTaB16e4k) rising: +9->+12 dB p=0.00033
    - `paper_f24.txt`: R3-bigamp @16 1362/20480 1299/20480 1418/20480 1397/20480 (raw_FHROTbB16e4k) rising: +9->+12 dB p=0.0096
  BiG-AMP (R3-bigamp) 외에는 Clustered SV 의 Perfect CSI +3 → +6 dB 한 칸 (0/2560 → 1/20480; 두 시행 집합이 만나는 칸) 뿐이다. 캡션 문구 예: "BiG-AMP (i.i.d. prior) reaches an error floor; its BLER is not monotone in SNR on the floor."
- **실패 0 점 (n = 20480)** (집계표 `fighs_<TAG>.txt`·`hisnr_<TAG>.txt` 에서; 태그 arm SNR): FHPILSV R5-genie +9/+12/+15 dB; FHPILSV V1-pilot +12/+15 dB; FHPILSV bstar-pilot +12/+15 dB; FHSPSV R5-genie +9/+12/+15 dB; FHSPSV SBL-loop +12/+15 dB; FHSPSV SBL-pilot +12/+15 dB; FHSVB16e4 M-ours-bstar +12/+15 dB; FHSVB16e4 M-ours-dscore-C-V1 +15 dB; FHSVB16e4 R0-pilot +15 dB; FHSVB16e4 R1-turbo +15 dB; FHSVB16e4 R2-ours-G +12/+15 dB; FHSVB16e4 R5-genie +9/+12/+15 dB. Perfect CSI 의 실패 0 점은 화살표 (0/20480 → 1.9×10⁻⁴, 0/2560 → 1.5×10⁻³), 다른 곡선은 그 점에서 끊긴다.
