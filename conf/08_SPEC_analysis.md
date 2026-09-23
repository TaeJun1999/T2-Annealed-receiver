# 08 — 분석·출력 사양

> 분석 스크립트는 **숫자만 낸다. 해석·결론을 쓰지 않는다.** 판독은 사람이 한다.
> 가능하면 `Demo/exp_0925_analysis.py`의 계산 루틴(paired sign test, SNR@0.1, bootstrap CI, goodput 포락선)을 **재사용**한다.

## 0. 표는 testbed별로 따로 낸다

D1과 D2는 **arm 집합이 다르다**(`06_SPEC_runner.md` §1). 합치지 않는다.
- **D1 표** 헤더: `CIRCULAR TESTBED — true prior is defined as a grid GMM; the GMM arm is correctly specified. No claim about learned priors can be made from this table.`
- **D2 표** 헤더: `CLAIM TESTBED — sparse specular; conditional Gaussianity broken (see T2d). Upper bound = genie only.`

> **정정 (2026-09-23, review_next R-10.3)** (사용자 위임에 따라 적용, 2026-09-22 CDT): 위 D2 헤더의 `Upper bound = genie only.` 는 R5-genie 를 bound 로 명명한다. R5-genie 는 같은 route_a 반복 수신기에 참 H 를 넣은 것이다(`code/arms.py:117`, `Demo/t2_route_a.py:388-389`; BLER@1/@2/@8/@16 = 0.225/0.102/0.043/0.034, `results/tables_D2_B16e4k.txt:92`). C2 −3 dB 에서 V1 성공·genie 실패 15 블록(`raw_B16e4k`)이 있어 블록별 하한도 아니다. 제안 헤더: `CLAIM TESTBED — sparse specular; conditional Gaussianity broken (see T2d). Reference = known-channel receiver (R5-genie: same EP detector + BCJR, true H); not a bound.` 승인되면 `code/common.py:228` 만 바꾸고 이미 생성된 `tables_D2_*.txt` 는 재생성하지 않는다 — 옛 헤더는 이 주석으로 읽는다.

## 1. 표 A — 셀별 arm 비교 (주 산출물)

행 = arm 10종, 열 = 각 SNR 점. 셀마다 한 표.

각 칸: `BLER (95% CI) / BER / NMSE_H@16`

표 아래 요약 행:
- **SNR@BLER 0.1** (보간), **90% paired bootstrap CI**
- 실패 분류 비율: `stuck` / `cyc2` / `diverged` / `other`
- clip 발동률
- 적합·학습 비용 (GMM EM wall-clock 초) — **빈칸으로 두지 않는다. 해당 없으면 `n/a`**

## 2. 표 B — paired 비교 (논문의 논지에 직결)

다음 **쌍만** 계산한다. 전 arm 짝짓기를 하지 않는다(다중비교 문제).

| 쌍 | 무엇을 읽나 |
|---|---|
| R1 → R2 | extrinsic+LOO의 몫 (맥락. T1의 결과이므로 headline 아님) |
| **R2 → M-ours-gmm32**, **R2 → M-ours-bstar** | Module H(GMM)의 몫 |
| **R2 → M-ours-dscore** | **학습된 diffusion prior의 몫 = D2에서의 논문 headline** |
| **M-ours-bstar ↔ M-ours-dscore** | **GMM vs diffusion 직접 대결.** D2의 핵심 |
| R2 → M-ours-score *(D1만)* | oracle 상한. 계측기이지 주장 아님 |
| **R2 → R4-scvamp** | 우리 이득이 Onsager 인터페이스만으로 얻어지는가 |
| R4-llr → R4-scvamp | 원문 ablation 재현 (기지 채널이 아닌 우리 설정에서도 성립하나) |
| R2 → R3-bigamp | AMP 계열 대조 |
| M-ours-* → R6-exactEP *(D1만)* / → R5-genie *(D2)* | 남은 headroom |

> **정정 (2026-09-23, review_next M-10.3a)** (사용자 위임에 따라 적용, 2026-09-22 CDT): 위 행의 "남은 headroom" 을 "reference 까지의 격차 (R6 = exact-prior EP reference, R5 = known-channel receiver reference; 기술적 서술이며 bound 아님)" 로 읽기를 제안한다. 근거는 10행 주석과 같다. R6 도 같은 route_a 루프(`code/arms.py:119`, 참 prior GMM site)이고 D1 C5 에서 V0 성공·R6 실패 91 블록이 있다(−3/+0/+3 dB 합, `results/tables_D1_C.txt:1139` 88:91).

각 쌍에 대해: paired sign test의 불일치 쌍 수와 $p$-값, SNR@0.1 격차와 90% paired bootstrap CI.

**검정력 하한(기존 관례 R6·R7 준용):** 결정 점이 격자 위에 3개 이상 있고 그중 2개 이상에서 불일치 쌍이 6개 이상일 때만 "유의/비유의"를 출력한다. 미달이면 **`UNDECIDED`** 를 찍는다. 판정하지 않는다.

## 3. 표 C — 교차-$T_p$ goodput 포락선

C1($T_p{=}2$)과 C2($T_p{=}4$)를 합쳐 arm별 goodput 포락선. 같은 BLER에서의 **파일럿 절감**을 읽는 근거.

## 4. 그림

**F2 (lemma 검증) — 우선순위 높음, 비용 10분.** `03_SPEC_ourmodel.md` §6. 두 패널: (좌) $\sigma^2$ 축에서 BCJR 조건부 평균 vs brute-force, (우) 오차 로그 축. 캡션에 오차 상한 수치를 적는다.

**나머지 그림 (여유가 있을 때만, 우선순위 최하)

- **F3**: C1의 BLER vs SNR. 곡선 6개만: `R0-pilot`, `R1-turbo`, `R2-ours-G`, `M-ours-*`(확정되지 않았으므로 전부 점선), `R4-scvamp`, `R5-genie`. 나머지는 표로.
- 축·단위·범례를 명시. 스타일은 최소한으로.

## 3.5 표 D — 학습 품질 (BLER과 무관, 독립적으로 실을 수 있는 결과)

- **D1:** 사다리 칸별 GA~GD 수치 (`gate_D1.txt`). 통과·미달 전부.
- **D2:** 동일 $\sigma_t$ 격자에서 GMM prior와 diffusion prior의 **held-out denoising NMSE** (GB′, `gate_D2.txt`). BLER 이전 단계의 공정한 비교이므로 그 자체로 결과다.
- **GMM 적합 표** (`gmm_fit_D2.txt`): $K$별 train/val 우도, 과적합 격차, **D1 대비 악화 정도** — testbed가 실제로 조건부 Gaussian을 깼다는 두 번째 증거.

## 5. 출력하지 말 것

- "유의하다 / 이득이 있다 / 우리 방법이 낫다" 같은 **판정 문장**.
- 검정력 미달인데 내려진 결론.
- 실패·발산 블록을 제외한 뒤 계산한 평균 (제외하려면 **제외 전후를 둘 다** 낸다).
- 논문 문장. 이 단계는 연구이지 집필이 아니다.
- **D1 표에서 학습 prior에 대한 주장.** D1은 순환 testbed다.
- D1과 D2를 합친 표.
