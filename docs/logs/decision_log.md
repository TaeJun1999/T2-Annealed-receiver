# T2 Decision Log

> 형식: `[날짜] D-번호 결정 / 이유 / 대안 / 근거`. 되돌릴 수 있는 결정은 "(reversible)" 표시. 표기: 기술 용어 영어, 수식 LaTeX. 상태: 정확 / 근사 / 추측.

---

## [2026-09-15] D-01 — 분산 규약: 복소 per-entry로 통일, Tweedie는 Wirtinger 형

**결정.**
1. 복소 확률변수에 붙는 모든 분산 기호($\sigma^2$, $\sigma_t^2$, $v_n$, $\tau$, $\mathbf C^{\setminus n}$)는 **per complex entry**: $w\sim\mathcal{CN}(0,\sigma^2)\Leftrightarrow\mathbb E|w|^2=\sigma^2$, real/imag 각각 $\sigma^2/2$. (MIMO 모델 $\mathbf W\sim\mathcal{CN}(0,\sigma^2\mathbf I)$, Sionna `no`, 3GPP $N_0$와 일치.)
2. 복소 Tweedie: $\mathbb E[\mathbf x\mid\tilde{\mathbf x}_t]=\tilde{\mathbf x}_t+\sigma_t^2\,\nabla_{\tilde{\mathbf x}_t^*}\log p_t(\tilde{\mathbf x}_t)$, $\nabla_{\mathbf z^*}=\tfrac12(\nabla_{\mathbf z_{\rm r}}+j\nabla_{\mathbf z_{\rm i}})$. 앞에 계수 2 없음. 실수 stacking 등가형: 실수 차원당 분산 $\sigma_t^2/2$, $\hat{\mathbf x}_{\mathbb R}=\tilde{\mathbf x}_{\mathbb R}+\tfrac{\sigma_t^2}{2}\nabla\log p_t$.
3. Onsager divergence는 $\partial\hat x_n/\partial r_n$ (not $\partial/\partial r_n^*$) $=v_n/\tau$. 따라서 variance-ratio $\alpha=v_{\rm post}/v_{\rm in}$는 실수·복소 표현 모두에서 정규화 divergence와 같다 (정확 MMSE denoiser일 때).
4. 채널 신뢰도 규칙: $L_c=2/(\text{constellation 축 방향 실수 노이즈 분산})$. 실수 모델: $L_c=2/\sigma^2$ (핸드오프 표기 그대로). 복소 embedding(per-entry $\sigma^2$): BPSK는 $\mathrm{Re}\{\tilde x\}$에 $L_c=4/\sigma^2$. 두 값 모두 $4E_s/N_0$ ($N_0$ per complex entry). 코드: Sionna `no`에 대해 `Lc = 4/no`.
5. Lemma는 실수 모델로 진술($L_c(t)=2/\sigma_t^2$ 문자 그대로), 복소 corollary($L_c(t)=4/\sigma_t^2$)를 붙인다. 복소 수신기에서 lemma 호출 시 $\sigma_t^2\leftarrow\tau_t/2$.
6. 포트폴리오 conventions file(README §3.5)의 한 줄을 다음으로 수정 제안: "$L_c=2/\sigma^2$ (real) $=4/\sigma^2$ (complex per-entry) $=4E_s/N_0$".

**이유.** 핸드오프 §2는 $\mathbf W\sim\mathcal{CN}(0,\sigma^2)$(복소 per-entry)와 $L_c=2/\sigma^2$(실수 관례)를 같은 기호로 쓰고 있어 BPSK-on-complex에서 factor 2 충돌. 실험 exp_0915 T4: $L_c=4/\sigma_c^2$이면 brute force와 $10^{-15}$ 일치, $L_c=2/\sigma_c^2$이면 $\sigma_c^2=3$에서 최대 오차 $0.495$.
**대안.** 실수 차원당 통일(기각: MIMO 모델·Sionna·VAMP 메시지 분산과 충돌).
**근거.** exp_0915 (T4, cplx Tweedie 오차 $\le 2\times10^{-9}$, 유한차분 정밀도).

---

## [2026-09-15] D-02 — arXiv:2604.19061 판정: 시나리오 1 ("proceed as planned")

**세 답(원문 근거).**
- (i) 채널: **알려진** linear mixing $\mathbf H\in\mathbb R^{M\times N}$ (i.i.d. $\mathcal N(0,1/M)$; 실험은 $32\times32$ block-diagonal) + **알려진** component-wise nonlinearity $f=\tanh$. Eq. (1)–(2) §II-B; Module C가 $\mathbf H^\top\mathbf H$를 직접 사용 (eqs. (16)–(17) §III-C1); §IV-B Fig. 4 caption. 채널 추정·파일럿·bilinear 언급 없음 (원문 없음).
- (ii) 학습된 채널 prior: **없음**. Prior module(B)은 LDPC code constraint $p_X$ (§III-C3). "learned score"는 likelihood module A에서 $f$가 unknown일 때의 가능성으로만 언급(§III-C2 끝, §V future work) — 구현 없음.
- (iii) Denoiser: **LDPC BP만** (§III-C3, eqs. (23)–(24); Kaira BP, 20 inner iter). BCJR/trellis/convolutional 없음 (원문 없음). 원문 스스로 "BP 출력 ≠ true MMSE $\mathbb E[\mathbf x\mid\mathbf r_x^{\rm in}]$", variance-ratio $\alpha^B$는 surrogate라고 명시(§III-C3).

**잔여 novelty.** (i)+(ii)+(iii)+(iv) 유지. 단 (ii)의 문장을 수정: "$t\leftrightarrow L_c$ 대응" 자체는 원문 §III-C3의 $L_i^{\rm in}=2r_{x,i}^{\rm in}/v_x^{\rm in}$과 고전 turbo에 이미 있음. 우리 것은 (a) trellis에서 decoder 출력이 **정확한** Tweedie denoiser이자 code prior의 score라는 lemma, (b) Onsager 항이 posterior variance로 **정확**(원문은 BP surrogate), (c) diffusion 시간축=$L_c$ 축의 annealing 해석과 message-variance 유도 스케줄.

**차별화 문장(확정).** "2604.19061은 known $\mathbf H$·known $f$·BPSK·LDPC-BP denoiser이며 채널 추정, 파일럿, 학습된 prior, trellis 정확성 중 어느 것도 다루지 않는다."
**추가 관찰.** 원문 §I·§III-C3은 "LLR subtraction은 heuristic"이라 주장하고 Fig. 3에서 moment-domain extrinsic이 LLR-domain보다 좋음(LDPC BP). 정확 BCJR에서는 LLR subtraction이 exact cavity marginal이므로 이 주장은 정확 decoder에는 적용되지 않음 → Q-04.
**스쿠핑 위험.** 여전히 높음: §III-A "general Markov chain $X_1\to\cdots\to X_L$" 일반성 + [11]의 data-driven score learning → 채널 module 추가는 그들에게 한 걸음. 단 bilinear(unknown $\mathbf H$)는 단일 latent Markov chain이 아니므로 BiG-AMP/BAd-VAMP형 coupling이 별도로 필요(Q-08). §V future work: SE, clipping/1-bit, unknown $f$ score learning — 채널 추정 없음.

---

## [2026-09-15] D-03 — Lemma v0 범위 (reversible)

- 포함: terminated convolutional code, BPSK ($0\mapsto+1$), 등방 실수 Gaussian $\sigma_t^2$, 정확 Log-MAP BCJR, uniform codeword prior (a priori $L_a$가 있으면 tilted prior에 대해 여전히 정확), puncturing은 erasure($L_{\rm ch}=0$)로 처리 시 정확(exp_0915 T6), bit interleaver(BPSK)는 permutation이라 무해.
- 제외: tail-biting(circular BCJR은 근사; 정확하려면 $2^\nu$회 pass), Max-Log-MAP(exp_0915 T5: 오차 최대 0.78), turbo/LDPC(근사, M6에서 EXIT로 특성화).
- QAM: symbol-level super-section trellis면 정확(exp_0915 T7: $10^{-15}$); bit-marginal 파이프라인은 근사(NMSE $\le3.5\times10^{-2}$, $|\Delta v|\le0.11$ at $\tau=1$). 경로 선택은 Q-02.

---

## [2026-09-15] D-04 — 첫 실험 부호: rate-1/2 convolutional $(133,171)_8$, $\nu=6$, terminated (default, 지도교수 승인 대기)

이유: lemma가 정확히 성립하는 유일한 부호족; 핸드오프 §0 권고. LDPC는 M6.

---

## [2026-09-16] D-05 — Q-02 승인: QAM은 심볼 단위 super-section trellis를 주 방식으로

**결정.** 심볼 단위 super-section BCJR(정확, Lemma 2)을 주 방식으로 채택; 비트 marginal 파이프라인(BICM bit metric → 비트 BCJR → product of marginals)은 ablation 전용. Interleaver 정책: symbol interleaver(또는 심볼 그룹 내부 비트 permutation)만 허용, 비트 인터리버가 심볼 경계를 넘지 않음(A7).
**이유.** exp_0916: super-section BCJR은 brute force와 $\le7\times10^{-15}$ 일치($K=16$, 65,536 codeword 포함); 비트 파이프라인은 $(133,171)_8$·16-QAM·$\tau=1$에서 NMSE $5.2\times10^{-2}$, 심볼 최대 오차 $0.52$, $|\Delta v|$ 평균 $0.21$. rate-1/2·16-QAM에서 branch metric 수는 비트 BCJR과 동일($2^\nu\cdot4$/심볼). 사용자 승인 2026-09-16.
**대안.** 비트 파이프라인 + 오차 보고(기각: 정확성 lemma의 payoff를 QAM에서 잃음).

## [2026-09-16] D-06 — QAM 라벨링·그룹 규약 (reversible)

3GPP TS 38.211 §5.1.4 Gray 식 채택(QPSK/16/64-QAM): I는 $(b_0,b_2,\dots)$, Q는 $(b_1,b_3,\dots)$; 심볼 그룹은 연속 $m$ coded bits(section 순, $q=m/n_c$ info bits/심볼). [VERIFY] Sionna `Constellation("qam", m)` 라벨링과 일치 여부(Q-13).

## [2026-09-16] D-07 — Lemma v1 확정, M1-lemma 완료

`lemma_decoder_score_v1.md`: Lemma 1(실수 BPSK), Corollary 1.1(복소 embedding)·1.2(puncturing, tilted prior), Lemma 2(심볼 단위 QAM: 정확 심볼 사후, 복소 Tweedie, Wirtinger Jacobian $\partial\bar x_n/\partial r_j=\tau^{-1}(\mathbb E[x_nx_j^*]-\bar x_n\bar x_j^*)$, 정확 비트 marginal), Remark 2.1(비트 파이프라인 근사 정량). 동반 노트 §8 완료 조건(정리·증명·가정 한 페이지 + $K\le20$ brute force 통과) 충족. M1 잔여: 없음. M1–M2 잔여: 채널 score 모델.

---

## [2026-09-17] D-08 (제안, 승인 대기) — route (a)의 골격은 EP/VAMP형 3-module, BiG-AMP형은 baseline (ii)

**제안.** Module D(Lemma 2 BCJR, 정확 extrinsic) / Module H(학습 score + Onsager) / Module L_X(LOO cavity + EP-LMMSE 검출) / Module L_H(가중 soft-symbol LS = EP site). 세부는 `route_a_design_v0.md` §3.
**이유.** (1) $8\times4$, $T\le56$에서 AMP Onsager는 large-system 근사(BiG-AMP §IV의 damping 필요); (2) T1 LOO = EP cavity, 유한 $T$에서 정확; (3) 2604.19061 Module C(eq. (16)–(17))는 $\mathbf C^{\setminus n}=\mathbf 0$ 특수경우로 환원되어 비교가 깨끗함.
**대안.** BiG-AMP Table III에 (R13)–(R14)를 BCJR로, (R15)–(R16)을 score denoiser로 바꾼 AMP형 — baseline group (ii)/(iv)로 구현(§2.3).

## [2026-09-17] D-09 (제안, D-08과 함께 승인 대기) — 채널 denoiser의 Onsager 항은 정확 autodiff Jacobian trace

**이유.** exp_0917 (Gaussian prior 폐형): $N=32$에서 단일 표본 Fisher 추정 $\mathrm{std}(\hat\alpha)=0.015\sim0.13$ → $v_{\rm ext}$ 상대오차 $28\sim63\%$; Hutchinson $K=16$은 $8\sim25\%$, $\nu=0.01$에서 발산. 정확 trace는 $2N_rN_t=64$회 JVP 또는 Jacobian 1회, 분산 0. Fisher 형은 (a) 대규모 배열($N\gtrsim10^3$: $6\sim13\%$), (b) 여러 블록 병렬 처리 시 배치 평균($B=8$에서 std $\sqrt8$배 감소), (c) score 모델 진단(curl 항)에 한정.
**부수 결과 [정확].** 복소 per-entry 규약에서 SC-VAMP (4)는 $\alpha=1-\tfrac{\nu}{N}J_c$, $J_c=\mathbb E\|\nabla_{\mathbf q^*}\log p\|^2$, $N$=복소 entry 수로 그대로 성립(유도 §1.8, 수치 검증 F1 mean = 폐형).

## [2026-09-17] 기록 — 원문 복사 완료
2601.07095: (1)–(15), (24)–(26), (30)–(33), (36)–(39), (41), (44)–(48), (64)–(70), §VI-A/D. 1310.2632v3: (1)–(3), (D1)–(D3), (I1)–(I2), (R1)–(R17), (71)–(72), (76)–(77), (93)–(98). 번역 표와 함께 `route_a_design_v0.md`에 보관. 기억으로 재구성한 식 없음.

## [2026-09-17] 기록 — 세션 1 종료
`T2_session1_handoff_2026-09-17.md` 생성. 다음 채팅의 첫 질문은 D-08/D-09 승인 여부(기본값: 승인 후 exp_0918). 커서: exp_0918 → M2.

---

## [2026-09-16] D-08 승인 · D-09 승인 (사용자, 세션 2 첫 턴)

route (a) = EP/VAMP형 3-module(D-08), 채널 denoiser Onsager = 정확 autodiff Jacobian trace(D-09). exp_0918 착수.
**날짜 메모.** 세션 2의 실제 날짜(시스템 시각)는 2026-09-16으로 핸드오프 기준일 09-17보다 앞선다(역전). 로그는 실제 날짜로 적고, 실험 파일명 `exp_0918`은 핸드오프 커서 식별자로 유지.
**파일 정리.** `decision_log__1_/__2_/__3_`, `open_questions__1_/__2_`는 구본·중간본. 이 파일과 `open_questions.md`가 세션 2 기준본.

## [2026-09-16] D-10 (기본값 적용, reversible) — L_H likelihood site는 marginalization 형(form A); v0의 $+\sum_n d_n\,\mathrm{diag}(\boldsymbol\tau_n)$ 항은 ablation 전용

**결정.** 채널 factor $f_n(\mathbf H,\mathbf x_n)=\mathcal{CN}(\mathbf y_n;\mathbf H\mathbf x_n,\sigma^2\mathbf I)$의 $\mathbf H$쪽 site는 $\mathbf x_n\sim\mathcal{CN}(\mathbf r_n,\mathbf T_n)$을 marginalize한 $\mathcal{CN}(\mathbf y_n;\mathbf H\mathbf r_n,\sigma^2\mathbf I+\mathbf H\mathbf T_n\mathbf H^H)$의 공분산을 $d_n^{-1}\mathbf I$, $d_n=(\sigma^2+\sum_j\tau_{jn}\mathbb E|h_{ij}|^2)^{-1}$로 선형화한 Gaussian: 행 precision $d_n\mathbf r_n\mathbf r_n^H$, $\mathbf G=\bar{\mathbf X}\mathbf D\bar{\mathbf X}^H$ (form A; BiG-AMP (R11)과 같은 구조; T1 §3.3의 L_X 형과 대칭).
**이유.** v0의 $\mathbf G=\bar{\mathbf X}\mathbf D\bar{\mathbf X}^H+\sum_nd_n\mathrm{diag}(\boldsymbol\tau_n)$는 심볼 불확실성을 noise inflation($d_n$)과 precision 증가(diag 항)로 두 번 센다. diag 항은 $\exp\mathbb E_{\mathbf x}[\log f_n]$(mean-field/EM, T1의 $\boldsymbol\Sigma=\bar{\mathbf X}\bar{\mathbf X}^H+\sum_n\mathrm{diag}(\mathbf v_n)$) 형에서만 나온다. [우리, 유도; 정확(선형화 안에서)]
**대안.** form B(v0 hybrid) — ablation. **근거.** exp_0918 T3: form B는 NMSE 1.6~2.2배, BLER 2~3배 나쁨(4점 모두).
**부수 결과 [정확].** form A + LMMSE에서 $\boldsymbol\Sigma^{\rm post}_n\preceq\mathbf T_n$, $\mathbf G\succeq\mathbf 0$이므로 L_X·L_H의 extrinsic precision은 구성상 음이 아니다; 무한 분산(precision 0)만 clamp. Q-15의 "비정정" 사례는 심볼별 $\alpha^D>1$(pointwise $v_k>\tau^L_k$, 이진 prior에서 $r\approx0$이면 발생) 한 곳으로 좁혀짐.

## [2026-09-16] 기록 — exp_0918 구현 규약 (`t2_route_a.py`)
- 채널 side 대수는 $\mathbf h=\mathrm{vec}(\mathbf H)$(column-major, $h_{i+N_rj}=H_{ij}$)의 명시적 $N\times N$ 행렬: site $\mathbf A_n=d_n(\mathbf r_n^*\mathbf r_n^{\rm T})\otimes\mathbf I_{N_r}$, $\mathbf b_n=d_n\,\mathbf r_n^*\otimes\mathbf y_n$; LOO cavity $\mathbf P^{\setminus n}=\mathbf P-\mathbf A_n$(T1 §3.2, 정확); L_X 노이즈 공분산 $\mathbf R_n=\sigma^2\mathbf I+\sum_{jj'}M_{jj'}\boldsymbol\Sigma^{[j,j']}$, $\mathbf M=\mathbf r_n\mathbf r_n^H+\mathbf T_n$(일반 공분산까지 정확; Kronecker면 v0의 $\mathrm{tr}(\mathbf C^{\setminus n}\mathbf M)$로 환원).
- G-1 guard: $\mathbf C_q=(\mathbf G+\mathbf I/\nu_{\max})^{-1}$, $\nu_{\max}=10^4$ (초기 $\mathbf G$ 특이, $T_p<N_t$). I-2: 선형화용 2차 모멘트 $\mathbb E|h_{ij}|^2$는 직전 반복의 채널 posterior(초기값 prior), scalar/colored 동일 규칙(v0는 site belief). I-3: 초기 site $\hat{\mathbf H}^E=\mathbf 0$, $\nu^E=\mathrm{tr}(\mathbf C)/N$ = Module H at $\nu^q\to\infty$의 극한(2604.19061 "large value"의 구체화).
- 파일럿: DFT$_{N_t}$의 앞 $T_p$열(unit modulus). 인터리버: 데이터 격자 위 random symbol permutation(trial별 고정). 부호 블록 = 데이터 격자 전체($N_s=N_tT_d$, $K=N_s/2-6$).
- `BitTrellis`: 이진 feed-forward trellis 전용 벡터화 Log-MAP(각 상태의 predecessor 2개, 동일 입력) — `bcjr_bits`와 $7\times10^{-15}$ 일치. `SymbolTrellis.bcjr`: 심볼별 $\tau_n$ + `return_info`(하위 호환).
- 기준 수신기: `colored`(Gaussian prior를 L_H에 정확히 fold; Gaussian에서는 "비등방 $\mathbf C_q$를 받는 Module H"와 동일 — Q-07 상한), `pilot_only`(파일럿 + 정확 colored prior LMMSE 1회 후 L_X↔D turbo), `genie`(known $\mathbf H$, $\mathbf C^{\setminus n}=\mathbf 0$ = 2604.19061 Module C 구조 + BCJR).

## [2026-09-16] D-11 (제안, 승인 대기) — Module H의 hybrid 초기화: 파일럿 단계는 채널 dataset의 2차 모멘트 $\hat{\mathbf C}$를 L_H에 fold(colored Gaussian), 이후 score-based H(스칼라 $\nu^q$)

**근거.** exp_0918b T4b($T_p=2<N_t$): scalar site의 BLER 손실은 대부분 "시작"(첫 반복의 prior 등방화)에서 온다 — colored-init 1회만으로 격차의 ~3/4가 닫힘(6 dB: 0.188→0.150 vs colored 0.138; 9 dB: 0.163→0.075 vs 0.050). 복호 성공 블록의 NMSE는 전 변형 동일(median 0.0047~0.0096)이므로 site 자체는 추정 품질을 해치지 않음. 학습 score에서 $\hat{\mathbf C}$는 dataset 표본 공분산이라 추가 학습 없이 얻어지고, Gaussian-site EP(colored)의 첫 반복은 정확 폐형(Kronecker 없이도 $N\le32$ 행렬). 잔여 격차(cinit1 vs colored, damping 후 9 dB 0.037 vs 0.013)는 colored-noise score(M2 stretch, Q-07)로만 닫힘.
**대안.** (i) 처음부터 colored-noise score 학습(비용 큼, M2 후반), (ii) 스칼라 유지(기각: $T_p<N_t$ 손실).

## [2026-09-16] D-12 (제안, 승인 대기) — decoder extrinsic $(r^D,\tau^D)$ damping $\beta=0.7$ 기본값

**근거.** exp_0918b T4a/T4c: F3(후반 NMSE 점프)의 정체는 **처음부터 복호 실패한 블록의 주기-2 limit cycle**(두 확신 오답 codeword 사이 진동, NMSE $0.36\leftrightarrow0.19$, BER $0.357\leftrightarrow0.405$; scalar·colored 동일, 성공 블록은 scalar = colored 0.0116). $\beta=0.7$이면 cycle이 깨져 실패 블록이 구조됨: $T_p=4$ 6 dB BLER $0.025\to0.000$; $T_p=2$ 6 dB scalar $0.188\to0.163$, cinit1 $0.150\to0.087$, colored $0.138\to0.100$; 9 dB $0.163\to0.087$, $0.075\to0.037$, $0.050\to0.013$. 대가: 수렴 반복 2→5회. $\epsilon\in\{10^{-6},10^{-3}\}$는 무관. BiG-AMP (97)–(98)·v0 의사코드의 damping 위치와 일치.

## [2026-09-16] 기록 — 측정 규약(M-1): 채널 NMSE는 평균 대신 **median + 복호 성공 조건부** 보고
실패 블록의 NMSE(0.4~0.7)가 평균을 지배(exp_0918 T3 colored 0.17 vs 성공 블록 0.0096). 수신기 비교는 BLER + 조건부 NMSE + "구조된 블록 수(t=2 실패 → t=8 성공)"로.

---

## [2026-09-17] 기록 — 세션 3 시작, 파일 버전 정리
프로젝트 업로드 시 파일명이 뒤바뀜: 최신본은 `decision_log__4_.md`, `open_questions__3_.md`, `t2_trellis__1_.py`(접미사 없는 파일이 구본). 이 파일부터 다시 `decision_log.md` / `open_questions.md` / `t2_trellis.py`가 기준본 — 프로젝트의 구본·`__N_` 사본은 삭제 권장. `T2_session1_handoff_2026-09-17.md`(#1)는 프로젝트에 없음(내용은 로그로 복원).

## [2026-09-17] D-11 강등(ablation 전용) · D-12 조건부 승인 — 사용자 "Continue"(세션 3 둘째 턴) = 제시한 기본값 채택으로 기록 (reversible)
**D-11 → ablation.** 이유: (1) F1의 원인은 v0의 등방화 규칙(D-13)이며 $\hat{\mathbf C}$ 없이 고쳐진다(exp_0919 T5/T2: cinit1 vs belief1 paired $p=0.89/0.13/0.22$ at 9/12/15 dB, 둘 다 v0보다 $p<10^{-7}$). (2) 앙상블 공분산이 정보를 주지 않는 prior에서는 D-11 ≡ v0 [예측 → exp_0920에서 확인: $\hat{\mathbf C}=\mathbf I$인 Gaussian-mixture prior, $T_p=2$ 12 dB BLER v0 .817 = D11 .817, 불일치 블록 0]. 지도교수 확인 대기 목록에서 "D-11 정당화 방식" 삭제.
**D-12 승인(기본값 $\beta=0.7$), 조건:** $T_p<N_t$에서는 반복 $\ge16$. 근거: QPSK $T_p=4$ 6 dB (n=320) BLER .041→.025 (불일치 5:0, $p=0.06$), 3 dB (n=140) .379→.343 (5:0); $T_p=2$ 8회 반복에서는 v0 scalar에 손해(.594→.653, $p=0.003$ at 12 dB), belief/colored 중립; 16회 반복(n=160)에서는 belief 중립(.388/.394), colored 이득(.256→.200, 12:3, $p=0.035$). 교차 시점 $t\approx6\sim10$. BPSK에서 보고된 "$T_p=2$ damping 이득"(exp_0918b)은 QPSK 8회 반복에서는 재현되지 않음.

## [2026-09-17] D-13 (기본값 적용, reversible) — L_H→H 메시지는 **belief 등방화**(VAMP의 LMMSE 단계), site 등방화(v0)는 ablation
**유도.** v0: 행렬 extrinsic $\mathbf C_q=\mathbf G^{-1}$을 구한 뒤 $\nu^q=\mathrm{tr}(\mathbf C_q)/N$ — EP가 projection하는 대상은 belief이지 site가 아니다. $T_p<N_t$에서 $\mathbf G$ 특이 → $\nu^q\to\nu_{\max}$ → Module H가 등방 prior를 돌려줌(= F1의 정확한 기작; T5: site 형의 $\hat{\mathbf h}$ = 등방 prior LMMSE, $3.69\times10^{-2}$ 동일).
D-13: $\boldsymbol\Sigma_L=(\mathbf I/\nu^E+\mathbf G)^{-1}$, $\hat{\mathbf h}_L=\boldsymbol\Sigma_L(\hat{\mathbf h}^E/\nu^E+\mathbf b)$, $\alpha_L=\mathrm{tr}(\boldsymbol\Sigma_L)/(N\nu^E)$, $\nu^q=\frac{\alpha_L}{1-\alpha_L}\nu^E$, $\mathbf q=\frac{\hat{\mathbf h}_L-\alpha_L\hat{\mathbf h}^E}{1-\alpha_L}$ [SC-VAMP (2)–(3)를 L_H 쪽에 그대로 적용; 상태 $(\hat{\mathbf h}^E,\nu^E)$는 반복 간 유지, 초기값 I-3]. 옵션 `n_inner`: L_X로 가기 전 L_H↔H를 반복.
**[정확, Gaussian prior]** 고정점에서 $\mathbf b-\mathbf G\hat{\mathbf h}=(\hat{\mathbf h}-\hat{\mathbf h}^E)/\nu^E$, $\mathbf C^{-1}\hat{\mathbf h}=(\mathbf q-\hat{\mathbf h})/\nu^q$, EP 평균 일치 $(\hat{\mathbf h}-\hat{\mathbf h}^E)/\nu^E=(\mathbf q-\hat{\mathbf h})/\nu^q$ ⇒ $\hat{\mathbf h}=(\mathbf C^{-1}+\mathbf G)^{-1}\mathbf b$ (정확 LMMSE 평균; 근사는 공분산에만). 수치: T5 $T_p=2$ 파일럿만 6 dB, $\|\hat{\mathbf h}-\mathbf h^\star\|^2/\|\mathbf h^\star\|^2$: site $3.7\times10^{-2}$ → belief 1/3/10/30회 $8.0\times10^{-3}$/$2.9\times10^{-3}$/$4.9\times10^{-4}$/$3.6\times10^{-6}$; $T_p=4$는 둘 다 정확. $\rho=0$ sanity 항등식은 임의의 $(\mathbf q,\nu^q)$에서 성립하므로 유지.
**부수 효과.** Module H 입력 범위가 유계: 첫 패스 $\nu^q\approx1.0\sim1.25$($T_p=2$; v0는 $5\times10^3$) → M2 학습 범위 $\nu\in[\sim10^{-3},\sim2]\times$채널 전력.
**prior art.** VAMP/EP의 표준 규칙(SC-VAMP (2)–(3), 원문 복사본). 우리 것은 (a) bilinear 수신기의 L_H에서 두 규칙의 차이가 F1의 원인임을 식별, (b) Gaussian 고정점 평균의 정확성 증명·수치 검증, (c) $\hat{\mathbf C}$ fold-in(D-11)과의 비교.

## [2026-09-17] D-14 (기본값 적용, reversible) — H→L site는 denoiser **전체 Jacobian**으로 만든 행렬 site
$\boldsymbol\Sigma_H=\nu^q\mathbf J$, $\mathbf J=\partial\hat{\mathbf h}^{\rm post}/\partial\mathbf q$ (Wirtinger; 2차 Tweedie $\mathrm{Cov}[\mathbf h|\mathbf q]=\nu^q\mathbf J$, 채널 side의 Lemma 2(c′)), $\boldsymbol\Lambda_E=\boldsymbol\Sigma_H^{-1}-\mathbf I/\nu^q$, $\boldsymbol\eta_E=\boldsymbol\Sigma_H^{-1}\hat{\mathbf h}^{\rm post}-\mathbf q/\nu^q$; L_X·LOO는 $\mathbf P=\boldsymbol\Lambda_E+\mathbf G$, site 벡터 $\boldsymbol\eta_E$. 등방 site $(\hat{\mathbf h}^E,\nu^E)$는 denoiser 입력(D-13) 생성에만 사용. 비용: D-09의 정확 trace와 같은 $2N$ JVP(추가 비용 0). Guard: $\boldsymbol\Lambda_E$ Hermitian화 + 고윳값 clip `lam_min`$=10^{-6}$ (비-log-concave prior에서 $\mathrm{Cov}\not\preceq\nu^q\mathbf I$; GMM에서 $\lambda_{\max}(\mathbf J)=1.86$ 관측).
**[정확, Gaussian prior]** 임의의 $(\mathbf q,\nu^q)$에서 $\boldsymbol\Lambda_E=\mathbf C^{-1}$, $\boldsymbol\eta_E=\mathbf 0$ ⇒ mode `colored`와 동일 (T6: $\le1.5\times10^{-13}$, $\nu^q=5\times10^3$ 포함). 따라서 Gaussian testbed의 `colored` 곡선 = "등방-노이즈 score + D-14"의 성능이며, Q-07의 "잔여 격차는 colored-noise score로만 닫힘"은 철회.
**[측정, 비-Gaussian]** exp_0920(GMM, $\hat{\mathbf C}=\mathbf I$): D-13+D-14 = exact-EP 기준(비등방 cavity에서의 정확 tilted 모멘트 = colored-noise denoiser가 줄 값)과 동률 — $T_p=2$ 12 dB .592 vs .592 (8:8), 15 dB .592 vs .608, $T_p=3$ 9 dB .283 vs .267. D-14 단독(site 등방화 유지)은 $T_p=2$에서 무이득(.817): 첫 패스 $\nu^q$가 무정보이기 때문 — D-13이 선행 조건.
**[VERIFY] prior art.** denoiser Jacobian을 사후 공분산으로 쓰는 것은 diffusion 역문제 문헌에 선행이 있는 것으로 기억(2차 Tweedie 기반 posterior covariance; 출처 미확인 [M]). 우리 것은 이를 bilinear turbo 수신기의 행렬값 EP site로 쓰는 것과 Gaussian 항등식·GMM 기준 대비 측정. 학습 score에서의 품질(비대칭 Jacobian, curl)은 추측 — Q-21.

## [2026-09-17] D-15 (제안, 승인 대기) — L_H는 decoder의 **a-posteriori** soft symbol $(\bar x_{jn},v_{jn})$을 소비(`feedback='posterior'`), L_X는 decoder extrinsic + LOO cavity 유지
**유도 [스칼라 모형에서 정확].** factor $f(h,x)=\mathcal{CN}(y;hx,\sigma^2)$, cavity $h\sim\mathcal{CN}(m_h,c_h)$, $x\sim\pi$(이산). tilted $\propto\pi(x)\mathcal{CN}(h;m_h,c_h)f$의 $h$-marginal은 $\sum_xw(x)\,\mathcal{CN}(h;\mu_x,s_x)$, $w(x)\propto\pi(x)\,\mathcal{CN}(y;m_hx,\sigma^2+c_h|x|^2)$ — 즉 **$x$의 tilted marginal(= decoder extrinsic × LOO 채널 하의 $y_n$ likelihood ≈ decoder APP)** 로 가중된다. EP의 $f_n\to\mathbf H$ 메시지는 이 tilted 모멘트에서 cavity를 나눈 것. v0의 "extrinsic 되먹임 + form A"는 tilted $x$-marginal 자리에 cavity $\pi$를 넣은 것이어서 $y_n$이 $x_n$에 대해 주는 정보를 버린다(과소 사용). T1의 F2(자기 강화)는 $w$를 LOO가 아닌 채널로 계산할 때의 문제 — `loo=True`가 막는다.
**근거(exp_0919b, Gaussian testbed, n=160, base = extrinsic+LOO).** BLER base / post_fb / no_loo / post_noloo: $T_p=4$ 3 dB .381/**.269**/.394/.287 (base vs post_fb 20:2, $p=1.2\times10^{-4}$); 6 dB .050/**.025**/.069/.056; $T_p=2$ 12 dB .263/**.150**/.287/.194 (24:6, $p=1.4\times10^{-3}$; post_fb vs post_noloo 0:7, $p=0.016$). exp_0920(GMM): D13x3+14 → +pf $T_p=2$ 12 dB .625→.358 ($p=4\times10^{-9}$), $T_p=3$ 9 dB .292→.158; exactEP .592→.300; Gaussian-$\hat{\mathbf C}$ turbo .842→.475.
**의미.** "posterior 되먹임 + LOO"는 T1의 구조(코드 보조 재추정 + LOO extrinsic 채널 추정)와 같다 — route (a)의 주 방식으로 승격 제안. 승인 시 exp_0919 T2 표는 `feedback='posterior'`로 다시 만든다.

## [2026-09-17] 기록 — Q-04·Q-04′ 닫힘 (exp_0919b)
Module D extrinsic은 **moment-domain(EP, project-then-divide) + 블록 평균 $\alpha^D$** 유지. (iii) pmf-domain(divide-then-project; BCJR에서 정확 extrinsic pmf $P(x_n|\mathbf r_{\setminus n})$를 구해 평균·분산 전달, 고전 turbo soft-symbol 되먹임; brute force 대비 $\le1.3\times10^{-15}$)은 정확 cavity임에도 나쁨: $T_p=4$ 3 dB .381→.450 (7:18, $p=0.043$), 6 dB .050→.094 ($p=0.039$), $T_p=2$ 12 dB .263→.344 ($p=0.047$); pilot-only·genie에서도 같은 방향. 2604.19061 Fig. 3의 주장(moment > LLR-domain)이 **정확 decoder에서도** 성립 [측정; 기작은 추측: LMMSE 모듈이 소비하는 것은 Gaussian family 안에서 Onsager 보정된 메시지]. 핸드오프 후보였던 "$r^D=\tau^DL^{\rm ext}/4$"는 방정식 하나에 미지수 둘이라 채택하지 않음. (iv) 심볼별 $\alpha^D$: BLER .425(6 dB)/.769(3 dB)/.444($T_p=2$ 12 dB), clip 도달 31~61% — 기각.

## [2026-09-17] 기록 — 세션 4 시작: 핸드오프 #3 §1.6의 로그 미반영 사항 반영
1. `n_inner` 기본값 = **1** (belief1 vs belief3 $p=0.60/0.14/0.86$; GMM D13+14 vs D13x3+14 .592 vs .625/.592, .283 vs .292 — 이득 없음; score 평가 1회/반복).
2. v1 옵션 묶음(`mode='scalar', scal='belief', hsite='matrix', lam_min=1e-6, beta=0.7` ± `feedback='posterior'`)은 Gaussian Kronecker testbed에서 `mode='colored'`와 동일($|\Delta{\rm NMSE}|\le1.4\times10^{-13}$, BER 동일) → Gaussian testbed 실험은 `colored`로 대체.
3. 스크립트 병합: `exp_0919_tests.py`(T0/T1/T5/T6/T7). **`exp_0919_analysis.py`는 프로젝트에 없음**(핸드오프 #3 §6 표와 불일치; 세션 3 컨테이너와 함께 소실) — exp_0919 raw를 다시 분석할 일이 생기면 재작성. exp_0921은 자체 분석 스크립트 사용.
4. raw 로그(npz) 미보관 — 핸드오프 #3 §6 명령으로 재생성.
5. F5 근거: 첫 패스 $\tau^L$의 SNR 무관성(9/12/15 dB: belief1 1.99/1.93/1.89, v0 2.63/2.52/2.49; $T_p=4$는 0.91→0.42). **$T_p=2$ 0 dB는 미실행.**
6. D-15는 세션 3에서 미응답 → 여전히 **승인 대기**(세션 4 첫 턴에 재질문).

## [2026-09-17] D-16 (사용자 지시, 확정) — 실행 분담: 실험 실행은 사용자, Claude는 코드·출력 사양·분석
시간·토큰 비용 때문에 **Python 실험은 Claude 컨테이너에서 돌리지 않는다.** Claude는 (i) 스크립트와 (ii) 필요한 출력 사양을 주고, 사용자가 실행해 결과 텍스트(`exp_MMDD_results.txt`)를 전달한다. 코드 기준 위치 = 사용자 git repo(채팅에 연결 예정). Claude 쪽에서 허용되는 실행: `py_compile`, $n\le2$ smoke test(수치는 버림), 폐형식 평가(초 단위). 이에 따라 스크립트는 (a) repo 루트 기준 상대 경로, (b) `--jobs` 멀티프로세스 + chunk 재개, (c) 붙여 넣기 좋은 압축 출력으로 작성. 세션 3 스크립트의 `/home/claude/t2` 하드코딩은 `.`로 치환한 사본을 전달(본문 무변경).

## [2026-09-17] 기록 — `t2_route_a.py` exp_0921 패치 (기본 동작 무변경)
`RouteA(..., Xp=None, beta_fb=None)`. `Xp`: 파일럿 override($N_t\times T_p$; 기본 DFT 앞 $T_p$열). `beta_fb`: `feedback='posterior'`일 때 L_H로 가는 a-posteriori 모멘트 $(\bar x,v)$의 damping(기본 None = 세션 3 동작). **발견:** D-12의 $\beta$는 extrinsic 쌍 $(r^D,\tau^D)$에만 걸리고 D-15 경로의 $(\bar x,v)$는 damping되지 않는다 → exp_0921 A에 `col_post_b0.7_fbd` 변형 추가(Q-24). 회귀 확인은 사용자가 `python exp_0919_tests.py t0`, `t6`으로(기대값: `exp_0919_results.txt` 앞부분).

## [2026-09-17] 기록 [정확, Gaussian prior] — F5의 폐형식: 첫 패스 = pilot-only LMMSE, 고SNR 잔차는 $\mathbf R_t$의 Schur complement
form A에서 $\bar{\mathbf x}_n=\mathbf 0$이면 데이터 site는 $\mathbf A_n=\mathbf 0$ → **모든 수신기의 첫 패스 채널 belief = 파일럿 LMMSE.** $\boldsymbol\Sigma=(\mathbf C^{-1}+(\mathbf X_p^*\mathbf X_p^{\rm T})\otimes\mathbf I/\sigma^2)^{-1}$, $\sigma^2\to0$: $\boldsymbol\Sigma\to\mathbf S^{\rm T}\otimes\mathbf R_r$, $\mathbf S=\mathbf R_t-\mathbf R_t\mathbf X_p(\mathbf X_p^H\mathbf R_t\mathbf X_p)^{-1}\mathbf X_p^H\mathbf R_t$, 따라서 $\mathrm{NMSE}_\infty=\mathrm{tr}\,\mathbf S/N_t$ ($\mathbf R_r$·$N_r$ 무관). 첫 패스 L_X 노이즈($\mathbf r=\mathbf 0,\tau=1\Rightarrow\mathbf M=\mathbf I$): $\mathbf R_n=\sigma^2\mathbf I+\mathrm{tr}(\mathbf S)\,\mathbf R_r$ → 간섭 제한 $\mathrm{SIR}_\infty=(1-\mathrm{NMSE}_\infty)/\mathrm{NMSE}_\infty$, **SNR 무관** = F5의 기작. 파일럿이 $\mathbf R_t$의 상위 $T_p$ 고유벡터를 span하면 $\mathrm{NMSE}_\infty=\sum_{k>T_p}\lambda_k/N_t$ = 모든 $T_p$차원 파일럿 부분공간 중 최소(Ky Fan).
수치(`exp_0921_run.py predict`, 폐형식): $\rho=0.7$ $\lambda=(2.725,.754,.318,.203)$. $\mathrm{NMSE}_\infty$ / $\mathrm{SIR}_\infty$: $T_p=2$ DFT **.168 / 6.9 dB**, eig .130 / 8.2 dB; $T_p=3$ DFT .102 / 9.4 dB, eig **.051 / 12.7 dB**; $\rho=0.9$: $T_p=2$ DFT .056 / 12.2 dB, eig .041 / 13.7 dB; $T_p=3$ eig .015 / 18.1 dB. 12 dB 유한 SNR: $\rho=0.7$ $T_p=2$ DFT .177 — 핸드오프 #3의 측정 \"첫 패스 NMSE≈0.2\"와 정합(측정은 trial별 비의 통계, 폐형식은 기대값의 비 — 엄밀 비교는 exp_0921 출력의 NMSE@1로).
**우리 것 / prior art:** 상관 채널에서 고유방향 정렬 훈련 신호의 최적성은 prior art [M — 출처 미확인, VERIFY: correlated MIMO training design 문헌]; \"annealed turbo 수신기의 시동 실패(F5)를 첫 패스 Schur 잔차로 설명하고 regime 선택에 쓰는 것\"이 우리 것.

## [2026-09-18] 기록 — exp_0921 A 결과 판독 (사용자 실행, repo `TaeJun1999/T2-Annealed-receiver` `Demo/`, 커밋 c719936; n=320/점, 16 반복)
**D-15 [측정, 새 시드에서 재현 + $\beta=0.7$·16 반복에서 유지].** `col_ext_b0.7` vs `col_post_b0.7` @16 불일치(ext만 실패 : post만 실패): $T_p=4$ 0/3/6/9 dB 52:1 / 35:5 / 7:1 / 1:0 ($p=10^{-14}$/$10^{-6}$/.07/1); $T_p=2$ 6/9/12/15 dB 87:11 / 70:14 / 51:13 / 34:6 (모두 $p<10^{-5}$). BLER@16: $T_p=4$ 3 dB .284→.191, 6 dB .037→.019; $T_p=2$ .531/.344/.231/.147 → **.294/.169/.113/.059**. D-15는 여전히 사용자 승인 대기이나 근거는 충분.
**LOO [측정].** posterior 되먹임에서 LOO 제거: 4:23, 2:23, 0:8 ($T_p=4$ 0/3/6 dB), 2:31, 2:15, 1:12, 1:5 ($T_p=2$). 실패 분류에서 no-LOO는 `stuck`(오답 고정점)이 5~30%로 증가(LOO 있으면 0~3%, 0 dB 제외) = 자기 강화(T1 F2)의 직접 증거.
**Q-24 닫힘 [측정].** posterior 경로 damping(`beta_fb=0.7`)은 해롭다: 0:7, 5:24, 5:21, 3:12, 2:16 ($p\le.035$; $T_p=4$ 3/6 dB는 @8에서만 손해 0:10 → @16 중립) → **`beta_fb=None` 유지.**
**D-12 × D-15 [측정].** `col_post_b1` vs `_b0.7` @16: 11:4, 11:10, 12:1($p=.003$), 0:0, 15:4($p=.019$), 10:5, 6:4, 10:1($p=.012$) — 손해 없음, 세 점에서 유의한 이득 → $\beta=0.7$ 유지. cyc2(주기-2) 실패 블록은 posterior에서 0.3~5.3%(extrinsic 2.5~10%).
**D-13/D-14의 재평가 [측정 — 기여 목록에 영향].** posterior 되먹임 하에서는 v0(site 등방화)도 크게 회복: $T_p=2$ @16 `v0_post_b0.7` .328/.247/.144/.119 ≈ `bel_post_b0.7` .347/.225/.150/.119 (paired 미실시 → 분석 스크립트에 쌍 추가). 즉 **D-15가 켜지면 D-13의 @16 이득은 사라짐**(@8에서는 소폭). D-14(행렬 site)는 유지: `bel_post` vs `col_post` 27:10, 34:16, 22:10, 24:5 ($p=.008/.015/.05/.0006$), $T_p=4$는 무차별. 해석[추측]: APP 되먹임은 첫 반복 직후 $\mathbf G$를 full-rank·고정밀로 만들어 site 등방화의 $\nu^q\to\nu_{\max}$ 문제(F1)를 한 반복 만에 벗어남.
**F5 폐형식 검증 [측정 정합].** NMSE@1(trial별 비의 median) $T_p=2$ 6/12/15 dB .208/.188/.167 vs 폐형식 .198/.177/(∞: .168); $T_p=4$ 6 dB .054 vs .049. $\tau^L$@1: $T_p=2$ 2.00/1.77/1.63/1.57(포화) vs $T_p=4$ 2.06/1.38/.91/.61.
**F5 재서술.** D-15+$\beta$+16 반복에서 $T_p=2$는 hard floor가 아니라 **완만한 기울기**(3 dB당 BLER 약 1/2; 15 dB .059, 계속 감소). 첫 패스 BLER≈1($\tau^L\ge1.57$)인데도 320 중 100~174 블록을 구조 — 시동에 첫 패스 복호 성공은 불필요.
**headline 점검.** $T_p=4$: pilot-only(best $\beta$) vs joint BLER@16 0 dB .809/.637, 3 dB .347/.191, 6 dB .062/.019(14:0), 9 dB .003/.003 → BLER 0.1 기준 약 5.2 → 3.8 dB(**≈1.3 dB 이득**, genie ≈1.5 dB). $T_p=2$ DFT: pilot-only는 .48~.82로 실패, joint는 0.1에 ≈12.6 dB — $T_p=4$ pilot-only(5.2 dB)보다 7 dB 나쁨, $K$ 이득은 +8.9% → **$\rho=0.7$·DFT·$T_p=2$는 headline 영역이 아님.** 후보는 폐형식이 가리키는 $T_p=3$(eig) — exp_0921 B로 판정.

## [2026-09-18] 기록 — Q-25(a) paired 확인 (repo 커밋 0f37555의 raw npz에 분석만 실행; 시뮬레이션 아님)
`v0_post_b0.7` vs `bel_post_b0.7` @16 (v0만 실패 : belief만 실패): $T_p=4$ 3:2, 3:3, 1:1, 0:0; $T_p=2$ 26:32, 38:31, 21:23, 24:24 — **전 점 $p\ge0.47$ → D-15 하에서 D-13의 @16 이득 없음 [측정].** @8도 $p\ge0.06$. `v0_post` vs `col_post`: $T_p=2$ @16 39:28($p=.22$), 46:21(.003), 30:20(.20), 29:10(.003); @8은 52:24, 58:19, 47:17, 44:12(모두 $p\le.002$) → **D-14(행렬 site)의 이득은 주로 수렴 속도(@8), @16에서는 부분적으로만 유지.**
관찰: BLER이 같은데도 불일치 쌍이 많다(예: 6 dB 26:32 / 320) → $T_p=2$의 실패는 채널 실현만으로 결정되지 않고 궤적에 민감(genie BLER = 0이므로 정보 한계가 아니라 시동 basin 문제) [추측 → Q-20(a)].

## [2026-09-18] 기록 — exp_0921 B 결과 판독 (사용자 실행, 커밋 0e905f7; 4x4, n=160/점, 16 반복, 192코어 서버에서 2.8분)
운영 메모(D-16 보강): 서버는 사실상 단독 사용 → 이후 명령에 `--jobs`를 지정하지 않는다(기본 = 전체 코어).
**SNR@BLER 0.1 [측정, 보간], $\rho=0.7$:** $T_p=4$: pilot-only 5.0, joint(`col_post_b0.7`) 4.0, genie 1.8. $T_p=3$: DFT pilot 18.0 / joint 6.8; **eig pilot 8.1 / joint 5.2**. $T_p=2$: DFT joint 12.6(A와 일치), **eig joint 9.2**, pilot-only는 두 파일럿 모두 >18. eig 파일럿 이득: joint 기준 $T_p=3$ 1.6 dB, $T_p=2$ 3.4 dB — 폐형식($\mathrm{SIR}_\infty$ 9.4→12.7, 6.9→8.2 dB)의 방향과 일치.
**pilot-only의 error floor를 joint가 제거 [측정]:** $T_p=3$ eig, 12/15/18 dB: pilot-only(best $\beta$) BLER .025/.025/.019 vs joint **0/0/0**; $T_p=2$ eig 9/12/15 dB: pilot .53/.40/.29 vs joint .106/.037/.013 (paired 70:2, 58:0, 44:0). 스크립트의 regime check(pilot ≥ .5 & joint ≤ .1)는 "none"이지만 $T_p=2$ eig 9 dB에서 .006 차이로 놓친 것 — 기준이 너무 빡빡했음.
**goodput 포락선 $K(1-\mathrm{BLER})/T$, $\rho=0.7$ (pilot-only 최선 구성 vs joint 최선 구성):** 0 dB .44 vs 1.04; 3 dB 2.01 vs 2.49; 6 dB 3.05 vs 3.15; 9 dB 3.19 vs 3.32($T_p=3$ eig); 12 dB 3.27 vs 3.37($T_p=2$ eig); 15 dB 3.27 vs 3.46($T_p=2$ eig). 즉 **저SNR에서는 같은 $T_p=4$에서 ≈1 dB, 중·고SNR에서는 파일럿 절감으로 +3~6% goodput.** headline은 "SNR 이득 ~1 dB + floor 제거 + 파일럿 절감 수 %" — 큰 숫자는 아님(정직하게 기록).
**$\rho=0.9$:** genie 자체가 8.8 dB 필요. $T_p=4$ joint 11.3 vs pilot 11.4(이득 없음, 저SNR에서만 18:1, 13:2), $T_p=3$ eig joint 12.3. → $\rho=0.9$는 headline 영역이 아님(강한 상관 = prior가 이미 채널을 거의 결정, 남는 손실은 다중화 자체).
**주의 [VERIFY]:** 18 dB 점에서 모든 수신기가 15 dB보다 나쁨($T_p=2$ eig joint .013→.069, pilot .29→.33, $\tau^L$@1도 1.371→1.384) → SNR별 독립 시드의 표본 효과로 판단(수신기 공통). 결정 점은 n 증량으로 확인. 개선안: SNR 간 common random numbers(같은 $H,u,$ perm, 노이즈만 스케일) 옵션 — 미도입.

## [2026-09-18] D-15 승인 (사용자, reversible) — L_H는 a-posteriori 소비, L_X는 extrinsic + LOO
사용자 메시지 "D-15 승인 하면 되는건가?"(2026-09-18)를 설명 후 승인으로 기록; 의도와 다르면 "보류" 한마디로 되돌린다. 근거: exp_0919(시드 20260919)와 exp_0921 A(시드 20260921, $\beta=0.7$·16 반복) 두 시드·8점에서 일관(87:11, 70:14, 51:13, 34:6 등), LOO 필수(2:31 등), posterior 경로 damping 불필요(Q-24).
귀결: (1) v1 기본 구성 = `colored`/(`belief`+`matrix`) + `feedback='posterior'` + `loo=True` + `beta=0.7` + `beta_fb=None` + `n_inner=1`. 단 **`RouteA`의 생성자 기본값은 바꾸지 않는다**(회귀 테스트 t0/t6이 기본값 = extrinsic·$\beta=1$에 의존) → 다음 코드 변경 때 preset 헬퍼(`RouteA.v1(...)`)로 추가. (2) 서술 변경: "extrinsic coupling"은 **L_X 방향(복호기→검출기)** 에만 해당, L_H(채널 추정)는 APP를 소비 — 지도교수 확인 목록에 확정 항목으로 추가. (3) 기여 목록 재평가는 exp_0921 C(Q-25(b)) 결과 후.

## [2026-09-18] 기록 — exp_0921 B 확장(4x4 $\rho=0.7$ n=640, 8x4 n=320) + C(GMM, n=320) 판독 (커밋 f877eb8; 서버 2분 08초)
**B, 4x4 $\rho=0.7$ n=640 [측정].** SNR@0.1: $T_p=4$ pilot 4.9 / joint 3.8(**1.1 dB**) / genie 1.4; $T_p=3$ eig pilot 8.2 / joint 4.8; $T_p=2$ eig joint 9.4, DFT 12.9. n=160의 18 dB 비단조성은 사라짐(표본 효과 확인).
**정정 — F5는 4x4에서 floor가 맞다.** $T_p=2$ eig joint BLER@16 12/15/18 dB = .052/.041/.036, DFT 15/18 dB = .087/.083(09-18 오전의 "완만한 기울기, hard floor 아님" 서술은 n=320·15 dB까지만 본 과대 해석). $T_p=3$ eig는 joint .006/.005/.002 vs pilot .023/.011/.011.
**goodput 포락선 정정(n=640).** joint/pilot 이득: 0 dB +114%, 3 dB +26%, 6 dB +4.1%, 9 dB +3.6%, 12~18 dB **+1.1~1.8%**(n=160의 +3~6%는 표본 효과 포함). pilot-only도 $T_p=3$ eig로 3.32까지 가기 때문. → **4x4 headline = 저SNR ≈1.1 dB, 그 외 goodput 1~4%. 약함.**
**B, 8x4 n=320 [측정] — 더 나은 영역.** $T_p=2$ eig: joint SNR@0.1 **2.4 dB** vs pilot-only 9.0 dB(DFT: 3.5 vs >18). joint BLER 9/12/15/18 dB = .013/.009/.003/**.000** (floor 없음) vs pilot-only .100/.094/.075/.059 (floor). 포락선 이득 0 dB +10%, 3 dB +4.8%, 9~18 dB +3.3~4.3%; 18 dB에서 joint $T_p=2$가 상한 $K/T=3.50$ 도달(pilot-only 최선은 $T_p=3$의 3.357). → **$N_r>N_t$에서 F5 floor 소멸; "$T_p<N_t$는 joint에서만 성립"이 깨끗하게 보임.** 단 goodput 이득의 상한이 파일럿 비율($4/28$)에 묶여 있어 수 %가 한계 → 파일럿 오버헤드가 큰 영역(짧은 $T$ 또는 큰 $N_t$)이 필요(Q-28).
**C, GMM [측정].** (1) D-15는 모든 site 규칙에서 성립: $T_p=2$ 9 dB `v0` 136:6, `D13` 106:14, `D13+14` 86:10, `exactEP` 115:7. (2) Q-25(b): $T_p=2$ @16 BLER 9/12/15 dB — `v0_pf` .450/.438/.406, `D13_pf` .406/.397/.378, `D14_pf` .456/.428/.406, **`D13+14_pf` .381/.344/.362**, `exactEP_pf` .319/.263/.244, `oracle_pf` .231/.156/.147, `lmmseC_pf` .525/.494/.431, `pilot_gmm` .869/.841/.809, genie 0. paired: `v0_pf` vs `D13+14_pf` 56:34($p=.026$), 47:17(.0002), 44:30(.13); D-14 단독은 v0와 동일(24:26, 26:23, 26:26), D-13 단독은 방향만(48:34, 39:26, 41:32; @8은 $p=.05/.006/.06$) → **비Gaussian testbed에서는 D-13+D-14 묶음이 D-15 위에서도 유의(단, 둘이 함께일 때만).** $T_p=4$에서는 모든 `_pf`가 동률(v0_pf .178 ≈ 묶음 .200 ≈ exactEP .200 ≈ oracle .191; pilot_gmm .356). (3) **score 인터페이스의 비용:** `D13+14_pf` vs `exactEP_pf` 53:33(.04), 61:35(.01), 73:35(.0003) — 등방 노이즈 denoiser만 쓰는 경로가 정확 mixture-EP site에 유의하게 뒤짐(Q-27). (4) `exactEP_pf` vs `oracle_pf` 36:8, 42:8, 43:12 — 성분 불확실성의 Gaussian 사영 손실이 큼. (5) 2차 모멘트 방법 대비: `lmmseC_pf` vs `D13+14_pf` 74:28, 61:13, 52:30, vs `v0_pf` 39:15, 29:11, 21:13 → "2차 모멘트를 넘는 prior의 이득" 지지.
**기여 목록 재평가(잠정).** ① D-15(APP→L_H, ext+LOO→L_X) = 두 testbed 모두에서 지배적 요인. ② D-13+D-14 묶음 = 비Gaussian·$T_p<N_t$에서 유의, Gaussian에서는 수렴 속도. ③ 등방 인터페이스의 비용(Q-27)은 정량화된 한계로 보고. ④ regime = $N_r>N_t$, $T_p<N_t$, 정렬 파일럿; goodput headline은 오버헤드가 큰 영역에서 재측정 필요.

## [2026-09-18] 기록 — exp_0921 B-T (Q-28) 판독: 짧은 블록 (커밋 e21e108; $\rho=0.7$, n=640, 서버 1분 46초)
**8x4, $T=16$ [측정].** 포락선(pilot-only 최선 vs joint 최선) goodput 이득: 0 dB +12.2%, 3~15 dB **+6.0~7.2%**, 18 dB +4.8% ($T=28$의 +3~4%에서 약 두 배). SNR@0.1: $T_p=2$ eig joint 2.2 dB vs pilot-only 10.8 dB; $T_p=2$ DFT 3.6 vs >18. joint $T_p=2$ eig goodput 6~18 dB = 3.03~3.09(상한 3.125; 잔류 BLER .011~.03), pilot-only 최선은 $T_p=3$ eig 2.875(18 dB에서만 $T_p=2$ eig 2.95).
**고정 goodput에서의 SNR 이득(8x4, $T=16$, 선형 보간):** 목표 2.85: pilot-only ≈7.5 dB vs joint ≈2.7 dB(**≈4.8 dB**); 목표 3.0: pilot-only는 0~18 dB에서 **도달 불가**, joint ≈5.3 dB. → headline 표현은 "동일 goodput에서의 SNR 이득 / pilot-only로 도달 불가능한 goodput"이 % 이득보다 적절.
**8x4, $T=12$:** +13.0%(0 dB), +6.4~9.2%(3~12 dB), +5.3%(18 dB). **4x4, $T=16$:** +34%(0 dB), +7~8%(3~6 dB), +3.4~5.2%(9~15 dB); $T_p=2$ floor 잔존(.03~.08).
**해석.** 이득의 실질 상한은 "$T_p=2$ vs pilot-only가 floor 없이 쓸 수 있는 최소 $T_p$(=3, eig)"의 $K$ 비: $T=16$ +8.7%, $T=12$ +13.3%. 측정 이득은 상한의 70~80%. (핸드오프 §6.1의 headline 목표와의 대조는 다음 세션 시작 시.)

## [2026-09-18] 기록 [정확 + 검증] — Q-27 유도: one-shot 등방 denoiser 인터페이스의 SNR-무관 floor
**모형.** L_H 메시지 $\propto\exp(-\mathbf h^H\mathbf G\mathbf h+2\Re\,\mathbf b^H\mathbf h)$, $\mathbf G=g\boldsymbol\Pi$ (rank $\kappa N$ 사영; 첫 패스·DFT 파일럿이면 정확히 이 형태, $g=N_t/\sigma^2$, $\kappa=T_p/N_t$), 등방 prior-site $(\hat{\mathbf h}^E,\nu^E)$. D-13(§2.1)에 대입:
$$\alpha_L=(1-\kappa)+\frac{\kappa}{1+g\nu^E},\qquad \boxed{\nu^q=\frac{1-\kappa}{\kappa}\,\nu^E+\frac{1}{\kappa g}},\qquad \mathbf q\xrightarrow{g\to\infty}\hat{\mathbf h}^E+\tfrac1\kappa\boldsymbol\Pi(\mathbf y-\hat{\mathbf h}^E).$$
**귀결.** (i) $\kappa<1$이면 denoiser 입력 노이즈가 SNR과 무관한 floor $\frac{1-\kappa}{\kappa}\nu^E$를 가짐($T_p=2$: $\nu^q\ge\nu^E=1$ = prior 분산 수준, $T_p=3$: $\ge1/3$). 정확 posterior는 관측된 $\kappa N$차원을 정밀도 $g$로 아는데, 등방 인터페이스는 이를 평균 내어 버림. (ii) 미관측 방향에는 $\mathbf q=\hat{\mathbf h}^E$, 즉 **수신기 자신의 이전 추정이 분산 $\nu^q$의 "관측"으로 되먹임** → 성분 책임도 $w_k(\mathbf q,\nu^q)\propto\pi_k\,\mathcal{CN}(\mathbf q;\mathbf 0,\mathbf C_k+\nu^q\mathbf I)$가 정확값 $w_k\propto\pi_k\det(\mathbf I+\mathbf C_k\mathbf G)^{-1}e^{\mathbf b^H\mathbf S_k\mathbf b}$에서 편향. (iii) $\kappa=1$·등방 $\mathbf G$($T_p=N_t$, DFT)에서는 $\nu^q=\sigma^2/N_t$, 인터페이스 무손실. (iv) Gaussian prior에서는 평균이 여전히 정확(D-14 항등식) — 손실은 **비Gaussian prior에서만**. (v) `n_inner`를 늘려도 floor는 남는다: 방향성 성분도 $\mathrm{tr}\,\mathbf C_k/N=1$이라 등방 요약 $\nu^E$가 줄지 않음 — 세션 3의 "n_inner=3 이득 없음"과 정합.
**검증.** 폐형식 $\nu^q$ = 코드(`RouteA` 로그) 4자리 일치: $T_p=2$ 6/12/18 dB 1.1256/1.0315/1.0079, $T_p=3$ .4171/.3544/.3386, $T_p=4$ $\sigma^2/4$. 핸드오프 #3의 "$T_p=2$ 첫 패스 $\nu^q$ 1.0~1.25"를 설명($1+2/g$, 3~15 dB). 측정 정합: exp_0921 C에서 `D13+14_pf` vs `exactEP_pf` 격차는 $T_p=2$에만 있고 $T_p=4$는 동률.
**우리 것 / prior art.** VAMP류의 등방(스칼라 분산) 인터페이스가 대형·회전불변 가정에서만 정확하다는 것은 prior art [M]. "turbo 수신기에서 $T_p<N_t$일 때 score-denoiser 인터페이스에 SNR-무관 floor $\frac{1-\kappa}{\kappa}\nu^E$가 생기고 이것이 성분 식별을 편향시킨다"는 정량화가 우리 것.
**처방 후보(Q-27 계속).** R-A: one-shot Tweedie 대신 **비등방 Gaussian likelihood + 등방 prior score의 annealed posterior sampling**(likelihood 기울기는 해석적이므로 등방 score만 있으면 됨; 표본 모멘트로 D-14 형 site 구성; turbo 반복 간 warm start) — 비용 큼, 학습 score에도 적용 가능. [M: score 기반 MIMO 채널 추정의 posterior sampling은 prior art — 프로젝트 PDF 2204.07122 확인 필요, VERIFY]. R-B: 관측 부분공간과 미관측 부분공간을 분리한 2-분산 인터페이스 — 학습 score로는 불가(등방 노이즈만 학습) → GMM에서 상한 확인용. 다음: `exp_0922_interface.py`로 첫 패스 손실 정량화 후 R-A 설계.

## [2026-09-18] 기록 — 세션 5 시작: 로그 파일 정리
repo `docs/logs/`에 `decision_log.md`(구본, 09-18 오전)와 `decision_log .md`(파일명에 공백; 세션 4 말 갱신본, B-T·Q-27 유도 2개 항목 +31행)가 공존. **본 파일이 공백본을 흡수한 정본.** 사용자 조치: 이 파일을 `docs/logs/decision_log.md`로 덮어쓰고 `decision_log .md`는 삭제. `open_questions.md`, `scooping_log.md`는 세션 4 말 갱신본이 정상 반영되어 있음(확인).

## [2026-09-18] 기록 — exp_0922 판독 (사용자 실행, 커밋 2a276fe; GMM, 4x4, DFT, 첫 패스, n=2000, 18초)
**[측정]** (1) $T_p=4$: 모든 열 일치(인터페이스 무손실, $\nu^q=\sigma^2/N_t$) — 예측대로. (2) 폐형식 $\nu^q$ = 측정 = `RouteA` 로그(4자리, 9점 전부). (3) $T_p=2$ 6/12/18 dB: $P_{\rm map}$ exact .767/.821/.841 vs iso **.402/.407/.447**; NMSE exact .416/.385/.378, D13 1-shot .587/.577/.578, **D13+D14 .471/.451/.450 (+13/+17/+19%, 0.5~0.8 dB)**, LMMSE($\mathbf I$) .519/.510/.505, oracle .373/.359/.342. (4) $T_p=3$: $P_{\rm map}$ .892/.943/.953 vs .727/.764/.771; NMSE exact .208/.176/.171 vs D13+D14 .227/.193/.187 (+9~10%).
**해석.** (a) 사전 기준("$P_{\rm map}$(iso) ≪ exact, NMSE(D13+D14) > exact") 충족 → **R-A 설계 진행.** (b) D13 1-shot 평균은 $T_p=2$에서 LMMSE($\mathbf I$)보다도 나쁘다: $\mathbf q=\frac1\kappa\boldsymbol\Pi\mathbf y$(관측 방향 2배, 미관측 방향 0)를 등방 관측으로 해석하기 때문. D-14가 $\mathbf G$를 다시 결합해 LMMSE($\mathbf I$)→exact 격차의 43~47%($T_p=2$), 79~80%($T_p=3$)를 회수. (c) 격차는 SNR과 함께 **커진다**(floor의 서명; exact는 SNR로 개선, iso는 정체). (d) [근사] 첫 패스 SIR proxy $(1-\mathrm{NMSE})/\mathrm{NMSE}$, $T_p=2$ 12 dB: exact 2.0 dB / D13+D14 0.9 dB / LMMSE($\mathbf I$) −0.2 dB — 시동 임계 부근에서 ≈1.2 dB 차이. exp_0921 C의 `D13+14_pf` vs `exactEP_pf`(73:35)와 방향 정합[추측: 인과는 미측정]. (e) exact vs oracle은 +5~10%로 작음(첫 패스 NMSE 기준).
**주의.** R-A가 정확 모멘트를 주면 GMM testbed에서 R-A ≡ `exactEP_pf` — 즉 **R-A의 BLER 상한은 이미 측정되어 있음**(exp_0921 C: $T_p=2$ 9/12/15 dB .381/.344/.362 → .319/.263/.244, n=320). 남은 질문은 표집기의 비용·정확도.

## [2026-09-18] 기록 [정확 + 폐형식 검증] — R-A 유도: noise-splitting 항등식과 Rao-Blackwell 모멘트; D-13+D-14는 단일점 특수 경우
**목표.** $\pi(\mathbf h)\propto p(\mathbf h)\,\ell(\mathbf h)$, $\ell=\exp(-\mathbf h^H\mathbf G\mathbf h+2\Re\,\mathbf b^H\mathbf h)$, $\mathbf G\succeq0$(특이 가능)의 평균·공분산을 **등방 denoiser** $D(\mathbf z,\nu)=\mathbb E[\mathbf h|\mathbf z=\mathbf h+\mathbf e]$, $\mathbf e\sim\mathcal{CN}(\mathbf 0,\nu\mathbf I)$만으로. (2-factor 모형에서 prior factor의 EP cavity는 $\ell$ 자체 → tilted = 정확 posterior. 문제는 오직 "비등방 $\mathbf G$ + 등방 denoiser".)
**항등식 [정확].** $\mathbf G=\mathbf V\mathrm{diag}(g_i)\mathbf V^H$, $\upsilon_i=(\mathbf V^H\mathbf b)_i/g_i$ ($\zeta_i=(\mathbf V^H\mathbf h)_i$의 잡음 분산 $1/g_i$ LS 관측). $\nu\le1/g_{\max}$이면 관측 잡음을 $w_i=e_i+w_i'$, $e_i\sim\mathcal{CN}(0,\nu)$, $\mathrm{Var}[w_i']=r_i=1/g_i-\nu\ge0$로 분할, $\mathbf z=\mathbf h+\mathbf e$. 그러면 $\mathbf h\to\mathbf z\to\mathbf y$가 Markov이고
$$\pi(\mathbf h)=\int\pi'(\mathbf z)\,p(\mathbf h|\mathbf z,\nu)\,d\mathbf z,\qquad \pi'(\mathbf z)\propto p_\nu(\mathbf z)\prod_{i:g_i>0}\mathcal{CN}(\upsilon_i;\zeta^z_i,r_i),$$
(정보형: $\mathbf G'=\mathbf G(\mathbf I-\nu\mathbf G)^{-1}$, $\mathbf b'=(\mathbf I-\nu\mathbf G)^{-1}\mathbf b$; $r_i=0$이면 $\zeta^z_i=\upsilon_i$ clamp; $g_i=0$이면 factor 없음). $\nabla_{\mathbf z^*}\log\pi'=(D(\mathbf z,\nu)-\mathbf z)/\nu+$(해석적 Gaussian 항) — **등방 score만으로 정확히 계산 가능.** Rao-Blackwell:
$$\mathbb E[\mathbf h|\mathbf y]=\mathbb E_{\pi'}[D(\mathbf z,\nu)],\quad \mathrm{Cov}[\mathbf h|\mathbf y]=\mathbb E_{\pi'}[\nu\mathbf J(\mathbf z,\nu)]+\mathrm{Cov}_{\pi'}[D(\mathbf z,\nu)],\quad P(k|\mathbf y)=\mathbb E_{\pi'}[w_k(\mathbf z,\nu)].$$
**귀결.** (i) $\nu_L=1/g_{\max}$까지만 anneal하면 되고(0까지 아님) 마지막은 Tweedie(1차·2차)가 정확히 마무리; within 항 $\mathbb E[\nu\mathbf J]$가 full-rank라 표본 공분산의 역행렬 문제가 없다. (ii) $\mathbf G=g\mathbf I$($T_p=N_t$, DFT): $\nu_L=1/g$에서 모든 좌표 clamp → $\mathbf z=\boldsymbol\upsilon=\mathbf q$ 결정적 → **R-A ≡ D-13+D-14 one-shot.** 즉 D-13+D-14는 "$\pi'$를 한 점 $(\mathbf q,\nu^q)$로 대체"한 근사이고 F6은 그 대체의 오차. (iii) $\mathbf G=g\boldsymbol\Pi$(첫 패스): 관측 좌표는 $\upsilon$에 clamp, 미관측 좌표는 $p_{1/g}(\mathbf z_u|\mathbf z_o)$에서 표집 = **잡음 수준 $1/g$에서의 정확한 "noisy inpainting"**; score는 $\boldsymbol\Pi^\perp s_\nu(\mathbf z)$.
**비등방 지표 [정확].** $\chi\triangleq\nu^q\,\mathrm{tr}(\mathbf G)/N\ge1$, 등호 ⇔ $\mathbf G\propto\mathbf I$ ($u_i=1/(1+g_i\nu^E)$에 Jensen: $\overline{1/u}\ge1/\bar u$). 첫 패스 12 dB: $T_p=4$ 1.00, $T_p=3$ 16.9, $T_p=2$ 32.7; aniso(−10 dB 파일럿 2개) 2.86. 용도: R-A ↔ one-shot 전환 규칙 후보(임계는 미정).
**왜 sampling인가 [추론].** EP site는 inclusive-KL 모멘트(다봉 posterior의 참 평균·공분산)를 요구; 변분/Laplace형 결정적 대안은 mode-seeking(과신 → turbo 자기강화 위험). 등방 질의 $(\mathbf q,\nu)$의 inclusive-KL 최적 조건은 $D(\mathbf q,\nu)=\mathbf m_\pi$, $\nu\,\mathrm{tr}\mathbf J=\mathrm{tr\,Cov}_\pi$ = VAMP 고정점 조건 → D-13(`n_inner`→∞)이 이미 그 한계.
**표집기 설계 [근사 bridge, 마지막 수준만 정확].** 수준 $\nu_1>\dots>\nu_L=1/g_{\max}$(기하). $\nu_l>1/g_i$인 좌표는 가상 관측 $\upsilon_i+\xi_i^{(l)}$, $\xi^{(l)}\sim\mathcal{CN}(0,\nu_l-1/g_i)$(clamp 좌표의 forward-noising 경로, chain별, 마지막 수준에서 역방향 누적)로 clamp; $\nu_l<1/g_i$는 weak 좌표(likelihood 분산 $r_i$); $g_i=0$은 자유. predictor = VE ancestral step $\zeta\leftarrow\zeta+(\nu_l-\nu_{l+1})s+\sqrt{\nu_{l+1}(\nu_l-\nu_{l+1})/\nu_l}\,n$ [유도: $\mathbf z_{l+1}|\mathbf z_l,\mathbf h$의 Gaussian 조건부에 $\mathbf h\to D$ 대입; 표준 VE ancestral step과 동일한 것으로 기억 [M]]. corrector = 좌표별 preconditioned ULA, $\epsilon_i=\delta/(1/\nu+1/r_i)$ (복소 규약: $\zeta\leftarrow\zeta+\epsilon\nabla_{\zeta^*}\log\pi+\sqrt{2\epsilon}\,n$, $n\sim\mathcal{CN}(0,1)$; Gaussian 정상분산 $c/(1-\epsilon/2c)$로 확인). NFE/chain $=(L-1)(K+1)+K_{\rm fin}$.
**보정 분석.** [정확, 1-D Gaussian] predictor 한 스텝의 분산 결손 $-\Delta^2c/(\nu_l(c+\nu_l))$, $\Delta=\nu_l-\nu_{l+1}$. [근사] corrector만 쓰는 ALD는 느린 방향이 $\nu_f\approx c\ln(\nu_1/\nu_L)/(S\delta)$에서 동결(총 스텝 $S$) → 분산 과대 ≈$\nu_f$; $S\sim300$~$600$에서 5~10% → PC 구조 채택 이유.
**검증.** (1) 폐형식(Monte Carlo 없음), GMM 16성분, rank-deficient $\mathbf G$ 포함 4 경우: $\max|w_k-w'_k|\le7\times10^{-13}$, 성분 평균 $\le10^{-13}$, 성분 공분산 $\le3\times10^{-14}$ ($\nu g_{\max}=0.999$에서 $3\times10^{-9}$). (2) clamp/weak/null 분할을 쓰는 정확 표집기(`gmm_exact_zsample`)의 혼합 가중 = 정확 $P(k|\mathbf y)$, $\le5\times10^{-14}$(aniso 포함). (3) $T_p=4$: R-A 전 구성 = D13+D14 = exact(행 일치). Monte Carlo 정확도는 exp_0923(사용자 실행 대기).
**우리 것 / prior art.** prior art: SVD 분리 + "annealing 잡음을 측정 잡음의 일부로 구성"하는 annealed Langevin = SNIPS(Kawar–Vaksman–Elad, NeurIPS 2021, arXiv:2105.14951) [V: 초록·서론 발췌만 확인, 본문 식 대조는 VERIFY]; score 기반 채널 추정 ALD = 2204.07122 Alg. 1 [V, 아래 항목]; denoiser 공분산(2차 Tweedie)을 likelihood score 근사에 쓰는 moment-matching 계열 = arXiv:2405.13712 §4.2와 그 참고문헌 [V: 발췌; 참고문헌 22–25 제목 VERIFY]. 우리 것: (a) $\nu_L=1/g_{\max}$에서 멈추고 Rao-Blackwell Tweedie 모멘트로 **EP site용 보정된 (평균, 공분산)** 을 얻는 구성, (b) D-13+D-14가 그 단일점 특수 경우라는 식별과 $\chi$ 지표, (c) turbo 수신기의 초기 패스 전용 hybrid. (a)의 선행 여부는 10-01 sweep 대상.

## [2026-09-18] 기록 — 원문 복사: arXiv:2204.07122v2 (Arvinte–Tamir) Algorithm 1, eq. (15), (17)
**원문 [V, 프로젝트 PDF 5~6쪽].** Alg. 1 — Inputs: pilot matrix $\mathbf P$, received pilots $\mathbf Y$, pretrained $s_\theta$, $\sigma^2_{\rm pilot}$, inference noise levels $\sigma^2_{z_i}$, hyper-parameters $L,M,\alpha_0,\beta,r<1$. Init $\mathbf H_{\rm est}\sim\mathcal{CN}(\mathbf 0,\mathbf I)$; for $i=1..L$: $\sigma\leftarrow\sigma_{z_i}$; for $m=1..M$: $\zeta\sim\mathcal{CN}(\mathbf 0,\mathbf I)$,
$\mathbf H_{\rm est}\leftarrow\mathbf H_{\rm est}+\alpha_0r^i\cdot\frac{(\mathbf H_{\rm est}\mathbf P-\mathbf Y)\mathbf P^H}{\sigma^2_{\rm pilot}+\sigma^2}+\alpha_0r^i\cdot s_\theta(\mathbf H_{\rm est})+\sqrt{2\beta\alpha_0r^i}\,\sigma\,\zeta$. Output $\mathbf H_{\rm est}$. 본문: $M=3$; "approximate MMSE" 기준선은 독립 실행 50개 표본의 평균; 수렴은 "first 200 steps" 빠른 단계 + 조기 종료, $\beta$는 낮출수록 빠르고 좋은 해(정지 기준에 민감).
**메모.** (i) 인쇄된 식 (17)·Alg. 1의 likelihood 항 부호는 $(\mathbf H\mathbf P-\mathbf Y)\mathbf P^H$ — 올바른 기울기는 $(\mathbf Y-\mathbf H\mathbf P)\mathbf P^H/\sigma^2$이므로 인쇄 오류로 판단[우리 판단]. (ii) 우리 표기: $\mathbf Y=\mathbf H\mathbf X_p+\mathbf W$, $\mathbf b=\mathrm{vec}$형, $\nabla_{\mathbf h^*}\log\ell=\mathbf b-\mathbf G\mathbf h$; 그들의 분모 $\sigma^2_{\rm pilot}+\sigma^2$는 $\mathbf G_l=\mathbf G(\mathbf I+\nu_l\mathbf G)^{-1}$형(정보를 **넓히는** tempering)의 스칼라판 — 우리 noise-splitting($\mathbf G'=\mathbf G(\mathbf I-\nu\mathbf G)^{-1}$, 마지막 수준에서 정확)과 방향이 반대. (iii) 그들은 점추정(표본 1개 또는 50개 평균)·$\beta<1$ 조율 → **보정된 공분산을 주지 않음**; EP site에는 그대로 못 씀. (iv) $L$, $\alpha_0$, $\beta$, $r$ 수치는 추출 텍스트에서 확인 못 함 [VERIFY, 표 II/§V].
**핸드오프 #4 §5의 [VERIFY] "2204.07122의 posterior sampling" → 확인 완료.**

## [2026-09-18] D-17 (제안, 승인 대기 — exp_0923 판독 후 확정) — Module H의 R-A 경로: noise-splitting PC 표집 + Rao-Blackwell 모멘트, $\chi$가 큰 초기 패스에서만
제안: `hsite='ra'`: $(\mathbf m,\mathrm{Cov})$ ← R-A, site $\boldsymbol\Lambda=\mathrm{Cov}^{-1}-\mathbf G$, $\boldsymbol\eta=\mathrm{Cov}^{-1}\mathbf m-\mathbf b$(D-14·`ep_site`와 같은 하류 인터페이스). $\chi\le\chi_0$이면 기존 D-13+D-14(비용 0). 기본 $(M,L,K)$와 $\chi_0$는 exp_0923 + turbo 통합 실험(세트 C, $T_p=2$, n≥640, 목표 = `exactEP_pf` 재현) 후 결정. 코드: `Demo/t2_ra_sampler.py`(신규; `t2_route_a.py`는 무변경).

## [2026-09-18] 기록 — exp_0923 판독 (사용자 실행, 커밋 6f19360; GMM 4x4 첫 패스, n=1000, 25초) + raw 재분석
**사전 등록 기준 대비 [측정].** (1) $T_p=4$ 전 행 일치 ✔. (2) 정확 표집기 `PS-M32`: NMSE exact 대비 +2.1~3.5%($T_p=2,3$ 전 점; 기준 ≤+4%) ✔, KL/N $T_p=2$ .090/.114/.126 vs D13+D14 .382/.380/.358 ✔; `PS-M128` +0.2~1.1%, KL/N .005~.023; 정확 표집기 가중 = exact $\le8\times10^{-12}$. **→ 항등식 + Rao-Blackwell 추정기는 작동하며 $M=32$면 Monte Carlo 바닥이 충분히 낮다.** (3) **미달.** `RA-M32-L24-K4`(NFE 123): $T_p=2$ NMSE +10.5/+13.7/+13.6% vs D13+D14 +14.7/+17.4/+15.1% → 격차 회수 29/21/10%(기준 ≥2/3); $T_p=3$ 12·18 dB에서는 D13+D14보다 **나쁨**(+11.6/+15.9 vs +10.3/+11.4%). `RA-M32-L48-K8`(NFE 439)도 51/56/40% → 미달. KL/N은 PS-M32의 1.65배(L24K4)·1.2~1.3배(L48K8)로 KL 기준만 충족. **→ 사전 규칙대로 "표집기 재설계".** (4) `-J1` = all-J(KL/N 차이 0~4%) ✔ → **Rao-Blackwell 단계의 Jacobian은 chain 1개로 충분.**
**그 밖의 측정.** (a) $M=8$은 공분산 불능($T_p=2$ KL/N .85~8.7). (b) aniso($\chi\approx2.5$~$3$): D13+D14가 이미 +0.1~2.1%, KL/N .0006~.016 — $M=32$ 표집(+2.3%, KL/N .06~.08)이 오히려 나쁨 → **$\chi$ 전환의 근거: $\chi\lesssim3$이면 one-shot.** aniso에서 RA ≈ PS(.0732 vs .0735) → weak 좌표 경로는 정상, 편향은 **null 공간 표집**에 국한. (c) v1 편향은 SNR과 함께 커지고 $(L,K)$에 느리게 수렴; `w_true` .56~.59(L24K4), .61~.66(L48K8) vs exact .67~.77; $P_{\rm map}$은 exact에 근접(.73~.81 vs .76~.84); site clip 86~92%(L24K4; exact 40~47%) = 과분산의 서명.
**raw 재분석 (one-shot 인터페이스가 참 성분을 맞혔는지로 조건화).** $T_p=2$에서 one-shot $P_{\rm map}$ 정답률 41~45%. *정답군* NMSE: exact .220~.251 / D13+D14 .229~.261 / PS-M32 .226~.256 — **D13+D14 ≈ exact.** *오답군*: exact .546~.586 / **D13+D14 .664~.696(+19~22%)** / PS-M32 .562~.604 / RA-L48K8 .591~.629. KL/N 분위(50/90/99%), 12 dB: D13+D14 .23/**.94/1.38**, PS-M32 .11/.16/.23, RA-L48K8 .14/.21/.30. 부호 검정($T_p=2$ 12 dB): D13+D14 vs PS-M32 579:421($p=7\times10^{-7}$), vs RA-L48K8 544:456($p=.006$); $T_p=3$은 전부 동률(차이는 꼬리에서만).
**해석.** F6의 손실은 "평균적으로 조금 나쁨"이 아니라 **성분 오식별 시의 확신에 찬 오답(무거운 꼬리)** — turbo 자기강화에 가장 위험한 형태[추측: BLER 인과는 미측정]. R-A의 가치는 꼬리 제거. v1 표집기의 편향은 전 시행에 걸친 넓은 확산(w_true 결손 .05~.15).
**v1 편향의 원인[추측 → exp_0924에서 분리].** replacement형 bridge는 수준 $l$에서 $p(\mathbf z_u^{l}|\mathbf z_o^{l})$(잡음 섞인 관측 좌표 조건)을 표적으로 하나 올바른 표적은 $p(\mathbf z_u^{l}|\boldsymbol\upsilon)$(깨끗한 관측 조건): 성분 선택이 일어나는 굵은 수준에서 관측 정보를 과소 사용 → 성분 빈도가 확산. 마지막 수준의 corrector는 조건수 $\sim c_{\max}/\nu_L\approx470$(12 dB)~$1900$(18 dB) ($c_{\max}=7.42$)이라 $K_{\rm fin}=8$로는 교정 불가[근사].

## [2026-09-18] 기록 [정확(Gaussian) + 폐형식 검증] — R-A v2 bridge: posterior diffusion + 정확 handover
**구성.** fresh-noise 확산 $\mathbf z^l=\mathbf h+\mathbf n_l$, $\mathbf n_l\sim\mathcal{CN}(\mathbf 0,\nu_l\mathbf I)$ ($\mathbf y$와 독립). [정확] $p(\mathbf z^{l+1}|\mathbf z^l,\mathbf h)=\mathcal{CN}(a\mathbf z^l+(1-a)\mathbf h,\ \nu_{l+1}(1-a)\mathbf I)$, $a=\nu_{l+1}/\nu_l$ ⇒ $p(\mathbf h|\mathbf z^l,\mathbf y)\approx\mathcal{CN}(\mathbf m_+,\mathbf S_+)$이면
$$\mathbf z^{l+1}\,|\,\mathbf z^l,\mathbf y\sim\mathcal{CN}\big(a\mathbf z^l+(1-a)\mathbf m_+,\ \nu_{l+1}(1-a)\mathbf I+(1-a)^2\mathbf S_+\big).$$
posterior denoiser 3종: **X** 정확 mixture(GMM 전용; 이산화 오차만 분리), **J** $p(\mathbf h|\mathbf z^l)\approx\mathcal{CN}(D,\nu\mathbf J)$ × 정확 likelihood: $\mathbf S_+=(\mathbf I+\boldsymbol\Sigma\mathbf G)^{-1}\boldsymbol\Sigma$, $\mathbf m_+=(\mathbf I+\boldsymbol\Sigma\mathbf G)^{-1}(D+\boldsymbol\Sigma\mathbf b)$, $\boldsymbol\Sigma=\nu\mathbf J$ (**= 매 스텝의 D-14 연산**), **S** $\boldsymbol\Sigma=\nu\frac{\bar c}{\bar c+\nu}\mathbf I$(Jacobian 없음).
**handover [정확: clamp·null 좌표].** $\nu_L=1/g_{\max}$에서 null 좌표의 $\mathbf e_u$는 관측 잡음의 일부가 아니므로 fresh-noise 표본의 $\mathbf z_u$ 주변분포 = $\pi'_{\nu_L}$의 $\mathbf z_u$ 주변분포; clamp 좌표는 $\upsilon$로 설정. weak 좌표만 근사 → 정확 표적 corrector $K_{\rm fin}$ 스텝으로 수리. 이후 Rao-Blackwell 모멘트는 v1과 동일.
**검증(폐형식, Monte Carlo 없음).** Gaussian prior(K=1): X·J의 $(\mathbf m_+,\mathbf S_+)$ = 정확 $p(\mathbf h|\mathbf z,\mathbf y)$ 모멘트 $\le4\times10^{-14}$; ancestral 재귀로 전파한 $\mathbf z^l$의 (평균, 공분산) = 정확 noised posterior $\mathcal{CN}(\mathbf m_\pi,\mathbf S_\pi+\nu_l\mathbf I)$, **모든 수준·$L=2$ 포함** $\le5\times10^{-14}$ ⇒ **v2-J는 Gaussian prior에서 스텝 크기와 무관하게 정확**(v1에는 없던 성질). v1 회귀: exp_0924의 `RA-M32-L24-K4` 행이 exp_0923 raw와 $\le10^{-14}$ 일치(n=2 smoke).
**우리 것 / prior art.** J형은 moment-matching posterior sampling 계열(arXiv:2405.13712 §4.2 [V: 발췌])과 같은 근사족 — prior art. 우리 것: (a) 그 위에 noise-splitting 정확 handover + Rao-Blackwell 모멘트를 붙여 **EP site용 보정 모멘트**로 쓰는 것, (b) "매 스텝 = D-14 연산, one-shot D-13+D-14 = 단일점" 이라는 식별, (c) 오식별 꼬리(조건부 분석)라는 F6의 실패 양상 측정.

## [2026-09-18] D-17 상태 갱신 — **보류 유지.** v1 표집기는 사전 기준 미달로 기각(ablation·회귀용으로 코드 유지). v2는 exp_0924 판독 후 재심.
exp_0924 사전 등록 기준: (i) `PSinit-K16/K128` ≈ `PS-M32`(NMSE ±1%p, KL/N ±10%) → 마지막 수준 corrector 무편향. (ii) `RA2X-L12`가 $T_p=2$에서 NMSE ≤ exact×1.06 → 이산화는 $L\le12$로 충분. (iii) **`RA2J-L12`가 $T_p=2$에서 D13+D14 대비 NMSE 격차의 ≥2/3 회수 + KL/N ≤ PS-M32×1.5 + KL 99% 분위 ≤ D13+D14의 1/3** → D-17 승인 제안 + turbo 통합. (iv) `RA2S`가 (iii)을 충족하면 bridge에서 Jacobian 제거. (iii) 미달·(ii) 충족이면 손실은 Gaussian guidance 근사 → 다중 가설/SMC류 검토 또는 R-A 포기 후 F6을 "정량화된 한계"로만 보고.

## [2026-09-18] 기록 — exp_0924 판독 (사용자 실행, 커밋 06c28ca; GMM 4x4 첫 패스, n=1000, exp_0923과 paired, 30초)
**사전 등록 기준 대비 [측정].** v1 회귀: 전 셀 $0.0$ ✔. (i) `PSinit-K16/K128` ≈ `PS-M32`(NMSE +2.0~3.9% vs +2.1~3.5%, KL/N ±3%) ✔ → **마지막 수준 corrector는 무편향.** (ii) `RA2X`: $T_p=2$ NMSE +5.1/+5.0/+3.6%(L12), **L6(NFE 5)에서도 +5.1/+4.9/+3.9%**, KL/N .094/.118/.136 ≈ PS(.090/.114/.126), w_true .665/.751/.766 ≈ exact ✔ → **bridge 구조·이산화는 문제가 아님; 정확 posterior denoiser가 있으면 5스텝이면 충분.** (iii) **미달 — 그것도 one-shot보다 나쁨.** `RA2J-L12` $T_p=2$: NMSE **+19.2/+20.7/+19.7%** vs D13+D14 +14.7/+17.4/+15.1%; KL/N .239/.260/.268(one-shot .382/.380/.358보다는 낮음), KL 99% .55/.58/.63 vs 1.26/1.38/1.43(비 .42~.44 > 기준 1/3), **KLc/N(site clip 왕복 후) .402/.513/.547 vs one-shot .382/.380/.358 — 수신기가 보는 값으로는 one-shot보다 나쁨**; clip 94~95%. $L$=24(+18.0/+19.6/+18.9), $K_{\rm fin}$=8, $M$=128(+16.7/+18.3/+17.4) 모두 무효. $T_p=3$: +14.9/+24.7/+23.8 vs one-shot +8.4/+10.3/+11.4. aniso: +10.6/+4.0/+3.4 vs +2.1/+0.3/+0.1. (iv) `RA2S`는 J보다 더 나쁨(+24~26%) ✘.
**부수 측정(Q-31).** 표본 모멘트 site의 clip 손실: PS-M32 KL→KLc는 $T_p=2$에서 작지만(.114→.122) aniso 고SNR에서 큼(.084→**.502** at 18 dB; exact 자신은 .0006). v1 `RA-M32-L24-K4`의 KLc는 $T_p=2$ .221/.374/.452 — 12·18 dB에서 one-shot(.380/.358)보다 낫지 않음.
**결론[측정 + 추론].** 손실 전부가 **Gaussian(모멘트 정합) guidance 근사**에서 나온다: X(정확 mixture posterior denoiser)는 5스텝으로 PS에 도달, J는 one-shot보다 나쁨. J가 쓰는 정보 = 한 점 $(\mathbf z,\nu)$에서의 등방 denoiser 평균 + Jacobian = D-14와 같은 정보 → 비등방 likelihood 하의 성분 evidence를 복원할 수 없음. 즉 **F6은 one-shot 인터페이스의 결함이 아니라 "등방 score + 2차(Gaussian) closure"의 정보적 한계**이며, 제거하려면 (a) 비등방 likelihood의 tilted 모멘트를 폐형식으로 주는 prior 표현(GMM) 또는 (b) 고비용 표집(v1: NFE 439×32 chain에서 NMSE 격차 40~56% 회수, 학습 score에서는 오차 누적 추가)이 필요. (정리 아님; GMM testbed 4x4 첫 패스에서의 측정.)

## [2026-09-18] D-17 철회(제안 → 기본값 적용, reversible) — R-A(표집 기반 Module H) 중단
이유: (1) v1은 사전 기준 미달(exp_0923), v2-J/S는 one-shot보다 나쁨(exp_0924) — 사전 등록된 분기 "(iii) 미달·(ii) 충족 → R-A 포기 후 F6을 정량화된 한계로 보고"에 해당. (2) v2-X가 작동하려면 mixture posterior denoiser가 필요 = 매개변수 prior가 있다는 뜻이고, 그러면 표집 없이 `ep_site`가 정확 site를 준다. (3) SMC/twisted류는 밀도 또는 추가 근사가 필요하고 학습 score의 오차 누적까지 고려하면 $N=16$~$32$ 영역에서 H-GMM(D-18)을 이길 전망이 낮음[추측]. 유지: `t2_ra_sampler.py`(항등식·RB 추정기·사다리 = F6 분석 도구), noise-splitting 항등식 [정확], 오식별 꼬리 측정. 억지로 (L,K,M)을 키워 맞추지 않는다.

## [2026-09-18] D-18 (사용자 승인 "H는 넣자") — Module H-GMM: 채널 dataset에 GMM 적합 → 정확 mixture EP site (`exact_prior=True`)
baseline 겸 대안 Module H. 구현: `GMMPrior.fit`(EM, zero-mean 복소 성분, full covariance, $K\in\{16,32,64\}$) → `RouteA(mode='colored', exact_prior=True, feedback='posterior', beta=0.7)`(기존 `exactEP_pf` 경로 그대로). prior art: GMM 기반 CME = Koller–Fesl–Turan–Utschick, IEEE TSP 2022 [V: 초록]; 우리 것은 그것을 bilinear turbo 수신기의 EP site로 쓰는 것(선행 여부 VERIFY — 10-01 sweep 최우선).

## [2026-09-18] D-19 (제안, 승인 대기) — 중단 기준(kill test)을 M2 학습 **이전**에 실행: exp_0925
**동기(사용자 질문: "baseline을 못 넘으면 중단이 맞지 않나").** 동의. 단 (i) 어느 baseline을 (ii) 어떤 여유로 (iii) 무엇을 중단하는지 사전 등록한다. score network를 학습하기 전에 판정 가능: **정확 score**는 어떤 학습 score보다도 유리한 상한이므로, "정확 score + one-shot 인터페이스(D13+D14)"가 "유한 표본에 적합한 GMM + 정확 site"를 못 이기면 score 분기는 학습 없이 기각된다.
**설계.** 참 prior = 연속 각도 혼합(송·수신 각도 $\psi_t,\psi_r$ 연속 균등 → 조밀 격자 $K_{\rm true}=32\times32$ 성분 GMM으로 *정의*; 유한 $K$ GMM으로 정확 표현 불가). 두 종류: **U**(전 각도 균등; 앙상블 공분산 $=\mathbf I$ → 비Gaussian prior에 최대로 유리), **S**(섹터 ±60° 제한; 앙상블 공분산이 정보를 가짐 → 현실 쪽). arm(모두 D-15+LOO, $\beta=0.7$, 16반복): (a) `lmmseC_pf` 표본 공분산 Gaussian prior, (b) `Hgmm-K{16,32,64}` ($N_{\rm train}=10^4$ 표본 EM 적합), (c) `Hscore-exact` 참 prior의 정확 score + D13+D14, (d) `exactEP-true` 참 prior 정확 site(모든 방법의 상한), pilot-only·genie. 영역: 4x4 $T=28$ $T_p=2$(exp_0921 C와 비교 가능) + **8x4 $T=16$ $T_p=2$(headline)**, n≥640.
**기준(사전 등록).** **K1:** prior S·headline 영역에서 상한 (d)가 (a) 대비 SNR@BLER 0.1 이득 < 0.5 dB → "학습 prior" 기여 무효 → **T2를 현 설계대로는 중단 제안**(D-15+LOO·regime 결과는 T1로 이관, lemma는 note로 보존). **K2:** (c)가 (b, $K$=32)를 paired sign test($p<.05$, SNR 3점 중 2점)로 이기지 못함 → **score prior 분기(M2 score model, D-13/D-14 묶음의 기여 ②) 중단**; 남는 선택지 = "GMM-prior EP turbo 수신기"로의 전환인데 이는 Utschick 그룹 선행 조사 후에만 결정. **K3:** (c) > (b) → M2 진행.
**사전 예상[추측].** K2 발동 가능성이 높다: 무선 채널은 대규모 기하 조건부 Gaussian이라 GMM이 구조적으로 맞고, 비등방 likelihood의 tilted 모멘트가 폐형식인 반면 score prior는 F6을 안고 간다. score/diffusion prior의 자리는 GMM 적합이 불가능한 고차원(대규모 배열·광대역)일 가능성 — 8x4 짧은 패킷 영역 밖.

---

## [2026-09-18] D-19 승인 (사용자 "Continue", 세션 6 첫 턴) + 보정 R1~R7 — exp_0925 kill test 확정
"Continue" = 제시한 기본값 채택(세션 3 관례와 동일). 의도와 다르면 "보류" 한마디로 되돌린다. D-19 본문(위 2026-09-18 항목)은 그대로 유효하며, 아래 보정만 추가한다. **모든 보정은 BLER을 한 번도 보기 전에 확정**(사전 등록).
- **R1 (prior 정의 확정).** D-19의 "섹터 ±60°"가 모호했다 [세션 6 유도, 정확]. **전기각** 해석($\psi\in[-\pi/3,\pi/3]$, $\lambda/2$ ULA에서 물리 ±19.5°)이 D-19 원문이며 앙상블 공분산이 정보를 가진다(8×4 유효 rank 12.6/32). **물리각** 해석($\theta\sim U(\pm60°)$, $\psi=\pi\sin\theta$)은 앙상블 공분산이 거의 백색(유효 rank 31.6/32)이라 D-19의 전제가 성립하지 않는다. → prior 3종: **U**(전 범위 균등, 앙상블 $=\mathbf I$ [정확]), **S**(전기각 ±π/3 = D-19 원문, **K1 결정 셀**), **P**(물리 120° 섹터, 맥락·범위 판단용). 참 prior는 세 경우 모두 $K_{\rm true}=32\times32$ 격자 혼합으로 *정의*.
- **R1b (범위 한정 분기, 원문보다 관대).** K1이 (H, S)에서 발동하더라도, prior P에서 **교차-$T_p$ goodput 포락선** 이득(exactEP-true vs 2차 모멘트 포락선)이 연속 3개 이상 SNR 점에서 ≥5%이면 결론은 "중단"이 아니라 **주장 범위 한정**(앙상블 공분산이 정보를 갖지 않는 채널로 한정)으로 한다.
- **R2 (H4 셀 추가).** $T_p=2$·$\mathbf R_{t,\rm ens}=\mathbf I$(prior U/P)에서는 2차 모멘트 방법의 첫 패스 $\mathrm{NMSE}_\infty=1-T_p/N_t=0.5$ [정확, F5 폐형식] — 같은 $T_p$에서 (d)−(a)를 비교하면 공허하다. 따라서 8×4·$T=16$·$T_p=4(=N_t)$ 셀을 추가하고, headline은 **교차-$T_p$ goodput 포락선**($K/T$: $T_p=2$ 3.125, $T_p=4$ 2.625)으로도 읽는다.
- **R3 (arm (b) 강화 — 우리 논지에 불리한 방향).** full-covariance EM은 $N=32$, $n=10^4$에서 과적합한다 [측정, 적합 단계만]. → (i) MAP shrinkage $\kappa\in\{0,16,64,256\}$, (ii) 검증 우도 early stopping, (iii) 성분별 Kronecker 구조 $\mathbf C_k=\mathbf T_k\otimes\mathbf R_k$(flip-flop M-step). **선택은 오직 검증 우도**로 하며 BLER을 보지 않는다. **b\*** := 검증 우도 최대인 Hgmm arm. **K3는 (c)가 원문 `Hgmm-K32`와 `b*`를 둘 다 이겨야 성립.**
- **R4 (clip 규칙 확인).** site clip 후 $\boldsymbol\eta$ 보존(현 코드)은 belief 평균을 tilted 평균에서 이동시킨다; 정밀도 고정 시 KL 최적은 평균 보존 [정확]. 진단 arm `-mp`를 병행하고, `-mp` 쌍의 판정이 다르면 **미결**로 둔다.
- **R5 (K1 불확실성).** SNR@BLER 0.1 이득의 90% paired bootstrap CI가 0.5 dB를 걸치면 미결 → $n$ 증량.
- **R6·R7 (검정력 하한, 신규).** K2는 "반대 결과를 탐지할 수 있었을 때"만 발동한다: 격자 위에 결정 점 3개가 존재하고(R7), 그중 2개 이상에서 불일치 쌍이 6개 이상(R6; 양측 sign test가 $p<.05$에 도달할 수 있는 최소값)이어야 한다. 미달이면 **미결**(n 증량 또는 SNR 격자 확장). 결정 점 = `Hgmm-K32`의 BLER@16이 0.1에 $|\log_{10}|$ 기준으로 가장 가까운 3점([0.005, 0.9] 내).
판정은 `exp_0925_analysis.py` §5가 기계적으로 계산한다(보조 자료; 최종 판독은 사람이 한다).

## [2026-09-18] 기록 [정확, 폐형식] — 세션 6 유도 1: prior S/P의 앙상블 2차 모멘트와 첫 패스
격자 혼합 prior의 앙상블 공분산은 $\hat{\mathbf C}=\mathbf R_{t,\rm ens}^{\rm T}\otimes\mathbf R_{r,\rm ens}$, $\mathbf R_{\cdot,\rm ens}=\frac1{K_g}\sum_a \mathbf R(\psi_a)$ [정확; 격자 지수 독립]. 수치(성분 $\rho_c=0.7$, $K_g=32$):
- **U:** $\mathbf R_{t,\rm ens}=\mathbf R_{r,\rm ens}=\mathbf I$ (오차 $\le5\times10^{-16}$) — 2차 모멘트가 정보를 전혀 갖지 않음.
- **S(전기각):** eig $\mathbf R_{t,\rm ens}$ = 2.123/1.185/0.456/0.236; $\mathbf R_{r,\rm ens}$(8) = 2.358…0.204; 유효 rank 6.7/16(4×4), 12.6/32(8×4).
- **P(물리 120°):** $\mathbf R_{t,\rm ens}=\mathbf I$, eig $\mathbf R_{r,\rm ens}$ = 1.114…0.735 — 거의 백색(유효 rank 31.6/32).
$T_p=2$ 첫 패스 $\mathrm{NMSE}_\infty=\mathrm{tr}\,\mathbf S/\mathrm{tr}\,\mathbf R_t$ (F5 폐형식): U·P는 DFT에서 0.500(파일럿 포착 전력 0.500), S는 DFT 0.233 → **eig 파일럿 0.173**(포착 0.827). → 파일럿 규칙: S만 eig, U·P는 DFT(eig가 무의미).

## [2026-09-18] 기록 [정확] — 세션 6 유도 2: EP site clip의 평균 보존
moment-matched $(\mathbf m,\boldsymbol\Sigma)$에서 site를 $\boldsymbol\Lambda=\boldsymbol\Sigma^{-1}-\mathbf G$, $\boldsymbol\eta=\boldsymbol\Sigma^{-1}\mathbf m-\mathbf b$로 만든 뒤 $\boldsymbol\Lambda$의 고윳값을 $\lambda_{\min}$으로 clip하면, **$\boldsymbol\eta$를 보존하는 현 규칙**의 belief 평균은 $(\boldsymbol\Lambda_c+\mathbf G)^{-1}(\boldsymbol\eta+\mathbf b)\ne\mathbf m$이 된다. 정밀도 $\mathbf P=\boldsymbol\Lambda_c+\mathbf G$를 고정하면 $\mathrm{KL}(\mathcal{CN}(\mathbf m,\boldsymbol\Sigma)\,\|\,\mathcal{CN}(\boldsymbol\mu,\mathbf P^{-1}))$는 $\boldsymbol\mu=\mathbf m$에서 최소 ⇒ **평균 보존** $\boldsymbol\eta=(\boldsymbol\Lambda_c+\mathbf G)\mathbf m-\mathbf b$가 KL 최적 [정확]. 무작위 $(\mathbf G,\mathbf b)$ 점검에서 상대 평균 이동 $|\boldsymbol\mu-\mathbf m|^2/|\mathbf m|^2$ = 0.04~0.09(8×4, clip 6/8회) [측정, 코드 점검]. 수신기 성능 영향은 **미측정** → exp_0925의 `-mp` arm(Q-34).
적용 범위: `GMMPriorB.ep_site`(정확 site 경로)와 `RouteAClip._matrix_site`(D-14 경로) 둘 다. `clip='eta'`가 기존 `RouteA`와 로그 완전 일치(차이 0.0)임을 단위 테스트 T6로 고정.

## [2026-09-18] 기록 [측정, 적합 단계 한정] — 세션 6: full-covariance EM의 과적합과 대안
prior S, 8×4($N=32$), $n_{\rm train}=10^4$, $n_{\rm val}=n_{\rm test}=5000$, plain EM($\kappa=0$, 300회 상한, restart 1): $K=16$ train−val 격차 2.07 / KL(true‖fit) 1.45; $K=64$ 격차 **8.00** / KL **4.21**; Gaussian 표본 공분산 prior KL 9.72. 4×4 $K=32$: 격차 1.39 / KL 0.69. → 성분당 $N^2$ 복소 자유도가 $n/K$ 표본을 압도. (b)가 허수아비가 되면 K3가 잘못 발동할 수 있으므로 R3 도입. EM 구현 [정확]: $\sum_k\pi_k\mathbf C_k$ = 표본 공분산($\kappa=$ floor $=0$일 때 단위 테스트 $\le10^{-12}$), Kronecker M-step은 가중 matrix-normal MLE(단위 테스트: $K=1$에서 LL(full)≥LL(kron)≥LL(true), 계수 오차 $O(n^{-1/2})$), $\kappa\to\infty$에서 $\mathbf C_k\to\hat{\mathbf C}$.

## [2026-09-18] 기록 — 세션 6: exp_0925 코드 작성 완료(실행 대기), `t2_route_a.py` 무변경
신규 `Demo/t2_gmm.py`(`GMMPriorB` 배치 1024성분 `ep_site`/`denoise_full`, `RouteAClip`, `fit_gmm_em`, U/S/P 생성기), `exp_0925_run.py`(`prior`/`fit`/`time`/`K`), `exp_0925_analysis.py`, `exp_0925_tests.py`. **`t2_route_a.py`·`t2_trellis.py`는 건드리지 않았다**(회귀 테스트 t0/t6 보호). 단위 테스트 전 항목 PASS(T1 tilted 모멘트 $\le6\times10^{-12}$, belief 수준 $\le10^{-9}$; T2 $\le5\times10^{-14}$; T3 EM 항등식·복원; T3k Kronecker; T4 prior 정의; T6 `RouteAClip`=`RouteA` 차이 0.0). 스모크($n\le4$, 수치 폐기)로 fit→K→analysis 전 경로 확인, 산출물 삭제. 비용 추정: 셀 H 4.2 s/trial, R 1.9 s/trial → 51점×$n$=640에서 192코어 약 11~12분; fit 약 1~2분.

## Experiment log

```
exp_0915 | 목적: lemma 수치 검증 (BCJR vs brute force, Tweedie/Jacobian 항등식, factor-2, Max-Log, puncturing, 16-QAM 근사 오차)
설정: (7,5)_8 nu=2 K=10 (N=24) 및 (133,171)_8 nu=6 K=8 (N=28); sigma^2 ∈ {0.05,0.3,1,3,10}; 16-QAM Gray (7,5)_8 K=10, 6 symbols/block, tau ∈ {0.05,0.2,0.5,1,2}, 20 trials
결과: BCJR=brute force max |tanh(L/2)-E[x|x~]| ≤ 3e-15; score(FD) ≤ 7e-10; Jacobian=Cov/sigma^2 ≤ 1.3e-10; diag=(1-tanh^2)/sigma^2; div=v_post/sigma^2;
      complex: Lc=4/sigma_c^2 정확, Lc=2/sigma_c^2 오차 0.495 (sigma_c^2=3); Max-Log 오차 최대 0.78; puncturing-as-erasure 정확(전송·천공 심볼 모두);
      16-QAM symbol-level BCJR 정확(3e-15); bit pipeline NMSE 2e-5(tau=0.2) → 3.5e-2(tau=1) → 2.7e-2(tau=2), 입력측(BICM bit metric) 1.9e-2 / 출력측(product of marginals) 3.2e-2 at tau=1
시드: 20260915 | 코드: exp_0915_bcjr_score_check.py | 결론/후속: lemma (a)-(d) 수치 통과; Q-02 판단 자료 확보
```

```
exp_0916 | 목적: (133,171)_8 nu=6 super-section BCJR 모듈 검증 (16-QAM 주, QPSK/64-QAM 보조), 복소 Tweedie·Wirtinger Jacobian, tilted prior, 비트 파이프라인 ablation, 비용
설정: K=12 (9 심볼, 4096 codeword) tau ∈ {0.05,0.2,0.5,1,2,5} 4 trials; K=16 (11 심볼, 65536 codeword) tau=1; QPSK K=12; 64-QAM K=12; 비용 K=200
결과: P_n, x̄_n, v_n, 비트 marginal, tilted prior 모두 brute force와 ≤ 7e-15; 복소 Tweedie ≤ 1.4e-9 (FD); Jacobian=(E[x_n x_j*]-x̄_n x̄_j*)/tau ≤ 4e-10; diag=v_n/tau; div=mean(v)/tau;
      비트 파이프라인 NMSE: 16-QAM 1.3e-5(tau=0.2)/8.7e-3(0.5)/5.2e-2(1)/2.6e-2(2)/1.3e-2(5), max 0.52, |dv| 0.21 at tau=1; QPSK 1e-30; 64-QAM 2.1e-2(0.5)/1.7e-2(2);
      wall-clock K=200: super-section 0.62 s vs 비트 BCJR 1.91 s (numpy 루프)
시드: 20260916 | 코드: t2_trellis.py, exp_0916_superbcjr_133171_qam.py | 결론/후속: Lemma 2 (a')-(d') 수치 통과; D-05 근거; Q-13 [VERIFY] Sionna 라벨링
```

```
exp_0917 | 목적: 채널 denoiser Onsager 계수 추정법 비교 (Q-05) + 복소 Fisher 공식 검증
설정: Gaussian prior CN(0, R_r⊗R_t), rho=0.7, N_r×N_t ∈ {8×4, 8×8, 32×32}, nu ∈ {0.01,0.1,0.3,1}, draws 2000/1000/200
결과: F1 mean = alpha_exact (공식 검증); std(alpha_hat): F1 0.015–0.13 (8×4), 0.011–0.09 (8×8), 0.013–0.025 (32×32); Hutchinson K=16: 0.017–0.042 (8×4);
      v_ext 상대오차 (8×4): F1 28–63 %, H16 8–25 % (nu=0.01에서 H 발산); 정확 trace = 2N 방향미분, 분산 0
시드: 20260917 | 코드: exp_0917_onsager_small_N.py | 결론/후속: D-09 제안; Q-05 절반 닫힘
```

```
exp_0918 | 목적: route (a) v0 결합 검증(Gaussian Kronecker prior, 학습 없음): sanity(등방 prior→H extrinsic=prior), 궤적, 기준선, D-10 ablation
설정: 4x4, T=28, Tp∈{4,2}, BPSK (133,171)_8 nu=6 terminated 1 codeword/block (K=42/46), symbol interleaver, DFT pilots, rho∈{0,0.7}, SNR=1/σ²∈{0,3,6,9,12} dB,
      8 반복, 80 trials(T2)/60(T3), damping 없음, ε=1e-6, ν_max=1e4; 모드 scalar/colored/pilot_only/genie
결과: T0 회귀: BitTrellis=bcjr_bits 7e-15; 비트별/심볼별 τ BCJR = brute force ≤2e-15(사후), 정보 LLR ≤7e-14. T1 sanity(ρ=0): ‖Ĥ^E‖=0, |ν^E−1|≤1.3e-14, scalar≡colored ≤7.6e-13.
      T2 Tp=4 6 dB: NMSE 0.061→0.018(2회 반복 수렴), τ^L 0.95→0.134→0.11 (L_c 4→30→36), ν^q 0.063→0.0116→0.0101, α^H→0.947, ν^E→0.18;
         BLER scalar 0.03 = colored 0.03 = pilot_only 0.03, genie 0.00 (0 dB: 0.20/0.19/0.28/0.01; 3 dB: 0.06/0.07/0.10/0.00).
      T2 Tp=2 6 dB: scalar BLER 0.93→0.19 (NMSE 0.264→0.100), colored 0.80→0.14 (0.235→0.085), pilot_only 0.46, genie 0.00; τ^L 3.1→1.0→0.45→0.26→0.20→0.18 (5~6단계 annealing);
         9 dB: 0.16 (NMSE 0.117) / 0.05 (0.021) / 0.38; 12 dB: 0.06 / 0.05 / 0.29. 비단조 NMSE step: Tp=4 2.5%, Tp=2 13%(scalar), 9%(colored).
      T3 D-10: form B는 4점 모두 나쁨 — Tp=4 3 dB NMSE 0.040 vs 0.065, BLER 0.05 vs 0.13; Tp=2 3 dB 0.158 vs 0.345, 0.30 vs 0.57.
      실패 모드: F1 scalar site가 첫 반복에서 prior 등방화 → Tp<Nt에서 느린 시작·정체; F2 α^D가 clip ε에 닿으면 NMSE 주기-2 소진동(~5%); F3 scalar에서 후반 NMSE 점프(Tp=4 6 dB 0.019→0.027, trial 5%; T3 재현);
                 F4 pilot_only Tp=2에서 일부 스트림 extrinsic precision 0 → τ^L clip. NMSE 평균은 복호 실패 블록의 heavy tail에 민감(median 병행 필요).
시드: 20260918 | 코드: t2_route_a.py, exp_0918_route_a_gaussian.py, t2_trellis.py(확장) | 결론/후속: 결합 버그 없음(T0/T1); M3 완료 조건 중 "BLER < pilot-only" 충족(0/3 dB, Tp=2 전 구간), "NMSE 단조"는 조건부(Tp=4 97.5% step);
                 D-10 확정 제안; Q-07 스칼라화 손실 정량화(Tp=2에서 큼) → F1 원인 분리(exp_0918b) 후 D-11(M2 colored-noise 조건화) 판단
```

```
exp_0918b | 목적: F1(scalar site 등방화)·F3(후반 NMSE 점프) 원인 분리; damping·ε 효과
설정: exp_0918과 동일 trial(시드 SEED+106/109), Tp=4 6 dB (T4a/T4c), Tp=2 6·9 dB (T4b); 변형 scalar / cinit1(첫 1회 colored) / colored × β∈{1,0.7}; ε∈{1e-6,1e-3}
결과: T4a: 점프 trial 2/80 = 처음부터 실패한 블록의 주기-2 cycle(colored도 2/80 동일); 성공 블록 NMSE scalar=colored=0.0116; α^D clip 도달 95% 반복, NMSE 부호 교대 60%(F2).
      T4c: β=0.7 → 점프 0/80, BLER 0.025→0.000 (수렴 5회); ε 무관.
      T4b 6 dB BLER: scalar .188 / cinit1 .150 / colored .138 ; β=.7: .163 / .087 / .100 ; 성공 블록 NMSE median 모두 .0093~.0096
           9 dB BLER: .163 / .075 / .050 ; β=.7: .087 / .037 / .013 ; 성공 블록 NMSE .0047~.0048 ; ν^q 정상값 ≈ σ²/T (9 dB .0052)
시드: 20260918 | 코드: exp_0918b_f1_isolation.py, t2_route_a.py(init_colored) | 결론/후속: Q-18 닫힘(F3 = 실패 블록 cycle, damping으로 해결); F1 = 시작 문제 → D-11; D-12 damping 기본값; M-1 측정 규약
```

```
exp_0919 | 목적: QPSK(Lemma 2 경로)로 route (a) 재확인; SymbolTrellis.bcjr 벡터화; L_H→H 등방화 규칙(site vs belief)·D-11·damping 비교; ν^q 표(Q-16)
설정: 4x4, T=28, Tp∈{4,2}, QPSK (133,171)_8 nu=6 terminated (K=90/98), rho=0.7, SNR=1/σ²∈{0,3,6,9,12,15} dB, 8 반복, β∈{1,0.7}, n=80(스캔)~320(결정 지점),
      변형 scalar(v0)/cinit1(D-11)/belief1·belief3(D-13, n_inner)/colored/pilot_only/genie; 같은 점의 모든 변형은 동일 (H,u,perm,Y); 시드 20260919+100+SNR
결과: T0 벡터화 BCJR = brute force ≤1.6e-15 (QPSK/16-QAM/64-QAM, 심볼별 τ, tilted prior), 정보 LLR ≤1.4e-14, 루프 구현과 ≤7.2e-15; 531→2.3 ms/호출. RouteA.run 0.043 s (BPSK 0.20 s).
      T1 QPSK sanity(ρ=0): ‖Ĥ^E‖=0, |ν^E−1|≤1.2e-14, scalar≡colored ≤2.1e-13 (β=0.7·init_colored=1에서도). 회귀: 기본 옵션으로 exp_0918b T4c 자릿수까지 재현.
      T5 (Gaussian 폐형, 파일럿만): site 형 = 등방 prior LMMSE (3.7e-2); belief 형 고정점 평균 = 정확 LMMSE (30회 3.6e-6). T6: 행렬 H-site ≡ colored ≤1.5e-13.
      T2 Tp=4 BLER(전 변형 동률): 0 dB .875 / 3 dB .379 / 6 dB .041 (β=.7: .025) / 9·12 dB 0; genie .250/.029/.003/0 → genie 대비 ~3 dB 손실.
      T2 Tp=2 BLER (n=320) scalar/cinit1/belief1/belief3/colored/pilot(n=80): 9 dB .697/.503/.497/.484/.369/.700; 12 dB .594/.388/.431/.400/.263/.537; 15 dB .469/.312/.281/.287/.188/.463.
      F5(신규): QPSK Tp<Nt는 floor 영역 — v0 scalar ≈ pilot-only(12 dB는 더 나쁨), colored도 15 dB .19, genie 0. 성공 블록 NMSE는 전 변형 동일(9 dB .0050~.0059).
      Q-16: 성공 블록 ν^q 정상값 = (1.08~1.14)·σ²/T, 전 SNR·Tp 공통 (6 dB .0098, 9 dB .0049, 12 dB .0025, 15 dB .0013); belief 형 첫 패스 ν^q: Tp=2 1.0~1.25, Tp=4 = σ²/N_t.
코드: t2_trellis.py(벡터화, bcjr_loop 보존), t2_route_a.py(scal/n_inner/hsite/nu_sw), exp_0919_{common,run,analyze,t0,t1,t5,t6}.py | 결과: exp_0919_results_{T0,T1,T2,T5,T6}.txt, exp_0919_raw/*.npz
결론/후속: 완료 조건 중 "QPSK sanity 재통과" 충족; "BLER < pilot-only"는 v0로는 Tp=2에서 미충족, belief/colored로 충족; "hybrid 초기화 회복률 ≥1/2"는 D-13이 $\hat C$ 없이 충족 → D-11 강등, D-13/D-14.
```

```
exp_0919b | 목적: ablation (ii) 채널 되먹임×LOO, (iii) Q-04 decoder extrinsic 도메인, (iv) Q-04′ 심볼별 α^D; D-12 조건(16회 반복)
설정: exp_0919와 동일 trial(시드 동일), 기본 수신기 = mode colored (Gaussian testbed에서 D-13+D-14와 동일, T6); Tp=4 3·6 dB, Tp=2 12 dB, n=160; iter16: Tp=2 9·12 dB n=160
결과: T7 단위 검증: 정확 extrinsic pmf = brute force ≤1.3e-15 (QPSK/16-QAM), BPSK L_ext ≤3.1e-15.
      (ii) BLER base(extrinsic+LOO)/post_fb(+LOO)/no_loo/post_noloo: Tp=4 3 dB .381/.269/.394/.287; 6 dB .050/.025/.069/.056; Tp=2 12 dB .263/.150/.287/.194.
      (iii) pmf-domain: .450/.094/.344 (base보다 나쁨, p≈0.04 세 점 모두). (iv) per-symbol α^D: .769/.425/.444, clip 31~61%.
      iter16 BLER t=8→16: belief1 β=1 .431→.388, β=.7 .419→.394 (12 dB); colored β=1 .263→.256, β=.7 .250→.200; 주기-2 실패 블록 1~4%.
코드: t2_trellis.py(return_ext), t2_route_a.py(dec_ext, decode(ext=True)), exp_0919_run.py(sets abl/iter16), exp_0919_t7_newparts.py, exp_0919b_0920_analyze.py | 결과: exp_0919b_0920_results.txt, exp_0919_results_T7.txt
결론/후속: D-15 제안(posterior 되먹임+LOO); Q-04·Q-04′ 닫힘; D-12 조건 확정.
```

```
exp_0920 | 목적: 학습 없는 **비-Gaussian** testbed — Gaussian-mixture 채널 prior(폐형 score·denoiser·Jacobian)에서 D-11 vs D-13/D-14 vs exact-EP 기준 vs oracle
설정: 16 성분, C_k = kron(R_t(ψ_a)^T, R_r(ψ_b)), R(ψ)=D(ψ)R_exp(0.7)D(ψ)^H, ψ=2π(k+1/2)/4 → 앙상블 공분산 = I (2.9e-16). 4x4, T=28, QPSK, 8 반복, β=1, n=120, 시드 20260920+100+SNR.
      수신기: v0 / D11 / D13(n_inner 1,3) / D14 / D13+14 / +pf(D-15) / exactEP(비등방 cavity 정확 tilted 모멘트) / lmmseC(Gaussian Ĉ turbo) / pilot_gmm(GMM-MMSE 파일럿 추정 후 turbo) / pilot_C / genie / oracle(성분 기지)
결과: T7 GMM denoiser 검증: K=1 ≡ Gaussian 8.9e-14; Tweedie(FD) ≤3.7e-9; J = Cov/ν (FD) ≤1.2e-9; MC MMSE = E tr Cov (0.0273 vs 0.0274); λ_max(J)=1.86(>1, 비-log-concave).
      Tp=2 12 dB BLER: v0 .817 = D11 .817 (불일치 0) / D13 .658 / D14 .817 / D13+14 .592 = exactEP .592 / lmmseC .842 / pilot_gmm .850 / oracle .517 / genie 0;
                +pf: D13x3+14 .358 / exactEP .300 / lmmseC .475 / oracle .225.   15 dB 동일 양상(.842/.833/.658/.817/.592/.608; +pf .375/.375/.458/.192).
      Tp=3 9 dB: v0 .408 = D11 .408 / D13 .342 / D13+14 .283 / exactEP .267 / oracle .208; +pf .158/.108/lmmseC .167/oracle .083. Tp=4 6 dB: 전부 .058~.083, +pf .033 (prior 무관).
      참고: 성분 상관 0.9(거의 rank-1)에서는 genie도 12 dB BLER .05 — 4-stream 다중화 자체가 불가, testbed로 부적합(20 trials 확인 후 0.7로 변경).
코드: t2_route_a.py(GaussianPrior, GMMPrior{denoise, denoise_full, ep_site}, steer_corr, exact_prior), exp_0920_gmm.py | 결과: exp_0919b_0920_results.txt, exp_0920_raw/*.npz
결론/후속: D-11은 2차 모멘트가 밋밋한 prior에서 무효(예측대로); D-13이 선행 조건, D-14는 그 위에서 exact-EP 기준에 도달; 남은 격차는 exactEP_pf vs oracle_pf(Tp=2 15 dB .375 vs .192) = 혼합 사후의 단일 Gaussian projection 손실(Q-23).
```

```
exp_0921 | 상태: **A 완료(2026-09-18, n=320, 결과 Demo/exp_0921_results.txt — A 블록이 두 번 append됨, 동일 내용), B(4x4) 완료(2026-09-18, n=160, 커밋 0e905f7, Demo/exp_0921_results_B.txt); B 확장(n=640, 8x4 n=320) + C(n=320) 완료(커밋 f877eb8, Demo/exp_0921_results_{A,B,C}.txt)** | 목적: A = D-15 기준 T2 표, B = Q-20 regime scan(headline 영역 탐색)
설정: QPSK, (133,171)_8, T=28, Nt=4, 16 반복 기록(@8 = 같은 궤적의 index 7), 시드 20260921+100+SNR, chunk 40, M-1 + paired sign test + 실패 분류(stuck/cyc2/other; BER 궤적 11..16 기준 조작적 정의).
      A: rho=0.7, 4x4; Tp=4: 0/3/6/9 dB, Tp=2: 6/9/12/15 dB; n=320. 변형 15: colored x {ext,post} x beta{1,.7}, col_post_b0.7_fbd(beta_fb=.7), col_postnoloo_b0.7,
         v0 x {ext,post} x beta{1,.7}, belief1 x {ext,post} (beta .7), pilot beta{1,.7}, genie.
      B: rho{.7,.9} x Tp{4,3,2} x 파일럿{dft, eig(=sqrt(Nt) U_{1:Tp}); Tp=4는 dft만} x SNR(rho=.7: 0..18, rho=.9: 6..24, 3 dB 간격); n=160; 이후 --Nr 8.
         변형 5: col_ext_b0.7, col_post_b0.7, pilot beta{1,.7}, genie. 지표: BLER@8/@16, goodput K(1-BLER)/T, SNR@BLER=0.1, regime check(pilot-only >= .5 & joint <= .1).
명령: python exp_0921_run.py predict | time | A [--n 320] | B [--n 160] [--Nr 8] ; python exp_0921_analysis.py A|B  -> exp_0921_results.txt
코드: exp_0921_run.py, exp_0921_analysis.py, t2_route_a.py(exp_0921 패치: Xp, beta_fb) | 결과: (대기)
```

```
exp_0921 C | 상태: **완료(2026-09-18, n=320, 커밋 f877eb8)** | 목적: Q-25(b) — GMM testbed(exp_0920 prior, 정확 score)에서 D-15가 켜지면 D-13/D-14가 여전히 필요한가
설정: QPSK 4x4, T=28, DFT 파일럿, rho_c=0.7, beta=0.7, n_inner=1, 16 반복, 시드 20260921+100+SNR, n=320. Tp=4: 3/6/9 dB, Tp=2: 9/12/15 dB.
      변형 14: {v0, D13, D13+14, exactEP} x {ext, pf}, D14_pf, lmmseC_pf, pilot_gmm, pilot_C, genie, oracle_pf(참 성분의 Gaussian prior).
      메모(Q-20(d)): 이 testbed는 앙상블 공분산이 정확히 I → 2차 모멘트 기반 "정렬 파일럿"은 DFT와 구별 불가. 정렬 파일럿 실험은 C에 넣지 않음.
명령: python exp_0921_run.py C ; python exp_0921_analysis.py C -> exp_0921_results_C.txt
분석 스크립트 보완: regime check 완화([S] pilot>=.3 & joint<=.1, [R] pilot>=.02 & joint<=pilot/5), goodput 포락선 자동 출력, A에 Q-25 쌍 추가.
```

```
exp_0921 B-T (Q-28) | 상태: **완료(2026-09-18, n=640, 커밋 e21e108)** | 목적: 파일럿 오버헤드가 큰 영역에서 headline 재측정
근거[정확]: goodput 상한 K/T = (Nt(T-Tp)-6)/T.  T=28: Tp=4 3.214, Tp=2 3.500 (+8.9%);  T=16: 2.625 -> 3.125 (+19.0%);  T=12: 2.167 -> 2.833 (+30.8%).
예상[추측]: T가 짧으면 (i) 데이터 보조 추정에 쓸 심볼 수 Td 감소 -> joint의 NMSE 이득 축소, (ii) 부호 길이 감소(T=16, Tp=4: K=42) -> waterfall 완만.
           이득이 상한에 근접하려면 8x4에서 Tp=2 joint의 floor 부재가 T=16에서도 유지되어야 함.
설정: B 세트 그대로(rho=0.7, Tp{4,3,2} x {dft,eig}, SNR 0..18, 변형 5), n=640, 시드 관례 동일. 파일명에 _T<T> 태그(T=28은 태그 없음 -> 기존 raw와 호환).
명령: python exp_0921_run.py B --T 16 --Nr 8 --rho 0.7 --n 640 ; ... --T 16 --Nr 4 ... ; ... --T 12 --Nr 8 ... ; python exp_0921_analysis.py B
코드 변경: run에 --T, analysis가 (Nr,T)별로 요약 + K/T 상한 출력 + genie all-NaN 경고 억제. 기존 8x4 T=28 raw 재분석으로 수치 재현 확인(2.4 dB, +4.3%).
```

```
exp_0922 interface (Q-27) | 상태: **완료(2026-09-18, n=2000, 커밋 2a276fe, 18초) — 판독은 위 09-18 항목** | 목적: 첫 패스에서 one-shot 등방 인터페이스(D-13, D-13+D-14)의 손실을 정확 mixture posterior와 비교
설정: GMM(exp_0920 prior, rho_c=0.7), 4x4, DFT 파일럿, Tp{4,3,2} x SNR{6,12,18}, n=2000, 시드 20260922+100Tp+SNR. 복호기 없음(수 초).
출력: nu_q(측정/폐형식/RouteA 로그), P(MAP 성분=참), E[w_true] (정확 vs 등방), NMSE(정확 혼합 / D13 1-shot / D13+D14 / LMMSE(I) / oracle).
명령: python exp_0922_interface.py  (결과 표를 Demo/exp_0922_results.txt로 저장)
```

```
exp_0923 R-A first pass (Q-27/Q-29) | 상태: **완료(2026-09-18, n=1000, 커밋 6f19360, 25초) — 기준 (1)(2)(4) 충족, (3) 미달 → 표집기 재설계(위 09-18 항목)** | 목적: 등방 score만 쓰는 annealed posterior sampling(R-A)이 exact-EP 모멘트를 어느 비용에서 회수하는가
설정: GMM(exp_0920 prior, rho_c=0.7), 4x4, 첫 패스. 경우: Tp4/Tp3/Tp2(DFT), aniso(전력 1 파일럿 2개 + -10 dB 파일럿 2개; weak 좌표 경로 점검) x SNR{6,12,18}, n=1000.
      방법(같은 (H,W)에 paired): exact, D13+D14, LMMSE(I), PS-M{8,32,128}(정확 표집기 = M-chain Monte Carlo 바닥), RA-M{M}-L{L}-K{K}: (32,12,2),(32,24,4),(32,48,8),(8,24,4),(128,24,4),
      -J1(Jacobian 1개만). delta=0.3, nu_1=10, K_fin=2K. 시드: data rng [20260923, case, snr, trial], sampler rng [..., method] (jobs/chunk 무관 재현).
출력: NFE/chain, NMSE(및 exact 대비 %), w_true, P_map, KL(N_exact||N_method)/N (mean, median), covErr, site clip%, chi, 정확 표집기 가중 검산. raw: exp_0923_raw/<case>_snr<S>.npz
명령: python exp_0923_ra_firstpass.py | tee exp_0923_results.txt        코드: t2_ra_sampler.py(신규), exp_0923_ra_firstpass.py
사전 검산(Claude, Monte Carlo 아님): noise-splitting 항등식 폐형식 <=7e-13; 정확 표집기 가중 = exact <=5e-14; Tp4 전 행 일치; n=2 smoke(수치 폐기).
판독 기준(사전 등록): (1) Tp4 전 행 일치. (2) PS-M32의 NMSE <= exact x 1.04, KL/N << D13+D14. (3) RA-M32-L24-K4가 Tp2에서 D13+D14 대비 NMSE 격차의 >=2/3 회수하고 KL/N이 PS-M32의 2배 이내 -> turbo 통합 진행;
      미달이면 (L,K) 증량 행(RA-M32-L48-K8)로 판단, 그것도 미달이면 표집기 재설계. (4) -J1 행이 all-J 행과 KL/N 10% 이내면 Jacobian 1개 채택.
```

```
exp_0924 R-A v2 bridge ladder (Q-29) | 상태: **완료(2026-09-18, n=1000, 커밋 06c28ca, 30초) — (i)(ii) 충족, (iii)(iv) 미달 → D-17 철회(위 09-18 항목)** | 목적: v1 표집기 미달의 원인 분리 + v2 bridge(posterior diffusion + 정확 handover) 평가
설정: exp_0923과 같은 GMM·같은 첫 패스 데이터(data rng [20260923, case, snr, trial] -> exp_0923 행과 paired), 경우 Tp3/Tp2/aniso x SNR{6,12,18}, n=1000, M=32, nu_1=10.
      사다리: exact, D13+D14, PS-M32, RA-M32-L24-K4(v1, exp_0923과 같은 표집 시드 -> 회귀), PSinit-K{16,128}, RA2X-L{6,12,24}, RA2J-L{6,12,24}, RA2S-L{12,24}, RA2J-L12-K8, RA2J-L12-M128.
출력: NFE, nJ, NMSE(+% vs exact), w_true, P_map, KL/N(mean/median/99%), KLc/N(site clip 1e-6 왕복 후 = 수신기가 보는 값), covErr, clip%, v1 회귀 오차. raw: exp_0924_raw/<case>_snr<S>.npz
명령: python exp_0924_ra2_bridge.py | tee exp_0924_results.txt      코드: t2_ra_sampler.py(v2 추가분; v1 부분 무변경), exp_0924_ra2_bridge.py
사전 검산(Claude): v2-X/J Gaussian 폐형식 <=5e-14(L=2 포함); v1 회귀 <=1e-14; n=2 smoke(수치 폐기). 판독 기준: 위 D-17 상태 갱신 항목 (i)~(iv).
```

```
exp_0925 kill test (D-19 + 보정 R1~R7) | 상태: **코드 작성·단위 테스트 완료(세션 6), 실행 대기** | 목적: score prior 분기와 T2 현 설계의 중단 여부를 M2 학습 전에 판정
설정: QPSK (133,171)_8 nu=6, Nt=4, 16반복, 모든 joint arm = D-15 + LOO + beta 0.7. 참 prior = 32x32 각도 격자 혼합(K_true=1024, 성분 rho_c=0.7), prior U/S/P(R1).
      셀 H(headline) 8x4 T=16 Tp=2 eig(S)/DFT(U,P) SNR -3..15 dB 7점; H4 동일 Tp=4(R2); R(비교용) 4x4 T=28 Tp=2 SNR 9/12/15. n=640/점, seed 20260925.
      arm: lmmseC_pf(a) / Hgmm-K{16,32,64}·Hgmm-kron(b, 검증 우도로 kappa·정지·K 선택 → b*) / Hscore-exact(c) / exactEP-true(d) / Hscore-K32 / *-mp(clip 진단) / pilot_C / pilot_Hgmm-K32 / genie / oracle_pf.
      적합: ntrain=1e4, n_val=n_test=5000, family{full,kron} x K{16,32,64} x kappa{0,16,64,256} x restart 3, 선택은 검증 우도만(BLER 미사용).
명령: python exp_0925_tests.py | tee exp_0925_tests.txt ; python exp_0925_run.py prior | tee exp_0925_prior.txt ; python exp_0925_run.py fit ; python exp_0925_run.py K ; python exp_0925_analysis.py | tee exp_0925_results.txt
코드: t2_gmm.py, exp_0925_run.py, exp_0925_analysis.py, exp_0925_tests.py (t2_route_a.py 무변경). raw: Demo/exp_0925_raw/*.npz, 적합: Demo/exp_0925_fits/*.npz
사전 검산(Claude): 단위 테스트 전 항목 PASS, 스모크 n<=4 전 경로(수치 폐기). 판독 기준: 위 D-19 + R1~R7 (analysis §5가 기계적으로 출력).
```
