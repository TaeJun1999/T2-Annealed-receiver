# 학회용 그림 (F16~F32)

`conf/figs/` 에 있는 학회용 그림의 사본이다. 각 그림은 `conf/code/figure_f*.py` 가 raw npz 에서 다시 계산해 그리고 기록된 실패 수를 assert 로 대조한다 (F27·F29 만 예외: 감사로 재현된 기록 파일의 값을 옮겨 그린다). `.txt` 에는 그림의 수치 전부와 캡션용 캐비엇이 있다.

공통 조건: 동일예산 N_train = 1.6e5, 테스트 시행 0..2559 (SNR 당 n = 2560), BLER@16. 예외: F32 는 추가 시행 10000..30479 (n = 20480) 를 원 태그 옆에 둔다. 그림은 보여 주기만 하고 검정하지 않는다. 검정된 비교와 라벨은 각 등록 문서 §6 에 있다.

| 그림 | 내용 | 스크립트 | 등록 문서 (§6) |
|---|---|---|---|
| F16 `F16_headline_budget` | D2 C2 헤드라인 BLER 곡선 + 동일예산 N_train 별 −3 dB BLER | `figure_f16.py` | Stage C, B32e4 |
| F17 `F17_codim_C6` | 여차원 C2 대 C6 (Nr=16) 곡선, 회수율 대 예산 | `figure_f17.py` | C6B16e4 |
| F18 `F18_oog_rule_K2` | C1 격자 밖 질의 규칙 K2 | `figure_f18.py` | K1K2 |
| F19 `F19_pilot_pareto` | 파일럿 오버헤드 Pareto | `figure_f19.py` | PARETO |
| F20 `F20_channel_models` | 채널 모델별 격차·UMi28 곡선·회수율 | `figure_f20.py` | D3B16e4, SVB16e4, 38901 |
| F21 `F21_all_baselines` | 6 데이터셋 × 핵심 baseline 곡선 | `figure_f21.py` | (위 등록들) |
| F22 `F22_pilot_only` | 파일럿 전용 prior 대 루프 | `figure_f22.py` | PILOT16e4 |
| F23 `F23_mismatch` | 학습/평가 채널 모델 불일치 8 쌍 | `figure_f23.py` | MISMATCH16e4 |
| F24 `F24_nonstationary_D2C2` | D2 C2 블록 안 도플러 ν = 0.005/0.01, 수신 배열 회전 15°/30° — 등록 baseline (ALD plug-in·V1-pilot 포함) 곡선 | `figure_f24.py` | DOP16e4, ROT16e4, SUPP16e4 |
| F25 `F25_nonstationary_all` | 24 조건 (6 데이터셋 × 4) −3 dB BLER: V1, 가장 가까운 baseline X\*, genie | `figure_f24.py` | SUPP16e4 |
| F26 `F26_drift_spatial` | 표류 학습 prior (B′, 15°/30°)와 공간 비정상 S2v (C, 16×4) 곡선 | `figure_f24.py` | ROTMIX16e4, S2V16e4 |
| F27 `F27_nonstationary_gap_recovery` | 6 데이터셋 × {정적, 도플러 2, 회전 2}: (a) SNR@0.1 격차 b\*−V1 [dB], (b) 회수율 R (−3 dB), 90% CI; 속 빈 점 = 등록 라벨 (iii)/(iv). 기록 파일 전사 | `figure_f27.py` | F20·F17 기록, SUPP16e4 |
| F28 `F28_nonstationary_C6` | D2 C6 (16×4) 도플러·회전 네 조건 곡선 (F24 와 같은 arm) | `figure_f27.py` | DOP16e4, ROT16e4, SUPP16e4 |
| F29 `F29_label_grid` | SUPP16e4 등록 라벨 격자 24 조건 × 13 baseline: (i) 301, (iii) 5, (iv) 6, (ii) 0 | `figure_f27.py` | SUPP16e4 |
| F30 `F30_scale_trend` | 배열 규모 축: Nr 8/16/32 (C2/C6/C9) 의 판정점 회수율 R_dp (90% CI), D2·UMi28 — 1차 ΔR 라벨·한정어와 단계 라벨 표기 (그림은 영문 풀이, 등록 원문은 .txt), C9 두 셀 BLER 곡선 (95% Wilson) | `figure_f30.py` | SCALE16e4 |
| F31 `F31_sparse_baselines` | 희소 baseline (SBL-loop, SBL-pilot, OMP-pilot) 대 V1: 6 데이터셋 판정점 R_X (90% CI; b\* 인용 병기, (iv) 표기) + D2 C2 BLER 곡선 | `figure_f31.py` | SPARSE16e4 (b\* 는 STATIC16e4 인용) |
| F32 `F32_hisnr_highsnr` | 고SNR 보강 (보고 전용, 라벨 없음): D2 C2·C6 +6..+15 dB BLER, 95% Wilson — 새 시행 n = 20480 과 원 태그 n = 2560 을 나란히 (합치지 않음) | `figure_f32.py` | HISNR16e4 |

인용 주의:
- D2 C2 헤드라인 외의 체크포인트(C6, C9, D3, SV8e, 38.901, S2v, S2d)는 UNGATED 측정이다.
- genie 는 알려진 채널 기준선이며 하한이 아니다. F24 (b) 와 F25 의 도플러 ν = 0.01 에서는 genie 가 블록의 H_0 만 알기 때문에 V1 보다 많이 실패하는 조건이 있다 (SUPP16e4 §0).
- SNR 점마다 채널과 잡음을 독립으로 뽑는다(`common.trial_rng`). 실패 수가 10 건 안팎인 고SNR 점에서 곡선이 한 점 올라가는 것은 표본 잡음이다.
- genie 의 고SNR 바닥은 경로 수 L = 3 < Nt = 4 인 **랭크 부족 블록**에서 온다: D2 C2 +9..+15 dB 의 genie 실패 6 건 전부 L = 3 (cond(H) ≈ 1e16), D3 27 건 중 L = 3 이 21 건·L = 4 가 5 건 (`conf/code/genie_floor.py`, `conf/results/review_next/genie_floor/`; 보고 전용 진단).
- F30 의 SCALE16e4 raw (C9 셀·UMi28 C6) 는 scale 워크트리 `~/t2_wtS/conf/raw_*` 에 있다 (미추적). 재사용 셀 raw 는 `conf/raw_*`. 경로는 F30 `.txt` 머리말에 있다.
- F32 는 보고 전용이다 (HISNR16e4 §1): 새 시행은 원 태그와 합치지 않고, 등록된 판정점·라벨·"전부" 문장은 원 태그의 것이다.
- 등록 문서 경로: `conf/results/review_next/NEXT_EXPERIMENTS_<이름>.md`. 결과 색인: 저장소 최상위 `conference/README.md`.
