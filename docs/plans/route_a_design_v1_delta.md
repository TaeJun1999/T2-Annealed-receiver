# Route (a) 설계 노트 v1-delta — v0 대비 변경분 (2026-09-17, 세션 3)

> 연구 노트(논문 문장 아님). `route_a_design_v0.md`의 §1–§2(원문 복사본)·메시지 표기는 그대로. 아래는 §3의 변경분만. 상태: **정확 / 근사 / 추측 / 측정**. 출처 태그: [복사], [우리], [prior art].

## 1. 변경 목록
| # | v0 | v1 | 결정 | 근거 |
|---|---|---|---|---|
| 1 | $\mathbf G=\bar{\mathbf X}\mathbf D\bar{\mathbf X}^H+\sum_nd_n\mathrm{diag}(\boldsymbol\tau_n)$ | form A: $\mathbf G=\bar{\mathbf X}\mathbf D\bar{\mathbf X}^H$ | D-10 | exp_0918 T3 |
| 2 | L_H→H: site 등방화 $\nu^q=\mathrm{tr}(\mathbf G^{-1})/N$ | **belief 등방화** (아래 §2.1) | D-13 | T5, exp_0919 T2, exp_0920 |
| 3 | H→L: 등방 site $(\hat{\mathbf h}^E,\nu^E)$ | **행렬 site** $(\boldsymbol\Lambda_E,\boldsymbol\eta_E)$ (§2.2); 등방 site는 denoiser 입력 생성에만 | D-14 | T6, exp_0920 |
| 4 | L_H가 decoder extrinsic $(r^D,\tau^D)$ 소비 | L_H는 decoder **a-posteriori** $(\bar x,v)$ 소비, L_X는 extrinsic + LOO 유지 (§2.3) | D-15 (승인 대기) | exp_0919b (ii), exp_0920 |
| 5 | damping 위치만 명시 | $(r^D,\tau^D)$ 모멘트 도메인 $\beta=0.7$; $T_p<N_t$는 반복 $\ge16$ | D-12 | exp_0919 T2, exp_0919b iter16 |
| 6 | Q-04/Q-04′ 미정 | moment-domain extrinsic + 블록 평균 $\alpha^D$ 확정 | — | exp_0919b (iii)(iv) |
| 7 | 초기화·guard 미정 | I-2, I-3, G-1(site 형에만 필요), `p_min`, `lam_min`$=10^{-6}$ | — | exp_0918, exp_0920 |
| 8 | hybrid 초기화(D-11) | ablation 전용 | — | exp_0920: $\hat{\mathbf C}=\mathbf I$이면 D-11 ≡ v0 |

## 2. 새 모듈 식
### 2.1 L_H→H (D-13) [복사 (2)–(3)을 L_H 쪽에 적용; 고정점 성질은 우리]
상태 $(\hat{\mathbf h}^E,\nu^E)$ (초기 $\mathbf 0$, $\mathrm{tr}\hat{\mathbf C}/N$). 매 반복(`n_inner`회):
$$\boldsymbol\Sigma_L=(\mathbf I/\nu^E+\mathbf G)^{-1},\quad \hat{\mathbf h}_L=\boldsymbol\Sigma_L(\hat{\mathbf h}^E/\nu^E+\mathbf b),\quad \alpha_L=\frac{\mathrm{tr}\boldsymbol\Sigma_L}{N\nu^E},\quad \nu^q=\frac{\alpha_L}{1-\alpha_L}\nu^E,\quad \mathbf q=\frac{\hat{\mathbf h}_L-\alpha_L\hat{\mathbf h}^E}{1-\alpha_L};$$
$$(\hat{\mathbf h}^{\rm post},\mathbf J)=\text{denoiser}(\mathbf q,\nu^q),\quad \alpha_H=\mathrm{tr}\mathbf J/N,\quad \hat{\mathbf h}^E\leftarrow\frac{\hat{\mathbf h}^{\rm post}-\alpha_H\mathbf q}{1-\alpha_H},\quad \nu^E\leftarrow\frac{\alpha_H}{1-\alpha_H}\nu^q.$$
**정확(Gaussian prior):** 고정점 평균 $=(\mathbf C^{-1}+\mathbf G)^{-1}\mathbf b$. **근사:** 공분산(등방), 비-Gaussian prior. $\mathbf G$가 특이해도 $\nu^q$ 유계($T_p=2$ 첫 패스 1.0~1.25).

### 2.2 H→L 행렬 site (D-14) [우리; 2차 Tweedie 자체는 prior art — VERIFY]
$$\boldsymbol\Sigma_H=\nu^q\mathbf J,\qquad \boldsymbol\Lambda_E=\big[\boldsymbol\Sigma_H^{-1}-\mathbf I/\nu^q\big]_{\succeq\lambda_{\min}},\qquad \boldsymbol\eta_E=\boldsymbol\Sigma_H^{-1}\hat{\mathbf h}^{\rm post}-\mathbf q/\nu^q,\qquad \mathbf P=\boldsymbol\Lambda_E+\mathbf G,\quad \hat{\mathbf h}=\mathbf P^{-1}(\boldsymbol\eta_E+\mathbf b),$$
LOO: $\mathbf P^{\setminus n}=\mathbf P-\mathbf A_n$, $\hat{\mathbf h}^{\setminus n}=(\mathbf P^{\setminus n})^{-1}(\boldsymbol\eta_E+\mathbf b-\mathbf b_n)$. **정확(Gaussian prior):** $\boldsymbol\Lambda_E=\mathbf C^{-1}$, $\boldsymbol\eta_E=\mathbf 0$ for any $(\mathbf q,\nu^q)$. **측정(GMM):** exact-EP 기준과 동률. **추측:** 학습 score에서의 품질.

### 2.3 L_H의 심볼 입력 (D-15 제안) [우리 유도; 고전 turbo 채널 추정의 APP 관행과 같은 방향 — M]
스칼라 모형에서 tilted $h$-marginal $=\sum_xw(x)\mathcal{CN}(h;\mu_x,s_x)$, $w(x)\propto\pi(x)\,\mathcal{CN}(y;m_hx,\sigma^2+c_h|x|^2)$ [정확]. $w$ = (decoder extrinsic) × (LOO 채널 하의 $y_n$ likelihood) ≈ decoder APP. 따라서 form A site에 넣을 모멘트는 $(\bar x_{jn},v_{jn})$: $\mathbf A_n=d_n(\bar{\mathbf x}_n^*\bar{\mathbf x}_n^{\rm T})\otimes\mathbf I$, $d_n=(\sigma^2+\sum_jv_{jn}\mathbb E|h_{ij}|^2)^{-1}$ [근사: 혼합을 Gaussian 하나로]. L_X는 변함없이 $(r^D,\tau^D)$ + LOO.

## 3. v1 의사코드
```
초기화: r^D=0, τ^D=1, (x̄,v)=(0,1); ĥ^E=0, ν^E=tr(Ĉ)/N; eh2 = prior 2차 모멘트
for t = 1..T_max (T_p<N_t: ≥16):
  [L_H]  sites A_n,b_n ← form A with (x̄,v) [D-15] (또는 (r^D,τ^D) [v0]); G=ΣA_n, b=Σb_n
  [L_H→H] (q,ν^q) ← belief 등방화 (D-13), n_inner회
  [H]    (ĥ_post, J) ← denoiser + autodiff Jacobian (D-09); 등방 extrinsic 갱신; (Λ_E,η_E) ← 행렬 site (D-14, clip)
  [L_X]  열 n마다: LOO cavity (P−A_n) → EP-LMMSE with R_n → extrinsic (r^L,τ^L)
  [D]    super-section BCJR (Lemma 2) → (x̄,v), L_u; α^D=mean(v/τ^L); (r^D,τ^D) ← (2)–(3); damping β=0.7 (모멘트 도메인)
출력: L_u 경판정, ĥ, 궤적 {τ^L(t), ν^q(t)};  보고는 M-1
```

## 4. 학습 없는 testbed 두 개
- **Gaussian Kronecker** ($\rho=0.7$): 결합 버그 격리, D-14 항등식. 여기서 default(D-13+D-14) ≡ mode `colored`.
- **Gaussian mixture** (exp_0920): 16 성분 $\mathbf C_k=\mathbf R_t(\psi_a)^{\rm T}\otimes\mathbf R_r(\psi_b)$, $\mathbf R(\psi)=\mathbf D(\psi)\mathbf R_{\exp}(0.7)\mathbf D(\psi)^H$, $\psi=2\pi(k+\tfrac12)/4$ ⇒ 앙상블 공분산 $=\mathbf I$, 폐형 score/denoiser/Jacobian, exact-EP 기준(`ep_site`)과 oracle(성분 기지) 제공. 학습 score로 가기 전 Module H 설계를 가르는 용도.
