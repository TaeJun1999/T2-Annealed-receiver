# 기록 감사 — STATIC16e4 (정적 6 데이터셋 V1 대 등록 baseline 13 개; 기존 raw 위 규칙 고정 사후 계산)  (Fable 5.1, 독립 기록 감사; 2026-09-30 07:54 KST = 09-29 17:54 CDT; main HEAD 4ec78c13)

대상: `NEXT_EXPERIMENTS_STATIC16e4.md` §6.1 (동결 2139f082 의 §0~§5 위에 faebac20 이 추가), `docs/EXPERIMENTS.md` 55 행 (STATIC16e4), `conf/DECISIONS.md` 297 행 (STATIC16e4 결과 기록, 07:39 KST). 출력 원본 `results/review_next/pairB_ST{B16e4k,NR16B16e4,D3B16e4,SVB16e4,U28B16e4,MXB16e4}.txt`.
대조 원본: `prereg_audit_2026-09-29/recompute_static.py` → `recompute_static.out`. 읽은 것: raw npz 청크 18 디렉터리 (`raw_<TAG>` 14 arm · `raw_PIL<suf>` · `raw_ALD<suf>`, 448 청크씩), `results/review_next/run_manifest_<tag>.json` 18 개, `results/ald/{ald,pilots}_PIL<suf>.*`, base V1 체크포인트 파일 (sha), `results/tables_D2_<TAG>.txt` (§0 의 b\*·R2 인용 원본), `logs/run_static16e4.log`, git. `pair_baselines.py`·`analysis.py` 는 호출하지 않았고, `pairB_ST<TAG>.txt` 는 **내 재계산과 대조하기 위해서만** 파싱했다 (판정에 쓰지 않음). **재사용한 함수** (전부 `prereg_audit_2026-09-28/recompute.py` 의 자체 구현; 그때 `analysis.load_raw` 와 전 필드 비트 동일·리더 없는 손 계산으로 검증됨): `Raw`, `fails` (blk_err@16, NaN → 1), `raised`, `table_b`/`dpoints`/`sign_p` (08_SPEC §2 표 B: 앵커 X 의 BLER ∈ [0.005, 0.9] 중 |log10(BLER/0.1)| 최소 3 점, 정확 양측 이항, POWERED = 3 점·불일치 ≥ 6 이 ≥ 2 점, (i)/(ii)/(iii)/(iv)), `recovery` (R_X = (F_X − F_V1)/(F_X − F_genie), paired bootstrap B = 2000, `default_rng(20260926)`, 복제마다 시행 인덱스 1 회 추출을 세 arm 에 공통 적용), `merged`, `same`, `git`, `sha16`. R0-pilot@1 은 궤적을 반복 1 에서 자른 것 (`blk_err[:, :1]`). **`--provenance manifest` 검사 5 가지와 `chunks-sha` 는 이 파일에서 §1 본문대로 다시 구현**했다 (manifest git-tracked·clean, n_raw_files = 청크 수, manifest 점 목록 = raw 점 집합, 모든 청크 mtime ≤ manifest `written` (KST 명시), git-tracked raw 디렉터리 clean; digest = 정렬된 청크별 sha256 hex 를 이어붙인 문자열의 sha256[:16]). 문서는 고치지 않았다 (감사 폴더 밖 변경 없음, 커밋 없음, GPU 없음, OMP 4 스레드).

## 총평
**전부 재현.** §6.1 의 수치·라벨·문장·채점, EXPERIMENTS 55 행, DECISIONS 297 행에서 **수치·라벨 오류 0 건**. 정정 필요 0 건, 선택 메모 5 건 (아래). 규칙 위반으로 볼 것은 없다. 동결 뒤 §0~§5 불변 (append-only), 실행 코드 = 동결 커밋 2139f082, 출처 (manifest 5 검사·chunks-sha 18 개) 전부 독립 재현.

## 재계산·대조 요약 (전부 recompute_static.out)
- **무결성 6/6 OK** (자체 검사, 데이터셋마다 raw 3 개): 격자 7 점·구멍/NaN 없음, 세 raw 모두 `run|git` 키 없음 (→ manifest 출처 경로가 맞음), `meta|rotation`·`meta|doppler` 없음(정적) 세 raw 동일, base 14 arm 집합 정확, PIL = {V1-pilot, bstar-pilot} + genie, ALD = {ALD-pilot, ALDv-pilot} + genie, genie 4 키 PIL/ALD = base (7 SNR 비트 동일), n = 2560, PIL/ALD raised 0, V1-pilot@1 = V1@1·bstar-pilot@1 = b\*@1, ALD 추정 고정·사전 계산값 (rtol 1e-9)·ckpt sha = base V1 ckpt (B16e4k 는 `meta|stagec_ckpt_id` 없음 → manifest "(none)" → `meta|stagec_ckpt` 파일 `d2sx_N160000_a1.pt` sha256[:16] = **4443921ce8d5c4a1** = ALD 추정 `prov.ckpt_sha` = `ckpt_sha`; 나머지 5 는 meta = manifest = ALD 추정 id).
- **출처 (`--provenance manifest`) 18/18 raw 통과**: manifest 18 개 git-tracked·clean; n_raw_files 448 = 청크 448; 점 목록 7 = raw 점 집합; 청크 mtime ≤ `written` (여유: B16e4k 597 분, NR16B16e4 251, D3B16e4 36, SVB16e4 25, U28B16e4 61, MXB16e4 75; PIL·ALD 12 개는 0~6 분); tracked raw 는 `raw_B16e4k` 하나 (448 파일) clean. **`manifest-head` 18 개·`chunks-sha` 18 개 = 6 파일 머리말 = §6.1 머리말 출처 6 줄, 전부 동일** (§6 6/6).
- **표 B 13 × 6 = 78 라벨**: 판정점·점별 a:b·pooled·POWERED·라벨·k/3·절대 격차·R_X 1차 (또는 정의하지 않음) 가 6 개 `pairB_ST` 파일과 **78/78 동일**, X\*·R_{X\*}·SUMMARY-B·문장 조건 줄·실패 수 표 19 행 × 7 SNR 도 6/6 동일 (§2 "pairB_ST files matching 6/6").
- **§6.1 데이터셋별 표 6 행 × 5 칸**: 원 b\*·k𝔅·m𝔅·판정 못함·(i) 아닌 X 목록·X\*(F)·R_{X\*} CI·문장 조건 — **6/6 동일** (77~82 행). **D2 C2 X 표 13 행 × 3 칸 13/13 동일** (88~100 행).
- **§0 (이미 알려진 라벨) 6/6 일치**: b\* 6 (SV8e (iv), 나머지 (i)) = `tables_D2_<TAG>.txt` 표 B (판정점·pooled·판정) = 재계산; R2 6 (전부 (i), pooled 778:69 / 396:10 / 705:50 / 302:59 / 409:41 / 387:30) = tables_D2 = 재계산; P1 (V1-pilot) = PILOT16e4 §6.1 (C6·SV8e (iv), 나머지 (i)); A1·A2 = ALD16e4 §6.1 (12 개 전부 (i)); X\* 와 F(X\*) (623 / V1-pilot 83 / 1298 / 464 / 1270 / 1421; 차점 V1-pilot 626 · b\* 184) 와 R_{b\*} 5 개 (0.470 [0.427, 0.512] · 0.367 [0.335, 0.399] · 0.143 [0.095, 0.188] · 0.062 [0.033, 0.089] · 0.090 [0.062, 0.117]) 전부 재계산과 같음. → `--expect` 통과 (rc = 0 × 6) 와 일치; 코드 드리프트 0.
- **집계**: 새 48 라벨 (i) 46 · (iv) 2 (SV8e b\*-scalar·gmm32; 판정점 −3/+0 두 개 — b\* 와 같은 이유) · (ii) 0 ✓; 72 라벨 (ii) 0 ✓ ((i) 68, (iv) 4); k𝔅 = 12 4/6 (B16e4k·D3·U28·MX), C6 11 (V1-pilot (iv)), SV8e 9 ✓; "전부" 문장 충족 4/6 = 가능 4 곳 전부 ✓; genie ≥ V1 가드 발동 0; 주 라벨 D2 C2 k𝔅 12·m𝔅 0 → (A), 원 b\* (i), R_{X\*} 하한 0.427 > 0 → 문장 충족 ✓; C6 R_{V1-pilot} (−3 dB) 0.492 [0.355, 0.630] (F 83 / V1 53 / genie 22) ✓ — 다른 등록 문서에 없는 새 값임을 grep 으로 확인.
- **§3 채점**: 1 ✓ 2 ✓ 3 ✓ 4 ✓ 5 ✓ (k𝔅 = 11) 6a ✓ 6b ✓ 7 ✓ → **적중 8 / 빗나감 0**; 항목 8 (무효·드리프트) 0/0 = §6.1·EXPERIMENTS·DECISIONS 와 같다.
- **git·로그 (§G)**: HEAD 4ec78c13, `conf/code`·`Demo`·세 기록 파일 작업 트리 깨끗. 동결 2139f082 (09-30 07:31:38 KST = 09-29 17:31 CDT) → HEAD 의 문서 diff 는 hunk 1 개 `@@ -63,3 +63,69 @@`, '−' 줄 0 → **§0~§5 불변** (동결본 65 줄, `## 6.` @65; §6.1 은 67 행부터). `diff 2139f082..HEAD -- conf/code Demo` 비어 있음 → 실행 코드 = 동결 코드 ✓ (`run_static16e4.sh` 도 동일). 6 파일 머리말 `# run_static16e4 git 2139f082` ✓. 로그: start 17:31 CDT (git 2139f082) → 6 데이터셋 rc = 0 (17:32~17:33) → `STATIC_DONE ok=6 fail=0` ✓; pairB_ST 6 개 mtime 17:32~17:33 CDT ✓. faebac20 (07:39:11 KST = 17:39 CDT) = §6.1 64 줄 + pairB_ST 6 + EXPERIMENTS 1 행 + DECISIONS 2 줄 ✓. 그 뒤 89c46b37 (WORK_QUEUE) 과 4ec78c13 (07:48 KST; 사용자 결정 "규칙 고정 사후 계산", 등록 문서 §6 끝에 1 줄 추가 + DECISIONS 1 줄) — 둘 다 추가만.
- 금지어 (여지·headroom·bound·최적·비긴다·강건·도달)·자리표시 ("x CDT"/"x KST") §6.1·EXPERIMENTS 55 행·DECISIONS 297 행에 없음 ✓. 시각 환산 (07:31~07:33 KST = 17:31~17:33 CDT; 기록 07:36/07:39 KST = 17:36/17:39 CDT) ✓.

## 수치·라벨 오류
- 없음.

## 규칙 적용 재검 (§1·§2 를 재계산값에 다시 적용)
- 판정점 = 앵커 X 기준 자동 (예: D2 C2 R0-pilot@1 +3/+6/+9, R3 +3/+12/+15, R4-llr +9/+12/+15; MIX3 R2 +6/+9/+12) ✓; R0-pilot 판독 @1 ✓; (iv) 는 k 에 세지 않음 ✓ (SV8e 9, C6 11).
- X\* = 𝔅 ∪ {b\*} 중 −3 dB 실패 최소 (동률 이름순) ✓ — 6 데이터셋 모두 동률 없음 (차점 F 는 recompute_static.out §2 각 줄). SV8e 는 b\* 가 (iv) 여도 X\* 규칙은 실패 수만 보므로 X\* = b\* (464) ✓ (§0 과 같음).
- R_X 1차: 포화 가드 (−3 dB BLER ∈ [0.005, 0.9], F_X > F_genie) + genie ≥ V1 가드 ✓; R_{X\*} 6 개 모두 정의됨.
- "전부" 문장 = **원 b\* (i)** ∧ k𝔅 = 12 ∧ m𝔅 = 0 ∧ R_{X\*} 하한 > 0 → 4 데이터셋 ✓; 불충족 2 곳 (C6: V1-pilot (iv); SV8e: 원 b\* (iv) + 3 (iv)) 은 §0 이 미리 적은 "불가" 2 곳과 같다 ✓. 주 라벨 문장·범위 한정 ("이 셀·예산·prior 한정; 이미 본 곡선 위의 규칙 고정 사후 계산") = §1·§2 등록 문구 ✓.
- 다중성: 보정 없음, 개수 서술만 ✓; 새 48 라벨 밖의 개별 (i) 을 독립 주장으로 쓰지 않음 ✓.

## 규칙 위반으로 볼 만한 것
- 없음. 새 BLER 없음 (18 raw 의 청크 mtime 전부 09-22~09-28, 동결 09-30 07:31 KST 이전; 실행은 CPU 사후 계산 2 분); §0~§5 동결 뒤 불변; 실행 코드 = 동결 커밋; 전제 검사 (conf/code·Demo clean, 등록·DECISIONS tracked+clean, 기존 pairB_ST 없음) 는 스크립트가 실행 전에 강제하고 로그 start 줄이 남아 있음; `--expect` 다섯 라벨 (b\*, V1-pilot, ALD-pilot, ALDv-pilot, R2) 은 §0 에 미리 적힌 값 그대로 스크립트 heredoc 에 있고 6/6 통과; 문장·라벨·채점 전부 등록 규칙 그대로; "전사만".

## 메모 (선택; 수치·라벨 변경 없음)
1. [§0 21 행, 동결 본문] "공개 −3 dB 실패 수 — ALD16e4 §6.1, TABLE A" — `NEXT_EXPERIMENTS_ALD16e4.md` 에 "TABLE A" 라는 이름의 표는 없다. 해당 수치 (623 · 626 · 83 · 184 · 1298 · 464 · 1270 · 1421) 는 ALD16e4 §6.1 의 산문 줄 **112 행** ("−3 dB BLER@16 실패 수 / 2560 (R0-pilot · bstar-pilot · … · genie)") 에 있고 값은 전부 일치한다. 동결 본문이므로 고치지 않는다; 인용 시 "ALD16e4 §6.1 −3 dB 실패 수 줄 (112 행)" 로 읽으면 된다.
2. [§6.1 131 행, 4ec78c13 추가] 원고 명칭 결정 줄이 "6.1 결과 (… 전사만)" 절 끝에 글머리표로 붙어 있다 — 결과 전사가 아니라 사용자 결정 전사다. 추가만이라 규칙 위반은 아니나, 뒤에 §6.2 (기록 감사) 를 붙일 때 이 줄이 §6.1 소속으로 남는다. 선택: 그대로 두거나 §6.2 앞에 "### 6.1a 사용자 결정" 소제목만 덧붙이기.
3. [보고 전용] R_X 1차가 포화 가드로 "정의하지 않음" 인 (데이터셋, X) 는 D3·UMi28·MIX3 의 R4-llr 셋 (−3 dB BLER 0.905 / 0.912 / 0.924 > 0.9) 뿐 — §6.1 은 인용하지 않으므로 영향 없음 (정의된 1차 R_X 75/78).
4. [pairB_ST 문장 줄] 파일의 "'등록된 baseline 전부와 멀어진다' condition (k = 13 …)" 은 **재계산된** b\* 라벨 (k = 13) 로 판정하고, §1·§6.1 의 문장 조건은 **원 b\* 라벨** 로 판정한다. 드리프트 0 이라 이번엔 같은 결과 (MET 4 / NOT met 2) 이지만 정의가 다른 두 줄임을 적어 둔다 (`--expect-bstar` 가 rc = 1 을 내므로 실제로 갈릴 일은 없다).
5. [B16e4k manifest] `written` 09-23 07:36 KST 가 마지막 청크 (09-22 21:39 KST) 보다 10 시간 뒤다 — 다른 17 개 (0~251 분) 와 달리 사후 작성이며 `git_commit` cd241b7e 도 실행 커밋 (98e22f8, §1) 이 아니다. §1 이 "manifest-head = 매니페스트 작성 시점 HEAD" 라고 미리 적었고 raw_B16e4k 는 git-tracked (448 파일 clean) 이라 청크 자체가 고정돼 있으므로 문제 없음; chunks-sha 78cbb59fc01ce520 이 이후 감사의 고정점이다.

## 일치 확인한 항목 (전수)
- §6.1 실행 문단: 동결 2139f082 · 17:31~17:33 CDT · git 2139f082 · 전제 검사 통과 · `STATIC_DONE ok=6 fail=0` · 무결성 6/6 · `--expect` 6/6 · 새 BLER 없음 ✓.
- 주 라벨 문단 (k𝔅 12·m𝔅 0 → (A), 원 b\* (i), 하한 0.427, 문장) ✓; 데이터셋별 표 6 행 ✓; D2 C2 X 표 13 행 ✓; 머리말 출처 6 줄 (manifest-head 18 · chunks-sha 18) ✓; 집계 문단 4 항목 ✓; §3 채점 표 9 행·합계 ✓; 보고 전용 문단 (파일 6 개 존재, C6 R_{V1-pilot} 새 값) ✓.
- EXPERIMENTS 55 행: 시각 (KST/CDT)·스크립트·동결 해시·명령 구성 (`--provenance manifest --r0 at1 --expect …`)·"새 BLER 없음"·seed·시행 0..2559·git 2139f082·GPU 없음·핵심 지표 6 항목·로그 경로·채점 8/8·"곡선·표를 먼저 봤음 (공개)" ✓.
- DECISIONS 297 행: 시각·실행 요약·주 라벨·문장 충족·k𝔅 목록 (C6 11 V1-pilot (iv); SV8e 9 b\*-scalar·gmm32·V1-pilot (iv))·(ii) 0·8/8·"전사만"·"다음: Fable 기록 감사" ✓. (295 행 동결 줄의 시각 07:31 KST = 커밋 2139f082 07:31:38 KST ✓.)
