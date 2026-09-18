# T2 세션 핸드오프 #5 — Q-27 종결(R-A 중단, F6 = 정보적 한계) · D-18 H-GMM 채택 · D-19 kill test(exp_0925) 대기 (2026-09-18)

> 연구 노트(논문 문장 아님). 표기·태그는 핸드오프 #4와 동일(bit 0→+1, 1→−1; $L_c=2/\sigma^2$; $\mathbf Y=\mathbf H\mathbf X+\mathbf W$; $\bar x_n, v_n$; **정확/근사/추측/측정**, [V]/[M]). 핸드오프 #4의 §0(실행 분담 D-16, repo 사용법), §1.2(exp_0921 결과), §7(프로토콜)은 그대로 유효 — 여기에는 변경분만 적는다.

## 0. 새 채팅에서 먼저 할 일
1. `git clone --depth 1 https://github.com/TaeJun1999/T2-Annealed-receiver.git` → `docs/logs/*.md`(정본; 세션 5 말 갱신본을 사용자가 올렸는지 확인: decision log 마지막 결정이 **D-19**여야 함), `docs/handoff/`(이 문서), `Demo/`.
2. **프로젝트 지침 확인:** 연구가 더 진행해도 좋지 않을 것 같으면 이유와 함께 중단 제안 / 결과를 억지로 맞추지 않기 / chat이 길어지면 handoff 제안 / **매 턴 끝에 chat 이름 추천**(세션 5에서 두 턴 누락 — 재발 금지).
3. **첫 작업 = D-19 승인 여부 확인 후 exp_0925(kill test) 코드 작성**(§3). Claude는 실험을 돌리지 않는다(D-16): 코드 + Claude Code 프롬프트(첫 줄 `git pull`, 코드 수정 금지, stderr는 `~/t2/logs/*.stderr`로, `--jobs` 미기재, `docs/logs`·`docs/plans` 수정 금지, 커밋 메시지 지정) + 사전 등록 판독 기준.
4. 전수 스쿠핑 sweep **2026-10-01** — 최우선 항목이 바뀜(§4).

## 1. 세션 5에서 확정된 것
### 1.1 결정
- **D-17 철회(기본값 적용, reversible):** R-A(표집 기반 Module H) 중단. v1(replacement bridge)은 exp_0923 기준 미달, v2-J/S(모멘트 정합 guidance)는 one-shot보다 나쁨(exp_0924). 코드 `Demo/t2_ra_sampler.py`는 분석 도구로 유지.
- **D-18(사용자 승인):** Module **H-GMM** = 채널 dataset에 GMM 적합(EM) → 정확 mixture EP site. `RouteA(mode='colored', exact_prior=True, feedback='posterior', beta=0.7)` 경로가 이미 있음(`GMMPrior.ep_site`); 필요한 것은 `GMMPrior.fit`뿐. baseline 겸 대안 Module H.
- **D-19(제안, 승인 대기):** kill test를 M2 학습 **전에** 실행(§3).

### 1.2 결과 요약 (GMM testbed, 4x4, 첫 패스, DFT 파일럿; 표 전문은 `Demo/exp_092{2,3,4}_results.txt`, raw `Demo/exp_092{3,4}_raw/`)
- **exp_0922 [측정, n=2000]:** $T_p=4$ 무손실. $T_p=2$: $P_{\rm map}$ exact .77~.84 vs iso .40~.45; NMSE(D13+D14) exact 대비 +13~19%($T_p=3$: +9~10%); 격차는 SNR과 함께 증가.
- **exp_0923 [측정, n=1000]:** 정확 표집기 `PS-M32` NMSE +2.1~3.5%, KL/N .09~.13(one-shot .36~.38) → 항등식·RB 추정기 작동, $M\ge32$ 필요, RB 단계 Jacobian은 chain 1개로 충분. v1 표집기: NFE 123에서 NMSE 격차 회수 10~29%, NFE 439에서 40~56%(기준 2/3 미달). aniso($\chi\approx3$)에서는 one-shot이 $M=32$ 표집보다 나음.
- **raw 재분석:** one-shot의 손실은 **성분 오식별 시행에 집중**($T_p=2$ 오답군 58%: NMSE +19~22%, 정답군은 ≈exact); KL/N 90·99% 분위 .94/1.38 vs PS .16/.23 → "확신에 찬 오답" 꼬리.
- **exp_0924 [측정, n=1000, exp_0923과 paired]:** `PSinit` ≈ PS(마지막 corrector 무편향). `RA2X`(정확 posterior denoiser) **NFE 5로 PS 도달**(NMSE +4~5%). `RA2J-L12`: $T_p=2$ NMSE **+19~21%**(one-shot +15~17%), KLc/N .40~.55(one-shot .36~.38) — 미달. `RA2S` 더 나쁨. 표본 모멘트 site의 clip 손실은 aniso 고SNR에서 큼(PS KL .084→KLc .50).

### 1.3 유도 (decision log에 식 포함)
- **noise-splitting 항등식 [정확, 폐형식 검증 ≤7e-13]:** $\nu\le1/g_{\max}$, $w_i=e_i+w_i'$, $\mathbf z=\mathbf h+\mathbf e$ ⇒ $\pi(\mathbf h)=\int\pi'(\mathbf z)p(\mathbf h|\mathbf z,\nu)d\mathbf z$, $\pi'\propto p_\nu(\mathbf z)\prod_i\mathcal{CN}(\upsilon_i;\zeta^z_i,1/g_i-\nu)$; $\mathbb E[\mathbf h|\mathbf y]=\mathbb E_{\pi'}[D]$, $\mathrm{Cov}=\mathbb E_{\pi'}[\nu\mathbf J]+\mathrm{Cov}_{\pi'}[D]$, $P(k|\mathbf y)=\mathbb E_{\pi'}[w_k]$. $\mathbf G=g\mathbf I$이면 R-A ≡ D-13+D-14(단일점 특수 경우). prior art: SNIPS(arXiv:2105.14951) [V: 초록].
- **비등방 지표 [정확]:** $\chi=\nu^q\mathrm{tr}\mathbf G/N\ge1$, 등호 ⇔ $\mathbf G\propto\mathbf I$.
- **v2 bridge [Gaussian에서 스텝 무관 정확, 폐형식 ≤5e-14]:** $\mathbf z^{l+1}|\mathbf z^l,\mathbf y\sim\mathcal{CN}(a\mathbf z^l+(1-a)\mathbf m_+,\nu_{l+1}(1-a)\mathbf I+(1-a)^2\mathbf S_+)$; J형 = 매 스텝 D-14 연산(= moment-matching posterior sampling 계열, arXiv:2405.13712 §4.2 [V: 발췌]).
- **F6 재정의 [측정+추론, 정리 아님]:** F6은 one-shot의 결함이 아니라 **"등방 score + 2차(Gaussian) closure"의 정보적 한계** — 한 점의 (평균, Jacobian)으로는 비등방 likelihood 하의 성분 evidence를 복원 못 함.
- 원문 복사: 2204.07122 Alg. 1 [V] (점추정 ALD, $\beta<1$ 조율, 보정된 공분산 없음; likelihood 항 부호는 인쇄 오류로 판단).

### 1.4 우리 것 vs prior art (세션 5 추가분)
- **우리:** F6의 실패 양상(오식별 꼬리) 측정; D-13+D-14 = noise-split 표적의 단일점 근사라는 식별과 $\chi$; "정확 posterior denoiser면 5스텝, Gaussian guidance면 one-shot 이하"라는 사다리 분리; (예정) bilinear turbo 수신기의 H-GMM site.
- **prior art:** SNIPS(노이즈 분할 + SVD 분리 ALD) [V: 초록], MMPS류 Tweedie 공분산 guidance [V: 발췌], score 기반 채널 추정 ALD 2204.07122 [V], **GMM 기반 CME — Koller–Fesl–Turan–Utschick, IEEE TSP 2022, arXiv:2112.12499 [V: 초록]**(감시 그룹), 같은 그룹의 diffusion prior 채널 추정 arXiv:2403.03545 [V: 제목만].

## 2. 기여 목록 재평가 (잠정, 세션 5 말)
① D-15 + LOO — 두 testbed에서 지배적 요인이나 **구조가 T1과 동일**(T2의 독립 기여로는 약함). ② D-13+D-14 묶음 — score prior를 쓸 때만 의미; K2 발동 시 소멸. ③ F6 — 이제 "한계 + 처방 실패의 측정 + 대안(H-GMM)"; 단독 논문감은 아님. ④ regime(8x4, $T_p=2$, eig, 짧은 $T$; 동일 goodput ≈4.8 dB) — **Gaussian prior로 얻은 결과**라 "학습 prior"의 기여가 아님; semi-blind/code-aided 선행과의 구분 VERIFY. ⑤ lemma(M1) — 유효하나 diffusion prior가 빠지면 "annealed/generative" 틀의 필요성이 약해짐.
→ **T2의 원 논지(학습 diffusion 채널 prior + decoder score)는 위험 상태.** 판정은 exp_0925.

## 3. 다음 단계 — exp_0925 kill test (D-19; 정본은 decision log)
- **논리:** 정확 score는 모든 학습 score의 상한 ⇒ "정확 score + D13+D14"가 "유한 표본 적합 GMM + 정확 site"를 못 이기면 score 분기는 network 학습 없이 기각.
- **참 prior:** 연속 각도 혼합을 $K_{\rm true}=32\times32$ 격자 GMM으로 *정의*(`steer_corr(n, 0.7, psi)`의 Kronecker). **U**: 각도 전 범위 균등(앙상블 공분산 $\mathbf I$; 비Gaussian prior에 최대로 유리). **S**: 섹터 ±60°(앙상블 공분산이 정보를 가짐; 현실 쪽).
- **arm**(D-15+LOO, $\beta=0.7$, 16반복): (a) `lmmseC_pf`(표본 공분산), (b) `Hgmm-K{16,32,64}`($N_{\rm train}=10^4$, EM), (c) `Hscore-exact`(참 prior 정확 score + D13+D14), (d) `exactEP-true`(상한), pilot-only, genie. 영역: 4x4 $T=28$ $T_p=2$ + **8x4 $T=16$ $T_p=2$**, n≥640, SNR 3점 이상.
- **기준:** **K1** prior S·headline에서 (d)−(a) < 0.5 dB @BLER 0.1 → T2 현 설계 중단 제안(결과는 T1로 이관, lemma는 note). **K2** (c)가 (b, K=32)를 paired sign test($p<.05$, 3점 중 2점)로 못 이김 → score 분기(M2 score model) 중단; GMM 수신기로의 전환은 Q-33(선행 조사) 후에만. **K3** (c)>(b) → M2 진행. 사전 예상[추측]: K2 발동.
- **필요 코드:** `GMMPrior.fit`(EM; zero-mean 복소 성분, full cov, 초기화 k-means 또는 무작위 책임도, 공분산 하한), 참 prior 생성기(U/S), `ep_site`·`denoise_full`의 성분 1024개 batched 버전(8x4에서 시간), 러너 세트 "K"(`exp_0921_run.py` 구조 재사용, `--Nr`, `--T`), 분석(쌍별 sign test, SNR@0.1).
- 그 외 보류: 8x4·$T=16$ 기준표(A/C 재확인), `RouteA.v1()` preset, route (b) ablation, baseline (ii) — **kill test 판정 전에는 착수하지 않음.**

## 4. 스쿠핑·검증 의무 (10-01 sweep)
- **최우선(Q-33):** GMM prior + turbo/복호 결합/semi-blind의 선행 — `Gaussian mixture model channel estimation turbo receiver`, `GMM prior joint channel estimation decoding`, `GMM semi-blind data-aided Utschick`, `conditionally Gaussian channel prior expectation propagation bilinear`; 2112.12499·2403.03545 본문.
- 유지: 핸드오프 #4 §5 목록 + 세션 5 키워드(scooping log "예정"). [VERIFY] 유지: SNIPS 본문 식 대조, 2405.13712의 참고문헌 22–25, TMPD/ΠGDM [M], 2204.07122의 $L,\alpha_0,\beta,r$ 수치, 정렬 파일럿 출처, Q-10·Q-13, D-06.

## 5. 파일 (정본 = repo, 커밋 06c28ca 이후)
| 위치 | 내용 |
|---|---|
| `Demo/t2_ra_sampler.py` | noise-splitting 표집기 v1/v2, `GMMBatch`, 정확 표집기, RB 모멘트, `site_from_moments`, `PostDenoiser`(X/J/S) |
| `Demo/exp_0922_interface.py`, `exp_0923_ra_firstpass.py`, `exp_0924_ra2_bridge.py` + results/raw | 세션 5 실험 3종 |
| `docs/logs/*.md` | 세션 5 말 갱신본(D-17 철회, D-18, D-19, Q-27·Q-29 닫힘, Q-31~Q-33) — **사용자 업로드 확인** |
| `docs/handoff/T2_session5_handoff_2026-09-18.md` | 이 문서 |
