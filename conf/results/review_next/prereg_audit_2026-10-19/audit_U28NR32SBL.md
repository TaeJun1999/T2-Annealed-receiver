# 기록 감사 — NEXT_EXPERIMENTS_U28NR32SBL.md §5 · §6 (E3′ UMi28 C9 32×4 SBL-loop 하나, 태그 U28NR32SBL)

- 감사자: Claude Code (Fable 5.1 서브에이전트, 독립 기록 감사; `gcap/PROMPT_SERVER_COMMON.md` §3 의 "기록 감사 1회"). 감사 시각 2026-10-19 08:47 ~ 09:0x CDT (= 10-19 22:47 ~ 23:0x KST; `date` 로 읽음).
- 감사 대상 판: 작업 트리 = HEAD **9a2c9fd4** (main). 감사 대상 파일 (등록 문서 · `sbl32/sbl32_s5.txt` · `sbl32/U28NR32SBL_accept.txt` · `pairB_U28NR32SBL.txt` · `pairB_U28NR32SBL_bstar.txt`) 은 모두 추적 중이고 작업 트리 = HEAD. 등록 §6 커밋 9b5ec869 (10-18 15:54:57 CDT), 실행 커밋 13f05fb1 (14:29:07 CDT), FREEZE d6a76fbf (14:23:45 CDT).
- 방식: 읽기 전용. 새 파일은 이 폴더 (`prereg_audit_2026-10-19/`) 에만: `recompute_sbl32.py` → `recompute_sbl32.out` · `recompute_sbl32.json` (numpy 로 npz 청크 직접 읽기; `pair_baselines` · `analysis` · `select_dev` 등 등록 코드 import 없음 — 판정점 선택 · exact 부호검정 · power guard · 라벨 · SNR@0.1 보간 · paired bootstrap · R_X · 개발 선택 규칙을 따로 구현), `rerun_pairB_U28NR32SBL_SBL.txt` · `rerun_pairB_U28NR32SBL_bstar_SBL.txt` · `rerun_accept_SBL.txt` (등록 도구를 stdout 만 이 폴더로 돌려 커밋본과 `diff`). CPU `nice -n 10 taskset -c 6-9`, GPU 미사용 (`CUDA_VISIBLE_DEVICES=`), runner 실행 하위 명령 · `run_*.sh` 미실행. git 상태 · 기존 파일 변경 없음. 다른 등록 test (E1+, CPU 24-47 …) 가 도는 동안 수행 — 그 CPU 는 쓰지 않았다.

## 1. 재계산한 것과 재현 여부

자동 비교는 `recompute_sbl32.out` 의 `COMPARISONS: 442 match, 0 mismatch` 가 정본이다 (항목별 이름은 스크립트의 `cmp(...)` 호출).

| 항목 | 방법 | 검사 값 수 | 결과 |
|---|---|---|---|
| raw 청크 계획 `raw_U28NR32SBL` {(40k, 40): k = 0..63} × 7 SNR (−12 … +6), 기준 raw 3 개 (`t2_wtS` base · PIL · ALD) 도 같은 계획; `run\|skip` · `run\|n` · `run\|snr` = 파일명 | 파일명 파싱 + 청크 안 값 | 4 × 448 | **재현** (구멍 · 중복 없음; `\|failed` 키 0; 비유한 blk_err@16 0 = raise 0) |
| raw meta 값 집합 (§6.1): `run\|git` {13f05fb1}, `meta\|sparse` {`{"L": 1, "n_em": 3, "rho_omp": 1, "rho_sbl": 4}`} (= `json.dumps(sort_keys)` 의 §5 설정), `meta\|bstar` {kron}, `kron_K` {4096}, `ll_val\|kron` {152.23176788511105}, `worker_gb` {7.0}, `jobs` {96}, `run\|iters` {16}, `run\|seed` {20260926}, `ntrain` {160000.0}, `stagec_ckpt_id` 없음, arm = {R5-genie, SBL-loop}; `ll_val\|gmm32` 54.033261174240884 = base raw 와 같음 (Cs 가 같은 fullK32 적합 — 대리 확인) | 448 청크 전부 | 13 | **재현** |
| 같은 시행 확인: R5-genie **7 KEYS_RAW + guardH** (등록 수용은 4 키) × 7 SNR × 2560 시행을 base raw 와 비트 대조 (NaN = NaN); PIL · ALD raw 의 genie 도 base 와 대조; `V1-pilot@1 nmse = V1@1`, `bstar-pilot@1 = b*@1` | `np.array_equal(equal_nan)` | 6,074,880 값 (3 raw) + 2 | **재현** (다른 배열 0) |
| 실패 수 @16 / 2560, 16 arm × 7 SNR (`pairB_U28NR32SBL.txt:107–122`; §6.2 의 SBL-loop 2522 · 1772 · 979 · 671 · 386 · 174 · 83, V1 · b\* · genie 행 포함); §0 의 판정점 합 b\* 958 · V1 599 · genie 127 | numpy 직접 (blk_err@16 ≠ 0 또는 비유한) | 112 + 3 | **재현** |
| 표 B X → V1, X = b\* + 13 (SBL-loop 포함): 판정점 (앵커 규칙: BLER@16 ∈ [0.005, 0.9] 중 \|log10(BLER/0.1)\| 최소 3 점), 점별 a:b · exact 양측 p (`%.2g` 문자열까지), pooled, POWERED, 2/3 규칙 · 라벨, SNR@0.1 격차 + 90 % paired bootstrap (B 2000, 시드 20260925 의 같은 재표집 순서를 따로 구현), 절대 격차 −3 dB, R_X −3 dB (primary) 와 판정점 (secondary) 의 점추정 + 90 % paired bootstrap (B 2000, 시드 20260926) | 직접 구현, 커밋본의 7 줄 블록과 문자열 비교 | 14 쌍 × 7 줄 = 98 | **재현** (전부 문자열 일치; SBL-loop → V1: −3/0/+3, 325:3 · 216:10 · 110:6, p 2.2e-92 · 1.5e-51 · 7.5e-26, pooled 651:19 p 1.3e-165, POWERED, 3/3 → (i), +3.14 dB [+2.78, +3.54] censored 0 %, 322 / 2560, 0.552 [0.519, 0.587], 0.572 [0.548, 0.597]) |
| 요약 줄: SUMMARY-B (13: (i) 13), SUMMARY 14 (i) 14, X\* = V1-pilot (F 440) R_X\* 0.259 [0.216, 0.301], '전부와 멀어진다' MET | 직접 | 4 | **재현** |
| 보고 전용 b\* → SBL-loop (`pairB_U28NR32SBL_bstar.txt`): 판정점 −3/0/+3, 34:196 · 47:129 · 23:52 (p 7.2e-29 · 5e-10 · 0.0011), pooled 104:377, b\* 적게 3/3, −0.85 dB [−1.16, −0.62], 판정점 실패 509/304/145 · 671/386/174 | 직접 | 5 줄 | **재현** (기계적 라벨은 (ii) 이나 §1.3 대로 §6 은 라벨을 붙이지 않음 — 일치) |
| 보고 전용 중앙 NMSE@16, 15 arm × 7 SNR (`:124–138`) | `nanmedian` 직접 | 105 | **재현** |
| 부트스트랩 CI (SNR@0.1 격차 · R_X): 등록 도구 재실행 → 커밋본과 `diff` | `pair_baselines.py` 2 회 (stdout 만 이 폴더), 실행 커밋과 같은 판 (sha256[:16] f11cea47e8c9c83c, `git diff 13f05fb1 HEAD -- code/pair_baselines.py` 0) | 2 파일 | **바이트 동일** (`rerun_pairB_U28NR32SBL_SBL.txt`, `rerun_pairB_U28NR32SBL_bstar_SBL.txt`) |
| 수용 검사 `eval_accept.py` (§1.3 인자 그대로, 같은 판 d05b660c07e899fe) | 재실행 | 1 | rc 0, `ACCEPT: OK -- U28NR32SBL`, 커밋본과 동일 (`rerun_accept_SBL.txt`) |
| SNR@0.1 격차 CI 의 시드 민감도 (보고 전용, 기록과 비교하지 않음) | 다른 시드 · 재표집 방식 | 1 | [+2.79, +3.53] (기록 [+2.78, +3.54]) |
| **개발 선택** (`t2_wtE3/conf/raw_U28NR32SBLd_*` 10 개): 청크 계획 SNR 마다 {(3840 + 10k, 10): k = 0..31}, `run\|iters` 16, `\|failed` 0, `meta\|sparse` = 후보 (warm 은 `"warm": true`), `run\|git` 후보마다 하나, R5-genie 7 키가 후보 사이 비트 동일; F(−3, 0, +3) · 합 · 지표 · raised; 동률 2 차 기준 (프로브 시간) · 3 차 (cold 먼저); TOP2; PICK; 범위 끝 | 직접 구현, `select_dev_cold.out` (9 줄) · `select_dev_final.out` (11 줄) 과 문자열 비교 | 10 × 5 + 20 | **재현** (r4e3 86 · 35 · 21 = 142 → … → r8e25 161; r8e3 = r16e3 148 동률 → 33.897 s < 124.065 s; TOP2 (4, 3) (8, 3); warm 146 · 147; PICK r4e3 cold, metric 0.14791666666666667, range_edge ['rho', 'n_em']) |
| 개발 실행 `run\|git`: cold 7 개 d3993c8d, r16e10 79ea962c, warm 둘 fe7e911b (§5) | raw 값 집합 | 3 | **재현** |
| 프로브 표 (§0 · §1.2 2 · `select_dev.py` 의 SEC 상수) = `sbl32/probe.out`; 시간 선별 30 h = 블록 578.6 s 초과 → (16, 25) 774.184 s (40.1 h) 만 제외; 경계 [295.3, 774.2) 무감도 | 파일 재독 · 산술 | 9 + 1 | **재현** |
| §5 산술: G = 6.580 × 1.05 = 6.909 → 7.0 (0.5 GB 올림); ⌊0.8 × 956.8 GiB / 7⌋ = 109 → 워커 min(96, 448, 109) = 96; ⌈448/96⌉ × 108 s = 540 s | 직접 | 3 | **재현** (MemAvailable 값 자체는 확인 불가 — §3) |
| §6.1 runner 로그: 메모리 가드 112 → 워커 96 (`run_D2_U28NR32SBL.log:3`), 448 청크 (:4), finished in 16.0 min (:453); 청크 시간 평균 194 s · 중앙 151 s · 범위 100–441 s | 로그 파싱 (448 값) | 5 | **재현** (194.3 / 151 / 100 / 441) |
| 예측 채점 (§3 → §6.3): 1 "ρ 클수록 F합 적음 (엄격)" — n_em 3: 142, 148, 148 · n_em 10: 154, 153, 155 · n_em 25: 159, 161 → **빗나감**; 2 cold 선택 → 적중; 3 (i) → 적중; 4 b\* 3/3 적게 → 적중 | 재계산 값에 §3 문구 재적용 | 4 | **재현** (관대한 채점 없음; 예측 1 은 한 열이라도 어긋나면 빗나감이라는 동결 채점 규칙 그대로) |
| 시각 (KST → CDT): v1 c197c234 10-17 11:56:29 · v2 d3993c8d 12:09:02 (개발 시작 12:09 ✓) · v2.1 79ea962c 13:03:42 ("13:0x" ✓) · v2.2 fe7e911b 19:59:01 · §5 fbd96825 10-18 13:52:44 ("13:52" ✓) · v2.3 73282a1e 14:23:08 ("14:23" ✓) · 병합 39f37711 14:23:23 / FREEZE d6a76fbf 14:23:45 · 실행 커밋 13f05fb1 14:29:07 · §6 9b5ec869 15:54:57; 파일: ALD 복사 13:51:26 ("13:51" ✓), `sbl32_s5.txt` 14:28:22, fits 복사본 14:29:11, test 첫 · 끝 청크 14:33:57 · 14:45:13, accept 14:45:21, pairB 14:45:38 · :46 ("14:45" ✓), 개발 raw r4e3 12:12:03–14:27:24 · r8e3w 20:11:03–20:19:33 (로그 20:07–20:27 ✓), `select_dev_cold.out` (t2_wtE3) 19:59:02 · `_final.out` 20:35:03 (warm 끝 20:27 뒤 ✓) | `git log`, `date -r`, 로그 | 22 | **2 건 1 분 차** → N1 (§5 "실행 커밋 14:28 CDT" · DECISIONS:447 "test 시작 14:28 CDT"; v2.2 "20:0x CDT") |
| 순서 규칙: 규칙 커밋 v2 (12:09:02) < 개발 첫 청크 (12:12:03) < cold 끝 (19:40) < v2.2 커밋 (19:59:01) < cold 선택 출력 (19:59:02) < warm (20:07–20:27) < final 선택 (20:35) < §5 커밋 (10-18 13:52:44) < v2.3 · FREEZE (14:23) < 실행 커밋 (14:29:07) < test 첫 청크 (14:33:57) < 끝 (14:45:13) < §6 커밋 (15:54:57) | 위 시각 | 1 | **재현** |
| FREEZE 뒤 동결 절 불변: `git diff -U0 d6a76fbf HEAD -- <등록>` = §5 의 "실행 커밋" 1 줄 + §6 24 줄 추가뿐; v2 (d3993c8d, 개발 BLER 전 커밋) → FREEZE 는 제목의 판 번호 · 머리말 3 줄 (v2.1–2.3) · §5 12 줄뿐 — **§0–§3 · §1.2 규칙은 v2 이후 바뀐 줄 없음**; `select_dev.py` v2 → v2.2 변경은 무결성 검사 (청크 모양 · 미완 후보 · warm = TOP2 · NaN 동등) 뿐 (지표 · 동률 규칙 불변), fe7e911b 이후 변경 없음 | `git diff` | — | **재현** |
| 코드 동일성: `git diff d6a76fbf 13f05fb1 -- conf/code Demo` 0 (§6.1); 개발 실행 커밋 셋 `d3993c8d` = `79ea962c` = `fe7e911b` (conf/code · Demo 0 바이트, §5); FREEZE 가 HEAD 조상; `run_sbl32.sh` · `eval_accept.py` · `pair_baselines.py` · analysis 계열은 13f05fb1 이후 변경 없음 | git | 5 | **재현** |
| 실행 창 (14:29:07 → 14:45 CDT) 안의 main 커밋: 없음 (다음 커밋 9b5ec869 15:54:57; 어느 브랜치에도 그 창의 커밋 없음) | `git log --all --since/--until` | 1 | **재현** |
| `sbl32_s5.txt` = §5 (FREEZE d6a76fbf · SPARSE 4,3,1,1 · WGB 7.0 · ALD 25a4152e…cf46 · PILT a901fa5c…79db) = 실제 sha256 (main 복사본 · t2_wtS 원본 모두); fits 폴더 2 파일 · 링크 아님 · sha d572e0ac…e215 · 2d72a434…f569; `logs/run_sbl32.log` 7 줄 (start resume=0 → runner exit 0 → accept_eval · accept_raw · pairB · pairB_bstar OK → `SBL32_DONE ok=4 fail=0`), 체인 로그 SBL32 14:29 → 14:45 exit 0 | `sha256sum`, 파일 | 12 | **재현** |
| 기록 줄: DECISIONS:447 (실행 커밋 · 시작) · :451 (결과), EXPERIMENTS:85, WORK_QUEUE:28 의 수치 (651:19, 325:3 · 216:10 · 110:6, +3.14 [+2.78, +3.54], R_X 0.552 [0.519, 0.587], 실패 7 개, 104:377 · −0.85 [−1.16, −0.62], 14 개 전부 (i), 예측 3/4, 16.0 min, 워커 96, 재개 없음, 커밋 13f05fb1 · FREEZE d6a76fbf, 시행 0..2559 · 개발 3840..4159 · B 2000, 로그 경로 4 개 존재 · 추적, 잠금 ID Demo 3b5c0a375509 = `LOCKED.md:7`) | §6 · 원자료와 대조 | ≈ 40 | **재현** (시각은 N1) |
| §6.2 "SCALE16e4 기록과 줄 단위 대조" 문장: `diff t2_wtS/…/pairB_U28NR32B16e4.txt pairB_U28NR32SBL.txt` → 머리 줄 (셸 머리말 · `# R0-pilot read at @1`) · R0-pilot@1 ↔ R0-pilot 행 (903:0 +6.25 dB ↔ 575:7 +4.56 dB, 둘 다 (i); 표의 실패 · NMSE 행 포함) · SBL-loop 행 · 요약 수 12 → 13, 13 → 14 뿐 | `diff` | 1 | **재현** (문장 그대로) |
| 라벨 문장 = §2.1 틀 ("UMi 32×4 에서 loop BLER 로 조정한 SBL-loop (ρ = 4, n_em = 3, cold) 대비 V1 이 적게 실패") + §1.2 5 의 "[조사 범위 끝: <축>, <사유>]"; 금지 문구 ("최적 SBL", "SBL 로는 부족", "동등", "비열등") §6 · DECISIONS · EXPERIMENTS · WORK_QUEUE 줄에 없음 (§2.2 의 규칙 문장에만 등장) | grep · 읽기 | — | 통과 |
| **test / 개발 분리**: 네 트리 (`t2`, `t2_wtS`, `t2_wtE3`, `t2_wtE5`) 의 모든 `raw_*` 가운데 UMi28 C9 32×4 청크에 SBL/OMP arm 을 가진 것 = test `raw_U28NR32SBL` (0..2559) · 개발 10 개 (3840..4159) · 스모크 `raw_U28NR32SBLdev` (4160..4199) · 병합 확인 `raw_U28NR32SBLmrg` (4160..4199) 뿐 → 시행 < 2560 에 SBL arm 이 있는 raw 는 test 실행 하나; 개발 raw 는 전부 ≥ 3840 (DEV_SKIP0 2560 이상); 프로브 · 스트림 확인은 개발 시행 2560 (BLER 미출력 · 수신기 미호출, `probe.out` · `verify_stream_sbl32.out`) | 청크 키 · 파일명 스캔 | 13 raw | **재현** (이 셀의 test 시행은 test 실행 전에 SBL 에 쓰이지 않았다 — 파일 기준) |

합계: 자동 비교 **442 값 중 0 불일치** (genie 대조 6,074,880 값은 1 항목으로 셈), 도구 재실행 3 파일 바이트 동일, 수동 대조 (git · 시각 · 기록 줄 · sha) 약 90 값 중 **시각 2 건 (1 분 차)** 외 불일치 없음.

## 2. 규칙 재적용 (§1–§2 를 재계산 값에)

- **판정점 (앵커 SBL-loop)**: BLER@16 = 0.9852 (−12, > 0.9 제외) · 0.692 · 0.382 · 0.262 · 0.151 · 0.068 · 0.032; \|log10(BLER/0.1)\| = 0.840 (−9) · 0.583 (−6) · **0.418 (−3)** · **0.178 (0)** · **0.168 (+3)** · 0.489 (+6) → 판정점 −3 / 0 / +3 dB (기록 일치; b\* 판정점과 같다).
- **부호검정 · power guard · 2/3 규칙**: 불일치 쌍 328 · 226 · 116 (모두 ≥ 6, 3 점 → POWERED); V1 적게 실패 (a > b, p < .05) 3/3 ≥ 2 → **(i) "V1 이 SBL-loop 보다 적게 실패"**. 문장 "UMi 32×4 에서 loop BLER 로 조정한 SBL-loop (ρ = 4, n_em = 3, cold) 대비 V1 이 적게 실패" + "[조사 범위 끝: ρ · n_em, …]" — ρ 4 ∈ {4, 16}, n_em 3 ∈ {3, 25} 이므로 §1.2 5 에 따라 꼬리표 필수 → §6.2 의 라벨 · 문장과 같다.
- **SNR@0.1 격차**: 첫 하향 교차의 log-선형 보간, SBL-loop − V1 = +3.14 dB, 90 % paired bootstrap [+2.78, +3.54], censored 0 % (격자 안) — 기록과 같다.
- **보고 전용 b\* → SBL-loop**: 앵커 b\* 판정점 −3/0/+3; b\* 만 실패 104 : SBL-loop 만 실패 377; b\* 적게 3/3 — §1.3 대로 라벨 없이 방향만 적음 (기록 일치).
- **개발 선택 (§1.2 3–5)**: 지표 = F 합 / 960; r4e3 142 최소; r8e3 = r16e3 동률은 프로브 시간으로 r8e3 앞; warm 두 변형 (146 · 147) 이 cold 최소 142 를 이기지 못함 → cold 선택; 범위 끝 두 축 → "[조사 범위 끝: ρ, n_em]" — `select_dev_*.out` · §5 와 같다. 시간 선별은 BLER 과 무관한 프로브 값으로 (16, 25) 만 제외.
- **예측 채점 (§3)**: 1 빗나감 · 2 적중 · 3 적중 · 4 적중 — §6.3 과 같다. 관대한 채점 없음.

## 3. 발견

### MUST-FIX
없음 — §6 의 수치 · 판정 · 라벨 · 채점 가운데 틀린 것을 찾지 못했다.

### SHOULD-FIX
없음 — 기록 사실의 오류 · 누락을 찾지 못했다.

### NIT

**N1 · 시각 2 건이 커밋 시각과 1 분 다르다 (기록 사실; 판정 · 수치 무관).**
- `NEXT_EXPERIMENTS_U28NR32SBL.md:97` "**실행 커밋 (2026-10-18 14:28 CDT, main)**" 과 `conf/DECISIONS.md:447` "`[2026-10-19 04:28 KST] … 실행 커밋 · test 시작 (… 2026-10-18 14:28 CDT)`": 실행 커밋 13f05fb1 의 시각은 **14:29:07 CDT** (`git log -1 --format=%ci 13f05fb1` = 04:29:07 +0900), test 시작은 `logs/run_sbl32.log:1` **14:29 CDT**. 14:28 은 `sbl32_s5.txt` 를 쓴 시각 (mtime 14:28:22 CDT) 이다. EXPERIMENTS:85 · WORK_QUEUE:28 은 14:29 로 맞다. 제안: §5 "실행 커밋 (… 14:29 CDT 커밋; s5 작성 14:28)", DECISIONS:447 은 덧붙임 줄로 "커밋 · 시작 14:29 CDT".
- `NEXT_EXPERIMENTS_U28NR32SBL.md:8` "**v2.2 (2026-10-17 20:0x CDT …)**": 이 줄 자체가 커밋 fe7e911b 에 들어 있고 그 커밋은 **19:59:01 CDT** (`logs/sbl32_dev.log:18` 의 19:59 CDT 줄도 git fe7e911b). 제안: "19:59 CDT".

**N2 · `NEXT_EXPERIMENTS_U28NR32SBL.md:16` (§0 비용 프로브) "최대 RSS 0.88–1.18 GB"** — `probe.out` 의 값은 878.0–1177.0 **MiB** (= 0.92–1.23 GB, 0.86–1.15 GiB); 적힌 수는 MiB 를 1000 으로 나눈 것. §0 은 판정에 쓰지 않고 G 는 §5 의 스모크 (6.580 GB) 로 따로 정했으므로 영향 없음. 제안: "878–1177 MiB".

### 그 밖에 확인한 것 (변경 불필요)
- §6.1 의 절차 편차 ("두 등록 문서 수정 금지" 중 §6 초안 작성, 14:47 CDT) 는 §6.1 · DECISIONS:451 에 공개돼 있고, SBL32 는 재개 없이 끝났으며 `run_e5.sh` 는 E5 문서만 본다 — 결과 영향 없음 (기록 그대로).
- `--r0` 기본값 (at16) 으로 R0-pilot 행이 SCALE16e4 기록 (at1) 과 다른 점은 §6.2 에 공개돼 있고 `SBL-loop → V1` 과 무관하다.
- 회귀 `SBL32REG4` · `SBL32REG5OFF` (`t2_wtE3`) 는 UMi28 **C2 8×4** test 시행 0..39 의 기존 SPARSE16e4 청크를 다시 돌려 비트 대조한 것 (§4 에 적힘) — 이 셀 (C9) 의 test 시행이 아니고 튜닝도 아니다.
- 등록 §1.3 "V1 · b\* 등은 기존 raw 재사용": base · PIL · ALD raw 모두 `run|git` b4433d3c 하나, V1 체크포인트 id sha256[:16]=463da87aa8dbfb61 role=best 32x4.

## 4. 검증하지 못한 것
- §5 의 MemAvailable 1003263876 kB (일시적 값), tmux 세션 이름 (`e3e5` · `sblsmoke`), 사용자 승인 (개발 CPU NUMA 0; 19:59 CDT 의 E5 runner 감지 ABORT 뒤 20:07 warm 시작 순서) — 파일로 확인 불가.
- "개발 · test BLER 미열람" 은 작성자 상태 주장이라 파일로는 순서만 확인했다: 규칙 커밋 (12:09) < 개발 raw, v2.2 커밋 (19:59:01) < cold 선택 출력 (19:59:02), §5 커밋 (13:52) < test 실행 (14:29). 모순되는 파일은 없다.
- DECISIONS:451 의 "verifier 결함 0 (추가 확인 2 · 선택 1)" — verifier 산출물 파일이 `reviews/` 에 없어 내용은 확인하지 못했다 (반영했다는 두 항목은 §6.2 문장에 들어 있다).
- 부트스트랩 CI 는 (a) 같은 시드 · 재표집 순서를 따로 구현해 문자열까지 일치, (b) 등록 도구 재실행 바이트 동일, (c) 다른 시드로 [+2.79, +3.53] 까지 확인했다. 다른 RNG 로 같은 자리수를 재현하는 것은 정의상 불가능하므로 하지 않았다.
- 스모크의 6.580 GB · 108 s, 프로브의 블록 시간은 로그 · json 값을 옮겨 확인했을 뿐 다시 재지 않았다 (수신기 실행 금지).
- Codex 교차 검토 파일 (`reviews/20261019-035934-…`, `…-041514-…`) 의 내용은 이 감사 범위 밖 (존재 · 커밋 포함만 확인).

## 5. 결론
- **§6.2 의 라벨 (i) 와 모든 인용 수치는 §1–§2 동결 규칙을 raw 에서 다시 적용해 재현된다** (판정점 −3/0/+3, 651:19, POWERED 3/3, +3.14 dB [+2.78, +3.54], R_X 0.552 [0.519, 0.587]; 보고 전용 b\* → SBL-loop 104:377, −0.85 dB [−1.16, −0.62]; 14 개 전부 (i); NMSE 표).
- **§5 의 개발 선택 (ρ 4, n_em 3, cold, 범위 끝 ρ · n_em) 은 §1.2 규칙을 개발 raw 에 다시 적용해 재현되고, 개발 · 스모크 · 병합 확인은 모두 시행 ≥ 3840 (test 와 분리) 이다.**
- **§6.3 채점 4 항목은 데이터에서 재현된다** (빗나감 · 적중 · 적중 · 적중).
- 동결 §0–§3 은 v2 (개발 BLER 전) 이후 바뀐 줄이 없고, FREEZE → 실행 커밋의 코드 차이 0, 실행 창 안 main 커밋 없음, 수용 검사 (genie 448 청크 전 시행 비트 동일 · run\|git · meta\|sparse) 재현.
- 고칠 것은 시각 1 분 차 2 건 (N1) 과 §0 의 단위 1 건 (N2) 뿐이며, 수치 · 판정 · 채점을 바꾸는 발견은 없다.
