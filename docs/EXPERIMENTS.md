# 실험 로그

한 실험 = 한 행. 실행이 끝나면 즉시 추가한다. logs/는 커밋되지 않으므로 이 표가 유일한 영구 기록이다.

| 날짜(KST) | 설정 파일 | seed | 커밋 | GPU | 핵심 지표 | 로그 | 메모 |
|---|---|---|---|---|---|---|---|
| 2026-09-18 07:05 | `exp_0921_run.py A --n 320` | 20260921+100+SNR | dc5d2bb | 없음 (CPU) | `Demo/exp_0921_results_A.txt` | `logs/20260918_0705_0921A.log` | D-15 baseline table. 8 points × n=320 → `Demo/exp_0921_raw/A_*.npz` 64개. 원본(쌍 2개 추가 전)은 커밋 dc5d2bb의 `exp_0921_results.txt` |
| 2026-09-18 09:04 | `exp_0921_run.py B --n 160` | 20260921+100+SNR | 0f37555 (실행 시점 코드) | 없음 (CPU) | `Demo/exp_0921_results_B.txt` | `logs/20260918_0904_exp0921B.log` | Q-20 regime scan. `--jobs 16`, 70 points × n=160 → `Demo/exp_0921_raw/B_*.npz` 280개, 2.8분, 경고/에러 없음. 결과 파일은 10:18 실행의 분석으로 덮어써짐. n=160 시점 내용은 커밋 0e905f7의 같은 경로 |
| 2026-09-18 10:18 | `exp_0921_run.py B --n 640 --rho 0.7` | 20260921+100+SNR | c3db37a (실행 시점 코드) | 없음 (CPU) | `Demo/exp_0921_results_B.txt` | `logs/20260918_1018_exp0921B_n640_rho0.7.log` | Q-20 rho=0.7 확장. `--jobs` 기본(192), 35 points × n=640 → `B_Nr4_rho0.7_*` chunk 560개 (기존 140 재사용 + 신규 420), 49초 |
| 2026-09-18 10:19 | `exp_0921_run.py B --n 320 --rho 0.7 --Nr 8` | 20260921+100+SNR | c3db37a (실행 시점 코드) | 없음 (CPU) | `Demo/exp_0921_results_B.txt` | `logs/20260918_1018_exp0921B_n320_Nr8.log` | Q-20 8x4. `--jobs` 기본(192), 35 points × n=320 → `B_Nr8_*` chunk 280개 전부 신규, 37초 |
| 2026-09-18 10:19 | `exp_0921_run.py C` | 20260921+100+SNR | c3db37a (실행 시점 코드) | 없음 (CPU) | `Demo/exp_0921_results_C.txt` | `logs/20260918_1018_exp0921C.log` | Q-25(b) GMM testbed, n=320 기본. `--jobs` 기본(192), 6 points × n=320 → `C_*` chunk 48개 전부 신규, 40초. genie의 NMSE가 전부 NaN이라 `np.nanmedian` RuntimeWarning 1건 |
