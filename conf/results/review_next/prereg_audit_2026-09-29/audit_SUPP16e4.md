# 기록 감사 — SUPP16e4 (DOP16e4·ROT16e4 보충: 24 조건 × 등록 baseline 전부)  (Fable 5.1, 독립 기록 감사; 2026-09-29 14:51 KST = 09-29 00:51 CDT; main HEAD 64f422c3)

대상: `NEXT_EXPERIMENTS_SUPP16e4.md` §6.1 (+ §5 ALD 조정 표 24 행), `docs/EXPERIMENTS.md` 54 행(SUPP16e4), `conf/DECISIONS.md` 291 행(SUPP16e4 결과 기록, 커밋 6730bc1d).
대조 원본: `prereg_audit_2026-09-29/recompute.py` → `recompute.out`. raw npz 청크(원 `raw_<T>` 24 + 새 `raw_X{L,P,A}<T>` 72 = 96 디렉터리, 448 청크씩) · `results/ald/{tune,ald,pilots}_XA<T>.*` · `logs/run_supp16e4.log` · git · `/proc` 만 읽었다. `pair_baselines.py`·`analysis.py`·`eval_accept.py` 는 호출하지 않았고 `pairB_X<T>.txt`·`X<T>_accept.txt` 의 수치는 판정에 쓰지 않았다(accept 파일은 "ACCEPT: OK" 문자열 개수만 셌다). **재사용한 함수**(전부 앞선 감사 `prereg_audit_2026-09-28/recompute.py` 의 자체 구현, 그때 `analysis.load_raw` 와 전 필드 비트 동일·리더 없는 손 계산으로 검증됨): `Raw`(청크 리더), `fails`(blk_err@16, NaN → 1), `raised`, `dpoints`/`table_b`/`sign_p`(08_SPEC §2 표 B: 앵커 X 의 BLER ∈ [0.005, 0.9] 중 |log10(BLER/0.1)| 최소 3 점, 정확 양측 이항, POWERED = 3 점·불일치 ≥ 6 이 ≥ 2 점, (i) V1 적음 ≥ 2 점 p < .05 / (ii) X 적음 / (iii) / (iv)), `recovery`(R_X = (F_X − F_V1)/(F_X − F_genie), paired bootstrap B = 2000, `default_rng(20260926)`, 복제마다 시행 인덱스 1 회 추출을 세 arm 에 공통 적용 — `recovery_ci.boot` 와 같은 추출 순서), `merged`, `same`, `git`, `sha16`. R0-pilot@1 은 `analysis.load_raw` 별칭 정의대로 궤적을 반복 1 에서 자른 것(`blk_err[:, :1]`)으로 직접 만들었다. 문서는 고치지 않았다(감사 폴더 밖 변경 없음, 커밋 없음, GPU 없음).

## 총평
**전부 재현.** §6.1 의 수치·라벨·문장·채점, EXPERIMENTS 54 행, DECISIONS 291 행에서 **수치·라벨 오류 0 건**. 정정 필요 0 건, 선택 메모 5 건(아래). 규칙 위반으로 볼 것은 없다.

## 재계산·대조 요약 (전부 recompute.out)
- **무결성 24/24 OK** (자체 검사: 격자 7 점·구멍/NaN 없음, raw 마다 단일 깨끗한 `run|git` — 원 DOP 063f3bcb / ROT a4cbd184, 새 XL·XP·XA 72 개 전부 e7c9f4a7, `meta|doppler`·`meta|rotation` 네 raw 동일 (ν = 0.005/0.01, δ = 15/30), meta 지문(ntrain·bstar·kron_K·em_sec·ll_val|kron·stagec_ckpt_id) 네 raw 동일, arm 집합 기대대로·겹침 없음, genie 4 키 XL/XP/XA = 원 raw (7 SNR 전부 비트 동일), n = 2560, PIL/ALD raised 0, V1-pilot@1 = V1@1·bstar-pilot@1 = b\*@1, ALD 추정 고정·사전 계산값(rtol 1e-9)·ckpt sha = 원 raw ckpt·조건(ν/δ) = 원 raw). 새 청크 32,256 개 zip 검사 이상 0 ("잘린 npz 0" ✓). run_manifest 72 개 = e7c9f4a7 / 448 파일. accept 24 개 "ACCEPT: OK" 24, FAILED 0. b\* 라벨 재계산 = §0 24/24 (드리프트 0).
- **D2 C2 X 표 (13 × 4 = 52 칸)**: 판정점·pooled a:b·라벨·k/3·절대 격차·R_X CI 가 **52/52 동일**(소수점 자리까지; 같은 시드·같은 추출 순서이므로 재현).
- **24 조건 표 (24 행 × 7 칸)**: 원 b\*·k𝔅·m𝔅·판정 못함·(i) 아닌 X 목록·X\*(F)·R_{X\*} CI(또는 가드 "정의하지 않음"+절대 격차)·문장 조건·−3 dB genie·V1 — **24/24 동일**.
- **집계**: (ii) 0/288 ✓; k𝔅 = 12 21/24 (D2 C2 4 + 나머지 17) ✓; k𝔅 < 12 = DOPbNR16 11 (V1-pilot (iii)), ROTaNR16 11 (V1-pilot (iii)), ROTaSV 8 (b\*-scalar·gmm32·V1-pilot·ALDv-pilot (iv)) ✓; "전부" 문장 18/24 ✓, 가능 19 중 불충족 ROTaNR16 하나 ✓, 불가 5 = DOPbB16e4k·DOPbNR16·DOPbU28·DOPaSV·ROTaSV ✓; arm 별 (i) 수(8 arm 24, scalar·gmm32·ALDv 23 + ROTaSV (iv), V1-pilot 21/2 (iii)/1 (iv), b\* 19/3/2) ✓; X\* = b\* 21 · V1-pilot 3 (DOPaNR16·ROTaNR16·ROTbNR16) ✓; genie ≥ V1 가드 DOPbB16e4k (846 ≥ 756)·DOPbNR16 (415 ≥ 179) ✓; DOPbD3 1418·1406 (격차 12), R_{X\*} 0.955 [0.826, 1.107], X\* 절대 격차 253 ✓.
- **§3 채점**: 1a ✓ 1b ✓ 1c ✓ 1d ✗((A)) · 2 ✓(17) · 3a ✗((ii) 0; DOPbNR16 (iii), 나머지 5 (i)) · 3b ✗(3) · 4 ✗(ALDv ROTaSV (iv)) · 5 ✗(gmm32 (i) 2/3, scalar (i) 3/3) · 6 ✓ · 7 무효 0·드리프트 0 → **적중 5 / 빗나감 5** = §6.1·EXPERIMENTS·DECISIONS 와 같다.
- **§5 ALD 조정 표 24 행**: ckpt sha·c·β·격자 끝(없음)·멈춤 단계 7·개발 NMSE 7·v 7·rot/dop 가 `tune_XA<T>.json` 과 **24/24 동일**; json 의 git d17f3d65 (동결 전), ald.py f1da04d1e91e0baf, seed 20260927, n_dev 512, dev_skip 2560 (개발 시행 2560..3071) — §5 서술과 같다. β 규칙: 24 개 모두 개발 최적 β 가 1e-5/1e-4/1e-3 이나 저자 기본 0.005 가 0.1 dB 안이라 0.005 유지(`selection_rule`) ✓.
- **git·로그·컨테이너 (§G)**: HEAD 64f422c3, 작업 트리 깨끗(conf/code·Demo·3 기록). 동결 e7c9f4a7 (09-29 07:14:05 KST = 09-28 17:14 CDT) → HEAD 의 문서 diff 는 hunk 1 개 `@@ -110,3 +110,109 @@`, '−' 줄 0 → **§0~§5 불변**(동결본 112 줄, `## 6.` @112). `diff e7c9f4a7..HEAD -- conf/code Demo` 비어 있음 ✓; d17f3d65..e7c9f4a7 코드 diff = pair_baselines.py·run_supp16e4.sh 만(§4 서술과 같음). 로그: tune 16:27~17:12 CDT (git d17f3d65) → `SUPP_TUNE_DONE 24/24` → eval start 17:14 CDT (git e7c9f4a7) → phase 0 17:22 → 19 조건 17:27~19:47 CDT(ROTaMX pair_baselines 19:47) → **컨테이너 PID 1 시작 09-29 09:48:21 KST = 09-28 19:48:21 CDT** (호스트 `who -b` 는 09-28 11:44 KST 그대로 → 호스트 재부팅이 아니라 컨테이너 재시작; §6.1 의 "서버(컨테이너) 재시작" 과 일치) → 22:45 CDT "resume re-run after reboot: ROTbMX DOPaNR16 DOPbNR16 ROTaNR16 ROTbNR16", eval start (git e7c9f4a7), phase 0 즉시 완료(ALD 추정 24 개 mtime 17:14~17:22 CDT → 재사용 ✓) → 22:57 ROTbMX … 00:32 `SUPP_EVAL_DONE ok=5 fail=0` ✓. `raw_XLROTbMX` 첫 청크 22:47 CDT("청크 0 개 상태" ✓). 동결 전(07:14:05 KST 이전) mtime 의 새 청크 0 개. pairB 19 개 mtime 17:27~19:47, 재개 5 개 22:57~00:32 → 재개가 끝난 조건을 다시 매기지 않았다. `resume_after_reboot.sh` 에 SUPP 없음(DECISIONS 291 행 서술 ✓). 시각 환산(07:14~09:47 + 12:45~14:32 KST = 17:14~19:47 + 22:45~00:32 CDT; 기록 14:36/14:37 KST = 00:36/00:37 CDT) ✓.

## 수치·라벨 오류
- 없음.

## 규칙 적용 재검 (§1·§2 를 재계산값에 다시 적용)
- 주 라벨 4 개: k𝔅 = 12·m𝔅 = 0 → (A) 4/4; DOP ν=0.01 은 원 b\* (iii) 이므로 "전부" 문장 불가 — §6.1 표기 그대로 ✓. "전부" 문장 = 원 b\* (i) ∧ k𝔅 = 12 ∧ m𝔅 = 0 ∧ R_{X\*} 정의됨 ∧ 하한 > 0 → 18 조건 ✓, 문자열은 §2 등록 문구 ✓, 가드 두 조건은 절대 격차만(377·243) ✓, §0 의 불가 5 조건 명시 ✓.
- R0-pilot 판독 @1 (§1) 로 계산 ✓ (D2 C2 표의 R0-pilot@1 행 4 칸 일치); (iv) 는 k 에 세지 않음 ✓ (ROTaSV 8).
- X\* 규칙(𝔅 ∪ {b\*} 중 −3 dB 실패 최소, 동률 이름순) ✓ — 24 조건 모두 동률 없음(차점 F 는 recompute.out 각 SUMMARY-B 줄).
- 예측 3a 의 "(ii)" 판정에 대해 V1-pilot 이 DOP ν=0.01 에서 (ii) 인 조건 0 ✓; (iii)/(iv) 는 "(i) 아님" 으로만 셌다(§3 머리말) ✓.
- 금지어(여지·headroom·bound·최적·비긴다·강건·도달)·자리표시("x CDT"/"x KST") §6.1·EXPERIMENTS 54 행·DECISIONS 291 행에 없음 ✓.

## 규칙 위반으로 볼 만한 것
- 없음. 새 raw 는 전부 동결 커밋 e7c9f4a7 코드로 동결 뒤에 생성(청크 `run|git`·manifest·mtime 삼중 일치); §0~§5 는 동결 뒤 불변; ALD 조정은 동결 전(d17f3d65)에 개발 시행 2560..3071 의 NMSE 만으로 했고 §5 에 값 그대로 기록; 재개는 §1 "인자 부분집합은 재개 전용" 대로 라벨 없는 5 조건만, 같은 커밋, 끝난 19 조건은 건드리지 않음, 전제 조건 통과(로그 eval start); 판정점·라벨·R_X·X\*·문장은 등록 규칙 그대로; 주 라벨 4 개 밖의 개별 (i) 을 독립 주장으로 쓰지 않았고 조건 사이 보정·해석 없음("전사만").

## 메모 (선택; 수치·라벨 변경 없음)
1. [§6.1 118 행] "그 뒤 서버(컨테이너) 재시작으로 중단됐다" — 재시작 시각이 없다. 컨테이너 PID 1 시작 = **09-28 19:48 CDT (= 09-29 09:48 KST)**, 호스트는 재부팅되지 않음(`who -b` 09-28 11:44 KST). 선택: "(컨테이너 19:48 CDT 재시작; 호스트 재부팅 아님)" 병기. 로그 229 행의 "after reboot" 는 스크립트 밖에서 적힌 줄이라 그대로 둬도 된다.
2. [§6.1 124·126·127 행] "전부" 문장 3 개에 §2 의 범위 한정 "(이 셀·예산·prior·조건 한정)" 이 붙어 있지 않다. §2 표에 이미 있고 §6.1 은 전사 전용이라 오류는 아니나, 원고로 옮길 때 빠지지 않도록 선택 병기.
3. [보고 전용] R_X 1차가 포화 가드(−3 dB BLER > 0.9)로 "정의하지 않음" 인 (조건, X) 가 가드 두 조건 밖에도 있다: R4-llr (DOPa/DOPb/ROTa/ROTb × D3·U28·MX 등) 과 R0-pilot@1 (DOPbD3·DOPbU28·DOPaMX·DOPbMX 등) — 목록은 recompute.out §5 "R_X defined" 줄. §6.1 은 이들을 인용하지 않으므로 영향 없음(정의된 1차 R_X 270/312).
4. [보고 전용] 테스트 ALD NMSE(hhat/H 재계산 = 추정 파일 `nmse`) 대비 §5 개발 NMSE 의 최대 |차| 는 24 조건에서 ≤ 0.37 dB (NR16 세 조건·ROTaD3 0.33~0.37). §1 보고 전용 목록에 "테스트 ALD NMSE" 가 있으나 §6.1 은 파일만 가리킨다 — 선택: 최대 |차| 한 줄.
5. [머리말·DECISIONS 289 행] "~06:1x KST", "~07:0x KST" 는 사용자 결정 시각의 의도적 근사("~")이고 동결 전 문구라 그대로 둔다(§6.1·EXPERIMENTS·DECISIONS 291 행에는 자리표시 없음). 참고: `conf/raw_smoke` 는 09-19 의 빈 디렉터리(파일 0)로 SUPP 스모크와 무관("raw 는 지웠다" ✓).

## 일치 확인한 항목 (전수)
- §6.1 실행·수용 문단: 동결 e7c9f4a7 · 17:14 시작 · phase 0 17:22 · 19 조건(D2C2·D3·SV8e·UMi28 전부 + MIX3 DOPa·DOPb·ROTa) 19:47 까지 · 재시작 · ROTbMX 청크 0 · 재개 22:45 5 조건 · 같은 커밋 · 잘린 npz 0 · ALD 추정 24 재사용 · 00:32 ok=5 fail=0 · 24/24 ACCEPT OK · 무결성 OK 24 · expect-bstar rc=0 24 · run|git e7c9f4a7 / 063f3bcb / a4cbd184 · 무효 0 ✓.
- 주 라벨 표 4 행(k·m, (A), 원 b\*, X\*(F)·R_{X\*} CI 또는 가드·절대 격차 377, 문장) ✓; D2 C2 X 표 52 칸 ✓; 24 조건 표 168 칸 ✓; 집계 문단 6 항목·arm 별 표 6 행 ✓; §3 채점 표 11 행·합계 ✓; 보고 전용 목록(파일 존재: pairB 24·accept 24·manifest 72·ald_XA 24) ✓.
- §5 표 24 행 × 7 칸 ✓ (+ 동결 전 git d17f3d65·ald.py sha·seed·n_dev·격자 끝 없음).
- EXPERIMENTS 54 행: 시각(KST/CDT)·스크립트·동결 해시·명령 구성·seed·ALD seed·GPU 서술·핵심 지표(24/24, (A) 4/4, (ii) 0/288, 21/24, 18/24, 가능 19 중 18, ROTaNR16)·로그 경로·채점(1d·3a·3b·4·5 빗나감, 1a–c·2·6 적중)·가드 2 조건 ✓.
- DECISIONS 291 행: 시각·재개 서술(resume_after_reboot.sh 미사용 포함)·합계·주 라벨·문장 충족/불가·집계·채점 ✓.
