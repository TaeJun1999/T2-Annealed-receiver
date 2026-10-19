# 기록 감사 — NEXT_EXPERIMENTS_U28NR32GCAP.md §5 · §6 (E2′ UMi28 C9 32×4 GMM 용량 확인, 태그 U28NR32GCAPe / U28NR32GCAPchk)

- 감사자: Claude Code (Fable 5.1 서브에이전트, 독립 기록 감사; 공통 절차 `gcap/PROMPT_SERVER_COMMON.md` §3 의 "기록 감사 1 회"). 감사 시각 2026-10-19 08:47 ~ 09:05 CDT (= 10-19 22:47 ~ 23:05 KST; `date` 로 읽음).
- 감사 대상 판: 작업 트리 = HEAD **9a2c9fd4** (등록 문서 · `gcap/gcap_s5.txt` 는 HEAD 와 같음, `git diff --quiet` 0). 실행 커밋 **64b2912f** (= `gcap_s5.txt` 를 만진 유일한 커밋), FREEZE **778bda1d**. 동결 §0~§4 는 778bda1d → HEAD 에서 **바뀐 줄 없음** (`git diff -U0 778bda1d HEAD -- <등록>`: 삭제된 줄은 §5 자리표시 한 줄뿐, 추가는 §5 · §6 만).
- 방식: 읽기 전용. 새 파일은 이 폴더 (`prereg_audit_2026-10-19/`) 에만: `recompute_gcap.py` → `recompute_gcap.out` (numpy 로 청크 · fit 직접 읽기; `analysis` · `gcap_compare` · `recovery_ci` · `Demo/` 미임포트; 부호검정 `math.comb`, 판정점 · SNR@0.1 보간 · R · 부트스트랩 자체 구현), `fitfields_gcap.py` → `fitfields_gcap.out` (fit npz 의 스칼라 필드; `covs` 미적재), `recompute_malloctest_gcap.out` (§6.4 개발 대조 재실행), `rerun_compare_U28NR32GCAP.txt` · `rerun_compare_GCAP_diff.txt` (등록 도구 `gcap_compare.py` 를 `--out` 만 이 폴더로 바꿔 재실행 → 커밋본과 diff), `rerun_accept_GCAPe.txt` · `rerun_accept_GCAPchk.txt` (`eval_accept.py` §1.3 원문 인자, stdout 만 이 폴더로). CPU `nice -n 10 taskset -c 2-5`, GPU 미사용 (`CUDA_VISIBLE_DEVICES=`), 수신기 · 등록 실행 스크립트 미실행. git 상태 · 기존 파일 변경 없음 (삭제 명령 없음; 이 폴더의 빈 보조 파일 2 개는 `mv` 로 GCAP 이름으로 바꿈).

## 1. 재계산한 것과 재현 여부

| 항목 | 방법 | 검사 값 수 | 결과 |
|---|---|---|---|
| raw 청크 계획: `raw_U28NR32GCAPe` 448 = 7 SNR × {(40k, 40): k = 0..63}, 기존 `~/t2_wtS/conf/raw_U28NR32B16e4` 448 같은 계획, `raw_U28NR32GCAPchk` = {0 dB (0, 40)} | 파일명 파싱 | 2 × 7 + 1 | **재현** (구멍 · 중복 없음; `\|failed` 키 없음; 어느 청크에도 빠진 키 없음; blk_err 전부 유한 · {0, 1}, shape (2560, 16)) |
| 새 raw meta/run 값 집합: `run\|git` {64b2912f} ("+dirty" 없음) · `meta\|bstar` {kron} · `kron_K` {8192} · `ll_val\|kron` {154.13990347772582} · `ntrain` {160000.0} · `worker_gb` {13.5} · `em_sec` {40544.76968383789} · `run\|seed` {20260926} · `iters` {16} · `dtype` {complex128/float64} · `stagec_ckpt_id` {sha256[:16]=463da87aa8dbfb61 epoch=232 best_epoch=232 role=best 32x4} · `meta\|jobs` {58: 116, 55: 332} | 448 청크 전부 | 12 | **재현** (§6.1 수용 · raw 행 전부) |
| 기존 raw: `run\|git` {b4433d3c}, `kron_K` {4096}, `ll_val\|kron` {152.23176788511105}; 새 청크마다 `run\|seed/iters/beta/t_in/dtype/n/skip/snr` 가 같은 이름의 기존 청크와 동일 | 448 쌍 | 3 + 448 × 8 | **재현** |
| R5-genie 비트 동일 (새 ↔ 기존, 448 청크 × `R5-genie\|*` 8 키 = 3584 배열, NaN 동등) | `array_equal` | 3584 | **재현** (차이 0) |
| chk (0 dB, 시행 0..39) ↔ 기존 청크: 데이터 키 집합 동일, 11 arm × 9 키 = 99 배열 비트 동일; `run\|git` 64b2912f, `kron_K` 4096, `ll_val` 152.23176788511105, `run\|snr` 0.0 | 직접 | 99 + 5 | **재현** |
| 실패 수 / 2560 × 7 SNR: b\*(GCAP) 2277 · 1196 · 746 · 505 · 294 · 143 · 61, V1 2219 · 1068 · 595 · 349 · 180 · 70 · 27, genie 846 · 423 · 227 · 88 · 30 · 9 · 3, b\*(기존) 2280 · 1207 · 761 · 509 · 304 · 145 · 62 | numpy 직접 | 28 | **재현** (§6.2 · compare 파일) |
| 판정점 (§1.3 규칙: 앵커 BLER@16 이 [0.005, 0.9] 안에서 \|log10(BLER/0.1)\| 최소 3 점): 앵커 b\*(GCAP) → −3/0/+3 (\|log10\| 0.295 · 0.060 · 0.253; 다음 −6 0.464), 앵커 b\*(기존) → −3/0/+3, 앵커 genie → −9/−6/−3 | 직접 | 3 | **재현** |
| 짝 부호검정 a:b · exact 양측 p (`%.2g`): b\*(GCAP)→V1 172:16 3.4e-34 · 127:13 1.1e-24 · 79:6 2.4e-17, pooled 378:35 8.3e-74; b\*(기존)→V1 173:13 7.3e-37 · 136:12 9e-28 · 82:7 2.4e-17, 391:32 1.3e-79; b\*(GCAP)→genie 774:1 · 520:1 · 419:2, 1713:4; b\*(기존)→genie 784:0 · 534:0 · 422:1, 1740:1; V1→genie 646:1 · 372:4 · 263:2, 1281:7 | `math.comb` 직접 | 5 쌍 × (3 a:b + 3 p + pooled) | **재현** (p 문자열까지 일치) |
| 검정력 가드 (3 판정점 ∧ 불일치 쌍 ≥ 6 이 ≥ 2 점) · 2/3 규칙: 5 쌍 모두 POWERED, "second arm fewer" 3/3 | 규칙 재적용 | 5 × 2 | **재현** → b\*(GCAP)→V1 **(i)** |
| SNR@0.1 (log-linear, 첫 하향 교차): b\*(GCAP) +0.576, V1 −1.596, genie −6.580, b\*(기존) +0.696 → 격차 +2.17 · +2.29 · +7.16 · +7.28 · +4.98 dB, censored 0 % | 자체 구현 | 5 | **재현** |
| 격차 90 % paired bootstrap: 등록 도구 재실행 (`gcap_compare.py --out` 이 폴더) → 커밋본 `gcap/compare_U28NR32GCAP.txt` 와 **바이트 동일** (diff 0 바이트); 자체 부트스트랩 (B 2000, 다른 seed) b\*(GCAP)−V1 [+1.83, +2.51], b\*(기존)−V1 [+1.96, +2.60] — 기록 [+1.83, +2.50] · [+1.98, +2.61] 과 0.02 dB 안 | 재실행 + 자체 | 1 파일 + 4 | **재현** |
| R (판정점 합): ΣF 942 · 599 · 127 → 343/815 = 0.420859; 기존 958 · 599 · 127 → 359/831 = 0.432010; 자체 paired bootstrap (다른 seed) [0.388, 0.454] · [0.400, 0.462] — 기록 [0.390, 0.451] · [0.402, 0.462] 과 0.003 안; 기록본 `recovery_U28NR32B16e4.txt` pooled 0.432 [0.402, 0.462] | 직접 + 자체 | 8 | **재현** |
| 보고 전용 b\*(기존)→b\*(GCAP) 7 점: 38:35 0.82 · 56:45 0.32 · 57:42 0.16 · 57:53 0.78 · 56:46 0.37 · 30:28 0.9 · 13:12 1; 실패 수 차 3 · 11 · 15 · 4 · 10 · 2 · 1 (모두 1–15, 새 쪽이 적음), 최소 p 0.16 | 직접 | 7 × 3 + 2 | **재현** (DECISIONS 445 "1–15 블록 적게 실패, 점별 p ≥ 0.16" 포함) |
| 수용 검사 `eval_accept.py` 두 호출 (§1.3 원문 인자) | 재실행 | 2 | rc 0, `ACCEPT: OK -- U28NR32GCAPe` · `-- U28NR32GCAPchk`, 커밋본과 바이트 동일 |
| fit 파일 필드 (§5 표): A ll_val 152.23176788511105 · it_best 30 · n_iter 31 · reseed 29980 · sec 10420.08 · cand_ll_val 3 개 · 학습 LL 31 개 (§0, 소수 6 자리) · ll[30]−ll[29] = −1.50e-4 · train−val 36.05; B ll_val 152.34773499788244 · it_best 10 · `stop budget` · `status completed` · steps 50/50 · reseed 50745 · n_tk_eye 1015 · sec 4602.19 · seed [20260926, 2, 9, 8, 32, 1, 4096, 0, 0, 1] · 궤적 6 점 · src sha 2d72a434…; C r0/r1/r2 ll_val 153.30391084218408 / 153.86125655672217 / 154.13990347772582 · n_iter 71 · it_best 30 · reseed 238991 / 234748 / 238023 · sec 12837.02 / 12813.70 / 12794.05 · `stop patience` × 3 · 궤적 8 점 × 3; 병합 restart 2 · ll_train 209.52733621460857 · train−val 55.387 · sec 38444.766 · cand_stop patience × 3 | npz 스칼라 직접 | ≈ 95 | **재현** (`fitfields_gcap.out`) |
| 적합 비용: 기존 격자 = 병합 15 파일 `sec` 합 128781.04; K8192 세 재시작 합 38444.77 → 38445; 합 167226; raw `em_sec` = 38444.76633501053 + fullK32 2100.003348827362 = 40544.76968383789 (repr 일치); chk manifest `em_sec` 12520.085 = kronK4096 10420.082 + 2100.003 | 직접 | 6 | **재현** |
| K 격자 ll_val (§0): kron 16 25.21 · 32 63.45 · 64 93.53 · 128 116.40 · 256 134.06 · 512 143.62 · 1024 148.95 · 2048 150.39 · 4096 152.23, full 최고 K128 80.06, full32 54.03 | fit 파일 | 11 | **재현** |
| sha256: 선택 fit d883afaf…f71b (GCAP 병합 = GCAPe 복사본 = GCAPdev 복사본), fullK32 d572e0ac…e215 (3 폴더), 기존 kron4096 2d72a434…f569 (원본 = GCAPchk 복사본), B 500ec2b9…, C r0/r1/r2 e9dc698d… / 7495ebe5… / f271bb04…, 체크포인트 463da87aa8dbfb61 (epoch 232 · best_epoch 232 · role best · rung D2SXUMi28NR32160000 · split_hash 01735b4ef4b87ff8, `torch.load(cpu)`), 프롬프트 사본 0c3feb4e…ac4b · d74abe6e…f7c7; 세 fits 폴더 각 2 파일 · 심볼릭 링크 아님 | `sha256sum` · `ls -la` | 16 | **재현** |
| 선택 (§1.2): B best 상태 10 > 0 → 별개 후보; argmax ll_val = C (154.1399 > 152.3477 > 152.2318); `select_gcap.py` 는 `ll_val` · 상태 · 정지 사유만 읽음 (BLER · `ll_test` 미사용 — 코드 확인); 예측 1 Δ +0.1160, 예측 3 +1.908 | 직접 | 5 | **재현** |
| 시각 (CDT ← KST 파일 mtime · 로그): manifest 커밋 09d2ea69 23:27:21 (10-16) < B 시작 23:27:25 (GPU 1) < C r0 23:36:37 (GPU 0) < r1 · r2 23:40:46 (GPU 2 · 3) < FREEZE 778bda1d 10-17 00:31:58 < B 끝 00:58:34 (파일 00:58:32) < C r0 03:36:30 · r2 03:39:13 · r1 03:39:33 < 병합 04:32:02 → 04:57:54 < 복사본 fullK32 · kron4096 04:32:33 · kron8192 04:58:35 < select 출력 04:58 < 스모크 끝 07:37:19 (wall 9504 s) < 실행 커밋 64b2912f 07:39:54 < 실행 1 시작 07:40 → chk 끝 (9759 s) → INTERRUPTED 22:33 → 재개 22:34 → 끝 10-18 12:49 (manifest `written` 02:49:13 KST) < §6 커밋 5d747901 13:58:48 (§6.1 "기록 13:44") | `date -r` · `git log` · 로그 | 22 | **재현** (모두 순서대로) |
| 실행 창 (10-17 07:40 → 10-18 12:49 CDT) 안 main 커밋: `main` 브랜치 reflog 와 main 워크트리 `HEAD` reflog 모두 64b2912f (07:39:54 CDT) 다음이 5d747901 (10-18 13:58:48 CDT) — **없음**; 같은 창의 브랜치 커밋 (e3-sbl32 · e5-qam16, 워크트리) 은 main 밖, 병합은 10-18 14:23 CDT (창 뒤) | git | 2 | **재현** (§6.1 "실행 내내 main HEAD = 64b2912f") |
| FREEZE 뒤 code/ · Demo/ 불변: `git diff 778bda1d 64b2912f -- conf/code Demo` 0 바이트; 09d2ea69..778bda1d 의 code/ 변경 = `gcap_compare.py` · `run_gcap.sh` 뿐 (§5 서술과 일치, 적합 경로 불변); FREEZE 와 HEAD 의 DECISIONS 에 동결 줄 | git | 3 | **재현** |
| E 로그 (`run_D2_U28NR32GCAPe.log`, 619 행): 머리 2 개 (1 행 07:40 resume=0, 144 행 22:34 resume=1); `done` 116 + 332 = 448, 재개 때 `exists` 116; 실행 1 평균 19995 · 중앙 19611 · 8061–37745 s, 실행 2 평균 7954 · 중앙 7260 · 6524–13125 s; 첫 회전 (1–58) 중앙 9746, 둘째 회전 (59–116 = E:67–124) 24753–37745 · 중앙 30816 · 2.54–3.87 배; `E:7` 워커 58, `E:150` 워커 55, `E:600` "finished in 854.4 min", `E:125–143` · `E:601–619` KeyError 'R2-ours-G' (analysis.py:321 `gain(… REF)`, REF = analysis.py:100); 벽시계 14 h 53 + 14 h 15 = 29 h 08 | 로그 파싱 | 24 | **재현** (§6.1 시간 행, §6.4 수정값, DECISIONS 443 "24.8–37.7 ks, 중앙 30.8, 2.5–3.9 배") |
| `run_gcap.log` 110 행: `G:1` start, `G:2` INTERRUPTED, `G:3` e 130 chk 0, `G:4–16` (accept_e FAILED · accept_chk OK · run_git FAILED · manifest 2 OK · guard OK · compare NOT RUN · analysis FAILED · `GCAP_DONE ok=4 fail=5`), `G:18` start resume=1 WGB 13.5 (used 13.5), `G:19–29` 전부 OK, `G:108` compare OK, `G:109` analysis FAILED, `G:110` `GCAP_DONE ok=7 fail=1` | 읽기 | 16 | **재현** |
| 메모리 가드 (§1.3 · §5): G = ⌈12.613 × 1.05 / 0.5⌉ × 0.5 = 13.5; 워커 ⌊0.8 × 1037860916 kB / 2²⁰ / 13.5⌋ = 58; 스모크 = 개발 청크 skip 2560 (`rss_smoke.py` `--skip0 2560`; raw_U28NR32GCAPdev 의 `run\|skip` 2560, `run\|git` 778bda1d) | 직접 | 4 | **재현** |
| §6.4 할당기 대조 (개발 시행만): MTa (기본) ↔ MTb (환경변수) 시행 4300..4302 (`run\|skip` 4300, n 3, 0 dB, git 64b2912f) 17 배열 비트 동일; MTc (환경변수, skip 2560 n 3) ↔ GCAPdev 스모크 청크 0..2 행 17 배열 비트 동일; a/b 로그 3003 / 934 s · utime 556 / 579 · stime 2431 / 350 · RSS 12.57 / 12.91 GB · b 의 env GLIBC_TUNABLES 표시; MTC_DONE 22:31 · MALLOCTEST_DONE 22:29 (재개 22:34 전); raw 에 환경변수 키 없음 | 재실행 (`recompute_malloctest_gcap.out`) + 로그 | 34 배열 + 12 | **재현** |
| test / 개발 분리: 선택은 ll_val (검증 stream 8) 만; 스모크 · MT 는 시행 2560 · 4300 (개발); chk 는 등록된 회귀 검사 (test 0..39, 기존 raw 와 비트 대조, 조정 없음); 선택 (04:58 CDT) 이 첫 test 청크 (07:40 CDT) 보다 앞; 스모크 로그의 진행 줄은 genie BLER 만 | 기록 · 코드 | — | 위반 없음 |
| 기록 줄 수치: DECISIONS 437 · 439 · 443 · 445 · 457, EXPERIMENTS 83, WORK_QUEUE 3 · 30 · 61 의 ll_val · sha · 판정점 · a:b · 격차 · R · ΣF · 시각 · 커밋 · 워커 수 · 청크 수 · GCAP_DONE | 대조 | ≈ 45 | **1 건 불일치** → S1 (EXPERIMENTS chk SNR) |
| §6 · 기록 줄의 금지 문구 (§2.3): "해소" · "수렴했다" · "동등" · "비열등" · "scaling law" · "비긴다" 없음; "최적 GMM" 은 등록 한정어 G_GCAP 의 "최적 GMM 이 아니다" 로만 | grep | — | 통과 |

합계: 자동 비교 **235 항목 (배열 3584 + 99 + 34 포함) 중 0 불일치**, 도구 재실행 3 파일 바이트 동일, 수동 대조 약 170 값 중 **1 건 불일치** (기록 줄, 아래 S1).

## 2. 규칙 재적용 (§1 · §2 → §6)

- 판정점: 앵커 b\*(GCAP) 자동 선택 −3/0/+3 (재현). 2/3 규칙: 3 점 모두 a > b, p < .05 → "second arm fewer failures 3/3". 검정력 가드: 3 판정점, 불일치 쌍 188 · 140 · 85 ≥ 6 → POWERED. → §2.1 **(i)** "UMi28 C9 (Nr 32) 에서 V1 이 b\*(GCAP) 보다 적게 실패 (GMM 용량 확인 재평가, UNGATED)" — §6.2 라벨 문자열과 글자까지 같음.
- 한정어: 최종 = C (K8192, 격자 끝) → G_GCAP 문자열 (§2.1 원문과 동일) + "[K 상한 민감: 외삽 불가]" **유지** (§2.1 첫 경우) — §6.2 · DECISIONS 439 · 445 일치. Q-K 재계산 없음 (§1.6).
- SNR@0.1 격차: 두 arm 모두 격자 안 교차 ("ok") → censored 아님 — "+2.17 dB [+1.83, +2.50]" 그대로.
- 선택 규칙 §1.2: 엄격한 argmax, B 는 best 상태 10 > 0 이라 후보 — 재현. 최종 ≠ A → §1.3 test 평가 (맞음). `gcap_s5.txt` 의 `FIT C 8192 <ll_val repr> <sha>` 가 선택 출력 · 파일 sha 와 일치; 스크립트가 거부하는 경우 (A 선택) 아님.
- 수용 조건 §1.3: 주 · chk ACCEPT OK + run\|git 449 청크 = HEAD (재실행 · 직접 확인) → 표 B 를 결과로 쓰는 조건 충족. `runner.py analysis` 실패는 §1.3 "사후 산출물" 행의 기록용 단계이고 표 B · R · 라벨은 `gcap_compare` 출력에서만 읽는다 (§1.3 분석 행) — 결과에 영향 없음 (compare 재실행 바이트 동일로 재확인).
- 예측 채점 (§3 → §6.3): 1 적중 (상태 10 > 0, Δ +0.1160 ∈ (0, 1.0]) · 2 적중 (`budget` · `completed` · 50/50) · 3 적중 (+1.908) · 4 적중 (`patience` × 3, `tol` 없음) · 5 적중 (C ≠ A) · 6 적중 (−3/0/+3, (i)) · 7 적중 (942 ∈ [910.1, 1005.9]) · 8 적중 (+2.17 ≥ +1.5). 관대한 채점 없음 — 8 개 모두 동결 문구의 수치 조건으로 채점됐다.
- 이탈 공개: 재개 명령의 glibc 할당기 환경변수 3 개는 §6.1 (등록 이탈 표시) · §6.4 (사유 · 증거 범위) · §6.5 (사용자 수용) · DECISIONS 443 · 457 · EXPERIMENTS 83 (명령줄 원문) · WORK_QUEUE 대기 9 에 같은 내용으로 적혀 있다. 증거 범위 서술 ("b\* 의 불변은 개발 시행으로만 확인, genie 는 448 청크 비트 동일") 이 재계산과 맞다 (개발 6 시행 × 17 배열, genie 3584 배열).

## 3. 발견

### MUST-FIX
없음 — §6 의 수치 · 판정점 · 라벨 · 구간 · R · 채점 가운데 틀린 것을 찾지 못했다.

### SHOULD-FIX

**S1 · `docs/EXPERIMENTS.md:83` "chk (`U28NR32GCAPchk`, −12 dB 청크 0, 11 arm, 기존 kronK4096)" — chk 는 0 dB 다.**
- 근거: `conf/raw_U28NR32GCAPchk/D2_C9_UMi28_Nr32_T16_Tp4_eig_snr0_skip0_n40.npz` (파일 하나, `run\|snr` 0.0), `conf/code/run_gcap.sh:62` `--snr 0`, `run_manifest_U28NR32GCAPchk.json` `"snr": "0.0"`, 등록 §1.3 "0 dB (판정점 가운데 …; 선례는 격자 첫 SNR)", §6.1 "`raw_U28NR32GCAPchk/` 1 npz". 비트 대조 (99 배열) 도 0 dB 기존 청크와 했다.
- 재현: `ls conf/raw_U28NR32GCAPchk/`; `grep -n "snr" conf/results/review_next/run_manifest_U28NR32GCAPchk.json`.
- 교체: `chk (\`U28NR32GCAPchk\`, 0 dB 청크 0 (시행 0..39), 11 arm, 기존 kronK4096)`. 판정 · 수치에 영향 없음 (기록 사실만).

### NIT

**N1 · `docs/EXPERIMENTS.md:83` "bootstrap B 2000 seed 20260926"** — 20260926 은 R 의 paired bootstrap seed (`recovery_ci.boot`; 등록 §1.3 · §6.2 대로) 이고, SNR@0.1 격차의 90 % paired bootstrap 은 `Demo/exp_0925_analysis.py:64` 의 `default_rng(20260925)` 를 쓴다 (등록 §1.3 은 격차 쪽 seed 를 적지 않았다). 교체 제안: `bootstrap B 2000 (SNR@0.1 격차 seed 20260925 = exp_0925.gain, R seed 20260926)`. 재현 세부만의 문제.

**N2 · EXPERIMENTS 83 · WORK_QUEUE 30 "verifier 2 회 (결함 4 + 1 반영)"** — 그 verifier 검토의 결함 목록 · 반영 내용이 저장소 어디에도 없다 (§6.4 머리말의 "수치 두 곳은 verifier 지적으로 고쳐 옮겼다" 가 유일한 흔적; Codex 교차 검토는 `reviews/20261019-035934-prompt_pretest_sbl32_e5_gcap6.md` 묶음 C 에 "확인된 추가 결함 없음" 으로 남아 있다). 이번 감사가 §6 을 전부 독립 재현했으므로 수치 위험은 없고, 기록 완전성 문제. 제안: §6 끝에 verifier 두 회의 결함 (4 + 1) 과 반영 지점을 한 줄로 덧붙이거나 검토 파일을 `prereg_reviews_*/` 에 둔다.

### 그 밖에 확인한 것 (변경 불필요)
- §6.4 가 `PENDING_DECISIONS_gcap_resume.md` 원본의 두 수치 ("MemAvailable 989 GB" → 삭제, "31–35 ks, 3.2–3.6 배" → 24753–37745 s, 2.54–3.87 배) 를 고쳐 옮겼다고 밝힌 것 — 고친 값이 E 로그 재계산과 일치하고, 원본 값은 실제로 틀리다 (989.8 GiB 이면 워커 58).
- §6.1 "runner.py analysis 는 동결 코드로 만들 수 없다" — `analysis.table_A` 가 모든 arm 의 격차를 `REF = "R2-ours-G"` (analysis.py:100) 에 대해 계산 (:321) 하므로 2 arm raw 에서 KeyError 가 필연 (두 실행 모두 같은 예외). 등록 결함의 공개로 충분하다.
- 실행 1 이 멈출 때 버린 계산 "약 58 개": 116 완료 · 58 워커 · 332 잔여 → 진행 중 58 개 — 일관.

## 4. 검증하지 못한 것
- tmux 세션 이름 (`gcap` · `gcap_rss`), 선택 출력의 "CPU 24", 재개 시점의 MemAvailable (runner 가 기록하지 않음; 55 워커는 928–945 GiB 구간에 해당), 메모리 압박의 진단치 (페이지 캐시 ≈ 430 GB, memory.pressure 65–90 %, 워커 user 0 % · sys 100 %, RSS 합계 473 → 531 → 686 GB) — 파일 기록 없음 (§6.4 가 "파일 기록 없음" 이라고 밝힌 항목 포함).
- "첫 멈춤 시도는 자동 권한 분류기가 거부" (§6.4), 사용자 발언의 시각 "22:2x–22:3x CDT" — 파일로 확인 불가.
- verifier §6 검토 2 회의 내용 (N2).
- 부트스트랩 구간: 등록 도구 재실행 (바이트 동일) 과 다른 seed 의 자체 부트스트랩 (0.02 dB · 0.003 안) 으로 확인했고, 같은 난수 스트림을 다시 구현하지는 않았다. 점추정은 모두 독립 재계산.
- fit 의 학습 · 검증 데이터가 stream 7 · 8 인지는 fit manifest 와 파일의 `ntrain` 160000 · `n_val` 5000 으로만 확인 (`fit_gpu.py` · `fit_gcap_cont.py` 의 데이터 생성 코드는 읽지 않음).
- "작성자가 선택 전 어떤 test BLER 도 보지 않았다": 파일로 검증 불가 (시간 순서와 로그의 진행 줄 (genie 만) 이 일관할 뿐).
- `lock id Demo` 는 돌리지 않았다 (LOCKED.md 7 행의 Demo ID 3b5c0a375509 와 EXPERIMENTS 83 이 일치함만 확인).

## 5. 결론
- **§6.2 라벨 (i) 와 모든 인용 수치 (378:35 · 점별 a:b · p · POWERED · +2.17 dB [+1.83, +2.50] · R 0.420859 [0.390, 0.451] · ΣF 942 · 599 · 127 · 7 SNR 실패 수 · 보고 전용 7 점 · 기존 b\* 재계산) 는 raw 에서 §1 · §2 동결 규칙을 다시 적용해 재현된다.** 등록 도구 (`gcap_compare` · `eval_accept` ×2) 재실행도 커밋본과 바이트 동일.
- **§6.3 채점 8/8 은 데이터 · fit 파일에서 재현된다** (관대한 채점 없음).
- 출처 · 무결성: 청크 계획 · meta · genie 3584 배열 · chk 99 배열 · fit sha · 체크포인트 · FREEZE/실행 커밋 관계 · 동결 절 불변 · 실행 창 안 main 커밋 없음 · 이탈 공개 — 전부 확인.
- 고칠 것은 EXPERIMENTS 행의 chk SNR 1 건 (S1) 과 NIT 2 건. 수치 · 판정 · 채점을 바꾸는 발견은 없다.
