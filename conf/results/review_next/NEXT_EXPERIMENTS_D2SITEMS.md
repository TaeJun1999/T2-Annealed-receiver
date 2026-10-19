# NEXT_EXPERIMENTS_D2SITEMS — 헤드라인 셀의 matched-scalar 대조: `V1-ms → V1` 짝 검정과 SNR 손실 L (E1+; D2 C2 8×4, S2; 새 arm 하나의 test 실행) — 사전 등록 v2.3

- v1 작성 2026-10-18 21:53 CDT (= 10-19 11:53 KST), Fable 5.1 subagent (Claude 의뢰; worktree `~/t2_wtMS`, 브랜치 `e1-ms`; 커밋 9dd8b5fe). **v2 작성 2026-10-18 22:27 CDT (= 10-19 12:27 KST)**, 같은 작성자, HEAD 1de35f0c: 적대적 검토 `prereg_reviews_2026-10-18/review_D2SITEMS.md` (Fable 5.1, 읽기 전용; MUST 2 · SHOULD 4 · NIT 8, Claude 가 모두 수용) 반영. **판정 규칙 — 검정 · 임계값 · 판정점 고정 (§1.4) — 는 v1 과 같다.** 코드 반영 (Claude): 7326010c `code/run_e1ms.sh` (M1c V1LS 가드 · S1 `raw_B16e4k` mtime · clean 전제 · N8 arm 집합 검사), 1de35f0c 흐름 시험 (S2). **v2.1 작성 2026-10-18 22:50 CDT (= 10-19 12:50 KST)**, 같은 작성자, HEAD 6b49603e: Codex 교차 검토 (`~/t2/reviews/20261019-123541-prompt_pretest_e1ms.md`, 대상 e1-ms f460f7b6; 결함 3, Claude 가 모두 수용 — 처리는 그 파일 끝) 와 verifier 검토 (v2 의 고친 범위; 결함 D1, 추가 확인 A1 · A2, 선택 O1–O3; Claude 요약) 반영. 판정 규칙은 바꾸지 않았다. 코드 반영 (Claude, 6b49603e): `run_e1ms.sh` 의 V1LS 가드를 명령줄 시작 고정 패턴으로 (O1), 이 문서의 FREEZE 불변 검사 (O2). **v2.2 작성 2026-10-18 23:16 CDT (= 10-19 13:16 KST)**, 같은 작성자, HEAD a7240aad: verifier 의 v2.1 (a7240aad) 재검토 — 결함 0, 동결 전 선택 개선 4 — 반영 (문안만; 코드 변경 없음, 판정 규칙 불변). **v2.3 작성 2026-10-18 23:27 CDT (= 10-19 13:27 KST)**, 같은 작성자, HEAD 7de0d3c8: verifier 의 v2.2 (7de0d3c8) 재검토 — 결함 D1 (§4 의 동결 대상), 선택 O1 · O2 — 반영 (문안만; 코드 변경 없음, 판정 규칙 불변). **동결 대상 = 이 판 (v2.3) 을 담은 `e1-ms` 커밋** — FREEZE 뒤에는 `run_e1ms.sh` 의 FREEZE 불변 검사 때문에 이 문서를 고칠 수 없다. 사용자 과제 `prompts/PROMPT_SERVER_E1MS.md` (사용자 10-18 21:19 CDT, "올렸으니까 필요할때 확인하고 연구 끊기지 않게 진행해"), 공통 규칙 `gcap/PROMPT_SERVER_COMMON.md`. 형식의 선례: `NEXT_EXPERIMENTS_SITE16e4.md` (같은 셀의 `V4 → V1`, 규칙 고정 사후 계산), `NEXT_EXPERIMENTS_V1LS.md` (가장 최근 등록).
- **지위: 사전 등록.** 새 arm `M-ours-dscore-C-V1ms` (V1-ms) 의 test 결과는 없고 (test 시행에서 돌린 적 없음 — §0.4 확인 3), 이 문서의 §0–§3 을 동결한 뒤에만 만든다. **작성 시점 공개**: 비교 상대 V1 · V4 의 test 결과 — 실패 수, BLER, 기록된 쌍 `V4 → V1` (SITE16e4 §6.1; RESULTS §24) — 는 기록돼 있고 작성자가 봤으며 `raw_B16e4k` 에서 다시 셌다 (§0.1). V1-ms 의 개발 스크린 (개발 시행 2560..2879, n 320; §0.3) 도 봤다. 따라서 §3 의 예측은 그 둘에 기댄 예측이다.
- **FREEZE** = 검토를 반영한 뒤의 `e1-ms` 커밋 (§0–§3 과 코드의 동결; 해시는 s5 에만 적는다 — 이 문서에는 적지 않는다). **병합** (`e1-ms` → main) 은 V1LS test 가 끝난 뒤 — `logs/run_v1ls_chain.log` 의 `CHAIN_DONE`, 체인이 끊겼으면 네 run 의 `V1LS_DONE` — 와 V1LS 의 실행 뒤 기록 커밋 뒤에만 한다. 이유 (검토 M1): V1LS 체인은 10-18 22:13 CDT 에 main 의 실행 커밋 1d706648 에서 시작했고, `run_v1ls.sh` 는 run 마다 HEAD = V1LS s5 를 마지막으로 건드린 커밋과 `git diff <V1LS FREEZE> HEAD -- code ../Demo` 비어 있음을 요구하므로, 그 전의 main 커밋 (병합 포함) 은 남은 V1LS run 을 ABORT 시키고 재개도 막는다. **순서 (verifier D1)**: V1LS 종료 · 기록 커밋 → 병합 → **사용자 승인** (test 집합 실행과, 병합 확인 (a) 가 test 시행 0..39 에서 V1 · V4 를 다시 돌리는 것을 **함께** 묻는다) → 병합 확인 (a)(b) (§5) → **실행 커밋** = `results/review_next/e1ms/e1ms_s5.txt` (§5) 와 실행 시작 DECISIONS 줄 (승인을 인용) 을 **같은 커밋**에 더한 것 → 실행. 실행 커밋은 `code/` · `Demo/` 와 이 문서를 건드리지 않는다. `run_e1ms.sh` 가 요구하는 조건 — HEAD = s5 를 마지막으로 건드린 커밋, s5 의 FREEZE 가 HEAD 의 조상, **이 문서가 FREEZE 와 같음** (`git diff --quiet FREEZE HEAD -- <이 문서>`, 6b49603e; FREEZE 뒤 이 문서의 어떤 변경도 실행을 막으므로 §4 · §5 도 실행 전에는 고치지 않는다), `git diff FREEZE HEAD -- code ../Demo` 비어 있음 — 은 병합 뒤에도 성립한다: `e1-ms` 는 99f62bfb 의 후손이고 99f62bfb..2a9b4d14 (V1LS 병합) · 99f62bfb..1d706648 (지금 main HEAD) 에 `code/` · `Demo/` 차이가 없어 (작성자 확인, `git diff --stat`), 병합 뒤 main 의 `code/` · `Demo/` = FREEZE 의 것이다. 그 사이 main 에 다른 `code/` · `Demo/` 커밋이 생기면 전제가 깨진다 → 실행하지 않고 사용자에게 보고 (새 동결은 검토를 다시 거친다). 동결 뒤 §0–§3 을 바꾸지 않는다.
- **범위 · 일정 (과제)**: E2′ · E3′ · E5 의 test 를 모두 건 뒤 (충족 — WORK_QUEUE 10-18 20:50 CDT: GCAP · SBL32 · E5 결과 기록 커밋), 10/19 이후, CPU 가 남을 때만 시작하고 핵심 실험과 겹치면 양보한다 (§1.3 시작 조건). **구현 · 확인 (= FREEZE 커밋까지) 은 착수 (10-18 21:24 CDT, worktree 생성) 후 한 작업일 (10-19 21:24 CDT) 안에** 끝낸다; 넘으면 원인과 상태를 기록하고 멈추며 그 경우 원고는 기존 scalar 대조 (V4) 만 쓴다 (§1.5). 병합 · s5 · 실행은 V1LS 뒤 자원이 날 때 하되 원고 반영 마감 2026-10-24 18:00 CDT 안에 넣는다. 이 결과는 논문의 중심 기여가 아니며 제출의 성패 조건도 아니다. 결과가 어떻든 사전에 정한 두 비교를 그대로 보고한다.

v1 → v2 (검토 항목마다 한 줄):
- M1 (a) FREEZE = `e1-ms` 커밋, 병합은 V1LS 종료 · 기록 커밋 뒤, 실행 커밋 = 병합 + s5 + 실행 시작 DECISIONS 줄 (머리말 · §4 · §5); (b) "한 작업일" 의 대상 = 구현 · 확인 = FREEZE 까지 (머리말 · §1.3 · §1.5); (c) §1.3 시작 조건에 V1LS 종료와 `pgrep -f "[r]un_v1ls(_chain)?\.sh"` 가드 (코드 7326010c) (§1.3 · §1.5 · §1.6).
- M2 §2.3 의 금지 문구를 좁혔다 — 금지: V4 ↔ V1-ms 를 한 요인으로 돌리는 표현, V1 ↔ V1-ms 의 closed loop 를 뺀 기구적 서술; 허용 꼴 명시 (§2.1 고정 설명과 함께); §0.2 마지막 문장도 같이 (§0.2 · §2.1 · §2.3).
- S1 §1.3 전제에 `raw_B16e4k` 의 청크 mtime ≤ manifest written (2026-09-23 07:36:44 KST) · git clean (코드 7326010c), "main 에서 raw_B16e4k 를 다시 체크아웃하는 git 조작 금지", worktree 에서는 절대 경로로만 통과 (§1.3 · §5).
- S2 §4 에 runner 뒤 흐름 시험 결과 (1de35f0c; 정상 경로 ok=3 fail=0, 청크 하나 뺀 경로 ok=0 fail=3).
- S3 test 시행 0..39 의 V1 · V4 회귀 (확인 3 · 병합 확인 (a)) 를 실행 커밋의 DECISIONS 줄에 기록하는 계획 (§0.4 · §4 · §5).
- S4 §0.2 의 인용 정정 — 첫 질의는 파일럿 site 와 공통 상수만으로 정해짐; 반복 0 의 nmse 상대 차 ≤ 1.2e-15 는 V1-ms ↔ V4 의 값 (첫 질의에 PSD 수리가 걸리지 않음); V1 ↔ V1-ms 는 반복 0 부터 다름 (최대 상대 28 % · 38 % · 75 %) (§0.2 · §0.3).
- N1 머리말 HEAD 1de35f0c, §4 의 정답 사례 출처 `kat_make.py` · `kat_compare.txt` (9dd8b5fe); N2 §0.3 "반복 1 에서의 최대" 와 그 뒤 반복의 크기; N3 §0.2 floor 조건을 "고유값이 λ_min 미만" 으로; N4 §0.4 "캐시된" → "같은 질의로 다시 계산한"; N5 예측 5 를 "출력 하한 ≥ +0.01" 로; N6 §2.1 censored 문장에 "격자는 늘리지 않는다"; N7 §2.4 영어 (iii) · (iv) 구분; N8 수용 ② 의 arm 집합 검사 (코드 7326010c) (§1.3).
- 그 밖 (검토 밖, 사실 갱신): §5 코드 sha (`run_e1ms.sh` → dfc23bbe96919423), 스모크 `eval_accept` 인자가 9dd8b5fe 에 기록됨, §5 산출물 없음 재확인 시각.

v2 → v2.1 (항목마다 한 줄; 출처 Codex `~/t2/reviews/20261019-123541-prompt_pretest_e1ms.md` · verifier (Claude 요약)):
- Codex 1 (수용) §2.4 (iii) 영어 문장을 2/3 규칙 그대로 — "neither direction was significant at two of the three decision SNRs" (개별 유의점은 있을 수 있다; 기록된 `V4 → V1` 의 −3 dB 56:33 p .019 가 (iii) 의 예); §2.1 (iii) 에 같은 뜻의 괄호 (라벨 문자열은 불변).
- Codex 2 (수용) §1.5 재개 명령에 `E1MS_CPUS=24-47,120-143,72-95,168-191` 를 붙임 (환경변수는 그 명령에만 전달; 없으면 스크립트 19 행이 die).
- Codex 3 (수용) §0.1 의 3 점 · 7 점 구간 차이 설명 정정 — 보간 차이가 아니라 추가 네 점이 난수를 소비해 두 번째 재표본부터 공통 세 점의 index 가 달라지는 유한 bootstrap 표본의 차이 (Codex 확인: 공통 세 점의 재표본을 같게 두면 두 격자 모두 [+0.0567, +0.2334], censored 0/2000); 수치는 그대로.
- verifier D1 (결함) 승인 순서 — V1LS 종료 → 병합 → 사용자 승인 (병합 확인 (a) 의 test 시행 0..39 V1 · V4 재실행 포함) → 병합 확인 (a)(b) → s5 + 실행 시작 DECISIONS 줄 (승인 인용) = 실행 커밋 → 실행 (머리말 · §1.3 · §4 · §5).
- verifier A1 §2.1 · §2.3 의 해석 문장을 허용 목록 방식으로 — 결과 문장에 붙는 해석은 §2.1 의 고정 설명과 허용 꼴뿐; 그 밖 (예: "행렬 site 가 더하는 몫 X dB") 은 결과를 본 뒤 사용자가 정한다.
- verifier A2 `e4-cost` (E4 비용 벤치 브랜치; e1-ms 9dd8b5fe 에서 갈라짐) 는 E1+ 실행이 끝난 뒤에만 main 에 병합 (§1.6 · §5).
- verifier O1 · O2 §1.3 시작 조건 · 전제에 명령줄 시작 고정 패턴의 V1LS 가드와 이 문서의 FREEZE 불변 검사 (코드 6b49603e); 머리말에도.
- verifier O3 §0.3 의 V1 ↔ V1-ms nmse 상대 차 정의 (|Δ|/nmse_V1, 앞 arm) 명시; 뒤 arm 으로 나눈 값 (0.390 · 0.614 · 3.046) 병기.
- 그 밖 (verifier) `raw_B16e4k` 청크 mtime 을 범위 2026-09-22 21:23:28–21:39:55 KST 로 (§0.1 · §1.3; 작성자 재확인); §5 코드 sha (`run_e1ms.sh` → e99f2483951d274c), 머리말 HEAD 6b49603e, §4 코드 · 검토 상태. FREEZE 시한 (10-19 21:24 CDT) 은 그대로.

v2.1 → v2.2 (항목마다 한 줄; 출처 verifier 의 v2.1 (a7240aad) 검토 — 결함 0, 동결 전 선택 개선 4; 반례 계산 세션 스크래치패드 `verify_e1ms_v21/labels.out`, 저장소 밖):
- 선택 1 §2.4 (iii) 영어 문장의 범위를 한 가지로 — "at two or more of the three decision SNRs" (원고 IV-A 의 정의, SITE16e4 §1 과 같은 꼴). verifier 반례: 8:0 / 0:8 / 3:3 은 두 점이 서로 다른 방향으로 유의해도 어느 방향도 2 점에 못 미쳐 (iii) 이다 — 옛 문장은 "두 SNR 에서 아무 방향도 유의하지 않음" 으로도 읽혔다.
- 선택 2 §2.1 (iii) 의 "그 점은 혼합 결과 규칙대로 §6 에 적는다" → "그 점의 방향과 p 는 §6 에 그대로 적는다" (혼합 결과의 정의 — 서로 다른 방향의 유의 점 — 와 겹치지 않게).
- 선택 3 허용 목록 (§2.1 · §2.3) 에 §2.2 고정 문장을 명시 — 결과 문장에 붙는 해석은 §2.1 고정 설명 · 허용 꼴 · §2.2 고정 문장뿐.
- 선택 4 §1.6 의 "V1 · V4 의 재실행" 을 비교 자료로서의 재실행으로 한정; §5 병합 확인 (a) 의 회귀 40 시행 (test 0..39, −3 dB; 승인 범위 안) 은 예외. FREEZE 시한은 그대로.

v2.2 → v2.3 (항목마다 한 줄; 출처 verifier 의 v2.2 (7de0d3c8) 검토 — 결함 1, 선택 2):
- D1 (결함) §4 의 동결 대상이 "이 v2.1" 로 남아 있었다 → "이 판 (v2.3) 을 담은 e1-ms 커밋" 으로; 검토 계획 줄에 "verifier v2.1 재검토 → v2.2 → verifier v2.2 재검토 → v2.3" 단계를 넣음 (§4 두 줄; 머리말에도). 변경 기록 줄의 "v2.1" · "v2.2" 는 그대로 (§2.1 · §2.3 의 "v2.2 선택 3" 은 기록 참조).
- O1 §2.4 (iii) 영어 문장을 원고 IV-A 의 "in its favor at two or more" 꼴로 — "neither receiver has p < 0.05 in its favor at two or more of the three tested SNRs" (2 점 이상이 각 arm 에 붙어 혼합 (iii), 예 8:0 / 0:8 / 3:3, 에서도 참); SNR 명사를 (i)–(iii) 모두 "tested SNRs" 로 통일하고 그 선택을 §2.4 에 한 줄 적음; §2.1 (iii) 의 풀이를 "2 개 이상에서" 로.
- O2 §2.1 혼합 결과 정의에 "(ii) 인데 한 점이 V1 쪽으로 유의" (예 6:0 / 0:6 / 0:6 → (ii)) 를 더함; 그 경우에도 점별 방향 · p 를 §6 과 보고에 적는다. FREEZE 시한 (10-19 21:24 CDT) 은 그대로.

## 0. 알고 있는 것 (판정에 쓰지 않는다)

### 0.1 기록된 test 수치 (`raw_B16e4k`; V1 · V4 · genie — 다시 돌리지 않는다)

| 항목 | 값 (출처) |
|---|---|
| raw | `raw_B16e4k` (D2 C2 8×4, prior S2, N′ = 1.6e5; test 시행 0..2559, n 2560 / SNR, 7 SNR −3 … +15 dB, 16 반복, chunk 40 → 448 청크; git 추적 cc3d40ab, 청결; main 의 청크 mtime 2026-09-22 21:23:28–21:39:55 KST). `run|git` 이 없는 raw 라 `results/review_next/run_manifest_B16e4k.json` (추적 · 청결; written 2026-09-23 07:36:44 KST) 으로 확인한다 — `manifest-head:cd241b7e/chunks-sha:78cbb59fc01ce520` (`pairB_SITEB16e4k.txt` :4; `pair_baselines.manifest_check`) |
| 실패 수 @16 / 2560 (−3 / 0 / +3 dB) | V1 371 / 88 / 29 · V4 394 / 96 / 21 · genie 87 / 26 / 12 (작성자가 raw 에서 다시 셈; V1 · V4 는 `pairB_SITEB16e4k.txt` :13 · :21 과 같다) |
| BLER@16 | V1 0.14492 / 0.03438 / 0.01133 · V4 0.15391 / 0.03750 / 0.00820 (같은 재계산) |
| 기록된 쌍 `V4 → V1` (SITE16e4 §6.1, `pairB_SITEB16e4k.txt` :17–21; RESULTS §24) | 판정점 −3 · 0 · +3 고정; 부호검정 56:33 (p .019) · 23:15 (p .26) · 6:14 (p .12), pooled 85:62 (p .069); POWERED; **라벨 (iii) "판정하지 못함 (유의 방향 없음)"**; SNR@0.1 격차 (V4 − V1) +0.14 dB [90 % +0.06, +0.23] — **7 점 격자** 위의 bootstrap |
| 같은 쌍을 **3 점 격자** (−3 / 0 / +3; 이 등록의 격자) 로 다시 계산 (작성자, `table_b` · `gain`; `kat_compare.txt` 의 보조 비교 줄과 같다) | 부호검정 · 라벨 같음 (점별 계산이라 격자와 무관); SNR@0.1 격차 +0.14 dB [**+0.05**, +0.23] (미반올림 +0.1425 [+0.0502, +0.2295]; censored 0 %). 하한이 +0.06 → +0.05 로 다른 것은 보간 차이가 아니라 **유한 bootstrap 표본의 차이**다 (Codex 3): `gain` 은 재표본마다 격자 점 순서대로 `rng.integers` 를 부르므로 7 점 격자에서는 추가 네 점 (+6 … +15 dB) 이 난수를 소비해 두 번째 재표본부터 공통 세 점의 index 가 3 점 격자와 달라진다 (Codex 확인: 공통 세 점의 재표본을 같게 두면 두 격자 모두 [+0.0567, +0.2334], censored 0/2000; B 2000 · seed 20260925) |
| 3 점 격자의 SNR@0.1 (`snr_at`: 로그 선형 보간, 첫 하향 교차) | **V1 −2.226 dB**, V4 −2.084 dB (둘 다 kind ok; −3 → 0 dB 사이 교차). 이 등록의 L = SNR_ms(0.1) − SNR_V1(0.1) 에서 **SNR_V1(0.1) = −2.226 dB 는 이미 정해져 있다** |
| 앵커 규칙 (확인용) | 3 점 격자에서 V1 기준 · V4 기준 자동 판정점 모두 `['-3', '+0', '+3']` |

### 0.2 V1-ms 의 대수적 성질 (작성자 확인; 코드 `arms.MatchedScalarPrior`, `Demo/t2_gmm.py` `RouteAClip._matrix_site`, `Demo/t2_route_a.py` `RouteA.run` · `_sites`)

- V1 배선 (`MODULE_H['score']`: mode scalar, scal belief, hsite matrix, λ_min = 1e-6; `LOOP`: feedback posterior, β 0.7, eps 1e-6, n_inner 1) 의 한 반복에서 질의 (q, ν) 가 정해지면 `prior.denoise` 가 (m, α) 를 주고 (α = tr J₊ / N, [eps, 1 − eps] 로 clip), SC-VAMP 식으로 hE = (m − αq)/(1 − α), νE = α/(1 − α)·ν 를 만든 뒤 (다음 질의로 이어지는 scalar feedback), `_matrix_site(q, ν, G)` 가 L_X 가 보는 site (P = Λ + G, η) 를 만든다. V4 (hsite scalar) 는 `_matrix_site` 없이 P = I/νE + G, η = hE/νE 를 쓴다.
- V1-ms 의 `_matrix_site` 는 (m, (tr J₊/N) I) 를 받으므로 C = s I, s = ν·tr(J₊)/N = ν α₀ (α₀ = clip 전 α) 이고, Λ = (1/s − 1/ν) I = (1 − α₀)/(ν α₀) I = **I/νE′**, η = m/s − q/ν = **hE′/νE′** (νE′ · hE′ 는 α₀ 로 만든 SC-VAMP 양). 즉 clip (α ≠ α₀) 과 floor (λ_min) 가 걸리지 않으면 **V1-ms 의 site 는 V4 의 등방 site 와 같은 꼴**이다. 수치 확인 (합성 (q, m, J₊, G) 3 사례, N 32): max|P − (I/νE + G)| = 0, max|η − hE/νE| ≤ 3.6e-15, floor 0 회.
- 그러므로 V4 와 V1-ms 가 체계적으로 다른 곳은 **α 를 만드는 Jacobian** 이다: V4 는 수리하지 않은 J 의 Hermitian 부 (`psd_project=False`; α = tr(Herm J)/N), V1-ms 는 PSD 수리한 J₊ (`score.project_psd`, 고유값 floor λ_min; tr J₊ ≥ tr Herm J 이고 음의 고유값이 있을 때만 다름). 그 밖의 차이는 가장자리 경우 — V4 의 site 는 clip 한 α 로, V1-ms 의 site 는 clip 전 s 로 (α₀ ∉ (eps, 1 − eps) 일 때만 다름); λ_min floor 는 Λ 의 고유값 (1 − α₀)/(ν α₀) 이 λ_min = 1e-6 **미만**일 때만 (α₀ ≥ 1 이거나 νE′ > 1e6) — 와 수치 경로 (eigh · inv 대 스칼라 식) 다. 개발 질의에서 PSD 수리는 자주 걸린다: −3 dB 개발 시행 2560..2563 의 64 질의 중 33 에서 λ_min(Herm J) < 1e-6 (최소 −4.2e-2) 이고, 걸린 질의의 trace 변화 (tr J₊ − tr Herm J)/tr Herm J 는 중앙값 1.0e-2, 최대 4.2e-2 (α = tr/N 범위 0.19–0.44).
- **closed loop 주의** (과제 확인 4; S4): 첫 질의 (q, ν) 는 파일럿 site (G, b) 와 공통 상수 (`cbar`, `eh2_prior`; 같은 체크포인트 · 같은 Chat) 만으로 정해지므로 세 arm 이 같다 — `RouteA.run` 은 hE = 0, νE = cbar 로 시작하고, 반복 0 의 데이터 열은 x̄ = 0 이라 `_sites` (lh_form A: A_n = d_n·kron(x̄x̄ᴴ, I), B_n = d_n·kron(x̄*, y_n)) 에 0 을 더한다. **V1-ms ↔ V4** 는 첫 질의에 PSD 수리가 걸리지 않아 (개발 960 시행 모두; 증거는 반복 0 의 nmse 상대 차 ≤ 1.2e-15, §0.3) 첫 site 도 같고, 반복 1 부터 α 가 갈리며 (J₊ 대 Herm J) 그 뒤 사후 분포 · decoder feedback · 질의 궤적이 갈린다. **V1 ↔ V1-ms** 는 첫 site 가 다르므로 (행렬 대 등방) 반복 0 부터 다르다 (nmse 상대 차 |Δ|/nmse_V1 최대 0.28 · 0.38 · 0.75, §0.3). V1 ↔ V1-ms 의 설계 차이는 EP site 공분산의 꼴 (full C₊ 대 trace 를 맞춘 등방) 하나이므로 라벨 · L 은 그 한 가지 설계 차이의 closed-loop 결과라고 적을 수 있다 (§2.1 의 고정 설명과 함께); closed loop 를 뺀 기구적 서술 ("고정 질의에서 X dB") 과 V4 ↔ V1-ms 를 한 요인으로 돌리는 서술 ("floor 만의 몫", "Jacobian 수리만의 효과") 은 하지 않는다 (§2.3).

### 0.3 개발 스크린 (`e1ms/dev_screen.out`, `raw_E1MSdev`; 개발 시행 2560..2879, n 320 / 점; 2807dd23, 10-18 21:35–21:40 CDT, 12 워커 nice 10; 판정에 쓰지 않음)

| | −3 dB | 0 dB | +3 dB |
|---|---|---|---|
| 실패 / 320: V1 · V1-ms · V4 · genie | 38 · 38 · 37 · 11 | 11 · 10 · 10 · 5 | 2 · 4 · 4 · 1 |
| `V1-ms → V1` (a = V1-ms 만 실패 : b = V1 만 실패) | 6:6 (p 1) | 1:2 (p 1) | 2:0 (p .5) |
| `V4 → V1-ms` (a = V4 만 : b = V1-ms 만) | 0:1 (p 1) | 0:0 | 0:0 |
| `V4 → V1` | 5:6 (p 1) | 1:2 (p 1) | 2:0 (p .5) |

- L (개발, 3 점 격자) = −0.03 dB [90 % −0.33, +0.24], censored replicates 24 % (n 320 이라 재표본의 1/4 에서 교차가 없다); `V4 → V1-ms` −0.05 dB [−0.15, +0.00] (23 %); `V4 → V1` −0.08 dB [−0.35, +0.18] (28 %).
- 궤적 (작성자, `raw_E1MSdev`): **V1-ms ↔ V4** (nmse 상대 차 = |Δ|/nmse_V4, 뒤 arm) — 반복 16 의 blk_err 가 다른 블록 **1 / 960** (−3 dB 1, 0 · +3 dB 0; 어느 반복에서든 다른 블록 −3 dB 1, 0 dB 1, +3 dB 0); nmse 는 반복 0 에서 상대 ≤ 1.2e-15, **반복 1 에서의 최대** 상대 3.2e-3 (−3) · 2.9e-2 (0) · 2.3e-2 (+3) 로 갈리고, 그 뒤 반복에서는 일부 시행에서 최대 3.9 · 12.8 · 0.33 까지 벌어진다 (N2); nmse 궤적이 비트 동일한 시행은 세 점 모두 0. **V1 ↔ V1-ms** — 반복 0 부터 다르다: 반복 0 nmse 상대 차 **|Δ|/nmse_V1 (이 항목만 앞 arm V1 로 나눈 값; O3)** 최대 0.281 · 0.380 · 0.753, 중앙값 0.017 · 0.027 · 0.039 (S4) — 뒤 arm V1-ms 로 나누면 최대 0.390 · 0.614 · 3.046; 반복 16 blk_err 불일치 12 · 3 · 2 블록 (V4 ↔ V1 11 · 3 · 2).

### 0.4 과제의 확인 1–4 (`e1ms/check_ms.py` → `check_ms.out`, 10-18 21:30 CDT; `e1ms/e1ms_regress.sh` → `logs/e1ms_regress.log`; ba1b7c35)

1. fixed-query site: −3 dB, 개발 시행 2560..2561 에서 V1-ms 의 `_matrix_site` 호출 32 개 (2 시행 × 16 반복) 가, 같은 질의로 다시 계산한 (m, J₊) (`sp.denoise_full(q, ν)`; 결정적) 로 만든 정의식 (P = max(1/s − 1/ν, λ_min) I + G, η = m/s − q/ν) 과 최대 상대 편차 3.94e-16; floor 0 회. 감싼 prior 는 V1 의 것과 다른 객체 (자기 질의 카운터) 이고 `denoise` 는 감싼 prior 의 메서드 (assert 로 확인).
2. 등방 공분산 (J = cI, c = 0.3 · 0.7) · clip 비활성 입력: V1 과 V1-ms 의 site 차 (P, η) 가 0.
3. 회귀: `raw_B16e4k` 의 −3 dB 청크 0 (test 시행 0..39 — 과제가 지정한 "같은 입력의 작은 청크") 에서 V1 · V4 를 `--ms-arm` on / off 로 다시 돌림 (`--arm M-ours-dscore-C-V1 M-ours-dscore-C-V4` — **V1-ms 는 test 시행에서 돌리지 않았다**: runner 의 `--arm` 필터 (`runner.py:623`) 가 시행 루프 (:643) 앞에 있어 선택되지 않은 arm 은 돌지 않는다): 2 arm × 7 KEYS_RAW = 14 배열이 기록과 비트 동일 (on · off 모두), 청크에 다른 arm 없음, `meta|ms_arm` 은 on 에만 있음 → **새 정보 없음**. 10-18 21:28–21:29 CDT, **git 99f62bfb+dirty** (커밋 전 작업 사본; 1–2 분 뒤 ba1b7c35 로 커밋 — 커밋본에서의 재확인은 §5 병합 확인 (a)). 산출물 `raw_E1MSregon` · `raw_E1MSregoff` (추적 안 함, 지우지 않는다). **기록 (S3)**: 이 회귀와 병합 확인 (a) 는 실행 커밋의 DECISIONS 줄에 적는다 (14 배열 비트 동일, V1-ms 미실행, 새 정보 없음).
4. closed loop: §0.2 마지막 항목.

### 0.5 이미 정해진 것 (결과 전 공개)

- SNR_V1(0.1) = −2.226 dB (3 점 격자) → L = SNR_ms(0.1) + 2.226 dB 는 V1-ms 의 주변 BLER 곡선만의 함수다. V1 은 −3 dB 에서 0.1 위, 0 dB 에서 아래이므로 L 의 kind 는 V1-ms 가 정한다: F_ms(−3 dB) ≥ 257 (BLER > 0.1; 256 = 0.1 은 'lo') 이고 F_ms(0 dB) ≤ 256 이면 (또는 F_ms(0) > 256 이고 F_ms(+3) ≤ 256 이면) ok, 아니면 censored (§1.4).
- 주 비교의 점별 a − b = F_ms − F_V1 = F_ms − 371 / 88 / 29; 보조 비교의 a − b = F_V4 − F_ms = 394 / 96 / 21 − F_ms. 불일치 쌍 수 D = a + b ≥ |a − b|.
- 보조 비교에서 D 가 작을 가능성 (§0.2–0.3): 개발 960 블록에서 V4 ↔ V1-ms 불일치 1 → test 에서도 power guard (판정점 3 개 중 2 개 이상에서 D ≥ 6) 를 넘지 못해 (iv) 가 나올 수 있다. 그래도 라벨과 문장은 규칙대로이며 (iv) 를 동등성으로 바꾸지 않는다.

## 1. 고정되는 것

### 1.1 셀 · 자산 · arm

| 항목 | 값 |
|---|---|
| 셀 | D2 C2 8×4 (T 16, T_p 4, DFT 파일럿), prior S2, N′ = 1.6e5, QPSK (기본 `--mod` qpsk; `raw_B16e4k` 와 같은 코드 · 파일럿 · 송신 블록 — 수용 ① 의 genie 재생이 확인) |
| 체크포인트 (V1 · V1-ms 공통) | `ckpt/d2sx_N160000_a1.pt`, sha256 `4443921ce8d5c4a11c7cda879a53a66436f43bd76864734a3e6203cfb4b82f29`, role legacy-last, epoch 1784 (best 1764) — `run_e1ms.sh` 가 sha256 을 검사하고 `eval_accept` 가 raw 의 `meta|stagec_ckpt_id` (`sha256[:16]=4443921ce8d5c4a1`, `role=legacy-last`) 를 검사 |
| fits | `results/gmm_fits_D2_D2SITEMS` = `results/gmm_fits_D2_B16e4k` 의 바이트 복사본 (스크립트가 `cp -L` 로 만들고 링크 없음 · 개수 · cmp 검사); b\* = kron 1024 (ll_val −11.459169831224418); `fit_S2_Nr8_kronK1024_n160000.npz` sha256 `bf796b84037e1b3790ed5a6d7917ea2a79f2bee4a9f155f0d3385d856c950997`, `fit_S2_Nr8_fullK32_n160000.npz` sha256 `d4601650a888b4b355565a9010cf0a23499a3e92505e657e2cd79a1c152359f3` (작성자가 원본에서 확인; 스크립트가 복사본에서 검사) |
| **새 arm `M-ours-dscore-C-V1ms` (V1-ms)** | `--ms-arm`: 새로 만든 V1 ScorePrior (`psd_project=True`, 자기 질의 카운터) 를 `arms.MatchedScalarPrior` 로 감싸 V1 과 같은 배선 (`route_a(…, "score", clip="eta")` = RouteAClip, `MODULE_H['score']`, `LOOP`) 에 넣는다. 감싼 prior 의 `denoise_full(q, ν)` 는 (m, J₊) 대신 (m, (tr J₊/N) I) 를 돌려주고, V1 의 `RouteAClip._matrix_site` (clip 'eta') 가 그대로 돌아 C₊ = νJ₊ 대신 C = s I, s = tr(C₊)/N 로 Λ₀ = C⁻¹ − I/ν, η₀ = C⁻¹m − q/ν, Λ = Herm(Λ₀) 의 고유값을 λ_min = 1e-6 으로 floor, η = η₀ 를 만든다 — 과제 "V1-ms 의 정의" 와 같다 (§0.4 확인 1). Jacobian 수리 (J₊), precision floor (λ_min), decoder damping (β 0.7), 다음 질의를 위한 scalar feedback (α = tr J₊/N, eps clip 포함) 은 V1 과 같고 — `denoise` 는 감싼 prior 의 것 — clip 한 α 로 site 공분산을 다시 대체하지 않는다 (s 는 clip 전 값). meta: `ms_arm` 문자열, `learned|…V1ms` · `fit_sec|…` = V1 의 것 (같은 가중치). V1 · V4 · 다른 arm 의 코드 경로는 바꾸지 않았다 (§0.4 확인 3; 플래그 없는 호출은 옛 task 튜플 그대로) |
| V1-ms 의 비용 | full Jacobian (`jacrev`, 2N JVP) 을 계산한 뒤 trace 를 취한다 — 저비용 구현이 아니며 **비용 주장에 쓰지 않는다** (과제) |
| 비교 상대 (재사용) | `M-ours-dscore-C-V1` (V1, 행렬 site) · `M-ours-dscore-C-V4` (V4, hsite scalar; `psd_project=False` 의 prior) — `raw_B16e4k` 의 같은 test 시행, 같은 가중치 파일 (SITE16e4 §6.1). **다시 돌리지 않는다** |
| 같은 시행 대조 arm | `R5-genie` 를 V1-ms 와 같은 run 에 넣는다 — 새 raw 의 genie 가 `raw_B16e4k` 의 genie 와 모든 시행에서 비트 동일해야 같은 (H, 잡음, 송신 블록) 임이 확인된다 (수용 ①; SBL32 와 같은 방식). 판정에 쓰지 않는다 |

### 1.2 test 점 · 시행

| 항목 | 값 |
|---|---|
| SNR | −3, 0, +3 dB (판정점이자 격자 전부; 과제) |
| 시행 | 각 점의 시행 스트림 test 0..2559 (`skip0` 0, n 2560, chunk 40 → 64 청크 / 점, **192 청크**); V1 · V4 (`raw_B16e4k`) 와 같은 시행 |
| 반복 | 16 (BLER@16), CPU complex128 (01_RULES §9.3) |
| arm | `M-ours-dscore-C-V1ms`, `R5-genie` (둘뿐) |
| tag · 산출물 | `D2SITEMS` → `raw_D2SITEMS`, `logs/run_D2_D2SITEMS.log` (runner), `logs/run_e1ms.log` (스크립트), `results/review_next/e1ms/D2SITEMS_accept.txt`, `results/review_next/e1ms/compare_D2SITEMS.txt` |

### 1.3 실행 (동결 · 병합 뒤; main 의 실행 커밋에서, tmux; `code/run_e1ms.sh`)

| 항목 | 고정 값 |
|---|---|
| 시작 조건 (사람) | **V1LS test 가 끝났을 것** — `logs/run_v1ls_chain.log` 의 `CHAIN_DONE` (끊겼으면 `logs/run_v1ls.log` 의 네 run 의 `V1LS_DONE`) 과 V1LS 실행 뒤 기록 커밋 — 그 뒤에 병합; **사용자 승인** (D1: test 집합 실행과, 병합 확인 (a) 가 test 시행 0..39 에서 V1 · V4 를 다시 돌리는 것을 한 번에 묻는다; 승인 뒤에 병합 확인 (a)(b) → 실행 커밋 → 실행); 10/19 이후; 시작 전에 `ps` · `uptime` · `nvidia-smi` 로 다른 세션의 실행을 확인해 합이 96 스레드를 넘지 않을 때 (등록 실행 · 핵심 실험과 겹치면 이 실험이 양보). 스크립트도 V1LS 실행 스크립트가 돌고 있으면 ABORT 한다 — 가드는 명령줄 시작에 고정한 패턴 `^(/usr)?(/bin/)?bash .*[r]un_v1ls(_chain)?\.sh` (6b49603e, O1: 스크립트 이름만 언급한 프롬프트 · 편집기 프로세스는 잡지 않는다; M1c: V1LS 체인의 run 사이 — 수용 · compare 단계 — 는 runner 가 없어서 runner 가드만으로는 못 본다) |
| 명령 | `cd ~/t2/conf && E1MS_CPUS=24-47,120-143,72-95,168-191 bash code/run_e1ms.sh [--resume]` (CPU 96 = 공통 규칙의 절반; GPU 숨김 `CUDA_VISIBLE_DEVICES=`). 한 번에 하나의 runner 만 돈다 |
| 스크립트 전제 (하나라도 어기면 `ABORT (precondition)`, 실행 없음) | `E1MS_CPUS` 설정; `code/` · `Demo/` 청결; 이 문서와 s5 가 추적되고 HEAD 와 같음; HEAD = s5 를 마지막으로 건드린 커밋; s5 에 `FREEZE` · `WGB`; FREEZE 가 HEAD 의 조상; **이 문서가 FREEZE 와 같음** (`git diff --quiet FREEZE HEAD -- <이 문서>`, 6b49603e, O2); `git diff FREEZE HEAD -- code ../Demo` 비어 있음; 체크포인트 sha256; fits 복사본 (링크 없음, 개수, cmp, b\* · fullK32 sha256); `raw_B16e4k` 에 `D2_*.npz` 448; **`raw_B16e4k` 의 청크 가운데 manifest written (2026-09-23 07:36:44 KST) 보다 새 것이 없고 `git status` 가 깨끗할 것** (S1 — `e1ms_compare` 의 `manifest_check` 가 실행 뒤에야 거부하는 것을 실행 전에 막는다; main 의 청크 mtime 은 2026-09-22 21:23:28–21:39:55 KST, 작성 시점에 새 것 0 · 청결); 다른 runner 없음 (CPU 예산 공유 — 사용자에게 순서를 묻는다); V1LS 스크립트 없음 (위); `raw_D2SITEMS` 비어 있음 (`--resume` 제외). **main 에서 `raw_B16e4k` 를 다시 체크아웃하는 git 조작 (checkout · restore · stash 등) 은 하지 않는다** — mtime 이 새로워져 이 전제와 `manifest_check` 가 실패한다. worktree 의 `raw_B16e4k` 체크아웃은 mtime 이 2026-10-19 11:24 KST 라 상대 경로로는 REFUSED 되고, 절대 경로 `/home/HTJ/t2/conf/raw_B16e4k` 로만 통과한다 (KAT · 흐름 시험이 그렇게 돌았다, §4) |
| 주 실행 | `taskset -c $E1MS_CPUS python code/runner.py run --testbed D2 --prior S2 --cell C2 --ntrain 160000 --stagec-ckpt <ckpt> --chunk 40 --n 2560 --snr -3 0 3 --arm M-ours-dscore-C-V1ms R5-genie --ms-arm --worker-gb <WGB> --tag D2SITEMS` |
| 워커 | min(허용 CPU 수 96, 청크 192, ⌊0.8·MemAvailable / G⌋), G = WGB = 1.5 (§5 스모크) → 96 워커, 2 물결 |
| 수용 ① (`eval_accept.py`) | `--tag D2SITEMS:legacy-last:4443921ce8d5c4a1:C2 --prior S2 --ntrain 160000 --kron-K 1024 --ll-val -11.459169831224418 --points C2:-3,0,3 --chunk 40 --n 2560 --ref-raw raw_B16e4k` → `D2SITEMS_accept.txt`. 검사: 점 집합 = C2 × {−3, 0, 3}; 청크 계획 {(40k, 40)}, k < 64; 첫 · 끝 청크의 meta (ntrain 160000, bstar kron, kron_K 1024, ll_val|kron 과 1e-9 이내, `stagec_ckpt_id` 에 sha256[:16] · role, run|iters 16); **genie 재생 — 모든 점의 모든 시행 (2560 / 점) 에서 `R5-genie` 의 blk_err · ber · tauL_gmean · alphaD @1..16 이 `raw_B16e4k` 와 비트 동일 (NaN = NaN)**; 태그 간 (bstar, kron_K, em_sec) 일치 |
| 수용 ② (스크립트 내장) | 모든 청크: `run|git` = 실행 커밋 (short; `+dirty` 없음 — runner 는 `code/` · `Demo/` 가 더러우면 `+dirty` 를 붙인다), `meta|ms_arm` 있음, **청크의 arm 집합이 정확히 {`M-ours-dscore-C-V1ms`, `R5-genie`}** (N8, 7326010c), 두 arm × KEYS_RAW 7 개 모양 (40, 16); 청크 수 192 |
| 분석 | ① · ② 가 모두 OK 일 때만 `code/e1ms_compare.py --raw raw_D2SITEMS --base raw_B16e4k --out results/review_next/e1ms/compare_D2SITEMS.txt` (§1.4). 스크립트의 자체 검사 (하나라도 어기면 `REFUSED`, 아무것도 계산하지 않음): 두 raw 에 `load_raw` WARNING 없음 (NOTE = raise 된 블록은 실패로 세고 출력); raw 의 점 = 정확히 −3 / 0 / +3 이고 base 에 있음; 모든 점에서 n 2560 과 arm 존재 (raw: V1-ms · genie, base: V1 · V4 · genie); raw 의 `run|git` 이 깨끗한 한 커밋, base 는 manifest 검사 (`manifest_check`: 추적 · 청결, 448, 점 목록, 청크 mtime ≤ manifest 시각, 추적 raw 청결); 모든 점에서 genie 의 KEYS4 가 두 raw 에서 동일 (`pair_cross.same`). 수용이 실패하면 `compare: NOT RUN` |
| 끝 표시 | `logs/run_e1ms.log` 의 `E1MS_DONE ok=<n> fail=<n>`; fail = runner 비정상 종료 (1) + 실패한 단계 수 (수용 실패로 compare 를 안 돌린 것도 1); 종료 코드 = fail |

### 1.4 분석 (`code/e1ms_compare.py`; `pair_baselines.table_b` · `analysis.gain` · `fails` 그대로; 수치만, 해석 없음; v1 과 같다)

- **주 비교 `V1-ms → V1`** (출력 `[primary] M-ours-dscore-C-V1ms -> M-ours-dscore-C-V1`): a = V1-ms 만 실패, b = V1 만 실패 (`paired`, 반복 16; raise 된 블록은 `load_raw` 가 1.0 = 실패로 바꾼다). **판정점 −3 / 0 / +3 dB 고정** (과제; `table_b(…, cand=SNRS)`). 앵커 규칙 (`decision_points`: BLER@16 ∈ [0.005, 0.9] 인 점 가운데 |log10(BLER/0.1)| 최소 3 점, 앵커 = 쌍의 첫 arm) 은 `check: the anchor rule on … gives […]` 확인 줄로만 출력하고 판정에 쓰지 않는다 (다른 셋을 내더라도 고정 판정점으로 판정하고 그 사실을 §6 에 적는다).
  - 검정: 판정점마다 불일치 블록의 exact 양측 부호검정 (`sign_p`), p < .05. power guard: 판정점 3 개이고 그중 2 개 이상에서 D = a + b ≥ 6 (`MIN_DISC`); 아니면 (iv). 라벨은 `table_b` 순서 **(iv) → (i) → (ii) → (iii)**: (i) = "second arm fewer" (b < a, p < .05) 인 점 2 개 이상 → V1 이 적게 실패, (ii) = "first arm fewer" (a < b, p < .05) 인 점 2 개 이상 → V1-ms 가 적게 실패, (iii) = POWERED 이고 둘 다 아님. pooled a:b · p 는 출력하지만 라벨에 쓰지 않는다 (보고 전용).
  - **SNR 손실 L** = `SNR@0.1 gap (M-ours-dscore-C-V1ms minus M-ours-dscore-C-V1)` = `gain(data, …, x=V1-ms, y=V1)`: 각 arm 의 SNR@0.1 은 3 점 격자 위의 로그 선형 보간 (`snr_at`: log10 BLER 의 첫 하향 교차; BLER 은 0.5/n 아래로 내리지 않음); 90 % paired bootstrap — **B 2000, `numpy.random.default_rng(20260925)`** (`Demo/exp_0925_analysis.py` `gain` 의 값; `pair_baselines.SEED` 20260926 은 R 의 bootstrap 전용이라 여기 쓰이지 않는다), 시행 index 를 점마다 재표집하되 두 arm 에 같은 index, 5 · 95 백분위, 교차 없는 재표본은 `censored replicates` % 로. **양수면 scalar 쪽 (V1-ms) 손실**. 점추정의 kind 가 ok 가 아니면 (어느 arm 이든 3 점 격자에 교차가 없으면 `gain` 은 `>= …` 또는 `n/a (…)` 문자열을 낸다) **L 은 censored** 로 보고하고 구간을 쓰지 않는다; SNR 점을 늘리지 않는다 (공통 규칙).
- **보조 비교 `V4 → V1-ms`** (출력 `[secondary, report-only] M-ours-dscore-C-V4 -> M-ours-dscore-C-V1ms`): a = V4 만 실패, b = V1-ms 만 실패; 같은 판정점 · 검정 · 라벨 규칙 · `gain(x=V4, y=V1-ms)` (양수면 V4 쪽 손실). **보고 전용** — 라벨은 적되 판정 · 문장의 근거로 쓰지 않는다. Jacobian 수리와 site 생성 규칙이 함께 다른 비교이므로 (§0.2) **"floor 만의 몫" 이라고 부르지 않는다**.
- BLER 표: 판정점 × arm (V1, V4, V1-ms, genie) 의 실패 수 / 2560 (raise 된 블록 = 실패).
- **다중성**: 판정 라벨 1 개 (주 비교); 보조 비교 라벨은 보고 전용. 보정 없음. 이 쌍은 08_SPEC §2 의 쌍 목록 밖이며 이 등록이 더한 것이다 (SITE16e4 의 `V4 → V1` 과 같은 지위); 검정 규칙은 표 B 그대로이고 08_SPEC 은 바꾸지 않는다.

### 1.5 예외 · 중단

- runner 비정상 종료 · 메모리 초과: 같은 HEAD 에서 `E1MS_CPUS=24-47,120-143,72-95,168-191 bash code/run_e1ms.sh --resume` (Codex 2: 환경변수는 그 명령에만 전달되므로 재개 때도 붙인다 — 없으면 스크립트 19 행이 die; 끝난 청크는 건너뛴다; raw 는 지우지 않는다). 수용 ① · ② 실패 또는 compare `REFUSED` → 분석 표를 결과로 쓰지 않고 원인과 함께 사용자에게 보고 (재실행은 사용자 결정; 새 tag).
- `ABORT (precondition)` 가운데 "another runner … is active" · "the V1LS test … is still running" 은 자원 · 순서 충돌이다 — 기다리거나 사용자에게 순서를 묻는다 (공통 규칙 §4). V1LS 체인이 돌고 있으면 병합 · 실행 모두 기다린다 (머리말). 미리 정한 중단 규칙은 묻지 않고 적용한 뒤 보고한다.
- 한 작업일 (착수 10-18 21:24 CDT 부터) 안에 **구현 · 확인 (= FREEZE 커밋)** 이 끝나지 않으면: 원인과 상태를 이 문서 §6 과 DECISIONS 에 기록하고 멈춘다; 원고는 기존 scalar 대조 (V4) 만 쓴다 (과제). 동결 뒤의 병합 · s5 · 실행은 V1LS 뒤 자원이 날 때 (10-24 18:00 CDT 전) 한다; 그 안에 못 하면 결과는 원고에 넣지 않는다 (공통 규칙 §2).
- 판정하지 못함 ((iii) · (iv)) 도 완료된 결과. 점 · 표본을 늘리지 않고, 결과에 따라 셀을 더하지 않는다.
- 실행 중 main 에 커밋하지 않는다; 이 문서 · `conf/code` · `Demo` · DECISIONS 를 고치지 않는다 (실행 뒤의 DECISIONS 줄은 모았다가 끝난 뒤; 실행 시작 줄은 실행 커밋에 — 머리말).

### 1.6 하지 않는 것

UMi32 확장, k-probe (Hutchinson) 같은 새 scalar 알고리즘, 결과에 따른 추가 셀 (과제); V1 · V4 의 재실행 (비교 자료로서 — `raw_B16e4k` 를 대신하거나 보태는 재실행을 뜻한다; §5 병합 확인 (a) 의 회귀 40 시행 (test 0..39, −3 dB, 비트 대조 전용, 승인 범위 안) 은 예외); 다른 SNR · 격자 확장; 다른 체크포인트 · 예산 · 변조; test 를 본 뒤 판정점 · 규칙 · 문장 · arm 정의 변경; V1-ms 를 비용 주장이나 "저비용 scalar" 로 쓰기; 비열등 margin 신설; V1LS test 가 끝나기 전의 main 커밋 (병합 포함) · runner 실행 (M1); E1+ 실행이 끝나기 전의 `e4-cost` (E4 비용 벤치 브랜치; e1-ms 9dd8b5fe 에서 갈라짐) 병합 — 먼저 병합하면 `git diff FREEZE HEAD -- code ../Demo` 가 비지 않아 ABORT 다 (verifier A2); main 에서 `raw_B16e4k` 를 다시 체크아웃하는 git 조작 (S1); 기존 등록 (B16e4k · SITE16e4) 의 §1–§3 · 라벨 수정 (이 결과는 어느 기존 판정도 바꾸지 않는다); 원고 저장소 (T2-ICC2027-paper) 수정.

## 2. 라벨 · 문장 (결과 전 고정; 원고 반영 여부 · 자리는 사용자 결정)

### 2.1 주 비교 (라벨은 compare 출력 `[primary]` 블록의 `-> (…)` 가 정한다)

- (i) "V1 (행렬 site) 이 V1-ms (matched-scalar site) 보다 적게 실패 (판정점 −3 / 0 / +3 dB 가운데 {2 | 3} 점에서 p < .05)" — {2 | 3} 은 POWERED 줄의 `second arm fewer at k/3` 의 k.
- (ii) "V1-ms (matched-scalar site) 가 V1 (행렬 site) 보다 적게 실패 (… {2 | 3} 점에서 p < .05)" — k 는 `first arm fewer at k/3`.
- (iii) "판정하지 못함 (유의 방향 없음)" — 라벨 문자열은 표 B 의 것 그대로이고 뜻은 2/3 규칙이다: POWERED 이지만 어느 쪽 arm 도 판정점 3 개 중 **2 개 이상에서** 자기 쪽으로 p < .05 를 얻지 못함 (`table_b` 의 wy < 2 이고 wx < 2); 개별 유의점은 있을 수 있다 (기록된 `V4 → V1` 의 −3 dB 56:33 p .019 가 (iii) 의 예; Codex 1) — 그 점의 방향과 p 는 §6 에 그대로 적는다. (iv) "판정하지 못함 (검정력 미달)".
- **L 문장 (항상 붙인다)**: kind ok 이면 "SNR 손실 L = SNR_ms(0.1) − SNR_V1(0.1) = {x} dB [90 % paired bootstrap {l}, {u}] (양수 = scalar 쪽 손실; 3 점 격자 −3 / 0 / +3 dB; censored replicates {c} %)" — x · l · u · c 는 `gain` 문자열의 네 수 그대로 (부호 포함, 소수 둘째 자리). kind 가 ok 가 아니면 "L: censored (3 점 격자에 교차 없음 — `gain` 출력: `{문자열 그대로}`; 격자는 늘리지 않는다, §1.6 — 출력 속 'extend the SNR grid' 는 `gain` 의 도우미 문자열일 뿐이다)" (N6).
- 혼합 결과 (라벨 (i) 에서 한 점이 V1-ms 쪽 유의; 라벨 (ii) 에서 한 점이 V1 쪽 유의 — 예 6:0 / 0:6 / 0:6 → (ii) (v2.3 O2); 또는 (iii) 에서 서로 다른 방향의 유의 점 — 예 8:0 / 0:8 / 3:3): 라벨과 첫 문장은 규칙대로 두고 §6 과 보고에 점별 방향 · p 를 그대로 적는다. 문장을 더 만들지 않는다.
- 모든 문장 끝에 V1-ms 의 **고정 설명**을 붙인다: "V1-ms = V1 과 같은 가중치 · 배선 · 안정화 (Jacobian PSD 수리, precision floor λ_min, decoder damping, scalar feedback) 에서 EP site 의 공분산만 C₊ = νJ₊ → (tr C₊/N) I 로 바꾼 arm (설계 차이는 이것 하나); 첫 질의 뒤 두 arm 의 질의 궤적은 갈린다; full Jacobian 을 계산하므로 저비용 구현이 아니다".
- 허용 꼴 (선택; M2): "두 arm 은 설계상 EP site 공분산의 꼴 (full C₊ 대 trace 를 맞춘 등방) 만 다르므로, 라벨 · L 은 그 한 가지 설계 차이의 closed-loop 결과다" — 항상 위 고정 설명과 함께 쓴다; 원고에 넣을지는 사용자 결정.
- **허용 목록 (verifier A1; v2.2 선택 3)**: 결과 문장에 붙는 해석은 위 고정 설명 · 이 허용 꼴 · §2.2 의 고정 문장 **셋뿐**이다. 그 밖의 해석 표현 (예: "행렬 site 가 더하는 몫 X dB", "방향 정보의 가치") 은 이 등록이 만들지 않으며, 결과를 본 뒤 사용자가 정한다.
- 범위: 이 셀 · 예산 · prior (Sparse specular 8×4, N′ = 1.6e5), 판정점 −3 / 0 / +3 dB, test 시행 0..2559.

### 2.2 보조 비교 (보고 전용 — 문장 하나, 판정 근거 아님)

"보조 (보고 전용) `V4 → V1-ms`: {라벨} — (i) 'V1-ms 가 V4 보다 적게 실패', (ii) 'V4 가 V1-ms 보다 적게 실패', (iii) '판정하지 못함 (유의 방향 없음)', (iv) '판정하지 못함 (검정력 미달)'; 점별 a:b · p {출력 그대로}; SNR@0.1 격차 (V4 − V1-ms) {gain 문자열, 또는 censored}. V4 와 V1-ms 는 Jacobian 수리 (V4 없음 · V1-ms 있음) 와 scalar site 를 만드는 경로가 함께 다르다 (§0.2)".

### 2.3 쓰지 않는 문구 (M2 로 좁힘)

- 공통 규칙의 금지 표현 ("동등", "비열등", "최적 GMM", "scaling law"); "비긴다", "차이 없음" ((iii) · (iv) 를 이렇게 바꾸지 않는다; 비열등 margin 을 새로 두지 않는다); "모든 SNR 에서".
- **V4 ↔ V1-ms 의 차이를 한 요인으로 돌리는 표현**: "floor 만의 몫", "Jacobian 수리만의 효과" (Jacobian 수리 · site 경로 · clip 가장자리 · 수치 경로가 함께 다르고 closed loop 가 갈린다, §0.2).
- **V1 ↔ V1-ms 의 closed loop 를 뺀 기구적 서술**: "고정 질의에서 X dB", "site 한 번의 효과가 X dB" 처럼 라벨 · L 을 한 반복의 site 차이로 환원하는 표현 (두 arm 은 첫 site 부터 궤적이 갈린다, §0.2). 허용 꼴은 §2.1 (설계 차이가 site 공분산의 꼴 하나라는 서술은 그 자체로 금지가 아니다).
- "저비용 scalar" · 비용 비교에 V1-ms 를 쓰는 표현.
- 허용 목록 방식 (A1; v2.2 선택 3): 위에 없는 표현이라도 허용 목록 (§2.1 고정 설명 · 허용 꼴 · §2.2 고정 문장) 에 없는 해석은 결과 문장에 붙이지 않는다; 그런 해석은 결과를 본 뒤 사용자가 정한다.

### 2.4 원고용 영어 문장 틀 (선택; 넣을지 · 어디에 넣을지는 사용자; 매크로 없이 적는다)

- (i): `In paired sign tests, the matrix-site receiver fails less than its matched-scalar variant at {two of the three | all three} tested SNRs.` (ii): `In paired sign tests, the matched-scalar variant fails less than the matrix-site receiver at {two of the three | all three} tested SNRs.` (iii): `In paired sign tests, the comparison between the matrix-site receiver and its matched-scalar variant is not decided: neither receiver has p < 0.05 in its favor at two or more of the three tested SNRs.` (Codex 1 · verifier 선택 1 · v2.3 O1: 원고 IV-A 의 "p<0.05 in its favor at two or more of the three SNRs" 꼴 — "2 점 이상" 이 각 receiver 에 붙는다; 개별 유의점은 있을 수 있고, 두 점이 서로 다른 방향으로 유의해도 (iii) 이며 이 문장은 그때도 참이다) (iv): `In paired sign tests, the comparison between the matrix-site receiver and its matched-scalar variant is not decided: too few blocks are discordant for the sign test.` (N7)
- SNR 명사 (v2.3 O1): (i) · (ii) · (iii) 모두 **"tested SNRs"** 로 통일한다 — 이 등록에서는 판정점 = 격자 전부 = {−3, 0, +3} dB 라 같은 집합이고, 원고에 "decision SNRs" 가 정의돼 있는지는 여기서 확인할 수 없어 SITE16e4 §2 의 원고 문장과 같은 "tested SNRs" 를 골랐다.
- 공통 (kind ok): `Relative to the matrix-site receiver, the matched-scalar variant reaches BLER 0.1 at an SNR offset of {L}\,dB [${l}$, ${u}$] (positive: more SNR needed).` — L · l · u 는 §2.1 의 x · l · u 와 같은 수 (부호 포함). censored 이면 이 문장을 쓰지 않고 §6 에만 적는다.

## 3. 미리 적는 예측 (test 미열람; 근거 = §0.1 의 기록된 V1 · V4 test 수치와 §0.2–0.3 의 개발 근거; 채점은 `compare_D2SITEMS.txt` 의 출력 줄로; 모두 채점용이며 판정이 아니다)

근거 요약: V1-ms 의 site 는 V4 의 등방 site 와 같은 꼴이고 (§0.2), 개발 960 블록에서 V4 ↔ V1-ms 의 반복 16 결과가 1 블록만 달랐다 (§0.3). 그래서 test 의 `V1-ms → V1` 은 기록된 `V4 → V1` (56:33 · 23:15 · 6:14, (iii), 3 점 격자 +0.14 dB [+0.05, +0.23]) 과 비슷하게 나오리라 예측한다. 개발 스크린의 L = −0.03 dB 는 n 320 (censored 24 %) 의 값이라 이 예측에 쓰지 않는다.

1. 주 비교 라벨 = **(iii)** (채점: `[primary]` 블록의 `-> (…)`).
2. −3 dB: V1 쪽 유의 (a > b, p < .05). 0 dB · +3 dB: 유의 아님 (p ≥ .05). 혼합 결과 아님 (V1-ms 쪽 유의 점 0).
3. POWERED = True (세 점 모두 D ≥ 6).
4. L: kind ok, censored replicates 0 %, 점추정 **L ∈ [+0.04, +0.25] dB** (채점: `SNR@0.1 gap (… V1ms minus … V1)` 줄).
5. L 의 90 % 구간의 **출력 하한 ≥ +0.01** (N5; 예측 4 보다 불확실 — 기록 쌍의 3 점 격자 하한이 +0.05 라 경계 근처).
6. 보조 비교 `V4 → V1-ms`: 라벨 **(iv)** — 판정점 가운데 D ≥ 6 인 점이 2 개 미만 (대안은 (iii)). 점별 D ≤ 20 / 10 / 10 (−3 / 0 / +3 dB; 채점: `[secondary …]` 블록의 sign test 줄의 a + b).
7. 실패 수: |F_ms − F_V4| ≤ 20 / 10 / 10 (−3 / 0 / +3 dB); F_ms(−3 dB) > 371 (= F_V1) 이고 F_ms(+3 dB) < 29 (BLER 표로 채점).
8. 앵커 규칙 확인 줄: 두 블록 모두 `['-3', '+0', '+3']`.
9. 수용 ① · ② OK; compare 의 NOTE 줄 0 (raise 된 블록 0 — V1-ms 는 개발 24 청크에서 경고 0, `raw_B16e4k` 는 raised 0).
10. runner 벽시계 ≤ 15 분 (§5 추정).
11. 빗나갈 경로: 수용 실패 → compare NOT RUN; 전제 위반 → ABORT; 한 작업일 초과 → §1.5.

## 4. 선행 작업 · 검토

| 항목 | 상태 (출처) |
|---|---|
| 코드 (Claude, worktree `e1-ms`; 이 등록은 판정 코드를 바꾸지 않는다) | ba1b7c35 (10-18 21:30 CDT): `arms.MatchedScalarPrior`, `build_our_arms(score_prior_ms=…)`, runner `--ms-arm` (build_point / task 튜플 25 번째 / CLI / meta `ms_arm`; `--stagec-ckpt` · `--tag` 필요; 기본 경로 불변) — 확인 1 · 2 · 3 (§0.4). 2807dd23 (21:34 CDT): `code/e1ms_compare.py`, `code/run_e1ms.sh`, `e1ms/rss_smoke_e1ms.py`. 3478d237 (21:41 CDT): 스모크 · 개발 스크린 기록 (§0.3, §5). 9dd8b5fe (22:02 CDT): 등록 v1, `e1ms/kat_make.py` · `kat_compare.txt`, 스모크 `eval_accept` 인자. **7326010c (22:23 CDT)**: 검토 기록 + `run_e1ms.sh` — V1LS 가드 (M1c), `raw_B16e4k` mtime · clean 전제 (S1), accept_raw 의 arm 집합 검사 (N8); 판정 · 분석 코드 (`e1ms_compare.py`) 는 그대로. **1de35f0c (22:24 CDT)**: 흐름 시험 기록 (아래). f460f7b6 (22:35 CDT): 등록 v2. **6b49603e (22:50 CDT)**: `run_e1ms.sh` — V1LS 가드를 명령줄 시작 고정 패턴으로 (O1), 이 문서의 FREEZE 불변 검사 `git diff --quiet $FREEZE HEAD -- $REG` (O2); 판정 · 분석 코드는 그대로 |
| 분석 코드의 정답 사례 (Claude; `e1ms/kat_make.py` → `kat_compare.txt`, 9dd8b5fe; N1) | 합성 raw = `raw_B16e4k` 의 −3 / 0 / +3 dB 192 청크에서 V1 → V1-ms 로 이름만 바꾼 것 (genie · meta · run 유지, `run|git` 'katfake0'; base 는 절대 경로): 주 비교 0:0 · 0:0 · 0:0 → (iv), +0.00 dB [+0.00, +0.00]; 보조 `V4 → V1-ms` = 기록된 `V4 → V1` 과 같은 부호검정 줄 (56:33 · 23:15 · 6:14, pooled 85:62, (iii)) 과 +0.14 dB [+0.05, +0.23]; 앵커 확인 줄 둘 다 `['-3', '+0', '+3']`. 작성자는 3 점 격자의 `V4 → V1` 을 `table_b` · `gain` 으로 독립 재계산해 같은 값을 얻었다 (§0.1) |
| **흐름 시험 (S2; Claude, 1de35f0c; `e1ms/flow/make_flow.py` · `flow_run_E1MSflow*.sh` · `flow_E1MSflow*.out`, `logs/e1ms_flow.log`, 10-18 22:23 CDT)** | 합성 raw (`raw_B16e4k` 3 점 192 청크, V1 → V1-ms, `run|git` = HEAD 7326010c, 스모크 청크의 `meta|ms_arm` · `stagec_ckpt_id` 등) 에 **전제와 runner 호출만 뺀 `run_e1ms.sh` 사본** (경로 worktree, base 절대 경로) 을 돌렸다. 정상 경로: accept_eval OK (`E1MSflow_accept.txt`: ACCEPT OK, `--ref-raw` genie 재생 포함) · accept_raw OK (192 chunks, 0 problems) · compare OK → `E1MS_DONE ok=3 fail=0`; `compare_E1MSflow.txt` 의 본문은 `kat_compare.txt` 와 같다. 청크 하나를 뺀 경로: accept_eval FAILED (chunk plan, genie 재생 shared 2520/2560) · accept_raw FAILED (191 chunks) → `compare: NOT RUN` → `E1MS_DONE ok=0 fail=3`, exit 3 (검토자가 적은 fail=2 가 아니라 코드대로 수용 둘 + NOT RUN 하나 = 3). 작성자의 v1 확인 (`bash -n` 통과; 수용 ② 조각을 스모크 raw 에 — 1 chunk, 0 problems) 은 이로써 대체된다 |
| 개발 스크린 · 스모크 | §0.3 · §5 |
| 회귀의 기록 (S3) | 확인 3 (`99f62bfb+dirty`, §0.4) 과 §5 병합 확인 (a) — test 시행 0..39 (−3 dB) 에서 V1 · V4 만 다시 돌린 것 — 은 **실행 커밋의 DECISIONS 줄**에 함께 적는다: 14 배열 비트 동일, V1-ms 미실행 (runner 의 `--arm` 필터가 시행 루프 앞), 새 정보 없음 |
| 검토 계획 (공통 규칙 §3: 검토 · 감사 각 1 회) | ① Fable 적대적 검토 1 회 — 끝남 (`prereg_reviews_2026-10-18/review_D2SITEMS.md`, MUST 2 · SHOULD 4 · NIT 8, 모두 수용) → 반영 = v2 (f460f7b6) + 7326010c · 1de35f0c → ② Codex 교차 검토 (코드 + 문서, 대상 f460f7b6) — 끝남 (`~/t2/reviews/20261019-123541-prompt_pretest_e1ms.md`: 결함 3, 모두 수용; 처리는 그 파일 끝; 의견이 갈린 항목 없음) 와 verifier (v2 의 고친 범위: D1 · A1 · A2 · O1–O3) → 반영 = v2.1 (a7240aad) + 6b49603e → verifier v2.1 재검토 (결함 0, 선택 4) → v2.2 (7de0d3c8) → verifier v2.2 재검토 (결함 1, 선택 2) → **이 v2.3** → ③ **FREEZE = 이 판 (v2.3) 을 담은 `e1-ms` 커밋** (한 작업일 안; 머리말) → **(D1 순서)** V1LS 종료 · 기록 커밋 → `e1-ms` 를 main 에 병합 → **사용자 승인** (test 실행 + 병합 확인 (a) 의 test 시행 0..39 V1 · V4 재실행) → 병합 확인 (a)(b) (§5) → s5 + 실행 시작 DECISIONS 줄 (승인 인용) = 실행 커밋 → 실행 → 수용 → §6 전사 → 기록 감사 1 회 → `docs/RESULTS.md` 새 절 · `conf/DECISIONS.md` · `docs/EXPERIMENTS.md` 줄 (KST · CDT 병기) |
| 남은 것 | ③ FREEZE (이 판 (v2.3) 을 담은 e1-ms 커밋; 10-19 21:24 CDT 안); V1LS 종료 뒤 병합 → 승인 → 병합 확인 → s5 → 실행 |

## 5. 평가 전 고정 기록

- **스모크** (`e1ms/rss_smoke_e1ms.py`, 10-18 21:34–21:35 CDT; raw 의 run|git 2807dd23; `e1ms/log_smoke.txt`): −3 dB 개발 청크 하나 (시행 2560..2599) 를 V1-ms + genie, jobs 1 로 → rc 0, 벽시계 49 s (청크 47 s), max RSS 0.966 GB → **G = ⌈1.05·RSS / 0.5⌉·0.5 = 1.5**. `eval_accept`: `ACCEPT: OK -- E1MSsm` (`e1ms/smoke_accept.txt`; 인자 `--tag E1MSsm:legacy-last:4443921ce8d5c4a1:C2 --prior S2 --ntrain 160000 --kron-K 1024 --ll-val -11.459169831224418 --points C2:-3 --chunk 40 --n 40 --skip0 2560`, `--ref-raw` 없음 — 개발 시행이라 기준 raw 가 없다; 9dd8b5fe 에 기록). 스모크 raw 의 `meta|stagec_ckpt_id` = `sha256[:16]=4443921ce8d5c4a1 epoch=1784 best_epoch=1764 role=legacy-last 8x4 | …`, arm 둘뿐, `meta|ms_arm` 있음. test 시행의 `--ref-raw` 경로는 흐름 시험이 확인했다 (§4).
- **추정 시간**: 192 청크, 96 워커 → 2 물결. 청크 하나 (두 arm, jobs 1) 47 s; 개발 실행 (네 arm, 12 워커, nice 10) 에서는 청크 137–146 s, 24 청크 4.8 분. 96 하이퍼스레드가 함께 돌면 느려지므로 **2–15 분** 으로 잡는다 (예측 10).
- **자산 고정**: 체크포인트 · fits sha256 (§1.1); base `raw_B16e4k` = `manifest-head:cd241b7e/chunks-sha:78cbb59fc01ce520` (compare 머리말에 같은 값이 나와야 한다); main 의 `raw_B16e4k` 는 manifest written 보다 새 청크 0 · 청결 (10-18 22:24 CDT 확인; S1 전제); V1 · V4 의 가중치 = 같은 파일 (SITE16e4 §6.1).
- **코드 고정** (HEAD 6b49603e 의 sha256[:16]; FREEZE 와 실행 커밋에서 같아야 한다 — 다르면 s5 를 만들기 전에 사용자에게 보고): `code/arms.py` 145f9b568e83a681, `code/runner.py` 9967a6b96a7f6fc2, `code/run_e1ms.sh` **e99f2483951d274c** (6b49603e; v2 는 dfc23bbe96919423, v1 은 e1a8bd16ddab8fad), `code/e1ms_compare.py` 9f19154555ccf3bc, `code/eval_accept.py` d05b660c07e899fe, `code/pair_baselines.py` f11cea47e8c9c83c. 동결 전에 코드가 다시 바뀌면 이 줄을 갱신한다.
- **병합 확인** (V1LS 종료 뒤 · 병합 뒤 · **사용자 승인 뒤** · s5 커밋 전 — (a) 가 test 시행 0..39 에서 V1 · V4 를 다시 돌리므로 승인 범위에 넣어 test 실행과 함께 묻는다 (D1); 결과는 실행 커밋의 DECISIONS 줄에 (S3) — 이 문서에는 적지 않는다 (FREEZE 뒤 이 문서는 실행까지 불변, O2)): main 의 병합 커밋에서 (a) `e1ms_regress.sh` 와 같은 청크 (`raw_B16e4k` −3 dB, test 0..39) 를 V1 · V4 · `--ms-arm` on 으로 다시 돌려 14 배열 비트 대조 (확인 3 이 `99f62bfb+dirty` 의 작업 사본에서 돈 것을 커밋본 · 병합본에서 다시 확인; V1-ms 는 돌리지 않는다), (b) 개발 청크 2560..2599 (−3 dB) 를 V1-ms + genie 로 돌려 `raw_E1MSdev` 의 같은 청크와 V1-ms 의 KEYS_RAW 7 배열 비트 대조. 하나라도 다르면 s5 를 만들지 않고 사용자에게 보고. 경로 · tag 만 바꾼 스크립트 사본을 쓰고 (돌고 있는 스크립트를 고치지 않는다), 산출물은 지우지 않는다. V1LS 체인이 돌고 있는 동안에는 (a) · (b) 도 돌리지 않는다 (runner 가 V1LS 의 가드에 잡힌다).
- **s5 형식** (`results/review_next/e1ms/e1ms_s5.txt`, 두 줄): `FREEZE <e1-ms 의 FREEZE 커밋 해시>`, `WGB 1.5`. FREEZE 해시는 s5 에만 적는다. s5 와 실행 시작 DECISIONS 줄 (사용자 승인 인용) 을 더한 커밋이 실행 커밋이고, 그 커밋은 `code/` · `Demo/` 와 이 문서를 건드리지 않는다.
- **병합 순서 (verifier A2)**: `e4-cost` (E4 비용 벤치 브랜치, e1-ms 9dd8b5fe 에서 갈라짐) 는 E1+ 실행이 끝난 뒤에만 main 에 병합한다 — 먼저 병합하면 `git diff FREEZE HEAD -- code ../Demo` 가 비지 않아 `run_e1ms.sh` 가 ABORT 한다.
- 실행 전 산출물 없음 (10-18 22:24 CDT, main): `results/review_next/e1ms/`, `logs/run_e1ms.log`, `raw_D2SITEMS`, `results/gmm_fits_D2_D2SITEMS` 모두 없음 (worktree 의 `raw_E1MS*` · `results/gmm_fits_D2_E1MS*` 는 개발 · 시험 산출물이며 추적하지 않는다).

## 6. 결과 (이 절은 추가만 한다)

기록 2026-10-19 08:49 CDT (= 10-19 22:49 KST, Opus 5.5). 출처: `results/review_next/e1ms/compare_D2SITEMS.txt` (`code/e1ms_compare.py` 출력, 수치는 옮긴 것), `logs/run_e1ms.log`, `logs/run_D2_D2SITEMS.log`, `e1ms/D2SITEMS_accept.txt`, `e1ms/console_D2SITEMS.txt` (tmux 화면 저장).

### 6.1 실행 · 수용
- 실행 커밋 9a2c9fd4 (s5: FREEZE e6ac9e65 · WGB 1.5). 사용자 승인 "다 진행하자" (DECISIONS 실행 시작 줄). 병합 확인 E1MS_MERGECHK OK (10-19 08:40–08:41 CDT; (a) test 0..39 의 V1 · V4 14 배열 on · off 비트 동일, V1-ms 미실행; (b) 개발 청크의 V1-ms + genie = `raw_E1MSdev` · `raw_E1MSsm`; 그 DECISIONS 줄).
- tmux `e1ms`, `E1MS_CPUS=24-47,120-143,72-95,168-191 bash code/run_e1ms.sh`, 워커 96 (메모리 가드 허용 529), 재개 없음. 10-19 08:42 CDT 시작 → runner 4.6 분 → 08:47 CDT `E1MS_DONE ok=3 fail=0`.
- 수용 ① `ACCEPT: OK -- D2SITEMS` (R5-genie 를 `raw_B16e4k` 와 대조); ② `192 chunks (want 192), 0 problems` (run|git 9a2c9fd4 · meta|ms_arm · arm 집합 · 모양 (40, 16)). compare 머리말: base `manifest-head:cd241b7e/chunks-sha:78cbb59fc01ce520` (§5 와 같음), `integrity: OK` (점, n = 2560, arm, raw 마다 깨끗한 커밋 하나, R5-genie KEYS4 동일). raise 된 블록 0 (compare 의 NOTE · WARNING 줄 0).
- 같은 시각의 다른 작업 (결과 무관): 08:46 CDT 부터 Codex 두 건 (V1LS §6 교차 검토 — CPU 66-67; E4 마무리 보고 — worktree `~/t2_wtCost`, CPU 1,97) 과 Fable 기록 감사 넷 (CPU 2–17, nice 10). 계산 명령은 이 실행의 CPU 밖 (Codex 66-67 · 1,97, Fable 2–17) 으로 묶도록 지시했다 — 에이전트 프로세스 자체는 묶지 않았다 (codex exec 의 affinity 0-191, verifier 확인). runner 를 띄우지 않았고, 시작 가드 (08:42 CDT) 뒤에 떴다. 08:46–08:47 CDT 에는 선언상 이 계정의 CPU 합이 96 + 20 스레드였다 (사용자 상한 168 안, 공통 규칙의 96 집합 밖).

### 6.2 판정 (§1.4 규칙 그대로, `compare_D2SITEMS.txt`)

| 비교 | 판정점 | 점별 a:b · p (−3 / 0 / +3 dB) | pooled (보고 전용) | POWERED (D) | 라벨 | SNR@0.1 격차 [90 %] |
|---|---|---|---|---|---|---|
| **주** `V1-ms → V1` (a = V1-ms 만 실패) | −3 · 0 · +3 (고정; 앵커 규칙 확인 줄도 같음) | 53:35 p .069 · 22:12 p .12 · 8:10 p .81 | 83:57 p .034 | True (88 · 34 · 18) | **(iii)** (second arm fewer 0/3, first arm fewer 0/3) | L = **+0.14 dB [+0.05, +0.22]**, censored 0 % |
| 보조 (보고 전용) `V4 → V1-ms` (a = V4 만 실패) | 같음 | 6:1 p .12 · 4:6 p .75 · 0:6 p .031 | 10:13 p .68 | True (7 · 10 · 6) | (iii) (second arm fewer 0/3, first arm fewer 1/3 — +3 dB) | +0.01 dB [−0.04, +0.04], censored 0 % |

실패 수 / 2560 (BLER@16; raise 된 블록 = 실패):

| SNR (dB) | V1 | V4 | V1-ms | genie |
|---|---|---|---|---|
| −3 | 371 | 394 | 389 | 87 |
| 0 | 88 | 96 | 98 | 26 |
| +3 | 29 | 21 | 27 | 12 |

V1 · V4 는 기록된 `raw_B16e4k` (§0.1 과 같은 수), V1-ms 는 `raw_D2SITEMS`; genie 는 두 raw 에서 비트 동일 (수용 ①).

### 6.3 등록 문장 (§2.1 · §2.2 의 틀 그대로)
- **주 비교 (iii)**: "판정하지 못함 (유의 방향 없음)". 개별 유의점 없음 (점별 p .069 · .12 · .81). "SNR 손실 L = SNR_ms(0.1) − SNR_V1(0.1) = +0.14 dB [90 % paired bootstrap +0.05, +0.22] (양수 = scalar 쪽 손실; 3 점 격자 −3 / 0 / +3 dB; censored replicates 0 %)". "V1-ms = V1 과 같은 가중치 · 배선 · 안정화 (Jacobian PSD 수리, precision floor λ_min, decoder damping, scalar feedback) 에서 EP site 의 공분산만 C₊ = νJ₊ → (tr C₊/N) I 로 바꾼 arm (설계 차이는 이것 하나); 첫 질의 뒤 두 arm 의 질의 궤적은 갈린다; full Jacobian 을 계산하므로 저비용 구현이 아니다". 범위: 이 셀 · 예산 · prior (Sparse specular 8×4, N′ = 1.6e5), 판정점 −3 / 0 / +3 dB, test 시행 0..2559.
- **보조 (§2.2)**: "보조 (보고 전용) `V4 → V1-ms`: (iii) '판정하지 못함 (유의 방향 없음)'; 점별 a:b · p −3 dB 6:1 p=0.12 · +0 dB 4:6 p=0.75 · +3 dB 0:6 p=0.031; SNR@0.1 격차 (V4 − V1-ms) +0.01 dB [90% paired bootstrap −0.04, +0.04; censored replicates 0%]. V4 와 V1-ms 는 Jacobian 수리 (V4 없음 · V1-ms 있음) 와 scalar site 를 만드는 경로가 함께 다르다 (§0.2)". (iii) 안의 개별 유의점: +3 dB 0:6 p .031 — V4 가 적게 실패.
- 원고용 영어 틀 (§2.4; 넣을지 · 어디에 넣을지는 사용자): (iii) `In paired sign tests, the comparison between the matrix-site receiver and its matched-scalar variant is not decided: neither receiver has p < 0.05 in its favor at two or more of the three tested SNRs.` · 공통 (kind ok) `Relative to the matrix-site receiver, the matched-scalar variant reaches BLER 0.1 at an SNR offset of +0.14\,dB [$+0.05$, $+0.22$] (positive: more SNR needed).`
- §2.3 의 쓰지 않는 문구는 쓰지 않는다. pooled 83:57 (p .034) 은 보고 전용이며 라벨 · 문장에 쓰지 않는다 (§1.4).

### 6.4 예측 채점 (§3)
1. 주 라벨 (iii) — **적중**.
2. −3 dB 에서 V1 쪽 유의 — 빗나감 (53:35, a > b 이지만 p .069 ≥ .05); 0 · +3 dB 유의 아님 — 맞음 (p .12 · .81); 혼합 결과 아님 (V1-ms 쪽 유의 점 0) — 맞음. → **빗나감** (부분 ✓ 병기).
3. POWERED True, 세 점 모두 D ≥ 6 (88 · 34 · 18) — **적중**.
4. L: kind ok, censored 0 %, 점추정 +0.14 ∈ [+0.04, +0.25] — **적중**.
5. L 구간 하한 +0.05 ≥ +0.01 — **적중**.
6. 보조 라벨 (iv) — 빗나감 ((iii): 점별 D 7 · 10 · 6 으로 세 점 모두 D ≥ 6 → POWERED; 등록이 적은 대안 (iii) 쪽); 점별 D ≤ 20 / 10 / 10 — 맞음 (7 · 10 · 6). → **빗나감** (부분 ✓ 병기).
7. |F_ms − F_V4| = 5 · 2 · 6 ≤ 20 / 10 / 10; F_ms(−3 dB) 389 > 371; F_ms(+3 dB) 27 < 29 — **적중**.
8. 앵커 규칙 확인 줄 두 블록 모두 `['-3', '+0', '+3']` — **적중**.
9. 수용 ① · ② OK, NOTE 줄 0 — **적중**.
10. runner 벽시계 4.6 분 ≤ 15 분 — **적중**.
11. (빗나갈 경로 — 해당 없음.)
→ 1–10 가운데 8 적중, 2 빗나감 (2 · 6, 둘 다 부분 ✓).

### 6.5 남은 일
기록 감사 (Fable, 1 회 — 사용자 승인 "다 진행하자"), Codex 교차 검토 (제안), 원고 · `docs/RESULTS.md` 반영은 사용자 요청 때. `e4-cost` 병합은 이제 가능하다 (E1+ 실행 끝, §5 병합 순서).

### 6.6 검토 (verifier, 보고 받음 2026-10-19 09:02 CDT; `scratchpad/verify_e1ms_s6/` 의 recompute · textcheck)
결함 0. 독립 재계산 (numpy, conf/code 미사용): 실패 수 표 · 점별 a:b · p · pooled · D · 라벨 (iii) · (iii) 일치; SNR@0.1 V1 −2.226 · V1-ms −2.090 · V4 −2.084 dB → L +0.137, 보조 +0.006; bootstrap (B 2000, seed 20260925) L [+0.050, +0.225] · 보조 [−0.037, +0.042], censored 0/2000; `e1ms_compare.py` 재실행 출력이 기록과 diff 없음. §6.3 문장은 §2.1 · §2.2 · §2.4 의 틀과 글자 단위로 같고 §2.3 금지 문구 0; 예측 채점 8/10 (2 · 6 빗나감, 대안을 적중으로 치지 않음). raw_D2SITEMS 192 청크 · 시행 0..2559 · run|git 9a2c9fd4 · meta 일치, genie 비트 동일, FREEZE 뒤 등록 문서는 §6 추가 (hunk 하나) 뿐. 선택 개선 1 반영: §6.1 의 CPU 문구 (위). 추가 확인 필요 1 (결과 무관): 같은 시각 에이전트들의 실제 CPU 사용은 지나간 일이라 확인 수단 없음.

### 6.7 기록 감사 (Fable 서브에이전트, 2026-10-19 09:08–09:22 CDT 보고; `prereg_audit_2026-10-19/audit_D2SITEMS.md`, 재계산 `recompute_e1ms.py` → `recompute_e1ms.out`, 도구 재실행 `rerun_E1MS_compare.txt` · `rerun_E1MS_compare_diff.txt` · `rerun_E1MS_accept.txt`; 기록 2026-10-19 09:25 CDT, Opus 5.5)

감사 대상 = HEAD 8b5322ca → e6619eb2 (대상 파일은 두 HEAD 에서 같음; 실행 커밋 9a2c9fd4, FREEZE e6ac9e65). 자동 비교 **162 / 162 일치** (numpy 직접, conf/code 미사용): 192 청크 계획 · meta 21 항목 · genie 1536 배열 비트 동일 · 실패 수 표 · a:b · exact p (scipy 와도 일치) · pooled · D · POWERED · 라벨 (iii) / (iii) · 앵커 확인 줄 · SNR@0.1 · L +0.137 · 보조 +0.006 · bootstrap 독립 구현 L [+0.050, +0.225] · 보조 [−0.037, +0.042] · censored 0 · 개발 스크린 §0.3 · 병합 확인 (a)(b) · 확인 3 raw · 자산 sha · s5 · base chunks-sha 78cbb59fc01ce520. `e1ms_compare.py` 재실행이 커밋본과 바이트 동일, `eval_accept.py` ACCEPT OK. 규칙 재적용 → §6.2 · §6.3 과 같음, 예측 8/10 (빗나감 2 · 6) 재현. 출처 · 무결성: run|git 9a2c9fd4 192/192, FREEZE 뒤 등록 문서 변경은 §6 추가뿐, 실행 창 (08:42–08:48 CDT) 안의 커밋은 실행 커밋뿐, 순서 (V1LS 기록 → 병합 → 병합 확인 → s5 · 실행 커밋 → 실행 → §6 → e4-cost 병합) 일관. test / 개발 분리: 10-19 11:00 KST 이후 쓰인 npz 23,001 개를 훑어 test 시행에서 실제로 돈 V1-ms 는 `raw_D2SITEMS` 뿐 (흐름 시험 · KAT 의 V1-ms 키는 raw_B16e4k 의 V1 배열을 이름만 바꾼 합성), 확인 3 · 병합 확인 (a) raw 의 arm 은 {V1, V4} 뿐.

**MUST 0 · SHOULD 0 · NIT 2 — 반영 (판정 · 수치 · 라벨 불변; §6.1 은 고치지 않고 여기에 정정)**: N1 DECISIONS 의 E1+ 동결 줄 "FREEZE = e1-ms e6ac9e65 (10-18 23:3x CDT …)" → 커밋 시각은 **10-18 23:29:10 CDT** (DECISIONS 에 정정 줄). N2 §6.1 의 "같은 시각의 다른 작업" 과 "선언상 CPU 합 96 + 20" 에 GPU 0 · 1 · 2 점유 더미 `gpu_hold.py` 셋 (CPU 0·96 / 22·118 / 23·119, nice 10; 5 s 마다 256×256 matmul — 부하는 무시할 만함) 이 빠졌다; 실행 내내 돌고 있었다. 감사가 확인하지 못한 것: 사용자 승인 원문 · 시각 (파일 간 인용 일치와 시각 일관성까지만), 같은 시각 Codex · Fable 프로세스의 실제 CPU 사용 (taskset 인자 · 시작 시각만), run_e1ms.sh 시작 전 전제 검사 (ABORT 없음 · 결과 raw 로 간접), §0.2 · §0.4 확인 1 · 2 (재실행 안 함).
