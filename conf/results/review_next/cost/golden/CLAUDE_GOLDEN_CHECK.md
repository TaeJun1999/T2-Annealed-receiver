# E4 bench_cost.py 의 정답 사례 대조 (Claude, 2026-10-19 03:32 CDT; 측정 도구 = Codex 작성, 정답 사례 = golden-writer 가 구현을 보지 않고 작성)

- 대상: `conf/code/bench_cost.py` (e4-cost worktree, Codex 작성 — 10-18 22:48 CDT 중단 시점의 판; Codex 의 확인 실행 `logs/cost/verify_20261018_222512_CDT_*.log`, 출력 `cost_{D2,U32}_20261018_222512_CDT.*`).
- 정답 사례: `golden_cost.md` (+ golden-writer 의 확인 스크립트).
- G1 H 호출 / 블록 16 — 일치 (Codex 확인 실행의 BLOCK 줄, 모든 arm · SNR).
- G2 forward / VJP — VJP 1,024 (8×4) · 4,096 (32×4) 일치; forward 는 32 (jacrev 안 1 + 평균 m 용 1, score.py:1120–1121) — golden 과 일치, 과제의 기대값 16 과는 다름 (보고에 정의를 밝힐 것).
- G3 SBL EM 48 / 블록 — 일치. G4 K: D2 1024, UMi32 4096 · 8192 — 일치 (태그별 fits 두 파일).
- G5 통계 S1–S7 — `claude_check_g5.py` 로 bench 의 quantiles · write_results 에 넣어 모두 일치 (호출 모음, 블록별 비의 median, 빈 입력 NaN 행 유지, 예외 블록 제외).
- G6 거부: R1-a (UMi32 last 복사본) · R1-b (K · ll_val 이 같은 재시작 파일을 정상 이름으로) · R1-c (한 바이트 뒤집음; 첫 시도는 원래 0x00 인 바이트라 무효, XOR 로 다시) → SHA256 MISMATCH 로 멈춤; R1-d 정상 통과; R2-a 기존 출력 거부 (원래 파일 불변, npz 안 생김); R3-a 다른 작업이 있으면 --force 없이 측정 안 함 (수신기 안 띄움). 로그 `r*.log`. 출력 폴더는 worktree 안만 허용 (`golden_check_claude/`).
- G8 개발 시행 2561 블록의 blk_err · nmse (tap / plain) — golden 의 외부 값과 모두 일치 (D2 −3 · +6 dB V1 · V1-ms · b\*, UMi32 −3 · +3 dB V1 · SBL).
- 참고: load_snapshot 은 GPU 더미 점유 (gpu_hold) 도 "다른 작업" 으로 센다 → 10/22–23 측정 때 더미를 내릴지 사용자에게 묻는다.
- **고친 범위 재확인 (2026-10-19 09:01 CDT, Claude)**: Codex 마무리 보고 (`~/t2/reviews/20261019-224612-codex_write_cost_report.md`, `finish_20261019_084909_CDT/`) 가 `bench_cost.py` 를 ece1fd93… (위 대조의 판; 첫 출력의 metadata source_sha256 과 같음) → f85be77e… 로 바꿨다. 바뀐 것은 write_results 의 머리말 세 줄 · 표 머리 · `batches=` → `pullback_batches=` · COUNT_CHECK 문구뿐이고 (diff 3 hunk), 세는 로직 · 시간 · sha · 거부 경로는 그대로다. G5 (`claude_check_g5.py`) 를 새 판에 다시 돌려 S1–S7 모두 OK (`G5 OK`). Codex 의 forward 32 설명 (score.py:1120 jacrev 안 1 + 평균 1) 은 위 G2 와 같다.
- threadpoolctl 3.7.0 을 torch env 에 pip 로 설치했다 (원 명세; Codex 는 `cost/deps` 에 두었다 — bench 는 env 를 먼저 import 하고 없을 때만 deps 를 쓴다).
