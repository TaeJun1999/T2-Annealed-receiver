# 적대적 검토 — NEXT_EXPERIMENTS_E5QAM16.md v1 + qam16/select_grid.py + qam16/run_grid.sh (worktree /home/HTJ/t2_wtE5, 커밋 b885a69f)

검토자: Fable 5.1 subagent, 읽기 전용 (2026-10-17 14:2x CDT). 아래는 검토자 보고를 Claude 가 이 파일로 옮긴 것 (항목·근거·문안 그대로, 표현만 줄임). 줄 번호는 v1 기준. 반영 = v2 (등록 문서 머리 'v1 → v2').

## MUST

**M1. §1.4 '같은 시행' 행의 사실 오류 — 16-QAM 의 채널 H 는 trial 1 부터 QPSK 와 다르다.** `runner.py:558–565` 는 한 스트림에서 시행마다 H → u (K 개) → perm → 잡음 순으로 뽑는다; K 42 → 90 이면 trial 0 의 H 만 같다. Codex 보고 `qam16/REPORT.md:88–89` 실측: H 일치 {0: True, 1: False, 2560…2563: False} (두 셀). v1 은 "채널 H 는 QPSK 와 같다 — 개발 한 청크에서 확인" 이라 적었다. 함의: (a) test 집합 = 16-QAM 스트림의 trial 0..2559 (번호 기준, QPSK test 와 실현이 다른 새 표본; 16-QAM 의 어느 번호도 BLER 로 열람된 적 없다); (b) `eval_accept --ref-raw` 불가; (c) §1.3 의 QPSK 비교는 '같은 시행 번호'; (d) 같은 run 안의 다섯 arm 이 같은 (H, u, perm, Y) 를 보는 것은 맞다 (`runner.py:538, 565`). 문안: '같은 시행' 행 대체, §1.3 정정, §5 의 'H 동일 확인' 삭제.

**M2. §1.4 수용 행이 실행할 수 없고 고정 수치 (ll_val repr) 가 없다.** (1) `eval_accept.py:75` 는 SNR 집합을 `C.CELLS[c]["snrs"]` (−3…15) 로 기대 → 16-QAM 격자에는 `--points C2:<격자>` 필요; (2) `--ref-raw` 는 M1 로 불가; (3) eval_accept 가 검사하는 것은 점 집합·청크 계획·meta ntrain/bstar/kron_K/ll_val/stagec_ckpt_id/iters 뿐 (`:78–98`) — modulation · payload · protocol · run|git · KEYS_RAW 모양은 `run_e5.sh` 가 직접; (4) 기존 raw 에서 읽은 값: U28B16e4 `meta|ll_val|kron` 5.797910431000217 (kron_K 4096, stagec id 'sha256[:16]=6f3a1b9490864af1 epoch=379 best_epoch=379 role=best 8x4', em_sec 9133.61854147911); B16e4k −11.459169831224418 (kron_K 1024, ckpt d2sx_N160000_a1.pt, stagec_ckpt_id 키 없음 — pre-P0-1); D2 ckpt role legacy-last (epoch 1784, best 1764, sha16 4443921ce8d5c4a1), UMi role best. 문안: ① eval_accept 명령 (두 셀, `--points`, ref-raw 없음) ② run_e5.sh 추가 검사; §1.1 에 ll_val repr.

## SHOULD

- **S1.** select_grid.py 가 'b\* 의 BLER' 전제를 검사하지 않는다 — `meta|bstar` kron, `kron_K`, `ll_val|kron` repr, `run|git` 이 SNR 사이에도 하나, `run|skip`·`run|snr` = 파일 이름.
- **S2.** §1.2 문장에 비단조 분기 (BLER(+3) ≤ 0.1 이면서 BLER(+21) ≥ 0.1 → G0 유지·보고) 와 경계 (정확히 0.1 = 안쪽 아님) 가 없다.
- **S3.** run_grid.sh: `shift 2` 뒤 `E5GRID_DONE $1` 이 첫 SNR 을 찍는다 → `CELL` 저장; fits 를 SRC 와 cmp 만 하고 등록 sha 와 대조하지 않는다 → b\* · fullK32 sha256 을 스크립트에 (`sha256sum -c`). 나머지 (청크 계획, BLER 미출력, 기존 청크 meta 검사, 청결 검사, SNR 화이트리스트) 는 맞다.
- **S4.** `analysis.table_B` 는 `b* → V1-pilot` 을 만들지 못한다 (`analysis.py:91–96`, `:388–402`) — e5_compare 가 `decision_points` · `paired` · `gain` 을 직접 부른다. `load_raw` 는 16-QAM raw 에서 돈다 (K 를 쓰지 않음; raise = 1.0 + NOTE); `recovery_ci` 는 판정점을 table_B 에서 넘긴다.
- **S5.** 스모크를 test 태그로 돌리면 test raw 폴더에 개발 청크가 들어간다 → 태그 `U28QAM16dev`, fits = test 폴더 바이트 복사본, `--skip0 5480 --n 40 --chunk 40`, BLER 미열람.
- **S6.** ν_q 진단 명령을 실행 가능한 형태로 (`--stagec-ckpt`, `--tag`, `--out`; `diag_sigma_coverage.py:189–193, 228, 244–263`); 예측 4 의 채점량 (반복 16 의 below+above / finite, 7 SNR 합).
- **S7.** ckpt 는 절대경로로 (`runner.py:1387` — `C.CONF` 아래에서 찾는다); 전체 sha 를 문서에. `--pilot-arms` + `--arm … V1-pilot` 은 V1-pilot 을 만든다 (`arms.py:405–409`).
- **S8.** D2 시작·중단 규칙이 일정 문구뿐 → (UMi 종료 + D2 추정) ≤ 10-24 06:00 CDT 일 때만 시작.
- **S9.** 예측 3 의 censored 채점, §2.1 라벨을 table_B 문자열에 묶기 (GCAP §2.1 과 같게).

## NIT

- N1. 개발 시행 조사 (전체 홈): UMi28 C2 2560..3839 와 10000..30479, D2 C2 ≤ 5119 와 10000..; ALD 개발 입력 2560..3071; Codex 스모크 2560..2563 — 5120..5519 는 두 셀 어디서도 미사용.
- N2. "24 파일" = UMi 병합 15 + 후보 9, D2 Nr8 13 + Nr4 11; b\* 선택 (ll_val argmax) 은 기존과 같다.
- N3. select_grid: 인자 없으면 IndexError; 0 · 24 dB 가 둘 다 있어도 경고 없음.
- N4. worktree 의 추적되지 않은 Codex 회귀 입력 복사본은 지우지 않는다는 한 줄.
- N5. em_sec (B16e4k 107957.18832826614, U28B16e4 9133.61854147911) 도 적어 두면 manifest 대조가 쉽다.

## 확인했지만 결함이 아닌 것
과제 요구 (두 셀 역할, 동결 ckpt/fit, payload 90, 에너지 정규화, arm 5 개, QPSK 회귀, 격자 규칙, 판정점 자동, ν_q 진단, 보고 항목, UMi 먼저, 하지 않는 것) 모두 들어 있다 — 과제와 어긋나는 해석은 M1 뿐. select_grid 의 이동 방향·새 점·'한 번만'·무결성은 맞다. 16-QAM 에서 QPSK 전용 arm 거부, runner analysis 의 16-QAM 거부는 전제와 맞다. D2 폴더의 링크는 `cp -L` 로 실제 파일이 복사된다.
