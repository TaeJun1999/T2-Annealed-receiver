# 실행 중 모아 둔 기록 (U28NR32GCAP 실행이 끝난 뒤 DECISIONS · §6 에 옮긴다; 실행 중 DECISIONS 수정 금지)

- 2026-10-17 22:35 CDT — GCAP 주 실행을 등록 §1.5 절차로 멈추고 (tmux Ctrl-C, 22:33 CDT; INTERRUPTED, runner exit e 130 chk 0, GCAP_DONE ok=4 fail=5 — 미완성 raw 의 수용 실패는 예상된 것) 같은 HEAD 64b2912f 에서 `--resume` (22:34 CDT; WGB 13.5 그대로, 메모리 가드가 MemAvailable 989 GB 로 워커 55).
  - 사유: 서버 메모리 압박 (다른 사용자의 페이지 캐시 ≈ 430 GB, MemFree 수 GB, 스왑 가득) 으로 GCAP 워커가 커널 직접 회수에 갇힘 (워커 표본 user 0 % · sys 100 %, cgroup memory.pressure 65–90 %); 둘째 회전 청크 31–35 ks (첫 회전 중앙값 9.7 ks 의 3.2–3.6 배).
  - 재개 때 바꾼 것: glibc 할당기 환경변수만 (GLIBC_TUNABLES=glibc.malloc.mmap_max=0:glibc.malloc.trim_threshold=68719476736, MALLOC_MMAP_MAX_=0, MALLOC_TRIM_THRESHOLD_=68719476736) — 해제한 메모리를 커널에 돌려주지 않고 다시 써서 반복 할당의 회수를 없앰. conf/code · Demo · 인자 · G 는 그대로.
  - 결과 불변 확인 (사전, 개발 시행만): GCAP 설정 (b* K8192 + genie, 0 dB) 시행 4300..4302 를 기본 / 할당기 설정으로 동시에 → 17 배열 바이트 동일; 시간 3003 s / 934 s (user 556 / 579 s, sys 2431 / 350 s), 최대 RSS 12.57 / 12.91 GB (가드 1.25·G = 16.9 GB 아래). 시행 2560..2562 를 할당기 설정으로 다시 돌려 GCAP 개발 스모크 청크 (기본 할당기) 의 첫 3 행과 대조 (결과는 scratchpad/malloctest/c.log).
  - 잃은 것: 멈출 때 진행 중이던 청크 약 58 개의 계산 (평균 약 4 h 진행분). 완료 청크 116 개는 그대로 (읽을 수 없는 청크 0).
  - 사용자: "뭐든 빨리 할 수 있는 방향으로 하자", "내가 지금 터미널을 건드리지 못해서 너가 할 수 있을까?" (2026-10-17 22:2x–22:3x CDT). 첫 멈춤 시도는 자동 권한 분류기가 거부, 사용자 요청 뒤 다시 실행.
  - 두 번째 확인 (결과 확정): 할당기 설정으로 시행 2560..2562 (0 dB) 를 다시 돌린 결과가 GCAP 개발 스모크 청크 (기본 할당기, 10-17 07:37 CDT, 압박 전) 의 첫 3 행과 17 배열 모두 바이트 동일 (scratchpad/malloctest/c.log "MTc vs GCAPdev rows 0..2: 17 arrays compared; differing: []", 22:31 CDT).
  - 재개 뒤 관찰: 힙이 최고치 (≈ 12.6 GB) 에 닿은 워커부터 user 55 % 안팎으로 계산 (재개 10 분 뒤 13/55 워커), 나머지는 메모리를 받는 동안 대기; RSS 합계 473 GB (2 분) → 531 GB (20 분).
