# NEXT_EXPERIMENTS_D3B16e4 — D3 (D2 prior S2c, α_l ~ CN(0, p_l)) 기전 대조, 셀 C2, 동일예산 N′ = 1.6e5 (사전 등록 v2)

- 작성: 2026-09-26 10:21 CDT (= 2026-09-27 00:21 KST) 초안 v1 → 적대적 검토 2건(A 설계·통계 11건, B 실행 가능성·코드·사실 12건; `prereg_reviews_2026-09-26/review_{A,B}_D3_SV.md`) 반영 v2 2026-09-26 10:36 CDT, Claude Code (Fable 5.1). 동결 시각 = 커밋 시각(`DECISIONS.md` 같은 줄). **결과 관측 전**: D3 의 어느 arm 도 테스트 시행에서 BLER 로 평가된 적이 없다(학습·GMM 격자·GB′ 는 끝났다, §4·§5). 사용자 결정: D3 기전 대조 실행(09-25 CDT, DECISIONS [2026-09-26 14:27 KST]), UNGATED·K 4096 멈춤·헤드라인 불변(DECISIONS [2026-09-26 15:03 KST] (2)(3)). 커밋 뒤에는 §1~§3 을 바꾸지 않는다; 바꿔야 하면 사용자 승인 + `DECISIONS.md`.
- 틀: `NEXT_EXPERIMENTS_C6B16e4.md` §0~§6 (UNGATED 측정·회수율 대역·§3d 사다리 처리 선례), `NEXT_EXPERIMENTS_B32e4.md` §1 (동일예산·격자 확장 규칙), `10_SPEC_stageC.md` §3d·§6d·§6l, `01_RULES.md` §4·§5·:76, `08_SPEC_analysis.md` §2 (판정점 3개·power guard·앵커 = baseline), review_next v3 §0 (테스트 0..2559, `_best.pt` 판정, CPU 수신기, "p ≥ 0.05 는 판정하지 못함이지 차이 없음이 아니다"). 재료: `results/review_next/PREREG_FACTS_2026-09-26.md` §0·§B + `_CHECK.md` 정정 3·4·6·7·(결과처럼 읽히는 문장 :352–353, B.3-6)·컴파일러 오기 4.
- 목적: **D2 의 V1 우위(C2 1.6e5, `raw_B16e4k`)가 경로 이득의 결정적 크기(조건부 비-Gaussian 성)에 묶여 있는가.** D3 는 D2 의 기하(L ~ U{3..8}, 연속 AoA/AoD ±π/3, p_l ∝ exp(−l/τ))를 그대로 두고 α_l 만 CN(0, p_l) 로 바꾼 prior 변형이다(`code/d2.py`, PID 5). 이 질문에는 §1 의 **회수율 비짝 차이 규칙**으로 답하고(표 B 문자열만으로 답하지 않는다), 사전 기대가 서로 반대인 둘(§3 E1·E2)을 모두 채점한다. 이 문서는 arm 판정이 아니라 **prior·기전 축 측정**이다(UNGATED).

---

## 0. 출발점 (판정에 쓰지 않는다)

**비교 대상 D2 (C2, N′ = 1.6e5, 태그 `B16e4k`, 헤드라인 legacy-last @1784, b\* kron 1024; `tables_D2_B16e4k.txt:61-76, 367-372`, `recovery_B16e4k.txt`)**

| C2 D2, BLER@16 (실패 수) | −3 dB | 0 dB | +3 dB | SNR@0.1 |
|---|---|---|---|---|
| M-ours-bstar (kron 1024) | 0.243 (623) | 0.072 (184) | 0.022 (57) | −0.81 |
| M-ours-dscore-C-V1 | 0.145 (371) | 0.034 (88) | 0.011 (29) | −2.23 |
| R5-genie (known-channel reference) | 0.034 (87) | 0.010 (26) | 0.005 (12) | ≤ −3 |
| b\* → V1 a:b | 302:50 | 117:21 | 35:7 | pooled 454:78, POWERED, 3/3 |
| 회수율 R = (b\*−V1)/(b\*−genie) [90% CI] | 0.470 [0.427, 0.512] | 0.608 [0.521, 0.684] | 0.622 [0.450, 0.781] | 3점 합 0.509 [0.470, 0.545] |

SNR@0.1 격차 b\*−V1 +1.41 dB [90% paired +1.22, +1.64]. 대조군 b\* → b\*-scalar 61:95 / 30:44 / 9:10 (POWERED, first arm fewer 1/3 → 유의 방향 없음). D2 의 동일예산 GB′ 는 1.6e5 에서 계산된 적이 없고(csv 의 1.6e5 행은 gmm_ntrain 1e4 이고 attempt 3 행뿐 — a1 행 없음 — median 0.464; 헤드라인 a1 의 값이 아니다), 3.2e5 동일예산에서 median 0.513, worst excess −0.121 (`d2_gbprime.csv`).

**D3 에 대해 이미 기록된 것(BLER 아님)**

- **사전 기대 E1** (`10_SPEC_stageC.md:857-860`, 저널 범위 항목): "α_l ~ CN(0,p_l) 로 한 줄만 바꾼 D3 에서 GMM 이 이기거나 비기는 것이 예상되며, 그것이 나와야 '학습 prior 는 혼합모형이 오설정되는 곳에서 이긴다' 는 더 강한 주장이 된다." 정정 R-5.2 (:862): 각도가 연속이므로 앙상블은 연속 혼합이고 유한 K GMM 은 여전히 근사다 — 예측 자체는 유지.
- **사전 기대 E2** (0단계 채널 통계, `testbed2_phase0/selection.md:50-53`; DECISIONS [14:06 KST]): 조건부 Gaussian 인 SV8e 에서도 GMM 의 격차 메움이 0.22 로 D2(0.26) 이하였다 → 이득 조건은 "독립 연속 잠재 각도의 수" 라는 해석. D3 는 D2 와 같은 연속 각도 구조이므로 V1 우위가 남을 수 있다. **D3 자체의 메움 비율은 측정되지 않았다.**
- **testbed 검증** `results/testbed_D3.txt` (2026-09-26 13:37 KST, d2e115e4; PASS 3/3): T3a E‖H‖²/(NrNt) = 1.000086 (n=4e6, 0.31 s.e.), **sd(‖H‖²/NrNt) = 0.5666** (D2 S2 0.16 — 블록 에너지 페이딩이 깊다); T3d 조건부 4차 모멘트 비 ≈ 2 회복(max |측정−2| = 0.0071, L=3..8 모두 CI 가 2 를 포함), T3dm D2 예측 2−Σp_l² 은 모든 CI 아래; T2b erank(Rt) 3.8770/4 → **DFT 파일럿**(S2 와 앙상블 공분산 인수 동일); T2e 유효 bin 5.895/32; C2 T2c NMSE_inf = 0. 따라서 D2·D3 는 2차 통계가 같고(R2-ours-G 의 prior 는 Chat 의 표본 오차만큼만 다르다) 차이는 고차 구조와 페이딩 깊이에서 온다.
- **σ 격자** `results/sigma_grid_D2_S2c.{txt,npz}` (13:32 KST): 헤드라인과 같은 절차(C1+C2, n=64, 시행 0..63, Gaussian 수신기, ν_q 만 기록), σ_t ∈ [3.2831e-02, 8.6484e-01] (D2 동결 격자 대비 −0.7% / +2.3%). **공개**: 이 측정이 D3 테스트 시행 0..63 (C1·C2, 7 SNR) 을 Gaussian 수신기(M-ours-G 궤적)로 한 번 실행했다 — BLER 은 기록하지 않았다. S2c 격자 기준 C2 반복 1 이 격자 위가 되는 SNR 은 < −7.77 dB → −3..15 는 안이다.
- 다른 BLER 실행: sandbox 스모크(시행 6400..6401, 수치 무의미, `D3TP_IMPL_REPORT.md` §6) 뿐. `runner.py smoke` 는 테스트 시행 0,1 을 쓰므로 D3 에 쓰지 않았고 쓰지 않는다.

## 1. 고정되는 것

| 항목 | 값 |
|---|---|
| **셀·예산·시행** | C2 = Nr 8, Nt 4, T 16, Tp 4 (DFT, T2b 결정), K 42, 7 SNR (−3…+15; **결과 뒤 격자를 늘리지 않는다**), n = 2560, 테스트 시행 **0..2559** (chunk 40 → {(40k, 40): k = 0..63}), 16 반복, 수신기 CPU complex128, `arms.LOOP` 그대로. 시드 `trial_rng([20260926, 2, PID 5, 8, 16, 4, snr+100])` → **D2 와 짝이 아니다**(다른 채널·잡음·비트). N′ = 160000: 채널 집합 하나 = `arms.training_set("D2","S2c",8,4,160000)` (스트림 7) 을 GMM 적합과 score 학습(자체 9:1 = 144000/16000, split_hash 5c098ecb6185bcc6) 이 함께 쓴다; GMM 검증 5000 = 스트림 8. Gaussian arm 의 Chat 도 같은 적합(full K=32 파일) |
| **지위** | **UNGATED** (사용자 결정 15:03 KST (2): D1 형제 규칙을 S2c 로 넓히지 않는다) → 이 문서의 결과는 **"prior·기전 축 측정"** 이며 arm 판정이 아니다. 헤드라인(C2 D2 1.6e5 B16e4k) 불변; D3 는 어느 결과에서도 헤드라인이 되지 않는다. 문장 범위(§6f): 셀·prior 한정 없는 주장을 쓰지 않는다 |
| **GMM 격자와 b\*** (BLER 은 선택에 쓰지 않는다) | 등록 선례(B32e4 §1, C6 §1)의 기본 격자는 full {16..512} × κ {0,16,64,256}, kron {16..2048} 이고, D3 큐(`run_d3.sh`)는 kron ≤ 1024 만 병합하고 2048·4096 을 재시작 후보로 미리 적합했다(**선례와 다른 점 공개**; 후처리에서 격자 끝 규칙으로 2048 → 4096 을 병합해 기본 격자 + 1 단계 확장까지 갔다). 선택 = validation ll 최대(`arms.gmm_selection`, `load_fits` 는 병합 파일만). 반복 규칙 = 계열 최대 K 이면 2K; **사용자 결정 (3) 으로 kron 4096 에서 멈춤(K=8192 없음)** → **b\* = kron K=4096, ll_val 0.08879931165293979** (§5). 캐비엇 ①**격자 끝**: 4096 이 2048 병합(−1.836008) 보다 +1.925 nat 높아 아직 오르는 중에 멈췄다. 캐비엇 ②**수렴**(C6 §6.5 와 같은 형태): 이 적합은 재시드 37,827 회, 검증 우도 최고가 마지막 평가 시점(it_best 190 / n_iter 200) 이고 정지 사유는 patience 나 상한이 아니라 학습 우도 증가량 < tol 규칙(`t2_gmm.fit_gmm_em:164`; DECISIONS [17:50 KST]) → 덜 수렴된 GMM 일 수 있고 방향은 V1 유리. 재시작 후보 3 개(kron ≥ 1024)는 존재한다. 수용 검사는 `--bstar kron --kron-K 4096` |
| **체크포인트·평가 가중치** | §3d 시행 1 (동결 레시피, 발산 없음, 사다리 미발동; `stopped_by=patience`; ckpt 의 `aborted` 필드는 None = 미설정, 로그 done 줄은 aborted=False): **측정 판정 태그 `D3B16e4` = `ckpt/d2sx_S2c_N160000_a1_best.pt`** (sha256[:16] **7ebf4e6647d4413f**, epoch 494, role best), **`D3B16e4last` = `ckpt/d2sx_S2c_N160000_a1.pt`** (last-EMA, sha **9fc82e075a5eaf8f**, epoch 514, best_epoch 494 = best.epoch ✓, role last) — 보고 전용. D2 비교 대상은 legacy-last(best 미저장) 이므로 last 도 나란히 보고한다(H0 6:6, B32e4, C6 에서 best 대 last 는 판정하지 못함). rung `D2SXS2c160000`, attempt 1, `sigma_tag = 'S2c'` (체크포인트에 저장; runner 는 ckpt 의 prior 불일치만 거부한다 — `runner.py:1201-1206`; sigma_tag 는 §5 에서 확인) |
| **σ 격자** | `S2c` 자체 격자(§0; 학습 로그 머리말 `MEASURED, 20 points … [3.2831e-02, 8.6484e-01]` 과 npz 일치). 학습·GB′ 모두 `sigma_tag="S2c"`. 동결 D2 격자로 바꾸려면 재학습이 필요하므로 바꾸지 않는다 |
| **실행 (테스트 집합, 14 arm = `raw_B16e4k` 와 같은 구성)** | `code/run_prior_eval.sh S2c D3B16e4 d2sx_S2c_N160000_a1 kron 4096 0.08879931165293979 7ebf4e6647d4413f 9fc82e075a5eaf8f "full:16,32,64,128,256,512 kron:16,32,64,128,256,512,1024,2048,4096"` (9번째 인자 = 수용 검사 격자, **필수**; 커밋 db038a10·33719007·2f6b6497): ① `runner.py run --testbed D2 --prior S2c --cell C2 --n 2560 --chunk 40 --ntrain 160000 --stagec-ckpt ckpt/d2sx_S2c_N160000_a1_best.pt --tag D3B16e4` → `analysis`; ② 같은 명령을 `…_a1.pt --tag D3B16e4last` → `analysis`; 두 태그에 `run_manifest.py`, `guard_report.py`, `recovery_ci.py --cell C2 --snrs <판정점>`; `eval_accept.py`; `frontier_ci.py --recovery` (아래; 2차 판정점은 스크립트가 `results/tables_D2_D3B16e4.txt` 의 앵커 b\* 판정점을 읽어 넣는다). 선행: 링크 `gmm_fits_D2_D3B16e4last → gmm_fits_D2_D3B16e4` (09-26 10:23 CDT 생성). 출력: `results/review_next/D3B16e4_accept.txt`, `recovery_D3B16e4{,last}.txt`, `recovery_diff_D3B16e4.txt`; 로그 `logs/run_prior_eval_D3B16e4.log`, 끝 표시 `PRIOR_EVAL_DONE`. **§5 가 채워져 커밋된 뒤에만 시작한다**(이 문서의 §5 는 동결 커밋에 포함) |
| **수용 검사** (`code/eval_accept.py --prior S2c --bstar kron --tag D3B16e4:best:7ebf4e6647d4413f:C2 --tag D3B16e4last:last:9fc82e075a5eaf8f:C2 --ntrain 160000 --kron-K 4096 --ll-val 0.08879931165293979 --fits-dir results/gmm_fits_D2_D3B16e4 --grid "full:16,32,64,128,256,512 kron:16,32,64,128,256,512,1024,2048,4096" --ref-raw raw_D3B16e4`) | (a) 격자 완전성: full 6 + kron 9 병합 파일, kron ≥ 1024 는 후보 `.k0r{0,1,2}.npz` 3 개; (b) 태그마다 7 점, 점마다 청크 정확히 {(40k,40)}, meta `ntrain=160000`, `bstar=kron`, `kron_K=4096`, `ll_val|kron` = §5 값(|Δ| ≤ 1e-9), 두 태그의 (bstar, kron_K, em_sec) 동일; (c) `stagec_ckpt_id` 의 sha·role 이 위와 일치, `run|iters` = 16; (d) **`D3B16e4last` 의 R5-genie `blk_err`·`ber`·`tauL_gmean`·`alphaD` @1..16 이 `D3B16e4` 와 7 SNR 전 시행 비트 동일**(판정 태그를 `--ref-raw` 로 넘기므로 best 의 자기 비교는 자명; C7/C8 처럼 외부 참조 raw 가 없는 새 스트림이다); (e) GB′ 로그 `GMM b* = kron (kron K=4096)` 가 §5 최종 b\* 와 같고 격자 확정 뒤 계산 — 충족(§5); (f) raw 이름에 `S2c`, analysis 머리말에 D3 경고(`D3_WARNING`), manifest prior 설명 "S2c, alpha_l ~ CN(0,p_l)"; (g) ckpt 의 prior `S2c`·sigma_tag `S2c`. 어긋나면 그 실행 무효 → 원인 기록, 새 태그 재실행. **비-Stage-C arm 전부의 두 태그 간 비트 동일성**은 도구가 검사하지 않으므로(C6 감사 선례) 결과 절에서 b\*·b\*-scalar·gmm32·R0~R4·genie 의 실패 벡터 일치를 손으로 확인해 적는다 |
| **측정 판정 (C2, 태그 `D3B16e4`)** | `08_SPEC` §2 표 B `M-ours-bstar → M-ours-dscore-C-V1`: 판정점 = 앵커 b\* 의 BLER@16 이 [0.005, 0.9] 안에서 \|log10(BLER/0.1)\| 최소 3 SNR (자동; **D2 의 −3/0/+3 과 다를 수 있다** — 페이딩이 깊어 위쪽으로 옮겨질 수 있음, 그대로 쓴다), 점마다 exact 양측 부호검정. POWERED = 판정점 3 이고 불일치 쌍 ≥ 6 인 점 ≥ 2. 라벨은 §2. `significant` 토큰은 판정 기준이 아니다. 대조군 `M-ours-bstar → M-ours-bstar-scalar` 를 같은 형식으로 보고 |
| **기전 판독 규칙 (목적 질문; `_best` 로 계산, last 값도 나란히)** | 회수율 R = (b\*−V1)/(b\*−genie) 를 실패 수로 **−3 dB(1차)** 와 **D3 판정점 3 점 합(2차)** 에서 계산하고 paired bootstrap(시행 인덱스 복원추출 B = 2000, `default_rng(20260926)`, 백분위 5/95 → 90% CI; `recovery_ci.py`) 을 붙인다. **D2 와의 비짝 차이** Δ = R_D3 − R_D2: `code/frontier_ci.py --recovery "raw_D3B16e4:C2:-3" "raw_B16e4k:C2:-3"` (두 raw 의 시행을 독립으로 복원추출, 각 raw 안에서는 세 arm 을 묶음, B = 2000, `default_rng(20260926)`, 백분위 5/95; 2차는 `-3 0 3` 의 D2 3 점 합 대 D3 판정점 3 점 합). 세 갈래: **90% CI < 0 → "D3 의 회수율이 D2 보다 낮다"; CI > 0 → "높다"; 0 포함 → "판정하지 못함"**. **포화 가드(1차)**: −3 dB 에서 앵커 b\* 의 BLER@16 이 [0.005, 0.9] 밖이거나 b\* 의 실패 수 ≤ genie 의 실패 수이면 1차 ΔR 은 "판정하지 못함(범위 밖)" 으로 고정하고 2차만 보고한다. **정의 불가 규칙**: 분모 b\*−genie ≤ 0 인 복제는 제외하고 개수를 적되, 그 비율이 5% 를 넘거나 점추정 자체가 정의되지 않으면 "판정하지 못함(정의 불가)". **ΔR 라벨은 1차(−3 dB)에서만 붙이고 2차(판정점 합 = 운영점을 맞춘 비교)는 보고만 한다 — 둘이 엇갈려도 조정하지 않는다.** 대안 b\*(다른 K·계열)를 BLER 로 평가하지 않는다. D2 값 −3 dB 0.470 [0.427, 0.512], 3 점 합 0.509 [0.470, 0.545] 를 옆에 찍는다. 동등성 여유는 등록하지 않으므로 "같다/비긴다" 는 어느 결과에서도 쓰지 않는다 |
| **판독표** (표 B 라벨 × Δ 라벨; 교란 요인을 항상 함께 적는다) | (i) & Δ 판정 못함 → "V1 우위가 결정적 \|α_l\| 없이도 남았고 회수율 차이는 판정하지 못함; '오설정된 곳에서 이긴다' 는 이 결과만으로는 서지 않는다" [채점: E2 적중·E1 빗나감]. (i) & Δ < 0 → "우위는 남되 회수율은 낮다: 조건부 비-Gaussian 성이 우위의 **일부**에 기여했을 수 있다(단정 아님)" [E2 적중·E1 빗나감]. (i) & Δ > 0 → "우위가 남고 회수율은 더 높다" [E2 적중·E1 빗나감]. (ii) → "D3 에서 GMM 우세; D2 우위의 범위를 정하는 대조" [E1 적중·E2 빗나감]. (iii)/(iv) → "판정하지 못함" [E1·E2 어느 쪽도 채점하지 않음 — 동등성 여유가 없으므로 (iii) 은 E1 의 '비김' 적중이 아니다]. **교란 요인(모든 칸에 적는다)**: D3 는 블록 에너지 페이딩이 깊어(sd 0.57 vs 0.16) 모든 arm 의 BLER 수준과 판정점이 옮겨질 수 있고, D2·D3 는 짝이 아니며, b\* 는 격자 끝·수렴 캐비엇을 달고 있다 → 회수율 차이의 원인을 조건부 비-Gaussian 성 하나로 돌리지 않는다 |
| 보고 전용 | D2 대 D3 표(−3 dB 와 판정점의 실패 수·BLER: b\*, V1, genie; pooled a:b; SNR@0.1 과 격차, 격자 밖이면 "n/a" 그대로); V0·V4·V4b, F3 가드 발동률; best 대 last V1 짝 부호검정(D3 안); GB′ (§5, last 파일 기준) 를 D2 3.2e5 동일예산 0.513 과 나란히(1.6e5 D2 동일예산 GB′ 는 없다 — 계산하려면 `run_d2_sx.py --ntrain 160000 --tag B16e4k` 가 git 추적 파일 `d2_gbprime_N160000_a1.npz` 를 덮어쓰므로 하지 않는다, CHECK 8); 격자 표(§5). 일괄 kron 경로(`fit_gpu_batched.py`) 의 S2c 재검사는 하지 않았다(대수 항등식; 검증은 S2 Nr 8/16 K ≤ 512, 재시드 포함) — 공개. **다중성**: 이 문서의 라벨 검정은 표 B 하나와 ΔR 1차 하나뿐이며, 세 등록(D3·SV8e·38.901 UMi28) 사이의 보정은 하지 않는다(서로 다른 가설); 기전에 관한 문장은 `NEXT_EXPERIMENTS_38901.md` 의 공동 판독표(연접 조건)로만 쓴다 |
| 비용·일정 | GPU 없음(학습·격자·GB′ 완료). CPU: 태그당 ≈ 35~50 분 [추정: C2 B32e4 태그 34.4 분 @K=4096; D3 의 −3 dB BLER 이 높으면 Module H 반복이 늘 수 있음] × 2 태그, 192 워커. tb2 큐(MIX3·UMi28 학습·적합)와 CPU 를 나눠 쓴다 |

## 2. 라벨 (여기서 고정; "측정" 이지 arm 판정이 아니다. UNDECIDED / 비유의는 "판정하지 못함" 이며 어느 쪽의 증거도 아니다)

| 표 B `b\* → V1` (C2, D3B16e4) | 기록 |
|---|---|
| (i) POWERED 이고 second arm fewer ≥ 2/3 | "D3 (조건부 Gaussian 경로 이득) 에서도 V1 이 b\* 보다 적게 실패 (prior·기전 축 측정, UNGATED)" — **§1 의 Δ 라벨(회수율 비짝 차이)과 반드시 함께** |
| (ii) POWERED 이고 first arm fewer ≥ 2/3 | "D3 에서 GMM b\* 가 더 적게 실패 (E1 적중)" — Δ 라벨과 함께 |
| (iii) POWERED 이고 어느 쪽도 ≥ 2/3 아님 | "판정하지 못함 (유의 방향 없음)" — Δ 는 보고만 |
| (iv) UNDECIDED (판정점 < 3 이거나 불일치 쌍 ≥ 6 인 판정점이 2 개 미만) | "판정하지 못함 (검정력 미달)" — SNR 격자를 결과 뒤 늘리지 않는다 |

- (ii)(iii)(iv) 어디에도 "비긴다/같다" 문구를 만들지 않는다(동등성 여유 미등록). (i) 만으로 "D2 우위의 기전은 연속 잠재 기하" 라고 쓰지 않는다 — 그 문장은 §1 판독표의 Δ 와 교란 요인을 붙여서만 쓴다. 어느 결과도 헤드라인·C2 D2 판정·10_SPEC 의 E1 기록을 바꾸지 않는다(빗나가면 채점만 한다).

## 3. 미리 적는 예측 (빗나가면 그대로 쓴다; D2 결과와 D3 채널 통계를 본 뒤의 약한 예측)

경쟁하는 사전 기대 둘을 모두 채점한다.
- **E1** (기존 등록 기대, 10_SPEC:857-860): **적중 = 표 B (ii) 만** — (iii) 은 동등성 여유를 등록하지 않았으므로 '비김' 적중으로 세지 않는다.
- **E2** (0단계 기전 해석): **적중 = 표 B (i) 만**.
- (i)/(ii) 는 배타이므로 둘 다 적중은 불가능하고, (iii)/(iv) 에서는 어느 쪽도 채점하지 않는다. 아래 수치 예측(4·5)은 범위 안/밖 이분으로 채점한다; 확신 등급은 채점과 무관하다.

1. 학습: 완료(514 epoch, patience, best val 3.534156e-01 @494, 발산 없음; D2 1.6e5 의 3.5196e-01 과 거의 같음) — 예측 아님, 기록.
2. GMM: 완료 — b\* kron 4096 격자 끝(§5). GB′ median 0.559 (D2 3.2e5 동일예산 0.513 보다 큼: D3 에서 확산 prior 가 GMM 에 상대적으로 덜 앞선다 — 판정 무관 보고값).
3. **표 B: E2 쪽(i) 에 무게(확신 낮음~중간)** — 근거는 GB′ 가 1 보다 뚜렷이 작다는 것(0.49~0.88)과 SV8e 의 0단계 메움이 낮았다는 것. E1 이 맞으면 그대로 쓴다.
4. −3 dB 실패 수(2560 중): **genie 150~450** (D2 87 보다 높음; 페이딩 깊이), **b\* 700~1300**, **V1 450~1000**. 판정점은 **−3/0/+3 또는 0/+3/+6** — 위쪽으로 한 칸 옮겨질 수 있다.
5. 회수율 −3 dB **0.30~0.55**; Δ = R_D3 − R_D2 의 90% CI: **예측 = 0 을 포함("판정하지 못함")**, 차선 = 음수; 양수는 예상하지 않는다(단일 예측으로 채점).
6. 대조군 b\*→b\*-scalar: D2 와 같이 유의 방향 없음 또는 b\* 우세. V0: 낮은 SNR 에서 가드 발동, −3 dB BLER ≥ 0.9. V4·V4b 는 V1 과 비슷하거나 나쁨.
7. best 대 last V1 (D3 안): 판정하지 못함(pooled p > 0.05).
8. 빗나갈 경로: (a) (ii) → E1 적중으로 기록, D2 우위의 범위 문장은 사용자; (b) (iv) 검정력 미달(예: b\* 의 BLER 이 +15 dB 에서도 > 0.9 인 극단) → 그대로 기록, 격자 확장 없음; (c) Δ CI > 0 → E2 와 맞음으로 기록하되 교란 요인 병기; (d) 수용 검사 실패 → 원인 기록, 새 태그.

## 4. 선행 작업과 실행 현황 (갱신한다)

| 항목 | 상태 · 담당 |
|---|---|
| D3 prior·인프라 (`d2.py` S2c, PID 5, testbed_D3, σ 격자 S2c, run_d3.sh) | 완료 301c6285 (DECISIONS [14:27 KST]); 기존 경로 비트 동일(`selftest_d3tp.py` IDENTICAL) |
| GPU 큐 `run_d3.sh` (학습 + 격자 22 작업, GPU 0–5) | 09-26 00:27 CDT 시작 → 03:30 CDT `D3_QUEUE_DONE` (`logs/d3.log`); 학습 GPU 5, 00:27~03:30 CDT, 10,939 s |
| kron 1024 병합 → 격자 끝 → 2048 병합 → 격자 끝 → 4096 병합 → 멈춤(결정 (3)) | 완료 (03:30 CDT 후처리 MANUAL 표시 → 03:50 CDT 기록 시점까지 병합·선택 완료, `logs/d3_post.log`, DECISIONS [17:50 KST]) |
| GB′ (격자 확정 뒤, last 파일) | 완료 04:50 CDT 기록 (첫 시도는 GPU 0 점유로 rc=1, 재시도 없이 다른 GPU 실행 rc=0; `d3_post.log`, DECISIONS [18:50 KST]) |
| 선행 코드: `run_prior_eval.sh` (범용 평가 스크립트; 판정점 자동 읽기), `frontier_ci.py --recovery` (비짝 회수율 차이 CI), `eval_accept.py` 인자(`--prior`, `--bstar`, `--kron-K` 선택, `--ref-arms`), fits 링크 `gmm_fits_D2_D3B16e4last` | **완료**: db038a10 (10:24 CDT), 33719007 (10:26 CDT), 2f6b6497 (10:33 CDT) (Fable, 09-26); 링크 09-26 10:23 CDT |
| 적대적 검토 2건(`prereg_reviews_2026-09-26/review_{A,B}_D3_SV.md`) → v2 → 동결 커밋 → 실행 ①② → §6 | v2 반영 완료(이 커밋 = 동결); 실행은 동결 커밋 직후 tmux 에서 |

## 5. 평가 전 고정 기록 (실행 ①② 전에 채우고 커밋한다; 갱신 시각을 적는다)

| 항목 | 값 |
|---|---|
| 격자: K 별(계열별) ll_val · n_iter · it_best · 재시드 · 구현 경로, 병합 ll_val (`results/gmm_fits_D2_D3B16e4/fit_S2c_Nr8_*_n160000*.npz`, 2026-09-26 10:20 CDT 읽음) | **kron** (κ = 0, 재시작 3; K ≤ 512 는 한 파일에 3 재시작 → 선택 재시작 표기, K ≥ 1024 는 후보 3 개 병합; **전부 일괄 경로** `kron_batched=1`): 16 −35.164 (r1, 251/210, 재시드 0) / 32 −28.538 (r0, 281/240, 0) / 64 −22.481 (r0, 312/310, 0) / 128 −17.083 (r1, 343/340, 0) / 256 −12.336 (r2, 281/240, 0) / 512 −8.041 (r2, 420/380, 0) / **1024 −4.547236710846172** (r0, 296/290, 0; r1 −4.749 378/370, r2 −4.749 151/110) / **2048 −1.8360078008201854** (r0, 273/270, 재시드 492; r1 −1.967 251/210 rs 297, r2 −1.908 261/220 rs 137) / **4096 0.08879931165293979** (r2, **200/190**, 재시드 **37,827**; r0 −0.348 131/130 rs 24,443, r1 −0.229 161/120 rs 30,609). **full** (κ ∈ {0,16,64,256} × 재시작 3, 전부 κ = 0 선택, **정확 경로**): 16 −35.289 (r0, 222/190) / 32 −28.005 (r2, **500/490, 상한 정지**) / 64 −21.412 (r1, 491/450) / 128 −16.168 (r2, **500/490, 상한 정지**) / 256 −12.094 (r0, **500/490, 상한 정지**) / 512 −10.859 (r2, 471/430). 상한 500 정지 = full 32·128·256 (b\* 아님). kron 4096 후보의 정지 사유(npz 에 필드가 없어 n_iter/it_best 에서 추론): r1 (161/120, 41 ≥ patience 40) 은 patience 정지, r0 (131/130)·r2 (200/190; = b\*) 는 학습 우도 tol 규칙 정지(재시드 다수). 재시작 후보 누락·재실행 없음 |
| 확장 결정(K=2048 / 4096 / 8192)과 시각 | [03:30 CDT] 후처리: b\* = kron 1024 = 계열 최대 → MANUAL(`d3.log`). [03:50 CDT 기록] 결정 (3) 과 선례에 따라 2048 병합(−1.836, 또 격자 끝) → 4096 병합(+0.0888) → **사용자 결정(15:03 KST (3))대로 4096 에서 멈춤**, K=8192 미적합 |
| 최종 b\*: 계열·K·ll_val(정확한 float), 내부 여부 / 캐비엇 | **b\* = kron K=4096, ll_val 0.08879931165293979** (재시작 2, n_iter 200, it_best 190, 재시드 37,827, ll_test − ll_test(Gaussian) 65.160 nat, train−val gap 5.403; `d3_post.log`). **격자 끝**(2048 대비 +1.925 nat, 오르는 중) + **수렴 캐비엇**(§1). full 최고 K=512 −10.859 는 b\* 보다 10.95 nat 낮다. 수용 검사 대조값 `ll_val|kron` = 0.08879931165293979, `kron_K` = 4096 |
| 체크포인트: last / best 의 sha256[:16]·epoch·best_epoch·stopped_by·aborted; best.epoch == last.best_epoch | [10:20 CDT 재계산] `ckpt/d2sx_S2c_N160000_a1.pt` sha **9fc82e075a5eaf8f**, epoch 514, best_epoch 494, stopped_by patience, aborted 필드 None(미설정; 로그 done 줄 aborted=False), role last, grad_clip 0.0 (§3d 시행 1); `ckpt/d2sx_S2c_N160000_a1_best.pt` sha **7ebf4e6647d4413f**, epoch 494 = last.best_epoch ✓, role best, best val 0.3534156382083893. 학습 09-26 00:28~03:30 CDT (로그 머리말 14:28:00 KST), 10,939 s, 평균 21.28 s/epoch, hp = 동결 레시피(dit vp/angle, lr 2.238046e-3, ema 0.999, batch 256, emb 256, w64 d6 h8 p1, 479,426 params), n_train 144000 / n_val 16000, split_hash 5c098ecb6185bcc6, E‖H‖²/(NrNt) 1.001014 (`logs/train_d2sx_S2c_N160000_a1.log`) |
| §3d 사다리 적용 여부 | 미발동(시행 1 patience 정지, 발산 없음). 대기 실행 없음 |
| σ 격자 태그·값 확인 | `sigma_tag='S2c'`, `results/sigma_grid_D2_S2c.txt` (2026-09-26 13:32:02 KST, git d2e115e4, C1+C2 n=64, 14 점 × 16 반복 = 14,336 표본): 20 점 σ_t ∈ [3.2831e-02, 8.6484e-01] = 학습 로그 머리말 `MEASURED, 20 points, log-uniform draw over [3.2831e-02, 8.6484e-01]` ✓ |
| GB′ (last 파일 기준; b\* 계열·K·ll_val, 비 min/max/median, worst excess; 격자 확정 뒤 계산) | [npz/csv mtime 04:30 CDT; DECISIONS 기록 04:50 CDT] `[d2sx] GMM b* = kron (kron K=4096) @N=160000 | diff/gmm min 0.4866 max 0.8803 median 0.5589 | equal_budget=True` (`d3_post.log`; `results/d2_gbprime_S2c.csv`: 0.486646 / 0.880254 / 0.558939, worst excess −0.119746, n_eval 4096, σ 격자 S2c 20 점). 격자 확정(kron 4096 병합 파일 mtime 03:49 CDT) 뒤 계산 → 수용 (e) 충족. 참고: D2 3.2e5 동일예산 0.452853 / 0.878976 / 0.512995, worst excess −0.121024 |
| 선행 코드 커밋 해시, fits 링크 생성 시각, 수용 검사·CI 스크립트 | db038a10 (`frontier_ci.py`, `eval_accept.py` 인자, `run_prior_eval.sh`, C7/C8 격자), 33719007 (판정점 자동 읽기), 2f6b6497 (`eval_accept --ref-arms all`); 링크 `gmm_fits_D2_D3B16e4last → gmm_fits_D2_D3B16e4` 09-26 10:23 CDT; 동결 = 이 문서의 v2 커밋(DECISIONS 같은 줄) |

## 6. 결과 (이 절은 추가만 한다)

(실행 후 기록: 실행 시각·태그·수용 검사 판정, §6.1 측정 판정, §6.2 기전 판독(Δ), §6.3 보고 전용, §6.4 §3 예측 채점, §6.5 기록 감사.)
