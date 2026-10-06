# 표 I 출처 (table1.tex · table1_compact.tex)

- 작성: 2026-10-06 15:19 KST (= 10-06 01:19 CDT), Opus 5.5 서브에이전트. 기준: main HEAD `5f02c87e` — 아래 인용 파일은 모두 이 커밋에서 깨끗하다 (`git status` 무변경 확인). 줄 번호는 이 판 기준이다.
- 규칙: 표의 수치는 기록에서 **그대로** 옮겼다. 재계산은 없다. 기록 행을 셈으로 읽은 곳(열거·뺄셈)만 아래 "작성자 산술" 로 표시했다. 해석 문장은 표에 넣지 않았다.
- 파일
  - `table1.tex` — 전체판, `table*` (2 단 폭). \footnotesize 로 1 단에 들어가지 않는다. 측정 (IEEEtran 10pt, Times, tectonic): 폭 516 pt, 표+주석 높이 약 621 pt = 쪽 높이 672 pt 의 0.92.
  - `table1_compact.tex` — 1 단판, `table`. 측정: tabular 폭 249.8 pt (단 폭 252 pt; T1·OT1 둘 다), 표+주석 높이 약 595 pt = 단 높이의 0.89.
  - 시험 컴파일: `/tmp/claude-1005/-home-HTJ-t2/6cbef450-8bb7-430d-b07a-4c32854f5588/scratchpad/table1_test/` (`test_compact2.tex`, `test_full.tex`, 측정용 `meas_*.tex`·`mw_*.tex`). tectonic 0.17 (XeTeX) 에 `\usepackage[T1]{fontenc}` 를 넣어 Times 글꼴 폭으로 쟀다 (넣지 않으면 XeTeX 가 Latin Modern 으로 대체해 폭이 달라진다). 오류·Overfull hbox 없음. 쪽 렌더링 도구(pdftoppm 등)가 없어 눈으로 보지는 못했고, PDF 텍스트를 뽑아 내용·순서만 확인했다.
- 약칭 (경로는 `/home/HTJ/t2` 기준)
  - **R** = `docs/RESULTS.md`
  - **SP** = `conf/results/review_next/pairB_SPB16e4k.txt` (SPARSE16e4 실행, git 02dafa1c; 헤드라인 셀의 16 개 비교 전부)
  - **ST** = `conf/results/review_next/pairB_STB16e4k.txt` (STATIC16e4, git 2139f082). ST:5–95 는 SP:5–95 와 바이트 동일 (13 개 블록; `diff` 로 확인)
  - **STd** = `conf/results/review_next/NEXT_EXPERIMENTS_STATIC16e4.md`
  - **SU** = `conf/results/review_next/NEXT_EXPERIMENTS_SUPP16e4.md`
  - **S1** = `conf/results/review_next/NEXT_EXPERIMENTS_SEEDS16e4.md`, **S3** = `…/NEXT_EXPERIMENTS_SEEDS3_16e4.md`, **SN** = `…/NEXT_EXPERIMENTS_SEEDSNR16e4.md`
  - **F20** = `conf/conference_plot/F20_channel_models.txt`
  - **T** = `conference/figures/TERMS.md` (용어 대응)
  - 표 위치: **F** = table1.tex, **C** = table1_compact.tex

## 0. 용어 대응 (TERMS.md 만 사용)

| 표 문구 | 내부 이름 | T 줄 |
|---|---|---|
| Proposed (diffusion prior), proposed | V1, `M-ours-dscore-C-V1` | T:9 |
| GMM prior | b\*, `M-ours-bstar` | T:12 |
| GMM prior, scalar site | `M-ours-bstar-scalar` | T:13 |
| GMM prior ($K=32$) | `M-ours-gmm32` | T:14 |
| GMM prior, pilot-only | `bstar-pilot` | T:20 |
| Gaussian prior | `R2-ours-G` | T:15 |
| Pilot-only LMMSE | `R0-pilot@1` (1-pass 판독) | T:16 |
| Turbo LMMSE receiver | `R1-turbo` | T:17 |
| BiG-AMP | `R3-bigamp` | T:18 |
| SC-VAMP / SC-VAMP (LLR) | `R4-scvamp` / `R4-llr` | T:19 |
| Proposed prior, pilot-only | `V1-pilot` | T:21 |
| Annealed Langevin (plug-in) / (error-aware) | `ALD-pilot` / `ALDv-pilot` | T:22 |
| SBL (in loop) / SBL (pilot-only) / OMP (pilot-only) | `SBL-loop` / `SBL-pilot` / `OMP-pilot` | T:23 |
| Perfect CSI | R5-genie | T:25 |
| Sparse specular / Sparse specular, CN gains / Clustered SV (Saleh–Valenzuela) / 3GPP UMi 28 GHz / 3GPP mixed | D2 / D3 / SV8e / UMi28 / MIX3 | T:31–35 |
| $8\times4$ / $16\times4$ / $32\times4$ | C2 / C6 / C9 | T:36 |
| Doppler $\nu$, rotation | DOP ν, ROT θ | T:39 |
| Gain [dB] = SNR gain at BLER 0.1 | SNR@0.1 격차 (X − V1) | T:47 |
| $R$, $R_X$ = fraction of the GMM- (baseline-) to-perfect-CSI gap closed | R (−3 dB), R_X, R_dp | T:48 |
| $K$ | kron K / full K | T:50 |
| $\surd$ / n.s. / insuff. | (i) / (iii) / (iv) | T:54–55, T:70 |
| proposed fails more | (ii) | T:70 |
| best baseline | X\* | T:64 |
| UMi, mixed, CN gains, clustered SV (주석 안의 줄임) | 위 이름의 줄임 (내부 코드 아님) | — |

표 파일에 내부 코드(V1, b\*, R5, genie, D2…, C2…, (i)…(iv), POWERED, UNGATED, Holm, ALD, X\* 등)가 없음을 grep 으로 확인했다.

## 1. (A) 등록 baseline 16 개 — sparse specular $8\times4$ (D2 C2, 태그 B16e4k, N_train 1.6e5)

공통: 각 블록은 `X -> M-ours-dscore-C-V1` 표 B. 라벨 = `POWERED=True … -> (i)` 줄, Gain = `SNR@0.1 gap (X minus V1)` 줄, a:b = `pooled` 값, $R_X$ = `R_X -3 dB (primary)` 줄 (보고 전용), Non-st. = SU §6.1 arm 별 표 (SU:184–189). 16 개 요약: SP:119 `SUMMARY registered baselines 16 (b* + 𝔅 15): (i) 16, (ii) 0, not decided 0`; R §20 :1339 (`16 · 0 · 0`), :1346.

| 표 행 (F·C) | Gain [dB] (90% CI) | Label | a:b | $R_X$ (90% CI) [F 만] | Non-st. √/n.s./insuff. (C 는 √ 수/24) | 내부 이름 | 출처 |
|---|---|---|---|---|---|---|---|
| GMM prior | +1.41 (+1.22, +1.64) | √ (3/3 점) | 454:78 | 0.470 (0.427, 0.512) | 19/3/2 | M-ours-bstar (kron K=1024) | SP:5–11; ST:5–11; R §1.3 :82 (454:78, +1.41 [+1.22, +1.64]); R §16 :1189, §20 :1339 (R 0.470 [0.427, 0.512]); STd:88; SU:189 (`19 (i), 3 (iii), 2 (iv)`) |
| GMM prior, scalar site | +1.58 (+1.37, +1.82) | √ | 498:73 | 0.502 (0.460, 0.542) | 23/0/1 | M-ours-bstar-scalar | SP:12–18; STd:89; SU:185 (`23 (i), 1 (iv)`) |
| GMM prior ($K=32$) | +1.76 (+1.53, +2.02) | √ | 565:78 | 0.517 (0.477, 0.557) | 23/0/1 | M-ours-gmm32 | SP:19–25; STd:90; SU:186 |
| GMM prior, pilot-only | +1.99 (+1.78, +2.21) | √ | 814:41 | 0.681 (0.654, 0.709) | 24/0/0 | bstar-pilot | SP:68–74; STd:97; SU:184 (`각 24 (i)`) |
| Gaussian prior | +2.29 (+2.03, +2.54) | √ | 778:69 | 0.622 (0.590, 0.656) | 24/0/0 | R2-ours-G | SP:40–46; STd:93; SU:184 (R2 는 인용 라벨, SU:5) |
| Pilot-only LMMSE | +8.25 (+7.78, +8.82) | √ | 832:0 | 0.845 (0.830, 0.860) | 24/0/0 | R0-pilot@1 | SP:26–32 (판독 @1: SP:4); STd:91; SU:184 |
| Turbo LMMSE receiver | +4.53 (+4.24, +4.85) | √ | 724:12 | 0.782 (0.762, 0.802) | 24/0/0 | R1-turbo | SP:33–39; STd:92; SU:184 |
| BiG-AMP | +4.54 (+4.25, +4.86) | √ | 461:4 | 0.782 (0.762, 0.802) | 24/0/0 | R3-bigamp | SP:47–53; STd:94; SU:184 |
| SC-VAMP | +8.06 (+7.46, +8.77) | √ | 759:2 | 0.807 (0.790, 0.825) | 24/0/0 | R4-scvamp | SP:61–67; STd:96; SU:184 |
| SC-VAMP (LLR) | ≥ +17.23 | √ | 1623:2 | 0.867 (0.854, 0.879) | 24/0/0 | R4-llr | SP:54–60 (SP:57 `>= +17.23 dB (R4-llr never reaches 0.1 on the grid)`); STd:95; SU:184 |
| Proposed prior, pilot-only | +0.92 (+0.77, +1.07) | √ (2/3 점) | 347:51 | 0.473 (0.432, 0.513) | 21/2/1 | V1-pilot | SP:75–81 (SP:77 `second arm fewer at 2/3`); STd:98; R §10.6 :1069 (P1 (i) 2/3 · +0.92 [+0.77, +1.07]); SU:188 (`21 (i), 2 (iii), 1 (iv)`) |
| Annealed Langevin (plug-in) | +1.82 (+1.62, +2.05) | √ | 678:54 | 0.619 (0.585, 0.651) | 24/0/0 | ALD-pilot | SP:82–88; STd:99; R §12 :1127 (A2 +1.82 [+1.62, +2.05]); SU:184 |
| Annealed Langevin (error-aware) | +1.54 (+1.37, +1.74) | √ | 644:50 | 0.629 (0.597, 0.659) | 23/0/1 | ALDv-pilot | SP:89–95; STd:100; R §12 :1127 (A1 +1.54 [+1.37, +1.74]); SU:187 |
| SBL (in loop) | +1.86 (+1.64, +2.10) | √ | 588:72 | 0.540 (0.503, 0.579) | not run / -- | SBL-loop | SP:96–102; R §20 :1314 |
| SBL (pilot-only) | +2.12 (+1.90, +2.35) | √ | 811:52 | 0.665 (0.635, 0.694) | not run / -- | SBL-pilot | SP:103–109; R §20 :1315 |
| OMP (pilot-only) | +3.24 (+2.99, +3.51) | √ | 451:20 | 0.697 (0.669, 0.723) | not run / -- | OMP-pilot | SP:110–116; R §20 :1316 |

- (A) 제목 "label √ for all 16 / 16 of 16": SP:119, R §20 :1339·:1346 (주 라벨 (A) "V1 이 희소 baseline 3 개 … 전부보다 적게 실패"), STd:71 (𝔅 12 전부 (A)).
- "not run" (희소 3 개의 비정상 조건): SU §1 의 𝔅 12 에 희소 arm 이 없다 (SU:32); 희소 arm 은 정적 6 데이터셋에서만 실행 (R §20 :1308).
- 작성자 산술 (열거): Non-st. 의 n.s.·insuff. 0 은 SU:184–188 행이 (iii)·(iv) 를 따로 적지 않은 경우의 0 이다 (예: `23 (i), 1 (iv)` → n.s. 0).

## 2. (B) 채널 모델, $8\times4$, proposed vs GMM prior

| 표 행 | Gain (90% CI) | Label | a:b [F 만] | $R$ (90% CI) (C 는 점추정만) | √ vs 16 | 내부 이름 | 출처 |
|---|---|---|---|---|---|---|---|
| Sparse specular | +1.41 (+1.22, +1.64) | √ | 454:78 | 0.470 (0.427, 0.512) | 16/16 | D2 C2 B16e4k (D1 형제 게이트 PASS 레시피) | R §10.1 :1007; R §16 :1189; R §20 :1339; F20:3 |
| Sparse specular, CN gains | +1.41 (+1.19, +1.67) | √ | 393:67 | 0.367 (0.335, 0.399) | 16/16 | D3 (D3B16e4), UNGATED | R §10.1 :1008; R §10.2 :1023; R §20 :1340; F20:4 |
| 3GPP UMi 28 GHz | +0.60 (+0.33, +0.87) | √ | 161:73 | 0.062 (0.033, 0.089) | 16/16 | UMi28 (U28B16e4), UNGATED | R :1009; R :1024; R :1342; F20:6 |
| 3GPP mixed | +0.98 (+0.68, +1.31) | √ (보고 전용) | 198:71 | 0.090 (0.062, 0.117) | 16/16 | MIX3 (MXB16e4), UNGATED, 보고 전용 부속 점 | R :1010; R :1026 (`MIX3 (보고)`); R :1343; F20:7 |
| Clustered SV (Saleh–Valenzuela) | +0.25 (+0.16, +0.33) | insuff. | 148:72 | 0.143 (0.095, 0.188) | 11/16 (5 insuff.) | SV8e (SVB16e4), UNGATED; 판정점 2 개 → (iv) | R :1011; R :1025; R :1341; F20:5 |

- √ vs 16: R §20 :1339–1343 의 `16 개 (b* + 𝔅 15)` 칸 `(i) · (ii) · 판정 못함` = `16 · 0 · 0` (네 데이터셋), SV8e `11 · 0 · 5`. 작성자 산술 (열거): SV8e 의 5 개가 모두 (iv) 라는 것은 같은 줄 :1341 의 "(i) 아닌 X" 목록 (b\*, b\*-scalar, gmm32, V1-pilot, SBL-loop 모두 (iv)) 에서 읽었다.
- C 의 (B) 아래 한 줄 "Vs. the 16 baselines: √ 16/16 in rows 1–4; 11/16 (5 insuff.) in row 5" 도 같은 출처.

## 3. (C) 비정상 조건 (24 조건 × GMM prior + 등록 baseline 12)

| 표 행 | 값 | 내부 이름 | 출처 |
|---|---|---|---|
| Proposed vs GMM prior √/n.s./insuff./fails more | 19/3/2/0 (C 는 19/3/2) | M-ours-bstar 원 라벨 24 조건 | SU:189 (`19 (i), 3 (iii), 2 (iv)`); R §13 :1143–1148 (조건별 라벨 격자) |
| √ vs GMM per condition type (F 만) | 5/3/5/6 (ν 0.005 / ν 0.01 / 15° / 30°, 각 6 중) | 측정 라벨 (i) 수 | R §13 :1150 (`ν = 0.005 5/6, ν = 0.01 3/6, 15° 5/6, 30° 6/6`) |
| Conditions with √ vs each of the other 12 | 21/24 | k𝔅 = 12 인 조건 | SU:178; R §15 :1180 |
| Labels with the proposed failing more (24 × 12) | 0/288 | (ii) 수, 표 B 288 라벨 | SU:177; R §15 :1180 |
| √ vs all 13 and R vs best baseline > 0 (19 eligible) | 18/24 | "등록된 baseline 전부와 멀어진다" 문장 조건 (가능 19 중 18) | SU:179; R §15 :1180 |
| Sparse specular 8×4: √ vs each of the 12 | 4/4 | D2 C2 네 조건 주 라벨 (A) "V1 이 𝔅 12 개 전부보다 적게 실패" | SU:122–127; R §15 :1180 |

- 작성자 산술: GMM 의 "fails more 0" = 24 − 19 − 3 − 2 = 0 (SU:189 는 (i)·(iii)·(iv) 만 적는다; R §13 격자에도 (ii) 없음).
- 조건 정의: 정적·0° 학습 prior 를 재학습 없이 비정상 시행에 적용 (R §13 :1139); 6 설정 = D2 C2, D2 C6, D3, SV8e, UMi28, MIX3 (R §13 :1141–1148, §15 :1173); 𝔅 12 (SU:32); 문장 조건 (SU:38).

## 4. (D) 확산 학습 시드 (proposed vs GMM prior)

| 표 행 | 시드 라벨 | Gain, seeds 1/2/3 [F 만] | $R$, seeds 1/2/3 [F 만] | 내부 이름 | 출처 |
|---|---|---|---|---|---|
| Sparse specular, 8×4 | 3/3 | +1.41 / +1.44 / +1.48 | 0.470 / 0.478 / 0.463 (R −3 dB) | D2 C2 a1·a2·a3, "시드 강건 (3/3 (i))" | R §10.5 :1052–1054, :1059; S1:88–90 (R(−3 dB) 열), S1:93 |
| Sparse specular, CN gains, 8×4 | 3/3 | +1.41 / +1.42 / +1.46 | 0.367 / 0.337 / 0.343 | D3 a1·a2·a3, "시드 강건 (3/3 (i))" | R §18 :1210–1212, :1222; S3:78–80, S3:89 |
| 3GPP UMi 28 GHz, 8×4 | 3/3 | +0.60 / +0.74 / +0.74 | 0.062 / 0.059 / 0.036 | UMi28 a1·a2·a3, "시드 강건 (3/3 (i))" | R §10.5 :1055–1057, :1059; S1:106–108, S1:112 |
| 3GPP mixed, 8×4 | 3/3 (보고 전용) | +0.98 / +0.72 / +0.83 | 0.090 / 0.078 / 0.085 | MIX3 a1·a2·a3, "시드 강건 (3/3 (i))" (보고 전용 부속 점) | R §18 :1216–1218, :1222; S3:84–86, S3:91 |
| Clustered SV, 8×4 | 0/3 (3 insuff.) | +0.25 / +0.24 / +0.30 | 0.143 / 0.127 / 0.148 | SV8e, "판정하지 못함 (0/3 (i), 3 판정 못함)" (결과 전에 정해짐, 보고 전용) | R §18 :1213–1215, :1222; S3:81–83, S3:90 |
| 3GPP UMi 28 GHz, 16×4 | 3/3 | +1.41 / -- / -- | 0.287 / 0.269 / 0.292 (R_dp) | UMi28 C6, "시드 강건 (3/3 (i))" | 라벨 R §22 :1582, SN:241; R_dp R §22 :1566–1568, SN:225–227; 시드 1 Gain R §21.3 :1453 |
| 3GPP UMi 28 GHz, 32×4 | 3/3 | +2.29 / -- / -- | 0.432 / 0.443 / 0.446 (R_dp) | UMi28 C9, "시드 강건 (3/3 (i))" | 라벨 R :1583, SN:242; R_dp R :1569–1571, SN:228–230; Gain R §21.3 :1454 |
| Sparse specular, 32×4 | 3/3 (주석: 시드 3 폴백) | +2.99 / -- / -- | 0.811 / 0.813 / 0.796 (R_dp) | D2 C9, "시드 강건 (3/3 (i); a3 = §3d fb2)" | 라벨 R :1584, SN:243; R_dp R :1572–1574, SN:231–233; Gain R §21.3 :1452 |

- "--" (시드 2·3 의 Gain): 시드 태그는 a1 판정점 3 점만 돌렸고 V1 SNR@0.1 은 재지 않았다 (R §22 :1560, :1597).
- 시드 3 폴백 (32×4 sparse specular): 원 시행 발산 → 등록 §3d 사다리 시행 2 (fb2, 클리핑 1.0) (R §22 :1560). 선례 규칙 라벨 "판정하지 못함 (2/3 (i), 1 판정 못함)" 은 보고 전용 (R §22 :1584; SN:243).
- 시드 규칙 (seed 1 = 보고용, BLER 뒤에 고르지 않음): R §10.5 :1048; R §18 :1206; S1:33.

## 5. 주석의 정의·조건 출처

| 주석 내용 | 출처 |
|---|---|
| 공통 조건: N_train 1.6e5 (동일예산), BLER@16 (16 회), n = 2560/SNR | R §1 :15, :20–21, :46; `conference/README.md`:16–19; R §10 :1001 |
| SNR 격자 −3:3:15 dB | SP:123 (`-3 +0 +3 +6 +9 +12 +15 dB`); 32×4 격자 −12..+6 dB: R §21.4 :1495, :1497 |
| 판정점: 앵커 BLER ∈ [0.005, 0.9] 인 격자점 중 0.1 에 가까운 3 점 | R §1 :22; `conf/code/analysis.py`:405–412 |
| √/n.s./insuff. 규칙: p < 0.05 인 점이 ≥ 2 → (i)/(ii), 아니면 (iii); 판정점 3 개 미만 또는 불일치 ≥ 6 인 점이 2 개 미만 → (iv) | `conf/code/pair_baselines.py`:87–92; `conf/code/analysis.py`:418–419 (MIN_DISC = 6); `conf/08_SPEC_analysis.md`:46; 라벨 뜻 `conference/README.md`:20 |
| n.s./insuff. = "not decided", "no difference" 아님 | `docs/paper/CONTRIBUTIONS.md`:15; R §6.3 :887 |
| Gain 정의 (X − V1, > 0 이면 proposed 쪽 이득), 90% paired bootstrap, 보고 필드 | `conference/README.md`:21; T:47; R §1.3 :82 열 이름; CONTRIBUTIONS:60 ("보고 필드로") |
| a:b 정의 | R §1.3 :84 |
| R 정의·상대 통계량 | `conf/code/pair_baselines.py`:96–100; R §21 :1388 ("R 은 상대 통계량"); T:48; 16×4/32×4 는 판정점 합 R_dp (R §22 :1562) |
| Perfect CSI = 같은 EP 검출기·BCJR 루프에 참 H, bound 아님 | CONTRIBUTIONS:13; R §1.2 :69; T:25 |
| 품질 게이트 밖 (UNGATED) 체크포인트 = 측정, arm 판정 아님; 헤드라인은 D1 형제 게이트 PASS 레시피 | R §10 :1001; R §21 :1388; `conference/README.md`:68–69; R §1 :30 |
| 3GPP mixed = 보고 전용 부속 점 | R §10.1 :1010; S3:91; `conference/README.md`:75 |
| "post-hoc, fixed rule" (규칙 고정 사후 계산): 13 개 정적 라벨 중 새로 계산된 8 개 (b\*-scalar, gmm32, R0-pilot@1, R1, R3, R4-llr, R4-scvamp, bstar-pilot), 인용 4 개 (R2 analysis 표 B, V1-pilot = PILOT16e4 P1, ALD-pilot = A2, ALDv-pilot = A1) + b\* (각 a1 등록), 작성자가 곡선을 본 뒤 | STd:5, STd:131; R §16 :1185; `conference/README.md`:71; PAPER_PLAN:20 |
| 개별 사전 등록: GMM (Stage C 헤드라인), ALD (ALD16e4 "사전 등록 v2"), V1-pilot (PILOT16e4 "사전 등록 v2"), 희소 3 개 (SPARSE16e4 "사전 등록 v2") | R §1.3 :73–82, CONTRIBUTIONS:60 ("사전 등록된 3점 짝지음 부호검정"); ALD16e4 제목 줄 :1; PILOT16e4 제목 줄 :1; R §20 :1308 |
| 희소 baseline 캐비엇: on-grid 오버샘플 2-D DFT 사전, ρ = 16 격자 끝; SBL-loop n_em 은 파일럿 개발 NMSE 로 고른 값을 루프에 그대로; OMP-pilot = 파일럿 LS 인 판정점 (SV8e +3, UMi28·MIX3 세 점 모두) | R §20 :1378, :1379, :1381, :1382; `conference/README.md`:72 |
| Annealed Langevin = 같은 V1 가중치, 원 방법(저자 네트워크)의 재현 아님 | R §12 :1123; PAPER_PLAN:20 |
| Pilot-only LMMSE = 1-pass @1 판독 (08_SPEC §1 규약) | SP:4; SU:32 |
| 비정상 조건 정의 (정적·0° prior, 재학습 없음; ν 0.005·0.01, 회전 15°·30°) | R §13 :1137–1139; SU:6 |
| (C) "all 13" 조건: 원 b\* (i) ∧ k𝔅 = 12 ∧ m𝔅 = 0 ∧ R_{X\*} 90% CI 하한 > 0, X\* = −3 dB 실패 최소 | SU:38; SU:179 (가능 19) |
| GMM K: D2 C2 kron 1024 격자 끝 (2048 미적합); D3·UMi28·MIX3 kron 4096 격자 끝 + 수렴 캐비엇; SV8e full 256 내부; UMi28 C6·C9 kron 4096 격자 끝; D2 C9 kron 2048 내부; "등록 프로토콜의 GMM 이며 최적 GMM 이 아니다" | R §10.4 :1038; R §21.1 :1402–1403; R §21.3 :1486; R §21.6 :1547 |
| K 선택 = 검증 우도 | T:12 ("검증 우도로 K 선택") |

## 6. 표에 넣지 않은 캐비엇 (원고 본문용; 표의 수치 뜻은 바꾸지 않는다고 판단)

- 헤드라인 가중치는 best 가 아니라 last-EMA (BEST_WEIGHTS_UNAVAILABLE) — `conference/README.md`:67, R §1 :24–26.
- 38.901 경계 공동 판독: SV8e (iv) × UMi28 (i) → "판정하지 못함"; 등록 예측 "38.901 에서 V1 우위 없음" 은 빗나감 — R §10.3 :1032–1033, F20:15.
- 채널 모델 회수율 ΔR 라벨 ("D2 보다 낮다": D3 −0.104, UMi28 −0.408, SV8e −0.327) — R §10.2 :1023–1025 (표에는 R 만).
- 비정상 DOP ν = 0.01 의 genie ≥ V1 가드 (D2 C2·C6, R 정의 불가) — SU:192, R §15 :1180. 표 (C) 의 18/24 는 이 두 조건이 GMM (iii) 이라 원래 불가였으므로 영향 없음 (SU:179).
- 확산 시드 하나 (D3·SV8e·MIX3 의 a1) 캐비엇은 (D) 로 해소; SV8e 시드 라벨은 결과 전에 정해짐 (표 주석에 있음).

## 7. 출처를 찾지 못한 수치

없음. 표의 모든 수치가 위 줄에 그대로 있다 (작성자 산술 3 곳은 위에 표시: (A) Non-st. 의 n.s./insuff. 0, (B) SV8e "5 insuff.", (C) GMM "fails more 0").

## 8. 기록 사이 불일치 (표 수치에 영향 없음)

- R_dp 의 90% CI 셋째 자리: 같은 셀의 `recovery_<T>.txt` 와 frontier (`scale2_step_*`/`primary_*`) 가 난수 흐름이 달라 다르다 — UMi28 C6 [0.253, 0.322] (SN:225) 대 [0.252, 0.322] (R §21.2 :1441), UMi28 C9 [0.402, 0.462] (SN:228) 대 [0.401, 0.463] (R §21.1 :1395). 기록 자신이 이유를 적어 두었다 (R §21.4 :1499). 표는 R_dp 점추정만 쓴다 (0.287, 0.432 은 양쪽 동일).
- 같은 $8\times4$ sparse specular 셀의 R 이 두 정의로 기록돼 있다: −3 dB 한 점 0.470 (표 (A)(B)(D) 가 쓰는 값) 대 판정점 합 R_dp 0.509 (R §21.1 :1394, PAPER_PLAN 2순위 행, 그림 F30). 정의 차이이지 모순은 아니지만, 표 I 와 그림 3 을 함께 쓰면 두 값이 나란히 보이므로 본문·캡션에서 정의를 밝혀야 한다 (CONTRIBUTIONS:113 끝 문장도 같은 주의).
- 그 밖에 표에 쓴 값에서 RESULTS·등록 문서·pairB·그림 .txt 사이 불일치는 찾지 못했다 (교차 확인: SP ↔ ST 13 블록 바이트 동일, SP ↔ R §20, R §10.1–10.2 ↔ F20, R §10.5 ↔ S1, R §18 ↔ S3, R §22 ↔ SN, SU 집계 ↔ R §15).


## Fable 감사 반영 출처 (2026-10-06 01:41 CDT)

| 추가한 주석 | 출처 (감사 보고 인용) |
|---|---|
| Gaussian prior 비교도 개별 사전 등록 | `conf/10_SPEC_stageC.md` :145–146; `conf/code/analysis.py` :396–399 (REF = `R2-ours-G`, :100); STATIC16e4 :5, :69 |
| SBL at UMi: oversampling 8 (격자 내부) | `docs/RESULTS.md` :1378 |
| EM tol 정지 (K=4096 적합, sparse specular 32×4) | `docs/RESULTS.md` :1038, :1402, :1486 |
| 평가 가중치: sparse specular 8×4 = last-epoch EMA (best 미저장), 그 밖 = best-validation | `docs/RESULTS.md` :25–26, :1003, :1206, :1388; 라벨 불변 :1013, R_dp best/last 차 ≤ 0.009 :1520–1522 |
| 다중성 보정 없음, 개수 문장 | SUPP16e4 :40; `docs/RESULTS.md` :1348; `docs/paper/CONTRIBUTIONS.md` :112 |
| 시드 3 폴백 없는 선례 규칙: 2/3, 1 판정 못함 (학습 실패) | `NEXT_EXPERIMENTS_SEEDSNR16e4.md` :243; `NEXT_EXPERIMENTS_SEEDS16e4.md` :33 |
| 32×4 SNR 격자 −12:3:6 dB | `docs/RESULTS.md` :1495, :1497, :1388 |
