# NEXT_EXPERIMENTS_U28NR32SBL — UMi28 C9 (32×4) 에서 receiver loop 의 개발 BLER 로 조정한 SBL-loop 하나 (E3′) — 사전 등록 v2.3

작성 2026-10-17 CDT (Opus 5.5). 사용자 과제 `conf/results/review_next/prompts/PROMPT_SERVER_SBL32.md` (웹 채팅 2026-10-16 CDT; 공통 규칙 `gcap/PROMPT_SERVER_COMMON.md`). 이 문서의 §0–§4 와 튜닝 규칙 (§1.2) 은 **개발 BLER 을 보기 전에** 브랜치 `e3-sbl32` 에 커밋한다 (main 은 U28NR32GCAP 실행 중이라 커밋 금지). 실행 커밋 = §5 를 더하고 `e3-sbl32` 를 main 에 병합한 커밋 (GCAP 이 끝난 뒤).

### v1 → v2 (적대적 검토 Fable 5.1 `prereg_reviews_2026-10-17/review_U28NR32SBL.md`: MUST 3 · SHOULD 7 · NIT 4 — 전부 반영; 개발 BLER 미열람)
- M1 분석 입력 (ALD 추정 파일) 을 main 에 복사·sha 대조, 경로는 절대경로 (§1.3). M2 실패 정의·계산 스크립트 `sbl32/select_dev.py` (이 커밋) · 미완 후보 규칙 (§1.2 3). M3 범위 끝 판정 (§1.2 5).
- **v2.1 (2026-10-17 CDT, 개발 BLER 미열람 — cold 개발 실행 중)**: Codex 교차 검토 (gpt-6-astra · effort max, 사용자 승인; `reviews/20261018-025441-prompt_sbl32_code.md`) — 수신기 코드 결함 0, `select_dev.py` 결함 3 전부 수용: 청크마다 (10, 16) 모양·`run|iters` 16·`run|n` 10 검사, `--allow-missing` 이 일부 청크만 있는 후보도 열지 않고 제외, final 이 warm 두 개 = cold 상위 둘을 강제 (`run_dev.sh warm` 도 `select_dev_cold.out` 의 TOP2 와 대조). 규칙 자체는 v2 그대로.
- **v2.2 (2026-10-17 20:0x CDT, 개발 BLER 미열람 — cold 단계 끝, 선택 전)**: `select_dev.py` 의 genie 대조가 NaN 을 다르게 봐서 (R5-genie 의 nmse 는 규약상 NaN) 같은 시행인데도 멈췄다 → `np.array_equal(..., equal_nan=True)` 로 고침 (출력 전에 멈춰 BLER 미열람). 그리고 cold 실행 중 v2.1 이 `run_dev.sh` 를 제자리에서 고쳐 그 실행의 마지막 줄 (`SBL32DEV_DONE`) 이 깨졌다 — 후보 8 개의 'end … rc=0' 이 결과이고, 완료 줄은 사유와 함께 손으로 덧붙였다 (`logs/sbl32_dev.log`). 규칙은 그대로.
- **v2.3 (2026-10-18 14:23 CDT, test 미사용)**: §5 기록 (fbd96825) 뒤 Codex 교차 검토 (gpt-6-astra · max, 사용자 승인; `reviews/20261019-035934-prompt_pretest_sbl32_e5_gcap6.md` 묶음 A) — `run_sbl32.sh` · §5 는 결함 0 (수용 인자 · 실패 분기 · 재개 · sha · G 재계산 확인), 결함 1 = `pair_baselines.py` 가 raise 블록의 `load_raw` NOTE 까지 무결성 실패로 보아 SBL-loop 에 raise 가 하나라도 있으면 등록 분석이 돌지 않음 → Codex 작성 수정 (`reviews/20261019-041514-codex_write_pairb_note.md`; NOTE 는 출력 머리에 남기고 WARNING 만 거부; 기록 pairB 3 개 (UMi28 C9 · D2 C9 · UMi28 C6) 바이트 동일, 합성 raise → 실패 +1 로 집계, 합성 WARNING 은 거부) — Claude 가 diff 검토. `--r0 at1` 누락은 `SBL-loop → V1` 판정에 영향 없음 (Codex 확인) — §1.3 명령 그대로. 규칙·선택·수치 변경 없음.
- S1 test 메모리·시간 = test fits 폴더 복사본으로 개발 한 청크 (§1.3). S2 `code/run_sbl32.sh` 를 동결 커밋에 (전제·수용·run|git·meta|sparse 검사, §4). S3 동률의 2 차 기준 (§1.2 3). S4 `run_dev.sh` 결함 4. S5 `--pairs` (§1.3). S6 시간 선별 경계의 무감도·`--resume` 중 main 커밋 (§1.2 2, §1.4). S7 예측 1 채점 (§3). NIT 4 (§0, §1.1, §1.2 6, §1.2 3).

## 0. 알고 있는 것 (판정에 쓰지 않는다)

- 셀 기록 (`U28NR32B16e4`, raw `/home/HTJ/t2_wtS/conf/raw_U28NR32B16e4`, 448 청크): 판정점 −3/0/+3 dB 실패 합 b\* (kron K4096) 958, V1 599, genie 127; 표 B `b* → V1` 391:32 (i); SNR@0.1 격차 +2.29 dB [+1.98, +2.61] (RESULTS §21.4; `gcap_compare.py` old = new 재현).
- 기존 SBL-loop (SPARSE16e4) 은 8×4 · 16×4 에서만 돌았다. n_em 은 파일럿 전용 개발 NMSE 로 SNR 별로 골랐고 (UMi28 C2: ρ 8, n_em 3), 호출마다 평탄 γ 에서 시작했다 (warm start 없음). 이 셀 (C9) 에서는 SBL 튜닝·평가가 없다.
- 이 셀의 개발 시행 2560..3839 는 다른 튜닝·검사가 썼다 (`raw_S1D2C9`·`raw_S1U28C9` 2560..3839, `raw_U28NR32`·`raw_snrC9` 2560..2719, `raw_U28NR32GCAPdev` 2560..2599 등 — 2026-10-17 조사). SBL 튜닝에 쓰인 적은 없다. ALD 개발 입력 `results/ald/pilots_PILU28NR32_dev.npz` 는 2560..3071. 어느 raw 도 3840..4159 와 겹치지 않는다 (검토 N1 재확인).
- **비용 프로브** (Codex, `conf/code/sbl_probe.py`; 1 스레드, 개발 시행 2560 한 블록 0 dB, cold, 블록 결과는 출력하지 않음; `results/review_next/sbl32/probe.out`): 블록당 시간 (s) — ρ 4: n_em 3 / 10 / 25 = 4.8 / 12.4 / 39.1; ρ 8: 33.9 / 43.3 / 122.0; ρ 16: 124.1 / 295.3 / 774.2. 블록당 ep_site 16 회. 최대 RSS 0.88–1.18 GB. **BLER 은 아무 후보에서도 보지 않았다.**

## 1. 고정되는 것

### 1.1 arm 과 셀

- 셀: UMi28 C9 (`--prior UMi28 --cell C9`), N_r 32, N_t 4, T 16, T_p 4 (송신 상관 고유벡터 파일럿), QPSK, K_b 42, 외부 반복 16, CPU complex128 (01_RULES §9.3).
- **SBL-loop** = `arms.SparsePrior(Cs, 32, 4, ρ, n_em[, warm])` 를 `route_a(..., "gmm_site")` (b\* 와 같은 EP 수신기) 에 넣은 것. 사전 `dft_dict(32, 4, ρ)` (M = 128 ρ²), MacKay 고정점, N×N Woodbury. Cs = R2 와 같은 표본 공분산 (`fit_UMi28_Nr32_fullK32_n160000.npz` 의 Chat, sha256 d572e0ac…e215) — SPARSE16e4 §1 규칙.
- warm start (§1.2 4 단계에서만 후보): 같은 시행 안의 연속된 ep_site 호출에서 γ 를 직전 호출의 끝 값에서 이어 n_em 단계; 새 시행의 첫 호출은 평탄 초기값 (코드 `e3-sbl32` 의 커밋 629b350c; cold 경로는 SPARSE16e4 raw 와 비트 동일 — §4).
- 실행 인자: `--sparse-arms ρ,n_em,1,1[,W]` (OMP 의 ρ·L 자리는 1 — OMP-pilot 은 만들어지지만 `--arm` 에 없어 돌지 않는다; 다섯째 값 1 = warm; cold 는 4 값이나 5 값-0, 두 표기의 `meta|sparse` 는 같은 문자열 — Codex 회귀 14/14) `--arm SBL-loop R5-genie`.

### 1.2 개발 튜닝 (test 미사용; 이 규칙은 개발 BLER 을 보기 전에 커밋한다)

1. **개발 블록**: SNR −3 / 0 / +3 dB (b\* 판정점) 마다 **시행 3840..4159 (n = 320)**, 모든 후보가 같은 시행 (짝). `--skip0 3840 --n 320 --chunk 10`. 태그 `U28NR32SBLd_r<ρ>e<n_em>[w]`, fits 폴더 = fullK32 복사본 하나 (SBL-loop · genie 는 Cs 만 쓴다).
2. **시간 선별 (BLER 전, 프로브 값으로)**: test 예상 시간 = 블록 시간 × 17920 / 96 이 **30 h 를 넘는 후보는 제외** (= 블록 579 s 초과). 근거: test 창 (10/18–21) 을 QAM16 (E5) test 와 나눠 쓰고, 원고 반영 마감 (10/24 18:00 CDT) 전에 감사·전사를 끝낸다. 이 기준은 프로브 시간을 본 뒤에 정했다 (BLER 미열람). → **제외: ρ 16 · n_em 25 (774 s, 40.2 h)**. 남는 cold 후보 8 개. 경계 양쪽 후보가 295.3 s 와 774.2 s 라 임계값을 [295.3, 774.2) s 어디에 두어도 같은 집합이다. 96 워커 가정은 E5 와 창을 나누면 낙관적이다 — 실제 추정은 §5 (S1 의 청크 시간 · 허용 워커).
3. **선택 지표**: F(c, s) = Σ_시행 [SBL-loop 의 blk_err@16 ≠ 0 또는 비유한 (raise 시행)] (`pair_baselines.fails` 와 같은 규칙, 01_RULES §4); 지표 = (F(−3) + F(0) + F(+3)) / 960, 작을수록 좋다. 동률의 2 차 기준 = 프로브 블록 시간 (짧은 쪽; warm 변형은 같은 (ρ, n_em) cold 의 값 — 개발 벽시계는 CPU 분할에 좌우돼 쓰지 않는다: 과제의 '전체 수신 시간' 을 이렇게 읽는다), 3 차 = cold 먼저. SNR 마다 따로 고르지 않는다. 계산은 `sbl32/select_dev.py cold|final` (이 커밋; 무결성: SNR 마다 10 시행 청크 32 개로 3840..4159, 후보마다 run|git 하나, R5-genie 가 후보 사이 비트 동일, meta|sparse = 후보; 출력 `sbl32/select_dev_<단계>.out`). 청크가 모자란 후보는 같은 HEAD 에서 이어 돌려 채운 뒤에만 비교하고, 10/18 CDT 안에 못 채우면 **제외** 하고 사유 (미완, BLER 아님) 를 적는다. 동률·역전이 잦아도 재실행·표본 추가 없이 이 규칙으로만 가른다 (n 320 이면 후보당 실패 합이 수십 수준).
4. **warm start**: cold 8 후보 가운데 지표 상위 둘 (동률은 3 의 규칙) 에 대해서만 warm 변형을 같은 개발 블록에서 돈다.
5. **동결**: cold 8 + warm 2 = 10 개를 3 의 지표로 비교해 하나를 고른다 (warm 과 그 cold 가 동률이면 cold). 끝 판정: 고른 ρ ∈ {4, 16} 이거나 n_em ∈ {3, 25} 이거나 (ρ 16, n_em 10) (ρ 16 열의 조사 상한 — 시간 선별) 이면 "[조사 범위 끝: <축>, <사유>]" 를 붙인다 (`select_dev.py final` 이 출력). 범위는 늘리지 않는다.
6. 개발 실행의 CPU: NUMA 0 의 48 스레드 (`0-23,96-119`; 사용자 승인 2026-10-17 CDT, GCAP 실행과 동시) — 후보마다 프로브 시간에 비례해 스레드를 나눠 같은 시각쯤 끝나게 한다. 결과·선택은 CPU 배치와 무관하다 (시행 스트림은 (prior, Nr, T, Tp, SNR) 로 고정; BLAS 1 스레드). 시작 전 `ps` 로 E5 (QAM16) 의 runner 가 없는지 확인하고, 있으면 순서를 묻는다. 실행 = `bash results/review_next/sbl32/run_dev.sh cold`, 그다음 `warm <상위 둘>` (tmux).

### 1.3 test 평가 (동결 뒤; 실행 = main 병합 커밋에서 `bash code/run_sbl32.sh [--resume]`, tmux)

| 항목 | 고정 값 |
|---|---|
| 주 실행 (태그 `U28NR32SBL`) | `CUDA_VISIBLE_DEVICES= taskset -c 24-47,120-143,72-95,168-191 python code/runner.py run --testbed D2 --prior UMi28 --cell C9 --ntrain 160000 --chunk 40 --n 2560 --arm SBL-loop R5-genie --sparse-arms <ρ>,<n_em>,1,1[,1] --worker-gb <G> --tag U28NR32SBL` — 7 SNR (−12 … +6 dB) × test 0..2559 = 448 청크, 외부 반복 16 |
| fits 폴더 (복사본, 링크 아님) | `results/gmm_fits_D2_U28NR32SBL/` = fullK32 (d572e0ac…e215) + 기존 kronK4096 (2d72a434…f569) — 기존 raw 의 meta (bstar kron 4096, ll_val 152.23176788511105) 와 같게 |
| 같은 시행 확인 | 주 실행의 R5-genie 를 기존 raw 와 **448 청크 전부·모든 시행** 비트 대조 (`eval_accept.py --ref-raw /home/HTJ/t2_wtS/conf/raw_U28NR32B16e4`) |
| V1 · b\* · 다른 baseline | 기존 raw 재사용 (base `raw_U28NR32B16e4`, PIL `raw_PILU28NR32`, ALD `raw_ALDU28NR32`, 모두 `/home/HTJ/t2_wtS/conf/`) |
| CPU · 메모리 | 워커 = min(96, 448, ⌊0.8·MemAvailable / G⌋). G·시간: **test fits 폴더의 바이트 복사본** `gmm_fits_D2_U28NR32SBLdev` (2 파일) 으로 고른 설정의 개발 청크 하나 (시행 4160..4199, 0 dB, `--arm SBL-loop R5-genie`, 1 스레드, `taskset -c 191` 이 비면 그곳) 를 돌려 실행 트리 최대 RSS → G = RSS × 1.05 를 0.5 GB 단위로 올림, 청크 시간 t → 총시간 ≈ ⌈448 / 워커⌉ × t (§5). 개발 튜닝 폴더 (fullK32 하나) 는 b\* prior 를 만들지 않아 메모리를 대표하지 않는다 (검토 S1) |
| 수용 | `eval_accept.py --tag U28NR32SBL:-:-:C9 --prior UMi28 --ntrain 160000 --bstar kron --kron-K 4096 --ll-val 152.23176788511105 --ref-raw /home/HTJ/t2_wtS/conf/raw_U28NR32B16e4` OK; 그리고 `run_sbl32.sh` 의 두 검사: 448 청크 모두 `run|git` = HEAD, 모두 `meta|sparse` = §5 설정의 `json.dumps(sort_keys=True)` 문자열. 셋 다 OK 일 때만 분석 표를 결과로 쓴다 |
| 분석 | `cd ~/t2/conf` (main 병합 커밋의 코드). 전제: `results/ald/ald_PILU28NR32.npz` · `results/ald/pilots_PILU28NR32_test.npz` 를 `/home/HTJ/t2_wtS/conf/results/ald/` 에서 **복사** (링크 아님), 복사 전후 sha256 동일 — §5 에 적고 `run_sbl32.sh` 가 대조 (main 의 `pair_baselines.py` 가 `C.CONF/results/ald/` 를 읽는데 그 파일은 t2_wtS 에만 있다; t2_wtS 의 코드에는 `--add-baselines` 가 없다). `pair_baselines.py --base /home/HTJ/t2_wtS/conf/raw_U28NR32B16e4 --pil /home/HTJ/t2_wtS/conf/raw_PILU28NR32 --ald /home/HTJ/t2_wtS/conf/raw_ALDU28NR32 --est PILU28NR32 --extra /home/HTJ/t2/conf/raw_U28NR32SBL --add-baselines SBL-loop --cell C9 --prior UMi28` (출력 `results/review_next/pairB_U28NR32SBL.txt`) → 표 B `SBL-loop → V1` (판정점 = 앵커 자동, 판정점별 exact 양측 부호검정 p < .05, 2/3 규칙, power guard), R_X (paired bootstrap), 절대 격차, SNR@0.1 격차 [90% paired, B 2000]. 보고 전용: 같은 인자에 `--pairs 'M-ours-bstar>SBL-loop'` 를 더한 두 번째 호출 (출력 `pairB_U28NR32SBL_bstar.txt`; 라벨을 붙이지 않는다) |
| 끝 표시 | 로그 `logs/run_sbl32.log`, `SBL32_DONE ok=<n> fail=<n>` |

### 1.4 예외·중단

- runner 비정상 종료 · 메모리 초과: 같은 HEAD 에서 `--resume`. genie 재생·run\|git 불일치 → 표 B 를 결과로 쓰지 않고 사용자에게 보고.
- 판정하지 못함 ((iii)·(iv)) 도 완료된 결과. SNR 점·표본을 늘리지 않는다. test BLER 을 본 뒤 설정을 다시 고르지 않는다.
- 개발 튜닝이 10/18 CDT 안에 끝나지 않을 것 같으면 사용자에게 알린다.
- 실행 중 다른 세션이 main 에 커밋하면 `--resume` 의 run|git 검사가 막는다 → 사용자에게 알린다 (E5 QAM16 이 같은 창).

### 1.5 하지 않는 것

SBL-pilot · OMP-pilot 을 32×4 에 추가 ("baseline 16 개 전부" 채우기), SNR 별 튜닝, 조사 범위 밖 ρ · n_em, off-grid 방법, test BLER 을 본 뒤의 재선택.

## 2. 라벨·문장

### 2.1 표 B `SBL-loop → V1`
기존 표 B 라벨 문자열 그대로: (i) "V1 이 SBL-loop 보다 적게 실패" (판정점 2/3 이상 유의, 같은 방향) / (ii) 반대 방향 / (iii) 판정하지 못함 (유의 방향 없음) / (iv) power guard 미달. 문장: "UMi 32×4 에서 loop BLER 로 조정한 SBL-loop (ρ = …, n_em = …, cold|warm) 대비 V1 …". 고른 설정이 조사 범위 끝이면 "[조사 범위 끝]" 을 붙인다.

### 2.2 쓰지 않는 문구
"최적 SBL", "SBL 로는 부족", "동등", "비열등". SBL 결과가 V1 보다 좋거나 비슷하면 그대로 주요 비교에 넣는다 (과제 목적).

## 3. 미리 적는 예측 (개발·test BLER 미열람; §6 에서 적중 / 빗나감)

1. 개발 지표는 ρ 가 클수록 (같은 n_em 에서) 좋아진다 (32 수신 안테나의 각도 해상도). 채점: n_em 3 · 10 열에서 F합(ρ4) > F합(ρ8) > F합(ρ16), n_em 25 열에서 F합(ρ4) > F합(ρ8) (엄격 부등호) 가 모두 성립하면 적중, 하나라도 어긋나면 빗나감.
2. 고른 설정은 cold 이다 (warm 이 지표를 이기지 못한다).
3. 표 B `SBL-loop → V1` 은 (i).
4. 보고 전용 `b* → SBL-loop`: b\* 가 SBL-loop 보다 적게 실패하는 방향 (SPARSE16e4 의 8×4 결과와 같은 방향).

## 4. 선행 작업·검토

- **코드 (Codex, 사용자 승인 2026-10-17 CDT; worktree `~/t2_wtE3`, 명세 `reviews/spec_sbl32_code.md`, 보고 `reviews/<stamp>-codex_write_sbl32.md`)**: `arms.SparsePrior` warm 선택지 (기본 꺼짐), runner `--sparse-arms` 다섯째 값, `code/sbl_probe.py`. 회귀: SPARSE16e4 raw 청크 (cold) 비트 동일, warm 단위 검사. 정답 사례 (golden-writer, 구현 미열람): 9 사례 (경계 4) — Claude 가 구현에 연결해 대조 — 9 사례 PASS, 의도적 결함 2 종 검출 (`sbl32/golden/check_e3.out`). 검토 (Claude): diff · 회귀 출력 · 전후 main 상태 비교.
- 적대적 검토 1 회 (Fable 5.1 subagent, 사용자 승인 2026-10-17 CDT): v1 (c197c234) → `prereg_reviews_2026-10-17/review_U28NR32SBL.md` MUST 3 · SHOULD 7 · NIT 4 전부 반영 = v2 (이 커밋) → 개발 튜닝 시작.
- test 실행 스크립트 `code/run_sbl32.sh` (GCAP `run_gcap.sh` 틀) 는 동결 (= 실행) 커밋에 넣는다: 전제 (code/·Demo/ 청결, fits 2 파일·링크 아님·sha, ALD 복사본 sha, 기존 raw 448 청크 ×3, 다른 `runner.py run` 없음, raw 폴더 비었음) → 주 실행 → eval_accept → run|git 검사 → meta|sparse 검사 → (셋 OK 일 때만) pair_baselines 두 번 → 종료 코드 = 실패 수.

## 5. 평가 전 고정 기록 (튜닝 결과; test 미사용)

(개발 튜닝 뒤: 후보별 실패 수 (−3 / 0 / +3 dB) · 지표 · 블록 시간, warm 둘, 선택 결과와 범위 끝 여부, 개발 실행 최대 RSS → `--worker-gb`, 추정 test 시간, 코드 커밋, 동결 = 실행 커밋)

기록 2026-10-18 13:52 CDT (Opus 5.5). 원본: `sbl32/select_dev_cold.out` · `sbl32/select_dev_final.out` (출력 그대로), 로그 `logs/sbl32_dev.log` · `logs/run_D2_U28NR32SBLd_*.log` · `logs/sbl32_rss_smoke.log`. **test 시행은 어느 단계에서도 쓰지 않았다.**

- **개발 실행** (`run_dev.sh cold`, 10-17 12:09 CDT 시작, git d3993c8d, NUMA 0 48 스레드 — §1.2 6; `run_dev.sh warm 4,3 8,3`, 20:07 → 20:27 CDT, git fe7e911b). 후보 raw 의 `run|git`: cold 7 개 d3993c8d, r16e10 79ea962c (첫 청크가 v2.1 커밋 뒤에 쓰였다), warm 둘 fe7e911b — `git diff d3993c8d 79ea962c -- conf/code Demo` · `git diff d3993c8d fe7e911b -- conf/code Demo` 모두 0 바이트 (수신기 코드 같음). cold 실행의 끝 줄 사정은 v2.2 머리말.
- **cold 8 (지표 = (F(−3) + F(0) + F(+3)) / 960, `select_dev_cold.out`)**: r4e3 86 · 35 · 21 = 142 (0.147917) / r8e3 90 · 35 · 23 = 148 / r16e3 90 · 35 · 23 = 148 / r8e10 153 / r4e10 154 / r16e10 155 / r4e25 159 / r8e25 161; raise 0 (모두). r8e3 · r16e3 동률 → 2 차 기준 프로브 시간 (33.9 s < 124.1 s) → **TOP2 = (4, 3), (8, 3)**.
- **warm 2** (`select_dev_final.out`): r4e3w 86 · 38 · 22 = 146, r8e3w 88 · 37 · 22 = 147.
- **선택 (§1.2 5)**: `PICK U28NR32SBLd_r4e3 rho 4 n_em 3 warm False metric 0.14791666666666667 range_edge ['rho', 'n_em']` → **SBL-loop = ρ 4, n_em 3, cold** (`--sparse-arms 4,3,1,1`; `meta|sparse` = `{"L": 1, "n_em": 3, "rho_omp": 1, "rho_sbl": 4}`). 범위 끝 → 라벨 문장에 "[조사 범위 끝: ρ, n_em]" (ρ 4 = 조사 하한, n_em 3 = 조사 하한).
- **메모리·시간 스모크 (§1.3)**: `cd ~/t2_wtE3/conf && CUDA_VISIBLE_DEVICES= nice -n 10 taskset -c 191 python results/review_next/sbl32/rss_smoke_sbl.py 4,3,1,1` (tmux `sblsmoke`, 10-18 13:46 → 13:48 CDT, git fe7e911b; `sbl32/rss_smoke_sbl.py` 는 이 커밋에 추가). dev fits `gmm_fits_D2_U28NR32SBLdev` = t2_wtS `gmm_fits_D2_U28NR32B16e4` 의 fullK32 (d572e0ac…e215) + kronK4096 (2d72a434…f569) 바이트 복사본 (스크립트가 sha256 대조). 청크 `raw_U28NR32SBLdev/D2_C9_UMi28_Nr32_T16_Tp4_eig_snr0_skip4160_n40.npz` (시행 4160..4199, 0 dB; meta bstar kron · kron_K 4096 · ll_val|kron 152.23176788511105 · meta|sparse 위와 같음 · stagec_ckpt_id 없음): 청크 108 s, rc 0, wall 110 s, **최대 RSS 6.580 GB → G = 7.0** (6.580 × 1.05 = 6.91 → 0.5 GB 단위 올림). SBL-loop BLER 은 출력하지도 열지도 않았다 (진행 줄은 R5-genie 만 찍는다).
- **워커·시간 추정**: MemAvailable 1003263876 kB (10-18 13:51–13:53 CDT 사이, 이 기록 직전) → ⌊0.8 · 956.8 / 7.0⌋ = 109 → 워커 = min(96, 448, 109) = **96** (runner 가 시작 때 다시 잰다). 총시간 ≈ ⌈448 / 96⌉ × 108 s = 5 × 108 = 540 s ≈ 9 min (단독 1 스레드 청크 시간; 동시 실행 경합은 반영하지 않음).
- **ALD 복사 (§1.3 분석 행)**: 10-18 13:51 CDT `cp /home/HTJ/t2_wtS/conf/results/ald/{ald_PILU28NR32.npz,pilots_PILU28NR32_test.npz} /home/HTJ/t2/conf/results/ald/` (링크 아님, git 미추적 데이터 — 다른 `ald_*.npz` 와 같음). sha256 원본 = 복사본: `ald_PILU28NR32.npz` 25a4152e006bf86be0f978c4b8e30fa7f146752b8cae71634e2f956ed590cf46, `pilots_PILU28NR32_test.npz` a901fa5ce8934b81c4da91440ff0dde282e5f7e3b9be1f2fa184015116eb79db.
- **test 실행 스크립트** `code/run_sbl32.sh` (이 커밋; GCAP `run_gcap.sh` · E5 `run_e5.sh` 틀): 전제 (code/·Demo/ 청결; 이 문서와 `sbl32/sbl32_s5.txt` 추적·청결; HEAD = `sbl32_s5.txt` 를 마지막으로 바꾼 커밋; FREEZE 가 HEAD 의 조상이고 그 뒤 code/·Demo/ 변경 없음; fits 폴더 2 파일·링크 아님·sha; ALD 복사본과 원본의 sha = §5; 기존 raw 448 청크 ×3; 다른 `runner.py run` 없음; raw 폴더 비었음, `--resume` 이면 기존 청크가 읽히고 run|git = HEAD) → 주 실행 (§1.3 명령, `taskset -c 24-47,120-143,72-95,168-191`) → 수용 ① eval_accept ② run|git · meta|sparse (448 청크) → 둘 다 OK 일 때만 pair_baselines 두 번 → `SBL32_DONE ok=<n> fail=<n>`, 종료 코드 = 실패 수. `bash -n` 통과, 미실행.
- `sbl32/sbl32_s5.txt` (실행 커밋에서 main 에 더한다): `FREEZE <이 커밋>` / `SPARSE 4,3,1,1` / `WGB 7.0` / `ALD 25a4152e…cf46` / `PILT a901fa5c…79db` (전체 자리).
- **실행 커밋 (2026-10-18 14:28 CDT, main)**: 이 문서 · `sbl32/sbl32_s5.txt`: FREEZE d6a76fbf / SPARSE 4,3,1,1 / WGB 7.0 / ALD 25a4152e…cf46 / PILT a901fa5c…79db (전체 자리는 파일) 를 더하는 커밋. FREEZE d6a76fbf = e3-sbl32 (73282a1e) 와 e5-qam16 (83b7f4f6) 를 main 에 병합한 커밋 (code/ 는 두 브랜치의 자동 병합 — arms.py · runner.py 는 겹치지 않는 hunk). 병합 확인 (`results/review_next/merge_check_e3e5.sh`, 10-18 14:23 → 14:27 CDT, git d6a76fbf, 로그 `logs/merge_check_e3e5.log`): 세 개발 스모크 청크 (SBL 4160..4199 0 dB · E5 UMi · D2 5480..5519 +12 dB) 를 병합 코드로 다시 돌려 브랜치 청크와 데이터 배열 16 · 43 · 43 개 모두 바이트 동일. `pair_baselines.py` 를 main 에서 기록 인자 (`--r0 at1`, 기존 raw 절대경로, ALD 는 main 복사본) 로 다시 돌린 출력 = t2_wtS `pairB_U28NR32B16e4.txt` (경로가 적힌 머리 줄 외 바이트 동일). 세 실행은 `results/review_next/run_e3e5_chain.sh` 가 차례로 띄운다 (SBL32 → E5 UMi → E5 D2; 각 스크립트가 다른 runner 가 돌면 거부).

## 6. 결과 (이 절은 추가만 한다)

### 6.1 실행 기록 (기록 2026-10-18 14:47 CDT, Opus 5.5 — 원자료 전사; 판정은 6.2)

- **실행**: 실행 커밋 13f05fb1 (FREEZE d6a76fbf; `git diff d6a76fbf 13f05fb1 -- conf/code Demo` 0), tmux `e3e5` 의 `run_e3e5_chain.sh` 첫 단계. `logs/run_sbl32.log`: 10-18 14:29 CDT start (resume=0, sparse 4,3,1,1, WGB 7.0) → 14:45 CDT runner exit 0 → accept_eval OK · accept_raw OK · pairB OK · pairB_bstar OK → **SBL32_DONE ok=4 fail=0**. 재개 없음.
- **runner** (`logs/run_D2_U28NR32SBL.log`): 메모리 가드 112 → 워커 96 (:3), 448 청크 (:4), finished in 16.0 min (:453); 청크 시간 평균 194 s · 중앙 151 s (100–441; 96 워커 동시).
- **raw** `raw_U28NR32SBL/` 448 npz, 값 집합 `run|git` {13f05fb1}, `meta|sparse` {`{"L": 1, "n_em": 3, "rho_omp": 1, "rho_sbl": 4}`}, `meta|bstar` {kron}, `meta|kron_K` {4096}, `meta|ll_val|kron` {152.23176788511105}, `meta|worker_gb` {7.0}, `meta|jobs` {96}, `run|iters` {16}, `run|seed` {20260926}, `meta|ntrain` {160000.0}; stagec_ckpt_id 없음; SBL-loop raise 0.
- **수용**: `sbl32/U28NR32SBL_accept.txt` "ACCEPT: OK" (R5-genie 를 기존 raw 와 448 청크 · 모든 시행 비트 대조 포함); accept_raw (run|git · meta|sparse 448 청크) OK. pair_baselines 두 출력 머리 `integrity: OK`, `# NOTE` 줄 0 (raise 없음).

- **절차 기록 (2026-10-18 15:37 CDT)**: 이 §6 초안은 체인이 E5 UMi 를 돌리던 10-18 14:47 CDT 에 썼다 — WORK_QUEUE 에 적은 '두 등록 문서 수정 금지' 와 어긋난다. 영향 없음: SBL32 는 SBL32_DONE 으로 끝나 재개가 필요 없었고, `run_e5.sh` 는 E5 문서 · s5 만, runner 의 +dirty 는 code/ · Demo/ 만 본다. verifier 지적 (범위 끝 사유, 대조 문구의 머리 줄) 반영은 체인이 끝난 뒤 (15:36 CDT 이후).

### 6.2 결과 · 라벨 (`pairB_U28NR32SBL.txt`, 보고 전용 `pairB_U28NR32SBL_bstar.txt`)

- **표 B `SBL-loop → V1`** (앵커 SBL-loop; 판정점 −3 · 0 · +3 dB): 부호검정 @16 −3 dB 325:3 (p 2.2e-92), 0 dB 216:10 (1.5e-51), +3 dB 110:6 (7.5e-26), pooled 651:19 (p 1.3e-165); POWERED, V1 적게 실패 3/3 → **(i)**. SNR@0.1 격차 (SBL-loop − V1) **+3.14 dB [90 % +2.78, +3.54]**, censored 0 %. 절대 격차 −3 dB F_X − F_V1 = 322 / 2560. R_X −3 dB (primary) 0.552 [0.519, 0.587], 판정점 (secondary) 0.572 [0.548, 0.597].
- **SBL-loop 실패 수 / 2560** (−12 … +6 dB): 2522 · 1772 · 979 · 671 · 386 · 174 · 83 (V1 2219 · 1068 · 595 · 349 · 180 · 70 · 27; b\* 2280 · 1207 · 761 · 509 · 304 · 145 · 62; genie 846 · 423 · 227 · 88 · 30 · 9 · 3 — 기존 raw).
- **라벨 (§2.1)**: **(i)** "V1 이 SBL-loop 보다 적게 실패" — 문장 "UMi 32×4 에서 loop BLER 로 조정한 SBL-loop (ρ = 4, n_em = 3, cold) 대비 V1 이 적게 실패 [조사 범위 끝: ρ · n_em, 둘 다 조사 하한 (ρ 4, n_em 3)]". (§1.2 5 의 틀 "[조사 범위 끝: <축>, <사유>]" 를 채운 것; §5 의 "[조사 범위 끝: ρ, n_em]" 은 사유를 괄호로 따로 적었다.)
- **보고 전용 `b* → SBL-loop`** (라벨 없음; 앵커 b\*, 판정점 −3 · 0 · +3): 34:196 · 47:129 · 23:52, pooled 104:377 (a = b\* 만 실패); b\* 가 3/3 점에서 적게 실패; SNR@0.1 격차 (b\* − SBL-loop) −0.85 dB [−1.16, −0.62]; 판정점 실패 b\* 509 / 304 / 145, SBL-loop 671 / 386 / 174.
- **같은 출력의 나머지 (기존 raw 재계산, 기록과 같은 규칙)**: 등록 baseline 14 개 (b\* + 13, SBL-loop 포함) 모두 (i); X\* = V1-pilot (−3 dB 실패 440), R_X\* 0.259 [0.216, 0.301]; "등록된 baseline 전부와 멀어진다" 조건 MET (k = 14). 이 등록의 라벨은 SBL-loop → V1 하나뿐이다. SCALE16e4 기록 (t2_wtS `pairB_U28NR32B16e4.txt`, `--r0 at1`) 과 줄 단위로 대조하면, 경로가 적힌 머리 줄 (기록 쪽은 셸 머리말 · `# R0-pilot read at @1` 줄; 이 출력은 절대경로 · `extra0=13f05fb1` 이 붙은 한 줄) 외에 다른 것은 (a) R0-pilot 행 — 이 호출은 `--r0` 기본값 at16 이라 'R0-pilot' (+0 · +3 · +6 dB 575:7, 격차 +4.56 dB), 기록은 'R0-pilot@1' (903:0, +6.25 dB); 둘 다 (i) — (b) SBL-loop 행과 그것을 더한 요약 수 (12 → 13, 13 → 14) 뿐이고, 다른 baseline 행은 모두 같다.

### 6.3 예측 채점 (§3)

1. **빗나감** — n_em 3 열: F합 ρ4 142 < ρ8 148 = ρ16 148 (예측은 ρ 가 클수록 적은 실패); n_em 10 열 154 · 153 · 155, n_em 25 열 159 · 161 (`sbl32/select_dev_cold.out`).
2. **적중** — 고른 설정 cold (warm 146 · 147 이 cold 142 를 이기지 못함).
3. **적중** — 표 B `SBL-loop → V1` (i).
4. **적중** — 보고 전용 `b* → SBL-loop`: b\* 가 적게 실패 (3/3 점).

### 6.4 기록 감사 (Fable 서브에이전트, 2026-10-19 08:47–09:04 CDT 보고; `prereg_audit_2026-10-19/audit_U28NR32SBL.md`, 재계산 `recompute_sbl32.py` → `recompute_sbl32.out` · `.json`, 도구 재실행 `rerun_pairB_U28NR32SBL{,_bstar}_SBL.txt` · `rerun_accept_SBL.txt`)

감사 대상 = HEAD 9a2c9fd4 (실행 커밋 13f05fb1, FREEZE d6a76fbf). 자동 비교 **442 일치 / 0 불일치** — 실패 수 16 arm × 7 SNR, 표 B 14 쌍 × 7 줄 (판정점 · a:b · p 문자열 · POWERED · 라벨 · SNR@0.1 격차 + 90 % CI · 절대 격차 · R_X), 요약 4 줄, 보고 전용 b\* → SBL-loop 5 줄, NMSE 15 × 7, 개발 선택 10 후보 (F · 지표 · 동률 규칙 · TOP2 · PICK · 범위 끝) 가 `select_dev_*.out` 과 줄 단위 일치, meta 값 집합 11, genie 비트 대조 6,074,880 값 차이 0, 예측 4/4 채점 재현, §5 산술 3. `pair_baselines.py` 재실행 2 파일 바이트 동일, `eval_accept.py` ACCEPT OK. 수동 ≈ 90 값 가운데 시각 2 건 (N1) 외 일치. FREEZE 뒤 §0–§3 불변, FREEZE → 실행 커밋 코드 0, 실행 창 안 main 커밋 없음, s5 = §5 = 실제 sha256. test / 개발 분리: 시행 < 2560 의 SBL arm 은 이 test 실행 하나뿐 (개발 3840..4159, 스모크 · 병합 확인 4160..4199).

**MUST 0 · SHOULD 0 · NIT 2 — 반영 (판정 · 수치 불변; 머리말 · §0 · §5 는 고치지 않고 여기에 정정; 기록 2026-10-19 09:06 CDT, Opus 5.5)**: N1 실행 커밋 13f05fb1 의 시각은 2026-10-18 **14:29:07 CDT** (`logs/run_sbl32.log:1` 시작 14:29 CDT) — §5 (97 행) 와 DECISIONS 실행 시작 줄의 "14:28 CDT" 는 s5 파일 작성 시각 (mtime 14:28:22) 이다; 머리말 v2.2 의 "20:0x CDT" 는 그 줄이 든 커밋 fe7e911b 의 19:59:01 CDT. N2 §0 (16 행) 의 "최대 RSS 0.88–1.18 GB" 는 `probe.out` 의 878–1177 MiB 를 1000 으로 나눈 값 — 바르게는 878–1177 MiB (0.86–1.15 GiB); §0 은 판정에 쓰지 않고 G 는 §5 스모크로 따로 정했다. 감사가 확인하지 못한 것: MemAvailable · tmux 이름 · 사용자 승인 시점 (파일 없음); "BLER 미열람" 은 파일 순서로만 (모순 없음); verifier 검토 내용 → 보고 원문을 세션 기록에서 `qam16/verifier_s6_E5_SBL32_2026-10-18.md` 로 옮김 (1 차 · 2 차); 부트스트랩은 같은 시드 재구현 + 도구 재실행 + 다른 시드 [+2.79, +3.53].

### 6.5 Codex 교차 검토 (gpt-6-astra · max, 사용자 승인 "승인할게"; 10-19 21:16–21:28 CDT; `reviews/20261020-111602-prompt_s6_sbl32_e5.md`; 기록 2026-10-19 21:29 CDT, Opus 5.5)

§6 수치 (판정점 a:b · p · pooled · power guard · 라벨 (i) · 격차와 구간 · R · baseline 14 개) 를 raw 에서 따로 재계산해 모두 일치, 수용 재실행 OK, 청크 구멍 · 중복 없음, genie 바이트 동일, 개발 선택 (시행 3840..4159) · 예측 3/4 재현. **확인된 결함 1 — 수용 (기록 정정)**: 보고 전용 출력 `pairB_U28NR32SBL_bstar.txt` 4 행의 `-> (ii)` 는 `pair_baselines.py` 가 모든 쌍에 자동으로 찍는 줄이다. §1.3 대로 이 비교에는 라벨을 붙이지 않는다 — 이 줄은 등록 라벨이 아니며 인용하지 않는다 (§6.2 · §6.3 · RESULTS §27 · 원고 수치 표는 라벨 없이 옮겼다). 출력 파일과 분석 도구는 고치지 않는다. 판정 · 수치 불변.
