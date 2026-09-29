# 학회용 그림 (F16~F26)

`conf/figs/` 에 있는 학회용 그림의 사본이다. 각 그림은 `conf/code/figure_f*.py` 가 raw npz 에서 다시 계산해 그리고, 기록된 실패 수를 assert 로 대조한다. `.txt` 에는 그림의 수치 전부와 캡션용 캐비엇이 있다.

공통 조건: 동일예산 N_train = 1.6e5, 테스트 시행 0..2559 (SNR 당 n = 2560), BLER@16. 그림은 보여 주기만 하고 검정하지 않는다. 검정된 비교와 라벨은 각 등록 문서 §6 에 있다.

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
| F24 `F24_nonstationary_D2C2` | D2 C2 블록 안 도플러 ν = 0.005/0.01, 수신 배열 회전 15°/30° — 등록 baseline (ALD·V1-pilot 포함) 곡선 | `figure_f24.py` | DOP16e4, ROT16e4, SUPP16e4 |
| F25 `F25_nonstationary_all` | 24 조건 (6 데이터셋 × 4) −3 dB BLER: V1, 가장 가까운 baseline X\*, genie | `figure_f24.py` | SUPP16e4 |
| F26 `F26_drift_spatial` | 표류 학습 prior (B′, 15°/30°)와 공간 비정상 S2v (C, 16×4) 곡선 | `figure_f24.py` | ROTMIX16e4, S2V16e4 |

인용 주의:
- D2 C2 헤드라인 외의 체크포인트(C6, D3, SV8e, 38.901, S2v, S2d)는 UNGATED 측정이다.
- genie 는 알려진 채널 기준선이며 하한이 아니다. F24 (b) 와 F25 의 도플러 ν = 0.01 에서는 genie 가 블록의 H_0 만 알기 때문에 V1 보다 많이 실패하는 조건이 있다 (SUPP16e4 §0).
- SNR 점마다 채널과 잡음을 독립으로 뽑는다(`common.trial_rng`). 실패 수가 10 건 안팎인 고SNR 점에서 곡선이 한 점 올라가는 것은 표본 잡음이다.
- 등록 문서 경로: `conf/results/review_next/NEXT_EXPERIMENTS_<이름>.md`. 결과 색인: 저장소 최상위 `conference/README.md`.
