# 적대적 검토 — NEXT_EXPERIMENTS_D2SITEMS.md v1 (worktree /home/HTJ/t2_wtMS, 브랜치 e1-ms, 커밋 9dd8b5fe)

검토자: Fable 5.1 subagent, 읽기 전용 (2026-10-18 22:xx CDT; 사용자가 승인한 방식 — 사전 등록 문안의 적대적 검토). 아래는 검토자 보고를 Claude 가 옮긴 것 (항목 · 근거 · 제안, 표현만 줄임).

## MUST
**M1. FREEZE (= main 병합) 가 V1LS 등록 실행과 충돌.** run_v1ls.sh 는 run 마다 `git diff $FREEZE HEAD -- code ../Demo` 가 비어 있음과 HEAD = s5 커밋을 요구 → e1-ms (arms.py · runner.py · run_e1ms.sh · e1ms_compare.py 변경) 를 체인이 끝나기 전에 병합하면 남은 V1LS run 이 ABORT, 재개도 막힘 (AGENTS.md · V1LS §1.5 '실행 중 main 커밋 금지'). 문서는 FREEZE = 병합, "한 작업일 안에 동결까지" 라 시한이 V1LS 일정에 묶임. run_e1ms.sh 의 pgrep "[r]unner.py run" 은 V1LS 체인의 run 사이 (수용 · compare 단계) 를 못 봄 → E1+ 가 시작되면 다음 V1LS run 이 ABORT. 제안: (a) FREEZE = 검토 반영 뒤 e1-ms 의 마지막 커밋 (git diff 99f62bfb 2a9b4d14 -- conf/code Demo 가 비어 있어 병합 뒤 조건 성립); 병합은 V1LS CHAIN_DONE (끊겼으면 네 run 의 V1LS_DONE) 과 V1LS 기록 커밋 뒤; (b) "한 작업일" = 구현 · 확인 (FREEZE) 까지, 병합 · s5 · 실행은 V1LS 뒤 (10-24 18:00 CDT 전); (c) run_e1ms.sh 에 `pgrep -f "run_v1ls(_chain)?\.sh"` 가드, §1.3 시작 조건에 V1LS 종료.

**M2. §2.3 금지 문구가 과제의 동기 · §2.1 과 모순.** 과제 "왜 하는가" 는 이 대조를 "공분산의 방향 정보만 다르게 한 대조" 로 정의; 과제가 금지한 것은 보조 비교의 "floor 만의 몫" 뿐. §2.3 은 V1 ↔ V1-ms 의 단일 요인 귀속까지 막음 (코드상 두 arm 의 설계 차이는 site 공분산의 꼴 하나). 제안: 금지 = V4 ↔ V1-ms 를 한 요인으로 돌리는 표현 ("floor 만의 몫", "Jacobian 수리만의 효과") 과 V1 ↔ V1-ms 의 closed loop 를 뺀 기구적 서술 ("고정 질의에서 X dB"); 허용 = "두 arm 은 설계상 EP site 공분산의 꼴 (full C₊ 대 trace 를 맞춘 등방) 만 다르므로 라벨 · L 은 그 한 가지 설계 차이의 closed-loop 결과" (§2.1 고정 설명과 함께). 원고 반영은 사용자 결정.

## SHOULD
- **S1.** raw_B16e4k manifest 검사 (모든 청크 mtime ≤ manifest written 2026-09-23 07:36:44 KST) 를 실행 전 전제로: worktree 체크아웃은 mtime 이 새로워 상대 경로로는 REFUSED (kat 는 절대 경로로 통과); 실제 실행에서는 run 과 수용 뒤 compare 에서야 걸림. run_e1ms.sh 에 find -newermt · git status 검사, "main 에서 raw_B16e4k 를 다시 체크아웃하는 git 조작 금지".
- **S2.** runner 뒤 흐름 (accept_eval → accept_raw → compare → E1MS_DONE) 끝-끝 확인: 스모크 raw 로는 compare 가 REFUSED (점 · n). KAT v2 (raw_B16e4k 3 점 192 청크, V1 → V1ms, run|git = HEAD, meta|ms_arm, meta|stagec_ckpt_id) 와 runner 줄을 뺀 사본으로 E1MS_DONE ok=3 fail=0, 청크 하나를 빼서 실패 경로 (fail=2).
- **S3.** test 시행 0..39 에서 V1 · V4 를 다시 돌린 회귀 (확인 3, 병합 확인 (a)) 를 DECISIONS 에 남긴다 (V1-ms 미실행 — runner.py 의 --arm 필터가 시행 루프 앞).
- **S4.** §0.2 의 "첫 질의 ... nmse 상대 차 ≤ 1.2e-15" 는 V1-ms ↔ V4 만의 값; V1 ↔ V1-ms 는 첫 site 부터 달라 반복 0 nmse 최대 상대 28 % · 38 % · 75 %. 문구 정정.

## NIT
N1 §4 의 "합성 raw 와 출력은 저장소에 없음" → kat_make.py · kat_compare.txt (9dd8b5fe); 머리말 HEAD. N2 §0.3 "반복 1 부터 최대 …" 는 반복 1 에서의 최대 (그 뒤 일부 시행 O(1)). N3 §0.2 고유값 floor 조건 문구 (λ_min 미만). N4 §0.4 "캐시된 (m, J₊)" → "같은 질의로 다시 계산한". N5 예측 5 "하한 > 0" → "출력 하한 ≥ +0.01". N6 censored 문장의 gain 도우미 문자열 ("extend the SNR grid") 에 "격자는 늘리지 않는다 (§1.6)". N7 §2.4 영어 (iii) · (iv) 구분. N8 accept_raw 에 "arm 둘뿐" 검사.

## 확인했지만 결함 아님 (요약)
§0.1 · §0.3 수치 전부 재계산 일치; 판정 규칙 = 코드 (판정점 고정, MIN_DISC 6, 라벨 순서, 방향 매핑, gain 부호, B 2000 · seed 20260925); 자산 sha256; MatchedScalarPrior · 배선 · LOOP 상수 동일; 스모크 · 개발 raw 의 V1-ms · genie 비트 동일 (arm 집합 무관); 과제의 정의 · 확인 1–4 · 보고 · 하지 않는 것 · 시작 조건 모두 반영; test / 개발 분리.

## Claude 의 처리 (2026-10-18 CDT)
- 전부 수용. 코드: run_e1ms.sh 에 V1LS 실행 가드 (M1c), raw_B16e4k mtime · clean 전제 (S1), accept_raw 의 arm 집합 검사 (N8). S2 흐름 시험은 Claude 가 개발 기록으로 실행. 문안 (M1a · b, M2, S1 · S3 · S4, N1–N7) 은 Fable 작성자가 v2 에서 반영.
- 참고: 검토 시점에는 V1LS 실행 전이었으나 10-18 22:13 CDT 에 체인이 시작됐다 — M1 의 우려가 그대로 적용된다.
