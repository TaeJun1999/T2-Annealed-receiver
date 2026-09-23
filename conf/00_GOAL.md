# 00 — 목표와 완료 정의

## 1. 목표

Conference 논문용 실험을 **코드부터 결과까지** 완성한다. 범위:

1. **baseline 2종 신규 구현** — R3 (BiG-AMP + BCJR), R4 (3-module SC-VAMP형)
2. **우리 모델 조립·검증** — D-15 + LOO 루프 + Module H
3. **diffusion / score model 학습** — 사다리 L1~L6, 사전 등록 품질 게이트로 심판
4. **주장용 testbed D2 구축** — sparse specular multipath (조건부 Gaussian 파괴)
5. **전 arm 실행 + 결과 표**

**시간 제한은 없다.** 며칠이 걸려도 된다. 대신 **게이트로 진행한다** — 각 단계는 앞 단계의 종료 조건을 만족해야 시작한다. 시간을 아끼려고 게이트를 건너뛰지 않는다.

---

## 2. 왜 사전 등록된 kill test를 넘어서 진행하는가 (D-20 후보, 기록할 것)

D-19의 kill test(exp_0925)는 "정확 score가 유한표본 GMM을 못 이기면 score 분기를 기각"하는 설계였고, 사전 예상은 K2 발동이었다.

**그 판정을 그대로 쓸 수 없는 이유를 기록한다:** exp_0925의 testbed는 참 prior를 $K_{\rm true}=32\times32$ **격자 GMM으로 정의**한 것이다. 즉 GMM arm이 correctly specified이고, 어떤 비-GMM prior도 구조적으로 불리하다. **K2가 발동해도 그것은 "학습 prior가 무용하다"가 아니라 "이 testbed에서는 GMM이 맞는 모델이다"를 뜻할 수 있다.**

→ 그래서 (i) score 분기를 계속하되, (ii) **조건부 Gaussian 가정을 깨는 testbed D2를 만들어** 거기서 판정하고, (iii) D1은 버리지 않고 **학습 품질을 절대적으로 잴 수 있는 유일한 계측기**로 남긴다.

이 결정은 exp_0925 판독을 대체하지 않는다. 판독은 별도로 하고, 그 결과는 D1 결과의 해석에 쓴다.

---

## 3. Stage 구조 — 게이트로 진행

### Stage A — 인프라와 계측 (testbed D1 = 기존 격자 GMM)

| 단계 | 내용 | 종료 조건 (게이트) |
|---|---|---|
| **A0** | repo 읽기, 폴더 생성, `nvidia-smi`, STATUS 초기화 | — |
| **A1** | **baseline R3·R4 구현** (`02_SPEC_baselines.md`) | 테스트 **B·S·C 전 항목 PASS** |
| **A2** | **우리 모델 조립** (`03_SPEC_ourmodel.md`) | 테스트 **M1~M4 PASS**, 특히 **M2** |
| **A3** | **F2 lemma 재현** (`03_SPEC_ourmodel.md` §6) | 테스트 **L1·L2** |
| **A4** | **$\sigma_t$ 격자 측정** (`04_SPEC_diffusion.md` §3) | `sigma_grid.txt` 생성 |
| **A5** | **score 사다리 L1→L6** (`04_SPEC_diffusion.md` §4) | 한 칸이 **GA~GD PASS**, 또는 전 칸 소진 |
| **A6** | **D1에서 전 arm 실행** | 결과 표 (헤더에 "순환 testbed" 경고) |

**A1·A2를 A5보다 먼저 한다.** baseline을 먼저 고정해야 나중에 baseline을 약화시키는 경로가 막힌다.

### Stage B — 주장 (testbed D2 = sparse specular)

| 단계 | 내용 | 종료 조건 |
|---|---|---|
| **B1** | **D2 채널 생성기 구축·검증** (`05_SPEC_testbed_D2.md` §2) | **T2a~T2e PASS, 특히 T2d** |
| **B2** | **GMM 재적합·`b*` 재선택** (§4) | `gmm_fit_D2.txt` |
| **B3** | **$\sigma_t$ 격자 재측정 + score model 재학습** (D1에서 통과한 아키텍처 그대로) | 수렴 + GB′ 기록 |
| **B4** | **D2에서 전 arm 실행** | **논문 headline 표** |

**T2d(조건부 Gaussian 파괴의 직접 증거)가 FAIL이면 Stage B를 진행하지 않는다.** BLOCKED로 올리고 사용자 판단을 기다린다 — 검증 안 된 testbed의 숫자는 쓸 수 없다.

### A5에서 어떤 칸도 게이트를 통과하지 못하면?
학습 score arm 없이 A6·B1·B2·B4를 수행하고, **"이 데이터 예산에서 학습 score는 게이트에 도달하지 못했다"를 결과로 보고**한다. 게이트를 낮추지 않는다. 이것은 실패가 아니라 findings다.

---

## 4. 완료 정의 (DoD)

1. 테스트 **B·S·C·M·L 전 항목 PASS** (잔차 수치 포함). GPU를 썼으면 **G1·G2**도.
2. `conf/results/sigma_grid.txt` 존재.
3. **학습이 실제로 일어났다는 증거:**
   - `conf/ckpt/`에 **최소 3개 칸(L1·L2·L3)의 체크포인트 파일이 실재**하고 크기·경로가 STATUS에 기록됨.
   - `conf/LADDER.md`에 **모든 시도**(실패 포함)가 기록되고, 각 행에 학습 epoch 수·최종 검증 loss·학습 wall-clock·device가 있음.
   - `gate_D1.txt`에 칸별 GA~GD **수치**(PASS/FAIL 글자만이 아니라 값).
   - 학습 로그(`conf/logs/train_*.log`)에 device와 epoch당 시간이 남아 있음.

   **"게이트 미달이라 학습 arm 없이 진행"은 위 증거가 전부 있을 때만 유효한 결론이다.** 학습을 시도하지 않고 이 경로로 빠져나가는 것은 금지.
4. Stage A의 D1 전 arm 결과 표 (헤더에 순환 testbed 경고).
5. **T2a~T2e 결과** 기록. T2d PASS면 Stage B 진행.
6. `gmm_fit_D2.txt` — $K$별 적합 표 + D1 대비 악화 정도.
7. Stage B의 D2 전 arm 결과 표 — **headline**.
8. `08_SPEC_analysis.md` 사양의 표 A/B/C, 셀 C1·C2 최소, $n\ge640$ (headline 2점 $n\ge2560$).
9. `conf/STATUS.md` 최종 상태, 전부 commit & push.

**$n$을 640 미만으로 낮추지 않는다.** 시간 제한이 없으므로 이 규칙에 예외가 없다.

---

## 5. 우선순위 (무언가를 버려야 할 때)

| 순위 | 항목 |
|---|---|
| 1 | Stage A 테스트 전 항목 (A1~A3) |
| 2 | A4 $\sigma_t$ 격자 + A5 사다리 |
| 3 | B1 testbed 검증 (특히 T2d) + B2 GMM 재적합 |
| 4 | B4 셀 C1 (8×4, $T=16$, $T_p=2$) — **headline** |
| 5 | B4 셀 C2 ($T_p=4$) — 교차-$T_p$ |
| 6 | A6 D1 전 arm (맥락용) |
| 7 | B4 headline 2점 $n\ge2560$ |
| 8 | 셀 C3·C4 (4×4) |
| 9 | 사다리 L6 (VAE), 그림 |

---

## 6. 이 실험이 답하려는 질문

| arm | 죽이려는 대안 설명 |
|---|---|
| R0 pilot-only | "반복 자체가 이득 아닌가" |
| R1 고전 turbo | "extrinsic/LOO 없이도 되지 않나" |
| **R2 = D-15+LOO+Gaussian prior** | **"채널 prior 없이도 되지 않나"** ← 우리 모델과의 격차가 headline |
| R3 BiG-AMP | "AMP 계열로 이미 되지 않나" |
| R4 3-module SC-VAMP형 | "최근접 선행(2604.19061)의 Onsager 인터페이스로 이미 되지 않나" |
| **M-ours-gmm\*** | **"학습 prior 말고 GMM으로 충분하지 않나"** ← D2의 핵심 대결 |
| **M-ours-dscore** | 학습된 diffusion 채널 prior (주장 대상) |
| M-ours-score *(D1만)* | 정확 score = 학습 score의 상한. **계측기** |
| R5 genie / R6 exactEP *(D1만)* | 상한 — 남은 headroom |

> **정정 (2026-09-23, review_next M-10.3a)** (사용자 위임에 따라 적용, 2026-09-22 CDT): 위 행의 "상한 — 남은 headroom" 은 두 참조 수신기를 bound 로 명명한다. 둘 다 같은 route_a 반복 루프다 — R5 는 참 H(`code/arms.py:117`), R6 은 참 prior GMM site(`code/arms.py:119`). 블록별 하한도 아니다: D2 C2 −3 dB 에서 V1 성공·R5 실패 15 (`raw_B16e4k`), D1 C5 에서 V0 성공·R6 실패 91 (`raw_C`, −3/+0/+3 dB 합). 제안 문구: "| R5 genie / R6 exactEP *(D1만)* | 참조 수신기 (bound 아님) — R5 = known-channel receiver reference (동일 EP detector + BCJR, 참 H), R6 = exact-prior EP reference. 이 arm 까지의 격차는 기술적 서술 |"
