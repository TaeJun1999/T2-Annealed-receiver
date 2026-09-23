# RECORD_CORRECTIONS_DRAFT — 기록 정정 초안 (미적용)

- 작성: 2026-09-23 KST, Claude Code (1차 Opus 5.5, 2차 Fable 5.1 감독). **초안이다. 어떤 기록 파일도 아직 수정하지 않았다.**
- 기준: HEAD `cd241b7e`. 줄 번호는 이 커밋 기준 (STATUS.md는 cd241b7e에서 헤더 1줄이 늘어 감사 문서의 번호보다 +1인 곳이 있다).
- 근거: `REVIEW_AUDIT.md`의 해당 항목. 수치는 초안 agent가 raw에서 다시 뽑았고, 별도 검증 agent가 (1) 원문 인용이 글자 그대로인지 (2) 수치 재도출 (3) 원 과해석을 유지하거나 반대 방향으로 과잉 정정하지 않는지 확인했다.
- 규모: 1차 66개 + 2차(1차 검증이 찾은 누락 위치) 49개 = **115개**. 검증에서 문제가 나온 37개는 **검증 agent가 고친 문구로 교체해 실었다** (항목마다 표시). 2차 검증 뒤에도 남은 소수 위치는 맨 끝 '3차 잔여'에 검증 agent 제안 그대로(2차 검증 없음) 둔다.
- 적용 방식 (기록 관례): `DECISIONS.md` = append 한 줄(`[2026-09-23 __:__ KST] 정정 — …`, 시각은 적용 시 기입) · `STATUS.md`/`PAPER_MATERIALS.md` = 원문 유지 + 바로 뒤 `> **정정 (2026-09-23, review_next <id>)**` · spec/rules 파일(00_GOAL, 01_RULES, 03/05/06/08/10_SPEC, PROMPT) = **사용자 승인 필요** 표시된 노트 · 코드 docstring/캡션 생성기 = 동작 불변 문구 교체(생성기 출력 문자열은 사용자 승인 뒤) · 이미 생성된 그림·표는 재생성하지 않음 · 커밋 메시지는 수정 불가(force push 필요) → DECISIONS 정정으로 대신.
- 복잡도 항목의 대체 수치는 `complexity_moduleH_ep.txt`(실경로 벤치, 아직 미실행) 결과로 채운다 — 초안에는 `V1/b\* = Module H 호출당 1.35× (−3 dB) · 1.39× (+6 dB), 블록 전체 1.33× · 1.38× (헤드라인 구성 kron K=1024 + d2sx_N160000_a1, 실제 수신기 경로; `results/review_next/complexity_moduleH_ep.txt`)` 자리표시.
- 원자료: `record_corrections_raw.json`(1차), `record_corrections_r2_raw.json`(2차).

## 목차

- **1차 · 꼬리·반복 해석 (R-10.1, M-10.1a, R-10.2)** — 7항목: `conf/STATUS.md`×4, `conf/DECISIONS.md`×2, `git`×1
- **1차 · genie/상한 명칭 (R-10.3, M-10.3a)** — 13항목: `conf/DECISIONS.md`×2, `conf/STATUS.md`×3, `conf/PAPER_MATERIALS.md`×2, `conf/08_SPEC_analysis.md`×1, `conf/code/common.py`×1, `conf/05_SPEC_testbed_D2.md`×1, `conf/00_GOAL.md`×1, `conf/figs/F11_bler_D2_confirmatory.txt`×1, `conf/STATUS.md,`×1
- **1차 · D2 testbed 서술·게이트 표현 (R-5.2, M-5.2a, G-1.2)** — 23항목: `conf/code/d2.py`×1, `conf/05_SPEC_testbed_D2.md`×2, `conf/DECISIONS.md`×3, `conf/01_RULES.md`×1, `conf/PAPER_MATERIALS.md`×3, `conf/10_SPEC_stageC.md`×2, `conf/PROMPT.md`×1, `conf/STATUS.md`×9, `conf/code/figures_stagec2.py`×1
- **1차 · 복잡도 4.6x·체크포인트 (P0-2b, cost/M1·M2, P0-1b, ckpt/M2)** — 23항목: `conf/STATUS.md`×9, `conf/results/NUMBERS_PACKAGE_2026-09-22.md`×1, `docs/EXPERIMENTS.md`×2, `conf/figs/F14_headline_C2_m3dB.txt`×1, `conf/figs/F14b_C2_m6dB_max_absolute_gap.txt`×1, `conf/figs/F14c_C2_p12dB_max_ratio.txt`×1, `conf/code/figure_f14.py`×2, `conf/results/complexity_moduleH.txt`×1, `conf/DECISIONS.md`×4, `conf/PAPER_MATERIALS.md`×1
- **2차 · genie/상한 명칭 (R-10.3, M-10.3a)** — 10항목: `conf/DECISIONS.md`×1, `conf/06_SPEC_runner.md`×1, `conf/10_SPEC_stageC.md`×1, `conf/results/NUMBERS_PACKAGE_2026-09-22.md`×1, `conf/results/jac_spectrum.txt`×1, `conf/code/figures.py`×1, `conf/code/figure_f14.py`×1, `conf/code/figures_stagec2.py`×1, `conf/code/analysis.py`×1, `N/A`×1
- **2차 · D2 testbed 서술·게이트 표현 (R-5.2, M-5.2a, G-1.2)** — 21항목: `conf/DECISIONS.md`×2, `conf/10_SPEC_stageC.md`×4, `conf/STATUS.md`×6, `conf/PAPER_MATERIALS.md`×2, `conf/code/figures_stagec3.py`×1, `conf/code/figures_stagec2.py`×2, `conf/code/figures_stagec.py`×1, `conf/code/figure_f14.py`×1, `conf/results/NUMBERS_PACKAGE_2026-09-22.md;`×1, `N/A`×1
- **2차 · 복잡도 4.6x·체크포인트 (P0-2b, cost/M1·M2, P0-1b, ckpt/M2)** — 18항목: `conf/code/bench_moduleH.py`×1, `conf/results/NUMBERS_PACKAGE_2026-09-22.md`×2, `conf/PAPER_MATERIALS.md`×4, `conf/results/jac_spectrum.txt,`×1, `conf/STATUS.md`×4, `conf/code/figures_stagec.py`×1, `conf/code/figures_stagec2.py`×1, `conf/10_SPEC_stageC.md`×2, `conf/DECISIONS.md`×1, `N/A`×1

---

## 1차 · 꼬리·반복 해석 (R-10.1, M-10.1a, R-10.2)

### tail-loop-1 · R-10.1 — `conf/STATUS.md` 1693, 1699, 1703 (원문). 삽입 위치: l.1705 뒤 (§3 문단 끝, l.1707 '## 4.' 앞), 위아래 빈 줄 1개씩

- 방식: **STATUS inline note** · ✏️ 검증 수정 반영 (인용 OK · 수치 OK · 문구 X)

**원문 (HEAD)**

```text
1693: ## 3. 그 꼬리는 **prior 의 문제가 아니다**
1699: | **겹침** | **250 — V1 꼬리의 87%** |
1703: V1 은 GMM 꼬리의 69% 를 이미 제거했고, 남은 꼬리는 **어느 prior 에게나 어려운 같은 채널 실현**이다.
```

**제안 문구**

```text
> **정정 (2026-09-23, review_next R-10.1)**: §3 제목 "그 꼬리는 prior 의 문제가 아니다" 와 l.1703 "남은 꼬리는 어느 prior 에게나
> 어려운 같은 채널 실현이다" 는 겹침 비율에서 원인을 추론한 과해석이다. 위 표 수치는 raw 에서 그대로 재현된다
> (V1 꼬리 289, GMM = `M-ours-bstar`(kron K=1024) 꼬리 813, 겹침 250 = V1 꼬리의 86.5%, V1 에만 39, GMM 에만 563).
> 그러나 (a) GMM 꼬리가 전체의 31.8%(813/2560)라, 두 꼬리가 무관하다면 V1 꼬리 중 GMM 꼬리 안에 드는 비율은 약 31.8% 다.
> 86.5% 는 두 arm 이 공유하는 어려운 블록이 있다는 뜻이지 꼬리가 prior 와 무관하다는 뜻이 아니다. (b) 같은 자료에서
> GMM 꼬리의 69.2%(563/813)는 V1 에서 꼬리가 아니다 — prior 와 Module H 가 함께 바뀌면 꼬리가 움직인다. V1 대 GMM 은
> 둘을 동시에 바꾸므로(`code/arms.py:34-38` MODULE_H, :163 bstar→`gmm_site`, :169 V1→`score`) 공동 실패로는 score·covariance
> calibration·cavity·반복 루프 중 원인을 가를 수 없고, 그것을 가르는 개입 실험은 인용되지 않았다.
> **대체 문구**: "남은 오류는 일부 어려운 블록에 집중되고 두 arm(V1·GMM)의 실패가 상당히 겹친다(V1 꼬리의 86.5% 가
> GMM 꼬리 안, V1 실패 371 중 321 이 GMM 도 실패). 공통 병목 가능성이 있으나 prior·interface·calibration 의 개선 여지는
> 배제되지 않았고, 확인하려면 별도 개입 실험이 필요하다." 출처: `raw_B16e4k` C2 −3 dB, n=2560, 꼬리 = 각 arm 의 NMSE@16 ≥ 0.12.
```

<details><summary>검증 agent 지적 / 초안 원안</summary>

지적: Quotes l.1693/1699/1703 match HEAD verbatim. Every number reproduces on an independent CPU re-derivation from the 64 raw_B16e4k C2 -3 dB npz files (n=2560, beta=0.7, t_in=5, bstar=kron K=1024 in every file): V1 tail 289, GMM tail 813, overlap 250 (0.8651), V1-only 39, GMM-only 563 (0.6925), GMM tail share 0.3176, fails 371/623, overlap 321 (0.8652). arms.py:34-38 is the MODULE_H dict; :163 bstar->gmm_site and :169 V1->score are the lines that actually show the two arms use different Module H. Three wording problems. (1) The replacement says 'prior·interface·calibration 의 개선 여지는 별도 개입 실험이 필요하다' but never says the headroom is 'not ruled out'. The task asks for that phrase, and the DECISIONS entry already has it. (2) It calls the two arms 'two priors' ('두 prior 의 실패'). The note's own argument is that V1 vs GMM changes the prior and Module H together, so this should read 'two arms (V1·GMM)'. (3) '우연 수준 겹침이 약 31.8%' is terse enough to misread; say that 31.8% is the expected share if the two tails were unrelated. Minor: the handoff §10.1 line cite (T2_DIFFUSION_CLI_HANDOFF_KO.md:545-551) appears only in the evidence. The handoff is an upload that is not on disk, so the cite cannot be checked. The proposed text does not depend on it.

초안 원안:

```text
> **정정 (2026-09-23, review_next R-10.1)**: §3 제목 "그 꼬리는 prior 의 문제가 아니다" 와 l.1703 "남은 꼬리는 어느 prior 에게나
> 어려운 같은 채널 실현이다" 는 겹침 비율에서 원인을 추론한 과해석이다. 위 표 수치는 raw 에서 그대로 재현된다
> (V1 꼬리 289, GMM = `M-ours-bstar`(kron K=1024) 꼬리 813, 겹침 250 = V1 꼬리의 86.5%, V1 에만 39, GMM 에만 563).
> 그러나 (a) GMM 꼬리가 전체의 31.8%(813/2560)라 우연 수준 겹침이 약 31.8% 다. 86.5% 는 두 arm 이 공유하는
> 어려운 블록이 있다는 뜻이지 꼬리가 prior 와 무관하다는 뜻이 아니다. (b) 같은 자료에서 V1 이 GMM 꼬리의
> 69.2%(563/813)를 없앴다 — prior 와 Module H 가 함께 바뀌면 꼬리가 움직인다. V1 대 GMM 은 둘을 동시에 바꾸므로
> (`code/arms.py:34-38`) 공동 실패로는 score·covariance calibration·cavity·반복 루프 중 원인을 가를 수 없고,
> 그것을 가르는 개입 실험은 인용되지 않았다.
> **대체 문구**: "남은 오류는 일부 어려운 블록에 집중되고 두 prior 의 실패가 상당히 겹친다(V1 꼬리의 86.5% 가
> GMM 꼬리 안, V1 실패 371 중 321 이 GMM 도 실패). 공통 병목 가능성이 있으나 prior·interface·calibration 의
> 개선 여지는 별도 개입 실험이 필요하다." 출처: `raw_B16e4k` C2 −3 dB, n=2560, 꼬리 = 각 arm 의 NMSE@16 ≥ 0.12.
```
</details>

<details><summary>근거</summary>

Re-derived (CPU) from conf/raw_B16e4k/D2_C2_S2_Nr8_T16_Tp4_dft_snr-3_skip*_n40.npz, all 64 files, n=2560 (run|beta=0.7, run|t_in=5, meta|bstar='kron', meta|kron_K=1024). Tail = nmse[:,15] >= 0.12. V1 (M-ours-dscore-C-V1) tail 289, GMM (M-ours-bstar) tail 813, overlap 250 = 0.8651 of V1 tail, V1-only 39, GMM-only 563 = 0.6925 of GMM tail (69.2%), GMM tail covers 813/2560 = 0.3176 of blocks. Failures blk_err[:,15]: V1 371, GMM 623, V1∩GMM 321 = 0.8652. BLER V1 0.1449, GMM 0.2434, genie 0.0340. V1 and bstar use different Module H (arms.py:34-38 MODULE_H 'score' vs 'gmm_site'; arms.py:163 bstar -> 'gmm_site'). Chance-level and 69% arguments come from REVIEW_AUDIT.md R-10.1 근거/반박 검토; handoff §10.1 wording from T2_DIFFUSION_CLI_HANDOFF_KO.md:545-551. Script: /tmp/claude-1005/-home-HTJ-t2-Demo/d3790660-21e8-42b4-971e-49b4049a6e64/scratchpad/rederive.py

검증: (위 참조)
</details>

### tail-loop-2 · M-10.1a — `conf/STATUS.md` 1704-1705 (원문). 삽입 위치: l.1705 뒤, R-10.1 정정 인용 바로 다음 (빈 줄로 구분)

- 방식: **STATUS inline note** · ✏️ 검증 수정 반영 (인용 OK · 수치 X · 문구 X)

**원문 (HEAD)**

```text
1704: 파일럿만 쓰는 첫 패스 NMSE(prior 무관)가 그것을 예측한다: 첫 패스 NMSE < 0.28 인 블록은 최종 꼬리비율
1705: 0.036·실패율 0.106, > 0.41 인 블록은 0.352·0.328.
```

**제안 문구**

```text
> **정정 (2026-09-23, review_next M-10.1a)**: l.1704-1705 의 인용값이 재현되는 "첫 패스 NMSE" 는 R0-pilot 반복 1 의 NMSE 다
> (R2-ours-G 반복 1 과 블록마다 동일, 중앙값 0.3183; V1 자신의 반복 1 NMSE 로는 재현되지 않는다). 이 첫 패스는 "prior 무관" 이 아니라
> 표본공분산 Gaussian prior 로 하는 파일럿 전용 LMMSE 다 — `GaussianPrior(Chat)`, Chat = 같은 N_train=160000 집합의 표본공분산
> (`code/arms.py:106-111`). GMM·diffusion 비교와 무관할 뿐이다. 두 구간도 문자 그대로의 임계값이 아니다: < 0.28 이면 n=693,
> 꼬리비율 0.038·실패율 0.108, > 0.41 이면 n=265, 0.343·0.321. 인용값 0.036·0.106 / 0.352·0.328 은 R0-pilot@1 NMSE 의
> **하위 25%**(n=640, < 0.27665) / **상위 10%**(n=256, ≥ 0.4124) 구간 값이다 (전체: 꼬리비율 0.113, V1 실패율 0.145).
> 문자 그대로의 구간으로도 방향은 같다.
> **대체 문구**: "파일럿 전용 첫 패스(R0-pilot@1, 표본공분산 Gaussian LMMSE — GMM·diffusion prior 와 무관) NMSE 가 최종 꼬리를
> 예측한다: 그 NMSE 하위 25%(n=640) 블록은 최종 꼬리비율 0.036·실패율 0.106, 상위 10%(n=256) 블록은 0.352·0.328."
> 출처: `raw_B16e4k` C2 −3 dB 재집계.
```

<details><summary>검증 agent 지적 / 초안 원안</summary>

지적: Quotes l.1704-1705 match verbatim. These reproduce: R0-pilot@1 == R2-ours-G@1 (allclose True), median 0.3183, V1's own @1 median 0.1688, the literal bins (<0.28: n=693, 0.038/0.108; >0.41: n=265, 0.343/0.321), the rank bins (bottom 640: 0.036/0.106; top 256: 0.352/0.328), and overall 0.113/0.145. arms.py:106-111 (Chat -> GaussianPrior -> R0-pilot pilot_only) is correct. NUMBERS FAIL: the stated bin edges '≤ 0.2766' and '≥ 0.4125' are rounded order statistics and do not work as literal thresholds. p1 ≤ 0.2766 selects 639 blocks, not 640, because the 640th value is 0.276623. p1 ≥ 0.4125 selects 255, not 256, because the 256th-from-top is 0.412461. That is exactly the kind of error this note corrects. The audit's '≤0.2768 / ≥0.4122' is also off (643/258). Valid literal edges are < 0.27665 (640) and ≥ 0.4124 (256). WORDING: (1) 'l.1704-1705 의 "첫 패스 NMSE" 는 R0-pilot 반복 1 의 NMSE 다' states as fact what is an identification: R0-pilot@1 is the quantity whose rank bins reproduce the quoted values. Say so, and note that V1's own @1 NMSE does not reproduce them. (2) The replacement's '그것을 예측한다' keeps a dangling '그것' whose antecedent (l.1703) is being corrected. Make the object explicit ('최종 꼬리를').

초안 원안:

```text
> **정정 (2026-09-23, review_next M-10.1a)**: l.1704-1705 의 "첫 패스 NMSE" 는 R0-pilot 반복 1 의 NMSE 다
> (R2-ours-G 반복 1 과 블록마다 동일, 중앙값 0.3183). 이 첫 패스는 "prior 무관" 이 아니라 표본공분산 Gaussian prior
> 로 하는 파일럿 전용 LMMSE 다 — `GaussianPrior(Chat)`, Chat = 같은 N_train=160000 집합의 표본공분산
> (`code/arms.py:106-111`). GMM·diffusion 비교와 무관할 뿐이다. 두 구간도 문자 그대로의 임계값이 아니다:
> < 0.28 이면 n=693, 꼬리비율 0.038·실패율 0.108, > 0.41 이면 n=265, 0.343·0.321. 인용값 0.036·0.106 /
> 0.352·0.328 은 R0-pilot@1 NMSE 의 **하위 25%**(n=640, ≤ 0.2766) / **상위 10%**(n=256, ≥ 0.4125) 구간 값이다
> (전체: 꼬리비율 0.113, V1 실패율 0.145). 문자 그대로의 구간으로도 방향은 같다.
> **대체 문구**: "파일럿 전용 첫 패스(R0-pilot@1, 표본공분산 Gaussian LMMSE — GMM·diffusion prior 와 무관) NMSE 가
> 그것을 예측한다: 그 NMSE 하위 25%(n=640) 블록은 최종 꼬리비율 0.036·실패율 0.106, 상위 10%(n=256) 블록은
> 0.352·0.328." 출처: `raw_B16e4k` C2 −3 dB 재집계.
```
</details>

<details><summary>근거</summary>

Same raw set. p1 = R0-pilot|nmse[:,0]; np.allclose(p1, R2-ours-G|nmse[:,0]) = True; median p1 0.3183 (matches tables_D2_B16e4k.txt NMSE med@1 0.3183 for R2). V1's own @1 median 0.1688 (not the source). Literal: p1<0.28 n=693 tail 0.038 fail 0.108; p1>0.41 n=265 tail 0.343 fail 0.321. Quantile: sorted p1 640th=0.27662 / 641st=0.27670 -> bottom 640 (25%) tail 0.036 fail 0.106; 2304th=0.41237 / 2305th=0.41246 -> top 256 (10%) tail 0.352 fail 0.328. Overall tail 289/2560=0.113, V1 fail 0.145. Prior of first pass: HEAD conf/code/arms.py:106-111 (Chat = fits[('full',32)]['Chat'] 'sample covariance of the SAME training set'; R0-pilot = route_a(..., Cs, ..., 'gaussian', mode='pilot_only')); raw meta|budget|R0-pilot = 'N_train=160000 -- ... its sample covariance Chat'.

검증: (위 참조)
</details>

### tail-loop-3 · R-10.2 — `conf/STATUS.md` 1707, 1709-1712, 1714-1715 (원문). 삽입 위치: l.1715 뒤 (§4 끝, l.1717 '## 5.' 앞), 위아래 빈 줄 1개씩

- 방식: **STATUS inline note** · ✏️ 검증 수정 반영 (인용 OK · 수치 OK · 문구 X)

**원문 (HEAD)**

```text
1707: ## 4. 그리고 반복을 늘려도 안 된다
1709: | 블록군 | NMSE it8 | it12 | it16 | BLER it8 → it16 |
1710: |---|---|---|---|---|
1711: | 비꼬리 | 0.0511 | 0.0505 | **0.0500** | 0.081 → 0.055 |
1712: | **꼬리** | 0.1853 | 0.1933 | **0.1938** | 0.862 → 0.848 |
1714: **꼬리 블록의 NMSE 는 반복 8 이후 개선되지 않고 오히려 미세하게 나빠진다.** EP 루프가 그 블록들에서
1715: **나쁜 고정점에 갇혀 있다.** 반복 수는 레버가 아니다.
```

**제안 문구**

```text
> **정정 (2026-09-23, review_next R-10.2)**: 위 표의 NMSE 는 **중앙값**이다(평균: 꼬리 0.2116/0.2146/0.2173,
> 비꼬리 0.0552/0.0541/0.0528). 수치는 raw 에서 재현되지만, §4 제목 "반복을 늘려도 안 된다" 와 l.1714-1715
> "나쁜 고정점에 갇혀 있다. 반복 수는 레버가 아니다" 는 진단 없이 쓴 과해석이다.
> (a) raw 가 반복마다 남기는 것은 blk_err·ber·nmse·tauL_gmean·alphaD·tauL_clip_frac·alphaD_clip 뿐이고 state
> residual 이 없다. 설정도 beta=0.7·t_in=5 하나다 — 고정점은 기존 자료로 진단할 수 없다.
> (b) 꼬리 289 중 it12→16 네 스텝의 최대 상대 NMSE 변화가 < 1e-3 인 블록은 76(26.3%), < 1e-2 는 121(41.9%);
> 스텝당 상대 변화 중앙값 0.7–1.2%.
> (c) 프로젝트의 BER 분류기(`Demo/exp_0921_analysis.py:54-60` fail_classes)로 꼬리 실패 245 = stuck 75 / cyc2 24 /
> other 146 (V1 실패 전체 371 = 113/38/220, `results/tables_D2_B16e4k.txt:88` 의 4.4/1.5/8.6% 와 일치).
> (d) 꼬리를 it16 NMSE 로 골랐다: NMSE@8 ≥ 0.12 로 고르면(n=317) 중앙값 it8/12/16 = 0.1829/0.1824/0.1791.
> (e) 같은 설정에서 V1 전체 실패는 it8 433 → it16 371 (순감 62 = 433 의 14.3%; BLER 0.169 → 0.145, 같은 표 :88) —
> "반복 수는 레버가 아니다" 는 이 설정 전체에도 맞지 않는다.
> **대체 문구**: "현재 설정(beta=0.7, t_in=5)에서 NMSE@16 ≥ 0.12 로 고른 꼬리 블록의 NMSE 는 반복 8→16 에서
> 개선되지 않는다(중앙값 0.1853→0.1938). 이 비교는 it16 으로 고른 블록군이라 '개선 없음' 쪽으로 치우친다
> (NMSE@8 ≥ 0.12 로 고르면 0.1829→0.1791). BER 분류기로 꼬리 실패 245 중 99 는 stuck·2-cycle, 146 은 other 다.
> 같은 설정에서 전체 V1 실패는 반복 8→16 에 433→371 로 준다. 현재 자료는 다른 damping·inner update·schedule·
> restart 가 무효임을 보이지 않는다." "고정점" 은 state residual·cycle·수렴 진단이 생길 때까지 쓰지 않는다.
```

<details><summary>검증 agent 지적 / 초안 원안</summary>

지적: Quotes l.1707, 1709-1712, 1714-1715 match verbatim. All numbers reproduce. Tail medians 0.1853/0.1933/0.1938, means 0.2116/0.2146/0.2173, BLER 0.862->0.848. Nontail medians 0.0511/0.0505/0.0500, means 0.0552/0.0541/0.0528, BLER 0.081->0.055. Max relative change it12->16: 76 blocks (26.3%) below 1e-3, 121 (41.9%) below 1e-2; per-step medians 0.0124/0.0074/0.0088/0.0072. fail_classes (exp_0921_analysis.py:54-60, applied verbatim): all V1 fails 371 = 113/38/220 (4.4/1.5/8.6%, matching tables:88), tail fails 245 = 75/24/146. Selecting on @8 gives n=317 with medians 0.1829/0.1824/0.1791. Population fails 433 -> 371. Per-iteration raw keys and the single beta/t_in setting are confirmed in the npz. WORDING: the replacement '현재 설정의 반복 정체를 보일 뿐' still carries part of the over-claim. Points (d) and (e) show the stagnation holds only for a block set selected on it16. In the same beta=0.7, t_in=5 setting, iterations 8->16 cut V1 failures by 62 net (433 -> 371, 14.3%). So 'iterations are not a lever' fails even for the current setting overall. The audit states this explicitly, and its suggested replacement also carries the classifier split (99/245 stuck or 2-cycle, 146 other). The replacement should state the selection caveat, the population result and the classifier split, not only list them in (a)-(e). Point (e) should also state its implication.

초안 원안:

```text
> **정정 (2026-09-23, review_next R-10.2)**: 위 표의 NMSE 는 **중앙값**이다(평균: 꼬리 0.2116/0.2146/0.2173,
> 비꼬리 0.0552/0.0541/0.0528). 수치는 raw 에서 재현되지만, §4 제목 "반복을 늘려도 안 된다" 와 l.1714-1715
> "나쁜 고정점에 갇혀 있다. 반복 수는 레버가 아니다" 는 진단 없이 쓴 과해석이다.
> (a) raw 가 반복마다 남기는 것은 blk_err·ber·nmse·tauL_gmean·alphaD·tauL_clip_frac·alphaD_clip 뿐이고 state
> residual 이 없다. 설정도 beta=0.7·t_in=5 하나다 — 고정점은 기존 자료로 진단할 수 없다.
> (b) 꼬리 289 중 it12→16 네 스텝의 최대 상대 NMSE 변화가 < 1e-3 인 블록은 76(26.3%), < 1e-2 는 121(41.9%);
> 스텝당 상대 변화 중앙값 0.7–1.2%.
> (c) 프로젝트의 BER 분류기(`Demo/exp_0921_analysis.py:54-60` fail_classes)로 꼬리 실패 245 = stuck 75 / cyc2 24 /
> other 146 (V1 실패 전체 371 = 113/38/220, `results/tables_D2_B16e4k.txt:88` 의 4.4/1.5/8.6% 와 일치).
> (d) 꼬리를 it16 NMSE 로 골랐다: NMSE@8 ≥ 0.12 로 고르면(n=317) 중앙값 it8/12/16 = 0.1829/0.1824/0.1791.
> (e) V1 전체 실패는 it8 433 → it16 371 (BLER 0.169 → 0.145, 같은 표 :88).
> **대체 문구**: "현재 설정(beta=0.7, t_in=5)에서 NMSE@16 ≥ 0.12 로 고른 꼬리 블록의 NMSE 는 반복 8→16 에서
> 개선되지 않는다(중앙값 0.1853→0.1938). 현재 설정의 반복 정체를 보일 뿐, 다른 damping·inner update·schedule·
> restart 가 무효임을 보이지 않는다." "고정점" 은 state residual·cycle·수렴 진단이 생길 때까지 쓰지 않는다.
```
</details>

<details><summary>근거</summary>

Same raw set, V1 = M-ours-dscore-C-V1, tail = nmse[:,15]>=0.12 (n=289), nontail n=2271. Tail median nmse it8/12/16 (cols 7/11/15) 0.1853/0.1933/0.1938, mean 0.2116/0.2146/0.2173, BLER col7->col15 0.862->0.848. Nontail median 0.0511/0.0505/0.0500, mean 0.0552/0.0541/0.0528, BLER 0.081->0.055. Per-block rel change |diff|/prev over nmse cols 11..15 (it12->16, 4 steps): max<1e-3 76/289=0.263, <1e-2 121/289=0.419; per-step median 0.0124/0.0074/0.0088/0.0072. Selection on nmse[:,7]>=0.12: n=317, medians 0.1829/0.1824/0.1791. Population V1 fails col7 433 (0.1691) -> col15 371 (0.1449); tables_D2_B16e4k.txt:88 'BLER@1/@2/@8/@16 = 0.574 0.320 0.169 0.145 ... fail% stuck/cyc2/other=4.4/1.5/8.6'. fail_classes applied verbatim (Demo/exp_0921_analysis.py:54-60): all V1 fails (371, 113, 38, 220); tail∩fail (245, 75, 24, 146). Per-iteration raw fields (40,16): blk_err, ber, nmse, tauL_gmean, alphaD, tauL_clip_frac, alphaD_clip; run|beta=0.7, run|t_in=5 scalars. Handoff §10.2 wording: T2_DIFFUSION_CLI_HANDOFF_KO.md:553-555.

검증: (위 참조)
</details>

### tail-loop-4 · R-10.1, R-10.2 — `conf/STATUS.md` 1719-1721 (원문; l.1723-1724 는 참조만). 삽입 위치: l.1721 뒤 (l.1723 '**남은 레버는' 앞), 위아래 빈 줄 1개씩

- 방식: **STATUS inline note** · ✏️ 검증 수정 반영 (인용 OK · 수치 OK · 문구 X)

**원문 (HEAD)**

```text
1719: **측정으로 배제된 것** (전부 이 프로젝트에서 이미 잰 값):
1720: 데이터 16배 (0.145 불변) · GMM 성분 4배 (격차 42.7→40.5%) · 반복 추가 (꼬리 NMSE 평탄) ·
1721: score 를 더 잘 학습 (꼬리가 prior 와 87% 무관).
[참조] 1723: **남은 레버는 수신기 루프의 탈출 능력이다.** 감쇠 β=0.7 과 내부 반복 t_in=5 는 Stage A 에서 고정된 뒤
[참조] 1724: **한 번도 조정된 적이 없고**, 꼬리 블록은 정확히 "초기 추정이 나빠 루프가 갇히는" 사례다. 재시작·감쇠
```

**제안 문구**

```text
> **정정 (2026-09-23, review_next R-10.1 · R-10.2)**: "반복 추가 (꼬리 NMSE 평탄)" 와 "score 를 더 잘 학습
> (꼬리가 prior 와 87% 무관)" 은 측정으로 배제된 것이 아니다. 87% 는 V1 꼬리 중 GMM 꼬리와 겹치는 비율
> (250/289 = 86.5%)이지 prior 와의 무관함이 아니며(§3 R-10.1 정정), 평탄은 beta=0.7·t_in=5 한 설정에서 it16
> NMSE 로 고른 꼬리의 중앙값이다 — 같은 설정에서 전체 V1 실패는 반복 8→16 에 433→371 로 준다(§4 R-10.2 정정).
> 두 항목은 이 목록에서 빼고 다음으로 읽는다: "반복 추가 — 현재 설정에서 it16 으로 고른 꼬리의 NMSE 정체, 다른
> damping·inner update·schedule·restart 는 미검증 · score 개선 — 배제되지 않음, 두 arm(V1·GMM)의 꼬리가 크게 겹치며
> prior·interface·calibration 개선 여지는 별도 개입 실험 필요." 데이터 16배·GMM 성분 4배 항목은 이 정정의 범위가
> 아니다. 이어지는 l.1723-1724 는 두 배제를 전제로 한 문장이므로 "남은 레버는 수신기 루프의 탈출 능력이다" 는
> "β·t_in(Stage A 이후 조정 안 됨)과 재시작·감쇠 스케줄·σ 어닐링은 prior·interface 개선과 나란히 미검증 후보다" 로,
> "루프가 갇히는" 은 §4 정정과 같이 진단 없는 표현으로 읽는다. l.1725-1727 의 선택 규칙(BLER 이 아닌 기준,
> 전 arm 동일 적용, 사전 등록)은 그대로 유효하다.
```

<details><summary>검증 agent 지적 / 초안 원안</summary>

지적: Quotes l.1719-1721 and the reference lines 1723-1724 match verbatim. The numbers (250/289 = 86.5%, beta/t_in, it16 selection) check out. Touching l.1723-1724 goes beyond the audit's cited ranges (R-10.1: 1717-1721; R-10.2: 1707-1715, 1720), but it is the sentence that rests on the two exclusions, the DECISIONS entry corrects the same conclusion, and the drafter flags this. Acceptable. WORDING: (1) '"β·t_in·재시작·σ 어닐링은 Stage A 이후 조정되지 않은 후보다"' attributes 'not tuned since Stage A' to restart and σ annealing. The original l.1723-1725 says only β and t_in were fixed at Stage A and never tuned. Restart, damping schedule and σ annealing are separate proposed mechanisms, and the draft drops 감쇠 스케줄. It also leaves them looking like the remaining lever, when score/interface headroom is not ruled out. (2) '현재 설정에서 꼬리 NMSE 정체' drops the it16 selection caveat, and the population result 433->371 in the same setting is missing (see the R-10.2 STATUS check). (3) '두 prior 의 꼬리' should read '두 arm(V1·GMM)', as in the R-10.1 check.

초안 원안:

```text
> **정정 (2026-09-23, review_next R-10.1 · R-10.2)**: "반복 추가 (꼬리 NMSE 평탄)" 와 "score 를 더 잘 학습
> (꼬리가 prior 와 87% 무관)" 은 측정으로 배제된 것이 아니다. 87% 는 V1 꼬리 중 GMM 꼬리와 겹치는 비율
> (250/289 = 86.5%)이지 prior 와의 무관함이 아니며(§3 R-10.1 정정), 평탄은 beta=0.7·t_in=5 한 설정에서 it16
> NMSE 로 고른 꼬리의 중앙값이다(§4 R-10.2 정정). 두 항목은 이 목록에서 빼고 다음으로 읽는다: "반복 추가 —
> 현재 설정에서 꼬리 NMSE 정체, 다른 damping·inner update·schedule·restart 는 미검증 · score 개선 — 배제되지
> 않음, 두 prior 의 꼬리가 크게 겹치며 prior·interface·calibration 개선 여지는 별도 개입 실험 필요." 데이터
> 16배·GMM 성분 4배 항목은 이 정정의 범위가 아니다. 이어지는 l.1723-1724 는 두 배제를 전제로 한 문장이므로
> "남은 레버는 수신기 루프의 탈출 능력이다" 는 "β·t_in·재시작·σ 어닐링은 Stage A 이후 조정되지 않은 후보다"
> 로, "루프가 갇히는" 은 §4 정정과 같이 진단 없는 표현으로 읽는다. l.1725-1727 의 선택 규칙(BLER 이 아닌 기준,
> 전 arm 동일 적용, 사전 등록)은 그대로 유효하다.
```
</details>

<details><summary>근거</summary>

Numbers as in the R-10.1 and R-10.2 entries (same raw re-derivation): overlap 250/289=0.8651; tail medians 0.1853/0.1933/0.1938 at beta=0.7, t_in=5 (run|beta, run|t_in); tail selected on nmse[:,15]. Audit locations: REVIEW_AUDIT.md R-10.1 (STATUS:1717-1721) and R-10.2 (STATUS:1720). l.1723-1724 is not cited by the audit; it is referenced only because it is the sentence that follows from the two exclusions, and the note does not alter l.1725-1727. Wording from handoff §10.1/§10.2 (T2_DIFFUSION_CLI_HANDOFF_KO.md:545-555).

검증: (위 참조)
</details>

### tail-loop-5 · R-10.1 — `conf/DECISIONS.md` 105 (신규 append, 현재 마지막 줄 104 뒤). 정정 대상: l.104

- 방식: **DECISIONS append** · ✏️ 검증 수정 반영 (인용 OK · 수치 OK · 문구 X)

**원문 (HEAD)**

```text
104 (발췌): `[2026-09-23 00:10 KST] "genie 에 더 붙일 수 있나" — 재분석으로 답했고, 다음 레버가 prior 가 아님을 확인했다 | ... (3) 그 꼬리는 **GMM 꼬리와 87% 겹치고** 파일럿 전용 첫 패스 NMSE 가 예측한다 → **prior 의 문제가 아니라 채널 실현의 문제**. ... | 결론: 데이터·성분·반복·score 품질은 전부 측정으로 배제됐다. 남은 레버는 **수신기 루프의 탈출 능력**(감쇠 β=0.7, 내부 반복 t_in=5 — Stage A 이후 한 번도 조정 안 됨, 재시작, σ 어닐링)이다 | ...`
```

**제안 문구**

```text
(l.105 빈 줄, l.106 에 append)
`[2026-09-23 __:__ KST] 정정 — genie 격차 해부의 "꼬리가 GMM 꼬리와 87% 겹침 → prior 의 문제가 아님, score 품질은 측정으로 배제" 는 과해석이다 (review_next R-10.1) | [2026-09-23 00:10] 항목의 제목 "다음 레버가 prior 가 아님을 확인했다", (3) "그 꼬리는 GMM 꼬리와 87% 겹치고 … → prior 의 문제가 아니라 채널 실현의 문제", 결론의 "score 품질은 … 측정으로 배제됐다" 는 겹침 비율에서 원인을 추론한 것이다. 다음으로 바꿔 읽는다: "남은 오류는 일부 어려운 블록에 집중되고 두 arm(V1·GMM)의 실패가 상당히 겹친다. 공통 병목 가능성이 있으나 prior·interface·calibration 의 개선 여지는 배제되지 않았고 별도 개입 실험이 필요하다." (3) 의 "파일럿 전용 첫 패스" 는 prior 가 없는 것이 아니라 표본공분산 Gaussian LMMSE(R0-pilot 반복 1)다 (STATUS M-10.1a 정정). 커밋 6ed06139 의 제목("꼬리는 prior 가 아니라 …")과 본문("꼬리는 GMM 꼬리와 87% 겹치고", "score 품질은 측정으로 배제되고")도 같은 과해석이다 — 이미 origin/main 에 push 됐고 뒤에 커밋 3개가 있어 메시지는 고치지 않으며 이 줄이 그 정정이다. (1)(2) 와 데이터·성분 배제는 이 정정의 범위가 아니다 ((1) 은 review_next R-10.3 항목) | raw_B16e4k C2 −3 dB n=2560 재집계, 꼬리 = NMSE@16 ≥ 0.12: V1(M-ours-dscore-C-V1) 꼬리 289, GMM(M-ours-bstar, kron K=1024) 꼬리 813, 겹침 250 = V1 꼬리의 86.5%, V1 에만 39, GMM 에만 563. 실패 기준으로도 V1 실패 371 중 321(86.5%)이 GMM 실패. (a) 같은 자료에서 GMM 꼬리의 69.2%(563/813)는 V1 에서 꼬리가 아니다 — prior 와 Module H 가 함께 바뀌면 꼬리가 움직인다. V1 대 GMM 은 둘을 동시에 바꾸므로(code/arms.py:34-38 MODULE_H, :163 bstar→gmm_site, :169 V1→score) 공동 실패로 score·calibration·cavity·루프 원인을 가를 수 없고, 인용된 개입 실험이 없다. (b) GMM 꼬리가 전체의 31.8%(813/2560)라 두 꼬리가 무관할 때의 겹침은 약 31.8% 다 — 86.5% 는 공유된 어려운 블록을 지지하지만 prior 와의 무관함을 뜻하지 않는다 | 원문은 그대로 두고 정정만 덧붙인다 — 코드·raw·표·그림 무변경, STATUS 에는 l.1705·l.1721 뒤 정정 인용으로 남긴다. 철회하려면 이 정정을 무르는 새 줄을 append 한다`
```

<details><summary>검증 agent 지적 / 초안 원안</summary>

지적: The elided excerpts all occur verbatim in l.104 (checked fragment by fragment). The entry keeps the 4-field format with exactly 3 ' | ' separators and no stray '|'. The commit facts hold: 6ed06139 is on origin/main and is followed by 54e8047c, 4ad41df9, cd241b7e. All numbers match the raw re-derivation. Problems. (1) Placement: from l.90 on, DECISIONS entries are separated by a blank line (l.91, 93, ..., 103 are blank). The new line should be l.106 after a blank l.105, not l.105. (2) Field 4 opens '기록 문구만 바꾼다'. Under the append-only / never-rewrite convention nothing is rewritten, and the phrase could lead an applier to edit l.104. Use '원문은 그대로 두고 정정만 덧붙인다'. (3) '두 prior 의 실패' should read '두 arm(V1·GMM)의 실패' (the entry itself says the arms differ in prior and Module H). (4) '(code/arms.py:34-38)' should add :163/:169, the lines where each arm picks its Module H. (5) 'V1 이 GMM 꼬리의 69.2%를 없앴다' is acceptable (it mirrors the record and audit). Rephrased below as a cross-arm fact to avoid a causal reading. The 'not ruled out + intervention experiment' phrasing is correct here.

초안 원안:

```text
`[2026-09-23 __:__ KST] 정정 — genie 격차 해부의 "꼬리가 GMM 꼬리와 87% 겹침 → prior 의 문제가 아님, score 품질은 측정으로 배제" 는 과해석이다 (review_next R-10.1) | [2026-09-23 00:10] 항목의 제목 "다음 레버가 prior 가 아님을 확인했다", (3) "그 꼬리는 GMM 꼬리와 87% 겹치고 … → prior 의 문제가 아니라 채널 실현의 문제", 결론의 "score 품질은 … 측정으로 배제됐다" 는 겹침 비율에서 원인을 추론한 것이다. 다음으로 바꿔 읽는다: "남은 오류는 일부 어려운 블록에 집중되고 두 prior 의 실패가 상당히 겹친다. 공통 병목 가능성이 있으나 prior·interface·calibration 의 개선 여지는 배제되지 않았고 별도 개입 실험이 필요하다." (3) 의 "파일럿 전용 첫 패스" 는 prior 가 없는 것이 아니라 표본공분산 Gaussian LMMSE(R0-pilot 반복 1)다 (STATUS M-10.1a 정정). 커밋 6ed06139 의 제목("꼬리는 prior 가 아니라 …")과 본문("꼬리는 GMM 꼬리와 87% 겹치고", "score 품질은 측정으로 배제되고")도 같은 과해석이다 — 이미 origin/main 에 push 됐고 뒤에 커밋 3개가 있어 메시지는 고치지 않으며 이 줄이 그 정정이다. (1)(2) 와 데이터·성분 배제는 이 정정의 범위가 아니다 ((1) 은 review_next R-10.3 항목) | raw_B16e4k C2 −3 dB n=2560 재집계, 꼬리 = NMSE@16 ≥ 0.12: V1(M-ours-dscore-C-V1) 꼬리 289, GMM(M-ours-bstar, kron K=1024) 꼬리 813, 겹침 250 = V1 꼬리의 86.5%, V1 에만 39, GMM 에만 563. 실패 기준으로도 V1 실패 371 중 321(86.5%)이 GMM 실패. (a) 같은 자료에서 V1 이 GMM 꼬리의 69.2%(563/813)를 없앴다 — prior 와 Module H 가 함께 바뀌면 꼬리가 움직인다. V1 대 GMM 은 둘을 동시에 바꾸므로(code/arms.py:34-38) 공동 실패로 score·calibration·cavity·루프 원인을 가를 수 없고, 인용된 개입 실험이 없다. (b) GMM 꼬리가 전체의 31.8%(813/2560)라 우연 수준 겹침은 약 31.8% 다 — 86.5% 는 공유된 어려운 블록을 지지하지만 prior 와의 무관함을 뜻하지 않는다 | 기록 문구만 바꾼다 — 코드·raw·표·그림 무변경, STATUS 에는 l.1705·l.1721 뒤 정정 인용으로 남긴다. 철회하려면 이 정정을 무르는 새 줄을 append 한다`
```
</details>

<details><summary>근거</summary>

Raw re-derivation as in STATUS R-10.1 entry (V1 tail 289, GMM tail 813, overlap 250 = 0.8651, V1-only 39, GMM-only 563 = 0.6925, GMM tail 0.3176 of 2560, fails 371/623, V1∩GMM 321 = 0.8652). DECISIONS.md at HEAD has 104 lines; l.104 is the [2026-09-23 00:10 KST] entry; format copied from l.26 '[2026-09-20 13:25 KST] 정정 — …'. Commit facts: `git log 6ed06139..HEAD` = 54e8047c, 4ad41df9, cd241b7e; `git branch -r --contains 6ed06139` = origin/main. No '|' inside fields other than the 3 separators.

검증: (위 참조)
</details>

### tail-loop-6 · R-10.2 — `conf/DECISIONS.md` 106 (신규 append, R-10.1 정정 줄 뒤). 정정 대상: l.104

- 방식: **DECISIONS append** · ✏️ 검증 수정 반영 (인용 OK · 수치 OK · 문구 X)

**원문 (HEAD)**

```text
104 (발췌): `... (4) 꼬리 블록의 NMSE 는 반복 8→16 에서 개선되지 않는다(0.1853→0.1938) → **루프가 나쁜 고정점에 갇힌 것**이지 반복 부족이 아니다 | 결론: 데이터·성분·반복·score 품질은 전부 측정으로 배제됐다. 남은 레버는 **수신기 루프의 탈출 능력**(감쇠 β=0.7, 내부 반복 t_in=5 — Stage A 이후 한 번도 조정 안 됨, 재시작, σ 어닐링)이다 | **주의**: β·t_in 은 arm 이 아니라 전 arm 공통 파라미터다. ...`
```

**제안 문구**

```text
(l.107 빈 줄, l.108 에 append)
`[2026-09-23 __:__ KST] 정정 — genie 격차 해부의 "꼬리 NMSE 가 반복 8→16 에서 평탄 → 루프가 나쁜 고정점에 갇힘, 반복은 측정으로 배제" 는 진단 없는 과해석이다 (review_next R-10.2) | [2026-09-23 00:10] 항목의 (4) "루프가 나쁜 고정점에 갇힌 것이지 반복 부족이 아니다" 와 결론의 "반복 … 측정으로 배제됐다" 를 다음으로 바꿔 읽는다: "현재 설정(beta=0.7, t_in=5)에서 NMSE@16 ≥ 0.12 로 고른 꼬리 블록의 NMSE 는 반복 8→16 에서 개선되지 않는다(중앙값 0.1853→0.1938). 이 비교는 it16 으로 고른 블록군이라 '개선 없음' 쪽으로 치우치고, 같은 설정에서 전체 V1 실패는 반복 8→16 에 433→371 로 준다. BER 분류기로 꼬리 실패 245 중 99 는 stuck·2-cycle, 146 은 other 다. 현재 자료는 다른 damping·inner update·schedule·restart 가 무효임을 보이지 않는다." "고정점" 은 state residual·cycle·수렴 진단이 생길 때까지 쓰지 않는다. 커밋 6ed06139 의 제목("루프의 고정점 문제다")과 본문("루프가 갇힌 것", "반복 … 측정으로 배제되고")도 같은 과해석이며, 메시지는 고치지 않고 이 줄이 그 정정이다. 앞 줄(R-10.1)과 합쳐 결론의 "남은 레버는 수신기 루프의 탈출 능력" 은 "β·t_in(Stage A 이후 조정 안 됨)과 재시작·σ 어닐링은 prior·interface 개선과 나란히 미검증 후보" 로 읽고, 유일한 레버라는 근거는 없다. 원 항목의 주의 (i)–(iii)(BLER 이 아닌 기준, 전 arm 동일 적용, 사전 등록)는 그대로다 | raw_B16e4k C2 −3 dB 재집계, V1(M-ours-dscore-C-V1), 꼬리 n=289: NMSE 중앙값 it8/12/16 = 0.1853/0.1933/0.1938(평균 0.2116/0.2146/0.2173; 원문은 중앙값임을 적지 않았다), 꼬리 BLER 0.862→0.848. (a) raw 는 반복마다 blk_err·ber·nmse·tauL_gmean·alphaD·tauL_clip_frac·alphaD_clip 만 남기고 state residual 이 없으며 beta=0.7·t_in=5 한 설정뿐이다 — 고정점은 기존 자료로 진단할 수 없다. (b) 꼬리 중 it12→16 네 스텝 최대 상대 NMSE 변화 < 1e-3 은 76(26.3%), < 1e-2 는 121(41.9%). (c) BER 분류기(Demo/exp_0921_analysis.py:54-60)로 꼬리 실패 245 = stuck 75 / cyc2 24 / other 146. (d) NMSE@8 ≥ 0.12 로 고르면(n=317) 중앙값 0.1829/0.1824/0.1791 — it16 선택 편향. (e) V1 전체 실패 it8 433 → it16 371(순감 62 = 14.3%; BLER 0.169→0.145, results/tables_D2_B16e4k.txt:88) — 같은 설정에서도 반복은 전체 실패를 줄인다 | 원문은 그대로 두고 정정만 덧붙인다 — 코드·raw·표·그림 무변경, STATUS 에는 l.1715·l.1721 뒤 정정 인용으로 남긴다. 철회하려면 이 정정을 무르는 새 줄을 append 한다`
```

<details><summary>검증 agent 지적 / 초안 원안</summary>

지적: The elided excerpt occurs verbatim in l.104. The entry has 3 separators and no stray '|'. The numbers reproduce (medians and means, BLER 0.862->0.848, 76/121 of 289, 245 = 75/24/146, @8 selection n=317 0.1829/0.1824/0.1791, 433 -> 371, tables:88). Problems. (1) Placement should be l.108 after a blank l.107 (blank-line convention), not l.106. (2) The replacement wording '현재 설정의 반복 정체를 보일 뿐' has the same gap as the STATUS R-10.2 entry. It omits the it16 selection caveat and the population result: in the same setting, 8 extra iterations remove 62 of 433 failures (14.3%), so 'iterations are not a lever' fails even there. The audit's suggested replacement also carries the 99/245 classifier split. Field 3 lists these facts, but the text readers will adopt is the replacement. (3) '"β·t_in·재시작·σ 어닐링은 Stage A 이후 조정되지 않은 후보"' misattributes 'not tuned since Stage A' to restart and σ annealing. l.104's parenthetical attaches it to β and t_in only. (4) Field 4 '기록 문구만 바꾼다' has the same problem as in the R-10.1 line; use '원문은 그대로 두고 정정만 덧붙인다'.

초안 원안:

```text
`[2026-09-23 __:__ KST] 정정 — genie 격차 해부의 "꼬리 NMSE 가 반복 8→16 에서 평탄 → 루프가 나쁜 고정점에 갇힘, 반복은 측정으로 배제" 는 진단 없는 과해석이다 (review_next R-10.2) | [2026-09-23 00:10] 항목의 (4) "루프가 나쁜 고정점에 갇힌 것이지 반복 부족이 아니다" 와 결론의 "반복 … 측정으로 배제됐다" 를 다음으로 바꿔 읽는다: "현재 설정(beta=0.7, t_in=5)에서 NMSE@16 ≥ 0.12 로 고른 꼬리 블록의 NMSE 는 반복 8→16 에서 개선되지 않는다(중앙값 0.1853→0.1938). 현재 설정의 반복 정체를 보일 뿐, 다른 damping·inner update·schedule·restart 가 무효임을 보이지 않는다." "고정점" 은 state residual·cycle·수렴 진단이 생길 때까지 쓰지 않는다. 커밋 6ed06139 의 제목("루프의 고정점 문제다")과 본문("루프가 갇힌 것", "반복 … 측정으로 배제되고")도 같은 과해석이며, 메시지는 고치지 않고 이 줄이 그 정정이다. 앞 줄(R-10.1)과 합쳐 결론의 "남은 레버는 수신기 루프의 탈출 능력" 은 "β·t_in·재시작·σ 어닐링은 Stage A 이후 조정되지 않은 후보" 로 읽고, 유일한 레버라는 근거는 없다. 원 항목의 주의 (i)–(iii)(BLER 이 아닌 기준, 전 arm 동일 적용, 사전 등록)는 그대로다 | raw_B16e4k C2 −3 dB 재집계, V1(M-ours-dscore-C-V1), 꼬리 n=289: NMSE 중앙값 it8/12/16 = 0.1853/0.1933/0.1938(평균 0.2116/0.2146/0.2173; 원문은 중앙값임을 적지 않았다), 꼬리 BLER 0.862→0.848. (a) raw 는 반복마다 blk_err·ber·nmse·tauL_gmean·alphaD·tauL_clip_frac·alphaD_clip 만 남기고 state residual 이 없으며 beta=0.7·t_in=5 한 설정뿐이다 — 고정점은 기존 자료로 진단할 수 없다. (b) 꼬리 중 it12→16 네 스텝 최대 상대 NMSE 변화 < 1e-3 은 76(26.3%), < 1e-2 는 121(41.9%). (c) BER 분류기(Demo/exp_0921_analysis.py:54-60)로 꼬리 실패 245 = stuck 75 / cyc2 24 / other 146. (d) NMSE@8 ≥ 0.12 로 고르면(n=317) 중앙값 0.1829/0.1824/0.1791 — it16 선택 편향. (e) V1 전체 실패 it8 433 → it16 371(BLER 0.169→0.145, results/tables_D2_B16e4k.txt:88) | 기록 문구만 바꾼다 — 코드·raw·표·그림 무변경, STATUS 에는 l.1715·l.1721 뒤 정정 인용으로 남긴다. 철회하려면 이 정정을 무르는 새 줄을 append 한다`
```
</details>

<details><summary>근거</summary>

Raw re-derivation as in STATUS R-10.2 entry: tail medians 0.1853/0.1933/0.1938, means 0.2116/0.2146/0.2173, BLER 0.862->0.848; max rel change it12->16 <1e-3 76/289=26.3%, <1e-2 121/289=41.9%; fail_classes tail (245, 75, 24, 146), all V1 (371, 113, 38, 220) matching tables_D2_B16e4k.txt:88 4.4/1.5/8.6%; select@8 n=317 medians 0.1829/0.1824/0.1791; population fails 433->371 (0.1691->0.1449). Per-iteration raw fields and run|beta=0.7, run|t_in=5 read from the npz keys. Wording from handoff §10.2 (T2_DIFFUSION_CLI_HANDOFF_KO.md:553-555).

검증: (위 참조)
</details>

### tail-loop-7 · R-10.1, R-10.2 — `git commit 6ed06139 (commit message)` 메시지 l.1, l.5, l.6, l.8-9

- 방식: **other** · ✅ 검증 통과

**원문 (HEAD)**

```text
1: conf: genie 격차 해부 — 수준이 아니라 꼬리 문제이고, 꼬리는 prior 가 아니라 루프의 고정점 문제다
5: 0.9% 로 genie 수준이다.  꼬리는 GMM 꼬리와 87% 겹치고 파일럿 전용 첫 패스 NMSE 가 예측한다.
6: 꼬리 NMSE 는 반복 8->16 에서 개선되지 않는다(0.1853->0.1938) - 루프가 갇힌 것.
8: 따라서 데이터/성분/반복/score 품질은 측정으로 배제되고, 남은 레버는 수신기 루프의
9: 탈출 능력(beta, t_in, 재시작, sigma 어닐링)이다.  전 arm 공통 파라미터이므로 BLER 이
```

**제안 문구**

```text
편집 없음. 이 커밋은 origin/main 에 push 됐고 뒤에 54e8047c·4ad41df9·cd241b7e 가 있어, 메시지를 고치려면 이력 재작성(force push)이 필요하다 — 하지 않는다. 정정은 DECISIONS 에 append 하는 두 줄이 담는다: R-10.1 줄(l.1 '꼬리는 prior 가 아니라', l.5 '87% 겹치고', l.8 'score 품질은 측정으로 배제') 과 R-10.2 줄(l.1 '루프의 고정점 문제', l.6 '루프가 갇힌 것', l.8 '반복 … 배제'). (선택) 이 정정을 적용하는 커밋 메시지에 '6ed06139 메시지의 과해석 정정 — DECISIONS 2026-09-23 정정 R-10.1/R-10.2 참조' 한 줄을 넣으면 git log 에서도 추적된다.
```

<details><summary>근거</summary>

git log -1 --format=%B 6ed06139 (lines numbered with cat -n); git log --oneline 6ed06139..HEAD = cd241b7e, 4ad41df9, 54e8047c; git branch -r --contains 6ed06139 = origin/main. The numbers the commit quotes (87%, 0.1853->0.1938) reproduce from raw_B16e4k (overlap 250/289 = 86.5%; tail medians); only the inferences are corrected.

검증: Message lines 1, 5, 6, 8, 9 match `git log -1 --format=%B 6ed06139` verbatim, including the double spaces on l.5 and l.9. 6ed06139 is on origin/main and is followed by 54e8047c, 4ad41df9, cd241b7e, so fixing the message would mean a force push; declining is right. The quoted 87% and 0.1853->0.1938 reproduce (250/289 = 86.5%; tail medians). Nit only: the DECISIONS lines will sit at l.106/l.108 (blank-line convention), not l.105/l.106.
</details>

### 1차 검증이 찾은 누락 위치 (→ 2차에서 초안 작성)

<details><summary>원문</summary>

No missed places carry the same wording. I grepped HEAD and the working tree (STATUS.md, DECISIONS.md, PAPER_MATERIALS.md, conf/*.md, conf/results/*.txt, conf/figs/*.txt captions, conf/code/*.py, docs/**/*.md including EXPERIMENTS.md and RESULTS.md) for 87%, 고정점/fixed point, prior 무관/prior-free, prior 의 문제가 아니, 채널 실현, 측정으로 배제, 탈출 능력, 레버, 반복을 늘려도, 갇히/갇힌, 0.1853/0.1938, 250/289, 563/813, 첫 패스. The only hits are STATUS l.1693/1699/1703/1704/1707/1715/1719-1721/1723-1724, DECISIONS l.104 and commit 6ed06139, and the draft covers all of them. The working tree has no uncommitted edits to STATUS or DECISIONS. Other hits are unrelated. 'fixed point' in 07_SPEC S3, tests.py B3/S3, results/tests*.txt, analysis.py:43/243 and docs/logs/decision_log.md refers to legitimate Gaussian-exactness or failure-class definitions. '첫 패스' in STATUS:69, PAPER_MATERIALS:147, 02/05/10_SPEC and the old handoffs is the T2c pilot-LMMSE notion, with no 'prior 무관' claim; 10_SPEC:849-884 and STATUS:1740-1749 ('학습 prior 가 메우는 genie 격차') do not rely on 'tail is not the prior's problem'. Adjacent but out of scope: STATUS l.1665 says '게이트 통과', while raw meta|stagec_gate reads 'NO GATE RECORD … UNVERIFIED'; audit item G-1.2 covers this. STATUS l.1675-1676 and DECISIONS l.104 item (1) ('0.0281 은 prior 로 줄일 수 없다') are audit item R-10.3, which the draft correctly leaves out. One unverifiable item: the drafter's evidence cites T2_DIFFUSION_CLI_HANDOFF_KO.md:545-555. That file is an upload and is not on disk anywhere under /home/HTJ or /tmp, so those line numbers could not be checked. No proposed text depends on them. Relevant paths: /home/HTJ/t2/conf/STATUS.md, /home/HTJ/t2/conf/DECISIONS.md, /home/HTJ/t2/conf/results/review_next/REVIEW_AUDIT.md (l.653-691), /home/HTJ/t2/conf/code/arms.py (l.34-38, 106-111, 163, 169), /home/HTJ/t2/Demo/exp_0921_analysis.py (l.54-60), /home/HTJ/t2/conf/results/tables_D2_B16e4k.txt (l.88), checker script /tmp/claude-1005/-home-HTJ-t2-Demo/d3790660-21e8-42b4-971e-49b4049a6e64/scratchpad/chk/check.py.
</details>

---

## 1차 · genie/상한 명칭 (R-10.3, M-10.3a)

### genie-1 · R-10.3 — `conf/DECISIONS.md` append after 104 (EOF). Corrects fragment (1) of line 104

- 방식: **DECISIONS append** · ✅ 검증 통과

**원문 (HEAD)**

```text
(1) V1 실패 371 중 72 는 genie 도 실패 → **0.0281 은 prior 로 못 줄인다**.
```

**제안 문구**

```text
`[2026-09-23 __:__ KST] 정정 — [2026-09-23 00:10] 항목 (1) "0.0281 은 prior 로 못 줄인다" 와 STATUS 1675-1676 "채널이 완벽해도 코드가 못 푸는 블록 … 0.0281 은 prior 로 줄일 수 없고, 0.1168 이 채널추정에 귀속된다" (review_next R-10.3) | 원문은 R5-genie 실패 87 을 블록별 하한으로 읽고 V1 실패 371 을 0.0281(prior 로 못 줄임) + 0.1168(채널추정 귀속)로 나눴다. 자료가 지지하는 것은 쌍별 계수뿐이다: raw_B16e4k C2 −3 dB n=2560 반복 16 에서 genie 실패 87, V1 실패 371, 동시 실패 72 (0.0281), V1 실패·genie 성공 299 (0.1168), **V1 성공·genie 실패 15**. GMM(M-ours-bstar)도 같은 모양이다: 동시 실패 77, GMM 성공·genie 실패 10. 대체 문구: "72 블록은 V1 과 known-channel receiver reference 가 모두 실패하고 299 블록은 V1 만, 15 블록은 reference 만 실패한다. 0.0281/0.1168 은 쌍별 계수이지 원인 귀속이 아니다. 72 블록을 prior·interface 개선으로 줄일 수 있는지는 배제되지 않았고 별도 개입 실험이 필요하다." | R5-genie 는 참 H 를 넣은 같은 반복 수신기다(arms.py:117 route_a(..., "gaussian", mode="genie"); Demo/t2_route_a.py:388-389 는 Hc, R 만 참값으로 바꾸고 이후 같은 열별 LMMSE soft-IC 검출 + BCJR 루프를 탄다). joint MAP 도 정보이론적 한계도 아니고 스스로 반복 의존적이다(BLER@1/@2/@8/@16 = 0.225/0.102/0.043/0.034, tables_D2_B16e4k.txt:92). 15 블록이 블록별 하한 해석을 반박한다. 같은 항목의 (3)(4)와 제목·결론의 "배제" 문구는 R-10.1/R-10.2 정정에서 따로 다룬다 | 원문 [00:10] 항목과 STATUS 1675-1676 은 고치지 않았다. 이 줄과 STATUS 1676 뒤 정정 주석을 지우면 원상태`
```

<details><summary>근거</summary>

CPU 재집계 (CUDA_VISIBLE_DEVICES=""): conf/raw_B16e4k/D2_C2_S2_Nr8_T16_Tp4_dft_snr-3_skip{0..2520}_n40.npz 64개, n=2560, '<arm>|blk_err'[:,15]. R5-genie 87 (0.033984), M-ours-dscore-C-V1 371 (0.144922), 동시 72 (0.028125), V1 성공·genie 실패 15, V1 실패·genie 성공 299 (0.116797). M-ours-bstar 623, 동시 77, bstar 성공·genie 실패 10, bstar 실패·genie 성공 546 (STATUS:1670-1673 표와 일치). genie BLER@1/@2/@8/@16 raw 재계산 0.2254/0.1023/0.0426/0.0340 = tables_D2_B16e4k.txt:92. 구현: conf/code/arms.py:117, Demo/t2_route_a.py:388-408. 표현 기준: handoff §10.1/§10.3 ('개선 여지는 별도 개입 실험이 필요', 'known-channel receiver reference').

검증: None blocking. The fragment appears verbatim in HEAD DECISIONS.md:104, and 104 is EOF (wc -l = 104). I re-ran the CPU count on raw_B16e4k C2 -3 dB (64 files, n=2560, blk_err[:,15]). genie 87 (0.033984), V1 371, both fail 72 (0.028125), V1 fails and genie succeeds 299 (0.116797), V1 succeeds and genie fails 15. bstar 623, both fail 77, bstar succeeds and genie fails 10, bstar fails and genie succeeds 546. genie BLER@1/@2/@8/@16 from raw is 0.2254/0.1023/0.0426/0.0340, which matches tables_D2_B16e4k.txt:92. The STATUS:1670-1673 table matches. The code refs hold: arms.py:117, t2_route_a.py:388-389 and 400-408 (L_X is named 'EP-LMMSE' in the module docstring, so 'EP detector' is consistent with the code). The entry has four fields and the replacement wording says 'not ruled out, needs an intervention experiment', so it does not over-correct. Gap, listed under missing: commit 6ed06139's message carries the same attribution ('V1 실패 371 = genie 도 실패 72 + 줄일 수 있는 299') and cannot be amended, so this entry should name it as read-through-this-line.
</details>

### genie-2 · R-10.3, M-10.3a — `conf/DECISIONS.md` append after the R-10.3 entry above (EOF)

- 방식: **DECISIONS append** · ✏️ 검증 수정 반영 (인용 OK · 수치 OK · 문구 X)

**원문 (HEAD)**

```text
08_SPEC_analysis.md:10 `... Upper bound = genie only.` / 05_SPEC_testbed_D2.md:48 '| `exactEP-true` (oracle 상한) | 없음. 상한은 `R5-genie`만 남는다 |' / 00_GOAL.md:111 '| R5 genie / R6 exactEP *(D1만)* | 상한 — 남은 headroom |' / STATUS.md:590 '**상한 대비**: `V0 → R6-exactEP` ...' / STATUS.md:692,795 & PAPER_MATERIALS.md:639 '| R5-genie (상한) | 0.034 | ...' / PAPER_MATERIALS.md:585 '**상한 대비 (C5):** ...'
```

**제안 문구**

```text
`[2026-09-23 __:__ KST] 정정 — R5-genie·R6-exactEP 를 "상한/upper bound/lower bound/headroom" 으로 부른 명칭 (review_next R-10.3 표 헤더, M-10.3a) | 앞으로 Claude 가 쓰는 기록(STATUS·PAPER_MATERIALS·DECISIONS 정정 주석)에서 R5-genie 는 "known-channel receiver reference (동일 EP detector + BCJR, 참 H)", R6-exactEP(D1 전용)는 "exact-prior EP reference" 로 부른다. 이 arm 까지의 차이는 "reference 까지의 격차" 로 기술하고 bound·상한·headroom 이라 쓰지 않는다. spec 문구·원고 명칭·생성기 출력 문자열은 사용자 승인 사항이라 여기서 정하지 않는다. arm id(R5-genie, R6-exactEP)는 raw 키·코드 식별자라 바꾸지 않는다. 이미 생성된 표·그림은 재생성하지 않는다 | 둘 다 같은 route_a 반복 루프다: R5 = arms.py:117 mode="genie" (t2_route_a.py:388-389, 참 H), R6 = arms.py:119 route_a(*a, true_prior.view("eta"), code, Xp, "gmm_site") (참 prior GMM site). 어느 것도 수학적으로 증명된 bound 가 아니고 블록별 하한도 아니다: D2 C2 −3 dB 에서 V1 성공·R5 실패 15 블록(raw_B16e4k·raw_C), D1 C5 에서 V0 성공·R6 실패 91 블록(−3/+0/+3 dB 합, raw_C; tables_D1_C.txt:1139 88:91, a:b 규약 :754). R6 도 반복 의존적이다(C5 −3 dB BLER@1/@2/@8/@16 = 0.961/0.821/0.551/0.505, tables_D1_C.txt:554). 적용 위치: STATUS 590·692·795·1675-1676, PAPER_MATERIALS 585·639 (정정 주석), 08_SPEC_analysis:10·38, 05_SPEC_testbed_D2:48, 00_GOAL:111 (사용자 승인 필요 spec 주석), 생성기 common.py:228·figures_stagec.py:531·642·787·840 (spec 승인 후, 재생성 없음). 같은 표기지만 audit 미기재 — 이 줄로 읽는다: STATUS:462, PAPER_MATERIALS:861·928, NUMBERS_PACKAGE_2026-09-22:479·632, results/jac_spectrum.txt:45 ("exact-EP bound"), F11 캡션:48, code/analysis.py:91 docstring ("bound arm"), 그림 범례 "genie CSI (lower bound)" (생성기 figures.py:35·figures_stagec.py:531·642·figure_f14.py:46·figures_stagec2.py:69 — R5 를 그린 PNG/PDF 범례에 이미 찍혀 있음). spec 이라 사용자 승인 필요: 06_SPEC_runner.md:18 ("oracle 상한"), 10_SPEC_stageC.md:824 ("상한 대비 위치") | 이 줄을 지우면 옛 명칭으로 돌아간다. 원문 행은 어디서도 고치지 않았다`
```

<details><summary>검증 agent 지적 / 초안 원안</summary>

지적: The quotes are abbreviated but faithful: 08_SPEC:10, 05_SPEC:48, 00_GOAL:111, STATUS:590/692/795 and PAPER_MATERIALS:585/639 all match HEAD. The numbers re-derive. raw_B16e4k and raw_C both give V1 succeeds and genie fails 15, and genie is blockwise identical in raw_B16e4k, raw_C and raw_B1e4. For raw_C D1_C5 V0 vs R6, only-V0-fails : only-R6-fails is 43:47, 32:35 and 13:9, pooled 88:91, which matches tables_D1_C.txt:1139 (the C5 block of TABLE B, which starts at 1028). The a:b convention is at :754. R6 C5 -3 dB is 1294/2560 failures, and tables_D1_C.txt:554 reads 0.961/0.821/0.551/0.505. Two problems. (a) Scope: '앞으로 기록·원고에서 … 로 부른다' decides naming for the manuscript, which the user writes, and it pre-empts the spec notes that the same entry marks 사용자 승인 필요. Limit it to the records Claude writes. (b) The list of locations outside the audit is incomplete. The same bound naming also appears at NUMBERS_PACKAGE_2026-09-22:632 ('gap to the genie bound'), results/jac_spectrum.txt:45 ('the exact-EP bound') and code/analysis.py:91 (docstring 'bound arm (R6-exactEP / R5-genie)'). It appears in the figure legend 'genie CSI (lower bound)' from figures.py:35, figures_stagec.py:531 and 642, figure_f14.py:46 and figures_stagec2.py:69; the F11 PNG legend visibly reads 'R5 genie CSI (lower bound)'. It also appears in two spec files: 06_SPEC_runner.md:18 ('oracle 상한' for R6) and 10_SPEC_stageC.md:824 ('상한 대비 위치').

초안 원안:

```text
`[2026-09-23 __:__ KST] 정정 — R5-genie·R6-exactEP 를 "상한/upper bound/headroom" 으로 부른 명칭 (review_next R-10.3 표 헤더, M-10.3a) | 앞으로 기록·원고에서 R5-genie 는 "known-channel receiver reference (동일 EP detector + BCJR, 참 H)", R6-exactEP(D1 전용)는 "exact-prior EP reference" 로 부른다. 이 arm 까지의 차이는 "reference 까지의 격차" 로 기술하고 bound·상한·headroom 이라 쓰지 않는다. arm id(R5-genie, R6-exactEP)는 raw 키·코드 식별자라 바꾸지 않는다. 이미 생성된 표·그림은 재생성하지 않는다 | 둘 다 같은 route_a 반복 루프다: R5 = arms.py:117 mode="genie" (t2_route_a.py:388-389, 참 H), R6 = arms.py:119 route_a(*a, true_prior.view("eta"), code, Xp, "gmm_site") (참 prior GMM site). 어느 것도 수학적으로 증명된 bound 가 아니고 블록별 하한도 아니다: D2 C2 −3 dB 에서 V1 성공·R5 실패 15 블록(raw_B16e4k·raw_C), D1 C5 에서 V0 성공·R6 실패 91 블록(−3/+0/+3 dB 합, raw_C; tables_D1_C.txt:1139 88:91, a:b 규약 :754). R6 도 반복 의존적이다(C5 −3 dB BLER@1/@2/@8/@16 = 0.961/0.821/0.551/0.505, tables_D1_C.txt:554). 적용 위치: STATUS 590·692·795·1675-1676, PAPER_MATERIALS 585·639 (정정 주석), 08_SPEC_analysis:10·38, 05_SPEC_testbed_D2:48, 00_GOAL:111 (사용자 승인 필요 spec 주석), 생성기 common.py:228·figures_stagec.py:787·840 (spec 승인 후, 재생성 없음). 같은 표기지만 audit 미기재: STATUS:462, PAPER_MATERIALS:861·928, NUMBERS_PACKAGE_2026-09-22:479, F11 캡션:48 — 이 줄로 읽는다 | 이 줄을 지우면 옛 명칭으로 돌아간다. 원문 행은 어디서도 고치지 않았다`
```
</details>

<details><summary>근거</summary>

R5: conf/code/arms.py:117 'arms["R5-genie"] = route_a(*a, Cs, code, Xp, "gaussian", mode="genie")'; Demo/t2_route_a.py:388-389 'if self.mode == "genie": Hc, R = H, self.sigma2 * self.I_Nr' → 400-408 같은 Kg/xhat/pL 검출. R6: arms.py:118-119. 재집계: raw_B16e4k·raw_C D2 C2 −3 dB 모두 genie 87 / V1 371 / 동시 72 / V1 성공·genie 실패 15 (genie 두 raw 에서 블록 단위 동일). raw_C D1_C5 −3/+0/+3 dB (각 n=2560, 64파일) V0→R6-exactEP only-V0-fails : only-R6-fails = 43:47, 32:35, 13:9, 합 88:91 = tables_D1_C.txt:1139; 규약 tables_D1_C.txt:754 "'a:b' = only-first-fails : only-second-fails". R6 C5 −3 dB 실패 1294/2560 = 0.505 = tables_D1_C.txt:554. 명칭 출처: 과업 지정 및 handoff §10.3.

검증: (위 참조)
</details>

### genie-3 · R-10.3 — `conf/STATUS.md` 1675-1676 (insert note after 1676)

- 방식: **STATUS inline note** · ✅ 검증 통과

**원문 (HEAD)**

```text
genie 자체 실패 87 (0.0340) 은 **채널이 완벽해도 코드가 못 푸는 블록**이다. 따라서 V1 의 0.1449 중
**0.0281 은 prior 로 줄일 수 없고, 0.1168 이 채널추정에 귀속된다.**
```

**제안 문구**

```text
> **정정 (2026-09-23, review_next R-10.3)**: 위 두 문장은 genie 실패를 블록별 하한으로 읽었다. R5-genie 는 같은 반복 수신기에 참 H 를 넣은 known-channel receiver reference (동일 EP detector + BCJR, 참 H) 이며(`code/arms.py:117`, `Demo/t2_route_a.py:388-389`) joint MAP·정보이론적 한계가 아니고 스스로 반복 의존적이다(BLER@1/@2/@8/@16 = 0.225/0.102/0.043/0.034, `tables_D2_B16e4k.txt:92`). 같은 raw 에서 **V1 성공·genie 실패 15 블록**이 있다(genie 87 = V1 과 동시 72 + genie 단독 15; GMM 은 동시 77 + genie 단독 10). 대체 문구: "72 블록(0.0281)은 V1 과 reference 가 모두 실패, 299 블록(0.1168)은 V1 만 실패, 15 블록은 reference 만 실패한다. 쌍별 계수이지 원인 귀속이 아니다. 72 블록을 prior·interface 개선으로 줄일 수 있는지는 배제되지 않았고 별도 개입 실험이 필요하다." 출처: `raw_B16e4k` C2 −3 dB `blk_err[:,15]`, n=2560. DECISIONS [2026-09-23 __:__] 정정 참조.
```

<details><summary>근거</summary>

raw_B16e4k C2 −3 dB 64파일 n=2560 반복 16: genie 87, V1 371, 동시 72, V1 성공·genie 실패 15, V1 실패·genie 성공 299 (0.116797); bstar 동시 77, bstar 성공·genie 실패 10. genie BLER@1/@2/@8/@16 raw 0.2254/0.1023/0.0426/0.0340 = tables_D2_B16e4k.txt:92. 원문 위치 HEAD cd241b7e STATUS.md:1675-1676 확인.

검증: None. The quote is verbatim at HEAD STATUS.md:1675-1676. All numbers re-derive from raw_B16e4k: 87 = 72 + 15, 299 = 0.1168, GMM 77 + 10, genie BLER 0.225/0.102/0.043/0.034 = tables_D2_B16e4k.txt:92. The note follows the '> **정정 (2026-09-23, review_next <id>)**' convention and leaves the original line unchanged. The replacement wording neither keeps the floor claim nor asserts that prior improvement is possible.
</details>

### genie-4 · R-10.3 — `conf/STATUS.md` 692 and 795 (each is the last row of its table; insert note after the row, with one blank line)

- 방식: **STATUS inline note** · ✅ 검증 통과

**원문 (HEAD)**

```text
692: | R5-genie (상한) | 0.034 | 참 채널 |
795: | R5-genie (상한) | 0.034 | [0.028, 0.042] |
```

**제안 문구**

```text
[692 뒤] > **정정 (2026-09-23, review_next R-10.3)**: 위 표의 `R5-genie (상한)` 은 bound 가 아니다. known-channel receiver reference (동일 EP detector + BCJR, 참 H) 로 읽는다 — 같은 route_a 반복 루프에 참 H 를 넣은 것이고(`code/arms.py:117`, `Demo/t2_route_a.py:388-389`), 같은 C2 −3 dB 에서 V1 성공·genie 실패 15 블록이 있다(`raw_C` `blk_err[:,15]`, n=2560). 0.034 는 불변. DECISIONS [2026-09-23 __:__] 명칭 정정 참조.

[795 뒤] > **정정 (2026-09-23, review_next R-10.3)**: 위 표의 `R5-genie (상한)` 은 bound 가 아니다. known-channel receiver reference (동일 EP detector + BCJR, 참 H) 로 읽는다 — 같은 route_a 반복 루프에 참 H 를 넣은 것이고(`code/arms.py:117`), 이 표의 run 에서도 V1(N=1e4) 성공·genie 실패 9 블록이 있다(`raw_B1e4` C2 −3 dB `blk_err[:,15]`, n=2560). 0.034 [0.028, 0.042] 는 불변. DECISIONS [2026-09-23 __:__] 명칭 정정 참조.
```

<details><summary>근거</summary>

692 표는 §'2차 결과'(STATUS:683, 출처 tables_D2_C.txt → raw_C): raw_C D2 C2 −3 dB genie 87, V1 371, 동시 72, V1 성공·genie 실패 15. 795 표는 §'동일예산 BLER'(STATUS:779-781, 출처 results/tables_D2_B1e4.txt → raw_B1e4): genie 87 (raw_B16e4k 와 블록 단위 동일), V1 372, 동시 78, V1 성공·genie 실패 9. 모두 CPU 재집계.

검증: None. 692 is the last row of the §'2차 결과' table (683; that section's run is tables_D2_C.txt → raw_C), and 693 is blank. 795 is the last row of the §'동일예산 BLER' table, whose source is results/tables_D2_B1e4.txt per STATUS:781. Recomputed on raw_C: V1 371, both fail 72, V1 succeeds and genie fails 15. Recomputed on raw_B1e4: V1 372, both fail 78, V1 succeeds and genie fails 9. genie is 87 in both runs and blockwise identical to raw_B16e4k. The blank line before each blockquote is needed so the note does not merge into the table, and the draft has it.
</details>

### genie-5 · R-10.3 — `conf/PAPER_MATERIALS.md` 639 (last row of §15.1 TABLE A; insert note after it, with one blank line)

- 방식: **other** · ✅ 검증 통과

**원문 (HEAD)**

```text
| R5-genie (상한) | 0.034 | [0.028, 0.042] |
```

**제안 문구**

```text
> **정정 (2026-09-23, review_next R-10.3)**: `R5-genie (상한)` → `R5-genie` (known-channel receiver reference: 동일 EP detector + BCJR, 참 H). 같은 route_a 반복 루프에 참 H 를 넣은 것이며(`code/arms.py:117`, `Demo/t2_route_a.py:388-389`) bound 가 아니다: 같은 C2 −3 dB 에서 V1 성공·genie 실패 15 블록(`raw_C` `blk_err[:,15]`, n=2560). 0.034 [0.028, 0.042] 불변. DECISIONS [2026-09-23 __:__] 명칭 정정 참조.
```

<details><summary>근거</summary>

PAPER_MATERIALS §15 출처 results/tables_D2_C.txt (PAPER_MATERIALS:614). raw_C D2 C2 −3 dB 재집계: genie 87, V1 371, 동시 72, V1 성공·genie 실패 15. 방식: PAPER_MATERIALS 는 Claude 관리 색인이라 STATUS 인라인 정정 관례를 준용(원문 행 유지).

검증: None. The quote is verbatim at HEAD PAPER_MATERIALS.md:639, the last row of §15.1 (640 is blank). The §15 source is tables_D2_C.txt (:614), which goes to raw_C, where V1 succeeds and genie fails in 15 blocks. PAPER_MATERIALS already uses the '> **정정 (...)**:' inline style (e.g. :54, :987, :1096), so this note matches the convention.
</details>

### genie-6 · R-10.3, M-10.3a — `conf/08_SPEC_analysis.md` 10 (note after line 10); 38 (last row of §2 table; note after it)

- 방식: **spec note (사용자 승인 필요)** · ✅ 검증 통과

**원문 (HEAD)**

```text
10: - **D2 표** 헤더: `CLAIM TESTBED — sparse specular; conditional Gaussianity broken (see T2d). Upper bound = genie only.`
38: | M-ours-* → R6-exactEP *(D1만)* / → R5-genie *(D2)* | 남은 headroom |
```

**제안 문구**

```text
[10 뒤] > **정정 제안 (2026-09-23, review_next R-10.3) — 사용자 승인 필요**: 위 D2 헤더의 `Upper bound = genie only.` 는 R5-genie 를 bound 로 명명한다. R5-genie 는 같은 route_a 반복 수신기에 참 H 를 넣은 것이다(`code/arms.py:117`, `Demo/t2_route_a.py:388-389`; BLER@1/@2/@8/@16 = 0.225/0.102/0.043/0.034, `results/tables_D2_B16e4k.txt:92`). C2 −3 dB 에서 V1 성공·genie 실패 15 블록(`raw_B16e4k`)이 있어 블록별 하한도 아니다. 제안 헤더: `CLAIM TESTBED — sparse specular; conditional Gaussianity broken (see T2d). Reference = known-channel receiver (R5-genie: same EP detector + BCJR, true H); not a bound.` 승인되면 `code/common.py:228` 만 바꾸고 이미 생성된 `tables_D2_*.txt` 는 재생성하지 않는다 — 옛 헤더는 이 주석으로 읽는다.

[38 뒤] > **정정 제안 (2026-09-23, review_next M-10.3a) — 사용자 승인 필요**: 위 행의 "남은 headroom" 을 "reference 까지의 격차 (R6 = exact-prior EP reference, R5 = known-channel receiver reference; 기술적 서술이며 bound 아님)" 로 읽기를 제안한다. 근거는 10행 주석과 같다. R6 도 같은 route_a 루프(`code/arms.py:119`, 참 prior GMM site)이고 D1 C5 에서 V0 성공·R6 실패 91 블록이 있다(−3/+0/+3 dB 합, `results/tables_D1_C.txt:1139` 88:91).
```

<details><summary>근거</summary>

08_SPEC_analysis.md:10 헤더가 conf/code/common.py:228 D2_WARNING 으로 그대로 출력됨 → tables_D2_B16e4k.txt:50 (및 :447, :489 내장 표). 38행은 audit 위치 목록 밖이지만 같은 파일·같은 명명(00_GOAL:111 '남은 headroom' 과 동일 표현)이라 포함. 수치: raw_B16e4k genie/V1 재집계(15), raw_C D1_C5 V0→R6 88:91 재집계.

검증: Quotes are verbatim at HEAD 08_SPEC_analysis.md:10 and :38 (38 is the last row of the §2 table, 39 is blank). All numbers re-derive: 15 from raw_B16e4k; 88:91 at tables_D1_C.txt:1139; genie at :92. Both notes are marked 사용자 승인 필요. Optional tweak, not a failure: the proposed header 'Reference = known-channel receiver (R5-genie …)' can read as saying R5 is the only reference, but R0-R4 are also reference receivers. 'Known-channel reference = R5-genie (same EP detector + BCJR, true H); not a bound.' avoids that reading. If adopted, use the same string in the common.py entry.
</details>

### genie-7 · R-10.3 — `conf/code/common.py` 228 (generator of every D2 table header, e.g. conf/results/tables_D2_B16e4k.txt:50)

- 방식: **caption/generator note** · ✅ 검증 통과

**원문 (HEAD)**

```text
"# CLAIM TESTBED -- sparse specular; conditional Gaussianity broken (see T2d). Upper bound = genie only.\n"
```

**제안 문구**

```text
08_SPEC:10 정정 제안이 승인된 뒤에만 적용 (출력 문자열 변경, 기존 표 재생성 없음):
old:     "# CLAIM TESTBED -- sparse specular; conditional Gaussianity broken (see T2d). Upper bound = genie only.\n"
new:     "# CLAIM TESTBED -- sparse specular; conditional Gaussianity broken (see T2d). Reference = known-channel receiver (R5-genie: same EP detector + BCJR, true H); not a bound.\n"
미승인 상태에서는 아무것도 바꾸지 않는다. tables_D2_B16e4k.txt:50 등 기존 표는 DECISIONS [2026-09-23 __:__] 명칭 정정으로 읽는다.
```

<details><summary>근거</summary>

git grep HEAD: 'Upper bound = genie' 는 conf/code/common.py:228 한 곳에서만 생성. audit R-10.3 수정 방향: 'Change it only via a dated spec note so the archived tables stay as they are; do not regenerate the old tables.' 헤더 문구가 08_SPEC:10(사용자 소유)에서 처방되므로 코드 변경은 승인 종속.

검증: None. The old line is verbatim at HEAD common.py:228, inside D2_WARNING. git grep confirms it is the only generator of 'Upper bound = genie only.'; every other hit is archived output (tables, logs, gate_D2, gmm_fit_D2, tp_trend_D2). Making the change depend on approval is correct, because it changes output text and the wording is prescribed by the user-owned 08_SPEC:10. The same optional header tweak as in the 08_SPEC entry applies.
</details>

### genie-8 · M-10.3a — `conf/05_SPEC_testbed_D2.md` 48 (mid-table; insert note after line 50, the table's last row)

- 방식: **spec note (사용자 승인 필요)** · ✏️ 검증 수정 반영 (인용 OK · 수치 OK · 문구 X)

**원문 (HEAD)**

```text
| `exactEP-true` (oracle 상한) | 없음. 상한은 `R5-genie`만 남는다 |
```

**제안 문구**

```text
> **정정 제안 (2026-09-23, review_next M-10.3a) — 사용자 승인 필요**: 48행의 "`exactEP-true` (oracle 상한)" 과 "상한은 `R5-genie`만 남는다" 는 두 참조 수신기를 bound 로 명명한다. `exactEP-true`(= D1 의 `R6-exactEP`)는 참 prior GMM site 를 쓰는 같은 route_a EP/터보 루프이고(`code/arms.py:119`) D1 C5 에서 V0 성공·R6 실패 91 블록이 있다(−3/+0/+3 dB 합, `results/tables_D1_C.txt:1139` 88:91). `R5-genie` 는 같은 루프에 참 H 를 넣은 것이고(`code/arms.py:117`) D2 C2 −3 dB 에서 V1 성공·genie 실패 15 블록이 있다(`raw_B16e4k`). 제안 문구: "| `exactEP-true` (exact-prior EP reference) | 없음. D2 에서 참값(참 prior·참 H)을 쓰는 참조 수신기는 `R5-genie` = known-channel receiver reference (동일 EP detector + BCJR, 참 H) 하나만 남는다. 어느 것도 bound 가 아니다 |"
```

<details><summary>검증 agent 지적 / 초안 원안</summary>

지적: The quote is verbatim at HEAD :48, and :50 is the table's last row. The numbers re-derive: raw_C D1_C5 43/32/13 : 47/35/9 = 88:91, and 15 from raw_B16e4k. The proposed wording adds a new false claim: 'D2 에 남는 참조 수신기는 `R5-genie` … 뿐이다'. D2 keeps R0-pilot, R1-turbo, R2-ours-G, R3-bigamp, R4-scvamp and R4-llr as reference receivers (arms.py:109-116). The original row means that R5 is the only reference with oracle information left on D2, so the replacement has to say that.

초안 원안:

```text
> **정정 제안 (2026-09-23, review_next M-10.3a) — 사용자 승인 필요**: 48행의 "`exactEP-true` (oracle 상한)" 과 "상한은 `R5-genie`만 남는다" 는 두 참조 수신기를 bound 로 명명한다. `exactEP-true`(= D1 의 `R6-exactEP`)는 참 prior GMM site 를 쓰는 같은 route_a EP/터보 루프이고(`code/arms.py:119`) D1 C5 에서 V0 성공·R6 실패 91 블록이 있다(−3/+0/+3 dB 합, `results/tables_D1_C.txt:1139` 88:91). `R5-genie` 는 같은 루프에 참 H 를 넣은 것이고(`code/arms.py:117`) D2 C2 −3 dB 에서 V1 성공·genie 실패 15 블록이 있다(`raw_B16e4k`). 제안 문구: "| `exactEP-true` (exact-prior EP reference) | 없음. D2 에 남는 참조 수신기는 `R5-genie` = known-channel receiver reference (동일 EP detector + BCJR, 참 H) 뿐이다. 어느 것도 bound 가 아니다 |"
```
</details>

<details><summary>근거</summary>

arms.py:118-119 'if testbed == "D1" and true_prior is not None: arms["R6-exactEP"] = route_a(*a, true_prior.view("eta"), code, Xp, "gmm_site")'. raw_C D1_C5 −3/+0/+3 dB n=2560 each: only-V0-fails 43/32/13, only-R6-fails 47/35/9 (합 88:91). raw_B16e4k D2 C2 −3 dB V1 성공·genie 실패 15.

검증: (위 참조)
</details>

### genie-9 · M-10.3a — `conf/00_GOAL.md` 111 (last line of file, last row of the arm table; note after it)

- 방식: **spec note (사용자 승인 필요)** · ✅ 검증 통과

**원문 (HEAD)**

```text
| R5 genie / R6 exactEP *(D1만)* | 상한 — 남은 headroom |
```

**제안 문구**

```text
> **정정 제안 (2026-09-23, review_next M-10.3a) — 사용자 승인 필요**: 위 행의 "상한 — 남은 headroom" 은 두 참조 수신기를 bound 로 명명한다. 둘 다 같은 route_a 반복 루프다 — R5 는 참 H(`code/arms.py:117`), R6 은 참 prior GMM site(`code/arms.py:119`). 블록별 하한도 아니다: D2 C2 −3 dB 에서 V1 성공·R5 실패 15 (`raw_B16e4k`), D1 C5 에서 V0 성공·R6 실패 91 (`raw_C`, −3/+0/+3 dB 합). 제안 문구: "| R5 genie / R6 exactEP *(D1만)* | 참조 수신기 (bound 아님) — R5 = known-channel receiver reference (동일 EP detector + BCJR, 참 H), R6 = exact-prior EP reference. 이 arm 까지의 격차는 기술적 서술 |"
```

<details><summary>근거</summary>

00_GOAL.md HEAD 111행 = 파일 마지막 행 (wc -l 111). 수치: raw_B16e4k (15), raw_C D1_C5 (91) CPU 재집계. 구현 arms.py:117, :119.

검증: None. The quote is verbatim at HEAD 00_GOAL.md:111, the last line (wc -l = 111). Numbers: 15 from raw_B16e4k and 91 from raw_C D1_C5 (the pooled only-R6-fails count), with code refs arms.py:117 and :119. The note is marked 사용자 승인 필요. Related but outside the audit: :110 calls M-ours-score '학습 score의 상한' (see missing).
</details>

### genie-10 · M-10.3a — `conf/figs/F11_bler_D2_confirmatory.txt (generator conf/code/figures_stagec.py)` F11 txt 162-163 and 47-48; generator figures_stagec.py 839-840 and 787

- 방식: **caption/generator note** · ✏️ 검증 수정 반영 (인용 OK · 수치 OK · 문구 X)

**원문 (HEAD)**

```text
F11:162-163 "THE STANDING CAVEAT ON THIS TESTBED, from the file's own header.  D2 is the CLAIM testbed: sparse\nspecular, conditional Gaussianity broken, and the upper bound is the genie only."
F11:47-48 "then outside the anchor window BLER in [0.005, 0.9].  No arm in this figure is therefore claimed to\n    differ from the genie bound on C2, however far apart the two curves look."
```

**제안 문구**

```text
F11 그림(PNG/PDF)과 캡션 txt 는 재생성·수기 수정하지 않는다(생성기 출력과 어긋나지 않게). 교정은 DECISIONS [2026-09-23 __:__] 명칭 정정으로 기록된다. 캡션 163행의 "from the file's own header" 는 표 파일 헤더(common.py:228 출력, 08_SPEC:10 처방)를 인용하므로, 08_SPEC 정정 제안이 승인된 뒤에만 생성기를 바꾼다(향후 재생성분에만 적용):
figures_stagec.py:840 old: specular, conditional Gaussianity broken, and the upper bound is the genie only.
new: specular, conditional Gaussianity broken, and R5-genie (true H) is the only oracle reference left: a
known-channel receiver reference (same EP detector + BCJR), not a bound.
figures_stagec.py:787 old:     differ from the genie bound on C2, however far apart the two curves look.
new:     differ from the known-channel receiver reference on C2, however far apart the two curves look.
같은 생성기의 범례 문자열도 같은 조건으로 (F10·F11 PNG/PDF 범례에 이미 "genie CSI (lower bound)" 로 찍혀 있음, 재생성 없음):
figures_stagec.py:531 old:     ("R5-genie", "R5  genie CSI (lower bound)", "k", "*", "-."),
new:     ("R5-genie", "R5  genie CSI (known-H reference)", "k", "*", "-."),
figures_stagec.py:642 old:     ("R5-genie",            "R5   genie CSI (lower bound)",                     "k",          "*",  "-."),
new:     ("R5-genie",            "R5   genie CSI (known-H reference)",               "k",          "*",  "-."),
```

<details><summary>검증 agent 지적 / 초안 원안</summary>

지적: The quotes are verbatim: F11 txt:47-48 and 162-163, generator figures_stagec.py:786-787 and 839-840. Three problems. (1) The proposed new line 'the only reference receiver is R5-genie' is false, because the same figure plots R1, R2 and the other reference arms; it needs the oracle qualifier. (2) The note misses the F11 legend, which comes from the same generator: figures_stagec.py:642 'R5   genie CSI (lower bound)'. The F11 PNG shows it ('R5 genie CSI (lower bound)'). The same file's F10 legend has it too, at :531. (3) Precision: the caption's 'from the file's own header' quotes the tables file header, which common.py:228 prints and 08_SPEC:10 prescribes; it does not quote 08_SPEC directly.

초안 원안:

```text
F11 그림과 캡션 txt 는 재생성·수기 수정하지 않는다(생성기 출력과 어긋나지 않게). 교정은 DECISIONS [2026-09-23 __:__] 명칭 정정으로 기록된다. 캡션 163행은 "from the file's own header" 즉 08_SPEC:10 헤더를 인용하므로, 08_SPEC 정정 제안이 승인된 뒤에만 생성기를 바꾼다(향후 재생성분에만 적용):
figures_stagec.py:840 old: specular, conditional Gaussianity broken, and the upper bound is the genie only.
new: specular, conditional Gaussianity broken, and the only reference receiver is R5-genie, a known-channel
receiver reference (same EP detector + BCJR, true H), not a bound.
figures_stagec.py:787 old:     differ from the genie bound on C2, however far apart the two curves look.
new:     differ from the known-channel receiver reference on C2, however far apart the two curves look.
```
</details>

<details><summary>근거</summary>

git grep HEAD: 'upper bound is the genie only' → conf/code/figures_stagec.py:840 → F11 txt:163; 'genie bound' → figures_stagec.py:787 → F11 txt:48. audit M-10.3a: 'Leave archived tables and figures unregenerated.' F11:48 은 audit 위치 목록 밖이나 같은 생성기·같은 명명.

검증: (위 참조)
</details>

### genie-11 · M-10.3a — `conf/STATUS.md` 590-591 (insert note after 591, end of paragraph)

- 방식: **STATUS inline note** · ✅ 검증 통과

**원문 (HEAD)**

```text
**상한 대비**: `V0 → R6-exactEP` C5 에서 **88:91 p=0.88, POWERED** — 검정력을 갖춘 상태에서 동률이다.
(n=640 의 7:8 은 검정력 부족이라는 감사 지적이 옳았고, n=2560 에서 비로소 의미를 갖는다.)
```

**제안 문구**

```text
> **정정 (2026-09-23, review_next M-10.3a)**: "상한 대비" 의 `R6-exactEP` 는 bound 가 아니라 exact-prior EP reference 다 — 참 prior GMM site 를 쓰는 같은 route_a EP/터보 루프이고(`code/arms.py:119`) 스스로 반복 의존적이다(C5 −3 dB BLER@1/@2/@8/@16 = 0.961/0.821/0.551/0.505, `tables_D1_C.txt:554`). 88:91 의 91 이 V0 성공·R6 실패 블록이다(a:b = only-first-fails : only-second-fails, `tables_D1_C.txt:754`). 대체 문구: "**exact-prior EP reference 대비**: `V0 → R6-exactEP` C5 에서 **88:91 p=0.88, POWERED** — 검정력을 갖춘 상태에서 동률이다." 수치·판정 불변. DECISIONS [2026-09-23 __:__] 명칭 정정 참조.
```

<details><summary>근거</summary>

tables_D1_C.txt:1139 'sign test @16: -3 dB 43:47 p=0.75  +0 dB 32:35 p=0.81  +3 dB 13:9 p=0.52   pooled 88:91 p=0.88' — raw_C D1_C5 재집계로 동일(43:47, 32:35, 13:9). 규약 tables_D1_C.txt:754. R6 C5 −3 dB 행 tables_D1_C.txt:554 (C5 절 523행 이후), raw 실패 1294/2560 = 0.505.

검증: None. The quote is verbatim at HEAD STATUS.md:590-591, and 592 is blank. Numbers: tables_D1_C.txt:1139 gives 43:47 / 32:35 / 13:9, pooled 88:91 p=0.88, reproduced from raw_C. The a:b convention is at :754. R6 C5 -3 dB at :554 (inside the C5 block, which starts at 523) reads 0.961/0.821/0.551/0.505, and raw gives 1294/2560 = 0.505. The replacement keeps the numbers and the verdict and changes only the label.
</details>

### genie-12 · M-10.3a — `conf/PAPER_MATERIALS.md` 585-586 (insert note after 586)

- 방식: **other** · ✅ 검증 통과

**원문 (HEAD)**

```text
**상한 대비 (C5):** `M-ours-dscore-C-V0 → R6-exactEP` 88:91 **p=0.88, POWERED**,
SNR@0.1 gap -0.00 dB [90% paired bootstrap -0.08, +0.07]. 검정력을 갖춘 상태의 동률이다.
```

**제안 문구**

```text
> **정정 (2026-09-23, review_next M-10.3a)**: "상한 대비 (C5)" → "exact-prior EP reference 대비 (C5)". `R6-exactEP` 는 참 prior GMM site 를 쓰는 같은 route_a EP/터보 루프(`code/arms.py:119`)이며 bound 가 아니다: 88:91 의 91 = V0 성공·R6 실패 블록(C5 −3/+0/+3 dB 합, `results/tables_D1_C.txt:1139`, 규약 :754). 수치·판정 불변. DECISIONS [2026-09-23 __:__] 명칭 정정 참조.
```

<details><summary>근거</summary>

tables_D1_C.txt:1139, :1142 (SNR@0.1 gap -0.00 dB [-0.08, +0.07]); raw_C D1_C5 재집계 88:91. 방식: PAPER_MATERIALS 에 STATUS 인라인 정정 관례 준용.

검증: None. The quote is verbatim at HEAD :585-586. 88:91 matches tables_D1_C.txt:1139, and SNR@0.1 -0.00 dB [-0.08, +0.07] matches :1142. The inline 정정 style has precedent in PAPER_MATERIALS.
</details>

### genie-13 · R-10.3, M-10.3a (audit 미기재 동일 표기) — `conf/STATUS.md, conf/PAPER_MATERIALS.md, conf/results/NUMBERS_PACKAGE_2026-09-22.md` STATUS 462; PAPER_MATERIALS 861, 928; NUMBERS_PACKAGE_2026-09-22 479

- 방식: **other** · ✅ 검증 통과

**원문 (HEAD)**

```text
STATUS:462 "**`V0 → R6-exactEP` 7:8 p=1.0** — 정확 EP 상한과 통계적으로 구별되지 않는다."
PAPER_MATERIALS:861 "- **D2 C2 에서 \"genie 상한과 유의하게 다르다 / 가깝다\" 는 검정 진술** — `R5-genie` 를 앵커로 한"
PAPER_MATERIALS:928 "사전 등록 power guard 가 판정을 내리지 않는다. → **C2 에서 어떤 arm 도 genie 상한과 다르다고 주장할 수"
NUMBERS_PACKAGE:479 "**The only POWERED \"ties the exact-EP bound\" statement on D1 is C5: V0 → R6-exactEP 88:91 p=0.88.**"
```

**제안 문구**

```text
별도 주석 없이 DECISIONS [2026-09-23 __:__] 명칭 정정 항목의 "audit 미기재" 목록으로만 덮는다(그 항목에 이미 나열). 사용자가 원하면 각 행 뒤에 한 줄: "> **정정 (2026-09-23, review_next M-10.3a)**: '상한/bound' → R5-genie = known-channel receiver reference (동일 EP detector + BCJR, 참 H), R6-exactEP = exact-prior EP reference. bound 아님. 수치·판정 불변." STATUS:462 는 이미 n=640 철회분(NUMBERS_PACKAGE_2026-09-22:564 R10)이다.
```

<details><summary>근거</summary>

grep -nE '상한|bound' HEAD cd241b7e 결과 중 audit R-10.3/M-10.3a 위치 목록에 없는 R5/R6 명명. NUMBERS_PACKAGE_2026-09-22:564 'Retracted: C2 "V0 → R6-exactEP 7:8 p=1.0"'. PAPER_MATERIALS:861·928 은 genie 쌍 UNDECIDED 를 올바르게 적되 'genie 상한' 표기만 해당. 00_GOAL:110·DECISIONS:26 의 'oracle 상한'(M-ours-score)은 다른 arm 이라 범위 밖.

검증: All four quotes are verbatim at HEAD (STATUS:462, PAPER_MATERIALS:861 and :928, NUMBERS_PACKAGE:479). NUMBERS_PACKAGE:564 is the R10 retraction of C2 'V0 → R6-exactEP 7:8 p=1.0', as the draft claims. Covering these through the DECISIONS list is consistent with the conventions. The list is incomplete, though: NUMBERS_PACKAGE:632 ('gap to the genie bound', inside retraction item 5), results/jac_spectrum.txt:45 and the other locations under missing. The corrected DECISIONS naming entry now names them.
</details>

### 1차 검증이 찾은 누락 위치 (→ 2차에서 초안 작성)

<details><summary>원문</summary>

Other places with the same wrong wording at HEAD cd241b7e that the draft does not cover. I found them with git grep and checked each against the file.

Floor/attribution wording (R-10.3):
(1) Commit 6ed06139 message: 'V1 실패 371 = genie 도 실패 72 + 줄일 수 있는 299'. It implies the 72 cannot be reduced, the same claim as STATUS:1676. Commits cannot be amended, so name it in the R-10.3 DECISIONS entry's 근거 as read through that line.

Bound naming (M-10.3a):
(2) conf/06_SPEC_runner.md:18 '| `R6-exactEP` | `exactEP-true` (참 prior 정확 EP, oracle 상한) | 기존 |'. This is a spec file, so the note needs 사용자 승인.
(3) conf/10_SPEC_stageC.md:824 '| A7 | genie 까지의 격차 중 메운 비율 | 상한 대비 위치 |'. Spec file, 사용자 승인 필요.
(4) conf/results/NUMBERS_PACKAGE_2026-09-22.md:632 '"V1 closes 80.1 % (or 85.3 %) of the gap to the genie bound"'. The claim is already retracted there; only the 'genie bound' name is the problem.
(5) conf/results/jac_spectrum.txt:45 'the learned arm ties the exact-score oracle and the exact-EP bound.' No code generator was found, so treat it as an archived text file.
(6) Figure legends saying 'genie CSI (lower bound)', from these generators: conf/code/figures.py:35 (F3), figures_stagec.py:531 (F10) and :642 (F11), figure_f14.py:46 (F14 family) and figures_stagec2.py:69. I looked at the F11 PNG and its legend reads 'R5 genie CSI (lower bound)'. The images are not regenerated; the generator strings change only after approval.
(7) conf/code/analysis.py:91, docstring 'bound arm (R6-exactEP / R5-genie), which stays last'. This is a docstring with no behaviour change, so it can be edited directly: old 'bound arm (R6-exactEP / R5-genie)' → new 'reference arm (R6-exactEP / R5-genie)'.

Related wording the audit does not cover (for the user to decide; not put in the corrections):
- M-ours-score is also a route_a-loop arm, and several places call it an upper bound: 00_GOAL.md:110 '정확 score = 학습 score의 상한', 03_SPEC_ourmodel.md:48 'oracle 상한 = 게이트 기준', 08_SPEC_analysis.md:34 'oracle 상한', DECISIONS.md:26 'oracle 상한'.
- Older logs from before conf/: docs/handoff/T2_session5_handoff_2026-09-18.md:41 '`exactEP-true`(상한)' and docs/logs/decision_log.md:222 'R-A의 BLER 상한 (exactEP_pf)'.
- docs/RESULTS.md, docs/EXPERIMENTS.md and the other figure caption txt files have no hits.
</details>

---

## 1차 · D2 testbed 서술·게이트 표현 (R-5.2, M-5.2a, G-1.2)

### testbed-gate-1 · R-5.2 + M-5.2a (d2.py 부분) — `conf/code/d2.py` 19-23

- 방식: **docstring edit** · ✅ 검증 통과

**원문 (HEAD)**

```text
Why |alpha_l| is deterministic [05_SPEC §1]: with alpha_l ~ CN (the 3GPP-style convention) H would be
Gaussian GIVEN the angles, i.e. a conditionally-Gaussian mixture, and a GMM would be correctly specified.
Sparse specular multipath with a deterministic power-delay profile is the physically standard mmWave
model; the failure of conditional Gaussianity is a CONSEQUENCE of that physics, and test T2d is its
direct evidence (conf/01_RULES.md §5 framing rule).
```

**제안 문구**

```text
Why |alpha_l| is deterministic [05_SPEC §1]: if the path gains were instead alpha_l ~ CN, independent
of the angles (a common simplification, as opposed to the fixed-amplitude model used here), H would be
Gaussian GIVEN (L, angles), i.e. a conditionally-Gaussian mixture over (L, angles).  The angles are
continuous, so that mixture is continuous: even then a finite-K GMM would approximate it, not be
correctly specified (only D1, whose true prior IS a grid GMM, has a correctly specified GMM arm).
D2 is a CONTROLLED sparse specular model -- fixed |alpha_l|, continuous uniform angles, fixed
exp(-l/tau) power profile -- built to isolate the failure of conditional Gaussianity; it is not
presented as a standard or realistic mmWave channel (05_SPEC:25; retraction 56 in
results/NUMBERS_PACKAGE_2026-09-22.md:695).  Test T2d is the direct evidence that conditional
Gaussianity fails in D2.  The stated reason is never 'unfavourable to the GMM' (conf/01_RULES.md §5).
[record correction 2026-09-23, review_next R-5.2 / M-5.2a: this paragraph previously called CN path
gains 'the 3GPP-style convention', said a GMM 'would be correctly specified', and called D2 'the
physically standard mmWave model'.]
```

<details><summary>근거</summary>

d2.py:13 'CONTINUOUS uniform in the PHYSICAL angle, no grid', :15 '|alpha_l| is DETERMINISTIC', :16 p_l ∝ exp(-l/tau), tau=2. 05_SPEC_testbed_D2.md:3 (D1 참 prior = 격자 GMM → GMM arm correctly specified), :25 ('D2의 차별점은 "실제 채널"이 아니라 "조건부 Gaussian의 파괴"'). results/NUMBERS_PACKAGE_2026-09-22.md:695 철회 56. 출처 확인: git grep -niE 'sionna|38\.901' HEAD -- conf ':!conf/results/review_next' → 0건. git log -S'38.901' / -S'ionna' -- conf → cd241b7e(감사 문서 추가)뿐. '3GPP' 는 d2.py:19, 05_SPEC:23/25, NUMBERS_PACKAGE:549/695 인용뿐. 수학: 각도·L 조건부에서 h 는 독립 CN 계수의 선형결합이므로 Gaussian(정확). 각도가 연속이므로 혼합 측도도 연속이고 유한 K 는 근사. docstring 만 바뀌고 동작은 불변. Demo/ 해시 대상(common.py:183 DEMO_LOCKED = t2_route_a/t2_trellis/t2_gmm)도 아니다. TR 38.901 의 실제 규정은 이 세션에서 확인하지 않아 문구에 넣지 않았다(감사 수정 방향의 38.901 서술은 채택 안 함). 01_RULES:77 금지 절(GMM 불리)은 위반하지 않는다. '물리적으로 표준' 근거 문구와의 정합은 01_RULES 노트 결정(사용자 승인)에 달려 있다. 사용자가 거부하면 'it is not presented as a standard or realistic mmWave channel (...)' 구절만 빼도 R-5.2 부분은 따로 성립한다.

검증: 19-23행은 HEAD에서 글자 그대로 일치한다. 근거 인용이 모두 맞다. d2.py:13/15/16, 05_SPEC:3/16-18/25, NUMBERS_PACKAGE:695(철회 56)를 확인했다. conf에서 'sionna|38.901'은 0건이다(review_next 제외). '3GPP'는 d2.py:19, 05_SPEC:23/25, NUMBERS_PACKAGE:549/695에만 나온다(나머지 매치는 npz 바이너리 하나뿐). git log -S 결과는 cd241b7e 하나다. common.py:183 DEMO_LOCKED도 맞다. 수학 서술에 문제없다. CN 이득이면 (L, 각도) 조건부로 Gaussian이고, 각도가 연속이라 연속 혼합이며, 유한 K는 근사다. 사소한 점 둘(수정 필수 아님). (a) '(only D1 ... has a correctly specified GMM arm)'은 지금 구현된 testbed가 D1/D2뿐이라 성립하지만 '(unlike D1, whose true prior IS a grid GMM, conf/05_SPEC_testbed_D2.md:3)'이 기록과 더 가깝다. (b) 같은 docstring의 기존 표기 '(conf/01_RULES.md §5)'에 맞추려면 경로를 conf/05_SPEC_testbed_D2.md:25, conf/results/NUMBERS_PACKAGE_2026-09-22.md:695로 쓰면 된다.
</details>

### testbed-gate-2 · R-5.2 (05_SPEC 부분) — `conf/05_SPEC_testbed_D2.md` 23 (노트는 23행 뒤에 빈 줄 + 삽입, 25행 [추측, VERIFY] 주의 앞)

- 방식: **spec note (사용자 승인 필요)** · ✏️ 검증 수정 반영 (인용 OK · 수치 OK · 문구 X)

**원문 (HEAD)**

```text
$|\alpha_\ell|$가 **결정적**이므로, **각도를 조건으로 줘도 $\mathbf H$가 Gaussian이 아니다.** 3GPP 계열 모델은 각도가 주어지면 $\alpha_\ell\sim\mathcal{CN}$ 이라 $\mathbf H\mid\text{angles}$가 Gaussian이고, 그래서 conditionally-Gaussian mixture(= GMM)가 correctly specified가 된다. 여기서는 그 성질이 깨진다. 이것이 D2의 존재 이유다.
```

**제안 문구**

```text
> **정정 노트 (2026-09-23, review_next R-5.2) — 사용자 승인 필요.** 위 문단의 "3GPP 계열 모델은 각도가 주어지면 α_ℓ∼CN 이라 … GMM)가 correctly specified가 된다" 는 두 곳이 과하다.
> (i) α_ℓ∼CN 을 "3GPP 계열" 의 성질로 적었으나 저장소에 출처가 없다(HEAD `cd241b7e` conf 전체에서 "38.901"·"Sionna" 0건, review_next 감사 문서 제외. "3GPP" 는 이 문서 23·25행, `code/d2.py:19`, NUMBERS_PACKAGE 의 이 문서 인용뿐이고, 25행도 [추측, VERIFY] 표시다). 출처 없이 적을 수 있는 것은 "각도와 독립인 α_ℓ∼CN 은 흔한 단순화" 정도다(감사 R-5.2 수정 방향의 표현).
> (ii) 그 단순화에서 H|(L, angles) 가 Gaussian 인 것은 맞다. 그러나 각도가 연속 균등(§1 표, 16행)이라 혼합은 연속 혼합이고, 유한 K GMM 은 그 근사이지 correctly specified 가 아니다. correctly specified GMM arm 은 참 prior 를 격자 GMM 으로 정의한 D1 뿐이다(3행).
> 대체 문구: "각도와 독립인 α_ℓ∼CN 이라는 흔한 단순화를 쓰면 H|(L, angles) 가 Gaussian 이 되어 앙상블이 조건부 Gaussian 혼합이 된다(각도가 연속이므로 연속 혼합이고, 유한 K GMM 은 그 근사다). 여기서는 |α_ℓ| 가 결정적이라 그 성질이 깨진다. 이것이 D2의 존재 이유다."
> 25행 주의, D2 정의(§1 표), T2d 는 불변.
```

<details><summary>검증 agent 지적 / 초안 원안</summary>

지적: 23행은 글자 그대로 일치한다. 24행은 빈 줄, 25행은 [추측, VERIFY] 주의다. 16행(연속 균등, 격자 없음)과 3행(D1 격자 GMM, correctly specified) 인용도 맞다. 문제는 (i)의 '기록이 뒷받침하는 범위는 "각도와 독립인 α_ℓ∼CN 은 흔한 단순화" 까지다'이다. 기록에는 이 특성화의 출처가 전혀 없다. 25행조차 [추측, VERIFY]이고, '흔한 단순화'는 감사 R-5.2 수정 방향에서 온 표현이다. 그래서 '기록이 뒷받침한다'고 쓰면 새로 근거를 주장하는 셈이 된다. 나머지 문구와 형식(사용자 승인 필요, 원문 불변)은 규칙에 맞다.

초안 원안:

```text
> **정정 노트 (2026-09-23, review_next R-5.2) — 사용자 승인 필요.** 위 문단의 "3GPP 계열 모델은 각도가 주어지면 α_ℓ∼CN 이라 … GMM)가 correctly specified가 된다" 는 두 곳이 과하다.
> (i) α_ℓ∼CN 을 "3GPP 계열" 의 성질로 적었으나 저장소에 출처가 없다(HEAD `cd241b7e` conf 전체에서 "38.901"·"Sionna" 0건, review_next 감사 문서 제외. "3GPP" 는 이 문서 23·25행, `code/d2.py:19`, NUMBERS_PACKAGE 의 이 문서 인용뿐). 기록이 뒷받침하는 범위는 "각도와 독립인 α_ℓ∼CN 은 흔한 단순화" 까지다.
> (ii) 그 단순화에서 H|(L, angles) 가 Gaussian 인 것은 맞다. 그러나 각도가 연속 균등(§1 표, 16행)이라 혼합은 연속 혼합이고, 유한 K GMM 은 그 근사이지 correctly specified 가 아니다. correctly specified GMM arm 은 참 prior 를 격자 GMM 으로 정의한 D1 뿐이다(3행).
> 대체 문구: "각도와 독립인 α_ℓ∼CN 이라는 흔한 단순화를 쓰면 H|(L, angles) 가 Gaussian 이 되어 앙상블이 조건부 Gaussian 혼합이 된다(각도가 연속이므로 연속 혼합이고, 유한 K GMM 은 그 근사다). 여기서는 |α_ℓ| 가 결정적이라 그 성질이 깨진다. 이것이 D2의 존재 이유다."
> 25행 주의, D2 정의(§1 표), T2d 는 불변.
```
</details>

<details><summary>근거</summary>

05_SPEC_testbed_D2.md:16 (AoA/AoD 연속 균등, 격자 없음), :3 (D1 = 격자 GMM, correctly specified), :25 ([추측, VERIFY] 주의는 GMM 유불리만 다루고 CN 특성화는 다루지 않는다, 감사 R-5.2 근거). grep 결과는 위 d2.py 항목과 같다. 사용자 소유 spec 이라 원문을 두고 노트만 제안한다.

검증: (위 참조)
</details>

### testbed-gate-3 · R-5.2 (DECISIONS) — `conf/DECISIONS.md` append (현재 마지막 행 104 뒤)

- 방식: **DECISIONS append** · ✅ 검증 통과

**원문 (HEAD)**

```text
(append-only — 대체할 원문 없음. 직전 마지막 행 104: `[2026-09-23 00:10 KST] "genie 에 더 붙일 수 있나" — 재분석으로 답했고, …`)
```

**제안 문구**

```text
`[2026-09-23 __:__ KST] 정정 — "α_ℓ∼CN 은 3GPP 계열 규약이고 그러면 GMM 이 correctly specified" 는 과했다 (review_next R-5.2) | code/d2.py:19-20 docstring 을 "각도와 독립인 α_ℓ∼CN 은 흔한 단순화다. 그때 H|(L, 각도) 는 Gaussian 이나 각도가 연속이라 혼합도 연속이고 유한 K GMM 은 근사다" 로 바꿨다(동작 변경 없음). 05_SPEC_testbed_D2.md:23 은 사용자 소유라 원문을 두고 노트만 제안했다(사용자 승인 필요) | (i) HEAD cd241b7e 의 conf 전체(review_next 감사 문서 제외)에서 "38.901"·"Sionna" 0건, "3GPP" 는 d2.py:19·05_SPEC:23/25·NUMBERS_PACKAGE:549/695 뿐이다. "3GPP 계열 규약" 의 출처가 기록에 없다. TR 38.901 의 실제 규정은 이 세션에서 확인하지 않았으므로 문구에 넣지 않았다. (ii) 각도는 연속 균등이다(05_SPEC:16, d2.py:13 "no grid"). CN 이득을 가정해도 조건부 Gaussian 성분이 연속으로 늘어선 연속 혼합이다. 유한 K GMM arm 이 correctly specified 인 testbed 는 격자 GMM 으로 정의된 D1 뿐이다(05_SPEC:3). (iii) D2 정의·생성기·T2d 는 불변 | d2.py docstring 을 cd241b7e 판으로 되돌리면 원상(코드 경로 무관, Demo/ 해시 대상 아님 — common.py:183 DEMO_LOCKED)`
```

<details><summary>근거</summary>

append-only 형식은 DECISIONS.md:4 '[시각] 모호했던 점 | 선택 | 근거 | 되돌리는 법'을 따른다. 정정 제목 형식은 DECISIONS.md:26 '[2026-09-20 13:25 KST] 정정 — …'. 수치·위치는 위 두 항목에서 재확인했다.

검증: 104행이 마지막 행이고, 인용한 앞부분이 일치한다. 4행 형식과 26행 '정정 —' 제목 형식을 따른다. grep과 위치 수치를 재확인했다. 사소한 점: 선택 필드 안의 'H|(L, 각도)'에 '|'가 하나 더 들어간다. 기존 DECISIONS 행 중 25개도 필드 밖 '|'를 포함하므로 규칙 위반은 아니다. 파싱 모호성을 피하려면 '(L, 각도) 조건부 H' 로 쓰면 된다.
</details>

### testbed-gate-4 · M-5.2a (01_RULES) — `conf/01_RULES.md` 77 (노트는 77행 바로 뒤, 같은 목록 항목의 들여쓴 인용으로)

- 방식: **spec note (사용자 승인 필요)** · ✏️ 검증 수정 반영 (인용 OK · 수치 OK · 문구 X)

**원문 (HEAD)**

```text
- **testbed 선택 근거는 "물리적으로 표준이라서"이지 "GMM에 불리해서"가 아니다.** 후자를 문서·코드 주석·결과 파일 어디에도 쓰지 않는다.
```

**제안 문구**

```text
> **노트 (2026-09-23, review_next M-5.2a) — 사용자 승인 필요.** 이 행의 금지("GMM에 불리해서" 를 쓰지 않는다)는 그대로다. 문제는 앞 절의 근거 "물리적으로 표준이라서" 다. 같은 기록의 두 곳이 반대로 적는다. `05_SPEC_testbed_D2.md:25` 는 "D2의 차별점은 "실제 채널"이 아니라 "조건부 Gaussian의 파괴"" 라 적는다. `results/NUMBERS_PACKAGE_2026-09-22.md:695` 는 철회 56 으로 "D2 is a standard mmWave channel, so the result transfers to real deployments." 를 인용 금지로 둔다. D2 의 정의(고정 |α_ℓ|, 연속 균등 각도, 고정 지수 PDP τ=2 — `05_SPEC_testbed_D2.md:16-18`)는 통제된 모델 하나이지 표준 채널이 아니다.
  > 제안 문구: "**testbed 선택 근거는 "조건부 Gaussian 가정의 파괴를 분리해 보는 통제 모델이라서"이지 "GMM에 불리해서"가 아니다.** 후자를 문서·코드 주석·결과 파일 어디에도 쓰지 않는다."
  > 같은 근거 문구가 `05_SPEC_testbed_D2.md:5`, `10_SPEC_stageC.md:176`, `PROMPT.md:88` 에도 있다(각각 노트 제안). `DECISIONS.md:23`([2026-09-20 12:35 KST] 행)의 근거 "D2 선택 근거가 "물리적으로 표준"이므로" 도 같은 문구이며, append-only 라 M-5.2a 정정 행이 대신 짚는다.
```

<details><summary>검증 agent 지적 / 초안 원안</summary>

지적: 77행은 글자 그대로 일치한다. 05_SPEC:25, NUMBERS_PACKAGE:695, 05_SPEC:16-18 인용도 맞고, 금지 절을 유지하는 방향도 맞다. 다만 '같은 근거 문구가 … 에도 있다' 목록이 빠져 있다. 초안이 쓴 grep 'physically standard|물리적으로 표준' 자체가 conf/DECISIONS.md:23([2026-09-20 12:35 KST] 행)을 돌려준다. 그 행에는 '… D2 선택 근거가 "물리적으로 표준"이므로 표준 120도 섹터가 맞는 읽기다. … 이것은 물리의 귀결이지 GMM 을 불리하게 만든 것이 아니며'라고 적혀 있다.

초안 원안:

```text
> **노트 (2026-09-23, review_next M-5.2a) — 사용자 승인 필요.** 이 행의 금지("GMM에 불리해서" 를 쓰지 않는다)는 그대로다. 문제는 앞 절의 근거 "물리적으로 표준이라서" 다. 같은 기록의 두 곳이 반대로 적는다. `05_SPEC_testbed_D2.md:25` 는 "D2의 차별점은 "실제 채널"이 아니라 "조건부 Gaussian의 파괴"" 라 적는다. `results/NUMBERS_PACKAGE_2026-09-22.md:695` 는 철회 56 으로 "D2 is a standard mmWave channel, so the result transfers to real deployments." 를 인용 금지로 둔다. D2 의 정의(고정 |α_ℓ|, 연속 균등 각도, 고정 지수 PDP τ=2 — `05_SPEC_testbed_D2.md:16-18`)는 통제된 모델 하나이지 표준 채널이 아니다.
  > 제안 문구: "**testbed 선택 근거는 "조건부 Gaussian 가정의 파괴를 분리해 보는 통제 모델이라서"이지 "GMM에 불리해서"가 아니다.** 후자를 문서·코드 주석·결과 파일 어디에도 쓰지 않는다."
  > 같은 근거 문구가 `05_SPEC_testbed_D2.md:5`, `10_SPEC_stageC.md:176`, `PROMPT.md:88` 에도 있다(각각 노트 제안).
```
</details>

<details><summary>근거</summary>

01_RULES.md:77(HEAD). 충돌 대상은 NUMBERS_PACKAGE_2026-09-22.md:695(철회 56, 실제 경로 conf/results/NUMBERS_PACKAGE_2026-09-22.md, HEAD 에 추적됨)와 05_SPEC_testbed_D2.md:25다. D2 정의는 05_SPEC:16-18과 d2.py:13-16. 같은 근거 문구를 git grep -nE 'physically standard|물리적으로 표준' HEAD -- conf 로 찾으면 01_RULES:77, 05_SPEC:5, 10_SPEC_stageC:176, PROMPT.md:88, PAPER_MATERIALS:769, d2.py:21 이 나온다(review_next 제외). 감사는 05_SPEC:5·10_SPEC:176·PROMPT.md:88 을 목록에 넣지 않았다. 사용자 소유 규칙 파일이라 l.77 을 일방적으로 바꾸지 않는다.

검증: (위 참조)
</details>

### testbed-gate-5 · M-5.2a (PAPER_MATERIALS) — `conf/PAPER_MATERIALS.md` 769-770 (노트는 770행 뒤, 771행 빈 줄 앞)

- 방식: **other** · ✅ 검증 통과

**원문 (HEAD)**

```text
- **testbed 선택 근거를 "GMM 에 불리해서"로 서술** — `01_RULES §5` 가 금지. 근거는 "물리적으로 표준"이고
  조건부 Gaussian 파괴는 그 물리의 귀결이며 T2d 가 직접 증거다.
```

**제안 문구**

```text
> **정정 (2026-09-23, review_next M-5.2a)**: 앞 절의 금지("GMM 에 불리해서" 로 서술하지 않는다)는 유지한다. 뒤따르는 "근거는 "물리적으로 표준"이고 조건부 Gaussian 파괴는 그 물리의 귀결" 은 같은 기록의 철회와 충돌한다. `results/NUMBERS_PACKAGE_2026-09-22.md:695`(철회 56)는 "D2 is a standard mmWave channel, so the result transfers to real deployments." 를 인용 금지로 두고, `05_SPEC_testbed_D2.md:25` 는 "D2의 차별점은 "실제 채널"이 아니라 "조건부 Gaussian의 파괴"" 라 적는다. D2 는 고정 |α_ℓ|·연속 균등 각도·고정 지수 PDP(τ=2)로 정의된 통제 모델 하나다(`05_SPEC_testbed_D2.md:16-18`).
  > 인용할 때는 이렇게 쓴다: "근거는 조건부 Gaussian 가정의 파괴를 분리해 보는 통제된 희소 정반사 모델이라는 것이고, T2d 가 그 파괴의 직접 증거다." `01_RULES:77` 의 같은 근거 문구는 사용자 결정을 기다린다(review_next M-5.2a 노트).
```

<details><summary>근거</summary>

PAPER_MATERIALS.md:769-770(HEAD, 4ad41df9 이후 변경 없음. git diff 4ad41df9 cd241b7e 에 이 파일 없음). NUMBERS_PACKAGE_2026-09-22.md:695, 05_SPEC:16-18/25. 원문 방식: PAPER_MATERIALS 는 명시 규칙이 없어 STATUS 인라인 정정과 같은 형식(원문 불변 + 뒤에 노트)을 따른다. §17.1 목록 항목 안이라 들여쓴 인용으로 둔다.

검증: 769-770행이 글자 그대로 일치하고 771행은 빈 줄이다. 4ad41df9..cd241b7e 사이에 이 파일은 바뀌지 않았다. 근거 인용이 맞고, 원문을 그대로 두고 노트를 뒤에 다는 형식도 맞다. 금지 절을 유지하고 과잉 정정은 없다.
</details>

### testbed-gate-6 · M-5.2a (05_SPEC:5, 감사 목록 밖 추가 발견) — `conf/05_SPEC_testbed_D2.md` 5 (노트는 5행 뒤에 이어지는 인용 줄로)

- 방식: **spec note (사용자 승인 필요)** · ✅ 검증 통과

**원문 (HEAD)**

```text
> **선택 기준은 "GMM에 불리해서"가 아니라 "물리적으로 표준이라서"다.** 전자는 리뷰어가 정확히 그 지점을 친다. 아래 §1의 채널은 mmWave 희소 다중경로라는 표준 모델이고, 조건부 Gaussian 가정이 깨지는 것은 그 물리의 **귀결**이지 목적이 아니다.
```

**제안 문구**

```text
>
> **노트 (2026-09-23, review_next M-5.2a) — 사용자 승인 필요.** 이 문단의 "물리적으로 표준이라서"·"mmWave 희소 다중경로라는 표준 모델" 은 이 문서 25행("D2의 차별점은 "실제 채널"이 아니라 "조건부 Gaussian의 파괴"")과 `results/NUMBERS_PACKAGE_2026-09-22.md:695` 철회 56 과 충돌한다. "GMM에 불리해서" 가 아니라는 부분은 유지한다. 제안 문구: "선택 기준은 "GMM에 불리해서"가 아니라 "조건부 Gaussian 가정의 파괴를 분리해 보는 통제 모델이라서"다. 아래 §1의 채널은 |α_ℓ| 와 PDP 를 고정한 희소 정반사 다중경로 통제 모델이고, 조건부 Gaussian 가정이 깨지는 것은 결정적 |α_ℓ| 의 귀결이다."
```

<details><summary>근거</summary>

git grep 'physically standard|물리적으로 표준' HEAD -- conf 에서 05_SPEC:5 가 나오지만 감사 M-5.2a 목록에는 없다. 같은 파일 :25 와 NUMBERS_PACKAGE:695 가 이 문구와 모순된다. 결정적 |α_ℓ| 는 05_SPEC:17-18, :23. 사용자 소유 spec 이다.

검증: 5행은 글자 그대로 일치한다(6행은 빈 줄). 대체 문구의 '결정적 |α_ℓ| 의 귀결'은 23행과 17-18행이 뒷받침한다. 이 문단은 원래 '귀결이지 목적이 아니다'라 적었지만 23행이 '이것이 D2의 존재 이유다'라 적으므로 '통제 모델이라서'로 바꿔도 과잉 정정이 아니다. 사용자 승인 필요 표시가 있다.
</details>

### testbed-gate-7 · M-5.2a (10_SPEC_stageC:176, 감사 목록 밖 추가 발견) — `conf/10_SPEC_stageC.md` 176-177 (노트는 177행 뒤, 178행 빈 줄 앞에 빈 줄 + 삽입)

- 방식: **spec note (사용자 승인 필요)** · ✅ 검증 통과

**원문 (HEAD)**

```text
그리고 테스트베드 선택 근거는 **계속** "물리적으로 표준인 mmWave 희소 다중경로"이지
어느 방법에 유·불리해서가 아니다 (01_RULES §5).
```

**제안 문구**

```text
> **노트 (2026-09-23, review_next M-5.2a) — 사용자 승인 필요.** "물리적으로 표준인 mmWave 희소 다중경로" 는 `05_SPEC_testbed_D2.md:25` 와 `results/NUMBERS_PACKAGE_2026-09-22.md:695`(철회 56)와 충돌한다. 제안 문구: "그리고 테스트베드 선택 근거는 **계속** "조건부 Gaussian 가정의 파괴를 분리해 보는 통제된 희소 정반사 모델"이지 어느 방법에 유·불리해서가 아니다 (01_RULES §5)." 01_RULES:77 노트와 함께 결정.
```

<details><summary>근거</summary>

10_SPEC_stageC.md:176-177(HEAD). 충돌 근거는 위 01_RULES 항목과 같다. 사전 등록 문서라 원문을 두고 노트만 단다.

검증: 176-177행이 글자 그대로 일치하고 178행은 빈 줄이다. 문구와 형식에 문제없다.
</details>

### testbed-gate-8 · M-5.2a (PROMPT.md:88, 감사 목록 밖 추가 발견) — `conf/PROMPT.md` 88-90 (노트는 90행 뒤)

- 방식: **spec note (사용자 승인 필요)** · ✅ 검증 통과

**원문 (HEAD)**

```text
D2 를 고른 근거는 "물리적으로 표준인 mmWave 희소 다중경로라서"이지 "GMM 에 불리해서"가
아니다. 후자를 문서·코드 주석·결과 파일 어디에도 쓰지 마라. 조건부 Gaussian 이 깨지는 것은
그 물리의 귀결이고, T2d 가 그 직접 증거다.
```

**제안 문구**

```text
(노트 2026-09-23, review_next M-5.2a — 사용자 승인 필요. 프롬프트 원문을 그대로 쓰는 파일이라면 노트 대신 원문 교체 여부를 사용자가 정한다.) 제안 문구: "D2 를 고른 근거는 "조건부 Gaussian 가정의 파괴를 분리해 보는 통제된 희소 정반사 모델이라서"이지 "GMM 에 불리해서"가 아니다. 후자를 문서·코드 주석·결과 파일 어디에도 쓰지 마라. 조건부 Gaussian 이 깨지는 것은 결정적 |α_ℓ| 의 귀결이고, T2d 가 그 직접 증거다." 근거: `05_SPEC_testbed_D2.md:25`, `results/NUMBERS_PACKAGE_2026-09-22.md:695`(철회 56).
```

<details><summary>근거</summary>

PROMPT.md:88-90(HEAD) 도 01_RULES:77 과 같은 근거 문구를 쓴다. 감사 grep 목록에는 없다. 충돌 근거는 05_SPEC:25, NUMBERS_PACKAGE:695.

검증: 88-90행이 글자 그대로 일치한다. 91행이 같은 [testbed 서술] 블록에서 이어지므로, 원문 교체 여부를 사용자가 정하게 한 단서가 적절하다.
</details>

### testbed-gate-9 · M-5.2a (DECISIONS) — `conf/DECISIONS.md` append (R-5.2 행 다음)

- 방식: **DECISIONS append** · ✏️ 검증 수정 반영 (인용 OK · 수치 OK · 문구 X)

**원문 (HEAD)**

```text
(append-only — 대체할 원문 없음)
```

**제안 문구**

```text
`[2026-09-23 __:__ KST] 정정 — D2 를 "물리적으로 표준인 mmWave 모델" 로 부른 근거 문구가 기록 안의 철회와 모순 (review_next M-5.2a) | code/d2.py:21-23 docstring 을 "조건부 Gaussian 파괴를 분리하는 통제된 희소 정반사 모델(고정 |α_l|, 연속 균등 각도, 고정 PDP)" 로 바꿨고, PAPER_MATERIALS:769-770 에는 인라인 노트를 달았다. 01_RULES:77, 05_SPEC_testbed_D2.md:5, 10_SPEC_stageC.md:176-177, PROMPT.md:88-90 은 사용자 소유라 노트만 제안했다(사용자 승인 필요). 원문은 불변이다. 01_RULES:77 의 금지 절("GMM에 불리해서" 를 쓰지 않는다)은 그대로다. 이 파일 23행([2026-09-20 12:35 KST])의 근거 중 "D2 선택 근거가 "물리적으로 표준"이므로" 도 같은 문구라 이 행으로 대체한다. 그 행의 선택(S2 = 물리각 ±π/3)은 바꾸지 않는다 — 같은 행의 첫 근거(05_SPEC 이 θ/φ 를 AoA/AoD 물리각으로 쓰고 "섹터 ±pi/3" 라 함)는 이 정정과 무관하다 | 01_RULES:77 은 근거를 "물리적으로 표준이라서" 로 정한다. 그런데 results/NUMBERS_PACKAGE_2026-09-22.md:695(철회 56)는 "D2 is a standard mmWave channel, so the result transfers to real deployments." 를 인용 금지로 두고, 05_SPEC_testbed_D2.md:25 는 "D2의 차별점은 "실제 채널"이 아니라 "조건부 Gaussian의 파괴"" 라 적는다. 같은 기록이 두 방향을 지시한다. D2 정의(|α_ℓ| 결정적, 각도 연속 균등, p_ℓ∝e^{−ℓ/2} 고정; 05_SPEC:16-18)는 통제 모델 하나다. 05_SPEC:5·10_SPEC_stageC:176·PROMPT.md:88·DECISIONS:23 은 감사 목록에 없어 같은 grep(physically standard|물리적으로 표준)으로 추가 확인했다 | d2.py docstring 을 cd241b7e 판으로 되돌리고 노트 행을 지운다(원문 행은 고치지 않았으므로 그것으로 원상)`
```

<details><summary>검증 agent 지적 / 초안 원안</summary>

지적: (1) d2.py에서 M-5.2a에 해당하는 범위는 21-23행이다(감사 위치 d2.py:21-23, 21행 'Sparse specular …'부터 23행 'direct evidence …'까지). 초안은 '21-22'로 적었다. (2) 초안이 인용한 grep(physically standard|물리적으로 표준)은 DECISIONS.md:23도 돌려주는데, 목록에서 빠졌다. append-only 파일이므로 이 정정 행이 23행 근거의 '"물리적으로 표준"이므로' 부분을 직접 짚어야 한다. 그 행의 선택(S2 = 물리각 ±π/3)까지 뒤집으면 과잉 정정이다. 같은 행의 첫 근거(05_SPEC이 θ/φ를 물리각으로 쓰고 '섹터 ±pi/3'라 함)는 이 정정과 무관하다. (3) '추가 확인했다' 목록에도 DECISIONS:23을 넣어야 한다. 나머지 인용은 맞다(NUMBERS_PACKAGE:695, 05_SPEC:16-18/25, τ=2).

초안 원안:

```text
`[2026-09-23 __:__ KST] 정정 — D2 를 "물리적으로 표준인 mmWave 모델" 로 부른 근거 문구가 기록 안의 철회와 모순 (review_next M-5.2a) | code/d2.py:21-22 docstring 을 "조건부 Gaussian 파괴를 분리하는 통제된 희소 정반사 모델(고정 |α_l|, 연속 균등 각도, 고정 PDP)" 로 바꿨고, PAPER_MATERIALS:769-770 에는 인라인 노트를 달았다. 01_RULES:77, 05_SPEC_testbed_D2.md:5, 10_SPEC_stageC.md:176, PROMPT.md:88 은 사용자 소유라 노트만 제안했다(사용자 승인 필요). 원문은 불변이다. 01_RULES:77 의 금지 절("GMM에 불리해서" 를 쓰지 않는다)은 그대로다 | 01_RULES:77 은 근거를 "물리적으로 표준이라서" 로 정한다. 그런데 results/NUMBERS_PACKAGE_2026-09-22.md:695(철회 56)는 "D2 is a standard mmWave channel, so the result transfers to real deployments." 를 인용 금지로 두고, 05_SPEC_testbed_D2.md:25 는 "D2의 차별점은 "실제 채널"이 아니라 "조건부 Gaussian의 파괴"" 라 적는다. 같은 기록이 두 방향을 지시한다. D2 정의(|α_ℓ| 결정적, 각도 연속 균등, p_ℓ∝e^{−ℓ/2} 고정; 05_SPEC:16-18)는 통제 모델 하나다. 05_SPEC:5·10_SPEC_stageC:176·PROMPT.md:88 은 감사 목록에 없어 같은 grep(physically standard|물리적으로 표준)으로 추가 확인했다 | d2.py docstring 을 cd241b7e 판으로 되돌리고 노트 행을 지운다(원문 행은 고치지 않았으므로 그것으로 원상)`
```
</details>

<details><summary>근거</summary>

위 M-5.2a 항목들의 위치·인용을 HEAD 에서 재확인했다.

검증: (위 참조)
</details>

### testbed-gate-10 · G-1.2 (감사 STATUS:825·828 → HEAD 826·829) — `conf/STATUS.md` 826, 829 (826-829 가 한 목록 항목이므로 노트는 829행 뒤)

- 방식: **STATUS inline note** · ✅ 검증 통과

**원문 (HEAD)**

```text
826: - **이 실행의 체크포인트 `ckpt/d2sx_N10000_a1.pt` 는 사전 등록 게이트에 실패했다** (GC 0.243 vs 0.15).
829:   **게이트 통과 모델의 결과는 `tables_D2_C.txt` 에 있고 V1 은 거기서도 0.145 다.**
```

**제안 문구**

```text
> **정정 (2026-09-23, review_next G-1.2)**: 826행 "체크포인트 `ckpt/d2sx_N10000_a1.pt` 는 사전 등록 게이트에 실패했다 (GC 0.243 vs 0.15)" 와 829행 "게이트 통과 모델" 은 D2 체크포인트에 게이트 판정을 직접 붙인 줄임말이다. 게이트는 D1 에서만 측정되고(10_SPEC_stageC:126-129) D2 체크포인트에는 게이트 행이 없다(`tables_D2_B1e4.txt:45`, `tables_D2_C.txt:45`: `NO GATE RECORD mentions d2sx_N…_a1.pt -- UNVERIFIED here`). GC 0.243 은 같은 레시피·같은 예산의 D1 형제 `sx_N10000_D1.pt` 값이다(`samplecx_D1.txt:28`, GC 0.24333 FAIL).
  > PAPER_MATERIALS:819-820 규칙대로 읽는다. 826: "이 실행의 체크포인트 `ckpt/d2sx_N10000_a1.pt` 는 D1 형제(N=1e4)가 게이트에 실패한 레시피·예산으로 D2 에 학습한 것이다 (D1 GC 0.243 vs 0.15)". 829: "D1 형제 `sx_N160000_D1.pt` 가 게이트를 통과한 레시피로 D2 에 학습한 체크포인트(`d2sx_N160000_a1.pt`)의 결과는 `tables_D2_C.txt` 에 있고 V1 은 거기서도 0.145 다." 수치·판정 불변.
```

<details><summary>근거</summary>

줄 번호: 감사는 4ad41df9 기준이고, cd241b7e 가 STATUS 머리말에 1행을 더해(git diff 4ad41df9 cd241b7e -- conf/STATUS.md: @@ -1,7 +1,8 @@ 한 덩어리뿐) 4행 이후가 +1 밀렸다. samplecx_D1.txt:28 '10,000 … GB 0.01174 GC 0.24333 GD 0.16081 … FAIL'(samplecx.csv 행 10000: GC 2.433337e-01). ckpt 이름 규칙은 run_samplecx.py:16 f"sx_N{N}_D1.pt". tables_D2_B1e4.txt:45 와 tables_D2_C.txt:45 는 'NO GATE RECORD … UNVERIFIED here'. 형제 PASS 는 LADDER_C.md:1 'GB +0.27% | GC 0.0999 | GD 0.0718 | PASS | GATED from sx_N160000_D1.pt'. 문구 수준 결함이고 면책(STATUS 390-392, 654-660)은 실재한다.

검증: 826행과 829행이 글자 그대로 일치한다. +1 이동도 git diff 4ad41df9 cd241b7e -- conf/STATUS.md(@@ -1,7 +1,8 @@ 한 덩어리)로 확인했다. 수치를 재도출했다. samplecx.csv 10000행 GC 2.433337e-01(False), samplecx_D1.txt:28 GC 0.24333 FAIL, tables_D2_B1e4.txt:45와 tables_D2_C.txt:45 게이트 행 없음, LADDER_C.md:1 PASS다. '같은 레시피'도 확인된다. logs/train_d2sx_N10000_a1.log와 logs/train_sx_N10000_D1.log의 hp 행이 같다(dit vp/angle w64 d6 lr 2.238046e-3 ema0.999 batch256). 선택 보강: results/NUMBERS_PACKAGE_2026-09-22.md:418과 :575가 이미 'STATUS.md:825 and 10_SPEC_stageC.md:453 … as if measured on that file. It was not.'로 이 결함을 지목했다. 노트에 선행 기록으로 인용하면 좋다.
</details>

### testbed-gate-11 · G-1.2 (감사 STATUS:875 → HEAD 876, 거울형 875 추가) — `conf/STATUS.md` 875, 876 (문단 875-877, 노트는 877행 뒤)

- 방식: **STATUS inline note** · ✅ 검증 통과

**원문 (HEAD)**

```text
875: 두 표 모두 체크포인트가 **게이트에 실패**했다 (N=1e4 GC 0.243, N=4e4 GC 0.167). §6d 가 미리
876: "arm 결과가 아니라 예산 축 측정" 으로 규정했다. 게이트 통과 모델의 결과는 `tables_D2_C.txt` 에
```

**제안 문구**

```text
> **정정 (2026-09-23, review_next G-1.2)**: 875행 "두 표 모두 체크포인트가 게이트에 실패했다" 와 876행 "게이트 통과 모델" 도 같은 줄임말이다. 두 표의 D2 체크포인트(`d2sx_N10000_a1.pt`, `d2sx_N40000_a1.pt`)에는 게이트 행이 없고(`tables_D2_B1e4.txt:45`, `tables_D2_B4e4.txt:45`), GC 0.243 / 0.167 은 D1 형제 값이다(`samplecx_D1.txt:28-29`, GC 0.24333 / 0.16651, 둘 다 FAIL). 읽는 법 — 875: "두 표 모두 D1 형제가 게이트에 실패한 예산의 D2 학습본이다 (D1 형제 GC: N=1e4 0.243, N=4e4 0.167)". 876 은 829행 정정과 같다. 수치 불변.
```

<details><summary>근거</summary>

samplecx_D1.txt:28 GC 0.24333 FAIL, :29 '40,000 … GC 0.16651 … FAIL'. tables_D2_B4e4.txt:45 'NO GATE RECORD mentions d2sx_N40000_a1.pt -- UNVERIFIED here'. 875행 거울형은 감사 목록에 없다(감사는 825 의 거울형만 지목).

검증: 875-877행이 일치한다. '두 표'는 836행 기준 tables_D2_B1e4와 B4e4다. 확인한 수치: samplecx_D1.txt:29 GC 0.16651 FAIL(csv 1.665124e-01), tables_D2_B4e4.txt:45 게이트 행 없음.
</details>

### testbed-gate-12 · G-1.2 (감사 STATUS:1256 → HEAD 1257) — `conf/STATUS.md` 1257 (제목, 노트는 1257행 뒤에 빈 줄 + 삽입)

- 방식: **STATUS inline note** · ✅ 검증 통과

**원문 (HEAD)**

```text
# ■■■ B16e4 — **게이트 통과 + 동일예산을 동시에 만족하는 첫 표** (2026-09-22 15:10 KST)
```

**제안 문구**

```text
> **정정 (2026-09-23, review_next G-1.2)**: 제목의 "게이트 통과" 는 이 표의 D2 체크포인트 `d2sx_N160000_a1.pt` 의 판정이 아니다. 그 체크포인트에는 게이트 행이 없다(`tables_D2_B16e4.txt:45` `NO GATE RECORD mentions d2sx_N160000_a1.pt -- UNVERIFIED here`). PASS 는 D1 형제 `sx_N160000_D1.pt` 의 행이다(`LADDER_C.md:1`, GB +0.27% / GC 0.0999 / GD 0.0718). 한정어는 본문 1262행에만 있다. 제목은 이렇게 읽는다: "B16e4 — D1 형제 게이트 PASS 레시피 + 동일예산을 동시에 만족하는 첫 표".
```

<details><summary>근거</summary>

tables_D2_B16e4.txt:45, LADDER_C.md:1, STATUS.md:1262 '(D1 형제 `sx_N160000_D1.pt` 가 GA~GD PASS, `LADDER_C.md:1`)'. samplecx_D1.txt:30 도 같은 값(GB 0.00266 GC 0.09986 GD 0.07183 PASS)이다.

검증: 1257행 제목이 일치하고 1262행에 한정어가 있다. tables_D2_B16e4.txt:45와 LADDER_C.md:1(GB +0.27% / GC 0.0999 / GD 0.0718)을 확인했다. samplecx_D1.txt:30 값(GB 0.00266 GC 0.09986 GD 0.07183 PASS)도 맞다.
</details>

### testbed-gate-13 · G-1.2 (감사 STATUS:1291 → HEAD 1292) — `conf/STATUS.md` 1292 (표 머리 행, 표가 1292-1297 이므로 노트는 1297행 뒤)

- 방식: **STATUS inline note** · ✅ 검증 통과

**원문 (HEAD)**

```text
| arm | N=1e4 (b\* 내부 증명) | N=4e4 | N=1.6e5 (게이트 통과) |
```

**제안 문구**

```text
> **정정 (2026-09-23, review_next G-1.2)**: 1292행 열 머리 "N=1.6e5 (게이트 통과)" 는 "N=1.6e5 (D1 형제 게이트 PASS)" 로 읽는다. 이 열의 D2 체크포인트에는 게이트 행이 없고(`tables_D2_B16e4.txt:45`), PASS 는 `LADDER_C.md:1` 의 `sx_N160000_D1.pt` 행이다. 나머지 두 열도 같은 규칙이다(N=1e4·4e4 는 D1 형제 FAIL, `samplecx_D1.txt:28-29`). 표 수치 불변.
```

<details><summary>근거</summary>

tables_D2_B16e4.txt:45, LADDER_C.md:1, samplecx_D1.txt:28-29 GC 0.24333/0.16651. 표 행 사이에 인용을 넣으면 표가 끊기므로 표 끝(1297) 뒤에 둔다.

검증: 1292행이 일치하고 표는 1292-1297행이다. 인용 수치도 맞다.
</details>

### testbed-gate-14 · G-1.2 (STATUS 1304-1305·1307, 감사 목록 밖 추가 발견) — `conf/STATUS.md` 1304, 1307 (노트는 1307행 뒤)

- 방식: **STATUS inline note** · ✅ 검증 통과

**원문 (HEAD)**

```text
1304: > "사전 등록 게이트를 통과한 학습 prior 가, 같은 채널 집합으로 적합한 GMM 을 같은 수신기에서
1307: 이전에는 게이트 통과 표(`tables_D2_C.txt`)는 예산이 달랐고, 동일예산 표(B1e4/B4e4)는 게이트 실패였다.
```

**제안 문구**

```text
> **정정 (2026-09-23, review_next G-1.2, 감사 목록 밖 추가 발견)**: 1304행 "사전 등록 게이트를 통과한 학습 prior 가" 와 1307행 "게이트 통과 표"·"게이트 실패였다" 도 같은 줄임말이다. 게이트 부분만 이렇게 읽는다. 1304: "사전 등록 게이트를 D1 에서 통과한 레시피로 D2 에 학습한 prior 가". 1307: "이전에는 D1 형제 게이트 PASS 레시피 표(`tables_D2_C.txt`)는 예산이 달랐고, 동일예산 표(B1e4/B4e4)는 D1 형제 게이트 FAIL 예산이었다(`samplecx_D1.txt:28-29`, GC 0.24333 / 0.16651)." 이 정정은 게이트 문구만 다루며 문장의 수치·범위는 건드리지 않는다.
```

<details><summary>근거</summary>

1304-1305 는 '이 표로 처음 쓸 수 있게 된 문장'(1302) 으로 인용될 문장이라 PAPER_MATERIALS:819-820 규칙 위반의 파급이 가장 크다. 감사·반박 검토 둘 다 이 줄을 놓쳤다. 근거 파일은 tables_D2_B16e4.txt:45, LADDER_C.md:1, samplecx_D1.txt:28-29.

검증: 1304행과 1307행이 일치한다. 노트 문구는 맞다. 다만 근거란의 '파급이 가장 크다'는 틀렸다. 1602행 '## 헤드라인 문장의 최종 형태' 아래 1604-1606행이 같은 문장('> **사전 등록 게이트를 통과한 학습 prior 가, 같은 1.6e5 채널 집합으로 …')의 최종판인데 초안에서 빠졌다(missing 참조).
</details>

### testbed-gate-15 · G-1.2 (감사 STATUS:1315 → HEAD 1316) — `conf/STATUS.md` 1316 (목록 항목 1311-1316 의 끝, 노트는 1316행 뒤)

- 방식: **STATUS inline note** · ✅ 검증 통과

**원문 (HEAD)**

```text
이고, 이 표는 "게이트 통과 모델에서도 같은 크기의 격차" 를 보이는 확인점이다.
```

**제안 문구**

```text
> **정정 (2026-09-23, review_next G-1.2)**: "게이트 통과 모델에서도" 는 "D1 형제 게이트 PASS 레시피로 학습한 D2 체크포인트에서도" 로 읽는다(근거는 1257행 정정과 같다: `tables_D2_B16e4.txt:45`, `LADDER_C.md:1`). 수치 불변.
```

<details><summary>근거</summary>

tables_D2_B16e4.txt:45, LADDER_C.md:1.

검증: 1316행이 일치하고, 1311-1316행이 한 목록 항목이다.
</details>

### testbed-gate-16 · G-1.2 (STATUS 340-341·1080·1348·1456, 감사 목록 밖 추가 발견) — `conf/STATUS.md` 340-341 (노트는 341행 뒤) / 1080 (노트는 1080행 뒤) / 1348 (문단 1346-1350, 노트는 1350행 뒤) / 1456 (노트는 1456행 뒤)

- 방식: **STATUS inline note** · ✅ 검증 통과

**원문 (HEAD)**

```text
340: **경고**: 위는 전부 n=64 진단 탐침이며 **게이트를 통과하지 못한 N=1e4 모델**로 얻었다.
341: 어떤 표에도 arm 으로 넣지 않는다. 확증은 게이트 통과 N=1.6e5 모델로 n≥2560 에서 1회 실행한다.
1080: 체크포인트 `ckpt/d2sx_N10000_a1.pt` 는 **게이트 실패**분이므로 §6d 와 같은 지위(체제 축 측정)다.
1348: 학습 arm 체크포인트는 게이트 실패분(§6d 지위). 짝지음 검정은 §6p 규칙대로 **네 SNR 전부**를 raw 에서
1456: N=1e4 만 보고 쓴 "Tp≥3" 은 과했다. 게이트 통과 표가 더 보수적이므로 그쪽 문장을 쓴다.
```

**제안 문구**

```text
[341행 뒤] > **정정 (2026-09-23, review_next G-1.2, 감사 목록 밖)**: 340행 "게이트를 통과하지 못한 N=1e4 모델" 과 341행 "게이트 통과 N=1.6e5 모델" 도 D2 체크포인트에 게이트 판정을 붙인 줄임말이다(313행 제목대로 이 D2 모델은 미게이트). 읽는 법 — 340: "D1 형제가 게이트에 실패한 예산의 N=1e4 D2 모델", 341: "D1 형제가 게이트를 통과한 레시피의 N=1.6e5 D2 모델".
[1080행 뒤] > **정정 (2026-09-23, review_next G-1.2, 감사 목록 밖)**: "게이트 실패분" 은 "D1 형제(N=1e4)가 게이트에 실패한 예산의 D2 학습본" 으로 읽는다(`tables_D2_B1e4x.txt:45` 게이트 행 없음, `samplecx_D1.txt:28` GC 0.24333 FAIL).
[1350행 뒤] > **정정 (2026-09-23, review_next G-1.2, 감사 목록 밖)**: 1348행 "게이트 실패분" 도 1080행 정정과 같이 읽는다(`tables_D2_B1e4lo.txt:45` 게이트 행 없음).
[1456행 뒤] > **정정 (2026-09-23, review_next G-1.2, 감사 목록 밖)**: "게이트 통과 표" 는 "D1 형제 게이트 PASS 예산(N=1.6e5)의 표(`B16e4`)" 로 읽는다. 1454행 "게이트 통과 예산" 은 예산을 가리키므로 그대로 둔다.
```

<details><summary>근거</summary>

HEAD 에서 grep '게이트 통과|게이트 실패|게이트를 통과하지 못한' 으로 확인했다. tables_D2_B1e4x.txt:45 와 tables_D2_B1e4lo.txt:45 는 각각 'NO GATE RECORD mentions d2sx_N10000_a1.pt -- UNVERIFIED here'이고, samplecx_D1.txt:28 은 GC 0.24333 FAIL 이다. 340 의 모델이 어느 D1 형제에 대응하는지 파일로 특정하지 못해(STATUS:301 은 HPO trial 386 의 D1 재게이트 GC 0.2241 FAIL 을 적는다) 340-341 노트에는 GC 수치를 넣지 않았다.

검증: 네 위치 모두 글자 그대로 일치한다. 313행 '미게이트 N=1e4 모델', tables_D2_B1e4x.txt:45, tables_D2_B1e4lo.txt:45(둘 다 d2sx_N10000_a1.pt에 게이트 행 없음), samplecx_D1.txt:28을 확인했다. 1454행을 예산 표현으로 보고 남긴 판단도 맞다. 같은 유형인 175행 '게이트 **미통과** N=1e4 모델'(표 172-185행, 2번 행)이 빠졌다(missing 참조).
</details>

### testbed-gate-17 · G-1.2 (감사 STATUS:1629 → HEAD 1630, 인접 1629 추가) — `conf/STATUS.md` 1629, 1630 (표 1627-1633, 노트는 1633행 뒤)

- 방식: **STATUS inline note** · ✅ 검증 통과

**원문 (HEAD)**

```text
1629: | **F12** 동작 범위 | N=1e4(게이트 실패) → **N=1.6e5 게이트 통과** `B16e4`. C5 가 동률이 되는 이유(앵커 판정점이 곡선 교차 뒤인 +6/+12/+15 에 놓임)를 캡션에 적었다. §6j 설명의 한계(격자 이탈은 충분조건 아님 — C2 −9 dB)도 그림 안 파란 메모로 반영 | `tables_D2_B16e4.txt`, `raw_B16e4` |
1630: | **F14** 헤드라인 | `B1e4`(게이트 실패) → **`B16e4k`** = 게이트 통과 + 동일예산 + **확장 K=1024 격자**. GMM 0.243 / V1 0.145. 게이트 문구가 실행 체크포인트를 따라가도록 고쳤고(이전엔 게이트 실패 문구가 붙어 있었다), (d) 패널이 다른 체크포인트의 진단임을 패널·캡션에 명시 | `tables_D2_B16e4k.txt`, `raw_B16e4k` |
```

**제안 문구**

```text
> **정정 (2026-09-23, review_next G-1.2)**: 1629·1630행의 "(게이트 실패)"·"게이트 통과" 는 D2 체크포인트가 아니라 D1 형제의 판정이다(D2 체크포인트 게이트 행 없음: `tables_D2_B1e4.txt:45`, `tables_D2_B16e4.txt:45`, `tables_D2_B16e4k.txt:45`. 형제: `samplecx_D1.txt:28` GC 0.24333 FAIL, `LADDER_C.md:1` PASS). 읽는 법 — 1629: "N=1e4(D1 형제 게이트 FAIL) → N=1.6e5(D1 형제 게이트 PASS) `B16e4`". 1630: "`B1e4`(D1 형제 게이트 FAIL) → `B16e4k` = D1 형제 게이트 PASS 레시피 + 동일예산 + 확장 K=1024 격자". 1633행 "게이트 통과 예산" 은 예산 표현이라 그대로 둔다. F12 캡션 제목의 같은 줄임말은 `code/figures_stagec2.py` 생성기 주석으로만 남긴다(그림 재생성 안 함).
```

<details><summary>근거</summary>

감사가 지목한 1629(4ad41df9)는 HEAD 1630 이다. HEAD 1629(F12 행)는 같은 표의 같은 줄임말이라 함께 다룬다. tables_D2_B16e4k.txt:45 'NO GATE RECORD mentions d2sx_N160000_a1.pt -- UNVERIFIED here'.

검증: 1629행과 1630행이 일치하고 표는 1627-1633행이다. tables_D2_B16e4k.txt:45도 확인했다. 1633행을 예산 표현으로 보고 남긴 판단이 맞다.
</details>

### testbed-gate-18 · G-1.2 (감사 STATUS:1664·1736 → HEAD 1665·1737) — `conf/STATUS.md` 1665 (문단 1665-1666, 노트는 1666행 뒤) / 1737 (문단 뒤에 표 1740-1747 이 이어지므로 노트는 1747행 뒤)

- 방식: **STATUS inline note** · ✅ 검증 통과

**원문 (HEAD)**

```text
1665: `raw_B16e4k` C2 −3 dB, n=2560, 게이트 통과 + 동일예산. 전부 **이미 있는 자료의 재분석**이며 새 실행 없음.
1737: C2 −3 dB, n=2560, 게이트 통과 + 동일예산(K=1024 격자, `raw_B16e4k`). 블록의 다양체 차원은 3L,
```

**제안 문구**

```text
[1666행 뒤] > **정정 (2026-09-23, review_next G-1.2)**: 1665행 "게이트 통과 + 동일예산" 은 "D1 형제 게이트 PASS 레시피 + 동일예산" 으로 읽는다(`raw_B16e4k` 의 학습 arm 체크포인트 `d2sx_N160000_a1.pt` 는 게이트 행 없음 `tables_D2_B16e4k.txt:45`. PASS 는 `LADDER_C.md:1` 의 `sx_N160000_D1.pt`).
[1747행 뒤] > **정정 (2026-09-23, review_next G-1.2)**: 1737행 "게이트 통과 + 동일예산" 도 1665행 정정과 같이 "D1 형제 게이트 PASS 레시피 + 동일예산" 으로 읽는다. 표 수치 불변.
```

<details><summary>근거</summary>

tables_D2_B16e4k.txt:45, LADDER_C.md:1. 1737 은 감사가 6ed0613..HEAD 구간에서 추가됐다고 적은 줄이다.

검증: 1665행과 1737행이 일치한다. 1737행 문단 뒤 표가 1740-1747행(L=3..8)이라 1747행 뒤 배치가 맞다.
</details>

### testbed-gate-19 · G-1.2 (감사 PAPER_MATERIALS:905·908 + 반박 검토가 놓친 911, 거울형 907) — `conf/PAPER_MATERIALS.md` 905, 907, 908, 911 (표 904-908 뒤 문단 910-911, 노트는 911행 뒤)

- 방식: **other** · ✅ 검증 통과

**원문 (HEAD)**

```text
905: | `F14_headline_C2_m3dB.*` | **헤드라인 지점, 최종.** run `B16e4k` = 게이트 통과 + 동일예산 + **확장 K=1024 격자**. C2 −3 dB: GMM 0.243 / V1 0.145 / V0 0.593 / genie 0.034. §6q 고정 메뉴 A1~A8. **(d) 패널만 다른 체크포인트(N=1e4 진단)** 이며 캡션·패널 안에 명시 | 게이트 통과 (형제) | **헤드라인 그림** |
907: | `F14b_C2_m6dB_max_absolute_gap.*` | 같은 메뉴, C2 −6 dB (N=1e4): **절대 감소 최대** 0.791→0.601. **사후 선택**, 캡션 첫 줄 명시 | 게이트 실패 (N=1e4) | 보조 |
908: | `F14c_C2_p6dB_max_ratio.*` | 같은 메뉴, C2 +6 dB (B16e4k): **비 최대** (게이트 통과 예산 1.7×, N=1e4 에서 3.2×). **사후 선택**, 명시 | 게이트 통과 | 보조 |
911: `F12`·`F14` 는 22:00 에 **실험 마감본**(F12 → 게이트 통과 `B16e4`, F14 → 확장 격자 `B16e4k`)으로 다시 그렸다. `F15` 는 그때 신규.
```

**제안 문구**

```text
> **정정 (2026-09-23, review_next G-1.2)**: §17.3 규칙(819-820: "게이트를 통과한 D2 모델" 이라고 쓰지 않고 "D1 에서 게이트를 통과한 레시피로 D2 에 학습한 체크포인트" 라고 쓴다)을 위 표가 스스로 어긴 곳이 있다. 읽는 법 — 905 설명: "run `B16e4k` = D1 형제 게이트 PASS 레시피 + 동일예산 + 확장 K=1024 격자"(게이트 열 "게이트 통과 (형제)" 는 이미 한정됨). 908 게이트 열: "D1 형제 게이트 PASS". 907 게이트 열: "D1 형제 게이트 FAIL (N=1e4)". 911: "F12 → D1 형제 게이트 PASS 예산 `B16e4`". 근거: D2 체크포인트 게이트 행 없음(`tables_D2_B16e4.txt:45`, `tables_D2_B16e4k.txt:45`, `tables_D2_B1e4.txt:45`), 형제 행 `LADDER_C.md:1` PASS(GB +0.27% / GC 0.0999 / GD 0.0718), `samplecx_D1.txt:28` GC 0.24333 FAIL. 904·908 괄호 안의 "게이트 통과 예산" 은 예산 표현이라 그대로 둔다. 그림 파일과 캡션은 재생성하지 않는다. 수치 불변.
```

<details><summary>근거</summary>

PAPER_MATERIALS.md:819-820(HEAD) 규칙 원문 '"게이트를 통과한 D2 모델" 이라고 쓰면 안 되고, **"D1 에서 게이트를 통과한 레시피로 D2 에 학습한 체크포인트"** 라고 쓴다'. 905/908 은 감사가 지목했고, 911 은 반박 검토가 추가로 찾았다. 904 는 반박 검토가 borderline 으로 분류했다. 907 거울형은 이 초안에서 추가했다. PAPER_MATERIALS 는 4ad41df9→cd241b7e 사이에 바뀌지 않아 줄 번호 이동이 없다.

검증: 905, 907, 908, 911행이 글자 그대로 일치한다. 819-820행 규칙 원문도 일치한다. 수치 확인: LADDER_C.md:1, samplecx_D1.txt:28, tables_D2_{B16e4,B16e4k,B1e4}.txt:45. 같은 표 906행 게이트 열 '캡션·푸터가 어느 패널이 게이트 실패분인지 명시'도 같은 줄임말(D1 형제 FAIL)이다(경계 사례). 이 노트에 한 구절을 더하면 완결된다. 같은 파일 690-692행('V0 는 실질 세 게이트를 통과한 체크포인트')은 빠졌다(missing 참조).
</details>

### testbed-gate-20 · G-1.2 (PAPER_MATERIALS:665, 반박 검토가 놓친 위치) — `conf/PAPER_MATERIALS.md` 665 (§15.3 표 663-668, 노트는 668행 뒤)

- 방식: **other** · ✅ 검증 통과

**원문 (HEAD)**

```text
| 1 | V0 는 게이트 통과에도 D2 에서 붕괴한다 | **맞음.** 세 셀 전부 파국적 (111:5310 / 107:5386 / 110:4321). C2 에서 BLER 0.593 으로 **고전 터보 0.537 보다 나쁘다** |
```

**제안 문구**

```text
> **정정 (2026-09-23, review_next G-1.2)**: 예측 1 의 "게이트 통과에도" 는 "D1 형제 게이트 PASS 레시피로 학습한 D2 체크포인트(`d2sx_N160000_a1.pt`)에서도" 로 읽는다. 등록 원문(`10_SPEC_stageC.md:385-386`, 예측 커밋 `9e0023c`)은 사전 등록 텍스트라 고치지 않는다. 채점(맞음)과 수치는 불변.
```

<details><summary>근거</summary>

PAPER_MATERIALS.md:661 '예측 커밋 `9e0023c` (실행 **전**)'. 10_SPEC_stageC.md:385 '네 게이트를 전부 통과한 N=1.6e5 체크포인트임에도'. D2 체크포인트 게이트 행이 없다는 근거는 tables_D2_C.txt:45.

검증: 665행이 일치한다. 661행 '예측 커밋 9e0023c'를 확인했고(git log: 'Stage C §6c — D2 확증 실행 전 예측 기록'), 10_SPEC_stageC.md:385-386이 §6c(372행) 예측 1이다. 인용이 정확하다.
</details>

### testbed-gate-21 · G-1.2 (10_SPEC_stageC:246·385·874, 반박 검토 지목 + 385 추가) — `conf/10_SPEC_stageC.md` 246 (목록 항목 246-248, 노트는 248행 뒤) / 385 (항목 385-387, 노트는 387행 뒤) / 874 (항목 873-874, 노트는 874행 뒤)

- 방식: **spec note (사용자 승인 필요)** · ✅ 검증 통과

**원문 (HEAD)**

```text
246: - 모델은 **게이트 통과 체크포인트만** 쓴다. 즉 N'=1.6e5 (GA/GB/GC/GD 전부 PASS, `LADDER_C.md`).
385: 1. **`M-ours-dscore-C-V0` 는 D2 에서 붕괴한다.** 네 게이트를 전부 통과한 N=1.6e5 체크포인트임에도
874:   arm 판정 아님)로 별도 표에 싣고 머리말에 명시한다. 게이트 통과 주장은 C2(Nr=8)에만 쓴다.
```

**제안 문구**

```text
[248행 뒤]   > **노트 (2026-09-23, review_next G-1.2) — 사용자 승인 필요.** "게이트 통과 체크포인트" 는 "D1 형제가 네 게이트를 전부 통과한 예산 N'=1.6e5 의 D2 체크포인트" 로 읽는다. `LADDER_C.md:1` 의 PASS 행은 `sx_N160000_D1.pt`(D1)의 것이고 D2 체크포인트에는 게이트 행이 없다(`results/tables_D2_C.txt:45`). 규칙 자체(126-129: 판정은 D1 게이트)는 불변.
[387행 뒤]    > **노트 (2026-09-23, review_next G-1.2) — 사용자 승인 필요.** 사전 등록 예측 원문이라 고치지 않는다. "네 게이트를 전부 통과한 N=1.6e5 체크포인트"·"D1 에서 멀쩡했던 바로 그 모델" 은 "D1 형제 `sx_N160000_D1.pt` 가 네 게이트를 통과한 레시피·예산으로 D2 에 학습한 체크포인트" 로 읽는다(두 모델은 레시피·예산·정지 규칙이 같고 testbed 만 다르다 — `STATUS.md:656-660`).
[874행 뒤]   > **노트 (2026-09-23, review_next G-1.2) — 사용자 승인 필요.** "게이트 통과 주장" 은 "D1 형제 게이트 PASS 주장" 으로 읽는다.
```

<details><summary>근거</summary>

반박 검토가 10_SPEC_stageC.md:246 과 :874 를 지목했다. :385 는 이 초안에서 grep 으로 추가했다. 규칙 원문은 10_SPEC_stageC.md:126-129('D1 게이트가 통과해야만 D2 재학습본이 … 자격을 얻는다', '판정은 오직 D1 게이트가 내린다'). 형제 연결은 STATUS.md:656-660(HEAD)이고, D2 게이트 행이 없다는 근거는 tables_D2_C.txt:45. 사전 등록 spec 이라 노트만 제안한다.

검증: 246, 385, 874행이 일치한다. 126-129행 규칙과 STATUS:656-660 형제 연결을 확인했다. 같은 파일의 같은 유형이 빠졌다. §6d 설계 표 451-455행 게이트 열은 d2sx_N10000 'FAIL (GC 0.243)', d2sx_N40000 'FAIL (GC 0.167)', d2sx_N160000 'PASS'다(453행은 NUMBERS_PACKAGE:418/:575가 이미 지목). 461-463행은 'N=1e4 와 N=4e4 의 학습 체크포인트는 게이트에 실패했다 … 게이트 실패를 명시한다', 548행은 'N=1e4·N=4e4 체크포인트는 게이트 실패분이므로'다(missing 참조).
</details>

### testbed-gate-22 · G-1.2 (figures_stagec2.py:246 F12 캡션 제목, 반박 검토 지목) — `conf/code/figures_stagec2.py` 246 (삼중따옴표 문자열 안이므로 주석은 245행 `return _save(fig, "F12_tp_envelope", """` 바로 앞에 삽입)

- 방식: **caption/generator note** · ✅ 검증 통과

**원문 (HEAD)**

```text
F12.  The pilot-budget operating envelope at equal training budget, GATE-PASSING checkpoint
```

**제안 문구**

```text
# NOTE (2026-09-23, review_next G-1.2): "GATE-PASSING checkpoint" in the caption title below is
    # shorthand.  The D2 checkpoint d2sx_N160000_a1.pt has no gate row (results/tables_D2_B16e4.txt:45);
    # it is qualified through its D1 sibling sx_N160000_D1.pt (GATE_LINE_PASS, printed in this caption).
    # figs/F12_tp_envelope.* are NOT regenerated for this; at the next regeneration the title should read
    # "checkpoint whose D1 sibling passes the gates".
```

<details><summary>근거</summary>

figures_stagec2.py:246(HEAD) 과 figs/F12_tp_envelope.txt:1 에 같은 제목이 있다. 같은 캡션 본문은 GATE_LINE_PASS(:61-63, 캡션 삽입 :293)로 'qualified through its D1 sibling sx_N160000_D1.pt, which PASSES GB 2.66e-3 / GC 0.0999 / GD 0.0718 (LADDER_C.md:1)' 을 싣는다. 주석만 넣으므로 출력은 불변이다. 감사 수정 방향 목록에는 없고 반박 검토가 지목한 위치라 적용 여부는 사용자가 판단한다. runner.py:185 등의 'no GATE-PASSING checkpoint' 는 D2 게이트 행이 없다는 사실과 맞아 대상이 아니다.

검증: 246행이 일치하고 245행이 `return _save(fig, "F12_tp_envelope", """`다. figs/F12_tp_envelope.txt:1도 같은 제목이다. GATE_LINE_PASS 값(GB 2.66e-3 / GC 0.0999 / GD 0.0718)이 맞고, 293행에서 삽입된다. 근거란의 줄 번호 하나가 틀렸다. GATE_LINE_PASS는 60-62행이다(초안은 ':61-63'). 제안 주석에는 줄 번호가 없어 영향이 없다. 같은 파일의 31행(모듈 docstring 'The gate-passing model's numbers live in results/tables_D2_C.txt')과 426행(F13 캡션 'F12 and F14 were re-drawn on the gate-passing N = 1.6e5 run', figs/F13_sign_vs_magnitude.txt:35)은 빠졌다.
</details>

### testbed-gate-23 · G-1.2 (DECISIONS) — `conf/DECISIONS.md` append (M-5.2a 행 다음)

- 방식: **DECISIONS append** · ✏️ 검증 수정 반영 (인용 OK · 수치 OK · 문구 X)

**원문 (HEAD)**

```text
(append-only — 대체할 원문 없음)
```

**제안 문구**

```text
`[2026-09-23 __:__ KST] 정정 — D2 체크포인트를 "게이트 통과/실패" 로 직접 부른 줄임말 (review_next G-1.2) | STATUS 175·340-341·815·826·829·875·876·1080·1257·1292·1304·1307·1316·1348·1456·1604·1617·1629·1630·1635·1665·1737 과 PAPER_MATERIALS 665·690·905·906·907·908·911 뒤에 인라인 정정 노트를 달았다. PAPER_MATERIALS:819-820 이 정한 형태("D1 에서 게이트를 통과한 레시피로 D2 에 학습한 체크포인트", 줄여 "D1 형제 게이트 PASS/FAIL")로 읽게 하는 노트다. 원문 행·수치·판정은 불변이다. 예산을 가리키는 "게이트 통과 예산"(STATUS 1113·1416·1454·1633, PAPER_MATERIALS 904·908 괄호 안)은 체크포인트 판정이 아니라 범위에서 뺐다. 10_SPEC_stageC:246·385·451-455·461-463·548·874 는 사용자 소유라 노트만 제안했다(385 는 사전 등록 예측 원문). 그림은 재생성하지 않고 생성기에 주석만 단다: figures_stagec2.py:246(F12 제목)·:426(F13 캡션)·:31(모듈 docstring), figures_stagec3.py:192-195(F15 그림 안 푸터), figures_stagec.py:515-516(F9 캡션). 이 파일 49행의 "게이트 미통과 N=1e4 체크포인트" 도 같은 줄임말이라 이 행이 대신 짚는다. 생성된 결과 파일(NUMBERS_PACKAGE P1/P13 사실 열, jacpsd_counterfactual_SUMMARY_n256.txt:6, settling_D2.txt:67)은 손대지 않는다 | 게이트는 D1 에서만 측정된다(10_SPEC_stageC:126-129). D2 체크포인트에는 게이트 행이 없다: tables_D2_{C,B16e4,B16e4k,B4e4,B1e4,B1e4x,B1e4lo}.txt:45 전부 "NO GATE RECORD mentions d2sx_N…_a1.pt -- UNVERIFIED here". 판정은 D1 형제 행에 있다. LADDER_C.md:1 sx_N160000_D1.pt PASS (GB +0.27% / GC 0.0999 / GD 0.0718). samplecx_D1.txt:28-30 GC 0.24333(N=1e4 FAIL) / 0.16651(4e4 FAIL) / 0.09986(1.6e5 PASS), 이름 규칙 run_samplecx.py:16 sx_N{N}_D1.pt. D1 PASS 를 D2 참-score 검증이라 쓴 행은 없고 면책(STATUS 390-392·654-660, 10_SPEC_stageC:175)도 있어 문구 수준 결함이다. STATUS:826(당시 825)과 10_SPEC_stageC:453 은 results/NUMBERS_PACKAGE_2026-09-22.md:418·:575 가 이미 같은 결함으로 지목했다. 감사의 STATUS 행 번호(825…1736)는 4ad41df9 기준이고, cd241b7e 의 머리말 1행 추가로 +1 이동했다. 감사 목록 밖 위치는 '게이트 통과|게이트를 통과한|게이트 \*\*통과|미통과|게이트 실패|게이트에 실패|gate-passing|FAILED the pre-registered' grep 으로 추가 확인했다 | 노트 행과 생성기 주석만 지우면 원상(원문을 고치지 않았다)`
```

<details><summary>검증 agent 지적 / 초안 원안</summary>

지적: 수치를 재도출했다. 모두 맞다. samplecx.csv GC 2.433337e-01 / 1.665124e-01 / 9.985910e-02, samplecx_D1.txt:28-30, LADDER_C.md:1, tables_D2_{C,B16e4,B16e4k,B4e4,B1e4,B1e4x,B1e4lo}.txt:45 모두 'NO GATE RECORD … UNVERIFIED here', run_samplecx.py:16이다. 예산 표현 분류(STATUS 1113·1416·1454·1633, PM 904·908 괄호)도 맞다. 문제는 '감사 목록 밖(…)은 같은 grep 으로 추가 확인했다'가 완결성을 뜻하는데 목록이 불완전하다는 점이다. 초안 grep은 '게이트를 통과한'과 굵은 글씨로 끊긴 형태를 못 잡았다. 빠진 곳: STATUS 175·815·1604·1617·1635, PM 690·906, 10_SPEC 451-455·461-463·548, figures_stagec2.py:31·:426(F13 캡션), figures_stagec3.py:192-195(F15 그림 안 푸터), figures_stagec.py:515-516(F9 캡션), 이 파일 49행 '게이트 미통과 N=1e4 체크포인트'. 이미 기록된 지목(NUMBERS_PACKAGE:418·:575, STATUS:825/10_SPEC:453)도 인용하지 않았다. 아래 교정문은 missing의 추가 노트들이 함께 적용된다는 전제다.

초안 원안:

```text
`[2026-09-23 __:__ KST] 정정 — D2 체크포인트를 "게이트 통과/실패" 로 직접 부른 줄임말 (review_next G-1.2) | STATUS 340-341·826·829·875·876·1080·1257·1292·1304·1307·1316·1348·1456·1629·1630·1665·1737 과 PAPER_MATERIALS 665·905·907·908·911 뒤에 인라인 정정 노트를 달았다. PAPER_MATERIALS:819-820 이 정한 형태("D1 에서 게이트를 통과한 레시피로 D2 에 학습한 체크포인트", 줄여 "D1 형제 게이트 PASS/FAIL")로 읽게 하는 노트다. 원문 행·수치·판정은 불변이다. 예산을 가리키는 "게이트 통과 예산"(STATUS 1113·1416·1454·1633, PAPER_MATERIALS 904·908 괄호 안)은 체크포인트 판정이 아니라 범위에서 뺐다. 10_SPEC_stageC:246·385·874 는 사용자 소유라 노트만 제안했다(385 는 사전 등록 예측 원문). figures_stagec2.py:246 캡션 제목은 생성기 주석만 달고 F12 는 재생성하지 않는다 | 게이트는 D1 에서만 측정된다(10_SPEC_stageC:126-129). D2 체크포인트에는 게이트 행이 없다: tables_D2_{C,B16e4,B16e4k,B4e4,B1e4,B1e4x,B1e4lo}.txt:45 전부 "NO GATE RECORD mentions d2sx_N…_a1.pt -- UNVERIFIED here". 판정은 D1 형제 행에 있다. LADDER_C.md:1 sx_N160000_D1.pt PASS (GB +0.27% / GC 0.0999 / GD 0.0718). samplecx_D1.txt:28-30 GC 0.24333(N=1e4 FAIL) / 0.16651(4e4 FAIL) / 0.09986(1.6e5 PASS), 이름 규칙 run_samplecx.py:16 sx_N{N}_D1.pt. D1 PASS 를 D2 참-score 검증이라 쓴 행은 없고 면책(STATUS 390-392·654-660, 10_SPEC_stageC:175)도 있어 문구 수준 결함이다. 감사의 STATUS 행 번호(825…1736)는 4ad41df9 기준이고, cd241b7e 의 머리말 1행 추가로 +1 이동했다. 감사 목록 밖(340-341, 875, 1080, 1304, 1307, 1348, 1456, 1629, PM 907, 10_SPEC 385)은 같은 grep 으로 추가 확인했다 | 노트 행만 지우면 원상(원문을 고치지 않았다)`
```
</details>

<details><summary>근거</summary>

위 G-1.2 항목들의 줄 번호는 전부 git show HEAD:<path> 사본에서 재확인했다(cd241b7e). 수치 출처: LADDER_C.md:1, samplecx_D1.txt:28-30(=samplecx.csv 행 10000/40000/160000: GC 2.433337e-01 / 1.665124e-01 / 9.985910e-02), tables_D2_*.txt:45.

검증: (위 참조)
</details>

### 1차 검증이 찾은 누락 위치 (→ 2차에서 초안 작성)

<details><summary>원문</summary>

줄 번호는 모두 HEAD cd241b7e 기준(git show HEAD:<path>)이다.

[R-5.2 / M-5.2a — '물리적으로 표준' 문구]
1. conf/DECISIONS.md:23 ([2026-09-20 12:35 KST] S2 섹터 행): 원문은 '… D2 선택 근거가 "물리적으로 표준"이므로 표준 120도 섹터가 맞는 읽기다. … 이것은 물리의 귀결이지 GMM 을 불리하게 만든 것이 아니며'다. 초안이 인용한 grep(physically standard|물리적으로 표준)이 바로 이 행을 돌려준다. append-only라 M-5.2a 정정 행이 짚어야 한다(교정문 반영). S2 선택 자체는 같은 행의 첫 근거(05_SPEC 물리각·'섹터 ±pi/3')로 남는다.
2. (경계, 선택) conf/10_SPEC_stageC.md:836-837 D3 저널 항목: 'D2 는 |α_l| 이 결정적이라 가우시안 혼합이 오설정되는 구조다 … α_l ~ CN(0,p_l) 로 한 줄만 바꾼 D3 에서 GMM 이 이기거나 비기는 것이 예상'. D3가 GMM을 제대로 지정한다는 함의가 있다. 그러나 D3도 각도가 연속이면 연속 혼합이다. correctly specified라고 명시하지는 않았으므로 노트는 선택이다.
docs/*.md, 그림 캡션, 결과 txt에는 'physically standard/물리적으로 표준/3GPP-style'이 더 없다.

[G-1.2 — D2 체크포인트를 게이트 통과/실패로 직접 부른 곳]
STATUS.md:
- 1604-1606 '## 헤드라인 문장의 최종 형태'(1602): '> **사전 등록 게이트를 통과한 학습 prior 가, 같은 1.6e5 채널 집합으로 적합하고 K 격자를 …'. 1304행의 최종판이자 원고 헤드라인이다. 파급이 가장 크다. 제안(1606행 뒤): '> **정정 (2026-09-23, review_next G-1.2)**: "사전 등록 게이트를 통과한 학습 prior 가" 는 "사전 등록 게이트를 D1 에서 통과한 레시피(D1 형제 `sx_N160000_D1.pt`, `LADDER_C.md:1`)로 D2 에 학습한 prior(`d2sx_N160000_a1.pt`, 게이트 행 없음 `tables_D2_B16e4k.txt:45`)가" 로 읽는다. 수치 불변.'
- 815: '따라서 이 결론은 게이트를 통과한 N=1.6e5 모델에도 그대로 적용된다.' → 'D1 형제가 게이트를 통과한 레시피의 N=1.6e5 D2 모델(`d2sx_N160000_a1.pt`, `tables_D2_C.txt:45` 게이트 행 없음)'.
- 175 (측정 요약 표 172-185, 2번 행): '게이트 **미통과** N=1e4 모델'. 340행과 같은 거울형이다. 노트는 185행 뒤.
- 1617: 'B16e4/B16e4k 게이트 통과 동일예산 표' → 'D1 형제 게이트 PASS 레시피 동일예산 표'. 노트는 1618행 뒤.
- 1635-1636: '게이트 **통과** 실행에도 "GC 0.243 FAILS" 문구가 붙었다' → 'D1 형제 게이트 PASS 레시피의 실행'.
PAPER_MATERIALS.md:
- 690-692 (§15.5 읽기 1): 'V0 는 실질 세 게이트를 통과한 체크포인트를 사전 등록 D-14 행렬 site 에 그대로 넣은 것'. d2sx_N160000_a1.pt(D2)를 가리킨다. → 'D1 형제가 실질 세 게이트를 통과한 레시피로 D2 에 학습한 체크포인트'.
- 906 게이트 열(경계): '어느 패널이 게이트 실패분인지' → 'D1 형제 게이트 FAIL 분'. 905/907/908/911 노트에 한 구절을 더하면 된다.
10_SPEC_stageC.md (사전 등록, 노트만):
- 451-455 §6d 설계 표 게이트 열: d2sx_N10000_a1.pt 'FAIL (GC 0.243)', d2sx_N40000_a1.pt 'FAIL (GC 0.167)', d2sx_N160000_a1.pt 'PASS'. 453행은 results/NUMBERS_PACKAGE_2026-09-22.md:418·:575가 이미 'as if measured on that file. It was not'으로 지목했다.
- 461-463: 'N=1e4 와 N=4e4 의 학습 체크포인트는 게이트에 실패했다 … 표 머리말에 게이트 실패를 명시한다'.
- 548: 'N=1e4·N=4e4 체크포인트는 게이트 실패분이므로'.
그림·캡션 (재생성하지 않고 생성기 주석만):
- code/figures_stagec3.py:192-194 F15 그림 안 푸터(png/pdf에 인쇄됨): '(b) rightmost point and (c) N=1.6e5 use the gate-passing d2sx_N160000_a1.' D2 체크포인트를 한정어 없이 gate-passing이라 부른다. :195 'gate-failing points'도 같은 유형이다. :240 → figs/F15_gap_robustness.txt:43 'use the gate-passing checkpoint:' 바로 뒤에 GATE_LINE_PASS 한정어가 붙으므로 경계 사례다.
- code/figures_stagec2.py:426 → figs/F13_sign_vs_magnitude.txt:35 'F12 and F14 were re-drawn on the gate-passing N = 1.6e5 run'.
- code/figures_stagec2.py:31 모듈 docstring 'The gate-passing model's numbers live in results/tables_D2_C.txt.'. docstring이라 직접 수정 가능하다.
- code/figures_stagec.py:515-516 → figs/F9_sigma_band_vs_snr.txt:31 'ckpt/d2sx_N10000_a1.pt, which FAILED the pre-registered gates (GC 0.224 …)'. 거울형이다. GC 0.224는 HPO trial 386의 D1 재게이트 값이다(NUMBERS_PACKAGE:403).
DECISIONS.md:
- 49 (경계, 거울형): '전부 게이트 미통과 N=1e4 체크포인트의 진단 탐침'. append-only라 G-1.2 정정 행이 짚는다(교정문 반영).
생성 결과 파일 (편집 대상 아님. 참고로만 기록):
- results/NUMBERS_PACKAGE_2026-09-22.md:3 'B16e4(게이트 통과 + 동일예산)'. :729 P1과 :751 P13의 사실 열 '게이트 통과 …'는 게이트 열이 '형제 PASS'로 한정하므로 PM 905와 같은 유형이다. :679 'diagnostic probe on a gate-FAILED checkpoint'.
- results/jacpsd_counterfactual_SUMMARY_n256.txt:6 'the N=1e4 checkpoint, which FAILED the pre-registered gate'. results/settling_D2.txt:67 'The checkpoint here FAILED the pre-registered gates'.
문제없는 용례(대상 아님): STATUS 427·439·447(D1 체크포인트), 10_SPEC 339-340·364(D1), PM 443·566(D1), figures_stagec.py:25/620(D1), tables_*:43 'no GATE-PASSING checkpoint'(사실과 일치).
</details>

---

## 1차 · 복잡도 4.6x·체크포인트 (P0-2b, cost/M1·M2, P0-1b, ckpt/M2)

### cost-ckpt-1 · P0-2b, cost/M2 — `conf/STATUS.md` 1221 뒤에 삽입 (1217 제목, 1219-1221, 1229 표 평균행, 1231 시행당 비용을 한 주석으로 다룸)

- 방식: **STATUS inline note** · ✏️ 검증 수정 반영 (인용 OK · 수치 OK · 문구 X)

**원문 (HEAD)**

```text
L1217: # ■ §6q A8 — Module H 1회 비용 (2026-09-22 14:30 KST) · **학습 prior 가 4.6배 비싸다**
L1219: `results/complexity_moduleH.txt` (정본). 사전 등록 §6q A8. CPU, float64, **1 스레드**(수신기와 동일),
L1220: 진입점은 양쪽 다 `prior.denoise_full(q, nu) -> (m, J)` 이며 외부 반복마다 **1회**, 시행당 16회 호출된다.
L1221: 루프의 나머지는 전 arm 공유이므로 이 한 번의 호출이 arm 간 복잡도 차이의 **전부**다.
L1229: | **평균** | **17.05 ms** | **78.75 ms** | **78.11 ms** | **4.6×** |
L1231: 시행당(16 반복): GMM **273 ms** 대 학습 **1260 ms**.
```

**제안 문구**

```text
> **정정 (2026-09-23, review_next P0-2b·cost/M2)**: 제목(1217)의 "학습 prior 가 4.6배 비싸다", 1219-1221, 표 평균행(1229), 시행당 비용(1231)은 **arm 간 수신기 비용비가 아니다.** ① 측정한 함수: 헤드라인 GMM arm `M-ours-bstar` 는 `denoise_full` 을 부르지 않는다. 이 arm 은 `gmm_site`(mode='colored', exact_prior=True; `arms.py:36,163`)라서 외부 반복마다 `GMMPriorB.ep_site(G, b, lam_min)` 를 부른다(`Demo/t2_route_a.py:373-374`). `raw_B16e4k` C2 −3 dB 64파일의 `M-ours-bstar|clip` 평균 0.798 은 ep_site 의 clip 카운터가 돌았다는 기록이다. 그러므로 1220 의 "진입점은 양쪽 다 `prior.denoise_full(q, nu) -> (m, J)`" 와 1221 의 "이 한 번의 호출이 arm 간 복잡도 차이의 **전부**다" 는 GMM 쪽에서 틀렸다. score 쪽(V0/V1)은 수신기가 실제로 부르는 함수를 쟀다. ② 측정 구성: GMM 은 kron **K=512**(N=1e4 적합), 학습 arm 은 `d2sx_N10000_a1.pt` 였다(`complexity_moduleH.txt:5-6`, `bench_moduleH.py:30-31`). 헤드라인 `raw_B16e4k` 448파일은 전부 kron_K=1024·ntrain=1.6e5·`d2sx_N160000_a1.pt` 이다. 두 ckpt 는 hp(dit w64 d6 h8 p1 emb256)가 같으므로, 구성 차이 가운데 비용에 걸리는 것은 GMM 의 K 다. ③ 재현성: 파일에는 평균만 있고, arm 을 ν 마다 연속된 블록으로 재서 부하 변동이 비에 그대로 들어간다(`bench_moduleH.py:39-44,75-87`). 같은 코드·시드·K·ckpt 로 다시 돌렸을 때 4.6× 가 재현되지 않았다(REVIEW_AUDIT cost/M2; 그 재측정은 저장되지 않아 수치로 인용하지 않는다). **대체 문장**: "A8(`complexity_moduleH.txt`)은 등방 `denoise_full` 마이크로벤치마크(GMM K=512, `d2sx_N10000_a1.pt`, 1 스레드, 평균만)이며 M-ours-bstar 수신기 경로(`ep_site`)의 비용이 아니다. 헤드라인 구성(K=1024, `d2sx_N160000_a1.pt`)의 실경로 Module H 비용비는 V1/b\* = Module H 호출당 1.35× (−3 dB) · 1.39× (+6 dB), 블록 전체 1.33× · 1.38× (헤드라인 구성 kron K=1024 + d2sx_N160000_a1, 실제 수신기 경로; `results/review_next/complexity_moduleH_ep.txt`)." A8 파일과 이 절은 기록으로 남긴다.
```

<details><summary>검증 agent 지적 / 초안 원안</summary>

지적: Quotes: all six lines (1217, 1219-1221, 1229, 1231) match HEAD verbatim. Numbers re-derived and all correct: complexity_moduleH.txt:2,5-6,16-18 (K=512, d2sx_N10000_a1.pt, 17.054/78.750/78.113 ms, 4.6x); bench_moduleH.py:30-31,39-44,75-87; arms.py:36,163; t2_route_a.py:277,373-374; the M-ours-bstar|clip[:,0] mean is 0.7976 over the 64 C2 -3 dB files (skip0 file 0.8109, bstar-scalar 0.0); all 448 raw_B16e4k files are ('kron',1024,160000,'d2sx_N160000_a1.pt'). Wording has two small faults. (a) The note puts two paraphrases in quotation marks ('진입점은 양쪽 다 denoise_full', '이 한 번의 호출이 차이의 전부'). Neither is verbatim, so the corrected text quotes 1220/1221 exactly. (b) ② lists the ckpt mismatch as if it bore on cost. REVIEW_AUDIT P0-2b 반박 (1) says it does not. I re-checked on CPU: both ckpts have the same hp (dit w64 d6 h8 p1 emb256) and 479,554 EMA elements. The corrected text adds one clause saying so, so the note does not imply a ckpt effect. The rest is sound. It does not claim the learned prior is cheaper, and it does not cite the unstored replay number.

초안 원안:

```text
> **정정 (2026-09-23, review_next P0-2b·cost/M2)**: 제목(1217)의 "학습 prior 가 4.6배 비싸다", 1219-1221, 표 평균행(1229), 시행당 비용(1231)은 **arm 간 수신기 비용비가 아니다.** ① 측정한 함수: 헤드라인 GMM arm `M-ours-bstar` 는 `denoise_full` 을 부르지 않는다. 이 arm 은 `gmm_site`(mode='colored', exact_prior=True; `arms.py:36,163`)라서 외부 반복마다 `GMMPriorB.ep_site(G, b, lam_min)` 를 부른다(`Demo/t2_route_a.py:373-374`). `raw_B16e4k` C2 −3 dB 64파일의 `M-ours-bstar|clip` 평균 0.798 은 ep_site 의 clip 카운터가 돌았다는 기록이다. 그러므로 "진입점은 양쪽 다 denoise_full" 과 "이 한 번의 호출이 차이의 전부" 는 GMM 쪽에서 틀렸다. score 쪽(V0/V1)은 수신기가 실제로 부르는 함수를 쟀다. ② 측정 구성: GMM 은 kron **K=512**(N=1e4 적합), 학습 arm 은 `d2sx_N10000_a1.pt` 였다(`complexity_moduleH.txt:5-6`, `bench_moduleH.py:30-31`). 헤드라인 `raw_B16e4k` 448파일은 전부 kron_K=1024·ntrain=1.6e5·`d2sx_N160000_a1.pt` 이다. ③ 재현성: 파일에는 평균만 있고, arm 을 ν 마다 연속된 블록으로 재서 부하 변동이 비에 그대로 들어간다(`bench_moduleH.py:39-44,75-87`). 같은 코드·시드·K·ckpt 로 다시 돌렸을 때 4.6× 가 재현되지 않았다(REVIEW_AUDIT cost/M2; 그 재측정은 저장되지 않아 수치로 인용하지 않는다). **대체 문장**: "A8(`complexity_moduleH.txt`)은 등방 `denoise_full` 마이크로벤치마크(GMM K=512, `d2sx_N10000_a1.pt`, 1 스레드, 평균만)이며 M-ours-bstar 수신기 경로(`ep_site`)의 비용이 아니다. 헤드라인 구성(K=1024, `d2sx_N160000_a1.pt`)의 실경로 Module H 비용비는 V1/b\* = Module H 호출당 1.35× (−3 dB) · 1.39× (+6 dB), 블록 전체 1.33× · 1.38× (헤드라인 구성 kron K=1024 + d2sx_N160000_a1, 실제 수신기 경로; `results/review_next/complexity_moduleH_ep.txt`)." A8 파일과 이 절은 기록으로 남긴다.
```
</details>

<details><summary>근거</summary>

git show HEAD:conf/results/complexity_moduleH.txt: L2 date 2026-09-22 14:29:53, L4 'entry point : prior.denoise_full', L5 'b* = kron (K = 512 components)', L6 'd2sx_N10000_a1.pt (479,426 parameters)', L16 GMM 17.054 / V0 78.750 / V1 78.113 ms, L17 4.6x, L18 per trial 272.9/1260.0/1249.8 ms. bench_moduleH.py:30-31 NTRAIN=10000, CKPT=d2sx_N10000_a1.pt; :77 times gmm.denoise_full. arms.py:36 gmm_site=mode 'colored', exact_prior=True; :163 M-ours-bstar=route_a(hp[bstar].view('eta'),...,'gmm_site'); Demo/t2_route_a.py:277 exact_prior requires hasattr(prior,'ep_site'); :373-374 'Lam, site_vec = self.prior.ep_site(G, b, self.lam_min)'. CPU re-read of raw npz (my script): all 448 raw_B16e4k files meta (bstar,kron_K,ntrain,stagec_ckpt)=('kron',1024,160000,'d2sx_N160000_a1.pt'); M-ours-bstar|clip[:,0] mean 0.7976 over the 64 C2 -3 dB files (0.8109 in the skip0 file, as the audit reports); M-ours-bstar-scalar 0.0. The replay non-reproduction is from REVIEW_AUDIT cost/M2 (not stored in the repo), so I cite it without its number.

검증: (위 참조)
</details>

### cost-ckpt-2 · P0-2b — `conf/STATUS.md` 1248 뒤에 삽입 (1242-1248 항목 2·3)

- 방식: **STATUS inline note** · ✏️ 검증 수정 반영 (인용 OK · 수치 OK · 문구 X)

**원문 (HEAD)**

```text
2. **GMM 비용은 K 에 비례하고 학습 비용은 그렇지 않다.** 지금 4.6× 는 b\*=K=512 기준이다.
   §6l 이 큰 예산에서 b\* 를 K=1024 로 옮기면 GMM 이 약 2배 느려져 비가 ~2.3× 로 줄어든다.
   **baseline 을 정당하게 강화하면 복잡도 격차가 자동으로 좁아진다** — 이것은 추측이 아니라
   K 스케일링에서 따라오지만, K=1024 의 실측 타이밍은 아직 없다.
3. **4.6× 는 학습 arm 의 상한이다.** 야코비안을 `torch.func.jacrev`(역방향, 64 real 차원 = 64 backward)
   로 계산했다. 순방향 모드나 배치 구현, 해석적 head 면 더 빠르다. 구현을 바꾸면 학습 쪽 숫자만
   바뀌고 GMM 쪽은 안 바뀐다. **그러므로 이 수는 "현재 구현" 의 수이지 방법의 하한이 아니다.**
```

**제안 문구**

```text
> **정정 (2026-09-23, review_next P0-2b)**: 항목 2 의 "~2.3×"(F14 캡션의 "nearer 2x" 도 같다)는 GMM `denoise_full` 비용을 K 로 외삽한 값이다. M-ours-bstar 가 실제로 부르는 함수는 `ep_site` 이므로 외삽한 함수가 틀렸고, K=1024 실측도 없었다(1245 가 적은 대로). 항목 3 의 "상한" 은 학습 쪽 구현을 더 빠르게 할 여지가 있다는 뜻으로만 성립한다. GMM 쪽을 다른 함수로 쟀으므로 4.6× 는 애초에 arm 간 비가 아니며, 실경로 비의 상한인지도 실측 전에는 말할 수 없다. 항목 1("V1 의 수리는 공짜다", −0.8%)은 score 쪽 같은 함수 안의 차이라 이 정정의 대상이 아니다(평균만 기록하고 블록 단위로 잰 점은 같다). **대체 문장**: "K 와 구현에 따른 비용비는 실경로 측정 V1/b\* = Module H 호출당 1.35× (−3 dB) · 1.39× (+6 dB), 블록 전체 1.33× · 1.38× (헤드라인 구성 kron K=1024 + d2sx_N160000_a1, 실제 수신기 경로; `results/review_next/complexity_moduleH_ep.txt`) 으로만 쓴다."
```

<details><summary>검증 agent 지적 / 초안 원안</summary>

지적: Quote: 1242-1248 match HEAD verbatim, including b\*. Numbers: no new numbers. The claim that the extrapolations scale denoise_full comes from REVIEW_AUDIT P0-2b 반박 (3), and STATUS:1245 does say K=1024 was not measured. The 'upper bound is open' phrasing is suitably conservative, because the only real-path ratios are the audit's unstored ad hoc runs. One small fault: the note quotes item 1 as "V1 수리 −0.8%", which does not appear in the file (the original reads 'V1 의 수리는 공짜다 ... −0.8%'). The corrected text quotes it verbatim.

초안 원안:

```text
> **정정 (2026-09-23, review_next P0-2b)**: 항목 2 의 "~2.3×"(F14 캡션의 "nearer 2x" 도 같다)는 GMM `denoise_full` 비용을 K 로 외삽한 값이다. M-ours-bstar 가 실제로 부르는 함수는 `ep_site` 이므로 외삽한 함수가 틀렸고, K=1024 실측도 없었다(1245 가 적은 대로). 항목 3 의 "상한" 은 학습 쪽 구현을 더 빠르게 할 여지가 있다는 뜻으로만 성립한다. GMM 쪽을 다른 함수로 쟀으므로 4.6× 는 애초에 arm 간 비가 아니며, 실경로 비의 상한인지도 실측 전에는 말할 수 없다. 항목 1 의 "V1 수리 −0.8%" 는 score 쪽 같은 함수 안의 차이라 이 정정의 대상이 아니다(부하에 민감한 것은 같다). **대체 문장**: "K 와 구현에 따른 비용비는 실경로 측정 V1/b\* = Module H 호출당 1.35× (−3 dB) · 1.39× (+6 dB), 블록 전체 1.33× · 1.38× (헤드라인 구성 kron K=1024 + d2sx_N160000_a1, 실제 수신기 경로; `results/review_next/complexity_moduleH_ep.txt`) 으로만 쓴다."
```
</details>

<details><summary>근거</summary>

REVIEW_AUDIT P0-2b 반박 검토 (3): 'Their K=1024 extrapolations (~2.3x at STATUS:1243, nearer 2x in the F14 caption) scale denoise_full, not ep_site.' Call path re-read at HEAD: arms.py:36,163 and Demo/t2_route_a.py:373-374 (M-ours-bstar -> ep_site). complexity_moduleH.txt:19 V1 minus V0 = -0.637 ms (-0.8%), with both timed through ScorePrior.denoise_full. The audit (P0-2a) confirms the score side times the function the receiver uses. STATUS:1245 itself says 'K=1024 의 실측 타이밍은 아직 없다'. The 1.1-1.4x and 2.65-3.14x real-path ratios in the audit are ad hoc and unstored, so I do not cite them. That is why the note says the upper-bound question is open rather than claiming a direction.

검증: (위 참조)
</details>

### cost-ckpt-3 · P0-2b, cost/M1 — `conf/STATUS.md` 1655 뒤에 삽입 (표 마지막 행이라 빈 줄 1개를 먼저 넣어 표를 끊는다)

- 방식: **STATUS inline note** · ✅ 검증 통과

**원문 (HEAD)**

```text
| 10 | A8 복잡도(4.6×)는 K=512 기준인데 헤드라인 GMM 은 K=1024 | 캡션에 캐비엇: K=1024 면 비는 2배 가까이 줄지만 **측정하지 않았다** |
```

**제안 문구**

```text
> **정정 (2026-09-23, review_next P0-2b·cost/M1)**: 10행의 캐비엇은 K 차이만 적고 **측정 함수 차이**(A8 은 GMM `denoise_full` 을 쟀고, 헤드라인 GMM arm 은 `ep_site` 를 부른다)를 빠뜨렸다. "K=1024 면 비는 2배 가까이 줄지만" 은 denoise_full 을 외삽한 것이다. 이 캐비엇은 `figure_f14.py:222-227` 에 조건 없이 하드코딩돼 F14b 에도 찍혔다. 그런데 F14b 는 `raw_B1e4lo`(C2 −6 dB 64파일 전부 kron_K=512·ntrain=1e4·`d2sx_N10000_a1.pt`)라서 "The GMM arm in THIS table is K=1024" 가 거짓이다. F14c(`raw_B16e4k`, K=1024)는 생성기를 마지막으로 고치기(23:07:59) 전에 쓰인 판(23:04:14)이라 캐비엇이 없다. 캡션은 재생성하지 않고, 세 캡션 파일 끝에 정정 주석을 단다.
```

<details><summary>근거</summary>

CPU re-read: all 64 raw_B1e4lo/D2_C2_*snr-6_* files give meta ('kron', 512, 10000.0, 'd2sx_N10000_a1.pt'), and all 512 raw_B1e4lo files have stagec_ckpt d2sx_N10000_a1.pt. All 448 raw_B16e4k files have kron_K=1024. figure_f14.py:225 hardcodes 'The GMM arm in THIS table is K=1024' with no condition. F14b_C2_m6dB_max_absolute_gap.txt:3 'raw raw_B1e4lo' and :26 carries that sentence. F14c_C2_p12dB_max_ratio.txt:23-25 has no caveat. stat mtimes: F14c 2026-09-22 23:04:14, figure_f14.py 23:07:59, F14 23:08:01, F14b 23:08:03. The working tree matches HEAD for these files (git diff --quiet); commit fd641739.

검증: Quote: line 1655 is verbatim; it is the last table row, and 1656 is blank. Numbers re-derived: all 64 raw_B1e4lo C2 -6 dB files are ('kron',512,10000.0,'d2sx_N10000_a1.pt'); figure_f14.py:225 hardcodes the K=1024 sentence with no condition; F14c mtime is 2026-09-22 23:04:14 and figure_f14.py 23:07:59; the working tree matches HEAD; the last commit touching both is fd641739. Wording: none.
</details>

### cost-ckpt-4 · P0-2b, cost/M2 — `conf/results/NUMBERS_PACKAGE_2026-09-22.md` 742 뒤에 삽입 (P12 가 표 마지막 행이라 빈 줄 1개 먼저)

- 방식: **other** · ✅ 검증 통과

**원문 (HEAD)**

```text
| P12 | A8 복잡도 | Module H 1회: GMM K=512 17.1 ms, 학습 78.8 ms (4.6×); PSD 투영 −0.8% (공짜) | 40/ν | CPU 1스레드 float64 | — | 추론만 | — | `complexity_moduleH.txt` |
```

**제안 문구**

```text
> **정정 (2026-09-23, review_next P0-2b·cost/M2)**: P12 는 **등방 `denoise_full` 마이크로벤치마크**(GMM kron K=512 = N=1e4 적합, 학습 arm `d2sx_N10000_a1.pt`, 1 스레드, ν 당 40회 평균만)의 수이지 arm 간 수신기 비용비가 아니다. 헤드라인 GMM arm `M-ours-bstar` 는 Module H 로 `GMMPriorB.ep_site` 를 부르는데(`arms.py:36,163`, `Demo/t2_route_a.py:373-374`) 이 벤치는 그 함수를 재지 않았다. 헤드라인 표(P13, `raw_B16e4k`)는 K=1024·N=1.6e5 이다. 같은 코드로 다시 돌렸을 때 4.6× 는 재현되지 않았다(REVIEW_AUDIT cost/M2, 저장 안 됨). **인용할 때**: "P12 = A8 마이크로벤치마크(K=512, denoise_full). 실경로 비용비는 V1/b\* = Module H 호출당 1.35× (−3 dB) · 1.39× (+6 dB), 블록 전체 1.33× · 1.38× (헤드라인 구성 kron K=1024 + d2sx_N160000_a1, 실제 수신기 경로; `results/review_next/complexity_moduleH_ep.txt`)." 원래 행은 기록으로 둔다.
```

<details><summary>근거</summary>

Same sources as the STATUS 1221 note: complexity_moduleH.txt:5-6,8,16-17 (K=512, d2sx_N10000_a1.pt, 40 reps, means 17.054/78.750 ms, 4.6x). arms.py:36,163 and t2_route_a.py:373-374. raw_B16e4k meta kron_K=1024, ntrain=160000 in all 448 files (CPU re-read). NUMBERS_PACKAGE:751 P13 is the K=1024 headline from raw_B16e4k.

검증: Quote: line 742 is verbatim, 743 is blank, and P13 is at 751. Numbers: K=512, d2sx_N10000_a1.pt, 40 reps, 17.1/78.8 ms and 4.6x all match complexity_moduleH.txt. raw_B16e4k is K=1024 and ntrain=160000 in 448/448 files. Wording: none.
</details>

### cost-ckpt-5 · P0-2b — `docs/EXPERIMENTS.md` 21 뒤 (파일 끝, 표 다음 빈 줄 후) — 이 파일의 두 정정 중 첫째

- 방식: **other** · ✅ 검증 통과

**원문 (HEAD)**

```text
A8 복잡도 학습 4.6× GMM(K=512).
```

**제안 문구**

```text
> 정정 (2026-09-23, review_next P0-2b): 21행 메모의 "A8 복잡도 학습 4.6× GMM(K=512)" 는 등방 `denoise_full` 마이크로벤치마크(K=512 GMM, `d2sx_N10000_a1.pt`, `conf/results/complexity_moduleH.txt`)의 수이지, 헤드라인(B16e4k: K=1024, `d2sx_N160000_a1.pt`) arm 간 수신기 비용비가 아니다. M-ours-bstar 는 `ep_site` 를 부르는데 벤치는 그 함수를 재지 않았다. 실경로 비용: V1/b\* = Module H 호출당 1.35× (−3 dB) · 1.39× (+6 dB), 블록 전체 1.33× · 1.38× (헤드라인 구성 kron K=1024 + d2sx_N160000_a1, 실제 수신기 경로; `results/review_next/complexity_moduleH_ep.txt`). 원래 행은 고치지 않는다.
```

<details><summary>근거</summary>

docs/EXPERIMENTS.md at HEAD has 21 lines, and line 21 is the last table row, containing the quoted fragment. Numbers and paths are the same as the STATUS 1221 note (complexity_moduleH.txt:5-6; raw_B16e4k meta re-read on CPU).

검증: Quote: the fragment 'A8 복잡도 학습 4.6× GMM(K=512).' is in line 21, the last line of a 21-line file. Numbers are consistent with complexity_moduleH.txt:5-6 and the raw_B16e4k meta. Wording: none.
</details>

### cost-ckpt-6 · P0-2b — `conf/figs/F14_headline_C2_m3dB.txt` 30 뒤 (파일 끝에 추가). 원문 23-28 은 그대로

- 방식: **caption/generator note** · ✅ 검증 통과

**원문 (HEAD)**

```text
A8, Module H cost per call (results/complexity_moduleH.txt, CPU float64 one thread): fitted GMM b*
K=512 17.1 ms, learned score 78.8 ms (4.6x; the PSD projection itself is -0.8%, i.e. free); the
equal-budget claim is 'same training data', not 'same inference complexity'.  CAVEAT: that benchmark
was run against K=512.  The GMM arm in THIS table is K=1024, whose mixture-EP site costs roughly twice
as much, so the ratio here is nearer 2x -- but that was not measured, and the measured number is the
K=512 one.
```

**제안 문구**

```text
CORRECTION (2026-09-23, review_next P0-2b): the A8 lines above report an isotropic denoise_full microbenchmark (fitted GMM kron K=512 from the N=1e4 fit, learned arm ckpt/d2sx_N10000_a1.pt; results/complexity_moduleH.txt, means only). They are not the receiver cost ratio of the arms in this table. M-ours-bstar calls GMMPriorB.ep_site once per outer iteration (arms.py:36,163; Demo/t2_route_a.py:373-374), and that benchmark did not time it. This table's GMM is K=1024 (raw_B16e4k meta kron_K=1024, all 448 files). 'Mixture-EP site costs roughly twice ... nearer 2x' was an extrapolation of denoise_full, not a measurement of ep_site. Real-path Module H cost at this configuration: V1/b\* = Module H 호출당 1.35× (−3 dB) · 1.39× (+6 dB), 블록 전체 1.33× · 1.38× (헤드라인 구성 kron K=1024 + d2sx_N160000_a1, 실제 수신기 경로; `results/review_next/complexity_moduleH_ep.txt`). This caption was not regenerated.
```

<details><summary>근거</summary>

The caption files are in English, so the note is in English to match the file. F14_headline_C2_m3dB.txt at HEAD has 30 lines; line 3 names raw raw_B16e4k; lines 23-28 are quoted above. CPU re-read: all 448 raw_B16e4k files have kron_K=1024, ntrain=160000, stagec_ckpt d2sx_N160000_a1.pt. complexity_moduleH.txt:5-6 (K=512, d2sx_N10000_a1.pt). ep_site call path: arms.py:36,163 and t2_route_a.py:373-374.

검증: Quote: lines 23-28 are verbatim; the file has 30 lines, and line 3 says 'raw raw_B16e4k'. Numbers: K=512 and d2sx_N10000_a1.pt (complexity_moduleH.txt:5-6); raw_B16e4k is kron_K=1024 in 448/448 files; the ep_site call path is confirmed. Wording: none. The Korean placeholder inside the English caption is acceptable as a fill-in marker.
</details>

### cost-ckpt-7 · cost/M1, P0-2b — `conf/figs/F14b_C2_m6dB_max_absolute_gap.txt` 30 뒤 (파일 끝에 추가). 원문 23-28 은 그대로

- 방식: **caption/generator note** · ✅ 검증 통과

**원문 (HEAD)**

```text
was run against K=512.  The GMM arm in THIS table is K=1024, whose mixture-EP site costs roughly twice
as much, so the ratio here is nearer 2x -- but that was not measured, and the measured number is the
K=512 one.
```

**제안 문구**

```text
CORRECTION (2026-09-23, review_next cost/M1, P0-2b): 'The GMM arm in THIS table is K=1024 ... nearer 2x' is false for this figure. In raw_B1e4lo, all 64 C2 -6 dB files have bstar=kron, kron_K=512, ntrain=1e4 and stagec_ckpt=d2sx_N10000_a1.pt, which are the same K and checkpoint as the A8 benchmark. The sentence was hardcoded in code/figure_f14.py:222-227 and printed for every raw set. What does apply here is the function mismatch: A8 timed GMMPriorB.denoise_full, but M-ours-bstar calls ep_site (arms.py:36,163; Demo/t2_route_a.py:373-374). So 4.6x is not this table's arm-to-arm receiver cost ratio either. No real-path measurement exists at K=512 / N=1e4 (the planned real-path benchmark, conf/code/bench_moduleH_ep.py, is set up for the B16e4k configuration only). This caption was not regenerated.
```

<details><summary>근거</summary>

CPU re-read of all 64 raw_B1e4lo/D2_C2_S2_Nr8_T16_Tp4_dft_snr-6_*.npz files gives {('kron', 512, 10000.0, 'd2sx_N10000_a1.pt')}. V1 1538/2560=0.6008 and bstar 2026/2560=0.7914 match the caption's 0.601/0.791. F14b line 3 'raw raw_B1e4lo'. figure_f14.py:225 hardcodes the K=1024 sentence. bench_moduleH_ep.py (untracked, not at HEAD) line 40: TAG='B16e4k', NTRAIN=160000, and there is no tag argument.

검증: Quote: lines 26-28 are verbatim. Numbers re-derived: all 64 raw_B1e4lo C2 -6 dB files are kron/512/1e4/d2sx_N10000_a1.pt. V1 is 1538/2560 = 0.6008 and bstar 2026/2560 = 0.7914, matching caption line 2 (0.791 -> 0.601). bench_moduleH_ep.py (untracked) line 40 hardcodes TAG='B16e4k', NTRAIN=160000, with no tag argument. Wording: none. The note refers to an untracked script. That is fine if the script is committed with the P0 fixes; otherwise drop the parenthetical.
</details>

### cost-ckpt-8 · cost/M1, P0-2b — `conf/figs/F14c_C2_p12dB_max_ratio.txt` 27 뒤 (파일 끝에 추가). 원문 23-25 는 그대로

- 방식: **caption/generator note** · ✅ 검증 통과

**원문 (HEAD)**

```text
A8, Module H cost per call (results/complexity_moduleH.txt, CPU float64 one thread): fitted GMM b*
K=512 17.1 ms, learned score 78.8 ms (4.6x; the PSD projection itself is -0.8%, i.e. free); the
equal-budget claim is 'same training data', not 'same inference complexity'.
```

**제안 문구**

```text
CORRECTION (2026-09-23, review_next cost/M1, P0-2b): this caption quotes A8 (4.6x) without the K caveat that the committed generator prints. Its file was written at 23:04:14, before the last edit of code/figure_f14.py at 23:07:59 (both are in commit fd641739). This table is raw_B16e4k (kron_K=1024, N=1.6e5, ckpt d2sx_N160000_a1.pt; all 448 files). A8 instead used K=512 and d2sx_N10000_a1.pt, and it timed GMMPriorB.denoise_full, whereas M-ours-bstar calls ep_site (arms.py:36,163; Demo/t2_route_a.py:373-374). So 4.6x is not this table's arm-to-arm receiver cost ratio. Real-path cost at this configuration: V1/b\* = Module H 호출당 1.35× (−3 dB) · 1.39× (+6 dB), 블록 전체 1.33× · 1.38× (헤드라인 구성 kron K=1024 + d2sx_N160000_a1, 실제 수신기 경로; `results/review_next/complexity_moduleH_ep.txt`). This caption was not regenerated.
```

<details><summary>근거</summary>

F14c at HEAD has 27 lines, and line 3 names raw raw_B16e4k. Line 2 itself says 'N=1.6e5 with K=1024'. File mtimes from stat: F14c 2026-09-22 23:04:14.53, figure_f14.py 23:07:59.67. git log for both paths shows fd641739 as the latest commit. The raw_B16e4k meta was re-read on CPU (448/448 kron_K=1024).

검증: Quote: lines 23-25 are verbatim; the file has 27 lines. Numbers: mtimes 23:04:14 (F14c) and 23:07:59 (figure_f14.py); commit fd641739; raw_B16e4k 448/448 K=1024 and d2sx_N160000_a1.pt. Wording: none.
</details>

### cost-ckpt-9 · cost/M1 — `conf/code/figure_f14.py` 13-15 (docstring)

- 방식: **docstring edit** · ✏️ 검증 수정 반영 (인용 OK · 수치 OK · 문구 X)

**원문 (HEAD)**

```text
A4 (guard) and A8 (Module H cost) are printed in the caption from results/guard_D2_<tag>.txt and
  results/complexity_moduleH.txt.
Every number is read from files; nothing is recomputed, resampled or re-run.  The headline-selection
```

**제안 문구**

```text
A4 (guard) is printed in the caption from results/guard_D2_<tag>.txt.  A8 (Module H cost) is NOT read
  from results/complexity_moduleH.txt: its text is hardcoded in the caption below and printed for every raw
  set (review_next cost/M1, 2026-09-23 -- the hardcoded 'THIS table is K=1024' caveat is false for raw_B1e4lo, K=512).
BLER, NMSE and guard numbers are read from files; the A8 text, the §6p ratios in the default first line and
the SCOPE/gate sentences are fixed text.  Nothing is recomputed, resampled or re-run.  The headline-selection
```

<details><summary>검증 agent 지적 / 초안 원안</summary>

지적: Quote: lines 13-15 at HEAD are verbatim. The replacement brings in a new false claim: 'Every number except the A8 text is read from files'. Other numbers in the generator are also fixed text: the default first line (lines 199-201) hardcodes the §6p ratios 1.32 / 1.14 / 1.74; SCOPE (line 228) hardcodes 'within 0.005 BLER'; the gate sentences come from constants GATE_LINE / GATE_LINE_PASS (figures_stagec2.py:58-62: GC 0.243, GB 2.66e-3 / GC 0.0999 / GD 0.0718). So the docstring would still overclaim. Corrected: say which numbers come from files (BLER, NMSE, guard) and name the fixed-text pieces.

초안 원안:

```text
A4 (guard) is printed in the caption from results/guard_D2_<tag>.txt.  A8 (Module H cost) is NOT read
  from a file: its text is hardcoded in the caption below and printed for every raw set (review_next
  cost/M1, 2026-09-23 -- the hardcoded 'THIS table is K=1024' caveat is false for raw_B1e4lo, K=512).
Every number except the A8 text is read from files; nothing is recomputed, resampled or re-run.  The headline-selection
```
</details>

<details><summary>근거</summary>

figure_f14.py:222-227 at HEAD: the A8 numbers (17.1 ms, 78.8 ms, 4.6x, -0.8%) and the K=1024 caveat are literal text inside the f-string that starts at line 202. No file read of complexity_moduleH.txt exists in the generator; the only occurrence of that name is in docstring line 14 and in caption text line 222. This is a docstring-only change, so behaviour does not change. If the generator note below is applied, drop the parenthetical from line 15.

검증: (위 참조)
</details>

### cost-ckpt-10 · cost/M1, P0-2b — `conf/code/figure_f14.py` 222 ("\nA8, Module H cost per call" 부터) ~ 227 끝까지 교체. 202 에서 시작하는 f-string 안쪽

- 방식: **caption/generator note** · ✅ 검증 통과

**원문 (HEAD)**

```text
...not what this checkpoint answers.\nA8, Module H cost per call (results/complexity_moduleH.txt, CPU float64 one thread): fitted GMM b*
K=512 17.1 ms, learned score 78.8 ms (4.6x; the PSD projection itself is -0.8%, i.e. free); the
equal-budget claim is 'same training data', not 'same inference complexity'.  CAVEAT: that benchmark
was run against K=512.  The GMM arm in THIS table is K=1024, whose mixture-EP site costs roughly twice
as much, so the ratio here is nearer 2x -- but that was not measured, and the measured number is the
K=512 one.
```

**제안 문구**

```text
...not what this checkpoint answers.\nA8, Module H cost per call (results/complexity_moduleH.txt, CPU float64 one thread, means only): an
isotropic denoise_full microbenchmark -- fitted GMM b* kron K=512 (N=1e4 fit) 17.1 ms, learned score
ckpt/d2sx_N10000_a1.pt 78.8 ms (4.6x; the PSD projection itself is -0.8%, i.e. free).  It is NOT the
receiver cost ratio of the arms: M-ours-bstar calls GMMPriorB.ep_site, which that benchmark did not time.
Real-path Module H cost (K=1024, ckpt/d2sx_N160000_a1.pt): V1/b\* = Module H 호출당 1.35× (−3 dB) · 1.39× (+6 dB), 블록 전체 1.33× · 1.38× (헤드라인 구성 kron K=1024 + d2sx_N160000_a1, 실제 수신기 경로; `results/review_next/complexity_moduleH_ep.txt`).  The
equal-budget claim is 'same training data', not 'same inference complexity'.

(적용 조건: complexity_moduleH_ep.txt 가 생긴 뒤 플레이스홀더를 그 파일의 수치로 채워서 적용한다. 이 문구는 어느 raw 세트에서도 참이 되도록 '이 표의 K' 를 주장하지 않는다. 기존 F14/F14b/F14c 캡션은 재생성하지 않고, 각 파일 끝의 정정 주석으로 대신한다. 적용하면 다음 생성부터 캡션 문구만 바뀌고 수치 계산은 바뀌지 않는다.)
```

<details><summary>근거</summary>

REVIEW_AUDIT cost/M1 수정 방향 asks for a figure_f14.py change and says to add the P0-2b wrong-function note. The user asked for record only, so I propose a text-only replacement (no conditional logic) and no regeneration. Facts: complexity_moduleH.txt:5-6,16-19 (K=512, d2sx_N10000_a1.pt, 17.054/78.750 ms, -0.8%); arms.py:36,163 and t2_route_a.py:373-374 (ep_site); all 448 raw_B16e4k files have K=1024.

검증: Quote: line 222 from '\nA8, ...' through line 227 matches HEAD; the \n are literal escape sequences inside the f-string that starts at line 202. Numbers: 17.1 / 78.8 ms, 4.6x and -0.8% are the rounded complexity_moduleH.txt:16-19 values. Wording: the new text makes no claim about 'this table's K', so it is true for every raw set, and it is conditional on the real-path file. It changes generator output (caption text only). That is acceptable because it is proposed only and conditional, as cost/M1 asks. If it is applied, drop the parenthetical from the docstring (entry above).
</details>

### cost-ckpt-11 · cost/M2, P0-2b — `conf/results/complexity_moduleH.txt` 31 뒤 (파일 끝에 추가). 1-31 은 그대로

- 방식: **other** · ✅ 검증 통과

**원문 (HEAD)**

```text
- The GMM cost scales with K; the learned cost does not.  At b* = K above, that is the
    comparison the BLER tables actually used.
```

**제안 문구**

```text
CORRECTION NOTE (2026-09-23, review_next P0-2a/P0-2b/cost-M2) -- this file is kept unchanged as the historical A8 record.
  - The GMM number times GMMPriorB.denoise_full.  The headline GMM arm M-ours-bstar never calls it: once per
    outer iteration it calls GMMPriorB.ep_site(G, b, lam_min) (arms.py:36,163; Demo/t2_route_a.py:373-374).
    'that is the comparison the BLER tables actually used' (lines 28-29) is therefore wrong for the GMM side.
  - K=512 and ckpt d2sx_N10000_a1.pt are the N=1e4 configuration.  The headline table (raw_B16e4k) is K=1024,
    N=1.6e5, ckpt d2sx_N160000_a1.pt.
  - Only means are recorded, and the arms are timed in consecutive blocks per nu (bench_moduleH.py:39-44,75-87),
    so load drift on the shared host enters the ratio directly.  A same-code replay did not reproduce 4.6x
    (REVIEW_AUDIT cost/M2; that replay was not stored).
  - Real-path cost: results/review_next/complexity_moduleH_ep.txt  V1/b\* = Module H 호출당 1.35× (−3 dB) · 1.39× (+6 dB), 블록 전체 1.33× · 1.38× (헤드라인 구성 kron K=1024 + d2sx_N160000_a1, 실제 수신기 경로; `results/review_next/complexity_moduleH_ep.txt`)
```

<details><summary>근거</summary>

REVIEW_AUDIT cost/M2 수정 방향: 'Leave complexity_moduleH.txt as the historical record, annotated as load-sensitive.' The file has 31 lines at HEAD, and lines 28-29 are quoted above. bench_moduleH.py:39-44 timed() times one arm over its whole q_list; :75-79 run GMM, V0, V1 as consecutive blocks per nu; :85-87 write means only. The output path results/review_next/complexity_moduleH_ep.txt comes from bench_moduleH_ep.py:162 (untracked, not yet run: results/review_next/ has no such file).

검증: Quote: lines 28-29 are verbatim; the file has 31 lines at HEAD. Numbers and lines: bench_moduleH.py:39-44 (timed) and :75-87 (per-nu consecutive blocks, means only) confirmed; bench_moduleH_ep.py:43,162 writes results/review_next/complexity_moduleH_ep.txt, and that file does not exist yet. Wording: none. The annotation follows the audit's instruction to leave the file as the historical record, annotated as load-sensitive.
</details>

### cost-ckpt-12 · P0-2b, cost/M1, cost/M2 — `conf/DECISIONS.md` 104 뒤 append (빈 줄 후 106행 예정) — 이번 네 append 중 첫째

- 방식: **DECISIONS append** · ✏️ 검증 수정 반영 (인용 OK · 수치 OK · 문구 X)

**원문 (HEAD)**

```text
(DECISIONS:102 의 일부) … F13 예산 주석, A8 의 K=1024 캐비엇 | **교훈: 그림 생성기가 결과 파일을 재계산하면 등록된 정의에서 벗어난다. 가능하면 결과 파일을 읽어라** — A4 를 그렇게 바꿨다`
```

**제안 문구**

```text
`[2026-09-23 __:__ KST] 정정 — §6q A8 "학습 prior 4.6배" 는 arm 간 수신기 비용비가 아니다 (review_next P0-2b·cost/M1·cost/M2) | A8 파일과 해당 절은 기록으로 두고, 각 위치에 정정 주석만 단다: STATUS 1221·1248·1655 뒤, NUMBERS_PACKAGE 742 뒤, EXPERIMENTS 21 뒤, 캡션 세 파일 끝, complexity_moduleH.txt 끝. 코드는 docstring 만 고친다(figure_f14.py 13-15, bench_moduleH.py 3-5·12). 대체 문장: "A8 은 등방 denoise_full 마이크로벤치마크(K=512, N=1e4 ckpt)이며 수신기 경로가 아니다. 헤드라인 구성(K=1024, d2sx_N160000_a1.pt)의 실경로 Module H 비용비는 V1/b\* = Module H 호출당 1.35× (−3 dB) · 1.39× (+6 dB), 블록 전체 1.33× · 1.38× (헤드라인 구성 kron K=1024 + d2sx_N160000_a1, 실제 수신기 경로; `results/review_next/complexity_moduleH_ep.txt`)." 그림과 표는 재생성하지 않는다 | A8(`complexity_moduleH.txt`, 09-22 14:29)은 양쪽 prior 를 `prior.denoise_full(q, nu)` 로 잰 등방 마이크로벤치마크이고, GMM 은 kron **K=512**(N=1e4 적합), 학습 arm 은 `d2sx_N10000_a1.pt` 였다(헤드라인 `d2sx_N160000_a1.pt` 와 hp 가 같아, 구성 차이 가운데 비용에 걸리는 것은 K 다). 헤드라인 GMM arm `M-ours-bstar` 는 denoise_full 을 부르지 않고 외부 반복마다 `GMMPriorB.ep_site(G,b,lam_min)` 를 부른다(`arms.py:36,163`, `Demo/t2_route_a.py:373-374`; `raw_B16e4k` C2 −3 dB 에서 `M-ours-bstar|clip` 평균 0.798). 헤드라인 `raw_B16e4k` 448파일은 kron_K=1024·N=1.6e5·`d2sx_N160000_a1.pt` 다. 그런데 STATUS §6q A8(1217-1248)·1655, NUMBERS_PACKAGE P12, EXPERIMENTS 21행, F14/F14b/F14c 캡션이 4.6× 를 arm 간 비용비로 인용했고, "K=1024 면 ~2.3×/nearer 2x" 는 denoise_full 외삽이었다. 22:30 항목에서 넣은 "A8 의 K=1024 캐비엇" 은 K 만 다루고 함수 차이를 빠뜨렸으며, `figure_f14.py:222-227` 에 하드코딩돼 F14b 에서는 거짓이 됐다(`raw_B1e4lo` C2 −6 dB 64파일 전부 K=512·N=1e4). F14c 는 생성기를 고치기 전의 판(23:04:14 < 23:07:59)이라 K 캐비엇이 없다. 같은 코드로 다시 돌렸을 때 4.6× 가 재현되지 않았다(감사 cost/M2, 미저장이라 수치는 인용하지 않음) | 추가한 정정 주석 줄을 지우고 두 docstring 을 이전 문구로 되돌리면 원상태다. 기록 문서의 원문은 바뀌지 않았다`
```

<details><summary>검증 agent 지적 / 초안 원안</summary>

지적: Quote: the DECISIONS:102 fragment is verbatim, and line 102 is the [2026-09-22 22:30] entry. The file has 104 lines, and line 26 is the 정정 pattern. Numbers: all re-derived and correct (0.798; 448/448 K=1024; 64/64 K=512 N=1e4; 23:04:14 < 23:07:59). Wording has three faults. (1) Field order: the file header is `모호했던 점 | 선택 | 근거 | 되돌리는 법`, but the draft puts evidence in field 2 and the choice in field 3. Swapped. (2) The revert field says '원문은 한 글자도 바뀌지 않았다'. That is false once the figure_f14.py docstring (and the missed bench_moduleH.py docstring) are edited. (3) As in the STATUS 1221 note, the ckpt mismatch is listed with no statement that the two ckpts share an architecture (audit P0-2b 반박 (1)). Added bench_moduleH.py docstring to the places list; it carries the same wrong sentence (see missing).

초안 원안:

```text
`[2026-09-23 __:__ KST] 정정 — §6q A8 "학습 prior 4.6배" 는 arm 간 수신기 비용비가 아니다 (review_next P0-2b·cost/M1·cost/M2) | A8(`complexity_moduleH.txt`, 09-22 14:29)은 양쪽 prior 를 `prior.denoise_full(q, nu)` 로 잰 등방 마이크로벤치마크이고, GMM 은 kron **K=512**(N=1e4 적합), 학습 arm 은 `d2sx_N10000_a1.pt` 였다. 헤드라인 GMM arm `M-ours-bstar` 는 denoise_full 을 부르지 않고 외부 반복마다 `GMMPriorB.ep_site(G,b,lam_min)` 를 부른다(`arms.py:36,163`, `Demo/t2_route_a.py:373-374`; `raw_B16e4k` C2 −3 dB 에서 `M-ours-bstar|clip` 평균 0.798). 헤드라인 `raw_B16e4k` 448파일은 kron_K=1024·N=1.6e5·`d2sx_N160000_a1.pt` 다. 그런데 STATUS §6q A8(1217-1248)·1655, NUMBERS_PACKAGE P12, EXPERIMENTS 21행, F14/F14b/F14c 캡션이 4.6× 를 arm 간 비용비로 인용했고, "K=1024 면 ~2.3×/nearer 2x" 는 denoise_full 외삽이었다. 22:30 항목에서 넣은 "A8 의 K=1024 캐비엇" 은 K 만 다루고 함수 차이를 빠뜨렸으며, `figure_f14.py:222-227` 에 하드코딩돼 F14b 에서는 거짓이 됐다(`raw_B1e4lo` C2 −6 dB 64파일 전부 K=512·N=1e4). F14c 는 생성기를 고치기 전의 판(23:04:14 < 23:07:59)이라 K 캐비엇이 없다. 같은 코드로 다시 돌렸을 때 4.6× 가 재현되지 않았다(감사 cost/M2, 미저장이라 수치는 인용하지 않음) | A8 파일과 해당 절은 기록으로 두고, 각 위치에 정정 주석만 단다: STATUS 1221·1248·1655 뒤, NUMBERS_PACKAGE 742 뒤, EXPERIMENTS 21 뒤, 캡션 세 파일 끝, complexity_moduleH.txt 끝, figure_f14.py docstring. 대체 문장: "A8 은 등방 denoise_full 마이크로벤치마크(K=512, N=1e4 ckpt)이며 수신기 경로가 아니다. 헤드라인 구성(K=1024, d2sx_N160000_a1.pt)의 실경로 Module H 비용비는 V1/b\* = Module H 호출당 1.35× (−3 dB) · 1.39× (+6 dB), 블록 전체 1.33× · 1.38× (헤드라인 구성 kron K=1024 + d2sx_N160000_a1, 실제 수신기 경로; `results/review_next/complexity_moduleH_ep.txt`)." 그림과 표는 재생성하지 않는다 | 추가한 정정 주석 줄을 지우면 원상태로 돌아간다. 원문은 한 글자도 바뀌지 않았다`
```
</details>

<details><summary>근거</summary>

DECISIONS.md at HEAD has 104 lines; entries from line 60 on are separated by blank lines, and line 26 shows the '정정 —' pattern. Every number here was re-derived: complexity_moduleH.txt:2,5-6,16-17; raw meta on CPU (raw_B16e4k 448/448 K=1024; raw_B1e4lo C2 -6 dB 64/64 K=512, N=1e4); M-ours-bstar|clip mean 0.7976; mtimes of F14c and figure_f14.py from stat; call path at arms.py:36,163 and t2_route_a.py:373-374.

검증: (위 참조)
</details>

### cost-ckpt-13 · P0-1b — `conf/STATUS.md` 652 뒤에 삽입 (best val 이 체크포인트 출처로 인용된 곳, D2 확증 실행 절)

- 방식: **STATUS inline note** · ✏️ 검증 수정 반영 (인용 OK · 수치 OK · 문구 X)

**원문 (HEAD)**

```text
실행에 쓴 체크포인트는 `ckpt/d2sx_N160000_a1.pt` (sha256 4443921ce8d5c4a1…, 1784 ep patience 종료,
best val **3.519379e-01 @1764**, 3시드 중 검증손실로 선택, BLER 미사용).
```

**제안 문구**

```text
> **정정 (2026-09-23, review_next P0-1b)**: 이 파일이 담은 가중치는 **best(@1764)가 아니라 마지막 epoch(@1784)의 EMA** 다. 4ad41df9 까지의 `score.train` 은 best 를 스칼라로만 추적하고 매 epoch 현재 EMA 로 같은 파일을 덮어썼으며, `load_model` 은 `st["ema"]` 를 읽는다. 체크포인트 실측: epoch 1784, best_epoch 1764, best_val 3.519379e-01, **@1784 EMA 의 val 3.519602e-01**(`hist`, `logs/train_d2sx_N160000_a1.log:1791`), ema sha256[:16] a43f1105eb27a29b. 두 시점 사이에 EMA 가 563×20 = 11,260회 갱신됐으므로, 평가된 EMA 에 남은 @1764 EMA 의 비중은 0.999^11260 ≈ 1.3e-5 다. 즉 둘은 서로 다른 가중치다. @1764 가중치는 어디에도 저장되지 않아 복구할 수 없다(**BEST_WEIGHTS_UNAVAILABLE**). 이 절(`raw_C` D2 1344파일)의 V0/V1/V4/V4b 와 이후 `raw_B16e4`(1344)·`raw_B16e4k`(448)의 같은 arm 은 전부 이 last-EMA 로 평가됐다(raw meta 에는 `stagec_ckpt` 경로만 있고 해시·epoch 는 없다). **대체 문장**: "실행에 쓴 가중치는 `ckpt/d2sx_N160000_a1.pt` 의 마지막 epoch(1784) EMA 이다(file sha256 4443921ce8d5c4a1…, ema a43f1105eb27a29b, 이 가중치의 val 3.519602e-01). 시드 선택에 쓴 best val 은 3.519379e-01 @1764 이며, 그 epoch 의 가중치는 저장되지 않았다(BEST_WEIGHTS_UNAVAILABLE)." 마지막 epoch val 로 비교해도 시드 선택 순서는 같다(a1 3.519602e-01 < a3 3.525437e-01 < a2 3.548169e-01). best 가중치로 평가한 BLER 은 측정된 적이 없다.
```

<details><summary>검증 agent 지적 / 초안 원안</summary>

지적: Quote: lines 651-652 are verbatim. Numbers re-derived on CPU: epoch 1784, best_epoch 1764, best_val 3.5193789e-01, hist val at 1784 0.3519601524 (3.519602e-01), file sha256[:16] 4443921ce8d5c4a1. The EMA hash a43f1105eb27a29b reproduces with sorted key-name+bytes hashing. range(0,144000,256) gives 563 steps per epoch; 563*20 = 11,260 and 0.999^11260 = 1.28e-5. Last-epoch vals: a1 3.519602e-01 < a3 3.525437e-01 < a2 3.548169e-01. Log lines 1771, 1791 and 1792 agree. One precision fault: '이 절(`raw_C` 1344파일)'. raw_C holds 2688 files (1344 D2 + 1344 D1 on sx_N160000_D1.pt), so this should say D2. The evidence field also cites 'L3 n_train=144000'; it is actually log line 4 (not in the proposed text).

초안 원안:

```text
> **정정 (2026-09-23, review_next P0-1b)**: 이 파일이 담은 가중치는 **best(@1764)가 아니라 마지막 epoch(@1784)의 EMA** 다. 4ad41df9 까지의 `score.train` 은 best 를 스칼라로만 추적하고 매 epoch 현재 EMA 로 같은 파일을 덮어썼으며, `load_model` 은 `st["ema"]` 를 읽는다. 체크포인트 실측: epoch 1784, best_epoch 1764, best_val 3.519379e-01, **@1784 EMA 의 val 3.519602e-01**(`hist`, `logs/train_d2sx_N160000_a1.log:1791`), ema sha256[:16] a43f1105eb27a29b. 두 시점 사이에 EMA 가 563×20 = 11,260회 갱신됐으므로, 평가된 EMA 에 남은 @1764 EMA 의 비중은 0.999^11260 ≈ 1.3e-5 다. 즉 둘은 서로 다른 가중치다. @1764 가중치는 어디에도 저장되지 않아 복구할 수 없다(**BEST_WEIGHTS_UNAVAILABLE**). 이 절(`raw_C` 1344파일)의 V0/V1/V4/V4b 와 이후 `raw_B16e4`(1344)·`raw_B16e4k`(448)의 같은 arm 은 전부 이 last-EMA 로 평가됐다(raw meta 에는 `stagec_ckpt` 경로만 있고 해시·epoch 는 없다). **대체 문장**: "실행에 쓴 가중치는 `ckpt/d2sx_N160000_a1.pt` 의 마지막 epoch(1784) EMA 이다(file sha256 4443921ce8d5c4a1…, ema a43f1105eb27a29b, 이 가중치의 val 3.519602e-01). 시드 선택에 쓴 best val 은 3.519379e-01 @1764 이며, 그 epoch 의 가중치는 저장되지 않았다(BEST_WEIGHTS_UNAVAILABLE)." 마지막 epoch val 로 비교해도 시드 선택 순서는 같다(a1 3.519602e-01 < a3 3.525437e-01 < a2 3.548169e-01). best 가중치로 평가한 BLER 은 측정된 적이 없다.
```
</details>

<details><summary>근거</summary>

CPU torch.load of conf/ckpt/d2sx_N160000_a1.pt: epoch=1784, best_epoch=1764, best_val=3.519379e-01, hist[-1]=(1784, train 0.35196015?, val ...). Precisely, hist[-1][2]=0.3519601524 is the val at epoch 1784, and the hist row at 1764 has val 0.3519378901. File sha256[:16]=4443921ce8d5c4a1; EMA sha256[:16] (sorted keys + bytes)=a43f1105eb27a29b. The log (logs/train_d2sx_N160000_a1.log) agrees: L1771 'epoch 1764 ... val 3.519379e-01 ... *', L1791 'epoch 1784 ... val 3.519602e-01', L1792 '# done: 1784 epochs, stopped_by=patience ... best val 3.519379e-01 @ epoch 1764'; L3 n_train=144000. ceil(144000/256)=563 updates/epoch x20=11,260, and 0.999^11260=1.28e-5. At 4ad41df9, score.py:830-834 computes val_loss from the EMA (ema.copy_to(vm)); :875 torch.save writes ema=ema.shadow every epoch. At HEAD, load_model score.py:1025 reads st['ema']. Raw meta re-read: raw_C 1344, raw_B16e4 1344 and raw_B16e4k 448 files all have stagec_ckpt=d2sx_N160000_a1.pt, and no hash or epoch key. arms.py:175-183: V0/V4/V4b all come from score_prior_c. Other seeds on CPU: a2 epoch 1378/best 1358, last val 3.548169e-01; a3 epoch 1044/best 1024, last val 3.525437e-01.

검증: (위 참조)
</details>

### cost-ckpt-14 · P0-1b — `conf/STATUS.md` 672 뒤에 삽입 (site ablation 표의 마지막 행 = 이 체크포인트의 V1 0.145 가 처음 보고된 곳. 표를 끊도록 빈 줄 1개 먼저)

- 방식: **STATUS inline note** · ✅ 검증 통과

**원문 (HEAD)**

```text
| **M-ours-dscore-C-V1** | 행렬 + PSD 투영 | **0.145** | [0.132, 0.159] |
```

**제안 문구**

```text
> **정정 (2026-09-23, review_next P0-1b)**: V1 0.145(= 371/2560; `raw_C` C2 −3 dB 64파일을 재집계한 값이며, `raw_B16e4`·`raw_B16e4k` 에서도 같은 371)와 이 표의 네 arm 은 `d2sx_N160000_a1.pt` 의 **마지막 epoch(1784) EMA** 로 평가됐다. best(@1764) 가중치가 아니다. 652 행 뒤 정정을 볼 것. BEST_WEIGHTS_UNAVAILABLE.
```

<details><summary>근거</summary>

CPU re-count of M-ours-dscore-C-V1|blk_err[:, -1] (iteration 16; shape (40,16) per file) over the 64 D2_C2_S2_Nr8_T16_Tp4_dft_snr-3_* files: raw_C 371/2560=0.1449, raw_B16e4 371/2560, raw_B16e4k 371/2560. By contrast raw_B1e4 (N=1e4 ckpt) gives 372/2560=0.1453. In STATUS, 672 is the first V1 number on this checkpoint: grep for 0.145 finds line 160 (summary, written later) and then 672 in the section dated 00:25 on 09-22.

검증: Quote: line 672 is verbatim and is the last table row (673 blank). Numbers: V1 blk_err[:, -1] over the 64 C2 -3 dB files is 371/2560 = 0.1449 in raw_C, raw_B16e4 and raw_B16e4k (raw_B1e4 gives 372/2560). Wording: none.
</details>

### cost-ckpt-15 · P0-1b — `conf/STATUS.md` 1591 뒤에 삽입 (B16e4k 헤드라인 절에서 학습 arm 체크포인트를 적은 줄. 헤드라인 표 1597·문장 1604-1606 바로 위)

- 방식: **STATUS inline note** · ✅ 검증 통과

**원문 (HEAD)**

```text
대비 **+3.18 nat**) 추가. raw meta `kron_K=1024` 로 b\* 이동 확인. 학습 arm 은 B16e4 와 같은 `d2sx_N160000_a1.pt`.
```

**제안 문구**

```text
> **정정 (2026-09-23, review_next P0-1b)**: 이 `d2sx_N160000_a1.pt` 는 **마지막 epoch(1784) EMA** 다(ema sha256[:16] a43f1105eb27a29b, 이 가중치의 val 3.519602e-01). best val 3.519379e-01 @1764 의 가중치가 아니다. 아래 헤드라인의 V1 0.1449(371/2560)와 V0·V4·V4b 는 전부 이 가중치의 값이다. best 가중치는 저장되지 않아 재평가할 수 없다(BEST_WEIGHTS_UNAVAILABLE). 재평가하려면 수정된 `score.train`(cd241b7e, `<ckpt>_best.pt`)으로 새 태그 재학습이 필요하다. 652 행 뒤 정정을 볼 것.
```

<details><summary>근거</summary>

Same checkpoint read as the 652 note. raw_B16e4k: 448/448 files have stagec_ckpt d2sx_N160000_a1.pt, and V1 C2 -3 dB is 371/2560=0.1449 (CPU re-count). The best-weights file path at HEAD is score.py:691 best_ckpt_path. CHANGELOG_REVIEW §5 says best-weight re-evaluation needs a new-tag retrain.

검증: Quote: line 1591 is verbatim. Numbers: 448/448 raw_B16e4k files use d2sx_N160000_a1.pt; V1 is 371/2560 = 0.1449; ema a43f1105eb27a29b; val 3.519602e-01. best_ckpt_path is at HEAD score.py:691. Wording: none.
</details>

### cost-ckpt-16 · P0-1b — `conf/DECISIONS.md` 104 뒤 append (106 의 cost 정정 다음, 빈 줄 후 108행 예정)

- 방식: **DECISIONS append** · ✏️ 검증 수정 반영 (인용 OK · 수치 OK · 문구 X)

**원문 (HEAD)**

```text
(DECISIONS:61 의 일부) **BLER arm 은 검증손실 최선인 a1 하나를 쓰고(3.519379e-01 @1764; a2 3.547692e-01, a3 3.525231e-01), 세 시드의 검증손실과 정지 방식은 전부 보고한다.**
(DECISIONS:100 의 일부) −3 dB 0.2527 → 0.2434, V1 0.1449, pooled 454:78 p=1.7e-65 3/3.
```

**제안 문구**

```text
`[2026-09-23 __:__ KST] 정정 — Stage C 학습 arm 은 best 가 아니라 마지막 epoch EMA 로 평가됐다 (review_next P0-1b) | 과거 수치는 고치지 않고 표기만 한다: "평가 = last-EMA @1784 (ema a43f1105eb27a29b), 보고된 best val = @1764, BEST_WEIGHTS_UNAVAILABLE". 표기 위치: STATUS 652·672·1591 뒤, EXPERIMENTS 21 뒤, PAPER_MATERIALS 620 뒤 정정 주석. [2026-09-21 23:00] 의 시드 선택은 마지막 epoch val 로 비교해도 순서가 같아(a1 3.519602e-01 < a3 3.525437e-01 < a2 3.548169e-01) 선택 결과는 변하지 않는다. best 가중치로 평가한 BLER 은 존재하지 않는다. 필요하면 cd241b7e 의 `<ckpt>_best.pt` 경로로 새 태그 재학습(GPU·장시간, 별도 승인) | 기록은 평가 체크포인트를 "best val 3.519379e-01 @1764" 로 소개했다(STATUS:651-652, PAPER_MATERIALS:415-416·618-620·977, NUMBERS_PACKAGE:195, 이 파일 [2026-09-21 23:00]). 그래서 평가된 가중치가 best 인 것처럼 읽힌다. 실제로는 4ad41df9 까지의 `score.train` 이 best 를 스칼라로만 추적하고 매 epoch 현재 model/EMA 로 같은 파일을 덮어썼으며, `load_model` 은 `st["ema"]` 를 읽는다. `d2sx_N160000_a1.pt`: epoch 1784, best_epoch 1764, @1784 EMA 의 val 3.519602e-01(best 대비 상대 +6.3e-5), file 4443921ce8d5c4a1, ema a43f1105eb27a29b, 두 시점 사이 EMA 갱신 11,260회. 영향 범위(raw meta 재집계): raw_C D2·raw_B16e4·raw_B16e4k(1344/1344/448파일, 모두 이 ckpt; V1 C2 −3 dB 는 세 곳 모두 371/2560) = V0/V1/V4/V4b 헤드라인 전부. raw_C D1(1344파일, `sx_N160000_D1.pt`, 200 vs best 136; V0/V1/V4 → tables_D1_C). raw_B1e4·B1e4lo·B1e4x(`d2sx_N10000_a1`, 673 vs best 653), raw_B1e4s2(a2, 657 vs 637), raw_B1e4s3(a3, 662 vs 642), raw_B4e4·B4e4k·B4e4k1(`d2sx_N40000_a1`, 1051 vs 1031), raw_supp(112파일, `meta|dscore_ckpt` d2sx_N10000_a1, arm M-ours-dscore). `raw_NR16run` 은 score arm 을 만들지 않았으므로(448파일 전부 stagec_status ABSENT) 해당하지 않는다 | 정정 주석을 지우면 되돌아간다. 원문·raw·ckpt 는 바뀌지 않았다`
```

<details><summary>검증 agent 지적 / 초안 원안</summary>

지적: Quote: the DECISIONS:61 and :100 fragments are verbatim. Numbers re-derived and correct (1784/1764, +6.3e-5, 11,260; raw counts 1344/1344/448; 673/653, 657/637, 662/642, 1051/1031; NR16run 448/448 ABSENT with no dscore-C keys). Wording has four faults. (1) The scope list misses two raw sets. raw_C D1 is 1344 files with meta|stagec_ckpt sx_N160000_D1.pt at epoch 200 against best 136; arms V0/V1/V4 feed tables_D1_C (audit P0-1b 반박 (4)). raw_supp is 112 files with meta|dscore_ckpt d2sx_N10000_a1.pt, arm M-ours-dscore. (2) '표기 위치는 STATUS 652·672·1591' leaves out the EXPERIMENTS 21 and PAPER_MATERIALS 620 notes that are in the same draft. (3) Fields 2 and 3 are in the wrong order (header: 선택 | 근거). (4) '그래서 읽는 사람은 ... best 로 읽는다' asserts what readers do; softened to '읽힌다'. The PAPER_MATERIALS line range is also fixed to 618-620.

초안 원안:

```text
`[2026-09-23 __:__ KST] 정정 — Stage C 학습 arm 은 best 가 아니라 마지막 epoch EMA 로 평가됐다 (review_next P0-1b) | 기록은 평가 체크포인트를 "best val 3.519379e-01 @1764" 로 소개했다(STATUS:651-652, PAPER_MATERIALS:415-416·618-619·977, NUMBERS_PACKAGE:195, 이 파일 [2026-09-21 23:00]). 그래서 읽는 사람은 평가된 가중치를 best 로 읽는다. 실제로는 4ad41df9 까지의 `score.train` 이 best 를 스칼라로만 추적하고 매 epoch 현재 model/EMA 로 같은 파일을 덮어썼으며, `load_model` 은 `st["ema"]` 를 읽는다. `d2sx_N160000_a1.pt`: epoch 1784, best_epoch 1764, @1784 EMA 의 val 3.519602e-01(best 대비 상대 +6.3e-5), file 4443921ce8d5c4a1, ema a43f1105eb27a29b, 두 시점 사이 EMA 갱신 11,260회. 영향 범위(raw meta `stagec_ckpt` 재집계): raw_C·raw_B16e4·raw_B16e4k(1344/1344/448파일, 모두 이 ckpt; V1 C2 −3 dB 는 세 곳 모두 371/2560) = V0/V1/V4/V4b 헤드라인 전부. raw_B1e4·B1e4lo·B1e4x(`d2sx_N10000_a1`, 673 vs best 653), raw_B1e4s2(a2, 657 vs 637), raw_B1e4s3(a3, 662 vs 642), raw_B4e4·B4e4k·B4e4k1(`d2sx_N40000_a1`, 1051 vs 1031). `raw_NR16run` 은 score arm 을 만들지 않았으므로(448파일 전부 stagec_status ABSENT) 해당하지 않는다 | 과거 수치는 고치지 않고 표기만 한다: "평가 = last-EMA @1784 (ema a43f1105eb27a29b), 보고된 best val = @1764, BEST_WEIGHTS_UNAVAILABLE". 표기 위치는 STATUS 652·672·1591 뒤 정정 주석. [2026-09-21 23:00] 의 시드 선택은 마지막 epoch val 로 비교해도 순서가 같아(a1 3.519602e-01 < a3 3.525437e-01 < a2 3.548169e-01) 선택 결과는 변하지 않는다. best 가중치로 평가한 BLER 은 존재하지 않는다. 필요하면 cd241b7e 의 `<ckpt>_best.pt` 경로로 새 태그 재학습(GPU·장시간, 별도 승인) | 정정 주석을 지우면 되돌아간다. 원문·raw·ckpt 는 바뀌지 않았다`
```
</details>

<details><summary>근거</summary>

CPU torch.load of each checkpoint: d2sx_N160000_a1 1784/1764 (val@1784 0.3519601524, best 0.3519378901, relative +6.33e-5); d2sx_N160000_a2 1378/1358 (last 0.3548169); d2sx_N160000_a3 1044/1024 (last 0.3525437); d2sx_N10000_a1 673/653; d2sx_N10000_a2 657/637; d2sx_N10000_a3 662/642; d2sx_N40000_a1 1051/1031. Raw meta stagec_ckpt counts from reading every raw_*/D2_*.npz: raw_B16e4 1344, raw_B16e4k 448, raw_C 1344 -> d2sx_N160000_a1; raw_B1e4 448, raw_B1e4lo 512, raw_B1e4x 896 -> d2sx_N10000_a1; raw_B1e4s2 448 -> a2; raw_B1e4s3 448 -> a3; raw_B4e4/B4e4k/B4e4k1 448 each -> d2sx_N40000_a1. raw_NR16run 448 files: no M-ours-dscore-C-* blk_err key, stagec_status 'ABSENT -- M-ours-dscore-C-* only: n/a (no score model for this array size)' (untracked directory). The best-val quote sites were found with git grep at HEAD.

검증: (위 참조)
</details>

### cost-ckpt-17 · P0-1b — `docs/EXPERIMENTS.md` 21 뒤 (파일 끝) — 위 cost 정정 주석 다음 줄

- 방식: **other** · ✏️ 검증 수정 반영 (인용 OK · 수치 OK · 문구 X)

**원문 (HEAD)**

```text
(**헤드라인: 게이트 통과 + 동일예산 N=1.6e5, GMM K=1024 0.2434 → V1 0.1449, pooled 454:78 p=1.7e-65, 3/3 POWERED**)
```

**제안 문구**

```text
> 정정 (2026-09-23, review_next P0-1b·ckpt/M2): 21행 헤드라인의 학습 arm(V1 0.1449 = 371/2560 등)은 `conf/ckpt/d2sx_N160000_a1.pt` 의 마지막 epoch(1784) EMA 로 평가됐다(ema sha256[:16] a43f1105eb27a29b, 이 가중치의 val 3.519602e-01). 시드 선택에 쓴 best val 3.519379e-01 @1764(`conf/STATUS.md:652`)의 가중치는 저장되지 않았다(BEST_WEIGHTS_UNAVAILABLE). 같은 행의 N=1e4/4e4 표(B1e4*, B4e4*)도 각 ckpt 의 마지막 epoch EMA 다. `tables_D1_C.txt` 의 학습 arm 과 "D1 게이트 PASS @N=1.6e5" 는 `sx_N160000_D1.pt` 의 @200 EMA 로, "λ=0.01 만 PASS" 는 `sx_V3_N160000_D1_a1_lam0.01.pt` 의 @200 EMA 로 측정됐다(각 best @136·@142 의 가중치는 저장되지 않음). 원래 행은 고치지 않는다.
```

<details><summary>검증 agent 지적 / 초안 원안</summary>

지적: Quote: the headline fragment is verbatim in line 21. Numbers are correct. Wording has two faults. (1) Line 21 also records 'tables_D1_C.txt', 'D1 게이트 PASS @N=1.6e5 (GB 2.66e-3/GC 0.0999/GD 0.0718)' and 'λ=0.01 만 PASS', and each of these was measured on a last-epoch EMA. sx_N160000_D1.pt: epoch 200, best 136. sx_V3_N160000_D1_a1_lam0.01.pt: epoch 200, best 7.398582e-01 @142, @200 val 7.399352e-01; gate_D1_L0.01.txt was written after the ckpt. A note on this line should cover them too (P0-1b scope plus ckpt/M2). (2) '기록된 best val 3.519379e-01 @1764' — EXPERIMENTS itself does not record that value, so the corrected text points to STATUS:652.

초안 원안:

```text
> 정정 (2026-09-23, review_next P0-1b): 21행 헤드라인의 학습 arm(V1 0.1449 = 371/2560 등)은 `conf/ckpt/d2sx_N160000_a1.pt` 의 마지막 epoch(1784) EMA 로 평가됐다(ema sha256[:16] a43f1105eb27a29b, 이 가중치의 val 3.519602e-01). 기록된 best val 3.519379e-01 @1764 의 가중치는 저장되지 않았다(BEST_WEIGHTS_UNAVAILABLE). 같은 행의 N=1e4/4e4 표(B1e4*, B4e4*)도 각 ckpt 의 마지막 epoch EMA 다. 원래 행은 고치지 않는다.
```
</details>

<details><summary>근거</summary>

Same CPU checkpoint reads and raw meta counts as the DECISIONS P0-1b entry. raw_B16e4k V1 C2 -3 dB is 371/2560 = 0.1449, matching the quoted 0.1449.

검증: (위 참조)
</details>

### cost-ckpt-18 · P0-1b — `conf/PAPER_MATERIALS.md` 620 뒤에 삽입 (618-620 글머리표 끝, 2칸 들여쓰기 인용). 977 행 표의 같은 서술도 이 주석으로 다룸 — 요청한 STATUS/DECISIONS 밖이라 적용 여부는 적용자 판단

- 방식: **other** · ✅ 검증 통과

**원문 (HEAD)**

```text
- 체크포인트 `ckpt/d2sx_N160000_a1.pt` (sha256 `4443921ce8d5c4a1…`, patience 로 1784 epoch 종료,
  best val **3.519379e-01 @1764**). **검증손실로 3시드 중 선택, BLER 미사용**
  (a1 3.519379e-01 / a2 3.547692e-01 / a3 3.525231e-01 — 시드 간 0.8%, `DECISIONS.md` 23:00).
```

**제안 문구**

```text
> **정정 (2026-09-23, review_next P0-1b)**: 이 파일의 가중치는 마지막 epoch(1784) EMA 다(ema sha256[:16] a43f1105eb27a29b, 이 가중치의 val 3.519602e-01). best val 3.519379e-01 @1764 는 선택 기준값일 뿐이고, 그 epoch 의 가중치는 저장되지 않았다(BEST_WEIGHTS_UNAVAILABLE). §15 와 이후 표의 V0/V1/V4/V4b 는 전부 last-EMA 로 낸 값이다. 원고에 "best 체크포인트" 로 쓰지 말 것. 977 행 표의 같은 서술에도 적용된다. 마지막 epoch val 로 비교해도 시드 순서는 같다(a1 3.519602e-01 < a3 3.525437e-01 < a2 3.548169e-01).
```

<details><summary>근거</summary>

PAPER_MATERIALS.md at HEAD, lines 618-620 and 977, quote the checkpoint with 'best val 3.519379e-01 @1764'. Checkpoint facts come from the CPU torch.load above. This file is Claude-written and not in the user-owned spec list; I include it because the paper is drafted from it. It is outside the STATUS/DECISIONS scope asked for P0-1b, so the applier decides.

검증: Quote: lines 618-620 are verbatim; line 977 has the same wording. Numbers: ema a43f1105eb27a29b, val 3.519602e-01, and the seed order are correct. Wording: none. The file is not user-owned. It is outside the STATUS/DECISIONS scope, as the drafter notes, so the applier decides. Related lines 416 (§12.3) and 566 (§14, D1 on sx_N160000_D1.pt at @200) are listed under missing.
</details>

### cost-ckpt-19 · ckpt/M2 — `conf/STATUS.md` 661 뒤에 삽입 (형제 D1 게이트 PASS 로 헤드라인 ckpt 자격을 연결한 문단 끝)

- 방식: **STATUS inline note** · ✅ 검증 통과

**원문 (HEAD)**

```text
D2 재학습본이 자격을 얻는다" 고 규정했고, 그 형제는 `ckpt/sx_N160000_D1.pt` 이며 `LADDER_C.md:1` 에
PASS 행이 있다 (GA 9.879e-16 / GB 2.659e-3 / GC 9.986e-2 / GD 7.183e-2). **두 모델은 같은 레시피
(dit vp/angle w64 d6 h8 p1 emb256 lr2.238046e-3 ema0.999 batch256), 같은 예산(N'=1.6e5), 같은 정지
규칙으로 학습됐고 testbed 만 다르다.** 이 문단이 그 자격 연결이며, 앞선 판에는 없었다.
GA 는 이 모델 계열에서 구조적 0 이므로 PASS 는 **GB·GC·GD 세 게이트**에 달려 있다.
```

**제안 문구**

```text
> **정정 (2026-09-23, review_next ckpt/M2)**: 형제의 PASS(GB 2.659e-3 / GC 9.986e-2 / GD 7.183e-2)는 `sx_N160000_D1.pt` 의 **마지막 epoch(200) EMA** 에서 측정됐다. 게이트 경로 `gates_D1 → _as_model → load_model` 이 `st["ema"]` 를 읽기 때문이다. 그 run 의 best 는 7.398444e-01 @136 이고, @200 EMA 의 val 은 7.398687e-01 이다(`logs/train_sx_N160000_D1.log:143,207-208`). min_epochs=200 이라 best 이후 64 epoch 를 더 학습했다. best(@136) 가중치의 게이트 값은 측정된 적이 없고 복구할 수도 없다. 자격 연결 문장은 그대로 두되, "PASS 는 형제의 last-EMA @200 에 대한 것" 을 함께 적는다.
```

<details><summary>근거</summary>

CPU torch.load of conf/ckpt/sx_N160000_D1.pt: epoch=200, best_epoch=136, best_val=7.398444e-01, hist val@200=0.7398687005; file sha256[:16] 9a38b0c9535d64a5, ema ae04fefa33998484. The log agrees: L143 'epoch 136 ... val 7.398444e-01 ... *', L207 'epoch 200 ... val 7.398687e-01', L208 '# done: 200 epochs, stopped_by=patience ... best val 7.398444e-01 @ epoch 136'. Its L6 is 'stopping: patience 20 on val loss, never before 200 epochs' (the same line appears in train_d2sx_N160000_a1.log). LADDER_C.md:1 'GATED from sx_N160000_D1.pt'. Gate path per REVIEW_AUDIT ckpt/M2 (score.py _as_model -> load_model reading st['ema'], HEAD score.py:1025).

검증: Quote: lines 657-661 are verbatim. Numbers re-derived: sx_N160000_D1.pt epoch 200, best 136, best 7.398444e-01, @200 val 7.398687e-01; 200-136 = 64. Log lines 143, 207 and 208 agree. The ckpt (mtime 09-21 09:14) predates gate_D1_C, so the gate read the @200 EMA. Wording: none. The evidence field cites log 'L6' for the stopping line; it is actually line 7 (not in the proposed text). The PASS is first recorded at STATUS:375, where the same note is needed; see missing.
</details>

### cost-ckpt-20 · ckpt/M2 — `conf/STATUS.md` 1497 뒤에 삽입 (§6e λ=0.1 게이트: best val @33 과 FAIL 판정이 같은 줄에 있음)

- 방식: **STATUS inline note** · ✅ 검증 통과

**원문 (HEAD)**

```text
`results/gate_D1_L0.1.txt`, `LADDER_L0.1.md`. `sx_V3_N160000_D1_a2_lam0.1.pt` (§3d 시행 2 = 클리핑 1.0, 시행 1 은 발산),
patience 종료 @200, best val 7.422616e-01 @33 (V0 7.398444e-01). **VERDICT FAIL — GB·GC·GD 세 게이트.**
```

**제안 문구**

```text
> **정정 (2026-09-23, review_next ckpt/M2)**: 이 FAIL 판정은 best(@33) 가중치가 아니라 **@200 EMA**(min_epochs=200)에서 측정됐다. 그 가중치의 val 은 7.458941e-01 로, 같은 줄의 best val 7.422616e-01 @33 과 다르다. best 가중치에서의 게이트 값은 측정된 적이 없고 복구할 수 없다. 판정이 달라지는지는 확인되지 않았다.
```

<details><summary>근거</summary>

CPU torch.load of conf/ckpt/sx_V3_N160000_D1_a2_lam0.1.pt: epoch=200, best_epoch=33, best_val=7.422616e-01, hist val@200=0.7458940744; file sha256[:16] 0ccfa7a45475ec92. The audit (ckpt/M2) found gate_D1_L0.1.txt gating this file at ep 200. The gate reads st['ema'], which is the last-epoch EMA.

검증: Quote: lines 1496-1497 are verbatim. Numbers: sx_V3_N160000_D1_a2_lam0.1.pt epoch 200, best 33, best 7.422616e-01, @200 val 7.458941e-01. The ckpt mtime (16:40:03) precedes gate_D1_L0.1.txt (16:46:19). Wording: none.
</details>

### cost-ckpt-21 · ckpt/M2 — `conf/STATUS.md` 74 뒤에 삽입 (Stage A/B 게이트 판정 요약)

- 방식: **STATUS inline note** · ✅ 검증 통과

**원문 (HEAD)**

```text
**총 959 시도** (사전 등록 사다리 18 + 확장칸 15 + TPE 724 + 균등표본 196 + 최종 재게이트 6) **전부 게이트 미달.**
```

**제안 문구**

```text
> **정정 (2026-09-23, review_next ckpt/M2)**: 이 게이트 판정들은 각 체크포인트 파일에 남은 **마지막 epoch EMA** 로 측정됐다(`gates_D1 → load_model` 이 `st["ema"]` 를 읽고, best 가중치는 저장되지 않았다). min_epochs=200 때문에 여러 칸이 best 보다 한참 뒤의 가중치로 게이트됐다. 예(best val @epoch → 게이트된 가중치의 val): L5_a3 1.048803 @100 → @200 1.677785 (LADDER:37·39, GB +109.16%), L4u_a3 0.732129 @70 → 0.992767 (LADDER:38), L4u_a1 0.734262 @74 → 0.892621 (LADDER:41), L6_a3 −0.061637 @107 → 0.622517 (LADDER:47), L5_a1 1.043899 @117 → 1.132333 (LADDER:31). LADDER 의 train 행은 best val 을 적는다. best 가중치에서 판정이 달라지는지는 확인되지 않았다. best 와 last 의 차이가 작은 L3_a1(221 vs 201)·L4_a1(253 vs 233)·L4_a2(207 vs 187)도 FAIL 이다.
```

<details><summary>근거</summary>

CPU torch.load (epoch, best_epoch, best_val, hist val at last epoch): L5_a3_D1 200/100/1.048803/1.6777847; L4u_a3_D1 200/70/0.7321294/0.9927667; L4u_a1_D1 200/74/0.7342620/0.8926206; L6_a3_D1 200/107/-0.06163746/0.6225166; L5_a1_D1 200/117/1.0438989/1.1323328; L3_a1_D1 221/201/0.7686900/0.7687177; L4_a1_D1 253/233/0.7292639/0.7293086; L4_a2_D1 207/187/0.7315967/0.7320463. LADDER.md at HEAD: L37 L5_a3 train row 'val 1.049e+00', L39 gate GB +109.16% GC 8.8627 FAIL, L38 L4u_a3 FAIL, L41 L4u_a1 FAIL, L47 L6_a3 GB +119.81% FAIL, L31 L5_a1 FAIL, L19 L3_a1 FAIL, L25 L4_a1 FAIL, L27 L4_a2 FAIL. The HPO path (hpo.py:121-124,289-292 at 4ad41df9) also gates the saved ckpt through score.gates_D1, so it too reads the last-epoch EMA. I did not measure HPO epoch gaps, so the note gives only the ladder examples.

검증: Quote: line 74 is verbatim. Numbers re-derived on CPU: L5_a3 1.048803@100→1.677785, L4u_a3 0.732129@70→0.992767, L4u_a1 0.734262@74→0.892621, L6_a3 −0.061637@107→0.622517, L5_a1 1.043899@117→1.132333; L3_a1 221/201, L4_a1 253/233, L4_a2 207/187. The LADDER line refs (19, 25, 27, 31, 37, 38, 39, 41, 47) and GB +109.16% match. The LADDER train rows print last-epoch train loss and best val. The HPO path at 4ad41df9 (hpo.py:121-124, 289-292) gates the saved last-epoch file. Wording: none.
</details>

### cost-ckpt-22 · ckpt/M2 — `conf/DECISIONS.md` 104 뒤 append (108 의 P0-1b 정정 다음, 빈 줄 후 110행 예정)

- 방식: **DECISIONS append** · ✏️ 검증 수정 반영 (인용 OK · 수치 X · 문구 X)

**원문 (HEAD)**

```text
(LADDER.md:37) [2026-09-20 14:02 KST] L5 | a3 | conv rf/pixel w512 d6 lr0.0003 ema0.999 base=L4 (28665346 par) | train 7.092e-01 / val 1.049e+00 | … | 200 ep (stop: patience) …
(LADDER.md:39) [2026-09-20 14:05 KST] L5 | a3 | … | GA 9.851e-16 | GB +109.16% | GC 8.8627 | GD 0.3859 | FAIL | GATED from L5_a3_D1.pt …
```

**제안 문구**

```text
`[2026-09-23 __:__ KST] 정정 — D1 게이트 판정은 best 가 아니라 마지막 epoch EMA 에 대해 측정됐다 (review_next ckpt/M2) | 판정은 고치지 않고 표기만 한다: "게이트 = last-EMA @<epoch>, best @<best_epoch> 가중치 미저장". 표기 위치는 STATUS 74·375·661·1497·1514 뒤 정정 주석. best 가중치에서 판정이 달라지는지는 확인되지 않았다. best 와 last 의 차이가 작은 L3_a1(221 vs 201)·L4_a1(253 vs 233)·L4_a2(207 vs 187)도 FAIL 이라 방향을 말할 수 없다. best 가중치로 다시 게이트하려면 cd241b7e 의 `<ckpt>_best.pt` 로 새 태그 재학습이 필요하다(별도 승인) | LADDER.md·LADDER_C.md·LADDER_L*.md 의 GATED 행, gate_D1_*.txt, resolve_hp 의 gate score 는 전부 `gates_D1 → _as_model → load_model` 이 읽는 `st["ema"]`(파일에 남은 마지막 epoch EMA)로 측정됐다. 반면 같은 LADDER 의 train 행은 best val 을 적는다. min_epochs=200 이라 best 보다 41~167 epoch 뒤의 가중치가 게이트된 칸이 있다(ckpt hist 재측정, best val @epoch → 게이트된 val): L5_a3 1.048803@100 → @200 1.677785, L4u_a3 0.732129@70 → 0.992767, L4u_a1 0.734262@74 → 0.892621, L6_a3 −0.061637@107 → 0.622517, L5_a1 1.043899@117 → 1.132333, L4_a3 0.728793@125 → 0.737369, V2 D1 a3 0.739868@74 → 0.740946, V3 D1 a3 0.748808@159 → 0.750499, λ=0.1 a2 0.742262@33 → 0.745894, λ=0.01 a1 0.739858@142 → 0.739935 (PASS), 헤드라인 자격을 준 형제 `sx_N160000_D1.pt` 0.739844@136 → @200 0.739869 (PASS). best 가중치는 저장되지 않아 다시 게이트할 수 없다 | 정정 주석을 지우면 되돌아간다. LADDER 와 gate 파일은 바뀌지 않았다`
```

<details><summary>검증 agent 지적 / 초안 원안</summary>

지적: Quote: the LADDER.md:37 and :39 fragments, with elisions, match HEAD. Numbers: every listed value re-derives correctly, but the stated range '64~167 epoch' contradicts the entry's own list. V3 D1 a3 (best 159, gated 200) is a gap of 41, and λ=0.01 a1 (best 142) is a gap of 58; both were forced to 200 by min_epochs. The range should be 41~167. Wording has two further faults. (1) The list omits λ=0.01 a1, which is a PASS gated at @200: 0.739858@142 → 0.739935 (gate_D1_L0.01.txt, STATUS:1513-1514). It also omits the primary PASS record, STATUS:375. Both are added to the list and to 표기 위치. (2) Fields 2 and 3 are in the wrong order (header: 선택 | 근거).

초안 원안:

```text
`[2026-09-23 __:__ KST] 정정 — D1 게이트 판정은 best 가 아니라 마지막 epoch EMA 에 대해 측정됐다 (review_next ckpt/M2) | LADDER.md·LADDER_C.md·LADDER_L*.md 의 GATED 행, gate_D1_*.txt, resolve_hp 의 gate score 는 전부 `gates_D1 → _as_model → load_model` 이 읽는 `st["ema"]`(파일에 남은 마지막 epoch EMA)로 측정됐다. 반면 같은 LADDER 의 train 행은 best val 을 적는다. min_epochs=200 이라 best 보다 64~167 epoch 뒤의 가중치가 게이트된 칸이 있다(ckpt hist 재측정, best val @epoch → 게이트된 val): L5_a3 1.048803@100 → @200 1.677785, L4u_a3 0.732129@70 → 0.992767, L4u_a1 0.734262@74 → 0.892621, L6_a3 −0.061637@107 → 0.622517, L5_a1 1.043899@117 → 1.132333, L4_a3 0.728793@125 → 0.737369, V2 D1 a3 0.739868@74 → 0.740946, V3 D1 a3 0.748808@159 → 0.750499, λ=0.1 a2 0.742262@33 → 0.745894, 헤드라인 자격을 준 형제 `sx_N160000_D1.pt` 0.739844@136 → @200 0.739869 (PASS). best 가중치는 저장되지 않아 다시 게이트할 수 없다 | 판정은 고치지 않고 표기만 한다: "게이트 = last-EMA @<epoch>, best @<best_epoch> 가중치 미저장". 표기 위치는 STATUS 74·661·1497 뒤 정정 주석. best 가중치에서 판정이 달라지는지는 확인되지 않았다. best 와 last 의 차이가 작은 L3_a1(221 vs 201)·L4_a1(253 vs 233)·L4_a2(207 vs 187)도 FAIL 이라 방향을 말할 수 없다. best 가중치로 다시 게이트하려면 cd241b7e 의 `<ckpt>_best.pt` 로 새 태그 재학습이 필요하다(별도 승인) | 정정 주석을 지우면 되돌아간다. LADDER 와 gate 파일은 바뀌지 않았다`
```
</details>

<details><summary>근거</summary>

CPU torch.load of every checkpoint listed (epoch/best_epoch/best_val/last hist val): L5_a3 200/100; L4u_a3 200/70; L4u_a1 200/74; L6_a3 200/107; L5_a1 200/117; L4_a3 200/125 (0.7287933 -> 0.7373693); sx_V2_N160000_D1_a3 200/74 (0.7398676 -> 0.7409458); sx_V3_N160000_D1_a3 200/159 (0.7488075 -> 0.7504991); sx_V3_N160000_D1_a2_lam0.1 200/33 (0.7422616 -> 0.7458941); sx_N160000_D1 200/136 (0.7398444 -> 0.7398687). Epoch gaps run from 64 (sibling) to 167 (lam0.1). min_epochs=200 comes from the score.train default (HEAD score.py:826) and the log header 'never before 200 epochs'. The gate path and the resolve_hp gate scores follow REVIEW_AUDIT ckpt/M2 and the P0-4 반박 (a).

검증: (위 참조)
</details>

### cost-ckpt-23 · P0-1b (V2/V3 부분) — `conf/DECISIONS.md` 104 뒤 append (110 의 ckpt/M2 정정 다음, 빈 줄 후 112행 예정)

- 방식: **DECISIONS append** · ✏️ 검증 수정 반영 (인용 OK · 수치 OK · 문구 X)

**원문 (HEAD)**

```text
(LADDER_C.md:2) … ckpt/d2sx_V2_N160000_a1.pt holds the best-val (epoch 85) EMA weights. …
(LADDER_C.md:3) … N_train=160000, ckpt ckpt/d2sx_V3_N160000_a1.pt holds the best-val (epoch 27) EMA weights. …
(LADDER_C.md:4) … N_train=160000, ckpt ckpt/sx_V2_N160000_D1_a1.pt holds the best-val (epoch 48) EMA weights. …
(LADDER_C.md:6) … The checkpoint holds the best-val (epoch 85) EMA weights and is intact. …
```

**제안 문구**

```text
`[2026-09-23 __:__ KST] 정정 — LADDER_C.md 2·3·4·6행의 "checkpoint holds the best-val (epoch N) EMA weights" 는 거짓이다 (review_next P0-1b, V2/V3 부분) | LADDER_C 는 append-only 라 행을 고치지 않고, 이 항목을 정정 기록으로 삼는다. V2 a1·V3 a1 은 감사(P0-1b)가 확인했고, V2 a2·V2 D1 a1 은 이 초안의 작성·검사 단계에서 같은 방법(CPU torch.load)으로 확인했다(감사의 2차 반박은 거치지 않음) | 네 행은 발산으로 멈춘 run 의 체크포인트가 best-val epoch 의 EMA 를 담는다고 적었다. 파일 실측(CPU torch.load): `d2sx_V2_N160000_a1.pt` 는 epoch 118(best 85; @118 val 1.2075), `d2sx_V3_N160000_a1.pt` 는 epoch 62(best 27; @62 val 1.7202), `sx_V2_N160000_D1_a1.pt` 는 epoch 57(best 48; @57 val 1277.08), `d2sx_V2_N160000_a2.pt` 는 epoch 191(best 85; @191 val nan, **EMA 원소 479,489 개 중 479,360 개가 비유한**)이다. 따라서 6행의 "and is intact" 도 거짓이다. 원인은 저장 경로가 매 epoch 덮어쓰기였기 때문이다(P0-1a). 이 넷은 BLER arm 으로 쓰인 적이 없다(EXPERIMENTS 21행 "V2·V3·λ∈{0.01,0.1,1.0} 은 arm 아님") | 이 줄을 지우면 되돌아간다`
```

<details><summary>검증 agent 지적 / 초안 원안</summary>

지적: Quote: the clauses from LADDER_C.md lines 2, 3, 4 and 6 are verbatim at HEAD; row 6 ('V2 | D2 a2 | ... grad_clip=1.0') is d2sx_V2_N160000_a2.pt. Numbers re-derived on CPU: V2 a1 118/85, @118 1.2075026; V3 a1 62/27, @62 1.7202276; V2 D1 a1 57/48, @57 1277.0775; V2 a2 191/85, @191 nan, 479,360 of 479,489 EMA elements non-finite. The other three have no non-finite elements. Wording has three faults. (1) The quote '(EXPERIMENTS 21행 "V2·V3·λ 은 arm 아님")' is not verbatim; line 21 reads 'V2·V3·λ∈{0.01,0.1,1.0} 은 arm 아님'. (2) Fields 2 and 3 are in the wrong order. (3) The provenance line can now say the checker also confirmed V2 a2 and V2 D1 a1 on CPU.

초안 원안:

```text
`[2026-09-23 __:__ KST] 정정 — LADDER_C.md 2·3·4·6행의 "checkpoint holds the best-val (epoch N) EMA weights" 는 거짓이다 (review_next P0-1b, V2/V3 부분) | 네 행은 발산으로 멈춘 run 의 체크포인트가 best-val epoch 의 EMA 를 담는다고 적었다. 파일 실측(CPU torch.load): `d2sx_V2_N160000_a1.pt` 는 epoch 118(best 85; @118 val 1.2075), `d2sx_V3_N160000_a1.pt` 는 epoch 62(best 27; @62 val 1.7202), `sx_V2_N160000_D1_a1.pt` 는 epoch 57(best 48; @57 val 1277.08), `d2sx_V2_N160000_a2.pt` 는 epoch 191(best 85; @191 val nan, **EMA 원소 479,489 개 중 479,360 개가 비유한**)이다. 따라서 6행의 "and is intact" 도 거짓이다. 원인은 저장 경로가 매 epoch 덮어쓰기였기 때문이다(P0-1a). 이 넷은 BLER arm 으로 쓰인 적이 없다(EXPERIMENTS 21행 "V2·V3·λ 은 arm 아님") | LADDER_C 는 append-only 라 행을 고치지 않고, 이 항목을 정정 기록으로 삼는다. V2 a1·V3 a1 은 감사(P0-1b)가 확인했고, V2 a2·V2 D1 a1 은 이 초안을 쓰면서 같은 방법으로 확인했다(2차 반박은 거치지 않음) | 이 줄을 지우면 되돌아간다`
```
</details>

<details><summary>근거</summary>

CPU torch.load: d2sx_V2_N160000_a1.pt epoch=118 best_epoch=85 best_val=3.653966e-01, last hist val 1.2075026; d2sx_V3_N160000_a1.pt epoch=62 best=27 best_val=6.919234e-01, last 1.7202276; sx_V2_N160000_D1_a1.pt epoch=57 best=48 best_val=7.399451e-01, last 1277.0775; d2sx_V2_N160000_a2.pt epoch=191 best=85 best_val=3.569986e-01, last nan, non-finite EMA entries 479360/479489 (torch.isfinite over st['ema']). The other three have 0 non-finite EMA entries. The LADDER_C.md lines 2, 3, 4 and 6 at HEAD contain the quoted 'holds the best-val' clauses (git show HEAD:conf/LADDER_C.md). REVIEW_AUDIT P0-1b covers V2 a1 (118 vs 85) and V3 a1 (62 vs 27). V2 a2 and V2 D1 a1 are my own additional checks.

검증: (위 참조)
</details>

### 1차 검증이 찾은 누락 위치 (→ 2차에서 초안 작성)

<details><summary>원문</summary>

The drafter missed the following places that carry the same wrong wording. All were checked at HEAD cd241b7e; ckpt facts were re-read on CPU.

COST (P0-2a/P0-2b):
(1) conf/code/bench_moduleH.py docstring, lines 3-5 and 12. It still says 'The receiver calls Module H ONCE per outer iteration ... through the identical entry point `prior.denoise_full(q, nu) -> (m, J)` ... this single call IS the complexity difference between the arms' and 'the GMM is b* ... exactly the arm in the BLER tables'. Docstrings may be edited directly. Suggested 3-5: 'Times prior.denoise_full(q, nu) -> (m, J) for both priors (an isotropic microbenchmark).  NOTE (review_next P0-2a/P0-2b, 2026-09-23): the headline GMM arm M-ours-bstar does not call denoise_full; once per outer iteration it calls GMMPriorB.ep_site(G, b, lam_min) (arms.py:36,163; Demo/t2_route_a.py:373-374), so this is NOT the arm-to-arm receiver cost difference.' Suggested 12: append '(N=1e4 fits -> kron K=512; not the K=1024 headline b*)'.

P0-1b (the ckpt was introduced with its best val but evaluated as last-EMA):
(2) NUMBERS_PACKAGE_2026-09-22.md:195 and PAPER_MATERIALS.md:415-416 (§12.3). The DECISIONS entry names both, but no inline note is drafted. Lower priority, same parenthetical: results/jac_spectrum.txt:126, figs/F7_jacspectrum_D1_D2.txt:25-26, and results/d2_gbprime.csv:8. That csv row pairs epoch 1784 with the best val 3.519379e-01; audit P0-1a 반박 flags it.
(3) The D1 half of raw_C is out of scope in the draft. It has 1344 files, meta|stagec_ckpt sx_N160000_D1.pt, epoch 200 against best 136, arms V0/V1/V4, and feeds tables_D1_C. It appears at STATUS:439 ('체크포인트 `ckpt/sx_N160000_D1.pt` (GA/GB/GC/GD 전부 PASS). raw 336개 → `results/tables_D1_C.txt`'), PAPER_MATERIALS:566 (§14) and the figs/F10_bler_D1_confirmatory.txt caption.
(4) raw_supp (112 files, meta|dscore_ckpt d2sx_N10000_a1.pt, 673 against best 653, arm M-ours-dscore) is also out of scope in the draft.

ckpt/M2 (gate verdicts measured on the last-epoch EMA):
(5) STATUS:375-376 ('## C3 결과 — D1 게이트 **통과**', ckpt/sx_N160000_D1.pt) is the primary PASS record and has no note. Suggested: '> **정정 (2026-09-23, review_next ckpt/M2)**: 이 PASS 는 `sx_N160000_D1.pt` 의 마지막 epoch(200) EMA 에서 측정됐다(best 7.398444e-01 @136, @200 val 7.398687e-01; best 가중치 미저장). 661 행 뒤 정정을 볼 것.'
(6) STATUS:1513-1514, the λ=0.01 PASS. 'patience 종료 @200, best val 7.398582e-01 @142' was gated on the @200 EMA, whose val is 7.399352e-01 (gate_D1_L0.01.txt written 17:11:53, after the ckpt at 17:10:19). Suggested: '> **정정 (2026-09-23, review_next ckpt/M2)**: 이 PASS 는 best(@142)가 아니라 @200 EMA(val 7.399352e-01)에서 측정됐다. best 가중치에서의 게이트 값은 측정된 적이 없고 복구할 수 없다.'
(7) Sibling or λ PASS wording in other places:
- STATUS:439 and STATUS:1262 ('D1 형제 `sx_N160000_D1.pt` 가 GA~GD PASS')
- NUMBERS_PACKAGE:187 (D1 gate PASS) and P10 (λ=0.01 PASS)
- docs/EXPERIMENTS.md:21 ('D1 게이트 PASS @N=1.6e5', 'λ=0.01 만 PASS'); the corrected EXPERIMENTS P0-1b note above now covers these
- PAPER_MATERIALS:299, 566, 625, 818, 964 and 976
- captions figs/F12_tp_envelope.txt:48, F14_headline_C2_m3dB.txt:29, F14c_C2_p12dB_max_ratio.txt:26 and F15_gap_robustness.txt:43, whose shared text comes from the hardcoded constant GATE_LINE_PASS at code/figures_stagec2.py:60-62. The audit does not ask for caption notes here, so these are optional.

User-owned spec files (a dated note needs 사용자 승인):
(8) conf/10_SPEC_stageC.md:345 lists the sx_N160000_D1.pt PASS values with no last-EMA qualifier.
(9) conf/10_SPEC_stageC.md:319 says 'DIVERGED 시행의 best 체크포인트는 보존하되'. The four diverged checkpoints did not keep their best weights (see the V2/V3 entry), so this rule was not met. A dated note stating that is needed; do not rewrite the rule.
</details>

---

## 2차 · genie/상한 명칭 (R-10.3, M-10.3a)

### genie-14 · genie-14 — `conf/DECISIONS.md (genie-1 append 항목의 근거 필드) — 원문은 git commit 6ed06139 메시지` genie-1 append(EOF, 104 뒤) 근거 필드 끝에 덧붙임. 원문 = commit 6ed06139 메시지 l.3

- 방식: **DECISIONS append** · ✅ 검증 통과

**원문 (HEAD)**

```text
raw_B16e4k C2 -3 dB 재분석(새 실행 없음): V1 실패 371 = genie 도 실패 72 + 줄일 수 있는 299.
```

**제안 문구**

```text
genie-1 제안 문구의 근거 필드는 '… 같은 항목의 (3)(4)와 제목·결론의 "배제" 문구는 R-10.1/R-10.2 정정에서 따로 다룬다' 로 끝난다. 그 뒤에 다음을 덧붙인다: ' 커밋 6ed06139 메시지 l.3 "V1 실패 371 = genie 도 실패 72 + 줄일 수 있는 299" 도 같은 귀속이다(72 는 못 줄이고 299 만 줄일 수 있다는 뜻). 커밋은 origin/main 에 push 됐고 뒤에 커밋 3개가 있어 고치지 않는다. 이 줄로 읽는다.' 371/72/299 수치는 맞다. 정정 대상은 '줄일 수 있는' 이라는 귀속뿐이다. (선택) tail-loop-7 의 '편집 없음' 문구에 'l.3 은 R-10.3 줄(genie-1)이 담는다' 를 덧붙이면 커밋 메시지 대응표가 l.1·3·5·6·8-9 로 완결된다.
```

<details><summary>근거</summary>

git log -1 --format=%B 6ed06139 | cat -n → l.3 원문 그대로. git branch -r --contains 6ed06139 = origin/main. git log --oneline 6ed06139..HEAD = cd241b7e, 4ad41df9, 54e8047c. 수치: genie-1 재집계와 같다(raw_B16e4k C2 −3 dB 64파일, n=2560, blk_err[:,15]). V1 371 = 동시 72 + V1 단독 299, V1 성공·genie 실패 15. CPU 재확인(scratchpad/genie2/below.py): raw_B16e4k C2 −3 dB 에서 V1 성공·genie 실패 = 15. 15 블록이 '72 는 못 줄인다' 의 블록별 하한 해석을 반박한다(REVIEW_AUDIT R-10.3). tail-loop-7 은 l.1·5·6·8·9 만 다루고 l.3 은 비어 있다.

검증: 없음. `git log -1 --format=%B 6ed06139 | cat -n` 의 l.3 과 글자 그대로 같다. 6ed06139 는 origin/main 에 있고 뒤에 54e8047c·4ad41df9·cd241b7e 가 있다. genie-1 근거 필드는 실제로 '… R-10.1/R-10.2 정정에서 따로 다룬다' 로 끝난다(DRAFT:375). CPU 재집계(raw_B16e4k C2 −3 dB, 64파일, n=2560, blk_err[:,15]): V1 371 = 동시 72 + V1 단독 299, V1 성공·genie 실패 15. '완결' 은 round-1 검증이 짚은 줄 기준이라 문제없다(l.4 는 기술 서술이고 l.10 은 l.9 의 이어짐).
</details>

### genie-15 · genie-15 — `conf/06_SPEC_runner.md` 18 (baseline 표 마지막 행, 19 빈 줄). 노트는 18 뒤에 빈 줄 1개를 넣고 삽입

- 방식: **spec note (사용자 승인 필요)** · ✏️ 검증 수정 반영 (인용 OK · 수치 OK · 문구 X)

**원문 (HEAD)**

```text
| `R6-exactEP` | `exactEP-true` (참 prior 정확 EP, oracle 상한) | 기존 |
```

**제안 문구**

```text
> **정정 제안 (2026-09-23, review_next M-10.3a) — 사용자 승인 필요**: 18행 `R6-exactEP` 의 "oracle 상한" 은 참조 수신기를 bound 로 부른다. R6 은 참 prior GMM site 를 넣은 같은 route_a EP/터보 반복 루프다(`code/arms.py:118-119`). 스스로 반복 의존적이다(D1 C5 −3 dB BLER@1/@2/@8/@16 = 0.961/0.821/0.551/0.505, `results/tables_D1_C.txt:554`). 블록별 하한이 아니다: D1 C5 에서 V0 성공·R6 실패 91 블록(−3/+0/+3 dB 합, `tables_D1_C.txt:1139` 88:91, a:b 규약 :754). 점추정으로도 최저가 아니다: C5 −3 dB 에서 M-ours-bstar 0.502, V0 0.504, R6 0.505(`tables_D1_C.txt:534,537,536`). 이 차이는 유의하지 않다(V0→R6 88:91 p=0.88 `:1139`, bstar→R6 74:76 p=0.93 `:1079`, 둘 다 POWERED). 제안 문구: "| `R6-exactEP` | `exactEP-true` (참 prior 정확 EP = exact-prior EP reference, bound 아님) | 기존 |". arm id·구성·testbed 집합(38행)은 그대로다. DECISIONS [2026-09-23 __:__] 명칭 정정(genie-2)을 참조한다.
```

<details><summary>검증 agent 지적 / 초안 원안</summary>

지적: 인용은 HEAD 18행과 같고 19행은 빈 줄, 20행은 '### 우리 모델' 이다. 수치는 모두 재현된다: tables_D1_C.txt:534 bstar 0.502, :536 R6 0.505, :537 V0 0.504, :554 0.961/0.821/0.551/0.505, :1139 88:91. raw_C D1 C5 −3 dB 실패 수는 R6 1294, bstar 1285, V0/V1 1290, score 1287. 21점 중 R6 실패가 있는 17점의 13점에서 R6 보다 낮은 arm 이 있다. 문구 문제: '이 차이는 유의하지 않다(88:91 p=0.88)' 가 bstar 와 V0 두 차이를 함께 받지만, 88:91 은 V0→R6 검정 하나다. bstar→R6 는 tables_D1_C.txt:1079 의 pooled 74:76 p=0.93(POWERED, :1080)이다. 두 검정을 모두 적어야 한다.

초안 원안:

```text
> **정정 제안 (2026-09-23, review_next M-10.3a) — 사용자 승인 필요**: 18행 `R6-exactEP` 의 "oracle 상한" 은 참조 수신기를 bound 로 부른다. R6 은 참 prior GMM site 를 넣은 같은 route_a EP/터보 반복 루프다(`code/arms.py:118-119`). 스스로 반복 의존적이다(D1 C5 −3 dB BLER@1/@2/@8/@16 = 0.961/0.821/0.551/0.505, `results/tables_D1_C.txt:554`). 블록별 하한이 아니다: D1 C5 에서 V0 성공·R6 실패 91 블록(−3/+0/+3 dB 합, `tables_D1_C.txt:1139` 88:91, a:b 규약 :754). 점추정으로도 최저가 아니다: C5 −3 dB 에서 M-ours-bstar 0.502, V0 0.504, R6 0.505(`tables_D1_C.txt:534,536,537`). 이 차이는 유의하지 않다(88:91 p=0.88). 제안 문구: "| `R6-exactEP` | `exactEP-true` (참 prior 정확 EP = exact-prior EP reference, bound 아님) | 기존 |". arm id·구성·testbed 집합(38행)은 그대로다. DECISIONS [2026-09-23 __:__] 명칭 정정(genie-2)을 참조한다.
```
</details>

<details><summary>근거</summary>

HEAD 06_SPEC_runner.md:18 원문 그대로, 19 빈 줄, 20 '### 우리 모델'. arms.py:119 'arms["R6-exactEP"] = route_a(*a, true_prior.view("eta"), code, Xp, "gmm_site")'. tables_D1_C.txt:534 bstar 0.502, :536 R6 0.505, :537 V0 0.504, :554 R6 BLER@1/@2/@8/@16 0.961/0.821/0.551/0.505, :1139 pooled 88:91 p=0.88. CPU 재집계(scratchpad/genie2/r6.py, raw_C D1): C5 −3 dB R6 실패 1294, bstar 1285, V0/V1 1290, score 1287. D1 21점 중 R6 실패가 있는 17점의 13점에서 R6 보다 점추정 BLER 가 낮은 arm 이 있다(대부분 비유의). genie-2 는 이 위치를 '사용자 승인 필요' 목록에만 넣었다. 문구는 genie-8 의 'exact-prior EP reference' 와 맞춘다.

검증: (위 참조)
</details>

### genie-16 · genie-16 — `conf/10_SPEC_stageC.md` 824 (분석 메뉴 표 중간. 표 끝은 825 A8, 826 빈 줄). 노트는 825 뒤에 빈 줄 1개를 넣고 삽입

- 방식: **spec note (사용자 승인 필요)** · ✏️ 검증 수정 반영 (인용 OK · 수치 OK · 문구 X)

**원문 (HEAD)**

```text
| A7 | genie 까지의 격차 중 메운 비율 | 상한 대비 위치 |
```

**제안 문구**

```text
> **정정 제안 (2026-09-23, review_next M-10.3a) — 사용자 승인 필요**: 824행 A7 의 '왜' 칸 "상한 대비 위치" 는 R5-genie 를 bound 로 부른다. R5-genie 는 같은 route_a 반복 수신기에 참 H 를 넣은 known-channel receiver reference 다(동일 EP detector + BCJR, 참 H; `code/arms.py:117`, `Demo/t2_route_a.py:388-389`). 스스로 반복 의존적이다(BLER@1/@2/@8/@16 = 0.225/0.102/0.043/0.034, `results/tables_D2_B16e4k.txt:92`). C2 −3 dB 에서 V1 성공·genie 실패 15 블록이 있다(`raw_B16e4k`). 제안 문구: "| A7 | genie 까지의 격차 중 메운 비율 | known-channel receiver reference(R5-genie) 대비 위치 — 기술적 서술, bound 아님 |". 메뉴는 동결 그대로이고 항목·계산식도 그대로다. '왜' 칸 명칭만 바꾼다. '격차' 는 기술량으로 성립한다: 측정한 모든 D2 점에서 genie 보다 점추정 BLER@16 이 낮은 arm 은 없다(동률 1곳: `conf/raw` C2 +15 dB M-ours-gmm32, 1/640). 참고: C2 의 arm-대-R5-genie 쌍은 전부 UNDECIDED 라서 A7 수치는 TABLE A 점추정 비율이다(`results/NUMBERS_PACKAGE_2026-09-22.md:632`).
```

<details><summary>검증 agent 지적 / 초안 원안</summary>

지적: 인용은 HEAD 824행과 같다. 표는 816-825, 826 은 빈 줄, 827 은 '## A8 …' 이다. 수치 재현: tables_D2_B16e4k.txt:92 0.225/0.102/0.043/0.034, raw_B16e4k 15. D2 raw 디렉터리 21개 전부(raw, raw_C, raw_B16e4, raw_B16e4k, raw_B1e4lo, raw_B1e4, raw_B1e4x, raw_B1e4s2/s3, raw_B4e4/k/k1, raw_NR16run, raw_supp …)에서 genie 보다 BLER@16 이 낮은 arm 은 없다. 문구 문제 두 가지. (1) '측정한 모든 D2 점에서 genie 점추정 BLER 가 최저' 는 동률 1곳을 가린다: conf/raw C2 +15 dB 에서 M-ours-gmm32 = genie = 1/640(raw_supp 도 같다). '낮은 arm 이 없다' 로 적어야 한다. (2) 'A7 수치는 … 결과 진술로 쓰지 않는다' 는 같은 노트의 '"왜" 칸 명칭만 바꾼다' 와 어긋난다. 동결 메뉴 노트 안에 새 사용 규칙을 넣는 셈이다. 사실 서술(NUMBERS_PACKAGE:632 가 적은 대로 C2 쌍은 UNDECIDED, 수치는 점추정 비율)로 바꾼다.

초안 원안:

```text
> **정정 제안 (2026-09-23, review_next M-10.3a) — 사용자 승인 필요**: 824행 A7 의 '왜' 칸 "상한 대비 위치" 는 R5-genie 를 bound 로 부른다. R5-genie 는 같은 route_a 반복 수신기에 참 H 를 넣은 known-channel receiver reference 다(동일 EP detector + BCJR, 참 H; `code/arms.py:117`, `Demo/t2_route_a.py:388-389`). 스스로 반복 의존적이다(BLER@1/@2/@8/@16 = 0.225/0.102/0.043/0.034, `results/tables_D2_B16e4k.txt:92`). C2 −3 dB 에서 V1 성공·genie 실패 15 블록이 있다(`raw_B16e4k`). 제안 문구: "| A7 | genie 까지의 격차 중 메운 비율 | known-channel receiver reference(R5-genie) 대비 위치 — 기술적 서술, bound 아님 |". 메뉴는 동결 그대로이고 항목·계산식도 그대로다. '왜' 칸 명칭만 바꾼다. 격차는 기술량으로 정의된다(측정한 모든 D2 점에서 genie 점추정 BLER 가 최저). A7 수치는 TABLE A 점추정 서술이며 결과 진술로 쓰지 않는다(`results/NUMBERS_PACKAGE_2026-09-22.md:632`).
```
</details>

<details><summary>근거</summary>

HEAD 10_SPEC_stageC.md:824 원문 그대로. 표 816-825, 826 빈 줄, 827 '## A8 에 대한 사전 경고'. 812 '분석 메뉴 (여기서 동결 …)' 라서 노트는 명칭만 다루고 항목은 건드리지 않는다. 수치: tables_D2_B16e4k.txt:92. raw_B16e4k C2 −3 dB V1 성공·genie 실패 15(scratchpad/genie2/below.py). 같은 스크립트로 raw, raw_C, raw_B16e4, raw_B16e4k, raw_B1e4lo 의 모든 D2 점을 보면 genie 보다 BLER@16 이 낮은 arm 이 없다. 따라서 '격차' 는 성립하고 바뀌는 것은 'bound' 명칭뿐이다. NUMBERS_PACKAGE:632 는 C2 arm-대-R5 쌍이 전부 UNDECIDED 라고 적는다. 동일 명명의 F14 캡션 'closes 47% of the GMM-to-genie gap (A7)' 에는 bound 표현이 없어 대상이 아니다.

검증: (위 참조)
</details>

### genie-17 · genie-17 — `conf/results/NUMBERS_PACKAGE_2026-09-22.md` 632 (§(F) DO NOT WRITE 목록 항목 5). 넣는다면 632 뒤, 633 '6.' 앞에 목록 안으로 3칸 들여쓰기

- 방식: **other** · ✅ 검증 통과

**원문 (HEAD)**

```text
5. ❌ *"V1 closes 80.1 % (or 85.3 %) of the gap to the genie bound"* stated as a result. — **Every arm-vs-R5-genie pair on C2 is UNDECIDED** under the pre-registered power guard (2 decision points where 3 are required) in **all three** C2 equal-budget tables **and** in `tables_D2_C.txt`. It is a TABLE A point-estimate description only.
```

**제안 문구**

```text
genie-13(같은 파일 :479)과 같이 처리한다. genie-2 명칭 정정 DECISIONS 줄이 이미 ':632' 를 '이 줄로 읽는다' 목록에 넣었으므로 기본은 그것으로 덮는다. round 1 cost-ckpt-4 처럼 파일에 인라인 주석을 넣는다면 632 뒤에 다음을 넣는다:
   > **정정 (2026-09-23, review_next R-10.3·M-10.3a)**: 항목 5 의 철회·금지 판정은 그대로다. 바뀌는 것은 인용 속 "the genie bound" 라는 명칭뿐이다. R5-genie 는 known-channel receiver reference(동일 EP detector + BCJR, 참 H; `code/arms.py:117`)이며 bound 가 아니다. C2 −3 dB 에서 V1 성공·genie 실패 15 블록이 있다(`raw_B16e4k`·`raw_C` `blk_err[:,15]`, n=2560). 80.1 %·85.3 % 수치와 UNDECIDED 판정은 그대로다.
```

<details><summary>근거</summary>

HEAD NUMBERS_PACKAGE_2026-09-22.md:632 원문 그대로, 633 = '6. ❌ …'. :535 가 80.1 % 를 TABLE A 점추정 비율로 이미 규정했다. 철회 자체는 문제없고(REVIEW_AUDIT R-10.3 'Mitigating context'), 남은 문제는 명칭뿐이다. 15 블록은 raw_B16e4k·raw_C 두 곳에서 모두 재확인했다(scratchpad/genie2/below.py). round 1 은 NUMBERS_PACKAGE 에 인라인 주석을 준 적이 있다(cost-ckpt-4, method other). 같은 그룹 genie-13 은 :479 를 DECISIONS 목록으로만 덮고 인라인 주석은 선택으로 두었다. 일관성을 위해 이 항목도 같은 형태로 둔다.

검증: 없음. 인용은 HEAD 632행과 같고 633 은 '6. ❌ …' 이다. genie-2 목록에 이미 ':632' 가 있다(DRAFT:398). 15 블록은 raw_B16e4k·raw_C 두 곳 모두에서 재현된다(동시 72, V1 단독 299, genie 단독 15). 80.1 % 가 TABLE A 점추정 비율이라는 점은 :535 와 맞는다. 같은 파일 :479 를 다룬 genie-13 과 같은 형태(기본은 DECISIONS 목록, 인라인은 적용 가능한 문안으로 제시)라 그룹 안에서 일관된다. 3칸 들여쓴 blockquote 는 목록 항목 5 안에 들어간다.
</details>

### genie-18 · genie-18 — `conf/results/jac_spectrum.txt` 45 (READING 1 끝 문장, 44-45)

- 방식: **other** · ✏️ 검증 수정 반영 (인용 OK · 수치 OK · 문구 X)

**원문 (HEAD)**

```text
the learned arm ties the exact-score oracle and the exact-EP bound.
```

**제안 문구**

```text
reference only. 파일은 편집하지 않는다(results/*.txt 보관 산출물이다. `conf/code/jac_spectrum.py` 는 수치 표만 출력하고 READING 문단을 만드는 코드는 없다). genie-2 명칭 정정 DECISIONS 줄이 이미 'results/jac_spectrum.txt:45 ("exact-EP bound")' 를 '이 줄로 읽는다' 목록에 넣었으므로 추가 조치는 없다. 읽는 법: "the exact-EP bound" = R6-exactEP = exact-prior EP reference 다(참 prior GMM site 를 넣은 같은 route_a 루프, `code/arms.py:119`). bound 가 아니다(D1 C5 V0 성공·R6 실패 91 블록, `tables_D1_C.txt:1139`). 같은 문장 'ties' 의 검정력 문제는 NUMBERS_PACKAGE:479·564(R10)가 따로 다루며 이 명칭 정정의 범위 밖이다.
```

<details><summary>검증 agent 지적 / 초안 원안</summary>

지적: 인용은 HEAD 45행과 같다(4칸 들여쓰기, 44-45가 한 문장). 헤더 :1-2(2026-09-21 16:55, 77ac40c)와 :14 가 맞다. 'exact-EP bound' 는 HEAD 에서 이 줄과 NUMBERS_PACKAGE:479 두 곳뿐이다. 91 은 tables_D1_C.txt:1139 와 같다. 사소한 사실 오류 하나: '생성기가 없다' 는 틀렸다. `conf/code/jac_spectrum.py` 가 HEAD 에 있고 헤더 :14 가 그 파일을 가리킨다. 다만 그 파일은 수치 표만 print 하고 READING 문단은 만들지 않는다. 'READING 문단을 만드는 코드가 없다' 로 고쳐야 한다. reference only 처리 자체는 관례에 맞다.

초안 원안:

```text
reference only. 파일은 편집하지 않는다(results/*.txt 보관 산출물이고 생성기가 없다). genie-2 명칭 정정 DECISIONS 줄이 이미 'results/jac_spectrum.txt:45 ("exact-EP bound")' 를 '이 줄로 읽는다' 목록에 넣었으므로 추가 조치는 없다. 읽는 법: "the exact-EP bound" = R6-exactEP = exact-prior EP reference 다(참 prior GMM site 를 넣은 같은 route_a 루프, `code/arms.py:119`). bound 가 아니다(D1 C5 V0 성공·R6 실패 91 블록, `tables_D1_C.txt:1139`). 같은 문장 'ties' 의 검정력 문제는 NUMBERS_PACKAGE:479·564(R10)가 따로 다루며 이 명칭 정정의 범위 밖이다.
```
</details>

<details><summary>근거</summary>

HEAD jac_spectrum.txt:44-45 원문 그대로(4칸 들여쓰기). 파일 헤더 :1-2 = 2026-09-21 16:55, commit 77ac40c. :14 'conf/code/jac_spectrum.py (new)'. git grep 'exact-EP\|ties the exact' HEAD -- conf/code 는 결과가 없다(READING 문단을 코드가 만들지 않는다). 'exact-EP bound' 는 HEAD 에서 이 줄과 NUMBERS_PACKAGE:479 두 곳뿐이다. 과업 관례: results/*.txt 는 편집하지 않는다. round 1 이 이 파일을 편집 대상으로 다룬 적도 없다.

검증: (위 참조)
</details>

### genie-19 · genie-19 — `conf/code/figures.py` 35 (STYLE dict, F3_bler_{D1,D2} 범례)

- 방식: **caption/generator note** · ✏️ 검증 수정 반영 (인용 OK · 수치 X · 문구 OK)

**원문 (HEAD)**

```text
"R5-genie":     ("R5  genie CSI (lower bound)",                  "k", "*", "-."),
```

**제안 문구**

```text
사용자 승인 뒤에만 적용한다(genie-2 가 생성기 출력 문자열을 사용자 승인 사항으로 두었다). 이미 생성된 F3_bler_D1/D2 PNG·PDF 는 재생성하지 않는다. 옛 범례는 DECISIONS [2026-09-23 __:__] 명칭 정정(genie-2)으로 읽는다. 문구는 genie-10(figures_stagec.py:531·642)과 같게 맞춘다.
old:     "R5-genie":     ("R5  genie CSI (lower bound)",                  "k", "*", "-."),
new:     "R5-genie":     ("R5  genie CSI (known-H reference)",            "k", "*", "-."),
(열 정렬 유지: 두 줄 길이가 같아 "k" 는 같은 자리(1 기준 70열)에 온다. 색·마커·선·ORDER 는 그대로 둔다.)
```

<details><summary>검증 agent 지적 / 초안 원안</summary>

지적: 인용은 HEAD 35행과 같다. :37 ORDER, :62 STYLE[a], :76 savefig 가 맞고, F3 은 load_raw 기본 root conf/raw(analysis.py:56 RAW, :118)를 쓴다. conf/raw D2 C2 −3 dB(64파일, n=2560)에서 genie 실패·gmm32 성공 9, genie 실패·bstar 성공 9 가 재현된다(동시 실패 각 78). conf/raw 에 genie 보다 낮은 arm 은 없다(C2 +15 dB gmm32 1/640 동률만 있다). 새 문자열은 옛 줄과 길이가 같다(85자). 수치 문제는 열 번호 하나다: "k" 는 1 기준 70열이다. 초안의 '69' 는 0 기준이라 편집기 표시와 어긋난다.

초안 원안:

```text
사용자 승인 뒤에만 적용한다(genie-2 가 생성기 출력 문자열을 사용자 승인 사항으로 두었다). 이미 생성된 F3_bler_D1/D2 PNG·PDF 는 재생성하지 않는다. 옛 범례는 DECISIONS [2026-09-23 __:__] 명칭 정정(genie-2)으로 읽는다. 문구는 genie-10(figures_stagec.py:531·642)과 같게 맞춘다.
old:     "R5-genie":     ("R5  genie CSI (lower bound)",                  "k", "*", "-."),
new:     "R5-genie":     ("R5  genie CSI (known-H reference)",            "k", "*", "-."),
(열 정렬 유지: "k" 는 같은 열 69에 온다. 색·마커·선·ORDER 는 그대로 둔다.)
```
</details>

<details><summary>근거</summary>

HEAD figures.py:35 원문 그대로. :37 ORDER 끝이 R5-genie 이고 :62 STYLE[a] 로 범례에 쓰인다. :76 savefig F3_bler_{tb}. F3 은 AN.load_raw(tb) 기본 root = conf/raw 를 쓴다(analysis.py:56). CPU 재집계(scratchpad/genie2/f3.py): conf/raw D2 C2 −3 dB 64파일 n=2560 에서 M-ours-gmm32 성공·genie 실패 9, M-ours-bstar 9. 두 arm 모두 F3 에 그려진다. 블록별 하한이 아니다. 과잉 정정 방지: conf/raw 의 모든 점에서 genie 보다 BLER@16 이 낮은 arm 은 없다(below.py). 그림의 곡선 순서는 사실이고 바뀌는 것은 'bound' 명칭뿐이다. genie 자체도 반복 의존적이다(0.225/0.102/0.043/0.034, tables_D2_B16e4k.txt:92).

검증: (위 참조)
</details>

### genie-20 · genie-20 — `conf/code/figure_f14.py` 46 (ARMS 목록, F14_headline_C2_m3dB / F14b_C2_m6dB_max_absolute_gap / F14c_C2_p12dB_max_ratio 범례)

- 방식: **caption/generator note** · ✏️ 검증 수정 반영 (인용 OK · 수치 X · 문구 OK)

**원문 (HEAD)**

```text
("R5-genie",            "genie CSI (lower bound)",                "k",          "*"),
```

**제안 문구**

```text
사용자 승인 뒤에만 적용한다(genie-2). F14·F14b·F14c 의 PNG/PDF/txt 는 재생성하지 않는다. 문구는 genie-10 과 같게 맞춘다.
old:     ("R5-genie",            "genie CSI (lower bound)",                "k",          "*"),
new:     ("R5-genie",            "genie CSI (known-H reference)",          "k",          "*"),
(열 정렬 유지: 두 줄 길이가 같아 "k" 는 같은 자리(1 기준 71열)에 온다. 이 파일은 cost-ckpt-9·10 에서도 docstring/캡션 정정 대상이다. 적용할 때 한 커밋으로 묶어도 된다.)
```

<details><summary>검증 agent 지적 / 초안 원안</summary>

지적: 인용은 HEAD 46행과 같다. :101/:122/:145 에서 ARMS 를 돌고 :191-193 에서 범례를 만든다. 캡션 raw 는 F14 raw_B16e4k, F14b raw_B1e4lo, F14c raw_B16e4k(각 txt :3)다. 재현: raw_B16e4k C2 −3 dB V1 성공·genie 실패 15, raw_B1e4lo C2 −6 dB 14(동시 506, V1 1538, genie 520). 두 raw 모두 genie 보다 낮은 arm 이 없다. F14 캡션 'closes 47% of the GMM-to-genie gap (A7)'(txt:8)에는 bound 표현이 없다. 수치 문제는 열 번호 하나다: "k" 는 1 기준 71열이고, '70' 은 0 기준이다(두 줄 모두 89자).

초안 원안:

```text
사용자 승인 뒤에만 적용한다(genie-2). F14·F14b·F14c 의 PNG/PDF/txt 는 재생성하지 않는다. 문구는 genie-10 과 같게 맞춘다.
old:     ("R5-genie",            "genie CSI (lower bound)",                "k",          "*"),
new:     ("R5-genie",            "genie CSI (known-H reference)",          "k",          "*"),
(열 정렬 유지: "k" 는 열 70. 이 파일은 cost-ckpt-9·10 에서도 docstring/캡션 정정 대상이다. 적용할 때 한 커밋으로 묶어도 된다.)
```
</details>

<details><summary>근거</summary>

HEAD figure_f14.py:46 원문 그대로. :101/:122/:145 에서 ARMS 로 그리고 :191-193 에서 범례를 만든다. 캡션 txt 의 raw: F14 = raw_B16e4k, F14b = raw_B1e4lo, F14c = raw_B16e4k. CPU 재집계(below.py): raw_B16e4k C2 −3 dB 에서 V1 성공·genie 실패 15, raw_B1e4lo C2 −6 dB 에서 14. 블록별 하한이 아니다. 두 raw 의 모든 점에서 genie 보다 BLER@16 이 낮은 arm 은 없다. 따라서 명칭만 바꾼다. F14 캡션 'closes 47% of the GMM-to-genie gap (A7)' 에는 bound 표현이 없어 대상이 아니다.

검증: (위 참조)
</details>

### genie-21 · genie-21 — `conf/code/figures_stagec2.py` 69 (ST dict, F12_tp_envelope 범례. ST 는 :145·:229 F12 에서만 쓰인다)

- 방식: **caption/generator note** · ✏️ 검증 수정 반영 (인용 OK · 수치 X · 문구 OK)

**원문 (HEAD)**

```text
"R5-genie":            ("genie CSI (lower bound)",                  "k",          "*", "-."),
```

**제안 문구**

```text
사용자 승인 뒤에만 적용한다(genie-2). F12_tp_envelope PNG/PDF/txt 는 재생성하지 않는다. 문구는 genie-10 과 같게 맞춘다.
old:     "R5-genie":            ("genie CSI (lower bound)",                  "k",          "*", "-."),
new:     "R5-genie":            ("genie CSI (known-H reference)",            "k",          "*", "-."),
(열 정렬 유지: 두 줄 길이가 같아 "k" 는 같은 자리(1 기준 73열)에 온다. 같은 파일 :246 F12 캡션 제목은 testbed-gate-22 가 따로 다룬다. figures_stagec.py:531(F10)·:642(F11) 범례는 genie-10 에 이미 있다.)
```

<details><summary>검증 agent 지적 / 초안 원안</summary>

지적: 인용은 HEAD 69행과 같다. ST(:64)는 :145·:229 에서만 쓰이고 둘 다 fig12 안이다(:245 _save F12_tp_envelope). fig13 은 ST 를 쓰지 않는다. F12 raw 는 CELLS(:71)에 따라 raw_B16e4 다. 모듈 docstring :19-20 은 raw_B1e4x/raw_B1e4 라고 적지만 옛 문구이고 CELLS 가 실제 값이다. 재현: raw_B16e4 C2 −3 dB V1 성공·genie 실패 15, C5 0 dB 8. raw_B16e4 의 21점에서 genie 보다 낮은 arm 은 없다. testbed-gate-22 가 :246 을 다룬다(DRAFT:1320). 수치 문제는 열 번호 하나다: "k" 는 1 기준 73열이고, '72' 는 0 기준이다(두 줄 모두 97자).

초안 원안:

```text
사용자 승인 뒤에만 적용한다(genie-2). F12_tp_envelope PNG/PDF/txt 는 재생성하지 않는다. 문구는 genie-10 과 같게 맞춘다.
old:     "R5-genie":            ("genie CSI (lower bound)",                  "k",          "*", "-."),
new:     "R5-genie":            ("genie CSI (known-H reference)",            "k",          "*", "-."),
(열 정렬 유지: "k" 는 열 72. 같은 파일 :246 F12 캡션 제목은 testbed-gate-22 가 따로 다룬다. figures_stagec.py:531(F10)·:642(F11) 범례는 genie-10 에 이미 있다.)
```
</details>

<details><summary>근거</summary>

HEAD figures_stagec2.py:69 원문 그대로. :64 ST 정의 뒤 :145 'for arm, (lab, col, mk, ls) in ST.items()' 로 그리고 :229 범례를 만든다. 둘 다 F12 함수 안이다(:245 _save F12_tp_envelope). F13(:391)은 ST 를 쓰지 않는다. F12 raw = raw_B16e4(:71 CELLS). CPU 재집계(below.py): raw_B16e4 C2 −3 dB 에서 V1 성공·genie 실패 15, C5 0 dB 에서 V1 8. raw_B16e4 의 모든 점에서 genie 보다 BLER@16 이 낮은 arm 은 없다. 명칭만 바꾸고 곡선 순서 서술은 유지한다.

검증: (위 참조)
</details>

### genie-22 · genie-22 — `conf/code/analysis.py` 90-91 (_pool docstring)

- 방식: **docstring edit** · ✅ 검증 통과

**원문 (HEAD)**

```text
"""Arm order of the tables: the pre-registered set with the Stage C arms slotted in just above the
    bound arm (R6-exactEP / R5-genie), which stays last."""
```

**제안 문구**

```text
동작 불변 docstring 교체:
old:
    """Arm order of the tables: the pre-registered set with the Stage C arms slotted in just above the
    bound arm (R6-exactEP / R5-genie), which stays last."""
new:
    """Arm order of the tables: the pre-registered set with the Stage C arms slotted in just above the
    last arm, R5-genie (known-channel receiver reference, not a bound), which stays last; on D1
    R6-exactEP keeps its place above the Stage C arms."""
검증 agent 의 최소안 'bound arm (R6-exactEP / R5-genie)' → 'reference arm (R6-exactEP / R5-genie)' 도 가능하다. 다만 최소안은 'D1 에서 R6 이 마지막' 이라는 옛 docstring 의 사실 오류를 그대로 남긴다.
```

<details><summary>근거</summary>

HEAD analysis.py:90-91 원문 그대로. :92-93 'p = list(ARMS[testbed]); return p[:-1] + list(STAGEC_ARMS) + p[-1:]'. :64-65 ARMS["D1"] 끝은 (..., "R6-exactEP", "R5-genie"), :66-67 ARMS["D2"] 끝은 "R5-genie". 따라서 두 testbed 모두 마지막은 R5-genie 하나이고 D1 의 R6 은 Stage C arm 위에 남는다. 산출물로 확인: tables_D1_C.txt:536 R6-exactEP, :537-540 V0/V1/V4/bstar-scalar, :541 R5-genie. 반환값에는 영향이 없다(문자열만 바뀐다).

검증: 없음. 인용은 HEAD 90-91행과 같다. :92-93 은 p[:-1] + STAGEC + p[-1:], :64-67 ARMS 는 D1 끝이 (…, R6-exactEP, R5-genie), D2 끝이 R5-genie 다. tables_D1_C.txt 에서 :536 R6, :537-540 Stage C, :541 R5 로 확인했다. 새 docstring 은 사실에 맞고 동작은 그대로다. 참고: 같은 파일 :380(pair_list docstring 'anchor the BOUND')과 :388(주석 '# headroom: …')도 같은 명명인데 round 1·2 어디에도 없다(missing 참조). 이 항목에 묶어 적용하면 된다.
</details>

### genie-23 · genie-23 — `N/A` N/A

- 방식: **other** · ✏️ 검증 수정 반영 (인용 X · 수치 OK · 문구 X)

**원문 (HEAD)**

```text
N/A
```

**제안 문구**

```text
사용자 판단 대상 목록 (정정 초안에 넣지 않음): (a) M-ours-score 를 상한으로 부른 곳 — 00_GOAL.md:110 '정확 score = 학습 score의 상한. **계측기**', 03_SPEC_ourmodel.md:13 '학습 score의 **상한이자 품질 게이트의 기준**', 03_SPEC_ourmodel.md:48 'oracle 상한 = 게이트 기준', 08_SPEC_analysis.md:34 'oracle 상한. 계측기이지 주장 아님', 10_SPEC_stageC.md:348-349 '정확 score 를 같은 인터페이스에 넣었을 때의 상한이며, 학습 prior 가 그 상한에 얼마나 못 미치는지를 보여야 한다', DECISIONS.md:26 '…score 인터페이스의 oracle 상한이 사라진다…'. M-ours-score 도 같은 route_a 루프다(arms.py:165 route_a(*a, true_prior, code, Xp, "score", clip="eta")). 참고로 raw_C D1 C5 −3 dB 에서 M-ours-bstar 실패 1285 < M-ours-score 1287 이다(쌍별 34:36 p≈0.90, CPU 재집계, 출하 표에는 없는 쌍). (b) conf/ 이전 옛 로그 — docs/handoff/T2_session5_handoff_2026-09-18.md:41 '`exactEP-true`(상한)', docs/logs/decision_log.md:222 'R-A ≡ `exactEP_pf` — 즉 **R-A의 BLER 상한은 이미 측정되어 있음**'. (c) 같은 글자지만 뜻이 다른 것 (대상 아님): 동결 σ 격자 상한(10_SPEC_stageC.md:710-771·822, STATUS.md:1130), 'upper bounds K/T'(tables_D1*/D2*, analysis.py:474), T2c '(상한)−(하한)'(05_SPEC_testbed_D2.md:37, d2.py:70·274), runner.py:71, STATUS.md:1246 '4.6× 는 학습 arm 의 상한'(복잡도 그룹 P0-2b 소관).
```

<details><summary>검증 agent 지적 / 초안 원안</summary>

지적: (1) 인용 오류: docs/logs/decision_log.md:222 를 '**R-A의 BLER 상한은 이미 측정되어 있음**(… `exactEP_pf` …)' 로 적었다. 실제 괄호 안은 'exp_0921 C: …' 이고 `exactEP_pf` 는 앞에 온다. 원문은 'R-A ≡ `exactEP_pf` — 즉 **R-A의 BLER 상한은 이미 측정되어 있음**' 이다. 나머지 인용(00_GOAL:110, 03_SPEC:13·48, 08_SPEC:34, DECISIONS:26, 10_SPEC:348-349, handoff:41, STATUS:1130·1246, analysis.py:474, d2.py:70·274, runner.py:71)은 HEAD 와 같다. round-1 목록 위치 DRAFT:740-743 도 맞다. (2) 'bstar 1285 < score 1287 이다(비유의)' 는 수치는 맞지만, 이 쌍은 출하된 표에 없다(pair_list 에 bstar↔score 가 없다). CPU 재집계로 34:36, p≈0.90 을 확인했으니 그 출처를 적는다. (3) (c) 목록에 같은 범주인 05_SPEC_testbed_D2.md:37 '(상한)−(하한)'(T2c, d2.py 와 같은 것)과 10_SPEC_stageC.md:822 A5 '동결 격자 상한' 이 빠졌다. 710-771 범위 밖이다.

초안 원안:

```text
사용자 판단 대상 목록 (정정 초안에 넣지 않음): (a) M-ours-score 를 상한으로 부른 곳 — 00_GOAL.md:110 '정확 score = 학습 score의 상한. **계측기**', 03_SPEC_ourmodel.md:48 'oracle 상한 = 게이트 기준', 08_SPEC_analysis.md:34 'oracle 상한. 계측기이지 주장 아님', DECISIONS.md:26 '…score 인터페이스의 oracle 상한이 사라진다…'. 같은 범주의 추가 발견: 03_SPEC_ourmodel.md:13 '학습 score의 **상한이자 품질 게이트의 기준**', 10_SPEC_stageC.md:348-349 '정확 score 를 같은 인터페이스에 넣었을 때의 상한이며, 학습 prior 가 그 상한에 얼마나 못 미치는지를 보여야 한다'. M-ours-score 도 같은 route_a 루프다(arms.py:165 route_a(*a, true_prior, code, Xp, "score", clip="eta")). 참고로 raw_C D1 C5 −3 dB 에서 M-ours-bstar 실패 1285 < M-ours-score 1287 이다(비유의). (b) conf/ 이전 옛 로그 — docs/handoff/T2_session5_handoff_2026-09-18.md:41 '`exactEP-true`(상한)', docs/logs/decision_log.md:222 '**R-A의 BLER 상한은 이미 측정되어 있음**(… `exactEP_pf` …)'. (c) 같은 글자지만 뜻이 다른 것 (대상 아님): 동결 σ 격자 상한(10_SPEC_stageC.md:710-771, STATUS.md:1130), 'upper bounds K/T'(tables_D1*/D2*, analysis.py:474), d2.py:70·274 T2c, runner.py:71, STATUS.md:1246 '4.6× 는 학습 arm 의 상한'(복잡도 그룹 P0-2b 소관).
```
</details>

<details><summary>근거</summary>

round-1 검증 agent 의 'Related wording the audit does not cover' 목록(RECORD_CORRECTIONS_DRAFT.md:740-743)에 git grep -n '상한\|headroom' HEAD -- 'conf/*.md' 결과를 더했다. 이 grep 에서 03_SPEC:13 과 10_SPEC:348-349 가 새로 나왔다. 각 인용은 git show HEAD:<path> 로 원문 그대로임을 확인했다. M-ours-score 는 audit R-10.3/M-10.3a 위치 목록에 없는 arm 이라 범위 밖이다. genie-13 근거도 '00_GOAL:110·DECISIONS:26 의 oracle 상한(M-ours-score)은 다른 arm 이라 범위 밖' 이라고 적었다.

검증: (위 참조)
</details>

---

## 2차 · D2 testbed 서술·게이트 표현 (R-5.2, M-5.2a, G-1.2)

### testbed-gate-24 · testbed-gate-24 — `conf/DECISIONS.md` 23 (정정 대상, append-only). 새 행 불필요: testbed-gate-9 검증 수정본(M-5.2a DECISIONS 행)에 이미 들어 있음

- 방식: **DECISIONS append** · ✏️ 검증 수정 반영 (인용 OK · 수치 OK · 문구 X)

**원문 (HEAD)**

```text
23: `[2026-09-20 12:35 KST] D2 의 S2 섹터가 D1 의 prior S 와 다른 각도 규약 | 05_SPEC §1 문자 그대로 물리각 ±pi/3 (표준 120도 섹터) 로 둔다. 이는 D1 의 prior **P** 규약과 같고 prior S(전기각 ±pi/3 = 물리각 ±19.5도)와는 다르다 | 05_SPEC 은 theta/phi 를 AoA/AoD(물리각)로 쓰고 "섹터 ±pi/3" 라 했으며, D2 선택 근거가 "물리적으로 표준"이므로 표준 120도 섹터가 맞는 읽기다. 결과: sin(±60도)=±0.866 이라 전기각의 87%를 덮어 앙상블 공분산이 거의 백색이 된다(측정 erank(Rt)=3.877/4). 이것은 물리의 귀결이지 GMM 을 불리하게 만든 것이 아니며, T2b 가 DFT 파일럿을 지시하고 T2c 가 교차-Tp goodput 으로 읽으라고 지시하는 근거가 된다 | d2.ANGLE_RANGE`
```

**제안 문구**

```text
(method: other. DECISIONS 에 새 행을 붙이지 않는 확인 항목이다.) append 행을 따로 두지 않는다. testbed-gate-9(M-5.2a 정정 행) 검증 수정본이 이미 이 행을 짚는다. 적용할 때는 그 수정본에 다음 구절이 빠지지 않았는지만 확인한다: "이 파일 23행([2026-09-20 12:35 KST])의 근거 중 "D2 선택 근거가 "물리적으로 표준"이므로" 도 같은 문구라 이 행으로 대체한다. 그 행의 선택(S2 = 물리각 ±π/3)은 바꾸지 않는다 — 같은 행의 첫 근거(05_SPEC 이 θ/φ 를 AoA/AoD 물리각으로 쓰고 "섹터 ±pi/3" 라 함)는 이 정정과 무관하다". 같은 행의 '표준 120도 섹터'(섹터 폭의 이름)와 '이것은 물리의 귀결이지 GMM 을 불리하게 만든 것이 아니며'(±60° 섹터 → 거의 백색 공분산, erank 3.877/4)는 섹터 선택의 결과를 말할 뿐 D2 를 표준 채널이라 부르지 않으므로 정정하지 않는다. 01_RULES:77 노트(testbed-gate-4 검증 수정본)도 이 행을 적는다.
```

<details><summary>검증 agent 지적 / 초안 원안</summary>

지적: 인용(23행)은 글자 그대로 맞다. 05_SPEC:16 인용과 testbed-gate-4/-9 검증 수정본 인용도 맞다. 내용 판단(S2 선택은 두고 '물리적으로 표준' 근거만 대체, '표준 120도 섹터'·'물리의 귀결'은 정정하지 않음)도 맞다. 문제는 방식 하나다. method 가 'DECISIONS append' 인데 append 할 행이 없다. testbed-gate-9 를 확인만 하는 항목이다. 적용 스크립트가 proposed_text 를 DECISIONS 한 줄로 붙일 위험이 있으므로 method 는 'other' 여야 한다.

초안 원안:

```text
append 행을 따로 두지 않는다. testbed-gate-9(M-5.2a 정정 행) 검증 수정본이 이미 이 행을 짚으므로, 적용할 때 그 수정본의 다음 구절이 빠지지 않았는지만 확인한다: "이 파일 23행([2026-09-20 12:35 KST])의 근거 중 "D2 선택 근거가 "물리적으로 표준"이므로" 도 같은 문구라 이 행으로 대체한다. 그 행의 선택(S2 = 물리각 ±π/3)은 바꾸지 않는다 — 같은 행의 첫 근거(05_SPEC 이 θ/φ 를 AoA/AoD 물리각으로 쓰고 "섹터 ±pi/3" 라 함)는 이 정정과 무관하다". 같은 행의 '표준 120도 섹터'(섹터 폭의 이름)와 '이것은 물리의 귀결이지 GMM 을 불리하게 만든 것이 아니며'(±60° 섹터 → 거의 백색 공분산, erank 3.877/4)는 섹터 선택의 결과를 말할 뿐 D2 를 표준 채널이라 부르지 않는다. 그래서 정정하지 않는다(과잉 정정 방지). 01_RULES:77 노트(testbed-gate-4 검증 수정본)도 이 행을 적는다.
```
</details>

<details><summary>근거</summary>

git show HEAD:conf/DECISIONS.md l.23 글자 그대로. 05_SPEC_testbed_D2.md:16 'AoA/AoD θ,φ | 연속 균등 (격자 없음). 전 범위 판 U2, 섹터 ±π/3 판 S2' → S2 선택의 첫 근거는 05_SPEC 자체에서 성립. 초안 testbed-gate-9 검증 수정본과 testbed-gate-4 검증 수정본이 이미 DECISIONS:23 을 인용함(RECORD_CORRECTIONS_DRAFT.md testbed-gate-4/-9). grep -nE 'physically standard|물리적으로 표준' HEAD -- conf 결과에 DECISIONS:23 포함.

검증: (위 참조)
</details>

### testbed-gate-25 · testbed-gate-25 — `conf/10_SPEC_stageC.md` 836-839 (D3 저널 항목). 노트는 839행 뒤, 같은 목록 항목의 들여쓴 인용으로 (840행 다음 항목 앞)

- 방식: **other** · ✅ 검증 통과

**원문 (HEAD)**

```text
836: - **D3 — 조건부 가우시안 형제 testbed.** D2 는 |α_l| 이 결정적이라 가우시안 혼합이 오설정되는
837:   구조다(`05_SPEC_testbed_D2.md` §1 이 스스로 밝힌다). α_l ~ CN(0,p_l) 로 한 줄만 바꾼 D3 에서
838:   **GMM 이 이기거나 비기는 것이 예상되며, 그것이 나와야** "학습 prior 는 혼합모형이 오설정되는
839:   곳에서 이긴다" 는 더 강한 주장이 된다. 컨퍼런스 범위 밖.
```

**제안 문구**

```text
optional (경계, 선택. 사용자 승인 필요). 839행 뒤에 들여쓴 인용으로:
  > **노트 (2026-09-23, review_next R-5.2 / M-5.2a) — 사용자 승인 필요, 선택.** 이 항목은 D3(α_l ~ CN(0,p_l))에서 혼합모형이 제대로 지정된다는 뜻으로 읽힐 수 있다. 한 줄만 바꾸면 각도는 D2 와 같이 연속 균등이다(`05_SPEC_testbed_D2.md:16`). 그러면 (L, 각도) 조건부 H 는 Gaussian 이지만 앙상블은 연속 혼합이고, 유한 K GMM 은 여전히 근사다. correctly specified GMM arm 은 참 prior 를 격자 GMM 으로 정의한 D1 뿐이다(`05_SPEC_testbed_D2.md:3`). 읽는 법: "α_l ~ CN(0,p_l) 로 한 줄만 바꾼 D3 에서는 조건부 Gaussian 성질이 회복된다(각도가 연속이라 유한 K GMM 은 여전히 근사다). 거기서 GMM 이 이기거나 비기는 것이 예상되며, …". 예측 자체와 '컨퍼런스 범위 밖' 지위는 바꾸지 않는다.
적용하면 R-5.2 DECISIONS 행(testbed-gate-3) 선택 필드에 '10_SPEC_stageC.md:836-839 에도 노트 제안(선택)' 한 구절을 더한다.
```

<details><summary>근거</summary>

git show HEAD:conf/10_SPEC_stageC.md l.836-839 (§'저널로 갈 때 추가로 필요한 것', l.834). 05_SPEC_testbed_D2.md:16 각도 연속 균등(격자 없음), :17 α_ℓ=√p_ℓ e^{jψ_ℓ}, :3 D1 격자 GMM = correctly specified. 수학: 각도·L 이 주어지면 h 는 독립 CN 계수의 선형결합이므로 Gaussian. 각도 분포가 연속이면 혼합 측도도 연속이고, 유한 K 는 근사(감사 R-5.2 반박 검토 'continuous uniform angles give an infinite (continuous) mixture'). 원문은 'correctly specified' 라고 명시하지 않으므로 선택 항목이다(round-1 checker '(경계, 선택)').

검증: 836-839행이 글자 그대로 맞다. 834행은 §'저널로 갈 때…' 제목이고 840행은 다음 항목이다. 05_SPEC:3/:16/:17 인용이 맞고, 감사 R-5.2 반박 검토의 'continuous uniform angles give an infinite (continuous) mixture' 도 실재한다. optional 표시와 method 'other' 도 지시대로다. 수학 서술(조건부 Gaussian, 연속 혼합, 유한 K 근사)이 맞고, 예측과 지위를 두어 과잉 정정이 없다. 사소한 점(수정 불요): 태그 'R-5.2 / M-5.2a' 는 R-5.2 만으로 충분하다. M-5.2a 는 '물리적으로 표준' 항목이다.
</details>

### testbed-gate-26 · testbed-gate-26 — `conf/STATUS.md` 1604-1606 (1602 '## 헤드라인 문장의 최종 형태'). 노트는 1606행 뒤에 빈 줄 1개 + 삽입 (인용 블록과 합쳐지지 않게). 1607행 빈 줄 유지

- 방식: **STATUS inline note** · ✏️ 검증 수정 반영 (인용 OK · 수치 OK · 문구 X)

**원문 (HEAD)**

```text
1604: > **사전 등록 게이트를 통과한 학습 prior 가, 같은 1.6e5 채널 집합으로 적합하고 K 격자를 우도가 오르는
1605: > 한계(K=1024)까지 넓힌 GMM 을 같은 수신기에서 이긴다: C2 −3 dB BLER 0.243 → 0.145 (−40.5%),
1606: > pooled 454:78, p=1.7e-65, n=2560, 3/3 판정점, POWERED.**
```

**제안 문구**

```text
> **정정 (2026-09-23, review_next G-1.2)**: 헤드라인 최종판의 "사전 등록 게이트를 통과한 학습 prior 가" 는 PAPER_MATERIALS:819-820 규칙("게이트를 통과한 D2 모델" 이라 쓰지 않는다)을 어긴 줄임말이다. 이 prior 의 D2 체크포인트 `d2sx_N160000_a1.pt` 에는 게이트 행이 없다(`results/tables_D2_B16e4k.txt:45` `NO GATE RECORD mentions d2sx_N160000_a1.pt -- UNVERIFIED here`). 게이트는 D1 에서만 측정된다(10_SPEC_stageC:126-129). PASS 는 D1 형제 `sx_N160000_D1.pt` 의 행이다(`LADDER_C.md:1`, GB +0.27% / GC 0.0999 / GD 0.0718). 게이트 구절은 이렇게 읽는다: "사전 등록 게이트를 D1 에서 통과한 레시피(D1 형제 `sx_N160000_D1.pt`)로 D2 에 학습한 prior 가, 같은 1.6e5 채널 집합으로 적합한 … GMM 을 같은 수신기에서 이긴다: …". 이 정정은 게이트 구절만 다루고, 문장의 나머지 표현과 수치·검정은 대상이 아니다. 1304행(testbed-gate-14)과 같은 문장의 최종판이다.
```

<details><summary>검증 agent 지적 / 초안 원안</summary>

지적: 1602행 제목과 1604-1606행이 글자 그대로 맞고, 1607행은 빈 줄이다. 확인한 수치와 근거: tables_D2_B16e4k.txt:45 게이트 행 없음, LADDER_C.md:1 GB +0.27% / GC 0.0999 / GD 0.0718 PASS, samplecx_D1.txt:30, 10_SPEC:126-129, PM:819-820. cost-ckpt-15(1591 뒤)와 위치가 겹치지 않는다. 문구 문제 둘. (1) '원고 헤드라인에는 이렇게 쓴다' 는 원고 문장을 지시하는 투다. 같은 문장의 앞선 판을 다룬 testbed-gate-14 는 '게이트 부분만 이렇게 읽는다' 로 썼고, 원고는 사용자가 쓴다. '게이트 구절은 이렇게 읽는다' 로 맞춘다. (2) 읽는 법 인용이 'K 격자를 우도가 오르는 한계(K=1024)까지 넓힌' 을 그대로 다시 싣는다. 이 구절은 감사 밖의 별개 문제다(missing 참조). '수치·검정은 불변이다' 도 그 구절을 승인하는 것처럼 읽힐 수 있다. 그래서 그 구절은 '…' 로 줄이고 '이 정정의 대상이 아니다' 로 쓴다.

초안 원안:

```text
> **정정 (2026-09-23, review_next G-1.2)**: 헤드라인 최종판의 "사전 등록 게이트를 통과한 학습 prior 가" 는 PAPER_MATERIALS:819-820 규칙("게이트를 통과한 D2 모델" 이라 쓰지 않는다)을 어긴 줄임말이다. 이 prior 의 D2 체크포인트 `d2sx_N160000_a1.pt` 에는 게이트 행이 없다(`results/tables_D2_B16e4k.txt:45` `NO GATE RECORD mentions d2sx_N160000_a1.pt -- UNVERIFIED here`). 게이트는 D1 에서만 측정된다(10_SPEC_stageC:126-129). PASS 는 D1 형제 `sx_N160000_D1.pt` 의 행이다(`LADDER_C.md:1`, GB +0.27% / GC 0.0999 / GD 0.0718). 원고 헤드라인에는 이렇게 쓴다: "사전 등록 게이트를 D1 에서 통과한 레시피(D1 형제 `sx_N160000_D1.pt`)로 D2 에 학습한 prior 가, 같은 1.6e5 채널 집합으로 적합하고 K 격자를 우도가 오르는 한계(K=1024)까지 넓힌 GMM 을 같은 수신기에서 이긴다: …". 이 정정은 게이트 구절만 다룬다. 수치·검정은 불변이다. 1304행(testbed-gate-14)과 같은 문장의 최종판이다.
```
</details>

<details><summary>근거</summary>

git show HEAD:conf/STATUS.md l.1602/1604-1606. results/tables_D2_B16e4k.txt:45 'NO GATE RECORD mentions d2sx_N160000_a1.pt -- UNVERIFIED here'. LADDER_C.md:1 '[2026-09-21 14:12 KST] SX160000 | a1 | … | GA 9.879e-16 | GB +0.27% | GC 0.0999 | GD 0.0718 | PASS | GATED from sx_N160000_D1.pt'. samplecx_D1.txt:30 '160,000 … 0.00266 0.09986 0.07183 … PASS'. 10_SPEC_stageC.md:126-129 '판정은 오직 D1 게이트가 내린다'. PAPER_MATERIALS.md:819-820. round-1 checker: 1304 의 최종판이고 영향이 가장 크다. cost-ckpt-15 는 1591 뒤에 삽입하므로 이 위치와 겹치지 않는다.

검증: (위 참조)
</details>

### testbed-gate-27 · testbed-gate-27 — `conf/STATUS.md` 815 (문단 814-815). 노트는 815행 뒤, 816행 빈 줄 앞에 빈 줄 + 삽입

- 방식: **STATUS inline note** · ✅ 검증 통과

**원문 (HEAD)**

```text
815: 같다. 따라서 이 결론은 게이트를 통과한 N=1.6e5 모델에도 그대로 적용된다.
```

**제안 문구**

```text
> **정정 (2026-09-23, review_next G-1.2)**: "게이트를 통과한 N=1.6e5 모델" 은 "D1 형제 `sx_N160000_D1.pt` 가 게이트를 통과한 레시피로 D2 에 학습한 N=1.6e5 체크포인트(`d2sx_N160000_a1.pt`)" 로 읽는다. 그 D2 체크포인트에는 게이트 행이 없고(`results/tables_D2_C.txt:45`), PASS 는 `LADDER_C.md:1` 의 D1 행이다. 게이트 문구만 다루며, 수치(V1 0.145 / 0.145)는 불변이다.
```

<details><summary>근거</summary>

git show HEAD:conf/STATUS.md l.814-815 (§'이것이 닫는 것' (2)). results/tables_D2_C.txt:45 'NO GATE RECORD mentions d2sx_N160000_a1.pt -- UNVERIFIED here'. LADDER_C.md:1 PASS 'GATED from sx_N160000_D1.pt'. PAPER_MATERIALS.md:816-820 (tables_D2_C 체크포인트에는 게이트 행이 없고, D1 쌍둥이가 자격을 준다).

검증: 815행(문단 814-815, §'이것이 닫는 것' 808)이 글자 그대로 맞다. V1 0.145 / 0.145 는 814행이고, tables_D2_C.txt:45 와 LADDER_C.md:1 PASS, PM:816-820 도 맞다. 문구와 형식에 문제없다.
</details>

### testbed-gate-28 · testbed-gate-28 — `conf/STATUS.md` 175 (표 172-185, 2번 행) + 183 (같은 표 10번 행, 2차 추가 발견). 노트는 185행(표 끝) 뒤 186행 빈 줄 다음에 삽입 + 빈 줄 (188행 '> **기전 정정' 인용과 분리)

- 방식: **STATUS inline note** · ✅ 검증 통과

**원문 (HEAD)**

```text
175: | 2 | 붕괴의 원인은 야코비안 고유값의 **부호**다 | 양방향 do() 개입, **n=64**, D2 C2, 0 dB, 게이트 **미통과** N=1e4 모델. 진단 탐침이며 arm 이 아니다 |
183: | 10 | 수리 3종이 D2 진단에서 발산을 제거 | 7 SNR 전부 발산율 0.000. 적합 GMM 대비 **7 중 5 SNR 에서 우세**(+9 dB 는 0.004 vs 0.000 으로 GMM 이 낫고 +15 dB 는 동률). n=256, **게이트 미통과** 모델 |
```

**제안 문구**

```text
> **정정 (2026-09-23, review_next G-1.2)**: 2번 행(175) "게이트 **미통과** N=1e4 모델" 과 10번 행(183) "**게이트 미통과** 모델" 은 D2 체크포인트 `d2sx_N10000_a1.pt` 에 게이트 판정을 직접 붙인 거울형 줄임말이다(340행 정정과 같은 유형). 그 D2 파일에는 게이트 행이 없다(`results/tables_D2_B1e4.txt:45`). 진단 파일도 이 체크포인트를 적는다(`results/diag/SUMMARY.md:4`, `results/settling_D2.txt:14`). FAIL 은 같은 레시피의 N=1e4 D1 기록에서 나온 판정이며, 두 기록 모두 GC 에서 FAIL 이다. `samplecx_D1.txt:28` GC 0.24333, `hpo_final_r2.txt` trial 386 재게이트 GC 0.224111. 어느 쪽을 인용하는지는 NUMBERS_PACKAGE:402-406 대로 밝힌다. 읽는 법: "D1 형제가 게이트에 실패한 레시피·예산의 N=1e4 D2 모델 (D2 자체 게이트 행 없음)". 진단 탐침이고 arm 이 아니라는 지위와 수치는 불변이다.
```

<details><summary>근거</summary>

git show HEAD:conf/STATUS.md l.172-186. results/diag/SUMMARY.md:4 'checkpoint under diagnosis: `ckpt/d2sx_N10000_a1.pt`'. results/settling_D2.txt:14 'Every row uses ckpt/d2sx_N10000_a1.pt, which FAILED the pre-registered gates (GC 0.224 vs 0.15)'. results/tables_D2_B1e4.txt:45 'NO GATE RECORD mentions d2sx_N10000_a1.pt -- UNVERIFIED here'. samplecx_D1.txt:28 '10,000 200 … 0.01174 0.24333 0.16081 … FAIL'. results/hpo_final_r2.txt:17-23 'trial 386 … passed=False … GC 2.24111e-01 <= 0.15'. 같은 레시피 확인: logs/train_d2sx_N10000_a1.log hp = {'arch':'dit','param':'vp','domain':'angle','lr':0.002238046051591068,'ema':0.999,'batch':256,…,'width':64,'depth':6} 로 trial 386 hp 와 같다. NUMBERS_PACKAGE:402-406 'TWO GC values circulate …'. 183행은 round-1·checker 둘 다 놓친 같은 표의 같은 유형이다.

검증: 175행과 183행이 글자 그대로 맞다. 표는 172-185행, 186-187행이 빈 줄, 188행이 '> **기전 정정' 이라 배치가 맞다. 체크포인트 대응을 확인했다. 2번 행(n=64 do() 개입)은 diag/SUMMARY.md §3.6 이고, :4 가 d2sx_N10000_a1.pt, :5 가 hp = HPO trial 386 이다. 10번 행(7 SNR, n=256)은 settling_D2.txt:14 가 d2sx_N10000_a1.pt 다. 수치: tables_D2_B1e4.txt:45 게이트 행 없음, samplecx_D1.txt:28 GC 0.24333 FAIL, hpo_final_r2.txt:17-23 GC 2.24111e-01 passed=False. 둘 다 GC 에서만 FAIL 이다(GB·GD 는 통과). logs/train_d2sx_N10000_a1.log:6 hp 는 trial 386 hp 와 같다. NUMBERS_PACKAGE:402-406 도 맞다.
</details>

### testbed-gate-29 · testbed-gate-29 — `conf/STATUS.md` 1617 (문단 1616-1618). 노트는 1618행 뒤에 빈 줄 + 삽입 (1619 빈 줄 유지)

- 방식: **STATUS inline note** · ✅ 검증 통과

**원문 (HEAD)**

```text
1617: · §6e λ 스윕(0.01/0.1/1.0 게이트 + asym/PSD) · §6p 저SNR 연장 · §6q A8 복잡도 · B16e4/B16e4k 게이트 통과 동일예산 표
```

**제안 문구**

```text
> **정정 (2026-09-23, review_next G-1.2)**: "B16e4/B16e4k 게이트 통과 동일예산 표" 는 "B16e4/B16e4k — D1 형제 게이트 PASS 레시피 + 동일예산 표" 로 읽는다. 두 표의 D2 체크포인트 `d2sx_N160000_a1.pt` 에는 게이트 행이 없다(`results/tables_D2_B16e4.txt:45`, `results/tables_D2_B16e4k.txt:45`). PASS 는 `LADDER_C.md:1` 의 `sx_N160000_D1.pt` 행이다.
```

<details><summary>근거</summary>

git show HEAD:conf/STATUS.md l.1616-1618. tables_D2_B16e4.txt:45, tables_D2_B16e4k.txt:45 둘 다 'NO GATE RECORD mentions d2sx_N160000_a1.pt -- UNVERIFIED here'. LADDER_C.md:1 PASS. 같은 표를 다룬 1257행 정정(testbed-gate-12)과 같은 문구.

검증: 1617행(문단 1616-1618)이 맞다. 1619·1620행은 빈 줄이다. tables_D2_B16e4.txt:45 와 B16e4k.txt:45 가 게이트 행 없음이고, LADDER_C.md:1 은 PASS 다. testbed-gate-12 와 같은 문구다.
</details>

### testbed-gate-30 · testbed-gate-30 — `conf/STATUS.md` 1635-1636. 노트는 1636행 뒤에 빈 줄 + 삽입

- 방식: **STATUS inline note** · ✅ 검증 통과

**원문 (HEAD)**

```text
1635: **F14 에서 고친 실제 버그 하나**: `GATE_LINE` 이 모듈 상수로 박혀 있어 게이트 **통과** 실행에도 "GC 0.243 FAILS"
1636: 문구가 붙었다. 실행의 raw 디렉토리로 문구를 고르도록 바꿨다.
```

**제안 문구**

```text
> **정정 (2026-09-23, review_next G-1.2)**: "게이트 **통과** 실행에도" 는 "D1 형제 게이트 PASS 레시피로 학습한 체크포인트(`d2sx_N160000_a1.pt`, `raw_B16e4*`)의 실행에도" 로 읽는다(그 D2 체크포인트에는 게이트 행이 없다: `results/tables_D2_B16e4k.txt:45`). 버그 서술(모듈 상수 → raw 디렉토리로 문구 선택, `code/figure_f14.py:98`)은 사실 그대로다. 지금 붙는 문구 `GATE_LINE_PASS` 는 형제 한정어를 싣고 있다(`code/figures_stagec2.py:60-62`).
```

<details><summary>근거</summary>

git show HEAD:conf/STATUS.md l.1635-1636. conf/code/figure_f14.py:98 'gate_line = GATE_LINE_PASS if a.raw.startswith("raw_B16e4") else GATE_LINE'. figures_stagec2.py:58-59 GATE_LINE '…its D1 sibling at N_train=1e4 FAILS GC 0.243 vs 0.15.', :60-62 GATE_LINE_PASS '…this D2 checkpoint is qualified through its D1 sibling sx_N160000_D1.pt, which PASSES GB 2.66e-3 / GC 0.0999 / GD 0.0718 (LADDER_C.md:1)…'. tables_D2_B16e4k.txt:45.

검증: 1635-1636행이 맞다. figure_f14.py:98 `GATE_LINE_PASS if a.raw.startswith("raw_B16e4") else GATE_LINE` 도 맞고, 35행이 figures_stagec2 에서 GATE_LINE 과 GATE_LINE_PASS 를 가져온다. figures_stagec2.py:58-59 GATE_LINE, :60-62 GATE_LINE_PASS(형제 한정어 포함)를 확인했고, F14 txt:29 에 인쇄돼 있다. 버그 서술은 그대로 두고 게이트 문구만 한정한다.
</details>

### testbed-gate-31 · testbed-gate-31 — `conf/PAPER_MATERIALS.md` 690-692 (§15.5 읽기 1, 목록 항목 690-692). 노트는 692행 뒤, 같은 항목의 들여쓴 인용으로 (693행 '2.' 앞)

- 방식: **PAPER_MATERIALS inline note** · ✅ 검증 통과

**원문 (HEAD)**

```text
690: 1. **사전 등록 배선이 수신기를 고전 터보보다 나쁘게 만든다.** V0 는 실질 세 게이트를 통과한
691:    체크포인트를 사전 등록 D-14 행렬 site 에 그대로 넣은 것이고 결과는 BLER 0.593 대 0.537.
692:    → **게이트 통과가 수신기 사용 가능성을 보증하지 않는다** 가 실측 확정됐다.
```

**제안 문구**

```text
> **정정 (2026-09-23, review_next G-1.2)**: 690-691행 "V0 는 실질 세 게이트를 통과한 체크포인트를" 은 §17.3 규칙(819-820)대로 "V0 는 D1 형제 `sx_N160000_D1.pt` 가 실질 세 게이트(GB·GC·GD. GA 는 이 모델 계열에서 구조적 0)를 통과한 레시피로 D2 에 학습한 체크포인트(`d2sx_N160000_a1.pt`)를" 로 읽는다. 그 D2 체크포인트에는 게이트 행이 없다(`results/tables_D2_C.txt:45`). 692행은 "D1 형제의 게이트 PASS 가 D2 수신기 사용 가능성을 보증하지 않는다" 로 읽는다(STATUS:390 과 같은 뜻). 수치(BLER 0.593 대 0.537)는 불변이다.
```

<details><summary>근거</summary>

git show HEAD:conf/PAPER_MATERIALS.md l.688-693. PAPER_MATERIALS.md:694 '학습 arm 은 N'=1.6e5' (§15 는 tables_D2_C 실행). results/tables_D2_C.txt:45 'NO GATE RECORD mentions d2sx_N160000_a1.pt -- UNVERIFIED here'. LADDER_C.md:1 GA 9.879e-16 / GB +0.27% / GC 0.0999 / GD 0.0718 PASS. STATUS.md:174 'GA 는 이 모델 계열에서 구조적 0 이므로 PASS 는 GB·GC·GD 3개에 달려 있다'. STATUS.md:390 'D1 게이트 통과는 D2 수신기 동작을 보증하지 않는다'. PAPER_MATERIALS.md:819-820 규칙.

검증: 690-692행이 맞고, 693행은 '2.' 이다. V0 체크포인트가 d2sx_N160000_a1.pt 임을 tables_D2_C.txt:37 에서 확인했다. LADDER_C.md:1 GA 9.879e-16, STATUS:174(GA 구조적 0), STATUS:390 도 맞다. 선택 보강(수정 불요): PM:688 이 '(네 문장, STATUS "읽기" 절)' 이라 적으므로 692행의 출처는 STATUS:744-745 다. 그 원문은 같은 명제에 '위 "체크포인트 출처" 의 형제-자격 연결 위에서만 성립하며, 그 연결을 함께 인용해야 한다' 는 한정을 붙인다. 근거로 STATUS:390 과 함께 744-745 를 들면 '옮기면서 한정어가 떨어졌다' 는 점이 더 직접 드러난다.
</details>

### testbed-gate-32 · testbed-gate-32 — `conf/PAPER_MATERIALS.md` 906 (그림 표 게이트 열, 경계). testbed-gate-19 노트(911행 뒤)의 '911: …' 구절 다음에 한 구절 추가

- 방식: **PAPER_MATERIALS inline note** · ✅ 검증 통과

**원문 (HEAD)**

```text
906: | `F15_gap_robustness.*` | **격차가 데이터·성분수·시드로 설명되지 않는다.** (a) C2 11 SNR 등예산, V1 이 11/11 우세·가드 0, 절대차 최대 −6 dB·비 최대 +6 dB 둘 다 표시 (b) 예산축 1e4/4e4/1.6e5 격차 0.107/0.105/0.108 (c) 성분축 K=512/1024/2048, 우도 +2.16~3.18 nat 에 BLER 불변 (d) 시드축 a1/a2/a3, V1 산포 0.0043 대 V0 0.0926. 생성 `code/figures_stagec3.py` | 패널별 혼재 — 캡션·푸터가 어느 패널이 게이트 실패분인지 명시 | **방어 그림** (§6d·§6l·§6g·§6p) |
```

**제안 문구**

```text
(testbed-gate-19 노트에 추가할 구절, 경계 사례) "906 게이트 열 '어느 패널이 게이트 실패분인지' 는 '어느 패널이 D1 형제 게이트 FAIL 분인지' 로 읽는다. F15 캡션과 푸터 원문은 이미 'checkpoints whose D1 siblings FAIL GC' 로 한정한다(`code/figures_stagec3.py:192-193`, `:237-238`)."
```

<details><summary>근거</summary>

git show HEAD:conf/PAPER_MATERIALS.md l.906. figures_stagec3.py:192-193 '(a), (c) N=4e4 column and (d) use checkpoints whose D1 siblings FAIL GC (0.243 at N=1e4, 0.167 at N=4e4)', :237-238 'use checkpoints whose D1 siblings FAIL the pre-registered GC gate'. samplecx_D1.txt:28-29 GC 0.24333 / 0.16651 FAIL. round-1 checker(testbed-gate-19 검증): '906 … 경계 사례. 이 노트에 한 구절을 더하면 완결된다'. round-1 G-1.2 DECISIONS 행(검증 수정본)은 PM 906 을 이미 목록에 넣었다.

검증: 906행이 맞다. figures_stagec3.py:192-193 'whose D1 siblings FAIL GC (0.243 at N=1e4, 0.167 at N=4e4)' 와 :237-238 을 확인했고, samplecx_D1.txt:28-29 도 맞다. round-1 은 이 행을 '(경계)' 로만 표시했고 '선택' 으로 표시하지 않았다. 검증 문구도 '한 구절을 더하면 완결된다' 였고 G-1.2 DECISIONS 행(testbed-gate-23 수정본)이 PM 906 을 이미 노트 목록에 넣었다. 그래서 optional 이 아닌 testbed-gate-19 노트 보강으로 두는 것이 맞다.
</details>

### testbed-gate-33 · testbed-gate-33 — `conf/10_SPEC_stageC.md` 451-455 (§6d 설계 표). 노트는 455행(표 끝) 뒤 456행 빈 줄 다음에 삽입 + 빈 줄 (457행 앞)

- 방식: **spec note (사용자 승인 필요)** · ✅ 검증 통과

**원문 (HEAD)**

```text
451: | 예산 | 학습 체크포인트 | GMM·가우시안 적합 | 게이트 |
452: |---|---|---|---|
453: | N=1e4 | `ckpt/d2sx_N10000_a1.pt` | `gmm_fits_D2` (n10000) | **FAIL** (GC 0.243) |
454: | N=4e4 | `ckpt/d2sx_N40000_a1.pt` | `gmm_fits_D2_n4e4` (n40000) | **FAIL** (GC 0.167) |
455: | N=1.6e5 | `ckpt/d2sx_N160000_a1.pt` | `gmm_fits_D2_n16e4` (진행 중) | **PASS** |
```

**제안 문구**

```text
> **노트 (2026-09-23, review_next G-1.2) — 사용자 승인 필요.** 사전 등록 표라 원문은 고치지 않는다. '게이트' 열의 FAIL/PASS 는 각 행 D2 체크포인트를 측정한 값이 아니다. 같은 레시피·같은 N_train 의 D1 형제에 대한 판정이다: N=1e4 `sx_N10000_D1.pt` GC 0.24333 FAIL, N=4e4 `sx_N40000_D1.pt` GC 0.16651 FAIL, N=1.6e5 `sx_N160000_D1.pt` GC 0.09986 PASS (`results/samplecx_D1.txt:28-30`. PASS 행은 `LADDER_C.md:1`). 세 D2 체크포인트 모두 게이트 행이 없다(`results/tables_D2_B1e4.txt:45`, `tables_D2_B4e4.txt:45`, `tables_D2_B16e4.txt:45`). 열 머리는 'D1 형제 게이트' 로 읽는다. 규칙(126-129: 판정은 D1 게이트)과 설계는 불변이다. 453행은 `results/NUMBERS_PACKAGE_2026-09-22.md:418`·`:575` 가 이미 같은 결함으로 지목했다.
```

<details><summary>근거</summary>

git show HEAD:conf/10_SPEC_stageC.md l.439(§6d 제목, '결과 관측 전'), 451-456. samplecx_D1.txt:28-30 (10,000 GC 0.24333 FAIL / 40,000 GC 0.16651 FAIL / 160,000 GC 0.09986 PASS). run_samplecx.py:16 f"sx_N{N}_D1.pt" (round-1 확인). LADDER_C.md:1 PASS GATED from sx_N160000_D1.pt. tables_D2_{B1e4,B4e4,B16e4}.txt:45 모두 'NO GATE RECORD mentions d2sx_N…_a1.pt -- UNVERIFIED here'. NUMBERS_PACKAGE:418 'STATUS.md:825 and 10_SPEC_stageC.md:453 both write … as if measured on that file. It was not.', :575 동일.

검증: 451-455행이 맞고 456행이 빈 줄, 457행이 본문이다. 439행 제목 '결과 관측 전' 을 확인했다. 수치: samplecx_D1.txt:28-30 GC 0.24333 / 0.16651 FAIL, 0.09986 PASS. run_samplecx.py:16 sx_N{N}_D1.pt. tables_D2_{B1e4,B4e4,B16e4}.txt:45 는 전부 게이트 행 없음이다. NUMBERS_PACKAGE:418·:575 인용도 맞다. 사전 등록 원문을 두고 사용자 승인 필요 노트만 단 형식이 맞다.
</details>

### testbed-gate-34 · testbed-gate-34 — `conf/10_SPEC_stageC.md` 461-463 (§6d 무결성 조건 첫 항목). 노트는 463행 뒤, 같은 항목의 들여쓴 인용으로 (464행 다음 항목 앞)

- 방식: **spec note (사용자 승인 필요)** · ✅ 검증 통과

**원문 (HEAD)**

```text
461: - **N=1e4 와 N=4e4 의 학습 체크포인트는 게이트에 실패했다.** 따라서 이 두 점은 **arm 결과가 아니라
462:   예산 축 측정**이며, 별도 표(`tables_D2_B1e4.txt`, `tables_D2_B4e4.txt`)에 싣고 표 머리말에
463:   게이트 실패를 명시한다. 사전 등록 표와 `tables_D2_C.txt` 는 불변이다.
```

**제안 문구**

```text
> **노트 (2026-09-23, review_next G-1.2) — 사용자 승인 필요.** "N=1e4 와 N=4e4 의 학습 체크포인트는 게이트에 실패했다" 는 "N=1e4·4e4 에서 D1 형제가 게이트에 실패했으므로(GC 0.24333 / 0.16651, `results/samplecx_D1.txt:28-29`) 그 예산의 D2 학습 체크포인트는 §5 형제 규칙(126-129)상 자격이 없다" 로 읽는다. 두 표의 머리말은 실제로 게이트 실패를 직접 적지 않는다. `NO GATE RECORD mentions d2sx_N{10000,40000}_a1.pt -- UNVERIFIED here` 와 형제 규칙을 적는다(`tables_D2_B1e4.txt:45`, `tables_D2_B4e4.txt:45`). 무결성 조건(두 점은 arm 결과가 아니라 예산 축 측정, 별도 표)은 불변이다.
```

<details><summary>근거</summary>

git show HEAD:conf/10_SPEC_stageC.md l.461-464. tables_D2_B1e4.txt:37-39,45 'gate: NO GATE RECORD mentions d2sx_N10000_a1.pt -- UNVERIFIED here. (GA-GD are measurable on D1 only, 10_SPEC §5: a D2 re-train is qualified by its D1 sibling's gate row, which this string cannot prove.)'. tables_D2_B4e4.txt:45 동일(d2sx_N40000_a1.pt). samplecx_D1.txt:28-29. 10_SPEC_stageC.md:126-129.

검증: 461-463행이 맞고 464행이 다음 항목이다. '두 표의 머리말은 게이트 실패를 직접 적지 않는다' 를 확인했다. tables_D2_B1e4.txt 와 B4e4.txt 머리말 1-46행에 FAIL 문구가 없다. 게이트 관련 줄은 37-39·45행의 'NO GATE RECORD … UNVERIFIED here' 와 형제 규칙, 43행 ABSENT 뿐이다. samplecx_D1.txt:28-29 와 10_SPEC:126-129 도 맞다.
</details>

### testbed-gate-35 · testbed-gate-35 — `conf/10_SPEC_stageC.md` 548-549 (§6f 목록 항목). 노트는 549행 뒤, 같은 항목의 들여쓴 인용으로 (550행 빈 줄 앞)

- 방식: **spec note (사용자 승인 필요)** · ✅ 검증 통과

**원문 (HEAD)**

```text
548: - N=1e4·N=4e4 체크포인트는 게이트 실패분이므로 §6d 와 같은 지위(**arm 결과가 아니라 체제 축 측정**)로
549:   별도 표에 싣는다. 태그는 `B1e4_<cell>` / `B4e4_<cell>`.
```

**제안 문구**

```text
> **노트 (2026-09-23, review_next G-1.2) — 사용자 승인 필요.** "게이트 실패분" 은 "D1 형제가 게이트에 실패한 예산의 D2 학습본(D2 자체 게이트 행 없음)" 으로 읽는다(`results/samplecx_D1.txt:28-29`, `results/tables_D2_B1e4x.txt:45`). 지위 규정(체제 축 측정, 별도 표, 태그)은 불변이다.
```

<details><summary>근거</summary>

git show HEAD:conf/10_SPEC_stageC.md l.522(§6f 제목), 548-550. samplecx_D1.txt:28-29 GC 0.24333 / 0.16651 FAIL. tables_D2_B1e4x.txt:45 'NO GATE RECORD mentions d2sx_N10000_a1.pt -- UNVERIFIED here'.

검증: 548-549행이 맞고 550행이 빈 줄, 522행이 §6f 제목이다. samplecx_D1.txt:28-29 와 tables_D2_B1e4x.txt:45(d2sx_N10000_a1.pt 게이트 행 없음)도 맞다. §6f 는 4e4 셀을 돌리지 않았으므로(STATUS:1616 '§6f 셀 일반화(1e4·1.6e5)') B1e4x 만 인용해도 충분하다.
</details>

### testbed-gate-36 · testbed-gate-36 — `conf/code/figures_stagec3.py` 192-195 (F15 그림 안 푸터, png/pdf 에 인쇄됨) + 240 (캡션, 경계). 주석은 192행 `    fig.text(0.5, 0.028, …` 바로 앞에 삽입. 출력 불변, 재생성 안 함

- 방식: **caption/generator note** · ✅ 검증 통과

**원문 (HEAD)**

```text
192:     fig.text(0.5, 0.028, "(a), (c) N=4e4 column and (d) use checkpoints whose D1 siblings FAIL GC "
193:                          "(0.243 at N=1e4, 0.167 at N=4e4); (b) rightmost point and (c) N=1.6e5 use the "
194:                          "gate-passing d2sx_N160000_a1.", ha="center", fontsize=6.5, color="0.3")
195:     fig.text(0.5, 0.004, "§6d registers the gate-failing points as budget-axis measurements, not arm results.",
240: N = 1.6e5 curve of (c) use the gate-passing checkpoint: """ + GATE_LINE_PASS + """
```

**제안 문구**

```text
# NOTE (2026-09-23, review_next G-1.2): the two footer strings below are printed INTO the figure
    # (figs/F15_gap_robustness.png/.pdf); they are NOT changed here and F15 is NOT regenerated.
    # "the gate-passing d2sx_N160000_a1" is shorthand: that D2 checkpoint has no gate row
    # (results/tables_D2_B16e4k.txt:45); it is qualified through its D1 sibling sx_N160000_D1.pt
    # (LADDER_C.md:1).  "the gate-failing points" are points whose D1 siblings FAIL GC
    # (results/samplecx_D1.txt:28-29).  At the next regeneration read: "... use d2sx_N160000_a1, whose
    # D1 sibling passes the gates." and "§6d registers the points whose D1 siblings fail GC as
    # budget-axis measurements, not arm results."  (Optional: the caption's "use the gate-passing
    # checkpoint:" is followed by GATE_LINE_PASS, which already carries the sibling qualifier.)
```

<details><summary>근거</summary>

git show HEAD:conf/code/figures_stagec3.py l.189-197, 236-241. 192-193행은 이미 'whose D1 siblings FAIL GC' 로 한정하고, 194행 'gate-passing d2sx_N160000_a1' 과 195행 'gate-failing points' 에는 한정어가 없다. 240행 바로 뒤 GATE_LINE_PASS(figures_stagec2.py:60-62, figs/F15_gap_robustness.txt:43 에 그대로 인쇄) → checker 가 경계로 분류. tables_D2_B16e4k.txt:45, LADDER_C.md:1, samplecx_D1.txt:28-29. 주석 안에 줄 번호를 쓰지 않은 것은 삽입 뒤 줄이 밀리기 때문이다(testbed-gate-22 관례).

검증: 192-195행과 240행이 맞다. 주석 위치(192행 앞)에서 보면 '아래 두 푸터 문자열' 은 192-194행과 195-196행이다. 189행 푸터는 게이트와 무관하다. tables_D2_B16e4k.txt:45, LADDER_C.md:1, samplecx_D1.txt:28-29 를 확인했다. 240행을 경계로 분류한 판단이 맞다(바로 뒤 GATE_LINE_PASS 가 형제 한정어를 싣는다). 출력 불변이고 재생성도 하지 않는다.
</details>

### testbed-gate-37 · testbed-gate-37 — `conf/code/figures_stagec2.py` 426-427 (F13 캡션 BUDGET NOTE, 삼중따옴표 문자열 안). 주석은 391행 `    return _save(fig, "F13_sign_vs_magnitude", """` 바로 앞에 삽입. 출력 불변

- 방식: **caption/generator note** · ✅ 검증 통과

**원문 (HEAD)**

```text
426: BUDGET NOTE (added 2026-09-22 22:20).  F12 and F14 were re-drawn on the gate-passing N = 1.6e5 run
427: (checkpoint ckpt/d2sx_N160000_a1.pt, n = 2560).  This figure was NOT: it stays on the n = 256
```

**제안 문구**

```text
# NOTE (2026-09-23, review_next G-1.2): the caption's BUDGET NOTE below says F12 and F14 "were
    # re-drawn on the gate-passing N = 1.6e5 run".  Shorthand: that run's D2 checkpoint
    # d2sx_N160000_a1.pt has no gate row (results/tables_D2_B16e4.txt:45, tables_D2_B16e4k.txt:45); it
    # is qualified through its D1 sibling sx_N160000_D1.pt (LADDER_C.md:1).  figs/F13_sign_vs_magnitude.*
    # are NOT regenerated for this; at the next regeneration read "re-drawn on the N = 1.6e5 run whose
    # D1 sibling passes the gates".
```

<details><summary>근거</summary>

git show HEAD:conf/code/figures_stagec2.py l.391(F13 _save 시작), 426-432. figs/F13_sign_vs_magnitude.txt:35 에 같은 문구가 인쇄돼 있다. 428행 'whose D1 sibling FAILS GC' 는 이미 한정돼 있다. tables_D2_B16e4.txt:45, tables_D2_B16e4k.txt:45, LADDER_C.md:1. 같은 파일 246행(F12 제목)의 주석은 testbed-gate-22 에 있다.

검증: 426-427행과 391행(`return _save(fig, "F13_sign_vs_magnitude", """`)이 맞다. figs/F13_sign_vs_magnitude.txt:35 에 같은 문구가 있다. F12 는 B16e4, F14 는 B16e4k 이고 두 표 :45 가 게이트 행 없음이다. 428행은 이미 한정돼 있다.
</details>

### testbed-gate-38 · testbed-gate-38 — `conf/code/figures_stagec2.py` 31 (모듈 docstring. 어디서도 __doc__ 를 쓰지 않으므로 직접 수정해도 출력 불변)

- 방식: **docstring edit** · ✅ 검증 통과

**원문 (HEAD)**

```text
31: an arm result.  The gate-passing model's numbers live in results/tables_D2_C.txt.
```

**제안 문구**

```text
old: an arm result.  The gate-passing model's numbers live in results/tables_D2_C.txt.
new:
an arm result.  The numbers of ckpt/d2sx_N160000_a1.pt -- no D2 gate row either; its D1 sibling
sx_N160000_D1.pt PASSES (LADDER_C.md:1) -- live in results/tables_D2_C.txt.  [record correction
2026-09-23, review_next G-1.2: previously 'The gate-passing model's numbers'.]
```

<details><summary>근거</summary>

git show HEAD:conf/code/figures_stagec2.py l.28-32. 28-30행은 이미 'NO GATE RECORD … its D1 sibling … FAILS GC' 로 한정하고, 31행만 한정어가 없다. grep '__doc__' figures_stagec*.py → 0건. results/tables_D2_C.txt:45 'NO GATE RECORD mentions d2sx_N160000_a1.pt', LADDER_C.md:1 PASS. testbed-gate-1(d2.py docstring)의 '[record correction …]' 괄호 관례를 따랐다.

검증: 31행이 맞다. 28-30행은 이미 한정돼 있다. figures_stagec*.py 에서 __doc__ 사용은 0건이다(conf/code 전체에서는 hpo.py·runner.py·verify_gpu_port.py 가 자기 docstring 만 쓴다). tables_D2_C.txt:45 와 LADDER_C.md:1 도 맞다. docstring 교체와 [record correction] 괄호 관례가 맞다.
</details>

### testbed-gate-39 · testbed-gate-39 — `conf/code/figures_stagec.py` 515-518 (F9 캡션 GATE STATUS, 삼중따옴표 문자열 안). 주석은 484행 `    return _save(fig, "F9_sigma_band_vs_snr", """` 바로 앞에 삽입. 출력 불변

- 방식: **caption/generator note** · ✅ 검증 통과

**원문 (HEAD)**

```text
515: GATE STATUS.  Every row of this figure uses ckpt/d2sx_N10000_a1.pt, which FAILED the pre-registered
516: gates (GC 0.224 against a bar of 0.15).  These are DIAGNOSTIC PROBES on an UN-GATED checkpoint.  They
517: may not enter a result table and they license no claim; 10_SPEC_stageC Sec.6/6c specifies the
518: confirmatory run with a gate-passing checkpoint at n >= 2560.
```

**제안 문구**

```text
# NOTE (2026-09-23, review_next G-1.2): the caption's GATE STATUS paragraph below says
    # ckpt/d2sx_N10000_a1.pt "FAILED the pre-registered gates (GC 0.224 ...)".  Shorthand (mirror case):
    # that D2 checkpoint has no gate row (results/tables_D2_B1e4.txt:45; gates are measurable on D1 only,
    # 10_SPEC_stageC Sec.5).  GC 0.224 is the D1 re-gate of the same recipe (HPO trial 386,
    # results/hpo_final_r2.txt: GC 2.24111e-01, passed=False; NUMBERS_PACKAGE_2026-09-22.md:402-406).
    # The next sentence ("DIAGNOSTIC PROBES on an UN-GATED checkpoint") is already exact.
    # figs/F9_sigma_band_vs_snr.* are NOT regenerated; at the next regeneration read "... uses
    # ckpt/d2sx_N10000_a1.pt, which has no gate record on D2; the D1 re-gate of its recipe FAILS
    # (GC 0.224 against a bar of 0.15, HPO trial 386)." and "... with a checkpoint whose D1 sibling
    # passes the gates, at n >= 2560."
```

<details><summary>근거</summary>

git show HEAD:conf/code/figures_stagec.py l.484(F9 _save 시작), 515-519. figs/F9_sigma_band_vs_snr.txt:31-34 에 같은 문구가 인쇄돼 있다. results/hpo_final_r2.txt:17-23 'trial 386 gate_score 1.4941 passed=False … GC 2.24111e-01 <= 0.15'. hp 가 logs/train_d2sx_N10000_a1.log 의 hp 와 같다(dit vp/angle lr 0.002238046051591068 ema 0.999 batch 256 w64 d6). NUMBERS_PACKAGE:404 '0.224111 … Quoted by figs/F8, figs/F9, settling_D2.txt'. tables_D2_B1e4.txt:45. 518행 'gate-passing checkpoint' 는 10_SPEC 계획을 가리키지만 같은 줄임말이라 같은 주석에서 함께 다룬다.

검증: 515-518행과 484행(F9 _save 시작)이 맞다. figs/F9_sigma_band_vs_snr.txt:31-34 에 같은 문구가 있다. hpo_final_r2.txt:17-23 trial 386 GC 2.24111e-01 passed=False, 같은 hp(diag/SUMMARY.md:5 '= HPO trial 386', train_d2sx_N10000_a1.log:6), NUMBERS_PACKAGE:404('Quoted by figs/F8, figs/F9, settling_D2.txt'), tables_D2_B1e4.txt:45 를 확인했다. 516행 'UN-GATED' 가 이미 정확하다는 판단도 맞다.
</details>

### testbed-gate-40 · testbed-gate-40 — `conf/DECISIONS.md` 49 (정정 대상, append-only, 경계·거울형). 새 행 불필요: testbed-gate-23(G-1.2 DECISIONS 행) 검증 수정본 보강

- 방식: **DECISIONS append** · ✏️ 검증 수정 반영 (인용 OK · 수치 OK · 문구 X)

**원문 (HEAD)**

```text
49: `[2026-09-21 17:25 KST] 정산실험 결과 — σ 대역 예측 확증, 진단 공백 해소 | results/settling_D2.txt (7 SNR x n=256 짝지음). 발산율(NMSE>1 비율)이 0.332→0.488→0.492→**0.523(+6dB 정점)**→0.344→0.242→0.082 로, 스펙트럼 측정이 예측한 σ~0.09~0.26 위험대를 수신기 동작점이 걸어 들어갔다 나오는 모양을 그대로 재현했다. 부호를 유지한 채 조건수만 고치면(abs1e-2) 전 SNR 에서 여전히 망가지고, 수리하면 발산율이 전 SNR 0.000 이다 | 이것이 진단(results/diag/SUMMARY.md)이 "부분적으로만 설명됨"으로 남긴 SNR 비단조성의 답이다. 별도 가설 없이 스펙트럼 측정 하나에서 예측이 나왔고 사전 등록된 실험으로 검정됐다. 수리된 학습 prior 는 7 SNR 전부에서 적합 GMM 을 이긴다(-3dB 0.168 vs 0.324, 0dB 0.039 vs 0.094) | 캐비엇: 전부 게이트 미통과 N=1e4 체크포인트의 진단 탐침이며 arm 이 아니다. 어떤 표에도 넣지 않는다. 확증은 §6/§6c 의 게이트 통과 모델로 n>=2560, 1회`
```

**제안 문구**

```text
(method: other. 새 append 가 아니라 testbed-gate-23 검증 수정본을 고치는 항목이다.) testbed-gate-23 행을 네 곳 고친다. (1) '이 파일 49행의 "게이트 미통과 N=1e4 체크포인트" 도 같은 줄임말이라 이 행이 대신 짚는다' → '이 파일 49행의 "게이트 미통과 N=1e4 체크포인트"·"§6/§6c 의 게이트 통과 모델" 도 같은 줄임말이라 이 행이 대신 짚는다(49행의 체크포인트는 settling_D2.txt:14 가 적은 d2sx_N10000_a1.pt 이고, 그 FAIL 은 같은 레시피의 D1 재게이트 GC 0.224111, hpo_final_r2.txt trial 386)'. (2) STATUS 목록에 183·956·1012 를 넣는다. 2차 missing 위치를 초안에 넣으면 PAPER_MATERIALS 목록에 23-25 를, 별도 구절로 docs/EXPERIMENTS.md:21 과 NUMBERS_PACKAGE :3·:543·:679 인라인 노트를 더한다. (3) 선택 필드 '그림은 재생성하지 않고 생성기에 주석만 단다: …' → '그림은 재생성하지 않는다. 생성기·코드에는 주석을 달거나 동작 불변 문구를 바꾼다: figures_stagec2.py:246(F12 제목)·:426(F13 캡션) 주석, :31(모듈 docstring 문구 교체), figures_stagec3.py:192-195(F15 그림 안 푸터 주석, :240 경계), figures_stagec.py:515-518(F9 캡션 주석), figure_f14.py:96-97(코드 주석 교체)'. (4) 되돌리는 법 필드 '노트 행과 생성기 주석만 지우면 원상(원문을 고치지 않았다)' → '노트 행과 생성기 주석을 지우고 figures_stagec2.py:31 docstring·figure_f14.py:96-97 주석을 cd241b7e 판으로 되돌리면 원상(기록 문서의 원문 행은 고치지 않았다)'. 나머지 필드는 그대로 둔다.
```

<details><summary>검증 agent 지적 / 초안 원안</summary>

지적: 49행이 맞다. settling_D2.txt:14 는 d2sx_N10000_a1.pt 와 GC 0.224 이고, hpo_final_r2.txt:17-23 도 맞다. testbed-gate-23 수정본에서 인용한 구절도 원문 그대로다. 문구·형식 문제 셋. (1) method 가 'DECISIONS append' 인데 새 행이 아니라 testbed-gate-23 초안 행을 고치는 항목이다. 'other' 여야 적용 스크립트가 따로 한 줄을 붙이지 않는다. (2) 2차에서 figures_stagec2.py:31 은 docstring 문구 교체(testbed-gate-38), figure_f14.py:96-97 은 주석 교체(testbed-gate-42)가 됐다. 그런데 testbed-gate-23 의 선택 필드 '생성기에 주석만 단다' 와 되돌리는 법 필드 '노트 행과 생성기 주석만 지우면 원상(원문을 고치지 않았다)' 가 그대로면 사실과 어긋난다. '나머지 필드는 그대로 둔다' 로는 부족하다. (3) 2차에서 새로 찾은 위치(missing 참조: PM 23-25, docs/EXPERIMENTS.md:21, NUMBERS_PACKAGE :3/:543/:679, arms.py:150, cf_rollup.py:46)를 초안에 넣으면 같은 목록에도 넣어야 한다.

초안 원안:

```text
append 행을 따로 두지 않는다. testbed-gate-23 검증 수정본이 이미 '이 파일 49행의 "게이트 미통과 N=1e4 체크포인트" 도 같은 줄임말이라 이 행이 대신 짚는다' 로 짚고 있다. 보강 두 가지. (1) 그 구절을 다음으로 바꾼다: '이 파일 49행의 "게이트 미통과 N=1e4 체크포인트"·"§6/§6c 의 게이트 통과 모델" 도 같은 줄임말이라 이 행이 대신 짚는다(49행의 체크포인트는 settling_D2.txt:14 가 적은 d2sx_N10000_a1.pt 이고, 그 FAIL 은 같은 레시피의 D1 재게이트 GC 0.224111, hpo_final_r2.txt trial 386)'. (2) 2차 초안에서 더한 위치를 같은 행의 목록에 넣는다. STATUS 목록에 183·956·1012. 생성기 주석 목록은 'figures_stagec.py:515-518(F9 캡션)', 'figures_stagec3.py:192-195(F15 그림 안 푸터, :240 경계)', 'figure_f14.py:96-97(코드 주석 교체)' 로 적는다. 나머지 필드는 그대로 둔다.
```
</details>

<details><summary>근거</summary>

git show HEAD:conf/DECISIONS.md l.49 (끝부분 '게이트 미통과 N=1e4 체크포인트'·'§6/§6c 의 게이트 통과 모델'). results/settling_D2.txt:14 'Every row uses ckpt/d2sx_N10000_a1.pt, which FAILED the pre-registered gates (GC 0.224 vs 0.15)'. hpo_final_r2.txt:17-23. RECORD_CORRECTIONS_DRAFT.md testbed-gate-23 검증 수정본 원문: '…figures_stagec.py:515-516(F9 캡션). 이 파일 49행의 "게이트 미통과 N=1e4 체크포인트" 도 같은 줄임말이라 이 행이 대신 짚는다.' 이 행은 목록이 완결됐다는 취지로 쓰였으므로(round-1 checker 지적), 새로 찾은 위치를 목록에 넣어야 그 취지가 유지된다.

검증: (위 참조)
</details>

### testbed-gate-41 · testbed-gate-41 — `conf/STATUS.md` 956-957 (노트는 957행 뒤에 빈 줄 + 삽입, 958 빈 줄 유지) / 1012 (노트는 1012행 뒤에 빈 줄 + 삽입). 2차 추가 발견, checker 목록 밖

- 방식: **STATUS inline note** · ✅ 검증 통과

**원문 (HEAD)**

```text
956: **범위**: C2, n=256/점, **게이트 미통과 N=1e4** 체크포인트의 진단 탐침이다. arm 이 아니고 어떤
957: BLER 표에도 들어가지 않는다.
1012: **범위**: n=8 진단 탐침, 게이트 미통과 N=1e4 체크포인트. arm 아님.
```

**제안 문구**

```text
[957행 뒤] > **정정 (2026-09-23, review_next G-1.2, 2차 추가 발견)**: "게이트 미통과 N=1e4 체크포인트" 는 "D1 형제(N=1e4)가 게이트에 실패한 레시피·예산의 D2 체크포인트 `d2sx_N10000_a1.pt`(D2 자체 게이트 행 없음, `results/tables_D2_B1e4.txt:45`)" 로 읽는다. 이 roll-up 이 인용하는 FAIL 은 `samplecx_D1.txt:28` 의 GC 0.24333 이다(`jacpsd_counterfactual_SUMMARY_n256.txt:6-7`). 진단 탐침이라는 지위는 불변이다.
[1012행 뒤] > **정정 (2026-09-23, review_next G-1.2, 2차 추가 발견)**: "게이트 미통과 N=1e4 체크포인트" 도 957행 정정과 같이 읽는다(`results/diag/sigma-coverage_D2_C1_n8.txt` 머리말의 checkpoint = `ckpt/d2sx_N10000_a1.pt`).
```

<details><summary>근거</summary>

git show HEAD:conf/STATUS.md l.956-958, 1011-1013. results/jacpsd_counterfactual_SUMMARY_n256.txt:6-7 'SCOPE : diagnostic probe on the N=1e4 checkpoint, which FAILED the pre-registered gate (GC 0.243 vs 0.15)'. figures_stagec2.py:28-30 (F13 도 같은 roll-up 이며 ckpt/d2sx_N10000_a1.pt, D1 sibling GC 0.243). results/diag/sigma-coverage_D2_C1_n8.txt:12 '# checkpoint : /home/HTJ/t2/conf/ckpt/d2sx_N10000_a1.pt (fixed, not retrained)'. tables_D2_B1e4.txt:45. STATUS 를 grep '게이트 통과|게이트를 통과|미통과|게이트 실패|게이트에 실패' 로 다시 훑어 찾았다. round-1·checker 목록에 없다.

검증: 956-957행과 1012행이 맞다. 956행은 §6h 절(950 제목, jacpsd roll-up 정본)이고 958·1013행은 빈 줄이다. jacpsd_counterfactual_SUMMARY_n256.txt:6-7 은 GC 0.243 이고 :10 run meta ckpt 는 d2sx_N10000_a1.pt 다. NUMBERS_PACKAGE:403 은 0.24333 을 jacpsd 가 인용한다고 적는다. diag/sigma-coverage_D2_C1_n8.txt:12 checkpoint 는 /home/HTJ/t2/conf/ckpt/d2sx_N10000_a1.pt 이고, tables_D2_B1e4.txt:45 도 맞다.
</details>

### testbed-gate-42 · testbed-gate-42 — `conf/code/figure_f14.py` 96-97 (코드 주석, 출력 무관). 2차 추가 발견

- 방식: **docstring edit** · ✅ 검증 통과

**원문 (HEAD)**

```text
96:     # the gate sentence must follow the CHECKPOINT this run used, not a module default: raw_B16e4* is
97:     # the gate-passing d2sx_N160000_a1, every other raw dir here is a gate-failing sibling.
```

**제안 문구**

```text
old:
    # the gate sentence must follow the CHECKPOINT this run used, not a module default: raw_B16e4* is
    # the gate-passing d2sx_N160000_a1, every other raw dir here is a gate-failing sibling.
new:
    # the gate sentence must follow the CHECKPOINT this run used, not a module default: raw_B16e4* used
    # d2sx_N160000_a1 (no D2 gate row; its D1 sibling passes the gates), every other raw dir here used a
    # checkpoint whose D1 sibling fails GC.  [record correction 2026-09-23, review_next G-1.2]
```

<details><summary>근거</summary>

git show HEAD:conf/code/figure_f14.py l.95-98. 98행 'gate_line = GATE_LINE_PASS if a.raw.startswith("raw_B16e4") else GATE_LINE' 은 동작이 바뀌지 않는다(주석만 교체). tables_D2_B16e4k.txt:45, LADDER_C.md:1, samplecx_D1.txt:28. 생성기 grep 'gate-pass|gate-fail' 로 찾았고 round-1·checker 목록에 없다. 이 파일은 cost-ckpt 그룹에서도 두 번 다루지만(genie 범례 :46 등) 줄이 겹치지 않는다.

검증: 96-97행이 맞고, 98행 동작은 불변이다. raw_B16e4* 외의 raw(B1e4, B1e4lo, B4e4*)는 전부 D1 형제가 GC 에서 FAIL 한 예산(0.24333 / 0.16651)이므로 새 주석의 'fails GC' 가 맞다. cost-ckpt 그룹이 이 파일에서 다루는 줄(:46, 202-227)과 겹치지 않는다.
</details>

### testbed-gate-43 · testbed-gate-43 — `conf/results/NUMBERS_PACKAGE_2026-09-22.md; conf/results/jacpsd_counterfactual_SUMMARY_n256.txt; conf/results/settling_D2.txt` NUMBERS_PACKAGE :3, :679, :729, :751 / jacpsd_counterfactual_SUMMARY_n256.txt:6 / settling_D2.txt:14-17, :67 — 참고만 (편집 안 함)

- 방식: **other** · ✏️ 검증 수정 반영 (인용 OK · 수치 OK · 문구 X)

**원문 (HEAD)**

```text
NUMBERS_PACKAGE_2026-09-22.md:3:      PENDING 표시: B16e4(게이트 통과 + 동일예산), 시드 a3, §6p 저SNR, K=1024@4e4/1.6e5, λ 스윕.
NUMBERS_PACKAGE_2026-09-22.md:679: 44. ❌ *"These diagnostics show the learned prior works."* — Every number in the mechanism family **except the D1 spectrum rows** is a diagnostic probe on a **gate-FAILED** checkpoint, …
NUMBERS_PACKAGE_2026-09-22.md:729: | P1 | **게이트 통과 + 동일예산** 표: V1 이 GMM 을 이김 | … | 학습 arm `d2sx_N160000_a1` — D1 형제 `sx_N160000_D1` PASS (LADDER_C.md:1); D2 자체 게이트 행 없음 | …
NUMBERS_PACKAGE_2026-09-22.md:751: | P13 | **헤드라인 최종 (확장 격자)**: 게이트 통과 학습 prior vs K=1024 GMM, 동일예산 | … | 형제 PASS (`sx_N160000_D1`), D2 자체 행 없음 | …
jacpsd_counterfactual_SUMMARY_n256.txt:6: # SCOPE     : diagnostic probe on the N=1e4 checkpoint, which FAILED the pre-registered gate
settling_D2.txt:67:   - Not an arm result.  The checkpoint here FAILED the pre-registered gates; 10_SPEC_stageC §3c
```

**제안 문구**

```text
NUMBERS_PACKAGE 는 round-1(cost-ckpt-4)이 인라인 노트 대상으로 다뤘으므로 그 관례를 따른다. 결과 txt 만 참고로 둔다.
[NUMBERS_PACKAGE 3행 바로 뒤, 1-4행 HTML 주석 안에 들여쓴 한 줄] 정정 (2026-09-23, review_next G-1.2): "B16e4(게이트 통과 + 동일예산)" 은 "B16e4(D1 형제 게이트 PASS 레시피 + 동일예산)" 로 읽는다. B16e4 의 D2 체크포인트 d2sx_N160000_a1.pt 에는 게이트 행이 없고(tables_D2_B16e4.txt:45), PASS 는 LADDER_C.md:1 의 sx_N160000_D1.pt 행이다. 이 패키지의 P1(729)·P13(751) 게이트 열은 이미 그렇게 한정한다.
[543행 뒤, 들여쓴 인용]   > **정정 (2026-09-23, review_next G-1.2)**: "the equal-budget tables build them from gate-FAILED checkpoints" 는 "… from D2 checkpoints (d2sx_N10000_a1 / d2sx_N40000_a1) that have no gate row (tables_D2_B1e4.txt:45, tables_D2_B4e4.txt:45) and whose D1 siblings FAIL GC (0.24333 / 0.16651, samplecx_D1.txt:28-29)" 로 읽는다. 이 패키지 418·575 가 같은 유형을 이미 지목했다.
[679행 뒤, 680 빈 줄 앞] > **정정 (2026-09-23, review_next G-1.2)**: 44번의 "a diagnostic probe on a gate-FAILED checkpoint" 는 D2 탐침 체크포인트에 판정을 직접 붙인 줄임말이다. 그 D2 체크포인트들에는 게이트 행이 없다(d2sx_N10000_a1.pt: tables_D2_B1e4.txt:45, results/diag/SUMMARY.md:4, settling_D2.txt:14). 그중 d2sx_N10000_a1.pt 는 같은 레시피의 N=1e4 D1 기록이 GC 에서 FAIL 이다(0.24333 samplecx_D1.txt:28 / 0.224111 hpo_final_r2.txt trial 386. 어느 쪽인지는 402-406 대로 밝힌다). 읽는 법: "a diagnostic probe on an UN-GATED D2 checkpoint (PAPER_MATERIALS §17.3)". 같은 줄의 "D1 spectrum rows use a gate-PASSING checkpoint" 는 D1 체크포인트(sx_N160000_D1.pt)라 맞다. 철회 문구 자체는 불변이다.
:729 P1·:751 P13 사실 열은 게이트 열이 '형제 PASS, D2 자체 행 없음' 으로 한정하므로 두고, :734 '게이트 통과 예산' 은 예산 표현이라 둔다.
참고만(생성된 결과 txt, 편집 안 함): jacpsd_counterfactual_SUMMARY_n256.txt:6-7, settling_D2.txt:14-17·:67-68. jacpsd 문구는 code/cf_rollup.py:46 의 문자열에서 나오므로, 다음 재생성에 대비해 생성기 주석을 달 수 있다(선택).
이에 맞춰 G-1.2 DECISIONS 행(testbed-gate-23)의 '생성된 결과 파일(NUMBERS_PACKAGE P1/P13 사실 열, jacpsd_counterfactual_SUMMARY_n256.txt:6, settling_D2.txt:67)은 손대지 않는다' 를 다음으로 바꾼다: 'NUMBERS_PACKAGE :3·:543·:679 에는 cost-ckpt-4 와 같은 인라인 노트를 달았다(P1/P13 사실 열은 게이트 열 한정으로 충분해 둔다). 생성된 결과 txt(jacpsd_counterfactual_SUMMARY_n256.txt:6, settling_D2.txt:14-17·:67)는 손대지 않는다'.
```

<details><summary>검증 agent 지적 / 초안 원안</summary>

지적: 인용한 줄은 모두 맞다: NUMBERS_PACKAGE :3, :679, :729, :751, :418, :575, jacpsd:6, settling:14-17·:67. 관례 문제: 이번 검증 관례는 'NUMBERS_PACKAGE 와 docs/EXPERIMENTS.md 는 round-1(cost-ckpt-4/-5/-17)에서 인라인 노트를 받았으니 따른다' 다. 따라서 NUMBERS_PACKAGE 를 '참고만' 으로 두고 사용자에게 넘기면 안 된다. :3 과 :679 에는 노트를 초안으로 써야 한다. 같은 유형인 :543('the equal-budget tables build them from gate-FAILED checkpoints')이 목록에서 빠졌다. :679 의 탐침 체크포인트에는 d2sx_N10000_a1 말고 N=1.6e5 스냅샷도 있다(PM:811). 그래서 노트는 '게이트 FAIL' 대신 §17.3 용어 'UN-GATED' 로 한정해야 과잉 정정이 없다. jacpsd·settling txt 는 참고만으로 두는 것이 맞다. jacpsd:6 문구의 생성기는 code/cf_rollup.py:46 이다.

초안 원안:

```text
참고만 한다(생성된 결과 파일이라 편집하지 않는다). 같은 줄임말이 남아 있는 곳: NUMBERS_PACKAGE:3 'B16e4(게이트 통과 + 동일예산)', :679 'gate-FAILED checkpoint', :729 P1 과 :751 P13 의 사실 열 '게이트 통과 …'(게이트 열이 '형제 PASS, D2 자체 행 없음' 으로 한정하므로 PM 905 와 같은 유형), jacpsd_counterfactual_SUMMARY_n256.txt:6, settling_D2.txt:14-17·:67. G-1.2 DECISIONS 행(testbed-gate-23 검증 수정본)이 '생성된 결과 파일(…)은 손대지 않는다' 로 이미 처리한다. NUMBERS_PACKAGE 는 :418·:575 에서 이 결함(STATUS:825, 10_SPEC:453)을 스스로 지목했다. 사용자 판단: cost-ckpt-4 선례처럼 NUMBERS_PACKAGE 에 인라인 노트를 달기로 하면 후보는 :3 과 :679 두 곳이다(:729/:751 은 게이트 열 한정으로 충분).
```
</details>

<details><summary>근거</summary>

git show HEAD:conf/results/NUMBERS_PACKAGE_2026-09-22.md l.3, 418, 575, 679, 729, 751. git show HEAD:conf/results/jacpsd_counterfactual_SUMMARY_n256.txt l.6-7. git show HEAD:conf/results/settling_D2.txt l.14-17, 67. 이번 작업 지시가 이 파일들을 'Reference only (generated files, not edited)' 로 지정했고, round-1 testbed-gate-23 도 같은 처리를 했다. 한편 전역 관례는 NUMBERS_PACKAGE 에 round-1 인라인 노트(cost-ckpt-4)가 있으면 그것을 따르라고 한다. 두 지시가 충돌하므로 선택은 사용자에게 넘긴다.

검증: (위 참조)
</details>

### testbed-gate-44 · testbed-gate-44 — `N/A` N/A

- 방식: **other** · ✏️ 검증 수정 반영 (인용 OK · 수치 OK · 문구 X)

**원문 (HEAD)**

```text
N/A
```

**제안 문구**

```text
사용자 판단 대상 목록 (정정 초안에 넣지 않음): (1) checker 가 대상 아님으로 분류한 곳: STATUS 427·439·447(D1 체크포인트), 10_SPEC_stageC 339-340·364(D1), PAPER_MATERIALS 443·566(D1), figures_stagec.py:25·:620(D1 gate-passing), tables_D2_*.txt:43 'no GATE-PASSING checkpoint'(사실과 일치). (2) 다시 확인해 대상 아님으로 둔 곳: '미게이트/UN-GATED' 표기(STATUS 313, PAPER_MATERIALS 473·801·811·837·953·967·969, figures_stagec.py:40·298·400·516)는 D2 게이트 행이 없다는 사실과 맞는다. DECISIONS 27·42 는 'D1 게이트를 통과하지 못했다' 로 이미 한정돼 있다. STATUS 107·151·617·637, PM 764·803, 10_SPEC 11·20·23·43·50·52·107·126·131·138·163·175·202·506·507 은 D1 이거나 일반 규칙이다. STATUS 421(D1 게이트로 한정)·429(폐기 표시된 인용)·604/606·879(V2/V3 의 D1 체크포인트)와 PM 839·842·1007(V2/V3 D1 쌍둥이)은 D1 판정이다. STATUS 744 는 같은 명제에 '형제-자격 연결 위에서만 성립' 이라는 한정이 이미 붙어 있다. code/runner.py:160·175·185 와 score.py:16·1142·1147·1161 의 'gate-passing checkpoint' 는 D2 에 그런 체크포인트가 없다는 사실과 맞고, run_B3.py:18 과 run_d1_variant.py:28·71 은 D1 이다. 예산 표현 STATUS 1113·1416·1454·1633, PM 904·908 괄호, NUMBERS_PACKAGE:734, docs/EXPERIMENTS.md:21 '동작 범위(게이트 통과 예산)', queue2.sh:35, queue_after_B1e4x.sh:23 은 round-1 기준대로 제외한다. (3) 그룹 밖 관찰(정정 초안 미작성): PAPER_MATERIALS:906 (b) '격차 0.107/0.105/0.108' 은 F15 캡션(figures_stagec3.py:213 'gap 0.107 / 0.106 / 0.108')과 가운데 값이 다르다(0.2504−0.1445=0.1059). 같은 행 (c) 'BLER 불변' 은 캡션의 'BLER moves 0.2504→0.2480 / 0.2527→0.2434'(1.0%·3.7%)보다 강한 표현이다. STATUS:1604 'K 격자를 우도가 오르는 한계(K=1024)까지' 는 N=4e4 에서 K=512→2048 로 검증 우도가 계속 올랐고(+2.16 nat, figures_stagec3.py:220-221), N=1.6e5 에서 K=2048 을 적합하지 않은 이유가 비용(STATUS:1610-1612 '1 재시작에 ~9 h')이라는 점과 맞지 않는다. 한계는 우도 포화가 아니라 계산 예산이다. 감사에 없는 항목이다. (PM:29 는 missing 의 PM 23-25 노트와 함께 다루므로 이 목록에서 뺐다.)
```

<details><summary>검증 agent 지적 / 초안 원안</summary>

지적: (1)·(2)의 분류를 HEAD 에서 다시 확인했다. 모두 맞다: STATUS 427·439·447·604/606(D1), 313·PM 473/801/811/837/953/967/969·figures_stagec.py:40/298/400/516('미게이트/UN-GATED'), DECISIONS 27·42('D1 게이트를 통과하지 못했다'). (4)의 산술도 맞다: 0.2523−0.1453=0.1070, 0.2504−0.1445=0.1059, 0.2527−0.1449=0.1078. 캡션 figures_stagec3.py:213 은 'gap 0.107 / 0.106 / 0.108', :221-224 는 1.0%·3.7% 다. 문제는 (3)이다. PM:29 를 경계 사례로 사용자에게 넘겼지만, 같은 문단 23-25행 '예산을 N'=1.6e5 로 올린 학습 score 가 D1 게이트를 **통과**했고 (…), 그 체크포인트로 두 testbed 의 확증 BLER 을 n = 2560 으로 돌렸다' 는 사실 오류라 초안 대상이다. D2 확증은 별도 D2 재학습본 d2sx_N160000_a1.pt 로 돌렸다(tables_D2_C.txt:37-39,44-45). D1 게이트를 통과한 것은 sx_N160000_D1.pt 다(STATUS:439). 23-25행은 굵은 글씨가 끼어 '게이트를 통과' grep 에 걸리지 않았다. 29행은 23-25 노트와 함께 다뤄야 하므로 사용자 판단 목록에서 뺀다. 재확인하며 대상 아님으로 분류한 곳도 목록에 더한다.

초안 원안:

```text
사용자 판단 대상 목록 (정정 초안에 넣지 않음): (1) checker 가 대상 아님으로 분류한 곳 — STATUS 427·439·447(D1 체크포인트), 10_SPEC_stageC 339-340·364(D1), PAPER_MATERIALS 443·566(D1), figures_stagec.py:25·:620(D1 gate-passing), tables_D2_*.txt:43 'no GATE-PASSING checkpoint'(사실과 일치). (2) 이번에 다시 확인해 대상 아님으로 둔 곳 — '미게이트/UN-GATED' 표기(STATUS 313, PAPER_MATERIALS 473·801·811·837·953·967·969, figures_stagec.py:40·298·400·516)는 D2 게이트 행이 없다는 사실과 맞는다. DECISIONS 27·42 는 'D1 게이트를 통과하지 못했다' 로 이미 한정돼 있다. STATUS 107·151 은 일반 서술이다. STATUS 604 V2 는 D1 체크포인트 `sx_V2_N160000_D1_a3.pt` 다. 예산 표현 STATUS 1113·1416·1454·1633 과 PM 904·908 괄호는 round-1 에서 이미 제외했다. (3) 경계, 사용자 결정 — PAPER_MATERIALS:29 '게이트 통과가 수신기 사용 가능성을 보증하지 않는다는 것이 이 실행의 실측 결과다' 는 692행과 같은 일반 명제다. 692행은 testbed-gate-31 노트에 넣었고 29행은 넣지 않았다. (4) 그룹 밖 관찰, 정정 초안 미작성 — PAPER_MATERIALS:906 (b) '격차 0.107/0.105/0.108' 은 F15 캡션(figures_stagec3.py:213 'gap 0.107 / 0.106 / 0.108')과 가운데 값이 다르다(0.2504−0.1445=0.1059). 같은 행 (c) 'BLER 불변' 은 캡션의 'BLER moves 0.2504→0.2480 / 0.2527→0.2434'(1.0%·3.7%)보다 강한 표현이다.
```
</details>

<details><summary>근거</summary>

round-1 checker 누락 위치 목록의 '문제없는 용례(대상 아님)' 줄(RECORD_CORRECTIONS_DRAFT.md 테스트베드 그룹 누락 위치). HEAD 에서 grep -nE '게이트 통과|게이트를 통과|미통과|미게이트|게이트 실패|게이트에 실패|gate-pass|gate-fail|FAILED the' 를 STATUS·PAPER_MATERIALS·10_SPEC·DECISIONS·figures_stagec*.py 에 돌려 재분류했다. STATUS:606 'ckpt/sx_V2_N160000_D1_a3.pt'. figures_stagec3.py:211-224 캡션 (b)(c) 수치. 산술: 0.2523−0.1453=0.1070, 0.2504−0.1445=0.1059, 0.2527−0.1449=0.1078.

검증: (위 참조)
</details>

---

## 2차 · 복잡도 4.6x·체크포인트 (P0-2b, cost/M1·M2, P0-1b, ckpt/M2)

### cost-ckpt-24 · cost-ckpt-24 — `conf/code/bench_moduleH.py` 3-5, 11 (검증 agent 는 '12' 라 적었으나 HEAD 에서 'the GMM is b* …' 는 11행이다. 12행 'both are timed on the same nu grid …' 은 대상 아님)

- 방식: **docstring edit** · ✏️ 검증 수정 반영 (인용 OK · 수치 OK · 문구 X)

**원문 (HEAD)**

```text
L3: The receiver calls Module H ONCE per outer iteration (16 per trial), through the identical entry point
L4: `prior.denoise_full(q, nu) -> (m, J)`.  Everything else in the loop is shared by every arm, so this
L5: single call IS the complexity difference between the arms.  Nothing else here is claimed.
L11:   - the GMM is b* selected by validation log-likelihood, exactly the arm in the BLER tables
```

**제안 문구**

```text
[3-5 교체, 5행이 된다]
Times `prior.denoise_full(q, nu) -> (m, J)` for both priors: an isotropic microbenchmark.  Nothing else is
claimed.  NOTE (review_next P0-2a/P0-2b, 2026-09-23): this is NOT the arm-to-arm receiver cost difference.
The headline GMM arm M-ours-bstar never calls denoise_full: once per outer iteration it calls
GMMPriorB.ep_site(G, b, lam_min) (arms.py:36,163; Demo/t2_route_a.py:373-374), which is not timed here.
The score side does time the receiver's call (one network+Jacobian evaluation per outer iteration).

[11 교체, 3행이 된다]
  - the GMM is b* selected by validation log-likelihood from the N=1e4 fits (NTRAIN below -> kron K=512;
    not the K=1024 headline b*).  It is the fit M-ours-bstar uses in the N=1e4 tables, but timed here
    through denoise_full, not through that arm's .view("eta").ep_site call (see NOTE)

(docstring 만 바뀌고 동작은 불변. cost-ckpt-12 의 DECISIONS 선택 필드 'bench_moduleH.py 3-5·12' 는 '3-5·11' 로 고칠 것 — cost-ckpt-40 참조.)
```

<details><summary>검증 agent 지적 / 초안 원안</summary>

지적: 인용(3-5·11) HEAD 그대로, :30-31·:77·complexity_moduleH.txt:5·arms.py:36,163·t2_route_a.py:373-374 확인. 문제 1건: 새 11행의 'same prior object as M-ours-bstar' 가 과함. bench 는 gm[bstar](module_h_priors 의 원 GMMPriorB, bench_moduleH.py:49-50)를 쓰고, M-ours-bstar 는 hp[bstar].view("eta") 를 받아(arms.py:163) ep_site 를 부른다. 게다가 같은 fit 은 N=1e4 표의 M-ours-bstar 뿐이고 헤드라인(K=1024)은 아니다. 11행 교체문만 고쳤다.

초안 원안:

```text
[3-5 교체, 5행이 된다]
Times `prior.denoise_full(q, nu) -> (m, J)` for both priors: an isotropic microbenchmark.  Nothing else is
claimed.  NOTE (review_next P0-2a/P0-2b, 2026-09-23): this is NOT the arm-to-arm receiver cost difference.
The headline GMM arm M-ours-bstar never calls denoise_full: once per outer iteration it calls
GMMPriorB.ep_site(G, b, lam_min) (arms.py:36,163; Demo/t2_route_a.py:373-374), which is not timed here.
The score side does time the receiver's call (one network+Jacobian evaluation per outer iteration).

[11 교체, 2행이 된다]
  - the GMM is b* selected by validation log-likelihood from the N=1e4 fits (NTRAIN below -> kron K=512;
    not the K=1024 headline b*); same prior object as M-ours-bstar, but not that arm's call (see NOTE)

(docstring 만 바뀌고 동작은 불변. cost-ckpt-12 의 DECISIONS 선택 필드 'bench_moduleH.py 3-5·12' 는 '3-5·11' 로 고칠 것 — cost-ckpt-40 참조.)
```
</details>

<details><summary>근거</summary>

git show HEAD:conf/code/bench_moduleH.py 3-5·11 원문 그대로 (working tree 도 HEAD 와 같음, git status 에 없음). :30-31 NTRAIN=10000, CKPT=d2sx_N10000_a1.pt; :77 'tg = timed(gmm.denoise_full, qs, nu)'. complexity_moduleH.txt:5 'b* = kron (K = 512 components)'. arms.py:36 gmm_site=dict(mode="colored", …, exact_prior=True); :163 M-ours-bstar=route_a(*a, hp[bstar].view("eta"), …, "gmm_site"); Demo/t2_route_a.py:373-374 'if self.exact_prior: Lam, site_vec = self.prior.ep_site(G, b, self.lam_min)'. score 쪽이 수신기 호출을 잰다는 점과 나머지 작업이 1 ms 미만이라는 점은 REVIEW_AUDIT P0-2a 반박 검토에서 확인됐다. headline raw_B16e4k 는 448/448 kron_K=1024 (cost-ckpt-1 근거).

검증: (위 참조)
</details>

### cost-ckpt-25 · cost-ckpt-25 — `conf/results/NUMBERS_PACKAGE_2026-09-22.md` 195 (삽입: 195 뒤, 196 빈 줄 앞)

- 방식: **other** · ✅ 검증 통과

**원문 (HEAD)**

```text
L195: **D2, gate NOT VERIFIABLE BY CONSTRUCTION** — D2 has no true score, so GA–GD are D1-only (`04_SPEC §5`). Diagnostic probe on `ckpt/d2sx_N160000_a1.pt` (patience-stopped 1784 epochs, best val 3.519379e-01 @1764, sha256 4443921ce8d5c4a1…). Equal budget **NO**: learned N=1.6e5 vs FITTED kron K=512 at N=1e4 (16×). Source `jac_spectrum.txt:132-138` (ADDENDUM 2026-09-21 23:50).
```

**제안 문구**

```text
> **정정 (2026-09-23, review_next P0-1b)**: 이 탐침이 읽은 가중치는 `d2sx_N160000_a1.pt` 의 **마지막 epoch(1784) EMA** 다. 경로는 `jac_spectrum.py:42` → `score._as_model` → `load_model` 이고 `load_model` 이 `st["ema"]` 를 읽는다(ema sha256[:16] a43f1105eb27a29b, 이 가중치의 val 3.519602e-01). 괄호 안 "best val 3.519379e-01 @1764" 는 저장되지 않은 @1764 가중치의 값이다(BEST_WEIGHTS_UNAVAILABLE). 아래 스펙트럼 수치는 @1784 EMA 의 값이며 바뀌지 않는다.
```

<details><summary>근거</summary>

CPU torch.load conf/ckpt/d2sx_N160000_a1.pt: epoch 1784, best_epoch 1764, best_val 3.519379e-01, hist[-1] val 3.519602e-01, file sha256[:16] 4443921ce8d5c4a1, ema a43f1105eb27a29b (정렬 키+바이트 해시, 1차 초안과 같은 방식). HEAD jac_spectrum.py:42 'score._as_model(a.ckpt, NR, NT, "cpu")[0]'; score.py:1188-1192 _as_model → load_model; :1025 st["ema"]. 탐침 시점: ckpt mtime 09-21 22:37, logs/jacspec_D2_final.log mtime 23:47. 1차 초안 cost-ckpt-16 은 근거 필드에 NUMBERS_PACKAGE:195 를 적었지만 인라인 주석은 없었다. 1차 초안이 NUMBERS_PACKAGE 에 인라인 주석을 달았으므로(cost-ckpt-4) 같은 방식을 따른다.

검증: 없음. 195 HEAD 그대로, 196 빈 줄. CPU 에서 다시 읽음: 1784/1764, best 3.519379e-01, @1784 3.519602e-01, file 4443921ce8d5c4a1, ema a43f1105eb27a29b (정렬 키+바이트 해시로 재현). jac_spectrum.py:42 는 측정 커밋 ee6ae61 에서도 _as_model 을 쓴다. ckpt mtime 22:37:02 < 로그 헤더 23:11:50 < 로그 mtime 23:47.
</details>

### cost-ckpt-26 · cost-ckpt-26 — `conf/PAPER_MATERIALS.md` 415-416 (§12.3; 삽입: 416 뒤, 417 빈 줄 앞)

- 방식: **PAPER_MATERIALS inline note** · ✅ 검증 통과

**원문 (HEAD)**

```text
L415: 체크포인트 `conf/ckpt/d2sx_N160000_a1.pt` (sha256 `4443921ce8d5c4a1…`, `stopped_by=patience`,
L416: **1784 epoch**, best val **3.519379e-01 @1764**). `logs/jacspec_D2_final.log`, n = 48.
```

**제안 문구**

```text
> **정정 (2026-09-23, review_next P0-1b)**: §12.3 의 스펙트럼은 이 파일의 **마지막 epoch(1784) EMA** 로 측정됐다. `jac_spectrum.py:42` → `score._as_model` → `load_model` 경로가 `st["ema"]` 를 읽는다(ema sha256[:16] a43f1105eb27a29b, 이 가중치의 val 3.519602e-01). 파일 mtime 09-21 22:37 이 측정(로그 23:47)보다 앞선다. "best val 3.519379e-01 @1764" 는 저장되지 않은 @1764 가중치의 값이다(BEST_WEIGHTS_UNAVAILABLE). 표 수치는 바뀌지 않는다. 원고에 "best 체크포인트에서 측정" 으로 쓰지 말 것. 620 행 뒤 정정을 볼 것.
```

<details><summary>근거</summary>

cost-ckpt-25 와 같은 CPU 체크포인트 판독 및 코드 경로. PAPER_MATERIALS.md:413 제목이 'ADDENDUM 2026-09-21 23:50 — D2 를 **최종 체크포인트**로 재측정'이고, 415-416 이 HEAD 원문 그대로다. 417 은 빈 줄, 418 은 코드블록 시작. 1차 초안 cost-ckpt-18 검증이 416 을 누락 위치로 지목했다.

검증: 없음. 413 제목, 415-416 HEAD 그대로, 417 빈 줄, 418 코드블록 확인. 수치는 cost-ckpt-25 와 같다.
</details>

### cost-ckpt-27 · cost-ckpt-27 — `conf/results/jac_spectrum.txt, conf/figs/F7_jacspectrum_D1_D2.txt (generator conf/code/figures_stagec.py), conf/results/d2_gbprime.csv` jac_spectrum.txt 125-127 · F7 txt 24-26 (생성기 figures_stagec.py 288-290) · d2_gbprime.csv 2-8 (검증 agent 는 8행만 지목했지만 2-8행 모두 같은 형태다)

- 방식: **other** · ✅ 검증 통과

**원문 (HEAD)**

```text
jac_spectrum.txt L125: audit flagged as irreproducible.  The N'=1.6e5 D2 training has since finished (stopped_by=patience,
jac_spectrum.txt L126: 1784 epochs, best val 3.519379e-01 @1764) and the checkpoint is permanent:
jac_spectrum.txt L127:     conf/ckpt/d2sx_N160000_a1.pt   sha256 4443921ce8d5c4a1...
F7 L24: WHICH D2 CHECKPOINT, AND WHY NOT THE EARLIER ONE.  Panel (b) is measured on ckpt/d2sx_N160000_a1.pt,
F7 L25: the permanent checkpoint at which that run stopped (patience, 1784 epochs, best val 3.519379e-01 at
F7 L26: epoch 1764).  It is NOT the epoch-240 snapshot of logs/jacspec_D2_N160000.log: that measurement was
d2_gbprime.csv L8: 160000,1,10000,False,1784,3.519379e-01,kron,512,4096,0.418279,0.866778,0.463761,-0.133222
```

**제안 문구**

```text
reference only — 이미 생성된 결과·그림 파일이라 편집하지 않는다. 각 파일은 저장된 마지막 epoch EMA 로 잰 값에 best val 을 짝지어 적었다. jac_spectrum.txt:126·F7:25-26 은 1784 epoch 판을 쟀는데 best val @1764 를 붙였다. d2_gbprime.csv 는 2-8행 모두 epochs 열에 마지막 epoch, val_loss 열에 best val 을 적었고, GB' 는 마지막 epoch EMA 로 계산했다. 정정 기록은 NUMBERS_PACKAGE:195 뒤와 PAPER_MATERIALS:416 뒤 주석(cost-ckpt-25/26), 그리고 DECISIONS P0-1b 행(cost-ckpt-16)이 맡는다.
(선택, 재생성할 때만) 생성기 figures_stagec.py:289-290
old: the permanent checkpoint at which that run stopped (patience, 1784 epochs, best val 3.519379e-01 at
     epoch 1764).  It is NOT the epoch-240 snapshot of logs/jacspec_D2_N160000.log: that measurement was
new: the permanent checkpoint at which that run stopped (patience, 1784 epochs; the file holds the epoch-1784
     EMA, val 3.519602e-01 -- the best-val epoch 1764, 3.519379e-01, was not stored).  It is NOT the epoch-240
     snapshot of logs/jacspec_D2_N160000.log: that measurement was
```

<details><summary>근거</summary>

git show HEAD 로 세 파일 원문을 확인했다. run_d2_sx.py:41 에서 G = score.gb_prime(ck, …)(score.py:1345 _as_model → load_model → st["ema"])이고, :51 이 res['epochs'](마지막)와 res['val_loss'](best)를 쓴다. CPU torch.load(epoch/best_epoch/best_val/last val): N2500_a1 597/577/4.338475e-01/4.339755e-01, N10000_a2 657/637/4.038046e-01/4.039307e-01, N10000_a3 662/642/4.048188e-01/4.049475e-01, N10000_a1 673/653/3.985658e-01/3.986240e-01, N160000_a3 1044/1024/3.525231e-01/3.525437e-01, N160000_a2 1378/1358/3.547692e-01/3.548169e-01, N160000_a1 1784/1764/3.519379e-01/3.519602e-01. 따라서 csv 의 val_loss 열은 7행 모두 best val 이다. figures_stagec.py:288-290 이 F7:24-26 을 만든다. audit P0-1a 반박이 csv 8행을 지목했다.

검증: 없음. jac_spectrum.txt:125-127, F7:24-26, figures_stagec.py:288-290, csv:8 모두 HEAD 그대로. 7개 ckpt 의 epoch/best_epoch/best_val/last val 을 CPU 로 전부 재현했고, csv 의 val_loss 열은 7행 모두 best 다(4ad41df9 train 이 val_loss=best, epochs=ep 를 반환; run_d2_sx.py:41 gb_prime(ck)→_as_model→load_model). 'reference only' 로 시작하고 생성기 변경은 '선택' 으로 표시돼 규약에 맞다.
</details>

### cost-ckpt-28 · cost-ckpt-28 — `conf/STATUS.md` 439 (문단 438-441; 삽입: 441 뒤, 442 빈 줄 앞)

- 방식: **STATUS inline note** · ✏️ 검증 수정 반영 (인용 OK · 수치 OK · 문구 X)

**원문 (HEAD)**

```text
L439: 체크포인트 `ckpt/sx_N160000_D1.pt` (GA/GB/GC/GD 전부 PASS). raw 336개 → `results/tables_D1_C.txt`.
```

**제안 문구**

```text
> **정정 (2026-09-23, review_next P0-1b·ckpt/M2)**: 이 절의 실행은 이 파일의 **마지막 epoch(200) EMA** 로 평가됐다(ema sha256[:16] ae04fefa33998484, 이 가중치의 val 7.398687e-01). 16:30 기록 시점의 336파일과 이후 n=2560 전량, 즉 현재 `raw_C` D1 1344파일이 모두 여기에 해당한다. 전부 `meta|stagec_ckpt` = `sx_N160000_D1.pt` 이고, 학습 arm V0/V1/V4 → `tables_D1_C.txt` 다. best val 7.398444e-01 @136 의 가중치는 저장되지 않았다(BEST_WEIGHTS_UNAVAILABLE). 괄호의 "GA/GB/GC/GD 전부 PASS" 도 같은 @200 EMA 에서 측정됐다(ckpt mtime 09-21 09:14 < 게이트 14:12 < raw_C D1 16:01–19:07). 그러므로 "게이트를 통과한 가중치로 돌린 확증 실행" 은 그대로 성립한다. best(@136) 가중치로 잰 게이트와 BLER 은 존재하지 않는다. 376 행 뒤 정정을 볼 것.
```

<details><summary>검증 agent 지적 / 초안 원안</summary>

지적: 인용·수치 OK: raw_C D1 1344/1344 stagec_ckpt sx_N160000_D1.pt, arm V0/V1/V4, mtime 09-21 16:01:52–19:07:40. ckpt 200/136, 7.398444e-01/7.398687e-01, ema ae04fefa33998484, mtime 09:14:59. 문구 1건: 첫 문장 '이 실행의 대상은 raw_C 의 D1 파일 전부(현재 1344개…)다' 가 16:30 에 기록된 이 실행(336파일)과 맞지 않는다. 또 원문의 'raw 336개' 를 고치는 것처럼 읽힌다. 근거 필드는 336 을 고치지 않는다고 적었다. 첫 문장만 고쳤다.

초안 원안:

```text
> **정정 (2026-09-23, review_next P0-1b·ckpt/M2)**: 이 실행의 대상은 `raw_C` 의 D1 파일 전부(현재 1344개, `meta|stagec_ckpt` = `sx_N160000_D1.pt`; 학습 arm V0/V1/V4 → `tables_D1_C.txt`)다. 이 실행은 이 파일의 **마지막 epoch(200) EMA** 로 평가됐다(ema sha256[:16] ae04fefa33998484, 이 가중치의 val 7.398687e-01). best val 7.398444e-01 @136 의 가중치는 저장되지 않았다(BEST_WEIGHTS_UNAVAILABLE). 괄호의 "GA/GB/GC/GD 전부 PASS" 도 같은 @200 EMA 에서 측정됐다(ckpt mtime 09-21 09:14 < 게이트 14:12 < raw_C D1 16:01–19:07). 그러므로 "게이트를 통과한 가중치로 돌린 확증 실행" 은 그대로 성립한다. best(@136) 가중치로 잰 게이트와 BLER 은 존재하지 않는다. 376 행 뒤 정정을 볼 것.
```
</details>

<details><summary>근거</summary>

CPU 에서 raw_C/D1_*.npz 를 읽었다: 1344/1344 가 meta|stagec_ckpt '/home/HTJ/t2/conf/ckpt/sx_N160000_D1.pt' 이고, 학습 arm 은 M-ours-dscore-C-V0/V1/V4, mtime 은 2026-09-21 16:01:52–19:07:40 이다. tables_D1_C.txt:39-41,45 가 같은 ckpt 를 적는다. CPU torch.load sx_N160000_D1.pt: epoch 200, best_epoch 136, best_val 7.398444e-01, hist val@200 7.398687e-01, file 9a38b0c9535d64a5, ema ae04fefa33998484. ckpt mtime 은 2026-09-21 09:14:59 로 그 뒤 바뀌지 않았고, LADDER_C.md:1 게이트는 [2026-09-21 14:12] 이다. 'raw 336개' 는 16:30 시점의 n=640 중간본(21점×16파일)이라 고치지 않는다. G-1.2 그룹이 RECORD_CORRECTIONS_DRAFT:1414 에서 STATUS 439 를 '문제없는 용례' 로 분류한 것은 D2 체크포인트를 게이트 통과라 부르는지를 본 것이다. 이 주석은 last-EMA 표기만 더하므로 그 분류와 충돌하지 않는다.

검증: (위 참조)
</details>

### cost-ckpt-29 · cost-ckpt-29 — `conf/PAPER_MATERIALS.md` 566 (§14 첫 글머리표 565-571; 삽입: 571 뒤, 572 '- `M-ours-dscore-C-V4b`' 앞, 2칸 들여쓴 인용)

- 방식: **PAPER_MATERIALS inline note** · ✅ 검증 통과

**원문 (HEAD)**

```text
L565: - 실행 조건: **전 격자점 n = 2560**, 셀 C1(Tp=2)/C2(Tp=4)/C5(Tp=3) x SNR 7점, `raw_C` 1344 파일.
L566:   체크포인트 `ckpt/sx_N160000_D1.pt` (**게이트 PASS**, §11.2).
```

**제안 문구**

```text
> **정정 (2026-09-23, review_next P0-1b·ckpt/M2)**: `sx_N160000_D1.pt` 가 담은 가중치는 마지막 epoch(200) EMA 다(ema sha256[:16] ae04fefa33998484, 이 가중치의 val 7.398687e-01). best val 7.398444e-01 @136 의 가중치는 저장되지 않았다(BEST_WEIGHTS_UNAVAILABLE). §14 의 학습 arm(V0/V1/V4, `raw_C` D1 1344파일)과 §11.2 의 게이트 PASS 는 둘 다 이 같은 @200 EMA 에서 측정됐다. 원고에 "best 체크포인트" 로 쓰지 말 것.
```

<details><summary>근거</summary>

cost-ckpt-28 과 같은 raw meta 판독 및 체크포인트 판독이다. 565-566 은 HEAD 원문 그대로이고, 글머리표는 571 에서 끝나며 572 가 다음 글머리표다. 1차 초안 cost-ckpt-18 의 형식(글머리표 끝, 2칸 들여쓴 인용)을 따랐다. G-1.2 가 PM 566 을 '문제없는 용례' 로 분류한 것(RECORD_CORRECTIONS_DRAFT:1414)은 다른 관점이다. 이 주석은 last-EMA 표기만 한다.

검증: 없음. 565-566 HEAD 그대로, 571 에서 글머리표가 끝나고 572 가 다음 글머리표다. 수치는 cost-ckpt-28 과 같다.
</details>

### cost-ckpt-30 · cost-ckpt-30 — `conf/code/figures_stagec.py (F10 caption generator); conf/figs/F10_bler_D1_confirmatory.txt` figures_stagec.py 619-621 (→ F10 txt 45-47). F10 txt·PNG 는 reference only

- 방식: **caption/generator note** · ✅ 검증 통과

**원문 (HEAD)**

```text
L619: GATE STATUS.  The Stage C arms use ckpt/sx_N160000_D1.pt, which PASSES all four pre-registered gates
L620: (LADDER_C.md SX160000: GA 9.879e-16, GB +0.27%, GC 0.0999, GD 0.0718).  This is a gate-passing
L621: confirmatory run, not a probe.
```

**제안 문구**

```text
old (figures_stagec.py:619-621):
GATE STATUS.  The Stage C arms use ckpt/sx_N160000_D1.pt, which PASSES all four pre-registered gates
(LADDER_C.md SX160000: GA 9.879e-16, GB +0.27%, GC 0.0999, GD 0.0718).  This is a gate-passing
confirmatory run, not a probe.
new:
GATE STATUS.  The Stage C arms use ckpt/sx_N160000_D1.pt, which PASSES all four pre-registered gates
(LADDER_C.md SX160000: GA 9.879e-16, GB +0.27%, GC 0.0999, GD 0.0718).  This is a gate-passing
confirmatory run, not a probe.  The gates and this run read the same weights, the file's last-epoch
EMA (epoch 200, val 7.398687e-01); the best-val epoch 136 (7.398444e-01) was not stored.
(적용 조건: 다음 재생성부터 캡션 문구만 바뀌고 수치 계산은 그대로다. 이미 생성된 F10 txt(45-47)와 PNG/PDF 는 재생성하지 않고 reference only 로 둔다. 기록은 STATUS 441 뒤와 PAPER_MATERIALS 571 뒤 주석이 맡는다.)
```

<details><summary>근거</summary>

git show HEAD:conf/code/figures_stagec.py 619-621 과 F10_bler_D1_confirmatory.txt 45-47 이 같은 문장이다(생성기 :587 _save(fig, "F10_bler_D1_confirmatory", …)). F10 의 학습 arm 은 tables_D1_C.txt ← raw_C D1 1344파일(sx_N160000_D1.pt @200 EMA)에서 온다. 게이트(LADDER_C.md:1, 14:12)도 같은 파일·같은 mtime(09:14:59)을 읽었다. 1차 초안 규약에 따라 figs/*.txt 는 편집하지 않는다(F10 은 1차에서 편집 대상으로 다루지 않았다). G-1.2 가 figures_stagec.py:620 을 D1 용례라 '문제없음' 으로 분류한 것과 충돌하지 않는다. 이 변경은 게이트 판정을 건드리지 않고 last-EMA 표기만 더한다.

검증: 없음. figures_stagec.py:619-621 은 :587 에서 시작하는 삼중따옴표 문자열 안에 있고, F10 txt:45-47 과 같은 문장이다. 게이트 판정은 그대로 두고 last-EMA 표기만 더한다. F10 txt 와 PNG 는 reference only 로 둔다.
</details>

### cost-ckpt-31 · cost-ckpt-31 — `conf/PAPER_MATERIALS.md` 483-484 (§13.1 체크포인트 식별 줄 = raw_supp BLER(표 3번)의 체크포인트; 삽입: 484 뒤, 485 빈 줄 앞)

- 방식: **PAPER_MATERIALS inline note** · ✏️ 검증 수정 반영 (인용 OK · 수치 OK · 문구 X)

**원문 (HEAD)**

```text
L483: 체크포인트 `ckpt/d2sx_N10000_a1.pt` (sha256 `d94aa99bdc5689067f90895b28d6394e7c61a296ed58ada3f041eb4ad8fdf01a`,
L484: HPO trial 386), D2 셀 C2.
```

**제안 문구**

```text
> **정정 (2026-09-23, review_next P0-1b)**: 이 파일(sha256 `d94aa99b…`)의 가중치는 **마지막 epoch(673) EMA** 다(ema sha256[:16] 62432fd33f0c9378, 이 가중치의 val 3.986240e-01, `logs/train_d2sx_N10000_a1.log:680-681`). best val 3.985658e-01 @653 의 가중치는 저장되지 않았다(BEST_WEIGHTS_UNAVAILABLE). 두 시점 사이 EMA 갱신은 36×20 = 720회다(0.999^720 ≈ 0.49). 그래서 두 가중치는 일부 겹치지만 같지 않다. 평가 경로 `score.load_model` 은 `st["ema"]` 를 읽는다. 따라서 §13 에서 이 파일을 읽은 수치(표 3번 BLER 포함)는 이 @673 EMA 의 값이다. 표 1번 GB'(`results/gate_D2.txt`, 09-21 07:49)는 이 파일이 아니라 형제 시드 `ckpt/B3_dscore_D2.pt` 에서 나왔다(`results/diag/checkpoint-provenance_SUMMARY.md:26-38`). 표 3번 BLER 의 출처는 `raw_supp` 112파일(전부 `meta|dscore_ckpt` = `ckpt/d2sx_N10000_a1.pt`, arm `M-ours-dscore`)이며, ckpt mtime 09-21 12:51:59 가 raw_supp 13:19–13:20 보다 앞선다. H5 "체크포인트 출처 REFUTED" 는 파일 동일성에 대한 판정이므로 그대로 둔다.
```

<details><summary>검증 agent 지적 / 초안 원안</summary>

지적: 인용 483-484 HEAD 그대로. 수치 OK: raw_supp 112/112 dscore_ckpt ckpt/d2sx_N10000_a1.pt, arm M-ours-dscore, mtime 13:19:12–13:20:18. ckpt 673/653, 3.985658e-01/3.986240e-01, file d94aa99bdc568906, ema 62432fd33f0c9378, mtime 12:51:59. 로그 :4 n_train=9000, :660/:680/:681. ceil(9000/256)=36, ×20=720, 0.999^720=0.487. 문구 1건(새 주장 과함): '§13 의 수치와 표 3번 BLER 은 이 @673 EMA 의 값' 은 §13.1 표 1번 GB'(`results/gate_D2.txt`, 헤더 09-21 07:49:41)까지 덮는다. 이 값은 이 파일 학습(12:40:51 시작)보다 먼저 나왔고, `results/diag/checkpoint-provenance_SUMMARY.md:26-38` 에 따르면 형제 시드 `ckpt/B3_dscore_D2.pt` 에서 나왔다.

초안 원안:

```text
> **정정 (2026-09-23, review_next P0-1b)**: 이 파일(sha256 `d94aa99b…`)의 가중치는 **마지막 epoch(673) EMA** 다(ema sha256[:16] 62432fd33f0c9378, 이 가중치의 val 3.986240e-01, `logs/train_d2sx_N10000_a1.log:680-681`). best val 3.985658e-01 @653 의 가중치는 저장되지 않았다(BEST_WEIGHTS_UNAVAILABLE). 두 시점 사이 EMA 갱신은 36×20 = 720회다(0.999^720 ≈ 0.49). 그래서 두 가중치는 일부 겹치지만 같지 않다. 평가 경로 `score.load_model` 은 `st["ema"]` 를 읽는다. 따라서 §13 의 수치와 표 3번 BLER 은 이 @673 EMA 의 값이다. 표 3번 BLER 의 출처는 `raw_supp` 112파일(전부 `meta|dscore_ckpt` = `ckpt/d2sx_N10000_a1.pt`, arm `M-ours-dscore`)이며, ckpt mtime 09-21 12:51:59 가 raw_supp 13:19–13:20 보다 앞선다. H5 "체크포인트 출처 REFUTED" 는 파일 동일성에 대한 판정이므로 그대로 둔다.
```
</details>

<details><summary>근거</summary>

CPU 에서 raw_supp/*.npz 를 읽었다: 112/112 가 meta|dscore_ckpt 'ckpt/d2sx_N10000_a1.pt' 이고 meta|stagec_ckpt 키는 없다. arm M-ours-dscore, mtime 은 2026-09-21 13:19:12–13:20:18 이다. CPU torch.load d2sx_N10000_a1.pt: epoch 673, best_epoch 653, best_val 3.985658e-01, hist val@673 3.986240e-01, file d94aa99bdc568906 (PM:483 의 sha256 과 앞자리가 같다), ema 62432fd33f0c9378. 로그 :660 'epoch 653 … val 3.985658e-01 … *', :680 'epoch 673 … val 3.986240e-01', :681 '# done : 673 epochs … best val 3.985658e-01 @ epoch 653'. n_train=9000(로그 :4), batch 256 이므로 range(0,9000,256)=36회/epoch 이고 ×20 = 720, 0.999^720 = 0.487 이다. st["ema"] 를 읽는 평가 코드는 score.py:1025 뿐이고 st["model"] 을 읽는 것은 tests.py:709 뿐이다(git grep). REVIEW_AUDIT P0-1b 반박 (4) 가 raw_supp 를 범위로 지목했고, 1차 DECISIONS 정정(cost-ckpt-16 검증본)이 범위 목록에 raw_supp 를 넣었다. 이 주석은 그 인라인 표기다. PM:475 가 '두 절의 모든 수치는 ckpt/d2sx_N10000_a1.pt 에서' 라고 적는다.

검증: (위 참조)
</details>

### cost-ckpt-32 · cost-ckpt-32 — `conf/STATUS.md` 373 (제목), 375-376 (한 문단; 삽입: 376 뒤, 377 빈 줄 앞 — cost-ckpt-22 의 '375 뒤' 는 이 위치를 뜻한다)

- 방식: **STATUS inline note** · ✅ 검증 통과

**원문 (HEAD)**

```text
L373: ## C3 결과 — D1 게이트 **통과** (2026-09-21 14:12 KST)
L375: `results/gate_D1_C.txt` / `LADDER_C.md`, 체크포인트 `ckpt/sx_N160000_D1.pt`,
L376: 구성 `dit vp/angle w64 d6 lr2.238e-3 ema0.999`, `n_eval=512 n_jac=64`, 보고용 stream 10.
```

**제안 문구**

```text
> **정정 (2026-09-23, review_next ckpt/M2)**: 아래 표의 PASS 는 `sx_N160000_D1.pt` 에 저장된 **마지막 epoch(200) EMA** 에서 측정됐다. `gates_D1 → _as_model → load_model` 경로가 `st["ema"]` 를 읽는다(ema sha256[:16] ae04fefa33998484). 그 run 의 best val 은 7.398444e-01 @136 이고, 게이트된 @200 EMA 의 val 은 7.398687e-01 이다(`logs/train_sx_N160000_D1.log:143,207-208`). min_epochs=200 때문에 best 이후 64 epoch 을 더 학습했다(EMA 갱신 563×64 = 36,032회). 따라서 둘은 다른 가중치다. best(@136) 가중치는 저장되지 않아 그 게이트 값은 측정된 적도 없고 복구할 수도 없다(BEST_WEIGHTS_UNAVAILABLE). 판정은 고치지 않는다. PASS 는 이 파일(@200 EMA)에 대해 참이고, §6b D1 확증 실행도 같은 가중치를 읽었다(441 행 뒤 정정). 661 행 뒤 정정을 볼 것.
```

<details><summary>근거</summary>

CPU torch.load sx_N160000_D1.pt: epoch 200, best_epoch 136, best_val 7.398444e-01, hist val@200 7.398687e-01, ema ae04fefa33998484. 로그 :143 'epoch 136 … val 7.398444e-01 … *', :207 'epoch 200 … val 7.398687e-01', :208 '# done : 200 epochs, stopped_by=patience … best val 7.398444e-01 @ epoch 136'. 로그 :4 n_train=144000 이므로 range(0,144000,256)=563/epoch, ×64 = 36,032, 0.999^36032 ≈ 2.2e-16 이다. HEAD score.py:1242 gates_D1 → _as_model(:1188) → load_model(:1025 st["ema"]). ckpt mtime 2026-09-21 09:14:59 < LADDER_C.md:1 [14:12]. 검증 agent 가 제안한 문구에 갱신 횟수와 '판정 불변' 을 더했다. 1차 cost-ckpt-19(661 뒤)·22(DECISIONS)와 같은 사실이다.

검증: 없음. 373·375-376 HEAD 그대로, 377 빈 줄. 로그 :143/:207/:208 확인. 563×64=36,032 이고 0.999^36032≈2.2e-16. load_model 은 게이트 커밋 7f5f5a21 에서도 st["ema"] 를 읽는다(score.py:814).
</details>

### cost-ckpt-33 · cost-ckpt-33 — `conf/STATUS.md` 1513-1514 (삽입: 1514 뒤, 1515 빈 줄 앞; 1518 표 val loss 행도 이 주석으로 다룸)

- 방식: **STATUS inline note** · ✅ 검증 통과

**원문 (HEAD)**

```text
L1513: `results/gate_D1_L0.01.txt`, `LADDER_L0.01.md`. `sx_V3_N160000_D1_a1_lam0.01.pt` (§3d 시행 1, 동결 lr 에서 발산 없이
L1514: 완주, patience 종료 @200, best val 7.398582e-01 @142 — V0 의 7.398444e-01 과 0.002% 차이).
L1518: | val loss | 7.398444e-01 | 7.398582e-01 | 7.422616e-01 | 7.488075e-01 |
```

**제안 문구**

```text
> **정정 (2026-09-23, review_next ckpt/M2)**: 이 PASS(와 아래 표의 λ=0.01 열)는 best(@142)가 아니라 파일에 저장된 **@200 EMA** 에서 측정됐다. 시각 순서는 ckpt mtime 17:10:19, `gate_D1_L0.01.txt` 헤더 date 17:10:36, 파일 17:11:53 이다. 게이트 경로는 `load_model` → `st["ema"]` 다(ema sha256[:16] 44c9e87eeafbcbdc). 그 가중치의 val 은 7.399352e-01 이다(`logs/train_V3_D1_N160000_a1_lam0.01.log:208-209`). 1514 의 "0.002% 차이" 와 1518 val loss 행은 best val 끼리의 비교다. 게이트된 가중치끼리 보면 V0 7.398687e-01 · λ=0.01 7.399352e-01(V0 대비 0.009%) · λ=0.1 7.458941e-01 · λ=1.0(V3 a3) 7.504991e-01 이다. 게이트 값 비교(GD 0.0887 대 0.0718 등)는 네 열 모두 @200 EMA 끼리다. best 가중치에서의 게이트 값은 측정된 적이 없고 복구할 수 없다.
```

<details><summary>근거</summary>

CPU torch.load(epoch/best_epoch/best_val/hist val@last): sx_V3_N160000_D1_a1_lam0.01 200/142/7.398582e-01/7.399352e-01 (file ee4a86475db437e0, ema 44c9e87eeafbcbdc); sx_N160000_D1 200/136/7.398444e-01/7.398687e-01; sx_V3_N160000_D1_a2_lam0.1 200/33/7.422616e-01/7.458941e-01; sx_V3_N160000_D1_a3 200/159/7.488075e-01/7.504991e-01. λ=1.0 열 = gate_D1_C.txt(HEAD) 의 sx_V3_N160000_D1_a3.pt(GB 5.91351e-02, GC 3.52507e-01, GD 3.44911e-01). 상대차: best 끼리 0.00187%, @200 끼리 0.00899%. 로그 :150 'epoch 142 … *', :208 'epoch 200 … val 7.399352e-01', :209 '# done : 200 epochs … best val 7.398582e-01 @ epoch 142'. gate_D1_L0.01.txt:1 '# date : 2026-09-22 17:10:36 KST', :10 checkpoints filter sx_V3_N160000_D1_a1_lam0.01.pt. stat: ckpt 17:10:19.57, gate 파일 17:11:53.10. 1차 cost-ckpt-22 가 표기 위치로 1514 를 적었다.

검증: 없음. 1513-1514·1518 HEAD 그대로. 네 ckpt 모두 epoch 200 이고, best/@200 val 을 재현했다(0.00187%, 0.00899%). gate_D1_L0.01.txt:1 date 17:10:36, :10 filter, ckpt 17:10:19.57, 파일 17:11:53. λ=1.0 열은 gate_D1_C.txt(HEAD, 07:30:44)의 V3 a3 값이며 그 ckpt mtime 은 07:24:51 이다. 로그 :150/:208/:209 확인.
</details>

### cost-ckpt-34 · cost-ckpt-34 — `conf/STATUS.md` 1262 (문단 1259-1262; 삽입: 1262 뒤, 1263 빈 줄 앞)

- 방식: **other** · ✅ 검증 통과

**원문 (HEAD)**

```text
L1262: `ckpt/d2sx_N160000_a1.pt` (D1 형제 `sx_N160000_D1.pt` 가 GA~GD PASS, `LADDER_C.md:1`). C2, n=2560.
```

**제안 문구**

```text
optional — > **정정 (2026-09-23, review_next ckpt/M2·P0-1b)**: 형제의 PASS 는 `sx_N160000_D1.pt` 의 @200 EMA(best @136 아님)에서 측정됐다. 이 표의 학습 arm 은 `d2sx_N160000_a1.pt` 의 @1784 EMA(best @1764 아님)로 평가됐다. 두 파일 모두 best 가중치는 저장되지 않았다(BEST_WEIGHTS_UNAVAILABLE). 376·652 행 뒤 정정을 볼 것.
```

<details><summary>근거</summary>

검증 agent 누락 목록 (7) 에서 선택 항목으로 분류됐다. raw_B16e4 는 1344/1344 가 stagec_ckpt d2sx_N160000_a1.pt 다(1차 cost-ckpt-16 근거). CPU 판독: sx_N160000_D1 200/136, d2sx_N160000_a1 1784/1764. 1262 는 HEAD 원문 그대로다.

검증: 없음. 1262 HEAD 그대로. optional 로 표시했고 method 는 other 다.
</details>

### cost-ckpt-35 · cost-ckpt-35 — `conf/results/NUMBERS_PACKAGE_2026-09-22.md` 187 (삽입: 188 'Source …' 뒤, 189 빈 줄 앞) / 740 P10 (표 안이라 삽입: 742 뒤, cost-ckpt-4 주석 다음 줄)

- 방식: **other** · ✅ 검증 통과

**원문 (HEAD)**

```text
L187: **D1, gate PASS** (`ckpt/sx_N160000_D1.pt`: GA 9.879e-16, GB 2.659e-3, GC 9.986e-2, GD 7.183e-2 — **PASS rests on GB/GC/GD; GA is a structural zero**). Equal budget **NO**: learned N=1.6e5 vs the FITTED reference (kron K=32) fitted at N=1e4; the TRUE prior is closed-form and carries no budget.
L740: | P10 | §6e λ 스윕 게이트 | λ=0.01 PASS (GB +0.32%, GC 0.0991, **GD 0.0887 > V0 0.0718**); λ=0.1 FAIL (0.065/0.369/0.319); λ=1.0 FAIL | n_eval 512, n_jac 64 | D1 | — | — | — | `gate_D1_L{0.01,0.1}.txt`, `LADDER_L*.md` |
```

**제안 문구**

```text
optional —
[188 뒤] > **정정 (2026-09-23, review_next ckpt/M2·P0-1b)**: 이 PASS 값과 아래 D1 스펙트럼(`logs/jacspec_D1_true.log`, 09-21 21:27)은 `sx_N160000_D1.pt` 에 저장된 마지막 epoch(200) EMA 에서 측정됐다(ema sha256[:16] ae04fefa33998484, val 7.398687e-01). best val 7.398444e-01 @136 의 가중치는 저장되지 않았다(BEST_WEIGHTS_UNAVAILABLE).
[742 뒤, cost-ckpt-4 주석 다음] > **정정 (2026-09-23, review_next ckpt/M2)**: P10 의 게이트 값은 모두 각 파일의 @200 EMA 에서 측정됐다(best 는 λ=0.01 @142, λ=0.1 @33, λ=1.0 = V3 a3 @159, 비교 기준 V0 = `sx_N160000_D1.pt` @136 이며 이 가중치들은 저장되지 않았다). 네 값은 같은 조건(@200 EMA)끼리의 비교다.
```

<details><summary>근거</summary>

검증 agent 누락 목록 (7) 에서 선택 항목으로 분류됐다. logs/jacspec_D1_true.log 헤더는 '# date : 2026-09-21 21:27:55 KST', 'ckpt = ckpt/sx_N160000_D1.pt' 이고, 이는 ckpt mtime 09:14:59 보다 뒤다. CPU 판독 값은 cost-ckpt-33 근거와 같다. 1차 초안이 NUMBERS_PACKAGE 에 인라인 주석을 달았으므로(cost-ckpt-4) 그 방식을 따른다.

검증: 없음. 187·740 HEAD 그대로. jacspec_D1_true.log 헤더는 21:27:55 이고 ckpt = ckpt/sx_N160000_D1.pt 다. optional 이고 method 는 other 다.
</details>

### cost-ckpt-36 · cost-ckpt-36 — `conf/PAPER_MATERIALS.md` 299·311 (§11.2; 삽입: 311 뒤) / 625 (삽입: 625 뒤, 2칸 들여쓴 인용) / 818-820 (삽입: 820 뒤) / 964·976 (§19.2 표; 삽입: 표 끝 984 뒤)

- 방식: **other** · ✅ 검증 통과

**원문 (HEAD)**

```text
L299: 출처 `LADDER_C.md` `[2026-09-21 14:12 KST] SX160000 | a1`, 체크포인트 `ckpt/sx_N160000_D1.pt`:
L311: D1 val loss 7.398444e-01. GB/GC/GD 는 `results/samplecx_D1.txt` 의 `N_train = 160,000` 행과 같은 값이다 (§8).
L625:   자격은 **같은 레시피의 D1 쌍둥이 `sx_N160000_D1.pt` 의 PASS 행**(§11.2)이 부여한다.
L818: 같은 레시피의 **D1 쌍둥이** `sx_N160000_D1.pt` 의 PASS 행이 부여한다 (§11.2). 인용할 때
L964: | `LADDER_C.md` | Stage C 사다리 (append-only). **PASS 행 = `sx_N160000_D1.pt`** | §11.2 |
L976: | `ckpt/sx_N160000_D1.pt` | D1 게이트 **PASS** 체크포인트 (Stage C arm 의 자격 근거) | §11.2 |
```

**제안 문구**

```text
optional —
[311 뒤] > **정정 (2026-09-23, review_next ckpt/M2)**: 위 PASS 는 `sx_N160000_D1.pt` 에 저장된 마지막 epoch(200) EMA 에서 측정됐다(ema sha256[:16] ae04fefa33998484). 311 행의 "D1 val loss 7.398444e-01" 은 best(@136) 가중치의 값이다. 게이트된 @200 EMA 의 val 은 7.398687e-01 이다(`logs/train_sx_N160000_D1.log:143,207`). best 가중치는 저장되지 않았다(BEST_WEIGHTS_UNAVAILABLE).
[625 뒤]   > **정정 (2026-09-23, review_next ckpt/M2)**: 이 PASS 행은 형제의 @200 EMA(best @136 아님)에 대한 것이다. §15 의 D2 체크포인트도 @1784 EMA 다(620 행 뒤 정정).
[820 뒤] > **정정 (2026-09-23, review_next ckpt/M2)**: 여기서 말하는 PASS 행은 형제의 @200 EMA 에 대한 것이다(best @136 가중치는 저장되지 않음). 311 행 뒤 정정을 볼 것.
[984 뒤] > **정정 (2026-09-23, review_next ckpt/M2)**: 964·976 행의 "PASS" 는 `sx_N160000_D1.pt` 의 @200 EMA 에 대한 것이다(best @136 가중치는 저장되지 않음). 977 행은 620 행 뒤 정정(cost-ckpt-18)이 다룬다.
```

<details><summary>근거</summary>

검증 agent 누락 목록 (7) 에서 선택 항목으로 분류됐다. 원문은 HEAD 그대로다. 312·626·821·985 는 빈 줄이고, §19.2 표는 961-984 다. CPU 판독: sx_N160000_D1 best 7.398444e-01 @136, @200 7.398687e-01. 311 의 7.398444e-01 은 로그 :143(best) 값과 같다. 566 은 cost-ckpt-29 가 필수 항목으로 다룬다.

검증: 없음. 299·311·625·818·964·976 HEAD 그대로. 312·626·821·985 는 빈 줄이고 §19.2 표는 961-984 다. optional 이고 method 는 other 다.
</details>

### cost-ckpt-37 · cost-ckpt-37 — `conf/code/figures_stagec2.py (GATE_LINE_PASS); conf/figs/F14_headline_C2_m3dB.txt, F14c_C2_p12dB_max_ratio.txt, F12_tp_envelope.txt, F15_gap_robustness.txt` figures_stagec2.py 60-62 → F12 txt 48 · F14 txt 29 · F14c txt 26 · F15 txt 43

- 방식: **other** · ✅ 검증 통과

**원문 (HEAD)**

```text
L60: GATE_LINE_PASS = ("checkpoint ckpt/d2sx_N160000_a1.pt: gates are measurable on D1 only, so this D2 checkpoint "
L61:                   "is qualified through its D1 sibling sx_N160000_D1.pt, which PASSES GB 2.66e-3 / GC 0.0999 / "
L62:                   "GD 0.0718 (LADDER_C.md:1); GA is a structural zero for this model family.")
```

**제안 문구**

```text
optional —
생성기 figures_stagec2.py:60-62 (재생성할 때만, 캡션 문구만 바뀜)
old: 위 원문
new:
GATE_LINE_PASS = ("checkpoint ckpt/d2sx_N160000_a1.pt: gates are measurable on D1 only, so this D2 checkpoint "
                  "is qualified through its D1 sibling sx_N160000_D1.pt, which PASSES GB 2.66e-3 / GC 0.0999 / "
                  "GD 0.0718 (LADDER_C.md:1); GA is a structural zero for this model family.  Both files hold "
                  "last-epoch EMA weights (sibling: epoch 200, best val epoch 136; this checkpoint: epoch 1784, "
                  "best val epoch 1764); the best-epoch weights were not stored.")
캡션 파일: F14(:29)와 F14c(:26)는 1차 초안이 파일 끝 CORRECTION 주석을 달기로 한 파일이다(cost-ckpt-6/8). 그 주석 끝에 한 문장을 더한다. 'The gate sentence in SCOPE refers to the sibling's last-epoch EMA (epoch 200; the best-val epoch 136 was not stored); this table's learned arms are the epoch-1784 EMA of ckpt/d2sx_N160000_a1.pt (best-val epoch 1764 not stored).' F12(:48)·F15(:43)는 reference only 로 두고 편집하지 않는다.
```

<details><summary>근거</summary>

검증 agent 누락 목록 (7) 에서 '감사가 캡션 주석을 요구하지 않으므로 선택' 으로 분류됐다. figures_stagec2.py:60-62 는 HEAD 원문 그대로이고, 네 캡션 줄에 같은 문장이 찍혀 있음을 확인했다. G-1.2 의 testbed-gate-22 는 figures_stagec2.py:245 앞에 NOTE 주석을 넣는 것이라 이 상수 변경과 겹치지 않는다. CPU 판독: sx_N160000_D1 200/136, d2sx_N160000_a1 1784/1764.

검증: 없음. 60-62 HEAD 그대로이고 F12:48·F14:29·F14c:26·F15:43 에 찍혀 있다. F14/F14c 는 1차에서 파일 끝 주석을 달기로 한 파일이므로 편집해도 규약에 맞다. F12/F15 는 reference only 로 둔다. optional 이다.
</details>

### cost-ckpt-38 · cost-ckpt-38 — `conf/10_SPEC_stageC.md` 345 (§6b 규칙 목록 첫 항목; 삽입: 345 뒤, 같은 목록 항목의 2칸 들여쓴 인용, 346 '- 셀:' 앞)

- 방식: **spec note (사용자 승인 필요)** · ✅ 검증 통과

**원문 (HEAD)**

```text
L345: - 체크포인트: `ckpt/sx_N160000_D1.pt` — GA 9.879e-16 / GB 2.659e-3 / GC 9.986e-2 / GD 7.183e-2, **PASS**.
```

**제안 문구**

```text
> **노트 (2026-09-23, review_next ckpt/M2·P0-1b) — 사용자 승인 필요.** 이 PASS 값은 `sx_N160000_D1.pt` 에 저장된 마지막 epoch(200) EMA 에서 측정됐다(ema sha256[:16] ae04fefa33998484, val 7.398687e-01). 그 run 의 best val 7.398444e-01 @136 가중치는 저장되지 않았다. 이 규칙이 지정한 §6b 실행(`raw_C` D1 1344파일)도 같은 파일·같은 가중치를 읽었으므로 게이트와 BLER 은 같은 가중치의 것이다. 339-340 의 "게이트 PASS 가 기록돼 있다" 도 같은 가중치에 대한 것이다. 규칙 문구는 바꾸지 않는다.
```

<details><summary>근거</summary>

10_SPEC_stageC.md:345 는 HEAD 원문 그대로이고 346 은 다음 목록 항목이다. 사전 등록 문서라 원문은 두고 노트만 단다. 형식은 1차 testbed-gate-4·7 을 따랐다. 사실 근거는 cost-ckpt-28·32 와 같다(CPU 판독; raw_C D1 1344/1344 stagec_ckpt sx_N160000_D1.pt; ckpt mtime 09:14:59 < 게이트 14:12 < raw 16:01).

검증: 없음. 345 HEAD 그대로, 346 은 다음 항목이다. '사용자 승인 필요' 노트 형식은 1차 testbed-gate 항목과 같다.
</details>

### cost-ckpt-39 · cost-ckpt-39 — `conf/10_SPEC_stageC.md` 319 (§3d 선택 규칙; 삽입: 319 뒤, 320 빈 줄 앞)

- 방식: **spec note (사용자 승인 필요)** · ✅ 검증 통과

**원문 (HEAD)**

```text
L318: **선택 규칙**: 폴백 시행 간 선택은 **검증 손실**로만 한다. 게이트 값으로도, BLER 로도 하지 않는다.
L319: DIVERGED 시행의 best 체크포인트는 보존하되, 폴백이 성공하면 폴백본을 쓴다.
```

**제안 문구**

```text
> **노트 (2026-09-23, review_next P0-1b) — 사용자 승인 필요.** 이 규칙의 "DIVERGED 시행의 best 체크포인트는 보존" 은 지켜지지 않았다. 당시 `score.train`(4ad41df9 까지)은 best 를 스칼라로만 추적하고, 매 epoch 현재 EMA 로 같은 파일을 덮어썼다. DIVERGED 로 기록된 8시행(`LADDER_C.md` 2·3·4·5·6·10·11행, `LADDER_L0.1.md` 1행)의 체크포인트는 전부 마지막 epoch 판이다. 각 파일의 epoch / best_epoch / 저장된 가중치의 val 은 다음과 같다: `d2sx_V2_N160000_a1` 118/85/1.2075 · `d2sx_V3_N160000_a1` 62/27/1.7202 · `sx_V2_N160000_D1_a1` 57/48/1277.08 · `sx_V2_N160000_D1_a2` 34/23/2.74e12 · `d2sx_V2_N160000_a2` 191/85/nan(EMA 원소 479,489 개 중 479,360 개 비유한) · `sx_V3_N160000_D1_a1` 41/12/63.27 · `sx_V3_N160000_D1_a2` 173/134/nan(479,554 개 중 479,426 개 비유한) · `sx_V3_N160000_D1_a1_lam0.1` 100/44/15.26. best-epoch 가중치는 어디에도 없다. 이 8개는 모두 BLER arm 으로 쓰인 적이 없다. cd241b7e 부터 `score.train` 이 `<ckpt>_best.pt` 를 따로 저장한다. 규칙 문구는 바꾸지 않는다.
```

<details><summary>근거</summary>

CPU torch.load 로 conf/ckpt 의 V2/V3/λ 체크포인트를 전부 읽었다(epoch, best_epoch, best_val, hist[-1] val, torch.isfinite over st['ema']). 위 8개 모두 epoch > best_epoch 이고, 나머지 비발산 파일은 대상이 아니다. DIVERGED 행은 git show HEAD:conf/LADDER_C.md 에서 grep 'DIVERG' 로 찾았다(2,3,4,5,6,10,11행). LADDER_L0.1.md:1 은 sx_V3_N160000_D1_a1_lam0.1.pt DIVERGED 다. conf/ 아래 별도 best/snapshot 파일은 없다(ls ckpt*, find). 검증 agent 는 '넷' 이라 적었지만, 그 넷(cost-ckpt-23)은 LADDER_C 에서 'holds the best-val' 을 주장한 행들이다. DIVERGED 전체는 여덟이다. arm 아님의 근거는 docs/EXPERIMENTS.md:21 'V2·V3·λ∈{0.01,0.1,1.0} 은 arm 아님'. best_ckpt_path 는 HEAD score.py:691(1차 cost-ckpt-15 근거).

검증: 없음. 318-319 HEAD 그대로. DIVERGED 행은 LADDER_C 2·3·4·5·6·10·11행과 LADDER_L0.1 1행이다. 8개 ckpt 의 epoch/best/@last val 과 비유한 개수(479,360/479,489, 479,426/479,554)를 CPU 로 재현했다. conf/ 아래에 *_best.pt 나 스냅샷은 없다(ckpt_hpo 만 있음).
</details>

### cost-ckpt-40 · cost-ckpt-40 — `conf/DECISIONS.md` 1차 초안 cost-ckpt-12·16·22·23 의 append 예정 행 (새 행 아님, 문구 보강)

- 방식: **DECISIONS append** · ✅ 검증 통과

**원문 (HEAD)**

```text
cost-ckpt-12 선택 필드: … 코드는 docstring 만 고친다(figure_f14.py 13-15, bench_moduleH.py 3-5·12). …
cost-ckpt-16 선택 필드: … 표기 위치: STATUS 652·672·1591 뒤, EXPERIMENTS 21 뒤, PAPER_MATERIALS 620 뒤 정정 주석. …
cost-ckpt-22 선택 필드: … 표기 위치는 STATUS 74·375·661·1497·1514 뒤 정정 주석. …
cost-ckpt-23 근거 필드 끝: … 이 넷은 BLER arm 으로 쓰인 적이 없다(EXPERIMENTS 21행 "V2·V3·λ∈{0.01,0.1,1.0} 은 arm 아님")
```

**제안 문구**

```text
(1차 초안의 해당 append 행에 반영할 문구 교체이며, 새 DECISIONS 행을 만들지 않는다.)
cost-ckpt-12: 'bench_moduleH.py 3-5·12' → 'bench_moduleH.py 3-5·11'.
cost-ckpt-16: '표기 위치: STATUS 652·672·1591 뒤, EXPERIMENTS 21 뒤, PAPER_MATERIALS 620 뒤 정정 주석.' → '표기 위치: STATUS 441·652·672·1591 뒤, EXPERIMENTS 21 뒤, PAPER_MATERIALS 416·484·571·620 뒤, NUMBERS_PACKAGE 195 뒤 정정 주석, figures_stagec.py:619-621 F10 캡션 문자열(재생성 시에만).'
cost-ckpt-22: '표기 위치는 STATUS 74·375·661·1497·1514 뒤 정정 주석.' → '표기 위치는 STATUS 74·376·441·661·1497·1514 뒤 정정 주석, 10_SPEC_stageC.md:345 노트(사용자 승인 필요).'
cost-ckpt-23 근거 필드 끝에 추가: '같은 저장 경로 때문에 DIVERGED 로 기록된 나머지 넷도 마지막 epoch 판이다: LADDER_C 5행 `sx_V2_N160000_D1_a2` 34/23, 10행 `sx_V3_N160000_D1_a1` 41/12, 11행 `sx_V3_N160000_D1_a2` 173/134(EMA 479,554 개 중 479,426 개 비유한), LADDER_L0.1 1행 `sx_V3_N160000_D1_a1_lam0.1` 100/44. 이 넷의 행은 best 보유를 주장하지 않았다. §3d(10_SPEC_stageC.md:319)의 보존 규칙이 지켜지지 않았다는 노트는 사용자 승인 대상이다.'
```

<details><summary>근거</summary>

1차 초안 RECORD_CORRECTIONS_DRAFT.md cost-ckpt-12(선택 필드에 'bench_moduleH.py 3-5·12'), cost-ckpt-16(검증본의 표기 위치 목록), cost-ckpt-22(검증본의 표기 위치 목록), cost-ckpt-23(검증본)을 참조했다. 새 위치의 근거는 이번 cost-ckpt-24~39 이고, 체크포인트 수치는 CPU 판독으로 확인했다(cost-ckpt-39 근거).

검증: 없음. 1차 cost-ckpt-12·16·22·23 의 해당 필드 문구가 초안 파일과 글자 그대로 같다. 추가 위치는 24~33·38 과 맞는다. LADDER_C 5·10·11행과 L0.1 1행에는 'holds the best' 주장이 없음을 확인했다.
</details>

### cost-ckpt-41 · cost-ckpt-41 — `N/A` N/A

- 방식: **other** · ✅ 검증 통과

**원문 (HEAD)**

```text
N/A
```

**제안 문구**

```text
사용자 판단 대상 목록: (1) docs/EXPERIMENTS.md:21 의 'D1 게이트 PASS @N=1.6e5'·'λ=0.01 만 PASS' — 검증 agent 가 cost-ckpt-17 검증본이 이미 다룬다고 적었으므로 추가 초안을 쓰지 않았다. (2) G-1.2 그룹이 '문제없는 용례' 로 분류한 STATUS 439·PM 566·figures_stagec.py:620(RECORD_CORRECTIONS_DRAFT:1414) — D2 체크포인트를 게이트 통과라 부르는지를 본 분류다. 이번 cost-ckpt-28·29·30 은 last-EMA 표기만 더하므로 두 분류는 충돌하지 않는다. 적용 시 함께 확인할 것. (3) 추가 발견(감사·1차 검증 목록 밖, 초안 미작성): (a) STATUS:610·623-624, PAPER_MATERIALS:321·334 '7.398444e-01 대 7.398676e-01 (0.003%)' 는 V0 @136·V2 a3 @74 의 best val 이다. GC 0.0999·0.1674 는 각 파일의 @200 EMA 에서 쟀고, 그 가중치의 val 은 7.398687e-01·7.409458e-01(0.146% 차)이다. val 차보다 GC 차가 훨씬 크다는 방향은 남지만 0.003% 는 게이트된 가중치의 차가 아니다. (b) STATUS:1506-1508 의 7.4226·7.488·7.3986 도 best val 이다(게이트된 가중치: 7.4589·7.5050·7.3994). (c) STATUS:265(samplecx_D1 예산표 '160,000 … PASS')와 figs/F7_jacspectrum_D1_D2.txt:31-32('PASSES all four … results/samplecx_D1.txt')는 같은 @200 EMA PASS 표기 위치인데 목록 밖이다. (d) STATUS:375 가 출처로 적은 results/gate_D1_C.txt 는 이후 e807a43f(V2)·ae2f3a78(V3) 에서 덮어써졌고, HEAD 판은 sx_V3_N160000_D1_a3.pt FAIL 이다. 이 PASS 의 원 파일은 커밋 7f5f5a21 판이고 PASS 행은 LADDER_C.md:1 에 남아 있다. PAPER_MATERIALS:315-316·965 는 이 파일이 V2 a3 를 담는다고 적는데 HEAD 판은 V3 a3 다. (e) PAPER_MATERIALS:975 'raw_C/ … npz 1344개 (D1 + D2)' — 실제로는 2688개(D1 1344 + D2 1344)다. (f) raw_supp 의 다른 위치: STATUS:273·283, NUMBERS_PACKAGE:285(C6), results/diag/checkpoint-provenance_SUMMARY.md:3·17, logs/diag_prov_loadpath.log:11('loaded_best_val' 은 best_val 스칼라일 뿐 로드된 가중치의 val 이 아니다). DECISIONS P0-1b 범위 목록(cost-ckpt-16)과 PM 484 뒤 주석(cost-ckpt-31)이 다루므로 개별 주석은 쓰지 않았다. (g) STATUS:439 'raw 336개' 는 16:30 시점 n=640 중간본의 수(21점×16파일)다. 현재 raw_C D1 은 1344파일이다. 시점 기록이라 정정 대상이 아니다.
```

<details><summary>근거</summary>

(1) RECORD_CORRECTIONS_DRAFT.md cost-ckpt 누락 위치 (7) 'the corrected EXPERIMENTS P0-1b note above now covers these'. (2) 같은 파일 :1414. (3a) CPU torch.load sx_V2_N160000_D1_a3 200/74/7.398676e-01/hist@200 7.409458e-01; sx_N160000_D1 @200 7.398687e-01. (3b) cost-ckpt-33 근거. (3d) git log -- conf/results/gate_D1_C.txt: 7f5f5a21(09-21 14:14 C3 PASS), e807a43f(22:28 V2 FAIL), ae2f3a78(09-22 07:33 V3 FAIL). HEAD 판 :10 'filter: ckpt=ckpt/sx_V3_N160000_D1_a3.pt', :35 VERDICT FAIL. (3e) ls conf/raw_C: D1 1344 + D2 1344 = 2688. (3f) git grep raw_supp. (3g) 336×40 = 13,440 = 21×640.

검증: 없음. (3a) V2 a3 @200 val 7.409458e-01 과 0.146% 를 재현했다. (3d) gate_D1_C.txt 커밋 이력과 HEAD 판(V3 a3 FAIL)을 확인했다. (3e) raw_C 1344+1344=2688. (3f) 각 줄이 존재하고 loaded_best_val=0.3985658 이다. (3g) 21×16=336.
</details>

---

## 3차 잔여 — 2차 검증 뒤에도 남은 위치 (검증 agent 제안 그대로, 2차 검증 없음)

### genie/상한 명칭 (R-10.3, M-10.3a)

round 1·2 이후에도 덮이지 않은 위치(모두 R5/R6 bound 명명, HEAD cd241b7e 에서 확인). (1) conf/code/analysis.py:380, pair_list docstring '      M-ours-*     -> R6-exactEP/R5-genie  anchor the BOUND      (the non-ours member)'. 동작 불변 docstring 교체 대상이다. 제안: 'anchor the BOUND' → 'anchor the REFERENCE'. (2) conf/code/analysis.py:388, 주석 '# headroom: D1 = exact EP, D2 = genie only'. 동작 불변 주석 교체 대상이다. 제안: '# reference arm: D1 = exact-prior EP, D2 = known-channel (genie) only'. (1)(2)는 genie-22(같은 파일 :90-91)에 묶어 적용하면 된다. (3) 커밋 446efe5c 메시지 l.12 '상한 대비: V0 -> R6-exactEP 가 C5 에서 88:91 p=0.88, POWERED. 검정력을 갖춘 동률이다.'. origin/main 에 push 됐고 뒤에 커밋이 있어 수정할 수 없다. genie-2 DECISIONS 줄의 '이 줄로 읽는다' 목록에 넣는다(STATUS:590·PAPER_MATERIALS:585 와 같은 문장). (4) 커밋 fd5787e9 메시지 l.9 'D1 C2: V0 -> R6-exactEP 7:8 p=1.0 — 정확 EP 상한과 구별 불가. C1 도 92:72 p=0.14 동률.'. origin/main 에 있어 수정할 수 없다. 이 줄은 n=640 철회분이기도 하다(NUMBERS_PACKAGE:564 R10, STATUS:462 와 같은 문장). genie-2 목록에 넣는다. 그 밖에는 git grep 으로 repo 전체(conf, docs, Demo, figs txt, results txt)를 다시 훑었고 추가 위치는 없다.

### D2 testbed 서술·게이트 표현 (R-5.2, M-5.2a, G-1.2)

1-2차를 합쳐도 G-1.2 에서 빠진 곳 (HEAD cd241b7e 줄 번호. 1-3번은 초안 대상, 4-5번은 선택):
1. conf/PAPER_MATERIALS.md:23-25 (Stage C 요약 문단, 문단 끝 29 뒤, 30 빈 줄 앞에 노트): '예산을 N' = 1.6e5 로 올린 학습 score 가 D1 게이트를 **통과**했고 (GB 0.0027 · GC 0.0999 · GD 0.0718; …), 그 체크포인트로 두 testbed 의 확증 BLER 을 n = 2560 으로 돌렸다.' 줄임말이 아니라 사실 오류다. D2 확증은 별도 D2 재학습본 d2sx_N160000_a1.pt 로 돌렸고(tables_D2_C.txt:37-39,44-45, 게이트 행 없음 :45), D1 게이트를 통과한 것은 sx_N160000_D1.pt 다(STATUS:439, LADDER_C.md:1). 읽는 법: '… D1 게이트를 통과했고(…), 그 체크포인트(D1)와 같은 레시피·예산으로 D2 에 따로 학습한 체크포인트(d2sx_N160000_a1.pt, D2 게이트 행 없음)로 두 testbed 의 확증 BLER 을 n=2560 으로 돌렸다'. 같은 문단 29행 '게이트 통과가 수신기 사용 가능성을 보증하지 않는다' 는 STATUS:744-745 처럼 형제-자격 한정을 붙여 읽는다. 굵은 글씨가 끼어 있어 '게이트를 통과' grep 에 걸리지 않았다.
2. docs/EXPERIMENTS.md:21 '(**헤드라인: 게이트 통과 + 동일예산 N=1.6e5, GMM K=1024 0.2434 → V1 0.1449, …**)'. cost-ckpt-17 이 이 구절을 인용하지만 EMA 문제만 다루고 게이트 문구는 다루지 않는다. 파일 끝 cost 정정 노트들 다음에 '> 정정 (2026-09-23, review_next G-1.2): 21행 헤드라인의 "게이트 통과 + 동일예산" 은 "D1 형제 게이트 PASS 레시피 + 동일예산" 으로 읽는다(d2sx_N160000_a1.pt 게이트 행 없음 tables_D2_B16e4k.txt:45, PASS 는 LADDER_C.md:1 sx_N160000_D1.pt). 원래 행은 고치지 않는다.' 를 단다. 같은 줄의 '동작 범위(게이트 통과 예산)' 는 예산 표현이라 둔다.
3. conf/results/NUMBERS_PACKAGE_2026-09-22.md:543 '§3c also required V4/V4b to be built only from a GATE-PASSING checkpoint (N′=1.6e5); the equal-budget tables build them from gate-FAILED checkpoints'. testbed-gate-43 목록에 없다. 교정문을 testbed-gate-43 corrected_proposed_text 에 넣었다.
4. (선택, 코드 문자열) conf/code/arms.py:150 docstring 'score_prior_c : the gate-passing Stage C checkpoint -> M-ours-dscore-C-V0'. D1 실행에서는 맞지만 D2 실행에서는 d2sx_N160000_a1.pt(게이트 행 없음)다. conf/code/cf_rollup.py:46 은 jacpsd_counterfactual_SUMMARY_n256.txt:6 'which FAILED the pre-registered gate' 를 찍는 생성기 문자열이다. 둘 다 동작 불변 주석이나 docstring 교체 후보다.
5. (경계, 운영 스크립트 주석) conf/code/queue_after_B1e4x.sh:2 'B16e4 is the ONLY table that is both gate-passing AND', :13 'with the GATE-PASSING checkpoint', conf/code/queue2.sh:4 'B16e4 (the only table that is both gate-passing AND equal-budget)', conf/code/fit_k1024_big.sh:10 'the budget of the gate-passing table'. STATUS:1257 제목과 같은 유형이다. 고칠지는 사용자가 정한다.
1-4번을 초안에 넣으면 G-1.2 DECISIONS 행(testbed-gate-23, testbed-gate-40 교정문)의 위치 목록에도 넣어야 한다. R-5.2/M-5.2a 에서 빠진 곳은 없다.

### 복잡도 4.6x·체크포인트 (P0-2b, cost/M1·M2, P0-1b, ckpt/M2)

1·2차 어디에도 없는 위치. 모두 선택/사용자 판단 등급이다(cost-ckpt-35/36 과 같은 부류이거나 reference only). (1) NUMBERS_PACKAGE:408 'The only PASS in the project … sx_N160000_D1.pt … → PASS' 와 :469 게이트 열 'PASS (sx_N160000_D1.pt)': last-EMA @200 한정어가 없다. (2) NUMBERS_PACKAGE:426 'D1 val V0 7.398444e-01 vs V2 7.398676e-01 = 0.003 % apart': cost-ckpt-41 (3a) 와 같은 best-val 비교인데 (3a) 목록에서 빠졌다. 게이트된 가중치끼리는 7.398687e-01 대 7.409458e-01, 0.146% 다. (3) PAPER_MATERIALS:237-238 ('N_train = 160,000 PASS 행이 바로 Stage C 가 arm 으로 올린 D1 체크포인트 ckpt/sx_N160000_D1.pt') 와 :216 코드블록('160,000 200 7.3984e-01 … PASS'): 200 epoch 에 best val 을 짝짓고 게이트 값은 @200 EMA 의 것이다. (4) results/samplecx_D1.txt:30 과 results/samplecx.csv:5 ('160000,200,7.398444e-01,…,True'): d2_gbprime.csv 와 같은 짝짓기다. 생성 파일이라 reference only(cost-ckpt-27 방식). (5) PAPER_MATERIALS:1016-1018 (§20.9 '3.519379e-01 @1764 를 쓴다'): best val 값 자체는 맞지만 평가 가중치로 읽힐 수 있다. 사용자 판단. 참고(범위 밖): PAPER_MATERIALS:475 '두 절의 모든 수치는 ckpt/d2sx_N10000_a1.pt 에서' 는 §13.1 표 1번 GB'(gate_D2.txt = B3_dscore_D2.pt, checkpoint-provenance_SUMMARY.md:26-38)와 맞지 않는다. P0-1b 항목이 아니므로 초안은 쓰지 않았다.
