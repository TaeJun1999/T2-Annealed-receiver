# 기록 감사 — HISNR16e4 §6.1 (D2 C2·C6 고SNR 보강, n = 20480, 보고 전용) — 수치 재계산 + 규칙·출처 감사

- 감사 2026-09-30 17:42 CDT (= 10-01 07:42 KST), Fable 5.1 서브에이전트 (읽기 전용; 원본 파일을 고치지 않았고 이 디렉터리만 만들었다). 커밋 없음.
- 대상: `NEXT_EXPERIMENTS_HISNR16e4.md` §6.1 (:41–143, 미커밋; §1–§5 동결 32444c91), `docs/EXPERIMENTS.md` 마지막 행 (:57, 미커밋), `DECISIONS.md` `[2026-10-01 07:27 KST] HISNR16e4 결과 기록` 줄 (:309, 미커밋). 틀·선례: `NEXT_EXPERIMENTS_SEEDS3_16e4.md` §6.1·§6.2, `prereg_audit_2026-09-30/audit_SEEDS3_16e4.md`.
- 방법: raw npz (`analysis.load_raw` 로 읽기만) · 보고/genie_floor/accept/manifest 파일 · 로그 · git 만 읽는 재계산 (`recompute_hisnr.py` → `recompute_hisnr.out`, 검사 327 항목, `mismatches: 0`). Wilson (교과서 식, z = 1.959963984540054) · 짝지음 불일치 수 · exact 양측 부호검정 (math.comb; scipy binomtest 로 교차 확인) · 원 태그 (n = 2560) 실패 수 · genie 실패 목록의 SNR 별 L 집계는 모두 **이 스크립트에서 다시 계산**했고 (`hisnr_report.py`·`analysis.paired/sign_p` 호출 없음), 문서 값은 마크다운·보고 txt 를 **파싱**해 대조했다 (손으로 옮기지 않음). genie L 자체는 `genie_floor.py` 를 두 태그에 다시 실행해 (`--skip0 10000`; 채널 재추첨만, 수신기 없음; C2 24.7 s) 저장 파일과 **바이트 동일**함을 확인 (`genie_floor_rerun_<TAG>.txt`). CPU 1 프로세스 (OMP 2), GPU 숨김. `~/t2_wtS`·`~/t2_wtSBL` 은 열지 않았다 — 동시 실행 프로세스는 `ps`·`/proc/<pid>/cwd`·`tmux display` 로만 봤다 (`concurrent_processes.txt`).

## 총평

**판정: 수치·채점 오류 없음, 규칙 위반 없음 (기록 자체). 정정은 기록 위생 1 건 (공개 누락) + 선택 2 건.** 문서의 수치 (보고 표 6 arm × 4 SNR × 2 셀의 실패 수·BLER·Wilson, 짝지음 8 칸, 원 태그 16 칸과 예측 3 의 16/16, genie 바닥 표 전부, 예측 1·2, EXPERIMENTS 행·DECISIONS 줄의 수열) 는 raw 에서 재계산한 값과 자리수까지 전부 일치한다. §1–§5 는 동결 이후 불변, §6 은 추가만 (+104/−0). 실행 사실 (시각·git·수용·매니페스트·링크·로그 줄) 도 전부 원본과 일치한다. 단 하나: §1 의 실행 조건 "실행 중 다른 CPU 작업 없음" 은 지켜지지 않았고 (SPARSE 재튜닝 CPU 프로세스가 구간 전체에, 2단계 GPU 적합 6 개가 C6 구간에 함께 돌았다), §6.1 의 편차 목록은 그중 감사 스크립트 두 개만 적었다 → 위생 1. 라벨 없음·채점 불변.

## 수치·채점 오류

**없음.** `recompute_hisnr.out`: 327 검사, `mismatches: 0`. (재계산 값은 아래 "독립 재현한 항목".)

## 규칙 위반

**없음 (기록).** 등록 §1·§3·§6 조건을 하나씩 검사한 결과:

1. **§1–§5 동결 불변**: `git diff 32444c91 HEAD -- 등록` 빈 diff; 작업 트리 `--numstat` = 104/0, 삭제 줄 0, 추가는 `## 6. 결과` (:39) 뒤부터 → **§6 추가만** ✓.
2. **보고 전용**: §6.1·EXPERIMENTS 행·DECISIONS 줄에 새 판정 라벨 없음, 원 태그와 **합치지 않고** 나란히만 (16 행 별도 열) ✓; 해석 어휘 (유의하게·낫다·우수·개선·도달·여지·headroom·bound·최적·비긴다·significant) 없음 ✓; p 값 "서술용"·"판정 아님" 표기 ✓ (§1 다중성 줄과 일치).
3. **예측 채점 = 문구 그대로**: 예측 1 "+9..+15 dB genie BLER > 0 이고 그 실패의 대다수 (> 50 %) 가 L = 3" — 36/16/13 > 0, L=3 35/36·16/16·11/13, 합 62/65 (SNR 별·합산 어느 읽기로도 > 50 %) ✓; 예측 2 "V1 ≤ b\* 네 SNR × 두 셀 (점추정)" — 8/8 ✓ (111≤235, 59≤149, 39≤81, 23≤72; 29≤178, 24≤130, 20≤72, 13≤46); 예측 3 "≥ 14/16" — 16/16 ✓. 합계 3/3 ✓.
4. **시행 집합·수용**: raw 두 태그 각 2048 npz, SNR 마다 skip 10000..30440 (n 40) 빈틈·겹침 없음, `run|skip` 최소 10000 → 테스트 (0..2559)·개발 (2560..)·P3 (3200..)·A1C5 (4480..) 와 겹치지 않음 ✓; `run|git` 6b1de688 하나, `run|iters` 16, `run|seed` 20260926 ✓; meta ntrain 160000·bstar kron·kron_K 1024/4096·ll_val|kron (−11.459169831224418 / 63.1751571838059, |diff| ≤ 1e-9)·ckpt id (sha·role) 가 §1 과 4096/4096 파일 일치 ✓ (`eval_accept.py` 가 검사하는 항목을 독립 재검) ; `<arm>|failed` 키 0, 6 arm × 16 반복 blk_err 비유한 0 ✓; `load_raw` 경고 0 (두 새 태그·두 원 태그) ✓.
5. **코드·커밋**: 실행 HEAD 6b1de688 ↔ 동결 32444c91 차이 = `conf/DECISIONS.md` 2/0 · `WORK_QUEUE.md` 4/4 (`--numstat`), `conf/code`·`Demo` 차이 0 줄 ✓ (사이 커밋 2734b66a·6b1de688 모두 문서); `6b1de688..HEAD -- conf/code Demo` 빈 diff, 작업 트리 conf/code 청결 ✓. 실행 구간 (09-30 22:03 – 10-01 07:09 KST) 안 main 커밋 0 (`git log --since/--until`); 직후 커밋 15d4e1dc 07:20:09 KST (= 17:20 CDT) ✓ — WORK_QUEUE "main 커밋 금지 구간" 준수.
6. **순서·시각**: `cpu_chain.log` SEEDS3 exit 0 → "HISNR registration frozen -> run" 08:03 CDT (체인 조건 = 등록 tracked+clean + DECISIONS `동결 — HISNR16e4` 줄 :303 ✓) → `run_hisnr16e4.log` start 08:03 (git 6b1de688) → HSB16e4k 수용 08:47 rc=0 → 보고·genie_floor 08:48 rc=0/0 → HSNR16 수용 17:09 rc=0 → 보고·genie_floor 17:09 rc=0/0 → `HISNR_DONE ok=2 fail=0` 17:09; 로그 10 줄, `start` 1 회, ABORT·INVALID·resume 없음 ✓. runner "finished in 44.4 min / 500.3 min", `/2048 done` 2048 줄씩 ✓ (08:03 + 44.4 min ≈ 08:47; 08:48 + 500.3 min ≈ 17:08 ✓). `CUDA_VISIBLE_DEVICES=` (스크립트 :5) ✓.
7. **KST↔CDT** (전부 −14 h): §6.1 머리말 17:27/07:27; EXPERIMENTS 22:03–07:09 ↔ 08:03–17:09; 매니페스트 written 22:47:57 KST ↔ 로그 08:47, 07:09:00 KST ↔ 17:09; 15d4e1dc 07:20:09 KST ↔ 17:20; SEEDS3 감사 파일 23:38·23:41·23:43·23:45 KST ↔ 09:38–09:45 (ls 23:38:01·23:41:53·23:43:01·23:45:32 ✓); DECISIONS 07:27/17:27; 동결 32444c91 13:06:12 KST ↔ 머리말 "v2 09-29 23:06 CDT"; 6b1de688 15:09:57 KST ↔ DECISIONS :305 "01:09 CDT" ✓. 자리표시 ('x CDT'·TODO·xx:xx) 없음 ✓. 기록 시각 17:27 CDT 는 이 감사 시작 (17:31 CDT `date`) 직전 — 모순 없음.
8. **매니페스트·링크·수용 파일**: git 6b1de688, n_raw_files 2048, config_hash b66966335b0c172b / 7e8fe21e1c7fea42, skip_min 10000·skip_max_end 30480, n_chunks 2048, kron_K 1024/4096, ckpt sha 4443921ce8d5c4a1 legacy-last / c050d611b2c714a6 best, arms 6 (정렬), fits_dir = `results/gmm_fits_D2_<TAG>` = 미추적 상대 링크 → `gmm_fits_D2_B16e4k` (mtime 09-30 22:03 KST) / `gmm_fits_D2_NR16B16e4` (22:48 KST) — 실행 스크립트 :16 `ln -sfn` ✓; `stagec_gate` 문구 = 원 태그 매니페스트 (`run_manifest_B16e4k.json:147`, `run_manifest_NR16B16e4.json:150`) 와 **문자열 동일** ✓; `<TAG>_accept.txt` = 정확히 `ACCEPT: OK -- <TAG>\n` (mtime 22:47:58 / 07:09:00 KST) ✓; 보고 머리말 2 줄 (git·시각·`load_raw warnings: 0`·REPORT-ONLY) ✓.
9. **§1 "실행 중 다른 CPU 작업 없음"**: **지켜지지 않았다** — 실행 조건의 편차이며 기록 규칙 위반은 아니다. §6.1 :136 은 이 편차를 적었으나 **일부만** (감사 스크립트 2 개) → 위생 1 로 정정.

## 정정 필요 (위생; 수치·채점 불변)

1. **[공개 누락] `NEXT_EXPERIMENTS_HISNR16e4.md:136` (§6.1 편차·주의 셋째 항목)** — HISNR 구간에 함께 돈 프로세스가 더 있다 (근거 `prereg_audit_2026-10-01/concurrent_processes.txt`; ps 는 지금 살아 있는 것만 보이므로 목록은 **하한**):
   - (b) SPARSE 재튜닝 `python code/sparse_tune.py --prior S2 --cell C6 --n 256` (작업 트리 `~/t2_wtSBL/conf`, tmux `sparsetune` = `bash code/run_sparse_tune.sh`, **CPU**): 프로세스 시작 09-30 10:49:14 KST (= 09-29 20:49 CDT), 감사 시각 10-01 07:39 KST 에도 실행 중 (ps %CPU 178) → HISNR 구간 (08:03–17:09 CDT) **전체**와 겹친다. WORK_QUEUE (동결 시점 문서) "진행 중" 표에 "SPARSE 재튜닝 v2b … CPU 2 스레드 × 6 | tmux sparsetune" 으로 이미 올라 있었다.
   - (c) 규모 확장 2단계 GPU 적합 `python code/fit_gpu.py 32 kron 2048 160000 {NR32B16e4 | U28NR32B16e4 --prior UMi28} --restart 0/1/2` 6 개 (작업 트리 `~/t2_wtS/conf`, tmux `job_g0`–`job_g5`, `CUDA_VISIBLE_DEVICES` 0–5; ps %CPU 각 ≈ 99 = 코어 1 개씩): 시작 10-01 01:13:52·01:22:00·01:33:13 KST (NR32, = 09-30 11:13·11:22·11:33 CDT) 와 06:03:20·06:41:02·06:51:09 KST (U28NR32, = 16:03·16:41·16:51 CDT) — 모두 C6 runner 구간 (08:48–17:08 CDT) 안. bash 루프 `code/gpu_sched.sh`·`code/edge_rule.sh` (00:43:20 KST = 10:43 CDT), `logs/batched_prefix.sh` (05:19:59 KST = 15:19 CDT; ps %CPU 0.3).
   - 고칠 문구 (:136 전체를 대체): "- §1 "실행 중 다른 CPU 작업 없음" 과 다른 점 (감사 정정 §6.2): HISNR 구간 (09-30 08:03–17:09 CDT) 에 함께 실행된 것 — (a) SEEDS3 기록 감사 (SEEDS3 §6.2) 의 raw 재계산 스크립트 두 개 (`prereg_audit_2026-09-30/recompute_seeds3.py`, `recompute_seeds3_numeric.py`; 파일 시각 .py 23:38·23:41 KST → .out 23:43·23:45 KST = 09:38–09:45 CDT); (b) SPARSE 재튜닝 `code/sparse_tune.py --prior S2 --cell C6 --n 256` (`~/t2_wtSBL/conf`, tmux sparsetune, CPU; 프로세스 시작 09-30 10:49:14 KST = 09-29 20:49 CDT, 10-01 07:39 KST 에도 실행 중 → 구간 전체와 겹침; WORK_QUEUE "진행 중" 표에 있던 작업); (c) 2단계 GPU 적합 `code/fit_gpu.py 32 kron 2048 160000 {NR32B16e4, U28NR32B16e4} --restart 0/1/2` 6 개 (`~/t2_wtS/conf`, tmux job_g0–g5, GPU 0–5, 코어 1 개씩; 시작 10-01 01:13:52·01:22:00·01:33:13 KST = 09-30 11:13·11:22·11:33 CDT, 06:03:20·06:41:02·06:51:09 KST = 16:03·16:41·16:51 CDT — 모두 C6 runner 구간 안) 와 bash 루프 gpu_sched.sh·edge_rule.sh (10:43 CDT)·batched_prefix.sh (15:19 CDT). 근거 `prereg_audit_2026-10-01/concurrent_processes.txt` (ps·/proc·tmux; 구간 안에서 끝난 프로세스는 보이지 않으므로 하한). 수신기 실행·raw 쓰기 아님; 프로세스 수 (b) 는 1 개만 확인."
   - `docs/EXPERIMENTS.md:57` 비고 칸 끝에 추가: "; §1 '실행 중 다른 CPU 작업 없음' 불충족 — SPARSE 재튜닝 (CPU, 구간 전체)·2단계 GPU 적합 6 개 (C6 구간)·SEEDS3 감사 스크립트 2 개가 함께 실행 (§6.1 편차, 감사 §6.2)".
   - `DECISIONS.md:309` "전사만 (§6.1)." 앞에 추가 (선택): "§1 '다른 CPU 작업 없음' 불충족 (SPARSE 재튜닝·GPU 적합 동시 실행; §6.1 편차)."
2. **[출처] `NEXT_EXPERIMENTS_HISNR16e4.md:85` (원 태그 계산 방법 문장)** — 선택. 기록자의 계산 스크립트 (`scratchpad/orig_wilson.py`) 는 스크래치라 사라졌다. 같은 값을 이 감사의 `recompute_hisnr.py` 가 재현하므로 (§3: 실패 수 24 개·Wilson 32 개·예측 3 16/16·가장 가까운 칸) 출처를 남겨 둔다.
   - 고칠 문구 (:85 문장 끝에 추가): " (재현: `prereg_audit_2026-10-01/recompute_hisnr.out` §3)".
3. **[문구] `NEXT_EXPERIMENTS_HISNR16e4.md:135` (소요)** — 선택. 합계가 없다: runner 합 544.7 min ≈ 9.1 h, 스크립트 전체 08:03–17:09 = 9 h 06 min (§1 추정 ≈ 8.2 h).
   - 고칠 문구: "- 소요: C2 runner 44.4 min, C6 runner 500.3 min (합 544.7 min ≈ 9.1 h), 스크립트 전체 09-30 08:03–17:09 CDT (9 h 06 min). §1 비용 추정은 C2 ≈ 0.5 h, C6 ≈ 7.5 h, 합계 ≈ 8.2 h."

## 메모 (정정 아님)

4. 위생 1 의 (b)·(c) 가 결과 값에 미친 영향은 이 감사가 판단하지 않는다 (해석 금지). 사실만: raw 는 결정적 시드 (`run|seed` 20260926, `trial_stream` 규칙) 로 쓰였고 수용·무결성 검사는 전부 통과했다; 벽시계는 §1 추정보다 길다 (위 3).
5. §1 문장 "실행 중 다른 CPU 작업 없음" 은 동결 시점의 WORK_QUEUE (같은 커밋 계열 2734b66a·6b1de688) "진행 중" 표 (SPARSE 재튜닝 CPU 2 스레드 × 6, 2단계 GPU 적합) 와 이미 어긋나 있었다 — §1 은 동결 문장이므로 고치지 않고 §6 편차로만 남긴다 (위생 1).
6. 예측 3 의 구간 끝 거리 (절대값) 순위: C2 +12 b\* 1.04e-04 (점 3.9551e-03, 원 하한 3.8508e-03) < C6 +6 V1 3.41e-04 < C6 +15 V1 4.20e-04 < C2 +15 V1 7.24e-04 — 문서 :142 의 "가장 작은 칸" ✓.
7. 등록 머리말 :4 "D2 C2 +9..+15 dB genie 실패 6 건 전부 L = 3" 의 6 = 원 태그 genie +9/+12/+15 = 2/2/2 ✓ (L 은 이 감사가 원 태그에 대해 재계산하지 않음). 머리말 :5 "기대 실패 수" = 원 태그 실패 × 8 전부 일치 (V1 C2 128/56/40/24 = 16/7/5/3 × 8 등 24 칸).
8. §6.1 :57 "반복 16 blk_err 비유한 값 0" — 16 반복 전부 (6 arm × 4 SNR × 2 태그) 비유한 0 으로 더 강하게 성립.
9. `scipy.stats.binomtest` 의 exact 양측 p 와 math.comb 계산이 8 칸 모두 `.2g` 자리에서 같다 (2.6e-20, 1.8e-17, 2.7e-06, 3.2e-10; 9.5e-38, 4e-27, 5.3e-10, 2.5e-07).
10. 매니페스트 `written` 22:47:57 KST 는 수용 (08:47 CDT) 직전에 `run_manifest.py` 가 쓴 시각 (스크립트 :20 → :21 순서) — §6.1 표 "매니페스트 작성" 열의 KST 표기는 다른 열 (CDT) 과 단위가 다르지만 라벨이 붙어 있어 정정하지 않는다.
11. §6.1 :43 "6b1de688 과 동결 32444c91 의 차이" 는 diff 서술로 맞다; 사이에 커밋 2 개 (2734b66a WORK_QUEUE, 6b1de688 DECISIONS·WORK_QUEUE) 가 있다는 사실은 적혀 있지 않아도 diff 와 모순 없음.
12. genie_floor 재실행 두 태그 모두 바이트 동일 → 저장 파일의 L·cond·sigma_min·‖H‖² 값은 재현 가능 (같은 코드·같은 시드라 독립 표본은 아님). SNR 별 L 집계 (:117) 와 L 표 (:111–116) 의 합계 (L=3 114 = 52+35+16+11, 44 = 15+16+7+6; 시행 합 81920) 는 목록에서 독립 집계.

## 독립 재현한 항목 (`recompute_hisnr.out`; 문서값과 자리수까지 일치, 327 검사 / 불일치 0)

- **raw 무결성** (§1): 태그별 npz 2048, SNR 별 청크 512 = {(10000 + 40k, 40)}, `run|git` {6b1de688}, `run|iters` {16}, `run|seed` 20260926, `|failed` 키 0, 비유한 blk_err 0 (16 반복 전부), meta·ckpt id 4096/4096 일치, `load_raw` 경고 0 (4 raw).
- **보고 표** (§2): 6 arm × 4 SNR × 2 셀 = 48 칸의 실패 수·n·BLER·Wilson 하한·상한 (보고 txt 와 §6.1 마크다운 양쪽 대조, 96 검사) — C2 V1 111/59/39/23, b\* 235/149/81/72, R2 467/292/182/133, R1 903/521/291/204, R3 1083/1033/1116/1100, genie 66/36/16/13; C6 V1 29/24/20/13, b\* 178/130/72/46, R2 309/213/125/80, R1 621/433/264/157, R3 1090/1265/1418/1099, genie 17/16/7/7. 짝지음 b\* only : V1 only 와 p (txt·§6.1·scipy) — C2 158:34 2.6e-20, 106:16 1.8e-17, 61:19 2.7e-06, 57:8 3.2e-10; C6 156:7 9.5e-38, 111:5 4e-27, 63:11 5.3e-10, 38:5 2.5e-07.
- **원 태그 (n = 2560)** (§3): 실패 수 V1 C2 16/7/5/3 · C6 6/2/2/2, b\* C2 28/17/16/8 · C6 22/14/10/5, genie C2 9/2/2/2 · C6 6/1/2/0 (비유한 0); Wilson 16 칸과 "이 실행 점추정 ∈ 원 구간" 16 칸 = §6.1 나란히 표 (16 행 파싱) 전부 일치; 예측 3 = 16/16; 가장 가까운 칸 C2 +12 b\* (3.955e-03 / 3.851e-03); 머리말 기대 실패 수 24 칸.
- **genie 바닥** (§4): 두 파일의 실패 목록 (131·47 건) = raw `R5-genie|blk_err@16` 의 실패 시행 집합 (SNR 별 4 × 2, 시행 번호 = 10000 + 행) 과 정확히 같다; SNR 별 L 집계 문자열 = §6.1 :117 (두 열); L=3..8 행 (시행·실패·비율) = 파일 = §6.1, 실패 수는 목록 집계와 같고 시행 합 81920; cond·sigma_min·‖H‖²·p95 행 문자열 = 파일; 예측 1 수 (36/16/13; 35/36, 16/16, 11/13; 62/65 = 95.4 %); L=3 합 114/131·44/47 (EXPERIMENTS·DECISIONS).
- **예측 2·문자열** (§5): V1 ≤ b\* 8/8; EXPERIMENTS 행의 "C2 111:235, … (짝지음 … 158:34, …)"·"C6 …"·"genie 실패 C2 66/36/16/13 (L=3 114/131), C6 17/16/7/7 (L=3 44/47)", DECISIONS 줄의 "C2 111:235·59:149·39:81·23:72, C6 29:178·24:130·20:72·13:46"·"genie 실패 L=3 C2 114/131, C6 44/47", §6.1 예측 2 문자열·기대 실패 수 문자열 — 재계산 수열로 만든 문자열이 각 문서에 포함됨.
- **매니페스트·수용·로그** (§6): 위 규칙 항목 6·8 의 값 전부 (매니페스트 9 항목 × 2, 링크 대상 2, 원 태그 gate 문구 동일 2, accept 파일 2, runner 분 2, done 2048 × 2, run 로그 10 줄 중 6 줄 문자열, chain 로그 4 줄, 보고 머리말 2 × 2); 자리표시·해석 어휘 없음 (세 추가분 합쳐서).
- **git**: 등록 동결 이후 불변 (diff 0), 작업 트리 +104/−0, 32444c91→6b1de688 numstat (2/0, 4/4; conf/code·Demo 0), 실행 구간 커밋 0, 15d4e1dc 07:20:09 KST.
