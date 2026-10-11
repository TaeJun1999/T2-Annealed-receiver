# 기록 감사 — NEXT_EXPERIMENTS_DMC16e4.md §5 · §6 (DeepMIMO DMC, 태그 DMCB16e4 / DMCB16e4last)

- 감사자: Claude Code (Fable 5.1 서브에이전트, 독립 기록 감사). 감사 시각 2026-10-10 22:02 ~ 22:30 CDT (= 10-11 12:02 ~ 12:30 KST; `date` 로 읽음).
- 감사 대상 판: 작업 트리 = HEAD **5aa7b9b4** (10-10 22:22:51 CDT; 감사 중에 부모 세션이 §6 를 그대로 커밋함 — 파일 mtime 10-11 12:01:20 KST = 10-10 22:01:20 CDT, 작업 트리와 HEAD 동일). 동결 §0~§3 은 9d4c3b4a → 27737b62 → HEAD 에서 **바뀐 줄 없음** (`git diff -U0` 로 §4 두 행·§5·§6 추가만 확인).
- 방식: 읽기 전용. 새 파일은 이 폴더(`prereg_audit_2026-10-10/`)에만: `recompute_dmc.py` → `recompute_dmc.out` (numpy 로 청크 직접 읽기; `s6_dmc.py` 미사용·`tables_*.txt` 미사용; `analysis.load_raw` 는 §9 교차검증에만), `recompute_leak.py` → `recompute_leak.out` (누수 층화 독립 재현; 등록 스크립트 미실행·미덮어쓰기), `rerun_recovery_*.txt`·`rerun_accept.txt` (등록 도구 재실행본, 커밋본과 diff). GPU 미사용(`CUDA_VISIBLE_DEVICES=`), CPU ≤ 8 스레드. git 상태·기존 파일 변경 없음.

## 1. 재계산한 것과 재현 여부

| 항목 | 방법 | 검사 값 수 | 결과 |
|---|---|---|---|
| raw 청크 계획 {(40k, 40): k = 0..63} × 7 SNR, 두 태그 + raw_B16e4k | 파일명 파싱 | 3 × 7 | **재현** (구멍·중복 없음; `\|failed` 키 없음; 비유한 blk_err 없음) |
| raw meta: `run\|git` 448 청크 동일 = 27737b62, "+dirty" 없음; `ntrain` 160000, `bstar` kron, `kron_K` 4096, `ll_val\|kron` = 122.37953759128766 (\|Δ\| ≤ 1e-9), `em_sec` 두 태그 동일 10073.224, `stagec_ckpt_id` sha·epoch·best_epoch·role | 전 청크 비교 | 18 | **재현** |
| 실패 수·BLER@16 (best, 14 arm + R0-pilot@1 + pilot_C@16) × 7 SNR, V1(last) × 7 | numpy 직접 | 112 + 112 + 7 | **재현** (§6.2 표 전부 일치, 소수 3 자리 BLER 포함) |
| 판정점 (앵커 b\* / R2-ours-G / R5-genie, 두 태그) — §1 규칙 재적용 | 직접 | 6 | **재현** (+9/+12/+15; b\* BLER@16 +15 0.345 → \|log10\| 0.538 최소) |
| 짝 부호검정 a:b · exact 양측 p (`%.2g`) · pooled: b\*→V1 (best·last), b\*→scalar, R2→b\*, b\*→V4, b\*→V4b, b\*→V0, V1→genie, b\*→genie | `math.comb` 로 직접 | 9 쌍 × (3 + 1) + p 16 | **재현** (p 문자열까지 일치: 5.8e-10 · 2.2e-08 · 1.4e-11 · 3.4e-27 등) |
| 검정력 가드 · 라벨 ((i)~(iv)) 두 태그 | 규칙 재적용 | 6 | **재현: (i)**, POWERED, second arm fewer 3/3 (best·last 모두) |
| best 대 last V1 짝 부호검정 | 직접 | 8 | **재현** 18:17 (p 1) · 10:15 (0.42) · 17:12 (0.46), pooled 45:44 (p 1) |
| 회수율 R 점추정: −3 dB · +9/+12/+15 · 판정점 합 (best·last), D2 B16e4k −3 · −3,0,3, ΔR 1차 −0.268 · 2차 −0.230, 실패 수 격차 | 직접 | 30 | **재현** |
| 포화 가드 (−3 dB b\* BLER@16 0.8719 ∈ [0.005, 0.9], b\* 2232 > genie 1756) · 정의 불가(undefined 0) | 직접 + 재실행 | 3 | **재현** (미발동; 상한 0.9 까지 여유 0.028 — 사실만 적음) |
| 부트스트랩 CI (R, ΔR, 격차): `recovery_ci.py` ×4, `frontier_ci.py --recovery` ×3 | 등록 도구 재실행 → 커밋본과 `diff` | 3 파일 | **바이트 동일** (`rerun_recovery_DMCB16e4{,last}.txt`, `rerun_recovery_diff_DMCB16e4.txt`) |
| 수용 검사 `eval_accept.py` (§5 인자 그대로) | 재실행 | 1 | rc 0, `ACCEPT: OK -- DMCB16e4, DMCB16e4last` |
| SNR@0.1: 전 arm(genie·R0-pilot@1 포함) 격자 끝까지 BLER > 0.1 → 격차 전부 n/a | 직접 | 15 | **재현** |
| F3 가드 발동 (NMSE > 10 또는 비유한, 16 반복 중 하나라도) 두 태그 전 arm × 7 SNR | nmse 배열에서 직접 | 2 × (7 + 7 + 12 + 1 + 1) | **재현** (V0 발동 수·비율 7 점, 나머지 각 1 시행의 (SNR, arm) 집합, 미발동 4 arm) |
| last 태그 R5-genie 가 best 와 비트 동일 (8 키 × 7 SNR × 2560) + 체크포인트를 안 쓰는 9 arm 의 blk_err 도 두 태그 동일 | `array_equal(equal_nan)` | 10 | **재현** |
| `analysis.load_raw` 교차검증 (+9·−3 dB, b\*·V1·genie·V0, meta ll_val, R0-pilot@1 별칭) | 직접 읽기와 비교 | 10 | **일치** (로더 경고 없음) |
| **누수 층화** (`DMCB16e4_leak_strata.txt`): 시행 스트림 재생(sample → integers → permutation → transmit), d 자체 구현(블록식; 24 시행은 비전개식과 비교 max\|diff\| 5e-16), 층별 n·실패 수·R, 중앙값·비율; 정렬 검사는 **시행 0..39 와 1000..1039** (등록 스크립트는 0..39 만) | `recompute_leak.py` | 25 | **재현** (정렬 두 구간 모두 비트 동일) |
| §5 격자 표: full 6 · kron 6 · kron 1024/2048/4096 병합 3 + 후보 9 의 ll_val·restart·n_iter/it_best·재시드·κ, 상한 500 미정지(최대 301), 파일 24 개, `em_sec` = 15 파일 `sec` 합 | fit npz 직접 읽기 | ≈ 100 | **재현** |
| 체크포인트: sha256[:16] 65b26ddd4f6437f4 / 92dc9f53c31af875, epoch 812/832, best_epoch 812, best_val 0.250690221786499, stopped_by None/patience, role, grad_clip 0, prior·sigma_tag DMC, rung, attempt, wall 5527.93 s (6.644 s/epoch), split_hash | `sha256sum`, `torch.load(cpu)` | 16 | **재현** |
| GB′: min 0.6963 · max 0.8982 · median 0.7148 · worst excess −0.1018 · 20 점 모두 < 1 · `GMM b* = kron (K=4096)` | csv·npz·로그 | 6 | **재현** |
| 풀 sha (H.npy 709a6346b0ea763b, split.npy 9f3237f1997d6b91) = `dmimo.POOL_SHA`; P_RAW·TRAIN_SHA; erank(Rt) 3.422 (participation-ratio 정의 = `make_pilots`) | `sha256sum`, 모듈 상수 | 6 | **재현** |
| 시각 (KST → CDT): 동결 18:12:28 · 병합 18:24:26/18:24:30 · 4096 후보 18:14:58/18:16:50/18:32:53 · 병합 18:33:24 · 학습 17:44:57~19:17:02 · GB′ 20:02:57 · §5 커밋 20:04:45 · 실행 20:04→21:00→21:52→21:53 · 다음 커밋 21:55:07 · 누수 층화 21:56:46 · §6 기록 22:01:20 · sparse_tune 18:35~21:28 · testbed 17:39 · 큐 17:44 · 검토 파일 18:10 | `date -r`, `git log`, 로그 | 25 | **1 건 불일치** → 발견 S1 (fits 링크 시각) |
| 순서 규칙: 동결(18:12:28) < 병합·선택(18:24) < 4096 병합(18:33:24) < GB′(20:02:57) < §5 커밋(20:04:45) < 실행(20:04) | 위 시각 | 1 | **재현** |
| 공개 완전성: `git log 9d4c3b4a..HEAD` 의 커밋 7 개(dcf94166·ae880c27·2b88eb53·501e0635·48803fe6·27737b62·3ddb0831)가 §5/§6 에 전부 적힘; 실행 창(20:04~21:53 CDT) 안 main 커밋 없음; 동결 커밋의 코드 변경은 주석 두 줄; ae880c27 은 `_which` 에 [20260930, …] 배치 분기 추가만(기존 스트림 불변) | git | — | **재현** |
| §6 문구: "비긴다"·"동등"·범위 없는 "ray-traced 채널에서" 없음; 손으로 적은 "hh:mx" 식 시각 없음; 해석 문장 없음(6.3-8 의 "'비슷' 으로 읽음" 은 채점 재량을 공개한 것) | grep·읽기 | — | 통과 |

합계: 자동 비교 **357 값(332 + 25) 중 0 불일치**, 도구 재실행 3 파일 바이트 동일, 수동 대조 약 150 값 중 **시각 1 건** 불일치.

## 2. 발견

### MUST-FIX
없음 — §6 의 수치·라벨·채점 가운데 틀린 것을 찾지 못했다.

### SHOULD-FIX

**S1 · §5 129 행 "링크 `gmm_fits_D2_DMCB16e4last` 10-10 18:33 CDT" — 파일은 20:03:45 CDT 를 가리킨다.**
- 파일: `ls -la results/` → `gmm_fits_D2_DMCB16e4last -> gmm_fits_D2_DMCB16e4` 의 lstat mtime **2026-10-11 10:03:45 KST = 10-10 20:03:45 CDT** (§5 커밋 20:04:45 CDT 1 분 전). `run_prior_eval.sh` 는 링크를 만들지 않고 존재만 검사하므로 실행이 바꾼 것은 아니다. 18:33 CDT 에 만들었다면 그 뒤 다시 만들어진 것이고, 아니면 20:03 CDT 에 만든 것이다 — 어느 쪽인지는 파일로 알 수 없다(확신: 파일 사실은 확실, 경위는 모름).
- 교체 제안: `링크 \`gmm_fits_D2_DMCB16e4last\` lstat mtime 10-10 20:03:45 CDT (§5 커밋 직전; 18:33 CDT 에 만든 링크라면 그 뒤 다시 만들어진 것)` → 두 가능성 중 작성자가 아는 쪽으로 한 문장.

**S2 · §5 123 행 괄호 "(kron 2048·4096 후보 가운데 일부는 동결 전에 적합이 끝나 파일이 있었으나 …)" — 동결 전에 끝난 K ≥ 2048 후보는 kron 2048 r0 하나뿐이다.**
- 파일: `logs/tb2.log` — kron 2048 r0 done **18:09 CDT**(파일 mtime 08:09:51 KST), 동결 18:12:28 CDT; 2048 r1 18:13 CDT, 2048 r2 18:15 CDT, **4096 r0 18:14 CDT(mtime 08:14:58 KST), r1 18:16, r2 18:32 CDT** — 4096 셋은 모두 동결 뒤. (§4 의 "18:12 CDT 16 개 종료" = full 6 + kron 16..512 6 + 1024 ×3 + 2048 r0 = 16 과 일치.)
- 문장이 동결 전 노출을 실제보다 크게 적었다(저자에게 불리한 방향이지만 부정확). 교체 제안: `(동결 전에 적합이 끝난 K ≥ 2048 후보는 kron 2048 r0 하나(18:09 CDT, \`tb2.log\`)뿐이고, 2048 r1·r2(18:13·18:15 CDT)와 4096 셋(18:14:58·18:16:50·18:32:53 CDT)은 동결 뒤 끝났다; 작성자는 동결 전 어떤 ll_val 도 읽지 않았다 — §3 머리말)`.

### NIT

**N1 · §6.2 176 행 "14 arm 과 genie 모두 "> 15""** — genie(R5-genie)는 14 arm 안에 있다(14 = M 7 + R 7, genie 포함). 교체: `14 arm(genie 포함) 과 R0-pilot@1 모두 "> 15"`.

**N2 · §5 128 행·§6.3 198 행 "반만 적중" (예측 6)** — 동결 문구는 접속("발산 없음, patience 정지, epoch 200–600")이고 §3 은 부분 점수를 정하지 않았다; 한 절이 틀린 접속 예측은 통상 "빗나감"이다. 사실은 두 곳에 다 적혀 있으므로 틀린 기록은 아니고 채점 틀의 문제. 교체 제안(두 곳): `**빗나감** (부분: 발산 없음 ✓ · patience 정지 ✓ · epoch ≤ 600 ✗ 832)`. 확신 중간(재량 영역).

**N3 · §6.3 200 행 예측 8 "V4 · V4b 는 V1 과 비슷하거나 나쁨 ✓"** — 판정점 3 점 합에서 **V4 2891 < V1 2895**(V4 가 4 개 적음)이라 "나쁨"은 그 점에서 성립하지 않고, 7 SNR 합(9590 > 9559)에서만 성립; 문턱 없는 예측이라 반증 불가. 기록이 "'비슷' 으로 읽음"을 이미 공개했으니 다음을 덧붙이면 충분: `(판정점 합에서는 V4 가 V1 보다 4 개 적다 — 등록 문턱이 없어 "비슷" 으로만 채점; 반증 가능한 예측이 아니었다)`.

**N4 · §6 138 행 수용 검사 (c) 의 배너·raw 이름·N_train 항목과 §1 63 행 `"sparse specular" 문구 없음`** — `eval_accept.py` 는 청크 계획·meta·체크포인트 id·genie 재생·격자 파일만 검사하고 **배너·raw 이름·N_train·prior/sigma_tag·Demo 해시는 검사하지 않는다**(그 항목은 표·manifest 를 읽어 확인한 것). 또 두 표에는 "sparse specular" 가 **한 번** 나온다 — `DM_WARNING` 자체의 "NOT sparse specular"(표 54 행); D2 의 "CLAIM TESTBED -- sparse specular" 배너는 없다. 교체 제안(§6): `analysis 머리말에 \`DM_WARNING\` 배너(D2 "CLAIM TESTBED -- sparse specular" 배너 없음; "sparse specular" 는 DM_WARNING 의 "NOT sparse specular" 로만 등장), raw 이름에 \`DMC\`, 학습 예산 줄 \`N_train=160000\`, 저장된 prior·sigma_tag DMC, Demo 해시 두 manifest 동일 — 이 항목들은 \`eval_accept.py\` 검사 항목이 아니라 표·manifest·체크포인트를 읽어 확인`.

**N5 · §6.2 182 행 "`code/dmc_leak_strata.py` @dcf94166, 10-10 21:57 CDT 실행"** — 출력 파일 머리말은 `git commit: 3ddb0831`(실행 시 HEAD), `date 2026-10-11 11:56:46 KST` = 21:56:46 CDT; 스크립트는 dcf94166 이후 변경 없음(`git log -- code/dmc_leak_strata.py` 1 건). 교체: `(@dcf94166 = 스크립트 커밋, 변경 없음; 실행 시 HEAD 3ddb0831, 머리말 10-10 21:56:46 CDT)`.

**N6 · §5 127 행 GB′ 행** — `tb2_post_DMC.log` 19:17 CDT 줄: "GB' resume on GPU 1 (… git 48803fe6); **ALD dev regen + tune on GPU 0**" → 같은 스크립트가 GB′ 와 함께 baseline 확장(DMCBASE16e4)의 ALD 개발 재생성·조정을 19:17–19:26 CDT 에 돌렸다(DMCBASE16e4 §4 에는 적혀 있음; DMC16e4 §5 에는 없음). 주 실행 수치와 무관. 덧붙임 제안: `(같은 \`run_dmc_post_gpu.sh\` 가 GPU 0 에서 ALD 개발 재생성·조정(DMCBASE16e4)을 19:17–19:26 CDT 에 함께 돌렸다; GB′ 실행 시 HEAD 48803fe6)`.

**N7 · §5 114 행 "스크래치 생성기 `s5_gen.py`"** — 저장소에 없다(세션 스크래치 `/tmp/claude-1005/-home-HTJ-t2/<session>/scratchpad/s5/s5_gen.py` 에만 있고 컨테이너 재생성 시 사라진다). `s6_dmc.py` 는 이 폴더에 보존·커밋됐으나 `s5_gen.py` 는 아니다. §5 값은 이 감사에서 전부 독립 재현됐으므로 수치 위험은 없고 재현성 위생 문제. 제안: `prereg_audit_2026-10-10/s5_gen.py` 로 복사해 두고 §5 에 경로를 적음.

**N8 · DECISIONS.md** — DMC16e4 의 자취는 동결(10-11 08:12 KST)에서 끝난다; §5 커밋·실행(20:04 CDT)과 §6 전사(22:01 CDT)의 줄이 없다(10-11 12:22 KST 줄은 DMCBASE16e4 건). 규칙 위반으로 지목할 조항은 없음 — 선택 사항.

### 그 밖에 확인한 채점 재량(변경 불필요)
- §6.3-3 (`R2-ours-G → b*`): 동결 괄호 "(first arm fewer ≥ 2/3)" 는 이 쌍의 방향과 반대이고 본문 "b\* 우세" 로 채점했음을 기록이 공개함. 본문의 방향이 명백하므로 "적중" 채점에 동의한다.
- §6.3-2: 세 하위 항목(SNR@0.1 격차 → 채점 불가 / 2차 R → 빗나감 / ΔR 1차 → 적중)은 동결 문구의 조건대로 채점됐다; 관대한 채점 없음.

## 3. 검증하지 못한 것
- tmux 세션 이름(`dmceval`·`tb2dmc`·`sptdmc`), `taskset` 고정의 정확한 시각(17:46 CDT): 로그 줄 없음. epoch 1–3 ≈ 22.9 s, epoch 4 12.0 s, epoch 5+ ≈ 6.5–7.0 s(`train_d2sx_DMC_N160000_a1.log`)로 "epoch 4 무렵 ≈ 17:46 CDT" 와 일관.
- "작성자는 동결 전 그 ll_val 을 읽지 않았다": 파일로 검증 불가(S2 는 파일이 언제 있었는지만 다룬다).
- 적대적 검토 "18:07 CDT 보고": 검토 파일 mtime 10-11 08:10:13 KST(= 18:10 CDT); 모순은 아니나 확인 불가.
- 부트스트랩 CI 는 등록 도구를 재실행해 바이트 동일함을 확인했고(시드 고정), 별도 부트스트랩 구현으로 다시 짜지는 않았다. 점추정은 모두 독립 재계산.
- §0 의 실행 전 수치(TDMa–i, σ 격자, 0단계 표)는 이번 감사 범위 밖(파일 mtime·sha·erank 3.422 만 확인).

## 4. 결론
- **§6.1 라벨 (i) 는 §1·§2 동결 규칙을 raw 에서 다시 적용해 재현된다** (best·last 모두 POWERED, second arm fewer 3/3; 포화 가드 미발동; ΔR 1차 CI [−0.325, −0.209] < 0 → "D2 보다 낮다"; 라벨 문장·필수 부속(회수율·ΔR·(1)(2)(3)) §2 와 일치).
- **§6.3 의 채점 11 항목은 모두 데이터에서 재현된다** (1 적중 · 2 채점 불가/빗나감/적중 · 3 적중 · 4 적중·적중 · 5 빗나감 · 6 "반만 적중"(틀 문제 N2) · 7 적중 · 8 ✓(문턱 없음 N3) · 9 빗나감 · 10 없음 · 11 미발동).
- 고칠 것은 §5 의 시각 1 건(S1)과 동결 전 후보 파일 서술 1 건(S2), 문구·위생 NIT 8 건. 수치·판정·채점을 바꾸는 발견은 없다.
