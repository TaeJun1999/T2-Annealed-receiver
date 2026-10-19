# 정답 사례: E4 수신 비용 벤치 `bench_cost.py` (구현 미열람)

- 작성: 2026-10-18 22:36 CDT (2026-10-19 12:36 KST), golden-writer (Opus 5.5). `/home/HTJ/t2_wtCost/conf/code/bench_cost.py` 와 그 worktree 의 새 파일은 열지 않았다.
- 명세: `reviews/spec_cost_bench.md`, 과제: `conf/results/review_next/prompts/PROMPT_SERVER_COST.md`, 틀: `~/.agents/prompts/golden.md`.
- 근거 코드의 판(版): worktree 브랜치 `e4-cost` = `9dd8b5fe` (`git rev-parse e4-cost`).
  - `score.py` · `common.py` · `Demo/t2_route_a.py` · `Demo/t2_gmm.py` 는 main 과 같다 (`git diff --quiet main 9dd8b5fe -- …` 의 exit 0). 그래서 이 파일들의 행 번호는 main 파일 기준이다.
  - `arms.py` · `runner.py` 의 행 번호는 `git show 9dd8b5fe:conf/code/…` 기준이다 ("@9dd8b5fe" 로 표시).
- 확인 스크립트는 모두 이 폴더에 있다. 실행은 전부 CPU 66–67, 1 스레드, GPU 없이, 개발 시행만 썼다. runner 명령은 실행하지 않았다(`g_runner.py` 는 모듈을 import 만 한다).
  - `g_sha.py`: sha256 계산
  - `g_fits.py`: b\* 규칙을 따로 다시 짜서 ll_val 과 covs 헤더를 읽는다
  - `g_ckpt.py`: checkpoint 메타데이터
  - `g_dtype.py`: 실행 시점 dtype
  - `g_count.py`: 내 계측. 로그 `g_count_D2_24.log` · `g_count_U32.log`. 로그에는 개발 시행 블록별 blk_err · nmse 가 들어 있다.
  - `g_stats.py`: 요약 통계 손계산 확인
  - `g_runner.py`: `parse_sparse_arms`, `_init` 경로
- **대조 전 유효 조건**: worktree 의 공유 코드가 `9dd8b5fe` 와 같아야 한다.
  - 확인 명령: `git -C /home/HTJ/t2_wtCost diff --quiet 9dd8b5fe -- conf/code/arms.py conf/code/score.py conf/code/runner.py conf/code/common.py Demo` 의 exit 이 0.
  - 아니면 G1–G4 를 다시 유도한다.
- 판정 규칙
  - 개수 · K · sha256 · 경로 · dtype 은 정확히 같아야 PASS 다.
  - 시간 값 자체에는 정답이 없다. G5 는 요약 함수(또는 npz 로부터의 재계산)에 손계산 입력을 넣었을 때의 출력이다.

---

## 0. 기대 표 요약 (시간 열 제외; 예외 없이 끝난 블록 기준)

| 셀 | arm (runner 이름) | SNR | 블록당 H 호출 | 블록당 네트워크 평가 E / backbone forward F | 블록당 VJP (논리) | 블록당 EM 단계 | K |
|---|---|---|---|---|---|---|---|
| D2 C2 8×4 | V1 `M-ours-dscore-C-V1` | −3, +6 | 16 | 16 / 32 | 1,024 | – | – |
| D2 C2 8×4 | b\* `M-ours-bstar` | −3, +6 | 16 | 0 | 0 | – | 1,024 |
| D2 C2 8×4 | V1-ms `M-ours-dscore-C-V1ms` (`--ms-arm`) | −3, +6 | 16 | 16 / 32 | 1,024 | – | – |
| UMi28 C9 32×4 | V1 | −3, +3 | 16 | 16 / 32 | 4,096 | – | – |
| UMi28 C9 32×4 | GMM b\* (K4096 태그) | −3, +3 | 16 | 0 | 0 | – | 4,096 |
| UMi28 C9 32×4 | GMM b\* (GCAP 태그) | −3, +3 | 16 | 0 | 0 | – | 8,192 |
| UMi28 C9 32×4 | SBL-loop (ρ 4, n_em 3, cold) | −3, +3 | 16 | 0 | 0 | 48 | – (사전 원자 M = 2,048) |

- 행 수
  - 기본은 D2 4 행 (`--ms-arm` 이면 6 행), UMi32 8 행이다.
  - UMi32 의 V1 · SBL 은 두 GMM 태그의 build_point 어느 쪽에서 만들어도 같은 객체 구성이다 (같은 ckpt, 같은 fullK32 → 같은 Chat · Cs). 그래서 SNR 마다 한 행씩만 있어야 한다. 같은 arm 을 두 번 재어 두 행으로 내면 명세의 표 구조(셀 × arm × SNR, 명세 70 행)와 어긋나므로 결함으로 본다.
- E 와 F 의 정의는 G2 에 있다. 과제의 "forward 16" 은 E 정의일 때만 맞다.

---

## G1. 블록당 module H 호출 수 (외부 반복 16, n_inner 1)

**공통 근거 (조기 종료 없음)**
- `RouteA.run` 의 외부 루프 `for t in range(n_iter)` (Demo/t2_route_a.py:339) 안에는 break · return · raise 가 없다. 유일한 return 은 루프 뒤 435 행이다.
- `RouteAClip` 은 `run` 을 다시 정의하지 않는다 (Demo/t2_gmm.py:101-123).
- 그래서 예외 없이 끝난 블록은 언제나 n_iter = `C.N_ITER` = 16 회 돈다 (common.py:49). "중간 종료" 는 구조상 0 이다.
- H 호출이 16 보다 적은 블록은 예외로 끝난 블록뿐이다.

| 사례 | 입력 (arm, 구성) | 기대 출력 | 근거 |
|---|---|---|---|
| G1-a | V1: `route_a(…, sp_v1, "score", clip="eta")` → RouteAClip, mode scalar, scal belief, hsite matrix, n_inner 1, init_colored 0, nu_sw None (arms.py@9dd8b5fe:18-51, 451) | `prior.denoise` 16 회, `rx._matrix_site` 16 회. 둘을 i 번째끼리 짝지어 **H 호출 16** | t2_route_a.py:346 에서 use_scalar 는 항상 참 (init_colored 0). 347 조건은 거짓 (scal belief, nu_sw None). 360 의 belief 분기 → 361 `for _ in range(n_inner=1)` → 365 denoise 1 회. 369-370 의 hsite matrix → `_matrix_site` 1 회 |
| G1-b | V1-ms: `route_a(…, MatchedScalarPrior(새 ScorePrior), "score", clip="eta")` (arms.py@9dd8b5fe:200-215, 502) | denoise 16, _matrix_site 16 → **H 호출 16** | 같은 분기다. MatchedScalarPrior 는 `denoise` 를 감싼 prior 의 것으로 그대로 넘기고 (`__getattr__`), `denoise_full` 만 바꾼다 |
| G1-c | b\*: `route_a(…, hp[bstar].view("eta"), "gmm_site")` → RouteA, mode colored, exact_prior True (arms.py@9dd8b5fe:36, 445) | `prior.ep_site` **16** | mode colored 라 use_scalar 는 거짓이다 → 372-374 의 else 분기, exact_prior → `ep_site` |
| G1-d | SBL-loop: `route_a(…, SparsePrior(Cs, 32, 4, 4, 3, warm=False), "gmm_site")` (arms.py@9dd8b5fe:512) | `SparsePrior.ep_site` **16** | 같은 else 분기다. SparsePrior 에 ep_site 가 있어 exact_prior 가 참이다 (t2_route_a.py:277) |

**SBL 의 module H 정의**
- `SparsePrior.ep_site(G, b, lam_min)` 한 번이 H 호출 하나다 (arms.py@9dd8b5fe:351-355).
- 그 안에서 `gamma()` 가 EM 을 n_em 단계 돌고, 이어서 사이트를 만든다 (Cx = A diag(γ) Aᴴ + εI, 그 역행렬).
- GMM 의 `ep_site` 와 같은 자리(같은 else 분기)라서 두 arm 의 H 정의가 짝을 이룬다.

**판정**
- score arm 의 "H 호출 수/블록" 은 16 이다 (denoise + _matrix_site 한 쌍이 한 호출). 두 메서드를 따로 세어 32 라고 적으면 정의 오류다. 기존 bench 도 쌍으로 셌다 (`bench_moduleH_ep.py:113-118`).
- 완료된 블록에서 denoise 수 ≠ _matrix_site 수이거나 16 이 아니면 결함이다.

**실측 (내 계측 `g_count.py`, bench 아님)**
- D2 −3 · +6 dB, 시행 2560 과 측정 블록 2561..2584 (SNR 마다 24 블록): V1 · V1-ms 는 모든 블록에서 denoise 16 · _matrix_site 16, b\* 는 ep_site 16, 반복 16, 예외 0.
- UMi32 −3 · +3 dB, 시행 2560 · 2561: V1 은 denoise 16 · _matrix_site 16, SBL 은 ep_site 16.

**경계 사례**
- G1-e (블록 하나가 예외)
  - 입력: rx.run 이 반복 6 에서 예외를 낸 블록 (그 전에 H 호출 5 회).
  - 기대: 예외 수 +1. 그 블록의 rx.run 시간 · 블록 H 누적 · 호출당 값 5 개는 통계에 넣지 않는다. "H 호출/블록" 은 완료 블록만으로 16 이다.
  - 근거: 명세 "예외는 세고, 시간에 넣지 않는다". 기존 bench 는 except 에서 continue 하고, 다음 run 전에 Tap 목록을 비운다 (`bench_moduleH_ep.py:100-108`).

---

## G2. 블록당 네트워크 forward 수와 VJP 수

**코드 구조**
- `ScorePrior._eval(q, ν)` (score.py:1107-1131)
  - 키는 `(q.tobytes(), float(ν))` 다 (1111).
  - 직전 키와 같으면 캐시를 돌려주고 네트워크를 부르지 않는다 (1112-1113).
  - 다르면 `n_query += 1` (1114) → `Jr = torch.func.jacrev(f)(x)` (1120) → **`m = np_unpack(f(x)…)` 로 forward 를 한 번 더** 돈다 (1121).
- 호출 경로: `f` = `tweedie_real` (589-592) → `score_real` 의 vp 분기 (411-412) → `_vp` (390-393) → `raw` (382-385) → `self.net(…)` 1 회.
- 두 checkpoint 모두 hp 가 arch `dit`, param `vp`, domain `angle` 이다 (`g_ckpt.py`).
- 설치된 torch 2.14.0+cu130 의 `jacrev` (`torch/_functorch/eager_transforms.py`, `wrapper_fn`)
  - `_vjp_with_argnums(func, …)` 에서 forward 를 1 회 돈다.
  - `chunk_size=None` 이면 출력(2N 실수)의 표준 기저 전체를 `vmap(vjp_fn)(basis)` 한 번으로 처리한다.
  - 그래서 **논리적 VJP 2N 개 = 벡터화된 backward 1 회** 다.
- 캐시 미스 한 번의 비용
  - jacrev 1 회 = 논리 VJP 2N 개
  - backbone (`sp.model.net`) forward 2 회 (jacrev 안에서 1 회 + 1121 행에서 1 회)
- **`_matrix_site` 안의 `denoise_full` 은 캐시 히트다.**
  - 반복마다 `denoise(q, ν)` 가 먼저 오고, 이어서 `_matrix_site` 가 같은 q 객체와 같은 ν 로 `prior.denoise_full` 을 부른다 (t2_gmm.py:113).
  - 실측: n_query 증가 16 = jacrev 16, `_eval` 호출 32.
- **PSD 투영(V1)은 forward 수를 바꾸지 않는다.**
  - `project_psd` 는 numpy `eigh` 만 쓴다 (score.py:603-619; 적용은 1129).
- V1-ms 는 build_point 가 새로 만든 ScorePrior 를 감싼다 (runner.py@9dd8b5fe:408). 그래서 V1 과 캐시 · 카운터를 공유하지 않고, 수는 V1 과 같다.

**정의와 기대값 (블록당, 예외 없이 끝난 블록)**

| 양 | 정의 (셀 수 있는 지점) | 8×4 (2N = 64) | 32×4 (2N = 256) | 과제 기대값과 비교 |
|---|---|---|---|---|
| E 네트워크 평가 수 | `torch.func.jacrev` 호출 수 = `ScorePrior.n_query` 증가분 = 캐시 미스 수 | **16** | **16** | "forward 16" 은 이 정의에서만 맞다 |
| F backbone forward 실행 수 | `sp.model.net` 의 forward 호출 (forward hook) 또는 `sp.model.score_real` 호출 | **32** | **32** | **기대 16 과 다르다.** 1121 행이 m 을 위해 forward 를 한 번 더 돈다 |
| V 논리적 VJP 수 | jacrev 호출마다 Jacobian 행 수 (= f 의 출력 원소 수 2N) 의 합 = E × 2N | **1,024** | **4,096** | 같다 (16·2N) |
| B 물리적 backward 실행 수 | vmap 된 `vjp_fn` 호출 = jacrev 호출 | 16 | 16 | 참고용 |
| (오답 함정) `_eval` 호출 수 | denoise 16 + denoise_full 16 | 32 (그중 히트 16) | 32 | forward 수로 쓰면 안 된다. F 와 수가 같은 것은 우연이다 |
| (오답 함정) `sp.model` (ScoreModel) 의 forward hook | ScoreModel 에는 `forward` 가 없고, `score_real` 은 `__call__` 을 거치지 않는다 | 0 | 0 | 0 이 나오면 hook 을 잘못된 모듈에 건 것이다 |

**실측 (`g_count.py`)**
- 계측 방법: `torch.func.jacrev` 를 감싸 호출 수와 Jacobian 행 수를 세고, `sp.model.net` 에 forward hook 을 걸었다.
- D2 V1 · V1-ms (−3 · +6 dB, 측정 24 블록 각각과 워밍업 2560)
  - jacrev 16, Jacobian 모양 (64, 64), 행 합 1,024
  - forward hook 32
  - n_query 증가 16, denoise_full 16
- UMi32 V1 (−3 · +3 dB, 시행 2560 · 2561)
  - jacrev 16, Jacobian 모양 (256, 256), 행 합 4,096
  - forward hook 32
  - n_query 증가 16

**판정**
- bench 가 F 를 센다면
  - 32 가 맞다.
  - "기대값 16 과 다름 (사유: `_eval` 이 jacrev 뒤에 m 을 위해 forward 를 한 번 더 돈다, score.py:1121)" 이라고 적어야 한다.
  - 16 이라고 적으면 결함이다.
- bench 가 E 를 센다면
  - 16 이 맞다.
  - 이 값이 "jacrev 호출(네트워크+Jacobian 평가) 수" 이고 평가 한 번이 backbone forward 2 회라는 점을 적어야 한다.
- VJP
  - 정의 V 로 1,024 / 4,096 이다.
  - backward 실행 수(B, 16)를 VJP 로 적거나, 2N 을 곱하지 않은 jacrev 수를 VJP 로 적으면 정의 불일치(결함)다.
  - 2N 은 가정해서 곱하면 안 되고, Jacobian 행 수(64 / 256)를 실제로 읽은 값이어야 한다. 명세는 "코드에서 센 값" 을 요구한다.
- GMM · SBL arm 은 forward 0 · VJP 0 이다 (네트워크가 없다).

**경계 사례**
- G2-x (arm 분리)
  - 입력: D2 에서 `--ms-arm` 으로 V1 과 V1-ms 를 같은 블록에서 돌린다.
  - 기대: arm 마다 E 16 · F 32 · V 1,024 다.
  - 결함 신호: 전역 카운터(예: jacrev 감싸기)를 arm 사이에 비우지 않으면 한쪽에 32 / 64 / 2,048 이 나온다.
- G2-y (캐시 히트로 E 가 줄 수 있음)
  - E 는 구조상 ≤ 16 이다. 연속된 두 반복의 (q, ν) 가 비트 단위로 같으면 둘째 반복의 denoise 도 캐시 히트가 되어 E 가 줄어든다.
  - 관측: 확인한 블록 (D2 2 SNR × 25 블록 × V1 · V1-ms, UMi32 2 SNR × 2 블록 × V1) 에서는 전부 16 이었다.
  - bench 는 E 를 가정하지 말고 세야 한다. 16 미만이 나오면 그 블록의 n_query 증가분과 같은지로 확인한다 (같으면 결함 아님).
- 워밍업 블록(시행 2560)도 같은 수(16 / 32 / 2N·16)를 갖지만 보고하지 않는다.

---

## G3. SBL 의 블록당 EM 단계 수 (ρ 4, n_em 3, cold)

**입력**
- `runner.parse_sparse_arms("4,3,1,1")` = `{'rho_sbl': 4, 'n_em': 3, 'rho_omp': 1, 'L': 1}` 다. "warm" 키가 없으므로 cold 다 (runner.py@9dd8b5fe:331-340, `g_runner.py` 출력).
- 비교용 입력
  - `"4,3,1,1,0"` 은 같은 dict 를 준다.
  - `"4,3,1,1,1"` 은 `'warm': True` 가 더해진다.
  - `"4,3,1"` · `"4,3,1,1,2"` 는 ValueError 다.
- `runner.SPARSE` 에 넣으면 `_sparse_at(±3)` 도 같은 dict 를 준다 (343-348).
- 등록 동결값은 `--sparse-arms 4,3,1,1`, `meta|sparse` = `{"L": 1, "n_em": 3, "rho_omp": 1, "rho_sbl": 4}` 다 (NEXT_EXPERIMENTS_U28NR32SBL.md:91).

**구조**
- `ep_site` 는 `gamma` 를 한 번 부른다 (arms.py@9dd8b5fe:352).
- `gamma` 는 `for _ in range(self.n_em)` (337) 를 break 없이 돈다.
- cold 이면 매 호출이 평탄 초기값 cbar·N/M 에서 시작한다.

**기대 출력**
- 블록당 EM 단계 = 16 (ep_site) × 3 = **48**.
- 사전 크기: `dft_dict(32, 4, 4)` 의 모양 = (128, 2048), 곧 M = **2,048** 원자 (= 128ρ²; 등록 문서 24 행).
- `rx.prior.n_em` = 3, `rx.prior.warm` = False.

**실측 (`g_count.py`)**
- UMi32 −3 · +3 dB, 시행 2560 · 2561 에서 ep_site 16, gamma 16, EM 단계 48 이다.
- EM 단계는 arms.py 안의 `np.einsum` 호출로 셌다. EM 한 단계에 einsum 이 1 회 불리고, ep_site 의 사이트 구성에는 einsum 이 없다.
- 사전 모양 (128, 2048) 도 확인했다.

**경계 사례**
- G3-a: warm(`4,3,1,1,1`)이어도 단계 수는 48 이다 (초기값만 다르다). 단계 수로는 cold 와 warm 을 가를 수 없다. 그래서 bench 는 설정 자체(meta sparse 문자열, `rx.prior.warm` False)도 기록해야 한다.

---

## G4. GMM arm 의 K: fits 폴더 구성과 b\* 선택 규칙

**규칙**
- 폴더 경로: `runner._init(tag)` 가 `arms.D2_FITS = <C.CONF>/results/gmm_fits_D2_<tag>` 로 정한다 (runner.py@9dd8b5fe:93-94, 113). `_init` 은 폴더를 만들지 않는다.
  - 예: worktree 에서 `_init("X")` → `/home/HTJ/t2_wtCost/conf/results/gmm_fits_D2_X`.
- 읽는 파일: `load_fits` 는 이름이 `fit_{prior}_Nr{Nr}_{fam}K{K}_n{ntrain}.npz` 이고 K ∈ D2_KS = (16 … 8192) 인 파일만, 있는 것만 연다 (arms.py@9dd8b5fe:72, 81-97).
  - `.k0r0.npz` · `.cont50.npz` · `.started_*` 는 무시된다.
  - ntrain 이 160000 이 아니면 파일을 찾지 못한다. bench 는 `build_point(…, ntrain=160000)` 이어야 한다.
- 선택: `gmm_selection` (106-115)
  1. kron 가족 안에서 ll_val 이 최대인 K 를 kron_K 로 고른다.
  2. 그 kron 과 full K 들을 놓고 ll_val 이 최대인 것이 b\* 다.
  3. 동률이면 dict 순서상 먼저 들어간 full 이 이긴다.
- 결과 객체: `M-ours-bstar = hp[bstar].view("eta")` (445), `meta = {bstar, kron_K}` (520).
  - `GMMPriorB.K = len(covs)` 다 (t2_gmm.py:30).
  - view 는 배열을 공유하는 얕은 복사본이다 (71-75).
- 필수 파일: build_baseline_arms 는 `fits[("full", 32)]["Chat"]` 가 반드시 있어야 한다 (arms.py:123).

**ll_val 과 covs 헤더** (`g_fits.py` 가 npz 에서 직접 읽음)

| 파일 | ll_val | covs (npy 헤더) |
|---|---|---|
| `fit_S2_Nr8_fullK32_n160000.npz` | −31.459660792742984 | (32, 32, 32) complex128 |
| `fit_S2_Nr8_kronK1024_n160000.npz` | −11.459169831224418 | (1024, 32, 32) complex128 |
| `fit_UMi28_Nr32_fullK32_n160000.npz` | 54.033261174240884 | (32, 128, 128) complex128 |
| `fit_UMi28_Nr32_kronK4096_n160000.npz` | 152.23176788511105 | (4096, 128, 128) complex128 |
| `fit_UMi28_Nr32_kronK8192_n160000.npz` | 154.13990347772582 | (8192, 128, 128) complex128 |

**사례**

| 사례 | 폴더 구성 (입력) | 기대 `meta["bstar"]` | 기대 `meta["kron_K"]` | M-ours-bstar 의 `rx.prior.K` |
|---|---|---|---|---|
| G4-a | D2: fullK32 + kronK1024 (B16e4k 의 두 링크가 가리키는 파일의 바이트 복사본) | `'kron'` | 1024 | **1024** |
| G4-b | D2: `gmm_fits_D2_B16e4k` 전체 (Nr8 13 개: full 16–512, kron 16–1024) | `'kron'` | 1024 | **1024** (G4-a 와 같다. 기존 bench 의 assert 와도 같다, bench_moduleH_ep.py:80) |
| G4-c | UMi32 K4096 태그: fullK32 + kronK4096 | `'kron'` | 4096 | **4096** |
| G4-d | UMi32 GCAP 태그: fullK32 (`t2_wtS/…/gmm_fits_D2_U28NR32B16e4` 의 것) + kronK8192 (`gmm_fits_D2_U28NR32GCAP`) | `'kron'` | 8192 | **8192** |
| G4-e (참고) | `t2_wtS/…/gmm_fits_D2_U28NR32B16e4` 전체 (Nr32 15 개) | `'kron'` | 4096 | 4096. 등록 raw 의 `meta\|kron_K` 4096 · `ll_val\|kron` 152.23176788511105 와 같다 (NEXT_EXPERIMENTS_U28NR32SBL.md:105) |
| G4-f (경계) | GCAP 원본 폴더만 (kronK8192 와 `.k0r*` · `.cont50` · `.started_*`; **fullK32 없음**) | (gmm_selection 만 보면 `'kron'`, 8192) | – | build_point 가 `fits[("full", 32)]` 에서 **KeyError** 를 낸다. 측정 전에 멈춰야 하고, 측정이 진행되면 결함이다 |
| G4-g (경계) | fullK32 + kronK4096 + kronK8192 를 한 폴더에 | `'kron'` | **8192** (4096 이 아님) | 8192. "K4096 arm" 이 소리 없이 8192 가 된다. 그래서 두 GMM 은 태그별 폴더가 따로 있어야 하고 (명세 77 행), bench 는 `meta["kron_K"]` 가 의도한 K 인지 확인해 기록해야 한다 (명세 31 행) |

**참고**
- D2 의 fits 폴더가 두 파일이든 B16e4k 전체든 K 는 1024 다. 명세 23 행은 두 파일을 적었으므로 어느 쪽도 명세 위반은 아니다.
- B16e4k 의 파일은 심볼릭 링크다. 복사본이 링크가 아닌 실제 바이트인지 확인한다 (`os.path.islink` 가 False).
- 두 UMi GMM 태그의 fullK32 는 같은 파일이다. 그래서 두 arm 의 Cs · Chat (초기 ν · eh2) 가 같고, 다른 것은 kron 성분뿐이다.

---

## G5. 요약 통계 손계산 (numpy 기본 percentile = linear)

**정의** (기존 bench 의 식: `bench_moduleH_ep.py:61-62, 113-118, 141-144`; 명세 49-55 행)
- 호출당 값
  - (셀, SNR, arm) 의 측정 블록 전체 호출을 **한 배열로 모은 뒤** median, [p25, p75], p90 을 낸다.
  - score arm 의 호출당 값 = denoise_i + _matrix_site_i (같은 i 번째 호출끼리 더한다).
- 블록 H 누적 = 그 블록의 호출당 값의 합이다.
- rx.run: 블록별 값의 median 과 [p25, p75] 다.
- H 비중: 기존 bench 정의는 median_b (H 누적_b / rx.run_b) 다. 집계 방식은 명세에 없다 (S4 와 "정답 미정" 참고).
- linear 보간: 위치 = p/100 × (n − 1) 이고, 이웃한 두 정렬값 사이를 선형으로 보간한다.
- 단위는 상관없다. 같은 단위로 넣고 같은 단위로 읽는다.
- **G5-0 재계산 규칙**: txt 표의 값은 같은 실행의 npz (블록별 · 호출별 원자료) 를 위 정의로 numpy 재계산한 값과 같아야 한다 (표시 자릿수 안에서).

| 사례 | 입력 | 기대 출력 | 계산 |
|---|---|---|---|
| S1 | 호출당 8 개: [3, 1, 4, 1, 5, 9, 2, 6] | median **3.5**, p25 **1.75**, p75 **5.25**, IQR 폭 **3.5**, p90 **6.9** (부동소수 6.8999999999999995) | 정렬 [1,1,2,3,4,5,6,9], n−1 = 7. median (3+4)/2. p25: 위치 1.75 → 1 + 0.75·(2−1). p75: 위치 5.25 → 5 + 0.25·(6−5). p90: 위치 6.3 → 6 + 0.3·(9−6) |
| S2 | score arm 한 블록 4 호출 (실제는 16): denoise [2.0, 3.0, 2.5, 4.0], _matrix_site [0.5, 0.4, 0.6, 0.5] | 호출당 [2.5, 3.4, 3.1, 4.5], 블록 H 누적 **13.5**, median **3.25**, p25 **2.95**, p75 **3.675**, p90 **4.17** | 정렬 [2.5, 3.1, 3.4, 4.5]. p25: 위치 0.75 → 2.5 + 0.75·0.6. p75: 위치 2.25 → 3.4 + 0.25·1.1. p90: 위치 2.7 → 3.4 + 0.7·1.1 |
| S2 오답 신호 | 같은 입력 | denoise 만 재면 median 2.75. 두 목록을 이어 붙여(8 개) 통계를 내면 median 1.3, p25 0.5, p75 2.625, p90 3.3 | 이 값들이 나오면 짝 합산 정의를 어긴 것이다 |
| S3 | 블록 1 호출 [1, 2, 9], 블록 2 호출 [3, 4, 5]; 블록 H 누적 [12, 12]; rx.run [40, 30] | 호출당 (6 개를 모아서): median **3.5**, p25 **2.25**, p75 **4.75**, p90 **7.0**. 블록 H 누적 median **12**. rx.run median **35**, IQR **[32.5, 37.5]**, p90 39. H 비중 (블록별 비의 median) **0.35** | 모은 정렬값 [1,2,3,4,5,9]. p90: 위치 4.5 → 5 + 0.5·4. H 비중: median(12/40, 12/30) = median(0.30, 0.40). 블록 median 의 median(= median(2, 4) = 3.0)을 호출당 median 으로 내면 결함이다 |
| S4 (정의가 갈리는 입력) | 블록 H 누적 [0.20, 0.60, 0.30], rx.run [1.00, 1.20, 0.90] | 블록별 비의 median **0.333333** (기존 bench 정의). 합의 비는 0.354839 (= 1.10/3.10), median 의 비는 0.300000 이다. rx.run median 1.00, IQR [0.95, 1.10], p90 1.16 | 블록별 비 [0.2, 0.5, 0.3333]. rx.run 정렬 [0.9, 1.0, 1.2]: p25 위치 0.5 → 0.95, p75 위치 1.5 → 1.10, p90 위치 1.8 → 1.0 + 0.8·0.2 |
| S5 (경계: `--trials 1`, 값 하나) | rx.run [7.0], 블록 H 누적 [2.1] | median = p25 = p75 = p90 = **7.0**, IQR 폭 **0**. H 비중 = **0.3** (= 2.1/7.0) | n = 1 이면 모든 percentile 이 그 값이다. 호출당 값은 16 개 (블록 1 × 16) |
| S6 (경계: 빈 입력 = 모든 측정 블록이 예외) | 측정 24 블록 전부 rx.run 예외 | 호출당 · 블록 · rx.run 통계는 모두 **NaN**, 예외 수 **24**. 그 행은 표에 **남아야 한다** | 기존 bench `q()` 는 빈 배열이면 nan 을 낸다 (bench_moduleH_ep.py:61-62). `np.median([])` 도 경고와 함께 nan 이다. 행이 빠지거나 프로그램이 죽으면 결함이다 |
| S7 (경계: 블록 하나만 예외) | 블록 3 개 중 블록 2 가 반복 6 에서 예외 (H 호출 5 회 뒤) | 예외 **1**, H 호출/블록 = median(16, 16) = **16**. 호출당 배열은 블록 1 · 3 의 **32** 개만 쓴다 | 블록 2 의 5 개가 섞여 37 개가 되면 결함이다 (G1-e) |

- `g_stats.py` 출력이 위 값과 모두 같다.

---

## G6. 거부 사례

**공통 기대** (명세 18, 64, 67, 85 행)
- 거부할 때는 `rx.run` 이 한 번도 불리지 않는다(측정 없음).
- `conf/results/review_next/cost/` 에 새 파일이 생기지 않는다.
- 기존 파일은 바뀌지 않는다.
- 사유를 출력한다.
- 종료 코드는 명세에 없다 ("정답 미정" 참고).

**정상 파일의 sha256** (`g_sha.py`, 링크는 따라가서 계산; 명세 값과 모두 일치)

| 파일 | 크기 (B) | sha256 |
|---|---|---|
| `/home/HTJ/t2/conf/ckpt/d2sx_N160000_a1.pt` (D2 V1 · V1-ms, legacy-last: epoch 1784, best_epoch 1764, role None) | 7,837,523 | `4443921ce8d5c4a11c7cda879a53a66436f43bd76864734a3e6203cfb4b82f29` |
| `/home/HTJ/t2/conf/ckpt/d2sx_UMi28NR32_N160000_a1_best.pt` (UMi32 V1; role best, epoch = best_epoch = 232, sigma_tag U28NR32) | 7,900,779 | `463da87aa8dbfb614c38ea30bc8cd26e2ade5099a0eb48407dca592b46b854e9` (명세의 앞 16 자리 `463da87aa8dbfb61` 와 일치) |
| D2 `fit_S2_Nr8_kronK1024_n160000.npz` (실체 `gmm_fits_D2_K1024n160000/`) | 9,533,338 | `bf796b84037e1b3790ed5a6d7917ea2a79f2bee4a9f155f0d3385d856c950997` |
| D2 `fit_S2_Nr8_fullK32_n160000.npz` (실체 `gmm_fits_D2_n16e4/`) | 314,000 | `d4601650a888b4b355565a9010cf0a23499a3e92505e657e2cd79a1c152359f3` |
| UMi `fit_UMi28_Nr32_fullK32_n160000.npz` | 7,578,202 | `d572e0ac63013a96042a148aa1fceaa6662710ddfdbcfb4a4dd051271704e215` |
| UMi `fit_UMi28_Nr32_kronK4096_n160000.npz` | 942,018,761 | `2d72a4349e2700e79aec72b48bebed29e59b0f336091b9a6706dbd70d29ef569` |
| UMi `fit_UMi28_Nr32_kronK8192_n160000.npz` | 1,888,279,028 | `d883afaf2e3e6133685594c5e7eaa892ac371b90c41505b7acd4a2b3fd49f71b` |

**R1. sha256 이 다르면 측정하지 않는다** (원본은 건드리지 않고, 복사본의 경로를 바꿔치기한다)

| 사례 | 입력 | 기대 |
|---|---|---|
| R1-a | UMi32 V1 체크포인트 자리에 last 파일 `d2sx_UMi28NR32_N160000_a1.pt` 의 복사본을 둔다. sha256 `347a1e5b6c27022242cb290dd1af2dcbe294a1131de9e3099bca65390ef078f6` | 멈춘다. 기대 `463da87a…54e9` 와 실제 `347a1e5b…78f6` 를 출력한다. 앞 16 자리만 비교해도 잡힌다 |
| R1-b | K4096 태그 폴더의 `fit_UMi28_Nr32_kronK4096_n160000.npz` 자리에 같은 K 의 재시작 파일 `….k0r0.npz` 의 바이트 복사본을 정상 이름으로 둔다. sha256 `849d4a64e06fc0b58bce7a0b973f5bcdcdf584691604f39bef13ead37c483918` | 멈춘다. **이 파일은 K (4096, covs 헤더 (4096, 128, 128)) 와 ll_val (152.23176788511105) 까지 정상 파일과 같다.** 그래서 `meta["bstar"]` 'kron', `kron_K` 4096, `ll_val\|kron` 검사를 모두 통과하고, sha256 검사만 이 파일을 잡는다. 이 사례에서 측정이 진행되면 결함이다 |
| R1-c | D2 체크포인트 복사본의 한 바이트를 바꾼다 | 멈춘다 |
| R1-d (정상) | 위 표의 정상 파일 7 개 (fits 는 바이트 복사본) | 통과해서 측정한다. 정상 파일을 거부하면 결함이다. 머리말에 7 개의 sha256 이 적힌다 (UMi ckpt 는 전체 64 자리) |

**R2. 출력 파일이 있으면 덮어쓰지 않는다**

| 사례 | 입력 | 기대 |
|---|---|---|
| R2-a | `cost/cost_<tag>.txt` 를 미리 둔다 (내용 임의, 실행 전 sha256 기록). 같은 `--tag` 로 실행한다 | 거부한다. 기존 txt 의 바이트(sha256)가 그대로이고, `cost_<tag>.npz` 는 새로 생기지 않는다 |
| R2-b (경계) | `cost_<tag>.npz` 만 있다 | 거부한다 (태그 출력 둘 중 하나라도 있으면) |
| R2-c | 다른 태그 | 정상 진행한다 (거부 조건은 태그 단위다) |

- 거부 시점: 덮어쓰지 않는 것은 필수다. 측정 전에(시작할 때) 거부하는 것이 명세 취지(측정 낭비 방지)에 맞지만, 시점 자체는 명세에 없다.

**R3. 다른 계산 작업이 보이면 `--force` 없이는 측정하지 않는다**

| 사례 | 입력 | 기대 |
|---|---|---|
| R3-a | **지금 상태 (2026-10-18 22:22–22:40 CDT 확인):** 이 계정(HTJ)에서 cmdline 에 runner 스크립트의 `run` 하위 명령이 있는 프로세스 97 개 (전부 `--tag U28LSQ`; 명세 13 행의 등록 test 로 보인다; CPU 24-47 · 120-143 · 72-95 · 168-191 에 배치), runner 를 담은 다른 프로세스 4 개, 이 계정의 GPU compute 프로세스 3 개 (pid 2432767 · 2945815 · 2945838, 각 596 MiB), load average 97.32. `--force` 없이 실행한다 | 경고(다른 작업 목록 · 부하)를 출력하고 **측정하지 않는다**. 출력 파일도 없다 |
| R3-b | 같은 상태에서 `--force` | 경고를 출력한 뒤 측정한다. 머리말에 경고, 시작 전 `uptime`, `ps -eo pid,pcpu,etime,comm --sort=-pcpu \| head -20` 이 남고, 끝난 뒤의 두 기록도 남는다 |
| R3-c (경계: 자기 자신) | 이 계정의 다른 runner · GPU 작업이 없는 조용한 환경에서 `--force` 없이 실행한다 | 경고 없이 측정한다. bench 자신의 프로세스나 그 부모 셸을 "다른 작업" 으로 세어 거부하면 결함이다 |
| R3-d (명세 14-15 행) | 부하 검사 도중의 프로세스 | bench 가 cmdline 에 `runner.py run` 이라는 글자를 그대로 담은 프로세스(예: 그 문자열을 인자로 준 `pgrep -f`)를 만들지 않는다. 만들면 돌고 있는 등록 test 의 다음 run 이 ABORT 한다. `/proc/*/cmdline` 을 파이썬에서 읽거나, 그 글자가 그대로 드러나지 않는 패턴을 써야 한다 |

---

## G7. 기타 기록값

- **dtype** (명세 34 행: 코드에서 읽어 기록; `g_dtype.py`, `g_fits.py`)
  - 신경망은 실행 시점에 **float64** 다. 근거: `load_model(…, dtype=torch.float64)` 기본값이 `m.to(dtype)` 를 부른다 (score.py:1052-1057). 입력 x 도 float64 다 (1117). 파라미터 · 버퍼 M 모두 float64 이고 device 는 cpu 다.
  - checkpoint 에 **저장된** EMA 가중치는 float32 다. bench 가 state_dict 의 dtype 을 읽어 "float32" 라고 적으면 결함이다.
  - GMM 의 covs · covinv · U 는 **complex128** 이다. ScorePrior.C 도 complex128 이다. 수신기 배열은 numpy complex128 이다.
- **스레드**
  - `torch.set_num_threads(1)` 뒤 `torch.get_num_threads()` 는 **1** 이다 (ScorePrior 도 cpu 일 때 1 로 맞춘다, score.py:1085-1086).
  - **threadpoolctl 은 지금 torch env 에 없다** (2026-10-18 22:2x CDT 에 import 실패를 확인). 그래서 구현자가 pip 로 설치하고 그 사실을 보고해야 한다 (명세 39 행).
  - 설치 뒤 `threadpool_limits(1)` 를 걸면 `threadpool_info()` 의 모든 항목에서 `num_threads` 가 1 이어야 한다.
- **CPU 모델**: `/proc/cpuinfo` 의 model name 은 `Intel(R) Xeon(R) 6740P` 다.
- **라이브러리**: python 3.12.14, numpy 2.5.2, torch 2.14.0+cu130 (2026-10-18 22:2x CDT 기준).
- **git HEAD**
  - worktree 의 HEAD 는 `9dd8b5fe` (e4-cost) 다.
  - bench_cost.py 는 커밋하지 않은 새 파일이므로, runner 의 관례(`git status --porcelain code ../Demo`, untracked 포함, runner.py 의 `_git_head`)로는 **`9dd8b5fe+dirty`** 가 기대값이다. dirty 정의는 "정답 미정" 참고.
- **시행 매핑** (명세 42-43 행; runner.py@9dd8b5fe:643-650 과 같은 순서)
  - SNR 마다 `common.trial_rng(…)` (common.py:228-229) 를 쓴다.
  - 시행 0..2559 를 같은 순서로 만들어 버린다. 순서는 H = `gen.sample`, u = `integers(0, 2, K)`, perm = `permutation(Ns)`, `transmit` 의 잡음이다.
  - 2560 은 워밍업이고, **2561..2584 를 측정**한다 (DEV_SKIP0 = 2560, common.py:51).
  - 블록 지문 = sha256(H‖u‖perm‖Y 의 바이트)[:16] (`g_count.py`):
    - D2 −3 dB: 2560 `b8268dc41df7dbad`, 2561 `ff045bd0054a87ce`, 2584 `5e67bbededffbfce`
    - D2 +6 dB: 2560 `24d901420e78da8c`, 2561 `171d58acfba9f3e2`, 2584 `4b7d4f0aa837bf23`
    - UMi32 −3 dB: 2560 `367eab93a4c834d4`, 2561 `013290eef5334ded`
    - UMi32 +3 dB: 2560 `b5daf2a7fa7454b2`, 2561 `8d30f26f0b65c88b`
- **arm 순서 순환** (기존 bench 98 행)
  - order(i) = ARMS[i mod n:] + ARMS[:i mod n] 이고, i = 0 이 워밍업, 1..24 가 측정 블록이다.
  - 측정 24 블록에서 각 arm 이 맨 앞에 서는 횟수는 24/n 이다. n = 2 면 12, n = 3 (D2 + ms) 이면 8, n = 4 (UMi32) 면 6.
  - 24 는 2 · 3 · 4 로 나누어떨어지므로 시작 위상과 상관없이 이 횟수가 나온다.
  - 예: ARMS = (V1, b\*) 이면 워밍업은 V1, b\* 순, 블록 1 은 b\*, V1 순, 블록 2 는 V1, b\* 순이다.
- **원자료 크기** (`--trials 24`, 예외 0)
  - (셀, SNR, arm) 마다 블록 값 24 개, 호출당 값 24 × 16 = **384** 개다.
  - `--trials 1` 이면 블록 1 개, 호출당 16 개다 (S5).
  - 단일 SNR(`--snr -3`) 이면 표에는 그 SNR 의 행만 있고, 블록당 개수는 같다.
- **arm 구성** (`g_count.py` 출력)
  - V1 · V1-ms: RouteAClip, mode scalar, scal belief, hsite matrix, exact_prior False, n_inner 1, init_colored 0, nu_sw None.
  - b\* · SBL: RouteA, mode colored, scal site, hsite scalar, exact_prior True.

---

## G8. 참고: 개발 시행 블록 결과 (명세 확인 4 "Tap 유무로 blk_err · nmse 동일" 의 외부 대조값)

- 내 구성(`load_prior(ckpt, psd_project=True, ntrain=160000)`, `route_a`)은 build_point 의 해당 arm 과 같은 호출이다.
- 블록 결과는 앞선 블록의 실행 여부와 무관하다 (캐시는 같은 키에 같은 값을 돌려주고, cold SBL 과 GMM view 에는 결과에 영향을 주는 상태가 없다).
- 그래서 bench 의 Tap 유 · 무 실행 모두 아래 값과 같아야 한다.
  - blk_err[-1] 은 정확히 같아야 한다.
  - nmse[-1] 는 보통 비트까지 같다. 허용 상대오차는 1e-9 다.
- 최종 반복(16) 값:

| 셀 | SNR | 시행 | V1 blk_err / nmse | V1-ms blk_err / nmse | b\* (K1024) blk_err / nmse | SBL blk_err / nmse |
|---|---|---|---|---|---|---|
| D2 | −3 | 2560 | 1 / 3.039156e-02 | 1 / 3.006018e-02 | 1 / 8.145810e-02 | – |
| D2 | −3 | 2561 | 0 / 1.134438e-01 | 0 / 1.133158e-01 | 0 / 1.058633e-01 | – |
| D2 | +6 | 2560 | 0 / 6.933133e-03 | 0 / 6.524255e-03 | 0 / 9.710770e-03 | – |
| D2 | +6 | 2561 | 0 / 1.297221e-03 | 0 / 1.297221e-03 | 1 / 4.809749e-02 | – |
| UMi32 | −3 | 2560 | 0 / 4.811239e-02 | – | (안 돌림) | 0 / 9.097121e-02 |
| UMi32 | −3 | 2561 | 1 / 4.575300e-02 | – | (안 돌림) | 1 / 2.381149e-01 |
| UMi32 | +3 | 2560 | 0 / 1.323109e-02 | – | (안 돌림) | 0 / 1.609790e-02 |
| UMi32 | +3 | 2561 | 0 / 1.134636e-02 | – | (안 돌림) | 0 / 2.088104e-02 |

---

## 정답 미정 (사유)

1. **시간 값 자체** (호출당 · 블록 · rx.run 의 median · IQR · p90, H 비중의 수치): 기계와 부하에 따라 달라진다. G5 는 계산 규칙만 정한다.
2. **H 비중의 집계 방식**: 명세는 "H 누적 / rx.run" 이라고만 적었다. 기존 bench 는 블록별 비의 median 을 쓴다. 다른 방식(합의 비, median 의 비)을 쓰면 S4 에서 값이 갈리므로, bench 는 쓴 정의를 머리말에 적어야 한다.
3. **워밍업 블록의 예외를 예외 수에 넣는지**: 명세에 없다. 기존 bench 는 `tr == 0` 을 검사하기 전에 nfail 을 올리므로 워밍업 예외도 센다 (bench_moduleH_ep.py:103-108).
4. **거부할 때의 종료 코드와 메시지 형식**: 명세에 없다. G6 은 "측정 없음 · 파일 불변" 만 정답으로 둔다.
5. **링크된 fits 파일을 거부해야 하는지**: 명세는 "바이트 복사본을 둔다" 고만 적었다. sha256 이 같은 링크를 거부할지는 정하지 않았다. 최소 기대는 bench 가 만든 파일이 링크가 아닌 것이다.
6. **BLAS threadpool 의 종류와 개수**: threadpoolctl 이 설치되어 있지 않아 지금은 볼 수 없다.
7. **"다른 계산 작업" 판정 기준의 세부**: 어느 프로세스를 셀지, 예컨대 CPU 사용률 문턱이나 다른 사용자의 작업을 넣는지. 명세의 예시는 "이 계정의 runner, GPU 학습 등" 이고, R3-a 의 지금 상태는 어느 기준으로도 해당한다.
8. **git dirty 의 정의**: untracked 를 넣는지가 명세에 없다. runner 관례(넣음)로는 `9dd8b5fe+dirty` 다.
9. **UMi32 GMM K4096 · K8192 arm 의 블록 결과 · 예외 수**: 메모리(GMMPriorB 하나에 covs · covinv · U 가 각각 1–2 GB)가 커서 돌리지 않았다. 호출 수(16)와 K 는 코드 구조와 파일 헤더로 정했다.
