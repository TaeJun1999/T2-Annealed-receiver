# `Demo/archive/` — repo 이전(pre-repo) 실험 산출물 (2026-09-15 ~ 09-20)

> 이 폴더는 **읽기 전용 증거 보관소**다. repo가 생기기 전에 Claude 세션 컨테이너(`/home/claude/t2`)에서 실행된
> 실험의 스크립트와 stdout이며, decision log가 근거로 인용하는 수치가 여기에 있다.
> 여기 있는 스크립트는 **더 이상 유지보수하지 않는다.** 경로가 `/home/claude/t2`로 하드코딩되어 있으므로
> 그대로 실행되지 않는다. 현행 코드는 `Demo/`의 `t2_trellis.py`, `t2_route_a.py`, `exp_0919_*.py`, `t2_gmm.py`다.

## 왜 보관하는가

decision log(`docs/logs/decision_log.md`)가 이 실험들을 근거로 인용하는 횟수:
`exp_0915` 13회, `exp_0916` 8회, `exp_0917` 8회, `exp_0918` 25회, `exp_0918b` 9회,
`exp_0919` 34회, `exp_0920` 20회. 이 파일들을 잃으면 D-01~D-14 계열 결정의 원 출력이 사라진다.

## 목록

| 파일 | 내용 | 비고 |
|---|---|---|
| `exp_0915_bcjr_score_check.py` / `_results.txt` | M1 "BCJR = score" 확인. 종단 rate-1/2 convolutional code, 전체 $2^K$ codeword brute force. T1: $\tanh(L_k/2)=\mathbb E[x_k\mid\tilde x]$ (BPSK, $L_c=2/\sigma^2$). T2: Tweedie $\nabla\log p_t(\tilde x)=(\mathbb E[x\mid\tilde x]-\tilde x)/\sigma^2$ (유한차분). T3: Jacobian = 조건부 공분산/$\sigma^2$ | Lemma 1의 수치 검증 |
| `exp_0916_superbcjr_133171_qam.py` / `_results.txt` | 심볼 수준 BCJR 모듈 검증, $(133,171)_8$, $\nu=6$, 복소 잡음 $\mathcal{CN}(0,\tau)$ (D-01 규약). S1 심볼 posterior/soft symbol/비트 marginal vs brute force, S2 복소 Tweedie, S3 Wirtinger Jacobian | super-section trellis |
| `exp_0917_onsager_small_N.py` / `_results.txt` | Q-05. Gaussian Kronecker 채널 prior $\mathbf C=\mathbf R_r\otimes\mathbf R_t$의 폐형식 score와 정확 $\alpha=\frac1N\mathrm{tr}(\mathbf C(\mathbf C+\nu\mathbf I)^{-1})$, 소규모 $N$ | autodiff Jacobian trace 결정(D-09)의 근거 |
| `exp_0918_route_a_gaussian.py` / `_results.txt` | route (a) v0 + Gaussian Kronecker prior. seed 20260918, $4\times4$, $T=28$, $T_p\in\{2,4\}$, BPSK, $(133,171)_8$, 심볼 인터리버, DFT 파일럿. T0 회귀, T1 $\rho=0$ sanity, T2 $\rho=0.7$ 본 실행(scalar/colored/pilot_only/genie, 반복별 NMSE·$\tau^L$·$\nu^q$·$\alpha$·BER·BLER) | F1/F3 발견 지점 |
| `exp_0918b_f1_isolation.py` / `_results.txt` | F1/F3 원인 분리. T4a 후기 NMSE 점프 per-trial 조사, T4b colored-init, T4c damping $\beta$·clip $\varepsilon$ | |
| `exp_0919_results.txt` | `exp_0919_tests.py`(T0/T1/T5/T6/T7)의 출력. 벡터화 `SymbolTrellis.bcjr` vs brute force/loop, 속도 비교 포함 | 스크립트는 `Demo/exp_0919_tests.py` |
| `exp_0919b_0920_results.txt` | ablation (ii)~(iv) 및 GMM testbed 출력 (QPSK, $\rho=0.7$, 8 iter, $n=160$) | 스크립트는 `Demo/exp_0919_run.py`, `Demo/exp_0920_gmm.py` |

## 재현

`exp_0919*`, `exp_0920*` 결과는 `Demo/`의 현행 스크립트로 재현된다 — 아카이브 시점의 프로젝트 사본과 repo 판본의
차이는 **출력 경로뿐**임을 diff로 확인했다(`/home/claude/t2/...` → `./...`). seed와 수치 논리는 동일하다.

`exp_0915`~`exp_0918b`는 현행 `Demo/` 코드로 재현되지 않는다. 당시 모듈 구조가 이후 리팩터링으로 바뀌었기 때문이며,
재현이 필요하면 이 폴더의 스크립트를 경로만 고쳐 별도 환경에서 실행한다.
