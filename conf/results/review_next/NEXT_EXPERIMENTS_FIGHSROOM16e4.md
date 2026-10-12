# NEXT_EXPERIMENTS_FIGHSROOM16e4 — Sionna RT 방 그림(prior SRB)의 고SNR 점을 새 시행 n = 20480 으로 (범례 11 곡선; +6..+15 dB; **보고 전용**, 등록 v2)

- 작성: 2026-10-11 16:44 CDT, Claude Code (Opus 5.5), 초안 v1 (커밋 1404d315) → 적대적 검토 1 건(Fable 5.1 서브에이전트; `prereg_reviews_2026-10-11/review_FIGHSROOM16e4.md`: MUST 1 · SHOULD 3 · NIT 8 — 전부 반영, §5) → **v2 2026-10-11 16:54 CDT = 실행 커밋**(§5 를 채운 커밋 = 이 문서를 마지막으로 바꾸는 커밋; `code/run_fighsroom16e4.sh` 는 HEAD 가 그 커밋일 때만 돈다). 실행 커밋 뒤 §1 을 바꾸지 않는다.
- 사용자 지시(2026-10-11 CDT, 원문): "figure 가 왜 그리다 만거 같지?" · "근데 proposed 보면 6dB에서 BLER가 9 dB 보다 낮게 나오는데 좀 이상하지 않아? 다시 점검해봐" · "figure는 매끄러운 곡선이 나타나는게 좋아". 이 세션이 제시한 세 선택지(세로축만 조정 / 0 실패 점에 화살표 / 고SNR 시행을 8 배로) 가운데 사용자가 매끄러운 곡선을 택했다 → 원고 주 그림에 쓴 방식(`NEXT_EXPERIMENTS_FIGHS16e4.md`)을 Sionna RT 방 그림에 적용한다.
- **틀(새 규칙 없음)** = `NEXT_EXPERIMENTS_FIGHS16e4.md` v2 의 §1 (새 시행 10000..30479, n = 20480, chunk 40, +6 / +9 / +12 / +15 dB, 단계 C 대조 → 단계 R 실행 → `eval_accept --skip0/--points` + (f) → 집계표, 그림 merge 규칙, **보고 전용**)을 SRB 의 세 행으로 읽는다. 각 arm 의 체크포인트·적합·조정값·플래그는 `NEXT_EXPERIMENTS_ROOM16e4.md` §5 (SRB) 의 것 그대로다.
- **보고 전용**: 새 판정 라벨·검정을 등록하지 않는다. 등록된 판정점·라벨·"전부"·"멀어진다" 문장은 ROOM16e4 §6 의 것 그대로다. **b\* → V1 의 판정점 −3 / 0 / +3 dB 는 이 보강이 건드리지 않는 SNR 이다. baseline 16 개의 판정점은 앵커별이라 R0-pilot@1 (+3/+6/+9), R1-turbo (0/+3/+6), R2-ours-G (0/+3/+6), R3-bigamp (+9/+12/+15), R4-llr (+9/+12/+15), R4-scvamp (+3/+6/+9), OMP-pilot (0/+3/+6) 은 +6 dB 이상을 포함한다 (`pairB_SPSRB.txt`); 그 판정·라벨은 원 raw (n = 2560) 로 그대로이고 새 시행으로 다시 판정하지 않는다 — 그림의 +6..+15 dB 점은 그 판정과 다른 시행 집합이며 캡션에 밝힌다.**
- **작성 시점 공개**: 작성자와 사용자는 SRB 의 n = 2560 결과를 전부 봤다 — 고SNR 의 실패 수(예: V1 +6 / +9 / +12 / +15 dB = 3 / 4 / 0 / 0, b\* 6 / 5 / 1 / 1, genie 1 / 0 / 0 / 0; ROOM16e4 §6.4), 그림 `F21srb_col`, 그리고 고SNR 실패 블록의 사후 진단(`results/review_next/SRBB16e4_highsnr_fail.txt`: V1 의 +6 · +9 dB 실패 7 블록은 모두 최대 특이값 에너지 비중 0.82–0.94 인 채널이고 같은 블록에서 다른 arm 도 실패). 시행을 늘리는 이유는 "점이 튀어 보인다" 는 것이며, 어느 arm 에 유리한지를 보고 정한 것이 아니다. 새 시행 10000..30479 는 SRB 에서 한 번도 쓰인 적이 없다(SRB 의 모든 raw 의 최대 skip 은 2520; ALD 개발 시행은 2560..3071; 희소 조정·GB′ 는 다른 스트림). **단, 풀 prior 에서 시행 하나는 테스트 풀 52,353 쌍에서의 복원 추출이다** — 새 시행은 "새 추첨 + 새 데이터·잡음" 이지 새 채널이 아니다(SNR 당 서로 다른 쌍은 약 1.7 만 개이고 시행 0..2559 의 쌍과도 겹친다); 집계표의 Wilson 구간은 이 풀에 대한 평균 BLER 의 것이다(검토 S-2).
- **범위**: prior SRB 의 그림 한 장(범례 11 곡선). 경로 풀 SRP (PATH16e4) 는 넣지 않는다 — 그 풀의 GMM 은 씨앗 초기화라(PATH16e4 §6.8) 원고에 쓸지부터 사용자 결정이 필요하다; 쓰게 되면 같은 틀로 따로 등록한다.

---

## 1. 고정되는 것 (FIGHS16e4 v2 §1 과 다른 곳만)

| 항목 | 값 |
|---|---|
| 행 (`code/run_fighsroom16e4.sh` 의 `ROWS`, 이 순서) | **FHSRBB16e4**: `--prior SRB --cell C2 --stagec-ckpt ckpt/d2sx_SRB_N160000_a1_best.pt` (sha ed437f21af15c305, role best), b\* = gmm1024 (ll_val 97.00871495382869), arm `R0-pilot R1-turbo R2-ours-G R3-bigamp M-ours-bstar M-ours-dscore-C-V1 R5-genie`, 대조 기준 `raw_SRBB16e4`. **FHSPSRB**: `--sparse-file results/sparse/pick_SRB_C2.json` (sha 4c6da315c701b9d4), arm `SBL-loop SBL-pilot OMP-pilot R5-genie`, genie 재생 기준 FHSRBB16e4, 대조 기준 `raw_SPSRB`. **FHALDSRB**: `--stagec-ckpt …_best.pt --ald-file /home/HTJ/t2/conf/results/ald/ald_PILSRB_hisnr.npz` (절대 경로 — meta·수용 (f) 가 이 문자열을 본다) (새 시행의 ALD 추정: `ald.py regen --set hisnr` (CPU) + `estimate --set hisnr` (GPU), 동결된 `tune_PILSRB.json` e0adb06cce792093 그대로), arm `ALD-pilot R5-genie`, genie 재생 기준 FHSRBB16e4, 대조 기준 `raw_ALDSRB`. 세 행 모두 fits `gmm_fits_D2_SRBB16e4` |
| 시행·SNR | 새 시행 10000..30479 (`common.HISNR_SKIP0`), n = 20480, chunk 40, SNR +6 / +9 / +12 / +15 dB; 수신기 CPU, 16 반복; 시행 스트림은 SRB 의 것(`common.trial_rng`, PID 13) → 테스트 풀 복원 추출(ROOM16e4 §1) |
| 스크립트 | `code/run_fighsroom16e4.sh` = `code/run_fighs16e4.sh` 에서 다음만 바꾼 것(머리말에 원문; 나머지 줄은 같다): 등록·로그 이름, `ROWS` 표, 새 실행의 전제 검사를 **이 스크립트의 태그로만** 한정(FIGHS16e4 의 `raw_FH*`·`FHC*`·`ald_*_hisnr.npz` 는 디스크에 그대로 둔다), ALD 기록(`PILSRB`: 테스트 추정 sha a3d249188f9c061a, 테스트 파일럿 sha 97a2d08640fef383), 회전 없는 ALD 행에서 `--rotation` 생략, HISNR raw 전제 삭제(재사용하는 행이 없다). 단계 C 대조(테스트 청크 0 에서 원 raw 와 비트 동일; ALD 추정기 대조)가 OK 가 아닌 행은 돌리지 않는다 |
| 수용 | FIGHS16e4 §1 그대로(스크립트): `eval_accept.py --skip0 10000 --n 20480 --points C2:6,9,12,15` (청크 계획, meta ntrain / bstar gmm1024 / ll_val, 체크포인트 sha·role, genie 재생), (f) 모든 청크의 `run|git` == HEAD, SP 행 `meta|sparse` == pick, ALD 행 `meta|ald_file`. 통과한 행만 집계표 `results/review_next/fighs_<TAG>.txt` 를 얻는다 |
| 그림 규칙 | `cd ~/t2/conf && CUDA_VISIBLE_DEVICES= python -B ~/t2/conference/figures/paper_f21dmc.py SRB hs > ~/t2/conference/figures/records/paper_f21srbhs.txt` → **`F21srbhs_col.{pdf,png}`**: 곡선마다 −3 / 0 / +3 dB = 원 raw (n = 2560, 등록된 판정의 시행), +6 / +9 / +12 / +15 dB = `raw_FH<원 태그>` (n = 20480) — `fighs_merge.merge` (한 점 = 한 raw, 합치지 않는다; 실패 수는 집계표와 대조 assert). y 축은 `ROOM` 분기의 규칙을 **그려지는 값**에 적용((2e-4, 1.2) — 0 실패 점이 없고 모든 점·막대 끝이 2e-4 위일 때 — 아니면 (3e-5, 1.2)); 0 실패 점에서는 곡선이 끊기고 Perfect CSI 에만 Wilson 상한 화살표(n = 20480 에서 실패 1 건인 점의 Wilson 하한 8.6e-6 은 축 아래로 잘린다 — FIGHS16e4 와 같다). "오르는 칸"(SNR 이 오르는데 BLER 이 오르는 칸)은 한쪽 Fisher p 와 함께 기록에 적는다 — **평활화·재실행·점 삭제는 하지 않는다**. 세 행 가운데 수용되지 않은 것이 있으면 그 곡선은 n = 2560 점을 유지하고 기록·캡션에 밝힌다(`FIGHS_N2560`). ROOM16e4 의 등록 그림 `F21srb_col` (전 SNR n = 2560) 은 그대로 둔다 |
| 다중성·해석 | 새 검정 없음. 집계표의 Wilson 구간은 점별 서술이다(풀 평균 BLER). −3 / 0 / +3 dB 와 +6 dB 이상은 서로 다른 시행 집합이라는 점을 캡션에 적는다(주 그림과 같음). **b\* → V1 의 판정점 −3 / 0 / +3 dB 는 이 보강이 건드리지 않는 SNR 이다. baseline 16 개의 판정점은 앵커별이라 R0-pilot@1 (+3/+6/+9), R1-turbo (0/+3/+6), R2-ours-G (0/+3/+6), R3-bigamp (+9/+12/+15), R4-llr (+9/+12/+15), R4-scvamp (+3/+6/+9), OMP-pilot (0/+3/+6) 은 +6 dB 이상을 포함한다 (`pairB_SPSRB.txt`); 그 판정·라벨은 원 raw (n = 2560) 로 그대로이고 새 시행으로 다시 판정하지 않는다 — 그림의 +6..+15 dB 점은 그 판정과 다른 시행 집합이며 캡션에 밝힌다.** |
| 비용 [추정] | FHSRBB16e4 ≈ 65 분, FHSPSRB ≈ 50 분, FHALDSRB ≈ 10 분 = 새 시행 4 SNR × 20480 의 파일럿 재생성(CPU) + ALD 추정(GPU 한 장) + runner (CPU 192 워커) |

(§2 라벨·§4 현황 절은 없다 — 보고 전용이라 라벨이 없고, 현황은 §5 에 적는다; FIGHS16e4 의 §0.5 식 사전 ALD 재현 검사는 따로 하지 않고 스크립트의 단계 C 대조가 그 역할을 한다 — 대조가 OK 가 아니면 그 행은 돌지 않는다.)

## 3. 미리 적는 예측 (빗나가면 그대로 쓴다)

1. n = 20480 에서 Proposed (V1) 의 실패 수는 +6 dB > +9 dB 이다(BLER 이 SNR 과 함께 내려간다). 채점: 실패 수 비교.
2. V1 · b\* · Perfect CSI 의 곡선에 Fisher p < 0.05 인 "오르는 칸" 이 없다(+3 → +6 dB 칸 포함).
3. +6 dB 와 +9 dB 에서 실패 수 V1 ≤ b\* (점추정).
4. +15 dB 에서 V1 의 실패 수 ≤ 5 / 20480.
5. 세 행 모두 대조·수용 통과(`FIGHS_DONE ok=3 fail=0`).

## 5. 실행 전 기록

v2 2026-10-11 16:54 CDT (Opus 5.5). 검토(MUST 1 · SHOULD 3 · NIT 8) 반영: **M-1** baseline 판정점에 +6 dB 이상이 들어 있다는 사실과 "다시 판정하지 않는다" 를 머리말·§1 에 정정; S-1 `DECISIONS.md` 에 사용자 결정 줄; S-2 풀 prior 에서 새 시행의 뜻; S-3 그림 명령 원문; N-1 스크립트의 회전 로그 문구(`rotation ${V:-none}`; 동작 불변); N-3 절대 경로; N-5 잘리는 막대; N-6 · N-7 절 번호와 단계 C; N-8 비용 문구; N-2 · N-4 는 메모로 남김(조정 기록은 추적·clean 검사로 고정; 그림 기록의 `raw_<원 태그>` 꼬리표는 덧붙는 블록이 설명). 검토가 확인한 것: `bash -n`, 원 스크립트와의 diff = 머리말에 적은 변경뿐, 모든 sha·파일·전제(HEAD 1404d315 기준), `ald.py --set hisnr`, `eval_accept` 의 gmm1024, SP 행의 `-:-`, genie 재생, `dmimo` 의 시행 → 테스트 풀, 집계표의 `R0-pilot@1`, `hs_tag`, 그림의 y 규칙. **실행 커밋 = 이 문서를 담은 커밋**(그 뒤 `FIGHS_DONE` 까지 main 커밋 없음). 실행 시작 전 상태: `raw_FHSRBB16e4` · `raw_FHSPSRB` · `raw_FHALDSRB` · `ald_PILSRB_hisnr.npz` 없음.

## 6. 결과 (기록 2026-10-11 18:32 CDT, Opus 5.5 — 전사만, 해석 없음; 이 절은 추가만 한다)

### 6.1 실행·운영 기록 (생성기 `prereg_audit_2026-10-11/s6_fighsroom_gen.py`; 수치는 모두 기록 파일에서 읽음)

`bash code/run_fighsroom16e4.sh` **한 번**, tmux `fighsroom`, 10-11 17:01 CDT 시작(git 193776a1 = 실행 커밋; 시작 줄 하나, 재개 없음). 단계 C (관측된 시험 청크 0 의 대조) 10-11 17:03 CDT: 3 receiver control(s) OK, 1 ALD estimator control(s) OK. `FIGHS_DONE ok=3 fail=0` 10-11 18:31 CDT. ABORT · SKIP · INVALID 줄: 0 개.

| 행 | 시작 (CDT) | runner | 작업 (done / exists) | 수용 (CDT) | 수용 판정 | manifest git · config_hash | 대조 |
|---|---|---|---|---|---|---|---|
| FHSRBB16e4 | 10-11 17:03 | 39.0 분 · 2048 작업 · 192 워커 | 2048 / 0 | 10-11 17:42 | rc=0; ACCEPT: OK -- FHSRBB16e4; ACCEPT (f): OK | 193776a1 · cef74db071b50187 | CONTROL: OK |
| FHSPSRB | 10-11 17:42 | 41.6 분 · 2048 작업 · 192 워커 | 2048 / 0 | 10-11 18:24 | rc=0; ACCEPT: OK -- FHSPSRB; ACCEPT (f): OK | 193776a1 · cef74db071b50187 | CONTROL: OK |
| FHALDSRB | 10-11 18:28 | 1.5 분 · 2048 작업 · 192 워커 | 2048 / 0 | 10-11 18:31 | rc=0; ACCEPT: OK -- FHALDSRB; ACCEPT (f): OK | 193776a1 · cef74db071b50187 | CONTROL: OK · CONTROL-ALD: OK |

수용 파일의 (f) 줄(raw 당 청크 수 · `run|git` · pick · ald · raised):

- `(f) raw_FHSRBB16e4: 2048 chunk files, run|git ['193776a1']; pick -; rotation -; ald -; raised trials per arm (= failures, report only) 0`
- `(f) raw_FHSPSRB: 2048 chunk files, run|git ['193776a1']; pick results/sparse/pick_SRB_C2.json; rotation -; ald -; raised trials per arm (= failures, report only) 0`
- `(f) raw_FHALDSRB: 2048 chunk files, run|git ['193776a1']; pick -; rotation -; ald /home/HTJ/t2/conf/results/ald/ald_PILSRB_hisnr.npz; raised trials per arm (= failures, report only) 0`

집계표 머리말:

- `# run_fighsroom16e4 git 193776a1 raw_FHSRBB16e4 C2: failures@16 / n, BLER, 95% Wilson -- REPORT-ONLY (FIGHSROOM16e4 §1); load_raw warnings 0`
- `# run_fighsroom16e4 git 193776a1 raw_FHSPSRB C2: failures@16 / n, BLER, 95% Wilson -- REPORT-ONLY (FIGHSROOM16e4 §1); load_raw warnings 0`
- `# run_fighsroom16e4 git 193776a1 raw_FHALDSRB C2: failures@16 / n, BLER, 95% Wilson -- REPORT-ONLY (FIGHSROOM16e4 §1); load_raw warnings 0`

### 6.2 원고 범례 11 곡선 — BLER@16 실패 수 (+6 / +9 / +12 / +15 dB; 새 시행 n = 20480 과 원 raw n = 2560)

| 곡선 (arm) | 출처 | +6 dB: k / 20480 (BLER, 95 % Wilson) | +9 dB: k / 20480 (BLER, 95 % Wilson) | +12 dB: k / 20480 (BLER, 95 % Wilson) | +15 dB: k / 20480 (BLER, 95 % Wilson) | 원 raw k / 2560 (+6 / +9 / +12 / +15) |
|---|---|---|---|---|---|---|
| M-ours-dscore-C-V1 | raw_FHSRBB16e4 | 45 (2.20e-03, [1.64e-03, 2.94e-03]) | 10 (4.88e-04, [2.65e-04, 8.99e-04]) | 3 (1.46e-04, [4.98e-05, 4.31e-04]) | 4 (1.95e-04, [7.60e-05, 5.02e-04]) | 3 / 4 / 0 / 0 |
| ALD-pilot | raw_FHALDSRB | 81 (3.96e-03, [3.18e-03, 4.91e-03]) | 25 (1.22e-03, [8.27e-04, 1.80e-03]) | 7 (3.42e-04, [1.66e-04, 7.05e-04]) | 11 (5.37e-04, [3.00e-04, 9.62e-04]) | 11 / 3 / 2 / 0 |
| M-ours-bstar | raw_FHSRBB16e4 | 90 (4.39e-03, [3.58e-03, 5.40e-03]) | 23 (1.12e-03, [7.48e-04, 1.68e-03]) | 11 (5.37e-04, [3.00e-04, 9.62e-04]) | 6 (2.93e-04, [1.34e-04, 6.39e-04]) | 6 / 5 / 1 / 1 |
| R2-ours-G | raw_FHSRBB16e4 | 438 (2.14e-02, [1.95e-02, 2.35e-02]) | 135 (6.59e-03, [5.57e-03, 7.80e-03]) | 37 (1.81e-03, [1.31e-03, 2.49e-03]) | 19 (9.28e-04, [5.94e-04, 1.45e-03]) | 49 / 18 / 4 / 2 |
| R1-turbo | raw_FHSRBB16e4 | 917 (4.48e-02, [4.20e-02, 4.77e-02]) | 287 (1.40e-02, [1.25e-02, 1.57e-02]) | 87 (4.25e-03, [3.45e-03, 5.24e-03]) | 34 (1.66e-03, [1.19e-03, 2.32e-03]) | 108 / 44 / 10 / 6 |
| R3-bigamp | raw_FHSRBB16e4 | 2861 (1.40e-01, [1.35e-01, 1.45e-01]) | 2507 (1.22e-01, [1.18e-01, 1.27e-01]) | 2813 (1.37e-01, [1.33e-01, 1.42e-01]) | 2481 (1.21e-01, [1.17e-01, 1.26e-01]) | 382 / 291 / 342 / 331 |
| R0-pilot@1 | raw_FHSRBB16e4 | 2630 (1.28e-01, [1.24e-01, 1.33e-01]) | 978 (4.78e-02, [4.49e-02, 5.08e-02]) | 376 (1.84e-02, [1.66e-02, 2.03e-02]) | 173 (8.45e-03, [7.28e-03, 9.80e-03]) | 318 / 140 / 53 / 17 |
| SBL-loop | raw_FHSPSRB | 261 (1.27e-02, [1.13e-02, 1.44e-02]) | 73 (3.56e-03, [2.84e-03, 4.48e-03]) | 17 (8.30e-04, [5.18e-04, 1.33e-03]) | 13 (6.35e-04, [3.71e-04, 1.09e-03]) | 22 / 7 / 3 / 4 |
| SBL-pilot | raw_FHSPSRB | 306 (1.49e-02, [1.34e-02, 1.67e-02]) | 85 (4.15e-03, [3.36e-03, 5.13e-03]) | 23 (1.12e-03, [7.48e-04, 1.68e-03]) | 13 (6.35e-04, [3.71e-04, 1.09e-03]) | 35 / 12 / 4 / 2 |
| OMP-pilot | raw_FHSPSRB | 607 (2.96e-02, [2.74e-02, 3.21e-02]) | 217 (1.06e-02, [9.28e-03, 1.21e-02]) | 63 (3.08e-03, [2.41e-03, 3.93e-03]) | 53 (2.59e-03, [1.98e-03, 3.38e-03]) | 76 / 39 / 8 / 6 |
| R5-genie | raw_FHSRBB16e4 | 17 (8.30e-04, [5.18e-04, 1.33e-03]) | 5 (2.44e-04, [1.04e-04, 5.71e-04]) | 1 (4.88e-05, [8.62e-06, 2.77e-04]) | 1 (4.88e-05, [8.62e-06, 2.77e-04]) | 1 / 0 / 0 / 0 |

Perfect CSI (R5-genie) 의 실패 수는 세 raw 에서 같다: FHSRBB16e4 [17, 5, 1, 1] · FHSPSRB [17, 5, 1, 1] · FHALDSRB [17, 5, 1, 1] → 동일.

0 실패 점 (n = 20480): 없음.

그림 기록 `records/paper_f21srbhs.txt` 의 '오르는 칸' (SNR 이 오를 때 BLER 이 오르는 칸, 한쪽 Fisher p; 보고만): 3 줄.
- `M-ours-dscore-C-V1  @16  45/20480 10/20480 3/20480 4/20480   (raw_FHSRBB16e4)   rising: +12->+15 dB p=0.5`
- `ALD-pilot           @16  81/20480 25/20480 7/20480 11/20480   (raw_FHALDSRB)   rising: +12->+15 dB p=0.24`
- `R3-bigamp           @16  2861/20480 2507/20480 2813/20480 2481/20480   (raw_FHSRBB16e4)   rising: +9->+12 dB p=3.7e-06`

### 6.3 §3 예측 채점

1. V1 의 실패 수 +6 dB > +9 dB → **적중** (45 대 10).
2. V1 · b\* · Perfect CSI 에 Fisher p < 0.05 인 오르는 칸 없음 → **적중** (오르는 칸의 p: M-ours-dscore-C-V1 [0.5], M-ours-bstar 없음, R5-genie 없음).
3. +6 · +9 dB 에서 실패 수 V1 ≤ b\* → **적중** (45 대 90, 10 대 23).
4. +15 dB 에서 V1 실패 수 ≤ 5 / 20480 → **적중** (4).
5. `FIGHS_DONE ok=3 fail=0` → **적중** (ok=3 fail=0).

### 6.4 그림과 공개 사항

- **그림** `conference/figures/F21srbhs_col.{pdf,png}`, 기록 `records/paper_f21srbhs.txt` (§1 의 명령 그대로, `FIGHS_DONE` 뒤): 실패 수 = 집계표(assert), y 축 (3e-05, 1.2) — 0 실패 점은 없지만 Perfect CSI 의 +12 · +15 dB 점(1 / 20480 = 4.9e-05)이 2e-4 아래라서 규칙의 둘째 범위. **[감사 S2 — 원인을 하나만 적었다]** 2e-4 아래의 점·막대 끝은 여섯이다: Perfect CSI +12 · +15 dB (1 / 20480 = 4.9e-05; Wilson 하한 8.6e-06), Proposed +12 · +15 dB (3 · 4 / 20480 = 1.5e-04 · 1.9e-04; 하한 5.0e-05 · 7.6e-05), GMM b\* +15 dB 와 Perfect CSI +9 dB 의 Wilson 하한 (1.3e-04 · 1.0e-04) — 제안 곡선 자신의 +12 · +15 dB 점도 (2e-4, 1.2) 에는 들어가지 않는다. −3 / 0 / +3 dB 는 원 raw (n = 2560) 그대로다.
- 그림 스크립트 `paper_f21dmc.py` 는 이 그림을 만들 때 작업 트리에 미커밋 변경 하나가 있었다[감사 N3: 파일 mtime 10-11 17:17 CDT — FHSRBB16e4 runner 시작 17:03 뒤·그림 18:31:58 전; diff 는 `HSREG` 세 줄과 `HS` 주석, 7 줄]: 기록 문구의 등록 이름을 prior 별로 넣는 `HSREG` (SRP 의 같은 보강 `NEXT_EXPERIMENTS_FIGHSPATH16e4.md` 를 위해; 이 §6 과 같은 커밋). SRB 의 출력은 그대로다 — 바뀐 스크립트로 `paper_f21dmc.py SRB` 를 다시 돌린 기록이 커밋된 `paper_f21srb.txt` 와 바이트 동일.
- 새 시행의 ALD 추정 파일 `results/ald/ald_PILSRB_hisnr.npz` sha256[:16] a7b2c943b3968846 (git 밖).
- 실행 중 main 커밋 없음(HEAD 193776a1 그대로; 스크립트의 HEAD 검사 통과). 함께 돈 것(결과 중립 — 수신기는 CPU 결정적): SRP 시드 학습(GPU 0, 등록 밖), ROOM16e4 의 기록 감사(17:01 CDT 까지)와 FIGHSPATH16e4 의 사전 검토(둘 다 Fable 서브에이전트, CPU 3 스레드 이하, 읽기 전용), 그림 스크립트의 회귀 확인 렌더 두 번(스크래치 출력).
- 실행 중 작성자는 이 실행의 진행 줄 수(`grep -c done`)와 운영 로그만 봤고 결과 파일은 `FIGHS_DONE` 뒤에 처음 열었다. 그 사이 사용자에게 SRP 의 n = 2560 미리보기 한 장을 보냈다(SRB 의 새 결과와 무관).
- 기록 감사(Fable)는 이 절을 쓴 뒤에 받는다 — 결과는 추가 줄로 적는다.

### 6.5 기록 감사 (Fable 5.1 서브에이전트, 보고서 파일 mtime 2026-10-11 18:56 CDT; `prereg_audit_2026-10-11/audit_FIGHSROOM16e4.md`, 재계산 `recompute_fighsroom.py` → `.out`, 등록 도구 재실행 `rerun_fighsroom_accept_FH*.txt`)

감사 대상 = 커밋 ed265304 (§6 과, 같은 커밋에 들어간 ROOM16e4 §6.8–6.10 · `docs/EXPERIMENTS.md` 의 새 행 5 개 · `DECISIONS.md` 두 줄). **이 문서 §6.1–6.4 의 수치·채점·인용 오류 0**: 자체 판독기로 새 raw 3 × 2048 청크·원 raw 3 × 448·대조 raw·ALD npz 를 직접 읽어 약 1,050 값 + 배열 비교 33,135 건(검사 묶음 58 개 중 56 통과; 나머지 2 는 아래 다른 문서의 정정). 시행 계획(10000..30479, SNR 당 한 번씩)·모든 청크의 `run|git` 193776a1 (`+dirty` 없음)·meta·SP 의 `meta|sparse` == pick·ALD 의 `meta|ald_file`·genie 세 raw 비트 동일·대조 비교 0 다름·집계표 56 행과 Wilson 문자열·6.2 의 44 칸과 원 raw 열·오르는 칸 3 개의 p (0.5 / 0.24 / 3.7e-06)·0 실패 점 없음·예측 다섯 적중·시각표(시작 줄 하나, 재개 없음, 실행 중 커밋 없음)·y 축 규칙 일치; `eval_accept` 세 행 재실행 → 모두 `ACCEPT: OK`; `paper_f21dmc.py SRB` · `SRB hs` 를 커밋된 스크립트로 다시 그린 기록 2 개·PDF/PNG 4 개가 **바이트 동일**(6.4 의 `HSREG` 진술 확인).

**MUST 1 · SHOULD 2 · NIT 4 — 모두 반영(이 문서의 수치·채점 불변; 기록 2026-10-11 18:58 CDT, Opus 5.5)**: **M1** (다른 문서) `docs/EXPERIMENTS.md` 의 SRP · SRB 주 실행 행에 적힌 "eig 파일럿" 은 틀렸다 — 두 풀 모두 **DFT 파일럿**(raw 이름 `…_Tp4_dft_…`; T2b 규칙 erank(Rt) 3.756 · 3.991 ≥ 3.6); 도시 풀 행의 문구를 옮기다 생긴 오류, 그 두 행을 고침. S1 (다른 문서) ROOM16e4 6.1 의 "배증당 증가" 수열 정정(+11.3 · +14.2 · +12.2 · +11.0 · +10.1 · +7.8 nat) — 제자리 표시 + `audit_ROOM16e4.md` 에 정정 줄. S2 y 축 범위의 원인 여섯을 6.4 에 적음(제자리 표시). N1 §1 의 비용 추정 65 / 50 / 10 분 대비 실측 runner 39.0 / 41.6 / 1.5 분 + 새 시행의 ALD 재생성·추정 약 3 분, 전체 17:01 → 18:31 CDT. N2 그림 기록의 "Asserts passed: counts = pairB …" 는 병합 **전** n = 2560 실패 수에 대한 것임을 hs 모드 기록 문구에 명시(`paper_f21dmc.py`; `paper_f21srbhs.txt` 를 다시 만듦 — 그림 파일은 바이트 동일). N3 미커밋 변경의 시각(6.4 제자리). N4 6.1 · 6.4 의 "tmux `fighsroom`" · "회귀 확인 렌더 두 번" · "결과 파일은 `FIGHS_DONE` 뒤에 처음" · "SRP 미리보기 한 장" 은 저장소에 증거가 없는 **세션 기록 기준** 진술이다(간접 증거인 파일 시각들은 일치). 감사가 확인하지 못한 것: 그 진술들, GPU 0 의 시드 학습, 풀 통계(§0)의 원 재계산.

감사 메모(정정 아님): 감사 중 `prereg_audit_2026-10-11/highsnr_fail_SRB.py` 에 `SKIP0` 모드가 추가됐다(10-11 18:51 CDT; 기본 모드의 출력은 커밋된 `SRBB16e4_highsnr_fail.txt` 와 바이트 동일 — 확인함) — 아래 6.6.

### 6.6 추가 줄 — 사후 진단: +12 · +15 dB 의 Proposed 실패 블록 (2026-10-11 18:58 CDT; 등록 밖·보고 전용)

사용자 질문 "15dB에서 왜 위로 튀지?" (그림에서 Proposed 가 +12 dB 3 건 → +15 dB 4 건). `prereg_audit_2026-10-11/highsnr_fail_SRB.py FHSRBB16e4 SRB 10000` → `results/review_next/FHSRBB16e4_highsnr_fail.txt` (새 raw 만 읽고 채널을 시행 스트림에서 다시 만든다; genie 재생 정렬 검사 네 SNR 모두 OK): V1 이 실패한 블록은 +12 dB 시행 1853 · 15558 · 19518, +15 dB 시행 3420 · 4014 · 9512 · 12742 — 서로 다른 채널 일곱 개이고, 최대 특이값 에너지 비중 0.854 · 0.936 · 0.980 / 0.988 · 0.991 · 0.846 · 0.821 (전체 시행의 중앙값 0.82), 일곱 건 모두 같은 시행에서 b\* 또는 R2-ours-G 가 함께 실패(한 건은 genie 도). V1 의 반복별 실패 수(반복 1 · 2 · 4 · 8 · 16)는 +12 dB 76 → 6 → 3 → 3 → 3, +15 dB 41 → 9 → 4 → 4 → 4 로 줄기만 한다. 시행 스트림은 SNR 마다 따로다(20480 시행 가운데 서로 다른 풀 채널 약 1.7 만 개). 이에 따라 사용자가 +12 · +15 dB 의 시행을 4 배(n = 81920)로 늘리기로 했다("2번 해") — 별도 등록 `NEXT_EXPERIMENTS_FIGHSX16e4.md`.
