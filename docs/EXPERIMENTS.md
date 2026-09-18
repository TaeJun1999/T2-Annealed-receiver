# 실험 로그

한 실험 = 한 행. 실행이 끝나면 즉시 추가한다. logs/는 커밋되지 않으므로 이 표가 유일한 영구 기록이다.

| 날짜(KST) | 설정 파일 | seed | 커밋 | GPU | 핵심 지표 | 로그 | 메모 |
|---|---|---|---|---|---|---|---|
| 2026-09-18 07:05 | `exp_0921_run.py A --n 320` | 20260921+100+SNR | dc5d2bb | 없음 (CPU) | `Demo/exp_0921_results.txt` | `logs/20260918_0705_0921A.log` | D-15 baseline table. 8 points × n=320 → `Demo/exp_0921_raw/A_*.npz` 64개 |
| 2026-09-18 09:04 | `exp_0921_run.py B --n 160` | 20260921+100+SNR | 0f37555 (실행 시점 코드) | 없음 (CPU) | `Demo/exp_0921_results_B.txt` | `logs/20260918_0904_exp0921B.log` | Q-20 regime scan. `--jobs 16`, 70 points × n=160 → `Demo/exp_0921_raw/B_*.npz` 280개, 2.8분, 경고/에러 없음 |
