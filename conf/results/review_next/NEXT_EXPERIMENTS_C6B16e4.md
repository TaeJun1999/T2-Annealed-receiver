# NEXT_EXPERIMENTS_C6B16e4 — 여차원 셀 C6 (Nr=16) 의 동일예산 점 N′ = 1.6e5 (사전 등록 v2)

- 작성: 2026-09-24 19:4x CDT 초안(v1) → 적대적 검토 2건(설계·통계 9건, 실행 가능성·코드 11건; 세션 에이전트 원문은 작업 로그) 반영 v2 20:2x CDT, Claude Code (Fable 5.1). 동결 시각 = 커밋 시각(`DECISIONS.md` 같은 줄). **결과 관측 전**: 이 예산의 Nr=16 체크포인트·적합은 BLER 로 평가된 적이 없다(학습·적합은 GPU 큐에서 진행 중, §4). 사용자 결정 2026-09-24 17:45 CDT 무렵 ("C6(Nr=16) 1.6e5 동일예산" 승인; 후보 조사 워크플로 wf_29534d69-69d). 커밋 뒤에는 §1~§3 을 바꾸지 않는다; 바꿔야 하면 사용자 승인 + `DECISIONS.md`.
- 틀: `10_SPEC_stageC.md` §7 (C6 정의·UNGATED 지위·예측·무결성, 2026-09-23 00:40 KST), §6d(동일예산)·§6l(격자 확장)·§3d(발산 사다리), `01_RULES.md` §4·§5·:76, `08_SPEC_analysis.md` §2(판정점 3개·power guard·앵커 = baseline), review_next v3 §0(테스트 0..2559, `_best.pt`, CPU 수신기, "p ≥ 0.05 는 판정하지 못함이지 차이 없음이 아니다"), `NEXT_EXPERIMENTS_B32e4.md` §1(같은 형식의 동일예산 재실행 — 이 문서는 그 규칙을 Nr=16 에 옮긴 것).
- 목적: **C6 의 1e4 결과(회수율 0.838, b\*/V1 = 3.98)가 소예산 효과인지** 헤드라인 예산 1.6e5 에서 같은 시행으로 확인한다. 이 질문에는 §2 의 **회수율 대역 규칙**으로 답하고(표 B 문자열만으로 답하지 않는다), 1e4 결과를 본 뒤 고른 예산 점이므로 §3 은 약한 예측이고 추세 검정은 등록하지 않는다.

---

## 0. 출발점 (판정에 쓰지 않는다)

| C6, N=1e4 (`tables_D2_NR16run2.txt`, `raw_NR16run2` 재집계, 테스트 0..2559, n=2560, @16) | −3 dB | +0 dB | +3 dB |
|---|---|---|---|
| b\* (kron K=128, 내부) 실패 (BLER) | 207 (0.081) | 81 (0.032) | 47 (0.018) |
| V1 (last-EMA @1688; best 미저장) | 52 (0.020) | 18 (0.007) | 12 (0.005) |
| R5-genie | 22 (0.009) | 10 (0.004) | 8 (0.003) |
| b\*→V1 a:b | 163:8 | 66:3 | 37:2 (pooled 266:13, POWERED, `3/3 … 0/3`) |
| 회수율 (b\*−V1)/(b\*−genie) | 0.838 | 0.887 | 0.897 |

대조군 b\*→b\*-scalar 62:158 (b\* 우세 3/3). V0 BLER −3~+3 dB 1.000, +15 dB 0.710 (가드 전 SNR 발동, −3 dB 2560/2560). 같은 예산 Nr=8 (C2, raw_B1e4): 회수율 0.490. 1.6e5 의 C2 (헤드라인) 회수율 0.470 (테스트 실패 623/371/87), 3.2e5 0.453. 1e4 의 GMM 격자: kron ll_val 16 −30.55 / 32 −12.99 / 64 −1.84 / **128 +5.696** / 256 +4.018 / 512 −0.514 (N/K 가 작아 큰 K 가 굶는다: kron 512 재시드 1010~1674/재시작); GB′ 비 0.314~0.474 (median 0.343). §7 예측 대조(EXPERIMENTS.md:23): (1)(2) 적중, (3) "GMM 쪽이 더 나빠져서" 는 문구대로는 아님(V1 이 더 많이 내려감), (4) 적중.

**이미 도는 것 (BLER 없음; 20:21 CDT 관측)**: tmux `nr16b`, `conf/code/run_nr16b.sh` (47f46477), 09-24 17:47 CDT 시작. score 학습 `train_nr16.py --ntrain 160000 --fits-tag NR16B16e4` (GPU 5; epoch 452, val 1.8741e-01 매 epoch 개선 중, 20.9 s/epoch; `_best.pt` 저장됨). GMM 격자 → `results/gmm_fits_D2_NR16B16e4/`: full 16 −29.634 / 32 / 64 4.249 / 128 14.735 (480 iter) / 256 16.611 (**상한 500 도달**, best@490) / 512 13.507 (51 iter, 재시드 2392); kron 16 −28.834 / 32 −8.699 / 64 7.710 / 128 24.365 / 256 38.407 / 512 50.185 / **1024 병합 58.857** (r2; r0/r1 57.014/57.324; 재시드 477) / **2048 병합 61.982** (r1; r0/r2 61.852/61.774; 재시드 17313/23279/16695) → 계열 최대 K → **kron 4096 재시작 0/1/2 실행 중** (GPU 0/1/3, 19:25~19:30 CDT 시작, 각 32.8 GB; BLER 무관, 01_RULES:76). full 은 정확 경로, kron 은 일괄 경로(`em_batched_check_nr.py` PASS: N′=1.6e5 K=512 6 반복 Δll 1.1e-12, 재시드 활성 N=1e4 K=512 371/371 동일; `results/nr16b_batched_check.txt` — 검증 범위는 K ≤ 512 이며 kron 2048·4096 의 재시드 수만 회 상황은 코드 검사(공통 재시드 분기)로만 보증, §5 에 명시). 큐 파일은 비어 있고 워커는 대기 중 — **4096 병합과 GB′ 재실행은 §4 의 담당대로 수동으로 넣는다.**

## 1. 고정되는 것

| 항목 | 값 |
|---|---|
| **셀·예산** | C6 = Nr 16, Nt 4, T 16, Tp 4, 7 SNR (−3…+15; **결과 뒤 격자를 늘리지 않는다**), n=2560, 테스트 시행 **0..2559** (NR16run2 와 같은 시행 → 예산 간 짝 비교; 공개). N′ = 160000: 채널 집합 하나 = `arms.training_set("D2","S2",16,4,160000)` (스트림 7) — GMM 적합(`runner._sets`)과 score 학습(`score.train` → `A.training_set`, `score.py:657`) 이 **같은 집합**(score 는 자체 9:1 = 144000/16000 분할, GMM 검증 5000 = 스트림 8, `runner.N_VAL`). 가우시안 arm 의 Chat 도 같은 적합 |
| **지위** | §7 그대로: D1 형제가 없으므로 체크포인트는 **UNGATED** → 이 예산 점은 **"기하·예산 축 측정"** 이며 arm 판정이 아니다. D1 형제 게이트 PASS 주장은 C2 에만. 헤드라인(C2 1.6e5 B16e4k) 불변; C6 는 어느 결과에서도 헤드라인이 되지 않는다 |
| **GMM 격자와 b\*** | 기본 격자 full K ∈ {16,…,512}, kron K ∈ {16,…,2048}; 선택 = validation ll 최대(`arms.gmm_selection`; `arms.D2_KS` 에 4096·8192 포함, `load_fits` 는 존재 파일만 적재). **반복 규칙(B32e4 §1 과 동일)**: b\* 가 어느 계열이든 그 계열의 최대 K 이면 2K 를 같은 프로토콜(kappa 격자·재시작 3·상한 500·검증 조기 종료)로 적합해 다시 선택; 멈춤 = 계열 최대 K 의 ll_val ≤ K/2 (내부). kron 4096 은 규칙대로 이미 진행 중(§0). **K = 8192 가 필요해지면 사용자 결정 뒤에만**(일괄 EM ≈ 50 s/iter 외삽 → 재시작당 ≤ 7 h; E-step (n,K) float64 3개 ≈ 31.5 GB 실사용, 예약 ≈ 65 GB → 96 GB 1장에 들어감); 거부되면 b\* = 격자 끝 + 캐비엇. 재시작 후보 파일이 누락되면 같은 시드의 그 재시작만 재실행(결정적)하고 §5 에 적는다. 상한 500 도달·재시드 수·구현 경로는 §5 에 파일별로. BLER 은 선택에 쓰지 않는다 |
| **체크포인트·평가 가중치** | `ckpt/d2sx_NR16_N160000_a1.pt` (last-EMA) 와 `ckpt/d2sx_NR16_N160000_a1_best.pt` (P0-1 코드). **측정 판정 태그 `NR16B16e4` = `_best.pt`** (v3 §0); **`NR16B16e4last` = last-EMA, 보고 전용**(1e4 C6 는 last-EMA 만 있으므로 예산 비교 표는 last 로). attempt 1 만. rung `D2SXNR16160000` (시드 규칙 그대로; N_train 표시는 47f46477 로 수정). "시도했다" = patience 종료 또는 ≥ 200 epoch (01_RULES §5; `train_nr16.py` min_epochs 200, patience 20 이 충족) |
| **학습 실패 처리** | `stopped_by=diverged` 또는 `aborted=True` → 10_SPEC §3d 사다리: 시행 2 = 기울기 클리핑 1.0, 시행 3 = 시행 2 + lr/3 (`score.GRAD_CLIP_LADDER`/`LR_DIV_LADDER`, `run_d2_sx.py --fallback` 과 같은 방식으로 `train_nr16.py --fallback 2\|3` 을 추가; 같은 rung·attempt = 같은 데이터 스트림, 체크포인트 `d2sx_NR16_N160000_a1_fb<k>.pt` / `_fb<k>_best.pt`), 시행 간 선택은 val loss 만, 발산 체크포인트로 평가하지 않는다; 시행 3 도 실패 → "학습 실패", BLER 없음. `max_epochs`(3000) 정지는 유효 |
| **σ 격자** | `NR16` (09-22 13:24 CDT `runner.py sigma --tag NR16` 로 C6 에서 측정, 20 점 [3.283e-02, 4.915e-01]; `sigma.py:34` 가 1e4 적합의 full K=32 Chat 를 쓰므로 N_train 의존은 Chat 를 통해서만, 약함) 을 **재사용**한다 — Nr=8 에서 모든 예산이 한 격자를 쓴 관례와 같다. 학습·GB′ 모두 `sigma_tag="NR16"` |
| **실행 (테스트 집합, 전 arm = NR16run2 와 같은 구성)** | ① `runner.py run --testbed D2 --cell C6 --prior S2 --n 2560 --chunk 40 --ntrain 160000 --stagec-ckpt /home/HTJ/t2/conf/ckpt/d2sx_NR16_N160000_a1_best.pt --tag NR16B16e4`; ② 보고 전용: 같은 명령을 `…/d2sx_NR16_N160000_a1.pt --tag NR16B16e4last`. 선행: `ln -s gmm_fits_D2_NR16B16e4 results/gmm_fits_D2_NR16B16e4last`. 수신기 CPU complex128, 16 반복, `arms.LOOP` 그대로. 그 뒤 `runner.py analysis --tag …`, `run_manifest.py --tag …`, 수용 검사. **§5 가 채워져 커밋된 뒤에만 ①② 를 시작한다** |
| **수용 검사** | (a) 격자 완전성: §5 를 채우기 전 `gmm_fits_D2_NR16B16e4/` 에 full {16..512} 6 개 + kron {16..4096} 병합 9 개(8192 는 결정에 따라) 전부 존재, K ≥ 1024 는 후보 `.k0r{0,1,2}.npz` 3 개 확인; (b) 태그마다 점마다 raw 청크 정확히 {(40k,40): k=0..63}, meta `ntrain=160000`, `bstar`·`kron_K`·`ll_val\|kron` 이 §5 최종 선택과 일치, 두 태그의 `bstar`·`kron_K`·`em_sec` 동일, fits_dir 같은 디렉터리; (c) `stagec_ckpt_id` sha·epoch·best_epoch·role 이 §5 와 일치(best: epoch == last.best_epoch); Demo 해시 동일; 표 머리말 N_train=160000; (d) **두 태그 모두 7 SNR 전 시행에서 `R5-genie\|blk_err`·`\|ber`·`\|tauL_gmean`·`\|alphaD` @1..16 이 `raw_NR16run2` 와 비트 동일**(재현 검사; genie 는 학습·적합 무관); (e) GB′ 로그의 `GMM b* = (계열, K)` 가 §5 최종 b\* 와 같고 npz 가 격자 완료 뒤에 쓰였을 것(학습 종료 시 자동 실행된 첫 GB′ 는 잠정 격자 기준이므로 **폐기**하고 재실행본만 인용). **선행 코드**: `b32e4_accept.py` 를 태그·ntrain·셀·기대값·참조 raw 인자로 일반화(또는 `nr16b_accept.py`), 회수율 CI 스크립트(아래). 어긋나면 그 실행 무효 → 원인 기록, 새 태그 재실행 |
| **측정 판정 (C6, 태그 NR16B16e4)** | `08_SPEC` §2 표 B: `M-ours-bstar → M-ours-dscore-C-V1`, 판정점 = 앵커 b\* 의 BLER@16 이 [0.005, 0.9] 안에서 \|log10(BLER/0.1)\| 최소 3 SNR (자동; 1e4 에서는 −3/0/+3), 점마다 exact 양측 부호검정. **유지 = `power guard … -> POWERED` 이고 `second arm fewer failures at k/3 points` 의 k ≥ 2.** `significant` 토큰은 판정 기준이 아니다. 대조군 `M-ours-bstar → M-ours-bstar-scalar` 도 같은 형식으로 보고 |
| **회수율 대역 (목적 질문의 규칙; 측정 판정 태그 `_best` 로 계산, last 값도 나란히)** | 회수율 R = (b\*−V1)/(b\*−genie) 를 −3 dB(1차) 와 판정점 3 점 합에서 실패 수로 계산하고, **같은 시행에서 세 arm 을 묶은 paired bootstrap** (시행 인덱스 복원추출 B = 2000, `numpy.random.default_rng(20260926)`, 백분위 5/95 → 90% CI) 을 붙인다(선행 코드 `recovery_ci.py`, B32e4·B16e4k 에도 같은 계산을 적용해 나란히). 대역(−3 dB 점추정): **R ≥ 0.70 → "기하 효과 대부분 유지"; 0.60 ≤ R < 0.70 → "일부 유지"; R < 0.60 → "대부분 소예산 효과"**. C2 1.6e5 값 0.470 과 1e4 C6 값 0.838 을 옆에 찍는다. **표 B "유지" 라벨은 회수율 대역과 반드시 같이 인용하고 단독으로 쓰지 않는다.** 대역 문장은 셀·예산 한정이며 arm 주장이 아니다 |
| 보고 전용 | C6 예산 표(행 1e4 · 1.6e5 last · 1.6e5 best): −3 dB 실패 수·BLER(b\*, V1, genie), pooled a:b, SNR@0.1 격차(격자 밖이면 "n/a" 그대로); V0·V4·V4b, F3 가드 발동률(전 arm); best 대 last V1 짝 부호검정(C6); 동일예산 GB′ (재실행본; 1e4 GB′ 와 나란히); 격자 표(재시작별 ll_val·n_iter·it_best·재시드·구현 경로). **추세 검정 없음**; 이 결과를 보고 예산 점을 더 추가하려면 별도 등록 |
| 비용·일정 | GPU: 학습 ≈ 21 s/epoch × patience 정지 시점(1e4 는 1688 epoch) → 예상 5~17 h (17:47 CDT 시작); kron 4096 3 재시작 병렬 (≈ 25 s/iter 외삽, 재시작당 ≤ 3.5 h). CPU: ①② 각 **≈ 4.5 h** (NR16run2 168.6 min at K=128; Module H 비용이 K 와 함께 커져 K=4096 이면 ≈ +100 min; K=8192 면 ≈ 6 h) |

## 2. 라벨 (여기서 고정; "측정" 이지 arm 판정이 아니다. UNDECIDED / 비유의는 "판정하지 못함" 이며 어느 쪽의 증거도 아니다)

| 표 B `b\* → V1` (C6, NR16B16e4) | 기록 |
|---|---|
| (i) 유지: POWERED 이고 second arm fewer ≥ 2/3 | "C6 동일예산 우위가 N′ = 1.6e5 에서도 유지 (기하 축 측정, UNGATED)" — **§1 회수율 대역 문장과 반드시 함께** |
| (ii) POWERED 이고 first arm fewer ≥ 2/3 | "N′ = 1.6e5 에서 C6 우위 없음 (GMM 우세)" — 회수율 대역 문장과 함께(음수·0 부근도 그대로) |
| (iii) POWERED 이고 어느 쪽도 ≥ 2/3 아님 | "판정하지 못함 (유의 방향 없음)" |
| (iv) UNDECIDED (판정점 < 3 또는 n_d < 6 인 점) | "판정하지 못함 (검정력 미달)" — 저-BLER 셀이므로 일어날 수 있다; SNR 격자를 결과 뒤 늘리지 않는다 |
| 학습 실패 (§3d 시행 3 까지) | BLER 미실행, "학습 실패" |

- (ii)(iii)(iv) 어디에도 "소예산 효과" 문구를 만들지 않는다 — 그 문구는 §1 회수율 대역에서만 나온다. 어느 결과도 헤드라인·C2 판정·§7 의 1e4 기록을 바꾸지 않는다. 문장 범위(§6f): C6 결과로 셀·예산 한정 없는 주장을 쓰지 않는다.

## 3. 미리 적는 예측 (빗나가면 그대로 쓴다; 1e4 결과를 본 뒤의 약한 예측)

1. 학습: 발산 없음, patience 정지, **epoch 900~2000**, best val < 0.19.
2. GMM: b\* = kron, **K=4096 이 K=2048 을 이겨 격자 끝**(1.6e5 는 N/K = 78 @2048, 39 @4096). K=8192 는 사용자 결정. 재시드 수는 K 와 함께 급증(2048 에서 이미 1.7~2.3만).
3a. 표 B (i) 유지 (POWERED, ≥ 2/3). 3b. 3점 모두 유의.
4. −3 dB: **V1 실패 40~65 (0.015~0.025)**(1e4 52, 예산 평평 가정), **b\* 100~170 (0.040~0.065)**(1e4 207; K 가 128 → ≥ 2048 로 커져 Nr=8 보다 개선 폭이 큼), genie 22 (같은 시행 → 동일). **회수율 −3 dB 0.65~0.80** → 대역 "대부분 유지" 또는 "일부 유지" (1e4 0.838 보다 낮지만 C2 1.6e5 의 0.470 보다 높음). 판정점 −3/0/+3 유지.
5. 대조군 b\*→b\*-scalar: b\* 우세(first arm fewer ≥ 2/3, 1e4 와 같은 방향). V0: 전 SNR 가드 발동, −3~+3 dB BLER ≥ 0.9 (1e4 는 +15 dB 0.71). V4·V4b 는 V1 과 비슷하거나 나쁨.
6. best 대 last V1 (C6): 판정하지 못함(pooled p > 0.05).
7. GB′ 비 median 0.35~0.55 (1e4 0.343 보다 커짐: GMM 이 데이터를 더 잘 씀).
8. 빗나갈 경로: (a) 회수율 < 0.6 → 대역 "대부분 소예산 효과" 로 기록, C6 범위 문장은 사용자; (b) V1 이 1e4 보다 나빠짐(입력 128 차원 + 동결 레시피) → 그대로 기록, 레시피 탐색 없음(A2); (c) K=4096 도 격자 끝 → K=8192 사용자 결정, 거부 시 캐비엇; (d) 발산 → §3d; (e) (iv) 검정력 미달 → 그대로 기록, 격자 확장 없음.

## 4. 선행 작업과 실행 현황 (갱신한다)

| 항목 | 상태 · 담당 |
|---|---|
| GPU 큐 `run_nr16b.sh` (학습, EM 검증, full 격자, kron 격자, kron 4096) | 진행 중 (17:47 CDT~); EM 검증 PASS 17:54; full 6 개·kron ≤ 2048 완료(§0); kron 4096 r0/1/2 실행 중 |
| kron 1024·2048 병합 (`fit_gpu.py 16 kron K 160000 NR16B16e4 --merge`, 수동) | 완료 19:2x / 19:48 CDT (Fable) |
| kron 4096 병합 → 반복 규칙(K=8192 는 사용자 결정) | **완료** 09-24 21:20 CDT (`--merge`, `logs/nr16b.log`): 병합 ll_val 63.1751571838059 (r2, 163 iter, best@160, 재시드 85594; r0/r1 62.979/63.163); 사용자 결정 21:12 CDT **K=4096 에서 멈춤** → b\* = kron 4096, 격자 끝 캐비엇 |
| 학습 종료 → 자동 GB′(잠정 격자, 폐기) → 격자 확정 뒤 `train_nr16.py --ntrain 160000 --fits-tag NR16B16e4` 재실행(학습은 완료 상태로 건너뜀) | **시행 1 DIVERGED** (09-24 23:46 CDT; §5) → 시행 1 의 자동 GB′(`d2_gbprime_NR16_N160000_a1.npz`, 발산한 last 파일 기준, 비 median 1.38·max 66.7) 는 **폐기**. §3d 시행 2 (`--fallback 2`, 클리핑 1.0) GPU 0 에서 23:49 CDT 시작; 시행 2 의 자동 GB′ 는 격자 확정 뒤 계산되므로 수용 검사 (e) 를 충족하면 그대로 인용 |
| 선행 코드: `train_nr16.py --fits-tag`, `runner.learned_budget` 표시 수정 (47f46477) | 구현 |
| 선행 코드: `train_nr16.py --fallback 2\|3`, 수용 검사 스크립트 일반화(격자 완전성·genie 비트 동일 포함), `recovery_ci.py`(paired bootstrap), fits 링크 `gmm_fits_D2_NR16B16e4last` | **구현** (Fable, 09-24 21:51 CDT 커밋): `train_nr16.py --fallback` (기본 동작 불변), `code/eval_accept.py` (B32e4 세 태그 + 격자 → OK, NR16run2 자기 참조 genie 검사 → OK 로 검증), `code/recovery_ci.py` (NR16run2 C6 −3 dB R 0.838 [0.781, 0.892], B16e4k C2 0.470 [0.427, 0.512]), 링크 생성 |
| §5 채우기 → 커밋 → 실행 ①② + analysis + manifest + 수용 검사 → §6 결과 | §5 완료·커밋(이 줄과 같은 커밋) → `code/run_nr16b_eval.sh 4096 63.1751571838059 c050d611b2c714a6 bf688d605691c7f7 d2sx_NR16_N160000_a1_fb2` (tmux `nr16beval`, 로그 `logs/run_nr16b_eval.log`, 끝 표시 `NR16B_EVAL_DONE`) 커밋 직후 시작 |

## 5. 평가 전 고정 기록 (실행 ①② 전에 채우고 커밋한다; 갱신 시각을 적는다)

| 항목 | 값 (채워질 것) |
|---|---|
| 격자: K 별(계열별) 재시작별 ll_val · n_iter · it_best(상한 500 도달) · 재시드 · 구현 경로(정확/일괄; 일괄 검증 범위 K ≤ 512), 병합 ll_val | [09-24 22:23 CDT, 격자 완료] 병합 ll_val (선택 재시작, n_iter/best@, 재시드). **kron** (κ=0, 재시작 3, 전부 **일괄 경로**): 16 −28.834 (r2, 155/150, 0) / 32 −8.699 (r2, 127/100, 0) / 64 7.710 (r2, 114/100, 0) / 128 24.365 (r1, 132/120, 0) / 256 38.407 (r1, 190/150, 0) / 512 50.185 (r1, 331/330, 0) / 1024 **58.857** (r2, 303/270, 477; r0 57.014 241/200 rs 6, r1 57.324 234/230 rs 4) / 2048 **61.982** (r1, 244/230, 23279; r0 61.852 164/160 rs 17313, r2 61.774 193/190 rs 16695) / 4096 **63.175** (r2, 163/160, 85594; r0 62.979 169/160 rs 86007, r1 63.163 223/220 rs 118097). **full** (κ ∈ {0,16,64,256} × 재시작 3, 전부 κ=0 선택, **정확 경로**): 16 −29.634 (r1, 275/270) / 32 −10.900 (r1, 495/460) / 64 4.249 (r0, 351/310) / 128 14.735 (r0, 480/470) / 256 16.611 (r0, 500/490, **상한 도달**) / 512 13.507 (r2, 51/50, 재시드 2392 — 성분 고갈로 조기 정지). 상한 500 도달은 full 256 뿐. 일괄 경로 검증 범위는 K ≤ 512 (재시드 활성 경우 포함); kron 1024~4096 의 재시드 수백~11만 회 상황은 공통 재시드 분기(코드 검사)로만 보증. 재시작 후보 누락·재실행 없음 |
| 확장 결정(K=4096 / 8192)과 시각 | [09-24 19:19 CDT] kron 2048 (61.85/61.98/61.77) > kron 1024 → kron 4096 r0/1/2 큐 추가 (Opus, `logs/nr16b.log`). [09-24 21:12 CDT] kron 4096 r0/r2 62.979/63.175 > 2048 병합 61.982 → 계열 최대 K; **사용자 결정: K=4096 에서 멈춤** (DECISIONS 11:12 KST) → b\* = kron 4096 병합값(r1 완료 후), 격자 끝 캐비엇 |
| 최종 b\*: 계열·K·ll_val(정확한 float), 내부 여부 / 격자 끝 캐비엇 | [09-24 21:20 CDT] **b\* = kron K=4096, ll_val 63.1751571838059** (재시작 2, 163 iter, best@160, 재시드 85594, ll_test − ll_test(Gaussian) 186.598 nat; 수용 검사의 `ll_val\|kron` 대조값). **격자 끝** — K=2048 병합(61.982) 대비 +1.193 nat 로 아직 오르는 중에 멈춤(사용자 결정 21:12 CDT, K=8192 미적합). full 최고(K=256 16.611, 상한 도달)는 b\* 보다 46.6 nat 낮다 |
| 체크포인트: last / best 의 sha256[:16]·epoch·best_epoch·stopped_by·aborted; best.epoch == last.best_epoch | [09-25 10:06 CDT] **§3d 시행 2** (`--fallback 2`, 기울기 클리핑 1.0, 같은 rung D2SXNR16160000·attempt 1 = 같은 데이터 스트림): `ckpt/d2sx_NR16_N160000_a1_fb2.pt` (last) sha256[:16] **bf688d605691c7f7**, epoch 1704, best_epoch 1684, role last; `ckpt/d2sx_NR16_N160000_a1_fb2_best.pt` sha **c050d611b2c714a6**, epoch 1684 = last.best_epoch ✓, role best, best val 1.784587e-01; stopped_by=patience, aborted=False; 09-24 23:49 ~ 09-25 10:04 CDT, 36,743 s, 21.6 s/epoch (`logs/train_d2sx_NR16_N160000_a1_fb2.log`) |
| §3d 사다리 적용 여부 | [09-24 23:49 CDT] **시행 1 DIVERGED**: epoch 1062 best val 1.814751e-01 → epoch 1064 train 9.589e+01 / val 8.963e-01 (발산 판정: best 의 3배 초과 연속 5 epoch, 1068 에서 중단), stopped_by=diverged, aborted=False, 21,210 s (`logs/train_d2sx_NR16_N160000_a1.log`; `LADDER_C.md` 행). 시행 1 체크포인트(`d2sx_NR16_N160000_a1.pt`, `_best.pt` @1062)는 보존하되 평가하지 않는다(§1·10_SPEC §3d). → **시행 2** = 동결 레시피 + 전역 기울기 노름 클리핑 1.0 (`train_nr16.py --ntrain 160000 --fits-tag NR16B16e4 --fallback 2`, 같은 rung·attempt = 같은 데이터 스트림, 체크포인트 `d2sx_NR16_N160000_a1_fb2.pt` / `_fb2_best.pt`), GPU 0, 23:49 CDT 시작. 시행 2 도 발산하면 시행 3 (+ lr/3); 시행 3 도 실패하면 "학습 실패", BLER 없음. 평가 스크립트 `run_nr16b_eval.sh` 는 체크포인트 stem 인자를 받도록 수정(§5 가 기록한 시행을 넘긴다) **[09-25 10:04 CDT] 시행 2 정상 종료**(patience, 1704 epoch, 발산 없음) → 사다리는 시행 2 에서 멈춘다. 대기 실행 시행 3 (`--fallback 3`, GPU 3, 00:18 CDT 시작)은 DECISIONS 6953d595 규칙대로 **열어보지 않고 10:04 CDT 에 중지**(rc=143; 로그·체크포인트·GB′ 미열람, 평가·선택·보고에 쓰지 않음) |
| σ 격자 태그·값 확인 (`NR16`, 출처 §1) | `results/sigma_grid_D2_NR16.txt` (2026-09-23 03:24:08 KST = 09-22 13:24 CDT, git 4ad41df9): 20 점 σ ∈ [3.283e-02, 4.915e-01]; 학습 로그 머리말 `sigma grid 'NR16' [3.2832e-02, 4.9152e-01] (20 pts)` 와 일치 |
| GB′ (재실행본; 기준 b\* 계열·K·ll_val, 비 min/max/median, worst excess; 자동 첫 실행본은 폐기) | [09-25 10:06 CDT] 시행 2 끝의 자동 GB′ — 격자 확정(21:20 CDT) 뒤 계산되어 수용 검사 (e) 충족: `logs/nr16b_gpu0.log` `[nr16] GMM b* = kron (kron K=4096) @N=160000` (§5 최종 b\* 와 같음), GMM 은 GPU 경로(CPU 루프 대비 최대 상대차 1.44e-14), 확산/GMM 디노이징 NMSE 비 **min 0.261 · max 0.508 · median 0.283**, worst excess (max 비 − 1) **−0.492** (σ 격자 NR16 20 점 전부에서 확산이 낮음); `results/d2_gbprime_NR16_N160000_a1_fb2.npz`. 1e4 (b\* kron 128): 0.314~0.474, median 0.343. 시행 1 의 자동 GB′ (`d2_gbprime_NR16_N160000_a1.npz`, 발산한 last 파일) 는 폐기(§4) |
| 선행 코드 커밋 해시, fits 링크 생성 시각, 수용 검사·CI 스크립트 | 47f46477 (`train_nr16 --fits-tag`, `learned_budget` 표시 수정, 큐·EM 검증), dad54e2e (`train_nr16 --fallback`, `eval_accept.py`, `recovery_ci.py`), e64652ed (`run_nr16b_eval.sh`). fits 링크 `gmm_fits_D2_NR16B16e4last → gmm_fits_D2_NR16B16e4` 09-24 21:50 CDT |

## 6. 결과 (2026-09-25 10:07~18:27 CDT, `run_nr16b_eval.sh` @2a36737c; 이 절은 추가만 한다)

**실행·수용**: ① NR16B16e4 (`_fb2_best.pt`) 10:07~14:16 CDT, ② NR16B16e4last (`_fb2.pt`) 14:16~18:27 CDT (192 워커, CPU complex128, 16 반복). `eval_accept.py` → **ACCEPT: OK -- NR16B16e4, NR16B16e4last** (`results/review_next/NR16B16e4_accept.txt`: 청크 {(40k,40)} 64 × 7 SNR, meta ntrain 160000, bstar kron / kron_K 4096 / ll_val 63.1751571838059, 두 태그 em_sec 동일, ckpt sha·role (best c050d611b2c714a6 / last bf688d605691c7f7), **R5-genie blk_err·ber·tauL_gmean·alphaD @1..16 이 raw_NR16run2 와 7 SNR 전 시행 비트 동일**, 격자 완전성 full 6 + kron 9·K≥1024 후보 3 개씩). manifest `run_manifest_NR16B16e4{,last}.json` (git 2a36737c, config_hash 51ae127c61aacdce). b\*·genie 실패 벡터는 두 태그에서 동일.

### 6.1 측정 판정 (C6, 태그 NR16B16e4 = `_best`; UNGATED → 기하·예산 축 측정, arm 판정 아님)

`M-ours-bstar → M-ours-dscore-C-V1` (`tables_D2_NR16B16e4.txt:368-373`): 판정점 −3/+0/+3 dB (앵커 b\* 자동), −3 dB 142:11 (p=3.5e-30) · +0 dB 45:4 (8.2e-10) · +3 dB 26:3 (1.5e-05), pooled 213:18 (p=1.8e-43); `power guard … -> POWERED`; `second arm fewer failures at 3/3 points, first arm fewer failures at 0/3 points -> significant`. SNR@0.1 격차 `n/a (<= -3 vs <= -3)` (두 arm 모두 격자 최저 SNR 에서 이미 0.1 아래; 격자는 늘리지 않는다).
→ **§2 행 (i): "C6 동일예산 우위가 N′ = 1.6e5 에서도 유지 (기하 축 측정, UNGATED)"** — 회수율 대역과 함께:

**회수율 대역 (§1, `recovery_NR16B16e4.txt`, paired bootstrap B=2000 seed 20260926)**: −3 dB **R = 0.809 [90% 0.747, 0.870]** → 대역 **R ≥ 0.70 "기하 효과 대부분 유지"**. (0 dB 0.804 [0.694, 0.903], +3 dB 0.958 [0.750, 1.188], 3 점 합 0.823 [0.771, 0.871].) 나란히: C6 1e4 (`recovery_NR16run2.txt`) 0.838 [0.781, 0.892], C2 1.6e5 헤드라인 (`recovery_B16e4k.txt`) 0.470 [0.427, 0.512]. 대역 문장은 셀·예산 한정이며 arm 주장이 아니다.

| C6 −3 dB (n=2560, 테스트 0..2559) | b\* | V1 | genie | b\*→V1 pooled (3점) | 회수율 −3 dB |
|---|---|---|---|---|---|
| 1e4 (NR16run2, last-EMA; b\* kron 128) | 207 | 52 | 22 | 266:13 | 0.838 |
| **1.6e5 last-EMA (NR16B16e4last; b\* kron 4096)** | 184 | 52 | 22 | 208:17 | 0.815 [0.756, 0.872] |
| 1.6e5 `_best` (NR16B16e4, 측정 판정 태그) | 184 | 53 | 22 | 213:18 | 0.809 [0.747, 0.870] |

### 6.2 보고 전용
- 대조군 `M-ours-bstar → M-ours-bstar-scalar` (`:386-390`): 42:65 (0.033) · 11:45 (5.4e-06) · 9:15 (0.31), pooled 62:125, POWERED, `second arm fewer failures at 0/3 points, first arm fewer failures at 2/3 points -> significant` (b\* 행렬 site 우세, 1e4 와 같은 방향).
- V4 · V4b 도 b\* 를 3/3 점에서 이긴다 (209:32, 195:35; `:374-385`). BLER@16 −3 dB: V1 0.021, V4 0.025, V4b 0.030, b\* 0.072, bstar-scalar 0.081, genie 0.009.
- V0: −3~+9 dB BLER 1.000, +12 0.979, +15 0.911; F3 가드 −3~+9 dB 1.000, +12 0.998, +15 0.993 (`guard_D2_NR16B16e4.txt`). 가드는 V0 에서만 발동(나머지 12 arm 발동 없음).
- best 대 last V1 짝 부호검정 (a = best 실패·last 성공): −3 dB 9:8 (p=1), 0 dB 2:6 (0.29), +3 dB 1:2 (1); 3 점 합 12:16 (p=0.57) — 판정하지 못함. B32e4last 표 B: 208:17 POWERED 3/3.
- 동일예산 GB′ (§5): 비 0.261~0.508, median 0.283, worst excess −0.492 (1e4: 0.314~0.474, median 0.343).
- 학습: §3d 시행 1 DIVERGED (epoch 1064), 시행 2 (클리핑 1.0) 정상 — 모든 1.6e5 C6 수치는 시행 2 가중치.

### 6.3 §3 예측 채점
1. 학습 "발산 없음": **빗나감** (시행 1 발산 → §3d 시행 2); patience 정지·epoch 900~2000 (1704)·best val < 0.19 (0.1785): **적중** (시행 2).
2. b\* = kron, K=4096 이 2048 을 이겨 격자 끝, 재시드 급증: **적중** (K=8192 는 사용자가 멈춤 결정).
3a. 표 B (i) 유지: **적중**. 3b. 3 점 모두 유의: **적중**.
4. V1 실패 40~65 → 53 **적중**; b\* 100~170 → 184 **빗나감** (b\* 개선이 예측보다 작음: 207 → 184); genie 22 **적중**; 회수율 0.65~0.80 → 0.809 **빗나감(근소, 더 높음)**, 대역 "대부분 유지 또는 일부 유지" → "대부분 유지" **적중**; 판정점 −3/0/+3 **적중**.
5. 대조군 b\* 우세 (first arm fewer ≥ 2/3): **적중** (2/3). V0 전 SNR 가드·−3~+3 dB BLER ≥ 0.9: **적중**. V4·V4b 는 V1 과 비슷하거나 나쁨: **적중**.
6. best 대 last 판정 못함: **적중** (12:16).
7. GB′ median 0.35~0.55 → 0.283 **빗나감** (확산 쪽이 예측보다 더 낮음).
8. 빗나갈 경로 (c) K=4096 격자 끝 → K=8192 사용자 결정(멈춤), (d) 발산 → §3d 가 실현. (a)(b)(e) 없음.
