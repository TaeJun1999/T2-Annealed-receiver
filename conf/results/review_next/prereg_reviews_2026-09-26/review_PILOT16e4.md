# 적대적 검토 — NEXT_EXPERIMENTS_PILOT16e4.md v1 + code/run_pilot16e4.sh + code/pair_cross.py (2026-09-26 22:17 CDT = 2026-09-27 12:17 KST; Fable 5.1; HEAD fb768181; 설계·통계 + 실행 가능성·코드·사실)

읽기 전용 조사. BLER·수신기 실행 없음, `raw_PIL*` 생성 없음, 이 파일 외 수정 없음. 대조 원본: `raw_{B16e4k,NR16B16e4,D3B16e4,SVB16e4,U28B16e4,MXB16e4}` (analysis.load_raw 로 재계산), `ckpt/*.pt` (sha256sum), `results/gmm_fits_D2_PIL*` 링크, `results/tables_D2_*.txt` 표 B, `logs/run_D2_PIL{dev,chk}.log`, `code/{arms,runner,analysis,eval_accept,selftest_pilot,pair_cross}.py`, `code/run_pilot16e4.sh`, `Demo/t2_route_a.py`, `Demo/exp_0921_analysis.py`, `Demo/exp_0925_analysis.py`, `08_SPEC_analysis.md` §2, `01_RULES` :85, `STATUS.md` :668–671, DECISIONS 최근 항목.

## A. 반드시 (동결 전 고침)

1. **`runner.py analysis` 단계가 파일럿 raw 에서 반드시 죽고, 스크립트는 그 실패를 버린다.** 위치: `run_pilot16e4.sh:29`, 등록 §1 "실행" 행("→ `runner.py analysis` →"). 문제: 파일럿 태그 raw 에는 `_pool` 의 arm 이 R5-genie 뿐이라 `analysis.table_A` 의 SNR@0.1 블록(`analysis.py:314-321`)이 `gain(data, …, "R5-genie", REF="R2-ours-G")` 를 호출 → `KeyError 'R2-ours-G'` → `tables_D2_<TAG>.txt` 미생성. 스크립트 29행은 rc 를 기록하지도 중단하지도 않는다. 증거: raw_B16e4k 를 R5-genie + V1-pilot + bstar-pilot 만 남기고 `table_A` 호출 → `table_A raises: KeyError 'R2-ours-G'` (재현 명령: 이 검토의 조사 스크립트; 읽기 전용). 감사 시 "등록된 단계의 산출물이 없다" 가 된다. 고정안(최소): 29행과 §1 의 "→ `runner.py analysis`" 를 **삭제**(판정 분석은 `pair_cross.py` 이며 표 A/B/C 는 이 raw 에 정의되지 않는다). 대안: 유지하려면 `; log "analysis rc=$? (표 A 는 R2-ours-G 필요; 판정 입력 아님)"` 로 rc 를 남기고 §1 에 "실패 예상, 판정 무관" 을 명시.

2. **무결성이 깨져도 등록 라벨이 그대로 출력된다(사후 선택 통로).** 위치: `pair_cross.py:49-65` (bad 가 비어 있지 않아도 PAIRS 루프·라벨·격차를 전부 출력, 종료 코드만 71행에서 1), `run_pilot16e4.sh:31-34` (eval_accept rc 와 무관하게 pair_cross 실행). 문제: 등록 §1 은 "하나라도 실패하면 그 데이터셋은 **무효**(판정 없음)" 인데, 작성자는 무효 데이터셋의 P1/P2 라벨을 본 뒤에 "원인 기록·재실행 승인 요청" 여부를 정하게 된다. 고정안: (a) `pair_cross.py` 에서 무결성 출력 직후 `if bad: sys.exit(1)` (라벨 계산 전); (b) 스크립트에서 `RC=$?` 를 받아 eval_accept 실패 시 `log "$NAME INVALID (accept rc=$RC)"; continue` — pair_cross 를 돌리지 않는다(원인은 `<TAG>_accept.txt` 에 있다). 등록 §1 (b) 에 "무효 시 표 B 출력 없음" 한 줄.

3. **arm 이 예외를 던진 시행의 규칙이 없고, 현재 코드로는 한 시행만 던져도 데이터셋 전체가 무효가 된다 — 재실행은 결정적이라 같은 결과.** 위치: `runner.py:476-481` (예외 시 그 시행의 **전 반복**이 NaN 행 + `<arm>|failed`), `analysis.load_raw:174-182` (blk_err NaN → 1.0), `pair_cross.py:45-48` (@1 동일성 검사가 그 시행에서 실패). 문제: V1-pilot 이 반복 2..16 어디서든 한 번 raise 하면 @1 도 NaN 이 되어 "V1-pilot@1 = V1@1" 이 깨지고 등록 규칙상 데이터셋 무효 → 재실행해도 동일 → 결과 상실 또는 사후 규칙 수정. 6 base raw 의 루프 arm(V1·b\*·genie·R0)은 raise 0 건(확인)이므로 새 arm 쪽만 문제. 고정안(사전 명세, ~4 줄): `pair_cross` 의 @1 동일성 검사는 `p[k][new].get("failed")==1` 인 시행을 **제외**하고 그 수를 출력; 그 시행은 표 B 에서 블록 오류로 **유지**(08_SPEC §5); 등록 §1 (b) 에 "raise 시행: @1 검사 제외·개수 보고·블록 오류로 계산, 데이터셋 무효 아님; raise 비율은 −3 dB 행 옆에 보고" 를 적는다.

4. **"채널 추정 고정" 이 코드 주장일 뿐 데이터로 검사되지 않는다 — 3 줄이면 된다.** 위치: `pair_cross.py:41-48` 무결성 목록, 등록 §1 (b). 문제: 새 arm 의 정의(§1 첫 행)는 "채널 사후를 고정한 채 검출·복호만 16 반복" 인데 무결성 검사는 @1 동일성과 genie 동일성뿐이다. `RouteA.run` 은 반복마다 `nmse` 를 `hpost` 로 기록하므로(`Demo/t2_route_a.py:383`) 고정이면 `nmse[:, t]` 가 모든 t 에서 같아야 한다 — R0-pilot(같은 `mode="pilot_only"`)은 6 base raw 모두에서 그렇다(확인: "R0-pilot nmse constant over iters: True" ×6). 고정안: `pair_cross` 에 `for new in ("V1-pilot","bstar-pilot"): nmse[:,1:] == nmse[:,:1]` (NaN 은 nan_to_num) 를 무결성에 추가하고 §1 (b) 에 "nmse 반복 불변" 을 명시.

5. **부분 실행·중단 뒤 선택을 막는 문장이 없다.** 위치: 등록 §1 "실행" 행("인자로 부분집합 가능"), `run_pilot16e4.sh:20-23`. 문제: 데이터셋별로 결과를 본 뒤 나머지를 안 돌리거나 순서를 바꿀 수 있는 절차가 등록에 열려 있다. 고정안: §1 에 "6 개 **전부** 실행·보고한다. 인자 부분집합은 중단된 데이터셋의 **재개**에만 쓰며(runner 는 완료 청크를 건너뜀), 어떤 데이터셋도 결과를 본 뒤 제외하지 않는다. 6 개 pair 파일이 모두 있을 때만 §6 을 쓴다" 를 추가.

## B. 권고

6. **Demo/ 가 dirty 검사 밖.** `run_pilot16e4.sh:12` 는 `conf/code` 만 본다. 이 실험의 핵심 경로(`mode="pilot_only"`, `exact_prior`)는 `Demo/t2_route_a.py:331-336, 388-391` 에 있고 `common.py` 가 이를 import 한다. 지금은 clean(확인). 고정안: `git status --porcelain conf/code Demo`. (선례 스크립트도 같은 공백이라 권고.)

7. **`PILOT_EVAL_DONE` 이 전부 ABORT 여도 찍힌다.** `run_pilot16e4.sh:22`(파이프 → 서브셸이라 카운터 전달 불가) :37. 고정안: `done < <(echo "$DS")` 로 바꾸고 OK/FAIL 카운터 → `log "PILOT_EVAL_DONE ok=$OK fail=$FAIL"`, `exit $FAIL`. 또 인자의 오타(예: `D2c2`)는 아무것도 안 돌리고 DONE 을 찍는다 → WANT 의 각 이름이 DS 에 있는지 먼저 검사.

8. **`pair_cross.py` 자체 검사 보강(각 1–2 줄).** (a) `keys` 를 prior 로도 거른다(38행; 지금은 cell 만) 와 `len(keys) == len(C.CELLS[cell]["snrs"])` 및 base 의 같은 (cell, prior) 점 집합과 동일 assert — eval_accept 가 같은 것을 보지만 pair_cross 단독 실행(감사 재현)에서도 닫히게; (b) `load_raw` 의 세 번째 반환값 `warns` 를 두 raw 모두 출력(청크 구멍·NaN 채움을 버리지 않기); (c) 머리말에 n(점당 시행 수)·git HEAD·두 raw 경로를 찍는다.

9. **P1 의 교란 요인을 등록 문장으로 미리 닫아라.** 루프 V1 은 Module H 를 16 번, V1-pilot 은 1 번 적용한다. 따라서 P1 (i) 는 "데이터 보조 재추정의 몫" 과 "같은 파일럿 우도 위에서 prior 를 반복 적용한 몫(EP 정련)" 을 가르지 못한다. 적대적 리뷰어의 첫 질문이다. 최소 고정안(코드 변경 없음): §머리말·§2 의 문장을 "**한 번** 쓰는 파일럿 전용 설정보다 루프가 …" 로 못박고, "파일럿 전용 EP 를 수렴까지 돌린 arm 은 이 등록에 없다(한계)" 를 §2 에 적는다. 선택지(코드 커밋 필요, 지금은 권고만): `PilotSitePrior(n_inner=K)` 보고 전용 arm — 동결 전 새 커밋·selftest 가 필요하므로 이번 등록에 넣지 않는 편이 낫다.

10. **채널 추정 지표(NMSE) 보고 전용 행.** Koller / Arvinte–Tamir 형 비교의 자연 지표는 NMSE 인데 등록은 BLER 만 다룬다. V1-pilot·bstar-pilot·R0-pilot 의 NMSE 는 @1 = 루프 arm @1 이라 이미 관측된 값이다(예: B16e4k −3 dB 중앙값 V1 5.47e-02, b\* 9.79e-02, R0 3.18e-01; `tables_D2_B16e4k.txt:61,69,71`). 고정안: `pair_cross` 가 SNR 별 nmse@16 중앙값(= @1, 항목 4 로 보장)을 세 arm 에 대해 보고 전용으로 출력하고 §1 "보고 전용" 에 한 줄 추가. 판정 아님.

11. **다중성 문장의 배치 수준 공개.** §1 "판정 층위" 는 등록 안의 보정만 말한다. SEEDS 선례처럼 "등록 사이 보정 없음(서로 다른 가설); 이 등록의 1차 검정 2 개(P1·P2 @ D2 C2), 측정 라벨 10 개, 보고 전용 pair 12 개; 1차 검정 수는 원고에 공개" 를 한 줄로.

12. **예측의 채점 규칙 세부.** 예측 2 "모두 (i) → 6 중 6" 은 한 항목인지 다섯 항목인지 명시(제안: 한 항목, 5/5 만 적중). 예측 6 은 표의 3 자리 값으로 판정(SEEDS §3-2 선례; 0.145 = 371/2560, 0.574 = 1469/2560 확인). 예측 4 의 "@1 차이가 1.5–2.5%" 는 SV8e 1.48%(38/2560), UMi28 0.78%(20/2560), MIX3 1.13%(29/2560) 로 범위가 틀리다 → "0.8–1.5%" 로 정정(예측 방향은 그대로).

13. **시각·상태 문구.** 머리말 "2026-09-26 밤, 응답 시각 미기록" → 상한을 적을 수 있다: 구현 커밋 2b27ef6a 가 11:55:41 KST = 21:55 CDT 이므로 "21:55 CDT 이전(구현 커밋), 응답 시각 미기록". §4 "fits 링크 6 개 | 동결 커밋에 포함(링크는 results/ 아래, 미커밋)" 은 자기모순 → "동결 시점에 존재(11:58 KST 생성; 링크는 커밋 대상 아님, 선례 동일)". §0 C6 행 "(i)" → "(i) 3/3" (142:11·45:4·26:3, `tables_D2_NR16B16e4.txt:370`). 헤더 "적대적 검토는 Fable 5.1 로 1건" 은 그대로.

14. **§1a 의 D2C2 가중치 근거를 한 줄 보강.** raw_B16e4k 에는 `stagec_ckpt_id` 가 없어 sha 는 기록(STATUS.md:668–671)에서 온다고 썼는데, 더 강한 근거가 이미 있다: PILchk(2b27ef6a; 현재 코드 + 이 파일이 raw_B16e4k 의 14 arm 을 비트 재현) 와 PARB16e4chk. "파일 sha 4443921ce8d5c4a1 = raw_B16e4k 를 재현하는 파일(PILchk)" 로 적으면 audit 이 닫힌다. 참고: `stagec_id_str` 은 이 파일에 `role=legacy-last … | BEST_WEIGHTS_UNAVAILABLE …` 를 붙이며 eval_accept 는 부분 문자열 검사라 통과한다(확인).

15. **표현 정정.** §1 "V1-pilot 의 디노이저 호출은 시행당 1 회" → `PilotSitePrior.ep_site` 는 `denoise` + `denoise_full`(야코비안) 를 한 번씩 부른다(`arms.py:170-171`) → "Module H 1 회(디노이저 + 야코비안 각 1 회)". §머리말 "반복 1 출력은 … 비트 동일하다(구성상)" 옆에 "개발 확인은 D2 C2 −3 dB 1 청크(S2)뿐; C6(Nr=16)·S2c·SV8e·UMi28·MIX3 는 테스트 무결성 검사에서 처음 확인" 을 병기.

16. **스크립트 산출물 명시·manifest.** 등록 §1 에 `results/review_next/pair_<TAG>.txt` 와 `logs/run_D2_<TAG>.log` 를 적을 것. `run_seeds16e4.sh` 처럼 `code/run_manifest.py --tag $TAG >> $L` 를 넣으면 git·ckpt id·fits 해시가 json 으로 남는다(raw 만 있으면 동작, `run_manifest.py:40-42`).

## C. 메모 (대조 결과; 고칠 것 없음)

17. **§0 전수 일치**(raw 재계산, −3 dB 실패 수/2560): D2C2 1469/371/1848/623/1918/1220/87 · C6 464/53/842/184/1005/376/22 · D3 1972/1000/2135/1298/2164/1738/485 · SV8e 1489/402/1527/464/1616/1010/31 · UMi28 2099/1228/2119/1270/2152/1781/594 · MIX3 2180/1354/2209/1421/2264/1896/679. `R0-pilot@1 == R2-ours-G@1`(blk_err 배열 동일) 6/6. 예측 1 근거 R2 1918→839 (R0 1918→1220 보다 큰 감소) 확인. 루프 표 B `b* → V1`: (i) 3/3 · (i) 3/3 · (i) 3/3 · (iv, 판정점 2) · (i) 3/3 · (i) 3/3 = §0 열.
18. **§1a 전수 일치**: sha256[:16] 6 개 = `sha256sum`; base raw `meta|stagec_ckpt_id` role=best ×5(a1.pt 는 키 없음, `stagec_id_str` = legacy-last); `meta|bstar / kron_K / ll_val|<b*>` = 문서 = 스크립트 DS 표(SV8e 는 gmm256, `ll_val|gmm256` 키 존재; meta kron_K 2048 은 `--bstar gmm256` 에서 검사 안 함 — 의도대로). 링크 6 개 존재(09-27 11:58 KST). `raw_PIL*` 없음, `tables_D2_PIL*` 없음, `run_D2_PILdev.log` 의 BLER16 필드는 빈 문자열(파일럿 arm 은 show 목록 밖) → "@16 을 보지 않았다" 와 부합.
19. **스크립트 대조**: `bash -n` OK; `export CUDA_VISIBLE_DEVICES=` 가 모든 자식에 적용; ckpt sha 검사·링크 검사 있음; `runner.py run` 인자 = §1 원문(`--pilot-arms` 는 `--stagec-ckpt` 필수, `--arm` 은 `--tag` 필수 — 충족; C6 은 16x4 ckpt 와 배열 일치); `run || { …; continue; }` 의 rc 는 리다이렉션 뒤에도 python 의 것; `log "… rc=$? ($(head …))"` 는 `$?` 가 먼저 확장됨(테스트: `false; echo "rc=$? ($(true))"` → rc=1). eval_accept: C6 은 `:C6` 으로 `C.CELLS["C6"]["snrs"]` 7 점 기대, SV8e 는 `--kron-K` 없이 `--bstar gmm256`(허용 경로 `eval_accept.py:63-64`), D2C2 는 `legacy-last` 부분 문자열 통과. conf/code 는 지금 `?? pair_cross.py`, `?? run_pilot16e4.sh` 라 동결 커밋 전에는 스크립트가 스스로 중단한다(의도대로).
20. **`pair_cross.py` 규칙 대조**: 앵커 = 첫째 arm(`decision_points(…, x)`), 라벨 (i)=`wy>=2`(a>b: 첫째만 실패 > 둘째만 실패 → 둘째 적게 실패), (ii)=`wx>=2`, POWERED = `len(cand)==3 and ≥2 점에서 a+b≥MIN_DISC(6)` — `analysis.table_B:437-439` 와 동일; 격차 부호 "첫째 − 둘째" = `gain(x, y)` = 표 B 관례; NaN 은 양쪽 `nan_to_num(1e300)` 으로 NaN==NaN; 배열 모양 불일치는 `array_equal` 이 False(예외 없음); 종료 코드 1/0. `PilotSitePrior.ep_site` 와 `RouteA.run` 반복 0(scal='belief', n_inner=1, hE=0, nuE=cbar, 데이터 열 xbar=0 → A·B 기여 0, LOO 캐비티 = 사후) 의 대응은 코드상 일치하고 PILdev 비트 동일이 뒷받침한다. 08_SPEC §2 "앵커는 기준선 측" — V1-pilot 은 P1 의 기준 설정이지 주장 arm 이 아니므로 규칙에 맞다(§1 문장으로 충분).
21. **범위 문장**: 재현 아님·"형 설정" 표기·헤드라인 불변·UNGATED 측정 라벨 구분·무효 규칙·빗나갈 경로 — 모두 있음. 금지어(유의하다/낫다 판정문) 0 건. 비용 추정은 PILdev(1 워커, 빌드 포함 76 s/청크 −3 dB) 로 보아 그럴듯함(검증 대상 아님).

## 사용자 결정 범위 밖
없음. 1–5 는 스크립트·분석 코드의 결함 수정과 등록 문구의 사전 명세이고(등록자 판단), 9 의 선택지(새 arm)는 이번 등록에 넣지 않기를 권고하므로 결정 요청이 아니다.
