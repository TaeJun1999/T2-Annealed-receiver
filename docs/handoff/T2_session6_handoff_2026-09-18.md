# T2 세션 핸드오프 #6 — D-19 승인(+보정 R1~R7) · exp_0925 코드·실행 완료 · **판독 미실시**(세션 7 첫 작업) (2026-09-18)

> 연구 노트(논문 문장 아님). 표기·태그는 핸드오프 #4/#5와 동일(bit 0→+1, 1→−1; $L_c=2/\sigma^2$; $\mathbf Y=\mathbf H\mathbf X+\mathbf W$; $\bar x_n, v_n$; **정확/근사/추측/측정**, [V]/[M]). 핸드오프 #4의 §0(D-16 실행 분담, repo 사용법), §7(프로토콜)과 핸드오프 #5의 §1(세션 5 결과), §2(기여 목록)는 그대로 유효 — 여기에는 변경분만 적는다.

## 0. 새 채팅에서 먼저 할 일
1. `git clone --depth 1 https://github.com/TaeJun1999/T2-Annealed-receiver.git` (**커밋 `b8afa9f` 이후**) → `docs/logs/*.md`(정본; decision log 마지막 결정이 **D-19 승인 + R1~R7**이어야 함. 아니면 사용자가 세션 6 갱신본을 아직 안 올린 것), `docs/handoff/`(이 문서), `Demo/`.
2. **첫 작업 = `Demo/exp_0925_results.txt` 판독**(§2). 이번 세션에서는 **한 줄도 읽지 않았다.** 사전 등록 기준(D-19 + R1~R7)은 decision log가 정본이고, `exp_0925_analysis.py` §5가 기계적 판정을 이미 출력해 두었다 — 그 출력은 **보조 자료**이고 판독은 사람이 한다.
3. **판독 순서(중요).** ① §1 fit 표 → (b) arm이 허수아비가 아닌지 먼저 확인. `b*`가 무엇인지, KL(true‖fit)가 Gaussian 표본 공분산 prior 대비 얼마나 줄었는지. **줄지 않았으면 (b)가 약한 것이고, K3가 나와도 신뢰할 수 없다**(Q-35). ② §5의 K1(결정 셀 = H, prior S) → ③ §5의 K2(literal / b\* / mp-clip 세 줄이 일치하는지) → ④ §3의 SNR@0.1과 bootstrap CI → ⑤ §4 교차-$T_p$ goodput(R1b 범위-한정 분기) → ⑥ §2의 clip 통계와 `-mp` 쌍(Q-34).
4. **과대 해석 금지**(핸드오프 #4 §7): 결정 점은 $n\ge640$ 후에 서술. 이번 실행은 $n=640$/점이다. 검정력 미달이면 §5가 "UNDECIDED"를 출력하며, 그때는 판정하지 말고 $n$ 증량 또는 SNR 격자 확장을 제안한다.
5. 전수 스쿠핑 sweep **2026-10-01** — 최우선은 여전히 Q-33(핸드오프 #5 §4) + 세션 6 추가분(§4).
6. 매 턴 끝에 chat 이름 추천(세션 5에서 두 턴 누락 — 재발 금지).

## 1. 세션 6에서 확정된 것

### 1.1 결정
- **D-19 승인**(사용자 "Continue" = 제시한 기본값 채택, 세션 3 관례와 동일; reversible). 본문은 D-19 원문 그대로, 아래 보정 추가. **모든 보정은 BLER을 한 번도 보기 전에 확정**(사전 등록).
- **R1 (prior 정의).** D-19의 "섹터 ±60°"가 모호했다 [정확]. → prior 3종: **U**(전 범위 균등, 앙상블 $=\mathbf I$), **S**(전기각 $\pm\pi/3$ = D-19 원문, **K1 결정 셀**), **P**(물리 120° 섹터, 맥락용). 참 prior는 셋 다 $K_{\rm true}=32\times32$ 격자 혼합으로 *정의*.
- **R1b (범위 한정 분기 — 원문보다 관대).** K1이 (H, S)에서 발동해도, prior P의 교차-$T_p$ goodput 포락선 이득이 연속 3점 이상에서 ≥5%면 "중단"이 아니라 **주장 범위 한정**.
- **R2 (H4 셀).** 8×4·$T=16$·$T_p=4$ 추가. headline을 교차-$T_p$ goodput으로도 읽는다.
- **R3 (arm (b) 강화 — 우리 논지에 불리).** MAP shrinkage $\kappa$ + 검증 우도 early stopping + Kronecker 구조 성분. 선택은 **검증 우도만**(BLER 미사용). **b\*** = 검증 우도 최대 Hgmm arm. **K3는 (c)가 `Hgmm-K32`와 `b*`를 둘 다 이겨야 성립.**
- **R4 (clip 규칙).** 진단 arm `-mp` 병행. `-mp` 쌍의 판정이 다르면 **미결**.
- **R5 (K1 불확실성).** SNR 이득의 90% paired bootstrap CI가 0.5 dB를 걸치면 미결 → $n$ 증량.
- **R6·R7 (검정력 하한).** K2는 결정 점 3개가 격자 위에 존재하고 그중 2개 이상에서 불일치 쌍 ≥6일 때만 발동. 미달이면 미결. (스모크에서 "증거 0:0인데 K2 발동"이 나와 추가.)

### 1.2 유도 (식은 decision log에 있음)
- **[정확, 폐형식]** 격자 prior의 앙상블 공분산 $\hat{\mathbf C}=\mathbf R_{t,\rm ens}^{\rm T}\otimes\mathbf R_{r,\rm ens}$. U: $\mathbf I$(오차 $\le5\times10^{-16}$). S(전기각): 유효 rank 6.7/16(4×4), 12.6/32(8×4). P(물리): 유효 rank 31.6/32 — **거의 백색이라 D-19의 "앙상블 공분산이 정보를 가짐"이 성립하지 않는다.**
- **[정확]** $T_p=2$ 첫 패스 $\mathrm{NMSE}_\infty$: U·P(DFT) **0.500**(= $1-T_p/N_t$), S(DFT) 0.233 → **eig 0.173**. ⇒ U·P에서 같은 $T_p$의 (d)−(a) 비교는 공허 → R2. 파일럿 규칙: S만 eig, U·P는 DFT.
- **[정확]** **EP site clip의 평균 보존이 KL 최적.** 정밀도 $\mathbf P=\boldsymbol\Lambda_c+\mathbf G$ 고정 시 $\mathrm{KL}$ 최소는 $\boldsymbol\mu=\mathbf m$ ⇒ $\boldsymbol\eta=(\boldsymbol\Lambda_c+\mathbf G)\mathbf m-\mathbf b$. 현 코드는 전부 $\boldsymbol\eta$ 보존. 무작위 $(\mathbf G,\mathbf b)$에서 상대 평균 이동 4~9% [측정, 코드 점검]; **수신기 영향은 미측정** → Q-34. 주의: Q-31의 KL→KLc 손실은 $\boldsymbol\eta$ 보존 하의 값이다.
- **[측정, 적합 단계 한정]** full-covariance EM 과적합: prior S·8×4·$n_{\rm train}=10^4$·plain EM에서 $K=64$ train−val 격차 8.0 nat / KL 4.2, $K=16$ 1.45, Gaussian 9.72 → R3. EM 구현 항등식 검증: $\sum_k\pi_k\mathbf C_k$ = 표본 공분산($\le10^{-12}$), Kronecker M-step의 MLE 성질, $\kappa\to\infty\Rightarrow\mathbf C_k\to\hat{\mathbf C}$.

### 1.3 코드 (모두 repo `Demo/`, 커밋 `b8afa9f`)
- **신규** `t2_gmm.py`(`GMMPriorB` = 1024성분 배치 `ep_site`/`denoise_full`, `RouteAClip` = clip 규칙·통계, `fit_gmm_em` = full/kron·$\kappa$·early stopping, U/S/P 생성기), `exp_0925_run.py`(`prior`/`fit`/`time`/`K`), `exp_0925_analysis.py`, `exp_0925_tests.py`.
- **`t2_route_a.py`·`t2_trellis.py`는 건드리지 않았다**(회귀 테스트 t0/t6 보호). `RouteAClip(clip='eta')` ≡ `RouteA`(로그 차이 0.0, 단위 테스트 T6).
- 단위 테스트 **전 항목 PASS**(서버 실행 5초, `Demo/exp_0925_tests.txt`).

### 1.4 실행 (사용자, 서버 192코어, 커밋 `b8afa9f`)
| 단계 | 소요 | 산출물 |
|---|---|---|
| `exp_0925_tests.py` | 5초 | ALL PASS |
| `exp_0925_run.py prior` | 0초 | `exp_0925_prior.txt` |
| `exp_0925_run.py fit` | 3분 25초 | `exp_0925_fits/*.npz` 36개 (8.0 MB) |
| `exp_0925_run.py K` | 19분 8초 | `exp_0925_raw/*.npz` 816개 (120 MB), 51점 × $n$=640 |
| `exp_0925_analysis.py` | 9초 | **`exp_0925_results.txt` (328 KB) — 미판독** |
stderr 전부 0바이트, rc=0. `docs/EXPERIMENTS.md`에 2행 추가(Claude Code).

## 2. 다음 단계 — exp_0925 판독 (세션 7 첫 작업)
- 판독 순서는 §0-3. 사전 등록 기준은 decision log(D-19 + R1~R7)가 정본이며 **판독 중에 기준을 바꾸지 않는다.**
- **K1 발동 시:** T2 현 설계 중단 제안(결과는 T1로 이관, lemma는 note). 단 R1b 확인 후.
- **K2 발동 시[사전 예상: 추측]:** score 분기(M2) 중단. GMM 수신기로의 전환은 **Q-33 선행 조사(10-01 sweep) 후에만** 결정 — 그 전에는 전환 작업 착수 금지.
- **K3 시:** M2 진행. 단 §1의 fit 표에서 (b)가 강했는지 먼저 확인(Q-35).
- **미결 시:** $n$ 증량(같은 명령 `--n 1280`이면 기존 chunk는 건너뛰고 이어붙는다) 또는 SNR 격자 확장. 판정하지 않는다.
- 판독 후: 기여 목록 재평가(핸드오프 #5 §2), Q-34(clip)·Q-35(적합 강도) 갱신, 세션 7 핸드오프.
- 그 외 보류(판정 전 착수 금지): 8×4·$T=16$ A/C 재확인, `RouteA.v1()` preset, route (b) ablation, baseline (ii).

## 3. 우리 것 vs prior art (세션 6 추가분)
- **우리:** prior 각도 규약 모호성의 식별과 세 prior 설계; $T_p=2$·$\mathbf R_{t,\rm ens}=\mathbf I$에서 (d)−(a)가 공허해진다는 지적과 교차-$T_p$ 대안; site clip 평균 보존의 KL 최적성; kill test 설계 전체(검정력 하한 포함).
- **prior art [VERIFY, 10-01]:** 구조화 공분산 GMM 채널 추정(arXiv:2205.03634, Utschick 그룹 [V: 제목만]) — 우리는 baseline 강화로만 사용하나 GMM arm 서술에 인용 필요. EP의 site 정밀도 PSD 사영/평균 보존 관행 [M] — 표준이면 우리 것으로 주장하지 않고 관행으로 인용.

## 4. 스쿠핑 (10-01 sweep)
핸드오프 #5 §4 그대로 + 세션 6 추가 키워드: `Kronecker structured Gaussian mixture channel prior`, `matrix normal mixture channel estimation`, `expectation propagation site precision positive definite projection`, `moment matching mean preserving damping EP`. 원문 확인 추가: 2205.03634.

## 5. 파일 (정본 = repo, 커밋 `b8afa9f`)
| 위치 | 내용 |
|---|---|
| `Demo/t2_gmm.py` | H-GMM 모듈(배치 mixture EP site, EM, U/S/P prior, `RouteAClip`) |
| `Demo/exp_0925_{run,analysis,tests}.py` | 러너·판독·단위 테스트 |
| `Demo/exp_0925_results.txt`, `exp_0925_{tests,prior,fit,K}.txt` | **판독 대상** |
| `Demo/exp_0925_raw/*.npz`(816), `exp_0925_fits/*.npz`(36) | raw·적합 |
| `docs/logs/*.md` | 세션 6 말 갱신본(D-19 승인+R1~R7, Q-34~Q-36) — **사용자 업로드 확인** |
| `docs/handoff/` | #4는 repo에 있음. **#5와 이 문서(#6)는 사용자가 업로드해야 함** |
