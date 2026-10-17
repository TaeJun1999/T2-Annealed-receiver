# verifier 재확인 (2 · 3 차) — U28NR32GCAP 실행·분석 스크립트, 2026-10-17 00:0x–00:25 CDT (verifier 서브에이전트, 독립·읽기 전용)

## 2 차 — 커밋 24ad4441 의 `run_gcap.sh` · `gcap_compare.py` diff · `select_gcap.py` · `rss_smoke.py`
- 결함 1: 최종 = A 를 막지 않는다 (`FIT A 4096 <ORIG sha>` 가 전제 통과) → 반영 (`B:4096`·`C:8192` 만, sha ≠ ORIG). Codex 결함 2 와 같다.
- 확인 필요 3 → 반영: `gcap_s5.txt` 동결 절차 (FREEZE ≠ 실행 커밋; HEAD = s5 의 마지막 커밋, DECISIONS 동결 줄, FREEZE 이후 code/·Demo/ 불변; 문서 diff 검사 제거), RSS 스모크 (rc·청크 재계산·dev 폴더 바이트 복사본 검사), Ctrl-C 뒤 chk 잔존 (§1.5).
- 선택 4 → 반영: 링크 거부, gcap_compare 출력 로그 보존, runner 종료 코드 집계, `--resume` 의 run|git 사전 검사.
- 결함 없음 확인: `bash -n`, S5 파싱·GCAP_WGB 인상 검사, git diff 범위, 해시 상수, CPU 집합 (119 + 1), 수용 호출 원문, run|git 검사 (가짜 449 파일), chk 계획 [(0, 40)]·11 arm × KEYS_RAW 7, select 규칙 (가짜 파일), NOTE 문자열 범위.
- 산출: `/tmp/claude-1005/-home-HTJ-t2/7f296764-20fc-422b-96c7-feef15a08581/scratchpad/verifier2/`.

## 3 차 — 24ad4441 이후 미커밋 변경 (위 반영분)
- 결함 1: 비대화형 bash 의 `&` 명령은 SIGINT 를 무시한 채 시작한다 — 주 runner 를 백그라운드로 바꾸자 tmux Ctrl-C 가 메모리 감시만 죽이고 주 실행은 감시 없이 계속됨 (대역 재현: 주 runner `SigIgn` 에 SIGINT 비트). → 반영: INT/TERM 트랩이 주 runner·워커와 감시를 멈추고 chk 는 끝까지 둔다.
- 결함 2: 워커 하나가 OOM (SIGKILL) 으로 죽으면 `mp.Pool` + `imap_unordered` 가 그 청크를 영원히 기다려 스크립트가 `wait` 에서 멈춘다 (대역 재현, Python 3.12.14 fork). → 반영: 두 스냅샷 이상 (≥ 30 s) 살아 있던 워커가 사라졌는데 60 s 뒤에도 runner 가 살아 있으면 멈춘다.
- 확인 필요 2: 주 runner 자체 OOM 뒤 고아 워커가 청크를 더 쓸 수 있음 (수용·`--resume` 전제가 막아 잘못 통과하지 않음 — 그대로 둠); memguard 정지가 청크 쓰기 도중이면 잘린 npz → `--resume` 검사가 원인 (읽히지 않는 파일 목록) 을 알리고 멈추도록 반영.
- 선택 1: FREEZE 커밋 자체에 DECISIONS 동결 줄이 있는지 → 반영.
- 결함 없음 확인: R = nan 가드 (958/599/127 → 0.432010; F_b\* ≤ F_g → nan), 전제 논리 11 경우 (스크래치 git 저장소), `--resume` 검사 5 경우, memguard·종료 코드 5 경우 (RSS 초과 발동·chk 오발동 없음·정상·수용 실패·chk 실패), rss_smoke 경로·청크 이름·jobs = 1.
- 산출: `/tmp/claude-1005/-home-HTJ-t2/7f296764-20fc-422b-96c7-feef15a08581/scratchpad/verifier3/`.
- 반영 뒤 작성자 확인 (대역 runner): 정상 / 워커 SIGKILL / 프로세스 그룹 SIGINT — 등록 §4.3.
