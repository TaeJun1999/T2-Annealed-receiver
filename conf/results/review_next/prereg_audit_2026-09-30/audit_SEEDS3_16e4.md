# 기록 감사 — SEEDS3_16e4 §6.1 (D3·SV8e·MIX3 시드 a2·a3) — 수치 감사 + 규칙·출처 감사 통합본

- 통합 2026-09-30 09:49 CDT (= 23:49 KST), Opus 5.5 서브에이전트. 독립 감사 2 건(둘 다 Fable 5.1 서브에이전트, 읽기 전용)을 합친 것이다: **수치 감사** (`recompute_seeds3_numeric.py` → `.out`) 와 **규칙·출처 감사** (`recompute_seeds3.py` → `.out`; 이 파일의 첫 판 09:48 CDT). 통합하면서 새 주장을 더하지 않았다. 두 감사 모두 원본 파일을 고치지 않았고 이 디렉터리만 만들었다.
- 대상: `NEXT_EXPERIMENTS_SEEDS3_16e4.md` 전체 (§0–§5 동결 73a93547, §5 채움 dbe0bdb3, §6.1 미커밋), `docs/EXPERIMENTS.md` 마지막 행 (:56, 미커밋), `DECISIONS.md` `[2026-09-30 23:30 KST] SEEDS3_16e4 결과 기록` 줄 (:307, 미커밋). 틀·기준: `NEXT_EXPERIMENTS_SEEDS16e4.md` §6, `prereg_audit_2026-09-27/audit_PILOT_SEEDS_MISMATCH.md`.
- 방법 (두 감사 공통): raw npz·ckpt·학습/실행 로그·manifest·git 만 읽는 재계산. 09-27 감사 `recompute.py` 의 helper 재사용 (첫 arm 앵커 표 B, scipy binomtest 정확 부호검정, POWERED·2/3 규칙, 짝 부트스트랩 시드 20260925, 회수율 부트스트랩 시드 20260926); `analysis` 표 코드·pair 스크립트·`recovery_ci.py` 호출 없음 (규칙 감사는 `eval_accept.py` 도 호출하지 않음; `analysis.load_raw` 는 raw 읽기로만 09-27 모듈을 통해 사용). 부트스트랩은 등록 시드라 자리수 일치는 **재현**이지 독립 표본이 아니다. CPU 1 프로세스 (OMP 2), GPU 숨김. HISNR 출력(`raw_HS*`·`hisnr_*`)은 열지 않았다; `~/t2_wtS/conf/logs/stage1.log` 는 `STAGE1_C6_DONE` 줄 하나만 grep (규칙 감사).

## 총평

**판정: 수치·라벨·예측 채점 오류 없음, 규칙 위반 없음.** 수치 감사는 문서값 약 120 항목을 프로그램으로 대조해 `mismatches: 0` (`recompute_seeds3_numeric.out` §4); 규칙 감사도 수치·라벨·채점 8/8 을 따로 재현했고, §0–§3 동결 불변, §5 채움·커밋 뒤 BLER, 체크포인트·적합·수용·순서·시각이 로그와 일치함을 확인했다. 어느 라벨도 채점도 바뀌지 않는다. 정정은 **기록 위생 6 건** (공개 누락 2, 시각 귀속 1, 문구 3) 이고 수치 변경은 없다. 위생 5·6 은 두 감사가 모두 짚었다 (수치 감사는 "선택" 으로 분류).

## 수치·라벨 오류

**없음** (두 감사 모두).

## 규칙 위반

**없음.** 등록 §1·§4·§5 조건을 하나씩 검사한 결과 (규칙 감사; ✓ 표시가 붙은 항목 중 수치 감사가 따로 확인한 것은 아래 "독립 재현" 절에 표시):

1. **§0–§3 동결 불변**: `git diff 73a93547 dbe0bdb3 -- 기록` = 4/4 줄 — §4 1 행("진행 중" → "완료") + §5 3 행 채움뿐; `dbe0bdb3..HEAD` 빈 diff; 작업 트리 = §6.1 42 줄 **추가만** (§6 "추가만" 규칙 준수). ✓
2. **§5 커밋 뒤에만 BLER**: dbe0bdb3 09:39:20 KST (09-29 19:39 CDT) < 실행 시작 09-30 18:11 KST (04:11 CDT). `run_seeds3_eval.sh` 는 §5 sha 6 개를 인자로 고정, `run_seeds16e4.sh:20` 이 sha 불일치면 ABORT. ✓
3. **체크포인트 (§5)**: sha256[:16] 6 개 = §5 (4e9a6ca2c3197004 · 3e4e36945a9314c3 · b05d92632e611494 · 5e1ff49f455f110a · d7a6b1a199c51637 · 128b8090036332bc); `_best.pt` epoch = best_epoch (386/449/236/299/433/351) = last `.pt` 의 best_epoch 6/6; best_val 정확 float 6 개 일치; last `.pt` stopped_by = patience 6/6, aborted = False; role = best; prior = sigma_tag; rung `D2SX{S2c,SV8e,MIX3}160000` attempt 2/3; split_hash = a1 (5c098ecb6185bcc6 · 60289e4ba2b3f97f · 16f67ba3d3f59660). manifest·run 로그·tables 머리말의 ckpt id 동일. ✓
4. **코드**: 여섯 태그의 tables 머리말·manifest·run 로그 git = **6b1de688** 하나; 실행 시 conf/code 청결 (`run_seeds3_eval.sh:8` 가 dirty 면 ABORT — 로그에 ABORT 없음, 등록 파일 tracked+clean 검사 :9 도 통과); `6b1de688..HEAD -- conf/code` 빈 diff; 지금 작업 트리 conf/code 청결. **단** 6b1de688 의 conf/code 는 동결 73a93547 과 **다르다** (12 파일 +276/−7; 위생 1). Stage C·수신기·runner 경로(`score.py`·`arms.py`·`runner.py`) 는 동결 이후 변경 없음 ✓; 비-Stage-C 10 arm 은 `--ref-arms all` 로 a1 raw 와 비트 동일 ✓ (재계산: KEYS_RAW 7 키 × 7 점, 다른 arm = {V0, V1, V4, V4b} 정확히, 여섯 태그).
5. **적합·재료**: fits 링크 6 개 = 상대 링크 → a1 디렉터리, mtime 09-30 06:57:25 KST (= 09-29 16:57 CDT, §4 ✓); git 미추적(관례). raw meta = a1 과 동일: D3 kron 4096 / ll_val 0.08879931165293979 / em_sec 15862.75, SV8e gmm256 / kron_K 2048 / −47.80545576704972 / 10589.88, MIX3 kron 4096 / 33.7604873920761 / 6242.08; ntrain 160000; iters 16; n 2560 × 7 점 × 14 arm, 448 raw 파일; 192 워커. ✓
6. **수용**: `<TAG>_accept.txt` 6 개 모두 "ACCEPT: OK -- <TAG>" (rc=0); `<TAG>_refarms.txt` 7 점 × "arms differing [V0, V1, V4, V4b]" 6 태그 → §1 조건 ⊆ {V0, V1, V4, V4b} 충족 (실행 유효). 판정점 = a1 (+0/+3/+6 · −3/+0 · +3/+6/+9). ✓
7. **순서·시각**: `cpu_chain.log` "stage 1 done → SEEDS3 BLER" 04:11 CDT (stage1.log `STAGE1_C6_DONE` 04:09 CDT ✓, 체인 폴링 120 s); `run_seeds3_eval.log` start 04:11 (git 6b1de688) → D3s2 04:11–04:53 → D3s3 –05:35 → SVs2 –06:04 → SVs3 –06:34 → MXs2 –07:18 → MXs3 –08:03 → `SEEDS3_EVAL_DONE ok=6 fail=0` 08:03; 순차·한 번에 하나 ✓; `CUDA_VISIBLE_DEVICES=''` 6/6 ✓. EXPERIMENTS 행 18:11–22:03 KST ✓.
8. **§4 학습 표 vs 로그** (`# =====` 머리말·재개 epoch): D3 a2 06:36:16 KST 시작 · 06:41:44 재개 (32 → 33) · 1 회 ✓; D3 a3 06:37:27 · 06:38:42 (4 → 5) · 06:40:15 (9 → 10) · 2 회 ✓; SV8e a2 06:37:41 · 06:38:55 (2 → 3) · 06:40:32 (5 → 6) ✓; SV8e a3 06:37:40 · 06:38:52 (3 → 4) · 06:40:29 (8 → 9) ✓; MIX3 a2 머리말 06:48:09 · 중단 0 ✓ (ckpt mtime − wall = 06:40:09 KST 프로세스 시작 ≈ "16:40:05 CDT"); 재개 전부 epoch ≤ 32 ✓; 여섯 모두 patience·발산 없음 ✓; 재추첨 없음(각 시드 ckpt 1 벌, 재개 로그 연속). **MIX3 a3 는 표에 "미시작" 그대로** → 위생 2.
9. **SV8e "이미 정해진 사실"**: a1 b\* BLER@16 +3 dB = 7/2560 = 0.0027 ("0.003") ∉ [0.005, 0.9] → 판정점 −3/+0 두 개 → POWERED 아님 → (iv); b\* 출력이 a2·a3 에서 비트 동일(재계산)이므로 판정점·(iv) 도 같다 — 주장 성립. `tables_D2_SVB16e4.txt:372-374` 인용 위치 ✓.
10. **MIX3 보고 전용**: `NEXT_EXPERIMENTS_38901.md` 제목·사용자 결정 [2026-09-27 00:07 KST] "MIX3 = 보고 전용 부속 점"; §1·§6.1 "역할 불변" 일관 ✓.
11. **자리표시·금지어**: 'x CDT'·TODO·유의하게·낫다·도달·여지·headroom·bound·최적·비긴다 — 기록·EXPERIMENTS 행·DECISIONS 줄에 없음 ✓. §1 의 `<sha §5>` 는 §5 참조 표기(값은 §5·스크립트에 있음), 자리표시 아님.
12. **KST/CDT**: 머리말 16:44/06:44, v2 16:57, 동결 17:00 (= 07:00:08 KST), §5 19:39 (= 09:39:20 KST), §6.1 09:30/23:30, EXPERIMENTS 18:11–22:03 ↔ 04:11–08:03, DECISIONS 23:30/09:30, 04:09·04:11·08:03 — 전부 −14 h 로 일치 ✓.
13. **검토·인용**: 검토 문서 반드시 7 · 권고 9 = 번호 항목 16 ✓; 반드시 1–7 은 본문에서 확인 (§4 표, 자리표시 없음, 재개 보장 범위 :5, §5 epoch 검사, SV8e 사실화 §0/§3-4, 라벨 절대 범주 §1, 겹침 정의 §3-3/5, fits 링크 §4). `score.py:872-916` (resume 복원: model·opt·EMA·`g`·best/best_epoch·hist) · `:1009-1027` (원자 저장, best 먼저) 인용 위치 ✓; `score.py` 에 deterministic/cudnn 설정 없음 ✓. `eval_accept.py` docstring 19 행 (gmm256 이면 kron_K 미검사) ✓.

## 정정 필요 (위생; 수치·라벨·채점 불변)

1. **[공개 누락] `NEXT_EXPERIMENTS_SEEDS3_16e4.md:74` (§6.1 실행·수용) "main HEAD 6b1de688; conf/code 청결"** (규칙 감사) — "청결" 은 참이나, 6b1de688 의 `conf/code` 는 동결 73a93547 과 **다르다** (SEEDS16e4 §6.1·§6.2 와 09-27 감사 정정 1 의 관례상 차이를 적어야 한다): 새 파일 6 (`cpu_chain.sh`, `run_seeds3_eval.sh`, `run_hisnr16e4.sh`, `run_static16e4.sh`, `genie_floor.py`, `hisnr_report.py`) + 수정 6 (`analysis.py` `load_raw` 청크 시작 검사에 `HISNR_SKIP0` 추가 1 줄 — 테스트 집합(청크 0 시작)에선 `max(...)=0` 으로 경로 불변; `common.py` 상수 1 줄; `eval_accept.py` `--skip0` 기본 0 → plan 불변; `run_manifest.py` split 라벨 분기(skip ≥ 10000 만; 이 실행은 "TEST set"); `pair_baselines.py` +63/−3 — 이 파이프라인은 호출하지 않음; `run_seeds3_train.sh` 주석). `score.py`·`arms.py`·`runner.py` 는 동결 이후 변경 없음.
   - 고칠 문구 (§6.1 :74 괄호): "(main HEAD 6b1de688, 실행 시 conf/code 청결; 동결 73a93547 과의 conf/code 차이 = HISNR·STATIC·체인 스크립트 추가 + `analysis.load_raw`/`eval_accept`/`run_manifest` 의 HISNR_SKIP0 분기(테스트 집합 경로 불변) + `pair_baselines.py`(미호출); Stage C·수신기·runner 코드 동일. 수신기 불변 근거: `--ref-arms all` 비-Stage-C 10 arm 비트 동일 6/6)".
   - `docs/EXPERIMENTS.md:56` 커밋 칸 "6b1de688" 뒤에: "(동결과 conf/code 차이 = 위; 수신기 코드 동일)".
2. **[공개 누락] `NEXT_EXPERIMENTS_SEEDS3_16e4.md:56` (§4 표) "MIX3 a3: 미시작"** (규칙 감사) — §5·§6.1 이 채워진 지금도 그대로다. 로그: 프로세스 시작 09-29 **18:08 CDT** (last ckpt mtime − wall = 08:08:06 KST; `seeds3_MIX3_a3.log` 생성 08:08:04 KST = D3 a3 종료 08:08:01 직후, 스크립트 :9-10 `wait` → GPU 2 대로), 첫 epoch 머리말 **18:15:52 CDT** (08:15:52 KST), 중단 0 회 (머리말 1 개, epoch 1 부터, resume 없음), 종료 19:14:03 CDT (371 epochs, patience). 머리말 `:5` "a2·a3 학습은 이 초안보다 먼저 시작했다 (16:36–16:41 CDT)" 는 MIX3 a3 에는 해당 없음 — 동결 17:00 CDT **뒤** 시작 (오히려 깨끗한 경우).
   - 고칠 문구 (§4 는 "갱신한다"; :56 "MIX3 a3: 미시작" 을 대체): "MIX3 a3: 프로세스 18:08 CDT, 첫 epoch 18:15:52, 중단 0 회, 종료 19:14 CDT (동결 뒤 시작)".
   - 머리말 `:5` 는 동결 문장이므로 고치지 않고 §6 감사 정정 각주로 남긴다.
3. **[시각 귀속] `NEXT_EXPERIMENTS_SEEDS3_16e4.md:55` (§4 표) "완료 (09-29 19:39 CDT, `SEEDS3_TRAIN_DONE`"** (규칙 감사) — `logs/seeds3_train.log` 는 09:14:06 KST = **19:14 CDT** 에 쓰였다 (MIX3 a3 마지막 ckpt 09:14:03 + rc 09:14:06). 19:39 CDT 는 §5 채움·커밋 시각 (dbe0bdb3 09:39:20 KST).
   - 고칠 문구: "완료 (09-29 19:14 CDT, `SEEDS3_TRAIN_DONE`; §5 채움 19:39 CDT; …".
4. **[문구] `NEXT_EXPERIMENTS_SEEDS3_16e4.md:65` (§5 표 첫 열 헤더) "sha256[:16] · epoch · best_epoch · stopped_by (`_best.pt`)"** (규칙 감사) — `_best.pt` 의 stopped_by 는 **None** (best 저장 시점엔 정지 전, `score.py:1025-1027` 주석대로); patience 는 last `.pt` (및 로그 done 줄) 의 값. 값은 맞다. 헤더만 고친다.
   - 고칠 문구: "sha256[:16] · epoch · best_epoch (`_best.pt`) · stopped_by (last `.pt`·로그 done 줄)".
5. **[문구] `NEXT_EXPERIMENTS_SEEDS3_16e4.md:82-83` (§6.1 표) SV8e a2·a3 라벨 칸 "**(iv)** UNDECIDED (판정점 2)"** (두 감사 모두) — §2 의 등록 문자열 "판정하지 못함 (검정력 미달)" 이 §6.1 에 없다 (09-27 감사 정정 5 와 같은 유형). 수치 감사는 SEEDS16e4 §6 선례도 같은 축약을 썼으므로 **선택** 으로 분류했다.
   - 고칠 문구: "**(iv)** '판정하지 못함 (검정력 미달)' (판정점 2 개; 격자 확장 없음)".
   - (i) 행의 "**(i)** 3/3" 은 SEEDS16e4 §6 처럼 "(i) POWERED 3/3" 로 두면 틀과 같아진다 (선택; 규칙 감사).
6. **[문구] `docs/EXPERIMENTS.md:56` (마지막 행) 결과 칸 'SV8e "판정하지 못함 (0/3, 3 판정 못함)"'** (두 감사 모두) — §1 형식·§6.1 (:90)·DECISIONS 줄 (:307) 은 "(0/3 (i), 3 판정 못함)". 수치 감사는 **선택** 으로 분류했다.
   - 고칠 문구: 'SV8e "판정하지 못함 (0/3 (i), 3 판정 못함)"'.

## 메모 (정정 아님)

7. 학습 GPU 번호 (GPU 1–5, MIX3 a3 GPU 2) 는 로그에 장치 색인이 없어 확인 불가 (스크립트 인자와 모순 없음). tmux 창 이름 미확인 (읽기 전용). (규칙 감사)
8. D3 a3·SV8e a2·SV8e a3·MIX3 a2 의 "ckpt mtime − wall" 프로세스 시작 = 06:40:09 KST (= 16:40:09 CDT) — §4 의 스크립트 3 차 인스턴스 16:40:05 와 4 s 차 (저장 지연), 일치. D3 a2 = 06:41:38 KST vs 재개 머리말 06:41:44 — 일치. (규칙 감사)
9. §3 항목 9 는 경로 서술이라 미채점 (틀과 같음) → "적중 8, 빗나감 0" 은 채점 가능 8 항목 기준. (규칙 감사)
10. raw 의 a1 ckpt id (D3 7ebf4e6647d4413f @494 · SV8e d2d78962c2846364 @240 · MIX3 b591ae24ae3c5f31 @464) 는 §0 의 epoch 과 일치. (규칙 감사)
11. `run_seeds3_train.sh` 주석 정정 (dbe0bdb3) 파일 mtime 09:39:19 KST = 학습 종료 (09:14) 뒤 — DECISIONS 동결 줄 "실행 중 파일이라 학습 종료 뒤 정정" 대로. (규칙 감사)
12. V0 −3 dB 가드 발동률 (보고 전용, 재계산): D3 0.233/0.216/0.304, SV8e 0.009/0.003/0.008, MIX3 0.536/0.516/0.576 (a1/a2/a3) — §6.1 은 파일로 넘겼으므로 대조 대상 없음. (규칙 감사; MIX3 a3 0.576 은 수치 감사 `.out` 에도 같다)
13. 시드별 V1 −3 dB 95% Wilson (문서에 없는 참고값, 수치 감사 `.out`): D3 a2 (0.381, 0.419) · a3 (0.379, 0.417); SV8e a2 (0.146, 0.174) · a3 (0.143, 0.171); MIX3 a2 (0.513, 0.552) · a3 (0.511, 0.550).
14. 파일 출처: 수치 감사 에이전트의 재계산 파일이 같은 폴더에서 병렬로 돌던 규칙 감사 에이전트에 의해 23:38 KST 에 덮어써졌다고 수치 감사가 보고했다 → 수치 감사 결과는 `recompute_seeds3_numeric.*`, 규칙 감사 결과는 `recompute_seeds3.*` 로 분리돼 있다.

## 규칙 적용 재검 (§1·§2·§3 을 재계산값에 다시 적용; 두 감사 결과 같음)

- **D3**: a2 판정점 +0/+3/+6, 223:31 (p 5.1e-37) · 117:23 (2.3e-16) · 57:12 (3.7e-08), pooled 397:66, POWERED, wy = 3 → (i); a3 224:34 · 118:18 · 59:10, pooled 401:62 → (i); a1 (i) → **"시드 강건 (3/3 (i))"** ✓.
- **SV8e**: a2·a3 판정점 −3/+0 (b\* +3 dB 0.0027 < 0.005), POWERED 아님 → (iv) · (iv); 120:65 · 27:12 pooled 147:77, 126:62 · 28:6 pooled 154:68; a1 (iv) → **"판정하지 못함 (0/3 (i), 3 판정 못함)"** ✓ (§0 사실, 보고 전용).
- **MIX3**: a2 +3/+6/+9, 79:38 · 62:28 · 41:15, pooled 182:81 → (i); a3 79:40 · 66:24 · 41:12, pooled 186:76 → (i) → **"시드 강건 (3/3 (i))"** (보고 전용) ✓.
- **§3 채점**: 1 ✓ · 2 (0.400, 0.398 ∈ [0.372, 0.410]) ✓ · 3 ([+1.20, +1.69]·[+1.24, +1.74] ∩ [+1.19, +1.67] ≠ ∅) ✓ · 4 (0.160, 0.156 ∈ [0.143, 0.172]) ✓ · 5 ([+0.15, +0.32]·[+0.22, +0.39] ∩ [+0.16, +0.33] ≠ ∅) ✓ · 6 ✓ · 7 (0.532, 0.530 ∈ [0.510, 0.548]) ✓ · 8 (6/6 patience) ✓ → 8/8, 문서와 같다.

## 독립 재현한 항목

**두 감사가 각자 재현** (문서값과 자리수까지 일치):
- 표 B `b* → V1` 9 태그 (a1 3 + 시드 6): 판정점 (D3 +0/+3/+6, SV8e −3/+0, MIX3 +3/+6/+9), a:b 25 개, pooled 9, POWERED, 라벨 (D3·MIX3 a1/a2/a3 (i) 3/3, SV8e a1/a2/a3 (iv) UNDECIDED 판정점 2).
- SNR@0.1 격차 90% CI 9 개 (2 자리). 4 자리 (참고): D3 a2 +1.4247 [+1.1974, +1.6924] · a3 +1.4647 [+1.2387, +1.7363]; SV8e a2 +0.2353 [+0.1486, +0.3203] · a3 +0.3034 [+0.2195, +0.3889]; MIX3 a2 +0.7207 [+0.4365, +1.0273] · a3 +0.8323 [+0.5414, +1.1539].
- V1 −3 dB BLER·실패 수 9 개, a1 95% Wilson 3 개 ([0.372, 0.410]·[0.143, 0.172]·[0.510, 0.548]).
- 회수율 R(−3 dB) 9 개와 90% CI (default_rng(20260926), B = 2000).
- b\*·genie −3 dB 실패 수 세 시드 동일 (1298·485, 464·31, 1421·679); b\*/genie −3 dB BLER a1 (0.507/0.189, 0.181/0.012, 0.555/0.265); 7 KEYS_RAW × 7 점에서 b\*·genie 비트 동일, a1 과 다른 arm = {V0, V1, V4, V4b} 여섯 태그 모두 (refarms 파일과 재계산 둘 다).
- 집계 라벨 3 개, 시드 간 산포 3 개 (0.391–0.400 / 0.156–0.160 / 0.529–0.532), §3 채점 8/8.
- §5: sha 6 · epoch 6 · best_epoch 6 · last epoch 6 · best val 6 (정확 float) · stopped_by = patience 6/6 · 참조 raw 6; §0 a1 best val 3 개 (0.3534156 @494 · 0.7134662 @240 · 0.4814744 @464).
- 실행 시각 (stage1 04:09 CDT, chain 04:11, DONE 08:03, ok=6 fail=0), manifest git 6b1de688, 실행 시 conf/code 청결, KST↔CDT 환산 (EXPERIMENTS 행·DECISIONS 줄·§6.1 머리말).
- EXPERIMENTS 행 (시각 4 · 커밋 3 · rung · 라벨 3 · ok/fail · 8/8) 과 DECISIONS 줄 (시각 2 · 04:11 · 08:03 · 6b1de688 · 라벨 3 · 8/8) — 규칙 감사는 전수 대조, 수치 감사는 라벨·시각·환산 대조.

**규칙 감사만 확인** (수치 감사 범위 밖): 규칙 검사 1 (동결 diff), 2 (§5 커밋 → BLER 순서, sha 고정 ABORT), 3 의 role·prior·rung·split_hash, 4 의 73a93547..6b1de688 conf/code diff 와 Stage C 코드 불변, 5 (fits 링크·mtime·raw meta), 6 (accept 파일), 7 의 태그별 시작·종료 시각, 8 (§4 학습 표 vs 로그 머리말·재개 epoch; MIX3 a3 시각), 9–13 (SV8e 사실 근거 인용, MIX3 보고 전용 근거, 자리표시·금지어, 검토 항목 수, `score.py`·`eval_accept.py` 인용 위치), 위생 1–4 의 근거.

**재현하지 못한 것**: 학습 GPU 번호 (메모 7).

## 재계산 파일 (이 디렉터리)

- `recompute_seeds3_numeric.py` → `recompute_seeds3_numeric.out` (186 줄; §4 summary `mismatches: 0`), `.err` 비어 있음 — 수치 감사. 문서값을 dict 로 옮겨 프로그램으로 대조.
- `recompute_seeds3.py` → `recompute_seeds3.out` (198 줄), `.err` 비어 있음 — 규칙·출처 감사. §0 git, §1 ckpt 12 + 학습 로그 6, §2 raw 9 (a1 × 3 + 시드 6), §3 manifest·tables·accept·refarms·로그·링크·stage1.
- 둘 다 CPU 1 프로세스 (OMP 2), GPU 숨김, `CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=2 ~/miniforge3/envs/torch/bin/python <script> > <out>`.
