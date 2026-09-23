# NEXT_EXPERIMENTS — P1 진단과 P2 후보 ablation의 사전 등록 (v3)

- 작성: 2026-09-23 KST, Claude Code (Fable 5.1). v1 은 3관점 적대적 검토(33건 지적, 26건 실제 결함; `prereg_review_raw.json`)로 v2, v2 는 2차 검토(20건 지적, 14건 실제 결함; `prereg_review2_raw.json`)로 v3 가 됐다. **결과 관측 전.** 커밋 뒤에는 §2·§3 의 판정 규칙·임계값·예측을 바꾸지 않는다. 바꿔야 하면 사용자 승인 + `DECISIONS.md` 항목.
- 근거: `REVIEW_AUDIT.md` (P1-1 ~ P1-4, P2-A/B/C, denoiser/M1~M4), `CHANGELOG_REVIEW.md`(P0 수정), 핸드오프 §7~§9·§12. 기존 규칙(`01_RULES.md` §5·§9, `04_SPEC_diffusion.md` §2·§5·§6, `08_SPEC_analysis.md` §2, `10_SPEC_stageC.md` §3b·§3c·§3d)은 그대로 적용된다.
- 목적: "학습 prior 의 정보를 수신기에 더 정확히 전달하면 BLER·안정성·계산이 좋아지는가" 를 **prior 자체 / uncertainty adapter / 반복 루프** 로 분리해 답한다. GMM 을 약화시키거나 잘 나오는 지점을 고르는 실험은 없다.

---

## 0. 고정되는 것 (전 실험 공통)

| 항목 | 값 | 출처 |
|---|---|---|
| 헤드라인 구성 | D2 / S2 / 셀 C2 (8×4, T=16, Tp=4), N_train = 160000, GMM b\* = kron K=1024, 체크포인트 `d2sx_N160000_a1.pt` (**last-EMA@1784, best@1764 미저장 = `BEST_WEIGHTS_UNAVAILABLE`**) | `tables_D2_B16e4k.txt`, `run_manifest_B16e4k.json` |
| **테스트 집합** | 각 (셀, SNR) 점의 시행 스트림 `common.trial_rng` 의 **skip 0 ~ 2559** (n=2560). 모든 기존 표·진단(`sigma.py` 64, `diag_*` ≤128, `stratify_L` 2560, `bench_*` 25)이 이 범위 안에 있다 | `raw_*` 파일명 |
| **개발 집합 (신규)** | 같은 스트림의 **skip 2560 ~ 3199** (n=640, 청크 40 × 16). 어떤 raw 디렉터리에도 없음(최대 skip 2520). **생성 수단**: `runner.py run --skip0 2560 --n 640 --tag <tag>` (opt-in, 기본 0 = 기존 동작 불변; `runner.chunk_plan`, `C.DEV_SKIP0`; selftest_ckpt `[chunk]`). **수용 검사**: 점마다 raw 파일 집합이 정확히 {(2560+40k, 40) : k=0..15} (16 청크, 합 640) 이 아니면 그 실행은 무효. `analysis.load_raw` 의 구멍 검사는 DEV_SKIP0 에서 시작하고, `run_manifest.py` 는 `trial_stream.split` 에 DEVELOPMENT/TEST 를 적는다 | 이 문서 |
| 판정에 쓰는 개발 점 | **C2 −3 dB 만** (V1 실패 ≈ 0.145 × 640 ≈ 93 블록). C2 +6 dB (V1 실패 ≈ 4/640)·C5 −3 dB·C1 −3 dB 는 **보고 전용** | 검토 지적: +6 dB 는 n=640 에서 검정력 0 |
| paired 검정 (house test) | 같은 시행의 실패 지표 쌍 → 불일치 쌍의 **양측 부호검정(exact)**, p < 0.05. 불일치 쌍 < 6 이면 UNDECIDED. **판정은 p 로만** 한다. MDD = 관측된 불일치 수 n_d 에서 p < 0.05 가 되는 최소 순 블록 수(n_d 19→11, 26→12, 32~38→14, 45~51→15; n=640 에서 BLER 0.017~0.023)이고, p < 0.05 에 이미 포함되므로 **보고용**이다. p ≥ 0.05 는 "이 설계로 차이를 판정하지 못함" 으로 쓴다("차이 없음" 이 아님) | `08_SPEC_analysis.md` §2, `Demo/exp_0921_analysis.py` sign_p, MIN_DISC=6 |
| 확증 실행 (테스트 집합) | **§3.1 2단계 통과 시 한 번**. 1차 비교·판정점·통과 기준을 §3.1 4단계에 적는다(10_SPEC §3c). 테스트 BLER 을 보고 무엇도 고르지 않는다 | `01_RULES` §5, `10_SPEC` §3c |
| held-out AWGN 질의 표본 | `C.train_rng(testbed, prior, Nr, 10)` 스트림 (GB′ 와 동일; 학습 스트림 7 과 분리). **n_eval = 2048** (§2.2, §2.4), **n = 512** (§2.3: 위상 8개 × Jacobian 이라 비용 8배) | `score.gb_prime` |
| σ 격자와 구간 | 동결 D2 격자 20점, **0-based k=0..19**, σ_k ∈ [0.0331, 0.8452]. **하 = k 0~6 (σ ≤ 0.092)**, **중 = k 7~14 (0.109 ≤ σ ≤ 0.360)**, **상 = k 15~19 (σ ≥ 0.40)**. 수신기 질의 범위(C2 −3 dB): 반복 1 σ≈0.50(상), 반복 2 σ≈0.36(중), 반복 16 σ≈0.27(중); +6 dB 반복 16 σ≈0.10(하). **세 구간 모두 판정 범위** | `sigma_grid_D2.txt` |
| 수신기 | CPU complex128, 16 반복, 전 arm 동일 파일럿·시드·채널·잡음(paired). GPU 는 학습·Jacobian·GB′ 류 계산에만(§9.3: 수신기 경로에는 쓰지 않음) | `01_RULES` §9 |
| 학습 규약 | 동결 레시피(dit vp/angle w64 d6 h8 p1 emb256 lr 2.238046e-3 ema 0.999 batch 256), patience 20 / min 200 / max 3000, §3d 발산 규칙, split 9:1 SEED_SPLIT. **한 학습 = 한 프로세스.** 학습 seed 는 rung 라벨에 의존하므로(SEED_TRAIN + _rung_ix(rung)·17 + attempt) 통제·ablation 은 기존과 **같은 rung 라벨**(D2: `D2SX160000`/`D2SX10000`, D1 형제: 기존 `sx_N160000_D1` 의 라벨)을 쓴다 — 학습 호출은 `train_ctrl.py`(§2.5) 와 같은 방식의 wrapper 로 고정한다. **초기 가중치**: `make_model` 은 전역 RNG 에서 초기값을 뽑고, 이 torch 빌드는 프로세스마다 initial_seed 가 달라진다(N1 정정). 따라서 현재 코드로는 attempt·aug/ctrl 이 **기록되지 않은 초기값까지 다르다**. 선행 작업(§6): `score.train(init_seed=...)` opt-in — make_model 직전에 `SEED_INIT + _rung_ix·17 + attempt` 로 초기값을 고정하고 init_seed·초기 state_dict 해시·phase_aug 플래그를 체크포인트에 저장(사용자 결정 대기). 이 선행 작업이 없으면 A1 의 aug/ctrl 비교는 "초기값 차이 포함" 으로 표기한다 | `04_SPEC` §2, `cd241b7e` |
| **평가 가중치** | 새로 학습한 모든 arm 은 **`_best.pt`** 로 평가하고, `ckpt_identity(best)['epoch'] == ckpt_identity(last)['best_epoch']` 를 확인해 manifest 에 적는다. 기존 V1 만 last-EMA(위) | `CHANGELOG_REVIEW.md` §5 |
| 학습 데이터 예산 | GMM 과 동일 집합·동일 N_train. diffusion 에 데이터·재시작·epoch 예산을 더 주지 않는다. 위상 augmentation 은 표본 수를 늘리지 않는다(같은 표본에 곱하는 위상뿐) — 그래도 "같은 학습 데이터" 이지 "같은 정보" 는 아님을 표에 명시한다 | `01_RULES` §5 |
| 계산 예산 (추론) | 변형 arm 의 Module H 실경로 비용을 `bench_moduleH_ep.py` 로 잰다. 비용이 늘어나는 변형은 표에 비용 열을 함께 싣는다 | 핸드오프 §1.2 |
| 결과 보존 | 새 태그·새 출력 경로(`ckpt_review_next/`, `raw_review_next_*`, `results/review_next/`)만 사용. 기존 raw·ckpt·표·게이트 파일은 읽기만 | 핸드오프 §1.1 |
| 새 진단의 이름 | GA~GD 를 완화하지 않는다. 새 진단은 **P1-x** 이고 게이트가 아니다 | 핸드오프 §1.2 |
| 재학습의 지위 | §2.5 통제 재학습은 사전 등록 실행의 "재실행" 이 아니라 **새 태그의 별도 학습**이다. 기존 `d2sx_N160000_a1.pt` 와 그 결과는 그대로 남는다. 시작 시 `DECISIONS.md` 에 한 줄 기록 | `01_RULES` §5 |

---

## 1. 질문과 가설 (반증 조건까지)

| id | 가설 | 이 결과가 나오면 **기각** (반증 조건) |
|---|---|---|
| H0 | best-epoch 가중치와 last-EMA 가중치의 BLER 차이는 무시할 수 있다 (val 상대차 6.3e-5) | **쌍 = 재학습 best vs 재학습 last(같은 run, §2.5)**, 개발 집합 C2 −3 dB: 양측 부호검정 p < 0.05 → 기각(MDD 는 함께 보고). 기존 last-EMA vs 재학습 last 는 GPU 비결정성(+초기값) 참조값으로 보고만 |
| H1 (cavity) | 수신기가 denoiser 에 주는 등방 cavity CN(q, ν_q I) 는 분산이 틀렸거나(e_t) 비등방이다(a_t) | **V1, C2 −3 dB, 반복 8, 블록 중앙값**: e_8 ∈ [0.7, 1.4] **그리고** a_8 ≤ 3 → 기각. (a_t 는 §2.1 정의 — 고유값 순위로 고정한 방향이라 등방 귀무 분포가 F(16,16), 중앙값 1·97.5% ≈ 2.8 이므로 3 은 실제 판별 폭이다.) (실패 블록과의 연관은 e_t 가 채널 오차를 포함해 동어반복이므로 **보고 전용**: 반복 4 의 NMSE 를 공변량으로 넣은 로지스틱 회귀에서 e_4 의 추가 설명력) |
| H2 (calibration) | V1 의 공분산 ν·J_psd 는 실제 오차를 과소/과대 설명한다 | **floor 되지 않은 고유부분공간에서** ρ_tr ∈ [0.8, 1.25] 이고 90% 명목 coverage ∈ [0.85, 0.95] 가 **20 격자점 합산 14점 이상**에서 성립 → 기각. 구간별 개수와 floor 된 고유질량은 따로 보고 |
| H3 (phase) | DiT denoiser 의 전역 위상 등변 오차는 denoising 오차의 무시 못 할 부분이고, 위상 augmentation 이 이를 줄이며 BLER 도 개선한다 | (a) ε_φ / denoising 오차 중앙값이 **세 구간 모두** < 0.10 → augmentation 자체를 하지 않는다. (b) augmentation 이 ε_φ 는 줄였지만 개발 집합 paired 검정에서 개선 없음 → "위상 오차는 인과 경로가 아니다" |
| H4 (pseudo-cov) | 이미 계산한 실 Jacobian 의 pseudo-covariance K 에 검출에 유효한 정보가 있다 | 실제 질의(V1, C2 −3 dB, **반복 4**)에서 블록 r_P 의 중앙값 < 0.2 **또는** 블록 r_P(반복 4)가 같은 반복의 NMSE 와 ν_q 를 통제한 로지스틱 회귀에서 실패를 추가로 설명하지 못함(우도비 p ≥ 0.05) → P2-A 를 하지 않는다 |
| H5 (mean-preserving clip) | 'eta' clip 이 belief 평균을 이동시키는 것이 꼬리 실패의 일부다 | 개발 집합 C2 −3 dB 에서 **V1-mean vs V1-eta** 양측 부호검정 p ≥ 0.05 또는 V1-mean 의 실패가 더 많음 → 기각. (H5 는 테스트 raw 의 clip 통계에서 나온 가설이다 — §3.2 는 개발 집합 전용·보고 전용이며 이 문서는 A2 의 테스트 확증을 계획하지 않는다) |

어느 쪽이든 보고한다. §7 에 예측을 적는다.

---

## 2. 설계

### 2.1 P1-1 — 실제 denoiser 입력(cavity) 분포. 개발 집합, CPU 수신기, `--skip0 2560`

- 점: **C2 −3 dB(판정)**, C2 +6 dB, C5 −3 dB (Tp=3 < Nt=4), **C1 −3 dB** (학습 arm 이 전부 발산하는 셀; 첫 질의 ν≈2.0 이 격자 상단 밖 — 보고 전용). 각 n=640.
- arm (같은 시행에서 paired): **V1(기존)**, **V0**, **M-ours-bstar-scalar** (mode='scalar' 의 GMM — 스칼라 cavity (q, ν_q) 를 실제로 형성하는 GMM 대조군), **M-ours-bstar** (colored ep_site 경로: (q, ν_q, α_H) 가 **존재하지 않으므로** G 기반 양만 저장).
- 저장(블록 × 반복): score/scalar arm — ν_q, q 의 격자 이탈 여부(σ(ν_q) 가 동결 D2 격자 [s_lo, s_hi] 밖; GMM 대조군도 같은 정의로 외부 계산), α_H, h_H, h_post, **V0/V1 만**: clip 여부와 shift = 각 `_matrix_site` 호출 전후 `RouteAClip.shift` 증분의 제곱근(호출당 상대 노름 |μ_clip − h_H|/|h_H|; bstar-scalar 는 hsite='scalar' 라 clip 이 없다), ‖h_post − h_true‖²/‖h_true‖², **e_t = ‖q − h_true‖² / (N ν_q)**, **a_t** = 블록마다 실제 오차 벡터 (q − h_true) 를 **정규화 cavity SigL = (I/ν_E + G)^{-1} 의 고유벡터**에 사영하고, **SigL 고유값 상위 8개 방향**의 |v_i^H(q − h_true)|² 평균 ÷ **하위 8개 방향**의 평균(방향은 고유값 순위로 고정, 사영값 크기로 정렬하지 않는다; 등방 귀무 = F(16,16)) — 반복 ≥ 2; 반복 1 의 G 는 C5 에서 구조적으로 rank Tp·Nr — 사실이지 측정이 아님, 서술만). bstar arm — G 의 고유값, G 고유기저에 사영한 h_post 오차, ep_site clip 카운터, tilted mean m, h_post. 공통 — 실패 플래그, 발산 플래그, 실행시간. h_true 는 진단 전용(수신기에 주지 않는다).
- 대조: GMM b\* 의 정확 posterior 를 **score arm 의 (q, ν_q) 에 반사실적으로** 적용한 (m, Cov) (`GMMPriorB.denoise_full`) — "같은 입력을 받았을 때 정확 GMM 은 무엇을 내는가".
- 지표: 반복별(1, 2, 4, 8, 16)·점별·arm 별 e_t, a_t 중앙값·IQR; 격자 이탈 비율; H1 판정값 = V1·C2 −3 dB·반복 8 중앙값.
- 새 코드: `conf/code/diag_p1_cavity.py` (RouteA 인스턴스의 `_sites`·`prior.denoise`·`_matrix_site`·`prior.ep_site` 를 감싸는 훅; `Demo/` 무수정). 결과 `results/review_next/p1_cavity_<point>.npz`.

### 2.2 P1-2 — 공분산 calibration. held-out AWGN 질의 (GPU) + §2.1 의 실제 질의

- held-out: q = h + CN(0, ν I), n_eval=2048, 격자 20점. V1: (m, Σ = ν·J_psd); V0: (m, ν·Herm(J)) — **V0 는 Herm(J) 가 대부분 indefinite 이므로 ρ_tr 만** 보고하고 coverage 는 PSD 인 부분집합에서 그 비율과 함께; GMM b\* 정확 posterior (m, Cov) 대조.
- 지표(격자점별): ρ_tr = E‖h−m‖² / E tr Σ; **floor 되지 않은 고유부분공간**(고유값 > 10·floor)에서의 whitened Mahalanobis d²/dim 중앙값과 명목 50/90% coverage; floor 된 고유질량 비율·평균 개수; 고유방향 calibration 기울기(Σ 고유값 5분위 × 실제 사영 분산); PSD floor 적중 비율.
- 실제 질의: §2.1 에서 저장한 (q, ν_q, h_true) 에 같은 지표(V1, V0, 반사실 GMM). site 전후 평균 이동은 호출당 상대 노름 |μ_clip − h_H|/|h_H| (`RouteAClip.shift` 는 clip 된 호출의 제곱 상대 노름 **합**이므로 호출 전후 증분의 제곱근으로 읽는다) 와 ‖h_post − h_H‖/‖h_H‖(감사 M3 의 "어느 평균이 보존되는가" 서술량)를 **따로** 기록한다.
- 새 코드: `conf/code/diag_p1_calib.py` (GPU, `torch.func.jacrev` 배치 float64). 결과 `results/review_next/p1_calib_*.npz/txt`.

### 2.3 P1-3 — 전역 위상 등변성. held-out AWGN 질의 (GPU), GMM 대조

- 같은 q 에 φ = 2πk/8 (k=0..7) 을 곱해 denoise 후 되돌린 상대 오차 ε_φ = ‖e^{−jφ} D(e^{jφ}q) − D(q)‖ / ‖D(q)‖. 격자 20점 × n=512. Jacobian 에 대해서도 ε_J.
- 지표: 격자점별 ε_φ 중앙값·최대, **비 = ε_φ / denoising 오차(‖D(q) − h‖/‖h‖) 의 중앙값** (구간별 = 구간 내 격자점 중앙값의 중앙값), GMM b\* 대조(기대 ~1e-15). §2.1 의 실제 질의에서도 반복별·실패별로 보고.
- 새 코드: `conf/code/diag_p1_phase.py`.

### 2.4 P1-4 — pseudo-covariance. held-out + 실제 질의 (GPU)

- K = 0.5[(A−D) + j(C+B)], r_P = ‖ν K‖_F / max(‖ν J‖_F, ε). 변환 정확성은 선형-Gaussian toy(정확 posterior)에서 스크립트 안에서 먼저 검사(상대 1e-12 이내; 감사 P1-4a 에서 1e-15 확인).
- 지표: 격자점별 r_P 중앙값·최대 (V1/V0, GMM b\* 대조); 실제 질의(V1, C2 −3 dB) 반복별; **H4 판정** = 블록별 r_P(반복 4)를 같은 반복의 NMSE·ν_q 와 함께 넣은 로지스틱 회귀의 우도비 검정; "r_P 중앙값" = 이 회귀에 들어간 블록 r_P 의 중앙값. 반복 ≥ 8 평균은 보고 전용.
- 새 코드: `conf/code/diag_p1_pseudo.py` (`ScorePrior` 를 상속한 `conf/code` 어댑터가 K 도 반환; 기본 경로 무변경).

### 2.5 H0 — best vs last (통제 재학습, 새 태그)

- 기존 레시피·seed·split 그대로 **`ckpt_review_next/ctrl_N160000_a1.pt`** 에 학습(P0 수정 코드 → `_best.pt` 생성). 예산: GPU 1개 ≈ 10 h (20 s/epoch × ~1800). 기존 가중치와 bit-identical 일 것을 요구하지 않는다(GPU 비결정성).
- 개발 집합 C2 −3 dB n=640, V1 wiring, paired: **판정 쌍 = 재학습 best vs 재학습 last**(H0 규칙). 참조 = 기존 last-EMA vs 재학습 last(비결정성 크기; 판정 아님). 지표: 부호검정 p, Δ(순 블록), NMSE 중앙값·p90, 실패 겹침.
- 이 재학습은 §3.1 A1 의 **통제군**이기도 하다(같은 코드·같은 seed·같은 프로세스 규약).

### 2.6 진행 조건 (진단 → ablation). 여기서 고정

| 조건 | 임계값 | 만족 시 | 불만족 시 |
|---|---|---|---|
| C-phase | §2.3 에서 ε_φ / denoising 오차 중앙값 ≥ 0.10 인 구간이 **세 구간 중 하나 이상** (= H3(a) 의 정확한 여집합) | **A1** (§3.1) | H3 기각(a). augmentation 안 함 |
| C-cavity | **H1 이 기각되지 않음** (V1·C2 −3 dB·반복 8 에서 e_8 중앙값 ∉ [0.7, 1.4] **또는** a_8 중앙값 > 3) | P2-B(공분산 조건부 denoiser) 프로토타입 설계 문서 (실행은 별도 사전 등록) | P2-B 보류 |
| C-pseudo | **H4 가 기각되지 않음** (반복 4 블록 r_P 중앙값 ≥ 0.2 **그리고** 우도비 p < 0.05) | P2-A 설계 문서 (실행은 별도 사전 등록; **GMM 에도 같은 인터페이스를 넣는다** — 감사 M1) | H4 기각. P2-A 보류 |
| C-calib | **H2 가 기각되지 않음** (20 격자점 합산 7점 이상에서, floor 제외 부분공간 기준 ρ_tr ∉ [0.8, 1.25] 또는 90% coverage ∉ [0.85, 0.95]) | A2 표에 PSD floor 변형(ν 상대 floor 1e-2) 을 **보고 전용** 행으로 추가 | 기록만 |
| C-clip | **조건 아님 — 이미 알려진 사실**: raw_B16e4k C2 −3 dB 에서 V1 clip 비율 0.908, +6 dB 0.767, bstar 0.798/0.586 (`REVIEW_AUDIT` P1-4b). | **A2 는 무조건 실행**(§3.2) | — |

임계값 근거: 0.10 은 감사의 예비 측정(n=16, 미저장: 0.29/0.16/0.07 @σ 0.033/0.182/0.845)이 하·중에서 넘고 상에서 못 넘는 값 — 예비 측정을 n=512 로 확인하는 검사가 된다. 0.2 / 우도비 0.05 는 "작지 않고 NMSE 로 설명되지 않는 추가 정보" 의 최소 요건. [0.7, 1.4], [0.8, 1.25], a ≤ 3 은 예비 자료 없이 정한 관용 폭이다.

---

## 3. Ablation

### 3.1 A1 — 전역 위상 augmentation (prior 자체의 개선). C-phase 만족 시

- 구현: `score.train(phase_aug=True)` opt-in. 학습 표본 b 와 잡음 e 에 표본마다 하나의 e^{jφ}(φ ~ U[0, 2π), **별도 generator**, 체크포인트에 상태 저장) 를 곱한다. 기본 스트림 bit-identical 유지(selftest). angle/phase-ramp augmentation 과 섞지 않는다.
- **승격 기준은 BLER 이 아니라 D1 게이트다** (`10_SPEC` §3b "arm 으로 승격할 변형은 D1 게이트 통과 여부로만 정한다", `04_SPEC` §6). 순서:
  1. **D1 형제 학습** `sx_N160000_D1_aug.pt` (phase_aug=True, 나머지 동결 레시피) → **GA~GD 측정**(기존 게이트, 완화 없음). **FAIL 이면 A1 은 여기서 끝**이고 실패로 보고한다(개발 BLER 을 보지 않는다).
  2. **1단계 ablation (N_train = 1e4, GPU, 변형당 ≈15 분)**: {aug, ctrl} × attempt 1·2·3, 각 학습은 별도 프로세스. 지표(**전부 보고 전용**): GB′(GMM b\*=kron K=512@1e4 대비), ε_φ, 개발 집합 C2 −3 dB n=640 BLER(V1 wiring, `_best.pt`). **검정**: 시행별로 3 attempt 의 실패 지표(`blk_err[:, -1]`, 예외로 실패한 블록 = 1)를 평균한 뒤 d = mean_aug − mean_ctrl 에 대해 **640 단위 양측 부호검정** 하나(d = 0 인 시행은 버리고, d < 0 / d > 0 의 개수로 검정)(같은 시행이 세 attempt 에 공유되므로 attempt 를 합쳐 n 을 부풀리지 않는다). 부차: attempt 별 3개 paired 검정과 "3 중 2 개선" 여부. MDD(≈13~20 순 블록) 를 같이 적는다.
  3. **2단계 (1 의 게이트 PASS 시에만; 2 의 결과와 무관하게 진행하되 2 의 결과를 함께 보고)**: N_train = 1.6e5, attempt 1, aug 1개(통제군 = §2.5). GPU 1개 ≈ 10 h. 개발 집합 3점(C2 −3(판정)/+6, C5 −3(보고))에서 paired 검정.
  4. **테스트 집합 확증 (2단계에서 C2 −3 dB 부호검정 p < 0.05 이고 aug 의 실패가 더 적을 때만, 한 번)**: 1차 비교 = **aug-V1(best) vs ctrl-V1(best)**, 지표 BLER@16(`blk_err[:, -1]`), **판정점 C2 −3/0/+3 dB**. **통과 = 세 판정점 중 2점 이상에서 aug 실패 < ctrl 실패 이고 exact 양측 부호검정 p < 0.05, 그리고 08_SPEC §2 power guard(3점 모두 있고 ≥ 2점에서 불일치 ≥ 6)**; pooled p 는 보고 전용, 나머지 SNR 은 보고 전용. 두 체크포인트 각각을 새 태그로 **테스트 집합 실행 2회**(ctrl-V1(best) 도 여기서 처음 테스트 집합에 돈다; `--arm M-ours-dscore-C-V1 R5-genie` 로 비용 제한), 짝 비교는 `pair_tags.py`(§6 선행 작업: 두 raw 디렉터리를 (cell, snr, skip) 로 맞추고 exp_0921_analysis.sign_p 로 계산). n=2560, 기존 표 무수정.
  5. **헤드라인 교체는 4 를 통과했을 때만**, 그리고 "게이트 통과 = D1 형제(aug)" 로 표기해서. 4 가 실패하면 A1 은 "개발 집합에서만 개선" 으로 기록된다.
- 성공 문장의 범위: "위상 augmentation 은 prior 자체의 개선이다(adapter·루프 불변)". 추론 비용 동일(벤치로 확인).
- 실패 처리: 학습 발산은 §3d, 실패한 attempt 도 표에 남긴다. ε_φ 만 줄고 BLER 불변이면 H3(b).

### 3.2 A2 — clip='mean' 대칭 ablation (adapter 의 효과). 무조건 실행, 개발 집합 전용, 보고 전용

- arm 추가(opt-in `build_our_arms(mean_arms=True)`, 기존 arm 무변경):
  - `M-ours-dscore-C-V1-mean` — RouteAClip clip='mean' (denoiser 단계 평균 h_H 보존)
  - **대칭 대조군** `gmmB-scorew-eta` / `gmmB-scorew-mean` — GMM b\* 를 **V1 과 같은 RouteAClip 배선**(mode scalar, belief, matrix site; `diag_ep_site.py` 의 gmmB|scorew 셀)에 넣은 것. clip 의미가 V1 과 동일하므로 이것이 adapter 효과의 진짜 대조군이다.
  - `M-ours-bstar-mean` — GMMPriorB.view('mean') (최종 colored belief 평균 m 보존; **의미가 다르므로 보고 전용 행**, 감사 M3)
- 개발 집합 C2 −3 dB(판정)·+6 dB·C5 −3 dB(보고), paired. 지표: BLER, NMSE, clip 비율·shift, ‖h_post − h_H‖/‖h_H‖.
- 판정(H5): V1-mean vs V1-eta 부호검정. **귀속 규칙**: 시행별 d = (fail_V1-mean − fail_V1-eta) − (fail_gmmB-mean − fail_gmmB-eta) 에 대한 exact 양측 부호검정(d = 0 제외). p < 0.05 이고 V1 쪽 개선이 더 크면 "prior 에 특이적인 adapter 효과", 아니면 "adapter 일반 효과 또는 판정 불가". 어느 쪽이든 **prior 이득으로 쓰지 않는다**. 테스트 집합 확증은 이 문서 범위 밖(필요하면 skip ≥ 3200 의 새 스트림으로 별도 사전 등록).

### 3.3 P3 (루프) — 이번 문서 범위 밖

damping·restart·n_inner 는 prior/adapter 실험과 분리해 별도 사전 등록한다. 재시작 선택은 관측 가능한 기준만(CRC 없음 — 가정하지 않는다).

---

## 4. 지표 정의

- **주 지표**: 개발 집합 paired 실패 지표 → 양측 부호검정(§0). 확증에서만 테스트 집합.
- **보조**: NMSE@16 평균·중앙값·p90/p95/p99(실패·발산 블록 포함), 실패 겹침, GB′, ε_φ, r_P, ρ_tr·coverage(floor 제외), clip 비율·shift, Module H 실경로 비용.
- 상대 BLER 감소는 **실패 수**로 계산하고 dB gain 이라 부르지 않는다.

## 5. 중단·발산 판정 (미리)

- 학습: `04_SPEC` §2 + §3d DIVERGE_TRAIN(P0 수정으로 음수 loss 안전, 재개 시 카운터 복원). ABORTED 는 attempt 로 세지 않는다.
- 수신기 블록: 기존 발산 판정 그대로, **표에서 빼지 않는다**.
- 진단 스크립트: 표본 수·격자·seed 를 결과 헤더에 적는다. 표본 수를 줄여야 하면 헤더와 이 문서 §6 에 남긴다.

## 6. 실행 현황 (갱신한다)

| 항목 | 상태 | 산출물 |
|---|---|---|
| 선행: `runner.py --skip0` (개발 집합 생성 수단) + 수용 검사 | **구현** (chunk_plan, DEV_SKIP0, load_raw 구멍 검사, manifest split 표기; selftest `[chunk]`) | 미커밋 |
| 선행: `score.train(init_seed=...)` opt-in + 체크포인트에 init_seed·초기 해시·phase_aug | **하지 않음** — 사용자 결정(2026-09-22 17:45 CDT, 올바른 전제로 재확인): 기록만. §0 규정대로 A1 의 aug/ctrl·attempt 비교는 "초기값 차이 포함" 으로 표기하고, 각 학습의 `torch.initial_seed()`·초기 가중치 해시를 로그에 남긴다(`train_ctrl.py` 방식) | — |
| 선행: `pair_tags.py` (태그 간 paired 부호검정 + 3점 규칙) | **구현·검증** (tables_D2_B16e4k 표 B p 값 재현) | `conf/code/pair_tags.py` |
| 선행: D1 형제 학습 wrapper (`train_ctrl.py` 확장: testbed D1, 기존 rung 라벨, phase_aug) | **구현·검증** (`--testbed D1 --phase-aug --gate`; 기존 sx_N160000_D1.pt 의 rung/prior/hp 와 일치 확인 후에만 학습) | `conf/code/train_ctrl.py` |
| 선행: `build_our_arms(mean_arms=True)`, gmmB-scorew arm | **구현·검증** (runner `--mean-arms`, --tag 필수; 기본 arm 집합 비트 동일; gmmB-scorew 가 ep_site 가 아닌 _matrix_site 경로를 탐 확인) | `arms.py`, `runner.py` |
| 선행: `score.train(phase_aug=True)` + selftest | **구현·검증** (별도 generator, 체크포인트에 rng_phase, 재개==무중단, 기본 경로 비트 동일; selftest [A1r~A1e]) | `score.py`, `selftest_ckpt.py` |
| §2.1 P1-1 cavity | **완료** (18:25 CDT, 개발 집합 4점 × 640). 판정점 C2 −3 dB: e_8 = 1.025, a_8 = 0.753 → **H1 기각** → C-cavity 불만족, P2-B 보류. H4: 반복 4 r_P 중앙값 0.482, NMSE·ν_q 통제 우도비 p = 0.69 (로그 변환 0.54) → **H4 기각** → C-pseudo 불만족, P2-A 보류 | `p1_cavity_*.{npz,txt}` |
| §2.2 P1-2 calibration | held-out **완료** (18:05 CDT): H2 기각 안 됨, C-calib 만족(1/20 점만 두 대역 충족; ρ_sub 는 대역 안, cov90 이 대역 밖). 실제 질의 부분은 §2.1 과 함께 | `p1_heldout.{npz,txt}` |
| §2.3 P1-3 phase | held-out **완료**: C-phase 만족(0.246/0.148/0.083, 해석 무관) → A1 진행 | `p1_heldout.{npz,txt}` |
| §2.4 P1-4 pseudo | held-out(보고 전용) 완료: V1 r_P 0.33~0.49. 판정(H4)은 §2.1 실제 질의 반복 4 에서 | `p1_heldout.{npz,txt}` |
| §2.5 H0 통제 재학습 | **완료** (23:39 CDT). best vs last(같은 run) C2 −3 dB 85:85, 불일치 6:6, p=1 → **H0 기각 안 됨**. 참조 기존 last-EMA 88 (8:11, p=0.648) | `ckpt_review_next/ctrl_N160000_a1{,_best}.pt`, `H0_*.txt` |
| §3.1 A1 | 1단계 **D1 형제 게이트 PASS** (GA 9.5e-16, GB 4.8e-4, GC 0.081, GD 0.066; `_best.pt` epoch 164). 2단계(N=1e4, 개발 집합 C2 −3 dB): aug 평균 83.3 vs ctrl 86.0 실패, 1차 부호검정 15:19 p=0.608 → **판정 불가**. 3단계: aug_N160000_a1 학습 중(09-23 00:06 CDT epoch 1071), 끝나면 `run_h0_a1s3.sh` 가 개발 집합 평가·부호검정 자동 실행 → `A1s3_*.txt` | `gate_aug_D1_N160000_a1.txt`, `A1s2_group_C2_m3.txt` |
| §3.2 A2 | **완료** (19:52 CDT). C2 −3 dB: V1-mean vs V1-eta 88:88 (4:4, p=1) → **H5 기각**. 상호작용 9:19 p=0.087 → 귀속 조건 불충족. gmmB-scorew: mean 이 eta 보다 나쁨(134 vs 124, p=0.041). 보고 전용 floor1e-2 행: 88 | `raw_review_next_A2`, `A2_interaction_C2_m3.txt` |
| P0-2 실경로 비용 벤치 | 코드 있음, C6 종료 후 실행 | `complexity_moduleH_ep.txt` |
| §7 C6 재실행 (`NR16run2`) | 실행 중 (05:28~) | `raw_NR16run2`, `tables_D2_NR16run2.txt` |
| NR16 GB′ | 완료 (GPU, CPU 대조 7.4e-15) | `d2_gbprime_NR16_N10000_a1.npz` |


### 6.1 구현 시 해석 명확화 (2026-09-22 18:10 CDT, 전체 실행 전 — n=32·1 시행 스모크만 본 상태; 9~11 은 18:40 CDT, A1 학습 전)

구현(`diag_p1_heldout.py`, `diag_p1_cavity.py`)에서 문구가 두 가지로 읽히는 곳이 나왔다. 아래를 **1차 해석**으로 고정하고, 스크립트는 다른 해석의 값도 함께 출력해 판정이 해석에 따라 갈리면 `READING-DEPENDENT` 로 표시한다.

1. H2·C-calib 의 ρ_tr = **floor 제외 고유부분공간의 ρ_tr (ρ_sub)** — §1·§2.6 문구 그대로. 전체 공간 ρ_tr 은 보고.
2. §2.3 위상 풀링 = **φ = 2πk′/8, k′ = 1..7** (k′=0 은 항등이라 0 에 가까운 값만 더한다). k′=0..7 값도 보고.
3. §2.3 비 = **표본별 ε_φ/δ 의 중앙값**(격자점별) → 구간값 = 격자점 중앙값의 중앙값. 중앙값끼리의 비도 보고.
4. coverage 기준분포 = 수신기가 가정하는 **proper complex Gaussian** (2d² ~ χ²(2·dim)).
5. V0 의 "PSD 부분집합" = λ_min(Herm J) ≥ 0. floor 적중 = 고유값이 floor(1e-6)에 붙은 것만.
6. a_t 의 ν_E = 수신기 자신의 순서(cbar, 이후 nuE[t−1]) — SigL 재구성이 수신기 ν_q 를 오차 0 으로 재현.
7. §2.4 변환 검사는 선형-Gaussian toy 대신 **widely-linear 사상 m = Mq + Wq\*** 로 한다(K ≠ 0 이라 더 강한 검사).
8. 산출 파일명: held-out 은 `p1_heldout.{npz,txt}` 하나(키 접두사 calib|/phase|/pseudo|), 실제 질의는 `p1_cavity/` 청크 + 병합본 `p1_cavity_<point>.{npz,txt}`.
9. A1 체크포인트 이름: §3.1 의 `sx_N160000_D1_aug.pt` 대신 `ckpt_review_next/aug_D1_N160000_a1.pt` (D2 는 `aug_N<N>_a<k>.pt`, 통제군 `ctrl_N<N>_a<k>.pt`). 내용은 같다.
10. A1 학습이 §3d 로 발산하면 wrapper 가 자동 fallback 을 하지 않는다 — 발산 시 같은 태그 체계로 attempt 2(grad_clip 1.0), 3(+lr/3) 을 수동으로 실행하고 기록한다. 게이트는 발산한 run 에 대해 돌리지 않는다.
11. 2·3단계 학습은 1단계 게이트 결과 전에 **학습만** 미리 돌린다(GPU 여유). 개발 집합 BLER 은 1단계 PASS 뒤에만 계산하고, FAIL 이면 "학습됨·미평가" 로 기록한다(DECISIONS 2026-09-23 08:40 KST).

## 7. 미리 적는 예측과 약속하지 않는 것

- 예측: C-phase 만족(예비값 0.29/0.16 @하·중; 상 0.07). C-cavity: e_8 ∈ [0.7, 1.4] 이지만 a_8 > 3 → 만족(비등방 쪽). C-pseudo: 반복 4 r_P 중앙값 ≈ 0.4 로 크지만 NMSE·ν_q 통제 후 추가 설명력 없음 → 불만족. C-calib: 하 구간에서 ρ_tr < 0.8(과대 분산)이 7점 이상 → 만족. C-clip: 알려진 사실. H0 기각 안 됨(p ≥ 0.05). A1: D1 형제 게이트 PASS, 1단계 개발 집합 부호검정 p ≥ 0.05(MDD 이하의 개선) — 즉 **위상 augmentation 이 ε_φ 는 줄이지만 BLER 개선은 이 설계로 판정 불가**가 가장 그럴듯한 결과다. 빗나가면 그대로 쓴다.
- 어떤 진단 결과도 헤드라인(C2, `tables_D2_B16e4k.txt`)을 바꾸지 않는다. 헤드라인 교체는 §3.1 의 5 단계로만.
- D1 게이트 PASS 를 D2 참-score 정확성으로 쓰지 않는다. 새 진단은 게이트가 아니다.
