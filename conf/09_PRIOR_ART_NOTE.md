# 09 — 원문 확인 기록 (prior art note)

> 웹 세션 2026-09-19에 원문을 직접 읽고 기록한 것. 구현 중 참고용이자, **사용자가 `docs/logs/`에 이관할 원본**이다.
> Claude Code는 이 파일을 **읽기만 한다.** `docs/logs/`는 수정 금지(`01_RULES.md` §2).

---

## 1. arXiv:2604.19061v1 — Three-Module SC-VAMP for LDPC-Coded Nonlinear Channels (Wadayama–Takahashi) [V: 본문 전체]

이 논문은 T2의 **최우선 스쿠핑 위험**으로 지정돼 있었고, 핸드오프 §0은 착수 전에 세 질문에 답하라고 요구했다. 이번에 닫힌다.

| 질문 | 답 | 근거 |
|---|---|---|
| (i) 채널이 미지/bilinear인가 | **아니다.** $\mathbf H\in\mathbb R^{M\times N}$, $H_{ij}\sim\mathcal N(0,1/M)$, **기지**. Module C가 $\mathbf H^\top\mathbf H$의 고유분해를 직접 사용. 채널 추정 절차 자체가 없다 | §II-B 식 (1); §III-C1 식 (16)–(18) |
| (ii) 학습된 **채널** prior가 있는가 | **없다.** prior는 LDPC 부호 제약 $p_X$ 하나. 학습 가능 score는 Module A의 **비선형성** $f$ 쪽 언급뿐 | §III-C2 |
| (iii) trellis(BCJR)인가 BP인가 | **BP만.** rate-1/2 LDPC (CCSDS 128/256/512, WiMax 1056/2304), BPSK 실수, 외부 20회 × BP 20회 | §IV |

**판정.** T2의 잔여 novelty 축 — **미지 채널 + bilinear 결합 + 학습된 채널 prior** — 은 이 논문에 대해 **온전하다.**

**새로 생긴 위험.** 이들의 ablation "LLR Turbo"(Module B만 고전 $L^{\rm ext}=L^{\rm app}-L^{\rm in}$)가 Onsager 인터페이스 대비 BER $10^{-2}$에서 **≈3 dB 손해**로 보고된다(기지 채널, $f=\mathrm{id}$). 우리 D-15+LOO 서술과 리뷰어가 반드시 연결시킬 지점이다. → baseline **R4**가 이 연결을 우리 설정(미지 채널)에서 실험으로 끊거나 인정해야 한다. 이것이 R4의 존재 이유다.

**인용 의무.** R4 arm을 서술할 때 이 논문을 인용하고, R4가 **저들의 알고리즘이 아니라 저들의 인터페이스를 우리 설정에 적응시킨 것**임을 명시한다.

---

## 2. arXiv:1310.2632v3 — Bilinear Generalized AMP, Part I (Parker–Schniter–Cevher) [V: 본문 Table III·§IV-A]

**원문 오타 발견 [정확, 폐형식 확인].**
damping 식 (95)는 $\nu^s\leftarrow\beta\big((\nu^z/\nu^p-1)/\nu^p\big)+\cdots$ 로 인쇄되어 Table III (R7)과 **부호가 반대**다.

(R7)이 맞다. AWGN에서 $\nu^z=\dfrac{\nu^p\sigma^2}{\nu^p+\sigma^2}<\nu^p$ 이므로
$$\frac{1-\nu^z/\nu^p}{\nu^p}=\frac{1}{\nu^p}\Big(1-\frac{\sigma^2}{\nu^p+\sigma^2}\Big)=\frac{1}{\nu^p+\sigma^2}>0,$$
이것이 원문 식 (72)의 $\nu^s_{ml}=1/(\nu^p_{ml}+\nu^w)$와 일치한다. 식 (95)를 따르면 $\nu^s<0$이 되어 발산한다.

→ 구현은 (R7)을 쓴다. 테스트 **B6**이 이를 잠근다.

**구조적 한계 (우리 baseline 서술에 필요).** Table III는 $p_{a_{mn}}$을 **element-wise 분리형**으로 가정한다. 우리 testbed의 Kronecker 상관 채널 prior를 넣을 방법이 없다(수신단 whitening은 $\mathbf R_t^{1/2}\mathbf X$가 부호·성상 prior를 깨므로 불가). 따라서 R3는 i.i.d. $\mathcal{CN}(0,1/N_r)$ prior로 돌리고, 이를 **BiG-AMP의 한계**로 결과와 논문에 명시한다. 상관 prior를 받는 대안(BAd-VAMP 계열)은 원문 확보·구현이 별도 작업이라 conference 범위 밖이다.

---

## 3. 이관 지시 (사용자용)

- **scooping log:** `2026-09-19 | 2604.19061 본문 확인 | [V, 초록만] → [V, 본문] | 세 질문 답변은 위 표 | T2 잔여 novelty 축 온전 | 새 위험: Onsager vs LLR 차감 3 dB 주장`
- **open questions:** `Q-37 (신규, 열림)` — R2와 R4-scvamp의 격차가 0.5 dB 미만이면 D-15+LOO 기여 서술을 어떻게 수정하나. 판정 근거 = conf 실험 표 B.
- **decision log:** 이번 폴더 착수는 D-20 후보(사용자 승인 시 기록). 알고리즘 오타 판정은 유도 항목으로 기록.
