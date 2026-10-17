# 적대적 검토 — NEXT_EXPERIMENTS_U28NR32GCAP.md 초안 v1 (커밋 09d2ea69) + gcap/fit_manifest_U28NR32GCAP.json

- 검토자: Fable 5.1 subagent, 2026-10-16 23:05 → 23:50 CDT (= 10-17 13:05 → 13:50 KST). 읽기 전용; CPU 만 (`CUDA_VISIBLE_DEVICES=`, `taskset -c 32-39`); GPU·tmux·실행 중 프로세스는 건드리지 않았고 BLER 코드는 돌리지 않았다.
- 읽은 것: 등록 문서 전체, fit manifest, `gcap/PROMPT_SERVER_GMMCAP.md` (sha256 0c3feb4e…ac4b 일치) · `PROMPT_SERVER_COMMON.md` (d74abe6e…f7c7 일치), `AGENTS.md`, `01_RULES.md`, `code/{gmm_em_gpu, fit_gpu, fit_gcap_cont, gcap_compare, runner (해당 부분), arms, analysis (해당 부분), recovery_ci, eval_accept}.py`, `gcap/{probe_gcap.py, run_gcap_fits.sh, run_probe.sh, test_gcap_em.py}`, `~/t2_wtS/conf` 의 기존 실행 (fit 파일 전부의 필드, raw 청크 하나의 키, `run_manifest_U28NR32B16e4.json`, `tables_D2_U28NR32B16e4.txt:308–313`, `logs/fit_edge_U28NR32B16e4.log`, `logs/run_D2_{U28NR32B16e4,K2U28NR32B16e4,U28NR32B16e4chk}.log`), RESULTS §21, 선례 ROOM16e4 · SCALE16e4 (라벨·메모리 가드·chk 수용 행), `review_ROOM16e4.md`, `code/run_scale2.sh`.
- 새 파일 (이 폴더만): `check_fit_fields_U28NR32GCAP.py` → `.out` (§0 수치 대조), `gcap_compare_selfcheck_old_eq_new.txt` (= `code/gcap_compare.py --old <기존 raw> --new <기존 raw>` 출력). 같은 폴더의 `verifier_U28NR32GCAP.md` 는 다른 에이전트가 쓴 것이며 읽지 않았다.
- **검토 시점의 상태 (사실)**: §1.1 의 적합은 이미 돌고 있다 — cont (GPU 1) 23:27:25 CDT, K8192 r0 (GPU 0) 23:36:37, r1 (GPU 2) · r2 (GPU 3) 23:40:46 CDT, 모두 git 09d2ea69 clean (`logs/gcap_fits.log`, tmux `gcap_cont`·`gcap_k8192`·`gcap_k8192_r1`·`gcap_k8192_r2`). tmux `gcap_k8192` 는 `k8192 0 0 1 2` (GPU 0 에서 r0→r1→r2 순차) 이고 r1·r2 는 별도 세션이 먼저 시작해 마커 `.started_k8192_r{1,2}` 를 만들었으므로 순차 루프가 건너뛴다 (`run_gcap_fits.sh:26`). 따라서 §1.1 에 대한 지적은 고칠 수 없고 캐비엇으로만 남는다; 아래 MUST 는 모두 아직 시작하지 않은 §1.2–§1.4 (선택·test 평가·수용·분석) 에 관한 것이다.
- 분류: MUST = 결과를 무효로 만들거나 과제·규칙을 어김 / SHOULD = 모호함·공개 누락·검사 누락 / NIT = 문구.

## 확인한 것 (결함 없음)

- **§0 수치 전부 파일과 일치** (`check_fit_fields_U28NR32GCAP.out`): `n_iter 31, it_best 30, restart 0, kappa 0`; `ll_val 152.23176788511105`, `ll_train 188.2857805090495`, 간격 36.054; `ll[30] − ll[29] = −1.5030e-4 < 0` 이고 `tol·|ll| = 1.883e-4` → legacy 규칙은 it 30 에서 발동, gcap 규칙 (0 ≤ dll) 은 발동하지 않음 (등록 §0 의 정지 사유 서술이 맞다; it ≥ 20 에서 조건을 만족한 것은 it 30 하나); `n_reseed 29980`, `kron_batched [1,1,1]`, `cand_ll_val 152.23176788511105 / 152.124183756404 / 151.79374075040246`; 세 후보 모두 마지막 스텝이 학습 LL 감소 (r1 −2.09e-2, r2 −3.27e-3). K 격자 ll_val (kron 16 25.21 … 2048 150.39 · 4096 152.23; full 최고 K128 80.06), full32 ll_val 54.033, `em_sec` 합 128781.04 = raw `meta|em_sec`. sha256: kron4096 2d72a434…f569 ✓, full32 d572e0ac…e215 ✓, 세 후보 849d…/ee1b…/7fb3… ✓, ckpt `~/t2/conf/ckpt/d2sx_UMi28NR32_N160000_a1_best.pt` sha256[:16] 463da87aa8dbfb61 ✓ (raw `meta|stagec_ckpt_id` 의 `epoch=232 best_epoch=232 role=best` ✓). 기존 raw 의 arm 은 정확히 §1.3 의 11 개 (manifest `arms`, 청크 키 확인) — chk 의 arm 목록은 맞다 (선례 `run_scale2.sh:53` 과 같다).
- **정지 규칙·"정확히 50회"·종료 사유 4 갈래**는 manifest 대로 구현돼 있다: `gmm_em_gpu.py:167–189` 검사 순서 numerical → (검증점) patience → tol → budget; gcap 의 tol 은 `0 ≤ dll < tol|ll|` 만 (`:186–187`); `n_iter = steps+1 = 51` 에 `it == n_iter−1` 에서 break → 상태 0..50 평가, M-step 50 회 (`fit_gcap_cont.py:60–64`); 검증은 `it % 10 == 0` → 0,10,…,50 (6 점); `best` 초기 −inf 라 상태 0 포함. B 의 재시드 seed 튜플 `[…, 4096, 0, 0, 1]` (로그 확인), C 는 runner.cmd_fit 의 튜플 그대로 (`fit_gpu.py:45`). 기본 경로 diff 는 전부 opt-in 추가 (git diff 확인; T1 의 "비트 동일" 자체는 GPU 가 필요해 여기서 다시 돌리지 않았다 — S5).
- **선택이 test 에 닿지 않는다**: 학습·검증은 `train_rng(…, 7/8)` 스트림, BLER 시행은 `trial_rng` 스트림 (common.py:228,236); `ll_test` (스트림 10) 는 채널 표본 우도이고 기록만 된다; 선택 (§1.2) 은 검증 LL 뿐이며 test 평가는 선택 뒤에만 돈다.
- **복사본 fits 폴더 경로**: `load_fits` 는 존재하는 K 파일만 읽고 (`arms.py:72–82`, D2_KS 에 8192 포함), 실행 경로가 fit 파일에서 읽는 필드는 `ll_val` (gmm_selection) · `covs`·`pi` (module_h_priors) · full32 의 `Chat` (baseline) · `sec` (fit_cost_meta) 뿐 — `.cont50.npz` 와 병합 K8192 파일 모두 갖고 있다. `run_manifest.py` 는 fits 폴더를 경로로만 적는다 (`:176`). full32 54.03 < 152 이라 b\* = kron ✓.
- **수용 논리**: `eval_accept --ref-raw` 는 R5-genie 4 키를 태그의 모든 청크·모든 시행에서 기준 raw 와 대조한다 (`eval_accept.py:99–133`); `--ref-arms all` 은 기준 청크의 `<arm>|KEYS_RAW` 전부 — 기준 raw 의 11 arm 과 chk 의 11 arm 이 같다. 절대 경로 `--ref-raw` 는 `os.path.join(C.CONF, <abs>)` 가 그대로 돌려줘 동작한다.
- **결합 분석 = 기존 파이프라인**: `gcap_compare.py --old = --new` 가 기록값을 그대로 재현했다 (`gcap_compare_selfcheck_old_eq_new.txt`): 판정점 −3/0/+3, 173:13 (7.3e-37) · 136:12 (9e-28) · 82:7 (2.4e-17), pooled 391:32, POWERED 3/3, SNR@0.1 격차 +2.29 dB [+1.98, +2.61], ΣF 958 · 599 · 127, R 0.432010 [0.402, 0.462] (= `tables_D2_U28NR32B16e4.txt:308–313`, RESULTS §21.3 pairB 값). 부트스트랩이 pair 순서에 무관한 이유: `exp_0925_analysis.gain` 은 호출마다 `default_rng(20260925)` (`:57–64`), `recovery_ci.boot` 는 seed 20260926 인자 — 3 arm 표에서도 전체 표와 같은 난수 흐름.
- **일정 (확인한 시각 기준)**: 프로브 K8192 183 s/반복 (`logs/gcap_probe.log`) → 예산 500 상태면 ≈ 25.4 h + 데이터 12.7 min → r0 ≤ 10-18 01:10 CDT, r1·r2 ≤ 01:15 CDT (셋이 병렬). cont 는 데이터 764 s + K4096 ≈ 92 s/상태 × 51 ≈ 10-17 01:00 CDT 쯤. GPU 메모리 24.2 GiB (프로브) / cont 26.8 GiB — 97.9 GB GPU 에 여유.

## 결함 (심각한 것부터)

### M1 · MUST · 주 실행에 메모리 가드 (`--worker-gb`) 가 없다 — K8192 면 95 워커가 가용 RAM 을 넘는다
- 근거: `Demo/t2_gmm.py:26–41` `GMMPriorB` 는 `covs`·`U`·`covinv` 세 개의 (K, N, N) complex128 배열을 들고, `tilted_moments` (`:44–52`) 가 EP 호출마다 `A`, `Sig`, `slogdet(A)` 임시를 더 만든다. K = 8192, N = 128 이면 배열 하나 2.0 GiB → 상주 6 GiB + 임시 ≥ 6 GiB. 선례 실측: SCALE16e4 §1 "메모리 가드" 행 — K 4096 RSS 스모크 최대 **7.367 GB** → G = 8.0 (`logs/run_D2_U28NR32B16e4.log` 머리말 `--worker-gb 8.0`, `jobs = 99`; raw `meta|worker_gb 8.0`). K 8192 는 그 두 배 ≈ 14.7 GB/워커. §1.3 의 명령은 `taskset -c <95>` + `runner.py run … --arm M-ours-bstar R5-genie` 로 `--worker-gb` 가 없어 `jobs = min(sched_getaffinity, tasks) = 95` (`runner.py:661–662`) → 95 × ~14.7 ≈ 1.4 TB > MemAvailable 981 GiB (`free -g`, 23:36 CDT). OOM 이면 워커가 죽고 청크가 빠진다 (runner 는 자기 OOM 을 재시도하지 않는다).
- 수정: (1) §1.3 "시간" 행의 개발 청크 측정을 **jobs = 1 로 돌려 워커 RSS 를 재는 것** (예: `/usr/bin/time -v` 의 `Maximum resident set size`) 으로 명시하고, SCALE 규칙 (RSS 최대 + 5 % 를 0.5 GB 단위로 올림) 으로 G 를 정해 §5 에 적는다; (2) 주 실행 명령에 `--worker-gb G` 를 넣는다 (`jobs = min(95, floor(0.8·MemAvailable/G))`; G ≈ 15.5 면 ≈ 50 워커); (3) SCALE 의 멈춤 규칙 (RSS > 1.25·G 또는 OOM → 멈추고 알린 뒤 `G′` 로 `--resume`) 을 §1.5 에 옮긴다; (4) 시간 추정을 다시 쓴다 — K2U28NR32B16e4 (bstar K2048 + genie, 99 워커) 가 청크당 중앙값 2022 s 였고 (`logs/run_D2_K2U28NR32B16e4.log`, 192 청크) GMM EP 비용은 K 에 비례하므로 K8192 ≈ 8000 s/청크 → 50 워커면 448/50 → 9 회전 ≈ 20 h (B = K4096 이 선택되면 G = 8.0, 95 워커, ≈ 5 회전 × 4000 s ≈ 6 h). 10/21 안이다. §1.3 에 "G 는 §5 뒤 바꾸지 않는다 (올리기만, 선례)" 도 적는다.

### M2 · MUST · 수용 호출이 실행 가능한 형태로 고정돼 있지 않다 — chk 호출은 지금 문구대로면 구조적으로 FAIL
- 근거: §1.3 수용 행은 chk 를 "chk 호출 (`--ref-arms all`, 청크 계획 {0 dB: (0, 40)})" 로만 적는다. `eval_accept.py:67–81`: `want = {(C9, s) for s in points.get("C9", CELLS["C9"]["snrs"])}` 이고 `plan = [(skip0 + 40k, 40) for k in range(n // 40)]` 이라 **`--points C9:0 --n 40` 이 없으면 7 점 중 6 점 missing + 청크 계획 불일치로 FAILED** 한다. chk 의 `--kron-K` 는 4096, `--ll-val` 은 A 의 152.23176788511105 (복사한 기존 kron4096 의 값) 이어야 하고, 주 실행 호출의 `--kron-K`·`--ll-val` 은 새 fit 의 값이며 `|diff| ≤ 1e-9` (`:88`) 라 repr 전체 자리가 필요하다. §1.3 은 "둘 다 OK 일 때만 §1.4 표를 결과로 쓴다" 는 게이트인데 호출 자체가 적혀 있지 않으면 결과를 본 뒤 플래그를 맞추게 된다. 실행 스크립트 `code/run_gcap.sh` 도 아직 없다 ("§4.1 에서 구현") — 동결 커밋 = 실행 커밋이므로 스크립트 없이 동결할 수 없다.
- 수정: §1.3 에 두 호출을 원문으로 적고 같은 문자열을 `run_gcap.sh` 에 넣어 동결 커밋에 포함한다 (선례 `run_scale2.sh:253`):
  - 주: `python code/eval_accept.py --tag U28NR32GCAPe:best:463da87aa8dbfb61:C9 --ntrain 160000 --kron-K <K> --ll-val <§5 repr> --ref-raw /home/HTJ/t2_wtS/conf/raw_U28NR32B16e4`
  - chk: `python code/eval_accept.py --tag U28NR32GCAPchk:best:463da87aa8dbfb61:C9 --ntrain 160000 --kron-K 4096 --ll-val 152.23176788511105 --n 40 --points C9:0 --ref-raw /home/HTJ/t2_wtS/conf/raw_U28NR32B16e4 --ref-arms all`
  - 스크립트에 전제 하나 추가: `results/gmm_fits_D2_U28NR32GCAPe/` 와 `…GCAPchk/` 에 파일이 정확히 2 개 (full32 + kron 하나) — `load_fits` 는 폴더에 있는 K 파일을 모두 읽으므로 (S7 과 같은 이유).

### M3 · MUST · 사용자 과제의 1 단계·3 단계 조항이 등록에 빠져 있다
- 3 단계 (`PROMPT_SERVER_GMMCAP.md:21`): "전체 적합이 10/18 안에 끝나지 않으면 사용자에게 알린다" — §1.1·§1.5 어디에도 적합 마감·알림 규칙이 없다 (§1.3 "시간" 행은 test 의 10/21 만). 프로브 수치 (183 s/반복, 24.2 GiB) 도 문서에 없다. 지금 일정 (세 재시작 병렬, 예산 소진이면 ≤ 10-18 01:15 CDT) 은 조항을 만족하지만, 재시작 하나가 죽어 다시 돌면 넘는다.
- 1 단계 (`:19`): "fit log (반복별 train/validation LL, 종료 사유) 를 확인하고 기록한다" — §0 은 요약만 적었다. 실제로 남아 있는 것은 fit 파일의 학습 `ll` 31 개와 it 30 의 검증 LL 하나뿐이다: `fit_edge_U28NR32B16e4.log` 에는 K4096 의 반복별 줄이 없다 (`fit_gpu._fit_one` 이 `log=` 를 넘기지 않음; 로그 `:12–22` 는 후보·병합 요약 줄만). 검증 LL 의 it 0/10/20 값은 어디에도 없다 (continuation 의 상태 0 재평가가 it 30 값을 다시 준다).
- 수정: §1.1 C 에 "적합 마감 10/18 CDT; 프로브 183 s/반복 → 재시작당 ≤ 25.4 h; 재시작 셋 병렬 (GPU 0/2/3); 재시작이 죽으면 마커를 지우지 않고 사용자에게 알린다" 를, §1.5 에 10/18 알림 규칙을 적는다. §0 (또는 §5) 에 학습 `ll` 31 값 (`check_fit_fields_U28NR32GCAP.out` 의 trajectory 줄) 과 "검증 LL 은 it 30 의 값만 존재, 반복별 검증 기록 없음" 을 적는다.

### S1 · SHOULD · 적합 비용 (01_RULES §5 "학습·적합 비용을 숨기지 않는다") 의 보고 방법이 없다
- GCAPe 폴더에는 full32 와 선택 fit 두 파일만 있으므로 raw 의 `meta|em_sec` = `fit_cost_meta` 의 폴더 합 (`runner.py:207–226`) = 2100 s + 새 파일의 `sec`. B 가 선택되면 `.cont50.npz` 의 `sec` 는 continuation 시간만이고 (A 의 10420 s, 격자 전체 128781 s 제외), C 면 K8192 세 재시작 합만이다. 분석표의 비용 열이 기존 run 과 다른 수가 된다.
- 수정: §1.4 에 "보고하는 적합 비용 = 기존 격자 128781 s + continuation (B) 또는 + K8192 세 재시작 (C); raw 의 `meta|em_sec` 은 폴더 두 파일의 합이라 그 수가 아니다" 를 적고, 두 수를 §6 에 함께 적는다.

### S2 · SHOULD · Q-K 한정어 "[K 상한 민감: 외삽 불가]" 의 처리가 두 경우에서 비어 있다
- §2.1: 최종 = C (K8192, 격자 끝) → "유지" (적혀 있음; 다만 SCALE 의 r·c_K 는 K/2 의 BLER 로 계산했는데 여기서는 K4096 raw 가 있으니 r 을 다시 계산할 수 있다 — 하겠는지 안 하겠는지 적어야 한다). 최종 = B (K4096, 이제 격자 내부) → "K 8192 까지 검사, 선택 K4096" 만 적고 한정어를 떼는지 말하지 않는다 (SCALE §2.1 정의로는 내부 b\* 는 '-'). §2.2 최종 = A → "기존 한정어 그대로" 인데 그 한정어의 전제 (4096 = 격자 끝) 가 K8192 적합 뒤에는 바뀐다.
- 수정: 세 경우를 한 줄씩 미리 정한다. 제안: C → 유지 + Q-K 재계산 안 함 (K8192 의 K/2 BLER 은 기존 raw 의 K4096 이므로 r 을 보고 전용으로만 적음); B → 한정어 삭제 대신 "K 8192 적합 (검증 LL Δ = …) 보다 검증 LL 높아 선택; 격자 내부" 로 교체; A → 기존 한정어 유지 + 같은 문장 병기.

### S3 · SHOULD · 라벨 문자열이 선례 형식과 다르다
- 선례: SCALE §2.3/RESULTS §21.3 "(i) 'UMi28 C9 (Nr 32) 에서 V1 이 b\* 보다 적게 실패 (배열 규모 축 측정, UNGATED)'", ROOM §2 "(… 에서 V1 이 b\* 보다 적게 실패 (prior·기전 축 측정, UNGATED))". §2.1 의 "(i) 'UMi28 C9 (Nr 32) 에서 V1 이 b\*(GCAP) 보다 적게 실패'" 에는 괄호 범위 (측정 종류·게이트 여부) 가 없고 "b\*(GCAP)" 의 정의가 라벨 문장에 없다.
- 수정: "b\*(GCAP) = §1.2 의 최종 fit (§5 경로·sha)" 을 §2.1 첫 줄에 두고, 라벨에 "(GMM 용량 확인 재평가, UNGATED)" 같은 괄호를 선례 형식으로 붙인다 (어떤 문구든 §2.1 에 고정하는 것이 요점).

### S4 · SHOULD · CPU 96 스레드를 이 실험이 혼자 다 쓰는 계획이다 — 같은 창의 우선순위 1·2 실험과 충돌
- COMMON §2 표: E3′ SBL32 test 와 E5 QAM16 test 가 같은 10/19–21 CDT 창이다. §1.3 은 주 실행 95 + chk 1 = 96 스레드라 다른 세션 몫이 0 이고, 전제 "합이 96 을 넘으면 시작하지 않고 묻는다" 는 결국 어느 한쪽이 기다린다는 뜻이다. M1 의 가드가 들어가면 K8192 때 워커 ≈ 50 으로 떨어져 45 스레드가 남는다.
- 수정: §1.3 에 `taskset` 코어 목록을 실제 번호로 적고 (공통 규칙의 NUMA 1·3 집합 `24-47,120-143,72-95,168-191` 안에서 주 실행 N 개 + chk 1 개), 다른 등록 runner 와의 순서 (어느 쪽이 먼저, 몇 스레드씩) 를 지금 사용자에게 묻는 한 줄을 §1.3 전제에 넣는다.

### S5 · SHOULD · §4 가 주장하는 자체 검사의 출력이 어디에도 없다
- §4.1: T1–T4 (`gcap/test_gcap_em.py`) 통과, `gmm_em_gpu._demo` GPU↔CPU 통과 — `gcap/` 에는 .py/.sh 만 있고 `logs/gcap_*` 은 cont·fits·k8192·probe 넷뿐이다. §0: "`gcap_compare.py` 를 old = new 로 돌리면 이 수치가 그대로 나온다 (23:23 CDT, §4.2)" — §4.2 는 비어 있다. 프로브 출력 (상태 0 재평가 rel diff 0.000e+00 둘, K8192 183 s/반복 · 24.2 GiB, 프로브 전용 seed r = 99 로 K8192 M-step 2 회의 ll [−206.751, −36.687, 121.07]) 도 아직 문서에 없다 — 동결 전에 K8192 EM 반복을 (후보가 아닌 seed 로) 둘 본 사실은 공개해야 한다.
- 수정: 동결 전에 `CUDA_VISIBLE_DEVICES=<빈 GPU> python gcap/test_gcap_em.py <(git show 5bcffc3e:conf/code/gmm_em_gpu.py)` 와 `python code/gmm_em_gpu.py` 를 한 번씩 돌려 `gcap/test_gcap_em.out`·`gcap/gmm_em_gpu_demo.out` 로 저장하고 §4.2 에 적는다; gcap_compare 자체 검사는 이 폴더의 `gcap_compare_selfcheck_old_eq_new.txt` 를 §4.2 에서 가리키면 된다; 프로브 네 줄을 §5 에 옮긴다.

### S6 · SHOULD · §1.2 선택 단계가 손으로 하는 비교다
- 세 ll_val (A 파일, B `.cont50.npz` — `it_best > 0` 일 때만 후보, C 병합) 을 비교하는 코드가 없다. `eval_accept --ll-val` 의 허용오차 1e-9 때문에 §5 에는 repr 전체 자리가 필요하다.
- 수정: 세 파일의 `ll_val`·`it_best`·`stop`·`status` 를 repr 로 찍고 argmax 를 쓰는 10 줄짜리 스크립트 (`gcap/select_gcap.py`) 의 출력을 `gcap/select_U28NR32GCAP.out` 으로 남기고, 그 뒤에 복사·sha 대조를 한다.

### S7 · SHOULD · 선례의 사후 산출물·검사가 빠졌다
- 선례 (SCALE·ROOM) 는 raw 마다 `code/run_manifest.py --tag <T>` (→ `results/review_next/run_manifest_<T>.json`) 와 `guard_report` 를 만든다; §1.3 순서에는 없다. `run_manifest.py` 는 raw 만 읽고 fits 폴더는 경로로 적으므로 `.cont50` 복사본에 걸릴 필드가 없다. `run|git` 에 `+dirty` 가 없다는 확인도 (FIGHSYDMI §1 "이른 확인" 선례) 적어 두면 좋다.
- 수정: `run_gcap.sh` 순서에 `run_manifest.py` (GCAPe·GCAPchk) 를 넣고, 첫 청크가 나오면 `run|git` 만 읽어 `+dirty` 유무를 보는 줄을 §1.3 에 추가.

### S8 · SHOULD · 적합 폴더 복사본의 `sec` 와 `n_tk_eye` 등 B 전용 필드의 해석을 적어 둔다
- `.cont50.npz` 는 `cand`·`cand_ll_val`·`sec_best` 가 없고 `steps_done`·`status`·`n_tk_eye`·`src_sha256` 가 있다 (`fit_gcap_cont.py:76–83`). 실행 경로는 문제없지만 (위 "확인한 것"), §5 에 "복사본은 arms.fit_path 이름이지만 필드 집합이 다르다 (어떤 것이 없고 어떤 것이 추가됐는지)" 를 적어 기록 감사가 놀라지 않게 한다. `status == "completed"` 와 `stop == "budget"` 을 §5 의 "50회 완료" 판정 근거로 명시.

### N1 · NIT · §0 "DFT 파일럿 `eig`" 는 자기모순
- `common.make_pilots` (`:161–175`): "DFT unless the transmit-side ensemble covariance is informative; then … eigenvectors (the 'eig' rule)". raw 이름의 `_eig_` 는 eigen-aligned 파일럿을 뜻한다 → "eigen-aligned 파일럿 (`eig`)".

### N2 · NIT · manifest `written` 의 "13:2x" 자리표시
- 커밋 시각 13:27:21 KST (= 23:27:21 CDT) 로 적는다 (manifest 자체는 §1.1 과 함께 바꾸지 않는다면 §5 에 보충).

### N3 · NIT · `run_gcap_fits.sh` 의 마커 파일
- 재시작이 죽어도 `.started_k8192_r*` 가 남아 재실행이 조용히 건너뛴다 (`:26`). 복구 경로 (마커 제거 = 삭제 명령 → 사용자가 한다) 를 §1.5 에 한 줄.

### N4 · NIT · chk 의 SNR 0 dB
- 선례 chk 는 격자 첫 SNR (−12 dB; `run_scale2.sh:238` `--snr $S0`). 0 dB 도 좋지만 (판정점) 이유를 한 줄 적는다. 1 스레드 기준 소요 ≈ 2 h (선례 7230 s, `logs/run_D2_U28NR32B16e4chk.log`).

### N5 · NIT · §1.1 C "최대 500 상태" 의 뜻
- gcap 은 상태 0..499 (M-step 499 회), legacy 는 M-step 500 회 (마지막 미평가) — manifest 에는 있고 §1.1 에는 없다.

### N6 · NIT · `fit_gpu.py --merge` 의 소요 시간
- `main` 과 `ref_task` 가 `_sets` 를 두 번 불러 데이터를 두 번 만든다 (`fit_gpu.py:122–123`, `runner.py:1057–1060`) → CPU 2 스레드에서 ≈ 25 min. 멈춘 것으로 오해하지 않게 §1.1 에 적는다.

### N7 · NIT · §4.3 에 검토 시점의 실행 상태를 적는다
- 위 "검토 시점의 상태" 네 시각과 "§1.1 은 검토 전에 시작됐다 (manifest 선커밋이 안전장치)" 를 §4.3 에 그대로 옮긴다.
