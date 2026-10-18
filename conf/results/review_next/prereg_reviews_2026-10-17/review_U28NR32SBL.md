# 적대적 검토 — NEXT_EXPERIMENTS_U28NR32SBL.md v1 + sbl32/run_dev.sh (worktree /home/HTJ/t2_wtE3, 커밋 c197c234)

검토자: Fable 5.1 subagent (사용자 승인 2026-10-17 CDT), 읽기 전용. 2026-10-17 12:1x CDT. 아래는 검토자 보고 원문 (Claude 가 이 파일로 옮김). 줄 번호는 v1 기준. 반영 = v2 (같은 폴더 상위의 등록 문서 머리 'v1 → v2').

파일을 만들거나 고치지 않았다. 실행한 것은 `bash -n`, 파일 존재·sha·raw meta 읽기, argparse 파싱 확인(taskset -c 2-3)뿐이다.

## MUST

**M1. §1.3 분석 명령이 main 에서 실행 불가 — `--est PILU28NR32` 의 입력 파일이 main 에 없다.**
- 근거: `pair_baselines.py:156–157` 은 `os.path.join(C.CONF, "results/ald", f"ald_{est}.npz")`·`pilots_{est}_test.npz` 를 읽고 `C.CONF` 는 코드가 있는 트리의 conf (`common.py:32`). `/home/HTJ/t2/conf/results/ald/` 에는 `tune_PILU28NR32.json` 만 있고 `ald_PILU28NR32.npz`·`pilots_PILU28NR32_test.npz` 는 `/home/HTJ/t2_wtS/conf/results/ald/` 에만 있다. 기존 표 B (`pairB_U28NR32B16e4.txt` 머리말 "run_scale2 git b4433d3c") 는 t2_wtS 에서 계산됐다. 그런데 t2_wtS 의 `code/pair_baselines.py` 에는 `--add-baselines`·`--pairs` 가 없다 → 거기서도 못 돈다.
- 문안: 분석은 `cd ~/t2/conf` 에서 main 병합 커밋의 코드로 돈다. 전제: 두 ald 파일을 t2_wtS 에서 복사 (링크 아님), sha256 을 §5 에 적고 `run_sbl32.sh` 가 대조. `--base/--pil/--ald/--extra` 는 절대경로 (`pair_baselines.py:131–135`).

**M2. 개발 선택 지표의 실패 정의·계산 절차가 없다 — raise 블록 처리와 미완 후보 처리가 결과를 본 뒤 정해질 수 있다.**
- 근거: §1.2 3 "실패 / 320" 만 있고, SBL-loop 이 예외를 내면 runner 는 그 시행을 NaN 행 + `failed=1` 로 남긴다 (`runner.py:574–579`). `pair_baselines.fails` (`:37–39`) 는 비유한 → 실패. 후보 하나의 runner 가 죽어 청크가 빠졌을 때 규칙도 없다.
- 문안: F(c,s) = Σ_trial [blk_err@16 ≠ 0 또는 비유한] — `pair_baselines.fails` 와 같은 규칙. 계산은 `sbl32/select_dev.py` (개발 BLER 전 커밋) 로. 청크가 모자란 후보는 같은 HEAD 에서 `--resume` 해 채운 뒤에만 비교; 10/18 CDT 안에 못 채우면 제외하고 사유 (미완, BLER 아님) 를 적는다.

**M3. "[조사 범위 끝]" 판정이 모호하다 — ρ 16 · n_em 10 이 뽑혔을 때 붙일지 결과를 본 뒤 정하게 된다.**
- 근거: §1.2 5 는 끝값을 "ρ 4 · 16, n_em 3 · 25 — 단 ρ 16 · n_em 25 는 시간 선별로 빠졌다" 라고만 적는다. ρ 16 열에서 조사된 n_em 의 최댓값은 10.
- 문안: 끝 판정: 고른 ρ ∈ {4, 16} 이거나 n_em ∈ {3, 25} 이거나 (ρ 16 이고 n_em 10) 이면 '[조사 범위 끝: <축>, <사유>]'. 범위는 늘리지 않는다.

## SHOULD

**S1.** `--worker-gb` 를 개발 실행의 RSS 로 정하는데 개발과 test 의 fits 폴더가 달라 워커 메모리가 다르다 (`build_our_arms` 는 arm 선택과 무관하게 b\* kron 4096 prior 를 모든 워커·청크에서 만든다 — `arms.py:349`, `:357–358`). 문안 (a): GCAP 선례대로 test 폴더의 바이트 복사본 (`gmm_fits_D2_U28NR32SBLdev`) 으로 개발 한 청크 (예: 4160..4199, 0 dB, 1 스레드) 를 돌려 G 와 청크 시간 t → §5. (b) test 폴더도 fullK32 하나 + 수용 인자 변경. (a) 가 SPARSE16e4 관례와 맞다.

**S2.** test 실행 스크립트 `code/run_sbl32.sh` 가 아직 없고, §1.3 주 실행 명령에 `--worker-gb`·`taskset`·`CUDA_VISIBLE_DEVICES=` 가 빠져 CPU 행과 어긋난다. 수용 행의 "run|git = HEAD, meta|sparse = §5 설정" 은 `eval_accept.py` 가 검사하지 않는다 (`:85–98`). 문안: §4 에 `run_sbl32.sh` 를 동결 커밋에 포함 (전제 → 주 실행 → eval_accept → run|git → meta|sparse (runner 가 `json.dumps(sort_keys=True)` 로 씀, `runner.py:463–464`) → pair_baselines 두 번 → 종료 코드 = 실패 수).

**S3.** 동률 규칙의 "프로브 블록 시간" 이 warm 변형에는 없다. 문안: 2 차 기준 = cold 의 프로브 블록 시간 (개발 벽시계는 CPU 분할에 좌우돼 쓰지 않는다 — 과제의 '수신 시간' 을 이렇게 읽는다); warm 변형의 시간 = 같은 (ρ, n_em) cold 의 값.

**S4.** `run_dev.sh` 결함 4: warm 단계가 인자를 `SEC` 키와 대조하지 않아 제외 후보·오타가 1 CPU 로 돈다 (시간 선별 위반 경로) → 대조 추가; 마지막 줄이 `log` 라 fail>0 이어도 rc 0 → `exit $fail`; `> logs/run_D2_$t.log` 는 재실행 때 앞 로그를 덮는다 → `>>`; 기존 raw 가 있을 때 (재개) 로그에 남기지 않는다 → 한 줄. 그 밖 확인: `SEC` = probe.out 일치; 슬라이스 20·9·9·3·2·3·1·1 = 48; runner 워커 = `len(os.sched_getaffinity(0))` (`runner.py:673–674`); BLAS 1 스레드 (`common.py:27`); 후보당 태스크 96; 예상 cold ≈ 4.5 h, warm ≈ 3–4 h; `--snr -3 0 3` 파싱 OK; fits SRC sha 일치; worktree `conf/code`·`Demo` clean.

**S5.** 보고 전용 `b* → SBL-loop` 은 `--pairs "M-ours-bstar>SBL-loop"` 로 낼 수 있다 (`pair_baselines.py:124–127, 220–232`). 문안: 두 번째 호출, 출력 `pairB_U28NR32SBL_bstar.txt`, 라벨 없음.

**S6.** 시간 선별의 임계값 (30 h) 이 프로브를 본 뒤 정해졌다 — 실질 영향은 없다: 경계 양쪽이 295.3 s 와 774.2 s 라 [295.3, 774.2) s 어디에 두어도 같은 집합. 그 사실과 96 워커 가정의 낙관성을 적는다. §1.4 에 "실행 중 다른 세션이 main 에 커밋하면 `--resume` 의 run|git 검사가 막는다 → 사용자에게 알린다" 추가.

**S7.** 예측 1 채점 규칙: n_em 3·10 열에서 F(ρ4) > F(ρ8) > F(ρ16), n_em 25 열에서 F(ρ4) > F(ρ8) (엄격 부등호) 가 모두 성립하면 적중.

## NIT

- N1. §0 개발 시행 조사에 ALD 개발 입력 `results/ald/pilots_PILU28NR32_dev.npz` (2560..3071) 추가. 어느 raw 도 3840..4159 와 겹치지 않음 (재확인).
- N2. §1.1 에 "cold 는 4 값 또는 5 값-0, 두 표기의 `meta|sparse` 는 같은 문자열" 을 적는다.
- N3. §1.2 6 에 "시작 전 `ps` 로 E5 의 runner 가 없음을 확인, 있으면 순서를 묻는다".
- N4. n 320 이면 동률·역전이 흔할 수 있다 — 재실행·표본 추가 없이 S3 의 규칙으로만 가른다는 한 줄.

## 확인했지만 결함이 아닌 것
- 기존 raw 셋 (`/home/HTJ/t2_wtS/conf/raw_{U28NR32B16e4,PILU28NR32,ALDU28NR32}`): 각 448 청크, run|git b4433d3c, meta bstar kron 4096 · ll_val 152.23176788511105, stagec id 463da87aa8dbfb61 — §1.3 수용 인자와 일치.
- `eval_accept --tag U28NR32SBL:-:-:C9 … --ref-raw <절대경로>`: 규격 적합.
- `pair_baselines`: extra raw 의 R5-genie 를 base 와 전 SNR 비교 (`:183–186`), 중복 arm 검사는 genie 제외, 시행 수 2560 검사 — SBL raw 구조와 맞음.
- warm 구현: 상태는 `CURRENT_TRIAL` 로만 이어지고 (`arms.py:259–274`), runner 가 시행마다 설정 (`runner.py:558`); arm 별 객체 분리; cold 경로 비트 동일은 Codex 회귀 14/14 로 뒷받침.
- Cs = `fits[("full",32)]["Chat"]` (`arms.py:350`) — SPARSE16e4 §1 과 일치; 개발/test fits 폴더 차이는 SBL-loop·genie 수치에 영향 없음 (S1 은 메모리 가드만의 문제).
- 라벨 방향 (§2.1) 은 GCAP §2.1 과 같은 `table_B` 읽기.
