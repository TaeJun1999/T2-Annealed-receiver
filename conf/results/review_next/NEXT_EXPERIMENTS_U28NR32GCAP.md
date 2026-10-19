# NEXT_EXPERIMENTS_U28NR32GCAP — UMi28 C9 (32×4) GMM 용량 확인: 기존 b\* (kron K4096) 의 EM 50 회 continuation · kron K = 8192 적합 → validation LL 로 b\* 재선택 → **새 b\* 일 때만** test 7 SNR 평가 (E2′) — 사전 등록 v2

- 작성: 초안 v1 2026-10-16 23:25 CDT (= 10-17 13:25 KST; 커밋 09d2ea69, fit manifest 와 함께) → 검토 2 건 (아래) → v2 2026-10-16 23:56 CDT (커밋 24ad4441) → 코드 교차 검토 2 건 (Codex · verifier 재확인, §4.3) 반영 → **v2.1 2026-10-17 00:31 CDT (= 10-17 14:31; 동결 커밋)**, Claude Code (Opus 5.5). 동결 시각 = 동결 커밋 시각 (`DECISIONS.md` 같은 줄). 동결 뒤에는 §1~§3 과 `code/run_gcap.sh` 를 바꾸지 않는다; 바꿔야 하면 사용자 승인 + `DECISIONS.md`. **동결 커밋 (FREEZE) ≠ 실행 커밋**: 실행 커밋 = §5 와 `gcap/gcap_s5.txt` 를 더하는 커밋 (선례 "§5 = 실행 커밋"); 둘 사이에 code/·Demo/ 는 바뀌지 않는다 (스크립트가 검사).
- 사용자 지시 (원문 사본, 이 폴더): `gcap/PROMPT_SERVER_GMMCAP.md` (sha256 0c3feb4e…ac4b) + `gcap/PROMPT_SERVER_COMMON.md` (d74abe6e…f7c7). 요지: 심사자가 "GMM 용량이 부족해서 진 것 아닌가" 를 물을 수 있으므로 K 를 한 단계 늘리고 기존 fit 의 수렴 상태를 확인한다; "결과가 이득을 줄이면 그 수치가 원고에 들어간다"; 원고 반영 마감 2026-10-24 18:00 CDT. 이 세션에서 받은 지시 (원문, 10-16 CDT): "GPU 여러개 동시 사용해" · "5개까지만 점유하자" · "CPU 워커를 쓸일이 있으면 120개까지만 점유하고".
- **결과 관측 전**: v2 를 쓰는 시각에 continuation · K8192 의 검증 LL 은 하나도 보지 않았다 (적합은 돌고 있다 — §4.3). 작성자가 본 적합 관련 수치는 프로브 (§4.2) 뿐이다. 새 fit 으로 BLER 을 잰 적이 없다.
- 절차 (공통 규칙 §3): 등록 → 적대적 검토 1 회 → 반영 (v2) → 동결 커밋 = 실행 커밋 → 실행 → 수용 → §6 전사 → 기록 감사 1 회 → `docs/RESULTS.md` 새 절 → DECISIONS · EXPERIMENTS 줄. 적합 (§1.1) 은 개발이라 v1·manifest 커밋 뒤 검토와 나란히 시작했다 (§4.3); test 를 쓰는 §1.3 은 동결 뒤에만.

### v1 → v2 (적대적 검토 Fable 5.1 `prereg_reviews_2026-10-17/review_U28NR32GCAP.md`: MUST 3 · SHOULD 8 · NIT 7 — 전부 반영; verifier `prereg_reviews_2026-10-17/verifier_U28NR32GCAP.md`: 결함 0, 확인 필요 2 · 선택 2 — 반영)
- M1 → §1.3 메모리 가드 행 (개발 청크 RSS 스모크 `gcap/rss_smoke.py` → G, 주 실행 `--worker-gb G`, 멈춤 규칙 1.25·G / OOM, 인상만) + 시간 행 재산정. M2 → §1.3 수용 행에 두 호출 원문, `code/run_gcap.sh` 구현 (동결 커밋에 포함; fits 폴더 "파일 정확히 2 개" 전제). M3 → §0 K4096 기록 (학습 LL 31 값, 검증 LL 은 it 30 하나뿐), §1.1 적합 마감 10/18 · 프로브 수치 · 재시작 병렬, §1.5 알림 규칙.
- S1 → §1.4 적합 비용. S2 → §2.1 Q-K 한정어 세 경우. S3 → §2.1 라벨 괄호·b\*(GCAP) 정의. S4 → §1.3 CPU 행 (사용자 상한 120, 코어 목록, 다른 등록 runner 가 돌면 시작 전 사용자에게 순서를 묻는다). S5 → §4.2 (자체 검사 출력 파일, 프로브 공개). S6 → `gcap/select_gcap.py` (§1.2). S7 → `run_gcap.sh` 에 run_manifest · guard_report · run\|git 검사. S8 → §1.1 B 필드 메모·"50 회 완료" 근거. N1–N7 → §0 파일럿 문구, §4.3, §1.5 마커, §1.3 chk SNR 이유, §1.1 "500 상태", 병합 소요, §4.3 실행 상태.
- verifier 확인 필요 1 → `gcap_compare.py` 는 load_raw 의 WARNING 만 거부, NOTE (raise 한 블록을 실패로 셈, 01_RULES §4) 는 출력에 옮긴다 (자체 검사 출력 바이트 동일). 확인 필요 2 → §1.5 프로세스 예외 규칙. 선택 → §1.1 `steps_done` 정의.

## 0. 알고 있는 것 (판정에 쓰지 않는다)

| 항목 | 값 (출처) |
|---|---|
| 셀 | 3GPP 38.901 UMi 28 GHz (prior `UMi28`, testbed D2 경로), C9: N_r 32, N_t 4, T 16, T_p 4, 파일럿 규칙 `eig` (`common.make_pilots`: 송신 측 앙상블 공분산이 informative 면 고유벡터 정렬, 아니면 DFT), QPSK, conv (133,171)_8 ν = 6 종단 (K_b 42), 외부 반복 16, BLER@16. N′ = 1.6×10⁵ training channels (stream 7) + 5000 validation (stream 8). SNR −12/−9/−6/−3/0/+3/+6 dB, test trial 0..2559 (skip0 0, chunk 40, 448 청크). 실행 커밋 b4433d3c (scale 브랜치), raw `~/t2_wtS/conf/raw_U28NR32B16e4` (`run_manifest_U28NR32B16e4.json` 과 일치 — 2026-10-16 23:15 CDT 대조; 검토가 독립 재확인) |
| V1 | `ckpt/d2sx_UMi28NR32_N160000_a1_best.pt` (sha256[:16] 463da87aa8dbfb61, best EMA @232). 재학습 없음 |
| 기존 b\* = A | kron K = 4096 (`~/t2_wtS/conf/results/gmm_fits_D2_U28NR32B16e4/fit_UMi28_Nr32_kronK4096_n160000.npz`, sha256 2d72a434…f569), 재시작 0 선택 (후보 ll_val 152.23176788511105 · 152.124183756404 · 151.79374075040246), it_best 30 / n_iter 31, reseed 29980, FIT_KRON_BATCHED = 1, 적합 10420 s (세 재시작), 격자 전체 em_sec 128781 s. **정지 사유: legacy tol 규칙이 학습 LL 감소 (ll[30] − ll[29] = −1.50e-4 < 0) 에서 발동; best-validation 상태가 마지막 검증점 (it 30) — 검증 LL 이 오르던 중에 멈췄다**. 세 후보 모두 마지막 스텝이 학습 LL 감소 (r1 −2.09e-2, r2 −3.27e-3). train − val 간격 36.05 nat |
| A 의 반복별 기록 (1 단계) | 남아 있는 것은 fit 파일의 학습 LL 31 개뿐이다: −215.608196 −70.470434 89.340179 142.006648 160.939801 169.459844 174.119919 177.200719 179.296717 180.897277 182.127186 183.052035 183.862627 184.601901 185.159914 185.617448 186.021813 186.416154 186.784385 187.039562 187.267622 187.467664 187.667824 187.821748 187.944583 188.031728 188.096836 188.139439 188.251491 188.285931 188.285781 (it 0..30). **검증 LL 은 it 30 의 값 (152.23176788511105) 하나만 있다** — `fit_gpu._fit_one` 이 반복별 로그를 넘기지 않아 `logs/fit_edge_U28NR32B16e4.log` 에는 후보·병합 요약 줄만 있고, it 0/10/20 의 검증 LL 은 어디에도 없다. 현재 코드로 다시 평가한 상태 0 의 학습·검증 LL 은 기록값과 비트 동일 (§4.2) |
| K 격자 (kron ll_val) | 16 25.21 · 32 63.45 · 64 93.53 · 128 116.40 · 256 134.06 · 512 143.62 · 1024 148.95 · 2048 150.39 · 4096 152.23 (full 최고 = K128 80.06; full32 54.03). 4096 이 격자 끝 → 기록 한정어 "[K 상한 민감: 외삽 불가]" (RESULTS §21, r = 1.28, c_K = inf). K ≥ 1024 kron 적합 모두 n_iter 31–59 에서 tol 로 멈췄다 |
| 기존 판정 (SCALE16e4 §6.1) | 판정점 −3/0/+3 (앵커 b\* 자동). 표 B `b* → V1` 173:13 · 136:12 · 82:7, pooled 391:32 → **(i)**. ΣF b\* 958 · V1 599 · genie 127, R = 0.432 [90% 0.402, 0.462]. SNR@0.1 격차 b\* − V1 +2.29 dB [90% paired +1.98, +2.61]. K2048 → 4096 은 ΣF_b\* 960 → 958 (RESULTS §21.4 (e)). 기존 raw 의 arm = 아래 chk 의 11 개 |

## 1. 고정되는 것

### 1.1 후보 세 개 (적합 = 개발; train / validation 만, test 시행·BLER 미사용)

정본은 `gcap/fit_manifest_U28NR32GCAP.json` (커밋 09d2ea69 = 2026-10-16 23:27:21 CDT, 적합 시작 전). 요약:

- **A (기존 K4096)**: 위 파일 그대로.
- **B (continued K4096)**: A 의 저장된 best-validation 상태에서 같은 학습·검증 데이터로 EM 을 **정확히 50 회** (M-step 50 회, 상태 0..50 평가; 상태 0 = A). LL 증가량 기준 조기 종료 (tol) 끔, 검증 patience 끔. 검증 LL 은 상태 0, 10, …, 50 에서 (6 점); 저장되는 fit = 그 6 점 중 검증 LL 최고 상태 (**상태 0 포함**). kron 플립플롭 시작 T_k = `gmm_em_gpu.kron_tk(covs)` (kron 성분은 정확, 재시드 성분 1015 개는 I — EM 이 들고 있던 그대로). 일괄 kron M-step (A 와 같음), floor 1e-4, κ 0, n_k < 4 재시드, 재시드 난수 = A 의 EM seed 튜플 + [1] = `[20260926, 2, 9, 8, 32, 1, 4096, 0, 0, 1]`. 수치 이상 (Cholesky 실패, 비유한 학습 LL) 으로 멈추면 실제 완료 반복 수·원인·그때까지의 best 상태를 기록하고 "50회 완료" 나 "수렴" 으로 분류하지 않는다. **"50 회 완료" 의 근거 = 파일의 `status == "completed"` ∧ `stop == "budget"` ∧ `steps_done == 50`** (`steps_done` = 평가된 마지막 상태 번호: Cholesky 실패면 실패한 상태 −1, 비유한 LL 이면 그 상태). 코드 `code/fit_gcap_cont.py`; 산출 `…kronK4096_n160000.cont50.npz` 는 병합 파일과 필드가 다르다 (`cand`·`cand_ll_val`·`sec_best` 없음; `steps_done`·`steps_requested`·`status`·`stop`·`ll_val_traj`·`n_tk_eye`·`seed`·`src*` 있음) — 실행 경로가 읽는 `ll_val`·`covs`·`pi` 는 같다.
- **C (kron K8192)**: 기존 규칙 — 재시작 3 (seed 튜플 = runner.cmd_fit 의 것, K = 8192), 상태 0..499 평가 (gcap 은 M-step 499 회·마지막 미평가 M-step 없음; legacy 는 M-step 500 회에 마지막 결과 미사용 — 평가되는 상태 수는 같다), 10 회마다 검증, best-validation 반환, patience 40 — 에 **정지 규칙 gcap**: tol 정지는 0 ≤ ll[it] − ll[it−1] < 10⁻⁶ |ll[it]| (it ≥ 20) 일 때만 (학습 LL 이 한 번 감소한 것만으로는 멈추지 않는다), E-step Cholesky 실패·비유한 LL 은 "numerical" 로 멈춘다. 일괄 kron M-step. 종료 사유 4 갈래: `tol` = 수렴, `patience` = 검증 정체 (기존 규칙, 수렴 아님), `budget` = 예산 소진, `numerical (…)` = 수치 이상. 병합 = 검증 LL 최고 재시작 (`fit_gpu.py --merge`, CPU; 데이터를 두 번 만들어 ≈ 25 분). 명령 `FIT_KRON_BATCHED=1 FIT_STOP_RULE=gcap code/fit_gpu.py 32 kron 8192 160000 U28NR32GCAP --restart r --prior UMi28` (`gcap/run_gcap_fits.sh`).
- **자원·일정 (사용자 과제 3 단계)**: 프로브 (§4.2) K8192 183 s/상태 (첫 3 상태, 초기화 포함), GPU 메모리 최대 24.2 GiB. 재시작 셋을 GPU 0/2/3 에서 병렬 (사용자 10-16 CDT "GPU 여러개 동시 사용해", 상한 5 장), B 는 GPU 1. 예산을 다 써도 재시작당 ≤ 25.4 h + 데이터 13 분 → 늦어도 10-18 01:15 CDT; 병합 25 분. **적합 마감 = 10/18 CDT**.
- 산출: `results/gmm_fits_D2_U28NR32GCAP/` (B: `…kronK4096_n160000.cont50.npz`, C: `…kronK8192_n160000.k0r{0,1,2}.npz` + 병합 `…kronK8192_n160000.npz`). 기존 fit·raw 는 읽기만 한다.

### 1.2 선택 규칙 (test 를 보기 전에 끝낸다)

최종 b\* = {A, B, C} 중 **검증 LL 최고** (엄격한 >). B 의 best 상태가 상태 0 이면 B 는 A 와 같은 상태이므로 별개 후보가 아니다 (재계산한 ll_val 의 반올림 차이로 B 를 고르지 않는다). 프로세스 예외로 파일이 없는 후보는 후보가 아니다 (§1.5). held-out `ll_test` (stream 10) 는 기존 코드가 기록하지만 선택에 쓰지 않는다. 선택은 `gcap/select_gcap.py` (세 파일의 `ll_val`·best 상태·정지 사유를 repr 로 찍고 argmax) 의 출력 `gcap/select_U28NR32GCAP.out` 으로 남긴다. 선택된 fit 의 경로·sha256·K·ll_val (repr 전체 자리) 을 §5 와 `gcap/gcap_s5.txt` 에 적고 동결한다. **최종 = A 이면 test 평가 없이 끝낸다** (§2.2 문장). 최종 ≠ A 이면 §1.3.

### 1.3 test 평가 (최종 ≠ A 일 때만; 실행 = `bash code/run_gcap.sh [--resume]`, tmux)

| 항목 | 고정 값 |
|---|---|
| fits 폴더 (복사본, 링크 아님; 각 파일 정확히 2 개 — `load_fits` 는 폴더의 K 파일을 모두 읽는다) | `results/gmm_fits_D2_U28NR32GCAPe/` = 기존 `fit_UMi28_Nr32_fullK32_n160000.npz` (sha256 d572e0ac…e215; R5-genie 의 Ĉ 출처) + 선택된 fit 을 `arms.fit_path` 이름 (`fit_UMi28_Nr32_kronK<K>_n160000.npz`) 으로 복사. `arms.gmm_selection` 이 이 폴더에서 b\* = kron (선택된 fit) 을 고른다 (full32 54.03 < 152). `results/gmm_fits_D2_U28NR32GCAPchk/` = full32 + **기존** kron4096 (sha256 2d72a434…f569). 개발 스모크용 `results/gmm_fits_D2_U28NR32GCAPdev/` = GCAPe 와 같은 두 복사본. 스크립트가 sha 를 대조한다 |
| 주 실행 (태그 `U28NR32GCAPe`) | `taskset -c 24-47,120-143,72-95,168-190,50-61,146-157 python code/runner.py run --testbed D2 --prior UMi28 --cell C9 --ntrain 160000 --stagec-ckpt /home/HTJ/t2/conf/ckpt/d2sx_UMi28NR32_N160000_a1_best.pt --chunk 40 --n 2560 --arm M-ours-bstar R5-genie --worker-gb <G> --tag U28NR32GCAPe` (`CUDA_VISIBLE_DEVICES=` 빈 값) — 7 SNR × test 0..2559 = 448 청크, 외부 반복 16, CPU complex128 (01_RULES §9.3), 워커 = min(허용 스레드 119, 청크 수, ⌊0.8·MemAvailable / G⌋) |
| 같은 시행 확인 (태그 `U28NR32GCAPchk`) | 같은 공통 인자로 `taskset -c 191 … --snr 0 --n 40 --arm M-ours-dscore-C-V1 M-ours-bstar M-ours-bstar-scalar M-ours-gmm32 R0-pilot R1-turbo R2-ours-G R3-bigamp R4-llr R4-scvamp R5-genie --tag U28NR32GCAPchk` — 기존 11 arm, 0 dB (판정점 가운데: 모든 arm 이 일부 실패해 비교 정보가 많다; 선례는 격자 첫 SNR), skip 0, n 40, 1 스레드 (선례 소요 ≈ 7230 s), 주 실행과 동시에. 기존 raw 의 같은 청크와 **모든 arm × KEYS_RAW 비트 동일** — 현재 HEAD 의 수신기가 기존 V1 · genie · b\* 를 그대로 재현한다는 확인 |
| V1 · genie | 기존 raw 재사용 (재실행 없음). 주 실행의 R5-genie 를 기존 raw 와 **448 청크 전부·모든 시행** 비트 대조 → 같은 채널·잡음·송신 블록 |
| CPU | 사용자 상한 120 스레드 (10-16 CDT): 주 실행 119 (`24-47,120-143,72-95,168-190` + NUMA 2 의 `50-61,146-157`; GPU 4·5 의 코어 쌍 48·49·144·145 는 비움) + chk 1 (`191`). 시작 전 다른 세션의 `runner.py run` 이 돌고 있으면 시작하지 않고 사용자에게 순서를 묻는다 (공통 규칙: E3′ SBL32 · E5 QAM16 의 test 가 같은 10/19–21 창) |
| 메모리 가드 (M1) | §5 에서 개발 시행 한 청크 (0 dB, trial 2560..2599 — test 아님) 를 jobs = 1 로 돌려 (`cd conf && CUDA_VISIBLE_DEVICES= taskset -c 191 python results/review_next/gcap/rss_smoke.py`, arm = 주 실행과 같음, fits = GCAPdev) 실행 트리 최대 RSS 를 재고 **G = RSS × 1.05 를 0.5 GB 단위로 올림** (SCALE16e4 규칙) 을 `gcap_s5.txt` 의 `WGB` 에 적는다 (스모크는 dev 폴더가 e 폴더의 2 파일 바이트 복사본이 아니거나, 개발 청크가 이미 있거나, runner 가 실패해 청크를 새로 쓰지 못하면 G 를 내지 않는다). 실행 중 `run_gcap.sh` 의 메모리 감시가 30 s 마다 주 runner 와 워커의 VmRSS 를 보고 1.25·G 를 넘으면 주 실행을 멈추고 로그에 MEMGUARD 줄을 쓴다; 30 s 넘게 살아 있던 pool 워커가 사라졌는데 60 s 뒤에도 runner 가 살아 있으면 (워커 OOM: `mp.Pool` 은 그 청크를 영원히 기다린다) 같은 방식으로 멈춘다; 스크립트에 온 INT/TERM (tmux Ctrl-C) 은 주 실행을 멈추고 chk 는 끝까지 돌게 둔다 (백그라운드 runner 는 SIGINT 를 무시하므로 트랩으로 전달); 그러면 사용자에게 알린 뒤 스크립트가 chk 를 기다려 끝난 다음 `GCAP_WGB=<G′ ≥ G> bash code/run_gcap.sh --resume` (G 는 올리기만; `gcap_s5.txt`·HEAD 불변) |
| 시간 | 같은 스모크의 청크 시간 t 로 총시간 ≈ ⌈448 / 워커 수⌉ × t 를 §5 에 적는다 (참고: K2U28NR32B16e4 = b\* K2048 + genie 가 청크당 중앙값 2022 s; EP 비용 ∝ K 이면 K8192 ≈ 8000 s/청크, G ≈ 15.5 면 워커 ≈ 50 → ≈ 20 h; K4096 이면 ≈ 4000 s, ≈ 5 회전 ≈ 6 h). **10/21 CDT 안에 못 끝날 것 같으면 시작 전에 사용자에게 알린다** |
| 수용 (ACCEPT; 원문) | 주: `python code/eval_accept.py --tag U28NR32GCAPe:best:463da87aa8dbfb61:C9 --ntrain 160000 --kron-K <K> --ll-val <§5 ll_val repr> --ref-raw /home/HTJ/t2_wtS/conf/raw_U28NR32B16e4` (격자·청크 계획·meta ntrain/bstar/kron_K·ll_val (|차| ≤ 1e-9)·ckpt id·iters·R5-genie 재생). chk: `python code/eval_accept.py --tag U28NR32GCAPchk:best:463da87aa8dbfb61:C9 --ntrain 160000 --kron-K 4096 --ll-val 152.23176788511105 --n 40 --points C9:0 --ref-raw /home/HTJ/t2_wtS/conf/raw_U28NR32B16e4 --ref-arms all`. 그리고 두 태그의 청크 449 개 전부 `run\|git` = HEAD (`+dirty` 없음). 셋 다 OK 일 때만 §1.4 표를 결과로 쓴다 |
| 사후 산출물 | `code/run_manifest.py --tag U28NR32GCAPe` · `--tag U28NR32GCAPchk` (→ `run_manifest_<T>.json`), `code/guard_report.py --raw raw_U28NR32GCAPe --testbed D2` (→ `results/guard_D2_U28NR32GCAPe.txt`), `runner.py analysis --testbed D2 --tag U28NR32GCAPe` (2 arm 표, 기록용) |
| 분석 | `code/gcap_compare.py --old /home/HTJ/t2_wtS/conf/raw_U28NR32B16e4 --new raw_U28NR32GCAPe --out results/review_next/gcap/compare_U28NR32GCAP.txt`: 결합 데이터 (b\* = 새 raw, V1 · genie = 기존 raw) 에 `analysis.table_B` (판정점 = 앵커 b\*(새) 자동, 판정점별 exact 양측 부호검정 p < .05, 2/3 규칙, power guard, SNR@0.1 격차 90 % paired bootstrap) 와 `recovery_ci` 의 R (판정점 합, paired bootstrap B = 2000, seed 20260926). 같은 표를 기존 b\* 로도 다시 계산해 나란히 둔다 (기록값과 같아야 한다 — §4.2). 보고 전용: SNR 별 b\*(기존) → b\*(새) 부호검정. 거부 조건: 점·청크 구멍/겹침·키 누락 (load_raw WARNING), genie 불일치; load_raw NOTE (raise 블록 = 실패) 는 출력 머리에 옮긴다 |
| `gcap_s5.txt` (실행 커밋에서 추적) | `FREEZE <동결 커밋>` / `FIT <B 또는 C> <K> <ll_val repr> <선택 fit sha256>` / `WGB <G>`. 스크립트는 `B:4096`·`C:8192` 만 받고, 선택 sha 가 기존 K4096 sha 와 같으면 거부한다 (최종 = A 이면 test 평가 없음) |
| 순서·끝 표시 | 전제 (code/·Demo/ 청결; 이 문서와 `gcap_s5.txt` 추적·청결; HEAD = `gcap_s5.txt` 를 마지막으로 바꾼 커밋 (= 실행 커밋); HEAD 의 DECISIONS 에 이 등록의 동결 줄; FREEZE 가 HEAD 의 조상이고 그 뒤 code/·Demo/ 변경 없음; fits 폴더 각 2 파일·링크 아님·sha; ckpt sha; 기존 raw 448 청크; 다른 `runner.py run` 없음; raw 폴더 비었음, `--resume` 이면 기존 청크의 run\|git = HEAD) → chk + 주 실행 (동시, 주 실행에 메모리 감시) → 수용 2 + run\|git (셋 중 하나라도 실패하면 gcap_compare 를 돌리지 않는다) → run_manifest 2 · guard → gcap_compare → runner analysis. runner 비정상 종료·단계 실패는 fail 로 세고 스크립트는 fail > 0 이면 0 이 아닌 코드로 끝난다. 로그 `logs/run_gcap.log`, 끝 `GCAP_DONE ok=<n> fail=<n>` |

### 1.4 보고 (최종 ≠ A)

표 하나에 나란히: 표 B `b*(GCAP) → V1` 의 판정점, 점별 a:b (p), pooled, 라벨 (§2.1), ΣF (b\*, V1, genie), R [90%], SNR@0.1 격차 [90% paired] ‖ 같은 항목의 기존 K4096 값. 최종 fit 의 경로·sha256 (E4 비용 측정이 같은 fit 을 쓴다). **적합 비용** (01_RULES §5): 보고하는 b\*(GCAP) 의 적합 비용 = 기존 격자 128781 s + (B 면 continuation `sec`, C 면 K8192 세 재시작 `sec` 합) — raw 의 `meta|em_sec` 은 GCAPe 폴더 두 파일의 합이라 그 수가 아니다; 두 수를 함께 적는다. 보고 전용: 7 SNR 실패 수, SNR 별 b\*(기존) → b\*(새).

### 1.5 예외·중단

- **적합 (사용자 과제 3 단계)**: 10/18 CDT 안에 B 와 C 병합이 끝나지 않을 것 같으면 (예: 재시작이 죽어 다시 돌아야 할 때) 그때 사용자에게 알린다.
- **프로세스 예외** (M-step 의 역행렬 실패, CUDA OOM 등 — 잡지 않는 예외): 프로세스가 죽고 후보 파일이 남지 않는다. `logs/gcap_fits.log` 의 rc ≠ 0 과 프로세스 로그로 "수치 이상 (프로세스 예외)" 로 기록하고 사용자에게 보고한다. 다시 돌릴지·C 를 남은 재시작으로 병합할지는 사용자 결정 (`fit_gpu.py --merge` 는 후보 셋이 다 있어야 한다). 재시작 마커 `.started_k8192_r*` 는 남는다 — 재실행 전 마커 제거는 사용자가 한다.
- chk 가 비트 동일이 아니거나 genie 재생·run\|git 이 어긋나면: 표 B 를 결과로 쓰지 않는다; 무엇이 어긋났는지 기록하고 사용자에게 보고한다 (원인을 확인한 뒤 결정).
- 메모리: §1.3 메모리 가드 행. runner 가 멈추면 같은 HEAD 에서 `--resume`. 손으로 멈출 때 (tmux Ctrl-C) 스크립트는 주 실행을 멈추고 chk 가 끝나기를 기다린 뒤 수용 단계를 돌고 실패로 끝난다 — 재개는 그 뒤에 한다 (chk 를 죽이지 않는다; 끝난 청크는 재개 때 건너뛴다). runner 는 청크를 제자리에 쓰므로 멈춘 실행이 잘린 청크를 남길 수 있다 — `--resume` 사전 검사가 읽히지 않는 청크를 찾아 목록과 함께 멈추고, 그 파일은 사용자가 지운다.
- 다른 세션이 실행 도중 main 에 커밋하면 `--resume` 의 run\|git 검사가 막는다 — 그때는 사용자에게 알린다 (공통 규칙: 같은 창의 E3′ · E5 세션).
- 판정하지 못함 ((iii)·(iv)) 도 완료된 결과다. 유의성을 얻으려고 SNR 점이나 표본을 늘리지 않는다.
- test BLER 을 본 뒤 fit 을 다시 고르거나 K 를 늘리지 않는다.

### 1.6 하지 않는 것

새 GMM family (각도 대각, circulant, Toeplitz 등) — **평가한 family 는 full · Kronecker 뿐**이다. UMi 16×4, D2 등 다른 셀. A 의 다른 재시작이나 K ≤ 2048 fit 의 continuation. K8192 를 넘는 확장. Q-K (r·c_K) 재계산.

## 2. 라벨·문장

### 2.1 표 B `b*(GCAP) → V1` (최종 ≠ A)

**b\*(GCAP) = §1.2 의 최종 fit (§5 경로·sha256).** `analysis.table_B` 의 `M-ours-bstar -> M-ours-dscore-C-V1` 블록에서 읽는다: POWERED 이고 "second arm fewer failures" 가 2/3 이상 → **(i)** "UMi28 C9 (Nr 32) 에서 V1 이 b\*(GCAP) 보다 적게 실패 (GMM 용량 확인 재평가, UNGATED)"; "first arm fewer failures" 2/3 이상 → **(ii)** "UMi28 C9 (Nr 32) 에서 b\*(GCAP) 가 V1 보다 적게 실패 (GMM 용량 확인 재평가, UNGATED)"; POWERED 이고 둘 다 아니면 **(iii)** "판정하지 못함 (유의 방향 없음)"; POWERED 아님 → **(iv)** "판정하지 못함 (검정력 미달)". SNR@0.1 격차가 격자 밖이면 censored 로 쓴다.

한정어 (문장에 붙인다): G_GCAP = "(b\*(GCAP) = 검사한 family (full · Kronecker) 와 K 범위 (kron ≤ 8192), 등록 절차 (continuation 50 회 포함) 안에서 검증 LL 로 고른 GMM 이며 최적 GMM 이 아니다)". K 상한 한정어는 경우별로 정한다:
- 최종 = C (K8192, 다시 격자 끝): "[K 상한 민감: 외삽 불가]" 를 **유지**한다. Q-K (r·c_K) 는 다시 계산하지 않는다.
- 최종 = B (K4096): 한정어를 "[K 8192 까지 적합, 검증 LL 로 K4096 (continuation) 선택 — 격자 내부]" 로 **바꾼다** (K8192 대비 검증 LL 차를 함께 적는다).
- 최종 = A: 기존 한정어를 유지하고 §2.2 문장을 병기한다 (K8192 를 적합해 졌으므로 4096 은 더 이상 격자 끝이 아님을 그 문장이 말한다).

### 2.2 최종 = A

"검사한 범위 (continuation 50회, K 8192) 에서 validation LL 이 기존 K4096 을 넘지 못했다." 기존 표 B 는 그대로.

### 2.3 쓰지 않는 문구

"용량 문제가 해소됐다", "최적 GMM", "수렴했다" (`tol` 로 멈춘 재시작에만 그 재시작에 한해 쓴다), "동등", "비열등", "scaling law". (iii)·(iv) 에서 "비긴다".

## 3. 미리 적는 예측 (v1 에 적은 그대로; 적합의 검증 LL·새 BLER 미열람; §6 에서 각각 적중 / 빗나감)

1. B: best 상태 > 0 (continuation 이 검증 LL 을 올린다), 상승 폭 0 < Δ ≤ 1.0 nat.
2. B: 50 회 완료 (`budget`, 수치 이상 없음).
3. C: 병합 K8192 의 검증 LL > A (152.2318).
4. C: 세 재시작 중 `tol` (수렴) 로 끝나는 것은 없다 (`patience` 또는 `budget`).
5. 최종 ≠ A (test 평가가 돈다).
6. (평가가 돌면) 판정점 −3/0/+3 유지, 표 B 라벨 (i).
7. (평가가 돌면) ΣF_b\*(새) 는 958 의 ±5 % 안 (910–1006).
8. (평가가 돌면) SNR@0.1 격차 b\*(새) − V1 점추정 ≥ +1.5 dB.

## 4. 선행 작업·검토

### 4.1 코드 (기본 경로 불변)

- `code/gmm_em_gpu.py`: opt-in `init` (저장 상태에서 시작, rng 미소비), `stop_rule="gcap"` (위 정지 규칙, 정지 사유 `out["stop"]`, 마지막 평가 상태 `out["final"]`), `tol=None` / `patience=None`, `kron_tk`. 기본값은 이전 코드와 비트 동일 (§4.2).
- `code/fit_gpu.py`: `FIT_STOP_RULE=gcap` (opt-in) → 후보·병합 파일에 `stop` · `stop_rule` · `ll_val_traj` (병합엔 `cand_stop`). 미설정이면 출력 파일 필드도 이전과 같다.
- `code/fit_gcap_cont.py` (B), `code/gcap_compare.py` (§1.3 분석; v2.1: R 분모 0 → nan), `code/run_gcap.sh` (§1.3 실행; v2 에서 구현, v2.1 에서 Codex · verifier 지적 반영, `bash -n` 통과, 미실행).
- `gcap/`: `probe_gcap.py`·`run_probe.sh` (A 상태 재평가 + K8192 시간·메모리), `run_gcap_fits.sh` (B·C 실행), `test_gcap_em.py`, `select_gcap.py` (§1.2), `rss_smoke.py` (§1.3 메모리 가드).
- 커밋: 09d2ea69 (코드·manifest·v1, 2026-10-16 23:27:21 CDT) → v2 커밋 (이 문서·`run_gcap.sh`·`gcap_compare.py` NOTE 처리·select/rss 스크립트·검토 파일).

### 4.2 자체 검사·프로브 기록

- `gcap/test_gcap_em.out` (2026-10-16 23:55 CDT, GPU 4, old = 5bcffc3e 의 `gmm_em_gpu.py`): T1 기본 경로 비트 동일 (full · kron · kron 일괄), T2 continuation = 같은 난수의 straight run (|Δll| 0, 재시드 89 = 42 + 47), T3 `kron_tk` 복원 ≤ 4.44e-16, T4 init 은 rng 미소비 → `test_gcap_em OK`. `gcap/gmm_em_gpu_demo.out`: GPU ↔ 읽기 전용 Demo CPU `fit_gmm_em` 자체 검사 OK (full · kron).
- `gcap_compare.py` old = new 자체 검사: `prereg_reviews_2026-10-17/gcap_compare_selfcheck_old_eq_new.txt` (검토자) 와 작성자 실행 (23:23 CDT; NOTE 처리 수정 뒤 23:44 CDT 재실행 바이트 동일) — 391:32, +2.29 dB [+1.98, +2.61], ΣF 958 · 599 · 127, R 0.432010 [0.402, 0.462] = `tables_D2_U28NR32B16e4.txt:308–313` · `recovery_U28NR32B16e4`.
- 프로브 (`logs/gcap_probe.log`, 2026-10-16 23:13–23:36 CDT, GPU 0, git = 작업 트리 (커밋 09d2ea69 전, 기본 경로)): 데이터 생성 744 s; **A 상태 재평가: 학습 LL 188.2857805090495 · 검증 LL 152.23176788511105, 기록값과 상대 차 0.000e+00**; K8192 일괄 EM 3 상태 (프로브 전용 seed — 재시작 번호 99, 후보 아님): 학습 LL −206.751 · −36.687 · 121.07, 재시드 8760, 549 s (183 s/상태, 초기화 포함), GPU 메모리 최대 24.2 GiB. 검증 LL 은 상태 0 (무작위 초기화) 하나만 계산됐고 출력하지 않았다.

### 4.3 적대적 검토 (1 회, 동결 전)

- Fable 5.1 서브에이전트, 2026-10-16 23:05 → 23:50 CDT, `prereg_reviews_2026-10-17/review_U28NR32GCAP.md` (+ `check_fit_fields_U28NR32GCAP.{py,out}`, `gcap_compare_selfcheck_old_eq_new.txt`): MUST 3 · SHOULD 8 · NIT 7 — 전부 반영 (위 v1 → v2). §0 수치는 전부 파일과 일치 확인.
- 검토 시점의 실행 상태 (사실): B 23:27:25 CDT (GPU 1), C r0 23:36:37 (GPU 0), r1 · r2 23:40:46 CDT (GPU 2 · 3), 모두 git 09d2ea69 clean (`logs/gcap_fits.log`). §1.1 은 검토 전에 시작됐다 — 안전장치는 적합 전에 커밋한 manifest (정지 규칙·후보·선택 규칙) 다. 검토의 §1.1 지적은 캐비엇 (반복별 검증 LL 은 B·C 부터 기록된다; A 는 it 30 하나뿐) 으로만 남는다.
- verifier (코드, 같은 시각대): `prereg_reviews_2026-10-17/verifier_U28NR32GCAP.md` — 결함 0; 확인 필요 2 · 선택 2 반영.
- **코드 교차 검토 (v2 → v2.1)**: Codex (사용자 승인 10-16 CDT; `reviews/20261017-140241-codex_prompt_U28NR32GCAP.md`, 프롬프트 `prereg_reviews_2026-10-17/codex_prompt_U28NR32GCAP.md`) 확인된 결함 5 — 전부 수용 (응답은 같은 파일 끝): 실행 중 1.25·G 감시 미구현 → `memguard`; 최종 = A 에서도 test 전제 통과 → 후보·K·sha 검사; 수용 실패 뒤 분석 진행·종료 코드 0 → 게이트·종료 코드; R 분모 0 → nan; RSS 스모크 유효성 → 청크 존재·rc·dev 복사본 검사. legacy 비트 동일·continuation 50 회·gcap 정지·비교 재현은 Codex 가 독립 확인. verifier 재확인 (v2 범위; 같은 폴더에 요약 없음 — 이 절이 기록): 결함 1 (= Codex 2), 확인 필요 3 — `gcap_s5.txt` 동결 절차 (FREEZE ≠ 실행 커밋 → 스크립트가 HEAD = s5 의 마지막 커밋·DECISIONS 동결 줄·FREEZE 이후 code/·Demo/ 불변을 검사; 등록 문서 diff 검사는 뺀다 — §5 가 실행 커밋에서 더해진다), RSS 스모크의 dev 폴더 대조, Ctrl-C 뒤 chk 잔존 (§1.5) — 전부 반영; 선택 4 (링크 거부, 비교 출력 로그 보존, runner 종료 코드 집계, `--resume` run\|git 사전 검사) 반영.
- **고친 범위 재확인 (verifier, v2.1 초안)**: `prereg_reviews_2026-10-17/verifier_U28NR32GCAP_v21.md` — 결함 2: (1) 백그라운드 주 runner 는 SIGINT 를 무시해 Ctrl-C 가 주 실행을 멈추지 못한다 → INT/TERM 트랩; (2) 워커 OOM 이면 `mp.Pool` 이 영원히 기다려 스크립트가 멈춘다 → 사라진 워커 감시. 확인 필요 2 (주 runner OOM 뒤 고아 워커 — 수용이 막아 잘못 통과하지 않음; 잘린 청크 → `--resume` 검사 메시지를 원인대로) 반영, 선택 1 (FREEZE 커밋의 DECISIONS 동결 줄 확인) 반영. 대역 runner (mp.Pool, fork) 로 작성자가 다시 확인: 정상 종료 `runner exit: e 0 chk 0`; 워커 SIGKILL → `MEMGUARD: pool worker … vanished` · e 143 · 남은 프로세스 0; 프로세스 그룹 SIGINT → `INTERRUPTED` · e 130 · chk 0 · 스크립트 실패 종료 · 남은 프로세스 0 (`/tmp/claude-1005/-home-HTJ-t2/7f296764-20fc-422b-96c7-feef15a08581/scratchpad/mguard/conf/{ok,oom,int}.out`).

## 5. 평가 전 고정 기록 (적합 결과; test 미사용)

전사 원본: `gcap/select_U28NR32GCAP.out` (2026-10-17 04:58 CDT, CPU 24; 세 fit 파일만 읽음). 적합 로그 `logs/gcap_fits.log` · `logs/gcap_k8192.log` · `logs/gcap_cont.log`. 적합은 전부 git 09d2ea69 에서 시작 (B·C 의 end 줄 git 778bda1d = 끝날 때의 HEAD; 09d2ea69..778bda1d 의 code/ 변경은 `gcap_compare.py`·`run_gcap.sh` 뿐 — 적합 경로 불변).

| 후보 | 검증 LL (repr) | 상태·정지 | 검증 궤적 (상태, ll_val) | 파일 sha256 |
|---|---|---|---|---|
| A (기존 K4096) | 152.23176788511105 | it_best 30 / n_iter 31 (legacy tol, 학습 LL 감소에서) | (30, 152.2318) 하나 | 2d72a434…f569 |
| B (K4096 continuation 50) | 152.34773499788244 | best 상태 10, `stop budget`, `status completed`, steps 50/50, 재시드 50745, Tk=I 1015, 4602 s (GPU 1, 10-16 23:27 → 10-17 00:58 CDT) | (0, 152.2318) (10, **152.3477**) (20, 152.0844) (30, 152.2370) (40, 151.6594) (50, 151.2185) | 500ec2b91480d62e67bc9a1141cdc8cd5dcec50c9abee89d0790be429da07e2c |
| C r0 (K8192) | 153.30391084218408 | it_best 30 / n_iter 71, `stop patience`, 재시드 238991, 12837 s (GPU 0) | (0, −215.1062) (10, 149.2235) (20, 152.4460) (30, **153.3039**) (40, 152.7942) (50, 152.1604) (60, 151.7323) (70, 151.3661) | e9dc698d5786e4eb739ad1abf5213bb68ce11d5fa230c355805219d75486d16a |
| C r1 | 153.86125655672217 | it_best 30 / n_iter 71, `stop patience`, 재시드 234748, 12814 s (GPU 2) | (0, −215.0437) (10, 151.3026) (20, 153.7521) (30, **153.8613**) (40, 153.7398) (50, 153.0123) (60, 152.7855) (70, 152.1493) | 7495ebe59786b150b026b0f763ca6e1ece17e5f0bc12fc39f702a3cb2032bcb0 |
| C r2 | 154.13990347772582 | it_best 30 / n_iter 71, `stop patience`, 재시드 238023, 12794 s (GPU 3) | (0, −215.1702) (10, 151.3904) (20, 153.9571) (30, **154.1399**) (40, 153.7284) (50, 153.0351) (60, 152.9402) (70, 152.3901) | f271bb0453ca9f585fd2ff94f5f15d5821a3098f4a22a4ddcc3c245aabcb3ce6 |
| C 병합 (= r2) | 154.13990347772582 | restart 2, 학습 LL 209.52733621460857, train − val 55.387 | — | d883afaf2e3e6133685594c5e7eaa892ac371b90c41505b7acd4a2b3fd49f71b |

- C 세 재시작: 10-16 23:36 / 23:40 CDT 시작, 10-17 03:36 · 03:39 · 03:39 CDT rc 0. 셋 다 `tol` (수렴) 아님 — `patience` (검증 정체: best 30 뒤 검증 4 점 연속 하락). 학습 LL 감소 스텝 33 · 29 · 32 회 (gcap 규칙이라 정지 안 함). 병합 `fit_gpu.py --merge` CPU 24,120, 04:32 → 04:57 CDT rc 0. 병합 로그는 기존 코드대로 held-out `ll_test − ll_test(Gaussian) = 427.232 nat` 를 찍는다 — 선택에 쓰지 않았다 (`select_gcap.py` 는 `ll_val` 만 읽음).
- **선택 (§1.2)**: B best 상태 10 > 0 → 별개 후보. argmax ll_val = **C** (154.13990347772582 > B 152.34773499788244 > A 152.23176788511105). C − A = +1.908 nat, C − B = +1.792 nat.
- **최종 b\*(GCAP)** = `results/gmm_fits_D2_U28NR32GCAP/fit_UMi28_Nr32_kronK8192_n160000.npz`, sha256 d883afaf2e3e6133685594c5e7eaa892ac371b90c41505b7acd4a2b3fd49f71b, kron K 8192, ll_val 154.13990347772582. K 상한 한정어: "[K 상한 민감: 외삽 불가]" 유지 (§2.1).
- **적합 비용 (§1.4)**: 기존 격자 128781 s + K8192 세 재시작 38445 s (12837 + 12814 + 12794; 병합 파일 `sec` 38444.77) = **167226 s**. raw 의 `meta|em_sec` 은 GCAPe 폴더 두 파일 합이라 이 수와 다르다. (B continuation 4602 s 는 선택되지 않은 후보의 비용 — 보고 전용.)
- **fits 복사본** (cp, 링크 아님; fullK32·kronK4096 10-17 04:32 CDT, kronK8192 04:58 CDT): `gmm_fits_D2_U28NR32GCAPe/` = fullK32 d572e0ac…e215 + kronK8192 d883afaf…f71b; `…GCAPdev/` = 같은 두 파일 (바이트 동일); `…GCAPchk/` = fullK32 d572e0ac…e215 + kronK4096 2d72a434…f569.
- **개발 스모크 (§1.3 메모리 가드)**: `cd conf && CUDA_VISIBLE_DEVICES= taskset -c 191 python results/review_next/gcap/rss_smoke.py` (tmux `gcap_rss`, 10-17 04:58:45 → 07:37:19 CDT, git 778bda1d; 로그 `logs/gcap_rss_smoke.log`): dev 폴더 = GCAPe 의 2 파일 바이트 복사본 확인 → 청크 `raw_U28NR32GCAPdev/D2_C9_UMi28_Nr32_T16_Tp4_eig_snr0_skip2560_n40.npz` 를 새로 씀 (청크 9502 s), rc 0, wall 9504 s, 실행 트리 최대 RSS 12.613 GB → **G = 13.5** (12.613 × 1.05 = 13.24 → 0.5 GB 단위 올림). 워커 = min(119, 448, ⌊0.8 · MemAvailable / G⌋): MemAvailable 1037860916 kB (989.8 GB, 07:38 CDT) → ⌊58.65⌋ = **58** (runner 가 시작 때 다시 잰다). 추정 총시간 ≈ ⌈448 / 58⌉ × 9502 s = 8 × 9502 s = 76016 s ≈ **21.1 h** (단독 1 스레드 청크 시간 — 58 워커 동시 실행의 경합은 반영하지 않음) → 10-17 08 시 CDT 쯤 시작하면 10-18 05 시 CDT 쯤, **10/21 CDT 안**. 개발 청크의 BLER 은 열지 않았다 (로그의 진행 줄이 R5-genie 만 찍음).
- `gcap/gcap_s5.txt`: `FREEZE 778bda1d` / `FIT C 8192 154.13990347772582 d883afaf2e3e6133685594c5e7eaa892ac371b90c41505b7acd4a2b3fd49f71b` / `WGB 13.5`. 동결 = 이 절과 `gcap_s5.txt` 를 더하는 실행 커밋 (code/·Demo/ 는 778bda1d 와 같다).

## 6. 결과 (이 절은 추가만 한다)

### 6.1 실행 기록 (기록 2026-10-18 13:44 CDT = 10-19 03:44 KST, Opus 5.5 — 원자료 전사; 판정은 6.2)

표기: `G:n` = `logs/run_gcap.log` n 행, `E:n` = `logs/run_D2_U28NR32GCAPe.log` n 행.

- **실행 커밋** 64b2912f (§5 커밋; FREEZE 778bda1d, `git diff 778bda1d 64b2912f -- conf/code Demo` 0 바이트). 실행 내내 main HEAD = 64b2912f (다른 커밋 없음), `git status --porcelain conf/code Demo` 0 줄.
- **실행 1** (tmux `gcap`, `bash code/run_gcap.sh`): `G:1` 10-17 07:40 CDT start (resume=0, WGB 13.5); runner 워커 58 (`E:7`). 서버 메모리 압박 (6.4) 으로 22:33 CDT 에 §1.5 절차 (tmux Ctrl-C) 로 멈춤: `G:2` INTERRUPTED, `G:3` runner exit e 130 chk 0, accept_e FAILED · accept_chk OK · run_git FAILED (미완성 raw 116/448), run_manifest 2 OK, guard_e OK, compare NOT RUN, analysis FAILED → `G:16` GCAP_DONE ok=4 fail=5. 완료 청크 116, 읽을 수 없는 청크 0.
- **실행 2** (같은 HEAD, 태그 없이 `--resume`; 등록 §1.3 (실행 행 `bash code/run_gcap.sh [--resume]`, 메모리 가드 행 `GCAP_WGB=<G′ ≥ G> bash code/run_gcap.sh --resume`) · §1.5 ("같은 HEAD 에서 `--resume`") 의 재개 명령에 없는 glibc 할당기 환경변수 3 개를 붙였다 — **등록 이탈**, 6.4): `G:18` 10-17 22:34 CDT start (resume=1, WGB 13.5); runner 워커 55 (`E:150`), `E:600` finished in 854.4 min → `G:19` 10-18 12:49 CDT runner exit e 0 chk 0; `G:20–29` accept_e OK, accept_chk OK, run_git OK, run_manifest_U28NR32GCAPe OK (448 파일, arm M-ours-bstar · R5-genie), run_manifest_U28NR32GCAPchk OK, guard_e OK; `G:108` compare OK; `G:109` **analysis FAILED** → `G:110` **GCAP_DONE ok=7 fail=1**.
- **analysis FAILED 원인** (`E:601–619`): `runner.py analysis --testbed D2 --tag U28NR32GCAPe` → `analysis.table_A` 가 arm 마다 SNR@0.1 격차를 `REF = "R2-ours-G"` (`code/analysis.py:100`) 에 대해 계산 (`:321`) → 이 raw 에는 M-ours-bstar · R5-genie 두 arm 만 있어 `KeyError: 'R2-ours-G'`. 실행 1 의 analysis FAILED 도 같은 예외 (`E:125–143`). 즉 §1.3 사후 산출물 행의 "`runner.py analysis` (2 arm 표, 기록용)" 는 동결 코드로 만들 수 없다 — 등록 작성·검토 때 놓친 결함. 표 B · R · 라벨은 §1.3 분석 행 · §2.1 대로 `gcap_compare` 출력에서만 읽으므로 이 단계와 무관하다. conf/code 를 고쳐야 하므로 다시 돌리지 않았다.
- **수용·raw** (단일 프로세스, `meta|*` · `run|*` 키만 읽음): `raw_U28NR32GCAPe/` 448 npz (= 7 점 × 64 청크); 값 집합 `run|git` {64b2912f}, `meta|bstar` {kron}, `meta|kron_K` {8192}, `meta|ll_val|kron` {154.13990347772582} (= §5), `meta|ntrain` {160000.0}, `meta|worker_gb` {13.5}, `meta|jobs` {58: 116 청크, 55: 332 청크}, `run|seed` {20260926}, `run|iters` {16}, `run|dtype` {complex128/float64}. `raw_U28NR32GCAPchk/` 1 npz (kron_K 4096, ll_val 152.23176788511105, run|git 64b2912f). `gcap/U28NR32GCAPe_accept.txt` · `U28NR32GCAPchk_accept.txt` = "ACCEPT: OK". `results/guard_D2_U28NR32GCAPe.txt`: NO GUARD FIRINGS. `gcap_compare` 검사 줄: 같은 7 점, n = 2560, R5-genie 가 기존 raw 와 모든 점·필드에서 비트 동일.
- **시간** (`E:` 의 `done` 줄 청크 초): 실행 1 116 청크 평균 19995 s · 중앙 19611 s (8061–37745; 둘째 회전부터 메모리 압박), 실행 2 332 청크 평균 7954 s · 중앙 7260 s (6524–13125). 벽시계 14 h 53 min + 14 h 15 min = 29 h 08 min (§5 추정 21.1 h). 실행 1 이 멈출 때 진행 중이던 청크 약 58 개의 계산은 버려졌다.
- **적합 비용 (§1.4 의 두 수)**: 등록 계산 167226 s (§5: 기존 격자 128781 s + K8192 세 재시작 38445 s). raw `meta|em_sec` = 40544.76968383789 s (448 파일 같음) = GCAPe fits 폴더 두 파일의 `sec` 합 (kronK8192 병합 38444.77 + fullK32 2100.003348827362 = `meta|em_sec|M-ours-gmm32`) — 정의가 달라 두 수가 다르다.

### 6.2 결과 · 라벨 (`gcap/compare_U28NR32GCAP.txt`)

| 쌍 (앵커) | 판정점 | 부호검정 @16 a:b (점별) · 합 | power guard · 판정 | SNR@0.1 격차 (90 % paired bootstrap) |
|---|---|---|---|---|
| b\*(GCAP) → V1 (b\*) | −3 · 0 · +3 | 172:16 (p 3.4e-34) · 127:13 (1.1e-24) · 79:6 (2.4e-17) — 378:35, p = 8.3e-74 | POWERED; V1 적게 실패 3/3 → significant | **+2.17 dB [+1.83, +2.50]**, censored 0 % |
| b\*(기존 A) → V1 (재계산) | −3 · 0 · +3 | 173:13 (p 7.3e-37) · 136:12 (9e-28) · 82:7 (2.4e-17) — 391:32, p = 1.3e-79 | POWERED, 3/3 → significant | +2.29 dB [+1.98, +2.61] |
| b\*(GCAP) → genie | −9 · −6 · −3 | 774:1 · 520:1 · 419:2 — 1713:4 | POWERED, 3/3 | +7.16 dB [+6.56, +7.64] (기존 +7.28 [+6.70, +7.77]) |
| V1 → genie (기존 raw, 두 표 같음) | −9 · −6 · −3 | 646:1 · 372:4 · 263:2 — 1281:7 | POWERED, 3/3 | +4.98 dB [+4.44, +5.47] |

- **R** (판정점 −3 · 0 · +3 합, B = 2000, seed 20260926): ΣF b\*(GCAP) 942 · V1 599 · genie 127 → **R = 0.420859 [0.390, 0.451]**; 기존 b\* 958 · 599 · 127 → 0.432010 [0.402, 0.462].
- **기존 b\* 재계산 = 기록값** (§4.2: 391:32, +2.29 [+1.98, +2.61], ΣF 958 · 599 · 127, R 0.432010 [0.402, 0.462]) — 일치.
- **SNR 별 실패 수 / 2560** (b\*(GCAP) · V1 · genie; V1 · genie = 기존 raw): −12: 2277 · 2219 · 846, −9: 1196 · 1068 · 423, −6: 746 · 595 · 227, −3: 505 · 349 · 88, 0: 294 · 180 · 30, +3: 143 · 70 · 9, +6: 61 · 27 · 3.
- **보고 전용 b\*(기존) → b\*(GCAP)** (점별 부호검정, 7 점; a = 기존만 실패 : b = 새만 실패): −12 dB 2280/2277 38:35 p 0.82, −9 1207/1196 56:45 p 0.32, −6 761/746 57:42 p 0.16, −3 509/505 57:53 p 0.78, 0 304/294 56:46 p 0.37, +3 145/143 30:28 p 0.9, +6 62/61 13:12 p 1 (실패 수 기존 / 새); 새 b\* 가 7 점 모두 1–15 블록 적게 실패, 유의한 점 없음. 라벨 없음.
- **라벨 (§2.1, 최종 = C)**: **(i)** "UMi28 C9 (Nr 32) 에서 V1 이 b\*(GCAP) 보다 적게 실패 (GMM 용량 확인 재평가, UNGATED)" + G_GCAP "(b\*(GCAP) = 검사한 family (full · Kronecker) 와 K 범위 (kron ≤ 8192), 등록 절차 (continuation 50 회 포함) 안에서 검증 LL 로 고른 GMM 이며 최적 GMM 이 아니다)" + "[K 상한 민감: 외삽 불가]".

### 6.3 예측 채점 (§3; 8 개 모두 적중)

1. 적중 — B best 상태 10 > 0, Δ = 152.34773499788244 − 152.23176788511105 = +0.1160 nat (0 < Δ ≤ 1.0).
2. 적중 — B `stop budget`, steps 50/50, `status completed` (§5).
3. 적중 — C 병합 154.1399 > A 152.2318 (+1.908 nat).
4. 적중 — C 세 재시작 모두 `patience` (§5).
5. 적중 — 최종 = C ≠ A.
6. 적중 — 판정점 −3 · 0 · +3, 라벨 (i).
7. 적중 — ΣF_b\*(새) 942 ∈ [910, 1006].
8. 적중 — 격차 점추정 +2.17 dB ≥ +1.5 dB.

### 6.4 실행 중 기록 (`gcap/PENDING_DECISIONS_gcap_resume.md` 를 옮김; 수치 두 곳은 verifier 지적으로 원자료에 맞게 고쳐 옮겼다 — 원본 파일은 그대로 둔다)

- 2026-10-17 22:35 CDT — 주 실행을 §1.5 절차로 멈추고 (tmux Ctrl-C, 22:33 CDT) 같은 HEAD 64b2912f 에서 `--resume` (22:34 CDT; WGB 13.5 그대로, 메모리 가드가 워커 55 — `E:150`; runner 는 읽은 MemAvailable 을 로그에 남기지 않는다. 원본의 "MemAvailable 989 GB" 는 runner 공식 `int(0.8·kB/2**20 // G)` 로 55 가 나오지 않는다 (989 GiB → 58) — 다른 시각의 측정값으로 보이며 출처가 없어 뺀다).
  - 사유: 서버 메모리 압박 (다른 사용자의 페이지 캐시 ≈ 430 GB, MemFree 수 GB, 스왑 가득) 으로 워커가 커널 직접 회수에 갇힘 (워커 표본 user 0 % · sys 100 %, cgroup memory.pressure 65–90 %); 둘째 회전 청크 (실행 1 의 `done` 줄 59–116 번째, `E:67–124`) 24753–37745 s, 중앙 30816 s — 첫 회전 (1–58 번째) 중앙값 9746 s 의 2.54–3.87 배 (원본의 "31–35 ks, 3.2–3.6 배" 는 틀린 값).
  - 재개 때 바꾼 것: glibc 할당기 환경변수만 (`GLIBC_TUNABLES=glibc.malloc.mmap_max=0:glibc.malloc.trim_threshold=68719476736`, `MALLOC_MMAP_MAX_=0`, `MALLOC_TRIM_THRESHOLD_=68719476736`) — 해제한 메모리를 커널에 돌려주지 않고 다시 써서 반복 할당의 회수를 없앰. conf/code · Demo · 인자 · G 그대로. (raw 에는 환경변수가 기록되지 않는다 — 이 절이 기록.)
  - 결과 불변 확인 (개발 시행만): GCAP 설정 (b\* K8192 + genie, 0 dB) 시행 4300..4302 를 기본 / 할당기 설정으로 동시에 (raw `raw_U28NR32MTa` / `raw_U28NR32MTb`) → 17 배열 바이트 동일; 시간 3003 s / 934 s (user 556 / 579 s, sys 2431 / 350 s), 최대 RSS 12.57 / 12.91 GB (가드 1.25·G = 16.9 GB 아래). 할당기 설정으로 시행 2560..2562 를 다시 돌린 결과 (`raw_U28NR32MTc`) 가 GCAP 개발 스모크 청크 (기본 할당기, 10-17 07:37 CDT, 압박 전) 의 첫 3 행과 17 배열 모두 바이트 동일 (22:31 CDT). 출처: 실행 스크립트·로그를 scratchpad 에서 `gcap/malloctest/` 로 옮김 (`run_both.sh` · `run_variant.py` · `run_c.sh`, `a.log` · `b.log` · `c.log`; `*_failed_ckpt.log` 는 8×4 체크포인트를 잘못 넘겨 runner 가 시작 전에 거부한 첫 시도 — rc 1, 5 s, 청크 없음); 두 대조는 `gcap/malloctest/cmp_mt.py` 로 raw 에서 다시 계산 → `cmp_mt.out` ("MTa vs MTb: 17 arrays compared; differing: []", "MTc vs GCAPdev rows 0..2: 17 arrays compared; differing: []", 10-18 CDT).
  - test 쪽 증거 (사후): 실행 2 의 332 청크를 포함한 448 청크 전부에서 R5-genie 가 기존 raw 와 비트 동일 (6.1 `gcap_compare` 검사 줄; verifier 독립 재확인). b\* 의 불변은 개발 시행으로만 확인됐다.
  - 사용자: "뭐든 빨리 할 수 있는 방향으로 하자", "내가 지금 터미널을 건드리지 못해서 너가 할 수 있을까?" (2026-10-17 22:2x–22:3x CDT). 첫 멈춤 시도는 자동 권한 분류기가 거부, 사용자 요청 뒤 다시 실행.
  - 재개 뒤 관찰 (원본): 힙이 최고치 (≈ 12.6 GB) 에 닿은 워커부터 user 55 % 안팎으로 계산 (재개 10 분 뒤 13/55 워커), 나머지는 메모리를 받는 동안 대기; RSS 합계 473 GB (2 분) → 531 GB (20 분). 추가 (세션 점검의 관찰, 파일 기록 없음): 23:42 CDT 워커 55 개 모두 힙 최고치, RSS 합계 686 GB, memory.pressure 0 %. 실행 2 청크 시간은 6.1 대로 첫 회전 (압박 전) 보다 짧다.

### 6.5 사용자 결정 (2026-10-18 15:59 CDT)

- 사용자 "9 -12 모두 제안대로 하자" (WORK_QUEUE 대기 9): 실행 2 의 glibc 할당기 환경변수 (등록 이탈, 6.1 · 6.4) 를 **수용**한다. 결과 (표 B (i) · R · 격차) 는 그대로 쓰고, 이탈과 증거 범위 (b\* 의 test 동등성은 개발 시행으로만 확인, genie 448 청크 비트 동일) 를 함께 적는다.
