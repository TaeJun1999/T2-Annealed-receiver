# T2 세션 핸드오프 #4 — D-15 승인 · exp_0921 A/B/C/B-T 완료 · F5 폐형식 · headline 영역(8×4, 짧은 블록) · Q-27 인터페이스 floor (2026-09-18)

> 연구 노트(논문 문장 아님). 표기는 원 핸드오프 그대로(bit 0→+1, 1→−1; $L_c=2/\sigma^2$; $\mathbf Y=\mathbf H\mathbf X+\mathbf W$; soft symbol $\bar x_n, v_n$). 상태 태그: **정확 / 근사 / 추측 / 측정**, 출처 태그 [V]/[M]. 핸드오프 #3의 §1.2(v1 규약)·§1.3(구현)·§7(프로토콜)은 아래에 적힌 변경 외에는 그대로 유효.

## 0. 새 채팅에서 먼저 할 일 (순서대로)
1. **repo를 읽는다(읽기 전용, push 권한 없음):** `git clone --depth 1 https://github.com/TaeJun1999/T2-Annealed-receiver.git` → `docs/logs/{decision_log,open_questions,scooping_log}.md`(정본), `docs/plans/`(설계 노트 3종), `Demo/`(코드·결과·raw npz), `docs/EXPERIMENTS.md`, `CLAUDE.md`(서버 규칙). 프로젝트 파일(`/mnt/project`)의 `__N_` 사본들은 **구본** — repo가 정본.
2. **실행 분담(D-16, 확정):** Python 실험은 Claude가 돌리지 않는다. Claude = 코드 + 출력 사양 + 판독. 사용자가 서버(192코어, 사실상 단독 사용)에서 Claude Code로 실행 → push → Claude가 clone해서 판독. Claude 쪽 허용: `py_compile`, $n\le2$ smoke test(수치 폐기), 폐형식 평가, **repo에 올라온 raw npz의 재분석**. 명령에 `--jobs`를 적지 않는다(기본 = 전체 코어).
3. **Claude는 턴 사이에 백그라운드 작업을 못 한다** — "실험 도는 동안 유도하겠다"는 약속을 하지 말 것. 유도는 그 턴 안에서 한다.
4. 사용자가 새 코드를 받으면: GitHub 웹에서 해당 폴더(`Demo/` 등)에 들어가 Upload(같은 이름 = 덮어쓰기; 새 폴더는 폴더째 드래그) → Claude Code 프롬프트 첫 줄은 항상 `git pull`. 로그 md는 Claude가 전체 파일로 주고 사용자가 `docs/logs/`에 덮어쓴다(Claude Code는 `docs/logs/`, `docs/plans/` 수정 금지).
5. **대기 중인 실행 1건:** `Demo/exp_0922_interface.py`(Q-27 첫 패스 손실 정량화, 수 초). repo에 `Demo/exp_0922_results.txt`가 있으면 판독부터, 없으면 §4의 프롬프트를 사용자에게 다시 준다.
6. 다음 전수 스쿠핑 sweep **2026-10-01**(§5).

## 1. 세션 4에서 확정된 것
### 1.1 결정 (누적에 추가)
- **D-15 승인(사용자, 2026-09-18, reversible):** L_H는 decoder **a-posteriori** $(\bar x,v)$ 소비, L_X는 extrinsic + LOO. posterior 경로는 damping하지 않음(`beta_fb=None`; Q-24 닫힘). **`RouteA` 생성자 기본값은 바꾸지 않음**(회귀 테스트 t0/t6이 의존) → 다음 `t2_route_a.py` 변경 때 `RouteA.v1(...)` preset 추가 예정(미구현).
- **D-16:** 위 §0-2. **v1 기본 구성:** `colored`(Gaussian) / `scalar+belief+matrix, lam_min=1e-6`(일반) + `feedback='posterior'` + `loo=True` + `beta=0.7` + `n_inner=1`, 16 반복.
- 서술 변경(지도교수 확인 목록 확정 항목): "extrinsic coupling"은 **L_X 방향에만** 해당; L_H는 APP 소비.
- 코드: `t2_route_a.py`에 `Xp`(파일럿 override), `beta_fb` kwarg 추가(기본 동작 불변). `exp_0921_run.py`(세트 A/B/C, `--T`, `--Nr`, chunk 재개, 멀티프로세스), `exp_0921_analysis.py`(M-1 + paired sign test + 실패 분류 stuck/cyc2/other + SNR@0.1 + goodput 포락선 + regime check [S]/[R]), `exp_0922_interface.py`.

### 1.2 결과 요약 (QPSK, $(133,171)_8$, $N_t=4$, 16 반복, 시드 20260921+100+SNR; 표 전체는 `Demo/exp_0921_results_{A,B,C}.txt`)
**A — D-15 기준표 (4×4, $\rho=0.7$, $T=28$, n=320) [측정].** `col_ext_b0.7` vs `col_post_b0.7` @16 (ext만 실패 : post만 실패): $T_p=4$ 0/3/6/9 dB 52:1, 35:5, 7:1, 1:0; $T_p=2$ 6/9/12/15 dB 87:11, 70:14, 51:13, 34:6. LOO 제거 시 2:31, 2:15, 1:12(그리고 `stuck` 5~30%로 증가 = 자기 강화의 직접 증거). `beta_fb=0.7`은 해로움(0:7, 5:24, 5:21, 3:12, 2:16). $\beta=0.7$은 손해 없음·세 점에서 유의. D-15가 켜지면 Gaussian testbed에서 D-13의 @16 이득 없음(`v0_post` vs `bel_post` 전 점 $p\ge.47$); D-14는 @8에서 유의(52:24~44:12), @16은 부분적.
**B — regime scan [측정].** 4×4 $\rho=0.7$ $T=28$ n=640, SNR@BLER 0.1 [dB]: $T_p=4$ pilot 4.9 / joint 3.8 / genie 1.4; $T_p=3$ eig pilot 8.2 / joint 4.8; $T_p=2$ eig joint 9.4(DFT 12.9), pilot-only >18. **4×4에서 F5는 floor**($T_p=2$ eig joint .052/.041/.036 @12/15/18 dB). goodput 포락선 이득 0 dB +114%, 3 dB +26%, 6~9 dB ≈+4%, 12~18 dB +1~2% → **4×4 headline 약함.** $\rho=0.9$: genie 자체가 8.8 dB, joint 이득 없음 → 제외. **8×4 $T=28$ n=320:** $T_p=2$ eig joint 2.4 dB vs pilot 9.0 dB, joint floor 없음(.013/.009/.003/.000), pilot-only floor(.10→.06); 포락선 +3~4%.
**B-T — 짧은 블록 (n=640, $\rho=0.7$) [측정].** **8×4 $T=16$:** 포락선 +12%(0 dB), **+6.0~7.2%(3~15 dB)**; $T_p=2$ eig SNR@0.1 joint 2.2 vs pilot 10.8 dB; **동일 goodput 2.85에서 ≈4.8 dB, goodput 3.0은 pilot-only 도달 불가(joint ≈5.3 dB)** ← 현재 headline 표현. 8×4 $T=12$: +6~9%(3~12 dB). 4×4 $T=16$: +3~8%, floor 잔존. 실질 상한 = $K(T_p{=}2)/K(T_p{=}3)$: $T=16$ +8.7%, 측정은 그 70~80%.
**C — GMM testbed (4×4, $T=28$, DFT, n=320) [측정].** D-15는 모든 site 규칙에서 성립(9 dB: 136:6, 106:14, 86:10, 115:7). $T_p=2$ @16 BLER 9/12/15 dB: `v0_pf` .450/.438/.406, `D13_pf` .406/.397/.378, `D14_pf` .456/.428/.406, **`D13+14_pf` .381/.344/.362**, `exactEP_pf` .319/.263/.244, `oracle_pf` .231/.156/.147, `lmmseC_pf` .525/.494/.431, `pilot_gmm` .87/.84/.81, genie 0. 묶음 vs v0: 56:34(.026), 47:17(.0002), 44:30(.13); D-14 단독 = v0; **묶음 vs exactEP: 53:33, 61:35, 73:35(유의하게 뒤짐 → Q-27)**; 2차 모멘트 방법 대비 74:28, 61:13, 52:30. $T_p=4$: 모든 `_pf` 동률.

### 1.3 유도 (세션 4, 모두 decision log에 식 포함)
- **F5 폐형식 [정확, Gaussian; 측정 정합].** 첫 패스 = pilot-only LMMSE. $\sigma^2\to0$: $\boldsymbol\Sigma\to\mathbf S^{\rm T}\otimes\mathbf R_r$, $\mathbf S=\mathbf R_t-\mathbf R_t\mathbf X_p(\mathbf X_p^H\mathbf R_t\mathbf X_p)^{-1}\mathbf X_p^H\mathbf R_t$, $\mathrm{NMSE}_\infty=\mathrm{tr}\,\mathbf S/N_t$, 첫 패스 $\mathbf R_n=\sigma^2\mathbf I+\mathrm{tr}(\mathbf S)\mathbf R_r$ → $\mathrm{SIR}_\infty=(1-\mathrm{NMSE}_\infty)/\mathrm{NMSE}_\infty$ SNR 무관. eig 파일럿($\sqrt{N_t}\mathbf U_{1:T_p}$)이 최소(Ky Fan). $\rho=0.7$: $T_p=2$ DFT .168/6.9 dB → eig .130/8.2 dB; $T_p=3$ .102/9.4 → .051/12.7 dB. 측정 NMSE@1 .208/.188/.167 vs 폐형식 .198/.177/(.168).
- **Q-27 인터페이스 floor [정확 + 코드 검증].** $\mathbf G=g\boldsymbol\Pi$(rank $\kappa N$, $\kappa=T_p/N_t$, $g=N_t/\sigma^2$), 등방 prior-site $(\hat{\mathbf h}^E,\nu^E)$: $\alpha_L=(1-\kappa)+\kappa/(1+g\nu^E)$, $\boxed{\nu^q=\frac{1-\kappa}{\kappa}\nu^E+\frac1{\kappa g}}$, $\mathbf q\to\hat{\mathbf h}^E+\frac1\kappa\boldsymbol\Pi(\mathbf y-\hat{\mathbf h}^E)$. $T_p<N_t$에서 denoiser 입력 노이즈가 SNR 무관 floor($T_p=2$: $\ge\nu^E=1$), 미관측 방향은 자기 추정 되먹임 → 성분 책임도 편향. $T_p=N_t$: 무손실. Gaussian prior: 평균은 여전히 정확. `n_inner`로는 제거 불가. 폐형식 = `RouteA` 로그 4자리 일치(1.1256/1.0315/1.0079; .4171/.3544/.3386).

### 1.4 실패 모드 (누적 변경분)
- **F5 개정:** 4×4에서는 floor(위), **$N_r>N_t$(8×4)에서는 소멸.** 원인 = 첫 패스 Schur 잔차(폐형식). 완화 = eig 파일럿, $N_r\uparrow$.
- **F6 (신규):** one-shot 등방 denoiser 인터페이스의 $\nu^q$ floor(§1.3) — 비Gaussian prior·$T_p<N_t$에서 exact-EP 대비 손실. 처방 후보 R-A(§4).
- 관찰[추측]: $T_p=2$ 실패는 궤적 민감(같은 BLER에서 불일치 쌍 다수, genie BLER 0) → 시동 basin 문제.

### 1.5 우리 것 vs prior art (세션 4 추가분)
- **우리:** F5의 Schur 잔차 설명과 regime 선택; D-15+LOO가 지배적 요인이라는 측정; "$T_p<N_t$는 joint에서만 성립"(8×4); 인터페이스 floor의 정량화와 성분 편향 기작.
- **prior art:** 상관 채널의 고유방향 정렬 훈련 신호 최적성 [M, 출처 미확인 — VERIFY]; VAMP류 스칼라 인터페이스의 대형·회전불변 가정 [M]; score 기반 MIMO 채널 추정의 posterior sampling [M — 프로젝트 PDF 2204.07122 확인 필요, VERIFY]; 2차 Tweedie [M, VERIFY 유지].

## 2. 열린 질문 상태 (정본: `docs/logs/open_questions.md`)
닫힘: Q-24, Q-25(a)(b). 열림·높음: **Q-27**(R-A 설계), **Q-28**(headline: 남은 것 = 8×4·$T=16$에서 A/C 재확인, $\rho=0.5$ 민감도, eig 파일럿 전력 불균등 ablation), Q-20(a)(시동 임계의 $\mathrm{SIR}_\infty$ 표현), Q-25(c)(학습 score에서 D-14 필요 범위). 낮음: Q-26(SNR 간 common random numbers).

## 3. 마일스톤·기여 목록 (원 핸드오프 §6.1, §5 기준)
- M1 ✔. **M3:** D-15 기준표 ✔, $8\times4$ ✔, regime scan ✔(headline 영역 = 8×4, $T_p=2$, eig, 짧은 $T$). 남은 것: route (b) ablation, baseline (ii) BiG-AMP형, 8×4·$T=16$ 기준표. **M2(채널 score 모델): 미착수** — Q-27이 M2의 인터페이스 사양을 좌우(one-shot Tweedie로 충분한가 vs posterior sampling).
- **기여 목록(잠정 재평가):** ① D-15 + LOO(두 testbed 모두 지배적) ② D-13+D-14 묶음(비Gaussian·$T_p<N_t$에서 유의; Gaussian에서는 수렴 속도) ③ 등방 인터페이스의 한계 정량화(F6) (+R-A가 되면 처방) ④ regime: $N_r>N_t$, $T_p<N_t$, 정렬 파일럿 — headline은 "동일 goodput SNR 이득(≈4.8 dB) + pilot-only 도달 불가 goodput". 감시 그룹 신규 게시물은 미확인(sweep 10-01).

## 4. 다음 단계
1. **exp_0922 실행·판독**(대기 중). Claude Code 프롬프트:
```
git pull 후 Demo/에서 (코드 수정 금지, CPU 전용):
~/miniforge3/envs/torch/bin/python exp_0922_interface.py 2>/dev/null | tee exp_0922_results.txt
docs/EXPERIMENTS.md에 한 행 추가(seed 20260922, 결과 파일 경로만). exp_0922_results.txt + EXPERIMENTS.md 커밋 & push.
커밋 메시지: "exp_0922: Q-27 isotropic-interface loss at first pass (GMM, n=2000)". 끝나면 결과 표를 그대로 보고.
```
   판독 기준: $T_p=4$에서 모든 열 일치(무손실) / $T_p<4$에서 P_map(iso) ≪ P_map(exact), NMSE(D13+D14) > NMSE(exact). 격차가 작으면 R-A 보류.
2. **R-A 설계(유도 먼저):** 비등방 Gaussian likelihood $(\mathbf G,\mathbf b)$ + 등방 prior score로 annealed posterior sampling → 표본 모멘트 $(\mathbf m,\mathrm{Cov})$ → D-14 형 site $\boldsymbol\Lambda=\mathrm{Cov}^{-1}-\mathbf G$. GMM testbed에서 exact-EP와 대조(정확 score 사용), 스텝 수·warm start 비용 평가. 2204.07122 원문에서 알고리즘 복사 후 번역(기억으로 재구성 금지).
3. **8×4·$T=16$ 기준표:** 세트 A/C를 `--Nr 8 --T 16`로(현재 `grid_A/C`는 Nr=4 고정 → 러너 수정 필요).
4. `RouteA.v1()` preset, route (b) ablation, baseline (ii).

## 5. 스쿠핑·검증 의무
- 전수 sweep **2026-10-01**: scooping log 키워드 + 세션 3 추가분 + 세션 4 추가분(`pilot contamination-free semi-blind fewer pilots than transmit antennas turbo`, `score-based posterior sampling channel estimation turbo decoding`, `isotropic denoiser interface VAMP rank-deficient`, `eigen-aligned pilots correlated MIMO joint estimation decoding`). 감시 그룹 동일(Wadayama–Takahashi, Segarra/Zilberstein, Schniter, Nachmani·Choukroun–Wolf, Utschick).
- [VERIFY] 유지·추가: Q-10·Q-13, D-06, D-14·D-15 prior art 2건, 정렬 파일럿 출처, 2204.07122의 posterior sampling.

## 6. 파일 (정본 = repo, 커밋 e21e108 이후)
| 위치 | 내용 |
|---|---|
| `Demo/t2_route_a.py`, `t2_trellis.py` | 수신기(세션 4 패치: `Xp`, `beta_fb`) |
| `Demo/exp_0921_run.py`, `exp_0921_analysis.py` | 세트 A/B/C, `--T/--Nr/--rho/--tp/--snr/--n` |
| `Demo/exp_0921_results_{A,B,C}.txt`, `Demo/exp_0921_raw/*.npz`(2,772개) | 결과·raw(파일명 `_T<T>` 태그는 $T\ne28$) |
| `Demo/exp_0922_interface.py` | Q-27 첫 패스 점검(**사용자가 업로드했는지 확인**) |
| `Demo/exp_0919_*.py`, `exp_0920_gmm.py` | 세션 3 스크립트(경로 이식본); `exp_0919_analysis.py`는 소실 |
| `docs/logs/*.md`, `docs/plans/*.md` | 로그 3종(세션 4 말 갱신본을 사용자가 업로드했는지 확인), 설계 노트 3종 |
| `docs/EXPERIMENTS.md` | 실행 기록(Claude Code가 관리) |

## 7. 대화 프로토콜 (추가분)
- 한 턴에 질문 하나 + 기본값. 코드 전달 시: 파일 카드 + "어느 폴더에 덮어쓸지" + Claude Code 프롬프트(첫 줄 `git pull`, "코드 수정 금지", "에러 시 traceback만 보고", 커밋 메시지, `docs/logs/`·`docs/plans/` 수정 금지).
- 결과 판독 시 과대 해석 주의: 세션 4에서 n=160/320 결과로 "floor 아님", "+3~6%"라고 했다가 n=640에서 정정함 → **결정 점은 n≥640 후에 서술.**
