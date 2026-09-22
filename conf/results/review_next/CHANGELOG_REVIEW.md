# CHANGELOG_REVIEW — review_next P0 수정

- 작성: 2026-09-23 KST, Claude Code (Opus 5.5)
- 기준: HEAD `4ad41df9` + 아래 미커밋 변경 (conf/code 6파일 수정 + `selftest_ckpt.py` 신규)
- 근거 문서: `REVIEW_AUDIT.md` (같은 디렉터리). 항목 id는 그 문서의 id.
- 범위: 사용자 승인 범위 **A(P0-1), B(§7 배선, C6 재실행 제외), D(P0-4), E(M3)**. C(실경로 비용 벤치), C6 재실행, NR16 GB′ 재산출, 기록 정정(F)은 **미실행**.
- 환경: torch 2.14.0+cu130, numpy 2.5.2, CPU 전용 테스트 (`CUDA_VISIBLE_DEVICES=""`). GPU 미사용.

## 1. 변경한 파일과 이유

| 파일 | 변경 | 대응 항목 |
|---|---|---|
| `conf/code/score.py` | `train()`: val 개선 시 그 epoch의 **전체 state**를 `<ckpt>_best.pt`(role='best')에 저장, `<ckpt>`는 role='last'(재개용). 두 저장 모두 `.tmp` → `os.replace` 원자적 저장. 저장 순서 best → last. state에 `stopped_by` 기록 | P0-1a |
| 〃 | 재개 시 `_already_stopped()`로 정지 규칙을 **학습 전에** 평가. 이미 끝난 체크포인트는 0 epoch 학습, 파일 무변경 (이전: 1 epoch 더 학습하며 평가된 ckpt를 덮어씀) | P0-1a 부수 위험 |
| 〃 | 발산 판정 `_bad_epoch()`: best ≥ 0이면 원래 식 `v > 3·best` 그대로, best < 0(VAE L6)이면 `v − best > 2·|best|`. 루프와 재개 판정이 같은 식을 씀 | P0 리뷰 발견 (HEAD부터 있던 결함) |
| 〃 | 재개 시 발산 카운터 `ndiv`를 hist 끝의 연속 bad 수로 복원 (이전: 0부터 다시 셈 → 중단·재개 run이 무중단과 다르게 멈춤) | P0 리뷰 발견 (HEAD부터) |
| 〃 | 신규 helper: `best_ckpt_path`, `_atomic_save`, `ckpt_identity`(sha256[:16]/epoch/best_epoch/role/Nr/Nt), `_val_draws`(train과 공유하는 고정 val draw), `val_loss_of`(체크포인트 val loss 재측정) | P0-1b, 테스트 |
| 〃 | `resolve_hp()`: rung별 argmin **attempt**를 기록하고 그 체크포인트의 hp를 상속. `sel`에 `base_attempt/base_ckpt/base_score` 추가 | P0-4 |
| `conf/code/runner.py` | `build_point`: Stage C arm 생성 조건을 `Nr != 8` → **체크포인트 자신의 (Nr,Nt) == 셀의 (Nr,Nt)** 로 | S7-b |
| 〃 | main 사전 점검: `--stagec-ckpt`가 선택된 어떤 셀과도 배열이 맞지 않으면 `run` 시작 전 거부 | s7/M1 |
| 〃 | `cmd_run` 출력: Stage C arm ON/ABSENT를 셀별로 출력 + 체크포인트 identity 출력 | s7/M1 |
| 〃 | raw meta에 `stagec_ckpt_id` 추가 (sha/epoch/best_epoch/role; 레거시 ckpt는 `BEST_WEIGHTS_UNAVAILABLE` 표시) | P0-1b |
| 〃 | `_best.pt`를 arm으로 평가할 경우 `fit_sec`은 last 파일의 `wall_sec`(patience tail 포함 전체 비용) | P0 리뷰 발견 |
| 〃 | `cmd_run`의 M-ours-dscore 안내 출력 조건을 290행 가드(`Nr in (8,16)`)와 일치 | 표시만 |
| `conf/code/analysis.py` | 셀 헤더에 `(kron K=…)` 출력, meta 출력 목록에 `stagec_ckpt_id` 추가 | M3 |
| `conf/code/train_nr16.py` | `gmm_selection` 전에 `A.D2_FITS = results/gmm_fits_D2_NR16` | S7-a |
| `conf/code/run_nr16.sh` | train 실패(비정상 종료) 시 BLER 단계로 가지 않고 ABORT | S7-c |
| `conf/code/selftest_V3.py` | 정리 루틴이 새 `_best.pt`도 삭제 (conf/ckpt에 selftest 잔여물 방지) | 부수 |
| `conf/code/selftest_ckpt.py` (신규) | P0-1/P0-4/정지 규칙 회귀 테스트 | 테스트 |

`Demo/`는 수정하지 않았다.

## 2. 기존 arm·기본값·재현성 보존

- **학습 수치 불변**: `selftest_V3` 검사 3 — 패치된 `score.train(jac_reg=0)`이 pre-patch 참조(git 5e2e77a)와 epoch 행·model/EMA 가중치(32+32 텐서 bitwise)·val loss가 동일. 발산 식 수정 후 재실행해도 PASS (best ≥ 0에서 식이 문자 그대로 동일).
- **기존 체크포인트·raw·결과 무변경**. 새 파일은 앞으로 학습할 때만 `<name>_best.pt`가 추가로 생긴다.
- **기존 Stage C 실행 재현**: Nr=8 체크포인트 + 8×4 셀(C1/C2/C5)은 이전과 같은 arm 집합 (C2 + `d2sx_N160000_a1.pt` → C-V0/V1/V4/V4b 확인). 4×4 셀은 이전처럼 ABSENT이며 사유 문자열만 배열 크기를 명시하도록 바뀜.
- **raw 스키마**: `--stagec-ckpt` 실행에만 meta 키 `stagec_ckpt_id`가 추가된다 (기존 키 불변).
- **동작이 바뀌는 경우** (의도된 수정):
  1. 이미 정지 규칙을 만족한 체크포인트를 재개하면 학습하지 않는다 (이전: 1 epoch 학습 후 덮어씀).
  2. 음수 loss(L6 VAE)의 발산 판정 — HEAD 식은 val이 음수가 된 뒤 모든 epoch를 bad로 봤다. 기록된 L6 run(09-20)은 발산 규칙 도입(09-21, c343853c) 이전에 학습되어 영향 없음.
  3. 발산 streak 도중 중단·재개한 run은 이제 무중단과 같은 epoch에서 멈춘다.
  4. `resolve_hp`는 argmin attempt의 hp를 쓴다. 기록된 ladder에서는 상속 필드가 attempt 간 동일해 결과 영향 없음 (REVIEW_AUDIT P0-4).

## 3. 실행한 테스트와 실제 출력

```
$ CUDA_VISIBLE_DEVICES="" ~/miniforge3/envs/torch/bin/python conf/code/selftest_ckpt.py
[stop] ok: sign-safe divergence predicate, trailing-bad count (resume restores ndiv=4)
[P0-4] ok: base L1 attempt 2 (score 0.1), param P_L1_a2
[1] ok: best @12 / last @15, files distinct
[2] ok: reload val best 7.688322e-01 (rec 7.688322e-01), last 7.709719e-01 (rec 7.709719e-01)
[3] ok: resume of finished ckpt trained 0 epochs, both files byte-identical
[4] ok: stop at 13 + resume == uninterrupted (last and best EMA identical)
[4b] ok: stop at 11 (< best @12) + resume rewrites _best.pt == uninterrupted
selftest_ckpt: ALL OK

$ OMP_NUM_THREADS=2 ~/miniforge3/envs/torch/bin/python conf/code/selftest_V3.py
  [PASS] epoch lines: 3 lines identical apart from the wall-clock column
  [PASS] weights: 32 model + 32 EMA tensors bitwise equal
  [PASS] val loss: 0.9901804327964783 == 0.9901804327964783
  ... (전 항목 PASS)
selftest_V3: OK -- all checks passed
```

판별력: 리뷰 agent가 pre-patch `score.py`로 `selftest_ckpt`를 돌려 실패함을 확인 (HEAD는 helper 부재로, helper만 붙인 HEAD는 `_best.pt` 부재로 실패; 재개 판정을 끈 변이는 [3]에서, alias 변이는 [1]에서 실패). 리뷰가 지적한 공허한 검사([4]가 재개 구간의 `_best.pt` 쓰기를 한 번도 거치지 않음)는 [4b] 추가로 보완.

스모크 (CPU, 파일 쓰기 없음 — 사전 점검은 `CMDS['run']`을 stub으로 바꿔 실행):

| 확인 | 결과 |
|---|---|
| `stagec_id_str(d2sx_N160000_a1.pt)` | `sha256[:16]=4443921ce8d5c4a1 epoch=1784 best_epoch=1764 role=legacy-last 8x4 \| BEST_WEIGHTS_UNAVAILABLE…` |
| `stagec_id_str(d2sx_NR16_N10000_a1.pt)` | `sha256[:16]=d7b1af69091e33b8 epoch=1688 best_epoch=1668 role=legacy-last 16x4 \| BEST_WEIGHTS_UNAVAILABLE…` |
| `build_point(C6, NR16 ckpt)` | C-V0 / C-V1 / C-V4 / C-V4b 생성 (이전: 전부 ABSENT) |
| `build_point(C2, N160000 ckpt)` | C-V0 / C-V1 / C-V4 / C-V4b (이전과 동일) |
| 사전 점검 C2 + NR16 ckpt | `SystemExit: … is a 16x4 checkpoint but no selected cell ['C2'] has that array. Refusing…` |
| 사전 점검 C6 + NR16 / C2 + N160000 | 통과 |
| analysis 헤더 (raw_B16e4k, 텍스트만) | `… b*=kron (kron K=1024)` |
| L6_a2 체크포인트 scratch 사본 재개 | `313 patience`, 0 epoch 학습, 파일 byte-identical (수정 전 패치: `313 diverged`, HEAD: `314 patience` + 1 epoch 덮어씀) |

(스모크 중 사전 점검이 만든 빈 디렉터리 `conf/raw_PREFLIGHTTEST`는 비어 있음을 확인 후 삭제.)

## 4. 적대적 리뷰 결과 (workflow `wf_97f24f54-bf5`, 3 lens × 발견별 독립 검증)

원자료: `p0_review_raw.json`.

| 발견 | 검증 | 조치 |
|---|---|---|
| 음수 loss에서 발산 판정이 모든 epoch를 bad로 봄 (L6 재개 시 'diverged' 오기록) | REAL (medium) | 수정 (`_bad_epoch`) |
| selftest [4]가 재개 후 `_best.pt` 쓰기 경로를 거치지 않음 | REAL (medium, 테스트 결함) | [4b] 추가 |
| 재개 시 `ndiv` 0 초기화 (중단·재개 ≠ 무중단, 발산 경로) — 두 lens가 독립 발견 | REAL (low, HEAD부터) | 수정 (`_trailing_bad`) |
| `_best.pt`의 `wall_sec`이 best epoch까지만 → arm으로 쓰면 학습 비용 과소 | REAL (low) | runner가 last 파일 `wall_sec` 사용 |
| 레거시 재개 후 개선 없으면 `stagec_id_str`이 없는 `_best.pt`를 안내 | 기각 (도달 경로 없음) | 한계로 기록 (아래 5) |
| resume=False 재학습 + 전 epoch NaN이면 이전 run의 `_best.pt`가 남음 / 두 저장 사이 크래시 + GPU 비결정성 | 기각 (도달 경로 없음) | 한계로 기록 |
| HPO trial마다 `_best.pt`로 디스크 약 2배 | 기각 (설계상 비용) | 한계로 기록 |
| `run_nr16.sh`가 완료된 태그 `NR16run`을 가리킴 | 기각 (운영 시나리오) | C6 재실행 시 새 태그 사용 |
| train이 diverged로 끝나도 exit 0 → `run_nr16.sh` 가드 미작동 | 기각 (현 파이프라인 도달 불가) | 한계로 기록 |
| `resolve_hp` 전부 NaN 시 DEFAULT_HP 'auto' 누출 / non-D1 분기 attempt 1 복사 | 기각 | 한계로 기록 |

## 5. 수정하지 않은 항목과 이유

- **과거 결과의 best 가중치**: 복구 불가 → `BEST_WEIGHTS_UNAVAILABLE`로 표시만 (raw meta는 앞으로의 실행부터, 과거 raw는 그대로). best 가중치 재평가는 새 태그 재학습이 필요 (GPU·장시간 → 별도 승인).
- **모델 초기 가중치가 torch 전역 RNG에 의존** (신규 발견): `score.train`의 `make_model`이 명시적 seed 없이 전역 RNG를 소비한다. 한 run = 한 프로세스인 현재 wrapper들은 torch 기본 seed로 재현되지만, 한 프로세스에서 여러 번 학습하는 경로(`hpo.py`)는 순서에 따라 초기값이 달라진다. 수정하면 기존 모든 recipe의 초기값이 바뀐다 — **사용자 결정(2026-09-23): 수정하지 않고 기록만 남긴다.**

> **정정 (2026-09-23 17:20 CDT, N1)**: 위의 "한 프로세스 한 run이면 torch 기본 seed로 재현된다"는 **틀렸다.** 이 torch 빌드(2.14.0+cu130)는 프로세스마다 `torch.initial_seed()`가 달라진다(두 번 실행: 472102272832343518 / 16063582425403287908; common·score import 후에도 매번 다름). 따라서 `score.train`의 초기 가중치는 **어떤 wrapper에서도 재현되지 않는다** — 기존 모든 체크포인트의 초기값은 기록되지 않은 난수다. 데이터 순서·σ·ε 스트림(`g`)과 split은 seed 고정이라 그대로 재현된다. 사용자의 '기록만' 결정은 틀린 전제에서 내려졌으므로 재확인을 요청했다.
- **P0-2 실경로 비용 벤치 (C)**: 미실행 — CPU 수십 분, 승인 대기.
- **C6(Nr=16) BLER 재실행**: 미실행 — 승인 대기. 재실행 시 새 태그(예: `NR16run2`), `raw_NR16run`은 arm 없는 실행의 기록으로 보존.
- **NR16 GB′ 재산출**: `train_nr16.py` 재실행은 이제 0 epoch 학습 후 GB′만 계산 (체크포인트 무변경이 보장됨). GPU 사용 → 승인 대기.
- **기록 정정 (F)**: §10 과해석 문구, "물리적으로 표준", "게이트 통과" 표현, 4.6x, F14 캡션 — 문구를 사용자가 정하도록 보류.
- **`_best.pt` 관련 알려진 한계** (리뷰에서 기전은 맞으나 도달 경로 없음으로 기각):
  1. resume=False로 같은 경로에 재학습했는데 첫 epoch부터 NaN이면 이전 run의 `_best.pt`가 남는다.
  2. best 저장과 last 저장 사이에 죽고, 재개 후 그 epoch 재학습에서 (GPU 비결정성으로) 개선 여부가 뒤집히면 `_best.pt`가 폐기된 궤적의 epoch를 담는다.
  3. 레거시 체크포인트를 재개해 한 번도 개선되지 않으면 role='last'가 되지만 `_best.pt`는 없다 → `stagec_ckpt_id`가 "_best.pt sibling"이라고 안내.
  → 평가에 `_best.pt`를 쓸 때는 `ckpt_identity(best)['epoch'] == ckpt_identity(last)['best_epoch']`를 확인할 것 (run_manifest 작성 시 점검 항목).
- **train이 diverged로 끝나도 exit 0**: `run_nr16.sh` 가드는 크래시만 잡는다.
