### 6.1 실행·운영 기록 (생성기 `prereg_audit_2026-10-11/s6_fighsx_gen.py`; 수치는 모두 기록 파일에서 읽음)

`bash code/run_fighsx16e4.sh`, 실행 커밋 037c6610; 시작 줄 3 개(첫 실행 + `--resume` 2 번), `FIGHS_DONE` 줄 3 개. 운영 로그 `logs/run_fighsx16e4.log` 의 시작 · 단계 C · 종료 · 중단 줄 전부(원문, 시간순):

- `[fighs 10-11 20:40 CDT] start (git 037c6610) rows: all resume=0 skip0 10000 n 81920 SNR 12 15`
- `[fighs 10-11 20:44 CDT] phase C done: 6 receiver control(s) OK, 2 ALD estimator control(s) OK`
- `[fighs 10-12 04:09 CDT] FXALDSRP ABORT: no free GPU for the ALD estimate (resume later; no automatic retry)`
- `[fighs 10-12 04:09 CDT] FIGHS_DONE ok=5 fail=1`
- `[fighs 10-12 04:39 CDT] ABORT (precondition): DECISIONS.md not tracked+clean (commit the registration first)`
- `[fighs 10-12 04:40 CDT] start (git 037c6610) rows: FXALDSRP resume=1 skip0 10000 n 81920 SNR 12 15`
- `[fighs 10-12 04:41 CDT] phase C done: 6 receiver control(s) OK, 2 ALD estimator control(s) OK`
- `[fighs 10-12 04:41 CDT] FXALDSRP SKIP: genie reference FXSRPB16e4 not accepted`
- `[fighs 10-12 04:41 CDT] FIGHS_DONE ok=0 fail=1`
- `[fighs 10-12 04:41 CDT] start (git 037c6610) rows: FXSRPB16e4 FXALDSRP resume=1 skip0 10000 n 81920 SNR 12 15`
- `[fighs 10-12 04:42 CDT] phase C done: 6 receiver control(s) OK, 2 ALD estimator control(s) OK`
- `[fighs 10-12 04:58 CDT] FIGHS_DONE ok=2 fail=0`

| 행 | 시작 (CDT) | runner | 작업 (done / exists) | 수용 (CDT) | 수용 판정 | manifest git · config_hash | 대조 |
|---|---|---|---|---|---|---|---|
| FXSRBB16e4 | 10-11 20:44 | 77.9 분 · 4096 작업 · 192 워커 | 4096 / 0 | 10-11 22:02 | rc=0; ACCEPT: OK -- FXSRBB16e4; ACCEPT (f): OK | 037c6610 · cf706d8f5999293c | CONTROL: OK |
| FXSPSRB | 10-11 22:02 | 100.7 분 · 4096 작업 · 192 워커 | 4096 / 0 | 10-11 23:45 | rc=0; ACCEPT: OK -- FXSPSRB; ACCEPT (f): OK | 037c6610 · cf706d8f5999293c | CONTROL: OK |
| FXALDSRB | 10-11 23:54 | 4.3 분 · 4096 작업 · 192 워커 | 4096 / 0 | 10-12 00:00 | rc=0; ACCEPT: OK -- FXALDSRB; ACCEPT (f): OK | 037c6610 · cf706d8f5999293c | CONTROL: OK · CONTROL-ALD: OK |
| FXSRPB16e4 | 10-12 00:00 · 10-12 04:42 | 154.2 · 0.0 분 · 4096 작업 · 192 워커 | 4096 / 4096 | 10-12 02:35 · 10-12 04:42 | rc=0; ACCEPT: OK -- FXSRPB16e4; ACCEPT (f): OK | 037c6610 · cf706d8f5999293c | CONTROL: OK |
| FXSPSRP | 10-12 02:35 | 92.0 분 · 4096 작업 · 192 워커 | 4096 / 0 | 10-12 04:09 | rc=0; ACCEPT: OK -- FXSPSRP; ACCEPT (f): OK | 037c6610 · cf706d8f5999293c | CONTROL: OK |
| FXALDSRP | 10-12 04:52 | 4.5 분 · 4096 작업 · 192 워커 | 4096 / 0 | 10-12 04:58 | rc=0; ACCEPT: OK -- FXALDSRP; ACCEPT (f): OK | 037c6610 · cf706d8f5999293c | CONTROL: OK · CONTROL-ALD: OK |

수용 파일의 (f) 줄:

- `(f) raw_FXSRBB16e4: 4096 chunk files, run|git ['037c6610']; pick -; rotation -; ald -; raised trials per arm (= failures, report only) 0`
- `(f) raw_FXSPSRB: 4096 chunk files, run|git ['037c6610']; pick results/sparse/pick_SRB_C2.json; rotation -; ald -; raised trials per arm (= failures, report only) 0`
- `(f) raw_FXALDSRB: 4096 chunk files, run|git ['037c6610']; pick -; rotation -; ald /home/HTJ/t2/conf/results/ald/ald_PILSRB_hisnr4.npz; raised trials per arm (= failures, report only) 0`
- `(f) raw_FXSRPB16e4: 4096 chunk files, run|git ['037c6610']; pick -; rotation -; ald -; raised trials per arm (= failures, report only) 0`
- `(f) raw_FXSPSRP: 4096 chunk files, run|git ['037c6610']; pick results/sparse/pick_SRP_C2.json; rotation -; ald -; raised trials per arm (= failures, report only) 0`
- `(f) raw_FXALDSRP: 4096 chunk files, run|git ['037c6610']; pick -; rotation -; ald /home/HTJ/t2/conf/results/ald/ald_PILSRP_hisnr4.npz; raised trials per arm (= failures, report only) 0`

집계표 머리말: `# run_fighsx16e4 git 037c6610 raw_FXSRBB16e4 C2: failures@16 / n, BLER, 95% Wilson -- REPORT-ONLY (FIGHSX16e4 §1); load_raw warnings 0`

집계표 머리말: `# run_fighsx16e4 git 037c6610 raw_FXSPSRB C2: failures@16 / n, BLER, 95% Wilson -- REPORT-ONLY (FIGHSX16e4 §1); load_raw warnings 0`

집계표 머리말: `# run_fighsx16e4 git 037c6610 raw_FXALDSRB C2: failures@16 / n, BLER, 95% Wilson -- REPORT-ONLY (FIGHSX16e4 §1); load_raw warnings 0`

### 6.2a SRB (방, 무작위 위치) — 범례 11 곡선의 +12 / +15 dB 실패 수: n = 81920 전체, 보지 않은 61440 시행만, 앞선 n = 20480

| 곡선 (arm) | 출처 | +12 dB: k / 81920 (BLER, 95 % Wilson) · 보지 않은 시행 k / 61440 (BLER) · 본 시행 k / 20480 [raw_FH 의 k] | +15 dB: k / 81920 (BLER, 95 % Wilson) · 보지 않은 시행 k / 61440 (BLER) · 본 시행 k / 20480 [raw_FH 의 k] |
|---|---|---|---|
| M-ours-dscore-C-V1 | raw_FXSRBB16e4 | 12 (1.46e-04, [8.38e-05, 2.56e-04]) · 9 (1.46e-04) · 3 [3] | 11 (1.34e-04, [7.50e-05, 2.40e-04]) · 7 (1.14e-04) · 4 [4] |
| ALD-pilot | raw_FXALDSRB | 40 (4.88e-04, [3.59e-04, 6.65e-04]) · 31 (5.05e-04) · 9 [7] | 31 (3.78e-04, [2.67e-04, 5.37e-04]) · 17 (2.77e-04) · 14 [11] |
| M-ours-bstar | raw_FXSRBB16e4 | 32 (3.91e-04, [2.77e-04, 5.51e-04]) · 21 (3.42e-04) · 11 [11] | 15 (1.83e-04, [1.11e-04, 3.02e-04]) · 9 (1.46e-04) · 6 [6] |
| R2-ours-G | raw_FXSRBB16e4 | 144 (1.76e-03, [1.49e-03, 2.07e-03]) · 107 (1.74e-03) · 37 [37] | 65 (7.93e-04, [6.23e-04, 1.01e-03]) · 46 (7.49e-04) · 19 [19] |
| R1-turbo | raw_FXSRBB16e4 | 319 (3.89e-03, [3.49e-03, 4.34e-03]) · 232 (3.78e-03) · 87 [87] | 127 (1.55e-03, [1.30e-03, 1.84e-03]) · 93 (1.51e-03) · 34 [34] |
| R3-bigamp | raw_FXSRBB16e4 | 11377 (1.39e-01, [1.37e-01, 1.41e-01]) · 8564 (1.39e-01) · 2813 [2813] | 10284 (1.26e-01, [1.23e-01, 1.28e-01]) · 7803 (1.27e-01) · 2481 [2481] |
| R0-pilot@1 | raw_FXSRBB16e4 | 1558 (1.90e-02, [1.81e-02, 2.00e-02]) · 1182 (1.92e-02) · 376 [376] | 676 (8.25e-03, [7.66e-03, 8.89e-03]) · 503 (8.19e-03) · 173 [173] |
| SBL-loop | raw_FXSPSRB | 90 (1.10e-03, [8.94e-04, 1.35e-03]) · 73 (1.19e-03) · 17 [17] | 43 (5.25e-04, [3.90e-04, 7.07e-04]) · 30 (4.88e-04) · 13 [13] |
| SBL-pilot | raw_FXSPSRB | 103 (1.26e-03, [1.04e-03, 1.52e-03]) · 80 (1.30e-03) · 23 [23] | 43 (5.25e-04, [3.90e-04, 7.07e-04]) · 30 (4.88e-04) · 13 [13] |
| OMP-pilot | raw_FXSPSRB | 304 (3.71e-03, [3.32e-03, 4.15e-03]) · 241 (3.92e-03) · 63 [63] | 178 (2.17e-03, [1.88e-03, 2.52e-03]) · 125 (2.03e-03) · 53 [53] |
| R5-genie | raw_FXSRBB16e4 | 5 (6.10e-05, [2.61e-05, 1.43e-04]) · 4 (6.51e-05) · 1 [1] | 4 (4.88e-05, [1.90e-05, 1.26e-04]) · 3 (4.88e-05) · 1 [1] |

Perfect CSI (R5-genie) 의 실패 수는 세 raw 에서 같다: FXSRBB16e4 [5, 4] · FXSPSRB [5, 4] · FXALDSRB [5, 4] → 동일. "본 시행" 의 수는 ALD-pilot 을 뺀 모든 arm 에서 n = 20480 raw 의 수와 같다(assert); ALD-pilot 은 새 사후 표본이라 다를 수 있다(등록 머리말 '시행').

0 실패 점 (n = 81920): 없음.

그림 기록 `records/paper_f21srbhsx.txt` 의 '오르는 칸' (한쪽 Fisher p; 보고만): 1 줄. y 축 (3e-05, 1.2).
- `R3-bigamp           @16  2861/20480 2507/20480 11377/81920 10284/81920   (+6..+15 dB: raw_FHSRBB16e4; then +12/+15 dB: raw_FXSRBB16e4)   rising: +9->+12 dB p=2.7e-10`

집계표 머리말: `# run_fighsx16e4 git 037c6610 raw_FXSRPB16e4 C2: failures@16 / n, BLER, 95% Wilson -- REPORT-ONLY (FIGHSX16e4 §1); load_raw warnings 0`

집계표 머리말: `# run_fighsx16e4 git 037c6610 raw_FXSPSRP C2: failures@16 / n, BLER, 95% Wilson -- REPORT-ONLY (FIGHSX16e4 §1); load_raw warnings 0`

집계표 머리말: `# run_fighsx16e4 git 037c6610 raw_FXALDSRP C2: failures@16 / n, BLER, 95% Wilson -- REPORT-ONLY (FIGHSX16e4 §1); load_raw warnings 0`

### 6.2b SRP (경로, 이동 단말) — 범례 11 곡선의 +12 / +15 dB 실패 수: n = 81920 전체, 보지 않은 61440 시행만, 앞선 n = 20480

| 곡선 (arm) | 출처 | +12 dB: k / 81920 (BLER, 95 % Wilson) · 보지 않은 시행 k / 61440 (BLER) · 본 시행 k / 20480 [raw_FH 의 k] | +15 dB: k / 81920 (BLER, 95 % Wilson) · 보지 않은 시행 k / 61440 (BLER) · 본 시행 k / 20480 [raw_FH 의 k] |
|---|---|---|---|
| M-ours-dscore-C-V1 | raw_FXSRPB16e4 | 4 (4.88e-05, [1.90e-05, 1.26e-04]) · 4 (6.51e-05) · 0 [0] | 1 (1.22e-05, [2.15e-06, 6.91e-05]) · 1 (1.63e-05) · 0 [0] |
| ALD-pilot | raw_FXALDSRP | 11 (1.34e-04, [7.50e-05, 2.40e-04]) · 6 (9.77e-05) · 5 [3] | 4 (4.88e-05, [1.90e-05, 1.26e-04]) · 2 (3.26e-05) · 2 [2] |
| M-ours-bstar | raw_FXSRPB16e4 | 14 (1.71e-04, [1.02e-04, 2.87e-04]) · 11 (1.79e-04) · 3 [3] | 6 (7.32e-05, [3.36e-05, 1.60e-04]) · 5 (8.14e-05) · 1 [1] |
| R2-ours-G | raw_FXSRPB16e4 | 16 (1.95e-04, [1.20e-04, 3.17e-04]) · 12 (1.95e-04) · 4 [4] | 6 (7.32e-05, [3.36e-05, 1.60e-04]) · 5 (8.14e-05) · 1 [1] |
| R1-turbo | raw_FXSRPB16e4 | 44 (5.37e-04, [4.00e-04, 7.21e-04]) · 33 (5.37e-04) · 11 [11] | 11 (1.34e-04, [7.50e-05, 2.40e-04]) · 7 (1.14e-04) · 4 [4] |
| R3-bigamp | raw_FXSRPB16e4 | 11333 (1.38e-01, [1.36e-01, 1.41e-01]) · 8452 (1.38e-01) · 2881 [2881] | 10874 (1.33e-01, [1.30e-01, 1.35e-01]) · 8192 (1.33e-01) · 2682 [2682] |
| R0-pilot@1 | raw_FXSRPB16e4 | 656 (8.01e-03, [7.42e-03, 8.64e-03]) · 487 (7.93e-03) · 169 [169] | 196 (2.39e-03, [2.08e-03, 2.75e-03]) · 141 (2.29e-03) · 55 [55] |
| SBL-loop | raw_FXSPSRP | 14 (1.71e-04, [1.02e-04, 2.87e-04]) · 6 (9.77e-05) · 8 [8] | 8 (9.77e-05, [4.95e-05, 1.93e-04]) · 6 (9.77e-05) · 2 [2] |
| SBL-pilot | raw_FXSPSRP | 20 (2.44e-04, [1.58e-04, 3.77e-04]) · 9 (1.46e-04) · 11 [11] | 8 (9.77e-05, [4.95e-05, 1.93e-04]) · 6 (9.77e-05) · 2 [2] |
| OMP-pilot | raw_FXSPSRP | 124 (1.51e-03, [1.27e-03, 1.80e-03]) · 94 (1.53e-03) · 30 [30] | 38 (4.64e-04, [3.38e-04, 6.37e-04]) · 29 (4.72e-04) · 9 [9] |
| R5-genie | raw_FXSRPB16e4 | 1 (1.22e-05, [2.15e-06, 6.91e-05]) · 0 (0.00e+00) · 1 [1] | 0 (0.00e+00, [0.00e+00, 4.69e-05]) · 0 (0.00e+00) · 0 [0] |

Perfect CSI (R5-genie) 의 실패 수는 세 raw 에서 같다: FXSRPB16e4 [1, 0] · FXSPSRP [1, 0] · FXALDSRP [1, 0] → 동일. "본 시행" 의 수는 ALD-pilot 을 뺀 모든 arm 에서 n = 20480 raw 의 수와 같다(assert); ALD-pilot 은 새 사후 표본이라 다를 수 있다(등록 머리말 '시행').

0 실패 점 (n = 81920): R5-genie +15 dB.

그림 기록 `records/paper_f21srphsx.txt` 의 '오르는 칸' (한쪽 Fisher p; 보고만): 1 줄. y 축 (7.5e-06, 1.2).
- `R3-bigamp           @16  3386/20480 2585/20480 11333/81920 10874/81920   (+6..+15 dB: raw_FHSRPB16e4; then +12/+15 dB: raw_FXSRPB16e4)   rising: +9->+12 dB p=2.7e-06`

### 6.3 §3 예측 채점 (n = 81920 으로 채점; 괄호 안의 둘째 수는 보지 않은 61440 시행만의 수)

1. SRB: V1 의 실패 수 +15 dB ≤ +12 dB → **적중** (12 → 11; 보지 않은 시행 9 → 7).
2. SRB: V1 · b\* · Perfect CSI 에 Fisher p < 0.05 인 오르는 칸 없음 → **적중** (오르는 칸의 p: M-ours-dscore-C-V1 없음, M-ours-bstar 없음, R5-genie 없음).
3a. SRB: +12 dB 에서 실패 수 V1 ≤ b\* → **적중** (12 대 32; 보지 않은 시행 9 대 21).
3b. SRB: +15 dB 에서 실패 수 V1 ≤ b\* → **적중** (11 대 15; 보지 않은 시행 7 대 9).
4a. SRB: V1 의 +12 dB 실패 수가 5..35 → **적중** (12).
4b. SRB: V1 의 +15 dB 실패 수가 7..41 → **적중** (11).
5. SRP: V1 의 실패 수 +15 dB ≤ +12 dB → **적중** (4 → 1; 보지 않은 시행 4 → 1).
6a. SRP: +12 dB 에서 실패 수 V1 ≤ b\* → **적중** (4 대 14; 보지 않은 시행 4 대 11).
6b. SRP: +15 dB 에서 실패 수 V1 ≤ b\* → **적중** (1 대 6; 보지 않은 시행 1 대 5).
7. 여섯 행 모두 대조·수용 통과(`FIGHS_DONE ok=6 fail=0`) → **빗나감** (첫 실행의 종료 줄 ok=5 fail=1; 시작 줄 3 개; 재개까지 마친 뒤 수용 파일이 `ACCEPT: OK` 인 행 6 / 6 — 엄격 채점: 한 번의 실행으로 ok=6 이 아니면 빗나감).
8. 처음 20480 시행이 `raw_FH*` 와 비트 동일(ALD-pilot 제외) → **적중** (작성자의 확인 `prereg_audit_2026-10-11/fx_overlap_check.py`; 기록 감사가 따로 확인한다):
   - `raw_FXSRBB16e4 vs raw_FHSRBB16e4: 1024 chunk files (expected 1024 = 512 x 2 SNR), arms ['M-ours-bstar', 'M-ours-dscore-C-V1', 'R0-pilot', 'R1-turbo', 'R2-ours-G', 'R3-bigamp', 'R5-genie'], 67584 array comparisons, 0 differ`
   - `raw_FXSPSRB vs raw_FHSPSRB: 1024 chunk files (expected 1024 = 512 x 2 SNR), arms ['OMP-pilot', 'R5-genie', 'SBL-loop', 'SBL-pilot'], 37888 array comparisons, 0 differ`
   - `raw_FXALDSRB vs raw_FHALDSRB: 1024 chunk files (expected 1024 = 512 x 2 SNR), arms ['R5-genie'], 13312 array comparisons, 0 differ; ALD-pilot (not required): 3214 of 9216 arrays differ`
   - `raw_FXSRPB16e4 vs raw_FHSRPB16e4: 1024 chunk files (expected 1024 = 512 x 2 SNR), arms ['M-ours-bstar', 'M-ours-dscore-C-V1', 'R0-pilot', 'R1-turbo', 'R2-ours-G', 'R3-bigamp', 'R5-genie'], 67584 array comparisons, 0 differ`
   - `raw_FXSPSRP vs raw_FHSPSRP: 1024 chunk files (expected 1024 = 512 x 2 SNR), arms ['OMP-pilot', 'R5-genie', 'SBL-loop', 'SBL-pilot'], 37888 array comparisons, 0 differ`
   - `raw_FXALDSRP vs raw_FHALDSRP: 1024 chunk files (expected 1024 = 512 x 2 SNR), arms ['R5-genie'], 13312 array comparisons, 0 differ; ALD-pilot (not required): 3229 of 9216 arrays differ`
   - `OVERLAP: OK`
